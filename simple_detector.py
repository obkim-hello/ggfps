#!/usr/bin/env python3
"""
Simple Screen Detector GUI
A focused application for real-time screen detection with settings.
"""

import sys
import os
import platform
import cv2
import numpy as np
import pyautogui
import threading
import time
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QCheckBox, QGridLayout, QFileDialog, QMessageBox, 
                             QTabWidget, QSpinBox, QGroupBox, QSlider, QFormLayout,
                             QLineEdit, QTextEdit, QProgressBar, QSystemTrayIcon,
                             QMenu, QAction)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon, QColor

# Optional keyboard import for hotkeys
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    keyboard = None
    KEYBOARD_AVAILABLE = False
    print("⚠️ keyboard module not installed - hotkeys will use GUI-based detection only")

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from glfps.detection import DetectionEngine
from glfps.screen_capture import ScreenCapture
from glfps.automation import Automation
from glfps.training.annotator import Annotator

class MouseController:
    """Controls mouse movement based on detections."""
    
    def __init__(self):
        self.enabled = False
        self.current_detections = []
        self.last_position = None
        self.smoothing_factor = 0.3  # Lower = smoother movement
        self.confidence_threshold = 0.5
        self.debug_mode = False
        
        # Body part priority (lower number = higher priority)
        self.body_part_priority = {
            "head": 1,
            "face": 2,
            "torso": 3,
            "body": 4,
            "left_arm": 5,
            "right_arm": 6,
            "left_leg": 7,
            "right_leg": 8,
            "left_hand": 9,
            "right_hand": 10,
            "left_foot": 11,
            "right_foot": 12,
            "person": 13
        }
        
        # Scaling factors for coordinate conversion
        self.scale_factor_x = 1.0
        self.scale_factor_y = 1.0
        self.original_frame_size = None
        self.processed_frame_size = None
        
        # Monitor offset for multi-monitor setups
        self.monitor_offset_x = 0
        self.monitor_offset_y = 0
        
        # Targeting position (where to aim on the detection box)
        self.targeting_position = "Top-Right Corner"  # Default to top-right
        
        # Control thread
        self.control_thread = None
        self.running = False

    def start(self):
        """Start the mouse control thread."""
        if not self.running:
            self.running = True
            self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
            self.control_thread.start()
            print("🎯 Mouse control started")

    def stop(self):
        """Stop the mouse control thread."""
        self.running = False
        if self.control_thread:
            self.control_thread.join(timeout=1.0)
        print("🎯 Mouse control stopped")

    def _control_loop(self):
        """Main control loop for mouse movement."""
        while self.running:
            # Handle normal mouse movement if enabled
            if self.enabled:
                self._move_to_target()
            
            time.sleep(0.05)  # 20 FPS control loop

    def _move_to_target(self):
        """Move mouse to the highest confidence detection from selected body parts."""
        if not self.current_detections:
            return
        
        # Find the best target from selected body parts only
        best_target = None
        best_confidence = 0
        
        for detection in self.current_detections:
            label = detection['label']
            confidence = detection['confidence']
            
            # Only consider detections from selected body parts
            if label in self.body_part_priority and self.body_part_priority[label] < 999:
                # Check if this is a better target (higher confidence)
                if confidence > best_confidence and confidence > self.confidence_threshold:
                    best_target = detection
                    best_confidence = confidence
        
        if best_target:
            bbox = best_target['bbox']
            x, y, w, h = bbox
            
            # Calculate target coordinates based on selected position
            if self.targeting_position == "Center":
                target_x = x + w // 2
                target_y = y + h // 2
            elif self.targeting_position == "Top-Right Corner":
                target_x = x + w
                target_y = y
            elif self.targeting_position == "Top-Left Corner":
                target_x = x
                target_y = y
            elif self.targeting_position == "Bottom-Right Corner":
                target_x = x + w
                target_y = y + h
            elif self.targeting_position == "Bottom-Left Corner":
                target_x = x
                target_y = y + h
            elif self.targeting_position == "Top Edge":
                target_x = x + w // 2
                target_y = y
            elif self.targeting_position == "Right Edge":
                target_x = x + w
                target_y = y + h // 2
            else:  # Default to center
                target_x = x + w // 2
                target_y = y + h // 2
            
            # Scale coordinates to original screen coordinates
            screen_x, screen_y = self._scale_coordinates(target_x, target_y)
            
            # Add monitor offset for multi-monitor setups
            absolute_x = screen_x + self.monitor_offset_x
            absolute_y = screen_y + self.monitor_offset_y
            
            # Apply smoothing for natural movement
            if self.last_position:
                # Use exponential smoothing for more linear movement
                smooth_x = int(self.last_position[0] * (1 - self.smoothing_factor) + 
                             absolute_x * self.smoothing_factor)
                smooth_y = int(self.last_position[1] * (1 - self.smoothing_factor) + 
                             absolute_y * self.smoothing_factor)
            else:
                smooth_x, smooth_y = absolute_x, absolute_y
            
            # Move mouse to center of detection with longer duration for smoother movement
            try:
                # Calculate distance to determine movement duration
                distance = 0
                if self.last_position:
                    distance = ((smooth_x - self.last_position[0])**2 + 
                              (smooth_y - self.last_position[1])**2)**0.5
                    # Longer duration for longer distances, but cap at reasonable time
                    duration = min(0.1, max(0.02, distance / 1000))
                else:
                    duration = 0.05
                
                # Get current mouse position before moving
                current_mouse_pos = pyautogui.position()
                
                pyautogui.moveTo(smooth_x, smooth_y, duration=duration)
                self.last_position = (smooth_x, smooth_y)
                
                # Always show debug output for troubleshooting
                print(f"🎯 TARGETING DEBUG:")
                print(f"   Detection: {best_target['label']} (confidence: {best_confidence:.2f})")
                print(f"   Bounding Box: x={x}, y={y}, w={w}, h={h}")
                print(f"   Target Position: {self.targeting_position}")
                print(f"   Target Coords (processed): ({target_x}, {target_y})")
                print(f"   Scale factors: X={self.scale_factor_x:.2f}, Y={self.scale_factor_y:.2f}")
                print(f"   Screen coords (scaled): ({screen_x}, {screen_y})")
                print(f"   Monitor offset: ({self.monitor_offset_x}, {self.monitor_offset_y})")
                print(f"   Absolute coords: ({absolute_x}, {absolute_y})")
                print(f"   Smooth coords: ({smooth_x}, {smooth_y})")
                print(f"   Mouse before: {current_mouse_pos}")
                print(f"   Mouse after: {pyautogui.position()}")
                print(f"   Movement: duration={duration:.3f}s, distance={distance:.1f}px")
                print(f"   Target monitor: {'Secondary' if self.monitor_offset_x > 0 else 'Primary'}")
                print("---")
                
            except Exception as e:
                print(f"Mouse movement error: {e}")

    def update_detections(self, detections):
        """Update current detections for mouse control."""
        self.current_detections = detections

    def set_enabled(self, enabled):
        """Enable or disable mouse control."""
        self.enabled = enabled
        if not enabled:
            self.last_position = None

    def set_target_parts(self, parts):
        """Set allowed body parts for targeting based on user selection."""
        # Reset all priorities to 999 (not allowed)
        for part in self.body_part_priority:
            self.body_part_priority[part] = 999
        
        # Set selected parts to allowed (priority 1-999)
        for i, part in enumerate(parts):
            if part in self.body_part_priority:
                self.body_part_priority[part] = i + 1
        
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"🎯 Allowed target parts: {parts}")
            print(f"🎯 Priority mapping: {self.body_part_priority}")

    def set_smoothing(self, factor):
        """Set mouse movement smoothing factor (0-1)."""
        self.smoothing_factor = max(0.1, min(1.0, factor))

    def set_confidence_threshold(self, threshold):
        """Set minimum confidence threshold for targeting (0-1)."""
        self.confidence_threshold = max(0.1, min(1.0, threshold))

    def set_debug_mode(self, enabled):
        """Enable/disable debug output for targeting."""
        self.debug_mode = enabled

    def set_targeting_position(self, position):
        """Set the targeting position on the detection box."""
        self.targeting_position = position
        if self.debug_mode:
            print(f"🎯 Targeting position set to: {position}")

    def update_scaling_factors(self, original_size, processed_size):
        """Update scaling factors for coordinate conversion."""
        if original_size and processed_size:
            orig_width, orig_height = original_size
            proc_width, proc_height = processed_size
            
            self.scale_factor_x = orig_width / proc_width
            self.scale_factor_y = orig_height / proc_height
            self.original_frame_size = original_size
            self.processed_frame_size = processed_size
            
            print(f"📏 SCALING UPDATE:")
            print(f"   Original frame: {original_size}")
            print(f"   Processed frame: {processed_size}")
            print(f"   Scale factors: X={self.scale_factor_x:.2f}, Y={self.scale_factor_y:.2f}")

    def update_monitor_offset(self, monitor_info):
        """Update monitor offset for multi-monitor setups."""
        if monitor_info and 'left' in monitor_info and 'top' in monitor_info:
            self.monitor_offset_x = monitor_info['left']
            self.monitor_offset_y = monitor_info['top']
            print(f"📏 MONITOR OFFSET UPDATE:")
            print(f"   Monitor info: {monitor_info}")
            print(f"   Offset: ({self.monitor_offset_x}, {self.monitor_offset_y})")
        else:
            print(f"📏 MONITOR OFFSET: No monitor info available")
            self.monitor_offset_x = 0
            self.monitor_offset_y = 0

    def _scale_coordinates(self, x, y):
        """Scale coordinates from processed frame to original screen coordinates."""
        scaled_x = int(x * self.scale_factor_x)
        scaled_y = int(y * self.scale_factor_y)
        print(f"📏 COORDINATE SCALING:")
        print(f"   Input (processed): ({x}, {y})")
        print(f"   Scale factors: ({self.scale_factor_x:.2f}, {self.scale_factor_y:.2f})")
        print(f"   Output (scaled): ({scaled_x}, {scaled_y})")
        return scaled_x, scaled_y

