# F4 — flight-control software

Status `PROPOSED`, revision **F4-R4**, 2026-11-09. Firmware ArduPlane 4.7.x stable on the CoreWing F405 Wing V2
(D-33, no Lua), `Q_TAILSIT_ENABLE` 1, copter Quad-X mixing on the four fin motors, two elevons. ArduPilot, not PX4:
the chosen board has an ArduPilot target and no PX4 target, and ArduPilot gives copter-motor tailsitter mixing,
differential-thrust yaw in fixed wing and an ESC-rpm notch over bidirectional DShot. Nothing loaded, flown or run in
SITL (not installed): every flight behaviour is `UNVERIFIED`.

## Deliverables (`redesign/subsystems/flight-software/`)

| File | What |
|---|---|
| `K09L.param` | 151 parameters, a comment line above every one; 6 LEGACY duplicates for older builds |
| `K09L-STAND.param` | thrust-stand overlay: 25 A limiter, fence off, log disarmed, raw-IMU batch log at sensor rate |
| `SPEC.md` | one page: key numbers, motor/output map, transition logic and limits, elevon schedule, failsafes, landing |
| `TUNING-PLAN.md` | 12 steps: bench → hanging yaw → stand → hover → FW tune → dive / level legs → transition |
| `SITL-PLAN.md` | 17 cases incl. RC / battery / fence / GPS / motor-out / e-stop; status `UNVERIFIED` |
| `params.json` | numbers claims read (`P:fsw.*`), mirrored from `K09L.param` and checked equal |

## R4 changes

| Item | Was → now | Unit | Claim (value, margin) | Status |
|---|---|---|---|---|
| `THR_MAX` (CR-B1-17 b, CR-C1-20) | 75 → **70** | % | `CL-F4-VLEVEL-VH` 0.98 (+2 %): level 21.3 ≤ 21.8 m/s | `UNVERIFIED` |
| FW rpm at `THR_MAX` | — → 7 750 | rpm | `CL-F4-FW-RPM-CAP` ≤ 7 950 (+3 %) | `UNVERIFIED` |
| FW output incl. full yaw | 0.8375 → 0.79 | — | `CL-F4-FW-ACT-MAX` ≤ 0.849 (+7 %) | `UNVERIFIED` |
| `BATT_LOW_MAH` (CR-E2-20) | 2 700 → **2 600** | mAh | `CL-F4-BATT-LOW` ≥ 2 600 (0 %) | `PROPOSED` |
| Hover crossover ceilings (CR-B3-19) | 5 → 4.5 / 4.5 / 2.4 | Hz | `CL-F4-XOVER-*` 1.1 / 2.6 / 1.0 | `UNVERIFIED` |
| P ceilings roll / pitch / yaw | 0.38 / 0.15 / 1.9 → 0.34 / 0.14 / 0.94 | — | `CALC-F4-XOVER` | `MODELLED` |
| Pitch-over rate (CR-B1-12 rev 3) | 12, 20 after logs → 12, **≤ 15** after the sag-0.76 stand run | °/s | B1: peak thrust 0.70 at 12 °/s | `UNVERIFIED` |
| `Q_M_SPIN_MIN` / `Q_M_THST_EXPO` | unset → 0.15 / 0.65 (defaults, stated) | — | inputs of `CALC-F4-VLEVEL` | `PROPOSED` |
| Stand IMU log (CR-H1-18) | — → `INS_LOG_BAT_OPT` 1 | — | ≥ 935 Hz read from the log | `UNVERIFIED` |
| Tests added | hanging yaw (CR-B4-16), thrust lag (CR-B3-19), FBWB level leg | — | `T-F4-HANG-YAW`, `T-F4-THRUST-LAG`, step 6c | `PROPOSED` |

## Check

`python -I redesign/team/F4/fsw_check.py` → lint OK on both files, mirror OK, **34 claims, one negative margin**
(`CL-F4-CANT-SENSE-D3` −1: D3's `cant_sense_UR` is still +1, CR-F4-11). 67 of 145 unique names matched to
ArduPilot source; 78 wait for SITL S1 on the 4.7.x tag. `proofs/build_graph.py` stops in `proofkit.fmt()` on an
infinite value in another role's drift message (CR-F4-17); with a local guard it lists no F4 error.

## Findings others depend on

| Finding | Effect |
|---|---|
| D3's printed cant gives UR thrust along +t; the map needs −t | hover yaw reverses on first spin-up; swap prints A/B (CR-F4-11); step 1b catches it |
| `THR_MAX` 70 keeps level speed under the VH that VD 27.2 assumes | C1 keeps VD 27.2 and n⁺ 3.4 if A1 accepts (CR-F4-15) |
| ArduPilot has no airspeed-scheduled surface limit; no Lua on the F405 | ≤ 1/3 at VD held by envelope only (CR-F4-12) |
| Land detector needs ≥ 5 s at the lower motor limit | touchdown cut is a pilot action on RC9 (CR-F4-14) |
| FW output path (pass-through vs thrust curve) not settled from source | caps use the higher of the two; SITL S4 settles it |
| Tailsitter forward transition ends on pitch angle, not airspeed | first FW tune can fly without the airspeed sensor (CR-I1-16); buy it before the first transition |

## Open

CR-F4-15 … 17 new (A1/C1, B1, tooling); CR-F4-11 (D3 cant), -12, -14, -03/04/06/09/10 open.
