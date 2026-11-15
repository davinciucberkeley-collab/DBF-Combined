# H3 flight card: K09-L (5 m/s card)

Revision H3-R3, 2026-11-14 (final re-run; R2 and R1 the same week). Status `PROPOSED`; **not signed, nothing flown**. Owner H3 (safety officer). Requirements: `R-SITE`, `R-TIPOVER` (stance rules), `R-WIND`, `R-SPIRAL`, `R-THERMAL`.
Print sections 1-4 and 4b on one laminated page (the box carries `subsystems/transport/CHECKLIST.md` for set-up). Compliance and site rules: [`COMPLIANCE.md`](COMPLIANCE.md). Packs: [`BATTERY-PROCEDURE.md`](BATTERY-PROCEDURE.md).
Wind method and log: [`WIND-RFS.md`](WIND-RFS.md). Test order and gates: [`../H2/FLIGHT-TEST-PLAN.md`](../H2/FLIGHT-TEST-PLAN.md). Range check: [`../F5/RANGE-TEST.md`](../F5/RANGE-TEST.md).
Sections 2 step 0, 4b and the fatigue line in 6 were added 2026-11-13 from change C-16 of `../../review/NASA-CR-132423-COMPLIANCE.md` (NASA CR-132423; gaps G-02, G-03, G-11, G-12, G-14); nothing flown.
R2 (closure round 2026-11-14, `../../review/CLOSURE-ROUND-2026-11-14/H3.md`): `BATT_LOW` 3 100 mAh and the go-around energy (E2, A2 / D-160), forward transition by the transition switch only (B3), the 300 m racetrack (A2), and the fixed-wing pitch-rate, throttle and assist limits F4 sets (C1 CR-C1-40, B4 CR-B4-31). Step 5b checks that the loaded parameters match this card.
R3 (final re-run 2026-11-14, A1-STATUS D-173 / D-174 / D-175): Gens Ace Shorty 6000 HV pack charged to **4.35 V per cell (LiHV)**, the **pack filler pieces** in the bay, **`Q_M_SPIN_MAX` 0.81** and **`THR_MAX` 41** with their consequences (section 5), `BATT_LOW` 3 000 / `BATT_CRT` 1 200, transition start **50 m**. The Lua / SPINCAP lines are gone (Lua withdrawn in D-173b; there were none on this card).

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
| 11 | Pack | Gens Ace Redline Shorty 4S 6000 HV (**LiHV**): charged the afternoon before to **4.35 V per cell (17.4 V)** with the charger in **LiHV mode** and the display showing 4 cells and 4.35 V; **never to 4.35 V in LiPo mode, never above 4.35 V**; one pack per sortie; arms only above 17.0 V (`BATT_ARM_VOLT` 17.0, `EST`, E2 to confirm); pack IR <= 3.8 mOhm per cell group at 25 C or it does not fly (`T-E2-IR`) | `team/E2/ENERGY.md` sections 4-5; E2 D-173; `BATTERY-PROCEDURE.md` |
| 11b | Pack filler pieces | the **aft filler `POD-013` (two XPS blocks, 16 mm fore piece and 27 mm stop piece) is in the bay behind the pack**, the U-spacer stack is the logged one (10 mm: blue 8 + white 2 as built), strap on; a missing filler lets the pack slide 37 mm aft (CG) and unloads the stop: **no-go**. The 16 mm fore piece comes out only for an aft-CG trim, recorded on the card | `subsystems/pod/BUILD.md` `POD-013`; D2 D-176; CG row 13 |
| 12 | Full throttle | no continuous full throttle longer than 10 s from a hover-warm motor | `env.full_throttle_max_s` (D-42) |
| 13 | CG | on the jig inside 46.6-51.4 mm with this pack and this spacer stack; **if aft of 51.4 mm do not fly** | `BUILD-GUIDE.md` stage 11; `MASS-CG.md` |
| 14 | Mass | <= 2.6 kg weighed with this pack | `requirements.mtow_gate_kg` |
| 15 | Link | range check today passed: LQ >= 0.9, no failsafe | `../F5/RANGE-TEST.md` |
| 16 | Gate | the flight is inside a passed gate or the next open one (`R-TEST-ORDER`) | `../H2/FLIGHT-TEST-PLAN.md` |
| 17 | Open issues | none of STATUS issues 1, 8, 9 is open for this gate (fin collar, foot, mount) | `STATUS.md` |

