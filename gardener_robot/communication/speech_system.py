#!/usr/bin/env python3
"""
Speech System for Gardener Robot
Handles text-to-speech, audio output, and voice communication
"""

import os
import subprocess
import threading
import time
from typing import Optional, Dict, List
import logging
import queue

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("pyttsx3 not available - speech will use espeak fallback")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("pygame not available - audio playback limited")


class SpeechSystem:
    """Text-to-speech and audio communication system"""
    
    def __init__(self, voice_rate=150, voice_volume=0.8):
        """
        Initialize speech system
        
        Args:
            voice_rate: Speech rate (words per minute)
            voice_volume: Voice volume (0.0 to 1.0)
        """
        self.voice_rate = voice_rate
        self.voice_volume = voice_volume
        
        # TTS engine
        self.tts_engine = None
        self.tts_available = False
        
        # Audio system
        self.audio_initialized = False
        
        # Speech queue for non-blocking operation
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        self.speech_active = False
        
        # Voice personality settings
        self.personality = {
            'friendly': True,
            'informative': True,
            'encouraging': True,
            'name': 'Garden Helper'
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize systems
        self._initialize_tts()
        self._initialize_audio()
    
    def _initialize_tts(self):
        """Initialize text-to-speech engine"""
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                
                # Configure voice properties
                self.tts_engine.setProperty('rate', self.voice_rate)
                self.tts_engine.setProperty('volume', self.voice_volume)
                
                # Try to select a better voice if available
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    # Prefer female voice if available
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                
                self.tts_available = True
                self.logger.info("pyttsx3 TTS engine initialized")
                
            except Exception as e:
                self.logger.warning(f"Failed to initialize pyttsx3: {e}")
                self.tts_available = False
        else:
            self.logger.warning("pyttsx3 not available - using espeak fallback")
    
    def _initialize_audio(self):
        """Initialize audio system"""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.audio_initialized = True
                self.logger.info("pygame audio system initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize pygame audio: {e}")
        else:
            self.logger.warning("pygame not available - limited audio support")
    
    def start_speech_service(self):
        """Start the speech service thread"""
        if self.speech_active:
            return
        
        self.speech_active = True
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        self.logger.info("Speech service started")
    
    def stop_speech_service(self):
        """Stop the speech service thread"""
        self.speech_active = False
        if self.speech_thread:
            self.speech_thread.join(timeout=5.0)
        self.logger.info("Speech service stopped")
    
    def _speech_worker(self):
        """Worker thread for processing speech queue"""
        while self.speech_active:
            try:
                # Get speech request from queue (blocking with timeout)
                speech_request = self.speech_queue.get(timeout=1.0)
                
                if speech_request:
                    text = speech_request.get('text', '')
                    priority = speech_request.get('priority', 'normal')
                    
                    if text:
                        self._synthesize_speech(text)
                
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in speech worker: {e}")
    
    def _synthesize_speech(self, text: str):
        """Actually synthesize and play speech"""
        try:
            if self.tts_available and self.tts_engine:
                # Use pyttsx3
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                # Fallback to espeak
                self._espeak_fallback(text)
                
        except Exception as e:
            self.logger.error(f"Error synthesizing speech: {e}")
            self._espeak_fallback(text)
    
    def _espeak_fallback(self, text: str):
        """Fallback TTS using espeak command line"""
        try:
            # Escape text for shell
            safe_text = text.replace('"', '\\"').replace('`', '\\`')
            
            # Build espeak command
            cmd = [
                'espeak',
                '-s', str(self.voice_rate),
                '-a', str(int(self.voice_volume * 100)),
                '-v', 'en+f3',  # English female voice
                safe_text
            ]
            
            # Execute espeak
            subprocess.run(cmd, check=True, capture_output=True)
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"espeak failed: {e}")
        except FileNotFoundError:
            self.logger.error("espeak not found - install with: sudo apt install espeak")
        except Exception as e:
            self.logger.error(f"Error in espeak fallback: {e}")
    
    def say(self, text: str, priority: str = 'normal', blocking: bool = False):
        """
        Queue text for speech synthesis
        
        Args:
            text: Text to speak
            priority: Priority level ('high', 'normal', 'low')
            blocking: Wait for speech to complete
        """
        if not text.strip():
            return
        
        # Add personality to the text
        personalized_text = self._personalize_text(text)
        
        speech_request = {
            'text': personalized_text,
            'priority': priority,
            'timestamp': time.time()
        }
        
        try:
            if priority == 'high':
                # For high priority, clear queue and speak immediately
                self._clear_queue()
            
            self.speech_queue.put(speech_request)
            
            if blocking:
                self.speech_queue.join()
                
            self.logger.debug(f"Queued speech: {text[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Error queuing speech: {e}")
    
    def _personalize_text(self, text: str) -> str:
        """Add personality to speech text"""
        if not self.personality['friendly']:
            return text
        
        # Add friendly greetings and personality
        personalized = text
        
        # Add encouraging words for plant care
        if any(word in text.lower() for word in ['water', 'watering', 'plant', 'garden']):
            if self.personality['encouraging']:
                encouraging_phrases = [
                    "Great! ",
                    "Wonderful! ",
                    "Perfect! ",
                    "Excellent! "
                ]
                import random
                if random.random() < 0.3:  # 30% chance to add encouragement
                    personalized = random.choice(encouraging_phrases) + personalized
        
        return personalized
    
    def _clear_queue(self):
        """Clear the speech queue"""
        try:
            while not self.speech_queue.empty():
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
        except queue.Empty:
            pass
    
    def announce_startup(self):
        """Announce that the robot is starting up"""
        startup_message = f"Hello! I'm your {self.personality['name']}, and I'm ready to help care for your garden!"
        self.say(startup_message, priority='high')
    
    def announce_plant_status(self, plant_id: str, moisture_level: float, needs_water: bool):
        """Announce plant status"""
        if needs_water:
            message = f"Plant {plant_id} needs attention. Soil moisture is {moisture_level:.1f} percent. I'll water it now."
        else:
            message = f"Plant {plant_id} is doing well with {moisture_level:.1f} percent soil moisture."
        
        self.say(message)
    
    def announce_watering_start(self, plant_id: str, duration: float):
        """Announce start of watering"""
        message = f"Starting to water plant {plant_id} for {duration:.0f} seconds."
        self.say(message)
    
    def announce_watering_complete(self, plant_id: str, amount: float):
        """Announce watering completion"""
        message = f"Finished watering plant {plant_id}. Dispensed {amount:.2f} liters."
        self.say(message)
    
    def announce_movement(self, action: str):
        """Announce robot movement"""
        movement_messages = {
            'forward': "Moving forward to the next plant.",
            'backward': "Moving backward.",
            'left': "Turning left.",
            'right': "Turning right.",
            'stop': "Stopping movement.",
            'arrived': "I've arrived at the destination."
        }
        
        message = movement_messages.get(action, f"Performing movement: {action}")
        self.say(message, priority='low')
    
    def announce_error(self, error_type: str, details: str = ""):
        """Announce errors or problems"""
        error_messages = {
            'water_low': "Warning: Water tank is running low. Please refill soon.",
            'sensor_error': "I'm having trouble reading a sensor. Please check connections.",
            'motor_error': "There's a problem with my movement system.",
            'emergency_stop': "Emergency stop activated. All systems halted for safety."
        }
        
        base_message = error_messages.get(error_type, f"Error detected: {error_type}")
        if details:
            message = f"{base_message} {details}"
        else:
            message = base_message
        
        self.say(message, priority='high')
    
    def announce_daily_summary(self, plants_watered: int, total_water_used: float):
        """Announce daily garden care summary"""
        message = f"Daily garden care complete! I watered {plants_watered} plants using {total_water_used:.2f} liters of water. All plants are happy and healthy!"
        self.say(message)
    
    def play_sound_effect(self, sound_file: str):
        """Play a sound effect file"""
        if not self.audio_initialized:
            return
        
        try:
            if os.path.exists(sound_file):
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                self.logger.debug(f"Playing sound: {sound_file}")
            else:
                self.logger.warning(f"Sound file not found: {sound_file}")
        except Exception as e:
            self.logger.error(f"Error playing sound: {e}")
    
    def set_personality(self, **kwargs):
        """Update personality settings"""
        self.personality.update(kwargs)
        self.logger.info(f"Personality updated: {self.personality}")
    
    def get_status(self) -> Dict:
        """Get speech system status"""
        return {
            'tts_available': self.tts_available,
            'audio_initialized': self.audio_initialized,
            'speech_active': self.speech_active,
            'queue_size': self.speech_queue.qsize(),
            'personality': self.personality.copy()
        }


def main():
    """Test speech system"""
    logging.basicConfig(level=logging.INFO)
    
    speech = SpeechSystem()
    speech.start_speech_service()
    
    try:
        print("Testing speech system...")
        
        # Test various announcements
        speech.announce_startup()
        time.sleep(2)
        
        speech.announce_plant_status("Plant 1", 25.5, True)
        time.sleep(1)
        
        speech.announce_watering_start("Plant 1", 15)
        time.sleep(1)
        
        speech.say("This is a test of the speech system. How do I sound?")
        time.sleep(3)
        
        speech.announce_watering_complete("Plant 1", 0.35)
        time.sleep(1)
        
        speech.announce_daily_summary(3, 1.2)
        
        # Wait for speech to complete
        time.sleep(5)
        
        print("Speech system test complete!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        speech.stop_speech_service()


if __name__ == "__main__":
    main()