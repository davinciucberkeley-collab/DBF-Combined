# H1 ground test: summary

Status `PROPOSED`, revision H1-R1, 2026-11-09. Plan and 14 test cards: `team/H1/GROUND-TEST-PLAN.md`. Rig sizing and
pass lines: `team/H1/ground_tests.py` → `claims.json` (32 claims, 3 planned rig tests). `build_graph.py`: no error or
warning on any H1 node; the build still fails on other roles' drift (A1, A5, J1). Nothing is `VERIFIED`: no hardware yet.

**One stand campaign, 25 Nov – 8 Dec, on the early-order hardware.** It runs eleven owner tests (E1, B4, C1, A1, E2, J1)
before the mid-December order: motor Rm/I0/Kv, the 11×5.5MR vs 11×4.5MR A/B with torque and rpm, peak thrust and
torque on a fresh 16.8 V pack, the installed run with tube, half-fin and wing strip, and pack weigh/capacity/IR at 25
and 10 °C. The weigh-in, CG, proof loads, tip-over, controls, restrained run and range check follow on the built aircraft.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Thrust cell range needed / rated | 2.69 / 20 | kgf | `CL-H1-THRUST-CELL-REQ` | `UNVERIFIED` (+87 %) |
| Torque cell range needed / rated (0.100 m arm) | 0.54 / 1.0 | kgf | `CL-H1-TORQUE-CELL-REQ` | `UNVERIFIED` (+46 %) |
| Noise / hover value, thrust · torque | 0.15 · 0.43 (need ≤ 0.5 · 2) | % | `CL-H1-THRUST-RES`, `-TORQUE-RES` | `UNVERIFIED` |
| Bench supply for 14.8 V sweeps | ≥ 44.6 | A | `CL-H1-SUPPLY-REQ` | `UNVERIFIED` |
| Unlimited 16.8 V step current vs ESC 10 s rating | 51.6 / 55 | A | `CL-H1-STEP-I` | `UNVERIFIED` (+6 %; step ≤ 2 s) |
| Stand pass line, fresh pack, limiter (T/W 2.0 incl. download) | ≥ 1.378 (predicted 1.62) | kgf | `CL-H1-T-PASS-FRESH` → `R-HOVER-TW` | `UNVERIFIED` (+15 %) |
| Stand pass line, 3.6 V/cell at 10 °C (T/W 1.6) | ≥ 1.102 (predicted 1.166) | kgf | `CL-H1-T-PASS-SAG` → `R-HOVER-TW` | `UNVERIFIED` (+5 %) |
| Peak thrust / torque pass, fresh 16.8 V | ≤ 21.1 / ≤ 0.42 | N / N·m | `CL-C1-T-LIMIT`, `CL-C1-MOTOR-TORQUE` | `PROPOSED` (replaces 17.8 N, CR-H1-01) |
| Weigh U95 / acceptance line | 5.2 / ≤ 2.595 | g / kg | `CL-H1-WEIGH-U95`, `-ACCEPT` | `UNVERIFIED` (5 % of A3's 108 g margin) |
| CG jig U95 / acceptance window x | 0.6 / 0.0406–0.0484 | mm / m | `CL-H1-CG-U95`, `-ACCEPT-FWD`, `-AFT` | `UNVERIFIED` |
| Wing proof, per side at y 0.328 m / tip deflection | 28.5 / ≤ 28.8 | N / mm | `CL-H1-WING-PROOF-P`, `-DEFL-MAX` | `UNVERIFIED` (C1 confirms, CR-H1-03) |
| Mount / fin-station proof | 19.6 / 46.0 | N | `CL-H1-MOUNT-PROOF-F`, `-FIN-PROOF-F` | `UNVERIFIED` |
| Pack retention pull (dummy) | 85 | N | `CL-H1-PACK-PULL-F` | `UNVERIFIED` |
| Restraint, four-motor run, total / per strap | 117.7 / 29.4 | N | `CL-H1-RESTRAINT-F`, `-PER-TIE` | `UNVERIFIED` |
| Pack capacity / IR at 10 °C acceptance | ≥ 5.98 / ≤ 7.5 | Ah / mΩ/cell | `CL-H1-PACK-CAP-MIN`, `-IR10-MAX` | `UNVERIFIED` |
| Rig cost | ≈ 160–180 `EST` | $ | `GROUND-TEST-PLAN.md` | `PROPOSED` (CR-H1-02) |

## Action items this revision

| Item | Result |
|---|---|
| One stand campaign (CR-B1-06, CR-C1-07, CR-E1-11, CR-B4-09, CR-E2-09) | GT-01…GT-05: torque cell, rpm, A/B, fresh-pack peak, installed run, pack 25/10 °C; `T-A1-WEIGH` in GT-06 |
| Use A2's evidence file names (CR-A2-10) | `team/H1/claims.json` exists; logs `team/H1/logs/<test id>_<date>.csv`; packs in `team/E2/pack_log.csv` (CR-H1-07) |

## Open issues

| Issue | Who |
|---|---|
| 17.8 N limit thrust is below C1's 21.1 N prediction; the stand decides | A1, C1 (CR-H1-01) |
| Pack-current limiter and output cap must be reproduced on one station | F4 (CR-H1-04) |
| Wing proof load points are an equivalent point; C1's whiffletree replaces them | C1 (CR-H1-03) |
| The bare tube fails mode separation (`CL-J1-TUBE-MODE-SEP`); GT-09 tap test measures the bonded fin | C4 |
| ESC temperature limit is a placeholder | E3 (CR-H1-06) |

## How to verify

`python -I redesign/team/H1/ground_tests.py` then `python -I redesign/proofs/build_graph.py` (no H1 line in the
output). Each card's pass table names its claim; the owner records the run with the H1 log as evidence.
