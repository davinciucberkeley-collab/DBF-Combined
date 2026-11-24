# Review round 10: T-035, T-095, T-097, T-098, Explorer Simulations view (2026-11-23)

Reviewer: independent eng-reviewer (opus). I did not write any of the work reviewed. I edited only this file. Ledger, spec,
requirements and CHANGE-LOG were not touched. Every verdict below rests on a check I ran myself; the authors' reports were
treated as claims.

## Verdicts
| Task | Verdict | Key check |
|---|---|---|
| T-035 design loop CLI | **VERIFIED** (recommend) | 4/4 tests pass (21.6 s); demo rerun to scratch reproduces the committed evidence.json exactly (volatile keys excluded) |
| T-095 Explorer stale text | **SEND BACK** (minor fix) | masses sum correctly (1,640.98 g); the Fins card still says "14 x 12 mm rib tubes", CAD is 25x23 |
| T-097 landing + SITL rerun | **VERIFIED as a record**, with a correction note required | defaults unchanged, no limit relaxed, SITL values match sum.json; the rib RF column is on a stale 14x12 tube and the audit wrongly says the rib is "read live from wing.py" |
| T-098 landing fix | **SEND BACK** | sweep tables recomputed from the raw JSON and match; spot reruns at 37.5 N (identical to the record file) and 31.5 N (20.1 mm FAIL, as the sweep) reproduce; but the TP-3 pass criterion admits (Fp, zeta) points the model fails, and D-244 is a relaxation with a wrong "fraction-preserving" argument |
| Explorer Simulations view | **VERIFIED** for fidelity to the JSON; text must be regenerated after T-098 is fixed | make_sims_view.py rerun in a scratch mirror produces a byte-identical app.html |
| ledger_audit | 0 errors | `python -I tools/ledger_audit.py`: 113 requirements, 99 tasks, 0 errors |

## T-035 design loop CLI
Checks run:
- `python -I tools/design_loop/test_design_loop.py`: 4 tests OK, 21.6 s (pytest not installed; the file runs as unittest).
- `python -I tools/design_loop/cli.py run --set pack_capacity_ah=3.3 --name pack-3p3Ah --evidence-dir <scratch>/demo`: exit 0.
  The new evidence.json equals `tools/design_loop/evidence/T035-demo-pack-3p3Ah/evidence.json` once `steps`, `started`,
  `wall_s`, `saved_design_dir`, `command` (paths and timestamps) are removed. `committed_unchanged` True,
  `baseline_matches_committed` {match True, n_diff 0}, 16 deltas, one flip CL-A-MASS-ITEM PASS -> FAIL (1.447 -> 1.496 kg).
- Coupling arithmetic recomputed: 270 g x 3.3 / 2.8 = 318.21 g (+48.21 g); 1,640.98 + 48.21 = 1,689.19 g. Matches.
- `git status` after the tests and the demo: no new modified files; `tools/design_loop/runs/` is ignored by
  `tools/design_loop/.gitignore`.
Findings: none blocking. Minor (info): the README/audit name the test runner `python -I ...test_design_loop.py`; that is what
works here (no pytest). Limits are stated honestly (no geometry parameters, Blender gates and SITL out of the loop).

## T-095 Explorer stale text
Checks run: summed `mass_g` by subsystem over all 131 parts of `redesign/site/data/viewer-data.json`:
wing 295.96, fins 192.96 + landing 20.00 = 212.96, cage 240.76, propulsion 391.04, power 282.40, avionics 73.73,
mechanisms 47.68, harness 68.68, assembly lump 27.77; total 1,640.98 g. All eight card masses in `app.html` #subsystems match
(rounded to 0.1 g). Card texts name X2216 (D-227), Kakute H743-Wing 75 mm left (D-239/D-240), D-212 rev 3, D-226 glass skin and
bulkheads, the machined hub (D-220). Remaining MN2212 / F405 mentions are labelled records.

| # | Severity | Finding | Evidence | Required fix |
|---|---|---|---|---|
| 95-1 | Major (stale engineering text in a card T-095 rewrote) | Fins card: "14 x 12 mm rib tubes to CF-sheet fin nodes". The drawn rib is 25x23 since T-077 p8 / D-226 (`redesign/qp/A/cad/amodel/wing.py` l.95 `RIB_OD, RIB_ID = 0.025, 0.023`; build step C1 and parts_links say 25x23). The 26.0 g mass in viewer-data is the 25x23 mass (pi/4 x (25^2-23^2) mm2 x 215.5 mm x 1.6 g/cm3 = 26.0 g). This is exactly the stale size that caused the T-097 rib-RF error. | `app.html` #subsystems Fins card; `wing.py` l.95 | Change the card to 25 x 23 mm. Root cause: the CAD part name in `wing.py` l.942 is still `'Fin rib tube 14x12 (%s)'`, so viewer-data carries the stale name (FIN-002-L/R); flag it to the CAD owner (rename needs a CAD regen, not part of T-095). |
| 95-2 | Minor | Intro says "the sum of the 129 placed parts"; viewer-data has 131 parts, all `in_model` True (130 without the hardware lump). | viewer-data.json | State the count that matches the data (or say what is excluded). |

