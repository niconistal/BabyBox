// common-params.scad — Shared dimensions for BabyBox enclosure + figurines
// All values in millimeters

// === Neodymium Magnets (6x3mm disc) ===
magnet_dia       = 6;      // nominal diameter
magnet_h         = 3;      // nominal height
magnet_pocket_dia = 6.3;   // pocket diameter (0.3mm clearance for drop-in)
magnet_pocket_h  = 3.2;    // cavity height (0.2mm extra so magnet sits below rim)
magnet_spacing   = 20;     // center-to-center distance between the two magnets
magnet_seal_h    = 1.0;    // solid wall thickness enclosing magnets on each side
                            // (pause print, insert magnets, resume to seal)

// === RFID Sticker Tag (25mm coin, MIFARE 13.56 MHz) ===
rfid_tag_dia     = 25;     // nominal diameter
rfid_tag_h       = 0.3;    // sticker thickness (very thin)
rfid_recess_dia  = 25.5;   // recess diameter (0.5mm tolerance)
rfid_recess_h    = 0.5;    // recess depth

// === MFRC522 RFID Module ===
mfrc522_l        = 60;     // board length
mfrc522_w        = 40;     // board width
mfrc522_h        = 4;      // PCB thickness (without header)
mfrc522_h_header = 8;      // total height with header pins
mfrc522_hole_dia = 2;      // mounting hole diameter (M2)
mfrc522_hole_x   = 56;     // mounting hole X spacing
mfrc522_hole_y   = 36;     // mounting hole Y spacing
mfrc522_hole_margin_x = 2; // hole inset from board edge X
mfrc522_hole_margin_y = 2; // hole inset from board edge Y

// === Print Tolerances ===
tol              = 0.3;    // general clearance tolerance
press_tol        = 0.15;   // press-fit tolerance (tighter)
wall_min         = 1.2;    // minimum printable wall thickness (3 perimeters at 0.4mm)

// === Screw Dimensions ===
m2_hole_dia      = 2.2;    // M2 clearance hole
m2_tap_dia       = 1.6;    // M2 self-tap hole in plastic
m25_hole_dia     = 2.7;    // M2.5 clearance hole
m25_tap_dia      = 2.0;    // M2.5 self-tap hole in plastic
m3_hole_dia      = 3.2;    // M3 clearance hole
m3_tap_dia       = 2.5;    // M3 self-tap hole in plastic

// ===================================================================
//  v3 "Tower" additions
// ===================================================================

// === Brass heat-set inserts (threaded inserts melted into plastic) ===
// The v3 build uses heat-set inserts everywhere instead of self-tapping,
// so the box can be opened and re-assembled many times. Default values are
// for the very common McMaster/CNC-Kitchen style tapered inserts. Tune the
// *_hole_dia to your specific inserts if needed (a touch tight is better —
// the melted brass swages into the wall).
//
// M3 insert (standard, body<->tray + top plate)
m3_insert_hole_dia = 4.0;   // pilot hole the insert melts into
m3_insert_h        = 5.0;   // insert length (boss must be deeper)
m3_insert_boss_od  = 6.5;   // outer diameter of the boss around the insert
// M2.5 insert (Pi Zero 2 W mounting)
m25_insert_hole_dia = 3.5;
m25_insert_h        = 4.0;
m25_insert_boss_od  = 5.5;
// M2 insert (MFRC522 mounting)
m2_insert_hole_dia  = 3.2;
m2_insert_h         = 3.5;
m2_insert_boss_od   = 5.0;

// === SunFounder WS2812B flexible strip (the LED "halo" ring) ===
// 8x 5050 RGB LEDs, 60 pixels/m -> 16.67 mm pitch, flexible & cuttable.
// Bent into a circle the lit length wraps to a centerline circle:
//   circumference = pitch * count  ->  dia = (pitch*count)/PI
led_count        = 8;
led_pitch        = 16.67;   // mm between LEDs (60/m)
led_strip_w      = 10.0;    // strip width  (standard 5050 flex strip)
led_strip_t      = 2.0;     // strip thickness (datasheet: 2 mm)
led_strip_fit    = 0.6;     // clearance added to width/thickness for the channel
// Centerline diameter when the strip is curled into a ring.
led_ring_mid_dia = (led_pitch * led_count) / PI;     // ~42.4 mm
led_lead_w       = 8;       // notch width for the 3-wire pigtail to drop through

// === Cherry MX (compatible) keyswitches + custom keycaps ===
// Plate-mount MX switch: 14x14 mm plate cutout, clips grab a ~1.5 mm plate.
mx_switch_cut    = 14.0;    // square hole in the plate (top-of-plate)
mx_switch_body   = 15.6;    // switch top housing footprint (sits ON the plate)
mx_plate_t       = 1.5;     // plate thickness the switch clips engage
mx_switch_below  = 5.0;     // body depth below the plate (to the pins start)
mx_switch_pins_h = 3.3;     // pin/leg protrusion below the body
mx_keycap_pitch  = 19.05;   // 1u spacing (center-to-center of adjacent caps)
// v3 uses BIG ROUND toddler keycaps instead of square 1u caps
mx_keycap_round_dia = 24;   // chunky circular button cap
mx_keycap_round_h   = 11;   // cap height above the plate (domed)
// MX stem (the + cross on the switch the keycap presses onto)
mx_stem_cross_w  = 4.1;     // length of each arm of the + (outer span)
mx_stem_arm_t    = 1.35;    // thickness of each arm (1.17 nominal + fit)
mx_stem_depth    = 4.0;     // how deep the cross socket goes into the cap

function led_ring_id() = led_ring_mid_dia - led_strip_t - led_strip_fit;  // inner wall sits here
function led_ring_od() = led_ring_mid_dia + led_strip_t + led_strip_fit;  // outer wall sits here
