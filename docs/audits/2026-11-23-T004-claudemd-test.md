# T-004 CLAUDE.md cold-read test (2026-11-23)

Method: a fresh session read only the project-root `CLAUDE.md` (Read tool, full file, 108 lines), answered from it alone,
then opened `docs/session-state.md` to compare. No other file was edited.

**`wc -c CLAUDE.md` = 7402 bytes.**

## Answers from CLAUDE.md alone

1. **Canonical spec.** `docs/MASTER_PROJECT_SPEC.md`. May: read it (required at milestones, after compaction, before final
   verification). May not: edit, summarise, or delete it (verbatim). Amendments are kept separately (see 2).
2. **Later user instructions.** Verbatim, append-only, into `docs/spec-amendments.md`.
3. **Recovery after compaction, restart or handoff.** Follow the "Recovery procedure" in `docs/session-state.md` before any
   work. A compaction summary is not authoritative. Also read the full spec at that point and before final verification.
   `python -I tools/ledger_audit.py` must pass.
4. **Communication.**
   - Work quietly: no narration of routine actions, no restating plan or ledger, no long progress summaries. Decide within
     permissions instead of asking.
   - Message the user only for: a direct question (answer fully), a milestone (1–3 sentences), a critical engineering issue,
     a decision or authorisation only the user can give, a real blocker, a significant failure, or project end. Never pause
     execution just to report.
   - Subagents return one line: `Task ID | Outcome | Verification | Evidence path | Blocker`; details go in files.
   - Brevity never reduces the work (tests, docs, warnings, error reports stay complete).
   - AM-028: do not ask "continue?" between steps; move to the next queue item. CLAUDE.md gives only the summary and points to
     `docs/spec-amendments.md` for the full text.
   - AM-030: no new test equipment. CLAUDE.md gives only the summary (the amendment itself is not reproduced here).
5. **Hard constraints.**
   - Budget: $2,000 total physical (hardware, spares, batteries, test gear, shipping, tax). Makers Pass paid outside it.
   - Schedule: built and flight-tested by end of April 2027.
   - Transport: a team of 4 moves it routinely; hard cap under 25 kg (55 lb); packed aircraft must fit one standard car
     trunk, two at most; need not travel in one piece.
   - 3-D gates: every build step and the assembled aircraft pass `redesign/showcase/animation/assembly_check.py` and
     `redesign/collision/collide.py --glb`, with no interpenetration, no open wire ends, no exemptions. Flight cases in the
     3-D sims (C5 landing, SITL) pass against their limits.
   - CAD fidelity: every part modelled to real shape and dimensions from vendor drawing or data sheet; no stand-in disks or
     boxes; unknown dimensions are stated and marked, never invented.
   - Wiring: wires inside arm tubes, wing-core channels, fairings or covers. Any exposed wire is listed with length and reason,
     kept to the minimum.
   - Engineering agents (`redesign/TEAM.md`) make design decisions within these constraints and log each in
     `redesign/params/CHANGE-LOG.md`.
6. **Commit attribution.** Credit the person working with `git commit --author "<Name> <email>"`; use `Co-Authored-By: <Name>
   <email>` trailers for joint work. Use the GitHub no-reply emails in the table (never personal addresses). If the person is
   not known, ask who is working or use the name they give.
7. **Unclear or contradictory items in CLAUDE.md.** See the list below.

## Unclear or contradictory items in CLAUDE.md

- **Stale configuration presented as current (contradiction).** Lines 28-31 say concept A continues as O4b with SunnySky
  X2216 880KV motors and a 2,800 mAh pack. Lines 37-38 (the 2026-11-14 paragraph) still say "T-Motor MN2212 KV780 on 4S,
  4S 2000 mAh packs" and "about 1.23 kg". Nothing marks lines 36-40 as superseded. A cold reader cannot tell which motor is
  current. Session-state confirms X2216 (and AM-017 found MN2212 infeasible).
- **Section placement.** The AM-008 paragraph (line 26) and the D-182 paragraph (line 33) sit under the "## Communication
  (AM-001)" heading, so they read as communication rules. Their own heading is missing.
