# T-071 Phase 1 step 1 (R-PHY-09, concept A): wing glass torsion skin option, RF table and STOP decision (2026-11-19)

Status: analysis only, NOT VERIFIED COMPLETE. Edited only `redesign/qp/A/structures/landing_path_a.py`; new files in `redesign/qp/A/mechanism/out/T071_data/`. No CAD, docs/, CHANGE-LOG, ledger, MASS-GATE, SITL or FEA. Nothing committed.
Categories: **rigid-body dynamics** (`landing_a.py` force histories, 23 cases, unchanged model, D2 pad arms) + **hand-calculation part checks** (thin-wall closed-cell torsion, composite-section beam bending, Prandtl stress function by finite difference for the foam, strut statics and Euler, sandwich wrinkling formula). No FEA, CFD, interference, kinematics or flight dynamics. Every allowable is EST unless a source is given.
Inputs: D-216 / T-070 (s3, s7 steps 1-2, bold stops), `T069_phase1.md`, `T069_data/p15_detail.py`, T-068 D2 (pad edge z >= 0.195, X_GROUND about 0.3415 per s4).

## Commands (cwd `redesign/qp/A/structures`, `python -I`)
| # | Command | Exit | Wall | Output |
|---|---|---|---|---|
| 1 | `python -I landing_path_a.py --skin` | 0 | 37 s | `T071_data/skin_run.txt`, stderr empty |
| 2 | `python -I ../mechanism/out/T071_data/t071_scans.py` (robustness matrix, fine strip scan, strut options) | 0 | 37 s | `T071_data/scans.txt` |
| 3 | `python -I landing_path_a.py` (skin option off; reproducibility) | 0 | 39 s | `T071_data/path_default_after.txt`: **identical** to `T069_data/path_p1.txt` after removing the `[n s]` timers (diff empty) |
One earlier `--skin` run failed in 3 s (my `set_pad(**dict)` call, fixed). Not kept.

## What was added (`landing_path_a.py`)
- `section_props(xmax=)`: foam section restricted to the cell ahead of the hinge (x <= 0.18375 m). Default unchanged.
- `wing_checks(..., skin=dict)` dispatches to `wing_checks_skin`: skin = glass laminate (`skin_laminate`: ply count, t, E, G, strengths), `K` (skin factor, default **KP 2.156**, never relaxed), `relief` (fin inertia, second column), `strip_A` (cove CF strip), `truss` (strut + spar truss). Rows: P15 spar torsion, foam shear (cell), skin shear, skin shear+axial interaction, wrinkling (torsion only; torsion + bending), P16 spar, foam, strip. Stations y 0.35, 0.285 (clamp node, outboard side, no truss credit), 0.228, 0.060, 0.040. In-plane moment taken about the neutral axis of the composite section.
- `strut_checks`: strut axial N = Fx_fin / ux (strut takes the chordwise shear inboard of the clamp; Vx = 0), Euler pinned-pinned without foam support, an upper bound with foam bedding (not credited), tube strength, bond at the clamp and at the hub socket.
- `set_pad`, `PAD_D2` (x_foot 0.3415, pad centre z 0.189 = edge 0.195 minus half of the 12 mm pad), `skin_variants`, `skin_main` (`--skin`).
- Geometry check (cell ahead of the hinge): enclosed A 3,389 mm2, perimeter 383 mm, cove face 8.6 mm; T-070 V5 gave 3,393 / 384 / 8.6. Agrees.

