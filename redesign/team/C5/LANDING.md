# Landing and impact: K09-L fin-tip feet

Owner C5 (landing / impact). Status `PROPOSED`, revision **C5-R2**, 2026-11-09, at params A1-R2, the A3-R3 roll-up,
B3's R1 CG range (`CL-B3-CG-FWD/-TARGET/-AFT` 0.0499 / 0.0526 / 0.0553 m, CR-B3-11), D2's pod (`CL-D2-*`) and D5's
foot (`team/D5/feet_calc.py`). Every number comes from `python -I redesign/team/C5/landing_calc.py` (claims in
`team/C5/claims.json`; the script prints every case table). Hardware is D5's: a PETG shoe bonded on each fin TE tip,
a PETG piston with a neoprene pad splayed to z ±0.219 m, an XPS crush cartridge, 32 mm stroke today.

What changed since C5-R1: the CG moved 6.5 mm aft (B3), which helps tip-over and opens 21.5 mm ahead of the pack. A
planar landing simulation replaced the symmetric hand calculation. It shows that **D5's 32 mm stroke is too short
once the real CG offset and a tilted touchdown are included**. Section 3 gives the sizing D5 needs.

## Verdict

| Check | Result | Claim | Status |
|---|---|---|---|
| Tip-over at the B3 target CG, pod side | 32.8° vs 30° | `CL-C5-TIPOVER-R1` → `R-TIPOVER` | `UNVERIFIED` (+9 %) |
| Tip-over, worst flying CG (forward limit, 680 g pack) | 32.4° | `CL-C5-TIPOVER-WORST` | `UNVERIFIED` (+8 %) |
| Bound: forward limit with z_cg at +0.030 m | 30.8° | `CL-C5-TIPOVER-B3-CORNER` | `UNVERIFIED` (+3 %) |
| Landing broadside in a 5 m/s lull (10° error, 0.3 m/s drift) | wind limit 4.35 m/s | `CL-C5-V-LAND-BROADSIDE` | `FAIL` → land span into wind |
| Landing span into wind | wind limit 8.4 m/s (8.0 with 0.21 m fins, CR-B3-14) | `CL-C5-V-LAND-SPANWISE` → `R-WIND` | `UNVERIFIED` (+5 %) |
| Level 1.5 m/s landing, D5 foot today | 28.6 of 29 mm usable (rotates onto the pod-side pair) | `CL-C5-DYN-LEVEL-CUR` | `UNVERIFIED` (+1 %) |
| **Pad pair first (worst tilt ≈ 4°), D5 foot today** | **32.8 mm vs 29 mm usable: bottoms out** | `CL-C5-DYN-PAIR-CUR` → `R-LANDING-IMPACT` | **`FAIL`** → CR-C5-10 |
| Pad pair first, proposed foot (38 mm, biased cartridges) | 34.5 of 35 mm usable, n 5.5 | `CL-C5-DROP-PAIR-PITCH` | `UNVERIFIED` (+1 %) |
| Level free drop 0.115 m, proposed foot | 27.5 mm, n 5.84 | `CL-C5-DYN-LEVEL-FREE-PROP`, `CL-C5-DYN-N-LEVEL` | `UNVERIFIED` (+3 % on n) |
| Foot side load on the mat (μ 0.7) vs C1 case L4 (μ 0.5) | 23.0 vs 16.5 N | `CL-C5-FOOT-SIDE-LOAD` | `FAIL` vs C1's case → CR-C5-09 |
| Parked standing, pack out, on the mat | largest gust 5.1 m/s | `CL-C5-V-PARK-GUST` → `R-WIND` | `UNVERIFIED` (+1 %) |
| Crush room ahead of the pack (5 m/s nose-in, ≤ 100 g) | needs 26.4 mm (550 g), has 21.5 mm | `CL-C5-PACK-NOSE-ROOM` → `R-PACK-RETENTION` | `FAIL` → CR-C5-02 (10 mm nose extension) |

## 1. Stance tip-over

Ground plane at x = c + foot = 0.365 m. Narrow axis = tipping over a pad pair at z = ±z_pad (about y). The pod side
(+z) governs because the CG sits 17 mm above the chord plane: its arm is z_pad − z_cg. Flying cases have the pack slid
until the CG sits on B3's target or a limit (`CALC-C5-STANCE`).

