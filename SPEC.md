# BabyBox — Toddler Media Player

## Overview

BabyBox is a toddler-friendly media player powered by a Raspberry Pi. The child places
a 3D-printed figurine on top of the box to play a song or video. Each figurine has an
RFID tag and magnets embedded inside. The box has matching magnets and an RFID reader
under the top surface, so the figurine snaps into place and is detected instantly.

Parents add content by pasting YouTube URLs into a web UI. The system downloads
the video and saves it locally — either as video (MP4) or audio-only (MP3),
depending on what the parent chooses. A daily video limit prevents excessive screen
time while audio remains unrestricted.

**Output routing:** Video goes to the TV via HDMI. All audio goes to a Bluetooth
speaker. For video content, the picture is on the TV and the sound comes from the
Bluetooth speaker.

**Playback lock:** Once content starts playing, it must finish before a new figurine is
accepted. Figurines placed during playback are ignored. This prevents a toddler from
endlessly swapping between content.

---

## 1. User Stories

| Who    | What                                                                    |
|--------|-------------------------------------------------------------------------|
| Child  | Places a figurine on the box and the associated song/video starts       |
| Child  | Sees a fun LED animation when a figurine is placed                      |
| Child  | Places figurines during playback — nothing happens (content must finish)|
| Child  | Gets a "last video" warning (LED + buzzer) when 1 video remains        |
| Child  | Gets a "all done" feedback (LED + buzzer) when video limit is reached   |
| Parent | Pastes a YouTube URL, picks audio or video, system downloads it         |
| Parent | 3D-prints figurines and embeds RFID tags + magnets                      |
| Parent | Assigns a figurine to a downloaded media file via the web UI            |
| Parent | Sets a daily video limit (e.g., 3 videos or 45 min/day)                |
| Parent | Sees playback history / daily stats on the web UI                       |

---

## 2. Hardware

### 2.1 Bill of Materials

| Component                       | Source        | Est. Cost |
|---------------------------------|---------------|-----------|
| Raspberry Pi Zero 2 W           | Purchase      | ~$15      |
| MicroSD card (32 GB+)           | Purchase      | ~$8       |
| MFRC522 RFID Module             | Kit           | --        |
| RFID sticker tags (MIFARE 13.56 MHz, 25mm coin type) | Purchase (10x) | ~$5 |
| Neodymium magnets (6x3mm disc, 20x) | Purchase  | ~$5       |
| Bluetooth speaker                | Already owned / Purchase | ~$0-20 |
| WS2812 RGB 8 LED Strip          | Kit           | --        |
| Passive Buzzer                   | Kit           | --        |
| Buttons (x2: play/pause, stop)  | Kit           | --        |
| Resistors / wires / breadboard  | Kit           | --        |
| 5V 3A micro USB power supply    | Purchase      | ~$8       |
| Mini HDMI to HDMI cable         | Purchase      | ~$5       |
| 3D-printed enclosure + figurines| Bambu Lab P2S | ~$5       |
| **Total (if speaker owned)**    |               | **~$51**  |

### 2.2 Why Pi Zero 2 W?

- Cheapest Pi with quad-core ARM (1 GHz) and hardware H.264 decode
- Built-in WiFi for the parent web UI (no extra dongles)
- Built-in Bluetooth for connecting to the speaker
- Enough GPIO for RFID, LEDs, buttons, and buzzer
- HDMI output for video to TV
- Runs headless Raspberry Pi OS Lite with minimal overhead

### 2.3 Output Routing

```
                    ┌──────────────┐
                    │  Raspberry   │
   Figurine         │  Pi Zero 2 W │
   (RFID + magnet)  │              │
     ▼         SPI  │  ┌────────┐  │──── HDMI ────► TV (video only)
   [Box top] ──────►│  │  mpv   │  │
                    │  └────────┘  │──── Bluetooth ► Speaker (all audio)
                    │              │
                    └──────────────┘
```

**Video content:** Picture on TV via HDMI, audio routed to Bluetooth speaker via
PulseAudio/PipeWire.

**Audio content:** Sound plays on Bluetooth speaker only. TV can be off or show an
idle screen.

**Why split?** The Bluetooth speaker can be placed near the child at a safe volume,
while the TV can be further away. Volume is controlled on the speaker itself.

### 2.4 GPIO Pin Assignment

