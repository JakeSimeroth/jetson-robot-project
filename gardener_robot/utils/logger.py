#!/usr/bin/env python3
"""
Logging utilities for gardener robot
Provides structured logging with file rotation and different output formats
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class GardenerLogger:
    """Custom logger for gardener robot with file rotation and formatting"""
    
    def __init__(self, name: str = "gardener_robot", log_level: str = "INFO", 
                 log_dir: Optional[str] = None, max_bytes: int = 10*1024*1024, 
                 backup_count: int = 5):
        """
        Initialize logger
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files (default: logs/ in project root)
            max_bytes: Maximum log file size before rotation
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        
        # Set log directory
        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.log_dir = project_root / "logs"
        else:
            self.log_dir = Path(log_dir)
        
        self.log_dir.mkdir(exist_ok=True)
        
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        # File handler with rotation
        log_file = self.log_dir / f"{self.name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=self.max_bytes, backupCount=self.backup_count
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Apply formatters
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger"""
        return self.logger


class StructuredLogger:
    """Structured logging for robot events with JSON output"""
    
    def __init__(self, log_dir: Optional[str] = None):
        """Initialize structured logger"""
        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.log_dir = project_root / "logs"
        else:
            self.log_dir = Path(log_dir)
        
        self.log_dir.mkdir(exist_ok=True)
        
        # Create event log file
        self.event_log_file = self.log_dir / "robot_events.jsonl"
    
    def log_event(self, event_type: str, **kwargs):
        """Log a structured event"""
        import json
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            **kwargs
        }
        
        try:
            with open(self.event_log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            print(f"Error logging event: {e}")
    
    def log_plant_watering(self, plant_id: str, duration: float, moisture_before: float, 
                          moisture_after: Optional[float] = None):
        """Log plant watering event"""
        self.log_event(
            'plant_watering',
            plant_id=plant_id,
            duration_seconds=duration,
            moisture_before=moisture_before,
            moisture_after=moisture_after
        )
    
    def log_sensor_reading(self, sensor_type: str, value: float, unit: str, 
                          location: Optional[str] = None):
        """Log sensor reading event"""
        self.log_event(
            'sensor_reading',
            sensor_type=sensor_type,
            value=value,
            unit=unit,
            location=location
        )
    
    def log_system_error(self, error_type: str, error_message: str, component: str):
        """Log system error event"""
        self.log_event(
            'system_error',
            error_type=error_type,
            error_message=error_message,
            component=component
        )
    
    def log_movement(self, action: str, duration: Optional[float] = None, 
                    start_position: Optional[list] = None, end_position: Optional[list] = None):
        """Log robot movement event"""
        self.log_event(
            'robot_movement',
            action=action,
            duration_seconds=duration,
            start_position=start_position,
            end_position=end_position
        )


def setup_robot_logging(log_level: str = "INFO") -> tuple:
    """
    Setup complete logging system for robot
    
    Args:
        log_level: Logging level
        
    Returns:
        Tuple of (standard_logger, structured_logger)
    """
    # Standard logger
    gardener_logger = GardenerLogger(log_level=log_level)
    standard_logger = gardener_logger.get_logger()
    
    # Structured logger
    structured_logger = StructuredLogger()
    
    return standard_logger, structured_logger


if __name__ == "__main__":
    # Test logging setup
    logger, event_logger = setup_robot_logging("DEBUG")
    
    logger.info("Testing standard logging")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Test structured logging
    event_logger.log_plant_watering("test_plant", 15.0, 25.5, 65.2)
    event_logger.log_sensor_reading("soil_moisture", 45.2, "percent", "plant_1")
    event_logger.log_system_error("connection", "Failed to connect to motor controller", "motors")
    
    print("Logging test complete - check logs/ directory")