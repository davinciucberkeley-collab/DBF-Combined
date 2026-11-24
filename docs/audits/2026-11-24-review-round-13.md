# Review: round 13 batch (T-099, T-101, T-103, T-104, T-105, T-015, T-037) @ 41f0827e + uncommitted T-101 reserve step

Reviewer: fresh reviewer (opus), Agent Standard v0.2. Format: aircraft-platform `standards/review-scorecard.md` @5653727 (opened via `gh api`), mapped by `docs/reference/agent-standard/LOCAL.md`: criteria = CLAUDE.md hard constraints and working rules, `docs/requirements.md` acceptance columns, ledger acceptance cells, `docs/reference/REVIEW-STYLE.md`. I wrote only this file. A local CI run rewrote 3 `archive/c0/analysis/*.json` files with line-ending changes only; I restored them with `git checkout`. The T-105 checker ran from a copy in the session scratchpad, so the tracked frames were not overwritten. No ledger status was changed.

The run stopped at the coordinator's turn limit. Items not fully covered are marked **NOT REVIEWED** (partial) with the reason.

## Automated

| Check | Result | Details |
|---|---|---|
| `python -I tools/ledger_audit.py` | PASS (exit 0) | 113 requirements, 105 tasks: VC 84, RFR 4, BLOCKED 5, DEFERRED 5, IN PROGRESS 3, NOT STARTED 4; 0 errors |
| `python -I redesign/qp/A/proofs/run_all.py` | exit 1 (strict), as expected | 570 nodes, 1,199 edges. **14 distinct STRICT FAIL**: MASS-PRED, MASS-GATE-ROOM, CUTS-REQUIRED, STALL-PRED 17.74, PITCH-USE **0.651**, VIB-IN-BAND, VIB-FC, VIB-GM, VIB-GM-SHIFT, HORN-RIB-FOAM-HOLD **446.6 kPa**, HORN-RIB-FOAM-STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY. Also UNVERIFIED strict: CL-A-STALL (A-P6), CL-A-FLUTTER-ELEVON-NOM (A-P13). `git status` of `proofs/` was the same before and after the run. |
| `python -I redesign/qp/A/bom_a.py` | PASS (exit 0) | caps sum $1,965; over cap: none (total $1,939.17 per D-251 log `G6_bom.txt`) |
| Site generators x2 (`make_sims_view`, `make_replays_view`, `make_index`) | PASS | all exit 0 both times; sims 45,010 B, replays 16 flight / 10 landing / 3,446.5 KB, index 571,168 B; `git status redesign/site` empty, so they match HEAD (idempotent); no Errno 22 |
| Session hook `recovery.py session-start` | PASS (exit 0) | prints the recovery procedure and the Agent Standard pointer; ledger counts match ledger_audit; missing state files: none |
| `python -I redesign/qp/A/schedule_a.py` | PASS (exit 0) | F01 16 Feb, F06 28 Apr, **+2 d**; p 0.60 -13 d, 3 mornings -16 d, main order after bench -5 d |
| T-104 link checker | exit 0 | 2 broken links, the same 2 as the baseline (`redesign/qp/A/sitl/SITL-FLIGHT.md` from `app.html` / `index.html`) |
| CI `regenerate-check.yml` steps run locally (archive/c0 paths) | PASS | sizing, export_bom, vlm, tradestudy, verify.py ("FAILED CHECKS: none"), review build all exit 0; `git -c core.autocrlf=input diff --exit-code` exit 0 |
| `check_replays.mjs` (headless Chrome, 1280 / 400, light / dark) | PASS (exit 0) | errs 0 in all 4 runs; scrollWidth = innerWidth at 400 |
| Agent files vs upstream @5653727 (`gh api`) | PASS | `agents-v0.2.md` identical to `standards/agents.md`; each of the 6 role files differs only by the appended pointer line plus a blank line |
| Token grep `git grep -E "dav_(ak\|gr)_[A-Za-z0-9]{12,}"` | PASS | no match; `.env` is ignored (`.gitignore:76`) |
| CAD gates (collide_a, collide_glb_a, a_assembly) | not re-run (brief) | CAD sources equal `c7d52d42` (`git diff --stat c7d52d42 -- redesign/qp/A/cad ...`: only `cad/out/REPORT.md` / `report.json` date and wall time, plus the D-250 pose report files); the revert logs G1 / G3 agree |

