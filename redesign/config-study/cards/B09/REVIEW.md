# B09 skeptic review: Flightory Stallion VTOL (bought files, printed airframe)

Reviewer: skeptic agent, 2026-11-09. Scope: CARD.md, sizing.py, sizing.json, cost.csv. I did not edit the card.
Tags: `ESTIMATE` = my guess, `UNVERIFIED` = not checked against a primary source.
Check script (stdlib, run against an unmodified copy of sizing.py):
`C:/Users/dillo/AppData/Local/Temp/claude/7dc708b3f4b13ffc/76f8c44c-eccf-4b13-8a50-e7f1d35cbb75/scratchpad/b09_check.py`
(a reviewer scratch file outside the repo). It reuses the card's mass build-up and replaces only the items listed below.

## Verdict in one line
The concept holds up. Mass, T/W and packing survive. Two numbers are optimistic: **cruise endurance (18.7 → ~12 min)**
and **reserve ($454 → ~$305, or ~$55 if Jacobs Maker Passes come out of this budget)**. The hover power is about 7 % low.

## 1. Reproducibility: PASS
`python -I sizing.py` on a copy gives output **identical** to the committed sizing.json (MTOW 2298 g, hover 551 W,
cruise 18.7 min). The arithmetic is consistent. The challenges below are about inputs.

## 2. Hover power and max thrust: the card's model is mostly right, calibrated on weak data
| Challenge | Evidence | Correction |
|---|---|---|
| FM·η 0.50 comes from a retailer listing (2100 g / 870 W, prop unstated) | Hobbywing published a full thrust table for a same-class 2807 1700KV (16 V, HQ7x3.5x3): 628 g @ 137 W, 885 g @ 213 W, 2129 g @ 45.6 A / 731 W at 100 % throttle. [HW] (different brand than Emax; best primary data found) | Interpolating at the card's loads (front 726 g, rear 847 g) gives 534 W bench, **587 W with the card's 1.10 install loss** (card: 551 W). Hover current is **≈ 40 A** (card: 37 A). The card is 7 % optimistic, a small error. |
| Max thrust 2100 g/motor | The [HW] table gives 2129 g at 16 V with a **3-blade** 7 in prop. The card specifies a **2-blade 7x5**, and no table for that pairing was found. | At 14.8 V: 2129·(14.8/16)² ≈ 1820 g → worst-motor T/W **2.15** (card 2.23). Still well above the 1.6 gate. Either fly the 7x3.5x3 that has published data, or thrust-stand the 7x5 in week 1 (the card already plans this). |
| 45 A ESC vs motor | [HW] full throttle draws 45.6 A, and Hobbywing recommends a 65 A ESC. The Emax peak is listed as 50–52 A (retailers disagree). | Throttle-capping works, but ESCs running at 100 % of their rating in hover-climb near a crash-repair-limited schedule is poor practice. **Buy 4 × 60 A-class ESCs (+≈ $50, ESTIMATE).** |
| Flightory specifies 1300KV on 4S | VTOL pack page [F2]: "Emax ECOII 2807 1300KV or T-Motor F90 1300KV", 4S. | The card's switch to 1700KV is **justified**. The thrust of a 1300KV motor on 4S with a 7 in prop is roughly 0.9–1.2 kg (rpm-squared scaling, ESTIMATE), and the rear motor carries 847 g. The card states this deviation honestly. |

## 3. Mass: accept 2.30 kg nominal, carry a 2.5 kg pessimistic case
- Flightory's own band is 2000–3000 g AUW for the VTOL pack [F2]. The base Stallion asks for "1 roll" of LW-PLA [F1]
  (an 800 g spool including waste), so the card's 700 g of LW-PLA for the VTOL wings, nacelles and fuselage is plausible.
- No owner-measured Stallion VTOL AUW, hover current or flight time was found. An ArduPilot thread asking owners for exactly
  these numbers got no answers [AP1]. A tilt-tri Mini Skyhunter was reported at 1470 g with a 4S 6000 Li-ion [AP2],
  a smaller airframe, so 2.3 kg for a 1.34 m aircraft with a 448 g pack is not light-washed.
- Risk: first-time LW-PLA prints often come out under-foamed and heavy (ESTIMATE). Pessimistic case: printed parts
  +25 % → **MTOW 2.52 kg**, hover 660 W / 45 A, worst T/W 1.96. That still passes.
- The 10 % contingency plus 250 g growth (≈ 395 g of margin on ≈ 1.6 kg) is adequate.

