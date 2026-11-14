# K01-LEAN: twin-boom quadplane 4+1, re-sized lean (tie-break against K09)

Status: `PROPOSED`, 2026-11-09. Written for the K09-vs-K01 tie-break (README §4.2–4.3). Numbers come from `sizing.py`
(run `python -I sizing.py`; it writes `sizing.json` and `cost.csv`). The method and coefficients are those of
`cards/K01/sizing.py`. The K01 and K09 skeptics' corrections are built into the **baseline**, not added afterwards.
The last section is this card's own skeptic pass with pessimistic numbers. Every mass, drag and efficiency figure is
`ESTIMATE` unless `sizing.py` names a datasheet.

**What changed from the K01 card, in one line each:**

- **Wing.** One-piece 1.20 × 0.27 m hot-wired XPS wing (K09 construction) instead of two 0.80 m halves on a joiner.
- **Spar.** One 22×20 CF spar runs 1.00 m and passes through both boom stations. The booms clamp to the spar, not to the foam (fixes REVIEW C3). It is "full-span" in the sense the skeptic asked for: only the last 0.10 m of each tip is foam alone, at ≈ 11 kPa under 3 g against ≈ 300 kPa for XPS. A 1.2 m tube would need a second SKU for no structural gain.
- **CF tubes.** One tube SKU, 22×20×1000, used for the spar, both booms and a spare (fixes C11).
- **Tail.** Foam-board H-tail: one elevator and two fixed fins. It ties the boom ends together and replaces the inverted-V.
- **Stability.** Static margin is set by construction: CG at 28.7 % MAC for a 15 % margin, 8.5 % pessimistic. The lift centroid sits on that CG (fixes C4).
- **Pusher.** The pusher is a sixth X3108S on an APC 10×6E. One motor SKU, one spare.
- **Avionics and battery.** SpeedyBee F405 Wing (C6). No Remote ID module (RFS is a FRIA). Two 4S 4000 packs.
- **Joints.** Three field joints instead of five.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 870 340" width="870" height="340" font-family="sans-serif" font-size="10">
  <!-- ALL THREE VIEWS AT ONE SCALE: 200 px = 1 m. Coordinates from sizing.json geometry. Props dashed. -->
  <rect width="870" height="340" fill="#fff"/>
  <text x="10" y="14" font-weight="bold">K01-LEAN 3-view, to scale (200 px = 1 m). Lift props 11 in, pusher 10 in (dashed). CG ● = lift centroid (28.7 % MAC), NP ○ (43.7 % MAC).</text>
  <!-- ================= TOP VIEW (nose up). x(m) -> y = 120 + 200x ; span y(m) -> x = 150 + 200y ================= -->
  <text x="110" y="34" font-weight="bold">TOP (nose up)</text>
  <g stroke="#000">
    <rect x="30" y="120" width="240" height="54" fill="#dde8f5"/>
    <rect x="34" y="162" width="52" height="12" fill="#9bc"/><rect x="214" y="162" width="52" height="12" fill="#9bc"/>
    <line x1="50" y1="133.5" x2="250" y2="133.5" stroke="#444" stroke-dasharray="6,3"/>
    <rect x="87.8" y="61" width="4.4" height="200" fill="#444"/><rect x="207.8" y="61" width="4.4" height="200" fill="#444"/>
    <rect x="140" y="80" width="20" height="100" rx="5" fill="#f2e3c6"/>
    <rect x="90" y="237.8" width="120" height="30" fill="#e6f0d8"/>
    <rect x="90" y="257.8" width="120" height="10" fill="#9bc"/>
    <rect x="86" y="237.8" width="8" height="30" fill="#7a5"/><rect x="206" y="237.8" width="8" height="30" fill="#7a5"/>
    <rect x="86" y="61" width="8" height="8" fill="#555"/><rect x="206" y="61" width="8" height="8" fill="#555"/>
    <rect x="86" y="202" width="8" height="8" fill="#555"/><rect x="206" y="202" width="8" height="8" fill="#555"/>
    <line x1="124.6" y1="183" x2="175.4" y2="183" stroke="#c00" stroke-width="2"/>
  </g>
  <g fill="none" stroke="#c00" stroke-dasharray="4,2">
    <circle cx="90" cy="65" r="27.9"/><circle cx="210" cy="65" r="27.9"/>
    <circle cx="90" cy="206" r="27.9"/><circle cx="210" cy="206" r="27.9"/>
  </g>
  <circle cx="150" cy="135.4" r="4" fill="#000"/><circle cx="150" cy="143.6" r="4" fill="none" stroke="#000"/>
  <g stroke="#000"><line x1="30" y1="300" x2="270" y2="300"/><line x1="30" y1="295" x2="30" y2="305"/><line x1="270" y1="295" x2="270" y2="305"/></g>
  <text x="112" y="314">span 1.20 m</text>
  <line x1="280" y1="120" x2="280" y2="174" stroke="#000"/><text x="283" y="150">c 0.27</text>
  <text x="96" y="232" font-size="9">H-stab 0.60 × 0.15 m</text>
  <text x="34" y="190" font-size="9">aileron</text>
  <text x="214" y="96" font-size="9">boom ±0.30</text>
  <text x="166" y="130" font-size="9">spar 1.00 m</text>
  <!-- ================= SIDE VIEW (nose left). x(m) -> X = 420 + 200x ; z(m) -> Y = 250 - 200z ================= -->
  <text x="430" y="34" font-weight="bold">SIDE (nose left)</text>
  <g stroke="#000">
    <path d="M420,247.8 Q432,239 452,238.6 Q478,239 474,244 L474,246 Q450,247 420,247.8 Z" fill="#dde8f5"/>
    <rect x="361" y="247.8" width="200" height="4.4" fill="#444"/>
    <rect x="380" y="225.4" width="100" height="16" rx="5" fill="#f2e3c6"/>
    <rect x="480" y="229" width="6" height="9" fill="#555"/>
    <line x1="487" y1="258.8" x2="487" y2="208" stroke="#c00" stroke-width="2"/>
    <rect x="361" y="240" width="8" height="8" fill="#555"/><rect x="502" y="240" width="8" height="8" fill="#555"/>
    <line x1="337" y1="238" x2="393" y2="238" stroke="#c00" stroke-width="2" stroke-dasharray="4,2"/>
    <line x1="478" y1="238" x2="534" y2="238" stroke="#c00" stroke-width="2" stroke-dasharray="4,2"/>
    <line x1="365" y1="252" x2="365" y2="278"/><line x1="506" y1="252" x2="506" y2="278"/>
    <rect x="537.8" y="245.8" width="30" height="3" fill="#e6f0d8"/>
    <rect x="537.8" y="217.8" width="30" height="28" fill="#cfe3b8"/>
    <line x1="330" y1="278" x2="600" y2="278" stroke="#999"/>
  </g>
  <circle cx="435.4" cy="244" r="3" fill="#000"/>
  <g stroke="#000"><line x1="361" y1="296" x2="567.8" y2="296"/><line x1="361" y1="291" x2="361" y2="301"/><line x1="567.8" y1="291" x2="567.8" y2="301"/></g>
  <text x="420" y="310">length 1.03 m (boom 1.00 + tail overhang)</text>
  <text x="380" y="220" font-size="9">pod 0.50 m on top of wing</text>
  <text x="490" y="205" font-size="9" fill="#c00">pusher 10×6E</text>
  <text x="540" y="212" font-size="9">fin 0.15</text>
  <text x="332" y="274" font-size="9">leg 0.13</text>
  <text x="470" y="274" font-size="9">pusher tip 9.7 cm off ground</text>
  <!-- ================= FRONT VIEW. y(m) -> X = 720 + 200y ; z(m) -> Y = 250 - 200z ================= -->
  <text x="690" y="34" font-weight="bold">FRONT</text>
  <g stroke="#000">
    <rect x="600" y="241.4" width="240" height="6.4" fill="#dde8f5"/>
    <rect x="710" y="225.4" width="20" height="16" rx="4" fill="#f2e3c6"/>
    <circle cx="660" cy="250" r="2.2" fill="#444"/><circle cx="780" cy="250" r="2.2" fill="#444"/>
    <rect x="656" y="240" width="8" height="8" fill="#555"/><rect x="776" y="240" width="8" height="8" fill="#555"/>
    <line x1="632.1" y1="238" x2="687.9" y2="238" stroke="#c00" stroke-width="2"/>
    <line x1="752.1" y1="238" x2="807.9" y2="238" stroke="#c00" stroke-width="2"/>
    <line x1="660" y1="247.8" x2="660" y2="217.8" stroke="#7a5" stroke-width="3"/>
    <line x1="780" y1="247.8" x2="780" y2="217.8" stroke="#7a5" stroke-width="3"/>
    <line x1="660" y1="248" x2="780" y2="248" stroke="#7a5" stroke-width="1.5"/>
    <line x1="660" y1="252" x2="660" y2="278"/><line x1="780" y1="252" x2="780" y2="278"/>
    <line x1="590" y1="278" x2="850" y2="278" stroke="#999"/>
  </g>
  <circle cx="720" cy="233.4" r="25.4" fill="none" stroke="#c00" stroke-dasharray="4,2"/>
  <g stroke="#000"><line x1="660" y1="296" x2="780" y2="296"/><line x1="660" y1="291" x2="660" y2="301"/><line x1="780" y1="291" x2="780" y2="301"/></g>
  <text x="688" y="310">booms 0.60 m</text>
  <text x="600" y="210" font-size="9">fins on boom ends; stab between</text>
  <text x="10" y="334" fill="#555">Lift discs clear the wing LE/TE by 2 cm in plan; pusher disc (±0.127 m) clears the lift discs (inner edge 0.16 m) by 3.3 cm. Tail LE 2 cm behind the rear discs.</text>