class DetectionThread(QThread):
    """Thread for running detection to prevent GUI freezing."""
    frame_ready = pyqtSignal(np.ndarray, list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, screen_capture, detector, detection_mode, target_parts, mouse_controller):
        super().__init__()
        self.screen_capture = screen_capture
        self.detector = detector
        self.detection_mode = detection_mode
        self.target_parts = target_parts
        self.mouse_controller = mouse_controller
        self.running = False
        
    def run(self):
        self.running = True
        while self.running:
            try:
                frame = self.screen_capture.get_frame()
                if frame is None:
                    continue
                
                # Store original frame size
                original_height, original_width = frame.shape[:2]
                original_size = (original_width, original_height)
                
                # Resize for performance
                processed_frame = frame.copy()
                if original_width > 1280:
                    scale = 1280 / original_width
                    new_width = int(original_width * scale)
                    new_height = int(original_height * scale)
                    processed_frame = cv2.resize(frame, (new_width, new_height))
                
                processed_size = (processed_frame.shape[1], processed_frame.shape[0])
                
                # Update mouse controller with scaling information and monitor offset
                if self.mouse_controller:
                    self.mouse_controller.update_scaling_factors(original_size, processed_size)
                    # Get monitor information for coordinate offset
                    monitor_info = self.screen_capture.get_monitor_info()
                    self.mouse_controller.update_monitor_offset(monitor_info)
                
                # Run detection on processed frame
                if self.detection_mode == "All Body Parts":
                    detections = self.detector.detect(processed_frame)
                elif self.detection_mode == "Person Only":
                    detections = [d for d in self.detector.detect(processed_frame) if d["label"] == "person"]
                else:  # Custom Selection
                    print(f"🔍 Custom Selection Mode - Target parts: {self.target_parts}")
                    # Get all detections first
                    all_detections = self.detector.detect(processed_frame)
                    
                    # Filter based on target parts
                    detections = []
                    for det in all_detections:
                        if det["label"] in self.target_parts:
                            detections.append(det)
                    
                    print(f"🔍 Custom Selection - Found {len(detections)} detections")
                
                # Filter detections based on current checkbox states (for all modes)
                if self.detection_mode == "Custom Selection":
                    # Only show detections for checked body parts
                    filtered_detections = []
                    for det in detections:
                        if det["label"] in self.target_parts:
                            filtered_detections.append(det)
                    detections = filtered_detections
                    print(f"🔍 After filtering: {len(detections)} detections")
                elif self.detection_mode == "All Body Parts":
                    # For "All Body Parts" mode, still respect checkbox states if they were changed
                    if hasattr(self, 'target_parts') and self.target_parts:
                        filtered_detections = []
                        for det in detections:
                            if det["label"] in self.target_parts:
                                filtered_detections.append(det)
                        detections = filtered_detections
                        print(f"🔍 All Body Parts mode - Filtered to {len(detections)} detections")
                
                # Debug: Print detection info
                if detections:
                    print(f"🎯 Detection mode: {self.detection_mode}")
                    print(f"🎯 Found {len(detections)} detections:")
                    for det in detections[:3]:  # Show first 3 detections
                        print(f"   - {det['label']}: {det['confidence']:.2f}")
                else:
                    print(f"🎯 No detections found for current settings")
                
                # Update mouse controller with detections
                if self.mouse_controller:
                    self.mouse_controller.update_detections(detections)
                
                self.frame_ready.emit(processed_frame, detections)
                
            except Exception as e:
                self.error_occurred.emit(str(e))
                break
    
    def stop(self):
        """Stop the detection thread safely."""
        self.running = False
        # Give the thread a moment to finish gracefully
        if not self.wait(2000):  # Wait up to 2 seconds
            print("⚠️ Detection thread did not stop gracefully, terminating...")
            self.terminate()
            self.wait(1000)  # Wait for termination

