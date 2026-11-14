# Servos, linkages and control surfaces: "how would we actually build this?" review

Reviewer: RC-builder pass on branch `redesign/v1`, 2026-11-11. Scope: `MEC-*` (D6-R2), the elevon panels in `WNG-011/012`
(D1-R2), the servo harness run (F2), the elevon outputs in `K09L.param` (F4-R5), and the B2/B3/C6/D3 claims they rest on.
Nothing was built or bench-tested for this review. Numbers I worked out myself are marked **(my est.)**. All other numbers
are quoted from the repo or the maker's datasheet.

## Verdict

This linkage can be built. The geometry is conventional and well chosen: an external 2-56 pushrod, both arm and horn
square to the rod at neutral, and a 0.61 arm/horn ratio that halves the torque the servo needs. The servo is a real,
stock part. The CML data sheet for the Savox SH-0255MG+ gives 3.9 kg·cm at 6.0 V, 22.8 × 12 × 29.4 mm, 16 g, and
90° operating travel at 1000–2000 µs, so ±45° at the arm and ±25° at the surface is reachable. Hinge moment against
servo torque is not the problem either: the margin is thin only at VD with full deflection, and the flight envelope
already prevents that case. Hover is not a sizing case. B3 puts the elevons outside the prop wash, so they carry almost
no hover load. That also means the brief's "elevons used in hover" claim needs checking (SC-06). The real risks are
build and field ones the analysis does not show:
- **Hinges.** Each panel hangs on a single strip of packing tape on the upper skin.
- **Bridge rod.** It is bonded rigidly at both ends, across two separate tape hinges, through a notch cut into a fin
  root that already fails its fillet allowable.
- **Field swap.** A stripped servo cannot be changed at the field. Its lead is shortened and re-crimped *after* it has
  been threaded up a 4 mm straw.

I found no Blocker. Fix the Majors before the first panel is taped. Three of them change FEA or CFD inputs: the fin-root
notch, the as-built hinge gap, and panel twist.

## Findings

