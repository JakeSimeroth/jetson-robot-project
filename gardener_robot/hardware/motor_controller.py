#!/usr/bin/env python3
"""
Motor Controller for Gardener Robot Tank Treads
Interfaces with Sabertooth motor driver for differential steering
"""

import time
import serial
import threading
from typing import Tuple, Optional
import logging

class MotorController:
    """Tank tread motor controller using Sabertooth driver"""
    
    def __init__(self, serial_port="/dev/ttyUSB0", baudrate=9600, address=128):
        """
        Initialize motor controller
        
        Args:
            serial_port: Serial port for Sabertooth driver
            baudrate: Communication baud rate
            address: Sabertooth device address
        """
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.address = address
        self.serial_conn = None
        self.is_connected = False
        self.emergency_stop = False
        
        # Motor state
        self.left_speed = 0
        self.right_speed = 0
        self.max_speed = 127  # Sabertooth max speed value
        
        # Safety
        self.last_command_time = time.time()
        self.command_timeout = 2.0  # Stop if no command for 2 seconds
        
        self.logger = logging.getLogger(__name__)
        
        # Start safety monitor thread
        self.safety_thread = threading.Thread(target=self._safety_monitor, daemon=True)
        self.safety_thread.start()
    
    def connect(self) -> bool:
        """Connect to Sabertooth motor driver"""
        try:
            self.serial_conn = serial.Serial(
                port=self.serial_port,
                baudrate=self.baudrate,
                timeout=1.0
            )
            self.is_connected = True
            self.logger.info(f"Connected to motor controller on {self.serial_port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to motor controller: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from motor controller"""
        self.stop_motors()
        if self.serial_conn:
            self.serial_conn.close()
        self.is_connected = False
        self.logger.info("Disconnected from motor controller")
    
    def _send_command(self, command: int, value: int):
        """Send command to Sabertooth driver"""
        if not self.is_connected or self.emergency_stop:
            return
        
        try:
            # Sabertooth packet format: [address, command, value, checksum]
            checksum = (self.address + command + value) & 0x7F
            packet = bytes([self.address, command, value, checksum])
            self.serial_conn.write(packet)
            self.last_command_time = time.time()
        except Exception as e:
            self.logger.error(f"Error sending motor command: {e}")
    
    def set_motor_speeds(self, left_speed: float, right_speed: float):
        """
        Set motor speeds for tank steering
        
        Args:
            left_speed: Left track speed (-1.0 to 1.0)
            right_speed: Right track speed (-1.0 to 1.0)
        """
        # Clamp speeds to valid range
        left_speed = max(-1.0, min(1.0, left_speed))
        right_speed = max(-1.0, min(1.0, right_speed))
        
        # Convert to Sabertooth values (-127 to 127)
        left_value = int(left_speed * self.max_speed)
        right_value = int(right_speed * self.max_speed)
        
        # Convert to Sabertooth command format (0-127 for each direction)
        if left_value >= 0:
            left_cmd = 0  # Forward
            left_val = left_value
        else:
            left_cmd = 1  # Reverse
            left_val = abs(left_value)
        
        if right_value >= 0:
            right_cmd = 4  # Forward
            right_val = right_value
        else:
            right_cmd = 5  # Reverse
            right_val = abs(right_value)
        
        # Send commands
        self._send_command(left_cmd, left_val)
        self._send_command(right_cmd, right_val)
        
        self.left_speed = left_speed
        self.right_speed = right_speed
        
        self.logger.debug(f"Motor speeds: L={left_speed:.2f}, R={right_speed:.2f}")
    
    def move_forward(self, speed: float = 0.5):
        """Move forward at specified speed"""
        self.set_motor_speeds(speed, speed)
    
    def move_backward(self, speed: float = 0.5):
        """Move backward at specified speed"""
        self.set_motor_speeds(-speed, -speed)
    
    def turn_left(self, speed: float = 0.3):
        """Turn left by rotating tracks in opposite directions"""
        self.set_motor_speeds(-speed, speed)
    
    def turn_right(self, speed: float = 0.3):
        """Turn right by rotating tracks in opposite directions"""
        self.set_motor_speeds(speed, -speed)
    
    def pivot_left(self, speed: float = 0.3):
        """Pivot left (left track reverse, right track forward)"""
        self.set_motor_speeds(-speed, speed)
    
    def pivot_right(self, speed: float = 0.3):
        """Pivot right (left track forward, right track reverse)"""
        self.set_motor_speeds(speed, -speed)
    
    def curve_left(self, forward_speed: float = 0.5, turn_factor: float = 0.3):
        """Curve left while moving forward"""
        left_speed = forward_speed * (1.0 - turn_factor)
        right_speed = forward_speed
        self.set_motor_speeds(left_speed, right_speed)
    
    def curve_right(self, forward_speed: float = 0.5, turn_factor: float = 0.3):
        """Curve right while moving forward"""
        left_speed = forward_speed
        right_speed = forward_speed * (1.0 - turn_factor)
        self.set_motor_speeds(left_speed, right_speed)
    
    def stop_motors(self):
        """Stop all motors immediately"""
        self.set_motor_speeds(0, 0)
    
    def emergency_stop_enable(self):
        """Enable emergency stop - disables all motor commands"""
        self.emergency_stop = True
        self.stop_motors()
        self.logger.warning("EMERGENCY STOP ACTIVATED")
    
    def emergency_stop_disable(self):
        """Disable emergency stop"""
        self.emergency_stop = False
        self.logger.info("Emergency stop disabled")
    
    def get_status(self) -> dict:
        """Get motor controller status"""
        return {
            'connected': self.is_connected,
            'emergency_stop': self.emergency_stop,
            'left_speed': self.left_speed,
            'right_speed': self.right_speed,
            'last_command_age': time.time() - self.last_command_time
        }
    
    def _safety_monitor(self):
        """Safety monitor thread - stops motors if no recent commands"""
        while True:
            time.sleep(0.5)
            
            if self.is_connected and not self.emergency_stop:
                command_age = time.time() - self.last_command_time
                if command_age > self.command_timeout:
                    if self.left_speed != 0 or self.right_speed != 0:
                        self.stop_motors()
                        self.logger.warning(f"Safety timeout - stopped motors after {command_age:.1f}s")


def main():
    """Test motor controller functionality"""
    logging.basicConfig(level=logging.INFO)
    
    motor = MotorController()
    
    if not motor.connect():
        print("Failed to connect to motor controller")
        return
    
    try:
        print("Testing motor movements...")
        
        # Forward
        print("Moving forward...")
        motor.move_forward(0.3)
        time.sleep(2)
        
        # Stop
        print("Stopping...")
        motor.stop_motors()
        time.sleep(1)
        
        # Turn left
        print("Turning left...")
        motor.turn_left(0.3)
        time.sleep(2)
        
        # Turn right
        print("Turning right...")
        motor.turn_right(0.3)
        time.sleep(2)
        
        # Backward
        print("Moving backward...")
        motor.move_backward(0.3)
        time.sleep(2)
        
        # Stop
        print("Final stop...")
        motor.stop_motors()
        
        print("Motor test complete!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        motor.disconnect()


if __name__ == "__main__":
    main()