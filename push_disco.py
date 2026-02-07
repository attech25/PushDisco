#!/usr/bin/env python3
"""
PushDisco - Raspberry Pi Push Button Audio and Relay Controller
Listens for push button input, plays an MP3 file, and activates a relay.
"""

import time
import threading
import subprocess
import shutil
from pathlib import Path

# Try gpiozero (preferred on modern Raspberry Pi OS) and fall back to RPi.GPIO
try:
    from gpiozero import Button, OutputDevice
    GPIO_BACKEND = "gpiozero"
except Exception:
    try:
        import RPi.GPIO as GPIO
        GPIO_BACKEND = "RPi.GPIO"
    except Exception:
        GPIO_BACKEND = None

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
        
        # Initialize GPIO using preferred backend
        if GPIO_BACKEND == "gpiozero":
            self.button = Button(self.button_pin, pull_up=True)
            self.relay = OutputDevice(self.relay_pin, active_high=True, initial_value=False)
            # gpiozero has its own debounce; use when_pressed to trigger
            self.button.when_pressed = self.on_button_press

        elif GPIO_BACKEND == "RPi.GPIO":
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.relay_pin, GPIO.OUT, initial=GPIO.LOW)
            GPIO.add_event_detect(
                self.button_pin,
                GPIO.FALLING,
                callback=self.on_button_press,
                bouncetime=int(DEBOUNCE_DELAY * 1000)
            )
        else:
            raise RuntimeError("No GPIO backend available. Install gpiozero or run on Raspberry Pi.")
    
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
        """Handle button press: play audio and activate relay simultaneously."""
        if self.is_playing:
            print("Already playing audio, ignoring button press")
            return
        
        self.is_playing = True
        
        try:
            # Run relay and audio in parallel threads
            relay_thread = threading.Thread(target=self.activate_relay)
            audio_thread = threading.Thread(target=self.play_audio)
            
            relay_thread.daemon = True
            audio_thread.daemon = True
            
            relay_thread.start()
            audio_thread.start()
            
            # Wait for both to complete
            relay_thread.join()
            audio_thread.join()
            
        except Exception as e:
            print(f"Error handling button press: {e}")
        finally:
            self.is_playing = False
    
    def activate_relay(self):
        """Activate relay for the specified duration."""
        print(f"Activating relay for {self.relay_duration} seconds...")
        # Turn relay ON
        if GPIO_BACKEND == "gpiozero":
            self.relay.on()
        else:
            GPIO.output(self.relay_pin, GPIO.HIGH)

        # Wait for specified duration
        time.sleep(self.relay_duration)

        # Turn relay OFF
        if GPIO_BACKEND == "gpiozero":
            self.relay.off()
        else:
            GPIO.output(self.relay_pin, GPIO.LOW)

        print("Relay deactivated")
    
    def play_audio(self):
        """Play the audio file."""
        audio_path = Path(self.audio_file)
        
        if not audio_path.exists():
            print(f"Error: Audio file not found at {self.audio_file}")
            return
        
        print(f"Playing audio: {self.audio_file}")

        # Prefer system audio players for reliability on Raspberry Pi 5
        player = None
        if shutil.which('mpg123'):
            player = ['mpg123', '-q', str(audio_path)]
        elif shutil.which('ffplay'):
            player = ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', str(audio_path)]
        elif shutil.which('aplay') and audio_path.suffix.lower() in ['.wav', '.wave']:
            player = ['aplay', str(audio_path)]
        else:
            print("No supported audio player found (mpg123/ffplay/aplay). Install mpg123 or ffmpeg.")

        if player:
            try:
                subprocess.run(player, check=True)
                print("Audio playback completed")
            except subprocess.CalledProcessError as e:
                print(f"Error during audio playback: {e}")
    
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
        """Clean up GPIO resources."""
        print("Cleaning up resources...")
        # Turn off relay if it's on / release resources depending on backend
        try:
            if GPIO_BACKEND == "gpiozero":
                try:
                    self.relay.off()
                except Exception:
                    pass
            elif GPIO_BACKEND == "RPi.GPIO":
                try:
                    GPIO.output(self.relay_pin, GPIO.LOW)
                except Exception:
                    pass
                try:
                    GPIO.cleanup()
                except Exception:
                    pass
        except Exception:
            pass

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
