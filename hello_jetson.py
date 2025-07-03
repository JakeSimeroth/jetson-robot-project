#!/usr/bin/env python3
"""
hello_jetson.py - System validation script for Jetson Robot Project

This script performs basic system checks to ensure the Jetson Nano is ready
for robotics development.
"""

import sys
import os
import platform
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Python version is compatible")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False

def check_system_info():
    """Display system information"""
    print("\n🖥️  System Information:")
    print(f"   Platform: {platform.platform()}")
    print(f"   Architecture: {platform.machine()}")
    print(f"   Processor: {platform.processor()}")
    
    # Check if running on Jetson
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
            if 'jetson' in model.lower():
                print(f"   ✅ Jetson device detected: {model}")
                return True
            else:
                print(f"   ⚠️  Not a Jetson device: {model}")
                return False
    except FileNotFoundError:
        print("   ⚠️  Device model not available")
        return False

def check_gpio_access():
    """Check GPIO access permissions"""
    print("\n🔌 Checking GPIO access...")
    
    try:
        import Jetson.GPIO as GPIO
        print("   ✅ Jetson.GPIO library available")
        
        # Test GPIO setup (non-destructive)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        print("   ✅ GPIO access successful")
        return True
        
    except ImportError:
        print("   ❌ Jetson.GPIO not installed")
        print("   💡 Install with: pip3 install Jetson.GPIO")
        return False
    except Exception as e:
        print(f"   ❌ GPIO access failed: {e}")
        print("   💡 Try: sudo usermod -a -G gpio $USER && sudo reboot")
        return False

def check_camera_access():
    """Check camera connectivity"""
    print("\n📷 Checking camera access...")
    
    try:
        import cv2
        print("   ✅ OpenCV available")
        
        # Try to open camera
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                print(f"   ✅ Camera accessible (Resolution: {width}x{height})")
                cap.release()
                return True
            else:
                print("   ❌ Camera not capturing frames")
                cap.release()
                return False
        else:
            print("   ❌ Camera not accessible")
            return False
            
    except ImportError:
        print("   ❌ OpenCV not installed")
        print("   💡 Install with: pip3 install opencv-python")
        return False
    except Exception as e:
        print(f"   ❌ Camera check failed: {e}")
        return False

def check_cuda_support():
    """Check CUDA availability"""
    print("\n🚀 Checking CUDA support...")
    
    try:
        import torch
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0)
            print(f"   ✅ CUDA available: {device_name}")
            print(f"   ✅ GPU devices: {device_count}")
            return True
        else:
            print("   ❌ CUDA not available")
            return False
    except ImportError:
        print("   ⚠️  PyTorch not installed (optional)")
        return False

def check_disk_space():
    """Check available disk space"""
    print("\n💾 Checking disk space...")
    
    try:
        statvfs = os.statvfs('/')
        free_bytes = statvfs.f_frsize * statvfs.f_bavail
        total_bytes = statvfs.f_frsize * statvfs.f_blocks
        free_gb = free_bytes / (1024**3)
        total_gb = total_bytes / (1024**3)
        
        print(f"   Total: {total_gb:.1f} GB")
        print(f"   Free: {free_gb:.1f} GB")
        
        if free_gb > 5.0:
            print("   ✅ Sufficient disk space")
            return True
        else:
            print("   ⚠️  Low disk space")
            return False
            
    except Exception as e:
        print(f"   ❌ Disk check failed: {e}")
        return False

def check_network_connectivity():
    """Check network connectivity"""
    print("\n🌐 Checking network connectivity...")
    
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '8.8.8.8'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("   ✅ Network connectivity available")
            return True
        else:
            print("   ❌ Network connectivity failed")
            return False
    except subprocess.TimeoutExpired:
        print("   ❌ Network check timed out")
        return False
    except Exception as e:
        print(f"   ❌ Network check failed: {e}")
        return False

def check_project_structure():
    """Check project directory structure"""
    print("\n📁 Checking project structure...")
    
    required_dirs = [
        'src', 'src/robot', 'src/vision', 'src/sensors', 
        'src/motors', 'src/ai', 'config', 'tests'
    ]
    
    all_good = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"   ✅ {dir_name}/ exists")
        else:
            print(f"   ❌ {dir_name}/ missing")
            all_good = False
    
    return all_good

def main():
    """Main system check function"""
    print("🤖 Jetson Robot Project - System Validation")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("System Info", check_system_info),
        ("GPIO Access", check_gpio_access),
        ("Camera Access", check_camera_access),
        ("CUDA Support", check_cuda_support),
        ("Disk Space", check_disk_space),
        ("Network", check_network_connectivity),
        ("Project Structure", check_project_structure)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            logger.error(f"Check '{check_name}' failed with exception: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n📊 System Check Summary:")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {check_name:<20} {status}")
    
    print(f"\n🎯 Overall Score: {passed}/{total} checks passed")
    
    if passed == total:
        print("🚀 System is ready for robotics development!")
        return 0
    else:
        print("⚠️  Some issues detected. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())