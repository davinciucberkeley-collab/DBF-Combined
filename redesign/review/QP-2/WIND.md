# QP-2 WIND: yaw and lean levers, hover wind limit, schedule (concept A, B3 + F4 + H2, 2026-11-14)

Files written: this page, `redesign/qp/A/sitl/` (plant `a_plant.py` and `run_case.py` extended with `arm`, `wing_s`, `fin_s`, `inst`; `batch3.sh` to `batch7.sh`; `wsum.py`; `wind_limits.py`; `wind_dir.py`; `runs/w_*`, `runs/w4_*`; `results.jsonl`). No git.
Labels: `EST` estimate; `V` vendor page; `—` unknown. All SITL numbers are from `runs/*/result.json` (same plant, same ArduPlane 4.7.3-beta1 JSON-backend SITL, `A.param`, mass 1.23 kg, sagged pack x0.767 as in `SITL.md`). Wind rows come from `config-study/tiebreak/wind/data/rcmc1_*.txt` (read by `wind_limits.py`). 4 SITL instances in parallel, 48 new runs of 40-45 s of wind each (about 0.5 h of simulated hover in all; one seed per case unless stated).

## Verdict

1. **Yaw, not lean or thrust, is what limits A, and heading decides it.** Wing edge into the wind within about 10 deg (wind from 80-100 deg off the belly) passes at 5 m/s steady with today's hardware (yaw differential 0.12 at 80 deg). At 70 / 60 / 45 deg it is marginal (0.35 / 0.40 / 0.37 against a 0.30 line) and any real turbulence breaks it: with 1 m/s turbulence the unmodified aircraft swings its heading 19-22 deg even edge-on, 34 deg and a motor on the floor 1.85 s at 60 deg.
2. **Cheapest lever that works: motor arm x1.2 plus cant 16 deg** (about +15 g, about +$5, `EST`). Steady and +2 m/s gust cases then pass with margin over a +-20 deg heading window (differential 0.25-0.29 against 0.30; yaw error 6-8 deg), and turbulence yaw peaks fall from 19-34 deg to 11-15 deg. **That last number is still marginal against my 10 deg line**: no honest "pass" in turbulence at 5 m/s with these two levers alone.
3. **Weathervane does the wrong thing for A** (heading goes belly-into-wind). Spin cap, fin size and prop thrust do nothing at 5 m/s. Wing side area is the strongest lever but costs cruise (below).
4. **Recommendation: keep 5 m/s mean (not 4), edge-on within +-10 deg by pilot heading hold, arm x1.2 + cant 16 deg.** 4 m/s would cost 1-8 mornings of slip and buys only about 1 deg of yaw in turbulence. Schedule fits either way. The bench plate and yaw tests decide whether the 5 m/s card stands (section 5).

Pass lines used (`EST`, mine, to be changed by the board): steady and gust cases **yaw error <= 10 deg, differential (mean of motors 1,2 against 3,4 over mean throttle) <= 0.30** (K09-L S20) with 0.40 (sizing authority line) as the ceiling for peaks; no motor at the 0.90 cap for more than 1 s, none on the 0.16 floor for more than 0.5 s. Turbulence (sigma 1.0 m/s, tau 2 s, vertical 0.5x, my model, not `SIM_WIND_*`): yaw peak <= 10 deg pass, 10-15 deg marginal, > 15 deg fail. Position offset is reported, not gated.

## 1. Lever results, 5 m/s steady, 40 s logged, differential = diag spread max

Baselines from `SITL.md`: wind from 45 deg: lean 23.8, yaw err 8.7, differential 0.37; from 70 deg: 13.5, 9.4, 0.35; belly (0 deg): lean 31.5, hold offset 4.5 m.

