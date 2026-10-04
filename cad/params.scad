// Glorb — shared parameters (include from other files)
// Units: millimeters
// Design OD ~12 in → R = 152.4 mm to outer diffuser face

RADIUS_MM = 152.4;

// Strut chords at RADIUS_MM (from mesh/edge_lengths.csv)
STRUT_SHORT = 83.292;
STRUT_LONG  = 94.188;

// Frame (no hub nodes) — faceplate rabbet
FACEPLATE_T = 1.0;       // flush pocket depth
RIM = 2.0;               // outer rim outside faceplate
LEDGE = 1.5;             // support under faceplate
STRUT_DEPTH = 8.0;       // frame thickness inward

// Hub / strut interface (legacy OpenSCAD struts — superseded by Frame_Channels)
STRUT_OD = 6.0;
STRUT_ID = 3.2;
HUB_SOCKET_DEPTH = 6.0;
HUB_BALL = 14.0;

// Light cup (optional alternate architecture)
CUP_WALL = 1.8;
CUP_DEPTH = 10.0;
CUP_FLOOR = 1.6;
LED_BORE = 5.2;
LED_WIRE_SLOT = 2.5;

// Diffuser / faceplate
DIFFUSER_T = FACEPLATE_T;
DIFFUSER_LIP = 0.4;

// Column / base / sphere sleeve
COLUMN_OD_IN = 22.0;     // section inside sphere (above ridge)
COLUMN_OD_BASE = 28.0;   // wider below ridge (mount stop)
COLUMN_ID = 16.0;
COLUMN_INTO_SPHERE = 50.8;  // 2.00 in
COLUMN_BELOW_RIDGE = 100.0;
SLEEVE_ID = 22.4;        // slip on COLUMN_OD_IN
SLEEVE_OD = 32.0;
SLEEVE_LEN = 40.0;
SLEEVE_FLANGE_OD = 36.0;
SLEEVE_FLANGE_T = 3.0;
BASE_D = 170.0;              // top outer OD (skirt); pack+DevKit+buck+stays+lip
BASE_FLOOR_T = 2.0;          // min floor thickness
BASE_SHELL_T = 5.0;          // lid thickness (column socket sits on this)
BASE_CLEAR_H = 44.45;        // 1.75 in interior clearance (battery-safe)
BASE_WALL_T = 5.0;           // BaseTop skirt wall
BASE_LIP_T = 2.5;            // BaseTub short register wall
BASE_LIP_H = 10.0;           // lip height top skirt slides over
BASE_SLIP = 0.4;             // diametral clearance top-ID vs lip-OD
BASE_H = BASE_FLOOR_T + BASE_CLEAR_H + BASE_SHELL_T;  // 51.45 mm overall
BASE_ID = BASE_D - 2 * BASE_WALL_T;  // top skirt ID (~160 mm)
BASE_LIP_OD = BASE_ID - BASE_SLIP;
BASE_BAY_ID = BASE_LIP_OD - 2 * BASE_LIP_T;  // clear inside tub lip

// Bay envelopes (mm) — leave air around; confirm on arrival
BATT_XYZ = [72, 57, 39];           // NYI 12V 6000mAh (2.83x2.26x1.52 in)
BATT_URL = "https://www.amazon.com/dp/B0FDVGB87N";
BATT_OUT_A = 3.0;                  // max continuous output (A)
// Charge with included 12.6V/2A supply only (not a plain 12V adapter)
BUCK_XYZ = [17.5, 12.3, 4.3];      // MP1584EN fixed 5V mini (Amazon B0B779ZYN1)
BUCK_URL = "https://www.amazon.com/dp/B0B779ZYN1";
// Common ESP32-WROOM DevKit (30-pin DOIT/clone ~51.5x28; DevKitC ~55x28 w/ antenna)
// Keep-out includes USB overhang + header height
ESP32_XYZ = [55, 30, 15];
ESP32_NOTE = "ESP32-WROOM DevKit class (home stock)";
JACK_HOLE_D = 12.0;                // panel barrel jack (charger / 12V in)
JACK_CENTER_Z = BASE_FLOOR_T + 20; // above lip — skirt opens into bay
// Base orientation: −Y = front (power switch), +Y = back (DC jack)

// DaierTek KCD1-5-101 round rocker (Amazon B07S1MV462) — snap-in Ø20 mm
SW_HOLE_D = 20.2;                  // print clearance on 20 mm mounting hole
SW_CBORE_D = 24.0;                 // underside counterbore (snap land)
SW_PANEL_T = 2.0;                  // remaining lid thickness at switch
SW_POS = [0, -50];                 // mm on BaseTop lid — front (−Y)
SW_URL = "https://www.amazon.com/dp/B07S1MV462";

// legacy alias
COLUMN_OD = COLUMN_OD_IN;
COLUMN_LEN = COLUMN_INTO_SPHERE + COLUMN_BELOW_RIDGE;
