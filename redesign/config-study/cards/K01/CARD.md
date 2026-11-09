# K01: small twin-boom quadplane 4+1 (class S, 4S)

Status: `PROPOSED`, concept sizing engineer, 2026-11-09. Mission: the REQUIREMENTS.md §3 default M-A (hover 2 min, cruise ≥ 5 / 10 min, 20 % reserve, no payload, 0.25 kg growth allowance). Numbers come from `sizing.py`, which writes `sizing.json`, and from `cost.csv`. Every mass, drag and efficiency figure is `ESTIMATE` unless a datasheet is named in `sizing.py`.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 390" width="640" height="390" font-family="sans-serif" font-size="10">
<rect width="640" height="390" fill="#fff"/>
<text x="10" y="14" font-weight="bold">TOP</text><text x="400" y="14" font-weight="bold">SIDE (nose left)</text><text x="10" y="268" font-weight="bold">FRONT</text>
<text x="400" y="380" fill="#555">Scale: 1 m = 180 px (all three views). Props shown at 11 in.</text>
<!-- TOP -->
<g stroke="#000" fill="none">
<rect x="26" y="90" width="288" height="45" fill="#dde8f5"/>
<line x1="170" y1="90" x2="170" y2="135" stroke-dasharray="3,2"/>
<rect x="113.75" y="43.2" width="4.5" height="180" fill="#444"/><rect x="221.75" y="43.2" width="4.5" height="180" fill="#444"/>
<rect x="159.2" y="36" width="21.6" height="111.6" rx="8" fill="#f2e3c6"/>
<circle cx="116" cy="45" r="25" stroke="#c00" stroke-dasharray="4,2"/><circle cx="224" cy="45" r="25" stroke="#c00" stroke-dasharray="4,2"/>
<circle cx="116" cy="165.6" r="25" stroke="#c00" stroke-dasharray="4,2"/><circle cx="224" cy="165.6" r="25" stroke="#c00" stroke-dasharray="4,2"/>
<rect x="116" y="198" width="108" height="25.2" fill="#e6f0d8"/>
<line x1="145" y1="150" x2="195" y2="150" stroke="#c00" stroke-width="2"/>
<line x1="26" y1="245" x2="314" y2="245"/><line x1="26" y1="240" x2="26" y2="250"/><line x1="314" y1="240" x2="314" y2="250"/>
</g>
<text x="150" y="258">span 1.60 m</text><text x="236" y="120">wing 0.80 m half, c 0.25 m</text>
<text x="230" y="40" fill="#c00">lift prop 11 in</text><text x="232" y="214">inverted-V tail</text><text x="182" y="160" fill="#c00">pusher</text>
<text x="40" y="215">boom 1.0 m CF 25 mm</text><text x="128" y="30">pod 0.62 m</text>
<!-- SIDE -->
<g stroke="#000" fill="none">
<rect x="416" y="114.6" width="111.6" height="21.6" rx="8" fill="#f2e3c6"/>
<rect x="470" y="116" width="45" height="6" fill="#dde8f5"/>
<line x1="423.2" y1="125.4" x2="603.2" y2="125.4" stroke-width="4" stroke="#444"/>
<rect x="421.5" y="116" width="7" height="8" fill="#888"/><rect x="542" y="116" width="7" height="8" fill="#888"/>
<line x1="400" y1="114" x2="450" y2="114" stroke="#c00" stroke-width="2"/><line x1="520.6" y1="114" x2="570.6" y2="114" stroke="#c00" stroke-width="2"/>
<line x1="425" y1="125.4" x2="425" y2="159.6"/><line x1="545.6" y1="125.4" x2="545.6" y2="159.6"/>
<line x1="530" y1="100.2" x2="530" y2="150.6" stroke="#c00" stroke-width="2"/>
<rect x="578" y="80.4" width="25.2" height="45" fill="#e6f0d8"/>
<line x1="390" y1="159.6" x2="630" y2="159.6" stroke="#999"/>
<line x1="416" y1="180" x2="603.2" y2="180"/><line x1="416" y1="175" x2="416" y2="185"/><line x1="603.2" y1="175" x2="603.2" y2="185"/>
</g>
<text x="480" y="194">length 1.04 m</text><text x="540" y="172" fill="#555">pusher tip 5 cm off ground</text>
<text x="400" y="75">tail apex +0.22 m</text><text x="432" y="152">0.18 m legs</text>
<!-- FRONT -->
<g stroke="#000" fill="none">
<rect x="26" y="327" width="288" height="5" fill="#dde8f5"/>
<rect x="159" y="324.6" width="22" height="21.6" rx="6" fill="#f2e3c6"/>
<circle cx="170" cy="335.4" r="25" stroke="#c00" stroke-dasharray="4,2"/>
<circle cx="116" cy="335.4" r="2.5" fill="#444"/><circle cx="224" cy="335.4" r="2.5" fill="#444"/>
<line x1="91" y1="326" x2="141" y2="326" stroke="#c00" stroke-width="2"/><line x1="199" y1="326" x2="249" y2="326" stroke="#c00" stroke-width="2"/>
<polyline points="116,335.4 170,290.4 224,335.4" stroke="#3a7d1f" stroke-width="2"/>
<line x1="116" y1="335.4" x2="116" y2="369.6"/><line x1="224" y1="335.4" x2="224" y2="369.6"/>
<line x1="10" y1="369.6" x2="330" y2="369.6" stroke="#999"/>
<line x1="330" y1="290.4" x2="330" y2="369.6"/>
</g>
<text x="334" y="334">0.44 m</text><text x="182" y="288">inverted-V 40°</text><text x="236" y="352">booms ±0.30 m</text>
</svg>

