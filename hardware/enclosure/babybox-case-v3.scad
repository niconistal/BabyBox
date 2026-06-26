// babybox-case-v3.scad — "Tower" revision of the BabyBox enclosure
//
// A complete redraw from the paper sketches (hardware/sketches/*.jpeg).
// Where v2 was a flat "pebble face" (LED mouth + button eyes on the front),
// v3 is an upright TOWER with a layered top, exactly as sketched:
//
//   ┌─ figurine sits on top, snaps to magnets ──────────────┐
//   │   ● TOP: glowing LED "halo" ring around a central     │
//   │     figurine podium; 2x MX-switch buttons in front    │
//   │   ● CENTER LID: a disc with embedded magnets; the     │
//   │     MFRC522 RFID reader hides directly beneath it     │
//   │   ● BODY: an open-ended rounded tube (the tower)      │
//   │   ● BOTTOM TRAY: the Pi Zero 2 W + buzzer bolt here   │
//   └────────────────────────────────────────────────────────┘
//
// SOLDERED BUILD — no breadboard. Everything is hand-wired to the Pi header.
// HEAT-SET INSERTS everywhere (brass, melted in) instead of self-tapping, so
// the box opens and closes many times without stripping. Four corner COLUMNS
// run the full height of the body with an insert at each end: the tray bolts
// up into the bottom, the top plate bolts down into the top.
//
// CUSTOM KEYCAPS + the translucent diffuser ring live in keycaps.scad.
//
// THE LED RING — the part driven by "fit the strip I have":
//   SunFounder 8x WS2812B, 60/m flexible strip (16.67 mm pitch, 10 mm wide,
//   2 mm thick). Curled into a circle its lit length wraps to ~42 mm dia, so
//   it shrink-wraps neatly around a 40 mm central hub. The translucent
//   diffuser ring slips over it and glows as a halo around the figurine.
//
// PRINTING (all parts: no supports):
//   * TRAY      — flat on bed
//   * BODY      — one open end on the bed (tube)
//   * TOP PLATE — top face DOWN on the bed (hub/ring print up cleanly as a
//                 cavity; flip after printing). PAUSE is NOT needed here.
//   * CENTER LID — print right-side up, PAUSE at the echoed Z, drop 2 magnets,
//                 resume (magnets sealed inside, just like the figurines).
//   * DIFFUSER / KEYCAPS — see keycaps.scad
//
// Render: set render_part, F5 to preview, F6 + export STL.

include <../common-params.scad>
use <keycaps.scad>      // big round keycaps (modules only, for the assembly view)

// === Render Selector ===
// "body" | "tray" | "top" | "lid" | "diffuser" | "assembly" | "exploded"
render_part = "assembly";

// Underside logo on the tray — disable (-D show_logo=false) for lighter
// web/preview STL exports; the text is heavy and faces the table anyway.
show_logo = true;

$fn = 64;

// ──────────────────────────────────────────────────
// Master dimensions
// ──────────────────────────────────────────────────
box_l    = 84;     // outer footprint X
box_w    = 84;     // outer footprint Y  (square-ish tower top)
wall     = 3;      // side wall thickness
corner_r = 16;     // XY corner radius (toddler-safe, toy look)

body_h       = 78;   // height of the main tube (the tower)
tray_h       = 5;    // bottom tray plate thickness
tray_lip_h   = 4;    // tray centering spigot that plugs up into the body
top_plate_h  = 12;   // top plate slab thickness
top_lip_h    = 5;    // top plate centering spigot that plugs down into the body
clr          = 0.4;  // nesting clearance between parts

inner_l = box_l - 2*wall;   // 78
inner_w = box_w - 2*wall;   // 78
cx = box_l/2;  cy = box_w/2;

// === Corner columns (full-height, heat-set insert at each end) ===
col_od    = 9;
col_inset = 13;                 // column centers, in from each outer corner
col_pos = [
    [col_inset,          col_inset],
    [box_l - col_inset,  col_inset],
    [col_inset,          box_w - col_inset],
    [box_l - col_inset,  box_w - col_inset],
];

