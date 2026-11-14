# Change requests from agent 2 (interfaces / CAD framework)

| # | To | What | Why |
|---|---|---|---|
| CR-IF-01 | Integrator (`redesign/params/`) | Add `"frame"` to `params.json`: metres, x aft from nose datum, y right, z up (right-handed). Or state a different frame and agent 2 will adapt `fusionkit` docs. | All modules, interfaces `cg_xyz_m` and the viewer must share one frame. The old design used X fwd / Y up / Z right; do not mix. |
| CR-IF-02 | Integrator (`redesign/params/`) | Publish the mass budget as `redesign/params/mass_budget.json`: `{"limit_g": 7750, "allocations_g": {"<subsystem folder>": g, ...}, "cg_x_m": [lo, hi]}`. | `merge_check.py` / `check.py` compare the roll-up against it automatically. Fallback: first table in `MASS-CG.md` with a `subsystem` column and an `alloc` column, row `total` = limit. |
| CR-IF-03 | Integrator / all subsystem agents | Confirm subsystem folder names so `redesign/fusion/modules.txt` (build order) matches: currently `fuselage, wing, booms, tail, landing_gear, pusher, power, harness, avionics`. | Unlisted modules still build (last, WARN). |
| CR-IF-04 | Harness / power agents | Electrical parts carry `"electrical"` = `source` / `bus` / `sink`; every electrical edge carries the `wire` block and is registered with `ctx.wire()`. | Unpowered / unconnected checks and wiring-as-installation (ADVISOR-XV24-LESSONS). |
