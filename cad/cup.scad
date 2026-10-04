// Glorb — triangular light cup (opaque)
// FACE_TYPE "A" or "B" picks equilateral vs isosceles placeholder geometry.
// Final: drive side lengths from facet_led_map.csv edge0/1/2 for each geo_id.

include <params.scad>

FACE_TYPE = "A"; // "A" or "B"

SIDE_A = FACE_TYPE == "A" ? STRUT_SHORT : STRUT_SHORT;
SIDE_B = FACE_TYPE == "A" ? STRUT_SHORT : STRUT_SHORT;
SIDE_C = FACE_TYPE == "A" ? STRUT_SHORT : STRUT_LONG;

module triangle_prism(s1, s2, s3, h, inset=0) {
    a = s1 - 2 * inset;
    b = s2 - 2 * inset;
    c = s3 - 2 * inset;
    sp = (a + b + c) / 2;
    area = sqrt(max(sp * (sp - a) * (sp - b) * (sp - c), 0.001));
    ha = 2 * area / a;
    x2 = (a*a + c*c - b*b) / (2 * a);
    pts = [[0, 0], [a, 0], [x2, ha]];
    cx = (pts[0][0] + pts[1][0] + pts[2][0]) / 3;
    cy = (pts[0][1] + pts[1][1] + pts[2][1]) / 3;
    linear_extrude(height=h)
        polygon([for (p = pts) [p[0] - cx, p[1] - cy]]);
}

module cup() {
    difference() {
        triangle_prism(SIDE_A, SIDE_B, SIDE_C, CUP_DEPTH + CUP_FLOOR);
        translate([0, 0, CUP_FLOOR])
            triangle_prism(SIDE_A, SIDE_B, SIDE_C, CUP_DEPTH + 0.2, inset=CUP_WALL);
        translate([0, 0, -0.1])
            cylinder(d=LED_BORE, h=CUP_FLOOR + 0.3, $fn=24);
        translate([0, -max(SIDE_A, SIDE_B, SIDE_C)/4, CUP_FLOOR/2])
            cube([LED_WIRE_SLOT, max(SIDE_A, SIDE_B, SIDE_C), CUP_FLOOR + 0.4], center=true);
        translate([0, 0, CUP_DEPTH + CUP_FLOOR - DIFFUSER_T])
            triangle_prism(SIDE_A, SIDE_B, SIDE_C, DIFFUSER_T + 0.2, inset=0.5);
    }
}

echo(str("cup type=", FACE_TYPE));
cup();
