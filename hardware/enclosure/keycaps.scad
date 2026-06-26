// keycaps.scad — Big round custom keycaps for the BabyBox v3 "Tower"
//
// NOT standard square 1u caps — these are chunky CIRCULAR buttons sized for
// toddler fingers, that press straight onto a Cherry-MX (compatible) switch
// stem. Two caps: PLAY/PAUSE (triangle + bars) and STOP (square), each with
// the icon engraved 0.6 mm into the domed top so it survives sticky hands.
//
// PRINTING: print TOP-DOWN (flat top on the bed). The chamfered top lands
// flat, the hollow underside and the + stem socket print cleanly with no
// supports. For a two-tone icon, do a filament swap at the engrave depth,
// or just print solid and the recessed icon reads fine on its own.
//
// FIT NOTE: the + socket is sized for a 0.15 mm press-fit. If your caps are
// loose, drop mx_stem_arm_t by 0.05; if they won't seat, raise it by 0.05.
//
// Render: set render_part, F5 preview, F6 + export STL.

include <../common-params.scad>

// "play" | "stop" | "both"
render_part = "both";

$fn = 96;

cap_d     = mx_keycap_round_dia;    // 24 — big round button
cap_h     = mx_keycap_round_h;      // 11
top_cham  = 3.0;                    // rounded-looking top chamfer
wall      = 1.4;                    // skirt wall
top_th    = 2.6;                    // solid roof under the icon
boss_od   = 7.0;                    // stem mount boss
icon_depth = 0.6;

// ──────────────────────────────────────────────────
// Cap shell + stem
// ──────────────────────────────────────────────────
module cap_blank() {
    // round puck with a chamfered top edge (prints flat-top-down)
    rotate_extrude()
        polygon([
            [0, 0],
            [cap_d/2, 0],
            [cap_d/2, cap_h - top_cham],
            [cap_d/2 - top_cham, cap_h],
            [0, cap_h],
        ]);
}

module mx_stem_socket() {
    // the + cross the switch stem presses into (a press-fit negative)
    linear_extrude(mx_stem_depth + 0.05) {
        square([mx_stem_cross_w, mx_stem_arm_t], center = true);
        square([mx_stem_arm_t, mx_stem_cross_w], center = true);
    }
}

module stem_mount() {
    // boss bridging the cap roof down to the switch stem
    difference() {
        cylinder(d = boss_od, h = cap_h - top_th);
        translate([0, 0, -0.01]) mx_stem_socket();
    }
    // four little ribs tying the boss to the skirt so the cap can't twist
    for (a = [45, 135, 225, 315])
        rotate([0, 0, a])
            translate([0, 0, 0])
                linear_extrude(cap_h - top_th)
                    polygon([[boss_od/2 - 0.2, -1], [cap_d/2 - wall, -0.6],
                             [cap_d/2 - wall, 0.6], [boss_od/2 - 0.2, 1]]);
}

// ──────────────────────────────────────────────────
// Icons (engraved into the top)
// ──────────────────────────────────────────────────
module icon_play_pause() {
    translate([-3.7, 0]) polygon([[-3, -4.5], [-3, 4.5], [3.6, 0]]);  // play ▶
    translate([3.2, 0]) square([1.9, 9], center = true);             // ❚
    translate([6.1, 0]) square([1.9, 9], center = true);             //  ❚
}
module icon_stop() { square([8.5, 8.5], center = true); }            // ■

// The skirt cavity is cut FIRST, then the stem boss/ribs are added back, so
// the boss survives (it lives inside the hollow).
module keycap_final(which) {
    union() {
        difference() {
            cap_blank();
            translate([0, 0, -0.01])
                cylinder(d = cap_d - 2*wall, h = cap_h - top_th + 0.01);
            translate([0, 0, cap_h - icon_depth])
                linear_extrude(icon_depth + 0.05)
                    if (which == "play") icon_play_pause(); else icon_stop();
        }
        stem_mount();
    }
}

if      (render_part == "play") keycap_final("play");
else if (render_part == "stop") keycap_final("stop");
else {
    translate([-cap_d/2 - 3, 0, 0]) keycap_final("play");
    translate([ cap_d/2 + 3, 0, 0]) keycap_final("stop");
}
