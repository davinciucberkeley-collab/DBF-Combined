# T-065 evidence: structures_run.md vs a fresh structures_a.py run (concept A)

Date 2026-11-19. Category of every analysis here: analytic beam-FE / hand calculation (3-D Euler beam frame, `fe_a.py`, modal forced response). Not FEA (solid), not CFD, not SITL. Seconds to run (about 28 s). No FEA/SITL/CFD launched.

## 0. Acceptance test (restated from the brief)
(1) Run `python -I redesign/qp/A/structures/structures_a.py` fresh. (2) Diff committed vs fresh by section; for each changed value find the input change and say whether the new value is right. (3) For each FAIL row: physical meaning, real or artefact, ladder resolution; limits not changed. (4) Replace the committed file with fresh output only if the script inputs are right.
Task ledger wording: "committed file equals a fresh run; every FAIL explained with a decision or open test".

## 1. Commands and exit codes
| Command | Exit | Note |
|---|---|---|
| `python -I redesign/qp/A/structures/structures_a.py` (cwd structures/) | 0 | 226 lines; byte-identical to `T064_data/structures_run_full_regen.md` (`cmp` equal) |
| same, cwd = scratch dir, after the script fix of s7 below | 0 | stdout equals the written file (`diff` clean except the missing final newline); saved `T065_data/structures_run_final_stdout.md` |
| 22ef3204 versions of structures_a.py / fe_a.py / landing_a.py run in scratch | 0 | does NOT reproduce the 22ef3204 committed md (155 changed lines in s4): see 3.4 |
| scratch copy of structures_a.py with the CURRENT tube set passed to `fe_a.build`, bridge 16x14 and 12x10 | 0 / 0 | `T065_data/structures_run_scratch_currentCFG_bridge16x14.md`, `..._bridge12x10.md`, script `structures_a_scratch_currentCFG.py` |

Process incident (record it): `structures_a.py` wrote `structures_run.md` into the CURRENT DIRECTORY, so my first run (cwd = structures/) overwrote the committed file, and the commit `5561c0bb` ("AM-004 recorded verbatim", made by another session while this task ran) swept that overwritten file into HEAD. HEAD therefore already holds the fresh iteration-1-geometry output. I did not commit. The old committed text is saved as `T065_data/structures_run_committed_2d4a2854.md` (also in git at `2d4a2854` and `22ef3204`). Fixed in the script: it now writes next to itself.

Files in `redesign/qp/A/mechanism/out/T065_data/`: `committed_vs_fresh.diff` (237 lines), `structures_run_fresh_iter1geom.md`, `structures_run_committed_2d4a2854.md`, `structures_run_final_stdout.md`, the two scratch current-CFG runs and the scratch script.

## 2. Finding that governs everything: the script's geometry is the QP-3 iteration-1 baseline, not the current design
`structures_a.py` hard-codes spar 16x14 (`A16`, `I16`, s1, s2, s3), arms and ribs 14x12 (`A14`), bridge 8x6 single (`A8`), and calls `fe_a.build(kind)` with fe_a defaults (the same tubes, no struts). The design moved on (D-185 iterations 2 and 3, D-202, D-206): spar 12x10 (`cad/amodel/common.py` line 38), arms 12x10 continuous (`wing.py` ARM_OD/ID), bridge 16x14 (`wing.py` BR_OD/ID, D-206) plus two 6x4.5 struts (`wing.py` STRUT_OD/ID); `iter3_run.py` CFG is spar 12x10, arms 12x10, rib 14x12, bridge "single+V", struts 6x4.5 at y 0.30, fin tube 16x14. Consequence: s1 (mass table), the spar lines of s2, s3, all of s4 and the mount-strength table in structures_run.md describe the baseline geometry. Their current-geometry records are `iter2_margins.md` (spar 12x10 MS +2.73, params `struct.ms_spar`), `iter3_run.md` (modes, forced-response sweep, control-band GM), `bridge_torsion_d206.md`, `foam_103.md`, MASS-GATE and `cad_mass.json` (CAD basic mass 1.27324 kg).
Not modelled by any of these FE runs: the D-202 continuous crossing arms (hub treated as a node), the printed hub compliance (the hub FEA `fea_hub.py` is the solid model).

Decision (item 4): the script inputs are NOT right for s1, s3, s4 (geometry), so the file is not presented as the current-design structures record. HEAD's content (fresh run) is kept, now headed by an explicit scope banner (a script edit, regenerated, so committed == fresh). Rewriting structures_a.py to the current geometry is proposed as T-065b below (not done: it is a re-baselining of the mass table, spar bending, mount strength and modes, and changes numbers that other records cite).

