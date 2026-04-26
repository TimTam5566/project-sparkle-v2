# Project Sparkle — V2

# Where it all started

In 2025 I was lucky enough to be accepted into the 2025 She Codes Australia - She Codes Plus Program. During our Python sprint Jordan Duabe (our lead mentor) and Kate Kirwin brought in different projects that could be created using Python and LED rings and Microbits. During one of these sessions Kate mentioned a dress that she would like to create using addressable LEDs. I took one look and knew that I would have to make that happen.

Things stalled as the program was intensive. Towards the end of the course I was listening to the "Raft of Bitches podcast" Hosted by Kate Kirwin, Jo Minney and Ricky Barnes (check it out if you haven't already) where Nina Karisik founder of MadeAPT was being interviewed. The final night of our program (Late December 2025) I approached Kate and told her I wanted to make the dress happen before our showcase in February 2026. That I listened to the podcast and that we needed to get Nina involved. That weekend we had a meeting with Nina who arranged for the dress to be made.

We ordered components, planned what we were going to do, and then Kate left the state, and a few weeks later left the country. The dress arrived 9 days before the Perth Showcase, Kate arrived 2 days before the showcase. She tried the dress on the day before and we had a critical failure. But in 24 hours the dress was ready to go. A programmable LED dress built as a passion project for the founder of She Codes Kate Kirwin, version one was a huge success.

Version 2 evolves the original one-strip prototype (https://github.com/j4ckofalltrades/project-sparkle) created with the assistance of Jordan Duabe our 2025 She Codes Plus cohort Python Mentor and Guru. 

Version 2 has evolved into a multi-zone, interactive light garment that responds to people and sound in real time. Built and coded by Tammy Healy with help from Emma Spear and Alice Maiorana. Learning new skills as we go. Troubleshooting attachment of components, wiring, soldering, component failure, component success and then component failure again.

![Status](https://img.shields.io/badge/status-showcased--April--2026-E67E22)
![Pi](https://img.shields.io/badge/hardware-Raspberry%20Pi%204-6A4C93)
![Python](https://img.shields.io/badge/code-MicroPython%20%2F%20Python-blue)

---

## What the dress does

At a glance, V2 runs three independent LED zones driven from a single Raspberry Pi 4:

- **LED strip (300 pixels)** — the main garment lighting, running a rolling waterfall
  pattern in the Project Sparkle palette (orange / purple)
- **8 × 32 pixel matrix** — displays the Project Sparkle logo and scrolling text
- **LED rings** — decorative accents in a range of sizes, driven off the same chain

Two sensors make it interactive:

- **Distance sensor** — when someone walks close to the wearer, the LED strip
  flashes in one of three alternating colours
- **Microphone** — loud sounds and music trigger pattern bursts, so the dress
  reacts to the venue's energy

Powered by three USB-A power banks (one per zone), fully portable, no mains cable.

## V1 → V2 — what changed

V1 was proof of concept: 600 LEDs, waterfall pattern, logo matrix, distance sensor responded by flashing when someone was in close proximity to the dress, hardwired straight off 2 power banks. It worked extremely well.

V2 is the event-ready version:

| Change | Why |
| --- | --- |
| 300 LEDs instead of 600 | Better refresh, less power draw, brighter effect per LED |
| Multiple LED rings added | More visual interest, zones of light instead of one blanket |
| Microphone added | Sound reactivity for wider audience participation, reaction to cheers and applause |
| Three power banks | One zone failing doesn't take down the whole dress |

## Hardware list

- Raspberry Pi 4 Model B (main controller)
- WS2812B addressable LED strip, 300 LEDs
- 8 × 32 pixel WS2812B matrix
- Assorted WS2812B LED rings
- HC-SR04 ultrasonic distance sensor
- USB microphone
- 2 × 20,000mAh USB A power banks
- 1 x 10,000mAh USB A power bank
- 3 x power cords with components 5v wire hardwired to the cord and ground cord split between the component and Raspberry Pi.
- SD card (32GB+) for the Pi — plus an identical spare (in case of corruption)  
- Outfit: Dress created in conjunction with Nina from MadeAPT, consists of dress and skirt in neoprene, with a sheer overskirt to diffuse the LEDs' light. LED rings and strip attached to skirt.
- Mounting hardware: LED strip attached via press buttons, rings are stitched to skirt future versions it is hoped we can find a robust way of attaching the components so they can be removed and replaced if there is a failure. Various attachments have been trialled what we are using on this version is our most successful to date. JST connectors connect components to each other or to power supply and Raspberry Pi 4. 5v is hardwired to power cord to reduce voltage load on the raspberry Pi 4.
- JST SM M/F connectors for bypass joins - for ring failures. 

## The code

| File | Purpose |
| --- | --- |
| `code/sparkle.py` | **Main program** — boots as a systemd service, drives all three LED zones and both sensors |
| `code/sparkle_clean.py` | Earlier/cleaner version of the main loop, kept for reference |
| `code/strip_test.py` | Isolated test for the 300-LED strip |
| `code/rings_test.py` | Isolated test for the LED ring chain |
| `code/mic_test.py` | Isolated test for the microphone input threshold |


## Docs

- `docs/Sparkle_V2_Reference.html` — the main V2 build reference
- `docs/Project_Sparkle_Guide.html` — general build walkthrough
- `docs/GPIO_Reference_Card.html` — Raspberry Pi pin-out cheat sheet

## Running the code on a Pi

These scripts are written for a Raspberry Pi 4 running Raspberry Pi OS (Debian 13,
trixie). They won't run on a regular computer — they need real GPIO pins.

High-level setup:

1. Flash Raspberry Pi OS to an SD card and boot the Pi
2. Install dependencies: `sudo apt install python3-pip portaudio19-dev`
3. Install Python packages: `pip3 install rpi_ws281x numpy pyaudio adafruit-circuitpython-hcsr04`
4. Wire up the LEDs to GPIO 18 (data), the distance sensor to GPIO 23/24, and the
   microphone via USB
5. Copy `sparkle.py` onto the Pi in `~/project-sparkle/`
6. Set it up as a systemd service so it runs on boot (see `docs/` for details)

⚠️ **Safety note on LED power:** A 300-pixel WS2812B strip at full white draws
up to 18 amps. Never run this off a Raspberry Pi's 5V pin. Always power LEDs
from their own source and share ground with the Pi.

## Acknowledgements

- **She Codes** — for the coding education, the community, and the confidence
  to take on any project
- Every friend or team mate (you know who you are) who's lent a power bank, a kitchen table, helped me debug a loose wire, or stood next to the dress at a show while I fixed something mid-event
- Kate, for waiting and waiting while the last minute crash is fixed the day before showcase, or the day before leaving for a showcase. For not being surprised when she walks in and I am shouting at the dress. For her patience, support, encouragement and belief in everything I do. For building the amazing She Codes community that has changed my life.

## Licence & reuse

This code is shared so other makers can learn from it. Feel free to reuse, adapt,
and remix — credit would be lovely but isn't required. If you build your own
LED garment, I'd love to see it.

## Version 3?

On the horizon, depending on what V2 teaches us: stay tuned we have some amazing things planned for version 3.

---

*Made in Australia 🇦🇺 in conjunction with She Codes Australia with a lot of pepsi max and several "have you tried turning it off and on again" moments.*
