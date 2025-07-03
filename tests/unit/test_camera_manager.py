#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from vision.camera_manager import CameraManager

class TestCameraManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.camera_manager = CameraManager(camera_id=0)
    
    def test_initialization(self):
        """Test camera manager initialization"""
        self.assertEqual(self.camera_manager.camera_id, 0)
        self.assertIsNone(self.camera_manager.cap)
    
    @patch('cv2.VideoCapture')
    def test_initialize_success(self, mock_video_capture):
        """Test successful camera initialization"""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap
        
        result = self.camera_manager.initialize()
        
        self.assertTrue(result)
        mock_video_capture.assert_called_once_with(0)
        mock_cap.set.assert_called()
    
    @patch('cv2.VideoCapture')
    def test_initialize_failure(self, mock_video_capture):
        """Test camera initialization failure"""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        result = self.camera_manager.initialize()
        
        self.assertFalse(result)
    
    def test_capture_frame_no_camera(self):
        """Test frame capture without initialized camera"""
        result = self.camera_manager.capture_frame()
        self.assertIsNone(result)
    
    @patch('cv2.VideoCapture')
    def test_capture_frame_success(self, mock_video_capture):
        """Test successful frame capture"""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap
        
        self.camera_manager.initialize()
        frame = self.camera_manager.capture_frame()
        
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (480, 640, 3))
    
    def test_get_frame_size_no_camera(self):
        """Test getting frame size without initialized camera"""
        width, height = self.camera_manager.get_frame_size()
        self.assertEqual((width, height), (0, 0))
    
    @patch('cv2.VideoCapture')
    def test_release(self, mock_video_capture):
        """Test camera release"""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap
        
        self.camera_manager.initialize()
        self.camera_manager.release()
        
        mock_cap.release.assert_called_once()

if __name__ == '__main__':
    unittest.main()