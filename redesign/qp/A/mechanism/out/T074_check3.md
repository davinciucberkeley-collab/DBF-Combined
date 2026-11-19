# T-074 check 3 (R-OPT-01, R-PHY-09), concept A, O4b: scheduled-cap window at 1.64 kg and F-5 landing re-runs (2026-11-19)

Status: analysis only ($0), NOT VERIFIED COMPLETE. Authorised by AM-006. Nothing committed. No CAD, docs/, CHANGE-LOG, ledger, MASS-GATE, BOM touched.
Limits not relaxed: A-P3 window >= +-5 %, C6 rows RF >= 1.0 at rigid-body demand, A-P9 >= 30 deg, A-P16 12.1 A one motor.
**Check 3 verdict: PASS** (both parts), with the conditions in section 4. Every analysis is labelled by category; every model constant is EST unless a source is given in the script it comes from.

Categories: step 1 = illustrative (hand arithmetic on the `prop_a.py` motor model, APC PER3 static rows, I0 0.5 A EST, pack R 30 mohm EST); step 2 = flight dynamics (ArduPlane SITL + `a_plant.py` plant, the C3-equivalent record, see 2.1); step 3 = rigid-body dynamics (`landing_a.py`) + hand calculation (C6 rows) + static geometry (A-P9).

## 0. Code changes (defaults reproducible)
| File | Change | Default check |
|---|---|---|
| `redesign/qp/A/prop_a.py` | added `cap_sched(vrest, m, imax=12.1)`, `tw_state`, `window_pct`, `sched_report`; new flag `--sched [--mass m]` | `python -I prop_a.py` output byte-identical to HEAD (cmp, 0 differences) |
| `redesign/qp/A/mission_gate_a.py` | appended block under `--sched [--mass m]` | `python -I mission_gate_a.py` md5 identical to HEAD version (d508b1b5...) |
| `redesign/qp/A/structures/landing_a.py` | `M_GATE` reads env `LAND_MASS_KG` (default 1.50); CAD CG x reads env `LAND_CG_X_MM` (default CAD 21.37 mm) | `python -I landing_a.py 30` diff against committed `T073_data/landing_a_30N.txt`: identical |
| `redesign/qp/A/structures/landing_centre_a.py` | cache dir reads env `LAND_OUT_DIR` (default `T071b_data`, unchanged) | default cached run diff against committed `T071b_data/centre_run.txt` (timing lines excluded): identical |
`sitl/run_fwd.py`, `a_plant.py`, `A.param` unchanged. New runs are in `sitl/runs/T074_*` (git-ignored) and copied (summary, result, parameter file, plant CSV) to `T074_data/sitl_runs/`.

## 1. Scheduled-cap case, 1.64 kg (illustrative; `python -I prop_a.py --sched --mass 1.64`, exit 0, 69 s; `mission_gate_a.py --sched --mass 1.64` exit 0)
Definition (audit s7 item 1): `cap(V_rest)` = largest duty (<= 1.0) with one saturated motor plus three hovering at 1.64 kg <= 12.1 A (`prop_a.one_motor`, as committed: hover thrust at derate 1.0). Window arithmetic = `mission_gate_a.py` (low edge 1.33 W, high edge 0.80 x T/W sag, T/W with hot 0.97 on sag, derate, cos 17 deg, no download factor).

| V_rest V | cap(V) | one-motor A at cap | one motor A uncapped | all-four A at cap |
|---|---|---|---|---|
| 16.8 (fresh) | 0.903 | 12.10 | 14.22 | 11.21 |
| 16.0 | 0.952 | 12.10 | 13.06 | 11.20 |
| 15.6 | 0.979 | 12.10 | 12.48 | 11.20 |
| 15.2 | 1.000 | 11.98 | 11.98 | 11.09 |
| 14.92 (sag, 3.73 V/cell) | **1.000** | 11.61 | 11.61 | 10.75 |
The cap is binding only above about 15.4 V rest; at the sag state A-P3 is judged at it is not binding (duty 1.0), A-P16 holds by construction.

