# Manufacturing and build-plan review: K09-L, frame A1-R5

Reviewer: manufacturing (independent, read-only), 2026-11-11. Scope: how four part-time MEng students would
actually build K09-L at Jacobs Hall between 2027-01-19 and 2027-04-30 on a $2 000 budget. Sources are repo paths on
branch `redesign/v1` plus the Jacobs Institute web pages cited at the end. Numbers marked **(reviewer est.)** are my
judgement from student builds and are not in the repo. Every other number comes from the cited source.

## Verdict

K09-L is buildable by hand: it uses foam, tape, one tube spar, foam board and small prints, and every BUILD.md is
detailed. But the shop cannot start from this repo today. **No shop output exists.** There are no per-part STLs in
print orientation, no DXF for the fins or the pod board, no S5010 hot-wire templates, and no jigs. The Fusion
backend has never run, and the manufacturing roles G1–G4 never produced their process plan. The build also leans on
Jacobs Hall for things its equipment page does not list: hot-wire foam cutting and, as far as the page says, an
enclosed printer for ASA. Jacobs also charges Maker Pass fees that the $2 000 budget does not carry. Three
tolerances are tighter than a hand build reliably holds, and they feed straight into the CFD/FEA margins: block
clocking and tube verticality (spec 0.5° against a 1° block), blade-to-tube clearance (1.1 mm margin against a ±1°
cant tolerance), and the leading-edge finish (stall margin +0.05 %). The ten BUILD.md files disagree in at least
eight places on order or method. The plan has no spare spar and no spare motor tube. First hover in build week 4 is
reachable only if every print, template, jig and electrical sub-assembly is finished before 19 January and the
open fin-station decisions are frozen by mid-December. **Week 5 is the honest target.** Fix MF-01 to MF-04 before
more CFD/FEA. MF-05 to MF-08 change analysis inputs, so the analysts should get their tolerance bands first.

## 1. What Jacobs Hall actually has (checked 2026-11-11)

| Need in the BUILD.md files | Jacobs Hall, per its own pages | Consequence |
|---|---|---|
| Laser cutter (templates, ply strips, mat, fin outlines) | 3 × Universal 32 × 18 in, 1 × Universal 48 × 25 in (studios 110/120) | A 20 × 30 in foam-board sheet fits only the 48 × 25 bed; cut the sheet down first. Whether foam board may be lasered is not stated (the config study already flagged this, `config-study/README.md:275`) |
| FDM printers, PETG | Prusa printers, LulzBot TAZ 6 (1.2 mm nozzle), 2 experimental printers; Stratasys Fortus 380MC, Markforged X7, Form 3 in the staffed Advanced Prototyping Lab (room 332) | PETG is fine on Prusas. **ASA "enclosed printer" (D-42)** is not shown on the open-access list. Fortus/Markforged are staffed lab machines, not drop-in |
| Hot-wire bow and supply | **Not listed** on the labs-and-equipment page | `ORDER-PLAN.md` asserts "hot-wire foam cutting is a stated Jacobs capability". The current page does not support that (MF-03) |
| CNC for foam (alternative to hot-wire) | 4 × 8 ft ShopBot PRSalpha, 2 Othermills, Tormach (metal shop), OMAX waterjet | The ShopBot can machine an XPS core two-sided if Jacobs allows foam on it (ask) |
| Drill press (cartridge pre-crush, coupons) | Delta drill press (woodshop), Clausing (metal shop) | OK, needs training |
| Band saw (box PE columns) | Laguna 18 in band saw | OK, needs training |
| FR4 shear (power bus board) | PCB shear in the Electronics Lab | Better than "metal shear or hacksaw" in `power/BUILD.md` |
| Soldering, heat gun, meters, scope | Electronics Lab: irons, heat guns, multimeters, scopes, supplies, Saleae | Supports the X10 loan, in-lab only |
| Spray booth | Spray painting booth with fume hood | Use it for the 3M 77 fin lamination |
| Access | Maker Pass **$125 per student per semester** (affiliated class / community rate). Fall access ends **18 Dec 2026**. Hands-on training runs only in the first half of each semester (fall 2026: 31 Aug – 23 Oct) | Fees are not in the BOM (MF-02). There is no shop from 18 Dec until spring opens (MF-04) |

## 2. Part / process table

Time = hands-on time for the whole set unless stated; cures are separate. "Repo" means the time is stated in that
BUILD.md.

