# Wing aerodynamics — K09-L (B2)

Status: `PROPOSED` (analysis complete, nothing flown). Revision B2-R2 (2026-11-09), re-run at params A1-R2: chord
0.32 m, half-fins 0.275 m chord at x 0.045–0.32 m, CG target 0.044 m, cruise 16 m/s (CR-A1-14). Covers section,
planform, twist, stall progression, elevon hinge moments and the spanwise loading that C1/C2 size the wing from.
Props-off, no pod; tools XFOIL 6.99 and AVL 3.52.

**Verdict.** S5010 section, rectangular, untwisted, spar on the camber line: unchanged. At c 0.32 m the trimmed
wing reaches **CLmax 0.80 at 5 % static margin**, so the stall at the 2.6 kg gate is **11.91 m/s**: `R-STALL`
(≤ 12 m/s) **passes by 0.8 %**, and 1.3 Vs = 15.5 m/s passes the 16 m/s cruise by 3 %. The c 0.30 FAIL (12.25 m/s)
no longer applies. **At the forward end of the CG range (SM 7.8 %) the up-elevon costs CLmax (0.78) and the stall
is 12.06 m/s, a 0.5 % FAIL** (CR-B2-11). The longer chord and the 16 m/s cruise raise the elevon hinge moment, so
each servo now needs **≥ 3.9 kgf·cm** (was 3.0, CR-B2-10). With the fins moved aft to x 0.045–0.32 m, the props-off
wing + fins are **directionally stable** (Cn_β +0.052 /rad; was −0.105 with the fins at −0.10).

## 1. Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Section | S5010, t/c 9.82 % | — | `team/B2/airfoils/s5010.dat` | `CHECKED` (coordinates vs UIUC) |
| Re at stall / cruise / dive (c 0.32 m) | 2.57e5 / 3.46e5 / 4.50e5 | — | `CL-B2-RE-STALL`, ν 1.48e-5 m²/s | `UNVERIFIED` |
| XFOIL design Re (follow the chord) | 2.6e5 / 3.5e5 / 4.5e5 | — | `P:b2.xfoil.re_stall`, `re_cruise`, `re_dive` | stall Re within 1 % (`CL-B2-RE-STALL-DEV`) |
| Section clmax, elevon neutral, Re 2.6e5 | 1.256 | — | `P:b2.xfoil.clmax_2d_stall` | `UNVERIFIED` |
| Trimmed wing CLmax, SM 5 % (critical section) | 0.798 | — | `CL-B2-CLMAX-DESIGN` | `UNVERIFIED` (T-B2-STALL) |
| Trimmed wing CLmax, forward CG (SM 7.8 %) | 0.778 | — | `CL-B2-CLMAX-FWD` | `UNVERIFIED` |
| Stall at 2.6 kg, SM 5 % / forward CG | 11.91 / 12.06 | m/s | `CL-B2-STALL-GATE`, `-GATE-FWD` | pass +0.8 % / `FAIL` −0.5 % |
| Stall at the predicted 2.495 kg (A3), SM 5 % / forward | 11.66 / 11.81 | m/s | scaled √m | pass |
| 1.3 Vs at 2.6 kg, SM 5 % / forward CG | 15.48 / 15.68 | m/s | `CL-B2-TRANSITION-GATE`, `-GATE-FWD` | pass vs 16 m/s (+3 % / +2 %) |
| Wing lift slope (wing + fins) | 3.48 | 1/rad | `CL-B2-CLA-3D` | `UNVERIFIED` |
| Neutral point, wing + fins (no pod, props off) | 0.0738 (23.0 % c) | m | `P:b2.avl.xnp_m` | `UNVERIFIED`; wing alone 0.0735 |
| CG for 5 % static margin (this model) | 0.0578 | m | Xnp − 0.05 c | B3 owns the CG range |
| Static margin at params CG 0.040 / 0.044 / 0.049 m | 10.5 / 9.3 / 7.7 | % c | `out/avl_results.json#cg_sweep` | props-off; B3 adds pod and props |
| Oswald factor, trimmed fit CL 0.3–0.9, wing + fins | 0.94 (SM 5 %), 0.92 (CG 0.044) | — | `P:b2.avl.e_oswald` | `UNVERIFIED` (upper bound, no pod) |
| Wing profile + induced drag, trimmed | CD = 0.0069 + 0.094 CL² | — | `P:b2.avl.cd0_wing` | `UNVERIFIED` |
| Cn_β / Cl_β, α 4°, CG 0.044 | +0.052 / +0.003 | 1/rad | `P:b2.avl.cnb_per_rad` | `UNVERIFIED`; meets `cnbeta_min` 0.03 props-off |
| Elevon effectiveness η (XFOIL / thin airfoil) | 0.61 | — | `CL-B2-ELEVON-ETA` | `UNVERIFIED` |
| Viscous cm correction to AVL | −0.0103 | — | `CL-B2-DCM-VISC` | `UNVERIFIED` |
| Elevon trim at 16 m/s / at CLmax (SM 5 %) | −5.4 / −9.8 | deg | `out/avl_results.json#design_trim` | `UNVERIFIED` |
| Hinge moment per servo, 25°, 20.8 m/s | 0.257 | N·m | `CL-B2-HINGE-MOMENT` | `UNVERIFIED` |
| Servo stall torque required (× 1.5) | 3.93 | kgf·cm | `CL-B2-SERVO-TORQUE-REQ` | `UNVERIFIED` (T-B2-HINGE) |
| Spar centre z for equal foam cover (x 0.08 m) | +7.0 | mm | `CL-B2-SPAR-Z-MID` | `UNVERIFIED`; params +6.6 passes (4.2 mm cover) |
| Twist | 0 | deg | §4 | `PROPOSED` |

