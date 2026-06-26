// babybox-case-v2.scad — "Pebble" revision of the BabyBox enclosure
//
// Compact, toy-styled two-piece case: 105 x 85 x 54 mm (vs v1: 150 x 110 x 75).
// 61% smaller volume. The breadboard bay is GONE — wiring is direct
// (dupont jumpers / soldered) to the Pi header, which is what made the
// old case so big.
//
// DESIGN LANGUAGE — looks like a commercial toy:
//   * Big 14mm corner radius + 5mm domed roundover on the lid (pebble look)
//   * The front is a FACE: two chunky button "eyes" (play/pause + stop)
//     and a wide recessed "mouth" whose floor is a sealed 0.8mm skin the
//     LEDs glow through — visible smile when off, glowing smile when on,
//     no through-hole, no insert, fully babyproof and diffused
//   * Engraved cheek dimples, star landing pad on top
//   * Two-tone by printing body and lid in different colors
//   * NO visible screws: 4x M3 enter from the BOTTOM into posts that
//     hang from the lid. A toddler cannot open it.
//
// ASSEMBLY (easy, ~10 min):
//   1. Screw Pi Zero 2 W onto floor standoffs (4x M2.5)
//   2. Screw MFRC522 onto lid ceiling standoffs (4x M2, header toward FRONT)
//   3. Press 12mm buttons into the eye holes (nut on inside)
//   4. Seat LED strip in the mouth pocket (rests on shelf, dab of hot glue)
//   5. Buzzer drops into its floor cradle
//   6. Wire everything to the Pi header (leave a service loop to the lid)
//   7. Place lid, flip box, drive 4x M3 screws + stick 4 silicone bumpers
//
// PRINTING:
//   * BODY: floor on bed, no supports
//   * LID: print UPSIDE-DOWN (top face on bed), no supports.
//     PAUSE at Z = 4.2 mm, drop the 2 magnets into the open cavities
//     (check polarity against figurines!), resume — fully sealed inside.
//
// Render: set render_part below, F5 to preview, F6 + export STL.

include <../common-params.scad>

// === Render Selector ===
// "body" | "lid" | "assembly" | "exploded"
render_part = "assembly";

$fn = 48;

// === Outer Dimensions ===
box_l      = 105;   // outer length (X)
box_w      = 85;    // outer width  (Y)
body_h     = 40;    // body outer height
lid_h      = 14;    // lid outer height       (total = 54)
wall       = 3;     // side wall thickness
floor_h    = 3;     // floor thickness
corner_r   = 14;    // XY corner radius (toddler-safe, toy look)
lid_edge_r = 5;     // 3D roundover on lid top edges (pebble dome)

inner_l = box_l - 2*wall;   // 99
inner_w = box_w - 2*wall;   // 79

// Lid nesting lip
lip_h         = 4;
lip_clearance = 0.4;

// === Pi Zero 2 W ===
pi_l = 65;  pi_w = 30;
pi_hole_x_spacing = 58;
pi_hole_y_spacing = 23;
pi_hole_inset     = 3.5;
pi_standoff_h     = 6;
pi_standoff_od    = 5.5;
pi_x = 18;                         // board left edge (clears rear-left post)
pi_y = box_w - wall - pi_w - 2;    // 2mm off the back inner wall (= 50)

// Port cutouts (back wall) — ports sit on top of the board
port_z     = floor_h + pi_standoff_h + 1;   // bottom of cutouts
hdmi_cut_w = 13;  hdmi_cut_h = 5.5;
usb_cut_w  = 9.5; usb_cut_h  = 5.5;
pi_hdmi_cx = pi_x + 12.4;   // mini HDMI center
pi_otg_cx  = pi_x + 41.4;   // micro USB OTG center
pi_pwr_cx  = pi_x + 54.0;   // micro USB power center

// === Face: button "eyes" ===
btn_hole_dia = 12.5;        // 12mm panel-mount momentary buttons
btn_z        = 26;          // eye height on front wall
btn_spacing  = 36;
btn1_x = box_l/2 - btn_spacing/2;   // 34.5 (play/pause)
btn2_x = box_l/2 + btn_spacing/2;   // 70.5 (stop)
bezel_od     = 19;          // raised eye ring
bezel_depth  = 2.5;         // how proud of the front wall

