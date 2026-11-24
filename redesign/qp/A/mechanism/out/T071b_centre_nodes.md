# T-071b (R-PHY-09, R-OPT-01, concept A): centre reaction of the landing pitch torque, then T-068 Phase 1 steps 2-4 around the glass skin (2026-11-19)

Status: analysis only ($0), NOT VERIFIED COMPLETE. Board option O4 "resize once" (AM-005) is the context. Nothing committed. No CAD, docs/, CHANGE-LOG, ledger, MASS-GATE, SITL, FEA, `arm_cup_checks.py`, `flutter*`, `mission_gate_a.py`, `fe_a.py` touched. `landing_path_a.py` is **unmodified** (`git status` clean for it), so its existing outputs stay reproducible; the new geometry is applied through its module constants from the new scripts.
Categories: **rigid-body dynamics** (landing_a.py foot-force histories, 23 cases, T-068 D2 pad; hub-side and wing-half wrenches from the same point-mass model the sim uses) + **hand calculation** (bearing, bond, plate, pin, wall) + **interference-class read-only box check** (stub build of `amodel`, part boxes) + static geometry (tip). No FEA, CFD, kinematics, flight dynamics. Every allowable is EST unless a source is given. KF 1.725 / KP 2.156 and RF >= 1.0 never relaxed.

New files: `redesign/qp/A/structures/landing_centre_a.py` (Part A), `landing_nodes_b.py` (Part B steps 2 and 4), `landing_tip_b.py` (Part B step 3); data in `T071b_data/` (`centre_run.txt`, `nodes_b.txt`, `tip_b.txt`, `demand_series.npz` 16 MB rigid-body histories, timers).

## Commands (cwd `redesign/qp/A/structures`, `python -I`)
| # | Command | Exit | Wall | Output |
|---|---|---|---|---|
| 1 | `python -I landing_centre_a.py --recompute` (23 sims, hub / R / L wrench split, sum-to-zero assert) then `python -I landing_centre_a.py` (cached series) | 0 / 0 | 29 s / 5 s | `T071b_data/centre_run.txt`, stderr empty |
| 2 | `python -I landing_tip_b.py` | 0 | 90 s | `T071b_data/tip_b.txt` |
| 3 | `python -I landing_nodes_b.py` | 0 | 35 s | `T071b_data/nodes_b.txt`, stderr empty |
Earlier dev runs: one failed on a heredoc/quoting error in my own script (not kept); the first `landing_nodes_b.py` run lacked the P14a and pin-option blocks (superseded by command 3).

## 0. Answers in one place
1. **The step-2 demand was a bound, not a load.** Step 2 put 2 x the single-fin foot torque (20.5 N m) through the bridge. The rigid-body wrench the centre really transmits to the hub side (motors, arms, hub, pack) is **6.05 N m at the bore mouth, 7.96 N m at the saddle forward end** (peak over 23 cases; 7/7 hard combo gives 5.41 / 7.70; worst is SITL Ta_h5 narrow). Each wing half hands **9.00 N m** (worst of spar line and mid-chord) to the centre, not 10.24. The three wrenches sum to zero at every time step (asserted), so this is not a bookkeeping shortcut. EST dynamic factor (flexible airframe, no transient FE run) shown as x1.5.
2. **Hub bridge bore needs L >= 15.7 mm (rigid-body), 19.3 mm (x1.5), 28.8 mm (2T bound)**; as drawn it is 9.0 mm (RF 0.33 / 0.22 / 0.10). The bore cannot be deepened by more than 1.5 mm: arm tube B (x -0.0625) and its sleeve sit 2.5 mm behind the floor. The length has to come from a **block aft extension** (nothing else lies there) or from moving tube B.
3. **Recommended (conductor decides): C6 = hub floor +1.5 mm, block aft extension 12 mm in a 24 x 24 flared collar (+5.3 g), saddle socket as drawn, and a re-built wing-end node (one-piece saddle with ears to y +-16.5, CF plate, clevis ears, 4 pins double shear; +13.9 g).** Total about **+19 g EST (solid PETG upper bound)**. RF at rigid-body demand: hub bearing 1.94, collar 2.51, saddle socket 1.69, bridge 4.24, node min 1.30; at x1.5: 1.29 / 1.67 / 1.13 / 2.83 / **0.87 (saddle body shear), 0.93 (ear bond)**. Against the 2T bound it fails (hub 0.61, saddle 0.67). Cheaper alternative C7 (extension 10 mm, 20 x 20, +2.1 g; total about +16 g) passes the rigid-body column only (min 1.30) and is 0.96 at x1.5.
4. **A CAD conflict decides the node geometry:** the saddle slot (|y| <= 0.0165) removes the bottom skin (41.6 mm of arc) and almost all foam, so the T-070 / step-2 plates "adjacent to the saddle" at y 0.0105 have no closed skin perimeter. The plate station must be y >= 0.0165, with the saddle ears reaching y = +-0.0165 (section 5).
5. **Part B stops (rows < 1.0 that no option in this task fixes):** the CUP rows of the proposed D3 shoe cup (0.01 / 0.14 / 0.15, pre-existing from T-069, crude EVA bearing model) and the four bond-integrity rows (coupon class). The PIN rows (0.23 bearing, 0.66 shear) are fixed on paper by 3 x 3 mm pins in a 4 mm wall (1.12 / 1.97) but that is a CAD change. Everything else on the foot path is >= 1.0 with the geometry and the print-orientation rule below. Details in section B.
6. **Corrections to T-071 step 2 (my reading):** pins were counted in double shear on one interface plane (single shear gives 0.20 against 0.39, N0b below); the "face bond" formula agrees with the rectangle polar-moment form within 1 % (0.392 vs 0.387 MPa per N m).