| ID | Severity | Component | Problem | Evidence | Changes CFD/FEA inputs? | Recommended fix | Cost / time |
|---|---|---|---|---|---|---|---|
| SC-01 | Major | Servo lead, `MEC-001`, D1 lead hole, F2 JR recess | **A stripped servo cannot be swapped at the field as designed.** The servo lead is cut to 40 mm, passed up a 4 mm straw, *then* given a JR male. A JR housing (about 2.5 × 7.6 mm) does not pass a 4 mm straw, so the old lead must be cut and the new one crimped at the field. The arm screw points along y and cannot be reached inside the pocket (CR-D6-10), so the arm must also be fitted and centred on the bench. | `harness/SPEC.md` l.50 ("servo's own lead (cut to 40 mm, re-terminated) → D1 lead hole … (4 mm straw)"); CR-F2-15; `wing/SPEC.md` cut table (lead hole 4 mm square) vs `wing/BUILD.md` step 4 (drill 5 mm) | No | Best: make the lead hole an 8 × 4 mm slot (x 0.173–0.181), so a housed JR plug passes. It sits inside the 4.2 mm foam wall to the JR recess, so ask D1/C2. Cheap alternative: keep spare servos ready with the lead cut to 40 mm, pins crimped and **no housing**. In the field, feed the pins through one at a time and snap them into a housing. Write this into BUILD as a field procedure, and carry a pin tool and 2 housings in the kit. Settle on one lead-hole size, 4 or 5 mm. | $0–5; 30 min of design; field swap then about 10 min instead of a crimp job |
| SC-02 | Major | Hinge, `MEC-010` | **Each panel hangs on one 25 mm strip of BOPP packing tape on the upper skin and nothing else.** Packing-tape adhesive creeps when warm and peels when the panel leading edge is pushed up: lift on the elevon, or the panel loading the tape while the aircraft stands on its tail. There is no lower hinge, no hinge pins and no hinge test in the bench plan (T-D6-SLOP checks free play, not peel). A peeled hinge on one panel of a one-servo pair can't be seen from the ground and gives asymmetric roll. | `mechanisms/SPEC.md` parts (`MEC-010` 25 mm strip, upper skin); `mechanisms/BUILD.md` step 4; datasheet operating temperature for the servo tops out at 50 °C, and the tape has no rating at all in the repo | Yes (CFD: as-built gap. The upper surface is sealed and the lower surface has an open bevel, 1.07 mm at +25° and 8.93 mm at −25° per `CL-D1-HINGE-CLEAR-*`. Model that, not a sealed or gapless surface.) | Use Blenderm or 3M filament-reinforced tape, not packing tape. Make it a two-sided hinge: a full-length top strip at neutral, plus a lower strip laid with the panel at full TE-up, which closes into a figure-8 hinge. Add a peel check: 3.5 N at the TE (the BUILD step 12 load) held for 10 min at about 40 °C. Add it to pre-flight as a "tug test". | About $10 tape, +1 g, 20 min per side |
| SC-03 | Major | Bridge rod `MEC-005` in `MEC-004/006` | **The rod is bonded rigidly in both horns across two independent tape hinges.** A tape hinge has no fixed axis, and the two hinge lines will not be exactly co-linear. A rigid rod 16.5 mm below the axes then preloads both hinges and both horn bonds through the whole stroke. For scale **(my est.)**: a 0.5 mm offset between the two axes at 25° gives about 0.2 mm of mismatch. The 47 mm free rod (67 mm minus 2 × 10 mm bonded; 1/8 in, E 110 GPa, fixed-fixed) then pushes back with roughly 10 N, against about 7 N of working load at VA (0.122 N·m / 16.5 mm). Repair is also a problem: after a wingtip strike you cannot remove the outboard panel without cutting the rod, because the rod is bonded on both sides of a notch in a bonded fin. | `mechanisms/SPEC.md` (`E-MEC-19…22` "rod bonded 10 mm in each boss"); `mec.horn.bridge_r_m` 0.0165; `mec.link.e_pa` 110 GPa; BUILD step 12 loads | Yes (FEA: horn-bond and hinge loads need a misalignment preload case; D6's lag/effectiveness model assumes a perfect rod) | Bond the rod in the **inboard** boss only. Make the outboard boss a sliding fit: a short 1/8 in ID brass tube bonded in the boss, or ream the boss to 3.25 mm, then slip a wheel collar or a dab of CA on the rod outboard of it. Motion still transfers (rod-normal), and the rod can float axially and cock slightly. To change a panel, pull the rod out sideways. Re-check free play (≤ 1°) afterwards. | $2; 15 min; no mass change |
| SC-04 | Major | Fin notch for the rod (`FIN-001-LR/LL`) | **The bridge rod passes through a 24 × 12 mm notch in the lower half-fin root, with the root fillet stopped over x 0.2376–0.2616.** That is the aft root, which the landing feet load (feet at the fin TE tips, x 0.368). The same fillet already fails C6's allowable (RF 0.81, CR-D3-35). Neither the C4 fin model nor the D3 root check shows the notch as a cut-out. C4 only notes "lower root free over the link slot". | `fins/SPEC.md` l.41 (`CL-D3-ROOT-FILLET-ALLOW` FAIL); CR-D3-25/31; CR-D6-04; `team/C4/fin_structures_d3.py` l.39 | **Yes (FEA: lower fin root must include the notch and the fillet gap, under the D-65 side load and the 1.5 m/s landing)** | (a) Have C4 run the root with the notch before anything is cut. (b) If it fails, add a CF or glass patch round the notch on both faces. (c) Or drop the rod altogether: give each panel its own SH-0255MG+ and Y-lead the two servos on each side to output 5 or 6. That removes the notch, the rod over-constraint (SC-03) and the 220 Hz rod mode (SC-11), at about +32 g and +$84 against the 9 g of headroom in the 80 g allocation. | (a) analysis only; (b) about 3 g, 1 h; (c) about +32 g, +$84, +2 frames/covers |
| SC-05 | Minor | Servo torque margin | **The torque margin is quoted at the 6.0 V rating, but the harness delivers 5.74 V at stall.** Interpolating the datasheet linearly gives about 3.73 kg·cm at 5.74 V **(my est.)** against the 3.49 needed: +7 %, not +11 %. The documents also disagree with each other. D-50 still says "servo stays 3.93 kgf·cm" (the retired 1:1 number). B2 CR-B2-19 says 4.8 V fails by 13 %; D6 says it passes by 36 % (that figure is on the F4 envelope basis). The VD case is held only by the flight envelope. At B1's capped VH, VD would be 32.1 m/s, which needs about 4.86 kg·cm **(my est., 3.49 × (32.1/27.2)²)**. In practice the servo then just blows back; nothing breaks. | `CL-D6-SERVO-TORQUE-REQ` 3.49; `CL-F2-SERVO-V` 5.73–5.74 V; `params/CHANGE-LOG.md` D-50; B2 CR-B2-19 vs D6 SUMMARY | No (hinge cases unchanged) | Quote the margin at 5.74 V. Fix the D-50 text. Run T-B2-HINGE on a real panel with tape friction. Accept blowback at VD and say so in the S&C note. | Docs only; bench test already planned |
| SC-06 | Major | Hover use of the elevons, F4 / B3 / B4 | **The brief says the elevons work in hover; the analysis says they can't.** B3 places the elevons 46 mm outside the contracted hover wash ("no hover authority"), and B4 CR-B4-06e agrees. `K09L.param` is a non-vectored tailsitter with `Q_TAILSIT_GSCMSK 1`, so ArduPilot will (to be confirmed in SITL) still drive the surfaces in Q modes. In hover they do nothing except wear the servos and pass gyro or D-term noise into them. In the back-transition flare (8–11 m/s, 30°/s) they suddenly have authority under copter-tuned, throttle-scaled gains. For servo sizing, hover is **not** a load case: a broadside 8.4 m/s wind on one side's two panels (0.031 m², Cn about 1.2) gives about 0.06 N·m against the 0.44 N·m design point **(my est.)**. | `team/B3/S-AND-C.md` l.208 (`CL-B3-ELEVON-WASH-GAP`); `K09L.param` l.23 and l.171; `Q_WVANE_LAND` 8.4 m/s note | Yes (CFD: no hover wash-on-elevon case is needed, and the team should stop expecting one. Back-transition CFD or S&C should use the elevon deflections the copter controller actually commands.) | Decide the intent in writing. If the elevons are not meant to act in hover, confirm in SITL what they do in QHOVER and QLAND and in the back-transition, and log servo current in the first hover. Keep the `Q_TAILSIT_GSCMIN/GSCMAX` defaults unless SITL shows the flare saturating. | SITL half-day; no hardware |
| SC-07 | Minor | Pushrod at the arm, `MEC-002/003` | **The Z-bend wire won't go into the specified hole.** A 2-56 rod is 0.072 in (1.83 mm; `mec.pushrod.d_m` 0.00183), but BUILD step 6 and edge `E-MEC-07` drill the arm to 1.6 mm, and the free-play budget assumes 0.05 mm of play there. A new 1.85 mm hole at 15.6 mm in the supplied arm may also break into an existing hole next to it, adding slop. | `mechanisms/params.json` `pushrod.d_m`, `pushrod.hole_play_mm`; BUILD step 6 | No | Drill #49 (1.85 mm) **only after** checking where the arm's own holes are. Otherwise use the nearest existing arm hole and re-solve the horn radius in `mech_calcs.py`, or use an aluminium 21T arm. Keep the Z-bend: it is the lowest-slop joint at the arm. | $0–6; 15 min |
| SC-08 | Minor | Throw and adjustment | **Throw is fine, but there is only one setting.** The datasheet gives 90° at 1000–2000 µs (±45°) and about 145° at 800–2200 µs, so ±25° is reachable even with the 1 % margin. But the horn has one clevis hole and the arm one drilled hole, so the only adjustment is in software. A 21T spline moves in 17° steps, so the BUILD check "arm 90° ±2°" cannot be met on the spline alone. SERVO_TRIM takes up the rest and eats the thin TE-up end. | CML SH-0255MG+ data sheet; `CL-D6-THROW-NEED` 44.7°; BUILD step 6; CR-F4-20 | No | Print the horn with three clevis holes (23.5 / 25.5 / 27.5 mm). Let F4 use 950–2050 µs if T-D6-THROW needs it. Centre on the bench by spline tooth first, then by clevis turns, and use SERVO_TRIM last. | $0; reprint |
| SC-09 | Minor | Servo dimensions vs frame and pocket | **The ear span, ear thickness, ear height and shaft position are D6 guesses.** The datasheet drawing lists 32.4 / 32.3, 28.4, 20.82, 16.8, 6, 12, 22.8 and 29.4 mm. The 17.0 mm ear-plane height in `mec.servo.ear_y_from_base_m` is not among them. If the ear plane really sits about 20.8 mm from the base, the end-wall slots are about 4 mm off and the servo will not drop in. The maker's lead is 250 ± 5 mm, not the 150 mm in D6's note (F2 already uses about 0.25 m). The datasheet lists 2 ball bearings, not 1. | `mechanisms/params.json` `servo.ear_*` "D6 estimate, measure"; CML data sheet (SH-0255MG+) | No | Buy the servos first. Measure them, then print the frame. Cut the pocket only after a printed frame drops into a test pocket in scrap foam. Also confirm which end the lead leaves from: D6 assumes the front (x 0.178). | $0; 1 h; avoids a scrapped core pocket |
| SC-10 | Minor | Cover `MEC-007`, screws `MEC-011` | **The cover is overloaded.** A 0.8 mm, 2-perimeter PETG cover is at once the servo retainer (it holds the ears in their slots), the TE-up hard stop (the arm hits the slot end), and a part you remove at every service. The M2 self-tappers go into 4 mm-wide bosses with a 1.6 mm pilot, which leaves about 1 mm of wall. They split or strip after a few removals, and if a screw backs out, the servo is loose. | `mec.cover.t_m` 0.0008; C6 JOINTS l.107 (4 × 5 × 6 mm bosses); SPEC mechanical stops | No | Make the cover 1.5 mm thick. Put the TE-up stop on the frame end wall, not the cover. Grow the bosses to at least 5 mm, or press in M2 heat-set inserts (needs a C6 exception, like D-58 b). Pre-flight already checks "cover screws snug"; add a paint-pen witness mark. | +0.5 g; reprint |
| SC-11 | Minor | Panel and rod dynamics | **The outboard panel's rotation mode is in the prop band.** On the CF rod it is about 220 Hz (D6 hand estimate), inside the 180 Hz hover BPF to 311 Hz max BPF band. Add 0.84° of free play and one-end-driven foam panels: classic flutter at ≤ 27 m/s on 70 mm foam elevons is unlikely, but buzz, servo hunting and gear wear are possible. | SPEC open issues (220 Hz); `K09L.param` INS_HNTCH notes; `CL-D6-SLOP` 0.84° | Yes (FEA/modal: C2/C4 modal should carry the panel-on-rod mode, or H1's tap-test result) | Tap-test the panel (CR-D6-18). On the stand, run up slowly through the full rpm range and watch the TEs with a strobe or phone slow-mo. Aim for free play ≤ 0.5° at the TE. | Test only |
| SC-12 | Minor | Surfaces on the ground and in a tip-over | **Standing on its tail:** the TE is 48 mm off the ground, 10 mm with the feet fully crushed, and the panels hang at the servo, which is powered whenever the pack is in. **Belly or back tip-over:** the 200 mm half-fins and the props hit first, so the horns (about 25 mm below the skin) are sheltered. **Sideways tip-over:** this is the likely direction, because `Q_WVANE_LAND 3` lands with a wingtip into the wind. The outboard panel's outer end is 1 mm from the TPU corner cap and about level with it. The panel scrapes, the tape peels, and the rod back-drives the inboard horn and servo. | `landing/SPEC.md` (TE clearance 10 mm crushed, corner caps y 0.5615–0.575, 1 mm gap at y 0.559); `K09L.param` Q_WVANE_LAND | No | Inset the outboard panel end 10 mm (y 0.549), or let the corner cap overhang 2 mm proud of the panel TE in z. After any tip-over, check that both panels are within 1° of each other (BUILD step 10 check). For transport, tape the panels at neutral or use a foam gust-lock. | $0; minor area change (B3 check) |
| SC-13 | Minor | Servo extension and connector | **The in-line JR plug has nothing holding it together.** It sits in an 18 × 10 × 5 mm recess under a tape flap with no latch, in a wing shaken at 90–311 Hz. The 26 AWG run is 0.558 m, which leaves 5.74 V at stall against a 5.7 V floor (+1 %). | `harness/SPEC.md` l.28, l.50; CR-F2-14 | No | Use a servo-lead safety clip or a turn of tape round the joint before closing the flap. Measure the rail at the servo with both servos stalled (T-F1-SERVO-STALL), not only at the FC. | <$1 |
| SC-14 | Minor | Panel twist, effectiveness and CFD | **CFD uses rigid panels at nominal deflection; the built panels will twist.** Each panel is driven from one end through a 5 × 4 CF tube (G 5 GPa assumed). D6 predicts a far-end lag of 2.8–3.0° at VA and effectiveness 0.92, more at VD. B3 already applies an effectiveness factor `e`; B2 and the elevon CFD do not. | `CL-D6-EFF-LOSS-OUT/IN`; BUILD step 12; `team/B3/S-AND-C.md` l.46 | Yes (CFD: run the elevon cases with the spanwise-varying deflection, or at least the mean 25° × e, and with the SC-02 gap) | Do T-D6-TWIST before the CFD rerun, and feed the measured lag back. | Test + one CFD rerun |