| Lever (change) | 45 deg: lean max / yaw max / diff | 70 deg: lean / yaw / diff | 60 deg | belly 0 deg: lean / hold offset (last 20 s) | Reading |
|---|---|---|---|---|---|
| none (base) | 23.8 / 8.7 / **0.37** | 13.5 / 9.4 / **0.35** | 17.6 / 10.0 / **0.40** | 31.5 / 4.52 m | marginal at 45, 60, 70 |
| arm x1.2 (motors at y 0.228, z 0.156 m) | 23.3 / 7.9 / 0.31 | 13.3 / 8.0 / 0.29 | | 31.0 / 4.38 m | yaw -16 %; lean unchanged |
| cant 16 deg | 23.6 / 7.8 / 0.33 | 13.2 / 8.3 / 0.31 | | | yaw -11 % (`SITL.md` d7c16 at 7 m/s: no rescue) |
| **arm x1.2 + cant 16** | 23.1 / 6.8 / **0.28** | 13.0 / 6.6 / **0.25** | 16.6 / 7.5 / **0.29** | | passes 0.30 at 45, 60, 70 |
| wing side area x0.75 | 18.6 / 7.0 / 0.28 | 11.8 / 6.4 / 0.24 | 13.9 / 7.6 / 0.30 | 26.0 / 2.76 m | lean -2 to -5 deg, belly offset -1.8 m |
| wing x0.75 + arm + cant | 18.3 / 6.2 / 0.21 | 11.8 / 5.5 / 0.18 | 13.6 / 6.1 / 0.22 | 25.9 / 2.80 m | best, costs cruise |
| spin cap 0.95 (`Q_M_SPIN_MAX`) | 23.4 / 7.7 / 0.37 | 13.1 / 7.8 / 0.34 | | | no change: the case is not at the cap (peak output 0.74) |
| fin area x0.7 | 23.6 / 8.5 / 0.37 | 11.7 / 9.0 / 0.34 | | | no change: fins are 0.086 m2 against the 0.22 m2 wing |
| `Q_WVANE_ENABLE` 1 (wind from 45 deg) | 30.0 / **31.8** / 0.22 | | | | heading turns **toward belly-on**: lean 30, hold 4.7 m off. Wrong way for A |
| heading only, no hardware change: wind from 80 / 110 deg | | | | | 80: lean 11.9, yaw 3.8, diff **0.12**; 110: 12.6, 4.6, 0.31 (the plant is not symmetric about the tip) |

Not run: 7 m/s with the levers (the question is 5 m/s; arm + cant adds about 26 % yaw authority by the sizing formula, `EST`, which `SITL.md` showed was not enough at 7 m/s and 45 deg). One more case, wing x0.75 + arm + cant at **6 m/s from 45 deg**: lean 24.5, yaw 7.1, diff 0.29, no saturation, so these levers hold about 6 m/s steady, not 7.

### Gust and turbulence (the cases that decide pass or fail)

| Case (5 m/s, wind from) | Hardware | lean max | yaw err max / rms | motor floor time | diff max | Verdict |
|---|---|---|---|---|---|---|
| 80 deg, gust +2 | base | 16.2 | 8.4 / 2.4 | 0 | 0.36 | pass |
| 70 deg, gust +2 | arm + cant | 15.4 | 8.1 / 3.4 | 0 | 0.46 | pass (diff above 0.40 for a moment, no saturation) |
| 60 deg, gust +2 | arm + cant | 17.6 | 8.1 / 3.6 | 0 | 0.52 | pass on yaw, diff peak 0.52 |
| 60 deg, gust +2 | wing 0.75 + arm + cant | 15.4 | 7.0 / 3.4 | 0 | 0.39 | pass |
| 90 deg, turbulence | base (seeds 1, 2) | 21.0, 21.8 | **19.5, 19.8** / 4.4, 7.2 | 0.20, 0.15 s | 0.66, 0.54 | **fail** (> 15 deg) |
| 80 deg, turbulence | base | 20.9 | **22.2** / 5.5 | 0.10 s | 0.65 | **fail** |
| 60 deg, turbulence | base | 23.1 | **34.2** / 6.8 | **1.85 s** | 0.91 | **fail** |
| 90 deg, turbulence | arm + cant | 21.0 | 11.1 / 2.8 | 0 | 0.46 | marginal |
| 80 deg, turbulence | arm + cant | 20.6 | 11.0 / 3.4 | 0 | 0.46 | marginal |
| 70 deg, turbulence (seeds 1, 2) | arm + cant | 20.0, 22.8 | 11.7, 14.7 / 3.6, 4.7 | 0 | 0.54, 0.50 | marginal (seed 2 close to fail) |
| 60 deg, turbulence | arm + cant | 20.4 | 11.7 / 4.1 | 0 | 0.58 | marginal |
| 90 deg, turbulence | wing 0.85 + arm + cant | 21.0 | **8.5** / 2.4 | 0 | 0.39 | pass |
| 70 deg, turbulence (seeds 1, 2) | wing 0.85 + arm + cant | 19.7, 20.7 | 9.9, 12.4 / 3.3, 4.1 | 0 | 0.44, 0.44 | marginal (seed 2) |
| 70 deg, turbulence (seeds 1, 2) | wing 0.75 + arm + cant | 19.2 (seed 2) | 10.9 (seed 2) | 0 | 0.39 | marginal |
| 60 deg, turbulence | wing 0.75 + arm + cant | 18.5 | 8.0 / 3.0 | 0 | 0.42 | pass |
| 4 m/s, 90 deg, turbulence | base | 16.9 | 11.1 / 3.4 | 0 | 0.46 | marginal |
| 4 m/s, 70 deg, turbulence | base / arm + cant | 16.1 / 15.6 | 13.8 / 10.3 | 0 | 0.56 / 0.40 | marginal / marginal |
| 4 m/s, 60 deg, turbulence | arm + cant | 15.4 | 10.0 / 3.5 | 0 | 0.43 | marginal (at the line) |

