# params.json change log — K09-L

Owner A1 (chief engineer). One row per decision; `params.json#meta.revision` names the current revision. A decision
changes `params.json` only here; the owning role then re-runs its script so `build_graph.py` shows no drift.
Every change request written so far is dispositioned in the second table (accept / reject / forward with one reason).

| Revision | Date | What | Re-check |
|---|---|---|---|
| A1-R0 | 2026-11-09 | design frame from the config study (chord 0.30, MH 45, tubes at x −0.10, CG 0.060) | — |
| A1-R1 | 2026-11-09 | after the first analysis round: D-01 … D-15 | `python -I redesign/team/A1/frame_claims.py` |
| A1-R2 | 2026-11-09 | change-request round: D-16 … D-23 | same, then `python -I redesign/proofs/build_graph.py` |
| **A1-R3** | 2026-11-09 | detail-analysis round (C2–C6, D2, D3, D5, D7, E3, F1, F3, F4, F5, H1, I1 and the B/E re-runs): D-24 … D-46 | same; A3 re-runs `mass_rollup.py`, B3/B4/B1/E2/E1/C1 re-run on the R3 keys |

## Decisions

| Id | Decision | From | Keys changed | Why (numbers) |
|---|---|---|---|---|
| D-01 | Chord 0.30 → **0.32 m**; cruise 15 → **16 m/s** | CR-B2-01, CR-B1-01, CR-A1-05, CR-A2-07 | `wing.chord_m`, `wing.te_x_m`, `performance.cruise_ms` | trimmed CLmax 0.80 gives Vs 11.86 m/s and 1.3 Vs 15.42 m/s at 2.6 kg (+1 % / +4 %); CLmax ≥ 0.92 is not reachable trimmed; +40 g from the reserve |
| D-02 | Airfoil MH 45 → **S5010** | CR-B2-02 | `wing.airfoil`, `wing.t_c` 0.0982, `performance.clmax` 0.80 (`CL-B2-CLMAX-DESIGN`) | trimmed CLmax +4 %, softer stall, same t/c and process; `ASM-A1-CLMAX` 0.9 superseded |
| D-03 | Spar centre z 0 → **+0.0066 m** (camber line at x 0.080) | CR-B2-03, CR-A5-01 | `wing.spar.z_m` | at z 0 the 22 mm tube breaks the lower skin by 2.9 mm; centred it has 3.7 mm foam each side |
| D-04 | **Motor tubes through the wing core at x = +0.045 m** (B3 option O4b); fin LE on the tube, fin chord 0.275, two half-fins per side, printed through-core block joins tube, spar and core | CR-B3-02, CR-A4-03, CR-A5-03, P25 | `fins.le_x_m`, `fins.chord_m`, `fins.pieces_per_fin`, `fins.tube.x_m`, `fins.saddle`, `propulsion.stations.x_mount_m` 0.045, `x_prop_plane_m` −0.005 | cruise Cn_β −0.105 → +0.044 /rad; tube-to-spar offset 0.18 → 0.035 m; prop-to-tube gap stays 39 mm |
| D-05 | Prop 11×4.5MR → **APC 11×5.5MR/MRP**; 4 × 11×4.5MR kept for the stand A/B | CR-E1-01, CR-B4-01, CR-B4-02, CR-E1-12 | `propulsion.prop`, `prop_mass_kg` 0.017, `thrust_max_per_motor_kg` 1.62 (limiter, fresh pack), `current_max_per_motor_a` 24.8, `thrust_table_g_w` note | −17 % cruise power for +3 % hover power, same price and diameter |
| D-06 | Voltage-sag thrust factor 0.93 → **0.72** (worst state: 20 % charge, 10 °C) | CR-E2-01c | `propulsion.voltage_sag` | T/W with sag at the gate 1.79 ≥ 1.6; E1's warm case 0.86 is the other bound; one worst-state claim to come (E1 + E2) |
| D-07 | **Allocations 2 200 g, A1 reserve 400 g** (wing 405, fins 370, pod 105, landing 40, propulsion 440, power 595, avionics 75, harness 105, mechanisms 65) | CR-A3-01, CR-B2-05, CR-E1-13, CR-A1-04 | `mass.allocation_g.*`, `mass.growth_reserve_g`, `requirements.mtow_sized_kg` 2.55 | A3 bottom-up plus D-01/D-04/D-11 geometry and the 15 g servos; predicted 2 495 g leaves 105 g under the gate |
| D-08 | Pod LE −0.02 → **−0.105 m** (pod spans −0.105 … 0.095) | CR-B3-02/03, CR-A3-02, CR-A5-03 | `pod.x_le_m`, `avionics.pitot_tip_xyz_m` −0.185 | with the motors at 0.045 the pod group moves forward, not aft, to hold the CG near 0.044 |
| D-09 | **3° tangential motor cant** | CR-B3-05, CR-B4-04 | `propulsion.stations.cant_deg` | hover yaw authority / 5 m/s disturbance 1.08 → 3.75; costs 0.14 % of thrust |
| D-10 | **CG range 0.040–0.049 m, target 0.044**; static margin ≥ 5 % kept | CR-B3-01, CR-A1-06 | `cg.x_range_m`, `cg.x_target_m`, `mass_budget.json#cg_x_m` | NP with props 0.0641 m at the R0 geometry; the old aft end 0.075 would be SM −3.6 %. B3 re-derives at R1 (D-17) |
| D-11 | **Feet 45 mm** beyond the TE, crush stroke ≥ 40 mm at η 0.5 (or ≥ 25 mm at η ≥ 0.8); landing allocation 24 → 40 g | CR-C1-01, CR-A4-02, CR-J1-08 | `cg.foot_height_m`, `requirements.foot_crush_stroke_min_m`, `landing_n_design` 6, `mass.allocation_g.landing` | with 10 mm feet a 2.2° roll error lands on the wingtip and n = 23 at 1.5 m/s |
| D-12 | **Two flight packs.** No 4S 4000 fallback; packs 3–4 ($87.37) only if the pessimistic reserve after the December order stays ≥ $309 + $87; test days at 2 sorties until then | CR-E2-01e, CR-E2-05 | `battery.pack` note | 4000 mAh gives 2.3 min pessimistic cruise (< 5); packs 3–4 now would take the reserve to $234 (< one $309 crash) |
| D-13 | **Performance block at the 2.6 kg gate**, conservative value carried where B1/E1/E2 disagree | CR-B1-02, CR-E1-02, CR-E2-01d | `performance.*` (hover 400 W / 27 A, cruise 307 W / 20.7 A, 12.3 min, 6.4 min pessimistic, lean 15 / 34°) | one basis for F1, F4, E2; B1 re-runs with the 11×5.5MR at 16 m/s |
| D-14 | **Limits adopted from A2 (39) and C1 (5)** as `requirements.*` keys | CR-A2-01, CR-C1-06 | `requirements.load_factor_limit_*`, `vd_ms`, `thrust_limit_per_motor_n`, `landing_*`, `box_drop_m`, `crash_decel_g`, `vibration_sep_frac`, … | one source per limit; A2 retires the `ASM-A2-*` duplicates |
| D-15 | Small adoptions: fin height **0.38 m** confirmed; `fins.board_t_m` 0.0048; `battery.size_m` [0.140, 0.048, 0.050] and pod height 0.07; `propulsion.rpm_max` 9 350; pitot on the pod nose; download 1.06 kept; `SRC-X3108S`, `SRC-APC-11X45MR`, `SRC-APC-11X55MR`, `SRC-S5010` checked; `SRC-LANRC-45A`, `SRC-OVONIC-4S6500` stay unchecked | CR-A2-02, CR-A5-05, CR-E2-01a/b, CR-E2-02, CR-B4-02, CR-B4-05, CR-A4-07, CR-E1-03 | as listed | numbers their owners produced; the pack is weighed before its source is marked checked |
| **D-16** | **Transport box 0.45 → 0.50 m high** (external 1.25 × 0.55 × 0.50) | `CL-A1-BOX-FIT` −25 mm, CR-A4-02 | `requirements.box_external_m` | the tube ends (±0.21 m) set a 0.425 m envelope; with 25 mm walls a 0.45 box is 25 mm short, a 0.50 box has 25 mm slack. D7 measures two cars before freezing; fallback 0.48 m with 12 mm lining |
| **D-17** | **Hold the pod at −0.105 m; no further layout move until B3 re-derives the CG range at R1 geometry** (c 0.32, S5010, tube at 0.045, 3° cant). Until then A3 carries the pack 29 mm forward of the pod centre (CG 0.044 on the R0 range). If the re-derived aft limit is < 0.051 m, A1 moves the pod to −0.125 | CR-A3-02, CR-B3-03, CR-A5-03, `CL-A3-CG-X-RANGE` | `cg._note`, `pod.x_le_m` note | A3 roll-up (basic, pack centred) 0.051 m is 2 mm aft of a range derived at the old NP; tubes and props at 0.045 and the longer chord both move the NP aft, so moving geometry twice would be waste |
| **D-18** | **Hover pitch-trim split limit 1.25** (`requirements.hover_split_max`) | CR-B3-10, CR-A3-04 | new key | B3: the 1.19 split uses 9.7 % of the pitch differential against 12.5 % allowed; no tube offset or pack recess |
| **D-19** | **Static margin stays 0.05**; CR-J1-02's 0.03 rejected | CR-J1-02, CR-B3-01 | — | B2's trimmed CLmax 0.80 already pays the elevon up-trim at SM 5 %; B3 keeps 5 % as the aft limit |
| **D-20** | **Joint ownership rules:** elevon hinge is owned by `wing` (D6 designs); ESC power leads by `harness` only (`power` owns the boxes); electrical `part_a` = supply side | CR-A4-01 | README joint table | an owner must hold one side of its edge; no edge under two owners |
| **D-21** | **CR-B3-07 superseded:** cruise stays 16 m/s; `ARSPD_FBW_MIN` comes from B3's trimmed stall at R1 geometry, not the 16.6 m/s derived at c 0.30 / MH 45 | CR-B3-07 | — | at c 0.32 and S5010 (trimmed CLmax 0.80) 1.3 Vs = 15.42 m/s; B3's 12.73 m/s stall was the R0 wing |
| **D-22** | **Box drop 0.3 m stays**; D7 puts ≥ 70 mm crush foam under the spar cradles (or a cradle under the pod with ≥ 55 mm); 1.5 m/s sink stays | CR-C1-05, CR-C1-10 | `requirements.box_drop_m` note | the cradle sits inside the 0.21 m the lower tubes need anyway, so the foam costs no box height; a 0.087 m label limit is not credible for students |
| **D-23** | **Mounts are the fuse:** printed motor mounts and props fail before the tube and the through-core block in a tip-over; carry point on the pod/spar with a "do not lift by the motors" label, and C4 still sizes the fin joint to case G2 (10.7 N·m) | CR-C1-03, CR-C1-04 | `fins.saddle` note (unchanged) | 3.5 J tip-over cannot be bumpered; students will lift by the tubes anyway |