## A. Centre reaction

### A.1 Demand (limit load; `centre_run.txt` section 1)
Model: the sim's own point-mass body (`landing_a.ITEMS` scaled to 1.50 kg, translated so its CG is the CAD CG, Iyy 0.0260 against CAD 0.0265 kg m2). From the foot forces: a_cg = F / m, alpha = I^-1 M_cg (gyroscopic terms, gravity and rotor thrust neglected: small against 100-250 N impact forces, EST). Sub-bodies: **hub side** = motors (353 g), arms (64 g), hub (46 g), pack (270 g); **R / L half** = everything else split by the sign of y (y = 0 lumps 50 / 50) with that side's fin and feet. Wrench the centre exerts on each, moved to the point needed with M' = M + (P - P') x F.
| Quantity (max over 23 cases and time) | N m | note |
|---|---|---|
| hub-side M at the bore mouth (x -0.045) | 6.05 | SITL Ta_h5 narrow; with the pack counted wing-side 6.21 (+3 %) |
| hub-side M at the saddle forward end (x 0.030) | 7.96 | includes the shear lever, Fz 30.5 N |
| wing-half torque into the node, worse of spar line x 0.060 and mid-chord | 9.00 | step 2 used 10.24 |
| single-fin foot torque (step 2) | 10.24 | 2T bound 20.48 |
Hub-side moment is 0.30 of the 2T bound. Sensitivity not run: the sim's mass list is the T-067-era roll-up, not the CAD part table; the mass partition (pack on the hub side) is an assumption (no-pack run above); the dynamic factor 1.5 is EST.

