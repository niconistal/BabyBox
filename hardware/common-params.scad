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
