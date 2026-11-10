# F1 power distribution: summary

Status `PROPOSED`. Analysis F1-R3 (`team/F1/power.py`, 37 claims) and design PWR-R1 (`subsystems/power/`, 10 claims,
CAD `MODELLED`). Nothing is bench-tested. R3 re-runs the analysis on F2's routed ESC leads, the 10 AWG jumpers,
E2's phase claims, the D-56 limit keys, D6's servo and D-48. Details: `team/F1/POWER.md`,
`subsystems/power/SPEC.md`.

## Decisions

| Item | Decision | Key number | Claim | Status |
|---|---|---|---|---|
| Main disconnect | **Amass AS150U**, packs re-terminated | 70 A ≥ 37.8 A; 150 A ≥ 54.3 A (1 min); 140 A ≥ 120 A | `CL-F1-AS150U-CONT`, `-SHORT`, `-BURST` | `UNVERIFIED` (reseller figures) |
| Main jumpers | **10 AWG**, 0.030 + 0.050 m | 0.5 °C above the joints (limit 10); loop 0.59 mΩ | `CL-F1-MAIN-RISE`, `CL-PWR-JUMPER-R` | `MODELLED` |
| ESC leads | **16 AWG**, routed 0.512–0.650 m (F2) | open run 9.2 °C; bundles 9.5 °C (+5 %); burst peak 23.7 °C ≤ 30 | `CL-F1-ESC-RISE`, `-BUNDLE-RISE`, `-BUNDLE-PEAK` | `MODELLED` |
| Pack's own leads | ≥ 10 AWG, 0.10 m | 16.4 °C ≤ 20 (12 AWG 28.5 °C: pack refused) | `CL-F1-PACKLEAD-RISE` | `UNVERIFIED` (gauge) |
| Path resistance | pack terminals → ESC pads | **6.94 mΩ** (was 6.5): drop 1.64 % at 30 A | `CL-F1-R-EXT`, `-DROP-CONT` | `MODELLED` |
| Drop at 100 A | farthest ESC (LR 0.650 m) | **5.03 % vs 5 %: fails by 0.03 pp**; leads ≤ 0.643 m pass | `CL-F1-DROP-PEAK`, `-ESC-LEN-ALLOW` | open, CR-F1-25 |
| Sensing | CoreWing V2 power board (`PWR-003`) | 90 / 215 A ≥ 38 / 120 A | `CL-F1-SENSOR-*` | `UNVERIFIED` (separation, CR-F1-26) |
| Protection | no propulsion fuse; 5 A fuse on the UBEC feed; 680 µF at each ESC | limiter worst case 105 A ≤ 140 A | `CL-F1-ILIM-WORST` | `MODELLED` |
| Servo rail | **UBEC 6 V 8 A kept** | SH-0255MG+ stall 1.4 A → 5.6 A > FC BEC 4.5 A | `CL-F1-SERVO-BEC-REQ`, `-UBEC-RATING` (+43 %) | `UNVERIFIED` |

## Limits and inputs (single sources)

| Limit / input | Value | Read from |
|---|---|---|
| Wire rise: steady / short (< 60 s) / pack leads | 10 / 30 / 20 °C | `P:electrical.wire_temp_rise_max_c`, `_short_max_c`, `pack_lead_rise_max_c` (D-56) |
| Mission profile (wire heating) | climb 35.5 A, hover 30.1, transition 43.5 / 40.0, cruise 22.4 A (407 s) | `CL-F1-PROFILE` ← `CL-E2-*-PESS` (CR-E2-19) |
| ESC lead lengths | UR 0.626, UL 0.512, LR 0.650, LL 0.534 m | `CL-F2-ESC-LEN-*` (CR-F2-02) |

## Mass (D-48)

| Item | g | Status |
|---|---|---|
| Pack | 550 | `UNVERIFIED` (503–680 listed) |
| AS150U half + jumpers 18.6 · power board 28 · bus 7.3 · UBEC 13 · frame 9 · fuse 3.5 · caps 8.8 | 88.2 | `EST` |
| **Total vs 648 g allocation** | **638.2: passes, +9.8 g** | `CL-PWR-MASS`; avionics 45 g is F3's number |

## Checks run (2026-11-09)

| Check | Result |
|---|---|
| `python -I redesign/team/F1/power.py` | 37 claims. Two fail by 1 % (`DROP-PEAK`, `ESC-LEN-ALLOW`), both from the same LR length. All six rise claims pass on the D-56 keys |
| `python -I redesign/team/F1/draw_schematic.py` | `power-schematic.svg` redrawn (10 AWG jumpers, routed lengths) |
| `python -I redesign/subsystems/power/power_claims.py`, `make_power.py` | 10 claims pass; `CL-PWR-MASS` 638.2 ≤ 648 g |
| `python -I redesign/proofs/build_graph.py` | **0 F1 / PWR errors.** R3 causes drift downstream in F2 `CALC-F2-SERVO-V` (stall 1.4 A) and F3 `CALC-F3-MAG` (I_cont +0.01 A). The build fails overall on other roles' drift |
| `python -I redesign/interfaces/merge_check.py` | 0 power errors; `PWR-*` stay unconnected until F2 declares the harness edges |

## Open issues

| Issue | Owner |
|---|---|
| LR lead is 7 mm over the length that keeps the drop at 5 %: trim it, or use 14 AWG on LR | F2 (CR-F1-25) |
| CoreWing PDB joins the FC by header pins: order the unsoldered-pins SKU. Outline assumed 52 × 32 mm, longer than the 42 mm deck; measure on arrival | F3, D2 (CR-F1-26) |
| `electrical.r_ext_mohm` 6.5 → 6.9; E1, E2, E3 and H1 re-run | A1 (CR-F1-24) |
| Acknowledge E-HRN-10…16, -21…23, -33…37: **pending** F2's `harness.py` re-run (the edges are still pending) | F2, then F1 |
| F2 per-metre wire mass source, stall re-run, stack description | F2 (CR-F1-23) |
| Amass sheet, UBEC datasheet, unplug force, straw heat run | F1, I1 (`T-PWR-ARRIVAL`, `T-F1-WIRE-HEAT`) |

Change requests: `team/F1/CHANGE-REQUESTS.md` (CR-F1-01 … 27; the R3 section answers CR-F2-02, CR-E2-19 and CR-D6-06).
Sources checked 2026-11-09: ArduPilot CoreWing F405 Wing V2 page; ReadyMadeRC listing 87195 (3-board stack, PDB
11.4 g, cable and pin-header set); Oscar Liang's SpeedyBee F405 Wing APP review (boards joined by header pins).
