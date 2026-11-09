# K09 skeptic review (2026-11-09)

Reviewer role: skeptic. I did not edit the card files; this file is append-only.
Scope: CARD.md, sizing.py, sizing.json and cost.csv, checked against the only real constraints in STUDY-BRIEF.md
($2,000 hard budget, VTOL, easy to transport, student-built, ~12-week build).

## 0. Reproducibility: PASS

I copied `sizing.py` to a scratch folder and ran `python -I sizing.py` with Python 3.14.2. The `sizing.json` and
`cost.csv` it wrote are **byte-identical** to the card's files. The arithmetic is consistent: 2.382 kg, 335 W, 22.6 A,
26.9 / 14.5 min, $1,528.51.

To produce the corrected numbers below, a scratch script imported the card's own `size()` and changed only the
inputs listed in section 9. The card's model is unchanged.

## 1. Verdict in one table

| Number | Card | Reviewer believes | Why (section) |
|---|---|---|---|
| MTOW | 2.38 kg | **2.43 kg** (range 2.3–2.6) | The pack is probably lighter than 680 g, but the fin-tube junction and build overrun are missing (§2) |
| Hover power / current | 335 W / 22.6 A | **355 W / 24 A** | Download 1.02 → 1.06, since the tube crosses each slipstream (§3) |
| T/W (table) | 2.65 | **2.6** | Follows from the MTOW above |
| Cruise power | 140 W | **~195 W** | The motors run at ~25 W each in cruise; η_motor 0.80 → 0.72 and η_prop 0.55 → 0.47 (§4) |
| Cruise after 2 min hover | 26.9 min (pess 14.5) | **~19 min (pess 12)** | §4. It still clears the 10 min objective |
| Hover-only endurance | 13.8 min | **13.0 min** | §3 |
| Gust lean 5 / 8 m/s | 16° / 37° | **16° / 36°** (method accepted) | §5 |
| Cost at order time | $1,528.51 | **~$1,632** | 18650 cells for the radio, connector re-termination, a real transport box, hot-wire jig, FAA registration (§6) |
| Reserve left | $471 | **~$368** | It still covers one bad crash (~$309) |
| Packed size | 1.2 × 0.5 × 0.4 m box | **~1.25 × 0.55 × 0.45 m box (external)** | The card's box has no room for walls or foam (§7) |
| Hands-on build to first hover | ~70 h | **~70–85 h to first hover; +30–40 h of flight-test sessions to a clean transition** | §8 |
| Control risk | "roll is the weak axis" | **4/5**. Cheapest fix: add 2 elevons | §8 |

Overall: the concept survives. The budget and transport claims hold with margin. The weak points are the
**cruise efficiency** (overstated by ~40 %) and **motor-only roll authority in cruise**, which the card
underplays.

## 2. Mass realism

