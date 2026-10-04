#!/usr/bin/env python3
"""Generate firmware/include/face_map.h from mesh CSVs."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "mesh"
OUT = ROOT / "firmware" / "include"
OUT.mkdir(parents=True, exist_ok=True)

facets = list(csv.DictReader(open(MESH / "facet_led_map.csv", encoding="utf-8")))
facets.sort(key=lambda r: int(r["led_index"]))
rows = list(csv.DictReader(open(MESH / "facet_neighbors.csv", encoding="utf-8")))
rows.sort(key=lambda r: int(r["led_index"]))

lines = [
    "#pragma once",
    "#include <Arduino.h>",
    "",
    "static const uint8_t NUM_FACES = 80;",
    "",
    "// Latitude degrees per led_index (for band effects)",
    "static const float FACE_LAT_DEG[NUM_FACES] = {",
]
for i, r in enumerate(facets):
    comma = "," if i < 79 else ""
    lines.append(f"  {float(r['lat_deg']):.3f}f{comma}")
lines.append("};")
lines.append("")
lines.append("// Up to 3 neighbor LED indices; unused slots = -1")
lines.append("static const int8_t FACE_NEIGHBORS[NUM_FACES][3] = {")
for i, r in enumerate(rows):
    ns = [int(x) for x in r["neighbor_led_indices"].split(";") if x != ""]
    while len(ns) < 3:
        ns.append(-1)
    ns = ns[:3]
    comma = "," if i < 79 else ""
    lines.append(f"  {{{ns[0]}, {ns[1]}, {ns[2]}}}{comma}")
lines.append("};")
lines.append("")

path = OUT / "face_map.h"
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", path)
print("face types", Counter(r["face_type"] for r in facets))
