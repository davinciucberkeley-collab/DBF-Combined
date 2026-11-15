# Stream A notes (stopped 2026-11-14, before any edit)

The coordinator restructured the round, so stream A stopped during analysis. **No repo file was edited, no script was
re-run, no SITL or background job was started, and there are no scratch scripts.** Everything below was read from repo
files. The working numbers are hand calculations from those files and are marked `EST`. Paths are relative to
`redesign/`.

## 1. Baseline values read (sources)

| Claim | Value | Limit | Source |
|---|---|---|---|
| `CL-B3-HOVER-YAW-WTIP-20` | 1.318 | ≥ 1.5 | `team/B3/results/sc_results.json` `CALC-B3-HOVER-WTIP.ratio_20deg_5` |
| same, at 10° cant (`-CANT10`) | 1.693 | — | same file `ratio_20deg_5_cant10` |
| yaw control moment, 7° / 10° cant | 0.550 / 0.706 N·m | — | `M_ctrl_Nm`, `M_ctrl_Nm_cant10` |
| wing moment at 20°, 5 m/s | 0.417 N·m | — | `M_wing_20deg_5_Nm` |
| `CL-B3-TRANS-PITCH-USE` (hub at hover thrust) | 0.909 (forward CG, 11 m/s) | ≤ 0.60 (`ASM-B3-TRANS-USE-MAX`) | `CALC-B3-TRANSITION.use_cap30_max_hhov` |
| same, no hub term / hub at hover rpm | 0.83 / 0.867 | ≤ 0.60 | `use_cap30_max_nohub`, `_hmax` |
| same, target CG row (hub at hover thrust) | 0.80 at 10 m/s | ≤ 0.60 | `CALC-B3-TRANSITION.target` rows |
| pitch moment at the 30 % cap | 1.541 N·m | — | `m_cap30_Nm` |
| `CL-E2-CRUISE-TO-LOW-PESS-V17` | 4.676 min | ≥ 5.0 | `team/E2/claims.json` `CALC-E2-BUDGET-V17` |
| pessimistic cruise at 17 m/s | 406.0 W, 29.28 A | — | same (`cruise_w_pess`, `cruise_a_pess`) |
| `BATT_LOW_MAH` needed at 17 m/s | 2 700 mAh | — | same (`low_mah`); **`K09L.param` still has 2 600** (built for 16 m/s) |
| `CL-E1-ILIM-I` | 30.0 A winding | ≤ 25 A | `review/CDR-2026-11-13/fixes/S2.md` D-116 |
| pack limit that holds 25 A in the winding | 71.1 A, T/W 2.04 fresh | ≥ 2.0 | S2.md D-116 (`CL-E1-ILIM-FOR-25A`, `-25A-TW`) |
| `CL-B2R3-VTR-GATE-FWD` | 15.70 m/s | ≤ `performance.transition_min_ms` 15.6 | S3.md D-122 |

## 2. Findings and the options weighed, per claim

### Hover yaw with a wingtip into the wind (`-WTIP-20`)
- **Model.** Control moment = 4 · dT · (kq_iso · f_low + r · sin(cant)). Here dT is 30 % of hover thrust, r = hypot(y, z)
  = hypot(0.32, 0.19) = 0.372 m, and k_yaw_low = 0.0678 m at 7° (`team/B3/sc_analysis.py` l.853–899).
- **The 30 % differential cap cannot be raised for yaw.** The `R-HOVER-AUTHORITY` text in `team/A2/requirements.json`
  says: "the 30 % cap applies on every axis, yaw included". Cant is therefore the lever.
- **Cant needed for exactly 1.5** (`EST`, linear in sin(cant)). k needed = 0.0678 × 1.5 / 1.318 = 0.0772 m. That needs
  sin(cant) up by 0.0094 / 0.372 = 0.0253 over sin 7°, which gives **cant ≈ 8.5°**. 10° gives 1.69 (+13 %).
- **Cost of the cant.** Lift loss against 7° is 0.78 % at 10° (`CL-B3-CANT10-LIFT-LOSS`) and about 0.4 % at 8.5° (`EST`).
  Cruise thrust also loses a factor cos(cant), so 10° adds about 0.8 % to cruise power, which makes R-MISSION slightly
  worse. Mass: about 0 g.
- **Cross-owner work.** A cant change moves the fins mount CAD (stream F owns it, D3) and needs E1's blade-to-tube gap
  re-checked (26.1 mm at 7°, from CDR-AE-04).
- **Leaning:** 10° (D-127), for its margin. It must be written as a request to stream F with the wedge angle.

### Transition pitch use (`-TRANS-PITCH-USE`)
- **Worst point:** forward CG, 10–11 m/s, alpha 37–43°. The needed moment is |M_aero| 1.27–1.28 N·m plus a hub term
  0.12–0.13 N·m, against a 30 % cap of 1.54 N·m.
- **The 0.60 limit applies on top of the 30 % cap.** This keeps 40 % of the differential for rate, gusts and mixing.
  It is not a double count, so it must not be relaxed.
