#!/usr/bin/env python3
"""
BabyBox Assembly Guide — PDF Generator
=======================================
Generates a comprehensive assembly guide covering 3D printing, magnet insertion,
electronics mounting, wiring, figurine construction, and final assembly.

Dependencies: fpdf2  (pip install fpdf2)
Output:       docs/BabyBox-Assembly-Guide.pdf

Usage:
    source docs/.venv/bin/activate
    python3 docs/generate-assembly-guide.py
"""

import textwrap
from datetime import date
from pathlib import Path

from fpdf import FPDF

# ─────────────────────────────────────────────────────────────
# Data Constants (from SPEC.md, common-params.scad, etc.)
# ─────────────────────────────────────────────────────────────

BOM = [
    ("Raspberry Pi Zero 2 W",           "1",  "Purchase",       "~$15"),
    ("MicroSD card (32 GB+)",            "1",  "Purchase",       "~$8"),
    ("MFRC522 RFID Module",              "1",  "Sensor kit",     "--"),
    ("RFID coin stickers (25mm, 13.56 MHz)", "10", "Purchase",   "~$5"),
    ("Neodymium magnets (6x3mm disc)",   "20+","Purchase",       "~$5"),
    ("Bluetooth speaker",                "1",  "Already owned",  "~$0-20"),
    ("WS2812 RGB 8-LED strip",           "1",  "Sensor kit",     "--"),
    ("Passive buzzer",                   "1",  "Sensor kit",     "--"),
    ("Tactile buttons (6x6mm)",          "2",  "Sensor kit",     "--"),
    ("Resistors / wires / breadboard",   "1",  "Sensor kit",     "--"),
    ("5 V 3 A micro-USB power supply",   "1",  "Purchase",       "~$8"),
    ("Mini-HDMI to HDMI cable",          "1",  "Purchase",       "~$5"),
    ("3D-printed enclosure + figurines", "1",  "Bambu Lab P2S",  "~$5 filament"),
]

GPIO_PINS = [
    ("MFRC522 SDA",  "GPIO 8",  "SPI0 CE0"),
    ("MFRC522 SCK",  "GPIO 11", "SPI0 SCLK"),
    ("MFRC522 MOSI", "GPIO 10", "SPI0 MOSI"),
    ("MFRC522 MISO", "GPIO 9",  "SPI0 MISO"),
    ("MFRC522 RST",  "GPIO 25", "General GPIO"),
    ("MFRC522 3.3 V","3.3 V",   "Pin 1 or 17"),
    ("MFRC522 GND",  "GND",     "Pin 6, 9, 14, 20, 25, 30, 34, 39"),
    ("WS2812 DIN",   "GPIO 18", "PWM0"),
    ("WS2812 5 V",   "5 V",     "Pin 2 or 4"),
    ("WS2812 GND",   "GND",     "Any GND pin"),
    ("Play/Pause btn","GPIO 17", "Internal pull-up"),
    ("Stop button",  "GPIO 27", "Internal pull-up"),
    ("Buzzer signal", "GPIO 12", "PWM1"),
    ("Buzzer GND",   "GND",     "Any GND pin"),
]

ENCLOSURE = {
    "outer_l": 150, "outer_w": 110, "outer_h": 75,
    "wall": 3, "corner_r": 5, "lid_h": 12, "body_h": 63,
    "floor_h": 3,
}
FIGURINE_BASE = {
    "dia": 35, "height": 6,
    "magnet_pocket_dia": 6.3, "magnet_pocket_h": 3.2,
    "magnet_seal_h": 1.0, "magnet_spacing": 20,
    "rfid_recess_dia": 25.5, "rfid_recess_h": 0.5,
    "chamfer": 0.8,
}
MAGNETS = {"dia": 6, "h": 3, "pocket_dia": 6.3, "pocket_h": 3.2, "spacing": 20, "seal_h": 1.0}

PRINT_SETTINGS = {
    "material": "PETG",
    "nozzle": "0.4 mm",
    "layer_height": "0.2 mm",
    "infill": "20 %",
    "perimeters": "3",
    "top_layers": "5",
    "bottom_layers": "4",
    "supports": "None (designed support-free)",
}

# Colors
COLOR_DARK   = (40, 40, 40)
COLOR_ACCENT = (0, 102, 204)
COLOR_RED    = (200, 30, 30)
COLOR_GREEN  = (30, 130, 60)
COLOR_WARN   = (220, 160, 0)
COLOR_GRAY   = (100, 100, 100)
COLOR_LIGHT  = (240, 240, 240)

# Wire colors for diagrams
WIRE_YELLOW = (220, 180, 0)
WIRE_ORANGE = (230, 120, 0)
WIRE_GREEN  = (40, 160, 40)
WIRE_BLUE   = (40, 80, 200)
WIRE_WHITE  = (180, 180, 180)
WIRE_RED    = (220, 40, 40)
WIRE_BLACK  = (40, 40, 40)

# Pin highlight colors
PIN_SPI   = (100, 149, 237)   # cornflower blue
PIN_PWM   = (144, 238, 144)   # light green
PIN_GPIO  = (255, 200, 100)   # gold
PIN_POWER = (255, 100, 100)   # red
PIN_GND   = (80, 80, 80)      # dark gray
PIN_UNUSED = (200, 200, 200)  # light gray


# ─────────────────────────────────────────────────────────────
# AssemblyGuide class
# ─────────────────────────────────────────────────────────────

class AssemblyGuide(FPDF):
    """Custom FPDF subclass with helpers for a technical assembly guide."""

    MARGIN = 15
    section_num = 0

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(self.MARGIN, self.MARGIN, self.MARGIN)

    # --- Page chrome ---
    def header(self):
        if self.page_no() <= 2:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*COLOR_GRAY)
        self.cell(0, 6, "BabyBox Assembly Guide", align="L")
        self.ln(8)

    def footer(self):
        if self.page_no() <= 1:
            return
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*COLOR_GRAY)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    # --- Content helpers ---

    def section_title(self, title):
        self.section_num += 1
        label = f"{self.section_num}.  {title}"
        self.add_page()
        self.start_section(label)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*COLOR_DARK)
        self.cell(0, 12, label, new_x="LMARGIN", new_y="NEXT")
        y = self.get_y()
        self.set_draw_color(*COLOR_ACCENT)
        self.set_line_width(0.8)
        self.line(self.MARGIN, y, self.w - self.MARGIN, y)
        self.ln(6)

    def subsection(self, title):
        self._ensure_space(14)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*COLOR_ACCENT)
        self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*COLOR_DARK)
        self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*COLOR_DARK)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bold_text(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*COLOR_DARK)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def note_box(self, text, kind="NOTE"):
        color = COLOR_RED if kind == "WARNING" else COLOR_ACCENT
        prefix = f"{kind}: "
        full_text = prefix + text

        self.set_font("Helvetica", "", 10)
        page_w = self.w - 2 * self.MARGIN
        inner_w = page_w - 10

        char_w = self.get_string_width("x")
        chars_per_line = max(1, int(inner_w / char_w))
        wrapped = textwrap.fill(full_text, width=chars_per_line)
        n_lines = wrapped.count("\n") + 1
        block_h = n_lines * 5 + 8

        self._ensure_space(block_h + 4)
        y0 = self.get_y()
        x0 = self.MARGIN

        self.set_fill_color(*color)
        self.rect(x0, y0, 3, block_h, "F")

        bg = (255, 235, 235) if kind == "WARNING" else (230, 240, 255)
        self.set_fill_color(*bg)
        self.rect(x0 + 3, y0, page_w - 3, block_h, "F")

        self.set_xy(x0 + 7, y0 + 3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*color)
        self.write(5, prefix)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*COLOR_DARK)
        self.multi_cell(inner_w - 4, 5, text)

        actual_y = self.get_y()
        self.set_y(max(y0 + block_h, actual_y) + 4)

    def numbered_steps(self, steps):
        for i, step in enumerate(steps, 1):
            self._ensure_space(12)
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*COLOR_ACCENT)
            self.cell(8, 5, f"{i}.", new_x="END")
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*COLOR_DARK)
            x = self.get_x()
            self.multi_cell(self.w - self.MARGIN - x, 5, step)
            self.ln(1.5)

    def bullet_list(self, items):
        for item in items:
            self._ensure_space(10)
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*COLOR_DARK)
            self.cell(6, 5, "-", new_x="END")
            x = self.get_x()
            self.multi_cell(self.w - self.MARGIN - x, 5, item)
            self.ln(1)

    def make_table(self, headers, rows, col_widths=None):
        page_w = self.w - 2 * self.MARGIN
        if col_widths is None:
            col_widths = [page_w / len(headers)] * len(headers)

        self._ensure_space(20)

        with self.table(
            col_widths=col_widths,
            text_align="LEFT",
            line_height=self.font_size * 2.2,
            first_row_as_headings=True,
            cell_fill_color=COLOR_LIGHT,
            cell_fill_mode="ROWS",
        ) as table:
            hrow = table.row()
            self.set_font("Helvetica", "B", 9)
            for h in headers:
                hrow.cell(h)
            self.set_font("Helvetica", "", 9)
            for row_data in rows:
                r = table.row()
                for cell_text in row_data:
                    r.cell(cell_text)
        self.ln(3)

    def _ensure_space(self, needed_mm):
        remaining = self.h - self.get_y() - 20
        if remaining < needed_mm:
            self.add_page()

    # --- Drawing helpers ---

    def _label(self, x, y, text, size=7, color=COLOR_DARK, align="L", bold=False):
        """Place a label at absolute position without moving cursor."""
        old_x, old_y = self.get_x(), self.get_y()
        style = "B" if bold else ""
        self.set_font("Helvetica", style, size)
        self.set_text_color(*color)
        self.text(x, y, text)
        self.set_xy(old_x, old_y)

    def _pin_circle(self, cx, cy, r, color, label="", label_side="L", label_size=5.5):
        """Draw a filled pin circle with an optional label."""
        self.set_fill_color(*color)
        self.set_draw_color(60, 60, 60)
        self.set_line_width(0.2)
        self.ellipse(cx - r, cy - r, 2 * r, 2 * r, "DF")
        if label:
            self.set_font("Helvetica", "", label_size)
            self.set_text_color(*COLOR_DARK)
            lw = self.get_string_width(label)
            if label_side == "L":
                self.text(cx - r - lw - 1.5, cy + 1.5, label)
            else:
                self.text(cx + r + 1.5, cy + 1.5, label)

    def _wire(self, x1, y1, x2, y2, color, label="", label_pos="mid"):
        """Draw a colored wire between two points with an optional label."""
        self.set_draw_color(*color)
        self.set_line_width(0.8)
        self.line(x1, y1, x2, y2)
        if label:
            self.set_font("Helvetica", "", 6)
            self.set_text_color(*color)
            if label_pos == "mid":
                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2
                self.text(mx + 1, my - 1, label)

    def _rounded_rect(self, x, y, w, h, r, style="D"):
        """Draw a rectangle (rounded corners approximated with regular rect)."""
        self.set_line_width(0.3)
        self.rect(x, y, w, h, style)

    def _component_box(self, x, y, w, h, label, color=(180, 210, 240)):
        """Draw a labeled component rectangle."""
        self.set_fill_color(*color)
        self.set_draw_color(60, 60, 60)
        self.set_line_width(0.4)
        self.rect(x, y, w, h, "DF")
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*COLOR_DARK)
        lw = self.get_string_width(label)
        self.text(x + (w - lw) / 2, y + h / 2 + 2, label)

    def _dimension_line(self, x1, y, x2, label):
        """Draw a dimensioning line with arrowheads and label."""
        self.set_draw_color(*COLOR_GRAY)
        self.set_line_width(0.25)
        # line
        self.line(x1, y, x2, y)
        # arrowheads (small ticks)
        self.line(x1, y - 1.5, x1, y + 1.5)
        self.line(x2, y - 1.5, x2, y + 1.5)
        # label
        self.set_font("Helvetica", "", 6)
        self.set_text_color(*COLOR_GRAY)
        lw = self.get_string_width(label)
        mx = (x1 + x2) / 2 - lw / 2
        self.text(mx, y - 2, label)


