# 🌱 Autonomous Gardener Robot

An intelligent autonomous robot for garden care, built on the NVIDIA Jetson Orin Nano platform. Features computer vision plant detection, environmental monitoring, automated watering, tank tread mobility, and AI-powered garden management with voice communication.

## 🎯 Project Overview

### Core Features
- **🤖 Autonomous Operation**: AI-driven garden management and plant care
- **👁️ Computer Vision**: YOLO-based plant and object detection using C922x camera
- **💧 Smart Watering**: Precision watering system with flow control and monitoring
- **🚗 Tank Tread Mobility**: Differential steering for navigating garden terrain
- **🗣️ Voice Communication**: Text-to-speech announcements and status updates
- **📊 Environmental Monitoring**: Soil moisture, temperature, humidity, light, and pH sensors
- **🧠 AI Decision Making**: Intelligent plant care scheduling and optimization
- **⚡ Battery Powered**: Autonomous operation with rechargeable LiPo battery system

### Target Applications
- **Home Gardens**: Automated care for vegetable and herb gardens
- **Greenhouse Management**: Monitoring and maintenance of controlled environments
- **Research**: Plant growth studies and agricultural automation
- **Education**: STEM learning platform for robotics and AI

---

## 🏗️ System Architecture

```
🌱 Gardener Robot System
├── 🧠 AI Core (Garden Brain)
│   ├── Decision Making Engine
│   ├── Plant Care Database
│   ├── Learning & Adaptation
│   └── Task Scheduling
├── 👁️ Vision System
│   ├── C922x USB Camera
│   ├── YOLOv8 Object Detection
│   ├── Plant Recognition
│   └── Navigation Assistance
├── 💧 Watering System
│   ├── 12V Water Pump
│   ├── Solenoid Valve Control
│   ├── Flow Rate Monitoring
│   └── Tank Level Management
├── 🚗 Mobility System
│   ├── Tank Tread Chassis
│   ├── Dual DC Motors
│   ├── Sabertooth Driver
│   └── Differential Steering
├── 📊 Sensor Array
│   ├── Soil Moisture Sensors (4x)
│   ├── DHT22 (Temp/Humidity)
│   ├── VEML7700 (Light)
│   ├── pH Sensor (Optional)
│   └── Flow Rate Sensor
├── 🗣️ Communication
│   ├── Text-to-Speech Engine
│   ├── I2S Speaker System
│   ├── Status Announcements
│   └── Error Notifications
└── ⚡ Power Management
    ├── 6S LiPo Battery (22.2V)
    ├── Power Distribution Board
    ├── Voltage Regulation
    └── Battery Monitoring
```

---

## 🛠️ Hardware Requirements

See [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md) for complete hardware selection guide.

### Essential Components (~$900 total)
- **✅ NVIDIA Jetson Orin Nano** (provided)
- **✅ Logitech C922x Camera** (provided)
- **Tank Tread Chassis** with dual motors
- **Sabertooth Motor Driver**
- **6S LiPo Battery & Charger**
- **Water Pump & Tank System**
- **Environmental Sensors**
- **Speaker System**

---

## 🚀 Quick Start

### 1. Hardware Setup
1. **Assemble chassis** with tank treads and motors
2. **Install battery system** with power distribution
3. **Mount Jetson Orin Nano** in weatherproof enclosure
4. **Connect sensors** and watering system
5. **Attach camera** and speaker system

### 2. Software Installation
```bash
# Clone repository
git clone https://github.com/JakeSimeroth/jetson-robot-project.git
cd jetson-robot-project

# Install dependencies
pip3 install -r requirements_robot.txt

# Install additional speech dependencies
sudo apt install espeak espeak-data libespeak1 libespeak-dev

# Set up GPIO permissions
sudo usermod -a -G gpio $USER
sudo reboot  # Reboot to apply group changes
```

### 3. Configuration
```bash
# Copy and edit configuration
cp config/robot_config.json config/my_garden_config.json
nano config/my_garden_config.json  # Edit for your garden layout
```

### 4. Run Robot
```bash
# Test systems
python3 run_robot.py --mode diagnostic

# Manual control mode
python3 run_robot.py --mode manual

# Autonomous garden care
python3 run_robot.py --mode autonomous --config config/my_garden_config.json
```

---

## 🎮 Operation Modes

### 1. Autonomous Mode
Fully autonomous garden care with AI decision making:
```bash
python3 run_robot.py --mode autonomous
```
**Features:**
- Continuous environmental monitoring
- Intelligent watering schedules
- Plant health assessment
- Automatic navigation
- Voice status updates
- Emergency safety protocols

### 2. Manual Mode
Interactive control for testing and direct operation:
```bash
python3 run_robot.py --mode manual
```
**Commands:**
- `status` - Show garden and robot status
- `water <plant_id>` - Water specific plant
- `water all` - Water all plants
- `test_speech` - Test voice system
- `test_motors` - Test movement system
- `emergency_stop` - Stop all operations

### 3. Diagnostic Mode
Comprehensive system testing and validation:
```bash
python3 run_robot.py --mode diagnostic
```
**Tests:**
- Sensor connectivity and readings
- Motor control and safety systems
- Watering system operation
- Speech and audio output
- Camera and vision system
- GPIO and hardware interfaces

