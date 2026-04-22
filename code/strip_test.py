# =====================================================
# strip_test.py — Project Sparkle
# Tests your 300 LED strip on GPIO18
#
# HOW TO RUN:
#   sudo python3 strip_test.py
#
# WHAT IT DOES:
#   Test 1 — Flashes all LEDs white (confirms all 300 work)
#   Test 2 — Red wipe (LEDs light up one at a time, left to right)
#   Test 3 — Green wipe
#   Test 4 — Blue wipe
#   Test 5 — Orange + Purple waterfall (like V1!) for 10 seconds
# =====================================================

import time
import board
import neopixel

# ============ CONFIG — edit these if needed ============
NUM_LEDS   = 300        # Number of LEDs on your strip
GPIO_PIN   = board.D18  # GPIO18 = physical Pin 12 on the Pi
BRIGHTNESS = 0.3        # 30% brightness for testing (safe on power bank)
# =======================================================

# --- Set up the strip ---
# auto_write=False means we control WHEN to send the signal
pixels = neopixel.NeoPixel(
    GPIO_PIN, NUM_LEDS,
    brightness=BRIGHTNESS,
    auto_write=False
)


# ---- Helper functions ----

def colour_wipe(colour, wait=0.01):
    """Light up LEDs one at a time from start to end of strip."""
    for i in range(NUM_LEDS):
        pixels[i] = colour
        pixels.show()
        time.sleep(wait)

def flash_all(colour, times=3):
    """Flash ALL LEDs on and off a few times."""
    for _ in range(times):
        pixels.fill(colour)   # Set every LED to this colour
        pixels.show()         # Send to the strip
        time.sleep(0.4)
        pixels.fill((0, 0, 0))  # Turn everything off (black = off)
        pixels.show()
        time.sleep(0.3)

def waterfall(colour1=(255, 80, 0), colour2=(100, 0, 180), wait=0.04):
    """
    Orange and purple waterfall — moves a band of colour down the strip.
    colour1 = first colour (orange by default)
    colour2 = second colour (purple by default)
    """
    band_size = 40  # How many LEDs wide the moving band is

    for start in range(NUM_LEDS + band_size):
        pixels.fill((0, 0, 0))  # Clear strip first

        for i in range(band_size):
            pos = start - i
            if 0 <= pos < NUM_LEDS:
                # Alternate colours every 10 LEDs within the band
                if (i // 10) % 2 == 0:
                    pixels[pos] = colour1
                else:
                    pixels[pos] = colour2

        pixels.show()
        time.sleep(wait)


# ---- Run the tests ----

print("========================================")
print("  PROJECT SPARKLE — STRIP TEST")
print(f"  Strip: {NUM_LEDS} LEDs on GPIO18")
print(f"  Brightness: {int(BRIGHTNESS * 100)}%")
print("========================================")
print()

print("Test 1: Flashing WHITE — check all 300 LEDs light up...")
flash_all((255, 255, 255))
time.sleep(1)

print("Test 2: RED colour wipe — should travel from end 1 to end 2...")
colour_wipe((255, 0, 0), wait=0.005)
time.sleep(1)

print("Test 3: GREEN colour wipe...")
colour_wipe((0, 255, 0), wait=0.005)
time.sleep(1)

print("Test 4: BLUE colour wipe...")
colour_wipe((0, 0, 255), wait=0.005)
time.sleep(1)

print("Test 5: WATERFALL — orange + purple for 10 seconds...")
start_time = time.time()
while time.time() - start_time < 10:
    waterfall()

# Turn everything off when done
pixels.fill((0, 0, 0))
pixels.show()

print()
print("========================================")
print("  STRIP TEST COMPLETE!")
print()
print("  ✓ All 300 lit up in Test 1? Great!")
print("  ✓ Colour wipe went one direction? Good.")
print("  ✓ Any LEDs that stayed off or wrong")
print("    colour? Check those solder joints.")
print("========================================")
