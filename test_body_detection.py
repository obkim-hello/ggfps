#!/usr/bin/env python3
"""
Test script for body part detection using YOLOv8 pose model.
"""

import cv2
import numpy as np
from glfps.detection import DetectionEngine

def test_body_detection():
    """Test body part detection on webcam or sample image."""
    
    # Initialize detection engine with pose model
    print("Loading YOLOv8 pose model...")
    detector = DetectionEngine(model_path="yolov8n-pose.pt")
    
    # Try to open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Webcam not available. Please provide a video file path.")
        video_path = input("Enter video file path (or press Enter to skip): ").strip()
        if video_path:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print("Failed to open video file.")
                return
        else:
            print("No video source available.")
            return
    
    print("Press 'q' to quit, 's' to save frame, 'b' to toggle body parts only")
    show_body_parts_only = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Get detections
        if show_body_parts_only:
            detections = detector.detect_specific_parts(frame, 
                ['head', 'face', 'torso', 'left_arm', 'right_arm', 'left_leg', 'right_leg', 
                 'left_hand', 'right_hand', 'left_foot', 'right_foot'])
        else:
            detections = detector.detect(frame)
        
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
        
        # Add mode indicator
        mode_text = "Body Parts Only" if show_body_parts_only else "All Detections"
        cv2.putText(frame, mode_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.imshow("Body Part Detection Test", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite("body_detection_test.jpg", frame)
            print("Frame saved as body_detection_test.jpg")
        elif key == ord('b'):
            show_body_parts_only = not show_body_parts_only
            print(f"Mode: {mode_text}")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_body_detection() 