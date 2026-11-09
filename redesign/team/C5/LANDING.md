# Landing and impact: K09-L fin-tip feet

Owner C5 (landing / impact). Status `PROPOSED`, revision C5-R1, 2026-11-09, at params A1-R2, A3-R3 roll-up and
D5's foot (`team/D5/feet_calc.py`). Every number comes from `python -I redesign/team/C5/landing_calc.py`
(claims in `team/C5/claims.json`, case tables printed by the script). The hardware is D5's: a PETG shoe bonded on
each fin TE tip, a PETG piston with a neoprene pad splayed to z = ±0.219 m, and an XPS crush cartridge, 32 mm stroke.

## Verdict

| Check | Result | Claim | Status |
|---|---|---|---|
| Tip-over at the R1 CG, unsplayed 45 mm feet (CR-A3-10) | 28.3° vs 30°: A1's 30.6° ignores the CG z offset (+0.017 m) | `CL-C5-TIPOVER-A1-R1-ZCG` | `FAIL` (that foot is superseded) |
| Tip-over at the R1 CG, D5 splayed pads, toward the pod | 32.3° vs 30° | `CL-C5-TIPOVER-R1` → `R-TIPOVER` | `UNVERIFIED` (+8 %) |
| Worst flying CG (pack slid forward 30 mm) | 31.6° | `CL-C5-TIPOVER-WORST` | `UNVERIFIED` (+5 %) |
| B3 range corner (x 0.040, z +0.030 m) | 30.05° | `CL-C5-TIPOVER-B3-CORNER` | `UNVERIFIED` (+0.2 %) |
| Broadside landing in a 5 m/s lull with 10° error and 0.3 m/s drift | needs 37.1°; broadside wind limit 4.3 m/s | `CL-C5-V-LAND-BROADSIDE` | `FAIL` → land span into wind |
| Span-into-wind landing | wind limit 8.3 m/s (≥ 8 m/s survive case) | `CL-C5-V-LAND-SPANWISE` → `R-WIND` | `UNVERIFIED` (+4 %) |
| Drop test 1.5 m/s at 2.6 kg, no rotor lift | 0.115 m drop, n 5.88, stroke 28.8 of 32 mm | `CL-C5-DROP-N`, `CL-C5-DROP-STROKE` → `R-LANDING-IMPACT` | `UNVERIFIED` (+2 % on n) |
| D5 foot vs the "≥ 40 mm stroke" text | 4.10 J capacity vs 3.06 J for 40 mm at η 0.5 | `CL-C5-FOOT-ENERGY` | `UNVERIFIED` (+34 %) |
| Parked standing, pack out, on the mat | largest gust 5.1 m/s (factor 1.5) | `CL-C5-V-PARK-GUST` → `R-WIND` | `UNVERIFIED` (+1 %) |
| Crush room ahead of the pack (5 m/s nose-in, ≤ 100 g) | needs 26 mm, has 1 mm | `CL-C5-PACK-NOSE-ROOM` → `R-PACK-RETENTION` | `FAIL` → CR-C5-02 |

**Splaying the feet passes the 30° requirement at every flying CG; the 33° target in CR-A1-20 is not reached
(32.3°) and is not needed.** The lever that matters is the landing heading. In 5 m/s the broadside lean is 18.8° at
the real flying mass (2.16 kg), and a lull with a 10° error leaves no room for drift. With a wingtip pointed into
the wind the lean is 11° and acts on the 45° wide axis, and the narrow axis only needs 18.3°. The flight card
carries that rule.

## 1. Stance tip-over (CR-A3-10)

Ground plane at x = c + foot = 0.365 m. Narrow axis = tipping over a pad pair at z = ±z_pad (about y, I_yy).
The pod side (+z) is critical because the CG sits 17 mm above the chord plane, so its arm is z_pad − z_cg.

| CG case | Mass kg | x_cg m | z_cg m | h m | Unsplayed z 0.19 ° | D5 pads, pod side ° | D5, other side ° | Wide ° |
|---|---|---|---|---|---|---|---|---|
| R1 A3 roll-up (feet 4 × 6 g) | 2.145 | 0.0440 | 0.0168 | 0.321 | 28.3 | 32.1 | 36.2 | 44.9 |
| R1 + D5 feet (39 g) | 2.160 | 0.0461 | 0.0167 | 0.319 | 28.5 | **32.3** | 36.4 | 45.1 |
| Pack 680 g | 2.290 | 0.0416 | 0.0182 | 0.323 | 28.0 | 31.7 | 36.1 | 44.7 |
| Pack 503 g | 2.113 | 0.0479 | 0.0161 | 0.317 | 28.7 | 32.5 | 36.4 | 45.3 |
| Pack slid forward 0.03 m | 2.160 | 0.0382 | 0.0167 | 0.327 | 27.9 | **31.6** | 35.7 | 44.4 |
| Pack slid aft 0.03 m | 2.160 | 0.0541 | 0.0167 | 0.311 | 29.1 | 32.9 | 37.0 | 45.8 |
| No pack (parked) | 1.610 | 0.0735 | 0.0077 | 0.291 | 32.0 | 35.8 | 37.8 | 47.7 |

