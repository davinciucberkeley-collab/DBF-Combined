# Change requests from A2 (systems engineer)

Status of rounds 1 and 2, then the round-3 requests from resolving CR-A1-37 (2026-11-09, A2-R2). Numbers quoted are
from `proofs/out/graph.json` at the A2-R2 build; the matrix is the live view.

## Rounds 1–2 — status

| # | To | Disposition (CHANGE-LOG) | A2 side |
|---|---|---|---|
| CR-A2-01 | A1 | accept, D-14 | done: 38 of 39 `ASM-A2-…` retired; one alias left while B2 cites it (CR-A2-16) |
| CR-A2-02, -03, -07, -09 | A1, B1/B2, C1 | closed | closed |
| CR-A2-04 | A3 | forward | done by A3 |
| CR-A2-05 | A4 | forward | half: `R-JOINT-STACK` now has six C6/D3 claims (+2 %); `R-NO-FLOATING` still has none |
| CR-A2-06 | J1 | forward | done, but `CL-J1-TUBE-MODE-SEP` (−91 %) is superseded by C4's `CL-C4-D3-SEP` (D-45) and still fails `R-VIBRATION`: CR-A2-23 |
| CR-A2-08 | F1 | closed by D-32 (AS150U) | closed; J1's XT60 claims still verify `R-DISCONNECT` (−50 %): CR-A2-23 |
| CR-A2-10 | H1, H2, H3 | forward | H1 has `GROUND-TEST-PLAN.md`, `claims.json`, `logs/`; the matrix now uses H1's names (CR-H1-07); no H2 or H3 folder yet |
| CR-A2-11 | J2 | forward, optional | open |
| CR-A2-12 | A1 | accept, D-34 | done: `R-TRANSPORT` text at D-31, `propulsion.motor_max_a` / `esc_burst_a` added and now read by `R-ESC-CURRENT`; CR-A1-17 closed |
| CR-A2-13 | E1 | forward | open: `CL-E1-IMAX-148/-168/-168-55/-148-55` still test the old typed 36 / 45 A (−1 to −18 %); `R-ESC-CURRENT` fails for that reason only |
| CR-A2-14 | F4, H1 | forward | open: no F4 `Q_M_BAT_CURR_MAX` claim, no H1 restrained-run test node (CR-A2-25) |
| CR-A2-15 | A3 | forward | open: `CL-A3-HOVER-SPLIT` 1.19 still has no `verifies`; `R-HOVER-SPLIT` has no claim (CR-A2-26) |
| CR-A2-16 | B2 | forward | open: `wing_claims.py` line 103 still cites `ASM-A2-SERVO-TORQUE-FACTOR`; the alias stays until then |
| CR-A2-17 | E2 | forward | done: alias gone |
| CR-A2-18 | D7, C1 | forward, D-31 | nearly: `CL-D7-A1-BOX-DROP-ALLOW` 0.291 vs 0.3 m (−3 %) at the 0.54 m box; `CL-D7-TUBE-CLEAR-DROP` 1.8 mm vs `trn.foam.travel_margin_m` (−82 %) is D7's own |
| CR-A2-19 | B3, A5 | forward | open: `CL-A5-LAYOUT-CG-X` 0.0531 m still tested against A5's 0.049 m (−8 %); `cg.x_range_m` is 0.050–0.055 |

