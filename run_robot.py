#!/usr/bin/env python3
"""
Main entry point for Gardener Robot
Simplified launcher script for the complete gardener robot system
"""

import sys
import os
from pathlib import Path

# Add gardener_robot to Python path
sys.path.insert(0, str(Path(__file__).parent / "gardener_robot"))

from gardener_robot.control.main_controller import main

if __name__ == "__main__":
    main()