**Counts:** Blocker 0 · Major 5 (SC-01, -02, -03, -04, -06) · Minor 9.

## Build steps as I'd actually do them (one side; mirror for the other)

1. **Buy and measure first.** Get 3 servos (2 + 1 spare). Weigh each one. Measure the case, ear span, ear thickness, ear
   height from the base, which end the lead leaves from, and the spline-to-end distance. Measure the arm's existing
   hole radii. Put the numbers into `mec.servo.*` and rerun `make_mechanisms.py` and `mech_calcs.py` (SC-09, SC-07).
2. **Test pocket in scrap foam.** Print one frame and one cover. Cut the pocket in an offcut of the same XPS. Check that
   the frame drops in, the servo ears seat, the cover screws bite without splitting the boss, and the arm sweeps
   ±50° without touching the foam (SC-10).
3. **Cut the wing pockets and lead hole** (D1 step 4) from the measured frame, with the lead hole as a slot if SC-01
   is accepted. Cut the servo-groove branch and the JR recess before skinning.
4. **Cut the panels free and bevel them** (D1 step 9). Rout the torque-tube grooves and the horn slots while the panel
   is still flat on the bench.
5. **Bond the torque tubes** with microballoon epoxy, flush. Cure for 24 h, then tape the bevel face to close the torsion
   box.
