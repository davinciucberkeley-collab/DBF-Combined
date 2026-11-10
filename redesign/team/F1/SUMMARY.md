# F1 power distribution: summary

Status `PROPOSED`. Analysis F1-R4 (`team/F1/power.py`, 39 claims) and design PWR-R1 (`subsystems/power/`, 10 claims,
CAD `MODELLED`). Nothing is bench-tested. R4 re-runs the analysis on F2's harness re-run (ESC leads trimmed to
0.475–0.620 m), adds a check on the power-board link and acknowledges the 15 power wires. **Every F1 and PWR
check passes.** Details: `team/F1/POWER.md`, `subsystems/power/SPEC.md`.

## Decisions

| Item | Decision | Key number | Claim | Status |
|---|---|---|---|---|
| Main disconnect | **Amass AS150U**, packs re-terminated | 70 A ≥ 37.8 A; 150 A ≥ 54.3 A (1 min); 140 A ≥ 120 A | `CL-F1-AS150U-CONT`, `-SHORT`, `-BURST` | `UNVERIFIED` (reseller figures) |
| Main jumpers | **10 AWG**, 0.030 + 0.050 m | 0.5 °C above the joints (limit 10); loop 0.61 mΩ | `CL-F1-MAIN-RISE`, `CL-PWR-JUMPER-R` | `MODELLED` |
| ESC leads | **16 AWG**, routed 0.475–0.620 m (F2) | open run 9.2 °C; bundles 9.5 °C (+5 %); burst peak 23.7 °C ≤ 30 | `CL-F1-ESC-RISE`, `-BUNDLE-RISE`, `-BUNDLE-PEAK` | `MODELLED` |
| Pack's own leads | ≥ 10 AWG, 0.066–0.10 m | 16.4 °C ≤ 20 (12 AWG 28.5 °C: pack refused) | `CL-F1-PACKLEAD-RISE` | `UNVERIFIED` (gauge) |
| Path resistance | pack terminals → ESC pads | **6.69 mΩ** (R3 6.94, params 6.5): drop 1.59 % at 30 A | `CL-F1-R-EXT`, `-DROP-CONT` | `MODELLED` |
| Drop at 100 A | farthest ESC (LR 0.620 m) | **4.89 % ≤ 5 %** (+2 %); leads ≤ 0.643 m pass | `CL-F1-DROP-PEAK`, `-ESC-LEN-ALLOW` | `MODELLED` (CR-F1-25 closed) |
| Sensing | CoreWing V2 power board (`PWR-003`) | 90 / 215 A ≥ 38 / 120 A | `CL-F1-SENSOR-*` | `UNVERIFIED` (measure on arrival) |
| Power-board link | GH-6, 28 AWG: sense + 5 V only, **no Vx** | 5 V line 2.7 °C at 0.87 A; 24.7 °C if servo stall current ran in it | `CL-F1-PMOD-RISE`, `-SERVO-RISE` | `MODELLED` (CR-F1-29) |
| Protection | no propulsion fuse; 5 A fuse on the UBEC feed; 680 µF at each ESC | limiter worst case 105 A ≤ 140 A | `CL-F1-ILIM-WORST` | `MODELLED` |
| Servo rail | **UBEC 6 V 8 A kept** | SH-0255MG+ stall 1.4 A → 5.6 A > FC BEC 4.5 A | `CL-F1-SERVO-BEC-REQ`, `-UBEC-RATING` (+43 %) | `UNVERIFIED` |

## Limits and inputs (single sources)

| Limit / input | Value | Read from |
|---|---|---|
| Wire rise: steady / short (< 60 s) / pack leads | 10 / 30 / 20 °C | `P:electrical.wire_temp_rise_max_c`, `_short_max_c` (4 peak claims), `pack_lead_rise_max_c` (D-56) |
| Mission profile (wire heating) | climb 35.5 A, hover 30.1, transition 43.5 / 40.0, cruise 22.4 A (407 s) | `CL-F1-PROFILE` ← `CL-E2-*-PESS` (CR-E2-19) |
| ESC lead lengths | UR 0.595, UL 0.475, LR 0.620, LL 0.497 m | `CL-F2-ESC-LEN-*` (F2 re-run 2026-11-09) |
| FC 5 V load | 0.87 A (2 × load) | `CL-F3-5V-REQ` |

## Mass (D-48)

| Item | g | Status |
|---|---|---|
| Pack | 550 | `UNVERIFIED` (503–680 listed) |
| AS150U half + jumpers 18.6 · power board 28 · bus 7.3 · UBEC 13 · frame 9 · fuse 3.5 · caps 8.8 | 88.2 | `EST` |
| **Total vs 648 g allocation** | **638.2: passes, +9.8 g** | `CL-PWR-MASS`; avionics 45 g is F3's number |
| ESC leads (F2's harness, not power) | 70.7 (R3 75.1) | `CL-F1-ESC-MASS` |

## Checks run (2026-11-10)

| Check | Result |
|---|---|
| `python -I redesign/team/F1/power.py` | 39 claims, **all limits pass**. Tightest: `DROP-PEAK` +2 %, `BUNDLE-RISE` +5 %, `ESC-RISE` +8 % |
| `python -I redesign/team/F1/draw_schematic.py` | `power-schematic.svg` redrawn (0.47–0.62 m, link "no Vx") |
| `python -I redesign/subsystems/power/make_power.py`, `power_claims.py` | 10 claims pass; `CL-PWR-MASS` 638.2 ≤ 648 g; 15 harness edges acknowledged |
| `python -I redesign/interfaces/merge_check.py` | PASS, 0 errors; **0 power warnings**. E-HRN-22/-23 wait for avionics' acknowledgement |
| `python -I redesign/proofs/build_graph.py` | **0 F1 / PWR errors.** One downstream drift: F3 `CALC-F3-MAG` (I_cont 30.26 → 30.27 A, from R3; F3 re-runs). The build fails overall on other roles' drift (632 errors, none F1 or PWR) |

## Open issues

| Issue | Owner |
|---|---|
| `electrical.r_ext_mohm` 6.5 → **6.7**; E1, E2, E3 and H1 re-run | A1 (CR-F1-24 rev) |
| Vx not on the link; servo/motor headers on FC or PDB? Measure the PDB outline (52 × 32 assumed), pads and mass | F3 on arrival (CR-F1-26, -29) |
| Acknowledge E-HRN-22, -23 | F3 (CR-F1-30) |
| `ASM-F2-WIRE-GPM` cites `CL-F1-W16-GPM`; keep ESC cuts ≤ 0.640 m | F2 (CR-F1-28) |
| E2 text reference to `ASM-F1-PROFILE` | E2 (CR-F1-27) |
| Amass sheet, UBEC datasheet, unplug force, straw heat run | F1, I1 (`T-PWR-ARRIVAL`, `T-F1-WIRE-HEAT`) |

Change requests: `team/F1/CHANGE-REQUESTS.md` (CR-F1-01 … 30; the R4 section closes CR-F1-25 and the E-HRN acks).