| Challenge | Evidence | Correction |
|---|---|---|
| The 680 g OVONIC 4S 6500 pack mass is UNVERIFIED and may be **too heavy** | Reseller listings for OVONIC 4S 6500 hard-case packs give **503 g (±5)** and **522 g**, with conflicting C-ratings ([rcdrone.top 6500 4S](https://rcdrone.top/products/ovonic-6500mah-4s-lipo-battery), [rcdrone.top 6500](https://rcdrone.top/products/ovonic-6500mah-lipo-battery), seen 2026-11-09, reseller data `UNVERIFIED`) | Use **0.55 kg** until a pack is weighed. This saves 0.13 kg |
| Fin construction: "two layers of foam board sandwiching the 22 mm CF tube" is not physically flat. The faces sit 22 mm apart at the LE, so the fin needs a spacer, a wedge or a filler | Geometry: 2 × 4.8 mm board over a 22 mm tube. A filled 22 mm XPS fin would be ~0.2 kg for the pair | Add **+0.08 kg** `ESTIMATE` for printed clips/spacers and epoxy at the tube-fin and tube-spar joints. Alternative: one foam-board layer with the tube clipped to the LE (lighter, but the joint needs more design) |
| Growth of 0.25 kg (~11 %) is thin for a first student foam build. The advisor's XV-24 run went 3 → 6 → 10.8 kg | ADVISOR-XV24-LESSONS.md. Pack re-termination, repair tape and glue reliably add weight | Add **+0.10 kg** of build overrun `ESTIMATE`. The card's own +0.30 kg sensitivity (21.8 / 11.7 min) remains a sensible worst case |
| Comparable aircraft | A hobby 3D-printed quad tailsitter with a **1.15 m span and no moving surfaces** reports an AUW of up to 4 kg (LinkedIn post via search, `UNVERIFIED`, printed structure). HKUST/HKU quadrotor tail-sitters (Lyu et al., ICRA 2017; Xu et al., [arXiv 1903.06393](https://arxiv.org/pdf/1903.06393)) fly on differential thrust only; I could not extract their masses | 2.4 kg for hot-wired XPS plus foam board is **plausible**, lighter than a printed airframe. Accept it with the corrections above |

Line items I checked and accept: XPS core 0.211 kg (30 kg/m³ is conservative for F-250), tape 65 g/m², spar,
motors (X3108S 81 g), avionics 0.14 kg and printed parts 0.126 kg.

**Corrected MTOW: 2.43 kg.** Empty without pack or growth: 1.63 kg (card: 1.45 kg).

## 3. Hover physics

- **Table method:** at 607 g per motor, the operating point sits below the first table row (690 g / 89 W). The card
  extrapolates linearly through zero. Power actually scales roughly as T^1.5, which gives about 73 W against the
  card's 78 W, so the card is slightly conservative. It also divides by ESC_EFF again, which is conservative too.
- **Momentum check:** ideal power is 38.6 W per motor, set against 78 W electrical. That implies an overall
  efficiency of 0.49 (FM 0.60 × η_motor 0.82), which is reasonable for an 11 in prop at DL 95 N/m². **Accepted.**
- **Prop mismatch:** the table is for APC 11x4.7 but the BOM buys 11x4.5MR. The difference is small but the claim
  is `UNVERIFIED`. Confirm it on the card's own thrust stand.
- **Download 1.02 is optimistic.** The 22 mm motor tube runs radially through the slipstream behind every prop
  (0.022 × 0.14 m, about 5 % of the disc), and the fin edge and feet sit in the wake. At Cd ≈ 1 and near-disc
  dynamic pressure, that costs about 3–5 % of thrust. **Use 1.06.**
- Result: **355 W, 24.0 A, 13.0 min hover-only**. At ~3.7C on a 6500 pack, current is not a concern.

## 4. Cruise efficiency: the card's largest error

The card uses η_prop 0.55 and η_motor 0.80 in cruise. Total cruise thrust is ~3.9 N × 1.05, which is **about 1 N
per prop**.

- **Prop:** for an 11x4.5MR at 14.5–15 m/s and 1 N, Ct ≈ 1/(ρn²D⁴) needs n ≈ 100–105 rps, so J ≈ 0.5. That is
  just short of the zero-thrust advance ratio of a P/D 0.41 multirotor prop. At that point η is about **0.45–0.50**,
  below the 0.55 peak. `ESTIMATE`; check against the APC PER3 data file for 11x4.5MR.
- **Motor:** each motor runs at ~6,000 rpm and ~25 W shaft power, a small fraction of its 450 W rating. No-load
  (iron) loss of ~0.6–1 A per motor is about 5 W each, 20 W across four motors. η_motor is therefore about
  **0.70–0.75**, not 0.80.
- Corrected base is η_prop 0.47 and η_motor 0.72. That gives **~194 W cruise and 19.2 min after 2 min hover**.
  The pessimistic case (η_prop 0.35, CD0 × 1.3, η_motor 0.72) gives **12.0 min**.
- On the 4S 4000 fallback, the corrected figures are 11.4 / 7.1 min. **The fallback misses the 10 min objective
  in the pessimistic case.** Keep the 6500 pack.
- Cruise L/D of 5.9 is accepted. The drag build-up is already pessimistic: the fins and tubes drag as much as the
  wing does.
- **Cheaper improvement:** stop the trailing lower or upper pair in cruise, or swap to a higher-pitch prop. The
  first conflicts with `Q_TAILSIT_ENABLE 2` (all motors kept for control), so it is only possible with elevons
  (see §8).

## 5. Hover in wind and stance

- The flat-plate check reproduces: 17.3 N against 23.4 N weight gives 36.5°. With the corrected MTOW it is 36°.
  I accept the method. It is conservative, because a tailsitter that weathervanes and pitches into the wind gets
  some wing lift.
- **Parameter name:** the ArduPilot tailsitter guide calls the pitch limit **`Q_A_ANGLE_MAX` (degrees)**, with
  roll separately limited by `Q_TAILSIT_RLL_MX` ([guide](https://ardupilot.org/plane/docs/guide-tailsitter.html),
  read 2026-11-09). The card's "Q_ANGLE_MAX 3000 cdeg" is the older name. The limit can be raised, and T/W 2.6
  allows about 66° of lean. The real limit is therefore pilot/landing tip-over (39° on the narrow axis), not the
  parameter. **A 5 m/s wind limit for flights is correct and should stay.**
- Stance on four foam-board fin tips on grass: 0.64 × 0.38 m footprint with the CG at 0.235 m. Crushable printed
  feet will need replacing after hard landings; budget spares in PETG.

## 6. Cost: missing lines

| Missing or understated line | Evidence | Add (pre-tax) |
|---|---|---|
| RadioMaster Pocket needs **2 × 18650 cells, not included**, and will not run on USB alone | Retailer listings, e.g. [GetFPV Pocket Crush](https://www.getfpv.com/radios/radio-controllers/radiomaster-pocket-crush-radio-controller-w-elrs-2-4ghz.html), [RaceDayQuads](https://www.racedayquads.com/products/radiomaster-pocket-edgetx-rc-transmitter-choose-version); Lumenier 18650 2-pack $24.49 (GetFPV, seen via search 2026-11-09) | **$24.49** |
| Packs ship with XT60 but the harness uses an AS150U loop, so 4 packs plus a charge lead need re-terminating (or drop AS150U and stay on XT60, which is rated 60 A against a 24 A hover) | BOM note; the hardware kit holds one connector pair | **$15** `ESTIMATE` |
| Transport box at $25 is too low for a 1.25 × 0.55 × 0.45 m plywood/foam box | 1/4 in plywood sheet + foam + hardware, Home Depot `ESTIMATE` | **+$35** (total $60) |
| Hot-wire bow/jig, MH 45 template stock, extra epoxy | Not in BOM | **$15** `ESTIMATE` |
| FAA registration (Part 107 or recreational) | FAA DroneZone, $5, not taxed | **$5** |
| Possible: Part 107 knowledge test at $175 per pilot, if the university treats the capstone as non-recreational | `UNVERIFIED` decision for the team. Not in the total; take it from the reserve if needed | (0) |
| Charger throughput: one 150 W port charges one 96 Wh pack in about 70 min, so ~4.7 h for 4 packs | Arithmetic | 0 (charge overnight). A second charger is a nice-to-have at ~$57 |

The card's existing lines already cover spares (1 motor, 4 ESCs, 8 props), the LiPo bag, ammo can, charger,
tax at 10.25 % and $120 shipping. Those are accepted.

**Corrected total:** $1,528.51 + $89.49 + 10.25 % tax ($9.17) + $5 = **≈ $1,632**. That leaves ≈ **$368** of
reserve, enough for one bad crash ($309 incl. tax, card's formula). The concept **passes the $2,000 hard limit
comfortably**.

## 7. Packability

- The props-off envelope is 1.15 × 0.445 × 0.39 m against a 1.2 × 0.5 × 0.4 m box. If those are external
  dimensions, a box with 12 mm walls is 0.376 m tall inside, so **the aircraft does not fit**. There is also no
  room for the foam lining the card describes.
- Corrected box: **~1.25 × 0.55 × 0.45 m external, ~6 kg loaded** `ESTIMATE`. That still fits across a back seat
  or in a hatchback. In a compact-sedan trunk (opening often ~1.0–1.1 m) it is marginal.
- It is still the best transport story in the study: one piece, no structural joints, 5 minutes to field-ready.
  The exposed fins and motor tubes are the parts most likely to be damaged in transit, so the box needs cradles
  under the spar, not foam pressing on the fins.

## 8. Buildability, schedule and controls risk

- **Build hours:** 70 h to first hover is plausible for 3–4 students, apart from the fin-tube joint (§2), which
  will take a design-and-reprint iteration. Add 5–10 h.
- **"FC and parameters 12 h" is optimistic** for the first motor-only tailsitter. Transition and back-transition
  tuning (`Q_TAILSIT_*` angles and rates, gain scheduling) usually takes several field sessions. Budget **30–40 h**
  of flight-test sessions beyond first hover. That still fits the 12-week window.
- Laser-cutting paper-faced polystyrene foam board at Jacobs Hall is `UNVERIFIED` (some makerspaces restrict foam).
  The fallback is hand-cutting with a knife, which costs no extra time.
- **Roll in cruise (the main controls risk):** with `Q_TAILSIT_ENABLE 2`, ArduPilot uses the motors for control in
  fixed-wing modes, and roll in cruise comes only from prop reaction torque (hover yaw). At ~1 N per prop in
  cruise, the available torque swing is small compared with a 1.15 m wing's roll damping and gusts.
  - On the PX4 forum, a builder of a similar quad tailsitter reports that controlling FW roll with motors (MC yaw)
    was "unfeasible in most cases" ([PX4 discuss](https://discuss.px4.io/t/quad-tailsitter-with-no-control-surfaces/26153),
    forum, `UNVERIFIED`).
  - The ArduPilot H-Wing thread reports success, but also motor saturation that caused uncontrollable rolling at
    high throttle ([ArduPilot discuss](https://discuss.ardupilot.org/t/quad-x-motor-tailsitter-without-control-surfaces-h-wing/68833?page=8),
    forum).
  - HKU/HKUST academic vehicles do fly with differential thrust only ([arXiv 1903.06393](https://arxiv.org/pdf/1903.06393)),
    but with custom controllers.
  - **Control risk: 4/5.**
- **Recommended mitigation:** add two elevons in foam (2 servos, hinge tape, horns, about +$30 and +0.05 kg
  `ESTIMATE`). Then fly `Q_TAILSIT_ENABLE 1` with `Q_TAILSIT_MOTMX` set for all four motors. Elevons give roll
  and pitch authority in cruise, and they allow motor-only mode to be tried later as an experiment rather than as
  the baseline. That would drop control risk to about 3/5 and build difficulty would rise only slightly.
- **Single motor failure is fatal** in hover and cruise. This is accepted for a demonstrator; it is the same for
  every quad.

## 9. Corrected inputs used (scratch re-run of the card's `size()`)

| Input | Card | Review |
|---|---|---|
| Pack mass | 0.68 kg | 0.55 kg (`UNVERIFIED`, weigh on arrival) |
| Extra mass | none | +0.08 kg fin-tube junction, +0.10 kg build overrun (`ESTIMATE`) |
| DOWNLOAD | 1.02 | 1.06 |
| η_prop cruise (base / pess) | 0.55 / 0.35 | 0.47 / 0.35 |
| η_motor cruise | 0.80 | 0.72 |

Output: MTOW 2.43 kg, hover 355 W / 24.0 A, T/W 2.60, Vs 11.2 m/s, cruise 15.0 m/s at ~194 W, cruise after 2 min
hover 19.2 min (pess 12.0), hover-only 13.0 min, gust lean 16° / 36°.

Sensitivity: if the pack really weighs 680 g, the figures become MTOW 2.56 kg, 18.4 / 11.5 min, T/W 2.47.

## 10. Scores (reviewer)

| | Score | Reason |
|---|---|---|
| Build difficulty (1 easy – 5 hard) | **2** | Hot-wire core, foam board and printed mounts. The only new problem is the fin-tube joint |
| Control risk (1 low – 5 high) | **4** | Motor-only roll in cruise, plus a first-time tailsitter transition tune. Drops to 3 with elevons |