| CG case | Mass kg | x_cg m | z_cg m | Pack x m | h m | Unsplayed z 0.19 ° | D5 pads, pod side ° | Wide ° |
|---|---|---|---|---|---|---|---|---|
| A3 R1 layout + D5 feet (pack 29 mm forward) | 2.160 | 0.0461 | 0.0167 | −0.0340 | 0.319 | 28.5 | 32.3 | 45.1 |
| **B3 target, 550 g** | 2.160 | 0.0526 | 0.0167 | −0.0087 | 0.312 | 29.0 | **32.8** | 45.7 |
| B3 target, 680 g / 503 g | 2.290 / 2.113 | 0.0526 | 0.0182 / 0.0161 | +0.0030 / −0.0144 | 0.312 | 28.8 / 29.1 | 32.6 / 32.9 | 45.7 |
| **B3 forward limit, 680 g** | 2.290 | 0.0499 | 0.0182 | −0.0059 | 0.315 | 28.6 | **32.4** | 45.4 |
| B3 aft limit, 550 g | 2.160 | 0.0553 | 0.0167 | +0.0018 | 0.310 | 29.2 | 33.0 | 45.9 |
| No pack (parked) | 1.610 | 0.0735 | 0.0077 | — | 0.291 | 32.0 | 35.8 | 47.7 |

- The unsplayed foot fails at every CG (28.3–29.2°, `CL-C5-TIPOVER-A1-R1-ZCG`). D5's splay is required.
- 33° (CR-A1-20) now needs a pivot at z 0.2196 m (`CL-C5-PAD-Z-FOR-33`), 1.6 mm beyond D5's 0.218 m. It is not
  needed: keep `requirements.tipover_min_deg` 30°, checked at the worst flying CG.
- CR-B3-14 (half-fins 0.21 m): keep the pad outer edge at z ±0.219 m. The splay shrinks from 29 mm to 9 mm, so
  tip-over and box height do not change and the flange overhang gets shorter.

## 2. Landing in wind: heading, drift, thrust, slope

Model as in C5-R1: touchdown tilted φ toward a pad line with horizontal CG speed v, pivot holds, plastic impact, sink
ignored (conservative). Lean from a flat plate, C_D90 1.28 (`ASM-B1-CD90`), at the 2.16 kg flying mass.

| Case (5 m/s card wind unless stated) | Lean ° | Drift allowed m/s | Wind limit m/s | Claim |
|---|---|---|---|---|
| Calm, 10° error | 0 | 0.88 | — | `CL-C5-DRIFT-ALLOW-CALM` |
| Broadside, lull at touchdown | 18.8 | 0.14 (< 0.3) | 4.35 | `CL-C5-DRIFT-ALLOW-LULL`, `CL-C5-V-LAND-BROADSIDE` |
| Span into wind (wingtip upwind), wide axis | 11.0 | 1.15 | 8.4 | `CL-C5-DRIFT-ALLOW-SPANWISE`, `CL-C5-V-LAND-SPANWISE` |

| Other limit | Value | Claim |
|---|---|---|
| Largest thrust fraction at contact that a 10° tilt survives | 0.72 W | `CL-C5-LAM-MAX` |
| Ground slope for a calm landing (10° error, 0.3 m/s drift) | 14.5° (card ≤ 5°) | `CL-C5-SLOPE-CALM` |
| Spanwise wind limit with 0.21 m half-fins (CR-B3-14) | 8.0 m/s (limit 8.0) | sensitivity run, not a claim |

## 3. Hard landing: dynamics and the sizing D5 needs

`CALC-C5-DROP-DYN` is a planar rigid-body model (pitch plane with I_yy, roll plane with I_zz). Each contact is two
feet with D5's crush law: ramp to 37.5 N, plateau 34.1 N, no rebound, stiff stop at the stroke. The design case is a
1.5 m/s sink with 2/3 W rotor lift (`ASM-C1-LAND-LIFT`), with touchdown tilts from −10° to +10° scanned in 1° steps.
Checks: the symmetric free drop gives 27.5 mm against the hand energy balance's 28.8 mm (`CL-C5-DYN-VALID`; the
sim's ramp absorbs a little more). A 4× smaller time step changes the governing stroke by 0.001 mm.

