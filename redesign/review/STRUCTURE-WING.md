# K09-L structure review: connections and wing construction

Reviewer: builder's review ("how would we actually build this?"), 2026-11-11, branch `redesign/v1`, read-only.
Scope: spar-to-core and spar-to-fin load path, fin-to-wing joint and the through-core blocks, pod-to-wing bond,
foot-to-fin attachment, tape skin, bond types and surface prep. CAD geometry was checked against the BUILD steps
using bounding boxes and vertices from `redesign/site/assets/k09l.glb`, read in Blender. The script and its output
are in the session scratchpad, not in the repo.

## Verdict

The materials are right for students to build: an XPS core, a CF spar bonded in a microballoon bed, packing-tape
skin and printed hard points. The Jacobs tools are enough for every joint. The documents, though, describe an
assembly nobody has rehearsed. In three places the CAD and the BUILD steps disagree badly enough to stop the build:

- The through-core block's strap eyes overhang the pocket, so the block cannot be inserted.
- D5-R6 and D3's tip disagree on where the fin tip is, and the CAD shoe clashes with the fin board.
- The pod handle bridge is meant to bond to a "slot fill" that the wing does not have.

Neither the jigs that set wing straightness and tube squareness nor any build fixture are designed, and the G team
folder does not exist. Once the spar is bonded, everything inboard of |y| 0.5 m is one bonded part: core, blocks,
tubes, half-fins, braces and pod. That part takes about eight 24 h cures in series. A typical student crash means a
new airframe, which only fits the Jan–Feb window if a second core kit is built in parallel. The weakest designed links
under a sideways landing are bonded fin-top joints that the team's own checks already rate below 1:

| Joint | Rating | Source |
|---|---|---|
| Strip tail | est. 0.67–0.74 | `team/C6/JOINTS.md:126` |
| Collar | 0.77 | `team/C6/JOINTS.md:125` |
| Root fillet | 0.81 | `team/C6/JOINTS.md:132` |
| Pins | est. 0.93 | `team/C6/JOINTS.md:128` |

None of these joints is a fuse, and each needs a 24 h cure to repair. Before spending more on CFD or FEA, do three
things:

1. Freeze the fin-tip and shoe geometry.
2. Put the grooves and slot seam into C2's wing model.
3. Build one fin-station test article in December. It doubles as the build rehearsal.

## Findings

