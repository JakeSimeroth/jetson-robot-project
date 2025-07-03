# 🌱 Gardener Robot Hardware Selection Guide

## Core System Requirements
- **Jetson Orin Nano** (✓ Already have) - Main compute unit
- **C922x USB Camera** (✓ Already have) - Vision system
- **Onboard battery system** - Power management
- **Tank treads** - Mobility platform
- **Watering system** - Plant care
- **Speaker system** - AI communication
- **Environmental sensors** - Garden monitoring

---

## 🔋 Battery & Power System

### Primary Battery
**Recommended: Tattu 22.2V 6S 10000mAh LiPo**
- **Voltage**: 22.2V (6S configuration)
- **Capacity**: 10000mAh (provides 4-6 hours runtime)
- **Discharge Rate**: 25C (250A burst capability)
- **Connector**: XT90 or XT60
- **Price**: ~$150-200

### Power Distribution
**Matek PDB-XT60** - Power Distribution Board
- **Input**: 22.2V from main battery
- **Outputs**: 
  - 12V for motors (via step-down converter)
  - 5V for Jetson and sensors
  - 3.3V for logic circuits
- **BEC**: Built-in voltage regulation
- **Price**: ~$25

### Battery Management
**ISDT T8 BattGo Smart Charger**
- **Charging**: 1-8S LiPo support
- **Safety**: Overcharge/discharge protection
- **Monitoring**: Cell voltage monitoring
- **Price**: ~$80

---

## 🚗 Movement System (Tank Treads)

### Track Platform
**Dagu Rover 5 Tracked Chassis**
- **Dimensions**: 26cm x 16cm x 7cm
- **Material**: Aluminum frame with rubber tracks
- **Motor Mounts**: Pre-installed gear motors
- **Load Capacity**: 2kg payload
- **Price**: ~$85

### Motors
**12V DC Gear Motors (2x required)**
- **Voltage**: 12V DC
- **Speed**: 150 RPM (with gearbox)
- **Torque**: 40 kg⋅cm
- **Encoder**: Quadrature encoder for position feedback
- **Price**: ~$45 each

### Motor Control
**Sabertooth 2x25 Motor Driver**
- **Channels**: Dual channel (left/right tracks)
- **Voltage**: 6V-30V input
- **Current**: 25A continuous per channel
- **Interface**: Serial, R/C, or analog control
- **Protection**: Overcurrent, thermal protection
- **Price**: ~$130

---

## 💧 Watering System

### Water Pump
**12V Submersible Water Pump**
- **Voltage**: 12V DC
- **Flow Rate**: 240L/hour (4L/min)
- **Head Height**: 2m maximum
- **Size**: Compact design for tank mounting
- **Price**: ~$25

### Water Tank
**Food-Grade Water Container**
- **Capacity**: 5L (1.3 gallon)
- **Material**: BPA-free plastic
- **Mounting**: Secure brackets for robot chassis
- **Filler**: Wide mouth for easy refilling
- **Price**: ~$20

### Flow Control
**12V Solenoid Valve**
- **Voltage**: 12V DC operation
- **Flow**: Normally closed, precise control
- **Thread**: 1/4" NPT connections
- **Response**: Fast open/close action
- **Price**: ~$15

### Hose & Nozzle
**Garden Hose Kit**
- **Hose**: 3m flexible tubing (6mm ID)
- **Nozzle**: Adjustable spray pattern
- **Fittings**: Quick-connect couplers
- **Price**: ~$20

---

## 🔊 Audio System

### Speaker
**Adafruit I2S 3W Stereo Speaker Bonnet**
- **Interface**: I2S connection to Jetson
- **Power**: 3W per channel
- **Quality**: Clear voice reproduction
- **Mounting**: Compact PCB design
- **Price**: ~$25

### Microphone (Optional)
**USB Microphone Array**
- **Channels**: 4-mic array for voice detection
- **Interface**: USB 2.0
- **Range**: 360° pickup pattern
- **Price**: ~$35

---

## 🌡️ Environmental Sensors

### Temperature & Humidity
**DHT22 Sensor**
- **Temperature**: -40°C to 80°C (±0.5°C accuracy)
- **Humidity**: 0-100% RH (±2% accuracy)
- **Interface**: Single-wire digital
- **Price**: ~$10

### Soil Moisture
**Capacitive Soil Moisture Sensor**
- **Type**: Capacitive (corrosion resistant)
- **Output**: Analog voltage (0-3V)
- **Interface**: I2C or analog ADC
- **Price**: ~$8 each (get 3-5 sensors)

### Light Sensor
**VEML7700 Ambient Light Sensor**
- **Range**: 0.0036 to 120,000 lux
- **Interface**: I2C communication
- **Resolution**: 16-bit
- **Price**: ~$7

### pH Sensor (Advanced)
**Atlas Scientific pH Sensor Kit**
- **Range**: pH 0.001 - 14.000
- **Interface**: I2C or UART
- **Calibration**: 3-point calibration
- **Price**: ~$185 (professional grade)

---

## 🔌 Connectivity & Interface

### GPIO Expansion
**Adafruit 16-Channel PWM Driver**
- **Channels**: 16 PWM outputs
- **Interface**: I2C (chainable)
- **Voltage**: 5V logic compatible
- **Uses**: Servo control, LED dimming
- **Price**: ~$15

