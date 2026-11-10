# A1 chief engineer: integration round, revision A1-R4a

Status: `PROPOSED` frame at revision **A1-R4** (D-47 … D-58) plus addendum **A1-R4a** (D-59), 2026-11-09.
Re-derive: `python -I redesign/team/A1/frame_claims.py` (22 claims, also writes `params/mass_budget.json`), then
`python -I redesign/proofs/build_graph.py`. `interfaces/merge_check.py` now **passes** (0 errors; CG 0.051 m).

## Action items this round

| Item | Decision | Numbers | Status |
|---|---|---|---|
| CG 2.7 mm aft of the aft limit (CR-A4-36, CR-A5-20, CR-A3-22) | **D-47:** pod nose −0.115 → −0.130, nose stack 14.8 → 8.8 mm, whole pack bay 21 mm forward, datum `pod.pack_x_nominal_m` −0.022. Pod group (saddle `POD-007` cannot move), stations (not buildable), power boxes (−3.4 of 5.5 mm) and ballast (≈ 70 g) rejected | 0.0577 `FAIL` → 0.0513 m basic, 0.0526 predicted (A3, all nine parts.csv) | `MODELLED` |
| B3's range (CR-B3-17) | adopted rounded inward: 0.050–0.0549 m, target 0.0522 | B3 0.04953 / 0.05495 | `UNVERIFIED` (B3) |
| Re-check after the parts got lighter aft | **D-59:** aft travel 8 → 12 mm (`pod.pack_aft_travel_m`, aft stop 0.060), spacer step 2 mm (`pod.pack_spacer_step_m`); each pack flies at the step nearest the target | 680 g needed 9.5 mm aft (A3); see the table below | `MODELLED` |
| R4 503 g station −0.0245 | superseded by the D-59 rule | it gave 0.0551 m predicted, 0.2 mm aft of the limit, on the A3-R5 roll-up | closed |
| Six allocations over (CR-A4-37, CR-A3-21) | **D-48:** allocations 2 355 g (power 648 with the 28 g PWR-003 board, avionics 45, harness 123, mechanisms 80, fins 418, pod 131, propulsion 462 with stripped ESC leads); reserve 245 g | every subsystem now inside (`CL-A3-ALLOC-WORST` 1.00, propulsion 462.0 / 462) | `MODELLED` |
| `frame_claims.py` drifts | `CALC-A1-PACK-STATION` replaced by `CALC-A1-PACK-CASES` (reads A3's live CG and mass, recovers the empty moment, checks every pack); A1 re-runs clean | 22 claims, no drift in A1 | `CHECKED` |

## Pack stations (D-59, `CALC-A1-PACK-CASES` on A3's 20:35 roll-up)

| Pack | Station x (m) | Spacer | CG basic → predicted (m) | Margin | Status |
|---|---|---|---|---|---|
| 550 g (carried) | −0.018 | 8 mm | 0.0522 → 0.0536 | fwd +2.2 / aft +1.3 mm | `MODELLED` |
| 503 g | −0.024 | 14 mm | 0.0523 → 0.0538 | aft +1.1 mm; 1.4 mm travel left | `MODELLED` |
| 680 g | −0.010 | none | 0.0507 → 0.0520 | fwd +0.7 mm | `MODELLED` (thin) |

## Key numbers (2.6 kg gate)

| Claim | Value | Limit | Margin | Status |
|---|---|---|---|---|
| `CL-A1-PACK-CG-FWD` / `-AFT` | +0.7 / +1.1 mm | ≥ 0 | — | `UNVERIFIED` (A3, B3 inputs) |
| `CL-A1-PACK-STATION` (503 g travel left) | 1.4 mm | ≥ 0 | — | `UNVERIFIED` (D2 re-lays) |
| `CL-A1-NOSE-BALLAST` | 0 g | ≤ 10 g | — | `UNVERIFIED` |
| `CL-A1-MASS-SIZED` / `-RESERVE-COVERS` | 2.600 kg / 0 g | ≤ 2.6 kg / ≥ 0 | +0 % | `UNVERIFIED` (A3: predicted 2 419 g, +181 g) |
| `CL-A1-HOVER-TW-GATE` / `-SAG` | 2.49 / 2.12 | ≥ 2.0 / 1.6 | +25 % / +33 % | `UNVERIFIED` (stand) |
| `CL-A1-STALL-GATE` / `-TRANSITION-GATE` | 11.91 / 15.48 m/s | ≤ 12 / 16 m/s | +1 % / +3 % | `UNVERIFIED` |
| `CL-A1-CG-RANGE-FWD` / `-AFT` | +0.5 / +0.05 mm | ≥ 0 | — | `UNVERIFIED` (B3) |
| `CL-A1-TIPOVER` | 30.6° | ≥ 30° | +2 % | `UNVERIFIED` (C5 re-runs at the new CG) |
| `CL-A1-PROP-CLEAR` / `CL-A1-BOX-FIT` | 34.6 mm / 2 mm | ≥ 25 mm / ≥ 0 | +38 % / — | `UNVERIFIED` / `CHECKED` |
| `CL-A1-RESERVE` | $313 | ≥ $309 | +1 % | `UNVERIFIED` (I1) |

## Open issues

1. **merge_check / check.py**: the CG error is gone in both (0.051 m). `check.py` still fails on 16 prop keep-out errors (E1's `prop_keepout` rotation, CR-A1-48) and two D2 parts with no mass (`POD-009/010`, D2-R5 in progress). The only mass warning is a float tie, "462 g > 462 g" (CR-A1-55 to A4).
2. **The 680 g pack** is 0.7 mm inside the forward limit and still fails the 100 g overrun rule (+51 g). The SKU line is now 631 g (CR-A1-56); E2 decides.
3. **A3's own station claims** (`CL-A3-CG-X-STATIONS` 1.17, `CL-A3-PACK-TRIM` 1.5 mm) still read 8 mm of aft travel: CR-A1-53. The predicted CG uses `ASM-A1-CG-GROWTH-DX` 1.4 mm until A3 publishes it.
4. **Re-runs owed** on D-47/D-59: D2 (aft stop 0.060, CR-A1-54), B3 (`CALC-B3-CG-CHECK`), C5 (crash per pack, tip-over), B4 (pitot −0.210), D7 (nose pad). `CL-A1-CG-CENTRED` reads B3's R3 pack-centred CG and refreshes when B3 re-runs.
5. Earlier open items (box height veto by car, budget reserve $4 over the crash cost) are unchanged; see `params/CHANGE-LOG.md` D-53 and D-57.

Files: `params/params.json` (two new keys, one note), `params/CHANGE-LOG.md` (D-59, A1-R4a row), `MASS-CG.md` (hand-written sections), `README.md` (two rows), `team/A1/frame_claims.py`, `team/A1/claims.json`, `team/A1/CHANGE-REQUESTS.md` (CR-A1-53 … 56).
