# Jetson Nano Robot Project - Claude Instructions

## Project Overview
This is a robotics project for the Nvidia Jetson Orin Nano featuring:
- GPIO control for motors and sensors
- Computer vision with camera interface
- AI/ML object detection capabilities
- Tank tread mobility system
- Temperature monitoring
- Battery power management

## Development Commands

### Testing & Validation
```bash
# Test basic system functionality
python3 hello_jetson.py

# Run unit tests
python3 -m pytest tests/

# Check GPIO permissions
sudo usermod -a -G gpio $USER

# Test camera
python3 scripts/test_camera.py
```

### Docker Commands
```bash
# Build ARM64 container
docker build -t jetson-robot:latest -f docker/Dockerfile .

# Run with GPU support
docker run --runtime nvidia --rm -it jetson-robot:latest

# Docker compose for development
docker-compose -f docker/docker-compose.yml up
```

### System Setup
```bash
# Install JetPack SDK dependencies
sudo apt update && sudo apt install -y python3-pip python3-dev

# Install requirements
pip3 install -r requirements.txt

# Set up GPIO permissions
sudo groupadd -f gpio
sudo usermod -a -G gpio $USER
```

### ROS 2 Integration
```bash
# Source ROS 2 (if using ROS)
source /opt/ros/humble/setup.bash

# Build workspace
colcon build

# Run robot nodes
ros2 run jetson_robot robot_controller
```

## Hardware Configuration
- Battery: 12V LiPo with BMS
- Motors: DC motors with L298N driver
- Cameras: CSI or USB cameras
- Sensors: Temperature sensors via I2C
- GPIO: Jetson.GPIO library for hardware control

## Key Files
- `src/robot_controller.py` - Main robot control logic
- `src/vision/camera_manager.py` - Camera interface
- `src/sensors/temperature_sensor.py` - Temperature monitoring
- `src/motors/motor_control.py` - Motor control
- `config/robot_config.yaml` - Robot configuration
- `hello_jetson.py` - System validation script

## Common Issues
- GPIO permissions: Run `sudo usermod -a -G gpio $USER` and reboot
- Camera not detected: Check CSI cable connection and run `v4l2-ctl --list-devices`
- Docker GPU access: Ensure nvidia-docker2 is installed