CG rule (open, `STATUS.md` issue 7): A3's D-59 rule or A1's mid-band rule decides the pack station; **the card uses one rule once H8 is answered** (`HANDOFF.md` H8). Until then use the marks above and weigh with each pack.

## 2. Set-up and arming sequence (box checklist first)

0. **Field walk** (every session, before the wind check; G-03, CR-132423 p. 167): re-walk the landing zone, approach sector and alternate spot; note new obstructions (vehicles, tents, other pilots' gear, cranes) against the field map (`subsystems/ops/FIELD-MAP.md`, to be written by H3; —). Zone >= 8 m square, flat, mown (EST); clear of pilot box, spectators and other pads by >= 8 m (CR p. 59); no obstacle above a 10 deg surface from the zone edge in the 90 deg sector centred on the wind (EST; CR p. 42, 58). Brief RFS's other users. Fence polygon read back against the map when it was uploaded (G-04; `FENCE_TYPE` 7 only after that).
1. Wind check (section 1, lines 1-3). Safety lead states go / no-go aloud.
2. Pack in its bag, ammo can 5 m from the pilot box, sand bucket beside it (`BATTERY-PROCEDURE.md`). Extinguisher or sand at hand. Crew in place; non-participants outside the operations area.
3. Aircraft stood on the mat, nose-up on its four feet, level within 5 deg (C5 S1), **wingtip into the wind** (S2). Fit props colour to colour (LH nut on the CW motors), 10 mm spanner, 1.5 N m; pitot boom in (`subsystems/transport/CHECKLIST.md`).
4. **Transmitter on, model K09L selected, throttle down. Then plug the pack in** (power-up order, `../F5/RC-LINK.md`); the aircraft refuses to arm if the link is down or the pack is used. Hatch closed <= 2 min before take-off.
5. Pre-arm checks pass on the Pocket screen; flight mode switch in a Q mode; e-stop (switch SD) tested; nobody in the prop plane +/-30 deg.
5b. **Parameter read-back** (before the first flight of the day, and after any parameter load): `BATT_LOW_MAH` 3000, `BATT_CRT_MAH` 1200, `BATT_LOW_VOLT` 14.4, `BATT_CRT_VOLT` 14.0, `BATT_ARM_VOLT` 17.0, `Q_M_SPIN_MAX` 0.81, `Q_M_BAT_CURR_MAX` 80, `Q_M_BAT_VOLT_MAX` 17.4, `THR_MAX` 41, `FWD_BAT_VOLT_MAX` 17.4, `PTCH2SRV_RMAX_UP` 35, `PTCH2SRV_RMAX_DN` 20, `Q_ASSIST_SPEED` 14, `Q_ASSIST_ALT` 0, `Q_ASSIST_ANGLE` 0, `FENCE_ALT_MAX` 110, `FENCE_RADIUS` 250. Any other value: **no-go** (sources in sections 4, 4b and 5). `subsystems/flight-software/K09L.param` read 2026-11-14 shows these values (R11, D-174); `Q_M_SPIN_MAX` is a fixed number, no script sets it, so a read-back of anything else means a stale file. FBWA sits on the transition switch only, never on the mode switch (B3 closure section 2, CL-4).
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
| Low battery (**3 000 mAh** remaining or 14.4 V) | RTL; in hover land at once. 3 000 mAh holds the landing need **plus one 40 s hover go-around** (section 4b), so that one go-around is already paid for; a second one is not | `BATT_LOW_MAH` 3 000 (E2 D-173 on the Shorty pack: 4.66 min cruise to BATT_LOW); `BATT_LOW_VOLT` 14.4 `K09L.param` |
| Critical (1 200 mAh remaining or 14.0 V) | QLAND. Expected charge at touchdown after a far-point QRTL from `BATT_LOW`: **1 207-1 212 mAh against the 1 200 line (E2 D-173), a margin of 7-12 mAh**, so `BATT_CRT` may fire on a normal landing: it is a QLAND already, expect it and do not treat it as a fault | `BATT_CRT_MAH` 1 200, `BATT_CRT_VOLT` 14.0 (E2 D-173); `K09L.param` |
| Doubt in transition | QHOVER | `subsystems/flight-software/TUNING-PLAN.md` |
| Airspeed below 14 m/s in fixed wing | the motors assist (speed trigger only): lower the nose, add throttle, or select QHOVER. Above 14 m/s there is **no assist** for height or attitude upsets (section 5) | `Q_ASSIST_SPEED` 14 (`K09L.param` l.214; B3 closure section 1.4); `Q_ASSIST_ALT` / `_ANGLE` 0 (B4 closure CR-B4-31) |
| Motor out, uncontrollable, area clear | e-stop (SD, `RC9_OPTION 31`) | `R-ARM-KILL` |
| After landing | disarm; **pull the plug from behind the pod**; IR the pack and motors; check witness marks, feet, hinges; log | `BUILD-GUIDE.md` stage 12 |
| After any crash | unplug; pack dented, puffed, hot or smelling: ammo can or sand outdoors, observe >= 30 min, never charge again; report injury or property damage to UCPD at once at 510-642-6760 | `team/E2/ENERGY.md` section 6; UC policy |
| Post-flight report | to UCPD within 3 business days: date and time of all flights, pilot names, drones flown, accidents or violations | UC policy |

## 4b. Procedures added by the NASA CR-132423 review (C-16)

| Procedure | Rule | Gap, CR page |
|---|---|---|
| **Wind go/no-go** | 5 m/s steady, **wingtip-into-wind landing only** (broadside limit 4 m/s, `STATUS.md` R-WIND row; the 5.4 vs 5.0 m/s margin is thin). **Above 8 m/s gust: lay flat or land at once.** First transitions: morning, <= 5 m/s (`TUNING-PLAN.md` step 7). Rescale after `R-WIND-MEASURE` | G-11, p. 22 |
| **Go-around (any Q-mode landing)** | Triggers: drift > 2 m from the spot (EST), tilt > 10 deg (`R-LANDING-IMPACT`), a spotter call (traffic, person or animal in the zone), a link warning, a gust above the card limit. Action: **QLOITER (switch position 3), climb to >= 10 m** (EST), re-position upwind, re-try once. **Energy: one 40 s hover go-around (about 325 mAh at the 29.2 A hover current of D-174, `EST`) is budgeted inside `BATT_LOW` 3 000 mAh** (E2 closure section 6; A2 closure section 2.1; `requirements.goaround_hover_s` 40, D-160). After that one go-around (a second abort, or a go-around past 40 s, `EST`), land at the alternate spot; do not try the main spot again. In fixed wing the hold is RTL or FBWA loiter at >= 50 m; never hold in hover | G-02, p. 33, 39 |
| **Alternate spot** | marked on the field map, upwind side, same clearance rules as the main zone (step 0) | G-02, G-03, p. 39 |
| **Traffic call** | The spotter watches only the sky and the zone. Fixed call "TRAFFIC - [direction]": in a Q mode the pilot goes to QLOITER and descends; in fixed wing descends below the traffic or selects RTL. No ADS-B receiver is proposed (no budget reserve, `STATUS.md` issue 2) | G-12, p. 40, 97, 167 |
| **Forward transition** | **Only by the transition switch**, never by the mode switch: throttle override at **1.285 x learnt hover throttle** (0.630 at 0.49, `EST` until SITL S4c), **1.0 s pre-climb** in QSTABILIZE (radio timer L06 0.9 s, FC hold 1.08-1.38 s, `EST`; B3 closure 2026-11-14, F5), then FBWA; the override releases >= 0.5 s after FBWA. Start at **50 m AGL** (55 m only after B3 confirms the climb at the 1.38 s hold, CL-F5-B3b): the climb is 50.6 m at a 1.0 s hold (B3, high band edge, `EST`), so the top is **100.6 m from 50 m** (9.4 m under the **110 m** fence, `FENCE_ALT_MAX`); the 1.38 s hold adds climb ("—" until B3 re-runs). Baro error "—" until the twin log. `FENCE_MARGIN` 10 m only notifies; a fence breach in hover starts a forward transition and is a bounded residual (F4 section 4.2), so do not start higher than 50 m. Into the wind, never toward the pilot box. **No AUTO forward transitions** (no `NAV_VTOL_TAKEOFF` followed by a fixed-wing leg); a mission starts only after the manual transition. Doubt: QHOVER (section 4) | B3 closure sections 1.4, 2, CL-5; `K09L.param` l.405 |
| **Cruise pattern** | **300 m racetrack** (300 m legs) at **17 m/s, 30 deg bank** (turn radius 51.0 m, lap 920.7 m = 54.2 s). Far point **201 m** from the centre, inside the **250 m** fence (49 m, 2.9 s buffer) and the 500 m VLOS. Centre it on the home point, legs along the wind. Mission: settle 15 s, 2 laps, 1 fixed-wing go-around lap, run-in into the wind = 3.41 min (`cruise_time_min` 3.5) | A2 closure section 2.1; `FENCE_RADIUS` 250 `K09L.param` l.407 |
| **Back-transition into wind** | Select QHOVER from cruise **only heading into the wind (within 45 deg, EST)**, at >= 50 m, never toward the pilot box. RTL does this itself with `Q_RTL_MODE` 2 (`K09L.param`) once SITL S18 has shown it; no downwind approach | G-01, p. 35, 172 |
| **Fatigue limit** | Maximum flights per pilot per session: — flights; minimum rest between flights: — min (H2 sets both). Rotate the spotter role each flight. Keep one parameter change per flight (`TUNING-PLAN.md` rules) | G-14, p. 169 |

## 5. Spiral, pitch-rate and assist notes for the pilot (`R-SPIRAL`, `R-LOADS`)

The spiral mode meets t2 >= 3.3 s only with roll-stabilised modes (D-66); in cruise fly FBWA/CRUISE, not manual. A CG outside the marks changes this (`R-SPIRAL`, `team/B3/S-AND-C.md`).

| Setting (F4) | Value | What the pilot feels | Source |
|---|---|---|---|
| `PTCH2SRV_RMAX_UP` / `_DN` | 100 -> **35 / 20 deg/s** | **Gentler pitch response in FBWA**: a full pull or push reaches its pitch angle more slowly, and a push is slower than a pull. Start pull-ups and push-overs early; do not chase the stick. A 45 deg turn at 17 m/s needs 23.4 deg/s, inside 35. The caps hold the load at VD 27.2 m/s to n 3.12 (limit 3.4) and -1.21 (limit -1.5). Transitions and hover use the VTOL controller and do not change | C1 closure sections 1.1, 4 (CR-C1-40) |
| `THR_MAX` | 60 -> **41 %** (with `FWD_BAT_VOLT_MAX` 17.4 compensation) | **Full stick in fixed wing is only 41 % of the battery-compensated throttle, not 100 %.** Level speed is about 21.2-21.5 m/s on a fresh pack against the 21.76 m/s dive limit VH (1 % margin, `EST`): there is **no reserve above `THR_MAX`**, and **a dive is not recoverable by throttle: use pitch**. The compensation scales the demand by 17.4 / resting pack volts (up to 54 % at 13.2 V), so the same stick gives about the same power on a part-used pack: the throttle percent on the OSD rises as the pack falls, which is normal. A fixed-wing climb is gentle (`TECS_CLMB_MAX` 3 m/s; the sagged climb reaches about 2.9): plan height early, do not try to climb out of a low pass | F4 R11 (D-174); `K09L.param` `THR_MAX`, `FWD_BAT_*` |
| `Q_M_SPIN_MAX` | 0.84 -> **0.81 (fixed)** | **Hover and Q-mode thrust stops at 81 % of motor output whatever the stick or the controller asks.** Fresh pack: thrust / weight 2.10; worst pack state (3.73 V/cell, 10 C): 1.77 (E1). A hard recovery, go-around or climb in a Q mode gets **no more than that** and the margin shrinks on a low or cold pack: land at `BATT_LOW`, do not stretch a hover. **The forward transition needs 1.285 x the learnt hover throttle, so it fits under 0.81 only if the learnt hover throttle is <= 0.63** (0.81 / 1.285, 0.49 start): if the learnt value is above 0.60, do **not** transition, land. Winding current on one saturated motor is 46 A (limit 50 A) and the ESC 37 A, so a stuck-high command is bounded, not free | E1 D-174 (tested: winding 46.07 A, ESC 37.35 A, T/W fresh 2.096, worst 1.771); B3; `K09L.param` |
| `Q_ASSIST_ALT`, `Q_ASSIST_ANGLE` | 15 / default 30 -> **0 / 0** | **Assist only below 14 m/s** (`Q_ASSIST_SPEED`). Low height or a large bank or pitch error at speed gets **no** motor help: stay >= 50 m in fixed wing, keep bank <= 45 deg (`ROLL_LIMIT_DEG`, `K09L.param` l.239), and recover an upset with FBWA levelling or QHOVER | B4 closure section 2.3 (CR-B4-31); C1 closure section 1.1 residual |

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
| Field walk done, new obstructions noted; fence corners checked against the field map (initials) | - |
| Flights flown by this pilot today (limit —); spotter this flight | - |
