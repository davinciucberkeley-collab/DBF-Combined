# Landing and impact: K09-L fin-tip feet

Owner C5 (landing / impact). Status `PROPOSED`, revision **C5-R6**, 2026-11-10. Inputs: params **A1-R5** (D-62 CG
range 0.0466–0.0514 m, target 0.0490, z 0.0185 and z range 0.010–0.025; D-62 bay: nose −0.140, forward stop aft face
−0.1312, no-spacer station −0.020; **D-64** Ovonic 120C EC5 pack 551 ± 5 g, 135 × 46 × 49 mm; **D-65** hard landing
1.2 m/s at ≤ 10° any direction, `landing_n_design` 6.6, side load 39.3 / 59.0 N, shoe sleeve end wall 2.0 / rim 3.0 /
R 1.0 / 25 mm engagement), A3-R6a roll-up (2.322 kg basic, I 0.173 / 0.044 / 0.168 kg·m²; A3 has not yet re-run on
the D-62 bay), D2-R5a pod params (block A = 1 mm epoxy bond line, forward stop 3 × 25 × 54 mm) and D5-R5a's foot
(stroke 38 mm, 35 mm usable, plateau U 39.6 / L 35.4 N). Numbers: `python -I redesign/team/C5/landing_calc.py`
(claims `claims.json`) and the simulation round `landing_sim_claims.py` (claims `claims.sim.json`,
`SIMULATION-REPORT.md` §0).

**What changed since C5-R5 / C5-S1 (this revision).**
1. **Tip-over on the D-62 range.** `CALC-C5-STANCE` reads the CG range and target from `params.json` (`cg.*`, D-62),
   not B3's R4 claims, and the D-64 packs (546 / 551 / 590 g) at their D-62 stations (`ASM-C5-D62-STATIONS`, A1's
   frame estimate until A3 re-runs). Corner bound at x 0.0466, z 0.025: **30.98°** (+3 %), same as `CL-A1-TIPOVER`.
2. **Crash block per D-64 pack on the D-62 bay.** All three pass at their marks (+0.7 / +2.4 / +6.6 mm). Two
   corrections: block A has been a 1 mm epoxy bond line since D-47 and no longer gets crush credit (−1 mm on every
   margin), and the "crush block ≥ 24.3 mm" in the D-62 bay note is the old 503 g number: the D-64 packs need
   **25.5 / 25.8 / 27.6 mm** (CR-C5-21).
3. **6-DOF sim at 1.2 m/s** with the D-62 CG and a lightest-mass case: worst stroke 34.9 of 35 mm at the gate, no
   case bottoms inside 10°, n **6.60 at the lightest flying mass** (limit 6.6, 0 %), side load unchanged at 39.3 N
   (μ 0.7) / 29.1 N (μ 0.5). With 0.3 m/s touchdown drift, 1.2 m/s bottoms a foot; 1.1 m/s holds (CR-C5-23). The
   drift cases raise the side load to 39.44 N, so the design basis rounds up to **39.5 N limit / 59.25 N ult**.
4. **Shoe FEA on the D-65 stack** (3 meshes): RF **@RF@** at 59.25 N ultimate (GCI @GCI@); the as-drawn D5-R5 shoe
   (RF 0.22) is kept only as a record.

## Verdict