## Key numbers (baseline: 4 lift, 4S 6500, XPS wing)

| Item | Value | Source |
|---|---|---|
| MTOW (including the 0.25 kg growth allowance) | **3.22 kg** (structure 1.31, propulsion 0.64, servos 0.19, pack 0.56, avionics 0.17, other 0.10) | `sizing.py` mass build-up, `ESTIMATE` |
| Span / area / AR / chord | 1.60 m / 0.40 m² / 6.4 / 0.25 m | chosen |
| Wing loading / stall (CLmax 1.1 `ESTIMATE`) | 8.05 kg/m² / **10.8 m/s**; transition ≥ 14.1 m/s (1.3 Vs) | calc |
| Disk loading / hover per motor | 129 N/m² / 829 g at 52 % of max thrust | calc |
| Hover power / current | **523 W / 35 A** (SunnySky table); momentum check with FM 0.65 gives 490 W | X3108S table (budget-lift.md) |
| Hover T/W | **1.96** on the 14.8 V table, 1.83 with sag. Passes 1.6, misses the recommended 2.0 | table × 4 / MTOW |
| Cruise @ 16 m/s | CD0 0.054 (parked props 31 %), **L/D 7.2**, 152 W, 10 A | drag build-up, `ESTIMATE` |
| Endurance (20 % reserve) | **22 min cruise after 2 min hover**; hover-only 8.8 min; 18 min if parked-prop CdA is ×2 | calc |
| Peak transition current | 65 A (hover + full pusher). 1.25× = 82 A, above the AS150U's 70 A continuous rating; within its 140 A 1-min rating | calc, Amass sheet |
| Cost, everything incl. tax 10.25 % + $120 shipping | **$1,741.68, leaving $258 reserve** ($302 if the conditional RID module is not bought) | `cost.csv` |
| Packed | **One box, 1.2 × 0.5 × 0.4 m**, ≈ 7 kg; longest piece 1.0 m (boom) + a field case for charger and packs | `sizing.py` packing |

**Options (from `sizing.json`):**

| Option | Effect |
|---|---|
| K21 hexa | T/W 2.74, survives a motor out in hover, 19 min cruise, +$102 |
| 4S 5000 pack | T/W 2.05, 16 min cruise; the best cheap fix for T/W |
| K04 folding props | L/D 8.1, +2.6 min cruise for $104. Not worth it at this size: energy is not the constraint |
| K05 fairings | +1.3 min |
| U04 foam board | −50 g; must pass the bend test |
| B03 Mini Talon | Stall rises to 11.7 m/s; kit out of stock |

