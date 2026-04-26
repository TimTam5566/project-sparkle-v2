# =====================================================
# sparkle.py — Project Sparkle V2
# Full dress program — April 2026 Showcase
#
# HOW TO RUN:
#   sudo python3 ~/project-sparkle/sparkle.py
# =====================================================

import time
import board
import neopixel
import RPi.GPIO as GPIO
import threading
import random

# ============================================================
# CONFIG
# ============================================================

STRIP_LEDS      = 300
STRIP_PIN       = board.D18

RINGS           = [60, 24, 48, 12, 40, 12, 32, 12, 12, 12, 12]
RINGS_LEDS      = sum(RINGS)         # = 276
RINGS_PIN       = board.D13

USE_MATRIX      = True               # Set False to disable matrix
MATRIX_LEDS     = 256                # 8 rows x 32 cols
MATRIX_PIN      = board.D10

USE_DISTANCE    = False              # Set True to enable distance sensor
TRIG_PIN        = 23
ECHO_PIN        = 24
CLOSE_CM        = 50

USE_MIC         = False              # Set True when mic is plugged in
MIC_THRESHOLD   = 3000

BRIGHTNESS      = 0.3               # 40% for showcase

# Dress colours
ORANGE          = (255, 80, 0)
PURPLE          = (100, 0, 180)
WHITE           = (255, 255, 255)
BLACK           = (0, 0, 0)

# Clap/cheer reaction — one of these chosen randomly per trigger
REACTION_COLOURS = [
    (255, 20, 147),   # Hot pink
    (0, 150, 255),    # Electric blue
    (0, 220, 80),     # Bright green
]

# Matrix dimensions
MATRIX_ROWS = 8
MATRIX_COLS = 32

# ">_" pixel art — She Codes logo
# 8 rows x 11 columns
TEXT_BITMAP = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # row 0
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # row 1
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # row 2
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],  # row 3  ← tip of arrow
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # row 4
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # row 5
    [1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],  # row 6  ← base of > and _ underline
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # row 7
]
TEXT_WIDTH = 11

# ============================================================

clap_detected   = False
person_detected = False

# ---- Set up LEDs ----
print("Setting up LEDs...")

strip = neopixel.NeoPixel(STRIP_PIN, STRIP_LEDS, brightness=BRIGHTNESS, auto_write=False)
rings = neopixel.NeoPixel(RINGS_PIN, RINGS_LEDS, brightness=BRIGHTNESS, auto_write=False)

try:
    matrix = neopixel.NeoPixel(MATRIX_PIN, MATRIX_LEDS, brightness=BRIGHTNESS, auto_write=False) if USE_MATRIX else None
except Exception as e:
    print(f"Matrix setup failed: {e} — matrix disabled")
    matrix = None


# ---- Helpers ----

def show_leds():
    strip.show()
    rings.show()

def fill_all(colour):
    strip.fill(colour)
    rings.fill(colour)
    show_leds()

def clear_all():
    fill_all(BLACK)


# ---- Matrix ----

def matrix_pixel_index(row, col):
    """
    Convert logical (row, col) to physical LED index.
    Physical layout: data enters bottom-right, snakes left column by column.
    led_col 0 = rightmost physical column, goes bottom-to-top.
    led_col 1 = second from right, goes top-to-bottom. (Serpentine)
    """
    if 0 <= row < MATRIX_ROWS and 0 <= col < MATRIX_COLS:
        led_col = MATRIX_COLS - 1 - col
        if led_col % 2 == 0:
            return led_col * MATRIX_ROWS + (MATRIX_ROWS - 1 - row)
        else:
            return led_col * MATRIX_ROWS + row
    return None

def draw_matrix_frame(scroll_offset, colour=ORANGE):
    """
    Draw one frame of the scrolling >_ logo on a purple background.
    scroll_offset starts at -TEXT_WIDTH (off left) and increases to MATRIX_COLS (off right).
    """
    if not matrix:
        return
    try:
        matrix.fill(PURPLE)
        for row in range(MATRIX_ROWS):
            for col in range(MATRIX_COLS):
                text_col = col - scroll_offset
                if 0 <= text_col < TEXT_WIDTH:
                    if TEXT_BITMAP[row][text_col]:
                        idx = matrix_pixel_index(row, col)
                        if idx is not None and idx < MATRIX_LEDS:
                            matrix[idx] = colour
        matrix.show()
    except Exception as e:
        print(f"Matrix error: {e}")


# ---- Distance sensor ----

if USE_DISTANCE:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)

def get_distance_cm():
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
    timeout = time.time() + 0.1
    start   = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        start = time.time()
        if time.time() > timeout:
            return 999
    stop = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        stop = time.time()
        if time.time() > timeout:
            return 999
    elapsed  = stop - start
    distance = (elapsed * 34300) / 2
    return distance

