#!/usr/bin/env python3
"""
YOLO Object Detection for Gardener Robot
Uses C922x USB camera for plant and garden object detection
"""

import cv2
import numpy as np
import time
import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    import torch
    import ultralytics
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("YOLOv8 not available. Install with: pip install ultralytics")

class GardenerYOLODetector:
    """YOLO-based object detector for gardening applications"""
    
    def __init__(self, model_path="yolov8n.pt", camera_index=0, confidence_threshold=0.5):
        """
        Initialize the detector
        
        Args:
            model_path: Path to YOLO model (will download if not exists)
            camera_index: Camera device index (0 for first camera)
            confidence_threshold: Minimum confidence for detections
        """
        self.model_path = model_path
        self.camera_index = camera_index
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.camera = None
        self.running = False
        
        # Garden-related classes (from COCO dataset)
        self.garden_classes = {
            'potted plant': 64,
            'vase': 86,
            'scissors': 87,
            'person': 0,
            'bottle': 39,
            'cup': 47,
            'bowl': 51,
            'apple': 53,
            'banana': 52,
            'orange': 55,
            'broccoli': 56,
            'carrot': 57,
        }
        
    def initialize_model(self):
        """Initialize YOLO model"""
        if not YOLO_AVAILABLE:
            print("ERROR: YOLO not available. Please install ultralytics:")
            print("pip install ultralytics")
            return False
            
        try:
            print(f"Loading YOLO model: {self.model_path}")
            self.model = YOLO(self.model_path)
            print("Model loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def initialize_camera(self):
        """Initialize camera connection"""
        try:
            print(f"Initializing camera {self.camera_index}...")
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                print(f"ERROR: Could not open camera {self.camera_index}")
                return False
                
            # Set camera properties for C922x
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Get actual properties
            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.camera.get(cv2.CAP_PROP_FPS)
            
            print(f"Camera initialized: {width}x{height} @ {fps} FPS")
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def detect_objects(self, frame):
        """Run YOLO detection on frame"""
        if self.model is None:
            return frame, []
            
        try:
            # Run inference
            results = self.model(frame, conf=self.confidence_threshold)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Get class name
                        class_name = self.model.names[class_id]
                        
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': class_name
                        })
                        
                        # Draw bounding box
                        color = (0, 255, 0) if class_name in self.garden_classes else (255, 0, 0)
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        
                        # Draw label
                        label = f"{class_name}: {confidence:.2f}"
                        cv2.putText(frame, label, (int(x1), int(y1) - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            return frame, detections
            
        except Exception as e:
            print(f"Error in detection: {e}")
            return frame, []
    
    def run_detection(self, display=True, save_video=False, output_path="detection_output.mp4"):
        """Run real-time object detection"""
        if not self.initialize_model():
            return False
            
        if not self.initialize_camera():
            return False
        
        self.running = True
        
        # Setup video writer if saving
        video_writer = None
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = self.camera.get(cv2.CAP_PROP_FPS)
            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        print("Starting detection. Press 'q' to quit, 's' to save screenshot")
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while self.running:
                ret, frame = self.camera.read()
                if not ret:
                    print("Failed to read frame")
                    break
                
                # Run detection
                detected_frame, detections = self.detect_objects(frame)
                
                # Add info overlay
                info_text = f"Frame: {frame_count} | Objects: {len(detections)}"
                cv2.putText(detected_frame, info_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Save frame if recording
                if video_writer:
                    video_writer.write(detected_frame)
                
                # Display frame
                if display:
                    cv2.imshow('Gardener Robot - YOLO Detection', detected_frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        screenshot_path = f"screenshot_{int(time.time())}.jpg"
                        cv2.imwrite(screenshot_path, detected_frame)
                        print(f"Screenshot saved: {screenshot_path}")
                
                # Print detection summary
                if detections:
                    garden_objects = [d for d in detections if d['class_name'] in self.garden_classes]
                    if garden_objects:
                        print(f"Garden objects detected: {[obj['class_name'] for obj in garden_objects]}")
                
                frame_count += 1
                
                # Calculate FPS every 30 frames
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"Processing FPS: {fps:.2f}")
                    
        except KeyboardInterrupt:
            print("\nDetection interrupted by user")
            
        finally:
            self.cleanup()
            if video_writer:
                video_writer.release()
            cv2.destroyAllWindows()
            
        return True
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.camera:
            self.camera.release()
        print("Detection stopped and resources cleaned up")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Gardener Robot YOLO Detection')
    parser.add_argument('--model', default='yolov8n.pt', help='YOLO model path')
    parser.add_argument('--camera', type=int, default=0, help='Camera index')
    parser.add_argument('--confidence', type=float, default=0.5, help='Confidence threshold')
    parser.add_argument('--no-display', action='store_true', help='Run without display')
    parser.add_argument('--save-video', action='store_true', help='Save detection video')
    parser.add_argument('--output', default='detection_output.mp4', help='Output video path')
    
    args = parser.parse_args()
    
    print("🌱 Gardener Robot YOLO Detection System 🌱")
    print("=" * 50)
    
    # Check if YOLO is available
    if not YOLO_AVAILABLE:
        print("Installing YOLOv8...")
        os.system("pip install ultralytics")
        try:
            from ultralytics import YOLO
            print("YOLOv8 installed successfully!")
        except ImportError:
            print("Failed to install YOLOv8. Please install manually:")
            print("pip install ultralytics")
            return 1
    
    # Initialize detector
    detector = GardenerYOLODetector(
        model_path=args.model,
        camera_index=args.camera,
        confidence_threshold=args.confidence
    )
    
    # Run detection
    success = detector.run_detection(
        display=not args.no_display,
        save_video=args.save_video,
        output_path=args.output
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())