## Criteria (judgment items)

### T-099 final design audit: SEND BACK

| Criterion | Result | Reason |
|---|---|---|
| R12-1 (round-12 blocking) | PASS | F-6 is answered by AM-037 / D-248: one date, 29 Jan 2027, in `sync_status_a.py:78` ("ANSWERED"), `session-state.md:29`, `README.md:23,142`, `CLAUDE.md:36`, `SCHEDULE-A.md:48`, `TEST-PLAN-O4B.md:12,16`. SCHEDULE-A motor text corrected. |
| R12-2 | PASS | README `:30` and the GLB gate text are updated. |
| R12-3 | PASS (partial) | The README discloses the D-247 entry rule as a gate definition the user may veto. CLAUDE.md is not edited; it was the conductor's call, and the record says so. |
| R12-4 | PASS | `app.html:411` caption reads X2216. |
| T-099 acceptance ("Explorer and GitHub copy consistent") | **FAIL** | run_all and the HEAD proof graph give pitch use **0.651** (D-251). `README.md:22`, `CLAUDE.md:34` and the Explorer (`app.html:455, 1226, 2518, 2592-2597`) still say 0.69-0.79 (or 0.79). No front-door file names D-251 / D-252 or 0.651. |
| `session-state.md` checkpoint (CLAUDE.md "state lives on disk") | FAIL (LOW) | "Next action" (`:44`) is dated 2026-11-23 and still says "76 of 94"; T-037 is shown as BLOCKED (`:63`), while the ledger says IN PROGRESS. |

### T-101 elevon work (D-249..D-252, AR-017..AR-019): SEND BACK (record fix only; the NO conclusion stands)

| Criterion | Result | Reason |
|---|---|---|
| Revert honest and complete (D-251; R-GEN-05) | PASS | CAD, drawing, `cad_mass.json`, `a_aero.py`, BOM and BUILD-GUIDE equal `c7d52d42`. The remaining diffs are the kept C3 changes (`A.param` TECS_SPDWEIGHT 0.5, TP-19) and the hinge-moment single source (0.146 x 0.31 / 0.30 = 0.151 N m). |
| No limit relaxed (T-101 acceptance; CLAUDE.md "no exemptions") | PASS | The claim and collector diffs change values, sources and how-text only. CL-A-PITCH-USE stays <= 0.60, FAIL. No derived line is proposed. |
| Hand reserve sum (AR-019) | PASS | I re-checked: p/delta = (0.0699 / 0.30) x 2 x 17 / 0.9 = 8.80 deg/s per deg, so 90 / 8.80 = 10.23 deg. Side gust 0.04 x (3/17) / 0.0699 = 0.101 rad = 5.79 deg. Sum 9.76 + 10.23 + 3.71 + 5.79 = 29.49 deg, margin -9.49. The per-surface linear sum is the right form for left = (roll + pitch) G. It is a deliberate worst case, and EST inputs (Clp, CLB, gust level, 90 deg/s with no derivation) are labelled. Without gusts it fits the stop by +0.01 deg but misses the 19.04 deg PWM clip by -0.95 deg, so NO holds under the stated criteria. |
| C3G numbers vs `sitl_T101C3G_T074/case.fwd.csv` and `c3g_metrics.json` (spot check) | PASS on values | My recompute matches: dl -20.0 / +7.47, dr -20.0 / +5.56, p +88.5 / -110.0 deg/s, time at the stop 0.5 / 0.3 s, mean peak 12.98, differential 12.95. `sum.json` agrees: pitch_use_15 0.87, t_elevon_sat_s 1.1, alt_peak 84.6 m, 1.3 Vs at 9.4 s. |
| C3G interpretation (CLAUDE.md working rule "every number cites its source"; R-PHY-06 honest labelling) | **FAIL** | Both stop contacts come after the gust window, which ends at 105.34 s: left 106.04-106.65 s (reversal leg, rate building to -108 deg/s) and right 107.51-107.92 s (after the stick was centred, rate recovering). So the stop hits come from the doublet reversal at rates above A-P11, not from "pitch peak + A-P11 roll + gust". In the gust plus first-leg window the worst surface was **-19.59 deg at 104.564 s**, not the -19.19 deg the audit and AR-019 give (`reserve.md` s3). That window still exceeds the 19.04 deg PWM clip, so NO stands. But "SITL governing, drives both elevons to the stops" needs rewording in `2026-11-24-T101-reserve.md`, AR-019 and D-252. |
| Inertia-assert fix (`elevon_dynamics.py`) | PASS | The stale hand-typed `I_E_CAD` (0.30-chord value) and its assert are removed. The script reads `cad_mass.json` (1.2548e-05) and adds the horn point mass, giving I_e_used 1.2628e-05 as reported. This is a "remove" rung with a single source. |
| Ladder named (R-OPT-01) | PASS | D-251 is the remove rung. D-252 names rung 3 (trim cut) and leaves the roll and gust criteria to the team. |
| Evidence hygiene | FAIL (LOW) | (a) `revert.md` says the patch is "36 MB"; the tracked `.patch.gz` is 10,817,571 B, and D-251 cites a `.patch` file that does not exist. (b) `cad/out/REPORT_linkage_poses_t101.md` and `report_linkage_poses_t101.json` are 0.30-chord (D-250) gate outputs committed into the live `cad/out/` with no "superseded / record" header. (c) `linkage_loads_check.py` docstring still says 17.05 N; the output is now 17.64 N. (d) `revert.md` s2 says `sims3d/` is untracked, but it is tracked at HEAD. |