## Sources (looked up 2026-11-19)
- Laminate: ACP Composites, "Mechanical Properties of Carbon Fiber Composite Materials, Fiber / Epoxy resin (120 C cure)", PDS Dec 2014, https://acpcomposites.com/wp-content/uploads/2024/05/Mechanical-Properties-of-Carbon-Fiber-Composite-Materials.pdf (PDF text extracted and read 2026-11-19). **E-glass fabric, Vf 50 %, dry, room temperature, not a wet lay-up sheet**, with the supplier's no-warranty statement. Fibres +-45 to the load axis: E 12.3 GPa, in-plane shear modulus 11 GPa, X 90 MPa, in-plane shear strength 100 MPa. 0/90: E 25, G12 4 GPa, S 40 MPa. This **confirms T-070's 100 MPa fibre-dominated shear strength and its modulus order of magnitude** but for Vf 50 % at 120 C cure.
- Wet ply: 48 g/m2 cloth + 40 g/m2 resin (T-070 EST) gives Vf 0.352; all ACP values are scaled by 0.352/0.50 = 0.70 (EST linear scaling): G(+-45) 7.7 GPa, E_x 8.7 GPa, shear strength S 70 MPa, X 63 MPa, ply fibre E 17.6 GPa. t = 0.054 mm/ply (EST). No wet lay-up coupon exists.
- A university micromechanics page (NTNU TMM4175, read 2026-11-19) gives plain-weave E-glass/epoxy Vf 0.45 G12 2.6 GPa (estimates, not tests), consistent in order with ACP 4 GPa. Used only as a cross-check.
- Wrinkling sigma_cr = 0.5 (E_f E_c G_c)^(1/3): Hoff and Mautner's empirical coefficient (theory 0.91). Two web results (Cambridge Aeronautical Journal "Theory of wrinkling in sandwich construction"; MDPI Materials 14(17) 5043) describe it but neither printed the formula in one line, and one result reports test failures below the c = 0.5 prediction. **EST: needs a skin wrinkling coupon.** Foam E 30 / G 8 MPa (30 kg/m3 values; 25 kg/m3 is softer; sensitivity x0.5 run).
- Foam strengths, spar and strut allowables, KF/KP: as T-069 (`landing_path_a.py` l.18-28, 156-157). Cap strip E 120 GPa: EST (T-070), vendor data not looked up, "—".

## RF table: minimum over 23 cases and the five stations (`T071_data/skin_run.txt`)
D2 pad arms. Skin-less with the D2 pad (for reference, same model as T-069): **P15 0.14, P16 0.11** (T-069: 0.15 / 0.11): the pad move costs about 7 % on torque as T-070 F-6 said.

V0 GATE: 1 ply 48 g/m2 at +-45, cove strip 3 mm2, no inertia relief, truss credited, skin factor KP:
| Row | min RF | governing |
|---|---|---|
| **STRUT Euler pinned, no foam support (Pcr 367 N)** | **0.93** | hard 10 wide + drift (peak strut compression 227.6 N limit, x KF 1.725 = 392.7 N) |
| STRUT bond at clamp (D6 x 14.2 mm, epoxy 2.0 MPa EST; length from the wing.py clamp box face y 0.272) | 1.09 | same |
| P15 skin wrinkling, torsion + bending (E_f = E_x) | 1.15 | hard 7/7 combo, all stations |
| P15 foam shear, cell ahead of hinge | 1.28 | hard 7/7 combo |
| P15 skin shear / skin shear + axial | 1.30 / 1.30 | hard 7/7 combo |
| P15 skin wrinkling, torsion only (E_f fibre) | 1.50 | hard 7/7 combo |
| STRUT bond at hub socket (D6 x 30 mm) | 2.30 | |
| P16 foam bending + axial (worst y 0.285) | 4.64 | hard 10 wide + drift |
| P16 cove CF strip | 4.92 | |
| P15 spar torsion | 5.28 | |
| STRUT Euler bound if bedded in foam (4,330 N, **not credited**) / tube strength | 11.0 / 11.0 | |
| P16 spar bending + axial | 22.5 | |
MIN P15 **1.15**, MIN P16 wing rows **4.64**, strut truss rows **0.93 (Euler)**.

Variants (min P15 / min P16 wing rows):
| Variant | P15 | P16 | note |
|---|---|---|---|
| V1 fin inertia relief 20 % (second column, EST; I_fin 83 g / Iyy 0.0265 gives about 27 %, T-070 V7 says 20-25 %) | 1.42 | 4.64 | |
| V2 truss credit off | 1.08 | 2.08 | truss helps P16 by 2.2x inboard |
| V3 skin E, G x0.7 | **0.94** (foam shear) | 4.48 | softer skin sends torque to the foam |
| V4 foam E, G x0.5 | **0.70** (wrinkling) | 4.81 | 25 kg/m3 foam is softer than the 30 kg/m3 values |
| V5 no cap strip | 0.98 | **0.75** | strip is needed |
| V6 skin factor KF instead of KP | 1.28 | 4.64 | |
| V7 2 plies +-45 | 2.12 | 5.15 | |
| V8 1 ply 0/90 | 0.55 | 5.17 | fails, as T-070 |
Robustness matrix (`scans.txt`): 2 plies +-45 stays >= 1.21 on P15 in all four stiffness / foam corners (1.21 at skin x0.7 and foam x0.5); 1 ply is below 1.0 in three of four corners (0.65-0.94).
Cap strip: P16 passes from **0.20 mm2 (1.01) / 0.5 mm2 (1.40)**; 1 mm2 gives 2.04 (1.24 g); 3 mm2 gives 4.64 (3.7 g). Strip size is not the driver. P15 is unchanged by the strip (1.15-1.17).
T-070 hand calc comparison: skin shear RF 1.30 here (KP, S 70 MPa) against T-070 2.52 (KF, 100 MPa); wrinkling 1.15 against 1.93; foam 1.28 against 1.19. The differences are the factor (KP) and the Vf-scaled strength.

