# H3 compliance: FAA, UC Berkeley, Richmond Field Station (RFS)

Revision H3-R1, 2026-11-13. Status `PROPOSED`; **nothing below has been filed.** Owner H3 (safety officer). Requirements: `R-LEGAL`, `R-SITE` (`team/A2/REQUIREMENTS.md`).
This page is engineering guidance for the team, not legal advice. Where a source could not be read it says so; every item to be filed is a person's job (section 6).
Dates in the Source column are the day the page or search was read (2026-11-13). `faa.gov` pages returned HTTP 403 to the automated fetch, so FAA statements are taken from the eCFR (fetched) or from search results of the FAA page (flagged `search`).

## 1. What the aircraft is

| Fact | Value | Source |
|---|---|---|
| Take-off mass | <= 2.6 kg gate (5.7 lb); legal limit < 25 kg (55 lb) | `requirements.mtow_gate_kg`, `requirements.mass_max_legal_kg`; `CLAUDE.md` |
| Use | UC capstone course project: recreational / educational exception, 49 U.S.C. 44809, with TRUST | `config-study/README.md` line 44 (the team's own reading) |
| Home-built, no Remote ID module fitted | module `X06` ($44.09) is gated, bought only if flown outside the FRIA | `team/I1/ORDER-PLAN.md`; `HANDOFF.md` |
| Payload, camera | none; GPS is receive-only; no video transmitter | `mission.payload_kg`; `../F5/RC-LINK.md` |

## 2. FAA requirements and status

| # | Requirement | What the rule says | Source | Status |
|---|---|---|---|---|
| 1 | **Registration** | A small unmanned aircraft may be flown only if registered and marked, except one flown only under 49 U.S.C. 44809 that weighs 0.55 lb (250 g) or less at take-off. K09-L is 5.7 lb, so it must be registered | 14 CFR 48.15, eCFR fetched 2026-11-13 (https://www.ecfr.gov/current/title-14/part-48/section-48.15) | **to do** |
| 2 | Registration fee and term | $5, three years, one registration number covers all a recreational flyer's aircraft (secondary guides read by search; the eCFR Part 47 and 48 text fetched did not state the Part 48 fee) | search 2026-11-13; `team/I1/build_bom.py` `FAA_FEE` 5.00; FAA DroneZone is the payment page (https://faadronezone-access.faa.gov) | confirm the amount on the DroneZone payment page before paying |
| 3 | **Marking** | The registration number must be legible, securely attached and displayed on an external surface for the whole operation | 14 CFR 48.205, eCFR fetched 2026-11-13 | the label is `WNG-020` (right upper skin, x 115-215 mm, y 375-405 mm; clear tape round the edge, `wing/BUILD.md` step 13) |
| 4 | **Remote ID** | An aircraft that must be registered may be operated only with Remote ID (standard, or a broadcast module with the owner's registration) or inside an FAA-recognised identification area (FRIA) | 14 CFR 89.105, 89.110, 89.115, eCFR fetched 2026-11-13; FAA page https://www.faa.gov/uas/getting_started/remote_id (403, search only) | RFS only: see rows 5 and section 3 |
| 5 | **FRIA** | In a FRIA a UA without Remote ID may fly only if both the aircraft and the person at the controls stay inside the boundary for the whole operation and the pilot can see the aircraft at all times. RFS is reported as a FRIA (the only one in the Bay Area at the time of the source). Approvals last 48 months | 14 CFR 89.115(b), eCFR fetched 2026-11-13; FAA FRIA page https://www.faa.gov/uas/getting_started/remote_id/fria (search 2026-11-13); RFS status from search of UC pages (not confirmed on an FAA page) | **verify RFS on the FAA UAS Data Delivery System map before the first flight and file a screenshot** (https://udds-faa.opendata.arcgis.com/datasets/faa::faa-recognized-identification-areas/about); expiry date `-` |
| 6 | **TRUST** | Every recreational flyer takes the free online TRUST and carries proof | FAA recreational flyers page https://www.faa.gov/uas/recreational_flyers (search 2026-11-13); 49 U.S.C. 44809 | each pilot: **to do** |
| 7 | **Airspace** | Check the FAA UAS facility map for the RFS flying area once and record the airspace class and any ceiling; fly within it | `R-LEGAL`; FAA UAS facility map (B4UFLY / LAANC) | class and ceiling: `-` (not looked up) |
| 8 | **Limits that apply** | <= 400 ft AGL, visual line of sight, no flight over people, daylight | `R-SITE`; `mission.ceiling_ft_agl`; FAA recreational flyers page (search) | built into the flight card |
| 9 | If the team ever flies outside the FRIA | buy `X06` (NewBeeDrone BeeID, $44.09) and register its serial with the aircraft, or fly only inside a FRIA | `team/I1/ORDER-PLAN.md` X06; 14 CFR 89.110 | not planned |

## 3. UC Berkeley and RFS rules

Source: UC Berkeley Unmanned Aircraft System (Drone) Policy, https://oercs.berkeley.edu/policies/campus-policy-library/unmanned-aircraft-system-drone-policy (fetched 2026-11-13); RFS services page https://rfs.berkeley.edu/services.html (fetched 2026-11-13).

| # | Rule | Status |
|---|---|---|
| 1 | File a **UAS Flight Request Form at least seven business days before** any on-campus outdoor flight; UCPD and Risk Services evaluate; the **RFS facility manager** approves use of RFS | to do, per flying block (`../I2/SCHEDULE.md` `TW2`, `FR1`) |
| 2 | RFS asks for a flight request at least **72 hours** ahead ("Reserve a flight window" on the RFS services page) | to do, in addition to the campus form |
| 3 | RFS recreational use is limited to **designated areas** (yellow sub-fields 1-4 per `env.site`), **<= 400 ft AGL**, **6 a.m. to sunset** | in the flight card |
| 4 | **Spotters** keep non-participants out of the operations area | crew role (`../H2/FLIGHT-TEST-PLAN.md`) |
| 5 | A drone over half a pound needs a **flight management system** with a way to report injury or property damage to UCPD promptly | the ArduPilot autopilot is the flight management system; the reporting number is **UCPD 510-642-6760** (on the flight card) |
| 6 | Recreational use is restricted to **Registered Student Organizations and their advisors, and UC courses (including senior projects) that build or fly drones**; operators must be currently registered UC students, staff or faculty | the team must be listed as a course project or RSO: **ask the capstone instructor** |
| 7 | Operators maintain liability insurance: recreational users need **>= $1 million per occurrence, which AMA membership can satisfy** | see section 4 |
| 8 | The pilot and the drone must register with the FAA; the registration number is on the drone (and the AMA number if applicable) | section 2 |
| 9 | **Post-flight report to UCPD within 3 business days** (date and time of all flights, pilot names, drones flown, accidents or violations); accidents causing injury or property damage are reported to UCPD immediately | template in `../H2/templates/flight_log.csv` plus a one-page report |
| 10 | Register aircraft and pilots in the **UC Drone Program** under a PI sponsor (`R-LEGAL`); the UC systemwide app is https://ucdrones.github.io/ (search 2026-11-13) | **to do**: needs a faculty PI sponsor |
| 11 | RFS staff work only after the "Working at RFS" EHS training for anyone with key access | ask RFS whether the team needs it |

## 4. Money items that are not in the BOM

| Item | Amount | Basis | Decision |
|---|---|---|---|
| AMA membership for the pilot (R-LEGAL asks for it per pilot; UC accepts it for the $1 million liability line) | **$89 per adult member per year** (AMA enrolment page, read by search 2026-11-13; an older page showed $85); one pilot = $89, two = $178 | https://www.modelaircraft.org/membership/membership-options (search) | **not in `team/I1/BOM.csv`, and the reserve cannot absorb it** (pessimistic reserve $283.72, all-in $20.45). First ask UC Risk Services whether UC cover satisfies the $1 million line for a course project; if not, the owner decides who pays (`CR-H3-01`) |
| FAA registration | $5 | section 2 row 2 | already in the BOM as the FAA fee |
| TRUST | free | FAA page (search) | none |
| Anemometer for `R-WIND-MEASURE` | $20-30 estimated by the tie-break, no BOM line | `config-study/tiebreak/DECISION.md` | `CR-H3-02` |

## 5. Gate to the first flight (all must be ticked)

| # | Item | Done | Evidence |
|---|---|---|---|
| 1 | FAA registration number on the airframe (`WNG-020`) | - | photo + DroneZone receipt |
| 2 | TRUST certificate for each pilot | - | PDF |
| 3 | UC Drone Program registration under a PI sponsor | - | confirmation |
| 4 | $1 million liability cover confirmed (UC cover or AMA) | - | email or membership card |
| 5 | Course project or RSO status accepted by UC for RFS flights | - | instructor email |
| 6 | RFS FRIA status checked on the FAA map; airspace class recorded | - | screenshot, class `-` |
| 7 | Flight request >= 7 business days (campus) and 72 h (RFS) accepted for the day | - | request id |
| 8 | Flight card signed for the day | - | `FLIGHT-CARD.md` section 6 |
| 9 | Post-flight report filed within 3 business days | - | copy |

## 6. People to act (not Claude)

Pilot: TRUST, AMA, registration of themselves. Team lead: PI sponsor, course status, UC Drone Program entry, the money decision in section 4. Safety lead: FRIA and airspace check, flight requests. Instructor or advisor: confirmation of the course status.

## 7. Change requests from H3

| # | To | What |
|---|---|---|
| CR-H3-01 | A1, owner | Decide how the AMA / liability line is met (UC cover or $89 per pilot) before the first twin flight (about 8 Dec, `../I2/SCHEDULE.md`) |
| CR-H3-02 | I1 | Add or borrow an anemometer |
| CR-H3-03 | A2 | `R-LEGAL` also needs "course project or RSO status" and "airspace class recorded" as evidence rows; both are in section 5 |
