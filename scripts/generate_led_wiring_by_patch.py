#!/usr/bin/env python3
"""
Per-patch LED daisy-chains for Glorb (8 whole-cup submodules).
LED 1 in inward from facet.

Within each patch: exact minimax Hamiltonian path on LED positions.
Prefers neighbor-only dual edges when a path exists; otherwise allows
short Euclidean jumps inside the patch.
Inter-patch jumpers are out of scope (user allows long wires between modules).
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "mesh"
INWARD_MM = 25.4
LABELS = [f"N-lon{i}" for i in range(4)] + [f"S-lon{i}" for i in range(4)]


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


def section_id(lat, lon):
    if lon < 0:
        lon += 360
    ns = 0 if lat >= 0 else 1
    return ns * 4 + int(lon // 90) % 4


def mst_max_from_edges(nodes, edge_list):
    """Kruskal MST max edge among nodes using provided (d,i,j) edges."""
    nodes = list(nodes)
    if len(nodes) <= 1:
        return 0.0
    parent = {i: i for i in nodes}
    rank = {i: 0 for i in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
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

    used = 0
    last = 0.0
    for d, i, j in sorted(edge_list):
        if i not in parent or j not in parent:
            continue
        if union(i, j):
            last = d
            used += 1
            if used == len(nodes) - 1:
                return last
    return float("nan")


def exact_minimax_path(nodes, candidates):
    """
    Exact minimax Ham path.
    candidates: list of (dist, i, j) undirected edges available inside the patch.
    Returns (path, hops, max_hop) or raises if no Ham path.
    """
    nodes = list(nodes)
    nloc = len(nodes)
    if nloc == 1:
        return nodes, [], 0.0
    if nloc == 2:
        d = next(d for d, a, b in candidates if {a, b} == set(nodes))
        return [nodes[0], nodes[1]], [d], d

    # adjacency with distances
    adj = {i: {} for i in nodes}
    for d, i, j in candidates:
        if i in adj and j in adj:
            adj[i][j] = d
            adj[j][i] = d

    # unique thresholds from edges that could appear in a path
    thresholds = sorted({d for d, i, j in candidates if i in adj and j in adj})

    def ham_exists(limit):
        # build subgraph
        g = {i: [] for i in nodes}
        for i in nodes:
            for j, d in adj[i].items():
                if d <= limit + 1e-9:
                    g[i].append(j)

        # connectivity quick reject
        start0 = nodes[0]
        seen = {start0}
        stack = [start0]
        while stack:
            u = stack.pop()
            for v in g[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        if len(seen) != nloc:
            return None

        # degree-sorted Warnsdorff-style backtracking from every start
        def dfs(path, visited):
            if len(path) == nloc:
                return True
            u = path[-1]
            opts = [v for v in g[u] if v not in visited]
            opts.sort(key=lambda v: sum(1 for w in g[v] if w not in visited))
            for v in opts:
                visited.add(v)
                path.append(v)
                if dfs(path, visited):
                    return True
                path.pop()
                visited.remove(v)
            return False

        for s in nodes:
            path = [s]
            if dfs(path, {s}):
                return list(path)
        return None

    lo, hi = 0, len(thresholds) - 1
    best_path = None
    best_t = None
    # lower bound: MST max on candidate edges
    lb = mst_max_from_edges(nodes, candidates)
    # start binary search from first threshold >= lb
    while lo < len(thresholds) and thresholds[lo] < lb - 1e-9:
        lo += 1
    if lo > hi:
        lo = 0

    # binary search
    left, right = lo, hi
    while left <= right:
        mid = (left + right) // 2
        t = thresholds[mid]
        path = ham_exists(t)
        if path is not None:
            best_path = path
            best_t = t
            right = mid - 1
        else:
            left = mid + 1

    if best_path is None:
        # exhaustive fallback from high end
        for t in thresholds:
            path = ham_exists(t)
            if path is not None:
                best_path = path
                best_t = t
                break
    if best_path is None:
        raise RuntimeError("no Ham path in candidate graph")

    hops = [
        adj[best_path[k]][best_path[k + 1]] for k in range(len(best_path) - 1)
    ]
    return best_path, hops, max(hops) if hops else 0.0


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
        led_p = sub(c, mul(nrm, INWARD_MM))
        lat = float(row["lat_deg"])
        lon = float(row["lon_deg"])
        faces.append(
            {
                "geo_id": int(row["geo_id"]),
                "face_type": row["face_type"],
                "v0": v0,
                "v1": v1,
                "v2": v2,
                "led": led_p,
                "lat": lat,
                "lon": lon,
                "patch_id": section_id(lat, lon),
            }
        )

    n = len(faces)
    led = [f["led"] for f in faces]
    edge_to = defaultdict(list)
    for i, f in enumerate(faces):
        a, b, c = f["v0"], f["v1"], f["v2"]
        for e in (
            (min(a, b), max(a, b)),
            (min(b, c), max(b, c)),
            (min(c, a), max(c, a)),
        ):
            edge_to[e].append(i)
    nbr = defaultdict(list)
    for fs in edge_to.values():
        if len(fs) == 2:
            nbr[fs[0]].append(fs[1])
            nbr[fs[1]].append(fs[0])
    nbrset = {i: set(nbr[i]) for i in range(n)}

    patches = defaultdict(list)
    for i, f in enumerate(faces):
        patches[f["patch_id"]].append(i)

    rows = []
    stats = []
    lines = []
    global_max = 0.0

    for pid in range(8):
        nodes = patches[pid]
        name = LABELS[pid]

        # neighbor edges inside patch
        nbr_edges = []
        for i in nodes:
            for j in nbr[i]:
                if j > i and j in set(nodes):
                    nbr_edges.append((dist(led[i], led[j]), i, j))

        # complete graph edges
        all_edges = []
        for a in range(len(nodes)):
            for b in range(a + 1, len(nodes)):
                i, j = nodes[a], nodes[b]
                all_edges.append((dist(led[i], led[j]), i, j))

        neighbor_mode = False
        try:
            path, hops, bot = exact_minimax_path(nodes, nbr_edges)
            neighbor_mode = True
            mode = "neighbor-only"
        except RuntimeError:
            path, hops, bot = exact_minimax_path(nodes, all_edges)
            mode = "with-jumps"

        mean = sum(hops) / len(hops) if hops else 0.0
        bound = mst_max_from_edges(
            nodes, nbr_edges if neighbor_mode else all_edges
        )
        non_nbr = sum(
            1
            for k in range(len(path) - 1)
            if path[k + 1] not in nbrset[path[k]]
        )
        global_max = max(global_max, bot)
        # Binary-search + backtracking is exact for n<=11; MST is only a
        # lower bound (path may need a longer bottleneck than the tree).
        stats.append(
            {
                "patch_id": pid,
                "patch_name": name,
                "n_cups": len(nodes),
                "mode": mode,
                "max_hop_mm": round(bot, 3),
                "max_hop_in": round(bot / 25.4, 4),
                "mean_hop_mm": round(mean, 3),
                "mst_bound_mm": round(bound, 3),
                "optimal": True,
                "non_neighbor_hops": non_nbr,
            }
        )
        lines.append(
            f"{name}: n={len(nodes):2d}  max={bot:.3f} mm ({bot/25.4:.4f} in)"
            f"  mean={mean:.3f} mm  jumps={non_nbr}  mode={mode}  OPTIMAL"
        )
        for wi, fi in enumerate(path):
            hop = hops[wi] if wi < len(hops) else ""
            is_nbr = ""
            if wi < len(hops):
                is_nbr = "yes" if path[wi + 1] in nbrset[fi] else "JUMP"
            lx, ly, lz = led[fi]
            rows.append(
                [
                    pid,
                    name,
                    wi,
                    faces[fi]["geo_id"],
                    faces[fi]["face_type"],
                    round(lx, 3),
                    round(ly, 3),
                    round(lz, 3),
                    round(hop, 3) if hop != "" else "",
                    round(hop / 25.4, 4) if hop != "" else "",
                    is_nbr,
                ]
            )

    with open(MESH / "led_wiring_by_patch.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "patch_id",
                "patch_name",
                "wire_index_in_patch",
                "geo_id",
                "face_type",
                "led_x_mm",
                "led_y_mm",
                "led_z_mm",
                "hop_to_next_mm",
                "hop_to_next_in",
                "is_mesh_neighbor",
            ]
        )
        w.writerows(rows)

    with open(
        MESH / "led_wiring_by_patch_summary.csv", "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.DictWriter(f, fieldnames=list(stats[0].keys()))
        w.writeheader()
        w.writerows(stats)

    text = (
        "Per-patch chains (inter-patch jumpers allowed separately)\n"
        f"LED depth: 1.00 in ({INWARD_MM} mm) inward\n"
        f"Within patch: exact minimax path; neighbor-only if Hamiltonian, "
        f"else short jumps\n"
        f"Worst patch max-hop: {global_max:.3f} mm = {global_max/25.4:.4f} in\n\n"
        + "\n".join(lines)
        + "\n"
    )
    (MESH / "led_wiring_by_patch_summary.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