## 2. Section selection

Four reflexed plank sections were run with the same XFOIL set-up (220 panels, Ncrit 9) on the same AVL wing,
trimmed at the params CG target 0.044 m (SM 9.3 % props-off). The deciding number is the **trimmed** CLmax: on a
plank the elevons trim up, which costs section clmax.

| Section | clmax Re 2.6e5 | cm c/4 at cl 0.7 | cd at cl 0.3 / 0.5, Re 3.5e5 | Post-stall cl drop (3°) | η | Trimmed CLmax, CG 0.044 |
|---|---|---|---|---|---|---|
| **S5010** | **1.256** | **−0.003** | 0.0076 / 0.0083 | 0.08 | 0.61 | **0.770** |
| MH 45 | 1.211 | −0.007 | 0.0072 / 0.0080 | 0.09 | 0.70 | 0.751 |
| MH 60 | 1.181 | −0.011 | 0.0072 / 0.0079 | 0.05 | 0.69 | 0.726 |
| E186 | 1.026 | +0.013 | 0.0090 / 0.0091 | 0.17 | 0.58 | 0.573 |

The S5010 keeps +2.5 % trimmed CLmax over the MH 45 (−1.3 % stall speed) at +0.0003–0.0004 cd in cruise (≈ +1 %
cruise power). At the new Re the two stall about equally softly (0.08 vs 0.09). Same thickness, same hot-wire
process. Coordinates: UIUC, t/c checked against the published value (`SRC-B2-S5010-COORD`).

![Polars](fig/B2-01-polars.svg)

`FIG B2-01 — Section polars, Re 2.6e5 (stall at c 0.32 m), Ncrit 9; blue = S5010.`

## 3. Trimmed CLmax and stall progression

Method: AVL trims Cm = 0 with the elevons, with the XFOIL section cm added (`CL-B2-DCM-VISC`) and the elevon gain set
to η. Each strip's cl is compared with the XFOIL clmax at that strip's deflection. The clmax(δ) used is the lower
of Re 2.6e5 and 3.5e5 at each δ, made non-increasing towards up-elevon to remove XFOIL scatter (FIG B2-02).

