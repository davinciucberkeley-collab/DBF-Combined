# QP-4 as-drawn aircraft: CAD pack move + SITL re-run, concept A (A5 / F4 / B3, 2026-11-15)

Executes BOARD QP-3 s7.2 #2 and the three coordinator changes made during the work: D-187 elevon mass balance (FLUTTER.md), EMAX ES3054HV servo (SERVO.md), FC hard-mounted on the spar centre (FOLDIN s1). Files edited only in `redesign/qp/A/` (`cad/a_model.py`, `cad/a_assembly_plan.py`, `sitl/a_plant.py`, `sitl/a_aero.py`, `sitl/run_fwd.py`, `sitl/fwd_sum.py`, `sitl/fwd_checks.py`, new `sitl/cad_mass.py` + `cad_mass.json`, `A.param`). No git. Labels: `CALC` computed here, `EST` estimate, `SITL` this machine, `V`/`SPEC` vendor, `-` unknown. SITL = ArduPlane 4.7.3-beta1 JSON backend, 4 instances max, logs in `sitl/runs/Z4_*` (git-ignored), job lists `sitl/jobs_z4.txt`, `jobs_z4b.txt`.

## Verdict

**CAD gates pass (check, collision at +-20 deg, 25-step assembly). G6: CG 23.0 mm PASS; predicted mass 1,433 g (CAD method) / 1,440 g (script method) is at the 1.44 kg line, PASS by 0.3-7 g; structure 473 g FAILS (494 g) because of the D-187 balance, and that is a board call.**
**G5 (SITL, as drawn): transitions, back-transitions, landings, cruise trim and the 150 m fence leg are clean; two lines are not met: roll rate peaks at 89.3-89.8 deg/s against 90 (marginal), and weathervane in 1 m/s turbulence swings 11-24 deg against 15 (fails in 5 of 7 runs, 4 of 4 at the A.param gain).**

## 1. CAD (`redesign/qp/A/cad/`)

### 1.1 What changed

| Item | Change |
|---|---|
| Pack | centre x -20 -> **-10 mm** (cells x -27.5 to +7.5 mm); tray plate now x -45 to +21.5 mm, end walls long enough for +-10 mm trim; **trim slots**: 4 slots 3.4 x 23.4 mm under the lip bolts (lips re-bolt at the trim station); **core tray slot** (open above, x -10 to +22.5 mm, y +-55.5 mm, floor z +5.5 mm) because the pack zone is now over the LE foam. Tray lowered from above as a new build step B3 (it can no longer dock with the cage from below through the foam). Tray 4.0 -> 5.3 g (area-scaled, `EST`) |
| FC | hard-mounted on foam tape **at x 45-75 mm, centre 60 mm = spar axis**. ESC moved aft (x 82-117), RX moved to y -52.5..-40.5 / x 102-122, GPS and airspeed boards forward (x 45-70 / 45-60). Pack lead re-routed round the FC (y -26.5 mm). All 11 wires re-laid, ends on pads |
| Elevons | y 0.04-0.34, +-20 deg (already in CAD; confirmed by the collision sweep at +-20 deg) |
| D-187 balance | per elevon: horn arm 6 x 1.2 mm + lead block 16 x 2.4 x 24.6 mm = 10.7 g lead + 0.6 g horn = **11.3 g**, centre **30 mm ahead of the hinge** at y 0.305, bonded to the elevon nose (0.4 mm epoxy gap), moves with the elevon. Core pocket cut as the hull of the horn and lead over -20..+20 deg plus the 25 mm install path |
| Servo | EMAX ES3054HV 28.4 x 13.0 x 26.7 mm (SERVO.md: servodatabase.com / getfpv, 2026-11-15; RMRC page gives no drawing) 20.5 g each; case x 127.0-155.4, spline kept at x 140.5; pocket y +-22.5 mm; arm top at z 13.7 mm vs skin 14.1 mm (0.4 mm), pushrod z 12.7 mm from the arm end. Part renamed |
| Iteration-2 structure | masses and sizes already in the CAD (191 / 112 + feet 10 / 122 / 37 g) |