### A.2 Options in ladder order (trade table; RF = min over 23 cases and all time steps; "RB" rigid-body, "x1.5" EST dynamic factor, "2T" step-2 bound)
Mass is solid PETG at 1.27 g/cm3 (infill / shell factor unknown, "—", so an upper bound) and CF 1.6 g/cm3.
| Option (rung) | Δmass g | Margin (hub bearing / collar interlayer / saddle bearing / node min; RB \| x1.5 \| 2T) | Works? | Reliability | Manufacture | Assembly | Aero | Constraints | Source |
|---|---|---|---|---|---|---|---|---|---|
| C1 Subtract demand: use the rigid-body wrench, hardware as drawn (1) | 0 | hub 0.33 \| 0.22 \| 0.10; saddle 1.69 \| 1.13 \| 0.67; node 0.30 \| 0.20 \| — | **no** (hub, node) | hub bore is the weak end | none | none | none | — | `centre_run.txt` s2-4 |
| C2 Modify geometry: bore floor 1.5 mm deeper only (2) | -0.4 | hub 0.45 \| 0.30 \| 0.13 | **no** | web over tube B 1.0 mm | one more mm of bore | — | none | tube B at x -0.0565 | s2 H1 |
| C3 Modify geometry: H2 = floor +1.5 and 10 mm block extension 20 x 20, node N1 = 5 mm glass-tape lap, one-piece saddle with ears to y +-16.5, 4 pins single shear, plate stays lite-ply (2) | +2.1 hub, +7.4 node = +9.5 | hub 1.63 \| 1.08 \| 0.51; collar 1.44 \| 0.96 \| 0.45; saddle 1.69; node ear bond **0.69** \| 0.46, plate shear "—" (no lite-ply allowable) | **no** (node) | lite-ply shear unknown | print + ply | notch tray plate | none | cell closure y >= 0.0165 | s2, s4 |
| C4 Same hub as C6 (H3) with node N1 (2) | +5.3 + 7.4 = +12.7 | as C3 but hub 1.94 \| 1.29 \| 0.61; collar 2.51 \| 1.67 \| 0.80 | **no** (node 0.69) | — | — | — | none | — | s2, s4 |
| C5 Rearrange: arm tube B 12.5 mm forward, bore floor to x -0.068, 6 mm extension, L 29 mm (3) | +5.0 EST | hub 3.29 \| 2.19 \| **1.02** (the only hub row that passes 2T) | **no**: CG forward trim end about 18.4 mm against 19.3 (CL-A-CG-TRIM-FWD, EST) | hub FEA (D-207 / d209) invalid | block 12.5 mm longer forward | hub redrawn | prop plane 6 mm forward | A-P4 / trim | s2 H4, s6 |
| **C6 Add material, RECOMMENDED if the rigid-body demand is accepted: H3 (floor +1.5, extension 12 mm in 24 x 24 flared collar) + N2 (CF plate 0.5 mm, ears on both faces of the plate, 4 pins double shear, one-piece saddle to y +-16.5) (4)** | **+5.3 hub, +13.9 node = about +19** | hub 1.94 \| 1.29 \| 0.61; collar 2.51 \| 1.67 \| 0.80; saddle 1.69 \| 1.13 \| 0.67; bridge 4.24 \| 2.83 \| 1.65; node: lap 3.92, plate 2.88, ear bond **1.39 \| 0.93**, pins 1.67 \| 1.11, saddle body shear **1.30 \| 0.87** | **yes at rigid-body demand (min 1.30)**; 0.87 at x1.5; no at 2T | bonded ears and pins act in parallel (additive bound 3.06 \| 2.04; min-of-rows is the conservative figure) | printed collar and one-piece saddle, CF plate cut | tray plate notch 24 x 12; saddle slot cut | none | y +-0.0165 plate station | s2-s4, s6 |
| C7 Cheaper variant of C6: H2 (10 mm, 20 x 20) + N2 (4) | +2.1 + 13.9 = +16 | hub 1.63 \| 1.08 \| 0.51; collar 1.44 \| 0.96; node as C6 | yes at RB (min 1.30); 0.87 at x1.5 | thinner collar | as C6 | as C6 | none | — | s2, s4 |
Not sized (named so they are not lost): a torque tube sleeve on the spar across the centre (spar alone at plates 0.057 would be 0.38), through-bolted CF plate bulkheads at the hub aft face (bolt couple 1.5 kN at 14 mm arm vs PETG pull-out, no allowable), a bridge larger than 16 mm (block is 20 mm wide: 23 mm needed).

