#!/bin/bash

# Entrypoint script for Jetson Robot container

echo "🤖 Starting Jetson Robot Container"
echo "=================================="

# Check if running on Jetson
if [ -f "/proc/device-tree/model" ]; then
    MODEL=$(cat /proc/device-tree/model)
    echo "Device: $MODEL"
else
    echo "Warning: Not running on Jetson hardware"
fi

# Set up GPIO permissions
if [ -e "/dev/gpiomem" ]; then
    echo "Setting up GPIO permissions..."
    chmod 666 /dev/gpiomem
fi

# Check camera devices
echo "Checking camera devices..."
if ls /dev/video* 1> /dev/null 2>&1; then
    echo "Camera devices found:"
    ls -la /dev/video*
else
    echo "No camera devices found"
fi

# Run system validation
echo "Running system validation..."
python3 hello_jetson.py

# If specific command provided, run it
if [ $# -gt 0 ]; then
    echo "Running command: $@"
    exec "$@"
else
    echo "Starting interactive shell..."
    exec /bin/bash
fi