# ─────────────────────────────────────────────────────────────
# Diagram Drawing Functions
# ─────────────────────────────────────────────────────────────

def draw_cover_enclosure(pdf: AssemblyGuide, cx, y_top):
    """Draw a 3D-ish enclosure sketch on the cover page."""
    # Front face
    w, h = 100, 48
    x = cx - w / 2
    y = y_top
    d = 15  # 3D depth offset

    pdf.set_draw_color(*COLOR_DARK)
    pdf.set_line_width(0.6)

    # Top face (parallelogram) — draw first so front face overlaps
    pdf.set_fill_color(200, 220, 245)
    top_pts = [(x, y), (x + d, y - d), (x + w + d, y - d), (x + w, y)]
    pdf.polygon(top_pts, style="DF")

    # Right face (parallelogram)
    pdf.set_fill_color(180, 200, 230)
    right_pts = [(x + w, y), (x + w + d, y - d), (x + w + d, y + h - d), (x + w, y + h)]
    pdf.polygon(right_pts, style="DF")

    # Front face (on top)
    pdf.set_fill_color(230, 240, 250)
    pdf.rect(x, y, w, h, "DF")

    # Figurine placement circle on top
    top_cx = cx + d / 2
    top_cy = y - d / 2
    pdf.set_draw_color(*COLOR_ACCENT)
    pdf.set_line_width(0.8)
    pdf.ellipse(top_cx - 12, top_cy - 5, 24, 10, "D")

    # Two magnets on top (small dots)
    pdf.set_fill_color(*COLOR_GRAY)
    pdf.ellipse(top_cx - 7, top_cy - 1.5, 3, 3, "F")
    pdf.ellipse(top_cx + 4, top_cy - 1.5, 3, 3, "F")

    # Buttons on front
    btn_y = y + h * 0.35
    pdf.set_fill_color(80, 180, 80)
    pdf.set_draw_color(60, 60, 60)
    pdf.set_line_width(0.3)
    pdf.ellipse(x + 25, btn_y, 10, 10, "DF")  # play/pause
    pdf.set_fill_color(200, 80, 80)
    pdf.ellipse(x + 65, btn_y, 10, 10, "DF")  # stop

    # Button labels
    pdf._label(x + 27.5, btn_y + 6, ">||", size=5, color=(255, 255, 255))
    pdf._label(x + 69, btn_y + 6, "[ ]", size=5, color=(255, 255, 255))

    # LED strip on front
    led_y = y + h * 0.7
    for i in range(8):
        lx = x + 20 + i * 8
        colors = [(255, 60, 60), (255, 140, 0), (255, 220, 0), (60, 220, 60),
                  (60, 180, 255), (80, 80, 255), (180, 60, 255), (255, 60, 180)]
        pdf.set_fill_color(*colors[i])
        pdf.ellipse(lx, led_y, 5, 5, "F")

    # Top label
    pdf._label(top_cx - 14, top_cy + 1, "place figurine", size=6, color=COLOR_ACCENT)

    # Dimensions
    dim_y = y + h + 6
    pdf._dimension_line(x, dim_y, x + w, "150 mm")
    pdf._dimension_line(x + w + 4, y, x + w + 4, "75 mm")
    pdf.set_draw_color(*COLOR_GRAY)
    pdf.line(x + w + 2, y, x + w + 6, y)
    pdf.line(x + w + 2, y + h, x + w + 6, y + h)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(*COLOR_GRAY)


def draw_gpio_header(pdf: AssemblyGuide, x0, y0):
    """Draw the 40-pin GPIO header with color-coded pins."""
    # Pin definitions: (pin#, label, color, is_used)
    # Odd = left column, Even = right column
    pin_data = {
        1:  ("3V3",  PIN_POWER, True),   2:  ("5V",   PIN_POWER, True),
        3:  ("SDA",  PIN_UNUSED, False),  4:  ("5V",   PIN_POWER, True),
        5:  ("SCL",  PIN_UNUSED, False),  6:  ("GND",  PIN_GND, True),
        7:  ("GP4",  PIN_UNUSED, False),  8:  ("TXD",  PIN_UNUSED, False),
        9:  ("GND",  PIN_GND, True),     10:  ("RXD",  PIN_UNUSED, False),
        11: ("GP17", PIN_GPIO, True),    12:  ("GP18", PIN_PWM, True),
        13: ("GP27", PIN_GPIO, True),    14:  ("GND",  PIN_GND, True),
        15: ("GP22", PIN_UNUSED, False), 16:  ("GP23", PIN_UNUSED, False),
        17: ("3V3",  PIN_POWER, True),   18:  ("GP24", PIN_UNUSED, False),
        19: ("MOSI", PIN_SPI, True),     20:  ("GND",  PIN_GND, True),
        21: ("MISO", PIN_SPI, True),     22:  ("GP25", PIN_GPIO, True),
        23: ("SCLK", PIN_SPI, True),     24:  ("CE0",  PIN_SPI, True),
        25: ("GND",  PIN_GND, True),     26:  ("CE1",  PIN_UNUSED, False),
        27: ("ID",   PIN_UNUSED, False), 28:  ("ID",   PIN_UNUSED, False),
        29: ("GP5",  PIN_UNUSED, False), 30:  ("GND",  PIN_GND, True),
        31: ("GP6",  PIN_UNUSED, False), 32:  ("GP12", PIN_PWM, True),
        33: ("GP13", PIN_UNUSED, False), 34:  ("GND",  PIN_GND, True),
        35: ("GP19", PIN_UNUSED, False), 36:  ("GP16", PIN_UNUSED, False),
        37: ("GP26", PIN_UNUSED, False), 38:  ("GP20", PIN_UNUSED, False),
        39: ("GND",  PIN_GND, True),     40:  ("GP21", PIN_UNUSED, False),
    }

    pin_r = 2.2
    row_h = 5.5
    col_gap = 10
    total_h = 20 * row_h + 4  # 20 rows

    # Board background
    pdf.set_fill_color(60, 120, 60)
    pdf.set_draw_color(40, 80, 40)
    pdf.set_line_width(0.5)
    pdf.rect(x0, y0, 60, total_h, "DF")

    # Title
    pdf._label(x0 + 8, y0 + 5, "Pi Zero 2 W  -  40-pin Header", size=7,
               color=(220, 255, 220), bold=True)

    pin_start_y = y0 + 9

    # Usage annotations (right side)
    annotations = {
        11: "Play/Pause",
        12: "WS2812 DIN",
        13: "Stop btn",
        19: "RFID MOSI",
        21: "RFID MISO",
        22: "RFID RST",
        23: "RFID SCLK",
        24: "RFID SDA",
        32: "Buzzer",
    }

    for pin_num in range(1, 41):
        label, color, used = pin_data[pin_num]
        row = (pin_num - 1) // 2
        is_left = (pin_num % 2 == 1)

        if is_left:
            cx = x0 + 18
        else:
            cx = x0 + 18 + col_gap
        cy = pin_start_y + row * row_h

        # Draw pin
        pdf._pin_circle(cx, cy, pin_r, color,
                        label=f"{label}" if used else "",
                        label_side="L" if is_left else "R",
                        label_size=5)

        # Pin number
        pdf.set_font("Helvetica", "", 4)
        pdf.set_text_color(200, 200, 200)
        pdf.text(cx - 1.2, cy + 1, str(pin_num))

        # Annotation arrow for key pins
        if pin_num in annotations:
            ax = x0 + 60 + 3
            pdf.set_draw_color(*color)
            pdf.set_line_width(0.4)
            pdf.line(cx + pin_r, cy, ax, cy)
            pdf._label(ax + 1, cy + 1.5, annotations[pin_num], size=6, color=color)

    # Legend
    ly = y0 + total_h + 5
    legend_items = [
        ("SPI (RFID)", PIN_SPI),
        ("PWM (LED/Buzzer)", PIN_PWM),
        ("GPIO (Buttons/RST)", PIN_GPIO),
        ("Power (3V3/5V)", PIN_POWER),
        ("GND", PIN_GND),
        ("Unused", PIN_UNUSED),
    ]
    lx = x0
    for lbl, col in legend_items:
        pdf.set_fill_color(*col)
        pdf.set_draw_color(60, 60, 60)
        pdf.set_line_width(0.2)
        pdf.ellipse(lx, ly, 3, 3, "DF")
        pdf._label(lx + 4, ly + 2.5, lbl, size=6)
        lx += pdf.get_string_width(lbl) + 8

    return total_h + 14


