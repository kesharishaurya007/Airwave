AirMIDI: Touchless Gesture Audio Engine

A Python-based virtual MIDI instrument that uses MediaPipe and OpenCV to translate hand gestures into real-time audio modulation. Built for zero-latency inference on Apple Silicon, it allows users to play notes and sculpt sound in mid-air without physical hardware.

Features & Gesture Controls

This application maps 3D hand coordinates to standard continuous MIDI CC parameters:

Pinch (Thumb + Index): Note On / Off (Trigger)

Slide (Horizontal X-Axis): Timbre (Hi-Fi / Lo-Fi Filter Cutoff)

Raise (Vertical Y-Axis): Expression / Volume

Glide (Depth Z-Axis): Pitchbend

Tilt (Wrist Rotation): Spatial Panning (Left / Right)

Setup Instructions

To run this project on your local machine, install the required Python dependencies:

pip install opencv-python mediapipe mido python-rtmidi numpy


macOS Users: You must enable the native virtual MIDI port to route gestures to your DAW. Open the Audio MIDI Setup app, click Window > Show MIDI Studio in the top menu bar, double-click the IAC Driver, and check Device is online.

Usage

Run the main script from your terminal. Ensure your hands are clearly visible to the webcam in a well-lit environment.

python main.py


Press q to close the camera feed and quit the application.

Academic Citation

This repository is the official codebase for the preprint paper: "Low-Latency Hand-Gesture Recognition for Real-Time Virtual MIDI Control Using MediaPipe and OpenCV on Consumer Apple Silicon".

If you use this code in your research, please cite:

@article{keshari2026airmidi,
  title={Low-Latency Hand-Gesture Recognition for Real-Time Virtual MIDI Control Using MediaPipe and OpenCV on Consumer Apple Silicon},
  author={Keshari, Shaurya},
  journal={OSF Preprints},
  year={2026},
  doi={https://doi.org/10.17605/OSF.IO/FTMY7}
}
