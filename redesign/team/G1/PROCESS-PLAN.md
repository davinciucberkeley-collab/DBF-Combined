# G1 process plan: K09-L

Revision G1-R1, 2026-11-13. Status `PROPOSED`. Owner G1 (manufacturing engineer). Requirements: `R-PROCESS`, `R-CRASH-REPAIR` (`team/A2/REQUIREMENTS.md`).
Companion files: [`PROCESS-TABLE.md`](PROCESS-TABLE.md) (generated, all 133 parts.csv lines classified, 0 exceptions) ·
[`../G2/COMPOSITES-FOAM-PLAN.md`](../G2/COMPOSITES-FOAM-PLAN.md) (hot-wire, foam, tape, CF, epoxy) · [`../G3/PRINT-LIST.md`](../G3/PRINT-LIST.md) (every printed part) ·
[`../G4/BUILD-STEPS.md`](../G4/BUILD-STEPS.md) (work packages, sheets that match `BUILD-GUIDE.md`) · [`../I2/SCHEDULE.md`](../I2/SCHEDULE.md).
The per-part process, jig and skill-risk analysis is `review/MANUFACTURING.md` section 2 and 6 (J6 review, 2026-11-11); this plan turns its findings into decisions.

## 1. Verdict

| Check | Result | Source |
|---|---|---|
| Every parts.csv line is bought or made by an allowed process (`R-PROCESS`) | **pass, 133 of 133 lines, 0 exceptions** | `PROCESS-TABLE.md` (re-run the script after any parts.csv change) |
| Printed parts <= 0.2 m on any axis | pass, largest file 178.7 mm | `../G3/PRINT-LIST.md` section 4 |
| No composite lay-up, no machining beyond drilling | pass; the heated-U-wire / router slot cut is the one grey area, decided below | `PROCESS-TABLE.md` notes |
| Shop files exist for every printed part, every nested sheet, the hot-wire templates and 4 jigs | yes: 249 checks, 0 FAIL | `manufacturing/out/CHECKS.md` (MF-01 fixed, D-79) |
| Crash-repair spares (`R-CRASH-REPAIR`: 1 motor, 4 ESCs, 8 props, 1 CF tube, 4 feet) | **partly: ESCs and props fall short, see section 6** | `team/I1/BOM.csv` |
| Where hot-wire cutting and epoxy work happen | **open: Jacobs lists no hot-wire cutter; a ventilated team workspace is needed** | `CR-G1-01`, `../I2/SCHEDULE.md` `CR-I2-04` |

## 2. Where each process happens (Jacobs Maker Pass, checked 2026-11-13)