def draw_enclosure_top_view(pdf: AssemblyGuide, x0, y0):
    """Draw the enclosure body top view with component positions."""
    # Scale: real 150x110mm -> draw at 0.8x
    s = 0.8
    w = 150 * s
    h = 110 * s

    # Outer box
    pdf.set_draw_color(*COLOR_DARK)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_line_width(0.5)
    pdf._rounded_rect(x0, y0, w, h, 4, "DF")

    # Inner wall
    wall = 3 * s
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.3)
    pdf.rect(x0 + wall, y0 + wall, w - 2 * wall, h - 2 * wall, "D")

    # Pi Zero 2 W (back-left)
    pi_x = x0 + wall + 10 * s
    pi_y = y0 + h - wall - 35 * s  # near back
    pi_w = 65 * s
    pi_h = 30 * s
    pdf._component_box(pi_x, pi_y, pi_w, pi_h, "Pi Zero 2 W", (180, 230, 180))

    # Pi standoffs (4 dots)
    for dx, dy in [(3.5 * s, 3.5 * s), (61.5 * s, 3.5 * s),
                   (3.5 * s, 26.5 * s), (61.5 * s, 26.5 * s)]:
        pdf.set_fill_color(150, 150, 150)
        pdf.ellipse(pi_x + dx - 1.5, pi_y + dy - 1.5, 3, 3, "F")

    # Port labels on back wall
    pdf._label(pi_x + 8 * s, y0 + h + 4, "HDMI", size=5, color=COLOR_GRAY)
    pdf._label(pi_x + 30 * s, y0 + h + 4, "USB-OTG", size=5, color=COLOR_GRAY)
    pdf._label(pi_x + 46 * s, y0 + h + 4, "USB-PWR", size=5, color=COLOR_GRAY)
    # Port arrows
    for px in [pi_x + 12 * s, pi_x + 37 * s, pi_x + 53 * s]:
        pdf.set_draw_color(*COLOR_GRAY)
        pdf.set_line_width(0.3)
        pdf.line(px, y0 + h - wall, px, y0 + h + 1)

    # Breadboard (center)
    bb_x = x0 + (w - 82 * s) / 2
    bb_y = y0 + (h - 55 * s) / 2 - 6 * s
    pdf._component_box(bb_x, bb_y, 82 * s, 55 * s, "Half Breadboard (82x55mm)",
                       (240, 230, 210))

    # Breadboard rows hint
    pdf.set_draw_color(200, 200, 200)
    for i in range(5):
        ry = bb_y + 8 + i * 8 * s
        pdf.line(bb_x + 4, ry, bb_x + 82 * s - 4, ry)

    # Buzzer (back-right)
    buz_cx = x0 + w - wall - 16 * s
    buz_cy = y0 + h - wall - 16 * s
    pdf.set_fill_color(220, 200, 180)
    pdf.set_draw_color(60, 60, 60)
    pdf.set_line_width(0.3)
    pdf.ellipse(buz_cx - 6 * s, buz_cy - 6 * s, 12 * s, 12 * s, "DF")
    pdf._label(buz_cx - 5 * s, buz_cy + 2, "Buzzer", size=5)

    # Screw posts (4 corners)
    post_inset = 8 * s
    for px, py in [(x0 + post_inset, y0 + post_inset),
                   (x0 + w - post_inset, y0 + post_inset),
                   (x0 + post_inset, y0 + h - post_inset),
                   (x0 + w - post_inset, y0 + h - post_inset)]:
        pdf.set_fill_color(160, 160, 160)
        pdf.set_draw_color(100, 100, 100)
        pdf.ellipse(px - 2.5, py - 2.5, 5, 5, "DF")
        pdf.set_fill_color(245, 245, 245)
        pdf.ellipse(px - 1, py - 1, 2, 2, "F")

    # Buttons on front wall
    btn_y = y0 + 3
    pdf.set_fill_color(80, 180, 80)
    pdf.ellipse(x0 + w * 0.3 - 4, btn_y - 1, 8, 4, "DF")
    pdf._label(x0 + w * 0.3 - 8, btn_y - 3, "Play/Pause", size=5, color=COLOR_GREEN)

    pdf.set_fill_color(200, 80, 80)
    pdf.ellipse(x0 + w * 0.7 - 4, btn_y - 1, 8, 4, "DF")
    pdf._label(x0 + w * 0.7 - 4, btn_y - 3, "Stop", size=5, color=COLOR_RED)

    # LED window on front wall
    led_x = x0 + w * 0.35
    led_w = w * 0.3
    pdf.set_fill_color(255, 255, 200)
    pdf.set_draw_color(200, 180, 0)
    pdf.rect(led_x, y0 - 1, led_w, 3, "DF")
    pdf._label(led_x + led_w / 2 - 8, y0 - 3, "LED Window", size=5, color=COLOR_WARN)

    # Dimensions
    pdf._dimension_line(x0, y0 + h + 8, x0 + w, "150 mm")
    # Vertical dimension
    pdf.set_draw_color(*COLOR_GRAY)
    pdf.set_line_width(0.25)
    pdf.line(x0 - 6, y0, x0 - 2, y0)
    pdf.line(x0 - 6, y0 + h, x0 - 2, y0 + h)
    pdf.line(x0 - 4, y0, x0 - 4, y0 + h)
    pdf.line(x0 - 5.5, y0, x0 - 2.5, y0)
    pdf.line(x0 - 5.5, y0 + h, x0 - 2.5, y0 + h)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(*COLOR_GRAY)
    # Rotate label idea — just place it sideways by placing chars vertically
    pdf._label(x0 - 10, y0 + h / 2, "110mm", size=6, color=COLOR_GRAY)

    # Title
    pdf._label(x0, y0 - 6, "Enclosure Body - Top View (open top, looking down)",
               size=8, color=COLOR_DARK, bold=True)

    return h + 18


