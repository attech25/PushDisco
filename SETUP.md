# PushDisco Setup Guide

A Python script for Raspberry Pi that listens for push button input, plays MP3 audio, and controls a relay.

## Hardware Requirements

- Raspberry Pi (original or newer)
- Push button switch
- Electric relay module (or relay with transistor driver)
- 3.5mm audio jack with speaker
- Jumper wires
- Resistor (10kΩ) for the button pull-down (optional, Pi has internal pull-up)

## GPIO Pin Configuration

Default configuration (customize in the script variables):
- **Button Input**: GPIO 17 (Pin 11)
- **Relay Output**: GPIO 27 (Pin 13)

### Wiring Diagram

```
Push Button:
  - One side to GPIO 17
  - Other side to GND

Relay:
  - GPIO 27 → Relay input/signal pin
  - GND → Relay GND

Audio:
  - 3.5mm jack connected to RPi audio output
```

## Installation

1. **Install dependencies on Raspberry Pi**:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-gpiozero python3-pygame
   sudo pip install -r requirements.txt
   ```

2. **Prepare audio file**:
   - Place your MP3 file in the same directory as the script
   - Default filename: `audio.mp3`
   - You can change the filename in the script by modifying `AUDIO_FILE`

3. **Make the script executable**:
   ```bash
   chmod +x push_disco.py
   ```

## Configuration

Edit the configuration variables at the top of `push_disco.py`:

```python
BUTTON_PIN = 17          # GPIO pin for push button
RELAY_PIN = 27           # GPIO pin for relay
RELAY_DURATION = 15      # Relay active time in seconds
AUDIO_FILE = "audio.mp3" # Path to MP3 file
VOLUME = 0.8             # Volume level (0.0-1.0)
```

## Usage

### Run the script
```bash
sudo python3 push_disco.py
```

The script requires `sudo` because it needs to access GPIO pins.

### How it works

1. Script starts and listens for button presses on GPIO 17
2. When button is pressed:
   - Relay on GPIO 27 activates (HIGH)
   - MP3 audio file begins playing through 3.5mm jack
   - Relay stays active for 15 seconds
   - Script waits for audio to finish playing
   - Relay deactivates (LOW)
3. Script is ready to handle the next button press
4. Press `Ctrl+C` to exit

## Running as a Service (Optional)

To run on startup, create a systemd service file:

1. **Create service file** (`/etc/systemd/system/pushdisco.service`):
   ```ini
   [Unit]
   Description=PushDisco Audio and Relay Controller
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/path/to/PushDisco
   ExecStart=/usr/bin/python3 /path/to/PushDisco/push_disco.py
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start the service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable pushdisco
   sudo systemctl start pushdisco
   ```

3. **Monitor the service**:
   ```bash
   sudo systemctl status pushdisco
   sudo journalctl -u pushdisco -f
   ```

## Troubleshooting

### Button not responding
- Check GPIO pin configuration matches your wiring
- Verify button is wired correctly with proper pull-up/down
- Test GPIO with `gpio readall` command

### No audio output
- Check 3.5mm jack is properly connected
- Verify MP3 file exists in the correct path
- Check audio file format is supported by pygame
- Test audio with: `pygame mixer` or `aplay audio.mp3`

### Relay not working
- Check relay module wiring and power supply
- Verify GPIO pin number matches relay connection
- Test relay with simple GPIO script first
- Check if relay needs pull-up/pull-down resistor

### Permission denied
- Script requires `sudo` to access GPIO
- Make sure to run with: `sudo python3 push_disco.py`

## Features

- **Debounced button input**: Prevents false triggers from button bounce
- **Non-blocking operation**: Uses threading to avoid freezing
- **Error handling**: Graceful error messages and cleanup
- **Resource cleanup**: Properly releases GPIO and audio resources on exit
- **Extensible design**: Easy to modify for different pins or behaviors