| Static margin (props-off NP 0.0738 m) | CG x (m) | Trimmed CLmax | Elevon at CLmax | Vs at 2.6 kg (m/s) |
|---|---|---|---|---|
| 3 % | 0.0642 | 0.863 | −6.6° | 11.45 |
| **5 % (SM floor, design)** | **0.0578** | **0.798** | **−9.8°** | **11.91** |
| 6 % | 0.0546 | 0.788 | −11.5° | 11.98 |
| 7 % | 0.0513 | 0.782 | −13.2° | 12.03 |
| **7.8 % (forward end: floor + B3 range width 9 mm)** | 0.0488 | **0.778** | −14.6° | **12.06** |
| 9.3 % (params CG target 0.044) | 0.0440 | 0.770 | −17.2° | 12.12 |
| 10.5 % (params forward 0.040) | 0.0400 | 0.763 | −19.3° | 12.18 |

The stall speed depends on the static margin, not on the CG station: a forward CG needs more up-elevon, so the
inboard elevon strip reaches its (lower) clmax sooner. `R-STALL` holds up to SM 6.4 %. The params CG range
(0.040–0.049 m) was derived by B3 at c 0.30 with the fins at −0.10. Against this props-off NP it is SM 7.7–10.5 %;
B3 re-derives it with the pod and props (D-17).

Stall starts at the inboard end of the inboard elevon (y 0.07 m) and spreads outboard along that panel
(0.07 → 0.08 → 0.10 → 0.13 → 0.17 m). The tips stay below their limit (FIG B2-03). Because the root stalls first and
the tips last, the stall is benign and roll authority is kept at the break.

![Spanwise loading and stall margin](fig/B2-03-span-stall.svg)

`FIG B2-03 — Left: cl/CL along the half-span. Right: cl / local clmax; red = stall; shaded = elevons; dashed = fin.`

![clmax vs elevon](fig/B2-02-clmax-elevon.svg)

`FIG B2-02 — Section clmax vs elevon deflection; line = envelope used, dots = Re 2.6e5 / 3.5e5 runs.`

## 4. Planform and twist

| Option | Trimmed CLmax (SM 5 %) | CD at CL 0.5 | Decision |
|---|---|---|---|
| **Rectangular, 0° twist** | **0.798** | 0.0301 | **keep** |
| −2° linear washout | 0.782 | 0.0301 | no: the critical strip is inboard, washout loads it more |
| −4° linear washout | 0.767 | 0.0303 | no |

The rectangular wing stalls at the root and carries its lift centroid at 0.422 of the semi-span (elliptic 0.424).
Washout buys nothing and costs CLmax. Taper or sweep would cut the root chord where the pack and spar sit and would
break the one-piece box fit, so neither was studied further.

## 5. Elevons (hinge moments; B3 sizes the area)

| Item | Value | Unit | Note |
|---|---|---|---|
| Hinge line | 0.78 c, upper-surface tape hinge | — | `params.json#wing.elevon` |
| XFOIL η (cm per degree vs thin airfoil) | 0.61 | — | −10…0°, cl 0.5, Re 2.6e5 (Re 3.5e5 polar rejected, §8) |
| AVL control derivatives (η applied, CG 0.044) | Cm_δe −0.0061 /deg · CL_δe 0.0154 /deg · Cl_δa −0.0029 /deg · Clp −0.31 | — | inputs to B3 |
| Hinge coefficient HMOM/(q c²), ±25°, α −4…8°, Re 4.5e5 | 0.0211 (inviscid, design) / 0.0125 (viscous, converged) | — | FIG B2-04 |
| Per servo (two panels, 0.45 m), 20.8 m/s, q 265 Pa | 0.257 | N·m | 1.3 × 16 m/s cruise (`ASM-B2-DIVE-FACTOR`) |
| Required servo stall torque (× 1.5) | 0.386 (3.93) | N·m (kgf·cm) | a 9 g micro servo (≈ 1.5–2 kgf·cm) is not enough |
| Pushrod force, 12 mm horn arm, one servo | 21.4 | N | for C6 / D6 |