</svg>

## Key numbers (baseline 4S 4000 pack; pessimistic column = own-skeptic case, last section)

| Item | Baseline | Pessimistic | Source |
|---|---|---|---|
| **AUW (incl. 0.25 kg growth)** | **2.44 kg** | **2.64 kg** | `sizing.json` mass build-up; pess +0.19 kg (overrun, saddles, pack) |
| Span × chord, area, AR | 1.20 × 0.27 m, 0.324 m², 4.4 | same | chosen: one piece, 1.25 m box |
| Wing loading, stall (CLmax 1.1) | 7.5 kg/m², **10.5 m/s**; transition ≥ 13.6 m/s | 8.1 kg/m², 10.9 / 14.2 m/s | calc |
| Hover per motor, power, current | 648 g (41 % of max), **357 W, 24 A (6 C)** | 726 g, 417 W, 28 A (7 C) | X3108S table, DOWNLOAD 1.06 / 1.10; momentum check 340 W |
| **Hover T/W, full voltage** | **2.59** (2.44 net of download) | 2.40 (2.18 net) | 4 × 1580 g / AUW |
| **Hover T/W, low voltage** (end of usable pack) | **2.38** (2.24 net) at 3.5 V/cell, thrust ∝ V^1.5 | **2.02 (1.84 net)** at 3.4 V/cell, thrust ∝ V² | calc; gate is 1.6 |
| **Static margin** | **15 % MAC** (CG 28.7 %, NP 43.7 %) | **8.5 %** (NP 37.2 %) | Etkin/Raymer method as REVIEW C4; Vh 0.58, Vv 0.065 |
| Cruise 15 m/s: CD0, L/D, power | 0.068 (parked props 30 %), **L/D 5.6, 146 W, 9.9 A** | 0.092, L/D 4.7, 243 W | drag build-up |
| **Cruise endurance after 2 min hover** (20 % reserve) | **13.3 min** | **7.5 min** | 59 Wh pack; mission needs 5 min |
| Hover-only endurance | 8.0 min | 6.8 min | calc |
| 4S 5000 option | 2.56 kg, T/W low-V 2.27, 17.5 min | 2.75 kg, 1.94, 10.0 min | variant |
| Hover lean in wind (nose into wind / broadside) | 2.6° / 6.4° at 5 m/s; **6.5° / 16° at 8 m/s** | about the same | flat-plate method as K09; the wing is edge-on in hover |
| Pusher | X3108S + APC 10×6E, ≈ 1.0 kgf static `UNVERIFIED`, 2.3 × cruise drag, pitch speed 29 m/s | 1.8 × drag | thrust stand day 1 |
| Peak transition current | 52 A → connector ≥ 65 A (AS150U 70 A ok) | 56 A → 70 A, at the limit | hover + 28 A pusher |
| Spar check (3 g cruise / 2.5 × hover) | 28 / 29 MPa vs ≈ 300 MPa allowable `ESTIMATE`; bare foam tip beyond the spar end 11 kPa | | `sizing.json` `structure` |
| **Spend / reserve** | **$1,718.62 / $281.38** | ≈ $1,775 / ≈ $225 | `cost.csv`; pess below |
| **Reserve vs one crash** | $281 vs **$266** (K01 card) ✓, vs **$309** (study formula) ✗ by $28, vs **$224** (this aircraft's own bill) ✓ | $225: covers own bill only | `cost.csv` crash lines |
| **Team-hours to first hover** | **90–110 h** (100) | **130 h** (outer bound 150) | build list below; S12 |
| Packed | 1 box **1.25 × 0.52 × 0.37 m** external, ≈ 5 kg; 4 pieces; 3 joints + 5 plugs; ≈ 7 min, 1 person | | `packing()` |

## Mass build-up (kg, baseline)

| Group | kg | Group | kg |
|---|---|---|---|
| Wing core XPS (calc 0.68·c·t·b·30 kg/m³) | 0.214 | 4 lift stations (X3108S 81 g + ESC 6.6 g + prop 20 g) | 0.430 |
| Tape skin, both sides | 0.042 | Pusher station (same motor + 10×6E) | 0.108 |
| Spar 22×20 × 1.0 m | 0.102 | Wiring along booms, 2 boom connectors | 0.080 |
| 2 booms 22×20 × 1.0 m | 0.204 | Pack, Admiral 4S 4000 (386 g, Motion RC / K09 card) | 0.386 |
| Pod (foam board + printed nose/tray/pusher mount) | 0.100 | Avionics (FC, GPS, RX, airspeed, AS150U, harness) | 0.150 |
| Printed PETG (mounts, saddles, legs, tail sockets) | 0.190 | Glue, Velcro, ties | 0.070 |
| H-tail + fins (foam board, CF rod) | 0.039 | **Sum 2.194 + growth 0.250 = 2.444** | |
| Servos (2 × ES08MA II, 1 × ES3005HV) + linkages | 0.079 | | |

Mass removed relative to the corrected K01 (3.45 kg): pack −0.17 (4000, not 6500), booms −0.14 (22×20, not 25×22),
servos −0.11, wing −0.19 (one 1.2 m piece, no joiner, no 1 in XPS pod), pusher motor −0.03, tail and legs −0.06, RID
module removed, and the rest from a smaller aircraft overall.

## Geometry and why the static margin is right this time

The script places the parts in this order (`geometry()`):
1. It picks the CG for a 15 % margin at the wing-plus-tail neutral point. The wing slope is Helmbold, 4.06/rad at
   AR 4.4. The tail slope is 3.88/rad. Downwash is dε/dα = 2a/(πAR) = 0.58. Tail efficiency is η 0.9, and pod, booms
   and props take 2 % MAC (the Raymer pod-and-boom term alone gives 1.0 %).
2. It puts the **lift centroid on that CG**: front motor at x = −0.275 m and rear motor at x = +0.43 m from the LE.
   Each disc clears the wing by 2 cm.
3. It places the tail LE 2 cm behind the rear discs, which gives a tail arm of 0.56 m and Vh 0.58.
4. It repeats steps 1–3 until the result stops changing.

The 1.0 m stock boom ends 3.4 cm short of the stab TE. The printed tail socket sleeves over the boom end and carries
that overhang.

Pessimistic: dε/dα + 0.07 and 5 % MAC for unmodelled parts gives NP 37.2 % and **SM 8.5 %**. Before the order freeze,
check the margin in XFLR5/AVL (10 min). It is set by where the parts are placed, so if it comes out short, enlarge the
stab (0.17 m chord: +6 g).

## Transport and assembly

- **Pieces (4):**
  - Wing + pod + pusher motor, one piece, 1.20 × 0.47 × 0.11 m.
  - Two booms, each with 2 motors, 2 ESCs and 2 legs (1.0 × 0.06 × 0.20 m).
  - H-tail with fins (0.60 × 0.15 × 0.16 m).
  - A prop tray.
- **Box:** 1.25 × 0.52 × 0.37 m external, ≈ 5 kg loaded. It goes across a back seat or in a hatchback. A compact-sedan trunk is marginal (same as K09).
- **Field assembly, ≈ 7 min, 1 person (2 easier) `ESTIMATE`:**
  1. Slide each boom into its spar saddle (printed, bonded through the wing at ±0.30 m) and tighten 2 thumbscrews.
  2. Push the H-tail sockets onto both boom ends and fit 1 pin each.
  3. Plug in, per boom: one XT60 power plug and one 4-pin signal plug (2 × DShot; the elevator lead rides the right boom).
  4. Fit 5 props and the pack.
- **Count:** 3 mechanical joints and 5 plugs (K01 card: 5 joints and 6 plugs; K09: 0 joints and 1 plug).

## How it is built (Jacobs Hall + bought parts), team-hours to first hover

| Task | h |
|---|---|
| Hot-wire one-piece core (printed templates, existing K09-style bow) and cut ailerons | 8 |
| Spar slot, epoxy spar, tape skin, servo bays | 8 |
| Pod: foam-board box, printed nose, pack tray, pusher mount | 8 |
| Boom-spar saddles, motor mounts, legs: design + 1 print iteration | 12 |
| H-tail, fins, sockets | 5 |
| Wiring: 5 ESCs, 2 boom connectors, 3 servos, airspeed | 14 |
| ArduPilot QuadPlane setup, params, failsafes, SITL check | 16 |
| Thrust-stand tests (lift + pusher) and bench tests | 10 |
| Integration, CG, tethered first hover | 8 |
| Slack for a first-time team | 11 |
| **Total to first hover** | **100 (range 90–110; pessimistic 130)** |

After first hover, allow **+25–35 h** of flight-test sessions to a clean transition. That figure is lower than K09's
30–40 h because ArduPilot's QuadPlane transition is the documented default path. At 35 h/week (the build judge's rate)
the aircraft hovers in about 3 weeks, or 4 weeks pessimistic. That leaves 7–8 of the 12 weeks for transition, cruise and
one crash.

