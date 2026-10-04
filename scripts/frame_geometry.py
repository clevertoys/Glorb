#!/usr/bin/env python3
"""
Build Glorb frame in Fusion: no hub nodes, 1mm faceplate rabbets.
This file is the source of truth for the Fusion MCP script body.
"""
# The Fusion-executed script is embedded in the agent call; this module
# mirrors the geometry helpers for local testing if needed.

from __future__ import annotations

import math


def normalize(v):
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
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
    """Inset a 3D triangle by dist in its plane. Returns three new corners."""
    if dist <= 0:
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
        db = sub(b2, b1)
        # solve a1 + da*s = b1 + db*t in plane using cross with normal
        # (a1 + da*s - b1) x db · n = 0
        ab = sub(a1, b1)
        # 2D basis on plane
        xaxis = normalize(da)
        yaxis = normalize(cross(n, xaxis))

        def to2(p):
            return (dot(sub(p, a1), xaxis), dot(sub(p, a1), yaxis))

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

    # new vertex i = intersection of offset edge (i-1,i) and (i,i+1)
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
        return normalize(
            ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5, (a[2] + b[2]) * 0.5)
        )

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
