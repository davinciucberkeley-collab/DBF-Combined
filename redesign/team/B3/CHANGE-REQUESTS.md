# Change requests from B3 (stability and control)

Numbers from `python -I redesign/team/B3/sc_analysis.py` and `run_avl_study.py` at R1 geometry (A1-R2 params,
2026-11-09). Detail: `S-AND-C.md`.

## Open (R1 re-run, answers CR-A1-10)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-B3-11 | A1 (copy A3, D2) | **D-17 answer: keep the pod nose at −0.105 m.** Set `cg.x_range_m` = [0.050, 0.055] (claims 0.0499 / 0.0553, rounded inward) and `cg.x_target_m` = 0.0526. A3 sets the pack's nominal centroid to **x = −0.001 m** (4 mm aft of the pod centre), not 29 mm forward. A1 re-runs `CALC-A1-POD-RULE`, which drifts on the new B3 claims. | The pack-centred CG is 0.0515 m, inside the range (`CL-B3-CG-CENTRED-FWD` +1.6 mm, `-AFT` +3.7 mm). The pod at −0.125 would give 0.0444 m, 5.5 mm ahead of the forward limit. Today's pack station gives 0.0440 (`CL-B3-CG-NOW-FWD` −5.9 mm, `FAIL`). The forward limit is set by the elevon at the trimmed CLmax ≤ 12.5° (`requirements.elevon_trim_travel_max`). The aft limit is set by SM 5 %. NP with props 0.0713 m |
| CR-B3-12 | A1, B4, D3, E1 (copy F4) | **Motor cant 3° → 7°** (`propulsion.stations.cant_deg`): tangential, same sense as today. B4 re-runs swirl recovery at 7°. If A2 prefers, it can instead lift the 30 % differential cap on yaw in `R-HOVER-AUTHORITY` (3° then gives 2.31× and 2.32 rad/s²) | With 3° at 30 % differential, yaw reaches 1.15× the 5 m/s disturbance and 1.15 rad/s² (`CL-B3-HOVER-YAW-RATIO/ACCEL` `FAIL` vs 1.5× and 2 rad/s²). 6.1° is needed (`CL-B3-HOVER-CANT-REQ`). 7° gives 2.23× and 2.24 rad/s² for 0.75 % thrust loss |
| CR-B3-13 | B2 | (a) Publish the S5010 clmax-vs-elevon envelope as a `P:b2.xfoil.clmax_vs_flap` key so B3 can drop `ASM-B3-CLMAX-FLAP`. (b) Re-run the wing+fins AVL at R1 (c 0.32, fins 0.045–0.32) and compare Xnp with `CL-B3-XNP-AERO` 0.0738 m. (c) η and Δcm at Re 2.6e5 for c 0.32 | The forward CG limit moves about 3 mm per ±20 % in η. B2's trimmed CLmax 0.798 and B3's 0.799 already agree |
| CR-B3-14 | A1, D3, D5 (copy C4, B4) | **Half-fins 0.21 m high** (`fins.half_height_m` 0.19 → 0.21), so the fin tips sit at the tube ends. Combine this with D5's foot splay to z ≥ ±0.21 (tip-over note). Fallback: extend the half-fin trailing edge 30 mm aft of the wing TE (0.0325 /rad; feet move aft) | `CL-B3-CNB` at the aft limit and 1.3 Vs is 0.0286 /rad (`R-DIRECTIONAL` ≥ 0.03, −5 %). With 0.21 m it is 0.0373. Cost ~+6 g, and the envelope is unchanged (tube ends already ±0.21). B4 checks the fin tip in the prop wash, C4 the fin modes |
| CR-B3-15 | F4 | `ARSPD_FBW_MIN` **15.6 m/s** (1.3 × 11.93 at the forward CG limit, `CL-B3-VT-TRIM` 15.51); `AIRSPEED_CRUISE` 16 holds. Expect elevon trim −6.1° at 16 m/s (target CG) and −12.6° at the stall (forward CG). Fixed-wing yaw by differential thrust is now optional damping, not required (Cn_β > 0, Dutch-roll ζ 0.32). Motor-out in cruise: the elevons hold E1's 0.22 N·m with 1.2°. Back-transition: the motors hold up to 1.03 N·m nose-up at 8–11 m/s (19 % of the differential). Put `results/sc_results.json` into SITL | Replaces CR-B3-04 (16.6 m/s was the R0 wing) |
| CR-B3-16 | A2 | Update the `R-CG-RANGE` text from "0.045–0.075 m until B3 narrows it" to `cg.x_range_m`. Decide whether the 30 % differential cap in `R-HOVER-AUTHORITY` applies to yaw (CR-B3-12) | B3 claims verify `R-CG-RANGE` only through A3 |
| CR-B3-09 | H1, H2 | Plan tests `T-B3-CG-BALANCE` (mark both limits at the fin roots: 0.050 and 0.055 m), `T-B3-TWIN-NP`, `T-B3-YAW-DOUBLET` (aft mark, 1.3 Vs), `T-B3-HOVER-WIND` | Every B3 claim is `UNVERIFIED` until a test runs |

## Closed or superseded (R0)

| # | Status |
|---|---|
| CR-B3-01 | superseded by CR-B3-11 (range re-derived at R1); elevons 22 % c, both panels, ±25° kept |
| CR-B3-02 | adopted (D-04, option O4b): Cn_β went from −0.105 to +0.029 /rad; the residual is CR-B3-14 |
| CR-B3-03 | superseded (D-08, D-17) |
| CR-B3-04 | superseded by CR-B3-15 |
| CR-B3-05 | adopted at 3° (D-09); now 7° (CR-B3-12) |
| CR-B3-06 | closed: B3 uses `CL-B2-DCM-VISC`, `CL-B2-ELEVON-ETA` and B2's critical-section method |
| CR-B3-07 | superseded (D-21): trimmed 1.3 Vs is 15.51 m/s at R1 |
| CR-B3-08 | done: `R-DIRECTIONAL` exists; `CL-B3-CNB` and `CL-B3-DR-ZETA` verify it |
| CR-B3-10 | done (D-18) |
