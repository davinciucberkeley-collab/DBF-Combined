# References for K09-L, by role

Status: `PROPOSED` reading list (J1, 2026-11-09; numbers updated to revision A1-R2). Every web page was read 2026-11-09. Tags: **DOC** official
ArduPilot/PX4 documentation or maker datasheet, **PAPER** peer-reviewed or thesis, **FORUM** builder's own post,
**REPO** a file in this repository. Numbers taken from a source carry its tag; `EST` is my judgement.
The forum survey of 16 tailsitter builds is already in `config-study/tiebreak/tailsitter-evidence/EVIDENCE.md`
(REPO) and is not repeated; §1 adds the comparables it lacked and §2 turns its failure list into design measures.
Numbers I computed are claims in `team/J1/claims.json` (`python -I redesign/team/J1/research_claims.py`).

## 1. Comparable aircraft

| Aircraft | Class | Span / mass | Surfaces, control | What worked | What failed or is unknown | Source |
|---|---|---|---|---|---|---|
| **K09-L** (this design) | quad tailsitter, fins | 1.15 m / 2.55 kg sized, 2.6 kg gate | 2 elevons + 4 motors, ArduPilot `Q_TAILSIT_ENABLE 1` | — | no logged precedent in class | `README.md` REPO |
| Box Kite (Wurzburg, ArduPilot dev) | quad tailsitter, foam board | ~0.76 m / 0.3–0.5 kg `EST` | 2 elevons (1.5 in, upper+lower linked), 2 × 9 g servos, 4 × 1804, 3S | flies; CG ~15 % chord; `Q_TRIM_PITCH −2`; taped LE and contact points | author: "zero wind day"; no transition log | [FORUM/DOC-listed](https://discuss.ardupilot.org/t/box-kite-copter-tailsitter-build-instructions) |
| Box Kite student fleet (dpapworth, 2025) | 4 identical quads, SpeedyBee F405 | small | 2 elevons | hover; FBWA 1–2 min | failed first transition; **all four yawed uncommanded in FBWA** (Plane has no FW yaw stabilisation by default); two boards with erratic loop rates | [FORUM, logs](https://discuss.ardupilot.org/t/boxkite-vtol-learning/139972) |
| HEQ Swan K1 / K1 PRO | commercial motor-only quad tailsitter (H-wing) | ~1.1 m / 1.0–1.12 kg empty, 2.2 kg MTOW (one dealer) | none; motors only; PX4 stock, ArduPilot port exists | sold RTF; "arm only in QHOVER/QLOITER" | roll in FW at motor limits (EVIDENCE §1.3); dealer wind "level 5" unverified | [DOC](https://ardupilot.org/plane/docs/common-Swan-K1.html), [dealer](https://druav.com/products/heq-swan-k1-pro-fixed-wing-aircraft) |
| Cygnet (richardg3) | printed motor-only quad tailsitter | 1.25 m / AUW not recalled; printed parts alone 1.62 kg | none | designer flies it | PETG copy never flown; printed structure heavy | [FORUM](https://discuss.ardupilot.org/t/3d-printed-cygnet-vtol-build-motor-only-no-control-surfaces-petg-version/142979) |
| irfan quad+ tailsitter | closest in class | 1.70 m, 0.55 m² / 2.75 kg dry | not stated | "ready to fly" | no outcome posted | [FORUM](https://discuss.ardupilot.org/t/copter-tailsitters/45514) |
| WingtraOne GEN II | commercial duo tailsitter, elevons | 1.25 m / 3.7 kg empty, 4.5–4.8 kg MTOW | 2 elevons + 2 motors, lands on its tail | 1 000 s of units; auto RTH if cruise wind > 12 m/s for 30 s | needs a flat landing spot; custom autopilot | [DOC](https://www.duncan-parnell.com/media/sparsh/product_attachment/WingtraOne_Gen_II_Tech_Specs___Wingtra.pdf) |
| HKU quadrotor tail-sitter (Lyu, Zhang) | research quad tailsitter | not extracted | motors only, custom unified controller | full-attitude wind-tunnel ID; transition with negligible altitude loss; hover and landing in crosswind | needs wind-tunnel data and a custom controller: not a stock-ArduPilot path | [PAPER](https://doi.org/10.1177/1756829318813633), [PAPER](https://doi.org/10.1109/LRA.2018.2847405) |
| DarkO (ENAC/LAAS) | research duo tailsitter | ~1 m `EST` | elevons, Paparazzi | hover held against unknown constant wind using two attitude DOF | — | [PAPER](https://hal.univ-lyon2.fr/LAAS-MAC/hal-04715046v1) |

Read-across: no quad tailsitter with elevons at 1–1.5 m and 2–3 kg has a public log of a clean round trip
(EVIDENCE §0 stands). Commercial tailsitters that work in wind (Wingtra, 12 m/s) are 2× K09-L's mass with
custom control; the hobby builds that are K09-L's size are either motor-only or small.

## 2. Failure modes the team must design out

Ranked by how often they appear in the evidence (EVIDENCE §1.3) plus what §3 found. Each has one owner.

| # | Failure mode | Evidence | Owner | Design measure (and the reference that supports it) |
|---|---|---|---|---|
| 1 | **Dive right after "transition done"**: FW pitch trim, CG or FW gains wrong when control hands over | 3 quads + 1 twin in EVIDENCE §1.2; dev: "FW pitch trim wrong, pitch-up demand to motor saturation; check CG / static margin" | B3, F4, H2 | Fixed-wing tune before any transition (DECISION §5.3). CG and trim known from AVL and the twin. `Q_TAILSIT_ANGLE` ≈ 60 (handover 30° above horizon) and `Q_TAILSIT_RAT_FW` slow at first; first transitions ≥ 50 m with QSTABILIZE rehearsed ([DOC](https://ardupilot.org/plane/docs/guide-tailsitter.html)) |
| 2 | **Uncommanded yaw in FBWA** (all four student aircraft) | dpapworth thread; ArduPilot: "NO direct rate stabilization … for yaw" in FW modes | **B3, F4** | `CL-J1-FIN-YAW-ARM` (`R-DIRECTIONAL`): with the tubes through the wing at x 0.045 (D-04) the fin centroid is 0.14 m (43 % chord) aft of the CG with no fin area ahead of it (R0 was 0.04 m and 40 %), and the prop normal force (Ribner) acts only 0.05 m ahead; B3's O4b gives Cn_β +0.044 /rad, re-run at R1 against `cnbeta_min` 0.03. Geometry no longer explains an FBWA yaw problem; software still can: F4 must name the FW yaw actuator (yaw damper needs a surface or `RUDD_DT_GAIN`-style differential thrust; see F4 list) ([DOC](https://ardupilot.org/plane/docs/yaw-in-plane.html), [PAPER](https://ntrs.nasa.gov/citations/19930091897)) |
| 3 | **Back-transition descent tumble**: low throttle, no prop wash over elevons | dpapworth twin, 5 months unsteady | F4, H2 | Keep descent throttle up (`Q_TAILSIT_THR_VT`), slow `Q_LAND_SPEED`, weathervane nose-into-wind in QLOITER/QLAND (`Q_WVANE_ENABLE 1`, gain start 1) ([DOC](https://ardupilot.org/plane/docs/quadplane-weathervaning.html)) |
| 4 | **Hover lean and tip-over in wind** | lean 15° at 5 m/s, 34° at 8 m/s (`CL-B1-LEAN-5MS`, `-8MS`); tip-over 30.6° on the narrow axis (`CL-A1-TIPOVER`; D5 splays the feet); large wing area makes tail-sitters crosswind-sensitive ([PAPER](https://doi.org/10.1109/LRA.2018.2847405)) | B1, C5, H3 | 5 m/s flight card stands; Wingtra's 12 m/s needs 2× the mass and a custom loop. Foot stance ≥ 30° kept; land into wind |
| 5 | **Motor-tube resonance with the motors** | `CL-J1-TUBE-MODE-SEP` **FAILS** (−91 %, `R-VIBRATION`): bare tube f₁ ≈ 183 Hz vs hover 2P 180 Hz (B4 rpm 5 396; 2 % apart) and cruise 2P 200 Hz; the forcing sweeps 1P 90–156 Hz and 2P 180–312 Hz up to the 9 350 rpm cap, so no bare-tube mode in 72–374 Hz clears 20 % at every steady point; E of a hobby tube is 50–140 GPa, so f₁ could be anywhere 130–215 Hz | **C4, H1** | Design the fin bond as the shear web that puts the first mode above ~375 Hz, or show it damped in the tap test (`R-VIBRATION` allows either); VIBE < 30 m/s², Clip 0 ([DOC](https://ardupilot.org/plane/docs/common-measuring-vibration.html)); RPM-based notch from ESC telemetry ([DOC](https://ardupilot.org/plane/docs/common-imu-notch-filtering.html)) |
| 6 | **Static margin vs trim**: the plank trims only what the airfoil's +Cm allows | `CL-J1-SM-TRIMMABLE`: the S5010's cm0 ≈ 0 (B2: −0.004 at Re 2.3e5) trims −0.9 % SM with elevons neutral at CL 0.44, so all 5 % of SM is elevon up-trim (B2 ≈ −4° at CL 0.5); Hepperle: planks use 2–5 % | **B2, B3** | Accepted by D-19 (CR-J1-02 rejected): the up-trim penalty is inside the trimmed CLmax 0.80. Flight check: elevon trim position in FBWA ≤ `elevon_trim_travel_max` ([DOC](https://www.mh-aerotools.de/airfoils/flywing1.htm)) |
| 7 | **Connectors**: XT60 under-rated for the 120 A momentary case | `CL-J1-XT60-BURST` **FAILS** (60 A / 1 min vs 120 A); XT60 continuous 35 A (Amass) vs 33.75 A required on the 27 A hover (+4 %) and **FAILS** vs 37.4 A on E2's 29.9 A gate-wind hover (`CL-J1-XT60-CONT-PESS`, −6 %); Holybro's 30 A fails both | **F1** | AS150U (70 A / 140 A, reseller values) or a cited short-time XT60 rating for the ≤ 5 s case at the 100 A limiter (A1's condition); 12 AWG leads; heat run at 37 A ([DOC](https://docs.holybro.com/power-module-and-pdb/power-module/connector-and-wire-rating), [DOC](https://www.china-amass.net/uploads/57.XT60-F-SPEC-2025V0.pdf)) |
| 8 | **Setup errors**: motor order, reversed surfaces, FC orientation, loop rate | 3 cases EVIDENCE §1.2; steph280 "disaster" = motor order | H1, F4 | Props-off motor-order and surface-direction check on the flight card; `Q_OPTIONS` bit 18 (arm only in VTOL mode); DCM-inconsistent prearm → lay horizontal 20 s (Box Kite) |
| 9 | **ESC desync / motor stop** on a low-KV, 4S, 11 in prop | low-KV high-inductance motors desync at high power; cure: timing up, ramp-up power down, low-ESR capacitor at the ESC ([web](https://oscarliang.com/fix-esc-desync)) | E1, F1 | Bench full-throttle step tests on the stand before flight; capacitor on each ESC; Bluejay reflash gives RPM telemetry for the notch |
| 10 | **Any motor/ESC failure is a crash** | accepted in CONFIGURATION.md | E1, H3 | Spares, thrust-stand burn-in of all four, connector inspection after every full-throttle run |
| 11 | **Pitot in prop wash / uncovered at boot** | ArduPilot: mount out of the prop flow; cover before power-up | B4, F3 | Wing LE at y ≈ 0.15 is inside the 0.28 m disc's wash band (y 0.18–0.46)? → check; pod nose is clear if ahead of the prop plane |
| 12 | **Compass interference** from 27–120 A loops | field rises with loop area and current | F2, F3 | GPS/compass on a mast ≥ 0.1 m from the power leads (`gps_mast_clearance_m`); twist pack-PDB-ESC leads; shortest loop ([DOC](https://ardupilot.org/plane/docs/common-magnetic-interference.html)) |

## 3. References by role

### A — Leadership and systems
| Ref | Take from it | Tag |
|---|---|---|
| `inputs/ADVISOR-XV24-LESSONS.md` | mass discipline and status words; the only thing that stopped a 4 000-part model was no mass budget | REPO |
| [Rehan et al. 2022, VTOL hybrid UAV overview, Aeronautical J.](https://cambridge.org/core/journals/aeronautical-journal/article/vertical-takeoff-and-landing-hybrid-unmanned-aerial-vehicles-an-overview/422DF985F2393E5E8EA82E3299190497) | taxonomy (tail-sitter = "mid-air flip"); use for the design-review framing, not numbers | PAPER |
| `team/J1/claims.json` | A2: `CL-J1-FIN-YAW-ARM` verifies `R-DIRECTIONAL`, `CL-J1-TUBE-MODE-SEP` verifies `R-VIBRATION` (fails −91 %, C4 owns), `CL-J1-XT60-*` and `CL-J1-AS150U-*` verify `R-DISCONNECT` (CR-A2-06 closed) | REPO |
| [ArduPilot vibration limits](https://ardupilot.org/plane/docs/common-measuring-vibration.html) | A2's verification matrix number: VIBE < 30 m/s², Clip = 0 | DOC |

### B — Aerodynamics
| Ref | Take from it | Tag |
|---|---|---|
| [Hepperle, MH 45](https://www.mh-aerotools.de/airfoils/mh45koo.htm) | t/c 9.85 %, cm c/4 = +0.0145, Re ≥ 100 000: the R0 section, superseded by the S5010 (D-02; cm0 −0.004 at Re 2.3e5 from B2's XFOIL, `P:b2.xfoil.cm0_2d_re2.3e5`); kept as the comparison point for the trim argument | DOC |
| [Hepperle, flying-wing basics](https://www.mh-aerotools.de/airfoils/flywing1.htm) | plank NP at c/4; stability coefficient 0.02–0.05; trim Cm = CL σ; flaps must not be up-deflected in trimmed flight | DOC |
| [APC PER3 11x4.5MR](https://www.apcprop.com/files/PER3_11x45MR.dat) | static 5.0 / 7.25 / 9.9 N at 5 / 6 / 7 krpm; zero thrust at J ≈ 0.545; at 1 N and 15 m/s η is 0.30–0.45 (`ASM-J1-ETA-CRUISE`). Closed by D-05: the flight prop is the 11×5.5MR, B4 `CL-B4-CRUISE-ETA` 0.46 (0.37 for the 11×4.5MR), E1 0.39; B1 re-runs endurance | DOC |
| [Ribner, NACA R-820](https://ntrs.nasa.gov/citations/19930091897) | yawed prop = fin of its projected side area; four tractor props 0.05 m (15 % chord) ahead of the CG at R1 (`CL-J1-PROP-ARM`; 0.21 m at R0) still destabilise pitch and yaw, 4× less than before: B3 includes it in the R1 neutral point (CR-J1-11) | PAPER |
| [Lyu 2018, unified control](https://doi.org/10.1177/1756829318813633) · [DOB hover](https://doi.org/10.1109/LRA.2018.2847405) | full-attitude aero model shape for the transition corridor; wing broadside in hover is the dominant wind force (REVIEW's flat-plate method is the right first cut) | PAPER |
| `config-study/cards/K09/REVIEW.md` §3–4 | download 1.06; cruise η_motor 0.72 (iron loss at 25 W shaft) | REPO |
| [Sansou 2024, DarkO](https://hal.univ-lyon2.fr/LAAS-MAC/hal-04715046v1) | B3: hover trim in steady wind uses pitch *and* roll DOF; relevant to `Q_WVANE` and lean limits | PAPER |

### C — Structures
| Ref | Take from it | Tag |
|---|---|---|
| [Easy Composites, tubes explained](https://www.easycomposites.co.uk/learning/carbon-fibre-tubes-explained) · [Epsilon pultrusions](https://www.epsilon-composite.com/wp-content/uploads/2022/01/ENG-2022-Standard-profiles-catalogue.pdf) | roll-wrapped vs pultruded: UD pultrusion E 100–140 GPa; woven hobby tubes far lower; roll-wrapped wins their bend test. `ASM-J1-E-TUBE` = 100 GPa `UNVERIFIED` → bend-test the bought tube (`T-J1-TUBE-BEND`) | DOC |
| `team/J1/claims.json` `CALC-J1-TUBE-MODE` · `CALC-J1-MOTOR-FREQ` | EI ≈ 365 N·m² (at 100 GPa); bare-tube f₁ ≈ 183 Hz with motor + 11×5.5MR + mount at 0.19 m; forcing from B4's rpm: hover 1P 90 / 2P 180 Hz, cruise 100 / 200 Hz, 9 350 rpm cap 156 / 312 Hz (unlimited fresh pack 177 / 355 Hz for < 5 s). C4 re-derives with the half-fin bonded along the tube: first mode above ~375 Hz or a measured damping | REPO |
| [Owens Corning FOAMULAR NGX 250](https://www.owenscorning.com/dms/43522) | compressive ≥ 25 psi (172 kPa), ASTM C578 Type IV (min 1.55 pcf ≈ 25 kg/m³); flexural 50–75 psi in older sheets; "non-structural" on the sheet: the tape skin and spar carry everything | DOC |
| [Flite Test tape-skinned foam-board method](https://flitetest.com/articles/an-alternative-foam-board-build-method) | the hobby-standard fin and twin construction; tape burnished with a card edge; no strength data exists → C4 sizes the fin as a foam-board shear web with a test coupon | FORUM |
| [TU Delft compliant landing gear](https://repository.tudelft.nl/file/File_1d3c3ae8-bbc3-49da-a470-07c94c81e44f) | C5: compliant gear cut peak force up to 75 % in drop tests; size feet by sink speed × stroke × load factor; no tailsitter foot data exists anywhere I looked → drop-test the foot | PAPER |
| [Box Kite build](https://discuss.ardupilot.org/t/box-kite-copter-tailsitter-build-instructions) | C5/C6: tape the LE and ground-contact points; trim elevons clear of the ground; expect contact | FORUM |
| `inputs/DECISIONS-ADOPTED.md` | C6: previous joint and insert findings carry over as evidence | REPO |

### D — Mechanical design
| Ref | Take from it | Tag |
|---|---|---|
| [Box Kite build](https://discuss.ardupilot.org/t/box-kite-copter-tailsitter-build-instructions) | D6: 1.5 in elevons bevelled 45°, fibre-reinforced packing-tape hinge, upper and lower elevons linked by bamboo rods, 9 g metal-gear servos; CG hanger printed; equipment "as far forward as possible" | FORUM |
| [ArduPilot vibration damping](https://ardupilot.org/plane/docs/common-vibration-damping.html) | D2: FC on gel pads or 3M foam squares, Velcro not over-tight; off-the-shelf mounts are for 5–10× heavier boards | DOC |
| [ArduPilot airspeed](https://ardupilot.org/plane/docs/airspeed.html) | D2: pitot ≥ 1 cm proud of the nose, out of the prop flow; cover fitted before power-up | DOC |
| [ArduPilot magnetic interference](https://ardupilot.org/plane/docs/common-magnetic-interference.html) | D2: GPS/compass mast up and away from the pack and PDB | DOC |
| `config-study/cards/K09/REVIEW.md` §7 | D7: cradles under the spar with ≥ 70 mm crush foam (D-22), never foam pressing on fins or tubes; box 1.25 × 0.55 × 0.50 m external (D-16: the tube ends set the 0.425 m envelope) | REPO |
| Swan K1 page | D3: an H-wing with motors on vertical fins is a sold product; its fins are the motor structure, as here | DOC |

### E — Propulsion and energy
| Ref | Take from it | Tag |
|---|---|---|
| [APC PER3 11x4.5MR](https://www.apcprop.com/files/PER3_11x45MR.dat) | E1: now the stand A/B prop only (D-05); the 11×5.5MR flies: B4 hover 5 396 rpm, cruise 6 000 rpm, cap 9 350 rpm, unlimited 10 637 rpm on a fresh pack (APC static runs ~10 % optimistic → confirm on the stand, P13) | DOC |
| [SunnySky X3108S page](https://sunnyskyusa.com/products/sunnysky-x3108s-motors) | E1: the 11×4.7 table in `params.json`; page rate-limited today (HTTP 429): re-open and set `checked` (CR-A1-07) | DOC |
| [ESC desync](https://oscarliang.com/fix-esc-desync) · [Amass XT60-F](https://www.china-amass.net/uploads/57.XT60-F-SPEC-2025V0.pdf) | E1/F1: low-KV motors on BLHeli_S: timing up, ramp-up power down, 470–1 000 µF low-ESR capacitor at each ESC; XT60 is 35 A at 12 AWG with 85 K rise | web/DOC |
| [ArduPilot notch filtering](https://ardupilot.org/plane/docs/common-imu-notch-filtering.html) | E1: ESC RPM telemetry is the best notch source → reflash the LANRC ESCs to Bluejay for bidirectional DShot (params.json already notes it) | DOC |
| `config-study/cards/K09/REVIEW.md` §4 · `params.json#performance` | E2: cruise power carried at B1's 307 W (11×4.5MR, η 0.37); 181 W (B4) to 216 W (E1) with the 11×5.5MR; pessimistic 340–397 W → cruise after hover 12.3 min base, 6.4 min pessimistic (E2); B1 re-runs at 16 m/s | REPO |
| [FAA recreational flyers](https://www.faa.gov/uas/recreational_flyers) | E2/H3: registration ($5 / 3 yr) above 250 g; the pack is the only item with a transport rule (carry-on, storage charge): see H3 | DOC (page blocked the fetch; `UNVERIFIED`) |

### F — Electrical and avionics
| Ref | Take from it | Tag |
|---|---|---|
| [Holybro connector table](https://docs.holybro.com/power-module-and-pdb/power-module/connector-and-wire-rating) · [Amass XT60-F](https://www.china-amass.net/uploads/57.XT60-F-SPEC-2025V0.pdf) · [AS150U listings](https://robu.in/product/amass-as150u-male-connector/) | F1: XT60 30 A (4 h, < 60 °C) / 60 A 1 min; Amass 35 A at 12 AWG; AS150U 70 A / 140 A (reseller; one forum melt report of the pre-charge contact). Required 33.75 A (1.25 × 27 A) or 37.4 A on E2's 29.9 A: `CL-J1-XT60-CONT-PESS` **FAILS** −6 %, `CL-J1-XT60-BURST` **FAILS** 120 A; AS150U passes both | DOC |
| [ArduPilot magnetic interference](https://ardupilot.org/plane/docs/common-magnetic-interference.html) | F2: twist pack–PDB–ESC leads; ESC–motor leads matter less (AC); loop area × current sets the field | DOC |
| [ArduPilot tailsitter guide](https://ardupilot.org/plane/docs/guide-tailsitter.html) | F3/F4: `Q_TAILSIT_ENABLE 1`, `Q_TAILSIT_MOTMX` all four, `Q_FRAME_CLASS 1 / TYPE 1`, `Q_OPTIONS` bit 18; `Q_TAILSIT_ANGLE` ≈ 60; `Q_TAILSIT_GSCMSK` with `Q_TAILSIT_DSKLD` = mass / total disc area (2.6 kg / 0.245 m² = 10.6 kg/m²); "an airspeed sensor should be fitted" | DOC |
| [Tailsitter tuning guide](https://ardupilot.org/plane/docs/tailsitter-tuning-guide.html) | F4/H2: notch → sharp pitch and yaw stick inputs in hover → FF from log (start X = 0.2; I = FF) → D then P by oscillate-and-halve → roll like a quad (QAUTOTUNE roll only) | DOC |
| [Yaw in Plane](https://ardupilot.org/plane/docs/yaw-in-plane.html) · [Box Kite learning](https://discuss.ardupilot.org/t/boxkite-vtol-learning/139972) · [dual-motor tailsitter FBWA yaw](https://discuss.ardupilot.org/t/dual-motor-tailsitter-yaw-stabilization-in-fbwa/69013) | F4: no FW yaw stabilisation by default; yaw damper works only through a surface or differential throttle; builders use `YAW2SRV_DAMP` ≈ 0.08–0.12 with `KFF_RDDRMIX 0`; K09-L has no rudder → decide the FW yaw actuator (`Q_OPTIONS` bit 8 motors-only assist, or always-on assist) and test it on the twin | DOC/FORUM |
| [Weathervaning](https://ardupilot.org/plane/docs/quadplane-weathervaning.html) | F4: `Q_WVANE_ENABLE 1`, `Q_WVANE_GAIN` start 1, `Q_WVANE_ANG_MIN` 1°; only in QLOITER/QLAND/QRTL | DOC |
| [Airspeed](https://ardupilot.org/plane/docs/airspeed.html) | F3: `ARSPD_AUTOCAL 1` needs turns; `ARSPD_OFFSET` consistency check at boot; `ARSPD_USE` options | DOC |
| [Vibration damping](https://ardupilot.org/plane/docs/common-vibration-damping.html) · [measuring](https://ardupilot.org/plane/docs/common-measuring-vibration.html) | F3: gel pads; VIBE < 30 m/s², Clip 0 (< 100 tolerable) | DOC |
| [Box Kite param file](https://discuss.ardupilot.org/t/box-kite-copter-tailsitter-build-instructions) | F4: a working small-quad-tailsitter starting set (`Q_A_RAT_YAW_P 2.3`, `Q_TRIM_PITCH −2`, `ARSPD_FBW_MIN 6 / MAX 16`, `LIM_ROLL_CD 6000`) — scale, do not copy | FORUM |
| `config-study/research/flight-control/FINDINGS.md` | F5: radio and telemetry findings carried over | REPO |

### G — Manufacturing
| Ref | Take from it | Tag |
|---|---|---|
| [MIT hot-wire guide](https://k12maker.mit.edu/uploads/9/7/5/8/97583140/hot_wire_guide.pdf) · [RCU cutting notes](https://www.rcuniverse.com/forum/airplanes-all-types-286/11715658-irregular-wing-surface-ridges.html) · [Petaurus Aero](https://petaurusaero.substack.com/p/hot-wire-cutting-wings) | G1/G2: kerf no wider than the wire = correct heat; constant feed ≈ 2–3 mm/s; numbered template increments called out by two cutters; ½ in lead-in/lead-out; templates smooth; test on scrap; ventilate | web |
| [FOAMULAR NGX 250](https://www.owenscorning.com/dms/43522) | G2: 2 in sheet, Type IV, 25 psi; weigh the first core against 30 kg/m³ (P14) | DOC |
| [Flite Test foam-board method](https://flitetest.com/articles/an-alternative-foam-board-build-method) · [Box Kite](https://discuss.ardupilot.org/t/box-kite-copter-tailsitter-build-instructions) | G2: tape over paper-faced board, card-edge burnish; hot glue; bevelled tape hinges | FORUM |
| [Cygnet PETG thread](https://discuss.ardupilot.org/t/3d-printed-cygnet-vtol-build-motor-only-no-control-surfaces-petg-version/142979) | G3: printed structure is heavy (1.62 kg of prints at 1.25 m); print only mounts, saddles, clips, feet, tray | FORUM |
| `config-study/cards/K09/REVIEW.md` §8 | G4: fin-tube joint needs one design-and-reprint iteration; add 5–10 h | REPO |

### H — Test and safety
| Ref | Take from it | Tag |
|---|---|---|
| [Tailsitter tuning guide](https://ardupilot.org/plane/docs/tailsitter-tuning-guide.html) · [notch](https://ardupilot.org/plane/docs/common-imu-notch-filtering.html) · [measuring vibration](https://ardupilot.org/plane/docs/common-measuring-vibration.html) | H1/H2: the order of the hover campaign; pass numbers VIBE < 30 m/s², Clip 0; three harmonics | DOC |
| `team/J1/claims.json` tests `T-J1-TAP-TEST`, `T-J1-TUBE-BEND`, `T-J1-XT60-HEAT` | H1: three bench tests that retire `ASM-J1-E-TUBE`, the tube-mode claim and the connector claims (heat run at 37 A, E2's gate-wind case) | REPO |
| `config-study/tiebreak/DECISION.md` §5.4 · EVIDENCE §1.3 | H2: twin → thrust stand → tethered hover (27 A ± 15 %, `hover_current_tol`) → FW campaign → transition ≥ 50 m → back-transition at altitude → landing practice in calm air; QSTABILIZE recovery rehearsed | REPO |
| [Box Kite build](https://discuss.ardupilot.org/t/box-kite-copter-tailsitter-build-instructions) | H2: zero-wind first hover; 10 × 10 m space; motor order checked "like a copter"; DCM prearm fix | FORUM |
| [FAA recreational flyers](https://www.faa.gov/uas/recreational_flyers) (fetch blocked, 403) · secondary: [Pilot Institute registration](https://pilotinstitute.com/drone-registration/) | H3: TRUST certificate per pilot; register (> 250 g, $5 / 3 yr, number on the aircraft); Remote ID exempt only inside a FRIA (RFS); 400 ft; VLOS; CBO guidelines. Confirm on faa.gov; the "educational" vs Part 107 question is open (REVIEW §6) | DOC/`UNVERIFIED` |
| [AS150U sparking thread](https://discuss.ardupilot.org/t/as150u-connectors-sparking/75032) | H3: the anti-spark contact can melt; inspect after full-throttle runs; LiPo bag, ammo can already in the BOM | FORUM |

### I — Program
| Ref | Take from it | Tag |
|---|---|---|
| [Aloft Hobbies 22 × 20 × 1 000 mm tube](https://alofthobbies.com/products/22-x-20-x-1000mm-mw-carbon-tubing-matte-finish) | I1: $24, listed in stock at a US hobby vendor (mandrel-wound, layup unstated) vs the BOM's overseas ~2-week line; buy one early for the bend test; Rock West's 20 × 22 pull-braided page was 404 today | web |
| [ArduPilot tailsitter guide](https://ardupilot.org/plane/docs/guide-tailsitter.html) | I1: airspeed sensor is a DOC recommendation, not optional (DECISION §5.1) | DOC |
| EVIDENCE §1.2–1.3 | I2: 3–6 weeks from first stable hover to first clean round trip for a first-time team; instructor fleet: 1 month to first attempt; budget 30–40 flight-test hours (REVIEW §8) | REPO |
| [SunnySky X3108S](https://sunnyskyusa.com/products/sunnysky-x3108s-motors) | I1: page rate-limited today; confirm stock before the ~20 Nov electronics order | DOC |

## 4. What I did not find

- Any public log of a quad tailsitter with elevons in K09-L's class completing a round trip (EVIDENCE §0 confirmed).
- Any tailsitter-specific landing-foot or tip-over data; C5 must make its own with a drop test.
- A maker datasheet for the AS150U; the 70 A figure is a reseller value.
- Measured arm-in-slipstream thrust loss for a tube across a prop disc; the REVIEW's 1.06 stays an estimate for B4.
- The FOAMULAR NGX 250 sheet's density line (the PDF fetched as binary); the Type IV minimum 1.55 pcf is from ASTM C578.