**Crash repair:**
- A new wing core is cut from the same sheet (≈ 5 cores per sheet) in a day.
- A broken boom swaps for the spare tube already bought.
- One spare motor covers all five stations.
- Motor mounts are reprinted overnight.

## Controls (ArduPilot Plane QuadPlane, documented default path)

- **Frame and outputs:**
  - `Q_ENABLE 1`, `Q_FRAME_CLASS 1`, `Q_FRAME_TYPE 1` (X).
  - Lift motors on functions 33–36 (DShot).
  - Pusher on throttle (70), ailerons on 4, elevator on 19.
  - No rudder: hover yaw comes from the motors, and the fins give cruise yaw damping.
- **Transition:**
  - Scheduled on airspeed (MS5525).
  - `AIRSPEED_MIN` 14, `Q_ASSIST_SPEED` 12, `Q_TRANS_FAIL` and failsafes per D10.
  - Cap the pusher at `THR_MAX` 85 % until thrust-stand current is known (keeps the peak under 65 A).
- **FC:** SpeedyBee F405 Wing. Confirm on firmware.ardupilot.org before ordering that a **stable** Plane build exists for
  `SpeedyBeeF405WING`, and that DShot works on all five motor outputs (timer groups). `UNVERIFIED`.
- **Order of flying:** QHOVER → QLOITER → transitions QLOITER ↔ FBWA.
- **Lift-motor failure in cruise:** the aircraft is wing-borne, so it is a glide with full control surfaces.
- **Lift-motor failure in hover:** a crash, as on every quad.

