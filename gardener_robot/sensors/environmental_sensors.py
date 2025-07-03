#!/usr/bin/env python3
"""
Environmental Sensors for Gardener Robot
Handles soil moisture, temperature, humidity, light, and pH monitoring
"""

import time
import threading
from typing import Dict, List, Optional
import logging
import random

try:
    import board
    import busio
    import adafruit_dht
    import adafruit_veml7700
    I2C_AVAILABLE = True
except ImportError:
    I2C_AVAILABLE = False
    print("Adafruit libraries not available - sensors will run in simulation mode")

try:
    import gpiod
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class SoilMoistureSensor:
    """Capacitive soil moisture sensor"""
    
    def __init__(self, sensor_id: str, pin: int, chip_number: int = 0):
        self.sensor_id = sensor_id
        self.pin = pin
        self.chip_number = chip_number
        self.chip = None
        self.line = None
        self.initialized = False
        
        # Calibration values (adjust based on your sensor)
        self.dry_value = 3.3  # Voltage when completely dry
        self.wet_value = 1.0  # Voltage when completely wet
        
        self.logger = logging.getLogger(__name__)
    
    def initialize(self) -> bool:
        """Initialize the sensor"""
        if not GPIO_AVAILABLE:
            self.logger.warning(f"GPIO not available for sensor {self.sensor_id}")
            return True  # Allow simulation mode
        
        try:
            self.chip = gpiod.Chip(f'gpiochip{self.chip_number}')
            self.line = self.chip.get_line(self.pin)
            self.line.request(consumer=f"SOIL_SENSOR_{self.sensor_id}", type=gpiod.LINE_REQ_DIR_IN)
            self.initialized = True
            self.logger.info(f"Soil moisture sensor {self.sensor_id} initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize soil sensor {self.sensor_id}: {e}")
            return False
    
    def read_moisture(self) -> float:
        """Read soil moisture percentage (0-100%)"""
        if not self.initialized:
            # Simulation mode
            return random.uniform(20, 80)
        
        try:
            # In real implementation, would read ADC value
            # For now, simulate reading
            voltage = random.uniform(self.wet_value, self.dry_value)
            
            # Convert to percentage (100% = wet, 0% = dry)
            if self.dry_value != self.wet_value:
                moisture = ((self.dry_value - voltage) / (self.dry_value - self.wet_value)) * 100
                moisture = max(0, min(100, moisture))
            else:
                moisture = 50.0
            
            return moisture
        except Exception as e:
            self.logger.error(f"Error reading soil sensor {self.sensor_id}: {e}")
            return 0.0
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.line:
            self.line.release()
        if self.chip:
            self.chip.close()
        self.initialized = False


