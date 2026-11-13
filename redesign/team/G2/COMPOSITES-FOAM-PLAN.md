# G2 composites, foam and hot-wire process plan: K09-L

Revision G2-R1, 2026-11-13. Status `PROPOSED`. Owner G2 (composites and foam specialist). Part of the G1 plan: [`../G1/PROCESS-PLAN.md`](../G1/PROCESS-PLAN.md).
Scope: hot-wire XPS cores and saddles, spar and tube bonding, epoxy and microballoon work, foam-board fins, packing-tape skin, CF tube cutting. Printing is [`../G3/PRINT-LIST.md`](../G3/PRINT-LIST.md);
the order of work is [`../G4/BUILD-STEPS.md`](../G4/BUILD-STEPS.md). Dimensions come from the BUILD.md files (`subsystems/wing`, `fins`, `pod`, `landing`, `mechanisms`), not from here.
Every number below is cited to a repo file or marked `EST`; unknowns are `-`.

## 1. Materials and what the BOM holds

| Material | Spec | BOM line | Note |
|---|---|---|---|
| XPS core | FOAMULAR NGX F-250, 2 in x 4 x 8 ft, <= 30 kg/m3 (else tell A3: +6.2 g per +1 kg/m3) | `W01` | about 6 cores per sheet; blank 1 200 x 330 x 50 mm (`wing/BUILD.md`) |
| Foam board | 20 x 30 in, 4.8 mm, paper faced, 10-pack | `W02` | fins (8 boards), pod shell, first foam-board twin |
| Packing tape | Scotch Heavy Duty 48 mm, 6 rolls; clear 100 mm for the LE strip | `W06` (100 mm roll: **not itemised**, `CR-G2-01`) | skin 47.9 g (`WNG-003`) |
| Epoxy | 30 min laminating epoxy + colloidal silica + glass microballoons | `C05` (small kit) | **quantity is short**: `BUILD-GUIDE.md` consumables lists epoxy "by the quart" (BR-32); `CR-G2-01` |
| Foam-safe glue | UHU Por / Gorilla clear | `W07` | **no CA, no solvent glue on XPS** |
| Spray adhesive | 3M 77 class | `FIN-106` (not a BOM line: `CR-G2-01`) | spray booth only |
| CF tube, strip, rod | 22x20 tube; 20x18 plug tube; 10 x 2 and 10 x 1 strip; 2.5 mm rod; 5x4 torque tube | `W03`, `W04`, `D01`-`D03`, `C03`, `H02` | tubes cut by hand, tape-wrapped |
| Hot wire | Ni80 24 AWG (0.51 mm), supply 30 V class, bow >= 1.25 m | `G11` (EARLY order), `H05` | bought: Jacobs lists no hot-wire cutter (checked 2026-11-13) |

## 2. Hot-wire cutting: set-up and practice protocol

**Decision.** Cut with a bow at least 1.25 m long, one pass per core, two templates (S5010, chord 320 mm, TE opened to 0.6 mm), LE on one line (`wing/BUILD.md` step 2, `review/MANUFACTURING.md` section 1).
`manufacturing/out/hotwire/WNG-001_template_root.dxf` and `_tip.dxf` (1:1 tiled PDF with registration crosses) are the template drawings. `wing/BUILD.md` specifies 2 mm ply or hardboard; cut them on a Jacobs laser cutter if staff allow that stock, else print the 1:1 PDF, glue it to the board and cut and sand to the line.
Kerf for the template offset is about 1 mm (`manufacturing/shopconfig.py`, from `wing/params.json elevon.end_gap_m`); wire 0.51 mm Ni80 24 AWG (BOM `G11`).

**Electrical set-up (`EST`, measure it).** A 24 AWG Ni80 wire is about 1.62 ohm per foot (a secondary resistance table read on 2026-11-13, not a datasheet); for a 1.25 m span (4.1 ft) R = 4.1 x 1.62 = 6.6 ohm.
For 2.5 A (a typical start value, `EST`) the supply must give V = I x R = 2.5 x 6.6 = 16.6 V and P = 41 W. The listed supply (ASIN B0CRSS744F, title "0-30 V 0-10 A 150 W, 15 V 10 A / 30 V 5 A") covers this.
**Start low, raise until the wire cuts a test strip at walking pace without drag, then record V, I and feed rate in the cut log.** The correct value is the lowest that cuts cleanly (`BUILD-GUIDE.md` safety).

**Practice cores (2-3, then stop).** Purpose: LE quality sets stall (B2: a turbulent LE costs 7 % stall speed; stall margin is +0.05 %, `BUILD-GUIDE.md` stage 2). Use the practice cores as the sheet allows (`../G1/PROCESS-PLAN.md` section 6: at most 3).

