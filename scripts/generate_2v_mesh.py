#!/usr/bin/env python3
"""Generate Class I 2V icosahedral geodesic sphere mesh for Glorb."""
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "mesh"
RADIUS_IN = 6.0
RADIUS_MM = RADIUS_IN * 25.4


def normalize(v):
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return (v[0] / n, v[1] / n, v[2] / n)


def unit_icosahedron():
    """Standard icosahedron on unit sphere (north pole, south pole, two pentagon rings)."""
    verts = []
    # poles
    verts.append((0.0, 0.0, 1.0))   # 0 north
    verts.append((0.0, 0.0, -1.0))  # 1 south
    # upper pentagon (z = 1/sqrt(5)), lower pentagon (z = -1/sqrt(5))
    z_u = 1.0 / math.sqrt(5.0)
    r_xy = 2.0 / math.sqrt(5.0)
    for i in range(5):
        a = 2.0 * math.pi * i / 5.0
        verts.append((r_xy * math.cos(a), r_xy * math.sin(a), z_u))
    for i in range(5):
        a = 2.0 * math.pi * i / 5.0 + math.pi / 5.0
        verts.append((r_xy * math.cos(a), r_xy * math.sin(a), -z_u))
    verts = [normalize(v) for v in verts]

    faces = []
    # north cap
    for i in range(5):
        faces.append((0, 2 + i, 2 + (i + 1) % 5))
    # south cap
    for i in range(5):
        faces.append((1, 7 + (i + 1) % 5, 7 + i))
    # upper band (pointing down) and lower band (pointing up)
    for i in range(5):
        u0 = 2 + i
        u1 = 2 + (i + 1) % 5
        l0 = 7 + i
        l1 = 7 + (i + 1) % 5
        faces.append((u0, l0, u1))
        faces.append((u1, l0, l1))
    return verts, faces


