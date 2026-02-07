#!/usr/bin/env python3
"""
Generate a 15-second disco-themed MP3 file
"""

import numpy as np
import subprocess
import struct
import wave
import os
from pathlib import Path

def generate_disco_audio(duration=15, bpm=120, output_file="audio.wav"):
    """
    Generate disco-themed audio with beat and melody.
    
    Args:
        duration: Duration in seconds
        bpm: Beats per minute (disco typically 120)
        output_file: Output WAV file path
    """
    # Audio parameters
    sample_rate = 44100  # 44.1 kHz
    num_samples = int(sample_rate * duration)
    
    # Time array
    t = np.arange(num_samples) / sample_rate
    
    # Calculate beat timing
    beat_duration = 60 / bpm  # Duration of one beat in seconds
    
    # Initialize audio signal
    audio = np.zeros(num_samples)
    
    # 1. Kick drum (bass) - 4 on the floor pattern (120 BPM = 2 beats per second)
    kick_freq = 60  # Hz
    for i in range(0, duration * 4):  # 4 beats per second at 120 BPM
        beat_start = int(i * sample_rate * beat_duration)
        beat_end = int(beat_start + sample_rate * 0.15)  # 150ms kick
        if beat_end < num_samples:
            kick_phase = 2 * np.pi * kick_freq * (t[beat_start:beat_end] - t[beat_start])
            kick_envelope = np.exp(-2 * (t[beat_start:beat_end] - t[beat_start]) / 0.15)
            audio[beat_start:beat_end] += 0.3 * np.sin(kick_phase) * kick_envelope
    
    # 2. Hi-hat closed (snare pattern) - on 2 and 4
    hihat_freq = 150  # Hz
    for i in range(0, duration * 2):  # 2 hits per second (on 2 and 4)
        beat_start = int((i * 2 + 1) * sample_rate * beat_duration)
        beat_end = int(beat_start + sample_rate * 0.1)  # 100ms hihat
        if beat_end < num_samples:
            hihat_noise = np.random.normal(0, 0.1, beat_end - beat_start)
            hihat_phase = 2 * np.pi * hihat_freq * (t[beat_start:beat_end] - t[beat_start])
            hihat_envelope = np.exp(-5 * (t[beat_start:beat_end] - t[beat_start]) / 0.1)
            audio[beat_start:beat_end] += (np.sin(hihat_phase) * 0.15 + hihat_noise * 0.2) * hihat_envelope
    
    # 3. Disco melody - simple synth line
    # Create a disco-style ascending note pattern
    melody_notes = [
        (262, 0.25),   # C (middle C)
        (294, 0.25),   # D
        (330, 0.25),   # E
        (349, 0.25),   # F
        (392, 0.5),    # G (longer)
        (440, 0.25),   # A
        (494, 0.25),   # B
        (523, 0.5),    # C (higher)
    ]
    
    # Repeat melody pattern to fill duration
    current_time = 0
    pattern_duration = sum([duration for _, duration in melody_notes])
    
    while current_time < duration:
        for freq, note_duration in melody_notes:
            if current_time >= duration:
                break
            
            note_start = int(current_time * sample_rate)
            note_end = int((current_time + note_duration) * sample_rate)
            note_end = min(note_end, num_samples)
            
            if note_start < num_samples:
                # Create synth note with envelope
                note_t = t[note_start:note_end] - t[note_start]
                phase = 2 * np.pi * freq * note_t
                
                # ADSR envelope
                attack_time = 0.05
                decay_time = 0.1
                sustain_level = 0.7
                release_time = 0.1
                
                envelope = np.ones(len(note_t))
                
                # Attack
                attack_samples = int(attack_time * sample_rate)
                envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
                
                # Decay and sustain
                sustain_start = int((attack_time + decay_time) * sample_rate)
                envelope[attack_samples:sustain_start] = np.linspace(1, sustain_level, sustain_start - attack_samples)
                envelope[sustain_start:] = sustain_level
                
                # Release
                release_start = int((note_duration - release_time) * sample_rate)
                if release_start < len(envelope):
                    envelope[release_start:] = np.linspace(sustain_level, 0, len(envelope) - release_start)
                
                # Mix synth (triangle wave for brightness)
                synth = np.sin(phase) * 0.25 * envelope
                audio[note_start:note_end] += synth
            
            current_time += note_duration
    
    # 4. Add bass line (lower register)
    bass_notes = [
        (110, 0.5),   # A2
        (123, 0.5),   # B2
        (147, 1.0),   # D3
        (165, 0.5),   # E3
    ]
    
    current_time = 0
    while current_time < duration:
        for freq, note_duration in bass_notes:
            if current_time >= duration:
                break
            
            note_start = int(current_time * sample_rate)
            note_end = int((current_time + note_duration) * sample_rate)
            note_end = min(note_end, num_samples)
            
            if note_start < num_samples:
                note_t = t[note_start:note_end] - t[note_start]
                phase = 2 * np.pi * freq * note_t
                bass = np.sin(phase) * 0.15
                audio[note_start:note_end] += bass
            
            current_time += note_duration
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.95
    
    # Convert to 16-bit PCM
    audio_int16 = np.int16(audio * 32767)
    
    # Write WAV file
    with wave.open(output_file, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)   # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
    
    print(f"WAV file generated: {output_file}")
    return output_file


def convert_wav_to_mp3(wav_file, mp3_file):
    """
    Convert WAV file to MP3 using ffmpeg.
    
    Args:
        wav_file: Input WAV file path
        mp3_file: Output MP3 file path
    """
    try:
        # Try using ffmpeg
        result = subprocess.run(
            [
                'ffmpeg',
                '-i', wav_file,
                '-q:a', '9',  # Quality (lower number = better quality)
                '-y',  # Overwrite output
                mp3_file
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"MP3 file generated: {mp3_file}")
            return mp3_file
        else:
            print(f"Error converting WAV to MP3: {result.stderr}")
            print(f"Using WAV file instead: {wav_file}")
            return wav_file
    
    except FileNotFoundError:
        print("ffmpeg not found. Install with: sudo apt-get install ffmpeg")
        print(f"Using WAV file instead: {wav_file}")
        return wav_file
    except Exception as e:
        print(f"Error during conversion: {e}")
        print(f"Using WAV file instead: {wav_file}")
        return wav_file


def main():
    """Generate disco audio file."""
    print("Generating 15-second disco music...")
    
    # Generate WAV file
    wav_file = generate_disco_audio(duration=15, bpm=120, output_file="audio.wav")
    
    # Try to convert to MP3
    mp3_file = convert_wav_to_mp3(wav_file, "audio.mp3")
    
    # Verify output
    if Path(mp3_file).exists():
        file_size = Path(mp3_file).stat().st_size
        print(f"✓ Successfully created {mp3_file} ({file_size} bytes)")
    elif Path(wav_file).exists():
        file_size = Path(wav_file).stat().st_size
        print(f"✓ Successfully created {wav_file} ({file_size} bytes)")
    else:
        print("✗ Failed to create audio file")


if __name__ == "__main__":
    main()
