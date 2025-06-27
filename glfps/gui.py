from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QInputDialog, QMessageBox, QLineEdit, QTextEdit, QComboBox, QHBoxLayout, QGridLayout, QCheckBox
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
        self.model_select.addItems([
            "yolov8n-pose.pt",  # Default pose model for body parts
            "yolov8s-pose.pt", 
            "yolov8m-pose.pt",
            "yolov8l-pose.pt",
            "yolov8n.pt",       # Regular detection models
            "yolov8s.pt",
            "yolov8m.pt",
            "yolov8l.pt",
            "runs/detect/train8/weights/best.pt"  # Custom trained model
        ])
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
        
        # Detection mode for live detection
        self.detection_mode = QComboBox()
        self.detection_mode.addItems(["All Body Parts", "Person Only", "Custom Selection"])
        self.detection_mode.currentTextChanged.connect(self.on_detection_mode_changed)
        layout.addWidget(QLabel("Detection Mode:"))
        layout.addWidget(self.detection_mode)
        
        # Body part selection (for custom mode)
        self.body_part_checkboxes = {}
        body_parts = ['head', 'face', 'torso', 'left_arm', 'right_arm', 'left_leg', 'right_leg', 
                     'left_hand', 'right_hand', 'left_foot', 'right_foot', 'body']
        
        checkbox_layout = QGridLayout()
        for i, part in enumerate(body_parts):
            checkbox = QCheckBox(part.replace('_', ' ').title())
            checkbox.setChecked(True)
            checkbox.setEnabled(False)  # Disabled by default
            self.body_part_checkboxes[part] = checkbox
            checkbox_layout.addWidget(checkbox, i // 3, i % 3)
        
        layout.addWidget(QLabel("Body Parts (Custom Mode):"))
        layout.addLayout(checkbox_layout)
        
        self.start_btn = QPushButton("Start Detection")
        self.start_btn.clicked.connect(self.toggle_detection)
        layout.addWidget(self.start_btn)
        self.setLayout(layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.capturing = False
        self.capture = ScreenCapture(monitor_index=self.monitor_select.currentData())
        self.detector = DetectionEngine(model_path=self.model_select.currentText())
        self.window_name = "Live Detection - Body Parts"

    def on_detection_mode_changed(self, mode):
        """Enable/disable checkboxes based on detection mode"""
        if mode == "All Body Parts":
            for checkbox in self.body_part_checkboxes.values():
                checkbox.setChecked(True)
                checkbox.setEnabled(False)
        elif mode == "Person Only":
            for checkbox in self.body_part_checkboxes.values():
                checkbox.setChecked(False)
                checkbox.setEnabled(False)
        else:  # Custom Selection
            for checkbox in self.body_part_checkboxes.values():
                checkbox.setEnabled(True)

    def change_model(self, model_path):
        try:
            self.detector = DetectionEngine(model_path=model_path)
        except Exception as e:
            QMessageBox.warning(self, "Model Error", f"Failed to load model: {e}")

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
        
        # Get detection mode and target parts
        mode = self.detection_mode.currentText()
        if mode == "All Body Parts":
            detections = self.detector.detect(frame)
        elif mode == "Person Only":
            detections = [d for d in self.detector.detect(frame) if d["label"] == "person"]
        else:  # Custom Selection
            target_parts = [part for part, checkbox in self.body_part_checkboxes.items() 
                          if checkbox.isChecked()]
            detections = self.detector.detect_specific_parts(frame, target_parts)
        
        # Color mapping for different body parts
        colors = {
            'head': (255, 0, 0),      # Blue
            'face': (255, 0, 255),    # Magenta
            'torso': (0, 255, 0),     # Green
            'left_arm': (255, 165, 0), # Orange
            'right_arm': (255, 165, 0), # Orange
            'left_leg': (128, 0, 128), # Purple
            'right_leg': (128, 0, 128), # Purple
            'left_hand': (0, 255, 255), # Yellow
            'right_hand': (0, 255, 255), # Yellow
            'left_foot': (165, 42, 42), # Brown
            'right_foot': (165, 42, 42), # Brown
            'body': (0, 255, 0),      # Green
            'person': (0, 255, 0)     # Green
        }
        
        # Draw detections
        for det in detections:
            x, y, w, h = det["bbox"]
            label = det["label"]
            conf = det["confidence"]
            det_type = det.get("type", "unknown")
            
            # Get color for this body part
            color = colors.get(label, (0, 255, 0))
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw label with confidence
            label_text = f"{label.replace('_', ' ').title()} {int(conf * 100)}%"
            cv2.putText(frame, label_text, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Add type indicator for body parts
            if det_type == "body_part":
                cv2.circle(frame, (x + w - 5, y + 5), 3, (255, 255, 255), -1)
        
        cv2.imshow(self.window_name, frame)
        cv2.waitKey(1)

class TrainingTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Body Part Detection Training"))
        
        # Data preparation section
        layout.addWidget(QLabel("📁 Data Preparation"))
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
        
        # Data configuration section
        layout.addWidget(QLabel("⚙️ Data Configuration"))
        self.data_yaml_path = "data/training/data.yaml"
        self.select_data_yaml_btn = QPushButton("Select data.yaml")
        self.select_data_yaml_btn.clicked.connect(self.select_data_yaml)
        layout.addWidget(self.select_data_yaml_btn)
        self.data_yaml_label = QLabel(f"Data config: {self.data_yaml_path}")
        layout.addWidget(self.data_yaml_label)
        
        # Create data.yaml button
        self.create_data_yaml_btn = QPushButton("Create Body Part data.yaml")
        self.create_data_yaml_btn.clicked.connect(self.create_body_part_data_yaml)
        layout.addWidget(self.create_data_yaml_btn)
        
        # Training configuration section
        layout.addWidget(QLabel("🎯 Training Configuration"))
        
        # Model selection
        model_layout = QHBoxLayout()
        self.model_select = QComboBox()
        self.model_select.addItems([
            "yolov8n-pose.pt",  # Pose models for body parts
            "yolov8s-pose.pt", 
            "yolov8m-pose.pt",
            "yolov8l-pose.pt",
            "yolov8n.pt",       # Regular detection models
            "yolov8s.pt",
            "yolov8m.pt",
            "yolov8l.pt"
        ])
        model_layout.addWidget(QLabel("Model:"))
        model_layout.addWidget(self.model_select)
        layout.addLayout(model_layout)
        
        # Training parameters
        params_layout = QHBoxLayout()
        self.epochs_input = QLineEdit("100")
        self.epochs_input.setPlaceholderText("Epochs")
        params_layout.addWidget(QLabel("Epochs:"))
        params_layout.addWidget(self.epochs_input)
        
        self.batch_input = QLineEdit("16")
        self.batch_input.setPlaceholderText("Batch Size")
        params_layout.addWidget(QLabel("Batch Size:"))
        params_layout.addWidget(self.batch_input)
        
        self.img_size_input = QLineEdit("640")
        self.img_size_input.setPlaceholderText("Image Size")
        params_layout.addWidget(QLabel("Image Size:"))
        params_layout.addWidget(self.img_size_input)
        layout.addLayout(params_layout)
        
        # Advanced training options
        advanced_layout = QHBoxLayout()
        self.patience_input = QLineEdit("50")
        self.patience_input.setPlaceholderText("Patience")
        advanced_layout.addWidget(QLabel("Patience:"))
        advanced_layout.addWidget(self.patience_input)
        
        self.lr_input = QLineEdit("0.01")
        self.lr_input.setPlaceholderText("Learning Rate")
        advanced_layout.addWidget(QLabel("Learning Rate:"))
        advanced_layout.addWidget(self.lr_input)
        layout.addLayout(advanced_layout)
        
        # Training controls
        self.train_btn = QPushButton("🚀 Start Training")
        self.train_btn.clicked.connect(self.start_training)
        layout.addWidget(self.train_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop Training")
        self.stop_btn.clicked.connect(self.stop_training)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        # Progress and logs
        layout.addWidget(QLabel("📊 Training Progress"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(200)
        layout.addWidget(self.log_area)
        
        self.setLayout(layout)
        self.annotator = Annotator()
        self.last_annotated_file = None
        self.is_windows = platform.system() == 'Windows'
        self.training_process = None

    def create_body_part_data_yaml(self):
        """Create a data.yaml file for body part detection training."""
        try:
            # Get training data directory
            train_dir = QFileDialog.getExistingDirectory(self, "Select Training Images Directory", "data/training/")
            if not train_dir:
                return
            
            # Get validation data directory
            val_dir = QFileDialog.getExistingDirectory(self, "Select Validation Images Directory", "data/training/")
            if not val_dir:
                return
            
            # Body part classes
            body_part_classes = [
                'head', 'face', 'torso', 'left_arm', 'right_arm', 
                'left_leg', 'right_leg', 'left_hand', 'right_hand', 
                'left_foot', 'right_foot', 'body'
            ]
            
            # Create data.yaml content
            yaml_content = f"""# Body Part Detection Dataset Configuration
train: {os.path.relpath(train_dir, os.path.dirname(self.data_yaml_path))}
val: {os.path.relpath(val_dir, os.path.dirname(self.data_yaml_path))}

# Number of classes
nc: {len(body_part_classes)}

# Class names
names: {body_part_classes}

# Dataset info
dataset_type: body_part_detection
description: Custom body part detection dataset
"""
            
            # Save data.yaml
            with open(self.data_yaml_path, 'w') as f:
                f.write(yaml_content)
            
            self.data_yaml_label.setText(f"Data config: {self.data_yaml_path}")
            self.log_area.append(f"✓ Created body part data.yaml with {len(body_part_classes)} classes")
            QMessageBox.information(self, "Success", f"Created data.yaml with {len(body_part_classes)} body part classes")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create data.yaml: {e}")

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
        """Start the training process with proper error handling and progress monitoring."""
        if not os.path.exists(self.data_yaml_path):
            QMessageBox.warning(self, "Missing Data", "Please select or create a data.yaml file first.")
            return
        
        epochs = self.epochs_input.text()
        batch = self.batch_input.text()
        model = self.model_select.currentText()
        img_size = self.img_size_input.text()
        patience = self.patience_input.text()
        lr = self.lr_input.text()
        
        # Validate inputs
        try:
            int(epochs)
            int(batch)
            int(img_size)
            int(patience)
            float(lr)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for all parameters.")
            return
        
        # Build training command
        cmd = [
            'yolo', 'train',
            f'data={self.data_yaml_path}',
            f'model={model}',
            f'epochs={epochs}',
            f'batch={batch}',
            f'imgsz={img_size}',
            f'patience={patience}',
            f'lr0={lr}',
            'save=True',
            'save_period=10'
        ]
        
        self.log_area.append(f"🚀 Starting training...")
        self.log_area.append(f"Command: {' '.join(cmd)}")
        self.log_area.append("=" * 50)
        
        # Update UI
        self.train_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        try:
            # Start training process
            self.training_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                shell=self.is_windows,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor training progress
            for line in iter(self.training_process.stdout.readline, ''):
                if line:
                    self.log_area.append(line.strip())
                    # Auto-scroll to bottom
                    self.log_area.verticalScrollBar().setValue(
                        self.log_area.verticalScrollBar().maximum()
                    )
                    QApplication.processEvents()
            
            # Wait for process to complete
            self.training_process.wait()
            
            if self.training_process.returncode == 0:
                self.log_area.append("✅ Training completed successfully!")
                QMessageBox.information(self, "Training Complete", "Model training completed successfully!")
            else:
                self.log_area.append("❌ Training failed!")
                QMessageBox.warning(self, "Training Failed", "Model training failed. Check the logs for details.")
                
        except Exception as e:
            self.log_area.append(f"❌ Error during training: {e}")
            QMessageBox.warning(self, "Training Error", f"An error occurred during training: {e}")
        finally:
            # Reset UI
            self.train_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.training_process = None

    def stop_training(self):
        """Stop the current training process."""
        if self.training_process:
            try:
                self.training_process.terminate()
                self.log_area.append("⏹️ Training stopped by user.")
                QMessageBox.information(self, "Training Stopped", "Training process has been stopped.")
            except Exception as e:
                self.log_area.append(f"❌ Error stopping training: {e}")
            finally:
                self.train_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.training_process = None

class VideoTestTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Test Detection on Video"))
        self.video_path = None
        self.model_path = "yolov8n-pose.pt"  # Default to pose model
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
        
        # Body part selection
        layout.addWidget(QLabel("Select Body Parts to Detect:"))
        self.body_part_checkboxes = {}
        body_parts = ['head', 'face', 'torso', 'left_arm', 'right_arm', 'left_leg', 'right_leg', 
                     'left_hand', 'right_hand', 'left_foot', 'right_foot', 'body']
        
        checkbox_layout = QGridLayout()
        for i, part in enumerate(body_parts):
            checkbox = QCheckBox(part.replace('_', ' ').title())
            checkbox.setChecked(True)  # Default to all checked
            self.body_part_checkboxes[part] = checkbox
            checkbox_layout.addWidget(checkbox, i // 3, i % 3)
        
        layout.addLayout(checkbox_layout)
        
        # Detection mode
        self.detection_mode = QComboBox()
        self.detection_mode.addItems(["All Body Parts", "Person Only", "Custom Selection"])
        self.detection_mode.currentTextChanged.connect(self.on_detection_mode_changed)
        layout.addWidget(QLabel("Detection Mode:"))
        layout.addWidget(self.detection_mode)
        
        self.start_btn = QPushButton("Start Video Detection")
        self.start_btn.clicked.connect(self.run_detection)
        layout.addWidget(self.start_btn)
        self.setLayout(layout)
        self.is_windows = platform.system() == 'Windows'

    def on_detection_mode_changed(self, mode):
        """Enable/disable checkboxes based on detection mode"""
        if mode == "All Body Parts":
            for checkbox in self.body_part_checkboxes.values():
                checkbox.setChecked(True)
                checkbox.setEnabled(False)
        elif mode == "Person Only":
            for checkbox in self.body_part_checkboxes.values():
                checkbox.setChecked(False)
                checkbox.setEnabled(False)
        else:  # Custom Selection
            for checkbox in self.body_part_checkboxes.values():
                checkbox.setEnabled(True)

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Videos (*.mp4 *.avi *.mov)")
        if path:
            self.video_path = path
            self.video_label.setText(f"Video: {path}")

    def select_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Model File", "", "PyTorch Model (*.pt)")
        if path:
            self.model_path = path
            self.model_label.setText(f"Model: {path}")

    def run_detection(self):
        if not self.video_path:
            QMessageBox.warning(self, "Missing Input", "Please select a video file.")
            return
        
        from glfps.detection import DetectionEngine
        import cv2
        
        try:
            detector = DetectionEngine(model_path=self.model_path)
        except Exception as e:
            QMessageBox.warning(self, "Model Error", f"Failed to load model: {e}")
            return
        
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            QMessageBox.warning(self, "Error", "Failed to open video file.")
            return
        
        window_name = "Video Detection - Body Parts"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # Color mapping for different body parts
        colors = {
            'head': (255, 0, 0),      # Blue
            'face': (255, 0, 255),    # Magenta
            'torso': (0, 255, 0),     # Green
            'left_arm': (255, 165, 0), # Orange
            'right_arm': (255, 165, 0), # Orange
            'left_leg': (128, 0, 128), # Purple
            'right_leg': (128, 0, 128), # Purple
            'left_hand': (0, 255, 255), # Yellow
            'right_hand': (0, 255, 255), # Yellow
            'left_foot': (165, 42, 42), # Brown
            'right_foot': (165, 42, 42), # Brown
            'body': (0, 255, 0),      # Green
            'person': (0, 255, 0)     # Green
        }
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Get detection mode and target parts
            mode = self.detection_mode.currentText()
            if mode == "All Body Parts":
                detections = detector.detect(frame)
            elif mode == "Person Only":
                detections = [d for d in detector.detect(frame) if d["label"] == "person"]
            else:  # Custom Selection
                target_parts = [part for part, checkbox in self.body_part_checkboxes.items() 
                              if checkbox.isChecked()]
                detections = detector.detect_specific_parts(frame, target_parts)
            
            # Draw detections
            for det in detections:
                x, y, w, h = det["bbox"]
                label = det["label"]
                conf = det["confidence"]
                det_type = det.get("type", "unknown")
                
                # Get color for this body part
                color = colors.get(label, (0, 255, 0))
                
                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
                # Draw label with confidence
                label_text = f"{label.replace('_', ' ').title()} {int(conf * 100)}%"
                cv2.putText(frame, label_text, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Add type indicator
                if det_type == "body_part":
                    cv2.circle(frame, (x + w - 5, y + 5), 3, (255, 255, 255), -1)
            
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):  # Spacebar to pause
                cv2.waitKey(0)
        
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