// === Face: LED "mouth" ===
// WS2812 8-LED stick (51.1 x 10.2 x 3.2). The mouth is a 0.6mm-deep
// recess on the OUTER face (visible smile when LEDs are off); behind it
// a pocket from the inside leaves a 0.8mm diffuser skin for the glow.
led_strip_l  = 51.1;
led_strip_w  = 10.2;
led_strip_h  = 3.2;
mouth_l      = 55;          // glow window length
mouth_h      = 11;          // glow window height (strip is 10.2)
mouth_r      = 5;           // corner radius of the smile
mouth_z      = 4.5;         // bottom of window
mouth_recess = 0.6;         // visible recess depth on the outer face
mouth_skin   = 1.4;         // total skin from outer face (1.4 - 0.6 = 0.8 diffuser)
cheek_dia    = 9;
cheek_depth  = 0.6;

// === Buzzer ===
buzzer_dia      = 12;
buzzer_mount_od = 15;
buzzer_mount_h  = 3;
buzzer_x = 88;  buzzer_y = 26;   // front-right floor, clear of post + Pi

// === Lid posts + hidden bottom screws ===
post_od    = 9;
post_inset = 12;            // post centers from outer corner
post_len   = body_h - floor_h;     // 33 — posts reach the floor
post_tap_depth = 14;        // M3 self-tap depth in post end
cbore_d    = 6.5;           // screw head counterbore in floor
cbore_h    = 1.8;
post_pos = [
    [post_inset,         post_inset],
    [box_l - post_inset, post_inset],
    [post_inset,         box_w - post_inset],
    [box_l - post_inset, box_w - post_inset]
];

// === Bottom details ===
bumper_dia   = 11;          // recess for 10mm stick-on silicone bumpers
bumper_depth = 0.5;
bumper_pos   = [[22,18],[83,18],[22,67],[83,67]];
vent_w = 3;  vent_l = 14;   // finger-safe floor vents under the Pi
vent_x = [30, 42, 54, 66];
vent_y = 58;

// === Lid: RFID + magnets + landing pad ===
rfid_standoff_h  = 4;
rfid_standoff_od = 5;
magnet_boss_od   = magnet_pocket_dia + 2*wall_min;
// boss hangs below ceiling far enough to give magnet_seal_h floor under cavity
magnet_boss_h    = (magnet_seal_h + magnet_pocket_h) - wall + magnet_seal_h;  // 2.2
figurine_marker_dia   = 36;
figurine_marker_line  = 1.2;
figurine_marker_depth = 0.6;
star_r1 = 5.5;  star_r2 = 2.3;       // landing star (kept clear of magnets)
lid_magnet_pause_z = magnet_seal_h + magnet_pocket_h;   // print-coord pause

cx = box_l/2;  cy = box_w/2;

// === Sanity echoes ===
echo(str(">>> BabyBox v2 'Pebble': ", box_l, " x ", box_w, " x ", body_h + lid_h, " mm"));
echo(str(">>> LID: print UPSIDE-DOWN, pause at Z = ", lid_magnet_pause_z,
         " mm, insert 2x 6x3mm magnets, resume."));
assert(pi_x + pi_l <= wall + inner_l - 2, "Pi does not fit in X");
assert(pi_y + pi_w <= box_w - wall, "Pi does not fit in Y");
assert(mouth_h >= led_strip_w + 0.6, "LED strip taller than mouth window");
assert(post_inset - post_od/2 >= wall + 1, "posts intersect walls");
// 12mm button nut (r~8) must clear the lid lip zone
assert(btn_z + 8 <= body_h - lip_h - 1, "button hardware hits lid lip");
// eye bezels must not clip the mouth recess
assert(btn_z - bezel_od/2 >= mouth_z + mouth_h + 0.5, "bezels overlap mouth");

// ──────────────────────────────────────────────────
// Utility
// ──────────────────────────────────────────────────

module rounded_box(size, r) {
    hull()
        for (x = [r, size.x - r], y = [r, size.y - r])
            translate([x, y, 0]) cylinder(r = r, h = size.z);
}

module rounded_slab_xz(l, h, r) {
    // Rounded-corner plate standing in the XZ plane (for face cutouts)
    hull()
        for (x = [r, l - r], z = [r, h - r])
            translate([x, 0, z]) rotate([-90, 0, 0]) cylinder(r = r, h = 1);
}

module star(r1, r2) {
    polygon([for (i = [0:9])
        let (a = 90 + i*36, r = (i % 2 == 0) ? r1 : r2)
        [r*cos(a), r*sin(a)]]);
}

// ──────────────────────────────────────────────────
// Body
// ──────────────────────────────────────────────────

module body_shell() {
    difference() {
        rounded_box([box_l, box_w, body_h], corner_r);
        translate([wall, wall, floor_h])
            rounded_box([inner_l, inner_w, body_h], corner_r - wall);
    }
}