| Check | Result | Claim | Status |
|---|---|---|---|
| Tip-over, D-62 target CG (551 g), pod side | 32.0° vs 30° | `CL-C5-TIPOVER-R1` → `R-TIPOVER` | `UNVERIFIED` (+7 %) |
| **Tip-over, worst flying CG** (forward limit 0.0466, 590 g) | **31.8°** | `CL-C5-TIPOVER-WORST` → `R-TIPOVER` | `UNVERIFIED` (+6 %) |
| Tip-over, each D-64 pack at its D-62 station (worst 590 g at −0.028) | 32.0° | `CL-C5-TIPOVER-D47` → `R-TIPOVER` | `UNVERIFIED` (+7 %) |
| **Corner bound: x 0.0466 with z_cg 0.025** | **30.98°** | `CL-C5-TIPOVER-B3-CORNER` (= `CL-A1-TIPOVER`) | `UNVERIFIED` (+3 %) |
| Worst station with the CG a further 5 mm higher | 31.6° | `CL-C5-TIPOVER-STATION-PLUS5` | `UNVERIFIED` (+5 %) |
| **Hard landing 1.2 m/s, ≤ 10° any direction, 2.6 kg (6-DOF)** | **34.9 of 35 mm** | `CL-C5-SIM3D-STROKE` → `R-LANDING-IMPACT` | `MODELLED` (+0.3 %) |
| Same at A3 predicted 2.436 kg / basic 2.322 kg | 32.6 / 31.0 mm | `CL-C5-SIM3D-STROKE-A3` | `MODELLED` |
| Tilt that bottoms a foot at 1.2 m/s | none inside 10° | `CL-C5-SIM3D-BOTTOM-TILT` | `MODELLED` |
| Sink limit, 10° any direction / with 0.3 m/s drift | 1.2 / 1.1 m/s | `CL-C5-SIM3D-V-SINK-10`, `-V-SINK-DRIFT` | `MODELLED` (0 %; CR-C5-23) |
| **Peak n, level, lightest flying mass (546 g pack, 2.318 kg)** | **6.60 vs 6.6** | `CL-C5-SIM3D-N-LIGHT` → `R-LANDING-IMPACT` | `MODELLED` (0 %; CR-C5-22) |
| Peak n, level, A3 basic 2.322 kg | 6.59 | `CL-C5-SIM3D-N` | `MODELLED` (+0.2 %) |
| Foot side load, design basis (limit / ult) | **39.5 / 59.25 N** (was 39.3 / 59.0) | `CL-C5-SIM3D-SIDE-LOAD`, `-SIDE-ULT` | `PROPOSED` (CR-C5-16) |
| Side load, 1.2 m/s envelope + drift (μ 0.7) | 39.44 N | `CL-C5-SIM3D-SIDE-12` | `MODELLED` (+0.2 %) |
| **Side load with a μ ≤ 0.5 pad face (option)** | **29.1 N limit / 43.7 N ult** | `CL-C5-SIM3D-SIDE-MU05`, `-ULT` | `MODELLED` (option for D5) |
| **Shoe GER-001, D-65 stack, RF at 59.25 N ult** | **@RF@** (@RFG@ with GCI) | `CL-C5-FEA-SHOE-SF`, `-SF-GCI` | `MODELLED` |
| Shoe RF with the μ 0.5 pad | @RFMU@ | `CL-C5-FEA-SHOE-SF-MU05` | `MODELLED` |
| Wingtip TE corner in a 10° roll landing | strikes from 7.5° (−7.2 mm planar) | `CL-C5-SIM3D-STRIKE-TILT`, `CL-C5-WINGTIP-CLEAR-ROLL` | `FAIL` by intent (corner cap `GER-007`, CR-C5-04) |
| Landing broadside, lull | 4.0 m/s (sim) / 4.39 (static) | `CL-C5-SIM3D-V-BROADSIDE`, `CL-C5-V-LAND-BROADSIDE` | `FAIL` → wingtip into wind (S2) |
| Landing span into wind | 8.0 m/s (sim) / 8.2 (static) | `CL-C5-SIM3D-V-SPANWISE`, `CL-C5-V-LAND-SPANWISE` | `MODELLED` (0 %) |
| Drift landings that tip (0.3 m/s, 10°) | 0 of 128 | `CL-C5-SIM3D-DRIFT-TIPS` | `MODELLED` |
| Normal landings per cartridge | 2.3 vs ≥ 5 | `CL-C5-LANDINGS-PER-CARTRIDGE` | `FAIL` → D5 (CR-D5-21) |
| **Crush room, worst D-64 pack at its D-62 mark** | **+0.7 mm** (546 g at −0.036) | `CL-C5-PACK-ROOM-MARGIN-WORST` → `R-PACK-RETENTION` | `UNVERIFIED` (thin) |
| Crush stack at the 24.3 mm minimum vs the block each pack needs | −3.3 mm (590 g) | `CL-C5-PACK-STACK-MARGIN` | `FAIL` as noted → CR-C5-21 |
| Pack deceleration, 5 m/s nose-in | 95 g (546 g pack) vs 100 | `CL-C5-PACK-CRASH-G` | `UNVERIFIED` (+5 %) |
| Box x slack with the D-62 nose | 17 mm | `CL-C5-BOX-X-SLACK-NOSE` → `R-TRANSPORT` | `UNVERIFIED` |

## 1. Stance tip-over (D-62 range, D-64 packs)

