# K19 — Flying-wing (tailless) quadplane 4+1, scratch foam, class S (4S)

Status: **PROPOSED** (concept sizing engineer, 2026-11-09). Numbers come from `sizing.py` → `sizing.json` and
`cost.csv`; mission is REQUIREMENTS.md §3 default **M-A**. `ESTIMATE` = engineering guess, `UNVERIFIED` = unchecked claim.
Same parts classes and price sheet as `research/components-cost/cost_model.py` ("S quadplane 4+1"), so it compares fairly with K01.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 400" width="900" height="400" font-family="Arial,sans-serif" font-size="11">
<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect width="900" height="400" fill="#fff"/>
<text x="20" y="20" font-weight="bold">PLAN (top)</text>
<polygon points="30.0,193.3 230.0,100.0 430.0,193.3 430.0,243.3 230.0,205.0 30.0,243.3" fill="#e8eef5" stroke="#223" stroke-width="1.5"/>
<ellipse cx="230.0" cy="150.0" rx="20.0" ry="60.0" fill="none" stroke="#223"/>
<line x1="175.0" y1="125.6" x2="175.0" y2="215.5" stroke="#c33" stroke-dasharray="4,3"/>
<polygon points="155.0,201.8 40.0,226.3 40.0,241.3 155.0,219.3" fill="#9bc" stroke="#223"/>
<line x1="175.0" y1="47.2" x2="175.0" y2="262.2" stroke="#222" stroke-width="5.5"/>
<circle cx="175.0" cy="59.8" r="34.9" fill="none" stroke="#777" stroke-dasharray="3,2"/>
<circle cx="175.0" cy="59.8" r="4.6" fill="#444"/>
<circle cx="175.0" cy="249.8" r="34.9" fill="none" stroke="#777" stroke-dasharray="3,2"/>
<circle cx="175.0" cy="249.8" r="4.6" fill="#444"/>
<line x1="30.0" y1="193.3" x2="30.0" y2="243.3" stroke="#223" stroke-width="3"/>
<line x1="285.0" y1="125.6" x2="285.0" y2="215.5" stroke="#c33" stroke-dasharray="4,3"/>
<polygon points="305.0,201.8 420.0,226.3 420.0,241.3 305.0,219.3" fill="#9bc" stroke="#223"/>
<line x1="285.0" y1="47.2" x2="285.0" y2="262.2" stroke="#222" stroke-width="5.5"/>
<circle cx="285.0" cy="59.8" r="34.9" fill="none" stroke="#777" stroke-dasharray="3,2"/>
<circle cx="285.0" cy="59.8" r="4.6" fill="#444"/>
<circle cx="285.0" cy="249.8" r="34.9" fill="none" stroke="#777" stroke-dasharray="3,2"/>
<circle cx="285.0" cy="249.8" r="4.6" fill="#444"/>
<line x1="430.0" y1="193.3" x2="430.0" y2="243.3" stroke="#223" stroke-width="3"/>
<line x1="201.4" y1="217.5" x2="258.6" y2="217.5" stroke="#c60" stroke-width="2.5"/>
<circle cx="230.0" cy="154.8" r="5" fill="#fff" stroke="#000"/>
<text x="238.0" y="158.8" >CG</text>
<text x="208.0" y="92.5" >root LE</text>
<text x="292.5" y="240.0" fill="#c33">joint at y = &#177;0.22 m</text>
<text x="335.0" y="287.5" >elevon</text>
<text x="32.5" y="130.0" >11 in lift prop (4)</text>
<text x="205.0" y="232.5" fill="#c60">9 in pusher</text>
<text x="305.0" y="70.0" >22 mm CF boom (2)</text>
<text x="395.0" y="255.0" >winglet</text>
<line x1="30.0" y1="300.0" x2="430.0" y2="300.0" stroke="#000" marker-start="url(#a)" marker-end="url(#a)"/>
<text x="200.0" y="314.0" >span 1.60 m</text>
<text x="470" y="20" font-weight="bold">FRONT</text>
<rect x="490.0" y="92.0" width="400.0" height="6.0" fill="#e8eef5" stroke="#223"/>
<ellipse cx="690.0" cy="93.8" rx="20.0" ry="11.2" fill="#e8eef5" stroke="#223"/>
<line x1="490.0" y1="95.0" x2="490.0" y2="57.5" stroke="#223" stroke-width="3"/>
<circle cx="635.0" cy="106.2" r="2.8" fill="#222"/>
<rect x="630.4" y="90.0" width="9.2" height="12.5" fill="#444"/>
<line x1="600.1" y1="88.8" x2="669.9" y2="88.8" stroke="#777" stroke-width="2"/>
<line x1="635.0" y1="106.2" x2="635.0" y2="143.8" stroke="#555" stroke-width="3"/>
<line x1="890.0" y1="95.0" x2="890.0" y2="57.5" stroke="#223" stroke-width="3"/>
<circle cx="745.0" cy="106.2" r="2.8" fill="#222"/>
<rect x="740.4" y="90.0" width="9.2" height="12.5" fill="#444"/>
<line x1="710.1" y1="88.8" x2="779.9" y2="88.8" stroke="#777" stroke-width="2"/>
<line x1="745.0" y1="106.2" x2="745.0" y2="143.8" stroke="#555" stroke-width="3"/>
<circle cx="690.0" cy="95.0" r="28.6" fill="none" stroke="#c60" stroke-dasharray="3,2"/>
<line x1="477.5" y1="143.8" x2="902.5" y2="143.8" stroke="#6a4"/>
<text x="757.5" y="135.0" >printed foot 0.15 m</text>
<text x="492.5" y="52.5" >winglet 0.15 m</text>
<text x="660.0" y="155.0" fill="#c60">pusher-ground &#8776;80 mm</text>
<text x="470" y="200" font-weight="bold">SIDE (root section; winglet dashed)</text>
<polygon points="575.0,300.0 580.2,296.3 585.5,295.1 590.8,294.4 596.0,294.0 601.2,293.8 606.5,293.7 611.8,293.8 617.0,293.9 622.2,294.1 627.5,294.4 632.8,294.8 638.0,295.2 643.2,295.7 648.5,296.2 653.8,296.7 659.0,297.2 664.2,297.8 669.5,298.5 674.8,299.2 680.0,299.9 680.0,300.1 674.8,300.5 669.5,300.9 664.2,301.3 659.0,301.7 653.8,302.0 648.5,302.3 643.2,302.6 638.0,302.9 632.8,303.1 627.5,303.3 622.2,303.5 617.0,303.7 611.8,303.7 606.5,303.8 601.2,303.7 596.0,303.6 590.8,303.4 585.5,303.0 580.2,302.2 575.0,300.0" fill="#e8eef5" stroke="#223"/>
<polygon points="668.2,300.0 700.0,262.5 718.2,262.5 718.2,300.0" fill="none" stroke="#223" stroke-dasharray="4,3"/>
<line x1="522.2" y1="311.2" x2="737.2" y2="311.2" stroke="#222" stroke-width="5.5"/>
<rect x="530.1" y="295.0" width="9.2" height="12.5" fill="#444"/>
<line x1="499.8" y1="293.8" x2="569.7" y2="293.8" stroke="#777" stroke-width="2"/>
<rect x="720.1" y="295.0" width="9.2" height="12.5" fill="#444"/>
<line x1="689.8" y1="293.8" x2="759.7" y2="293.8" stroke="#777" stroke-width="2"/>
<line x1="527.5" y1="311.2" x2="527.5" y2="348.8" stroke="#555" stroke-width="3"/>
<line x1="732.5" y1="311.2" x2="732.5" y2="348.8" stroke="#555" stroke-width="3"/>
<line x1="692.5" y1="271.4" x2="692.5" y2="328.6" stroke="#c60" stroke-width="2.5"/>
<line x1="495.0" y1="348.8" x2="762.5" y2="348.8" stroke="#6a4"/>
<circle cx="629.8" cy="300.0" r="4" fill="#fff" stroke="#000"/>
<text x="500.0" y="282.5" >front lift motor</text>
<text x="680.0" y="255.0" >winglet</text>
<text x="575.0" y="362.5" >lift motors 0.76 m apart, CG between</text>
<line x1="20" y1="385" x2="145" y2="385" stroke="#000" stroke-width="3"/>
<text x="20" y="376">0.5 m  (all three views at the same scale, 250 px/m)</text>
</svg>


