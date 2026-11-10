# Landing and impact: K09-L fin-tip feet

Owner C5 (landing / impact). Status `PROPOSED`, revision **C5-R5**, 2026-11-10. Inputs: params **A1-R4a** (D-47 pod
nose −0.130; **D-59** aft stop 0.060 and per-pack flight stations 503 g −0.024, 550 g −0.018, 680 g −0.010), A3's
**R6** roll-up (2.323 kg basic, I_yy 0.0448 / I_zz 0.1674 kg·m²), B3's CG range as rebuilt on A3-R6
(`CL-B3-CG-FWD/-TARGET/-AFT` 0.0508 / 0.0529 / 0.0549 m), D2's **R5a** pod params (`subsystems/pod/params.json`:
block A 1 mm, forward stop 3 × 25 × 54 mm, `pack_x_per_pack_m`) and D5-R4's foot (`CL-D5-*`: stroke 38 mm, plateau
U 39.6 / L 35.4 N, mean 37.49 N, bias 1.056, peak = plateau, η 0.903, set 1.28 mm). Every number comes from
`python -I redesign/team/C5/landing_calc.py` (claims in `team/C5/claims.json`; the script prints every case table).
`build_graph.py` shows no C5 drift, crash or warning. Other roles' inputs were being re-run while C5 ran, so the last
digit of some numbers moves between runs. None of these changes crosses a limit.

**What changed since C5-R4.**
1. The `IndexError` in `CALC-C5-STANCE` stays fixed. The script finds the pack as the single power/energy row of
   A3's items (`PWR-001`) and stops with a clear message if that row is missing. The calc runs on A3-R6.
2. D-59 moved the flight stations aft (550 g −0.022 → −0.018, 680 g −0.014 → −0.010, 503 g −0.0245 → −0.024). The
   stance and crash checks read the stations from `pack_x_per_pack_m`, so both now use them. The claim ids keep
   "D47" because other roles cite them; the titles say D-59.
3. **Tip-over with the CG higher.** From the pre-D-47 bay to the D-59 550 g station the CG rises 4.1 mm (5.0 mm at the
   D-47 station). New claim `CL-C5-TIPOVER-STATION-PLUS5` adds a further 5 mm to the worst station case: 31.7°
   (+6 %). The +2 % corner bound (30.7°) sits at B3's forward limit, and no flying case can go past that limit.
4. Crash block, each pack at its D-59 mark in D2's R5a bay: +2.4 / +7.0 / +8.9 mm (503 / 550 / 680 g). New claims
   give the most forward station per pack (S9) and the block B cut length that fills the gap (CR-C5-14c).
5. D5-R4's cartridges re-run on A3-R6 inertia: pitch pair-first 31.5 of 35 mm, n 5.88. The "foot today" claims
   (`CL-C5-DYN-LEVEL-CUR`, `-PAIR-CUR`) stay cross-checks without `verifies` (CR-A2-21a). The lower cartridges are
   `GER-008-LR/LL` everywhere; no claim names `GER-003-LR/LL` (CR-A4-47).

## Verdict

