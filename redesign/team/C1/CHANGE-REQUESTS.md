# Change requests from C1 (loads engineer)

Revision **C1-R5** (2026-11-10, D-65 action items). Numbers from `python -I redesign/team/C1/loads.py` at params
A1-R5 (landing_n_design **6.6**, CG range [0.0466, 0.0514] m, z 0.0185 m, pod nose -0.140, pack datum -0.032) and
A3-R7 (`CL-A3-GROUPS`, `CL-A3-IYY` 0.0461 kg m2, basic 2.342 kg), C5's `CL-C5-SIM3D-SIDE-LOAD` 39.3 N. All loads
limit unless marked ult (= 1.5 x limit). Inputs are live: a later A3/C5/D5 republish moves these by a few %.

## New in R5 (open)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-C1-35 | C4, C6, D3 (cc A1, C5, D5) | **Fin roots at n 6.6 and the 39.3 N side load.** Re-run `fin_structures_d3.py` / `joints.py` on: fin-joint moment ult **22.46 N m** (design x 1.15 x 1.25 = **32.28**), fin-joint force ult **89.15 N**, half-fin torsion at the wing plane **12.63 / 18.94 N m** lim / ult, half-fin bending ult **16.33 N m**, foot cut force ult **79.75 N** (L4/L5 govern all but the force, L1). Read `CL-C1-G3-CAN-F` (**23.46 N** limit, 35.19 ult) in place of `ASM-C4-G3-CAN-F` (answers CR-C4-29). | Vs R4: torsion **+71 %**, joint moment +57 %, half-fin bending +43 %. Of that, n 6.6 is ~10 %, the side load the rest (`data/sensitivity_side.json`). C1's linear scaling of C4's R4 margins (estimate, C4 to replace): collar bond MS 0.16 -> about **-0.32**, fin face with shoe cheeks 0.01 -> about **-0.29**, through-core block 0.55 -> about **0.0**, brace 0.79 -> about +0.05. With C5's mu <= 0.5 pad face (29.1 N): torsion 9.38 N m, joint design 25.4 N m, block MS about +0.26, collar about -0.08, face about -0.11. |
| CR-C1-36 | D5, C5 (cc A1) | Decide the pad face: C1 recommends C5's **mu <= 0.5** option for the fin roots' sake (side load 39.3 -> 29.1 N; torsion -26 %, joint moment -21 %). Size the shoe, cartridge and fin-tip fitting to `CL-C1-FOOT-SIDE-DESIGN` **39.30 / 58.96 N** with the normal load **`CL-C1-FOOT-LEVEL-UPPER` 44.41 / 66.62 N** (supersedes CR-C1-34's 40.38 / 60.56; D5's plateau 39.58 N is now 11 % inside, `CL-C1-FOOT-D5-RATIO` 0.891). The upper bound is conservative: at the gate mass and n 6.6 C1's mean foot is 42.1 N, above the plateau a cartridge can reach. | D-65. C1 applies the side load with the corner load (36.7 N) in L4 (y) and L5 (z). |
| CR-C1-37 | C3 (cc D2, H1) | **Pack stop and pod saddle at n 6.6**: pack-to-tray resultant **42.49 N** limit / **63.73 N** ult (`CL-C1-PACK-STOP-LIM/-ULT`, L1, mostly +x into the aft stop); with the fitting and printed factors 63.73 x 1.15 x 1.25 = **91.6 N**, above the crash retention load **73.75 N** (`CL-C1-PACK-CRASH-LOAD`, now on A3's acceptance pack): the **landing now sizes the aft stop**. Replace `ASM-C3-PACK-LOADS` (R4 L1 Fx 35.4 N, MC-C only) with `data/joints.csv` J-PACK rows **both mass configs** (MC-P L1 Fx 42.46 N). Pod-to-wing (spar saddle POD-007 + bond): **75.82 / 113.73 N** (`CL-C1-POD-F-LIM`, `-ULT`), 3 % below R4 (A3 groups move the harness out of the pod). | D-65 asks C1 and C3 to check the pack stop and spar saddles at 6.6. |
| CR-C1-38 | D7 (cc A1, A2) | **Nose-drop allowance not confirmed.** With the pod nose on the nose pad (new case X6: the transport mass stops through the pod shell, saddle and bond) the airframe tolerates **n 4.98** (`CL-C1-TRANSPORT-N-ALLOW-NOSE`, J-POD governs), not `-ALLOW-X` 13.04 (X1 holds only while the cradles stop the aircraft in x). D7's formula h = (n - 1) eta eps_use t gives **0.021 m** on the 3/4 in pad, **0.014 m** on the D-62 1/2 in pad, against the **0.059 m** carried. Please (a) read `CL-C1-TRANSPORT-N-ALLOW-NOSE` in `CL-D7-NOSE-DROP-ALLOW`, and (b) either add x-stops at the cradles that hold the spar before the nose gap closes (then X1 applies, n 13.04) or keep the nose drop as label-only ("keep upright", D-53). **Aft wall: confirmed.** C1's allowable is now **n 10.76** (J-FIN force governs); the R4 value 9.22 stays a safe lower bound; demand 7.79 (C1) / 7.46 (D7). `CL-D7-AFT-N` should be limited by `CL-C1-TRANSPORT-N-ALLOW-AFT`, not `-ALLOW-X`. Floor drop unchanged: n 10.09 vs 13.19. | Answers CR-D7-24 and the D-62 forward. |
| CR-C1-39 | H1 (cc C2) | **GT-08 pad table at R5** (supersedes CR-C1-30's numbers; positions unchanged): pads y **0.120 / 0.250 / 0.355 / 0.465 m**, limit **9.01 / 5.14 / 4.44 / 6.01 N** per side (masses **0.919 / 0.524 / 0.453 / 0.613 kg**; sum 24.60 N, centroid y 0.274 m), relief pull **19.92 N** up at each tube (2.031 kg), hanger 49.2 N. **Step 2** (each side in turn, V-block under the spar at y 0.32 m): pads 3 / 4 at **4.90 / 16.10 N** (0.499 / 1.642 kg), reproduces V 21.8 N and Mx 2.61 N m outboard of the fin, cover >= 0.987. Pad 2 fell (7.90 -> 5.14 N) because the harness now rides at y 0.256 as A3 places it. | `CL-C1-PROOF-*`, `data/whiffletree.json`. CR-C1-27 (one proof, C2) still stands. |

## Answered in R5

| # | State |
|---|---|
| CR-C1-33 (A3) | **Done by A3-R7** (`CL-A3-GROUPS`, `CL-A3-CG-Z`): C1 now places the centre group, pack and harness at A3's centroids; the CG trim fell **28.7 -> 7.2 mm**. The remaining offset is C1's fin and foot lumps (fins 27 mm forward of A3's, feet 26 mm aft; `data/checks.json`). Spread still at the pod half-length; Iyy 0.90-1.02 of A3 (band 0.85-1.15). |
| CR-C4-29 | Done: `CL-C1-G3-CAN-F` 23.46 N limit, `-ULT` 35.19 N. |
| CR-C5-16, CR-C5-19 | Done: side load 39.3 / 59.0 N in L4/L5 (`CL-C1-FOOT-SIDE-DESIGN(-ULT)`), n 6.6 in every landing case. |
| CR-D7-24 | Answered by CR-C1-38 (nose allowance lower than D7's; aft wall confirmed). |
| CR-C1-29, -30, -31, -34 | Superseded by CR-C1-35, -39, -38, -36 (R5 numbers). |
| CR-B2-18 | Acknowledged: C1 reads B2's AVL table (1 g root lift moment 3.0942 N m reproduced). B2's 10.5 N m at n 3.4 is the aero moment alone; C1's net F1 root moment is 2.83 N m after the fin, station and pod inertia relief. A Schrenk shape (x 1.096 on the aero part) would add about 1 N m there; the spar is sized by L1 (13.8 N m limit), so the AVL shape is kept. |

## R4 (history)

R4 header (history): revision **C1-R4** (2026-11-10, D-50 action items). Numbers from `python -I redesign/team/C1/loads.py` at params
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
