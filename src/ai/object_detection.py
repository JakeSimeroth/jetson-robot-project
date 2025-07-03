#!/usr/bin/env python3

import cv2
import numpy as np
import logging
from typing import List, Tuple, Optional

class ObjectDetector:
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.net = None
        self.logger = logging.getLogger(__name__)
        self.classes = []
        
    def load_yolo_model(self, weights_path: str, config_path: str, names_path: str):
        """Load YOLO model for object detection"""
        try:
            self.net = cv2.dnn.readNet(weights_path, config_path)
            
            # Load class names
            with open(names_path, 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]
                
            self.logger.info("YOLO model loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load YOLO model: {e}")
            return False
            
    def detect_objects(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> List[dict]:
        """Detect objects in frame"""
        if self.net is None:
            return []
            
        height, width = frame.shape[:2]
        
        # Create blob from frame
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        
        # Run inference
        outputs = self.net.forward()
        
        # Process detections
        detections = []
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > confidence_threshold:
                    # Get bounding box coordinates
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    detections.append({
                        'class_id': class_id,
                        'class_name': self.classes[class_id] if class_id < len(self.classes) else 'unknown',
                        'confidence': float(confidence),
                        'bbox': (x, y, w, h),
                        'center': (center_x, center_y)
                    })
                    
        return detections
        
    def draw_detections(self, frame: np.ndarray, detections: List[dict]) -> np.ndarray:
        """Draw bounding boxes and labels on frame"""
        for detection in detections:
            x, y, w, h = detection['bbox']
            label = f"{detection['class_name']}: {detection['confidence']:.2f}"
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw label
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        return frame