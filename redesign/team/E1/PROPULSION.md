# Propulsion — K09-L quad tailsitter

Owner: E1 (propulsion engineer), revision 5, 2026-11-09. Model and claims: `team/E1/propulsion.py` →
`team/E1/claims.json` (61 claims, `CL-E1-…`), `subsystems/propulsion/parts.csv` and
`subsystems/propulsion/interfaces.json`. Figures: `team/E1/plots.py`. Every number is at the 2.6 kg gate and reads
`params.json` as of this revision: cruise 16 m/s, chord 0.32 m, CLmax 0.80, **7° motor cant** (D-27), harness
6.5 mΩ (D-32), and B1's rev 3 polar (CD0 0.0513, k 0.0943, trim 1.02).

**Verdict.** Keep the SunnySky X3108S KV900, the LANRC 45 A ESC and the APC 11×5.5MR/MRP. Full throttle stays
current-limited (`Q_M_BAT_CURR_MAX` 100 A). The worst-state hover T/W is **2.12** (limit 1.6). Propulsion is
**462.0 g** against the 462 g allocation (D-48, ESCs carried stripped of their power leads), zero margin. Three
claims fail, all fixed by D3 values A1 has already adopted (D-51) but `subsystems/fins/params.json` does not carry yet:
the prop-to-collar gap (`face_ahead_m` 0.001 → 0.0025, CR-E1-22) twice, and the ESC strap slot (pad 28 → 31 mm,
CR-E1-30). Every number is `UNVERIFIED` until `T-E1-MOTOR-RM` and `T-E1-STAND` run.

## Revision 5 (2026-11-09): CR-A1-48, CR-A4-43, CR-A5-21, CR-D3-22, CR-B4-20

| Item | Resolution | Numbers | Claim | Status |
|---|---|---|---|---|
| Re-run on current inputs (CR-E2-17) | `CALC-E1-WORST` reads `P:electrical.r_ext_mohm` ÷ 1000; stored map rewritten | T/W worst **2.12**, sag 0.851, pack R 22.5 / 30.5 mΩ warm / cold | `CL-E1-TW-WORST`, `CL-E1-SAG-FACTOR` | `UNVERIFIED` |
| `PRP-002` stripped (D-48) | F2 removes the factory power leads and solders 16 AWG to the pads | ESC 11.0 → **7.6 g**; propulsion **462.0 / 462 g** | `CL-E1-MASS-PRP` | `UNVERIFIED` (weigh) |
| Tilted keep-outs (CR-A5-21) | `k9.prop_keepout(..., rotate=rot, blade_half=0.010)` in `fusion/propulsion.py` | cylinder on the 7° axis, R 164.7 mm, half **35 mm** (10 + 25) | `CL-E1-KO-HALF` | `MODELLED` (`check.py` 0 hits) |
| Adapter screws (CR-A4-43, D-58) | M3×4 at 2.5 mm stays under deviation D-58 (a), minimum 2.0 mm; the condition is now a claim and a test step; M3×5 is the compliant swap if the bell allows | thread needed **2.5 mm**; M3×5 engages 3.5 mm (rule 3.0, +0.5 mm) and needs **4.0 mm** free depth; RF 2.12 at 2.5 mm, 1.70 at 2.0 mm | `CL-E1-ADAPTER-THREAD-D58`, `-M3X5-ENGAGE`, `-M3X5-DEPTH`, `-RF-NOM`, `-STRIP` | `UNVERIFIED` (measure) |
| Motor interface (CR-D3-22) | added to `T-E1-MOTOR-RM`: base Ø ≥ 28 mm, 16 × 19 mm pattern, base hole depth ≥ 4.0 mm | M3×8 through the 4.5 mm plate → 3.5 mm | `CL-E1-HOLE-DEPTH-MIN`, `CL-E1-SCREW-ENGAGE` | `UNVERIFIED` |
| Lead reach (CR-F2-07) | motor phase-lead length measured against F2's routed **0.121 m**; if it reaches, no splice (F2 −12 g) | — | `CL-F2-PHASE-REACH` | `UNVERIFIED` |
| ESC envelope for B4 (CR-B4-20) | body 45 × 20 × 6 mm in shrink + 1.5 mm strap over a 10 mm band | **7.5 mm** proud of the pad (B4 assumed 6.8), 23 mm wide, 172.5 mm² frontal | `CL-E1-ESC-PROUD`, `CL-E1-ESC-FRONTAL` | `UNVERIFIED` |
| Acknowledgements | declared edges in `acknowledges` (16); A4's plan edges not yet declared in `acknowledges_pending` (20: `E-HRN-13…16`, `-24…27`, `-34…37`, `E-FIN-81…88`), moved on the next run after F2 / D3 declare | — | `make_propulsion.py` | `CHECKED` |

