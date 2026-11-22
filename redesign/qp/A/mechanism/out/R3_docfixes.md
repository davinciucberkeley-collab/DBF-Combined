# R3 doc fixes (review round 3: M-D, m-G, m-C, m-A, m-E), 2026-11-22

Source: `docs/audits/2026-11-22-review-round-3.md`. Category: documentation / accounting edit, no new analysis. Numbers read from `T084_report.md` s0, s1.3, s3, `T085_report.md` s7, `T086_report.md`, `T087_report.md`, and `python -I bom_a.py` (total $1,939.17, margin $60.83). Not edited: docs/, CHANGE-LOG, ledger. Nothing committed. All paths under `redesign/qp/A/`.

## Edits
| Finding | File | Edit |
|---|---|---|
| M-D | `MASS-GATE.md` s15 roll-up table | "T-083b tallied" row demoted from current basis; added T-084 as drawn row (1,633.0 g, 1.8717 kg, CG 21.95, SM 7.65) and **T-084 tallied** row (1,640.0 g = 1,633.0 + 7.0 cups, 1.8796 kg, CG 23.13 mm, SM 7.17 %, trim 22.14 / 24.78, window +11.88 %, T/W 2.632 / 2.111, cruise 234 s, 1.3 Vs 17.56) |
| M-D | `MASS-GATE.md` s15 text | "1.873 kg" superseded note extended to 1.8796 kg; new T-084 paragraph (FIN_H 0.180 -> 0.1937 m, deltas, A-P9 31.00 deg, limits, 1.50 kg gate FAIL carried, T-087 no mass change, D-185 status); old BOM $1,981.31 / +$18.69 marked superseded by $1,939.17 / +$60.83 (D-234, D-235) |
| M-D | `MISSION.md` | New T-084..T-087 status note above the T-083c note: mass, CG, SM, window, T/W, cruise, A-P6, A-P9 31.00 deg, BOM, D-185 (a) carried FAIL decided by TP-10b; energy lines of s4 marked "—" (not re-derived); T-083c note marked as earlier state |
| M-D | `REQUIREMENTS-A.md` | Bracketed current-state notes on A-U1 (BOM), A-P1 (mass, CG, SM, T/W), A-P6 (17.56 m/s), A-P9 (31.00 deg, 30.22-30.52 sensitivity, TP-3 re-check) |
| M-D | `SCHEDULE-A.md` | Appended "Update 2026-11-22" section: current state, TP-10b placement (after build, before F01, 0.5 d EST, not gating 12-15), option C contingency "—", R15 supply "—", `schedule_a.py` not re-run so slack "—" |
| m-G | `REQUIREMENTS-A.md` A-P10(a) | MN2212 rotor bands replaced by band 94-321 Hz (113 Hz hover 1P at 6,789 rpm / 1.2; 267.6 Hz hover-lean 2P at 8,028 rpm x 1.2), cited to `proofs/gen_params_a.py` / `structures/structures_run.md` s4; old bands kept as marked record; (a) recorded as carried FAIL on the model (CL-A-VIB-IN-BAND, D-236) decided by TP-10b |
| m-C | `TEST-PLAN-O4B.md` s0 item 1 | A-P10 tap test removed from the list that decides 2026-12-15; sentence now says it runs after the build, before the first tethered hover, and does not gate 12-15 (D-236) |
| m-C | `TEST-PLAN-O4B.md` s5 item 6 | alternatives (partial PETG cage / move criterion 3) replaced by "Closed (D-236, TP-10b)" |
| m-A | `TEST-PLAN-O4B.md` TP-10b step 3 and step 8 | pulse bandwidth check now on the reference mass AND the motor cup (3 dB roll-off criterion labelled team EST; must reach 321 Hz; otherwise "not measured" = undecided, not pass); step 8 records both spectra |
| m-A | `mechanism/out/T085_report.md` s7 route A | "below 94 Hz / (1 + u) decoupled" replaced by the TP-10b step 6 coupling rule (pass max(cx,cy) x (1+u) < 0.5 in 94-321 Hz; fail max/(1+u) >= 0.5; between = fail until FE updated) |
| m-E | `proofs/gen_params_a.py` l.193, `proofs/claims_a2_struct.py` l.143 | `cruise_2p_hz_hi` renamed `hover_lean_2p_hz` (the only two source references; note text updated). Generated files refreshed by the run: `params-A.json`, `proofs/claims.a2_struct.json`, `proofs/out/CHAIN.md`, `graph.js`, `graph.json`. Older records in `mechanism/out/` (T065, T066M1, T083/T084/T087 backups) keep the old name as history |

## Verification (m-E)
`cd redesign/qp/A; python -I proofs/run_all.py` (rc 1, expected). Summary `UNVERIFIED 222, PROPOSED 17, CHECKED 323, VERIFIED 0; fails 13` (same as review V7). STRICT fails: MASS-PRED, MASS-GATE-ROOM, CUTS-REQUIRED, HORN-RIB-FOAM-HOLD, HORN-RIB-FOAM-STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY (8) + VIB-IN-BAND (value 3, limit 0) = 9; CL-A-FLUTTER-ELEVON-NOM UNVERIFIED. `git diff` of `params-A.json`, `claims.a2_struct.json`, `CHAIN.md`: only the key name, the input reference and the note text changed; `hover_lean_2p_hz` = 267.6 Hz CHECKED, unchanged. Output saved at scratchpad `r3_runall.txt`.
`python -I bom_a.py`: Total 1,939.17, Margin 60.83.

## Not done / open
Cell edits to the CRLF files kept CRLF. No unit gate or 3-D gate run (no CAD change). M-A (D-236 forced response), M-B, G-9, m-B, m-D claim note, m-F, m-H are not in this task.
