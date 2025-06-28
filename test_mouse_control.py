#!/usr/bin/env python3
"""
Test script for mouse control functionality.
"""

import sys
import os
import time
import threading

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simple_detector import MouseController

def test_mouse_controller():
    """Test the mouse controller functionality."""
    print("Testing Mouse Controller...")
    
    # Create mouse controller
    controller = MouseController()
    
    # Test settings
    controller.set_target_parts(['head', 'face'])
    controller.set_smoothing(0.3)
    controller.set_confidence_threshold(0.5)
    
    # Create mock detections
    mock_detections = [
        {
            'label': 'head',
            'confidence': 0.8,
            'bbox': [100, 100, 50, 50]  # x, y, w, h
        },
        {
            'label': 'face',
            'confidence': 0.9,
            'bbox': [200, 200, 60, 60]
        }
    ]
    
    print("Mock detections created:")
    for det in mock_detections:
        print(f"  - {det['label']}: {det['confidence']:.1f} at {det['bbox']}")
    
    # Test targeting logic
    print("\nTesting targeting logic...")
    controller.update_detections(mock_detections)
    
    # Simulate mouse movement (without actually moving)
    print("Simulating mouse movement to target...")
    controller.enabled = True
    
    # Start controller
    controller.start()
    
    # Let it run for a few seconds
    print("Controller running for 3 seconds...")
    time.sleep(3)
    
    # Stop controller
    controller.stop()
    
    print("✅ Mouse controller test completed!")
    print("\nTo test with real detection:")
    print("1. Run: python3 simple_detector.py")
    print("2. Start detection")
    print("3. Enable mouse control")
    print("4. The mouse should move to detected head/face regions")

if __name__ == "__main__":
    test_mouse_controller() 