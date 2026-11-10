# Change requests from C1 (loads engineer)

Revision **C1-R4** (2026-11-10, D-50 action items). Numbers from `python -I redesign/team/C1/loads.py` at params
A1-R4 / A1-R4a, A3-R5 roll-up (basic mass 2.3225 kg), F4's capped level speed `CL-F4-VLEVEL` 21.28 m/s. All loads
limit unless marked ult (= 1.5 x limit).

## New in R4 (open)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-C1-27 | C2 (cc H1) | **One wing limit proof.** Withdraw `T-C2-WING-PROOF` (2 x 25 N per side over \|y\| 0.33-0.50 + 51 N at an upper tube end). GT-08 runs `T-C1-WING-PROOF`: step 1 the four-pad tree (`data/whiffletree.json`), step 2 C2's padded V-block under the spar at y 0.32 m with pads 3 and 4 only at **4.85 / 15.85 N** limit (0.495 / 1.616 kg). C2 keeps the set-up, the 0.5 mm permanent-set criterion and `T-C2-TWIST`; the 51 N tube-end hang becomes `T-C1-STATION-PROOF` (G2: J-FIN 42.2 N, 8.09 N m limit). | CR-H1-13. C2's 25 N pair was an ultimate-level moment at the rejected VD 32.1 (about 5 N m at y 0.32, 2 x the 2.57 N m step 2 reproduces). Step 1 + step 2 cover the flight envelope to >= 0.99 out to pad 3 (`CL-C1-PROOF-OUT-*`). |
| CR-C1-28 | C2 | Re-run `c2_claims.py` on R4 loads, and point `CALC-C2-AE-REQ` at **`CL-C1-VD-ENV` (27.2 m/s)**, not `CL-C1-VD` (26.7, a derived check value). | Spar root Mb ult 20.38 -> **19.64 N m**, flap Mx ult 14.01 -> **12.02 N m**, torsion ult 6.95 -> **7.53 N m**, shear ult 42.7 -> **32.31 N** (`CL-C1-SPAR-MB-ULT`, `-SPAR-MX-ULT`, `-WING-TORSION-ULT`, `-WING-SHEAR-ULT`). Flutter/divergence margin must be on the speed the structure is cleared to. |
| CR-C1-29 | C4, C5, C6 (cc D3) | Re-run on the R4 inertia-matched loads: fin-joint moment ult **14.41 N m** (design x 1.15 x 1.25 = 20.7), half-fin torsion at the wing plane **7.40 / 11.10 N m** lim / ult (`CL-C1-FINHALF-T-WINGPLANE-*`, J-FINHALF collar), corner foot **32.71 N** (`CL-C1-FOOT-CORNER`, was 29.08), mount force ult **31.23 N**, motor-plane side force **8.43 N** and mount-face moment **0.49 N m** limit (`CL-C1-MOTOR-FSIDE-LIM`, `-MOTOR-MB-LIM`; cant 2.57 N included, CR-C6-21a). | Matching A3's Iyy (0.90-0.99 of A3 vs 0.72-0.82 before) raised every L4-driven load 10-14 %. `CALC-C4-STATIC-2L` drifts today (face stress +12 %, MS 1.26 -> 1.01). |
| CR-C1-30 | H1 | GT-08 pad table at R4 (supersedes CR-C1-23's numbers): pads y **0.120 / 0.250 / 0.355 / 0.465 m**, limit **8.95 / 7.66 / 4.44 / 6.04 N** per side (sum 27.08 N, centroid y 0.272 m), relief pull **19.40 N** up at each tube, hanger 54.2 N; masses 0.912 / 0.781 / 0.452 / 0.616 kg, relief 1.979 kg. Pad 4 is now a claim (`CL-C1-PROOF-Y4`, `-P4-LIM`). Add step 2 (CR-C1-27). | CR-H1-09, CR-H1-13. Tree reproduces F1 at VD (MC-C) at the pod edge (Mx 2.24 N m) and both sides of the fin. |
| CR-C1-31 | D7 (cc A2) | Axis names confirmed (answers CR-D7-14a): aircraft **x = chord = box long walls** (X1 nose, cradle-reacted; X5 aft, feet-reacted), **y = span = end walls** (wingtips). Aft-wall drop (CR-D7-14b, done as X5): use C1's allowable **n 9.22** (J-FINHALF bending governs), not 12.1; demand at 0.25 m on D5's plateaus n **7.79** (+18 %). | `CL-C1-TRANSPORT-N-AFT`, `-N-ALLOW-AFT`. Floor drop n 10.09 vs 12.45 unchanged. |
| CR-C1-32 | F4 (cc H2, B1) | Keep `CL-F4-VLEVEL-VH` as a flight-test gate: the first full-throttle FW level log at THR_MAX 70 % must show **<= 21.76 m/s** (= 27.2 / 1.25). If it shows more, C1 re-runs (VD goes up, q at VD up with V^2). Republish `CL-F4-VLEVEL` if B1's polar changes (0.14 m pod). CR-C1-08 (stall-line n 5.22 at VD) stays open, held by D-50's envelope. | `CL-C1-VH` 21.28 -> `CL-C1-VD` 26.7 <= 27.2 (+1.9 %). |
| CR-C1-33 | A3 | Publish per-group centroid and own inertia (pod group, pack, fins, stations) so C1 can drop its +/-0.1125 m centre-group spread; C1's lumped model sits **28-29 mm** ahead of the CG limits before trim. | `CL-C1-INERTIA-RATIO-MIN` 0.8975 (MC-P Iyy) with the spread already at the pod half-length cap; `data/mass_model.csv` TRIM rows. |
| CR-C1-34 | D5 (cc C5) | Size the foot cartridge and fin-tip fitting to C1's L1 upper-foot bound **40.38 N limit / 60.56 N ult** (`CL-C1-FOOT-LEVEL-UPPER(-ULT)`), not to D5's 39.58 N plateau: the margin is 2 % (`CL-C1-FOOT-D5-RATIO` 0.980). | CR-D5-23 adopted (per-type plateaus, eta 0.903 read live). Any plateau rise > 2 % makes C1's bound the lower one. |

## Answered or closed in R4

| # | State |
|---|---|
| CR-C1-20 | Closed by D-50 (THR_MAX 70 %, VD 27.2, n+ 3.4). The 32.1 m/s alternative and the 27.25 rounding are rejected; `CL-C1-VD-UNCAPPED` kept as information. |
| CR-C1-22 | Closed by D-53 (label-and-test for nose, end and lid drops; aft wall on the feet, CR-C1-31). |
| CR-C1-23 | Superseded by CR-C1-30 (R4 numbers). |
| CR-C1-18 | Done: C1 reads B2's c 0.32 strip table, CLmin 0.44, CL_alpha 3.48 /rad (CR-B2-13). |
| CR-C1-25 | Done by A3-R5 (`CL-A3-PACK-X-REQ` read live); residual trim offset is CR-C1-33. |
| CR-B2-13, CR-D5-23, CR-C6-21a, CR-H1-09, CR-H1-13, CR-D7-14 | Answered in C1-R4 (LOADS.md action-item table). |

## R3 requests (history; state in the R4 tables above)

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
| CR-C1-08 | F4 | `ARSPD_FBW_MAX` and pitch/elevon limits above VA (stall-line n at VD 5.22 at R4, was 7.3 at VD 32.1; D-50 holds it by envelope); body rates ≤ 3 rad/s; confirm the spin map and the cant sense | Open |
| CR-C1-18 | B2 | `loads_spanwise.json` at c 0.32 with the R3 CG range | Done (R4) |