## Mass of the skin solution (EST)
| Item | g | basis |
|---|---|---|
| 1 ply glass skin, y -0.40..+0.40, perimeter 383 mm | 27.0 | 0.088 kg/m2 x 0.383 m x 0.80 m (T-070: 28.8) |
| centre / fin-node plates and bulkheads | about 5 | T-070 EST, not re-derived |
| cove CF strip 1-3 mm2 | 1.2-3.7 | 0.80 m x 1.55 g/cm3 |
| **1 ply total** | **about 33-36** | T-070 +37 |
| 2 plies instead (robust to the V3 / V4 corners) | skin 53.9, total about 60-62 | +27 g over 1 ply |
| Strut 6x4.0 instead of 6x4.5 (Euler RF 1.10 pinned) | +3.0 | availability and price "—" |
| Strut 7x5 (Euler RF 1.87) | +5.7 | hub and clamp sockets change; availability and price "—" |

## STOP decision
**P16 strut Euler without foam support is 0.93 < 1.0, so D-216 s7 step 1's stop rule applies: STOP after step 1; step 2 (bridge bending at 2T, CGE-006 node, hub bore) was NOT started.** The wing rows themselves pass at the gate (P15 1.15, P16 4.64 with the strip). Things that are not hidden by this:
1. The 6x4.5 strut (CGE-005) in compression at 227.6 N limit needs Pcr >= 393 N; it has 367 N pinned. The foam does not rescue it by right: the strut sits in a groove that is open below with 0.5 mm clearance per side (`wing.py` groove, "bonded slip fit clearance EST"), so no bedding credit. Pinned ends are conservative (hub socket 30 mm bonded, clamp socket 14 mm); a fixed-pinned factor (RF 1.91) is not credited without a source. **What is needed:** a stiffer strut, 6x4.0 (+3.0 g, RF 1.10) or 7x5 (+5.7 g, RF 1.87), or a bonded foam bed with a coupon. Note the clamp bond is 1.09 (EST bond allowable) at a 14.2 mm bonded length: close to 1.0 as well.
2. P15 at the gate passes by 1.15 (wrinkling, an EST formula with no coupon). With the skin 30 % softer or the foam 50 % softer it falls to 0.94 / 0.70. A robust skin is 2 plies (about +27 g more). The glass allowable is a dry Vf 50 % fabric sheet scaled by 0.70 EST, not a wet lay-up datum.
3. The pad move (T-068 D2) is included. Fin inertia relief is not credited in the gate column.
Neither the ply count nor the strip size fixes the Euler row. Not done and "—": sections inboard of y 0.040 (tray slot, hub), groove and pocket cuts (not subtracted from foam), centre node and bridge (step 2), skin peel, out-of-plane bending, flutter and A-P10 re-run with the skin GJ (step 5), strut end fixity, price of any tube size.

---
# Addendum (conductor decision): strut 6x4.0, then Phase 1 step 2

## A. Strut 6x4.0 rerun (command `python -I landing_path_a.py --strut40`, exit 0, 32 s; `T071_data/strut40.txt`)
Code change: `strut_checks(..., id_=)` (default unchanged); new `strut40_main`. Same 23 cases, D2 pad, KF 1.725 / KP 2.156.
| Row | 6x4.5 (T-071 step 1) | **6x4.0** | governing |
|---|---|---|---|
| STRUT Euler pinned, no foam support | 0.93 (Pcr 367 N) | **1.10 (Pcr 431 N)** | hard 10 wide + drift, 227.6 N limit |
| STRUT bond at clamp (D6 x 14.2 mm, 2.0 MPa EST) | 1.09 | 1.09 | same (bond area unchanged: OD unchanged) |
| STRUT bond at hub socket (30 mm) | 2.30 | 2.30 | |
| STRUT tube strength (350 MPa EST) | 11.0 | 14.0 | |
| Euler bound with foam bedding (not credited) | 11.0 | 14.0 | |
**Strut Euler is now >= 1.0 with no foam credit and no fixity credit.** Margin is only 10 %, the clamp bond is 9 %. Mass +3.0 g for two struts (CF 1.55 g/cm3 EST). Existence of the tube: a 6 mm OD x 4 mm ID x 1 m pultruded CF tube (1 mm wall) is listed by Easy Composites, https://easycomposites.co.uk/6mm-pultruded-carbon-fibre-tube, shown in a web search result 2026-11-19 (page itself not opened; one search result flags a wall-thickness discrepancy on a different, roll-wrapped listing, so confirm the wall before ordering). BOM R10 is the RMRC 6x4.5; RMRC 6x4.0 product, price and stock: "—" (not looked up). Pultruded UD tube E and crush behaviour in the socket: EST at the 70 GPa project value.

