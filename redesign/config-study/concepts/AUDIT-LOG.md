# Completeness audit log

Method (mentor, 2026-11-04): ask "is this complete, what is missing?" against `MORPH.md`, record which sources
added a genuinely new concept, repeat until a round adds nothing. Renames and minor variants of existing rows are
not logged as additions. Tags: `ESTIMATE` = engineering guess, `UNVERIFIED` = not checked against a primary source.
Prices: date seen and vendor given per item; search-result listings are `UNVERIFIED` until a product page is opened.

---

## Round 1 — 2026-11-09 (completeness auditor)

Inputs: `MORPH.md` (33 concepts K01–K18, B01–B07, U01–U08), `STUDY-BRIEF.md`, `requirements/REQUIREMENTS.md`,
`inputs/ADVISOR-XV24-LESSONS.md`, `inputs/MENTOR-GUIDANCE-2026-11-04.md`, `research/components-cost/cost_model.py`
(run 2026-11-09 with `python -I` on a scratch copy; new rows below use its unit prices and floors unchanged),
`docs/research/configurations.md`. The three `research/*/FINDINGS.md` files still did not exist at audit time.

Method this round: walked every cell of the 11-dimension chart for empty or single-concept cells, then ran
web searches (ArduPilot docs and forum, vendor pages, 2026-11-09) for configurations, kits and build methods not
in §3 of `MORPH.md`.

### Additions (6)

