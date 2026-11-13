# H3 flight card: K09-L (5 m/s card)

Revision H3-R1, 2026-11-13. Status `PROPOSED`; **not signed, nothing flown**. Owner H3 (safety officer). Requirements: `R-SITE`, `R-TIPOVER` (stance rules), `R-WIND`, `R-SPIRAL`, `R-THERMAL`.
Print sections 1-4 on one laminated page (the box carries `subsystems/transport/CHECKLIST.md` for set-up). Compliance and site rules: [`COMPLIANCE.md`](COMPLIANCE.md). Packs: [`BATTERY-PROCEDURE.md`](BATTERY-PROCEDURE.md).
Wind method and log: [`WIND-RFS.md`](WIND-RFS.md). Test order and gates: [`../H2/FLIGHT-TEST-PLAN.md`](../H2/FLIGHT-TEST-PLAN.md). Range check: [`../F5/RANGE-TEST.md`](../F5/RANGE-TEST.md).

## 1. Limits (go / no-go)

Any single **no** is a no-go. The pilot or H3 can call no-go at any time; the other cannot overrule it.

| # | Limit | Value | Source |
|---|---|---|---|
| 1 | Steady wind at 2 m, mean of three 1-min readings | **<= 5 m/s** | `requirements.wind_limit_ms` (P8); CR-B1-14 |
| 2 | Gusts | **<= 8 m/s**; above it lay the aircraft flat, pack out | `team/B1/CHANGE-REQUESTS.md` CR-B1-14; C5 S5 |
| 3 | Wind at RFS vs RCMC1 | ratio < 1.4, else the card is rescaled or the K01 reversal applies | `R-WIND-MEASURE`, `requirements.wind_ratio_max`; `WIND-RFS.md` |
| 4 | Time | 07:00-10:00 (RFS allows 06:00 to sunset) | `env.site`; UC policy (https://oercs.berkeley.edu/policies/campus-policy-library/unmanned-aircraft-system-drone-policy, fetched 2026-11-13) |
| 5 | Site | RFS yellow sub-fields 1-4 only; aircraft and pilot **both inside the FRIA** the whole flight, aircraft in sight | `env.site`; 14 CFR 89.115 (eCFR fetched 2026-11-13) |
| 6 | Height, distance | <= 400 ft (122 m) AGL; <= 500 m from the pilot (VLOS); geofence 110 m and 250 m | `mission.ceiling_ft_agl`, `requirements.vlos_max_m`, `K09L.param` `FENCE_*` |
| 7 | Crew | pilot, spotter, logger, safety lead (no double role with the pilot) | `../H2/FLIGHT-TEST-PLAN.md` section 2 |
| 8 | Approvals | UC flight request >= 7 business days ahead (RFS asks 72 h), accepted; registered aircraft; TRUST, AMA, UC Drone Program on file | `COMPLIANCE.md` |
| 9 | Ambient | <= 44 C (field-ambient ceiling for the full mission) | `env.ambient_ceiling_c` (D-42, D-67) |
| 10 | Pack at take-off | **20-34 C by IR thermometer**; a cold pack is warmed in the cabin, in its bag | `env.pack_takeoff_max_c` (D-42); CR-E2-06 |
| 11 | Pack | charged the afternoon before to 4.20 V per cell; one pack per sortie; arms only above 16.4 V (`BATT_ARM_VOLT`) | `team/E2/ENERGY.md` sections 4-5 |
| 12 | Full throttle | no continuous full throttle longer than 10 s from a hover-warm motor | `env.full_throttle_max_s` (D-42) |
| 13 | CG | on the jig inside 46.6-51.4 mm with this pack and this spacer stack; **if aft of 51.4 mm do not fly** | `BUILD-GUIDE.md` stage 11; `MASS-CG.md` |
| 14 | Mass | <= 2.6 kg weighed with this pack | `requirements.mtow_gate_kg` |
| 15 | Link | range check today passed: LQ >= 0.9, no failsafe | `../F5/RANGE-TEST.md` |
| 16 | Gate | the flight is inside a passed gate or the next open one (`R-TEST-ORDER`) | `../H2/FLIGHT-TEST-PLAN.md` |
| 17 | Open issues | none of STATUS issues 1, 8, 9 is open for this gate (fin collar, foot, mount) | `STATUS.md` |

CG rule (open, `STATUS.md` issue 7): A3's D-59 rule or A1's mid-band rule decides the pack station; **the card uses one rule once H8 is answered** (`HANDOFF.md` H8). Until then use the marks above and weigh with each pack.

## 2. Set-up and arming sequence (box checklist first)

1. Wind check (section 1, lines 1-3). Safety lead states go / no-go aloud.
2. Pack in its bag, ammo can 5 m from the pilot box, sand bucket beside it (`BATTERY-PROCEDURE.md`). Extinguisher or sand at hand. Crew in place; non-participants outside the operations area.
3. Aircraft stood on the mat, nose-up on its four feet, level within 5 deg (C5 S1), **wingtip into the wind** (S2). Fit props colour to colour (LH nut on the CW motors), 10 mm spanner, 1.5 N m; pitot boom in (`subsystems/transport/CHECKLIST.md`).
4. **Transmitter on, model K09L selected, throttle down. Then plug the pack in** (power-up order, `../F5/RC-LINK.md`); the aircraft refuses to arm if the link is down or the pack is used. Hatch closed <= 2 min before take-off.
5. Pre-arm checks pass on the Pocket screen; flight mode switch in a Q mode; e-stop (switch SD) tested; nobody in the prop plane +/-30 deg.
6. Arm only from the RC arm switch (SA). Call "arming" and "clear".

## 3. Stance and landing rules (C5)

| Rule | Value | Source |
|---|---|---|
| S1 | land on the mat, >= 0.8 x 0.8 m, level within 5 deg | `team/C5/LANDING.md` section 5 |
| S2 | final descent and touchdown with a wingtip into the wind (broadside limit 4.0 m/s, span-into-wind 8.0 m/s) | same |
| S3 | touch down in QLAND / QLOITER at <= 0.5 m/s; pilot down-stick <= 1.0 m/s | same; `Q_LAND_FINAL_SPD` 0.3 |
| S4 | spin down at once after contact | same |
| S5 | between flights lay the aircraft flat unless gusts <= 5 m/s, pack in, on the mat | same |
| S6 | lay flat, pod up, lower props turned spanwise first | same |
| S7 | check the replace-mark groove of every foot after every landing | same |
| S8 | after a hard landing or tip-over: shoe bonds, fin tips, wingtip caps, props, mounts, pod nose, block | same |
| D-40 | the one field tool is the 10 mm prop spanner | `params/CHANGE-LOG.md` D-40 |

## 4. In-flight and after-flight

| Event | Action | Source |
|---|---|---|
| Link lost | Q modes: QLAND in place; FW: circle, RTL at 5 s, then QRTL | `K09L.param`, `../F5/RC-LINK.md` |
| Low battery (2 600 mAh remaining or 14.0 V) | RTL; in hover land at once | `K09L.param` `BATT_*` |
| Critical (1 300 mAh remaining or 13.6 V) | QLAND | same |
| Doubt in transition | QHOVER | `subsystems/flight-software/TUNING-PLAN.md` |
| Motor out, uncontrollable, area clear | e-stop (SD, `RC9_OPTION 31`) | `R-ARM-KILL` |
| After landing | disarm; **pull the plug from behind the pod**; IR the pack and motors; check witness marks, feet, hinges; log | `BUILD-GUIDE.md` stage 12 |
| After any crash | unplug; pack dented, puffed, hot or smelling: ammo can or sand outdoors, observe >= 30 min, never charge again; report injury or property damage to UCPD at once at 510-642-6760 | `team/E2/ENERGY.md` section 6; UC policy |
| Post-flight report | to UCPD within 3 business days: date and time of all flights, pilot names, drones flown, accidents or violations | UC policy |

## 5. Spiral and CG-dependent notes for the pilot (`R-SPIRAL`)

The spiral mode meets t2 >= 3.3 s only with roll-stabilised modes (D-66); in cruise fly FBWA/CRUISE, not manual. A CG outside the marks changes this (`R-SPIRAL`, `team/B3/S-AND-C.md`).

## 6. Signatures (one card per flying day, kept with the flight row)

| Field | Value |
|---|---|
| Date, site sub-field, flight-request id | - |
| Wind: three readings, mean, max gust, RCMC1 reading | - |
| Pack ids, IR temperatures at take-off | - |
| CG with each pack, mass | - |
| Gate flown today | - |
| Go / no-go (H3) and time | - |
| Pilot | - |
