# Training Guide

## 1. Data Collection
- Import your own videos or photos via the GUI.
- Supported formats: .mp4, .avi, .jpg, .png, etc.

## 2. Annotation
- Use the built-in annotation tool to label human-like objects in your data.
- Save annotations in YOLO or COCO format.

## 3. Training
- Select your annotated dataset in the GUI.
- Choose model type (default: YOLOv5 or similar).
- Configure training parameters (epochs, batch size, etc.).
- Start training; progress and results are shown in the GUI.

## 4. Evaluation & Export
- Evaluate model performance on validation data.
- Export the trained model for use in the main app.

## 5. Retraining
- Add more data and repeat the process to improve accuracy.

**Dependencies:** PyTorch/TensorFlow, OpenCV, annotation tool (e.g., labelImg or custom GUI).

See `ARCHITECTURE.md` for integration details. 