Ground plane at x = c + foot = 0.368 m; the narrow axis tips over the pad pair at z = ±0.218 m (`CL-D5-CONTACT-Z`).
The pod side (+z) governs: the CG is 18.5 mm above the chord plane. A3-R6a's items still carry the D-47 bay; each
flying case slides the pack until the CG is on a D-62 line, or puts the pack at its D-62 flight-card station.

| CG case | Mass kg | x_cg m | z_cg m | Pack x m | h m | D5 pads, pod side ° | Other side ° | Wide ° |
|---|---|---|---|---|---|---|---|---|
| Pre-D-47 bay (reference) | 2.322 | 0.0577 | 0.0185 | −0.001 | 0.310 | 32.7 | 37.3 | 45.9 |
| A3-R6a as listed (D-47 datum −0.022) | 2.322 | 0.0522 | 0.0185 | −0.022 | 0.316 | 32.3 | 36.8 | 45.4 |
| **Target 0.0490, 550 g** | 2.322 | 0.0490 | 0.0185 | −0.0374 | 0.319 | **32.0** | 36.6 | 45.1 |
| Target, 590 g / 546 g | 2.362 / 2.318 | 0.0490 | 0.0190 / 0.0184 | −0.0315 / −0.0380 | 0.319 | 32.0 / 32.0 | 36.6 | 45.1 |
| **Forward limit 0.0466, 590 g** | 2.362 | 0.0466 | 0.0190 | — | 0.321 | **31.8** | 36.4 | 44.9 |
| Forward limit, 546 g | 2.318 | 0.0466 | 0.0184 | — | 0.321 | 31.8 | 36.3 | 44.9 |
| Aft limit 0.0514, 550 g | 2.322 | 0.0514 | 0.0185 | — | 0.317 | 32.2 | 36.8 | 45.3 |
| D-62 station 546 g (−0.036) | 2.318 | 0.0495 | 0.0184 | −0.036 | 0.319 | 32.1 | 36.6 | 45.1 |
| D-62 station 551 g (−0.034) | 2.323 | 0.0498 | 0.0185 | −0.034 | 0.318 | 32.1 | 36.6 | 45.2 |
| **D-62 station 590 g (−0.028)** | 2.362 | 0.0499 | 0.0190 | −0.028 | 0.318 | **32.0** | 36.7 | 45.2 |
| **Corner bound: x 0.0466, z 0.025** | — | 0.0466 | 0.025 | — | 0.3214 | **30.98** | — | 44.9 |
| No pack (parked) | 1.772 | 0.0758 | 0.0092 | — | 0.292 | 35.5 | 37.9 | 47.6 |

- **The corner bound is 30.98°, +3 %.** It is geometry only: atan((0.218 − 0.025) / 0.3214). No flying case reaches
  it, because A3 rolls up z 0.0185 and B3's z range is held 6.5 mm above that.
- The D-62 bay moves the CG forward, i.e. up in the stance: from the pre-D-47 bay to the 551 g D-62 station the CG
  rises 7.9 mm and costs 0.65° (`CL-C5-D47-CG-RISE`, `-TIP-CHANGE`). A further 5 mm still gives 31.6°.
- A3's station predictions use A1's −0.9 mm D-61 stack shift; the items here do not. That moves h by < 1 mm (0.08°).
- On a slope: the calm-landing slope limit is 13.7° (`CL-C5-SLOPE-CALM`); the card stays at ≤ 5° (S1).

## 2. Landing in wind

Unchanged in method (static: tilted touchdown, pivot holds; 6-DOF: crushing feet, friction). Static broadside limit
4.39 m/s, span into wind 8.2 m/s; 6-DOF 4.0 and 8.0 m/s (lull, sink 0.5 and 1.2 m/s). Rule S2 stands: land with a
wingtip into the wind. Thrust fraction a 10° tilt survives: 0.71 W (`CL-C5-LAM-MAX`, +6 %).

## 3. Hard landing at 1.2 m/s (D-65)

The 6-DOF model (`sim/landing_sim3d.py`) is the design check; the planar model (`CALC-C5-DROP-DYN`) stays as a
cross-check of the pitch and roll pairs only: a diagonal touchdown lands on one foot, which the planar model cannot
show (planar pair-first 21.5 mm vs 6-DOF diagonal 34.9 mm at the gate).

