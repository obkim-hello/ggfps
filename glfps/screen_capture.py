import numpy as np
from mss import mss
import cv2

class ScreenCapture:
    """
    Handles real-time screen capture for analysis, with monitor selection.
    """
    def __init__(self, monitor_index=1):
        self.sct = mss()
        self.monitor_index = monitor_index
        self.monitor = self.sct.monitors[self.monitor_index]

    def set_monitor(self, monitor_index):
        self.monitor_index = monitor_index
        self.monitor = self.sct.monitors[self.monitor_index]

    def get_frame(self):
        sct_img = self.sct.grab(self.monitor)
        frame = np.array(sct_img)
        if frame.size == 0:
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame 