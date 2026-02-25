// babybox-case.scad — Parametric enclosure for BabyBox toddler media player
// Two-piece design: body (bottom, open top) + lid (top surface for figurine).
//
// HIDDEN MAGNETS (lid): Magnets are fully enclosed inside the lid top wall.
//   1. Print lid UPSIDE-DOWN (top surface on bed for nice finish)
//   2. Pause at Z = magnet_seal_h + magnet_pocket_h (see echo output)
//   3. Drop 2x neodymium magnets into the open cavities
//   4. Resume print — ceiling layers seal the magnets inside
//
// Usage: Open in OpenSCAD, set render_part below, then F5 (preview) or F6 (render).

use <../common-params.scad>
include <../common-params.scad>

// === Render Selector ===
// "body"      — bottom enclosure (for printing upside-down)
// "lid"       — top lid with magnet bosses + RFID mount (print top-down)
// "assembly"  — body + lid together (for visual check)
// "exploded"  — body + lid separated vertically
render_part = "assembly";  // change this to switch views

// === Enclosure Dimensions ===
box_l        = 150;    // outer length (X)
box_w        = 110;    // outer width  (Y)
box_h        = 75;     // total outer height (body + lid)
wall         = 3;      // wall thickness
corner_r     = 5;      // corner rounding radius (toddler-safe)

// Body/lid split
lid_h        = 12;     // lid outer height
body_h       = box_h - lid_h;  // body outer height

// Lid nesting lip
lip_h        = 3;      // inner lip depth
lip_clearance = 0.4;   // clearance between lip and body inner wall

// Floor thickness
floor_h      = 3;

$fn = 40;

// Print the pause height to the console
echo(str(">>> LID: Print UPSIDE-DOWN. Pause at Z = ", lid_magnet_pause_z,
         " mm to insert magnets"));
echo(str("    Seal below magnets (on bed): ", magnet_seal_h, " mm"));
echo(str("    Magnet cavity: ", magnet_pocket_h, " mm"));
echo(str("    Seal above magnets: ", wall - magnet_seal_h, " mm (top wall remainder) + boss floor"));

// === Component Placement ===
// All positions are relative to the inner floor origin (0,0) at front-left corner.
// Inner dimensions:
inner_l = box_l - 2*wall;  // 144
inner_w = box_w - 2*wall;  // 104

// --- Pi Zero 2 W ---
pi_l = 65;
pi_w = 30;
pi_h = 5.2;
pi_hole_x_spacing = 58;   // mounting hole X spacing
pi_hole_y_spacing = 23;   // mounting hole Y spacing
pi_hole_inset = 3.5;      // hole inset from board edge
pi_standoff_h = 5;        // standoff height above floor
pi_standoff_od = 5;       // standoff outer diameter

// Pi placement: near back wall, left side
pi_x = 10;                // left edge of Pi board (from inner left wall)
pi_y = inner_w - pi_w - 5; // 5mm from back inner wall

// Pi port positions (from left edge of board, along the back long edge)
// Ports face the back wall
pi_sd_offset = 0;         // micro SD on left short edge
pi_hdmi_offset = 12.4;    // mini HDMI center from left edge
pi_usb_otg_offset = 41.4; // micro USB OTG center
pi_usb_pwr_offset = 54.0; // micro USB power center

// Port cutout sizes
hdmi_cut_w = 12;
hdmi_cut_h = 4;
usb_cut_w  = 9;
usb_cut_h  = 4;
sd_cut_w   = 12;
sd_cut_h   = 3;

// --- Half Breadboard ---
bb_l = 82;
bb_w = 55;
bb_h = 10;
bb_tol = 0.5;  // tolerance per side
bb_recess_l = bb_l + 2*bb_tol;
bb_recess_w = bb_w + 2*bb_tol;
bb_recess_h = bb_h;

// Breadboard placement: centered horizontally, middle of box
bb_x = (inner_l - bb_recess_l) / 2;
bb_y = (inner_w - bb_recess_w) / 2 - 8;  // slightly toward front

// --- Buzzer ---
buzzer_dia = 12;
buzzer_h   = 8.5;
buzzer_mount_od = 15;
buzzer_mount_h  = 3;

// Buzzer placement: back-right corner
buzzer_x = inner_l - 20;
buzzer_y = inner_w - 20;

// --- Buttons (6x6x5mm tactile, 12mm cap hole) ---
btn_hole_dia = 12;
btn_spacing  = 60;  // distance between button centers

