# Body Part Detection Training Guide

## Overview
This guide explains how to train custom body part detection models using the GLFPS application.

## 🎯 Supported Body Parts

The training system supports detection of the following body parts:

| Class ID | Body Part | Description |
|----------|-----------|-------------|
| 0 | head | Head (nose, eyes, ears) |
| 1 | face | Face (facial features) |
| 2 | torso | Torso (shoulders and hips) |
| 3 | left_arm | Left arm (shoulder to wrist) |
| 4 | right_arm | Right arm (shoulder to wrist) |
| 5 | left_leg | Left leg (hip to ankle) |
| 6 | right_leg | Right leg (hip to ankle) |
| 7 | left_hand | Left hand |
| 8 | right_hand | Right hand |
| 9 | left_foot | Left foot |
| 10 | right_foot | Right foot |
| 11 | body | Full body outline |
| 12 | person | Full person detection |

## 📁 Dataset Preparation

### 1. Data Organization
Organize your dataset in the following structure:
```
data/training/
├── train/
│   ├── images/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   └── labels/
│       ├── image1.txt
│       ├── image2.txt
│       └── ...
├── valid/
│   ├── images/
│   │   ├── val_image1.jpg
│   │   ├── val_image2.jpg
│   │   └── ...
│   └── labels/
│       ├── val_image1.txt
│       ├── val_image2.txt
│       └── ...
└── data.yaml
```

### 2. Image Requirements
- **Format**: JPG, PNG, JPEG
- **Size**: Recommended 640x640 or larger
- **Quality**: Clear, well-lit images
- **Variety**: Different poses, angles, lighting conditions

### 3. Label Format (YOLO)
Each image should have a corresponding `.txt` file with YOLO format annotations:
```
class_id x_center y_center width height
```

Example:
```
0 0.5 0.3 0.2 0.4  # head
2 0.5 0.6 0.3 0.5  # torso
3 0.3 0.5 0.15 0.3 # left_arm
```

## 🏷️ Annotation Process

### Using labelImg (Recommended)
1. Click "Annotate Data (labelImg)" in the Training tab
2. Select your images directory
3. Use labelImg to draw bounding boxes around body parts
4. Save annotations in YOLO format

**Installation**: `pip install labelImg`

## ⚙️ Training Configuration

### 1. Model Selection
Choose from available YOLOv8 models:
- **Pose Models** (Recommended for body parts):
  - `yolov8n-pose.pt` - Fastest, good for testing
  - `yolov8s-pose.pt` - Balanced speed/accuracy
  - `yolov8m-pose.pt` - Higher accuracy
  - `yolov8l-pose.pt` - Best accuracy, slower

- **Regular Detection Models**:
  - `yolov8n.pt` - Fastest
  - `yolov8s.pt` - Balanced
  - `yolov8m.pt` - Higher accuracy
  - `yolov8l.pt` - Best accuracy

### 2. Training Parameters

| Parameter | Recommended Value | Description |
|-----------|-------------------|-------------|
| Epochs | 100-200 | Number of training iterations |
| Batch Size | 16-32 | Images per batch (adjust based on GPU memory) |
| Image Size | 640 | Input image resolution |
| Learning Rate | 0.01 | Initial learning rate |
| Patience | 50 | Early stopping patience |

### 3. Advanced Parameters
- **Save Period**: Save model every N epochs (default: 10)
- **Validation Split**: 20% of data for validation
- **Augmentation**: Automatic data augmentation applied

## 🚀 Training Process

### 1. Setup Data Configuration
1. Prepare your dataset in the required directory structure
2. Create or select a `data.yaml` file with your class definitions
3. Ensure training/validation directories exist

### 2. Start Training
1. Select your model
2. Set training parameters
3. Click "🚀 Start Training"
4. Monitor progress in the log area

### 3. Monitor Training
- **Loss**: Should decrease over time
- **mAP**: Mean Average Precision (higher is better)
- **Validation**: Check for overfitting
- **Logs**: Real-time training progress

### 4. Stop Training
- Click "⏹️ Stop Training" to stop early
- Training auto-saves best model
- Check `runs/detect/train/` for results

## 📊 Training Results

### Output Directory
```
runs/detect/train/
├── weights/
│   ├── best.pt      # Best model
│   └── last.pt      # Last epoch model
├── results.png      # Training curves
├── confusion_matrix.png
└── ...
```

### Model Evaluation
- **best.pt**: Use this for inference
- **results.png**: Training metrics
- **confusion_matrix.png**: Class-wise performance

## 🔧 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size
   - Use smaller model (yolov8n)
   - Reduce image size

2. **Poor Detection Results**
   - Check annotation quality
   - Increase training data
   - Adjust learning rate
   - Train for more epochs

3. **Training Not Starting**
   - Verify data.yaml exists
   - Check file paths
   - Ensure images and labels match

4. **Overfitting**
   - Increase validation data
   - Reduce model complexity
   - Add data augmentation
   - Use early stopping

### Performance Tips

1. **Data Quality**
   - Use diverse, high-quality images
   - Ensure consistent annotations
   - Balance class distribution

2. **Training Strategy**
   - Start with pre-trained models
   - Use appropriate learning rate
   - Monitor validation metrics
   - Save best model only

3. **Hardware Requirements**
   - **Minimum**: CPU training (slow)
   - **Recommended**: GPU with 8GB+ VRAM
   - **Optimal**: RTX 3080/4090 or similar

## 📈 Expected Performance

### Typical Results (with good data)
- **mAP@0.5**: 0.7-0.9
- **Precision**: 0.8-0.95
- **Recall**: 0.7-0.9

### Training Time
- **yolov8n-pose**: 2-4 hours (100 epochs)
- **yolov8s-pose**: 4-8 hours (100 epochs)
- **yolov8m-pose**: 8-16 hours (100 epochs)

## 🎯 Next Steps

After training:
1. Test your model in the Video Test tab
2. Fine-tune parameters if needed
3. Export model for deployment
4. Integrate with automation features

For more advanced training options, refer to the [Ultralytics documentation](https://docs.ultralytics.com/). 