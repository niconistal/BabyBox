# BabyBox v3 — build guide

Compact box drawn from the paper sketches in `../sketches/`. Soldered build (no
breadboard), brass heat-set inserts throughout, two MX-switch buttons with big
round custom keycaps, and a **raised, sealed WS2812B LED ring** around a
**recessed hole** the figurine drops straight into — with the RFID reader
mounted flush right beneath the hole floor so it reads reliably.

Footprint **90 × 90 mm**, body only **~47 mm** tall (the ring stands ~11 mm
proud; the figurine sticks up out of the hole).

## Parts & how to print

Each part is one `render_part` of `babybox-case-v3.scad` (keycaps are in
`keycaps.scad`). Render: `openscad -o part.stl -D 'render_part="body"' babybox-case-v3.scad`

| Part | `render_part` | Filament | Print orientation | Supports |
|------|---------------|----------|-------------------|----------|
| Bottom tray | `tray` | body color | flat, as drawn | none |
| Body tube | `body` | body color | either open end on the bed | none |
| Top plate | `top` | accent color | **right-side up** (underside on the bed); **pause** to drop the ring magnets | none |
| Diffuser ring | `diffuser` | **translucent / natural** (it glows) | flat | none |
| Keycap ×2 | `play`, `stop` (in `keycaps.scad`) | accent color | **top face DOWN** | none |

Two-tone: print body color (tray + body) and accent color (top plate, keycaps)
separately; the diffuser ring in a translucent filament. Figurines come from
`../figurines/`.

### Pause-and-insert magnets (top plate)
Print the top plate right-side up and pause at the height OpenSCAD echoes
(`Z = 4.2 mm`), drop the two **6 × 3 mm** neodymium magnets into the hole-floor
pockets (mind polarity vs. the figurines!), then resume — the floor layers seal
them in, under the figurine and over the RFID.

## Hardware

- **Heat-set inserts** (brass, melted in with a soldering iron):
  - **M3 ×8** — 4 in the body column tops, 4 in the column bottoms
  - **M2.5 ×4** — Pi Zero 2 W standoffs on the tray
  - **M2 ×4** — MFRC522, screwed flush to the top-plate underside
  - Pilot-hole diameters are in `common-params.scad` (`*_insert_hole_dia`);
    nudge them ±0.1 mm to suit your specific inserts.
- **Screws:** M3 (tray→body, top plate→body), M2.5 (Pi), M2 (MFRC522).
- **2× MX (Cherry-compatible) keyswitches** — snap into the 14 × 14 mm plate
  cut-outs (the top plate leaves a 1.5 mm clip shelf).
- **SunFounder 8× WS2812B** 60/m flexible strip (10 mm wide, 2 mm thick).

## Assembly order

1. **Tray:** heat-set the 4× M2.5 inserts, screw the Pi Zero 2 W down, press
   the buzzer into its cradle.
2. **Body:** heat-set the 8× M3 inserts (4 top, 4 bottom of the columns).
3. **Top plate:**
   - heat-set the 4× M2 inserts; screw the MFRC522 **flush** to the underside,
     **antenna-up** under the hole floor (header/pads face down into the body).
   - snap the 2 MX switches into the button cut-outs.
   - wrap the LED strip around the hole wall (adhesive backing sticks to it,
     LEDs facing out), feed the 3 leads down through the wire notch.
   - **glue the diffuser ring** down over the strip — it caps the top and outer
     face so the strip is fully sealed (nothing for little fingers to pick).
4. **Wire everything to the Pi header** (see `../../SPEC.md` §2.4 for pins —
   LED→GPIO18, buttons→GPIO17/27 + GND, buzzer→GPIO12, MFRC522→SPI/CE0).
   Leave a small service loop so the top plate can lift off.
5. **Close it up:** screw the top plate down into the body column tops, set the
   body on the tray and screw it up from underneath, add silicone bumper feet.
6. **Press the round keycaps** onto the MX stems. Drop a figurine into the hole.

## Read-distance sanity

The figurine sits **recessed in the hole**, so its RFID tag ends up only
~**5–7 mm** above the MFRC522 antenna (just the thin hole floor) — well inside
the reader's ~30 mm range. Two **6 × 3 mm** magnets in the hole floor (20 mm
apart) give a gentle snap/hold and align with the figurine-base magnets.

## Tuning (all in `common-params.scad` / the case file header)

- Caps loose/tight on the switches → `mx_stem_arm_t` ∓ 0.05.
- Box too tall/short → `body_h` (currently 32 mm; the assert keeps it tall
  enough for the Pi).
- Different LED strip → set `led_pitch` / `led_count`; the wrap diameter and the
  ring follow `strip_wrap_r` automatically.
- Bigger/smaller round buttons → `mx_keycap_round_dia` (asserts keep them clear
  of the ring and each other).
- Figurine sits too proud/deep → `well_depth`.