```
Pi Zero 2 W GPIO Layout
========================

MFRC522 (SPI0):
  SDA  → GPIO 8  (CE0)
  SCK  → GPIO 11 (SCLK)
  MOSI → GPIO 10 (MOSI)
  MISO → GPIO 9  (MISO)
  RST  → GPIO 25
  3.3V → 3.3V
  GND  → GND

WS2812 LED Strip:
  DIN  → GPIO 18 (PWM0)
  5V   → 5V
  GND  → GND

Buttons (active low, internal pull-up):
  Play/Pause → GPIO 17
  Stop       → GPIO 27

Passive Buzzer:
  Signal → GPIO 12 (PWM1)
  GND    → GND
```

No I2S DAC conflicts since audio goes over Bluetooth, so GPIO 18 is free for the
WS2812 strip.

---

## 3. Software Architecture

```
┌───────────────────────────────────────────────────────┐
│                     BabyBox OS                        │
│              (Raspberry Pi OS Lite + PulseAudio)      │
├───────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────┐  ┌─────────────┐  ┌────────────────┐ │
│  │ RFID       │  │ Media       │  │ LED / Buzzer   │ │
│  │ Listener   │  │ Player      │  │ Feedback       │ │
│  │ (mfrc522)  │  │ (mpv)       │  │ Controller     │ │
│  └─────┬──────┘  └──────▲──────┘  └───────▲────────┘ │
│        │                │                 │           │
│  ┌─────▼──────────────────────────────────┴────────┐  │
│  │           Core Controller (Python)              │  │
│  │  - Tag → media mapping (SQLite)                 │  │
│  │  - Playback state machine (with lock)           │  │
│  │  - Video limit enforcement                      │  │
│  │  - Button input handling                        │  │
│  │  - Bluetooth speaker connection management      │  │
│  └─────────────────────▲───────────────────────────┘  │
│                        │                              │
│  ┌─────────────────────▼───────────────────────────┐  │
│  │           Parent Web UI (Flask)                 │  │
│  │  - Map figurines to media files                 │  │
│  │  - Set video limits                             │  │
│  │  - View playback history                        │  │
│  │  - Upload media                                 │  │
│  │  - Bluetooth speaker pairing                    │  │
│  └─────────────────────────────────────────────────┘  │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │           PulseAudio / PipeWire                 │  │
│  │  - Default audio sink → Bluetooth speaker       │  │
│  │  - HDMI sink → video only (no audio)            │  │
│  └─────────────────────────────────────────────────┘  │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### 3.1 Tech Stack

| Layer           | Technology                    | Why                           |
|-----------------|-------------------------------|-------------------------------|
| Language        | Python 3                      | Best RPi GPIO ecosystem       |
| RFID            | `mfrc522` Python lib (SPI)    | Direct support for MFRC522    |
| Media download  | `yt-dlp`                      | YouTube download, audio extract|
| Media playback  | `mpv` (via python-mpv)        | Lightweight, HW-accelerated   |
| Audio routing   | PulseAudio                    | Bluetooth A2DP sink support   |
| LED control     | `rpi_ws281x`                  | Native WS2812 driver          |
| Database        | SQLite                        | Zero config, single file      |
| Web UI          | Flask + vanilla HTML/JS       | Lightweight, no build step    |
| Process mgmt    | systemd services              | Auto-start on boot            |

### 3.2 Data Model

```sql
-- Media files stored on disk at /home/pi/babybox/media/{audio,video}/
CREATE TABLE media (
    id          INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    filename    TEXT NOT NULL,          -- relative to media dir
    media_type  TEXT NOT NULL,          -- 'audio' | 'video'
    source_url  TEXT,                   -- original YouTube URL
    thumbnail   TEXT,                   -- path to downloaded thumbnail
    duration_s  INTEGER,               -- duration in seconds
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RFID tag to media mapping (each tag is inside a figurine)
CREATE TABLE tags (
    uid         TEXT PRIMARY KEY,       -- RFID tag UID (hex string)
    media_id    INTEGER NOT NULL,
    label       TEXT,                   -- friendly name ("Elsa figurine")
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (media_id) REFERENCES media(id)
);

-- Playback log for stats and limit enforcement
CREATE TABLE playback_log (
    id          INTEGER PRIMARY KEY,
    media_id    INTEGER NOT NULL,
    tag_uid     TEXT,
    started_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at    TIMESTAMP,
    completed   BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (media_id) REFERENCES media(id)
);

-- Parental controls
CREATE TABLE settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL
);
-- Default settings:
--   daily_video_limit_count  = 5
--   daily_video_limit_minutes = 60
--   limit_reset_hour = 6          (reset at 6 AM)
--   bt_speaker_mac = ""           (paired Bluetooth speaker MAC address)
```

### 3.3 Core State Machine

```
              ┌──────────┐
    ┌─────────│   IDLE   │◄─────────────────────────────┐
    │         └────┬─────┘                              │
    │              │ figurine placed                     │
    │              ▼                                    │
    │    ┌──────────────────┐                           │
    │    │ CHECK LIMITS     │                           │
    │    │ (video only)     │                           │
    │    └──┬────────┬──────┘                           │
    │       │ OK     │ exceeded                         │
    │       ▼        ▼                                  │
    │  ┌────────┐  ┌──────────────┐                     │
    │  │LOADING │  │ ALL DONE     │                     │
    │  │(LEDs)  │  │ (buzzer+LED) │─────────────────────┘
    │  └──┬─────┘  └──────────────┘
    │     │
    │     │ last video?
    │     ├────yes──► "last video" warning (buzzer + yellow LEDs)
    │     │           then continue to PLAYING
    │     │
    │     ▼
    │  ┌───────────────────┐
    │  │ PLAYING           │ ◄── figurines placed here are IGNORED
    │  │ (audio or video)  │
    │  │                   │──── stop button → IDLE
    │  └───────┬───────────┘
    │          │ playback ends naturally
    │          ▼
    │  ┌───────────────────┐   was last video?
    │  │ FINISHED          │──────yes──► "all done" feedback
    │  │ (log playback)    │              (buzzer + red→off LEDs)
    │  └───────┬───────────┘              then → IDLE
    │          │ no
    └──────────┘