## 3. Section-by-section diff (committed 2d4a2854 vs fresh), cause, and is the new value right
Diff hunks: s2 header + one table row; s4 (rpm lines, three tables, forced response); s6 last line. s1, s2 (all other rows), s3, the mount-strength table and s5 are unchanged.

### 3.1 s2 C1 loads
| Value | Committed | Fresh | Cause | Right? |
|---|---|---|---|---|
| VD | 22 m/s ("1.25 VC rounded up") | 24 m/s | commit `11d8da6a` (QP-4, 2026-11-15) changed `VD = 22.0` to `24.0`; basis D-186: VH 18.8 m/s x 1.25 = 23.5, rounded up; params `req.vd_ms` = 24, A-P13 | Yes. 24 is the project VD |
| Gust U 4 m/s at VD, n | 2.85 (stall line 3.32) | 3.01 (stall line 3.96) | follows from VD (n = 1 + Kg rho U V a / 2 w/s, stall line = 0.5 rho V^2 S CLmax / W) | Yes. Equals params `sim.gust_n_vd` 3.01 / 3.96 and `iter3_run.md` C1 |
| Gust U 8 m/s at VC | 3.85 -> 1.98 | same | VC 17 unchanged | n/a |
The header text now also cites the flutter/divergence-at-VD-24 open item (G8), which is already in the old CHANGE-LOG.

### 3.2 s4 C4 modes
| Value | Committed | Fresh | Cause | Right? |
|---|---|---|---|---|
| Cruise rpm | 9,700 (EST band 8,900-10,500) | 7,450 (SITL band 7,300-7,540, QP-3 BOARD s1 item 2: `sitl/fu_level.py` with APC V > 0 data) | `11d8da6a` replaced the `RPM`, `pts`, `forced()` call and table headers | Yes for the rpm: 1P 124 / 2P 248 Hz; params `sim.cruise_2p_hz_hi` 253 (7,600 rpm). Cruise rpm remains a model value (M8 audio FFT replaces it) |
| Motor mass in the FE | 81.06 g (65 + 11.06 + 5) | 88.26 g (adds 4.3 + 2.9) | `e29526c3` (2026-11-15) changed fe_a.py `motor_g`; matches `landing_a.py` ITEMS motor assembly 4 x 88.26 g | Yes in itself (heavier motor assembly); effect on first mode about -2 % (3.2 / 11.9 / 15.5 Hz old vs 3.2 / 11.6 / 15.3 Hz new, nom, scratch check) |
| Mode list (bridge 5 -> 3 Hz, 17 -> 15 Hz spar, 43 -> 38 Hz etc.) | iter-1 frame | different list | the committed table could not have come from the committed code: the 22ef3204 versions of the three scripts produce the 3.2 Hz bridge mode, while `fe_a_iter1.py` gives 4.7 Hz, which matches the committed "5". The committed s4 was generated by an iteration-1 fe_a that was edited before the QP-3 commit. The committed s4 was therefore not reproducible from its own commit | The fresh list is the right output of the committed code, but of the iteration-1 geometry (section 2) |
| Separation percentages | e.g. kd 589 Hz 82 % | 137 % | cruise 2P moved from 323 to 248 Hz; rows that were above cruise 2P are now farther, rows near 250-275 Hz are now near cruise 2P | Arithmetic follows from the rpm |
| Forced response (IMU accel, MS) | hover hi 63.9 m/s2, MS -0.5; cruise kd 24.4, MS +0.2 | hover hi 18.3, MS +0.6; cruise hi 18.7, MS +0.6; worst fin-tip 31.2 | rpm 9,700 -> 7,450 moves the 1P order off the 86-104 Hz wing-box / spar resonance region (the old hi hover -0.5 came from the 104 Hz spar mode on the hover 1P order at 6,272 rpm and U omega^2 at 9,700); plus the mode-shape change above | Right for the baseline geometry. Cruise value now consistent with `iter3_run.md` (9.5 to 10.2 m/s2 at 7,300-7,600 rpm, current-ish geometry) |

### 3.3 s6 last line (pack tray to hub bond)
600 mm2 -> 218 mm2 (27.2 x 8 flange), 0.115 -> 0.32 MPa, RF 17 -> 6.3. Cause: commit `85118feb` (D-208): outer flange tabs were never attached to the hub, so the bond area is the flange only. Right (CAD fact; allowable 2.0 MPa unchanged).