class EnvironmentalSensors:
    """Complete environmental monitoring system"""
    
    def __init__(self, dht_pin=22, soil_sensors_config=None):
        """
        Initialize environmental sensors
        
        Args:
            dht_pin: GPIO pin for DHT22 temperature/humidity sensor
            soil_sensors_config: List of soil sensor configs [{'id': 'plant1', 'pin': 23}, ...]
        """
        self.dht_pin = dht_pin
        self.soil_sensors_config = soil_sensors_config or [
            {'id': 'plant1', 'pin': 23},
            {'id': 'plant2', 'pin': 24},
            {'id': 'plant3', 'pin': 25},
        ]
        
        # Sensors
        self.dht_sensor = None
        self.light_sensor = None
        self.soil_sensors = {}
        
        # Latest readings
        self.temperature = 25.0  # Celsius
        self.humidity = 50.0  # Percentage
        self.light_level = 1000.0  # Lux
        self.soil_moisture = {}  # {sensor_id: moisture_percentage}
        self.ph_level = 7.0  # pH value
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.update_interval = 30.0  # seconds
        
        self.logger = logging.getLogger(__name__)
    
    def initialize(self) -> bool:
        """Initialize all environmental sensors"""
        success = True
        
        # Initialize DHT22 sensor
        if I2C_AVAILABLE:
            try:
                self.dht_sensor = adafruit_dht.DHT22(getattr(board, f'D{self.dht_pin}'))
                self.logger.info("DHT22 temperature/humidity sensor initialized")
            except Exception as e:
                self.logger.warning(f"DHT22 sensor failed to initialize: {e}")
                success = False
        else:
            self.logger.warning("DHT22 sensor not available - using simulation")
        
        # Initialize light sensor
        if I2C_AVAILABLE:
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                self.light_sensor = adafruit_veml7700.VEML7700(i2c)
                self.logger.info("VEML7700 light sensor initialized")
            except Exception as e:
                self.logger.warning(f"Light sensor failed to initialize: {e}")
                success = False
        else:
            self.logger.warning("Light sensor not available - using simulation")
        
        # Initialize soil moisture sensors
        for config in self.soil_sensors_config:
            sensor = SoilMoistureSensor(config['id'], config['pin'])
            if sensor.initialize():
                self.soil_sensors[config['id']] = sensor
                self.soil_moisture[config['id']] = 0.0
            else:
                success = False
        
        self.logger.info(f"Environmental sensors initialized: {len(self.soil_sensors)} soil sensors")
        return success
    
    def start_monitoring(self):
        """Start continuous sensor monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Environmental monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous sensor monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        self.logger.info("Environmental monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self.update_all_readings()
                time.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5.0)
    
    def update_all_readings(self):
        """Update all sensor readings"""
        # Temperature and humidity
        self._update_temperature_humidity()
        
        # Light level
        self._update_light_level()
        
        # Soil moisture
        self._update_soil_moisture()
        
        # pH (would be updated separately in real system)
        self._update_ph_level()
        
        self.logger.debug(f"Sensor readings updated: T={self.temperature}°C, H={self.humidity}%, L={self.light_level}lux")
    
    def _update_temperature_humidity(self):
        """Update temperature and humidity from DHT22"""
        try:
            if self.dht_sensor:
                temp = self.dht_sensor.temperature
                humid = self.dht_sensor.humidity
                
                if temp is not None and humid is not None:
                    self.temperature = temp
                    self.humidity = humid
                else:
                    self.logger.warning("DHT22 returned None values")
            else:
                # Simulation mode
                self.temperature = 25.0 + random.uniform(-5, 10)
                self.humidity = 50.0 + random.uniform(-20, 30)
                
        except Exception as e:
            self.logger.error(f"Error reading DHT22: {e}")
            # Use simulated values
            self.temperature = 25.0 + random.uniform(-5, 10)
            self.humidity = 50.0 + random.uniform(-20, 30)
    
    def _update_light_level(self):
        """Update light level from VEML7700"""
        try:
            if self.light_sensor:
                self.light_level = self.light_sensor.light
            else:
                # Simulation mode - vary by time of day
                hour = time.localtime().tm_hour
                if 6 <= hour <= 18:  # Daytime
                    self.light_level = random.uniform(10000, 100000)
                else:  # Nighttime
                    self.light_level = random.uniform(0, 100)
                    
        except Exception as e:
            self.logger.error(f"Error reading light sensor: {e}")
            # Default simulation
            self.light_level = random.uniform(1000, 50000)
    
    def _update_soil_moisture(self):
        """Update soil moisture from all sensors"""
        for sensor_id, sensor in self.soil_sensors.items():
            try:
                moisture = sensor.read_moisture()
                self.soil_moisture[sensor_id] = moisture
            except Exception as e:
                self.logger.error(f"Error reading soil sensor {sensor_id}: {e}")
    
    def _update_ph_level(self):
        """Update pH level (simulated - real sensor would be separate)"""
        # Simulate pH with small variations
        self.ph_level = 7.0 + random.uniform(-0.5, 0.5)
    
    def get_plant_needs(self, plant_id: str) -> Dict:
        """Analyze plant needs based on sensor data"""
        if plant_id not in self.soil_moisture:
            return {'error': f'Plant {plant_id} not found'}
        
        moisture = self.soil_moisture[plant_id]
        needs = {
            'plant_id': plant_id,
            'current_moisture': moisture,
            'needs_water': moisture < 30.0,
            'water_urgency': 'high' if moisture < 20.0 else 'medium' if moisture < 40.0 else 'low',
            'optimal_conditions': {
                'temperature_ok': 15.0 <= self.temperature <= 30.0,
                'humidity_ok': 40.0 <= self.humidity <= 70.0,
                'light_ok': self.light_level > 1000.0,
                'ph_ok': 6.0 <= self.ph_level <= 8.0
            }
        }
        
        # Calculate watering recommendation
        if needs['needs_water']:
            # Base watering time on how dry the soil is
            dryness_factor = (30.0 - moisture) / 30.0  # 0-1 scale
            base_time = 10.0  # seconds
            needs['recommended_watering_time'] = base_time * dryness_factor
        else:
            needs['recommended_watering_time'] = 0.0
        
        return needs
    
    def get_garden_summary(self) -> Dict:
        """Get complete garden environmental summary"""
        plant_statuses = {}
        for plant_id in self.soil_moisture.keys():
            plant_statuses[plant_id] = self.get_plant_needs(plant_id)
        
        return {
            'timestamp': time.time(),
            'environmental_conditions': {
                'temperature': self.temperature,
                'humidity': self.humidity,
                'light_level': self.light_level,
                'ph_level': self.ph_level
            },
            'soil_moisture': self.soil_moisture.copy(),
            'plant_statuses': plant_statuses,
            'urgent_needs': [
                plant_id for plant_id, status in plant_statuses.items()
                if status.get('water_urgency') == 'high'
            ]
        }
    
    def cleanup(self):
        """Clean up all sensor resources"""
        self.stop_monitoring()
        
        for sensor in self.soil_sensors.values():
            sensor.cleanup()
        
        self.logger.info("Environmental sensors cleaned up")


def main():
    """Test environmental sensors"""
    logging.basicConfig(level=logging.INFO)
    
    sensors = EnvironmentalSensors()
    
    if not sensors.initialize():
        print("Failed to initialize some sensors")
    
    try:
        print("Starting environmental monitoring...")
        sensors.start_monitoring()
        
        # Run for 30 seconds
        for i in range(6):
            time.sleep(5)
            summary = sensors.get_garden_summary()
            print(f"\nGarden Status Update {i+1}:")
            print(f"Temperature: {summary['environmental_conditions']['temperature']:.1f}°C")
            print(f"Humidity: {summary['environmental_conditions']['humidity']:.1f}%")
            print(f"Light: {summary['environmental_conditions']['light_level']:.0f} lux")
            
            for plant_id, moisture in summary['soil_moisture'].items():
                print(f"Plant {plant_id}: {moisture:.1f}% moisture")
            
            if summary['urgent_needs']:
                print(f"URGENT: Plants need water: {summary['urgent_needs']}")
        
        print("\nEnvironmental monitoring test complete!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        sensors.cleanup()


if __name__ == "__main__":
    main()