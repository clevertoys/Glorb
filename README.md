# Glorb

**2V geodesic sphere lamp** (~12 in OD, 80 RGB facets) — 3D printed on an Ender 5, ESP32 + FastLED.

| Doc | Contents |
|-----|----------|
| [`SPEC.md`](SPEC.md) | Locked design |
| [`BOM.md`](BOM.md) | Parts & rough cost |
| [`GEOMETRY.md`](GEOMETRY.md) | 2V mesh, strut lengths, LED map |
| [`PRINT.md`](PRINT.md) | Ender 5 print guide |
| [`ASSEMBLY.md`](ASSEMBLY.md) | Build order |
| [`cad/`](cad/) | OpenSCAD sources |
| [`firmware/`](firmware/) | ESP32 FastLED |
| [`mesh/`](mesh/) | Generated CSV maps |
| [`scripts/`](scripts/) | Mesh / header generators |

## Quick start

```bash
python scripts/generate_2v_mesh.py
python scripts/generate_face_map_h.py
```

Then print a prototype cup ([`PRINT.md`](PRINT.md)), flash firmware ([`firmware/README.md`](firmware/README.md)), assemble ([`ASSEMBLY.md`](ASSEMBLY.md)).
