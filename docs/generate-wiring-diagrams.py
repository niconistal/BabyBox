#!/usr/bin/env python3
"""Generate realistic Fritzing-style wiring diagrams for the BabyBox website.

Outputs SVG files into website/images/diagrams/:
  - wiring-stock.svg          : full stock-build wiring overview (Bluetooth audio)
  - wiring-wired-speaker.svg  : wired-speaker variant (KALLSUP driver + MAX98357A)
  - audio-bluetooth.svg       : stock Bluetooth audio option graphic

Run from anywhere:  python3 docs/generate-wiring-diagrams.py
"""

import os

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "website", "images", "diagrams")

FONT = "Inter, -apple-system, 'Segoe UI', sans-serif"
MONO = "'SF Mono', 'Fira Code', monospace"

# Wire colors (match the website legend)
C = {
    "red":    "#D32F2F",   # power (3.3V / 5V)
    "black":  "#37352F",   # GND
    "yellow": "#E0A800",   # SDA / signal
    "orange": "#E07800",   # SCK / BCLK
    "green":  "#2E9E44",   # MOSI / DIN (data)
    "blue":   "#2F5FD0",   # MISO
    "white":  "#E8E8E8",   # RST / LRC
    "teal":   "#26A69A",   # moved-pin highlight
}


def darker(hex_color, f=0.62):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"#{int(r * f):02X}{int(g * f):02X}{int(b * f):02X}"


# ---------------------------------------------------------------- Pi Zero 2 W

PI_W, PI_H = 420, 190
HDR_INSET_X, HDR_Y, HDR_H = 24, 10, 40
HDR_W = PI_W - 2 * HDR_INSET_X
PITCH = HDR_W / 20.0


def pin_local(phys):
    """Local (x, y) of a physical header pin (1..40). Header along top edge.
    Even pins = outer/top row, odd pins = inner/bottom row (SD slot on left)."""
    col = (phys + 1) // 2
    x = HDR_INSET_X + PITCH * (col - 0.5)
    y = HDR_Y + (11 if phys % 2 == 0 else 29)
    return x, y


