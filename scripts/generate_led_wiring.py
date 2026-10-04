#!/usr/bin/env python3
"""
Minimax-ish neighbor LED daisy-chain for Glorb.
LED 1 in inward from facet. Warnsdorff Ham path on dual + bottleneck 2-opt.
Also reports dual-MST lower bound and max neighbor edge.
"""
from __future__ import annotations

import csv
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "mesh"
INWARD_MM = 25.4


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


def norm(v):
    return math.sqrt(dot(v, v))


def normalize(v):
    n = norm(v)
    return (v[0] / n, v[1] / n, v[2] / n)


def dist(a, b):
    return norm(sub(a, b))


def warnsdorff_path(nbr, n, start, led):
    """Greedy Ham path; returns path or None if stuck."""
    path = [start]
    visited = {start}
    while len(path) < n:
        u = path[-1]
        opts = [v for v in nbr[u] if v not in visited]
        if not opts:
            return None
        opts.sort(
            key=lambda v: (
                sum(1 for w in nbr[v] if w not in visited),
                dist(led[u], led[v]),
            )
        )
        path.append(opts[0])
        visited.add(opts[0])
    return path


def path_hops(path, led):
    return [dist(led[path[k]], led[path[k + 1]]) for k in range(len(path) - 1)]


def bottleneck_2opt(path, nbrset, led):
    n = len(path)
    improved = True
    while improved:
        improved = False
        hops = path_hops(path, led)
        bot = max(hops)
        for a in range(n - 1):
            for b in range(a + 2, n):
                if path[b] not in nbrset[path[a]]:
                    continue
                if b + 1 < n and path[a + 1] not in nbrset[path[b + 1]]:
                    continue
                new_path = (
                    path[: a + 1]
                    + list(reversed(path[a + 1 : b + 1]))
                    + path[b + 1 :]
                )
                if max(path_hops(new_path, led)) + 1e-9 < bot:
                    path = new_path
                    improved = True
                    break
            if improved:
                break
    return path


