# Jetson Robot Project

A comprehensive robotics project for the Nvidia Jetson Orin Nano featuring computer vision, AI/ML object detection, motor control, and sensor integration.

## Features

- 🤖 **Robot Control**: Tank tread mobility with GPIO-controlled motors
- 📷 **Computer Vision**: Camera interface with OpenCV integration
- 🧠 **AI/ML**: Object detection using YOLO and TensorRT
- 🌡️ **Sensor Integration**: Temperature and humidity monitoring
- 🔋 **Power Management**: Battery monitoring and power optimization
- 🐳 **Docker Support**: Containerized deployment for ARM64
- 🔧 **ROS Integration**: Ready for ROS 2 integration

## Hardware Requirements

- Nvidia Jetson Orin Nano Developer Kit
- CSI or USB Camera
- DC Motors with L298N Motor Driver
- DHT22 Temperature/Humidity Sensor
- 12V LiPo Battery with BMS
- Tank Tread Chassis
- Jumper Wires and Breadboard

## Quick Start

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-dev python3-opencv

# Set up GPIO permissions
sudo groupadd -f gpio
sudo usermod -a -G gpio $USER
sudo reboot
```

### 2. Install Python Dependencies

```bash
# Install project requirements
pip3 install -r requirements.txt

# For additional AI/ML capabilities
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. Test System

```bash
# Run system test
python3 hello_jetson.py

# Test camera
python3 scripts/test_camera.py
```

### 4. Run Robot

```bash
# Start robot controller
python3 src/robot/robot_controller.py

# Or use Docker
docker build -t jetson-robot .
docker run --runtime nvidia --privileged jetson-robot
```

## Project Structure

```
jetson-robot-project/
├── src/                          # Source code
│   ├── robot/                    # Robot control logic
│   │   └── robot_controller.py   # Main robot controller
│   ├── vision/                   # Computer vision
│   │   └── camera_manager.py     # Camera interface
│   ├── sensors/                  # Sensor interfaces
│   │   └── temperature_sensor.py # Temperature monitoring
│   ├── motors/                   # Motor control
│   │   └── motor_control.py      # GPIO motor control
│   └── ai/                       # AI/ML modules
│       └── object_detection.py   # YOLO object detection
├── tests/                        # Test files
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
├── config/                       # Configuration files
│   └── robot_config.yaml         # Robot configuration
├── scripts/                      # Utility scripts
├── docker/                       # Docker configuration
├── hello_jetson.py              # System test script
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Configuration

Edit `config/robot_config.yaml` to customize:

- Camera settings (resolution, FPS)
- Motor GPIO pin assignments
- Sensor configurations
- AI/ML model parameters
- Power management settings

## Hardware Connections

### Motor Driver (L298N)
- ENA → GPIO 20 (Left Motor PWM)
- IN1 → GPIO 18 (Left Motor Direction 1)
- IN2 → GPIO 19 (Left Motor Direction 2)
- ENB → GPIO 23 (Right Motor PWM)
- IN3 → GPIO 21 (Right Motor Direction 1)
- IN4 → GPIO 22 (Right Motor Direction 2)

### Temperature Sensor (DHT22)
- VCC → 3.3V
- GND → GND
- DATA → GPIO 4

### Camera
- CSI Camera → CSI connector
- Or USB Camera → USB port

## Development

### Running Tests

```bash
# Run unit tests
python3 -m pytest tests/unit/

# Run integration tests
python3 -m pytest tests/integration/

# Run all tests
python3 -m pytest
```

### Docker Development

```bash
# Build development image
docker build -t jetson-robot:dev -f docker/Dockerfile.dev .

# Run with development setup
docker-compose -f docker/docker-compose.yml up
```

### ROS 2 Integration

```bash
# Install ROS 2 Humble
sudo apt install ros-humble-desktop

# Source ROS 2
source /opt/ros/humble/setup.bash

# Build ROS workspace
colcon build

# Run ROS nodes
ros2 run jetson_robot robot_controller
```

## AI/ML Models

### Object Detection

The project supports YOLO models for object detection:

1. Download pre-trained YOLO weights
2. Place in `models/` directory
3. Update config with model paths
4. Use TensorRT for optimization

### Custom Models

Add your own models to `src/ai/` and integrate with the main robot controller.

## Troubleshooting

### Common Issues

**GPIO Permission Denied**
```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

**Camera Not Detected**
```bash
# Check available cameras
v4l2-ctl --list-devices

# Test camera
gst-launch-1.0 nvarguscamerasrc ! nvoverlaysink
```

**Docker GPU Access**
```bash
# Install nvidia-docker2
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update && sudo apt install -y nvidia-docker2
sudo systemctl restart docker
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Nvidia for the Jetson platform
- OpenCV community
- ROS community
- Contributors and testers