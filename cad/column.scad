// Glorb — central wiring column

include <params.scad>

module column() {
    difference() {
        cylinder(d=COLUMN_OD, h=COLUMN_LEN, $fn=64);
        translate([0, 0, -1])
            cylinder(d=COLUMN_ID, h=COLUMN_LEN + 2, $fn=56);
        // side exits for power injection (two latitudes)
        for (z = [COLUMN_LEN * 0.35, COLUMN_LEN * 0.65])
            translate([0, 0, z])
                rotate([0, 90, 0])
                    cylinder(d=6, h=COLUMN_OD, $fn=24);
    }
}

column();
