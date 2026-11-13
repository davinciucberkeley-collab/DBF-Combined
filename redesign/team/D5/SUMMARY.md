# D5 Landing feet: summary (revision D5-R8, 2026-11-13; R5a text below)

> **R8 (2026-11-13, CR-H1-22, side-load margin):** the R7 shoe passed the 59.25 N ultimate side load with RF 1.06
> (`CL-D5-SIDE-RIM-SF`, +y 37.6 MPa at the rim vs `ASM-D5-PETG-SIGMA` 40 MPa); H1's 0.62 (`CL-H1-D5-SIDE-RIM-SF`)
> was a stale ×35/59 scaling of an RF that was already at 59 N. R8 adds margin without moving the fin step:
>
> | Change | R7 → R8 | Why (D5 FEA, `sim/fea_shoe_d5.py`, h 0.4 sweep in `sim/out/*_v_*.json`) |
> |---|---|---|
> | Sleeve inside fillets | R 1.0 → **2.0** | +y 37.6 → 35.5, +z 31.0 → 21.2 MPa at rim 3.4 |
> | Rim y sides (`shoe.rim_side_t_m`, new) | 3.4 → **4.6** mm | +y 35.5 → 28.7 MPa; past ~4.8 the window corner governs |
> | Rim floor side (`shoe.rim_floor_t_m`, new) | 3.4 → **0.4** mm | not a stop face; a thick floor rim raised the +y peak (floor 1.4 / 0.4 / 0: 30.1 / 29.3 / 30.0 MPa at rs 4.4–4.8) |
> | Tine chamfer / rails | 1.0 / 2.0 → **1.4 / 2.5** mm | chamfer clears the R 2.0 arc by 0.16 mm (`CL-D5-FILLET-CLEAR`; 1.0 mm would leave 0.03); rails restore the tine |
> | Tine SF formula | F a on the windowed section | max(F a full section, F (a − 3 mm) windowed): the window starts 3 mm aft of the sleeve end and enters it only as the lever shrinks |
>
> Results: shoe RF **1.27** at the finest mesh (h 0.4 / 0.3 / 0.2 mm, +y: 28.7 / 30.1 / 31.6 MPa; the h 0.2 peak is
> the sharp inboard window corner, still rising; the rim converges at 30.4 MPa, RF 1.32), tine SF **1.23** (R7 1.15 on
> the old formula), bond RF 1.43 and flange SF 1.07 unchanged, fin step x 0.2614 / |z| 0.2010 unchanged, landing
> **59.08 → 58.94 g** (−0.14 g). C5's `CL-C5-FEA-SHOE-SF` (1.076) is a record of the R6 stack; it does not drift.

> **R7 (2026-11-11, D-75 / D-76 / D-78):** cartridges in FOAMULAR 400 at 14.5 × 9.8 mm (same 37.5 N mean plateau);
> shoe 19.1 × 14.4 mm, rim 3.4 mm; landing **69.9 → 59.1 g** vs a 60 g allocation (48 → 60 from power). Fin step at
> x 0.2614 / |z| 0.2010 is the one source; D3 copies it (mismatch 0) and the CAD shoe no longer overlaps the fin.
> Shoe FEA RF 1.06, tine 1.15, flange 1.07, bond 1.44. See `subsystems/landing/SPEC.md` and CR-D5-32/-33.

Subsystem `subsystems/landing/` (prefix GER), params A1-R3. Four telescoping crush feet on the half-fin TE tips plus
two TPU wingtip corner caps. R5 closes CR-A4-39, CR-A5-25 and CR-A1-46: the caps are built on `WNG-001` now that D1
declares it, and the ground kit has CAD. Feet geometry and loads are unchanged from R4. R5a (2026-11-10) re-ran
`make_interfaces.py`, `feet_calc.py` and all checks against today's params: interfaces.json is unchanged (already R5),
claims moved only in the 4th digit (C5 pair stroke 31.45 → 31.43 mm), and D3 has applied the D-54 fin step.

## What changed in R5

| Item | R4 | R5 | Why |
|---|---|---|---|
| Corner caps `GER-007-R/L` | `PROPOSED`, not built | `MODELLED`, built on `WNG-001` | D1 declares `WNG-001` |
| `E-GER-21/22` (cap on `WNG-001`) | `edges_pending` | `edges`, registered as contacts | CAD and interfaces.json agree (cleared 4 ERROR, 4 WARN) |
| Ground kit `GER-005`, `-006`, `-009…013` | `PROPOSED`, no CAD | `MODELLED`, `"flight": false`, one unit per line in a row at y 0.85 m | cleared 7 `missing` WARN; layout only (kit travels in `TRN-108`) |
| Sheet `GER-006` / tube `GER-013` mass | 0 / 0 g | 193.2 / 15.1 g (ground) | a component needs mass > 0; `CL-D5-KIT-SHEET-MASS`, `-TUBE-MASS` |
| Fin step (CR-D5-11) | open | **closed** (R5a): fins params read `tip_square_m` 0.0454, `tip_step_z_m` 0.2005 | D-54, applied by D3 R4 |
| Envelope span | 1.150 + 1.6 mm growth | 1.152 adopted by A1, growth 0 | CR-D5-16 closed |
| Side load at the pad (C5) / rim SF | 20.4 N limit / 1.18 | 22.8 N limit / 1.05; `T-D5-SIDE` 32 → 35 N | upstream C5 change; rim SF is thin, the test decides |
| C1 ult bound / bond RF | 60.8 N / 1.54 | 59.6 N / 1.57 | upstream C1 change |

## Key results

| Quantity | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Plateau upper / lower / mean | 39.6 / 35.4 / 37.49 | N | `CL-D5-F-PLATEAU-*` | `UNVERIFIED` |
| Peak upper limit / ult (C1 ult bound 59.6) | 39.6 / 59.4 | N | `CL-D5-F-PEAK-UPPER`, `-F-ULT-UPPER` | `UNVERIFIED` |
| Level 1.5 m/s landing: stroke / n / η | 23.0 mm / 5.88 / 0.90 | — | `CL-D5-STROKE-USED`, `-N-LAND`, `-ETA` | `UNVERIFIED` |
| Usable stroke vs C5 pair-first | 35 vs 31.4 | mm | `CL-D5-STROKE-USABLE` | `UNVERIFIED` |
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
| `python -I redesign/proofs/build_graph.py` | no `CALC-D5` drift; downstream `CALC-H1-D5` drifts on the D5 numbers (CR-D5-30) and `CALC-C5-STANCE` on the D-59 pack stations (C5 to re-run; D-47 worst narrow tip-over 31.99 → 32.08 deg, still ≥ 30) |

## Change requests filed (`CHANGE-REQUESTS.md`)

CR-D5-28 D1 acknowledge `E-GER-21/22` · CR-D5-29 A3/A4 ground kit modelled, ground masses · CR-D5-30 C6/H1 re-run on bond RF 1.57, rim SF 1.05, `T-D5-SIDE` 35 N · CR-D5-11 closed (D3 applied the D-54 step).
R4 requests CR-D5-21…27 stand.