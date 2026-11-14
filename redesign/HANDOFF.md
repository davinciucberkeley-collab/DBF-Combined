# Hand-off to the team — K09-L, 2026-11-10

Written by A1 (chief engineer) at the end of the design program. Everything below is for people with hands,
accounts, licences and money; the agents cannot do it. Earlier A1 hand-off notes (pack thresholds, the retired pod
rule): [`team/A1/HANDOFF.md`](team/A1/HANDOFF.md).

## 1. Read first (about one hour)

| Order | Read | For |
|---|---|---|
| 1 | [`README.md`](README.md) | the aircraft, key numbers, who owns what |
| 2 | [`STATUS.md`](STATUS.md) | what is done, what fails, what is unverified |
| 3 | [`CONFIGURATION.md`](CONFIGURATION.md) | why K09-L, its price, the reverse-to-K01 conditions |
| 4 | [`MASS-CG.md`](MASS-CG.md) verdict table | mass and CG, the two numbers that decide whether it flies |
| 5 | [`team/A2/VERIFICATION-MATRIX.md`](team/A2/VERIFICATION-MATRIX.md) header | the 11 failing requirements and why |
| 6 | [`team/I1/ORDER-PLAN.md`](team/I1/ORDER-PLAN.md) | what to buy, when, and what is unconfirmed |
| 7 | [`team/H1/GROUND-TEST-PLAN.md`](team/H1/GROUND-TEST-PLAN.md) | the 18 test cards and the Jacobs equipment questions |
| 8 | [`params/CHANGE-LOG.md`](params/CHANGE-LOG.md) "Revision A1-R5" | the decisions the simulation round forced |

## 2. Decisions only humans can make

| # | Decision | Options | A1's position | By |
|---|---|---|---|---|
| H1 | **Keep K09-L or reverse to K01-lean** | keep; reverse if the twin fails the 5 m/s hover or a transition, if K01-lean's reserve is verified ≥ $309, or if RFS wind ≥ 1.4 × RCMC1 | keep until the twin flies; decide at the December order | 15 Dec |
| H2 | **Ask Jacobs staff four questions** (`team/H1/JACOBS-LOAN-REQUEST.md`, rewritten 2026-11-13): flux and wick at the stations, K-type multimeter, hot-wire or ShopBot on foam, Spring 2027 pass. The pass is paid outside the budget; it is in-lab access, not loans | ask in the Electronics Lab or by email from a Berkeley account; file the reply | nothing waits on it: soldering is in the lab, the hot wire is bought (G11, H05) | before 20 Nov |
| H3 | **Run BuildAll in Fusion 360** once | any teammate with a licence (`fusion/README.md` steps 1–6) | the first run is the test of `fusion_backend.py`; report FAIL/ERROR lines to A5 unchanged, do not fix geometry by hand | next week |
| H4 | **Approve and pay the 20 Nov order** (~$1 091, R4: includes the hot-wire supply `G11`) | read every cart total; the pack cart first | pay only after the checks in §4 | 20 Nov |
| H5 | **Name the two cars** for `subsystems/transport/CAR-FIT.md` (box 1.25 × 0.55 × 0.54 m) | — | before the box is cut (January) | Dec |
| H6 | **Name the pilot** and confirm RFS site rules, FAA registration ($5), Remote ID if flown outside the FRIA | — | pilot flies the twin first, then SITL ≥ 10 h | Dec |
| H7 | **Collar height** (CR-C6-37): 22 mm now, or coupon `T-C6-LAP-PETG` first then size | +4.4 g from a 0 g reserve either way | wait for C4's re-run (CR-C6-38); no collar prints before | before the December Aloft cart |
| H8 | **Decided (D-98, 2026-11-13).** A1's mid-band pack-station rule; the balance test overrides it | — | — | done |
| H9 | **Decided (D-96).** `cg.z_range_m[0]` 0.010 → 0.0165 m; stall line re-derived to 12.3 m/s on the integer `AIRSPEED_MIN` | — | — | done |
| H10 | **Decided (D-97).** Carry 253 W at 16 m/s, L/D 5.66; E2 re-ran (11.4 / 6.0 min) | — | — | done |
| H11 | **Ground-test purchases** $26 (strain gauges G12, G13; CR-H1-25), $6 over the D-39 line | buy / borrow | buy: the fin-proof decision needs them | 20 Nov cart |

## 3. Before the mid-December order: de-risking checklist

Mandatory items from `CONFIGURATION.md`, with what the design round added.

