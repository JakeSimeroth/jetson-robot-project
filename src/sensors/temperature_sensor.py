#!/usr/bin/env python3

import time
import logging
from typing import Optional

try:
    import board
    import busio
    import adafruit_dht
    DHT_AVAILABLE = True
except ImportError:
    DHT_AVAILABLE = False

class TemperatureSensor:
    def __init__(self, sensor_type: str = "DHT22", pin: int = 4):
        self.sensor_type = sensor_type
        self.pin = pin
        self.logger = logging.getLogger(__name__)
        self.sensor = None
        
    def initialize(self) -> bool:
        """Initialize temperature sensor"""
        if not DHT_AVAILABLE:
            self.logger.warning("DHT sensor libraries not available")
            return False
            
        try:
            if self.sensor_type == "DHT22":
                self.sensor = adafruit_dht.DHT22(getattr(board, f"D{self.pin}"))
            elif self.sensor_type == "DHT11":
                self.sensor = adafruit_dht.DHT11(getattr(board, f"D{self.pin}"))
            else:
                self.logger.error(f"Unsupported sensor type: {self.sensor_type}")
                return False
                
            self.logger.info(f"{self.sensor_type} sensor initialized on pin {self.pin}")
            return True
        except Exception as e:
            self.logger.error(f"Sensor initialization failed: {e}")
            return False
            
    def read_temperature(self) -> Optional[float]:
        """Read temperature in Celsius"""
        if not self.sensor:
            return None
            
        try:
            temperature = self.sensor.temperature
            if temperature is not None:
                return temperature
        except Exception as e:
            self.logger.error(f"Failed to read temperature: {e}")
        return None
        
    def read_humidity(self) -> Optional[float]:
        """Read humidity percentage"""
        if not self.sensor:
            return None
            
        try:
            humidity = self.sensor.humidity
            if humidity is not None:
                return humidity
        except Exception as e:
            self.logger.error(f"Failed to read humidity: {e}")
        return None
        
    def get_readings(self) -> dict:
        """Get both temperature and humidity readings"""
        return {
            "temperature": self.read_temperature(),
            "humidity": self.read_humidity(),
            "timestamp": time.time()
        }