## 4. Cruise and endurance: optimistic
| Challenge | Evidence | Correction |
|---|---|---|
| Cruise is taken at **14.0 m/s, the bottom of the sweep and exactly 1.3 Vs** | Flightory's optimal speed is 60–70 km/h = **16.7–19.4 m/s** [F1]. Richmond Field Station is a bay-shore site where 5–8 m/s afternoon wind is common (ESTIMATE). Nobody would cruise a 2.3 kg VTOL at its transition-minimum speed. | Use **16 m/s**. |
| CD0 0.040 | LW-PLA surface finish, two tilt nacelles with exposed motors, a stopped rear 7 in prop, skids and a pitot. K06 shares the same value, so the comparison stays fair but both are low. | CD0 **0.050** (ESTIMATE) |
| Result | With the [HW] hover power, CD0 0.05 at 16 m/s: 108 W, L/D 8.0. (Flightory claims ~4 A ≈ 60 W for the clean, lighter non-VTOL Stallion [F1], UNVERIFIED. Scaling by W^1.5 to 2.3 kg plus VTOL drag puts 100–110 W in line.) | **Cruise after 2 min hover + 2 transitions: 12.0 min** (card 18.7). Pessimistic case (2.52 kg, CD0 0.055, 17 m/s): **8.1 min**. Hover-only: **4.8 min** (card 5.2). The 5 min threshold holds in all cases. The 10 min objective holds nominally but not in the pessimistic case. |

Transition energy (2 × 15 s at 1.25 × hover) is thin for first flights. Real early tests spend more time in QLOITER/QHOVER.
Plan test cards with 3 min hover, which costs ~3 min of cruise.

## 5. Cost: missing or understated lines
| Line | Why | Add (pre-tax) |
|---|---|---|
| Transport box / case for the 1.09 × 0.44 × 0.31 m pack | The card's transport claim depends on "one box" but has no cost line | +$40 (ESTIMATE; long hard-sided case or box + foam) |
| 2 × 18650 cells for the RadioMaster Pocket | Pocket radios ship **without** batteries and will not run on USB alone [RM] | +$15 |
| 60 A-class ESCs replacing the 45 A ones (§2) | Hobbywing recommends a 65 A ESC for this motor class [HW] | +$50 (ESTIMATE, net of the $30 4-pack) |
| 4th LW-PLA spool | First-time LW-PLA temperature/flow tuning burns 200–300 g before good parts (ESTIMATE); 3 spools ≈ 2 airframes at 30 % scrap with no tuning allowance | +$30 |
| Subtotal + 10.25 % tax | | **+$149** |
| **Conditional:** Jacobs Hall Maker Pass | Listed at **$125/semester** per person for Jacobs-affiliated classes [JH1] (UNVERIFIED for spring 2027). It may be covered by the capstone course. | +$125–250 if the team pays |

Lines checked and accepted: the charger (the HTRC C150 is AC-input, so no PSU needed), 3 packs, LiPo bags, ammo can,
thrust stand, soldering, spare motor/ESC/servos, the 10.25 % tax rate, $120 shipping.
**Corrected spend ≈ $1,695, reserve ≈ $305** (≈ 1.5 typical $208 crashes). If two Maker Passes are paid from the budget,
the reserve is ≈ $55, which is less than one crash.

## 6. Build, schedule and lead time
- Jacobs printers: the labs page lists **Prusa printers** (count not stated) and says they use the house PLA. A BYO-LW-PLA policy
  was **not found** [JH2]. The posted rules (UNVERIFIED currency) are: one printer per user at a time, jobs over 4 h must run overnight,
  and jobs started after 9 pm are capped at 12 h [JH1]. Overnight jobs help throughput, so the card's 8 h/day assumption is
  conservative. **If LW-PLA is refused, this concept loses its airframe process.** Ask Jacobs before ordering. The fallback is a team-owned
  printer (≈ $250–350, ESTIMATE), which would eat the reserve.
- Person-hours: 100 h is plausible for the airframe. The 20 h for ArduPilot setup is low for a tilt-tri with **no published PIDs**
  plus a fixed-wing AUTOTUNE across several weather-dependent field days. Use **≈ 120–130 h total** (ESTIMATE). The bought design is
  still the fastest route to a first hover in this study.
- The SpeedyBee F405 Wing is listed as backordered in Nov 2026 (cost.csv). If it is not in hand by mid-December, Flightory's output map is lost.
  Pre-select an in-stock alternative (e.g. Matek F405-WTE / H743-WING) and accept remapping.
