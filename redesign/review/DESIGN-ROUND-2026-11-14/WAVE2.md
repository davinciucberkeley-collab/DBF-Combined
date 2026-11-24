# Design round 2026-11-14: wave-2 rules

A1 applied the `params/params.json` edits for D-145 … D-155 on 2026-11-14 (see `A1.md` §1 and the notes on each key,
which start "D-14x (Design round 2026-11-14"). Wave 2 draws and sets what `A1.md` §3 says, **one role per agent**
(`TEAM.md`). `RULES.md` still applies, with these changes:

| | Wave 1 | Wave 2 |
|---|---|---|
| May edit | own `team/<role>/` | own `team/<role>/` **plus** the subsystem the role owns in `TEAM.md` (`subsystems/<name>/`), and only for the brief |
| `params/params.json` | no | **no**. Request any further key edit in your report; A1 applies it |
| Generators | none | your own subsystem generator and self-check only |

## Do not run (any role)
- `fusion/check.py`, `merge_check.py`, `proofs/build_graph.py`, `collision/`, `blender/`, `showcase/`,
  `manufacturing/make_shop_files.py`, `team/F2/harness.py`. A1 runs the shared gates after wave 2, in one pass, so two
  roles never write `interfaces/` or `proofs/out/` at the same time.
- git (no add, commit, stash, checkout).
- `params/CHANGE-LOG.md`, `STATUS.md`, `README.md`.
- Heavy FE jobs: one at a time per role, `-j` / thread count ≤ 4. Other roles run FE at the same time.
- Do not write large outputs into the repo outside a git-ignored folder (`team/C2/fea/out/c2r5/` is the example: do not
  add to it).

## Report `review/DESIGN-ROUND-2026-11-14/<role>-W2.md`
1. What you changed (files, keys, dimensions), with the decision id.
2. Self-checks run and their result (command and the PASS / FAIL line).
3. Claims moved: before → after, against the limit.
4. Requests to A1 or other roles (exact keys and values), and anything you could not close.

House rules from the root `CLAUDE.md`: every number cites its source; estimates `EST`; unknowns "—"; follow
`docs/reference/REVIEW-STYLE.md`. Never loosen a limit to pass.
