#!/usr/bin/env python3
"""
PushDisco - Raspberry Pi Push Button Audio and Relay Controller
Listens for push button input, plays an MP3 file, and activates a relay.
"""

import RPi.GPIO as GPIO
import pygame
import time
import threading
from pathlib import Path

# GPIO Configuration
BUTTON_PIN = 17          # GPIO pin for push button input
RELAY_PIN = 27           # GPIO pin for relay output
RELAY_DURATION = 15      # Relay activation duration in seconds
DEBOUNCE_DELAY = 0.2     # Debounce delay in seconds

# Audio Configuration
AUDIO_FILE = "audio.mp3"  # Path to MP3 file to play
VOLUME = 0.8              # Volume level (0.0 to 1.0)


class PushDiscoController:
    """Controller for push button audio and relay activation."""
    
    def __init__(self, button_pin, relay_pin, audio_file, relay_duration=15):
        """
        Initialize the PushDisco controller.
        
        Args:
            button_pin: GPIO pin number for the button
            relay_pin: GPIO pin number for the relay
            audio_file: Path to the MP3 file to play
            relay_duration: Duration to keep relay activated in seconds
        """
        self.button_pin = button_pin
        self.relay_pin = relay_pin
        self.audio_file = audio_file
        self.relay_duration = relay_duration
        self.last_button_press = 0
        self.is_playing = False
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.relay_pin, GPIO.OUT, initial=GPIO.LOW)
        
        # Set up button event detection
        GPIO.add_event_detect(
            self.button_pin,
            GPIO.FALLING,
            callback=self.on_button_press,
            bouncetime=int(DEBOUNCE_DELAY * 1000)
        )
        
        # Initialize pygame mixer for audio
        pygame.mixer.init()
        pygame.mixer.music.set_volume(VOLUME)
    
    def on_button_press(self, channel):
        """
        Callback function when button is pressed.
        
        Args:
            channel: GPIO channel that triggered the event
        """
        current_time = time.time()
        
        # Additional debouncing check
        if current_time - self.last_button_press < DEBOUNCE_DELAY:
            return
        
        self.last_button_press = current_time
        
        # Run button action in a separate thread to avoid blocking
        thread = threading.Thread(target=self.handle_button_press)
        thread.daemon = True
        thread.start()
    
    def handle_button_press(self):
        """Handle button press: play audio and activate relay."""
        if self.is_playing:
            print("Already playing audio, ignoring button press")
            return
        
        self.is_playing = True
        
        try:
            # Activate relay
            self.activate_relay()
            
            # Play audio file
            self.play_audio()
            
        except Exception as e:
            print(f"Error handling button press: {e}")
        finally:
            self.is_playing = False
    
    def activate_relay(self):
        """Activate relay for the specified duration."""
        print(f"Activating relay for {self.relay_duration} seconds...")
        
        # Turn relay ON
        GPIO.output(self.relay_pin, GPIO.HIGH)
        
        # Wait for specified duration
        time.sleep(self.relay_duration)
        
        # Turn relay OFF
        GPIO.output(self.relay_pin, GPIO.LOW)
        print("Relay deactivated")
    
    def play_audio(self):
        """Play the audio file."""
        audio_path = Path(self.audio_file)
        
        if not audio_path.exists():
            print(f"Error: Audio file not found at {self.audio_file}")
            return
        
        try:
            print(f"Playing audio: {self.audio_file}")
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.play()
            
            # Wait for audio to finish playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            print("Audio playback completed")
        
        except pygame.error as e:
            print(f"Error playing audio: {e}")
    
    def run(self):
        """Start listening for button presses."""
        print("PushDisco started. Listening for button presses...")
        print(f"Button pin: GPIO {self.button_pin}")
        print(f"Relay pin: GPIO {self.relay_pin}")
        print(f"Audio file: {self.audio_file}")
        print("Press Ctrl+C to exit")
        
        try:
            # Keep the program running
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\nShutting down...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up GPIO and pygame resources."""
        print("Cleaning up resources...")
        
        # Stop audio if playing
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        
        # Turn off relay if it's on
        GPIO.output(self.relay_pin, GPIO.LOW)
        
        # Clean up GPIO
        GPIO.cleanup()
        print("Cleanup complete")


def main():
    """Main entry point."""
    # Verify audio file exists
    audio_path = Path(AUDIO_FILE)
    if not audio_path.exists():
        print(f"Error: Audio file '{AUDIO_FILE}' not found")
        print("Please create the file or update AUDIO_FILE path in the script")
        return
    
    # Create and run controller
    controller = PushDiscoController(
        button_pin=BUTTON_PIN,
        relay_pin=RELAY_PIN,
        audio_file=AUDIO_FILE,
        relay_duration=RELAY_DURATION
    )
    
    controller.run()


if __name__ == "__main__":
    main()
