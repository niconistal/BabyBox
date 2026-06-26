# BabyBox v3 "Tower" — build guide

Upright tower enclosure drawn from the paper sketches in `../sketches/`.
Soldered build (no breadboard), heat-set inserts throughout, MX-switch buttons
with big round custom keycaps, and a WS2812B LED **halo** ring around the
figurine podium.

Footprint **84 × 84 mm**, ~**95 mm** tall (plus the figurine on top).

## Parts & how to print

Each part is one `render_part` of `babybox-case-v3.scad` (keycaps are in
`keycaps.scad`). Render: `openscad -o part.stl -D 'render_part="body"' babybox-case-v3.scad`

| Part | `render_part` | Filament | Print orientation | Supports |
|------|---------------|----------|-------------------|----------|
| Bottom tray | `tray` | body color | flat, as drawn | none |
| Body tube | `body` | body color | either open end on the bed | none |
| Top plate | `top` | accent color | **top face DOWN** on the bed | none |
| Center lid | `lid` | accent color | right-side up; **pause** to drop magnets | none |
| Diffuser ring | `diffuser` | **translucent / natural** (it glows) | flat | none |
| Keycap ×2 | `play`, `stop` (in `keycaps.scad`) | accent color | **top face DOWN** | none |

Two-tone: print body color (tray + body) and accent color (top plate, lid,
keycaps) separately; the diffuser ring in a translucent filament.

### Pause-and-insert magnets (center lid)
Print the lid right-side up and pause at the height OpenSCAD echoes
(`Z = 4.2 mm`), drop in the two **6 × 3 mm** neodymium magnets (mind polarity
vs. the figurines!), then resume — the ceiling layers seal them in.

## Hardware

- **Heat-set inserts** (brass, melted in with a soldering iron):
  - **M3 ×8** — 4 in the body column tops, 4 in the column bottoms
  - **M2.5 ×4** — Pi Zero 2 W standoffs on the tray
  - **M2 ×4** — MFRC522 standoffs under the top plate
  - Pilot-hole diameters are in `common-params.scad` (`*_insert_hole_dia`);
    nudge them ±0.1 mm to suit your specific inserts.
- **Screws:** M3 (tray→body, top plate→body), M2.5 (Pi), M2 (MFRC522).
- **2× MX (Cherry-compatible) keyswitches** — they snap into the 14 × 14 mm
  plate cut-outs (the top plate leaves a 1.5 mm clip shelf).
- **SunFounder 8× WS2812B** 60/m flexible strip (10 mm wide, 2 mm thick).

## Assembly order

1. **Tray:** heat-set the 4× M2.5 inserts, screw the Pi Zero 2 W down, press
   the buzzer into its cradle.
2. **Body:** heat-set the 8× M3 inserts (4 top, 4 bottom of the columns).
3. **Top plate:**
   - heat-set the 4× M2 inserts, mount the MFRC522 **antenna-up** (header pins
     point down into the tower).
   - snap the 2 MX switches into the button cut-outs.
   - wrap the LED strip around the 40 mm hub (adhesive backing sticks to it),
     feed the 3 leads down through the wire notch.
   - drop the **diffuser ring** over the strip onto its ledge.
   - press the **center lid** into the figurine well, over the RFID reader.
4. **Wire everything to the Pi header** (see `../../SPEC.md` §2.4 for pins —
   LED→GPIO18, buttons→GPIO17/27 + GND, buzzer→GPIO12, MFRC522→SPI/CE0).
   Leave a small service loop so the top plate can lift off.
5. **Close it up:** screw the top plate down into the body column tops, set the
   body on the tray and screw it up from underneath, add silicone bumper feet.
6. **Press the round keycaps** onto the MX stems.

## Read-distance sanity

RFID stack from antenna to figurine tag ≈ **14 mm** (top-plate floor + hub +
center lid), well under the MFRC522's ~30 mm range. The magnets in the center
lid and figurine base are ~20 mm apart center-to-center for a clean snap.

## Tuning (all in `common-params.scad` / the case file header)

- Caps loose/tight on the switches → `mx_stem_arm_t` ∓ 0.05.
- Different LED strip → set `led_pitch` / `led_count`; the ring auto-resizes
  and `hub_od` can follow (`led_ring_mid_dia` is derived).
- Bigger/smaller round buttons → `mx_keycap_round_dia` (asserts keep them clear
  of the halo and each other).
