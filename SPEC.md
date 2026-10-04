# Glorb — Project Spec

**2V geodesic sphere lamp** · Working baseline 2026-09-22 (methodology revised)

A ~**12 in** (305 mm) diameter Class I **2V** icosahedral geodesic sphere: **80** triangular **light cups**, each with interior baffles (no bleed) and a mount for one addressable RGB LED. **Design one cup first**, then Fusion-instance into the 2V pattern, boolean-union, and cut into Ender 5–printable subsections. Base + central column carry ESP32 / wiring.

---

## 1. Locked choices

| Item | Choice |
|------|--------|
| Geometry | Class I **2V icosahedral** full sphere → **80** facets, **42** vertices, **120** edges |
| Outer diameter | **~12 in** (305 mm) at outer face |
| Printer | **Ender 5** (~220 × 220 × 300 mm) |
| LEDs | **12 mm flat WS2811/UCS1903** pixels @ 12 V — [LEDLightingHut strand of 100](https://www.ledlightinghut.com/12mm-flat-digital-led-pixels-12v.html) (locked); push-fit **Ø12 mm** hole in cup |
| Controller | **ESP32** in base + **FastLED** (locked; Data only) |
| Isolation | **Per-cup baffles** + **opaque white PLA** walls — single color per facet; white interior reflects to even face glow |
| Structure method | **Single cup** → instance ×80 → boolean weld → **8 whole-cup patches** (see §1.1) |
| LED depth | **1.00 in** inward from facet face (along inward face normal) |
| LED chain | **Per-patch** daisy-chains (long jumpers OK between the 8 modules); see §1.2 |
| Column | Hollow central column, **2″ into sphere**; stepped OD with ridge stop; sphere sleeve for registration; base houses ESP32/PSU |
| Firmware v1 | USB serial + effect picker / button; Wi-Fi UI out of scope |

### 1.1 Print patches — **8 whole-cup subsections (locked)**

Do **not** cut through cups. Partition the **80** triangles into **8** disjoint edge-connected sets by **face centroid**:

| Rule | |
|------|--|
| Hemisphere | `lat ≥ 0` → North · `lat < 0` → South |
| Longitude bin | `lon` in (−180,180] → shift to [0,360); bin = `floor(lon/90) % 4` |
| Patch id | `0..3` = N-lon0..3 · `4..7` = S-lon0..3 |
| Seams | Shared edges only — **34** glue edges between patches |
| Counts | **8–11 cups** per patch; all **80** covered once |
| Map file | [`mesh/print_patches_8.csv`](mesh/print_patches_8.csv) |

Each printable part = boolean union of that patch’s cups only.

### 1.2 LED wiring — per-patch chains (locked)

| Assumption | Value |
|------------|-------|
| LED position | Face centroid, then **1.00 in (25.4 mm)** along **inward** face normal |
| Scope | One daisy-chain **per patch**; **long wires OK between** the 8 modules |
| Objective | Minimize **max** Euclidean hop **within** each patch |

**Result (exact minimax per patch):**

| Patch | Cups | Mode | Max hop | Jumps |
|-------|------|------|---------|-------|
| N-lon0 | 11 | 1 short jump | **66.189 mm (2.606 in)** | 1 |
| N-lon1 | 8 | neighbor-only | **41.517 mm (1.635 in)** | 0 |
| N-lon2 | 11 | 1 short jump | **66.189 mm (2.606 in)** | 1 |
| N-lon3 | 10 | neighbor-only | **41.517 mm (1.635 in)** | 0 |
| S-lon0 | 11 | 1 short jump | **66.189 mm (2.606 in)** | 1 |
| S-lon1 | 10 | neighbor-only | **41.517 mm (1.635 in)** | 0 |
| S-lon2 | 11 | 1 short jump | **66.189 mm (2.606 in)** | 1 |
| S-lon3 | 8 | neighbor-only | **41.517 mm (1.635 in)** | 0 |

| Aggregate | |
|-----------|--|
| **Worst patch max-hop** | **66.189 mm (2.606 in)** |
| Why jumps | 4 patches (the 11-cup ones) have a connected dual but **no** neighbor-only Ham path — one intra-patch non-adjacent hop is required |
| Sequences | [`mesh/led_wiring_by_patch.csv`](mesh/led_wiring_by_patch.csv) |
| Summary | [`mesh/led_wiring_by_patch_summary.txt`](mesh/led_wiring_by_patch_summary.txt) |
| Generator | [`scripts/generate_led_wiring_by_patch.py`](scripts/generate_led_wiring_by_patch.py) |

Reference (whole-sphere neighbor-only, not used for assembly): max **41.517 mm** — [`mesh/led_wiring_sequence.csv`](mesh/led_wiring_sequence.csv).

### Build volume vs full sphere / sections

| | Size | Fits Ender 5? |
|--|------|----------------|
| Full sphere OD | **305 mm** | **No** (~1.39× bed / +85 mm XY; +5 mm Z) |
| **8 whole-cup patches** | AABB ≈ **170–200 × 152–200 × 152 mm**, **8–11 faces** each | **Yes** — good margin |
| Same +10 mm wall budget | ~205 × 220 × 172 mm worst | **Yes** — tightest XY ~0.5–15 mm; re-check after boolean |
| Pole-to-pole 45° gores | some ~305 mm tall | **Avoid** |

**Single cup** (~83 / 94 mm edges) fits easily.

---

## 2. Architecture / method

```
1. Design ONE triangular cup (baffles + **Ø12 mm** LED hole) — dims from locked stock
2. Fusion: pattern/instance cups on 2V face frames
3. Boolean union → continuous shell
4. Group into **8 whole-cup patches** ([`mesh/print_patches_8.csv`](mesh/print_patches_8.csv); no mid-triangle cuts)
5. Wire each patch per [`mesh/led_wiring_by_patch.csv`](mesh/led_wiring_by_patch.csv) (worst intra-patch hop **2.606 in**; long jumpers between patches)
6. Base + column + ESP32 harness
```

Pins recover nothing geometric — the **printed frame** sets the sphere. LEDs only color the cups.

---

## 3. Geometry (summary)

Full detail: [`GEOMETRY.md`](GEOMETRY.md) · maps in [`mesh/`](mesh/).

| Quantity | Value |
|----------|-------|
| Frequency / class | **2V** Class I |
| Faces / vertices / edges | **80 / 42 / 120** |
| Design radius (OD/2) | **6.00 in** (152.4 mm) to outer face |
| Edge types | **2** strut lengths (chord factors × R) — see geometry tables |
| Face types | **2** triangle classes (cup A / cup B) |

Column axis = sphere **Z** (poles). Base sits below −Z pole.

---

## 4. Light cups (bleed isolation + fill)

| Feature | Spec |
|---------|------|
| Body | Opaque triangular cup — **opaque white PLA** (locked) |
| Why white | Max **internal reflectance** → bounce fill softens hotspot; still opaque enough to block neighbor bleed if walls are solid |
| Wall height | Cup depth per Fusion (working ~28 mm+; deepen if uniformity needs more throw) |
| Wall thickness | **≥2.0 mm** (raise if any tint shows through in QC) |
| Floor | **Ø12 mm** LED hole through **5 mm** baffle; **1.4 mm** snap lip + Ø16 counterbore |
| Diffuser / faceplate | Translucent **white PETG** or natural/white translucent PLA, seats in rabbet |
| Interior finish | As-printed white OK; avoid painting black inside |
| Exterior (cups) | White as-printed (hidden behind faceplates / interior) |
| Variants | **Cup A** and **Cup B** matching the two 2V face classes |

**QC:** Light one cup full white beside a dark neighbor cup; no visible tint through the shared wall. If bleed: thicken walls or add a second perimeter pass / higher infill on walls.

---

## 5. Frame, base, column

| Part | Spec |
|------|------|
| Hubs | 42 vertex pieces; strut sockets; cup registration; polar hubs clear the column |
| Struts | 120 edges in two lengths; friction or M2/M3 at hubs |
| Frame finish | Print any practical color; **hand-paint exterior gold** after assembly/dry-fit (locked look) |
| Split | **Equator split** (or polar cap) so cups and harness can be installed before closing |
| Column | Hollow stepped tube on Z; **gold PLA**; **Ø22 mm** into sphere (**2″**), **Ø28 mm** below; ridge = mount stop; **Ø16 mm** wire bore |
| Sphere sleeve | Interior **registration sleeve** at south pole (flange on ridge, slip fit on Ø22); joins to sphere / south patch |
| Base | **2-piece** gold PLA · **Ø170 × H≈51.5 mm** — tub = floor + short lip; top = skirt walls + lid + column socket (slides over lip) |
| Base bay | **[NYI pack](https://www.amazon.com/NYI-6000mAh-Rechargeable-Lithium-Connector/dp/B0FDVGB87N/)** + **[MP1584EN](https://www.amazon.com/Regulator-Reducer-Converter-Aircraft-MP1584EN/dp/B0B779ZYN1/)** + **ESP32-WROOM DevKit (~55×30×15 keep-out)** + panel **DC5521** jack |
| Column socket | On upper shell; accepts Ø28 column stub; serviceable (no glue to sphere) |

CAD: [`cad/`](cad/) OpenSCAD parametric sources.

---

## 6. Electronics

| Item | Spec |
|------|------|
| LED stock | **80** × **12 mm flat** WS2811/UCS1903 pixels (1× RGB each); **Ø12 × 23 mm deep**; IP68; see [`BOM.md`](BOM.md) |
| LED seat | **Ø12 mm** hole in **5 mm** baffle floor; **1.4 mm** flange snap-lip + Ø16 counterbore from interior |
| Protocol | **WS2811** timing — **Data only** (3-wire with 12 V / GND) |
| Addressing | FastLED indices **0..79** = face order in per-patch chains ([`mesh/led_wiring_by_patch.csv`](mesh/led_wiring_by_patch.csv)); map `geo_id` ↔ index in firmware |
| Logic | Level-shift ESP32 3.3 V → **5 V** on Data (12 V is power only) |
| Power | LEDs from **12 V** pack (**3 A max** → OK for ~2 A full white / 0.6 A @ 30%); charge pack with **included 12.6 V** supply only |
| ESP32 power | **[MP1584EN](https://www.amazon.com/Regulator-Reducer-Converter-Aircraft-MP1584EN/dp/B0B779ZYN1/)** buck pack **12 V → 5 V** (tiny; add input/output caps near module) |
| Hemi join | South 4 modules glued, north 4 glued; LEDs + test; then equator CA; **JST** between hemis |
| Sphere mount | Slip-fit on column ridge/sleeve (**no glue**); base serviceable |
| Ground | Common GND: 12 V, buck/ESP32, LED chain |
| Wire pitch | Stock **100 mm (4″)** between pixels — covers worst intra-patch hop (**66 mm**) |

Wiring detail: [`ASSEMBLY.md`](ASSEMBLY.md) · buy list: [`BOM.md`](BOM.md).

---

## 7. Firmware

| Item | Spec |
|------|------|
| Platform | PlatformIO · ESP32 · **FastLED** |
| Buffer | `CRGB faces[80]` face-indexed |
| Effects (v1) | Solid, rainbow wash, neighbor ripple, latitude bands, sparkle |
| Control | USB serial commands + optional GPIO button on base |
| Path | [`firmware/`](firmware/) |

Adjacency for ripple effects comes from [`mesh/facet_neighbors.csv`](mesh/facet_neighbors.csv).

---

## 8. Build sequence (high level)

1. Prototype one cup + diffuser + LED (bleed test).  
2. Print sample hub + both strut lengths; dry-fit curvature.  
3. Batch-print frame; dry-assemble without LEDs.  
4. Install LEDs + harness; bench-test map on ESP32.  
5. Fit cups, close equator, mount base, run effects.

Detail: [`PRINT.md`](PRINT.md) · [`ASSEMBLY.md`](ASSEMBLY.md).

---

## 9. Decision log

| Date | Decision |
|------|----------|
| 2026-09-22 | Project start — 2V / ~12 in / Ender 5 |
| 2026-09-22 | ESP32 + FastLED locked (no WLED in v1) |
| 2026-09-22 | Methodology → **single triangular cup** first (baffles + LED mount); instance + boolean + cut subsections |
| 2026-09-22 | Full sphere **does not fit** Ender 5: OD 305 vs bed 220 (~1.39× / +85 mm); Z 305 vs 300 |
| 2026-09-22 | Print split **8 whole-cup patches**: N/S × 4×90° by centroid; 34 seams; map `print_patches_8.csv` |
| 2026-09-22 | LED chain: 1″ inward; neighbor-only whole-sphere minimax **41.517 mm (1.635 in)** — optimal |
| 2026-09-22 | Per-patch chains (long inter-module OK): worst max-hop **66.189 mm (2.606 in)**; 4×11-cup patches need 1 jump each |
| 2026-09-22 | LED stock locked: SuperLightingLED **12V WS2801** modules (35×35×5 mm, 0.96 W, 20/string); FastLED Data+Clock; **12 V** rail |
| 2026-09-22 | LED stock **replaced**: LEDLightingHut **12 mm flat WS2811/UCS1903** @ 12 V (0.3 W, Ø12×23 mm, 100 mm pitch, strand of 100); cup = **Ø12 mm** push-fit hole |
| 2026-09-22 | Cups: **opaque white PLA** (internal reflectance for even face glow; opaque walls still isolate facets) |
| 2026-09-22 | Finish: frame **hand-painted gold**; column + base **gold PLA** |
| 2026-09-22 | Column: stepped **Ø22 / Ø28** (ridge stop) + **SphereSleeve** for vertical registration |
| 2026-09-22 | Interior harness: LED bodies + leads will be busy but **manageable** (spot-checked with LEDProxy) — no redesign for crowding |
| 2026-09-22 | Sleeve intersects **4 south SubModules (4–7)**; split into lon quarters for print; column hole = sleeve Ø22.4 bore |
| 2026-09-22 | Assembly: glue S/N hemispheres → LEDs + sleeve lead + **JST** → test open → glue equator → slip-on column; base **12 V + 5 V buck** (battery optional) |
| 2026-09-22 | Base: 2-piece; floor ≥2 mm + **1.75″** clear + 5 mm shell → **H ≈ 51.5 mm**; **Ø140** bay (pack + DevKit + buck + jack) |
| 2026-09-22 | Base redo: **Ø170**; tub = floor + short lip; **top carries skirt walls** (slides over lip); stays inside bay |
| 2026-09-22 | Power switch: **DaierTek KCD1-5-101** (B07S1MV462) on BaseTop lid; mount **Ø20.2** + CB → **2 mm** snap land |
| 2026-09-22 | Battery locked: **NYI 12V 6000 mAh** (B0FDVGB87N) — DC5521, **3 A max**, charge **12.6 V** only; ~10 h @ 30% white |
| 2026-09-22 | Buck locked: **MP1584EN 5 V** mini (B0B779ZYN1) — **17.5×12.3×4.3 mm**, 5–28 V in, ≤1.5 A practical |
| 2026-09-22 | ESP32: **WROOM DevKit** class — keep-out **~55×30×15 mm** (typical ~51–55×28 PCB) |

---

## 10. Open items

1. Exact filament brand for **opaque white** cups (confirm 2 mm wall fully blocks tint) and diffuser translucency.  
2. Final cup depth after hotspot / bounce prototype.  
3. Confirm panel jack is **DC5521** (5.5×2.1) for the NYI 12.6 V charger.  
4. Optional foam/weight in base for tip stability.  
5. Equator JST pinout / strain relief detail.  
6. Add local caps on MP1584EN (in/out) if ESP32 browns out on Wi‑Fi spikes.