// === Back power / service slot (exposes the Pi connector edge) ===
pwr_slot_w = 50;
pwr_slot_h = 12;
pwr_slot_z = 4;                 // bottom of slot, body-local Z (clears tray seam)

// === Pi Zero 2 W on the tray ===
pi_l = 65;  pi_w = 30;
pi_hole_x_spacing = 58;
pi_hole_y_spacing = 23;
pi_hole_inset     = 3.5;
pi_standoff_h     = 4;
pi_standoff_od    = 6;
pi_x = (box_l - pi_l)/2;            // 9.5  (centered in X)
pi_y = box_w - wall - pi_w - 4;     // connector edge ~4 mm off the back wall

// === Buzzer cradle (on the tray, front-left of the Pi) ===
buzzer_dia      = 12;
buzzer_mount_od = 15;
buzzer_mount_h  = 4;
buzzer_x = 16;  buzzer_y = 16;

// === LED halo hub + figurine well (on top of the top plate) ===
// The halo sits toward the BACK so the two buttons get a clear "control deck"
// in front of it (matches the sketch: ring up top, buttons below).
hub_cx        = cx;
hub_cy        = cy + 10;            // shift the whole figurine stack rearward
hub_od        = 40;                 // strip shrink-wraps around this
hub_h         = 12;                 // rises above the top plate
well_id       = 37;                 // central figurine podium well
well_depth    = 6;                  // recess for the center lid
rfid_seat_z   = 3;                  // plastic left above the RFID pocket
ledge_w       = 2.5;               // diffuser-ring seating ledge width
ledge_od      = hub_od + 2*led_strip_t + 2*clr + 2*ledge_w;   // diffuser seat
strip_notch_w = led_lead_w;         // wire pass-through at the hub base

// === MX-switch buttons on the top plate ===
// Spacing is set so the BIG ROUND keycaps clear each other and the halo.
btn_spacing = 34;                   // center-to-center of the two switches
btn_y       = 15;                   // toward the FRONT of the top
btn1_x = cx - btn_spacing/2;        // play / pause
btn2_x = cx + btn_spacing/2;        // stop

// === MFRC522 under the top plate (antenna up, header pins down) ===
rfid_standoff_h  = 2.5;
rfid_standoff_od = 5;
rfid_pocket_clr  = 1.5;             // clearance pocket around the board

// === Bottom-of-tray details ===
bumper_dia   = 11;  bumper_depth = 0.5;
bumper_pos   = [[16,16],[box_l-16,16],[16,box_w-16],[box_l-16,box_w-16]];
vent_w = 3;  vent_l = 16;
vent_x = [30,42,54,66];  vent_y = 30;

// ──────────────────────────────────────────────────
// Sanity echoes + asserts
// ──────────────────────────────────────────────────
echo(str(">>> BabyBox v3 'Tower': ", box_l, " x ", box_w,
         " x ~", tray_h + body_h + hub_h, " mm (figurine on top adds more)"));
echo(str(">>> LED strip curls to centerline dia ", led_ring_mid_dia,
         " mm around the ", hub_od, " mm hub."));
echo(str(">>> CENTER LID: print up, PAUSE at Z = ",
         magnet_seal_h + magnet_pocket_h, " mm, drop 2x 6x3 magnets, resume."));

assert(pi_x + pi_l <= box_l - wall, "Pi too long for tower footprint");
assert(pi_y >= wall, "Pi overruns the front wall");
assert(pi_y + pi_w <= box_w - wall, "Pi overruns the back wall");
assert(hub_od + 2*led_strip_t + 4 <= inner_l, "LED hub too big for the top");
assert(well_id < hub_od - 2, "figurine well leaves no hub wall");
assert(mfrc522_l <= inner_l && mfrc522_w <= inner_w, "MFRC522 won't fit inside");
// the big round keycaps must clear the diffuser halo ledge AND each other
assert(sqrt(pow(btn2_x - hub_cx, 2) + pow(btn_y - hub_cy, 2))
       - mx_keycap_round_dia/2 - ledge_od/2 >= 0.5, "round caps overlap the LED halo");