- Emax 2807 1700KV: stocked by several US retailers (RDQ, Pyrodrone, NewBeeDrone) [E1], so lead time is low.
- LW-PLA HDT is **50 °C at 1.8 MPa / 54 °C at 0.45 MPa** [PM]. The card's "softens ≈ 55–60 °C" is the Tg/Vicat figure, so heat
  risk starts lower than stated. A spring car interior in the sun can reach this. Keep it in the trunk with the shade side up, not on the rear shelf.

## 7. Packing: accepted with the card's own caveat
1.09 × 0.44 × 0.31 m holds geometrically: half-wing 0.62 m × (0.24 + 0.15 nacelle). Flightory only advertises a
"fully detachable nose" [F1], and wing removal over the 10 mm spar comes from the manual summary. **Whether the V-tail is removable is unconfirmed**,
so carry 1.09 × 0.44 × **0.41 m** as the worst case. That is still a normal car trunk or back seat for one person.

## 8. Controls risk: accept the card's rating, add two points
- Tilt-tri with vectored yaw (Q_TILT_TYPE 2) is a supported ArduPilot frame. The single rear motor is a single point of failure,
  and it is also the most-loaded motor (847 g; 928 g in the pessimistic case). Its arm (0.36 m) is an ESTIMATE. A shorter real arm
  raises its share. **Measure the CG-to-rear-motor distance from the STEP files before ordering.**
- The rear motor's reaction torque is trimmed only by differential front tilt. Servo backlash in the 16 g tilt servos shows up as
  hover yaw wobble. The card's servo gyro-margin calc (5.9×) ignores this. The week-1 bench test should include a backlash check.
- Small inconsistency: the card's mass list names a PowerHD 1810MG tilt servo, but the VTOL pack page lists Kingmax 1203MD /
  GDW DS041MG [F2]. Pick one and confirm its torque.

## Numbers I believe (corrected)
| Quantity | Card | Corrected |
|---|---|---|
| MTOW | 2.30 kg | **2.30 kg nominal** (2.52 kg pessimistic) |
| Hover power / current | 551 W / 37 A | **587 W / 40 A** |
| Worst-motor T/W with sag | 2.23 | **2.15** (1.96 pessimistic) |
| Cruise speed / power | 14 m/s / 75 W | **16 m/s / 108 W** |
| Hover-only endurance | 5.2 min | **4.8 min** |
| Cruise after 2 min hover + transitions | 18.7 min | **12.0 min** (8.1 pessimistic) |
| Spend / reserve | $1,546 / $454 | **$1,695 / $305** (reserve $55–180 if Maker Passes are paid) |
| Packed | 1.09 × 0.44 × 0.31 m | 1.09 × 0.44 × 0.31–0.41 m |
| Person-hours | ≈ 100 | **≈ 125** |
| Build difficulty / controls risk (1–5) | n/a | **2 / 3** |

## Sources (seen 2026-11-09)
- [HW] Hobbywing XRotor-2807 1700KV spec and thrust table: https://www.hobbywing.com/uploads/file/20251117/433421b6b5012f9625b63096b02ebd5a.pdf (manufacturer data, different brand than Emax)
- [F1] Flightory Stallion: https://flightory.com/?p=3082 (manufacturer; "4 A … over 4 hours" claim UNVERIFIED)
- [F2] Flightory Stallion VTOL Pack: https://flightory.com/?p=3755
- [E1] Emax ECO II 2807 listings: https://www.unmannedtechshop.co.uk/products/emax-eco-ii-series-2807-motor-1300kv-1500kv-1700kv , https://newbeedrone.com/products/emax-eco-ii-2807-brushless-motor-1700kv (retailer)
- [AP1] https://discuss.ardupilot.org/t/proven-3d-printable-vtol-fixed-wing-project/144948 (forum; no owner data posted)
- [AP2] https://discuss.ardupilot.org/t/vtol-ttricopter-y3-mini-skyhunter/32994 (forum, via search summary, UNVERIFIED)
- [PM] Polymaker LW-PLA TDS v7.0: https://polymaker.com/wp-content/uploads/TDS_PolyLite_LW-PLA_v7.0_2026-04-09.pdf (via search summary)
- [RM] RadioMaster Pocket "2 x 18650 (not included)": https://www.getfpv.com/radios/radio-controllers/radiomaster-pocket-radio-cc2500-elrs-2-4ghz.html (retailer)
- [JH1] Jacobs Maker Pass / printer rules: https://jacobsinstitute.berkeley.edu/our-space/makerpass/ (via search summary, UNVERIFIED currency)
- [JH2] Jacobs labs and equipment: https://jacobsinstitute.berkeley.edu/our-spaces-at-a-glance/labs-and-equipment/
