# Closure round: work rules for each role

Read `RULES.md` (this folder) and `A2.md` (requirement re-derivation, accepted by A1 as **D-160**, applied to
`params/params.json` on 2026-11-14: cruise 3.5 min, hover 3.0 min total incl. a 40 s go-around
(`requirements.goaround_hover_s`), crash reserve $130, first hover week 6 / 35 days cut-to-hover).

Failing claims at the start of the round: `proofs/out/graph.json` (2026-11-14 23:26 UTC). Each role closes its own.

| How a claim may close | Allowed |
|---|---|
| Design change in your discipline (with numbers; geometry via the D-role that owns the subsystem) | yes |
| Corrected model, with the reason stated (and the before → after) | yes |
| Re-derived **derived** limit (A2 basis, A1 accepts) | via A2 / A1 only |
| A claim about an option that is **not in the design** (rejected alternative) or a sensitivity row: re-class as information (no limit) with the reason, or delete it | yes, list each one in your report; J6 reviews |
| Loosen a physical limit, or leave a test-gated hold point as the "fix" | **no** |

If a test decides a value, design so that the claim passes at the pessimistic end of the test's range today, and keep
the test as confirmation.

Edit only your own `team/<role>/` folder (design roles: also their own `subsystems/<name>/`). Run your own scripts
(they rewrite your own `claims.json`). Do not run `fusion/check.py`, `merge_check.py`, `proofs/build_graph.py`,
`collision/`, `blender/`, `showcase/`, `make_shop_files.py`, another role's scripts, or git. `params/params.json`:
request edits from A1 in your report (key, old → new, note text). FE / sim jobs ≤ 4 threads.

Report `review/CLOSURE-ROUND-2026-11-14/<role>.md`: (1) each failing claim, its cause, the fix; (2) scripts run and
the PASS / FAIL lines; (3) before → after against the limit; (4) requests to A1 and other roles (exact numbers).
