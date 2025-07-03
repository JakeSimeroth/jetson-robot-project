#!/usr/bin/env python3

import cv2
import numpy as np
import logging
from typing import Optional, Tuple

class CameraManager:
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap = None
        self.logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """Initialize camera connection"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                self.logger.error(f"Failed to open camera {self.camera_id}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.logger.info(f"Camera {self.camera_id} initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {e}")
            return False
            
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame"""
        if not self.cap:
            return None
            
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
        
    def get_frame_size(self) -> Tuple[int, int]:
        """Get camera frame dimensions"""
        if not self.cap:
            return (0, 0)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)
        
    def release(self):
        """Release camera resources"""
        if self.cap:
            self.cap.release()
            self.logger.info("Camera released")