assert(btn_spacing - mx_keycap_round_dia >= 4, "round caps collide with each other");
// RFID pocket must not breach the back wall
assert(hub_cy + (mfrc522_w + 2*rfid_pocket_clr)/2 <= box_w - wall, "RFID pocket hits back wall");

// ──────────────────────────────────────────────────
// Utilities
// ──────────────────────────────────────────────────
module rounded_box(size, r) {
    hull()
        for (x = [r, size.x - r], y = [r, size.y - r])
            translate([x, y, 0]) cylinder(r = r, h = size.z);
}

// A tube (rounded rectangular wall, open top and bottom)
module rounded_tube(size, r, w) {
    difference() {
        rounded_box(size, r);
        translate([w, w, -0.5])
            rounded_box([size.x - 2*w, size.y - 2*w, size.z + 1], r - w);
    }
}

// Heat-set insert pocket (drilled from +Z face downward at this origin)
module insert_pocket(hole_d, depth) {
    translate([0, 0, -0.01]) cylinder(d = hole_d, h = depth + 0.01);
    // lead-in chamfer so the insert starts square
    translate([0, 0, -0.01]) cylinder(d1 = hole_d + 1.2, d2 = hole_d, h = 1.0);
}

// ──────────────────────────────────────────────────
// BODY  (the open tube + corner columns + power slot)
// ──────────────────────────────────────────────────
module body_columns() {
    for (p = col_pos) translate([p.x, p.y, 0])
        difference() {
            cylinder(d = col_od, h = body_h);
            // bottom insert (tray bolts up into here)
            translate([0, 0, 0]) rotate([0,0,0])
                insert_pocket(m3_insert_hole_dia, m3_insert_h + 1.5);
            // top insert (top plate bolts down into here)
            translate([0, 0, body_h])
                mirror([0,0,1]) insert_pocket(m3_insert_hole_dia, m3_insert_h + 1.5);
        }
}