6. **Hinge.** Lay the top strip (Blenderm or filament tape) with the panel at neutral on a straightedge, both panels of
   a side in one setup so their axes line up. Flip the wing, fold the panel fully TE-up and lay the lower strip into
   the bevel gap (SC-02). Swing the panel ±30° and check that it moves freely with no tape wrinkle.
7. **Horns.** Cut the tape back at the horn stations, dry-fit both horns with the rod through the fin notch, then bond
   the **inboard** horn only, with the rod in place and both panels clamped flat at neutral. Bond the outboard horn
   with the rod sliding in a brass sleeve (SC-03). Cure for 24 h.
8. **Bench-prep the servo.** Plug it into a servo tester at 1500 µs. Pick the spline tooth that puts the arm nearest
   straight down, screw the arm on with Loctite 222, and drill the Z-bend hole to 1.85 mm at the hole radius chosen in
   step 1. Cut the lead to 40 mm and crimp the pins, but leave the housing off for now.
9. **Frame.** Bond it in the pocket with microballoon epoxy, open side toward the arm plane. Cure for 24 h.
10. **Install the servo.** Feed the pinned lead up through the straw or slot and click the pins into the JR housing in
    the recess. Seat the ears in the slots, fit the cover (1.5 mm version) and tighten the 2 × M2 snug. Tape the cover
    edges. Mark the screw heads with paint pen.