Derate sweep at 1.64 kg (`T074_data/s1_prop_sched_1.64.txt`; 1.639 kg file alongside):
| derate | T/W fresh (sched cap 0.903) | T/W sag (cap 1.0) | window +-% scheduled | +-5 % mass g scheduled | fixed 0.90: T/W sag | fixed 0.90 window | fixed 0.90 +-5 % mass g |
|---|---|---|---|---|---|---|---|
| 1.00 | 2.266 | 2.104 | +11.7 | 1,878 | 1.781 | +3.4 | 1,590 |
| **0.93 (design)** | **2.107** | **1.957** | **+8.1** | **1,747** | 1.657 | **-0.2** | 1,478 |
| 0.90 | 2.039 | 1.894 | +6.5 | 1,690 | 1.603 | -1.8 | 1,431 |
| 0.88 | 1.994 | 1.852 | +5.4 | 1,653 | 1.567 | -2.9 | 1,399 |
| 0.873 | 1.978 | 1.837 | +5.0 | 1,640 | 1.555 | -3.3 | 1,388 |
| 0.85 | 1.926 | 1.789 | +3.7 | 1,597 | 1.514 | -4.7 | 1,351 |
| 0.80 | 1.812 | 1.684 | +0.6 | 1,503 | 1.425 | -7.7 | 1,272 |
Reads: matches the audit (+8.1 / +8.2 %, 1,747 g, threshold derate 0.873). At 1.64 kg the fixed 0.90 cap fails A-P3 (-0.2 %), so O4b depends wholly on the scheduled cap. T/W fresh falls under A-P2's 2.0 below derate about 0.88 (1.994 at 0.88), a second limit that bites a little earlier than the window.
Side check, `Q_M_BAT_CURR_MAX` 41 A (`A.param`, audit s7 item 2; `batt_curr_check.py`, illustrative): at sag with all four at duty 1.0 the pack current is **43.9 A** (53 A fresh uncapped), so the 41 A limiter acts on the full-duty state and would hold the sag duty to 0.974 (-4.1 % thrust): window +-6.1 %, +-5 % mass 1,676 g. Still above 5 %, but the parameter must be raised to 45 A or more, or the window figures above carry that 2 points.

## 2. C3 time-domain pitch-over at 1.64 kg with the scheduled cap (flight dynamics)
### 2.1 Which tool is "the C3 record"
There is no stand-alone C3 script for concept A. `T-A-C3-PITCHOVER` is state "planned" in `proofs/claims_a0_base.py`; MASS-GATE s1 and A-P3 give the window by arithmetic only ("C3's time-domain run replaces both edges"). The committed time-domain pitch-over evidence is the **SITL entry-ratio sweep** (`sitl/run_fwd.py case=trans r=...`, runs `S_r120 ... S_r160`, `redesign/review/QP-3/SITL-FLIGHT.md` s2: ArduPlane SITL + `a_plant.py` fwd=1 with APC prop, full-alpha wing, elevons, fins). I used that same tool and procedure (50 m hover, QSTABILIZE 1.0 s pre-climb, FBWA, CRUISE; wind 0; `hold=25 cruise_s=8`). Pass criteria are the ones that record applies: no altitude loss, handover speed >= 12.94 m/s, pitch use <= 0.60 of the 20 deg stop (params `pitch_use_max`), peak altitude under the 110 m fence from a 50 m start, no sustained motor cap, alpha not above about 25 deg (1.20 was called marginal at 32 deg).
**Cap model (no Lua in the loop):** the scheduled cap is modelled as a constant `P:Q_M_SPIN_MAX=1.0` = cap(14.92 V), the value a Lua schedule would hold at the plant's resting voltage (the plant runs the 14.92 V sag state throughout). A voltage-scheduled cap at one resting voltage is a constant; the Lua script's estimator, rate limit and failsafe are not modelled. `stick_for()` in `run_fwd.py` reads the same parameter, so the throttle mapping is consistent.
Control: `T074_ctl150` (mass 1.50, r 1.33, A.param as today) vs committed `S_r133`: alt gain 31.4 vs 30.3 m, handover 13.3 vs 13.2 m/s, alpha 9.8 vs 10.7 deg, u max 0.774 vs 0.808. Same behaviour; the small differences are the A.param / CAD updates since 2026-11-15 (pitch use 0.48 of 20 deg).