### 3.4 What did not change and the reproducibility point
s1 mass (492 g baseline), s2 spar bending, s3, s5 (T-064 refresh) and the mount-strength table are identical. The s5 refresh in `2d4a2854` was already in the committed file; only the s6 pack-tray line was stale there.

## 4. The FAIL rows (task wording corrected)
Correction to the task brief: the fresh forced-response table has no FAIL row (MS +0.6 to +1.3 on the IMU, all PASS). The 9 FAIL rows are in the "Fin out-of-plane modes and weakly coupled spar / rib modes" separation table. The old committed file (2d4a2854) had 13 FAIL rows: 3 in the strongly coupled table (nom 92 Hz, hi 96 and 104 Hz) and 10 in the weak-mode table (kd 97, 207, 346; nom 104, 221, 292, 311; hi 311, 330, 351). The fresh run has 9, all in the weak-mode table, so it has fewer FAILs, not more (the 3 strong-mode FAILs disappear with the new cruise rpm and mode list). Fresh and old both show FAIL in the weak-mode table, so that is not new.

Fresh FAIL rows (all weak-coupling spar/rib modes, cx, cy < 0.5): kd 97 (spar 53 %, rib 40 %, 3 %), kd 206 (1 %), kd 257 (rib 90 %, 4 %), kd 273 (10 %); nom 104 (0 %), nom 220 (5 %); hi 102 (2 %), hi 118 (5 %), hi 250 (1 %).
- Physical meaning: a spar/rib wing-box bending mode whose frequency lies within 20 % of a rotor order (1P hover 100-105 Hz, 2P hover 201-209 Hz, 2P lean 238, 2P cruise 248 Hz) so a rotor harmonic can excite it. The screen is a frequency rule only.
- Real or artefact: artefact of the rule, not a demonstrated vibration problem, for three reasons. (a) D-185 as ruled applies the 20 % separation only to strongly coupled modes (coupling >= 0.5 over the four motors); weak modes are judged by forced response. (b) The same script's forced response, which sums every mode, gives IMU 6.6-9.5 m/s2 (current geometry) or 13-19 m/s2 (baseline) against 30 m/s2. (c) `iter3_run.md` (current-ish geometry): weak modes in band 169-242 Hz have coupling 0.00-0.45, on-resonance single-mode FC acceleration 0.0-1.3 m/s2 at zeta 0.5 % (fraction 0.00-0.04 of 30), and the full rpm sweep worst is 18.6-19.0 m/s2 at the all-four-at-cap point, 9.5-10.2 at cruise. The old mode frequencies in these 9 rows belong to the 16x14 spar, so which rows fail changes with geometry anyway.
- Current geometry check (scratch, this method, bridge 16x14 / 12x10): strongly coupled table 0 FAIL (1 MARGINAL with 16x14); weak table 14 FAIL rows at 181-267 Hz (rib/fin/spar), forced response IMU MS +2.1 to +3.5 (hover 6.6-8.4, cruise 8.5-9.6 m/s2). So the screening FAIL persists in a different form while the amplitude check passes by a wide margin. Fin-tip acceleration 1P at cruise is 30.2 / 27.5 / 31.6 m/s2 (kd / nom / hi, bridge 16x14); the 30 m/s2 limit is the FC (IMU) VIBE guidance and no sensor sits on the fin, so it is information, not a limit; it feeds fin-skin fatigue (not computed: "-").
- Ladder (spec 6.1): rung 1 not applicable (no feature to subtract); rung 2 (geometry) would move spar/rib frequencies but the forced response already passes, so no design change; the failing item is the check's label. Resolution is a record/criterion alignment, rung 4 on the check approach (judge weak modes by forced response, as D-185 ruled), no limit changed. Open tests that close it physically: tap-test of the built wing (expect the spar/rib mode in 90-120 Hz, T-A-TAP), balance props to <= 0.3 g mm (U 1.0 g mm is the model input), first tethered hover logs IMU VIBE < 30 m/s2, M8 audio FFT on first cruise for the cruise rpm. No design change, so no trade rows.
- Residual real risk worth keeping visible: baseline forced response is U omega^2-sensitive; U = 1.0 g mm per rotor is EST (ISO G16 prop is 0.27 g mm); damping 1 % EST; free-free, hard-mounted FC (no isolation credit).

## 5. Script edits made (analytic script, no CAD change; docs/*.md untouched)
`redesign/qp/A/structures/structures_a.py`: (i) scope banner printed at the top (baseline geometry, pointers to the current records); (ii) a one-line note under the weak-mode table stating the D-185 rule; (iii) output file written next to the script instead of the cwd (the clobber incident above). Regenerated `structures_run.md` (+2 lines). No numbers changed by these edits.