def draw_magnet_cross_section(pdf: AssemblyGuide, x0, y0, part="base"):
    """Draw a cross-section of the magnet pocket."""
    # Draw a wide rectangle representing the part cross-section
    w = 130
    total_h = 48 if part == "base" else 55

    pdf._ensure_space(total_h + 20)
    y0 = pdf.get_y() + 4

    title = "Figurine Base Cross-Section" if part == "base" else "Lid Cross-Section (printed upside-down)"
    pdf._label(x0, y0, title, size=8, color=COLOR_DARK, bold=True)
    y0 += 6

    # Scaling: base is 6mm tall -> draw 36mm. Lid is 12mm -> draw 42mm
    real_h = 6 if part == "base" else 12
    scale = 6.0  # mm drawing per mm real
    draw_h = real_h * scale

    # Z positions (real mm)
    z_bot = 0
    z_seal_bot = MAGNETS["seal_h"]             # 1.0
    z_pocket_top = z_seal_bot + MAGNETS["pocket_h"]  # 4.2
    z_top = real_h

    # Convert to drawing Y (y increases downward, Z increases upward)
    def zy(real_z):
        return y0 + draw_h - real_z * scale

    # Outer shell
    pdf.set_fill_color(180, 200, 220)
    pdf.set_draw_color(80, 80, 80)
    pdf.set_line_width(0.4)
    pdf.rect(x0 + 10, zy(z_top), w - 20, draw_h, "DF")

    # Magnet pockets (two cavities)
    pocket_w = 12
    pocket_centers = [x0 + w / 2 - 18, x0 + w / 2 + 18]
    for pcx in pocket_centers:
        # Cavity (white = empty space)
        cav_y = zy(z_pocket_top)
        cav_h = MAGNETS["pocket_h"] * scale
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(pcx - pocket_w / 2, cav_y, pocket_w, cav_h, "DF")

        # Magnet inside cavity
        mag_h = MAGNETS["h"] * scale
        mag_y = cav_y + (cav_h - mag_h) / 2
        pdf.set_fill_color(160, 160, 170)
        pdf.set_draw_color(100, 100, 100)
        pdf.rect(pcx - pocket_w / 2 + 1, mag_y, pocket_w - 2, mag_h, "DF")

        # Label magnet
        pdf._label(pcx - 5, mag_y + mag_h / 2 + 1.5, "magnet", size=5, color=(80, 80, 80))

        # N/S labels
        if part == "base":
            pdf._label(pcx - 1, mag_y - 0.5, "S", size=5, color=COLOR_RED)
            pdf._label(pcx - 1, mag_y + mag_h + 3.5, "N", size=5, color=COLOR_ACCENT)
        else:
            pdf._label(pcx - 1, mag_y - 0.5, "N", size=5, color=COLOR_ACCENT)
            pdf._label(pcx - 1, mag_y + mag_h + 3.5, "S", size=5, color=COLOR_RED)

    # RFID recess (bottom of base / top surface of lid)
    if part == "base":
        rfid_w = 40
        rfid_h = 1.5
        rfid_x = x0 + w / 2 - rfid_w / 2
        rfid_y = zy(z_bot) - rfid_h
        pdf.set_fill_color(255, 230, 180)
        pdf.set_draw_color(200, 160, 80)
        pdf.rect(rfid_x, rfid_y + rfid_h - 1, rfid_w, 1, "DF")
        pdf._label(rfid_x + 5, rfid_y + rfid_h + 3, "RFID sticker (bottom)", size=5,
                   color=(180, 130, 40))

    # Z-axis labels
    z_label_x = x0 + w - 6

    pdf.set_draw_color(COLOR_ACCENT[0], COLOR_ACCENT[1], COLOR_ACCENT[2])
    pdf.set_line_width(0.2)

    # Bottom line + label
    pdf.line(x0 + 5, zy(z_bot), x0 + w - 5, zy(z_bot))
    pdf._label(z_label_x + 3, zy(z_bot) + 1.5, f"Z = 0 mm  (build plate)", size=6,
               color=COLOR_GRAY)

    # Seal bottom
    pdf.set_draw_color(200, 100, 100)
    self_dashed = [(x0 + 5, zy(z_seal_bot)), (x0 + w - 5, zy(z_seal_bot))]
    # Dashed effect with short segments
    for seg_x in range(int(x0 + 5), int(x0 + w - 5), 4):
        pdf.line(seg_x, zy(z_seal_bot), min(seg_x + 2, x0 + w - 5), zy(z_seal_bot))
    pdf._label(z_label_x + 3, zy(z_seal_bot) + 1.5,
               f"Z = {z_seal_bot} mm  (seal floor)", size=6, color=(200, 100, 100))

    # Pause height
    pdf.set_draw_color(*COLOR_RED)
    pdf.set_line_width(0.5)
    pdf.line(x0 + 5, zy(z_pocket_top), x0 + w - 5, zy(z_pocket_top))
    pdf._label(z_label_x + 3, zy(z_pocket_top) + 1.5,
               f"Z = {z_pocket_top} mm  PAUSE HERE", size=6, color=COLOR_RED, bold=True)

    # Top
    pdf.set_draw_color(*COLOR_ACCENT)
    pdf.set_line_width(0.3)
    pdf.line(x0 + 5, zy(z_top), x0 + w - 5, zy(z_top))
    pdf._label(z_label_x + 3, zy(z_top) + 1.5, f"Z = {z_top} mm  (top)", size=6,
               color=COLOR_GRAY)

    # Arrows showing layers
    arrow_x = x0 + 4
    pdf.set_font("Helvetica", "", 5.5)

    # Seal floor bracket
    pdf.set_draw_color(100, 100, 100)
    pdf.set_line_width(0.2)
    pdf.line(arrow_x, zy(z_bot), arrow_x, zy(z_seal_bot))
    pdf._label(arrow_x - 9, (zy(z_bot) + zy(z_seal_bot)) / 2 + 1.5,
               f"{z_seal_bot}mm", size=5, color=COLOR_GRAY)

    # Cavity bracket
    pdf.line(arrow_x, zy(z_seal_bot), arrow_x, zy(z_pocket_top))
    pdf._label(arrow_x - 9, (zy(z_seal_bot) + zy(z_pocket_top)) / 2 + 1.5,
               f"{MAGNETS['pocket_h']}mm", size=5, color=COLOR_GRAY)

    # Seal top bracket
    seal_top = z_top - z_pocket_top
    pdf.line(arrow_x, zy(z_pocket_top), arrow_x, zy(z_top))
    pdf._label(arrow_x - 9, (zy(z_pocket_top) + zy(z_top)) / 2 + 1.5,
               f"{seal_top:.1f}mm", size=5, color=COLOR_GRAY)

    return draw_h + 18


def draw_wiring_diagram(pdf: AssemblyGuide, x0, y0):
    """Draw a schematic-style wiring diagram showing Pi connected to all peripherals."""
    total_h = 115
    pdf._ensure_space(total_h + 10)
    y0 = pdf.get_y() + 2

    pdf._label(x0, y0, "Wiring Overview", size=9, color=COLOR_DARK, bold=True)
    y0 += 7

    # Central Pi
    pi_x = x0 + 55
    pi_y = y0 + 20
    pi_w = 45
    pi_h = 65
    pdf._component_box(pi_x, pi_y, pi_w, pi_h, "", (180, 230, 180))
    pdf._label(pi_x + 5, pi_y + 8, "Raspberry Pi", size=7, color=COLOR_DARK, bold=True)
    pdf._label(pi_x + 7, pi_y + 14, "Zero 2 W", size=7, color=COLOR_DARK, bold=True)

    # Pin labels on Pi box
    pi_pins_left = [
        (pi_y + 22, "3V3", PIN_POWER),
        (pi_y + 28, "GP8 (CE0)", PIN_SPI),
        (pi_y + 34, "GP10 (MOSI)", PIN_SPI),
        (pi_y + 40, "GP9 (MISO)", PIN_SPI),
        (pi_y + 46, "GP11 (SCLK)", PIN_SPI),
        (pi_y + 52, "GP25 (RST)", PIN_GPIO),
        (pi_y + 58, "GND", PIN_GND),
    ]
    for py_pin, lbl, col in pi_pins_left:
        pdf.set_fill_color(*col)
        pdf.ellipse(pi_x - 1.5, py_pin - 1.5, 3, 3, "F")
        pdf._label(pi_x + 2, py_pin + 1.5, lbl, size=4.5, color=col)

    pi_pins_right = [
        (pi_y + 22, "5V", PIN_POWER),
        (pi_y + 30, "GP18 (PWM0)", PIN_PWM),
        (pi_y + 38, "GP17", PIN_GPIO),
        (pi_y + 44, "GP27", PIN_GPIO),
        (pi_y + 52, "GP12 (PWM1)", PIN_PWM),
        (pi_y + 58, "GND", PIN_GND),
    ]
    for py_pin, lbl, col in pi_pins_right:
        pdf.set_fill_color(*col)
        pdf.ellipse(pi_x + pi_w - 1.5, py_pin - 1.5, 3, 3, "F")
        pdf._label(pi_x + pi_w - 26, py_pin + 1.5, lbl, size=4.5, color=col)

    # ── MFRC522 (left side) ──
    rfid_x = x0
    rfid_y = y0 + 15
    rfid_w = 35
    rfid_h = 50
    pdf._component_box(rfid_x, rfid_y, rfid_w, rfid_h, "", (200, 210, 240))
    pdf._label(rfid_x + 5, rfid_y + 7, "MFRC522", size=7, color=COLOR_DARK, bold=True)
    pdf._label(rfid_x + 3, rfid_y + 13, "RFID Module", size=6, color=COLOR_GRAY)

    # RFID pins
    rfid_pins = ["3V3", "SDA", "MOSI", "MISO", "SCK", "RST", "GND"]
    rfid_colors = [WIRE_RED, WIRE_YELLOW, WIRE_GREEN, WIRE_BLUE, WIRE_ORANGE, WIRE_WHITE, WIRE_BLACK]
    for i, (pin, wcol) in enumerate(zip(rfid_pins, rfid_colors)):
        py = rfid_y + 18 + i * 5
        pdf._label(rfid_x + 4, py + 1.5, pin, size=5, color=COLOR_DARK)
        # Wire to Pi
        pdf._wire(rfid_x + rfid_w, py, pi_x - 1.5, pi_pins_left[i][0], wcol)

    # Wire color legend for RFID
    pdf._label(rfid_x, rfid_y + rfid_h + 3, "Wire colors:", size=5, color=COLOR_GRAY)
    legend_wires = [("Red=3V3", WIRE_RED), ("Yel=SDA", WIRE_YELLOW), ("Grn=MOSI", WIRE_GREEN),
                    ("Blu=MISO", WIRE_BLUE), ("Org=SCK", WIRE_ORANGE), ("Wht=RST", WIRE_WHITE),
                    ("Blk=GND", WIRE_BLACK)]
    for i, (lbl, col) in enumerate(legend_wires):
        ly = rfid_y + rfid_h + 8 + i * 4
        pdf.set_draw_color(*col)
        pdf.set_line_width(1)
        pdf.line(rfid_x, ly, rfid_x + 5, ly)
        pdf._label(rfid_x + 7, ly + 1.5, lbl, size=4.5, color=col)

    # ── WS2812 LED Strip (upper right) ──
    led_x = pi_x + pi_w + 25
    led_y = y0 + 10
    led_w = 55
    led_h = 14
    pdf._component_box(led_x, led_y, led_w, led_h, "", (255, 240, 200))
    pdf._label(led_x + 4, led_y + 6, "WS2812", size=6, color=COLOR_DARK, bold=True)
    pdf._label(led_x + 4, led_y + 11, "8-LED Strip", size=5, color=COLOR_GRAY)
    # LED dots
    for i in range(8):
        c = [(255, 60, 60), (255, 140, 0), (255, 220, 0), (60, 220, 60),
             (60, 180, 255), (80, 80, 255), (180, 60, 255), (255, 60, 180)][i]
        pdf.set_fill_color(*c)
        pdf.ellipse(led_x + 22 + i * 4, led_y + 2, 3, 3, "F")

    # LED wires
    pin_5v = pi_pins_right[0]  # 5V
    pin_gp18 = pi_pins_right[1]  # GP18
    pin_gnd_r = pi_pins_right[5]  # GND

    pdf._wire(pi_x + pi_w + 1.5, pin_gp18[0], led_x, led_y + 5, WIRE_GREEN, "DIN")
    pdf._wire(pi_x + pi_w + 1.5, pin_5v[0], led_x, led_y + 9, WIRE_RED, "5V")
    pdf._wire(pi_x + pi_w + 1.5, pin_gnd_r[0], led_x, led_y + 12, WIRE_BLACK, "GND")

    # ── Buttons (middle right) ──
    btn_x = pi_x + pi_w + 25
    btn_y = y0 + 35

    # Play/pause button
    pdf.set_fill_color(80, 180, 80)
    pdf.set_draw_color(60, 60, 60)
    pdf.set_line_width(0.4)
    pdf.ellipse(btn_x + 5, btn_y, 12, 12, "DF")
    pdf._label(btn_x + 8, btn_y + 7, ">||", size=5, color=(255, 255, 255))
    pdf._label(btn_x + 20, btn_y + 7, "Play/Pause", size=6, color=COLOR_DARK)

    pdf._wire(pi_x + pi_w + 1.5, pi_pins_right[2][0], btn_x + 5, btn_y + 6,
              WIRE_YELLOW, "GP17")
    pdf._wire(btn_x + 17, btn_y + 6, btn_x + 40, btn_y + 6, WIRE_BLACK, "GND")

    # Stop button
    btn2_y = btn_y + 18
    pdf.set_fill_color(200, 80, 80)
    pdf.ellipse(btn_x + 5, btn2_y, 12, 12, "DF")
    pdf._label(btn_x + 9, btn2_y + 7, "[ ]", size=5, color=(255, 255, 255))
    pdf._label(btn_x + 20, btn2_y + 7, "Stop", size=6, color=COLOR_DARK)

    pdf._wire(pi_x + pi_w + 1.5, pi_pins_right[3][0], btn_x + 5, btn2_y + 6,
              WIRE_YELLOW, "GP27")
    pdf._wire(btn_x + 17, btn2_y + 6, btn_x + 40, btn2_y + 6, WIRE_BLACK, "GND")

    # ── Buzzer (lower right) ──
    buz_x = pi_x + pi_w + 25
    buz_y = y0 + 78
    pdf.set_fill_color(220, 200, 180)
    pdf.set_draw_color(60, 60, 60)
    pdf.set_line_width(0.4)
    pdf.ellipse(buz_x + 5, buz_y, 14, 14, "DF")
    pdf._label(buz_x + 8, buz_y + 9, "Buz", size=6, color=COLOR_DARK)
    pdf._label(buz_x + 22, buz_y + 7, "Passive Buzzer", size=6, color=COLOR_DARK)

    pdf._wire(pi_x + pi_w + 1.5, pi_pins_right[4][0], buz_x + 5, buz_y + 5,
              WIRE_YELLOW, "GP12")
    pdf._wire(pi_x + pi_w + 1.5, pi_pins_right[5][0], buz_x + 5, buz_y + 10,
              WIRE_BLACK, "GND")

    # ── Output labels (bottom) ──
    out_y = y0 + total_h - 10
    pdf.set_draw_color(*COLOR_ACCENT)
    pdf.set_line_width(0.5)

    # HDMI arrow
    pdf.line(pi_x + pi_w / 2 - 10, pi_y + pi_h, pi_x + pi_w / 2 - 10, out_y)
    pdf._label(pi_x + pi_w / 2 - 22, out_y + 4, "HDMI -> TV", size=6, color=COLOR_ACCENT)

    # Bluetooth arrow
    pdf.set_draw_color(80, 80, 200)
    pdf.line(pi_x + pi_w / 2 + 10, pi_y + pi_h, pi_x + pi_w / 2 + 10, out_y)
    pdf._label(pi_x + pi_w / 2 + 2, out_y + 4, "BT -> Speaker", size=6, color=(80, 80, 200))

    return total_h + 10