def monitor_distance():
    global person_detected
    while True:
        try:
            dist = get_distance_cm()
            if dist < CLOSE_CM:
                person_detected = True
        except Exception:
            pass
        time.sleep(0.1)


# ---- Microphone ----

def monitor_mic():
    global clap_detected
    try:
        import pyaudio
        import numpy as np
    except ImportError:
        print("pyaudio not installed — run: pip3 install pyaudio numpy --break-system-packages")
        return
    p = pyaudio.PyAudio()
    mic_index = None
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            name = info['name'].lower()
            if 'usb' in name or 'mic' in name:
                mic_index = i
                break
            elif mic_index is None:
                mic_index = i
    if mic_index is None:
        print("No microphone found")
        p.terminate()
        return
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100,
                    input=True, input_device_index=mic_index, frames_per_buffer=1024)
    while True:
        data   = stream.read(1024, exception_on_overflow=False)
        audio  = np.frombuffer(data, dtype=np.int16)
        volume = int(np.abs(audio).mean())
        if volume > MIC_THRESHOLD:
            clap_detected = True
        time.sleep(0.02)


# ---- Animations ----

def chase_frame(pixels, num_leds, offset):
    """
    Orange and purple bands that scroll along — like a barber pole.
    """
    band_size = 15
    for i in range(num_leds):
        pos_in_cycle = (i + offset) % (band_size * 2)
        if pos_in_cycle < band_size:
            pixels[i] = ORANGE
        else:
            pixels[i] = PURPLE


def colour_flash_reaction():
    """
    Clap/cheer trigger:
    Strip flashes one randomly chosen bold colour (pink, blue or green).
    Rings flash bright WHITE at reduced brightness (0.2) — 3 times.
    """
    colour = random.choice(REACTION_COLOURS)
    print(f"  Flashing {colour}")
    rings.brightness = 0.2
    for _ in range(3):
        strip.fill(colour)
        rings.fill(WHITE)
        show_leds()
        time.sleep(0.2)
        strip.fill(BLACK)
        rings.fill(BLACK)
        show_leds()
        time.sleep(0.15)
    rings.brightness = BRIGHTNESS


def distance_flash_reaction():
    """
    Distance sensor trigger:
    Strip and rings cycle through purple, orange and white quickly.
    """
    flash_colours = [PURPLE, ORANGE, WHITE]
    for _ in range(4):
        for colour in flash_colours:
            strip.fill(colour)
            rings.fill(colour)
            show_leds()
            time.sleep(0.12)
    strip.fill(BLACK)
    rings.fill(BLACK)
    show_leds()
    time.sleep(0.2)


# ---- Main program ----

def main():
    global clap_detected, person_detected

    print("=" * 40)
    print("  PROJECT SPARKLE V2 — STARTING UP")
    print(f"  Strip:  {STRIP_LEDS} LEDs")
    print(f"  Rings:  {RINGS_LEDS} LEDs ({len(RINGS)} rings)")
    print(f"  Matrix: {'ON' if matrix else 'OFF'}")
    print(f"  Brightness: {int(BRIGHTNESS * 100)}%")
    print("=" * 40)

    if USE_MIC:
        threading.Thread(target=monitor_mic, daemon=True).start()
        print("Mic monitoring on")
    if USE_DISTANCE:
        threading.Thread(target=monitor_distance, daemon=True).start()
        print("Distance sensor on")

    print("Running! Press Ctrl+C to stop.")

    offset         = 0
    frame          = 0
    matrix_offset  = -TEXT_WIDTH     # Start text off left edge of matrix
    matrix_colour  = ORANGE

    try:
        while True:

            # --- Clap/cheer reaction ---
            if clap_detected:
                clap_detected = False
                print("CLAP DETECTED!")
                colour_flash_reaction()
                offset = 0
                continue

            # --- Distance reaction ---
            if person_detected:
                person_detected = False
                print("PERSON DETECTED!")
                distance_flash_reaction()
                offset = 0
                continue

            # --- Default: orange + purple chase on strip and rings ---
            chase_frame(strip, STRIP_LEDS, offset)
            chase_frame(rings, RINGS_LEDS, offset)
            show_leds()

            # --- Matrix: scroll >_ logo left to right, update every 5 frames ---
            if matrix:
                if frame % 5 == 0:
                    draw_matrix_frame(matrix_offset, colour=matrix_colour)
                    matrix_offset += 1
                    if matrix_offset > MATRIX_COLS:
                        matrix_offset = -TEXT_WIDTH

            offset += 1
            frame  += 1
            time.sleep(0.04)

    except KeyboardInterrupt:
        print("\nShutting down Project Sparkle...")
        clear_all()
        if matrix:
            try:
                matrix.fill(BLACK)
                matrix.show()
            except Exception:
                pass
        if USE_DISTANCE:
            GPIO.cleanup()
        print("All LEDs off. Goodbye! ✨")


if __name__ == "__main__":
    main()
