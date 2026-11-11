# Motor mounts and propulsion installation: build review

Reviewer: multirotor/VTOL build review (read-only; this is the only file written) · 2026-11-11 · branch `redesign/v1`
Scope: `FIN-003` mounts, `PRP-001…008` stations, ESC pads, phase leads, field service, tip-over.
Method: I read the propulsion, fins and power SPEC/BUILD/parts files, the E1, C4, C6, E3 and F2 notes and the CHANGE-LOG,
and I checked the shipped geometry in `redesign/site/assets/k09l.glb` in Blender: shell bounding boxes of `FIN-003-UR`
and three close-up renders. The renders are outside the repo, in
`C:/Users/dillo/AppData/Local/Temp/claude/7dc708b3f4b13ffc/76f8c44c-eccf-4b13-8a50-e7f1d35cbb75/scratchpad/review/`
(`mount_top_color.png`, `mount_outboard_aft.png`, `mount_rear_access.png`).
Every number below is a repo value or a direct geometric consequence of one; I name the source each time.

## Verdict

The station layout is sound and the clearances hold up. Prop to motor tube is 26.1 mm, prop to wing is about 35 mm on
E1's swept envelope, the upper and lower discs are about 100 mm apart (0.38 m − 0.279 m), and in the standing pose the
props sit at the top of the aircraft, nowhere near the ground. The rotation map, the prop hands and the LH/RH nut hands
are consistent with each other, and the corrected D-52 cant sense now aids the reaction torque (I recomputed it below).

The weak part is the motor mount. As exported, the outboard cheek of every mount runs through the clamp slit and joins
both pinch ears (verified in the GLB). The slip clamp therefore cannot close as designed, and T-D3-SLIP numbers taken on
that print mean nothing. Beyond that defect, the 7° cant and the yaw alignment rest only on friction that is set at its
own breakaway point, on hot ASA, with nothing positive holding them. The motor screws bear straight on ASA at
0.20 N·m with no washer, and the creep test meant to cover this measures breakaway torque, which Loctite dominates.
The "mount is the fuse" idea does not work in the real tip-over direction: lying on the ±z side, the props reach
0.33 m against 0.218 m at the feet, so the props and shafts take the hit, not the slip clamp. The prop nut ends 0.11 mm
past the post with no locking element, and the LH/RH adapters are out of stock.

Fix the mount (cut the slit through the cheek, key it to the station collar, add a metal spreader under the screw heads)
and measure its rocking stiffness hot **before** C4 runs more modal or FEA work. C4's 0.20 separation margin currently
rests on an estimated 3 000 N·m/rad.

## Findings

