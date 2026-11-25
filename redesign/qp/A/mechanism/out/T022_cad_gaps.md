# T-022 CAD realism gaps, concept A (parent R-CAD-03/04/05; source T-016 `docs/capability-audit.md`)

Date 2026-11-19, branch redesign/v1, nothing committed. Analysis category: interference (static collision) and inspection of the CAD source; no kinematics, FEA or dynamics were run for this task. Paths: `A/` = `redesign/qp/A/`, `AM/` = `A/cad/amodel/`.

## Result in one paragraph
I checked every row of the audit's gap lists (section 4 stand-ins, section 1 "Gaps" column, section 5 unknowns) against the current `AM/*.py`. No CAD file was edited: every remaining gap is either already closed, or rests on a vendor dimension that no obtainable source publishes (the audit's EST/"-" items). Inventing those dimensions is forbidden by CLAUDE.md, and each is already marked in the part/body name with EST or "-". Two items need a decision (questions Q1, Q2 below). Gates were rerun on the unchanged model and are green (collision PASS, 0 overlaps; proofs fail the known 6).

## Gap table
Status key: CLOSED-ALREADY (where), FIXED-NOW (none this task), CANNOT (unknown dimension: part is marked in its body name; "measure on arrival" per `AM/electrical.py:9`), DECISION (question below).

