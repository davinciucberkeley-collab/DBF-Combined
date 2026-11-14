# Morphological chart and concept set (v1)

Status: PROPOSED (concept generator, 2026-11-09). Every concept below is a `PROPOSED` combination; none is
`MODELLED`, `CHECKED` or `VERIFIED`. Tags: `ESTIMATE` = engineering guess, `UNVERIFIED` = not checked against a
primary source.

**Inputs read:** `STUDY-BRIEF.md`; `requirements/REQUIREMENTS.md` (gates G1–G6, mission default M-A, scoring §5);
`inputs/ADVISOR-XV24-LESSONS.md`; `inputs/MENTOR-GUIDANCE-2026-11-04.md`; `research/components-cost/cost_model.py`
(run 2026-11-09, `python -I`); `analysis/tradestudy.json` + `docs/research/configurations.md` (29 variants);
`concepts/concepts.json` (a0–c3) and `concepts/variants/a1–a3/design.md`; `explorations/tiltwing/README.md`.
**Not yet available:** `research/existing-vtol/FINDINGS.md`, `research/flight-control/FINDINGS.md` and
`research/components-cost/FINDINGS.md` did not exist when this file was written (folders empty except
`cost_model.py`). Re-run the completeness audit (§4) when they land; any build or kit they cite that is not in §3
becomes a new row.

How to read: §1 the chart (11 dimensions × options, each option coded). §2 the price anchors used. §3 the concepts,
each written as a code string through the chart, with a one-line screen against the gates. §4 completeness audit
and empty regions. §5 what to test before dismissing the unconventional ones.

---

## 1. Morphological chart

Option codes are used in §3. "Seen in" points to where the option already has evidence.

| # | Dimension | Options |
|---|---|---|
| **D1** | VTOL lift method | **L1** dedicated fixed vertical lift rotors (stopped in cruise) · **L2** tilting rotors (some or all) · **L3** whole body tilts (tailsitter) · **L4** wing + rotors tilt together (tilt-wing) · **L5** multirotor only, never leaves rotor-borne flight · **L6** body pitches nose-down, wing adds lift (tilt-body / wing-assisted multirotor) · **L7** ducted fans / fan-in-wing |
| **D2** | Cruise thrust | **T1** dedicated pusher (1 motor) · **T2** dedicated tractor in nose · **T3** the lift/hover rotors after tilting or body rotation (shared) · **T4** twin wingtip tractors (concept a1) · **T5** none: rotors provide all thrust while tilted (L6) |
| **D3** | Transition method | **X1** speed-scheduled handover, ArduPilot QuadPlane (`Q_ASSIST_SPEED`, `Q_TRANSITION_MS`) · **X2** tilt servo schedule (`Q_TILT_*`) · **X3** body pitch-over (`Q_TAILSIT_*`) · **X4** wing-pivot schedule (`Q_TILT_WING_FLAP`) · **X5** no mode switch: Copter flight with forward pitch · **X6** none (pure hover) |
| **D4** | Wing / body form | **W1** conventional straight wing + pod fuselage · **W2** flying wing / delta · **W3** biplane (two stacked wings) · **W4** tandem wing · **W5** box / joined wing · **W6** ring (annular) wing · **W7** no wing |
| **D5** | Tail / control | **C1** twin-boom inverted-V or H tail + ailerons · **C2** V-tail on single boom · **C3** tailless with elevons · **C4** fins only, control by differential thrust (no moving surfaces) · **C5** canard / tandem-wing pitch · **C6** multirotor attitude control only |
| **D6** | Rotor count / arrangement | **R1** 4 lift + 1 cruise (4+1) · **R2** 8 lift (+1) or coax X8 · **R3** 3 rotors, 2 front tilt + 1 rear fixed (tilt-tri) · **R4** 4 rotors, 2 front tilt + 2 rear fixed/folding · **R5** 4 rotors, all on wing/fin tips, body-fixed (quad tailsitter) · **R6** 2 rotors (twin) · **R7** 4 rotors in X on a frame (quad) · **R8** 4 rotors at wing tips of a tandem/box wing |
| **D7** | Landing method | **G1** skids / boom ends · **G2** tail fins or wingtips as legs (tailsitter) · **G3** wheels (also allows a rolling emergency landing) · **G4** foam pads on fuselage belly · **G5** printed crushable feet (sacrificial) |
| **D8** | Transport / break-down | **P1** two wing halves on a carbon spar joiner, booms stay on halves · **P2** one-piece wing removed from fuselage, booms removable · **P3** whole aircraft fits the 1.2 m box, no breakdown · **P4** folding arms / folding wing (hinge + lock) · **P5** wing panels slide on spar tubes (no glue joint) · **P6** buy-kit's own breakdown (kit case) |
| **D9** | Primary structure material / process | **M1** hot-wire XPS/EPS core + packing-tape or laminating-film skin + carbon spar · **M2** foam board (paper-faced, laser/knife cut, FT style) + carbon spar · **M3** FDM-printed (LW-PLA / PETG) shells + carbon spar · **M4** balsa/plywood laser-cut ribs + film covering · **M5** bought moulded EPO/EPP airframe (kit) · **M6** aluminium or carbon tube space frame + printed nodes (multirotor style) · **M7** carbon/glass wet lay-up over foam (spray booth only) |
| **D10** | Energy source | **E1** single 4S LiPo · **E2** single 6S LiPo · **E3** 2 LiPo packs in parallel · **E4** bought Li-ion 18650/21700 pack (cruise-heavy missions) · **E5** split bus: LiPo for lift, Li-ion for cruise |
| **D11** | Buy vs build airframe | **B1** scratch-built (all airframe made in Jacobs) · **B2** buy a foam fixed-wing kit, add VTOL hardware (convert) · **B3** buy a complete VTOL PNP / kit, add own FC/radio · **B4** buy a carbon multirotor frame, build the wing · **B5** two aircraft: a cheap bought VTOL as trainer/mule + a scratch-built main aircraft |

