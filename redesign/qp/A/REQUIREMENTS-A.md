# Requirements, concept A (scaled quad tailsitter), 2026-11-14 (updated D-183 / D-184)

Status `PROPOSED`, owner A2. Adapted from `qp/requirements/REQUIREMENTS-QP.md` (written for B) and the K09-L set (`review/CLOSURE-ROUND-2026-11-14/A2.md` s1). Numbers from SIZING-A.md, MISSION.md, MASS-GATE.md, BOM-A.csv. `EST` estimate, `—` unknown. Paths relative to `redesign/`.
Classes: **USER** user constraint; **PHYSICAL** physical, safety or legal limit; **DERIVED** team choice with its basis. Disp: carry / adapt / drop / new.

## 1. User requirements (the only fixed ones)

| ID | Requirement | Class | Disp | Basis |
|---|---|---|---|---|
| A-U1 | Total physical spend <= $2,000 incl. tax, shipping, packs, charger, radio, test gear, tools, crash reserve. Makers Pass outside | USER | carry | root `CLAUDE.md`. BOM-A: $1,651.85 / +$348.15 nominal, +$217.53 at +30 % on the 9 unverified lines (D-183 levers, D-184 +$5); see D184.md |
| A-U2 | Built and flight-tested by 2027-04-30 | USER | carry | `CLAUDE.md` |
| A-U3 | Transport: multi-piece allowed; must fit **one car trunk, two pieces at most**; team of 4 carries it | USER | adapt | user rule given for this round (replaces "one piece in a car box", D-J6-2). A is one piece, 0.90 x 0.50 x 0.39 m props on; trunk size `—` (no car measured) |
| A-U4 | 3-D physics pass: no floating parts, no phasing, assembly swept | USER | carry | `CLAUDE.md` |
| A-U5 | Mass < 25 kg (55 lb) | USER/LEGAL | carry | `CLAUDE.md`; A 1.5 kg |

## 2. Configuration, mission, mass

| ID | Requirement | Class | Disp | Basis |
|---|---|---|---|---|
| A-D1 | Scaled quad tailsitter: 0.90 x 0.245 m wing, 2 fins, 4 fixed MN2212 KV780 with APC 9x4.5MR/MRP props in an X (arm x1.2, motors at y 0.228 / z 0.156 m, cant 16 deg), 4S Tattu 2300 | DERIVED | adapt (from QP-D1, R-CONFIG) | D-182; BOARD |
| A-D2 | Mission: 3.0 min hover-mode incl. 40 s go-around, 3.41 min cruise at 17 m/s (requirement 3.5), 20 % reserve | DERIVED (phases), PHYSICAL-linked (reserve: T/W 1.6 at 20 % rest voltage) | adapt | MISSION.md |
| A-P1 | Mass gate 1.50 kg frozen as-built; T/W fresh >= 2.0 and sag >= 1.6 at the gate with `Q_M_SPIN_MAX` 0.90 (2.30 / 1.82 `EST`, prop_a.py x0.93) | PHYSICAL | adapt (R-MASS-GATE, QP-P1) | MASS-GATE s1; C5 |
| A-D3 | Design target <= 1.44 kg predicted incl. growth (now 1.381 kg); growth by maturity; overrun 48 g | DERIVED | adapt | MASS-GATE s2-4 |
| A-P2 | Hover T/W >= 2.0 fresh, >= 1.6 worst pack state (20 % rest, 3.73 V/cell); hover throttle <= 0.625 | PHYSICAL | carry (R-HOVER-TW) | `hover_tw_min*` |
| A-P3 | Transition entry window >= +-5 % of the weight-ratio entry thrust (R2 floor) by a time-domain pitch-over with elevon limit; entry >= 1.33 W, <= 0.80 x T/W sag; 20 % control thrust reserve kept | PHYSICAL | adapt (R-TRANSITION) | C3; MASS-GATE s1. Window +-4.5 % at 1.50 kg with the 0.90 cap (+-6.6 % at 1.44, +-8.7 % at 1.381) |
| A-P4 | Static margin >= 5 % chord; CG 20-26 mm aft of LE (target), <= 28.5 mm hard; lateral CG <= 5 mm | PHYSICAL | adapt (R-CG-RANGE, R-STATIC-MARGIN) | C4; MASS-GATE s5 |
| A-D4 | Pack accepted at <= listed + 5 g (Tattu 2300: 270 g, 275 g) and fits the cage ahead of the LE | DERIVED | adapt (R-PACK-MASS, QP-D4) | BOM W01 |
| A-P5 | Pack retained at 12 g crash decel (1.2 m/s on 6 mm crush) | PHYSICAL | carry (R-PACK-RETENTION) | SIZING-A s4 |
| A-D5 | Crash reserve = pack + motor + servo + full airframe set beyond spares, x 1.1025 + 3 shipments; FC and ESC board not in it | DERIVED | adapt (R-RESERVE) | bom_a.py; K09-L lesson (tube) |
| A-D6 | One BOM, one mission, one gate shared by all A reports; per-subsystem cost caps in `bom_a.py` | DERIVED | new | BOARD C6 |