| ID | Sev. | Component | Problem | Evidence | Changes CFD/FEA inputs? | Recommended fix | Cost / time impact |
|---|---|---|---|---|---|---|---|
| SW-01 | Major | Through-core block `FIN-004` ↔ block pocket | **The block cannot be inserted as BUILD describes.** The CAD block reaches y 0.3446 m: the upper strap eye at z 0.0202–0.0302 and the lower eye at z −0.018…−0.008, both at x 0.042–0.048. The pocket ends at \|y\| 0.3382 and its chamfer at 0.3412. One eye sits above the upper skin and one below the lower skin, both outboard of the pocket wall. Threaded on the spar, the block can go neither up from below nor down from above. | glb `FIN-004-R` vertices; `subsystems/wing/SPEC.md:46-47`; `subsystems/fins/BUILD.md:41-42` ("strap eyes outboard"); `subsystems/wing/BUILD.md:44-47` | FEA: minor (C2 block outline). CFD: yes, the eyes and bosses stand 7.6 mm proud at x 0.031–0.074. | Print the eyes as separate clips bonded on after the spar bond, or move them inside the pocket footprint. Ground-run ties could also go round the tube instead. Do not notch the core. | CAD edit plus one reprint; $0 |
| SW-02 | **Blocker** | Fin tip ↔ foot shoe `GER-001` | **The fin-tip step and the shoe disagree.** Landing BUILD R6 needs the step and strip ends at x 0.2616 (58.4 mm). Fins BUILD, fins params and the CAD strips all end at 0.2746. The CAD shoe starts at x 0.2538 and fills z 0.1936–0.2162 where the CAD fin board still rises to z 0.210 (x 0.255–0.2746), so the two solids overlap. The last pins (to x 0.264) were placed to stop before cheeks at 0.2666 (R5), which R6 moves forward over them. The landing SPEC and its bond claim still describe the R5 sleeve (21.1 × 17.1 mm, 1 350 mm², RF 1.57). CR-D5-31 does not appear in the CHANGE-LOG. | `subsystems/landing/BUILD.md:13-21,27`; `subsystems/fins/BUILD.md:23,66-67,85-87`; `subsystems/fins/params.json:89,103`; `subsystems/landing/SPEC.md:15,36`; glb `FIN-011-*` (x max 0.2746), `GER-001-UR`, `FIN-001-UR` | **Yes.** C4 fin-station model (tip, strip length, cheek clamp, which D-70 credits with 53 % of the side-load moment); C6 shoe bond area; D5 FEA | A1 decides one tip; D3 and D5 redraw to it. Then re-derive the shoe bond area and pin row, and only then run C4's re-solve (CR-C6-38). Print no shoes or collars and cut no fin tips before this. | 1–2 CAD days (est.); blocks the fin and foot prints |
| SW-03 | Major | Foot → fin load path (crash philosophy) | **The foot side-load path has no fuse.** D-23 makes the motor mounts the fuse for prop strikes. A sideways-drifting landing (D-65: 39.3 N limit / 59.0 N ult per foot) instead runs pad → shoe → strips → collar tail → tube. The weakest links on that path are bonded joints already below RF 1 (strip tail est. 0.67–0.74, collar 0.77, pins est. 0.93; the root fillet at 0.81 is fail-safe only). The first thing to break in a skidding landing is therefore a 24 h + post-cure repair at the fin top, not a 3-minute insert swap. | `params/CHANGE-LOG.md` D-23, D-65; `team/C6/JOINTS.md:125-132`; `subsystems/fins/SPEC.md:39,41`; `subsystems/landing/SPEC.md:37` (rim SF 1.05 on R5) | **Yes.** C1/C4/C6 side-load case: cap it at a defined foot breakaway load | Make the foot the side-load fuse: the piston snap or rim lets go at a load set below the fin chain's capacity, with a tethered insert. Size C4/C6 to that capped load instead of chasing collar and tail sizes. | D5 redesign (est. 1–2 days); can save the +4.4 g collar growth (HANDOFF H7) |
| SW-04 | Major | Strip-tail joint in the station collar `FIN-008` | **The joint is hard to make and hard to inspect, and the proposed fixes make it harder.** Two 1 mm CF strips go into FDM slots 40 mm deep while the collar is slid axially down the tube. The slot walls scrape the epoxy off on entry, which is why BUILD needs needle injection and a 20 N pull. C6's estimate wants 53 mm of embedment and a 22 mm ring, which means even deeper blind slots. All PETG bores (collar, block) rely on epoxy adhesion to PETG, and that coupon has not been run. The pins are drilled after the collar is fitted, on a standing fin. | `subsystems/fins/BUILD.md:68-87`; `team/C6/JOINTS.md:125-126,177`; `HANDOFF.md` H7 | **Yes.** C4/C6 joint model (tail embedment, collar bond allowable) | Coupon a lashed alternative alongside the tail: strip ends wrapped to the tube with epoxy-wet Kevlar or CF tow, and a printed collar used only as a former. Add 0.3 mm circumferential grooves to the PETG bores so the joint keys mechanically. Fit the strips and drill the pins on the flat laminate on the bench before the half-fin goes on the wing. | Tow ~$10 (est.); 1 coupon day; saves standing-fin drilling |
| SW-05 | Major | Wing core, band \|y\| 0.23–0.34 m (fin station) | **C2's FEA leaves out cuts that sit on the hot spot.** The ESC grooves are cut into both surfaces at x 54–64 mm, 2.4–3.1 mm deep, over \|y\| 0.086–0.296. They end 6 mm inboard of the block pocket, against the bead chamfer at 0.2989. C2's peak foam stress is at that pocket's inboard-front-lower corner. Behind the grooves is a 3 mm web to the spar slot, which is cut from below and re-capped over \|y\| ≤ 0.5 and also not modelled. The same 110 mm band holds the anchor pockets, the servo pocket from below, the JR recess (5 mm deep, 4.2 mm wall), the servo-groove branch, the torque-tube groove end and the elevon end cuts. A chordwise crack here is the likely wing damage in a cartwheel, and it is not field-repairable. | `subsystems/wing/SPEC.md:41-53`; `team/C2/SIMULATION-REPORT.md:28,31` (geometry list, "bond lines not modelled"); no "groove" in `team/C2/fea/*.py`; `params/CHANGE-LOG.md` D-68 (corner MS −0.26) | **Yes.** C2 geometry: grooves, slot cap seam, JR recess | Add the grooves and the slot seam (as a no-tension line) to C2's model before the D-68 re-run (CR-D1-14). Cheaper still: stop the lower ESC grooves well short of the bead chamfer with a rounded end, or run the leads in the upper grooves only. | C2 re-mesh (est. 1 day); D1/F2 routing tweak |
| SW-06 | Major | Spar bond and later assembly: fixtures | **No fixture holds the wing at the steps that freeze straightness and twist.** Wing step 8 says "weight the core flat on the bench", but the blocks are already in and stick out 7.6 mm above (z 0.0304 vs core 0.0228) and 9.3 mm below (−0.018 vs −0.0087). After tube install (z ±0.172 m) the wing can never lie on a bench again, yet half-fins, fillets on both faces, strips, collars, pins, braces, pod, skin and mechanisms all come after. The "spar jig" and "G1 jig" are cited but not designed; there is no `team/G*` folder. | `subsystems/wing/BUILD.md:12,46-51`; `subsystems/fins/BUILD.md:42,49-51`; glb `FIN-004-R`, `WNG-001`, `FIN-002-R` bounding boxes; `HANDOFF.md` §5 (G1–G4 unnamed) | No | Keep both hot-wire beds and cut reliefs for the bosses and eyes. Bond the spar inverted in the upper bed, weighted, LE on a straight edge. Laser-cut a ply block jig (two 22 mm pins through both tube bores, y ±320 mm, square). Build a stand that holds the wing by LE and TE saddles at y 0 and ±0.45 m (clear of the CG-jig patch), and that can be flipped. | Ply + hardware ~$30 (est.); 1–2 shop days in December |
| SW-07 | Minor | Spar slot (wing BUILD 3) | The cutter is undefined and contradicts the cap: a router with a ball bit turns the strip to chips, yet step 8 re-bonds "the trimmed slot strip". A 1 m long, 27 mm deep slot with a round top, made by a heated U-wire on a rail, is a custom tool nobody owns. A fence on a sanded, curved LE sets x poorly. With the slot cut, the core is hinged on 4–5 mm of foam and cracks if lifted. | `subsystems/wing/BUILD.md:12,23-25,46-48` | No | Cut the slot with the core in its lower bed and the fence on the bed's flat edge. Accept a router and make a fresh cap strip from offcut. Never lift the slotted core out of its bed. | 0.5 day (est.) |
| SW-08 | Minor | Block ↔ spar bond `E-FIN-49/50` | Two adhesives for one joint. Fins step 7 bonds the blocks to the spar with 30-min structural epoxy in a jig. Wing step 8 sets them in the single microballoon pour. A microballoon mix cannot enter the 0.1–0.3 mm bore gap, and C6's RF 4.64 assumes a 2.0 MPa structural bond. Sliding a buttered block 180 mm along the tube also smears epoxy over the spar bond zone. (Separately, fins BUILD names "C2's six spar plugs" in 20 × 18 CF tube, while the wing uses four PETG plugs.) | `subsystems/fins/BUILD.md:12,41-45`; `subsystems/wing/BUILD.md:46-49`; `subsystems/wing/SPEC.md:62`; `team/C6/JOINTS.md:123` | No (C6 allowable basis only) | Bond the blocks to the spar first in the SW-06 jig with silica-thickened epoxy, applied at the final station with tape dams. Cure, then do the core pour. Fix the plug wording. | None |
| SW-09 | Minor | Tape skin order (wing 11, fins 17) | The skin goes on last, around 4 half-fins with fillets, 4 braces, 4 anchors and the bosses. Every spanwise strip breaks into pieces. The "continuous" LE strip has to be slit round the boss, which starts at x 0.0314, inside the 32 mm seam-free zone. The 24 mm tab-edge tape (12 mm per face) lands on the toe of the 13 mm aft root fillet, which is 2.2 mm off the tab edge. | `subsystems/wing/BUILD.md:66-79`; `subsystems/fins/BUILD.md:59-61,94-95`; glb `FIN-004-R` (x ≥ 0.0314 above the skin) | CFD: minor (LE seam at the fin stations) | Skin the wing after the spar/block bond and elevon cuts but before the tubes and half-fins. Then remove the tape with a hot knife only over the root, anchor and pod footprints. Lay the tab-edge tape before the root fillets. | Saves ~0.5 day (est.) |
| SW-10 | Minor | Pod handle bridge `POD-007` ↔ wing | Pod BUILD step 11, the pod interfaces, params and `pod.py` bond the foot bridge onto "the slot fill over \|y\| < 29". D1 answered that the slot is cut from below, so the bridge sits on bare foam with about 4 mm of cover over the spar. Since D-69 the aft-stop strut ends on that bridge (hover and landing pack load), and C3 modelled it as a "spar bridge". | `subsystems/pod/BUILD.md:15,32`; `subsystems/pod/interfaces.json:109`; `subsystems/pod/fusion/pod.py:472`; `team/D1/CHANGE-REQUESTS.md:15` (CR-D1-07); `team/C3/SIMULATION-REPORT.md:13,80` | **Yes.** C3 boundary condition: the bridge is carried by the two feet saddles only | Fix the pod docs. C3 confirms the strut load reaches the spar through the bridge in bending to the saddles, not through foam. | Docs + 1 C3 re-run |
| SW-11 | Major | Whole airframe: repairability and schedule | After the spar bond, the core, spar, blocks, tubes, half-fins, anchors, braces and pod are one bonded part. The only documented wing repair is the tip re-cut outboard of \|y\| 0.5. The fins repair table has no entry for the block, the tube or a core crack at the station. On the critical path the core goes through about eight 24 h cures in series: spar bond, tubes, strips, collars, recess fillet, pod box, handle, shoes. That leaves no room for a crash rebuild inside January to early February. | `subsystems/wing/BUILD.md:91-92`; `subsystems/fins/BUILD.md:111-120`; cure steps in wing/fins/pod/landing BUILD; `HANDOFF.md` §5 (one crash-repair loop) | No | Hot-wire and slot two cores and bond two spar+block sets in the same sessions; keep #2 un-finned. Structure parts per airframe are about $125 from the wing and fins `parts.csv` unit costs. Add repair cards for a station crack (inject, tape doubler, re-proof) and for the pod nose. | ~$125 + ~2 shop days (est.) |
| SW-12 | Major | Paper-faced foam board joints (root fillets, shoe legs, strips, laminate) | The board joints load the paper face in peel, but there is no peel allowable and no coupon for it. A side load peels the 7 mm shoe legs and the fillet toe off the board's paper face, and the failure is the paper parting from the foam core. C6 carries a 0.10 MPa shear and a 0.05 MPa flat-wise value, and `T-C6-BOARD-LAP` tests PETG tabs on a single board. The two boards are laminated with 3M 77 contact adhesive, whose glue line is the laminate's mid-plane shear plane. C4 models the laminate as perfectly bonded. | `team/C6/JOINTS.md:134,147,178`; `subsystems/fins/BUILD.md:20-21`; `team/C4/SIMULATION-REPORT.md:29,142`; `subsystems/landing/BUILD.md:55-58` | **Yes.** C4 laminate interface; C6 peel allowable for the shoe and fillet | Laminate the boards with thin, rolled laminating epoxy, or add a short-beam test of the 3M 77 laminate. Add a peel coupon: a fillet or shoe leg on the laminate, pulled out of plane. Wrap the shoe legs and fillet toes with one layer of light glass or tape. | Coupons ~0.5 day; a few g |
| SW-13 | Minor | Collar tongue fit | The tongue and the slot walls are drawn for a 9.6 mm laminate, but BUILD accepts 9.6 ± 0.3 mm. FDM slots near 1 mm wide and 40 mm deep do not print to tolerance. HANDOFF holds the collar print for H7. | `subsystems/fins/BUILD.md:26,32-34`; `subsystems/fins/SPEC.md:39` | No | Laminate first, measure, then set the tongue and slot widths in params before printing. Leave slot clearance for thickened epoxy. | None |
| SW-14 | Minor | Post-cure, motor-zone bonds | "Parts within 50 mm of a motor + 4 h at 50 °C" applies to collars bonded on a complete 1.15 m airframe with tape skin. No oven is named. | `subsystems/fins/BUILD.md:8`; `team/C6/JOINTS.md` bonded-joints header | No | Do the post-cure in a local heat tent (box + lamp, thermocouple on the collar, XPS and tape kept cool), or bond the collars on the bench sub-assembly where possible (SW-04). | ~$10 (est.) |
| SW-15 | Minor | Pod spar ties `E-POD-09` | The 7.6 mm ties are laid under the spar before the microballoon spar bond, so the slot fill glues them in. They cannot be replaced, and epoxy can reach the free ends. | `subsystems/wing/BUILD.md:44-45`; `subsystems/pod/BUILD.md:15` | No | Sleeve each tie in a straw or heat-shrink and wax it before the pour; tape the free ends up. | None |
| SW-16 | Minor | TE and elevons | The templates call for a 0.6 mm TE in hot-wired XPS. As cut and sanded it will be thicker and uneven, and BUILD's check is "TE ≥ 0.6 mm" with no upper limit. | `subsystems/wing/BUILD.md:12,22` | **CFD: yes** (TE thickness and base drag) | Cut a 300 mm test section in December, measure the real TE, and feed that number to B1/B2. | Part of the test article |
| SW-17 | Minor | Elevon torque-tube groove | The groove leaves 1.1 mm of foam under the hinge face, and it is routed after the panel has been cut free (a loose 70 mm panel). | `subsystems/wing/BUILD.md:52-60`; `subsystems/wing/SPEC.md:27` | No | Route the groove with a depth stop while the core is still whole in its bed, then cut the panels free. | None |
| SW-18 | Minor | Document consistency, fin joint chain | The collar height is 15 mm in CAD/SPEC, 13 mm in D-70 and 22 mm in HANDOFF H7. A builder cannot tell which one to print. | `subsystems/fins/SPEC.md:39`; `params/CHANGE-LOG.md` D-70; `HANDOFF.md` H7 | Yes (C6 collar RF) | One value in params, decided at H7, after SW-03. | None |