| ID | Name | Code (L·T·X·W·C·R·G·P·M·E·B) | Why it is new, not a variant | cost_model.py total (class S) | Source |
|---|---|---|---|---|---|
| **K19** | Flying-wing (tailless) quadplane, Skywalker X8 / DeltaQuad style | L1 T1 X1 W2 C3 R1 G1 P1 M1 or M5 E1 B1 or B2 | Fills the empty **W2 + L1** cell. Every quadplane in §3 has a tail and pod (K01, K03, B03); the tailless 4+1 is the most-documented hobby quadplane form on ArduPilot. Two elevon servos instead of four surface servos, no tail boom, short fuselage: cheaper and packs shorter than K01. | **$1,591.85** (reserve $408.15; 4 lift S stations, 1 cruise, 2 ctrl servos, 3 packs) | Build threads: https://discuss.ardupilot.org/t/skywalker-x8-quadplane-build-4/42083 (4th X8 quadplane by one builder; wing extensions 880 g each, stall ≈ 14 m/s), https://discuss.ardupilot.org/t/skywalker-x-8-vtol-conversion-my-way/66879, https://discuss.ardupilot.org/t/a-tale-of-two-quadplanes/18856; PX4 X8 setup https://discuss.px4.io/t/skywalker-x8-vtol-setup/7932. All forum builds, not manufacturer data. |
| **K20** | Single-motor non-vectored tailsitter (3D-foamie profile plane stood on its tail) | L3 T3 X3 W1 C3 (elevons + rudder in prop wash) R9 (1 rotor) G2 P2 M5 or M2 E2 B2 | Fills a **new rotor-count option R9 = one rotor**: every tailsitter in §3 has 2 or 4 motors. ArduPilot documents the type (`Q_TAILSIT_ENABLE 1`, `Q_FRAME_CLASS 10`, `Q_TAILSIT_MOTMX 0`): "any fixed-wing aircraft capable of 3D flight can be flown as a single or dual motor tailsitter". Cheapest propulsion of any concept (one motor, one ESC). Kill risk: no yaw authority in hover without vectoring; forum builders report pitch stability and rudder-in-wash problems; one ArduPilot developer said a large rudder cancels the high-AR wing benefit. **No logged hover-to-cruise transition of a single-motor tailsitter on ArduPilot found this round: `UNVERIFIED`.** | **$1,568.80** (reserve $431.20; 1 M lift station, 4 ctrl servos, 3 × 6S packs) | ArduPilot tailsitter guide https://ardupilot.org/plane/docs/guide-tailsitter.html (manufacturer/doc); forum: https://discuss.ardupilot.org/t/non-vectored-tailsitter-planes/22704, https://discuss.ardupilot.org/t/single-motor-tailsitter-with-elevons/23293, https://discuss.ardupilot.org/t/tips-tricks-for-high-aspect-ratio-single-motor-tail-sitter/46129 (2019; advice: add two wing motors with pitch vectoring instead) |
| **K21** | Hexa 6+1 quadplane (class S) | L1 T1 X1 W1 C1 R10 (6 lift + 1 cruise) G1 P1 M1 E1 B1 | Fills the gap between K01 (no hover motor-out) and K15 (octo, fails G1). Six 4S lift stations on the K01 airframe is the **only hover-motor-out-tolerant layout that passes G1** at current prices. ArduPilot QuadPlane hexa is frame class 2; a Jan-2026 dev call discussed a QuadPlane thrust-loss PR tested on a hexa (merge status `UNVERIFIED`). Motor-out survival still needs power headroom ("brute force"), so T/W ≥ 2 with one motor out must be sized in. Costs: two more motors, ESCs, props and wiring than K01; longer booms or a third cross-tube. | **$1,732.90** (reserve $267.10; 6 lift S stations, 1 cruise, 4 ctrl servos, 3 packs) | https://ardupilot.org/plane/docs/quadplane-frame-setup.html (doc); dev call https://discuss.ardupilot.org/t/dev-call-jan-12-2026/141878; forum on hexa motor-out limits https://discuss.ardupilot.org/t/hexacopter-redundancy/72447, https://discuss.ardupilot.org/t/will-an-hexacopter-crash-when-there-is-a-motor-failure/79795 |
| **K22** | Tri 3+1 quadplane (two fixed wing-mounted lift motors + one tail lift motor on a yaw servo + pusher) | L1 T1 X1 W1 C2 R11 (3 fixed lift + yaw servo + 1 cruise) G1 P2 M1 E1 B1 | New rotor option: §3 has tilt-tri (K06) and 4+1 but not the **fixed-tricopter lift set**. One lift station fewer than K01 (saves ≈ $36 goods plus an ESC output), rear motor on the tail boom doubles as the yaw actuator; ArduPilot QuadPlane lists Tricopter as `Q_FRAME_CLASS 7`. Kill risk: one loaded yaw servo on the tail motor (same buildability penalty as a tilt servo), no hover motor-out, and **no documented 3-fixed-lift + pusher hobby build found this round (`UNVERIFIED`)**; a forum reply warns frame-class/servo mapping for tri has had firmware bugs. Listed so the cheaper-than-4+1 region is not empty; needs a SITL check before anything else. | **$1,609.48** (reserve $390.52; 3 lift S stations, 1 cruise, 5 servos incl. yaw) | https://ardupilot.org/plane/docs/quadplane-frame-setup.html (doc, class 7); forum https://discuss.ardupilot.org/t/reverse-quadplane-tricopter/102423, https://discuss.ardupilot.org/t/questions-about-q-frame-class-parameters/72797 |
| **B08** | Sub-$350 ArduPilot-ready tilt-tri PNP: FIMI Manta (700 mm) or ZOHD Altus VTOL (980 mm) | L2 T3 X2 W1 C2 R3 G4 P6 M5 E1 B3 | Same layout family as B01/B02 but a **different buy path**: the manufacturer publishes ArduPilot parameter files (Manta: Matek F405-WTE target, FIMI param files per forum Aug 2023), which removes B01's `UNVERIFIED` "does the bundled FC run ArduPilot with logging" risk, at roughly half B01's price. Changes the B06 arithmetic: a < $300 mule leaves ≈ $1,500 for the scratch main aircraft instead of $1,300–1,400. Manta: 3 motors (2 front tilt, fixed tail), ~500 g TOW, detachable wing, 3S 18650 pack; price seen $165–323 (rcbuying.com listing, 2026-11-09, `UNVERIFIED`), PNP-FC edition ≈ $191–262 at launch (2023 press). Altus VTOL PNP: 3 × 2204 motors, 2 tilt servos, needs own FC; £219.95 Unmanned Tech UK, sold out (2026-11-09); VTOL add-on kit $119.99 at DefianceRC on top of the $154.99 Altus PNP. Kill risk: sub-1 kg aircraft are wind-limited at RFS (same as B01); FIMI US stock and 2026 price `UNVERIFIED`; one forum poster disputed FIMI's endurance claims. | ≈ $190–330 kit + packs, radio, ground floor ≈ **$950–1,100 total `ESTIMATE`** (same method as MORPH §2 kit-path calc) | FIMI forum thread https://discuss.ardupilot.org/t/new-fimi-manta-vtol-fixed-wing/104248 (one builder reports "flies very well" on ArduPilot, no logs posted); FIMI store https://store.fimi.com/products/fimi-manta-vtol-fixed-wing; review https://oscarliang.com/fimi-manta-vtol; ZOHD Altus VTOL https://www.unmannedtechshop.co.uk/products/zohd-altus-vtol, https://www.defiancerc.com/products/zohd-altus-twin-motor-980mm-fpv-plane-vtol-kit |
| **B09** | Bought design files, printed airframe (Flightory Stallion VTOL, Eclipson E-VTOL) | Stallion: L2 T3 X2 W1 C2 R3 G4 P2 M3 E1 B6 (new: buy the design, make the airframe) · E-VTOL: L3 T3 X3 W2 C3 R6 G2 P2 M3 E1 B6 | New **buy-vs-build option B6: buy the CAD/STL, print it on Jacobs Hall's free Prusa printers**. Fills M3 (FDM airframe) with complete, flown designs rather than a team-designed printed structure. Stallion: 1.30–1.34 m span, LW-PLA with PETG hard parts, twin tractor + V-tail with a tilt-tri VTOL pack, SpeedyBee F405 Wing + M10Q GPS, ArduPilot parameter files supplied; files $34.99 + VTOL pack $12.99 (flightory.com, 2026-11-09). Eclipson E-VTOL: 1,065 mm LW-PLA twin-motor tailsitter, ~800 g AUW on 3S, Matek F405 Wing, transitions flown Jan 2022 with yaw problems and several crashes during tuning; file price not found. Kill risks: LW-PLA stiffness (a builder reported wing resonance and "PLA not rigid enough"), heat deformation in sun, 100 h-class printer time `ESTIMATE`, licence is personal/recreational (check before a university project uses it), and tilt-tri servo risk as K06. Low design content for a capstone unless the team adds the wing/structure analysis. | Files ≈ $48 + filament ≈ $60–100 `ESTIMATE` + class-S propulsion/avionics/ground floors ≈ **$1,250–1,400 total `ESTIMATE`** | Stallion: https://flightory.com/wp-content/uploads/2025/02/STALLION-MANUAL-VTOL-V2.pdf (manufacturer manual), https://dronexl.co/2025/04/04/3d-printed-stallion-drone-diy-fixed-wing/, https://flightory.com/?p=3755 (VTOL pack price); Eclipson: https://discuss.ardupilot.org/t/eclipson-e-vtol-3d-printable-dual-motor-tailsitter/80324 (forum build log) |

New chart options introduced by this round (add to `MORPH.md` §1 in the next edit): **R9** one rotor (single-motor
tailsitter), **R10** 6 lift + 1 cruise, **R11** 3 fixed lift with tail yaw servo + 1 cruise, **B6** buy design
files and print the airframe. Cell **W2 + L1** is now occupied (K19).

### Considered and not added (so round 2 does not repeat them)