| Check | Result | Claim | Status |
|---|---|---|---|
| Tip-over, B3 target CG, pod side | 32.3° vs 30° | `CL-C5-TIPOVER-R1` → `R-TIPOVER` | `UNVERIFIED` (+8 %) |
| **Tip-over, worst flying CG** (forward limit, 680 g) | **32.0°** | `CL-C5-TIPOVER-WORST` → `R-TIPOVER` | `UNVERIFIED` (+7 %) |
| **Tip-over, each pack at its D-59 station** (worst: 680 g at −0.010) | **32.1°** | `CL-C5-TIPOVER-D47` → `R-TIPOVER` | `UNVERIFIED` (+7 %) |
| CG rise / tip-over change, pre-D-47 bay → D-59 550 g station | +4.1 mm / −0.34° | `CL-C5-D47-CG-RISE`, `-TIP-CHANGE` | `MODELLED` |
| Worst station with the CG a further 5 mm higher | 31.7° | `CL-C5-TIPOVER-STATION-PLUS5` | `UNVERIFIED` (+6 %) |
| Bound: forward limit with z_cg +0.030 m | 30.7° | `CL-C5-TIPOVER-B3-CORNER` | `UNVERIFIED` (+2 %) |
| Landing broadside, 5 m/s lull | wind limit 4.44 m/s | `CL-C5-V-LAND-BROADSIDE` | `FAIL` → land with a wingtip into the wind (S2) |
| Landing span into wind | 8.3 m/s vs 8.0 | `CL-C5-V-LAND-SPANWISE` → `R-WIND` | `UNVERIFIED` (+3 %) |
| **Pad pair first in pitch, D5-R4 cartridges as delivered** | **31.5 of 35 mm** | `CL-C5-DYN-PAIR-CUR` (cross-check) | `UNVERIFIED` (+10 %) |
| Same, C5 design case (bias 1.055) | 31.6 of 35 mm | `CL-C5-DROP-PAIR-PITCH` → `R-LANDING-IMPACT` | `UNVERIFIED` (+10 %) |
| One fin first in roll | 27.9 of 35 mm | `CL-C5-DROP-PAIR-ROLL` → `R-LANDING-IMPACT` | `UNVERIFIED` (+20 %) |
| Peak n, level free drop / tilted | 5.88 / 5.88 vs 6 | `CL-C5-DYN-N-LEVEL`, `-TILTED`, `-N-CUR` | `UNVERIFIED` (+2 %) |
| Wing TE at full stroke / wingtip TE worst roll | 10 mm / +2.3 mm | `CL-C5-TE-CLEAR-PROP`, `-WINGTIP-CLEAR-ROLL` | `UNVERIFIED` (keep the corner cap) |
| Normal landings per cartridge | 2.3 vs ≥ 5 | `CL-C5-LANDINGS-PER-CARTRIDGE` | `FAIL` → D5 (CR-D5-21) |
| Foot side load on the mat | 22.9 N = C1's L4 | `CL-C5-FOOT-SIDE-LOAD` | `UNVERIFIED` |
| Parked standing, pack out, on the mat | largest gust 5.3 m/s | `CL-C5-V-PARK-GUST` → `R-WIND` | `UNVERIFIED` (+6 %) |
| **Crush room ahead of the pack, worst pack at its D-59 station** | **+2.4 mm** (503 g) | `CL-C5-PACK-ROOM-MARGIN-WORST` → `R-PACK-RETENTION` | `UNVERIFIED` |
| Crush room, 550 g at −0.018 | needs 30.2 mm, has 37.2 | `CL-C5-PACK-NOSE-ROOM` → `R-PACK-RETENTION` | `UNVERIFIED` (+19 %) |
| Box x slack with the R5 nose | 2 mm | `CL-C5-BOX-X-SLACK-NOSE` → `R-TRANSPORT` | `UNVERIFIED` |

## 1. Stance tip-over

Ground plane at x = c + foot = 0.368 m. The narrow axis tips over a pad pair at z = ±0.218 m (`CL-D5-CONTACT-Z`).
The pod side (+z) governs because the CG sits 18–20 mm above the chord plane. A3-R6's items carry the D-47 bay with
the 550 g pack at the −0.022 datum. Each flying case either slides the pack until the CG sits on a B3 line or puts
the pack at its D-59 flight-card station.

| CG case | Mass kg | x_cg m | z_cg m | Pack x m | h m | Unsplayed ° | D5 pads, pod side ° | Wide ° |
|---|---|---|---|---|---|---|---|---|
| Pre-D-47 bay, pack −0.001 (not a flying case) | 2.323 | 0.0577 | 0.0185 | −0.0010 | 0.310 | 31.7 | 32.7 | 45.9 |
| A3-R6 as listed (pack at the −0.022 datum) | 2.323 | 0.0522 | 0.0185 | −0.0220 | 0.316 | 31.2 | 32.3 | 45.4 |
| **B3 target, 550 g** | 2.323 | 0.0529 | 0.0185 | −0.0211 | 0.315 | 31.3 | **32.3** | 45.4 |
| B3 target, 680 g / 503 g | 2.453 / 2.276 | 0.0529 | 0.0201 / 0.0179 | −0.0069 / −0.0280 | 0.315 | 31.1 / 31.4 | 32.1 / 32.4 | 45.4 |
| **B3 forward limit, 680 g** | 2.453 | 0.0508 | 0.0201 | −0.0142 | 0.317 | 30.9 | **32.0** | 45.3 |
| B3 forward limit, 503 g | 2.276 | 0.0508 | 0.0179 | −0.0371 | 0.317 | 31.2 | 32.3 | 45.3 |
| B3 aft limit, 550 g | 2.323 | 0.0549 | 0.0185 | −0.0125 | 0.313 | 31.5 | 32.5 | 45.6 |
| D-59 station, 503 g (−0.024) | 2.276 | 0.0537 | 0.0179 | −0.0240 | 0.314 | 31.4 | 32.5 | 45.5 |
| D-59 station, 550 g (−0.018) | 2.323 | 0.0536 | 0.0185 | −0.0180 | 0.314 | 31.3 | 32.4 | 45.5 |
| **D-59 station, 680 g (−0.010)** | 2.453 | 0.0520 | 0.0201 | −0.0100 | 0.316 | 31.0 | **32.1** | 45.4 |
| No pack (parked) | 1.773 | 0.0758 | 0.0092 | — | 0.292 | 34.5 | 35.5 | 47.6 |