// Button placement: on front wall, symmetric about center
btn_y_center = wall / 2;  // through front wall
btn1_x = box_l/2 - btn_spacing/2;  // left button (play/pause)
btn2_x = box_l/2 + btn_spacing/2;  // right button (stop)
btn_z  = body_h / 2;               // vertically centered on body front

// --- LED Strip (WS2812 8-LED) ---
led_strip_l = 51.1;
led_strip_w = 10.2;
led_strip_h = 3.2;

// LED window on front wall, centered between buttons
led_window_l = 55;   // slightly wider than strip
led_window_h = 12;   // window height
led_window_z = btn_z - led_window_h/2;  // aligned with buttons vertically
led_channel_depth = 5; // depth of channel behind window

// --- Screw Posts (M3, 4 corners) ---
post_od   = 8;
post_id   = m3_tap_dia;
post_h    = 15;
post_inset = 8;  // inset from outer wall corner

// === RFID + Magnets on Lid ===
// Centered on lid top surface
figurine_marker_dia = 36;  // engraved circle on top
figurine_marker_depth = 0.6;

// RFID module standoffs hang from lid ceiling
rfid_standoff_h = 4;     // hang distance below ceiling
rfid_standoff_od = 5;

// Magnet bosses hang from lid ceiling (enclose magnets fully)
magnet_boss_od = magnet_pocket_dia + 2*wall_min;
// Boss must house the portion of the pocket that extends below the lid top wall,
// plus a solid floor (magnet_seal_h) below the pocket.
// Cavity spans: lid_h - magnet_seal_h - magnet_pocket_h  to  lid_h - magnet_seal_h
// Lid ceiling (bottom of top wall) is at: lid_h - wall
// Boss hangs from ceiling down to cavity bottom - magnet_seal_h
magnet_boss_h  = (magnet_seal_h + magnet_pocket_h) - wall + magnet_seal_h;
                 // = how far below ceiling the boss extends

// Figurine marker — ring outline (not filled) to avoid thinning seal over magnets
figurine_marker_line = 1.2;  // ring line width (3 nozzle widths)

// Lid magnet pause height (when printing upside-down)
lid_magnet_pause_z = magnet_seal_h + magnet_pocket_h;

// ──────────────────────────────────────────────────
// Utility Modules
// ──────────────────────────────────────────────────

module rounded_box(size, r) {
    // Solid rounded-corner box using hull of 4 cylinders
    hull() {
        for (x = [r, size.x - r])
            for (y = [r, size.y - r])
                translate([x, y, 0])
                    cylinder(r = r, h = size.z);
    }
}

module rounded_shell(size, r, w) {
    // Hollow rounded box (open top)
    difference() {
        rounded_box(size, r);
        translate([w, w, w])
            rounded_box([size.x - 2*w, size.y - 2*w, size.z], r - w);
    }
}

// ──────────────────────────────────────────────────
// Body Modules
// ──────────────────────────────────────────────────

module body_shell() {
    // Main hollow box, open top, with floor
    difference() {
        rounded_box([box_l, box_w, body_h], corner_r);
        // Hollow out interior (leave floor)
        translate([wall, wall, floor_h])
            rounded_box([inner_l, inner_w, body_h], corner_r - wall);
    }
}

module breadboard_bay() {
    // Recess in the floor for the breadboard to sit in
    translate([wall + bb_x, wall + bb_y, floor_h - bb_recess_h])
        cube([bb_recess_l, bb_recess_w, bb_recess_h + 0.01]);
}

module pi_standoffs() {
    // 4 standoffs for Pi Zero 2 W mounting holes
    hole_positions = [
        [pi_hole_inset, pi_hole_inset],
        [pi_hole_inset + pi_hole_x_spacing, pi_hole_inset],
        [pi_hole_inset, pi_hole_inset + pi_hole_y_spacing],
        [pi_hole_inset + pi_hole_x_spacing, pi_hole_inset + pi_hole_y_spacing]
    ];
    for (pos = hole_positions) {
        translate([wall + pi_x + pos[0], wall + pi_y + pos[1], floor_h]) {
            difference() {
                cylinder(d = pi_standoff_od, h = pi_standoff_h);
                translate([0, 0, -0.01])
                    cylinder(d = m25_tap_dia, h = pi_standoff_h + 0.02);
            }
        }
    }
}