## Cost (from `cost.csv`; tax 10.25 %, shipping $120 `ESTIMATE`, FAA $5)

| Block | Pre-tax $ | Notes |
|---|---|---|
| Propulsion | 268.81 | 6 × X3108S (one SKU), 8 ESCs, 12 lift props, 3 pusher props, adapter rings |
| Servos | 60.46 | 3 × ES08MA II (WREKD $13.49, seen 2026-11-09), 1 × ES3005HV |
| Battery | 107.00 | Admiral 4S 4000 2-pack, Motion RC (cached $102.49–107.00) |
| Avionics + radio | 237.94 | SpeedyBee F405 Wing $47.99 (RDQ, search snippet), GPS, MS5525, Pocket + 18650 cells, RP3 |
| Airframe | 254.12 | XPS sheet, foam board, 4 × CF 22×20×1000, PETG, tape, glue |
| Hardware | 139.01 | shared $124.01 kit + pack re-termination |
| Ground floor (nothing owned) | 378.12 | charger, bags, ammo can, watt meter, IR, thrust stand, iron + PD, multimeter, solder, hot-wire + bow, smoke stopper, box |
| **Goods** | **1,445.46** | + tax 148.16 + shipping 120 + FAA 5 = **$1,718.62**, reserve **$281.38** |