def pi_zero(ox, oy, used_pins, title="Raspberry Pi Zero 2 W"):
    """Render the Pi at (ox, oy). used_pins: {phys: (color, label)} highlights."""
    s = [f'<g transform="translate({ox},{oy})">']
    # drop shadow + board
    s.append(f'<rect x="3" y="5" width="{PI_W}" height="{PI_H}" rx="14" fill="#000" opacity="0.10"/>')
    s.append(f'<rect width="{PI_W}" height="{PI_H}" rx="14" fill="url(#pcbGreen)" stroke="#1B4D2A" stroke-width="2"/>')
    # mounting holes
    for hx, hy in ((16, 16), (PI_W - 16, 16), (16, PI_H - 16), (PI_W - 16, PI_H - 16)):
        s.append(f'<circle cx="{hx}" cy="{hy}" r="7" fill="#C9A227" stroke="#8C6E14" stroke-width="1.5"/>')
        s.append(f'<circle cx="{hx}" cy="{hy}" r="3.5" fill="#FAF6EC"/>')
    # header block
    s.append(f'<rect x="{HDR_INSET_X - 8}" y="{HDR_Y}" width="{HDR_W + 16}" height="{HDR_H}" rx="4" fill="#1A1A1A"/>')
    for p in range(1, 41):
        x, y = pin_local(p)
        s.append(f'<rect x="{x - 3.2:.1f}" y="{y - 3.2:.1f}" width="6.4" height="6.4" fill="#E6C35C" stroke="#9C7E20" stroke-width="0.8"/>')
    # pin 1 marker (square outline)
    x1, y1 = pin_local(1)
    s.append(f'<rect x="{x1 - 5.6:.1f}" y="{y1 - 5.6:.1f}" width="11.2" height="11.2" fill="none" stroke="#FFF" stroke-width="1.2"/>')
    s.append(f'<text x="{x1 - 12}" y="{y1 + 16}" font-family="{MONO}" font-size="9" fill="#CFE8D5">1</text>')
    x40, y40 = pin_local(40)
    s.append(f'<text x="{x40 + 6}" y="{y40 - 24}" font-family="{MONO}" font-size="9" fill="#CFE8D5">40</text>')
    # SoC + RAM
    s.append(f'<rect x="{PI_W / 2 - 32}" y="92" width="64" height="64" rx="4" fill="#2B2B2B" stroke="#111" stroke-width="1"/>')
    s.append(f'<text x="{PI_W / 2}" y="121" text-anchor="middle" font-family="{MONO}" font-size="8" fill="#888">BCM2710A1</text>')
    s.append(f'<text x="{PI_W / 2}" y="133" text-anchor="middle" font-family="{MONO}" font-size="7" fill="#666">+ 512MB RAM</text>')
    # SD slot (left edge)
    s.append(f'<rect x="-6" y="76" width="46" height="40" rx="3" fill="#9DA5AB" stroke="#6B7176" stroke-width="1.5"/>')
    s.append(f'<text x="18" y="100" text-anchor="middle" font-family="{FONT}" font-size="7.5" fill="#3A3F44" font-weight="600">microSD</text>')
    # camera connector (right edge)
    s.append(f'<rect x="{PI_W - 14}" y="72" width="14" height="48" rx="2" fill="#D8D2C4" stroke="#A89F8C" stroke-width="1"/>')
    # bottom edge ports: mini-HDMI, USB OTG, USB PWR
    for px, pw, lbl in ((96, 64, "mini-HDMI"), (218, 44, "USB (OTG)"), (286, 44, "USB (PWR)")):
        s.append(f'<rect x="{px}" y="{PI_H - 16}" width="{pw}" height="22" rx="3" fill="#AEB6BC" stroke="#787F85" stroke-width="1.5"/>')
        s.append(f'<rect x="{px + 6}" y="{PI_H - 10}" width="{pw - 12}" height="10" rx="2" fill="#42484D"/>')
        s.append(f'<text x="{px + pw / 2}" y="{PI_H + 22}" text-anchor="middle" font-family="{FONT}" font-size="9" fill="#636E72">{lbl}</text>')
    # silk title
    s.append(f'<text x="{PI_W / 2}" y="78" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="#E8F5EC">{title}</text>')
    # used-pin highlights + tiny pin-number flags
    for p, (color, lbl) in used_pins.items():
        x, y = pin_local(p)
        s.append(f'<circle cx="{x}" cy="{y}" r="6.5" fill="none" stroke="{color}" stroke-width="2.5"/>')
        if lbl:
            ly = y - 14 if p % 2 == 0 else y + 18
            anchor_y = ly - 8 if p % 2 == 0 else ly - 8
            s.append(f'<g font-family="{MONO}" font-size="8.5" font-weight="700">'
                     f'<text x="{x}" y="{ly}" text-anchor="middle" fill="#FFF" stroke="#FFF" stroke-width="2.5" paint-order="stroke">{lbl}</text>'
                     f'<text x="{x}" y="{ly}" text-anchor="middle" fill="{darker(color, 0.8)}">{lbl}</text></g>')
    s.append("</g>")
    return "\n".join(s)


def pi_pin(ox, oy, phys):
    x, y = pin_local(phys)
    return ox + x, oy + y


# ------------------------------------------------------------------ Wires

def wire(x1, y1, x2, y2, color, d1="up", d2="down", k=70, label=None, lx=0, ly=0):
    """Curved jumper wire. d1/d2 = direction the wire leaves each endpoint."""
    def ctrl(x, y, d, k):
        return {"up": (x, y - k), "down": (x, y + k), "left": (x - k, y), "right": (x + k, y)}[d]
    c1x, c1y = ctrl(x1, y1, d1, k)
    c2x, c2y = ctrl(x2, y2, d2, k)
    p = f"M {x1:.0f} {y1:.0f} C {c1x:.0f} {c1y:.0f}, {c2x:.0f} {c2y:.0f}, {x2:.0f} {y2:.0f}"
    s = [f'<path d="{p}" fill="none" stroke="{darker(color)}" stroke-width="5.6" stroke-linecap="round" opacity="0.9"/>',
         f'<path d="{p}" fill="none" stroke="{color}" stroke-width="3.4" stroke-linecap="round"/>']
    for ex, ey in ((x1, y1), (x2, y2)):
        s.append(f'<circle cx="{ex:.0f}" cy="{ey:.0f}" r="3.6" fill="#222" stroke="#555" stroke-width="1"/>')
    if label:
        mx = (x1 + 3 * c1x + 3 * c2x + x2) / 8 + lx
        my = (y1 + 3 * c1y + 3 * c2y + y2) / 8 + ly
        s.append(f'<g font-family="{MONO}" font-size="10" font-weight="700">'
                 f'<text x="{mx:.0f}" y="{my:.0f}" text-anchor="middle" fill="#FFF" stroke="#FFF" stroke-width="3.4" paint-order="stroke">{label}</text>'
                 f'<text x="{mx:.0f}" y="{my:.0f}" text-anchor="middle" fill="{darker(color, 0.75)}">{label}</text></g>')
    return "\n".join(s)


