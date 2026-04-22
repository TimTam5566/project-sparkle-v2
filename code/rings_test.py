# =====================================================
# rings_test.py — Project Sparkle
# Tests your daisy-chained LED rings on GPIO18
#
# HOW TO RUN:
#   sudo python3 rings_test.py
#
# YOUR RINGS (in chain order, first ring = closest to Pi):
#   Ring 1:  60 LEDs
#   Ring 2:  24 LEDs
#   Ring 3:  48 LEDs
#   Ring 4:  12 LEDs
#   Ring 5:  40 LEDs
#   Ring 6:  12 LEDs
#   Ring 7:  32 LEDs
#   Ring 8:  12 LEDs
#   Ring 9:  12 LEDs
#   Ring 10: 12 LEDs
#   Ring 11: 12 LEDs
#   Ring 12:  7 LEDs
#   TOTAL:  283 LEDs
#
# WHAT IT DOES:
#   Test 1 — Flash all rings white (confirms whole chain works)
#   Test 2 — Light each ring one at a time in a different colour
#             Use this to confirm which ring is which on the dress!
#   Test 3 — Purple chase (fills rings one by one)
#   Test 4 — Rainbow sparkle across all rings
# =====================================================

import time
import board
import neopixel

# ============ CONFIG — edit if you change your ring order ============
# List your rings in the ORDER they are connected (first to last in chain)
RINGS = [60, 24, 48, 12, 40, 12, 32, 12, 12, 12, 12, 7]

GPIO_PIN   = board.D18      # GPIO18 = physical Pin 12 on the Pi
BRIGHTNESS = 0.3            # 30% for testing
# =====================================================================

# Automatically work out total LED count
TOTAL_LEDS = sum(RINGS)

# --- Set up the full chain as one long strip ---
pixels = neopixel.NeoPixel(
    GPIO_PIN, TOTAL_LEDS,
    brightness=BRIGHTNESS,
    auto_write=False
)


# ---- Helper functions ----

def get_ring_start(ring_index):
    """
    Works out which LED number a ring starts at.
    Example: Ring 0 starts at LED 0
             Ring 1 starts at LED 60 (after the 60-LED ring)
             Ring 2 starts at LED 84 (after 60 + 24)
    """
    return sum(RINGS[:ring_index])

def light_ring(ring_index, colour):
    """Light up just ONE ring by its position in the chain."""
    start = get_ring_start(ring_index)
    end   = start + RINGS[ring_index]
    for i in range(start, end):
        pixels[i] = colour
    pixels.show()

def clear_all():
    """Turn all LEDs off."""
    pixels.fill((0, 0, 0))
    pixels.show()

def flash_all(colour, times=3):
    """Flash all LEDs on and off."""
    for _ in range(times):
        pixels.fill(colour)
        pixels.show()
        time.sleep(0.4)
        clear_all()
        time.sleep(0.3)

def rainbow_sparkle(duration=8):
    """Random sparkle effect across all rings with rainbow colours."""
    import random
    colours = [
        (255, 0, 0),     # Red
        (255, 80, 0),    # Orange
        (255, 220, 0),   # Yellow
        (0, 255, 0),     # Green
        (0, 100, 255),   # Blue
        (100, 0, 255),   # Indigo
        (200, 0, 255),   # Violet
        (255, 0, 150),   # Pink
    ]
    start_time = time.time()
    while time.time() - start_time < duration:
        # Randomly turn on a few LEDs
        for _ in range(15):
            led = random.randint(0, TOTAL_LEDS - 1)
            pixels[led] = random.choice(colours)
        # Randomly turn off a few LEDs
        for _ in range(10):
            led = random.randint(0, TOTAL_LEDS - 1)
            pixels[led] = (0, 0, 0)
        pixels.show()
        time.sleep(0.05)


# ---- Colours to show each ring during Test 2 ----
# One colour per ring so you can tell them apart easily
RING_COLOURS = [
    (255, 0, 0),      # Ring 1  (60 LEDs)  — Red
    (0, 220, 0),      # Ring 2  (24 LEDs)  — Green
    (0, 80, 255),     # Ring 3  (48 LEDs)  — Blue
    (255, 160, 0),    # Ring 4  (12 LEDs)  — Orange
    (150, 0, 255),    # Ring 5  (40 LEDs)  — Purple
    (255, 255, 0),    # Ring 6  (12 LEDs)  — Yellow
    (0, 220, 220),    # Ring 7  (32 LEDs)  — Cyan
    (255, 0, 200),    # Ring 8  (12 LEDs)  — Pink
    (0, 255, 120),    # Ring 9  (12 LEDs)  — Mint
    (255, 100, 100),  # Ring 10 (12 LEDs)  — Salmon
    (100, 100, 255),  # Ring 11 (12 LEDs)  — Periwinkle
    (255, 220, 100),  # Ring 12  (7 LEDs)  — Gold
]


# ---- Run the tests ----

print("========================================")
print("  PROJECT SPARKLE — RINGS TEST")
print(f"  {len(RINGS)} rings, {TOTAL_LEDS} LEDs total")
print(f"  Ring sizes: {RINGS}")
print(f"  Brightness: {int(BRIGHTNESS * 100)}%")
print("========================================")
print()

# Test 1: Flash all white
print("Test 1: Flashing ALL rings WHITE...")
print("        → All 283 LEDs should light up.")
flash_all((255, 255, 255))
time.sleep(1)

# Test 2: One ring at a time
print()
print("Test 2: Lighting each ring one at a time...")
print("        → Watch which ring on the dress lights up!")
print("        → If a ring doesn't light up, check its DIN/DOUT connections.")
print()

for i, ring_size in enumerate(RINGS):
    clear_all()
    light_ring(i, RING_COLOURS[i])
    start_led = get_ring_start(i)
    print(f"  Ring {i+1:2d}: {ring_size:3d} LEDs  "
          f"(chain positions {start_led}–{start_led + ring_size - 1})"
          f"  — check which ring on the dress is lit!")
    time.sleep(2)   # 2 seconds to look at each ring

clear_all()
time.sleep(0.5)

# Test 3: Purple chase
print()
print("Test 3: Purple chase — filling rings one by one...")
for i in range(len(RINGS)):
    light_ring(i, (130, 0, 180))
    time.sleep(0.4)
time.sleep(2)
clear_all()
time.sleep(0.5)

# Test 4: Rainbow sparkle
print("Test 4: Rainbow sparkle for 8 seconds...")
rainbow_sparkle(duration=8)

# All off
clear_all()

print()
print("========================================")
print("  RINGS TEST COMPLETE!")
print()
print("  ✓ Test 1 lit all 283? Great chain!")
print("  ✓ Test 2 — note the ORDER rings lit")
print("    up so you know which is which.")
print("  ✓ Any ring skipped? Check DOUT → DIN")
print("    connection at that join point.")
print("========================================")
