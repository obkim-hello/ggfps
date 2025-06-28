# Human Object Detection & Automation App

## Overview
This application captures your screen (screen sharing), detects human-like objects and body parts in real-time, and performs customizable I/O actions (mouse movement, key presses, etc.). It is cross-platform (macOS and Windows), built with Python, and features a user-friendly GUI.

## Features
- **Real-time screen capture and analysis**
- **Advanced body part detection** using YOLOv8 pose models:
  - Head, face, torso
  - Arms (left/right), hands (left/right)
  - Legs (left/right), feet (left/right)
  - Full body detection
- **Human-like object detection** using AI
- **Customizable automation** (mouse, keyboard)
- **Video detection** with body part filtering
- **Custom model training** for body part detection
- **GUI for configuration, training, and monitoring**
- **Easy packaging for macOS and Windows**

## Body Part Detection

The app now supports detailed body part detection using YOLOv8 pose models:

### Detected Body Parts:
- **Head** - Nose, eyes, ears
- **Face** - Facial features
- **Torso** - Shoulders and hips
- **Arms** - Left and right arms (shoulder to wrist)
- **Hands** - Left and right hands
- **Legs** - Left and right legs (hip to ankle)
- **Feet** - Left and right feet
- **Body** - Full body outline

### Detection Modes:
1. **All Body Parts** - Detect all available body parts
2. **Person Only** - Detect only full person bounding boxes
3. **Custom Selection** - Choose specific body parts to detect

### Color Coding:
- Head: Blue
- Face: Magenta
- Torso: Green
- Arms: Orange
- Legs: Purple
- Hands: Yellow
- Feet: Brown
- Person: Green

## Getting Started

### Prerequisites
```bash
pip install -r requirements.txt
```

**Note**: The `keyboard` module is optional and may not work on macOS due to permission restrictions. The application will work without it using GUI-based key detection.

### Download Models
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n-pose.pt')"
```

### Run the Application
```bash
python -m glfps
```

### Test Body Part Detection
```bash
python test_body_detection.py
```

### Test Stop Functionality
```bash
python test_stop_functionality.py
```

## Usage

### 1. Live Detection Tab
- Real-time body part detection from screen capture
- Model selection (pose models recommended)
- Detection mode selection
- Custom body part filtering

### 2. Video Test Tab
- Test detection on video files
- Customizable body part selection
- Color-coded detection display
- Pause/resume controls

### 3. Training Tab
- **Data Preparation**: Annotate images using labelImg
- **Model Training**: Train custom body part detection models
- **Progress Monitoring**: Real-time training logs and metrics
- **Model Selection**: Choose from YOLOv8 pose and detection models

### 4. Settings Tab
- Configure application settings

## Stop Functionality

The application provides multiple ways to stop detection and mouse control:

### Emergency Stop
- **ESC Key**: Press ESC when the GUI window is focused (works on all platforms)
- **Emergency Button**: Click the large red "🚨 EMERGENCY STOP" button
- **Both methods**: Immediately stop all detection and mouse control

### Normal Stop
- **Stop Detection Button**: Click to stop detection gracefully
- **Mouse Control Toggle**: Uncheck to disable mouse control only

### Visual Feedback
- Status indicators show current application state
- Color-coded feedback (red for emergency, green for running)
- Emergency stop dialog confirms action

For detailed information, see [STOP_FUNCTIONALITY_FIX.md](STOP_FUNCTIONALITY_FIX.md).

## Mouse Targeting System

The application features an intelligent mouse targeting system with priority ranking for human body parts:

### Priority Ranking (Highest to Lowest)
1. **Head** - Highest priority target
2. **Face** - Second highest priority
3. **Torso** - Body center
4. **Body** - Full body outline
5. **Legs** - Left and right legs
6. **Arms** - Left and right arms
7. **Hands** - Left and right hands
8. **Feet** - Left and right feet
9. **Person** - Full person (lowest priority)

### Targeting Features
- **Center Targeting**: Mouse moves to the exact center of detected bounding boxes
- **Priority Selection**: Always targets the highest priority body part available
- **Confidence Filtering**: Only targets detections above the confidence threshold
- **Smooth Movement**: Natural mouse movement with configurable smoothing
- **Debug Mode**: Console output shows targeting information

### Configuration Options
- **Target Priority**: Choose which body parts to prioritize
- **Mouse Smoothing**: Adjust movement smoothness (10-90%)
- **Target Confidence**: Set minimum confidence threshold (30-90%)
- **Debug Targeting**: Enable console output for targeting information

### Targeting Modes
- **Head & Face (Highest Priority)**: Target head and face only
- **Head Only**: Target head exclusively
- **Face Only**: Target face exclusively
- **Head, Face & Torso**: Target upper body parts
- **Torso Only**: Target body center
- **Full Body Priority**: Target all major body parts
- **Legs Priority**: Target leg regions
- **Arms Priority**: Target arm regions
- **All Body Parts (Priority Order)**: Target all parts in priority order

## Training Custom Models

### Quick Start Training
1. **Prepare Data**: Add images to `data/training/train/images/` and `data/training/valid/images/`
2. **Annotate**: Use labelImg to annotate your images (click "Annotate Data (labelImg)")
3. **Configure**: Select model and training parameters
4. **Train**: Click "Start Training" and monitor progress

### Supported Models
- **Pose Models** (Recommended): `yolov8n-pose.pt`, `yolov8s-pose.pt`, `yolov8m-pose.pt`, `yolov8l-pose.pt`
- **Detection Models**: `yolov8n.pt`, `yolov8s.pt`, `yolov8m.pt`, `yolov8l.pt`

### Training Parameters
- **Epochs**: 100-200 (recommended)
- **Batch Size**: 16-32 (adjust based on GPU memory)
- **Image Size**: 640 (default)
- **Learning Rate**: 0.01 (default)
- **Patience**: 50 (early stopping)

### Training Results
- Models saved to `runs/detect/train/weights/`
- Best model: `best.pt`
- Training metrics: `results.png`
- Confusion matrix: `confusion_matrix.png`

For detailed training instructions, see [TRAINING_GUIDE.md](TRAINING_GUIDE.md).

## Technical Details
See `ARCHITECTURE.md` for technical details and `PACKAGING.md` for packaging instructions. 