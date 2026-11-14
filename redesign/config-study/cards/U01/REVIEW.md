# U01 skeptic review (2026-11-09)

Reviewer role: skeptic. I tried to refute the card's numbers and claims. I did not edit the card. The re-runs used
copies in a scratch folder, so the card's `sizing.json` is untouched.

## 0. Reproduction

`python -I sizing.py` (copy) reproduces the card's `sizing.json` exactly (diff empty). MTOW is 2.712 kg, hover is
356 W / 24.0 A, cruise at 14 m/s is 140 W (9.4 A), and the box is 0.65 × 0.44 × 0.38 m. **The card's numbers are what
its script says. The question is whether its inputs hold up.**

Corrected run (`ESTIMATE`, same script, six inputs changed): FM 0.65→0.60, η 0.80→0.78, K_UPWASH 0.5→1.0, wing CD0
0.020→0.030, body CdA 0.025→0.030 m², motor 100→81 g (vendor listing, §2).

| Output | Card | Corrected run | Verdict |
|---|---|---|---|
| MTOW | 2.71 kg | 2.64 kg (2.70 ± 0.15 believed, §2) | holds |
| Hover | 356 W / 24 A / 13.0 min | 379 W / 25.6 A / **12.2 min** | slightly optimistic |
| Current saving vs bare quad, 12 m/s | 52 % | 25 % (model); **~19 % measured on a similar build** (§1) | **refuted, about ½ to ⅓** |
| Current saving at 14 m/s | 48 % | 24 % (model); the flight test shows only +6.9 % range at 16.8 m/s | refuted |
| Cruise at 14 m/s with wing | 140 W / 33 min | 230 W / **20 min** | refuted (optimistic by 1.6×) |
| Wing lift at 6 m/s | +4 % W | **−19 % W** (wing in the rotor inflow at negative AoA) | new risk, §4 |
| Gust 5→8 m/s hover, ΔL | −5 % to +20 % W | −21 % to +21 % W | worse |
| M-A mission (2 min hover + 10 min cruise) | met | still met (2 min hover + ~17 min cruise left) | holds; the bare quad also meets it |

## 1. Forward-flight saving: the headline claim does not survive

- **Challenge.** The card says the wing cuts current by 48 % at 14 m/s and by 52 % at 12 m/s. It also says "there is no
  documented fixed-wing-on-quad build with logs".