def midpoint(a, b):
    return normalize(((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5, (a[2] + b[2]) * 0.5))


def subdivide_2v(verts, faces):
    edge_mid = {}
    new_verts = list(verts)

    def mid_index(i, j):
        key = (min(i, j), max(i, j))
        if key not in edge_mid:
            edge_mid[key] = len(new_verts)
            new_verts.append(midpoint(verts[i], verts[j]))
        return edge_mid[key]

    new_faces = []
    for a, b, c in faces:
        ab = mid_index(a, b)
        bc = mid_index(b, c)
        ca = mid_index(c, a)
        new_faces.append((a, ab, ca))
        new_faces.append((b, bc, ab))
        new_faces.append((c, ca, bc))
        new_faces.append((ab, bc, ca))
    return new_verts, new_faces


def dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def face_edge_lengths(face, verts):
    a, b, c = face
    return [
        dist(verts[a], verts[b]),
        dist(verts[b], verts[c]),
        dist(verts[c], verts[a]),
    ]


def main():
    MESH.mkdir(parents=True, exist_ok=True)
    unit_verts, faces = unit_icosahedron()
    v2, f2 = subdivide_2v(unit_verts, faces)
    assert len(v2) == 42, len(v2)
    assert len(f2) == 80, len(f2)

    verts = [(p[0] * RADIUS_MM, p[1] * RADIUS_MM, p[2] * RADIUS_MM) for p in v2]

    edges = {}
    for a, b, c in f2:
        for i, j in ((a, b), (b, c), (c, a)):
            key = (min(i, j), max(i, j))
            if key not in edges:
                edges[key] = dist(verts[key[0]], verts[key[1]])
    assert len(edges) == 120, len(edges)

    lengths = list(edges.values())
    c1, c2 = min(lengths), max(lengths)
    for _ in range(12):
        g1 = [L for L in lengths if abs(L - c1) <= abs(L - c2)]
        g2 = [L for L in lengths if abs(L - c2) < abs(L - c1)]
        c1 = sum(g1) / len(g1)
        c2 = sum(g2) / len(g2)
    short_m, long_m = (c1, c2) if c1 < c2 else (c2, c1)

    def strut_type(L):
        return "short" if abs(L - short_m) <= abs(L - long_m) else "long"

    edge_to_faces = {}
    for fi, (a, b, c) in enumerate(f2):
        for i, j in ((a, b), (b, c), (c, a)):
            key = (min(i, j), max(i, j))
            edge_to_faces.setdefault(key, []).append(fi)
    neighbor_map = {i: set() for i in range(len(f2))}
    for fs in edge_to_faces.values():
        if len(fs) == 2:
            neighbor_map[fs[0]].add(fs[1])
            neighbor_map[fs[1]].add(fs[0])

    geo = []
    for fi, face in enumerate(f2):
        el = sorted(face_edge_lengths(face, verts))
        et = [strut_type(L) for L in el]
        ftype = "A" if et[0] == et[1] == et[2] else "B"
        cx = (verts[face[0]][0] + verts[face[1]][0] + verts[face[2]][0]) / 3
        cy = (verts[face[0]][1] + verts[face[1]][1] + verts[face[2]][1]) / 3
        cz = (verts[face[0]][2] + verts[face[1]][2] + verts[face[2]][2]) / 3
        n = math.sqrt(cx * cx + cy * cy + cz * cz)
        lat = math.degrees(math.asin(max(-1.0, min(1.0, cz / n))))
        lon = math.degrees(math.atan2(cy, cx))
        geo.append({
            "geo_id": fi,
            "face_type": ftype,
            "v0": face[0],
            "v1": face[1],
            "v2": face[2],
            "centroid_x_mm": round(cx, 3),
            "centroid_y_mm": round(cy, 3),
            "centroid_z_mm": round(cz, 3),
            "lat_deg": round(lat, 3),
            "lon_deg": round(lon, 3),
            "edge0_mm": round(el[0], 3),
            "edge1_mm": round(el[1], 3),
            "edge2_mm": round(el[2], 3),
            "neighbor_geo_ids": sorted(neighbor_map[fi]),
        })

    geo_sorted = sorted(geo, key=lambda r: (-r["lat_deg"], r["lon_deg"]))
    geo_to_led = {g["geo_id"]: i for i, g in enumerate(geo_sorted)}

    with open(MESH / "facet_led_map.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "led_index", "geo_id", "face_type",
            "centroid_x_mm", "centroid_y_mm", "centroid_z_mm",
            "lat_deg", "lon_deg",
            "edge0_mm", "edge1_mm", "edge2_mm",
            "v0", "v1", "v2",
        ])
        for led, g in enumerate(geo_sorted):
            w.writerow([
                led, g["geo_id"], g["face_type"],
                g["centroid_x_mm"], g["centroid_y_mm"], g["centroid_z_mm"],
                g["lat_deg"], g["lon_deg"],
                g["edge0_mm"], g["edge1_mm"], g["edge2_mm"],
                g["v0"], g["v1"], g["v2"],
            ])

    with open(MESH / "facet_neighbors.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["led_index", "neighbor_led_indices"])
        for led, g in enumerate(geo_sorted):
            nleds = sorted(geo_to_led[n] for n in g["neighbor_geo_ids"])
            w.writerow([led, ";".join(str(x) for x in nleds)])

    with open(MESH / "vertices.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["vertex_id", "x_mm", "y_mm", "z_mm"])
        for i, v in enumerate(verts):
            w.writerow([i, round(v[0], 3), round(v[1], 3), round(v[2], 3)])

    short_n = sum(1 for L in edges.values() if strut_type(L) == "short")
    long_n = sum(1 for L in edges.values() if strut_type(L) == "long")
    with open(MESH / "edge_lengths.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["strut_type", "length_mm", "length_in", "chord_factor", "count"])
        w.writerow([
            "short", round(short_m, 3), round(short_m / 25.4, 4),
            round(short_m / RADIUS_MM, 6), short_n,
        ])
        w.writerow([
            "long", round(long_m, 3), round(long_m / 25.4, 4),
            round(long_m / RADIUS_MM, 6), long_n,
        ])

    with open(MESH / "edges.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["v_a", "v_b", "length_mm", "strut_type"])
        for (a, b), L in sorted(edges.items()):
            w.writerow([a, b, round(L, 3), strut_type(L)])

    a_count = sum(1 for g in geo if g["face_type"] == "A")
    b_count = sum(1 for g in geo if g["face_type"] == "B")
    text = (
        f"Glorb 2V mesh @ R={RADIUS_MM:.3f} mm ({RADIUS_IN} in)\n"
        f"vertices={len(verts)} faces={len(f2)} edges={len(edges)}\n"
        f"strut short={short_m:.3f} mm ({short_m/25.4:.4f} in) chord={short_m/RADIUS_MM:.6f} x{short_n}\n"
        f"strut long={long_m:.3f} mm ({long_m/25.4:.4f} in) chord={long_m/RADIUS_MM:.6f} x{long_n}\n"
        f"face type A={a_count} B={b_count}\n"
        f"LED order: latitude desc, then longitude\n"
    )
    (MESH / "summary.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
