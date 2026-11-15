# Closure round, 2026-11-14: rules (one agent per TEAM.md role)

Goal set by the user (Dillon, 2026-11-14): **the finalized design has zero failing claims.**
The user's only constraints are the hard constraints in the root `CLAUDE.md`:

| User constraint | Value |
|---|---|
| Budget | $2,000 total physical (Jacobs Makers Pass outside) |
| Schedule | built and flight-tested by end of April 2027 |
| Portability | team of 4 moves it; < 25 kg; one piece in a box that fits a standard car |
| 3-D physics | every build step and the assembly pass the 3-D physics check (no interpenetration, no open wire ends, no exemptions); the 3-D flight / landing sims pass |
| Configuration | K09-L quad tailsitter (team decision 2026-11-13) |

Everything else (mass gate 2.6 kg, 2 min hover + 5 min cruise, 20 % reserve, build overrun line, P1–P25 in
`config-study/REQUIREMENTS-PROPOSED.md`, A2 `REQUIREMENTS.md` rows) was proposed by the agents. The team **may re-set a
derived requirement**, but only by re-deriving it from the user constraints and physics, with the basis written out.

## Engineering rules
- A fail closes only by: a real design change; a corrected model with a stated reason; a test that decides it (the
  claim then stays a test-gated hold point, and that is **not** allowed at the end of this round — find a design that
  passes with the test as confirmation); or a re-derived requirement (A2, basis written, A1 accepts).
- Physical limits stay real limits: stress and margins of safety, T/W for control, current and temperature ratings,
  stall margin, clearances, vibration separation, 3-D physics. Never loosen these to pass.
- A derived target that has no physical or user basis (for example a cruise time picked as a demonstrator assumption)
  may be re-derived from what the flight-test programme actually needs.
- House rules (root `CLAUDE.md`): every number cites its source; estimates `EST`; unknowns "—"; reports follow
  `docs/reference/REVIEW-STYLE.md`.

## Process
Same as `review/DESIGN-ROUND-2026-11-14/RULES.md` and `WAVE2.md`: each role edits its own `team/<role>/` folder (and in
the design wave its own subsystem), never `params/params.json` (requests go to A1), never runs `fusion/check.py`,
`merge_check.py`, `proofs/build_graph.py`, `collision/`, `blender/`, `showcase/`, `make_shop_files.py`,
`team/F2/harness.py` or git. FE jobs ≤ 4 threads, one at a time per role.

Reports: `review/CLOSURE-ROUND-2026-11-14/<role>.md`.
