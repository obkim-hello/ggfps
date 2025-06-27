from ultralytics import YOLO
import numpy as np

class DetectionEngine:
    """
    Runs the AI model to detect human-like objects in frames.
    """
    def __init__(self, model_path='yolov8n.pt'):
        # Load YOLOv8 model (or custom model)
        self.model = YOLO(model_path)
        self.target_classes = [0]  # COCO class 0 = 'person'

    def detect(self, frame):
        """
        Run YOLO detection and return bounding boxes for human-like objects.
        """
        results = self.model(frame)
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                if cls in self.target_classes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    bbox = [x1, y1, x2 - x1, y2 - y1]
                    label = r.names[cls]
                    confidence = float(box.conf[0])
                    detections.append({"bbox": bbox, "label": label, "confidence": confidence})
        return detections 