class DetectionTab(QWidget):
    """Main detection interface."""
    
    def __init__(self):
        super().__init__()
        self.mouse_controller = MouseController()
        self.init_ui()
        self.detection_thread = None
        self.setup_hotkeys()
        
    def keyPressEvent(self, event):
        """Handle key press events for emergency stop."""
        if event.key() == Qt.Key_Escape:
            # Emergency stop when ESC is pressed
            self.emergency_stop()
        else:
            super().keyPressEvent(event)
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Set focus policy to receive keyboard events
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Title
        title = QLabel("Real-time Screen Detection")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        layout.addWidget(title)
        
        # Control Panel
        control_group = QGroupBox("Detection Controls")
        control_layout = QVBoxLayout()
        
        # Model and Monitor Selection
        top_row = QHBoxLayout()
        
        # Model selection
        model_layout = QVBoxLayout()
        model_layout.addWidget(QLabel("Detection Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "yolov8n-pose.pt", "yolov8s-pose.pt", "yolov8m-pose.pt", 
            "yolov8l-pose.pt", "yolov8x-pose.pt"
        ])
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_layout.addWidget(self.model_combo)
        
        # Model file picker
        self.model_picker_btn = QPushButton("Browse Model")
        self.model_picker_btn.clicked.connect(self.pick_model_file)
        model_layout.addWidget(self.model_picker_btn)
        
        top_row.addLayout(model_layout)
        
        # Monitor and FPS
        monitor_layout = QVBoxLayout()
        monitor_layout.addWidget(QLabel("Monitor:"))
        self.monitor_combo = QComboBox()
        self.monitor_combo.addItems(["Primary", "Secondary", "All"])
        self.monitor_combo.currentTextChanged.connect(self.on_monitor_changed)
        monitor_layout.addWidget(self.monitor_combo)
        
        # FPS control
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 30)
        self.fps_spinbox.setValue(10)
        self.fps_spinbox.valueChanged.connect(self.on_fps_changed)
        fps_layout.addWidget(self.fps_spinbox)
        monitor_layout.addLayout(fps_layout)
        
        top_row.addLayout(monitor_layout)
        
        # Test button
        test_layout = QVBoxLayout()
        test_layout.addWidget(QLabel("Test:"))
        self.test_btn = QPushButton("Test Capture")
        self.test_btn.clicked.connect(self.test_capture)
        test_layout.addWidget(self.test_btn)
        top_row.addLayout(test_layout)
        
        control_layout.addLayout(top_row)
        
        # Detection Mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Detection Mode:"))
        self.detection_mode = QComboBox()
        self.detection_mode.addItems(["All Body Parts", "Person Only", "Custom Selection"])
        self.detection_mode.currentTextChanged.connect(self.on_detection_mode_changed)
        mode_layout.addWidget(self.detection_mode)
        control_layout.addLayout(mode_layout)
        
        # Body Parts Selection
        self.body_parts_group = QGroupBox("Body Parts to Detect")
        self.body_parts_layout = QGridLayout()
        self.body_part_checkboxes = {}
        body_parts = ['person', 'head', 'face', 'torso', 'left_arm', 'right_arm', 'left_leg', 'right_leg', 
                     'left_hand', 'right_hand', 'left_foot', 'right_foot', 'body']
        
        for i, part in enumerate(body_parts):
            checkbox = QCheckBox(part.replace('_', ' ').title())
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.on_body_part_changed)
            self.body_part_checkboxes[part] = checkbox
            self.body_parts_layout.addWidget(checkbox, i // 4, i % 4)  # 4 columns instead of 3
        
        self.body_parts_group.setLayout(self.body_parts_layout)
        control_layout.addWidget(self.body_parts_group)
        
        # Mouse Control Section
        mouse_group = QGroupBox("Mouse Control")
        mouse_layout = QVBoxLayout()
        
        # Mouse control toggle
        mouse_toggle_layout = QHBoxLayout()
        self.mouse_control_checkbox = QCheckBox("Enable Mouse Control")
        self.mouse_control_checkbox.setChecked(False)
        self.mouse_control_checkbox.stateChanged.connect(self.on_mouse_control_toggled)
        mouse_toggle_layout.addWidget(self.mouse_control_checkbox)
        
        # Mouse control status
        self.mouse_status_label = QLabel("Status: Disabled")
        self.mouse_status_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        mouse_toggle_layout.addWidget(self.mouse_status_label)
        mouse_layout.addLayout(mouse_toggle_layout)
        
        # Mouse control info
        info_label = QLabel("Hotkeys: F1=Enable, F2=Disable, ESC=Emergency Stop")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        mouse_layout.addWidget(info_label)
        
        # Emergency Stop Button
        emergency_layout = QHBoxLayout()
        self.emergency_btn = QPushButton("🚨 EMERGENCY STOP")
        self.emergency_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #fff;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.emergency_btn.clicked.connect(self.emergency_stop)
        emergency_layout.addWidget(self.emergency_btn)
        
        # ESC key reminder
        esc_label = QLabel("(or press ESC key)")
        esc_label.setStyleSheet("color: #e74c3c; font-size: 12px; font-weight: bold;")
        emergency_layout.addWidget(esc_label)
        emergency_layout.addStretch()
        
        mouse_layout.addLayout(emergency_layout)
        
        mouse_group.setLayout(mouse_layout)
        control_layout.addWidget(mouse_group)
        
        # Start/Stop Button
        self.start_btn = QPushButton("Start Detection")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #fff;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.start_btn.clicked.connect(self.toggle_detection)
        control_layout.addWidget(self.start_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Status
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Keyboard focus indicator
        self.keyboard_status = QLabel("⌨️ Press ESC for emergency stop (when GUI is focused)")
        self.keyboard_status.setStyleSheet("color: #f39c12; font-size: 11px; font-weight: bold;")
        self.keyboard_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.keyboard_status)
        
        # Video Display
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ecf0f1;
            }
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("No video feed")
        layout.addWidget(self.video_label)
        
        self.setLayout(layout)
        
        # Initialize components
        self.screen_capture = None
        self.detector = None
        self.is_detecting = False
        
    def setup_hotkeys(self):
        """Setup global hotkeys for mouse control."""
        if not KEYBOARD_AVAILABLE:
            print("⚠️ keyboard module not available - using GUI-based key detection only")
            print("⚠️ ESC key will work when GUI is focused")
            self.setup_fallback_hotkeys()
            return
            
        try:
            # Enable mouse control
            keyboard.add_hotkey('f1', self.enable_mouse_control)
            # Disable mouse control
            keyboard.add_hotkey('f2', self.disable_mouse_control)
            # Emergency stop
            keyboard.add_hotkey('esc', self.emergency_stop)
            print("✅ Hotkeys registered: F1=Enable, F2=Disable, ESC=Emergency Stop")
        except Exception as e:
            print(f"⚠️ Failed to register hotkeys: {e}")
            print("⚠️ Hotkeys may not work on macOS due to permissions.")
            print("⚠️ You can still use the GUI controls to enable/disable mouse control.")
            print("⚠️ ESC key should still work for emergency stop via GUI focus.")
            # Create a fallback timer to check for key presses
            self.setup_fallback_hotkeys()
    
    def setup_fallback_hotkeys(self):
        """Setup fallback hotkey checking using a timer."""
        # For macOS, we'll rely on the GUI keyPressEvent instead
        # This is more reliable than trying to use global hotkeys
        print("⚠️ Using GUI-based key detection (ESC key will work when GUI is focused)")
        
        # Set focus policy to receive keyboard events
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Initialize key state tracking
        self.key_states = {}
        self.last_key_press = {}
    
    def enable_mouse_control(self):
        """Enable mouse control via hotkey."""
        print("🟢 Mouse control enabled via hotkey")
        self.mouse_control_checkbox.setChecked(True)
    
    def disable_mouse_control(self):
        """Disable mouse control via hotkey."""
        print("🔴 Mouse control disabled via hotkey")
        self.mouse_control_checkbox.setChecked(False)
    
    def emergency_stop(self):
        """Emergency stop - disable mouse control and stop detection."""
        print("🚨 EMERGENCY STOP ACTIVATED!")
        
        # Disable mouse control immediately
        self.mouse_control_checkbox.setChecked(False)
        if hasattr(self, 'mouse_controller'):
            self.mouse_controller.set_enabled(False)
            self.mouse_controller.stop()
        
        # Stop detection if running
        if self.is_detecting:
            self.toggle_detection()
        
        # Update status
        self.status_label.setText("Status: Emergency Stop - All systems disabled")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 12px; font-weight: bold;")
        
        # Update keyboard status
        self.keyboard_status.setText("🚨 EMERGENCY STOP ACTIVATED - All systems disabled")
        self.keyboard_status.setStyleSheet("color: #e74c3c; font-size: 12px; font-weight: bold;")
        
        # Show emergency stop message
        QMessageBox.critical(self, "Emergency Stop", 
                           "🚨 EMERGENCY STOP ACTIVATED!\n\n"
                           "All detection and mouse control has been disabled.\n"
                           "The application is now safe.")
        
        print("Emergency stop activated - all systems disabled")
    
    def reset_status(self):
        """Reset status indicators after emergency stop."""
        self.status_label.setText("Status: Ready")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        self.keyboard_status.setText("⌨️ Press ESC for emergency stop (when GUI is focused)")
        self.keyboard_status.setStyleSheet("color: #f39c12; font-size: 11px; font-weight: bold;")
    
    def on_mouse_control_toggled(self, state):
        """Handle mouse control checkbox toggle."""
        enabled = state == Qt.Checked
        self.mouse_controller.set_enabled(enabled)
        
        if enabled:
            self.mouse_status_label.setText("Status: Enabled")
            self.mouse_status_label.setStyleSheet("color: #27ae60; font-size: 12px;")
            if not self.mouse_controller.running:
                self.mouse_controller.start()
        else:
            self.mouse_status_label.setText("Status: Disabled")
            self.mouse_status_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        
    def on_model_changed(self, model_path):
        try:
            self.detector = DetectionEngine(model_path=model_path)
            self.status_label.setText(f"Model loaded: {model_path}")
        except Exception as e:
            self.status_label.setText(f"Error loading model: {e}")
            QMessageBox.warning(self, "Model Error", f"Failed to load model: {e}")
    
    def pick_model_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Model File", "", "PyTorch Model (*.pt)")
        if path:
            self.model_combo.setCurrentText(path)
    
    def on_monitor_changed(self, monitor_name):
        try:
            if monitor_name == "Primary":
                monitor_index = 1
            elif monitor_name == "Secondary":
                monitor_index = 2
            else:  # All
                monitor_index = 0
            
            self.screen_capture = ScreenCapture(monitor_index=monitor_index, max_fps=self.fps_spinbox.value())
            
            # Get and display monitor information
            monitor_info = self.screen_capture.get_monitor_info()
            if monitor_info:
                left = monitor_info.get('left', 0)
                top = monitor_info.get('top', 0)
                width = monitor_info.get('width', 1920)
                height = monitor_info.get('height', 1080)
                
                self.status_label.setText(f"Monitor {monitor_name}: {width}x{height} at ({left}, {top})")
                print(f"📺 Selected monitor {monitor_name}: {width}x{height} at ({left}, {top})")
                
                # Update mouse controller with monitor info
                if hasattr(self, 'mouse_controller'):
                    self.mouse_controller.update_monitor_offset(monitor_info)
                    print(f"📏 Updated mouse controller monitor offset: ({left}, {top})")
            else:
                self.status_label.setText(f"Monitor {monitor_name}: No info available")
                print(f"⚠️ No monitor info available for {monitor_name}")
                
        except Exception as e:
            self.status_label.setText(f"Error changing monitor: {e}")
            print(f"❌ Error changing monitor: {e}")
    
    def on_fps_changed(self, fps):
        if self.screen_capture is not None:
            self.screen_capture.set_fps(fps)
            self.status_label.setText(f"FPS set to {fps}")
    
    def on_detection_mode_changed(self, mode):
        if mode == "All Body Parts":
            # Check all body part checkboxes and disable them
            for checkbox in self.body_part_checkboxes.values():
                checkbox.setChecked(True)
                checkbox.setEnabled(False)
        elif mode == "Person Only":
            # Check only person checkbox and disable all
            for part, checkbox in self.body_part_checkboxes.items():
                if part == 'person':
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)
                    checkbox.setEnabled(False)
        else:  # Custom Selection
            # Enable all checkboxes and set some default selections
            for part, checkbox in self.body_part_checkboxes.items():
                checkbox.setEnabled(True)
                # Set head and face as default selections for precision targeting
                if part in ['head', 'face']:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)  # Don't check person or other body parts by default
        
        # Update the body parts group title to show current mode
        self.body_parts_group.setTitle(f"Body Parts to Detect ({mode})")
        
        # If detection is running, update the detection thread
        if hasattr(self, 'detection_thread') and self.detection_thread and self.detection_thread.isRunning():
            self.update_detection_targets()
        
        # Force update the UI
        self.body_parts_group.update()
    
    def update_detection_targets(self):
        """Update the target parts for the detection thread."""
        if hasattr(self, 'detection_thread') and self.detection_thread and self.detection_thread.isRunning():
            # Get current target parts based on checkboxes
            target_parts = [part for part, checkbox in self.body_part_checkboxes.items() 
                          if checkbox.isChecked()]
            
            # Update the detection thread's target parts
            self.detection_thread.target_parts = target_parts
            
            # Also update the mouse controller's target parts
            if self.mouse_controller:
                self.mouse_controller.set_target_parts(target_parts)
            
            print(f"🔄 Updated detection targets: {target_parts}")
    
    def test_capture(self):
        if self.screen_capture is None:
            self.screen_capture = ScreenCapture(monitor_index=1, max_fps=self.fps_spinbox.value())
        
        frame = self.screen_capture.get_frame()
        if frame is None:
            QMessageBox.warning(self, "Capture Error", 
                              "Failed to capture screen.\n\n"
                              "On macOS, check screen recording permissions.")
            return
        
        # Show test capture
        cv2.imshow("Test Capture", frame)
        cv2.waitKey(3000)
        cv2.destroyWindow("Test Capture")
        
        QMessageBox.information(self, "Test Result", 
                              f"Capture working!\n"
                              f"Frame size: {frame.shape[1]}x{frame.shape[0]}")
    
    def toggle_detection(self):
        if not self.is_detecting:
            # Reset status if it was in emergency stop
            if "Emergency Stop" in self.status_label.text():
                self.reset_status()
            
            # Initialize components
            if self.screen_capture is None:
                self.screen_capture = ScreenCapture(monitor_index=1, max_fps=self.fps_spinbox.value())
            
            if self.detector is None:
                try:
                    self.detector = DetectionEngine(model_path=self.model_combo.currentText())
                except Exception as e:
                    QMessageBox.warning(self, "Model Error", f"Failed to load model: {e}")
                    return
            
            # Test capture
            if not self.screen_capture.test_capture():
                QMessageBox.warning(self, "Capture Error", "Screen capture not working.")
                return
            
            # Start detection thread
            target_parts = [part for part, checkbox in self.body_part_checkboxes.items() 
                          if checkbox.isChecked()]
            
            self.detection_thread = DetectionThread(
                self.screen_capture, 
                self.detector, 
                self.detection_mode.currentText(),
                target_parts,
                self.mouse_controller
            )
            self.detection_thread.frame_ready.connect(self.update_frame)
            self.detection_thread.error_occurred.connect(self.on_detection_error)
            self.detection_thread.start()
            
            self.is_detecting = True
            self.start_btn.setText("Stop Detection")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: #fff;
                    border: none;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            self.status_label.setText("Detection running...")
        else:
            # Stop detection
            print("🛑 Stopping detection...")
            
            # Stop mouse controller first
            if hasattr(self, 'mouse_controller'):
                self.mouse_controller.set_enabled(False)
                self.mouse_controller.stop()
            
            # Stop detection thread
            if self.detection_thread:
                try:
                    self.detection_thread.stop()
                    if not self.detection_thread.wait(3000):  # Wait up to 3 seconds
                        print("⚠️ Force terminating detection thread...")
                        self.detection_thread.terminate()
                        self.detection_thread.wait(1000)
                except Exception as e:
                    print(f"⚠️ Error stopping detection thread: {e}")
                finally:
                    self.detection_thread = None
            
            # Reset state
            self.is_detecting = False
            self.start_btn.setText("Start Detection")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: #fff;
                    border: none;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
            """)
            self.status_label.setText("Status: Detection stopped")
            self.status_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
            self.video_label.setText("No video feed")
            print("✅ Detection stopped successfully")
    
    def update_frame(self, frame, detections):
        # Color mapping for body parts
        colors = {
            'head': (255, 0, 0), 'face': (255, 0, 255), 'torso': (0, 255, 0),
            'left_arm': (255, 165, 0), 'right_arm': (255, 165, 0),
            'left_leg': (128, 0, 128), 'right_leg': (128, 0, 128),
            'left_hand': (0, 255, 255), 'right_hand': (0, 255, 255),
            'left_foot': (165, 42, 42), 'right_foot': (165, 42, 42),
            'body': (0, 255, 0), 'person': (0, 255, 0)
        }
        
        # Draw detections
        for det in detections:
            x, y, w, h = det["bbox"]
            label = det["label"]
            conf = det["confidence"]
            
            color = colors.get(label, (0, 255, 0))
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            label_text = f"{label.replace('_', ' ').title()} {int(conf * 100)}%"
            cv2.putText(frame, label_text, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Convert to Qt format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale to fit label
        scaled_image = qt_image.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(QPixmap.fromImage(scaled_image))
    
    def on_detection_error(self, error_msg):
        self.status_label.setText(f"Detection error: {error_msg}")
        self.toggle_detection()  # Stop detection

    def on_body_part_changed(self, state):
        """Handle body part checkbox change."""
        # Find which checkbox was changed
        sender = self.sender()
        for part, checkbox in self.body_part_checkboxes.items():
            if checkbox == sender:
                print(f"🔄 Body part '{part}' changed to {'checked' if state == Qt.Checked else 'unchecked'}")
                # Update detection targets if detection is running
                if hasattr(self, 'detection_thread') and self.detection_thread and self.detection_thread.isRunning():
                    self.update_detection_targets()
                break

class SettingsTab(QWidget):
    """Settings interface."""
    
    def __init__(self, detection_tab=None):
        super().__init__()
        self.detection_tab = detection_tab
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Settings")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        layout.addWidget(title)
        
        # Mouse Control Settings
        mouse_group = QGroupBox("Mouse Control Settings")
        mouse_layout = QFormLayout()
        
        # Target body parts
        self.target_parts_combo = QComboBox()
        self.target_parts_combo.addItems([
            "Head & Face (Highest Priority)",
            "Head Only", 
            "Face Only",
            "Head, Face & Torso",
            "Torso Only",
            "Full Body Priority",
            "Legs Priority",
            "Arms Priority",
            "All Body Parts (Priority Order)"
        ])
        self.target_parts_combo.currentTextChanged.connect(self.on_target_parts_changed)
        mouse_layout.addRow("Target Priority:", self.target_parts_combo)
        
        # Mouse smoothing
        self.smoothing_slider = QSlider(Qt.Horizontal)
        self.smoothing_slider.setRange(10, 90)
        self.smoothing_slider.setValue(30)
        self.smoothing_slider.valueChanged.connect(self.on_smoothing_changed)
        mouse_layout.addRow("Mouse Smoothing:", self.smoothing_slider)
        
        self.smoothing_label = QLabel("30%")
        self.smoothing_slider.valueChanged.connect(
            lambda v: self.smoothing_label.setText(f"{v}%")
        )
        mouse_layout.addRow("", self.smoothing_label)
        
        # Minimum confidence for targeting
        self.target_confidence = QSlider(Qt.Horizontal)
        self.target_confidence.setRange(30, 90)
        self.target_confidence.setValue(50)
        self.target_confidence.valueChanged.connect(self.on_target_confidence_changed)
        mouse_layout.addRow("Target Confidence:", self.target_confidence)
        
        self.target_confidence_label = QLabel("50%")
        self.target_confidence.valueChanged.connect(
            lambda v: self.target_confidence_label.setText(f"{v}%")
        )
        mouse_layout.addRow("", self.target_confidence_label)
        
        # Debug mode for targeting
        self.debug_targeting = QCheckBox()
        self.debug_targeting.setChecked(False)
        self.debug_targeting.setToolTip("Show targeting information in console")
        self.debug_targeting.stateChanged.connect(self.on_debug_targeting_changed)
        mouse_layout.addRow("Debug Targeting:", self.debug_targeting)
        
        # Targeting position
        self.targeting_position_combo = QComboBox()
        self.targeting_position_combo.addItems([
            "Center",
            "Top-Right Corner",
            "Top-Left Corner", 
            "Bottom-Right Corner",
            "Bottom-Left Corner",
            "Top Edge",
            "Right Edge"
        ])
        self.targeting_position_combo.setCurrentText("Top-Right Corner")
        self.targeting_position_combo.currentTextChanged.connect(self.on_targeting_position_changed)
        mouse_layout.addRow("Target Position:", self.targeting_position_combo)
        
        mouse_group.setLayout(mouse_layout)
        layout.addWidget(mouse_group)
        
        # Performance Settings
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QFormLayout()
        
        self.default_fps = QSpinBox()
        self.default_fps.setRange(1, 30)
        self.default_fps.setValue(10)
        self.default_fps.setToolTip("Default FPS for screen capture")
        perf_layout.addRow("Default FPS:", self.default_fps)
        
        self.max_frame_width = QSpinBox()
        self.max_frame_width.setRange(640, 1920)
        self.max_frame_width.setValue(1280)
        self.max_frame_width.setToolTip("Maximum frame width for processing")
        perf_layout.addRow("Max Frame Width:", self.max_frame_width)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        # Detection Settings
        detect_group = QGroupBox("Detection Settings")
        detect_layout = QFormLayout()
        
        self.confidence_threshold = QSlider(Qt.Horizontal)
        self.confidence_threshold.setRange(10, 100)
        self.confidence_threshold.setValue(50)
        self.confidence_threshold.setToolTip("Minimum confidence threshold for detections")
        detect_layout.addRow("Confidence Threshold:", self.confidence_threshold)
        
        self.confidence_label = QLabel("50%")
        self.confidence_threshold.valueChanged.connect(
            lambda v: self.confidence_label.setText(f"{v}%")
        )
        detect_layout.addRow("", self.confidence_label)
        
        detect_group.setLayout(detect_layout)
        layout.addWidget(detect_group)
        
        # Display Settings
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout()
        
        self.show_confidence = QCheckBox()
        self.show_confidence.setChecked(True)
        self.show_confidence.setToolTip("Show confidence percentage on detections")
        display_layout.addRow("Show Confidence:", self.show_confidence)
        
        self.show_labels = QCheckBox()
        self.show_labels.setChecked(True)
        self.show_labels.setToolTip("Show detection labels")
        display_layout.addRow("Show Labels:", self.show_labels)
        
        self.show_target_indicator = QCheckBox()
        self.show_target_indicator.setChecked(True)
        self.show_target_indicator.setToolTip("Show targeting indicator on screen")
        display_layout.addRow("Show Target Indicator:", self.show_target_indicator)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # System Info
        info_group = QGroupBox("System Information")
        info_layout = QFormLayout()
        
        info_layout.addRow("Platform:", QLabel(platform.system()))
        info_layout.addRow("Python Version:", QLabel(platform.python_version()))
        
        # Check OpenCV version
        cv_version = cv2.__version__
        info_layout.addRow("OpenCV Version:", QLabel(cv_version))
        
        # Check PyAutoGUI version
        try:
            import pyautogui
            pyautogui_version = pyautogui.__version__
            info_layout.addRow("PyAutoGUI Version:", QLabel(pyautogui_version))
        except:
            info_layout.addRow("PyAutoGUI:", QLabel("Not installed"))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Save/Load Settings
        settings_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(self.save_btn)
        
        self.load_btn = QPushButton("Load Settings")
        self.load_btn.clicked.connect(self.load_settings)
        settings_layout.addWidget(self.load_btn)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_settings)
        settings_layout.addWidget(self.reset_btn)
        
        layout.addLayout(settings_layout)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        self.setLayout(layout)
    
    def on_target_parts_changed(self, selection):
        """Handle target body parts selection change."""
        if not self.detection_tab or not self.detection_tab.mouse_controller:
            return
            
        if selection == "Head & Face (Highest Priority)":
            target_parts = ['head', 'face']
        elif selection == "Head Only":
            target_parts = ['head']
        elif selection == "Face Only":
            target_parts = ['face']
        elif selection == "Head, Face & Torso":
            target_parts = ['head', 'face', 'torso']
        elif selection == "Torso Only":
            target_parts = ['torso']
        elif selection == "Full Body Priority":
            target_parts = ['head', 'face', 'torso', 'body']
        elif selection == "Legs Priority":
            target_parts = ['left_leg', 'right_leg']
        elif selection == "Arms Priority":
            target_parts = ['left_arm', 'right_arm']
        else:  # All Body Parts (Priority Order)
            target_parts = ['head', 'face', 'torso', 'body', 'left_leg', 'right_leg', 'left_arm', 'right_arm']
            
        self.detection_tab.mouse_controller.set_target_parts(target_parts)
    
    def on_smoothing_changed(self, value):
        """Handle mouse smoothing change."""
        if self.detection_tab and self.detection_tab.mouse_controller:
            smoothing_factor = value / 100.0
            self.detection_tab.mouse_controller.set_smoothing(smoothing_factor)
    
    def on_target_confidence_changed(self, value):
        """Handle target confidence threshold change."""
        if self.detection_tab and self.detection_tab.mouse_controller:
            confidence_threshold = value / 100.0
            self.detection_tab.mouse_controller.set_confidence_threshold(confidence_threshold)
    
    def on_debug_targeting_changed(self, state):
        """Handle debug targeting checkbox toggle."""
        if self.detection_tab and self.detection_tab.mouse_controller:
            self.detection_tab.mouse_controller.set_debug_mode(state == Qt.Checked)
    
    def on_targeting_position_changed(self, position):
        """Handle targeting position selection change."""
        if self.detection_tab and self.detection_tab.mouse_controller:
            self.detection_tab.mouse_controller.set_targeting_position(position)
    
    def save_settings(self):
        # TODO: Implement settings save
        QMessageBox.information(self, "Settings", "Settings saved!")
    
    def load_settings(self):
        # TODO: Implement settings load
        QMessageBox.information(self, "Settings", "Settings loaded!")
    
    def reset_settings(self):
        self.default_fps.setValue(10)
        self.max_frame_width.setValue(1280)
        self.confidence_threshold.setValue(50)
        self.smoothing_slider.setValue(30)
        self.target_confidence.setValue(50)
        self.debug_targeting.setChecked(False)
        self.show_confidence.setChecked(True)
        self.show_labels.setChecked(True)
        self.show_target_indicator.setChecked(True)
        QMessageBox.information(self, "Settings", "Settings reset to defaults!")

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Human Object Detection & Automation App")
        self.setGeometry(100, 100, 800, 600)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Add tabs
        self.detection_tab = DetectionTab()
        self.settings_tab = SettingsTab(self.detection_tab)
        
        self.tabs.addTab(self.detection_tab, "Detection")
        self.tabs.addTab(self.settings_tab, "Settings")
        
        # Setup system tray for global access
        self.setup_system_tray()
        
    def setup_system_tray(self):
        """Setup system tray icon for global access."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setToolTip("GLFPS Detection App")
            
            # Create tray menu
            tray_menu = QMenu()
            
            # Emergency stop action
            emergency_action = QAction("🚨 Emergency Stop", self)
            emergency_action.triggered.connect(self.emergency_stop_global)
            tray_menu.addAction(emergency_action)
            
            tray_menu.addSeparator()
            
            # Show/hide action
            show_action = QAction("Show/Hide", self)
            show_action.triggered.connect(self.toggle_visibility)
            tray_menu.addAction(show_action)
            
            # Quit action
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
            print("✅ System tray icon created - right-click for emergency stop")
    
    def emergency_stop_global(self):
        """Global emergency stop accessible from system tray."""
        print("🚨 GLOBAL EMERGENCY STOP ACTIVATED!")
        # Find the detection tab and trigger emergency stop
        for child in self.findChildren(DetectionTab):
            if hasattr(child, 'emergency_stop'):
                child.emergency_stop()
                break
    
    def toggle_visibility(self):
        """Toggle window visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def closeEvent(self, event):
        """Handle window close event."""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            # Hide instead of close if tray icon is available
            self.hide()
            event.ignore()
        else:
            event.accept()

def launch_gui():
    app = QApplication(sys.argv)
    app.setApplicationName("Simple Screen Detector")
    app.setApplicationVersion("1.0")

    # Dark mode palette
    dark_palette = app.palette()
    dark_palette.setColor(app.palette().Window, QColor(0, 0, 0))
    dark_palette.setColor(app.palette().WindowText, QColor(255, 255, 255))
    dark_palette.setColor(app.palette().Base, QColor(0, 0, 0))
    dark_palette.setColor(app.palette().AlternateBase, QColor(30, 30, 30))
    dark_palette.setColor(app.palette().ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(app.palette().ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(app.palette().Text, QColor(255, 255, 255))
    dark_palette.setColor(app.palette().Button, QColor(30, 30, 30))
    dark_palette.setColor(app.palette().ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(app.palette().BrightText, QColor(255, 0, 0))
    dark_palette.setColor(app.palette().Highlight, QColor(45, 140, 240))
    dark_palette.setColor(app.palette().HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)

    # Dark stylesheet for widgets
    app.setStyleSheet('''
        QMainWindow, QWidget, QTabWidget::pane, QGroupBox, QLabel, QComboBox, QSpinBox, QSlider, QLineEdit, QTextEdit {
            background-color: #181a1b;
            color: #f1f1f1;
            border: none;
        }
        QTabWidget::pane {
            background: #181a1b;
            border: 1px solid #232629;
        }
        QTabBar {
            background: #181a1b;
        }
        QTabBar::tab {
            background: #232629;
            color: #f1f1f1;
            padding: 8px 16px;
            margin-right: 2px;
            border-radius: 4px 4px 0 0;
            min-width: 120px;
        }
        QTabBar::tab:selected {
            background: #232629;
            color: #2d8cf0;
            border-bottom: 3px solid #2d8cf0;
        }
        QTabBar::tab:!selected {
            color: #f1f1f1;
            background: #232629;
        }
        QTabBar::tab:hover {
            background: #2a2d2f;
        }
        QGroupBox {
            border: 1px solid #232629;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #2d8cf0;
            color: #fff;
            border: none;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #1e6fb8;
        }
        QPushButton:pressed {
            background-color: #145388;
        }
        QCheckBox, QRadioButton {
            color: #f1f1f1;
        }
        QSlider::groove:horizontal {
            border: 1px solid #232629;
            height: 8px;
            background: #232629;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #2d8cf0;
            border: 1px solid #232629;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        QSpinBox, QLineEdit, QTextEdit {
            background: #232629;
            color: #f1f1f1;
            border: 1px solid #232629;
            border-radius: 4px;
        }
        QProgressBar {
            background: #232629;
            color: #f1f1f1;
            border: 1px solid #232629;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk {
            background: #2d8cf0;
            border-radius: 4px;
        }
    ''')

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    launch_gui() 