The Maker Pass is paid by the owner outside the budget (2026-11-13). It is drop-in access to the Jacobs Hall makerspaces with tool-specific training, not equipment loans
(https://jacobsinstitute.berkeley.edu/making-at-jacobs/). Tool list: https://jacobsinstitute.berkeley.edu/our-spaces-at-a-glance/labs-and-equipment/. Hands-on trainings run only in the first half of a semester, so the
fall window (31 Aug - 23 Oct per `review/MANUFACTURING.md`) is closed (`../I2/SCHEDULE.md` `CR-I2-03`).

| Process | Where | Tool (source) | Training / access | Open |
|---|---|---|---|---|
| Hot-wire XPS cores, saddles, cartridge sticks | **team workspace** (not Jacobs) | bought supply and Ni80 wire `G11`, bow and templates `H05` | none; XPS fumes: extraction or outdoors (`BUILD-GUIDE.md` safety) | name the workspace (`CR-G1-01`); ask Jacobs whether the ShopBot may cut XPS (a yes would replace the hot wire for cores) |
| Laser cutting: S5010 templates, ply jigs, mat panels, foam-board nests | Jacobs studios 110 / 120: 3 x 32 x 18 in, 1 x 48 x 25 in | Universal laser cutters | laser training (hands-on) | foam board on the laser is not stated (`config-study/README.md` line 275); knife-cut from the 1:1 PDF is the fallback |
| Knife-cut foam board, Coroplast, XPS finishing | bench, anywhere | knife, steel rule | none | none |
| Spray lamination (3M 77) of fin boards | Jacobs spray booth with fume hood | spray painting booth | booth training (not stated: ask) | confirm access and training |
| FDM printing | Jacobs Prusa printers (PLA free, no training for PLA); team printers | Prusa, LulzBot TAZ 6, Form 3 and Markforged in the staffed lab (room 332) | none for PLA per the page | PETG not stated; **ASA needs an enclosed printer, not on the open list** (`../G3/PRINT-LIST.md` `CR-G3-01`) |
| Drilling (pin holes, mount holes, cartridge bores) | Jacobs drill presses: Delta (woodshop), Clausing (metal shop) | drill press | woodshop / metal-shop training | none |
| Band saw (PE foam columns) | Jacobs Laguna 18 in band saw (woodshop) | band saw | woodshop training | none |
| Soldering, heat gun, multimeter, bench supply, scope, FR4 shear | **Jacobs Electronics Lab, studio 110** (iron, solder, fume extractor, PCB shear) | lab equipment (BOM lines G07-G09 deleted 2026-11-13) | electronics training | flux and wick not stated (`G10` gated X10); **lab is closed 19 Dec - 18 Jan: no soldering then** |
| Epoxy, CA, 3M 77 at the bench | team workspace | bought consumables (C04, C05) | none | ventilation, nitrile gloves |
| CF tube cutting | team workspace or Jacobs band saw | fine-tooth saw on tape; dust mask and vacuum (`BUILD-GUIDE.md` safety) | none | CF dust: do not use Jacobs machines for CF without asking |
| Heat tent (post-cure collars 4 h at 50 C, mounts) | team workspace | box, lamp, thermocouple (SW-14) | none | thermocouple probes are in `G12` |

## 3. Process decisions per risky part

Each row closes one finding of `review/MANUFACTURING.md` section 2 for the build. "Gate" is the inspection that stops the next step.

| Part (id) | Process decision | Jig, template, fixture | Gate (accept by) | Time `EST` | Source |
|---|---|---|---|---|---|
| Wing core `WNG-001` | Hot-wire, two S5010 templates (c 320, TE opened to 0.6 mm), LE on one line, **one 1.15 m pass**, bow >= 1.25 m; cut 2 cores, finish 1, keep 1 bare; **2-3 practice cores first** | `manufacturing/out/hotwire/WNG-001_template_root.dxf` and `_tip.dxf`, 1:1 tiled PDF; LE alignment base; cradle beds = the offcuts | template gauge at three stations, chord 320 +/- 1 mm, TE >= 0.6 mm, LE ridge-free by touch | 1 h per cut; bow, templates, base 1-2 days | `wing/BUILD.md` step 2; MF-05 |
| Spar slot, pockets, grooves | **Hot tool or guided knife in the lower bed; router with a 22 mm ball bit and fence only as the fallback**; never lift a slotted core out of its bed | R 3.15 / R 3 corner templates, 45 deg block, depth gauges, printed 45 deg P1 guide | blocks and frames drop in with no corner contact; foam over pocket ceiling >= 4 mm | 1 day | `wing/BUILD.md` steps 3-5; SW-07 |
| Spar `WNG-002` + plugs | Buy 22 x 20 tube, scuff, bond printed plugs to the dowel marks, 24 h cure | marked 18 mm dowel (180 / 258 mm) | dowel marks; tap test | 1 h + 24 h | `wing/BUILD.md` step 6 |
| Through-core blocks `FIN-004` | PETG FDM; bond to the spar in the clocking jig with silica-thickened epoxy | **JIG-01 tube posts** (`manufacturing/out/jigs/`), ply base board and top bar (laser 3 mm ply) | blocks at y +/-320 +/- 1 mm; bores parallel and vertical within +/-0.5 deg | print 92 min each (`../G3/PRINT-LIST.md`); jig 1 day | MF-06 |
| Elevons `WNG-011/012` | Knife cut from the core after the pass; torque-tube groove with a depth stop **while the core is whole** | router depth stop or groove guide (to draw: `CR-G1-02`) | >= 1 mm foam over each tube; panels 228 / 218 mm | 3-4 h | `wing/BUILD.md` step 9; SW-17 |
| Tape skin `WNG-003` | Hand-laid 48 mm strips, 10 % overlap, 100 mm LE strip last; no seam within 32 mm of the LE | pen lines at x 41.8 / 45.5 / 46.6 mm; ruler gauge | rule from the LE at five stations each side >= 32 mm (`CL-D1-LE-SEAM-X`) | 3-4 h for two | `wing/BUILD.md` step 11 |
| Half-fins `FIN-001` x 4 | Spray-laminate two 4.8 mm boards (booth), measure laminate 9.6 +/- 0.3 mm, then knife- or laser-cut from the DXF; root follows the S5010 contour | `manufacturing/out/laser/foamboard_sheet*.dxf` (5 sheets, 4 spare laminates), `foamboard_1to1_letter.pdf` | laminate thickness measured before the slots are cut | 3 h | `fins/BUILD.md` step 1 |
| Motor tubes `FIN-002` + plugs `FIN-006` | Saw on tape, sand square; plugs sanded to fit; 344 +/- 0.5 mm | mitre block / saw guide (to draw: `CR-G1-02`) | 344 +/- 0.5 mm; plug fit | 1 h + 24 h | `fins/BUILD.md` |
| Motor mounts `FIN-003` | ASA print, drill 3.4 mm **from a printed guide, never through the motor**, feeler check of the 1.5 mm slit; post-cure in the heat tent | **JIG-03 cant gauge A/B** (7 deg), squaring block | cant 7 +/- 1 deg with the inclinometer; slit feeler | 1 h per mount | MM-01, MM-04; `fins/BUILD.md` steps 18-19 |
| Station collars `FIN-008` | PETG 100 %; **ON HOLD** until the 18 Dec freeze (STATUS issue 1); clock the collar notch if the keyed mount is used | JIG-02 fin-alignment collar | dry fit and inspection table | hold | STATUS issue 1; MF-13 |
| Edge strips, 48 pins, braces `FIN-009/011/012` | Cut CF strip; drill 2.5 mm through strip-laminate-strip on a drill press with a square guide; inject epoxy; **pin row depends on the tip decision** | pin drill guide (to draw: `CR-G1-02`) | pins flush; hole square | 4 h | `fins/BUILD.md` |
| Pod board and prints | Knife- or laser-cut foam board; XPS filler hot-wired; seven PETG prints epoxied full-area to the board | DXF nest on 20 x 30 in sheets | box square; tray flat | about 8.5 h + 3 x 24 h | `pod/BUILD.md` |
| Cartridges `GER-003/008/010/011` | XPS F-400 sticks 20.9 x 11.0 x 35.0, half bored with the sharpened 5/32 in brass tube, each **pressed to 34.0 mm on a drill press**; 108 sticks | stick-cutting fence and pre-crush block (to draw: `CR-G1-02`) | stick length and crush depth by gauge | most of a day | `landing/BUILD.md`; MANUFACTURING section 2 |
| Power bus `PWR-004`, frame `PWR-006` | Shear FR4 in the Electronics Lab, file the slot, solder 8 AWG bars (80-100 W iron), PETG frame | lab stations | polarity, > 1 Mohm between rails, loop resistance logged | about 3 h + 24 h | `power/BUILD.md`; BUILD-GUIDE stage 5 |
| Harness `HRN-*` | Cut, twist, label, crimp on the bench; **solder only in the Electronics Lab** | wire-list labels, a layout board | `T-F2-CONT`: every net < 0.1 ohm, > 1 Mohm between nets | 1-2 days | `harness/WIRE-LIST.csv`; stage 6 |
| Transport box `TRN-*` | Score and fold Coroplast (knife and straightedge; panels exceed every laser bed), hot-wire saddles to the S5010 template, laser ply strips and mat | saddle template from a taped wing rib | box closes with the aircraft seated; MF-16 | about 6 h for two + 1.5 h mat | `transport/BUILD.md` |
| Ground fixtures (stand, lever frame, whiffletree, tilt board, foot sled, CG jig) | Each is its own small build; hours not in any older estimate (MF-23) | `team/H1/GROUND-TEST-PLAN.md` | per card | in the I2 load (`H01`, `W02`) | MF-23 |

## 4. Jigs, templates and fixtures: inventory

| Item | Status | File | Used by |
|---|---|---|---|
| S5010 hot-wire templates, root and tip | drawn (DXF + 1:1 PDF) | `manufacturing/out/hotwire/` | wing core, cradles, box saddles |
| JIG-01 tube posts x 2, JIG-02 fin-alignment collar x 4, JIG-03 cant gauge A/B x 2 + 2 | drawn (STL) | `manufacturing/out/jigs/` | blocks, tubes, mounts |
| Foam-board and Coroplast nests, ply sheets (JIG-01 base, handle strips, mat) | drawn (DXF) | `manufacturing/out/laser/` | fins, pod, box, jigs |
| Block clocking jig base and top bar | drawn as ply parts | `laser/ply3_sheet*.dxf` | spar bond |
| Pin drill guide, mitre block, cartridge fence and pre-crush block, router depth stop, 45 deg P1 guide, build stand, CG jig | **named, not drawn** | none | `CR-G1-02` to A5 (CAD) or build from stock by G4 |
| LE alignment base, cradle beds | made on the bench from the core offcuts | none | wing core |

## 5. Tolerances that decide whether a part is accepted

From `review/MANUFACTURING.md` section 5 (hand-build reality) and the BUILD.md files. Measure and log in the build traveler (G4); out-of-band parts go to A3 and the owner, not into the aircraft.

| Feature | Spec | Gauge | If out |
|---|---|---|---|
| Spar bore | OD + 0.4 mm (0.1-0.3 mm per side) | feeler | re-cut slot |
| Core straightness / twist | 1 mm over the span, both TEs on the bench | straight edge, bench | core 2 |
| Block y-station | +/-1 mm at y +/-320 mm | jig, rule | rebond before cure |
| Tube vertical / parallel | +/-0.5 deg (blocks 1 deg) | JIG-01 posts, inclinometer | rebond |
| Motor cant | 7 +/- 1 deg | JIG-03, inclinometer on the can | re-print or shim |
| Motor face to collar | 7.5 +/- 0.5 mm | spacer block | spacer |
| Laminate thickness | 9.6 +/- 0.3 mm | calipers | re-laminate |
| CG x | 0.0472-0.0508 m accepted band (marks 46.6 / 51.4 mm on the jig) | CG jig | ballast only as trim (`BUILD-GUIDE.md` stage 11) |
| Fillet and bead mass | weigh a cup from every batch (<= 13 g for 20 cm3 of bead mix) | 0.1 g scale | tell A3 before the next batch (MF-14) |

## 6. Crash repair (`R-CRASH-REPAIR`)

Requirement: a crashed wing core is re-cut and skinned in <= 1 day from stock on hand (>= 1 spare XPS sheet, templates and STLs kept in the repo); the BOM holds 1 motor, 4 ESCs, 8 props, 1 CF tube, 4 feet.

| Needed | In the BOM today (`team/I1/BOM.csv`, 2026-11-13) | Status |
|---|---|---|
| XPS sheet for a re-cut core | `W01`: one 2 in x 4 x 8 ft sheet, about 6 cores; 2-3 are used by practice | **pass if practice uses at most 3**; keep core 2 and one bare core (`review/MANUFACTURING.md` section 5) |
| Templates, STLs, DXFs | in the repo (`manufacturing/out/`) | pass |
| 1 spare motor | `B01` 4 fitted + 1 spare | pass |
| 4 spare ESCs | `B02` is a 4-pack, 0 spare; the spare pack is gated `X01` ($33.08) | **short by 4** until `X01` passes its gate |
| 8 spare props | `B03` 4 fitted + 4 spare 11x5.5; the stand props `B04` are 11x4.5 | **short by 4** (gated `X03` is the optional E pair, not spares) |
| 1 spare CF tube | `W03` (bend-test tube, then spare) + `W04` x 2 for spar and motor tubes | pass |
| 4 feet | 2 spare shoes, 8 spare pistons, 16 + 16 spare cartridges (`GER-005/009/010/011/012`) | pass |

**Repair timing.** A core re-cut is 1 h of hot wire + sanding, but a core with blocks and tubes is about 4-5 days through the same cure chain (`review/MANUFACTURING.md` section 5), so `R-CRASH-REPAIR` (<= 1 day) holds only for a bare skinned core; the plan therefore keeps core 2 and the spare block, collars and mounts finished before the first hover (`I2` task `CR1` allows 11 days). Decision for A2: reword the requirement to "bare core 1 day, fin station 4-5 days".

## 7. Safety by process

Procedures are `BUILD-GUIDE.md` Safety and `../H3/BATTERY-PROCEDURE.md`. Hot wire: XPS fumes, never unattended, lowest supply current that cuts cleanly. Epoxy and CA: nitrile gloves, ventilation, no CA or solvent glue on XPS. CF dust:
mask and vacuum. LiPo re-termination: below 3.8 V per cell, one lead bare at a time, in the Electronics Lab with staff aware. Spray 3M 77 only in the booth.

## 8. Change requests from G1

| # | To | What | Why |
|---|---|---|---|
| CR-G1-01 | Team lead, I2 | Name a ventilated workspace for hot-wire cutting, epoxy and spray bench work by 30 Nov; ask Jacobs if XPS may be cut on the ShopBot | Jacobs lists no hot-wire cutter |
| CR-G1-02 | A5, D3, D5 | Draw or confirm the undrawn aids: pin drill guide, mitre block, cartridge fence and crush block, router depth stop, 45 deg P1 guide, build stand, CG jig | `manufacturing/out/jigs` has 4 |
| CR-G1-03 | I1, A2 | ESC spares (4) and spare props (4) are short of `R-CRASH-REPAIR`; decide the gate `X01`/`X03` or reword the requirement | section 6 |
| CR-G1-04 | A2 | Reword `R-CRASH-REPAIR` as above | section 6 |