module pi_standoffs() {
    holes = [[0,0],[pi_hole_x_spacing,0],[0,pi_hole_y_spacing],
             [pi_hole_x_spacing,pi_hole_y_spacing]];
    for (h = holes)
        translate([pi_x + pi_hole_inset + h.x, pi_y + pi_hole_inset + h.y, floor_h])
            difference() {
                cylinder(d = pi_standoff_od, h = pi_standoff_h);
                translate([0,0,-0.01])
                    cylinder(d = m25_tap_dia, h = pi_standoff_h + 0.02);
            }
}

module pi_port_cutouts() {
    for (p = [[pi_hdmi_cx, hdmi_cut_w, hdmi_cut_h],
              [pi_otg_cx,  usb_cut_w,  usb_cut_h],
              [pi_pwr_cx,  usb_cut_w,  usb_cut_h]])
        translate([p[0] - p[1]/2, box_w - wall - 0.5, port_z])
            cube([p[1], wall + 1.5, p[2]]);
}

module eye_bezels() {
    // Tapered raised rings around the button holes (the "eyes")
    for (bx = [btn1_x, btn2_x])
        translate([bx, 0.01, btn_z])
            rotate([90, 0, 0])
                cylinder(d1 = bezel_od, d2 = bezel_od - 3, h = bezel_depth);
}

module eye_holes() {
    for (bx = [btn1_x, btn2_x])
        translate([bx, bezel_depth + 1, btn_z])
            rotate([90, 0, 0])
                cylinder(d = btn_hole_dia, h = wall + bezel_depth + 2);
}

module mouth_shape(depth) {
    // rounded-rect prism extruded in +Y (the smile silhouette)
    hull()
        for (x = [mouth_r, mouth_l - mouth_r], z = [mouth_r, mouth_h - mouth_r])
            translate([x, 0, z]) rotate([-90, 0, 0]) cylinder(r = mouth_r, h = depth);
}

module mouth_smile_recess() {
    // Visible recess on the OUTER face — the face has a smile even when off
    translate([cx - mouth_l/2, -0.01, mouth_z])
        mouth_shape(mouth_recess + 0.01);
}

module mouth_pocket() {
    // Pocket cut from the INSIDE of the front wall; together with the
    // outer recess this leaves a sealed 0.8mm diffuser skin. No openings.
    translate([cx - mouth_l/2, mouth_skin, mouth_z])
        mouth_shape(wall - mouth_skin + led_strip_h + 1.5);
}

module mouth_shelf() {
    // Ledge the LED strip rests on, at the pocket floor
    translate([cx - mouth_l/2 - 1, wall - 0.01, floor_h])
        cube([mouth_l + 2, led_strip_h + 2, mouth_z - floor_h]);
}

module cheeks() {
    for (chx = [17.5, box_l - 17.5])
        translate([chx, -0.01, 13])
            rotate([-90, 0, 0])
                cylinder(d = cheek_dia, h = cheek_depth);
}

module buzzer_mount() {
    translate([buzzer_x, buzzer_y, floor_h])
        difference() {
            cylinder(d = buzzer_mount_od, h = buzzer_mount_h);
            translate([0,0,-0.01])
                cylinder(d = buzzer_dia + 0.4, h = buzzer_mount_h + 0.02);
        }
}

module floor_screw_holes() {
    for (p = post_pos) translate([p.x, p.y, 0]) {
        translate([0,0,-0.01]) cylinder(d = m3_hole_dia, h = floor_h + 0.02);
        translate([0,0,-0.01]) cylinder(d = cbore_d, h = cbore_h);
    }
}

module floor_vents() {
    for (vx = vent_x)
        translate([vx - vent_w/2, vent_y, -0.01])
            rounded_box([vent_w, vent_l, floor_h + 0.02], vent_w/2 - 0.01);
}

module bumper_recesses() {
    for (p = bumper_pos)
        translate([p.x, p.y, -0.01])
            cylinder(d = bumper_dia, h = bumper_depth);
}

module bottom_logo() {
    // Engraved on the underside; mirrored so it reads correctly from below
    translate([cx, cy, bumper_depth + 0.01])
        rotate([180, 0, 0])
            linear_extrude(0.5 + bumper_depth)
                text("BabyBox", size = 8, font = "Liberation Sans:style=Bold",
                     halign = "center", valign = "center");
}

module body() {
    difference() {
        union() {
            body_shell();
            pi_standoffs();
            buzzer_mount();
            mouth_shelf();
            eye_bezels();
        }
        pi_port_cutouts();
        eye_holes();
        mouth_smile_recess();
        mouth_pocket();
        cheeks();
        floor_screw_holes();
        floor_vents();
        bumper_recesses();
        bottom_logo();
    }
}

