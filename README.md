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
- **Data Preparation**: Extract frames from videos, annotate images
- **Model Training**: Train custom body part detection models
- **Progress Monitoring**: Real-time training logs and metrics
- **Model Selection**: Choose from YOLOv8 pose and detection models

### 4. Settings Tab
- Configure application settings

## Training Custom Models

### Quick Start Training
1. **Prepare Data**: Add images to `data/training/train/images/` and `data/training/valid/images/`
2. **Annotate**: Use the Training tab to annotate your images
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