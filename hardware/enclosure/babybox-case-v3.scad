// babybox-case-v3.scad — "Tower" enclosure, rev C (recessed figurine well)
//
// Redrawn from the paper sketches in hardware/sketches/ and refined from
// feedback. The top is a RAISED, SEALED LED ring with a RECESSED HOLE in the
// middle: the figurine drops straight down into the hole and sits nested,
// ringed by the glow. The MFRC522 sits flush right under the thin hole floor
// (a few mm from the tag) so it reads reliably. No raised lid, no exposed
// LED strip, and the body is only as tall as the electronics need.
//
//   ┌─ figurine drops into the hole, sits recessed ─────────┐
//   │   ● RAISED LED RING (sealed): flexible WS2812B strip   │
//   │     wrapped around the hole wall, fully covered by a   │
//   │     glued translucent diffuser cap — nothing to pick   │
//   │   ● RECESSED HOLE: figurine well, magnets in the floor │
//   │   ● MFRC522 mounts FLUSH under the hole floor (~5 mm)  │
//   │   ● 2x MX buttons with big round keycaps, in front     │
//   │   ● short BODY tube; Pi Zero 2 W + buzzer on the TRAY  │
//   └────────────────────────────────────────────────────────┘
//
// SOLDERED build, no breadboard. HEAT-SET inserts everywhere. Four corner
// columns run the body height with an insert at each end (tray bolts up,
// top plate bolts down).
//
// PRINTING (all parts, no supports):
//   * TRAY      — flat on the bed
//   * BODY      — one open end on the bed
//   * TOP PLATE — print RIGHT-SIDE UP (underside on the bed): the raised ring
//                 prints up, the figurine hole is a clean recess, the RFID
//                 insert holes drill up from the underside. PAUSE at the
//                 echoed Z to drop the 2 ring magnets, then resume.
//   * DIFFUSER  — translucent/natural; glued over the strip to seal the ring
//   * KEYCAPS   — see keycaps.scad
//
// Render: set render_part, F5 to preview, F6 + export STL.

include <../common-params.scad>
use <keycaps.scad>      // big round keycaps (modules only, for the assembly view)

// === Render Selector ===
// "body" | "tray" | "top" | "diffuser" | "assembly" | "exploded"
render_part = "assembly";

// Underside logo on the tray — disable (-D show_logo=false) for lighter
// web/preview STL exports; the text is heavy and faces the table anyway.
show_logo = true;
// Show a stand-in figurine seated in the hole (assembly/exploded views only).
show_figurine = true;

$fn = 64;

// ──────────────────────────────────────────────────
// Master dimensions
// ──────────────────────────────────────────────────
box_l    = 90;     // outer footprint X
box_w    = 90;     // outer footprint Y  (square; deep enough that the RFID
                   //   board clears the rear corner columns)
wall     = 3;      // side wall thickness
corner_r = 16;     // XY corner radius (toddler-safe, toy look)

body_h       = 32;   // main tube height — only as tall as the Pi + wiring need
tray_h       = 5;    // bottom tray plate thickness
tray_lip_h   = 4;    // tray centering spigot up into the body
top_plate_h  = 10;   // top plate slab thickness
top_lip_h    = 5;    // top plate centering spigot down into the body
clr          = 0.4;  // nesting clearance

inner_l = box_l - 2*wall;   // 78
inner_w = box_w - 2*wall;   // 78
cx = box_l/2;  cy = box_w/2;

// === Corner columns (full-height, heat-set insert at each end) ===
col_od    = 9;
col_inset = 13;
col_pos = [
    [col_inset,          col_inset],
    [box_l - col_inset,  col_inset],
    [col_inset,          box_w - col_inset],
    [box_l - col_inset,  box_w - col_inset],
];

// === Back power hole ===
// The SMALLEST sensible opening: a little rounded RECTANGLE lined up EXACTLY
// with the Pi's micro-USB *power* port. No HDMI/USB-data is exposed — the box
// is otherwise fully closed (baby-safe). The Pi sits at the back with its
// connector edge facing this wall; the power port is the rightmost of the
// three connectors (~54 mm along the board from the SD-card end).
pi_pwr_off = 54.0;             // power-port center, from the board's left edge
pwr_hole_w = 11;              // width  (clears a micro-USB plug)
pwr_hole_h = 6;               // height (too shallow to admit a finger)
pwr_hole_r = 1.5;             // rounded corners — no sharp edges
// position is derived from the Pi below (pwr_hole_cx, pwr_hole_z)

