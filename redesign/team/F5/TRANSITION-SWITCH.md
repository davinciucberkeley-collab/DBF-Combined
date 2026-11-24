# Timed transition switch: EdgeTX set-up on the RadioMaster Pocket (ELRS)

Status `PROPOSED`, revision F5-R3, 2026-11-14 (closure round, B3 request CL-4). Owner F5. Numbers:
`team/F5/transition_switch.py` (tables, timing, logic model) → `results/transition.json`; claims `CL-F5-TRANS-*` in
`team/F5/claims.json` (`python -I redesign/team/F5/rc_link.py`). SITL check: `team/F5/transition_sitl.py`.
`EST` marks an estimate. Pocket switch names and directions are `UNVERIFIED` until the radio arrives (`RC-LINK.md`).

## Verdict

- **One switch does the forward transition.** From QSTABILIZE, armed, stick above 40 %: flip **SC down**.
  - The radio overrides CH3 so that ArduPilot's QSTABILIZE `throttle_in` = **1.285 × learnt θh** (0.630 at θh 0.49).
  - **0.9 s** later (logical-switch delay) the flight-mode channel CH6 jumps to the **FBWA** slot.
  - **1.2 s** after that the override is released and CH3 follows the stick again.
  - At the flight controller this is **1.08–1.38 s** in QSTABILIZE at the entry throttle (`EST`, timing model §5),
    and the override ends **≥ 0.62 s** after FBWA is active.
- **FBWA, CRUISE and RTL exist only after that sequence.** No switch position, no order of switch moves and no stick
  position puts a fixed-wing slot on CH6 otherwise: 0 violations in 200 random 2-minute switch histories with 100+
  completed sequences (`CL-F5-TRANS-NO-DIRECT-FW`).
- **SC back up = back-transition to QHOVER**, whatever SB says, until SB is moved.
- **The 1.285 θh target is met exactly at the set θh and tracks it.**
  - Fixed setting: 37 % override → stick step 67 % → `throttle_in` 0.6297, ratio **1.2850** at θh 0.49.
  - ArduPilot's own `throttle_curve` keeps the ratio inside B3's window for any learnt θh from **0.4766 to 0.5056**.
  - Outside that band, a pre-flight table (§4) gives the override and, where needed, `Q_THROTTLE_EXPO`.
- **New finding for B3 and F4.** ArduPilot reads the throttle stick as an **integer percent** (`control_in` is
  `int16_t` on a range of 100). One step moves the ratio by **1.39 %**, wider than B3's whole window (1.17 %).
  - "An exact channel value" therefore does not by itself give an exact ratio.
  - The design above handles it. B3's `ASM-B3-TRANS-REALISE` text should say so (request CL-F5-B3a).
- **SITL (stage A, logic) confirms the sequence.**
  - QSTABILIZE hold 2.18 s, release 0.90–0.94 s after FBWA.
  - ThI / ThH = 1.2849, held to "Transition FW done" whatever the stick did.
  - The abort and the QHOVER flip do nothing (§7).

| Claim | Value | Limit | Status |
|---|---|---|---|
| `CL-F5-TRANS-THR-IN` | 0.6297 | — | at θh 0.49 |
| `CL-F5-TRANS-R-REAL-LO` / `-HI` | 1.2850 | ≥ 1.2769 / ≤ 1.2919 | pass |
| `CL-F5-TRANS-THETA-LO` / `-HI` | 0.4766 / 0.5056 | — | band of the 37 % setting |
| `CL-F5-TRANS-R-STEP` | 1.395 % per stick step | — | information |
| `CL-F5-TRANS-PWM-MARGIN` | 4.48 µs | ≥ 2 µs (`ASM-F5-TRANS-CHAIN`, `EST`) | pass |
| `CL-F5-TRANS-HOLD-MIN` | 1.079 s | ≥ 1.0 s | pass (`EST`) |
| `CL-F5-TRANS-HOLD-MAX` | 1.381 s | — | B3 to check (CL-F5-B3b) |
| `CL-F5-TRANS-RELEASE` | 0.619 s | ≥ 0.5 s | pass (`EST`) |
| `CL-F5-TRANS-NO-DIRECT-FW` | 0 | ≤ 0 | pass (logic model) |
| `CL-F5-TRANS-NEUTRAL-Q` | 0 | ≤ 0 | pass with the FLTMODE order of §3 |