## 3. Flight envelope and tailsitter specifics

| ID | Requirement | Class | Disp | Basis |
|---|---|---|---|---|
| A-P6 | Clean stall Vs <= cruise / 1.3 at the gate mass: Vs 12.19 m/s at 1.50 kg, 1.3 Vs 15.85 < 17 m/s cruise (11.70 / 15.21 at 1.381 kg); measured stall replaces CLmax 0.75 | DERIVED | adapt (R-STALL) | MISSION s1 |
| A-P7 | Hover yaw authority >= **0.35 N m** at +-0.10 throttle (fail < 0.30 N m: the 5 m/s card is reopened), measured on the hanging yaw test at arm x1.2 (0.228 m) and cant **16 deg**; rotor reaction Q >= 55 N mm; ratio to the wind moment >= 1.5 before free hover | PHYSICAL | adapt (R-HOVER-AUTHORITY) | C1; D-184, WIND.md s5 (0.35 `EST`; model Q 59.7 N mm gives 0.346, marginal) |
| A-P8 | Wind: <= 5 m/s mean (RCMC1 basis, rescaled by the H3 RFS ratio), gust <= 8 m/s; survive-and-land 8 m/s gust; lean <= `Q_A_ANGLE_MAX` 45 deg at 7 m/s; no motor above 85 % output (SITL peak 0.87 at 5 m/s; none held at the 0.90 cap > 1 s) | PHYSICAL | adapt (R-WIND, R-GUST-LEAN) | C2; lean 29 / 47 deg at 5 / 7 m/s |
| A-P8a | **Heading rule (D-184):** hover and loiter with the wing edge into the wind within +-10 deg by pilot yaw (+-20 deg in steady wind and gust only); belly-on only to 3 m/s; takeoff and landing edge-on; `Q_WVANE_ENABLE` 0 (weathervane turns the belly into the wind); 4 m/s limit if the bench plate yaw moment or the tethered turbulence test fails | PHYSICAL | new | WIND.md s2-s4: arm x1.2 + cant 16 deg passes steady and +2 m/s gust over +-20 deg; turbulence yaw peak 11-15 deg is **marginal**, not a pass |
| A-P9 | Landing on fin tips: static tip-over >= 30 deg (33.2 deg `EST`); parked tip 6.8 m/s < 8 m/s gust, so crew catches or lays down the aircraft | PHYSICAL | adapt (R-TIPOVER, R-LANDING-IMPACT) | SIZING-A s4; C2 |
| A-P10 | Fin and root bending mode >= 20 % from hover 1P and 2P (71 / 142 Hz fresh, 76 / 153 sag) at the as-built root; tap test | PHYSICAL | adapt (R-VIBRATION) | C8; 7 % at fixity 0.75 `EST` |
| A-P11 | Cruise control: roll rate >= 90 deg/s with elevons; servo stall torque >= 1.5 x hinge moment (ES3352HV 1.7-2.4 kgf-cm `U`) | PHYSICAL | adapt (R-CRUISE-AUTHORITY, R-SERVO-TORQUE) | `—` hinge moment not computed |
| A-P12 | Cruise prop chosen on the bench with hover T/W still >= 2.0 fresh at the gate | PHYSICAL | new | C7 |
| A-P13 | Loads: limit +3.4 / -1.5 g floor, ultimate 1.5 x limit, MS >= 0 on spar, cage, fin root at 1.5 x limit; fin tips at 12 g | PHYSICAL | adapt (R-LOADS, R-STRUCT-MARGIN) | `—` not computed for A |
| A-P14 | Airspeed error <= 0.5 m/s at cruise; pitot outside rotor wash | PHYSICAL | carry (R-AIRSPEED) | BOM V05 |
| A-P15 | Directional stability Cn_beta >= 0.03 /rad; no spiral divergence (fins + wing) | PHYSICAL | adapt (R-DIRECTIONAL, R-SPIRAL) | `—` not computed |

## 4. Electrical, avionics, safety

