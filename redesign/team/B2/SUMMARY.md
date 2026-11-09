# B2 — Wing aero engineer (K09-L)

Status: `PROPOSED`, revision B2-R2 (re-run at params A1-R2 for CR-A1-14). Report: [`WING-AERO.md`](WING-AERO.md).
Claims: `claims.json` (21 claims, 2 tests). Change requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md).

**Verdict.** S5010, rectangular, no twist, spar on the camber line. At c 0.32 m the trimmed CLmax is 0.80 at
SM 5 %, which gives an **11.91 m/s stall at 2.6 kg: `R-STALL` passes by 0.8 %** (the 12.25 m/s FAIL was the c 0.30
value). At the forward end of the CG range (SM 7.8 %) the stall is 12.06 m/s, a 0.5 % FAIL (CR-B2-11). The fins
at x 0.045 m now make the wing directionally stable, and the servo torque rises to 3.93 kgf·cm (CR-B2-10).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Section | S5010, t/c 9.82 % | — | `airfoils/s5010.dat` | `PROPOSED` |
| Planform, twist | rectangular 1.15 × 0.32, 0° | m, deg | `WING-AERO.md` §4 | `PROPOSED` |
| XFOIL Re stall / cruise / dive | 2.6e5 / 3.5e5 / 4.5e5 | — | `P:b2.xfoil.re_*` (follow the chord) | `CHECKED` (stall Re ±1 %) |
| Trimmed wing CLmax, SM 5 % / forward CG SM 7.8 % | 0.798 / 0.778 | — | `CL-B2-CLMAX-DESIGN`, `CL-B2-CLMAX-FWD` | `UNVERIFIED` |
| Stall at 2.6 kg, SM 5 % | 11.91 | m/s | `CL-B2-STALL-GATE` | `UNVERIFIED`, passes 12 m/s by 0.8 % |
| Stall at 2.6 kg, forward CG | 12.06 | m/s | `CL-B2-STALL-GATE-FWD` | `FAIL` −0.5 % (CR-B2-11) |
| 1.3 Vs at 2.6 kg, SM 5 % / forward | 15.48 / 15.68 | m/s | `CL-B2-TRANSITION-GATE`, `-FWD` | `UNVERIFIED`, pass vs 16 m/s |
| Stall starts at | y 0.07–0.17 m (inboard elevon), tips last | m | FIG B2-03 | `UNVERIFIED` |
| Neutral point, wing + fins, props off (was 0.0695 at c 0.30) | 0.0738 (23.0 % c) | m | `P:b2.avl.xnp_m` | `UNVERIFIED` |
| Oswald factor, wing + fins (was 0.93) | 0.94 (SM 5 %), 0.92 (CG 0.044) | — | `P:b2.avl.e_oswald` | `UNVERIFIED` |
| Cn_β, wing + fins, props off (was −0.105) | +0.052 | 1/rad | `P:b2.avl.cnb_per_rad` | `UNVERIFIED` |
| Wing lift slope | 3.48 | 1/rad | `CL-B2-CLA-3D` | `UNVERIFIED` |
| Elevon effectiveness η | 0.61 | — | `CL-B2-ELEVON-ETA` | `UNVERIFIED` |
| Hinge moment per servo, 25°, 20.8 m/s | 0.257 | N·m | `CL-B2-HINGE-MOMENT` | `UNVERIFIED` |
| Servo stall torque required (was 3.04) | 3.93 | kgf·cm | `CL-B2-SERVO-TORQUE-REQ` | `UNVERIFIED` |
| Root bending / torsion, 1 g | 3.09 / 0.32 | N·m | `CL-B2-ROOT-BM-1G`, `-TORSION-1G` | `UNVERIFIED` |
| Negative section clmax (was −0.38) | −0.435 | — | `CL-B2-CLMIN-2D` | `UNVERIFIED` |
| Spar centre z (equal cover 4.6 mm); params +6.6 passes | +7.0 | mm | `CL-B2-SPAR-Z-MID` | `UNVERIFIED` |

## Files

| File | What |
|---|---|
| `xfoil_wing.py` | 76 polars (4 sections, Re 2.0–4.5e5, design Re from the chord, Ncrit 5/9, elevon −15…+10°), 40 hinge cases, panel convergence |
| `avl_wing.py` | wing + fins from params: trim with viscous cm, critical-section CLmax, CG, static-margin and twist sweeps, lattice convergence, loads |
| `results_to_params.py` → `params.json` | run results the proof chain reads (`P:b2.*`) |
| `wing_claims.py` → `claims.json` | claims, assumptions, tests (proofkit) |
| `plots_wing.py` → `fig/B2-0*.svg` | polars, clmax vs elevon, span loading and stall margin, hinge moments |
| `out/loads_spanwise.json` | strip loads, shear, bending, torsion per N of half-lift, for C1/C2 |

## Checks

| Check | Result | Status |
|---|---|---|
| XFOIL 160/220/300 panels, Re 3.5e5 | clmax ±0.7 %, cd and cm unchanged | `CHECKED` |
| AVL 3 lattice levels | Xnp ±0.05 mm, CLα ±0.1 % | `CHECKED` |
| XFOIL branch filter on η | Re 3.5e5 δ −10° polar rejected (branch jump); η 0.606 from Re 2.6e5 | `CHECKED` |
| Hand calcs (Helmbold, thin-airfoil flap, hinge moment, elliptic centroid) | within 6 % / as expected | `CHECKED` |
| `python -I redesign/proofs/build_graph.py` | no B2 drift or error; A1, B1, B3 drift on new B2 values (they re-run) | `CHECKED` |
| Slow-flight stall, servo bench | `T-B2-STALL`, `T-B2-HINGE` planned | `UNVERIFIED` |

## Open issues

| Issue | Owner |
|---|---|
| `R-STALL` −0.5 % at the forward CG: forward SM ≤ 6.4 % or R-STALL stated at the SM floor (CR-B2-11) | B3, A1 |
| Elevon at CLmax −9.8° (SM 5 %) to −14.6° (SM 7.8 %); B3's ≤ 10° up-trim rule leaves almost no CG range | B3 |
| Servo ≥ 3.93 kgf·cm: heavier than the 15 g servo in `mechanisms` (CR-B2-10) | D6, A3 |
| XFOIL clmax and low-Re cm not validated; the twin's stall and trim close it | B2, H2 |