| Step | Do | Accept by |
|---|---|---|
| 1 | Cut a 300 mm test block with the real templates and record V, I, feed, kerf | kerf 1 +/- 0.3 mm |
| 2 | Cut a full 1.15 m practice core; sand the LE with a long 120-grit block | no wire step or ridge felt along the LE |
| 3 | Check at three stations: chord 320 +/- 1 mm, TE >= 0.6 mm, twist (both TEs on the bench) | template gauge; feeler |
| 4 | Weigh the core against `WNG-001` 201.9 g (CAD mass, `wing/parts.csv`) | within the A3 band; tell A3 |
| 5 | Repeat until two consecutive cores pass steps 2-4, or three cores are used | then cut cores 1 and 2 |

Where: team workspace with extraction or outdoors (XPS fumes). **Never leave the wire powered unattended.**

## 3. Process sheets

Times are hands-on and `EST` from `BUILD-GUIDE.md` / `review/MANUFACTURING.md`; cures are separate. Cure rule: 30 min epoxy handles after 1 h, loads after 24 h at >= 18 C; laminating epoxy 24 h (`wing/BUILD.md`, `fins/BUILD.md`).
Parts within 50 mm of a motor get 4 h at 50 C (C6, `fins/BUILD.md`): the heat tent is a box, a lamp and a thermocouple (SW-14); keep XPS and tape below the foam limit (`-`: C6 sets it, not stated in the sources read).

### P-01 Wing core (WNG-001) and bare-wing prep

| Item | Detail |
|---|---|
| Input | XPS blank, templates, bow, cut log |
| Steps | wing BUILD steps 1-2: measure and weigh the blank; hot-wire the 1.150 m section in one pass; trim ends square at y +/-0.575 m; sand the LE; mark y 0 and the cut-table stations |
| Accept | chord 320 +/- 1 mm at both ends and mid-span; TE >= 0.6 mm; weighed |
| Hazard | fumes; hot wire; do not touch the wire |
| Make two | cut 2 cores, finish 1, keep 1 bare with its slot (`review/MANUFACTURING.md` section 5) |

### P-02 Slot, pockets, grooves (core in its lower bed)

| Item | Detail |
|---|---|
| Steps | wing BUILD steps 3-5: 22.4 mm spar slot from below, centred x 80 mm, to z +17.8 mm, |y| <= 500 mm; block pockets x 28-97 mm with R 3.15 mm corners from the printed template; 3 x 3 mm 45 deg lip chamfers; anchor pockets; pod saddle windows and recess; servo pockets from below; signal and power grooves; JR recess 18 x 10 x 5 mm; P1 pass 8 mm at 45 deg |
| Tool decision | heated U-wire on a guide rail or a guided knife first; the router is the fallback only (`../G1/PROCESS-TABLE.md` notes) |
| Accept | tube slides in with 0.1-0.3 mm per side, top 4.8 mm under the upper skin (>= 2 mm); blocks and frames drop in with no corner contact; foam over the pocket ceiling >= 4 mm; 3.0 mm foam between the aft groove and the slot |
| Rule | **never lift a slotted core out of its bed** (SW-07) |

### P-03 Spar plugs, spar and blocks into the core

| Item | Detail |
|---|---|
| Steps | wing steps 6-8: scuff tube ends and bore (120 grit, IPA); butter each plug with thickened epoxy; push the anchor plug first (centre 258 mm from the tube end) then the block plug (centre 180 mm) with the marked dowel; 24 h cure. Blocks on the spar in the clocking jig at y +/-320 mm (thickened 30 min epoxy); then bond spar and blocks into the core with microballoon epoxy, fill the lip-bead chamfers in the same pour, weight the core on the bench with the LE on a straight edge; 24 h |
| Accept | dowel marks; tap test hard spots; core straight within 1 mm; no twist; blocks at y +/-320 +/- 1 mm; bores parallel and vertical within +/-0.5 deg in the jig; beads continuous and flush within 0.3 mm |
| Time | 1 h + 24 h; jig step 3 h; bonding 3 h + 24 h (`../I2/SCHEDULE.md` `B03`-`B05`) |
| Open | **SW-01: the through-core block strap eyes stop the block entering its pocket: pending fix before this step** (`BUILD-GUIDE.md` stop items) |

### P-04 Elevons and torque tubes

| Item | Detail |
|---|---|
| Steps | wing step 9: vertical cut at x 249.6 mm over |y| 70-300 and 340-560 mm; leave foam to R 3 mm at the four tab corners; trim 1 mm at the ends; 30 deg lower bevel; route the 5.4 mm torque-tube groove from below with a depth stop **while the core is whole**; knife the 2.5 mm horn-blade slots; bond the 5x4 tubes flush (microballoon epoxy, 24 h) |
| Accept | panels 228 and 218 mm long, chord 70.4 mm; >= 1 mm foam over each tube; corner radii by gauge |
| Time | 3-4 h + 24 h |

### P-05 Motor tubes, half-fins and the fin station

