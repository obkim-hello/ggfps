#!/usr/bin/env python3
"""
Test script for enhanced screen capture functionality.
This will help diagnose screen capture issues on macOS.
"""

import cv2
import numpy as np
import platform
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from glfps.screen_capture import ScreenCapture

def test_screen_capture():
    """Test the enhanced screen capture functionality."""
    print(f"Testing screen capture on {platform.system()}")
    print(f"Python version: {sys.version}")
    
    # Test different monitor indices
    for monitor_index in [0, 1, 2]:
        print(f"\n--- Testing Monitor {monitor_index} ---")
        
        try:
            # Create screen capture instance
            capture = ScreenCapture(monitor_index=monitor_index)
            
            # Get monitor info
            monitor_info = capture.get_monitor_info()
            print(f"Monitor info: {monitor_info}")
            
            # Test capture
            print("Attempting to capture frame...")
            frame = capture.get_frame()
            
            if frame is not None and frame.size > 0:
                print(f"✅ Success! Frame size: {frame.shape[1]}x{frame.shape[0]}")
                
                # Save test image
                test_filename = f"test_capture_monitor_{monitor_index}.png"
                cv2.imwrite(test_filename, frame)
                print(f"Saved test image: {test_filename}")
                
                # Show frame briefly
                cv2.imshow(f"Monitor {monitor_index} Test", frame)
                cv2.waitKey(2000)  # Show for 2 seconds
                cv2.destroyAllWindows()
                
            else:
                print("❌ Failed to capture frame")
                
        except Exception as e:
            print(f"❌ Error testing monitor {monitor_index}: {e}")
    
    print("\n--- Testing Complete ---")
    print("\nIf capture failed, on macOS make sure to:")
    print("1. Go to System Preferences > Security & Privacy > Privacy")
    print("2. Select 'Screen Recording' from the left sidebar")
    print("3. Add your Python/Terminal application to the list")
    print("4. Restart your terminal/application")

if __name__ == "__main__":
    test_screen_capture() 