## T-097 landing + SITL rerun at 1.881 kg
Checks run:
- `git diff` of the three code edits: `a_aero.py` adds `A_MOTOR=x2216` -> KV 880, Rm 0.089, I0 0.5 (matches `prop_a.py` l.11);
  `a_plant.py` KQ 0.0145 under the same switch (matches T089_report s1.1); `landing_mass_cad.py` adds the `LAND_PART_TABLE` env.
  Defaults verified by import: without the env KV 780 / Rm 0.173, with it 880 / 0.089. No pass line or limit constant touched.
- `T097_results.json` (202 rows): 14 FAIL rows; they are exactly the failures in the audit tables (30 N narrow + drift stroke /
  n / RF; 45 N hard level n and three RF rows; items sensitivity; pitch use on 15 deg).
- SITL `sum.json` of the four runs: pitch use 15/20/25 = 0.69/0.52/0.41 (Z5, Z5_lua), 0.79/0.59/0.47 (T074), 0.77/0.58/0.46
  (T074_lua), peak alt 89.4 / 84.9 m: all match the audit and AR-015.
- `landing_cad_1881_p30.txt`: failing case Fmax 183.9 N, stroke 20.3 mm, n 17.45 g, RF 0.42: matches.

| # | Severity | Finding | Evidence | Required fix |
|---|---|---|---|---|
| 97-1 | Major (accuracy of record) | All rib-root RF values in T-097 / AR-014 / T097_results.json are on the 14x12 tube: `landing_a.py` l.11 takes `LAND_RIB_OD/ID` from the environment with default 0.014/0.012, and T-097 did not set it. The audit s1 row "Landing geometry ... rib tube from `wing.py`; read live from `cad/amodel`" is false for the RF check (`cad_geom()` returns `rib=` but the RF uses the module constants). Stroke, n, tilt are unaffected (rib mass comes from the part table, 26.0 g each, correct). | `landing_a.py` l.10-12, l.120; T098 reproduction (plateau_rib14 at 30 N gives RF 0.42) | Add a correction note to AR-014 and the T-097 audit (and a `superseded_by` / note field on the RF rows of T097_results.json) pointing to AR-016. Do not delete the rows. |
| 97-2 | Info | The pitch-use 20 deg margin in the T-074 case (0.01-0.02) is inside the 0.03 scatter; T-097 says so. | sum.json | none |

Judgement on acceptability as a record: acceptable. The rerun did what it was asked (current mass, motor, CG; no limit relaxed;
defaults reproduce AR-008 via `GEOM_LEGACY`), and its stroke / n verdicts at 30 and 45 N still stand on the 25x23 rib
(plateau_rib25.json gives the same 20.3 mm / 17.45 g at 30 N and 12.60 g at 45 N). Only the RF column is wrong, and it is wrong
on the conservative side. T-098 corrects it, so T-097 can be VERIFIED once fix 97-1 (correction note) is in place; I recommend
VERIFIED conditional on that note, which is a documentation change only.

## T-098 landing fix
Checks run:
- Recomputed the worst-of-10 table for every plateau, both rib bases and both zeta values from the raw rows of
  `T098_data/plateau_rib25.json`, `plateau_rib14.json`, `zeta_rib25.json`. Every number in the audit table, D-243 and AR-016
  matches (e.g. 33 N 19.38 mm / 9.64 g / 2.66 deg / RF 3.19; 37.5 N 17.21 / 10.76 / 2.27 / 3.36; 43.5 N 12.24 g).
- The sweep and the record run used the same part table (SHA-256 of T097_data and T098_data copies identical, 6a5c3eda...).
- Spot reruns (rib 25x23 env as the audit, 1.881 kg, CAD mass model, two runs in parallel, 4 min 49 s / 4 min 53 s, exit 0):
  `landing_a.py 37.5`: all 10 case lines identical to `T098_data/landing_cad_1881_p37p5_rib25.txt` (`diff` empty; worst stroke
  17.2 mm, n 10.76 g, tilt 2.3 deg, RF 3.36). `landing_a.py 31.5`: worst stroke 20.1 mm (hard 10 narrow + drift, FAIL),
  n 9.26 g, tilt 2.8 deg, RF 2.44: identical to the 31.5 N row of `plateau_rib25.json`. The lower band edge and the chosen
  spec reproduce. Outputs: scratch only (not kept in the repo).
