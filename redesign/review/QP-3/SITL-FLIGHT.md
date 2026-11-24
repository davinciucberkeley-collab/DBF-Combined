# QP-3 SITL forward flight, concept A (F4 + B3, 2026-11-15)

Files written: `redesign/qp/A/sitl/` (new `a_aero.py`, `a_apc_data.py`, `run_fwd.py`, `fwd_sum.py`, `fwd_checks.py`, `jobq.py`, `jobs.txt`, `jobs2.txt`; `a_plant.py` extended with a `fwd` switch; `runs/<tag>/case.fwd.csv`, `result.json`, `sum.json`) and `redesign/qp/A/A.param` (3 edits, section 7). No git. Nothing bought.
Labels: `EST` estimate (mine, flight test decides); `V` vendor / maker data; `—` unknown. Every number below is from `runs/*/sum.json` or the closed-form `fwd_checks.py` on this machine. ArduPlane 4.7.3-beta1 SITL (JSON backend, same binary as `SITL.md`), `A.param` with the QP-2 SIM-only overrides, plus `ARSPD_TYPE` 100 (SITL airspeed from the plant). 59 runs, 2.46 h simulated, at most 4 instances at a time. Mass 1.381 kg (the "1.38 kg" predicted case) and 1.50 kg (gate); pack in the **sag state** (rest 14.92 V = 3.73 V/cell, pack R 0.030 ohm, thrust x0.97 hot) unless stated.

## Verdict

**The tailsitter flies the whole sequence on this model: transition, cruise at 17 m/s, back-transition, landing, takeoff and every hover failsafe pass. Two things are not clean: (1) `THR_MAX` 60 in the old `A.param` cannot hold 17 m/s (fixed here, 80); (2) the model is gentler than the K09-L B3 analysis in the transition, so the transition rating rests on an EST aero model whose key coefficients (post-stall moment, elevon effectiveness, prop in cross-flow) nobody has measured.** Motor-out is fatal in hover, as declared. Ratings use the pass lines in section 1 (mine, EST).

## 1. What the plant now models (all `EST` unless a source is named)

`a_plant.py cfg fwd=1` (default 0 = the unchanged hover plant; regression: 5 m/s from 45 deg, arm 1.2, cant 16, 1.23 kg gives lean 23.0, yaw 6.8, differential 0.281 against WIND.md 23.1 / 6.8 / 0.28).

