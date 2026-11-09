# Concept screening (43 → 7)

Status: PROPOSED (screener, 2026-11-09). Tags: `ESTIMATE` = engineering guess, `UNVERIFIED` = not checked against
a primary source.

**Inputs read:** `STUDY-BRIEF.md`; `inputs/ADVISOR-XV24-LESSONS.md`; `inputs/MENTOR-GUIDANCE-2026-11-04.md`;
`requirements/REQUIREMENTS.md` (gates G1–G6, scoring §5); `concepts/MORPH.md` (33 concepts);
`concepts/AUDIT-LOG.md` rounds 1–3 (10 more concepts plus evidence on existing rows);
`research/components-cost/cost_model.py` (run 2026-11-09 with `python -I` on a scratch copy; totals below are its
output); `docs/research/configurations.md` (previous 29-variant trade study, 2026-10-21/25).
**Not available:** `research/existing-vtol/FINDINGS.md`, `research/flight-control/FINDINGS.md` and
`research/components-cost/FINDINGS.md` did not exist at screening time. Every controls-maturity call below therefore
rests on the audit log's forum/doc citations and the old trade study; re-screen the `UNVERIFIED` cells when they land.

**What the team lead actually fixed (2026-11-09):** $2,000 hard; VTOL; easy to transport; student-built. The
numbers in `REQUIREMENTS.md` (planning cap $1,850, 1.2 m box, 1.5 m piece, T/W ≥ 1.6, 12-week build) were chosen by
a previous agent. This screen uses them as **working thresholds** and says so at each use; no concept is dropped
*only* because it misses a derived number. Where it would be dropped under the raw $2,000 too, the row says so.

---

## 1. How the screen was run

Step 1, **deduplicate**: a concept that is the same lift + transition + wing form as another, differing only in a
material, a landing gear, a pack, a prop or a purchase route, is merged into its parent and becomes an *option* on
that parent (§2). It is still listed in §3 with the merge named, never silently dropped.

Step 2, **four quick numbers per surviving concept** (§3 columns):

| Column | Quick number | Threshold used (source) | Why it matters |
|---|---|---|---|
| **Cost** | `cost_model.py` total (tax 10.25 % + shipping) or the audit's kit-path calc | ≤ $1,850 (REQUIREMENTS G1 planning cap = $150 crash reserve) ; hard fail only if > $2,000 | The only constraint the team called hard. Floor for any scratch build: avionics $212.72 + ground/test $264.62 + hardware $124.01 = $601.35 pre-tax → **$783 with tax and $120 shipping before a single motor** (cost_model.py). |
| **Pack** | Largest piece and number of boxes `ESTIMATE` from span class | ≤ 1.5 m piece, ≤ 2 boxes 1.2 × 0.5 × 0.4 m (REQUIREMENTS C3, a proposal; "fits a normal car" is the real test) | Team lead: carried and assembled by one or two people. |
| **Build** | Loaded mechanisms (tilt servos, pivots, folds) + parts outside Jacobs Hall processes; scratch-build weeks `ESTIMATE` | ≤ 2 loaded mechanisms; ≤ 8 weeks first cut → first hover, leaving ≥ 4 of the 12 for test and one crash repair (STUDY-BRIEF schedule) | Mentor: buildability before simulation. Advisor's run never finished. |
| **Controls** | ArduPilot/PX4 frame support + count of documented hobby builds that transitioned | A maintained mode (REQUIREMENTS D7, which comes from campus logging policy, so it is real) **and** ≥ 1 documented transition at hobby scale | One airframe, one first-time pilot: the layout must have flown for someone else first. |

Step 3, **keep/drop**: drop on any hard fail (> $2,000, no VTOL, no supported autopilot mode, cannot fit a car) or on
two or more soft fails (over the $1,850 cap, > 2 loaded mechanisms, > 8 build weeks, no documented transition).
Step 4, **shortlist** 6–8 that span the lift/transition space: ≥ 1 buy-and-modify, ≥ 1 unconventional if it
survives on merit, no near-identical pairs.

---

## 2. Deduplication (43 concepts → 24 distinct families)

