# Glorb — Bill of Materials

Working baseline 2026-09-22 · Companion: [`SPEC.md`](SPEC.md)

Planning costs are rough retail bands (USD); confirm before buy.

---

## Electronics

### LED stock (locked product)

| | |
|--|--|
| Product | [12V 12mm Diffused Flat Digital RGB LED Pixels](https://www.ledlightinghut.com/12mm-flat-digital-led-pixels-12v.html) (LEDLightingHut) |
| SKU | LLH-1515-2811/1903-100 |
| Form | Silicone **flat** pixel · **1× RGB** (5050-class) + WS2811/UCS1903 · diffused dome |
| Size | **Ø12 mm** face · **23 mm deep** (0.45″ × 0.9″) |
| Mount | Push into **Ø12 mm** hole; four flanges grip material **≤1.5 mm / 0.06″** thick (optional screw ears on base) |
| Spacing (stock) | **100 mm / 4″** wire between pixels · **100 pcs / strand** |
| Electrical | **DC 12 V** · **0.3 W/pcs** (~**25 mA**) · **IP68** |
| Cable | **18 AWG**, all black, **3-wire** (12 V / Data / GND) — confirm pinout on arrival |
| Protocol | **WS2811 / UCS1903** (same timing; FastLED `WS2811`) — Data only, no Clock |
| Price | **$75.50** / 100-pc strand (qty breaks lower) |
| Option | Pigtail: JST (IP20) or IP65 waterproof (+$2.50) |

| Buy | Qty strands | Pixels | Planning $ |
|-----|-------------|--------|------------|
| Build + spare | **1** | 100 (80 + 20 spare) | ~$76–80 |

Stock **100 mm** pitch ≫ worst intra-patch hop (**66 mm**); short hops leave slack. Inter-patch jumpers still custom if patches are separate physical chains.

**Supersedes:** SuperLightingLED 35×35 mm WS2801 4-LED modules (too bright/power-hungry for this lamp).

### Rest of electronics

| Item | Spec | Qty | Notes | Planning $ |
|------|------|-----|-------|------------|
| Battery | **[NYI 12V 6000 mAh](https://www.amazon.com/NYI-6000mAh-Rechargeable-Lithium-Connector/dp/B0FDVGB87N/)** (ASIN B0FDVGB87N, BP017) · **~72×57×39 mm** · 320 g · **$32** | **1** | Out **12 V / 3 A max**; charge **12.6 V / 2 A** (included charger only); **DC5521**; BMS; ~**10 h** LEDs @ 30% white | ~$32 |
| Barrel jack | Panel **DC5521** (5.5×2.1) · **Ø12** hole typical | **1** | Base **back** (+Y), **20 mm** above floor — skirt into bay | ~$2 |
| Power switch | **[DaierTek KCD1-5-101](https://www.amazon.com/dp/B07S1MV462)** round rocker · snap-in **Ø20 mm** · SPST · **20 A @ 12 V DC** | **1** (of 5-pack) | BaseTop lid **front** (−Y); print hole **Ø20.2** + underside CB for ~2 mm land | ~$2 |
| Buck converter | **[MP1584EN mini 5 V](https://www.amazon.com/Regulator-Reducer-Converter-Aircraft-MP1584EN/dp/B0B779ZYN1/)** (ASIN B0B779ZYN1) · **17.5×12.3×4.3 mm** · 5-pack ~$9 | **1** (of 5) | In **5–28 V** → out **5 V** fixed; claim **1.8 A** (prefer ≤1.5 A); ESP32 OK | ~$2 |
| MCU | **ESP32-WROOM DevKit** (home stock) · keep-out **~55×30×15 mm** | **1** | Typical 30-pin / DevKitC class (~51–55 × ~28 mm PCB) | $0 |
| Level shifter | 74AHCT125 or similar 3.3→5 V | **1** | Data line | ~$2–5 |
| PSU (optional) | **12 V ≥ 3 A** wall | 0–1 | Bench only — **not** for charging this pack | ~$12–25 |
| JST pair | 3–4 pin (12 V/GND/Data) | **1** | North↔south hemi disconnect | ~$2 |
| JST pair | 3–4 pin (12 V/GND/Data) | **1** | North↔south hemi disconnect | ~$2 |
| CA glue | Thin/medium for PLA | 1 | Module + equator seams; clamp | ~$5 |
| Hookup wire | 18–20 AWG power; 22–26 signal | ~20 ft | Sleeve lead + patches | ~$8 |
| Capacitor | **1000 µF** 16 V+ across 12 V/GND at chain start | **1** | Inrush | ~$1 |
| Resistor | **330–470 Ω** on Data | **1** | Near first pixel | ~$0.10 |
| Button | Momentary, panel | **1** optional | Effect cycle | ~$1 |
| Heat shrink / connectors | Assortment | 1 kit | Strain relief / spares | ~$10 |

**Electronics subtotal (planning):** ~**$110–150** (incl. 1×100 LED strand)

---

## Fasteners / hardware

| Item | Spec | Qty | Planning $ |
|------|------|-----|------------|
| Screws | **M2 × 8–10 mm** (hub/cup) | ~200 | ~$8 |
| Screws | **M3 × 10–12 mm** (base/column) | ~20 | ~$3 |
| Thread inserts | M2/M3 heat-set (optional) | ~50 | ~$8 |
| Cable ties | Small | 1 pack | ~$3 |

---

## Filament (Ender 5)

| Role | Material | Color | Est. mass | Planning $ |
|------|----------|-------|-----------|------------|
| **Cups** | **PLA** | **Opaque white** (locked) | ~0.6–1.0 kg | ~$18–30 |
| Hubs, struts (frame) | PLA or PETG | Any (under paint) | ~0.25–0.4 kg | ~$8–15 |
| Frame finish | Acrylic / model enamel | **Hand-painted gold** | — | ~$8–20 |
| **Column + base** | **PLA** | **Gold** (locked) | base ~**52 mm** tall (2-piece) | ~$10–18 |
| Diffusers / faceplates | PLA or PETG | **Translucent / natural white** | ~0.15–0.25 kg | ~$8–15 |

Cups dominate filament use — buy **opaque white PLA** first (not “silk” / translucent). Verify a swatch is fully opaque at 2 mm. Gold PLA for column/base; paint frame after dry-fit (mask cup seats / wire paths).

---

## Printed parts (counts)

| Part | Qty | Source |
|------|-----|--------|
| Cup A | per map (`face_type=A`) | [`cad/cup.scad`](cad/cup.scad) |
| Cup B | per map (`face_type=B`) | same |
| Diffuser A / B | same counts as cups | [`cad/diffuser.scad`](cad/diffuser.scad) |
| Vertex hub | **42** (polar variants may differ) | [`cad/hub.scad`](cad/hub.scad) |
| Strut short | count from edge map | [`cad/strut.scad`](cad/strut.scad) |
| Strut long | count from edge map | same |
| Column | **1** | [`cad/column.scad`](cad/column.scad) |
| Base | **1** (+ optional lid) | [`cad/base.scad`](cad/base.scad) |

Exact A/B and short/long counts: [`mesh/edge_lengths.csv`](mesh/edge_lengths.csv) · [`mesh/facet_led_map.csv`](mesh/facet_led_map.csv).

---

## Tools (assume owned)

Ender 5 · slicer · soldering iron · multimeter · flush cutters · M2/M3 drivers · calipers.

---

## Combined planning

| Package | Planning $ |
|---------|------------|
| Electronics (incl. LED strand) | ~$110–150 |
| Fasteners / wire kit | ~$20–40 |
| Filament | ~$30–50 |
| **Build kit (no printer)** | **~$160–240** |

Excludes: failed prototypes, spare cups, fancy PSU enclosure paint.