| Item | Model | Source |
|---|---|---|
| Wing | S 0.22 m2, b 0.90, c 0.245, AR 3.68; lift slope 3.74 /rad (Helmbold); attached CL soft-clipped at CLmax 0.75; stall blend at 17 deg into a plate branch (hover plant's Cd 2.0 cross-flow, plus a 0.55 normal-force plateau so it is a soft stall); CD0 0.0356 and e 0.8 calibrated to L/D 7.19 at CL 0.352 | S, b, c: SIZING-A; CLmax, L/D: MISSION s1; blend, plateau, e: EST |
| Result | Vs 11.84 / 12.34 m/s at 1.381 / 1.50 kg (MISSION 11.70 / 12.19; +1.2 % is rho 1.225 against 1.20), 1.3 Vs 15.39 / 16.04; L/D 7.13 / 7.38 at 17 m/s | `a_aero.py`, `fwd_checks.py` |
| Pitch | AC 0.065 c behind the CG (SM 6.5 %), Cm0 +0.015 (reflexed section), Cmq -1.0, plate force at mid-chord (gives the post-stall nose-down) | MASS-GATE (SM); rest EST |
| Elevons | not in REQUIREMENTS-A or SIZING-A (only "2 elevons"), so: chord 25 %, span 0.10-0.40 m each side, area 0.0368 m2 both, tau 0.5, CL_delta 0.31 /rad, stops +-25 deg, 300 deg/s, lag 0.04 s, effectiveness 0.30 in separated flow; full 1000-2000 us = the +-25 deg stops; no prop-wash credit (props are 0.156 m above and below the wing plane, gap about 0.04 m; sensitivity `slip` run) | K09-L "25 deg travel" scale; rest EST |
| Fins | 2 x 0.36 x 0.12 m at 0.215 m aft, lift slope 2.5 /rad (AR 3, wing as end plate) then plate; yaw rate in the local velocity | SIZING-A geometry; slope EST |
| Prop and motor | APC 9x4.5MR **PER3 data file read 2026-11-15** (https://www.apcprop.com/files/PER3_9x45MR.dat; Ct, Cp vs J at 4k / 6k / 8k / 10k rpm in `a_apc_data.py`), MN2212 KV780, Rm 0.173, I0 0.5 A; thrust x0.93 (prop_a.py R3 derate) x0.97 download; windmilling beyond the table held at J = 1; `Q_M_SPIN_MAX` 0.90 comes from the FC | V (APC); Kv, Rm: SIZING-A V; I0, J>1: EST |
| Check | static 402 gf per motor at 1.50 kg and cant 16 reproduces prop_a.py; at 17 m/s level flight needs duty 0.62 (fresh) to 0.70 (sag), 144-147 W electric at 1.50 kg | `fwd_checks.py`, below |
| Not modelled | prop thrust change in cross-flow (the transition's big unknown), prop wash on wing, rotor H-force, a failed motor's windmill drag, battery voltage drift, airspeed noise, real servo linkage and free play | |

Pass lines (mine, EST, change them if the board has others): transition: elevon pitch use <= 0.60 of 15 deg (B3 K09-L: 25 deg travel less 10 deg kept), no run at the 0.90 cap > 1 s, no motor >= 0.85 for more than 1 s, peak altitude < 110 m from a 50 m start (fence), climb < 60 m (B3 `CL-B3-TRANS-CLIMB`), 1.3 Vs within 15 s, stable cruise after; landing: sink <= 1.2 m/s (design case 12 g on 6 mm crush), no tip-over; takeoff: lean <= 40 deg; failsafes: QLAND <= 3 s in hover (A-P19).

Elevon sign: of the four sign combinations for servo 5 / 6 only (5: +, 6: -) held roll (others rolled or saturated within 10 s). The `SERVO5_REVERSED` 1 / `SERVO6_REVERSED` 0 pair is K09-L's; **the bench must confirm that servo 5 and 6 move mirrored for a roll command and nose-up gives trailing edge up on both.**

## 2. Forward transition (entry procedure: held throttle, 1.0 s pre-climb in QSTABILIZE, then FBWA; hold 3 s after "Transition FW done", then CRUISE)

Entry throttle = static T0/W at the window centre of D184 (low edge 1.33, high edge 0.80 x T/W at the 0.90 cap; sag state): **1.44 at 1.381 kg, 1.38 at 1.50 kg**, set as a stick PWM through the A.param throttle curves (about 1790-1800 us at the SITL-learnt `Q_M_THST_HOVER` 0.46-0.51). Start 50 m, hover first in QLOITER with the wind on.

| Mass | Wind (m/s, from) | T0/W | alt gain at handover / peak gain (m) | peak alt (m) | handover V (m/s) | t to 1.3 Vs (s) | pitch use (of 15 deg) | elevon peak (deg) | u max | s at 0.90 cap | back-transition: balloon above switch alt (m) / s at cap | rating |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.381 | 0 | 1.44 | 35.0 / 38.2 | 89.1 | 13.6 | 7.1 | 0.52 | 8.1 | 0.783 | 0.0 | 7.7 / 0.00 | pass |
| 1.381 | 3 head | 1.44 | 35.3 / 38.7 | 89.3 | 13.6 | 7.1 | 0.52 | 8.0 | 0.800 | 0.0 | 7.6 / 0.00 | pass |
| 1.381 | 5 head | 1.44 | 35.1 / 38.3 | 88.9 | 13.7 | 7.0 | 0.52 | 7.9 | 0.832 | 0.0 | 7.6 / 0.00 | pass |
| 1.381 | 3 tail | 1.44 | 35.6 / 38.8 | 89.4 | 13.7 | 7.1 | 0.52 | 8.0 | 0.800 | 0.0 | - | pass |
| 1.381 | 5 tail | 1.44 | 35.4 / 38.6 | 89.4 | 13.7 | 7.1 | 0.50 | 7.7 | 0.833 | 0.0 | - | pass |
| 1.381 | 3 cross | 1.44 | 36.3 / 39.5 | 90.2 | 13.7 | 7.2 | 0.54 | 8.2 | 0.787 | 0.0 | - | pass |
| 1.381 | 5 cross | 1.44 | 34.3 / 37.5 | 88.2 | 13.7 | 7.0 | 0.52 | 8.2 | 0.825 | 0.0 | - | pass |
| 1.50 | 0 | 1.38 | 33.2 / 35.9 | 87.1 | 13.9 | 7.5 | 0.55 | 8.6 | 0.779 | 0.0 | 5.8 / 0.55 | pass |
| 1.50 | 3 head | 1.38 | 32.1 / 34.8 | 85.8 | 13.7 | 7.4 | 0.54 | 8.2 | 0.817 | 0.0 | 5.7 / 0.50 | pass |
| 1.50 | 5 head | 1.38 | 31.9 / 34.6 | 85.6 | 13.7 | 7.4 | 0.52 | 7.9 | 0.849 | 0.0 | 5.8 / 0.50 | pass |
| 1.50 | 3 tail | 1.38 | 32.2 / 34.8 | 85.8 | 13.8 | 7.5 | 0.53 | 8.0 | 0.802 | 0.0 | - | pass |
| 1.50 | 5 tail | 1.38 | 31.2 / 33.8 | 84.9 | 13.8 | 7.4 | 0.53 | 8.1 | 0.850 | 0.0 | - | pass (a motor at 0.85 for 0.05 s) |
| 1.50 | 3 cross | 1.38 | 33.4 / 36.1 | 87.2 | 13.9 | 7.5 | 0.55 | 8.4 | 0.805 | 0.0 | - | pass |
| 1.50 | 5 cross | 1.38 | 31.8 / 34.5 | 85.6 | 13.7 | 7.4 | 0.54 | 8.3 | 0.837 | 0.0 | - | pass |

Reading: the aircraft **climbs 31-40 m** during the pitch-over (no altitude loss in any case), hands over at 13.6-13.9 m/s (B3 line 12.94), reaches 1.3 Vs 7.0-7.5 s after the mode change, peak altitude 85-90 m (fence 110, climb limit 60), settles at 17.0-17.3 m/s in CRUISE with roll < 2 deg. Wind 0-5 m/s changes nothing by more than 3 m of altitude because the pitch-over is over in 7 s. MISSION s2 assumed "about 31 m" of climb: the 1.50 kg runs sit at 31-36 m, the 1.381 kg runs 34-40 m. No motor reached the 0.90 cap in the transition; the peak 0.85 is the 1.50 kg tail / head 5 m/s case.

Sensitivities (1.50 kg, no wind unless stated; T0/W is the static ratio at the stick):

| Run | T0/W | alt gain (m) / peak alt (m) | handover V | pitch use | alpha max (deg) | note |
|---|---|---|---|---|---|---|
| below the window | 1.20 | 13.8 / 65.0 | 12.3 | 0.45 | 31.8 | passes but handover under 12.94 and the wing goes to 32 deg alpha: **marginal** |
| K09-L literal 1.285 | 1.285 | 30.9 / 82.1 | 13.1 | 0.54 | 12.7 | pass; note 1.285 is below A's 1.33 low edge and still flew |
| low edge | 1.33 | 33.1 / 84.4 | 13.2 | 0.53 | 10.7 | pass |
| high edge | 1.42 | 39.6 / 90.9 | 14.2 | 0.50 | 9.9 | pass |
| above the window | 1.60 | 50.5 / 101.7 | 15.7 | 0.52 | 10.1 | pass, 8 m under the fence |
| no pre-climb | 1.33 | 3.9 / 55.2 | 11.9 | **0.91** | 45.1 | **marginal**: use 0.91, alpha 45 deg, handover below 12.94, a motor touches the cap (0.05 s) |
| elevon travel x0.6 (same deflection needs 1.7x the command) | 1.33 | 34.1 / 85.2 | 13.5 | 0.52 | 10.0 | pass: command headroom is not the limit |
| prop-wash credit on elevons (slip 1.0) | 1.33 | 33.2 / 84.5 | 13.2 | 0.51 | 10.8 | no change |
| tail 5 m/s, low edge | 1.33 | 31.3 / 82.3 | 13.3 | 0.51 | 12.9 | pass |
| head 5 m/s, high edge | 1.42 | 37.5 / 88.4 | 13.9 | 0.50 | 63.4 (in the hover tilt) | pass, u max 0.863 |
| 5 m/s cross + 3 m/s gust peaking 2 s after FBWA, 1 m/s turbulence | 1.33 | 32.8 / 83.7 | 14.7 | 0.56 | 30.1 | pass (B3 gust line <= 1.0) |
| **fresh pack, same stick as the sag runs** (no voltage compensation in SITL) | 1.57 | 48.1 / 99.4 | 15.0 | 0.44 | 8.9 | pass, **11 m under the fence**: the real FC compensates with `Q_M_BAT_VOLT_*`; still, a start above 50 m would not pass |

So the pre-climb is what keeps use below the 0.60 line, and the fence margin from a 50 m start is 8-11 m when the throttle is high. **A start at 50 m is the maximum; a start at 60 m fails on a fresh pack.** Window width: every ratio from 1.285 to 1.60 passes; below about 1.25 the handover speed and alpha degrade. The B3 K09-L result that the window is about +-4 % wide does not appear here: this model has no post-stall moment peak taken from a measured section, so I do **not** read this as proof the window is wide. It is a pass on this model.

## 3. Back-transition, descent and landing

Back-transition from CRUISE: switch to QLOITER (`FLTMODE6`), A.param `Q_TAILSIT_RAT_VT` 30, `Q_TAILSIT_THR_VT` 55. It pitches up in 4-6 s, "Transition VTOL done, timeout", airspeed 17 to 3 m/s in about 8 s, and balloons **5.7-5.8 m (1.50 kg) / 7.6-7.7 m (1.381 kg)** above the switch altitude. Motors reach the 0.90 cap for **0.50-0.55 s at the gate mass** (0.45 s at 0.85+ at 1.381 kg, no cap): inside the 1 s line, **marginal at the gate**. Into 5 m/s the aircraft stands belly-on for the first seconds: lean 26-29 deg (agrees with SITL.md 29 deg).

Edge-on rule (D-184): after the 5 m/s back-transition a yaw stick of 0.82 s (about 110 deg/s) turned the belly 89-90 deg, then QLAND from 82-88 m (QLAND descent 1.2 m/s, 0.3 m/s below 6 m). With yaw 1.3 s it overshot to 143 deg and the lean rose to 30 deg: the pilot needs the heading cue, not a timed stick.

| Case | Mass | Wind (m/s, from) | sink, peak last 1 s (m/s) | lean at touch (deg) | lateral speed at touch (m/s) | drift from QLAND start (m) | tipped | rating |
|---|---|---|---|---|---|---|---|---|
| landing from a hover at 20 m, edge-on, 1 m/s turbulence | 1.381 | 5, 90 | 0.30 | 9.5 | 0.32 | 1.8 | no | pass |
| same | 1.50 | 5, 90 | 0.32 | 12.1 | 0.45 | 1.5 | no | pass |
| belly-on, 0.5 m/s turbulence | 1.381 | 3, 0 | 0.31 | 5.0 | 0.16 | 1.8 | no | pass |
| same | 1.50 | 3, 0 | 0.30 | 5.3 | 0.40 | 1.3 | no | pass |
| after back-transition into wind, belly-on | 1.381 / 1.50 | 3, 0 | 0.30 / 0.30 | 11.3 / 10.3 | 0.11 / 0.12 | 0.8 / 0.7 | no | pass |
| after back-transition, yawed edge-on | 1.381 / 1.50 | 5, 0 (belly yawed 90) | 0.30 / 0.31 | 9.3 / 5.0 | 0.00 / 0.16 | 0.3 / 0.3 | no | pass |

Sink is 0.3 m/s against the 1.2 m/s design case (4x margin; QLAND is not the hard-landing case). Lean at touch 5-12 deg is the wind lean, static tip-over 33 deg `EST`. The contact model is four spring-damper fin tips with friction 0.6: it says nothing about foam crush, fin bending or a gust at touch (not run; A-P8 gust <= 8 m/s survive-and-land is **not** covered here).

## 4. Takeoff in 5 m/s (QLOITER, wind on before arming)

| Mass | Wind from | liftoff after throttle (s) | to 12 m (s) | lean max (deg) | drift at 12 m (m) | u max | heading change (deg) | rating |
|---|---|---|---|---|---|---|---|---|
| 1.381 | 90 (edge-on, the rule) | 3.0 | 9.9 | 11.8 | 5.2 | 0.74 | 0.8 | pass |
| 1.50 | 90 | 3.2 | 10.3 | 11.4 | 4.7 | 0.77 | 0.7 | pass |
| 1.381 | 0 (belly-on, outside the 3 m/s rule) | 3.0 | 9.9 | 17.9 | 12.3 | 0.70 | -1.2 | informational: lean 18 deg, 12 m downwind |
| 1.50 | 0 | 3.2 | 10.1 | 17.3 | 11.7 | 0.73 | -1.8 | informational |

No sliding or tipping before liftoff, no heading slip. Drift of 5 m at 12 m is the QLOITER settling; belly-on moves the aircraft 12 m.

## 5. Failsafes (A.param as loaded; trigger by `BATT_LOW_MAH` 5975 in flight as in K09-L S8, `SIM_RC_FAIL` 1 with the overrides stopped)

| Case | 1.50 kg | 1.381 kg | rating |
|---|---|---|---|
| Battery low, hover 51 m | QLAND at once ("Battery 1 is low"), lands in 62.5 s, sink 0.28 m/s | QLAND at once, 61.3 s, 0.23 m/s | pass (`BATT_FS_LOW_ACT` 6) |
| RC loss, hover | QLAND 1.2 s after the last frame ("RC Short Failsafe: switched to QLand"), 63.7 s to land | 1.2 s, 62.4 s | pass (A-P19 <= 3 s) |
| Battery low, cruise 17 m/s at 86 m | mode 25 (loiter to altitude, then QLAND): QLAND after 25.8 s at 50.7 m, back-transition, lands 95.2 s after the trigger; it flew 93 m beyond the trigger point | QLAND after 27.0 s, lands 96.9 s | pass on behaviour; **marginal on range**: a 201 m racetrack far point plus 93 m is 294 m, over the 250 m fence (SITL fence off; my test flew a straight line to 343 m before the trigger, so the absolute 417 m is the test, the +93 m is the failsafe) |
| RC loss, cruise | short failsafe circles, RTL 4.2 s later (`FS_LONG_TIMEOUT`), approach, "Starting VTOL land approach path", QRTL, lands at home (0 m); one "VTOL Overshoot yerr=113" message | RTL at 4.0 s, same path | pass, **marginal**: the approach overshoots once |
| Motor 1 out, hover | tumbles, inverted at touch after 5.5 s at 9.7 m/s (sink 8.7) | 6.1 s, 17.8 m/s | **fatal, expected (A-P20)**; "Potential VTOL Thrust Loss" 2.0 s after the failure |
| Motor 1 out, cruise | level flight on 3 motors for 25 s: pitch 4-7 deg, roll < 5 deg, u max 0.75 (model: the dead rotor has no windmill drag, so optimistic) | same, u max 0.74 | survivable in the model only until the pilot or a failsafe needs hover |
| Motor 1 out in cruise, then QLOITER (back-transition on 3 motors) | pitch-up completes, tumbles, inverted at touch 36.6 s later, 8.1 m/s | inverted, touch 31.8 s after (0.7 m/s at the instant of contact, the aircraft landed inverted) | **fatal**: cruise motor-out must not be followed by a Q mode; the flight card needs "after a motor loss in cruise do not switch to a Q mode" (a belly or glide landing was not simulated) |

A.param has no failsafe that fires on a motor loss in cruise (ArduPilot only warns, "Potential VTOL Thrust Loss"; no thrust-loss option is set in the file). Declare, do not mitigate: 6 rotors are outside $2,000.

## 6. A.param name check

`check_names.py` (all 157 lines loaded unfiltered through `--defaults`): **155 accepted, 2 unknown (`SERVO_BLH_BDMASK`, `SERVO_BLH_POLES`, board-only as before), no value differs.** Done after the `THR_MAX` edit, before the `SCALING_SPEED` edit (a plain existing name). The transition cases above also loaded it with the flight overrides: `Q_TAILSIT_RAT_FW`, `Q_TAILSIT_RAT_VT`, `Q_TAILSIT_THR_VT`, `Q_A_ANGLE_BOOST` 0 read back in the earlier QP-2 pass and behaved as set (held throttle through the pitch-over, "Transition FW done" 6.4-6.6 s after FBWA).

## 7. A.param changes (done in the file)

1. **`THR_MAX` 60 -> 80.** At 60 the cruise throttle is duty 0.60: the aircraft settled at 15.3 m/s and sank 1 m/s (first smoke run, 1.50 kg, sag), never reached 1.3 Vs (15.85) after the transition. The model needs duty 0.62 (fresh) to 0.70 (sag) for 17 m/s level (144-147 W, 1.50 kg; MISSION 161-170 W `EST`, so the model is 10 % cheaper), so 80 leaves 0.10 duty. The old comment ("0.60 = ... above the 122 W planning cruise") was for the 9545 and 15 m/s. With 80, CRUISE held 17.0-17.3 m/s in every run.
2. `SCALING_SPEED` 15 -> 17 (cruise speed; the 15 was left over). Not isolated in SITL.
3. Comment only: the entry procedure for A (T0/W 1.33-1.42 at the sag state, stick about 1790-1800 us at the SITL-learnt hover throttle; K09-L's 1.285 x hover is below A's low edge; pre-climb 0 gives use 0.91).

Not changed: `Q_TAILSIT_RAT_FW` 12, `Q_TAILSIT_ANGLE` 70, `Q_ASSIST_SPEED` 13, `AIRSPEED_MIN` 16 (1.3 Vs 15.85 at the gate: ok), failsafe actions, fence 250 / 110. Open for the board: the 250 m fence against the cruise-battery failsafe (+93 m).

## 8. What only flight test can confirm

1. **Prop thrust and power in forward flight and in cross-flow during the pitch-over** (APC static-to-J data is wind-tunnel at small angles; the aircraft sees the disc at 90 deg to the flow). The whole transition depends on T(V, angle).
2. **Post-stall wing and elevon behaviour from 90 deg to 15 deg alpha**: the nose-down moment peak (B3 K09-L bound the entry with it), CLmax 0.75, the soft-stall plateau, elevon effectiveness in separated flow (0.30 `EST`), hinge-moment coefficient (peak 0.0585 N m at 18 m/s, 25 deg against 0.167-0.235 N m of servo, ratio 2.9 `EST`).
3. Cruise power and the 17 m/s duty (144-154 W in the model against 161-170 W `EST` in MISSION) and the thrust at the sag state: sets THR_MAX and the battery gate.
4. Elevon servo direction and travel (section 1), free play, and whether full 1000-2000 us equals the 25 deg stops. Roll rate: closed form 95 deg/s at +-8.7 deg differential at 17 m/s (A-P11 needs 90): `EST`.
5. Cn_beta: 0.235 /rad from the fins alone (A-P15 needs 0.03), the wing's contribution unknown.
6. The back-transition altitude balloon (5.7-7.7 m) and the 0.5 s at the cap at the gate mass; the exact yaw-to-edge-on cue.
7. Landing: crush, tip-over with a gust at touch (A-P8 8 m/s), fin-tip friction on real surfaces; takeoff slip on wet grass.
8. Failsafe geometry in cruise (loiter-to-QLAND +93 m, RTL approach overshoot), EKF with real wind and a real pitot, RC link behaviour with the real receiver.
9. Hinge, elevon and fin vibration at 70 Hz and the notch (not in the plant).
10. Everything with stock FW gains: no `PTCH2SRV`, `RLL2SRV`, TECS tuning was done; SITL flew them as shipped.

## 9. Reproduce

```
set SCR=<folder with sitl\ArduPlane.elf + cyg*.dll and src\quadplane.parm>        # same install as SITL.md
%SCR%\venv\Scripts\python redesign\qp\A\sitl\run_fwd.py Tb_x5 case=trans mass=1.50 wind=5 from=90 hold=30 cruise_s=15 inst=0
%SCR%\venv\Scripts\python redesign\qp\A\sitl\jobq.py redesign\qp\A\sitl\jobs.txt     # the 34-run matrix, 4 instances; jobs2.txt = sensitivities, yaw, motor-out then QLOITER
python redesign\qp\A\sitl\fwd_sum.py Tb_x5                                           # metrics; python a_aero.py and fwd_checks.py: closed-form checks
```
Disk: `runs/` is about 1.2 GB (SITL logs and terrain per run); the `logs`, `terrain` and `eeprom.bin` folders can be deleted, `case.fwd.csv`, `result.json` and `sum.json` are what this page uses.


---

# Follow-ups (F4 / B3 with C1, 2026-11-15)

Files: `redesign/qp/A/sitl/` new `fu_level.py` (level speed, compensation, VD loads), `fu_cage.py` (flex-mode loop analysis; outputs `fu_cage_final.md`, `fu_cage.md`, `fu_cage_sweep.md`), `fu_back.py`, `fu_batt.py`, `jobs_fu*.txt`; `run_fwd.py` gained keys `cthr` (pin the cruise throttle) and `wv_after`; `A.param` edited. Runs `runs/Fu_*` (about 25 SITL runs, at most 4 at a time, SITL 4.7.3-beta1 as above; 1.50 kg, sag state unless stated). Labels as above: `EST` mine, `V` vendor, `—` unknown. No git, nothing bought. Name check after the edits: 159 names, 157 accepted, the same 2 board-only unknowns, no value differs.

## Ratings

| # | Item | Result | Rating |
|---|---|---|---|
| 1 | THR_MAX 80 against VH / VD | 80 gives 22.0 m/s level on a fresh pack = VD 22 (VH limit 17.6). **Fix: THR_MAX 68 with the FWD_BAT compensation already in the file, VD 24 (C1 re-check done)** | pass `EST` |
| 2 | Cage flex modes in the rate band | the old gains are unstable or at gain margin 1.0 on pitch; new gains + FC on the spar pass (min GM 2.1-2.8); **FC on the cage hub fails** | pass **only with the FC on the spar**; yaw PM 34 deg marginal |
| 3 | Back-transition at the cap | `Q_TAILSIT_RAT_VT` 24: no cap (0 s) at 0 and 5 m/s head wind; crosswind 5 m/s still 2.3 s | pass head wind; **marginal crosswind** |
| 4 | Cruise battery failsafe range | outward 70 -> 49 m with R 40; with a 200 m leg 200 m outward / 245 m any-direction against the 250 m fence | pass outward, marginal on the conservative bound |
| 5 | Edge-on heading cue | `Q_WVANE_ENABLE` 3 + `Q_WVANE_GAIN` 1: turns to 86 deg edge-on by itself, holds it to the ground | pass in SITL (calm); needs the card step below |

## 1. THR_MAX and VH / VD

The FC passes THR_MAX straight to the motor duty: SITL pinned cruise (`Fu_t80`, `Fu_t60`, fresh 16.8 V) read duty 0.800 and 0.600. Closed form (`fu_level.py`, same a_aero + APC model as the plant; level = lift W, 4 x thrust x cos 16 = drag at trim alpha) reproduces the SITL speeds within 1-2 % (80 fresh: 22.0 closed form, 21.9 m/s measured in a 3.8 deg climb; 60 fresh: 16.5 against 16.6).

| THR_MAX (with FWD_BAT 16.8 / 13.2 V) | ceiling duty fresh / 14.92 V rest / 13.2 V rest | level speed 1.50 kg (m/s) | level speed 1.381 kg | climb at 17 m/s 1.50 kg (m/s) |
|---|---|---|---|---|
| 80 (before) | 0.80 / 0.90 / 1.00 | **22.0** / 21.8 / 21.2 | 22.0 / 21.8 / 21.2 | +8.8 / +8.0 / +6.8 |
| 70 | 0.70 / 0.79 / 0.89 | 19.3 / 19.1 / 19.0 | 19.3 / 19.2 / 19.1 | +3.8 / +3.4 / +3.1 |
| **68 (now)** | 0.68 / 0.77 / 0.87 | **18.7** / 18.6 / 18.5 | 18.8 / 18.7 / 18.5 | +2.8 / +2.5 / +2.2 |
| 66 | 0.66 / 0.74 / 0.84 | 18.2 / 18.1 / 17.9 | 18.3 / 18.1 / 18.0 | +1.9 / +1.6 / +1.4 |
| 64 | 0.64 / 0.72 / 0.82 | 17.6 / 17.5 / 17.4 | 17.7 / 17.6 / 17.5 | +1.0 / +0.7 / +0.6 |
| 60 (original) | 0.60 / 0.68 / 0.76 | 16.5 / 16.4 / 16.3 | 16.6 / 16.4 / 16.4 | -0.8 / -0.9 / -1.0 |

17 m/s needs duty 0.618 fresh, 0.701 at 14.92 V, 0.797 at 13.2 V (1.50 kg). Answers:
- **At 80 the fresh-pack level speed is 22.0 m/s: it exceeds VH and equals VD (22).** C1 used VD 22 = 1.25 VC rounded (`structures_a.py`); the rule VH <= VD / 1.25 allows 17.6, and AIRSPEED_MAX is 18.
- No fixed THR_MAX works: 17.6 fresh needs <= 0.639, 17 on a sag needs >= 0.70. **FWD_BAT compensation** (`FWD_BAT_VOLT_MAX` 16.8 / `MIN` 13.2, already in the file) scales demand and THR_MAX by 16.8 V / resting voltage (K09-L, F4 closeout 2026-11-14), so the ceiling is the same motor terminal voltage on every pack; the maximum level speed is then the fresh one and falls a little on a sag. SITL with the battery monitor on (`Fu_sagpin`, `Fu_frpin`, THR_MAX 66): ceiling duty **0.750** at SIM_BATT_VOLTAGE 14.92 (closed form 0.743), **0.660** at 16.8; `Fu_sagcr` / `Fu_frcr` (TECS, THR_MAX 66): CRUISE held 17.2 m/s level at duty 0.705 sagged / 0.621 fresh.
- Why 68 and not the 17.6 limit (THR_MAX 63-64): at 64 the climb margin at 17 m/s is 0.6-1.0 m/s, and MISSION estimates the cruise power 10-15 % above this model (161-170 W against 144-147 W): a duty of 0.65 may be needed, so the 17.6 ceiling has no headroom. 68 keeps 0.06 duty above the cruise duty on every pack state.
- **C1 re-check at VD 24 (VH 18.8 x 1.25 = 23.5)**, same formulas as `structures_a.py` (`fu_level.py loads()`): gust 4 m/s at VD: 3.02 (2.85 at 22; stall line 3.6-4.0) **below the 3.4 manoeuvre limit that sizes the spar** (the 4 m/s gust reaches 3.4 only at VD 28.6); pitch-rate-limited n at 35 deg/s: 2.5; so spar, cage, rib and fin-root margins (iter2_margins: spar +2.73) **do not change**. Elevon hinge moment scales with V^2: 0.104 N m at 25 deg and VD 24 (0.0585 at 18 m/s), servo ratio 1.61 against 1.5 (A-P11) at the full stop, 2.7 at the 15 deg actually used; at VD 25 the full-stop ratio would be 1.48 (fails). `—` not checked: flutter (never computed for A) at 24 m/s, fin side loads at VD, wing-tip torsion; C1 to add them to the first-build checks. **Final values: `THR_MAX` 68, `FWD_BAT_VOLT_MAX` 16.8, `FWD_BAT_VOLT_MIN` 13.2, `TECS_CLMB_MAX` 2 (was 3; worst-state climb 2.2), structures VD 24.**

## 2. Cage flex modes (9-11 Hz and the rest of the rate band)

Method (`fu_cage.py`): the iteration-2 FE (`qp/A/structures/fe_a.py`, CFG of `iter2_run.py`, free-free, kd / nom / hi corners) gives every mode shape; motor-pair torque (x-forces, plus the 16 deg cant tangential components and the shaft reaction for yaw) -> body rate at the IMU node is the modal sum; the A.param rate loop (P, I, D, D filter, `INS_GYRO_FILTER` 2-pole, 40 ms motor lag as the plant, 4 ms delay, ArduPilot's 2.5 Hz yaw error filter) is closed around it and the closed-loop poles are computed. Worst case over 3 corners x zeta 0.3 / 1 % (a guess, `EST`) x thrust scale 0.77 / 1.0 / 1.25. FE rigid inertias 0.021 (pitch), 0.069 (roll), 0.061 (yaw) kg m2 (plant EST 0.03 / 0.05: same order).

What the FE modes are on the three control axes: **yaw 7.9 / 8.1 / 9.6 Hz (kd / nom / hi)** (cage rocking about the thrust axis on the bridge: this is the "9-11 Hz" mode), **pitch 12.1 / 12.4 / 14.8 Hz**, **roll 28.7 / 30.5 / 34.8 Hz**, each with a modal gain 0.7-1.1 times the rigid gain. The rigid crossover is 1.5-3.9 Hz, so the pitch mode is only 3-8 x above it.

`fu_cage_final.md` (36 loops per row; GM = factor on the loop gain before a right-half-plane pole; 1.00 = unstable somewhere):

| settings | axis | IMU at | min GM | unstable loops of 18 | rigid PM deg | crossover Hz |
|---|---|---|---|---|---|---|
| A.param before | pitch | spar centre | **1.00** | **4** | 50 | 3.9 |
| | roll | spar centre | 2.44 | 0 | 62 | 2.2 |
| | yaw | spar centre | 1.97 | 0 | 33 | 1.5 |
| | pitch / roll / yaw | **cage hub** | 1.00 | 4 / 17 / 15 | | |
| A.param now | pitch | spar centre | **2.76** | 0 | 56 | 2.6 |
| | roll | spar centre | 2.52 | 0 | 64 | 1.8 |
| | yaw | spar centre | 2.06 | 0 | 34 | 1.5 |
| | pitch | cage hub | 3.22 | 0 | 56 | 2.6 |
| | roll / yaw | **cage hub** | 1.00 | **12 / 15** | | |

Reading: the coupling is real. With the old settings the 12-15 Hz pitch mode peaks the loop gain at 6-9 (against 1) and the loop is unstable at zeta 0.3 % or +25 % thrust. The cause is lag: motor 40 ms, gyro filter 40 Hz and D filter 32 Hz put the mode beyond 180 deg. A notch did **not** help (a 13.5 Hz notch, 20-30 dB, BW 6-12 Hz left 8-12 of 18 loops unstable; it adds lag below its centre and cannot cover 12.1-14.8 Hz). Making the mode stiffer alone does not help either (15-40 Hz with the same gains: unstable, the mode just moves to more lag). What works is **less lag and less gain at the mode**.

Settings (all in A.param): `INS_GYRO_FILTER` 60 (was 40); `Q_A_RAT_PIT_P` 0.15 (0.25), `_D` 0.002 (0.004), `_FLTD` 40 (32), `_I` 0.25 unchanged; `Q_A_RAT_RLL_P` 0.20, `_D` 0.003, `_FLTD` 32 unchanged, `_I` 0.25; yaw unchanged. Hover wind check (rigid plant, 5 m/s from 45 deg, 1 m/s turbulence, 1.50 kg, `Fu_h0` old against `Fu_h1` new): lean max 23.3 / 24.4 deg, yaw error max 13.1 / 12.6 deg, position error rms 2.03 / 2.05 m, peak duty 0.859 / 0.854: no change.

**Hard requirement: the flight controller sits on the wing spar centre (C4's IMU node), not on the cage hub or pack tray.** With the IMU on the hub the yaw mode (8-10 Hz) and the roll mode are unstable at zeta <= 1 % with any gain set above; notches only reach GM 1.2-1.4 (yaw 8.5 Hz, BW 8 Hz, 25 dB; roll 31 Hz, BW 24 Hz, 30 dB). If the FC must go on the cage the yaw-torsion frequency would have to double (about 4 x the bridge torsion stiffness) and the roll mode rise above about 50 Hz, which breaks the rotor-order separation iteration 2 settled: do not. Also: yaw PM is only 33-35 deg with ArduPilot's default 2.5 Hz yaw error filter (independent of the cage); try `Q_A_RAT_YAW_FLTE` 4 if the hanging test shows yaw ringing (not tested). Bench: tap-test the built cage for the 8-15 Hz modes; if the first pitch mode is below 11 Hz, cut `Q_A_RAT_PIT_P` further. Flag, not changed: `INS_HNTCH_FREQ` 70 / BW 35 dates from the 9545 prop (1P 71 Hz); the 9x4.5MR hover 1P is 100-119 Hz (STRUCTURES), so the harmonic notch setting needs checking against the first IMU log.

## 3. Back-transition with the motors at the cap (1.50 kg, `fu_back.py`)

Baseline `Q_TAILSIT_RAT_VT` 30, THR_VT 55, no wind: 0.56 s at 0.90, balloon 5.8 m, 82 m of travel to 3 m/s.

| Variant | peak duty | s at cap (>= 0.895) | s >= 0.85 | balloon (m) | pitch-up to > 70 deg (s) | travel to 3 m/s (m) |
|---|---|---|---|---|---|---|
| 30 (baseline) | 0.90 | 0.56 | 1.02 | 5.8 | 6.2 | 82 |
| 24, no wind | 0.877 | 0 | 0.31 | 6.2 | 8.0 | 102 |
| 24, 5 m/s head | 0.812 | 0 | 0 | 5.4 | 7.8 | 58 (to 3 m/s not reached: wind) |
| 20, 5 m/s head | 0.845 | 0 | 0 | 5.1 | 9.0 | 68 (same) |
| 18, no wind | 0.833 | 0 | 0 | 4.8 | 9.8 | 126 |
| 18, 5 m/s head | 0.832 | 0 | 0 | 4.9 | 9.9 | 75 (same) |
| 24, 5 m/s **crosswind** (hover turned edge-on first) | 0.90 | **2.2-2.4** | 2.6 | 5.3-5.4 | 7.6 | 106 |
| 18 / 20, crosswind | 0.90 | 1.3 / 1.5 | 2.5-2.8 | 4.9-5.0 | 9-10 | 124-134 |
| THR_VT 40 (RAT 30) | 0.90 | 3.3 | 5.6 | 1.3 | 11.5 | 113 |
| entry at 15 m/s (AIRSPEED_CRUISE 15; the aircraft held 16.7) | 0.90 | 0.26 | 0.92 | 5.0 | 6.3 | 83 |

**Fix: `Q_TAILSIT_RAT_VT` 24.** The cap is the pitch-up rate demand, not the throttle: slower pitch-up gives no cap in 0 and 5 m/s head wind, balloon 5.4-6.2 m, 20 m more travel than at 30; 18 costs 44 m more travel for 0.04 less peak duty. **Leave `Q_TAILSIT_THR_VT` 55**: lowering it to 40 loses lift (lean 64 deg, 3.3 s at the cap). Entry speed is not the lever. **Procedure: switch to QLOITER from level cruise heading into the wind** (head wind, not crosswind); a crosswind back-transition at 5 m/s still holds the cap 1.3-2.4 s (marginal; 0.90 is 12.1 A phase, under the 13 A rating, but no control margin is left). Not re-run at THR_MAX 68: the back-transition throttle is `Q_TAILSIT_THR_VT`, not THR_MAX.

## 4. Cruise battery failsafe against the 250 m fence (`fu_batt.py`, `battC`)

Mechanism: `BATT_FS_LOW_ACT` 6 = loiter to `Q_RTL_ALT` 50 m about the trigger point, then QLAND (the back-transition travel is part of the excursion). Action 1 (RTL) is not an option: in a Q mode it starts a forward transition (K09-L; the SITL source `events.cpp` has no VTOL case in the RTL branch), so the lever is the geometry.

| Case (trigger at 87 m, 17 m/s) | to QLAND (s) / to touchdown (s) | max distance from trigger | outward along the track | energy trigger -> touchdown |
|---|---|---|---|---|
| before: R 60, RAT_VT 30 (`Fb_battC`) | 25.8 / 101 | 93 m | 70 m | 4.91 Wh |
| R 40, RAT_VT 30 (`Fu_c40`) | 27.0 / 103 | 80 m | 49 m | 4.98 Wh |
| R 40, RAT_VT 18 (`Fu_c40b`) | 27.7 / 103 | 124 m | 49 m | 4.91 Wh |
| **R 40, RAT_VT 24 (`Fu_f4`, as now)** | 28.3 / 105 | **94 m** | **49 m** | 5.03 Wh |

- **`WP_LOITER_RAD` 60 -> 40** (bank 36 deg at 17 m/s, stall 13.6 m/s against 15.85 minimum airspeed; the racetrack radius stays 51 m). The slower back-transition (24) gives back the saved distance in the any-direction number, so that stays at 94 m; outward is 49 m.
- Far point: the 300 m leg (far point 201 m) gives 250 m outward (at the fence) and 295 m any-direction. **Fly a 200 m leg** (lap 42 s, far point 151 m): **200 m** outward-heading and **245 m** for the conservative any-direction bound (the radial component cannot reach all of 94 m), against 250 m less `FENCE_MARGIN` 10 m. Flight-card change, written into MISSION.md s2; total cruise time unchanged. `FENCE_RADIUS` 250 and `FENCE_ALT_MAX` 110 unchanged.
- Energy: 5.0 Wh from trigger to touchdown against 9.4 Wh left at `BATT_LOW_MAH` 650 (1.9 x). `BATT_CRT_MAH` 345 is only 5.1 Wh: a backstop, not a margin. `BATT_LOW_MAH` 650 unchanged.
- Not changed: `BATT_FS_*_ACT`, `Q_RTL_ALT` 50 (raising it adds hover time at 1.2 m/s). Not covered: wind (SITL ran calm) and a trigger while turning at the far point.

## 5. Heading cue for edge-on

ArduPilot `Q_WVANE_ENABLE` has a **side-into-wind** mode (3; read from `AC_WeatherVane.cpp` Plane-4.7.2, https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/libraries/AC_AttitudeControl/AC_WeatherVane.cpp, 2026-11-15): the pitch lean from a belly-on wind is turned into a yaw until the wing edge faces the wind. QP-2 had weathervane off because mode 1 puts the belly into the wind. **`Q_WVANE_GAIN` defaults to 0 on Plane**, so ENABLE 3 alone does nothing (`Fu_wv`, heading unchanged for 55 s). With GAIN 1:

| Run | Result |
|---|---|
| `Fu_wv2`: hover 20 m QLOITER, 5 m/s from the belly, then QLAND | belly heading 0 -> -36 deg (6 s) -> -84 deg (12 s), held -82 deg to touchdown; lean 8.4 deg (25 deg belly-on); landed, no tip |
| `Fu_wv7`: head-wind back-transition (RAT_VT 24, peak duty 0.81, no cap), weathervane on 20 s later with `Q_WVANE_SPD_MAX` 2 | belly 1 -> 80 deg (+7 s) -> 86 deg; lean 9 deg through the 88 m descent; edge-on to touchdown (4 deg inside the +-10 deg rule) |
| `Fu_wv3` / `Fu_wv6`: weathervane on from the start | hover turns edge-on before the pitch-over, so the transition and back-transition are crosswind: 2.2-2.4 s at the cap (item 3) |
| `Fu_f3`: `Q_WVANE_ENABLE` -1 with `Q_WVANE_LAND` 3 | no turn (heading stayed 2 deg): this option set does not work here |

Final: `Q_WVANE_ENABLE` 3, `Q_WVANE_GAIN` 1, `Q_WVANE_SPD_MAX` 2 (A.param). It works only in position-controlled Q modes with the yaw stick centred for 2 s; a pilot yaw command overrides it. **Flight card:** before the pitch-over yaw the belly to the intended flight heading and go QLOITER -> QSTABILIZE -> FBWA within 2 s, so the weathervane never acts before the transition; after the back-transition leave the yaw stick centred and the aircraft turns itself edge-on in about 25 s and lands edge-on. Backup cues, not needed now: the GCS HUD wind arrow against heading; an analog OSD wind element (the BOM has no OSD or video link, `—`). A-P8a still says `Q_WVANE_ENABLE` 0: change it to "3 (side into wind)" at the next requirements edit (not edited here).

## 6. A.param diff (all in `redesign/qp/A/A.param`)

```
THR_MAX                 80   -> 68      (FWD_BAT_VOLT_MAX 16.8 / MIN 13.2 unchanged: required)
TECS_CLMB_MAX           3    -> 2
INS_GYRO_FILTER         40   -> 60
Q_A_RAT_PIT_P           0.25 -> 0.15    Q_A_RAT_PIT_D 0.004 -> 0.002    Q_A_RAT_PIT_FLTD 32 -> 40
Q_A_RAT_RLL_P           0.25 -> 0.20    Q_A_RAT_RLL_D 0.004 -> 0.003
Q_TAILSIT_RAT_VT        30   -> 24
WP_LOITER_RAD           60   -> 40
Q_WVANE_ENABLE          0    -> 3       Q_WVANE_GAIN (new) 1     Q_WVANE_SPD_MAX (new) 2
```
Other files: `qp/A/MISSION.md` s2 (200 m leg note). Structures VD 22 -> 24 is for C1 to carry into `structures_a.py` (loads above); not edited here.

## 7. What still needs the bench or flight

1. Cruise duty for 17 m/s (the model is 10-15 % cheaper than MISSION): measure on the thrust stand and the first cruise; if 17 m/s needs more than 0.65 fresh, raise THR_MAX and VD together (VD = 1.25 x VH; THR_MAX 70 needs VD 25 and fails the A-P11 hinge ratio at the full stop).
2. FWD_BAT uses the resting-voltage estimate: confirm the 0.66-0.75 duty read-back on the bench with a sagging pack (SITL used the instantaneous analog voltage).
3. FC position on the spar, tap test of the cage (8-15 Hz) and zeta (1 % is a guess); IMU log FFT in the tethered hover against the gyro filter and notch settings.
4. Crosswind and gusty back-transition above 5 m/s; battery failsafe geometry in wind.
5. Weathervane holding edge-on within 10 deg in turbulence: it is a feedback on lean, not a heading hold; SITL here was calm, `—` not simulated with gusts.

Reproduce: `python -I fu_level.py` (PYTHONPATH = sitl folder), `python -I fu_cage.py [sweep|final]`, `python -I fu_back.py <tag>`, `python -I fu_batt.py <tag>`; runs `jobs_fu.txt` .. `jobs_fu4.txt` with `jobq.py`; the `Fu_t*`, `*pin`, `*cr`, `Fu_h*`, `Fu_wv*` runs by hand with `run_fwd.py` / `run_case.py` and the `P:` overrides recorded in `runs/<tag>/A_sitl.parm`.