| Part (id) | Process · tool | Jig / template / fixture needed | Setup + time | Skill risk | Alternatives |
|---|---|---|---|---|---|
| Wing core `WNG-001` (XPS, 1.15 × 0.32 m) | Hot-wire, one 1.15 m pass, bow ≥ 1.25 m, 30 V supply, Ni80 wire | Two S5010 c 320 templates (2 mm ply/hardboard, TE 0.6 mm), LE alignment base, cradle beds (keep the offcuts) | Bow, templates and base: 1–2 days to make and tune; each cut under 1 h with LE sanding; plan 2–3 practice cores (reviewer est.) | **High.** Uneven feed, wire lag and burn-in at the thin TE; LE ridge costs stall (B2: 7 %) | ShopBot two-sided machining (ask Jacobs); buy a CNC hot-wire service cut (not priced); a cheap 4-axis CNC hot-wire is outside the budget |
| Spar slot, pockets, grooves, recess, servo pockets | Router with a 22 mm ball bit and fence, or a heated U-wire on a rail; knife, hot tool, 45° block | Cradle under the curved lower surface; printed R 3.15 / R 3 corner templates (named in `wing/BUILD.md`, not drawn); 45° P1 guide block; depth gauges | 1 day (reviewer est.) | **Medium–high.** Slot depth is referenced to a curved surface; 3.0 mm foam walls between groove and slot | CNC the slot and pockets on the ShopBot together with the core |
| Spar `WNG-002` + plugs `WNG-004/005` | Buy the tube, scuff; print PETG plugs; push to depth with a marked dowel | Marked 18 mm dowel (180/258 mm) | 1 h + 24 h cure | Low | none needed |
| Elevons `WNG-011/012`, torque tubes `MEC-009` | Knife cut from the core; 5.4 mm groove with 1.1 mm foam left under the skin | Router depth stop or groove guide (not drawn) | 3–4 h (reviewer est.) | **Medium.** Breaking through the 1.1 mm skin | Bond the tube in a lower-face groove and tape over it |
| Tape skin `WNG-003` | Hand-laid 48 mm strips, a 100 mm LE strip, doublers, tab folds | Pen lines at x 41.8/45.5/46.6 mm; a ruler gauge for the 32 mm seam rule | 3–4 h for two people (reviewer est.) | Medium (wrinkles at the LE, seam rule) | Laminating film (heavier, needs an iron) |
| Half-fins `FIN-001` × 4 | Spray-laminate two 4.8 mm boards (3M 77), knife- or laser-cut from DXF; 8 mm brass-tube hole; **root follows the S5010 contour** (`k09kit.py:446`) | DXF outline with the root contour (does not exist); stepped-tip template; brass-tube cutter | 3 h (reviewer est.) | Medium (root fit to a curved skin, 9.6 ± 0.3 mm laminate) | Laser-cut each single board with two registration holes, then laminate on pins |
| Motor tubes `FIN-002` + plugs `FIN-006` | Saw on tape, sand square; sand 20 × 18 plugs to fit | Saw guide / mitre block for 344 ± 0.5 mm | 1 h + 24 h | Low | — |
| Through-core blocks `FIN-004` × 2 | PETG FDM, 3 perimeters, 15 % gyroid, about 41 g each | **Clocking and spacing jig** that holds both bores parallel and vertical at y ±0.320 while the spar is bonded (not drawn; MF-06) | Print several hours per block (reviewer est.); jig 1 day | **High** (sets the thrust lines) | Add a key flat on the block and a matching printed key on the spar |
| Motor mounts `FIN-003` × 4 (+ spares) | ASA FDM in an enclosed printer; drill 3.4 mm to the real motor | Printed cant gauge (7°) and squaring block (not drawn) | 1 h per mount after printing; post-cure 4 h at 50 °C needs a heat box | Medium | CF-PETG or PETG (changes C4/C6 inputs); machined aluminium on Jacobs' Tormach/Othermill (heavier) |
| Station collars `FIN-008` × 4 | PETG 100 % | — | **On hold** (STATUS issue 1: "do not print collars or drill pins until settled") | Medium (dry-fit and the inspection table) | — |
| Edge strips, 48 pins, braces `FIN-009/011/012` | Cut CF strip; drill Ø 2.5 through strip–laminate–strip; inject epoxy | **Pin drill guide** square to the face (named, not drawn) | 4 h (reviewer est.) | Medium (48 holes, CF dust) | — |
| ESC pads `FIN-007` | ASA FDM | — | short | Low | PETG, if E3 accepts the temperature |
| Pod shell + hatch `POD-001/003` | Foam board, knife or laser; XPS filler and crush blocks hot-wired | DXF of the floor, walls, deck and hatch (not drawn) | Repo: about 8.5 h hands-on for the pod plus 3 × 24 h cures | Medium | Laser-cut the board parts |
| Pod prints `POD-002, 005–008, 010` and handle `POD-007` | PETG FDM, about 95 g, spacers in 4 colours | — | Printing over several sessions (reviewer est.) | Low–medium (full-area bonds to paper) | — |
| Landing shoes `GER-001` (4 + 2), pistons `GER-002` (4 + 8) | PETG FDM, rim end on the bed | — | Repo: 4 × 55 min shoes, 4 × 25 min pistons, 60 min bench, 24 h cure | Low–medium (fit is sensitive to extrusion) | — |
| Cartridges `GER-003/008/010/011` | XPS sticks 20.9 × 11.0 × 35.0, half of them bored, each pressed to 34.0 mm on a drill press | Stick-cutting fence and pre-crush block (block named, not drawn) | 108 sticks (12 fitted + 96 field kit): most of a day (reviewer est.) | Low (repetitive) | Hot-wire the sticks from a slab against a fence |
| Corner caps `GER-007` | **TPU 95A** FDM | — | 2 × 10 min (repo) | Low | — |
| Mechanisms prints `MEC-004…008`, pushrods | PETG; Z-bend pliers; pin vise | Flat board to clamp the panels at neutral | Per side, several hours plus 24 h cures (repo steps) | Medium | — |
| Power bus `PWR-004`, frame `PWR-006` | Shear FR4, file the slot, solder 8 AWG; PETG frame | — | Repo: about 3 h + 24 h | **Medium–high** (80–100 W iron, LiPo re-termination) | — |
| Harness `HRN-*` | Cut, twist, solder, crimp JR | Wire-list labels; a board to lay out the twisting | 1–2 days (reviewer est.) | Medium–high | — |
| Transport box `TRN-*` | Score and fold Coroplast; band-saw PE; hot-wire saddles; laser-cut ply strips and mat | Saddle template from a **taped** wing rib | Repo: about 6 h for two people + 1.5 h for the mat | Low | Separate taped panels (MF-16) |
| Ground fixtures (thrust stand, lever frame, whiffletree, tilt board, foot sled, CG jig) | Wood, steel plate, prints | Each is its own small build (`team/H1/GROUND-TEST-PLAN.md`) | Not in any hour estimate I found (MF-23) | Medium | Borrow or simplify where H1 allows |