**Two effects the hand calculation missed.**
1. **CG offset.** With four equal constant-force feet, the 17 mm z_cg offset makes the net foot force pitch the
   aircraft onto the pod-side pair. Level landing: 28.6 mm on that pair, against 25.0 mm symmetric.
2. **Pair first.** The first pair stops only its share. The aircraft rotates and the second pair lands faster. The
   worst tilt is about 4°, not 10°. D5's 54 mm (all energy into two feet) is too pessimistic; 29 mm usable is too
   little.

| Case (design: 1.5 m/s, lift 2/3 W) | D5 foot today (32 mm, equal) | Proposed (38 mm, biased) | Claim |
|---|---|---|---|
| Usable stroke (stop − 3 mm guard) | 29.0 mm | 35.0 mm | `CL-C5-DYN-USABLE-CUR/-PROP` |
| Level | 28.6 mm | 23.8 mm | `CL-C5-DYN-LEVEL-CUR/-PROP` |
| Pad pair first, pitch, worst tilt | 32.8 mm, bottoms (`FAIL`) | 34.5 mm at −4° | `CL-C5-DYN-PAIR-CUR`, `CL-C5-DROP-PAIR-PITCH` |
| One fin first, roll, worst tilt | 30.5 mm | 30.5 mm at 8° | `CL-C5-DROP-PAIR-ROLL` |
| Peak n, level free drop 0.115 m / tilted design | 46 (bottoms) / — | 5.84 / 5.54 | `CL-C5-DYN-N-LEVEL/-TILTED` |
| Wing TE above ground at full stroke | 13 mm | 10 mm (with the 48 mm foot) | `CL-C5-TE-CLEAR-PROP` |
| Wingtip TE, worst roll landing | −6.5 mm | −3.5 mm: the corner cap touches | `CL-C5-WINGTIP-CLEAR-ROLL` |

More plateau force cannot fix the pair-first case: n is set by the level case with four feet. A two-stage cartridge
was tried (25 mm soft, then 1.3–1.7×) and it pushes n to 6.8–9. **Stroke is the fix.**

### Sizing for D5 (CR-C5-10)

| Item | Today | Required | Basis |
|---|---|---|---|
| Stroke (flange-to-sleeve gap) | 32 mm | **≥ 38 mm** | worst pair-first 34.5 mm + 3 mm guard; cartridge usable crush 0.55 × 77 = 42 mm is enough |
| Foot beyond the wing TE | 45 mm | **48 mm** (A1 param, CR-C5-11) | wing TE ≥ 10 mm off the ground at full stroke |
| Cartridge plateau, upper (pod side, UR/UL) feet | 34.1 N | **36.7 N** (×1.077: section 11 × 19.4 mm) | no net pitch moment in a level landing; same total, n unchanged |
| Cartridge plateau, lower (LR/LL) feet | 34.1 N | **31.4 N** (×0.923: section 11 × 16.6 mm) | as above; colour-mark the two cartridge types |
| Peak force per upper foot, limit / ultimate | 37.5 / 56.6 N | 40.4 / 60.5 N | 1.10 × plateau, × 1.5; D5's flange SF 1.33 drops to ≈ 1.25, bond SF 2.7 to ≈ 2.5 |
| Side load at the pad (μ 0.7 mat), limit / ultimate | — | 23.0 / 34.5 N | `CL-C5-FOOT-SIDE-LOAD`; piston-in-sleeve bearing at full stroke, shoe legs |
| Pad outer edge z | ±0.219 m | keep ±0.219 m (also with 0.21 m fins) | tip-over 32.4° worst; box height unchanged |
| Wingtip TE corner cap | none | ≤ 1 g TPU cap or 2 wraps of filament tape over 40 mm | roll landings at 6–10° touch it (CR-C5-04) |
| Landing mass | 39.1 g | ≈ 42.5 g `EST` (+0.85 g per foot: 6 mm more sleeve and skirt) | ≈ 2.5 g over the 40 g allocation → A1 reserve (CR-C5-11) |

### Drop tests (T-C5-FOOT-RIG, then T-C5-AIRCRAFT-DROP = C1's T-C1-FOOT-DROP)