| # | Gap (audit ref) | Current CAD (file:line) | Status |
|---|---|---|---|
| 1 | Elevon servo plain box, no ears/output boss (s4, s1 row 4, s5) | `electrical.py:1030` box 28.4 x 26.7 x 13.0, body name says 'ears and output boss "-"'; arm sits on case top, `ARM_Z0 = SV_Z1` (`:541`) with the rule that a measured boss raises ARM_Z0 and everything above it. Web check 2026-11-19 (readymaderc 85975, getfpv, hobbyrc, flymod): no ear span, hole positions or boss height published; the RMRC page says "See Drawing Below" and the drawing is an image not available as text. Heights conflict between listings (26.7 mm HV on hobbyrc; 31.10 mm for the standard ES3054 on alofthobbies), and which of 26.7 or 28.4 is the long axis including ears is not stated. The 32 mm ear span found belongs to a different model (ES09MD HV), not used. | CANNOT. Marked. Build step: measure the received servo (ears, boss, case axes) before the pocket is cut (pocket `wing.py:652-654` is 41 x 26.7+ mm in plan, so ears are inside it). |
| 2 | Servo retention: servo is epoxied in its pocket, no screws (s1 row 21) | edge `E-MEC-` 'servo in its pocket' `electrical.py:739` (epoxy) | CANNOT until ears are known; the design decision (epoxy vs ear screws) follows from the measured ears. See Q3. |
| 3 | Servo arm outline, hole row beyond used hole (s4) | `electrical.py:1016-1036`: hub bore for 23T, one 1.3 mm hole at 8.5 mm (D-212 rev 3 M-4), body name notes the unknown row | CANNOT (vendor arm drawing not published). Marked. |
| 4 | Horn, size EST (s4) | Now a made PETG 2 mm profile with rib through the elevon (D-212 rev 3, `electrical.py:551-556,1049-1056`); it is a made part, so its dimensions are design values, not vendor unknowns | CLOSED-ALREADY (D-212 rev 3). Remaining EST is only head radius `HORN_HR` 2.2 mm, a design value of the printed part. |
| 5 | Clevis sleeve, cheeks, clevis pin EST (s4) | `electrical.py:1059-1064`, names say EST 3.0 / 0.8 x 3.2 / 1.0 mm | CANNOT (vendor RMRC linkage set gives only the 1.2 mm rod). Marked. |
| 6 | Pushrod length "not stored", binding (s1 row 4, s5) | Derived from `tipx`, `xe` (`:1058`); ROD_LEG_L 2.50 mm leg, Z-bend keeper MEC-008, keeper height/vertical freedom constants (`:545-547`); linkage swept by mesh in T-020 (AR-007) | CLOSED-ALREADY (D-212 rev 3, T-020). Rod length hole-to-hole 43.25 mm remains a CALC, not a named constant: logging it is a record item, see proposed text. |
| 7 | Linkage not moved in collision (s1, s3) | `collide_a.py --linkage-poses` and `mechanism/elevon_sweep_collision.py` exist; last result `A/cad/out/REPORT_linkage_poses.md` (T-020 PASS) | CLOSED-ALREADY (T-020). Not rerun now: no linkage part changed. |
| 8 | Servo lead boot EST (s4) | `electrical.py:1031` body name says EST | CANNOT. Marked. |
| 9 | HRN-001 harness remainder, mass proxy (s4) | `electrical.py:692`, `proxy=True`, not a solid; the strands themselves are drawn as wires, the proxy covers splices, ties, heat-shrink, JST plugs | CANNOT as solids (no vendor shapes for ties/sleeves); stays a listed mass proxy. |
| 10 | HRD-001 hardware remainder, mass proxy (s4) | `electrical.py:696`, `proxy=True` (epoxy, paint, loose small hardware by mass); modelled screws/nuts are real shapes via `k9.hw_screw` | CANNOT as solids (epoxy/paint have no shape); stays a listed mass proxy. |
| 11 | ESC component envelope shape unknown, PCB thickness EST, solder mounds EST (s4) | `propulsion.py:245-258`: PCB 35 x 35 with 4 x 3.5 mm holes at 20 x 20 (V), 5.5 mm overall height (V), envelope outline EST, PCB 1.6 mm EST | CANNOT (SpeedyBee gives only the overall size). Marked in the body name. ESC is held by foam tape plus a tie (`propulsion.py:178`), no screws although the PCB has the 20 x 20 holes; that is a design choice, not a gap. |
| 12 | Motor base ring thickness/diameter, lead exit position (s4) | `propulsion.py:30-31,219`: base ring 3.5 mm thick (read off the side view +-1 mm), D 27.5; the 4 x M2.5 on 19 x 16 and 2-hole 12 mm top pattern are from the T-Motor drawing (V); lead exit EST | CANNOT (ring OD and exit not on the drawing). Marked. |
| 13 | Prop blade section shape, hub bore, adapter ring ID/OD, spinner ogive (s4) | `propulsion.py:84,154,43`: chord/twist/sweep from the APC PE0 file (V); hub D 0.65 in, T 0.34 in (V retail listings); bore 1/4 in "usually" (EST); ring OD/ID EST; ogive EST | CANNOT (APC publishes no section coordinates or bore for this size). Marked. |
| 14 | Adapter and spinner nut thread masses (s4) | `propulsion.py:162-164,183` CALC/EST | CANNOT (bell-top thread depth not published). |
| 15 | Pitot/airspeed barb positions and OD (s4) | `electrical.py:525-529,911-918,937-941`: probe 160 x 3 mm EST, block EST, barb OD 2.0 = tubing bore (V RMRC 2 mm ID) | CANNOT (RMRC gives no drawing). Marked. |
| 16 | Receiver antennas drawn 50 mm, real about 65 mm (s4) | `electrical.py:894-903`: antennas leave the RX at x 0.124 and run +x 50 mm to x 0.174. At the real 65 mm the tip is x 0.189, 5 mm past the hinge (XH 0.18375), and the inboard antenna at y -0.042 is inside the elevon span (|y| 0.04-0.35), so a full-length antenna would lie over the moving elevon | DECISION. See Q1. |
| 17 | Receiver/GPS retained by tape and tie only; RX/GPS/airspeed board sizes EST (s4) | `electrical.py:513-534,897-918` (RX size V 22 x 13 x 4; GPS/airspeed sizes EST) | RX CLOSED-ALREADY (V size); GPS and MS4525 board size CANNOT. Marked. |
| 18 | Wing core mass lumped (s4) | geometry drawn, mass single number (`wing.py:513`) | CLOSED-ALREADY in geometry; mass lump is an accounting choice, not a shape gap. |
| 19 | Hinge tape has no geometry (s4, s1 row 3) | `wing.py:557-558` joint only; tape thickness and width not in the BOM data | CANNOT. Drawing a tape solid needs a vendor thickness and the tape-to-skin layer; it would also sit on the skin surfaces, adding sub-0.1 mm contact the gate would count. Left as a joint only. See Q2. |
| 20 | Elevon chord fraction 0.25, inboard end 0.04, authority limit 20 deg (s4) | `common.py:33,35`, `wing.py:13` | CLOSED as design values (they define a made part; D-182..D-212 trade records), no vendor unknown. Remain labelled EST in the audit only because they are design inputs. |
| 21 | Printed parts 0.6 mm single wall caps/cover/conduits, EST basis (s4) | `wing.py:178`, `electrical.py:263,308` | Design values for made parts; slicer/wall choice is a bench check. Not a vendor unknown. |
| 22 | Wires are sharp-cornered polylines (s4) | `wire_inventory.py:11`; min bend radii in the table below (all >= rule 4 mm except noted) | CLOSED as a convention (centre lines; drawn fillets 1-3 % shorter). Bends below 4 mm are listed in the next section. |
| 23 | Exposed wiring non-zero (s1 row 23) | `wire_inventory.py` rerun now: EXPOSED 1.025 strand-m of 10.872. Per-edge list below | Listed per CLAUDE.md. Not closed: see list. |
| 24 | Exposed 0.87 on the site page vs 1.02 (s1 row 23, s2.1) | `redesign/site/app.html:453` | Record item for the site owner (not a CAD change). |
| 25 | Fasteners: threads analytic, no preload (s1 row 21) | `k9.hw_screw` real head/shank/thread shapes; joint stacks `STACK(...)` | CLOSED-ALREADY as a modelling convention; preload and thread helices are analysis scope, not CAD shape. |
| 26 | Structural parts: hub/arm FEA uses a re-meshed model, not the CAD body (s1 row 22) | `A/structures/fea_hub.py` (gmsh of its own hub model) | Out of T-022 scope (analysis fidelity, under the structures agent). Noted only. |
| 27 | Servo output spline axis y = 0.200 EST (s5) | `common.py:52` SERVO_Y | Design value, tied to the pocket and the hinge; the hole y follows from it. Measure-on-arrival item with the servo ear check (gap 1). |
| 28 | Servo free play, deadband, travel PWM map (s5) | Not CAD shapes | CANNOT. Bench items (claims CL-A-LINKAGE-FREEPLAY, `-`). |
| 29 | Hinge stiffness/friction (s5) | not CAD | CANNOT. Bench item. |