### 1.2 Gates (all re-run on the final geometry)

| Gate | Result |
|---|---|
| `build_a.py` (CAD check) | PASS, 10 modules, 0 errors, 0 warnings |
| `collide_a.py` (A's fixed checker `a_collide_blender.py`, 70 parts, 131 bodies, tolerance 0.05 mm) | **PASS**: static 0, elevons at -20 deg 0, +20 deg 0 (balance horns and lead move with the elevons and clear the core pocket), wire ends on terminations 0 missing, wire folds 0. Two fixes on the way: a 0.26 mm arm-root overlap (0.4 mm gap), a 1.0 mm pushrod-in-arm overlap (rod starts at the arm end) |
| `a_assembly.py` | **PASS, 25 of 25 steps** (was 24: the tray is now its own step B3, lowered from above; C2 carries the elevons with their balance horns; the install path is inside the pocket), 70 of 70 parts, no unsupported part, no wire laid before its ends |

### 1.3 Mass and CG (`sitl/cad_mass.py`, CAD centroids, basic mass, no growth)

| Group | g | x of group CG, mm aft of the LE |
|---|---|---|
| Wing incl. 2 balance horns (22.6 g) | 213.7 | 98.2 |
| Fins / feet | 111.8 / 10.0 | 249.6 / 304.9 |
| Cage incl. tray 5.3 g | 121.8 | -57.1 |
| Motors + props + ESC | 324.2 | -90.0 |
| Pack | 270.0 | -10.0 |
| Avionics / harness lump | 54.5 / 55.5 | 58.6 / 31.0 |
| Servos + linkage (2 x 20.5 + 6) | 47.0 | 145.6 |
| Hardware lump | 37.0 | 101.0 |
| **Total basic** | **1,245.5** | **22.96** (y +1.9, z +6.7) |

Trim: +-10 mm of pack = +-2.17 mm of CG, **20.8-25.1 mm**, inside the 20-26 mm band at both ends. SM with NP 40.7 mm (`EST`, CAD.md): 7.2 % (SM 8.1 % at 20.8, 6.4 % at 25.1).

**How far the pack had to move.** From the QP-3 position (centre -20 mm, CG 16.2) the CAD CG for a 23.0 mm target needs the pack at **centre -10 mm: 10 mm aft of the QP-3 position, not the 29 mm that 23 mm needed before the D-187 balance and the servos**. `CALC` sequence: pack at +9 mm centre gave 23.0 mm at 1,207 g; the balance (+22.6 g, x 154) alone would take that to 25.4 and the servos (+17 g, x 140) to about 27; both adders are aft of the CG and 39.6 g together shift it about 4 mm aft, so the pack moves forward again by 19 mm to -10 mm. Built and measured at each step: CG 23.05 (balance, pack -2), 24.7 (+ servos), **22.96** (pack -10). The tray is shorter as a result (end x 21.5 mm, was 40.5) and the core slot ends at 22.5 mm.

| G6 line | Result |
|---|---|
| CAD CG 20-26 mm | **23.0 mm, PASS** (mid-band; 20.8-25.1 over the trim range) |
| Predicted mass <= 1.44 kg | basic 1,245.5 + growth 139 + overrun 48 (CAD.md method) = **1,432.5 g PASS**; the `mission_gate_a.py` method (basic x 1.1174 + 48) = **1,439.7 g, 0.3 g under the line: PASS with no headroom**. SERVO.md's 1,413 g + 21 g balance = 1,434 g is consistent. Gate 1.50 kg: headroom 60-67 g |
| Structure <= 473 g | CAD itemised **471.7 g without the balance (PASS)**, **494.3 g with the 22.6 g D-187 balance (FAIL by 21 g)**; FLUTTER.md reaches 494 g independently. Servos (+17 g) are outside the structure line. **Board decision**: raise the structure line to 494 g or find 21 g (balance 7.1 g at 45 mm needs a thicker wing than the 16.8 mm section at x 154 mm) |

### 1.4 Findings that need an owner

1. **The 30 mm balance does not fit the wing section.** Over +-20 deg the lead sweeps 20.5 mm vertically; the section at x 154 mm is 16.8 mm thick (zu +9.5, zl -7.3). Best centring (lead centre 5.5 mm below the hinge axis) still pokes **up to 5.5 mm through both skins**, so the core pocket is open on both faces over a 24.6 x ~25 mm window (an elevon-hinge fairing bump on the upper and lower surface at each elevon, drag not computed). Options: (a) accept with a printed fairing; (b) reach 25 mm and 12.8 g lead (+4.3 g total) cuts the poke to 1.4 mm; (c) reach 20 mm and 16 g (+10.7 g total) fits inside the skin with 0.7 mm margin; (d) 10.7 g mass balance on a thicker region. `CALC`, geometry only; FLUTTER.md did not consider the vertical sweep.
2. **Balance moment check** (`CALC`): lead 10.7 g x 30 mm + horn 0.6 g x 11 mm = 328 g mm per elevon against 7.1 g x 30 mm = 213 g mm for CG-on-hinge (FLUTTER.md), 1.5x. Elevon CG falls 7.3 mm ahead of the hinge (was 21.4 mm aft, `EST` elevon CG 0.35 of the chord).
3. The pack zone cuts the LE foam over y +-55 mm (12 % of span, x < 22.5 mm, above z 5.5 mm); the spar is at x 60 so the D-nose there is not the torsion path, but C1 should confirm the skin and tray carry the pack landing load (tray was previously on the hub only; the tray now also rests in the slot floor with 0.5 mm clearance).
4. Pitot, GPS, FC, ESC pad coordinates are CAD interpretations (all `EST`); the FC servo rail must be set to **7.2 V** before servos are powered (build note added to `A.param`; SERVO.md open item 1).
5. Pack lead flexes with the trim (strain loop); the lips need slotted M3 bolts: not drawn.

## 2. SITL on the as-drawn aircraft

### 2.1 Plant update (what the plant now takes from the CAD)

`sitl/cad_mass.py` writes `cad_mass.json` (CAD point masses plus own inertias, products of inertia dropped as before) and `a_plant.py` / `a_aero.py` read it (`cad=1` default; `cg_aft` key overrides for trim runs):

| Quantity | QP-3 plant | As drawn |
|---|---|---|
| CG aft of the LE | 24.6 mm | **22.96 mm** |
| Inertia kg m2 (roll Ixx / pitch Iyy / yaw Izz, scaled to the case mass) | 0.05 / 0.03 / 0.05 table | **0.0632 / 0.0259 / 0.0697** at 1,245.5 g (`CALC`, includes balance and servos) |
| Prop plane (thrust station) forward of the CG | 110 mm | **121 + 23.0 = 144 mm** (hub x -120.7 mm) |
| Feet | y 0.45, x 0.30 | y 0.38 (fin), x 0.3375 (pad aft face) |
| Static margin | 6.5 % | 7.2 % (NP 40.7 mm `EST`) |
| Elevon | y 0.04-0.34, +-20 deg (set in the fold-in), arm 0.19 | unchanged; elevon centroid and fin arm now re-referenced to the CG |
| Elevon hinge inertia (one) | not modelled | 1.06e-5 (foam elevon) + 1.00e-5 (balance) = **2.06e-5 kg m2** (`CALC`); plant has no hinge dynamics, so the 300 deg/s rate limit and 0.04 s lag stay; inertial torque at that lag is 0.0027 N m against the ES3054HV 0.333-0.397 N m (SERVO.md): 0.8 %, negligible |

Cases ran at 1.43 kg (as-drawn predicted incl. growth, case mass in the plant) and the 1.50 kg gate. `THR_MAX 80`, `Q_WVANE_ENABLE 0` during entry and `wv_after 3` after the back-transition are SIM overrides (as QP-3; the real `THR_MAX 68` needs the BATT voltage compensation that SITL does not carry). Entry throttle = D184 window centre, pre-climb 1.0 s, as before.

### 2.2 Transition (entry from 50 m, hold, pitch-over, cruise 15 s)

| Mass | Wind (m/s, from) | Alt gain at handover / peak abs (m) | Handover V | t to 1.3 Vs (s) | Pitch use: of 15 / of 20 deg | Elevon peak (deg) | u max / s at cap | Rating |
|---|---|---|---|---|---|---|---|---|
| 1.43 | 0 | 34.2 / 87.5 | 13.7 | 7.3 | **0.60** / 0.45 | 9.3 | 0.786 / 0 | pass |
| 1.43 | 5 head | 32.8 / 86.1 | 13.6 | 7.1 | 0.60 / 0.45 | 9.1 | 0.843 / 0 | pass |
| 1.43 | 5 tail | 33.1 / 86.3 | 13.6 | 7.1 | 0.60 / 0.45 | 9.2 | 0.843 / 0 | pass |
| 1.43 | 5 cross | 33.9 / 87.3 | 13.6 | 7.2 | 0.60 / 0.45 | 9.3 | 0.831 / 0 | pass |
| 1.50 | 0 | 33.7 / 87.2 | 13.7 | 7.5 | **0.62** / 0.46 | 9.5 | 0.786 / 0 | pass on the stop, 0.02 over on the 15 deg basis |
| 1.50 | 5 head | 32.5 / 85.7 | 13.7 | 7.4 | 0.56 / 0.42 | 8.5 | 0.852 / 0 | pass |
| 1.50 | 5 cross | 32.5 / 86.1 | 13.5 | 7.4 | **0.62** / 0.46 | 9.4 | 0.837 / 0 | pass on the stop, 0.02 over on the 15 deg basis |

All runs: transition handover 6.5 s after FBWA, cruise settles at 17.1-17.4 m/s, roll < 1.3 deg, no run above 110 m (peak 85.7-87.5 m, fence margin 22 m), no motor above 0.852, no time at the 0.90 cap, no alt loss. QP-3 (old CG, +-25 deg stops): pitch use 0.50-0.55 of 15 deg, peak 31-40 m climb. The 5 m/s head wind runs show alpha 64-67 deg only during the hover tilt before the pitch-over (as in QP-3).

**Pitch-use basis.** The QP-3 line was "elevon pitch use <= 0.60 of 15 deg" (25 deg travel less 10 deg kept). The stop is now 20 deg, so the 15 deg basis no longer has a meaning in the hardware; the peak elevon is 8.5-9.5 deg, **0.42-0.46 of the stop**. **Rating: G5 pass on the stop fraction (0.46 <= 0.60); on the old 15 deg basis the 1.50 kg 0-wind and cross runs read 0.62, 0.02 over.** The board should state which basis G5 uses.

### 2.3 Back-transition (cruise -> QLOITER, 8 s, then QLAND from the descent; weathervane on 20 s after the switch; 0.5 m/s turbulence)

| Mass | Wind (m/s, from) | Balloon above the switch alt (m) | u max / at cap | Lean max in descent (deg) | Belly heading at QLAND (wind from; edge-on = 90 off) | Sink at touch / lean at touch / lateral speed | Tipped | Rating |
|---|---|---|---|---|---|---|---|---|
| 1.43 | 5, 0 | 6.7 | 0.786 / no | 31.3 | -94 (4 deg of edge-on) | 0.13 m/s / 10.2 deg / 0.19 m/s | no | pass |
| 1.43 | 5, 45 | 6.9 | 0.877 / no | 23.0 | -42 (the vane stops at 3 deg off edge-on from 45 deg) | 0.12 / 6.1 / 0.18 | no | pass |
| 1.43 | 5, 90 | 6.9 | **0.900 / at the cap** (short) | **40.7** | -4 | 0.06 / 6.6 / 0.07 | no | **marginal**: lean 40.7 deg and the cap touched in the cross-wind back-transition (QP-3 listed 26-29 deg lean into a head wind); stay below A-P6 lean 45 if the cap time stays < 1 s |
| 1.50 | 5, 45 | 6.1 | 0.900 / at the cap | 21.9 | -41 | 0.23 / 7.3 / 0.32 | no | pass (cap momentary) |
| 1.50 | 0 | 5.8 | 0.813 / no | 4.0 | +5 | 0.04 / 0 / 0.02 | no | pass |

Sink at touch 0.04-0.23 m/s against the 1.2 m/s design case; no tip-over; peak altitude after the switch within 7 m. Cap contact at the gate mass is the same marginal item as QP-3 (0.50-0.55 s at 1.50 kg); the cross-wind 0.90 at 1.43 kg is new. Rating: pass with the cross-wind lean flagged.

### 2.4 Cruise trim and roll rate

Cruise trim (last 8 s of cruise, `SITL`): 1.43 kg: V 17.14 m/s, pitch 6.3 deg, alpha 5.6 deg, **elevon -2.75 deg (TE up)**, duty 0.705, 149 W; 1.50 kg: 17.18 m/s, alpha 5.8, **-3.05 deg**, duty 0.708, 151 W. Closed form (`fwd_checks.py`) agrees (2.5 / 3.0 deg). The pitch trim uses 14-15 % of the 20 deg stop, and the more forward QP-3 CG would have asked for more. Hinge moment at trim 0.005-0.006 N m.

Roll (`case=roll`, FBWA full stick right 3 s then left 4 s at 17 m/s, `ROLL_LIMIT_DEG` 45, `RLL2SRV_RMAX` 150; repeat with 75 deg and 300 deg/s limits):

| Run | Peak roll rate | Differential elevon at the peak | Elevon max (incl. trim) | Bank reached | Alt min / V min |
|---|---|---|---|---|---|
| 1.43 kg, A.param limits | **89.3 deg/s** | 13.0 deg | 20.0 deg | 49 deg | 48.5 m / 14.4 |
| 1.50 kg, A.param limits | **89.8 deg/s** | 13.0 deg | 20.0 deg | 49 deg | 44.1 / 14.5 |
| 1.43 kg, limits raised (75 deg, 300 deg/s) | 89.3 deg/s | 13.0 deg | 20.0 deg | 51 deg | 47.0 / 14.4 |

**Rating: not met by 0.2-0.7 deg/s (99 %).** Raising the controller limits gives the identical 89.3: the rate is surface-limited (an elevon reaches the 20 deg stop with the -3 deg trim and the 13 deg differential). Steady-state authority (`fwd_checks.py`, `CALC`): 72 deg/s at 8.7 deg differential, 107 deg/s at 13 deg, 124 deg/s at 15 deg; 90 deg/s needs 10.8 deg differential; that would leave 6 deg to the stop with the 3 deg trim. The SITL step is dynamic and the roll inertia is 0.063 against 0.05 in QP-3 (balance, servos and motors in the CAD), which is why the SITL peak sits 1 % under the line. Marginal: needs the board to accept a 1 % shortfall or a larger elevon (the CAD y 0.04-0.34 is the full span between the fin and the hub) or 25 deg stops (the 20 deg stop is the C1 hinge-moment rule at VD 24).

### 2.5 Weathervane (Q_WVANE_ENABLE 3, SPD_MAX 2) in turbulence

Hover at 50 m in QLOITER, 100 s with 5 m/s wind and the WIND.md turbulence model at **1 m/s** (OU, tau 2 s, vertical 0.5x), heading from the plant. Excursion = largest deviation of the belly heading from its settled (median) value over the second half.

| Run | Mass | Wind from | Seed | Gain | Settled edge-on error (deg) | Excursion (deg) | Peak-to-peak (deg) | Lean mean / max (deg) |
|---|---|---|---|---|---|---|---|---|
| Z4_wv1 | 1.43 | 45 | 1 | 1.0 | 2.4 | **15.4** | 29.1 | 11.3 / 20.5 |
| Z4_wv2 | 1.43 | 45 | 2 | 1.0 | 6.8 | **23.7** | 42.1 | 9.2 / 18.9 |
| Z4_wv3 | 1.43 | 0 | 3 | 1.0 | 0.4 | **17.7** | 28.2 | 8.7 / 20.8 |
| Z4_wv4 | 1.50 | 90 | 4 | 1.0 | 1.4 | **18.8** | 29.7 | 8.0 / 22.4 |
| Z4_wv1g5 | 1.43 | 45 | 1 | 0.5 | 1.1 | 11.8 | 22.8 | 11.4 / 20.8 |
| Z4_wv2g5 | 1.43 | 45 | 2 | 0.5 | 5.8 | **19.4** (14.4 in the last third) | 35.9 | 9.2 / 18.8 |
| Z4_wv3g5 | 1.43 | 0 | 3 | 0.5 | 1.0 | 11.4 | 19.4 | 8.7 / 20.8 |

**Rating: FAILS the <= 15 deg line.** At the A.param gain (1) all four seeds exceed 15 deg (15.4-23.7 deg); at gain 0.5 two of three pass (11.8, 11.4) and one fails (19.4). The vane holds the mean heading edge-on within 0.4-6.8 deg, so the mean behaviour is right and it is the gust-driven swing that exceeds the line; peak-to-peak is 20-42 deg. Consequence for M9: the 15 deg line is not met by the vane at the current gain; gain 0.5 is better, not a pass. A lower gain slows the turn into the wind (not measured), so it is a trade. Options for B3: gain 0.3-0.5 plus a longer `Q_WVANE_SPD_MAX`/lean filter, or accept pilot heading hold in turbulence. Turbulence is 1 m/s sigma as WIND.md; the board's condition is therefore **not discharged**.

### 2.6 Fence during QLAND with the 150 m leg

`A.param` `FENCE_RADIUS` now **240** (was 250; BOARD item 7); fence ON in these runs (type 3, alt 110 m, radius 240 m, action RTL, margin 10). Cruise straight out from the transition, battery-low trigger when the aircraft is at the far point of the 150 m leg (127 m from home; 150 m for the leg end), `BATT_FS_LOW_ACT` as in A.param (mode 25: loiter to altitude, then QLAND with back-transition).

| Mass | Distance from home at the trigger (m) | Max distance from home (m) | Peak alt (m) | Modes after the trigger | Fence event | Margin to 240 m | Rating |
|---|---|---|---|---|---|---|---|
| 1.43 | 127 | **183** | 89 | mode 25 -> QLAND 27.7 s later -> "Transition VTOL done" -> landed 102.8 s after the trigger | none | 57 m | pass |
| 1.43 | 151 | **206** | 90 | QLAND after 28.3 s, landed 103.3 s | none | 34 m | pass |
| 1.50 | 129 | **184** | 89 | QLAND after 28.1 s, landed 103.4 s | none | 56 m | pass |
| 1.50 | 150 | **204** | 89 | QLAND after 28.3 s, landed 103.6 s | none | 36 m | pass |

The run-out after the trigger is 55-57 m (QP-3 measured 93 m at a 17 m/s straight line with the old CG and 25 deg stops), so the MISSION s2 any-direction bound of 220 m is not exceeded. The test flies a straight line (no racetrack); a racetrack turn would shorten the run-out in one direction and lengthen it in the other, and the 220 m bound covers that. No breach, no RTL pitch-over during the QLAND. Conditions: sag-state pack, THR_MAX 80 SIM override, calm.

## 3. Ratings against G5 and the board's lines

| Line | Source | Result | Rating |
|---|---|---|---|
| Pitch use <= 0.60 | G5, SITL-FLIGHT s1 | 0.42-0.46 of the 20 deg stop; 0.56-0.62 of the old 15 deg basis | **pass** (0.02 over on the 15 deg basis at 1.50 kg: board to state the basis) |
| No cap > 1 s into wind | G5 | 0 s at the cap in every transition; back-transition 5 m/s cross reaches 0.90 momentarily, below 1 s | **pass** (cross-wind lean 40.7 deg flagged) |
| 1.3 Vs within 15 s | G5 | 7.1-7.5 s | **pass** |
| Roll >= 90 deg/s within +-20 deg | G5 | 89.3-89.8 deg/s SITL step (surface-limited, 13 deg differential); CALC steady 107 deg/s at 13 deg | **marginal, 0.2-0.7 deg/s short** |
| Weathervane heading excursion <= 15 deg in 1 m/s turbulence | BOARD s6 condition | 15.4-23.7 deg at gain 1; 11.4-19.4 deg at gain 0.5 | **FAIL** (condition not discharged) |
| Fence during QLAND, 150 m leg | BOARD 7.2 #2 | max 183-206 m from home, no breach, 34-57 m margin | **pass** |
| CAD CG 20-26 mm | G6 | 22.96 mm (20.8-25.1 with trim) | **pass** |
| Predicted <= 1.44 kg | G6 | 1,432-1,440 g | **pass, no headroom** (script method 0.3 g under) |
| Structure <= 473 g | G6 | 471.7 g without D-187, **494.3 g with** | **FAIL as stated** (board decision on D-187) |
| CAD check, collision, assembly | task | pass, pass, pass (25 steps) | **pass** |

**Overall G5: 4 of 6 pass; roll rate marginal; weathervane fails. G6: CG and mass pass, structure fails by the D-187 balance.**

## 4. Actions

1. Board: G6 structure line 473 -> 494 g (D-187) or find 21 g; the balance does not fit the 16.8 mm section at +-20 deg (finding 1.4.1): choose reach / mass / fairing; state the pitch-use basis for 20 deg stops.
2. B3: weathervane gain 0.3-0.5 and a longer filter; re-run 4 seeds before M9; rely on pilot heading hold otherwise.
3. Roll rate: 1 % short; check on the first bench servo-throw calibration (SERVO5/6 MIN/MAX must give +-20 deg) and decide whether 25 deg stops are allowed at VD 24.
4. A1: `MASS-GATE.md`, `mission_gate_a.py` and BOM still carry the old servo, balance and pack positions (not edited here); CG 22.96 mm, basic 1,245.5 g.
5. C1: tray / pack landing load on the LE-slot floor; FLUTTER step 5 with the balance fitted.
6. Build notes: Kakute servo rail 7.2 V (A.param); balance lead bonded at the elevon nose before the elevon is installed (step C2).

## 5. Not covered

SITL uses an `EST` aero model (QP-3 s1: post-stall moment, elevon effectiveness, prop in cross-flow unmeasured); no hinge dynamics, no free play, no gust on the back-transition beyond 0.5 m/s turbulence; products of inertia (Ixz) and the 6.7 mm CG height dropped; the lead bumps through the skin (finding 1.4.1) are not in the aero; 150 m leg tested as a straight run-out, not the full racetrack; weathervane runs are 100 s, one seed each at gain 0.5 for two winds. Reproduce: `python -I redesign/qp/A/cad/build_a.py`, `collide_a.py`, `a_assembly.py`; `python -I redesign/qp/A/sitl/cad_mass.py`; `SCR=<scratch> jobq.py jobs_z4.txt` then `python fwd_sum.py Z4_*`.