### 2.2 Results (`T074_data/s2_c3_table.md`; 12 SITL runs, 126 s wall each, 3 in parallel, all exit 0, `run_c3.log`)
Mass 1.64 kg, sag state, CAD CG 21.37 mm, SPIN_MAX 1.0 (S) or 0.90 as in A.param (F):
| Run | entry T/W | duty at entry | alt gain m | peak alt m | handover V m/s | pitch use of 20 deg | alpha max deg | u max | motor A / pack A peak | rating |
|---|---|---|---|---|---|---|---|---|---|---|
| S 1.20 | 1.20 | 0.744 | 12.7 | 63.8 | **12.8** | 0.52 | **32.3** | 0.901 | 7.9 / 22.2 | marginal (V < 12.94, alpha 32), as 1.20 was at 1.50 kg |
| S 1.25 | 1.25 | 0.763 | 21.1 | 74.1 | 14.2 | 0.49 | 23.6 | 0.875 | 7.5 / 23.5 | pass |
| S 1.33 | 1.33 | 0.793 | 30.7 | 83.6 | 13.8 | 0.44 | 10.5 | 0.814 | 6.4 / 25.9 | pass |
| S 1.42 | 1.42 | 0.826 | 37.2 | 90.4 | 14.5 | 0.49 | 9.0 | 0.845 | 7.0 / 28.5 | pass |
| S 1.51 (0.80 x T/W sag) | 1.51 | 0.860 | 44.3 | 98.0 | 15.4 | 0.50 | 9.1 | 0.879 | 7.8 / 31.3 | pass |
| S 1.60 | 1.60 | 0.893 | 49.0 | 103.0 | 16.3 | 0.54 | 9.7 | 0.913 | 8.5 / 34.5 | pass, fence margin 7 m |
| F 1.20 | 1.20 | 0.744 | 13.8 | 65.0 | 13.0 | 0.54 | 30.5 | 0.885 | 7.6 / 22.6 | marginal |
| F 1.33 | 1.33 | 0.793 | 32.1 | 85.0 | 13.8 | 0.44 | 9.9 | 0.818 | 6.5 / 26.2 | pass |
| F 1.60 | 1.60 | 0.893 | 48.5 | 101.9 | 16.2 | 0.56 | 10.0 | 0.900 | 8.4 / 34.1 | pass (u max at the 0.90 cap, 7 s at u >= 0.85) |
CG sensitivity (S, 1.64 kg): r 1.33 at CG 19.3 mm: pitch use **0.55**, alpha 10.3, alt gain 31.6 m; at 26.0 mm: 0.39 / 10.5 / 30.8; r 1.51 at 26.0 mm: 0.37 / 9.1 / 43.5. Pitch use at the forward trim end (0.55) is under 0.60 by 0.05. The predicted CG at 1.64 kg is "—" (no placed positions for the skin, C6 node, new pack or growth), so the A-P4 range ends are bracketed instead of one point.
Every run: no altitude loss, no touchdown, no fence crossing, roll after handover under 1 deg (see `sum.json`), cruise at 16.4-16.5 m/s.

### 2.3 Window
| Definition | Low | High | Window |
|---|---|---|---|
| A-P3 / MASS-GATE arithmetic as committed (no download factor), sag, scheduled cap | 1.33 | 0.80 x 1.957 = 1.566 | **+-8.1 %** (+-5 % mass 1,747 g) |
| Same arithmetic with the plant's 3 % slipstream download (`a_aero.DOWNLOAD` 0.97; what the SITL static thrust uses, `run_fwd.static()`) | 1.33 | 0.80 x 1.888 = 1.510 | **+-6.35 %** (+-5 % at derate 0.905 instead of 0.873) |
| Time-domain passing band (SITL, section 2.2) | 1.25 (1.20 marginal) | >= 1.60 (not found; fence margin 7 m) | +-12.3 % or wider |
| Fixed 0.90 cap, download included, same low edge (for contrast) | 1.33 | 0.80 x 1.619 = 1.295 | -1.3 % (fails) |
**Reported window: +-6.35 %** (the more conservative of the two arithmetic forms; time-domain run passes the whole 1.33-1.51 band with margin, u max 0.879 and 7.8 A per motor at 1.51). The repo arithmetic omits the download factor that the plant carries: the committed A-P3 numbers (+-4.3 % at 1.50 kg) are the no-download form, so I report both rather than pick. Time-domain finding to flag: in the plant the fixed 0.90 cap does not stop the transition either (F runs pass at 1.33 and 1.60); the cap changes the 20 % control-reserve edge of the A-P3 definition, not the plant's pass/fail. I did not change the definition.
**A-P3 at 1.64 kg with the scheduled cap: PASS (>= +-5 %).**

## 3. F-5 landing re-runs at 1.64 kg (rigid-body dynamics; commands in `run_s3.sh`)
Method: `LAND_MASS_KG=1.64`; CG = CAD 21.37 mm (default) with 19.3 and 26.0 mm for `landing_centre_a.py` and the static tip angle (A-P4 range ends; the predicted CG is "—"). The sim scales its whole item list uniformly to the new mass (`mass_props(scale_to)`), so inertia scales with mass, the pad plateau stays 30 N, C6 +19 g and the other T-070 changes are not added as separate items (EST). Stroke limit 20 mm usable.