# ------------------------------------------------------------- Components

def mfrc522(ox, oy):
    """MFRC522 board 200x132, 8-pin header along the BOTTOM edge.
    Returns (svg, {name: (x, y)}) pin coords (global)."""
    w, h = 200, 132
    s = [f'<g transform="translate({ox},{oy})">']
    s.append(f'<rect x="3" y="5" width="{w}" height="{h}" rx="10" fill="#000" opacity="0.10"/>')
    s.append(f'<rect width="{w}" height="{h}" rx="10" fill="url(#pcbBlue)" stroke="#0D3A78" stroke-width="2"/>')
    # antenna coil traces
    for i, r in enumerate((10, 17, 24)):
        s.append(f'<rect x="{r}" y="{r}" width="{w - 2 * r}" height="{h - 2 * r - 14}" rx="8" fill="none" stroke="#7FB3E8" stroke-width="2.2" opacity="{0.85 - i * 0.2}"/>')
    # chip
    s.append(f'<rect x="{w / 2 - 22}" y="{h / 2 - 24}" width="44" height="34" rx="3" fill="#1E1E1E" stroke="#000" stroke-width="1"/>')
    s.append(f'<text x="{w / 2}" y="{h / 2 - 4}" text-anchor="middle" font-family="{MONO}" font-size="7.5" fill="#999">MFRC522</text>')
    s.append(f'<text x="{w / 2}" y="36" text-anchor="middle" font-family="{FONT}" font-size="11" font-weight="700" fill="#D8E9FB">RFID-RC522</text>')
    # 8-pin header on bottom edge
    names = ["SDA", "SCK", "MOSI", "MISO", "IRQ", "GND", "RST", "3.3V"]
    pins = {}
    px0, ppitch = 28, (w - 56) / 7.0
    s.append(f'<rect x="{px0 - 12}" y="{h - 12}" width="{(w - 56) + 24}" height="12" rx="2" fill="#1A1A1A"/>')
    for i, n in enumerate(names):
        x = px0 + i * ppitch
        s.append(f'<rect x="{x - 2.6:.1f}" y="{h - 9}" width="5.2" height="7" fill="#E6C35C"/>')
        s.append(f'<text x="{x:.1f}" y="{h - 17}" text-anchor="middle" font-family="{MONO}" font-size="7.5" fill="#BBD8F5" transform="rotate(-90 {x:.1f} {h - 17})">{n}</text>')
        pins[n] = (ox + x, oy + h)
    s.append("</g>")
    return "\n".join(s), pins


def ws2812(ox, oy):
    """8-LED strip 230x40, pads on LEFT edge (5V, DIN, GND top to bottom)."""
    w, h = 230, 40
    led_colors = ["#FF6B6B", "#FFB84D", "#FFE66D", "#6BCB77", "#4ECDC4", "#6C8EFF", "#9B6BFF", "#FF6BD6"]
    s = [f'<g transform="translate({ox},{oy})">']
    s.append(f'<rect x="3" y="4" width="{w}" height="{h}" rx="6" fill="#000" opacity="0.10"/>')
    s.append(f'<rect width="{w}" height="{h}" rx="6" fill="#FAFAF5" stroke="#C9C4B8" stroke-width="2"/>')
    pins = {}
    for i, n in enumerate(["5V", "DIN", "GND"]):
        y = 8 + i * 12
        s.append(f'<rect x="-6" y="{y - 3}" width="10" height="6" rx="1.5" fill="#E6C35C" stroke="#9C7E20" stroke-width="0.8"/>')
        s.append(f'<text x="10" y="{y + 3}" font-family="{MONO}" font-size="7.5" fill="#8A8474">{n}</text>')
        pins[n] = (ox - 6, oy + y)
    for i in range(8):
        x = 38 + i * 24.5
        s.append(f'<rect x="{x}" y="{h / 2 - 9}" width="18" height="18" rx="2" fill="#FFFDF2" stroke="#C9C4B8" stroke-width="1.2"/>')
        s.append(f'<circle cx="{x + 9}" cy="{h / 2}" r="6" fill="{led_colors[i]}" opacity="0.85"/>')
        s.append(f'<circle cx="{x + 9}" cy="{h / 2}" r="2.4" fill="#FFF" opacity="0.9"/>')
    s.append(f'<text x="{w / 2 + 10}" y="-8" text-anchor="middle" font-family="{FONT}" font-size="11" font-weight="700" fill="#5A5346">WS2812 LED strip (x8)</text>')
    s.append("</g>")
    return "\n".join(s), pins