def draw_figurine_cross_section(pdf: AssemblyGuide, x0, y0):
    """Draw figurine + lid stacking cross-section showing magnet attraction."""
    total_h = 70
    pdf._ensure_space(total_h + 10)
    y0 = pdf.get_y() + 2

    pdf._label(x0, y0, "Figurine on Lid - Cross Section (assembled)", size=8,
               color=COLOR_DARK, bold=True)
    y0 += 8

    w = 120
    cx = x0 + w / 2

    # Lid (bottom part in this view - box surface)
    lid_y = y0 + 35
    lid_h = 14
    pdf.set_fill_color(180, 200, 220)
    pdf.set_draw_color(80, 80, 80)
    pdf.set_line_width(0.4)
    pdf.rect(x0 + 15, lid_y, w - 30, lid_h, "DF")
    pdf._label(x0 + 18, lid_y + lid_h - 2, "Lid top wall (3mm)", size=5, color=(80, 80, 80))

    # Lid magnets
    for mx in [cx - 15, cx + 15]:
        pdf.set_fill_color(160, 160, 170)
        pdf.rect(mx - 5, lid_y + 3, 10, 5, "DF")
        pdf._label(mx - 1, lid_y + 2, "N", size=5, color=COLOR_ACCENT, bold=True)
        pdf._label(mx - 1, lid_y + 10.5, "S", size=5, color=COLOR_RED, bold=True)

    # MFRC522 below lid
    rfid_y = lid_y + lid_h + 3
    pdf._component_box(cx - 22, rfid_y, 44, 8, "MFRC522 antenna", (200, 210, 240))

    # Signal waves from RFID
    pdf.set_draw_color(100, 180, 255)
    pdf.set_line_width(0.3)
    for i in range(3):
        wy = lid_y - 2 - i * 3
        half_w = 8 + i * 4
        pdf.ellipse(cx - half_w, wy - 1, 2 * half_w, 2, "D")

    # Figurine base (above lid)
    base_y = y0 + 8
    base_h = 25
    pdf.set_fill_color(200, 220, 200)
    pdf.set_draw_color(80, 80, 80)
    pdf.rect(x0 + 25, base_y, w - 50, base_h, "DF")
    pdf._label(x0 + 28, base_y + 5, "Figurine base (6mm)", size=5, color=(80, 80, 80))

    # Figurine magnets
    for mx in [cx - 15, cx + 15]:
        pdf.set_fill_color(160, 160, 170)
        pdf.rect(mx - 5, base_y + base_h - 9, 10, 5, "DF")
        pdf._label(mx - 1, base_y + base_h - 10, "N", size=5, color=COLOR_ACCENT, bold=True)
        pdf._label(mx - 1, base_y + base_h - 2, "S", size=5, color=COLOR_RED, bold=True)

    # RFID sticker on bottom of base
    pdf.set_fill_color(255, 230, 180)
    pdf.rect(cx - 16, base_y + base_h - 2, 32, 2, "DF")
    pdf._label(cx + 18, base_y + base_h - 1, "RFID sticker", size=5, color=(180, 130, 40))

    # Decorative top
    pdf.set_fill_color(100, 200, 100)
    pdf.set_draw_color(60, 140, 60)
    pdf.ellipse(cx - 10, base_y - 10, 20, 12, "DF")
    pdf._label(cx - 12, base_y - 14, "Figurine top (decorative)", size=5, color=COLOR_GREEN)

    # Attraction arrows between magnets
    pdf.set_draw_color(*COLOR_RED)
    pdf.set_line_width(0.6)
    for mx in [cx - 15, cx + 15]:
        # Arrow from base magnet down to lid magnet (attraction)
        a_y1 = base_y + base_h - 3
        a_y2 = lid_y + 4
        mid_y = (a_y1 + a_y2) / 2
        pdf.line(mx, a_y1, mx, a_y2)
        # Arrowheads pointing inward (attraction)
        pdf.line(mx - 1.5, a_y1 - 2, mx, a_y1)
        pdf.line(mx + 1.5, a_y1 - 2, mx, a_y1)
        pdf.line(mx - 1.5, a_y2 + 2, mx, a_y2)
        pdf.line(mx + 1.5, a_y2 + 2, mx, a_y2)

    pdf._label(cx + 25, (base_y + base_h + lid_y) / 2 + 1, "ATTRACT", size=6,
               color=COLOR_RED, bold=True)

    # Gap annotation
    pdf._label(x0 + w - 8, lid_y - 3, "~0mm gap", size=5, color=COLOR_GRAY)
    pdf._label(x0 + w - 8, lid_y - 7, "(magnets snap", size=4.5, color=COLOR_GRAY)
    pdf._label(x0 + w - 8, lid_y - 4, "together)", size=4.5, color=COLOR_GRAY)

    # Distance annotation to RFID
    pdf.set_draw_color(*COLOR_GRAY)
    pdf.set_line_width(0.2)
    brace_x = x0 + 12
    pdf.line(brace_x, base_y + base_h - 1, brace_x, rfid_y)
    pdf._label(brace_x - 12, (base_y + base_h + rfid_y) / 2 + 1, "~8mm", size=5,
               color=COLOR_GRAY)

    return total_h