module pi_port_cutouts() {
    // Back wall cutouts: mini HDMI, 2x micro USB
    // Pi back edge is at wall + pi_y + pi_w, which should align near back wall
    back_wall_y = box_w - wall/2;
    port_z = floor_h + pi_standoff_h;  // port height = floor + standoff

    // Mini HDMI
    translate([wall + pi_x + pi_hdmi_offset - hdmi_cut_w/2,
               back_wall_y - wall,
               port_z]) {
        cube([hdmi_cut_w, wall + 2, hdmi_cut_h]);
    }

    // Micro USB OTG
    translate([wall + pi_x + pi_usb_otg_offset - usb_cut_w/2,
               back_wall_y - wall,
               port_z]) {
        cube([usb_cut_w, wall + 2, usb_cut_h]);
    }

    // Micro USB Power
    translate([wall + pi_x + pi_usb_pwr_offset - usb_cut_w/2,
               back_wall_y - wall,
               port_z]) {
        cube([usb_cut_w, wall + 2, usb_cut_h]);
    }

    // Micro SD on left short edge of Pi
    // SD card slot is on the left short edge, facing the left wall
    translate([wall + pi_x - wall - 1,
               wall + pi_y + pi_w/2 - sd_cut_w/2,
               port_z]) {
        cube([wall + 2, sd_cut_w, sd_cut_h]);
    }
}

module button_holes() {
    // Two button holes on the front wall
    for (bx = [btn1_x, btn2_x]) {
        translate([bx, -1, btn_z])
            rotate([-90, 0, 0])
                cylinder(d = btn_hole_dia, h = wall + 2);
    }
}

module led_window() {
    // Rectangular slot on front wall for LED strip visibility
    translate([box_l/2 - led_window_l/2, -1, led_window_z])
        cube([led_window_l, wall + 2, led_window_h]);
}

module led_strip_mount() {
    // Channel behind the LED window to hold the strip
    // Slightly wider than the strip for insertion
    channel_w = led_strip_w + 1;
    channel_h = led_strip_h + 1;
    translate([box_l/2 - led_window_l/2, wall - 0.01, led_window_z + (led_window_h - channel_h)/2])
        cube([led_window_l, led_channel_depth, channel_h]);
}

module buzzer_mount() {
    // Ring cradle on the floor for the passive buzzer
    translate([wall + buzzer_x, wall + buzzer_y, floor_h]) {
        difference() {
            cylinder(d = buzzer_mount_od, h = buzzer_mount_h);
            translate([0, 0, -0.01])
                cylinder(d = buzzer_dia + 0.4, h = buzzer_mount_h + 0.02);
        }
    }
}

module screw_posts_body() {
    // 4 screw posts at corners for lid attachment
    positions = [
        [post_inset, post_inset],
        [box_l - post_inset, post_inset],
        [post_inset, box_w - post_inset],
        [box_l - post_inset, box_w - post_inset]
    ];
    for (pos = positions) {
        translate([pos[0], pos[1], floor_h]) {
            difference() {
                cylinder(d = post_od, h = post_h);
                translate([0, 0, -0.01])
                    cylinder(d = post_id, h = post_h + 0.02);
            }
        }
    }
}

module body() {
    difference() {
        union() {
            body_shell();
            pi_standoffs();
            buzzer_mount();
            screw_posts_body();
        }
        breadboard_bay();
        pi_port_cutouts();
        button_holes();
        led_window();
        led_strip_mount();
    }
}

// ──────────────────────────────────────────────────
// Lid Modules
// ──────────────────────────────────────────────────

module lid_shell() {
    // Shallow box forming the lid (print upside-down)
    rounded_box([box_l, box_w, lid_h], corner_r);
}

module lid_hollow() {
    // Hollow out the inside of the lid, leaving top wall intact
    lid_top_wall = wall;  // 3mm top wall
    translate([wall, wall, -0.01])
        rounded_box([inner_l, inner_w, lid_h - lid_top_wall + 0.01], corner_r - wall);
}

module lid_lip() {
    // Inner rim that nests inside the body opening
    lip_inset = wall + lip_clearance;
    lip_l = box_l - 2*lip_inset;
    lip_w = box_w - 2*lip_inset;
    translate([lip_inset, lip_inset, -lip_h])
        difference() {
            rounded_box([lip_l, lip_w, lip_h], corner_r - lip_inset);
            translate([wall_min, wall_min, -0.01])
                rounded_box([lip_l - 2*wall_min, lip_w - 2*wall_min, lip_h + 0.02],
                            corner_r - lip_inset - wall_min);
        }
}

