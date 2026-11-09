# B2 — Wing aero engineer (K09-L)

Status: `PROPOSED`. Report: [`WING-AERO.md`](WING-AERO.md). Claims: `claims.json` (16 claims, 2 tests).
Change requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md).

**Verdict.** S5010 section, rectangular, no twist, spar on the camber line. Trimmed CLmax 0.80 gives a 12.25 m/s
stall at 2.6 kg: `R-STALL` fails by 2 % and 1.3 Vs needs a 16 m/s cruise. A 0.32 m chord fixes both (CR-B2-01).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Section | S5010 (was MH 45), t/c 9.82 % | — | `airfoils/s5010.dat` | `PROPOSED` |
| Planform, twist | rectangular 1.15 × 0.30, 0° | m, deg | `WING-AERO.md` §4 | `PROPOSED` |
| Trimmed wing CLmax, SM 5 % | 0.80 | — | `CL-B2-CLMAX-DESIGN` | `UNVERIFIED` |
| Stall at 2.6 kg | 12.25 | m/s | `CL-B2-STALL-GATE` | `FAIL` (−2 % vs 12) |
| 1.3 Vs at 2.6 kg | 15.9 | m/s | `CL-B2-TRANSITION-GATE` | `FAIL` vs 15 m/s |
| Stall starts at | y 0.07–0.17 m (inboard elevon), tips last | m | FIG B2-03 | `UNVERIFIED` |
| Neutral point, wing + fins | 0.0695 | m | `P:b2.avl.xnp_m` | `UNVERIFIED` (agrees with B3) |
| Oswald factor, wing + fins | 0.93 | — | `P:b2.avl.e_oswald` | `UNVERIFIED` |
| Elevon effectiveness η | 0.61 | — | `CL-B2-ELEVON-ETA` | `UNVERIFIED` |
| Hinge moment per servo, 25°, 19.5 m/s | 0.199 | N·m | `CL-B2-HINGE-MOMENT` | `UNVERIFIED` |
| Servo stall torque required | 3.04 | kgf·cm | `CL-B2-SERVO-TORQUE-REQ` | `UNVERIFIED` |
| Root bending / torsion, 1 g | 3.10 / 0.36 | N·m | `CL-B2-ROOT-BM-1G`, `-TORSION-1G` | `UNVERIFIED` |
| Spar centre z (equal cover 3.7 mm) | +6.6 | mm | `CL-B2-SPAR-Z-MID` | `UNVERIFIED` (tube OD) |

## Files

| File | What |
|---|---|
| `xfoil_wing.py` | 64 polars (4 sections, Re 2.0–4.0e5, Ncrit 5/9, elevon −15…+10°), 40 hinge cases, panel convergence |
| `avl_wing.py` | wing + fins: trim with viscous cm, critical-section CLmax, CG and twist sweeps, lattice convergence, loads |
| `results_to_params.py` → `params.json` | run results the proof chain reads (`P:b2.*`) |
| `wing_claims.py` → `claims.json` | claims, assumptions, tests (proofkit) |
| `plots_wing.py` → `fig/B2-0*.svg` | polars, clmax vs elevon, span loading and stall margin, hinge moments |
| `out/loads_spanwise.json` | strip loads, shear, bending, torsion per N of half-lift, for C1/C2 |
| `airfoils/*.dat` | S5010, MH 45, MH 60, E186 (UIUC, checked) |

## Checks

| Check | Result | Status |
|---|---|---|
| XFOIL 160/220/300 panels | clmax ±1 %, cd and cm unchanged | `CHECKED` |
| AVL 3 lattice levels | Xnp ±0.1 mm, CLα ±0.2 % | `CHECKED` |
| Hand calcs (Helmbold, thin-airfoil flap, elliptic centroid) | within 6 % / as expected | `CHECKED` |
| `python -I redesign/proofs/build_graph.py` | OK, every stored number re-computes | `CHECKED` |
| Slow-flight stall, servo bench | `T-B2-STALL`, `T-B2-HINGE` planned | `UNVERIFIED` |

## Open issues

| Issue | Owner |
|---|---|
| `R-STALL` / `R-TRANSITION` fail: chord 0.32 m or mass (CR-B2-01) | A1, B1 |
| Fins directionally destabilising (Cn_β −0.105 /rad); aft CG limit 0.075 m unstable | B3, D3 |
| XFOIL clmax and low-Re cm not validated; the twin's stall and trim close it | B2, H2 |
