# AirMIDI: Touchless Gesture-Based Audio Engine

Touchless virtual MIDI instrument and audio engine built with Python, MediaPipe, and OpenCV. Play notes and sculpt sound in mid-air using simple hand waves, pointing, and finger gestures. Features zero-touch, real-time control over spatial panning, Hi-Fi/Lo-Fi filtering, and dynamic audio modulation.

## Core Features
* **Zero-Latency Inference:** Optimized specifically for Apple Silicon (M1/M2) using MediaPipe Lite models to maintain >30 FPS.
* **Spatial Filtering:** Implements Exponential Moving Average (EMA) and deadband gating to eliminate landmark jitter during static hand holds.
* **Multi-Parameter Modulation:** Map complex 3D hand geometries to standard MIDI CC parameters for synth manipulation in any DAW (Ableton, Logic Pro, FL Studio).

## Gesture Mapping & Control Scheme
The system translates 3D spatial coordinates into continuous MIDI signals. 

| Physical Gesture | Spatial Axis / Metric | Musical Parameter / Action |
| :--- | :--- | :--- |
| **Pinch** (Thumb + Index) | Euclidean Distance ($d$) | Note On / Off (Trigger) |
| **Raise** (Vertical Move) | Y-Axis Translation | Expression / Volume |
| **Slide** (Horizontal Move) | X-Axis Translation | Timbre (Hi-Fi / Lo-Fi Filter Cutoff) |
| **Glide** (Z-Axis Depth) | Z-Axis Translation | Pitchbend |
| **Tilt** (Wrist Rotation) | Palm Angle / Roll | Spatial Pan (Left / Right) |

## Installation (macOS / Apple Silicon)

**1. Create a Virtual Environment (Recommended)**
```bash
python3 -m venv venv
source venv/bin/activate
