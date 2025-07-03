#!/usr/bin/env python3
"""
Quick camera test for C922x
"""

import cv2
import sys

def test_camera():
    print("Testing C922x camera...")
    
    # Try camera indices 0 and 1
    for camera_idx in [0, 1]:
        print(f"Testing camera {camera_idx}...")
        cap = cv2.VideoCapture(camera_idx)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✓ Camera {camera_idx} working - Frame shape: {frame.shape}")
                cap.release()
                return camera_idx
            else:
                print(f"✗ Camera {camera_idx} opened but no frame")
        else:
            print(f"✗ Camera {camera_idx} failed to open")
        
        cap.release()
    
    print("No working cameras found")
    return None

if __name__ == "__main__":
    working_camera = test_camera()
    if working_camera is not None:
        print(f"Use camera index {working_camera} for YOLO detection")
        sys.exit(0)
    else:
        print("No camera available")
        sys.exit(1)