**Adapter-screw decision at `T-E1-MOTOR-RM`** (first motor, before any adapter is torqued):

| Measured in the bell top | Screw | Engagement | Basis |
|---|---|---|---|
| thread ≥ 3.0 mm and free depth ≥ 4.0 mm | M3×5 SHCS (buy 20, ≈ $3 `EST`) | 3.5 mm | 1.0 d rule met, no deviation |
| 2.5 mm ≤ thread < 3.0 mm, or free depth < 4.0 mm | supplied M3×4 | 2.5 mm (min 2.0) | D-58 (a), RF 1.70 at 2.0 mm |
| thread < 2.5 mm | none: the station is not flown | — | D-58 condition fails; E1 re-assesses (motor-box adapter, other motor) |

## Selection

| Item | Choice | Unit price | Qty (spares) | Key rating | Source | Status |
|---|---|---|---|---|---|---|
| Motor | SunnySky X3108S KV900, 81 g, 3–4S | $24.99 | 5 (1) | 25 A / 30 s, 370 W; R 86 mΩ, I0 0.9 A | [sunnyskyusa.com](https://sunnyskyusa.com/products/sunnysky-x3108s-motors), [data image](https://cdn.shopify.com/s/files/1/2024/0305/files/SunnySky_X3108S_KV900_Data_3.jpg), [HiModel](https://www.himodel.com/electric/SUNNYSKY_X3108S_KV900_Outrunner_Brushless_Motor_for_Multirotor.html) | `UNVERIFIED` |
| ESC | LANRC BLHeli_S 45 A, 2–6S, Bluejay reflash | $7.50 ($30 / 4) | 8 (4) | 45 A cont, 55 A 10 s | [amazon.com/dp/B0D2HS4Y4J](https://www.amazon.com/dp/B0D2HS4Y4J) | `UNVERIFIED` (price not re-checked) |
| ESC fallback | Holybro Tekko32 F4 45A AM32, 5.8 g | $22.50 | — | 45 A cont, current sensor | [readymaderc.com](https://www.readymaderc.com/products/details/87186-holybro-tekko32-f4-45a-esc-am32) | `CHECKED` 2026-11-09 |
| Prop | APC 11×5.5MRP on UR, LL (CW from the nose); 11×5.5MR on UL, LR (CCW) | $3.83 | 8 (4) | 17 g; hub Ø16.5 × 8.9 mm | [apcprop.com 11x5-5mr](https://www.apcprop.com/product/11x5-5mr/) | `CHECKED` 2026-11-09 |
| Prop (stand A/B) | APC 11×4.5MR / MRP | $3.83 | 4 | 17 g | [apcprop.com 11x4-5mr](https://www.apcprop.com/product/11x4-5mr/) | `CHECKED` |
| Prop adapter | Bolt-on M6×1: **LH on UR, LL**, RH on UL, LR; M3×4 screws, nuts, washers | $23.95 / 4 | 1 set | 4 × M3 on Ø12 mm | [smallpartscnc.com](https://www.smallpartscnc.com/index.php?product_id=174&route=product%2Fproduct) | `CHECKED` (out of stock 2026-11-09) |
| Motor screws `PRP-005` | M3×8 SHCS ISO 4762 A2 | $0.10 `EST` | 20 (4) | — | Bolt Depot | `PROPOSED` |

Rotation and thread hand follow F4's motor map (`subsystems/flight-software/SPEC.md`). The prop lags the shaft, so
a CW motor needs a left-hand post for the nut to tighten itself.

## Margins (11×5.5MR unless stated)

| Case | Value | Limit | Claim | Status |
|---|---|---|---|---|
| Hover thrust per motor (download 1.06, cant 7°) | 6.81 N, 5 313 rpm, duty 0.50 | — | `CL-E1-HOVER-T` | `UNVERIFIED` |
| Hover pack current / power (kP 1 → 1.24) | 27.3 A / 338–405 W | ≤ 31.05 A (27 A + 15 %) | `CL-E1-HOVER-I-55` | `UNVERIFIED` |
| T/W, bus held 14.8 V, no limiter | 3.58 | ≥ 2.0 | `CL-E1-TW-TABLE` | `UNVERIFIED` |
| T/W, fresh pack, 100 A limiter | 2.47 | ≥ 2.0 | `CL-E1-ILIM-TW-FRESH` | `UNVERIFIED` |
| **T/W, worst pack state** | **2.12** | ≥ 1.6 | `CL-E1-TW-WORST` | `UNVERIFIED` |
| Per-motor current with the limiter | 24.75 A | ≤ 25 A (`propulsion.motor_max_a`) | `CL-E1-ILIM-I` | `UNVERIFIED` |
| Pack current with the limiter | 100 A | ≤ 100 A (`full_throttle_current_a`) | `CL-E1-IPACK-LIM` | `UNVERIFIED` (bench) |
| Unlimited burst per motor at 16.8 V | 51.6 A | ≤ 55 A (`esc_burst_a`, 10 s) | `CL-E1-IMAX-168-55` | `UNVERIFIED` |
| Unlimited pack peak, low pack (wiring case) | 108 A | ≤ 120 A (`electrical.peak_current_a`) | `CL-E1-IPACK-PEAK` | `UNVERIFIED` |
| Cruise drag 16 m/s (B1 polar, W/D 6.22) | 4.10 N, 1.03 N per prop | — | `CL-E1-CRUISE-DRAG` | `UNVERIFIED` |
| Cruise J, η_prop, rpm | 0.58, 0.36, 5 944 | — | `CL-E1-CRUISE-ETA-55` | `UNVERIFIED` |
| Cruise propulsion power (kP 1 → 1.24) | 191–234 W, 15.8 A | ≤ 218 W (params, stale) | `CL-E1-CRUISE-P-55` | `FAIL` (CR-E1-24) |
| Transition corridor margin, worst point | 2.13 at 1.6 m/s | ≥ 1.3 | `CL-E1-CORRIDOR-55` | `UNVERIFIED` |
| Winding rise in hover (R_th 1.0 K/W `EST`) | 23 K | ≤ 50 K | `CL-E1-HOVER-DT` | `UNVERIFIED` |

**Mission (indicative; B1 and E2 own it).** 77 Wh usable. Hover takes 13.5 Wh (2 min at 405 W), which leaves
**16 min of cruise** at 234 W + 6 W avionics against the 5 min requirement.

## Worst-state hover T/W and the sag factor (D-35)

One calculation (`CALC-E1-WORST`): the E1 station model with E2's pack assumptions and F1's harness resistance.

| State | OCV | Pack R | Winding | Bus V | Thrust / motor | T/W | Status |
|---|---|---|---|---|---|---|---|
| Fresh, warm | 16.8 V | 22.5 mΩ | 25 °C | 14.6 V | 1 634 gf | 2.49 | `UNVERIFIED` |
| Reserve line, warm | 14.9 V | 22.5 mΩ | 80 °C | 12.7 V | 1 450 gf | 2.22 | `UNVERIFIED` |
| **Reserve line, 10 °C pack (claim)** | 14.9 V | 30.5 mΩ | 80 °C | 11.9 V | **1 390 gf** | **2.12** | `UNVERIFIED` |
| Below reserve, 3.60 V/cell, cold | 14.4 V | 30.5 mΩ | 80 °C | 11.4 V | 1 350 gf | 2.06 | `UNVERIFIED` |

| Sag factor (worst ÷ fresh, limiter on) | Value | Method | Claim |
|---|---|---|---|
| E1 station model | **0.851** | PER3 + motor model at each bus voltage | `CL-E1-SAG-FACTOR` |
| E1 closed form | 0.873 | same 100 A in both states, so P ∝ V_bus; static T ∝ P^2/3; no winding heating | `CL-E1-SAG-XCHECK` |
| E2 | 0.758 | (V / 14.8 V)² applied to a thrust that is already limited at 100 A | `CL-E2-SAG-F-WORST` |
| params (D-35) | 0.76 | the lower of E1 and E2, carried until they agree | `propulsion.voltage_sag` |

The two E1 methods agree within 3 %. E2's method counts the voltage twice: the limited thrust already includes the
fresh-pack bus voltage, and with the limiter binding, a lower bus voltage costs power in proportion to V, not V².
Both values pass 1.6. The cold-pack stand run settles it (CR-E1-25).

## Motor and prop interface (for D3, A4, A5)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Body: OD × length (mount face to bell top) | 37.8 × 26.5 | mm | HiModel listing | `UNVERIFIED` |
| Base bolt pattern | not published: D3 drills the 2.5 mm pilots to the measured motor (no slots, C6) | mm | — | `UNVERIFIED` |
| Motor screw | M3×8 through D3's 4.5 mm canted plate: **3.5 mm** engagement at every hole (window 2.5–3.5) | mm | `CL-E1-SCREW-ENGAGE` | `UNVERIFIED` |
| Base hole depth needed | ≥ 4.0 (else plate 5.0 mm, `CL-E1-SCREW-SEAT`) | mm | `CL-E1-HOLE-DEPTH-MIN` | `UNVERIFIED` (probe) |
| Prop adapter | bolt-on, 4 × M3×4 on Ø12 mm, M6×1 post 15.2 mm, base 6.35 mm | mm | Small Parts CNC | `CHECKED` (vendor fit list) |
| **Mount face to prop mid-plane** | **37.3** (D3's CAD: 39.0) | mm | `CL-E1-STACK-PROP-PLANE`, `CL-E1-STACK-VS-D3` −1.7 | `UNVERIFIED` |
| Prop plane to collar front ÷ 0.14 D (with 1 mm `face_ahead`) | 0.979 | — | `CL-E1-PROP-GAP` | `FAIL` → `face_ahead_m` 2 mm (CR-E1-22) |
| Mount face to hub front / post tip | 41.7 / 48.1 | mm | `CL-E1-STACK-POST-TIP` | `UNVERIFIED` |
| M6 nut: thread past the full nut height | 0.1 | mm | `CL-E1-NUT-ENGAGE` | `UNVERIFIED` (tight) |

**Stack confirmation (D-28).** The motors are ordered in mid-December, so the stack cannot be measured yet. The
measurement is step 1 of `T-E1-MOTOR-RM` on the first motor that arrives. Until then the 37.3 mm paper value
stands, and with D3's 1 mm `face_ahead_m` the gap is 0.8 mm short. A 2 mm `face_ahead_m` covers both stacks.

## Interfaces (`subsystems/propulsion/interfaces.json`)

| Edge | Parts | Via | Owner | Key data |
|---|---|---|---|---|
| `E-PRP-01…04` | adapter `PRP-004-<st>` → motor `PRP-001-<st>` | `CT-PROP-ADAPTER` | propulsion | 4 × M3×4, 2.5 mm in the bell, 0.6 N·m + Loctite 243 |
| `E-PRP-05…08` | prop `PRP-003-<st>` → adapter | `CT-PROP-NUT` | propulsion | M6 nut 5.3 mm engaged, 1.5 N·m `EST`, field joint |
| `E-FIN-61…64` | motor → mount `FIN-003-<st>` | `CT-M3-SHCS-MOTOR` | fins (acknowledged) | 4 × M3×8 `PRP-005` |
| `E-FIN-65…68` | ESC `PRP-002-<st>` → pad `FIN-007-<st>` | `CT-STRAP-VELCRO` | fins (acknowledged) | heat-sink side out |
| `E-HRN-17…20` | ESC phase → motor | `CT-SOLDER-PHASE` | harness (acknowledged) | per ESC 24.75 A limited, 51.6 A burst |
| `E-TRN-17…20` | prop → box slot | `CT-TRN-POCKET` | transport (acknowledged) | stowed props |
| `E-HRN-13…16`, `-24…27`, `-34…37`; `E-FIN-81…88` | ESC power, DShot, cap leads; motor / ESC thermal contact | — | harness, fins (`acknowledges_pending`) | from A4's plan |

`merge_check.py`: no propulsion errors; 16 nodes, 462.0 g against 462 g (WARN `mass` at zero margin); the 8
electrical nodes warn `unpowered` until harness declares `E-HRN-13…16`.

## Mass (`CL-E1-MASS-PRP`, `subsystems/propulsion/parts.csv`)

| Part | Per unit | Qty | Total | Basis | Status |
|---|---|---|---|---|---|
| Motor with factory leads + 4 × M3×8 (`PRP-001`; screws `PRP-005` at 0 g) | 84.2 g | 4 | 336.8 g | listing 81.0 + ISO 3.2 | `UNVERIFIED` |
| ESC stripped (power leads off, F2's 16 AWG on the pads), signal lead, shrink | 7.6 g `EST` | 4 | 30.4 g | 6.6 g board + 1.0 g | `UNVERIFIED` |
| Prop | 17.0 g | 4 | 68.0 g | APC page | `CHECKED` |
| Adapter + 4 × M3×4 + M6 nut + washer | 6.7 g | 4 | 26.8 g | vendor 3.0 g + ISO | `UNVERIFIED` |
| **Total** | 115.5 g | | **462.0 g** | allocation 462 g (D-48) | `UNVERIFIED` |

## Losses per station (input to E3)

| Phase | Motor loss | ESC loss | Motor current | Winding rise | Status |
|---|---|---|---|---|---|
| Hover | 23.1 W | 2.4 W | 13.7 A | 23 K | `UNVERIFIED` |
| Cruise 16 m/s | 11.6 W | < 1.2 W | 7.8 A | 12 K | `UNVERIFIED` |
| Full throttle with the limiter, ≤ 10 s (`env.full_throttle_max_s`) | 86 W | 10 W | 30 A | transient | `UNVERIFIED` |

## Motor out (`CALC-E1-MOTOR-OUT`)

| Phase | What is left | Numbers | Verdict |
|---|---|---|---|
| Hover | The diagonal partner must also stop, which leaves 2 motors turning the same way | T/W 1.07 at the worst state; yaw torque 0.28 N·m against 0.16 N·m from a ±30 % differential | **Fatal**, as accepted in `CONFIGURATION.md` |
| Cruise 16 m/s | 2 motors carry 4.10 N, 179 W | 0.21 N·m roll torque for the elevons (B3) | Possibly survivable: throttle cut, FBWA glide (F4 SITL) |

## Open issues

| Issue | Owner | Status |
|---|---|---|
| Stack 37.3 vs 39 mm and the 0.14 D gap: `face_ahead_m` 2 mm | D3 / A1 | `FAIL` until CR-E1-22 |
| `performance.cruise_power_w` 218 W is stale (B1 228, E1 240 W with avionics) | A1 | `FAIL` until CR-E1-24 |
| Sag factor 0.851 (E1) vs 0.758 (E2) | E2 / A1 | open, CR-E1-25 |
| Bolt pattern, hole depth (≥ 4.0 mm), lead length unpublished | E1 / D3 | `UNVERIFIED` |
| Nut margin 0.1 mm: if the boxed adapter's post is shorter, use a flanged nut | E1 | `UNVERIFIED` |
| PER3 correction transfer, R, I0, pack IR | H1 / E2 | `UNVERIFIED` |

## How to verify

1. `python -I redesign/team/E1/propulsion.py` (writes claims, `parts.csv`, `interfaces.json`), then
   `python -I redesign/proofs/build_graph.py`: no `CALC-E1` drift.
2. `python -I redesign/interfaces/merge_check.py`: no `PRP` errors.
3. `T-E1-MOTOR-RM` on the first motor: stack (mount face to hub face − 4.45 mm), hole depth, bolt pattern, lead
   length, masses, R, I0. Update `ASM-E1-STACK` and `ASM-E1-PART-MASS`, re-run, tell D3 and A1.
4. `T-E1-STAND`: held 14.8 V, fresh pack, then a pack at 3.73 V/cell cold-soaked to 10 °C; the ratio checks
   `CL-E1-SAG-FACTOR`.

![Overall efficiency map](fig-prp-01-efficiency-map.svg)

`FIG PRP-01 — Overall efficiency against airspeed and thrust per motor; B1's drag line at 2.6 kg, cruise point 16 m/s.`

![Static thrust against current](fig-prp-02-static.svg)

`FIG PRP-02 — Static thrust against battery current per motor at a held 14.8 V; the maker's points fall below the model above 12 A (sagging supply).`
