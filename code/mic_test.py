# =====================================================
# mic_test.py — Project Sparkle
# Tests your USB microphone and checks volume levels
#
# HOW TO RUN (no sudo needed for mic):
#   python3 mic_test.py
#
# First, install required library:
#   pip3 install pyaudio numpy --break-system-packages
#
# WHAT IT DOES:
#   - Finds your USB microphone automatically
#   - Shows a live volume bar in the terminal
#   - Prints TRIGGERED when volume goes above your threshold
#   - Helps you find the right threshold for clapping/cheering
# =====================================================

import pyaudio
import numpy as np
import time

# ============ CONFIG ============
SAMPLE_RATE       = 44100   # Standard audio quality (don't change this)
CHUNK             = 1024    # How many audio samples to grab at once
VOLUME_THRESHOLD  = 2000    # Volume level that counts as a "trigger"
                            # ↑ Start here, then adjust:
                            #   Too sensitive? Raise to 3000 or 4000
                            #   Not triggering? Lower to 1000 or 1500
# ================================


# ---- Find the USB microphone ----
p = pyaudio.PyAudio()

print("========================================")
print("  PROJECT SPARKLE — MIC TEST")
print("========================================")
print()
print("Scanning for audio input devices...")
print()

mic_index = None
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"  [{i}] {info['name']}")
        # Prefer anything with 'usb' or 'mic' in the name
        name_lower = info['name'].lower()
        if 'usb' in name_lower or 'mic' in name_lower:
            mic_index = i
        elif mic_index is None:
            mic_index = i   # Fall back to first input found

print()
if mic_index is None:
    print("ERROR: No microphone found!")
    print("Check your USB mic is plugged in and try: arecord -l")
    p.terminate()
    exit()

selected = p.get_device_info_by_index(mic_index)
print(f"Using: [{mic_index}] {selected['name']}")
print(f"Trigger threshold: {VOLUME_THRESHOLD}")
print()
print("Make noise to test — clap, speak, cheer!")
print("Press Ctrl+C to stop.")
print()
print(f"{'Volume bar':<52} Level")
print("-" * 62)


# ---- Open the audio stream ----
try:
    stream = p.open(
        format=pyaudio.paInt16,       # 16-bit audio (standard quality)
        channels=1,                    # Mono (one channel, fine for mic)
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=mic_index,
        frames_per_buffer=CHUNK
    )
except Exception as e:
    print(f"ERROR opening microphone: {e}")
    print("Try running: arecord -l   to check your mic is detected.")
    p.terminate()
    exit()


# ---- Listen loop ----
trigger_count = 0

try:
    while True:
        # Read a chunk of audio
        data = stream.read(CHUNK, exception_on_overflow=False)

        # Convert raw bytes into numbers we can work with
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Calculate average volume (how loud is it right now?)
        volume = int(np.abs(audio_data).mean())

        # Build a visual bar (max 50 characters wide)
        bar_length = min(int(volume / 120), 50)
        bar = '█' * bar_length
        spaces = ' ' * (50 - bar_length)

        if volume > VOLUME_THRESHOLD:
            trigger_count += 1
            # Print TRIGGERED on its own line so it's easy to spot
            print(f"|{bar}{spaces}| {volume:5d}  ← TRIGGERED! (#{trigger_count})")
        else:
            # Overwrite the same line (end='\r') so terminal stays clean
            print(f"|{bar}{spaces}| {volume:5d}", end='\r')

        time.sleep(0.02)   # Small pause (50 checks per second)

except KeyboardInterrupt:
    print()
    print()
    print("========================================")
    print("  MIC TEST COMPLETE!")
    print(f"  Total triggers: {trigger_count}")
    print()
    print("  NEXT STEPS:")
    print(f"  If triggering too easily: increase")
    print(f"  VOLUME_THRESHOLD above {VOLUME_THRESHOLD}")
    print(f"  If not triggering: decrease it.")
    print("========================================")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
