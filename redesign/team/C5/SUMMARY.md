# C5 Landing / impact: summary

Fin-tip feet of the K09-L tailsitter (hardware by D5). Revision **C5-S1**, 2026-11-10: a simulation round on the
settled geometry (D5-R5 stack, D5-R4 cartridges, A3-R6a roll-up 2.322 kg, I 0.173 / 0.044 / 0.168 kg·m²) on top of
the hand / planar analysis C5-R5 (`LANDING.md`). Full report: `SIMULATION-REPORT.md`.

**Verdict: the as-designed feet fail four landing requirements**, and change requests CR-C5-16 to CR-C5-19 are
filed. The fixes are a 1.2 m/s hard-landing requirement (or a longer stroke), a stronger shoe and a higher side-load
basis.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Worst foot stroke, 1.5 m/s, ≤ 10° any direction (usable 35) — 3-D sim / planar | 38.6 / 31.5 | mm | `CL-C5-SIM3D-STROKE`, `CL-C5-DYN-PAIR-CUR` | `FAIL` (−10 %) |
| Touchdown tilt that bottoms a foot at 1.5 m/s (need ≥ 10) | 5.0 | ° | `CL-C5-SIM3D-BOTTOM-TILT` | `FAIL` |
| Sink speed that keeps 10° in any direction inside the stroke | 1.2 | m/s | `CL-C5-SIM3D-V-SINK-10` | `FAIL` vs 1.5 (CR-C5-17) |
| Peak n, level, at as-designed 2.32 kg / gate 2.6 kg (limit 6.0) | 6.59 / 5.88 | — | `CL-C5-SIM3D-N`, `CL-C5-DYN-N-CUR` | `FAIL` / `UNVERIFIED` (CR-C5-19) |
| Sustained foot side load — 3-D sim / hand | 39.3 / 22.9 | N | `CL-C5-SIM3D-SIDE-LOAD`, `CL-C5-FOOT-SIDE-LOAD` | `MODELLED` (CR-C5-16) |
| Shoe GER-001 RF at 34.4 N ult (D5 basis) / 59.0 N ult (sim) | 0.38 / 0.22 | — | `CL-C5-FEA-SHOE-SF-HAND`, `-SF` | `FAIL` (CR-C5-18) |
| Shoe stress, SU2 FEA / D5 beam at 111 N lip reaction | 106 / 38.1 | MPa | `CL-C5-FEA-OVER-BEAM` 2.78 | `CHECKED` (GCI 0.35 %) |
| Tip-over, pod side: worst flying / corner bound (limit 30) | 32.0 / 30.7 | ° | `CL-C5-TIPOVER-WORST`, `-B3-CORNER` | `UNVERIFIED` |
| Broadside landing wind limit — 3-D sim / static (card 5) | 4.0 / 4.44 | m/s | `CL-C5-SIM3D-V-BROADSIDE`, `CL-C5-V-LAND-BROADSIDE` | `FAIL` (CR-C5-05) |
| Spanwise landing wind limit (gust 8) | 8.0 | m/s | `CL-C5-SIM3D-V-SPANWISE` | `MODELLED` (0 %) |
| Drift landings that tip (0.3 m/s, 10°, 128 cases) | 0 | — | `CL-C5-SIM3D-DRIFT-TIPS` | `MODELLED` |
| Wingtip TE strike onset tilt (corner cap GER-007 takes it) | 7.5 | ° | `CL-C5-SIM3D-STRIKE-TILT` | `FAIL` by intent (CR-C5-04) |
| Crush block B margin, 503 / 550 / 680 g pack | +2.4 / +7.0 / +8.9 | mm | `CL-C5-PACK-ROOM-MARGIN-*` | `UNVERIFIED` |
| Normal landings per cartridge | 2.3 (≥ 5) | — | `CL-C5-LANDINGS-PER-CARTRIDGE` | `FAIL` (CR-D5-21) |

## Verification of the simulations

| Check | Result | Status |
|---|---|---|
| 3-D sim time step, 5 levels (80 → 5 µs) | stroke 0.01 %, side load 0.1 %, tip threshold steady from 40 µs | `CHECKED` |
| 3-D sim vs planar / hand, level drop | stroke −4 % (22.6 vs 23.5 mm), n equal (5.88), free drop −2 % | `CHECKED` |
| Shoe FEA, 3 mesh levels (61 k / 108 k / 182 k hexes) | +y rim GCI 0.35 % (order 4.4); +z rim within 3.5 % | `CHECKED` |
| FEA element vs beam (cantilever strip, 3 levels) | stress +1 to +5 %, deflection −7.5 % (clamped plate) | `CHECKED` |
| Inputs still current | `CL-C5-SIM-INPUTS-STALE` = 0 | `CHECKED` |

## Files

| File | What | Status |
|---|---|---|
| `landing_calc.py`, `claims.json`, `LANDING.md` | hand / planar analysis C5-R5: stance, wind, dynamics, crash path, rules S1–S9 | `CHECKED` |
| `sim/landing_sim3d.py`, `sim/sink_sweep.py`, `sim/side_check.py` | 6-DOF touchdown on 4 crushing feet with friction, envelopes | `CHECKED` |
| `sim/fea_shoe.py`, `sim/su2fea.py`, `sim/run_fea.sh`, `sim/run_variants.sh` | gmsh + SU2 ELASTICITY FEA of the shoe, 3 levels, strip verification, fix variants | `CHECKED` |
| `landing_sim_claims.py` → `claims.sim.json` | 17 claims from the simulation records, staleness check | `CHECKED` |
| `sim/plots.py` → `sim/fig/fig-c5-s1…s5.svg` | design-system figures | `CHECKED` |
| `SIMULATION-REPORT.md`, `CHANGE-REQUESTS.md` | this round; CR-C5-16 to -19 new | open |

## Open issues

- Not yet tested: the crusher plateau (coupon), μ 0.7, the gust factor and the 100 g pack shock limit. Physical
  checks are T-C5-AIRCRAFT-DROP and T-C5-SHOE-SIDE-FAIL.
- C5 re-runs the shoe FEA on D5's new stack after CR-C5-18, and the 3-D sim after CR-C5-17 or CR-C5-19.