---

## 📊 System Monitoring

### Real-time Status
The robot provides continuous monitoring of:
- **Plant Health**: Soil moisture, watering needs, care history
- **Environmental Conditions**: Temperature, humidity, light levels
- **System Health**: Battery level, water tank, error conditions
- **Performance Metrics**: Plants watered, water usage, uptime

### Logging System
- **Standard Logs**: Detailed system operation logs with rotation
- **Event Logs**: Structured JSON logs for data analysis
- **Error Tracking**: Comprehensive error logging and recovery
- **Performance Metrics**: Historical data for optimization

### Voice Communication
The robot announces:
- **Startup/Shutdown**: System status changes
- **Plant Care**: Watering activities and plant status
- **Navigation**: Movement and location updates
- **Errors**: System issues and safety alerts
- **Daily Summary**: End-of-day care summary

---

## 🔧 Configuration

### Garden Layout
Configure your garden in `config/robot_config.json`:
```json
{
  "garden": {
    "plants": [
      {
        "id": "tomato_1",
        "type": "tomato",
        "location": [0, 0],
        "optimal_moisture": 65,
        "critical_moisture": 25
      }
    ],
    "area_size": [3, 1],
    "watering_thresholds": {
      "critical": 20.0,
      "low": 35.0,
      "optimal": 60.0
    }
  }
}
```

### Hardware Settings
Adjust for your specific hardware:
```json
{
  "hardware": {
    "motors": {
      "serial_port": "/dev/ttyUSB0",
      "max_speed": 0.8
    },
    "watering": {
      "pump_pin": 18,
      "valve_pin": 19,
      "max_pump_runtime": 300
    },
    "sensors": {
      "soil_sensors": [
        {"id": "tomato_1", "pin": 23}
      ]
    }
  }
}
```

---

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
python3 -m pytest tests/

# Test specific modules
python3 -m pytest tests/unit/test_watering_system.py
python3 -m pytest tests/unit/test_motor_controller.py
```

### Integration Tests
```bash
# Test complete system integration
python3 tests/integration/test_garden_brain.py

# Test hardware interfaces
python3 tests/hardware/test_all_sensors.py
```

### Manual Testing
```bash
# Test individual components
python3 gardener_robot/hardware/motor_controller.py
python3 gardener_robot/hardware/watering_system.py
python3 gardener_robot/sensors/environmental_sensors.py
python3 gardener_robot/communication/speech_system.py
```

---

## 📈 Performance Optimization

### Jetson Orin Nano Optimization
- **GPU Acceleration**: YOLO inference on integrated GPU
- **TensorRT**: Model optimization for faster inference
- **Power Management**: Balanced performance and battery life
- **Memory Management**: Efficient resource utilization

### AI Performance
- **Model Selection**: Lightweight YOLOv8n for real-time performance
- **Inference Speed**: ~220ms per frame on Orin Nano
- **Decision Making**: 60-second intervals for garden analysis
- **Learning**: Adaptive watering based on plant response

---

## 🛡️ Safety Features

### Emergency Systems
- **Emergency Stop**: Immediate halt of all operations
- **Timeout Protection**: Safety shutoffs for all actuators
- **Water Level Monitoring**: Prevents dry pump operation
- **Battery Monitoring**: Low voltage protection
- **Thermal Protection**: Temperature-based shutdowns

### Fail-Safe Design
- **Default Safe States**: All systems default to safe positions
- **Redundant Sensors**: Multiple monitoring systems
- **Manual Override**: Physical emergency stops
- **Error Recovery**: Automatic retry and fallback procedures

---

## 🔄 Maintenance

### Daily Maintenance
- Check water tank level
- Verify battery charge
- Clean camera lens
- Check plant sensor placement

### Weekly Maintenance
- Clean soil moisture sensors
- Check motor operation
- Verify watering system flow
- Review system logs

### Monthly Maintenance
- Deep clean watering system
- Calibrate sensors
- Update plant database
- Performance analysis

---

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip3 install -r requirements_robot.txt
pip3 install black flake8 mypy pytest

# Code formatting
black gardener_robot/
flake8 gardener_robot/

# Type checking
mypy gardener_robot/
```

### Adding New Features
1. **Sensors**: Add new sensor types in `gardener_robot/sensors/`
2. **Plants**: Extend plant database with new species care profiles
3. **Behaviors**: Implement new AI behaviors in `garden_brain.py`
4. **Hardware**: Add support for new actuators and devices

---

## 📚 Documentation

- **[Hardware Guide](HARDWARE_GUIDE.md)**: Complete component selection
- **[API Documentation](docs/api.md)**: Software interface reference
- **[Troubleshooting](docs/troubleshooting.md)**: Common issues and solutions
- **[Development Guide](docs/development.md)**: Contributing and extending

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **NVIDIA**: Jetson Orin Nano platform
- **Ultralytics**: YOLOv8 computer vision models
- **Adafruit**: Sensor libraries and hardware guides
- **Open Source Community**: Various libraries and tools

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JakeSimeroth/jetson-robot-project/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JakeSimeroth/jetson-robot-project/discussions)
- **Documentation**: [Project Wiki](https://github.com/JakeSimeroth/jetson-robot-project/wiki)

**Built with 💚 for sustainable and intelligent agriculture**