- **CG height in the stance (CR-A3-22, D-47).** The D-47 bay raised the CG 5.0 mm at the −0.022 datum. The D-59
  station for the 550 g pack gives back 0.9 mm, so the net rise is 4.1 mm. It costs 0.34° on the pod side. Every
  flying case passes with at least 2.0° to spare.
- **A further 5 mm higher** (roll-up error, a heavier nose, nose ballast): the worst station case falls to 31.7°
  (+6 %, `CL-C5-TIPOVER-STATION-PLUS5`). Each mm of CG height costs about 0.08°.
- The +2 % corner bound (30.7°) combines the forward limit with the top of the z range. The CG may not fly ahead of
  B3's forward limit, so no flying case sits higher than this bound. The 680 g pack at its D-59 station is 1.2 mm aft
  of the limit.
- 33° would need the pivot at z 0.223 m. That is not needed, so keep D5's pads at ±0.218 m.
- The unsplayed foot reaches 30.9° (+3 %), but it is a reference case only. Fly D5's splayed pads.

## 2. Landing in wind

Same model as R3 (tilted touchdown, pivot holds, plastic impact). Flying mass 2.32 kg. A3-R6 inertia.

| Case (5 m/s card wind unless stated) | Lean ° | Drift allowed m/s | Wind limit m/s | Claim |
|---|---|---|---|---|
| Calm, 10° error | 0 | 0.85 | — | `CL-C5-DRIFT-ALLOW-CALM` |
| Broadside, lull at touchdown | 17.6 | 0.17 (< 0.3) | 4.44 | `CL-C5-DRIFT-ALLOW-LULL`, `CL-C5-V-LAND-BROADSIDE` |
| Span into wind, wide axis | 11.2 | 1.12 | 8.3 | `CL-C5-DRIFT-ALLOW-SPANWISE`, `CL-C5-V-LAND-SPANWISE` |

| Other limit | Value | Claim |
|---|---|---|
| Thrust fraction at contact that a 10° tilt survives | 0.71 W (vs 0.667 assumed) | `CL-C5-LAM-MAX` |
| Ground slope for a calm landing | 14.0° (card ≤ 5°) | `CL-C5-SLOPE-CALM` |

## 3. Hard landing and the D5-R4 cartridges

`CALC-C5-DROP-DYN` is a planar rigid-body model: the pitch plane with I_yy, the roll plane with I_zz, two feet per
contact, and a crush law of ramp → plateau → stiff stop. Design case: 1.5 m/s sink with 2/3 W rotor lift, tilts from
−10° to +10° in 1° steps, a 0.25° re-scan round the worst tilt, and a bias search from 1.000 to 1.100 in 0.005 steps.
Checks: the symmetric free drop strokes 24.9 mm against the hand balance's 26.2 mm (`CL-C5-DYN-VALID`), and a 4×
smaller time step changes the governing stroke by 0.002 mm.

| Case (design: 1.5 m/s, lift 2/3 W) | **D5-R4 as delivered** (38 mm, U 39.6 / L 35.4 N, bias 1.056) | C5 optimum (37.5 N mean, bias 1.055) | Claim |
|---|---|---|---|
| Usable stroke (stop − 3 mm guard) | 35.0 mm | 35.0 mm | `CL-C5-DYN-USABLE-CUR/-PROP` |
| Level, upper pair (governs) | 23.5 mm | 23.6 mm | `CL-C5-DYN-LEVEL-CUR/-PROP` |
| Pad pair first, pitch, worst tilt (−4°) | **31.5 mm** | 31.6 mm | `CL-C5-DYN-PAIR-CUR`, `CL-C5-DROP-PAIR-PITCH` |
| One fin first, roll, worst tilt (−7°) | 27.9 mm | 27.9 mm | `CL-C5-DROP-PAIR-ROLL` |
| Peak n, level free drop / tilted | 5.88 / 5.88 | 5.88 / 5.88 | `CL-C5-DYN-N-CUR`, `-N-LEVEL/-TILTED` |
| Wing TE at full stroke / wingtip TE worst roll | 10 mm / +2.3 mm | same | `CL-C5-TE-CLEAR-PROP`, `-WINGTIP-CLEAR-ROLL` |

