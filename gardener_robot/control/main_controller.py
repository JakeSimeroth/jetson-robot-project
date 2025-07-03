#!/usr/bin/env python3
"""
Main Controller for Gardener Robot
Entry point and coordination for all robot systems
"""

import os
import sys
import time
import signal
import logging
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from ai.garden_brain import GardenBrain
from communication.speech_system import SpeechSystem


class GardenerRobotController:
    """Main controller for the complete gardener robot system"""
    
    def __init__(self, config_file: str = None, log_level: str = "INFO"):
        """
        Initialize the main robot controller
        
        Args:
            config_file: Path to configuration file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.config_file = config_file
        self.log_level = log_level
        
        # Setup logging
        self._setup_logging()
        
        # Initialize garden brain (main AI system)
        self.garden_brain = GardenBrain(config_file)
        
        # System state
        self.running = False
        self.shutdown_requested = False
        
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Setup file and console logging
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=log_format,
            handlers=[
                logging.FileHandler(log_dir / "gardener_robot.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown_requested = True
    
    def startup(self) -> bool:
        """Start up the robot system"""
        self.logger.info("🌱 Starting Gardener Robot System 🌱")
        
        try:
            # Initialize all subsystems
            if not self.garden_brain.initialize_systems():
                self.logger.error("Failed to initialize robot systems")
                return False
            
            self.logger.info("Robot system startup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during startup: {e}")
            return False
    
    def run_autonomous_mode(self):
        """Run robot in autonomous garden care mode"""
        if not self.startup():
            self.logger.error("Startup failed - cannot run autonomous mode")
            return
        
        try:
            self.logger.info("Starting autonomous garden care mode")
            self.running = True
            
            # Start autonomous operation
            self.garden_brain.start_autonomous_operation()
            
            # Main monitoring loop
            while self.running and not self.shutdown_requested:
                time.sleep(5.0)
                
                # Get system status
                status = self.garden_brain.get_garden_status()
                
                # Check for critical issues
                if status['robot_status']['subsystem_status']['watering']['water_level'] < 5.0:
                    self.logger.critical("Critical water level - manual intervention required")
                
                # Log periodic status
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self._log_status_summary(status)
            
            self.logger.info("Autonomous mode stopped")
            
        except KeyboardInterrupt:
            self.logger.info("Autonomous mode interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in autonomous mode: {e}")
        finally:
            self.shutdown()
    
    def run_manual_mode(self):
        """Run robot in manual control mode"""
        if not self.startup():
            self.logger.error("Startup failed - cannot run manual mode")
            return
        
        try:
            self.logger.info("Starting manual control mode")
            self.running = True
            
            # Display available commands
            self._show_manual_commands()
            
            while self.running and not self.shutdown_requested:
                try:
                    command = input("\nEnter command (h for help, q to quit): ").strip().lower()
                    
                    if command == 'q' or command == 'quit':
                        break
                    elif command == 'h' or command == 'help':
                        self._show_manual_commands()
                    elif command == 'status':
                        self._show_status()
                    elif command.startswith('water'):
                        self._handle_manual_watering(command)
                    elif command == 'test_speech':
                        self._test_speech()
                    elif command == 'test_motors':
                        self._test_motors()
                    elif command == 'emergency_stop':
                        self.garden_brain.emergency_stop()
                    else:
                        print(f"Unknown command: {command}")
                        
                except EOFError:
                    break
                except Exception as e:
                    self.logger.error(f"Error processing command: {e}")
            
            self.logger.info("Manual mode stopped")
            
        except Exception as e:
            self.logger.error(f"Error in manual mode: {e}")
        finally:
            self.shutdown()
    
    def _show_manual_commands(self):
        """Show available manual commands"""
        print("\n🌱 Gardener Robot Manual Commands 🌱")
        print("=" * 40)
        print("h, help          - Show this help")
        print("q, quit          - Quit manual mode")
        print("status           - Show system status")
        print("water <plant_id> - Water specific plant")
        print("water all        - Water all plants")
        print("test_speech      - Test speech system")
        print("test_motors      - Test motor system")
        print("emergency_stop   - Emergency stop all systems")
        print("=" * 40)
    
    def _show_status(self):
        """Show current system status"""
        status = self.garden_brain.get_garden_status()
        
        print("\n🌱 Garden Status 🌱")
        print("=" * 30)
        
        # Environmental conditions
        env = status['environmental_conditions']
        print(f"Temperature: {env['temperature']:.1f}°C")
        print(f"Humidity: {env['humidity']:.1f}%")
        print(f"Light Level: {env['light_level']:.0f} lux")
        print(f"pH Level: {env['ph_level']:.1f}")
        
        # Plant status
        print("\nPlant Status:")
        for plant_id, moisture in status['soil_moisture'].items():
            needs_water = moisture < 35.0
            status_icon = "💧" if needs_water else "✅"
            print(f"  {status_icon} {plant_id}: {moisture:.1f}% moisture")
        
        # Robot status
        robot = status['robot_status']
        print(f"\nRobot Status:")
        print(f"  Active: {robot['active']}")
        print(f"  Current Task: {robot['current_task']}")
        print(f"  Tasks Queued: {robot['task_queue_length']}")
        
        # Performance metrics
        metrics = robot['performance_metrics']
        print(f"\nToday's Performance:")
        print(f"  Plants Watered: {metrics['plants_watered_today']}")
        print(f"  Water Used: {metrics['water_used_today']:.2f}L")
        print(f"  Errors: {metrics['errors_today']}")
    
    def _handle_manual_watering(self, command: str):
        """Handle manual watering commands"""
        parts = command.split()
        if len(parts) < 2:
            print("Usage: water <plant_id> or water all")
            return
        
        if parts[1] == 'all':
            # Water all plants
            plant_ids = list(self.garden_brain.plant_database.keys())
            print(f"Watering all plants: {plant_ids}")
            for plant_id in plant_ids:
                success = self.garden_brain.manual_water_plant(plant_id)
                if success:
                    print(f"  ✅ Queued watering for {plant_id}")
                else:
                    print(f"  ❌ Failed to queue watering for {plant_id}")
        else:
            # Water specific plant
            plant_id = parts[1]
            success = self.garden_brain.manual_water_plant(plant_id)
            if success:
                print(f"✅ Queued watering for {plant_id}")
            else:
                print(f"❌ Failed to queue watering for {plant_id}")
    
    def _test_speech(self):
        """Test speech system"""
        print("Testing speech system...")
        speech = self.garden_brain.speech
        speech.say("Hello! This is a test of my speech system. How do I sound?")
        print("Speech test queued")
    
    def _test_motors(self):
        """Test motor system"""
        print("Testing motor system...")
        motors = self.garden_brain.motors
        
        if not motors.is_connected:
            print("❌ Motors not connected")
            return
        
        print("Moving forward...")
        motors.move_forward(0.3)
        time.sleep(2)
        
        print("Stopping...")
        motors.stop_motors()
        time.sleep(1)
        
        print("Turning left...")
        motors.turn_left(0.3)
        time.sleep(1)
        
        print("Stopping...")
        motors.stop_motors()
        
        print("✅ Motor test complete")
    
    def _log_status_summary(self, status: dict):
        """Log periodic status summary"""
        robot = status['robot_status']
        urgent_needs = status.get('urgent_needs', [])
        
        self.logger.info(f"Status: Active={robot['active']}, "
                        f"Task={robot['current_task']}, "
                        f"Queue={robot['task_queue_length']}, "
                        f"Urgent={len(urgent_needs)}")
    
    def run_diagnostic_mode(self):
        """Run system diagnostics"""
        self.logger.info("Running system diagnostics...")
        
        if not self.startup():
            return
        
        try:
            # Test each subsystem
            print("\n🔧 System Diagnostics 🔧")
            print("=" * 30)
            
            # Sensor test
            print("Testing sensors...")
            self.garden_brain.sensors.update_all_readings()
            summary = self.garden_brain.sensors.get_garden_summary()
            print(f"  ✅ Environmental sensors: {len(summary['soil_moisture'])} plants monitored")
            
            # Watering system test
            print("Testing watering system...")
            watering_status = self.garden_brain.watering.get_status()
            print(f"  ✅ Watering system: GPIO initialized = {watering_status['gpio_initialized']}")
            
            # Motor test
            print("Testing motor system...")
            motor_status = self.garden_brain.motors.get_status()
            print(f"  ✅ Motor system: Connected = {motor_status['connected']}")
            
            # Speech test
            print("Testing speech system...")
            self.garden_brain.speech.say("Diagnostic test of speech system")
            speech_status = self.garden_brain.speech.get_status()
            print(f"  ✅ Speech system: TTS available = {speech_status['tts_available']}")
            
            # Vision test
            print("Testing vision system...")
            print("  ⚠️  Vision system: Camera detection requires manual verification")
            
            print("\n✅ Diagnostic complete!")
            
        except Exception as e:
            self.logger.error(f"Error during diagnostics: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the robot system gracefully"""
        self.logger.info("Shutting down robot system...")
        
        self.running = False
        
        try:
            # Cleanup garden brain (handles all subsystems)
            self.garden_brain.cleanup()
            
            self.logger.info("Robot system shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Gardener Robot Controller')
    parser.add_argument('--mode', choices=['autonomous', 'manual', 'diagnostic'], 
                       default='manual', help='Robot operation mode')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Create controller
    controller = GardenerRobotController(
        config_file=args.config,
        log_level=args.log_level
    )
    
    # Run in selected mode
    if args.mode == 'autonomous':
        controller.run_autonomous_mode()
    elif args.mode == 'manual':
        controller.run_manual_mode()
    elif args.mode == 'diagnostic':
        controller.run_diagnostic_mode()


if __name__ == "__main__":
    main()