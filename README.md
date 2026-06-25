<div align="center">

# 🧸 BabyBox

### A screen-free, figurine-driven media player for toddlers

*Place a 3D-printed character on the box — its song or video plays. No menus, no screens, no swiping.*

<img src="renders/babybox_render.png" alt="BabyBox render — a soft white box with a glowing rainbow LED strip and a pink figurine on top" width="640">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Zero%202%20W-A22846?logo=raspberrypi&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-web%20UI-000000?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-storage-003B57?logo=sqlite&logoColor=white)
![OpenSCAD](https://img.shields.io/badge/OpenSCAD-parametric%20CAD-F9D72C?logoColor=black)
![Tests](https://img.shields.io/badge/pytest-22%20tests-2ea44f)

</div>

---

## What it is

BabyBox is a tangible, Montessori-friendly media player built around a Raspberry Pi. A child plays content by **physically placing a figurine** on top of the box — each figurine hides an RFID tag and magnets, so it snaps into place and is detected instantly. Parents curate content from a phone or laptop via a web UI; kids interact with nothing but the toys.

It's a full-stack hardware project: **embedded software, a parent web app, parametric 3D-printed hardware, and the audio/Bluetooth plumbing** to tie it together.

> [!NOTE]
> This is a personal/portfolio build. It demonstrates end-to-end ownership of a physical product — from OpenSCAD CAD and GPIO wiring up through a tested Python service and a Flask UI — including a hardware-abstraction layer that lets the entire system run and be tested **on a laptop with no Raspberry Pi attached**.

---

## How it works

```
   Figurine                Raspberry Pi Zero 2 W
 (RFID + magnets)     ┌───────────────────────────┐
        │             │                           │
        ▼   SPI       │   ┌─────────┐             │──── HDMI ───► TV   (video only)
   ┌─────────┐  ┌────►│   │   mpv   │  playback   │
   │ box top │──┘     │   └─────────┘             │──── BT A2DP ► Speaker (all audio)
   │ RFID +  │        │                           │
   │ magnets │        │   Flask web UI  ◄── WiFi ─┼──── 📱 Parent's phone / laptop
   └─────────┘        └───────────────────────────┘
```

1. **Tap to play** — a figurine is placed; the MFRC522 reader picks up its RFID UID.
2. **Map & play** — the controller looks up the tag → media mapping (SQLite) and plays it with `mpv`.
3. **Split A/V** — video goes to the TV over HDMI; *all* audio is routed to a Bluetooth speaker (placed near the child at a safe volume).
4. **Playback lock** — once content starts, new figurines are ignored until it finishes. No toddler content-hopping.
5. **Parents stay in control** — a web UI handles YouTube downloads (`yt-dlp`), figurine assignment, daily video limits, and history.

---

## Highlights

| | |
|---|---|
| 🎯 **Zero-screen interface for kids** | The only "UI" a toddler touches is a physical toy. RFID + magnets give a satisfying snap and reliable reads. |
| 🔌 **Mock/real hardware abstraction** | A factory + `base` interfaces swap real GPIO drivers for mocks via `BABYBOX_ENV=dev`. The whole stack runs and is unit-tested off-Pi. |
| 📺 **Split audio/video routing** | Picture on the TV (HDMI), sound on a portable Bluetooth speaker — solved with a non-trivial PipeWire/WirePlumber config. |
| ⏳ **Real parental controls** | Per-day video limits (count *and* minutes), 6 AM reset, audio always unlimited, with gentle LED + buzzer "last video / all done" feedback. |
| 🧩 **Parametric 3D-printed hardware** | OpenSCAD enclosure + figurine bases with pause-and-insert magnet pockets (fully sealed = toddler-safe). Includes a custom "burgerdog" multi-color mascot. |
| 🧠 **Robust by design** | Falls back to HDMI audio if the speaker is off; de-dupes rapid RFID reads; a finite-state playback machine keeps behavior predictable. |

---

## Tech stack

| Layer | Tech |
|-------|------|
| **Core service** | Python 3, threaded RFID/button loops, FSM controller |
| **Media** | `yt-dlp` (download) · `mpv` via `python-mpv` (playback) |
| **Audio** | PipeWire + WirePlumber (Bluetooth A2DP, no-suspend config) |
| **Hardware** | MFRC522 RFID (SPI) · WS2812 LEDs · passive buzzer · 2 buttons |
| **Web UI** | Flask + vanilla HTML/JS (no build step) |
| **Storage** | SQLite (single file, zero-config) |
| **CAD** | OpenSCAD (parametric, code-defined) → STL → Bambu Studio |
| **Ops** | systemd services · `setup.sh` provisioning |
| **Tests** | pytest (controller, limits, db) |

---

## Getting started (dev mode — no Pi required)

The hardware layer mocks itself, so you can run the full service on macOS/Linux:

```bash
cd software
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run with mock hardware + web UI
BABYBOX_ENV=dev BABYBOX_DATA_DIR=./_data python -m software.main
# → web UI at http://localhost:8080

# Run the test suite
pytest
```

In dev mode, "scanning a figurine" and button presses are simulated through the mock drivers, and media playback is stubbed — so you can exercise the controller, limits, and web UI end-to-end without any electronics.

### On the Raspberry Pi

```bash
# Raspberry Pi OS Lite — enable SPI, install system deps, BT config, systemd units
sudo ./scripts/setup.sh
```

This installs the Pi-only drivers (`mfrc522`, `rpi_ws281x`, `RPi.GPIO`), the WirePlumber Bluetooth fixes (`scripts/wireplumber/`), and registers the `babybox` + Bluetooth auto-connect services. The parent UI is then reachable at **`http://babybox.local`**.

---

## Repository layout

```
BabyBox/
├── software/            # Python service
│   ├── main.py          #   entry point — wires hardware, controller, web together
│   ├── controller.py    #   playback state machine + video-limit logic
│   ├── player.py        #   mpv wrapper (split A/V output)
│   ├── downloader.py    #   yt-dlp wrapper (MP4 video / MP3 audio)
│   ├── bluetooth.py     #   speaker pairing + auto-connect
│   ├── limits.py        #   daily video-limit enforcement
│   ├── db.py / models.py#   SQLite layer + data classes
│   ├── hardware/        #   ⭐ base interfaces + mock/ and real/ drivers (factory)
│   ├── web/             #   Flask app (dashboard, library, figurines, settings, history)
│   └── tests/           #   pytest suite
├── hardware/
│   ├── enclosure/       #   babybox-case.scad — parametric box
│   └── figurines/       #   base template + "burgerdog" multi-layer mascot
├── scripts/             #   setup.sh, systemd units, WirePlumber configs, STL gen
├── renders/             #   Blender renders + exported STLs
├── docs/                #   printable assembly guide (PDF + generator)
├── website/             #   marketing site (deployed via GitHub Pages)
└── SPEC.md              #   full design spec (hardware, software, BoM, decisions)
```

---

## Hardware (bill of materials)

Roughly **~$51** total if you already own a Bluetooth speaker:

Raspberry Pi Zero 2 W · MicroSD · MFRC522 RFID module + MIFARE coin stickers · WS2812 LED strip · passive buzzer · 2 buttons · neodymium magnets (6×3 mm) · 5V/3A supply · mini-HDMI cable · 3D-printed enclosure & figurines (Bambu Lab P2S).

Full BoM, GPIO pinout, wiring, and design rationale live in **[`SPEC.md`](SPEC.md)**.

---

## Design decisions worth calling out

- **Figurine = the interface.** RFID coin stickers are invisible to the child and embedded in the toy; magnets guarantee the tag lands over the antenna every time.
- **Magnets are sealed inside the print** using a pause-and-insert technique (solid layers above and below) — they cannot be removed or swallowed.
- **Audio over Bluetooth, not the Pi jack** — portable, volume-safe near the child, and frees GPIO 18 for the LED strip. The tradeoff was a finicky shared-radio Bluetooth stack, fixed with two WirePlumber configs.
- **Playback lock over a "stop and switch" model** — toddlers will otherwise swap figurines endlessly. Content must finish; the stop button is a parent escape hatch.
- **Code-defined CAD (OpenSCAD)** — the enclosure is parametric and diff-able, not a binary blob.

---

<div align="center">

*Built as a portfolio project — a small physical product taken from spec to (almost) toddler-tested.*

See **[`SPEC.md`](SPEC.md)** for the complete design document.

</div>
