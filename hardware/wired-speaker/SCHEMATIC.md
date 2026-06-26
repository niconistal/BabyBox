# BabyBox Variant — Wired Speaker (IKEA KALLSUP donor)

A variation of the standard BabyBox build that replaces the Bluetooth speaker with
a **wired speaker driver salvaged from an IKEA KALLSUP** ($10 Bluetooth cube),
driven by a **MAX98357A I2S mono class-D amplifier** on the Pi.

Why wire it instead of using KALLSUP's own Bluetooth?

- No pairing, no reconnect logic, no audio dropouts — audio works the instant the Pi boots
- No battery to charge (or to age inside a toddler's toy)
- Zero Bluetooth latency — button feedback beeps and playback start are instant
- The speaker lives *inside* the BabyBox enclosure: one box, one power cable

---

## 1. Bill of Materials (delta vs. SPEC.md §2.1)

| Change | Component                                   | Est. Cost |
|--------|---------------------------------------------|-----------|
| −      | Bluetooth speaker                           | −$0–20    |
| +      | IKEA KALLSUP (donor — driver only)          | ~$10      |
| +      | MAX98357A I2S amp breakout (Adafruit 3006 or clone) | ~$3–6 |
| +      | 24 AWG twisted-pair speaker wire (~20 cm)   | —         |

Everything else (Pi Zero 2 W, MFRC522, LEDs, buttons, buzzer, PSU) is unchanged.
The 5V 3A supply has ample headroom for the amp (≤ ~0.7 A peak at full volume).

### Why the MAX98357A?

- 3.2 W into 4 Ω at 5 V — an exact match for the KALLSUP's 3 W single driver
- I2S digital input: no DAC needed, no analog ground-loop hum, and the
  Pi Zero 2 W has no analog audio jack anyway
- Mono output — correct for the KALLSUP's single full-range driver
  (it mixes (L+R)/2 by default, so stereo media plays fully)

---

## 2. KALLSUP Teardown

1. Peel the four rubber feet and remove the screws beneath them, then split the
   cube (some seams are clipped — pry gently with a spudger).
2. Photograph the board before desoldering anything.
3. **Desolder the speaker driver's two wires** from the Bluetooth PCB
   (or cut them as long as possible if you'd rather not desolder).
4. **Remove the battery**: it's a LiPo pouch/cell. Tape over its leads
   immediately and take it to battery recycling. Never bin a LiPo.
5. The Bluetooth PCB, antenna and buttons are not used — set them aside.
6. Keep: the **driver** (and optionally the cube shell + grille as an external
   speaker pod, if you prefer not to mount the driver inside the BabyBox case).

### Verify the driver before wiring

Measure DC resistance across the driver terminals with a multimeter:

| Reading      | Nominal impedance | MAX98357A output @ 5 V | OK?  |
|--------------|-------------------|------------------------|------|
| ~3.2–3.6 Ω   | 4 Ω (expected)    | up to 3.2 W            | ✅   |
| ~6.4–7.2 Ω   | 8 Ω               | up to 1.8 W            | ✅ (slightly quieter) |
| < 3 Ω        | — (suspect)       | —                      | ❌ do not connect |

Note the polarity markings (+ / −) on the driver terminals — keep them for step 4.

---

## 3. GPIO Pin Assignment (changes vs. SPEC.md §2.4)

I2S on the Pi is fixed to GPIO 18/19/21, and GPIO 18 currently drives the
WS2812 strip — so the strip moves to GPIO 13 (PWM1, fully supported by
`rpi_ws281x`).

```
Pi Zero 2 W GPIO Layout — wired-speaker variant
================================================

MFRC522 (SPI0):                          (unchanged)
  SDA  → GPIO 8  (CE0)
  SCK  → GPIO 11 (SCLK)
  MOSI → GPIO 10 (MOSI)
  MISO → GPIO 9  (MISO)
  RST  → GPIO 25
  3.3V → 3.3V
  GND  → GND

MAX98357A (I2S):                         (NEW)
  BCLK → GPIO 18 (PCM_CLK)   physical pin 12
  LRC  → GPIO 19 (PCM_FS)    physical pin 35
  DIN  → GPIO 21 (PCM_DOUT)  physical pin 40
  VIN  → 5V                  physical pin 2 or 4
  GND  → GND
  GAIN → unconnected         (= 9 dB default; see §5)
  SD   → unconnected         (= (L+R)/2 mono mix on Adafruit breakout)

WS2812 LED Strip:                        (MOVED 18 → 13)
  DIN  → GPIO 13 (PWM1)
  5V   → 5V
  GND  → GND

Buttons (active low, internal pull-up):  (unchanged)
  Play/Pause → GPIO 17
  Stop       → GPIO 27

Passive Buzzer:                          (unchanged pin, software PWM)
  Signal → GPIO 12
  GND    → GND
```

> **PWM note:** `rpi_ws281x` claims the hardware PWM block via DMA when driving
> the strip on GPIO 13. Drive the buzzer with **software PWM** (gpiozero's
> default `TonalBuzzer`/`PWMOutputDevice`) — perfectly adequate for beeps.

---

## 4. Schematic

```
                         ┌────────────────────────┐
                         │   Raspberry Pi Zero 2 W│
                         │                        │
   5V PSU ──────────────►│ 5V          HDMI ──────┼────► TV (video only)
   (5V 3A micro-USB)     │                        │
                         │ GPIO18 (PCM_CLK) ──────┼──┐
                         │ GPIO19 (PCM_FS)  ──────┼──┤
                         │ GPIO21 (PCM_DOUT)──────┼──┤
                         │ 5V ────────────────────┼──┤
                         │ GND ───────────────────┼──┤
                         └────────────────────────┘  │
                                                     ▼
                                        ┌─────────────────────┐
                                        │      MAX98357A      │
                                        │  BCLK LRC DIN VIN GND│
                                        │                     │
                                        │   GAIN ─ n/c (9 dB) │
                                        │   SD ─── n/c (mono) │
                                        │                     │
                                        │      +  ▒▒  −       │   twisted pair,
                                        └──────┬──────┬───────┘   24 AWG, ≤20 cm
                                               │      │
                                               +      −
                                        ┌──────┴──────┴───────┐
                                        │  KALLSUP driver     │
                                        │  1.8" full-range    │
                                        │  4 Ω · 3 W (verify) │
                                        └─────────────────────┘
```

**Wiring rules:**

- Amp **+** → driver **+**, amp **−** → driver **−**. Polarity only matters for
  multi-speaker setups, but keep it correct anyway.
- The amp output is a **bridge-tied load (BTL)**: never connect either speaker
  terminal to GND, and never share the speaker wires with other grounds.
- Twist the speaker pair and keep it short to keep class-D switching noise
  away from the RFID antenna. Route it away from the MFRC522.

---

## 5. Gain setting (optional)

Default (GAIN unconnected) is 9 dB, which is right for this driver. To change:

| GAIN pin              | Gain  |
|-----------------------|-------|
| → GND via 100 kΩ      | 15 dB |
| → GND directly        | 12 dB |
| unconnected           | 9 dB  |
| → VIN directly        | 6 dB  |
| → VIN via 100 kΩ      | 3 dB  |

For a toddler device, consider hard-limiting loudness with **6 dB** (GAIN → VIN)
and relying on software volume below that ceiling.

---

## 6. Software changes

1. **Enable the I2S DAC** in `/boot/firmware/config.txt`:

   ```ini
   dtoverlay=max98357a
   # (or: dtoverlay=hifiberry-dac — same I2S setup, works with clones)
   ```

2. **Audio sink**: the amp appears as an ALSA card. Make it the default
   PulseAudio sink instead of the Bluetooth A2DP sink. The HDMI sink stays
   video-only as before. mpv config is unchanged (`--audio-device=pulse`).

3. **Disable Bluetooth speaker logic** (SPEC.md §5): set `bt_speaker_mac = ""`
   and skip pairing/reconnect at boot. The HDMI audio fallback path is no
   longer needed — wired audio cannot go out of range.

4. **Volume**: the MAX98357A has no hardware volume control. Set the output
   level in software (PulseAudio/ALSA) and expose it in the parent web UI;
   the GAIN ceiling from §5 guarantees a maximum loudness regardless.

5. **LED strip pin**: change the WS2812 GPIO from 18 to **13** in the app
   config, and ensure the buzzer uses software PWM.