```

**Key behaviors:**

**Playback lock**
- While in PLAYING state, all RFID scans (figurines placed) are silently ignored
- Content must finish on its own (or be stopped via the stop button)
- The stop button is a parent escape hatch, not intended for the child
- After content finishes, the system returns to IDLE and accepts new figurines

**Last video warning**
- When the child starts what will be their last allowed video, the box signals
  "this is the last one" before playback begins
- Short buzzer melody (gentle, not alarming) + LEDs pulse yellow briefly
- Playback proceeds normally after the warning

**All done feedback**
- When the last video finishes, or when a figurine is placed after the limit is
  reached, the box signals "no more videos today"
- Distinct buzzer melody (calm, final-sounding) + LEDs pulse red then fade off
- Audio figurines still work normally — only video is limited

---

## 4. Video Limit System

- Limits tracked per calendar day (resets at configurable hour, default 6 AM)
- Two limit modes (whichever is hit first):
  - **Count-based:** max N videos per day
  - **Time-based:** max M minutes of video per day
- Audio content is never limited — only video counts against the daily allowance
- Parents can override / adjust limits via web UI

### Feedback stages

| Moment                          | Buzzer                        | LEDs                          |
|---------------------------------|-------------------------------|-------------------------------|
| **Last video starting**         | Gentle ascending tone (short) | Pulse yellow 3x, then normal  |
| **Last video finished**         | Calm descending melody        | Pulse red 3x, then fade off   |
| **Limit already reached** (figurine placed, no videos left) | Same descending melody | Same red pulse + fade off |

The two feedback patterns are intentionally distinct so the child learns to
associate them:
- **Yellow / ascending** = "one more, then we're done"
- **Red / descending** = "all done for today, let's do something else"

---

## 5. Bluetooth Audio Setup

The Pi Zero 2 W connects to a Bluetooth speaker over A2DP (Advanced Audio
Distribution Profile) using PulseAudio.

### Auto-connect on boot
- The speaker MAC address is stored in the database
- A systemd service runs on boot that:
  1. Powers on the Bluetooth adapter
  2. Connects to the paired speaker
  3. Sets it as the default PulseAudio sink
- If the speaker is off or out of range, audio falls back to HDMI

### mpv audio routing
- mpv is configured with `--audio-device=pulse` so all audio goes through PulseAudio
- PulseAudio's default sink is the Bluetooth speaker
- For video, mpv sends video to HDMI framebuffer and audio to PulseAudio (BT speaker)
- For audio-only, mpv just outputs to PulseAudio (BT speaker)

### Pairing flow (one-time, via web UI)
1. Parent opens Settings page
2. Puts Bluetooth speaker in pairing mode
3. Clicks "Scan for speakers" in the web UI
4. Selects the speaker from discovered devices
5. System pairs, trusts, and saves the MAC address

---

## 6. Figurines

Each figurine is a small 3D-printed character or object that the child places on top
of the box to trigger playback. Figurines are the primary interface — no screens or
menus for the child.

### 6.1 Construction

Each figurine contains two embedded components:

```
    ┌─────────┐
    │  ╭───╮  │  ← 3D-printed shell (two halves or cavity)
    │  │   │  │
    │  ╰───╯  │
    │ ┌─────┐ │
    │ │RFID │ │  ← MIFARE 13.56 MHz coin sticker tag (25mm)
    │ │stickr│ │    glued flat inside the base
    │ └─────┘ │
    │ (•) (•) │  ← 2x neodymium disc magnets (6x3mm)
    │         │    fully enclosed inside printed base
    └─────────┘
