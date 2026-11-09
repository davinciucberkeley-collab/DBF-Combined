# params.json change log — K09-L

Owner A1 (chief engineer). One row per decision; `params.json#meta.revision` names the current revision. A decision
changes `params.json` only here; the owning role then re-runs its script so `build_graph.py` shows no drift.
Every change request written so far is dispositioned in the second table (accept / reject / forward with one reason).

| Revision | Date | What | Re-check |
|---|---|---|---|
| A1-R0 | 2026-11-09 | design frame from the config study (chord 0.30, MH 45, tubes at x −0.10, CG 0.060) | — |
| A1-R1 | 2026-11-09 | after the first analysis round: D-01 … D-15 | `python -I redesign/team/A1/frame_claims.py` |
| **A1-R2** | 2026-11-09 | change-request round: D-16 … D-23 | same, then `python -I redesign/proofs/build_graph.py` |

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