## Round 3 — new (CR-A1-37)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-A2-20 | A1 | (a) Paste the R3 wordings into `params/claims.json` for `R-MASS-GATE`, `R-TIPOVER` and `R-DISCONNECT` (exact text: `REQUIREMENTS.md` "Shared nodes awaiting A1's edit"; the build drops each row once the texts match). (b) Adopt F1's two wire limits as keys so `R-DISCONNECT` cites parameters: `electrical.wire_temp_rise_short_max_c` 30 degC (any case < 60 s, `ASM-F1-TRANSIENT-LIMIT`) and `electrical.pack_lead_rise_max_c` 20 degC (`ASM-F1-PACKLEAD-LIMIT`); F1 then re-points the six rise claims. (c) `requirements.vd_ms` 27.2 → 27.25 (or C1 rounds `CL-C1-VD` to 0.1 m/s): 27.212 vs 27.2 fails `R-LOADS` by −0.05 % on rounding alone. (d) Close CR-A1-37. | D-14 one source per limit; `R-MASS-GATE` text still says 2 200 + 400 g (D-38 is 2 324 + 276); `R-TIPOVER` text still says "C5 re-derives" |
| CR-A2-21 | C5 (cc C1, D5) | (a) Drop `verifies` on the "D5 foot today" claims `CL-C5-DYN-LEVEL-CUR` and `CL-C5-DYN-PAIR-CUR` (−5 to −17 %): D-30 adopted the 38 mm biased cartridge, so they describe a superseded foot. (b) Keep `landing_calc.py` re-run at R3 after every A3 / C1 change (the four CR-C5-03 claims drift with the roll-up mass). (c) C1: `CL-C1-N-LAND-STROKE-MIN` 6.37 vs 6 (−6 %) is the single-foot bound at eta 0.5; re-derive for the constant-force cartridge (eta ≥ 0.8, 38 mm; CR-C1-17 gave ≥ 26 mm) or drop `verifies`. | `R-LANDING-IMPACT` is now worded per CR-C5-03 (tilt envelope, 2/3 W lift, n ≤ 6, ≥ 3 mm left, planar model + `T-C5-AIRCRAFT-DROP`) and should fail only if that model fails |
| CR-A2-22 | C2 (cc F4, B3, H1) | Per D-45: `CL-C2-WING-MODE-SEP` (0.077, −62 %) drops `verifies=['R-VIBRATION']` and stays as information; C2 adds `CL-C2-WING-MODES-CLOSED` (no calc, `PROPOSED`, `verifies=['R-VIBRATION']`, `how` = tap test) stating that every station-participating wing mode is either damped or inside F4's rpm-tracking notch, verified by `T-C2-TAP-TEST` (H1 adds it to the campaign with the modes to look for: 12–15, 21–27, ~82, ~215 Hz). F4's `CL-F4-NOTCH-LOW` already verifies the requirement; B3 adds the 12–15 Hz mode to the hover loop model. | `R-VIBRATION` part (b) is the tap-test + notch branch; the proof graph has no "or", so the failing separation claim must stop verifying the requirement |
| CR-A2-23 | J1 | Retire `CL-J1-TUBE-MODE-SEP` (superseded by `CL-C4-D3-SEP` 0.41, D-45) and the XT60 claims `CL-J1-XT60-CONT-PESS` (−6 %), `CL-J1-XT60-BURST` (−50 %) (D-32 chose the AS150U): drop their `verifies` or delete them; restates CR-C4-12 and CR-F1-05 | they alone keep `R-VIBRATION` at −91 % and `R-DISCONNECT` at −50 %; every F1 AS150U and wire claim passes |
| CR-A2-24 | E3 (cc A1) | (a) `CL-E3-MOUNT-PETG` (65.8 vs 58 degC, −14 %) and `CL-E3-ESC-PAD-PETG` describe the PETG option D-42 rejected: drop `verifies` so `R-THERMAL` fails only for a real reason. (b) The typed limits (motor 80, ESC 85, pack 50, FC 85 degC) become parameter keys (`propulsion.motor_temp_max_c`, …, via a CR to A1) and the claims cite `P:`. | `R-THERMAL` now lists E3's seven claims and three tests as its evidence (CR-E3-08); it should pass on paper |
| CR-A2-25 | H1 (cc E1, F4) | (a) Publish the restrained four-motor run (GT-13) as a test node, proposed id `T-H1-RESTRAINED-RUN`, verifying `CL-E1-ILIM-I`, `CL-F4-SPIN-MAX` and the `Q_M_BAT_CURR_MAX` claim F4 adds under CR-A2-14; GT-10 (pack pull) and GT-12 (arm / kill) also need test ids. (b) The matrix now names H1's raw data as `team/H1/logs/<test id>_<YYYYMMDD>.csv` per requirement (`T-C5-TILT-BOARD`, `T-C5-AIRCRAFT-DROP`, `T-C5-FOOT-RIG`, `T-F3-COMPASSMOT`, `T-F5-RANGE`, `T-E3-MOTOR-TAU`, `T-E3-ESC-PAD`, `T-F1-WIRE-HEAT`, `T-F1-CONN-HEAT`, `T-C4-TAP-D3`, `T-C2-TAP-TEST`, `T-E1-STAND`, `T-A1-WEIGH`, `T-A3-CG-BALANCE`): keep those ids when logging. | CR-H1-07; `R-ESC-CURRENT` part (a) is still nobody's test |
| CR-A2-26 | A3 | Re-run `mass_rollup.py` on D-24 / D-38 (CR-A1-25) and publish: `CL-A3-CG-X-RANGE` (`R-CG-RANGE`) and `CL-A3-ALLOC-WORST` (`R-MASS-ALLOC`) fail in the graph (−19 to −94 % depending on which stored run is on disk); add `verifies=['R-HOVER-SPLIT']` to `CL-A3-HOVER-SPLIT` (CR-A2-15) | three requirements fail on one stale script; the live margins are in the matrix |
| CR-A2-27 | F3 | `R-COMPASS` now defines the interference ratio against the total Earth field (compassmot convention, CR-F3-09): confirm `CL-F3-COMPASS-RATIO` and `T-F3-COMPASSMOT` use that denominator; `R-AIRSPEED` is worded on the RSS after `ARSPD_AUTOCAL` + reciprocal legs (`T-F3-ARSPD-CAL`) | same ratio on paper and in the ground station |
| CR-A2-28 | B2 | `R-STALL` fails only on `CL-B2-STALL-GATE-FWD` 12.06 m/s at the old 0.040 m forward limit (−0.5 %): re-run at 0.050 m (D-44, B3 gives 11.93 there) together with CR-A2-16 | the stall requirement is judged over `cg.x_range_m` |