def draw_lid_bottom_view(pdf: AssemblyGuide, x0, y0):
    """Draw the lid from below showing RFID module and magnet positions."""
    s = 0.65
    w = 150 * s
    h = 110 * s

    pdf._label(x0, y0, "Lid - Bottom View (looking up into the lid)",
               size=8, color=COLOR_DARK, bold=True)
    y0 += 6

    # Outer rectangle
    pdf.set_fill_color(220, 230, 240)
    pdf.set_draw_color(80, 80, 80)
    pdf.set_line_width(0.4)
    pdf._rounded_rect(x0, y0, w, h, 3, "DF")

    cx = x0 + w / 2
    cy = y0 + h / 2

    # MFRC522 module (centered)
    rfid_w = 60 * s
    rfid_h = 40 * s
    pdf._component_box(cx - rfid_w / 2, cy - rfid_h / 2, rfid_w, rfid_h,
                       "MFRC522", (200, 210, 240))

    # 4 standoffs
    sx = 56 * s / 2
    sy = 36 * s / 2
    for dx, dy in [(-sx, -sy), (sx, -sy), (-sx, sy), (sx, sy)]:
        pdf.set_fill_color(150, 150, 150)
        pdf.ellipse(cx + dx - 2, cy + dy - 2, 4, 4, "DF")

    # Magnet bosses
    for dx in [-10 * s, 10 * s]:
        pdf.set_fill_color(160, 160, 170)
        pdf.set_draw_color(100, 100, 100)
        mag_r = 5
        pdf.ellipse(cx + dx * 2 - mag_r, cy - mag_r, mag_r * 2, mag_r * 2, "DF")
        pdf._label(cx + dx * 2 - 3, cy + 2, "mag", size=4.5, color=(80, 80, 80))

    # Figurine ring (engraved on outer surface, shown as dashed circle)
    ring_r = 18 * s
    pdf.set_draw_color(*COLOR_ACCENT)
    pdf.set_line_width(0.6)
    # Approximate circle with segments
    import math
    n_seg = 24
    for i in range(0, n_seg, 2):
        a1 = 2 * math.pi * i / n_seg
        a2 = 2 * math.pi * (i + 1) / n_seg
        pdf.line(cx + ring_r * math.cos(a1), cy + ring_r * math.sin(a1),
                 cx + ring_r * math.cos(a2), cy + ring_r * math.sin(a2))

    pdf._label(cx + ring_r + 3, cy + 2, "figurine ring", size=5, color=COLOR_ACCENT)

    # Screw holes (4 corners)
    inset = 8 * s
    for px, py in [(x0 + inset, y0 + inset), (x0 + w - inset, y0 + inset),
                   (x0 + inset, y0 + h - inset), (x0 + w - inset, y0 + h - inset)]:
        pdf.set_fill_color(100, 100, 100)
        pdf.ellipse(px - 2, py - 2, 4, 4, "DF")
        pdf.set_fill_color(220, 230, 240)
        pdf.ellipse(px - 1, py - 1, 2, 2, "F")

    # Lip outline
    lip_inset = 3.4 * s
    pdf.set_draw_color(160, 160, 180)
    pdf.set_line_width(0.3)
    pdf._rounded_rect(x0 + lip_inset * 3, y0 + lip_inset * 3,
                      w - lip_inset * 6, h - lip_inset * 6, 2, "D")
    pdf._label(x0 + lip_inset * 3 + 2, y0 + lip_inset * 3 + 4,
               "nesting lip", size=4.5, color=(160, 160, 180))

    return h + 12


# ─────────────────────────────────────────────────────────────
# Section functions
# ─────────────────────────────────────────────────────────────

