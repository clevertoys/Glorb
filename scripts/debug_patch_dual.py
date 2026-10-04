#!/usr/bin/env python3
import csv
from collections import defaultdict

faces = []
for row in csv.DictReader(open("mesh/facet_led_map.csv", encoding="utf-8")):
    lat = float(row["lat_deg"])
    lon = float(row["lon_deg"])
    if lon < 0:
        lon += 360
    pid = (0 if lat >= 0 else 1) * 4 + int(lon // 90) % 4
    faces.append(
        {
            "geo": int(row["geo_id"]),
            "v": (int(row["v0"]), int(row["v1"]), int(row["v2"])),
            "pid": pid,
        }
    )

edge_to = defaultdict(list)
for i, f in enumerate(faces):
    a, b, c = f["v"]
    for e in (
        (min(a, b), max(a, b)),
        (min(b, c), max(b, c)),
        (min(c, a), max(c, a)),
    ):
        edge_to[e].append(i)
nbr = defaultdict(set)
for fs in edge_to.values():
    if len(fs) == 2:
        nbr[fs[0]].add(fs[1])
        nbr[fs[1]].add(fs[0])

for pid in range(8):
    nodes = [i for i, f in enumerate(faces) if f["pid"] == pid]
    degs = [sum(1 for j in nbr[i] if j in set(nodes)) for i in nodes]
    seen = set()
    stack = [nodes[0]]
    nset = set(nodes)
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        for v in nbr[u]:
            if v in nset:
                stack.append(v)
    print(
        f"patch {pid} n={len(nodes)} connected={len(seen)==len(nodes)} "
        f"deg={sorted(degs)} geos={[faces[i]['geo'] for i in nodes]}"
    )
