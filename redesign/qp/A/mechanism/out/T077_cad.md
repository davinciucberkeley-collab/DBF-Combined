# T-077 concept A O4b CAD (partial: pack, tray, strut, cover, mass basis), 2026-11-20

Status: **PARTIAL. Not VERIFIED COMPLETE. Nothing committed.** Edited: `cad/amodel/common.py`, `wing.py`, `electrical.py`, new `cad/amodel/printed_mass.json`; gate runs regenerated tracked outputs (interfaces.json, cad/out/*, sitl/cad_mass.json, params-A.json, proofs/out/*, drawings/out/*). No docs/, CHANGE-LOG, ledger, MASS-GATE edit. Data and scripts: `T077_data/`.

## 0. Acceptance test (restated from the brief)
1. FIRST: RDQ 2,800 mAh pack (107 x 33 x 46 mm, 270 g) fit against bay / tray / cover and the 0.90 x 0.50 x 0.39 m box; STOP and report options if it needs other systems moved.
2. Then CAD for the decided O4b parts with vendor/real shapes, enclosed wiring (exposed lengths listed), no interpenetration, masses from volume x T-067 basis, drawings regenerated, gates once at the end (build, collide pose 21, linkage poses, assembly, wire_inventory, cad_mass, mission_gate, T-067 audit, proofs/run_all).
Categories: interference (fit check, collide, assembly), geometry arithmetic (mass), illustrative (CG shift), kinematics (linkage poses, unchanged).

## 1. Step 1: pack fit check (`T077_data/fit_check.py`, output `fit_check_out.txt`): FITS, no other system moved; no STOP
Orientation: 107 mm along y, 33 mm along x, 46 mm up (z). Pack cell 46 x 33 x 107 occupies x -26.5..6.5 mm (centre -10, as before), z 9..55 mm.
- Tray: pack half length 53.5 mm vs end wall inner face 54.0 mm (0.5 mm gap). Walls moved outward 1.5 mm each (tray plate 109 -> 112 mm wide, core slot 114 -> 117 mm). Nothing else is in that y range at x -45..22.5.
- Trim travel kept: at -6 / 0 / +10 mm the cell x ranges are -32.5..0.5 / -26.5..6.5 / -16.5..16.5; bbox overlaps with every other part (excluding tray, strap, pad, wires, core): none. Cover AVN-008 starts x 22.5: 6.0 mm clear at full aft trim.
- Upper arm tubes at the pack end (|y| 53.5): axis z 36.6, x -81.5..-56.5; pack x min -32.5: 24 mm clear in x.
- Box proxy: whole-aircraft CAD bbox 479.4 x 900.0 x 461.3 mm before and after (the pack sets no extreme: x min PRP-005-LL, z extremes PRP-002). **Pre-existing finding (not caused by T-077): sorted extent 0.900 / 0.479 / 0.461 m against the 0.90 / 0.50 / 0.39 proxy: the third dimension is 0.461, over by 71 mm, because the props (z +-230.7 mm) are included.** `params-A.json` `box.packed_m` says 0.39 "props on"; the CAD does not agree. Needs the packed configuration decided (props off or rotated).
- Rejected orientation B (46 mm along x, 33 up): x span -39..23 mm at full trim, pack top z 42 mm against the cover roof outer z 8.9 mm at x 23: collides with the cover at aft trim, would remove the +10 mm trim travel (CG authority) or force the cover and FC/ESC aft. Not taken.
- Strap: drawn loop inner perimeter 354 mm (327 mm with the Tattu). **BOM W08 is a 300 mm strap: too short, already too short for the old loop.** Longer strap needed (about 384 mm with buckle overlap EST); price "-". Mass in the CAD scaled 5.5 g x 384/300 = 7.0 g (EST).
- Leads: vendor XT60 lead 80 mm (RDQ page, 2026-11-19). Drawn route E-HRN-13 is 117.5 mm per strand (was 107.5). **Extension of about 37.5 mm 14 AWG (solder splice + heat-shrink, on the exposed run) or a re-soldered XT60 is needed; not drawn.** Pack tiny shifts: power leads exit x 1.5 mm (was 2.5) so the 3.0 mm strand clears the balance lead (gate caught a 0.56 mm overlap with 2.5).
- Not analysed (no sims until final): aero effect of a 55 mm tall nose pack (was 38 mm), CG height (+8.5 mm of cell centroid).

## 2. What was implemented (file:line)
| Item | Change | Where |
|---|---|---|
| RDQ pack | PACK_L/W/H 107 x 33 x 46 mm (V racedayquads.com, read 2026-11-19), PACK_X (-26.5, 6.5), LEAD_LEN 80 mm, PACK_XL 1.5 mm, part name, mass 270 g | `common.py:48`, `electrical.py:534,539,545,711`, `wing.py:31` |
| Tray y walls | TRAY_YI/YO 54.0/56.0, wall top z 29.5 (leads at z 32 clear by 1.0 mm), core slot +-58.5 | `common.py:51-52`, `wing.py:732` |
| R1'' tray CGE-008 | one source of solids and windows (`_tray_solids`, `tray_volume_m3`, `tray_stats`): 1.2 mm plate on a 2.0 mm root pad (x -45..-35), centre rib tangent to the bridge tube, 3 x 4 plate windows per side drawn as 52.6 % of the 112 x 66.5 mm plate (R1'' calc used 50 % with 1.2 mm ribs; here ribs 2.0 mm, EST, T-073 hand calc NOT re-run), 2.0 mm end walls with 3 windows each, two 40 x 2.0 tabs per lip, solid band over the raceway footprint | `wing.py:512-565`, builder `wing.py:918+` |
| Strut 6x4.0 | STRUT_ID 4.0 mm; mass from length x section x 1600 kg/m3 | `wing.py:83,622` |
| Bay cover | COV_T 0.5 mm (vacuum-formed sheet, D-221) | `electrical.py:263` |
| Strap | loop follows the pack height; mass scaled to the needed length | `electrical.py:712-714,911` |
| Mass basis | `printed_mass.json` read by `P()` (T-067 s7 option A): printed parts = CAD volume x T-067 shell + infill basis; CGE-008 and AVN-008 re-run on the new shapes (`t077_mass_audit.py`, h 0.25 mm), the rest = T-067 adopted values | `common.py:176-188`, `T077_data/t077_write_printed_mass.py` |

## 3. NOT done (needs the next implementer; each is a CAD module change that ripples into edges, build steps, assembly plan, drawings)
- D-220 machined 6061 hub (the hub is still the printed PETG D-202 body, 15.82 g); D-222 sleeve L 32, staggered/tapered doubler, sleeve-mouth chamfer (touches the hub mesh `hub_body.py`, pins, doublers, cups); D-215 non-gated items; T-070 s7 Phase 2 CGE-006 node (Onyx + CF), CGE-007 tubular + R4 fillets r >= 1.5 and 3 x 3 mm pins in 4 mm walls, FIN-003/FIN-005 clamshell, glass skin shell part (1 ply +-45) and cove CF strip; R2 (AVN-001 removed, FC/ESC on bosses) and the Kakute H743-Wing part; R3fix cups.
- Why stopped: each is a multi-file change to coupled geometry (wire holes, edges, assembly steps, FEA constants); doing them half-way would leave the 3-D gates failing. The pack and tray were done first by the stop rule, gated, and are in a passing interference state.
- Kakute H743-Wing vendor data read (docs.holybro.com `kakute-h743-wing/overview.md`, 2026-11-20): dimensions 45 x 30 x 13.5 mm, mounting 25 x 25 mm M2, weight 28 g with USB extender. Hole diameter, PCB thickness, connector and header heights, stack/standoff height: "-" (not on the page; holybro.com store pages returned HTTP 429/404). It is a single 45 x 30 board against the 30 x 25 two-board F405 stack in the CAD, so the FC footprint, cover roof (45 mm now) and wire pads all change: not drawn.
- Test-gated, left as drawn: pad foam / stroke change (December drop test), anything that waits on TP-4 / TP-5 coupons.
- Not run: `collision/collide.py --glb` (not found as an A gate; `collide_a.py` is the A equivalent, as for D-212/T-022b).

## 4. Gate results (all after the final edit; driver `T077_data/run_gates.sh`, summary `gates_summary.txt`)
| Gate | Command | Exit | Time | Result |
|---|---|---|---|---|
| build / check | `python -I build_a.py` | **1** | 13 s | **FAIL: `graph:cg` CG x 29.7 mm outside 0.004..0.029 m.** All 10 modules ok, 0 warnings. A real consequence of s5, not a model error |
| collide pose 21 | `A_ELEV_POSE=21 python -I collide_a.py` | 0 | 151 s | PASS, 496 bodies, 115 parts, 0 pairs > 0.05 mm static / -21 / +21 (`REPORT_pose21.md`) |
| linkage poses | `collide_a.py --linkage-poses` | 0 | 253 s | PASS, 18 poses, 0 hits |
| assembly | `a_assembly.py` | 0 | 1749 s | 66 steps, 115/115 placed, blocked or unsupported 0, wires before end parts none (`ASSEMBLY.md`) |
| wire inventory | `wire_inventory.py` | 0 | 9 s | exposed 0.478 strand-m (was 0.448) |
| cad_mass | `sitl/cad_mass.py` | 0 | 6 s | 1.40283 kg, CG x 29.72 mm |
| mission_gate | `mission_gate_a.py` | 0 | 0 s | **stale**: hard-codes the Tattu 2300 (34 Wh) and CAD_BASIC 1,273.3 g / CG 21.37 mm (lines 59, 74); it does not read the CAD, so its output is unchanged and does not test T-077 |
| T-067 audit | `t077_mass_audit.py 0.5` (all 42 printed parts) and `0.25 AVN-008 CGE-008` | 0 | minutes | tray 14.07 g (h 0.25; 13.94 at 0.5), cover 8.82 g; `t077_rows_*.json` |
| proofs | `proofs/run_all.py` | 1 (strict) | 3 s | **fails 20 (stdout count, duplicates included) against the known 5 FAILS + A-P13 unverified.** New fails: CL-A-MASS-PRED / MASS-GATE-ROOM 1.615 kg vs 1.47, CUTS-REQUIRED 171 g, CG-HI 29.72 vs 26 mm, CG-TRIM-AFT 31.65 vs 28.5, SM 4.48 % vs 5 %, WINDOW-PRED 0.60 % vs 5, WINDOW-MASS, CRUISE-AVAIL 202.3 vs 204.6 s |
| drawings | `make_drawings_a.py` | 0 | 170 s | 41/41 composed, 42 STLs |

## 5. Mass roll-up and the CG finding (decision needed, not mine)
CAD basic mass 1,287 g (HEAD build) -> **1,402.8 g**. Parts: printed parts to the T-067 basis +125.6 g (fin root blocks +31.4, saddles +26.8, cups +20.8, shoes +12.6, tray +10.3, avionics plate +9.9, clamps +10.2, node +7.7, hub -2.2, cover -1.6), strut 6x4.0 +about 3 g, strap +1.5 g, pack 0. CG x 21.2 -> **29.7 mm** (+8.5 mm; `cg_shift.py`). Three-fifths of it is the two fin root blocks (x 283 mm) and the four foot shoes (x 298 mm) whose drawn solids were already far above their listed 3.2 / 1.4 g (T-067). Consequences (claims above): SM 4.5 % chord below the 5 % limit, CG over the A-P4 26 mm top by 3.7 mm, over the 28.5 mm aft trim limit; the pack cannot fix it (270 g x 36 mm needed, the hub face is at -45 mm). Options for the board: forward ballast / forward-mounted FC and ESC, lighter aft parts (X7 Onyx blocks, -4 to -8 g pair per T-080), or re-derive the CG window. The predicted 1,639 g (T-074) is not reproduced by the CAD yet: hub Al, skin, node, bosses, H743 and growth are not drawn.

## 6. Exposed wire table (CLAUDE.md rule; `wire_inventory.json`, strand-metres, sharp-corner lengths)
| Edge | Wire | Exposed length | Reason it cannot be enclosed |
|---|---|---|---|
| E-HRN-13 | pack power leads, 2 strands 14 AWG | 117.5 mm each (was 107.5) | pack is outside the 53 mm wide cover; leads run from the end face over the wall and along the skin to the XT60 at x 85. Vendor lead 80 mm: about 37.5 mm extension |
| E-HRN-14 | balance lead 5 x 26 AWG | 63.5 mm (was 54) | end face to the JST plug on the pack top (pack is 46 mm taller) |
| E-HRN-12 | battery tail | 42.5 mm | unchanged |
| E-HRN-07/08/11/10 | servo / I2C groove ends | 12 / 12 / 0 / 3 mm | unchanged |
Total exposed 0.478 strand-m (was 0.448): +30 mm. Min bend radius of E-HRN-13 4.0 mm (rule >= 4), E-HRN-14 1.5 mm (as before, 1.2 mm class lead).

## 7. Proposed CHANGE-LOG text (for the conductor)
D-223 (T-077 partial, 2026-11-20): RDQ 2,800 mAh pack (107 x 33 x 46 mm, 270 g) fits standing 107 y x 33 x 46 z in the existing bay with the tray walls moved out 1.5 mm; no other system moved; trim travel -6/+10 mm kept; orientation with the 46 mm side along x rejected (cover and trim). Tray redrawn as R1'' (windows 52.6 %, ribs 2.0 mm EST, hand calc not re-run); strut 6x4.0; bay cover 0.5 mm vacuum-formed; masses of printed parts now from CAD volume x T-067 basis via `printed_mass.json`. Gates: collide pose 21, 18 linkage poses and the 66-step assembly pass; build check and proofs fail on CG / mass (CG 29.7 mm, 1,403 g basic) because the drawn fin blocks and shoes were under-listed. Open: strap 384 mm, pack lead extension 37.5 mm, packed box z 0.461 vs 0.39 m, mission_gate_a.py stale, hub Al / skin / node / R2 / R3fix / R4 / H743 not drawn.

## 8. Limits
Tray strength not re-checked on the drawn windows (T-073 numbers were 50 % / 1.2 mm ribs); orientation and print-basis values are EST (T-067); 6061, Onyx, glass values not used (those parts not drawn); lead exit height at mid thickness is EST (RDQ page does not give it); strap and lead extensions have no price ("-").

---
# Part 2 (2026-11-20, after conductor commit 77f3a8dd). PARTIAL again. Not VERIFIED COMPLETE. Nothing committed.

## P2.0 What was and was not done
Done: (a) ladder rung 1 for the CG: pack moved 10 mm forward (centre -20 mm, the QP-4 position) in the bay/tray; (b) `mission_gate_a.py --o4b` switch; (c) strap and lead-extension BOM text (proposed below); (d) all gates re-run.
**NOT drawn (unchanged from part 1 s3):** Al hub (D-220) and sleeves L 32, D-222 arm-tube exit (staggered tapered doubler, sleeve-mouth chamfer, conduits), glass skin shell, X7 centre node, waterjet CF saddle clamshell, R2 bosses (avionics plate AVN-001 still drawn), R3fix cups, R4 clamps, Kakute H743-Wing part.
Reasons, stated plainly: (1) the hub body is an OpenCASCADE mesh (`hub_body.py`, cached `hub_body_cache.npz`); **pythonocc / cadquery are not installed here (`No module named 'OCC'`)**, so a hub with sleeve L 32 or octagonal sleeves cannot be regenerated, and an Al hub from primitives would also change pins, doublers, cups, conduits, `fea_hub.py` constants and the lead-exit holes together; (2) R2 and the H743 move the FC / ESC pad coordinates that every wire (E-HRN-02..11) and the cover (roof 45 mm over a 30 x 25 board, now 45 x 30) depend on; (3) skin, node, clamshell need new parts with edges, assembly steps and drawings. Doing them half-way would break the 3-D gates, so I stopped before editing instead of leaving a failing tree. Each is a separate implementer task; suggested order: install OCC (or write the hub from prisms), then hub + D-222 together, then R2 + H743, then skin / node / clamshell.
Kakute H743-Wing part name to use when drawn (CAD rule): "Flight controller Holybro Kakute H743-Wing, 45 x 30 x 13.5 mm (V docs.holybro.com, 2026-11-20), M2 25 x 25 mm, 28 g with USB extender; hole diameter -, PCB thickness -, connector and header heights -".

## P2.1 CG and SM (CAD as drawn now, A-P4 band 19.3..26.0 mm, SM limit 5 %)
| State | Basic g | CG x mm | SM % chord | Verdict |
|---|---|---|---|---|
| part 1 (pack centre -10) | 1,402.8 | 29.72 | 4.48 | fail CG band and SM |
| **part 2 rung 1 (pack centre -20)** | 1,402.8 | **27.70** | **5.31** | SM passes; **CG-HI 27.7 vs 26 fails (-6.5 %)**; CL-A-CG-TRIM-AFT 29.62 vs 28.5 fails |
(`sitl/cad_mass.json`, `mission_gate_a.py --o4b`; NP 40.7 mm from the script.) `build_a.py` check now PASSES (CG inside its 4..29 mm band).
Rung 1 is exhausted: the front lip is at x -44.5..-42.5 on the root pad, the hub face is at x -45 (no further room); the +10 / -6 mm trim travel is unchanged, so the aft trim end is +10 mm of pack = +1.9 mm CG.
**Rung 2 (avionics / ESC forward), estimate only, not drawn:** the plate may start at about x 31 (pack aft edge at +10 trim is now 6.5 mm; cover starts 22.5). FC + ESC + GPS + RX + plate + cover are about 100 g; moving them 10-20 mm forward is 1,000-2,000 g mm = -0.7 to -1.4 mm of CG.
**Undrawn items, EST (g mm about the 27.7 mm CG, 1,403 g):** Al hub +11 g at x -65 = -1,040 (-0.7 mm); R2 (plate 17.9 g -> bosses about 3 g at x 92) = -960 (-0.7 mm); R3fix cups -11.2 g at x -73 = +1,130 (+0.8 mm); glass skin plus cove strip about 30 g at x 70 = +1,270 (+0.9 mm); H743 vs F405 +11 g at x 60 = +360 (+0.3 mm); net about +0.6 mm. All EST: skin mass is 48 g/m2 x about 0.32 m2 x 2 (resin) from the wing area, not from drawn volume.
**Projection:** 27.7 + 0.6 - (0.7..1.4 rung 2) = 26.9..27.6 mm. **Rearranging cannot close it to 26.0 mm.** The residual 0.9-1.6 mm is 1,300-2,300 g mm. Ladder rung 3 (geometry), numbers: each fin root block FIN-003 is 18.9 g at x 283 mm (lever 255 mm): -4 g per block = -2,040 g mm = -1.5 mm CG (T-080's X7 Onyx variant gives -4 to -8 g for the pair: -0.7 to -1.4 mm); each foot shoe 4.55 g at x 298 (lever 270): -1 g on all four = -1,080 g mm = -0.8 mm; the saddles FIN-005 14.4 g each at x 67 are forward of the CG and do not help. No ballast, A-P4 band unchanged, as instructed. I stop here per the rule and report the options; the choice (X7 fin blocks and a lighter shoe, or a pack-length / hub geometry change) is the conductor's.

## P2.2 Gates (re-run after the last edit; `gates_summary.txt`; part-1 outputs kept in `part1_gates/`)
| Gate | Exit | Time | Result |
|---|---|---|---|
| build_a.py | **0** | 14 s | check PASS, 10 modules, 0 warnings, 1,403 g, CG 27.7 mm |
| collide_a (A_ELEV_POSE=21) | 0 | 153 s | PASS, 0 pairs > 0.05 mm static / -21 / +21 |
| collide_a --linkage-poses | 0 | 254 s | PASS, 18 poses |
| a_assembly.py | 0 | 1745 s | 66 steps, 115/115 placed, 0 blocked or unsupported |
| wire_inventory | 0 | 9 s | exposed 0.504 strand-m (HEAD 0.448); E-HRN-13 131 mm per strand, E-HRN-14 63.5 mm |
| cad_mass | 0 | 6 s | 1.40283 kg, CG 27.70 mm |
| mission_gate_a.py (default) | 0 | 1 s | output unchanged from before |
| mission_gate_a.py --o4b | 0 | 1 s | RDQ 2800 (41.4 Wh, 784 mAh left at BATT_LOW); CAD basic 1,402.8 g, CG 27.70 mm, SM 5.31 %. Its mass roll-up table (the 1.466 kg rows) is still the old item list, so the energy rows use that mass, not 1.40 / 1.64 kg: not edited |
| proofs/run_all.py | 1 (strict) | 1 s | fails 19 (was 20). Known: 5 FAILS + A-P13 unverified. New or still failing from the mass adoption: MASS-PRED and MASS-GATE-ROOM 1.615 vs 1.47 kg, CUTS-REQUIRED 171 g, CG-HI 27.7 vs 26, CG-TRIM-AFT 29.62 vs 28.5, WINDOW-PRED, WINDOW-MASS, CRUISE-AVAIL 202.3 vs 204.6 s. CL-A-SM now passes |
Collision of the redrawn conduits: not applicable (conduits not redrawn).

## P2.3 Strap and lead extension as real items (proposed BOM text; BOM-A.csv NOT edited)
Exposed run now 131 mm per strand (pack 10 mm further forward) against the 80 mm vendor lead: extension 51 mm of 14 AWG per strand, or move the XT60 pair 51 mm forward (then the battery tail E-HRN-12 grows by the same and is exposed on the skin: rejected, more exposed wire).
- W01 (change): "RDQ Series 14.8 V 4S 2800 mAh 100C XT60, 107 x 33 x 46 mm, 270 g +-1 %, XT60 lead 80 mm, JST-XH balance 35 mm; Race Day Quads $54.99, in stock, ground shipping only; page read 2026-11-19 (T079 addendum)". Qty and spares as the board set them.
- W08 (change): "Pack strap 20 mm webbing, buckle, length >= 385 mm (drawn loop 354 mm inner + 30 mm overlap, EST; the STRIX 20 x 300 mm listing is 85 mm too short). Source and price: - (not looked up; suggestion: any 20 mm battery strap sold in 400 mm or longer)". CAD mass 7.0 g (EST, 5.5 g x 385/300).
- New W10 (add): "Pack lead extension: 2 x 55 mm 14 AWG silicone (red + black; from W05 stock, 0.11 m), 2 solder splices with 3 mm heat-shrink (W05 kit), 0 extra purchase; about 1 g". Not drawn as a part (the CAD draws the full 131 mm run as the wires E-HRN-13); splice location on the exposed run, 3 mm.

---
# Part 3 (2026-11-20, T-077-p3). PARTIAL. Not VERIFIED COMPLETE. Nothing committed. No docs/, CHANGE-LOG, ledger, MASS-GATE or BOM edit (text proposed below).

Acceptance test (restated from the brief): (1) machined 6061 hub per D-220 / D-221 (octagonal sleeves, L 32 per D-222, mass = drawn volume x 2.70 g/cm3) and the D-222 arm-tube exit (staggered tapered doubler, sleeve-mouth chamfer, conduits collision-checked); (2) glass skin shell (1 ply +-45, real thickness) and cove CF strip; (3) X7 centre node and waterjet CF saddle clamshell; (4) R2 FC / ESC bosses, Kakute H743-Wing; (5) R3fix cups, R4 clamps (fillets r >= 1.5); then the CG test against A-P4 19.3-26.0 mm and SM >= 5 %, rungs 2-3 only with a strength check; gates once at the end with no failing 3-D gate. Categories of every number below: interference (collide, assembly), geometry arithmetic (masses, CG moments), illustrative (CG sensitivities marked EST). No simulation, FEA, CFD or flight dynamics was run (no sims until final).
Data and gate outputs: `T077_data/p3_gate_*.txt`, `p3_gates_summary.txt`, driver `T077_data/run_gates_p3.sh`; probe scripts for the hub fillet limit are described in P3.2.

## P3.1 Outcome per item
| Item | Status | Where |
|---|---|---|
| (1) Al hub, octagonal sleeves L 32, D-220 collar and 30 mm bore | **DONE, gated** | `wing.py` (constants SLV_*, COL_*, HUB_FIL*, hub_vol_m3, dbl_profile), `hub_body.py` (v3), `hub_body_cache.npz` regenerated with gmsh 4.15.2 OCC (5 s) |
| (1) D-222 P1 staggered tapered doubler, sleeve-mouth chamfer; P2 L 32 | **DONE, gated** | `wing.py` DBL_STAG / DBL_TAPER / MOUTH_CH, `build_cage` |
| (1) conduits redrawn | Conduits HRN-004 are generated from seat cuts against the new hub and doubler; no geometry change was needed, the collision gate is clean with them | `electrical.py` cd_mass_g mask updated to the octagon |
| (2) glass skin shell WNG-011, cove CF strip WNG-012 | **DONE, gated** | `wing.py` (SKIN_*, skin_loops, strip_loop), assembly step A1 |
| (3) X7 node CGE-006, CF saddle clamshell FIN-005 | **NOT drawn** (P3.4) | |
| (4) R2 bosses, H743 part | **NOT drawn** (P3.4) | |
| (5) R3fix cups, R4 clamps | **NOT drawn** (P3.4) | |
| CG test | **FAILS and cannot be closed by rungs 2-3**; stop and numbers in P3.5 | |

## P3.2 Hub CGE-001 as drawn (D-220 / D-221 s7.1 / D-222)
- Material 6061-T6 (machined), density 2.70 g/cm3 (T-080 s1, https://en.wikipedia.org/wiki/6061_aluminium_alloy read 2026-11-20; secondary source, the conductor must replace it with a mill cert or MMPDS value before H-A1). `printed_mass.json` no longer lists CGE-001. **Mass = drawn volume 22.78 cm3 x 2.70 = 61.5 g** (was 15.82 g printed PETG, +45.7 g). Volume = core by voxel (pitch 0.25 mm: block + collar + two sleeves minus bores, pins, lead exits) + OCC junction-radius material 18.0 mm3 + strut sockets, webs and tray flange (analytic) - chamfers (analytic).
- Shape: centre block 38.5 x 20 x 20 mm on the bridge axis (front face moved 0.5 mm forward, x -14.5, so sleeve A's front flat is flush with it), 3 mm radii on the four x-parallel edges; **two octagonal sleeves, 16 mm across flats (apothem 8.0 mm = 14 mm doubler OD + 2 x 1.0 mm wall at the flats; circumradius 8.66 mm), flats facing +-x and +-t (T-080 s7.1.1), over s +-32 mm (D-222 P2, was +-24, round R 8.5)**; the bore is the 12 mm tube for |s| < 11 and the 14 mm doubler OD for 11..32 (seat cut by the doubler); **0.5 mm x 45 deg internal chamfer at each sleeve mouth (D-222 P1; size EST, D-222 gives none)** and 0.5 mm x 45 deg chamfers on the four 4.8 mm lead exits (T-080 s7.1.5).
- **D-220 collar drawn: 24 x 24 mm (y +-12, z -16..+8, top flush with the tray plate top z 8, 3 mm edge radii), mouth at x -24 (hub axis +45 mm), so the bridge bore is 30 mm long (floor at +15)**: T-071b C6 test box and D-220 "mouth about x 45". The tray plate and root pad are notched by a seat cut against the hub (T-071b: "24 x 12 mm notch"; tray mass not re-audited, the notch removes under 1 g, so CGE-008 14.07 g is conservative).
- Junction radii: T-080 s7.1.2 asks R >= the end-mill radius (R 3.0 for a 6 mm cutter, EST). The OpenCASCADE fillet of the octagonal prisms **fails at 1.5, 2.0 and 3.0 mm** (probe: gmsh `occ.fillet` "Could not compute fillet" at sleeve A; sleeve B accepts 3.0 mm alone, sleeve A only up to 0.9 mm, 1.0 mm / 0.9 mm works as a pair). Drawn **1.0 mm (sleeve B) / 0.9 mm (sleeve A)**: needs a 2 mm end mill; cutter list "-". The 3.0 mm radius is NOT met: a machinist may add it, the CAD does not show it (mass effect about +0.1 g).
- NOT drawn (sizes unspecified, "-"): lightening pockets (T-080: 24-30 g EST "lightened"; the drawn solid is the knee-mill / upper-mass-end shape, T-080 s3.1), 2.5 mm floor web (the floor is at +15 with the 45 deg cone as before), cross-pin holes through the collar and bridge (3 mm, drilled with the tubes bonded), glass-scrim barrier, anodise. **Grommets at the lead exits not drawn: the 3 x 1.8 mm strand bundle (3.88 mm envelope) leaves 0.46 mm per side in the 4.8 mm hole, no room for a grommet wall; size and material "-".**
- Doubler CGE-009 (D-222 P1): s 11..47 mm (15 mm past the sleeve end), outer 5 mm tapered to a 0.2 mm tip wall (EST ply drop-off), 2.01 g each = revolved volume 1,259 mm3 x 1.6 g/cm3 (was 1.46 g); +2.2 g for four (audit EST +3.8 g for a straight 15 mm stagger).
- Pack and strap interaction (decision needed, P3.6): the collar mouth at x -24 lies across the strap path (strap passes under the bridge at z -10 inside the collar's z -16..8, |y| <= 12), so **the strap moved aft to x -23.5..-3.5 and the pack went back to centre -10 mm (part-2 rung 1 reverted)**: the pack leads and balance plug sit in the pack's aft 10 mm (x -8.5 / -3.5 at centre -20), exactly under that strap. Gate evidence: with the pack at -20 and the strap at -23.5 the first collide run had E-HRN-13 / E-HRN-14 / JST plug vs strap overlaps of 1.29 / 0.27 / 1.60 mm.

## P3.3 Glass skin WNG-011 and cove strip WNG-012 as drawn
- WNG-011: 1 ply 48 g/m2 cloth + 40 g/m2 resin = 88 g/m2 (T-071_wing_skin.md l.24, l.67; T-070 s3), wet ply 0.054 mm (EST, no wet lay-up coupon), density 1.63 g/cm3 (= 88 g/m2 / 0.054 mm). Closed shell over the leading edge and the cove face on the core outline, y -0.40..+0.40 (T-070). **Drawn inside the core outline** (core machined by a seat cut), so every part that sits on the surface still sits on it. Openings are the core's own cuts: all explicit core cuts (including the wire slits, pitot and I2C slots, pockets, tray slot) and the core's guest seats are replicated on the skin. **Mass 26.7 g from the shell volume** (T-071: 27.0 g, T-070: 28.8 g). Packing-tape skin and hinge tape stay inside WNG-001's lumped 100.1 g (T-070 did not credit them).
- WNG-012: cove CF strip, section **6 x 0.5 mm = 3 mm2 is my split: T-071 l.32 / l.69 give only the 3 mm2 area**, width, thickness and product "-" (in the part name). Under the skin on the cove face, centred, y -0.40..+0.40, interrupted by the same openings; 1.55 g/cm3 (T-071 l.69): **3.7 g** (full length; the openings are not subtracted: about 0.2 g conservative).
- Assembly: laid in step A1 with the core (no sweep). Edges E-WNG-90 / 91 / 92 (epoxy).
- Cost: the collision gate went from 152 s to 675 s (thin shell with ~40 copied cutters); the linkage and assembly gates are slower in proportion.

## P3.4 Not drawn, and why (each is a specification or decision gap, not effort; nothing half-built is in the tree)
- **(3) CGE-006 X7 node (T-071b N2: one-piece saddle with ears to y +-16.5, 0.5 mm CF plate, clevis ears, 4 x 3 mm pins in double shear).** The repo gives areas and EST allowables only (ear bond 41.5 x 19 mm, plate 0.5 mm): no ear outline, plate outline, pin coordinates or fibre layout. T-080 s3.2 itself says "expected yes; must be shown" (six-component rows, D-1 transient T-076c and coupons C-2 / C-3 pending). Drawing it would mean inventing about 15 dimensions; a material swap alone (Onyx 1.2 / 1.27 = x 0.945, -0.5 g) would be a false picture of N2. The current CGE-006 (9.67 g printed saddle) is unchanged.
- **(3) FIN-005 clamshell (T-068 D4, D-221: 0.5 mm waterjet CF plates, about 50 x 75 mm at z +-7.5..9 inside the core, slim 2 mm cradle, rib engagement >= 40 mm, CF pins).** Three conflicts: the drawn socket is 24 mm long and the rib starts at the saddle front (40 mm engagement needs a longer rib or another socket); T-071b B.2 shows the cradle pin bearing at 0.37 (fix on paper: 4 mm boss, 3 pins) and the plate outlines are "about"; the core plate pockets and the spar ring (r 10.5) against plates at z +-9 are not reconciled. Needs a drawn-to-dimension spec. Current FIN-005 (14.4 g each in `printed_mass.json`) unchanged.
- **(4) R2 / Kakute H743-Wing.** Removing AVN-001 moves the FC and ESC pad coordinates that E-HRN-02..11 and the cover (roof 45 mm) depend on, and the H743 is one 45 x 30 board against the drawn 30 x 25 two-board stack; GPS, RX and the cover seat need their own pads (T-073: +1..3 g). Part name ready: "Flight controller Holybro Kakute H743-Wing, 45 x 30 x 13.5 mm (V docs.holybro.com kakute-h743-wing, read 2026-11-20), M2 25 x 25 mm, 28 g with USB extender; hole diameter -, PCB thickness -, connector and header heights -".
- **(5) R3fix cups.** T-073 gives "5 mm plate over the +y 13 mm, 3 mm web 55 % of the area elsewhere (EST), tab widths my assumption, sleeve wall 3.5 -> 2.5 mm except at the screw-head pockets": which regions are windowed is not defined. **R4 clamps (socket OD 9 x 25 mm tube along the strut axis, ring wall 2.5, junction strips 2 x 2.5 x 9 mm EST, fillets r >= 1.5):** the CAD kernel's tube / revolve bodies are axis-aligned and the strut is 66 deg to x, so it needs an OCC mesh body like the hub (the hub_body route now works); not started.
- Lightening of FIN-003 (rung 3): blocked, see P3.5.

## P3.5 CG and static margin (illustrative, geometry arithmetic; `sitl/cad_mass.json`, `mission_gate_a.py --o4b`; A-P4 band 19.3..26.0 mm, SM >= 5 %)
| State | Basic g | CG x mm | SM % | Verdict |
|---|---|---|---|---|
| part 2 (pack -20, no hub / skin) | 1,402.8 | 27.70 | 5.31 | CG-HI fails |
| **part 3 as drawn (pack -10: the collar forces the strap and the pack aft)** | **1,483.3** | **28.30** | **5.06** | SM passes by 0.15 mm (limit CG 28.45); **A-P4 CG-HI fails by 2.3 mm; CL-A-CG-TRIM-AFT 30.12 vs 28.5 fails** |

Moment budget part 2 -> part 3 (g mm about x 0): hub 61.5 g at x -58.4 replaces 15.8 g: -2,548; four doublers +2.2 g: -165; skin 26.7 g at x 91.9: +2,454; strip 3.7 g at x 181.2: +670; pack back 10 mm: +2,700; net +3,111 (+3,119 from the CAD totals). The solid Al hub gains 1.7 mm of forward CG, the skin and the strip take back 2.1, and the collar costs the 1.8 mm of the pack's rung 1.

- Rung 1 (pack forward 10 mm, centre -20; `mission_gate_a --o4b` shows CG 26.5 mm, SM 5.8 %) is not available as drawn: it needs the two power leads and the balance plug moved to the front 12 mm of the pack (x -33..-29, ahead of the strap) with a longer exposed run over the nose (not drawn, not routed). Even then **26.5 > 26.0**.
- Rung 2 (avionics forward): the group (plate 17.9 + FC 17.0 + RX 4.6 + GPS 13.5 + pads 1.0 + ESC 20.0 + cover 8.8 + screws 3.4 = 86.2 g) can move at most 5.5 mm (cover front x 22.5 against the pack aft edge 16.5 at +10 trim, 0.5 mm margin): 86.2 x 5.5 / 1,483 = **-0.32 mm** (EST, not drawn).
- Rung 3 (lighten the fin root blocks / shoes): **no strength margin to give.** FIN-003 as drawn (PETG, 18.9 g) already has P6 0.50 / P8 0.51 against the landing demand (T-080 s3.4, "As drawn, PETG: no"); the decided T-068 enlarged block (+12.2 g pair, P6 1.58 / P8 1.72 in-layer) is not drawn yet. An X7 CF-reinforced slimmer block (+4 to +8 g EST, bond to Onyx "-", coupons C-1 to C-3) is "not shown" in T-080, and no D-223 landing-path run (`landing_path_a.py` / `landing_nodes_b.py`) exists for it, so I lightened nothing. The shoes (+7 g, T-068 D3) are decided aft growth, not savings.
- **What the decided-but-undrawn items add** (EST, dg x (x - 28.3) / M): R2 -0.65 (plate out, bosses back +3 g at x 92), R3fix +0.78 (-11.2 g at x -73.6), R4 -0.08, X7 node about +0.2, H743 +0.24, **enlarged root blocks +2.08 (+12.2 g at x 283), shoe cups and pads +1.27 (+7 g at x 298)**. Sum about +3.8 mm: CG about **32 mm (EST), SM about 3.5 %** if every decided item is drawn at its estimate.
- **The A-P4 band cannot be met by rungs 1-3 with the band unchanged and no ballast.** Stop; numbers above for the board. Options (conductor's call): move the wing about 6 mm aft relative to the hub (re-run the hub / bridge geometry), a longer nose for the pack (the collar sets x -24), re-derive the band, or give up the enlarged root blocks and the shoe cup growth (needs a strength path).

## P3.6 Decisions and open items for the conductor
1. Collar vs strap / pack (above): choose between pack aft (as drawn, CG 28.3), pack forward with the leads moved to the front (CG 26.5), or a shorter collar (D-220 asks for 30 mm of bond; a 21 mm collar cannot give it).
2. The hub is drawn solid: pockets "-" (T-080 expected 24-30 g lightened; solid 61.5 g). 10 g of pockets moves the CG aft by about 0.59 mm (10 x (28.3 + 58.4) / 1,473). Decide the pocket mass only after the CG is closed.
3. Junction radii 1.0 / 0.9 mm (2 mm cutter) instead of R3.0; confirm the cutter or accept a mesh body built another way.
4. Hub FEA H-A1 / H-A2 and the D-222 re-judgement (P1 doubler, P2 L 32) were NOT run here (no FEA in this task): the drawn octagon wall (1.0 mm at the flats, 0.5 mm at the chamfered mouth edge) and the collar section are inputs for them. The wall at the chamfered mouth is below the T-080 1.0 mm rule (the 0.5 mm chamfer is EST).
5. Tray strength with the collar notch and the windows is not re-checked (T-073 numbers: 50 % windows, 1.2 mm ribs).
6. The mass-dependent gates (proofs below) fail on mass and CG; see P3.7.

## P3.7 Gates (final tree, driver `T077_data/run_gates_p3.sh`; drawings composed separately)
| Gate | Command | Exit | Time | Result |
|---|---|---|---|---|
| build / check | `python -I build_a.py` | 0 | 15 s | PASS, 10 modules, 0 warnings, 1,483 g declared |
| collide pose 21 | `A_ELEV_POSE=21 python -I collide_a.py` | 0 | 675 s | **PASS**, 498 bodies, 117 parts, 0 pairs > 0.05 mm static / -21 / +21 |
| linkage poses | `python -I collide_a.py --linkage-poses` | 0 | 788 s | **PASS**, 18 poses, 0 hits |
| assembly (Blender) | `python -I a_assembly.py` | 0 | 1,852 s | **PASS**: 66 steps, 117 / 117 parts placed, blocked or unsupported 0, wires before end parts none |
| wire inventory | `python -I wire_inventory.py` | 0 | 9 s | exposed **0.478 strand-m** (part 2: 0.504; part 1: 0.478): E-HRN-13 117 mm per strand, E-HRN-14 64 mm, E-HRN-12 43 mm, servo / I2C groove ends 12 / 12 / 0 / 3 mm; no new exposure from the hub or the skin |
| cad_mass | `sitl/cad_mass.py` | 0 | 7 s | 1.48331 kg, CG x 28.30 mm |
| mission gate | `mission_gate_a.py --o4b` | 0 | 1 s | RDQ 2800 pack, 41.4 Wh; CAD basic 1,483.3 g, CG 28.30 mm, SM 5.06 %; CG with the pack at -20: 26.5 mm (SM 5.8 %); its roll-up rows still use the old item list (1.466 kg), unchanged |
| proofs | `proofs/run_all.py` | 1 (strict) | 4 s | the known 5 (ELEVON-TORSION-FOAM, HORN-BEARING-STALL, HORN-RIB-FOAM-HOLD / STALL, LINKAGE-FREEPLAY) plus the mass / CG / energy ones: **MASS-PRED and MASS-GATE-ROOM 1.704 kg vs 1.47 (part 2: 1.615)**, CUTS-REQUIRED 251.5 g, **CG-HI 28.3 vs 26**, CG-TRIM-AFT 30.12 vs 28.5, WINDOW-PRED -2.1 %, WINDOW-MASS 1.478 kg, CRUISE-AVAIL 173.5 vs 204.6 s, **TW-SAG-PRED 1.594 vs 1.6 (new)**; 14 distinct claims fail |
| drawings | `make_drawings_a.py` (jobs + render, then `--compose`; the `-I` form cannot import compose_drawings) | 0 | 86 s + 95 s | 43 / 43 composed (41 before: WNG-011, WNG-012 added); hub step B0b text updated to the machined part in `a_build_steps.py` |

The 3-D gates (collide pose 21, linkage poses, assembly, build check) pass without exemptions. The failing proofs are mass / CG claims, not interference: the drawn parts now carry the decided masses (hub, skin) while the mass savings (R2, R3fix, R4) are not drawn.

## P3.8 Proposed text (for the conductor; not applied)
- CHANGE-LOG D-224 (T-077 p3, 2026-11-20): "CAD now carries D-220 / D-221 / D-222: machined 6061 hub (octagonal sleeves 16 mm across flats, L 32; 24 x 24 mm collar with a 30 mm bridge bore; 0.5 mm mouth and exit chamfers; junction radii 1.0 / 0.9 mm because OCC cannot fillet larger on the octagons; no pockets: 61.5 g = 22.78 cm3 x 2.70), staggered tapered doublers (s 11..47, +0.55 g each), glass skin shell 26.7 g (0.054 mm wet ply, EST) and cove CF strip 3.7 g. The collar crosses the pack strap path: strap moved to x -23.5..-3.5 and the pack back to centre -10 mm. CAD basic 1,483.3 g, CG 28.30 mm, SM 5.06 %: A-P4 CG-HI fails by 2.3 mm; rungs 1-3 cannot close it (rung 2 -0.3 mm, rung 1 needs the leads moved and still gives 26.5, rung 3 has no strength margin); the decided-but-undrawn aft items add about +3.8 mm (EST). Not drawn: X7 node, CF clamshell, R2 / H743, R3fix, R4 (specification gaps). Gates: collide pose 21, 18 linkage poses and the 66-step assembly pass; proofs fail on mass and CG."
- BOM (not edited): 6061-T6 bar about 63.5 x 63.5 x 50.8 mm x 2 (T-080 V7, price "-"); glass cloth 48 g/m2 about 0.33 m2 per aircraft plus epoxy (O4b list, price "-"); CF strip 3 mm2 x 0.8 m (price "-"); the longer doublers use the same 14x12 CF tube (+0.55 g each).
- MASS-GATE basis: hub 61.5 g solid (T-080 est. 24-30 g with pockets), skin 26.7, strip 3.7, doublers +2.2; the hub is no longer a printed part (removed from `printed_mass.json`).

## P3.9 Limits
Strength of the drawn hub, collar and doublers: not checked (H-A1 / H-A2 not run). Skin thickness 0.054 mm and the strip split 6 x 0.5 mm are EST; the skin was collision-checked at its real thickness, but the 0.05 mm tolerance is close to it, so a skin / part overlap below 0.05 mm would pass. 6061 density is from a secondary source. The pocket-free hub mass and all CG sensitivities are estimates labelled EST. Nothing was committed.