| Item | Detail |
|---|---|
| Steps | fins BUILD steps 1-11: measure stock (tube OD 22.0 +/- 0.1 mm, board 4.8 +/- 0.2 mm); spray-laminate board pairs in the booth, roll flat, weight 1 h; knife- or laser-cut the four half-fins (stepped tip per D-75, 8 mm hole by a twisted sharpened brass tube); cut tubes 344 +/- 0.5 mm; plugs sanded to fit and epoxied (24 h); test-fit prints; tubes through boss, block, boss; squared in the jig; epoxy 24 h; half-fin roots and cove fillets |
| Fillet mix | microballoons about 3 : 1 by volume with laminating epoxy, <= 3 % colloidal silica, <= 0.45 g/cm3 cured, about 14 cm3 per root; **weigh a 20 cm3 cured cup from every batch** (MF-14: the CG has no aft margin) |
| Accept | laminate 9.6 +/- 0.3 mm; tubes vertical within 0.5 deg; half-fin +6.3 g after fillet (weigh before and after); no filler in lead holes or elevon gaps; **no fillet on the lower link-slot zone** (CR-D6-04) |
| Hold | collars `FIN-008`, pin row and tip: wait for the 18 Dec freeze (STATUS issue 1) |

### P-06 Edge strips, pins, braces

| Item | Detail |
|---|---|
| Steps | cut CF strips (10 x 1 x 224 mm, 8; 10 x 2, 4); fit and drill pins **on the bench, flat, before the half-fin is on** if the team adopts SW-04; 2.5 mm pins through strip-laminate-strip with a square guide; inject epoxy |
| Accept | pins flush, hole square; 48 holes logged |
| Hazard | CF dust: mask and vacuum |

### P-07 Packing-tape skin

| Item | Detail |
|---|---|
| Steps | wing step 11: lower surface first, spanwise strips from the TE forward, 10 % overlap, the forward strip ending at x 41.8 mm; upper the same (40.8 mm); then the 100 mm LE strip per half-span, laid last, upper edge on the pen line at x 45.5 mm, lower edge at x 46.6 mm; doublers over block pockets and servo pockets; tab-edge folds; tape both faces of each elevon; slit the tape round every lead |
| Rule | **no seam, overlap or doubler edge within 32 mm of the LE** (CR-B2-17); nothing runs on top of the tape (D-86); trim the tape square along the fin fillet (D-88) |
| Accept | rule from the LE at five stations each side: both LE-strip edges >= 32 mm (`CL-D1-LE-SEAM-X`); no wrinkles at the LE; grooves visible under the tape; skin weighed (47.9 g `EST`) |
| Time | 3-4 h for two people |

### P-08 Foam-board pod and box parts

| Item | Detail |
|---|---|
| Steps | pod shell, hatch: knife- or laser-cut from `manufacturing/out/laser/foamboard_sheet*.dxf`; XPS filler and crush blocks hot-wired; printed prints epoxied full-area to the paper; transport saddles hot-wired to the S5010 template |
| Accept | box square, tray flat, saddles seat the wing (`../G4/BUILD-STEPS.md` stage 5) |
| Time | pod about 8.5 h + 3 x 24 h cures (`BUILD-GUIDE.md` stage 5) |

### P-09 CF tube cutting (all tubes and strips)

Tape over the cut line, fine-tooth saw through the tape, square the ends on 120 grit, scuff bond zones, IPA. Tubes: 22 x 20 x 344 mm (2), spar 1 000 mm, 20 x 18 x 53 mm plugs (2). Check lengths with calipers and a steel rule; log. Mask and vacuum for dust. Not on Jacobs machines without asking.

## 4. Coupons and proof articles that belong to G2's process

| Coupon / article | Why | Where defined |
|---|---|---|
| Tape-skin seam and peel coupon | LE seam rule and warm peel (3.5 N at the TE, 10 min) | `team/H1/GROUND-TEST-PLAN.md` GT-15 |
| Fin test article (300 mm wing stub, block, tube, one half-fin, one foot) | rehearsal for stages 2-5 and `T-C4-FIN-PROOF` | `BUILD-GUIDE.md` stage 1 step 6; H1 GT-09 |
| Fillet cup weighing | CG | MF-14 |
| Bend test of the first 22 x 20 tube (`W03`) | decides the Aloft tube cart; result to I1 by 10 Dec | H1 GT-16 |

## 5. Hazards and PPE (this plan)

Nitrile gloves for epoxy and CA; ventilation for epoxy, 3M 77 (booth) and hot wire; mask and vacuum for sanded cured epoxy and CF; safety glasses at the saw and drill; keep the hot wire supply at the lowest cutting current.
H3's general safety is `../H3/BATTERY-PROCEDURE.md` and `BUILD-GUIDE.md` Safety.

## 6. Change requests from G2

| # | To | What | Why |
|---|---|---|---|
| CR-G2-01 | I1 | Itemise: epoxy in the quantity the build needs (consumable list BR-32: today `C05` is a small kit), 100 mm clear tape, 3M 77, mixing cups, nitrile gloves, IPA, microballoons for the fillet mass of 4 half-fin roots (about 14 cm3 each) | `BUILD-GUIDE.md` consumables note; `FIN-105/106` are not BOM lines |
| CR-G2-02 | A3 | Receive the cut-log weights per core and the cup weights per fillet batch | MF-14 |
| CR-G2-03 | C6 | State the foam-safe post-cure temperature for parts near the foam | heat tent (SW-14) |