## Exposed wire list (CLAUDE.md rule), from `python -I A/cad/wire_inventory.py`, exit 0
Exposed length per edge (m per strand x strands = strand-m). Reasons from the edge notes in `electrical.py`.

| Edge | Path | Exposed per strand | Strands | Strand-m | Reason it cannot be enclosed |
|---|---|---|---|---|---|
| E-HRN-13 | pack power leads from the pack end face to the XT60 male, taped on the skin | 0.1075 | 2 | 0.215 | vendor leads, fixed length, outside the covered bay; the pack is strapped on and removable, so the leads must leave the tray |
| E-HRN-11 | I2C lead to the airspeed board in the left wing | 0.071 | 4 | 0.284 | crosses the wing top between the bay cover and the shallow channel; needs a skin slit routing to enclose (not drawn) |
| E-HRN-09 | RX UART (CRSF) | 0.073 | 4 | 0.292 | between the RX pads and the cover/groove entry; not enclosed in the current CAD |
| E-HRN-12 | 14 AWG tail XT60 female to ESC battery pads | 0.0425 | 2 | 0.085 | flat pair over the ESC, only 24 mm lies under the cover |
| E-HRN-14 | pack balance lead to the JST-XH plug on the pack top | 0.054 | 1 | 0.054 | vendor lead; plug must stay reachable for charging |
| E-HRN-07/08 | servo leads | 0.012 each | 3 | 0.072 | last length at the servo pocket from the groove to the case |
| E-HRN-10 | GPS lead | 0.003 | 6 | 0.018 | connector stub |
| E-HRN-01, 04 | XT60 mating / phase lead | 0.001 each | 1 / 3 | ~0.004 | mated connector and a tie point |
Total about 1.02 strand-m (inventory 1.025). Min bend radius below the 4 mm rule: servo leads 3.0 mm, RX 2.5, GPS 2.5, I2C 2.72 (26-28 AWG leads), E-HRN-14 1.5 mm and E-HRN-12 6.0 (ok); 4 mm rule applies to the 20 AWG phase leads (all 4.0). These small-bend leads are 26-28 AWG and are listed here, not changed.

Open improvement (not done, would change wiring and the wire inventory, the Blender build film and several gates): enclose E-HRN-09 and E-HRN-11 (0.58 strand-m, over half the exposed total) in a foam-core groove or the bay cover. See Q4.