Options counted: 7 + 5 + 6 + 7 + 6 + 8 + 5 + 6 + 7 + 5 + 5 = **67**. Full combinations ≈ 7×5×6×7×6×8×5×6×7×5×5
≈ 1.06 × 10⁹; most are incoherent (e.g. L3 with T1), so §3 picks coherent paths.

### Compatibility rules used to prune (why some combinations are not concepts)
- L3 (tailsitter) ⇒ T3, X3, G2, and C3/C4; a separate pusher (T1) or a tail boom adds mass with no use.
- L1 ⇒ X1 and a dedicated cruise motor (T1/T2/T4); L1 + T3 is impossible.
- L2 ⇒ X2; any rotor that tilts carries a loaded servo (buildability penalty, `REQUIREMENTS.md` §5).
- L5 ⇒ W7, X6, no transition: fails mission M-A (`REQUIREMENTS.md` §3) but kept as a trainer/control.
- E4/E5 only help when cruise time > ~15 min (M-B); for M-A a LiPo is cheaper and lighter in hover `ESTIMATE`.
- B3 (bought VTOL) fixes D1–D9 to whatever the kit is; the team's design content shifts to integration, tuning,
  mission and testing.

---

## 2. Price anchors used in the screen

From `research/components-cost/cost_model.py` (prices and sources in that file; run 2026-11-09). Totals include
10.25 % tax and shipping, against the $2,000 cap; G1 needs total ≤ $1,850.

| cost_model.py layout | Total | Reserve vs $2,000 |
|---|---|---|
| S quad tailsitter (4 × 4S stations) | $1,491.55 | $508.45 |
| S tilt-tri (2 tilt + 1) | $1,548.77 | $451.23 |
| S tilt-quad (front tilt) | $1,597.26 | $402.74 |
| S twin tailsitter (6S stations) | $1,600.66 | $399.34 |
| S quadplane 4+1 | $1,635.93 | $364.07 |
| M quadplane 4+1 (C0-class, 6S) | $2,003.10 | −$3.10 (fails G1) |
| M octo 8+1 | $2,350.08 | −$350.08 (fails G1) |

The fixed floor (avionics $212.72 + ground/test $264.62 + hardware $124.01 = **$601.35** pre-tax) is paid by every
concept that is not a bought package. One bad class-S crash ≈ $308.93 with tax (cost_model.py).