## 3. Does the CAD give the shop what it needs?

| Output the shop needs | Exists? | Evidence | Missing |
|---|---|---|---|
| Per-part STL in print orientation | **No** | `showcase/stl/*.stl` holds one mesh per subsystem, in assembly position and in mm, decimated to ≤ 25 MB, for GitHub's viewer (`showcase/tools/export_stl.py` docstring). `pod/BUILD.md` says "export one STL per component" from Fusion, which has never run (`STATUS.md`) | A per-part exporter: one STL per printed part id, placed in the orientation the BUILD.md names, with spare quantities. It can be built on the stub or Blender backend without Fusion |
| Orientation / slicer settings | Partly, in prose | Landing, power, pod and mechanisms name a bed face; fins name infill only (blocks, collars, anchors) | Orientation for the blocks, mounts, collars and handle; seam position; a print list with counts, colours and spares |
| DXF: half-fin outlines (with the S5010 root contour) | **No** | `fins/BUILD.md` step 2 "from the DXF"; `make_fins.py:201` refers to it; no DXF writer anywhere (`grep dxf` finds only prose) | DXF of the 4 half-fins (upper and lower), stepped tip, LE notch, link slot, 8 mm hole, registration holes |
| DXF: pod floor, walls, deck, hatch | **No** | `pod/BUILD.md` step 3 lists dimensions in prose | DXF nest on a 20 × 30 in sheet |
| Hot-wire templates (S5010, c 320, TE 0.6) | **No** | `wing/BUILD.md` "print templates 1:1 from its sketches"; `wing.py` models the core as prisms with stepped radii ("the shop cuts the true radius from the template") | Template DXF/PDF from `s5010.dat` with the TE opened to 0.6 mm, a wire-kerf offset, LE/TE registration marks and the spar station mark |
| Corner, radius and bead templates | **No** | Named in `wing/BUILD.md` tools (R 3.15, R 3, 45° block) | A printable template sheet |
| Jigs: block clocking, spar bond, P1 45° guide, pin drill guide, cant gauge, cartridge crush block, CG jig | **No** | Named across the BUILD.md files and `GROUND-TEST-PLAN.md`; none modelled | Model them as `flight: false` parts so they print from the same exporter |
| Saddle template for the box | Partly | `transport/BUILD.md` step 6: trace from a taped rib | A DXF offset by the measured tape thickness |
| Build traveler (one ordered sequence across subsystems) | **No** | G4 "build order and work packages" not started (`STATUS.md` phases) | See MF-09 |

