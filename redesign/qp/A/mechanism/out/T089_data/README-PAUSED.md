# T-089 paused 2026-11-22 (AM-026: "Reach a good place to pause for later resumption")

The T-089 implementer was stopped before its report. Nothing here is reviewed.
- Partial edit of `sitl/fu_cage.py` (config switch for the X2216 / current plant, mid-refactor) saved as
  `t089_partial.patch` and `fu_cage_post_t089_partial.py`; the working tree was reverted to HEAD. The partial edit
  is incomplete (stopped while refactoring the cases): review before reuse.
- Done: backups `*_pre_t089.*`; `run_all_before_stdout.txt`; `t089_gm.py` (plant constants printed: TFULL 14.168 N
  per motor, KQ_SHAFT 0.0145 m, yaw arm 0.0953 m); `t089_fvib.py` regression only: the spar-only sweep reproduces
  structures_run.md s4 (worst 26.5 / 23.7 / 22.7 m/s2 kd / nom / hi). The upgraded-model forced response and the
  gain margins are NOT computed yet.
- To do: finish fu_cage config, gm_nominal / gm_shifted / gm_shifted_up at the corners (D-191 method, limits
  unchanged), forced response of the 94.6-108.7 Hz mode at FC and motors on the T-085 model, re-point params,
  run_all, `T089_report.md` + D-237.
