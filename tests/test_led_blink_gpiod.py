#!/usr/bin/env python3
"""
LED Blink Test for Jetson Orin Nano using onboard LED
Tests onboard LED functionality by blinking the built-in LED 10 times.
"""

import time
import sys
import os

def run_onboard_led_blink_test():
    """Run LED blink test using onboard LED"""
    
    LED_PATH = "/sys/class/leds/mmc0::"
    BRIGHTNESS_FILE = f"{LED_PATH}/brightness"
    TRIGGER_FILE = f"{LED_PATH}/trigger"
    BLINK_COUNT = 10
    BLINK_DURATION = 0.5
    
    print("=== Onboard LED Blink Test for Jetson Orin Nano ===")
    print(f"Using onboard LED: {LED_PATH}")
    print(f"Blinking {BLINK_COUNT} times")
    print("Watch for the onboard LED to blink!")
    print("Press Ctrl+C to stop early")
    
    try:
        # Save original trigger setting
        try:
            with open(TRIGGER_FILE, 'r') as f:
                original_trigger = f.read().strip()
            print(f"Original trigger: {original_trigger}")
        except:
            original_trigger = "mmc0"
        
        # Set trigger to none for manual control
        try:
            with open(TRIGGER_FILE, 'w') as f:
                f.write("none")
            print("LED trigger set to manual control")
        except PermissionError:
            print("Permission denied. Trying with sudo...")
            os.system(f"echo 'none' | sudo tee {TRIGGER_FILE} > /dev/null")
        
        # Blink the LED
        for cycle in range(BLINK_COUNT):
            print(f"Blink {cycle + 1}/{BLINK_COUNT}")
            
            # LED on
            try:
                with open(BRIGHTNESS_FILE, 'w') as f:
                    f.write("1")
            except PermissionError:
                os.system(f"echo '1' | sudo tee {BRIGHTNESS_FILE} > /dev/null")
            print("  LED ON")
            time.sleep(BLINK_DURATION)
            
            # LED off
            try:
                with open(BRIGHTNESS_FILE, 'w') as f:
                    f.write("0")
            except PermissionError:
                os.system(f"echo '0' | sudo tee {BRIGHTNESS_FILE} > /dev/null")
            print("  LED OFF")
            time.sleep(BLINK_DURATION)
        
        print("Onboard LED blink test completed successfully!")
        return True
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return False
    except Exception as e:
        print(f"Error during test: {e}")
        return False
    finally:
        try:
            # Turn off LED and restore original trigger
            try:
                with open(BRIGHTNESS_FILE, 'w') as f:
                    f.write("0")
            except PermissionError:
                os.system(f"echo '0' | sudo tee {BRIGHTNESS_FILE} > /dev/null")
                
            try:
                with open(TRIGGER_FILE, 'w') as f:
                    f.write(original_trigger)
            except PermissionError:
                os.system(f"echo '{original_trigger}' | sudo tee {TRIGGER_FILE} > /dev/null")
            print("LED restored to original state")
        except:
            print("Warning: Could not restore LED state")
            pass


if __name__ == "__main__":
    success = run_onboard_led_blink_test()
    sys.exit(0 if success else 1)