def tact_button(ox, oy, cap_color, glyph):
    """6x6mm tactile button, 44px body. Two wire legs on bottom: (sig, gnd)."""
    s = [f'<g transform="translate({ox},{oy})">']
    s.append(f'<rect x="2" y="3" width="44" height="44" rx="6" fill="#000" opacity="0.10"/>')
    s.append('<rect width="44" height="44" rx="6" fill="#C7CCD1" stroke="#8E959B" stroke-width="2"/>')
    for lx, ly in ((6, 6), (38, 6), (6, 38), (38, 38)):
        s.append(f'<circle cx="{lx}" cy="{ly}" r="2.6" fill="#8E959B"/>')
    s.append(f'<circle cx="22" cy="22" r="14" fill="{cap_color}" stroke="{darker(cap_color)}" stroke-width="2"/>')
    s.append(f'<text x="22" y="27" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#FFF" font-weight="700">{glyph}</text>')
    s.append("</g>")
    return "\n".join(s), {"sig": (ox + 10, oy + 44), "gnd": (ox + 34, oy + 44)}


def buzzer(ox, oy):
    """Passive buzzer, r=26 disc. Legs bottom: (sig, gnd)."""
    s = [f'<g transform="translate({ox},{oy})">']
    s.append('<circle cx="2" cy="3" r="27" fill="#000" opacity="0.10"/>')
    s.append('<circle r="27" fill="#1F1F1F" stroke="#000" stroke-width="2"/>')
    s.append('<circle r="20" fill="none" stroke="#3A3A3A" stroke-width="1.5"/>')
    s.append('<circle r="4.5" fill="#0A0A0A" stroke="#444" stroke-width="1"/>')
    s.append(f'<text x="0" y="-33" text-anchor="middle" font-family="{FONT}" font-size="11" font-weight="700" fill="#5A5346">Passive buzzer</text>')
    s.append(f'<text x="-14" y="16" font-family="{MONO}" font-size="9" fill="#BBB">+</text>')
    s.append("</g>")
    return "\n".join(s), {"sig": (ox - 9, oy + 25), "gnd": (ox + 9, oy + 25)}


def max98357a(ox, oy):
    """MAX98357A I2S amp breakout 180x120. Bottom header: LRC BCLK DIN GAIN SD GND Vin.
    Top screw terminal: speaker - +."""
    w, h = 180, 120
    s = [f'<g transform="translate({ox},{oy})">']
    s.append(f'<rect x="3" y="5" width="{w}" height="{h}" rx="10" fill="#000" opacity="0.10"/>')
    s.append(f'<rect width="{w}" height="{h}" rx="10" fill="url(#pcbBlue)" stroke="#0D3A78" stroke-width="2"/>')
    # screw terminal block (top edge)
    s.append(f'<rect x="{w / 2 - 34}" y="-16" width="68" height="34" rx="4" fill="#3BA55D" stroke="#1F7A3C" stroke-width="2"/>')
    pins = {}
    for i, n in enumerate(["-", "+"]):
        x = w / 2 - 16 + i * 32
        s.append(f'<circle cx="{x}" cy="1" r="8" fill="#D9DEE2" stroke="#7C8489" stroke-width="1.5"/>')
        s.append(f'<line x1="{x - 4}" y1="1" x2="{x + 4}" y2="1" stroke="#7C8489" stroke-width="2"/>')
        s.append(f'<text x="{x}" y="30" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" fill="#D8E9FB">{n}</text>')
        pins["spk" + n] = (ox + x, oy - 16)
    s.append(f'<text x="{w / 2}" y="52" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="#D8E9FB">MAX98357A</text>')
    s.append(f'<text x="{w / 2}" y="66" text-anchor="middle" font-family="{FONT}" font-size="8.5" fill="#9FC4EE">I2S 3W class-D amplifier</text>')
    s.append(f'<rect x="{w / 2 - 14}" y="72" width="28" height="20" rx="2" fill="#1E1E1E" stroke="#000"/>')
    # bottom header
    names = ["LRC", "BCLK", "DIN", "GAIN", "SD", "GND", "Vin"]
    px0, ppitch = 22, (w - 44) / 6.0
    s.append(f'<rect x="{px0 - 11}" y="{h - 12}" width="{(w - 44) + 22}" height="12" rx="2" fill="#1A1A1A"/>')
    for i, n in enumerate(names):
        x = px0 + i * ppitch
        s.append(f'<rect x="{x - 2.6:.1f}" y="{h - 9}" width="5.2" height="7" fill="#E6C35C"/>')
        s.append(f'<text x="{x:.1f}" y="{h - 17}" text-anchor="middle" font-family="{MONO}" font-size="7.5" fill="#BBD8F5" transform="rotate(-90 {x:.1f} {h - 17})">{n}</text>')
        pins[n] = (ox + x, oy + h)
    s.append("</g>")
    return "\n".join(s), pins