- A1 (`CL-A1-TIPOVER`, 30.6°) and D5 (`CL-D5-TIPOVER-NARROW`, 34.2°) both use z_cg = 0. With the CG offset the
  values are 28.3° and 32.3°. CR-C5-01 asks both to subtract z_cg.
- The 33° target needs a pivot at z 0.224 m (`CL-C5-PAD-Z-FOR-33`): +6 mm of splay per side, which takes 11.6 mm
  of the 12 mm box-height slack (`CL-D5-BOX-SLACK`). It buys 0.7°. C5 retires the target and keeps
  `requirements.tipover_min_deg` = 30°, now checked with z_cg at the worst flying CG.
- A fully crushed foot lowers h by 32 mm and raises every angle by 2–3°, so the uncrushed stance is the bound.

## 2. Landing in wind: heading, drift, thrust, slope

Model: the aircraft touches down tilted φ toward a pad line with horizontal CG speed v toward it. The pivot holds
and the impact is plastic. Sink is ignored, which is conservative because sink adds a restoring moment. It tips if
(m v b)² / 2I_p > m g (R − b), with b = z sin φ + h cos φ, R = √(z² + h²) and I_p = I_cg + m R² (A3 inertia).
Lean is from a flat plate: tan λ = q S C_D90 / (m g), C_D90 1.28 (`ASM-B1-CD90`), taken at the 2.16 kg flying
mass. B1's 15.8° is at the 2.6 kg gate. A lighter aircraft leans more.

| Case (5 m/s card wind unless stated) | Lean ° | Tilt toward pivot ° | Drift allowed m/s | Wind limit m/s | Claim |
|---|---|---|---|---|---|
| Calm, 10° error | 0 | 10 | 0.86 | — | `CL-C5-DRIFT-ALLOW-CALM` |
| Broadside (wind on the wing face), lull at touchdown | 18.8 | 28.8 | 0.12 | 4.3 | `CL-C5-DRIFT-ALLOW-LULL`, `CL-C5-V-LAND-BROADSIDE` |
| Span into wind (wingtip upwind), wide axis | 11.0 | 21.0 | 1.12 | 8.3 | `CL-C5-DRIFT-ALLOW-SPANWISE`, `CL-C5-V-LAND-SPANWISE` |
| Tip angle needed with 0.3 m/s drift: broadside / span into wind (narrow) | | | | | 37.1° / 18.3° (`CL-C5-TIPOVER-REQ-*`) |

| Other landing limit | Value | Claim | Status |
|---|---|---|---|
| Tip angle with 2/3 W thrust still on and the attitude loop not correcting | 11.4° (vs 10° error) | `CL-C5-TIP-RESIDUAL-THRUST` | `UNVERIFIED` (+14 %) |
| Largest thrust fraction at touchdown that a 10° tilt survives | 0.71 W | `CL-C5-LAM-MAX` | `UNVERIFIED` (+6 % over 2/3) |
| Ground slope for a calm landing with 10° error and 0.3 m/s drift | 14.0° (card: ≤ 5°) | `CL-C5-SLOPE-CALM` | `UNVERIFIED` |
| Roll error that grounds the wingtip TE: uncrushed / first foot crushed | 10.0° / 5.3° | `CL-C1-WINGTIP-STRIKE-ANGLE`, `CL-C5-WINGTIP-ROLL-CRUSHED` | `UNVERIFIED` → CR-C5-04 |

Thrust left on after contact overturns the aircraft: it acts along the body axis at the pad offset. ArduPilot must
reach spin-min quickly after it detects the landing, and F4 confirms this on the twin (CR-C5-05).

## 3. Foot drop test (T-C5-FOOT-RIG, then T-C5-AIRCRAFT-DROP = C1's T-C1-FOOT-DROP)

