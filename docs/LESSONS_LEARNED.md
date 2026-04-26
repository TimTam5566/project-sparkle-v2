# Project Sparkle V2 — Lessons Learned

*Showcase: Brisbane, 23/04/2026*
*Captured: 26/04/2026*

This document captures what worked and what didn't in Version 2 of Project Sparkle, so that V3 (Sydney showcase) can build on V2's wins and avoid repeating its problems. It's intended to be useful both for Tammy (the builder) and for new contributors joining the project who don't have firsthand context on the issues described.

---

## 1. Hardware & Wiring

### Power System — Worked Well

- **Setup:** 2× 20,000 mAh + 1× 10,000 mAh batteries (50,000 mAh total).
- **Result:** Powered the full 4+ hour showcase with no battery swap required.
- **Brightness dialed to 30%** (not full power) — a deliberate choice during build to extend battery runtime for the 4+ hour event.
- **Architecture worth keeping:** All 5V components hardwired directly to power. Only the distance sensor draws from the Raspberry Pi's GPIO.

**Why this matters:** Hundreds of WS2812B LEDs draw far more current than a Raspberry Pi's onboard 5V rail can supply. Routing them through the Pi would cause brownouts (the Pi briefly losing power and rebooting). Hardwiring all high-draw components directly to battery power keeps the Pi stable and lets it focus on running code, not delivering current.

**Carry into V3:** Same power architecture. ~50 Ah is the proven floor for a multi-hour event.

---

### LED Strip (300 LEDs) — Worked Well

- Performed reliably for the entire event.
- Minor assembly issue on arrival in Brisbane, resolved via video call.
- Snap fasteners attach the strips to the dress — works well for strips specifically (do not fit rings).

**V2 issue → V3 lesson:** Assembly required a remote video call because no assembly guide accompanied the dress. An illustrated component-attachment guide should travel with the dress to every future event so on-site setup is self-serve.

**Why this matters:** When the builder isn't physically present at a showcase (as was the case in Brisbane), the on-site team has to either guess at assembly or interrupt the builder mid-day for a video call. A printed or laminated assembly guide removes that single point of failure.

---

### 8×32 LED Matrix — Worked Well

- Brand logo display ran flawlessly.
- No mounting, visibility, or pattern timing issues.

**Carry into V3:** Keep the matrix as-is.

---

### LED Rings — Mixed