def speaker_driver(ox, oy, r=78):
    """Salvaged KALLSUP driver, front view. Terminals on left edge: (+, -)."""
    s = [f'<g transform="translate({ox},{oy})">']
    s.append(f'<circle cx="3" cy="5" r="{r + 6}" fill="#000" opacity="0.12"/>')
    # mounting frame + ears
    for a in (45, 135, 225, 315):
        s.append(f'<circle cx="0" cy="0" r="4.5" fill="#8E959B" transform="rotate({a}) translate({r + 2} 0)"/>')
    s.append(f'<circle r="{r + 6}" fill="#5E666D" stroke="#3F464C" stroke-width="2.5"/>')
    s.append(f'<circle r="{r - 4}" fill="#2A2D30"/>')                       # surround
    s.append(f'<circle r="{r - 14}" fill="url(#coneGrad)"/>')               # cone
    s.append(f'<circle r="{(r - 14) * 0.38}" fill="url(#capGrad)" stroke="#1A1A1A" stroke-width="1"/>')  # dust cap
    # terminals (left edge)
    pins = {}
    for i, n in enumerate(["+", "-"]):
        ty = -14 + i * 28
        s.append(f'<rect x="{-r - 22}" y="{ty - 5}" width="18" height="10" rx="2" fill="#C9A227" stroke="#8C6E14" stroke-width="1.2"/>')
        col = "#D32F2F" if n == "+" else "#37352F"
        s.append(f'<text x="{-r - 30}" y="{ty + 4}" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="700" fill="{col}">{n}</text>')
        pins[n] = (ox - r - 22, oy + ty)
    s.append(f'<text x="0" y="{r + 28}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="#5A5346">KALLSUP driver</text>')
    s.append(f'<text x="0" y="{r + 44}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="#8A8474">1.8&#8243; full-range &#183; 4 &#937; &#183; 3 W</text>')
    s.append("</g>")
    return "\n".join(s), pins


# ------------------------------------------------------------------ Defs

def svg_open(w, h):
    return f'''<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">
<defs>
  <linearGradient id="pcbGreen" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#3E9A52"/><stop offset="1" stop-color="#27713A"/>
  </linearGradient>
  <linearGradient id="pcbBlue" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#2C6FC4"/><stop offset="1" stop-color="#174E96"/>
  </linearGradient>
  <radialGradient id="coneGrad" cx="0.38" cy="0.34" r="0.9">
    <stop offset="0" stop-color="#6E747A"/><stop offset="0.7" stop-color="#3C4146"/><stop offset="1" stop-color="#26292C"/>
  </radialGradient>
  <radialGradient id="capGrad" cx="0.35" cy="0.3" r="1">
    <stop offset="0" stop-color="#53595F"/><stop offset="1" stop-color="#1E2124"/>
  </radialGradient>
</defs>
<rect width="{w}" height="{h}" rx="16" fill="#FDFBF7"/>'''


def title_block(w, title, subtitle):
    return (f'<text x="{w / 2}" y="34" text-anchor="middle" font-size="17" font-weight="800" fill="#2D3436">{title}</text>'
            f'<text x="{w / 2}" y="54" text-anchor="middle" font-size="11.5" fill="#636E72">{subtitle}</text>')


# ================================================================ Diagram 1
# Stock build wiring overview

