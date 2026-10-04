# Glorb CAD (OpenSCAD)

Parametric sources for Ender 5 STLs. Units **mm**. Shared numbers: [`params.scad`](params.scad).

| File | Part | Notes |
|------|------|-------|
| `hub.scad` | Vertex hub | Placeholder socket directions — finalize from `mesh/edges.csv` per vertex |
| `strut.scad` | Edge strut | Set `STRUT_TYPE` to `"short"` or `"long"` before export |
| `cup.scad` | Light cup | Set `FACE_TYPE` `"A"` / `"B"`; drive exact sides from CSV for production |
| `diffuser.scad` | Face diffuser | Matching triangle plate |
| `column.scad` | Wiring column | Side exits for power injection |
| `base.scad` | Base | ESP32 bay + barrel jack + column socket |

## Export

1. Open part in OpenSCAD.  
2. Set type parameters.  
3. Render (F6) → Export STL into `cad/stl/`.  
4. Slice per [`PRINT.md`](../PRINT.md).

## Next CAD hardening (not blocking docs)

- Generate per-vertex hub STLs from neighbor edge directions.  
- Generate per-`geo_id` cup STLs from `edge0/1/2` in `facet_led_map.csv`.  
- Equator split ring fasteners.