## 1. What the sequence does

| t (radio) | Event | CH3 | CH6 → ArduPilot mode |
|---|---|---|---|
| — | hover in QSTABILIZE (SB up), stick ≈ mid | stick | QSTABILIZE |
| 0 | **SC flipped down** (armed, stick > 40 %, SB up) | override 37 % (1689 µs) | QSTABILIZE (forced) |
| 0 → 0.9 s | pre-climb at 1.285 θh | override | QSTABILIZE |
| 0.9 s | FBWA command | override | **FBWA** (ArduPilot switches 0.29–0.49 s later) |
| 3.1 s | override released | stick | FBWA; firmware holds the entry throttle to 70° (B3 §1.2) |
| any time | **SC up** | stick | before 0.9 s: stays QSTABILIZE (abort); after: **QHOVER** (back-transition) |
| in FW | SB up / mid / down | stick | FBWA / CRUISE / RTL |

- **Why the start needs QSTABILIZE.** B3's entry is a QSTABILIZE throttle. Starting from QHOVER would also add a mode
  change (0.29–0.49 s) inside the pre-climb.
  - So the logic only starts when SB is up and the radio is not in its forced-QHOVER state.
  - Flipping SC from QHOVER or QLOITER does nothing. The pilot returns SC up, selects QSTABILIZE and flips again.
- **Why a stick guard.** Flipping SC on the ground with the stick low does nothing.
- **Why an SC edge, not a level.** Arming with SC already down does nothing. Only the flip itself starts the sequence.

## 2. Channel map (replaces the table in `RC-LINK.md`)

| Ch | Function | Source on the Pocket | ArduPilot |
|---|---|---|---|
| 1–4 | roll, pitch, throttle, yaw (AETR, mode 2) | sticks; **CH3 overridden by SF1** during the sequence | `RCMAP_*` default; `RC3_MIN/MAX/DZ` 988 / 2012 / 30 |
| 5 | arm / disarm | SA (2-pos, self-locking), down = armed | `RC5_OPTION` 153 |
| 6 | flight mode | mixes from SB, SC and L-switches (§4.3) | `FLTMODE_CH` 6, slots of §3 |
| 9 | motor emergency stop | SD (2-pos, self-locking), down = stop | `RC9_OPTION` 31 |
| 7, 8, 10–12 | spare | — | `RCn_OPTION` 0 |

- **SC (3-pos)**: up = VTOL, middle = VTOL (no function), **down = transition / fixed wing**.
- **SB (3-pos)**:
  - in VTOL: up QSTABILIZE, middle QHOVER, down QLOITER;
  - in FW: up FBWA, middle CRUISE, down RTL.
- **Pocket switch types.** SA and SD are self-locking 2-position, SB and SC 3-position, SE momentary (Pocket manual
  via search summary, 2026-11-14, `UNVERIFIED`). SE stays unused.

## 3. ArduPilot flight-mode slots (F4 sets them, CR-F5-15)

The mode switch is read at 7 Hz with a 200 ms debounce (`SRC-F5-AP-MODESW`). Thresholds 1231 / 1361 / 1491 / 1621 /
1750 µs. Slot order is chosen so that the three pulses an accident is most likely to produce are all Q modes:

- 1500 µs: EdgeTX 0 %, e.g. a deleted mix line;
- 988 µs and 2012 µs: the end points of a single-switch mix.

