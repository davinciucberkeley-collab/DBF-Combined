# Landing and impact: K09-L fin-tip feet

Owner C5 (landing / impact). Status `PROPOSED`, revision **C5-R3**, 2026-11-09, at params **A1-R3** (feet 48 mm,
stroke ≥ 38 mm, half-fins 0.21 m, pod nose −0.115 m, box 0.54 m), A3's R3 roll-up (14:54 run), B3's CG range
(`CL-B3-CG-FWD/-TARGET/-AFT` 0.0499 / 0.0526 / 0.0553 m), D2's pod, C3's stops and D5's foot (`team/D5/feet_calc.py`,
not yet re-run at R3). Every number comes from `python -I redesign/team/C5/landing_calc.py` (claims in
`team/C5/claims.json`; the script prints every case table).

**What changed since C5-R2.**
1. A3's R3 roll-up moved the CG aft: 0.056 m with the pack at A3's station (−0.001). To fly on B3's target the
   pack slides to −0.0144 m. That takes 10 mm away from the crush block.
2. A3's pitch inertia moved between 0.030 and 0.042 kg·m² during this round. At 0.030 the R2 cartridges bottom.
   The R3 cartridges (pre-crushed, 37.5 N mean, bias 1.05) pass at both values.
3. C1 adopted μ 0.7 (CR-C5-09). The crush model now uses the real R3 nose (−0.115, 4.8 mm foam-board wall) and C3's
   3 mm forward stop, which breaks away into the block.

## Verdict

| Check | Result | Claim | Status |
|---|---|---|---|
| Tip-over, B3 target CG, pod side | 32.6° vs 30° | `CL-C5-TIPOVER-R1` → `R-TIPOVER` | `UNVERIFIED` (+9 %) |
| **Tip-over, worst flying CG** (forward limit, 680 g pack) | **32.2°** | `CL-C5-TIPOVER-WORST` | `UNVERIFIED` (+7 %) |
| Bound: forward limit with z_cg +0.030 m | 30.6° | `CL-C5-TIPOVER-B3-CORNER` | `UNVERIFIED` (+2 %) |
| Landing broadside, 5 m/s lull | wind limit 4.47 m/s | `CL-C5-V-LAND-BROADSIDE` | `FAIL` → wingtip into wind (S2) |
| Landing span into wind | 8.2 m/s vs 8.0 | `CL-C5-V-LAND-SPANWISE` → `R-WIND` | `UNVERIFIED` (+3 %) |
| Pad pair first, D5 foot today (32 mm, equal) | 33.1 vs 29 mm usable: bottoms | `CL-C5-DYN-PAIR-CUR` | `FAIL` → CR-C5-10 |
| **Pad pair first in pitch, 48 mm foot, R3 cartridges** | **31.5 of 35 mm** (34.6 at I_yy 0.030) | `CL-C5-DROP-PAIR-PITCH` → `R-LANDING-IMPACT` | `UNVERIFIED` (+10 %) |
| One fin first in roll, same foot | 28.0 of 35 mm | `CL-C5-DROP-PAIR-ROLL` | `UNVERIFIED` (+20 %) |
| Peak n, level free drop / tilted | 5.88 / 5.88 vs 6 | `CL-C5-DYN-N-LEVEL`, `-TILTED` | `UNVERIFIED` (+2 %) |
| Wing TE at full stroke | 10 mm | `CL-C5-TE-CLEAR-PROP` | `UNVERIFIED` (at the limit by design) |
| Foot side load on the mat | 20.4 N = C1's L4 | `CL-C5-FOOT-SIDE-LOAD` | `UNVERIFIED` (C1 adopted μ 0.7) |
| Parked standing, pack out, on the mat | largest gust 5.3 m/s | `CL-C5-V-PARK-GUST` → `R-WIND` | `UNVERIFIED` (+6 %) |
| **Crush room ahead of the 550 g pack, trimmed to the B3 target** | **needs 29.4 mm, has 25.8** | `CL-C5-PACK-NOSE-ROOM` → `R-PACK-RETENTION` | **`FAIL`** → CR-C5-12 |
| Same, worst pack (503 g) | −9.3 mm | `CL-C5-PACK-ROOM-MARGIN-WORST` | `FAIL` → CR-C5-12 |
| Same at A3's pack station (−0.004 m, before the R3 roll-up) | 29.4 vs 36.0 mm; 503 g +2.0 mm | earlier run this round | passes |

