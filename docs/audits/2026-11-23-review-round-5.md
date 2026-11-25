# Independent review, round 5 (2026-11-23), T-042 to T-045, HEAD c8ec35a5

Category: repository hygiene review. Reviewer reran cheap commands only. No tracked file changed (`git status --short` empty after `node review/build.mjs`).

## Reruns
- `python -I tools/ledger_audit.py`: 109 requirements, 93 tasks, 0 errors (now READY FOR REVIEW 4, as expected).
- `node --check` review/build.mjs, inventory/build_overview.mjs, inventory/build_variants.mjs: rc 0 each.
- `node review/build.mjs`: rc 0, "wrote templates.html 12 templates"; git status clean.
- Saved logs (`docs/audits/2026-11-23-T043-logs/`): proofs.txt has 16 STRICT lines; build_a.txt rc=1, only `graph:mass 1641 g > 1500 g`; wire.txt EXPOSED 0.597; bom.txt Total 1,939.17; ledger_audit.txt 0 errors. All match the s2 table.
- `git branch`: 14 branches, all removed-worktree branches present (build-film-audit, structures-d9x, claude/morph-chart-bc71a6, claude/proof-chain-readable-c5026d, 7 worktree-agent-*). `git worktree list`: main + ui-redesign-survey only. Matches s3/s10.
- `git show 8d15f419 --stat`: removed paths are exactly those listed (Inventory-Overview.html, cfd3d_viz.json, overview-full.png, site animation build/*, k09l-how-it-flies.mp4, poster.png, plus 52 sitl/runs BIN). No protected file (spec, .claude, ledger_audit.py) deleted; spec-integrity.sha256 and spec-amendments only appended. `git cat-file -e 8d15f419^:Inventory-Overview.html` succeeds: recoverable.
- `git ls-files '*.BIN'`: 3 (T076_data), matches s4. `git ls-files redesign/site/assets | grep -ci k09`: 0. `git ls-files | wc -l`: 15,281 matches s4.
- timing-T031-main.json: seconds_per_rendered_frame 1.94, rendered 6470, seconds 5298.4; 5298.4/6470 = 0.819 s matches s8.
- AM-002 and AM-029 present in docs/spec-amendments.md (lines 74 and 363) with the quoted text. Batch 1 approval ("approved, remove the two clean...") is a chat quote recorded only in repository-audit.md:44 and session-state.md:55, not in spec-amendments.md. Not independently checkable.

## T-042: PASS WITH FIXES
Every removal has an approval (batch 1 chat quote, batch 2 AM-002, batch 3 AM-029), branches kept, paths verified gone, doc labels appended without deleting content, script fixes small and correct (`fileURLToPath`, skip messages).
Findings:
1. LOW, docs/repository-audit.md:52: still says the dangling references are "open for T-042 / T-044 ... Not edited yet." They were fixed in 85ae8c0f. Fix: replace with "Fixed in T-042, see docs/audits/2026-11-23-T042-refs.md."
2. LOW, docs/repository-audit.md:35 and :39-40: "Batches 1 and 2 below" and "every removal now waits for Dillon's approval" are stale (batch 3 exists, approvals given). Fix: say batches 1 to 3 and that the 2026-11-18 block was cleared by AM-002 / AM-029.
3. LOW, docs/audits/2026-11-23-T042-refs.md:38-40 says the build_overview exit 1 is "Not fixed ... flag for T-044" while the conductor follow-up at :43 fixes it. Internally consistent only if read to the end; add "(fixed below)" at :40.
4. INFO: batch 1 approval has no spec-amendments entry (the chat answer was a user message but is quoted second-hand). No fix required; optionally append to spec-amendments.md by the conductor.

## T-043: PASS
Each value is either a command with `time` (logs saved in repo) or a quoted file with source and date; gate times are labelled "recorded, not re-run". Browser load time is honestly "—". Before/after: audit s8 states no speed baseline exists and claims no speed change; sizes only. No overclaim found.
Minor: LOW, docs/repository-audit.md:100 table says "recorded 2026-11-23" while the geometry-text change e0ee0017 postdates the gate run; disclosed in T-043 s3 note 3 and audit s12 item 5. No fix needed.

## T-044: PASS WITH FIXES
Reruns match the claims (all expected results reproduce). "All green" in the acceptance is satisfied only as "matches expected", since run_all rc 1 (12 FAIL + A-P13 UNVERIFIED) and build_a rc 1 are the standing design findings; the report says so.
Findings:
1. MEDIUM, spec 9.8 coverage: collide_a, assembly_check, drawings, Blender, CAD viewer load and Explorer in a browser were not re-run, so "CAD models still load / simulations still execute / video rendering still works" is not demonstrated after cleanup. Disclosed in docs/repository-audit.md:118 and T-043-T044.md:63, and the justification (cleanup touched no CAD/sim inputs; only SITL BIN and site copies were removed) is reasonable. Fix: either run `collide_a.py --glb` once at program end (T-049) or note in the ledger row that 9.8 simulation/render re-execution is deferred to T-049.
2. LOW, docs/repository-audit.md:112 "All PASS" is ambiguous; add "(expected FAIL counts match the standing baseline)".
3. LOW, docs/repository-audit.md:112 uses HEAD 85ae8c0f and :61 uses 76894339; harmless, state one.

## T-045: PASS WITH FIXES
All 12 spec 9.9 items are present with real content: baseline (s1), inventory (s1+s4), candidates (s2), removed (s3), consolidated (s5), dependencies (s6, honestly "none, not inventoried"), space (s7), benchmarks (s8), regression (s9), inefficiencies (s10), preserved (s11), risks (s12). The numbering offset (spec item order vs section numbers) is explained at lines 56-58 but is confusing: section s4 is not spec item 4.
Findings:
1. LOW, docs/repository-audit.md:54-58: heading numbering differs from spec order. Fix: add the spec item names to the s4-s12 headings, e.g. "### 5. Functionality consolidated (spec item 5)" for the later ones and note s2/s3 mapping once, or renumber to the spec order.
2. LOW, docs/repository-audit.md:78 and :81: s5 and s6 admit duplicate CAD pipelines/dependencies were not audited. Honest, but a "—" gap against spec 9.4; track it for T-049 (add to s12).
3. LOW, docs/repository-audit.md:92: "about 10.9 GB" sum mixes bases; labelled approximate. Acceptable.
4. Tracked-tree before/after (s4:64) is labelled "not a clean before/after". Honest.

## Overall
No protected file was removed, every removal is approved and recoverable, benchmarks are measured or sourced, before/after claims size only. No FAIL. Fixes above are documentation-only (T-042 items 1-3, T-044 items 1-3, T-045 items 1-2).

## Re-check of the fixes (conductor, 2026-11-23)
- repository-audit.md l.35 / l.40 / l.52: batches 1 to 3, approvals cleared (batch 1 chat, AM-002, AM-029), dangling references "Fixed in T-042 (85ae8c0f)". Applied.
- Headings s5-s12 carry "(spec item N)"; s4 already says spec item 2; the mapping paragraph stays.
- Spec 9.8 re-execution (collide / assembly / render / browser load after cleanup): recorded in the T-044 ledger evidence as deferred to T-049 (program-end audit) and the final 3-D gate run; cleanup touched no CAD, sim or render input.
- Batch 1 approval: quoted in the batch log only (it predates the amendments file for cleanup approvals); left as is, as the review allows.
