# Propulsion — K09-L quad tailsitter

Owner: E1 (propulsion engineer), 2026-11-09. Model and claims: `team/E1/propulsion.py` → `team/E1/claims.json`
(33 claims, ids `CL-E1-…`). Figures: `team/E1/plots.py`. All numbers are at the 2.6 kg gate unless stated.

**Verdict.** Keep the SunnySky X3108S KV900 and the LANRC 45 A ESC. Change the prop to the **APC 11×5.5MR/MRP**
(same price, mass and hub as the 11×4.5MR): cruise power drops about 20 %, and hover and T/W change by less than 3 %.
Full throttle **must be current-limited** (`Q_M_BAT_CURR_MAX` 100 A). Without the limit each motor draws 37–52 A,
and the motor is rated 25 A for 30 s. Status of every number: `UNVERIFIED` until the thrust stand (`T-E1-STAND`) runs.

## Selection

| Item | Choice | Unit price | Qty (spares) | Key rating | Source | Status |
|---|---|---|---|---|---|---|
| Motor | SunnySky X3108S KV900, 81 g, 3–4S | $24.99 | 5 (1) | 25 A / 30 s, 370 W; R 86 mΩ, I0 0.9 A | [sunnyskyusa.com](https://sunnyskyusa.com/products/sunnysky-x3108s-motors), [data image](https://cdn.shopify.com/s/files/1/2024/0305/files/SunnySky_X3108S_KV900_Data_3.jpg), [Robu spec](https://robu.in/?p=1569817) | `UNVERIFIED` (R, I0: one listing; price seen 2026-11-01, page HTTP 429 today) |
| ESC | LANRC BLHeli_S 45 A, 2–6S, 6.6 g (4-pack) | $30.00 / 4 | 8 (4) | 45 A cont, 55 A 10 s | [amazon.com/dp/B0D2HS4Y4J](https://www.amazon.com/dp/B0D2HS4Y4J) | `UNVERIFIED` (Amazon HTTP 503 today; listing from `docs/research/bom-savings.md`) |
| ESC fallback | Holybro Tekko32 F4 45A, AM32, current sensor, 5.8 g | $22.50 | — | 45 A cont, 2–6S | [readymaderc.com](https://www.readymaderc.com/products/details/87186-holybro-tekko32-f4-45a-esc-am32) | `CHECKED` 2026-11-09 (backorder to Dec 2026) |
| Prop (proposed) | APC 11×5.5MR (LP11055MR) + 11×5.5MRP (LP11055MRP) | $3.83 | 8 (4) | 17 g, 1/4 in bore | [apcprop.com 11x5-5mr](https://www.apcprop.com/product/11x5-5mr/), [11x5-5mrp](https://www.apcprop.com/product/11x5-5mrp/) | `CHECKED` 2026-11-09 |
| Prop (stand A/B, twin) | APC 11×4.5MR / MRP | $3.83 | 4 | 17 g (params says 20 g) | [apcprop.com 11x4-5mr](https://www.apcprop.com/product/11x4-5mr/) | `CHECKED` 2026-11-09 |
| Adapter rings | APC LPAR06E | $0.50 `EST` | 12 | — | `config-study/cards/K09/cost.csv` | `UNVERIFIED` |

Cost is unchanged at $236.91 before tax (`cards/K09/cost.csv` lines). Mass per station: 81 + 6.6 + 17 + 1 =
105.6 g, so 422 g for four stations against the 430 g allocation (`params.json#mass.allocation_g.propulsion`).

## Method

1. **Prop:** APC PER3 blade-element files (Ct, Cp versus rpm and J) for the 11×4.5MR, 11×5.5MR, 12×4.5MR and 11×4.7SF ([PER3_11x45MR.dat](https://www.apcprop.com/files/PER3_11x45MR.dat)).
2. **Motor:** Kv 900 rpm/V, R 86 mΩ (raised to 80 °C for the thrust cases), I0 0.9 A. **ESC:** 10 mΩ + 0.5 W. **Pack:** 24 mΩ including the harness, plus 1 A for the avionics.
3. **Calibration (`CALC-E1-CAL`):** the maker's 18-row table for the same motor on an APC 11×4.7 was fitted against PER3 for that prop.
   - kT = 1.039 (thrust at the measured rpm, rms error 0.6 %).
   - kP = 1.24 (battery power, rows 5–12 A, maximum error 6.3 %).
4. **The maker table is not a 14.8 V table at the top end.** Its W column is 14.8 V × A. The top row (1 580 gf at 7 500 rpm) is only reachable with about 11.2 V at the motor (`CL-E1-MAKER-SUPPLY`), so the test supply sagged. The `params.json` row `[1580, 447]` is therefore not a 14.8 V point.
5. **Lower bound:** pure PER3 (kP = 1, `CALC-E1-SENS`). The stand result is expected to fall between this and the calibrated model.

## Margins (gate 2.6 kg, download 1.06, 689 gf per motor in hover)

| Case | 11×4.5MR | 11×5.5MR | Limit | Claim | Status |
|---|---|---|---|---|---|
| Hover rpm / duty | 5 690 / 0.52 | 5 290 / 0.49 | — | `CALC-E1-HOVER` | `UNVERIFIED` |
| Hover pack current (14.8 V) | 26.2 A | 27.0 A | ≤ 27.6 A (24 A + 15 %) | `CL-E1-HOVER-I`, `-55` | `UNVERIFIED` |
| Hover power (band, kP 1 → 1.24) | 325–387 W | 335–400 W | — | `CALC-E1-SENS`, `CALC-E1-HOVER` | `UNVERIFIED` |
| Hover efficiency | 7.1 gf/W | 6.9 gf/W | — | `CL-E1-HOVER-GW` | `UNVERIFIED` |
| T/W, bus held at 14.8 V, no limiter | 3.41 | 3.58 | ≥ 2.0 | `CL-E1-TW-TABLE` | `UNVERIFIED` |
| T/W, low pack (3.6 V/cell OCV, sag to 12.0 V, 80 °C) | 2.23 | 2.28 | ≥ 1.6 | `CL-E1-TW-SAG`, `-55` | `UNVERIFIED` |
| T/W with the 100 A limiter, fresh / low pack | 2.56 / 2.22 | 2.50 / 2.15 | ≥ 2.0 / ≥ 1.6 | `CL-E1-ILIM-TW-FRESH`, `-LOW` | `UNVERIFIED` |
| Full-throttle current per motor, 14.8 V / 16.8 V, no limiter | 37.3 / 45.6 A | 42.4 / 51.6 A | ≤ 36 / ≤ 45 A | `CL-E1-IMAX-148`, `-168` | `FAIL` |
| Per-motor current with the limiter | 24.8 A | 24.8 A | ≤ 25 A (motor) | `CL-E1-ILIM-I` | `UNVERIFIED` |
| Peak pack current, low pack, no limiter | 101 A | 111 A | F1 sizes to it | `CL-E1-IPACK-PEAK` | `UNVERIFIED` |
| Cruise 15 m/s, 1.08 N per prop: J, η_prop | 0.49, 0.30 | 0.57, 0.39 | — | `CL-E1-CRUISE-ETA-45`, `-55` | `UNVERIFIED` |
| Cruise power (band, kP 1 → 1.24) | 219–269 W | 176–216 W | params 194 W | `CL-E1-CRUISE-P-45`, `-55` | `FAIL` vs params (mission still passes, see below) |
| Transition corridor: full thrust ÷ thrust needed, worst point | 2.14 at 2.9 m/s | 2.19 at 2.4 m/s | ≥ 1.3 | `CL-E1-CORRIDOR-45`, `-55` | `UNVERIFIED` |

The 12×4.5MR was screened and rejected. It cruises at 321 W (worst), draws 45 A at 14.8 V and needs 0.03 m more
prop clearance.

**Mission (indicative, B1 owns it).** 77 Wh usable (96.2 Wh × 0.8). Hover takes 13.3 Wh (2 min at 400 W), which
leaves **17.7 min of cruise on the 11×5.5MR** (22 min at the lower bound) and 14.3 min on the 11×4.5MR, against the
5 min requirement. The `FAIL` is against the `params.json` cruise power of 194 W, not against the mission.

![Overall efficiency map](fig-prp-01-efficiency-map.svg)

`FIG PRP-01 — Overall efficiency (thrust power ÷ battery power) against airspeed and thrust per motor; the cruise drag line at 2.6 kg is ink for the 11×4.5MR and blue for the 11×5.5MR.`

![Static thrust against current](fig-prp-02-static.svg)

`FIG PRP-02 — Static thrust against battery current per motor at a held 14.8 V; the maker's points fall below the model above 12 A because their supply sagged.`

## Temperatures and losses per station (input to E3)

| Phase | Motor loss | ESC loss | Phase current | Winding rise (R_th 1.0 K/W `EST`) | Status |
|---|---|---|---|---|---|
| Hover, 11×4.5MR / 11×5.5MR | 20.7 / 22.8 W | 2.1 / 2.4 W | 12.6 / 13.6 A | 21 / 23 K → about 53 °C at 30 °C ambient | `UNVERIFIED` |
| Cruise 15 m/s | 12.7 / 10.9 W | < 1.2 W | 8.2 / 7.6 A | < 13 K | `UNVERIFIED` |
| Full throttle with the limiter, fresh pack (≤ 30 s) | 79 / 86 W | 9 / 10 W | 29 / 30 A (24.8 A battery side) | transient; the motor is rated 25 A / 30 s | `UNVERIFIED` |
| Full throttle, no limiter, 14.8 V | 129 / 164 W | 14–18 W | 37–42 A | the maker logged 94 °C at its 30 A row | `FAIL` (not allowed) |

The ESC runs at 28 % of its continuous rating in hover. Both motor and ESC sit in the prop wash in every phase.

## Motor out (`CALC-E1-MOTOR-OUT`)

| Phase | What is left | Numbers | Verdict |
|---|---|---|---|
| Hover | To balance the moments, the diagonal partner of the failed motor must also stop. That leaves 2 motors turning the same way | T/W 1.12; unbalanced yaw torque 0.26 N·m against 0.15 N·m of yaw control from a ±30 % differential | **Fatal:** the aircraft spins and descends. Accepted in `CONFIGURATION.md` |
| Cruise 15 m/s | The same 2 motors carry the drag at 2.2 N each and 200 W | 0.22 N·m of roll torque for the elevons to hold (CR-E1-04) | **Possibly survivable:** throttle cut, FBWA glide, belly landing. The procedure is F4's; the SITL motor-failure test is `UNVERIFIED` |
| Transition | Whichever of the two applies at that instant | — | Treat as fatal |

## Open issues

| Issue | Owner | Status |
|---|---|---|
| R and I0 come from one retailer listing; measure them on arrival (`T-E1-MOTOR-RM`) | E1 / H1 | `UNVERIFIED` |
| The PER3 correction is assumed to transfer from the 11×4.7SF to the MR props; the stand A/B of both props settles it | H1 | `UNVERIFIED` |
| Pack IR of 24 mΩ is assumed; E2 measures it | E2 | `UNVERIFIED` |
| Transition uses a flat-plate post-stall wing with no prop wash (conservative); B1/B2 replace it | B1 | `UNVERIFIED` |
| BLHeli_S desync on 11 in props under throttle punches: covered by the stand step test; Bluejay reflash gives bidirectional DShot for rpm logs and the harmonic notch | E1 / F4 | `PROPOSED` |
| The X3108S prop clamp (included holding disk) and its thread are unconfirmed; check on arrival before D3 freezes the prop-plane x | E1 / D3 | `UNVERIFIED` |

## How to verify

1. `python -I redesign/team/E1/propulsion.py`, then `python -I redesign/proofs/build_graph.py` (must report "every stored number re-computes").
2. `T-E1-MOTOR-RM` (milliohm and no-load), then `T-E1-STAND` (both props, held 14.8 V and a flight pack, throttle punches). Enter the rows in `MAKER_1147`'s place and re-run.
3. `T-E1-HOVER-LOG`: tethered hover current within 27.6 A and the can temperature.