**D5-R4 meets C5-R3's cartridge request.** The worst stroke differs from the optimum by 0.03 mm. At A3-R6's I_yy
(0.0448 kg·m²) the optimum bias stays 1.055 (1.050 at R3), so D5's 7/32 in bore is now the better choice. With
pre-crushed cartridges the n margin is 2 %. The coupon tolerance stays at −3 / +2 %.

**Wingtip corner.** With A3-R6's I_zz the wingtip TE corner clears by 2.3 mm in the worst roll landing; at R3 it hit
by 2.1 mm. That margin is inside the model's accuracy, so keep the ≤ 1 g corner caps (CR-C5-04, `GER-007`).

**Normal landings per cartridge: 2.3 (`FAIL` against 5).** D5's permanent set is 1.28 mm per 0.5 m/s landing. The
fix is D5's (CR-D5-21: move the replace mark, or keep normal touchdowns under the 0.32 m/s no-set speed). Until
then the flight card must say "check the groove after every landing; swap at the mark" (S7), with 16 spares of each
type in the kit.

### Cartridge numbers for D5 (closed by D5-R4)

| Item | D5-R4 | C5 requirement | Claim / basis |
|---|---|---|---|
| Stroke / foot beyond the TE | 38 / 48 mm | ≥ 38 / 48 mm | `CL-D5-STROKE-AVAIL`, `P:cg.foot_height_m` |
| Pre-crush | 1 mm per segment, both segments | removes the initial peak | `ASM-C5-PRECRUSH-PEAK` (`UNVERIFIED`, coupon) |
| Plateau upper UR/UL (`GER-003`) | 39.6 N | 39.6 N | `CL-C5-CART-PLATEAU-UPPER` |
| Plateau lower LR/LL (`GER-008`) | 35.4 N | 35.4 N | `CL-C5-CART-PLATEAU-LOWER` |
| Section, upper / lower (y 17.3 mm) | 13.3 mm, solid / 5.56 mm bore | 13.3 / 11.9 mm equivalent z | `CL-C5-CART-SECTION-UPPER/-LOWER` |
| Ultimate axial load, upper foot | 59.4 N | 59.3 N | `CL-C5-CART-ULT-UPPER` |
| Side load at the pad (μ 0.7), limit | — | 22.9 N | `CL-C5-FOOT-SIDE-LOAD` |
| Coupon acceptance | — | mean force 5–35 mm within −3 / +2 % | `T-D5-COUPON` |

### Drop tests

| Drop | Height pad-to-floor | Pass | Claims |
|---|---|---|---|
| Rig, one foot, 0.69 kg sled (upper) / 0.61 kg (lower), pre-crushed | 0.115 m | sled ≤ 6.0 g (100 Hz), no bond crack | `CL-C5-DROP-STROKE`, `-N` |
| Aircraft level ×2, no lift, 2.6 kg | 0.115 m | CG ≤ 6.0 g; stroke ≤ 35 mm; each pair within 3 mm of the model | `CL-C5-DYN-LEVEL-FREE-PROP`, `-N-LEVEL` |
| Aircraft pitch ±4°, roll 8° | **0.098 m** (`CL-C5-TEST-TILT-H`) | each pair within 3 mm of the re-run model; TE clear except the corner cap | `CL-C5-DROP-PAIR-PITCH`, `-ROLL` |

## 4. Stance rules for the flight card (to H3, CR-C5-06)

