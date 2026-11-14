# H1 ground test: summary

Status `PROPOSED`, revision H1-R3, 2026-11-10.

Plan and 18 cards: `team/H1/GROUND-TEST-PLAN.md`. Rig sizing and pass lines: `team/H1/ground_tests.py` →
`claims.json` (96 claims, every limit met). Requests: `CHANGE-REQUESTS.md`. Jacobs loan request, drafted but **not
sent**: `JACOBS-LOAN-REQUEST.md`. Nothing is `VERIFIED` because no hardware has been tested. R3 read C4's 15:01
re-publish, so the mount-stiffness and fin-proof lines follow it.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Fin proof: pad deflection at 1.0 × L4 splitting 3-D (3.70) and shell (18.86) | ≤ 8.36 (geometric mean) | mm | `CL-H1-FP-DEFL-SPLIT` | `MODELLED` |
| Fin proof gauges: face at 1.5 × / strip at 1.0 × / 2σ resolution | 1 612 / 800 / 0.9 | µε | `CL-H1-FP-EPS-FACE-ULT`, `-EPS-STRIP-LIM`, `CL-H1-SG-RES-FRAC` | `UNVERIFIED` |
| Gauge self-heating at 0.45 V vs 4.3 V bare (limit 78) | 19 / 1 761 | W/m² | `CL-H1-SG-PDENS`, `-PDENS-BARE` | `UNVERIFIED` |
| Dial travel to 1.0 × / available | 23.6 / 25 | mm | `CL-H1-FP-TRAVEL-REQ` | `UNVERIFIED` (+6 %) |
| Mount stiffness pass = max(1 100, C4 need) / C4 estimate | 1 966 / 1 500 | N·m/rad | `CL-H1-MSTIFF-K-PASS`, `-NOM-RATIO` 0.76 | `PROPOSED`, expected `FAIL` (CR-H1-24) |
| GT-17 spot at 1.5 kg, wall 5.0 m / U95 | ≤ 4.02 / 6.9 % | mm / – | `CL-H1-MSTIFF-SPOT-ACCEPT`, `-U` | `UNVERIFIED` |
| Lever 15:1 vs need (1.25 × 2 131 N) / 9:1 vs CR-C6-33 | 2 942 vs 2 664 / 1 765 vs 1 554 | N | `CL-H1-LEVER-CAP`, `-NEED`, `-CAP9`, `-NEED9` | `MODELLED` |
| Pivot bearing: bare wood / steel plates / M6 in wood | 10.3 (> 4.3) / 65 / 3.4 | MPa | `CL-H1-LEVER-WOOD-BRG`, `-PLATE-BRG`, `-M6-BRG` | `MODELLED` |
| Tube GJ at G 3 GPa / U95 / ring δ at 20 N (E_hoop 8 GPa) | 21.9 N·m² / 1.9 % / 0.26 mm | – | `CL-H1-TORS-GJ-LO`, `-U`, `CL-H1-RING-DEFL` | `UNVERIFIED` |
| ESC film f acceptance (1.131 + U95 3.2 % on h) / hold | ≥ 1.205 / ≥ 617 s | – / s | `CL-H1-ESCCFD-F-ACCEPT`, `-RUN` | `UNVERIFIED` |
| Wing proof step 1 per side: pads 1–4 / relief per tube | 0.919 / 0.524 / 0.453 / 0.613 / 2.031 | kg | `CL-H1-WP-M1..M4`, `-RELIEF-M` | `UNVERIFIED` |
| Wing proof step 2 (V-block y 0.32): pads 3 / 4 | 0.499 / 1.642 | kg | `CL-H1-WP-S2-M3`, `-M4` | `UNVERIFIED` |
| CG balance marks / jig acceptance window | 0.0466, 0.0514 / 0.0472–0.0508 | m | `P:cg.x_range_m`, `CL-H1-CG-ACCEPT-FWD`, `-AFT` | `UNVERIFIED` |
| `T-D5-SIDE` load / D5 rim SF scaled to it | 58.96 / 0.62 | N / – | `CL-H1-D5-SIDE-F`, `-RIM-SF` | `UNVERIFIED` (CR-H1-22) |
| `T-C3-POD-PROOF` bracket pull, +x and −z | 199.6 | N | `CL-H1-POD-BRACKET-F` | `UNVERIFIED` (CR-H1-23) |
| Station proof: mount / station / pack pull | 21.1 / 57.3 / 73.8 | N | `CL-H1-MOUNT-PROOF-F`, `-FIN-PROOF-F`, `-PACK-PULL-F` | `UNVERIFIED` |
| Stand: peak pass / limited fresh / cold pack | ≤ 20.98 N / ≥ 1.391 / ≥ 1.115 kgf | – | `CL-H1-T-PEAK-ACCEPT`, `-FRESH-ACCEPT`, `-SAG-ACCEPT` | `UNVERIFIED` |
| Ground-test purchases `G12` + `G13` | 26.00 (D-39 line 20) | $ | `CL-I1-GROUNDTEST-BOUGHT` | `PROPOSED` (A1, CR-H1-25) |

## Action items this revision

| Item | Result |
|---|---|
| `T-C4-FIN-PROOF` as drawn, gauges, dial (CR-C4-36/-38) | GT-09: two half bridges with dummies, shunt 1 744 µε, dial to 1.0 ×, then a rule; 1.0 × comparison step |
| `T-C4-MOUNT-STIFF` ≥ 1 100 (CR-C4-41) | floor kept; card follows C4's live 1 966; wall 5.0 m, photo read-out |
| `T-C6-STRIP-ANCHOR` frame ≥ 1 560 N (CR-C6-33; -39 asks 2 660) | 15:1 / 9:1 lever with steel pivot plates; both met |
| `T-C3-STOP-PUSH` bonded, `T-C3-POD-PROOF` + 200 N (CR-C3-20) | GT-15 and GT-09 (b) |
| `T-C4-TUBE-BEND` with GJ (CR-C2-15) | GT-16 steps 4 (two lasers) and 5 (ring crush, E_hoop) |
| `T-E3-ESC-PAD-CFD` (CR-E3-17) | GT-04 step 2b; 5 min hold too short (CR-H1-21) |
| GT-08 pad table and step 2 (CR-C1-30) | from C1's claims; text mismatch to C1 (CR-H1-20) |
| GT-07 marks 0.0466 / 0.0514 m | drawn at the limits; jig window guard-banded inside |
| `T-D5-SIDE` at 59 N ultimate | GT-09 at 58.96 N on the CR-A1-65 shoe |
| Jacobs written yes before 20 Nov (D-72) | request drafted, **not sent**: a team member sends it by 13 Nov (CR-H1-26) |

## Open issues

| Issue | Who |
|---|---|
| Jacobs' written yes ($157.34 of I1's levers) not in hand; due 20 Nov | team (CR-H1-26) |
| C4's mount estimate (1 500) is below its own need (1 966); GT-17 expected to fail | C4 (CR-H1-24) |
| D5's drawn rim expected to crack at 59 N | D5 (CR-H1-22) |
| 200 N crash pull on a flight pod | C3 (CR-H1-23) |
| C4 test texts still R4; gauge predictions not claims (`ASM-H1-FP-PRED`) | C4 (CR-H1-24, -10) |
| Face gauge on paper over foam needs a coupon factor (stack 0.63 × face) | H1, C4 (GT-15) |

## How to verify

`python -I redesign/team/H1/ground_tests.py` (96 claims, no `FAILS`), then `python -I redesign/proofs/build_graph.py`.
