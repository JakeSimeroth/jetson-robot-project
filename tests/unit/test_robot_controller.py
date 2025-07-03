#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from robot.robot_controller import RobotController

class TestRobotController(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.controller = RobotController()
    
    def test_initialization(self):
        """Test robot controller initialization"""
        self.assertIsNotNone(self.controller)
        self.assertFalse(self.controller.running)
        self.assertEqual(self.controller.config, {})
    
    def test_start_stop(self):
        """Test start and stop functionality"""
        # Test start
        self.controller.start()
        self.assertTrue(self.controller.running)
        
        # Test stop
        self.controller.stop()
        self.assertFalse(self.controller.running)
    
    def test_movement_commands(self):
        """Test movement command methods exist"""
        # These should not raise exceptions
        self.controller.move_forward(0.5)
        self.controller.move_backward(0.5)
        self.controller.turn_left(0.5)
        self.controller.turn_right(0.5)
        self.controller.stop_movement()
    
    def test_config_initialization(self):
        """Test initialization with config"""
        config = {"test_key": "test_value"}
        controller = RobotController(config)
        self.assertEqual(controller.config, config)

if __name__ == '__main__':
    unittest.main()