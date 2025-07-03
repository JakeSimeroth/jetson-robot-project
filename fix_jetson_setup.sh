#!/bin/bash

echo "🔧 Jetson Nano Setup Fix Script"
echo "================================"

echo "1. 🔌 Fixing GPIO permissions..."
sudo usermod -a -G gpio $USER
sudo groupadd -f gpio
echo "   ✅ Added user to gpio group"

echo ""
echo "2. 📷 Checking camera devices..."
echo "Available video devices:"
ls -la /dev/video* 2>/dev/null || echo "No video devices found"

echo ""
echo "Checking for CSI cameras:"
ls -la /dev/nvhost-* 2>/dev/null || echo "No CSI devices found"

echo ""
echo "3. 📦 Installing missing dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-dev

echo ""
echo "Installing Jetson GPIO library..."
sudo pip3 install Jetson.GPIO

echo ""
echo "Installing PyTorch for Jetson (this may take a while)..."
sudo pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo ""
echo "4. 🔍 Installing additional camera tools..."
sudo apt install -y v4l-utils

echo ""
echo "5. 📋 System info after fixes:"
echo "Groups for user $USER:"
groups $USER

echo ""
echo "Video devices:"
v4l2-ctl --list-devices 2>/dev/null || echo "v4l2-ctl not available"

echo ""
echo "🔄 IMPORTANT: You need to reboot for GPIO changes to take effect!"
echo "Run: sudo reboot"
echo ""
echo "After reboot, run: python3 hello_jetson.py"