## Answers to the CRs forwarded to A2 (CHANGE-LOG round 3)

| CR | From | A2 answer |
|---|---|---|
| CR-B3-16 | B3 | `R-CG-RANGE` reads `cg.x_range_m` with B3's two limit definitions; the 30 % differential cap stays on every axis including yaw (D-27 took 7° cant instead of lifting it), now stated in `R-HOVER-AUTHORITY` |
| CR-C2-04, CR-C4-06 | C2, C4 | `R-VIBRATION` rewritten: operating points are the criterion of record (band rule advisory); wing modes close by tap test + notch (D-45); follow-up CR-A2-22 |
| CR-C5-01, CR-C5-03 | C5 | `R-TIPOVER` R3 wording (to A1, CR-A2-20) and `R-LANDING-IMPACT` as CR-C5-03 asked; follow-up CR-A2-21 |
| CR-F1-01, CR-F1-15 | F1 | `R-DISCONNECT` R3 wording: continuous = max of hover, cruise, climb; 10 °C steady / 30 °C < 60 s / 20 °C pack leads; keys requested in CR-A2-20b |
| CR-F3-09 | F3 | `R-AIRSPEED` on the RSS ≤ 0.5 m/s after autocal + reciprocal legs; `R-COMPASS` ratio against the total Earth field |
| CR-F4-09 | F4 | `R-FSW-PARAMS` `how` records 63 / 113 matched, 50 at SITL S1, 3 LEGACY duplicates; the end state is unchanged |
| CR-F5-08 | F5 | `R-RC-LINK`: 25 mW, RSSI ≥ −93.8 dBm at 100 m, LQ ≥ 0.9 and RSSI ≥ −102 dBm in flight out to the fence radius, 500 m by analysis |
| CR-H1-07 | H1 | evidence names adopted; `GROUND-TEST-PLAN.md` added to `R-TIPOVER`, `R-ARM-KILL`, `R-COMPASS`, `R-PACK-RETENTION` and nine more; `pack_log.csv` on `R-PACK-MASS` |
| CR-I1-12 | I1 | `R-BUDGET` / `R-RESERVE` `how` and evidence name `CL-I1-SPEND-PESS`, `-RESERVE-PESS`, `-RESERVE-BASE` (they already verify the ids) |
| CR-E3-08 | E3 | `R-THERMAL` evidence and `how` name the seven claims and three tests; the four `env.*` thermal keys are its value |
| D-40, D-41 | A1 | `R-FIELD-SETUP` one spanner; `R-JOINT-STACK` per-type keys (the four previously unused `requirements.*` keys are now read) |
