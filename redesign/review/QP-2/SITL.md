# QP-2 SITL crosswind hover, concept A (F4 + B3, 2026-11-14)

Files written: `redesign/qp/A/sitl/` (plant, runner, batch scripts, `runs/*/case.csv` + `result.json`, `table.md`) and `redesign/qp/A/A.param` (draft). Nothing else edited, no git.
Labels: `EST` estimate; `V` vendor page (sizing_a.py, read 2026-11-14); `—` unknown. Every number in the tables below is from `runs/*/result.json` on this machine.

## Verdict

**5 m/s steady hover is not a SITL failure for A on this model, so R2 (BOARD) is not triggered by this test. 7 m/s is a fail, and the failure that matters is yaw, not lean or thrust.**

| Wind | Belly into wind | Wing edge into wind | 45 deg and 20 deg off the tip |
|---|---|---|---|
| 3 m/s | pass | pass | pass (45 deg) |
| 5 m/s | **marginal**: lean 29 deg, no saturation, but position hold stays 4.5 m off (stock gains) | **pass**: lean 10 deg, hold 0.4 m | **marginal**: yaw error up to 9 deg, differential 35-37 % of the 40 % line |
| 5 + 2 m/s gust | marginal (lean peak 34 deg, same offset) | pass (lean peak 17 deg) | not run |
| 7 m/s | **fail**: lean 42-44 deg, at the 45 deg cap, hold 11 m off | **pass**: lean 19 deg, hold 1.1 m | **fail**: heading lost (yaw error 67-117 deg), a motor at its floor 2-6 s |

Reading it: A hovers fine in a crosswind when the wing edge points into it. Broadside it needs 29 deg of lean at 5 m/s (sizing_a.py: 29 deg, agrees) and 42 deg at 7 m/s (sizing 47 deg). Between those two headings the wing plate's yaw moment grows faster than the cant can answer. This supports BOARD C2 (land wing-edge into the wind) and says the 5 m/s flight-card limit should also carry a heading window, which SITL has only sampled at 0, 45, 70 and 90 deg (below).

## 1. The SITL model, and what it cannot represent

The stock `quadplane-copter_tailsitter` model is not A: it is a small over-powered airframe with its own aerodynamics, fixed mass and inertia, and `SIM_WIND_*` acts on it only. None of its parameters set mass, inertia, thrust curve or cant. So the A runs use **ArduPlane SITL's JSON backend** (`--model JSON:127.0.0.1`, the same `ArduPlane.elf` as `team/F4/sitl/RESULTS.md`: 4.7.3-beta1, Windows Cygwin build) driven by `qp/A/sitl/a_plant.py`, a hover-only rigid-body model of A written for this test. ArduPilot's own code (EKF, QLOITER, rate loops, mixer) runs unchanged; only the airframe, wind and ground are mine. Output map is K09-L's (motors 1-4, X frame, elevons 5-6), so no wiring override was needed.

| Item in the plant | Value | Source |
|---|---|---|
| Mass | 1.23 kg (low end, leans most); 1.37 kg checked at 5 m/s | task, sizing_a.py |
| Inertia about body x (yaw) / y (copter pitch) / z (copter roll) | 0.053 / 0.016 / 0.054 kg m^2 at 1.23 kg; 0.059 / 0.018 / 0.060 at 1.37 | `EST`: sizing mass table, point masses at the motor cage, fins, pack, plus wing plate. sizing_a.py used 0.036 for yaw with fewer items; this is the larger, slower case |
| Motors | 4 x MN2212 KV780 + 9545 at (y, z) = (+-0.19, +-0.13) m, prop plane 0.11 m ahead of the CG; ArduCopter X spin directions | sizing_a.py `Y_M`, `Z_M`; x `EST` |
| Thrust per motor | maker table at 14.8 V (293 / 476 / 605 / 742 / 918 g at 50 / 65 / 75 / 85 / 100 %), power law below 50 %, x0.97 download, **x0.767 pack-sag and hot-winding factor** (sizing_a.py: 13.16 V, 0.97) | V; sagged = worst case. Hover then needs throttle 0.61, cap 0.90 gives 614 g/motor (T/W 1.9 at 1.23 kg after cant and download) |
| Cant | 14 deg, tangential, thrust vector tilted about the radial direction; reaction torque kq = 0.0204 m | sizing s4 (Q 65 N mm at 3.19 N). Checked offline: +-0.10 throttle differential gives 0.276 N m of yaw at 14 deg (sizing: 0.279 at 30 % differential) |
| Motor lag | 0.04 s first order | `EST` |
| Inflow | thrust falls as 1 - (Vc / V0)^2 with the air component along the shaft, V0 = pitch speed at hover rpm (8.1 m/s) | `EST`, sizing's prop model |
| Wing in wind | cross-flow plate on the normal component, Cd 2.0, S 0.22 m^2; centre of pressure moves to the windward quarter span, scaled by min(1, vy / (2.75 vz)) | Cd and 0.25 b from sizing s4; the **scaling with heading is mine (`EST`)** |
| Fins | two plates 0.36 x 0.12 m, Cd 2.0, 0.215 m aft of the CG | sizing; Cd `EST` |
| Wind | 4 s ramp after the aircraft is hovering at 20 m; gust = 1-cosine 2 s; turbulence = first-order, sigma 1.0 m/s (0.5 vertical), tau 2 s | mine, **not** `SIM_WIND_*` |
| Ground | four fin-tip contacts (0.275 m below the CG), takeoff in still air | sizing s4 |