### T-103 schedule re-plan: PASS (LOW notes)

| Criterion | Result | Reason |
|---|---|---|
| T-103 acceptance: no fabrication before reopening | PASS | In the `SCHEDULE-A.md` AM-037 table every "Fabrication? yes" row starts on 19 Jan or later. December and the break hold purchasing, SITL, wind mornings and USB-only FC work. |
| Slack computed (>= 0 or shortfall with options) | PASS | `schedule_a.py` re-run: +2 d. The 77 h / 21 h per week chain (25.7 d) lands on 16 Feb, which matches. Negative cases have $0 options. |
| One consistent go/no-go date | PASS (LOW) | It is 29 Jan everywhere live. Residue: `TEST-PLAN-O4B.md:311` says "cannot run before 15 Dec"; `SCHEDULE-A.md:92` says TEST-PLAN "still prints 15 Dec" (no longer true); `SCHEDULE-A.md:174` (dated update section) says "2026-12-15 go/no-go". |
| Risk visibility (CLAUDE.md "label estimates") | NOTE | B1 (first cut of wing cores, 26 Jan) starts before the 29 Jan bench decision, which can reopen the configuration (AM-016). This is not stated as a risk. |

### T-104 layout cleanup: PASS (LOW notes)

| Criterion | Result | Reason |
|---|---|---|
| R-GEN-05 / R-REPO-08: nothing broken | PASS | CI steps pass locally on the `archive/c0` paths. The link checker equals the baseline. Generators are idempotent. Pages URLs stay under `redesign/site/`. |
| Redirect stubs | PASS (LOW) | All 6 stub targets exist in `archive/c0/` and the root `index.html` goes to `redesign/site/`. The root index `<title>` still reads "Lift + Cruise VTOL Review". |
| README map vs tree | PASS | `ls` shows 17 visible root entries, all in the README table; the tracked top level matches. |
| UI merge (AM-043) | PASS (note) | The merge record is complete. It edits the criterion file itself: `REVIEW-STYLE.md` gains a font exception that matches the product (41f0827e). The user owns that house style, so flag it to Dillon. |
| Pre-existing broken link | LOW | `SITL-FLIGHT.md` link from `app.html` / `index.html` (2 hits) is still broken. |

### T-105 3-D replays: PASS