| Drop | Height pad-to-floor | Pass | Claims |
|---|---|---|---|
| Rig, one foot, 0.70 kg sled (upper cartridge) / 0.60 kg (lower) | 0.115 m | sled ≤ 6.0 g (100 Hz), stroke ≤ 29 mm, no bond crack | `CL-C5-DROP-STROKE`, `-N` (hand) |
| Aircraft level ×2, no lift, 2.6 kg (sandbag of the weighed pack mass) | 0.115 m | CG ≤ 6.0 g; stroke ≤ 35 mm; upper and lower pairs within 3 mm of each other | `CL-C5-DYN-LEVEL-FREE-PROP`, `-N-LEVEL` |
| Aircraft pitch ±4°, roll 8° | **0.082 m** (`CL-C5-TEST-TILT-H`) | each pair's stroke within 3 mm of the model re-run at the measured height and tilt; TE clear except the corner cap | `CL-C5-DROP-PAIR-PITCH`, `-ROLL` |

A tilted drop from 0.115 m without rotor lift would need about 47 mm. The tilted drops therefore validate the model
at a lower height, and the validated model carries the design case. This is the reduced-energy approach of
14 CFR 23.725 (wing lift taken as 2/3 W), applied to rotor lift.

## 4. Stance rules for the flight card (to H3, CR-C5-06)

| # | Rule | Number behind it |
|---|---|---|
| S1 | Land on the mat (≥ 0.8 × 0.8 m, rubber on ply), level within 5° | slope room 14.5° calm; μ 0.7 |
| S2 | Final descent and touchdown with **a wingtip into the wind** | broadside limit 4.35 m/s; span into wind 8.4 m/s |
| S3 | Touch down in QLAND / QLOITER at ≤ 0.5 m/s | drift allowed 0.88 m/s calm, 1.15 m/s span into wind |
| S4 | Spin down at once after contact; never hold hover thrust on the pads | > 0.72 W tips a 10° tilt |
| S5 | Between flights **lay it flat** unless gusts ≤ 5 m/s, the pack is in and it stands on the mat; always lay it flat to change the pack; never leave it standing unattended | pack out: allowed gust 5.1 (mat) / 4.3 (grass) m/s |
| S6 | Lay flat pod up, **lower props turned spanwise first** | blade clearance +17 mm spanwise, −111 mm blade down; lifts at 10.8 m/s |
| S7 | Check the replace-mark groove after every landing | about 13 normal landings per cartridge |
| S8 | After a hard landing or tip-over: check shoe bonds, fin TE tips, wingtip caps, props, motor mounts, pod nose | crash path, section 5 |

## 5. Crash energy path

Order of failure, cheapest first. The pack, FC, spar and motor tubes must never fail first.

| Order | Element | Takes | Repair | Owner |
|---|---|---|---|---|
| 1 | XPS foot cartridge | 1.5 m/s landing, any tilt ≤ 10° (proposed foot) | swap, 3 min | D5 |
| 2 | Piston / pad, shoe bond; wingtip corner cap | beyond full stroke; roll landings ≥ 6° | printed spare, 10 min | D5 |
| 3 | Props | tip-over onto a prop pair, 4.6 J (`CL-C1-TIPOVER-ENERGY`) | field spares | E1 |
| 4 | Printed motor mount | fails before the tube (D-23) | printed spare | D3, C4 |
| 5 | Half-fin, wingtip TE | fall beyond the feet | re-cut, 1 day | D3, D1 |
| 6 | XPS wing core | major crash | re-cut, ≈ $20, 1–2 days | D1 |
| 7 | Pack crush block (nose-in) | 5 m/s, pack ≤ 100 g | cut a new block | D2 |
| never | Pack, FC, spar, motor tubes | — | — | D2, C3, F3 |

**Nose-in (cruise attitude, 5 m/s, `CALC-C5-CRASH`).** The n ≤ 100 g limit (`ASM-C5-PACK-G-MAX`, UN 38.3 T.4
150 g / 1.5) sets the crush length, whatever the foam: at least 24.3 mm of XPS. F-250 over the full bay section
(52 × 59 mm) behind a 1.5 mm spreader is the practical block.

| Pack (weighed) | Pack x on the B3 target m | Block force N / n | Block length mm | Room needed / available mm | Nose wall inside face needed m |
|---|---|---|---|---|---|
| 503 g | −0.0144 | 493 / 100 | 24.3 | 25.8 / 15.8 | −0.1102 |
| 550 g | −0.0087 | 527 / 97.7 | 24.9 | 26.4 / 21.5 | −0.1050 |
| 680 g | +0.0030 | 527 / 79.0 | 30.7 | 32.2 / 33.2 | −0.0992 |