Bought-VTOL anchors (web search 2026-11-09; listing prices seen in search results, product pages not opened, so
`UNVERIFIED` until the components-cost agent confirms):

| Item | Price seen | Vendor (URL) |
|---|---|---|
| HEEWING T1 Ranger VTOL PNP (730 mm, tilt-tri) | $289.00 | DefianceRC, https://www.defiancerc.com/products/heewing-t-1-ranger-vtol-pnp-kit |
| HEEWING T1 Ranger VTOL PNP + F405 VTOL FC | $409.99 | DefianceRC, https://www.defiancerc.com/collections/fixed-wing/products/heewing-t-1-ranger-vtol-pnp-flight-controller-kit |
| T1 Ranger PNP→VTOL conversion kit (3 × 1806 motors, 2 tilt servos) | $159.99 | DefianceRC, https://www.defiancerc.com/products/heewing-t-1-ranger-pnp-vtol-conversion-kit |
| HEEWING T2 Cruza VTOL PNP (1.2 m) | €723.79 (≈ $830 at 1.15 $/€, `ESTIMATE`) | Rotorama (EU), https://www.rotorama.com/product/heewing-t2-cruza-vtol-pnp |
| X-UAV Mini Talon EPO kit (1.3 m), base for quadplane conversions | $149.97 listed, out of stock | https://shop.simon.com/products/x-uav-mini-talon-epo-1300mm-wingspan-v-tail-fpv-plane-aircraft-kit.oembed; build thread https://discuss.ardupilot.org/t/mini-talon-quadplane-conversion/19763 |
| MFE Fighter 2430 mm 4+1 VTOL kit (no electronics) | £799.90 | 3DXR, https://www.3dxr.co.uk/products/make-fly-easy-mfe-fighter-2430mm-wingspan-vtol |

Kit-path cost, worked (T1 Ranger VTOL + FC): kit $409.99 + 3 × 4S 2200 packs at $35 `ESTIMATE` ($105) + TX/RX
$84.98 (cost_model.py) + ground/test floor $264.62 + conversion kit as spare motor/servo set $159.99 = **$1,024.58**
goods; × 1.1025 = $1,129.60; + $60 shipping `ESTIMATE` = **≈ $1,190 total, ≈ $810 reserve**. Whether the bundled
F405 FC runs ArduPilot with logging (D7) is `UNVERIFIED`; if not, add the $67.26 CoreWing F405 from cost_model.py.

---

## 3. Concepts

Code string order: L·T·X·W·C·R·G·P·M·E·B. "Screen" = quick read against G1–G6; it is not a score. Cost class
refers to §2. Numbering is K = conventional or literature, B = buy-and-modify, U = unconventional.

### 3.1 Conventional and research-derived