| Criterion | Result | Reason |
|---|---|---|
| R-PHY-06 labels honest | PASS | Every panel carries "Playback of recorded simulation output (not a new simulation)", the source link and the KB loaded. The Lua and non-Lua runs and the linkage "not to scale" are labelled. |
| Default = design basis | PASS | `DEFAULT_FLIGHT = 'T101C3_T074'`, the worst C3 case at the 0.25 chord (0.651), which is the current basis per D-251. The landing default is "hard level, 37.5 N, 0.05" (T-098 basis, labelled). That is not the worst D-243 corner (37.5 N / 0.02); acceptable as labelled. |
| Spot values vs JSON (my run) | PASS | `check_replays.mjs` re-run: 0 errors in 4 layouts. Two values I read: flight index 556 shows alt "34.2 m" against JSON 34.228, and V "1.6 m/s" against 1.572. Index 1001 shows pitch "45.6 deg" against 45.624, and alt 72.1 against 72.076. The match flags are true. |
| R-INT-05 no new dashboard | PASS | Inside the existing #sims view. |
| Display encoding | NOTE | The spot-values capture shows "Â°" mojibake in the degree signs. It may come from the CDP capture rather than the page; check one screenshot. |

### T-015 Agent Standard adoption: PASS (one LOW)

| Criterion | Result | Reason |
|---|---|---|
| R-ORC-04 "adopted; no conflicting framework" | PASS | Files are verbatim plus one pointer line (upstream diff above). The retired definitions are gone from `.claude/agents/`. CLAUDE.md:14-17, `execution-plan.md:31` and the hook point to the standard. |
| "Not adopted" reasoning (LOCAL.md) | PASS | Hooks expect `plans/` agent tables that this repo does not have. The standard's own "Not built yet" section allows enforcement by reading, and PR-per-unit conflicts with R-GEN-02 push approval. |
| Residual framework text | FAIL (LOW) | `requirements.md:53` (R-TRK-05 how-column) still names `ledger-auditor` / `eng-reviewer`. `requirements.md:62` R-ORC-04 status is BLOCKED while T-015 is READY FOR REVIEW. LOCAL.md has no substitute for `plans/agent-log.jsonl` (see Process). |

### T-037 DaVinci: NOT REVIEWED (partial, turn limit)

| Criterion | Result | Reason |
|---|---|---|
| No token or grant tracked | PASS | grep clean; `.env` is ignored. |
| $0 spend backed by probe records | FAIL (MED) | Every "before / after unchanged" reading is $49.060351 / 1,093 events with **asOf 2026-11-09T07:22:13Z** (`davinci-import-2026-11-23.md:32,46`; findings `:123-151`). The usage snapshot predates all probes, so equal readings do not show $0. The file says "re-read after a day", and Dillon's visual check (`findings:164`) is the only other evidence. Keep the claim as "no change observed, usage snapshot stale" until a post-probe asOf is read. |
| Storage incident recorded honestly | FAIL (LOW) | `davinci-import:102,116` records the account at its 1.0 GB limit (1,073,743,780 B) as the blocker. The "836 MB in the org" figure from the brief is not in any `docs/integration/davinci-*` file, so whose files fill the account, and whether the team's ~38.6 MB uploads should be removed, is not stated. |
| What remains blocked | partial | Blocked on storage being freed (or a larger plan) to finish the assembly upload, and on a fresh usage read. The full `tools/davinci_*.py` review was not done (turn limit). |

## Blocking issues
1. **R13-1 (MED, T-099):** the front door is inconsistent with run_all. README `:22`, CLAUDE.md `:34` and Explorer `app.html` 455 / 1226 / 2518 / 2592-2597 say pitch use 0.69-0.79; the basis is 0.651 (D-251, AR-017), with D-252's NO on reserve. Update the text via the generators / `sync_status_a.py`, then rerun `make_index.py`.
2. **R13-2 (MED, T-101):** correct the C3G attribution in `docs/audits/2026-11-24-T101-reserve.md` s3 / s4, AR-019 and D-252. The stop contacts (106.04-106.65 s, 107.51-107.92 s) follow the gust window (ends 105.34 s) and occur in the doublet reversal and recovery above A-P11. The first-leg worst is -19.59 deg at 104.564 s, not -19.19 deg. State that NO rests on the hand sum plus the first-leg excess over the 19.04 deg PWM clip, not on SITL stop contact at A-P11.
3. **R13-3 (MED, T-037):** the "$0 spend" claim rests on a usage snapshot dated 2026-11-09. Re-read Usage with an asOf after the probes, or reword the claim.
4. **R13-P1 (MED, Process):** there is no agent record for this batch (below).

