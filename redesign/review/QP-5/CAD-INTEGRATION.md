# Concept A CAD integration (fidelity round, D-193 / D-194)

Date 2026-11-15. Owner: CAD integrator. Scope: `redesign/qp/A/cad/` after lanes A (wing, cage), B (propulsion) and C (electrical) finished. Labels: `V` vendor page or drawing read 2026-11-15, `PE0` APC file `vendor/apc/9x45MR-PERF.PE0`, `CALC` computed in the CAD, `EST` estimate (measure on arrival), `-` unknown. Nothing was committed or published.

## 1. Result

| Gate | Command | Result |
|---|---|---|
| Build | `python -I redesign/qp/A/cad/build_a.py` | PASS, 10 modules, 0 errors, 0 warnings (96 parts, 35 joints, 12 wires) |
| Collision, neutral and +-21 deg stop | `collide_a.py` | PASS: 0 part pairs deeper than 0.05 mm in all 3 poses; wire ends not on a termination 0; wire folds 0 (444 bodies, 96 parts) |
| Collision +-20 deg | `A_ELEV_POSE=20 collide_a.py` | PASS, same counts |
| Collision +-22 deg | `A_ELEV_POSE=22 collide_a.py` | 4 pairs, all the expected stop-boss contacts (balance tab x stop boss, 0.24 mm lower, 0.28 mm upper, R and L); nothing else |
| Assembly | `a_assembly.py` | 35 steps, 96 of 96 parts placed, 0 blocked, 0 unsupported, 0 wires laid before both ends are on |
| Stop check | `stop_check.py` | PASS: lead/tab to cap cavity 0.51 mm (upper) and 0.52 mm (lower) over -21..+21, boss to lead >= 1.35 mm |
| CAD mass | `sitl/cad_mass.py` | `cad_mass.json` written (section 4) |

Reports: `cad/out/REPORT.md`, `report.json`, `report_pose20/21/22.json`, `ASSEMBLY.md`, `STOP_CHECK.md`. One caveat: the collision poses move the horn, balance, damper and elevon only; the pushrod and servo arm stay at neutral ("linkage path not modelled"), so the linkage sweep is checked by the arm-angle table in 3.12, not by Blender.

The lanes left the tree failing (wire ends not seated, 43 static overlaps, lower cap into the elevon). Section 3 lists what I changed for each.

## 2. What each lane changed (as received)

| Lane | Files | Change |
|---|---|---|
| A | `wing.py`, `common.COORDS` | Section Selig S5010 from `subsystems/wing/s5010.dat` (unscaled, 9.82 % t/c); balance lead `BAL_DZ` -6.0 -> -3.3 mm; lens caps redrawn (15.9 g for four); hub CGE-001 now a printed frame (13.1 g, 25 mm arm sockets, 0.8 mm walls `EST`); motor cup holes on the 19 x 16 pattern; fin fairing real section; foam masses re-derived (core 100.1 g, elevons 6.7 g each); plate seat `ZP` 16.07 -> 18.88 mm |
| B | `propulsion.py` | Real APC 9x4.5MR / MRP blades lofted from the PE0 file (hub 0.65 x 0.34 in, adapter ring `EST`); motor per the T-Motor drawing (base 4 x M2.5 on 19 x 16, bell top 2 holes at 12 mm); new PRP-004 prop adapter (4.3 g each) and PRP-005 spinner nut (2.9 g each), `CALC` 6061; ESC real 35 x 35 x 5.5 board with pads |
| C | `electrical.py` | Pack 105 x 35 x 29 with 14 AWG leads, XT60 male and balance lead; strap PWR-002; avionics plate with windows, holes and nut pockets; Kakute stack with standoffs; RP3, M10Q, MS4525, pitot; HWC-001 / HWC-002 hardware; servo arm perpendicular to the rod, rod 52.5 mm hole to hole (the old arm pointed along the rod and gave about +-4 deg of elevon travel); horn, Z-bend rod, clevis; HRN-002 XT60 female and tail; wire bundles with real gauges |

## 3. Fit decisions and their basis