Reading: turbulence sets the yaw excursion, almost independent of mean wind between 4 and 5 m/s (the 1 m/s swing in direction rotates the plate force). The motors never reach the 0.90 cap (peak 0.87) with any lever set; the failures are heading excursions and the base case touching the floor, not lost control. Arm + cant roughly halves the excursion (19.5 to 11.1 deg at 90 deg; 34 to 11.7 deg at 60 deg). Nothing tried gets every seed under 10 deg; the best (wing x0.75 to x0.85 plus arm and cant) is 8-12 deg. **The turbulence rows are one or two realisations of my own model**; treat the 10-15 deg band as "needs the aircraft".

## 2. What each lever costs (`EST`, mass table from `SIZING-A.md`; no CAD)

| Lever | Mass | Cost | Other claims it touches | Verdict |
|---|---|---|---|---|
| Arm x1.2 (motor cage 0.19 / 0.13 to 0.228 / 0.156 m) | +15 g (longer cage struts; cage line 120 g, `SIZING-A.md` mass table, scaled by the lengthened members) | +$3-5 (carbon tube and print) | box 1.25 x 0.55 x 0.45 m: motor+prop extent 0.35 m, inside the wing half-span 0.45 m, fits; yaw inertia up (plant includes it: Ixx 0.053 to 0.064, `EST`); cage mass and motor spacing re-do for the fin vibration check C-claim (cage not in the fin load path) | **take** |
| Cant 14 to 16 deg | 0 | $0 (printed mount) | thrust x cos: 0.970 to 0.961 (-0.9 %, T/W 1.9 to about 1.88); mount geometry must be redone, `T-B3-HOVER-YAW` hanging test must re-run; Q = rotor reaction part unchanged | **take** |
| Wing side area x0.75 (chord trim, span kept) | -55 g (`EST`: wing line 220 g x 0.25) | -$10 skin foam | **wing loading +33 %: stall speed +15 %, 1.3 Vs from 14.3 to about 16.5 m/s against 15 m/s cruise** (`SIZING-A.md` s5, `EST`); static margin and cruise range move; the transition window ±13 % was a point-mass `EST` and would need rerunning | **do not take** as a yaw fix; at most x0.85 if the bench says it is needed, with the cruise claim rerun |
| Higher spin cap 0.95 | 0 | $0 | one-motor transient current 10.8 A at 0.90 moves toward the uncapped 13.3 A (`SIZING-A.md` s3; about 12 A at 0.95, `EST`), ESC 45 A fine, motor has no burst rating | **no benefit at 5 m/s**; matters only at 7 m/s |
| Bigger prop or hotter KV for more thrust | +20-40 g | +$40-60 for 4 motors (V price $46.90 each, `SIZING-A.md`) | current and cruise match change | **no benefit at 5 m/s** (not at cap); not run |
| Fin area x0.7 | -10 g | $0 | fins also carry the tip landing and pitch-over directional stability | no yaw benefit; do not take |
| `Q_WVANE_ENABLE` 1 | 0 | $0 | K09-L D-152 turned belly into wind; same in A | **do not use**; `A.param` stays 0 |

### Heading rules (needs F4 and C2 sign-off)

- **Hover and loiter:** the pilot holds the aircraft wing-edge-on: wind from the wing tip, within +-10 deg for the unmodified aircraft, +-20 deg with arm 1.2 + cant 16 (steady and gust only; in turbulence prefer +-10). A fixed heading stays within +-10 deg of the wind for 77 % of 30 min blocks, +-15 deg for 92 %, +-20 deg for 97 % (RCMC1, 07-10, mean 2-5 m/s, Jan-Apr 2022-25, `wind_dir.py`). Below 2 m/s the wind lean is under 5 deg and no heading rule is needed.
- **Belly-on is the worst heading** (lean 29-31 deg at 5 m/s, hold 4.4 m off, `SITL.md`): belly-on only to 3 m/s. Do not use `Q_WVANE`.
- **Takeoff:** crew places the aircraft on its fin tips with the wing tips pointing along the wind (ribbon or handheld anemometer on a pole; the H3 procedure already needs one). Yaw holds the placed heading through lift-off. **Landing:** fly the approach so the final heading is edge-on, `Q_LAND_FINAL_ALT` 6 m at 0.3 m/s, QLOITER or QHOVER yaw held, RC9 cut at contact. Takeoff and landing in wind are **not in the plant** (`SITL.md`: not represented) and ground yaw authority with the feet down is `—`, so the rule rests on the sizing (parked tip-over 6.8 m/s, `BOARD.md` C2) and not on SITL.
- Auto edge-on yaw (a Lua script setting a heading from the wind estimate) is `—`, not written, not tested; pilot yaw is the plan.

