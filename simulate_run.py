#!/usr/bin/env python3
"""Simulated dry-run for PushDisco without GPIO or audio players.

This script sets PUSH_DISCO_SIMULATE=1 before importing `push_disco` so that
no real GPIO library is required. It also monkeypatches `play_audio` to avoid
calling external system audio players during the dry-run.
"""
import os
os.environ['PUSH_DISCO_SIMULATE'] = '1'

import push_disco
from push_disco import PushDiscoController, BUTTON_PIN, RELAY_PIN, AUDIO_FILE

print(f"[SIM] env PUSH_DISCO_SIMULATE={os.environ.get('PUSH_DISCO_SIMULATE')}")
print(f"[SIM] push_disco.GPIO_BACKEND={getattr(push_disco, 'GPIO_BACKEND', None)}")

# Monkeypatch audio playback to avoid external dependencies during simulation
def _fake_play_audio(self):
    print(f"[SIM] Pretend to play: {self.audio_file}")

PushDiscoController.play_audio = _fake_play_audio

if __name__ == '__main__':
    controller = PushDiscoController(
        button_pin=BUTTON_PIN,
        relay_pin=RELAY_PIN,
        audio_file=AUDIO_FILE,
        relay_duration=1,
    )

    print("Running simulated button press (dry-run)...")
    controller.handle_button_press()

    print("Simulated run complete; cleaning up...")
    controller.cleanup()