### Voltage Level Shifting
**SparkFun Logic Level Converter**
- **Voltage**: Bidirectional 3.3V ↔ 5V
- **Channels**: 4 channels
- **Protection**: Built-in protection
- **Price**: ~$3

### USB Hub
**Powered USB 3.0 Hub**
- **Ports**: 4-port hub
- **Power**: External 5V adapter
- **Speed**: USB 3.0 compatibility
- **Price**: ~$25

---

## 🔧 Mechanical Components

### Mounting Hardware
**Aluminum T-Slot Extrusion Kit**
- **Profile**: 20mm x 20mm T-slot
- **Length**: Various lengths (1m sections)
- **Brackets**: Corner brackets and joining plates
- **Price**: ~$50 for complete kit

### Weather Protection
**IP65 Enclosure for Electronics**
- **Material**: ABS plastic with gasket seal
- **Size**: 200mm x 150mm x 75mm
- **Features**: Cable glands, mounting points
- **Price**: ~$30

### Cables & Connectors
**Waterproof Connector Kit**
- **Types**: XT60, JST, Molex connectors
- **Rating**: IP67 waterproof rating
- **Includes**: Heat shrink tubing, cable ties
- **Price**: ~$25

---

## 📊 Total Cost Estimate

| Category | Component | Price | Qty | Total |
|----------|-----------|-------|-----|-------|
| **Power** | 6S 10000mAh LiPo Battery | $180 | 1 | $180 |
| | Power Distribution Board | $25 | 1 | $25 |
| | Battery Charger | $80 | 1 | $80 |
| **Movement** | Tracked Chassis | $85 | 1 | $85 |
| | DC Gear Motors | $45 | 2 | $90 |
| | Motor Driver | $130 | 1 | $130 |
| **Watering** | Water Pump | $25 | 1 | $25 |
| | Water Tank | $20 | 1 | $20 |
| | Solenoid Valve | $15 | 1 | $15 |
| | Hose Kit | $20 | 1 | $20 |
| **Audio** | I2S Speaker | $25 | 1 | $25 |
| **Sensors** | DHT22 (Temp/Humidity) | $10 | 1 | $10 |
| | Soil Moisture Sensors | $8 | 4 | $32 |
| | Light Sensor | $7 | 1 | $7 |
| **Electronics** | PWM Driver | $15 | 1 | $15 |
| | Logic Level Converter | $3 | 2 | $6 |
| | USB Hub | $25 | 1 | $25 |
| **Mechanical** | T-Slot Kit | $50 | 1 | $50 |
| | IP65 Enclosure | $30 | 1 | $30 |
| | Connectors & Cables | $25 | 1 | $25 |
| **TOTAL** | | | | **$901** |

---

## 🛒 Shopping List by Priority

### Phase 1 - Core Mobility ($285)
- [ ] Tracked Chassis ($85)
- [ ] DC Gear Motors x2 ($90)
- [ ] Motor Driver ($130)

### Phase 2 - Power System ($285)
- [ ] LiPo Battery ($180)
- [ ] Power Distribution Board ($25)
- [ ] Battery Charger ($80)

### Phase 3 - Watering System ($80)
- [ ] Water Pump ($25)
- [ ] Water Tank ($20)
- [ ] Solenoid Valve ($15)
- [ ] Hose Kit ($20)

### Phase 4 - Sensors & Audio ($89)
- [ ] I2S Speaker ($25)
- [ ] DHT22 Sensor ($10)
- [ ] Soil Moisture Sensors x4 ($32)
- [ ] Light Sensor ($7)
- [ ] PWM Driver ($15)

### Phase 5 - Support Components ($162)
- [ ] Logic Level Converters ($6)
- [ ] USB Hub ($25)
- [ ] T-Slot Kit ($50)
- [ ] IP65 Enclosure ($30)
- [ ] Connectors & Cables ($25)
- [ ] pH Sensor (Optional) ($185)

---

## 🔗 Recommended Suppliers

### Electronics
- **Adafruit** - Sensors, breakouts, speaker systems
- **SparkFun** - Development boards, connectors
- **Pololu** - Motors, motor drivers, robotics parts

### Batteries & Power
- **HobbyKing** - LiPo batteries, chargers
- **Amazon** - Power distribution, voltage converters

### Mechanical
- **ServoCity** - Aluminum extrusion, mounting hardware
- **McMaster-Carr** - Professional mechanical components

### Specialized
- **Atlas Scientific** - Professional pH/water quality sensors
- **RobotShop** - Complete robotics systems and parts

---

## ⚠️ Safety Considerations

### Electrical Safety
- **Fuse Protection**: Install appropriate fuses for each power rail
- **Voltage Monitoring**: Monitor battery voltage to prevent over-discharge
- **Waterproofing**: Protect all electronics from moisture

### Mechanical Safety
- **Weight Distribution**: Keep center of gravity low
- **Emergency Stop**: Implement wireless emergency stop
- **Speed Limiting**: Limit maximum speed for safety

### Chemical Safety
- **Water Quality**: Use only clean water in system
- **pH Handling**: Follow safety protocols for pH sensor calibration
- **Battery Handling**: Proper LiPo storage and charging procedures