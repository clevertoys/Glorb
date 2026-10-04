// Glorb — edge strut
// Set STRUT_LEN to short or long chord, minus 2*HUB_SOCKET_DEPTH for print length.

include <params.scad>

STRUT_TYPE = "short"; // "short" or "long"
CHORD = STRUT_TYPE == "short" ? STRUT_SHORT : STRUT_LONG;
PRINT_LEN = CHORD - 2 * HUB_SOCKET_DEPTH;

module strut() {
    difference() {
        cylinder(d=STRUT_OD, h=PRINT_LEN, $fn=28, center=true);
        cylinder(d=STRUT_ID, h=PRINT_LEN + 1, $fn=20, center=true);
        // slight taper cues at ends for hub entry
        for (s = [-1, 1])
            translate([0, 0, s * PRINT_LEN/2])
                cylinder(d1=STRUT_OD - 0.4, d2=STRUT_OD + 0.2, h=1.5, center=true, $fn=28);
    }
}

echo(str("strut type=", STRUT_TYPE, " print_len_mm=", PRINT_LEN));
strut();