def diagram_stock():
    W, H = 1000, 720
    out = [svg_open(W, H)]
    out.append(title_block(W, "BabyBox Wiring — Standard Build",
                           "All components connect to the Pi&#8217;s 40-pin header. Audio is wireless (Bluetooth) &#8212; no speaker wiring."))

    PX, PY = 290, 470
    used = {
        24: (C["yellow"], "24"), 23: (C["orange"], "23"), 19: (C["green"], "19"),
        21: (C["blue"], "21"), 22: (C["white"], "22"), 17: (C["red"], "17"), 6: (C["black"], "6"),
        12: (C["green"], "12"), 2: (C["red"], "2"), 9: (C["black"], "9"),
        11: (C["yellow"], "11"), 14: (C["black"], "14"), 13: (C["yellow"], "13"), 20: (C["black"], "20"),
        32: (C["yellow"], "32"), 34: (C["black"], "34"),
    }

    # --- components ---
    rf_svg, rf = mfrc522(40, 120)
    led_svg, led = ws2812(330, 110)
    b1_svg, b1 = tact_button(660, 120, "#4ECDC4", "&#9654;")
    b2_svg, b2 = tact_button(740, 120, "#FF6B6B", "&#9632;")
    bz_svg, bz = buzzer(900, 160)

    # --- wires (draw under components/Pi for clean pin entry: draw wires first
    #     then components? pins sit on edges; draw wires after boards but they
    #     start at pin centers, fine) ---
    out.append(pi_zero(PX, PY, used))
    out.append(rf_svg)
    out.append(led_svg)
    out.append(b1_svg)
    out.append(b2_svg)
    out.append(bz_svg)
    out.append(f'<text x="700" y="106" text-anchor="middle" font-size="11" font-weight="700" fill="#5A5346">Play/Pause</text>')
    out.append(f'<text x="762" y="106" text-anchor="start" font-size="11" font-weight="700" fill="#5A5346">Stop</text>')

    # MFRC522 (7 wires) — fan into left side of header
    out.append(wire(*rf["SDA"], *pi_pin(PX, PY, 24), C["yellow"], "down", "up", 90, "SDA &#8594; GPIO8", -40, 26))
    out.append(wire(*rf["SCK"], *pi_pin(PX, PY, 23), C["orange"], "down", "up", 100, "SCK &#8594; GPIO11", -78, -12))
    out.append(wire(*rf["MOSI"], *pi_pin(PX, PY, 19), C["green"], "down", "up", 80, "MOSI &#8594; GPIO10", -68, 50))
    out.append(wire(*rf["MISO"], *pi_pin(PX, PY, 21), C["blue"], "down", "up", 86, "MISO &#8594; GPIO9", 16, 88))
    out.append(wire(*rf["RST"], *pi_pin(PX, PY, 22), C["white"], "down", "up", 112, "RST &#8594; GPIO25", 64, -34))
    out.append(wire(*rf["3.3V"], *pi_pin(PX, PY, 17), C["red"], "down", "up", 60, "3.3V", -16, -38))
    out.append(wire(*rf["GND"], *pi_pin(PX, PY, 6), C["black"], "down", "up", 46, "GND", -52, 8))

    # WS2812 (3 wires)
    out.append(wire(*led["DIN"], *pi_pin(PX, PY, 12), C["green"], "left", "up", 70, "DIN &#8594; GPIO18", 64, 36))
    out.append(wire(*led["5V"], *pi_pin(PX, PY, 2), C["red"], "left", "up", 90, "5V", -4, 0))
    out.append(wire(*led["GND"], *pi_pin(PX, PY, 9), C["black"], "left", "up", 56, "", 0, 0))

    # Buttons (4 wires)
    out.append(wire(*b1["sig"], *pi_pin(PX, PY, 11), C["yellow"], "down", "up", 130, "GPIO17", -10, -6))
    out.append(wire(*b1["gnd"], *pi_pin(PX, PY, 14), C["black"], "down", "up", 120, "", 0, 0))
    out.append(wire(*b2["sig"], *pi_pin(PX, PY, 13), C["yellow"], "down", "up", 160, "GPIO27", 30, -16))
    out.append(wire(*b2["gnd"], *pi_pin(PX, PY, 20), C["black"], "down", "up", 148, "", 0, 0))

    # Buzzer (2 wires)
    out.append(wire(*bz["sig"], *pi_pin(PX, PY, 32), C["yellow"], "down", "up", 130, "GPIO12", 26, -30))
    out.append(wire(*bz["gnd"], *pi_pin(PX, PY, 34), C["black"], "down", "up", 110, "GND", 56, 6))

    # Wireless audio + HDMI callouts (sides, below component zone)
    out.append(f'''<g transform="translate(18,{PY + 90})">
      <rect width="252" height="62" rx="10" fill="#6C63FF" fill-opacity="0.07" stroke="#6C63FF" stroke-width="1.4" stroke-dasharray="5 4"/>
      <text x="126" y="25" text-anchor="middle" font-size="10.5" font-weight="700" fill="#6C63FF">Audio &#8212; Bluetooth (A2DP), no wires</text>
      <text x="126" y="44" text-anchor="middle" font-size="9.5" fill="#636E72">Pi pairs with the speaker at boot</text>
    </g>''')
    out.append(f'''<g transform="translate(730,{PY + 90})">
      <rect width="252" height="62" rx="10" fill="#636E72" fill-opacity="0.07" stroke="#636E72" stroke-width="1.4" stroke-dasharray="5 4"/>
      <text x="126" y="25" text-anchor="middle" font-size="10.5" font-weight="700" fill="#636E72">Video &#8212; mini-HDMI cable to TV</text>
      <text x="126" y="44" text-anchor="middle" font-size="9.5" fill="#636E72">Picture on TV, sound on speaker</text>
    </g>''')

    # legend
    out.append(legend(W, H - 46, [
        ("Signal / data", C["yellow"]), ("SCK / clock", C["orange"]), ("MOSI / DIN", C["green"]),
        ("MISO", C["blue"]), ("RST / misc", C["white"]), ("Power", C["red"]), ("Ground", C["black"]),
    ]))
    out.append("</svg>")
    return "\n".join(out)