| Command (cwd `redesign/qp/A/structures`, `python -I`, env as above) | Exit | Wall | Output |
|---|---|---|---|
| `landing_a.py 30` | 0 | 44 s | `s3_landing_a_30_m1.64.txt` (and default check, identical to committed) |
| `landing_side_a.py` | 0 | 134 s | `s3_side_m164_cgcad.txt` |
| `landing_tip_b.py` | 0 | 91 s | `s3_tip_m164_cgcad.txt` |
| `landing_centre_a.py --recompute` (cache in `LAND_OUT_DIR`, deleted after: 16 MB each, regenerable in 42 s) | 0 | 42 s | `s3_centre_m164_cgcad.txt`, CG variants `..._cg19.3.txt`, `..._cg26.0.txt` (44 s each) |
| `landing_centre_a.py` (cached) | 0 | 8 s | `s3_centre_cached_m164_cgcad.txt` |
| `landing_nodes_b.py` (C6 foot-path rows, bonus) | 0 | 37 s | `s3_nodes_m164_cgcad.txt` |
All stderr files empty.

### 3.1 C6 (T-071b A.2 recommended: H3 hub extension + N2 node), min RF (`c6_extract.py`, `s3_c6_rows.txt`)
| Row | 1.50 kg (T071b) RB / x1.5 | 1.64 kg CAD CG RB / x1.5 | 1.64, CG 19.3 RB | 1.64, CG 26.0 RB |
|---|---|---|---|---|
| hub bore bearing | 1.94 / 1.29 | 1.76 / 1.17 | 1.82 | 1.81 |
| collar bending (interlayer 9.5 MPa) | 2.51 / 1.67 | 2.27 / 1.52 | 2.35 | 2.35 |
| saddle socket bearing | 1.69 / 1.13 | 1.56 / 1.04 | 1.59 | 1.62 |
| bridge bending | 4.24 / 2.83 | 3.89 | 3.98 | 4.04 |
| node: skin to plate lap / plate shear / ear bond / pins | 3.92 / 2.88 / 1.39 / 1.67 | 3.75 / 2.75 / **1.33** / 1.60 | 1.32 | 1.35 |
| saddle body shear | 1.30 / 0.87 | **1.24 / 0.83** | 1.24 | 1.26 |
| **C6 minimum** | **1.30 / 0.87** | **1.24 / 0.83** | **1.24 / 0.83** | **1.26 / 0.84** |
**C6 min RF at rigid-body demand = 1.24 at 1.64 kg (governing: printed saddle body shear), >= 1.0: PASS** (audit's scaled estimate was about 1.19, so the re-run is a little better). At the EST x1.5 dynamic factor it is 0.83 (was 0.87): below 1.0 as it was, not a check-3 criterion, still open. Demand: hub-side moment moves from 6.05 N m at 1.50 kg; the per-case values are in section 1 of `s3_centre_m164_cgcad.txt`.

### 3.2 Landing loads and stroke (30 N plateau, mu 0.40; `s3_landing_a_30_m1.64.txt`, 1.50 kg values from `T073_data/landing_a_30N.txt`)
| Case | stroke 1.50 / 1.64 mm (of 20) | Fmax N | side N | rib RF |
|---|---|---|---|---|
| hard level | 8.4 / 9.1 | 39.7 / 40.2 | 12.4 / 12.4 | 2.95 / 3.00 |
| hard 10 narrow + drift .5 | 17.5 / **19.1** | 40.1 / 40.6 | 16.0 / 16.2 | 2.85 / 2.03 |
| hard 10 wide + drift .5 y | 10.9 / 11.8 | 46.4 / 47.4 | 18.6 / 19.0 | 1.49 / 1.47 |
| hard 7/7 combo | 10.3 / 11.2 | 42.5 / 43.1 | 17.0 / 17.3 | 1.24 / 1.23 |
Answer to audit F-5 ("bottoming at 1.64 kg is '—'"): **no bottoming at the 30 N plateau, but the stroke margin shrinks from 2.5 to 0.9 mm** (worst case 19.1 of 20 mm, A-P13's quoted 15.2 mm is the older figure). `landing_side_a.py` s3 plateau sweep: 27 N now bottoms (20.3 mm; 19.4 mm at 1.50 kg) and 24 N too (20.5), i.e. the plateau must stay at 30 N or more; rib RF min at 30 N is 1.23 (1.24 at 1.50 kg). The mu at rib RF = 1 is 0.50-0.55 (0.49-0.57 at 1.50 kg). The SITL "lean 29 narrow" row tips over at both masses (tilt_end 178 deg, rib RF 0.07 against 0.11): it is a pre-existing outside-envelope row, unchanged in kind. Demand is not monotone in mass: some rows improve (root-block pin shear 0.66 to 0.84, bearing 0.23 to 0.30; P9a/b rib tube 1.03 to 1.31; PIN 1 pin rows stay below 1.0 as drawn).
Foot-path rows from `landing_nodes_b.py` (1.64 vs T071b 1.50): strut clamp bond 1.05 (1.07), strut Euler 1.06 (1.08), P15 wrinkling 1.22 (1.23): pass but thinner. Still below 1.0 and unchanged in kind: CUP EVA rows 0.01 / 0.14 / 0.15 (model class), bond-integrity rows P3 0.25, P5 0.97 (was 1.03, now below 1), P10 0.08, P13 0.54 (coupon class), 1-pin rows (0.84 shear / 0.30 bearing), cradle pin bearing 0.48 (3 x 2 mm wall).

### 3.3 A-P9 tip-over
Static tip-over does not depend on mass. At the T-068 D2 pad (ground plane x 0.3415, edge z 0.195, pad centre z 0.189, CG z 6.37 mm, "—" measured) vs CG x (`tip_static_cg.py`, `s3_tip_static_cg.txt`):
| CG x mm | edge angle deg (A-P9 >= 30; T-068 target 30.5) | pad-centre bound deg |
|---|---|---|
| 19.3 (A-P4 forward trim end) | 30.35 | 29.55 |
| 21.37 (CAD) | 30.51 | 29.70 |
| 26.0 (A-P4 aft end) | 30.87 | 30.06 |
**A-P9 at the edge definition (T-068 s4): 30.35-30.87 deg, >= 30 across the A-P4 CG range; the T-068 30.5 target is missed at the forward end (-0.15 deg); the pad-centre bound is under 30 over most of the range (as in T-071b).** Dynamic lean scan at 1.64 kg (`landing_tip_b.py`, 2 deg grid) gives the same maximum upright leans as the committed 1.50 kg run (D2: 24 / 16 / 12 / 8 deg at lateral 0.16 / 0.40 / 0.52 / 0.70 m/s, mu 0.40; 24 / 16 / 14 / 12 at mu 0.30); the grid is coarse, so a change under 2 deg would not show.

## 4. Verdict and conditions
**Check 3: PASS.** (a) Scheduled-cap window at 1.64 kg is +-8.1 % (repo arithmetic) / +-6.35 % (plant arithmetic with download), time-domain pitch-over passes 1.25-1.60 at every CG tried: >= +-5 %. (b) C6 min RF 1.24 at rigid-body demand at 1.64 kg: >= 1.0. A-P9 holds at the edge definition.
Conditions that go with the PASS (none are relaxed limits):
1. Window margin is thin against the bench derate: threshold 0.873 (repo arithmetic) or about 0.905 (plant arithmetic, download included); the design value 0.93 is EST until the 2026-12-15 bench.
2. Fixed 0.90 fails at 1.64 kg (-0.2 % / -1.3 %): O4b needs the scheduled cap running on the real FC (check 1, Lua on the Kakute, is not part of this task) or an equivalent. `Q_M_BAT_CURR_MAX` 41 A must go to 45 A or more (else +-6.1 %).
3. The cap is modelled as a constant at the sag voltage; the Lua estimator, rate limit and failsafe-to-0.90 are not exercised. At fresh voltage cap(16.8) = 0.903, so a failsafe to 0.90 costs nothing at fresh and the transition window is judged at sag.
4. Landing: stroke 19.1 of 20 mm (0.9 mm left) and plateau >= 30 N required; C6 at x1.5 is 0.83; cup, bond-integrity and 1-pin rows stay below 1.0 (model / coupon class, pre-existing); P5 integrity dipped to 0.97. CG at 1.64 kg is "—": results are bracketed over 19.3-26.0 mm. Uniform mass scaling is the sim's convention; the +19 g C6 and the new items are not modelled individually.
5. SITL plant gaps already named in SITL-FLIGHT.md s2 (no measured post-stall moment peak, EST elevon effectiveness) apply: "pass on this model", not proof of a wide window.

## Files
`redesign/qp/A/mechanism/out/T074_check3.md` (this), `T074_data/`: `s1_*` (step 1), `s2_c3_table.md`, `run_c3.sh`, `run_c3_jobs.txt`, `run_c3.log`, `sitl_runs/`, `s2_batt_curr_check.txt`, `batt_curr_check.py`, `s3_*` (landing), `run_s3.sh`, `c6_extract.py`, `s3_c6_rows.txt`, `tip_static_cg.py`.
Modified sources (uncommitted): `prop_a.py`, `mission_gate_a.py`, `structures/landing_a.py`, `structures/landing_centre_a.py`.
