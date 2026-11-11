# Change requests from A2 (systems engineer)

Status of rounds 1–3, then the round-4 requests from resolving A1-R5's action items (2026-11-10, A2-R3: D-65, D-66,
D-70, D-71). Numbers quoted are from `proofs/out/graph.json` at the A2-R3 build; the matrix is the live view.

## Rounds 1–3 — status

| # | To | Disposition (CHANGE-LOG) | A2 side |
|---|---|---|---|
| CR-A2-01 | A1 | accept, D-14 | done: 38 of 39 `ASM-A2-…` retired; one alias left while B2 cites it (CR-A2-16) |
| CR-A2-02, -03, -07, -09, -12, -17 | A1, B1/B2, C1, E2 | closed | closed |
| CR-A2-04 | A3 | forward | done by A3 |
| CR-A2-05 | A4 | forward | half: `R-JOINT-STACK` has its C6/D3 claims; `R-NO-FLOATING` still has none |
| CR-A2-06, -23 | J1 | forward | open: `CL-J1-TUBE-MODE-SEP` (−91 %) and the XT60 claims still verify `R-VIBRATION` / `R-DISCONNECT` (CR-A1-50 asked J1 to retire them) |
| CR-A2-08 | F1 | closed by D-32 | closed |
| CR-A2-10, -25 | H1, H2, H3 | forward | H1's `GROUND-TEST-PLAN.md`, `claims.json`, `logs/` exist and the matrix uses its names; no H2 or H3 folder yet (`R-PILOT`, `R-SITE`, `R-TEST-ORDER`, `R-TWIN`, `R-WIND-MEASURE` have no claim) |
| CR-A2-11 | J2 | forward, optional | open |
| CR-A2-13 | E1 | forward | done: `CL-E1-IMAX-168-55`, `-IPACK-LIM`, `-ILIM-I` read the D-34 keys (`esc_burst_a`, `full_throttle_current_a`, `motor_max_a`) |
| CR-A2-14 | F4, H1 | forward | open: no `Q_M_BAT_CURR_MAX` claim, no restrained-run test node |
| CR-A2-15 | A3 | forward | done: `CL-A3-HOVER-SPLIT` 1.217 verifies `R-HOVER-SPLIT` (+3 %) |
| CR-A2-26 | A3 | forward | open: A3 re-runs on D-62 / D-63 / D-64 (CR-A1-64); re-issued as CR-A2-37 |
| CR-A2-16 | B2 | forward | open: `wing_claims.py` line 103 still cites `ASM-A2-SERVO-TORQUE-FACTOR`; the alias stays until then |
| CR-A2-18 | D7, C1 | forward, D-31 | open: `CL-D7-TUBE-CLEAR-DROP` is D7's own foam margin |
| CR-A2-19 | B3, A5 | forward | done: `CL-A5-LAYOUT-CG-X` no longer verifies; A5's `CL-A5-ASSY-CG-X*` are judged on `cg.x_range_m` and listed under `R-CG-RANGE` |
| CR-A2-20 | A1 | accept, D-56 | (b) done: `electrical.wire_temp_rise_short_max_c` and `pack_lead_rise_max_c` exist and A1 pasted the `R-DISCONNECT` text (row closed); (a) `R-TIPOVER` pasted (re-opened for D-64, CR-A2-29b); `R-MASS-GATE` still says D-48 / 245 g; (c) closed: C1's `CL-C1-VD` re-derived to 26.7 on the capped VH |
| CR-A2-21 | C5 | forward | done: the "foot today" claims no longer verify; `CL-C1-N-LAND-STROKE-MIN` 2.47 passes; the 6-DOF model is now the model of record (CR-A2-32) |
| CR-A2-22 | C2 | forward | open: `CL-C2-WING-MODE-SEP` (−62 %) still verifies `R-VIBRATION`; no `CL-C2-WING-MODES-CLOSED` yet |
| CR-A2-24 | E3 | forward | done: `thermal.*_temp_max_c` keys exist and the `-ASD-*` claims cite them; the PETG claims are gone |
| CR-A2-27 | F3 | forward | open |
| CR-A2-28 | B2 | forward, D-71 | done: `CL-B2R3-VS-GATE-FWD` 11.99 at the D-62 forward limit (+0.1 %); `T-B2-STALL` is the gate |

