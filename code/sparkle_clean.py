import time
import board
import neopixel
import RPi.GPIO as GPIO
import threading
import random

STRIP_LEDS      = 300
STRIP_PIN       = board.D18
RINGS           = [60, 24, 48, 12, 40, 12, 32, 12, 12, 12, 12]
RINGS_LEDS      = sum(RINGS)
RINGS_PIN       = board.D13
USE_MATRIX      = False
MATRIX_LEDS     = 256
MATRIX_PIN      = board.D10
USE_DISTANCE    = False
TRIG_PIN        = 23
ECHO_PIN        = 24
CLOSE_CM        = 50
USE_MIC         = False
MIC_THRESHOLD   = 3000
BRIGHTNESS      = 0.3
ORANGE          = (255, 80, 0)
PURPLE          = (100, 0, 180)
WHITE           = (255, 255, 255)
BLACK           = (0, 0, 0)
REACTION_COLOURS = [(255, 20, 147), (0, 255, 100), (0, 150, 255)]

clap_detected   = False
person_detected = False

print("Setting up LEDs...")
strip  = neopixel.NeoPixel(STRIP_PIN,  STRIP_LEDS,  brightness=BRIGHTNESS, auto_write=False)
rings  = neopixel.NeoPixel(RINGS_PIN,  RINGS_LEDS,  brightness=BRIGHTNESS, auto_write=False)
matrix = neopixel.NeoPixel(MATRIX_PIN, MATRIX_LEDS, brightness=BRIGHTNESS, auto_write=False) if USE_MATRIX else None

def fill_all(colour):
    strip.fill(colour)
    rings.fill(colour)
    if matrix:
        matrix.fill(colour)
    show_all()

def show_all():
    strip.show()
    rings.show()
    if matrix:
        matrix.show()

def clear_all():
    fill_all(BLACK)

if USE_DISTANCE:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)

def get_distance_cm():
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
    start = time.time()
    stop  = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        start = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        stop = time.time()
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

def monitor_mic():
    global clap_detected
    try:
        import pyaudio
        import numpy as np
    except ImportError:
        print("pyaudio not installed")
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
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index=mic_index, frames_per_buffer=1024)
    while True:
        data   = stream.read(1024, exception_on_overflow=False)
        audio  = np.frombuffer(data, dtype=np.int16)
        volume = int(np.abs(audio).mean())
        if volume > MIC_THRESHOLD:
            clap_detected = True
        time.sleep(0.02)

def chase_frame(pixels, num_leds, offset):
    band_size = 15
    for i in range(num_leds):
        pos_in_cycle = (i + offset) % (band_size * 2)
        if pos_in_cycle < band_size:
            pixels[i] = ORANGE
        else:
            pixels[i] = PURPLE

def white_flash_reaction():
    fill_all(WHITE)
    time.sleep(0.2)
    clear_all()
    time.sleep(0.1)
    fill_all(WHITE)
    time.sleep(0.2)
    clear_all()
    time.sleep(0.1)
    burst_colour = random.choice(REACTION_COLOURS)
    fill_all(burst_colour)
    time.sleep(0.5)
    clear_all()
    time.sleep(0.2)

def distance_flash_reaction():
    flash_colours = [(255, 0, 0), (255, 255, 0), (0, 100, 255)]
    for _ in range(4):
        for colour in flash_colours:
            fill_all(colour)
            time.sleep(0.12)
    clear_all()
    time.sleep(0.2)

def matrix_sparkle():
    if not matrix:
        return
    for _ in range(5):
        led = random.randint(0, MATRIX_LEDS - 1)
        matrix[led] = random.choice([ORANGE, PURPLE, WHITE])
    for _ in range(3):
        led = random.randint(0, MATRIX_LEDS - 1)
        matrix[led] = BLACK
    matrix.show()

def main():
    global clap_detected, person_detected
    print("========================================")
    print("  PROJECT SPARKLE V2 — STARTING UP")
    print(f"  Strip:  {STRIP_LEDS} LEDs")
    print(f"  Rings:  {RINGS_LEDS} LEDs ({len(RINGS)} rings)")
    print(f"  Brightness: {int(BRIGHTNESS * 100)}%")
    print("========================================")
    if USE_MIC:
        threading.Thread(target=monitor_mic, daemon=True).start()
    if USE_DISTANCE:
        threading.Thread(target=monitor_distance, daemon=True).start()
    print("Running! Press Ctrl+C to stop.")
    offset = 0
    try:
        while True:
            if clap_detected:
                clap_detected = False
                print("CLAP DETECTED!")
                white_flash_reaction()
                offset = 0
                continue
            if person_detected:
                person_detected = False
                print("PERSON DETECTED!")
                distance_flash_reaction()
                offset = 0
                continue
            chase_frame(strip, STRIP_LEDS, offset)
            chase_frame(rings, RINGS_LEDS, offset)
            strip.show()
            rings.show()
            if USE_MATRIX:
                matrix_sparkle()
            offset += 1
            time.sleep(0.04)
    except KeyboardInterrupt:
        print("\nShutting down...")
        clear_all()
        if USE_DISTANCE:
            GPIO.cleanup()
        print("All LEDs off. Goodbye!")

if __name__ == "__main__":
    main()
