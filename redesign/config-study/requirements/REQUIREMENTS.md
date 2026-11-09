# Requirements for the configuration study

Status: PROPOSED (requirements engineer, 2026-11-09). Inputs: `STUDY-BRIEF.md` (team lead's four constraints),
`docs/DESIGN-BASIS.md` v0.4.0 (previous agent's R1–R21), `redesign/inputs/ADVISOR-XV24-LESSONS.md`,
`redesign/inputs/MENTOR-GUIDANCE-2026-11-04.md`. Web sources checked 2026-11-09 unless dated otherwise.
Tags: `ESTIMATE` = engineering guess, `UNVERIFIED` = claim not checked against a primary source, `ASSUMPTION` = the
team can overturn it.

How to read this file: §1 is what the team actually said, made measurable. §2 is what law, safety and physics add
whether the team likes it or not. §3 is the one thing nobody has decided (the mission). §4 disposes of the old
R-numbers. §5 is the scoring sheet the configuration agents must use.

---

## 1. The four real constraints, quantified

| ID | Team's words | Quantified requirement | How the number was chosen |
|---|---|---|---|
| **C1** | "Budget $2,000, hard" | Total spend **≤ $2,000.00** including 10.25 % Berkeley sales tax on goods, all carrier shipping, batteries, charger, radio, test gear, spares and shop consumables. **Planning cap for a configuration = $1,850** so that **≥ $150 stays as crash reserve** at order time. Outside the cap: FAA registration ($5), AMA membership, TRUST (free), any Part 107 exam fee. | Tax rate and "everything inside" from the existing BOM practice (`docs/DESIGN-BASIS.md` R6, `decisions/D10.md`). Reserve: one lift motor + ESC + prop + a wing panel of foam is about $100–150 at the prices in `docs/research/bom-savings.md` (2026-11-01) → $150 `ESTIMATE`. The previous design ended at a $118–145 reserve and the team called it tight. |
| **C2** | "A sort of VTOL drone" | Takes off and lands **vertically with zero ground roll** from an unprepared grass or dirt area **≤ 10 m × 10 m** `ESTIMATE`, no launcher, catcher, net or runway, in the wind of §2 D11. **Any VTOL layout qualifies** (lift + cruise, tailsitter, tiltrotor, tilt-wing, pure multirotor). Whether a wingless multirotor is an acceptable answer is a mission question (§3), not a constraint. | Area: RFS flying zones are subdivided fields (rfs.berkeley.edu/sky.html); 10 m square is a conservative patch any field offers. |
| **C3** | "Easy to transport — fits in a normal car, carried and assembled by one or two people quickly" | (a) Everything that flies packs into **one or two boxes, each ≤ 1.2 × 0.5 × 0.4 m**, so one box fits in a mid-size sedan trunk and the other across the back seat. (b) **No single piece > 1.5 m long** (fits through a folded 60/40 rear seat) `ESTIMATE`. (c) **Each box ≤ 15 kg** so one person lifts it `ESTIMATE`. (d) Transport → flight-ready in **≤ 15 min by 2 people**, ≤ 6 field joints, one hex-key set, every joint with a positive lock and an electrical disconnect at every removable joint (`ADVISOR-XV24-LESSONS.md` item 3). (e) Field-site handling: 2 people carry the assembled aircraft 100 m. **M-item: measure two team members' cars and replace (a)–(b).** | Trunk volumes: Camry 15.1 ft³, Civic 14.8 ft³, Accord 16.7 ft³ (https://www.edmunds.com/toyota/camry/2024/st-401999976/features-specs; https://ahgautoservice.com/how-big-is-the-cargo-space-on-a-honda-accord). No manufacturer publishes trunk-opening sizes; a 1.2 × 0.5 × 0.4 m box (0.24 m³ = 8.5 ft³) is just over half of the smallest trunk, leaving room for the second box or a toolbox. 1.5 m matches the previous R4 envelope. 15 kg is below common one-person manual-handling guidance for an awkward box `ESTIMATE`. |
| **C4** | "Student-built, Jacobs Hall, hot-wire foam possible, first flights ≈ April 2027" | Every part is **bought**, or made by one of: FDM print (Prusa PLA, free with Maker Pass; LulzBot TAZ 6; Markforged X7 / Stratasys Fortus at the Advanced Prototyping Lab if the lab's per-print charge, `UNVERIFIED`, is in the BOM), laser cut plywood/acrylic ≤ 32 × 18 in (three machines) or ≤ 48 × 25 in (one), ShopBot CNC router 4 × 8 ft, OMAX waterjet 26 × 26 in, Tormach 440 and manual mill/bandsaw, table-saw/bandsaw cut foam, vacuum-former ≤ ¼ in sheet, team-owned hot-wire bow (priced $41.73, `docs/research/bom-savings.md`). **Not available: autoclave, CNC hot-wire, composite moulds.** Wet lay-up only as a hand process in the spray booth. No part needs a tolerance tighter than ±0.3 mm (printed) or ±0.5 mm (laser) `ESTIMATE`. Schedule: design frozen by **2026-12-15**, all orders placed by **2027-01-15**, airframe complete **2027-02-28**, first hover **2027-03-15**, first transition **2027-04-15** `ASSUMPTION`. | Equipment list: https://jacobsinstitute.berkeley.edu/our-spaces-at-a-glance/labs-and-equipment/ (checked 2026-11-09). Vendor lead times of 10–20 working days from China (`bom-savings.md`) force the January order date. |

---

## 2. Derived must-haves (law, safety, physics)

| ID | Requirement | Why it is not optional | Source |
|---|---|---|---|
| **D1** | Take-off mass **< 25 kg (55 lb)** with everything attached. | Above that it is not a "small unmanned aircraft"; none of the paths below apply. | 49 U.S.C. § 44801 ("small unmanned aircraft": less than 55 lb incl. everything on board): https://www.law.cornell.edu/uscode/text/49/44801; § 44809 and Part 107 both apply only to small UAS |
| **D2** | **Register** the aircraft with the FAA ($5 per aircraft) and display the number on the outside. Applies above 0.55 lb take-off weight. | 14 CFR 48.15 / 48.30 / 48.205. | https://www.law.cornell.edu/cfr/text/14/48.15, https://www.law.cornell.edu/cfr/text/14/48.30 |
| **D3** | **Operating path: 49 U.S.C. § 44809 (recreational), which by statute includes "an institution of higher education for educational or research purposes."** Conditions: each pilot passes TRUST (free) and carries the certificate; follow a CBO's guidelines (AMA); VLOS at all times; give way to manned aircraft; ≤ 400 ft AGL in Class G; authorization (LAANC) in B/C/D/E-surface airspace. Alternative: one Part 107 pilot (exam fee ≈ $175 `UNVERIFIED`, outside C1). Part 107 adds 87 kt and 3 sm visibility limits. | Without a legal path the university will not approve a flight request. | § 44809(a)(1)–(8) and the § 350 educational note as amended by Pub. L. 118-63 § 928 (2024): https://www.law.cornell.edu/uscode/text/49/44809; 14 CFR 107.51: https://www.law.cornell.edu/cfr/text/14/107.51 |
| **D4** | **Remote ID:** standard RID, a broadcast module, **or fly only inside a FRIA. Richmond Field Station is a FRIA** ("the only FRIA in the East Bay"), so **no RID module is needed if every flight is at RFS**. Carry a $40 broadcast-module line in the BOM as *conditional*: it is bought only if a non-FRIA site is used. | 14 CFR 89.101 applies RID to every registered aircraft; 89.115 gives the module and FRIA alternatives. | https://www.law.cornell.edu/cfr/text/14/89.101, https://www.law.cornell.edu/cfr/text/14/89.115; FRIA: https://rfs.berkeley.edu/sky.html; module price BeeID $39.99 (newbeedrone.com, `bom-savings.md`, 2026-11-01) |
| **D5** | **Site process (RFS):** a UC Berkeley sponsor (PI) anchors the activity; drones registered with FAA *and* UC, pilots registered with UC (UC Drone Program); flight request ≥ 72 h ahead at RFS *and* the campus policy's ≥ 7 business days for UCPD/Risk Services — plan on 7 business days; post-flight report within 3 business days; ≥ $1 M liability per pilot (AMA membership satisfies it); spotters; 6 a.m.–sunset; RFS ceiling 400 ft AGL; fly only in the yellow sub-fields 1–4. **Only RFS is approved for transition testing** (Clark Kerr 200 ft, La Loma < 20 ft). | Campus policy and site rules. | https://oercs.berkeley.edu/policies/campus-policy-library/unmanned-aircraft-system-drone-policy; https://rfs.berkeley.edu/sky.html; https://ucdrones.github.io/New_User_Guide/ |
| **D6** | **Airspace at RFS: check the FAA UAS Facility Map / a LAANC app for the exact site before the first flight.** RFS is ~13 nm north of OAK (Class C) and under the SFO Class B shelves; the 400 ft layer is believed to be Class G or Class E-700 `UNVERIFIED`. If it is controlled, LAANC authorization is a per-flight step, not a design change. | § 44809(a)(5)–(6). | https://www.faa.gov/air_traffic/publications/aim_html/chap11_section_4.html |
| **D7** | **Flight controller with data logging** and a maintained VTOL mode for the chosen layout (ArduPilot Plane QuadPlane / tailsitter / tiltrotor, or PX4 VTOL). The campus policy requires a "flight management system" whose logs can support an incident report for aircraft > 0.5 lb. | Policy; and a first-time team cannot write and debug its own VTOL controller by April. | Campus policy (D5 link); https://ardupilot.org/plane/docs/quadplane-parameters.html |
| **D8** | **Arming and kill:** hardware safety switch or equivalent + RC arm switch + full `ARMING_CHECK`; an RC "motor emergency stop" function that cuts all motors within 1 s; props off for every bench test of the electrics. | Standard practice; the single most common student-build injury is a motor starting on the bench `UNVERIFIED`. | https://ardupilot.org/plane/docs/quadplane-reliability.html |
| **D9** | **Physical power disconnect** on the aircraft, anti-spark, rated **≥ 1.25 × the peak transition current** continuous `ESTIMATE` (e.g. Amass AS150U 70 A cont. / 140 A 1 min; XT90-S is 40 A and failed this check on the 7.4 kg design); pack-to-bus wire sized for hover current with ≤ 10 °C rise `ESTIMATE`. | Fire and arc-flash safety; the previous design already found XT90-S under-rated (`decisions/D5.md`). | `docs/DESIGN-BASIS.md` R20 and `docs/research/propulsion-margin-data.md` |
| **D10** | **Failsafes configured and tested on the bench before flight:** RC loss → QRTL/QLAND (`Q_OPTIONS` bit 5/20), GCS loss (if telemetry used), low battery → `BATT_FS_LOW_ACT 6` (fixed-wing return, loiter to `Q_RTL_ALT`, QLAND), critical battery → land, `Q_TRANS_FAIL`/`Q_TRANS_FAIL_ACT` → QRTL, geofence set to the RFS 400 ft ceiling and the yellow sub-field boundary with `FENCE_ACTION` RTL/land, `Q_ASSIST_SPEED` ≈ `AIRSPEED_MIN` − 3 m/s. | ArduPilot's own reliability guidance for QuadPlanes. Parameter names are version-specific; re-check against the installed firmware. | https://ardupilot.org/plane/docs/quadplane-reliability.html; https://ardupilot.org/plane/docs/apms-failsafe-function.html |
| **D11** | **Hover thrust-to-weight ≥ 1.6 at take-off mass (2.0 recommended)**, from the motor maker's thrust table at nominal pack voltage; hover **controllable in steady 5 m/s, gusts 8 m/s** `ESTIMATE` (RFS is on the bay shore; afternoon sea breeze is routine → morning flights). Transition completes at **≥ 1.3 × stall speed**. | T/W below 1.6 leaves no control authority in gusts; stall during transition is the classic quadplane crash. | T-Motor VTOL guide: https://shop.tmotor.com/blog/vtol-propulsion-system-selection-guide (checked 2026-11-01 by the previous agent); ArduPilot: `AIRSPEED_MIN` "about 25 % above stall" (D10 link) |
| **D12** | **Battery handling:** LiPo stored and transported at storage charge (3.80–3.85 V/cell) in a fire-resistant LiPo bag inside the car trunk, never charged unattended or in a car, charged on a non-flammable surface with a bucket of sand or a Class D/ABC extinguisher at hand; packs inspected for puffing before every charge; damaged packs discharged and taken to campus e-waste. **Buy packs from US stock**: LiPo ships ground-only and several vendors cannot ship it out of the US (`docs/research/budget-energy-test.md`). If the aircraft ever travels by air, each pack must be ≤ 160 Wh and carry-on with airline approval (a 6S 6500 mAh pack is 144 Wh; 6S 8000 mAh is 178 Wh and cannot fly) — informational, not a design driver while the team drives. Campus EH&S has no LiPo-specific sheet found; UCSB's checklist is the closest UC guidance. | Fire safety; the only hazard that can reach beyond the team. | FAA PackSafe: https://www.faa.gov/hazmat/packsafe/lithium-batteries; UC Drone Program fire-safety chapter: https://ucdrones.github.io/Advanced_SOP/fire-safety.html; UCSB EH&S checklist: https://www.ehs.ucsb.edu/sites/default/files/docs/ls/Lithium_Battery_Safety_Checklist.pdf |
| **D13** | **Thermal:** motors, ESCs and pack stay inside their rated temperatures for the full mission at the field ambient on the day; the configuration study reports the ambient ceiling as an output (the previous 25 °C was a C0-specific result). | Physics; a sealed pack bay cooked the previous design's margins to +4–7 K (`decisions/D11.md`). | `docs/research/thermal.md` method |
| **D14** | **Mass discipline:** a mass budget with per-subsystem allocations exists before any CAD, and the as-built take-off mass gate is set at the sized mass + 5 % `ESTIMATE`. Every part has a status (`PROPOSED` / `MODELLED` / `CHECKED` / `VERIFIED`). No floating parts; every part on a joint. | The advisor's XV-24 run went 3 → 10.8 kg and never flew; the mentor asked for buildability before simulation. | `ADVISOR-XV24-LESSONS.md`; `MENTOR-GUIDANCE-2026-11-04.md` |
| **D15** | **Pilot readiness:** the pilot logs ≥ 10 h on a simulator (RealFlight or ArduPilot SITL with the team's parameters) and flies a < $150 foam trainer or small quad before the first hover `ESTIMATE`; the trainer cost sits inside C1 only if the team has no pilot with RC experience. | A first-time pilot and an untested airframe on the same day is the dominant crash risk; the team has one airframe and one budget. | Engineering judgement; ArduPilot SITL quadplane frame (D10 link) |

---

## 3. The mission question (ASSUMPTION the team can overturn)

The team never fixed a mission; "VTOL + fits in a car + $2,000" says nothing about how far, how fast or with what.
The mission sets battery energy, which sets mass, which sets cost. Three candidates:

| | **M-A: VTOL demonstrator** | **M-B: efficient-cruise mapping demo** | **M-C: small-payload delivery demo** |
|---|---|---|---|
| Profile | Vertical take-off, hover 1 min, transition, cruise pattern, back-transition, hover 1 min, vertical landing | Take-off, transition, fly a lawn-mower pattern over one RFS sub-field at best-L/D speed while a camera records, land | Take-off with a 0.5 kg box, transition, cruise to a pad ≤ 300 m away, back-transition, precision hover-land on a 2 × 2 m pad, release, return |
| Endurance (threshold / objective) | Hover 2 min total; cruise **5 / 10 min**; 20 % reserve | Hover 1.5 min; cruise **20 / 30 min**; 20 % reserve | Hover **4 min** total (precision landing twice); cruise 5 min; 20 % reserve |
| Speed | 1.3–1.6 × Vs, i.e. 14–20 m/s `ESTIMATE` | Best L/D, ≈ 12–15 m/s; needs an airspeed sensor | 14–18 m/s; hover authority matters more than speed |
| Payload | None; **0.25 kg growth allowance** in the sizing `ESTIMATE` | 0.15–0.25 kg camera + mount (a used action camera, ≈ $50–100) | 0.5 kg + release mechanism (servo + printed latch, ≈ $20) |
| Energy per flight `ESTIMATE` | ≈ 100–150 Wh (6S 6500 class pack) | ≈ 250–350 Wh (two packs in parallel or a 10 Ah pack: +$70–140) | ≈ 150–200 Wh; hover with payload drives T/W and motor cost |
| Size / mass implication `ESTIMATE` | Span 1.2–2.4 m, MTOW 3–7 kg; smallest airframe of the three | Span 2–2.5 m, MTOW 5–8 kg, higher aspect ratio; largest wing | Span 1.5–2.2 m, MTOW 5–8 kg; T/W ≥ 1.6 *with* payload pushes motor size |
| Fits C1–C4? | Yes; cheapest | Marginal: the previous C0 at $1,855 had a 12 min cruise, and a 30 min cruise needs roughly double the pack | Marginal: payload + T/W margin was exactly what broke the previous design's mass (R12 history) |
| Configurations it favours | Any; tailsitters and small tiltrotors become viable | Lift + cruise with a clean high-AR wing; parked-rotor drag is penalised | Lift + cruise or multirotor; tailsitters are poor at precision hover in wind |
| Capstone content | Transition is the hard, novel part | Adds an aero-efficiency story and a data product | Adds a mechanism and a precision-landing control problem |

**Recommended default for the study: M-A, the VTOL demonstrator**, with these numbers as the assumption:
hover ≥ 2 min total, cruise ≥ 5 min threshold / 10 min objective at 14–20 m/s, 20 % reserve, 0 payload +
0.25 kg growth allowance, VLOS pattern inside one RFS sub-field (≤ 500 m from the pilot).

Reasons: (1) it needs the least energy, so it is the only one with comfortable budget room, and C1 is the one
hard constraint; (2) the transition is the hardest and most instructive thing a VTOL does, and a first-time team
should spend its single airframe on learning it; (3) M-A is a strict subset of M-B and M-C: the same airframe can
grow into a mapping flight by adding a pack and a camera later, but a design sized for M-B or M-C cannot shrink its
cost back; (4) it keeps the wingless multirotor out of the answer set, because a multirotor does not demonstrate
transition. The team overturns this by writing a different row into §5's "mission fit" anchors; nothing else in
this file changes.

---

## 4. Disposition of the previous agent's R-numbers (`docs/DESIGN-BASIS.md` v0.4.0)

| R | Was | Verdict | One-line reason |
|---|---|---|---|
| R1 | Lift + cruise, pusher, stopped lift rotors | **CHANGE** → C2 | The team said "a sort of VTOL"; the layout is the study's output, not its input. Lift + cruise is one candidate. |
| R2 | MTOW 8–15 kg target, < 25 kg cap | **CHANGE** | Keep the < 25 kg legal cap (D1). Drop the 8–15 kg band: the 7.4 kg design already sat below it and it had no basis. MTOW is an output; C3's 15 kg box is the practical ceiling. |
| R3 | Span 2–3 m | **DROP** | Span is an output of mission and stall speed; the real limit is the C3 box and the 1.5 m piece. |
| R4 | Largest piece ≤ 1.5 × 0.5 × 0.4 m, measure the car | **CHANGE** → C3 | Keep the idea, state it as two boxes and a 1.5 m piece; keep the M-item to measure real cars. |
| R5 | Two carry, four handle, ≤ 15 min assembly | **KEEP** (folded into C3 d–e) | Matches the team's words; numbers are still estimates. |
| R6 | ≤ $2,000 incl. tax and shipping, fixed | **KEEP** → C1 | The only hard constraint the team gave. |
| R7 | Second pack + spares; reserve = whatever remains, ≥ $100 | **CHANGE** → C1 | Reserve becomes a planned ≥ $150 line, not a residual; the previous design proved a residual shrinks to $24–145 as prices firm up. Second pack stays (a test day with one pack is a 20-minute day). |
| R8 | Flight-tested through transition by 2027-04-30 | **KEEP** → C4 | The team's date; milestones added. |
| R9 | Mission: hover–transition–cruise–land | **CHANGE** → §3 | Becomes an explicit assumption (M-A) with threshold and objective values, open to the team. |
| R10 | ≥ 10 min cruise + 2 min hover, 20 % reserve | **CHANGE** → §3 | 10 min becomes the objective; 5 min threshold lets cheaper, smaller layouts into the comparison. |
| R11 | Cruise 18–22 m/s, stall ≤ 12 m/s, transition ≥ 1.3 Vs | **CHANGE** | Keep ≥ 1.3 Vs transition (D11) and stall ≤ 12 m/s *only for layouts whose emergency mode is a fixed-wing landing*; drop the cruise band in favour of 1.3–1.6 Vs. |
| R12 | No payload | **CHANGE** → §3 | 0 payload, but a 0.25 kg growth allowance in sizing; "every gram counts" was the symptom of a design with zero margin (D14). |
| R13 | Hover T/W ≥ 1.6 on the maker's 22.2 V table | **KEEP** → D11 | Sourced and sensible; applies to every layout. |
| R14 | Lift-motor-out in cruise: continue as fixed wing (hard); in hover: desired | **CHANGE** | Generalise: any single propulsion failure in cruise must leave a controlled landing path (glide or VTOL); hover motor-out stays a scored desire. Layouts where one motor-out in hover is fatal are allowed but penalised in §5. |
| R15 | Pusher-out in cruise: re-enter hover and land | **CHANGE** | Generalise to "cruise-propulsion failure → return to hover"; for tailsitters and tiltrotors this is the same motors, so the requirement is a glide instead. |
| R16 | Steady 5 m/s, gusts 8 m/s | **KEEP** → D11 | Still an estimate; RFS is a bay-shore site. |
| R17 | Open-source autopilot with maintained VTOL support | **KEEP** → D7 | Also required by campus policy (logging). |
| R18 | FAA path: § 44809 educational or Part 107, TRUST, registration, RID module or FRIA, VLOS, 400 ft | **CHANGE** → D3, D4 | Two facts change it: the 2024 Act put higher-education use in the statute, and **RFS is a FRIA**, so the RID module becomes conditional. |
| R19 | Campus policy: 7 business days, $1 M, post-flight report, site ceilings | **CHANGE** → D5 | Add the RFS-specific process (PI sponsor, UC Drone Program registration, 72 h, sub-fields). |
| R20 | Arming switch / kill, RTL-then-land failsafe, geofence, AS150U disconnect | **KEEP** → D8–D10 | Generalise the connector rating to the chosen layout's current; add the emergency motor stop. |
| R21 | No full mission above 25 °C field ambient | **CHANGE** → D13 | Keep the principle (an ambient ceiling derived from thermal analysis and written on the flight card); drop the 25 °C, which belongs to the C0 motors, pack and bay. |

Net: 6 KEEP, 14 CHANGE, 1 DROP. Nothing in the old set was wrong in kind; most of it was a specific design's
numbers written as if they were requirements.

---

## 5. Evaluation criteria for comparing configurations

**Step 1 — gates (pass/fail, no score).** A layout that fails any gate is listed but not ranked.

| Gate | Test |
|---|---|
| G1 Budget | Priced BOM (tax, shipping, two packs, charger, radio, spares) ≤ $1,850; prices dated and sourced. |
| G2 VTOL | C2: zero-roll vertical take-off and landing in the D11 wind. |
| G3 Transport | C3 (a)–(c): boxes, 1.5 m piece, 15 kg per box. |
| G4 Buildable | Every part is bought or made with a C4 process; no composite mould, no custom machined metal beyond the Tormach/waterjet. |
| G5 Legal | D1 (< 25 kg) and D7 (supported autopilot mode). |
| G6 Mission threshold | §3 default: hover 2 min + cruise 5 min with 20 % reserve, T/W ≥ 1.6. |

**Step 2 — weighted score (0–10 per criterion against fixed anchors, weights sum to 100).**

| Criterion | Weight | Why this weight | Anchors (0 → 10) |
|---|---|---|---|
| Budget margin | **25** | The only hard constraint. Every other failure (crash, redesign, bad part) is paid for from the same $2,000, so margin here is margin everywhere. | 0: reserve $150 (just passes G1) → 10: reserve ≥ $500. Linear. |
| Buildability | **20** | Mentor: "buildability before simulation"; advisor's run never finished a part inventory. A first-time student team's throughput, not analysis, sets whether it flies. | Score = 10 − (count of: custom-machined parts, composite parts, parts > 300 mm printed, moving mechanisms with load (tilt servos, wing pivots), unique fasteners) capped at 0; ×0.5 if any part needs a process outside C4. |
| Flight risk / controllability | **20** | One airframe, one budget, one first-time pilot: a crash in March ends the project. Includes hover in wind, transition margin, motor-out behaviour, community evidence of the layout flying on ArduPilot/PX4. | 0: no documented hobby-scale builds flying the layout on the chosen autopilot, or any single motor-out fatal in hover *and* cruise → 10: ≥ 5 documented builds, hover T/W ≥ 2.0, gust tilt ≤ 15°, motor-out survivable in cruise. |
| Schedule to April 2027 | **15** | Fixed date (C4). Parts lead time, tuning effort and the number of distinct subsystems to debug. | 0: > 12 weeks estimated build + tuning after orders → 10: ≤ 6 weeks. Add −2 for each subsystem with no off-the-shelf tuning guide. |
| Transportability | **10** | A real constraint, but almost any layout under 2.5 m with a removable wing meets it; it differentiates little. | 0: just passes G3 with two boxes and 15 min → 10: one box ≤ 1.0 m, no tools, ≤ 5 min. |
| Mission fit | **10** | Low because the mission is an assumption (§3). Rises if the team fixes a mission. | 0: meets the §3 threshold only → 10: meets the objective (10 min cruise) with growth to M-B or M-C without a new airframe. |

**Step 3 — sensitivity.** Re-run the ranking with each weight × 0.7 and × 1.3 (12 cases, as the previous trade study
did). Report which layouts stay in the top two in every case; a winner that depends on one weight is not a winner.

**Step 4 — honesty.** Every score cell cites its evidence or is marked `ESTIMATE`. A layout with mostly `ESTIMATE`
cells gets a "confidence" column, not a better score.
