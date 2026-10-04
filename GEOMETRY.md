# Glorb — Geometry

Class I **2V** icosahedral geodesic sphere · design outer radius **R = 6.00 in (152.4 mm)** · OD **~12 in**.

Regenerate maps anytime:

```bash
python scripts/generate_2v_mesh.py
```

Outputs land in [`mesh/`](mesh/).

---

## Topology

| Item | Count |
|------|-------|
| Faces (facets / LEDs) | **80** |
| Vertices (hubs) | **42** |
| Edges (struts) | **120** |

Built by subdividing each of the 20 icosahedron faces into 4 triangles (edge midpoints projected onto the sphere).

---

## Strut lengths (locked at R = 152.4 mm)

| Type | Length | Chord factor (L/R) | Qty |
|------|--------|--------------------|-----|
| **short** | **83.292 mm** (3.279 in) | **0.546533** | **60** |
| **long** | **94.188 mm** (3.708 in) | **0.618034** | **60** |

Source: [`mesh/edge_lengths.csv`](mesh/edge_lengths.csv) · per-edge list: [`mesh/edges.csv`](mesh/edges.csv).

Scale rule: at a different radius R′, multiply lengths by `R′ / 152.4`.

---

## Face types (light cups)

| Type | Meaning | Qty | Cup STL |
|------|---------|-----|---------|
| **A** | All three edges same strut class (near-equilateral after projection) | **20** | Cup A |
| **B** | Mixed short/long edges (isosceles) | **60** | Cup B |

Per-face edge lengths and vertex IDs: [`mesh/facet_led_map.csv`](mesh/facet_led_map.csv).

---

## LED / assembly index order

`led_index` **0..79** is the daisy-chain order and FastLED address.

**Sort:** latitude descending (north → south), then longitude ascending.

| File | Role |
|------|------|
| [`mesh/facet_led_map.csv`](mesh/facet_led_map.csv) | `led_index`, `geo_id`, `face_type`, centroid, lat/lon, edges, vertices |
| [`mesh/facet_neighbors.csv`](mesh/facet_neighbors.csv) | Adjacency in **LED** indices (ripple effects) |
| [`mesh/vertices.csv`](mesh/vertices.csv) | Hub positions (mm) |

Coordinate frame: sphere center at origin; **+Z = north pole** (top); column along Z; base below south pole.

---

## Design notes for CAD

- Strut length in CAD = chord length **minus** hub socket engagement on each end (set `hub_inset` in OpenSCAD).
- Cup outer triangle should match the spherical face’s planar chord triangle at the cup lip radius (slightly inside OD if diffuser sits at OD).
- Working cup depth **10 mm**; tune after bleed prototype.
- Polar hubs (near ±Z) need a clear bore for the central column.
