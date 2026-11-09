# K19 review (skeptic), 2026-11-09

Reviewer: skeptic agent. Scope: CARD.md, sizing.py, sizing.json and cost.csv in this folder. I did not edit the card.
I re-ran `python -I sizing.py`. It reproduces sizing.json exactly (MTOW 3.10 kg, hover 542 W, cruise 165 W, 17.4 min).
The arithmetic is consistent. My challenges are about the inputs.
Correction scenarios: scratch script `k19_check.py` (stdlib) with the same equations as sizing.py, run with the inputs
changed below. Tags: `ESTIMATE` = engineering guess, `UNVERIFIED` = unchecked claim (forum data counts as UNVERIFIED).

## Verdict
The concept survives. Budget, VTOL and transport all still pass after correction. The headline performance is
optimistic, though: **cruise is about 10 min, not 17.4 min**, and the **crash reserve is about $190, not $344**.
Every correction below points the same way (heavier, more power, more cost). None of them, taken alone, kills the
concept.

## Challenges

| # | Claim on card | Challenge and evidence | Corrected estimate |
|---|---|---|---|
| 1 | Hover 542 W / 39 A (maker table 6.6 g/W at 799 g) | The maker table is a clean static thrust-stand figure. It leaves out mounting losses, gust and attitude control, low-voltage running and hot motors. One real data point is an ArduPilot forum X8 quadplane: 4.2 kg AUW, 4S, 13 in props, about 58–60 A in hover (https://discuss.ardupilot.org/t/skywalker-x8-quadplane-build-4/42083, UNVERIFIED). Scaling it by momentum theory (P ∝ T^1.5/D) to K19 gives **≈ 660 W at 3.10 kg** and ≈ 720 W at 3.30 kg. That is 20–30 % above the card. | **≈ 640 W, ≈ 46 A** at 3.3 kg (between the table and the forum scaling, ESTIMATE). Measure it in the centre-section tether test. |
| 2 | T/W 2.04 | 1,580 gf is full throttle at 14.8 V. Under load at the end of the pack (≈ 13.2 V) thrust falls by about (13.2/14.8)^1.5. | T/W **1.92 fresh / 1.61 at low voltage** (3.3 kg). This is still at or above the study's 1.6 floor, with no margin left. |
| 3 | MTOW 3.10 kg, gate 3.26 kg | The build-up is credible: the 397 g of growth and contingency is 13 %, and the X8 EPO kit is ≈ 1.3 kg for 0.8 m², so 1.17 kg of structure for 0.5 m² of solid XPS plus booms is plausible. Three items look light. (a) Packing-tape skin at 60 g/m² assumes one layer; overlaps and the doubled LE/TE come closer to 80–100 g/m² (ESTIMATE; the card's own M2 weigh test is still pending). (b) Wiring at 130 g for a 4S system with a 145 A peak, 4 boom runs and 16 AWG motor leads (the 18 AWG listed is thin for 30 A full throttle). (c) Socket/insert hardware for the 22 mm joiner in foam (see #8). The advisor's run is the warning case: 3 kg grew to 6 kg. | **3.30 kg** expected first build (+6 %, ESTIMATE). The 3.26 kg gate will probably be exceeded on the first weigh-in. Set the gate at 3.4 kg or make trimming mass a planned task. |
| 4 | CLmax 0.75, Vs 11.6 m/s, transition at ≥ 15.0 m/s, cruise 16 m/s | 0.75 is the untrimmed-wing value. A tailless wing trims with up-elevon (reflex), and that lowers the usable CLmax. 0.60–0.65 is the usual range for trimmed flying wings (ESTIMATE). The card itself notes the X8 stalls around 14 m/s. | CLmax 0.65 at 3.3 kg gives **Vs 12.8 m/s, 1.3 Vs = 16.6 m/s, so cruise must be ≥ 17 m/s**. At 16 m/s the card's cruise sits inside the transition margin. |
| 5 | L/D 7.3, cruise 165 W | CD0 0.042 is reasonable: the card admits that 34 % of it is the 4 stopped props. Two inputs are optimistic. e = 0.80 is high for a low-AR (5.2) swept wing with stubby winglets and boom/pod interference; 0.70–0.75 is more likely. η_prop 0.55 for a 9×6 pusher running in the pod wake, with the stopped rear lift props 27–38 mm away, is also on the high side; 0.50 is more likely. A hand-made tape skin is wavier than EPO. | At 17 m/s, 3.3 kg, CD0 0.045, e 0.75, η_p 0.50: **L/D 6.6, cruise ≈ 227 W (≈ 15 A)**. |
| 6 | Endurance 17.4 min cruise; 8.5 min hover-only | Re-running with #1–#5 changed. I also assumed 60 s for the two transitions instead of 40 s: a clean, low-drag flying wing decelerates slowly on back-transition (ArduPilot `Q_TRANS_DECEL`). Usable energy is 75 Wh (6.5 Ah × 0.8 × ≈ 14.4 V average under load) instead of 77 Wh. | **Cruise ≈ 9.6 min, hover-only ≈ 7.0 min** (ESTIMATE). Pessimistic case (3.45 kg, CLmax 0.60, CD0 0.05, e 0.70, η_p 0.45, 700 W hover): **5.7 min**. The demonstrator mission (short cruise) is still met with good margin in every case. Do not quote 17 min. |
| 7 | Transition peak 864 W / 64 A; AS150U fine | With the corrected hover power the peak is ≈ 960 W / ≈ 71 A. ×1.25 (D9) gives ≈ 89 A, above the AS150U's 70 A continuous. A transition is short, so the burst rating covers it. | **≈ 71 A peak**. It is acceptable, but the claim should read "relies on burst rating" (fine with the card's own caveat). |
| 8 | Outer panel on a 22 mm joiner in XPS, one nylon thumb screw | Bearing check (my calculation). Each outer panel carries ≈ 33 % of lift (0.164 m² of 0.496 m²). At 4 g and 3.3 kg that is ≈ 42 N at ≈ 0.26 m arm, so ≈ 11 N·m root moment. Over a ≈ 0.15 m socket the couple is ≈ 100 N on a 22 × 30 mm bearing patch, ≈ 0.15 MPa. F-250 compressive strength is 25 psi ≈ 0.17 MPa (Owens Corning rating). Margin ≈ 1.1 with no factor of safety: bare foam will crush and the socket will go loose after a few hard landings or pull-ups. | A **glued-in sleeve (CF or paper tube) with ply ribs at the socket ends** is required, not optional. Add ≈ 40 g and ≈ 3 h. |
| 9 | Hand-glide the bare wing "ballasted to 3.1 kg" | At 3.1 kg the wing stalls at 11.6–12.8 m/s. A person throws at about 8–10 m/s, so this test would only stall the wing into the grass. The CG/reflex test is valid at **lower mass** with the same CG % MAC. | Glide at **≤ 1.5 kg** (Vs ≈ 8–9 m/s) with the CG at the same % MAC. Or skip the glide test and trim in flight under `Q_ASSIST`. |
| 10 | 95 h hands-on build, 3–4 weeks | The 20 h for FC configuration does not cover ArduPilot QuadPlane tuning (QAUTOTUNE, `Q_TRIM`, transition and back-transition tuning, weathervane). Builders usually need several flight sessions for that. Two more items are missing from the hour count: the joiner sleeves (#8), and Bluejay reflashing of the BLHeli_S ESCs for bidirectional DShot. | **≈ 120–140 h** (ESTIMATE). That is still the easy end of the study, inside the 12-week window. |
| 11 | Pusher-to-rear-lift-prop clearance | sizing.py gives 27 mm, worst case in plan view. The 9 in pusher runs in the 11 in rear props' wake in hover and in their disturbed flow in cruise. The result is noise, vibration and lower η_p (already in #5). A blade strike risk exists if a boom twists in a hard landing. | Accept, but tolerances must be checked after every crash repair. Moving the rear motors aft (BOOM_DX 0.40–0.42) costs ≈ 5 cm of packed length, which still fits in 1.2 m. |
| 12 | Packed one box 1.2 × 0.5 × 0.4 m, longest piece 1.06 m | Fits a back seat (≈ 1.3 m wide) and most sedan trunks sideways. The centre section carries 4 motors and props exposed. Props parked fore-aft are fine, but they need foam blocks or should be removed, which adds about 2 min at the field. The box itself is not in the BOM (coroplast or cardboard, ≈ $0–20). | **Claim stands.** Assembly ≈ 8–10 min including prop checks (ESTIMATE). |
| 13 | Controls: ArduPilot QuadPlane on CoreWing F405 Wing V2, Plane 4.7 beta | ArduPilot now has an official board page (https://ardupilot.org/plane/docs/common-CoreWingF405WingV2.html). Bidirectional DShot is on outputs 1–4 only, which matches the 4 lift motors. Earlier forum threads say support came only from vendor .hex builds (https://discuss.ardupilot.org/t/corewing-v2-support/145339). An F405 also has 1 MB flash, so some features are stripped. Flying-wing quadplanes are proven (DeltaQuad commercially; many X8 ArduPilot builds, e.g. https://discuss.ardupilot.org/t/a-tale-of-two-quadplanes/18856). So control risk is moderate, not high. The real risks are the ones the card lists: pitch trim at transition with elevons only, and weak yaw in gusts. | Control risk **3/5**. Mitigation: check on the firmware server that a **stable** (not beta) Plane build exists for this board before ordering. Fallback: Matek F405-WING / H743-WING (+$20–60). |

## Cost: missing or understated lines

| Line | Evidence | Δ goods |
|---|---|---|
| Ovonic 4S 6500 50C ×3. Card uses $45.42 each; listing is out of stock | Ampow US listing $59.91 (ships from EU, so a lead-time risk) seen 2026-11-09 in search results, https://www.ampow.com/products/ovonic-50c-14-8v-6500mah-4s1p-hardcase-14-deans-lipo-battery; rcdrone.top lists $130.56. Pack mass 522 ± 20 g confirmed (https://rcdrone.top/products/ovonic-4s-6500mah-lipo-battery) | +$43.47 (+$97 if bought from a US stocker at ~$78) |
| 2 spare 22 × 20 × 1000 CF tubes. All 3 tubes bought are consumed exactly (2 booms + spar), and they ship from overseas | cost.csv's own price $28.32 | +$56.64 |
| LiPo cell checker / buzzer | ESTIMATE | +$8 |
| FAA registration | $5, 3 yr (https://www.faa.gov/uas/getting_started/register_drone; fee from third-party guides) | +$5 (no tax) |
| More shipping: ≈ 10 vendors, LiPo ground shipping, EU-shipped packs | ESTIMATE | +$30 |
| Iron for AS150U / 10 AWG joints (a Pinecil is marginal on large connectors) | ESTIMATE; or borrow at Jacobs | $0–40 (not counted) |
| **Jacobs Hall Maker Pass** | $125 per student per semester, 50 % off for student groups, waivers available (https://jacobsinstitute.berkeley.edu/making-at-jacobs/get-maker-pass/). It may be covered by the capstone course (UNVERIFIED) | CONDITIONAL, $0–250 |

Corrected total: $1,655.60 + $108.11 goods + $11.08 tax + $5 + $30 shipping = **≈ $1,810 → reserve ≈ $190** (≈ $230
without the conditional RID module). This is above the card's $150 planning floor but below one "bad crash"
($310, cost_model.py). If the team must pay for Maker Passes, the reserve falls to $0–65. **Confirm Maker Pass
coverage with the course before the December order.**

## Numbers I believe (corrected)

| Item | Card | Believed |
|---|---|---|
| MTOW | 3.10 kg | **3.30 kg** (ESTIMATE) |
| Span / packed | 1.60 m / 1.2 × 0.5 × 0.4 m box | 1.60 m / **same box** |
| Hover power / current | 542 W / 39 A | **≈ 640 W / ≈ 46 A** |
| Hover T/W | 2.04 | **1.9 fresh, 1.6 at low voltage** |
| Stall / min transition / cruise | 11.6 / 15.0 / 16 m/s | **12.8 / 16.6 / 17 m/s** |
| Cruise L/D / power | 7.3 / 165 W | **6.6 / ≈ 230 W** |
| Cruise endurance (2 min hover, 2 transitions, 20 % reserve) | 17.4 min | **≈ 10 min** (pessimistic 6) |
| Hover-only endurance | 8.5 min | **≈ 7 min** |
| Cost / reserve | $1,656 / $344 | **≈ $1,810 / ≈ $190** (Maker Pass conditional) |
| Build hours | 95 h | **120–140 h** |
| Build difficulty (1–5) | — | **2.5** (hot-wire foam, bought parts) |
| Control risk (1–5) | — | **3** (tailless transition trim, hover yaw) |

## Must-do before December order
1. Check that a stable ArduPilot Plane build exists for the CoreWing F405 Wing V2. If not, switch to a Matek board.
2. Buy 2 spare CF tubes and price the LiPos from a US stocker (both have overseas lead times).
3. Confirm whether the course covers Maker Passes.
4. Redesign the joiner socket (#8) and replan the glide test at ≤ 1.5 kg (#9).

Sources: https://discuss.ardupilot.org/t/skywalker-x8-quadplane-build-4/42083 ·
https://discuss.ardupilot.org/t/a-tale-of-two-quadplanes/18856 ·
https://ardupilot.org/plane/docs/common-CoreWingF405WingV2.html · https://discuss.ardupilot.org/t/corewing-v2-support/145339 ·
https://rcdrone.top/products/ovonic-4s-6500mah-lipo-battery ·
https://www.ampow.com/products/ovonic-50c-14-8v-6500mah-4s1p-hardcase-14-deans-lipo-battery ·
https://jacobsinstitute.berkeley.edu/making-at-jacobs/get-maker-pass/ · https://www.faa.gov/uas/getting_started/register_drone