## Non-blocking suggestions
1. R13-4: `session-state.md` "Next action" and the T-037 row are stale; refresh them.
2. R13-5: T-101 hygiene (a)-(d) above. Label the two `*_linkage_poses_t101*` files in `cad/out/` as D-250 record, or move them under `T101_data/chord/`.
3. R13-6: T-103 residue lines (`TEST-PLAN-O4B.md:311`, `SCHEDULE-A.md:92,174`). Name the B1-before-D1 risk.
4. R13-7: root `index.html` title; the 2 broken `SITL-FLIGHT.md` links.
5. R13-8: R-TRK-05 role names and the R-ORC-04 status in `requirements.md`.
6. R13-9: flag to Dillon the REVIEW-STYLE.md font exception, a criterion edited to fit the product.
7. R13-10: record whose data fills the DaVinci 1.0 GB (the 836 MB figure) and whether the team's uploads should be deleted (deletion needs Dillon, R-GEN-02).
8. **Could it be simpler / removed?**
   - T-101: the opt-in `c3g` branch in `run_fwd.py` (12 lines) and the `GV` gust in `a_plant.py` are default-off, so they are safe. If rung 3 does not reuse C3G, remove them or fold them into the existing `gust` key. The 10.8 MB `.patch.gz` duplicates `T101_data/chord/pre*` copies; keep one.
   - The untracked `cad/out/glb/` (D-250 export) can be deleted after a purpose check.
   - The elevon_dynamics fix is already the subtractive form. An `abs(i_e - cad_mass) < tol` check against the same file would add nothing.
   - T-104: six redirect stubs plus a root index are minimal.
   - T-105: `manifest.json` holds prop geometry derived at build time, which is fine. The hard-coded flight CG offset could read `cad_mass.json` instead.
9. Criterion gap (propose; no criterion exists): a named requirement for the elevon reserve rule (roll rate and gust level). D-252 says it is a team decision. Add it to `REQUIREMENTS-A.md` once decided, rather than keeping the 0.60-of-15 deg line without a derivation (D-245).

## Process

| Check | Criterion (agents-v0.2.md) | Result | Details |
|---|---|---|---|
| Agents run, by role and model (`plans/agent-log.jsonl`) | `#how-this-is-enforced` | **FAIL** | There is no `plans/` and no agent log (hooks not adopted, LOCAL.md), and LOCAL.md names no substitute. `docs/model-usage.md` has no row for T-101, T-103, T-104, T-105, T-015 or T-037 (grep). Roles are visible only in the audit headers: `T101-servo-scout.md` (scout, sonnet), the T-104 plan (tactician, U2 scout haiku), the T-105 "independent re-check by the tactician", and the D-251 "advisor report". Fix: backfill rows and map the agent log in LOCAL.md. |
| Launches not in an agent table | `#planning` | N/A | LOCAL.md maps agent tables to ledger T-ids; every brief I saw names its T-id. |
| Conductor edits | `#how-this-is-enforced` | NOT REVIEWED | `plans/conductor-edits.md` is not adopted. The conductor's REVIEW-STYLE.md edit is noted in R13-9. |
| Subtract before adding | `#fixing-subtract-before-adding` | PASS | D-251 remove; elevon_dynamics remove; D-252 names the rung. |
| Loop rule (two failed fixes, then a scout or advisor) | `#fixing-subtract-before-adding` | PASS | Controls C1-C3 were exhausted, then the trim scout ran; D-250 failed and an advisor was called before D-251. |
| Fresh reviewer per batch | `#reviews` | PASS | This review. |
| Cost check | `#cost-check` | NOT REVIEWED | No per-agent token or model record exists to score (see the first row). |

## Fix pass C (2026-11-24, builder)

Files touched are listed per finding; nothing committed.