## 4. Findings

Severity: **Blocker** = the build cannot start or the budget gate fails; **Major** = costs a week, a crash or a
re-analysis; **Minor** = fix in passing. "CFD/FEA" = whether the fix changes an analysis input.

| ID | Sev. | Problem | Evidence | CFD/FEA? | Recommended fix | Cost / time |
|---|---|---|---|---|---|---|
| MF-01 | **Blocker** | No manufacturing outputs: no per-part STLs, no DXFs, no hot-wire templates, no jigs. Fusion never run. The G1–G4 process plan, print list and build steps do not exist | §3; `STATUS.md` ("G1–G4 process plan, print list, build steps" not done; `UNVERIFIED-IN-FUSION`); no `team/G*` folder | No | One person writes `fusion/export_shop.py` on the stub/Blender backend: per-part STL in print orientation, DXF fins and pod board from the CAD loops, S5010 template DXF from `s5010.dat`, jig parts. Run BuildAll once (H3) as a cross-check | 3–5 person-days (reviewer est.); $0 |
| MF-02 | **Blocker** | Maker Pass fees are not in the $2 000. At $125 per student per semester, four spring passes cost $500 against a $326 pessimistic reserve (margin over the crash reserve: $17.41) | Jacobs "Get Maker Pass" page; `config-study/README.md:248` flagged it `UNVERIFIED`; not in `team/I1/BOM.csv` | No | Ask the capstone instructor or Jacobs now whether the course is an affiliated class with comped passes, or whether the department pays. If the team pays, the budget needs a decision | $0 – $500 |
| MF-03 | Major | Hot-wire cutting is not a listed Jacobs capability. The BOM and order plan count on borrowing it (lever 2, $62.54) | Jacobs labs page lists no foam cutter; `ORDER-PLAN.md` gate X11 note; `JACOBS-LOAN-REQUEST.md` item 2 | No | Send the loan request (due 13 Nov) but treat X11 as bought. Buy the supply and wire in the early order so the bow and templates are tuned before 18 Dec | +$62.54; reserve falls below $309 unless offset |
| MF-04 | Major | Shop access gap. Fall access ends 18 Dec; spring hands-on training only runs in the first half of the semester. The order lands about 20 Dec; build week 1 is 19 Jan. Coupons (GT-15, "Dec – 16 Jan") and the fin test article (Dec) fall partly in the closure | Jacobs pages; `GROUND-TEST-PLAN.md` campaign order | No | Before 18 Dec: complete every tool training for all four students, cut templates, build the bow, print jigs and test articles. Plan the closure as home work: harness pre-fab, bus board, ESC/FC flashing, SITL. Ask Jacobs for intersession access | Moves about 3 days of work into November and December |
| MF-05 | Major | The wing core is the hardest hand operation: one 1.15 m pass, sanded LE, and the stall margin is +0.05 %. A first-time hot-wire core typically shows LE ridges and TE burn-through | `wing/BUILD.md` step 2; `README.md` stall 11.99 / 12.0 m/s; B2 "turbulent LE costs 7 %" | **Yes:** B2 should run stall against an as-built section tolerance (e.g. ±0.5 mm on the LE radius, TE 0.6–1.0 mm) and a tripped LE | Laser-cut templates with a kerf offset; two people with a weighted bow; 2–3 practice cores (the sheet gives about 6). Accept a core by template gauge at 3 stations. Alternative: ShopBot two-sided | 1–2 days and 1 XPS sheet already in W01 |
| MF-06 | Major | Block clocking and tube verticality. The blocks sit on a round spar with no key, so they are free to rotate. The block bore is "square within 1°" but the tube must be "vertical within 0.5°". A tube cannot be truer than the bore it passes through with ≤ 0.3 mm play. The two tubes must also be parallel to each other | `fins/BUILD.md` steps 5, 7, 10 | **Yes:** B3/B4 need a thrust-line misalignment band (pitch and differential) for hover trim and yaw authority (1.30) | A printed clocking jig that carries two 22 mm dummy tubes through both blocks off a flat base plate during the spar bond; or a key flat on block and spar. One tolerance, ±0.5°, for both steps | 1 day to design and print; $0 |
| MF-07 | Major | Blade-to-tube clearance is 26.1 mm against a 25 mm gauge (1.1 mm margin). Cant tolerance is ±1°, the mount is squared "to the fin" by eye, and the slip clamp is designed to rotate in a crash. At the 139.7 mm prop radius, 1° of disc tilt moves the blade about 2.4 mm axially (139.7 × sin 1°). Where on the blade the minimum sits is in B4's model | `README.md` key numbers (D-61); `fins/BUILD.md` steps 18–19 | **Yes:** B4 should re-run the clearance with ±1° cant, ±0.5° tube and ±0.5 mm face-to-collar tolerance | Printed cant/square gauge that indexes off the fin face; tighten cant to ±0.5°; check with the 25 mm gauge after every slip | $0; about 1 h per set-up |
| MF-08 | Major | The fin tip conflicts between subsystems. `fins/BUILD.md` (R5) cuts the step at x 0.2746, ends the strips there and pins up to x 0.264 ("shoe cheeks start at 0.2666"). `landing/BUILD.md` R6 says the step starts at x 0.2616 (58.4 mm) and the strips end at 0.2616. Pins at 0.264 then fall past the strip end | the two BUILD.md files cited | **Yes:** C4's `T-C4-FIN-PROOF` article is "D5 shoe as drawn", and the drawing has two versions | D3 re-issues the fin BUILD and DXF at R6; pin field ends 5 mm forward of the step | $0; must close before fins are cut |
| MF-09 | Major | The BUILD.md files disagree on order or method: (a) grooves and fin lead holes are cut twice, in wing step 5 and fins step 2 and again in harness steps 3–4; (b) servos go in **before** skinning (harness step 10) and **after** it (mechanisms preamble, wing step 12); (c) "No CA on XPS" (wing, pod) against CA for straws and grommets in XPS (harness step 4); (d) 4 PETG spar plugs (wing) against "C2's six spar plugs" from the 20 × 18 tube (fins step "Bought"); (e) the pod "needs first" refers to a top slot fill over \|y\| < 29 while the wing slot is cut from below and capped full span; (f) propulsion's prerequisite says the mounts are "bonded" and post-cured, but they are slip-clamped; no oven is in any tool list; (g) the transport render shows props fitted in the box while the procedure stows them in the tray | file and step cited in each item | No | G4 writes one traveler, with an order by day and by person, and deletes the duplicate steps. Rule for (b): servo leads to the JR recess before skin, servos installed after skin. Rule for (c): foam-safe CA or epoxy only | 1 day |
| MF-10 | Major | No spare spar or motor tube. The only spare tube, W03, is the GT-16 bend/torsion specimen, and a 20 mm ring is cut from it for the ring-crush test, so it is no longer a 1 000 mm unspliced spar. W04 × 2 = spar + 2 × 344 mm tubes, which leaves a 312 mm offcut, shorter than one motor tube. The spare servo and ESCs are gated (X01, X02) | `BOM.csv` W03/W04; `GROUND-TEST-PLAN.md` GT-16 step 5; `wing/parts.csv` (spar "stock length used as is") | No | Cut the crush ring from the W04 offcut; keep the W03 bend test elastic (4 kg) and re-designate W03 as the spare spar after inspection. Or buy one more W04 | $0 or +$26–31 |
| MF-11 | Major | Consumables and tooling are missing from the BOM, and the pessimistic margin over the crash reserve is $17.41. Missing: TPU filament (`GER-007`), 3M 77 spray adhesive, foam-safe CA, **100 mm** clear tape (W06 is 48 mm), 12 mm filament tape, straws, phenolic microballoons, mixing cups/gloves/IPA, blades, abrasives, 22 / 5.4 / 3 mm ball bits, 2.5 / 3.4 / 8 mm drills, insert tip, inclinometer, Z-bend pliers, pin vise, 0.1 g and 1 g scales (H1: +$33 if not lent), a 50 °C heat box, PETG in 4+ colours (BOM: one 1 kg spool). One "small kit" ($14) of epoxy, silica and microballoons covers the spar bond, 8 root fillets (about 14 cm³ each), beads, pod fillets, mechanisms, coupons and repairs | `BOM.csv` C05, W05, W06; tool rows of every BUILD.md | No | I1 adds a consumables group from the BUILD.md tool rows, prices it and re-runs the gate; buy epoxy by the quart, not the small kit | Not priced here; very likely more than the $17 margin |
| MF-12 | Major | First hover by week 4 is optimistic. The wing path alone has at least 8 serial 24 h cures: spar plugs → spar + blocks + beads → motor tubes → collars → recess fillet and pod box → handle → mechanisms tubes → horns / shoes. Then GT-06/07/08/12/13/18 run on the flight article before tethered hover. The 70–85 h figure is hands-on time only | BUILD.md cure lines; `GROUND-TEST-PLAN.md` campaign order; `params.json` schedule | No | Pre-stage everything printable and electrical before 19 Jan; run two cure chains in parallel (wing and pod); set week 5 for the first tethered hover and keep week 4 as a stretch (§5) | — |
| MF-13 | Major | Open structural decisions gate the prints on the critical path: collar height (CR-C6-37), pins and strip anchor (CR-C6-38), cheek extension (+16 g, decided by `T-C4-FIN-PROOF` on a December test article), the D5 sleeve not yet in CAD, and mount stiffness expected to fail GT-17 (1 500 vs 1 966 N·m/rad) | `STATUS.md` issues 1, 8, 9; `HANDOFF.md` H7 | **Yes** (these are FEA re-runs) | Freeze date **18 Dec**, with the coupons and fin test article built before the shop closes. Anything not frozen ships at the conservative option (22 mm collar, cheeks on) | Mass +4.4 to +20 g from a 0 g reserve |
| MF-14 | Major | Fillet mass control against CG. About 112 cm³ of root fillet (8 × 14 cm³) sits mostly aft of the CG. If the mix cures at 0.60 instead of 0.45 g/cm³ (an illustrative miss), that adds about 17 g near x 0.2 m: about 1 mm of CG shift against a 0.8 mm aft margin, and 13 g of nose lead per mm from a 0 g reserve | `fins/BUILD.md` fillet row (≤ 0.45 g/cm³, cup ≤ 9.0 g); `MASS-CG.md`; `GROUND-TEST-PLAN.md` GT-07 (13 g/mm) | Yes (A3 mass, B3 CG) | Weigh a cup from **every** batch; practise on coupons first; weigh each half-fin before and after (already step 11); hold a ballast plan | $0; skill |
| MF-15 | Major | ASA needs an enclosed printer (D-42). Jacobs' open-access list does not say any printer is enclosed. The mounts are the most-crashed printed part | `fins/BUILD.md` prints row; Jacobs labs page | Yes, if the material changes (C4 mount stiffness, E3 temperature) | Ask Jacobs, or use a teammate's enclosed printer, or the staffed Fortus. Fallback: PETG/CF-PETG mounts with C4 sign-off | $0 – service fee |
| MF-16 | Major | The box base blank does not fit one Coroplast sheet. The cross-shaped blank is 542 + 2 × 536 = 1 614 mm wide against a 48 in (1 219 mm) sheet. The box is also gated (X07, $149.72) but is needed before the first field drive | `transport/BUILD.md` step 2; `BOM.csv` T01, X07 | No | Separate wall panels joined with taped and hot-melted corner angles, or buy a third sheet; un-gate X07 or name the borrowed carton | +about $15 for one more sheet (T01 line price) |
| MF-17 | Minor | The spar slot is cut with a fence on the LE while the core rests on a curved, reflexed lower surface. Neither slot tool (22 mm ball bit, "heated U-wire on a guide rail") is owned or in the BOM | `wing/BUILD.md` step 3 | No | Keep the hot-wire lower offcut as a cradle; a router sled on rails; or ShopBot | Bit not priced |
| MF-18 | Minor | The torque-tube groove leaves 1.1 mm of foam under the upper skin | `wing/BUILD.md` step 9 | Maybe (C6 panel torsion) | Router depth stop; accept and tape a breakthrough | — |
| MF-19 | Minor | Repetitive parts with no jig: 48 pin holes, 108 cartridge sticks pre-crushed one by one | `fins/BUILD.md` step 14; `landing/BUILD.md` 4–4a | No | Printed drill guide; fence and crush block; batch the sticks from one slab | Saves several hours |
| MF-20 | Minor | The wing proof (GT-08), the station proofs and `T-C5-AIRCRAFT-DROP` load the only flight airframe before first hover, with no spare core ready | `GROUND-TEST-PLAN.md` GT-08–10 | No | Cut core 2 in week 1, the same day as core 1 | 1 h extra |
| MF-21 | Minor | The foam-board source differs (parts.csv "Dollar Tree / Adams"; BOM W02 Amazon 10-pack), and the boss slots depend on 4.8 ± 0.2 mm. Laser policy for foam board unknown | `fins/parts.csv` FIN-001; `BOM.csv` W02 | No | Buy one board brand; measure, then print the slots | — |
| MF-22 | Minor | `transport-box.png` shows props mounted in the box | render vs `transport/BUILD.md` step 9, `propulsion/BUILD.md` Field | No | Re-render, props in the tray | — |
| MF-23 | Minor | Ground-test fixtures (stand, lever frame with steel plates, whiffletree, tilt board, foot sled, CG jig) are builds in their own right, and no hour estimate covers them | `GROUND-TEST-PLAN.md` GT-01, 08, 09, 11, 15 | No | Put them in the traveler and give them an owner; build in Nov–Dec | Several person-days (reviewer est.) |

