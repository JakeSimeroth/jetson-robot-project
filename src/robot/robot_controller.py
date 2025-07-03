#!/usr/bin/env python3

import time
import logging
from typing import Dict, Any

class RobotController:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.running = False
        
    def start(self):
        """Start the robot controller"""
        self.running = True
        self.logger.info("Robot controller started")
        
    def stop(self):
        """Stop the robot controller"""
        self.running = False
        self.logger.info("Robot controller stopped")
        
    def move_forward(self, speed: float = 0.5):
        """Move robot forward"""
        self.logger.info(f"Moving forward at speed {speed}")
        
    def move_backward(self, speed: float = 0.5):
        """Move robot backward"""
        self.logger.info(f"Moving backward at speed {speed}")
        
    def turn_left(self, speed: float = 0.5):
        """Turn robot left"""
        self.logger.info(f"Turning left at speed {speed}")
        
    def turn_right(self, speed: float = 0.5):
        """Turn robot right"""
        self.logger.info(f"Turning right at speed {speed}")
        
    def stop_movement(self):
        """Stop all movement"""
        self.logger.info("Stopping movement")