**What worked:**
- JST M/F connectors made the rings electrically interchangeable.
- One ring failed in Perth pre-flight; a bypass cable allowed the dress to ship; the ring worked again in Brisbane (likely an intermittent solder joint — to be inspected on the dress's return).

**What didn't work:**
- Rings are *sewn* to the dress. Even though they're electrically swappable, they cannot be physically replaced in the field — only bypassed.
- Standard hot-glue sticks were failing on the ring solder joints, likely from operating heat.
- No assembly guide for ring placement existed.

**V3 plan:**
- Use **high-temperature glue sticks** for all ring solder joints.
- Move from sewn rings to a **universal velcro mounting system** that fits both rings *and* strips — enabling true component swaps mid-event.
- Find a stronger adhesive for attaching velcro to the back of the rings.
- Alternatives evaluated and ruled out for V3: snap fasteners (only fit strips, restrict swaps), magnetic mounting (too heavy and costly), pocket sleeves (lock in specific ring sizes, limit creativity).

**Why this matters:** JST connectors solve the *electrical* swap problem (you can unplug a failed ring without soldering). They don't solve the *mechanical* swap problem — the ring is still attached to the fabric. A failed ring stitched to the dress can only be bypassed (the bypass cable jumps the broken connection so the rest of the chain still lights up), not replaced. A universal velcro mounting system solves both problems together: unplug, peel off, stick a new one on, plug back in.

---

### Microphone — Major Win

- Programmed to detect frequencies **above 8000 Hz** — this filters out human speech and music while picking up the sharp transient sounds of clapping and cheering.
- Audience-reactive lighting became a defining moment of the Brisbane showcase.

**Why this matters:** Most ambient sounds in a showcase environment (voices, background music, room hum) sit below 8000 Hz. Sharp percussive sounds like clapping and cheering have significant energy above that threshold. Setting the trigger high lets the dress respond to *audience reaction* rather than constantly flickering through speeches and music — making the moments it does light up feel intentional.

**Carry into V3:** Keep absolutely. Build additional interactive features around this proven sensor.

---

### Wire Length — Goldilocks Problem

- V1: wires too short.
- V2: wires too long.

**V3 lesson:** Measure and document optimal wire length per component path *before* cutting. Build a small reference table per component during prototyping.

**Why this matters:** Too-short wires put strain on solder joints (they pull and break with movement). Too-long wires create extra weight, tangle, snag on fabric, and add resistance that can dim distant LEDs. The right length lets components sit naturally on the dress with a small amount of slack.

---

### Raspberry Pi Cooling — Preventative Concern

- The Pi sits inside a two-piece neoprene belt joined with velcro (designed to hide the Pi and cables).
- Pi ran hot during the event. **No failure** occurred, but on-site helpers flagged the heat as a concern.

**V3 options to investigate** (preventative, not urgent):
- Mesh ventilation panels sewn into the neoprene (passive airflow).
- Alternative belt material (canvas or stretch mesh) with an internal pocket for cable management.
- Stick-on aluminium heat sinks for the Pi's CPU and RAM (~$10 — helps regardless of belt design).
- Active cooling (5V fan with vent cutout) — only if passive isn't enough.

**Why this matters:** Neoprene is an insulator — the same material wetsuits are made of. Its job is literally to *trap heat*. Putting a Raspberry Pi (which generates heat under load) inside a sealed neoprene pocket means the pocket warms up and never releases that heat. Sustained high temperatures shorten the life of the Pi and can cause it to throttle (slow itself down to avoid damage), which would make LED patterns stutter.

---

### Remote Access at Events — Major Gap

- iOS hotspots and the Pi 4's onboard WiFi did not connect reliably in Brisbane.
- No SSH access meant no remote troubleshooting or code changes during the showcase trip.
- No physical fallback (HDMI display + USB keyboard) was packed with the dress.

**V3 plan:**
- Purchase a **4G/5G mobile hotspot** to travel with the dress (also useful for off-grid camping projects). Look for dual-band WiFi (2.4 GHz and 5 GHz), 6+ hour battery life, and unlocked SIM compatibility.
- Pack a small portable HDMI display and a folding USB keyboard as a physical-access fallback so the Pi is never inaccessible.

**Why this matters:** SSH ("Secure Shell") is the standard way to log into a Raspberry Pi remotely from a laptop — it lets you change code, restart services, and troubleshoot from across the room or even from another city. SSH needs both devices to be on the same network. iOS hotspots use security and band settings that the Pi 4's onboard WiFi sometimes refuses to connect to. A dedicated mobile hotspot creates a known, controllable network that both devices can join. A physical screen and keyboard (HDMI + USB) is the always-available fallback when no network works at all — you can sit down at the Pi and use it like a small computer.

---

---

## 2. Code & Patterns

### Visual Patterns Running in V2

V2's main code (`sparkle.py`) drove three independent visual layers simultaneously:

- **Waterfall pattern** on the LED strip and rings — orange and purple bands chasing along the lights, like a barber pole. New in V2; V1 used a static alternating pattern, not a moving one.
- **Scrolling logo** on the 8×32 matrix — a `>_` pixel-art logo (She Codes branding) scrolling left-to-right on a purple background, refreshed every 5 frames.
- **Reactive overlays** triggered by the distance sensor and microphone (covered below).

The frame loop ran at roughly 25 frames per second (`time.sleep(0.04)` per loop).

**Why this matters:** Driving three independent LED outputs (strip, rings, matrix) from a single Python loop on a Raspberry Pi is non-trivial. WS2812B LEDs are timing-sensitive — too slow a loop produces visible flicker, too fast and the Pi can't keep up. ~25 FPS hit a stable balance.

---

### Distance Sensor — Worked Well

- **Trigger:** ultrasonic sensor (HC-SR04) detects a person within 50 cm.
- **Reaction:** strip and rings cycle through purple → orange → white quickly, four times.
- **Cooldown:** roughly 3 seconds between triggers.
- The 3-second cooldown felt right during the showcase — long enough that walk-by triggers didn't feel spammy.

**Why this matters:** Without a cooldown, anyone standing in the dress's "close zone" would cause the reaction to fire continuously, making the dress look stuck. A cooldown gives each reaction breathing room and makes the moment feel intentional.

---

### Microphone — Major Win (field performance pending Kate's confirmation)

- **Trigger:** USB microphone monitored at 44.1 kHz in 1024-sample windows (about 23 ms each); each window's average absolute volume compared against a threshold (`MIC_THRESHOLD = 3000` on a 16-bit signed integer scale).
- **Reaction:** the strip flashes one randomly chosen bold colour (hot pink, electric blue, or bright green); the rings flash bright white at reduced brightness — three flashes total.
- **Auto-detection of the mic device:** the code searches for the first input device whose name contains "usb" or "mic", falling back to the first available input — so even if the USB mic is plugged into a different port, the code still finds it.

**Why this matters:** Claps and cheers at close range hit much higher peak volumes than ambient room noise or normal speech, so a well-tuned volume threshold separates "the audience reacted" from "background noise" surprisingly well — no fancy frequency analysis required. The threshold itself was tuned during real-world-volume testing (see *Bug Battles* below): high enough that everyday sound didn't trigger it, low enough that genuine audience reactions did. The auto-detection of the mic device adds another layer of robustness — it doesn't matter which USB port the mic ends up in.

*Field performance during the Brisbane showcase to be confirmed with Kate — placeholder for follow-up.*

---

### Code-Sync Gap (resolved)

There was a small drift between Pi-side code and the repo at showcase time:

- The repo's `sparkle.py` had `BRIGHTNESS = 0.4` (40%); the version running on the Pi at Brisbane had been reduced to `0.3` (30%) — a deliberate choice during build to extend battery runtime for the 4+ hour event.
- A small amount of duplicated code was tidied up on the Pi during the build phase.

Both have since been synced back to the repo.

**V3 lesson:** before the dress ships, commit any Pi-side tweaks back to the repo and tag the commit (e.g., `v2.0-showcase`) so the public record matches the showcase reality at the moment of the showcase. The brightness change is the cleanest example — a deliberate engineering decision (less light = more battery hours) that wasn't visible in the committed code at flight time.

**Why this matters:** When a future contributor reads the repo to understand "what did V2 do at Brisbane?", the answer should be "exactly what's in the repo at this commit." Drift between live and committed code makes lessons harder to verify later — and important reasoning (like "we chose dimmer light to get longer runtime") gets lost.

---

### Defensive Coding — Worked Well

V2's `sparkle.py` includes several "things break gracefully" patterns that proved their worth:

- **Distance sensor timeout** — `get_distance_cm()` returns `999` if no echo arrives within 100 ms, instead of waiting forever. Without this, the sensor could hang the entire program in environments with no reflective surfaces.
- **Matrix setup wrapped in try/except** — if the matrix fails to initialise, the program prints a warning and continues with strip and rings only, instead of crashing.
- **Threading for sensors** — the mic and distance sensor each run on their own daemon thread, so a slow sensor read never stalls the animation loop.

**Why this matters:** Showcase environments are unpredictable. A piece of hardware that failed three days before a flight, or a sensor that sees nothing in an open room, shouldn't take the whole dress down with it. Defensive coding turns "everything stops" into "one thing degrades, the rest keeps running."

---

### Code Structure

The `code/` folder contains four Python files:

- **`sparkle.py`** — the showcase version. Polished, fully commented, runs all three layers (strip, rings, matrix) plus both sensors.
- **`mic_test.py`**, **`rings_test.py`**, **`strip_test.py`** — standalone hardware validators used during the build, especially after soldering the rings. Each one exercises a single component independently to isolate problems.

An earlier minimalist draft (`sparkle_clean.py`) was kept in the repo through the showcase but removed afterwards as part of cleanup, since it added confusion (the name suggested "the clean/good version" when in reality the showcase code is in `sparkle.py`).

**V2 lesson:** delete dead code rather than leaving it for later. File names are the first cue any future contributor sees, and ambiguous names cost reading time.

**Why this matters:** Repos accumulate experimental files during a build. Each one that survives past its purpose is a small landmine for future-you or future contributors. Cleanup is a 5-minute job at the time, a 30-minute archaeology dig later.

---

### Workflow & Tooling

- **Build phase:** all coding done over **SSH using Termius** on the Raspberry Pi directly. Edits made on the Pi, tested on the Pi.
- **Pre-flight:** code transferred into **VS Code** locally and committed to **GitHub** so the codebase could be published to the V2 repo.
- **Auto-start:** code ran as a **systemd service** (`sparkle.service`) so the Pi boots and goes — no terminal, no manual start, no flashing screen on stage.

**Why this matters:** A systemd service means the dress is "switch on the Pi, wait 30 seconds, it's running." For non-technical operators on the day, this is the difference between a 1-step setup and a 6-step setup.

---

### Tweak Loop

The standard development cycle during V2 was:

1. Stop the service (`sudo systemctl stop sparkle.service`)
2. Edit the code
3. Start the service (`sudo systemctl start sparkle.service`)
4. Watch the dress and judge the result
5. Repeat

This worked, but added friction — each colour or timing tweak required a service stop and restart.

**V3 possibility:** investigate a faster tweak loop — for example, a config file the running service can re-read without a restart, or a "test mode" that runs `sparkle.py` directly from the command line without the service wrapper. Anything that shortens the loop pays for itself within an hour of iteration.

**Why this matters:** Friction in the tweak loop directly slows down creative iteration. When changing a single number (like brightness or cooldown) takes 30 seconds, you tweak less than you should. Removing that friction lets aesthetic choices be made in minutes instead of hours.

---

### Test Strategy — Worked Well

V2 used a layered testing approach:

1. **Component-level:** each piece of hardware (strip, rings, mic) tested in isolation using its own test script (`mic_test.py`, `rings_test.py`, `strip_test.py`).
2. **Process-level:** each program behaviour (waterfall, distance reaction, mic reaction) tested individually before combining.
3. **Integration:** all components running together in `sparkle.py`.
4. **Wearer-level:** final check with Kate wearing the dress before packing for Brisbane.

**Why this matters:** When something breaks at level 3 or 4, you already know levels 1 and 2 are good — so the bug is in the interaction, not the individual parts. This dramatically narrows where to look. Skipping straight to integration testing is the most expensive way to find bugs.

---

### Bug Battles

The hardest parts of V2's code work, in rough order of pain:

- **Getting colours and timing right** — the brightness, the colour mix, the speed of the chase pattern — these aren't math problems, they're aesthetic decisions that only reveal themselves on the actual hardware in actual lighting. Many small tweaks.
- **Getting reactions to fire correctly** — making the strip flash one random colour while the rings flash white at lower brightness, with the right number of flashes and the right pause between them. Lots of iteration on `colour_flash_reaction()`.
- **The "heavy metal" microphone test** — testing the mic at home in a quiet house, the only ambient noise was dogs barking. Quiet domestic conditions didn't simulate a real showcase. Solution: played heavy metal music at high volume to mimic the noise floor of an actual event, then tuned the threshold against that.

**Why the heavy metal story matters:** it's a small but illustrative version of a much bigger principle — *test environments need to match real conditions, or you're tuning for the wrong thing.* A mic threshold calibrated against silence plus dog barks would have triggered constantly in a venue full of speeches and applause. Adapting the test environment caught this before the showcase, not after.

---

---

## 3. Team & Process

### V2 Team Composition

V2 was built by:

- **Tammy Healy** — lead builder, all coding, and primary hardware integration.
- **Emma Spear** — build-phase collaborator. Notably fixed the distance sensor logic and contributed to the colour reaction work.
- **Alice Maiorana** — build-phase collaborator. Sewed the velcro for the matrix mounting and assisted with the final fit test before the dress was packed for Brisbane.
- **Kate Kirwin** — the wearer, owner, and Brisbane on-site lead. Did the final fit check before packing and was responsible for setup on the day.
- **Lucy Nguyen** — Brisbane on-site assembly partner. Held the phone during video troubleshooting calls so Tammy (offsite, in Perth) could see exactly what was happening on the dress.
- **Reece Jocumsen** — Brisbane on-site assembly partner. Helped Kate connect everything to the Raspberry Pi.

Nina from MadeAPT made the dress for V1 but did not contribute to V2. Jordan Duabe was V1's lead mentor and did not contribute to V2.

---

### What Worked Well

- **Kate's final fit test before packing** — a hard pre-flight gate. If the dress doesn't work on Kate's body in Perth, it doesn't go in the suitcase.
- **The Wednesday Brisbane troubleshooting session** — the dress wasn't working initially. Lucy on-site holding the phone, Kate in the dress, Tammy on video from Perth. The three-way coordination got the dress functional in time for the showcase. A strong "this collaboration is working" moment, and a proud one for everyone involved.
- **Emma's targeted fixes** — distance sensor and colour reaction work. Bringing in someone with focused expertise on a specific issue is faster than trying to solve everything alone.
- **Alice's contributions** — velcro-for-matrix sewing and the final fit test. Proper physical assembly of components onto the dress requires hands that aren't busy with code.
- **A multi-person on-site Brisbane team (Lucy + Reece + Kate)** — even with the builder offsite, having more than one person physically with the dress meant problems could be diagnosed and fixed in real time.

**Why this matters:** For a multi-disciplinary project (code, electronics, sewing, on-site assembly), each "this worked" moment shows the same principle in action — the build benefits from clearly-defined helpers with focused roles, rather than one person trying to cover everything.

---

### Communication & Coordination

- **Primary channel:** Slack — used for almost all team communication during the build.
- **Build cadence:** ad-hoc, scheduled around Tammy's availability since the build space and tools are at her location.

**Why this matters:** When the build is concentrated in one physical space (the builder's home/workshop), the schedule is naturally constrained by that space's availability. Slack lets contributors coordinate around that constraint asynchronously.

---

### Build Structure for Volunteers

V2 build effort was concentrated heavily into the final stretch.

**V3 lesson — Tammy's framing:** "A more structured approach to the build to allow volunteers to know what needs to be done and where they can help." Before V3 build kicks off, define and share a clear task list — what's needed, who could pick up each piece, and by when.

**Why this matters:** Volunteers are often willing to help but don't always know where their skills fit. A clear structure ("we need someone who can solder rings on Saturday afternoon" or "we need help testing patterns next Wednesday evening") makes contribution low-friction. It also makes it visible when nobody has signed up for a critical task — which is exactly when extra effort or scope adjustment is needed.

---

### Handover to Kate

V2's handover to Kate (offsite builder, on-site wearer) included:

- **Step-by-step component connection docs** — with photos — for power banks to Pi and components to power.
- **SSH helper docs** — to support remote troubleshooting if needed.

**What was missing:** a detailed photo guide for *connecting the LED strip to the dress itself*. The handover assumed Kate would attach the components to the dress at Brisbane, but the components hadn't been physically attached in Perth before shipping — so Kate was assembling the mounting for the first time on the day.

**V3 lesson:** any handover to a wearer or offsite assembler must include a *visual mounting guide* — photos with arrows, every step, every component. Don't assume the wearer can intuit placement just because they're the one wearing the dress.

**Why this matters:** The hardest documentation to write is for the steps your own hands do automatically. The builder knows where the strip attaches because they've handled it a hundred times; the offsite assembler is seeing it for the first time. Photos cost minutes to take during the build and save hours of confusion under showcase pressure.

---

### What to Repeat

- **Helpers at the destination location.** Even when the builder is on-site at the showcase, a team of 2–3 helpers at the venue makes assembly, troubleshooting, fit checks, and last-minute fixes dramatically faster. For V2, this same approach made offsite assembly possible at all.

**Why this matters:** A live event has many simultaneous demands — assembly, troubleshooting, fit checks, last-minute fixes, watching for hardware issues during the performance. One pair of hands cannot cover all of them at once. Always plan for at least two on-site helpers, regardless of where the builder is.

---

*This document captures the V2 lessons learned. It will be updated if any field-performance details emerge from post-event reflection (notably, microphone behaviour on the day — pending Kate's input).*