Cannot be represented, so every result is conditional on these: elevon force (hover is motors only, no slipstream credit, as sizing and K09-L); prop in-plane (H) force and flapping; wing and fin lift in the slipstream; motor current, battery and ESC limits (the cap is the `Q_M_SPIN_MAX` 0.90 output, not an ampere limit); vibration and the 70 Hz notch; the real thrust curve (the maker's rpm column is inconsistent, sizing s3); takeoff or landing in wind; transition, cruise, back-transition (not run, see section 5). SITL sensors use ArduPilot's default noise. The EKF's yaw comes from SITL's own compass model of the JSON attitude.

## 2. Cases and results (hover at 20 m, QLOITER, yaw held at the heading at takeoff, 36 s of steady wind logged)

Setup: `A.param` minus board-only lines, plus SIM-only overrides (listed in section 6). Wind direction is where the wind comes from, belly of the aircraft facing 0 deg. Limits used (EST, mine, stated so the board can change them): lean <= 40 deg (`Q_A_ANGLE_MAX` 45 less 5 deg); a motor at the 0.90 cap for one unbroken run <= 1 s; a motor at the floor (<= 0.16) one run <= 0.5 s; yaw error <= 10 deg; yaw differential (mean of motors 1,2 against 3,4, divided by mean throttle) <= 30 % (K09-L S20) and **40 % = the sizing's "authority at 30 % thrust differential"**; position error is reported against K09-L S3's 1 m line, not gated.

| case | wind | lean max / mean (deg) | max motor output | s at cap (longest run) | min output / s at floor | yaw err max / rms (deg) | position err max / rms / last-20 s mean (m) | yaw diff max | verdict |
|---|---|---|---|---|---|---|---|---|---|
| w0 | 0 | 0.6 / 0.2 | 0.611 | 0 | 0.607 / 0 | 4.7 / 3.8 | 0.56 / 0.43 / 0.43 | 0.00 | pass |
| b3 | 3 belly | 15.1 / 12.9 | 0.657 | 0 | 0.545 / 0 | 3.0 / 2.8 | 1.98 / 0.64 / 0.40 | 0.02 | pass |
| b5 | 5 belly | 31.5 / 29.3 | 0.711 | 0 | 0.488 / 0 | 2.2 / 1.9 | 6.59 / 4.93 / 4.52 | 0.03 | **marginal** (position) |
| b7 | 7 belly | 44.1 / 42.4 | 0.799 | 0 | 0.502 / 0 | 1.5 / 1.3 | 13.5 / 11.8 / 11.4 | 0.03 | **fail** (lean) |
| e3 | 3 edge | 4.8 / 3.7 | 0.648 | 0 | 0.569 / 0 | 4.2 / 3.6 | 0.43 / 0.39 / 0.41 | 0.01 | pass |
| e5 | 5 edge | 12.3 / 10.2 | 0.713 | 0 | 0.502 / 0 | 2.1 / 1.8 | 1.21 / 0.45 / 0.42 | 0.01 | pass |
| e7 | 7 edge | 21.3 / 18.8 | 0.809 | 0 | 0.408 / 0 | 1.3 / 0.6 | 3.09 / 1.4 / 1.14 | 0.01 | pass |
| d3 | 3, 45 deg | 9.2 / 7.6 | 0.661 | 0 | 0.517 / 0 | 4.8 / 3.5 | 1.13 / 0.45 / 0.36 | 0.14 | pass |
| d5 | 5, 45 deg | 23.8 / 20.0 | 0.739 | 0 | 0.342 / 0 | 8.7 / 4.7 | 3.83 / 2.12 / 1.79 | 0.37 | **marginal** (yaw) |
| d7 | 7, 45 deg | 47.3 / 41.9 | 0.900 | 2.35 (0.35) | 0.150 / 5.65 | 67.3 / 33.7 | 11.3 / 10.1 / 10.0 | 0.70 | **fail** (yaw lost) |
| t20_5 | 5, 20 deg off the tip | 13.5 / 10.5 | 0.745 | 0 | 0.359 / 0 | 9.4 / 3.9 | 1.51 / 0.49 / 0.36 | 0.35 | **marginal** (yaw) |
| t20_7 | 7, 20 deg off the tip | 47.2 / 40.4 | 0.900 | 2.30 (1.55) | 0.150 / 2.0 | 117.3 / 68.5 | 14.6 / 12.1 / 12.5 | 0.81 | **fail** (yaw lost) |
| gb | 5 belly + 2 gust at +20 s | 34.0 / 29.6 | 0.725 | 0 | 0.429 / 0 | 2.1 / 1.9 | 6.55 / 4.84 / 4.37 | 0.04 | marginal (same offset) |
| ge | 5 edge + 2 gust | 17.1 / 10.4 | 0.776 | 0 | 0.423 / 0 | 2.2 / 1.9 | 1.27 / 0.43 / 0.43 | 0.01 | pass |
| tb | 5 belly, turbulence 1.0 m/s | 37.5 / 28.0 | 0.795 | 0 | 0.238 / 0 | 8.7 / 3.0 | 5.65 / 4.05 / 3.22 | 0.43 | **marginal**: lean over 36 deg 2.7 % of the time, yaw differential over 0.40 for 0.4 % (3 samples) |
| m137b | 5 belly, 1.37 kg | 29.3 / 27.2 | 0.751 | 0 | 0.520 / 0 | 2.5 / 2.2 | 5.78 / 4.10 / 3.71 | 0.03 | marginal (position) |
| m137e | 5 edge, 1.37 kg | 11.2 / 9.2 | 0.749 | 0 | 0.540 / 0 | 2.2 / 2.1 | 1.33 / 0.29 / 0.14 | 0.01 | pass |
| d7c16 | 7, 45 deg, **cant 16 deg** | 52.0 / 40.7 | 0.900 | 2.05 (0.55) | 0.150 / 2.5 | 71.8 / 29.3 | 13.7 / 11.3 / 12.0 | 0.73 | fail (yaw lost) |
| b5pos | 5 belly, `Q_P_NE_VEL_I` 1.5, `Q_P_NE_POS_P` 1.0 | 35.5 / 33.1 | 0.786 | 0 | 0.333 / 0 | 11.3 / 6.6 | 3.55 / 2.75 / 2.73 | 0.32 | tuning try, rejected (oscillates) |

Simulated hover time: 19 cases of about 100-110 s each, about 0.6 h in all (`R-PILOT` credit is A2's call: it is a custom plant, not the stock stage-A model). One seed per case; the turbulence run is one realisation.

## 3. Against the board's limits

- **Yaw authority.** This decides the 7 m/s cases. Authority is as sizing_a.py says (0.28 N m at 30 % thrust differential, matched offline), and the plant reproduces the sizing's 5 m/s, 20 deg-off-tip wind moment (steady differential 25 % of throttle against 40 % available = ratio about 1.6, the sizing's 1.57). But the **sizing's worst case is not the worst heading in this model**: at 45 deg and 5 m/s the differential peaks at 37 %, because the plate's normal force there is 4.3 times larger than at 20 deg off the tip while the centre-of-pressure shift (my taper, `EST`) has not shrunk as fast. At 7 m/s the moment (about 0.54 N m at 45 deg, `EST`) exceeds what the motors can give before they hit the 0.90 cap and the 0.15 floor, so the heading runs away to about 70 deg and settles there. Cant 16 deg (d7c16) adds about 10 % authority and does **not** rescue 7 m/s. B3 should treat this as an open aero input: the plate Cn(heading) and centre-of-pressure shift are the model's weakest numbers and the yaw verdict depends on them.
- **Lean <= `Q_A_ANGLE_MAX` less margin (45 - 5 = 40 deg).** Belly into wind: 5 m/s needs 29-31 deg (mean 29.3, max 31.5; gust 34; turbulence 37.5), margin 6-10 deg: pass. 7 m/s needs 42-44 deg: fail. Edge-on: 12 / 21 deg at 5 / 7 m/s. The wind-needed lean is physics (it did not change when the limit went from 30 to 45 deg), so **the limit must be set to 45 for belly-on hover**; 30 would clip a 5 m/s belly hover with no margin.
- **Saturation.** Nothing is at the 0.90 cap at 5 m/s in any heading (peak 0.74-0.80, i.e. 10-16 % output headroom, **on the sagged pack**; a fresh pack has more). The only cap time is in the two failing 7 m/s yaw cases (0.35-1.55 s per run, 2.0-2.35 s in total) together with motors on the floor (2.0-5.65 s): authority exhausted, not a thrust shortfall.
- **Yaw hold.** Error 1-5 deg at 3 m/s and 5 m/s belly/edge (rms 0.6-4); 9 deg peak at 5 m/s with the wind 20-45 deg off the tip. The 4-5 deg shown at zero wind (w0) is a slow yaw wander I did not isolate: rms 3.8 deg with no wind, so treat 4 deg as the noise floor of this test.
- **Position.** Edge-on holds within about 0.4 m (steady), belly-on at 3 m/s within 0.4 m, belly-on at 5 m/s settles 4.3-4.5 m downwind and does not close in 36 s (stock `Q_P_NE_*`, `Q_LOIT_ANG_MAX` 15): by K09-L's S3 line (95 % within 1 m) it fails. `Q_LOIT_ANG_MAX` 40 changed nothing; raising `Q_P_NE_VEL_I` to 1.5 and `Q_P_NE_POS_P` to 1.0 gave an oscillation (b5pos). I did not find the cause; it appears only when the needed lean is above about 25 deg (edge-on at 19 deg converged). Open tuning item, needs the real aircraft or a closer model of the loiter limit.

## 4. Parameter starting set: `redesign/qp/A/A.param`

Built from `K09L.param` R11. 163 names; loaded into this SITL build through `--defaults` with `check_names.py`: all accepted except the two board-only (`SERVO_BLH_BDMASK`, `SERVO_BLH_POLES`) and the six `Q_WVANE_*` sub-parameters, which the build only exposes when `Q_WVANE_ENABLE` is 1 (K09-L found the same); `AIRSPEED_MIN` is an integer parameter, now 15. Findings that changed the file:

| Finding in this build | A.param |
|---|---|
| **`Q_ANGLE_MAX` does not exist** (read back: absent); the hover lean limit is `Q_A_ANGLE_MAX` in degrees, stock 30 | `Q_A_ANGLE_MAX` 45. BOARD C2's wording should say this name |
| `Q_LOIT_ANG_MAX` stock 15, no effect on a 29 deg hold | left stock |
| Rate loops: A is a much smaller, lighter airframe than K09-L (2.6 kg gate) | roll/pitch P 0.25, I 0.25, D 0.004 (K09-L 0.08 / 0.08 / 0.002), yaw 0.40 / 0.04 as K09-L. Tuned only by hovering the EST plant; **bench starting values, not tuned gains** |
| Thrust table curve | `Q_M_THST_EXPO` 0.55 (fit, K09-L 0.65), `Q_M_THST_HOVER` 0.42 (learned: hover reads 0.61 output on the sagged pack), `Q_M_SPIN_MAX` 0.90 (sizing's cap), `Q_M_SPIN_MIN` 0.15 |
| Weathervane | `Q_WVANE_ENABLE` 0: K09-L turned the belly into the wind (D-152); BOARD C2 wants A edge-on, `Q_WVANE` has no heading offset, so edge-on must be a pilot or mission yaw. SITL says belly-on is the **worse** heading for lean and position, edge-on the better one for lean, with yaw the price off-axis |

K09-L lessons carried unchanged and **not re-tested for A in this round** (names read back only): transition switch (`Q_TAILSIT_RAT_FW` 12, `Q_A_ANGLE_BOOST` 0, THR hold; its S4c logic test is stage A and not airframe-specific, but A's pitch-over has not been run: C3 stays open), `Q_ASSIST_ALT` / `ANGLE` 0 and `Q_ASSIST_SPEED` 13, failsafes (`BATT_FS_LOW_ACT` 6 = QLAND in a hover mode, `RC_FS_TIMEOUT` 1.0, `FS_LONG_ACTN` 1), fence (a breach in a Q mode starts RTL = a pitch-over; mode switch refused during recovery), `PTCH2SRV_RMAX_UP/DN` 35 / 20 (a 45 deg bank at 15 m/s needs 26.5 deg/s up: covered; no structural basis for A yet), `Q_TAILSIT_DSKLD` 6.7, `INS_HNTCH_FREQ` 70 (hover 1P is 71-76 Hz). Battery: sizing says one 4S 2000 mAh pack, BOARD's working point says 2 x 2300; A.param uses 2000 and says so (open between C5 and C6).

## 5. What the bench and the yaw test must confirm

1. **Hanging yaw test (BOARD C1/M3, 4 flight motors, foam planform, 14-16 deg).** The SITL result rests on the authority matching sizing: 0.28 N m at +-0.10 throttle. Confirm yaw torque at 326 gf (`BENCH.md` pass line Q >= 55 N mm) **and** measure the whole authority curve to the 0.90 cap, because 7 m/s and the 45 deg heading consume all of it.
2. **Plate yaw moment against heading.** The decisive unknown is the wing's yaw moment vs wind heading (Cn and centre of pressure). Hang or tether the foam planform in a fan or a measured 5 m/s flow and read the yaw torque at 0, 20, 45, 70, 90 deg; SITL's numbers (about 0.18 N m at 20 deg and about 0.28 N m at 45 deg, 5 m/s, `EST`) are the lines to beat.
3. **A thrust stand at the sagged-pack condition** (sizing asks for it already): the plant's x0.767 factor decides the 10-16 % output headroom at 5 m/s.
4. **First tethered hover** records `Q_A_ANGLE_MAX` 45 lean in a 5 m/s breeze belly-on (expect about 29 deg), position hold against the 1 m line, and the yaw differential (should stay under 30 %); stop at once if one motor reaches 0.80 or the heading drifts past 10 deg.
5. **Rate and position gains** are SITL-model values; retune on the aircraft (autotune or by hand) before trusting any of section 3's yaw-error or position numbers.
6. Not covered by this round and still open: C3 pitch-over with elevon limit; elevon authority; takeoff and landing in wind; transition and back-transition on A's aerodynamics; motor-out; fin and mount vibration.

**Flight-card line SITL supports (EST, on this model only): hover wind <= 5 m/s steady, wing edge into the wind within about 20 deg; belly-on only for <= 3 m/s without pilot attention to position; no hover above 5 m/s steady in any heading.** The heading window around edge-on is not mapped (SITL has 70 and 90 deg only); the 45 deg and 70 deg cases are marginal at 5 m/s, so a window narrower than 20 deg may be needed.

## 6. Reproduce, and SIM-only overrides

```
set SCR=<folder with sitl\ArduPlane.elf + cyg*.dll and src\quadplane.parm>   # the 2026-11-13 scratch install of team/F4/sitl/RESULTS.md
%SCR%\venv\Scripts\python redesign\qp\A\sitl\run_case.py b5 wind=5 from=0 hold=40       # one case
bash redesign/qp/A/sitl/batch.sh ; bash redesign/qp/A/sitl/batch2.sh                      # all cases (about 2 min each)
python redesign/qp/A/sitl/gather.py                                                        # table + verdicts
%SCR%\venv\Scripts\python redesign\qp\A\sitl\check_names.py                                # A.param name check
```

SIM-only overrides (not in `A.param`): `Q_M_PWM_TYPE` 0 (PWM 1000-2000, the plant reads PWM), `BATT_MONITOR` 0, `ARSPD_TYPE` 0, `ARMING_CHECK` 0 with a forced arm, `FENCE_ENABLE` 0, `THR_FAILSAFE` 0, mode-switch map and servo 5/6 limits, `SERIAL*` / `INS_HNTCH_*` / `COMPASS*` / `INS_POS*` lines skipped. Climb in QHOVER, hold in QLOITER (`FLTMODE6`). Wind starts 15 s after the aircraft passes 18 m; position error is measured from where it was when the wind arrived (the aircraft was still drifting a metre or two as the hold settled, so the first 8 s of each run are excluded from the statistics).