### A.3 Hub-end rows (`centre_run.txt` s2)
Required bore length for RF 1.0: 15.7 / 19.3 / 28.8 mm (RB / x1.5 / 2T). Bearing = mean over D x L with triangular distribution, 6M/(D L^2) + V/(D L), x KP, PETG 20 MPa EST (step-2 model; it reproduces step 2: 0.10 / 0.67 / 1.65 at 2T). Cosine contact on a cylindrical bore would raise the peak by about 1.27: not included (consistent with step 2), so every bearing RF would be about 0.8 x the figure. Collar bending: pressure over the extension as a cantilever from the block face; 24 x 24 section minus the 16 mm bore, Z 2,036 mm3 (20 x 20: 1,012); interlayer 9.5 MPa used as the governing allowable because the print orientation of the hub is not fixed (in-layer 20 MPa: 5.28 | 3.52 for H3). The collar and block walls are 2 mm PETG around the bore, so this is a hand check of a thin printed wall carrying a concentrated couple: **FEA of the extended hub (fea_hub.py, flight plus landing loads) is needed before the CAD is changed** (fe_a.py is another agent's, not run).

### A.4 Wing-end node rows (`centre_run.txt` s4); T_skin = 0.890 x 9.00 = 8.01 N m per side (V0 skin shares skin 0.890, spar 0.056, foam 0.053; cell A 3,389 mm2)
| Row (RB \| x1.5) | N0 step 2 as drawn | N0b pins single shear | N1 | N2 |
|---|---|---|---|---|
| skin-to-plate bond (epoxy 2.0 MPa EST, q = T / 2A) | 0.39 \| 0.26 (lap 0.5 mm) | same | 3.92 \| 2.62 (lap 5 mm) | same |
| plate shear flow at the ear edge | "—" (no lite-ply allowable) | "—" | "—" | 2.88 \| 1.92 (CF 0.5 mm, S 90 MPa x 0.70) |
| plate-to-ear bond (rect polar moment, epoxy 2.0 MPa EST) | 0.30 \| 0.20 (23.5 x 21, 1 face) | same | 0.69 \| 0.46 (41.5 x 19, 1 face) | 1.39 \| 0.93 (2 faces) |
| CF pins 3 mm (30 MPa EST) | 0.44 \| 0.29 (2, double) | 0.22 \| 0.15 (2, single) | 0.83 \| 0.56 (4 at r 17, single) | 1.67 \| 1.11 (double) |
| printed saddle body shear, ear to bridge socket (2.5 mm walls, 20 / sqrt 3 in-layer EST) | not run | — | — | 1.30 \| 0.87 |
| saddle ring bond on spar, spar torque share | 12.4 | | | |
CF plate source: ACP Composites PDS Dec 2014 (`https://acpcomposites.com/wp-content/uploads/2024/05/Mechanical-Properties-of-Carbon-Fiber-Composite-Materials.pdf`, saved PDF text extracted 2026-11-19): Std CF fabric, Vf 50 %, dry, room temperature, 120 C cure, 0/90 axes: Xt 600 / Xc 570 MPa, S 90 MPa, E 70 GPa, G12 5 GPa, density 1.6 g/cm3; +-45 to the load axis: S 260 MPa. Reference datum with a no-warranty statement; x 0.70 EST for a bought cured sheet or wet lay-up; bearing in the plate "—". The ear-bond area is limited by the slot (x 0.0295..0.071, 41.5 mm) and the airfoil height at the fore end (z -10.8..9.4 at x 0.0295, so 19 mm). Plate and ear positions, the lap width and the pin layout are NOT drawn: assumptions.

### A.5 CAD cuts that interrupt the torsion cell (`centre_run.txt` s5; perimeter ahead of the hinge 383 mm)
| Cut (wing.py core cut) | Skin arc removed | Where it matters |
|---|---|---|
| tray slot, x -0.010..0.0225, |y| <= 0.057, open above z 5.5 | 8.3 mm (2.2 %) | notch only (airfoil z > 5.5 only for x > 0.0145); lining the slot floor with glass closes it |
| saddle slot, x 0.0295..0.071, |y| <= 0.0165, open below, up to z 0.0115 | 41.6 mm bottom plus nearly all foam | plates inside this slot have no closed perimeter: **plate station y >= 0.0165** |
| bridge slot, x 0..0.056, |y| <= 0.0085, open below | 57.0 mm bottom | inside the saddle slot |
| servo pocket, x 0.1245..0.1655, y 0.1775..0.2225, open to the upper skin | 41.3 mm top (10.8 %) | **inside the T-071 step-1 cell, not in its stations (0.228, 0.060); not analysed here** |

### A.6 Envelope check of the recommended hub end (`centre_run.txt` s6; read-only stub build of `amodel`, world part boxes)
Test box x -0.045..-0.033, y +-0.012, z -0.016..+0.008 (extension 12 mm, 24 x 24 with the top at the tray plate top z 8). Only CGE-004 (the bridge, in its bore) and CGE-008 (the tray: plate z 6..8 needs a 24 x 12 mm notch; the pack front lip at x -0.0355..-0.0335 stays above z 8) overlap. y clearance to the raceway notches beside the hub pad flange (|y| 13.6): 1.6 mm per side. CG shift H1 +0.02, H2 -0.10, H3 -0.25 mm (forward trim end about 20.1 - 0.25 = 19.8 mm against 19.3, EST, uses 1,273 g and CG 21.37 mm). The node ears are inside the saddle slot (41.5 mm x 19 mm, airfoil 20.2 mm at the fore end), the saddle box lengthens from y +-10.5 to +-16.5, which is the existing slot width (no new core cut in y); the +4.4 g solid is in the node mass. **Hub CG, hub FEA, wire routing at the extension and the pack-tray mass change are not re-solved.**

## B. T-068 Phase 1 steps 2-4 around the skin
Set-up: D2 pad (x_ground 0.3415, pad centre z 0.189, edge 0.195), face mu 0.30, 23 cases, plateau 30 N, skin V0 (1 ply 48 g/m2 +-45, strip 3 mm2, KP), strut 6x4.0, geometry through P.* constants: root block ring OD 25 (`RING_BL_RO`), socket 22 x 22 from x 0.235 (`BLK_X0`, `BLK_W`), saddle rib engagement 40 mm (`SAD_X1` 0.1105). `nodes_b.txt`.

### B.1 Step 3: tip sizing (`tip_b.txt`, CAD CG x 21.37, z 6.37 mm)
| Variant | static edge / pad centre (deg) | max upright lean (deg) at lateral 0.16 / 0.40 / 0.52 / 0.70 m/s, mu 0.40 \|\| mu 0.30 |
|---|---|---|
| CAD as drawn (edge z 0.183) | 29.19 / 28.36 | 22/14/10/8 \|\| 22/14/12/12 |
| **T-068 D2 (x 0.3415, edge 0.195)** | **30.51** / 29.70 | 24/16/12/8 \|\| 24/16/14/12 |
| D2 + 3 mm track (edge 0.198) | 30.90 / 30.11 | 24/16/12/10 \|\| 24/16/14/12 |
| D2 with CG z 0 (sensitivity) | 31.35 / 30.56 | 24/16/12/10 \|\| 24/16/14/14 |
D2 meets the 30.5 deg edge target by **0.01 deg**: no margin, on an unmeasured CG z and the CAD 1,273 g CG; the post-T-067 CG (predicted 1,625 g) is not available ("—"). The pad-centre value 29.70 is below 30. +3 mm track gives 30.90 / 30.11 (about +1 g per foot EST, not computed). Dynamic gain from D2 is +2 deg at low lateral speed and +4 deg at 0.70 m/s with the 0.30 face. Recommendation for the conductor: D2 plus 3 mm if the box fit allows (box proxy 0.40 m against 0.39 m bare, T-068 s4; not re-checked).

### B.2 Step 2: root block and saddle
| Row (min over 23 cases, mu 0.30) | as drawn | T-071b geometry, interlayer 9.5 MPa | T-071b, in-layer 20 MPa rule |
|---|---|---|---|
| P6 root-block ring-to-socket junction | 0.48 | 0.75 | **1.58** |
| P8 root-block socket wall | 0.49 | 0.82 | **1.72** |
| P7 rib bearing / shear (D14 x 51) | 2.52 / 2.10 | 6.67 / 3.45 | same |
| P7 bond integrity (coupon class) | 0.25 | 0.67 | 0.67 |
| P5 ring bond shear / integrity | 11.5 / 1.03 | same | same |
| P2 shoe plate-ring junction | 0.96 | 0.96 | **2.03** |
| P10 saddle socket bearing / shear (engagement 40 mm) | 0.83 / 1.35 | 3.55 / 2.71 | same |
| P10 bond integrity | 0.08 | 0.36 | 0.36 |
| P11 / P12 printed saddle walls | 0.39 / 0.31 | 0.43 / 0.31 | 0.90 / 0.66: **replaced by the clamshell plates** |
| P13 saddle ring on spar, shear / integrity | 1.29 / 0.55 | same | same |
| P9a / P9b rib tube | 1.03 | 1.03 | 1.03 |
| P14a spar under the saddle | 0.31 skin-less bound | — | **1.53** with the skin torsion share (0.056 on the spar), bending in full |
The enlarged block passes **only with the in-layer print rule** (z-up, hub junction bending in the layer plane; P6 0.75 and P8 0.82 otherwise). Mass of the enlarged blocks +55 to +60 g pair solid (T-068 s6, not recomputed).
Clamshell first-order rows (plates 50 x 75 mm, CF fabric 0.7 x ACP, a_z 16.5 mm; EST areas): plate x / y stress **15.9 / 16.2** (t 1.0 mm), **23.8 / 24.3** (t 1.5); plate-to-cradle bond **2.70** (frame fraction 0.5 EST, epoxy 2.0 MPa EST; peel 151, integrity class); **CF pins 2 x 3 mm double shear 1.32**; **pin bearing in a 2 mm PETG cradle wall 0.37**. Plate thickness is not governing. Cradle wall bending and bearing in the plate: "—". T-068 s6 says stop if a row < 1.0: **the cradle pin bearing (0.37) fails; the paper fix is a 4 mm boss with 3 pins (1.12 bearing, 1.97 shear)**, a CAD change.

### B.3 Step 4: foot-path rows with the skin and the new geometry (`nodes_b.txt`)
Minimum per row family. P15 wrinkling 1.23, foam shear 1.34, skin shear 1.37, P15 spar 5.54, P16 foam 5.31, strip 5.63, spar 24.6; strut Euler 1.08 (6x4.0 pinned, no foam credit), strut clamp bond 1.07, hub socket bond 2.27, tube 13.8. Pin options (torque Mx shared by n pins, couple arm = rib OD): 1 x 3 mm 0.66 shear / 0.23 bearing (2.5 mm wall); 2 x 3: 1.32 / 0.47; 2 x 3 in a 4 mm wall: 1.32 / 0.74; **3 x 3 in a 4 mm wall 1.97 / 1.12**; 4 x 3: 2.63 / 1.49.
**Rows still below 1.0, no option fixes them here (STOP and report):**
| Row | min RF | Why it stays |
|---|---|---|
| CUP EVA bearing at rim (15 x 2 mm) | 0.01 | carried from T-069 (0.01). The crude model bears the cup-rim side reaction R = Fs (L + D) / D (8.5 Fs for L 30, D 4 mm) on EVA at the 0.17 MPa crush plateau: the allowable force on the rim is about 2.4 N, so no cup depth that fits fixes it. The model, not the geometry, is in question; EVA bearing / shear data are "—" |
| CUP EVA bearing at pin hole / CUP wall bending | 0.14 / 0.15 | same model; no EVA allowable, no coupon |
| bond-integrity rows (outside the RF minimum, T-069 F-3): P3 0.26, P7 0.67, P10 0.36, P13 0.55 (P5 1.03) | 0.26 | coupon class: no peel allowable exists; covered by the node coupons |
| PIN root block / saddle bearing and shear (1 pin as drawn) | 0.23 / 0.66 | fixed on paper by 3 pins in a 4 mm wall; CAD not changed |
Tight passes to watch (>= 1.0 but < 1.1): strut clamp bond 1.07, strut Euler 1.08, P9a / P9b 1.03, P5 integrity 1.03.

## Limits and what is "—"
Rigid-body demand uses the sim's roll-up masses (not the CAD part table) and a pack-on-hub partition; the dynamic factor 1.5 is EST and no transient FE exists: the recommended node is 0.87 / 0.93 at that factor. The bearing models are mean-stress hand models of a thin printed wall (no FEA); allowables PETG 20 MPa bearing / in-layer, 9.5 interlayer, epoxy 2.0 MPa, CF pin 30 MPa are EST (no coupons). Not done: hub FEA of the extension, cradle wall bending, plate bearing, post-T-067 CG for the tip, EVA data, skin peel, cell effect of the servo pocket, flutter and A-P10 with the new masses, `mission_gate_a.py` roll-up, any CAD. Proposed CHANGE-LOG entry (for the conductor): "D-2xx T-071b: centre reaction demand re-derived by rigid-body wrench (hub M 6.05 N m, not 20.5); hub block aft extension 12 mm, 24 x 24 collar; node plates at y +-0.0165; clamshell and block rows per T071b_centre_nodes.md".