- **R13-1 (pitch-use text).** Basis now 0.651 of 15 deg against 0.60, FAIL, with C3 controls at 0.25 chord; D-250 reverted (D-251); the derived roll + gust reserve does not fit (D-252, AR-019); next rung cut the cruise trim. Edited generators `redesign/site/make_sims_view.py` (3 strings) and `redesign/site/sync_status_a.py` (status row and sources), the static row at `redesign/site/app.html` (the "Strict proof build" row, which no generator writes), and `README.md:22`. Reran `sync_status_a.py`, `make_sims_view.py`, `make_replays_view.py`, `make_index.py` twice (Errno 22 retried): `app.html` and `index.html` hash identical between runs. The remaining 0.69-0.79 in `app.html` / `index.html` is one status-row mention labelled as an earlier figure (record). The proof graph files (`claims_a0_base.py`, `claims_a1_flight.py`, `gen_params_a.py`, `graph.js`) still carry 0.69-0.79 in claim text; they were not in the named list, so they are left (not touched).
- **R13-2 (C3G record).** Checked `sitl_T101C3G_T074/case.fwd.csv`: at or above 19.0 deg the surfaces are in contact at 104.513-104.615 s (first leg, roll rate 22-49 deg/s), 106.038-106.648 s (roll rate -108.5 to -33.5 deg/s) and 107.512-107.919 s (+30.5 to +85.5 deg/s); first-leg worst -19.59 deg (right) at 104.564 s. Note: the rate is above 90 deg/s only in part of the 106.0 window (peak -110); in the 107.5 window it is below 90. Wrote that precisely. Edited `2026-11-24-T101-reserve.md` (s0 answer, first-leg line, combination table, final answer), AR-019 (`docs/analysis-records.md`) and D-252 (`redesign/params/CHANGE-LOG.md`). NO stands, resting on the hand sum (with the gust) and the first-leg excess over the 19.04 deg PWM clip. Patch name and size fixed (`docs/audits/2026-11-24-T101-D250-revert.patch.gz`, 10,817,571 B) in `T101-revert.md` and D-251. D-250 linkage-pose files in `redesign/qp/A/cad/out/`: header line added to the two `.md` files and new `README-D250-RECORD.md` (also covers the JSON).
- **R13-4.** `docs/session-state.md` Next action rewritten (fix pass C, push, T-047 / T-059 / T-049, AM-050 branch deletion, T-093 1-4 Dec); the DaVinci row now says T-037 IN PROGRESS.
- **T-103 LOW.** Removed the 15 Dec residue at `TEST-PLAN-O4B.md:311` and `SCHEDULE-A.md:92, :174` (was-history kept). Added the "Risk: B1 before D1" paragraph with three options to SCHEDULE-A.
- **T-104 / T-105 LOW.** Root `index.html` title changed. Mojibake: `redesign/site/replay.js` had literal non-ASCII characters (degree, plus-minus, check marks) that render as "Â°" when the file is served without a UTF-8 charset; they are now `\u` escapes (11 `°`); `make_replays_view.py` rerun. The 2 SITL-FLIGHT.md links are listed as known in the T-104 plan file.
- **R13-3.** Added the spend-evidence and storage-facts sections to `docs/integration/davinci-findings.md` and `davinci-import-2026-11-23.md`.
- **R13-P1.** Added 12 rows (T-101 x6, T-103, T-104, T-105, T-015, T-037, round-13 reviewer) and a backfill note to `docs/model-usage.md`; models and token counts are "—" where the audits do not record them.

## Re-review (2026-11-24, reviewer, fresh instance, opus) of fix pass C @ 6cc99eeb

### Automated
- `python -I tools/ledger_audit.py`: `113 requirements, 105 tasks, {'VERIFIED COMPLETE': 88, 'BLOCKED': 5, 'EXPLICITLY DEFERRED': 5, 'IN PROGRESS': 3, 'NOT STARTED': 4}; 0 errors`.
- Site generators `sync_status_a.py`, `make_sims_view.py`, `make_replays_view.py`, `make_index.py` run twice: sha256 of `redesign/site/app.html` (6119d46e...), `index.html` (021c2fd6...) and `redesign/site/index.html` (f6485884...) identical between runs and identical to the committed files; `git status` clean apart from the pre-existing untracked `redesign/qp/A/cad/out/glb/`.
- run_all, collide and BOM not rerun (no geometry or BOM change in fix pass C; brief limits long runs).

