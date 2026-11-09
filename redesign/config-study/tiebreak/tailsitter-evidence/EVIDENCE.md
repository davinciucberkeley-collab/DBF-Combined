# Tailsitter evidence: quad tailsitter (K09) vs small quadplane 4+1 (K01)

Tiebreak input for `README.md` §4. Written 2026-11-09. All web pages were seen on 2026-11-09.
Tags: **DOC** = official ArduPilot or PX4 documentation, or a peer-reviewed paper or thesis. **FORUM** = a builder's own
post on discuss.ardupilot.org (some attach a `.bin` log, noted where they do). **VIDEO** = video only, no log.
`ESTIMATE` = my judgement. `UNVERIFIED` = not checked against the primary source.

## 0. Bottom line (one paragraph)

I found **no** documented ArduPilot (or PX4) quad tailsitter **with elevons in the 1–1.5 m / 2–3 kg class** that has a
posted `.bin` log of a clean full transition and back-transition. What does exist: the configuration is officially
supported (**DOC**). The ArduPilot wiki lists one build guide in this family, Henry Wurzburg's foam-board "Box Kite"
quad tailsitter with elevons, but it is small (1804 motors, 3S 1000–1300 mAh). There are about a dozen FORUM reports of
quad tailsitters. Of those, **one** posts a log of an auto mission with a transition, cruise and vertical landing
(size and surfaces unknown), and **three** post or describe a **dive right after "transition done"**. The best-matched
teaching case (an instructor with students, four identical Box Kite style aircraft, 2025) shows failed transitions
and uncommanded yaw in a log, and no success in the thread. Small quadplanes are the opposite: the most mature
ArduPilot VTOL path, with an expert reaching transitions 8 days after first hover. First-timers still crash them,
nearly always through setup errors (reversed surfaces, zero throttle, overweight) rather than through the control law.
**`ESTIMATE` P(first full transition and back by week 8): K09 ≈ 0.40 (0.25–0.55), K01 ≈ 0.45 (0.30–0.60).** K09 reaches
hover about 3 weeks earlier, and that head start roughly cancels its harder transition. By week 12, K01 leads
(≈ 0.75 vs ≈ 0.60). The README's statement that a logged quad-tailsitter-with-elevons transition is `UNVERIFIED` still
stands after this search. It is now "searched for and not found in the target class", not "not looked for".

---

## 1. Quad tailsitter (copter-motor tailsitter): what is documented

### 1.1 Official support (DOC)