## Transport and assembly
- **Packing:** the two booms (motors and legs left on, props off), the pod and the two stacked wing halves sit side by side in one 1.2 × 0.5 × 0.4 m box. The tail panels fold flat at the apex hinge and go on top with the props and the 0.40 m joiner.
- **Field assembly, 2 people, ≈ 10 min `ESTIMATE`:**
  1. Slide the halves onto the joiner through the pod and fit one M5 nylon wing bolt per side.
  2. Clamp each boom into two printed wing saddles with 2 M4 thumbscrews into heat-set inserts.
  3. Slide the tail onto the boom-end stubs and fit an M3 pin on each side.
  4. Connect the plugs: per side, one XT60 and one 3-pin DShot lead at the wing root, plus one servo lead at the tail.
  5. Fit 5 props and install the pack.
- **Count:** 5 mechanical joints and 6 plugs. One person can carry the assembled aircraft.

## How it is built (Jacobs Hall + bought parts)
- **Wing:** hot-wired XPS cores from printed templates, a tape skin, a CF joiner socket and servo bays (≈ 22 h).
- **Pod:** XPS or foam-board shell with a printed nose, battery tray and pusher mount (≈ 12 h).
- **Booms:** stock 1 m CF tubes, no cutting, with printed PETG motor mounts, saddles, legs and tail clamps (≈ 40 h printer time + 10 h).
- **Tail:** foam board (≈ 6 h).
- **Electrical:** harness and ESCs (≈ 20 h).
- **Setup and test:** ArduPilot setup and bench tests (≈ 30 h).
- **Total:** ≈ 100–120 team-hours `ESTIMATE`. With 3–4 people that is 5–7 weeks to the first hover, which leaves 5–7 of the 12 weeks for flight test and one crash.
- **Crash repair:** a wing half is re-cut in about a day, and motor mounts are reprinted overnight.

## Controls
- **Firmware:** ArduPilot Plane QuadPlane, `Q_ENABLE 1`, `Q_FRAME_CLASS 1`, `Q_FRAME_TYPE 1` (X).
- **Outputs:** lift motors on functions 33–36 (DShot). Pusher on function 70. Inverted-V on functions 79/80 (V-tail mixing; reverse to suit the inverted geometry). Ailerons on function 4.
- **Transition:** speed-scheduled on the MS5525 airspeed sensor. `AIRSPEED_MIN` 14, `Q_ASSIST_SPEED` 11, `Q_TRANSITION_MS` at default. `Q_TRANS_FAIL` and failsafes set as in REQUIREMENTS D10.
- **Flight modes:** fly QHOVER/QLOITER first, then QLOITER → FBWA transitions.
- **Firmware target risk:** the CoreWing F405 Wing V2 has a Plane target in **beta 4.7.2 only** (budget-avionics.md). The fallback is a SpeedyBee F405 Wing on a stable release (`UNVERIFIED` price parity).

## Top 3 risks
1. **Hover margin and single-point failures.**
   - T/W is 1.96, or 1.83 with sag. Adding 0.3 kg drops it to 1.80.
   - Losing any lift motor or ESC in hover is a crash.
   - Mitigations:
     - Set the mass gate at 3.38 kg (+5 %).
     - Switch to the 4S 5000 pack.
     - Fit the K21 hexa if the reserve allows.
2. **Pusher and transition data are unproven.**
   - No maker thrust table exists for the X2814 on 11×5.5 (static thrust ≈ 1.4 kgf is `UNVERIFIED`).
   - CLmax 1.1 and the parked-prop drag are guesses. The energy margin is large, so stall speed and transition authority matter more than drag here.
   - Measure all three on the thrust stand and with a car-top test before the order freeze.
3. **Booms, joints and lead time.**
   - Hover loads go through printed saddles into a foam wing, so boom twist means motor tilt and lost yaw authority. Six plugs are made at every assembly.
   - The CF tubes ship from overseas and the FC is backordered.
   - The 82 A transition requirement is above the AS150U's continuous rating. Cap the pusher at 70 % throttle during transition.

## First prototype test
- **Test:** one lift station on the thrust stand (day 1). Then a tethered hover of the complete aircraft in QHOVER at 1 m.
- **Pass if:**
  - hover throttle is ≤ 55 %;
  - pack current is 35 A ± 15 %;
  - there is no boom twist visible on video;
  - vibration is within ArduPilot limits.
- **Next:** a stopped-prop and pusher car-top test at 16 m/s, before the first transition.