| Slot | Pulse band (µs) | EdgeTX % (pulse) | Mode | Was (`K09L.param` F4-R7) |
|---|---|---|---|---|
| 1 | < 1231 | −65 (1167) | **QSTABILIZE** 17 | QSTABILIZE 17 |
| 2 | 1231–1360 | −40 (1295) | **FBWA** 5 | QHOVER 18 |
| 3 | 1361–1490 | −15 (1423) | **CRUISE** 7 | QLOITER 19 |
| 4 | 1491–1620 | +11 (1556) | **QHOVER** 18 | FBWA 5 |
| 5 | 1621–1749 | +36 (1684) | **RTL** 11 | CRUISE 7 |
| 6 | ≥ 1750 | +62 (1817) | **QLOITER** 19 | RTL 11 |

Each EdgeTX value sits 62–68 µs inside its band. CH6 rides the ELRS Wide round robin at 7 bit (about 8 µs per step),
which is far finer than the band.

## 4. EdgeTX model "K09L"

### 4.1 Model settings

| Item | Setting |
|---|---|
| Internal RF | ExpressLRS, 150 Hz, telemetry 1:4, Wide switch mode, 100 mW fixed (`RC-LINK.md`), **model match on** |
| EdgeTX flight modes | none (FM0 only); no global variables used |
| Throttle source | Thr; throttle warning on; **throttle trim off** on CH3 (the stick low end must stay −100 % = 988 µs) |
| Switch warnings at model load | **SA up, SC up, SD up** |
| Outputs | CH3 and CH6: min −100, max +100, subtrim 0, no curve. No slow / delay on any CH6 mix line, so CH6 jumps between slot centres and never sweeps through other slots |

### 4.2 Logical switches

EdgeTX steps sticky, edge and delay timers every 0.1 s and restarts a delay whenever its condition drops
(`SRC-F5-EDGETX-LS`). L04 and L05 refer to L13–L15, which have higher numbers. EdgeTX then uses the previous cycle's
value. That is harmless here, because the loop goes through sticky states that only change on the 0.1 s tick.

| LS | Function | V1 | V2 | AND switch | Delay | Meaning |
|---|---|---|---|---|---|---|
| L01 | a>x | Thr | −20 | — | — | stick above 40 % (hover guard) |
| L02 | AND | SC↓ | SA↓ | — | — | transition requested while armed |
| L03 | Edge | SC↓ | [0.0 : <<] | — | — | 0.1 s pulse when SC reaches down |
| L04 | AND | L03 | L01 | L15 | — | valid start |
| L05 | Sticky | L04 | !L02 | — | — | **sequence latched**; cleared by SC up or disarm |
| L06 | AND | L05 | SA↓ | — | **1.9** | **FBWA command** (FW state) |
| L07 | AND | L06 | SA↓ | — | **1.2** | release time |
| L08 | AND | L05 | !L07 | — | — | **throttle override on** |
| L09 | AND | L06 | SB− | — | — | CRUISE |
| L10 | AND | L06 | SB↓ | — | — | RTL |
| L11 | AND | L12 | !L06 | — | — | SB moved outside FW |
| L12 | \|Δ\|>x | SB | 50 | — | — | SB moved (0.1 s pulse) |
| L13 | Sticky | L06 | L11 | — | — | after FW: hold QHOVER until SB moves |
| L14 | AND | SA↓ | !L13 | — | — | armed and not in forced QHOVER |
| L15 | AND | SB↑ | L14 | — | — | start allowed (really in QSTABILIZE) |

Duration is 0.0 on every line, and Persist is off on both sticky switches.

### 4.3 Mixes

CH6, top to bottom. Each line uses Source MAX, Weight as listed, and no offset, curve, slow or delay. Lines 2–8 use
Multiplex **Replace**, so the lowest active line wins.

| Line | Weight | Switch | Mode |
|---|---|---|---|
| 1 | −65 | — (always) | QSTABILIZE |
| 2 | +11 | SB− | QHOVER |
| 3 | +62 | SB↓ | QLOITER |
| 4 | +11 | L13 | QHOVER (back-transition) |
| 5 | −65 | L05 | QSTABILIZE (pre-climb, whatever SB does) |
| 6 | −40 | L06 | FBWA |
| 7 | −15 | L09 | CRUISE |
| 8 | +36 | L10 | RTL |