11. **Pushrod.** Z-bend at the arm. Thread the clevis on the other end and adjust its length with the panel at neutral
    on a flat board. Clip the clevis on and fit the keeper. Run the servo tester from 900 to 2100 µs and check for
    binding.
12. **Throws on the FC** (T-D6-THROW). Put a protractor on the TE and set SERVO5/6 MIN/MAX/TRIM for exactly −25/+25° on
    both panels. Check that the inboard and outboard panels agree within 1° at 0 and at ±25°. Push to the 30° stops by
    hand and confirm the servo never buzzes at the software limits.
13. **Free play and load** (T-D6-SLOP, T-D6-TWIST, T-B2-HINGE). Measure free play with a dial gauge at the TE. Hang the
    VA load with the wing on its back, then hold it for 10 min with a heat gun keeping the tape warm (hinge peel check).
14. **Stand run-up** with the props on. Sweep slowly through the full rpm range and watch both TEs with phone
    slow-motion video for buzz (SC-11). Log servo current in a tethered hover (SC-06).
15. **Field kit:** a spare servo pre-pinned (step 8 state), JR housing, pin tool, 2 M2 × 6 screws, spare clevis and
    keeper, hinge tape, Phillips #0/#1. Practise a full servo swap once against the clock before the competition.

## Questions for the team