| Candidate | Why not a row |
|---|---|
| Vectored twin tailsitter (motors tilt for hover control, `Q_TAILSIT_VFGAIN`) | Minor variant of K10/B04: same airframe plus two tilt servos. Note it in K10's screen as the ArduPilot-recommended form (dual-motor thread, FT Bronco TVBS). |
| E-flite X-Vert (twin tailsitter BNF, $149) and Convergence (tilt-tri PNP) as the "purchasable tailsitter kit" cell | Both **discontinued** at Horizon Hobby (pages read 2026-11-09); proprietary FC, no logging. The B3 + L3 cell stays empty. |
| WLtoys XK X450 (450 mm 3-motor VTOL toy, $150 Walmart/Best Buy listings 2026-11-09) | Proprietary FC, no ArduPilot, fails D7; only a pilot-trainer alternative to B06's mule. |
| Cruciform (X-wing) quad tailsitter (VertiKUL-style) | Form variant of K09 with more side area; nothing it fixes. |
| Wing-mounted lift nacelles without booms on a conventional wing | Covered by K13's tip-motor idea and B03/K03 conversions; no new mechanism. |
| Compound / winged helicopter (ArduPilot Heli + fixed wing) | Rotor never stops; no transition in the mission's sense; heli kit + tuning risk exceeds any benefit. |
| Lighter-than-air assisted VTOL, autogyro jump-start, cyclocopter, monocopter | Fail C2 or C3 or have no supported autopilot mode (D7); not credible in a 12-week student build. |
| "Buy used" (eBay airframes) | A purchasing tactic, not a configuration; applies to any B-row. |

### Sources that produced additions this round

| Source | Added |
|---|---|
| ArduPilot tailsitter guide (doc) | K20 (single-motor type, parameters) |
| ArduPilot QuadPlane frame-setup page (doc) + Jan-2026 dev call | K21 (hexa class 2), K22 (tri class 7) |
| ArduPilot forum X8 quadplane threads | K19 |
| FIMI Manta forum thread, FIMI store, ZOHD/DefianceRC listings | B08 |
| Flightory manual and store, Eclipson forum log, DroneXL | B09 |
| Chart walk (empty cells) with no external source | R9/R10/R11/B6 option codes |

Saturation: round 1 added 6 concepts and 4 chart options from 5 external source groups; **not saturated**. Round 2
should run after `research/existing-vtol/FINDINGS.md` and `research/flight-control/FINDINGS.md` land, and should
specifically (a) look for a logged single-motor tailsitter transition (K20), (b) look for any flown 3-fixed-lift +
pusher build (K22), (c) open the FIMI Manta and Flightory product pages for current US price and stock.

---

## Round 2 — 2026-11-09 (completeness auditor)

Inputs: `MORPH.md` (33 concepts) + round-1 additions K19–K22, B08, B09 (39 concepts), `STUDY-BRIEF.md`,
`requirements/REQUIREMENTS.md`, `inputs/ADVISOR-XV24-LESSONS.md`, `inputs/MENTOR-GUIDANCE-2026-11-04.md`,
`research/components-cost/cost_model.py` (run 2026-11-09 with `python -I` on a scratch copy; new rows use its unit
prices and floors unchanged). `research/existing-vtol/FINDINGS.md` and `research/flight-control/FINDINGS.md` still did
not exist at audit time, so the round-1 follow-ups (a)–(c) remain open for the research agents.

Method this round: walked the 11-dimension chart again for cells still empty after round 1 (M4, M7, T2+L1, B3+L3, W6,
L6), then ran web searches (2026-11-09) for VTOL lift mechanisms, rotor arrangements, buy paths and build methods not
in any row: folding/morphing-wing VTOL, purchasable tailsitter kits, ring-wing builds, wing-assisted multirotors,
binary (retract-servo) tilt, tilt-boom layouts, iNav VTOL, coaxial single-column tailsitters, universal quadplane
boom kits, free printed VTOL design files, and the OMPHobby ZMO as another B08-class kit.

### Additions (2)

