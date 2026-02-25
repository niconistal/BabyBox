// base-template.scad — Parametric figurine base for BabyBox
// All figurines share this base; the decorative top is merged separately.
//
// HIDDEN MAGNETS: Magnets are fully enclosed inside the base.
//   1. Print this part right-side up (flat bottom on bed)
//   2. Pause at Z = magnet_seal_h + magnet_pocket_h (see echo output)
//   3. Drop 2x neodymium magnets into the open cavities
//   4. Resume print — ceiling layers seal the magnets inside
//
// Usage: Open in OpenSCAD, set render_part below, then F5 (preview) or F6 (render).

use <../common-params.scad>
include <../common-params.scad>

// === Render selector ===
// "base"        — printable base only
// "cross"       — cross-section for inspection
// "demo"        — base with a sample figurine body on top
render_part = "base";  // change this to switch views

// === Base Parameters ===
base_dia      = 35;    // outer diameter
base_h        = 6;     // total height (floor + magnet + ceiling + margin)
chamfer       = 0.8;   // bottom edge chamfer

// Derived: pause height for magnet insertion
magnet_pause_z = magnet_seal_h + magnet_pocket_h;
magnet_ceiling = base_h - magnet_pause_z;

// === Figurine Demo ===
demo_body_dia = 20;    // sample body diameter
demo_body_h   = 30;    // sample body height

$fn = 80;  // circle smoothness

// Print the pause height to the console
echo(str(">>> FIGURINE BASE: Pause print at Z = ", magnet_pause_z, " mm to insert magnets"));
echo(str("    Floor below magnets: ", magnet_seal_h, " mm"));
echo(str("    Magnet cavity: ", magnet_pocket_h, " mm"));
echo(str("    Ceiling above magnets: ", magnet_ceiling, " mm"));

// ──────────────────────────────────────────
// Modules
// ──────────────────────────────────────────

module base_body() {
    // Cylinder with chamfered bottom edge via rotate_extrude of a 2D profile
    r = base_dia / 2;
    rotate_extrude()
        polygon([
            [0, 0],
            [r - chamfer, 0],     // bottom edge, inset by chamfer
            [r, chamfer],          // outer wall starts after chamfer
            [r, base_h],           // top outer edge
            [0, base_h],           // top center
        ]);
}

module magnet_pockets() {
    // Two enclosed magnet cavities inside the base.
    // Floor: Z = 0 to magnet_seal_h (solid, printed first)
    // Cavity: Z = magnet_seal_h to magnet_seal_h + magnet_pocket_h (hollow)
    // Ceiling: Z = magnet_pause_z to base_h (solid, printed after pause)
    for (x = [-magnet_spacing/2, magnet_spacing/2]) {
        translate([x, 0, magnet_seal_h])
            cylinder(d = magnet_pocket_dia, h = magnet_pocket_h);
    }
}

module rfid_recess() {
    // Shallow recess on the bottom face for the RFID coin sticker
    translate([0, 0, -0.01])
        cylinder(d = rfid_recess_dia, h = rfid_recess_h + 0.01);
}

module figurine_base() {
    difference() {
        base_body();
        magnet_pockets();
        rfid_recess();
    }
}

module cross_section() {
    // Half-cut view for inspecting pocket depths and wall thicknesses
    difference() {
        figurine_base();
        translate([0, -base_dia, -1])
            cube([base_dia, base_dia * 2, base_h + 2]);
    }
}

module demo() {
    // Base + sample cylindrical body to visualize a complete figurine
    figurine_base();
    translate([0, 0, base_h])
        cylinder(d1 = demo_body_dia, d2 = demo_body_dia * 0.7, h = demo_body_h);
}

// ──────────────────────────────────────────
// Render
// ──────────────────────────────────────────

if (render_part == "base") {
    figurine_base();
} else if (render_part == "cross") {
    cross_section();
} else if (render_part == "demo") {
    demo();
}