## 6. Proposed records (not written to docs/)
### Proposed AR-013 (ten fields + result and limits)
### AR-013 structures_a.py regeneration and reconciliation (T-065, R-PHY-09; 2026-11-19)
- **Category:** rigid-body modal analysis, analytic beam FE (3-D Euler-Bernoulli frame, free-free) plus hand calculations; illustrative for the forced-response amplitudes (EST inputs).
- **Solver / engine:** `redesign/qp/A/structures/structures_a.py` (imports `fe_a.py`, `landing_a.py`), Python 3.14, numpy/scipy, `python -I`, about 28 s.
- **Model version:** git `5561c0bb` tree plus the T-065 script edits; fe_a.py as of `e29526c3` (motor 88.26 g).
- **Inputs:** hard-coded in the script: VD 24 (D-186), cruise rpm 7,450 (QP-3 BOARD s1 item 2), hover 6,272 / 6,018 / 7,151 rpm, U 1.0 g mm, 2P ripple 5 %, zeta 1 %, E_CF 61 / 70 / 90 GPa, PETG 1.6 / 2.1 / 2.4 GPa; tubes: spar 16x14, arms/ribs 14x12, bridge 8x6 (QP-3 baseline).
- **Assumptions:** iteration-1 geometry (NOT the current CAD); hub a node; FC hard-mounted; weak modes judged by forced response.
- **Boundary conditions / loads:** free-free frame; unbalance and 2P axial ripple at the four motors; static mount loads as listed in the run.
- **Numerical settings:** 90 modes per corner (kd, nom, hi); worst-phase modal sum.
- **Outputs:** `structures_run.md` (regenerated, equals stdout), `redesign/qp/A/mechanism/out/T065_data/`.
- **Acceptance criteria:** every changed value traced to an input commit; every FAIL row explained; no limit changed.
- **Result:** changed values traced to `11d8da6a` (VD 22 -> 24, cruise 9,700 -> 7,450), `e29526c3` (motor mass +7.2 g), `85118feb` (pack-tray bond 218 mm2); the committed s4 was not reproducible from the committed code (iteration-1 fe_a before the QP-3 commit). 9 FAIL rows, all weak-coupling spar/rib modes judged by a separation screen that D-185 applies only to strongly coupled modes; forced response passes (baseline MS +0.6 to +1.3; current-geometry scratch run +2.1 to +3.5). Not a design failure; no limit changed.
- **Limits / validity:** s1, s2 spar, s3, s4 and mount strength are baseline-geometry numbers; current-geometry modes are `iter3_run.md` (spar 12x10, bridge 12x10 single+V) and the scratch run here (bridge 16x14, D-206); neither models the D-202 continuous crossing arms or the hub compliance. Cruise rpm and unbalance are EST.

### Proposed CHANGE-LOG entry (suggested id: D-214, "pending review")
"T-065: structures_run.md regenerated (VD 24, cruise 7,450 rpm, motor 88.26 g, pack-tray bond 218 mm2) and headed with a scope banner: it is the QP-3 iteration-1 baseline geometry; current-geometry modes/forced response are `iter3_run.md` and the T-065 scratch run. The separation FAIL rows are weak-coupling spar/rib modes screened by a rule D-185 applies only to coupling >= 0.5; forced response passes. No limit changed, no CAD change. Ladder: rung 4 on the check (criterion aligned to D-185), no design rung needed. Open: T-065b."

### Proposed T-065b (new ledger row, S, not started)
Re-baseline `structures_a.py` to the current geometry: take the tube set from `cad/amodel/common.py`/`wing.py` (spar 12x10, arms 12x10, rib 14x12, bridge 16x14 + struts 6x4.5) and the fin from CAD; replace the hard-coded mass table by `cad_mass.json`; make the weak-mode rows carry coupling and a forced-response verdict rather than a separation-only label; add the iter3 rpm sweep. Then rerun, diff against `iter3_run.md`, and re-point claims that cite the baseline numbers. Needs the D-202 arm crossing and hub stiffness modelled (or listed as a limit).

## 7. Open items and blocker
- Not done: current-geometry re-baseline of the script (T-065b); fin-skin fatigue from the 30 m/s2 fin-tip acceleration ("-").
- The tree has uncommitted edits by other sessions (docs/session-log.md, cad/out); HEAD `5561c0bb` already contains the overwritten structures_run.md. My edits (structures_a.py, structures_run.md, T065 files) are uncommitted.
- Blocker: none.
