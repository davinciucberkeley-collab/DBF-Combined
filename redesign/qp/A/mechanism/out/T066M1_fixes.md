# T-066 M-1 and T-023 F-10 fixes. 2026-11-22. Not VERIFIED COMPLETE. Nothing committed.

No edit to docs/, the CHANGE-LOG, the ledger or spec files. Categories: stored-result proof chain (structures: FEA-lite beam FE, hand calculation, read not re-run); drawings regeneration (no analysis).

## 1. M-1: vibration inputs re-pointed (redesign/qp/A/proofs/gen_params_a.py, claims_a0_base.py, claims_a2_struct.py, explain_a.py)
New sources registered: SRC-A-STRUCT-RUN = structures/structures_run.md (T-084 rerun, X2216, 1.8796 kg), SRC-A-T085 = mechanism/out/T085_report.md (D-236).
| Param | Was (iter3_run.md, MN2212) | Now | Source |
|---|---|---|---|
| sim.gust_n_vd | 3.01 (stall line 3.96) | 2.71 (stall line 3.16) | structures_run.md s2, gust U 4 m/s at VD 24 |
| sim.vib_below_hz | 63 / 67 / 77 | 66 / 69 / 81 | structures_run.md s4, highest strong mode below the band, kd / nom / hi (spar-only beam FE) |
| sim.vib_above_hz | 432 / 462 / 524 | 438 / 474 / 532 | structures_run.md s4, lowest strong above the band |
| sim.hover_1p_rpm_lo | 6,018 | 6,789 | structures_run.md s4 hover derate 1.0 (1P 113 Hz); limit 94.29 Hz (document: 94) |
| sim.cruise_2p_hz_hi | 253 | 267.6 | structures_run.md s4, 2P of the highest of the five operating rpm (hover lean 8,028 rpm; cruise 2P is 248 Hz; name kept); limit 321.1 Hz (document: 321) |
| sim.vib_fc_ms2 | 25.8 27.1 23.9 23.9 23.7 23.7 (6,000-10,500 rpm) | 26.5 26.6 23.7 23.7 22.7 22.7 (6,000-11,415 rpm) | structures_run.md s4 sweep table; worst 26.6 m/s2, MS +0.13 |
| sim.vib_inband_corners (new, est) | - | 3 | structures_run.md s4 (201 / 215 / 244 Hz, cy 0.52, in band) and T085_report.md s3.1 / D-236 (strong mode 94.6-108.7 Hz, cx 0.74-0.85, cy 1.12-1.35; 23 of 24 bound groups fail; the one pass is by 0.1 Hz) |
| sim.gm_nominal / gm_shifted / gm_shifted_up | iter3_run.md | values unchanged, marked est (UNVERIFIED), note "STALE, MN2212 / iteration-2 cage" | not re-run: sitl/fu_cage.py builds the iteration-2 cage (`CFG` from iter2_eval.py) with the MN2212 aero (`a_aero.motor`); a rerun with X2216 inertias needs that config and plant rebuilt, not a quick run. "—" source pending |
New claim CL-A-VIB-IN-BAND (corners with a strong mode inside the band, limit <= 0, D-185 (a), A-P10): value 3, **FAILS** (carried FAIL, same form as the other STRICT FAILs; no limit relaxed, band and 0.5 rule unchanged). Added to test T-A-TAP (TP-10b decides). CL-A-VIB-LOW / HIGH how-texts say they do not show D-185 (a) met. explain_a.py cards updated.
Not re-sourced / pending ("—"): fu_cage gain margins (3 params above); `cruise_2p_hz_hi` name still says cruise.

## 2. Claim lists (python -I proofs/run_all.py from redesign/qp/A; before stored in the scratchpad run, summary here)
| | Before | After |
|---|---|---|
| STRICT failing claims | CL-A-MASS-PRED, CL-A-MASS-GATE-ROOM, CL-A-CUTS-REQUIRED, CL-A-HORN-RIB-FOAM-HOLD, CL-A-HORN-RIB-FOAM-STALL, CL-A-ELEVON-TORSION-FOAM, CL-A-HORN-BEARING-STALL, CL-A-LINKAGE-FREEPLAY (8) | the same 8 + **CL-A-VIB-IN-BAND** (9) |
| UNVERIFIED STRICT | CL-A-FLUTTER-ELEVON-NOM | same; CL-A-VIB-GM and CL-A-VIB-GM-SHIFT now UNVERIFIED (stale inputs) |
| Summary line | UNVERIFIED 213, CHECKED 327, fails 11 (node-level count) | UNVERIFIED 222, CHECKED 323, fails 13 (node-level count) |
| Values | VIB-LOW 77 Hz (limit 83.58), VIB-HIGH 432 (303.6), VIB-FC 27.1, GUST-N 3.01 | VIB-LOW 81 (94.29), VIB-HIGH 438 (321.1), VIB-FC 26.6, GUST-N 2.71 |
run_all exit: FAILED (expected, as before).

## 3. F-10: drawings regenerated (drawings/make_drawings_a.py, python -B, 3 min 52 s, run as run_gates_t084.sh does)
Output: "49 of 49 drawings composed -> out/DRAWINGS-A.pdf". DRAWINGS-A.md now reads "commit 604443a7" (was de638ea8). git diff --stat: the 49 sheet PDFs and DRAWINGS-A.pdf changed by 4 lines each (embedded date metadata), DRAWINGS-A.md by the stamp line; no PNG, STL or other file changed.