| # | Rule | Number behind it |
|---|---|---|
| S1 | Land on the mat (≥ 0.8 × 0.8 m, rubber on ply), level within 5° | slope room 14.0° calm; μ 0.7 |
| S2 | Final descent and touchdown with **a wingtip into the wind** | broadside limit 4.44 m/s; span into wind 8.3 m/s |
| S3 | Touch down in QLAND / QLOITER at ≤ 0.5 m/s | drift allowed 0.85 m/s calm, 1.12 m/s span into wind |
| S4 | Spin down at once after contact | > 0.71 W tips a 10° tilt |
| S5 | Between flights **lay it flat** unless gusts ≤ 5 m/s, pack in, on the mat; never leave it standing unattended | pack out: gust 5.3 (mat) / 4.5 (grass) m/s |
| S6 | Lay flat pod up, **lower props turned spanwise first** | +17 mm spanwise, −111 mm blade down; lifts at 11.3 m/s |
| S7 | Check the replace-mark groove **after every landing** | 2.3 normal landings per cartridge at D5-R4 |
| S8 | After a hard landing or tip-over: shoe bonds, fin TE tips, wingtip caps, props, mounts, pod nose and block | section 5 |
| S9 | **Pack at its D-59 mark only** (503 g −0.024, 550 g −0.018, 680 g −0.010), block B cut to fill the gap; **never forward of** −0.0264 (503 g), −0.0250 (550 g), −0.0189 m (680 g) | `CL-C5-PACK-X-FWD-MAX-*`, section 5 |

## 5. Crash energy path

Order of failure, cheapest first. The pack, FC, spar and motor tubes must never fail first.

| Order | Element | Takes | Repair | Owner |
|---|---|---|---|---|
| 1 | XPS foot cartridge | 1.5 m/s landing, any tilt ≤ 10° | swap, 3 min | D5 |
| 2 | Piston / pad, shoe bond; wingtip corner cap | beyond full stroke; roll landings ≥ 6° | printed spare, 10 min | D5 |
| 3 | Props | tip-over onto a prop pair | field spares | E1 |
| 4 | Printed motor mount | fails before the tube (D-23) | printed spare | D3, C4 |
| 5 | Half-fin, wingtip TE | fall beyond the feet | re-cut, 1 day | D3, D1 |
| 6 | XPS wing core | major crash | re-cut, 1–2 days | D1 |
| 7 | Pack crush block B + forward stop (nose-in) | 5 m/s, pack ≤ 100 g | cut a new block, reprint the stop | D2, C3 |
| never | Pack, FC, spar, motor tubes | — | — | D2, C3, F3 |

