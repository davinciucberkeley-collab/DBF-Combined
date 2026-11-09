# Propulsion — K09-L quad tailsitter

Owner: E1 (propulsion engineer), revision 2, 2026-11-09. Model and claims: `team/E1/propulsion.py` →
`team/E1/claims.json` (38 claims, `CL-E1-…`) and `subsystems/propulsion/parts.csv`. Figures: `team/E1/plots.py`.
Every number is at the 2.6 kg gate and comes from `params.json` as of this revision: cruise 16 m/s, L/D 5.6, chord
0.32 m, CLmax 0.80, 3° motor cant.

**Verdict.** Keep the SunnySky X3108S KV900, the LANRC 45 A ESC and the APC 11×5.5MR/MRP. Full throttle stays
current-limited (`Q_M_BAT_CURR_MAX` 100 A). The worst-state hover T/W is **2.18**, and this one figure replaces both
E1's 2.15 and E2's 1.89. Propulsion mass with leads, adapters and screws is **476 g**, which is 36 g over the 440 g
allocation (`FAIL`, CR-E1-14). Status of every number: `UNVERIFIED` until `T-E1-MOTOR-RM` and `T-E1-STAND` run.

## Selection

| Item | Choice | Unit price | Qty (spares) | Key rating | Source | Status |
|---|---|---|---|---|---|---|
| Motor | SunnySky X3108S KV900, 81 g, 3–4S | $24.99 | 5 (1) | 25 A / 30 s, 370 W; R 86 mΩ, I0 0.9 A | [sunnyskyusa.com](https://sunnyskyusa.com/products/sunnysky-x3108s-motors), [data image](https://cdn.shopify.com/s/files/1/2024/0305/files/SunnySky_X3108S_KV900_Data_3.jpg), [HiModel](https://www.himodel.com/electric/SUNNYSKY_X3108S_KV900_Outrunner_Brushless_Motor_for_Multirotor.html) | `UNVERIFIED` (R and I0 now agree across two listings) |
| ESC | LANRC BLHeli_S 45 A, 2–6S, Bluejay reflash | $7.50 ($30 / 4) | 8 (4) | 45 A cont, 55 A 10 s | [amazon.com/dp/B0D2HS4Y4J](https://www.amazon.com/dp/B0D2HS4Y4J) | `UNVERIFIED` (price not re-checked) |
| ESC fallback | Holybro Tekko32 F4 45A AM32, 5.8 g | $22.50 | — | 45 A cont, current sensor | [readymaderc.com](https://www.readymaderc.com/products/details/87186-holybro-tekko32-f4-45a-esc-am32) | `CHECKED` 2026-11-09 |
| Prop | APC 11×5.5MR + 11×5.5MRP | $3.83 | 8 (4) | 17 g; hub Ø16.5 × 8.9 mm, 1/4 in bore | [apcprop.com 11x5-5mr](https://www.apcprop.com/product/11x5-5mr/) | `CHECKED` 2026-11-09 |
| Prop (stand A/B) | APC 11×4.5MR / MRP | $3.83 | 4 | 17 g | [apcprop.com 11x4-5mr](https://www.apcprop.com/product/11x4-5mr/) | `CHECKED` |
| Prop adapter | Bolt-on M6×1, 2 RH + 2 LH, 3.0 g, with M3×4 screws, nuts and washers | $23.95 / 4 | 1 set | 4 × M3 on Ø12 mm, 4 mm pilot | [smallpartscnc.com](https://www.smallpartscnc.com/index.php?product_id=174&route=product%2Fproduct) | `CHECKED` (out of stock 2026-11-09) |
| Motor screws | M3×8 SHCS ISO 4762 A2 | $0.10 `EST` | 16 | — | Bolt Depot | `PROPOSED` |

## Margins

| Case | 11×4.5MR | 11×5.5MR | Limit | Claim | Status |
|---|---|---|---|---|---|
| Hover thrust per motor (download 1.06, cant 3°) | 6.77 N | 6.77 N | — | `CL-E1-HOVER-T` | `UNVERIFIED` |
| Hover rpm / duty | 5 690 / 0.52 | 5 300 / 0.49 | — | `CALC-E1-HOVER` | `UNVERIFIED` |
| Hover pack current / power (band kP 1 → 1.24) | 26.2 A / 326–388 W | 27.1 A / 335–401 W | ≤ 27.6 A | `CL-E1-HOVER-I`, `-55` | `UNVERIFIED` |
| T/W, bus held 14.8 V, no limiter | 3.41 | 3.58 | ≥ 2.0 | `CL-E1-TW-TABLE` | `UNVERIFIED` |
| T/W, fresh pack, 100 A limiter | 2.56 | 2.50 | ≥ 2.0 | `CL-E1-ILIM-TW-FRESH` | `UNVERIFIED` |
| **T/W, worst pack state** (below) | — | **2.18** | ≥ 1.6 | `CL-E1-TW-WORST` | `UNVERIFIED` |
| Per-motor current with the limiter | 24.8 A | 24.8 A | ≤ 25 A (motor) | `CL-E1-ILIM-I` | `UNVERIFIED` |
| Full-throttle current per motor, no limiter, 14.8 / 16.8 V | 37.3 / 45.6 A | 42.4 / 51.6 A | ≤ 36 / ≤ 45 A | `CL-E1-IMAX-*` | `FAIL` (hence the limiter) |
| Cruise 16 m/s, 1.14 N per prop: J, η_prop | 0.49, 0.29 | 0.57, 0.38 | — | `CL-E1-CRUISE-ETA-*` | `UNVERIFIED` |
| Cruise pack power (band kP 1 → 1.24) | 253–311 W | 201–247 W | params 307 W | `CL-E1-CRUISE-P-55` | `UNVERIFIED` |
| Transition corridor margin, worst point | 2.14 at 2.6 m/s | 2.19 at 2.1 m/s | ≥ 1.3 | `CL-E1-CORRIDOR-*` | `UNVERIFIED` |

**Mission (indicative; B1 and E2 own it).** 77 Wh usable. Hover takes 13.4 Wh (2 min at 401 W), which leaves
**15.4 min of cruise** at 247 W (19.0 min at the lower bound) against the 5 min requirement.

## Worst-state hover T/W (one claim, E1 + E2)

E1 had 2.15 (sag factor 0.86) and E2 had 0.72, later 0.76 (T/W 1.79–1.89). Now there is one calculation
(`CALC-E1-WORST`): E1's station model, using E2's pack model and E2's assumption ids.

| State | OCV | Pack R | Winding | Bus V | Thrust / motor | T/W | Status |
|---|---|---|---|---|---|---|---|
| Fresh, warm | 16.8 V | 19 mΩ | 25 °C | 14.9 V | 1 659 gf | 2.55 | `UNVERIFIED` |
| Reserve line, warm | 14.9 V | 19 mΩ | 80 °C | 13.0 V | 1 476 gf | 2.27 | `UNVERIFIED` |
| **Reserve line, 10 °C pack (claim)** | 14.9 V | 27 mΩ | 80 °C | 12.2 V | **1 417 gf** | **2.18** | `UNVERIFIED` |
| Below reserve, 3.60 V/cell, cold (sensitivity) | 14.4 V | 27 mΩ | 80 °C | 11.7 V | 1 377 gf | 2.12 | `UNVERIFIED` |

Pack values come from `ASM-E2-OCV-20` (3.73 V/cell), `ASM-E2-R-CELL` (4 mΩ), `ASM-E2-COLD-R` (×1.5) and
`ASM-E2-R-EXT` (3 mΩ). The 100 A limiter binds in every state, so per-motor current stays at 24.8 A.

- **Why E2's 0.76 is too low:** E2 applied (V/14.8 V)² to `thrust_max_per_motor_kg`. That value is already the current-limited fresh-pack thrust, so the voltage loss was counted twice. With the limiter on, a lower bus voltage costs electrical power (∝ V), not the V² of a fixed-duty prop.
- **Replacement for `params.json#propulsion.voltage_sag`:** 0.854 (`CL-E1-SAG-FACTOR`), defined as worst ÷ fresh with the limiter on. Then 4 × 1.62 × 0.854 / 2.6 = 2.13, which agrees with the claim within the warm-R difference.

## Motor and prop interface (for D3, A4, A5)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Body: OD × length (mount face to bell top) | 37.8 × 26.5 | mm | HiModel listing | `UNVERIFIED` |
| Shaft Ø / overall length (protrudes ~6.5 mm above the bell into the adapter pilot) | 4 / 33 | mm | HiModel; adapter pilot 4 × 8.5 mm | `UNVERIFIED` |
| **Base bolt pattern** | not published: print 4 radial M3 slots (3.4 mm wide, r 7.5–13.5 mm, at 90°) to fit 16×19, 19×19 and 19×25 mm; freeze to the caliper value on arrival | mm | no source found 2026-11-09 | `UNVERIFIED` |
| Base centre relief (bearing, circlip) | Ø10 × 2 | mm | `EST` | `PROPOSED` |
| Mount plate at the screw bosses | 5.0 | mm | `ASM-E1-MOUNT-SCREW` | `PROPOSED` (D3) |
| **Motor screw** | M3×8 SHCS A2, no washer, Loctite 243, 0.5 N·m: 3.0 mm engagement (window 2.5–3.5 mm) | — | `CL-E1-SCREW-ENGAGE` | `UNVERIFIED` (probe hole depth) |
| **Prop adapter** | bolt-on, 4 × M3×4 on Ø12 mm in the bell, M6×1 post 15.2 mm, base 6.35 mm; **LH thread on CW motors**, RH on CCW | — | Small Parts CNC set | `CHECKED` (fit claim by the vendor) |
| Prop hub thickness / Ø | 8.9 / 16.5 | mm | APC page (0.35 / 0.65 in) | `CHECKED` |
| **Mount face to prop mid-plane** | 37.3 | mm | `CL-E1-STACK-PROP-PLANE` | `UNVERIFIED` |
| Mount face to hub front / post tip | 41.7 / 48.1 | mm | `CL-E1-STACK-POST-TIP` | `UNVERIFIED` |
| Prop axial keep-out about the mid-plane | −6 / +10 (toward the motor / forward, includes coning) | mm | `EST` | `PROPOSED` |
| Prop nut: M6 ISO 4032 (5.2 mm) on a 1.0 mm washer: thread past the nut | 0.1 | mm | `CL-E1-NUT-ENGAGE` | `UNVERIFIED` (tight: no thicker washer, no nylock) |
| Motor lead length / gauge | not published | — | — | `UNVERIFIED`: measure; the A3 ESC position is ~100 mm away |

With the plate face at x = 0.034 m, the prop mid-plane sits at x = −0.0033 m. `params.json` has −0.005 m (CR-E1-16).

## Mass (`CL-E1-MASS-PRP`, `subsystems/propulsion/parts.csv`)

| Part | Per unit | Qty | Total | Basis | Status |
|---|---|---|---|---|---|
| Motor, factory leads, no bullets | 81.0 g | 4 | 324.0 g | listing | `UNVERIFIED` |
| ESC with leads and heat-shrink | 11.0 g `EST` | 4 | 44.0 g | 6.6 g board + 2 × 80 mm 16 AWG + signal lead + shrink | `UNVERIFIED` |
| Prop | 17.0 g | 4 | 68.0 g | APC page | `CHECKED` |
| Adapter + 4 × M3×4 + M6 nut + washer | 6.7 g | 4 | 26.8 g | vendor 3.0 g + ISO masses | `UNVERIFIED` |
| Motor screws 4 × M3×8 | 3.2 g | 4 | 12.8 g | ISO | `PROPOSED` |
| **Total** | 118.9 g | | **475.6 g** | allocation 440 g | `FAIL` |

The A3 figure of 438 g left out the ESC leads and the motor screws. Levers: Tekko32 ESCs (5.8 g with leads,
−21 g, +$60), aluminium prop nuts (−4 g), and counting the motor screws under the fin mount (−13 g).

## Losses per station (input to E3)

| Phase | Motor loss | ESC loss | Phase current | Winding rise (R_th 1.0 K/W `EST`) | Status |
|---|---|---|---|---|---|
| Hover, 11×5.5MR | 22.9 W | 2.4 W | 13.6 A (30 % of the ESC rating) | 23 K | `UNVERIFIED` |
| Cruise 16 m/s | 12.1 W | < 1.2 W | 8.2 A | 12 K | `UNVERIFIED` |
| Full throttle with the limiter, ≤ 30 s | 86 W | 10 W | 30 A | transient | `UNVERIFIED` |

## Motor out (`CALC-E1-MOTOR-OUT`, 11×5.5MR)

| Phase | What is left | Numbers | Verdict |
|---|---|---|---|
| Hover | The diagonal partner must also stop, which leaves 2 motors turning the same way | T/W 1.09 at the worst state; yaw torque 0.28 N·m against 0.16 N·m of yaw control from a ±30 % differential | **Fatal**, as accepted in `CONFIGURATION.md` |
| Cruise 16 m/s | 2 motors carry the drag at 2.3 N each, 193 W | 0.23 N·m of roll torque for the elevons (B3) | Possibly survivable: throttle cut, FBWA glide (F4 SITL) |

## Open issues

| Issue | Owner | Status |
|---|---|---|
| Base bolt pattern, hole depth and lead length are not published; measure the first motor before D3 freezes the mount | E1 / D3 | `UNVERIFIED` |
| Mass is 36 g over the allocation; the ESC-with-leads mass is the largest unknown | E1 / A3 | `FAIL` |
| Nut engagement margin is 0.1 mm: check the adapter supplied with the motor; if its post is shorter, use a flanged prop nut | E1 | `UNVERIFIED` |
| The `R-ESC-CURRENT` text still fails unlimited full throttle (CR-E1-07) | A2 | `FAIL` |
| PER3 correction transfer, R and I0, and pack IR | H1 / E2 | `UNVERIFIED` |

## How to verify

1. `python -I redesign/team/E1/propulsion.py`, then `python -I redesign/proofs/build_graph.py` (no `CALC-E1` drift).
2. `T-E1-MOTOR-RM` incoming check: masses, bolt pattern, hole depth, lead length, R and I0. Update `ASM-E1-PART-MASS` and `ASM-E1-STACK`, then re-run.
3. `T-E1-STAND`: both props, held 14.8 V, fresh pack, then a pack at 3.73 V/cell cold-soaked to 10 °C. Their ratio checks `CL-E1-SAG-FACTOR`.

![Overall efficiency map](fig-prp-01-efficiency-map.svg)

`FIG PRP-01 — Overall efficiency against airspeed and thrust per motor; cruise drag line at 2.6 kg, cruise point 16 m/s.`

![Static thrust against current](fig-prp-02-static.svg)

`FIG PRP-02 — Static thrust against battery current per motor at a held 14.8 V; the maker's points fall below the model above 12 A (sagging supply).`