def legend(W, y, items):
    n = len(items)
    bw = 124
    x0 = (W - n * bw) / 2
    s = [f'<g transform="translate(0,{y})" font-size="9.5">']
    for i, (lbl, col) in enumerate(items):
        x = x0 + i * bw
        s.append(f'<line x1="{x}" y1="-3" x2="{x + 22}" y2="-3" stroke="{darker(col)}" stroke-width="6" stroke-linecap="round"/>')
        s.append(f'<line x1="{x}" y1="-3" x2="{x + 22}" y2="-3" stroke="{col}" stroke-width="3.6" stroke-linecap="round"/>')
        s.append(f'<text x="{x + 28}" y="0" fill="#636E72">{lbl}</text>')
    s.append("</g>")
    return "\n".join(s)


# ================================================================ Diagram 2
# Wired-speaker variant

def diagram_wired():
    W, H = 1000, 660
    out = [svg_open(W, H)]
    out.append(title_block(W, "Wired-Speaker Mod &#8212; KALLSUP driver + MAX98357A",
                           "Five jumper wires from the Pi to the amp, two speaker wires to the salvaged driver. LED strip moves to GPIO 13."))

    PX, PY = 70, 400
    used = {
        4: (C["red"], "4"), 6: (C["black"], "6"),
        12: (C["orange"], "12"), 35: (C["white"], "35"), 40: (C["green"], "40"),
        33: (C["teal"], "33"),
    }
    amp_svg, amp = max98357a(560, 150)
    spk_svg, spk = speaker_driver(880, 210)

    out.append(pi_zero(PX, PY, used))
    out.append(amp_svg)
    out.append(spk_svg)

    # I2S + power wires (Pi header -> amp bottom header)
    out.append(wire(*pi_pin(PX, PY, 4), *amp["Vin"], C["red"], "up", "down", 120, "5V &#8594; Vin", -120, 40))
    out.append(wire(*pi_pin(PX, PY, 6), *amp["GND"], C["black"], "up", "down", 140, "GND", -96, 6))
    out.append(wire(*pi_pin(PX, PY, 12), *amp["BCLK"], C["orange"], "up", "down", 170, "GPIO18 &#8594; BCLK", -86, -38))
    out.append(wire(*pi_pin(PX, PY, 35), *amp["LRC"], C["white"], "up", "down", 95, "GPIO19 &#8594; LRC", -68, 64))
    out.append(wire(*pi_pin(PX, PY, 40), *amp["DIN"], C["green"], "up", "down", 130, "GPIO21 &#8594; DIN", 78, 30))

    # speaker wires (amp screw terminal -> driver tabs), twisted-pair note
    out.append(wire(*amp["spk+"], *spk["+"], C["red"], "up", "left", 36, "", 0, 0))
    out.append(wire(*amp["spk-"], *spk["-"], C["black"], "up", "left", 60, "", 0, 0))
    out.append(f'<text x="760" y="84" text-anchor="middle" font-size="10" font-weight="700" fill="#5A5346">twisted pair, &#8804;20 cm</text>')
    out.append(f'<text x="760" y="100" text-anchor="middle" font-size="9" fill="#8A8474">never connect either wire to GND (BTL output)</text>')

    # n/c flags for GAIN + SD
    gx, gy = amp["GAIN"]
    sx, sy = amp["SD"]
    for (x, y), lbl in (((gx, gy), "GAIN: n/c = 9 dB"), ((sx, sy), "SD: n/c = mono mix")):
        pass
    out.append(f'<g font-size="9" font-family="{MONO}">'
               f'<line x1="{gx}" y1="{gy}" x2="{gx + 14}" y2="{gy + 26}" stroke="#B0AA9C" stroke-width="1.2" stroke-dasharray="3 2"/>'
               f'<text x="{gx + 18}" y="{gy + 32}" fill="#8A8474">GAIN n/c &#8594; 9 dB</text>'
               f'<line x1="{sx}" y1="{sy}" x2="{sx + 22}" y2="{sy + 46}" stroke="#B0AA9C" stroke-width="1.2" stroke-dasharray="3 2"/>'
               f'<text x="{sx + 26}" y="{sy + 52}" fill="#8A8474">SD n/c &#8594; (L+R)/2 mono</text></g>')

    # moved LED pin callout
    mx, my = pi_pin(PX, PY, 33)
    out.append(f'''<g>
      <path d="M {mx} {my + 14} C {mx} {my + 60}, {mx + 60} {my + 78}, {mx + 110} {my + 78}" fill="none" stroke="{C['teal']}" stroke-width="1.6" stroke-dasharray="4 3"/>
      <g transform="translate({mx + 114},{my + 56})">
        <rect width="396" height="46" rx="9" fill="#26A69A" fill-opacity="0.08" stroke="#26A69A" stroke-width="1.4"/>
        <text x="12" y="19" font-size="10.5" font-weight="700" fill="#1B7B71">Changed vs. standard build (I2S audio needs GPIO 18):</text>
        <text x="12" y="35" font-size="10" fill="#41594F">WS2812 LED strip DIN moves from GPIO 18 to GPIO 13 (pin 33)</text>
      </g>
    </g>''')

    out.append(legend(W, H - 28, [
        ("BCLK (clock)", C["orange"]), ("LRC (word sel)", C["white"]), ("DIN (audio data)", C["green"]),
        ("Power 5V", C["red"]), ("Ground", C["black"]), ("Speaker +", C["red"]), ("Moved pin", C["teal"]),
    ]))
    out.append("</svg>")
    return "\n".join(out)


