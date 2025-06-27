from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QInputDialog, QMessageBox, QLineEdit, QTextEdit, QComboBox, QHBoxLayout
from PyQt5.QtCore import QTimer
import sys
import cv2
from glfps.screen_capture import ScreenCapture
from glfps.detection import DetectionEngine
from glfps.training.annotator import Annotator
import subprocess
from mss import mss
import numpy as np
import os
import platform

def launch_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Human Object Detection & Automation App")
        self.setGeometry(100, 100, 800, 600)
        tabs = QTabWidget()
        tabs.addTab(DetectionTab(), "Detection")
        tabs.addTab(TrainingTab(), "Training")
        tabs.addTab(VideoTestTab(), "Video Test")
        tabs.addTab(SettingsTab(), "Settings")
        self.setCentralWidget(tabs)

class DetectionTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Live Detection: Select model and start")
        layout.addWidget(self.label)
        self.model_select = QComboBox()
        self.model_select.addItems([ "runs/detect/train6/weights/best.pt"])
        self.model_select.currentTextChanged.connect(self.change_model)
        layout.addWidget(QLabel("Detection Model:"))
        layout.addWidget(self.model_select)
        # Monitor selection
        self.sct = mss()
        self.monitor_select = QComboBox()
        for i, mon in enumerate(self.sct.monitors[1:], 1):
            self.monitor_select.addItem(f"Monitor {i}: {mon['width']}x{mon['height']}", i)
        self.monitor_select.currentIndexChanged.connect(self.change_monitor)
        layout.addWidget(QLabel("Screen to Record:"))
        layout.addWidget(self.monitor_select)
        self.start_btn = QPushButton("Start Detection")
        self.start_btn.clicked.connect(self.toggle_detection)
        layout.addWidget(self.start_btn)
        self.setLayout(layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.capturing = False
        self.capture = ScreenCapture(monitor_index=self.monitor_select.currentData())
        self.detector = DetectionEngine(model_path=self.model_select.currentText())
        self.window_name = "Live Detection"

    def change_model(self, model_path):
        self.detector = DetectionEngine(model_path=model_path)

    def change_monitor(self, idx):
        monitor_index = self.monitor_select.itemData(idx)
        if monitor_index is not None:
            self.capture.set_monitor(monitor_index)

    def toggle_detection(self):
        if not self.capturing:
            self.capturing = True
            self.start_btn.setText("Stop Detection")
            self.timer.start(100)
        else:
            self.capturing = False
            self.start_btn.setText("Start Detection")
            self.timer.stop()
            cv2.destroyWindow(self.window_name)

    def update_frame(self):
        frame = self.capture.get_frame()
        if frame is None or frame.size == 0:
            self.timer.stop()
            self.start_btn.setText("Start Detection")
            cv2.destroyWindow(self.window_name)
            QMessageBox.warning(self, "Screen Capture Error", "Failed to capture screen frame.")
            return
        detections = self.detector.detect(frame)
        for det in detections:
            x, y, w, h = det["bbox"]
            label = det["label"]
            conf = det["confidence"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.imshow(self.window_name, frame)
        cv2.waitKey(1)

class TrainingTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Training (to be implemented)"))
        self.annotate_btn = QPushButton("Annotate Data (labelImg)")
        self.annotate_btn.clicked.connect(self.launch_annotator)
        layout.addWidget(self.annotate_btn)
        self.inapp_annotate_btn = QPushButton("In-App Annotate")
        self.inapp_annotate_btn.clicked.connect(self.launch_inapp_annotator)
        layout.addWidget(self.inapp_annotate_btn)
        self.extract_frames_btn = QPushButton("Extract Frames from Video")
        self.extract_frames_btn.clicked.connect(self.extract_frames)
        layout.addWidget(self.extract_frames_btn)
        self.current_file_label = QLabel("Current file: None")
        layout.addWidget(self.current_file_label)
        # Data.yaml picker
        self.data_yaml_path = "data/training/data.yaml"
        self.select_data_yaml_btn = QPushButton("Select data.yaml")
        self.select_data_yaml_btn.clicked.connect(self.select_data_yaml)
        layout.addWidget(self.select_data_yaml_btn)
        self.data_yaml_label = QLabel(f"Data config: {self.data_yaml_path}")
        layout.addWidget(self.data_yaml_label)
        # Training controls
        params_layout = QHBoxLayout()
        self.epochs_input = QLineEdit("50")
        self.epochs_input.setPlaceholderText("Epochs")
        params_layout.addWidget(QLabel("Epochs:"))
        params_layout.addWidget(self.epochs_input)
        self.batch_input = QLineEdit("16")
        self.batch_input.setPlaceholderText("Batch Size")
        params_layout.addWidget(QLabel("Batch Size:"))
        params_layout.addWidget(self.batch_input)
        self.model_select = QComboBox()
        self.model_select.addItems(["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt"])  # Add more as needed
        params_layout.addWidget(QLabel("Model:"))
        params_layout.addWidget(self.model_select)
        layout.addLayout(params_layout)
        self.train_btn = QPushButton("Start Training")
        self.train_btn.clicked.connect(self.start_training)
        layout.addWidget(self.train_btn)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        self.setLayout(layout)
        self.annotator = Annotator()
        self.last_annotated_file = None
        self.is_windows = platform.system() == 'Windows'

    def select_data_yaml(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select data.yaml", "data/training/", "YAML Files (*.yaml *.yml)")
        if path:
            self.data_yaml_path = path
            self.data_yaml_label.setText(f"Data config: {path}")

    def launch_annotator(self):
        self.annotator.annotate(self)
        self.annotate_btn.setText("Annotation Started (see console)")

    def launch_inapp_annotator(self):
        self.annotator.in_app_annotate(self)

    def extract_frames(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Videos (*.mp4 *.avi *.mov)")
        if not video_path:
            return
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", "data/training/")
        if not output_folder:
            return
        interval, ok = QInputDialog.getInt(self, "Frame Interval", "Extract every Nth frame:", 30, 1, 1000, 1)
        if not ok:
            return
        saved = self.annotator.extract_frames_from_video(video_path, output_folder, interval)
        QMessageBox.information(self, "Extraction Complete", f"Extracted {saved} frames to {output_folder}")

    def start_training(self):
        epochs = self.epochs_input.text()
        batch = self.batch_input.text()
        model = self.model_select.currentText()
        cmd = [
            'yolo', 'train',
            f'data={self.data_yaml_path}',
            f'model={model}',
            f'epochs={epochs}',
            f'batch={batch}',
            'imgsz=640'
        ]
        self.log_area.append(f"Running: {' '.join(cmd)}")
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=self.is_windows)
            for line in iter(proc.stdout.readline, ''):
                self.log_area.append(line.strip())
                QApplication.processEvents()
            proc.stdout.close()
            proc.wait()
            self.log_area.append("Training complete.")
        except Exception as e:
            self.log_area.append(f"Error: {e}")

class VideoTestTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Test Detection on Video"))
        self.video_path = None
        self.model_path = "runs/detect/train/weights/best.pt"
        self.select_video_btn = QPushButton("Select Video")
        self.select_video_btn.clicked.connect(self.select_video)
        layout.addWidget(self.select_video_btn)
        self.video_label = QLabel("No video selected.")
        layout.addWidget(self.video_label)
        self.select_model_btn = QPushButton("Select Model (.pt)")
        self.select_model_btn.clicked.connect(self.select_model)
        layout.addWidget(self.select_model_btn)
        self.model_label = QLabel(f"Model: {self.model_path}")
        layout.addWidget(self.model_label)
        self.start_btn = QPushButton("Start Video Detection")
        self.start_btn.clicked.connect(self.run_detection)
        layout.addWidget(self.start_btn)
        self.setLayout(layout)
        self.is_windows = platform.system() == 'Windows'

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Videos (*.mp4 *.avi *.mov)")
        if path:
            self.video_path = path
            self.video_label.setText(f"Video: {path}")

    def select_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Model File", "runs/detect/", "PyTorch Model (*.pt)")
        if path:
            self.model_path = path
            self.model_label.setText(f"Model: {path}")

    def run_detection(self):
        if not self.video_path or not self.model_path:
            QMessageBox.warning(self, "Missing Input", "Please select both a video and a model.")
            return
        from glfps.detection import DetectionEngine
        import cv2
        detector = DetectionEngine(model_path=self.model_path)
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            QMessageBox.warning(self, "Error", "Failed to open video file.")
            return
        window_name = "Video Detection"
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            detections = detector.detect(frame)
            for det in detections:
                x, y, w, h = det["bbox"]
                label = det["label"]
                conf = det["confidence"]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {int(conf * 100)}%", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyWindow(window_name)

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Settings (to be implemented)"))
        self.setLayout(layout)

class ScreenCapture:
    def __init__(self, monitor_index):
        self.sct = mss()
        self.monitor = self.sct.monitors[monitor_index]

    def get_frame(self):
        sct_img = self.sct.grab(self.monitor)
        frame = np.array(sct_img)
        if frame.size == 0:
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame

    def set_monitor(self, monitor_index):
        self.monitor = self.sct.monitors[monitor_index] 