// ──────────────────────────────────────────────────
// Lid
// ──────────────────────────────────────────────────

module lid_blank() {
    // Flat-bottomed pebble: vertical sides, 3D-rounded top edges.
    e = lid_edge_r;
    intersection() {
        translate([e, e, 0])
            minkowski() {
                rounded_box([box_l - 2*e, box_w - 2*e, lid_h - e], corner_r - e);
                sphere(r = e);
            }
        translate([-1, -1, 0]) cube([box_l + 2, box_w + 2, lid_h]);
    }
}

module lid_hollow() {
    translate([wall, wall, -0.01])
        rounded_box([inner_l, inner_w, lid_h - wall + 0.01], corner_r - wall);
}

module lid_lip() {
    inset = wall + lip_clearance;
    difference() {
        translate([inset, inset, -lip_h])
            rounded_box([box_l - 2*inset, box_w - 2*inset, lip_h + 0.01],
                        corner_r - inset);
        translate([inset + wall_min + 0.4, inset + wall_min + 0.4, -lip_h - 0.01])
            rounded_box([box_l - 2*(inset + wall_min + 0.4),
                         box_w - 2*(inset + wall_min + 0.4), lip_h + 0.03],
                        corner_r - inset - wall_min - 0.4);
    }
}

module lid_posts() {
    // Full-height posts: screws come up from the bottom — nothing visible on top
    for (p = post_pos) translate([p.x, p.y, 0]) {
        translate([0, 0, -post_len])
            cylinder(d = post_od, h = post_len + lid_h - wall + 0.01);
        // gusset where the post meets the ceiling
        translate([0, 0, lid_h - wall - 2.5])
            cylinder(d1 = post_od, d2 = post_od + 5, h = 2.5);
    }
}

module lid_post_taps() {
    for (p = post_pos)
        translate([p.x, p.y, -post_len - 0.01])
            cylinder(d = m3_tap_dia, h = post_tap_depth);
}

module rfid_standoffs() {
    // MFRC522 hangs antenna-up against the lid ceiling. Header toward FRONT.
    for (off = [[-mfrc522_hole_x/2, -mfrc522_hole_y/2],
                [ mfrc522_hole_x/2, -mfrc522_hole_y/2],
                [-mfrc522_hole_x/2,  mfrc522_hole_y/2],
                [ mfrc522_hole_x/2,  mfrc522_hole_y/2]])
        translate([cx + off.x, cy + off.y, lid_h - wall - rfid_standoff_h])
            difference() {
                cylinder(d = rfid_standoff_od, h = rfid_standoff_h + 0.01);
                translate([0,0,-0.01])
                    cylinder(d = m2_tap_dia, h = rfid_standoff_h + 0.03);
            }
}

module magnet_bosses() {
    for (mx = [-magnet_spacing/2, magnet_spacing/2])
        translate([cx + mx, cy, lid_h - wall - magnet_boss_h])
            cylinder(d = magnet_boss_od, h = magnet_boss_h + 0.01);
}

module magnet_pockets() {
    for (mx = [-magnet_spacing/2, magnet_spacing/2])
        translate([cx + mx, cy, lid_h - magnet_seal_h - magnet_pocket_h])
            cylinder(d = magnet_pocket_dia, h = magnet_pocket_h);
}

module landing_pad() {
    // Engraved ring + star showing where the figurine snaps on.
    // Ring and star stay clear of the magnet pockets (seal not thinned).
    translate([cx, cy, lid_h - figurine_marker_depth]) {
        difference() {
            cylinder(d = figurine_marker_dia, h = figurine_marker_depth + 0.01);
            translate([0,0,-0.01])
                cylinder(d = figurine_marker_dia - 2*figurine_marker_line,
                         h = figurine_marker_depth + 0.03);
        }
        linear_extrude(figurine_marker_depth + 0.01)
            star(star_r1, star_r2);
    }
}

module lid() {
    difference() {
        union() {
            // hollow the shell FIRST, then add the hanging features
            difference() {
                union() { lid_blank(); lid_lip(); }
                lid_hollow();
            }
            lid_posts();
            rfid_standoffs();
            magnet_bosses();
        }
        magnet_pockets();
        landing_pad();
        lid_post_taps();
    }
}

// ──────────────────────────────────────────────────
// Assembly / render
// ──────────────────────────────────────────────────

module assembly(gap = 0) {
    color("#f6f1e7") body();
    color("#7fd8c4") translate([0, 0, body_h + gap]) lid();
}

if (render_part == "body")          body();
else if (render_part == "lid")      lid();
else if (render_part == "assembly") assembly();
else if (render_part == "exploded") assembly(gap = 35);