| Case (1.2 m/s, lift 2/3 W, μ 0.7) | Lightest 2.318 kg | A3 basic 2.322 kg | A3 predicted 2.436 kg | Gate 2.6 kg | Limit |
|---|---|---|---|---|---|
| Worst stroke, ≤ 10° any direction | 30.9 mm | 31.0 mm | 32.6 mm | **34.9 mm** | 35 mm usable |
| Peak n, level | **6.60** | 6.59 | 6.28 | 5.88 | 6.6 |
| Sustained side load (1 ms) | 39.3 N | 39.3 N | 39.3 N | 39.3 N | design 39.5 N |
| Wingtip TE corner strikes from | 10° | 10° | 7.5° | 7.5° | cap `GER-007` |

| Envelope check | Result | Claim |
|---|---|---|
| Sink sweep, 10° any of 24 directions, gate | 1.2 m/s holds, 1.3 m/s bottoms | `CL-C5-SIM3D-V-SINK-10` |
| + 0.3 m/s drift in 8 directions, gate / A3 predicted | 1.2 m/s: 38.1 / 36.9 mm (bottoms); 1.1 m/s: 33.4 / 31.4 mm | `CL-C5-SIM3D-V-SINK-DRIFT` |
| μ 0.5 pad face, gate | stroke 27.6 mm, side 29.1 N | `CL-C5-SIM3D-SIDE-MU05` |
| Free-drop corner test height (no lift, 10°, gate) | ≤ 50 mm (34.1 mm); fly the test at 45 mm (31.0 mm) | `CL-C5-TEST-CORNER-H` |

- **n at the lightest mass is exactly at 6.6.** n = 4 × 37.5 N / (m g) does not depend on the sink speed. The
  coupon tolerance (+2 %) would give 6.73. CR-C5-22 asks D5 to accept cartridges at −3 / +0 % of nominal, or C1 to
  check the airframe at 6.75. Lowering the plateau is not an option: the gate stroke has no margin left.
- **The 3 mm guard is the plateau-scatter allowance** (`ASM-C5-DROP-GUARD`); with it the gate case has 0.1 mm in
  hand. The flying aircraft is 2.44–2.46 kg, where the margin is 2.4 mm.
- **Drift.** The D-65 case has no drift. A pilot down-stick landing in QLOITER can drift 0.3 m/s, and then 1.2 m/s
  bottoms a foot. C5 asks F4 for `Q_PILOT_SPD_DN` 1.0 m/s (CR-C5-23); the requirement stays 1.2 m/s.
- Planar cross-checks at 1.2 m/s (`CL-C5-DYN-*`, `CL-C5-DROP-PAIR-*`): level 15.5 mm, pitch pair 21.4 mm, roll pair
  20.1 mm, n 5.88 at 2.6 kg; free drop 0.073 m strokes 17.7 mm (hand).

## 4. Foot side load and the shoe (sizing for D5)

| Item | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Design side load at the pad, limit / ultimate (μ 0.7) | 39.5 / 59.25 | N | `CL-C5-SIM3D-SIDE-LOAD`, `-ULT` | `PROPOSED` |
| Option: pad face μ ≤ 0.5 on the mat, limit / ultimate | 29.1 / 43.7 | N | `CL-C5-SIM3D-SIDE-MU05`, `-ULT` | `MODELLED` |
| Hand value (C1 corner load × μ 0.7), superseded | 24.9 | N | `CL-C5-FOOT-SIDE-LOAD` | record |
| D-65 shoe: tine lip reaction per N of side load | @LEV@ | — | `ASM-C5-FEA-LEVER-D65` | `MODELLED` |
| D-65 shoe: governing von Mises at 59.25 N ult | @SIG@ | MPa | `CALC-C5-FEA-SHOE-D65` | `MODELLED` |
| **D-65 shoe RF (allowable 40 MPa)** | **@RF@** | — | `CL-C5-FEA-SHOE-SF` | `MODELLED` (GCI @GCI@) |
| Limit side load at RF 1 | @CAP@ | N | `CL-C5-FEA-SIDE-CAPACITY-D65` | `MODELLED` |
| As-drawn D5-R5 shoe RF at 59.25 N (record) | 0.22 | — | `CL-C5-FEA-SHOE-SF-R5` | superseded |

Build notes for D5: print the inside corners with R ≥ 1.0 mm and the layers along the sleeve axis; the governing
stress sits in the rim body at the sleeve end, not in the clamp edge at the fin TE (that peak is a modelling
singularity and is reported only). If D5 adopts the μ 0.5 pad face, the parked-slide checks use μ 0.5 too:
`CL-C5-V-SLIDE-GRASS-EMPTY` is already computed at 0.5.

## 5. Stance rules for the flight card (to H3, CR-C5-06)

