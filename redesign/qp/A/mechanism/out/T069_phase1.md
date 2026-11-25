# T-069 Phase 1 (R-PHY-09, concept A): step 1 result and STOP decision (2026-11-19)

Status: analysis only, NOT VERIFIED COMPLETE. Nothing in CAD, docs/, CHANGE-LOG, ledger or MASS-GATE was edited. No SITL. Steps 2-4 of D-215 s7 were NOT started (stop rule).
Categories: **rigid-body dynamics** (landing_a.py force histories, unchanged) + **hand-calculation part checks** (statics, beam and Saint-Venant torsion theory, finite-difference Prandtl stress function for the foam section) . No FEA, CFD, interference or flight dynamics run. All allowables are EST (no coupons).
CG: `redesign/qp/A/sitl/cad_mass.json` (2026-11-18, 1.27324 kg basic). **Flag: T-067 (another agent) may change printed-part masses and CG; the post-T-067 CG was not available and is not used.** Loads are unaffected in the P15/P16 results below (they use the force histories, M_GATE 1.50 kg).

## Commands (cwd `redesign/qp/A/structures`, Python -I)
| # | Command | Exit | Wall | Output |
|---|---|---|---|---|
| 1 | `python -I landing_path_a.py` (edited: F-4, F-5, bond-integrity relabel, P1 PSA rows deleted, pin rows, cup rows, P15, P16; 23 cases + volumes; final run) | 0 | 43 s | `T069_data/path_p1.txt`, stderr empty `path_p1.err` |
| 2 | `python -I ../mechanism/out/T069_data/p15_detail.py` (share sensitivity foam E,G x0.5/1/2, bored/solid J, bounds independent of the share model) | 0 | ~2 min | `T069_data/p15_detail.txt` |
Two earlier runs of command 1 (exit 0, 42 s) and two failed edits (syntax error in my own print line, fixed) are not kept.

## Step 1 edits (landing_path_a.py)
- F-4: P12 now `rect_rf(..., M[:,1] (My), M[:,2] (Mz), SAD_W, a_chord)`; P12 minimum 0.28 -> **0.29**. F-5: P11 section from SAD_W (no numerical change today, P11 0.34).
- Peel rows relabelled "BOND INTEGRITY (coupon, outside RF minimum; T-069 F-3)" and excluded from the minimum (P3, P5, P7, P10, P13 peel); bearing rows remain RF rows. P1 PSA rows (peel and shear) deleted (D-215 F-2).
- New rows: PIN (1 x 3 mm CF cross-pin, R14: shear, double shear, couple arm = rib OD 14 mm; bearing in PETG wall 3 x 2.5 mm) at the root block and saddle; CUP (wall bending, EVA bearing at rim and pin hole, pin shear) for the PROPOSED cup 4 mm deep / 1.5 mm walls, free foam 30 mm. Pin shear allowable 30 MPa EST (structures_a.py TAU; 41.3 MPa Tap sheet only a sensitivity, landing_side_a.py l.66). **CF-tube hole bearing allowable at the 3 mm hole in the 1 mm RMRC wall: "—" (no source), so that row is not computed.** EVA allowable "—": the 0.17 MPa crush plateau (30 N / 180 mm2) is used as the bearing limit, EST. The cup-rim model (couple on a lever of one cup depth) is a crude upper-demand model: read the CUP rim and wall rows as "the cup as sketched does not carry the 30 mm lever", not as a design number.
- P15 (wing torsion) and P16 (wing in-plane bending), `wing_checks()` at y 0.38 (fin station), 0.228 (motor station), 0.060 (just outboard of the pack-tray slot end 0.057; sections inboard of 0.057 are weaker, "—" not computed).

## P15 / P16 model and sources
- Section: Selig S5010 from `common.COORDS` (WING_DZ shifted), chord 0.245 m (common.py), spar CF 12x10 at x 0.060 (SPAR_*), bore 12 mm; foam = XPS 25 kg/m3 (BOM R01). **Tape skin: product and thickness "—" (BUILD-GUIDE-A.md l.149): skin-less bound.**
- Foam: E 30 MPa, G 8 MPa (structures_a.py l.254, "Ec 30, Gc 8 MPa EST", for 30 kg/m3 XPS; 25 kg/m3 is softer; sensitivity x0.5 / x2). Compressive 103 kPa (Owens Corning FOAMULAR 150 data sheet, 15 psi min ASTM D1621, checked 2026-11-19 by web search; no modulus or shear row in the sheets found), tension 129 kPa and shear 86 kPa EST (foam_103.py). Spar G 3 GPa (fe_a.py l.11), E 70 GPa (iter2_margins.py l.13), 350 / 30 MPa EST.
- Torsion: foam J from a finite-difference Prandtl stress function (0.4 mm grid; 'bored' = 12 mm bore as a phi = 0 boundary, lower bound; 'solid' = no bore, upper bound); foam max shear = 99.5-percentile |grad phi| (staircase-boundary spike removed). Spar and foam share by GJ; KF 1.725 (spar), KP 2.156 (foam).
- In-plane bending: moment of one fin's feet about z at the station (outboard free body; hub, pack and motor masses are inboard of every station; wing-foam inertia ignored, EST), shares by EI about the composite neutral axis (x 0.0615 m), foam extreme fibre at the trailing edge (conservative: sharp TE tip).
- Reference line x0 = spar axis and mid-chord, worse of the two taken. Torque (about the span axis) is constant along y from the fin to the hub: 9.63 N m limit (hard 7/7 combo; same number as P14a), i.e. the wing, not just the spar, has to carry it.

