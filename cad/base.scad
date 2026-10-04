// Glorb — base (2-piece: floor tub with short lip + skirted top with column socket)
// Top slides down over tub lip. Bay: 12V pack + buck + ESP32 + barrel jack
// Orientation: −Y = front (power switch), +Y = back (DC jack)
// Overall H ≈ 51.5 mm · OD BASE_D (170 mm)

include <params.scad>

module base_tub() {
    // Full-OD floor (flush with top skirt) + short register lip
    difference() {
        union() {
            cylinder(d=BASE_D, h=BASE_FLOOR_T, $fn=96);
            translate([0, 0, BASE_FLOOR_T])
                cylinder(d=BASE_LIP_OD, h=BASE_LIP_H, $fn=96);
        }
        translate([0, 0, BASE_FLOOR_T])
            cylinder(d=BASE_BAY_ID, h=BASE_LIP_H + 1, $fn=88);
    }
}

module base_bay_keepouts() {
    translate([-5, -18, BASE_FLOOR_T + BATT_XYZ[2]/2])
        cube(BATT_XYZ, center=true);
    translate([3, 42, BASE_FLOOR_T + BUCK_XYZ[2]/2])
        cube(BUCK_XYZ, center=true);
    translate([-28, 28, BASE_FLOOR_T + ESP32_XYZ[2]/2])
        cube(ESP32_XYZ, center=true);
}

module base_shell() {
    // Skirt walls + lid + column socket; ports in skirt
    difference() {
        union() {
            cylinder(d=BASE_D, h=BASE_CLEAR_H + BASE_SHELL_T, $fn=96);
            translate([0, 0, BASE_CLEAR_H + BASE_SHELL_T])
                cylinder(d=COLUMN_OD_BASE + 6, h=12, $fn=48);
        }
        // Bay cavity (skirt ID) — leaves lid
        translate([0, 0, -0.01])
            cylinder(d=BASE_ID, h=BASE_CLEAR_H + 0.02, $fn=88);
        // Column bore in socket
        translate([0, 0, BASE_CLEAR_H + BASE_SHELL_T - 1])
            cylinder(d=COLUMN_OD_BASE + 0.4, h=14, $fn=48);
        // Wire bore through lid
        translate([0, 0, BASE_CLEAR_H - 1])
            cylinder(d=COLUMN_ID - 1, h=BASE_SHELL_T + 14, $fn=40);
        translate([15, 0, BASE_CLEAR_H - 1])
            cylinder(d=8, h=BASE_SHELL_T + 2, $fn=24);

        // KCD1-5-101 power switch on lid (front −Y)
        translate([SW_POS[0], SW_POS[1], BASE_CLEAR_H - 1])
            cylinder(d=SW_HOLE_D, h=BASE_SHELL_T + 2, $fn=48);
        translate([SW_POS[0], SW_POS[1], BASE_CLEAR_H - 0.01])
            cylinder(d=SW_CBORE_D, h=BASE_SHELL_T - SW_PANEL_T + 0.02, $fn=48);

        // Barrel jack in skirt at back (+Y)
        translate([0, BASE_D/2 - 1, JACK_CENTER_Z - BASE_FLOOR_T])
            rotate([90, 0, 0])
                cylinder(d=JACK_HOLE_D, h=BASE_WALL_T + 8, $fn=36);

        // USB slot (−X)
        translate([-BASE_D/2 + BASE_WALL_T/2, 28, 10])
            cube([BASE_WALL_T + 4, 14, 10], center=true);
    }
}

base_tub();
translate([0, 0, BASE_FLOOR_T])
    base_shell();