## B. Step 2 (new rows; `T071_data/step2.py`, exit 0, 31 s; `T071_data/step2.txt`). Categories: rigid-body dynamics (histories) + HAND CALCULATION; EST allowables.
Model: both wing torques arrive at the centre as bending of the 16x14 bridge (T-070 F-4). Limit-load pitch moment into the bridge: **2T bound = 2 x single-fin max = 20.5 N m** (single-fin max 10.24 N m with the D2 pad; T-069 had 9.63); the actual same-instant sum over the 23 cases is 13.1 N m (SITL Ta_h5 narrow). Both columns shown. Skin torque share 0.890 (V0). Hub-side inertia relief (EST 0.37 of Iyy, T-070 s3.1) is shown as a second column only.
| Row (hand calc) | 2T bound 20.5 N m | same-instant sum 13.1 N m |
|---|---|---|
| Bridge tube 16x14 bending (Z 166 mm3, sigma x KF vs 350 MPa EST) | **1.65** (212 MPa) | 2.59 |
| CGE-006 saddle socket bearing (PETG 20 MPa EST, socket 23.5 mm, 6M/(D L^2) x KP, conservative triangular bearing) | **0.67** | 1.05 |
| **Hub bridge bore bearing** (PETG 20 MPa EST, **bore depth 9.0 mm** = HUB_X1 -0.045 minus floor -0.054, `wing.py` l.18/81) | **0.10** (204 MPa x KP) | 0.15 |
| same, with hub-side inertia share 0.37 (EST, not credited) | 0.26 | 0.41 |
| bore depth needed for RF 1 (no relief) | 28.8 mm | 23.0 mm |
| Skin shear flow at the centre bulkhead: q = T_skin/(2A) = 9.12 N m / (2 x 3,389 mm2) | 1,345 N/m limit | |
| Bulkhead plate to skin bond, epoxy 2.0 MPa EST, bond width 0.5 / 1.5 / 3.0 mm | 0.34 / 1.03 / 2.07 | |
| Plate-to-saddle face bond in torsion (face 23.5 x 21 mm, rectangle torsion beta 0.246) | **0.26** | |
| CF cross-pin 3 mm, pair at 18 mm arm (layout assumed, not drawn), double shear, 30 MPa EST | **0.39** | |
| Pin bearing in the 0.5 mm lite-ply plate | "—" (no allowable; stress would be about 730 MPa) | |
Notes: plate thickness 0.5 mm is inferred from T-070's "2 x lite-ply about 2 g" with 0.6 g/cm3 EST (so a butt edge is 0.5 mm; a flange of >= 1.5 mm is needed for RF 1.0, 3 mm for 2.1). Plate shear strength: "—". The pin lever and the saddle face are my assumption: T-070 did not specify the node.

## C. Step 2 STOP decision
**STOP: the hub bridge bore is 0.10 (0.26 even with hub-side inertia relief), the CGE-006 socket 0.67, the plate-to-saddle bond 0.26 and the pin 0.39 are all below 1.0.** The bridge tube itself passes (1.65). Nothing past step 2 was started (no step 3 onwards). What this says: the 9 mm deep bridge bore in the hub cannot react the landing pitch torque as a bending couple; it needs about 29 mm (or 17 mm with the EST hub inertia share), or a different reaction path (for example a sleeve or flange spreading the couple over the tray / hub flange, or a longer bore through the hub block, which was cut back to 9 mm by D-207), and the centre node needs a larger bonded face or a drawn pin pattern with a larger arm. These are CAD changes and a design decision (conductor / Phase 2), plus the bearing allowable is EST (PETG 20 MPa, no coupon). The strut rows and the wing P15 / P16 skin rows from step 1 stand. Wing P15 at the gate remains 1.15, with the V3 / V4 sensitivity (0.94 / 0.70) from step 1 unresolved.
Limits: skin-off default rerun after the `strut_checks` edit (`python -I landing_path_a.py`, exit 0, about 39 s): output identical to T069_data/path_p1.txt. No FEA; hub bore bearing is a hand model (rigid bonded tube, triangular bearing), conservative against a real compliant bond, and the hub FEA runs d208 / d209 used flight loads only.