The test is a free drop with no rotor lift, so it is harder than the design landing (lift 2/3 W): stroke 28.8 mm
against 25.0 mm.

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Design sink / drop height pad-to-floor | 1.5 / 0.115 | m/s, m | `P:requirements.landing_sink_ms`, `CL-C5-DROP-HEIGHT` | `PROPOSED` |
| Test mass | 2.6 (gate, sandbag in place of the LiPo) | kg | `P:requirements.mtow_gate_kg` | `PROPOSED` |
| Predicted CG peak / limit | 5.88 / 6.0 | g | `CL-C5-DROP-N` | `UNVERIFIED` (+2 %) |
| Predicted stroke / available / pass limit (3 mm guard) | 28.8 / 32 / 29.0 | mm | `CL-C5-DROP-STROKE`, `CL-C5-DROP-STROKE-MARGIN` | `UNVERIFIED` (0.2 mm left) |
| One foot first (10° pitch + roll), m_eff 0.58 kg | 21.2 | mm | `CL-C5-DROP-ONE-FOOT` | `UNVERIFIED` |
| Energy at full stroke, 4 feet / 40 mm at η 0.5 and n 6 | 4.10 / 3.06 | J | `CL-C5-FOOT-ENERGY` | `UNVERIFIED` |
| Single-foot rig: sled mass, drop | 0.65 / 0.115 | kg, m | `CALC-C5-DROP` | `PROPOSED` |

The "≥ 40 mm stroke" in `R-LANDING-IMPACT` is C1's η 0.5 figure. D5's constant-force foot (η 0.84) meets the
intent in 32 mm, and its energy capacity is 34 % higher. CR-C5-03 asks A2 to word the requirement as energy plus n,
with the drop test as the proof.

**Sequence.** (1) Rig: three drops on new cartridges. Pass: sled ≤ 6.0 g at a 100 Hz low-pass, stroke ≤ 29 mm, no
crack in the shoe bond. (2) Aircraft, props off, FC on a small 2S pack logging IMU at ≥ 1 kHz: two level drops,
then 10° pitch, 10° roll and 10° pitch + roll, with new cartridges before each level drop. Pass: CG ≤ 6.0 g, every
stroke ≤ 29 mm, wing TE clear in the level and pitch drops (the taped wingtip corner may touch in the roll and
corner drops), no damage beyond the cartridges. If n > 6 or the stroke is > 29 mm, D5 tunes `cartridge.section_z_m`
by the force ratio (T-D5-COUPON) and the rig is repeated.

## 4. Stance rules for the flight card (to H3, CR-C5-06)

| # | Rule | Number behind it | Claim |
|---|---|---|---|
| S1 | Land on the landing mat (≥ 0.8 × 0.8 m rubber on ply), level within 5° | μ 0.7 vs grass 0.5; slope room 14° calm | `CL-D5-PAD-MU`, `CL-C5-SLOPE-CALM` |
| S2 | Final descent and touchdown with **a wingtip pointed into the wind** | broadside limit 4.3 m/s, span-into-wind 8.3 m/s | `CL-C5-V-LAND-*` |
| S3 | Touch down in QLAND / QLOITER (GPS hold) at 0.5 m/s | drift allowance 0.86 m/s calm, 1.12 m/s span-into-wind | `CL-C5-DRIFT-ALLOW-*` |
| S4 | Throttle to idle / let the land detector disarm at once after contact; never hold hover thrust on the pads | 0.71 W tips a 10° tilt | `CL-C5-LAM-MAX` |
| S5 | **Between flights lay it flat** unless gusts ≤ 5 m/s, the pack is in and it stands on the mat. Always lay it flat to change the pack. Never leave it standing unattended | pack out: tips 7.5 m/s, slides on grass 5.2 m/s; allowed gust 5.1 (mat) / 4.3 (grass) m/s, about 3.6 m/s mean | `CL-C5-V-PARK-GUST` |
| S6 | Lay flat = pod up on the mat, **both lower props turned spanwise first**; it rests on the lower pads and the tube-end caps; TE toward the wind | blade clearance +17 mm spanwise, −111 mm with a blade down; lifts only above 10.8 m/s | `CL-C5-LAYFLAT-PROP-*`, `CL-C5-V-LIFT-FLAT` |
| S7 | After every landing look at the replace-mark groove on each piston; at the mark, swap the cartridge (3 min) | about 13 normal landings per cartridge | `CL-C5-LANDINGS-PER-CARTRIDGE` |
| S8 | After any hard landing or tip-over: check the shoe bonds, fin TE tips, props, motor mounts and pod nose before the next flight | fuse order, section 5 | — |

## 5. Crash energy path

Order of failure, cheapest first. The pack, FC, spar and motor tubes must never be the first thing to break.

| Order | Element | Takes | Repair | Owner |
|---|---|---|---|---|
| 1 | XPS foot cartridge | 1.5 m/s landing, 4.1 J at full stroke | swap, 3 min, wing-core offcut | D5 |
| 2 | Foot piston / pad, shoe bond | beyond full stroke; shoe bond SF 2.7 at the design load | printed spare, 10 min | D5 |
| 3 | Props | tip-over onto the upper or lower pair, 4.6 J (`CL-C1-TIPOVER-ENERGY`) | spare props in the field kit | E1 |
| 4 | Printed motor mount | fails before the tube (D-23, CR-C1-03) | printed spare | D3, C4 |
| 5 | Foam-board half-fin, wingtip TE corner | fall beyond the feet; wingtip strike | re-cut, 1 day | D3, D1 |
| 6 | XPS wing core | major crash | re-cut core, about $20, 1–2 days | D1 |
| never | Pack, FC, spar, motor tubes | — | — | D2, C3, F3 |