## Key numbers

| Item | Value | Basis |
|---|---|---|
| Span / area / AR | 1.60 m / 0.496 m² / 5.2; root 0.42 m, tip 0.20 m, LE sweep 25° | PROPOSED geometry |
| MTOW (mass gate +5 %) | **3.10 kg** (3.26 kg) | build-up: propulsion 679 g, structure 1,173 g, systems 293 g, pack 560 g, growth 250 g, +10 % contingency 147 g (`ESTIMATE` for all foam/printed parts) |
| Wing loading / stall | 61 N/m² (6.3 kg/m²) / **11.6 m/s** | CLmax 0.75 reflexed wing `ESTIMATE` |
| Transition ≥ 1.3 Vs / cruise | 15.1 m/s / 16 m/s (1.38 Vs) | REQUIREMENTS D11 |
| Hover T/W | **2.04** | 4 × 1,580 gf, SunnySky X3108S + APC 11x4.7 @14.8 V maker table |
| Hover | 799 g/motor, disk loading 128 N/m², **542 W, 39 A** | momentum (FM 0.62, η 0.80 × 0.95) 120 W/motor vs maker table 122 W/motor; larger used; +3 % download, +10 % control margin |
| Cruise L/D (stated) | **7.3** at 16 m/s (8.8 max at 11.7 m/s); clean wing alone would be ≈ 15.7 | CD0 0.042: wing 0.012 + extras CdA 0.0128 m² (4 parked 11 in units = 50 % of it, ≈ 34 % of CD0), e 0.80 — all `ESTIMATE` |
| Cruise power | **165 W, 11 A** | η prop 0.55 × motor 0.80 × ESC 0.95 |
| Transition peak | 864 W, ≈ 64 A (all-motors-full 145 A momentary) | lift at hover power + pusher 25 A `ESTIMATE` |
| Pack | Ovonic 4S 6500 (96 Wh, 560 g), 3 bought | study class-S pack |
| Endurance (20 % reserve, 2 min hover, 2 transitions) | **cruise 17.4 min** (threshold 5 ✔, objective 10 ✔); hover-only 8.5 min | `sizing.json` |
| Cost (tax + shipping) | **$1,655.60 → reserve $344.40** ($388 without the conditional RID module) | `cost.csv` |
| Packed | **one box 1.2 × 0.5 × 0.4 m**: centre section + booms 1.06 × 0.48 × 0.27 m, panels 0.58 × 0.36 × 0.06 m ×2 on top; longest piece 1.06 m; ≈ 6 kg box + LiPo ammo can | props parked fore-aft along the booms |

