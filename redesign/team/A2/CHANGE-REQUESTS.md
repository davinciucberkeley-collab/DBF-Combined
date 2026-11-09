# Change requests from A2 (systems engineer)

Status of the first round, then the new requests from resolving CR-A1-17 (2026-11-09, A2-R1).

## Round 1 — status

| # | To | Disposition (CHANGE-LOG) | A2 side |
|---|---|---|---|
| CR-A2-01 | A1 | accept, D-14 | done: 37 of 39 `ASM-A2-…` retired; 2 aliases remain while B2 and E2 still cite them (CR-A2-16, -17) |
| CR-A2-02 | A1 | accept, D-15 (fin height 0.38 m) | closed |
| CR-A2-03 | A1 | closed | closed |
| CR-A2-04 | A3 | forward (also CR-A1-11) | done by A3: `CL-A3-CG-X/Z-RANGE` → `R-CG-RANGE`, `CL-A3-ALLOC-WORST` → `R-MASS-ALLOC` |
| CR-A2-05 | A4 | forward | open: `R-NO-FLOATING` and `R-JOINT-STACK` still have no claim |
| CR-A2-06 | J1 | forward (also CR-A1-16) | done by J1: `CL-J1-TUBE-MODE-SEP` → `R-VIBRATION` (fails −91 %, C4's), `CL-J1-FIN-YAW-ARM` → `R-DIRECTIONAL` |
| CR-A2-07 | B1, B2 | closed by D-01 | closed; `R-TRANSITION` still shows `FAIL` on `CL-B3-VT-TRIM` (16.55 vs 16 m/s, R0 wing; D-21 says B3 re-runs at R1) |
| CR-A2-08 | F1 | forward | open: `R-DISCONNECT` fails on J1's XT60 claims; A1's rule in CHANGE-LOG (XT60 only with a cited burst rating covering the ≤ 5 s 100 A case) |
| CR-A2-09 | C1 | closed | closed; `team/C1/LOADS.md` exists; C1 already cites `P:requirements.*` (no `ASM-A2-…` left in C1) |
| CR-A2-10 | H1, H2, H3 | forward | open: 27 evidence files in the matrix still absent; no H folder yet |
| CR-A2-11 | J2 | forward, optional | open |

## Round 2 — new

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-A2-12 | A1 | (a) Update `R-TRANSPORT` text in `params/claims.json` from "≤ 1.25 × 0.55 × 0.45 m" to the D-16 box `requirements.box_external_m` (1.25 × 0.55 × 0.50 m); A2's row already reads the key. (b) Add two propulsion keys so E1's limiter claims cite parameters, not typed numbers: `propulsion.motor_max_a` 25 A (30 s, `SRC-X3108S`) and `propulsion.esc_burst_a` 55 A (10 s, `SRC-LANRC-45A`). (c) Close CR-A1-17: `ASM-A2-*` retired (2 aliases pending B2/E2), `R-ESC-CURRENT` rewritten, `R-HOVER-SPLIT` added, `CL-A1-BOX-FIT` mapped at 0.50 m. | one source per number; the shared node text contradicts D-16 |
| CR-A2-13 | E1 | Re-point the `R-ESC-CURRENT` claims to the rewritten requirement: `CL-E1-ILIM-I` limit → `P:propulsion.motor_max_a` (after CR-A2-12b; 24.75 A passes); `CL-E1-IMAX-168-55` (and `-168`) limit → `P:propulsion.esc_burst_a` (51.6 A passes 55 A); `CL-E1-IMAX-148`, `CL-E1-IMAX-148-55` drop `verifies` (unlimited 14.8 V is no longer a requirement; keep as information or delete); `CL-E1-HOVER-I-55` limit → `hover_current_a × (1 + hover_current_tol)` = 31.05 A from a calc on the two parameters, not the typed 27.6 A; `CL-E1-IPACK-PEAK` gets `limit=('<=', 'P:performance.full_throttle_current_a')` and `verifies=['R-ESC-CURRENT']`. | 4 of the 7 claims on `R-ESC-CURRENT` fail against the old text (−18 % worst); the limiter is the design case (CR-E1-07, A1 concurs) |
| CR-A2-14 | F4, H1 | F4: a claim (no calc, `PROPOSED`) that the parameter file sets `Q_M_BAT_CURR_MAX = 100` and `Q_M_BAT_IDX` to the flight pack, `verifies=['R-ESC-CURRENT', 'R-FSW-PARAMS']`, `how` = parameter diff. H1: a `kit.test` (planned) for the restrained-frame four-motor full-throttle run (fresh pack, 2 s, dataflash `BAT.Curr` ≤ 100 A, clamp ≤ 25 A per ESC lead) verifying `CL-E1-ILIM-I`, plus the single-station unlimited burst ≤ 55 A. | part (a) of `R-ESC-CURRENT` is inspection + test; nobody owns it yet |
| CR-A2-15 | A3 | `CL-A3-HOVER-SPLIT`: add `verifies=['R-HOVER-SPLIT']` and re-run `mass_rollup.py` (the script already cites `P:requirements.hover_split_max`; `claims.json` on disk still shows `ASM-A3-SPLIT-MAX` 1.10 and `FAIL`). | `R-HOVER-SPLIT` (new, D-18) has no claim; yours is the one |
| CR-A2-16 | B2 | `wing_claims.py` input `sf: "ASM-A2-SERVO-TORQUE-FACTOR"` → `"P:requirements.servo_torque_factor"` (1.5, same value); re-run. | last citation of that retired id; A2 then deletes the alias |
| CR-A2-17 | E2 | `energy_claims.py`: input `cap_frac: "ASM-A2-PACK-CAPACITY-FRAC"` → `"P:requirements.pack_capacity_min_frac"` (0.92, same value) and drop the id from `assumes` (a parameter is not an assumption); re-run. | last citation of that retired id; A2 then deletes the alias |
| CR-A2-18 | D7, C1 | `CL-D7-A1-BOX-DROP-ALLOW` fails −47 % (allowable drop 0.158 m vs `requirements.box_drop_m` 0.3 m): the cradle foam is short of the ≥ 70 mm D-22 asks for. Point the drop-stroke claims (`CL-D7-CRADLE-STROKE`, `CL-D7-DROP-N`, `CL-D7-A1-BOX-DROP-ALLOW`) at `R-LOADS` (transport case) as well as `R-TRANSPORT`, and size the foam to the 0.3 m drop. | `R-TRANSPORT` shows `FAIL` for a load-case reason, not a fit reason; `CL-A1-BOX-FIT` itself is +25 mm |
| CR-A2-19 | B3, A5 | `CL-A5-LAYOUT-CG-X` (A5) verifies `R-STATIC-MARGIN` and fails −18 % against the old 0.045 m forward limit; the R1 range is `cg.x_range_m` 0.040–0.049 (D-10). A5 points it at `R-CG-RANGE` with `P:cg.x_range_m`; B3 re-derives the range at R1 geometry (D-17) so `R-STATIC-MARGIN` fails only for a static-margin reason. | each requirement fails for its own reason |
