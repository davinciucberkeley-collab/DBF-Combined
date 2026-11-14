# K09 — Quad tailsitter, flat flying wing, motor-only (U03 = K09; options K11, U06)

Status: PROPOSED (concept sizing engineer, 2026-11-09). Numbers come from `sizing.py` → `sizing.json` (run with `python -I sizing.py`).
Prices are in `cost.csv`. The mission is the REQUIREMENTS §3 default, M-A. Method and coefficients match `cards/K01/sizing.py`:
same X3108S thrust table, Cf, form factor, interference, ESC efficiency and energy rule. Anything marked `ESTIMATE` is a guess.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 250" width="800" height="250" font-family="sans-serif" font-size="11">
  <!-- scale 200 px = 1 m; props dashed; all three views same scale -->
  <text x="10" y="16" font-weight="bold">3-view, to scale (200 px = 1 m). Cruise attitude. Props dashed (11 in).</text>
  <!-- FRONT VIEW (from nose) centre 160,130 -->
  <text x="110" y="40">FRONT (from nose)</text>
  <rect x="45" y="127" width="230" height="6" fill="#bbb" stroke="#000"/>
  <rect x="150" y="115" width="20" height="12" fill="#ddd" stroke="#000"/>
  <line x1="96" y1="92" x2="96" y2="168" stroke="#000" stroke-width="3"/>
  <line x1="224" y1="92" x2="224" y2="168" stroke="#000" stroke-width="3"/>
  <g fill="#555"><circle cx="96" cy="92" r="4"/><circle cx="224" cy="92" r="4"/><circle cx="96" cy="168" r="4"/><circle cx="224" cy="168" r="4"/></g>
  <g fill="none" stroke="#666" stroke-dasharray="3,3"><circle cx="96" cy="92" r="28"/><circle cx="224" cy="92" r="28"/><circle cx="96" cy="168" r="28"/><circle cx="224" cy="168" r="28"/></g>
  <line x1="45" y1="215" x2="275" y2="215" stroke="#000"/><text x="135" y="230">span 1.15 m</text>
  <line x1="96" y1="200" x2="224" y2="200" stroke="#000"/><text x="128" y="196">motors ±0.32 m</text>
  <line x1="285" y1="92" x2="285" y2="168" stroke="#000"/><text x="289" y="134">0.38 m</text>
  <!-- TOP VIEW centre 470; LE y=100, TE y=160 -->
  <text x="430" y="40">TOP (nose up)</text>
  <rect x="355" y="100" width="230" height="60" fill="#bbb" stroke="#000"/>
  <rect x="460" y="108" width="20" height="40" fill="#ddd" stroke="#000"/>
  <line x1="406" y1="80" x2="406" y2="160" stroke="#000" stroke-width="3"/>
  <line x1="534" y1="80" x2="534" y2="160" stroke="#000" stroke-width="3"/>
  <rect x="402" y="72" width="8" height="8" fill="#555"/><rect x="530" y="72" width="8" height="8" fill="#555"/>
  <line x1="378" y1="70" x2="434" y2="70" stroke="#666" stroke-dasharray="3,3" stroke-width="2"/>
  <line x1="506" y1="70" x2="562" y2="70" stroke="#666" stroke-dasharray="3,3" stroke-width="2"/>
  <line x1="595" y1="100" x2="595" y2="160" stroke="#000"/><text x="599" y="134">0.30 m</text>
  <text x="440" y="180">pod 0.20 × 0.10 m</text>
  <!-- SIDE VIEW: nose left; tube x=650, LE x=670, TE x=730, wing y=130 -->
  <text x="660" y="40">SIDE (nose left)</text>
  <rect x="650" y="92" width="80" height="76" fill="#eee" stroke="#000"/>
  <path d="M670,130 Q685,123 705,126 Q722,129 730,129 Q715,133 690,133 Q675,133 670,130 Z" fill="#bbb" stroke="#000"/>
  <line x1="650" y1="92" x2="650" y2="168" stroke="#000" stroke-width="4"/>
  <rect x="642" y="88" width="8" height="8" fill="#555"/><rect x="642" y="164" width="8" height="8" fill="#555"/>
  <line x1="640" y1="64" x2="640" y2="120" stroke="#666" stroke-dasharray="3,3" stroke-width="2"/>
  <line x1="640" y1="140" x2="640" y2="196" stroke="#666" stroke-dasharray="3,3" stroke-width="2"/>
  <g fill="#000"><circle cx="730" cy="92" r="3"/><circle cx="730" cy="168" r="3"/></g>
  <text x="736" y="95">foot</text><text x="736" y="171">foot</text>
  <line x1="650" y1="215" x2="730" y2="215" stroke="#000"/><text x="652" y="230">fin 0.40 m</text>
  <text x="655" y="245">hover: stands on 4 feet, nose up</text>
</svg>

**What it is.** A rectangular flying wing with a reflexed section (MH 45-type, 10 %) and no moving surfaces. Two foam-board
fins at ±0.32 m each carry a vertical 22 mm carbon tube along their leading edge, with one motor at each tube end. That puts four
motors in an X, two above and two below the wing. The aircraft stands on the fins' trailing-edge tips, takes off as a quad, and
pitches 90° nose-down onto the same four motors for cruise. **Mass is 2.38 kg** (0.25 kg growth included). **The whole aircraft
goes in one 1.2 × 0.5 × 0.4 m box as a single piece, with no structural joint.**