// === Pi Zero 2 W on the tray ===
pi_l = 65;  pi_w = 30;
pi_hole_x_spacing = 58;
pi_hole_y_spacing = 23;
pi_hole_inset     = 3.5;
pi_standoff_h     = 4;
pi_standoff_od    = 6;
pi_x = (box_l - pi_l)/2;
pi_y = box_w - wall - pi_w - 4;   // connector edge (+Y) faces the back wall

// power hole lines up with the Pi's micro-USB power port (derived)
pwr_hole_cx = pi_x + pi_pwr_off;              // X of the power port
pwr_hole_z  = pi_standoff_h + 3;              // ~ micro-USB center above the tray

// === Buzzer cradle (on the tray) ===
buzzer_dia      = 12;
buzzer_mount_od = 15;
buzzer_mount_h  = 4;
buzzer_x = 16;  buzzer_y = 16;

// === RAISED LED ring + RECESSED figurine hole ===========================
hub_cx     = cx;
hub_cy     = cy + 5;             // ring/hole sits toward the back
well_dia   = 38;                 // the hole the figurine drops into
well_depth = 5;                  // recess into the plate (figurine nests here)
well_floor = top_plate_h - well_depth;   // 5 mm of floor under the figurine
well_wall  = 2;                  // wall between the hole and the strip
ring_h     = led_strip_w + 1;    // how far the sealed ring stands proud (11)

// strip wraps the OUTSIDE of the hole wall; LEDs face out into the diffuser
strip_wrap_r = well_dia/2 + well_wall;          // 21 -> wrap dia 42 (= strip len/pi)
strip_out_r  = strip_wrap_r + led_strip_t;      // 23
diff_ir      = strip_out_r + 0.3;               // 23.3 (clears the strip)
diff_wall    = 1.8;
diff_or      = diff_ir + diff_wall;             // 25.1 (glowing outer face)
diff_flange  = 1.2;                             // top cap thickness over the strip
strip_notch_w = led_lead_w;                     // wire pass-through at the ring base

// magnets in the hole floor (snap + align the figurine). Printed right-side
// up, the pockets seal when the print reaches this Z — pause and drop them in.
ring_magnet_pause_z = magnet_seal_h + magnet_pocket_h;   // = 4.2 mm

// === RFID flush under the hole floor (antenna up, ~5 mm to the tag) ===
rfid_pocket_clr = 1.0;          // around the board, so it locates flush

// === MX-switch buttons ===
btn_spacing = 34;
btn_y       = 15;
btn1_x = cx - btn_spacing/2;
btn2_x = cx + btn_spacing/2;

// === Bottom-of-tray details ===
bumper_dia   = 11;  bumper_depth = 0.5;
bumper_pos   = [[16,16],[box_l-16,16],[16,box_w-16],[box_l-16,box_w-16]];
vent_w = 3;  vent_l = 16;
vent_x = [33,45,57,69];  vent_y = 60;   // under the Pi (which sits at the back)

// ──────────────────────────────────────────────────
// Sanity
// ──────────────────────────────────────────────────
echo(str(">>> BabyBox v3 rev C: ", box_l, " x ", box_w,
         " x ", tray_h + body_h + top_plate_h, " mm body (ring +",
         ring_h, " mm, figurine on top)"));
echo(str(">>> LED strip wraps dia ", 2*strip_wrap_r,
         " mm (strip length ~", led_pitch*led_count, " mm)."));
echo(str(">>> TOP PLATE: print right-side up, PAUSE at Z = ",
         ring_magnet_pause_z, " mm, drop 2x 6x3 magnets, resume."));