**Counts: 2 Blocker · 14 Major · 7 Minor.**

### Tolerance stack-ups a hand build will not hold without a fixture

| Feature | Spec | What drives it | Hand-build reality | Fixture |
|---|---|---|---|---|
| Spar bore | OD + 0.4 mm (0.1–0.3 mm per side) | slot tool, curved reference surface | The fit is easy to hit; the slot **depth** is not | Cradle + router sled |
| Core straightness / twist | 1 mm over span, both TEs on the bench | bond under weight | OK on a flat bench with a straight edge | Use the hot-wire offcuts as beds |
| Block y-station | ±1 mm at y ±0.320 | spar jig | OK with a jig; not drawn | Clocking jig (MF-06) |
| Block clocking / tube vertical | 1° (block) vs 0.5° (tube) | round spar, no key | Contradictory spec | Clocking jig (MF-06) |
| Motor cant | 7 ± 1° (inclinometer on the can) | print + tube + squaring by eye | ±1° is achievable; it consumes the clearance margin (MF-07) | Cant gauge |
| Motor face to collar | 7.5 ± 0.5 mm | print + spacer | OK with the spacer | Spacer block |
| Laminate thickness | 9.6 ± 0.3 mm | board brand + glue film | Measure before printing the slots | — |
| CG x | 0.0472–0.0508 m accepted band | fillets, tape, wire mass | Thin (0.8 mm aft margin) | Weigh every batch (MF-14) |