## 1. Stance tip-over

Ground plane at x = c + foot = 0.368 m. Narrow axis = tipping over a pad pair at z = ±0.218 m (`CL-D5-CONTACT-Z`).
The pod side (+z) governs because the CG sits 16 mm above the chord plane. Flying cases slide the pack until the CG
is on B3's target or a limit (`CALC-C5-STANCE`).

| CG case | Mass kg | x_cg m | z_cg m | Pack x m | h m | Unsplayed z 0.21 ° | D5 pads, pod side ° | Wide ° |
|---|---|---|---|---|---|---|---|---|
| A3 roll-up, pack at A3 station (not a flying case) | 2.314 | 0.0558 | 0.0162 | −0.0010 | 0.312 | 31.8 | 32.9 | 45.7 |
| **B3 target, 550 g** | 2.314 | 0.0526 | 0.0162 | −0.0144 | 0.315 | 31.6 | **32.6** | 45.4 |
| B3 target, 680 g / 503 g | 2.444 / 2.267 | 0.0526 | 0.0176 / 0.0156 | −0.0016 / −0.0207 | 0.315 | 31.4 / 31.6 | 32.4 / 32.7 | 45.4 |
| **B3 forward limit, 680 g** | 2.444 | 0.0499 | 0.0176 | −0.0112 | 0.318 | 31.2 | **32.2** | 45.2 |
| B3 forward limit, 503 g | 2.267 | 0.0499 | 0.0156 | −0.0327 (ahead of D2's stop −0.0302) | 0.318 | 31.4 | 32.5 | 45.2 |
| B3 aft limit, 550 g | 2.314 | 0.0553 | 0.0162 | −0.0032 | 0.313 | 31.8 | 32.8 | 45.7 |
| No pack (parked) | 1.764 | 0.0735 | 0.0078 | — | 0.295 | 34.5 | 35.5 | 47.4 |

- Tip-over passes at the worst flying CG. The 48 mm foot costs about 0.3° against R2. 33° would need a pivot at
  z 0.221 m: not needed.
- With 0.21 m half-fins even the unsplayed foot now reaches 31.2–31.8°. Keep D5's pads at z ±0.219 m anyway: the
  corner bound is only +2 %.
- A 503 g pack cannot reach the forward limit: its station would be 2.5 mm ahead of D2's forward stop (A3, A1).

## 2. Landing in wind

Same model as R2 (tilted touchdown, pivot holds, plastic impact). Flying mass 2.31 kg.

| Case (5 m/s card wind unless stated) | Lean ° | Drift allowed m/s | Wind limit m/s | Claim |
|---|---|---|---|---|
| Calm, 10° error | 0 | 0.87 | — | `CL-C5-DRIFT-ALLOW-CALM` |
| Broadside, lull at touchdown | 17.6 | 0.18 (< 0.3) | 4.47 | `CL-C5-DRIFT-ALLOW-LULL`, `CL-C5-V-LAND-BROADSIDE` |
| Span into wind, wide axis | 11.3 | 1.12 | 8.2 | `CL-C5-DRIFT-ALLOW-SPANWISE`, `CL-C5-V-LAND-SPANWISE` |

| Other limit | Value | Claim |
|---|---|---|
| Thrust fraction at contact that a 10° tilt survives | 0.71 W | `CL-C5-LAM-MAX` |
| Ground slope for a calm landing | 14.3° (card ≤ 5°) | `CL-C5-SLOPE-CALM` |

## 3. Hard landing and the cartridge sizing D5 needs

`CALC-C5-DROP-DYN` is a planar rigid-body model (pitch plane with I_yy, roll plane with I_zz), two feet per contact,
crush law ramp → plateau → stiff stop. Design case: 1.5 m/s sink with 2/3 W rotor lift, tilts −10° … +10° in 1°
steps. R3 adds a 0.25° re-scan around the worst tilt and a bias search (1.000–1.100 in 0.005 steps). Checks: the
symmetric free drop is 27.5 mm against the hand balance's 28.8 mm (`CL-C5-DYN-VALID`). A 4× smaller time step changes
the governing stroke by 0.002 mm.

| Case (design: 1.5 m/s, lift 2/3 W) | D5 today (32 mm, 34.1 N, peak 1.10, equal) | R3 proposal (38 mm, 37.5 N mean, pre-crushed, ×1.05 / ×0.95) | Claim |
|---|---|---|---|
| Usable stroke (stop − 3 mm guard) | 29.0 mm | 35.0 mm | `CL-C5-DYN-USABLE-CUR/-PROP` |
| Level, upper / lower pair | 28.9 / 19.5 mm | 23.1 / 20.2 mm | `CL-C5-DYN-LEVEL-CUR/-PROP` |
| Pad pair first, pitch, worst tilt | 33.1 mm, bottoms (`FAIL`) | **31.5 mm at 4°** | `CL-C5-DYN-PAIR-CUR`, `CL-C5-DROP-PAIR-PITCH` |
| One fin first, roll, worst tilt | 30.7 mm (`FAIL`) | 28.0 mm at −8° | `CL-C5-DROP-PAIR-ROLL` |
| Peak n, level free drop / tilted | 81 (bottoms) | 5.88 / 5.88 | `CL-C5-DYN-N-LEVEL/-TILTED` |
| Wing TE at full stroke / wingtip TE worst roll | 16 mm / −3.3 mm | 10 mm / −2.1 mm (corner cap) | `CL-C5-TE-CLEAR-PROP`, `-WINGTIP-CLEAR-ROLL` |

**Robustness.** The R2 cartridges (34.1 N, peak 1.10, bias 1.077) passed by 0.5 mm at I_yy 0.042. At 0.030 they
bottomed: 38.2 mm, n 27.6. The R3 cartridges give 31.5 mm at 0.042 and 34.6 mm at 0.030, n 5.88 at both. Plateau
scatter: −3 % → 32.6 mm, +3 % → n 6.06. Hence the −3 / +2 % coupon tolerance. Pre-crushing raises the usable plateau
10 % for the same peak n, because the 1.10 initial peak goes away. A 52 mm foot / 42 mm stroke is the fallback only
if `T-A3-SWING` measures I_yy < 0.030 kg·m² (box x slack −4 mm).

### Cartridge plateaus and loads for D5 (CR-C5-10, R3)

| Item | D5 today | Required (R3) | Claim / basis |
|---|---|---|---|
| Stroke (flange-to-sleeve gap) / foot beyond the TE | 32 / 45 mm | **≥ 38 / 48 mm** (D-30) | `ASM-C5-STROKE-PROP`, `P:cg.foot_height_m` |
| Cartridge treatment | none | **pre-crush 2 mm on a press**; 40 mm usable crush left of 42 | `ASM-C5-PRECRUSH-PEAK` (`UNVERIFIED`, coupon) |
| Plateau, upper feet UR/UL | 34.1 N | **39.4 N**, section 11 × **20.8** mm | `CL-C5-CART-PLATEAU-UPPER`, `-SECTION-UPPER` |
| Plateau, lower feet LR/LL | 34.1 N | **35.6 N**, section 11 × **18.8** mm | `CL-C5-CART-PLATEAU-LOWER`, `-SECTION-LOWER` |
| Bias upper / lower | 1 / 1 | **1.05 / 0.95**, colour-marked | `CL-C5-CART-BIAS-UPPER` (min. worst pitch stroke) |
| Coupon acceptance | — | mean force 5–35 mm within −3 / +2 % | `T-D5-COUPON` |
| Axial load per upper foot, limit / ultimate | 37.5 / 56.2 N | 39.4 / **59.1 N** | `CL-C5-CART-ULT-UPPER` (× `requirements.safety_factor_ult`) |
| Side load at the pad (μ 0.7), limit / ultimate | — | 20.4 / 30.5 N | `CL-C5-FOOT-SIDE-LOAD` |
| Pad outer edge z | ±0.219 m | keep | tip-over 32.2° worst |
| Wingtip TE corner cap | none | ≤ 1 g TPU cap or tape | CR-C5-04 |

### Drop tests

| Drop | Height pad-to-floor | Pass | Claims |
|---|---|---|---|
| Rig, one foot, 0.68 kg sled (upper) / 0.62 kg (lower), pre-crushed cartridge | 0.115 m | sled ≤ 6.0 g (100 Hz), no bond crack | `CL-C5-DROP-STROKE`, `-N` |
| Aircraft level ×2, no lift, 2.6 kg | 0.115 m | CG ≤ 6.0 g; stroke ≤ 35 mm; each pair within 3 mm of the model | `CL-C5-DYN-LEVEL-FREE-PROP`, `-N-LEVEL` |
| Aircraft pitch ±4°, roll 8° | **0.093 m** (`CL-C5-TEST-TILT-H`) | each pair within 3 mm of the model re-run; TE clear except the corner cap | `CL-C5-DROP-PAIR-PITCH`, `-ROLL` |

## 4. Stance rules for the flight card (to H3, CR-C5-06)

| # | Rule | Number behind it |
|---|---|---|
| S1 | Land on the mat (≥ 0.8 × 0.8 m, rubber on ply), level within 5° | slope room 14.3° calm; μ 0.7 |
| S2 | Final descent and touchdown with **a wingtip into the wind** | broadside limit 4.47 m/s; span into wind 8.2 m/s |
| S3 | Touch down in QLAND / QLOITER at ≤ 0.5 m/s | drift allowed 0.87 m/s calm, 1.12 m/s span into wind |
| S4 | Spin down at once after contact | > 0.71 W tips a 10° tilt |
| S5 | Between flights **lay it flat** unless gusts ≤ 5 m/s, pack in, on the mat; never leave it standing unattended | pack out: gust 5.3 (mat) / 4.5 (grass) m/s |
| S6 | Lay flat pod up, **lower props turned spanwise first** | +17 mm spanwise, −111 mm blade down; lifts at 11.3 m/s |
| S7 | Check the replace-mark groove after every landing | about 13 normal landings per cartridge |
| S8 | After a hard landing or tip-over: shoe bonds, fin TE tips, wingtip caps, props, mounts, pod nose and block | section 5 |

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
| 7 | Pack crush blocks + forward stop (nose-in) | 5 m/s, pack ≤ 100 g | cut new blocks, reprint the stop | D2, C3 |
| never | Pack, FC, spar, motor tubes | — | — | D2, C3, F3 |

**Nose-in at 5 m/s (`CALC-C5-CRASH`).** The pack must stay ≤ 100 g (`ASM-C5-PACK-G-MAX`). That limit, not the foam,
sets the length: ≥ 24.3 mm of XPS F-250 over the full bay section (52 × 59 mm). The R3 geometry, from the nose:
- nose wall inside face at −0.1102 m (−0.115 + 4.8 mm foam board);
- block A, 7 mm;
- C3's 3 mm forward stop, aft face at −0.1002. It breaks off at ~100 N and spreads into block A;
- block B behind a 1.5 mm spreader, up to the pack fore face.

The energies of the two blocks add.

| Pack (weighed) | Pack x on the B3 target m | Force N / n | Room avail. / needed mm | Margin, full-section stop / C3's 25 mm stop mm |
|---|---|---|---|---|
| 503 g | −0.0207 | 493 / 100 | 19.5 / 28.8 | **−9.3** / −13.1 |
| 550 g | −0.0144 | 527 / 97.7 | 25.8 / 29.4 | **−3.6** / −7.6 |
| 680 g | −0.0016 | 527 / 79.0 | 38.6 / 35.2 | +3.3 / −0.7 |

D-25's 10 mm extension was enough while the pack sat near −0.004 m. With that item list, the earlier run this round
gave +6.7 mm (550 g) and +2.0 mm (503 g). A3-R3's aft CG now pulls the trimmed pack 10 mm forward. **CR-C5-12:**
trim by moving the pod group forward about 10 mm (≈ −0.125), which keeps the pack's place in the pod (≈ +9.8 / +4 mm
`EST`). Otherwise extend the nose a further 9.3 mm. Either way the box x slack falls from 17 to about 7.7 mm.
**CR-C5-13:** the forward stop must span the bay section. A 25 mm-tall stop loses 3.8–4.0 mm of block length.

