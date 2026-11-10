# F2 harness engineer: summary

Status `PROPOSED`, F2-R1, 2026-11-09 (first output, CR-A1-40). One script, `team/F2/harness.py`, routes all 29
wires as polylines through the real pod, wing, fin and propulsion geometry, checks the installation rules and
writes the wire list, `subsystems/harness/` and 20 claims. Nothing is bench-tested. Re-run 15:32: `--check` exit 0,
outputs fresh against current inputs; SPEC gained a removable-joint table (every removable joint has a disconnect or
carries no wire; the pitot boom is pneumatic only).

## Deliverables

| File | What |
|---|---|
| `subsystems/harness/WIRE-LIST.csv` | 29 wires: from, to, signal, gauge, connector each end, cut length incl. loop, route id, supports, strain relief, disconnect, mass |
| `subsystems/harness/SPEC.md` · `BUILD.md` | one-page spec · 10 build steps |
| `subsystems/harness/params.json` | rules (with sources), groove spec, wire table, fittings, passes, CAD bundle legs (generated) |
| `subsystems/harness/interfaces.json` · `edges-pending.json` | 3 HRN parts, 11 declared edges · 21 edges waiting for `WNG/PWR/AVN/MEC` declarations (auto-promoted) |
| `subsystems/harness/parts.csv` · `fusion/harness.py` | bundles + 11 bought lines (≈ $68 `EST`) · route bodies and wires |
| `team/F2/mass_estimate.csv` · `claims.json` · `fig-hrn-01-route.svg` | A3 rows `HRN-E01…07` · proof chain · route figure |

## Action items (CR-A1-40)

| From | Asked | Done | Status |
|---|---|---|---|
| F1 | 8 AWG ≤ 0.15 m twisted | 0.038 m per conductor | `UNVERIFIED` (stack assumption) |
| F1 | 16 AWG in two taped surface grooves 5 mm apart, not buried, ≥ 0.12 m from the mast top | 3 grooves per surface ahead of the spar slot, + / − at 5 mm pitch, wire 0.5 mm under tape; 0.173 m to the mast | `CHECKED` |
| F1 | 680 µF cap at each ESC | on the board face beside the power pads, leads ≤ 20 mm | `PROPOSED` |
| E1 | phase extension ≤ 100 mm if short | reach 0.121 m, extension 0.061 m with a 60 mm motor lead (`EST`); soldered, not bulleted | `UNVERIFIED` |
| F3 | I²C ≤ 0.5 m; GPS cable alone; RX GH ≤ 150 mm twisted | 0.455 m; right leg, 90° crossings, ≥ 25 mm over the UBEC; RX 0.134 m twisted | `UNVERIFIED` (pin-out) |
| F4 | `signal.fc_port` on `E-HRN-24…29` | UR 4, UL 2, LR 1, LL 3, elevon L 5, R 6; DShot300 bidir / PWM 50 Hz | written (pending file until AVN/MEC exist) |
| D2 | exits, AS150U park | side exits on the groove line + aft exits for servos; park inboard (CR-F2-03) | `PROPOSED` |
| D3 | tie points collar and block boss | boss-tail tie + collar tie; grommeted fin hole (CR-F2-05) | `PROPOSED` |
| A3 | `mass_estimate.csv` vs 105 g | 122.6 g | **`FAIL`** (CR-F2-01) |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| ESC power leads UR / UL / LR / LL | 0.626 / 0.512 / 0.650 / 0.534 | m | `CL-F2-ESC-LEN-*` | `CHECKED` |
| Harness mass (allocation 105) / without phase extension | 122.6 / 110.9 | g | `CL-F2-MASS` | `FAIL` −17 % |
| Harness CG x / effect on aircraft CG vs A3 model | 0.067 / ≈ +1.6 | m / mm | `CL-F2-CG-X` | `CHECKED` |
| DShot longest lead (≤ 0.7) | 0.686 | m | `CL-F2-DSHOT-LEN` | `UNVERIFIED` +2 % |
| Servo voltage at stall (≥ 5.7) | 5.75 | V | `CL-F2-SERVO-V` | `UNVERIFIED` +1 % |
| Bend ratio / free span / fill | 1.07 / 0.050 m / 0.31 | — | `CL-F2-BEND`, `-FREE-SPAN`, `-FILL` | `CHECKED` |

## Checks run

| Check | Result |
|---|---|
| `python -I redesign/team/F2/harness.py` then `--check` | 20 claims; all margins ≥ 0 except `CL-F2-MASS` (−17 %); `--check` exit 0 (outputs fresh) |
| `python -I redesign/fusion/check.py` | harness module builds (3 parts, 21 bodies, 4 wires); 3 ERROR floating on the carried bundles (check.py lacks merge_check's carried exemption, CR-F2-09); overall FAIL from other modules |
| `python -I redesign/interfaces/merge_check.py` | no harness errors; WARN mass 123 > 105 g, one-sided until fins/propulsion acknowledge |
| `python -I redesign/proofs/build_graph.py` | no F2 drift or errors; warnings only for undeclared `AVN/MEC/PWR` part ids; build FAILED on other roles |

## Open issues

| Issue | Owner |
|---|---|
| Mass over allocation; harness CG aft of A3's model | A1, A3 (CR-F2-01) |
| Factory lead lengths, CoreWing pin-out, power-board stack, servo pocket side are assumptions | E1, F3, F1, D6 |
| 21 electrical/channel edges wait for `WNG/PWR/AVN/MEC` declarations | D1, F1, F3, D6 |
| Wire g/m and fitting masses `EST` until `T-F2-WEIGH` | F2 |

Change requests: `team/F2/CHANGE-REQUESTS.md` (CR-F2-01 … 12).