| # | Rule | Number behind it |
|---|---|---|
| S1 | Land on the mat (≥ 0.8 × 0.8 m), level within 5° | slope room 13.7° calm |
| S2 | Final descent and touchdown with **a wingtip into the wind** | broadside 4.0 m/s; span into wind 8.0 m/s |
| S3 | Touch down in QLAND / QLOITER at ≤ 0.5 m/s; pilot down-stick ≤ 1.0 m/s | 1.2 m/s + 0.3 m/s drift bottoms a foot |
| S4 | Spin down at once after contact | > 0.71 W tips a 10° tilt |
| S5 | Between flights lay it flat unless gusts ≤ 5 m/s, pack in, on the mat | pack out: gust 5.3 (mat) / 4.5 (grass) m/s |
| S6 | Lay flat pod up, lower props turned spanwise first | lifts at 11.3 m/s |
| S7 | Check the replace-mark groove after every landing | 2.3 normal landings per cartridge |
| S8 | After a hard landing or tip-over: shoe bonds, fin tips, wingtip caps, props, mounts, pod nose and block | §6 |
| S9 | **Pack at its D-62 mark only** (546 g −0.036, 551 g −0.034, 590 g −0.028), block B cut to fill the gap; **never forward of** −0.0367 (546 g), −0.0364 (551 g), −0.0346 m (590 g) | `CL-C5-PACK-X-FWD-MAX-*` |

## 6. Crash energy path

Order of failure, cheapest first. The pack, FC, spar and motor tubes must never fail first.

| Order | Element | Takes | Repair | Owner |
|---|---|---|---|---|
| 1 | XPS foot cartridge | 1.2 m/s landing, any tilt ≤ 10° | swap, 3 min | D5 |
| 2 | Piston / pad, shoe; wingtip corner cap | beyond full stroke; roll landings ≥ 7.5° | printed spare, 10 min | D5 |
| 3 | Props | tip-over onto a prop pair | field spares | E1 |
| 4 | Printed motor mount (slip collar 2.5 N·m) | fails before the tube (D-23) | printed spare | D3, C4 |
| 5 | Half-fin, wingtip TE | fall beyond the feet | re-cut, 1 day | D3, D1 |
| 6 | XPS wing core | major crash | re-cut, 1–2 days | D1 |
| 7 | Pack crush block B + forward stop (nose-in) | 5 m/s, pack ≤ 100 g | cut a new block, reprint the stop | D2, C3 |
| never | Pack, FC, spar, motor tubes | — | — | D2, C3, F3 |

**Nose-in at 5 m/s (`CALC-C5-CRASH`, D-62 bay, D-64 packs).** Stack from the nose: shell at −0.140, nose wall
inside face −0.1352 (4.8 mm board), 1 mm epoxy bond line (no crush credit), forward stop 3 mm, aft face **−0.1312**,
then block B (XPS F-250 over the full 52 × 56.9 mm bay: 509 N, so n < 100 for every D-64 pack), a 1.5 mm spreader
and the pack fore face (pack 135 mm long).

| Pack (weighed) | D-62 mark | Force N / n | Block B needed (+ spreader) | Gap at the mark | **Margin** | Most forward station | Block B cut to fill |
|---|---|---|---|---|---|---|---|
| 546 g | −0.036 | 509 / 95 | 25.5 (27.0) mm | 27.7 mm | **+0.7 mm** | −0.0367 | 26.2 mm |
| 551 g | −0.034 | 509 / 94 | 25.8 (27.3) mm | 29.7 mm | **+2.4 mm** | −0.0364 | 28.2 mm |
| 590 g | −0.028 | 509 / 88 | 27.6 (29.1) mm | 35.7 mm | **+6.6 mm** | −0.0346 | 34.2 mm |

Claims: `CL-C5-PACK-ROOM-MARGIN-546/-551/-590`, `CL-C5-BLOCK-L-546`, `CL-C5-BLOCK-L` (551 g, read by D2),
`CL-C5-BLOCK-L-590`, `CL-C5-PACK-X-FWD-MAX-*`, `CL-C5-BLOCK-FILL-*` (+3 / +9 / +24 % over the length each needs).

- **The 24.3 mm minimum block is too short for the D-64 packs.** It was the 503 g pack's length. A pack on the
  crush stack at −0.0379 (CR-A1-62) would have 24.3 mm of block where it needs 25.5–27.6 mm: −1.2 to −3.3 mm
  (`CL-C5-PACK-STACK-MARGIN`). Every D-62 mark is aft of its limit, so nothing flies short today, but the stack
  rule must become per pack (CR-C5-21).