Counts: 1 Blocker, 7 Major, 10 Minor.

## What breaks first in a typical student crash

Ordered by likelihood. The ratings come from the team's own checks.

1. **Tip-over at take-off or landing in wind.** Props break and the mounts slip, as designed (D-23). This is
   field-fixable.
2. **Landing with sideways drift.** The foot side load goes into the fin top. By the RFs above, the strip tail,
   collar or pins fail before anything that unclips (SW-03). The shoe can also peel off the paper face (SW-12). Each
   is a 24 h repair.
3. **Failed transition from 5–20 m.** The pod nose crushes; the crush block is designed for this. The half-fins
   crease. The core cracks chordwise in the fin-station band (SW-05), and the block or its beads can let go. That is a
   new airframe (SW-11).

## Build sequence as I'd actually do it

1. **December, before any flight part.**
   - Laser-cut the S5010 templates and the ply jigs: block-on-spar jig, build stand, 45° and pin drill guides
     (SW-06).
   - Run the coupons: PETG lap, board peel, laminate short-beam, a tow-lashed strip versus the collar tail (SW-04,
     SW-12).
   - Build one **fin-station test article**: a 300 mm wing stub with block, tube, one half-fin and a foot. It
     rehearses steps 2–9 and doubles as `T-C4-BLOCK-PROOF`/`T-C4-FIN-PROOF`.