- **Mass gate not stated.** CLAUDE.md says "mass gate missed" (line 31) but never gives the current concept-A gate. The only
  number is K09-L's 2.6 kg (line 42). Session-state gives "mass gate 1.5 kg". The hard constraints list only the 25 kg cap.
- **Budget reserve undefined.** Budget line (45) lists categories but not the crash reserve. Session-state says the budget is
  "total incl. crash reserve by its definition <= $2,000 (AM-013, AM-018)" and that the reserve is defined in
  `T082_data/bom_t082.py`. CLAUDE.md does not point to that definition.
- **Amendment reading on recovery.** CLAUDE.md (line 4-5) says where amendments go but not that they must be read on recovery.
  Session-state step 3 says to read all amendments, and the amendment named in each requirements.md row.
- **Rule text versus amendment text.** AM-028 and AM-030 appear only as one-line glosses ("no 'continue?' prompts",
  "no new test equipment"). The full wording is in `docs/spec-amendments.md`. The gloss for AM-030 does not show its
  "continue every doable task" half, which session-state records.
- **Commit attribution gap.** The team rules name only team members. They do not say whether an AI co-author trailer is
  allowed or required alongside a team trailer, nor what to use when the user gives no name. The session's git identity and
  the attribution the session reminder asks for are not addressed by CLAUDE.md.
- **"Ask who is working."** Working rules say to ask, but Communication (line 18) says decide within permissions instead of
  asking. Not a hard contradiction, but a reader has to pick one.
- **Stale pointers.** Lines 74-76 say the root `analysis/` + `cad/` are the 11-02 resize while `inventory/`, `fusion/`,
  `concepts/variants/` are on v0.3.1. Those statements predate the O4b configuration and no current status is given.
- **Subagent return format.** Line 22 says `Task ID | Outcome | Verification | Evidence path | Blocker` with no labels. The
  format in the launching brief uses `Task: T-nnn | Outcome: ...`. Both are one line, but CLAUDE.md does not say which.
- **Undefined terms.** "C5", "SITL", "O4b", "D-" and "AM-" IDs, "R-ids", "VERIFIED COMPLETE" are used without definitions in
  CLAUDE.md. They are defined elsewhere (ledger, spec, decisions).

## Cross-check: `docs/session-state.md`

Opened and read in full. **No direct contradiction with CLAUDE.md found.** Specific checks:

- Recovery order: session-state step 1 is "Project-root CLAUDE.md"; CLAUDE.md names the same procedure. Consistent.
- Compaction summary not authoritative: both say so. Consistent.
- Full spec read at milestones, after compaction, before final verification: both say so. Consistent.
- `python -I tools/ledger_audit.py` must pass: CLAUDE.md requires it; session-state records "0 errors". Consistent.
- Spec and amendments path and append-only rule: consistent. Session-state adds that `tools/spec_guard.py` does not exist and
  the seal check is `tools/ledger_audit.py`. CLAUDE.md does not mention `spec_guard.py`, so no conflict.
- AM-028 and AM-030 as standing rules: both documents agree (session-state adds detail).
- Concept A configuration: session-state gives X2216, 9x4.5 props, and O4b, which matches CLAUDE.md lines 28-31 but not lines
  37-38 (MN2212, 2000 mAh). This is the stale-text issue noted above; session-state is the more current source.
- Budget: both say $2,000. Session-state adds the reserve definition and BOM $1,939.17 (CLAUDE.md agrees on the BOM).
- Mass: CLAUDE.md 1.881 kg EST and session-state 1.881 kg agree. The gate value differs only by omission (see above).
- Wiring, CAD fidelity, transport, 3-D gates: session-state does not restate them, so nothing to contradict.
- Session-state "Inspection (R-PRES-13): CLAUDE.md kept whole; no AGENTS.md": consistent with this file being present.

## Blocker

None for this test. Items above are documentation gaps; none stops the next action. Recommend the user or lead decide
whether to mark lines 36-40 as superseded and to define the amendment-reading and attribution rules. This audit does not edit
CLAUDE.md.

## Conductor follow-up (2026-11-23)
The one gap found (MN2212 / 2000 mAh paragraph without a supersession marker) is fixed: its heading now reads "History (superseded by the O4b status above)". All seven items were answered from CLAUDE.md alone; no contradiction with session-state.md.