## 3. Operating wind limit and the schedule (`wind_limits.py`)

Station: RCMC1 Richmond, 7.2 m anemometer, 2022-2025, read as `config-study/tiebreak/wind/wind_stats.py` does (criterion B: every hour 07-10 has mean <= limit and gust <= gust limit; days with fewer than 3 valid hours dropped). **No height correction and no RFS/RCMC1 ratio** (unmeasured, `team/H3/WIND-RFS.md`, 0 of 3 mornings measured); the card limit is rescaled by that ratio when H3 measures it. January added to the files already in the repo (the earlier script stops at February).

| Limit (mean, gust) | Jan | Feb | Mar | Apr | Jan-Apr | worst single year, Jan-Apr | per 7 days (Jan-Apr) |
|---|---|---|---|---|---|---|---|
| 5 m/s, 8 m/s gust (flight card today) | 0.78 | 0.79 | 0.77 | 0.86 | **0.80** | 0.73 | 5.6 |
| 4 m/s, 6.4 m/s gust (scaled gust) | 0.62 | 0.56 | 0.63 | 0.76 | **0.64** | 0.54 | 4.5 |
| 4 m/s, 8 m/s gust | 0.67 | 0.59 | 0.69 | 0.78 | 0.69 | 0.58 | 4.8 |
| 3 m/s, 5 m/s gust (belly-on or no edge-on control) | 0.40 | 0.40 | 0.44 | 0.53 | 0.44 | 0.36 | 3.1 |

(`H2/FLIGHT-TEST-PLAN.md` s6 uses 5.0 per 7 days, which is lower than the 5.6 here: its basis is the worst year of Mar-Apr criterion B. Both bases give the same answer below.)

