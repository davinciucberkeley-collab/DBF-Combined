# Change requests from C1 (loads engineer)

Revision C1-R3 (2026-11-09). Numbers from `python -I redesign/team/C1/loads.py` at params A1-R3.

## New in R3 (open)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-C1-20 | A1 (cc F4, B1, B2, D6) | Decide VD. **Recommended:** F4 caps the fixed-wing `THR_MAX` so level speed ≤ **21.8 m/s** (= 27.2 / 1.25), B1 gives the throttle %, H2 shows it in logs; then C1 reads the capped VH and keeps `requirements.vd_ms` 27.2 and n⁺ 3.4. **Alternative:** raise `vd_ms` to **32.1 m/s** and `load_factor_limit_pos` to **3.6** (neg −1.6). | `CL-B1-VMAX` 25.7 m/s (11×5.5MR at the cap) → `CL-C1-VD` 32.1 (`FAIL` −18 %), gust n +3.58 / −1.58. Structure is insensitive (`data/sensitivity_vd.json`: spar, fin joint, mounts, pod, feet unchanged; wing Vz +3 %); q at VD rises 453 → 631 Pa (+39 %): elevon hinge, horns and servo (B2, D6) and the stall-line n 5.2 → 7.3 (F4). Until decided the envelope runs at 32.1. |
| CR-C1-21 | C4 (cc C6, D3) | Re-run `CALC-C4-D3-STATIC` on `ASM-C1-FRICTION` **0.7** and `CL-C1-FOOT-CORNER` 29.1 N; publish the station-collar torque as a claim (limit) that C6 reads; add an equilibrium check: the FE section torque at the wing plane in L4 equals `CL-C1-FINHALF-T-LIM` (6.60 N·m) within 5 %. | Agreement on CR-C6-03: C1's 6.60 N·m is the **section total** about the tube axis; C4's collar value is an **internal** path quantity (strip end + brace-ear couple) and may exceed it. C6 sizes the collar to the larger (expect ≈ 11.6 N·m limit = 9.3 × 6.60/5.29). |
| CR-C1-22 | D7 (cc A2) | End and side impacts: either label the box "keep upright, do not drop on end or side" and make them test-only, or add crush foam: **≥ 54 mm** (end) and **≥ 57 mm** (side) of stroke for a 0.3 m drop. Lid-down: pillars carry **102 N** per side (limit) at n 10.1 with the same stroke; size the pillar and pad for it. | `CL-C1-TRANSPORT-N-ALLOW-X/-Y` 12.13 / 11.53, `CL-C1-BOX-STROKE-REQ-X/-Y`; box gaps 16 / 36 mm (CR-D7-02b). Floor drop passes: n_T 10.09 vs 12.45 on your 66 mm (`CL-D7-CRADLE-STROKE`). |
| CR-C1-23 | H1 | Replace the equivalent point of GT-08 with `data/whiffletree.json`: aircraft inverted on the pod, four pads per side (y 0.120 / 0.260 / 0.355 / 0.465 m; **limit** 9.93 / 7.98 / 4.69 / 6.40 N, sum 29.0 N) and an **upward relief pull 20.0 N** at each motor tube. Proof at limit; ultimate (× 1.5) on a sacrificial wing only. | CR-H1-03 answered. `CL-C1-WING-SHEAR-ULT` **is ultimate** (33.4 N; limit 22.2 N, case F7-VA). The old point (P = V_ult/1.5 at y = Mx_ult/V_ult) mixed a flight shear with the G2 handling moment. |
| CR-C1-24 | C4, C6 (cc H3) | Size the motor mount for the set-down case G3: **23.2 N** per lower motor can at 2 g (mount force 20.9 N limit, 31.3 N ult), or H3 adds to the flight card "set it on its feet or on the foam pad, never on the motors". | `CL-C1-MOUNT-F-ULT` now governed by G3, +6 % over the flight/hover value (H5 0.65 N·m still sets the moment). |
| CR-C1-25 | A3 | Re-run the R3 roll-up with the pack at x −0.001 m and publish the pack station claim on that basis; C1's lumped model needs a +16/+18 mm centre-group shift to sit on the CG limits. | `data/mass_model.csv` (TRIM rows); open issue 3 in LOADS.md |
| CR-C1-26 | J1 | CR-J1-10 done: `team/C1/claims.json` names no `ASM-J1-*` id (mount mass is now `ASM-C1-MOUNT-MASS`). J1 may delete `ASM-J1-APC-KT` and `ASM-J1-MH45-CM0`. | — |

## Answered or closed in R3

| # | State |
|---|---|
| CR-C1-04 (carry point / G2) | Closed: L4 at μ 0.7 (8.34 N·m) now sets the fin-joint moment, G2 does not. A "do not lift by the motors" label stays good practice. |
| CR-C1-12, -13, -16, -17 | Adopted by A1 (D-29, D-30). CR-C1-13/-16 are reopened by B1's VH as CR-C1-20. |
| CR-C1-14 | Answered by B1 (`CL-B1-VMAX` 25.7 m/s), now read. |
| CR-C1-15 | Deflection schedule adopted (D-29, forwarded to F4); C1 runs F6/F7 at full travel to VA and ⅓ at VD (`ASM-C1-ELEVON-VD-FRAC`). Hinge sizing waits on CR-C1-20. |
| CR-D7-02 (a, b, c), CR-C5-09, CR-C6-03, CR-H1-03, CR-J1-10 | Done in C1-R3 (LOADS.md, action-item table). |
| CR-C1-05, CR-C1-11 | Closed (D-22 / C6 RF 3.26). |

## Still open from R1/R2

| # | To | What | State |
|---|---|---|---|
| CR-C1-02 | H3, C5 | Parked stance: μ needed 0.68 vs mat 0.70 (3 % margin); lay flat above 5 m/s (C5 S1–S8) | Forwarded to H2/H3 |
| CR-C1-07 | E1, H1 | Stand test, fresh pack, 11×5.5MR, F4 cap and limiter as flown (`T-C1-THRUST-FRESH`) | Open |
| CR-C1-08 | F4 | `ARSPD_FBW_MAX` and pitch/elevon limits above VA (stall-line n at VD 7.3); body rates ≤ 3 rad/s; confirm the spin map and the cant sense | Open |
| CR-C1-18 | B2 | `loads_spanwise.json` at c 0.32 with the R3 CG range | Forwarded by A1 |