**Nose-in (cruise attitude).** Today the pack's fore face sits 1 mm behind the pod nose skin
(`CL-A3-PACK-FWD-ROOM`), so in a nose-in crash the pack is the crush zone. Holding a 680 g pack at 5 m/s to
≤ 100 g (UN 38.3 T.4 150 g / 1.5) needs a 24 mm XPS block over 3 880 mm² (62 × 62 mm) behind a 1.5 mm printed
spreader plate. That is 26 mm of room with the 2 mm nose wall. Without the spreader, the pack face alone loads
the foam to 62 g but needs a 39 mm block. Extending the pod nose 25 mm leaves 4.7 mm of box-length slack
(`CL-C5-BOX-X-SLACK-NOSE`) and moves the CG forward. Moving the pack aft instead would put the CG past the 0.049 m
aft limit (0.26 mm per mm). The request is CR-C5-02.

**Fin-tip fall (hover attitude).** The nose is up and the pack is driven aft (+x) toward the FC bay at
x 0.036–0.095 m. An aft pack stop (bulkhead) must carry the 85 N crash load (`CL-C1-PACK-CRASH-LOAD`) so the FC is
never the pack's stop. A fall from 2 m (6.3 m/s, about 43 J) is ten times what the feet hold. The half-fins and the
wing TE take the rest, and the pod is at the far end from the impact.

**Cruise crash at 16 m/s** (about 87 J in the pack alone): no structure protects the pack. H3's LiPo post-crash
procedure applies (bag, sand, 15 min watch).

## Assumptions

| Id | Value | Status | Basis |
|---|---|---|---|
| `ASM-C5-TD-DRIFT` | 0.3 m/s | `UNVERIFIED` | GPS-hold touchdown; replace with twin logs (T-C5-DRIFT-LOG) |
| `ASM-C5-PARK-SF` | 1.5 | `PROPOSED` | on overturning moment and friction, unattended case |
| `ASM-C5-GUST-FACTOR` | 1.4 | `UNVERIFIED` | 2 m open terrain; H3 measures |
| `ASM-C5-CL-FLAT` | 0.6 | `UNVERIFIED` | wing lying flat, any wind direction |
| `ASM-C5-PROP-HALF-DEPTH` / `ASM-C5-TUBE-CAP` | 12 / 5 mm | `UNVERIFIED` / `PROPOSED` | measure on the built aircraft |
| `ASM-C5-PACK-G-MAX` | 100 g | `UNVERIFIED` | UN 38.3 T.4 150 g / 1.5 (`SRC-C5-UN383`) |
| `ASM-C5-NOSE-WALL` / `ASM-C5-DROP-GUARD` | 2 / 3 mm | `PROPOSED` | D2 shell; 10 % of the stroke |

## Open issues

| Issue | Effect | Owner |
|---|---|---|
| Drop-test margins are thin (n +2 %, stroke 0.2 mm beyond the guard) and rest on the XPS plateau and the 1.10 peak factor | the coupon and the rig decide; the cartridge section is the knob | D5, C5 |
| Span-into-wind heading in hover: yaw authority and whether ArduPilot's weathervane option supports it on a tailsitter | rule S2 needs it | F4, B3, H2 (twin) |
| Pack crush room 1 mm vs 26 mm | nose-in crash crushes the pack | A1, D2, C3 (CR-C5-02) |
| Wingtip TE corner touches at about 5° roll once a foot crushes | elevon / core corner damage | D5, D1 (CR-C5-04) |
| The CG z of the built aircraft sets every narrow-axis angle (±5 mm ≈ ±0.8°) | re-run after T-A3-CG-BALANCE | A3, C5 |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-C5-TILT-BOARD` | tilt board, four directions, pack in / forward / out | tip-over claims, CG z and height |
| `T-C5-FOOT-RIG` | 0.65 kg sled on one foot, 0.115 m | drop n and stroke (early, cheap) |
| `T-C5-AIRCRAFT-DROP` | 2.6 kg aircraft, 0.115 m, level, pitch, roll, corner | `R-LANDING-IMPACT` claims |
| `T-C5-DRIFT-LOG` | 20 twin and aircraft landings: ground speed at contact, time to spin-min | drift and thrust claims |
| `T-D5-PAD-MU`, `T-D5-COUPON`, `T-D5-REPLACE` | D5's pad friction, crush curve and swap time | inputs to the above |