### Revision A1-R3 (detail-analysis round)

| Id | Decision | From | Keys changed | Why (numbers) |
|---|---|---|---|---|
| **D-24** | **CG range at R1 geometry: 0.050–0.055 m, target 0.0526 m; the pod stays at the D-08 layout; D-17 closed.** A3 sets the pack nominal centroid to x = −0.001 m (4 mm aft of the old pod centre); the −0.125 m fallback, `CALC-A1-POD-RULE` and `ASM-A1-POD-*` are retired; replaced by `CALC-A1-CG-RANGE` (params range inside B3's claims, pack-centred CG +1.5 mm from the forward end) | CR-B3-11; supersedes CR-A3-11, CR-A5-11, CR-D2-02, CR-A1-22/23/24 | `cg.x_range_m`, `cg.x_target_m`, `cg._note`, `pod.x_le_m` note, `mass_budget.json#cg_x_m` | NP with props and pod 0.0713 m; forward limit from elevon trim ≤ 12.5° at CLmax (`CL-B3-CG-FWD` 0.0499), aft from SM 5 % (`CL-B3-CG-AFT` 0.0553); pack-centred CG 0.0515 is inside; the pod at −0.125 would be 5.5 mm ahead of the forward limit. B3 re-runs once for D-26/D-27 |
| **D-25** | **Pod nose shell to −0.115 m with an XPS crush block; pod 0.21 × 0.14 × 0.07 m; pitot tip [−0.195, −0.046, 0.045]; pod allocation 122 g.** Tray, hatch and bay forward stop (x −0.1002) unchanged; the 3 mm printed forward stop is the spreader backstop; D2 re-lays the bay so the pack aft face reaches x 0.069 (0.073 with a 680 g pack); CR-C3-02 (−0.108) void | CR-C5-02, CR-C3-06, CR-C3-03, CR-D2-01, CR-D2-03, CR-C3-01 | `pod.x_le_m`, `pod.size_m`, `avionics.pitot_tip_xyz_m`, `mass.allocation_g.pod` | ≥ 24.3 mm of crush holds any 503–680 g pack to ≤ 100 g in a 5 m/s nose-in crash (`CL-C5-PACK-NOSE-ROOM` fails by 5 mm today); a 0.10 m pod cannot hold the 52 mm bay and the FC side by side (+3 % drag, B1 re-runs); at y 0 the pitot socket sits in the pack; C3 stops + guides 9.5 g |
| **D-26** | **Fins: two board layers (one layer rejected), half-fins 0.21 m high, tube 0.344 m, fins allocation 408 g, half-fin ids `FIN-001-UR/UL/LR/LL`** | CR-C4-14 (over CR-D3-02), CR-B3-14, CR-C4-20, CR-D3-01, CR-C4-15, CR-A4-15b, CR-A5-15 (over CR-D3-08) | `fins.layers` note, `fins.half_height_m`, `fins.tube.length_m`, `fins.saddle`, `fins.pieces_per_fin` note, `propulsion.stations.z_m` note, `mass.allocation_g.fins` | one-layer station mode 228 Hz is 14 % from cruise 2P (`CL-C4-D3-SEP-1L` 0.14 FAIL; two layers 0.41); Cn_β at the aft limit 0.0286 → 0.0373 /rad with 0.21 m fins (R-DIRECTIONAL ≥ 0.03), +6 g, envelope unchanged; the shorter tube lets the motor screws be reached from behind the plate (−7.8 g per tube; C4 mount stiffness ≥ 900 N·m/rad); D3 CAD 364.5 + 37.5 g second layer = 402 g; one suffix family per part (README rule) |
| **D-27** | **Motor cant 3° → 7°**, same sense (UR + LL print A, UL + LR print B) | CR-B3-12; A2's 30 % differential cap kept | `propulsion.stations.cant_deg` | 3° gives hover yaw 1.15 × the 5 m/s disturbance and 1.15 rad/s² against 1.5 × and 2 rad/s² (`CL-B3-HOVER-YAW-RATIO/ACCEL` FAIL); 6.1° needed, 7° gives 2.23 × / 2.24 rad/s² for 0.75 % thrust. B4 re-runs swirl recovery; D3 changes one print parameter; C4/C6 check the 12 % side component on the mount |
| **D-28** | **Prop plane x −0.0082 m, motor plate face x 0.0309 m** (D3's CAD stack carried over E1's −0.0033); the tube front face stays at 0.034; D3 and E1 freeze the stack on the measured motor | CR-D3-04 (over CR-E1-16), CR-E1-16 | `propulsion.stations.x_prop_plane_m`, `x_mount_m` note | the 2 mm collar wall sits ahead of the tube, so the plate moves 3 mm forward to keep ≥ 39 mm (0.14 D, B4) from the prop plane to any structure (`CL-D3-PROP-GAP` 1.02); E1's stack 37.3 mm would put the plane at −0.0064 |
| **D-29** | **Loads: n⁺ 3.4, VD 27.2 m/s, thrust limit 21.1 N per motor; elevon deflection schedule (full travel to VA 20.5 m/s, ≤ 1/3 at VD) enforced by F4; servo ≥ 3.93 kgf·cm** | CR-C1-16, CR-C1-13, CR-C1-12, CR-H1-01, CR-F4-07, CR-C1-15, CR-B2-10 | `requirements.load_factor_limit_pos`, `vd_ms`, `thrust_limit_per_motor_n` | gust n 3.36 at VH 21.8 m/s; VD = 1.25 × the 11×5.5MR pitch speed at the 9 350 rpm cap; `CL-C1-T-CAP` 21.08 N (the 100 A limiter is time-filtered and does not bound a step); F4 keeps the cap rather than lowering it to 8 590 rpm; spar and fin joints are landing-governed, mounts and motors +18 %; hinge moment at VD would need 5.9 kgf·cm, the schedule keeps B2's 3.93 at 1.3 × cruise |
| **D-30** | **Feet 48 mm, constant-force cartridge stroke ≥ 38 mm with biased plateaus; landing 43 g; tip-over ≥ 30° toward the pod side at the worst flying CG with the pad contact at z ±0.218 and z_cg subtracted; the 33° target (CR-A1-20) retired** | CR-C5-10, CR-C5-11 (over CR-C1-17's 41 / 26 mm), CR-C5-01, CR-D5-01, CR-D5-06 | `cg.foot_height_m`, `requirements.foot_crush_stroke_min_m`, `tipover_min_deg` note, `mass.allocation_g.landing`, `CALC-A1-TIPOVER` | C5's planar model: the 17 mm z_cg pitches a level landing onto the pod-side pair and a pair-first touchdown lands the second pair harder (today 32.8 mm needed vs 29 usable, FAIL); 38 mm gives 34.5 of 35 mm, n 5.84 / 5.54; 48 mm keeps the TE ≥ 10 mm off the ground after the stroke; tip-over 32.4° worst flying CG, 30.6° corner bound (`CL-A1-TIPOVER`), 28.3–29.2° unsplayed (FAIL) |
| **D-31** | **Transport box 1.25 × 0.55 × 0.54 m (`PROPOSED`, freeze after two measured cars; fallback 0.50 m with a "max drop 0.15 m" label); box 3.63 kg; packs in the LiPo bag; envelope [1.15, 0.483, 0.438]; D-22's "costs no box height" corrected** | CR-D7-01, CR-D7-07, CR-D5-01, CR-A2-18 | `requirements.box_external_m`, `box_wall_m` note, `box_drop_m` note, `box_mass_max_kg` note, `mass.transport_box_kg`, `transport.envelope_props_off_m`, `transport.cradle` | in a floor drop the aircraft sinks by the ~70 mm cradle stroke, so the lower tube ends and pads need that travel above the floor: height needed 0.535 m (`CL-D7-BOX-H-REQ`); the 0.50 box allows a 0.18 m drop (`CL-D7-A1-BOX-DROP-ALLOW` −42 %); loaded 5.90 kg without packs, 7.00 with |
| **D-32** | **Main disconnect Amass AS150U, packs re-terminated (XT60 rejected); `electrical.r_ext_mohm` 6.5; UBEC fitted with a 5 A fuse; power allocation 620 g.** Closes CR-A2-08, CR-A4-09, CR-J1-04 | CR-F1-02, CR-F1-03, CR-F3-04, CR-F1-14 | `electrical.main_disconnect`, `electrical.r_ext_mohm`, `battery.pack`, `mass.allocation_g.power` | required 37.8 A continuous (1.25 × 30.3 A) and 53.7 A ≤ 60 s; XT60 35 A fails and has no cited rating ≥ 120 A momentary; AS150U 70 / 140 A (reseller: F1 opens the maker sheet before the order); FC servo BEC 4.5 A < 5.2 A needed; power excluding the pack 69 g vs 45 carried; pack leads ≥ 10 AWG (12 AWG rises 28 °C) |
| **D-33** | **Avionics: CoreWing F405 Wing APP V2 (Plane 4.7.x stable, target CoreWingF405WingV2); MS4525DO airspeed at 0x28 (MS5525 dropped); HGLRC M100-5883 on a 45°-tilted mast pad; telemetry over ELRS (no radio); RC FCC firmware; avionics 80 g; `requirements.rc_rssi_check_min_dbm` −93.8; range check at 25 mW** | CR-F3-01, CR-F3-03, CR-F5-06, CR-F5-07, CR-F5-05 | `avionics.flight_controller`, `airspeed`, `gps`, `rc`, `telemetry`, `requirements.range_check_min_m` note, `rc_rssi_check_min_dbm`, `mass.allocation_g.avionics` | stable tailsitter build checked on firmware.ardupilot.org; the MS5525's 0x76 clashes with the board baro on the only I²C bus; a level patch faces the horizon in hover; 78.5 g vs 75 (the FC's 40 g includes its power board, carried at 0 g in power); no Lua on any F405; a SiK pair only if the reserve later allows |
| **D-34** | **Propulsion allocation 476 g; motor screws stay in `propulsion`; `propulsion.motor_max_a` 25 A, `esc_burst_a` 55 A added** | CR-E1-14, CR-A2-12b | `mass.allocation_g.propulsion`, `propulsion.motor_max_a`, `propulsion.esc_burst_a` | per station: motor 81.0 with leads, ESC 11.0 with leads and heat-shrink, prop 17, adapter + nut + washer 6.7, screws 3.2 = 118.9 g (`CL-E1-MASS-PRP` 475.6 FAIL at 440); E1's limiter claims cite parameters, not typed ratings (CR-A2-13) |
| **D-35** | **Voltage-sag thrust factor 0.72 → 0.76** (E2's limiter-consistent value); E1's 0.854 (`CL-E1-TW-WORST` 2.18) is the other bound; E1 and E2 publish one worst-state claim and the cold-pack stand run decides | CR-E2-12, CR-E1-15 | `propulsion.voltage_sag`, `CL-A1-HOVER-TW-SAG` note | T/W with sag at the gate 1.89 ≥ 1.6; E2 applied (V/14.8)² to an already current-limited thrust (E1: with the limiter binding thrust ∝ V), so 0.72 double-counted; the lower of the two reconciled numbers is carried (D-13 rule). F4's 12 °/s pitch-over rate (CR-B1-12) was derived at 0.72: B1 re-checks at 0.76 |
| **D-36** | **Performance block from B1 rev 2 (16 m/s, 11×5.5MR): cruise 218 W / 14.7 A (pessimistic 285 W / 19.3 A), L/D 6.9, cruise after hover 13.7 min (E2 mission base; B1 17.0), pessimistic 7.3 (E2 re-run; B1 12.7), hover-only 11.9, lean 16 / 36°, transition 15.6 m/s (B3 `CL-B3-VT-TRIM` at the forward CG limit), stall 11.9.** E1's 247 W not carried (reads the old L/D 5.6) | CR-B1-10, CR-B3-15, CR-E2-12, CR-E1-19 (part), CR-B1-11 | `performance.*` | the 13.7 / 7.3 min are `build_graph.py`'s re-run of E2's `CALC-E2-BUDGET-*` on B1's `CL-B1-CRUISE-P` 216.9 / 283.4 W (E2 publishes, CR-E2-11); `AIRSPEED_MIN` 15.6 (F4; 15 holds only if Vs ≤ 12.5); B1 re-runs for the 0.14 m pod (+3 % drag) |
| **D-37** | **Airspeed error allowance 1.0 → 0.5 m/s**; cruise stays 16 m/s (B1's 16.5 m/s alternative not taken) | CR-B1-13, CR-F3-09 | `requirements.airspeed_err_max_ms` | margin from cruise down to 1.3 Vs is 0.49–0.58 m/s; F3's RSS budget 0.44 m/s after `ARSPD_AUTOCAL` and reciprocal legs; 16.5 m/s would cost 15 W and 1.1 min |
| **D-38** | **Mass allocations 2 324 g (wing 405, fins 408, pod 122, landing 43, propulsion 476, power 620, avionics 80, harness 105, mechanisms 65); A1 reserve 276 g; growth allowance 250 → 170 g; sized 2.59 kg.** A3 re-runs the roll-up on these allocations; the gate rests on A3's maturity growth ≤ 170 g and the pack weigh-in | CR-C4-15, CR-C3-03, CR-C5-11, CR-E1-14, CR-F1-02, CR-F3-01, CR-A3-12, CR-C2-06, CR-D5-06 | `mass.allocation_g.*`, `mass.growth_reserve_g`, `requirements.growth_allowance_kg`, `mtow_sized_kg`, `mass_budget.json` | six allocations raised to the designers' own numbers (+124 g); the flat 250 g allowance double-counted growth on CAD and datasheet masses; `CL-A1-MASS-SIZED` 2.594 kg (+0 %), `CL-A1-RESERVE-COVERS` +6 g: thin. A1 rough prediction with A3's factors: ≈ 2 450 g with a 550 g pack, ≈ 2 580 g with 680 g, before the 100 g overrun. Levers: Tekko32 ESCs −21 g, aluminium nuts −4 g, pack ≤ 550 g; the one-layer fin (−40 g) is rejected (D-26) and 18 AWG leads (−18 g) by F1 |
| **D-39** | **Budget: ground-test equipment counts against the $2 000; cost keys from I1's BOM (spend 1 569.03 / 1 680.35, reserve 319.65); lever order for any new line: gate the Small Parts adapter set (X05, $26.40), SpeedyBee FC (+$21.25), defer the airspeed sensor last (+$66.14)** | CR-H1-02, CR-I1-02, CR-I1-03, CR-E1-20 | `cost.*` | the pessimistic margin to the $309 crash is $10.65; H1's rigs ≈ $160–180 `EST` cannot all be bought: borrow from Jacobs Hall, buy ≤ $20 (load cell); the adapter set is out of stock anyway and E1's fallback (motor-box adapters + Loctite) is accepted; expected reserve ≈ $326 |
| **D-40** | **Field kit: one 10 mm prop spanner is the single allowed tool** (R-FIELD-SETUP "no tools" re-worded by A2) | CR-C6-05, CR-D7-05 | `requirements.field_setup_max_min` note, `transport.field_steps` | the M6 prop nut at 1.5 N·m is the only field joint needing a tool; a tool-free prop retention is not worth inventing (4 × 35 s of a 265 s set-up) |
| **D-41** | **Thread engagement per type: 1.0 d metal, 1.5 d heat-set insert, 2.0 d self-tapping plastic, nyloc + 2 pitches** | CR-C6-06 | `requirements.thread_engagement_min` note, `thread_engagement_insert_min`, `thread_engagement_plastic_min`, `nyloc_pitches_min` | A2 (1.0 d in an insert) and SCHEMA (1.5 d) disagreed |
| **D-42** | **Thermal keys: `env.ambient_ceiling_c` 43, `pack_takeoff_max_c` 34, `full_throttle_max_s` 10; motor mounts and ESC pads printed in ASA (PETG 58 °C limit fails by 8 K)** | CR-E3-07, CR-E3-01, CR-E3-04, CR-E3-05 | `env.*`, `fins.saddle` note | motor base 65.8 °C mission / 66.4 steady hover; ESC pad 61.6 °C; from a hover-warm motor full throttle is thermally limited to ~13 s (E1's "≤ 30 s" is not available); the PETG collar would relax the D-23 slip-torque preload |
| **D-43** | **Spar stays 22 × 20 mm at z +0.0066 m** (CR-B2-09's +0.0070 and the 16 × 14 trade rejected) | CR-B2-09, CR-C2-10 | — | cover 5.0 / 4.3 mm already passes ≥ 2 mm (`CL-A5-SPAR-COVER`); C2 sized the slot and plugs at 0.0066; a 16 × 14 spar saves 29 g but costs 26 % of the first torsion frequency and needs separate stock |
| **D-44** | **`R-STALL` is judged over the R3 CG range** (0.050–0.055): B2 re-runs `CL-B2-STALL-GATE-FWD` at 0.050 (B3: 11.93 m/s there); the SM-7.8 % case at 0.040 is void | CR-B2-11 (closed by D-24) | `performance.stall_ms` note | at the old forward limit the stall was 12.06 m/s (−0.5 %); the new forward limit is set by elevon trim, not SM, and sits 10 mm further aft |
| **D-45** | **Wing modes close by the tap-test branch of `R-VIBRATION` plus the rpm-tracking notch;** B3 adds the 12–15 Hz antisymmetric torsion mode to the hover loop model; F4 keeps the rate-loop crossover ≤ 5 Hz | CR-C2-03, CR-C2-04, CR-C4-06 | — (A2 words it) | no spar between 16 and 25 mm clears the ±20 % windows over the E uncertainty (`CL-C2-WING-MODE-SEP` 0.077 FAIL); fin/tube modes are C4's `CL-C4-D3-SEP` 0.41 (supersedes `CL-J1-TUBE-MODE-SEP`) |
| **D-46** | **Shared tooling: A4 is assigned the `redesign/interfaces/` changes** (19 plan connection types; `merge_check.py`: harness-owned electrical edges exempt from the `owner` warning, non-structural types skipped in the floating check, power wires followed `part_a` → `part_b`); A5 re-runs `fusion/tests` and `check.py` after | CR-A4-15a, CR-A5-10a | — | `merge_check.py --strict` cannot pass at a gate while 23 wires warn `owner`; `check.py`, `build_all.py` and the Blender backend import the module |

## Change-request dispositions

`accept` = adopted in `params.json` or README; `forward` = not A1's to decide, A1's position given, the named role acts;
`reject` = not adopted; `closed` = already answered by another row. One line each; evidence is the requester's file.

### To A1

| CR | From | Decision | Reason |
|---|---|---|---|
| CR-A2-01 | A2 | accept (D-14) | 39 limits are `requirements.*` keys; A2 retires `ASM-A2-*` |
| CR-A2-02 | A2 | accept (D-15) | fin height 0.38 m; P6's 0.40 was the old fin chord |
| CR-A2-03 | A2 | closed | CR-A1-09 closed; CR-A4-13 and CR-J1-09 are answered by A2's `R-NO-FLOATING`, `R-DIRECTIONAL`, `R-VIBRATION` |
| CR-A3-01 | A3 | accept with changes (D-07) | A3's 2 185 g plus D-01/D-04/D-11 geometry and 15 g servos = 2 200 g; reserve 400 g |
| CR-A3-02 | A3 | superseded (D-04, D-08, D-17) | with the motors at 0.045 the pod moved forward 85 mm, not aft |
| CR-A4-01 | A4 | accept (D-20) | README joint table rewritten |
| CR-A4-02 | A4 | accept (D-11, D-16) | feet 45 mm; box 0.50 m |
| CR-A5-01 | A5 | accept as B2's value (D-03) | 0.0066 m on the S5010 camber line, not the 0.0048 placeholder |
| CR-A5-03 | A5 | closed (D-04, D-08, D-10, D-17) | layout CG now 0.051 (A3) against 0.040–0.049; B3 re-derives the range |
| CR-A5-05 | A5 | accept (D-15) | `fins.board_t_m` 0.0048 |
| CR-A5-08 | A5 | accept, assigned to the team lead | a teammate with Fusion runs BuildAll on the skeleton; listed in HANDOFF |
| CR-B1-01 | B1 | accept (D-01) | cruise 16 m/s |
| CR-B1-02 | B1 | accept in part (D-13) | B1's values carried where they are the conservative ones; B1 re-runs with the 11×5.5MR |
| CR-B2-01 | B2 | accept (D-01) | chord 0.32 m, cruise 16 m/s; gate mass unchanged |
| CR-B2-02 | B2 | accept (D-02) | S5010 |
| CR-B2-03 | B2 | accept (D-03) | spar z 0.0066 m |
| CR-B3-01 | B3 | accept (D-10) | CG range 0.040–0.049, SM 0.05, elevons unchanged |
| CR-B3-02 | B3 | accept O4b (D-04) | tube at 0.045 through the core; fallback O7 not needed |
| CR-B3-05 | B3 | accept (D-09) | 3° cant |
| CR-B3-07 | B3 | superseded (D-21) | re-run at R1 geometry before any cruise-speed change |
| CR-B4-02 | B4 | accept (D-05, D-15) | prop, rpm_max, pitot, download 1.06 kept, APC source checked |
| CR-C1-01 | C1 | accept (D-11) | feet 45 mm, stroke ≥ 40 mm |
| CR-C1-06 | C1 | accept (D-14) | five load limits are `requirements.*` keys |
| CR-E1-01 | E1 | accept with changes (D-05, D-06) | prop and 24.8 A adopted; `thrust_max` carried as 1.62 kg (fresh, limited) with sag 0.72 from E2 instead of 1.48 kg |
| CR-E1-02 | E1 | accept (D-13) | hover 400 W / 27 A; cruise carried at B1's 307 W until B1 re-runs |
| CR-E1-03 | E1 | accept (D-15) | sources marked as E1 reported; LANRC stays unchecked |
| CR-E2-01 | E2 | accept (D-06, D-12, D-13, D-15) | pack envelope, sag 0.72, pessimistic 6.4 min, no 4000 fallback; mass stays `UNVERIFIED` |
| CR-E2-05 | E2 | defer (D-12) | packs 3–4 only if the post-order reserve is ≥ $396; 2 sorties per test day |
| CR-J1-02 | J1 | reject (D-19) | SM stays 0.05; the up-trim penalty is inside B2's trimmed CLmax |

### Forwarded (A1's position; the named role acts)

| CR | To | Decision | Reason |
|---|---|---|---|
| CR-A1-01 | A5 | closed | `fusion/modules.txt` rewritten |
| CR-A1-02 | A4 | open | the six queued `interfaces/` changes; apply D-20 and CR-A3-09, CR-A5-04 in the same pass |
| CR-A1-03 | J4 / viewer | open | prefix → hue map |
| CR-A1-04 … 09 | A3, B1/B2, B3, E1, E2, A2 | closed | D-07, D-01, D-10, D-15, D-15, A2's P-map |
| CR-A2-04 | A3 | forward | point the CG claims at `R-CG-RANGE`, `CL-A3-ALLOC-WORST` at `R-MASS-ALLOC` |
| CR-A2-05 | A4 | forward | `R-NO-FLOATING`, `R-JOINT-STACK` |
| CR-A2-06 | J1 | forward | `R-VIBRATION`, `R-DIRECTIONAL`; re-run after R1 (six calcs drift today) |
| CR-A2-07 | B1, B2 | closed by D-01 | B2 re-runs `CL-B2-STALL-GATE` at c 0.32; B1 the 8 m/s lean is already at the gate |
| CR-A2-08, CR-A4-09, CR-J1-04 | F1 | forward | A1 accepts XT60 only with a claim that the ≤ 5 s momentary case at the 100 A limiter is inside a cited XT60 burst rating; otherwise AS150U. UBEC: F1 decides on the FC's BEC rating × 2 |
| CR-A2-09 | C1 | closed | `team/C1/LOADS.md` exists; C1 re-runs at R1 |
| CR-A2-10 | H1, H2, H3 | forward | use A2's file names |
| CR-A2-11 | J2 | forward, optional | `--requirements` filter |
| CR-A3-03 | B3 | forward (D-17) | NP with props at R1 geometry is B3's first job |
| CR-A3-04, CR-B3-10 | A3, B3, F4 | accept (D-18) | split 1.25; A3 points `ASM-A3-SPLIT-MAX` at `P:requirements.hover_split_max` |
| CR-A3-05, CR-E1-13 | E1 | forward | propulsion allocation stays 440 g; E1 writes `parts.csv` with per-unit masses incl. leads |
| CR-A3-06 | F1, F2 | forward | 18 AWG if 30 A momentary on 0.5 m passes `wire_temp_rise_max_c`; `team/F2/mass_estimate.csv` |
| CR-A3-07 | D2 | forward | pod carries mast and pitot mount; pack low |
| CR-A3-08 | E2 | forward | weigh one pack in the November order first |
| CR-A3-09 | A4, A5 | accept | per-unit `mass_g`, one node per instance `<id>-<UR|UL|LR|LL|L|R>`; rule written into README; A4 puts it in SCHEMA.md |
| CR-A3-10 | C5 | forward | tip-over at the R1 CG is 30.6° (A1) — thin; D5 splays the feet (see D-11 note) |
| CR-A4-03 | D3, D1, C4 | closed (D-04) | half-fins, tube through a core hole, printed through-core block |
| CR-A4-04 | D6, D3, B3 | forward | both panels stay (B3); D6/D3 slot the lower half-fin root for the link |
| CR-A4-05 | F2, D1 | forward | wire channel aft of the spar (x > 0.095) or through the through-core block |
| CR-A4-06 | E1, E3 | forward | bolt pattern, screw length, adapter; PETG mount temperature |
| CR-A4-07, CR-B4-05 | D2, F3 | accept (D-15) | pitot on the pod nose, tip at x −0.185 |
| CR-A4-08 | F3, F5 | forward | I2C 0x76 clash, compass distance, antennas |
| CR-A4-10 | C6, C4 | forward | 19 joint stacks + 8 clamps, M2/M3 only |
| CR-A4-11 | A5 | forward | transport touch checks, harness bodies, thermal contact |
| CR-A4-12 | F4 | forward | ports from `signal.fc_port`; publish the motor map |
| CR-A4-13, CR-J1-09, CR-B3-08 | A2 | closed | `R-NO-FLOATING`, `R-DIRECTIONAL`, `R-VIBRATION`, `R-HOVER-AUTHORITY` exist |
| CR-A4-14 | all designers | forward | use the register ids |
| CR-A5-02, CR-B2-04 | B2 → D1, A5 | accept | copy `team/B2/airfoils/s5010.dat` to `subsystems/wing/s5010.dat` (D1) |
| CR-A5-04 | A4 | forward | SCHEMA.md frame text → `params.json#frame`; `9xx` ids reserved |
| CR-A5-06 | E1 | forward | prop hub thickness, shaft + adapter length |
| CR-A5-07 | designers | forward, endorsed | start from `fusion/skeleton/<key>/` |
| CR-A5-09 | J3 | forward | `k09kit.hover_pose()` for renders |
| CR-B1-03, CR-B2-08 | B2 → B1 | closed | B2 answered; B1 re-runs |
| CR-B1-04, CR-B3-07 | B3 → B1 | forward | CLα 3.56, e 0.93 (R0); B3 re-derives at R1 first |
| CR-B1-05, CR-B4-08 | B4 → B1 | closed | 11×5.5MR η 0.474; B1 re-runs |
| CR-B1-06, CR-C1-07, CR-E1-11, CR-B4-09, CR-E2-09, CR-B3-09, CR-B1-09 | H1, H2 | forward | one stand campaign: Rm/I0, A/B props, fresh-pack peak thrust and torque, pack weigh/capacity/IR; flight tests as listed |
| CR-B1-07, CR-B3-04, CR-B4-06, CR-C1-08, CR-E1-08, CR-E2-03, CR-J1-05, CR-A4-12 | F4 | forward | one parameter file; the list is in `team/A1/SUMMARY.md` |
| CR-B1-08, CR-E1-09, CR-E2-04 | F1 | forward | design currents: hover 29.9 A, climb 30.2 A, transition 42.9 A (20 s), limited peak 100 A, momentary 120 A (< 5 s) |
| CR-B2-05 | D6, A3 | accept (D-07) | servo ≥ 3.04 kgf·cm; mechanisms 65 g |
| CR-B2-06, CR-B3-06 | B3, B2 | closed | B2 answered with `CL-B2-ELEVON-ETA`, `CL-B2-DCM-VISC` |
| CR-B2-07, CR-C1-09 | C1 | forward | replace the guesses with B2 claims and `loads_spanwise.json` |
| CR-B3-03 | A3, D2 | superseded (D-08, D-17) | — |
| CR-B4-01, CR-E1-06 | E1, B4 | closed (D-05) | concur |
| CR-B4-03, CR-E1-04 | B3 | forward | hover authority with fin swirl recovery and cant; motor-out roll 0.22 N·m |
| CR-B4-04, CR-C1-03 | D3 | accept (D-09, D-23) | canted mounts; tube face ≥ 39 mm behind the prop plane; mounts as the fuse |
| CR-B4-07, CR-J1-03 | C4 | forward, first job | fin + tube modes outside 80–330 Hz; `CL-J1-TUBE-MODE-SEP` fails today |
| CR-B4-10, CR-E1-10, CR-E2-07 | E3 | forward | ESC pads in the slipstream, motor losses, pack heat path |
| CR-B4-11, CR-E1-12, CR-J1-07 | I1 | accept | props 8 + 4 (+ optional 11×5.5E pair), US-stock tube in the ~20 Nov order |
| CR-C1-02 | H3, C5 | forward | flight card: lay flat between flights above 5 m/s; rubber foot pads |
| CR-C1-04 | D2, D7, H3, C4 | accept (D-23) | carry point and label, and C4 sizes to G2 |
| CR-C1-05 | D7 | accept (D-22) | ≥ 70 mm crush foam under the cradles |
| CR-C1-10 | A2 | closed (D-11, D-22) | both requirement numbers kept |
| CR-C1-11 | C6 | forward | mount clamp sized to the 3.2 N·m prop-nut case |
| CR-E1-05, CR-E2-08 | B1 | forward | re-run with 11×5.5MR 216 W (E1) / 181 W (B4) and feed E2 |
| CR-E1-07 | A2 | forward, concur | rewrite `R-ESC-CURRENT` around the 100 A limiter |
| CR-E2-02 | D2 | accept (D-15) | bay ≥ 0.160 × 0.052 × 0.053 m; pod height 0.07 |
| CR-E2-06 | H3 | forward | charging room, pack ≥ 20 °C at take-off |
| CR-E2-10 | I2 | forward (D-12) | 2 sorties per test day |
| CR-J1-01 | B3 | closed (D-04) | — |
| CR-J1-06 | B4, B1 | closed (D-05) | — |
| CR-J1-08 | C5, C1 | closed (D-11) | C1's case supersedes the 10 mm stroke |

## Change-request dispositions, revision A1-R3 (detail-analysis round)

Same rules. Requests from the first round that were dispositioned above are not repeated; C4's and C5's first-round
requests (never logged) are included.

### To A1

| CR | From | Decision | Reason |
|---|---|---|---|
| CR-A2-12 | A2 | accept (D-34) | (a) `R-TRANSPORT` text now reads `requirements.box_external_m` (A1 edits `params/claims.json`); (b) `propulsion.motor_max_a` 25, `esc_burst_a` 55 added; (c) CR-A1-17 closed |
| CR-A3-11 | A3 | superseded (D-24) | the pack goes 4 mm aft of the pod centre, not 26–29 mm forward; the nose-wall problem disappears |
| CR-A3-12 | A3 | accept (D-26, D-38) | one-layer fin rejected by C4; fins 408 and power 620 g allocated from the reserve; the pack weigh-in decides the gate |
| CR-A4-15 | A4 | accept (D-46, D-26) | (a) A4 does the `interfaces/` changes, A5 re-tests; (b) `FIN-001-UR/UL/LR/LL` |
| CR-A5-11 | A5 | closed (D-24) | 0.053 m is inside the R1 range; no pod move, no aft channel needed for CG reasons |
| CR-A5-15 | A5 | accept (D-26) | station codes |
| CR-B1-10 | B1 | accept (D-36) | all rev-2 values carried; cruise minutes from E2's mission budget (conservative), B1's level-cruise figures in the notes |
| CR-B1-13 | B1 | accept (D-37) | 0.5 m/s; F3's RSS 0.44 fits |
| CR-B2-09 | B2 | reject (D-43) | 0.0066 passes; C2 has sized to it |
| CR-B2-11 | B2 | closed (D-24, D-44) | the forward limit moved to 0.050; `R-STALL` judged over the new range; B2 re-runs the forward-CG stall there |
| CR-B3-11 | B3 | accept (D-24) | D-17 closed; A3 moves the pack; D2 re-lays the bay |
| CR-B3-12 | B3 | accept (D-27) | 7° cant; B4 re-runs swirl, D3 one print parameter, C4/C6 mount side load, F4 cant check |
| CR-B3-14 | B3 | accept (D-26) | 0.21 m half-fins with two layers (C4 CR-C4-20); D5 pads stay at ±0.219 (C5) |
| CR-B4-02 (R2 notes) | B4 | accept | pitot note 1.66 %, download 1.034–1.043 kept at 1.06, `SRC-APC-11X45MR` checked |
| CR-C1-12 | C1 | accept (D-29) | 21.1 N; F4 keeps the cap (CR-F4-07); H1 replaces with the measured peak (CR-H1-01) |
| CR-C1-13 | C1 | accept (D-29) | VD 27.2 m/s with the elevon deflection schedule; B1 re-runs VMAX (CR-C1-14) |
| CR-C1-16 | C1 | accept (D-29) | n⁺ 3.4 |
| CR-C1-17 | C1 | accept in part (D-30) | C5's planar model governs: 38 mm constant-force stroke at 48 mm; C1's 41 / 26 mm is the single-foot bound |
| CR-C2-10 | C2 | accept (D-43) | spar unchanged |
| CR-C3-02 | C3 | void (D-25) | the 10 mm nose extension of CR-C5-02 absorbs the 3 mm |
| CR-C3-03 | C3 | accept (D-25, D-38) | pod 122 g |
| CR-C3-06 | C3 | accept (D-25) | crush block + spreader stop |
| CR-C4-01 (R1) | C4 | accept in part | brace and edge strips done by D3; one layer withdrawn by C4 itself (CR-C4-14) |
| CR-C4-14 | C4 | accept (D-26) | two layers; `fins.layers` `CHECKED` against `CL-C4-D3-SEP` 0.41 |
| CR-C4-15 | C4 | accept (D-26, D-38) | fins 408 g (402 + 6 for the 0.21 m fin) |
| CR-C5-01 | C5 | accept (D-30) | `CALC-A1-TIPOVER` reads `CL-D5-CONTACT-Z` and subtracts z_cg at the worst corner (30.6°); 33° retired; A2 re-words `R-TIPOVER` |
| CR-C5-02 (revised) | C5 | accept (D-25) | pod nose shell −0.115 with the XPS block; box slack 17 mm |
| CR-C5-11 | C5 | accept (D-30, D-38) | feet 48 mm; landing 43 g |
| CR-C6-05 | C6 | accept (D-40) | one prop spanner |
| CR-C6-06 | C6 | accept (D-41) | per-type keys |
| CR-D2-01 | D2 | accept (D-25) | pod width 0.14; B1 adds the drag |
| CR-D2-02 | D2 | superseded (D-24) | nominal pack centroid x −0.001 (B3), not the forward stop; aft travel must reach 0.073 m pack aft face |
| CR-D2-03 | D2 | accept (D-25) | pitot y −0.046; B4 re-runs (CR-F3-11) |
| CR-D3-01 | D3 | accept (D-26) | tube 0.344 |
| CR-D3-02 | D3 | reject (D-26) | C4's mode check fails with one layer on D3's own geometry |
| CR-D3-04 | D3 | accept (D-28) | prop plane −0.0082; E1 stack reconciled on the measured motor |
| CR-D3-08 (id part) | D3 | reject (D-26) | ids are `FIN-001-UR/UL/LR/LL`; D3 renames, D5's edges already use them |
| CR-D5-01 | D5 | accept (D-30, D-31) | envelope 0.438 m; `CL-A1-TIPOVER` on the contact z; README feet row |
| CR-D7-01 | D7 | accept as `PROPOSED` (D-31) | 0.54 m box pending two measured cars; fallback 0.50 + 0.15 m label; box 3.63 kg |
| CR-E1-14 | E1 | accept (D-34, D-38) | 476 g; screws stay in propulsion |
| CR-E1-15 | E1 | accept in part (D-35) | one worst-state claim is right; 0.76 (E2) carried until E2 concurs or the stand decides; `CL-A1-HOVER-TW-SAG` notes `CL-E1-TW-WORST` |
| CR-E1-16 | E1 | superseded (D-28) | D3's collar moves the plate; −0.0082 carried |
| CR-E1-19 | E1 | reject (D-36) | 247 W reads the old L/D 5.6; B1's 218 / 285 W carried; E1 re-points at `CL-B1-CRUISE-LD` (CR-B1-11) |
| CR-E2-12 | E2 | accept with changes (D-35, D-36) | sag 0.76; pessimistic cruise 7.3 min from the re-run on B1 rev 2 (not 5.1, which was the 11×4.5MR) |
| CR-E3-07 | E3 | accept (D-42) | three `env` keys |
| CR-F1-02 | F1 | accept (D-32) | AS150U, re-termination, `r_ext_mohm`, power 620 |
| CR-F3-01 | F3 | accept (D-33) | FC, airspeed, GPS, avionics 80 |
| CR-F4-07 | F4 | accept (D-29) | 21.1 N; the cap stays at 9 350 rpm |
| CR-F5-07 | F5 | accept (D-33) | telemetry key, 25 mW note, `rc_rssi_check_min_dbm` |
| CR-H1-01 | H1 | accept (D-29) | 21.1 N until GT-02d; then the measured peak rounded up to 0.5 N |
| CR-H1-02 | H1 | accept (D-39) | rigs count; borrow first, buy ≤ $20; I1 adds the line |
| CR-I1-02 | I1 | accept (D-39) | `cost.*` from the BOM; `CL-A1-RESERVE` reads it |
| CR-I1-03 | I1 | accept (D-39) | lever order: adapter set gated, SpeedyBee, airspeed last |

### Forwarded (A1's position; the named role acts)

| CR | To | Decision | Reason |
|---|---|---|---|
| CR-A2-13, CR-A5-13, CR-E3-12, CR-F4-03, CR-E1-17 | E1 | forward | re-point the limiter claims at `propulsion.motor_max_a` / `esc_burst_a`; `CL-E1-HOVER-T` parts → `PRP-001-<st>`; publish `subsystems/propulsion/interfaces.json` with instance nodes; motor-map and adapter hand (LH on CW) as F4 published; slotted mount pattern until measured |
| CR-A2-14, CR-B1-12, CR-B3-15, CR-C1-08, CR-C1-15, CR-C2-03, CR-C2-04, CR-C4-07, CR-C5-05, CR-C5-09 (part), CR-D5-09, CR-E1-21, CR-E3-05, CR-F1-10, CR-F3-02, CR-F5-01, CR-J1-12, CR-D3-07 | F4 | forward | one parameter file: `AIRSPEED_MIN` 15.6, `Q_TAILSIT_RAT_FW` 12 (re-check at sag 0.76), deflection schedule to VD 27.2, `THR_MAX`, rate-loop crossover ≤ 5 Hz and notch on ESC rpm, `Q_M_BAT_CURR_MAX` 100 claim, spin-min at touchdown, wingtip-into-wind landing, cant sense A/B vs the map, `ARSPD_TYPE 1`, ELRS channel map, LH adapters on CW motors |
| CR-A2-15, CR-C1-19, CR-C2-06, CR-D5-06, CR-E2-15, CR-F1-12, CR-A4-17, CR-B2-10 | A3 | forward | re-run on D-24 (pack at x −0.001, D-38 allocations); `CL-A3-HOVER-SPLIT` verifies `R-HOVER-SPLIT`; rows from C2 (397 g + plugs), D5 (39.1 g), F1 (69 g, UBEC 13 g, ESC leads 64.6 g), E1 parts.csv; clip rows per half-fin; 17–20 g servos |
| CR-A2-16, CR-B1-15, CR-B3-13, CR-C1-18, CR-C2-09, CR-C1-15 (hinge part) | B2 | forward | `sf` → `P:requirements.servo_torque_factor`; AVL polar and trimmed CL(α) as params keys; `clmax_vs_flap` key; `loads_spanwise.json` at c 0.32 and the R3 CG range; `CL-B2-STALL-GATE-FWD` at 0.050 (D-44); flexible-wing roll effectiveness noted |
| CR-A2-17, CR-B1-11, CR-E3-10, CR-F1-03, CR-F1-04, CR-D7-07, CR-I1-06 | E2 | forward | `cap_frac` → `P:requirements.pack_capacity_min_frac`; re-run on B1 rev 2 and `r_ext` 6.5; phase currents as claims; one sag claim with E1 (D-35); packs in the LiPo bag; confirm the pack connector and lead gauge at order |
| CR-A2-18, CR-A4-21, CR-A5-14, CR-C2-05, CR-D3-11, CR-C6-08 | D7 | forward (D-31) | cradle pads ≥ 40 × 40 mm at y ±0.20, inboard of 0.23; box in the aircraft frame with `stowed` edges; pitot slot; M3 handles; two measured cars before the 0.54 m freeze |
| CR-A2-19, CR-A3-13, CR-B2-12, CR-B4-03, CR-B4-12, CR-C2-03, CR-C4-20, CR-F4-01, CR-F4-02, CR-J1-11, CR-C5-05 (yaw) | B3 | forward | re-run once at R3 (7° cant, 0.21 m fins, pack at −0.001, A3 inertia): publish `CL-B3-CG-FWD/AFT/TARGET` under the same ids (A1's `CALC-A1-CG-RANGE` reads them), Cn_β at the aft limit with prop normal force, symmetric differential-thrust yaw with `THR_MIN` 10 %, the 12–15 Hz torsion mode in the hover loop |
| CR-A4-16, CR-D2-03, CR-D3-15, CR-F3-11, CR-C4-08 | B4 | forward | half-fin ids; pitot at [−0.195, −0.046, 0.045]; swirl recovery and yaw at 7° cant; collars, braces and ESC pads in the download and drag models |
| CR-A4-18, CR-C4-16, CR-C4-17, CR-C4-19, CR-C6-01, CR-C6-02, CR-C6-03, CR-C6-10, CR-D5-03, CR-E3-01, CR-E3-02, CR-H1-08, CR-C2-02 | D3 | forward (D-26, D-27, D-28, D-42) | two layers, 0.21 m half-fins, tube 0.344, 7° mount angle, ASA mounts and pads, 40 mm two-face collar tail, CF through-pins on the strips, collar 16 mm, motor screws 0.20 N·m on a drilled (not slotted) pattern, ids `UR/UL/LR/LL`, square 40 mm tips for the feet, strap eye at each root, SPEC pointed at `CL-C4-D3-*`; the 36 mm spar plug is C2's part |
| CR-C2-01, CR-C2-02, CR-C4-18, CR-D2-04, CR-D3-03, CR-D7-04, CR-A5-12 | D1 (C2) | forward | build the wing from `team/C2/sizing.json`: six PETG spar plugs, slot from the lower surface, block pockets x 0.0279–0.0972 at y 0.302–0.338, anchor pockets 20 × 16 at (0.080, ±0.242), pod recess and bare-foam footprint, ties under the spar, cradle patches free, wire channel ahead of the spar or through the block; declare `WNG-001/002` and acknowledge the fins, pod and transport edges |
| CR-C3-01, CR-C3-04, CR-C5-07, CR-C6-07, CR-C6-09, CR-E3-03, CR-F1-08, CR-F1-13, CR-F3-03, CR-F5-03, CR-A4-19, CR-C2-07, CR-A1-24 (closed) | D2 (C3) | forward (D-24, D-25) | pod at 0.21 × 0.14 × 0.07 with the crush block; stops 3.0 mm, guides 1.5 mm, epoxy tray-to-floor, 50 mm strap overlap, 12 × 40 hatch tab; bay re-laid for the pack aft face at 0.069 / 0.073; AS150U park 60 mm; vents; FC on gel pads, airspeed on foam tape (no M2); pitot flange and y −0.046; two antenna exits; bond to bare foam; nothing waits on the pod station any more |
| CR-C4-09, CR-C5-04, CR-C5-10, CR-C6-12, CR-D3-08 (shoe part), CR-H1-08 | D5 (C5) | forward (D-30) | 48 mm foot, ≥ 38 mm stroke, biased cartridges colour-marked, shoe for the 9.6 mm board + strip ends, 6 mm snap fingers, TE corner caps, CG-jig patch free at \|y\| 0.45 |
| CR-D3-05, CR-C6-13, CR-D7-04, CR-F1-11, CR-I1-07, CR-B2-10 | D6 | forward | link slot x 0.2376–0.2616 in the lower half-fin root; horns and frames ≥ 720 mm² into XPS, through-panel horn, screws into bosses; servo ≥ 3.93 kgf·cm, ≤ 6 V, stall current to F1; keep the cradle patches clear |
| CR-A4-20, CR-C3-05, CR-C4-22, CR-D5-04, CR-C1-11 | C6 | closed / forward | joint stacks delivered (`joint_stacks.json`); own the pod allowables; collar and brace-end bonds on C4's R2 numbers; coupons CR-C6-14 |
| CR-C5-09, CR-C6-03, CR-C6-02a, CR-D3-10, CR-C4-13, CR-C4-21 | C4 (C1) | forward | fin face and strips at μ 0.7 side load (23 N); agree the collar torsion (5.29 vs 9.3 N·m: C6 sizes to C4's); strip shear flow in the FE; mount side component at 7° cant; `T-C4-MOUNT-STIFF`, `T-C4-TAP-D3` |
| CR-C1-14, CR-C4-08, CR-D2-01 (drag), CR-D3-15, CR-E2-11, CR-B2-14 | B1 | forward | `CL-B1-VMAX` with the 11×5.5MR at the cap; +3 % pod drag, collars and braces; re-check the 12 °/s pitch-over at sag 0.76; keep `CL-B1-CRUISE-P` ids |
| CR-D7-02, CR-H1-03, CR-J1-10, CR-C5-09, CR-C6-03 | C1 | forward | cradle stroke 0.0699, x/y box allowables, lid preload case; whiffletree loads and limit/ultimate labels for H1; retire `ASM-J1-*` names; L4/L5 at μ 0.7; `J-FINHALF` torsion with C4 |
| CR-A5-10, CR-D2-08, CR-D3-13, CR-D5-07, CR-D7-03, CR-E3-11, CR-F1-06, CR-F3-08, CR-F5-10, CR-C6-15 | A4 | forward (D-46) | `stowed` key; new parts, edges and connection types from D2, D3, D5, D7, E3, F1, F3, F5; `E-HRN-10` → `CT-AS150U`; `E-AVN-01` gel pad, `E-AVN-04` tape; `GND-001`; merge the joint stacks; `interfaces/` tooling changes |
| CR-D3-14, CR-D5-02 | A5 | forward | skeleton `fins` to R3 (tube 0.344, half-fins 0.21, 7° mounts), `DATUMS.md` (DP-TUBE, DP-TE, DP-GROUND 0.368, `DX-FOOT-*` = pad contact ±0.218, `DX-COLLAR`, `DX-ANCHOR`), box 0.54; re-test after A4's `merge_check.py` change |
| CR-A2-14, CR-B1-16, CR-C2-08, CR-C3-07, CR-C4-21, CR-C6-14, CR-D5-08, CR-E3-06, CR-F3-10, CR-F4-06, CR-F5-05, CR-I1-08 | H1 | forward | one campaign plus the structures coupons and proofs: stand points at 14.0 / 13.6 V with the limiter, GT-02d peak at the cap, A/B hover ratio, mount stiffness, C2/C3/C6 coupons and proof loads, D5 cartridge coupon and pad friction, GT-04 pass lines (ESC ≤ 33 K, motor ≤ 38 K, 600 s τ step), I²C scan, range test at 25 mW with the RSSI line, Aloft tube bend test by 10 Dec |
| CR-B1-14, CR-C5-06, CR-C5-08, CR-E3-04, CR-F4-10, CR-F5-09, CR-D7-07, CR-F3-10 | H2, H3 | forward | flight card: wind ≤ 5 m/s for fin-tip landing, lay flat above 8 m/s, wingtip into wind, stance rules S1–S8 on the mat, full throttle ≤ 10 s, pack 20–34 °C, hatch open on the ground > 5 min, TX on before the pack, RSSI alarms, transition at 12 °/s until logs show ≤ 0.7, motor-out = throttle cut + glide; log 20 twin touchdowns |
| CR-C6-11, CR-D3-09, CR-D5-10, CR-E1-20, CR-E3-06, CR-F1-12, CR-F1-14, CR-F3-06, CR-F5-06, CR-B4-11, CR-I1-01 | I1 | forward (D-39) | fastener kit (M3 only), CF strips and plugs, neoprene, thermocouples, AS150U × 5, 8 / 16 / 20 AWG, UBEC, caps, fuse, PDB, CoreWing V2 now, MS4525DO, FCC RC, ground-test line ≤ $20, adapter set gated (X05); designers deliver `parts.csv` with prices |
| CR-E2-16, CR-I1-11 | I2 | forward | 2 sorties per test day; order dates 20 Nov / 10 Dec / 15 Dec, build start 19 Jan |
| CR-B3-16, CR-C2-04, CR-C4-06, CR-C5-03, CR-F1-01, CR-F1-15, CR-F3-09, CR-F4-09, CR-F5-08, CR-H1-07, CR-I1-12, CR-E3-08 | A2 | forward | `R-CG-RANGE` → `cg.x_range_m`; `R-VIBRATION` tap-test branch for the wing (D-45); `R-TIPOVER` and `R-LANDING-IMPACT` texts per C5; `R-DISCONNECT` wire limits 10 °C steady / 30 °C < 60 s and the pack-lead 20 °C; `R-FIELD-SETUP` one spanner (D-40); `R-AIRSPEED` RSS 0.5; `R-RC-LINK` 25 mW + RSSI; `R-FSW-PARAMS` 63 / 113 matched; H1 evidence names; `R-BUDGET` → I1 claims; `R-THERMAL` claims; per-type thread engagement (D-41) |
| CR-A4-05, CR-A5-12, CR-D2-07, CR-D3-12, CR-E1-18, CR-F1-07, CR-F3-05, CR-F4-04, CR-F5-04 | F2 | forward | first job: wire list and routing (8 AWG ≤ 0.15 m twisted; ESC leads 16 AWG in two taped surface grooves 5 mm apart, not buried, ≥ 0.12 m from the mast top; phase extension ≤ 100 mm if needed; I²C ≤ 0.5 m; RX lead; `signal.fc_port` on `E-HRN-24…29`), `team/F2/mass_estimate.csv`, `subsystems/harness/` |
| CR-F3-04, CR-E2-14, CR-F1-09, CR-I1-10 | F1 | closed | FC power board is `PWR-003`; UBEC stays; currents as E2 lists; AS150U answered |
| CR-E3-09, CR-F1-09, CR-D2-06, CR-D7-06, CR-F5-02, CR-I1-09, CR-B4-05 | F3 | closed / forward | answered in F3-R1 (1.73 W, 4.5 A BEC, gel pads, boom QD, RX on a DMA UART, V2 confirmed); write `subsystems/avionics/` |
| CR-C4-12, CR-F1-05, CR-B2-15 | J1 | forward | supersede `CL-J1-TUBE-MODE-SEP` by `CL-C4-D3-SEP` and the XT60 claims by F1's AS150U claims; re-point `cm0` at `P:b2.xfoil.cm0_2d_stall` |
| CR-E3-01 (G3 part), CR-C6-04 | G2, G3, E3 | forward | ASA (HDT 93 °C) for mounts and pads; 4 h / 50 °C post-cure for bonds within 50 mm of a motor; E3 gives the collar temperature |
| CR-H1-04, CR-H1-05, CR-H1-06, CR-I1-04, CR-I1-05 | F4, E1, E3 | forward | stand parameter set (25 A per station); `ASM-E1-RM` line-to-line at 25 °C; GT-04 limits (answered by CR-E3-06); one ESC 4-pack now; box adapters for the stand |