1. **Hover intent (F4, B3, B4).** Do you expect the elevons to do anything in hover? If not, what should ArduPilot do with
   them in QHOVER, QLAND and the back-transition flare, and has SITL confirmed it?
2. **Fin notch (C4, D3).** Has anyone run the lower fin root with the 24 × 12 mm notch and no fillet over x
   0.2376–0.2616, given the fillet already shows RF 0.81? If it fails, would you rather patch it, or go to four servos
   Y-leaded per side?
3. **Hinge material (D6, D1).** Why packing tape rather than Blenderm or filament tape? Is there a peel or creep test, and
   at what temperature?
4. **Field swap (F2, D6).** Who owns the field servo-swap procedure? Will you accept a lead slot about 8 × 4 mm so that a
   housed JR plug passes?
5. **Rod joint (D6, C6).** Is there a reason the bridge rod must be bonded at both ends rather than slip-fit at the
   outboard horn?
6. **Torque basis (A2, B2, D6).** Can the margin be quoted at 5.74 V, and can D-50's "3.93 kgf·cm" be retired so that one
   torque number exists?
7. **Servo PWM range (F4).** Is 900–2100 µs acceptable on outputs 5–6 if T-D6-THROW needs it? The datasheet allows
   800–2200 µs.
8. **Mechanical stops (D6).** Should the TE-down stop be the foam bevel (it crushes) and the TE-up stop the 0.8 mm cover?
   Would you move both to the frame or the horn?
9. **Ground handling (D5, H1).** With the props removed, are the servos powered while the aircraft stands on its tail in
   the pits? If not, what holds the panels against wind and handling?

Sources used for the servo: CML Distribution SH-0255MG+ data sheet
(https://www.cmldistribution.co.uk/product/SAV-SH0255MG+/files/SAV-SH0255MP%20Data%20Sheet.pdf) and the Lindinger listing
(https://www.lindinger.at/en/RC-ELECTRONICS/Servos-Accessories/Servos-Digital-Low-Voltage/SAVOEX-SH-0255MG-6V-3-9KG-0-13s-Digital-Micro-Servo/9795255).