| Fact | Source | Tag |
|---|---|---|
| All tailsitters are QuadPlanes in ArduPilot. `Q_TAILSIT_ENABLE = 1` with control surfaces, `= 2` for copter-motor tailsitters with no surfaces (forces motor control in FW modes). | [ArduPilot Tailsitter Planes](https://ardupilot.org/plane/docs/guide-tailsitter.html) | DOC |
| Copter-motor tailsitters ("CopterMotor") use `Q_TAILSIT_MOTMX` ≠ 0 plus `Q_FRAME_CLASS/TYPE`. Types 16/17 (Plus/X) are "no yaw torque" variants. | same | DOC |
| Transition is set by `Q_TAILSIT_ANGLE`, `Q_TAILSIT_RAT_FW`, `Q_TAILSIT_RAT_VT`, `Q_TAILSIT_ANG_VT`, `Q_TAILSIT_THR_VT`. A "Transition FW done, timeout" message means the tune or parameters are wrong. | same | DOC |
| Gain scaling with airspeed (`Q_TAILSIT_GSCMSK`, `Q_TAILSIT_DSKLD`) is relative to hover throttle. **An airspeed sensor is recommended.** Without surfaces, "get the aircraft flying well in hover modes first". | same | DOC |
| Tailsitter tuning order: harmonic notch hover, then a hover with sharp pitch/yaw inputs, then set FF from the log (pitch/yaw are FF-dominated on surfaces), then D and P by oscillate-and-halve. Roll is tuned like a quad. **No time estimate, no wind guidance.** | [Tailsitter VTOL tuning](https://ardupilot.org/plane/docs/tailsitter-tuning-guide.html) | DOC |
| Copter-tailsitter yaw control (frame types 16/17) **only existed in master in 2021**, not in stable 4.0/4.1 (H. Wurzburg, dev). It is in stable now, but it is young code compared with quadplane code. | [H-Wing thread](https://discuss.ardupilot.org/t/quad-x-motor-tailsitter-without-control-surfaces-h-wing/68833) | FORUM (dev) |
| Wiki build list: two tailsitters (C1 Chaser TVBS twin; **foam-board "Box Kite" copter tailsitter**) and four quadplane/tiltrotor builds. | [Building a QuadPlane](https://ardupilot.org/plane/docs/quadplane-building.html) | DOC |
| PX4: duo and quad tailsitters share one airframe type. Quads are "easier to fly in hover mode, and more stable in windy conditions". All tailsitters are "much harder to tune for both hover and transition". Quad examples: Skypull SP-1, UAV Works VALAQ Patrol (video). No sizes or wind numbers. | [PX4 Tailsitter VTOL](https://docs.px4.io/main/en/frames_vtol/tailsitter.html) | DOC (examples VIDEO) |
| Research quad tailsitters fly full envelopes, but with **custom controllers** (wind-tunnel models, unified attitude control, disturbance observers), not stock ArduPilot. Examples: HKU, Lyu et al., *Int. J. Micro Air Vehicles* 2018/19, DOI 10.1177/1756829318813633 (motor-differential control, no surfaces); Virginia Tech, G. Carter 2021 MS thesis, MRAC transition flight tests. These are graduate-year efforts. | [arXiv 1903.06393](https://arxiv.org/abs/1903.06393), [VT handle 10919/103385](https://vtechworks.lib.vt.edu/handle/10919/103385) | DOC (abstracts only read; specs `UNVERIFIED`) |

### 1.2 Builds and outcomes (FORUM unless marked)

| Builder, date | Airframe | Size / mass | Surfaces | Transition outcome | Log? | Crash / cause | Tag |
|---|---|---|---|---|---|---|---|
| H. Wurzburg (ArduPilot dev), 2020 | **Box Kite** foam-board quad tailsitter, the wiki build | 3 × 20×30 in foam board; 1804 motors, 5 in props, 3S 1000–1300 mAh (≈ 0.3–0.5 kg `ESTIMATE`) | **2 elevons**, top and bottom linked | Flies (dev's own aircraft). Guide **does not show** a transition log. Author: fly on a **zero-wind day**. | No | Taped ground-contact points and leading edges for durability | DOC-listed / FORUM [link](https://discuss.ardupilot.org/t/box-kite-copter-tailsitter-build-instructions) |
| DaveSprague (reply), 2021 | Box Kite copy | same | elevons | Short hover hops "went well"; yaw sluggish. Hover only after the wind dropped. | No | — | FORUM (same thread) |
| **dpapworth (instructor, with students), Oct 2025** | **4 identical Box Kite style** quads, 1806, 5 in tri-blade, SpeedyBee F405 | small | 2 elevons | **Failed transition to FW** (log); recovered in QSTABILIZE. **All 4 yaw uncommanded in FBWA.** Two FCs had bad loop rates. No success in thread. | **Yes** | No crash; setup and tuning faults | FORUM [link](https://discuss.ardupilot.org/t/boxkite-vtol-learning/139972) |
| same instructor, Nov 2024 – Apr 2025 | twin-motor tailsitter, foam board | ≈ 315 g | 2 elevons | First hover Nov; first transition flight **Dec 3** with FW oscillation; **still unsteady 5 months later** (descent after back-transition tumbles: low throttle, no airflow over elevons) | Yes | none reported | FORUM [link](https://discuss.ardupilot.org/t/learning-vtol-tailsitter/126754) |
| Farkhod Khikmatov, Jan 2024 | quad tailsitter, 4S | not given | not stated (likely none) | **AUTO mission: transition, waypoint cruise, vertical landing** (manual QRTL for the last part). "Two of three builds flying". | **Yes** (`2024-01-03 15-29-53.bin`) | No crash; slow final descent from 70 m (Q_LAND_SPEED) | FORUM [link](https://discuss.ardupilot.org/t/copter-tailsitters/45514?page=50) |
| airton_dep, Dec 2023 | Swan-style H-wing quad, **≈ 1.7 × Swan K1 span** | not given | **none** | Transition OK, **then dive ≈ 10 m, twice**; recovered to QLOITER on the first attempt | **Yes** | Dev (P. Hall): FW pitch trim wrong and pitch-up demand rising to motor saturation; check CG/static margin | FORUM (same page) |
| Jaliy4, Dec 2025 | Swan-style quad | not given | none | Transition, **then immediate nose dive**; recovered to QLOITER | No (params only) | Not found | FORUM (same page) |
| S. Singer, 2025 (**twin**, for reference) | plank flying wing, reflexed NACA 25115, SLS fuselage | not given | elevons ¼–⅓ of wing | Hover and transition smooth, then a **violent pitch discontinuity at FW handoff, unrecoverable, every flight** | Drive link | Dev: tune FW gains; lower `Q_TAILSIT_ANGLE` | FORUM [link](https://discuss.ardupilot.org/t/crash-with-tailsitter-after-transition-handoff/145514) |
| irfan (mono), Aug 2019 | **quad+ tailsitter, 1.70 m span, 0.55 m² wing, 2.75 kg dry** (the closest in class) | 1.7 m / > 3 kg wet | not stated | "Ready to fly"; **no outcome posted** | No | — | FORUM [link](https://discuss.ardupilot.org/t/copter-tailsitters/45514) |
| lorbass, Dec 2019 – Apr 2020 | quad+ tailsitter | not given | elevons (later unused for yaw) | Dec 2019: **rolled 180° ≈ 1 s after takeoff, crash**. Mar 2020: forward transition "looks good", "but the Earth was too close"; uncontrolled CW yaw at motor minimum. | Yes (Drive) | Insufficient yaw torque, turbulence (dev); strong gusty wind on the day | FORUM [p.10](https://discuss.ardupilot.org/t/copter-tailsitters/45514?page=10), [p.30](https://discuss.ardupilot.org/t/copter-tailsitters/45514?page=30) |
| Tim Clemens, Feb 2020 | tandem-wing quad tailsitter, foam board + CF | **48 in (1.22 m)** | 8 surfaces | Describes 3 s out, 2 s back | No | — | VIDEO [p.25](https://discuss.ardupilot.org/t/copter-tailsitters/45514?page=25) |
| Mallikarjun_SE, Feb 2020 | tailsitter | not given | not stated | QHOVER transition "pretty good" at 14–15 m/s, "not great" elsewhere | Promised, not posted | — | FORUM (same page) |
| adam (chc), Jan 2021 | quad-X, no surfaces | not given | none | Transition to FBWA normal; **in MANUAL, roll and pitch uncontrollable** | No | Motor-only in manual has no authority | FORUM [p.39](https://discuss.ardupilot.org/t/copter-tailsitters/45514?page=39) |
| steph280, Feb 2024 | NYT quad-X (dev advised against) | — | none | **First flight "ended in disaster"** | No | Motor order | FORUM [H-Wing p.6](https://discuss.ardupilot.org/t/quad-x-motor-tailsitter-without-control-surfaces-h-wing/68833?page=6) |
| RickyG, 2022–23 | printed Swan K1 style H-wing | — | none | Built by Aug 2023; **no flight reported in ≈ 1 year of thread** | `.bin` posted but "don't show flight" | — | FORUM [H-Wing p.4](https://discuss.ardupilot.org/t/quad-x-motor-tailsitter-without-control-surfaces-h-wing/68833?page=4) |
| Cygnet (richardg3 design) / Reb1, 2026 | printed motor-only quad tailsitter | **1249 mm**, 4S, 2212, 9×4 props; PETG copy's printed parts alone 1.62 kg | none | Designer flies it on ArduPilot (no log, no AUW recalled). PETG builder: not flown; dev says PETG would be "maxed out" | No | — | FORUM [link](https://discuss.ardupilot.org/t/3d-printed-cygnet-vtol-build-motor-only-no-control-surfaces-petg-version/142979) |
| losawing (letpi), 2018–21 | many biwing/tandem tailsitters | ≈ 1 m | various | Flies well (expert) | Some | **≈ 10 crashes into water over ≈ 2 years** | FORUM [p.10](https://discuss.ardupilot.org/t/copter-tailsitters/45514?page=10) |

### 1.3 What this says for K09 (1.15 m, 2.43 kg, 4 fixed motors on fins, 2 elevons)

| Question | Evidence | Read for K09 |
|---|---|---|
| Logged success in class? | None found with elevons at 1–1.5 m / 2–3 kg. Nearest: Farkhod (log, size unknown), Cygnet 1.25 m (no log), Tim Clemens 1.22 m (video). | **Not found.** The team would be close to first in its class on stock ArduPilot. |
| Wind limit | No documented number. Box Kite author: zero wind. PX4: quads are better in wind than duos. lorbass's gusty-day flights produced yaw upsets. dpapworth: breeze made a light tailsitter "twitchy". | The README's 5 m/s card limit (lean-angle method) is the only number, and it is a calculation, not a field result. `ESTIMATE`: treat ≤ 4–5 m/s as the field limit for first transitions. |
| Landing / tip-over | No tip-over statistics. Box Kite tapes its contact points (so it expects them to hit). Back-transition descent is the reported weak point: at low throttle the surfaces lose prop wash and the aircraft tumbles (dpapworth). Forum: crosswind landing makes yaw hard. | Consistent with README §4.1: fin-tip landing is the recurring damage mode. Keep descent throttle up (`Q_TAILSIT_THR_VT`, slow `Q_LAND_SPEED`), and land into the wind. |
| Typical crash causes, ranked by count in §1.2 | (1) **Dive or pitch upset right after FW handoff**: FW pitch trim/CG/FW gains (3 quads + 1 twin). (2) **Setup errors**: motor order, reversed axes, FC loop rate (3). (3) **Yaw authority** with motor torque (2). (4) Overweight or underpowered (2). | Cause (1) is the one K09 must design out. **Mitigation: hand-launch K09 as a plain flying wing in FBWA/AUTOTUNE before any transition**, so FW trim, CG and gains are known when the first handoff happens (Wurzburg's advice in dpapworth's thread: tune VTOL first, then autotune FW, as two independent tunes). |
| Tuning time to first transition | Expert devs: days–weeks (not logged as a number). Instructor with students: first transition attempt ≈ 1 month after first hover, still not clean ≈ 5 months later (twin). The 4-aircraft quad class: failed first transition, no success posted. Hobbyist H-wing: a year without a reported flight. | `ESTIMATE` 3–6 weeks from first stable hover to first clean round trip for a first-time team with an expert reviewing logs on the forum; more without one. |
| Elevons vs motor-only | Motor-only: "MANUAL uncontrollable" (adam), poor roll at FW loiter (Swan K1 motors at limits, FORUM). Elevons: needed for surface authority but go limp at low throttle on descent. Elevon size ¼–⅓ of wing is recommended (FORUM). | Supports the README's elevon decision. K09's elevons (0.22 × 0.05 m each ≈ 6 % of wing) are **far below** the ¼–⅓ that tailsitter builders use. They are for cruise roll/pitch only, which is fine because hover is on the 4 motors, but they will not help at all in the descent tumble case. |

---

## 2. Small ArduPilot quadplane 4+1 (comparison, brief)

| Builder, date | Airframe | Outcome | Time | Crash / cause | Tag |
|---|---|---|---|---|---|
| Greg Covey, Jul 2016 | HobbyKing Bix3 trainer, ≈ 1.55 m span (`UNVERIFIED`, not in thread), ≈ 1.6 kg target (58 oz, thread), 4 × 2212 + pusher | First hover Jul 23, **maiden with transitions Jul 31**, 4 min, 60 % pack left | **≈ 8 days hover → transition** (expert) | none | FORUM [link](https://discuss.ardupilot.org/t/quadplane-conversion-of-hobby-king-bix3-trainer/10368) |
| aamadeuss, Aug 2017 | X-UAV Mini Talon 1.3 m, 4 × MT3506 + pusher, 4S 6600 | "Flying awesome"; added CF for yaw | weeks | none | FORUM/VIDEO [link](https://discuss.ardupilot.org/t/mini-talon-quadplane-conversion/19763) |
| PerthUAV (Mozzie, OBC team) | larger quadplane | Flies in up to 80 km/h wind; quad motors shut off ≥ ≈ 14 m/s. Warns that **small quadplanes descend poorly above ≈ 5 m/s** and nose-dive in high-wind QHOVER with airspeed. | years | — | FORUM (same threads); [Mozzie docs](http://mozzie.readthedocs.io/) DOC-listed |
| Robel, 2020 | Baby Shark quadplane; **racing-quad pilot, little FW experience** | Tumbles at the start of AUTO transition; **8 months, 3 crashes** | — | Reversed elevator compensation suspected; zero throttle in AUTO; airspeed params with no sensor | FORUM [link](https://discuss.ardupilot.org/t/quadplane-flips-during-transition/65883) |
| Paul (flyingw), Jun 2020 | 30 in Nutball quadplane, first quadplane | Hover 2 days after build (after fixing a **backwards-mounted FC**); **FBWA transitions tumble, MANUAL crash** | no transition | Overweight, wing area lost to fan holes | FORUM [link](https://discuss.ardupilot.org/t/vtol-nutball-quadplane/57406) |
| Porter QuadPlane / OctaQuadPlane | large | "Building, flying and crashing" write-ups | — | (not read in detail, `UNVERIFIED`) | DOC-listed [link](https://diydrones.com/profiles/blogs/building-flying-and-crashing-a-large-quadplane) |

**Pattern.** Quadplane failures are **setup errors** that a props-off ground check catches (surface directions, FC
orientation, throttle in AUTO, phantom airspeed sensor), or a **weight overrun**. The quadplane also has two safety nets
the tailsitter lacks. In a bad transition the pilot can drop back to QSTABILIZE, and the aircraft is still level, so the
lift motors catch it (Robel, Paul and the PerthUAV notes all recover this way at least once). In cruise, a lift-motor
failure is a glide. Its weak points are wind on small frames (> 5 m/s descent problems) and the K01-specific budget and
build hours (README §4.2).

---

## 3. P(first full transition, out and back, by week 8 of 12), first-time student team

Model: P = P(stable hover by week H) × P(clean round-trip transition in the weeks left | hover). Inputs: README §3.3 team
hours at the build judge's 35 h/week, the evidence above, one crash and repair assumed in the window. All `ESTIMATE`.

| Factor | K09 quad tailsitter + elevons | K01 quadplane 4+1 | Basis |
|---|---|---|---|
| Team-hours to first hover | 70–85 h → **week 3–4** (incl. parts arrival, ground tests) | 150–180 h → **week 5–6** | README §3.3 |
| P(stable hover by then) | 0.85 (quad-like hover on 4 fixed motors, T/W 2.6, simplest build) | 0.85 (conventional quad hover) | DOC; Covey/Paul hover within days |
| Weeks left for transition work by week 8 | ≈ 4–5 | ≈ 2–3 | — |
| Weekly hazard of achieving the round trip once hover-tuned | ≈ 0.15–0.2/wk. Needs the FW hand-launch tune first (≈ 1 wk), then handoff-dive and back-transition-descent issues; evidence shows weeks to months for amateurs | ≈ 0.35–0.4/wk. Expert 8 days; failures are setup errors caught on the ground | §1.2, §2 |
| Crash during campaign, repair time | likely (0.5); 2–4 days (re-cut XPS, ≈ $20 core) | likely (0.4); 1–2 weeks (booms, joints, ≈ $266 per README) | README §4.1–4.2 |
| Flight days lost to wind (RFS afternoons) | larger (5 m/s card) | smaller (≈ 5 m/s descent issue, but a tail, weathervane) | README §4.3; `wind/` tiebreak |
| P(transition by week 8 \| hover) | 1 − (0.82)^4.5 ≈ 0.59 → **≈ 0.47** after the crash/wind discount | 1 − (0.62)^2.5 ≈ 0.70 → **≈ 0.53** after the crash discount | arithmetic |
| **P(first full transition by week 8)** | 0.85 × 0.47 ≈ **0.40** (range 0.25–0.55) | 0.85 × 0.53 ≈ **0.45** (range 0.30–0.60) | |
| P by week 12 (for context) | ≈ 0.60 | ≈ 0.75 | same model, 4 more weeks |

**How to read it.** At week 8 the two are within the noise, because K09's earlier hover pays for its harder
transition. The tailsitter's distribution has a longer tail: when it goes wrong, it goes wrong as a dive at handoff,
or a descent tumble that wrecks the airframe, and the evidence shows hobbyists stuck for months. The quadplane's failures
are cheaper to find. K09 moves to **≈ 0.50** if three things are true: (a) the airframe is flown as a hand-launched
flying wing and autotuned before the first transition, (b) an airspeed sensor is fitted for gain scheduling, and (c)
someone on the team has ≥ 10 h SITL with the copter-tailsitter model. K09 drops to **≈ 0.25** if it waits for hover to
work before the FW tune, or if spring winds at RFS are routinely > 5 m/s.

## 4. Consequences for the decision (no recommendation change made here)

1. The README's "logged transition `UNVERIFIED`" caveat is confirmed: **no in-class logged precedent exists** that I
   could find. The README's K09 pick rests on budget, build and schedule, not on flight evidence. That still holds, but
   the flight-risk judge's 3.5–5 is supported, not pessimistic.
2. Add **"FW hand-launch tune before transition"** to the K09 test plan. It removes the most-reported tailsitter crash cause.
3. The foam-board twin in the README §4.3 is essentially the wiki's Box Kite. Build it **from Wurzburg's published guide**
   rather than from scratch, and use it to rehearse the full transition (not just hover in wind) before December.
4. Weak points of this file: the forum sample favours problems (successes are posted less often). Sizes and masses are
   missing for most entries. I read only the abstracts of the two academic sources.

## Sources (all seen 2026-11-09)
- DOC: https://ardupilot.org/plane/docs/guide-tailsitter.html · https://ardupilot.org/plane/docs/tailsitter-tuning-guide.html ·
  https://ardupilot.org/plane/docs/quadplane-building.html · https://ardupilot.org/plane/docs/quadplane-flying.html ·
  https://docs.px4.io/main/en/frames_vtol/tailsitter.html · https://ardupilot.org/copter/docs/common-Swan-K1.html ·
  https://arxiv.org/abs/1903.06393 · https://vtechworks.lib.vt.edu/handle/10919/103385
- FORUM: https://discuss.ardupilot.org/t/box-kite-copter-tailsitter-build-instructions ·
  https://discuss.ardupilot.org/t/boxkite-vtol-learning/139972 · https://discuss.ardupilot.org/t/learning-vtol-tailsitter/126754 ·
  https://discuss.ardupilot.org/t/copter-tailsitters/45514 (pages 1, 10, 25, 30, 39, 50) ·
  https://discuss.ardupilot.org/t/quad-x-motor-tailsitter-without-control-surfaces-h-wing/68833 (pages 1, 4, 6) ·
  https://discuss.ardupilot.org/t/crash-with-tailsitter-after-transition-handoff/145514 ·
  https://discuss.ardupilot.org/t/3d-printed-cygnet-vtol-build-motor-only-no-control-surfaces-petg-version/142979 ·
  https://discuss.ardupilot.org/t/quadplane-conversion-of-hobby-king-bix3-trainer/10368 ·
  https://discuss.ardupilot.org/t/mini-talon-quadplane-conversion/19763 ·
  https://discuss.ardupilot.org/t/quadplane-flips-during-transition/65883 · https://discuss.ardupilot.org/t/vtol-nutball-quadplane/57406