**Bought X8 shell (checked, rejected):** builder X8 quadplanes weigh ≈ 5.1 kg (configurations.md S33). On these class-S
stations T/W = 1.24 (fails D11 1.6). Moving to 6S class-M stations + the $290 US X8 kit (reach.dog listing, `UNVERIFIED`
stock) adds ≈ $640 incl. tax and shipping → ≈ **$2,300, over the hard $2,000**. The 2.12 m X8 also does not fit a 1.2 m box
without removing the outer wings. The scratch 1.6 m wing is the only K19 route inside the budget.

## Transport and assembly
- **Pieces:** centre section (pod, battery bay, spar stub, both booms with all 4 lift motors, pusher, FC, all ESCs and
  wiring) + 2 outer panels (elevon + servo each) + 2 plug-in winglets + pack. Every power and lift-motor wire stays on
  the centre section; the only wires crossing a joint are the 2 elevon servo leads (latched servo connector at each root).
- **Assembly, 1 person, ≈ 5–8 min `ESTIMATE`:** slide each panel onto the 22 mm carbon joiner, lock with one nylon M5
  thumb screw, plug servo lead (×2); push winglets into slots, magnet + one tape wrap (×2); battery in, strap, AS150U
  plug. 5 field joints, no tools. Disassembly is the reverse. Two people only to carry the assembled aircraft 100 m.

