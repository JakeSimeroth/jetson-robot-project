#!/usr/bin/env python3
"""
Garden Brain - AI Decision Making System
Integrates all systems for intelligent garden management
"""

import time
import json
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

# Import robot systems
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sensors.environmental_sensors import EnvironmentalSensors
from hardware.watering_system import WateringSystem
from hardware.motor_controller import MotorController
from communication.speech_system import SpeechSystem
from vision.yolo_detector import GardenerYOLODetector


class GardenBrain:
    """Central AI system for garden management and decision making"""
    
    def __init__(self, config_file: str = None):
        """
        Initialize the garden brain
        
        Args:
            config_file: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Initialize subsystems
        self.sensors = EnvironmentalSensors()
        self.watering = WateringSystem()
        self.motors = MotorController()
        self.speech = SpeechSystem()
        self.vision = GardenerYOLODetector()
        
        # System state
        self.active = False
        self.current_task = None
        self.task_queue = []
        
        # Garden knowledge
        self.plant_database = {}
        self.garden_map = {}
        self.care_history = {}
        
        # Decision making
        self.decision_interval = 60.0  # Check every minute
        self.last_decision_time = 0
        
        # Learning and adaptation
        self.performance_metrics = {
            'plants_watered_today': 0,
            'water_used_today': 0.0,
            'errors_today': 0,
            'uptime_today': 0.0
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Main control thread
        self.control_thread = None
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            'garden': {
                'plants': [
                    {'id': 'plant1', 'type': 'tomato', 'location': [0, 0], 'water_schedule': 'daily'},
                    {'id': 'plant2', 'type': 'pepper', 'location': [1, 0], 'water_schedule': 'daily'},
                    {'id': 'plant3', 'type': 'basil', 'location': [2, 0], 'water_schedule': 'twice_daily'}
                ],
                'area_size': [3, 1],  # 3x1 grid
                'watering_thresholds': {
                    'critical': 20.0,
                    'low': 35.0,
                    'optimal': 60.0
                }
            },
            'behavior': {
                'patrol_interval': 300,  # 5 minutes
                'water_check_interval': 60,  # 1 minute
                'communication_style': 'friendly',
                'learning_enabled': True
            },
            'safety': {
                'max_watering_time': 30,  # seconds
                'emergency_stop_enabled': True,
                'low_water_threshold': 10.0  # percentage
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                default_config.update(loaded_config)
                self.logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load config file: {e}")
        
        return default_config
    
    def initialize_systems(self) -> bool:
        """Initialize all robot subsystems"""
        self.logger.info("Initializing garden robot systems...")
        
        success = True
        
        # Initialize sensors
        if not self.sensors.initialize():
            self.logger.error("Failed to initialize sensors")
            success = False
        
        # Initialize watering system
        if not self.watering.initialize_gpio():
            self.logger.error("Failed to initialize watering system")
            success = False
        
        # Initialize motor controller
        if not self.motors.connect():
            self.logger.warning("Motor controller not connected - navigation disabled")
        
        # Initialize speech system
        self.speech.start_speech_service()
        
        # Initialize vision system
        if not self.vision.initialize_model():
            self.logger.warning("Vision system failed to initialize")
        
        # Load plant database
        self._initialize_plant_database()
        
        if success:
            self.logger.info("All systems initialized successfully")
            self.speech.announce_startup()
        else:
            self.logger.error("Some systems failed to initialize")
            self.speech.announce_error("startup", "Some systems failed to initialize")
        
        return success
    
    def _initialize_plant_database(self):
        """Initialize knowledge about plants in the garden"""
        for plant_config in self.config['garden']['plants']:
            plant_id = plant_config['id']
            self.plant_database[plant_id] = {
                'type': plant_config['type'],
                'location': plant_config['location'],
                'water_schedule': plant_config['water_schedule'],
                'last_watered': None,
                'total_water_received': 0.0,
                'health_score': 100.0,
                'growth_stage': 'seedling'
            }
            
            # Initialize care history
            self.care_history[plant_id] = []
        
        self.logger.info(f"Initialized database for {len(self.plant_database)} plants")
    
    def start_autonomous_operation(self):
        """Start autonomous garden management"""
        if self.active:
            self.logger.warning("Autonomous operation already active")
            return
        
        self.active = True
        self.control_thread = threading.Thread(target=self._main_control_loop, daemon=True)
        self.control_thread.start()
        
        # Start subsystem monitoring
        self.sensors.start_monitoring()
        
        self.logger.info("Autonomous garden management started")
        self.speech.say("Beginning autonomous garden care mode. I'll monitor and care for all plants.")
    
    def stop_autonomous_operation(self):
        """Stop autonomous garden management"""
        self.active = False
        
        # Stop subsystems
        self.sensors.stop_monitoring()
        
        # Stop motors
        self.motors.stop_motors()
        
        # Wait for control thread
        if self.control_thread:
            self.control_thread.join(timeout=10.0)
        
        self.logger.info("Autonomous garden management stopped")
        self.speech.say("Autonomous garden care mode stopped. Thank you for using my services!")
    
    def _main_control_loop(self):
        """Main AI decision-making and control loop"""
        while self.active:
            try:
                current_time = time.time()
                
                # Check if it's time to make decisions
                if current_time - self.last_decision_time >= self.decision_interval:
                    self._make_decisions()
                    self.last_decision_time = current_time
                
                # Execute current task
                if self.current_task:
                    self._execute_current_task()
                elif self.task_queue:
                    self.current_task = self.task_queue.pop(0)
                    self.logger.info(f"Starting new task: {self.current_task['type']}")
                
                # Brief sleep to prevent CPU hogging
                time.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error in main control loop: {e}")
                self.speech.announce_error("system", f"Control loop error: {str(e)}")
                time.sleep(5.0)
    
    def _make_decisions(self):
        """AI decision making based on current garden state"""
        self.logger.debug("Making garden management decisions...")
        
        # Get current garden status
        garden_summary = self.sensors.get_garden_summary()
        
        # Check each plant's needs
        for plant_id, plant_data in self.plant_database.items():
            plant_needs = self.sensors.get_plant_needs(plant_id)
            
            if plant_needs.get('needs_water', False):
                urgency = plant_needs.get('water_urgency', 'medium')
                
                # Create watering task
                watering_task = {
                    'type': 'water_plant',
                    'plant_id': plant_id,
                    'urgency': urgency,
                    'recommended_time': plant_needs.get('recommended_watering_time', 10.0),
                    'timestamp': time.time()
                }
                
                # Add to queue based on urgency
                if urgency == 'high':
                    self.task_queue.insert(0, watering_task)  # High priority - insert at front
                    self.speech.announce_error("plant_urgent", f"Plant {plant_id} urgently needs water!")
                else:
                    self.task_queue.append(watering_task)
                
                self.logger.info(f"Added watering task for {plant_id} (urgency: {urgency})")
        
        # Check for maintenance tasks
        self._schedule_maintenance_tasks()
        
        # Update performance metrics
        self._update_performance_metrics()
    
    def _execute_current_task(self):
        """Execute the current task"""
        if not self.current_task:
            return
        
        task_type = self.current_task['type']
        
        try:
            if task_type == 'water_plant':
                self._execute_watering_task()
            elif task_type == 'patrol_garden':
                self._execute_patrol_task()
            elif task_type == 'system_check':
                self._execute_system_check()
            elif task_type == 'daily_summary':
                self._execute_daily_summary()
            else:
                self.logger.warning(f"Unknown task type: {task_type}")
                self.current_task = None
            
        except Exception as e:
            self.logger.error(f"Error executing task {task_type}: {e}")
            self.speech.announce_error("task_error", f"Failed to complete {task_type}")
            self.current_task = None
    
    def _execute_watering_task(self):
        """Execute a plant watering task"""
        plant_id = self.current_task['plant_id']
        watering_time = self.current_task['recommended_time']
        
        self.logger.info(f"Watering plant {plant_id} for {watering_time:.1f} seconds")
        
        # Get current plant status
        plant_status = self.sensors.get_plant_needs(plant_id)
        current_moisture = plant_status.get('current_moisture', 0)
        
        # Announce watering start
        self.speech.announce_plant_status(plant_id, current_moisture, True)
        self.speech.announce_watering_start(plant_id, watering_time)
        
        # TODO: Navigate to plant location if navigation is available
        plant_location = self.plant_database[plant_id]['location']
        if self.motors.is_connected:
            self._navigate_to_plant(plant_location)
        
        # Perform watering
        success = self.watering.water_plant(watering_time)
        
        if success:
            # Update plant database
            self.plant_database[plant_id]['last_watered'] = datetime.now()
            self.plant_database[plant_id]['total_water_received'] += watering_time * 0.067  # Approximate L/s
            
            # Record in care history
            care_record = {
                'timestamp': time.time(),
                'action': 'watered',
                'duration': watering_time,
                'moisture_before': current_moisture,
                'moisture_after': None  # Will be updated on next reading
            }
            self.care_history[plant_id].append(care_record)
            
            # Update metrics
            self.performance_metrics['plants_watered_today'] += 1
            self.performance_metrics['water_used_today'] += watering_time * 0.067
            
            # Announce completion
            water_amount = watering_time * 0.067
            self.speech.announce_watering_complete(plant_id, water_amount)
            
            self.logger.info(f"Successfully watered plant {plant_id}")
        else:
            self.logger.error(f"Failed to water plant {plant_id}")
            self.speech.announce_error("watering", f"Failed to water plant {plant_id}")
            self.performance_metrics['errors_today'] += 1
        
        # Task complete
        self.current_task = None
    
    def _navigate_to_plant(self, location: List[float]):
        """Navigate to a plant location (simplified)"""
        # This is a simplified navigation - in real implementation would use
        # more sophisticated path planning and localization
        self.logger.info(f"Navigating to location {location}")
        self.speech.announce_movement("forward")
        
        # Simulate navigation time
        time.sleep(2.0)
        
        self.motors.stop_motors()
        self.speech.announce_movement("arrived")
    
    def _schedule_maintenance_tasks(self):
        """Schedule regular maintenance and monitoring tasks"""
        current_time = time.time()
        
        # Daily summary task
        now = datetime.now()
        if now.hour == 18 and now.minute < 5:  # 6 PM daily
            daily_task = {
                'type': 'daily_summary',
                'timestamp': current_time
            }
            if not any(task['type'] == 'daily_summary' for task in self.task_queue):
                self.task_queue.append(daily_task)
        
        # System check task
        if len(self.task_queue) == 0:  # Only when nothing urgent
            system_check_task = {
                'type': 'system_check',
                'timestamp': current_time
            }
            self.task_queue.append(system_check_task)
    
    def _execute_system_check(self):
        """Execute system health check"""
        self.logger.info("Performing system health check")
        
        # Check all subsystems
        sensor_status = self.sensors.get_garden_summary()
        watering_status = self.watering.get_status()
        motor_status = self.motors.get_status()
        speech_status = self.speech.get_status()
        
        # Report any issues
        issues = []
        
        if watering_status['water_level'] < self.config['safety']['low_water_threshold']:
            issues.append("Water level is low")
            self.speech.announce_error("water_low")
        
        if not motor_status['connected']:
            issues.append("Motor controller not connected")
        
        if motor_status['emergency_stop']:
            issues.append("Emergency stop is active")
        
        if issues:
            self.logger.warning(f"System issues detected: {issues}")
        else:
            self.logger.info("All systems healthy")
        
        self.current_task = None
    
    def _execute_daily_summary(self):
        """Execute daily care summary"""
        plants_watered = self.performance_metrics['plants_watered_today']
        water_used = self.performance_metrics['water_used_today']
        
        self.speech.announce_daily_summary(plants_watered, water_used)
        
        # Reset daily metrics
        self.performance_metrics['plants_watered_today'] = 0
        self.performance_metrics['water_used_today'] = 0.0
        self.performance_metrics['errors_today'] = 0
        
        self.current_task = None
    
    def _update_performance_metrics(self):
        """Update system performance metrics"""
        # Update uptime
        if hasattr(self, 'start_time'):
            self.performance_metrics['uptime_today'] = time.time() - self.start_time
    
    def manual_water_plant(self, plant_id: str, duration: float = None) -> bool:
        """Manually trigger watering for a specific plant"""
        if plant_id not in self.plant_database:
            self.logger.error(f"Plant {plant_id} not found in database")
            return False
        
        if duration is None:
            # Use AI recommendation
            plant_needs = self.sensors.get_plant_needs(plant_id)
            duration = plant_needs.get('recommended_watering_time', 10.0)
        
        # Create immediate watering task
        watering_task = {
            'type': 'water_plant',
            'plant_id': plant_id,
            'urgency': 'manual',
            'recommended_time': duration,
            'timestamp': time.time()
        }
        
        # Insert at front of queue for immediate execution
        self.task_queue.insert(0, watering_task)
        
        self.logger.info(f"Manual watering requested for {plant_id}")
        return True
    
    def get_garden_status(self) -> Dict:
        """Get comprehensive garden status"""
        garden_summary = self.sensors.get_garden_summary()
        
        # Add robot status
        robot_status = {
            'active': self.active,
            'current_task': self.current_task,
            'task_queue_length': len(self.task_queue),
            'performance_metrics': self.performance_metrics.copy(),
            'plant_database': self.plant_database.copy(),
            'subsystem_status': {
                'sensors': 'healthy',
                'watering': self.watering.get_status(),
                'motors': self.motors.get_status(),
                'speech': self.speech.get_status()
            }
        }
        
        garden_summary['robot_status'] = robot_status
        return garden_summary
    
    def emergency_stop(self):
        """Emergency stop all operations"""
        self.logger.warning("EMERGENCY STOP ACTIVATED")
        
        # Stop all systems
        self.motors.emergency_stop_enable()
        self.watering.emergency_stop()
        
        # Clear task queue
        self.task_queue.clear()
        self.current_task = None
        
        # Announce emergency stop
        self.speech.announce_error("emergency_stop")
    
    def cleanup(self):
        """Clean up all systems"""
        self.logger.info("Cleaning up garden brain systems")
        
        self.stop_autonomous_operation()
        
        # Cleanup subsystems
        self.sensors.cleanup()
        self.watering.cleanup_gpio()
        self.motors.disconnect()
        self.speech.stop_speech_service()


def main():
    """Test garden brain functionality"""
    logging.basicConfig(level=logging.INFO)
    
    brain = GardenBrain()
    
    try:
        print("Initializing garden brain...")
        if not brain.initialize_systems():
            print("Failed to initialize some systems")
        
        print("Starting autonomous operation...")
        brain.start_autonomous_operation()
        
        # Run for 2 minutes
        for i in range(12):
            time.sleep(10)
            status = brain.get_garden_status()
            print(f"\nStatus update {i+1}:")
            print(f"Active: {status['robot_status']['active']}")
            print(f"Current task: {status['robot_status']['current_task']}")
            print(f"Queue length: {status['robot_status']['task_queue_length']}")
            
            if status['urgent_needs']:
                print(f"Urgent needs: {status['urgent_needs']}")
        
        print("\nGarden brain test complete!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        brain.cleanup()


if __name__ == "__main__":
    main()