# Small quadplane: what can be reused (QP-1, A2)

Status `PROPOSED`, 2026-11-14. Verdicts come from opening the files named below (heads, function lists, argument lists, parameter lines), not from `CLAUDE.md`. Nothing was run, so "runs unchanged" means "reads as generic", not "tested". Paths relative to `redesign/` unless they start `../` (repo root). `—` = unknown.
Verdict key: **reuse** (use as is), **adapt** (same structure, change inputs or values), **rewrite** (idea only), **drop**.

**Finding that changes the plan.** The repo root has a parameter set that already is a QuadPlane (4 lift quad X + 1 pusher, same CoreWing F405 Wing V2 board): `../firmware/vtol_c0.param` (207 lines, ArduPlane 4.7.2), with a validator (`../firmware/tools/check_params.py`), a 7-scenario SITL mission test (`../firmware/sitl/mission_test.py`) and a 6-DOF JSON physics model (`../firmware/sitl/c0_physics.py`). It belongs to the older 7.4 kg hybrid concept (C0), so its values do not apply, but its structure is nearer to the quadplane than K09-L's tailsitter file is. `CLAUDE.md` says the older root folders describe that concept: they are reused here as structure only, and the quadplane needs its own `QP.param`.

## 1. Flight software and parameter file

`subsystems/flight-software/K09L.param` has 514 lines, 179 parameter lines, 12 sections. By section:

| K09L.param section | Verdict | What carries / what changes |
|---|---|---|
| 1 Frame (l.24-40): `Q_ENABLE` 1, `Q_FRAME_CLASS` 1, `Q_FRAME_TYPE` 1 (quad X) | adapt | These three lines apply to a quadplane as is. Delete `Q_TAILSIT_ENABLE`, `Q_TAILSIT_MOTMX`; `Q_OPTIONS` 262400 = bit 18 ARMVTOL + bit 8 (assist affects lift motors only): bit 18 carries (arm only in a Q mode, matches `../firmware` 262144); bit 8 is decided in SITL (QP-P9) |
| 2 Outputs (l.41-62) | rewrite | K09-L: motors on outputs 1-4 (bidirectional DShot only works on 1-4 of this board), elevons 5-6. Quadplane needs 4 lift + 1 pusher + ailerons / elevator / rudder: the timer-group map of `../firmware/vtol_c0.param` section 2 (lift S5-8, pusher S9 DShot, surfaces on PWM groups) already solves the group rule ("no servo may share a DShot group"); re-check for the final output count. `SERVO_BLH_BDMASK` 15 for rpm telemetry needs lift motors on 1-4, so decide which outputs get bidirectional DShot (the notch needs it) |
| 2b Elevon throw | drop | no elevons |
| 3 Motor limits (l.92-140) | adapt | `Q_M_SPIN_MAX/MIN`, `Q_M_THST_EXPO`, `Q_M_THST_HOVER`, `Q_M_HOVER_LEARN` 2, `Q_M_BAT_CURR_MAX`, `_TC` 1, `_IDX`, `Q_M_BAT_VOLT_MAX/MIN`, `FWD_BAT_*`, `THR_MAX`: same parameters, **values from QP1-2** (K09-L's 0.81 / 80 A / 17.4 V are X2814 + 6 Ah numbers). `Q_M_PWM_TYPE` 5 (DShot300) carries. `THR_MAX` and `FWD_BAT_*` are the pusher's, not 4 motors |
| 4 Hover (l.141-212): `Q_A_ANGLE_MAX` 30, rate and accel limits, `Q_A_RAT_*`, `Q_WP_SPD_DN` 1.2, `Q_PILOT_SPD_DN` 1.0, `Q_LAND_FINAL_SPD` 0.3, `Q_LAND_FINAL_ALT` 6, weathervane `Q_WVANE_*` | adapt | structure and the descent / landing speeds carry (they match QP-D2 hover segments); **gains `Q_A_RAT_*` do not carry** (K09-L 11 in props, 2.6 kg, 0.08 / 0.002): restart from the quadplane tuning steps (QP-1 SITL, then `QAUTOTUNE`). Weathervane is a K09-L landing-orientation rule (belly into the wind): re-decide |
| 5 Transition (l.213-267): `Q_TAILSIT_*` (7 lines), `Q_TRANSITION_MS` 11667, `Q_A_ANGLE_BOOST` | rewrite | tailsitter pitch-over logic. Replace with `Q_ASSIST_*`, `Q_TRANSITION_MS`, `Q_TRANS_FAIL`, `Q_TRANS_FAIL_ACT`, `Q_TRANS_DECEL`, `Q_BACKTRANS_MS` as in `../firmware/vtol_c0.param` section 6 (structure, with its source keys). K09L.param has `Q_ASSIST_SPEED` 14 at l.250, `_ALT` 0, `_ANGLE` 0: tailsitter values. Precedent from the C0 file: assist 3 m/s below `AIRSPEED_MIN` and stall 12, min 16 (stall + 1). QP-P9 asks Vs + 2; at QP-B (stall 9.6, min 13) the C0 rule gives 10.0, only 0.4 above stall: **conflict, SITL and flight settle it, not picked here** |
| 6 Fixed-wing envelope (l.268-310): `ARSPD_*`, `AIRSPEED_MIN/CRUISE/MAX`, TECS, `PTCH2SRV_*`, `RLL2SRV_*`, `YAW2SRV_*`, `MIXING_GAIN` | adapt | parameter names carry; every value is re-derived (QP-P7, QP-P8, cruise 15 m/s); elevon mixing (`MIXING_GAIN`) drops |
| 7 Yaw by differential thrust (l.311-318) | drop | no tailsitter fixed-wing yaw by thrust |
| 8 IMU filtering (l.319-345): rpm-tracking notch `INS_HNTCH_*` mode 3, `INS_GYRO_FILTER`, `INS_LOG_BAT_*` | adapt | mechanism carries (ESC telemetry notch, batch log for FFT, `INS_LOG_BAT_OPT` 5 needed for QP1-5); frequencies re-set from QP1-2 rpm. The C0 file left the notch off until a hover FFT exists |
| 9 Battery (l.346-384): `BATT_*` | adapt | structure and the "low-with-go-around, critical-for-QRTL" logic carry; capacities and voltages from QP1-3 (4S 3000, 14.8 V, LiPo not LiHV). Sensor scale lines (`BATT_VOLT_MULT`, `BATT_AMP_PERVLT`) are board-and-calibration items |
| 10 RC link and failsafes (l.385-476): `SERIAL6_PROTOCOL` 23 (CRSF), `RC_FS_TIMEOUT` 1.0, `RC*_OPTION`, `FS_*`, `ARMING_*`, `FLTMODE_CH` 6 | reuse | ELRS on UART6 CRSF is the same in the C0 file. `FLTMODE1-6` (17 / 5 / 7 / 18 / 11 / 19) is K09-L's latched Q/FW order (CR-F5-15): quadplane slots chosen anew; C0 uses QSTABILIZE first |
| 11 Geofence (l.477-493): `FENCE_*` | adapt | `FENCE_RADIUS` 250, `FENCE_ALT_MAX` 110: the racetrack far point is 189.7 m at 15 m/s (QP-D2), so 250 holds; RFS limits from H3 |
| 12 Board and sensors (l.494-514): `AHRS_ORIENTATION`, `INS_POS*`, `GPS1_POS*`, `COMPASS_AUTO_ROT`, `SERIAL5_PROTOCOL` | adapt | CoreWing lines are right **only if the flight controller stays CoreWing F405 Wing V2** (K09-L and C0 both use it). The restudy floor prices a SpeedyBee F405 Wing APP instead: if that board is chosen, GPS UART, voltage scale and DShot timer groups are re-derived from its hwdef. Sensor offsets are re-measured on the quadplane (K09-L numbers are fin-frame) |

Other flight-software files:

| File | Verdict | Note |
|---|---|---|
| `K09L-STAND.param` (stand overlay) | adapt | current limiter and rpm logging overlay for QP1-2: new values |
| `team/F4/ap_plane_param_names_4.7.1.txt` (5,725 lines: 5,721 names) and the name check in `team/F4/fsw_check.py` (it reads that file, `NAMES_FILE`) | **reuse** | configuration-independent name list; `fsw_check.py` itself holds K09-L physics (motor map, elevon PWM, tailsitter crossover) and is not reused beyond its name check |
| `../firmware/tools/check_params.py` | **reuse** | validates syntax, names, ranges, bitmasks, and the CoreWing DShot timer groups (`--corewing`) against the ArduPlane metadata; runs against several firmware versions; better than `fsw_check.py` for a new quadplane file |
| `../firmware/sitl/mission_test.py`, `sitl_overrides.param` | **adapt** | seven scripted scenarios (nominal VTOL mission, RC loss in cruise and hover, transition failure, low battery, fence, ELRS MAVLink mode) map to QP1-1 S4, S8; add the motor-out and airspeed-fail cases (QP-P15, S6-S7). Params and thresholds are C0's |
| `../firmware/sitl/c0_physics.py` (JSON physics model, `--validate`) | **adapt** | the only thing in the repo toward SITL stage B (the K09-L plan lists it as not written): reads mass, geometry, AVL derivatives, motor and prop data from `analysis/` and `cad/`; would be re-pointed at QP-B numbers. Effort `—` |
| `subsystems/flight-software/SITL-PLAN.md` (native Windows install) | **reuse** | install steps 1-4 unchanged; model name changes (QP1-1) |
| `subsystems/flight-software/TUNING-PLAN.md`, `SPEC.md` | adapt | tuning ladder idea (one parameter per flight, stop conditions) carries; steps for twin, pitch-over, elevon schedule drop |
| `../firmware/checklists.md`, `peripherals.md` | adapt | bench, pre-flight, failsafe checklists and ESC / ELRS / GPS notes are C0 quadplane-shaped; not opened beyond the index |

## 2. F5: radio setup

| Item | Verdict | Note |
|---|---|---|
| Hardware choice (`team/F5/RC-LINK.md`): RadioMaster Pocket ELRS 2.4 GHz FCC, RP3 V2 receiver, telemetry via CRSF, Mission Planner on USB | **reuse** | the restudy floor prices the same Pocket and RP3 V2 ($89.98 pair, `U`); the C0 package lists the same RP3 V2 |
| Link budget and `rc_link.py` (`fspl_db`, `link_budget`, `range_check`, `antenna_clearance`) | **reuse** | generic free-space and fade maths; 21.6 dB at 515 m is the K09-L result: rerun with the quadplane's antenna placement (150 mm antenna length needs a new check) |
| Range test `RANGE-TEST.md` (`T-F5-RANGE`), template `team/F5/templates/range_log.csv` | **reuse** | steps, pass lines (>= 105 m, LQ >= 0.9, RSSI >= -93.8 dBm at 25 mW) are config-independent |
| EdgeTX model for the K09-L aircraft, mode slots | adapt | channels and mode switch slots re-assigned (QP QSTABILIZE / QLOITER / FBWA / QRTL) |
| `TRANSITION-SWITCH.md`, `transition_switch.py`, `transition_sitl.py`, `results/` | **drop** | the timed override that forces FBWA 0.9 s after a throttle override only exists for the tailsitter pitch-over; a quadplane transitions by mode (FBWA / assist) or `Q_*` logic |

## 3. Harness tooling

| Item | Verdict | Note |
|---|---|---|
| `subsystems/harness/SPEC.md` rules: wire support <= 0.15 m, bend radius, chafe sleeves, strain relief, one pack disconnect, per-ESC XT30U | adapt | rules carry (`wire_support_max_m`); connector choices re-checked for 4S 3000 and about 58 A peak (`EST`) |
| `team/F2/harness.py` (1,600+ lines: wire polylines through fins, pod, groove spec; generates `WIRE-LIST.csv`, `params.json`, `interfaces.json`, claims) | rewrite | the wire router and its `build()` are K09-L geometry (fin grooves, pod floor, fin lead holes); helper functions (`seg_len`, `path_len`, `lengths`, `mass_cg`, `bends`, `free_span`, `mast_clear`, `calc_servo_v`, `calc_cap_ripple`) are generic and can be lifted into a new script |
| `subsystems/harness/WIRE-LIST.csv` (33 rows, 25 electrical edges) | drop | K09-L cut list; its column format (wire_id, edge_id, gauge, conductors, connectors, route, supports, strain relief, mass) is reusable as the quadplane template |
| `team/F1/power.py`, `team/E2/energy_claims.py` (`pack_current`, `hover_bus_w`, `cruise_bus_w`, `budget`, `sag`) | adapt | pack sag, hover and cruise power and mission budget functions are parameterised by mass, prop, table; feed them QP1-2 / QP1-3 results; E2 `pack_log.csv` is the pack template |

## 4. CAD framework

| Item | Verdict | Note |
|---|---|---|
| `fusion/fusionkit.py` (814 lines; `ctx.part / rigid / revolute / wire / contact / keepout_cylinder`; stub and Fusion backends) | **reuse** | its own docstring: configuration-independent |
| `fusion/check.py` (319 lines; module, part, missing, register, touch, transport, floating, keepout checks; `--root DIR`, `--strict`, `--tol-mm`) | **reuse** | run on a quadplane tree with `--root`; its envelope and datum checks apply only to K09-L roots (lines 254-265), so they stay silent. Also needs `interfaces/` (schema, `merge_check.py`, `connection_types.json`) per module |
| `fusion/k09kit.py` (759 lines) | adapt | copy as a `qpkit.py`. **Generic helpers keep:** `val`, `read_dat`, `reflex_placeholder`, `section_loop`, `surface_y/z`, `wing_core` (elevon cut-outs usable for ailerons), `elevon` (as aileron), `spar_y`, `strut`, `bundle`, `box_frame`, `box_shell`, `motor_envelope`, `prop_disc`, `prop_keepout`, `pair`, the `hw_*` fastener parts. **Drop:** `hover_pose`, `to_hover`, `hover_ground` (stand on fin tips), `fin_plate`, `half_fin`, `fin_brace_points`, `foot_contact_z`, `tube_z`, the datum sheet (`datum_specs`, `build_datums`, `datums_md_stale`, K09-L `params.json` keys) and `quad()` (ids UR/UL/LR/LL mirrors). **Add:** boom tube (horizontal), pusher motor + prop disc on the tail, gear |
| `fusion/skeleton/`, `fusion/examples/` (ex_booms, ex_fuselage, ex_wing; `check.py --examples`) | adapt | `ex_booms` and `ex_wing` are the closest starting layout for a twin-boom quadplane |
| `collision/collide.py` (+ `collide_blender.py`, `collide_glb_blender.py`, Blender path in `inputs/SIM-TOOLS.md`) | adapt | mesh-level inside-test is generic, but the script builds its job from `REDESIGN/subsystems` and the K09-L harness params (line 186), and its sweep poses are elevon joints: needs a `--root` option and a pose list for ailerons; flagged `—` effort |
| `showcase/animation/assembly_check.py` (swept-path assembly check) + `assembly_plan.py` (STEPS) | adapt | the motion-finding engine is generic; `assembly_plan.STEPS` and the part-id groups (WNG-, FIN-, PRP-, MEC-) are K09-L's build guide: rewrite the plan, reuse the engine. The report is `ASSEMBLY-CHECK.md` |

## 5. Proof graph

| Item | Verdict | Note |
|---|---|---|
| `proofs/proofkit.py`, `proofs/build_graph.py`, `proofs/SCHEMA.md`, viewer | **reuse** | the README states the tools do not depend on the configuration (demo aircraft in `proofs/examples`); `build_graph.py --root DIR --out DIR` scans a folder for `claims*.json`, so a quadplane graph can live in `qp/` |
| Cautions | | with the default root the graph scans all of `redesign/` and loads `params/params.json` (K09-L numbers; duplicate or conflicting ids are errors in `load`). Use `--root redesign/qp --out redesign/qp/proofs-out` and give each QP claim file its own `params` list (`qp/params/params.json`, to be written; not created here). `proofs/out/graph.json` is K09-L's record and stays untouched |
| K09-L claim files (`team/*/claims.json`, ~hundreds of claims) | drop | no quadplane claim exists; K09-L claims that are pure physics (momentum theory, tube bending, link budget) can be copied as formulas |

## 6. H2 / H3 test cards

| Item | Verdict | Note |
|---|---|---|
| `team/H2/FLIGHT-TEST-PLAN.md` structure: principles (gates in order, one parameter change per flight, never waive), crew roles, before-flight checklist, mission metrics M1a-M2, pilot gate, `logs/` and `templates/flight_log.csv`, `PILOT-LOG.md` | adapt | principles, roles, logging and gate 0 (10 h SITL) carry; **gate 1 twin, 1i transition switch, 1j belly landing, gates 3-4 (stand-on-fin hover, foot landings) are rewritten** to the section 4 programme in `REQUIREMENTS-QP.md` |
| `team/H3/FLIGHT-CARD.md` sections 1 (limits: wind <= 5 m/s, gust <= 8, 07:00-10:00, RFS yellow fields, FRIA) and 4-4b (in-flight, go-around) | adapt | limits carry (QP-P22); section 3 stance and landing rules (wingtip into the wind, belly to wind), section 5 spiral and pitch-rate notes are K09-L and are rewritten; the `COMPLIANCE.md`, `BATTERY-PROCEDURE.md`, `WIND-RFS.md`, `templates/wind_log.csv` carry |
| H1 `GROUND-TEST-PLAN.md` cards | per `TEST-PLAN-QP1.md` | carried cards: GT-01, 02 (adapted), 04, 05, 06, 07, 12, 14, 16, 18; dropped: GT-03, 08-11, 15, 17 |
| H1 `templates/*.csv` (motor_incoming, stand_run, cg, weigh, thermal, load_test, bench_checks) | **reuse** | column sets are config-independent |

## 7. Transport box

| Item | Verdict | Note |
|---|---|---|
| Box: 1.25 x 0.565 x 0.54 m corrugated board, cradles, crush columns (`subsystems/transport/`, `team/D7/transport_calc.py`) | **drop (dimensions) / adapt (method)** | **does not fit:** QP-B span is 1.40 m (EST) against 1.25 m. Whether the wing splits or the box grows is open (D-QP-1). The drop-test method (0.3 m floor drop, crush column stroke, load factor), the 6 kg loaded limit and the field-setup checklist carry |
| `CAR-FIT.md` (measure two cars) | **reuse** | the K09-L results table is still empty ("No car has been measured yet"); the same tape measurement now sets the box length for the quadplane. Do it before D-QP-1 is decided |
| `box_frame`, `box_shell` in `k09kit.py` | adapt | geometry helpers take external size from `params.json` |

## 8. Summary of reuse

- Reuse as is: parameter name list and `check_params.py`; the F5 hardware choice, range test and link-budget maths; H1 templates and the pack / weigh / CG / thermal / tap methods; SITL install; `fusionkit.py`, `check.py`; proof graph tools with `--root`.
- Adapt: parameter structure of K09L.param sections 1, 3, 4, 6, 8-12 (and `../firmware/vtol_c0.param` for section 2 and 5); `k09kit.py` (generic half); harness rules and the generic routing helpers; collision and assembly check engines (need a root option and new part groups); H2 / H3 principles and limits; the energy / power functions.
- Rewrite or drop: tailsitter transition and elevon content, the transition switch, fin / foot / pod CAD and proofs, K09-L claim files, the 1.25 m box dimensions, the K09-L wire list.
- Not checked: whether the `inputs/SIM-TOOLS.md` Blender install still runs on this machine; run time and effort for the collision and assembly adaptations (`—`).