Other channels:
- CH1 Ail, CH2 Ele, CH3 Thr, CH4 Rud: one line each, source = stick, weight 100.
- CH5: source SA, weight 100.
- CH9: source SD, weight 100.

### 4.4 Special functions

| SF | Switch | Function | Value | Enable |
|---|---|---|---|---|
| SF1 | L08 | **Override CH3** | **37** (§4.5 table) | on |
| SF2 | L05 | Play sound | "Warn1" (sequence started) | on |
| SF3 | L06 | Haptic | 3 (FBWA commanded) | on |
| SF4 | SA↓ | SD Logs | 0.1 s (`RC-LINK.md` ground log) | on |

Override CHx returns the value straight to the output, before the limits (`mixer.cpp applyLimits`). The value is an
integer percent, i.e. 1500 + 5.12 × value µs at ArduPilot.

### 4.5 The override value: how it tracks θh

**Firmware path** (Plane-4.7.2, `SRC-F5-AP-THRCURVE`):

- `control_in` = trunc(100 × (pwm − 1018) / 994), an integer from 0 to 100.
- `throttle_in` = throttle_curve(θh, `Q_THROTTLE_EXPO`, control_in / 100).
- θh is the learnt `Q_M_THST_HOVER`, and it does not move in QSTABILIZE (B3 §1.2).
- `throttle_curve` puts mid stick at θh. A fixed stick step therefore follows θh partly by itself: the ratio falls by
  0.40 % per +0.01 of θh.

**At the design point:**

- 37 % gives 1689.4 µs, which is `control_in` 67, 4.5 µs inside its 9.94 µs step.
- `throttle_in` = 0.6297 = 1.2850 θh at θh 0.49.
- B3's window allows the ratio from 1.2769 to 1.2919. That is −0.63 % / +0.54 %: the margins of B3's low edge
  (1.2908 vs 1.2827) and high edge (1.3893 vs 1.3968).
- So the learnt θh may lie anywhere from **0.4766 to 0.5056** with no change.

**Pre-flight table** (`results/transition.json`, every 0.005; every 0.01 shown):

- Q_THROTTLE_EXPO stays at 0.2 when the nearest step is within ±0.25 % of 1.285.
- Otherwise the expo is solved so that the step gives 1.285 exactly.

| Learnt θh | Stick step (%) | `Q_THROTTLE_EXPO` | SF1 value (%) | Pulse (µs) | `throttle_in` | Ratio | Error |
|---|---|---|---|---|---|---|---|
| 0.40 | 65 | 0.2 | 33 | 1669.0 | 0.5145 | 1.2862 | +0.09 % |
| 0.42 | 65 | 0.179 | 33 | 1669.0 | 0.5397 | 1.2849 | −0.01 % |
| 0.44 | 66 | 0.217 | 35 | 1679.2 | 0.5654 | 1.2850 | 0 |
| 0.45 | 66 | 0.2 | 35 | 1679.2 | 0.5786 | 1.2858 | +0.06 % |
| 0.46 | 66 | 0.188 | 35 | 1679.2 | 0.5910 | 1.2849 | −0.01 % |
| 0.47 | 66 | 0.172 | 35 | 1679.2 | 0.6040 | 1.2850 | 0 |
| 0.48 | 67 | 0.217 | 37 | 1689.4 | 0.6167 | 1.2849 | −0.01 % |
| **0.49** | **67** | **0.2** | **37** | **1689.4** | **0.6297** | **1.2850** | **0** |
| 0.50 | 67 | 0.183 | 37 | 1689.4 | 0.6425 | 1.2850 | 0 |
| 0.51 | 68 | 0.222 | 39 | 1699.7 | 0.6553 | 1.2849 | −0.01 % |
| 0.52 | 68 | 0.2 | 39 | 1699.7 | 0.6687 | 1.2860 | +0.08 % |
| 0.53 | 68 | 0.184 | 39 | 1699.7 | 0.6811 | 1.2851 | +0.01 % |
| 0.55 | 69 | 0.2 | 41 | 1709.9 | 0.7064 | 1.2843 | −0.05 % |
| 0.57 | 70 | 0.2 | 43 | 1720.2 | 0.7333 | 1.2865 | +0.12 % |
| 0.60 | 72 | 0.228 | 47 | 1740.6 | 0.7710 | 1.2851 | 0 |

