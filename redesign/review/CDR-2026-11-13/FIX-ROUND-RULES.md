# CDR fix round, 2026-11-13: rules for every fix stream

Four streams work in the same checkout at the same time, plus the integrator, who owns the power-board CAD (CDR-17),
the harness, collision, blender, the assembly check and the proof-graph run.
The task list is `CDR-SUMMARY.md`. Each stream owns only the rows assigned to it.

| Stream | Rows | Owns these files (write only here) |
|---|---|---|
| S1 structures | CDR-01, -13, -18, -19, -27, -28 | `team/C1..C6/`, `team/D3/`, `team/D5/`, `team/D6/mech_calcs.py`, `team/H1/`, `subsystems/fins/`, `subsystems/landing/` (not `fusion/` of other subsystems) |
| S2 proofs + power models | CDR-03, -05, -29 | `proofs/` tooling, `PROOFS.md`, `team/E1/`, `team/E2/`, `team/B1/`, `team/F1/`, `team/F2/` claims scripts (not `team/F2/harness.py` geometry), `team/I2/` claims |
| S3 flight software + aero | CDR-07, -14, -15, -16, -26 | `subsystems/flight-software/`, `team/F4/`, `team/F5/`, `team/F3/` (not CAD), `team/B2/`, `team/B3/`, `team/B4/`, `team/A2/` |
| S4 BOM, mass, schedule, docs | CDR-09 (repo part), -10, -12, -20, -23 (docs not owned above), -24 | `team/I1/`, `team/I2/` schedule docs, `team/G1/`, `team/G3/`, `team/G4/`, `team/A1/`, `team/A3/`, `MASS-CG.md`, `STATUS.md`, `README.md`, `BUILD-GUIDE.md`, `team/D7/`, `subsystems/transport/` |

Shared files:
- `params/params.json` (and any `subsystems/*/params.json` you own): change only with a small exact Edit of the keys
  your rows need. Never rewrite the whole file from a script. Re-read the file just before each edit, because another
  stream may have changed it.
- `params/CHANGE-LOG.md`: **do not edit.** Write your decisions as change-log rows in
  `review/CDR-2026-11-13/fixes/<stream>.md`, in the CHANGE-LOG table format (Id `D-105`…: S1 uses D-105…D-114,
  S2 D-115…D-119, S3 D-120…D-129, S4 D-130…D-139). The integrator merges them.

Do not run:
- `proofs/build_graph.py`. Only S2 may run it, to test its tooling fix.
- `collision/`, `blender/`, `showcase/`, `manufacturing/make_shop_files.py` or `team/F2/harness.py`.
- git. Do not add, commit, stash or check out.

You may run your own team scripts and your own `subsystems/<x>/make_<x>.py` (S1: fins and landing), plus the read-only
checks `python -I redesign/fusion/check.py` and `python -I redesign/interfaces/merge_check.py`.

House rules (root `CLAUDE.md`): every number cites its source; estimates `EST`; unknowns "—"; reports follow
`docs/reference/REVIEW-STYLE.md`. Do not pick a side silently on a design conflict: decide and log it. The board
decisions B1, B4, B6, B7, B8, B9 are taken. B2, B3, B5, B10 and B11 need the students' sign-off: draft them as
PROPOSED and do not apply them as decided.

At the end, write `review/CDR-2026-11-13/fixes/<stream>.md` with three parts:
- The change-log rows.
- A table of the CDR rows you addressed: done / partly / not done, and why.
- The files you changed.