| # | Item (flag) | Decision | Basis |
|---|---|---|---|
| 1 | Spar foam 0.57 mm under the 12 mm bore at x 54-66 | **Airfoil datum lowered 5.0 mm** (`WING_DZ` in `common.py`, applied to `COORDS`, servo pocket heights `SV_Z0/SV_Z1`, harness route heights). Foam above / below the bore is now 6.27 / 5.62 mm (min 5.65 mm over x 54-66), was 11.3 / 0.6 mm. Cage, spar, saddles, hub and bridge tube stay at z 0, so no structure moved. Section shape and aero are unchanged (only z datum) | `CALC` from `s5010.dat`: chord line z 0 puts the lower skin at -6.6 mm at x 54-66; mid thickness there is +5.3 mm. Spar centred in the section. Pack tray, pack and hub stay on the cage datum, so the pack stands 5 mm higher above the skin than before (CG z in section 4) |
| 2 | 14x12 fin rib pokes through the skin aft of x 91 | **Faired, not shrunk.** After the datum change the rib is inside both skins to x 135 and rises out of the **upper** skin only (6.2 mm proud at the hinge x 183.75; nothing below). New part FIN-006-R/L, an XPS + tape blister 17 mm wide, top 1.5 mm over the tube, x 130 to the hinge, trimmed by the core and the rib (0.3 g each, `EST`) | The 14x12 x 0.2 m rib is the structural member (root bending MS 3.49, `review/QP-3/STRUCTURES.md` s6 line "Rib 14x12 root bending"; mass 14.8 g in `qp/A/structures/iter2_run.md`), so it is not made smaller. No tube fits the 9 mm section at the hinge |
| 3 | Tray lead notch for the pack leads and XT60 | End wall R cut from z 21.5 mm up to the wall top (open above so the pack drops in with its leads), x -10.6 to +15.6 mm (covers the leads at +-10 mm trim: lead x 2.5 +- 10 +- 8.1) | Lead exit z 22.5 mm = pack mid thickness (`electrical.PACK_ZL`); pack drop-in blocked at 1.21 mm until the notch was opened to the top (assembly step E4) |
| 4 | Strap overlaps the 12 mm bridge tube by 1.6 mm; strap vs +-10 mm trim | Strap loop kept: inner contour z -6..top, so it passes **under** the tube (tube bottom z -6, strap -7.6..-6) and no overlap exists in the model (0 collision). Core tray slot widened from y +-55.5 to **+-57.0 mm** so the strap (outer face 56.1 mm) clears the foam at every trim x (strap x reaches +7.5 mm at +10 trim, inside the core). Strap is a flexible part: assembly step E5 checks the fitted position only (travel 0); threading under the tube is by hand | `PWR-002` 25 mm x 1.6 mm `EST`; pack mass and trim `PACK_X`, `TRIM` |
| 5 | Tray-lip M3 bolts undesigned | **Bolts dropped.** The tray is one printed part bonded to the hub pad; the lips are integral and moved to the ends of the trim travel (front x -39.5..-37.5, rear +17.5..+19.5). The pack sits against a lip (trim -10 / +10) or on foam shims (not drawn, `EST`) and is held by the strap; the pack now has its own edge to the tray (anti-slip pad, `EST`). The 4 trim slots were removed | The lips were drawn as part of the tray, so slotted bolts had nothing to move (`review/QP-4/ASDRAWN.md` s5 item 5 "not drawn") |
| 6 | Motor cup holes 3.4 -> M2.5 clearance | 2.9 mm (ISO 273 medium series for M2.5) | T-Motor drawing 4-M2.5 on 19 x 16 mm (`propulsion.py` header, read 2026-11-15). New type `CT-A-M25-SHCS-MOTOR` |
| 7 | Servo pocket, arm-rod region, cove, horn blade top | Pocket x 124.5-165.5, y +-22.5 about the servo already holds the arm sweep (radius 14 mm, arm angle -18.3 / +13.3 deg, 3.12). Cove widened from stop + 4 to stop + 6 deg (`cove_x`): the S5010 core grazed the elevon nose by 0.08 mm at +21 deg. Horn base plate now sits on the highest skin point it covers (0.27 mm overlap before); horn blade starts 1.5 mm ahead of the hole (`EST`, was 4.5 mm); clevis sleeve shortened to 2 mm so the fork cheeks, not the sleeve, straddle the blade | Collision at neutral, +-20, +-21: 0 |
| 8 | Lower lens cap into the elevon (0.45 mm static, 0.51 mm at +21) | Cap shell cut **4.0 mm ahead of the hinge** (`cap_profile`): the ramp ran on to x 185 over the elevon nose, and the elevon's lower nose corner (9 mm below the hinge axis) swings 3.2 mm forward at +21 deg. Needed region ends at x 172 (lead/tab) and 176.4 (boss); clearances unchanged (stop check) | `stop_check.py`, collision |
| 9 | FC screws 22.9-23.3 mm are cut lengths | **Stock M2 x 25** for all four. Foam-tape pads 1.5 -> 3.0 mm (generic 3 mm double-sided foam tape, `EST`; mass kept at 1.0 g `EST`), which lifts the stack 1.5 mm; screw tip ends 0.1 mm short of to 0.6 mm past the nut bottom. The core carries four relief holes for the tips (HWC-001 and HWC-003 are core seat guests) | Stock lengths for M2 pan screws are 20 / 22 / 25 / 30 (retailer catalogues, not fetched: confirm on order) |
| 10 | Nuts could not be seated by the build sequence | HWC-001 split into screws (2.97 g) and **HWC-003 nuts** (0.41 g): nuts sit in the plate pockets when the plate goes on (E2), screws go down through the FC stack later (E3a) | Assembly check |
| 11 | Connection types | New `interfaces/connection_types.json` entries (additions only): `CT-HW-SEATED` (named in `collide.py` MOVE_VIA but missing), `CT-A-M25-SHCS-MOTOR`, `CT-A-PROP-ADAPTER`, `CT-A-PROP-NUT`. `CT-PROP-NUT` keeps its K09-L text (M6x1) and is no longer used by concept A | Library note: "a type used by one subsystem stays local"; these are shared additions, none edited |
| 12 | Linkage kinematics (new, not flagged) | Rod 52.5 mm hole to hole, horn R 12.9 mm, arm 12 mm: arm angle for elevon -21 / -20 / -10 / 0 / +10 / +20 / +21 deg = -18.3 / -17.3 / -8.1 / 0 / +7.0 / +12.8 / +13.3 deg (rod length error < 0.01 mm). Travel is asymmetric (about 0.87 deg per deg one way, 0.63 the other) | `CALC` from the CAD (horn hole at 9.24, 9.01 mm from the hinge axis). Clevis pin split out as MEC-005-R/L (0.03 g, carried inside the rod's 1.0 g before) so the clevis can straddle the blade (D4) and the pin follows along y (D5) |
| 13 | BOM / ORDER-LIST prop labels | `BOM-A.csv` P02, `ORDER-1.csv` O1-02, `bench/ORDER-LIST.csv` O2 restated: seen from the thrust side MR (standard) turns CCW and MRP (reverse) turns CW, as in `sitl/a_plant.py` lines 69-76 (UR, LL = MRP). The RMRC page (read 2026-11-15) says "Standard (CW)" and "Reverse (Pusher/CCW)", which is the view from behind the prop; the old "2 CW MR + 2 CCW MRP" was therefore not wrong in that view but contradicted the CAD and SITL. Check the blade marking before mounting | RMRC `86771`; the CAD follows the thrust-side view |
| 14 | Wires (new, found by the collision gate) | Strands now mitred at corners (the old per-vertex offsets crossed by 0.4-0.5 mm); every strand end gets a solder-joint / crimp block (`EST`, strand diameter + 0.6 mm) on its host part; ESC BAT pad moved to the aft-right corner (110, +12 mm; pad layout is `EST`); tail routed out at x 122 over the plate; ESC signal bundle (3 x 2, 6 x 26 AWG) straight along y 0 into the FC stack; servo leads out of the FC aft between the boards and outboard of the XT60 pair (y +-76, z 14.7 mm over the skin, taped bridge); heights follow the new datum | collision 0 wire ends, 0 folds, 0 overlaps |

## 4. Mass and CG

T-Motor MN2212 V2.0 page (`store.tmotor.com/goods-388-MN2212-V20.html`, read 2026-11-15): the spec table lists "Weight Excluding Cables" 55 g and "Weight Including Cables" 65 g (cable 400 mm). The packing list is "1x Motor" and "1x Hardware pack"; the page does not say what the hardware pack holds, so **the 65 g is the motor plus its cable only. It includes no prop adapter, no spinner and no screws.** (The page also names "MN4112" once in the packing list: a page defect.) Consequences:

- The 65 g already carries the motor phase leads, so the drawn phase wires (E-HRN-02..05) add no mass. Nothing to remove.
- The adapter (4.3 g) and spinner nut (2.9 g) are in no lump: `MASS-GATE.md` s2 has motors 260 g (4 x 65), props 44 g, hardware 40 g, and the hardware line is "M3 screws/nuts (motors 16, others), epoxy fillets, paint" (`structures/structures_run.md` line 24). They are therefore added in full: +28.8 g. If the T-Motor hardware pack turns out to contain the adapter (usual for T-Motor motors, not confirmed), the BOM has no buy line for it either way (BOM P01 prices the motor only): confirm on the first order.
- Lane C's removals from lumps are genuine: HRD-001 30.0 -> 26.08 g (FC screws and nuts 3.38 g, arm screws 0.54 g, taken from "screws and nuts"); HRN-001 55.5 -> 42.9 g (XT60 female and tail 8 g, strap 3 g, AVN-003 +1.6 g, taken from the 106 g wiring lump, itself 110 g less the ESC lead). The strap and XT60 being inside the 110 g avionics-wiring line is an `EST` judgement.
- The drawn motor and adapter screws (M2.5 x 8, M3 x 6) stay in HRD-001 (40 g line lists "motors 16"); nothing was removed for them.

| | Before (HEAD) | After | Change |
|---|---|---|---|
| Basic mass | 1,231.34 g | **1,259.14 g** | +27.80 g |
| CG x aft of LE | 24.39 mm | **21.47 mm** | -2.92 mm (band 20-26, target 20-24: in band) |
| CG y | 1.88 mm | 2.57 mm | +0.69 mm (limit 5 mm) |
| CG z | 6.77 mm | 6.06 mm | -0.71 mm |
| Ixx / Iyy / Izz (CAD axes) | 0.06319 / 0.02573 / 0.07006 kg m2 | 0.06550 / 0.02698 / 0.07219 kg m2 | +3.6 / +4.9 / +3.0 % |
| Elevon hinge inertia, total | 1.687e-5 kg m2 | 1.485e-5 kg m2 | -12 % |
| Elevon CG aft of hinge, balanced | -6.06 mm | -7.63 mm | |

Where the +27.8 g came from: added parts +44.3 g (prop adapters 17.2, spinner nuts 11.6, XT60 female and tail 8.0, strap 3.0, FC screws and nuts 3.38, arm screws 0.54, rib fairings 0.6; the clevis pins, 0.06 g, are taken out of the rods); lump and foam reductions -21.0 g (HRN-001 -12.6, HRD-001 -3.9, core -1.9, elevons -2.6); lens caps +2.8 g, RX +1.6 g, hub +0.1 g. The CG moved forward mainly because the prop adapters and spinner nuts (28.8 g) sit at x -121 mm; the datum change moved the wing 5 mm down against the cage axes, which is most of the CG z change.

Predicted mass with the MASS-GATE rule (basic x 1.1174 + 48 g) is **1,455 g** (`EST`): 15 g under the 1.47 kg gate (D-190) and **15 g over the 1.44 kg design target**. This needs a decision from A1 (cut or accept); I did not change any lump to hide it. `mission_gate_a.py` was not re-run.

## 5. Gate detail

- Static, +-20, +-21: no part pair above 0.05 mm. Fixed on the way: lower lens cap into the elevon (item 8), horn plate and clevis sleeve into the horn and elevon (7), pack into the tray (3), core into the elevon nose at +21 (7), 78 open wire ends and 43 overlaps (14).
- Assembly: D4 (rods) was blocked by the clevis pin crossing the blade (0.26-0.83 mm); pin split out and added as D5/D5b. New steps: C1a (rib fairings), D2a (arm screws), D5 / D5b (clevis pins), E3a (FC screws), E4a (XT60 female), E5 (strap, fitted position only).
- `a_assembly_plan.py` CAGE group now also carries PRP-004 and PRP-005 (built on the bench with the motors and props).

## 6. Remaining EST / unknown dimensions (measure on arrival)

| Group | Items |
|---|---|
| Motor, adapter, spinner | Drawing read from a 473 px render (+-0.3 mm); base ring thickness 3.5 and diameter 27.5; bell-top hole orientation; stud height 18.5 (the 13 and 24 mm dimensions are ambiguous); spinner ogive curve; adapter and nut masses (CALC 6061, 4.3 / 2.9 g); hardware pack contents; prop adapter screw thread and length |
| Props | Hub 0.65 x 0.34 in from retailer listings (ReadyMadeRC says 0.33); bore 1/4 in and adapter ring ID 5 / OD (not published); blade section shape (NACA thickness on a flat bottom; PE0 names the sections, gives no coordinates); MR / MRP direction by blade marking |
| ESC | PCB 1.6 mm, component envelope outline, pad layout and mound size, corner radius, BAT / SIG pad positions (moved here) |
| Pack, XT60 | Lead length (100 mm on two retailers, 35 / 60 on one), lead OD 3.0 mm, XT60 pin pitch 7.2 mm, housing length 12 mm, keying chamfer, pouch radius 3 mm, pack width 35 (EU retailers 33 x 28); strap thickness 1.6 mm and length; anti-slip pad and trim shims (not drawn) |
| Flight controller stack | Board spacing (standoff 16.8 mm assumes boards at the stack ends), PCB 1.6 mm, standoff OD 4 mm, pad positions, 3.0 mm tape thickness; stock M2 x 25 availability; RP3, M10Q (connector assumed JST-SH 6-pin), MS4525 sizes (15 x 15 EST) |
| Servo and linkage | Servo ears, output boss height, case size from servodatabase.com (not on the RMRC page); arm outline and 2 mm thickness; hole row; horn blade 15 x 2 mm, base plate 20 x 8 x 1 mm; clevis sleeve, cheeks and pin size; Z-bend geometry; rod length 52.5 mm |
| Wing and cage | Hub wall 0.8 mm and socket sizes; cap wall 0.6 mm; bonding flange 0.4 mm; tray end-wall thickness, lip heights, notch size; rib fairing 0.3 g, 17 mm width; solder-joint block size (not a real feature); core relief holes for the screw tips; the real wing foam density and the foam under the spar after the datum change |
| Wires | All routes and heights (taped bridges over the skin are not drawn); strand counts per cable; motor lead exit position on the cup |

## 7. Analyses whose inputs changed (not run here)

| Analysis | What changed | Where |
|---|---|---|
| Aero for the S5010 | Section is the real S5010 (was the reflex placeholder): lift slope, moment coefficient, stall, elevon effectiveness, wing drag; the datum shift changes no aero shape | `prop_a.py` / aero tables, SITL aero model |
| Flutter | Elevon hinge inertia 1.485e-5 kg m2 (was 1.687e-5), `BAL_DZ` -3.3 mm, lead 15.6 g at 20 mm, elevons 6.7 g, caps 3.8 g each, damper unchanged, new section | `structures/flutter_a.py`, `review/QP-4/FLUTTER.md` |
| Pushrod buckling and linkage loads | Rod 52.5 mm hole to hole (FIXES2 had 42.5); arm +13.3 / -18.3 deg for +-21 deg, asymmetric ratio; servo torque against the hinge moment with the real arm (12 mm) and horn (12.9 mm) | `review/QP-4/SERVO.md`, `structures/fixes2_*` |
| Hub socket wall | Hub is a printed frame with 0.8 mm walls and 25 mm sockets (`EST`) | `structures/fe_a.py`, cage modes (`iter3_*`) |
| Spar foam and shear | Foam around the 12 mm bore 5.6 / 6.3 mm; core volume changed (S5010, cove +6 deg); bond rule |y| <= 0.20 m | `structures/foam_103.py`, `fixes2_run.py` |
| Mass gate | Basic 1,259.1 g, predicted 1,455 g `EST` (target 1,440, gate 1,470); +28.8 g adapter and nut line has no source lump | `MASS-GATE.md`, `mission_gate_a.py`, `REQUIREMENTS-A.md` A-D3 |
| CG and static margin | CG x 21.47 mm, y 2.57 mm, z 6.06 mm; the wing sits 5 mm lower against the cage and thrust axes (z-offset of the aerodynamic centre from the thrust plane) | `MASS-GATE.md` s5, `sitl/a_plant.py` |
| SITL forward flight | Cant 17 deg (D-189) and the D-191 gains with the new mass, inertia, CG and elevon hinge inertia; `run_fwd.py` still bakes in cant 16 | `sitl/` |
| Landing / C5 | Mass and CG changed; feet unchanged | `structures/landing_a.py` |
| BOM and cost | No buy line for the T-Motor adapter / spinner unless the hardware pack has them; stock M2 x 25 screws; 3 mm foam tape; the two prop labels | `BOM-A.csv`, `bom_a.py` |

## 8. Files changed

`qp/A/cad/amodel/common.py`, `wing.py`, `propulsion.py`, `electrical.py`; `qp/A/cad/a_assembly_plan.py`; regenerated `qp/A/cad/model/*/interfaces.json`, `cad/out/*`, `qp/A/sitl/cad_mass.json`; `interfaces/connection_types.json` (4 entries added); `qp/A/BOM-A.csv`, `ORDER-1.csv`, `bench/ORDER-LIST.csv` (prop labels); `params/CHANGE-LOG.md` (D-193, D-194); this file. `WING_DZ` can be overridden with the environment variable `A_WING_DZ` (default 0.005) for a before / after comparison.
