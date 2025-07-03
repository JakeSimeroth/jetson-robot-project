#!/usr/bin/env python3

import time
import logging
from typing import Dict, Any

try:
    import Jetson.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

class MotorControl:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        self.initialized = False
        
    def _default_config(self) -> Dict[str, Any]:
        """Default motor configuration"""
        return {
            "left_motor": {"pin1": 18, "pin2": 19, "pwm": 20},
            "right_motor": {"pin1": 21, "pin2": 22, "pwm": 23},
            "pwm_frequency": 1000
        }
        
    def initialize(self) -> bool:
        """Initialize GPIO pins for motor control"""
        if not GPIO_AVAILABLE:
            self.logger.warning("Jetson.GPIO not available")
            return False
            
        try:
            GPIO.setmode(GPIO.BCM)
            
            # Setup left motor pins
            left_config = self.config["left_motor"]
            GPIO.setup(left_config["pin1"], GPIO.OUT)
            GPIO.setup(left_config["pin2"], GPIO.OUT)
            GPIO.setup(left_config["pwm"], GPIO.OUT)
            
            # Setup right motor pins
            right_config = self.config["right_motor"]
            GPIO.setup(right_config["pin1"], GPIO.OUT)
            GPIO.setup(right_config["pin2"], GPIO.OUT)
            GPIO.setup(right_config["pwm"], GPIO.OUT)
            
            # Initialize PWM
            self.left_pwm = GPIO.PWM(left_config["pwm"], self.config["pwm_frequency"])
            self.right_pwm = GPIO.PWM(right_config["pwm"], self.config["pwm_frequency"])
            
            self.left_pwm.start(0)
            self.right_pwm.start(0)
            
            self.initialized = True
            self.logger.info("Motor control initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Motor initialization failed: {e}")
            return False
            
    def set_motor_speed(self, motor: str, speed: float, direction: str = "forward"):
        """Set motor speed and direction"""
        if not self.initialized:
            return
            
        speed = max(0, min(100, abs(speed)))  # Clamp speed to 0-100
        
        if motor == "left":
            config = self.config["left_motor"]
            pwm = self.left_pwm
        elif motor == "right":
            config = self.config["right_motor"]
            pwm = self.right_pwm
        else:
            self.logger.error(f"Invalid motor: {motor}")
            return
            
        if direction == "forward":
            GPIO.output(config["pin1"], GPIO.HIGH)
            GPIO.output(config["pin2"], GPIO.LOW)
        else:
            GPIO.output(config["pin1"], GPIO.LOW)
            GPIO.output(config["pin2"], GPIO.HIGH)
            
        pwm.ChangeDutyCycle(speed)
        
    def move_forward(self, speed: float = 50):
        """Move robot forward"""
        self.set_motor_speed("left", speed, "forward")
        self.set_motor_speed("right", speed, "forward")
        
    def move_backward(self, speed: float = 50):
        """Move robot backward"""
        self.set_motor_speed("left", speed, "backward")
        self.set_motor_speed("right", speed, "backward")
        
    def turn_left(self, speed: float = 50):
        """Turn robot left"""
        self.set_motor_speed("left", speed, "backward")
        self.set_motor_speed("right", speed, "forward")
        
    def turn_right(self, speed: float = 50):
        """Turn robot right"""
        self.set_motor_speed("left", speed, "forward")
        self.set_motor_speed("right", speed, "backward")
        
    def stop(self):
        """Stop all motors"""
        if self.initialized:
            self.left_pwm.ChangeDutyCycle(0)
            self.right_pwm.ChangeDutyCycle(0)
            
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.initialized and GPIO_AVAILABLE:
            self.stop()
            self.left_pwm.stop()
            self.right_pwm.stop()
            GPIO.cleanup()
            self.logger.info("Motor control cleaned up")