module rfid_standoffs() {
    // 4 M2 standoffs hanging from the lid ceiling for MFRC522 mounting
    // RFID module centered on lid
    rfid_cx = box_l / 2;
    rfid_cy = box_w / 2;

    hole_offsets = [
        [-mfrc522_hole_x/2, -mfrc522_hole_y/2],
        [ mfrc522_hole_x/2, -mfrc522_hole_y/2],
        [-mfrc522_hole_x/2,  mfrc522_hole_y/2],
        [ mfrc522_hole_x/2,  mfrc522_hole_y/2]
    ];

    for (off = hole_offsets) {
        translate([rfid_cx + off[0], rfid_cy + off[1], -rfid_standoff_h]) {
            difference() {
                cylinder(d = rfid_standoff_od, h = rfid_standoff_h + 0.01);
                translate([0, 0, -0.01])
                    cylinder(d = m2_tap_dia, h = rfid_standoff_h + 0.03);
            }
        }
    }
}

module magnet_bosses() {
    // Solid cylindrical bosses hanging from the lid ceiling.
    // These provide material around the magnet cavity below the top wall.
    // The cavity itself is cut by magnet_pockets_lid().
    mag_cx = box_l / 2;
    mag_cy = box_w / 2;
    lid_ceiling_z = lid_h - wall;  // Z of lid ceiling (bottom of top wall)

    for (mx = [-magnet_spacing/2, magnet_spacing/2]) {
        translate([mag_cx + mx, mag_cy, lid_ceiling_z - magnet_boss_h])
            cylinder(d = magnet_boss_od, h = magnet_boss_h + 0.01);
    }
}

module magnet_pockets_lid() {
    // Enclosed magnet cavities inside the lid top wall + bosses.
    // Sealed by magnet_seal_h of solid material on the top surface, and
    // magnet_seal_h of solid boss floor below.
    // Cavity: Z = lid_h - magnet_seal_h - magnet_pocket_h  to  Z = lid_h - magnet_seal_h
    mag_cx = box_l / 2;
    mag_cy = box_w / 2;
    cavity_bottom = lid_h - magnet_seal_h - magnet_pocket_h;

    for (mx = [-magnet_spacing/2, magnet_spacing/2]) {
        translate([mag_cx + mx, mag_cy, cavity_bottom])
            cylinder(d = magnet_pocket_dia, h = magnet_pocket_h);
    }
}

module figurine_marker() {
    // Engraved ring on the top surface showing where to place figurines.
    // Ring outline only (not filled) — avoids thinning the magnet seal area.
    translate([box_l/2, box_w/2, lid_h - figurine_marker_depth]) {
        difference() {
            cylinder(d = figurine_marker_dia, h = figurine_marker_depth + 0.01);
            translate([0, 0, -0.01])
                cylinder(d = figurine_marker_dia - 2*figurine_marker_line,
                         h = figurine_marker_depth + 0.03);
        }
    }
}

module screw_holes_lid() {
    // M3 clearance holes matching body screw posts
    positions = [
        [post_inset, post_inset],
        [box_l - post_inset, post_inset],
        [post_inset, box_w - post_inset],
        [box_l - post_inset, box_w - post_inset]
    ];
    for (pos = positions) {
        translate([pos[0], pos[1], -lip_h - 1])
            cylinder(d = m3_hole_dia, h = lid_h + lip_h + 2);
    }
}

module lid() {
    difference() {
        union() {
            lid_shell();
            lid_lip();
            rfid_standoffs();
            magnet_bosses();
        }
        lid_hollow();
        magnet_pockets_lid();
        figurine_marker();
        screw_holes_lid();
    }
}

// ──────────────────────────────────────────────────
// Assembly
// ──────────────────────────────────────────────────

module assembly() {
    body();
    translate([0, 0, body_h])
        lid();
}

module exploded() {
    explode_gap = 30;
    body();
    translate([0, 0, body_h + explode_gap])
        lid();
}

// ──────────────────────────────────────────────────
// Render
// ──────────────────────────────────────────────────

if (render_part == "body") {
    body();
} else if (render_part == "lid") {
    lid();
} else if (render_part == "assembly") {
    assembly();
} else if (render_part == "exploded") {
    exploded();
}