Blocks of `H2/FLIGHT-TEST-PLAN.md` s6 (K09-L plan dates, `I2/SCHEDULE.md`: F01 12-14 Feb, F02 15-22 Feb, F03 23 Feb-3 Mar, F04 4-10 Mar, F05 22 Mar-2 Apr, F06 3-18 Apr; 2 sorties per morning; A's own gate list is not in the repo, so these are the K09-L needs, `EST`). Usable mornings, all years average / worst year for the month:

| Block | days | needed | 5 m/s | 4 m/s (gust 6.4) | 3 m/s |
|---|---|---|---|---|---|
| F01 | 3 | 2 | 2.4 / 2.2 | 1.7 / **1.1** (short) | 1.2 / 0.9 (short) |
| F02 | 8 | 5 | 6.3 / 6.0 | 4.5 (short) / **3.0** (short) | 3.2 / 2.4 (short) |
| F03 | 9 | 4 | 7.0 / 6.3 | 5.3 / 3.8 | 3.7 / 2.7 (short) |
| F04 | 7 | 3 | 5.4 / 4.3 | 4.4 / 3.6 | 3.1 / 2.3 (short) |
| F05 | 12 | 5 | 9.4 / 7.7 | 7.8 / 6.5 | 5.5 / 4.0 (short) |
| F06 | 16 | 3 | 13.7 / 12.3 | 12.1 / 10.7 | 8.4 / 5.9 |
| **Days added to F01-F06 (shortfall)** | | | **0 / 0** | **1.4 d / 8.4 d** | 7.0 d / 22.2 d |

I2 slack to 30 Apr is **12 d with the 10.5 d crash loop CR1 already inside** (`I2/SCHEDULE.md`). Reading:

- **5 m/s with mandatory edge-on hover (Q_WVANE not used, pilot heading):** no shortfall in any block, the schedule is unchanged, 12 d slack. The heading rule costs no mornings; the weather criterion is the same as today. Edge-on also holds the position within 0.4 m, belly-on does not.
- **4 m/s:** F01 and F02 are short (the February blocks, the tightest in the plan, F01 latest 24 Feb allowed). Average year +1.4 d, worst year +8.4 d. 12 d of slack still covers it (3.6 d left in the worst year), but the margin that was the crash-repair buffer is gone, and the first-hover date moves toward the 24 Feb latest date. It still fits 30 Apr.
- **3 m/s (no heading control):** +7 d average, +22 d worst year: does **not** fit in a bad year. This is the case where the heading rule is not used.
- Yaw benefit of the lower limit is about 1 deg in turbulence (11.1 deg at 4 m/s, 19.5 deg at 5 m/s, both unmodified edge-on; with arm + cant 10.0-10.3 deg at 4 m/s against 11.0-11.7 at 5 m/s). The hardware levers buy much more than the lower limit does.

## 4. Recommendation (cheapest combination, `EST`)

**Hardware: arm x1.2 + cant 16 deg: about +15 g, about +$5, one mount redesign; wing area and fins unchanged. Limit 5 m/s mean (RCMC1 basis, rescaled by the H3 RFS/RCMC1 ratio), gust <= 8 m/s, edge-on within +-10 deg by pilot heading hold, belly-on only to 3 m/s, `Q_WVANE_ENABLE` 0.**

- Steady 5 m/s and +2 gust: pass with margin over +-20 deg (diff 0.25-0.29 steady, yaw 6-8 deg).
- Turbulence sigma 1.0 m/s: **marginal** (yaw peak 11-15 deg, no saturation). It is not a pass, and I am not calling it one. If the bench shows the plate yaw moment above SITL's, drop the limit to 4 m/s (+1.4 d to +8.4 d, still fits) and, if still short, trim wing side area toward x0.85 (cruise claim to be rerun).
- Total effect on the build plan: no extra gate; D-182 mass table +15 g (1.23 to 1.245 kg low case, 2.6 kg gate untouched), cost margin $415 to about $410 (`SIZING-A.md` s7, `EST`).

## 5. What the bench and the yaw test must confirm

1. **Hanging yaw test at cant 16 deg, arm 0.228 m:** authority at +-0.10 throttle >= **0.35 N m** (SITL 0.276 at 14 deg arm 1 scaled by the sizing formula: 0.201 x 1.2 x (sin16/sin14) + 0.078 = about 0.35, `EST`), and the whole curve to the 0.90 cap; the old pass line `Q >= 55 N mm` on rotor reaction stays. Fail line: below 0.30 N m the 5 m/s card is reopened.
2. **Plate yaw moment against heading in a fan or measured 5 m/s flow** at 0, 20, 45, 60, 70, 80, 90 deg on the foam planform. SITL's number to beat: 0.18 N m at 20 deg off the tip and about 0.28 N m at 45 deg (5 m/s, `EST`), and **the steep rise between 80 and 70 deg** (differential 0.12 to 0.35) which comes from my centre-of-pressure taper. If the real curve is flatter, the +-10 deg window can widen; if steeper, it narrows.
3. **A tethered hover in light turbulence (RFS afternoon):** log heading excursion and the yaw differential; stop at 15 deg heading error or any motor above 0.85 output. This is the first test that can turn the marginal turbulence rows into pass or fail.
4. **Pilot heading hold is practised in a simulator or on the tether**: the 77 / 92 / 97 % figures show the wind direction moves outside +-10 deg in 23 % of 30 min blocks, so the pilot re-yaws during a sortie.
5. **Takeoff and landing edge-on in 3-5 m/s wind** are untested in SITL and only sized (`C2`, tip-over 6.8 m/s): a tethered tip-standing test with the real mount.
6. Still not modelled: elevon force in the slipstream (no credit taken), prop in-plane force, ground yaw, real thrust curve (maker rpm column inconsistent), vibration. The plate Cn(heading) and the turbulence spectrum are my numbers; the whole yaw verdict rests on them.

## Reproduce

```
set SCR=<folder with sitl\ArduPlane.elf + cyg*.dll and src\quadplane.parm>
bash redesign/qp/A/sitl/batch3.sh; ... batch7.sh        # lever and turbulence runs, 4 SITL instances in parallel (inst=0..3 ports 9002+10i, tcp 5760+10i)
python redesign/qp/A/sitl/wsum.py                         # table of every w_ / w4_ run
python -I redesign/qp/A/sitl/wind_limits.py               # mornings and block shortfall
python -I redesign/qp/A/sitl/wind_dir.py                  # wind direction steadiness
```
Run keys added to `run_case.py`: `arm=` (motor position scale), `wing_s=` (wing side area scale), `fin_s=`, `inst=`; `P:NAME=VALUE` as before.
