# D5 Landing feet: summary (revision D5-R5, 2026-11-09)

Subsystem `subsystems/landing/` (prefix GER), params A1-R3. Four telescoping crush feet on the half-fin TE tips plus
two TPU wingtip corner caps. R5 closes CR-A4-39, CR-A5-25 and CR-A1-46: the caps are built on `WNG-001` now that D1
declares it, and the ground kit has CAD. Feet geometry and loads are unchanged from R4.

## What changed in R5

| Item | R4 | R5 | Why |
|---|---|---|---|
| Corner caps `GER-007-R/L` | `PROPOSED`, not built | `MODELLED`, built on `WNG-001` | D1 declares `WNG-001` |
| `E-GER-21/22` (cap on `WNG-001`) | `edges_pending` | `edges`, registered as contacts | CAD and interfaces.json agree (cleared 4 ERROR, 4 WARN) |
| Ground kit `GER-005`, `-006`, `-009…013` | `PROPOSED`, no CAD | `MODELLED`, `"flight": false`, one unit per line in a row at y 0.85 m | cleared 7 `missing` WARN; layout only (kit travels in `TRN-108`) |
| Sheet `GER-006` / tube `GER-013` mass | 0 / 0 g | 193.2 / 15.1 g (ground) | a component needs mass > 0; `CL-D5-KIT-SHEET-MASS`, `-TUBE-MASS` |
| Fin step (CR-D5-11) | open | decided by A1 in D-54; D3 still has to cut it | fins params still read 0.040 m |
| Envelope span | 1.150 + 1.6 mm growth | 1.152 adopted by A1, growth 0 | CR-D5-16 closed |
| Side load at the pad (C5) / rim SF | 20.4 N limit / 1.18 | 22.8 N limit / 1.05; `T-D5-SIDE` 32 → 35 N | upstream C5 change; rim SF is thin, the test decides |
| C1 ult bound / bond RF | 60.8 N / 1.54 | 59.6 N / 1.57 | upstream C1 change |

## Key results

| Quantity | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Plateau upper / lower / mean | 39.6 / 35.4 / 37.49 | N | `CL-D5-F-PLATEAU-*` | `UNVERIFIED` |
| Peak upper limit / ult (C1 ult bound 59.6) | 39.6 / 59.4 | N | `CL-D5-F-PEAK-UPPER`, `-F-ULT-UPPER` | `UNVERIFIED` |
| Level 1.5 m/s landing: stroke / n / η | 23.0 mm / 5.88 / 0.90 | — | `CL-D5-STROKE-USED`, `-N-LAND`, `-ETA` | `UNVERIFIED` |
| Usable stroke vs C5 pair-first | 35 vs 31.5 | mm | `CL-D5-STROKE-USABLE` | `UNVERIFIED` |
| Tip-over at target / worst flying CG (≥ 30) | 34.6 / 30.6 | deg | `CL-D5-TIPOVER-NARROW`, `-CORNER` | `UNVERIFIED` |
| Bond RF / flange SF / rim SF / tine SF (side 34.2 N ult) | 1.57 / 2.74 / 1.05 / 3.14 | — | `CL-D5-BOND-SF` etc. | `UNVERIFIED` |
| Mass (4 feet + 2 caps) vs allocation | 42.50 vs 43 | g | `CL-D5-MASS-TOTAL` | `UNVERIFIED` (CAD volumes) |
| Envelope span growth from caps | 0 | m | `CL-D5-ENVELOPE-SPAN-GROWTH` | `MODELLED` |

## Checks run

| Command | Result for landing |
|---|---|
| `python -I redesign/team/D5/feet_calc.py` | all limits met; CAD volumes = calc for feet and kit |
| `python -I redesign/team/D5/make_interfaces.py` | 25 parts (18 flight, 7 ground), 22 edges, no `edges_pending` |
| `python -I redesign/fusion/check.py` | `landing ok`, 25 components, 0 errors, 0 module WARN. Graph WARN: `E-GER-21/22` one-sided until D1 acknowledges (CR-D5-28). Global FAIL is from other modules (prop keep-outs, CG), not D5 |
| `python -I redesign/interfaces/merge_check.py` | no landing errors; same one-sided WARN; global FAIL is not D5 |
| `python -I redesign/proofs/build_graph.py` | no `CALC-D5` drift; downstream C6 and H1 drift on the new D5 numbers (CR-D5-30) |

## Change requests filed (`CHANGE-REQUESTS.md`)

CR-D5-28 D1 acknowledge `E-GER-21/22` · CR-D5-29 A3/A4 ground kit modelled, ground masses · CR-D5-30 C6/H1 re-run on bond RF 1.57, rim SF 1.05, `T-D5-SIDE` 35 N · CR-D5-11 D3 apply the D-54
step (still open on the fins side). R4 requests CR-D5-21…27 stand.