module body_column_webs() {
    // Stadium-section gussets tying each column to the two nearest inner walls.
    for (p = col_pos) {
        xw = (p.x < cx) ? wall : box_l - wall;   // inner X wall face
        yw = (p.y < cy) ? wall : box_w - wall;   // inner Y wall face
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

module body_power_slot() {
    translate([cx - pwr_slot_w/2, box_w - wall - 0.5, pwr_slot_z])
        cube([pwr_slot_w, wall + 1.0, pwr_slot_h]);
}

module body() {
    difference() {
        union() {
            rounded_tube([box_l, box_w, body_h], corner_r, wall);
            body_columns();
            intersection() {   // keep webs inside the cavity only
                body_column_webs();
                translate([wall, wall, -1])
                    rounded_box([inner_l, inner_w, body_h + 2], corner_r - wall);
            }
        }
        body_power_slot();
    }
}

// ──────────────────────────────────────────────────
// BOTTOM TRAY  (Pi + buzzer mount here; bolts up into the body)
// ──────────────────────────────────────────────────
module tray_plate() {
    rounded_box([box_l, box_w, tray_h], corner_r);
    // centering spigot up into the body bore
    translate([wall + clr, wall + clr, tray_h - 0.01])
        rounded_tube([inner_l - 2*clr, inner_w - 2*clr, tray_lip_h + 0.01],
                     corner_r - wall, wall_min);
}

module tray_screw_holes() {
    // clearance + counterbore from the underside (heads hidden under bumpers)
    for (p = col_pos) translate([p.x, p.y, 0]) {
        translate([0,0,-0.01]) cylinder(d = m3_hole_dia, h = tray_h + 0.02);
        translate([0,0,-0.01]) cylinder(d = 6.5, h = 2.2);   // M3 head counterbore
    }
}

module pi_standoffs() {
    holes = [[0,0],[pi_hole_x_spacing,0],[0,pi_hole_y_spacing],
             [pi_hole_x_spacing,pi_hole_y_spacing]];
    for (h = holes)
        translate([pi_x + pi_hole_inset + h.x, pi_y + pi_hole_inset + h.y, tray_h])
            difference() {
                cylinder(d = pi_standoff_od, h = pi_standoff_h);
                translate([0,0,pi_standoff_h])
                    mirror([0,0,1]) insert_pocket(m25_insert_hole_dia, m25_insert_h);
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
        union() {
            tray_plate();
            pi_standoffs();
            buzzer_cradle();
        }
        tray_screw_holes();
        tray_vents();
        tray_bumpers();
        if (show_logo) tray_logo();
    }
}

// ──────────────────────────────────────────────────
// TOP PLATE  (LED halo hub + figurine well + MX buttons + RFID mounts)
// ──────────────────────────────────────────────────
module top_slab() {
    // full-footprint slab + a downward spigot that plugs into the body bore
    rounded_box([box_l, box_w, top_plate_h], corner_r);
    translate([wall + clr, wall + clr, -top_lip_h])
        rounded_tube([inner_l - 2*clr, inner_w - 2*clr, top_lip_h + 0.01],
                     corner_r - wall, wall_min);
}

module top_screw_holes() {
    // countersunk from the top into the body column top inserts
    for (p = col_pos) translate([p.x, p.y, 0]) {
        translate([0,0,-0.01]) cylinder(d = m3_hole_dia, h = top_plate_h + 0.02);
        translate([0,0,top_plate_h - 1.7])               // 90° countersink
            cylinder(d1 = m3_hole_dia, d2 = 6.4, h = 1.8);
    }
}

module led_hub() {
    // Solid hub the strip wraps around, rising above the slab.
    translate([hub_cx, hub_cy, top_plate_h - 0.01])
        cylinder(d = hub_od, h = hub_h + 0.01);
    // seating ledge for the diffuser ring, around the hub base
    translate([hub_cx, hub_cy, top_plate_h - 0.01])
        cylinder(d = ledge_od, h = 1.2);
}

module figurine_well() {
    // recess in the top of the hub for the center lid
    translate([hub_cx, hub_cy, top_plate_h + hub_h - well_depth])
        cylinder(d = well_id, h = well_depth + 0.1);
}

module strip_wire_notch() {
    // slot from the hub base down through the slab to route the 3 LED wires
    translate([hub_cx - strip_notch_w/2, hub_cy + hub_od/2 - 2, -0.1])
        cube([strip_notch_w, 6, top_plate_h + 3]);
}

module mx_cutout() {
    // Thick-plate MX mount: 14x14 clip plate on top, opening up below so the
    // body passes and the clips grab the mx_plate_t shelf.
    translate([0, 0, top_plate_h - mx_plate_t])
        translate([-mx_switch_cut/2, -mx_switch_cut/2, 0])
            cube([mx_switch_cut, mx_switch_cut, mx_plate_t + 0.1]);
    translate([-mx_switch_body/2, -mx_switch_body/2, -0.1])
        cube([mx_switch_body, mx_switch_body, top_plate_h - mx_plate_t + 0.2]);
}

module mx_buttons_cut() {
    for (bx = [btn1_x, btn2_x]) translate([bx, btn_y, 0]) mx_cutout();
}

module rfid_pocket() {
    // board-shaped clearance pocket on the underside (length along X) so the
    // board + header tuck up close without breaching the back wall.
    pl = mfrc522_l + 2*rfid_pocket_clr;
    pw = mfrc522_w + 2*rfid_pocket_clr;
    translate([hub_cx - pl/2, hub_cy - pw/2, -0.1])
        rounded_box([pl, pw, top_plate_h - rfid_seat_z + 0.1], 3);
}

module rfid_standoffs() {
    // antenna-up, header toward the front; M2 inserts
    z0 = top_plate_h - rfid_seat_z;          // pocket ceiling
    for (off = [[-mfrc522_hole_x/2, -mfrc522_hole_y/2],
                [ mfrc522_hole_x/2, -mfrc522_hole_y/2],
                [-mfrc522_hole_x/2,  mfrc522_hole_y/2],
                [ mfrc522_hole_x/2,  mfrc522_hole_y/2]])
        translate([hub_cx + off.x, hub_cy + off.y, z0 - rfid_standoff_h])
            difference() {
                cylinder(d = rfid_standoff_od, h = rfid_standoff_h + 0.01);
                insert_pocket(m2_insert_hole_dia, m2_insert_h);
            }
}

module top_plate() {
    difference() {
        union() {
            top_slab();
            led_hub();
            rfid_standoffs();
        }
        figurine_well();
        strip_wire_notch();
        mx_buttons_cut();
        rfid_pocket();
        top_screw_holes();
    }
}

// ──────────────────────────────────────────────────
// CENTER LID  (magnet landing disc; figurine snaps to it, RFID reads beneath)
// ──────────────────────────────────────────────────
lid_dia = well_id - clr;            // drops into the figurine well
lid_h   = well_depth;               // flush-ish with the hub top
lid_marker_dia  = lid_dia - 4;
lid_marker_line = 1.2;
lid_marker_depth = 0.6;

module lid_star(r1, r2) {
    polygon([for (i = [0:9])
        let (a = 90 + i*36, r = (i % 2 == 0) ? r1 : r2)
        [r*cos(a), r*sin(a)]]);
}

module center_lid() {
    difference() {
        cylinder(d = lid_dia, h = lid_h);
        // sealed magnet pockets (pause-and-insert, like the figurine base)
        for (mx = [-magnet_spacing/2, magnet_spacing/2])
            translate([mx, 0, magnet_seal_h])
                cylinder(d = magnet_pocket_dia, h = magnet_pocket_h);
        // engraved landing ring + star on top
        translate([0, 0, lid_h - lid_marker_depth]) {
            difference() {
                cylinder(d = lid_marker_dia, h = lid_marker_depth + 0.05);
                translate([0,0,-0.05])
                    cylinder(d = lid_marker_dia - 2*lid_marker_line,
                             h = lid_marker_depth + 0.15);
            }
            linear_extrude(lid_marker_depth + 0.05) lid_star(5.5, 2.3);
        }
    }
}

// ──────────────────────────────────────────────────
// DIFFUSER RING  (print in translucent / natural filament — it glows)
// Slips over the LED strip and seats on the hub-base ledge.
// ──────────────────────────────────────────────────
diffuser_id   = hub_od + 2*led_strip_t + 2*clr;     // clears the strip OD
diffuser_wall = 1.6;
diffuser_od   = diffuser_id + 2*diffuser_wall;
diffuser_h    = hub_h;

module diffuser_ring() {
    difference() {
        cylinder(d = diffuser_od, h = diffuser_h);
        translate([0,0,-0.01]) cylinder(d = diffuser_id, h = diffuser_h + 0.02);
    }
}

// ──────────────────────────────────────────────────
// Assembly / render
// ──────────────────────────────────────────────────
module assembly(gap = 0) {
    color("#f6f1e7") translate([0, 0, 0]) tray();
    color("#e9e2d0") translate([0, 0, tray_h + gap]) body();
    color("#7fd8c4") translate([0, 0, tray_h + body_h + 2*gap]) top_plate();
    color([0.9,1,0.95,0.45]) translate([hub_cx, hub_cy,
                                 tray_h + body_h + top_plate_h + 2.5*gap])
        diffuser_ring();
    color("#ffd166") translate([hub_cx, hub_cy,
                                 tray_h + body_h + top_plate_h + hub_h
                                 - well_depth + 3*gap]) center_lid();
    // big round keycaps perched on the two MX switches
    for (b = [[btn1_x, "play"], [btn2_x, "stop"]])
        color("#ef626c") translate([b[0], btn_y,
                             tray_h + body_h + top_plate_h + 4 + 2.5*gap])
            keycap_final(b[1]);
}

if      (render_part == "body")     body();
else if (render_part == "tray")     tray();
else if (render_part == "top")      top_plate();
else if (render_part == "lid")      center_lid();
else if (render_part == "diffuser") diffuser_ring();
else if (render_part == "assembly") assembly();
else if (render_part == "exploded") assembly(gap = 28);