- `landing_a.py` itself is unmodified in the working tree (not in `git status`).

| # | Severity | Finding | Evidence | Required fix |
|---|---|---|---|---|
| 98-1 | **Critical** (the bench pass line accepts a failing design) | The new TP-3 criterion (TEST-PLAN-O4B s2.3) is "every specimen's Fp in 33.0-42.0 N ... with zeta <= 0.05". The model fails inside that region: at Fp 33 N, zeta 0.02 the hard case bottoms (20.47 mm) and hits 26.83 g (`zeta_rib25.json`). Lower zeta is the expected direction (s2.3 calls 0.02 the target), and zeta < 0.02 was not run at all. At 37.5 N, zeta 0.02 the margin is 0.44 mm. The band 33-42 N is a zeta = 0.05 result only; D-243 says so but the pass criterion does not encode it. | `zeta_rib25.json` rows Fp 33.0 zeta 0.02 | Make the TP-3 criterion a joint (Fp, zeta) acceptance region that the model passes at every corner: e.g. run zeta 0, 0.02, 0.035, 0.05 across 33-42 N and accept only the (Fp, zeta) set where all 10 cases pass, or require the measured (Fp, zeta) pair to be rerun in `landing_a.py` before acceptance. Update D-243, AR-016 and the sims view text. |
| 98-2 | **Major** (upper band edge not checked against the governing structure) | The D-226 cell / rib / bridge / strut / R4 rows were last sized at Fp 36 N (T-083: min RF 1.09-1.11 at zeta 0.05, x2.23). D-243 now accepts up to 42 N, which raises the peak foot force (landing_a Fmax 46.0 N at 30 N -> 55.9 N at 37.5 N in the record run; about +22 %). `landing_path_a.py` was not rerun, so the 37.5 and 42 N points are not shown to keep RF >= 1.0 on those rows. The T-098 audit lists this as a limit but still issues a pass criterion up to 42 N. | T083_report s5.3; `landing_cad_1881_p37p5_rib25.txt`; T-098 audit s2 last bullet | Rerun the T-083 strength table (`landing_path_a.py` / t083 demand method) at 37.5 and 42 N (and the zeta corners of 98-1), or cap the band at the plateau where those rows were shown to pass. |
| 98-3 | Major (internal contradiction in the paragraph T-098 edited) | TP-3 s2.3 "Pass" line keeps "peak foot force <= 37 N model value at 1.2 m/s", but the band plateau itself is 33-42 N and the record run gives Fmax 41-56 N; the line cannot be met by any passing foam. | TEST-PLAN-O4B.md s2.3 | Replace with the model value at the chosen spec (or remove), consistent with 98-2. |
| 98-4 | **Major** (D-244 is a relaxation, not a re-derivation) | See the D-244 judgement below. | SITL-FLIGHT.md l.25; D-244 | Re-derive the line from A's roll / gust authority need, or keep the 15 deg-equivalent allowance, and correct the fraction-preserving arithmetic. |
| 98-5 | Minor | T-098 coverage is the 10 AR-014 cases at mu 0.40; T-083 used 23 cases and mu 0.30 as well. The band is not shown for mu 0.30 or the other 13 cases. | T083_report s5.2 | State it as a limit in D-243 / AR-016 or run the 23-case, mu 0.30 set at the band edges. |
| 98-6 | Minor | D-244 "Peak individual surface 10.6 deg" is the Z5 value; the T-074 case reaches 12.0 deg (`sitl_T097_T074/sum.json` elevon_max_deg 12.0), which is the full 0.60 x 20 allowance. | sum.json | Quote the worst case. |

### D-244 judgement (pitch-use basis 20 deg instead of 15 deg)
The line came from SITL-FLIGHT.md l.25: "elevon pitch use <= 0.60 of 15 deg (B3 K09-L: 25 deg travel less 10 deg kept)".
Its intent is a control-authority reserve: of 25 deg travel, 10 deg is kept for roll / yaw / gusts, and pitch may use 0.60 of
the remaining 15 deg, i.e. at most 9 deg, leaving 16 deg (64 % of travel) free. The pitch-use line is a derived requirement,
so the team may re-derive it, but only with reasoning about the reserve it protects.

D-244 instead moves the basis to the 20 deg commanded endpoint. With the 0.60 kept, the allowed mean pitch deflection rises
from 9 deg to 12 deg and the reserve falls to 8 deg (40 % of travel), with no calculation of the roll or gust authority A needs
during transition. The reasoning given ("A has no hardware at 15 deg") answers why 15 is not a hardware number; it does not
answer what reserve A needs. On the merits this is a relaxation of the margin, not a re-derivation.