## RF table (23 cases, min over cases; KF 1.725 / KP 2.156; criterion RF >= 1.0)
Full table with governing cases: `T069_data/path_p1.txt` (the "demand stress" column is only meaningful for the P-rows that had it before; for the new rows it is allowable / RF and is not a stress). Rows < 1.0 unless noted.
| Row | min RF | case |
|---|---|---|
| **P15 wing torsion (skin-less), y 0.38 / 0.228 / 0.060** | **0.15** (all three) | hard 7/7 combo |
| **P16 wing in-plane bending (skin-less), y 0.38** | **0.31** | hard 16 wide + drift |
| **P16, y 0.228** | **0.18** | hard 10 wide + drift |
| **P16, y 0.060** | **0.11** | hard 10 wide + drift |
| CUP EVA bearing at rim (crude model) / at pin hole / cup wall bending | 0.01 / 0.12 / 0.13 | hard 16 wide + drift |
| PIN bearing in PETG wall (root block, saddle) | 0.19 | SITL Tb_h5 wide |
| PIN CF 3 mm shear (root block, saddle) | 0.55 | SITL Tb_h5 wide |
| P12 saddle junction (after F-4) | 0.29 | hard 7/7 combo |
| P14a spar torsion under the saddle | 0.32 | hard 7/7 combo |
| P11 / P6 / P8 | 0.34 / 0.50 / 0.51 | unchanged |
| P10 bearing | 0.72 | |
| P9a / P9b rib | 0.86 / 0.86 | |
| P14b 1.45, P2 1.46, P7 bearing 2.62, P3 bearing 3.73, P4 3.91, P13 bearing 4.78, CUP pin shear 8.13, P5 bearing 10.87, P5 / P7 / P10 / P13 / P3 shear rows 1.09-10.7 | pass | |
Bond-integrity rows (outside the minimum): P10 0.07, P7 0.26, P3 0.37, P13 0.48, P5 1.09.

## Robustness of P15 / P16 < 1 (T069_data/p15_detail.txt)
- Foam E, G x0.5 / x1 / x2 and bored / solid J: P15 0.23 / 0.15 / 0.11 (bored), 0.23 / 0.16 / 0.12 (solid); P16 at y 0.060: 0.19 / 0.18 / 0.17. No variant reaches 1.0.
- **Bounds that do not use the share model** (limit loads, 23-case maxima at the worst case of four): spar alone carries 3.06 N m torsion and the foam alone 0.71 N m (EST, 86 kPa, KP) against a demand of **9.63 N m**; even adding the two capacities as if fully ductile gives RF **0.39**. Spar alone in-plane capacity 17.8 N m against demand 13.3 / 23.3 / 38.7 N m at y 0.38 / 0.228 / 0.060 (RF 1.34 / 0.76 / 0.46) even if the foam took nothing.
- Skin: with the skin "—", the torque the skin would have to carry at RF 1 is about 8.2 N m limit (elastic share), a shear flow of about 1,130 N/m on the 3.6e-3 m2 enclosed area (EST; no sourced skin allowable, so the number is a requirement on the skin, not a check).
- Not checked, "—": the skin; sections inboard of y 0.057 (pack-tray slot, bridge slot, hub); rib-groove and servo-pocket cuts at y 0.228 (not subtracted: so the real RFs are lower, not higher); out-of-plane wing bending and shear.

## STOP decision
**P15 = 0.15 and P16 = 0.11-0.31 are below 1.0. STOP after step 1, as D-215 s7 requires.** Steps 2 (clamshell / enlarged-block sizing, plate allowables lookup), 3 (tip sizing) and 4 (rerun at mu 0.30 with new geometry) were not started, because D-215 s6 states the package "may be redone around" a failed wing check and F-1 sends the fix to the board (s8 item 4). This is a valid outcome, not a failure of the task.
What the result says: the landing pitch torque from each fin (about 9.6 N m limit in the 1.2 m/s hard cases, 3-4.5 N m in SITL-envelope cases) and the in-plane moment (13-39 N m limit) cannot be carried by the 12x10 spar plus XPS core on the EST allowables; the wing is not just conservative on P14a. A wing-structure change (torsion skin over the outboard wing, larger spar, or a landing load path that bypasses the wing, e.g. a landing frame to the hub) is needed before saddle or block detail matters. That reopens mass (gate already -0.95 g flat rule), flutter (A-P13) and cost: board / Dillon, outside this task.
Caveats that could move the numbers (all EST): foam E, G and strengths (no 25 kg/m3 data), the foam extreme-fibre rule for P16, and the unquantified tape skin. A skin coupon (torsion and in-plane) and a wing torsion test would be the cheapest way to replace the EST, but the hard 9.63 N m versus 3.8 N m ductile-sum bound is 2.5x, larger than any of those uncertainties.
Also note for the conductor: P15 does not depend on y (torque is not relieved until the hub) so a mid-span reinforcement does not help unless it spans fin to hub.