assert(pi_x + pi_l <= box_l - wall, "Pi too long for footprint");
assert(pi_y >= wall && pi_y + pi_w <= box_w - wall, "Pi doesn't fit in Y");
assert(well_floor >= magnet_seal_h + magnet_pocket_h, "hole floor too thin for magnets");
assert(mfrc522_l <= inner_l && mfrc522_w <= inner_w, "MFRC522 won't fit inside");
// big round keycaps clear the raised ring and each other
assert(sqrt(pow(btn2_x - hub_cx, 2) + pow(btn_y - hub_cy, 2))
       - mx_keycap_round_dia/2 - diff_or >= 0.5, "round caps overlap the LED ring");
assert(btn_spacing - mx_keycap_round_dia >= 4, "round caps collide");
// RFID board must clear the back wall and the corner columns
assert(hub_cy + mfrc522_w/2 <= box_w - wall - 0.5, "RFID board hits back wall");
rfid_holes = [for (sx = [-1,1], sy = [-1,1])
              [hub_cx + sx*mfrc522_hole_x/2, hub_cy + sy*mfrc522_hole_y/2]];
assert(min([for (h = rfid_holes) for (c = col_pos) norm([h.x-c.x, h.y-c.y])]) >= 5,
       "RFID mount holes collide with the corner columns");
// body must be tall enough for the Pi to clear the flush RFID under the lid
assert(body_h >= pi_standoff_h + 12 + 4, "body too short for the Pi stack");
// power hole sits over the Pi board and on the flat part of the back wall
assert(pwr_hole_cx - pwr_hole_w/2 >= pi_x && pwr_hole_cx + pwr_hole_w/2 <= pi_x + pi_l,
       "power hole not over the Pi board");
assert(pwr_hole_cx + pwr_hole_w/2 <= box_l - corner_r - 1,
       "power hole runs into the rounded corner");

// ──────────────────────────────────────────────────
// Utilities
// ──────────────────────────────────────────────────
module rounded_box(size, r) {
    hull()
        for (x = [r, size.x - r], y = [r, size.y - r])
            translate([x, y, 0]) cylinder(r = r, h = size.z);
}
module rounded_tube(size, r, w) {
    difference() {
        rounded_box(size, r);
        translate([w, w, -0.5])
            rounded_box([size.x - 2*w, size.y - 2*w, size.z + 1], r - w);
    }
}
module insert_pocket(hole_d, depth) {
    translate([0, 0, -0.01]) cylinder(d = hole_d, h = depth + 0.01);
    translate([0, 0, -0.01]) cylinder(d1 = hole_d + 1.2, d2 = hole_d, h = 1.0);
}

// ──────────────────────────────────────────────────
// BODY
// ──────────────────────────────────────────────────
module body_columns() {
    for (p = col_pos) translate([p.x, p.y, 0])
        difference() {
            cylinder(d = col_od, h = body_h);
            insert_pocket(m3_insert_hole_dia, m3_insert_h + 1.5);
            translate([0, 0, body_h]) mirror([0,0,1])
                insert_pocket(m3_insert_hole_dia, m3_insert_h + 1.5);
        }
}
module body_column_webs() {
    for (p = col_pos) {
        xw = (p.x < cx) ? wall : box_l - wall;
        yw = (p.y < cy) ? wall : box_w - wall;
        hull() {
            translate([p.x, p.y, 0]) cylinder(d = col_od - 3, h = body_h);
            translate([xw,  p.y, 0]) cylinder(d = 3,          h = body_h);
        }
        hull() {
            translate([p.x, p.y, 0]) cylinder(d = col_od - 3, h = body_h);
            translate([p.x, yw,  0]) cylinder(d = 3,          h = body_h);
        }
    }
}
module body_power_hole() {
    // little rounded rectangle through the back wall, centered on the Pi's
    // micro-USB power port
    translate([pwr_hole_cx, box_w - wall - 0.6, pwr_hole_z])
        rotate([-90, 0, 0])
            hull()
                for (sx = [-1, 1], sz = [-1, 1])
                    translate([sx*(pwr_hole_w/2 - pwr_hole_r),
                               sz*(pwr_hole_h/2 - pwr_hole_r), 0])
                        cylinder(r = pwr_hole_r, h = wall + 1.2);
}
module body() {
    difference() {
        union() {
            rounded_tube([box_l, box_w, body_h], corner_r, wall);
            body_columns();
            intersection() {
                body_column_webs();
                translate([wall, wall, -1])
                    rounded_box([inner_l, inner_w, body_h + 2], corner_r - wall);
            }
        }
        body_power_hole();
    }
}