Each pulse is ≥ 3.3 µs inside its step at RC3 988 / 2012 / 30. If RC3 is ever re-calibrated, re-run
`transition_switch.py` with the new values.

**Pre-flight procedure** (every transition flight; flight card, H2):

1. Connect USB. Read `Q_M_THST_HOVER`. With `Q_M_HOVER_LEARN` 2 the firmware saves the learnt value at disarm, so it
   holds the value from the last hover.
2. If it lies in **0.477–0.505**, keep SF1 37 and `Q_THROTTLE_EXPO` 0.2.
   - Otherwise take the row for the nearest 0.005 from `results/transition.json`.
   - Set SF1 on the radio and, if the row says so, `Q_THROTTLE_EXPO` (Mission Planner).
   - Re-do bench step B2 (§6).
3. In flight, hover in QHOVER or QLOITER **≥ 60 s** before the transition, so the learning settles (time constant
   10 s). Then select QSTABILIZE, hold height with the stick near mid, and flip SC.
4. After the flight, from the DataFlash log: QTUN.ThI / QTUN.ThH over the pre-climb must lie within
   **1.2769–1.2919**.
   - The logged θh drift between flights is the number that shows how often step 2 is needed. It is unknown today
     ("—").

## 5. Timing (radio → ELRS → ArduPilot), `EST`

| Element | Value | Source |
|---|---|---|
| EdgeTX delay effective | 0.8–0.9 s (L06, set 0.9), 1.1–1.2 s (L07) | 0.1 s tick, `SRC-F5-EDGETX-LS` |
| CH3 over ELRS | 1–2 packets: 6.7–13.3 ms | every packet carries ch 1–4 |
| CH6 over ELRS | 6.7–59 ms | `CL-F5-SWITCH-LATENCY` |
| Mode switch read | 7 Hz, accepted after ≥ 200 ms: 286–429 ms after the pulse arrives | `SRC-F5-AP-MODESW` |
| **FC time in QSTABILIZE with the override** | **1.08–1.38 s** | `CL-F5-TRANS-HOLD-MIN` / `-MAX` |
| FBWA active → override released at the FC | 0.62–0.92 s (≥ 0.5 s, B3) | `CL-F5-TRANS-RELEASE` |

- The 0.9 s delay puts the shortest hold at 1.08 s, at or above B3's 1.0 s pre-climb (closure 2026-11-14: 2.0 s -> 1.0 s because the 11x8E climb at the high edge was 66.2 m at 2.0 s, over the 60 m allowance; 50.6 m at 1.0 s).
  A longer hold only adds climb at the high edge; the low edge needs none (B3: pitch use 0.320 without it).
- The longest hold, 1.38 s, adds climb at B3's high edge (B3 scales its 50.6 m; fence 110 m from a 50 m start leaves 60 m). B3 checks this (CL-F5-B3b).


## 6. Bench test `T-F5-TRANS-BENCH` (props off, aircraft tied down)