def cover_page(pdf: AssemblyGuide):
    pdf.add_page()
    pdf.ln(25)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(*COLOR_DARK)
    pdf.cell(0, 14, "BabyBox", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(*COLOR_ACCENT)
    pdf.cell(0, 10, "Assembly Guide", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(0, 7, "Toddler Media Player  |  Raspberry Pi Zero 2 W + RFID + 3D Printing",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    draw_cover_enclosure(pdf, pdf.w / 2, pdf.get_y())
    pdf.set_y(pdf.get_y() + 75)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(0, 6, f"Generated {date.today().isoformat()}", align="C",
             new_x="LMARGIN", new_y="NEXT")


def render_toc(pdf: AssemblyGuide, outline):
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*COLOR_DARK)
    pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    for entry in outline:
        if entry.level > 1:
            continue
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*COLOR_DARK)
        label = entry.name
        page = entry.page_number
        w = pdf.w - 2 * pdf.MARGIN
        label_w = pdf.get_string_width(label) + 4
        page_str = str(page)
        page_w = pdf.get_string_width(page_str) + 4
        dot_w = w - label_w - page_w
        dots = " ." * int(dot_w / pdf.get_string_width(" ."))
        pdf.cell(label_w, 7, label, new_x="END")
        pdf.set_text_color(*COLOR_GRAY)
        pdf.cell(dot_w, 7, dots, new_x="END")
        pdf.set_text_color(*COLOR_DARK)
        pdf.cell(page_w, 7, page_str, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)


def sec_bom(pdf: AssemblyGuide):
    pdf.section_title("Bill of Materials")
    pdf.body_text(
        "Everything you need to build a BabyBox. Most electronic components come from "
        "a standard sensor kit. The total cost is approximately $51 if you already own "
        "a Bluetooth speaker."
    )
    pdf.make_table(
        headers=["Component", "Qty", "Source", "Est. Cost"],
        rows=BOM,
        col_widths=[75, 12, 45, 35],
    )
    pdf.note_box(
        "Magnets must be 6 x 3 mm neodymium discs. Larger magnets will not fit the "
        "printed pockets. Buy extras -- you need at least 4 per figurine (2 for the "
        "figurine base + 2 for the lid) plus spares for polarity mistakes.",
        kind="NOTE",
    )


def sec_gpio(pdf: AssemblyGuide):
    pdf.section_title("GPIO Wiring Reference")
    pdf.body_text(
        "All connections use the Raspberry Pi Zero 2 W 40-pin header. "
        "SPI must be enabled in raspi-config for the MFRC522. "
        "Buttons use internal pull-ups (active low)."
    )
    pdf.make_table(
        headers=["Signal", "Pin", "Notes"],
        rows=GPIO_PINS,
        col_widths=[45, 30, 92],
    )

    pdf.subsection("Pin Diagram (color-coded by function)")
    y_before = pdf.get_y()
    h = draw_gpio_header(pdf, pdf.MARGIN + 10, pdf.get_y())
    pdf.set_y(y_before + h + 4)


def sec_3d_printing(pdf: AssemblyGuide):
    pdf.section_title("3D Printing")
    pdf.body_text(
        "The BabyBox has three printed parts: the enclosure body, the lid, and "
        "figurine bases. All parts are designed in OpenSCAD and printed on a "
        "Bambu Lab P2S (or any FDM printer with a 256 x 256 mm bed)."
    )

    pdf.subsection("Recommended Print Settings")
    settings_rows = [(k, v) for k, v in PRINT_SETTINGS.items()]
    pdf.make_table(
        headers=["Parameter", "Value"],
        rows=settings_rows,
        col_widths=[60, 107],
    )

    pdf.subsection("Part A: Enclosure Body")
    pdf.body_text(
        f"Dimensions: {ENCLOSURE['outer_l']} x {ENCLOSURE['outer_w']} x "
        f"{ENCLOSURE['body_h']} mm (body height without lid).\n"
        f"Wall thickness: {ENCLOSURE['wall']} mm. Corner radius: {ENCLOSURE['corner_r']} mm.\n"
        f"Floor thickness: {ENCLOSURE['floor_h']} mm."
    )
    pdf.bullet_list([
        "Print UPRIGHT (open top facing up). No supports needed.",
        "The breadboard bay is a recess in the floor -- prints as part of the body.",
        "Four M3 screw posts at the corners accept screws from the lid.",
        "Button holes (12 mm dia) and LED window (55 mm wide) are on the front wall.",
        "Port cutouts (mini-HDMI, 2x micro-USB, microSD) are on the back/side walls.",
    ])

    # Drawn top view
    y_before = pdf.get_y()
    pdf._ensure_space(110)
    h = draw_enclosure_top_view(pdf, pdf.MARGIN + 10, pdf.get_y())
    pdf.set_y(pdf.get_y() + h + 2)

    pdf.subsection("Part B: Enclosure Lid")
    pdf.body_text(
        f"Dimensions: {ENCLOSURE['outer_l']} x {ENCLOSURE['outer_w']} x "
        f"{ENCLOSURE['lid_h']} mm.\n"
        "The lid has a 3 mm nesting lip that fits inside the body opening."
    )
    pdf.bullet_list([
        "Print UPSIDE-DOWN (top surface on the build plate for a smooth finish).",
        "RFID module (MFRC522) mounts on standoffs hanging from the ceiling.",
        "Two magnet bosses enclose the neodymium magnets (see Section 4).",
        "A 36 mm engraved ring on the top surface marks the figurine placement zone.",
        "Four M3 clearance holes at the corners align with the body screw posts.",
    ])

    # Lid bottom view diagram
    pdf._ensure_space(90)
    h = draw_lid_bottom_view(pdf, pdf.MARGIN + 15, pdf.get_y())
    pdf.set_y(pdf.get_y() + h + 2)

    pdf.subsection("Part C: Figurine Base")
    pdf.body_text(
        f"Diameter: {FIGURINE_BASE['dia']} mm. Height: {FIGURINE_BASE['height']} mm.\n"
        f"Chamfer: {FIGURINE_BASE['chamfer']} mm on the bottom edge.\n"
        "All figurines share the same base for consistent magnet alignment."
    )
    pdf.bullet_list([
        "Print RIGHT-SIDE UP (flat bottom on build plate).",
        "Two magnet pockets (6.3 mm dia, 3.2 mm deep) spaced 20 mm apart.",
        "Shallow RFID recess (25.5 mm dia, 0.5 mm deep) on the bottom face.",
        "Magnets inserted via pause-and-insert at Z = 4.2 mm (see Section 4).",
    ])


def sec_magnets(pdf: AssemblyGuide):
    pdf.section_title("Hidden Magnet Insertion")

    pdf.note_box(
        "Neodymium magnets are extremely dangerous if swallowed by a child. "
        "The pause-and-insert technique fully encloses each magnet inside solid "
        "plastic with no access points. NEVER leave magnets accessible. "
        "Always verify the seal layers printed correctly after resuming.",
        kind="WARNING",
    )

    pdf.body_text(
        "Both the lid and figurine bases use the same technique: the print is paused "
        "at a specific Z height, magnets are dropped into the open cavities, and "
        "printing resumes to seal them with solid layers above."
    )

    pdf.subsection("Pause Heights")
    pdf.make_table(
        headers=["Part", "Pause Z", "Seal below", "Cavity", "Seal above"],
        rows=[
            ("Figurine base (right-side up)", "4.2 mm",
             f"{MAGNETS['seal_h']} mm", f"{MAGNETS['pocket_h']} mm",
             f"{FIGURINE_BASE['height'] - MAGNETS['seal_h'] - MAGNETS['pocket_h']} mm"),
            ("Lid (upside-down)", "4.2 mm",
             f"{MAGNETS['seal_h']} mm", f"{MAGNETS['pocket_h']} mm",
             f"~{ENCLOSURE['wall'] - MAGNETS['seal_h']} mm (top wall)"),
        ],
        col_widths=[55, 22, 25, 22, 43],
    )

    pdf.subsection("Step-by-Step Procedure")
    pdf.numbered_steps([
        "Slice the part in Bambu Studio and add a pause (M600) at the target Z height. "
        "For both figurine bases and the lid, pause at Z = 4.2 mm.",
        "Start the print. When the printer pauses, the cavities will be open cylinders "
        "with a solid floor of 1.0 mm below.",
        "Check magnet polarity BEFORE inserting! Use a reference magnet taped to the "
        "build plate with the correct pole facing up. Each new magnet must ATTRACT the "
        "reference (i.e., opposite poles face each other).",
        "Drop one magnet into each cavity. It should sit flush or slightly below the rim. "
        "If it sticks up, the pocket depth is wrong -- do not continue.",
        "Resume the print. The printer will lay solid layers over the magnets, "
        "permanently sealing them inside.",
        "After the print completes, verify the top surface is smooth and fully sealed. "
        "Try to feel or pry out the magnets -- you should not be able to.",
    ])

    # Drawn cross-sections
    pdf.subsection("Figurine Base Cross-Section")
    h = draw_magnet_cross_section(pdf, pdf.MARGIN, pdf.get_y(), part="base")
    pdf.set_y(pdf.get_y() + h + 2)

    pdf.subsection("Lid Cross-Section (printed upside-down)")
    h = draw_magnet_cross_section(pdf, pdf.MARGIN, pdf.get_y(), part="lid")
    pdf.set_y(pdf.get_y() + h + 2)

    pdf.subsection("Polarity Reference")
    pdf.body_text(
        "All magnets in the BabyBox must have matching polarity so figurine magnets "
        "ATTRACT the lid magnets. Use this system:"
    )
    pdf.numbered_steps([
        "Mark one magnet with a dot of paint on its NORTH face. This is your reference.",
        "When inserting magnets into the LID (printed upside-down), place them with "
        "the NORTH (dotted) face UP (toward you, away from the build plate).",
        "When inserting magnets into FIGURINE BASES, place them with the SOUTH "
        "(un-dotted) face UP.",
        "Test: after both parts are printed, place the figurine on the lid. "
        "The magnets should snap together firmly.",
    ])

    # Assembled view
    pdf.subsection("Assembled View: Figurine on Lid")
    h = draw_figurine_cross_section(pdf, pdf.MARGIN + 15, pdf.get_y())
    pdf.set_y(pdf.get_y() + h + 2)


def sec_electronics(pdf: AssemblyGuide):
    pdf.section_title("Electronics Mounting")

    pdf.subsection("Raspberry Pi Zero 2 W")
    pdf.body_text(
        "The Pi mounts on four M2.5 standoffs (5 mm tall) near the back-left corner "
        "of the enclosure body. Use M2.5 x 6 mm screws from above."
    )
    pdf.bullet_list([
        "Ports face the back wall: mini-HDMI, 2x micro-USB (OTG + power).",
        "The microSD slot faces the left side wall.",
        "Ensure the Pi sits level and does not contact the floor (standoffs provide clearance).",
        "Flash Raspberry Pi OS Lite to the SD card before mounting.",
    ])

    pdf.subsection("MFRC522 RFID Module")
    pdf.body_text(
        "The MFRC522 mounts on four M2 standoffs hanging from the lid ceiling, "
        "centered on the lid. The antenna faces upward toward the figurine placement zone."
    )
    pdf.bullet_list([
        "Module dimensions: 60 x 40 x 4 mm (8 mm with header pins).",
        "Mounting holes: M2, spaced 56 x 36 mm.",
        "Use M2 x 8 mm screws from below (through the standoffs into the module).",
        "The module must sit as close to the lid's inner ceiling as possible for best read range.",
        "Total distance to figurine RFID tag: ~3 mm wall + ~5 mm figurine base = ~8 mm "
        "(well within the 30 mm read range).",
    ])

    pdf.subsection("Half Breadboard")
    pdf.body_text(
        "A half-size breadboard (82 x 55 mm) sits in a recessed bay in the enclosure floor. "
        "This provides a prototyping area for wiring the MFRC522, buttons, buzzer, "
        "and LED strip without soldering."
    )
    pdf.bullet_list([
        "The bay is 83 x 56 mm (with 0.5 mm tolerance per side).",
        "The breadboard sits flush with the floor surface.",
        "Peel off the adhesive backing and press into the bay, or leave it friction-fit.",
    ])

    pdf.subsection("Buttons")
    pdf.body_text(
        "Two 6x6 mm tactile buttons mount through 12 mm holes in the front wall. "
        "Use button caps (12 mm round) for a toddler-friendly surface."
    )
    pdf.bullet_list([
        "Left button (Play/Pause): GPIO 17, with internal pull-up.",
        "Right button (Stop): GPIO 27, with internal pull-up.",
        "Buttons are spaced 60 mm apart, centered on the front wall.",
        "Wire one leg to the GPIO pin and the opposite leg to GND.",
    ])

    pdf.subsection("WS2812 LED Strip")
    pdf.body_text(
        "An 8-LED WS2812 strip (51 x 10 mm) mounts behind the LED window on the "
        "front wall. The LEDs shine outward through the window slot."
    )
    pdf.bullet_list([
        "Window dimensions: 55 mm wide x 12 mm tall.",
        "A 5 mm deep channel behind the window holds the strip.",
        "Adhere the strip with its self-adhesive backing, LEDs facing outward.",
        "DIN connects to GPIO 18 (PWM0). 5V and GND to the Pi header.",
    ])

    pdf.subsection("Passive Buzzer")
    pdf.body_text(
        "A 12 mm passive buzzer sits in a ring cradle in the back-right corner of the floor."
    )
    pdf.bullet_list([
        "Cradle outer diameter: 15 mm, inner: 12.4 mm.",
        "Signal pin connects to GPIO 12 (PWM1). GND to any ground pin.",
        "Passive buzzers require a PWM signal to produce tones (unlike active buzzers).",
    ])


def sec_wiring(pdf: AssemblyGuide):
    pdf.section_title("Wiring Guide")
    pdf.body_text(
        "All wiring goes through the half breadboard. Use jumper wires (male-to-female "
        "for the Pi header, male-to-male for the breadboard)."
    )

    # Full wiring diagram
    h = draw_wiring_diagram(pdf, pdf.MARGIN, pdf.get_y())
    pdf.set_y(pdf.get_y() + h + 4)

    pdf.subsection("MFRC522 RFID Module (7 wires)")
    pdf.make_table(
        headers=["MFRC522 Pin", "Wire Color (suggested)", "Pi Header Pin"],
        rows=[
            ("SDA",  "Yellow", "GPIO 8  (Pin 24, CE0)"),
            ("SCK",  "Orange", "GPIO 11 (Pin 23, SCLK)"),
            ("MOSI", "Green",  "GPIO 10 (Pin 19, MOSI)"),
            ("MISO", "Blue",   "GPIO 9  (Pin 21, MISO)"),
            ("RST",  "White",  "GPIO 25 (Pin 22)"),
            ("3.3V", "Red",    "3.3 V   (Pin 1 or 17)"),
            ("GND",  "Black",  "GND     (Pin 6)"),
        ],
        col_widths=[40, 50, 77],
    )

    pdf.note_box(
        "The MFRC522 operates at 3.3 V. NEVER connect it to 5 V -- this will "
        "permanently damage the module.",
        kind="WARNING",
    )

    pdf.subsection("WS2812 LED Strip (3 wires)")
    pdf.make_table(
        headers=["LED Pin", "Wire Color", "Pi Header Pin"],
        rows=[
            ("DIN", "Green", "GPIO 18 (Pin 12, PWM0)"),
            ("5V",  "Red",   "5 V     (Pin 2 or 4)"),
            ("GND", "Black", "GND     (Pin 9)"),
        ],
        col_widths=[40, 50, 77],
    )

    pdf.subsection("Buttons (4 wires total)")
    pdf.make_table(
        headers=["Button", "Leg A", "Leg B"],
        rows=[
            ("Play/Pause", "GPIO 17 (Pin 11)", "GND (Pin 14)"),
            ("Stop",       "GPIO 27 (Pin 13)", "GND (Pin 14 or 20)"),
        ],
        col_widths=[45, 60, 62],
    )
    pdf.body_text(
        "No external pull-up resistors needed -- the software enables internal pull-ups."
    )

    pdf.subsection("Passive Buzzer (2 wires)")
    pdf.make_table(
        headers=["Buzzer Pin", "Wire Color", "Pi Header Pin"],
        rows=[
            ("Signal (+)", "Yellow", "GPIO 12 (Pin 32, PWM1)"),
            ("GND (-)",    "Black",  "GND     (Pin 34)"),
        ],
        col_widths=[40, 50, 77],
    )

    pdf.note_box(
        "Route wires neatly and keep them away from the RFID antenna area in the lid. "
        "Loose wires near the MFRC522 can cause interference and reduce read range.",
        kind="NOTE",
    )


def sec_figurines(pdf: AssemblyGuide):
    pdf.section_title("Figurine Construction")

    pdf.subsection("Base Printing")
    pdf.body_text(
        f"All figurines share a standard base: {FIGURINE_BASE['dia']} mm diameter, "
        f"{FIGURINE_BASE['height']} mm tall. The base has two magnet pockets "
        f"({MAGNETS['pocket_dia']} mm dia, {MAGNETS['pocket_h']} mm deep) "
        f"spaced {MAGNETS['spacing']} mm apart, and a shallow RFID recess "
        f"({FIGURINE_BASE['rfid_recess_dia']} mm dia) on the bottom."
    )
    pdf.numbered_steps([
        "Open hardware/figurines/base-template.scad in OpenSCAD.",
        "Set render_part = \"base\" and press F6 to render.",
        "Export as STL. Import into Bambu Studio.",
        "Use PETG, 0.2 mm layer height, 20% infill.",
        "Add a pause at Z = 4.2 mm for magnet insertion.",
        "Print right-side up (flat bottom on bed).",
    ])

    pdf.subsection("Magnet Insertion")
    pdf.body_text(
        "Follow the procedure in Section 4 (Hidden Magnet Insertion). "
        "Insert magnets at the pause, with the correct polarity (SOUTH face up for bases)."
    )

    pdf.subsection("RFID Sticker Application")
    pdf.numbered_steps([
        "Take a 25 mm MIFARE 13.56 MHz coin sticker.",
        "Peel off the backing to expose the adhesive.",
        "Center the sticker on the BOTTOM face of the figurine base, inside the "
        f"shallow recess ({FIGURINE_BASE['rfid_recess_dia']} mm dia).",
        "Press firmly. The sticker should sit flush in the recess.",
        "Test: hold the base near the MFRC522 module. The tag UID should be read "
        "successfully at up to ~25 mm distance.",
    ])

    pdf.subsection("Figurine Top (Decorative Shell)")
    pdf.body_text(
        "The top part of each figurine is the decorative character or object that "
        "the child interacts with. There are two approaches:"
    )

    pdf.bold_text("Option A: AI-Generated (Meshy AI + Blender)")
    pdf.numbered_steps([
        "Go to meshy.ai and generate a 3D model from a text prompt "
        "(e.g., \"cute cartoon dinosaur, low poly, smooth\").",
        "Download the model as OBJ or GLB.",
        "Open Blender. Import the Meshy model and the figurine base STL.",
        "Position the decorative top on top of the base. Boolean-union them together.",
        "Verify the magnet pockets and RFID recess are not obstructed.",
        "Export as STL. Slice in Bambu Studio and print.",
    ])

    pdf.bold_text("Option B: Simple Geometric Shape (OpenSCAD)")
    pdf.body_text(
        "For simpler figurines, you can add a geometric top directly in OpenSCAD "
        "(cylinder, sphere, cone, etc.) on top of the base template."
    )

    pdf.subsection("Figurine Design Guidelines")
    pdf.bullet_list([
        "Total height: 40-60 mm (base + top). Easy for toddler hands.",
        "Base diameter: 35 mm (standardized for magnet alignment).",
        "No small detachable parts. Everything is one solid piece after assembly.",
        "Bright colors. Multi-color prints possible with Bambu AMS.",
        "Minimal overhangs to avoid supports.",
        "Test each figurine on the box before giving to the child.",
    ])


def sec_final_assembly(pdf: AssemblyGuide):
    pdf.section_title("Final Assembly Sequence")
    pdf.body_text(
        "Follow these steps in order to assemble a complete BabyBox from printed "
        "parts and electronics."
    )

    pdf.numbered_steps([
        "Print the enclosure BODY (Part A). Inspect for clean button holes, "
        "LED window, port cutouts, and screw posts.",

        "Print the enclosure LID (Part B) upside-down. Pause at Z = 4.2 mm and "
        "insert 2x magnets (NORTH face up). Resume and let it complete.",

        "Print at least 2 figurine BASES (Part C). Pause at Z = 4.2 mm and "
        "insert 2x magnets per base (SOUTH face up). Resume and complete.",

        "Test magnet polarity: place a figurine base on the lid. The magnets "
        "should snap together firmly and align the base over the engraved ring.",

        "Mount the Raspberry Pi Zero 2 W on its standoffs in the body using "
        "4x M2.5 screws. Ports face the back wall.",

        "Mount the MFRC522 RFID module on its standoffs under the lid ceiling "
        "using 4x M2 screws. Antenna faces upward.",

        "Place the half breadboard in the floor recess. Press down to seat it.",

        "Wire the MFRC522 to the Pi header (7 wires: SDA, SCK, MOSI, MISO, "
        "RST, 3.3V, GND). Route wires through the breadboard.",

        "Wire the WS2812 LED strip (DIN to GPIO 18, 5V, GND). Adhere the strip "
        "behind the LED window with LEDs facing outward.",

        "Wire the two buttons (Play/Pause to GPIO 17 + GND, Stop to GPIO 27 + GND). "
        "Mount buttons through the front wall holes with caps.",

        "Wire the passive buzzer (signal to GPIO 12, GND). Seat it in the "
        "back-right cradle.",

        "Flash Raspberry Pi OS Lite to the microSD card. Insert it into the Pi.",

        "Connect a 5V 3A micro-USB power supply to the Pi's power port (the one "
        "further from the HDMI port). Verify the Pi boots.",

        "Place the lid on the body. Align the nesting lip and screw posts. "
        "Secure with 4x M3 screws at the corners.",

        "Attach RFID stickers to figurine bases (centered in the bottom recess). "
        "Glue or attach decorative tops to the bases.",

        "Test: place a figurine on the lid. The RFID tag should be read, the "
        "LEDs should animate, and media should play. Connect a Bluetooth speaker "
        "and verify audio routing.",
    ])


def sec_safety(pdf: AssemblyGuide):
    pdf.section_title("Safety Notes")

    pdf.note_box(
        "This device is intended for toddlers (ages 1-4). Safety is paramount. "
        "Review all points below before allowing a child to use the BabyBox.",
        kind="WARNING",
    )

    pdf.subsection("Magnet Safety")
    pdf.bullet_list([
        "ALL magnets MUST be fully enclosed inside 3D-printed plastic using the "
        "pause-and-insert technique. No magnets should be accessible.",
        "After printing, verify the seal: the top surface should be smooth and "
        "continuous with no visible cavities or holes.",
        "If a print fails mid-seal (power outage, filament runout), DISCARD the "
        "part. Do not use it with exposed magnets.",
        "Neodymium magnets are extremely dangerous if swallowed. Two magnets "
        "swallowed separately can attract through intestinal walls, causing "
        "perforation, obstruction, or death.",
        "Keep loose magnets locked away during assembly.",
    ])

    pdf.subsection("Electrical Safety")
    pdf.bullet_list([
        "Use only a regulated 5V power supply. Never exceed 5V.",
        "The MFRC522 operates at 3.3V. Never connect it to 5V.",
        "Keep all wiring inside the enclosed box. No exposed connections.",
        "The enclosure should be fully closed (lid screwed on) during use.",
        "Do not use the device near water or liquids.",
        "Unplug the power supply when not in use or when opening the enclosure.",
    ])

    pdf.subsection("Volume and Hearing")
    pdf.bullet_list([
        "All audio goes to an external Bluetooth speaker.",
        "Set the speaker volume to a safe level BEFORE giving it to the child.",
        "The American Academy of Pediatrics recommends keeping volume below "
        "75 dB for extended listening.",
        "Place the speaker at least 1 meter from the child when possible.",
    ])

    pdf.subsection("Screen Time")
    pdf.bullet_list([
        "The BabyBox has a built-in daily video limit system.",
        "Set appropriate limits in the web UI (Settings page).",
        "Audio content is unlimited; only video counts against the daily limit.",
        "The box provides LED + buzzer feedback when the video limit is reached.",
        "Supervise screen time for children under 2 (AAP recommendation).",
    ])

    pdf.subsection("Physical Safety")
    pdf.bullet_list([
        "All enclosure corners are rounded (5 mm radius).",
        "Walls are 3 mm thick PETG -- sturdy enough for toddler handling.",
        "Figurines should be inspected regularly for cracks. If a crack exposes "
        "a magnet, remove the figurine immediately.",
        "The device is not a toy -- supervise initial use sessions.",
        "Keep small parts (screws, wire scraps) away from children during assembly.",
    ])


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    pdf = AssemblyGuide()
    pdf.set_title("BabyBox Assembly Guide")
    pdf.set_author("BabyBox Project")

    cover_page(pdf)

    pdf.add_page()
    pdf.insert_toc_placeholder(render_toc, pages=1)

    sec_bom(pdf)
    sec_gpio(pdf)
    sec_3d_printing(pdf)
    sec_magnets(pdf)
    sec_electronics(pdf)
    sec_wiring(pdf)
    sec_figurines(pdf)
    sec_final_assembly(pdf)
    sec_safety(pdf)

    out_dir = Path(__file__).parent
    out_path = out_dir / "BabyBox-Assembly-Guide.pdf"
    pdf.output(str(out_path))
    print(f"Generated: {out_path}")
    print(f"Pages: {pdf.pages_count}")


if __name__ == "__main__":
    main()