// ──────────────────────────────────────────────────
// BOTTOM TRAY
// ──────────────────────────────────────────────────
module tray_plate() {
    rounded_box([box_l, box_w, tray_h], corner_r);
    translate([wall + clr, wall + clr, tray_h - 0.01])
        rounded_tube([inner_l - 2*clr, inner_w - 2*clr, tray_lip_h + 0.01],
                     corner_r - wall, wall_min);
}
module tray_screw_holes() {
    for (p = col_pos) translate([p.x, p.y, 0]) {
        translate([0,0,-0.01]) cylinder(d = m3_hole_dia, h = tray_h + 0.02);
        translate([0,0,-0.01]) cylinder(d = 6.5, h = 2.2);
    }
}
module pi_standoffs() {
    holes = [[0,0],[pi_hole_x_spacing,0],[0,pi_hole_y_spacing],
             [pi_hole_x_spacing,pi_hole_y_spacing]];
    for (h = holes)
        translate([pi_x + pi_hole_inset + h.x, pi_y + pi_hole_inset + h.y, tray_h])
            difference() {
                cylinder(d = pi_standoff_od, h = pi_standoff_h);
                translate([0,0,pi_standoff_h]) mirror([0,0,1])
                    insert_pocket(m25_insert_hole_dia, m25_insert_h);
            }
}
module buzzer_cradle() {
    translate([buzzer_x, buzzer_y, tray_h])
        difference() {
            cylinder(d = buzzer_mount_od, h = buzzer_mount_h);
            translate([0,0,1]) cylinder(d = buzzer_dia + 0.4, h = buzzer_mount_h);
        }
}
module tray_vents() {
    for (vx = vent_x)
        translate([vx - vent_w/2, vent_y, -0.01])
            rounded_box([vent_w, vent_l, tray_h + 0.02], vent_w/2 - 0.01);
}
module tray_bumpers() {
    for (p = bumper_pos)
        translate([p.x, p.y, -0.01]) cylinder(d = bumper_dia, h = bumper_depth);
}
module tray_logo() {
    translate([cx, cy, bumper_depth + 0.01])
        rotate([180,0,0])
            linear_extrude(0.6 + bumper_depth)
                text("BabyBox", size = 8, font = "Liberation Sans:style=Bold",
                     halign = "center", valign = "center");
}
module tray() {
    difference() {
        union() { tray_plate(); pi_standoffs(); buzzer_cradle(); }
        tray_screw_holes();
        tray_vents();
        tray_bumpers();
        if (show_logo) tray_logo();
    }
}