| # | Item | Pass line | Owner | By |
|---|---|---|---|---|
| D1 | Build and fly the **$40 foam-board twin** (Box Kite guide) on the real motors, FC and pack | holds position within 1 m in 5 m/s; then one transition round trip | H2, G2, F4 | early Dec |
| D2 | **Fixed-wing tune first**: hand-launch and tune the twin as a plain flying wing before any transition | stable FBWA flight | H2, F4 | with D1 |
| D3 | **Slow-flight stall on the twin** at the gate mass and the forward CG, airspeed logged, three runs (`T-B2-STALL`, D-71) | ≤ 12.3 m/s (D-96); sets `AIRSPEED_MIN` = ceil(1.3 × measured): 16 up to 12.31 m/s, else 17 with `AIRSPEED_CRUISE` 17 (holds to 13.07 m/s) | H2, B2, F4 | before `ARSPD_FBW_MIN` is frozen |
| D4 | **≥ 10 h SITL** on a stable ArduPilot Plane tailsitter build for the CoreWing F405 Wing V2 | SITL installed; `K09L.param` loads; transitions and failsafes exercised | F4, F3 | 15 Dec |
| D5 | **Handheld anemometer at RFS** vs the RCMC1 station, mornings 07–10 | ratio < 1.4 | H3, B1 | Dec |
| D6 | **Early order (~20 Nov)** of electronics, two packs, one US-stock carbon tube, props (§4) | all received, weighed, logged | I1, E2 | 20 Nov |
| D7 | **Bend-test the carbon tube** (`T-C4-TUBE-BEND`, with GJ): decides Aloft vs overseas tubes for the December cart | E, G within the `ASM-*` band | C4, H1 | 10 Dec |
| D8 | **Jacobs staff answers** (H2 above; no purchase waits on them since R4) | in hand | team | 20 Nov |
| D9 | **Weigh the first pack and the first tube on arrival**; log in `team/E2/pack_log.csv`; confirm 10 AWG leads and 135 mm length | pack ≤ **560 g** (`CL-A3-PACK-ACCEPT`, one line since D-95); spar ≤ 112 g | E2, A3 | arrival |
| D10 | **Confirm the FC build and board variant** (CoreWing F405 Wing APP V2, not Mini; output pads and Vx location) before the FC cart | `T-F3-ARRIVAL` | F3 | before 20 Nov |

Before the first hover of the real aircraft (not before the order): cant sense on every mount with an inclinometer
and a hanging yaw test (D-52); blade-to-tube gap with the 25 mm gauge (D-61); pack station mark for the weighed pack
(D-62); CG balance on the 0.0466 / 0.0514 m marks (GT-07).

## 4. What to order

From `team/I1/ORDER-PLAN.md` (I1-R3). Prices are 2026 list before 10.25 % tax; `EST` shipping. Re-read every listing
on order day (`T-I1-LISTINGS`), log in `team/I1/listing_log.csv` (new file), re-run `build_bom.py`.

### Early order, ~20 Nov — $1 091 (goods $921 + tax $94 + shipping $75 `EST`; R4 2026-11-13 adds `G11`; the Amazon row and totals below are regenerated by `team/I1/make_order_plan.py`, see `ORDER-PLAN.md`)

Purpose: the twin, the thrust stand, charging, first power bench on real hardware.

| Vendor | Lines | With tax | Confirm before paying |
|---|---|---|---|
| Ampow / OVONIC | `P01` 2 × 4S 6500 120C hard case EC5 | $126 (pess. $131) | **place first, ~14 d from Germany**; no USD price found; ask the seller for ≥ 10 AWG leads (12 AWG → stop, tell E2 / F1); not the 130C XT60 SKU (680 g) |
| Amazon | ESCs `B02`, wire, tools, chargers, hot-wire supply + wire (`A05`, `A06`, `W02`, `W06`, `W07`, `F01`–`F09`, `G01`, `G04`–`G06`, `G11`, `G12`) | $375 | **LANRC 45 A 4-pack ASIN unconfirmed** (page 503); fallback Tekko32 F4 45A AM32 +$60; many `EST` lines |
| SunnySky USA | `B01` 5 × X3108S KV900 | $138 | page returned 429; price from a search snippet; measure bolt pattern, hole depth, leads on arrival |
| RadioMaster | `A03` RP3 V2 receiver, `R01` Pocket (Crush) | $94 | **FCC variant** for both, not LBT |
| ReadyMadeRC | `A01` CoreWing F405 Wing APP V2 | $74 | F3 gate: stable tailsitter build confirmed; product page moved |
| APC | `B03` 8 × 11×5.5MR/MRP, `B04` 4 × 11×4.5MR/MRP, `B05` rings | $57 | props `CHK` $3.83 |
| DigiKey | `H01` JST-GH | $45 | separate shipping; pigtails if the cart allows |
| GetFPV | `R02` 18650 cells | $27 | RadioMaster ships cells only with a radio |
| Aloft Hobbies | `W03` one US-stock CF 22 × 20 × 1 000 tube | $26 | weigh on arrival; the December tubes follow the bend test |
| RaceDayQuads, Pyrodrone, Bolt Depot | `A02`, `G02`, `B07`, `C01` | $52 | Bolt Depot minimum order |
| Harbor Freight (store) | `G03` ammo can, before the first charge | $22 | — |