**Fin-tip fall (hover attitude).** The pack goes into D2's aft stop (85 N). CR-C5-07 still asks C3/D2 to bond the
aft stop wall to the side guides. **Cruise crash at 16 m/s** (≈ 70 J in a 550 g pack): no structure protects it; H3's
LiPo post-crash procedure applies.

## Assumptions

| Id | Value | Status | Basis |
|---|---|---|---|
| `ASM-C5-F-PLATEAU-PROP` / `ASM-C5-PRECRUSH-PEAK` | 37.5 N / 1.0 | `PROPOSED` / `UNVERIFIED` | n ≤ 6 level free drop; coupon |
| `ASM-C5-STROKE-PROP` / `ASM-C5-FOOT-PROP` | 38 / 48 mm | `PROPOSED` (adopted D-30) | section 3 |
| `ASM-C5-MU-GRASS` | 0.5 | `UNVERIFIED` | pad on grass; C1 moved its value to the mat |
| `ASM-C5-TD-DRIFT` / `ASM-C5-GUST-FACTOR` / `ASM-C5-PARK-SF` | 0.3 m/s / 1.4 / 1.5 | `UNVERIFIED` / `UNVERIFIED` / `PROPOSED` | logs; anemometer |
| `ASM-C5-PACK-G-MAX` | 100 g | `UNVERIFIED` | UN 38.3 T.4 / 1.5 |
| `ASM-C5-SPREADER-T` / `ASM-C5-DROP-GUARD` | 1.5 / 3 mm | `PROPOSED` | D2 practice; plateau scatter |
| Planar model | frictionless pads, lift at the CG, rigid airframe | `UNVERIFIED` | tilted drops validate it |