The nose wall inside face is at −0.1002 m today. **Moving it forward 10 mm (pod nose −0.105 → −0.115 m) covers any
pack in the listed range** (`CL-C5-NOSE-EXT`); a weighed 550 g pack alone needs 4.8 mm. Box length slack with the
extension is 20 mm (`CL-C5-BOX-X-SLACK-NOSE`). This is a 10 mm shell extension, not the R1 request to move the
whole pod (B3 keeps the pod at −0.105). The block is the forward trim spacer: cut it to fill the gap at the
balanced station, and never put a PETG spacer ahead of the pack. Pack leads exit aft.

**Fin-tip fall (hover attitude).** The pack is driven aft into D2's aft stop (85 N ultimate, `CL-C1-PACK-CRASH-LOAD`).
The FC sits in the side channel, not behind the pack, so CR-C5-07 is answered. If the 1.5 mm, 25 mm-high stop wall
is held only at its base it reaches ≈ 54 MPa against 40 MPa for PETG. Bond it to the side guides as well (C3,
CR-C5-07).

**Cruise crash at 16 m/s** (≈ 87 J in the pack): no structure protects the pack. H3's LiPo post-crash procedure
applies.

## Assumptions

| Id | Value | Status | Basis |
|---|---|---|---|
| `ASM-C5-TD-DRIFT` | 0.3 m/s | `UNVERIFIED` | GPS-hold touchdown; twin logs (T-C5-DRIFT-LOG) |
| `ASM-C5-GUST-FACTOR` / `ASM-C5-PARK-SF` | 1.4 / 1.5 | `UNVERIFIED` / `PROPOSED` | open terrain at 2 m / unattended case |
| `ASM-C5-CL-FLAT` | 0.6 | `UNVERIFIED` | wing lying flat |
| `ASM-C5-PACK-G-MAX` | 100 g | `UNVERIFIED` | UN 38.3 T.4 / 1.5 (`SRC-C5-UN383`) |
| `ASM-C5-STROKE-PROP` / `ASM-C5-FOOT-PROP` | 38 / 48 mm | `PROPOSED` | section 3 |
| `ASM-C5-SPREADER-T` / `ASM-C5-NOSE-WALL` / `ASM-C5-DROP-GUARD` | 1.5 / 2 / 3 mm | `PROPOSED` | D2 practice; 10 % of the stroke |
| Planar model | frictionless pads, lift at the CG, rigid airframe | `UNVERIFIED` | validated by the tilted drops |

## Open issues

| Issue | Effect | Owner |
|---|---|---|
| D5 foot today bottoms in a pair-first landing (32.8 vs 29 mm) | fin tips and shoe bonds take the overload | D5, A1 (CR-C5-10, -11) |
| Proposed pitch case leaves 0.5 mm inside the guard; rests on the XPS plateau and lift 2/3 W | coupon and tilted drops decide | D5, C5 |
| Side load 23 N on the mat (C1 used 16.5 N) | C4's fin face stress +40 % | C1, C4 (CR-C5-09) |
| Pack crush room 21.5 vs 26.4 mm | nose-in crash overloads the pack | A1, D2, C3 (CR-C5-02) |
| The 680 g pack trims to x +0.003 m, 9.5 mm beyond D2's aft travel | trim not reachable with a heavy pack | D2, A1 (noted in CR-C5-02) |
| Span-into-wind heading needs yaw authority (CR-B3-12 cant) | rule S2 | F4, B3, H2 |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-C5-TILT-BOARD` | tilt board, four directions, pack at the target, forward-limit mark, out | tip-over, CG z and height |
| `T-C5-FOOT-RIG` | sled on one foot, 0.115 m | crush force and stroke per cartridge type |
| `T-C5-AIRCRAFT-DROP` | 2.6 kg aircraft: level 0.115 m; pitch ±4°, roll 8° at 0.082 m | dynamics claims, `R-LANDING-IMPACT` |
| `T-C5-DRIFT-LOG` | 20 twin and aircraft landings | drift and spool-down |
| `T-D5-PAD-MU`, `T-D5-COUPON`, `T-D5-REPLACE` | D5 inputs | pad μ, plateau, swap time |
