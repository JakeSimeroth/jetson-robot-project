#!/bin/bash

# Development entrypoint script for Jetson Robot container

echo "🛠️  Starting Jetson Robot Development Environment"
echo "================================================"

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

# Install project in development mode
echo "Installing project in development mode..."
pip3 install -e .

# Run system validation
echo "Running system validation..."
python3 hello_jetson.py

# Start services based on arguments
if [ "$1" = "jupyter" ]; then
    echo "Starting Jupyter Lab..."
    jupyter lab --allow-root --ip=0.0.0.0 --port=8888 --no-browser
elif [ "$1" = "shell" ]; then
    echo "Starting interactive shell..."
    exec /bin/bash
elif [ $# -gt 0 ]; then
    echo "Running command: $@"
    exec "$@"
else
    echo "Starting development environment..."
    echo "Available commands:"
    echo "  jupyter - Start Jupyter Lab"
    echo "  shell   - Start interactive shell"
    echo ""
    echo "Project structure:"
    tree -L 3 /app
    echo ""
    echo "Starting interactive shell..."
    exec /bin/bash
fi