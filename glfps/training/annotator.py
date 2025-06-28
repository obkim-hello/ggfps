from PyQt5.QtWidgets import QFileDialog
import subprocess
import sys
import os
import shutil
import cv2

class Annotator:
    """
    Provides annotation tools for labeling human-like objects in images and videos.
    """
    def __init__(self):
        pass

    def annotate(self, parent=None):
        """Launch annotation tool for the given data path (file dialog or labelImg)."""
        file_path, _ = QFileDialog.getOpenFileName(parent, "Select Image or Video", "", "Images (*.png *.jpg *.jpeg);;Videos (*.mp4 *.avi)")
        if file_path:
            print(f"Selected for annotation: {file_path}")
            self.launch_labelimg(os.path.dirname(file_path))
            return file_path
        else:
            print("No file selected.")
            return None

    def launch_labelimg(self, folder):
        """Launch labelImg in the selected folder using the executable, searching PATH."""
        try:
            labelimg_path = shutil.which('labelImg')
            if not labelimg_path:
                print("labelImg executable not found in PATH. Please install it with 'pip install labelImg' and ensure it's in your PATH.")
                return
            subprocess.Popen([labelimg_path, folder])
        except Exception as e:
            print(f"Failed to launch labelImg: {e}")

    def start_training(self, data_path, model, epochs, batch, imgsz):
        """
        Start training a YOLOv8 model.
        Args:
            data_path (str): Path to the dataset YAML file.
            model (str): Model name or path.
            epochs (int): Number of training epochs.
            batch (int): Batch size.
            imgsz (int): Image size.
        """
        cmd = [
            'yolo', 'train',
            f'data=data.yaml',
            f'model={model}',
            f'epochs={epochs}',
            f'batch={batch}',
            'imgsz=640'
        ]
        try:
            subprocess.run(cmd, check=True)
            print("Training completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Training failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}") 