### Mid-December order, 15 Dec — $431 (goods $350 + tax $36 + shipping $45 `EST`)

Place the **Aloft carbon cart first** (motor tubes `W04` × 2, strips `D01`–`D03`, 20 × 18 tube), then the rest.

| Vendor | Lines | With tax | Confirm |
|---|---|---|---|
| Aloft Hobbies | `W04` × 2, `D01`, `D02` × 3, `D03` | $106 | Aloft or overseas by the 10 Dec bend test; strips `EST` |
| Savox USA / dealer | `M01` × 2 SH-0255MG+ | $93 | single-source; 7-day lead; price from D6, not re-read |
| Amazon | `A07`, `H03`, `C02`–`C06`, `D04`–`D06`, `G13` | $107 | `EST` lines |
| West3D | `W05`, `W08` ASA filament | $51 | ASA is not in Jacobs stock |
| Amazon / hobby shop | `H02`, `D07` | $30 | — |
| Home Depot El Cerrito (store; XPS and bow stock late Nov / early Dec for the practice cores) | `W01` XPS sheet, `H05` hot-wire bow stock | $83 | check the sheets are flat |

### Gated lines (held, not in the totals)

Bought only when the realised reserve after the December receipts is ≥ $309 plus the line: `X01` spare ESC 4-pack
$33, `X02` third servo $46, `X03` 11×5.5E pair $18, `X04` packs 3–4 $91, `X05` CNC prop adapters $26, `X06` Remote ID
$44 (only outside the FRIA), `X07` box and field kit $150 (before the first drive to the field), `X08` airspeed
sensor $66 (last), `X09` thermocouple logger $17 (only if no lab meter reads K-type) and `X10` flux and wick $17 (only if the Electronics Lab has none). The old `X10` soldering kit and `X11` hot-wire gear are closed (2026-11-13): the Jacobs Maker Pass covers the lab's soldering station and meters, and the hot-wire gear is bought (not on the Jacobs list).

## 5. Who owns what next week

Fill the name column at the first team meeting. One person per row; the agent roles stay as the paper trail.

| Area | Agent roles | Name | This week |
|---|---|---|---|
| Team lead | A1, I2 | | decisions H1–H11; January–April schedule with one crash-repair loop (`R-SCHEDULE`, `R-BUILD-HOURS`) |
| Fusion / CAD | A5, D1–D7 | | BuildAll run (H3); report; D5 draws the D-65 sleeve; D3 holds collars and pins |
| Procurement | I1, E2 | | Jacobs request sent (H2); listings re-read; carts built; pack cart first; arrival weigh-ins |
| Structures | C1, C4, C6, D3 | | C4 re-solves the fin station on the D-65 loads (CR-C6-38); collar decision (H7); coupon plan with the first prints |
| Aero | B1, B2, B3 | | reconcile CLmax (0.862 vs 0.787) and the NP; B3 re-runs on the D-62 bay; CR-B2-20 |
| Mass and CG | A3 | | re-run after D5-R5 and F1's pack node; one acceptance line; stations for the flight card |
| Flight software and avionics | F4, F3, F5 | | install SITL; load `K09L.param`; 10 h plan; FC variant check; FCC radio variants |
| Test | H1, H2, H3 | | twin build plan with G2; thrust stand parts list; flight card (5 m/s, mornings, roll-stabilised modes only); RFS anemometer; FAA registration |
| Manufacturing | G1–G4 | | process plan, hot-wire jig and S5010 templates, print list (PETG / ASA), build steps for the manual |
| Documentation and review | J3–J6 | | renders from `blender/`, build manual from `manual-kit/`, the overview page, then the design review board |

Re-check before any meeting: `python -I redesign/team/A1/frame_claims.py` · `python -I redesign/team/A3/mass_rollup.py --check` ·
`python -I redesign/fusion/check.py` · `python -I redesign/interfaces/merge_check.py` · `python -I redesign/proofs/build_graph.py`.
