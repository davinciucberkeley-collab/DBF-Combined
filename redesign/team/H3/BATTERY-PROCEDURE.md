# H3 battery handling and charging procedure: 4S 6500 mAh packs

Revision H3-R1, 2026-11-13. Status `PROPOSED`; no pack has arrived. Owner H3 (with E2). Requirement `R-BATT-HANDLING`: packs are stored and carried at storage charge (3.80-3.85 V per cell) in a LiPo bag; charged attended on a non-flammable
surface with sand or an extinguisher at hand, never in a car; inspected for puffing before every charge; bought from US stock and shipped by ground (`team/A2/REQUIREMENTS.md`).
This file is the procedure; the numbers (charge current, thresholds, acceptance line) belong to E2 and are read from [`../E2/ENERGY.md`](../E2/ENERGY.md) sections 4-8, never re-typed here.
Pack: Ovonic 4S 6500 mAh 120C hard case, EC5, 2-pack (`P01`), listed 551 +/- 5 g, 96.2 Wh; re-terminated to AS150U (`team/I1/ORDER-PLAN.md`; `ENERGY.md` section 6).

## 1. Equipment and where it comes from

| Item | Line | Status |
|---|---|---|
| Charger HTRC C150, 150 W | `G01` | in the BOM |
| LiPo bags, 2 | `G02` (Pyrodrone) | in the BOM |
| Ammo can with its rubber gasket removed (vents, does not pressurise) | `G03` (Harbor Freight 63750) | in the BOM |
| IR thermometer | `G05` | in the BOM |
| Watt meter 150 A, balance-lead checker | `G04` | in the BOM |
| Sand bucket (dry sand, 5 m from the pilot box) | - | **not a BOM line**; review estimated the LiPo sand bucket in a ~$20 field-kit line (`review/BUILDABILITY-REVIEW.md` BR-26): `CR-H3-04` |
| Fire extinguisher for the charging place | - | **not a BOM line**; E2 allows "extinguisher or sand at hand" (`ENERGY.md` section 6): sand is the plan, a borrowed extinguisher if the workspace has one |
| Non-flammable charging surface (ceramic tile, concrete, metal tray) | - | a team-workspace item (not bought) |
| Safety glasses, nitrile gloves | - | personal / workspace |
| Iron for re-termination | Jacobs Electronics Lab station | covered by the Maker Pass (in-lab only), 100 W iron per `ENERGY.md` section 6: **ask staff whether LiPo re-termination is allowed in the lab** (`CR-H3-05`) |

## 2. Roles

One **battery lead** (named by the team) owns the pack log and does all charging. A second person is present for re-termination, for every charge and at the field. **Nobody charges unattended, and nobody charges alone in a closed room.**

## 3. On arrival (once per pack)

| Step | Action | Record |
|---|---|---|
| 1 | Inspect for puffing, dents, lead damage. Any damage: do not use; photograph; tell I1 (return) | `team/E2/pack_log.csv` notes |
| 2 | Cell voltages at arrival: every cell 3.75-3.90 V, spread <= 0.02 V | `cell_v_on_arrival` |
| 3 | Weigh with leads on a 1 g scale: accept <= 592.6 g (`CL-A1-PACK-ACCEPT`) | `mass_g` |
| 4 | Calipers (fits the D2 bay 160 x 52 x 53 mm); lead gauge >= 10 AWG (12 AWG: stop, tell E2 and F1) | `length_mm`..., notes `AWG10` |
| 5 | IR load step at 25 C (`T-E2-IR`), <= 5 mohm per cell | `ir_mohm_cell_25c` |
| 6 | Mark `E2-P1`, `E2-P2` on tape with the in-service date | label |
| 7 | **Re-terminate EC5 to AS150U** per `ENERGY.md` section 6: pack at storage voltage, non-flammable mat, bag and sand at hand, safety glasses; **cut and terminate one lead at a time, never both cut at once**; heat-shrink both cups; polarity check, then every cell on the balance lead; put the cut EC5 in the parts bin | `pack_log.csv` notes |

## 4. Charging

