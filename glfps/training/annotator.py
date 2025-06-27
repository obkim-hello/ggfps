from PyQt5.QtWidgets import QFileDialog, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QApplication
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage
from PyQt5.QtCore import Qt, QRect
import subprocess
import sys
import os
import shutil
import cv2

class AnnotationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("In-App Annotation Tool")
        self.setGeometry(200, 200, 1000, 800)
        self.image_path = None
        self.image = None
        self.boxes = []  # (x1, y1, x2, y2)
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.label = 0  # Default to class 0 (person)

        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.img_label.setMouseTracking(True)
        self.setCentralWidget(self.img_label)

        self.open_image()

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_path = file_path
            self.image = QPixmap(file_path)
            self.img_label.setPixmap(self.image)
            self.boxes = []
        else:
            self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.image is not None:
            pos = self.img_label.mapFromParent(event.pos())
            self.drawing = True
            self.start_point = pos
            self.end_point = pos

    def mouseMoveEvent(self, event):
        if self.drawing and self.image is not None:
            pos = self.img_label.mapFromParent(event.pos())
            self.end_point = pos
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing and self.image is not None:
            pos = self.img_label.mapFromParent(event.pos())
            self.end_point = pos
            self.drawing = False
            x1 = self.start_point.x()
            y1 = self.start_point.y()
            x2 = self.end_point.x()
            y2 = self.end_point.y()
            self.boxes.append((x1, y1, x2, y2))
            self.update()

    def paintEvent(self, event):
        if self.image is not None:
            pixmap = QPixmap(self.image)
            painter = QPainter(pixmap)
            pen = QPen(Qt.red, 2)
            painter.setPen(pen)
            for box in self.boxes:
                rect = QRect(int(box[0]), int(box[1]), int(box[2] - box[0]), int(box[3] - box[1]))
                painter.drawRect(rect)
            if self.drawing and self.start_point and self.end_point:
                rect = QRect(int(self.start_point.x()), int(self.start_point.y()), int(self.end_point.x() - self.start_point.x()), int(self.end_point.y() - self.start_point.y()))
                painter.drawRect(rect)
            painter.end()
            self.img_label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S:
            self.save_annotations()
        elif event.key() == Qt.Key_Escape:
            self.close()

    def save_annotations(self):
        if not self.image_path or not self.boxes:
            return
        img = QImage(self.image_path)
        w, h = img.width(), img.height()
        yolo_lines = []
        for box in self.boxes:
            x1, y1, x2, y2 = box
            x_center = ((x1 + x2) / 2) / w
            y_center = ((y1 + y2) / 2) / h
            bw = abs(x2 - x1) / w
            bh = abs(y2 - y1) / h
            yolo_lines.append(f"{self.label} {x_center} {y_center} {bw} {bh}")
        txt_path = os.path.splitext(self.image_path)[0] + ".txt"
        with open(txt_path, "w") as f:
            f.write("\n".join(yolo_lines))
        self.setWindowTitle(f"Saved: {txt_path}")

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

    def in_app_annotate(self, parent=None):
        window = AnnotationWindow()
        window.show()
        return window.image_path if hasattr(window, 'image_path') else None

    def extract_frames_from_video(self, video_path, output_folder, interval=30):
        """
        Extract frames from a video file every 'interval' frames and save as images.
        Args:
            video_path (str): Path to the video file.
            output_folder (str): Directory to save frames.
            interval (int): Save every Nth frame.
        Returns:
            int: Number of frames extracted.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Failed to open video: {video_path}")
            return 0
        count = 0
        saved = 0
        base = os.path.splitext(os.path.basename(video_path))[0]
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if count % interval == 0:
                frame_name = f"{base}_frame_{count:05d}.jpg"
                frame_path = os.path.join(output_folder, frame_name)
                cv2.imwrite(frame_path, frame)
                saved += 1
            count += 1
        cap.release()
        print(f"Extracted {saved} frames to {output_folder}")
        return saved

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