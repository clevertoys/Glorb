# Glorb firmware (ESP32 + FastLED)

PlatformIO project. Face count **80**; indices match [`../mesh/facet_led_map.csv`](../mesh/facet_led_map.csv).

## Regenerate face map header

After changing the mesh:

```bash
python scripts/generate_2v_mesh.py
python scripts/generate_face_map_h.py
```

Writes [`include/face_map.h`](include/face_map.h).

## Build / flash

```bash
cd firmware
pio run -t upload
pio device monitor
```

## Wiring (v1)

| Signal | ESP32 |
|--------|-------|
| LED data (via 330–470 Ω + level shift) | **GPIO 13** |
| Effect button (to GND) | **GPIO 0** (DevKit BOOT) or your panel pin |
| GND | Common with LED GND / PSU |

Set `DATA_PIN` / `BUTTON_PIN` in `src/main.cpp` if your board differs.

## Serial commands

| Key | Action |
|-----|--------|
| `n` | Next effect |
| `0`–`4` | Solid / Rainbow / Ripple / Lat bands / Sparkle |
| `+` / `-` | Brightness up / down |

Default brightness is **48/255** — raise only after power injection is confirmed.
