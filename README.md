# PushDisco
Push a button to trigger 15 seconds of disco fun!

## Raspberry Pi 5 — Setup Notes

- Install recommended packages:

	```bash
	sudo apt update
	sudo apt install -y mpg123 ffmpeg python3-gpiozero
	python3 -m pip install --user -r requirements.txt
	```

- Ensure the Pi's audio output is configured (HDMI or 3.5mm) and works.

- Connect the button to the `BUTTON_PIN` (default GPIO 17) with a pull-up to 3.3V and the relay module to `RELAY_PIN` (default GPIO 27). Use a proper transistor/optocoupler-backed relay board.

## Simulated Dry-Run (no hardware)

To run a simulated test on a workstation or on the Pi without wiring or audio players, run:

```bash
python3 simulate_run.py
```

This script uses an internal simulation mode (no GPIO lib required) and skips real audio playback.