## Questions needing a decision
Q1. Antennas. Real RP3 V2 antennas are about 65 mm (V in the code comment). At 65 mm the tips cross the hinge by 5 mm and the inboard one lies over the elevon span. Options: (a) draw 65 mm with the last 15 mm bent back/aft-laterally over the cover (a design choice with an assumed bend that is not a vendor shape); (b) shift the RX forward 15 mm so a straight 65 mm antenna ends at the hinge (moves RX_B, pad and wire routes, changes the mass CG slightly); (c) keep 50 mm and mark it. Recommendation: (b), because it keeps the antenna straight and real-length with the smallest assumption; cost is a re-route of E-HRN-09 and a full gate rerun plus the Blender build film. Not done now because it moves wiring and the build sequence.

Q2. Hinge tape. Do we model the tape strip as a thin solid (needs tape thickness/width from a vendor, not in the BOM) or leave the joint-only convention and list it? Recommendation: leave as joint only and list; its effect is below the 0.05 mm gate tolerance.

Q3. Servo retention. Epoxy in the pocket (current) or ears with screws? Cannot be decided before the received servo's ears are measured. Recommendation: epoxy as drawn plus a measured-ear check at receipt (AM-004 style, decide-and-log by the engineering agent then).

Q4. Exposed 0.58 strand-m on RX UART and I2C. Option: add shallow foam-core grooves under the existing skin tape, as the servo leads already do (D-199 grooves). Recommendation: do it as its own task after the antenna decision, because both touch the RX routing.

## Commands, exit codes, wall times (all on the unchanged model; no CAD source file was edited)
| Command | Exit | Wall | Result | Output |
|---|---|---|---|---|
| `python -I redesign/qp/A/cad/build_a.py` | 0 | 14.7 s | check PASS (10 modules, 0 errors, 0 warnings); mass 1273 g, CG 0.021, -0.002, 0.007 m | `T022_build_stdout.txt` |
| `A_ELEV_POSE=21 python -I redesign/qp/A/cad/collide_a.py` | 0 | 166 s | PASS, 486 bodies in 115 parts, 3 poses (static, -21, +21): 0 part pairs penetrate > 0.05 mm; wire ends not on a termination 0; wire folds 0 | `T022_collide_stdout.txt`, `A/cad/out/REPORT.md` |
| `python -I redesign/qp/A/cad/wire_inventory.py` | 0 | seconds | EXPOSED 1.025 strand-m; table above | `A/cad/out/wire_inventory.json` |
| `python -I redesign/qp/A/proofs/run_all.py` | 1 | 2 s | status CHECKED 321, UNVERIFIED 217, PROPOSED 17; fails 6, the known six (CL-A-HORN-RIB-FOAM-HOLD, -FOAM-STALL, CL-A-ELEVON-TORSION-FOAM, CL-A-HORN-BEARING-STALL, CL-A-LINKAGE-FREEPLAY, plus STRICT A-P13: CL-A-FLUTTER-ELEVON-NOM UNVERIFIED). Identical set and values to `T020_run_all_stdout.txt` | `T022_run_all_stdout.txt` |

Not run: `collide_a.py --linkage-poses` (no linkage part changed; last PASS `REPORT_linkage_poses.md`); Blender `a_assembly` (no build-sequence part changed, not needed). The rerun rewrote `A/cad/out/REPORT.md`, `report.json`, `_job.json` with the same results (timestamps/timing only; `git status` shows them modified).

Ledger note: `docs/session-log.md`, `A/structures/structures_a.py`, `structures_run.md` show as modified by other agents, not by me.

## Proposed CHANGE-LOG text (for the owner to paste; I did not edit it)
T-022 (2026-11-19) CAD realism gap review, concept A. Decision: no CAD change. Each gap of the T-016 audit was checked against the current CAD: horn, Z-bend keeper, linkage poses and pushrod are closed by D-212 rev 3 and T-020; the remaining items are vendor dimensions that no source publishes (servo ears, output boss and arm hole row; ESC component shape and PCB thickness; motor base ring; prop hub bore, adapter ring and spinner ogive; clevis hardware; pitot probe and barbs; GPS and MS4525 board sizes), all marked EST or "-" in the body names and listed as measure-on-arrival. Failure-resolution ladder: rung 0, no fix possible without inventing a dimension; rung 4, record and mark. Gates on the unchanged model: build_a PASS, collide PASS (0 overlaps at 0, -21, +21 deg), proofs fail the known six. Open questions in `T022_cad_gaps.md`: Q1 antenna length versus the hinge (recommend moving the RX 15 mm forward), Q2 hinge tape geometry, Q3 servo retention, Q4 enclosing the RX UART and I2C leads (0.58 strand-m exposed).
