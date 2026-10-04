#include <Arduino.h>
#include <FastLED.h>
#include "face_map.h"

// --- hardware (12mm flat WS2811/UCS1903 @ 12V: Data only) ---
#define DATA_PIN 13
#define BUTTON_PIN 0          // boot button on many DevKits; change if using panel button
#define LED_TYPE WS2811
#define COLOR_ORDER RGB       // verify on first string; swap if colors wrong

CRGB faces[NUM_FACES];

uint8_t brightness = 48;      // keep low until PSU verified
uint8_t effect = 0;
uint32_t lastButtonMs = 0;

enum Effect : uint8_t {
  FX_SOLID = 0,
  FX_RAINBOW,
  FX_RIPPLE,
  FX_LAT_BANDS,
  FX_SPARKLE,
  FX_COUNT
};

void showFaces() {
  FastLED.show();
}

void fxSolid() {
  fill_solid(faces, NUM_FACES, CHSV(millis() / 40, 200, 255));
}

void fxRainbow() {
  uint8_t base = millis() / 20;
  for (uint8_t i = 0; i < NUM_FACES; i++) {
    faces[i] = CHSV(base + i * 3, 240, 255);
  }
}

void fxRipple() {
  // Expanding wave from north pole (led 0) using adjacency BFS-ish falloff by hop estimate
  static uint8_t dist[NUM_FACES];
  static bool built = false;
  if (!built) {
    for (uint8_t i = 0; i < NUM_FACES; i++) dist[i] = 255;
    dist[0] = 0;
    bool changed = true;
    while (changed) {
      changed = false;
      for (uint8_t i = 0; i < NUM_FACES; i++) {
        if (dist[i] == 255) continue;
        for (uint8_t k = 0; k < 3; k++) {
          int8_t n = FACE_NEIGHBORS[i][k];
          if (n < 0) continue;
          uint8_t nd = dist[i] + 1;
          if (nd < dist[n]) {
            dist[n] = nd;
            changed = true;
          }
        }
      }
    }
    built = true;
  }
  uint8_t t = (millis() / 80) % 24;
  for (uint8_t i = 0; i < NUM_FACES; i++) {
    uint8_t d = dist[i];
    uint8_t wave = (uint8_t)abs((int)d - (int)t);
    uint8_t v = wave < 3 ? (255 - wave * 80) : 0;
    faces[i] = CHSV(160 + d * 8, 220, v);
  }
}

void fxLatBands() {
  uint8_t t = millis() / 30;
  for (uint8_t i = 0; i < NUM_FACES; i++) {
    // map lat -90..90 → hue bands scrolling
    float lat = FACE_LAT_DEG[i];
    uint8_t hue = (uint8_t)(t + (lat + 90.0f) * 1.2f);
    faces[i] = CHSV(hue, 230, 255);
  }
}

void fxSparkle() {
  fadeToBlackBy(faces, NUM_FACES, 40);
  for (uint8_t n = 0; n < 3; n++) {
    faces[random8(NUM_FACES)] = CHSV(random8(), 200, 255);
  }
}

void runEffect() {
  switch (effect) {
    case FX_SOLID: fxSolid(); break;
    case FX_RAINBOW: fxRainbow(); break;
    case FX_RIPPLE: fxRipple(); break;
    case FX_LAT_BANDS: fxLatBands(); break;
    case FX_SPARKLE: fxSparkle(); break;
    default: fxSolid(); break;
  }
  FastLED.setBrightness(brightness);
  showFaces();
}

void nextEffect() {
  effect = (effect + 1) % FX_COUNT;
  Serial.printf("effect %u\n", effect);
}

void handleButton() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    uint32_t now = millis();
    if (now - lastButtonMs > 350) {
      lastButtonMs = now;
      nextEffect();
    }
  }
}

void handleSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'n' || c == 'N') nextEffect();
    if (c == '+') {
      brightness = qadd8(brightness, 16);
      Serial.printf("brightness %u\n", brightness);
    }
    if (c == '-') {
      brightness = qsub8(brightness, 16);
      Serial.printf("brightness %u\n", brightness);
    }
    if (c >= '0' && c <= '4') {
      effect = c - '0';
      Serial.printf("effect %u\n", effect);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(faces, NUM_FACES);
  FastLED.setBrightness(brightness);
  FastLED.clear(true);
  Serial.println("Glorb ready. Serial: n next, 0-4 effect, +/- brightness");
}

void loop() {
  handleButton();
  handleSerial();
  runEffect();
  delay(16);
}
