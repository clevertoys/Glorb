// Glorb — vertex hub (generic)
// Export: hub.stl  ·  print 42 (polar hubs may use hub_polar.scad later)

include <params.scad>

module hub_body() {
    difference() {
        sphere(d=HUB_BALL, $fn=48);
        // hollow for weight / wires near equator hubs
        sphere(d=HUB_BALL - 4, $fn=36);
        // strut sockets: placeholder along +X,+Y,+Z and three tetrahedral dirs
        // Final hubs need per-vertex strut directions from mesh/vertices.csv + edges.csv
        for (a = [0, 120, 240])
            rotate([35, 0, a])
                translate([0, 0, HUB_BALL/2 - HUB_SOCKET_DEPTH])
                    cylinder(d=STRUT_OD + 0.3, h=HUB_SOCKET_DEPTH + 2, $fn=24);
    }
}

hub_body();
