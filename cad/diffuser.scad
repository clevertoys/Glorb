// Glorb — translucent diffuser plate for light cup
// Print in white / natural translucent PLA or PETG.

include <params.scad>

FACE_TYPE = "A";
SIDE_A = FACE_TYPE == "A" ? STRUT_SHORT : STRUT_SHORT;
SIDE_B = FACE_TYPE == "A" ? STRUT_SHORT : STRUT_SHORT;
SIDE_C = FACE_TYPE == "A" ? STRUT_SHORT : STRUT_LONG;

module triangle_plate(s1, s2, s3, h) {
    sp = (s1 + s2 + s3) / 2;
    area = sqrt(max(sp * (sp - s1) * (sp - s2) * (sp - s3), 0.001));
    ha = 2 * area / s1;
    x2 = (s1*s1 + s3*s3 - s2*s2) / (2 * s1);
    pts = [[0, 0], [s1, 0], [x2, ha]];
    cx = (pts[0][0] + pts[1][0] + pts[2][0]) / 3;
    cy = (pts[0][1] + pts[1][1] + pts[2][1]) / 3;
    linear_extrude(height=h)
        polygon([for (p = pts) [p[0] - cx, p[1] - cy]]);
}

// Slightly undersized vs cup lip recess
triangle_plate(SIDE_A - 1.4, SIDE_B - 1.4, SIDE_C - 1.4, DIFFUSER_T);