```

- **RFID sticker tag:** 25mm diameter coin-type, self-adhesive, stuck to the inside
  floor of the figurine. Must sit within ~25mm of the MFRC522 antenna (through the
  box top wall) for reliable reads.
- **Magnets:** 2x neodymium disc magnets (6mm diameter x 3mm thick) fully enclosed
  inside the printed base using a pause-and-insert technique: the print is paused at
  the correct Z height, magnets are dropped into the cavities, and printing resumes
  to seal them with solid layers above. This makes magnets impossible to remove —
  critical for toddler safety. Polarity must match the box magnets (attract, not repel).

### 6.2 Design Guidelines

- **Size:** 40-60mm tall, 30-40mm base diameter — easy for toddler hands to grab
- **Base:** Flat, ~5mm thick, with printed cavities for magnets and space for RFID tag
- **Shell:** Print in two halves (top + base) that snap or glue together after
  inserting the tag and magnets. Or print with a cavity and a press-fit lid.
- **Style:** Simple, recognizable shapes — animals, vehicles, characters.
  Minimal overhangs so they print without supports.
- **Material:** PLA or PETG, bright colors. Bambu Lab P2S supports multi-color
  with the AMS, so figurines can be printed in multiple colors in one go.
- **Safety:** No small detachable parts. Magnets are fully enclosed inside the
  printed base using pause-and-insert (sealed with solid layers above and below).
  A toddler cannot access or remove them.

### 6.3 Figurine Base (standard across all figurines)

All figurines share the same base dimensions so they align with the box magnets:

```
        Top view of figurine base
        ┌───────────────────┐
        │                   │
        │   (•)       (•)   │  ← magnet pockets (6mm dia, 3mm deep)
        │                   │     20mm apart center-to-center
        │   ┌───────────┐   │
        │   │   RFID    │   │  ← RFID sticker (25mm coin)
        │   │  sticker  │   │    centered
        │   └───────────┘   │
        │                   │
        └───────────────────┘
              35mm wide
```

### 6.4 RFID Read Distance

- MFRC522 typical read range: **~30mm** through air
- The signal must pass through: box top wall (~3mm) + figurine base (~5mm) = ~8mm
- This leaves ~22mm margin — more than enough for reliable reads
- The RFID antenna on the MFRC522 board is positioned directly under the box top
  surface, centered on the magnet alignment point

---

## 7. Enclosure (3D Printed — OpenSCAD)

The enclosure is defined as parametric OpenSCAD code, generated by Claude Code.
OpenSCAD renders the model to STL, which is then sliced in Bambu Studio.

Design goals for the Bambu Lab P2S printed enclosure:

- **Toddler-proof:** Rounded corners, thick walls (3mm+), no small parts
- **Top surface:** Flat RFID scan area with a printed visual marker (circle, paw print,
  star, etc.) showing where to place figurines. Magnets embedded under the surface
  to hold figurines in place.
- **Front:** 2 large buttons (play/pause, stop), LED strip window
- **Side:** Micro SD card slot access (behind a cover)
- **Back:** Mini HDMI port access, 2x micro USB (OTG + power)
- **Internal:** Snap-fit or screw mount points for Pi, RFID module, LED strip
- **LED window:** Translucent or open slot for WS2812 strip to shine through
- **No speaker grille needed** — audio goes to external Bluetooth speaker
- **Size:** Approx. 150mm x 110mm x 75mm (fits breadboard, fits on P2S build plate)
- **Print:** PETG or PLA+, no supports needed if designed with flat faces

### 7.1 Box Top — Magnet and RFID Layout

```
    Cross-section of box top (figurine placed)

    ══════════════════════════  ← figurine base (6mm)
    │(•)│    │RFID stickr│ │(•)│  magnets fully enclosed inside base
    ──────────────────────────
    ┃         3mm wall        ┃  ← box top wall
    ┃  (•)  ┌──────────┐ (•) ┃  ← box magnets fully enclosed in lid
    ┃       │ MFRC522  │     ┃  ← RFID module mounted directly under the wall
    ┃       │ antenna  │     ┃
    ┃       └──────────┘     ┃
