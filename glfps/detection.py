from ultralytics import YOLO
import numpy as np
import cv2

class DetectionEngine:
    """
    Runs the AI model to detect human-like objects and body parts in frames.
    """
    def __init__(self, model_path='yolov8n-pose.pt'):
        # Load YOLOv8 pose model for body part detection
        self.model = YOLO(model_path)
        self.target_classes = [0]  # COCO class 0 = 'person'
        
        # Body part keypoints mapping for YOLOv8 pose model
        self.body_parts = {
            0: "nose",
            1: "left_eye", 2: "right_eye",
            3: "left_ear", 4: "right_ear",
            5: "left_shoulder", 6: "right_shoulder",
            7: "left_elbow", 8: "right_elbow",
            9: "left_wrist", 10: "right_wrist",
            11: "left_hip", 12: "right_hip",
            13: "left_knee", 14: "right_knee",
            15: "left_ankle", 16: "right_ankle"
        }
        
        # Group body parts for detection
        self.body_part_groups = {
            "head": [0, 1, 2, 3, 4],  # nose, eyes, ears
            "face": [0, 1, 2, 3, 4],  # nose, eyes, ears
            "torso": [5, 6, 11, 12],  # shoulders and hips
            "left_arm": [5, 7, 9],    # left shoulder, elbow, wrist
            "right_arm": [6, 8, 10],  # right shoulder, elbow, wrist
            "left_leg": [11, 13, 15], # left hip, knee, ankle
            "right_leg": [12, 14, 16], # right hip, knee, ankle
            "left_hand": [9],         # left wrist
            "right_hand": [10],       # right wrist
            "left_foot": [15],        # left ankle
            "right_foot": [16],       # right ankle
            "body": [5, 6, 11, 12]    # torso
        }

    def detect(self, frame):
        """
        Run YOLO pose detection and return bounding boxes for human-like objects and body parts.
        """
        results = self.model(frame)
        detections = []
        
        for r in results:
            if hasattr(r, 'keypoints') and r.keypoints is not None:
                # Pose detection - extract body parts
                keypoints = r.keypoints.data[0] if len(r.keypoints.data) > 0 else None
                if keypoints is not None:
                    detections.extend(self._extract_body_parts(keypoints, frame.shape))
            
            # Also get person bounding boxes
            if hasattr(r, 'boxes') and r.boxes is not None:
                boxes = r.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    if cls in self.target_classes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        bbox = [x1, y1, x2 - x1, y2 - y1]
                        label = "person"
                        confidence = float(box.conf[0])
                        detections.append({
                            "bbox": bbox, 
                            "label": label, 
                            "confidence": confidence,
                            "type": "person"
                        })
        
        return detections

    def _extract_body_parts(self, keypoints, frame_shape):
        """
        Extract body part bounding boxes from keypoints.
        """
        detections = []
        height, width = frame_shape[:2]
        
        for part_name, keypoint_indices in self.body_part_groups.items():
            # Find valid keypoints for this body part
            valid_points = []
            for idx in keypoint_indices:
                if idx < len(keypoints):
                    kp = keypoints[idx]
                    if kp[2] > 0.5:  # Confidence threshold
                        valid_points.append([int(kp[0]), int(kp[1])])
            
            if valid_points:
                # Create bounding box around the body part
                x_coords = [p[0] for p in valid_points]
                y_coords = [p[1] for p in valid_points]
                
                x_min, x_max = max(0, min(x_coords)), min(width, max(x_coords))
                y_min, y_max = max(0, min(y_coords)), min(height, max(y_coords))
                
                # Add some padding around the body part
                padding = 10
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(width, x_max + padding)
                y_max = min(height, y_max + padding)
                
                bbox = [x_min, y_min, x_max - x_min, y_max - y_min]
                
                # Calculate average confidence
                confidences = [keypoints[idx][2] for idx in keypoint_indices if idx < len(keypoints) and keypoints[idx][2] > 0.5]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
                
                detections.append({
                    "bbox": bbox,
                    "label": part_name,
                    "confidence": float(avg_confidence),
                    "type": "body_part"
                })
        
        return detections

    def detect_specific_parts(self, frame, target_parts=None):
        """
        Detect specific body parts only.
        target_parts: list of body parts to detect (e.g., ['head', 'hand', 'foot'])
        """
        if target_parts is None:
            target_parts = ['head', 'hand', 'foot', 'leg', 'arm', 'torso', 'face', 'body']
        
        all_detections = self.detect(frame)
        filtered_detections = []
        
        for det in all_detections:
            if det["label"] in target_parts:
                filtered_detections.append(det)
        
        return filtered_detections 