## Open issues

| Issue | Effect | Owner |
|---|---|---|
| A3-R3 CG 0.056 m at the pack station; trimmed pack eats the crush room | nose-in crash overloads the pack | A1, A3, B3 (CR-C5-12) |
| Forward stop 25 mm tall | block A under-used | C3, D2 (CR-C5-13) |
| I_yy moving 0.030–0.042 kg·m² in A3's runs | R3 cartridges pass at both; measure with `T-A3-SWING` | A3, H1 |
| D5 not re-run at R3 (23 drifting outputs) | foot CAD still 45 mm / 32 mm | D5 (CR-C5-10) |
| Pre-crush and plateau tolerance untested | n margin 2 % | D5, H1 (`T-D5-COUPON`) |
| 503 g pack cannot reach the forward CG limit (station ahead of the stop) | trim range | A3, D2 |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-C5-TILT-BOARD` | tilt board, four directions | tip-over, CG z and height |
| `T-C5-FOOT-RIG` | sled on one pre-crushed foot, 0.115 m | plateau per cartridge type |
| `T-C5-AIRCRAFT-DROP` | 2.6 kg: level 0.115 m; pitch ±4°, roll 8° at 0.093 m | dynamics claims, `R-LANDING-IMPACT` |
| `T-C5-DRIFT-LOG` | 20 twin and aircraft landings | drift and spool-down |
| `T-D5-COUPON`, `T-D5-PAD-MU`, `T-A3-SWING` | D5 / A3 inputs | plateau ±, μ, I_yy |
