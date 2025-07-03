#!/usr/bin/env python3
"""
Basic system tests for gardener robot
Tests core functionality without requiring hardware
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add gardener_robot to path
sys.path.insert(0, str(Path(__file__).parent.parent / "gardener_robot"))

from gardener_robot.sensors.environmental_sensors import EnvironmentalSensors, SoilMoistureSensor
from gardener_robot.hardware.watering_system import WateringSystem
from gardener_robot.hardware.motor_controller import MotorController
from gardener_robot.communication.speech_system import SpeechSystem
from gardener_robot.ai.garden_brain import GardenBrain


class TestSoilMoistureSensor(unittest.TestCase):
    """Test soil moisture sensor functionality"""
    
    def setUp(self):
        self.sensor = SoilMoistureSensor("test_plant", 23)
    
    def test_initialization(self):
        """Test sensor initialization"""
        self.assertEqual(self.sensor.sensor_id, "test_plant")
        self.assertEqual(self.sensor.pin, 23)
        self.assertFalse(self.sensor.initialized)
    
    def test_moisture_reading_simulation(self):
        """Test moisture reading in simulation mode"""
        # Should work without GPIO
        moisture = self.sensor.read_moisture()
        self.assertIsInstance(moisture, float)
        self.assertGreaterEqual(moisture, 0.0)
        self.assertLessEqual(moisture, 100.0)


class TestEnvironmentalSensors(unittest.TestCase):
    """Test environmental sensor system"""
    
    def setUp(self):
        self.sensors = EnvironmentalSensors()
    
    def test_initialization(self):
        """Test sensors initialization"""
        # Should work in simulation mode
        result = self.sensors.initialize()
        self.assertTrue(result)
    
    def test_sensor_readings(self):
        """Test reading all sensors"""
        self.sensors.update_all_readings()
        
        # Check that readings are reasonable
        self.assertIsInstance(self.sensors.temperature, float)
        self.assertIsInstance(self.sensors.humidity, float)
        self.assertIsInstance(self.sensors.light_level, float)
        self.assertIsInstance(self.sensors.ph_level, float)
        
        # Check ranges
        self.assertGreater(self.sensors.temperature, -50)
        self.assertLess(self.sensors.temperature, 60)
        self.assertGreaterEqual(self.sensors.humidity, 0)
        self.assertLessEqual(self.sensors.humidity, 100)
        self.assertGreaterEqual(self.sensors.light_level, 0)
    
    def test_plant_needs_analysis(self):
        """Test plant needs analysis"""
        # Set up test data
        self.sensors.soil_moisture['test_plant'] = 25.0  # Low moisture
        
        needs = self.sensors.get_plant_needs('test_plant')
        
        self.assertIn('plant_id', needs)
        self.assertIn('current_moisture', needs)
        self.assertIn('needs_water', needs)
        self.assertIn('water_urgency', needs)
        self.assertTrue(needs['needs_water'])  # Should need water
        self.assertEqual(needs['water_urgency'], 'high')  # Should be urgent
    
    def test_garden_summary(self):
        """Test garden summary generation"""
        summary = self.sensors.get_garden_summary()
        
        self.assertIn('timestamp', summary)
        self.assertIn('environmental_conditions', summary)
        self.assertIn('soil_moisture', summary)
        self.assertIn('plant_statuses', summary)


class TestWateringSystem(unittest.TestCase):
    """Test watering system functionality"""
    
    def setUp(self):
        self.watering = WateringSystem()
    
    def test_initialization(self):
        """Test watering system initialization"""
        # Should work in simulation mode
        result = self.watering.initialize_gpio()
        self.assertTrue(result)
    
    def test_pump_control(self):
        """Test pump start/stop"""
        # Should work in simulation mode
        result = self.watering.start_pump()
        self.assertTrue(result)
        self.assertTrue(self.watering.pump_running)
        
        self.watering.stop_pump()
        self.assertFalse(self.watering.pump_running)
    
    def test_valve_control(self):
        """Test valve open/close"""
        result = self.watering.open_valve()
        self.assertTrue(result)
        self.assertTrue(self.watering.valve_open)
        
        self.watering.close_valve()
        self.assertFalse(self.watering.valve_open)
    
    def test_watering_operation(self):
        """Test complete watering operation"""
        # Short watering test
        result = self.watering.water_plant(2.0)  # 2 seconds
        self.assertTrue(result)
        
        # Check that pump and valve are off after watering
        self.assertFalse(self.watering.pump_running)
        self.assertFalse(self.watering.valve_open)
    
    def test_safety_limits(self):
        """Test safety limit enforcement"""
        # Test invalid duration
        result = self.watering.water_plant(-1.0)
        self.assertFalse(result)
        
        # Test excessive duration
        result = self.watering.water_plant(500.0)  # Exceeds max runtime
        self.assertFalse(result)
    
    def test_status_reporting(self):
        """Test status reporting"""
        status = self.watering.get_status()
        
        self.assertIn('pump_running', status)
        self.assertIn('valve_open', status)
        self.assertIn('water_level', status)
        self.assertIn('flow_rate', status)
        self.assertIn('gpio_initialized', status)


class TestMotorController(unittest.TestCase):
    """Test motor controller functionality"""
    
    def setUp(self):
        # Mock serial to prevent actual hardware access
        with patch('serial.Serial'):
            self.motors = MotorController()
    
    def test_initialization(self):
        """Test motor controller initialization"""
        self.assertEqual(self.motors.left_speed, 0)
        self.assertEqual(self.motors.right_speed, 0)
        self.assertFalse(self.motors.emergency_stop)
    
    def test_speed_setting(self):
        """Test motor speed setting"""
        self.motors.set_motor_speeds(0.5, -0.3)
        self.assertEqual(self.motors.left_speed, 0.5)
        self.assertEqual(self.motors.right_speed, -0.3)
    
    def test_movement_commands(self):
        """Test movement command methods"""
        self.motors.move_forward(0.5)
        self.assertEqual(self.motors.left_speed, 0.5)
        self.assertEqual(self.motors.right_speed, 0.5)
        
        self.motors.turn_left(0.3)
        self.assertEqual(self.motors.left_speed, -0.3)
        self.assertEqual(self.motors.right_speed, 0.3)
        
        self.motors.stop_motors()
        self.assertEqual(self.motors.left_speed, 0)
        self.assertEqual(self.motors.right_speed, 0)
    
    def test_emergency_stop(self):
        """Test emergency stop functionality"""
        self.motors.set_motor_speeds(0.5, 0.5)
        self.motors.emergency_stop_enable()
        
        self.assertTrue(self.motors.emergency_stop)
        self.assertEqual(self.motors.left_speed, 0)
        self.assertEqual(self.motors.right_speed, 0)
        
        # Should not accept new commands while emergency stop is active
        self.motors.set_motor_speeds(0.5, 0.5)
        self.assertEqual(self.motors.left_speed, 0)
        self.assertEqual(self.motors.right_speed, 0)
    
    def test_status_reporting(self):
        """Test status reporting"""
        status = self.motors.get_status()
        
        self.assertIn('connected', status)
        self.assertIn('emergency_stop', status)
        self.assertIn('left_speed', status)
        self.assertIn('right_speed', status)


class TestSpeechSystem(unittest.TestCase):
    """Test speech system functionality"""
    
    def setUp(self):
        self.speech = SpeechSystem()
    
    def test_initialization(self):
        """Test speech system initialization"""
        self.assertIsNotNone(self.speech.personality)
        self.assertIn('friendly', self.speech.personality)
    
    def test_speech_queueing(self):
        """Test speech message queueing"""
        # Start speech service
        self.speech.start_speech_service()
        
        # Queue a message
        self.speech.say("Test message")
        
        # Check that message was queued
        self.assertGreater(self.speech.speech_queue.qsize(), 0)
        
        # Stop service
        self.speech.stop_speech_service()
    
    def test_announcement_methods(self):
        """Test various announcement methods"""
        # These should not raise exceptions
        self.speech.announce_startup()
        self.speech.announce_plant_status("test_plant", 25.5, True)
        self.speech.announce_watering_start("test_plant", 15.0)
        self.speech.announce_watering_complete("test_plant", 0.35)
        self.speech.announce_error("water_low")
    
    def test_personality_settings(self):
        """Test personality configuration"""
        original_friendly = self.speech.personality['friendly']
        
        self.speech.set_personality(friendly=False)
        self.assertFalse(self.speech.personality['friendly'])
        
        # Restore original
        self.speech.set_personality(friendly=original_friendly)
    
    def test_status_reporting(self):
        """Test status reporting"""
        status = self.speech.get_status()
        
        self.assertIn('tts_available', status)
        self.assertIn('audio_initialized', status)
        self.assertIn('speech_active', status)
        self.assertIn('personality', status)


class TestGardenBrain(unittest.TestCase):
    """Test garden brain AI system"""
    
    def setUp(self):
        # Mock all hardware dependencies
        with patch.multiple(
            'gardener_robot.ai.garden_brain',
            EnvironmentalSensors=MagicMock(),
            WateringSystem=MagicMock(),
            MotorController=MagicMock(),
            SpeechSystem=MagicMock(),
            GardenerYOLODetector=MagicMock()
        ):
            self.brain = GardenBrain()
    
    def test_initialization(self):
        """Test garden brain initialization"""
        self.assertIsNotNone(self.brain.config)
        self.assertIn('garden', self.brain.config)
        self.assertIn('behavior', self.brain.config)
        self.assertIn('safety', self.brain.config)
    
    def test_plant_database_initialization(self):
        """Test plant database setup"""
        self.brain._initialize_plant_database()
        
        self.assertGreater(len(self.brain.plant_database), 0)
        
        # Check that each plant has required fields
        for plant_id, plant_data in self.brain.plant_database.items():
            self.assertIn('type', plant_data)
            self.assertIn('location', plant_data)
            self.assertIn('water_schedule', plant_data)
            self.assertIn('health_score', plant_data)
    
    def test_configuration_loading(self):
        """Test configuration system"""
        config = self.brain._load_config(None)  # Load defaults
        
        self.assertIn('garden', config)
        self.assertIn('plants', config['garden'])
        self.assertIn('behavior', config)
        self.assertIn('safety', config)
    
    def test_manual_watering_request(self):
        """Test manual watering functionality"""
        self.brain._initialize_plant_database()
        
        # Get a plant ID from the database
        plant_id = list(self.brain.plant_database.keys())[0]
        
        # Request manual watering
        result = self.brain.manual_water_plant(plant_id, 10.0)
        self.assertTrue(result)
        
        # Check that task was added to queue
        self.assertGreater(len(self.brain.task_queue), 0)
        
        # Check task details
        task = self.brain.task_queue[0]
        self.assertEqual(task['type'], 'water_plant')
        self.assertEqual(task['plant_id'], plant_id)
    
    def test_status_reporting(self):
        """Test comprehensive status reporting"""
        # Mock the sensors to return status
        self.brain.sensors.get_garden_summary.return_value = {
            'timestamp': 1234567890,
            'environmental_conditions': {
                'temperature': 25.0,
                'humidity': 60.0,
                'light_level': 1000.0,
                'ph_level': 7.0
            },
            'soil_moisture': {'plant1': 45.0},
            'plant_statuses': {},
            'urgent_needs': []
        }
        
        status = self.brain.get_garden_status()
        
        self.assertIn('robot_status', status)
        self.assertIn('environmental_conditions', status)
        
        robot_status = status['robot_status']
        self.assertIn('active', robot_status)
        self.assertIn('performance_metrics', robot_status)
        self.assertIn('subsystem_status', robot_status)


def run_basic_tests():
    """Run all basic system tests"""
    print("🧪 Running Basic System Tests 🧪")
    print("=" * 40)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestSoilMoistureSensor))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvironmentalSensors))
    suite.addTests(loader.loadTestsFromTestCase(TestWateringSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestMotorController))
    suite.addTests(loader.loadTestsFromTestCase(TestSpeechSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestGardenBrain))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 40)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)