def main():
    verts = {}
    for row in csv.DictReader(open(MESH / "vertices.csv", encoding="utf-8")):
        verts[int(row["vertex_id"])] = (
            float(row["x_mm"]),
            float(row["y_mm"]),
            float(row["z_mm"]),
        )

    faces = []
    for row in csv.DictReader(open(MESH / "facet_led_map.csv", encoding="utf-8")):
        v0, v1, v2 = int(row["v0"]), int(row["v1"]), int(row["v2"])
        p0, p1, p2 = verts[v0], verts[v1], verts[v2]
        c = mul(add(add(p0, p1), p2), 1.0 / 3.0)
        nrm = normalize(cross(sub(p1, p0), sub(p2, p0)))
        if dot(nrm, c) < 0:
            nrm = mul(nrm, -1)
        led = sub(c, mul(nrm, INWARD_MM))
        faces.append(
            {
                "geo_id": int(row["geo_id"]),
                "face_type": row["face_type"],
                "v0": v0,
                "v1": v1,
                "v2": v2,
                "led": led,
                "lat": float(row["lat_deg"]),
                "lon": float(row["lon_deg"]),
            }
        )

    n = len(faces)
    led = [f["led"] for f in faces]
    edge_to_faces = defaultdict(list)
    for i, f in enumerate(faces):
        a, b, c = f["v0"], f["v1"], f["v2"]
        for e in (
            (min(a, b), max(a, b)),
            (min(b, c), max(b, c)),
            (min(c, a), max(c, a)),
        ):
            edge_to_faces[e].append(i)

    nbr = defaultdict(list)
    dual_edges = []
    for fs in edge_to_faces.values():
        if len(fs) == 2:
            i, j = fs[0], fs[1]
            nbr[i].append(j)
            nbr[j].append(i)
            dual_edges.append((dist(led[i], led[j]), i, j))
    dual_edges.sort()
    nbrset = {i: set(nbr[i]) for i in range(n)}

    # MST lower bound
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_max = 0.0
    used = 0
    for d, i, j in dual_edges:
        ri, rj = find(i), find(j)
        if ri == rj:
            continue
        parent[ri] = rj
        mst_max = d
        used += 1
        if used == n - 1:
            break
    max_neighbor = dual_edges[-1][0]

    # Try many Warnsdorff starts; keep path with smallest bottleneck
    best = None
    best_bot = float("inf")
    order = list(range(n))
    # prioritize poles
    order.sort(key=lambda i: led[i][2])
    starts = order[:10] + order[-10:] + list(range(n))
    random.seed(42)
    extra = list(range(n))
    random.shuffle(extra)
    starts = list(dict.fromkeys(starts + extra))  # unique preserve order

    for s in starts:
        p = warnsdorff_path(nbr, n, s, led)
        if p is None:
            continue
        p = bottleneck_2opt(p, nbrset, led)
        bot = max(path_hops(p, led))
        if bot < best_bot:
            best_bot = bot
            best = p
            # early exit if we hit MST lower bound
            if abs(bot - mst_max) < 1e-6:
                break

    if best is None:
        raise RuntimeError("Warnsdorff failed for all starts")

    path = best
    hops = path_hops(path, led)
    bottleneck = max(hops)
    bot_i = max(range(len(hops)), key=lambda k: hops[k])

    # Unrestricted multi-fragment
    all_edges = [
        (dist(led[i], led[j]), i, j)
        for i in range(n)
        for j in range(i + 1, n)
    ]
    all_edges.sort()
    parent = list(range(n))
    rank = [0] * n

    def find3(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union3(a, b):
        ra, rb = find3(a), find3(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        elif rank[ra] > rank[rb]:
            parent[rb] = ra
        else:
            parent[rb] = ra
            rank[ra] += 1
        return True

    degree = [0] * n
    u_hops = []
    for d, i, j in all_edges:
        if degree[i] >= 2 or degree[j] >= 2:
            continue
        if not union3(i, j):
            continue
        degree[i] += 1
        degree[j] += 1
        u_hops.append(d)
        if len(u_hops) == n - 1:
            break

    with open(MESH / "led_wiring_sequence.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "wire_index",
                "geo_id",
                "face_type",
                "led_x_mm",
                "led_y_mm",
                "led_z_mm",
                "hop_to_next_mm",
                "hop_to_next_in",
            ]
        )
        for wi, fi in enumerate(path):
            hop = hops[wi] if wi < len(hops) else ""
            lx, ly, lz = led[fi]
            w.writerow(
                [
                    wi,
                    faces[fi]["geo_id"],
                    faces[fi]["face_type"],
                    round(lx, 3),
                    round(ly, 3),
                    round(lz, 3),
                    round(hop, 3) if hop != "" else "",
                    round(hop / 25.4, 4) if hop != "" else "",
                ]
            )

    def section_id(f):
        lon = f["lon"]
        if lon < 0:
            lon += 360
        ns = 0 if f["lat"] >= 0 else 1
        return ns * 4 + int(lon // 90) % 4

    labels = [f"N-lon{i}" for i in range(4)] + [f"S-lon{i}" for i in range(4)]
    with open(MESH / "print_patches_8.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["geo_id", "patch_id", "patch_name", "lat_deg", "lon_deg"])
        for face in faces:
            pid = section_id(face)
            w.writerow([face["geo_id"], pid, labels[pid], face["lat"], face["lon"]])

    patch_lines = []
    for pid, name in enumerate(labels):
        geos = [
            faces[i]["geo_id"] for i in range(n) if section_id(faces[i]) == pid
        ]
        patch_lines.append(f"{name} (id={pid}): {len(geos)} cups — geo_ids {geos}")
    (MESH / "print_patches_8.txt").write_text("\n".join(patch_lines) + "\n", encoding="utf-8")

    text = (
        f"LED depth: 1.00 in ({INWARD_MM} mm) inward from facet face\n"
        f"Chain: neighboring cups only (shared mesh edge)\n"
        f"MAX HOP: {bottleneck:.3f} mm = {bottleneck/25.4:.4f} in\n"
        f"Worst hop: wire_index {bot_i}->{bot_i+1} "
        f"(geo_id {faces[path[bot_i]]['geo_id']} -> {faces[path[bot_i+1]]['geo_id']})\n"
        f"Mean hop: {sum(hops)/len(hops):.3f} mm = {sum(hops)/len(hops)/25.4:.4f} in\n"
        f"Lower bound (dual MST max edge): {mst_max:.3f} mm = {mst_max/25.4:.4f} in\n"
        f"Upper bound (longest dual edge): {max_neighbor:.3f} mm = {max_neighbor/25.4:.4f} in\n"
        f"Unrestricted chain (may jump): {max(u_hops):.3f} mm = {max(u_hops)/25.4:.4f} in\n"
        f"Optimal? {'YES (matches MST bound)' if abs(bottleneck-mst_max)<1e-4 else 'heuristic (between MST bound and max dual edge)'}\n"
    )
    (MESH / "led_wiring_summary.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