// ──────────────────────────────────────────────────
// TOP PLATE (raised sealed ring + recessed hole + flush RFID + MX buttons)
// ──────────────────────────────────────────────────
module top_slab() {
    rounded_box([box_l, box_w, top_plate_h], corner_r);
    translate([wall + clr, wall + clr, -top_lip_h])
        rounded_tube([inner_l - 2*clr, inner_w - 2*clr, top_lip_h + 0.01],
                     corner_r - wall, wall_min);
}
module top_screw_holes() {
    for (p = col_pos) translate([p.x, p.y, 0]) {
        translate([0,0,-0.01]) cylinder(d = m3_hole_dia, h = top_plate_h + 0.02);
        translate([0,0,top_plate_h - 1.7])
            cylinder(d1 = m3_hole_dia, d2 = 6.4, h = 1.8);
    }
}
module ring_wall() {
    // the hole wall, rising the full plate + raised-ring height
    translate([hub_cx, hub_cy, 0])
        cylinder(d = well_dia + 2*well_wall, h = top_plate_h + ring_h);
}
module figurine_hole() {
    // recess from the top, down to the thin floor (figurine sits in here)
    translate([hub_cx, hub_cy, well_floor])
        cylinder(d = well_dia, h = top_plate_h + ring_h);
}
module ring_magnet_pockets() {
    // sealed pockets in the floor, magnets dropped in on a print pause
    for (mx = [-magnet_spacing/2, magnet_spacing/2])
        translate([hub_cx + mx, hub_cy, magnet_seal_h])
            cylinder(d = magnet_pocket_dia, h = magnet_pocket_h);
}
module strip_wire_notch() {
    translate([hub_cx - strip_notch_w/2, hub_cy + strip_wrap_r - 1, -0.1])
        cube([strip_notch_w, 5, top_plate_h + ring_h]);
}
module mx_cutout() {
    translate([0, 0, top_plate_h - mx_plate_t])
        translate([-mx_switch_cut/2, -mx_switch_cut/2, 0])
            cube([mx_switch_cut, mx_switch_cut, mx_plate_t + 0.1]);
    translate([-mx_switch_body/2, -mx_switch_body/2, -0.1])
        cube([mx_switch_body, mx_switch_body, top_plate_h - mx_plate_t + 0.2]);
}
module mx_buttons_cut() {
    for (bx = [btn1_x, btn2_x]) translate([bx, btn_y, 0]) mx_cutout();
}
module rfid_mount() {
    // 4 M2 insert holes drilled up from the underside; board mounts flush,
    // antenna up under the hole floor. A shallow board recess locates it.
    for (off = [[-mfrc522_hole_x/2, -mfrc522_hole_y/2],
                [ mfrc522_hole_x/2, -mfrc522_hole_y/2],
                [-mfrc522_hole_x/2,  mfrc522_hole_y/2],
                [ mfrc522_hole_x/2,  mfrc522_hole_y/2]])
        translate([hub_cx + off.x, hub_cy + off.y, 0])
            insert_pocket(m2_insert_hole_dia, m2_insert_h);
}
module top_plate() {
    difference() {
        union() { top_slab(); ring_wall(); }
        figurine_hole();
        ring_magnet_pockets();
        strip_wire_notch();
        mx_buttons_cut();
        rfid_mount();
        top_screw_holes();
    }
}

// ──────────────────────────────────────────────────
// DIFFUSER  (translucent; glued over the strip — seals the ring)
// Tube + inward top flange so the strip is fully covered: nothing to pick.
// ──────────────────────────────────────────────────
module diffuser_ring() {
    difference() {
        cylinder(d = 2*diff_or, h = ring_h);
        // cavity around the strip (leaves the top flange)
        translate([0,0,-0.01]) cylinder(d = 2*diff_ir, h = ring_h - diff_flange + 0.01);
        // hole through the flange for the hole wall to pass
        translate([0,0,ring_h - diff_flange])
            cylinder(d = 2*strip_wrap_r + 0.6, h = diff_flange + 0.02);
    }
}

// ──────────────────────────────────────────────────
// Stand-in figurine (render only — yours come from figurines/)
// ──────────────────────────────────────────────────
module demo_figurine() {
    fig_base_d = well_dia - 1;
    union() {
        cylinder(d = fig_base_d, h = 6);                       // base, sits on floor
        translate([0,0,6]) cylinder(d1 = fig_base_d*0.8, d2 = 14, h = 26); // body
        translate([0,0,32]) sphere(d = 18);                    // head
    }
}

// ──────────────────────────────────────────────────
// Assembly / render
// ──────────────────────────────────────────────────
module assembly(gap = 0) {
    color("#f6f1e7") translate([0, 0, 0]) tray();
    color("#e9e2d0") translate([0, 0, tray_h + gap]) body();
    color("#7fd8c4") translate([0, 0, tray_h + body_h + 2*gap]) top_plate();
    color([0.9,1,0.95,0.5]) translate([hub_cx, hub_cy, tray_h + body_h + top_plate_h + 2.6*gap])
        diffuser_ring();
    for (b = [[btn1_x, "play"], [btn2_x, "stop"]])
        color("#ef626c") translate([b[0], btn_y, tray_h + body_h + top_plate_h - 3 + 2.5*gap])
            keycap_final(b[1]);
    if (show_figurine)
        color("#ffd166") translate([hub_cx, hub_cy, tray_h + body_h + well_floor + 3.2*gap])
            demo_figurine();
}

if      (render_part == "body")     body();
else if (render_part == "tray")     tray();
else if (render_part == "top")      top_plate();
else if (render_part == "diffuser") diffuser_ring();
else if (render_part == "figurine") demo_figurine();
else if (render_part == "assembly") assembly();
else if (render_part == "exploded") assembly(gap = 26);