| Parent | Merged into it (becomes an option, decided at detail design) | Why they are the same configuration |
|---|---|---|
| **K01** small twin-boom quadplane 4+1 | K03 (H-frame lift booms), K04 (folding lift props), K05 (faired/aligned parked props), U04 (foam-board flat-pack build), U07 (split-chemistry packs), U08 (crushable feet + wheels), K21 (two more lift stations → hexa 6+1), B03 (buy a Mini Talon EPO airframe instead of cutting foam) | All are L1 lift + T1 pusher + X1 QuadPlane transition on a tailed wing. K03 changes where the booms attach; K04/K05 change the parked prop; U04 changes the wing material; U07 the pack; U08 the gear; K21 the motor count; B03 the airframe source. None changes hover, transition, autopilot mode or what the pilot does. |
| **K06** scratch tilt-tricopter | U05 (one coupled tilt servo), K07 (add a 4th fixed rear motor → front-tilt quad) | Same L2 + X2 `Q_TILT` transition; U05 is a mechanism choice (lose vectored yaw, gain one servo); K07 is K06 with one more rear lift station (+$48, cost_model.py) and the same fatal rear motor-out. |
| **K09** quad tailsitter | U03 (motor-only; K09's own code already has C4 = no moving surfaces, so U03 *is* K09), K11 (biplane "Box Kite" planform), U06 (folding outer panels) | Same four motors, same `Q_TAILSIT` copter-motor mode, same fin landing. K11 and U06 change planform/hinge, not the flight mechanics the autopilot sees. |
| **K10** twin-motor tailsitter | B04 (buy a foam wing instead of cutting one) | B04 is K10's purchase route; the audit's Z-84 TVBS evidence applies to both. |
| **B08** sub-$350 ArduPilot-ready tilt-tri PNP | B01 (HEEWING T1, same layout at $410, FC/ArduPilot support `UNVERIFIED`), B02 (HEEWING T2, 1.2 m, EU stock), B06 (the "mule" use of any of these) | All are "buy a tilt-tri PNP and integrate"; B06 is a programme plan (mule + scratch main), not a configuration, and attaches to whichever scratch concept wins. |
| **U01** wing-assisted quad | B07 (the bought carbon quad frame U01 is built on), U09 (same test with the wing on a free pivot instead of fixed) | B07 has no wing of its own; it is U01's base and K18's frame. U09 is the one-day variant of the U01 foam test. |
| **K18** pure quadcopter | — (stands alone as the trainer / hover test bed, not a VTOL-with-transition concept) | |
| Stand-alone families: K02, K08, K12, K13, K14, K15, K16, K17, K19, K20, K22, K23, K24, K25, B05, B09, U02 | | |

---

## 3. Screening table — every concept

Dispositions: **KEEP** = on the shortlist (§4); **MERGE→X** = carried as an option on X (not a separate row);
**DROP** = out, reason given. Cost = total with tax and shipping unless marked; "cm" = cost_model.py run 2026-11-09.

| ID | Concept | Cost | Pack `ESTIMATE` | Build (loaded mechs; weeks `ESTIMATE`) | Controls | Disposition | One-line reason |
|---|---|---|---|---|---|---|---|
| K01 | Small twin-boom quadplane 4+1, class S | **$1,636** cm (reserve $364) | halves ≤ 0.9 m + pod; 2 boxes | 0; 6–8 wk | `Q_FRAME_CLASS 1`, best-documented VTOL path, ≥ 5 builds | **KEEP** | Passes every gate with $364 reserve; the only layout the previous team already sized end-to-end, so the least unknowns. |
| K02 | C0-class quadplane (6S, 2.4 m) reference | **$2,003** cm | halves 1.2 m; 2 boxes | 0; 8–10 wk | As K01 | **DROP** | Over the raw $2,000 before any crash; K01 is the same layout at the size that fits the money. |
| K03 | Single-boom H-frame quadplane | ≈ K01 | one-piece wing ≤ 1.5 m at 1.5 m span; 2 boxes | 0; 6–8 wk | As K01 (Mini Talon / X8 conversions) | **MERGE→K01** | Boom attachment choice on K01; decide it in detail design (wiring never crosses the wing joint is a real plus). |
| K04 | Folding-prop quadplane | K01 + ≈ $94 pre-tax for 3 folding-prop pairs (configurations.md §2.5) | As K01 | 0; as K01 | As K01 | **MERGE→K01** | Prop choice; benefit is `ESTIMATE` (CdA halved) and must be measured (budget-lift.md M3) before ordering. |
| K05 | Faired, aligned stopped rotors | K01 + ≈ $22 goods | As K01 | 0 (+ magnetic detent); as K01 | As K01 | **MERGE→K01** | Printed nacelle option on K01; −85 W cruise is `ESTIMATE` on C0 and smaller at class S. |
| K06 | Scratch tilt-tricopter | **$1,549** cm (reserve $451) | 1.2–1.5 m wing in halves; 1–2 boxes | 2 tilt servos; 6–8 wk + tilt tuning | `Q_TILT_*` documented; Convergence / HEEWING lineage; Z-84 and MiniHawk builds flew | **KEEP** | Cheapest tilt layout, $113 under K01; the representative of the tilt family; must stay ≤ 2 kg class to keep T/W (old study: 1.59 at 6 kg). |
| K07 | Front-tilt quad (2 tilt + 2 fixed) | $1,597 cm | As K06 | 2; as K06 | Same mode as K06; Nimbus-class `UNVERIFIED` | **MERGE→K06** | K06 plus one rear station: same servos, same fatal rear motor-out, +$48; choose it only if K06's yaw/pitch authority tests short. |
| K08 | All-four tiltrotor | ≈ $1,650 `ESTIMATE` (K07 + 2 tilt servos) | As K06 | 4 tilt servos; 8+ wk | Generic tilt page only; one builder hit roll/yaw inversion and quit | **DROP** | Two soft fails (4 loaded mechanisms, no clean documented transition) for no gain K06 lacks. |
| K09 | Quad tailsitter, flat flying wing (motor-only) | **$1,492** cm (reserve $508) | 1.2–1.5 m wing, halves or one piece; 1 box possible | 0; 4–6 wk | `Q_TAILSIT_ENABLE 2` copter-motor; H-Wing and Cygnet builds fly; old trade study rank 1 (7.37) | **KEEP** | Cheapest and fastest scratch build, zero servos; its known weakness (30° tilt at 8 m/s gust, no motor-out) is a test-site rule (morning flights), not a gate fail. |
| K10 | Twin-motor tailsitter flying wing | $1,601 cm | As K09 | 0 (2 tilt servos if TVBS); 5–7 wk | Class 10 supported; weathervane crashes documented; TVBS belly form is the one that flies | **DROP** | Any motor-out fatal in both modes (score-0 anchor) and it costs $109 more than K09 for the same hover-in-wind problem; K09 covers the tailsitter cell. |
| K11 | Biplane quad tailsitter (Box Kite) | ≈ K09 | box ~0.6–0.8 m; **1 box, no joint** | 0; 3–5 wk | Foam-board Box Kite on ArduPilot page; Mini QBIT flew (Betaflight) | **MERGE→K09** | Planform option on K09 that may remove the field joint entirely; biplane L/D loss is `ESTIMATE`; build it as the §5 foam model. |
| K12 | Tilt-wing | > $2,000 at class M (old study $2,149); class S `ESTIMATE` ≈ $1,700 | wing + pivot ≤ 1.5 m | 1 pivot under full lift load + tail fan; 10+ wk | `Q_TILT_WING_FLAP` only; one documented build (CL-84) | **DROP** | Loaded wing pivot, thin autopilot support, one build; the old study found it infeasible. |
| K13 | Fixed tandem-wing quadplane | ≈ K01 at class S; $2,015 at class M | short span, packs well | 0; 7–9 wk | No dedicated mode; CG-sensitive pitch; Vahana-like attempt moved to Copter | **DROP** | No documented transition and CG-sensitive stability on a first-time team's only airframe; packing gain is small versus K01 halves. |
| K14 | Box-wing quadplane | ≈ K01 + tip plates; $2,111 at class M | packs well | 0 + tip-plate joints; 8–10 wk | No dedicated mode; none documented | **DROP** | Half-chord panels lose L/D at low Re (S21); no build evidence; nothing it fixes for this mission. |
| K15 | Octo / coax X8 quadplane | **$2,350** cm | As K01 | 0; 8+ wk | Class 3/4 supported | **DROP** | Over the raw $2,000; its one virtue (hover motor-out) is available cheaper as the K21 option on K01. |
| K16 | Bicopter tiltrotor | $2,156 at class M; class S `ESTIMATE` ≈ $1,600 | small | 2 tilt servos, pitch only by tilt; 8+ wk | Type 3 / class 10; a 2022 builder gave up on ArduPilot | **DROP** | Any motor-out fatal and no documented hobby transition; the highest control risk in the set. |
| K17 | Ducted-fan / fan-in-wing | > $2,000 `ESTIMATE` (EDF hover power → 6S, big packs) | fits | cover actuators + buried fans; 10+ wk | No supported mode for covered fans | **DROP** | High disk-loading hover eats the pack and the budget; no autopilot support; listed for completeness only. |
| K18 | Pure quadcopter, folding arms | ≈ $1,100–1,300 `ESTIMATE` (frame + 4 S stations + floors) | 1 box | 0; 1–2 wk | ArduCopter, fully mature | **DROP (as the aircraft)** | No transition, so it is not the VTOL demonstrator; keep it as the D15 trainer and the hover test bed for K01/K09 motors, inside the winner's budget if room. |
| K19 | Flying-wing (tailless) quadplane, X8 / DeltaQuad style | **$1,592** cm (reserve $408) | X8-class 2.1 m → halves ~1.0 m + short pod; 2 boxes | 0; 5–7 wk (2 elevon servos, no tail boom) | `Q_FRAME_CLASS 1`; most-documented hobby quadplane form (≥ 4 X8 build threads, PX4 page) | **KEEP** | Same transition as K01 with 2 fewer servos, no tail boom and $44 less; kept beside K01 because the wing/tail form changes packing, stall (≈ 14 m/s on X8) and crash behaviour, not as a duplicate. |
| K20 | Single-motor non-vectored tailsitter | $1,569 cm | small | 0; 4–6 wk | Type documented (`Q_TAILSIT_MOTMX 0`) but **no logged transition found**; no hover yaw without vectoring | **DROP** | Cheapest propulsion but zero hover yaw authority and no documented transition; a dev's advice was "add two wing motors", which is K09. |
| K21 | Hexa 6+1 quadplane | $1,733 cm (reserve $267) | As K01 | 0; 7–9 wk | Class 2 supported; motor-out needs power headroom; thrust-loss PR status `UNVERIFIED` | **MERGE→K01** | It is K01 with two more stations ($97 more); decide after K01's T/W and reserve are known. Only motor-out-tolerant layout under the cap, so it stays visible. |
| K22 | Tri 3+1 quadplane (tail yaw servo + pusher) | $1,609 cm | one-piece wing | 1 loaded yaw servo; 6–8 wk | Class 7 exists; **no documented 3-fixed-lift + pusher build**; frame/servo-mapping bug reports | **DROP** | Saves $27 against K01 and adds a loaded servo plus an unflown layout; two soft fails. |
| K23 | Folding-wing Transwing (AeroFold-class) | $1,611 cm | folded = transport state; **1 box, no joint** | 1 fold actuator + printed hinges under flight load; 10+ wk (hinge geometry unsolved by two students) | **No native mode** (binary-tilt fake or Lua); one hobby build, transition video `UNVERIFIED`; patent | **DROP** | Hard fail on a maintained autopilot mode (D7) plus the hinge geometry risk; outlandish-but-worthy: do the < $40 foam fold mock-up only as a side project if a shortlisted build runs ahead of schedule. |
| K24 | Reverse tricopter-tiltrotor | $1,580 cm | one-piece wing | 3 loaded servos; 7–9 wk | `Q_FRAME_TYPE 6` exists; **two forward transitions failed** (nose rears up); outcome past page 3 `UNVERIFIED` | **DROP** | Three loaded mechanisms and the weakest transition record of any tilt row; K06 covers the three-motor tilt cell with better evidence. |
| K25 | Y6 tilt flying wing (FireFly6-type) | $1,663 cm (reserve $337) | one-piece wing off arms | 1 tilt axle carrying 4 motors; 8–10 wk (6 stations to wire) | Class 5 / type 11 supported; documented yaw loss in transition fixed in 2025 by one builder; no kit | **DROP** | Motor-out tolerance is bought with 6 stations, $115 over K06 and a documented stall/flat-spin transition failure mode; too many unknowns for one airframe in 12 weeks. |
| B01 | Buy HEEWING T1 Ranger VTOL (730 mm) | ≈ $1,190 incl. floor (MORPH §2 calc, listing `UNVERIFIED`) | **1 box, wing off** | 0; 1–2 wk | Bundled F405 runs ArduPilot with logging? `UNVERIFIED`; many T1 builds | **MERGE→B08** | Same buy path as B08 at twice the kit price and with the FC question open; B08's fallback if FIMI/ZOHD stock fails. |
| B02 | Buy HEEWING T2 Cruza VTOL (1.2 m) | ≈ $1,550 `ESTIMATE` (kit ≈ $830 + packs, radio, floor, customs) | 1–2 boxes | 0; 1–2 wk | As B01 | **MERGE→B08** | The larger, less wind-limited member of the buy family; EU seller is a lead-time/customs risk for a mid-December order and US stock is `UNVERIFIED`. |
| B03 | Mini Talon EPO quadplane conversion | ≈ K01 − $100 airframe `ESTIMATE` (+ $150 kit, **out of stock**) | 1.3 m wing; 2 boxes | 0; 4–6 wk | 300+ post ArduPilot thread | **MERGE→K01** | The airframe-source option on K01/K03: take it if a kit is in US stock in December, otherwise cut foam. |
| B04 | Foam FPV flying wing → twin tailsitter | < $150 airframe + floors ≈ $1,100 `ESTIMATE` | 1 box | 0–2 (TVBS tilts); 2–4 wk | Z-84 TVBS build guide flew and transitioned (650 g) | **MERGE→K10 (dropped)** | Cheapest airframe in the set, but it inherits K10's fatal motor-out and documented wind problem ("always a problem for a tailsitter"); if the team wants a < $150 trainer this is it, not the demonstrator. |
| B05 | MakeFlyEasy Fighter/Striver 4+1 kit | £800 airframe ≈ $1,010 + 6S M-class propulsion ≈ $500 + floors ≈ $600 → **> $2,000** `ESTIMATE` | 2.4 m; halves 1.2 m | 0; 4–6 wk | Commercial 4+1, ArduPilot common | **DROP** | Over the raw $2,000 and UK/China lead time; the bought C0 layout costs more than building K01. |
| B06 | Two-aircraft plan: bought VTOL mule + scratch main | mule $300–550 + main ≥ $1,490 → $1,800–2,050 | — | — | — | **MERGE→B08 (programme option)** | Not a configuration; it is a way to spend the reserve on pilot and parameter practice. Fits only with a < $350 mule (B08) and K09/K06/K19-class main, and leaves < $200 for a crash. Decide after the main concept is priced. |
| B07 | Bought carbon quad frame + team-built bolt-on wing | frame $80–150 `ESTIMATE` | 1 box | 0; 2–3 wk | ArduCopter | **MERGE→U01** | B07 is the base of U01 (and K18); on its own it has no transition. |
| B08 | Sub-$350 ArduPilot-ready tilt-tri PNP (FIMI Manta / ZOHD Altus VTOL) | ≈ **$950–1,100** (AUDIT-LOG r1 calc, listings `UNVERIFIED`) → reserve ≈ $900 | **1 box, wing off**, no tools | 0 team-made; 1–2 wk to flying | Maker-published ArduPilot params (Manta: Matek F405-WTE); 1 forum "flies very well" (no logs) | **KEEP** | The buy-and-modify representative: lowest cost, lowest build hours, maker param files remove B01's FC question; sub-1 kg so wind-limited at RFS and stock/price must be opened, not searched. |
| B09 | Bought design files, printed airframe (Flightory Stallion VTOL / Eclipson E-VTOL) | ≈ **$1,250–1,400** `ESTIMATE` (files $48 + filament + class-S floors) | printed sections on carbon spars, sub-1 m pieces; 1–2 boxes | 2 tilt servos (Stallion); ≈ 100 h printer time `ESTIMATE` + 3–4 wk assembly | Stallion ships ArduPilot params, SpeedyBee F405 Wing; Eclipson transitions flown with crashes | **KEEP** | A different buy path (buy the design, Jacobs prints it free) with a flown aircraft and supplied params; kill risks are LW-PLA stiffness and heat, and the personal-use licence, both checkable in week 1. |
| U01 | Wing-assisted quad (tilt-body hybrid) on a bought frame | ≈ **$1,310–1,390** `ESTIMATE` (frame $80–150 + 4 S stations $145 + foam $30 + 3 packs $136 + spares $87 + hardware $124 + floors $477, × 1.1025 + $120 ship) | 1 box + wing | 0; 2–3 wk | ArduCopter only, no VTOL mode needed; **no documented build**; forum tri-with-wing "quite a problem with wind" | **KEEP (conditional on a 1-day test)** | The unconventional survivor: lowest control risk of anything with a wing, fully in Copter, cheapest scratch path; the open question (does the wing pay, and does it count as VTOL with transition for the team) is settled by a < $20, one-day foam test in §5 before any order. |
| U02 | Ring-wing (annular) quad tailsitter | ≈ K09 + printing | **1 box, no joint** | 0; 4–6 wk (printed ring > 300 mm) | Same mode as K09; ETH annular-wing paper (hover + forward flight); no ArduPilot build | **DROP** | Poor L/D and the largest side area in gusts of any tailsitter, for a transport gain K11 gives more cheaply; K09 covers the cell. |
| U03 | Motor-only quad tailsitter | = K09 | = K09 | 0 | H-Wing thread flies with `Q_ASSIST` | **MERGE→K09** | K09's own code is already motor-only (C4); this is the same concept named for its servo count. |
| U04 | Flat-pack foam-board quadplane | ≈ K01 − $40 foam `ESTIMATE` | As K01 | 0; 4–6 wk; 1 h panel repair | As K01 | **MERGE→K01** | Material/manufacturing option on K01 (mentor's axis); the §5 bend-test decides foam board vs XPS. |
| U05 | Single-servo coupled front-tilt tricopter | K06 − $28 | As K06 | 1 tilt servo (single point of failure); as K06 | Loses differential-tilt yaw `UNVERIFIED` | **MERGE→K06** | Mechanism option on K06; the bench rig in §5 decides it. |
| U06 | Retractable/folding-wing quad tailsitter | K09 + hinges/servos ≈ $60 `ESTIMATE` | folds for the box | 1–2 fold mechanisms under aero load; +2–3 wk | Paper only (arXiv 2511.04251); UPenn bistable wing never flew winged | **MERGE→K09 (phase-2 option)** | Fixes K09's wind weakness on paper, but adds a loaded mechanism and weeks; build K09 first, add the fold only if gust drift measured at RFS demands it. |
| U07 | Split-chemistry quadplane | K01 + Li-ion pack ≈ $70–140 | As K01 | 0 + second battery monitor | As K01 | **MERGE→K01** | Pays only above ≈ 15 min cruise (mission M-B); for the M-A demonstrator it is wiring and cost with no return. |
| U08 | Quadplane with crushable printed feet + wheels | K01 + ≈ $15 | As K01 | 0; as K01 | As K01 | **MERGE→K01** | Landing-gear option on K01 answering the mentor's wheels-vs-skids question; decide after the RFS grass is walked. |
| U09 | Free-pivot wing / tilt-body quad (Colibri type) | ≈ U01 + $30 pivot | As U01 | 1 free pivot + encoder under flight load | **No ArduPilot/PX4 mode**; hover-only research hardware; documented wing–body oscillation | **MERGE→U01 (test variant)** | Hard fail on autopilot support as a flight article; survives only as the free-spar variant of U01's one-day foam test. |

Count: 43 rows; 7 KEEP, 19 MERGE (carried as options on a kept or dropped parent), 17 DROP.

---

## 4. Shortlist (7) — one card each

The seven span the lift axis (L1 fixed lift × 2 wing forms, L2 tilt × 2 buy/build paths, L3 tailsitter, L6
wing-assisted) and the buy/build axis (scratch × 3, buy PNP, buy design files, buy frame + build wing). Every card's
cost is total with tax and shipping against $2,000; "reserve" is what is left for crashes.

### S1 — K01 Small twin-boom quadplane 4+1 (class S, 4S)
- **Cost:** $1,636 (cm), reserve $364. Options merged: K03 H-frame, K04 folding props (+$94), K05 fairings (+$22),
  U04 foam board (−$40), U08 feet/wheels (+$15), K21 hexa (+$97, reserve → $267), B03 EPO airframe if in stock.
- **Pack:** wing halves ≤ 0.9 m on a carbon joiner, booms stay on the halves; pod < 1.0 m; two boxes `ESTIMATE`.
- **Build:** 0 loaded mechanisms; hot-wire XPS + carbon tubes + printed nodes; 6–8 weeks `ESTIMATE`.
- **Controls:** ArduPilot QuadPlane class 1, the most documented VTOL path; speed-scheduled transition; motor-out
  in cruise survivable (glide on the pusher), in hover not (unless K21).
- **Why kept:** every gate passed with margin; the previous team's sizing, thermal and electrical work transfers.
- **What kills it:** parked-prop drag (36–40 % of cruise drag on C0, `ESTIMATE`) if the 5 min cruise threshold is
  missed on a 4S 6500 pack; measure stopped-prop CdA before the order.

### S2 — K19 Flying-wing (tailless) quadplane, X8 / DeltaQuad style
- **Cost:** $1,592 (cm), reserve $408 (2 elevon servos instead of 4, no tail boom).
- **Pack:** X8-class 2.1 m span → halves ≈ 1.0 m plus a short centre body; two boxes `ESTIMATE`.
- **Build:** 0 loaded mechanisms; 5–7 weeks `ESTIMATE`; a bought EPO X8 shell (M5) is a documented shortcut.
- **Controls:** same QuadPlane mode as S1; ≥ 4 ArduPilot X8 quadplane build threads plus a PX4 setup page; stall
  ≈ 14 m/s reported on an extended X8, so transition at ≥ 1.3 Vs needs ≈ 18 m/s `ESTIMATE`.
- **Why kept beside S1:** same propulsion and transition, but a different wing/tail form with real consequences
  (fewer servos, shorter pieces, higher stall speed, elevon-only pitch authority in a back-transition).
- **What kills it:** flying-wing pitch authority with four stopped props in the elevon wash `UNVERIFIED`; the
  bought-shell route depends on US stock in December.

### S3 — K06 Scratch tilt-tricopter (2 front tilt + 1 fixed rear)
- **Cost:** $1,549 (cm), reserve $451. Options merged: U05 single coupled servo (−$28), K07 fourth rear motor (+$48).
- **Pack:** 1.2–1.5 m wing in halves; one or two boxes `ESTIMATE`.
- **Build:** 2 loaded tilt servos (the known failure point; `Q_TILT_TYPE 1` binary retract servos remove the
  hold-under-load mode); 6–8 weeks plus tilt tuning `ESTIMATE`.
- **Controls:** `Q_TILT_*` documented; Convergence / HEEWING T1 lineage, Z-84 TVBS and MiniHawk builds flew.
- **Why kept:** the tilt family's cheapest and best-documented member; nothing parked in cruise, so no stopped-prop
  drag; cheapest scratch concept after K09.
- **What kills it:** T/W: the old study found 1.59 at the 6 kg class, so the aircraft must stay ≈ 1.5–2.5 kg; rear
  motor-out in hover is fatal; any tilt-servo strip is a crash.

### S4 — K09 Quad tailsitter, flat flying wing, motor-only
- **Cost:** $1,492 (cm), reserve $508, the largest of any scratch concept. Options merged: K11 biplane planform
  (may fit one box with no joint), U06 folding panels (phase 2 only).
- **Pack:** 1.2–1.5 m wing; one box in halves, or one box whole as K11 `ESTIMATE`.
- **Build:** 0 servos, 0 loaded mechanisms, fewest parts in the set; 4–6 weeks `ESTIMATE`; foam-board repair in hours.
- **Controls:** `Q_TAILSIT_ENABLE 2` copter-motor tailsitter; H-Wing and Cygnet motor-only builds fly; old study
  ranked it first (7.37/10) with T/W 2.41 and 22 min cruise at class M.
- **Why kept:** cheapest, fastest, simplest; the reserve alone covers a second airframe.
- **What kills it:** hover in wind (30° tilt at 8 m/s gust `ESTIMATE`, no weathervane assist, no motor-out) at a
  bay-shore site; fin landings in gusts. Mitigation is procedural (morning flights, 5 m/s limit on the flight card).

### S5 — B08 Buy an ArduPilot-ready tilt-tri PNP (FIMI Manta 700 mm or ZOHD Altus VTOL 980 mm; B01 HEEWING T1 fallback)
- **Cost:** ≈ $950–1,100 `ESTIMATE` (AUDIT-LOG r1; kit $190–330, listings `UNVERIFIED`), reserve ≈ $900; B01
  fallback ≈ $1,190. The reserve funds the B06 two-aircraft plan (this as mule, S4/S3/S2 as main) if the team wants it.
- **Pack:** one box, wing off, no tools.
- **Build:** nothing structural to make; 1–2 weeks to first flight; team work is ArduPilot setup, failsafes (D8–D10),
  logging, tuning, test campaign and a mission add-on.
- **Controls:** maker-published ArduPilot parameter files (Manta on Matek F405-WTE), which is what B01 lacks.
- **Why kept:** research supports it as the one buy-and-modify path with a known autopilot route and half the budget
  left; it is also the only concept that can fly in January.
- **What kills it:** sub-1 kg aircraft are wind-limited at RFS; FIMI US stock and 2026 price unopened; little
  airframe-design content unless the team adds a measured modification (wing extension, payload, gear).

### S6 — B09 Buy the design files, print the airframe (Flightory Stallion VTOL; Eclipson E-VTOL as the tailsitter form)
- **Cost:** ≈ $1,250–1,400 `ESTIMATE` (files $48, filament $60–100, class-S propulsion/avionics/ground floors).
- **Pack:** printed sections bolt to carbon spars, every piece < 1 m; one or two boxes.
- **Build:** 2 tilt servos (Stallion tilt-tri pack); ≈ 100 h of free Prusa time `ESTIMATE` plus 3–4 weeks assembly;
  design hours near zero, which is the point.
- **Controls:** Stallion ships ArduPilot params on a SpeedyBee F405 Wing; Eclipson transitions logged (with crashes).
- **Why kept:** a flown design with supplied parameters, made on Jacobs Hall's free machines; a distinct buy/build
  cell (B6) no other shortlist row occupies.
- **What kills it:** LW-PLA stiffness and sun deformation (a builder reported wing resonance), printer throughput
  over the holidays, and the personal-use licence (check with Flightory before a university project uses it).

### S7 — U01 Wing-assisted quad on a bought carbon frame (conditional)
- **Cost:** ≈ $1,310–1,390 `ESTIMATE` (frame $80–150, four class-S stations, foam wing, floors), reserve ≈ $600.
- **Pack:** one box (frame) plus a wing panel.
- **Build:** 0 loaded mechanisms; 2–3 weeks; the wing is the only designed part.
- **Controls:** ArduCopter only, no VTOL mode, no transition logic; nothing to tune beyond a standard quad.
- **Why kept:** the only unconventional concept that survives on merit: it removes the transition failure mode
  entirely, costs the least design time, and the team lead's own words ("a sort of VTOL drone") admit it. A
  tilt-tri builder measured 19 A hover → 13 A at 10 m/s with rotors at zero tilt, which is the effect U01 relies on
  (forum, `UNVERIFIED`).
- **Condition:** the §5 one-day foam test must show ≥ 20 % cruise-current reduction at 12 m/s with no hover
  instability; it is dropped if it fails, and U09 (free-pivot spar) is tried the same day if the fixed wing
  weathercocks. The team must also decide whether a no-transition aircraft meets its own demonstrator goal.

---

## 5. Tests that must run before the ranking (cheap, from MORPH §5)

| Test | Decides | Cost / time `ESTIMATE` |
|---|---|---|
| Foam-board wing at 25° taped to any team quad (S7 / U09 variant) | Keep or drop S7 | < $20, 1 day |
| 0.6 m foam-board quad-tailsitter model on 4 small motors, QHOVER with `Q_TAILSIT`, 5 m/s fan | S4 hover-in-wind; K11 planform | < $40, 2 days |
| One wing panel in foam board vs hot-wired XPS, bend-test and weigh | U04 option on S1/S2 | < $30, 1 day |
| Bench rig: one servo rotating a tube with two motors at hover thrust | U05 option on S3; binary vs continuous tilt | < $40, 1 day |
| Open FIMI / ZOHD / DefianceRC / Flightory product pages: US stock, price, FC and licence | S5 and S6 stay or go | 0, 1 h |
| Stopped-prop drag on a 11 in prop (budget-lift.md M3 method) | S1/S2 cruise threshold; K04/K05 options | < $20, 1 day |

---

## 6. What this screen could not settle (for the ranking agent)

- The three `research/*/FINDINGS.md` files were absent; every controls-maturity cell cites forum threads via the
  audit log. A documented transition log (not a video) for S3, S5 and S6 is still `UNVERIFIED`.
- The $1,850 planning cap, the 1.2 m box and the 12-week build are the previous agent's numbers; if the team
  measures its cars and sets its own reserve, K21 (hexa on S1) and B02 (1.2 m bought tilt-tri) move from MERGE to
  candidates, and nothing in the DROP column changes except K15 and B05, which fail the raw $2,000 regardless.
- Seven is the top of the 6–8 band; if the ranking agent needs six, S6 (B09) is the first to fold into S5 as "the
  other buy path", since both are tilt-tri layouts bought in different forms.
