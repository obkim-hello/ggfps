import cv2
import numpy as np
import platform
import subprocess
import tempfile
import os
import time
from typing import Optional, Tuple

class ScreenCapture:
    """
    Enhanced screen capture that can capture windows on macOS with performance optimizations.
    """
    def __init__(self, monitor_index=1, max_fps=15):
        self.monitor_index = monitor_index
        self.is_macos = platform.system() == 'Darwin'
        self.is_windows = platform.system() == 'Windows'
        self.max_fps = max_fps
        self.last_capture_time = 0
        self.frame_interval = 1.0 / max_fps
        
        # Performance optimizations
        self.last_frame = None
        self.cache_duration = 0.1  # Cache frames for 100ms
        
        if self.is_macos:
            self._setup_macos_capture()
        else:
            self._setup_standard_capture()
    
    def _setup_macos_capture(self):
        """Setup macOS-specific screen capture methods."""
        try:
            # Try to use mss first (fastest method)
            from mss import mss
            self.sct = mss()
            self.monitor = self.sct.monitors[self.monitor_index]
            self.use_mss = True
            print("✅ Using mss for screen capture")
        except Exception as e:
            print(f"mss not available: {e}")
            self.use_mss = False
        
        # Setup alternative capture methods
        self._setup_screencapture()
    
    def _setup_standard_capture(self):
        """Setup standard screen capture for other platforms."""
        try:
            from mss import mss
            self.sct = mss()
            self.monitor = self.sct.monitors[self.monitor_index]
            self.use_mss = True
        except Exception as e:
            print(f"mss not available: {e}")
            self.use_mss = False
    
    def _setup_screencapture(self):
        """Setup screencapture command for macOS."""
        self.screencapture_path = None
        try:
            # Check if screencapture is available
            result = subprocess.run(['which', 'screencapture'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.screencapture_path = result.stdout.strip()
        except Exception as e:
            print(f"Could not find screencapture: {e}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Capture a frame from the screen with performance optimizations.
        Returns:
            numpy.ndarray: BGR image array or None if capture failed
        """
        current_time = time.time()
        
        # Check if we should skip this frame due to FPS limiting
        if current_time - self.last_capture_time < self.frame_interval:
            # Return cached frame if available
            if self.last_frame is not None:
                return self.last_frame.copy()
            return None
        
        # Check if we can use cached frame
        if (self.last_frame is not None and 
            current_time - self.last_capture_time < self.cache_duration):
            return self.last_frame.copy()
        
        # Perform actual capture
        if self.is_macos:
            frame = self._capture_macos()
        else:
            frame = self._capture_standard()
        
        if frame is not None and frame.size > 0:
            self.last_frame = frame.copy()
            self.last_capture_time = current_time
            return frame
        
        return None
    
    def _capture_macos(self) -> Optional[np.ndarray]:
        """Capture screen on macOS with multiple fallback methods."""
        # Method 1: Try mss first (fastest)
        if self.use_mss:
            try:
                frame = self._capture_with_mss()
                if frame is not None and frame.size > 0:
                    return frame
            except Exception as e:
                print(f"mss capture failed: {e}")
        
        # Method 2: Try screencapture command (slower, but more reliable)
        if self.screencapture_path:
            try:
                frame = self._capture_with_screencapture()
                if frame is not None and frame.size > 0:
                    return frame
            except Exception as e:
                print(f"screencapture failed: {e}")
        
        return None
    
    def _capture_with_mss(self) -> Optional[np.ndarray]:
        """Capture using mss library (optimized)."""
        try:
            sct_img = self.sct.grab(self.monitor)
            frame = np.array(sct_img)
            if frame.size == 0:
                return None
            # Convert BGRA to BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            return frame
        except Exception as e:
            print(f"mss capture error: {e}")
            return None
    
    def _capture_with_screencapture(self) -> Optional[np.ndarray]:
        """Capture using macOS screencapture command (fallback)."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            # Capture screen using screencapture
            cmd = [
                self.screencapture_path,
                '-x',  # Don't play sound
                '-R', f'{self.monitor["left"]},{self.monitor["top"]},{self.monitor["width"]},{self.monitor["height"]}',
                temp_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0 and os.path.exists(temp_path):
                # Read the captured image
                frame = cv2.imread(temp_path)
                # Clean up temporary file
                os.unlink(temp_path)
                return frame
            
            # Clean up if file exists
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
        except Exception as e:
            print(f"screencapture error: {e}")
        
        return None
    
    def _capture_standard(self) -> Optional[np.ndarray]:
        """Standard capture for non-macOS platforms."""
        if self.use_mss:
            try:
                sct_img = self.sct.grab(self.monitor)
                frame = np.array(sct_img)
                if frame.size == 0:
                    return None
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                return frame
            except Exception as e:
                print(f"Standard capture error: {e}")
        
        return None
    
    def set_monitor(self, monitor_index: int):
        """Change the monitor to capture."""
        self.monitor_index = monitor_index
        if hasattr(self, 'sct') and self.use_mss:
            try:
                self.monitor = self.sct.monitors[monitor_index]
                # Clear cache when changing monitors
                self.last_frame = None
                self.last_capture_time = 0
            except IndexError:
                print(f"Monitor {monitor_index} not available")
    
    def set_fps(self, fps: int):
        """Set the maximum capture frame rate."""
        self.max_fps = max(1, min(30, fps))  # Limit between 1-30 FPS
        self.frame_interval = 1.0 / self.max_fps
        print(f"Screen capture FPS set to {self.max_fps}")
    
    def get_available_monitors(self) -> list:
        """Get list of available monitors."""
        if hasattr(self, 'sct') and self.use_mss:
            return self.sct.monitors
        return []
    
    def get_monitor_info(self) -> dict:
        """Get current monitor information."""
        if hasattr(self, 'monitor'):
            return self.monitor
        return {}
    
    def test_capture(self) -> bool:
        """Test if screen capture is working."""
        frame = self.get_frame()
        return frame is not None and frame.size > 0 