| ID | Severity | Component | Problem | Evidence | Changes CFD/FEA inputs? | Recommended fix | Cost / time |
|---|---|---|---|---|---|---|---|
| MM-01 | **Blocker** | `FIN-003` slit collar / outboard cheek | The outboard cheek box is drawn from the plate back face to `max(bx)+cheek_len` = x 0.0491, at y 11.5–14 mm from the fin plane and z 0.1661–0.205. The slit sits at x 0.04425–0.04575, y 11.15–13.15 mm, and the pinch ears at x 0.0402–0.0443 and 0.0457–0.0498, y ≥ 12.65 mm, z 0.160–0.172. The cheek therefore fills the slit for the top 8.4 mm of its 14.5 mm height and welds the upper half of both ears together. Nothing re-cuts the slit after the union. The GLB confirms it: the `FIN-003-UR` shell for the outboard cheek spans x 0.0275–0.0493, y 0.3315–0.3340, z 0.1661–0.205, which overlaps the slit and both ear shells. Tightening the M3×16 then has to bend a solid ASA bridge, the clamp does not grip as designed, and the 70–80 N slip setting is not reachable or not repeatable. This affects all four mounts (A and B are mirrors). | `subsystems/fins/fusion/fins.py:549-554` (cheek box), `:534-537` (slit ring and cap); `subsystems/fins/params.json:292` (cheeks reach "to the tube axis"); GLB shell bounds; render `mount_top_color.png` | **yes**: the mount clamp FEA, `CL-D3-SLIP-*`, `CL-C4-D3-MOUNT-K-REQ` / rocking stiffness, and C6's `E-FIN-05…08` stack all assume an open slit | In Fusion, cut a 1.5 mm slot through the whole body (collar, cap, cheek and ears) after the union. Or end the outboard cheek at x < x_t − slit/2 − 1 mm (front ear face 0.0402) and close the load path through the front half of the collar. Re-export the STLs and check the slit with a feeler before printing four. | about 1 h of CAD and one test print; no added mass |
| MM-02 | Major | `FIN-003` → tube (cant and yaw alignment) | No positive anti-rotation. The 7° cant direction, and with it the yaw authority (D-27, D-52), depends on friction in a 12 mm-grip ASA collar, deliberately set "until the collar just turns" (BUILD 19). A clamp set at its breakaway point, in hot ASA (mount 66.3 °C design against an 83 °C limit), relaxes, and the slip torque drifts down with it. The witness line only detects a slip after it has happened. The slip spec also disagrees between documents: fins BUILD says 70–80 N, SPEC says 74 N, C6 says 85–100 N at the can. | `subsystems/fins/BUILD.md:102-105`; `subsystems/fins/SPEC.md:38`; `team/C6/JOINTS.md:102`; `team/E3/THERMAL.md:48`; `params/CHANGE-LOG.md:68` (D-42 already notes that preload relaxation sank PETG) | **yes**: the thrust-vector direction per station in CFD, and the mount boundary condition (friction versus keyed) in FEA and modal | Key the mount to the bonded station collar: a dog on the mount collar's lower face into a notch in the ring top of `FIN-008`, which sets the cant clocking positively. If a fuse is still wanted, make the dog a shear tab or a 1.75 mm filament shear pin sized by C6. Keep the pinch bolt as the clamp. Settle one slip number. This must be decided **before fins step 13**, because the station collars are bonded there (coordinate with CR-D3-36, which is growing that collar). | reprint 4 mounts and 4 collars (a few grams of ASA/PETG); about 2 h of CAD; C6 sizes the pin |
| MM-03 | Major | Motor screws `E-FIN-61…64` | Four M3×8 at 0.20 N·m, "no washer", bearing directly on the ASA plate, whose base runs at 66.3 °C. Under-head ASA creep sheds preload. Loctite 243 on the tips then holds the screws in place while the joint itself goes slack and the motor fretts on the plate. The planned test, `T-C6-HEAD-CREEP` (breakaway ≥ 0.15 N·m after 2 h at 70 °C), can pass with zero preload left, because the threadlocker sets the breakaway torque. | `subsystems/fins/BUILD.md:96-97`; `subsystems/propulsion/SPEC.md:49`; `team/C6/JOINTS.md:183`; `team/E3/THERMAL.md:48,86` | **yes**: the motor-to-plate joint stiffness in the modal model, and the joint FEA (head bearing) | Put a 1–1.5 mm aluminium or G10 spreader plate (an X- or square plate that fits inside the 23 mm between the cheeks) under the heads, or penny washers if they fit. Re-check engagement: the spreader eats thread, so M3×10 may be needed, and only if the measured base-hole depth allows (MM-09). Rerun the creep test **without** threadlocker and judge it on loss of the turn angle or clamp, not on breakaway. Keep the motor face x fixed by thinning the ASA by the spreader thickness. | about 4 small plates (G10 offcut or a laser-cut set); +1–2 g per station, to be weighed; about 1 h |
| MM-04 | Major | Motor bolt pattern and plate envelope | The pattern is unpublished. The prints carry pilots for a 16 × 19 mm cross and the plan is to "drill to the measured motor". The geometry only allows that within limits. Screw heads (Ø5.5) clear the cheeks (inner face 11.5 mm) only when the y half-span is ≤ 8.75 mm, so the y pattern must be ≤ 17.5 mm. In z, the lowest head clears the lip cap by 3.2 mm at 19 mm and by about 0.2 mm at 25 mm. The lead-exit clocking also fixes the pattern orientation. The plan also says "motor as template": a 3.4 mm drill through the motor's M3 tapped holes ruins them and throws chips into the motor. The only public listing I found gives a 4 mm shaft, Ø37.8 × 26.5 mm and 81 g, and no pattern. | `subsystems/fins/params.json:256` ("motor as template"); `subsystems/fins/BUILD.md:38-40`; `fins.py:117-123` (pattern drives head and cap z); `subsystems/propulsion/SPEC.md:63`; retailer listing (robu.in, X3108S KV900; the sunnyskyusa.com page returned HTTP 429 during this review) | **yes, if the pattern is out of envelope**: plate, cap and face x change, which moves the prop plane x (CFD) and the mount geometry (FEA) | Get the pattern **now** from SunnySky support or photos, or from the first motor as soon as it lands. Make the plate STL parametric so a reprint is cheap. Mark the holes with a transfer punch or a printed drill guide, then drill **without** the motor. Never drill through the motor's threads. | 0–4 reprints; 1 day of risk if the pattern is 19 × 19 or wider |
| MM-05 | Major | Tip-over (D-23 "mounts are the fuse") | Lying on the ±z side, the contact points are the feet at z ±0.218 and the fin tips at 0.21, while the motor can top is at 0.209 and the prop tips reach z up to 0.33 (0.19 + 0.1397). Unless a blade is parked spanwise, the props are a contact point. The impact load runs along the tube axis and as bending about y at the plate, which is not the axis the slip clamp releases about. The cap is seated against the tube end, so there is no fuse in that direction. Likely damage, in order: props, then a bent 4 mm shaft (a motor swap), then a cracked plate or cheek (the cheeks are loaded across layer lines because the collar axis is printed vertical). Spares: 1 motor and 4 flight props; parts.csv has no spare mounts, yet the repair table assumes "swap in a spare ASA print". | `params/CHANGE-LOG.md:44` (D-23, 3.5 J), `:56` (tip-over about 30°); `fusion/DATUMS.md:73-88` (feet z ±0.218); `subsystems/propulsion/SPEC.md:38`; `subsystems/fins/parts.csv:4` (qty 4); `subsystems/fins/BUILD.md:111-116` | **yes**: add a tip-over load case (prop-tip impact along ∓z at r 0.14 m, 37 mm ahead of the plate) to the mount, tube and cheek FEA; C5's tip-over energy is the input | Arm crash disarm and fast landed-disarm (F4) so props stop before the fall ends. Carry 2 spare motors, 8 flight props, and 4 spare mounts (2 A + 2 B) undrilled plus a drill guide. Test-break one mount at T-C4-FIN-PROOF in the tip-over direction. | +1 motor $24.99, +4 props × $3.83 (repo prices), about 50 g of ASA |
| MM-06 | Major | Prop retention `E-PRP-05…08` | (a) Thread past a full ISO 4032 nut is 0.11 mm, so any hub or washer tolerance leaves the nut short. (b) There is no locking element: self-tightening hands help on spin-up, but hard braking for quad yaw/attitude control (Bluejay, bidirectional DShot) tries to back the nut off. (c) The LH/RH adapter set is out of stock. The fallback is a single-hand boxed adapter "with Loctite 243 on the nut", on a joint that is undone at every set-up for transport. | `subsystems/propulsion/SPEC.md:22,47`; `subsystems/propulsion/parts.csv:5`; `subsystems/propulsion/BUILD.md:28,31-33`; `team/E1/PROPULSION.md:208,263` | no (the post grows forward of the hub; E1's +10 mm forward envelope covers a few mm, but check it) | Buy or confirm adapters with a post that leaves ≥ 2 full threads past an M6 **nyloc** (or flanged nyloc) prop nut, in matched LH/RH sets, and order them now. If only one hand is available, use nylocs on all four and drop the Loctite field joint. Witness-mark each nut every flight (already in C6). | price of a replacement set unknown (`UNVERIFIED`); nylocs pennies; +about 1 g per station |
| MM-07 | Major | Mount rocking stiffness (vibration) | C4 needs ≥ 971–1 030 N·m/rad to keep 0.20 separation from 2P. The only input is an "estimate 3 000", and at 1 000 N·m/rad the separation falls to 0.26. The real stiffness of a 12 mm friction collar with 2.5 mm ASA cheeks, measured hot, is unknown, and MM-01/02/03 all change it. | `team/C4/BOOM-STRUCTURES.md:84-94,150,168`; `team/C4/SUMMARY.md:18` | **yes**: the C4 modal mount spring and the Campbell diagram | Build one fixed mount on a 100 mm tube stub and run `T-C4-MOUNT-STIFF` at room temperature and at 66 °C (heat gun plus thermocouple) **before** further modal or FEA runs. Feed the measured value to C4. | half a day; uses a spare print |
| MM-08 | Minor | Cant-sense documentation | Propulsion SPEC open issue 3 still reads "+0.045 N·m/N … opposes the CW reaction torque: swap prints A/B". With `cant_sense_UR = −1` the UR side component is (0, +0.511, −0.860), giving Mx = 0.32·(−0.860) − 0.19·(0.511) = −0.372 × T sin 7° ≈ −0.045 N·m/N. That is along −x, the same as the reaction torque of a motor turning CW about +x. The CAD is right and the text is stale. A builder reading it could swap the prints. | `subsystems/propulsion/SPEC.md:61`; `params/CHANGE-LOG.md:294` (D-52); `fins.py:102-114` | no | Delete or rewrite issue 3. In BUILD, state "CW from the nose = CW looking aft from ahead of the aircraft". Keep the inclinometer check and the hanging yaw test. | 10 min |
| MM-09 | Minor | Bell-top adapter screws and base-hole depth | Torque is 0.5 N·m in the SPEC and BUILD but 0.6 N·m in the E1 interface table. The free depth to the windings (bell top) and the base-hole depth are measured on "one of each" only. A screw too long for one motor shorts a phase. | `subsystems/propulsion/SPEC.md:23,46`; `team/E1/PROPULSION.md:218`; `subsystems/propulsion/BUILD.md:21` | no | Settle on one torque value. Probe every motor's 8 holes before its screws go in, and record them on the build sheet. | 15 min per motor |
| MM-10 | Minor | Field serviceability | Phase splices are soldered and staggered, and the ESC power is soldered into the skin grooves (chosen for mass, −15.6 g, and for no contacts in the fatal path). A field motor swap therefore needs an iron, heat-shrink and a re-spin test. An ESC swap is a shop job. | `subsystems/harness/BUILD.md:18-20`; `team/F2/CHANGE-REQUESTS.md:11`; `subsystems/propulsion/SPEC.md:51` | no | Keep the soldered design, but pre-build the spare motor with its extension spliced and labelled, carry a battery iron in the field kit, and write a timed motor-swap card (rehearse it once). | about 1 h of rehearsal |
| MM-11 | Minor | Torque method | 0.20 N·m set as "4 N on a luggage scale 50 mm out": coarse at the bottom of a luggage scale's range. The nyloc's prevailing torque also hides the pinch-bolt preload. | `subsystems/fins/BUILD.md:96-97`; `subsystems/propulsion/BUILD.md:25` | no | Use a preset torque screwdriver in the 0.1–1 N·m range (shared shop tool). Keep the luggage scale for the slip pull only. | one tool |
| MM-12 | Minor | Phase lead routing | The phase bundle runs over the pinch bolt and nyloc (1.3 mm clearance to the bolt in ROUTE-CLEARANCE) and is tied at the pinch ear, on the part that is designed to rotate. That invites chafe at 90 Hz, puts strain on the lead if the mount slips, and means re-setting the slip needs the ties cut. | `subsystems/harness/SPEC.md:49`; `team/F2/ROUTE-CLEARANCE.md:31-35` | no | Sleeve the bundle where it crosses the bolt. Tie it only to fixed structure (collar-tail lug) with a 10–15 mm service loop to the motor. | minutes |
| MM-13 | Minor | Shaft retention and rear opening | In the tractor sense, thrust pulls the bell off the stator, held by the rear E-clip. The 10 mm square plate opening is "UNVERIFIED against the motor" for the clip and shaft end. | `subsystems/propulsion/SPEC.md:34`; `subsystems/fins/params.json:272` | no | At incoming inspection, check that each clip is fully seated and that the shaft end and clip clear the opening on a hand spin with the motor bolted. | minutes |
| MM-14 | Minor | Vibration path to the FC | The path is motor → ASA mount → CF tube → PETG block → spar → core → pod → gel FC mount. The fin panel mode is 71–76.5 Hz, about 21 % below hover 1P (90 Hz), and the FC isolation (T = 0.21 at 1P) is unverified. The rpm notch is planned (F4), but prop balance is not in any BUILD step. | `team/C4/SUMMARY.md:39`; `subsystems/avionics/SPEC.md:20-21`; `subsystems/flight-software/SPEC.md:29` | no | Balance every prop (and the bell with the adapter fitted) on a magnetic balancer before T-E1-STAND. Do the tap test with the ESCs and props fitted. Review the first-hover FFT per F4's tuning plan. | about 1 h; balancer if the shop has none |

Counts: **1 Blocker, 6 Major, 7 Minor.**

Checked and OK, so not listed as findings: prop to tube 26.1 mm (E1 `prop_clearance.json`, `face_ahead` 7.5 mm); prop to
wing about 35 mm on the swept envelope; upper/lower disc gap about 100 mm; prop to pod about 110 mm (inboard tip at
y 0.180 against the pod at ±0.07); props about 0.33 m+ above ground in the standing pose (`hover-pose.png`); ESC on the
fin face inside the wash (0.89 R), 56.1 °C against 85 °C (E3); rotation map, MR/MRP and thread hand consistent
(SPEC:40, BUILD:3-4).

## Build steps as I'd actually do them

1. **Before any print is final:** fix MM-01 (cut the slit through) and MM-02 (dog/notch to the station collar) in Fusion,
   add the spreader pocket (MM-03), and settle one slip number. Print **one** mount A and one station collar as a test
   article.
2. **Incoming, every motor (not one of each):** weigh it; measure the pattern, base Ø, the depth of all 4 base holes and
   all 4 bell-top holes to the windings, shaft protrusion, clip seating and lead length; check phase resistance, I0 and
   both spin directions. Label the motor. Reject or quarantine any outlier.
3. **Pattern check against the envelope** (y ≤ 17.5 mm, z ≤ about 24 mm with the lip cap): if it is outside, reprint
   from a parametric STL. Do not try to drill your way out of it.
4. **Drill the plates from a transfer-punched mark or a printed drill guide**, square to the canted face, with no motor
   on the plate. Deburr. Print 2 spare A and 2 spare B now.
5. **Adapters on the bench:** check that the post leaves ≥ 2 threads past a nyloc on the real prop and washer. Fit the
   screws with 243 on the tips at one agreed torque using a torque driver, then spin on a balancer and true the
   adapter. Witness mark.
6. **Motor to plate:** spreader plate, then the screws (length from step 2), 243 on the tips only, torque driver,
   witness marks. Hand-spin: no rub at the rear opening.
7. **Station collars bonded with the notch clocked** using the inclinometer on a dummy mount (the cant is set here,
   once, not by friction later). Cure per fins BUILD.
8. **Mount onto the tube**, dog in the notch, pinch bolt to the agreed setting, slip/shear check. Then run
   `T-C4-MOUNT-STIFF` on the test article, cold and at about 66 °C, and send the number to C4 before any more modal
   work.
9. **ESC pad and strap**, phase splices with sleeves, the bundle tied to fixed structure with a service loop, clear of
   the pinch bolt. Spin test for direction at 5 %.
10. **Props:** balance each one, fit by hand (MR on UL/LR, MRP on UR/LL), washer, nyloc, 1.5 N·m with the bell held,
    witness mark. T-E1-STAND on each station: thrust, current, ten punch-outs, then check the nut and screw witness
    marks again.
11. **First hover:** hanging yaw test first, then a tethered hover; log VIBE and FFT, and look for the 70–90 Hz band.
12. **Field kit:** 10 mm spanner, torque driver, 2.5 mm key, 2 spare motors (one pre-spliced), 8 props, 4 spare mounts,
    spare nylocs, battery iron, heat-shrink, motor-swap card. **After any tip-over:** spin every motor by hand (bent
    shaft = wobble at the nut), check the witness lines and look for cheek cracks before re-arming.

## Questions for the team

1. D3: was the cheek-through-slit overlap (MM-01) intended as a "bridge" for print stability? If so, how was the 2.5 N·m
   slip derived with a bridged slit? Has any physical slip test been run on an R5 print?
2. D3 / C6: which slip value is the real one, 70–80 N (fins BUILD) or 85–100 N (C6 JOINTS)? Is a slipping mount still
   wanted, now that the tip-over load mostly arrives along the tube axis?
3. E1: has anyone seen an X3108S in hand or a drawing? Specifically: the pattern, whether the shaft protrudes above the
   bell for the Ø4 pilot, bell-top thread depth, and whether the box includes an X-mount or a different prop adapter.
4. E1: what is the post length of the boxed adapter, and can you get a matched LH/RH set with a nyloc-length post before
   the motors arrive?
5. F4: are crash disarm and the landed-disarm delay set for Q-modes, and is reverse/active braking enabled (it affects
   prop-nut back-off)?
6. C4: what is the 3 000 N·m/rad mount estimate based on, and would you accept a measured hot value in its place before
   the next Campbell run?
7. C5 / D5: which side does the aircraft tip to in your model (the pod side, +z, per D-30)? Since blade position at
   touchdown cannot be controlled, is a light tip skid or guard on that pair worth its mass, or do we accept props as
   consumables?
8. A1: with propulsion at 462.0 / 462 g, where do the spreader plates (+1–2 g per station) and nylocs come from?