```

- **Box magnets:** 2x neodymium disc magnets (6x3mm) fully enclosed in the box lid
  using pause-and-insert during printing (same technique as figurine base).
  Lid prints upside-down; magnets are inserted at the correct pause height.
- **Magnet alignment:** Figurine magnets and box magnets are 20mm apart
  center-to-center. This creates a satisfying snap when the figurine is placed and
  ensures consistent positioning over the RFID antenna.
- **MFRC522 mounting:** The module is mounted face-up directly under the top wall,
  centered between the magnets. The antenna coil faces upward toward the figurine.

### 7.2 Enclosure Sketch

```
        ┌──────────────────────┐
       ╱   ★ place figurine ★ ╱│  ← top: magnet snap zone + RFID reader
      ╱     (•)    (•)       ╱ │     underneath
     ┌──────────────────────┐  │
     │                      │  │
     │    ┌──┐      ┌──┐    │  │  ← 2 chunky buttons
     │    │▶║│      │ ◼│    │  │    (play/pause, stop)
     │    └──┘      └──┘    │  │
     │                      │  │
     │ ════════════════════ │ ╱   ← LED strip window
     └──────────────────────┘╱
```

---

## 8. Parent Web UI

Accessible at `http://babybox.local` (mDNS) from any device on the same WiFi.

### Pages:

1. **Dashboard** — now playing, today's video count/limit, quick stats
2. **Media Library** — list all downloaded media (with thumbnails), add new from
   YouTube, delete. Shows download progress for pending items.
3. **Figurine Manager** — place a figurine on the box → assign to media, label it,
   list all mappings
4. **Settings** — video limits, Bluetooth speaker pairing, WiFi config, shutdown/reboot
5. **History** — playback log, daily/weekly charts

### Add Media Flow (YouTube download):
1. Parent opens Media Library page
2. Pastes a YouTube URL
3. Chooses save mode: **Video** (MP4) or **Audio only** (MP3)
4. Clicks "Download"
5. System uses `yt-dlp` to download in the background:
   - **Video mode:** downloads best quality MP4 (up to 1080p) + thumbnail
   - **Audio mode:** extracts audio track, converts to MP3 + thumbnail
6. Progress bar shows download status
7. Once complete, media appears in the library with title and thumbnail
   auto-populated from YouTube metadata

### Figurine Assignment Flow:
1. Parent opens Figurine Manager page
2. Clicks "Register New Figurine"
3. Places figurine on the box
4. Web UI shows the detected RFID tag UID
5. Parent selects a media file from the library (shows thumbnails)
6. Parent gives figurine a friendly name (e.g., "Blue dinosaur")
7. Saves → figurine is now mapped

---

## 9. Project Structure