## Round 4 — new (A1-R5 action items)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-A2-29 | A1 | (a) Adopt `requirements.spiral_t2_min_s` 3.3 s (D-66) so `R-SPIRAL` and B3's `CL-B3-V-LAT-T2` cite a key instead of a typed 3.3 / 4.0. (b) Paste the R3 wordings in `REQUIREMENTS.md` "Shared nodes awaiting A1's edit": `R-MASS-GATE` (D-63: the reserve is `{P:mass.growth_reserve_g}` 214 g), `R-TIPOVER` (D-64: "any accepted pack, 546 g to the `CL-A1-PACK-ACCEPT` line" replaces "503 to 680 g"; adds `CL-C5-SIM3D-DRIFT-TIPS`), `R-PROP-CLEAR` (blade swept volume on the canted axis, the tube as the governing gap, three codes + the 25 mm gauge). (c) Close the A2 line of CR-A1-50 and the A1-R5 forward (D-65 / D-66 / D-70 / D-71 all worded). | D-66 names A2 as the decider: A2 takes option (b) as written (t2 ≥ 3.3 s = B3's `sens_zcg.py` value at the top of `cg.z_range_m`, 3.34 s, so the limit holds over the whole z range; roll-stabilised modes only, which F4's `K09L.param` already satisfies: `FLTMODE1-6` = 17 / 18 / 19 / 5 / 7 / 11, no 0 / 2 / 4) |
| CR-A2-30 | B3 (cc A1) | (a) `CL-B3-V-LAT-T2`: `limit=('>=', 'P:requirements.spiral_t2_min_s')` once CR-A2-29a lands, `verifies=['R-SPIRAL']`; today it has a typed 4.0 and no `verifies`, so `R-SPIRAL` has no claim. (b) Add `CL-B3-V-LAT-T2-ZTOP` (t2 at the top of `cg.z_range_m`, `sens_zcg.py` 3.34 s) verifying `R-SPIRAL`, since the requirement is judged over the z range. (c) `CL-B3-V-SM-A3-ENV` 0.0476 (−4.8 %) and `CL-B3-V-CG-A3-AFT-ENV` −0.77 mm fail `R-STATIC-MARGIN` / `R-CG-RANGE` on A3-R6a's CG in the D-47 bay: re-run on A3's D-62 roll-up when it lands (expected +1.5 mm). | `R-SPIRAL` is new in `team/A2/claims.json` (owner B3, support F4 / H2 / H3, method A+I+D) |
| CR-A2-31 | F4 (cc H3) | (a) Emit `CL-F4-NO-RAW-MODES` from `fsw_check.py`: count of `FLTMODE1-6` values in {0 MANUAL, 2 STABILIZE, 4 ACRO} = 0, `verifies=['R-SPIRAL']`, `how` = lint of `K09L.param` (today 17 / 18 / 19 / 5 / 7 / 11). (b) `CL-F4-DESCENT` (`Q_PILOT_SPD_DN` 1.2) adds `limit=('<=', 'P:requirements.landing_sink_ms')` and `verifies=['R-LANDING-IMPACT']`: the hard-landing requirement is now the pilot's down-stick limit (D-65). (c) H3: "no MANUAL / ACRO / STABILIZE above 5 m" and "QLAND for the last 6 m" on the flight card. | `R-SPIRAL` part 2 is an inspection of the parameter file; without a claim it stays `UNVERIFIED (no claim)` |
| CR-A2-32 | C5 (cc D5, C1, C4, H1) | (a) Re-run `landing_sim_claims.py` at `requirements.landing_sink_ms` 1.2 so the claims of record carry the 1.2 m/s values: `CL-C5-SIM3D-STROKE` (38.6 vs 35 mm usable, −10 %) and `CL-C5-SIM3D-BOTTOM-TILT` (5.0 vs 10 deg, −50 %) still hold the 1.5 m/s run and fail `R-LANDING-IMPACT` for a superseded reason; D-65 expects 34.5 mm at 2.6 kg. (b) `verifies=['R-LANDING-IMPACT']` on `CL-C5-SIM3D-V-SINK-10` (the sink that clears 10 deg ≥ `landing_sink_ms`) and on `CL-C5-SIM3D-SIDE-LOAD` / `-SIDE-ULT` with the limit = D5's sleeve capacity on the D-65 sleeve (today the limit is the superseded hand value `CL-C5-FOOT-SIDE-LOAD`, so the design side load fails against itself). (c) `CL-C5-FEA-SHOE-SF` 0.22: re-run the SU2 shoe FEA on D5's D-65 sleeve (wall 2.0, rim 3.0, R 1.0, 25 mm engagement) or drop `verifies` until D5 delivers it. (d) `CL-C5-SIM3D-V-BROADSIDE` 4 m/s vs `wind_limit_ms` 5 (−20 %) fails `R-WIND`: landings are flown wingtip-into-wind (`R-TIPOVER`, flight card), so either verify `R-WIND` with `-V-SPANWISE` (8 m/s) only or ask H3 for a broadside rule. (e) `CL-C5-TIPOVER-WORST` re-run at the D-62 corner (forward limit 0.0466, z 0.025; A1's bound 30.98°). | `R-LANDING-IMPACT` is worded on the 6-DOF model (D-65) and should fail only if that model fails at 1.2 m/s |
| CR-A2-33 | H1 (cc C5, E3, A3, B3, A5) | (a) GT-10: level drop 0.115 m (1.5 m/s, C1's L1 bound, unchanged) plus 10° pitch, 10° roll and the diagonal corner drop from 0.073 m (1.2 m/s, D-65) in place of "pitch 4°, roll 8° at 0.093 m"; pass line strokes ≤ 35 mm within 3 mm of the 6-DOF model, CG ≤ 6.6 g (`landing_n_design`), shoe sleeves uncracked. (b) GT-07: `CL-H1-CG-ACCEPT-FWD/-AFT` read `P:cg.x_range_m`, so re-run `ground_tests.py` on D-62 (the plan text still prints 0.0506–0.0544); keep the three balance ids (`T-A3-`, `T-B3-`, `T-A5-CG-BALANCE`) as one event or publish one alias. (c) GT-04: add `T-E3-ESC-PAD-CFD` (E3's half-fin mock-up film-coefficient check) with the log name `logs/T-E3-ESC-PAD-CFD_<YYYYMMDD>.csv`; the matrix already looks for it. | the matrix names H1's raw-data files per requirement (CR-H1-07) |
| CR-A2-34 | B4 (cc E1, A5) | Re-run `props.py` on the D-61 mount (`face_ahead_m` 0.0075) so the ids of record carry the R5 gaps: `CL-B4-GAP-TUBE-ENV` (21.1 mm, −15 %) and `CL-B4-TIP-WING` (34.2) still hold the R4 mount while `CL-B4-GAP-TUBE-FIX5` (26.1) and `CL-B4-TIP-WING-FIX5` (35.8) carry the fix without `verifies`; or move `verifies=['R-PROP-CLEAR']` to the FIX5 pair. Drop `verifies` on the hub-mid-plane `CL-B4-GAP-TUBE` (superseded by the swept-volume claim). E1's `CL-E1-TIP-GAP-TUBE` already re-ran to 26.1 mm. | `R-PROP-CLEAR` lists the three claims A1 named; it fails today on B4's stored R4 value only |
| CR-A2-35 | E3 | `CL-E3-CEIL-ASD` tests a typed `>= 30`: cite `P:env.ambient_design_c`. | one source per limit (D-14) |
| CR-A2-36 | C4 (cc B4, A3) | Make the D-70 re-run triggers visible in the graph: `CL-C4-RERUN-RPM` (`CL-B4-CRUISE-RPM` ≤ 6 390 rpm) and `CL-C4-RERUN-MASS` (station mass ≤ 1.15 × the as-designed 84.2 + 7.6 + 4 g), information claims with no `verifies`, so a breach shows as `FAIL` in `CHAIN.md` instead of in a note. `R-VIBRATION` text now records both triggers and names `CL-C4-SIM-SEP` 0.29 as the value of record. | the requirement would otherwise pass silently after the next rpm or mass change |
| CR-A2-37 | A3 (cc A1) | Re-run `mass_rollup.py` on D-62 / D-63 / D-64 (CR-A1-64): `CL-A3-CG-X-RANGE` and `-X-STATIONS` are judged against the new `cg.x_range_m` [0.0466, 0.0514] with the pack still at the D-47 datum, so `R-CG-RANGE` fails for a stale reason; update `ASM-A3-PACK-RANGE` to the 546 / 550 / 590 g cases and add `verifies=['R-HOVER-SPLIT']` to `CL-A3-HOVER-SPLIT` (CR-A2-15). | three requirements (`R-CG-RANGE`, `R-MASS-ALLOC`, `R-MASS-GATE`) fail on one stale script |

## Answers to the CRs forwarded to A2 (CHANGE-LOG A1-R5)

| CR | From | A2 answer |
|---|---|---|
| CR-C5-17, CR-C5-19 | C5 | `R-LANDING-IMPACT` re-worded (D-65): 1.2 m/s at ≤ 10° of combined tilt in any direction, n ≤ `landing_n_design` (6.6) at the as-designed mass, the simulated side load as the design side load, the 6-DOF model of record, C1's 1.5 m/s L1 / L4 kept as the structural bounds in `R-LOADS`; follow-ups CR-A2-32, -33 |
| CR-B3-26 | B3 | `R-SPIRAL` added: t2 ≥ 3.3 s over `cg.z_range_m`, roll-stabilised modes only, no MANUAL / ACRO / STABILIZE above 5 m (D-66 option b, A2's decision; rationale in `SUMMARY.md`); follow-ups CR-A2-29a, -30, -31 |
| CR-C4-39 | C4 | the re-run triggers (cruise rpm > 6 390, station mass > +15 %) are in the `R-VIBRATION` text and `how`; `CL-C4-SIM-SEP` is the value of record; follow-up CR-A2-36 |
| CR-B3-16 | B3 | `R-CG-RANGE` reads `cg.x_range_m` with the V1 ids `CL-B3-V-CG-FWD` / `-CG-AFT-ENV` and the CG height; the 30 % cap stays on yaw (`R-HOVER-AUTHORITY`) |
| CR-A5-31 | A5 | `CL-A5-ASSY-CG-X`, `-FWD`, `-RANGE-USE` listed under `R-CG-RANGE` (A5 in support; `team/A5/claims.json` is evidence) |
| CR-B4-22 | B4 | `CL-B4-TIP-WING`, `CL-E1-TIP-GAP-TUBE`, `CL-B4-GAP-TUBE-ENV` listed under `R-PROP-CLEAR` with an R3 wording on the blade swept volume; follow-up CR-A2-34 |
| CR-E3-18 | E3 | the `-ASD-*` ids, `CL-E3-CEIL-ASD` and `T-E3-ESC-PAD-CFD` are in `R-THERMAL`'s `how` and evidence; follow-up CR-A2-35 |
| CR-B2-19, CR-D6-07 | B2, D6 | `CL-B2R3-SERVO-TORQUE-REQ` (3.49 kgf·cm at the servo output through D6's linkage vs 3.9 at 6 V, +11 %) verifies `R-SERVO-TORQUE`; the text now names the 6 V rail and the linkage ratio (D-71) |
| CR-C6-21 (a), CR-E1-36 | C6, E1 | no requirement change: `R-JOINT-STACK` and `R-ESC-CURRENT` already read the D-41 / D-34 keys |