2. **Hot-wire two cores** and keep all four beds. Sand the LE. Measure the TE.
3. **Cut the pockets, grooves and recess, and the slot from below**, all with the core in its lower bed. Route the
   torque-tube grooves now (SW-17).
4. **Push the plugs into both spars.** Bond the blocks to each spar in the jig with structural epoxy and cure
   (SW-08). The strap eyes are not on the block yet (SW-01).
5. **Bond spar + blocks into the core**, inverted in the relieved upper bed: microballoon bed, cap strip, lip beads,
   pod ties sleeved. Weight the core with the LE on a straight edge and cure. Check twist on both cores.
6. **Cut the elevons free.** Pocket and bond the anchors. Lay the recess-step fillet.
7. **Skin the whole wing** with the LE strip, doublers and tab-edge tape. Hot-knife the tape off the root, anchor and
   pod footprints (SW-09).
8. **Move the wing onto the build stand.** Bond the pod box in the recess, then the handle and brackets in one
   session. The pod box itself is built on the bench in parallel.
9. **On the bench, in parallel with step 8**: laminate the half-fins and measure them; cut the final tip (SW-02);
   bond the strips and pins; print the collars to the measured laminate.
10. **On the stand**: tubes in, squared with the jig.
    - Upper half-fins with root fillets, then flip the wing, then the lower ones.
    - Collars or tow lashing, braces, ESC pads.
    - Post-cure tent (SW-14).