1. Only in the named place: **the team workspace, on a non-flammable surface, indoors with the door open or outdoors under cover, never in a car, never unattended** (`R-BATT-HANDLING`). The place is named by the team lead (`CR-H3-05`); Jacobs LiPo policy is not stated on its pages (checked 2026-11-13).
2. Bag the pack, sand within reach, phone in hand.
3. Inspect again: no puffing, dents or damaged leads, balance lead intact.
4. Charger in **balance mode**, balance lead connected, charge current per E2 (1C, `ENERGY.md` section 5), 4S selected; check the charger shows 4 cells before starting.
5. **Charge to 4.20 V per cell only the afternoon before a flying morning**; if the pack will not fly within 48 h, return it to storage (3.80-3.85 V per cell, charger STORAGE mode) (`ENERGY.md` section 5).
6. Charge only between 10 C and 45 C; a cold pack is brought into the cabin, in its bag, first (`team/H1/GROUND-TEST-PLAN.md` rules; `env.pack_takeoff_max_c`).
7. At full charge cell spread must be <= 0.02 V; **quarantine** if the spread after a 1 h rest is > 0.05 V or any cell is below 3.0 V.
8. Unplug, pack back in its bag, log: pack id, mAh in, cell voltages, IR if shown.

Time: about 59 min per pack from the 20 % line, 2.0 h for two packs (`CL-E2-CHARGE-MIN`, `CL-E2-CHARGE-H-4`, `UNVERIFIED`).

## 5. Storage and transport

| Situation | Rule | Source |
|---|---|---|
| Storage | 3.80-3.85 V per cell, each pack in a bag, bags in the ammo can (gasket removed), room temperature, away from flammables | `ENERGY.md` section 6 |
| To the field | charged packs in bags in the ammo can, in the cabin (not the trunk), never left in a closed car in the sun; packs do **not** travel inside the airframe box | `ENERGY.md` section 6; CR-D7-07 |
| Air travel | not planned; 96.2 Wh < 100 Wh would allow a spare in cabin baggage | `ENERGY.md` section 6 (`SRC-E2-FAA-PACKSAFE`) |
| Shipping | US warehouse, ground (UN3480) | `ENERGY.md` section 6 |

## 6. Field use

| Step | Action |
|---|---|
| 1 | Ammo can and sand bucket **5 m from the pilot box** (`ENERGY.md` section 6) |
| 2 | Packs come out only to fly; one fully charged pack per sortie; a part-used pack is never re-flown the same day |
| 3 | IR the pack: **20-34 C** at take-off (`env.pack_takeoff_max_c`); warm a cold pack in its bag in the cabin |
| 4 | Pack in at the trim mark with this pack's spacer stack and crush block, strap, AS150U plugged **last**, after the transmitter is on (`subsystems/pod/BUILD.md` field card) |
| 5 | After landing: disarm, **pull the plug from behind the pod**, IR the pack, bag it, log mAh used and temperature |
| 6 | Pack warm or hot (>= 34 C) after landing: leave bagged in the can, do not charge until it returns to room temperature |

## 7. Damage, crash and fire

| Event | Action |
|---|---|
| Crash with a pack aboard | unplug; if dented, puffed, hot or smelling: into the ammo can or sand **outdoors**, observe >= 30 min, **never charge it again** (`ENERGY.md` section 6) |
| Smoke or fire | step back; **do not carry the pack**; smother with sand; call 911 if it spreads |
| Injury or property damage | UCPD at once, 510-642-6760 (UC policy, fetched 2026-11-13) |
| Pack on retirement: capacity < 80 % of nameplate, IR > 1.5 x new, puffing > 2 mm, or any crash damage | discharge to 0 V on a resistive load, bag it, then Alameda County household hazardous waste (800-606-6606; Oakland 2100 East 7th Street; the Fremont, Hayward and Livermore sites list swollen Li-ion packs, StopWaste listing read by search 2026-11-13: **call first to confirm they accept LiPo and whether an appointment is needed**) |

## 8. Records

`team/E2/pack_log.csv` (one line per charge and per flight, pack id, mAh, temperatures); flight row `pack_id`, `pack_start_v`, `mah_used` (`../H2/templates/flight_log.csv`).

## 9. Change requests from H3

| # | To | What |
|---|---|---|
| CR-H3-04 | I1 | Add a sand bucket and sand (price `-`, not looked up) to the field kit |
| CR-H3-05 | Team lead | Name the charging place; ask Jacobs staff whether LiPo re-termination in the Electronics Lab is allowed; if not, the re-termination place is the charging place with a second person present |