- **Dropped:**
  - The Remote ID module (−$44 incl. tax; RFS is a FRIA).
  - The third pack.
  - The 25 mm tubes, the 1 in XPS sheet and three ES3005HV servos.
- **Crash, three ways:**
  - The study's class-S formula gives $308.93 incl. tax. It assumes a $100 airframe rebuild and a $67 FC.
  - The K01 card's figure is $266.
  - This aircraft's own bill is $224 (2 stations, props, FC, GPS, 1 tube, $15 of foam and prints).
- **Recovery levers (not taken):** borrowing the iron, multimeter and supply from Jacobs could add up to +$105
  (`UNVERIFIED`). Dropping the airspeed sensor would add $66 but weakens the documented transition path; not
  recommended.

## Risks (honest list, highest first)

1. **Single-saddle boom joint.** Each boom is held at one printed saddle on the spar. An unbalanced front/rear thrust
   at full throttle puts ≈ 13 N·m (2.5×) of pitch moment into the joint.
   - If the saddle creeps, motor tilt costs yaw authority (K01's own risk 3).
   - Mitigation: an 80 mm saddle plus a second bearing pad under the wing near the TE. The H-stab ties the boom ends
     together.
   - Test: load the joint with 2 kg on the front motor station before the first hover.
2. **Pusher thrust is unmeasured.** The X3108S on a 10×6E has no maker table. 1.0 kgf and 28 A are estimates.
   - If it is below ≈ 0.6 kgf, transition is slow and the hover motors carry it longer.
   - Fallback: X2814 900 KV on 11×5.5 (K01 card, +$30, +27 g).
3. **Low L/D, 5.6.** The parked 11 in props are 30 % of CD0, and the low-AR (4.4) wing pays induced drag. Endurance
   is still 2.6× the mission (1.5× pessimistic), but the cruise power estimate is the least certain number on this card.
4. **Hover single-point failure.** Any lift motor or ESC lost in hover is a crash. BLHeli_S ESCs have no continuous
   rating. This is the same for every quad in the study.
5. **Static margin rests on hand formulas.** 8.5 % pessimistic is only just above the 8 % floor. An XFLR5 check is
   required before ordering.
6. **Lead time and stock.**
   - CF tubes come from overseas (≈ 2 weeks, order first).
   - The SpeedyBee stock and the Admiral price come from search snippets and cached pages.
   - Fallback FC: CoreWing F405 Wing V2 (+$19).
7. **Wing in hover wind is not a risk here** (8 m/s gust → 16° broadside lean, against K09's 36°). This is the
   concept's main advantage, and the reason it exists in the tie-break.

## First prototype test

1. **Thrust stand, day 1:** one lift station and the pusher (10×6E).
   - Pass: lift ≥ 1.5 kgf at full throttle on a 3.6 V/cell pack; pusher ≥ 0.7 kgf at ≤ 30 A.
2. **Boom-joint load test.**
3. **Tethered QHOVER at 1 m.**
   - Pass: hover throttle ≤ 50 %, pack current 24 A ± 15 %, no boom creep on video, vibration within ArduPilot limits.
4. **Car-top test at 15 m/s** (pusher thrust, parked-prop drag), then the first transition.

---

## Own skeptic: where this card is optimistic, and the pessimistic numbers

| # | Optimistic assumption | Why it may be wrong | Pessimistic value used |
|---|---|---|---|
| S1 | Airframe 0.90 kg (wing + spar + booms + pod + prints + tail) | The Mini Talon quadplane conversions in the K01 review are 2.55–3.0 kg AUW. Hand-built parts come out heavy, and K09's skeptic added 0.10 kg overrun to a simpler airframe | **+0.10 overrun, +0.06 saddles/prints, +0.034 pack (420 g weighed)** → 2.64 kg |
| S2 | Printed parts 0.19 kg | Saddles that take 13 N·m will be thicker than 25 g | inside S1 |
| S3 | DOWNLOAD 1.06 | The rear disc has a boom under its full diameter and a leg in the wake | **1.10** |
| S4 | Low-voltage thrust ∝ V^1.5 at 3.5 V/cell | Near full throttle, thrust follows rpm², so V² is the upper bound, and a tired pack sags to 3.4 V | **V², 3.4 V/cell → T/W 2.02 (1.84 net of download)** |
| S5 | Cruise η_prop 0.60, η_motor 0.76, interference 1.15 | 10×6E behind a pod, a motor at 1/3 load, tape seams and leg roots | **0.50 / 0.70 / 1.35, parked-prop CdA × 1.5** → 243 W, **7.5 min** |
| S6 | Static margin 15 % | Hand NP formula, a low-AR wing whose downwash at the tail is uncertain, props ahead of the CG | **dε/dα + 0.07, 5 % MAC unmodelled → 8.5 %** |
| S7 | Pusher 1.0 kgf / 28 A | No table. The 10×6E might draw more and push less | 0.6 kgf (transition ≈ 2× longer); +$30 fallback motor |
| S8 | Shipping $120 for about 11 vendors | K01/K09 used $120 for fewer vendors | **$150** |
| S9 | SpeedyBee $47.99 in stock | Search snippet only. NewBeeDrone is sold out | **CoreWing $67.26 (+$19.27)** |
| S10 | Tax 10.25 % | A Berkeley +0.5 % measure was on the 2026-11-03 ballot | **+$7** |
| S11 | Hot-wire bow $15, box $55 | Plywood boxes and jigs grow | **+$20** |
| S12 | 100 team-hours | K01 card 100–120 became 150–180 under review (×1.5); K09's 70 became 70–85 (×1.2). This build is simpler than K01 (one wing piece, 3 joints, one tube SKU) but still has 5 stations, 3 servos and an airspeed sensor | **130 h** (≈ 4 weeks to first hover); outer bound **150 h** if this card is as optimistic as K01's was (×1.5) |
| S13 | Crash = $224 own bill | It assumes the spares are not already used and that only 2 stations die | study formula **$309** |

**Pessimistic summary.** AUW 2.64 kg. Hover T/W 2.40 at full voltage, **2.02 at low voltage** (1.84 net of download).
Static margin 8.5 %. Cruise **7.5 min** after 2 min hover (10 min on the 5000 pack). Spend ≈ $1,718.62 + $30
shipping + $21 FC + $7 tax + $22 jig/box ≈ **$1,799 → reserve ≈ $201**. That covers this aircraft's own $224 crash
only if the spares are untouched, and misses both the $266 and $309 crash figures. Build 130 h to first hover.

**For the tie-break, on the same corrected basis:**

| | K01-lean (base / pess) | K09 + elevons (README corrected) |
|---|---|---|
| AUW | 2.44 / 2.64 kg | 2.48 kg |
| Hover T/W, low voltage | 2.38 / 2.02 | ≈ 2.4 (2.6 table) |
| Hover lean, 8 m/s gust | 16° | 36° |
| Static margin | 15 / 8.5 % (tail) | reflex flying wing, not computed |
| Cruise after 2 min hover | 13.3 / 7.5 min | ≈ 19 / 12 min |
| Reserve | $281 / ≈ $201 | ≈ $335 |
| Team-hours to first hover | 100 / 130 | 70–85 |
| Field joints / plugs | 3 / 5 | 0 / 1 |
| Motor-out in cruise | glide | fatal |

Read plainly: the lean K01 closes most of the budget gap. The reserve moves from $103 to about $281, which is one crash
on the K01 figure but not on the study formula. The hover margin and the static margin are fixed. It keeps the
wind and failure advantages. It still costs about 15–45 more team-hours, three joints, and about $55–135 of reserve
compared with K09.