| ID | Name | Code | Description | Source | Screen |
|---|---|---|---|---|---|
| K01 | Small twin-boom quadplane (4+1) | L1 T1 X1 W1 C1 R1 G1 P1 M1 E1 B1 | C0's layout shrunk to class S: ~1.5–1.8 m span `ESTIMATE`, 4S, two carbon booms carry 4 lift motors and an inverted-V tail, pusher on the pod; wing halves plug on a carbon joiner. | `docs/research/configurations.md` §2.1; cost_model.py "S quadplane 4+1" | $1,636; best-documented ArduPilot path (Q_FRAME_CLASS 1); parked-prop drag ~36–40 % of cruise drag on C0 |
| K02 | C0-class quadplane (6S, 2.4 m) | L1 T1 X1 W1 C1 R1 G1 P1 M1 E2 B1 | The previous design: 7.4 kg, 2.4 m. Kept as the reference point. | `docs/DESIGN-BASIS.md`; tradestudy C0 | Fails G1 at today's prices ($2,003, cost_model.py M quadplane) |
| K03 | Single-boom H-frame quadplane | L1 T1 X1 W1 C2 R1 G1 P2 M1 E1 B1 | Lift motors on a carbon "H" (two cross tubes through the fuselage, fore and aft of the wing), V-tail on one tail boom. One-piece wing lifts off; H-frame unbolts as one unit, so lift wiring never crosses the wing joint. | Mini Talon / Skywalker X8 quadplane conversions, https://discuss.ardupilot.org/t/mini-talon-quadplane-conversion/19763 | ~K01 cost; front props near the wing leading edge cause wash interference `UNVERIFIED` |
| K04 | Folding-prop quadplane | L1 T1 X1 W1 C1 R1 G1 P1 M1 E1 B1 + folding lift props | K01 with folding lift props parked by airflow, cutting the largest cruise-drag term. | tradestudy C0-lean-fold (14.3 vs 11.9 min) | Folding-prop CdA is `ESTIMATE`; measure first (budget-lift.md M3) |
| K05 | Faired, aligned stopped rotors | K01 + printed nacelles and magnetic prop detent | Parks the 2-blade lift props fore-aft inside printed NACA fairings. | `concepts/variants/a3/design.md` | +$22 goods; −85 W cruise `ESTIMATE` on C0 |
| K06 | Tilt-tricopter, scratch-built | L2 T3 X2 W1/W2 C3 R3 G1 P1 M1 E1 B1 | 2 front motors tilt on servos for cruise, rear motor fixed and stops in cruise; ~1.2–1.5 m flying wing or short-pod wing. | E-flite Convergence, HEE WING T1 (configurations.md §3); ArduPilot tilt-rotor guide https://ardupilot.org/plane/docs/guide-tilt-rotor.html | $1,549; tilt servos under load are the known failure (forum S26); tradestudy found T/W 1.59 at 6 kg class, so stay small |
| K07 | Front-tilt quad (2 tilt + 2 fixed) | L2 T3 X2 W1 C1 R4 G1 P1 M1 E1 B1 | Two front motors on tilting nacelles at the wing leading edge, two rear lift motors on short booms that stop in cruise; no separate pusher. | cost_model.py "S tilt-quad"; Foxtech Nimbus-class layouts (`UNVERIFIED` snippet in configurations.md) | $1,597; 2 tilt axes, rear motor-out in hover fatal |
| K08 | All-four tiltrotor | L2 T3 X2 W1 C1 R4 G1 P1 M1 E1 B1 (4 tilts) | All four rotors tilt; nothing parked in cruise. | Mousaei et al. arXiv 2205.05533; forum S23 | 4 loaded servos; S23 builder hit roll/yaw inversion and gave up; tradestudy infeasible at 6 kg |
| K09 | Quad tailsitter, flat wing | L3 T3 X3 W2 C4 R5 G2 P3/P1 M1 E1 B1 | Flying wing with 4 motors in X (2 above, 2 below the wing, on fins); stands on fins; Q_TAILSIT copter-motor mode. | tradestudy rank 1 (TS-quad 7.37); ArduPilot https://ardupilot.org/plane/docs/guide-tailsitter.html | $1,492 (cheapest scratch path); gust tilt 30° at 8 m/s, no weathervane assist, no motor-out |
| K10 | Twin-motor tailsitter flying wing | L3 T3 X3 W2 C3 R6 G2 P1 M1 E2 B1 | Wingtra-style: 2 big props, elevons in slipstream do all hover control. | tradestudy TS-duo; WingtraOne (S46) | $1,601; weathervane crashes documented (S25); any motor-out fatal |
| K11 | Biplane quad tailsitter | L3 T3 X3 W3 C4 R5 G2 P3 M2 E1 B1 | Two stacked wings joined by vertical struts, motor on each strut end; a box structure that stands on its lower wingtips. Very stiff, all-foam-board build. | ArduPilot quadplane-building page link to the foam-board "Box Kite" copter tailsitter (search 2026-11-09, https://ardupilot.org/plane/docs/quadplane-building.html) | Low cost (~K09); biplane L/D lower than monoplane `ESTIMATE`; same gust weakness as K09 but shorter span |
| K12 | Tilt-wing | L4 T3 X4 W1 C1 R4 G1 P2 M1 E1 B1 | Whole wing with 2–4 motors pivots; small tail fan for pitch in hover. | `explorations/tiltwing/`; GL-10 (S43); CL-84 model (S24) | Wing-pivot actuator under full lift load; only one documented ArduPilot build; tradestudy infeasible |
| K13 | Fixed tandem-wing quadplane | L1 T1 X1 W4 C5 R8 G1 P2 M1 E1 B1 | Two short wings, lift motors on the 4 wingtips (no booms); pusher at the tail. Short span packs easily. | configurations.md §3 tandem row; Munk stagger theorem (S4) | No dedicated AP support; pitch stability CG-sensitive; tradestudy infeasible at 6 kg |
| K14 | Box-wing quadplane | L1 T1 X1 W5 C5 R8 G1 P2 M1 E1 B1 | Front and rear wing joined by tip plates; lift motors at the four joints. | concepts.json c1; Schiktanz & Scholz (S3) | Half-chord panels at low Re lose L/D (S21); tradestudy infeasible |
| K15 | Octo / coax X8 quadplane | L1 T1 X1 W1 C1 R2 G1 P1 M1 E2 B1 | 8 lift rotors for hover motor-out tolerance. | tradestudy C1/C2 | Fails G1 ($2,350, cost_model.py) |
| K16 | Bicopter tiltrotor | L2 T3 X2 W1 C3 R6 G1 P1 M1 E2 B1 | V-22-like: 2 tilting rotors, hover pitch by tilt only. | configurations.md §3; forum S22 (builder gave up on AP) | Very high control risk; any motor-out fatal |
| K17 | Ducted-fan / fan-in-wing | L7 T1 X1 W1 C1 R1 G4 P2 M3 E2 B1 | Lift fans buried in the wing, covered in cruise. | concepts.json c2 (ERAU thesis) | EDF hover power high (high disk loading); covers need actuators; listed for completeness |
| K18 | Pure quadcopter, folding arms | L5 T5 X6 W7 C6 R7 G1 P4 M6 E1 B4 | Bought carbon X frame, 4S. Not a transition aircraft. | — (baseline) | Fails mission M-A (no transition, `REQUIREMENTS.md` §3); useful as trainer (D15) and as the hover test-bed for any L1/L3 motor choice |

### 3.2 Buy-and-modify

| ID | Name | Code | Description | Source | Screen |
|---|---|---|---|---|---|
| B01 | HEEWING T1 Ranger VTOL as the aircraft | L2 T3 X2 W1 C2 R3 G4 P6 M5 E1 B3 | Buy the 730 mm tilt-tri PNP (+FC). Team work: ArduPilot setup, failsafes, tuning, logging, a mission add-on (camera, precision landing), structural/propulsion test campaign. | DefianceRC listings (§2) | ≈ $1,190 total, ≈ $810 reserve (§2 calc); ~1 kg class `UNVERIFIED`; small, wind-sensitive at RFS; little airframe design content |
| B02 | HEEWING T2 Cruza VTOL | L2 T3 X2 W1 C2 R3 G4 P6 M5 E1 B3 | Same idea at 1.2 m, 2.0–3.5 kg flying weight (Rotorama listing). | Rotorama listing (§2) | ≈ $830 kit; EU seller → lead-time and customs risk for a mid-December order; US stock `UNVERIFIED` |
| B03 | Mini Talon quadplane conversion | L1 T1 X1 W1 C2 R1 G1 P2 M5 E1 B2 | Buy the EPO 1.3 m airframe, add two carbon booms with 4 lift motors (well-trodden ArduPilot conversion with 300+ forum posts). | https://discuss.ardupilot.org/t/mini-talon-quadplane-conversion/19763 | Kit $150 out of stock (`UNVERIFIED` availability); then ≈ K01 propulsion cost minus most airframe materials |
| B04 | Foam FPV flying wing → twin tailsitter | L3 T3 X3 W2 C3 R6 G2 P6 M5 E1 B2 | Buy a cheap EPP wing (e.g. ZOHD/AtomRC class `UNVERIFIED`), mount two motors on the leading edge and fins as legs. | Dual-motor tailsitter thread https://discuss.ardupilot.org/t/dual-motor-tailsitters/15302 (1 m span, 10 in props, 1.38 kg build reported) | Very cheap (< $150 airframe `ESTIMATE`); same weathervane risk as K10 |
| B05 | MFE Fighter / Striver 4+1 kit | L1 T1 X1 W1 C1 R1 G1 P2 M5 E2 B3 | Commercial 2.1–2.4 m 4+1 kit, add electronics. | 3DXR listing (§2) | £800 airframe only + 6S M-class propulsion ⇒ over G1 `ESTIMATE`; UK/China lead time |
| B06 | Two-aircraft plan: bought VTOL mule + scratch main | B01 (mule) + K01, K06 or K09 (main) ; B5 | Buy B01 in December, fly it in January while the main aircraft is built: pilot practice (D15), ArduPilot VTOL parameter experience, failsafe tests. Main aircraft reuses the radio and charger. | REQUIREMENTS.md D15 (trainer) | Mule ≈ $410–$550 incl. packs; main must then fit ≈ $1,300–$1,400 ⇒ only class-S scratch layouts fit; reserve thin |
| B07 | Bought carbon quad frame + bolt-on foam wing | L1/L6 … B4 | Buy a 450–650 mm carbon X frame (motor mounts, arms, landing gear done) and design only the wing and its mount. Basis for U01 and K18. | — | Lowest build hours of any scratch option `ESTIMATE` |

### 3.3 Unconventional (worth a cheap test before dismissal)

| ID | Name | Code | Description | Why it might win | What kills it | Source |
|---|---|---|---|---|---|---|
| U01 | Wing-assisted quad (tilt-body) | L6 T5 X5 W1 C6 R7 G1 P2 M2 E1 B4 | A bought X quad with a foam wing fixed at ~+20–30° incidence relative to the frame; in fast forward flight the quad pitches nose-down and the wing carries part of the weight. Flies in ArduCopter only: no transition mode, no servos, no tilt hardware. | Lowest control risk of anything that has a wing; reuses Copter tuning; one-person build in days | Wing is stalled/draggy in hover and gusts (download, weathercocking); efficiency gain may be small; does it count as "VTOL drone with transition"? (team's call) | Engineering idea `ESTIMATE`; no documented build found yet — research agent to search |
| U02 | Ring-wing (annular) quad tailsitter | L3 T3 X3 W6 C4 R5 G2 P3 M3 E1 B1 | Coleopter-style: a ~0.5–0.6 m diameter printed/foam ring wing around a quad, motors on 4 internal struts; sits on the ring's trailing edge. | Fits one box with no assembly (P3, best transport); ring is stiff and guards the props; same ArduPilot tailsitter mode as K09 | Low aspect ratio ⇒ poor L/D; large side area in hover gusts; little documented hobby evidence | Coleopter history `UNVERIFIED`; ArduPilot tailsitter guide |
| U03 | Motor-only quad tailsitter (no control surfaces) | L3 T3 X3 W2 C4 R5 G2 P1 M2 E1 B1 | K09 with every moving surface removed; all control by differential thrust in both modes. | Zero servos ⇒ fewest parts, fastest repair; foam-board build in hours | Yaw/roll authority in cruise from differential thrust is small at high speed; needs a 2:1 T/W | https://discuss.ardupilot.org/t/3d-printed-cygnet-vtol-build-motor-only-no-control-surfaces-petg-version/142979 |
| U04 | Flat-pack foam-board quadplane | L1 T1 X1 W1 C1 R1 G1 P5 M2 E1 B1 | K01 built from paper-faced foam board (Flite Test style), laser-cut templates; wing panels slide on carbon spar tubes; a crashed panel is re-cut in ~1 h. | Repair speed and build hours (schedule weight 15, buildability 20) | Foam board stiffness/weight at 3–4 kg; water sensitivity at bay-shore site | FT build method `UNVERIFIED`; mentor's "manufacturing as a design axis" |
| U05 | Single-servo coupled front tilt | L2 T3 X2 W1 C3 R3 G1 P1 M1 E1 B1 | K06, but both front motors sit on one carbon tube running through the wing that one servo rotates. | Halves tilt servos and keeps tilt symmetric; tube is also the front spar | Loses vectored yaw (ArduPilot tilt-tri uses differential tilt for yaw `UNVERIFIED`); one servo = single point of failure | Engineering idea; HEE WING T1 uses 2 servos (conversion kit contents §2) |
| U06 | Retractable-wing tailsitter | L3 T3 X3 W2 C4 R5 G2 P4 M3 E1 B1 | Quad tailsitter whose outer wing panels fold or slide in during hover, cutting gust drift (0.820 m → 0.081 m at ~5 m/s in the cited paper). Folding hinge also gives P4 transport. | Directly fixes the tailsitter's main weakness (wind) | Mechanism under aero load; build hours | Liang et al. arXiv 2511.04251 (S30) |
| U07 | Split-chemistry quadplane | L1 T1 X1 W1 C1 R1 G1 P1 M1 E5 B1 | K01 with a small high-C LiPo for the lift motors and a bought Li-ion pack for the pusher and avionics. | Energy-dense cruise pack → growth path to mission M-B without a new airframe | Two packs, two monitors, more wiring; only pays when cruise > ~15 min `ESTIMATE` | tradestudy Li-ion packs (RobopowerUA 15000, over cap on C0) |
| U08 | Quadplane with printed crushable feet + wheels | L1 T1 X1 W1 C1 R1 G3/G5 P1 M1 E1 B1 | K01 whose boom ends carry sacrificial printed feet, plus two small wheels so a failed hover can end in a rolling fixed-wing landing. | Crash repair in minutes; adds an emergency landing mode (mentor's wheels-vs-skids question) | Wheels' mass and drag; RFS grass may be too rough to roll | Mentor guidance 2026-11-04 (open question) |

Count: 18 K + 7 B + 8 U = **33 concepts** (K02, K15, B05 expected to fail G1; K18 fails M-A; they are kept so the
ranking shows why).

---

## 4. Completeness audit (round 1)

Per the mentor's method: list which sources added new options, and where the chart has no concept.

| Source | New options it added |
|---|---|
| Previous trade study (tradestudy.json) | L1–L4, R1–R6, W4–W5, E3–E4 |
| concepts.json (a1–c3) | T4, L7, faired rotors (K05) |
| cost_model.py | class-S vs class-M split, price floor |
| Web search 2026-11-09 (kits, forum) | B2, B3, P6, M5, C4 (motor-only), W3 (Box Kite), U03 |
| Mentor guidance | G3 vs G1 question, M-axis, U04, U08 |
| This agent (no external source) | L6/T5/X5 (U01), W6 (U02), E5 (U07), B5 (B06), U05 |

Empty or thin regions (candidate for round 2 once research FINDINGS.md land):
- **M4 (balsa/ply ribs) and M7 (wet lay-up)** appear in no concept: both are slower than M1/M2 for a first-time
  team `ESTIMATE`; a balsa-rib wing on K01 is a valid variant if foam stiffness fails.
- **T2 (nose tractor) + L1** (quadplane with a tractor) is unused; it moves the cruise prop away from the booms'
  wake but puts it in front of the camera/pitot; minor variant of K01.
- **W6 ring wing and L6 tilt-body** have only one concept each and no documented hobby build yet; the
  existing-vtol agent should search for both before they are tested.
- **Kits with tailsitter layout (B3 + L3)** are missing: no purchasable tailsitter kit was found in this pass.

Saturation: round 1 added 6 new options from external sources and 5 from this agent; not saturated.

---

## 5. Cheap tests before dismissing the unconventional ones

| ID | Test | Cost / time `ESTIMATE` | Pass sign |
|---|---|---|---|
| U01 | Tape a foam-board wing at 25° to any team quad; fly in ArduCopter, log current at 8, 12, 15 m/s with and without the wing | < $20 foam, 1 day | Cruise current drops ≥ 20 % at 12 m/s with no hover instability |
| U02 / U03 / K11 | Foam-board 0.6 m model on 4 small quad motors from K18; hover in QHOVER with Q_TAILSIT, fan a 5 m/s gust | < $40, 2 days | Holds position within 1 m; then try transition |
| U04 | Cut one wing panel from foam board and one from hot-wired XPS; bend-test and weigh | < $30, 1 day | Foam board ≤ XPS mass at equal tip deflection |
| U05 | Bench rig: one servo rotating a tube with two motors at hover thrust; time 0–90° | < $40, 1 day | Servo holds and does not strip at full thrust |
| U06 | Hinge mock-up loaded to 2 g wing load | < $20, 1 day | No slop; lock engages by hand |
| U07, U08 | Desk calc only until the main layout is chosen | 0 | — |
