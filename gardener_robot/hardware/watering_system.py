#!/usr/bin/env python3
"""
Watering System Controller for Gardener Robot
Controls water pump, solenoid valves, and flow monitoring
"""

import time
import threading
from typing import Optional, Dict
import logging

try:
    import gpiod
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("gpiod not available - watering system will run in simulation mode")


class WateringSystem:
    """Complete watering system with pump, valve, and flow control"""
    
    def __init__(self, pump_pin=18, valve_pin=19, flow_sensor_pin=20, chip_number=0):
        """
        Initialize watering system
        
        Args:
            pump_pin: GPIO pin for water pump relay
            valve_pin: GPIO pin for solenoid valve
            flow_sensor_pin: GPIO pin for flow sensor (optional)
            chip_number: GPIO chip number
        """
        self.pump_pin = pump_pin
        self.valve_pin = valve_pin
        self.flow_sensor_pin = flow_sensor_pin
        self.chip_number = chip_number
        
        # GPIO setup
        self.chip = None
        self.pump_line = None
        self.valve_line = None
        self.flow_line = None
        self.gpio_initialized = False
        
        # System state
        self.pump_running = False
        self.valve_open = False
        self.water_level = 100.0  # Percentage (will be measured by sensor)
        self.flow_rate = 0.0  # L/min
        self.total_dispensed = 0.0  # Total liters dispensed
        
        # Safety limits
        self.max_pump_runtime = 300  # 5 minutes max continuous operation
        self.min_water_level = 10.0  # Stop if water level below 10%
        self.pump_start_time = None
        
        # Flow monitoring
        self.flow_pulses = 0
        self.last_flow_time = time.time()
        self.flow_calibration = 7.5  # Pulses per liter (typical for YF-S201)
        
        self.logger = logging.getLogger(__name__)
        
        # Safety monitor thread
        self.safety_thread = threading.Thread(target=self._safety_monitor, daemon=True)
        self.safety_thread.start()
    
    def initialize_gpio(self) -> bool:
        """Initialize GPIO pins for watering system"""
        if not GPIO_AVAILABLE:
            self.logger.warning("GPIO not available - running in simulation mode")
            return True
        
        try:
            # Open GPIO chip
            self.chip = gpiod.Chip(f'gpiochip{self.chip_number}')
            
            # Setup pump control (output)
            self.pump_line = self.chip.get_line(self.pump_pin)
            self.pump_line.request(consumer="PUMP_CONTROL", type=gpiod.LINE_REQ_DIR_OUT)
            self.pump_line.set_value(0)  # Start with pump off
            
            # Setup valve control (output)
            self.valve_line = self.chip.get_line(self.valve_pin)
            self.valve_line.request(consumer="VALVE_CONTROL", type=gpiod.LINE_REQ_DIR_OUT)
            self.valve_line.set_value(0)  # Start with valve closed
            
            # Setup flow sensor (input with interrupt)
            self.flow_line = self.chip.get_line(self.flow_sensor_pin)
            self.flow_line.request(consumer="FLOW_SENSOR", type=gpiod.LINE_REQ_DIR_IN)
            
            self.gpio_initialized = True
            self.logger.info("Watering system GPIO initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GPIO: {e}")
            return False
    
    def cleanup_gpio(self):
        """Clean up GPIO resources"""
        if self.gpio_initialized:
            self.stop_pump()
            self.close_valve()
            
            if self.pump_line:
                self.pump_line.release()
            if self.valve_line:
                self.valve_line.release()
            if self.flow_line:
                self.flow_line.release()
            if self.chip:
                self.chip.close()
            
            self.gpio_initialized = False
            self.logger.info("GPIO resources cleaned up")
    
    def start_pump(self) -> bool:
        """Start water pump with safety checks"""
        if self.pump_running:
            self.logger.warning("Pump already running")
            return True
        
        # Safety checks
        if self.water_level < self.min_water_level:
            self.logger.error(f"Water level too low: {self.water_level}%")
            return False
        
        try:
            if self.gpio_initialized and self.pump_line:
                self.pump_line.set_value(1)
            
            self.pump_running = True
            self.pump_start_time = time.time()
            self.logger.info("Water pump started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start pump: {e}")
            return False
    
    def stop_pump(self):
        """Stop water pump"""
        try:
            if self.gpio_initialized and self.pump_line:
                self.pump_line.set_value(0)
            
            self.pump_running = False
            self.pump_start_time = None
            self.logger.info("Water pump stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop pump: {e}")
    
    def open_valve(self) -> bool:
        """Open solenoid valve"""
        try:
            if self.gpio_initialized and self.valve_line:
                self.valve_line.set_value(1)
            
            self.valve_open = True
            self.logger.info("Solenoid valve opened")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open valve: {e}")
            return False
    
    def close_valve(self):
        """Close solenoid valve"""
        try:
            if self.gpio_initialized and self.valve_line:
                self.valve_line.set_value(0)
            
            self.valve_open = False
            self.logger.info("Solenoid valve closed")
            
        except Exception as e:
            self.logger.error(f"Failed to close valve: {e}")
    
    def water_plant(self, duration: float, flow_rate: Optional[float] = None) -> bool:
        """
        Water a plant for specified duration
        
        Args:
            duration: Watering duration in seconds
            flow_rate: Target flow rate in L/min (None for max flow)
            
        Returns:
            Success status
        """
        if duration <= 0:
            self.logger.error("Invalid watering duration")
            return False
        
        if duration > self.max_pump_runtime:
            self.logger.error(f"Duration {duration}s exceeds max runtime {self.max_pump_runtime}s")
            return False
        
        self.logger.info(f"Starting watering sequence: {duration}s duration")
        
        try:
            # Start pump and open valve
            if not self.start_pump():
                return False
            
            if not self.open_valve():
                self.stop_pump()
                return False
            
            # Monitor watering process
            start_time = time.time()
            initial_dispensed = self.total_dispensed
            
            while time.time() - start_time < duration:
                # Check safety conditions
                if self.water_level < self.min_water_level:
                    self.logger.error("Water level too low - stopping")
                    break
                
                # Update flow monitoring
                self._update_flow_rate()
                
                # Log progress
                elapsed = time.time() - start_time
                dispensed = self.total_dispensed - initial_dispensed
                if elapsed > 0 and int(elapsed) % 5 == 0:  # Log every 5 seconds
                    self.logger.info(f"Watering progress: {elapsed:.1f}s, {dispensed:.2f}L dispensed")
                
                time.sleep(0.1)
            
            # Stop watering
            self.close_valve()
            self.stop_pump()
            
            final_dispensed = self.total_dispensed - initial_dispensed
            self.logger.info(f"Watering complete: {final_dispensed:.2f}L dispensed in {duration}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during watering: {e}")
            self.close_valve()
            self.stop_pump()
            return False
    
    def prime_system(self, duration: float = 5.0) -> bool:
        """Prime the watering system to remove air bubbles"""
        self.logger.info(f"Priming watering system for {duration}s")
        return self.water_plant(duration)
    
    def _update_flow_rate(self):
        """Update flow rate measurement from sensor"""
        if not self.gpio_initialized or not self.flow_line:
            # Simulate flow rate in demo mode
            if self.pump_running and self.valve_open:
                self.flow_rate = 2.0  # Simulated 2 L/min
                self.total_dispensed += self.flow_rate / 60.0 * 0.1  # Update every 0.1s
            else:
                self.flow_rate = 0.0
            return
        
        try:
            # Read flow sensor (in real implementation, would use interrupt)
            current_time = time.time()
            time_diff = current_time - self.last_flow_time
            
            if time_diff >= 1.0:  # Calculate flow rate every second
                # Convert pulses to liters
                liters = self.flow_pulses / self.flow_calibration
                self.flow_rate = liters * 60.0  # Convert to L/min
                self.total_dispensed += liters
                
                # Reset counters
                self.flow_pulses = 0
                self.last_flow_time = current_time
                
        except Exception as e:
            self.logger.error(f"Error reading flow sensor: {e}")
    
    def _update_water_level(self):
        """Update water level from tank sensor"""
        # In real implementation, would read from ultrasonic or float sensor
        # For now, simulate gradual decrease
        if self.pump_running and self.valve_open:
            self.water_level -= 0.1  # Decrease by 0.1% per safety check
            self.water_level = max(0.0, self.water_level)
    
    def _safety_monitor(self):
        """Safety monitoring thread"""
        while True:
            time.sleep(1.0)
            
            # Update sensors
            self._update_water_level()
            self._update_flow_rate()
            
            # Check pump runtime
            if self.pump_running and self.pump_start_time:
                runtime = time.time() - self.pump_start_time
                if runtime > self.max_pump_runtime:
                    self.logger.error(f"Pump runtime exceeded {self.max_pump_runtime}s - emergency stop")
                    self.emergency_stop()
            
            # Check water level
            if self.pump_running and self.water_level < self.min_water_level:
                self.logger.error(f"Water level critical: {self.water_level}% - stopping pump")
                self.stop_pump()
                self.close_valve()
    
    def emergency_stop(self):
        """Emergency stop all watering operations"""
        self.logger.warning("WATERING SYSTEM EMERGENCY STOP")
        self.stop_pump()
        self.close_valve()
    
    def get_status(self) -> Dict:
        """Get watering system status"""
        runtime = 0
        if self.pump_running and self.pump_start_time:
            runtime = time.time() - self.pump_start_time
        
        return {
            'pump_running': self.pump_running,
            'valve_open': self.valve_open,
            'water_level': self.water_level,
            'flow_rate': self.flow_rate,
            'total_dispensed': self.total_dispensed,
            'pump_runtime': runtime,
            'gpio_initialized': self.gpio_initialized
        }


def main():
    """Test watering system functionality"""
    logging.basicConfig(level=logging.INFO)
    
    watering = WateringSystem()
    
    if not watering.initialize_gpio():
        print("Failed to initialize GPIO")
        return
    
    try:
        print("Testing watering system...")
        
        # Get status
        status = watering.get_status()
        print(f"Initial status: {status}")
        
        # Prime system
        print("Priming system...")
        watering.prime_system(3.0)
        
        # Water for 5 seconds
        print("Watering plant...")
        watering.water_plant(5.0)
        
        # Final status
        status = watering.get_status()
        print(f"Final status: {status}")
        
        print("Watering system test complete!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        watering.cleanup_gpio()


if __name__ == "__main__":
    main()