#!/usr/bin/env python3
"""
test_camera.py - Camera testing script for Jetson Robot Project

This script tests camera functionality and displays video feed.
"""

import cv2
import sys
import time
import argparse
from pathlib import Path

def test_camera(camera_id=0, duration=10):
    """Test camera connectivity and display feed"""
    print(f"🎥 Testing camera {camera_id}...")
    
    # Initialize camera
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"❌ Cannot open camera {camera_id}")
        return False
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Get actual properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"✅ Camera opened successfully")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps}")
    print(f"   Testing for {duration} seconds...")
    print("   Press 'q' to quit early")
    
    start_time = time.time()
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to capture frame")
                break
            
            frame_count += 1
            
            # Add text overlay
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Camera: {camera_id}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow('Camera Test', frame)
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Check duration
            if time.time() - start_time > duration:
                break
    
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    
    finally:
        # Calculate statistics
        elapsed_time = time.time() - start_time
        actual_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
        
        print(f"\n📊 Test Results:")
        print(f"   Duration: {elapsed_time:.2f} seconds")
        print(f"   Frames captured: {frame_count}")
        print(f"   Actual FPS: {actual_fps:.2f}")
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        if frame_count > 0:
            print("✅ Camera test completed successfully")
            return True
        else:
            print("❌ Camera test failed")
            return False

def list_cameras():
    """List available cameras"""
    print("🔍 Scanning for available cameras...")
    
    available_cameras = []
    
    # Test camera indices 0-3
    for i in range(4):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                print(f"   Camera {i}: Available ({width}x{height})")
                available_cameras.append(i)
            cap.release()
    
    if available_cameras:
        print(f"✅ Found {len(available_cameras)} camera(s)")
        return available_cameras
    else:
        print("❌ No cameras found")
        return []

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test Jetson camera functionality')
    parser.add_argument('--camera', '-c', type=int, default=0,
                       help='Camera ID to test (default: 0)')
    parser.add_argument('--duration', '-d', type=int, default=10,
                       help='Test duration in seconds (default: 10)')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available cameras')
    
    args = parser.parse_args()
    
    print("📷 Jetson Camera Test")
    print("=" * 30)
    
    if args.list:
        cameras = list_cameras()
        if cameras:
            print(f"\nAvailable cameras: {cameras}")
        return 0 if cameras else 1
    
    # Test specific camera
    success = test_camera(args.camera, args.duration)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())