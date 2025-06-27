# Architecture

## Main Components

- **Screen Capture Module**: Captures the screen in real-time for analysis.
- **Detection Engine**: Runs the AI model to detect human-like objects in the captured frames.
- **I/O Automation Module**: Executes customizable actions (mouse, keyboard) based on detection results.
- **GUI**: Allows users to configure detection, automation, and training settings.
- **Training Pipeline**: Handles data import, annotation, and model training.

## Data Flow
1. Screen is captured and frames are sent to the Detection Engine.
2. Detection Engine processes frames and identifies objects.
3. If a target is detected, the I/O Automation Module performs the configured action.
4. The GUI provides real-time feedback and control.

## Technologies
- Python 3.x
- PyQt5 or Tkinter (GUI)
- OpenCV (screen capture, image processing)
- PyTorch or TensorFlow (AI model)
- PyAutoGUI (automation)

See `TRAINING.md` for training details and `PACKAGING.md` for deployment. 