11. **Shoes and inserts, then hand over** to mechanisms, harness and propulsion. Run the slip set (T-D3-SLIP).
12. **Weigh, balance and proof.** Core #2 stays as a spar-bonded spare with no fins.

## Questions for the team

1. Who owns tooling? G1–G4 have no folder in `team/`, and the "spar jig" and "G1 jig" are undesigned. Is there a
   hot-wire bow of at least 1.25 m at Jacobs, or does line X11 need buying?
2. Does Jacobs allow paper-faced foam board in the laser cutter? Laser-cut outlines, Ø 8 holes and slots would beat
   knife-cutting through 9.6 mm.
3. Which fin tip is real: D3/D-54 (step at x 0.2746) or D5-R6 (x 0.2616, CR-D5-31)? Will C4's CR-C6-38 re-solve use
   it?
4. Should the foot be the side-load fuse? If so, at what breakaway load, and who sizes it (D5 with C1/C4)?
5. Do the strap eyes have to be on the block, or can the ground-run ties go round the tube or boss?
6. Did B1's and B4's SU2 geometry include the block bosses and eyes, the brace anchors (~8 mm proud of both skins)
   and the pod handle?
7. Are there `T-C6-LAP-PETG` results yet? Every PETG-to-CF bond (bores, collar, anchors, saddles) depends on them.
8. Is ~$125 plus two shop days approved for a second spar-bonded core (SW-11)?
9. Will the fin-station test article be built and broken in December, before the January build starts?