| ID | Name | Code (L·T·X·W·C·R·G·P·M·E·B) | Why it is new, not a variant | cost_model.py total (class S) | Source |
|---|---|---|---|---|---|
| **K23** | Folding-wing VTOL (Transwing-type): wings fold about skewed hinges so the four wing-mounted motors form a quad in hover; wings unfold for cruise and all four motors keep pulling | **L8** (new lift option: wing folds, rotors fixed to the wing) T3 **X7** (new transition option: wing-fold schedule, driven as a binary tilt servo or by Lua) W1 C1 (V-tail + ailerons) R4-like (4 motors, none parked) G1 (fuselage belly / skids) **P4 native** (the fold that transitions also folds for the box) M3 E1 B1 or B6 | No row in §3 changes the wing geometry to transition; L1–L7 tilt rotors, the body, the wing on a pivot, or nothing. Here the hinge does what the tilt servos do in K08 (all four motors used in cruise) with **one** actuator instead of four, and the folded state is also the transport state, so it is the only layout whose transport breakdown needs no field joint. Hobby evidence: AeroFold V1/V2 by t4obrien, 1.6 m span, fully printed, 4 motors, V-tail + ailerons on 4 servos, fold driven by **one sail-winch servo through a kevlar pulley line**, min 50 Wh / max ≈ 240 Wh pack, NACA 4414→4412, 2° incidence; designer's log reports successful VTOL transitions posted 2025-05-09 (video on Instagram/YouTube, not opened; `UNVERIFIED`); a viewer judged the OSD to be ArduPilot (`UNVERIFIED`); the V2 page recommends an H7 board because Lua scripting is likely needed. Company evidence: PteroDynamics Parus4, 4 ft span, "flown 100+ times" on a KK board then ArduPilot (sUAS News, March 2019; company claims). ArduPilot hobby attempt (Rolf/Walter, 2021): 2 wing motors + 1 rear, linear actuator seen as a binary tilt servo (`Q_FRAME_CLASS 7`, `Q_TILT_TYPE 1`), proof-of-concept linkage only, no flight; files lost in a flood; two students (Oct 2024, Mar 2025) could not get the hinge geometry to bring the wings fully vertical. Kill risks: **no native ArduPilot mode** (fold must be faked as a binary tilt or scripted), CG shift during the fold (AeroFold V2 was redesigned for it), hinge geometry is the hard part, printed hinge under flight load, the Transwing patent (company says non-commercial builds are welcome, 2019 forum post; check before a university project), and zero documented builds other than AeroFold. Fits the brief's "test the outlandish before dismissing": a foam-board fold mock-up on K18's motors costs < $40 `ESTIMATE`. | **$1,610.52** (reserve $389.48; 4 lift S stations, 0 cruise, 1 fold actuator priced as a tilt servo, 4 ctrl servos, 3 packs; printed-airframe filament inside the S airframe line `ESTIMATE`) | AeroFold files: https://makerworld.com/models/1221812 (V1), https://makerworld.com/models/1810710 (V2), https://www.thingiverse.com/thing:6984316 (CC BY-NC per search listing; pages returned 403 to fetch, specs taken from search snippets and the IntoFPV thread https://intofpv.com/t-folding-wing-vtol-3d-printed-very-cool); ArduPilot hobby thread https://discuss.ardupilot.org/t/tri-mot-transwing/70702; PteroDynamics on ArduPilot https://discuss.ardupilot.org/t/transwing-code-for-ardupilot/42486; sUAS News 2019 https://www.suasnews.com/2019/03/transwing-a-revolutionary-vtol/ (company claims); related student capstone (not read) https://engineering.usu.edu/mae/students/senior-projects/fall2023-spring2024/projects/rapid-prototyped-transition-fixed-wing-vtol-drone |
| **K24** | Reverse tricopter-tiltrotor: one front tractor motor tilts 90° for cruise, two rear lift motors (hover-sized) stop in cruise and vector ±30–45° for yaw | L2 T3 X2 W1 C1/C3 **R12** (new rotor option: 1 front tilt + 2 rear fixed/vectored) G1 P2 M1 E1 B1 | K06 is the mirror (2 front tilt, 1 rear fixed), but the motor roles differ: here the single tilting motor is sized for cruise and the fixed pair for hover, the same lift/cruise split as a quadplane with three motors instead of five, and **one** 90° tilt servo instead of two. ArduPilot has an explicit frame type for it: `Q_FRAME_TYPE 6` (PLUSREV, Peter Hall PR #10846, 2019), `Q_TILT_MASK 8`, `Q_TILT_TYPE 0`. Flight evidence is the weakest of any tilt row: Rolf/Walter hovered it (Aug 16 and 19, 2019, with wings, negative `Q_A_RAT_PIT_P` on standard firmware) but **two forward transitions failed** (Aug 26, Sep 8, 2019: "the nose rears up during transition", rear motors fighting the front one); a second builder's similar aircraft diverged in pitch; the thread continues past page 3 and the outcome was not read this round (`UNVERIFIED`). Listed so the R-axis cell is occupied and because it is the cheapest 3-motor tilt layout in cost_model.py; it needs a SITL run and a search of the thread's later pages before it is ranked. Kill risks: pitch coupling in transition, 3 loaded servos, no hover motor-out. | **$1,579.59** (reserve $420.41; 3 lift S stations, 0 cruise, 3 loaded servos priced as tilt servos, 2 ctrl servos, 3 packs) | https://discuss.ardupilot.org/t/reverse-tricopter-vtol-plane/39829 (pages 1–3 read); ArduPilot tilt-rotor guide https://ardupilot.org/plane/docs/guide-tilt-rotor.html (doc) |

New chart options introduced by this round (add to `MORPH.md` §1 in the next edit): **L8** wing folds about skewed
hinges, rotors stay fixed to the wing; **X7** wing-fold schedule (binary tilt or Lua); **R12** one front tilt + two rear
fixed/vectored.

### Evidence found for existing rows (not new concepts; fold into the screens)

| Row | Evidence (2026-11-09) |
|---|---|
| K11 biplane quad tailsitter | Mini QBIT (Peter Ryseck, U. Maryland research lineage): 3 in quad, two wings below the motors, no control surfaces, wings and nose attach by magnets so they shed in a crash; flies in Betaflight angle mode for hover and acro for cruise with a channel-swap switch (no transition code). Cited 2017 paper: "68 % less power in forward flight than hovering". V1 STLs free, V2 sold as kits. https://hackaday.com/2021/08/02/vtol-tailsitter-flies-with-quadcopter-control-software . Betaflight has no mission/failsafe logging in the D7 sense; use the ArduPilot copter-tailsitter mode instead. |
| B04 foam wing → twin tailsitter | Z-84 TVBS build guide: 845 mm Wing Wing Z-84, two 2204 motors on printed tilt mounts with two micro servos, 650 g AUW, 10 A hover / 2.5 A cruise on 4S Li-ion, flew and transitioned (Aug 2020, params posted Aug 2021); printed pivot blocks broke in early mishaps; "moderate to heavy wind is always a problem for a tailsitter". https://discuss.ardupilot.org/t/z-84-tvbs-conversion-build-guide/60945 . Confirms the round-1 note that the vectored (TVBS) form is the one that flies. |
| U02 ring-wing tailsitter | ETH Zurich annular-wing VTOL (MDPI Drones 2020, 4(2):14): quadrotor inside a foam annular wing that also shrouds the props; hover and forward flight documented in a peer-reviewed paper (abstract via search; page returned 403). https://www.mdpi.com/2504-446X/4/2/14 . A forum poster asked for the same architecture on ArduPilot and found no documentation. Single-motor thrust-vectored ring (AWuAV 3015E, https://hackaday.io/project/27216, 2017) is a K20 × U02 cross, not added. |
| U03 motor-only quad tailsitter | H-Wing thread (quad X motor tailsitter without control surfaces) flies with Q_ASSIST keeping copter stabilisation in fixed-wing modes. https://discuss.ardupilot.org/t/quad-x-motor-tailsitter-without-control-surfaces-h-wing/68833 |
| U01 wing-assisted quad | Closest documented data points: a 1 m tricopter-with-wing hybrid "proved to have quite a problem with wind"; a tilt-tri builder measured 19 A hover → 13 A at 10 m/s with rotors at zero tilt (wing lift alone). Both forum reports; no pure fixed-wing-on-copter build with logs found. https://discuss.ardupilot.org/t/new-build-long-distance/19482 , https://discuss.ardupilot.org/t/tilt-rotor-triplane/13524 . The §5 one-day foam test stays the right next step. |
| B09 printed design files | Free alternatives to the paid Flightory/Eclipson files: MiniHawk VTOL (Steve Carlson, fully printed tilt-tri) and the Nano/Mini/Big Drak VTOL conversions with ArduPilot parameter files (Thingiverse thing 5387189; Printables 698239 / 698235; forum build log https://discuss.ardupilot.org/t/nano-drak-vtol-conversion/86573 "a few successful flights"). Removes the licence-cost line but not the LW-PLA stiffness or print-hour risks. |
| K06 / K07 / U05 tilt servos | ArduPilot `Q_TILT_TYPE 1` (binary) drives retract-style servos that lock at both ends, which removes the "loaded tilt servo holds position" failure mode at the cost of no intermediate angle and no tilt-assisted roll/pitch; `Q_TILT_RATE` must equal the measured servo rate. https://ardupilot.org/plane/docs/guide-tilt-rotor.html (doc). A mechanism choice for the tilt rows, not a new row. |
| Flight stack (all rows) | iNav 9.0 (2025) supports VTOL through two mixer profiles with in-flight switching, tilt-rotor servo rules and automated transitions; tailsitters via `tailsitter_orientation_offset`; not on F411 targets. https://github.com/iNavFlight/inav/blob/master/docs/VTOL.md . For the flight-control agent: an alternative to ArduPilot/PX4 on cheap FCs; logging adequacy for D7 `UNVERIFIED`. |

### Considered and not added (so round 3 does not repeat them)

| Candidate | Why not a row |
|---|---|
| Purchasable tailsitter kit (B3 + L3 cell) | Second search found none in stock: X-Vert discontinued (round 1); only conversions (Z-84, C1 Chaser, Finwing AlbaBird TVBS guides) and printed files (Eclipson, B09). Cell stays empty; treat B04 as its occupant. |
| Universal bolt-on quadplane boom kit | None exists; every VTOL conversion kit found is airframe-specific (HeeWing T1 $138.99–159.99, T2 Cruza $226–264, 2026-11-09 listings `UNVERIFIED`) or a Flightory STL pack ($12.99). B03 already assumes team-made booms. |
| OMPHobby ZMO V2 / Pro (1.2 m tilt-tri, 6S) as another B08 kit | $1,099–1,199 US listings (2026-11-09, `UNVERIFIED`): fails G1 once packs, radio and the ground floor are added. PX4 has a ZMO setup page; ArduPilot support `UNVERIFIED`. |
| All-three-tilt tricopter, tilt-boom quad (two booms each rotating two motors on one servo) | Servo-count variants of K06/K08 and of U05's coupled-tilt idea; forum builders report the hard part is centring several tilt servos, not the layout. |
| Coaxial contra-rotating single-column tailsitter (Pogo style) | K20 with a coax motor; no ArduPilot build found, only a scale-model article. |
| Nicholas Rehm folding-wing tailsitter (dRehmFlight) | Custom Teensy flight controller: fails D7 (no maintained VTOL mode with mission logging). |
| Cruciform / H-wing / tri-wing tailsitter shapes | Planform variants of K09/U03, no new mechanism. |
| Deflected-slipstream, tilt-duct, stop-rotor, autogyro jump take-off, compound helicopter, lighter-than-air | Not zero-roll VTOL at hobby scale, or no supported autopilot mode (D7), or rejected in round 1. |
| Coroplast (corrugated PP) or balsa-rib airframe, three-piece wing (centre + tips), landing cradle for tailsitters, nose-tractor quadplane (T2 + L1) | Material / transport / landing / cruise-prop options for existing rows, not configurations; the still-unoccupied cells M4, M7 and T2 + L1 are deliberate (slower or no benefit for a 12-week build). |

### Sources that produced additions this round

| Source | Added |
|---|---|
| MakerWorld / Thingiverse AeroFold listings (via search snippets), IntoFPV thread, sUAS News 2019, ArduPilot tri-mot Transwing thread | K23 (L8, X7) |
| ArduPilot reverse-tricopter thread (pages 1–3) + tilt-rotor guide | K24 (R12) |
| Hackaday (Mini QBIT), ArduPilot Z-84 TVBS guide, H-Wing thread, Nano Drak log, MDPI Drones 2020, iNav docs | Evidence for K11, B04, U03, B09, U02; flight-stack note (no new rows) |

Saturation: round 2 added **2** concepts and 3 chart options from 2 external source groups, against 6 concepts and
4 options in round 1; 9 candidates were examined and rejected as variants or gate failures. **Approaching
saturation**: the remaining open cells (M4, M7, T2 + L1, B3 + L3) are either deliberately empty or have no
purchasable occupant. Round 3 should run only after `research/existing-vtol/FINDINGS.md` and
`research/flight-control/FINDINGS.md` land, and should (a) open the AeroFold V2 page and transition video to confirm
the fold mechanism, flight controller and licence for K23, (b) read the reverse-tricopter thread past page 3 for K24,
(c) close round-1 items (a)–(c): logged single-motor tailsitter transition (K20), any flown 3-fixed-lift + pusher
build (K22), FIMI Manta / Flightory current price and stock (B08, B09).

---

## Round 3 — 2026-11-09 (completeness auditor)

Inputs: `MORPH.md` (33 concepts) + rounds 1–2 (K19–K24, B08, B09: 41 concepts), `STUDY-BRIEF.md`,
`requirements/REQUIREMENTS.md`, `inputs/ADVISOR-XV24-LESSONS.md`, `inputs/MENTOR-GUIDANCE-2026-11-04.md`,
`research/components-cost/cost_model.py` (run 2026-11-09 with `python -I` on a scratch copy; new rows use its unit
prices and floors unchanged). `research/existing-vtol/FINDINGS.md` and `research/flight-control/FINDINGS.md` **still
did not exist** at audit time, so the round-1 (a)–(c) and round-2 (a)–(c) follow-ups remain open for the research agents.

Method this round: (1) checked the ArduPilot "vehicle types" page and the tailsitter and tilt-rotor guides for any
supported VTOL frame not in a row; (2) read three VTOL taxonomy reviews (Rehan et al. 2022, Finger et al. 2017,
Darvishpoor et al. 2020, via search abstracts) for lift classes not in D1; (3) web searches (2026-11-09) for mechanisms
that remove the known failure points of existing rows: loaded tilt servos (passive tilt), tailsitter wind sensitivity
(free-pivot wing, belly landing), fold actuators (bistable wings), hover motor-out in tilt layouts (Y6), plus
transport (swing-to-stow wing) and buy paths (Y6 tilt kits, printed lift+cruise).

### Additions (2)

| ID | Name | Code (L·T·X·W·C·R·G·P·M·E·B) | Why it is new, not a variant | cost_model.py total (class S) | Source |
|---|---|---|---|---|---|
| **K25** | Y6 tilt flying wing (FireFly6-type): three arms, six motors in coaxial pairs, the two front arms tilt on one axle for cruise, rear pair fixed and stopped in cruise | L2 T3 X2 W2 C3 **R13** (new rotor option: Y6, 6 motors, front 4 tilt on one axle) G1 P2 M1 E1 B1 | Fills the empty cell **motor-out-tolerant + tilting**: K21 (hexa) is the only hover-motor-out row and it is fixed-lift; every tilt row (K06, K07, K08, K24, U05) loses the aircraft on any hover motor-out. One tilt axle (one servo or a pair on a common shaft) carries four motors, so the servo count equals U05 but the redundancy is new. ArduPilot support is documented: the tilt-rotor guide's supported-frame table lists Y6 (`Q_FRAME_CLASS 5`, `Q_FRAME_TYPE` ignored for Tri and Y6); the vehicle-types page names "QuadPlane Delta Y6: 3 pairs of coaxial motors in Y6 arrangement lifting an elevon plane, fronts tilting for fwd flight"; forum setup notes give the FireFly6 motor order as `Q_FRAME_TYPE 11` (Y6F, added by tridge in 3.8.x). Flight evidence: the BirdsEyeView FireFly6 was a commercial APM-based product (diydrones, 2014; DIY frame now discontinued per the archived PX4 page) and a Jan-2025 forum log reports it hovering and, after fixes, "transitions consistently" on ArduPilot. Kill risks: **documented yaw-authority loss during transition** (hover yaw from differential thrust fades as the axle tilts; sideslip led to stalls and flat spins; fixed by smaller winglets and a fast second tilt rate, PR #27194), coaxial pairs cost hover efficiency `ESTIMATE`, no purchasable kit found (2026-11-09), and two more motors/ESCs than K06. | **$1,663.42** (reserve $336.58; 6 lift S stations, 0 cruise, 1 tilt servo, 2 elevon servos, 3 packs): $115 above K06, $70 below K21 | Docs: https://ardupilot.org/plane/docs/guide-tilt-rotor.html (frame table, class 5), https://ardupilot.org/ardupilot/docs/common-all-vehicle-types.html ("QuadPlane Delta Y6"); forum: https://discuss.ardupilot.org/t/solving-y6-transition-issues-no-winglets-firefly6/128439 (2025-01-06), https://discuss.ardupilot.org/t/firefly6-vtol-with-apm-plane/21444 (`Q_FRAME_CLASS 5`, `Q_FRAME_TYPE 11`), https://discuss.ardupilot.org/t/firmware-for-y6-vtol-with-tilting-front-motors/91893 (2022, unanswered on the AP side); product history https://diydrones.com/profiles/blogs/vtol-firefly6-now-available-with-apm-based-autonomy-built-in; archived PX4 page https://docs.px4.io/v1.9.0/en/frames_vtol/vtol_tiltrotor_birdseyeview_firefly_y6_pixfalcon.html |
| **U09** | Free-pivot wing (Freewing / Colibri type): a quad tailsitter wing carrying the four motors, with the fuselage hung on a free pitch pivot at the wing's aerodynamic centre, so the body stays level while the wing settles into the relative wind; a small tail motor on the fuselage trims the body in hover and adds cruise thrust | L6/L3 hybrid T3 (+ tail motor) X5 (no autopilot mode; copter pitch-over) **W8** (new wing option: wing free to rotate in pitch relative to the body) C3 (elevons on the wing) R5 G1 (fuselage belly / skids, body stays level) P2 M1 E1 B1 | No row lets the wing and body move relative to each other passively: U01 fixes the wing to the quad (and stalls it in hover and gusts), U06 and K23 move the wing with an actuator, K12 pivots it under servo load. A free pivot is the classic answer to gust sensitivity (NASA free-wing studies, CR-2946, 1978; University of Maryland / Freewing Aerial Robotics "tilt-body" STOL UAVs built with Rutan, 1990s–2000s) and it keeps the payload level through transition, which the Colibri paper gives as the point of the design. Hardware evidence at hobby scale: ENAC / ISAE-SUPAERO / ONERA / LAAS "Colibri", 1.7 kg (wing 0.53 kg with four motors, fuselage 1.17 kg), 12-bit encoder on the pivot, elevons, Paparazzi autopilot, **hover only** (2 m climb, 54 s hold, one waypoint); no transition flown. A US patent (11254430, "tilt winged multi rotor") claims the same free wing on a multirotor. Kill risks: **no ArduPilot or PX4 mode** (the simplest team path is an ArduCopter quad with a passive wing, as U01, which gives up the body-level benefit), documented wing–body coupling oscillations and poor disturbance rejection in hover, a pivot bearing and encoder under flight load, and zero transition evidence at any scale on an open autopilot (`UNVERIFIED` whether any Freewing Scorpion flew a VTOL profile; it was STOL, piston). Fits the brief's "test the outlandish before dismissing": the §5 U01 foam-wing test with the wing on a free spar bearing instead of taped fixed costs the same < $20 and one day `ESTIMATE`, and settles whether a free wing stops the hover download / weathercock problem. | **$1,591.85** (reserve $408.15; 4 lift S stations on the wing, 1 S cruise/tail station, 2 elevon servos, 3 packs; pivot bearing and encoder not in cost_model.py, about $30 `ESTIMATE`) | Colibri: https://arxiv.org/abs/2406.17313 and https://ar5iv.labs.arxiv.org/html/2406.17313 (ICUAS 2024, peer-reviewed); history: https://en.wikipedia.org/wiki/Freewing_Scorpion , Aeronautical Journal "Flight mechanics of a freewing tilt-body aircraft" https://resolve.cambridge.org/core/journals/aeronautical-journal/article/abs/flight-mechanics-of-a-freewing-tiltbody-aircraft/2501505B2B094D0E8AE8F4D43F0AA363 ; NASA CR-2946 (1978) via search listing; patent https://patents.google.com/patent/US11254430 ; ONERA 2025/26 internship on a freewing "T1 Ranger" with INDI in Paparazzi https://w3.onera.fr/stages/sites/default/files/2024-12/DTIS-2025-67.pdf (listing only, results `UNVERIFIED`) |

New chart options introduced by this round (add to `MORPH.md` §1 in the next edit): **R13** Y6 coaxial pairs with the
front axle tilting; **W8** wing free to pivot in pitch relative to the body. Note also **G6** belly landing for
vectored twin tailsitters (ArduPilot "TVBS"), recorded below as an option for K10/B04, not a row.

### Evidence found for existing rows (not new concepts; fold into the screens)

| Row | Evidence (2026-11-09) |
|---|---|
| K10 / B04 twin tailsitter | ArduPilot's tailsitter guide defines the **TVBS (Thrust Vectored Belly Sitter)**: "dual motor vectored thrust tailsitters that don't sit on their tails, but rather their belly"; takes off from a horizontal stance (tilt servos need at least 45°, 60° preferred, of throw each side), `RCx_OPTION 89` forces the tilts upright at idle so it can also land as a fixed wing without prop strike. The page says belly landers "lie flat for landing to improve stability in wind", a direct answer to the weathervane-landing crashes logged against K10. The Z-84 TVBS guide cited in round 2 is this type. https://ardupilot.org/plane/docs/guide-tailsitter.html (doc). Adds landing option **G6** (belly) for the vectored twin rows. |
| U06 retractable-wing tailsitter | University of Pennsylvania (GRASP / SIG), ICRA 2021: a quadrotor with 3D-printed bistable folding wings that snap between folded and deployed **with no extra actuator**, driven by a thrust pulse and the inertia of the centre mass (about 0.75 s full-thrust pulse to deploy). 783 g prototype on ARRIS X220 electronics. Mode switching was tested on a boom and the wings by hand; **no winged flight**. A zero-actuator fold mechanism for U06, not a flown concept. https://arxiv.org/abs/2011.00426 , https://ar5iv.labs.arxiv.org/html/2011.00426 |
| K06 / K07 / U05 tilt servos | Ito, Funada, Sampei (ECC 2024): four rotors on a link joined to the fuselage by a **passive joint**, tilt angle set by rotor thrust alone, no servo. **Simulation only**; no hardware. Keep as a bench idea for the tilt rows (one unloaded hinge with end stops instead of a loaded servo), not a row. https://arxiv.org/abs/2311.05259 |
| B09 / M3 printed airframe | Tsung Xu (June 2025 press): lift+cruise VTOL printed as 100+ parts in foaming PLA and PETG on a Bambu A1, built in 90 days by a self-taught engineer, claims a 130-mile / about 3 h flight; early hover tests failed from ESC overheating. Flight controller, mass and span not stated; claims are the builder's own (`UNVERIFIED`). Supports the M3 build path's feasibility, not a new row. https://3dprintingindustry.com/news/amateur-engineer-tsung-xu-creates-a-high-endurance-3d-printed-vtol-drone-240885/ |
| K01 (pusher) | Forum thread 2026-07-16: a 4+1 whose **pusher also tilts down** (slow screw actuator, 7 s for 90°) to add lift so the four lift motors can be cheaper. Only reply: "not supported by any current frame class or type", needs a custom frame class; suggested a coaxial X8 + fixed pusher instead. Not flown. https://discuss.ardupilot.org/t/standard-quad-vtol-plus-rear-pusher-with-tilt-how-to-setup/144581 |
| All rows (taxonomy check) | Rehan et al. 2022 (Aeronautical Journal) sorts hybrid VTOL UAVs into four convertiplane classes (tilt-rotor, tilt-wing, rotor-wing/stop-rotor, dual-system lift+cruise) and three tail-sitter classes (mono/dual/quad thrust); Finger et al. 2017 adds lift fans, ducted fans and jet lift; Darvishpoor et al. 2020 splits tilt vs non-tilt. Every class is already a D1 option (L1–L7) or a rejected one (stop-rotor, jet). No new lift class found. https://cambridge.org/core/journals/aeronautical-journal/article/vertical-takeoff-and-landing-hybrid-unmanned-aerial-vehicles-an-overview/422DF985F2393E5E8EA82E3299190497 ; https://researchgate.net/publication/320617037 |

### Considered and not added (so round 4 does not repeat them)

| Candidate | Why not a row |
|---|---|
| Passive-joint rotor tilt (no servo), arXiv 2311.05259 | Simulation only, no hardware, no autopilot support (fails D7); logged as a mechanism note on the tilt rows. |
| Bistable zero-actuator folding wing on a quad (UPenn, ICRA 2021) | No winged flight demonstrated; wings tested by hand. Mechanism note for U06. |
| "Chinook" quadplane: coaxial pair at nose and tail of a flying wing, props tilt for cruise | Built and hovered "with some manual help" by one forum member; ArduPilot developer (Peter Hall) says the fore-and-aft bicopter layout is not supported; repliers saw no roll authority in VTOL. Fails D7. https://discuss.ardupilot.org/t/chinook-layout-quadplane-configuration-sort/99493 |
| 4+1 with a tilting pusher as fifth lift motor | Not supported by any frame class, not flown (2026-07 thread above); a K01 variant with one more loaded actuator. |
| TVBS belly-sitter as its own row | Same airframe as K10/B04 plus two tilt servos; recorded as landing option G6 on those rows (round 1 already treated the vectored twin as a K10 variant). |
| Tilt-Y3 ("QuadPlane Delta Y3", all three motors tilt) and tilt-hexa (front four of six tilt, ArduPilot tilt-rotor guide) | All-three-tilt was rejected in round 2 (servo-count variant of K06); tilt-hexa is K21 + four tilt servos, the worst case of the loaded-servo penalty. |
| Swing-to-stow wing (whole wing pivots parallel to the fuselage for transport) | Only a patent (US 12084175 "variable incidence wing aircraft having a wing stowage mode") and swing-wing F-14 foamies found; no VTOL product or build. A P-option idea for K01/K19 if the 1.2 m box ever fails, not a configuration. |
| Tandem-wing tilt-wing (FAU senior design 2020) | W4 + L4; the old trade study found both tilt-wing and tandem wing infeasible, and the FAU page gives no flight result. Variant of K12/K13. https://www.fau.edu/engineering/senior-design/projects/fall2020/hybrid-fixed-wing-quad-rotor-drone/ |
| MorphoCopter (quad that folds into a stacked bicopter) | No wing, no cruise mode; a transport trick for K18 only. https://arxiv.org/abs/2506.07204 |
| Rotor-wing / stop-rotor (ROTORwing drone; ArduPilot 8 kW stopped-rotor thread) | Rejected in round 2; the ArduPilot thread confirms it would need "a large Lua script to manage everything". https://discuss.ardupilot.org/t/can-ardupilot-be-modified-to-control-a-stopped-rotor-configuration-with-8kw-motors/115769 |
| Flapping-wing (ornithopter) VTOL | Not in any round yet: no open-autopilot support, no useful cruise at 2–4 kg; fails D7 and the C2 hover-in-wind requirement. |
| Y6 tilt as a bought kit (B3 + R13) | No Y6 tilt-rotor kit for sale found (2026-11-09); FireFly6 DIY frame discontinued. K25 is scratch-only. |
| Hobby-scale free-wing build (B2 + W8) | None found; "Freewing" search results are the EDF-jet brand. U09 rests on research hardware only. |

### Sources that produced additions this round

| Source | Added |
|---|---|
| ArduPilot tilt-rotor guide (frame table) + vehicle-types page (doc), FireFly6 forum logs 2017–2025, diydrones 2014 product post | K25 (R13) |
| arXiv 2406.17313 (ICUAS 2024, ENAC/ONERA/LAAS), Freewing Scorpion history, NASA CR-2946, US 11254430 | U09 (W8) |
| ArduPilot tailsitter guide (TVBS section) | G6 landing option on K10/B04 (no new row) |
| UPenn bistable wing, Ito et al. passive tilt, Tsung Xu printed VTOL, Chinook and tilt-pusher threads, three taxonomy reviews | Evidence and rejections only |

Saturation: round 3 added **2** concepts and 2 chart options from 2 external source groups, against 2 in round 2 and 6
in round 1, and 12 candidates were rejected. Both additions have weaker evidence than any round-1 or round-2 row
(K25: a discontinued product plus forum logs; U09: hover-only research hardware), and the three taxonomy reviews list
no lift class the chart lacks. **Treat the configuration space as saturated for lift method, rotor arrangement and
transition method.** Round 4, if run at all, should run only after `research/existing-vtol/FINDINGS.md` and
`research/flight-control/FINDINGS.md` land, confine itself to buy paths and build methods (the cells M4, M7, T2 + L1,
B3 + L3, B3 + R13 stay empty for stated reasons), and close the open follow-ups: round 1 (a)–(c), round 2 (a)–(c), and
from this round (d) whether any Colibri or Freewing-type aircraft has flown a transition on an open autopilot (U09)
and (e) the FireFly6 thread's final tilt-rate PR status and whether a 3-arm Y6 fits the 1.2 m box without a field joint (K25).
