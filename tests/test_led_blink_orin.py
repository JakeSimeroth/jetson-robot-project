#!/usr/bin/env python3
"""
LED Blink Test for Jetson Orin Nano
Tests GPIO functionality by blinking an LED on pin 7 for 10 cycles.
Uses sysfs GPIO interface for broader compatibility.
"""

import time
import os
import sys

class GPIOController:
    """Simple GPIO controller using sysfs interface"""
    
    def __init__(self, pin_number):
        self.pin = pin_number
        self.gpio_path = f"/sys/class/gpio/gpio{pin_number}"
        self.export_path = "/sys/class/gpio/export"
        self.unexport_path = "/sys/class/gpio/unexport"
        
    def setup(self):
        """Export and configure GPIO pin"""
        try:
            # Export the pin
            with open(self.export_path, 'w') as f:
                f.write(str(self.pin))
            time.sleep(0.1)  # Give time for export
            
            # Set direction to output
            with open(f"{self.gpio_path}/direction", 'w') as f:
                f.write("out")
                
            print(f"GPIO pin {self.pin} configured as output")
            return True
            
        except Exception as e:
            print(f"Error setting up GPIO pin {self.pin}: {e}")
            return False
    
    def set_value(self, value):
        """Set GPIO pin value (0 or 1)"""
        try:
            with open(f"{self.gpio_path}/value", 'w') as f:
                f.write(str(value))
        except Exception as e:
            print(f"Error setting GPIO value: {e}")
    
    def cleanup(self):
        """Unexport GPIO pin"""
        try:
            self.set_value(0)  # Turn off first
            with open(self.unexport_path, 'w') as f:
                f.write(str(self.pin))
            print(f"GPIO pin {self.pin} cleaned up")
        except Exception as e:
            print(f"Error cleaning up GPIO: {e}")


def run_led_blink_test():
    """Run LED blink test on GPIO pin 7"""
    
    # Jetson Orin Nano pin 7 corresponds to GPIO pin 106
    GPIO_PIN = 106  # This is the actual GPIO number for pin 7 on Orin Nano
    BLINK_COUNT = 10
    BLINK_DURATION = 0.5
    
    print("=== LED Blink Test for Jetson Orin Nano ===")
    print(f"Using GPIO pin {GPIO_PIN} (physical pin 7)")
    print(f"Blinking {BLINK_COUNT} times")
    print("Connect LED with 220Ω resistor between pin 7 and GND")
    print("Press Ctrl+C to stop early")
    
    gpio = GPIOController(GPIO_PIN)
    
    try:
        if not gpio.setup():
            print("Failed to set up GPIO. You may need to run with sudo.")
            return False
        
        for cycle in range(BLINK_COUNT):
            print(f"Blink {cycle + 1}/{BLINK_COUNT}")
            
            # LED on
            gpio.set_value(1)
            print("  LED ON")
            time.sleep(BLINK_DURATION)
            
            # LED off
            gpio.set_value(0)
            print("  LED OFF")
            time.sleep(BLINK_DURATION)
        
        print("LED blink test completed successfully!")
        return True
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return False
    except Exception as e:
        print(f"Error during test: {e}")
        return False
    finally:
        gpio.cleanup()


if __name__ == "__main__":
    success = run_led_blink_test()
    sys.exit(0 if success else 1)