| Step | Set-up | Do | Pass |
|---|---|---|---|
| B0 | EdgeTX Companion simulator, model K09L | walk every SA × SB × SC combination in both orders; then the nominal sequence | CH6 shows −40 / −15 / +36 (fixed-wing slots) **only** after SC↓ from SB↑ with SA↓ and Thr > −20, after 0.9 s; CH3 shows 37 from the flip to 1.2 s after the FBWA command; SC↑ in FW gives +11 until SB moves |
| B1 | Radio bound to the FC, Mission Planner on USB, disarmed | Radio calibration screen: read RC3 at stick low / high and RC6 in each slot | RC3 988 ± 2 / 2012 ± 2; RC6 within ± 3 µs of 1167 / 1295 / 1423 / 1556 / 1684 / 1817; mode readout as §3 |
| B2 | same | SA↓ (FC refuses to arm with the stick high: fine), stick at mid, SC↓ | RC3 = 1689 ± 2 µs (the SF1 pulse of the row in use); i.e. `control_in` step 67 |
| B3 | armed in QSTABILIZE (props off), log on | stick to mid, SC↓, wait 10 s, SC↑, disarm | log: RCIN.C3 step to MODE FBWA **1.0–1.4 s**; MODE FBWA to RCIN.C3 back to stick **≥ 0.5 s**; QTUN.ThI in the pre-climb = table `throttle_in` ± 0.002 (the bench hover throttle is the stored θh); after SC↑ MODE QHOVER |
| B4 | armed, QSTABILIZE | SC↓ then SC↑ after 0.5 s | no FBWA in the log; ThI returns to the stick |
| B5 | armed, SB mid (QHOVER) | SC↓ | nothing (no override, no mode change); SF2 silent |
| B6 | disarmed, SC↓ | arm (SA↓) | nothing; arming with SC down never starts the sequence |
| B7 | armed, stick low (< 40 %) | SC↓ | nothing |

The bench runs before the first transition flight and again after any EdgeTX, ELRS or RC calibration change.

## 7. SITL check `T-F5-TRANS-SITL` (stage A, logic)

`transition_sitl.py` runs the logic model of §4 (`transition_switch.Pocket`) at 10 ms steps of SIM time and sends its
CH3 / CH5 / CH6 / CH9 as `RC_CHANNELS_OVERRIDE`. The firmware therefore sees the radio's pulses.

- **Set-up.** ArduPlane SITL 4.7.3-beta1 (the build in `team/F4/sitl/RESULTS.md`), the stock
  `quadplane-copter_tailsitter` model, K09L.param with F4's stage-A SIM overrides, plus:
  - FLTMODE1–6 = 17 / 5 / 7 / 18 / 11 / 19;
  - RC3 988 / 2012 / 30;
  - `Q_THROTTLE_EXPO` 0.2, `Q_A_ANGLE_BOOST` 0.
- **Flight.** Arm in QHOVER, climb to 50 m, hover 60 s, read the learnt `Q_M_THST_HOVER`, pick the table row, then:
  - **A** nominal;
  - **B** stick to 30 % and then 100 % during the pitch-over;
  - **C** abort after 0.5 s (before the 0.9 s FBWA command);
  - **D** flip from QHOVER.

