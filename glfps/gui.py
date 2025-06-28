import sys
import os
import platform
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QCheckBox, QGridLayout, QTextEdit, QFileDialog,
                             QMessageBox, QTabWidget, QProgressBar, QSpinBox,
                             QDoubleSpinBox, QGroupBox, QLineEdit)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np

# Import our modules
from glfps.detection import DetectionEngine
from glfps.screen_capture import ScreenCapture
from glfps.automation import Automation
from glfps.training.annotator import Annotator

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
        
        # Title
        title = QLabel("Real-time Body Part Detection")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["yolov8n-pose.pt", "yolov8s-pose.pt", "yolov8m-pose.pt", "yolov8l-pose.pt", "yolov8x-pose.pt"])
        self.model_combo.currentTextChanged.connect(self.change_model)
        model_layout.addWidget(self.model_combo)
        
        # Model file picker
        self.model_picker_btn = QPushButton("Browse Model")
        self.model_picker_btn.clicked.connect(self.pick_model_file)
        model_layout.addWidget(self.model_picker_btn)
        
        layout.addLayout(model_layout)
        
        # Monitor selection
        monitor_layout = QHBoxLayout()
        monitor_layout.addWidget(QLabel("Monitor:"))
        self.monitor_combo = QComboBox()
        self.monitor_combo.addItems(["Primary", "Secondary", "All"])
        self.monitor_combo.currentTextChanged.connect(self.change_monitor)
        monitor_layout.addWidget(self.monitor_combo)
        
        # FPS control
        monitor_layout.addWidget(QLabel("FPS:"))
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 30)
        self.fps_spinbox.setValue(10)  # Default to 10 FPS for better performance
        self.fps_spinbox.valueChanged.connect(self.change_fps)
        monitor_layout.addWidget(self.fps_spinbox)
        
        # Screen capture test button
        self.test_capture_btn = QPushButton("Test Capture")
        self.test_capture_btn.clicked.connect(self.test_screen_capture)
        monitor_layout.addWidget(self.test_capture_btn)
        
        layout.addLayout(monitor_layout)
        
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
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Detection")
        self.start_btn.clicked.connect(self.toggle_detection)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Detection")
        self.stop_btn.clicked.connect(self.toggle_detection)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        
        # Status and debug info
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)
        
        # Debug info for macOS
        if platform.system() == 'Darwin':
            self.debug_label = QLabel("macOS Debug: Check permissions for screen recording")
            self.debug_label.setStyleSheet("color: orange; font-size: 12px;")
            layout.addWidget(self.debug_label)
        
        # Video display
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid gray; background-color: black;")
        layout.addWidget(self.video_label)
        
        # Initialize components
        self.screen_capture = None
        self.detector = None
        self.is_detecting = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # Set layout
        self.setLayout(layout)

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
            self.status_label.setText(f"Status: Model loaded - {model_path}")
        except Exception as e:
            self.status_label.setText(f"Status: Error loading model - {e}")
            QMessageBox.warning(self, "Model Error", f"Failed to load model: {e}")

    def change_monitor(self, monitor_name):
        """Change the monitor to capture."""
        try:
            if monitor_name == "Primary":
                monitor_index = 1
            elif monitor_name == "Secondary":
                monitor_index = 2
            else:  # All
                monitor_index = 0
            
            self.screen_capture = ScreenCapture(monitor_index=monitor_index)
            self.status_label.setText(f"Status: Monitor changed to {monitor_name}")
            
            # Test capture
            if self.screen_capture.test_capture():
                self.status_label.setText(f"Status: Monitor {monitor_name} - Capture working")
            else:
                self.status_label.setText(f"Status: Monitor {monitor_name} - Capture failed")
                
        except Exception as e:
            self.status_label.setText(f"Status: Error changing monitor - {e}")

    def change_fps(self, fps):
        """Change the capture frame rate."""
        if self.screen_capture is not None:
            self.screen_capture.set_fps(fps)
            # Update timer interval
            timer_interval = max(16, int(1000 / fps))  # Minimum 16ms (60 FPS max)
            self.timer.setInterval(timer_interval)
            self.status_label.setText(f"Status: FPS set to {fps}")

    def toggle_detection(self):
        if not self.is_detecting:
            # Initialize components if needed
            if self.screen_capture is None:
                self.screen_capture = ScreenCapture(monitor_index=1, max_fps=self.fps_spinbox.value())
            
            if self.detector is None:
                try:
                    self.detector = DetectionEngine(model_path=self.model_combo.currentText())
                except Exception as e:
                    QMessageBox.warning(self, "Model Error", f"Failed to load model: {e}")
                    return
            
            # Test capture before starting
            if not self.screen_capture.test_capture():
                QMessageBox.warning(self, "Capture Error", "Screen capture is not working. Please check permissions.")
                return
            
            self.is_detecting = True
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Status: Detection running...")
            
            # Set timer interval based on FPS
            fps = self.fps_spinbox.value()
            timer_interval = max(16, int(1000 / fps))  # Minimum 16ms (60 FPS max)
            self.timer.start(timer_interval)
        else:
            self.is_detecting = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("Status: Detection stopped")
            self.timer.stop()
            cv2.destroyAllWindows()

    def update_frame(self):
        if not self.is_detecting or self.screen_capture is None or self.detector is None:
            return
        
        frame = self.screen_capture.get_frame()
        if frame is None or frame.size == 0:
            self.status_label.setText("Status: Capture failed - check permissions")
            return
        
        try:
            # Resize frame for faster processing (optional)
            height, width = frame.shape[:2]
            if width > 1280:  # Resize if too large for performance
                scale = 1280 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
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
                
                # Add type indicator
                if det_type == "body_part":
                    cv2.circle(frame, (x + w - 5, y + 5), 3, (255, 255, 255), -1)
            
            # Convert frame to Qt format for display (only if needed)
            if hasattr(self, 'video_label') and self.video_label.isVisible():
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Scale image to fit label while maintaining aspect ratio
                scaled_image = qt_image.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.video_label.setPixmap(QPixmap.fromImage(scaled_image))
            
            # Show in OpenCV window for debugging
            cv2.imshow("Live Detection - Body Parts", frame)
            cv2.waitKey(1)
            
        except Exception as e:
            self.status_label.setText(f"Status: Detection error - {e}")

    def pick_model_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Model File", "", "PyTorch Model (*.pt)")
        if path:
            self.model_combo.setCurrentText(path)
            self.change_model(path)

    def test_screen_capture(self):
        """Test screen capture functionality."""
        if self.screen_capture is None:
            self.screen_capture = ScreenCapture(monitor_index=1, max_fps=self.fps_spinbox.value())
        
        frame = self.screen_capture.get_frame()
        if frame is None or frame.size == 0:
            QMessageBox.warning(self, "Screen Capture Error", 
                              "Failed to capture screen frame.\n\n"
                              "On macOS, make sure to:\n"
                              "1. Grant screen recording permissions in System Preferences > Security & Privacy\n"
                              "2. Restart the application after granting permissions")
            return
        
        # Show test capture
        cv2.imshow("Test Capture", frame)
        cv2.waitKey(3000)  # Show for 3 seconds
        cv2.destroyWindow("Test Capture")
        
        QMessageBox.information(self, "Capture Test", 
                              f"Screen capture working!\n"
                              f"Frame size: {frame.shape[1]}x{frame.shape[0]}\n"
                              f"FPS: {self.fps_spinbox.value()}")

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

    def select_data_yaml(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select data.yaml", "data/training/", "YAML Files (*.yaml *.yml)")
        if path:
            self.data_yaml_path = path
            self.data_yaml_label.setText(f"Data config: {path}")

    def launch_annotator(self):
        self.annotator.annotate(self)
        self.annotate_btn.setText("Annotation Started (see console)")

    def start_training(self):
        """Start the training process with proper error handling and progress monitoring."""
        if not os.path.exists(self.data_yaml_path):
            QMessageBox.warning(self, "Missing Data", "Please select a data.yaml file first.")
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