## 5. Realistic build plan (week by week)

Assumes MF-02 to MF-04 are resolved, the early order lands by early December and the December order by about
22 Dec. Build week 1 = 19 Jan 2027. "Cure" = an overnight 24 h cure. Week numbers match `params.json#schedule`.

| When | Build work | Gate at the end |
|---|---|---|
| **11 Nov – 18 Dec** (shop open) | All four students take the laser, printer, woodshop and drill-press trainings. Write the shop exporter (MF-01). Laser-cut S5010 templates; build and tune the hot-wire bow; cut 2 practice cores. Twin build and flight (D1–D3). Thrust stand, lever frame, CG jig. Print and test coupons and the fin test article; run `T-C4-FIN-PROOF`. Print the clocking jig, cant gauge and drill guides | **Design freeze 18 Dec:** collar, pins, cheek, sleeve, mount material. Traveler issued |
| **19 Dec – 18 Jan** (no Jacobs) | Home or personal printers if any: blocks, collars, pod prints, feet, pistons (2 sets). Harness cut and labelled; ESCs flashed; bus board and AS150U leads (if a safe bench exists); FC flashed, `K09L.param` loaded, SITL hours. GT-16 tube result already in by 10 Dec | All flight prints and the electrical sub-assemblies on the shelf |
| **Wk 1** (19–25 Jan) | Cut cores 1 and 2. Spar plugs (cure). Slot, pockets, grooves. Fin laminates and DXF cuts. Pod board parts; forward-stop T and tray (cure). Mounts in ASA, drilled to motors | Core 1 accepted by template gauge |
| **Wk 2** (26 Jan – 1 Feb) | Spar + blocks + beads in the clocking jig (cure). Elevons free, torque grooves. Anchors, motor tubes (cure). Recess fillet (cure). Pod walls and stop fill. Half-fin roots and fillets, weighed | Tubes vertical and parallel per the jig |
| **Wk 3** (2–8 Feb) | Collars (cure), strips, pins, braces, ESC pads. Pod into the recess (cure), handle (cure). Harness in the grooves; JR recess. Skin. Mechanisms: torque tubes (cure), horns and frame (cure). Shoes (cure). Power stack into the pod | Airframe complete; `T-D3-SLIP`, throws |
| **Wk 4** (9–15 Feb) | Avionics, calibration. GT-06 weigh, GT-07 CG, GT-18 tap, GT-12 bench, GT-13 restrained run, GT-14 range. Box built (MF-16) | Restrained run passes (stretch: tethered hover) |
| **Wk 5** (16–22 Feb) | **First tethered hover** (realistic). GT-08 wing proof only after hover data, or on core 2 | Hover log, VIBE, compassmot |
| Wk 6–7 | Free hover tuning; fixed-wing tune per D2; first transition attempt late wk 7 at the earliest | `R-SCHEDULE` transition wk 7 is a stretch |
| Wk 8–9 | Transition round trips; **crash-repair loop budgeted here** (core re-cut from stock in about 1 day per P12; fins about 24 h cure) | One clean round trip |
| Wk 10–14 (to 30 Apr) | Mission demonstrations, second crash repair, documentation | Complete by 30 Apr |

