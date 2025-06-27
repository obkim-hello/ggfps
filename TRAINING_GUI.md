# Training GUI Plan

## Overview
This document outlines the plan for implementing a user-friendly training GUI for the human-object detection app. The goal is to allow users to easily manage training data, annotate, and train custom detection models directly from the GUI.

## Requirements
- **Training Data Folder:**
  - All training materials (videos and photos) will be stored in a dedicated folder (e.g., `data/training/`).
  - The GUI will allow users to select this folder and display its contents.
- **Annotation:**
  - Users can annotate images/videos using either the in-app annotation tool or labelImg.
  - Annotations will be saved in YOLO format in the same folder as the images.
- **Model Training:**
  - The TrainingTab will provide options to:
    - Select the training data folder.
    - Set training parameters (epochs, batch size, model type, etc.).
    - Start training with a button.
    - View training progress and logs in the GUI.
    - Save/export the trained model to the `models/` directory.

## TrainingTab GUI Features
- **Folder Selection:**
  - Button to select the training data folder (default: `data/training/`).
  - Display a list of images/videos in the selected folder.
- **Annotation Tools:**
  - Buttons to launch in-app annotation or labelImg for selected files.
- **Training Controls:**
  - Input fields for training parameters (epochs, batch size, etc.).
  - Button to start training.
  - Progress bar and log area to show training status and output.
- **Model Export:**
  - Button to export/save the trained model to the `models/` directory.

## Data Structure
```
data/
  training/
    image1.jpg
    image1.txt  # YOLO annotation
    video1.mp4
    ...
models/
  custom_model.pt
```

## Next Steps
- Implement the updated TrainingTab in the GUI according to this plan.
- Ensure all training data and annotations are organized in the specified folder structure.
- Integrate training logic and progress display in the GUI. 