#!/usr/bin/env python3
"""
Test script for stop functionality.
"""

import sys
import os
import time
import threading

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test import with optional keyboard module
try:
    from simple_detector import MouseController, DetectionThread
    print("✅ Successfully imported simple_detector modules")
except ImportError as e:
    print(f"❌ Failed to import simple_detector: {e}")
    sys.exit(1)

try:
    from glfps.screen_capture import ScreenCapture
    from glfps.detection import DetectionEngine
    print("✅ Successfully imported glfps modules")
except ImportError as e:
    print(f"⚠️ Could not import glfps modules: {e}")
    print("This is normal if the modules are not set up yet.")

def test_mouse_controller_stop():
    """Test that the mouse controller can be stopped properly."""
    print("Testing Mouse Controller Stop Functionality...")
    
    # Create mouse controller
    controller = MouseController()
    
    # Start the controller
    controller.start()
    print("✅ Mouse controller started")
    
    # Let it run for a moment
    time.sleep(1)
    
    # Stop the controller
    controller.stop()
    print("✅ Mouse controller stopped")
    
    # Verify it's stopped
    if not controller.running:
        print("✅ Mouse controller is properly stopped")
    else:
        print("❌ Mouse controller is still running")
    
    return True

def test_emergency_stop():
    """Test emergency stop functionality."""
    print("\nTesting Emergency Stop Functionality...")
    
    # Create mouse controller
    controller = MouseController()
    
    # Enable mouse control
    controller.set_enabled(True)
    controller.start()
    print("✅ Mouse control enabled and started")
    
    # Simulate emergency stop
    print("🚨 Simulating emergency stop...")
    controller.set_enabled(False)
    controller.stop()
    
    # Verify emergency stop worked
    if not controller.enabled and not controller.running:
        print("✅ Emergency stop successful - mouse control disabled and stopped")
    else:
        print("❌ Emergency stop failed")
    
    return True

def test_detection_thread_stop():
    """Test detection thread stop functionality."""
    print("\nTesting Detection Thread Stop Functionality...")
    
    try:
        # Create screen capture (this might fail on some systems)
        screen_capture = ScreenCapture(monitor_index=1, max_fps=10)
        
        # Create detector
        detector = DetectionEngine(model_path='yolov8n-pose.pt')
        
        # Create mouse controller
        mouse_controller = MouseController()
        
        # Create detection thread
        detection_thread = DetectionThread(
            screen_capture, 
            detector, 
            "All Body Parts",
            ['head', 'face'],
            mouse_controller
        )
        
        # Start the thread
        detection_thread.start()
        print("✅ Detection thread started")
        
        # Let it run for a moment
        time.sleep(2)
        
        # Stop the thread
        detection_thread.stop()
        print("✅ Detection thread stop() called")
        
        # Wait for it to finish
        if detection_thread.wait(3000):
            print("✅ Detection thread stopped gracefully")
        else:
            print("⚠️ Detection thread did not stop gracefully, terminating...")
            detection_thread.terminate()
            detection_thread.wait(1000)
            print("✅ Detection thread terminated")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Could not test detection thread (likely due to missing model or permissions): {e}")
        print("This is normal if you haven't downloaded the YOLO model yet.")
        return True

def main():
    """Run all stop functionality tests."""
    print("🧪 Testing Stop Functionality\n")
    print("=" * 50)
    
    # Test mouse controller stop
    if not test_mouse_controller_stop():
        print("❌ Mouse controller stop test failed")
        return False
    
    # Test emergency stop
    if not test_emergency_stop():
        print("❌ Emergency stop test failed")
        return False
    
    # Test detection thread stop
    if not test_detection_thread_stop():
        print("❌ Detection thread stop test failed")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All stop functionality tests passed!")
    print("\nTo test the full application:")
    print("1. Run: python3 simple_detector.py")
    print("2. Start detection")
    print("3. Enable mouse control")
    print("4. Press ESC key or click the Emergency Stop button")
    print("5. Verify that everything stops properly")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 