**Result, run 2026-11-14** (`results/transition_sitl.json`). The first run lost cases B–D to the 110 m fence: the stock
model climbs 77–98 m in the pitch-over (as in F4's S4a). The second run lifts the fence as F4's S5 sweep does.

- **Set-up values.** Learnt θh 0.3500 in SITL, which is below the table range. The rule picked step 64, SF1 31 %
  (1658.7 µs) and `Q_THROTTLE_EXPO` 0.185, for a target `throttle_in` of 0.4497.

| Case | Hold in QSTABILIZE with the override (RCIN.C3 step → MODE FBWA) | FBWA → release | QTUN.ThI pre-climb / ThH | ThI from FBWA to "Transition FW done" | Result |
|---|---|---|---|---|---|
| A nominal | **2.179 s** | **0.940 s** | 0.44973 / 0.35002 = **1.2849** | 0.44973 constant, 136 samples over 6.24 s | pass. Then SB mid → CRUISE; SC up → QHOVER, "Transition VTOL done" |
| B stick to 30 %, then 100 % after FBWA | 2.180 s | 0.900 s | 0.44990 / 0.35016 = 1.2848 | **0.44990 constant** (137 samples, 6.25 s) while the stick moved | pass: the firmware ignores the stick to 70° (B3 §1.2 confirmed in SITL) |
| C SC up after 1.0 s | — | — | 0.45008 / 0.35031 = 1.2848 | no FBWA; mode stays QSTABILIZE; CH3 back to the stick | pass |
| D SC down from QHOVER (SB mid) | — | — | — | no override, no mode change | pass |

- **Summary.** The ratio of 1.2848–1.2849 lies inside 1.2769–1.2919. The holds of 2.18 s and the releases of
  0.90–0.94 s lie inside the model bands of 2.08–2.38 s and 0.62–0.92 s.
  - The A release of 0.940 s is 0.02 s above the modelled maximum. SITL adds MAVLink-override latency in place of
    ELRS, and that latency only lengthens the release, which is the safe direction.
- **Re-run needed.** The table above is the 1.9 s (2.08–2.38 s FC hold) run of 2026-11-14 and is kept as logged. L06 is now 0.9 s (FC hold 1.08–1.38 s); `transition_sitl.py` is updated (stick moves at 1.0 + 0.9 s) but NOT re-run in this session (needs the SITL build). Logic model re-run: nominal FBWA at 0.9 s, abort at 0.5 s holds QSTABILIZE, 0 violations in 400 histories.
- **Stage A only.** The airframe is not K09-L, so no height, speed or margin above is a K09-L number.


## 8. Hazards and how the design handles them

| Hazard | Handling |
|---|---|
| FBWA from a plain mode-switch position at hover throttle (B3 §2, path 1) | no such position exists (§4.3); `CL-F5-TRANS-NO-DIRECT-FW` 0 |
| SC flipped on the ground | needs armed **and** stick > 40 % **and** an SC edge; arming with SC down does nothing (B6) |
| SC flipped below 50 m in a hover with the stick above 40 % | the logic cannot know height: flight card (H2/H3) "SC only at ≥ 50 m AGL". A telemetry altitude guard was **not** adopted: it depends on the downlink and an EdgeTX sensor offset that are `UNVERIFIED` |
| Mix line deleted or CH6 at 0 % / ±100 % | slots 1 / 4 / 6 are Q modes (§3) |
| RC link lost during the sequence | ArduPilot's RC failsafe (F4): QSTABILIZE → QLAND; in FBWA → FW short failsafe. The radio logic plays no part |
| Pilot moves SB during the pitch-over | CH6 goes to CRUISE or RTL (fixed-wing modes; the transition continues). Flight card: SB stays up until "Transition FW done" |
| Back-transition into QSTABILIZE by mistake | SC up always gives QHOVER (L13) until SB moves |
| θh outside the band | pre-flight table; post-flight log check of ThI / ThH |
| RC3 re-calibrated | the override may land one step off: re-run the table with the new RC3 values and repeat B2 |

## 9. Requests

| # | To | Request (exact) |
|---|---|---|
| CR-F5-15 | F4 | `K09L.param`: keep `FLTMODE_CH` 6. **FLTMODE1–6 = 17, 5, 7, 18, 11, 19** (QSTABILIZE, FBWA, CRUISE, QHOVER, RTL, QLOITER; was 17, 18, 19, 5, 7, 11). `INITIAL_MODE` 17 unchanged. State `RC6_OPTION` 0, `RC7_OPTION` 0, `RC10_OPTION`–`RC12_OPTION` 0; keep `RC5_OPTION` 153, `RC8_OPTION` 0, `RC9_OPTION` 31; no `RCn_OPTION` may select any flight mode. Add `RC3_MIN` 988, `RC3_MAX` 2012, `RC3_DZ` 30 (default, stated), `RC3_TRIM` 988, with the comment "do not re-calibrate RC3; if calibrated, F5 re-picks the override". State `Q_THROTTLE_EXPO` 0.2 (default; changed only from `TRANSITION-SWITCH.md` §4.5), `Q_M_HOVER_LEARN` 2 and `Q_A_ANGLE_BOOST` 0 (B3). Drop the 0.65 fallback text (B3 CL-3) |
| CR-F5-16 | F4 | `SPEC.md` forward-transition row, `TUNING-PLAN.md` step 7, `SITL-PLAN.md` S1b and S4c: entry = "SC down from QSTABILIZE (stick > 40 %), radio holds 1.285 θh for 1.9 s, then FBWA"; S1b slot pulses 1167 / 1295 / 1423 / 1556 / 1684 / 1817 µs → 17 / 5 / 7 / 18 / 11 / 19; S4c driven by `team/F5/transition_sitl.py`, pass lines: ThI / ThH in the pre-climb 1.2769–1.2919, QSTABILIZE-with-override 2.0–2.4 s, ThI held within 0.01 of entry to 70°, override release ≥ 0.5 s after FBWA |
| CL-F5-B3a | B3 | `ASM-B3-TRANS-REALISE`: the stick is read in integer percent; one step = 1.39 % of the ratio. The realised ratio is 1.2850 at the set θh and stays within 1.2769–1.2919 while the learnt θh is 0.4766–0.5056 (37 %); the table covers 0.40–0.60. No change to B3 numbers needed |
| CL-F5-B3b | B3 | Re-check the pre-climb at the FC hold of **1.08–1.38 s** (`EST`; SITL §7): `CL-B3-TRANS-CLIMB` (49.5 m at 2.0 s) and the gust / handover at the high edge with `w0` up to ≈ 9.1 m/s. If 2.38 s does not pass, F5 shortens L06 to 1.8 s (hold 1.98–2.28 s) and B3 confirms the low edge at 1.98 s |
| CR-F5-17 | H2 / H3 | Flight card: (1) before a transition flight read `Q_M_THST_HOVER` and apply §4.5; (2) hover ≥ 60 s in QHOVER / QLOITER, then QSTABILIZE, stick near mid, ≥ 50 m AGL; (3) **transition only by SC down; never move SB until "Transition FW done"**; (4) back-transition: SC up (QHOVER); (5) after the flight check ThI / ThH. Switch warnings SA / SC / SD up at model load |

## What the team must measure

| # | What | How | Confirms |
|---|---|---|---|
| M1 | RC3 / RC6 pulses at the FC | B1, B2 | `CL-F5-TRANS-PWM-MARGIN`, slots |
| M2 | Hold and release timing | B3 log; SITL §7 | `-HOLD-MIN`, `-RELEASE` |
| M3 | θh spread between flights | `Q_M_THST_HOVER` after each hover flight | how often the table is needed |
| M4 | ThI / ThH at every transition | DataFlash | ratio in the window |

## Sources

**Repo:** `team/B3/results/closure1114.json` (window, band), `review/CLOSURE-ROUND-2026-11-14/B3.md` §1.2–1.4, §2;
`subsystems/flight-software/K09L.param` §1, §10; `team/F4/sitl/RESULTS.md`; `team/F5/RC-LINK.md`.

**Web, read 2026-11-14:**
- https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/ArduPlane/quadplane.cpp (`get_pilot_throttle`)
- https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/libraries/AP_Math/AP_Math.cpp (`throttle_curve`)
- https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/libraries/RC_Channel/RC_Channel.cpp and `.h`
  (`read_6pos_switch`, `debounce_completed`, `pwm_to_range_dz`, `int16_t control_in`)
- https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/ArduPlane/radio.cpp (`set_range(100)`, dead zone 30),
  `ArduPlane/Plane.cpp` (scheduler: `read_mode_switch` 7 Hz), `ArduPlane/Log.cpp` (QTUN fields)
- https://raw.githubusercontent.com/EdgeTX/edgetx/v2.11.3/radio/src/switches.cpp, `mixer.cpp`, `functions.cpp`
- https://manual.edgetx.org/bw-radios/model-select/logical-switches,
  https://manual.edgetx.org/bw-radios/model-select/special-functions,
  https://manual.edgetx.org/bw-radios/model-select/inputs-mixes-and-outputs/mixes.md
- https://xcopter.com/download/Pocket_User_Manual.pdf (switch types; through a search summary, `UNVERIFIED`)
