# Stream P notes (stopped 2026-11-14, before any edit)

Stopped by the coordinator before any design change. No repo file was edited. No scratch script was written. No
background job was started. No prices were looked up, so this file cites no URLs.

## 1. R-PACK-RETENTION: what the three fails are

### `CL-C3-BLOCK-A-SHARE` 0.43 vs ≤ 0.10 and `CL-C3-STOP-SECTION-PENALTY` 6.2 mm vs ≤ 1 mm: stale model input
- `team/C3/pod_structures.py` `CALC-C3-NOSE-PATH` reads `ASM-C3-D47-NOSE` = [-0.1212, 0.0088]. That is the D-47
  forward-stop aft face, hard-coded.
- D-62 (`params/CHANGE-LOG.md`) moved the nose to -0.140 and the forward stop to -0.1312. The C3 assumption was
  never updated.
- Result now (`team/C3/out/results.json`): L_A = (-0.1212 - 0.003) - (-0.140 + 0.0048) = 11.0 mm, which is wrong.
  The pod params say `nose_block_l_m` 0.001. The model therefore credits block A with 11 mm of XPS. That XPS does
  not exist: D-47 deleted block A, and D2-R5 made it a 1 mm epoxy bond line (CR-C3-08).
- The correct L_A at D-62 is (-0.1312 - 0.003) - (-0.1352) = 1.0 mm. The shares and penalties scale linearly with
  L_A:
  - block A share 0.4306 × 1/11 = **0.039** (≤ 0.10, passes);
  - stop-section penalty 6.17 × 1/11 = **0.56 mm** (≤ 1 mm, passes).
  These match the values recorded in `team/C3/SUMMARY.md` (0.041, 0.56).
- Proposed fix (model correction, no limit change): derive the stop aft face from `pod.x_le_m` + `fins.board_t_m`
  + `nose_block_l_m` + `fwd_stop_m[0]` (`subsystems/pod/params.json`). Do not use the hard-coded D-47 value.
  - Owner: `team/C3/` (stream P, or its successor role).
  - Re-run: `pod_structures.py`.
  - Not done.

### `CL-C5-PACK-STACK-MARGIN` -3.3 mm vs ≥ 0: real conflict, not stale
- `team/C5/landing_calc.py` `CALC-C5-CRASH`: stack margin = blk_min - (8.8 mm + gap_B needed).
  - blk_min = `ASM-A3-NOSE-STACK` 34.6 mm (`team/A3/mass_rollup.py`, an integrator file). It is built on a 24.3 mm
    block.
  - 24.3 mm = v²/(2 · 100 g · eff), with eff = 0.55 - 0.05/2 = 0.525. That is the ideal length only if the block
    crushes at exactly the 100 g pack limit. It was also the retired 503 g pack's length (`team/C5/LANDING.md`,
    CR-C5-21).
- F-250 over the bay section caps the force at σA = 172 kPa × 2.959e-3 m² = 509 N.
  - The 590 g pack then needs block B 27.6 mm + 1.5 mm spreader = 29.1 mm.
  - Margin = 34.6 - 8.8 - 29.1 = **-3.3 mm**.
  - Per pack, block B needs 25.5 / 25.8 / 27.6 mm (546 / 551 / 590 g).
  - The most forward safe centroid is -0.0367 / -0.0364 / -0.0346 (`CL-C5-PACK-X-FWD-MAX-*`).
- **A hidden real fail.** A3's live roll-up (`team/A3/rollup/rollup.json` `cg.station_cases`) flies **all three
  packs at -0.036**, using `pack_x_fwd_limit_m` -0.0379.
  - The 590 g pack at -0.036 is 1.4 mm ahead of its block-B limit (-0.0346).
  - C5's margins pass only because C5 reads D2's older stations: `pack_x_per_pack_m` 546 -0.036 / 550 -0.034 /
    590 -0.030.
- The CG is tight at the aft end (`rollup.json`):
  - the aft margins at -0.036 are -0.07 mm (546 g), +0.10 mm (551 g) and +1.44 mm (590 g);
  - CG moves 0.231 mm per mm of pack.
  - Moving the light packs aft to -0.034 to satisfy a uniform 37.9 mm stack would push the CG about 0.46 mm past
    the aft limit (0.0513).

Options evaluated (on paper only, nothing changed):
1. **Stiffer block, one size for all packs (F-400, 276 kPa, already bought for the D-76 cartridges).**
   - Over the full section: 816 N, which is 141–152 g on the pack. That fails the 100 g limit.
   - Section cut to keep the 546 g pack at ≤ 100 g gives F ≤ 535 N. The 590 g pack then needs 26.2 mm, and the
     stack margin is -1.9 mm.
   - Rejected: no single block can hold both packs, because L_590 ≥ 24.27 × 590/546 = 26.2 mm.
2. **Section or material cut per pack, so each pack's block sits at 100 g.**
   - Length 24.3 mm for each pack, so the margin is about 0.
   - It sits exactly on the G limit, and the ±10 % plateau uncertainty breaks it. Rejected.
3. **Drop the 3 mm forward stop.** Gains 3 mm, still -0.3 mm short, and loses the D-69 T-stop structure (C3 FEA).
   Rejected.
4. **Use the 564.4 g acceptance line (`mass.pack_accept_g`) instead of the 590 g bound.** Still -2.1 mm. It would
   also weaken a load case. Rejected.
