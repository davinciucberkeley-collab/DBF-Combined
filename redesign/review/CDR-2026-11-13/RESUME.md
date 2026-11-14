# Paused 2026-11-13: where the CDR fix round stands and how to resume

The work was paused mid-round at the owner's request. Everything below is committed on `redesign/v1` as a WIP commit.
It has **not** been verified end to end. Run the checks in section 3 before trusting any number.

## 1. State

| Stream | State | Record |
|---|---|---|
| Board (aero, structures, electrical, build-and-test, chair) | Done, committed `53b02c9` | `CDR-*.md`, `CDR-SUMMARY.md` |
| S1 structures | Done | `fixes/S1.md` (D-105…). Cap 24.5 N (D-138); landing-shoe legs 7 → 30 mm (+10.9 g) |
| S2 proof graph, power and propulsion models | **Stopped mid-work** | `fixes/S2.md` (partial). The zero-limit fix in `proofs/build_graph.py`, the winding-current claim and `r_ext_mohm` 7.9 are in; the graph was not re-run to a fixed point |
| S3 flight software and aero | Done | `fixes/S3.md` (D-120…D-128). Parameter names checked against ArduPilot 4.7.1; SITL installed (Cygwin build); `MIXING_GAIN` 0.65; CG range [0.0394, 0.0513] |
| S4 BOM, mass, schedule, docs, box | Done | `fixes/S4.md` (D-130…D-134). Reserve at order $98 pessimistic; flight-ready over $2 000 (needs a team decision) |
| Integrator | Done | `fixes/INTEGRATOR.md` (D-135…D-138): power board on a foam pad, spar slot and cap `WNG-008`, mass rebalanced (predicted 2 502 g, +98 g to the gate), cap 24.5 N |
| Build-sequence physics rework (owner: "every step must pass a real physics check, no exemptions") | **Stopped mid-work** | `showcase/animation/assembly_check.py`, `assembly_plan.py`, `render_build.py` edited. It was making the convex cutter test faster at the sample points. Not yet run to PASS |
| Website redesign | Done on its own branch `ui-redesign-survey` (`4281a19`), **not merged** | `site/UI-SURVEY.md` (108 sites) |
| Wing FEA level 3 (`team/C2/fea/wing_fea_d68.py --phase local --job d68/3`) | Was still running at pause | The merge commands are in `fixes/S1.md` |

The change-log rows from `fixes/S1.md`, `S2.md`, `S3.md`, `S4.md` and `INTEGRATOR.md` are **not yet merged** into
`params/CHANGE-LOG.md`.

## 2. Resume order

1. **Agents.** Resume the two stopped agents with a message (their transcripts are kept), or start fresh ones with
   the task text in this file:
   - S2: finish the CDR-03 tooling, then `python -I redesign/proofs/build_graph.py` to a fixed point. Report the newly
     visible fails.
   - The build-sequence rework: finish the brief in this file, section 1. Every OVERRIDES exemption becomes a real
     motion: swept, rotated, built body by body, or elastically checked with numbers. The spar `cut_by` exemption is
     removed because `WNG-008` now exists. Re-plan the stage-10 feet on the 30 mm shoe legs. Iterate until the check
     reports PASS with 0 violations and no exempted pair.
2. **Merge** the five fixes files into `params/CHANGE-LOG.md` (ids D-105…D-138; check there is no clash). Refresh
   `STATUS.md` fail counts from `proofs/out/graph.json`.
3. **Verify in this order:**
   1. `bash` the scratch `verify.sh`: generators, `fusion/check.py`, `merge_check.py`, GLB export, `collide.py --glb`.
   2. `python -I redesign/showcase/animation/assembly_check.py` (about 11 min).
   3. The proof graph to a fixed point.
4. **Media:** `render_build.py` (about 19 min), then re-encode the site copy of the film to under 15 MB (scratch
   `transcode.py`, 850 kbps), the media script, `make_shop_files.py`.
5. **Website:** merge `ui-redesign-survey` into `redesign/v1`, regenerate (`make_build_guide.py`,
   `make_proof_embed.py`, `make_index.py`), check it in a browser at desktop and 400 px, light and dark.
6. **Push** and republish the Explorer (https://claude.ai/artifact/XYkihMreBq6Gn7deTEwSC8) in two parts: data and
   renders, then animation.

## 3. Decisions waiting on the student team

| Item | Options | Source |
|---|---|---|
| Flight-ready budget is over $2 000 ($2 042–2 236) | More money outside the $2 000, or a scope cut; B10 (US-stock pack) and L5 (Jacobs ShopBot) close the baseline but not the pessimistic case | `fixes/S4.md` |
| Crash reserve rule (B3) | $309 or about $228 (K09-L's own repair bill) or about $141 net of held spares | `CDR-SUMMARY.md`, `fixes/S4.md` |
| `R-BUILD-HOURS` re-wording (B2) | ≤ 90 h of build (stages 2–10), ≤ 5 weeks from first cut | `fixes/S4.md` P-S4-2 |
| December order split if the twin has not transitioned by 13 Dec (B5) | Common lines only; carbon held to 5 Jan | `CDR-SUMMARY.md` |
| D-127 cant 10° contingency, D-128 40 % differential, `AIRSPEED_MAX` 20 | PROPOSED | `fixes/S3.md` |
| Root `CLAUDE.md` box size 1.25 × 0.56 × 0.54 m | PROPOSED | `fixes/S4.md` P-S4-3 |
| Paperwork by 17–24 Nov: pilot named, PI sponsor, UC Drone Program, FAA and TRUST, flight request, AMA | HUMAN | `CDR-SUMMARY.md` |

## 4. Open engineering fails to carry

- **Wing block-pocket corners:** foam at 284 / 193 kPa against 150 / 120 kPa; D1 needs a fix (CDR-13).
- **Station-mode separation:** 0.147 against 0.20; only a stiffer tube passes (CDR-19).
- **Hover yaw:** wingtip into wind at 20° error, ratio 1.32 against 1.5.
- **Transition pitch use:** 0.91 against 0.60 (S3).
- **Transition gate:** `CL-B2R3-VTR-GATE-FWD` reads 15.70 against 15.6 after the airspeed change (S3).
- **Piston flange:** RF 0.77; the fix needs A1's stroke key (S1).
- **Fin face:** the shell model and the 3-D model disagree. Run `T-C4-FIN-PROOF` before cutting flight half-fins.