Viscous up-deflection cases do not converge (the flow separates on the lower-surface kink), so the inviscid value
is the design value for both directions (`ASM-B2-HINGE-INVISCID`).

![Hinge moment](fig/B2-04-hinge.svg)

`FIG B2-04 — S5010 hinge moment vs deflection, Re 4.5e5; band = α −4…8°.`

## 6. Loads inputs for C1 and C2

Trimmed, SM 5 % (CG 0.0578 m), per N of half-wing lift (multiply by n·m·g/2). Full strip data:
`out/loads_spanwise.json` (regenerated at c 0.32).

| y (m) | 0 | 0.05 | 0.10 | 0.20 | 0.30 | 0.32 (fin) | 0.40 | 0.50 (spar end) | 0.575 |
|---|---|---|---|---|---|---|---|---|---|
| Shear / half-lift | 1.000 | 0.886 | 0.792 | 0.595 | 0.365 | 0.327 | 0.212 | 0.040 | 0 |
| Bending (m) | 0.243 | 0.196 | 0.154 | 0.087 | 0.041 | 0.034 | 0.0134 | 0.0017 | 0 |
| Torsion about spar, nose-up + (m), CL 0.8 | 0.026 | 0.025 | 0.023 | 0.019 | 0.014 | 0.013 | 0.010 | 0.002 | 0 |
| Torsion, CL 0.3 (dive) | 0.033 | 0.031 | 0.030 | 0.024 | 0.017 | 0.016 | 0.012 | 0.003 | 0 |

| Item for C1 | Value | Unit | Source |
|---|---|---|---|
| Root bending / torsion at 1 g, 2.6 kg | 3.09 / 0.32 | N·m | `CL-B2-ROOT-BM-1G`, `CL-B2-ROOT-TORSION-1G` |
| Trimmed CLmax (manoeuvre envelope) | 0.80 | — | `CL-B2-CLMAX-DESIGN` |
| Negative section clmax | −0.435 (use −0.44) | — | `CL-B2-CLMIN-2D`, Re 3.5e5 |
| Wing lift slope for gusts | 3.48 | 1/rad | `CL-B2-CLA-3D` (section 6.61 /rad) |
| Broadside CN (hover, wind on the face) | 1.2 | — | flat plate AR 3.6 (Hoerner); same as `ASM-C1-CD-PLATE` |

The loading shape barely changes with CL (centroid 0.2416–0.2427 m from CL 0.3 to 1.0), so one shape serves all
symmetric cases. Not included: pod, prop slipstream, fin side loads (B3/B4/C4).

## 7. Spar placement

At x = 0.08 m (x/c 0.25) the S5010 is +22.6 / −8.6 mm about the chord line (31.2 mm thick). Centred on the camber
line (z = +7.0 mm), the 22 mm tube has 4.6 mm of foam above and below (`CL-B2-SPAR-COVER-CENTRED`, ≥ 2 mm). The
params value +6.6 mm (set at c 0.30) leaves 5.0 mm above and 4.2 mm below (`CL-B2-SPAR-COVER`). That passes, so
CR-B2-09 is optional.

## 8. Checks

