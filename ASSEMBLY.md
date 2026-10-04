# Glorb — Assembly

Locked build sequence (hemisphere glue-up). Companion: [`SPEC.md`](SPEC.md) · [`PRINT.md`](PRINT.md)

Adhesive for PLA module seams: **CA (super glue)** + clamp while curing. Spot-test on scrap white PLA first.

---

## 0. Prep

- Print **8** submodule solids (opaque white PLA) + faceplates; **Column** + **Base** (gold PLA).  
- Flash ESP32; smoke-test a short WS2811 run.  
- Label modules `SubModule0..7`; keep [`mesh/led_wiring_by_patch.csv`](mesh/led_wiring_by_patch.csv) handy.

---

## 1. Glue southern hemisphere

1. Dry-fit `SubModule4..7` (sleeve quarters should form a continuous south sleeve).  
2. Apply CA on glue faces (incl. vertical sleeve splits); **clamp** until set.  
3. Confirm **Ø22.4** sleeve bore is clean and round; clear flash.

## 2. Glue northern hemisphere

1. Dry-fit `SubModule0..3`.  
2. CA + clamp as above (no sleeve).

*(Optional: hand-paint exterior gold on frame-facing surfaces later; cups stay white inside.)*

---

## 3. LEDs — south half

1. Mount **12 mm WS2811** pixels per south patch wiring maps.  
2. Dress leads inward; bring the **main harness out through the sleeve** (12 V / GND / Data).  
3. Fit faceplates after electrical check (or leave off until final test).

## 4. LEDs — north half

1. Same for north modules.  
2. Terminate the north harness in a **JST** (or similar) that mates to the south/column side so the two hemispheres can unplug.

---

## 5. Bench test (hemispheres separate)

1. Power at **low brightness**.  
2. Test south chain alone (lead via sleeve).  
3. Test north chain via JST to the same controller/harness.  
4. Fix addressing / bad pixels / shorts **before** equator glue.

---

## 6. Close sphere + mount base

1. When happy: CA the **equator** (north hemi ↔ south hemi); clamp.  
2. Slide sphere onto **Column** until sleeve flange seats on the Ø28 ridge (**no glue** — friction / gravity / optional set screw later).  
3. Column seats in **Base** (no glue preferred for service access).

---

## 7. Base electronics

| Rail | Role |
|------|------|
| **12 V** | LED string (direct) |
| **5 V** | ESP32 — via **buck** from 12 V, **or** USB, **or** battery pack (TBD) |

**Option A (locked battery):** **[NYI 12V 6000 mAh](https://www.amazon.com/NYI-6000mAh-Rechargeable-Lithium-Connector/dp/B0FDVGB87N/)** in base → LED 12 V bus (**≤3 A** pack limit). Charge only with **included 12.6 V** charger via base **DC5521** jack (or unplug pack). **Buck 12→5 V** → ESP32.  

**Option B:** battery (e.g. 3S Li-ion ~12 V for LEDs + buck to 5 V for ESP, or USB power bank for ESP only) — runtime/charge TBD; leave until A works.

Common **GND** everywhere. **1000 µF** on 12 V at entry; level-shift Data; series resistor on Data.

---

## 8. Bring-up

1. Low brightness first.  
2. Serial effect picker; confirm map.  
3. Raise brightness within PSU/battery budget ([`BOM.md`](BOM.md)).

---

## Service

- Sphere lifts off column (unglued).  
- Equator is permanent once glued — debug hemispheres **before** step 6.  
- JST at equator (or sleeve/column breakout) is the main harness disconnect.

---

## Safety

- Do not run full-white 80 px on a tiny PSU/USB port.  
- Vent base if PSU/buck enclosed.  
- CA: ventilate; avoid bonding skin to PLA.
