# B09: Buy the design files, print the airframe (Flightory Stallion VTOL, tilt-tri)

Status: PROPOSED (concept sizing engineer, 2026-11-09). Numbers come from `sizing.py` → `sizing.json` and `cost.csv`.
Mission: REQUIREMENTS.md §3 M-A default. Method and shared assumptions match `cards/K06` (the scratch-built tilt-tri),
so the two compare directly. `ESTIMATE` = guess, `UNVERIFIED` = not checked against a primary source.
The Eclipson E-VTOL tailsitter version is not sized: no file price was found, and its own build log reports yaw problems and crashes.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 370" width="880" font-family="sans-serif" font-size="11">
<rect width="880" height="370" fill="#fff"/>
<g stroke="#222" fill="none" stroke-width="1.2">
<!-- TOP VIEW, 0.3 px/mm, centreline x=221, nose y=30 -->
<polygon points="20,120 422,120 422,168 221,192 20,168" fill="#dde8f3"/>
<rect x="204.5" y="30" width="33" height="165" rx="14" fill="#f3f3f3"/>
<rect x="218.6" y="195" width="4.8" height="132" fill="#888"/>
<polygon points="221,291 161,311 161,327 221,327" fill="#dde8f3"/>
<polygon points="221,291 281,311 281,327 221,327" fill="#dde8f3"/>
<rect x="150.5" y="75" width="9" height="78" fill="#f3f3f3"/>
<rect x="282.5" y="75" width="9" height="78" fill="#f3f3f3"/>
<circle cx="155" cy="75" r="26.7" stroke-dasharray="4 3"/>
<circle cx="287" cy="75" r="26.7" stroke-dasharray="4 3"/>
<circle cx="221" cy="246" r="26.7" stroke-dasharray="4 3"/>
<line x1="221" y1="20" x2="221" y2="340" stroke="#aaa" stroke-dasharray="6 3" stroke-width="0.6"/>
<line x1="20" y1="350" x2="170" y2="350"/><line x1="20" y1="345" x2="20" y2="355"/><line x1="170" y1="345" x2="170" y2="355"/>
<!-- FRONT VIEW, centre x=661, ground y=150 -->
<rect x="460" y="99" width="402" height="5" fill="#dde8f3"/>
<rect x="644.5" y="82" width="33" height="39" rx="10" fill="#f3f3f3"/>
<line x1="661" y1="95" x2="613" y2="58"/><line x1="661" y1="95" x2="709" y2="58"/>
<rect x="591" y="84" width="8" height="15" fill="#f3f3f3"/><rect x="723" y="84" width="8" height="15" fill="#f3f3f3"/>
<line x1="568" y1="82" x2="622" y2="82" stroke-width="2"/><line x1="700" y1="82" x2="754" y2="82" stroke-width="2"/>
<line x1="634" y1="74" x2="688" y2="74" stroke-width="2" stroke="#666"/>
<line x1="652" y1="121" x2="646" y2="150"/><line x1="670" y1="121" x2="676" y2="150"/>
<line x1="450" y1="150" x2="872" y2="150" stroke="#aaa" stroke-width="0.6"/>
<!-- SIDE VIEW, nose x=470, ground y=330 -->
<rect x="470" y="272" width="165" height="39" rx="14" fill="#f3f3f3"/>
<rect x="635" y="283" width="132" height="5" fill="#888"/>
<polygon points="560,276 632,278 560,281" fill="#dde8f3"/>
<rect x="511" y="266" width="8" height="18" fill="#f3f3f3"/>
<line x1="488" y1="264" x2="542" y2="264" stroke-width="2"/>
<rect x="683" y="272" width="6" height="11" fill="#f3f3f3"/>
<line x1="659" y1="270" x2="713" y2="270" stroke-width="2"/>
<polygon points="737,283 767,283 767,243 757,243" fill="#dde8f3"/>
<line x1="545" y1="311" x2="540" y2="330"/><line x1="600" y1="311" x2="605" y2="330"/>
<line x1="460" y1="330" x2="790" y2="330" stroke="#aaa" stroke-width="0.6"/>
</g>
<g fill="#222">
<text x="20" y="16" font-weight="bold">TOP (hover; dashed = 7 in prop discs)</text>
<text x="22" y="365">500 mm (all views 0.3 px/mm)</text>
<text x="326" y="116">span 1340 mm</text>
<text x="300" y="72">tilt motor + servo</text>
<text x="252" y="250">fixed rear motor</text>
<text x="290" y="322">V-tail on 4 mm spars</text>
<text x="80" y="188">wing half, slides off 10 mm main spar</text>
<text x="240" y="40">LW-PLA fuselage</text>
<text x="460" y="30" font-weight="bold">FRONT (hover)</text>
<text x="460" y="230" font-weight="bold">SIDE (hover)</text>
<text x="470" y="350">length 990 mm; CG 60 mm aft of wing LE (Flightory)</text>
</g>
</svg>

## Key numbers (`sizing.json` baseline: Ovonic 4S 5000 LiPo)