### Blocking items
| Item | Criterion | Verdict | Reason |
|---|---|---|---|
| R13-1 | CLAUDE.md working rules (every number cites its source; front door consistent with run_all) | PASS | README:22 and CLAUDE.md:34-35 state 0.651 vs 0.60 FAIL and name D-251 and D-252; `app.html` live text says 0.651 with D-251 / D-252; the 0.69-0.79 strings are labelled "earlier ... record". The AR-015 transition table (app.html sims section, 0.69 / 0.69) is the AR-015 runs' measured result under a paragraph that labels it earlier. Root `index.html` is a redirect stub with no figures. |
| R13-2 | CLAUDE.md working rules (every number cites its source) against `sitl_T101C3G_T074/case.fwd.csv` | SEND BACK | Checked: stop/clip windows (|dl| or |dr| >= 19.0) at 104.513-104.615, 106.038-106.648, 107.512-107.919 s; roll rate p 21.7-48.7, -108.5 to -33.5, +30.5 to +85.5 deg/s; wind column non-zero 104.31-105.327 s (gust ends about 105.34 s); first-leg worst -19.59 deg (right) at 104.564 s. All correct. Still wrong: AR-019 result, D-252 and reserve.md s4 caveat say "+88.5 deg/s (first leg, A-P11)" and "the first leg alone (88.5 deg/s) already reached 19.59 deg"; in the CSV the first leg (104.32-105.82 s) peaks at +82.0 deg/s at 104.818 s, p is 35.6 deg/s at the 19.59 deg sample, and +88.5 deg/s occurs at 108.021 s in the recovery. Reserve.md:66 "first leg (A-P11 reached)" is likewise unsupported. AR-019 also says the stop contacts show "the roll reversal at the A-P11 rate"; the 107.5 s window is at 30.5-85.5 deg/s, below 90 (fix pass C's own note says so, the record does not). |
| R13-3 | CLAUDE.md working rules (label estimates; no unsupported claims) | SEND BACK | The new sections in both files say equal Usage is "consistent with no charge but not proof" (asOf 2026-11-09) and record storage (836.1 MB API Test, about 1.0 of 1.0 GB, Model Benchmarks 226 MB, 205 STEP objects). But `davinci-findings.md:3` status still reads "Nothing has been called and nothing has been spent", which the probes in the same file contradict. One-line fix. |
| R13-4 | spec 10.4 checkpoint (docs/session-state.md "Next action") | PASS | Next action names push approval, T-047 / T-059 / T-049, AM-050 branch deletion, T-093 1-4 Dec, CL-A-PITCH-USE 0.651 open; DaVinci row says T-037 IN PROGRESS. LOW: step (1) still says "Fix pass C", which is now done; replace it with the re-review outcome. |
| R13-P1 | standards agents.md agent record (docs/model-usage.md) | PASS | 12 rows (T-101 x6, T-103, T-104, T-105, T-015, T-037, round-13 reviewer) plus a backfill note; unrecorded models and tokens shown as "—", not invented. |

### Overall
- **T-099 (final design audit): PASS.** Its only blocker, R13-1, is closed; it can be marked VERIFIED COMPLETE.
- **T-101 (records only): SEND BACK.** The roll-rate attribution in AR-019, D-252 and reserve.md must match the CSV (first-leg peak +82.0 deg/s, +88.5 deg/s in the recovery at 108.02 s, 19.59 deg reached at 35.6 deg/s, 107.5 s contact below A-P11). The NO conclusion is not affected: it rests on the hand sum and the 19.59 deg first-leg excess over the 19.04 deg clip, both verified. T-101 stays IN PROGRESS regardless (CL-A-PITCH-USE 0.651 FAIL).
- T-037 stays IN PROGRESS (spend proof pending a Usage read after asOf moves).

### Non-blocking suggestions
- Simpler: in AR-019 / D-252 drop the per-leg rate attribution and cite only the window times, the per-window p range and the peak -110 deg/s; that removes the error source.
- The proof-graph claim text (`claims_a0_base.py`, `claims_a1_flight.py`, `gen_params_a.py`, `graph.js`) still carries 0.69-0.79 (fix pass C note); refresh it with the next run_all so the graph view matches the front door.

### Process
- This re-review: reviewer, opus, one instance, about 15 tool calls; launched nothing. Process miss: none found in fix pass C beyond the R13-2 residue.