- **The 546 g pack has 0.7 mm at −0.036.** Any forward play eats it, so block B must be cut to fill the gap (26.2 mm)
  and the spacer stack must be solid. Trimmed onto the target in A3-R6a's items it would sit at −0.038 and be 1.4 mm
  short (`CL-C5-PACK-ROOM-MARGIN-TRIM`): fly the mark, not a balance trim.
- **R5 credited the 1 mm bond line as crush.** Block A has been epoxy since D-47; C5-R6 removes the credit, so the
  forward-stop section no longer matters (`CL-C5-PACK-ROOM-C3-STOP` = the full margin).
- No nose extension is needed (`CL-C5-NOSE-EXT` 0); box x slack 17 mm.

**Fin-tip fall (hover attitude):** the pack goes into D2's aft stop (85 N, strutted by D-69). **Cruise crash at
16 m/s** (≈ 70 J): no structure protects it; H3's LiPo post-crash procedure applies.

## Assumptions

| Id | Value | Status | Basis |
|---|---|---|---|
| `ASM-C5-D62-STATIONS` | 546 g −0.036, 551 g −0.034, 590 g −0.028 m | `UNVERIFIED` | A1 `CALC-A1-PACK-CASES` until A3 / D2 re-run |
| `ASM-C5-SIDE-DESIGN-D65` | 39.5 N | `PROPOSED` | C5-S1 39.30 N, drift cases 39.44 N, rounded up |
| `ASM-C5-PILOT-SPD-DN` | 1.0 m/s | `PROPOSED` | CR-C5-23 to F4 |
| `ASM-C5-F-PLATEAU-PROP` / `ASM-C5-PRECRUSH-PEAK` | 37.5 N / 1.0 | `PROPOSED` / `UNVERIFIED` | coupon |
| `ASM-C5-MU-GRASS` / `ASM-D5-PAD-MU` | 0.5 / 0.7 | `UNVERIFIED` | T-D5-PAD-MU |
| `ASM-C5-TD-DRIFT` / `ASM-C5-GUST-FACTOR` / `ASM-C5-PARK-SF` | 0.3 m/s / 1.4 / 1.5 | `UNVERIFIED` / `UNVERIFIED` / `PROPOSED` | logs; anemometer |
| `ASM-C5-PACK-G-MAX` | 100 g | `UNVERIFIED` | UN 38.3 T.4 / 1.5 |
| `ASM-C5-SPREADER-T` / `ASM-C5-DROP-GUARD` | 1.5 / 3 mm | `PROPOSED` | D2 practice; plateau scatter |

## Open issues

| Issue | Effect | Owner |
|---|---|---|
| n 6.60 at the lightest mass vs 6.6, coupon tolerance +2 % | n 6.73 with a strong cartridge | D5 / C1 (CR-C5-22) |
| Gate stroke 34.9 of 35 mm at 1.2 m/s; drift bottoms at 1.2 m/s | no margin beyond the 3 mm guard | F4 (CR-C5-23) |
| Crush stack 24.3 mm rule and pod params still on 503 / 550 / 680 g | stations and block lengths drift | A1, D2, A3 (CR-C5-21) |
| D5 has not published the D-65 shoe numbers | FEA runs on C5's overrides | D5 (CR-C5-20) |
| 546 g pack margin +0.7 mm at its mark | no forward play allowed | H3, D2 (S9) |
| 2.3 normal landings per cartridge | many swaps per field day | D5 (CR-D5-21) |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-C5-TILT-BOARD` | tilt board, four directions, each pack at its mark | tip-over, CG z and height |
| `T-C5-FOOT-RIG` | sled on one pre-crushed foot | plateau per cartridge type |
| `T-C5-AIRCRAFT-DROP` | 2.6 kg: level 0.073 m; pitch / roll pairs at 0.073 m; 10° corner drops at **45 mm** | stroke, n, `R-LANDING-IMPACT` |
| `T-C5-SHOE-SIDE-FAIL` | two D-65 shoes, +y and +z, to failure | ≥ 59.25 N |
| `T-C5-DRIFT-LOG` | 20 twin and aircraft landings | drift, sink, spool-down |
| `T-D5-COUPON`, `T-D5-PAD-MU`, `T-A3-SWING` | D5 / A3 inputs | plateau ±, μ, inertia |