- **Levers evaluated** (`EST`, scaling the denominator):
  - Allowing 40 % differential in transition (as D-128 does for the gust): 0.909 × 0.75 = 0.68. Fails.
  - 40 % with the Ribner-only term: 0.83 × 0.75 = 0.62. Fails.
  - Target CG instead of forward CG, at 40 %: 0.80 × 0.75 = 0.60. Zero margin.
  - Allowing 45 %: 0.61. Allowing 50 %: 0.55.
  - Motor spacing z: would need ×1.52 (0.19 → 0.29 m). Not feasible; z is set by the fin geometry.
- **Elevon credit at alpha 43°.** It is post-stall and was excluded by CDR-AE-07, so it is not credited.
- **Not done:** a time-domain pitch-over model, which CDR-AE-07 and S3 both said was missing. Because the quasi-steady
  level case is the bound, only that model, SITL stage B, or the twin's logged RCOU split can close this claim honestly.
- **Leaning:** state that it cannot close on paper. The best option is a transition differential cap with stated
  reasoning (yaw demand is small in transition), together with the time-domain model and SITL S5. No result yet.

### Transition gate at forward CG (`-VTR-GATE-FWD`)
- The aircraft flies `AIRSPEED_MIN` 17 (D-122, tripped stall 12.94 m/s; 1.3 Vs = 16.82 ≤ 17, `CL-F4-ARSPD-MIN-TRIP`).
  The key `performance.transition_min_ms` 15.6 is stale: its source is `CL-B3-VT-TRIM`.
- **Fix (design speed, not a looser limit):** set `performance.transition_min_ms` to 17. The claim is
  `team/B2/sim/sim_claims.py` l.275, and `team/F4/fsw_check.py` l.490 reads it.
- **Required with it:** `R-TRANSITION` says "≤ cruise {P:performance.cruise_ms}", so `performance.cruise_ms` must also
  go 16 → 17. That matches `AIRSPEED_CRUISE` 17 already in `K09L.param`.
- **Ripple.** About 23 scripts read these keys. The grep list includes A1 `frame_claims.py`, B1, B2, B3, B4, C1, D6, E1,
  E2, E3, F1, F3, F4 and J1.
- **Open:** key ownership. `performance.*` was treated as A1's in the CDR fix round (S2, S3), but these two keys cite
  B3 and B1 sources.

### Mission at 17 m/s (`-CRUISE-TO-LOW-PESS-V17`)
- **Arithmetic.** to_low = (6.5 − 2.7 − 1.518 Ah used before cruise) / 29.28 A × 60 = 4.68 min.
- **What 5.0 min needs:** pessimistic cruise current ≤ 27.4 A (−6.5 %), or +0.16 Ah.
- **Option: 11×5.5E / EP pair.** It exists as a matched pair (B4 `PROPS.md` §1 and §9).
  - Cruise at 17 m/s ×0.909 (`CL-B4-AB-CRUISE-RATIO-E-17`); hover +0.3 %.
  - Hand calculation (`EST`): 369 W → 26.4 A. `low_mah` stays 2 700, giving **about 5.17 min (+3 %)**.
  - Costs: +24 g (4 × 6 g, which takes the gate margin from +98 g to +74 g) and the price difference (EP price not
    looked up: —).
  - Not yet checked: E1 full-throttle T/W and the limiter with this prop.
- **Option: 11×7E.** −23 % cruise power, but **no 11×7EP exists** (APC product page 404, checked by S3 2026-11-13). It
  cannot fly as a quad set.
- **Rejected:**
  - A slower cruise: below `AIRSPEED_MIN` 17, so it would hide the fail.
  - A shorter `BATT_LOW` return leg: 60 s is in the model, and `FENCE_RADIUS` is 250 m (about 15 s at 17 m/s).
    Shortening the leg would loosen a reserve.
  - A bigger pack: mass, since the 4S 8000 is 0.70 kg `EST`.
  - Li-ion 4S2P 9 Ah: 0.62 kg `EST`, and 90 A continuous only works with a 71 A limiter. Too large a change.
- **Separate finding:** `BATT_LOW_MAH` in `K09L.param` should be 2 700 for a 17 m/s cruise (`CL-E2-BATT-LOW-MAH-V17`).

### Winding current (`CL-E1-ILIM-I`)
- **Fix candidate:** `Q_M_BAT_CURR_MAX` 100 → 71 (or 70). F4 owns `K09L.param`, and `performance.full_throttle_current_a`
  would follow.
- **Effect** (S2): 25 A in the winding, T/W 2.04 fresh against 2.0 (+2 %).
- **Still to check with an E1 re-run:**
  - the worst-state T/W of 1.6 at the lower limiter;
  - the second bound;
  - gust headroom of 1.3;
  - transition thrust (`CL-B1-TRANS-THRUST`);
  - the `R-ESC-CURRENT` text, which quotes 100 A and 24.8 A.
- An 11×5.5E prop would change these numbers too.

## 3. Requests that would have been made (not sent)
- **Stream F (D3 mount):** cant 7° → 10° wedge, if D-127 is adopted. **E1:** re-check the blade gap.
- **Integrator / A1:** `performance.transition_min_ms` 17 and `performance.cruise_ms` 17, then the re-run chain.
- **CG:** none yet. The target-CG transition case needs no CG change.

## 4. Sources
Only repo files were read. No web lookups were made this session; no URLs were checked.