```
BabyBox/
├── SPEC.md
├── README.md
├── hardware/
│   ├── wiring-diagram.md         # Fritzing or text-based wiring guide
│   ├── enclosure/                # Box OpenSCAD source + exported STL
│   │   ├── babybox-case.scad     # Parametric enclosure (Claude Code generated)
│   │   ├── babybox-lid.scad      # Lid with magnet pockets + RFID mount
│   │   └── README.md             # How to render and print
│   └── figurines/                # Figurine 3D print files
│       ├── base-template.scad    # Parametric base (Claude Code generated)
│       ├── dino.stl              # Example figurine (Meshy AI generated)
│       └── bunny.stl             # Example figurine (Meshy AI generated)
├── software/
│   ├── requirements.txt
│   ├── config.py                 # Paths, GPIO pins, defaults
│   ├── main.py                   # Entry point, orchestrates everything
│   ├── rfid.py                   # RFID listener (MFRC522)
│   ├── player.py                 # Media playback (mpv wrapper)
│   ├── downloader.py             # YouTube download (yt-dlp wrapper)
│   ├── bluetooth.py              # Bluetooth speaker connection mgmt
│   ├── leds.py                   # WS2812 LED animations
│   ├── buzzer.py                 # Buzzer feedback patterns
│   ├── buttons.py                # Physical button handler
│   ├── limits.py                 # Video limit enforcement
│   ├── db.py                     # SQLite database layer
│   ├── models.py                 # Data classes
│   └── web/
│       ├── app.py                # Flask app
│       ├── templates/
│       │   ├── base.html
│       │   ├── dashboard.html
│       │   ├── library.html
│       │   ├── figurines.html
│       │   ├── settings.html
│       │   └── history.html
│       └── static/
│           ├── style.css
│           └── app.js
├── scripts/
│   ├── setup.sh                  # System setup (deps, SPI, Bluetooth, etc.)
│   ├── babybox.service           # systemd unit file
│   └── bt-connect.service        # systemd unit for Bluetooth auto-connect
└── media/                        # Downloaded content lives here
    ├── audio/                    # MP3 files (audio-only downloads)
    ├── video/                    # MP4 files (video downloads)
    └── thumbnails/               # YouTube thumbnails for the web UI
```

---

## 10. Implementation Phases

### Phase 1 — Core MVP
- YouTube download via `yt-dlp` (video as MP4, audio-only as MP3)
- RFID scanning → media playback (video via HDMI, audio via Bluetooth speaker)
- Bluetooth speaker pairing and auto-connect on boot
- SQLite database with figurine-to-media mapping
- Playback lock (ignore figurines while playing, wait for content to finish)
- Basic CLI tool to register figurines
- Auto-start on boot

### Phase 2 — Physical Controls & Feedback
- Button handling (play/pause, stop)
- WS2812 LED animations (scan feedback, now playing, idle pulse)
- Buzzer feedback (scan confirm, error, limit reached)

### Phase 3 — Parental Controls
- Video limit enforcement (count + time based)
- Web UI: YouTube download (paste URL, pick audio/video), figurine management, settings
- Bluetooth speaker management in web UI
- Playback history and stats

### Phase 4 — Enclosure & Figurines
- OpenSCAD enclosure (parametric, generated by Claude Code, rendered to STL)
- OpenSCAD figurine base template (parametric, generated by Claude Code)
- First set of figurine tops (3-5 designs via Meshy AI, merged with base in Blender)
- Magnet polarity testing and assembly
- Final testing with actual toddler

---

## 11. Key Design Decisions

| Decision                  | Choice              | Rationale                                  |
|---------------------------|---------------------|--------------------------------------------|
| Language                  | Python              | Best GPIO/hardware library support         |
| Content source            | YouTube (via yt-dlp) | Vast library, parent curates what to download |
| Media player              | mpv                 | HW-accelerated, scriptable, split A/V out  |
| Database                  | SQLite              | Zero-config, single file, durable          |
| Web framework             | Flask               | Minimal, well-known, fits the Pi           |
| LED driver                | rpi_ws281x          | Native, well-supported                     |
| RFID protocol             | MIFARE 13.56 MHz    | What MFRC522 supports                      |
| RFID form factor          | Coin sticker in figurine | Invisible to child, embedded in toy    |
| Figurine attachment       | Neodymium magnets   | Satisfying snap, consistent RFID alignment |
| Video output              | HDMI to TV          | Native, zero config, full resolution       |
| Audio output              | Bluetooth speaker   | Portable, adjustable, near the child       |
| Audio routing             | PulseAudio          | Built-in Bluetooth A2DP sink support       |
| Playback lock             | Ignore during play  | Prevents toddler content-hopping           |
| Enclosure CAD             | OpenSCAD (AI-generated) | Code-based = AI can write it, parametric |
| Enclosure material        | PETG                | Tougher than PLA, toddler-safe             |
