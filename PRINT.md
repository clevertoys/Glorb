# Glorb — Printing (Ender 5)

Printer: **Creality Ender 5** · bed ~**220 × 220 × 300 mm**. All parts modular.

Companion: [`cad/`](cad/) · [`SPEC.md`](SPEC.md) · [`GEOMETRY.md`](GEOMETRY.md)

---

## Material

| Part | Filament | Color | Why |
|------|----------|-------|-----|
| Cups | **PLA** | **Opaque white** | Internal bounce fill; must stay opaque at wall thickness |
| Hubs, struts (frame) | PLA or PETG | Any (will be painted) | Structure |
| Frame exterior | — | **Hand-painted gold** | After dry-fit; mask LED seats / glue faces as needed |
| Column, base | **PLA** | **Gold** | Printed finish (locked) |
| Diffusers / faceplates | PLA or PETG | **White / natural translucent** | Even face glow |

Prototype cups in **opaque white** before committing to a full 80-count batch. Confirm no neighbor tint-through.

---

## Part counts

| Part | Qty | Source | Notes |
|------|-----|--------|-------|
| **Print_SubModule0..7** | **8** | Fusion `Glorb Cups Assembly` | Boolean-joined cups (+ sleeve quarter on south) |
| Faceplates / diffusers | **80** | per cup A/B | Separate thin prints |
| Column | **1** | Fusion `Column` | Gold PLA; stepped Ø22/Ø28 |
| Base | **1** | TBD | Gold PLA |

*(Legacy per-cup OpenSCAD counts superseded by 8 submodule prints.)*

---

## Submodule export (Fusion) — sleeve + column hole

### Who owns the sleeve?

The south-pole **SphereSleeve** sits on the **−Z** axis and spans all four longitude bins. It intersects:

| SubModule | Patch | Sleeve? |
|-----------|-------|---------|
| 0–3 | N-lon0..3 | **No** |
| **4** | S-lon0 | **Yes** → `SleeveQ0` |
| **5** | S-lon1 | **Yes** → `SleeveQ1` |
| **6** | S-lon2 | **Yes** → `SleeveQ2` |
| **7** | S-lon3 | **Yes** → `SleeveQ3` |

So **4 of 8** submodules get a sleeve quarter; the sleeve is **not** a ninth print.

### Column hole

Do **not** cut a separate hole through random cups. The sleeve already has **Ø22.4 mm** ID (slip fit on Ø22 column). After joining a sleeve quarter to its submodule solid, that bore **is** the column hole for the assembly. North modules need no column cut.

### Prep recipe (each of 8 modules)

1. **Join cups** in `SubModuleN`: Combine → Join all cup bodies (or `Create Components` → copy bodies into `Print_SubModuleN` with world transforms, then Join) → one solid.
2. **South only (N=4..7):** run [`scripts/fusion_split_sleeve_quarters.py`](scripts/fusion_split_sleeve_quarters.py) once to make `SleeveQ0..3`; Combine → Join the matching quarter onto `Print_SubModuleN`.
3. **Check** the Ø22.4 bore is open and coaxial with −Z; clean any cup material that intrudes into the bore (Combine → Cut with a Ø22.4 cylinder tool if needed).
4. **Export** `Print_SubModuleN` as mesh STL/3MF (mm), one file per module.
5. Print in **opaque white PLA**; column separate in **gold PLA**.

Glue faces between south modules should include the vertical sleeve split planes (same 90° lon cuts).

---

## Orientation & settings (starting point)

| Part | Bed orientation | Layer | Infill | Supports |
|------|-----------------|-------|--------|----------|
| Cup | **Floor down** (open face up) | 0.2 mm | 20% | No |
| Diffuser | Flat on bed | 0.16–0.2 mm | 100% | No |
| Strut | Lying on side **or** vertical | 0.2 mm | 30% | No if horizontal |
| Hub | Flat on a socket face | 0.2 mm | 30% | As needed |
| Column | Vertical | 0.2 mm | 20% | No |
| Base | Bottom on bed | 0.2 mm | 20% | No |

**Temps (typical):** PLA 200/60 · PETG 240/80 — use your known profiles.

**Clearances:** First strut-in-hub fit should be snug; sand or ±0.1 mm `STRUT_OD` tweak in `params.scad` if loose/tight.

---

## Bed packing (rough)

- Cups: ~6–10 per plate depending on size (~80–95 mm triangles).  
- Expect **~8–12 plates** of cups alone, plus hubs/struts/base.  
- Diffusers can nest densely on fewer plates.

---

## Prototype order (do not skip)

1. **1× cup + diffuser + LED** — opacity/bleed test against a second cup; check face hotspot with white walls.  
2. **1× hub + 1 short + 1 long strut** — socket fit.  
3. Small arc of 3–5 hubs (curvature check).  
4. Then batch.

If bleed: increase `CUP_DEPTH` in [`cad/params.scad`](cad/params.scad) before mass printing.