- **Evidence.** A documented flight test does exist. Su, Mei, Zhou, Shan, Yu & Wang, "Flight Performance Characteristics
  of a Modified Quadcopter with and Without a Wing Based on Flight Test", AIAA 2023 (DOI 10.2514/6.2023-2103;
  preprint https://engrxiv.org/preprint/view/7362). The configuration matches U01: a lifting wing fixed at a **30°**
  setting angle on a quad. The abstract reports **18.97 % power saving at the max-endurance speed (10.1 m/s)** and
  **+6.9 % range at 16.78 m/s** compared with the same quad without the wing. I read the abstract only; the PDF body
  could not be parsed (`UNVERIFIED` beyond the abstract). Other builds that report ~50 %
  (https://arxiv.org/pdf/2006.15579, Beihang lifting-wing multicopter; Oslo thesis
  https://duo.uio.no/handle/10852/100013) use a **much larger wing** that carries most of the weight, and they
  compare against *hover* power, not against the same quad in forward flight. Those figures are not comparable to
  U01's 1.2 m add-on wing. The add-on folding-wing extender in MDPI Drones 9(12):877 (2025) reports about 20 % at
  20 m/s (abstract only).
- **Model issue.** K_UPWASH = 0.5 is the input that drives the result. With full inflow (1.0) the trimmed wing sits
  near 0° AoA and carries only 20–25 % of the weight, not 49 %. The card's own pessimistic set gives 15 %.
- **Corrected estimate.** About **20 % saving at 10–12 m/s, falling to 5–10 % at 16 m/s** (`ESTIMATE`, anchored on
  Su et al.). The screen's ≥ 20 % pass condition is **a coin flip at best**, not a likely pass. The day-1 test is still
  the right gate, but the card's prior should be about 20 %, not 50 %.

## 2. Mass realism

- Holybro X500 V2 frame: **610 g, 500 mm wheelbase, 215 mm gear, 16×16 motor pattern**. Multiple vendor listings
  agree (getfpv https://www.getfpv.com/holybro-x500-v2-frame-kit.html; Holybro docs
  https://docs.holybro.com/drone-development-kit/px4-development-kit-x500v2). Holds.
- SunnySky X3108S KV900: one vendor listing gives **81 g**, 25 A continuous and 370 W
  (https://robu.in/?p=1569817; vendor, not a SunnySky datasheet). The card's 100 g is about 76 g too heavy for four
  motors.
- Items missing or light: wing-root joiner protrusion and sleeve (see §5), battery strap and pad, antenna mounts,
  Remote ID wiring, the 2 kg-class prop-adapter screws. Together they roughly offset the motor saving.
- **Believed MTOW: 2.70 ± 0.15 kg.** This includes 0.25 kg growth, so the margin is honest.

## 3. Hover power and endurance

- Momentum check by hand: T = 2.71 × 9.81 × 1.03 = 27.4 N, A = 0.245 m², P_ideal = 27.4^1.5/√(2·1.225·0.245) =
  185 W. The script agrees.
- FM 0.65 at η 0.80 gives 7.6 g/W at the system level. That sits at the top of the range for 11 in props at about
  0.68 kg per motor on a frame with arms and gear tubes under the disks. FM 0.60 / η 0.78 is a more defensible central
  value: **~380 W, ~26 A, 12 min hover** on 77 Wh usable. T/W ≈ 2.2 still clears 1.6, but the thrust is `UNVERIFIED`
  (no X3108S-900KV + APC 11×4.5MR table found), so the bench thrust stand in the BOM is needed before first flight.
- Smaller model issue: the profile term uses a fixed 100 m/s tip speed. At cruise thrust (about half of hover) RPM drops
  about 28 %, so μ is underestimated and the profile power is low by a few percent. The low-pitch 11×4.5 prop running
  with 4 m/s or more of axial inflow at 14–16° nose-down is also off its design point (`ESTIMATE`). Both errors make
  the model optimistic.

## 4. Controls risk

- **Lower than other VTOLs, but not zero.** Su et al. report that the lifting wing had an "insignificant effect on
  controllability and stability" (abstract). ArduCopter QUAD/X is the most mature, best-documented path a student
  team can take. **Control risk is 2/5**, the lowest of any VTOL-like option.
- New finding: with full inflow on the wing, the wing's lift swings from **−19 % W at 6 m/s to +25 % W at 13 m/s**,
  so it changes sign through the speed range the vehicle accelerates through. The altitude loop must absorb about
  45 % of the weight change over ~7 m/s. The card says "drop throttle by about 50 % between 6 and 12 m/s". The size is
  right, but the sign change at low speed is not mentioned. Fly the first passes in AltHold and then Loiter, with a
  conservative `ANGLE_MAX`.
- Tailwind in hover puts the 25° wing at about −25° AoA (stalled, downward). This is not modelled. With T/W ≈ 2.2 it is
  survivable, but the pilot must keep the nose into wind (the card says this; ArduCopter has no weathervane, which is
  correct).
- FC: ArduPilot does document the CoreWing F405 Wing V2
  (https://ardupilot.org/plane/docs/common-CoreWingF405WingV2.html). It is a 1 MB-flash F405, so ArduCopter builds
  for it have reduced features. That is acceptable for QUAD/X. The board has had naming confusion with the SpeedyBee
  F405 Wing (https://discuss.ardupilot.org/t/corewing-v2-support/145339), so confirm the Copter build exists on
  firmware.ardupilot.org before ordering (`UNVERIFIED`).

## 5. Packability and geometry

- **Inconsistency.** The longest piece is listed as 0.60 m (a wing half), yet each half has a glued 0.55 m stub that
  plugs into a 0.30 m sleeve in the saddle. Either the stubs protrude about 0.15 m from the wing root, which makes the
  piece about **0.75 m** long, or the halves sit about 0.30 m apart, which makes the span about 1.5 m and changes S, AR
  and the mass. The card must pick one.
- **Corrected packed box: ~0.80 × 0.44 × 0.38 m**, one box, about 4.5 kg. This still fits a car trunk easily.
  Transport is a genuine strength of U01: the quad travels whole, and assembly takes about 5 minutes.
- Tape-skinned XPS halves dent in transport. Pack them in a foam-lined sleeve. Keep a spare half (foam sheet already
  bought).

## 6. Cost: missing and doubtful lines

| Item | Card | Correction | Δ pre-tax | Source / status |
|---|---|---|---|---|
| SunnySky X3108S 900KV ×5 (4 + spare) | $24.99 | $29.99 (KV720 regular price; 900KV price not found) | +$25 | buddyrc.com KV720 listing, 2026-11-09, `ESTIMATE` |
| 2× 18650 cells + charger for the RadioMaster Pocket (cells not included) | — | add | +$15 | `ESTIMATE` |
| FAA registration | — | add | +$5 | faa.gov fee |
| X500 V2 spare arm set (arms are the first part to break) | — | add | +$30 | `ESTIMATE` |
| LiPo checker / alarm + charge lead adapters (AS150U ↔ charger) | — | add | +$18 | `ESTIMATE` |
| Charger | HTRC C150 | OK: AC 100–240 V input, 150 W, so no PSU needed | 0 | pyrodrone listing |
| Tax on additions (10.25 %) | | | +$10 | |
| **Total added** | | | **≈ +$103** | |

- **Corrected committed cost ≈ $1,626**, leaving **≈ $374** for crashes (≈ 1.4 bad crashes at the card's $275). That is
  still inside the $2,000 budget, with the thinnest margin of any bought-frame option.
- Operational note: one 150 W AC charger takes about 45 min per 6500 mAh pack and gives no field charging, so expect
  3 flights per test day.

## 7. Buildability and schedule

- 55–65 h to first hover is plausible for bought parts. Add 10–20 h for the 16×16 → X3108 motor adapter (the pattern
  is `UNVERIFIED`), the ArduCopter tune done twice (bare and winged), and the wing saddle iteration. **≈ 70–85 h, 3
  weeks.** That is still the fastest build in the study and fits the 12-week worst case comfortably. Crash repair
  takes about a day (bolt-on arms, foam halves). Lead times: Holybro and SunnySky are in stock at US vendors; APC
  props ship domestically. Low risk.

## 8. Mission fit (the decisive issue)

The team lead's mission is: vertical take-off, **transition to forward flight**, a short cruise, **transition back**,
vertical landing. U01 has no transition. Its rotors always carry ≥ 75 % of the weight (corrected), so it is a
quadcopter carrying a wing. The card flags this honestly as risk 1. I am stronger on it: **as specified, U01 does not
meet the stated mission.** It only qualifies if the team explicitly redefines "transition" as tilt-body
partial wing-borne flight. If the team wants a real demonstrator in this family, the documented ~50 % lifting-wing
designs (Beihang, arXiv 2006.15579) need a wing that carries most of the weight, which means a larger S and a bigger
pitch-over. That is a different and riskier concept. U01's real value is as the **trainer and test bed**, which takes
up about 70 % of the BOM and transfers to any concept.

## Numbers I believe (corrected)

| Field | Value |
|---|---|
| Take-off mass | 2.70 kg (± 0.15, incl. 0.25 growth) |
| Span | 1.2 m (1.5 m if the joiner gap is real) |
| Hover endurance (80 % usable) | ~12 min |
| Cruise endurance, 14 m/s, wing on | ~20 min (bare quad ~15 min: 20.5 A × 14.8 V = 303 W) |
| Saving vs bare quad | ~20 % at 10–12 m/s, ≤ 10 % at ≥ 16 m/s |
| Cost committed | ≈ $1,626, leaving ≈ $374 for crashes |
| Packed | 1 box ~0.80 × 0.44 × 0.38 m, ~4.5 kg |
| Build difficulty | 2/5 (≈ 70–85 h) |
| Control risk | 2/5 |
| Mission fit | **Fails** the stated transition mission unless "transition" is redefined |
