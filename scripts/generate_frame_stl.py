#!/usr/bin/env python3
"""Generate Glorb frame STL: no hubs, 1mm faceplate rabbets on each triangular opening."""
from __future__ import annotations

import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "stl"
OUT.mkdir(parents=True, exist_ok=True)

# Design in mm
R_MM = 6.0 * 25.4
FACEPLATE_T = 1.0       # mm — flush pocket depth
RIM = 2.0               # mm — outer strut rim outside faceplate
LEDGE = 1.5             # mm — support under faceplate
STRUT_DEPTH = 8.0       # mm — frame thickness inward


def normalize(v):
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return (v[0] / n, v[1] / n, v[2] / n)


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def inset_triangle(p0, p1, p2, dist):
    if dist <= 1e-9:
        return p0, p1, p2
    pts = [p0, p1, p2]
    n = normalize(cross(sub(p1, p0), sub(p2, p0)))
    c = mul(add(add(p0, p1), p2), 1.0 / 3.0)

    def offset_line(a, b):
        t = normalize(sub(b, a))
        inward = normalize(cross(n, t))
        if dot(inward, sub(c, a)) < 0:
            inward = mul(inward, -1)
        o = mul(inward, dist)
        return add(a, o), add(b, o)

    lines = [
        offset_line(pts[0], pts[1]),
        offset_line(pts[1], pts[2]),
        offset_line(pts[2], pts[0]),
    ]

    def intersect(l1, l2):
        (a1, a2), (b1, b2) = l1, l2
        da = sub(a2, a1)
        xaxis = normalize(da)
        yaxis = normalize(cross(n, xaxis))

        def to2(p):
            d = sub(p, a1)
            return (dot(d, xaxis), dot(d, yaxis))

        ax1, ay1 = to2(a1)
        ax2, ay2 = to2(a2)
        bx1, by1 = to2(b1)
        bx2, by2 = to2(b2)
        dax, day = ax2 - ax1, ay2 - ay1
        dbx, dby = bx2 - bx1, by2 - by1
        den = dax * dby - day * dbx
        if abs(den) < 1e-12:
            return a1
        s = ((bx1 - ax1) * dby - (by1 - ay1) * dbx) / den
        return add(a1, mul(da, s))

    q0 = intersect(lines[2], lines[0])
    q1 = intersect(lines[0], lines[1])
    q2 = intersect(lines[1], lines[2])
    return q0, q1, q2


def unit_icosa_2v():
    verts = [(0.0, 0.0, 1.0), (0.0, 0.0, -1.0)]
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
    for i in range(5):
        faces.append((0, 2 + i, 2 + (i + 1) % 5))
    for i in range(5):
        faces.append((1, 7 + (i + 1) % 5, 7 + i))
    for i in range(5):
        u0, u1 = 2 + i, 2 + (i + 1) % 5
        l0, l1 = 7 + i, 7 + (i + 1) % 5
        faces.append((u0, l0, u1))
        faces.append((u1, l0, l1))

    edge_mid = {}
    new_verts = list(verts)

    def midpoint(a, b):
        return normalize(((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5, (a[2] + b[2]) * 0.5))

    def mid_index(i, j):
        key = (min(i, j), max(i, j))
        if key not in edge_mid:
            edge_mid[key] = len(new_verts)
            new_verts.append(midpoint(verts[i], verts[j]))
        return edge_mid[key]

    new_faces = []
    for a, b, c in faces:
        ab, bc, ca = mid_index(a, b), mid_index(b, c), mid_index(c, a)
        new_faces += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
    return new_verts, new_faces


def face_normal(p0, p1, p2):
    n = normalize(cross(sub(p1, p0), sub(p2, p0)))
    # outward = away from origin
    c = mul(add(add(p0, p1), p2), 1.0 / 3.0)
    if dot(n, c) < 0:
        n = mul(n, -1)
    return n


def tri_norm(a, b, c):
    return normalize(cross(sub(b, a), sub(c, a)))


def add_tri(tris, a, b, c):
    n = tri_norm(a, b, c)
    tris.append((n, a, b, c))


def add_quad(tris, a, b, c, d):
    # a-b-c-d around face
    add_tri(tris, a, b, c)
    add_tri(tris, a, c, d)


def ring_prism_walls(tris, top, bot):
    """Side walls between two triangles (same winding)."""
    for i in range(3):
        j = (i + 1) % 3
        add_quad(tris, top[i], top[j], bot[j], bot[i])


def frame_for_face(p0, p1, p2, tris):
    n = face_normal(p0, p1, p2)
    outer = (p0, p1, p2)
    fp = inset_triangle(p0, p1, p2, RIM)
    inner = inset_triangle(p0, p1, p2, RIM + LEDGE)

    # Levels along -n (inward from outer sphere face)
    def shift(tri, dist):
        o = mul(n, -dist)
        return tuple(add(p, o) for p in tri)

    # z=0 outer surface, z=FACEPLATE_T ledge level, z=STRUT_DEPTH bottom
    outer0 = outer
    outerD = shift(outer, STRUT_DEPTH)
    fp0 = fp
    fpT = shift(fp, FACEPLATE_T)
    innerT = shift(inner, FACEPLATE_T)
    innerD = shift(inner, STRUT_DEPTH)

    # Outer flush rim (top): outer0 -> fp0 annulus
    for i in range(3):
        j = (i + 1) % 3
        add_quad(tris, outer0[i], outer0[j], fp0[j], fp0[i])

    # Rabbet vertical wall: fp0 -> fpT
    ring_prism_walls(tris, fp0, fpT)

    # Ledge seat (under faceplate): fpT -> innerT annulus
    for i in range(3):
        j = (i + 1) % 3
        add_quad(tris, fpT[i], fpT[j], innerT[j], innerT[i])

    # Inner window walls: innerT -> innerD
    ring_prism_walls(tris, innerT, innerD)

    # Outer vertical walls: outer0 -> outerD
    ring_prism_walls(tris, outer0, outerD)

    # Bottom annulus: outerD -> innerD
    for i in range(3):
        j = (i + 1) % 3
        add_quad(tris, outerD[i], innerD[i], innerD[j], outerD[j])


def write_binary_stl(path: Path, tris):
    # Fix normals to match winding
    buf = bytearray()
    buf += b"Glorb frame no-hubs 1mm rabbet".ljust(80, b"\0")
    buf += struct.pack("<I", len(tris))
    for n, a, b, c in tris:
        # recompute normal
        nn = tri_norm(a, b, c)
        buf += struct.pack(
            "<12fH",
            nn[0], nn[1], nn[2],
            a[0], a[1], a[2],
            b[0], b[1], b[2],
            c[0], c[1], c[2],
            0,
        )
    path.write_bytes(buf)


def main():
    unit_verts, faces = unit_icosa_2v()
    pts = [mul(v, R_MM) for v in unit_verts]
    tris = []
    for a, b, c in faces:
        frame_for_face(pts[a], pts[b], pts[c], tris)
    out = OUT / "Frame_Channels.stl"
    write_binary_stl(out, tris)
    print(f"wrote {out} tris={len(tris)}")
    print(
        f"R={R_MM} faceplate_t={FACEPLATE_T} rim={RIM} ledge={LEDGE} depth={STRUT_DEPTH}"
    )


if __name__ == "__main__":
    main()
