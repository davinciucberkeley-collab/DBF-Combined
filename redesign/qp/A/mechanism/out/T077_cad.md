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