| Quantity | Value | Basis |
|---|---|---|
| Span / length / wing area | 1.34 m / 0.99 m / 0.268 m² (AR 6.7) | span, length from Flightory; chords 0.24/0.16 m `ESTIMATE` |
| MTOW (incl. 10 % contingency, 0.25 kg growth) | **2.30 kg**; printed 800 g, carbon 123 g, propulsion 294 g, battery 448 g | Flightory AUW band 2.0–3.0 kg; part masses `ESTIMATE` |
| Wing loading / stall / transition ≥ 1.3 Vs | 8.6 kg/m² / 10.7 m/s / 13.9 m/s | CLmax 1.2 `ESTIMATE` |
| Hover power / current | 551 W / 37 A (worst motor 14 A); disk loading 303 N/m² | momentum theory, FM·η 0.50 calibrated from the 2100 g / 870 W listing `UNVERIFIED` |
| T/W total / worst motor with 10 % sag | 2.74 / **2.23** (gate 1.6) | rear motor carries 37 % with arms 0.21 m / 0.36 m `ESTIMATE` |
| Cruise | 14 m/s, L/D 10.1, 75 W, 5.0 A (103 W at 17 m/s) | CD0 0.040, e 0.8 as K06, `ESTIMATE` |
| Endurance (64 % of 74 Wh usable after reserve) | hover-only 5.2 min; **cruise 18.7 min after 2 min hover + 2 transitions** (4S 3300: 7.5 min) | meets 5 min threshold and 10 min objective |
| Transition current / disconnect | 49 A / needs ≥ 61 A → AS150U | D9 |
| Gust tilt (8 m/s side gust) | 12° | side area 0.10 m² `ESTIMATE` |
| **Cost incl. tax + shipping** | **$1,546.29; reserve $453.71** (a typical crash costs about $208) | `cost.csv` |
| Packed | one box 1.09 × 0.44 × 0.31 m, ≈ 3 kg with battery; longest piece 0.99 m | passes C3 |
| Print | ≈ 700 g LW-PLA + 100 g PETG ≈ **100 printer-h** (≈ 6 days on 2 Prusas at 8 h/day); reprinting one wing half takes ≈ 25 h | 10 g/h LW-PLA, 30 % scrap `ESTIMATE` |

**Propulsion deviation (honest):** Flightory's 2807 **1300 KV** is a 6S motor. On 4S it gives roughly 0.44 of its 6S thrust,
which leaves a worst-motor T/W under 1.6 (`ESTIMATE`). This card therefore uses the same-can **1700 KV** variant, which is listed at 2100 g on 4S.
The study's class-S station (X3108S + 11 in) is **not** used: the bought nacelles, mounts and prop clearances are drawn for 7 in props.
Fitting 11 in props means re-drawing the design you paid for. The 45 A ESCs sit below the motor's 52 A peak, so cap the throttle until a
thrust-stand run proves the current.

## Transport and assembly
One box. Fuselage, boom and V-tail ride on the box floor, the two wing halves (motors on, props off) lie flat above them,
and the main spar, battery and props go alongside. V-tail removability is `UNVERIFIED`; if the tail is glued, the box gets 0.1 m taller.
**At the field, 1 person, ≈ 10 min `ESTIMATE`:** slide the spar in, slide the wings on and screw them, then mate 2 multi-pin connectors per
wing (tilt motor 3-phase or ESC power + signal, tilt servo, aileron servo). Fit 3 props, fit the pack, run the arming checks. One hex key.

## How it is built
Processes: FDM only (Jacobs Prusas: LW-PLA for the skins and structure, PETG for spar roots, tilt and motor mounts, skids), cut carbon
tubes, heat-set inserts, CA/epoxy, soldering. No foam, no lay-up, no machining. **Person-hours ≈ 100 `ESTIMATE`:** 15 h
running prints and tuning the LW-PLA profile, 25 h cleanup and gluing, 10 h spars and hardware, 25 h wiring, 8 h tilt rig, 20 h ArduPilot
setup and bench tests. Calendar from first print to first hover ≈ 3–4 weeks. Design hours are near zero, and that is the point of this
concept. The weakness it brings is that a capstone needs its own analysis on top (structure test, sizing, tuning log).

## Controls
ArduPilot Plane QuadPlane with `Q_FRAME_CLASS 7` (Tri), `Q_TILT_ENABLE 1`, `Q_TILT_TYPE 2` (vectored yaw), `Q_TILT_MASK 3`,
`Q_TILT_RATE_UP 15` (Flightory manual: 6 s full tilt), airspeed-scheduled transition with `Q_ASSIST_SPEED`, and failsafes per D8–D10.
Flightory supplies an output map for the SpeedyBee F405 Wing and base parameters. A forum user says Flightory does not supply PIDs
(`UNVERIFIED`), so expect to tune from scratch: QAUTOTUNE in hover, then fixed-wing AUTOTUNE.

## Top 3 risks
1. **The LW-PLA structure.** A builder reported wing resonance and "PLA not rigid enough". LW-PLA softens at ≈ 55–60 °C, so a car
   trunk in the sun can warp it. It is brittle in a crash. Mitigation: reprinting is cheap (spare spool bought, about 25 h per wing half),
   keep the airframe out of hot cars, and run a wing load test in week 1.
2. **Tilt-tri control.** Losing the rear motor in hover is fatal. Two 16 g tilt servos hold each nacelle. No published PIDs, and the
   2.3 kg aircraft is wind-sensitive at bay-shore RFS. Same risk class as K06.
3. **Licence and printer throughput.** The files are "licensed for personal use only", so email Flightory before buying for a
   university capstone. Bring-your-own-filament and overnight-print rules at Jacobs Hall are `UNVERIFIED`. The 1700 KV motor
   and 7 in props are off the designer's list, so the supplied parameters may need re-tuning.

## First prototype test (week 1, < $70 of the BOM)
Print **one wing half with its nacelle** in LW-PLA and PETG and weigh it against the 190 g budget. Load the spar at the root to 2.5 g
(≈ 2.9 kg on one half) and record tip deflection and twist. Then mount a 2807 1700 KV with a 7×5 prop on the printed tilt mount, run it
on the thrust stand to full throttle, check current against the 45 A ESC, and sweep the tilt servo through 0–90° at hover thrust.
Pass: no permanent set, thrust ≥ 1.9 kg at < 45 A, servo holds its angle. Fail on stiffness or heat → move to K06 (same layout, foam wing).
