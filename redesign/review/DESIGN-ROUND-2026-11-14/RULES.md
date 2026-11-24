# Design round, 2026-11-14: rules (one agent per TEAM.md role)

After the CDR fix round (D-105 … D-144) the proof graph is clean (0 drift), but 13 requirements fail on 45 claims
(`proofs/out/graph.json`, `STATUS.md` row 6). This round closes the engineering fails by design changes.
Budget and schedule (R-BUDGET, R-RESERVE, R-BUILD-HOURS) are the students' decisions and are not in this round.
The configuration stays K09-L. Mass gate 2.6 kg: predicted 2 502 g today, margin +98 g against the 84 g build
overrun line (`team/A3/mass_rollup.py`).

The round follows `TEAM.md`: **each agent has exactly one role and does only that.** An earlier start with four
multi-role streams was stopped; what they found is in `notes-W.md`, `notes-F.md`, `notes-P.md`, `notes-A.md` in
this folder. Read the notes that touch your role, and re-check anything you use from them.

## Waves

| Wave | Roles | Job |
|---|---|---|
| 1 Analysis | C2, C4, C3, C5, B1, B2, B3, E1, E2 | Each analyses its fail, evaluates options in its own discipline, and recommends one fix with numbers. No CAD. |
| A1 resolves | A1 (integrator) | Reads every wave-1 report, settles the trade-offs between them (stiffness vs mass, yaw vs transition, CG), applies the `params.json` edits, and writes the design brief for wave 2. |
| 2 Design | D1, D3, D2, D5, D6, F4, F1 (only those with work) | Draw or set exactly what A1's brief says, run their generators and self-checks. |
| 3 Check | A3, then A1 runs collision, assembly check and proof graph; J6 board reviews | Mass and CG; gates; independent review before any fail counts as closed. |

## Ownership in wave 1

| Role | Fail to analyse | Writes only in |
|---|---|---|
| C2 wing structures | R-STRUCT-MARGIN: `CL-C2-FEA-FOAM-CORNER-*` (block-pocket corners, 126–288 kPa against 100–150 kPa) | `team/C2/` |
| C4 fin / motor-tube structures | R-VIBRATION: `CL-C4-SIM-SEP` 0.145 against 0.20 | `team/C4/` |
| C3 pod structures | R-PACK-RETENTION: `CL-C3-BLOCK-A-SHARE` 0.43 vs ≤ 0.10, `CL-C3-STOP-SECTION-PENALTY` 6.2 vs ≤ 1 mm | `team/C3/` |
| C5 landing / impact | R-PACK-RETENTION: `CL-C5-PACK-STACK-MARGIN` −3.3 mm; R-WIND: `CL-C5-SIM3D-V-BROADSIDE` 4.5 vs 5.0 m/s | `team/C5/` |
| B1 aero performance | R-MISSION side of cruise power and speed (17 m/s point), transition corridor | `team/B1/` |
| B2 wing aero | R-TRANSITION: `CL-B2R3-VTR-GATE-FWD` 15.70 vs 15.6 m/s (1.3 Vs, forward CG) | `team/B2/` |
| B3 stability and control | R-HOVER-AUTHORITY / R-WIND: `CL-B3-HOVER-YAW-WTIP-20` 1.32 vs 1.5; R-TRANSITION: `CL-B3-TRANS-PITCH-USE` 0.91 vs 0.60 | `team/B3/` |
| E1 propulsion | R-ESC-CURRENT: `CL-E1-ILIM-I` 30.0 vs 25 A at the 100 A limiter | `team/E1/` |
| E2 battery / energy | R-MISSION: `CL-E2-CRUISE-TO-LOW-PESS-V17` 4.68 vs 5.0 min | `team/E2/` |

Wave-1 roles **do not edit** `params/params.json`, any `subsystems/` file, or another role's folder. To test an
option, run your scripts on a scratch copy or with an in-script override, never by editing shared files. Put the
exact key edits you want in your report; A1 applies them.

## Do not run (any role)
- `proofs/build_graph.py`, `collision/`, `blender/`, `showcase/`, `manufacturing/make_shop_files.py`,
  `team/F2/harness.py`.
- git (no add, commit, stash or checkout).
- `params/CHANGE-LOG.md`, `STATUS.md`, `README.md`: do not edit.

## Engineering rules
- A fail closes only by a real design change, a corrected model with a stated reason, or a test that decides it.
  Never remove or loosen a limit to make a claim pass. If it cannot pass, say so and give the best option.
- Stay in your discipline. Where your fix needs another discipline (a motor cant moves the mount, a CG shift moves
  the pack), state the need with numbers as a request; A1 routes it.
- Weigh mass (grams against the gate), CG (`params.cg.x_range_m` [0.0394, 0.0513]), stiffness, cost (look prices
  up, cite URL and date), build hours.
- House rules (root `CLAUDE.md`): every number cites its source; estimates `EST`; unknowns "—"; reports follow
  `docs/reference/REVIEW-STYLE.md`.

## Report `review/DESIGN-ROUND-2026-11-14/<role>.md` (e.g. `C2.md`)
1. The fail, its cause, and the options evaluated (numbers, sources).
2. Recommended fix: exact params key edits, CAD changes for the designer (dimensions), mass, CG and cost effects.
3. Requests to other roles.
4. Claims it will move, with predicted before → after, and the scripts to re-run.
Decision ids are given by A1 when the brief is written (D-145 onward).