Critical path: templates and bow → core 1 → spar/block bond (jig) → motor tubes → collars → pins/braces → shoes →
bench tests → hover. The pod is a parallel chain that must join before skinning (wing step 10). Long poles: the
**design freeze** (MF-13), **Jacobs access and training** (MF-04), **the Ovonic packs from Germany** (about 14 d) and the
**Aloft carbon cart** (`ORDER-PLAN.md`).

### Make ×2 from day one

| Part | Why |
|---|---|
| Wing core (cut 2, finish 1, keep 1 bare with its slot) | Tip strikes and proof tests; the sheet already gives about 6 |
| Motor mounts `FIN-003` (8 total: 4 A + 4 B) | Crash fuse; the repo repair says "swap in a spare ASA print" |
| Collars `FIN-008` (8), through-core block `FIN-004` (3) | A broken block means a new core, so the spare must already exist |
| Half-fin laminates (4 spare, uncut fillets) | Landing on fin tips "is the recurring damage mode" (`CONFIGURATION.md`) |
| Shoes and pistons | Already planned (2 spare shoes, 8 spare pistons) |
| Elevon horns, servo frame, pod handle | Small and quick, and they break in cartwheels |
| Spar and motor tubes | MF-10: none exist now |
| Props | 4 spare are in B03; keep them |