# ================================================================ Diagram 3
# Bluetooth option graphic

def diagram_bluetooth():
    W, H = 760, 300
    out = [svg_open(W, H)]
    out.append(f'<g transform="translate(40,60) scale(0.62)">{pi_zero(0, 0, {}, "Pi Zero 2 W")}</g>')

    # Bluetooth waves
    cx, cy = 392, 132
    for i, r in enumerate((30, 52, 74)):
        out.append(f'<path d="M {cx} {cy - r} A {r} {r} 0 0 1 {cx} {cy + r}" fill="none" stroke="#6C63FF" stroke-width="3.2" stroke-linecap="round" opacity="{0.85 - i * 0.25}"/>')
    out.append(f'<text x="{cx + 40}" y="{cy - 78}" text-anchor="middle" font-size="11" font-weight="700" fill="#6C63FF">Bluetooth A2DP</text>')
    out.append(f'<text x="{cx + 40}" y="{cy - 62}" text-anchor="middle" font-size="9.5" fill="#8A85C9">no wiring at all</text>')

    # speaker cube (KALLSUP-ish)
    out.append(f'''<g transform="translate(540,52)">
      <rect x="4" y="6" width="160" height="160" rx="18" fill="#000" opacity="0.10"/>
      <rect width="160" height="160" rx="18" fill="#F2EFE8" stroke="#C9C4B8" stroke-width="2.5"/>
      <rect x="46" y="-2" width="26" height="8" rx="4" fill="#C9C4B8"/>
      <rect x="86" y="-2" width="26" height="8" rx="4" fill="#C9C4B8"/>''')
    dots = []
    for r in range(7):
        for c in range(7):
            dx, dy = 33 + c * 16, 33 + r * 16
            if (dx - 80) ** 2 + (dy - 80) ** 2 <= 58 ** 2:
                dots.append(f'<circle cx="{dx}" cy="{dy}" r="4.6" fill="#B8B2A4"/>')
    out.append("".join(dots))
    out.append('</g>')
    out.append(f'<text x="620" y="242" text-anchor="middle" font-size="12" font-weight="700" fill="#5A5346">Any Bluetooth speaker</text>')
    out.append(f'<text x="620" y="258" text-anchor="middle" font-size="10" fill="#8A8474">paired once via the web UI</text>')
    out.append("</svg>")
    return "\n".join(out)


# ================================================================ main

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, fn in (("wiring-stock.svg", diagram_stock),
                     ("wiring-wired-speaker.svg", diagram_wired),
                     ("audio-bluetooth.svg", diagram_bluetooth)):
        path = os.path.join(OUT_DIR, name)
        with open(path, "w") as f:
            f.write(fn())
        print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    main()