| Key number | Value | Basis |
|---|---|---|
| MTOW / empty without pack | **2.38 kg** / 1.45 kg | Mass build-up by group in `sizing.json`. Core mass is calculated from geometry; the rest is `ESTIMATE` |
| Span × chord, area, AR | 1.15 × 0.30 m, 0.345 m², 3.8 | Chosen so the aircraft fits the C3a box in one piece |
| Wing loading, stall | 6.9 kg/m², **11.1 m/s** (CLmax 0.9 `ESTIMATE`) | Transition at 1.3 Vs or above = 14.4 m/s. Cruise at 14.5 m/s |
| Hover: disk loading, power, current | 95 N/m², **335 W, 22.6 A** at 4S; 607 g per motor | Maker table (X3108S + APC 11x4.7, 14.8 V). Momentum cross-check: 309 W at FM 0.65. FM implied by the table: 0.60 |
| T/W (table / with sag) | **2.65 / 2.47** | 4 × 1580 g max. Clears D11's 2.0 |
| Cruise L/D, power | **6.0** (pessimistic 5.0), 140 W, 9.5 A | CD0 0.059. The fins, motor tubes and four running motors together drag about twice what the wing does. η_prop 0.55 (pessimistic 0.35), +5 % trim `ESTIMATE` |
| Pack, endurance | OVONIC 4S 6500, 96 Wh | **26.9 min cruise after 2 min hover** (14.5 pessimistic). Hover-only 13.8 min. 20 % reserve kept. The 4S 4000 fallback gives 17.0 / 9.1 min |
| Hover in wind (wing broadside) | Tilt **16° at 5 m/s, 37° at 8 m/s** | Exceeds the default Q_ANGLE_MAX of 30°, so the aircraft drifts in an 8 m/s gust. Same flat-plate method as configurations.md |
| Cost | **$1,528.51** total, tax and shipping included. Reserve $471 (of which $150 is the planned crash line) | `cost.csv`. Passes the G1 $1,850 cap |
| Options | K11 biplane 0.80 m: 1 box, gust tilt 30°, **L/D 5.0, cruise 22.6 min**. U06 fold: gust tilt 22°, +0.09 kg, +$60 `ESTIMATE` | Variants in `sizing.json` |

**Pack and assembly for transport.** The aircraft is one piece, 1.15 × 0.45 × 0.39 m with props off, in a foam-lined box of
about 5 kg total (`ESTIMATE`). The field steps are: fit 4 props (one nut each), put the pack in the pod and strap it, close the
AS150U loop, then run the arm check. That takes **5 min with 1 person** (`ESTIMATE`). There are no structural field joints, and
the only electrical disconnect is the pack. The second box holds the charger, ammo can, tools and spares.

**How it is built.** Hot-wire the wing core from 2 in XPS using printed MH 45 templates, then slot and epoxy the 22×20 CF
spar. Skin it with packing tape. Each fin is two layers of laser-cut foam board sandwiching the CF tube. Print in PETG: four
motor mounts, two tube-to-spar saddles, four crushable feet, and the pod tray. Solder four ESC leads into the pod, then do
ArduPilot setup on the bench. **About 70 h of hands-on work, roughly 3 weeks to first hover** for 3 to 4 students (`ESTIMATE`):
cores 6, spar/skin 6, fins 6, print design 8 (printing unattended), wiring 10, FC and parameters 12, bench and thrust tests 8,
pod 4, plus about 10 h of slack. A crashed wing can be re-cut in a day; one XPS sheet gives about six cores. Parts lead time is
short, all from US vendors, except the CF tubes, which take about 2 weeks.

**Controls.** ArduPilot Plane with `Q_ENABLE 1`, `Q_TAILSIT_ENABLE 2` (copter motors only, so Qassist is always forced),
`Q_FRAME_CLASS 1` and `Q_FRAME_TYPE 1` (X). `Q_TAILSIT_MOTMX` is ignored in this mode. Use `Q_OPTIONS` bit 18 (arm only in a
VTOL mode). Source: [ArduPilot tailsitter guide](https://ardupilot.org/plane/docs/guide-tailsitter.html), read 2026-11-09.
In cruise, yaw comes from left-right thrust, pitch from upper-lower thrust, and roll from motor torque only. Roll is therefore
the weak axis. Documented builds: [H-Wing](https://discuss.ardupilot.org/t/quad-x-motor-tailsitter-without-control-surfaces-h-wing/68833) and the Cygnet motor-only build (forum sources, `UNVERIFIED` logs).
Without control surfaces there is no airspeed-sensor dependence (optional, $59.99). Failsafes are set per D10.

**Top 3 risks.**
1. **Hover and landing in wind.** At 8 m/s the wing needs 37° of lean, which is past the 30° default. The aircraft drifts, and
   a fin landing in a gust tips over beyond 39°. RFS is on the bay shore. Mitigation: morning flights, a 5 m/s wind limit on the
   flight card, and the U06 fold or K11 planform as phase 2. This is the reason the concept may lose.
2. **Motor-only cruise authority.** With no surfaces, roll in cruise relies on differential motor torque alone. Cruise
   efficiency also depends on hover props running lightly loaded (η 0.35–0.55). That spread is the gap between the 27 min and
   14.5 min cruise figures. **A motor failure is fatal in both hover and cruise** (score-0 anchor in §5).
3. **Transition and back-transition tuning** (`Q_TAILSIT_*` angles and rates, attitude gain scheduling with airspeed) by a
   first-time team. Mitigation: SITL with these parameters (D15), then the foam-board twin described below.

**First prototype test.** Build a foam-board copy of the same airframe on the real motors, FC and pack: about $40 of material,
2 days. Run 1: tethered QHOVER over grass, hold position within 1 m in calm air and in a 5 m/s fan or breeze, and log the lean
angle against the 16° predicted. Run 2: QLOITER at 30 m and above, transition to FBWA at 15 m/s or faster, fly 2 laps,
back-transition. Pass means log current within ±15 % of 22.6 A hover and 9.5 A cruise. If the wind test fails, flight-test U06
or K11 before cutting the XPS wing.