| ID | Requirement | Class | Disp | Basis |
|---|---|---|---|---|
| A-P16 | Winding and ESC current <= rating: motor 13 A / 180 s; `Q_M_SPIN_MAX` 0.90 required: APC 9x4.5MR uncapped full duty 13.0 A fresh (14.3 A one motor), at 0.90 one motor 12.1 A phase / 10.9 A bus (prop_a.py); ESC 35 A per channel; connector >= 1.25 x peak | PHYSICAL | carry (R-ESC-CURRENT, R-DISCONNECT) | SIZING-A s3; prop_a.py; BOM P04 |
| A-P17 | ESC speaks bidirectional DShot for the rpm notch (`INS_HNTCH_*`) | PHYSICAL | new | BOARD s1 item 3; BOM P04 BLHeli_S, Bluejay `—` |
| A-P18 | Thermal limits from maker; BEC >= 2 x servo stall; compass interference <= 30 % at hover current; HDOP <= 1.2 | PHYSICAL | carry (R-THERMAL, R-AVIONICS-POWER, R-COMPASS) | BOM P05 BEC part `—` |
| A-P19 | Arm and hard kill stop all motors <= 1 s; ELRS LQ >= 0.9; RC loss in a Q mode -> QLAND; failsafes | PHYSICAL | carry (R-ARM-KILL, R-RC-LINK, R-FAILSAFES) | `estop_time_max_s` |
| A-P20 | **Any motor out in hover: not survivable** (4 fixed rotors in an X); controls: motor test before every flight, no motor > 85 %, winding within rating | PHYSICAL | new (declared) | QP-P15 carried; 6 rotors outside $2,000 |
| A-P21 | Param file passes the firmware-name check; tailsitter frame name `UNVERIFIED` until read in `vehicleinfo.py` | PHYSICAL | adapt (R-FC-STABLE, R-FSW-PARAMS) | BOARD s4 |
| A-P22 | Harness: supports <= 0.15 m, chafe, strain relief at motors; mass from the routed harness | PHYSICAL | adapt (R-HARNESS-INSTALL) | `—` no routed mass |
| A-P23 | Battery handling: LiPo bag, charge 10-45 C, no re-flying a part-used pack | PHYSICAL | carry (R-BATT-HANDLING) | `H3/BATTERY-PROCEDURE.md` |

## 5. Process, site, build

| ID | Requirement | Class | Disp | Basis |
|---|---|---|---|---|
| A-D7 | Test order, no gate skipped: SITL crosswind hover, M1 thrust stand, M3 hanging yaw, M4 fin tap, M5 CG breadboard, tether, free hover, C3 pitch-over run, transition >= 50 m | DERIVED | adapt (R-TEST-ORDER) | BOARD actions; no twin |
| A-D8 | First tethered hover by 2027-02-15 (R4 trigger); latest first tethered hover from the 30 Apr date = 30 Apr minus flight programme minus one crash loop (`—` until I2 plans A) | DERIVED | adapt (R-BUILD-HOURS) | BOARD R4; build hours `—` |
| A-D9 | >= 10 h SITL on the tailsitter model with A's param file before first hover; stick time on a small quad | DERIVED | carry (R-PILOT) | `sitl_hours_min` |
| A-P24 | Site and law: RFS yellow fields, FRIA, VLOS <= 500 m, <= 400 ft, spotter, request >= 7 business days ahead; fence 250 m / 110 m (racetrack far point 201 m) | PHYSICAL/LEGAL | carry (R-SITE, R-LEGAL) | H3 flight card |
| A-D10 | Transport drop 0.3 m, <= 6 kg loaded; field setup <= 5 min one person (props on, one piece) | DERIVED | adapt (R-TRANSPORT, R-FIELD-SETUP) | `box_drop_m` |
| A-D11 | Print bed 0.2 m; thread engagement; claims graph without failing claims | PHYSICAL/DERIVED | carry (R-PROCESS, R-PROOF-BUILD) | |
| A-D12 | Wind measured at the field before each sortie | DERIVED | carry (R-WIND-MEASURE) | `WIND-RFS.md` |

## 6. Dropped from the B set and K09-L

Dropped: B's pusher, boom, wing-joint, gear, Q_ASSIST, parked-prop and pusher-clearance items (QP-P8, P9, P16-P18); K09-L's 1.15 m / 1.25 m box requirement (A-U3 replaces it), fin-tube joint and cartridge-foot items (A has CFRP-skinned foam fins, no cartridge). Open: confirm in the first bench round which of A-P11, A-P13, A-P15 values are met (`—`, not computed for A).
