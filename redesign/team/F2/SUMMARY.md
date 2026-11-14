# F2 harness engineer: summary

Status `PROPOSED`, F2-R3, 2026-11-10. One script, `team/F2/harness.py`, routes 36 wires (28 electrical edges) as
polylines through the real pod, power stack, wing, fin and propulsion geometry, checks the install rules and writes
the wire list, `subsystems/harness/` and 26 claims. Nothing is bench-tested. `--check` now fails on a broken install
rule as well as on a stale file. Before R3 it only checked staleness, which is how a 50.4 mm free span got through.

## Action items (CR-A4-38a/b, CR-A5-24, CR-A3-21, CR-A1-45)

| Asked | Done | Status |
|---|---|---|
| Promote the 21 parked wires (E-HRN-02/04, -10…16, -21…32) | `edges-pending.json` is empty; all 37 edges are in `interfaces.json`; `fusion/harness.py` draws 28 wires | `CHECKED`: check.py and merge_check report no unconnected or unpowered part |
| CR-F1-18: E-HRN-21 bus → fuse PWR-007; E-HRN-33 PWR-007 → PWR-005; E-HRN-34…37 PRP-002 → PWR-008 (CT-SOLDER-DC, ≤ 20 mm); E-HRN-11/12 10 AWG | all done; cap legs 0.011 m; 10 AWG jumpers 0.030 / 0.050 m | `CHECKED` (calc) |
| Wire ends on F3's port points (CR-F3-16) and F1's PWR-R1 stack | `PORTS` table in the script, each point sourced | `UNVERIFIED` (F3 points ±10 mm) |
| Servo lead through D1's lower pocket; fin hole 22 mm off the skin (CR-D3-23) | read from `wing/params.json#servo_pocket` and `fins/params.json#wire_hole` | `MODELLED` |
| HRN-002-R/L CG from the bodies | bundle legs sized by wire mass; body vs wire CG gap 0.5 mm (wing-fin), 6.4 mm (pod) | `CHECKED` ≤ 10 mm |
| parts.csv priced for I1 | HRN-101…112, ≈ $68 | `UNVERIFIED` prices |
| D-48: allocation 123 g | 117.3 g routed | `CHECKED` +5 % |
| A4 OWED: `E-HRN-34…37` had no `current_a` / `signal` block | `current_a` {cont 4.2, peak 12.4 A, kind "AC ripple RMS, no DC"} from new `CALC-F2-CAP-RIPPLE` (I_esc √(D(1−D)) ≤ 0.5 I_esc; I_esc 8.4 A hover = 27/4 × 1.25, 24.8 A max); rating check asked of F1 (CR-F2-18) | `MODELLED`; data block in `subsystems/harness/interfaces.json` |
| Found in R3: phase free span 50.4 mm > 50, and the route tie sat 18 mm from D3's collar lug | tie moved to the collar-tail front (x 0.060), read from D3's `fins.geometry()`; free span 47 mm; CR-F2-16 asks D3 to move the lug there | route `CHECKED`; lug `PROPOSED` |

## Key numbers

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| ESC power leads UR / UL / LR / LL | 0.595 / 0.475 / 0.620 / 0.497 | m | `CL-F2-ESC-LEN-*` | `CHECKED` |
| Harness mass (allocation 123) / without phase extension | 117.3 / 106.4 | g | `CL-F2-MASS` | `CHECKED` +5 % |
| Harness CG x | 0.064 | m | `CL-F2-CG-X` | `CHECKED` |
| Phase reach / extension (≤ 0.10) | 0.116 / 0.056 | m | `CL-F2-PHASE-REACH`, `-EXT` | `UNVERIFIED` (motor lead length) |
| DShot longest (≤ 0.7) / I²C (≤ 0.5) / RX (≤ 0.15) | 0.674 / 0.461 / 0.116 | m | `CL-F2-DSHOT-LEN`, `-I2C-LEN`, `-RX-LEN` | `UNVERIFIED` +4 % / +8 % / +23 % |
| Servo voltage at stall (≥ 5.7) | 5.73 | V | `CL-F2-SERVO-V` | `UNVERIFIED` +1 % |
| ESC cap-leg ripple, hover / max (RMS, upper bound) | 4.2 / 12.4 | A | `CL-F2-CAP-RIPPLE-CONT`, `-PEAK` | `MODELLED`; `UNVERIFIED` until `T-F1-RIPPLE` |
| Bend ratio / free span (≤ 0.05) / fill (≤ 0.40) | 1.02 / 0.047 / 0.31 | — / m / — | `CL-F2-BEND`, `-FREE-SPAN`, `-FILL` | `CHECKED` |

## Checks run (2026-11-10)

| Check | Result |
|---|---|
| `python -I redesign/team/F2/harness.py` then `--check` | 26 claims, every margin ≥ 0; no rule failures, no stale files; exit 0 |
| `python -I redesign/fusion/check.py` | harness module ok (3 parts, 31 bodies, 28 wires, 117 g, 0 errors); overall FAIL comes from propulsion keep-outs on the fins and wing |
| `python -I redesign/interfaces/merge_check.py` | PASS; the only harness warnings are one-sided edges: wing `E-HRN-02/04`, avionics `E-HRN-22…32` |
| `merge_check.py --root redesign/subsystems --out <scratch>` (after the cap fix) | PASS, 0 errors, 17 warnings (one-sided only); merged `E-HRN-34…37` carry `current_a`. The integrated `interfaces/interfaces.json` picks it up on the integrator's next merge run |
| `python -I redesign/proofs/build_graph.py` | no F2 drift or error; FAILED on A5, C4, H1 and J1 drift |

## Open issues

| Issue | Owner |
|---|---|
| Collar tie lug at x 0.084 must move to 0.060, slot along x | D3 (CR-F2-16) |
| Wing and avionics edge acknowledgements | D1 (CR-F2-14), F3 (CR-F2-17) |
| F1 re-run on the R3 lead lengths | F1 (CR-F2-13) |
| `PWR-008` ripple rating vs 4.2 / 12.4 A RMS on the cap legs | F1 (CR-F2-18) |
| Factory lead lengths, CoreWing pin-out, wire g/m and fitting masses stay `EST` until `T-E1-MOTOR-RM`, `T-F2-WEIGH`, `T-F2-FIT` | E1, F3, F2 |

Change requests: `team/F2/CHANGE-REQUESTS.md` (CR-F2-01 … 18, status table at the end).