The arithmetic offered for the owner is also wrong. D-244 says the fraction-preserving reading "gives 12 deg pitch allowance
against a 10.4 deg mean pitch demand" (a pass). Preserving K09-L's fraction gives a basis of 20 x 15/25 = 12 deg, and the line
is 0.60 of the basis: 7.2 deg. Demand is 10.4 deg (Z5) to 11.8 deg (T-074, 0.59 x 20): use 0.87-0.98, FAIL. The literal reading
(20 - 10 = 10 deg basis) gives 1.04-1.18, FAIL. So both readings that keep K09-L's reserve logic fail; only the reading that
drops the reserve passes, and on T-074 it passes by 0.01-0.02, inside the 0.03 run-to-run scatter (not a demonstrated pass).

D-244 is honestly flagged for owner confirmation, which is right, but as written it should not be counted as closing the pitch
line. Required: either (a) derive A's needed roll / yaw-assist reserve (e.g. roll authority to hold a stated gust or the
transition roll demand seen in SITL, plus the T-076b scatter) and set the line from that, or (b) keep the pitch-use line FAIL
and take the ladder (pitch-authority fix) to the owner; in both cases fix the fraction-preserving arithmetic in D-244, the
trade table, AR-016 and the sims view.

## Explorer Simulations view (`redesign/site/make_sims_view.py`, #sims)
Checks run: copied `make_sims_view.py`, `app.html`, both results JSON and `T097_plots/` to a scratch mirror and ran the
generator: exit 0, "24756 bytes, plots 2, T-098 in"; the output app.html is byte-identical to the working-tree one, so the
section is generated from the JSON with no hand edits. `site.js` ROUTES and TITLES include `sims`; nav link `#sims` in
app.html l.128 and index.html l.136; section present in both. Spot-checked numbers in the rendered text against the JSON
(30 N and 45 N tables, 37.5 N table, plateau sweep with both rib columns, pitch-use rows): all match. "Failed 1 and 4 of 10
cases" is correct (30 N: 1; 45 N: hard level, hard 10 wide, 7/7, wide + drift y). Plot caption "one foot hits the stop at
about 170 N" matches the normal-force plot (Fmax 183.9 N in the text output is the force magnitude); acceptable.

| # | Severity | Finding | Required fix |
|---|---|---|---|
| SV-1 | Major (inherits T-098) | The view states "Landing passes all ten touchdown cases with a foam that crushes at 33-42 N" and presents the 20 deg basis as the proposed governing basis with "pass". Both rest on 98-1 / 98-4. | Regenerate after T-098 is fixed; state the zeta condition on the band. |
| SV-2 | Minor | "battery capacity and voltage sag are not modelled": `a_plant.py` l.154 models IR sag (vbus = vrest - 30 mohm x I); what is not modelled is discharge drift and capacity. | Reword to "state-of-charge drift and capacity". |
| SV-3 | Minor | The AR-015 intro gives only the Z5 margin ("passes with 0.08 to spare"); the T-074 margin 0.01-0.02 appears only later in the T-098 block. | Give both margins in the intro. |

The view is accurate to its source files; I mark it VERIFIED for fidelity, with SV-1 to be regenerated once T-098 is fixed.

## Commands run (this review)
| Command | Exit | Result |
|---|---|---|
| `python -I tools/ledger_audit.py` | 0 | 113 requirements, 99 tasks, 0 errors |
| `python -I tools/design_loop/test_design_loop.py` | 0 | 4 tests OK, 21.6 s |
| `python -I tools/design_loop/cli.py run --set pack_capacity_ah=3.3 ... --evidence-dir <scratch>/demo` | 0 | identical to committed evidence (volatile keys excluded) |
| viewer-data.json subsystem sum (inline python) | 0 | 1,640.98 g |
| `A_MOTOR=x2216` / unset import of `a_aero` | 0 | 880/0.089 vs 780/0.173 |
| recompute worst-of-10 from T098 sweep JSON (inline python) | 0 | matches audit |
| `make_sims_view.py` in scratch mirror | 0 | byte-identical app.html |
| `LAND_MASS_KG=1.881 LAND_MASS_MODEL=cad LAND_PART_TABLE=.../T097_data/cad_part_table_t097.json LAND_RIB_OD=0.025 LAND_RIB_ID=0.023 python -I landing_a.py 37.5` and `... 31.5` (structures/) | 0, 0 | 37.5 N identical to the T-098 record; 31.5 N 20.1 mm FAIL as the sweep |