**Nose-in at 5 m/s (`CALC-C5-CRASH`, D2's R5a bay, D-59 stations).** The pack must stay at or below 100 g
(`ASM-C5-PACK-G-MAX`). The R5 stack, from the nose:
- nose shell at −0.130, nose wall inside face at −0.1252 (4.8 mm foam board);
- block A, 1.0 mm (`P:nose_block_l_m`). At R5 it is only a filler;
- forward stop, 3 × 25 × 54 mm, aft face at **−0.1212**;
- block B (XPS F-250, full bay section 52 × 56.9 mm), then a 1.5 mm spreader, then the pack fore face.

| Pack (weighed) | Station (D-59 mark) | Force N / n | Block B needed (+ spreader) | Gap available | **Margin** | With D2's 25 mm stop | Most forward station that keeps the block | Block B cut to fill |
|---|---|---|---|---|---|---|---|---|
| 503 g | −0.024 | 493 / 100 | 24.3 (24.8) mm | 27.2 mm | **+2.4 mm** | +1.9 mm | −0.0264 | 25.7 mm |
| 550 g | −0.018 | 509 / 94 | 25.7 (26.2) mm | 33.2 mm | **+7.0 mm** | +6.4 mm | −0.0250 | 31.7 mm |
| 680 g | −0.010 | 509 / 76 | 31.8 (32.3) mm | 41.2 mm | **+8.9 mm** | +8.3 mm | −0.0189 | 39.7 mm |

Claims: `CL-C5-PACK-ROOM-MARGIN-503/-550/-680`, `CL-C5-BLOCK-L-503`, `CL-C5-BLOCK-L`, `CL-C5-BLOCK-L-680`,
`CL-C5-PACK-X-FWD-MAX-503/-550/-680`, `CL-C5-BLOCK-FILL-503/-550/-680` (each fill is at least the length that pack
needs: +6 / +23 / +25 %), `CL-C5-PACK-ROOM-C3-STOP` +1.9 mm.

- **D-47 and D-59 keep the crush block whole.** CR-C5-12 stays closed: D-47 superseded it, because the bay moved with
  the nose. No further nose extension is needed (`CL-C5-NOSE-EXT` 0), and the box x slack is 2 mm.
- **D-59 only helps.** Moving a pack aft lengthens block B's gap by the same amount: 550 g +4.0 mm, 680 g +4.0 mm,
  503 g +0.5 mm. The aft stop at 0.060 plays no part in the nose-in case.
- **Cut block B to fill the gap** from the stop to the spreader: 25.7 / 31.7 / 39.7 mm for 503 / 550 / 680 g. That
  is the pod note's 39.7 mm stop-to-stop room minus each spacer stack and the spreader. The pack then cannot slide
  forward. MASS-CG.md lists the 503 g pack with 1.4 mm of play at −0.0254; even there the margin is +1.0 mm.
- **Trimming the pack forward eats the block.** Slid onto the B3 target (−0.0280), the 503 g pack is 1.5 mm short
  (`CL-C5-PACK-ROOM-MARGIN-TRIM`). Fly it at its D-59 mark (−0.024, CG 0.0537 m, inside the range). Flight-card
  rule S9.
- **CR-C5-13 stays withdrawn, and C3 and D2 own it.** Block A is 1 mm at R5, so a full-section forward stop gains
  only 0.5 mm, and all three packs pass with D2's 25 mm stop. C3 has declined it (keep the 4 g), and C5 agrees.

**Fin-tip fall (hover attitude).** The pack goes into D2's aft stop (85 N). CR-C5-07 still asks C3/D2 to bond the
aft stop wall to the side guides. **Cruise crash at 16 m/s** (≈ 70 J in a 550 g pack): no structure protects it; H3's
LiPo post-crash procedure applies.

## Assumptions

| Id | Value | Status | Basis |
|---|---|---|---|
| `ASM-C5-PRE-D47` | pack −0.001, kit +21 mm, nose +15 mm | `PROPOSED` | only for the CG-rise comparison |
| `ASM-C5-F-PLATEAU-PROP` / `ASM-C5-PRECRUSH-PEAK` | 37.5 N / 1.0 | `PROPOSED` / `UNVERIFIED` | n ≤ 6 level free drop; coupon |
| `ASM-C5-STROKE-PROP` / `ASM-C5-FOOT-PROP` | 38 / 48 mm | `PROPOSED` (adopted D-30) | section 3 |
| `ASM-C5-MU-GRASS` | 0.5 | `UNVERIFIED` | pad on grass |
| `ASM-C5-TD-DRIFT` / `ASM-C5-GUST-FACTOR` / `ASM-C5-PARK-SF` | 0.3 m/s / 1.4 / 1.5 | `UNVERIFIED` / `UNVERIFIED` / `PROPOSED` | logs; anemometer |
| `ASM-C5-PACK-G-MAX` | 100 g | `UNVERIFIED` | UN 38.3 T.4 / 1.5 |
| `ASM-C5-SPREADER-T` / `ASM-C5-DROP-GUARD` | 1.5 / 3 mm | `PROPOSED` | D2 practice; plateau scatter |
| Planar model | frictionless pads, lift at the CG, rigid airframe | `UNVERIFIED` | tilted drops validate it |

## Open issues

| Issue | Effect | Owner |
|---|---|---|
| 2.3 normal landings per cartridge (set 1.28 mm) | many cartridge swaps per field day | D5 (CR-D5-21) |
| D2's `CL-D2-*` and `CALC-D2-NOSE-EXT` should read the D-59 stations and C5's per-pack block lengths, not the B3-target trim stations | D2's nose-extension numbers can drift for no real reason | D2 (CR-C5-14) |
| 503 g margin +2.4 mm at its mark; −1.5 mm if trimmed onto the B3 target | pack overload in a nose-in crash if the pack sits forward of its mark | H3, D2 (S9, CR-C5-14) |
| Pre-crush and plateau tolerance untested | n margin 2 % | D5, H1 (`T-D5-COUPON`) |
| Wingtip TE corner +2.3 mm in the worst roll landing | inside the model's accuracy | D5 (keep `GER-007`) |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-C5-TILT-BOARD` | tilt board, four directions, each pack at its mark | tip-over, CG z and height |
| `T-C5-FOOT-RIG` | sled on one pre-crushed foot, 0.115 m | plateau per cartridge type |
| `T-C5-AIRCRAFT-DROP` | 2.6 kg: level 0.115 m; pitch ±4°, roll 8° at 0.098 m | dynamics claims, `R-LANDING-IMPACT` |
| `T-C5-DRIFT-LOG` | 20 twin and aircraft landings | drift and spool-down |
| `T-D5-COUPON`, `T-D5-PAD-MU`, `T-A3-SWING` | D5 / A3 inputs | plateau ±, μ, I_yy |
