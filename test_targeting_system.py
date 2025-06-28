#!/usr/bin/env python3
"""
Test script for the new targeting system with priority ranking.
"""

import sys
import os
import time
import threading

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test import with optional keyboard module
try:
    from simple_detector import MouseController
    print("✅ Successfully imported MouseController")
except ImportError as e:
    print(f"❌ Failed to import MouseController: {e}")
    sys.exit(1)

def test_priority_ranking():
    """Test the priority ranking system for body parts."""
    print("🎯 Testing Priority Ranking System")
    print("=" * 50)
    
    # Create mouse controller
    controller = MouseController()
    
    # Test different priority configurations
    test_configs = [
        ("Head & Face", ['head', 'face']),
        ("Head Only", ['head']),
        ("Torso Priority", ['torso']),
        ("Full Body", ['head', 'face', 'torso', 'body']),
        ("Legs Priority", ['left_leg', 'right_leg']),
        ("Arms Priority", ['left_arm', 'right_arm']),
        ("All Parts", ['head', 'face', 'torso', 'body', 'left_leg', 'right_leg', 'left_arm', 'right_arm'])
    ]
    
    for config_name, target_parts in test_configs:
        print(f"\n📋 Testing: {config_name}")
        controller.set_target_parts(target_parts)
        
        # Show priority mapping
        print("   Priority mapping:")
        for part, priority in sorted(controller.body_part_priority.items(), key=lambda x: x[1]):
            if priority < 999:  # Only show active priorities
                print(f"     {part}: {priority}")
    
    return True

def test_targeting_logic():
    """Test the targeting logic with mock detections."""
    print("\n🎯 Testing Targeting Logic")
    print("=" * 50)
    
    # Create mouse controller
    controller = MouseController()
    controller.set_debug_mode(True)  # Enable debug output
    
    # Set target parts
    controller.set_target_parts(['head', 'face', 'torso'])
    
    # Create mock detections with different priorities
    mock_detections = [
        {
            'label': 'torso',
            'confidence': 0.9,
            'bbox': [100, 100, 80, 120]  # x, y, w, h
        },
        {
            'label': 'head',
            'confidence': 0.7,
            'bbox': [120, 80, 40, 40]
        },
        {
            'label': 'face',
            'confidence': 0.8,
            'bbox': [125, 85, 30, 30]
        },
        {
            'label': 'left_arm',
            'confidence': 0.95,
            'bbox': [80, 120, 30, 60]
        }
    ]
    
    print("Mock detections created:")
    for det in mock_detections:
        priority = controller.body_part_priority.get(det['label'], 999)
        print(f"  - {det['label']}: confidence={det['confidence']:.1f}, priority={priority}, bbox={det['bbox']}")
    
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
    
    print("✅ Targeting logic test completed!")
    
    return True

def test_center_calculation():
    """Test that mouse moves to center of detections."""
    print("\n🎯 Testing Center Calculation")
    print("=" * 50)
    
    # Create mouse controller
    controller = MouseController()
    controller.set_debug_mode(True)
    
    # Test different bounding box sizes
    test_boxes = [
        ([100, 100, 50, 50], "Small box"),
        ([200, 150, 100, 80], "Medium box"),
        ([300, 200, 150, 120], "Large box"),
        ([400, 250, 200, 160], "Extra large box")
    ]
    
    for bbox, description in test_boxes:
        x, y, w, h = bbox
        center_x = x + w // 2
        center_y = y + h // 2
        
        print(f"\n{description}:")
        print(f"  Bounding box: {bbox}")
        print(f"  Calculated center: ({center_x}, {center_y})")
        
        # Create mock detection
        mock_detection = {
            'label': 'head',
            'confidence': 0.8,
            'bbox': bbox
        }
        
        controller.update_detections([mock_detection])
        controller.enabled = True
        controller.start()
        
        # Let it run briefly
        time.sleep(1)
        controller.stop()
    
    print("✅ Center calculation test completed!")
    
    return True

def test_confidence_threshold():
    """Test confidence threshold filtering."""
    print("\n🎯 Testing Confidence Threshold")
    print("=" * 50)
    
    # Create mouse controller
    controller = MouseController()
    controller.set_debug_mode(True)
    
    # Set high confidence threshold
    controller.set_confidence_threshold(0.8)
    print(f"Confidence threshold set to: {controller.confidence_threshold}")
    
    # Create detections with different confidence levels
    mock_detections = [
        {
            'label': 'head',
            'confidence': 0.6,  # Below threshold
            'bbox': [100, 100, 50, 50]
        },
        {
            'label': 'face',
            'confidence': 0.9,  # Above threshold
            'bbox': [200, 200, 40, 40]
        },
        {
            'label': 'torso',
            'confidence': 0.7,  # Below threshold
            'bbox': [150, 150, 80, 120]
        }
    ]
    
    print("Mock detections with different confidence levels:")
    for det in mock_detections:
        status = "✅ Above threshold" if det['confidence'] >= controller.confidence_threshold else "❌ Below threshold"
        print(f"  - {det['label']}: {det['confidence']:.1f} {status}")
    
    # Test targeting
    controller.update_detections(mock_detections)
    controller.enabled = True
    controller.start()
    
    print("Testing targeting with confidence threshold...")
    time.sleep(2)
    
    controller.stop()
    print("✅ Confidence threshold test completed!")
    
    return True

def main():
    """Run all targeting system tests."""
    print("🎯 Targeting System Test Suite")
    print("=" * 60)
    print("This test suite verifies the new targeting system with")
    print("priority ranking for human body parts.\n")
    
    # Run tests
    test_priority_ranking()
    test_targeting_logic()
    test_center_calculation()
    test_confidence_threshold()
    
    print("\n" + "=" * 60)
    print("✅ All targeting system tests completed!")
    print("\n📋 Summary of Targeting Features:")
    print("• Priority Ranking: Head > Face > Torso > Body > Legs > Arms > Hands > Feet")
    print("• Center Targeting: Mouse moves to center of bounding box")
    print("• Confidence Filtering: Only targets detections above threshold")
    print("• Smooth Movement: Natural mouse movement with smoothing")
    print("• Debug Mode: Console output shows targeting information")
    
    print("\n🎮 To test the full application:")
    print("1. Run: python3 simple_detector.py")
    print("2. Go to Settings tab")
    print("3. Select different Target Priority options")
    print("4. Enable Debug Targeting to see console output")
    print("5. Start detection and enable mouse control")
    print("6. Watch the mouse target the highest priority body part")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 