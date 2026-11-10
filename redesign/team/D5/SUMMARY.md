# D5 Landing feet: summary (revision D5-R4, 2026-11-09)

Subsystem `subsystems/landing/` (prefix GER), params A1-R3. Four telescoping crush feet on the half-fin TE tips plus
two TPU wingtip corner caps. R4 adopts C5-R3's pre-crushed, biased cartridges and corrects the per-landing wear model.

## What changed in R4

| Item | R3 | R4 | Why |
|---|---|---|---|
| Cartridge section (y × z) | 16 × 13.3 mm | 17.3 × 13.3 mm | C5-R3 plateau 39.4 N upper (CR-C5-10 revised) |
| Type-L bore | 6.35 mm (1/4 in) | 5.56 mm (7/32 in) | bias 1.05 (got 1.056) |
| Pre-crush | none, peak 1.10 | 1 mm per segment, peak = plateau | removes both first-yield peaks |
| Shoe legs | 10 mm | 7 mm | pays the +1.4 g of the wider foot |
| Replace mark | 6 mm | 3 mm | the mark now keeps the 3 mm guard + C5's 31.5 mm |
| Elastic credit per landing | 5 % strain | 2 % strain | the 5 % knee is mostly plastic |
| Ground spares | notes only | nodes with `"flight": false` | CR-A3-18 |

## Key results

| Quantity | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Plateau upper / lower / mean | 39.6 / 35.4 / 37.49 | N | `CL-D5-F-PLATEAU-*` | `UNVERIFIED` |
| Peak upper limit / ult (C1 bound 41.2 / 60.8) | 39.6 / 59.4 | N | `CL-D5-F-PEAK-UPPER`, `-F-ULT-UPPER` | `UNVERIFIED` |
| Level 1.5 m/s landing: stroke / n / η | 23.0 mm / 5.88 / 0.90 | — | `CL-D5-STROKE-USED`, `-N-LAND`, `-ETA` | `UNVERIFIED` |
| Usable stroke vs C5 pair-first | 35 vs 31.5 | mm | `CL-D5-STROKE-USABLE` | `UNVERIFIED` |
| Set per 0.5 m/s landing / sink with no set | 1.28 / 0.32 | mm / m/s | `CL-D5-SET-NORMAL`, `-V-NO-SET` | `UNVERIFIED` |
| Tip-over at target / worst flying CG (≥ 30) | 34.7 / 30.6 | deg | `CL-D5-TIPOVER-NARROW`, `-CORNER` | `UNVERIFIED` |
| Bond RF / flange SF / rim SF / tine SF | 1.54 / 2.69 / 1.18 / 3.52 | — | `CL-D5-BOND-SF` etc. | `UNVERIFIED` |
| Mass (4 feet + 2 caps) vs allocation | 42.50 vs 43 | g | `CL-D5-MASS-TOTAL` | `UNVERIFIED` (CAD volumes) |

## Checks run

| Command | Result for landing |
|---|---|
| `python -I redesign/team/D5/feet_calc.py` | all limits met; CAD volumes = calc (16 components) |
| `python -I redesign/fusion/check.py` | `landing ok`, 0 errors. WARN: caps wait for `WNG-001` (D1); 7 ground nodes have no CAD (by design). Global FAIL is from harness, pod, transport and the CG, not D5 |
| `python -I redesign/interfaces/merge_check.py` | no landing errors. WARN: the right-side fin group and the caps float until D1 declares the wing. Global FAIL is from `E-POD-*` and `E-TRN-*` dangling |
| `python -I redesign/proofs/build_graph.py` | no D5 errors. C1 and C5 drift on `CL-D5-ETA` and `CL-D5-MASS-TOTAL` (re-runs requested) |

## Change requests filed (`CHANGE-REQUESTS.md`)

CR-D5-21 F4 `Q_LAND_SPEED` 30 cm/s · CR-D5-22 C5 re-run on the R4 cartridge · CR-D5-23 C1 per-type loads ·
CR-D5-24 C6 bond 1 350 mm² / rim 1.18 · CR-D5-25 H1 coupon pass lines · CR-D5-26 A3 mass 42.50 g, ground nodes ·
CR-D5-27 I1 7/32 in tube · CR-D5-11 D3 fin-tip step (still open).
