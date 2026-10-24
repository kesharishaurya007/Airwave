import cv2
import mediapipe as mp
import mido
import numpy as np
import time

# --- MIDI SETUP ---
try:
    outport = mido.open_output('IAC Driver Bus 1')
    # Hard Reset all 16 channels to kill any hanging screeches
    for c in range(16):
        outport.send(mido.Message('control_change', control=123, value=0, channel=c))
        outport.send(mido.Message('pitchwheel', pitch=0, channel=c))
    print("✅ ROLI Airwave: Anti-Feedback Engine Online")
except:
    print("❌ MIDI Error: Check IAC Driver")
    exit()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

# --- SETTINGS ---
NUM_KEYS = 25
START_NOTE = 48
SMOOTHING = 0.3 
MIDI_RATE_LIMIT = 0.02 # Seconds (50Hz) - Prevents MIDI Buffer Overflow

# State: {hand_id: {'note': int, 'x': float, 'sx': float, 'sy': float, 'chan': int, 'last_cc': {}, 'last_time': float}}
active_hands = {}

cv2.namedWindow("ROLI Airwave Pro HUD", cv2.WINDOW_NORMAL)
cv2.resizeWindow("ROLI Airwave Pro HUD", 1280, 720)
cap = cv2.VideoCapture(0)

def send_throttled_cc(hand_id, control, value, channel):
    current_time = time.time()
    d = active_hands[hand_id]
    
    # 1. Check if enough time has passed since the last message
    if current_time - d['last_time'].get(control, 0) < MIDI_RATE_LIMIT:
        return False
        
    # 2. Check if the value has changed significantly
    last_val = d['last_cc'].get(control, -1)
    if abs(value - last_val) > 3: 
        outport.send(mido.Message('control_change', control=control, value=int(value), channel=channel))
        d['last_cc'][control] = value
        d['last_time'][control] = current_time
        return True
    return False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # Draw HUD
    cv2.rectangle(frame, (0, 0), (w, 60), (20, 20, 20), -1)
    active_gestures = {"GLIDE": False, "TILT": False, "RAISE": False, "SLIDE": False}
    
    # Keyboard UI
    key_w = w // NUM_KEYS
    for i in range(NUM_KEYS):
        cv2.rectangle(frame, (i * key_w, h-80), ((i+1) * key_w, h), (100, 100, 100), 1)

    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    current_ids = []

    if results.multi_hand_landmarks:
        for idx, lms in enumerate(results.multi_hand_landmarks):
            current_ids.append(idx)
            pts = lms.landmark
            itip, wrist = pts[8], pts[0]
            
            # --- STRIKE ---
            if idx not in active_hands and itip.y > 0.6:
                root_note = START_NOTE + int(itip.x * NUM_KEYS)
                chan = idx 
                outport.send(mido.Message('note_on', note=root_note, velocity=90, channel=chan))
                active_hands[idx] = {
                    'note': root_note, 'x': itip.x, 'sx': itip.x, 'sy': wrist.y, 
                    'chan': chan, 'last_cc': {}, 'last_time': {}
                }
            
            # --- GESTURES ---
            if idx in active_hands:
                d = active_hands[idx]
                d['sx'] = (d['sx'] * (1 - SMOOTHING)) + (itip.x * SMOOTHING)
                d['sy'] = (d['sy'] * (1 - SMOOTHING)) + (wrist.y * SMOOTHING)
                
                # Glide (Pitch Bend)
                diff_x = d['sx'] - d['x']
                if abs(diff_x) > 0.005:
                    bend = int(np.clip(diff_x * NUM_KEYS * 4000, -8191, 8191))
                    outport.send(mido.Message('pitchwheel', pitch=bend, channel=d['chan']))
                    active_gestures["GLIDE"] = True

                # Tilt (Pan - CC 10)
                tilt = int(np.clip((pts[4].y - pts[20].y) * 127 + 64, 0, 127))
                if send_throttled_cc(idx, 10, tilt, d['chan']): active_gestures["TILT"] = True

                # Raise (Expression - CC 11)
                vol = np.clip((1 - d['sy']) * 140, 30, 110)
                if send_throttled_cc(idx, 11, vol, d['chan']): active_gestures["RAISE"] = True
                
                # Slide (Timbre - CC 74)
                dist = np.linalg.norm(np.array([pts[0].x, pts[0].y]) - np.array([pts[8].x, pts[8].y]))
                slide = np.clip(dist * 400, 0, 127)
                if send_throttled_cc(idx, 74, slide, d['chan']): active_gestures["SLIDE"] = True

                mp_draw.draw_landmarks(frame, lms, mp_hands.HAND_CONNECTIONS)

    # --- DRAW HUD STATUS ---
    for i, (name, active) in enumerate(active_gestures.items()):
        color = (0, 255, 0) if active else (50, 50, 50)
        start_x = 20 + (i * 280)
        cv2.rectangle(frame, (start_x, 15), (start_x + 30, 45), color, -1)
        cv2.putText(frame, name, (start_x + 40, 40), 1, 1.2, (255, 255, 255), 2)

    # --- LIFT ---
    to_rem = [hid for hid in active_hands if hid not in current_ids]
    for hid in to_rem:
        ch = active_hands[hid]['chan']
        outport.send(mido.Message('note_off', note=active_hands[hid]['note'], channel=ch))
        outport.send(mido.Message('pitchwheel', pitch=0, channel=ch))
        # Reset expression to a safe level
        outport.send(mido.Message('control_change', control=11, value=64, channel=ch))
        del active_hands[hid]

    cv2.imshow('ROLI Airwave Pro HUD', frame)
    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()