| Check | Result | Status |
|---|---|---|
| XFOIL panels 160 / 220 / 300 (MH 45, Re 3.5e5) | clmax 1.234 / 1.241 / 1.250 (±0.7 %); cm0 −0.0018 and cd at cl 0.5 0.0080 unchanged | `CHECKED` |
| AVL lattice, 3 levels (8×0.6, 12×1, 18×1.6) | CLα 3.473 / 3.477 / 3.480; Xnp 0.07373 / 0.07376 / 0.07382 m; elevon at CL 1.0 ±3 % | `CHECKED` |
| Ncrit 5 vs 9 (outdoor, tape skin), S5010 Re 2.6e5 | clmax 1.274 vs 1.256 (+1.4 %): Ncrit 9 is the conservative choice | `CHECKED` |
| Stall Re vs the polar Re | 2.57e5 vs 2.6e5: 1 % (`CL-B2-RE-STALL-DEV` ≤ 10 %) | `CHECKED` |
| XFOIL branch check for η | S5010 Re 3.5e5, δ −10°: cl(α) jumps between a lower-surface-separated and an attached branch (cm +0.02 off its neighbours). `smooth_at()` in `avl_wing.py` rejects that polar; η from Re 2.6e5 = 0.606, the same value Re 2.3e5 and 3.0e5 gave at c 0.30 | `CHECKED` |
| Hand: Helmbold lift slope, AR 3.59 | 3.70 /rad (2π) / 3.79 (a₀ 6.61) vs AVL 3.48 (rectangular, elevon gaps): −6 %, expected sign | `CHECKED` |
| Hand: thin-airfoil flap effectiveness | dcm/dδ −0.0113 /deg vs XFOIL −0.0068: η 0.61, within the 0.5–0.7 usual for plain flaps at low Re | `CHECKED` |
| Hand: hinge moment | 0.0211 × ½·1.225·20.8² × 0.32² × 0.45 = 0.257 N·m | `CHECKED` |
| Lift centroid | 0.422 b/2, elliptic 4/(3π) = 0.424 | `CHECKED` |
| Fins in AVL | x 0.045–0.32 m, 0.275 m chord, ±0.19 m (params A1-R2; `out/avl/s5010_base.avl`) | `CHECKED` |
| Proof chain | `python -I redesign/proofs/build_graph.py`: no B2 drift or error; A1, B1 and B3 drift on the new B2 values until they re-run | `CHECKED` |

## 9. Open issues

| Issue | Owner | Effect |
|---|---|---|
| `R-STALL` fails by 0.5 % at the forward end of the CG range (SM 7.8 %) | B3, A1 (CR-B2-11) | forward SM ≤ 6.4 %, or the gate at ≤ 2.57 kg, or R-STALL stated at the SM floor |
| Elevon at CLmax −9.8° at SM 5 %, −14.6° at SM 7.8 %: B3's "≤ 10° up-trim at CLmax" rule leaves almost no CG range | B3 | B3 re-derives with pod and props (D-17) |
| Servo torque up to 3.93 kgf·cm (heavier servo than the 15 g in `mechanisms`) | D6, A3 (CR-B2-10) | ≈ +5–10 g |
| XFOIL clmax not validated against test data at Re 2.6e5 | B2, H2 | twin / XPS slow-flight stall (`T-B2-STALL`) |
| XFOIL up-elevon polars have two branches near Re 3.5e5 | B2 | η from the smooth Re 2.6e5 polar; trim checked in the first FBWA flight |
| Hinge moment excludes gap and tape friction | D6 | covered by the 1.5 factor; bench test `T-B2-HINGE` |

## 10. Re-run

From the repo root, in order (XFOIL ~6 min for new Re, cached after; AVL ~1 min):
`python -I redesign/team/B2/xfoil_wing.py` → `python -I redesign/team/B2/avl_wing.py` →
`python -I redesign/team/B2/results_to_params.py` → `python -I redesign/team/B2/wing_claims.py` →
`python redesign/team/B2/plots_wing.py` (matplotlib needs the user site, so no `-I`) →
`python -I redesign/proofs/build_graph.py`. The XFOIL design Re follow `wing.chord_m`, the stall limit and the
cruise speed, so a chord change re-runs the right polars. Raw inputs and outputs: `out/xfoil/`, `out/avl/`.