Rebuild time after a typical cartwheel (reviewer est.): mounts and props 1 h; one half-fin 24 h of cure; a core
with blocks and tubes about 4–5 days through the same cure chain, which is why core 2 and the spare block should
exist before the first hover.

## 6. Skills risk

| Skill the design needs | Where | Risk if nobody on the team has it | Mitigation |
|---|---|---|---|
| Hot-wire cutting a 1.15 m section | wing, pod blocks, saddles, cartridges | High: LE quality sets stall (MF-05) | 2–3 practice cores in Nov–Dec |
| Epoxy / microballoon fillet work with mass control | fins, wing beads, pod | High: CG and the 0 g reserve (MF-14) | Coupons, cup weighing |
| High-current soldering, LiPo re-termination | power, harness | High (safety) | Electronics Lab staff check; H3 procedure |
| ArduPilot tailsitter set-up and tuning | flight software | High (`STATUS.md` issue 10: never run) | SITL ≥ 10 h; twin |
| FDM tuning in PETG/ASA (fits ≤ 0.3 mm) | all prints | Medium | Print the test-fit set first |
| Fusion/Python CAD export | MF-01 | Medium | One owner, start this week |

## 7. Questions for the team

1. Who pays the Maker Pass ($125 per student per semester), and is the capstone a Jacobs-affiliated class with comped passes?
2. Does anyone own an enclosed printer (ASA), or a printer usable at home over the winter closure?
3. Will Jacobs allow (a) foam board in the Universal lasers, (b) XPS on the ShopBot, (c) access during intersession?
4. Has any of the four ever hot-wired a wing core or laid microballoon fillets? If not, who practises in November?
5. Can the design freeze (collar, pins, cheek, sleeve, mount material) happen by 18 Dec? If not, which conservative option do we build?
6. Is the W03 bend test elastic only, so that W03 can serve as the spare spar? Or do we buy one more tube?
7. Who owns the shop exporter (STL, DXF, templates, jigs), and who writes the single traveler?
8. Where do overnight cures happen, and is there a room at ≥ 18 °C and a 50 °C heat box for the mount post-cure?
9. Which two cars, and will the 1 614 mm box blank be redesigned as panels?
10. Is first hover in week 4 a hard commitment? If yes, what gets cut from the build-end test cards before it?

## Sources

- [Jacobs Institute: Labs and equipment](https://jacobsinstitute.berkeley.edu/our-spaces-at-a-glance/labs-and-equipment/)
- [Jacobs Institute: Maker Pass](https://jacobsinstitute.berkeley.edu/our-space/makerpass/)
- [Jacobs Institute: Get Maker Pass (price, fall access end, training dates)](https://jacobsinstitute.berkeley.edu/making-at-jacobs/get-maker-pass/)
- Repo: `redesign/README.md`, `STATUS.md`, `HANDOFF.md`, `CONFIGURATION.md`, `subsystems/*/BUILD.md` and
  `parts.csv`, `team/I1/BOM.csv`, `ORDER-PLAN.md`, `team/H1/GROUND-TEST-PLAN.md`, `JACOBS-LOAN-REQUEST.md`,
  `params/params.json#schedule`, `fusion/README.md`, `showcase/tools/export_stl.py`, `showcase/renders/*.png`.
