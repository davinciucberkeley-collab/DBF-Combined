# Change requests from C1 (loads engineer)

Revision C1-R2 (2026-11-09). Numbers from `python -I redesign/team/C1/loads.py` at params A1-R2.

## New in R2 (open)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-C1-12 | A1 (cc E1, F4, B4) | Set `requirements.thrust_limit_per_motor_n` 17.8 → **21.1 N**. Alternative: F4 lowers the output cap so the fresh-pack rpm stays ≤ 8 590 rpm (T ≤ 17.8 N, fresh T/W 2.79). | `CL-C1-T-CAP` 21.08 N = APC 11×5.5MR at the 9 350 rpm cap (`P:propulsion.rpm_max`, B4) × E1 k_T 1.039. The 100 A limiter (`ASM-E1-ILIM`, 15.9 N per motor) is time-filtered and does not bound a step to full throttle. Only mount and motor loads change (+18 %); spar, fin joint, pod and feet are landing-governed. |
| CR-C1-13 | A1 (cc F4, A2) | Set `requirements.vd_ms` 22.4 → **27.2 m/s** (q 454 Pa). Alternative: F4 limits fixed-wing THR_MAX so level speed ≤ 17.9 m/s, shown in flight logs, and keeps 22.4. | `CL-C1-VD` = 1.25 × VH; VH = 21.8 m/s, the 11×5.5MR pitch speed at the 9 350 rpm cap (B1's 19.7 m/s was with the 11×4.5MR). VC 16 m/s does not govern. The envelope already runs at 27.2 (`CL-C1-VD-ENV`). |
| CR-C1-14 | B1 | Re-run `CL-B1-VMAX` with the 11×5.5MR, the 9 350 rpm cap and c 0.32; C1 then replaces the pitch-speed proxy in `CL-C1-VH`. | VH sets VD and every flight q; B1's 11×4.5MR top speed (19.7) already exceeds that prop's pitch speed at the cap (17.8), so the proxy may be low. |
| CR-C1-15 | B2, D6 (cc F4) | Re-size the elevon hinge moment and servo torque at VD 27.2 m/s (B2 used 19.5 m/s: ×1.95 → ~5.9 kgf·cm at 25°), or adopt a deflection schedule (full travel to VA 20.5 m/s, ≤ 1/3 at VD, FAR 23.441 practice) that F4 enforces. Elevon panel limit load 31.9 N/m at CN 1.0 (`data/envelope.json`). | `CL-C1-Q-VD` 454 Pa vs 233 Pa at 19.5 m/s |
| CR-C1-16 | A1 (cc A2) | Set `requirements.load_factor_limit_pos` 3.0 → **3.4**; keep `load_factor_limit_neg` −1.5. | `CL-C1-GUST-N-POS` 3.36 at 21.8 m/s with B2's CL_α 3.58 /rad and the 8 m/s gust line to VD 27.2. Spar sizing is unchanged (landing governs); wing shear and torsion use 3.36 already. |
| CR-C1-17 | A1, C5, D5 | Restate `requirements.foot_crush_stroke_min_m`: **≥ 41 mm at η 0.5, or ≥ 26 mm with a constant-force crush core (η ≥ 0.8)**. Recommend the constant-force core: a linear foam foot 45 mm tall bottoms at ~70 % strain (~32 mm, n_L ≈ 7.6). | `CL-C1-N-LAND-STROKE-MIN` 6.07 at 40 mm (−1 %); `CL-C1-FOOT-STROKE-REQ` 40.5 mm. Foot height stays ≥ 45 mm: the wingtip clears a 10° roll error by 0.01° (`CL-C1-WINGTIP-STRIKE-ANGLE` 10.01°). |
| CR-C1-18 | B2 | Re-run `out/loads_spanwise.json` at c 0.32 (AR 3.59) with the R1 CG range; C1 re-runs on it. | `ASM-C1-B2-SPANLOAD` is the c 0.30 run (centroid 0.423 b/2) |
| CR-C1-19 | A3 | Confirm the pack station `CL-A3-PACK-X-REQ` (−0.034 m) after CR-A3-11; C1 reads it. MC-C (402 g growth at the pod centre) puts the CG at 0.036 m, ahead of the 0.040 m limit: if A1 places growth elsewhere, tell C1. | Mass configurations bound the root bending and the station loads |

## Carried from R1

| # | To | What | State |
|---|---|---|---|
| CR-C1-01 | C5, D5 | Feet 45 mm beyond the TE, crush stroke for n_L ≤ 6 | Adopted (D-11, D-14); stroke wording refined by CR-C1-17 |
| CR-C1-02 | H3, C5 | Parked on its feet in 8 m/s it slides (μ needed 0.68 > 0.5) and tips at 8.8 m/s: lay it flat between flights in gusts, or grip pads μ ≥ 0.7 | Open (`CL-C1-STANCE-MU-REQ`, `CL-C1-STANCE-TIP-WIND`) |
| CR-C1-03 | C4, D3, C5 | Tip-over onto the upper tube ends (4.6 J, 1.56 m/s) is a damage case: mounts fail before the tube | Adopted (D-23) |
| CR-C1-04 | D3, D7, H3 | Marked carry point + "do not lift by the motors" label, or C4 sizes the fin joint to G2 (9.4 vs 7.2 N·m limit) | Open |
| CR-C1-05 | D7 | Box cradle foam stroke ≥ 64 mm for the 0.3 m drop | Closed by D-22 (70 mm): n_T 9.57 ≤ 10.34. D7: 70 mm is **stroke**, ~0.10–0.12 m of block |
| CR-C1-06 | A1 | Requirement keys for n, VD, landing n, thrust limit | Done (D-14); values updated by CR-C1-12, -13, -16 |
| CR-C1-07 | E1, H1 | Stand test on a 16.8 V pack, now with the **11×5.5MR**, the F4 output cap and the 100 A limiter as flown: step to full throttle, log peak thrust, torque, rpm (`T-C1-THRUST-FRESH`) | Open |
| CR-C1-08 | F4 | `ARSPD_FBW_MAX` ≤ 22 m/s and pitch/elevon limits in manual modes above VA 20.5 m/s (stall-line n at VD 5.26 > 3.36); body rates ≤ 3 rad/s; confirm the motor spin map (C1 assumes UR and LL alike) | Open, numbers updated |
| CR-C1-09 | B2, B3 | CLmax, CLmin, lift slope, Cm, elevon effectiveness, strip loads | Closed by CR-B2-07 (now used) |
| CR-C1-10 | A2 | `R-LOADS` basis | Superseded by CR-C1-12, -13, -16, -17 |
| CR-C1-11 | C6 | Size the mount clamp for the prop-nut torque 1.5 N·m (3.2 N·m design); use `data/envelope.json#joints` for every other joint | Open |