## How it is built (≈ 95 h hands-on `ESTIMATE`, ≈ 3–4 weeks for 3 students part-time, + ≈ 40 h unattended printing)
| Work | Process | Hours |
|---|---|---|
| Centre section + 2 outer panels, F-250 XPS | hot-wire with laser-cut ply root/tip templates | 12 |
| Spar channel, joiner sockets, boom saddles, ply hard-point plates, battery tray | knife/router, laser cut ply, epoxy | 10 |
| Booms (cut 22x20 CF), PETG motor mounts, feet, nose, hatch | bandsaw, Prusa FDM | 8 |
| Packing-tape skin, elevon cut and tape hinge, servo pockets, horns | hand | 10 |
| Winglets (1 in XPS + tape) with slot sockets | hand | 4 |
| Electrical: 5 ESCs, bus, AS150U, UBEC, servo leads, joint connectors, strain relief | solder bench | 18 |
| FC config, failsafes (D8–D10), motor order/direction, bench and thrust-stand checks | laptop + thrust stand | 20 |
| CG fixture, balance, weigh-in against the 3.26 kg gate | hand | 3 |
| Crash-repair kit: spare panel templates kept; a new outer panel ≈ 6 h | — | 10 |

## Controls approach
ArduPilot **Plane QuadPlane** (CoreWing F405 Wing V2 target is Plane beta 4.7.x per `docs/research/budget-avionics.md`):
`Q_ENABLE 1`, `Q_FRAME_CLASS 1` / `Q_FRAME_TYPE 1` (quad X), lift motors `SERVOn_FUNCTION 33–36` on DShot outputs,
pusher `70` (throttle), elevons `77/78` (ArduPilot mixes elevons itself; no tail servos). Airspeed sensor fitted:
`AIRSPEED_MIN 15`, `AIRSPEED_CRUISE 16`, `Q_ASSIST_SPEED 12`; `Q_WVANE_GAIN` on so the wing yaws into wind in hover;
lift motors tilted ≈ 3° for yaw authority `UNVERIFIED` (common quadplane practice). Transition is the same as K01: speed-scheduled, lift motors fade
once airspeed > `AIRSPEED_MIN`. PX4 "standard VTOL" with elevon mixing is the fallback, but the study's F405 board is
an ArduPilot path. Failsafes per REQUIREMENTS D10.

## Top 3 risks
1. **Tailless pitch trim through transition.** Static margin ≈ 8 % MAC means a CG window of only ≈ ±13 mm; the pusher
   thrust line, the parked props' drag and the battery position all move pitch trim, and the elevons are the only
   pitch control once lift motors fade. A wrong CG shows up exactly at transition. *Mitigation:* CG fixture marks on the
   pod, hand-glide test of the bare wing (below), `Q_ASSIST_SPEED`, first transitions at altitude ≥ 30 m.
2. **Hover yaw and gust handling.** Four 11 in props on a 3.1 kg wing with 0.05 m² of winglet side area give weak
   torque yaw; 8 m/s gusts at RFS can saturate it. *Mitigation:* motor tilt, `Q_WVANE_GAIN`, morning flights, 5 m/s
   flight-card limit. Any single lift-motor-out in hover is fatal (true of every 4+1).
3. **Boom hard-point in foam + parts lead time.** All hover and landing loads go through two printed saddles on one
   22 mm spar inside XPS; a hard landing can tear them out (repair = new centre section, ≈ 15 h). The 22 mm CF tubes ship from overseas
   (Oct–Nov delivery window seen) and the CoreWing was backordered: order both first. Also note D9: 64 A transition
   peak × 1.25 = 80 A exceeds the AS150U's 70 A continuous (fine for its 140 A/1 min rating; confirm with the team).

## First prototype test (week 3–4 of the build)
**Centre-section quad hover.** Before the outer panels exist, the centre section with booms *is* a quadcopter: tether it
and fly QHOVER/QLOITER at 2 m. Pass: stable hover, hover current within ±15 % of 39 A (as-built mass scaled), ESC and motor
temps < 70 °C after 3 min, motor-stop switch works. In parallel, **hand-glide the bare outer panels + centre (ballasted
to 3.1 kg, no motors)** over grass to set CG and elevon reflex. Only then the full aircraft: VTOL hover, then
`Q_ASSIST`-protected transitions at RFS.
