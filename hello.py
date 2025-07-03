#!/usr/bin/env python3
"""
Hello World for Jetson Orin Nano Robotics Project
A simple introduction script that demonstrates basic Jetson capabilities
"""

import time
import sys
import os
import platform

def print_system_info():
    """Print system information about the Jetson"""
    print("=== Jetson Orin Nano System Information ===")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python Version: {platform.python_version()}")
    
    # Check for Jetson-specific info
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
        print(f"Device Model: {model}")
    except:
        print("Device Model: Unknown")
    
    try:
        with open('/etc/nv_tegra_release', 'r') as f:
            tegra_info = f.read().strip()
        print(f"Tegra Release: {tegra_info.split(',')[0]}")
    except:
        print("Tegra Release: Not found")

def test_onboard_led():
    """Test the onboard LED"""
    print("\n=== Testing Onboard LED ===")
    led_path = "/sys/class/leds/mmc0::"
    
    try:
        # Quick LED test
        print("Blinking onboard LED 3 times...")
        for i in range(3):
            # LED on
            os.system(f"echo '1' | sudo tee {led_path}/brightness > /dev/null 2>&1")
            print(f"  Blink {i+1} - ON")
            time.sleep(0.3)
            
            # LED off
            os.system(f"echo '0' | sudo tee {led_path}/brightness > /dev/null 2>&1")
            print(f"  Blink {i+1} - OFF")
            time.sleep(0.3)
        
        print("LED test completed!")
        return True
        
    except Exception as e:
        print(f"LED test failed: {e}")
        return False

def check_robotics_capabilities():
    """Check available robotics-related capabilities"""
    print("\n=== Checking Robotics Capabilities ===")
    
    # Check GPIO access
    gpio_available = os.path.exists('/dev/gpiochip0')
    print(f"GPIO Access: {'✓ Available' if gpio_available else '✗ Not available'}")
    
    # Check camera devices
    camera_devices = []
    for i in range(10):
        if os.path.exists(f'/dev/video{i}'):
            camera_devices.append(f'/dev/video{i}')
    print(f"Camera Devices: {camera_devices if camera_devices else 'None found'}")
    
    # Check I2C buses
    i2c_buses = []
    for i in range(10):
        if os.path.exists(f'/dev/i2c-{i}'):
            i2c_buses.append(f'/dev/i2c-{i}')
    print(f"I2C Buses: {i2c_buses if i2c_buses else 'None found'}")
    
    # Check UART devices
    uart_devices = []
    for device in ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyS0']:
        if os.path.exists(device):
            uart_devices.append(device)
    print(f"UART Devices: {uart_devices if uart_devices else 'None found'}")
    
    return {
        'gpio': gpio_available,
        'cameras': len(camera_devices),
        'i2c_buses': len(i2c_buses),
        'uart_devices': len(uart_devices)
    }

def main():
    """Main function"""
    print("🤖 Hello from Jetson Orin Nano Robotics Project! 🤖")
    print("=" * 50)
    
    # System information
    print_system_info()
    
    # Test onboard LED
    led_success = test_onboard_led()
    
    # Check robotics capabilities
    capabilities = check_robotics_capabilities()
    
    # Summary
    print("\n=== Project Status ===")
    print(f"LED Control: {'✓ Working' if led_success else '✗ Failed'}")
    print(f"GPIO Available: {'✓ Yes' if capabilities['gpio'] else '✗ No'}")
    print(f"Cameras Found: {capabilities['cameras']}")
    print(f"I2C Buses: {capabilities['i2c_buses']}")
    print(f"UART Devices: {capabilities['uart_devices']}")
    
    print("\n🎯 Ready to start building your robotics project!")
    print("Next steps:")
    print("  1. Connect sensors and actuators")
    print("  2. Test camera functionality")
    print("  3. Set up motor control")
    print("  4. Implement autonomous behaviors")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)