5. **Recommended (not done): a real nose-stack change.**
   - Block-B minimum 24.3 → 27.6 mm (cut 28). The stack becomes 8.8 + 28 + 1.5 = 38.3 mm.
   - Pod nose and the whole bay move 4 mm forward: `pod.x_le_m` -0.140 → -0.144, `pod.size_m[0]` 0.235 → 0.239,
     forward stop -0.1312 → -0.1352.
   - The most forward centroid, with the block sized for the 590 g pack, becomes -0.144 + 0.0383 + 0.0675 =
     -0.0382. That is 0.3 mm more forward room than today's -0.0379, with every pack's block long enough.
     Stations unchanged.
   - Stack margin = 38.3 - 8.8 - 29.1 = **+0.4 mm**.
   - Cost, all `EST`:
     - mass about +1–2 g (4 mm of foam-board shell around a 0.42 m perimeter, plus 3.7 mm of F-250 block about
       0.3 g); weigh in CAD;
     - shell mass moves slightly forward, which helps the aft-tight CG;
     - box x slack falls from 17 to 13 mm (`transport.envelope_props_off_m` note);
     - hatch about 4 mm longer (re-check the C3 hatch suction and the D-143/144 latch-tab clearance);
     - antenna tube B tip rule ≥ -0.150 (`ant_b_tip_min_x_m`) must be re-checked;
     - pitot tip -0.220 → -0.224, or a 4 mm shorter boom.
   - Needs: integrator edits to `ASM-A3-NOSE-STACK` (34.6 → 38.3 mm), `transport.envelope_props_off_m`, the
     pitot tip and the D7 nose pad. C5 should read the stack from a pod-owned key, not from A3's copy. Price of
     the F-250 offcut: — (not looked up).

## 2. R-WIND broadside: `CL-C5-SIM3D-V-BROADSIDE` 4.5 vs 5.0 m/s

- Source: `team/C5/sim/out/sim3d.json` (landing_sim3d.py, run 928 s).
  - Limits: broadside lull 0.5 / 1.2 = 4.5 m/s, steady 0.5 = 4.5, steady 1.2 = 5.0; spanwise 8.5–10.
  - The claim takes the minimum of the two lull cases (`landing_sim_claims.py` line 89).
- The tip starts at a touchdown tilt of 26.98° (lean at 5 m/s about 17° + 10° error). At 4.5 m/s it is about 24°
  and holds.
- Inputs:
  - CG: x 0.049, z 0.018, height above the ground 0.368 - 0.049 = 0.319 m;
  - pads: z_outer 0.219, pad 19.1 × 17.8 mm, y_fin 0.32;
  - μ 0.40, drift 0.3 m/s, λ 0.667, m 2.409 kg, Cd90 1.28, S_b = 1.15 × 0.32 m².
  - The lean toward +z (pod side) has a lever of 0.219 - 0.018 = 0.20 m. Static tip angle atan(0.20/0.319) =
    32°; the dynamic threshold is about 25–27°.
  - The -z side has 0.237 m of lever, and the sim does not check it.
- Options identified, none simulated yet:
  - (a) **Wider stance in z.** An outboard pad toe on the feet raises `landing.pad.z_outer_m` (D5-owned,
    `subsystems/landing/params.json`). Estimate: +12–15 mm of lever for about +2–3° of tip angle.
    - Constraint: the props-off envelope z is 0.438 and the box is 0.54 high with a 77 mm height slack
      (`transport.envelope_props_off_m` note). Some room, but the D7 cradle and drop travel must be re-checked.
    - The geometry is symmetric in `landing_sim3d.py` `geometry()`. The +z feet alone would need an asymmetric
      pad model.
  - (b) **Lower pad μ** (UHMW face, μ < 0.40 is inside the D-105 cap). Smaller trip moment. The parked-gust claim
    already has no limit (D-105). Untested in the sim.
  - (c) **Procedure (stream A / F4).** Lower the touchdown drift `ASM-C5-TD-DRIFT` (0.3 m/s), or level the
    attitude before touchdown. Needs a request to flight software.
  - (d) Existing mitigation: rule S1, land wingtip into the wind (CR-C5-05).
- Plan not run: a scratch script that imports `landing_sim3d.simulate()` and runs only the broadside cases (V
  4–6 m/s) with z_outer +10 / +20 mm, μ 0.25 / 0.30, drift 0.15 m/s. About 100 cases at 2 s, a few minutes each.

## 3. Facts checked, for re-use
- `subsystems/pod/params.json`: `nose_block_l_m` 0.001, `fwd_stop_m` [0.003, 0.025, 0.054],
  `pack_x_per_pack_m` {546: -0.036, 550: -0.034, 590: -0.030}, `latch_tab_m` [0.008, 0.06],
  `block_top_clear_m` 0.003.
- `params/params.json`: `pod.x_le_m` -0.140, `pod.size_m` [0.235, 0.14, 0.07], `cg.x_range_m`
  [0.0394, 0.0513], `fins.board_t_m` 0.0048, box [1.25, 0.56, 0.54], envelope [1.152, 0.508, 0.438].
- Mass (`team/A3/rollup/rollup.json`): predicted 2 501.6 g; gate margin +98.4 g (550 g pack), +58.4 g (590 g
  pack).
