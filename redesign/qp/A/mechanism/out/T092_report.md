# T-092: FC 75 mm off the wing centre (D-239 implementation). 2026-11-23. Not VERIFIED COMPLETE. Committed in 5660ee07 (D-240); round-4 review fixes 2026-11-23 marked [R4].

Labels: **interference** (collide_a pose 21 + 18 linkage poses, a_assembly sweep, proxy_collide screen, wire-wire distance check), **illustrative / hand calculation** (CG tally, wire lengths, masses; EST where marked). No kinematics, rigid-body dynamics, FEA, CFD or flight dynamics was run in T-092; the GM figures quoted are the T-091 FEA-lite results (not re-run). Unknowns "—".

## Acceptance test (restated)
FC (Kakute H743-Wing, mount, stack) 75 mm off centre along the spar, hard-mounted; CAD, cable runs inside channels / cover (no new exposed wire, no open ends), build steps, parts list, INS_POS updated; mass / CG / SM re-run; stale claims text fixed; R15 shipping read; gates once at the end: build_a fails only the 1.5 kg gate, proofs the same 12 STRICT FAILs, collide + 18 linkage poses + a_assembly clean.

## Result: met, with the open items in s6
Gates (`T092_data/gates/gates_summary.txt`, script `T092_data/run_gates_t092.sh`):
| Gate | Result |
|---|---|
| build_a | exit 1, only `graph:mass TOTAL aircraft 1641 g > limit 1500 g` (10 modules, 1 error) |
| wire_inventory | exit 0; exposed strand length 0.597 m = T-084 (0.597); min bend 4.0 mm (centre lines) |
| cad_mass, mission_gate --o4b | exit 0 |
| collide pose 21 | PASS (0 pairs > 0.05 mm, 0 wire ends, 0 folds; 585 bodies) |
| collide 18 linkage poses | PASS (0 / 0 / 0) |
| a_assembly | exit 0: 66 steps, 129 parts placed, 0 blocked paths |
| proofs/run_all | exit 1: 12 FAILS (CL-A-MASS-PRED, -MASS-GATE-ROOM, -CUTS-REQUIRED, -VIB-IN-BAND, -VIB-FC, -VIB-GM, -VIB-GM-SHIFT, HORN-RIB-FOAM-HOLD / -STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY) = the expected 12 (T-084 had 8: the 4 VIB claims were rebuilt by T-089 after it) |
| drawings, build_guide, parts_links | exit 0 |
First pose-21 run failed with 3 wire folds (E-HRN-06, fake kink from a 0.26 mm sample next to a 2.8 mm one after a 68 deg rise with an 8 mm radius); radius at that vertex set to 6 mm, the kink function (`collision/collide.py kinks`) returns none, all gates re-run from the start (run 1 kept in `T092_data/gates_run1_wirefold`).

## 1. FC move: where and why
- Side chosen: **-y (left)**, centre y = -75 mm (board y -97.5 to -52.5, x 32-62 unchanged, 45 mm along y, hard-mounted on four R2 bosses, D-186 kept; foam tape pads and M2 screws as before). The model node s+0.075 (T-091) is symmetric in y.
- Why -y, not +y: (a) enclosure: the GPS board (y +27.5 to +52.5) is on +y, so a +y FC needs a tunnel past the GPS (no hood over the GPS: sky view); -y needs one annex of the cover; (b) the RX UART (E-HRN-09), the airspeed I2C (E-HRN-11) and the left servo lead go to -y anyway (shorter); (c) GPS / compass clearance: FC is 80 mm from the GPS; no current-carrying part moves. Cost: lateral CG moves from -1.66 to **-3.32 mm** (limit 5 mm, A-P4, CL-A-CG-LATERAL +34 % margin); +y would have kept it near -0.4 mm (EST, mirror of the measured shift; not computed by cad_mass) [R4]; the 1.68 mm left is the allowance for as-built asymmetry (pack y-trim, wire routing, the 0.6 g splice). Margin left 1.68 mm. Tell the owner: a +y mounting gives better lateral balance and a tunnel; the choice is reversible by mirroring FC_YC and the annex.
- D-186 (BOARD s3 / SITL-FLIGHT follow-up 2) only requires the FC on the wing, hard-mounted, not on the cage hub; "wing spar centre" appears in an A.param comment (l.102, "REQUIRES the flight controller on the wing spar centre (C4's IMU node)"): that comment is now superseded by D-239 (spar station 75 mm; not edited, listed in s6).
- 75 mm is feasible (checked: bosses at y -62.5 / -87.5 are above the skin, the left centre bulkhead face at |y| 60-60.5 is under the skin; no part clash). A node at exactly 75 mm exists in the T-091 FE model, so no other station was needed (T091_data/t091_nodes.py not re-run).
- CAD (`cad/amodel/electrical.py`; pre / post copies in `T092_data/pre`, `post`): `FC_YC = -0.075` moves holes, bosses, tape pads, PCB, pads, screws, nuts; GPS and I2C pads swap sides (EST layout; the pad positions are EST, Holybro gives names only); **FC annex of the bay cover AVN-008** (x 22.5-72.2, y -26.5 to -99.0, roof 45 mm as the cover, 0.5 mm vacuum-formed wall EST design value; the -y end wall of the main cover is open over the annex). Cover mass 9.01 -> 14.61 g (`printed_mass.json`, +5.6 g from `cover_mass_g()`).
- Cable runs (all stay under the cover or in a core groove; routes in `esc_path()`, `gps_path()`, `servo_lead_pts()`, `uart_path()`, `i2c_path()`):
  - ESC signal bundle E-HRN-06: ESC pad forward at 24 mm, up to the lane x 68.5 / z 41.5, along y under the roof to y -75, down onto the FC ESC pad (149 mm, was 41 mm).
  - Servo lead R (S5, FC pad y -70): aft to x 64 at pad height, along y across the bay under the phase bundles to its existing slit at y +24 (347 mm, was 273 mm). Servo lead L (S6, pad y -80): straight down a new 8 mm slit at x 64 / y -80 between the bosses into the existing groove outboard (198 mm, was 273 mm); its groove no longer starts at |y| 19.5 and no longer crosses the left centre bulkhead (that bulkhead slot removed). Ribbon pattern of the L lead rotated 90 deg (`SRV_TH0`) so its strand pattern in the end run equals T-084 (frame-transport artefact; exposed length stays equal).
  - GPS E-HRN-10: up the existing cover slot at y +24.75, across at 40.5 mm (x 42.5) to the pad at y -80 (162 mm). RX UART E-HRN-09 (153 mm) and I2C E-HRN-11 (650 mm): same lanes as before, longer first run.
- Wire inventory (strand-metres, all strands): ARM 3.496, RACE 1.554, GROOVE 3.312 (was 3.480), COVER 4.227 (was 2.698), **EXPOSED 0.597 (was 0.597)**. No new exposed length; the remaining exposed lengths are unchanged (last 12 mm of each servo lead, 3 mm GPS plug end, pack leads, phase-lead ends). Min strand-pair clearance of different wires > 0.3 mm (`wwd.py`, closest E-HRN-04 / -10 0.32 mm, unchanged geometry at y +24.75).
- Servo lead length: servo stock lead length is "—" (not published); the old design assumed it reaches the old pad. The right lead needs about 74 mm more: 0.6 g extension (3 x 26 AWG + a splice) added to HRN-001; the left lead is cut shorter (mass not subtracted). **Check on the real servo (BUILD D0 text updated).**
- Build steps: `cad/a_build_steps.py` (D0 slit positions; stale x 83 -> 64; E2 FC position and bulkhead note; E3 y ranges; E3b lead routes; E7 annex and mass), `cad/a_assembly_plan.py` (D0, E3b, E7 text), `make_build_guide_a.py` run -> `BUILD-GUIDE-A.md`. Parts list: `cad/parts_links_a.py` (AVN-002, AVN-008 notes); `AVN-002` / `AVN-008` descriptions in electrical.py.
- ArduPilot params (`A.param` l.268-): `INS_POS1_X -0.0250`, `INS_POS1_Y -0.0717`, `INS_POS1_Z -0.0111` (m): body x forward = -x CAD, y right = +y CAD, z down = -z CAD, relative to the CAD CG (22.05 / -3.32 / 6.56 mm) and the FC board centre (x 47.0, y -75.0, z 17.68 mm). **IMU chip position on the board "—"** (EST +-10 mm); **the ArduPilot parameter definition (reference point = CG) was not re-read this session (the doc page is truncated in the fetch): verify before flight.** GPS / compass offsets stay "—".

## 2. Mass / CG / SM vs T-084 (cad_mass, mission_gate --o4b)
| | T-084 | T-092 |
|---|---|---|
| basic as drawn | 1,633.0 g | **1,641.0 g** (+8.0: annex +5.6, ESC / GPS / RX ribbons +, servo extension +0.6) |
| CAD CG x | 21.95 mm | 22.05 mm |
| SM at CAD CG (NP 40.7) | 7.65 % | 7.61 % |
| CG y | -1.66 mm | -3.32 mm (limit 5) |
| CG z | 6.48 mm | 6.56 mm |
| Ixx / Iyy / Izz kg m2 | 0.08802 / 0.03508 / 0.09836 | 0.08805 / 0.03509 / 0.09839 |
| tallied (T-084 basis +7.0 g cups, EST) | 1,640.0 g, CG 23.13, SM 7.17 % | 1,648.0 g, CG about **23.22 mm**, SM about **7.13 %** (my hand tally with the T-084 cup arm 298 mm, not a rerun of MASS-GATE s15); predicted: the claim value CL-A-MASS-PRED 1.881 kg (run_all, params-A.json: 1.64098 x 1.1174 + 0.048) is the figure quoted; my 1.888 kg hand tally is superseded [R4] |
The 1.5 kg gate stays missed (D-232 style, physics checks govern); CL-A-CG, CL-A-SM, CL-A-CG-LATERAL pass in run_all.

## 3. Claims text
- `proofs/claims_a0_base.py` l.149 (T-A-TAP procedure): stale "Cage pitch mode 12-16 Hz, roll 21-43 Hz" replaced by the T-089 / T-091 modes (16-18 / 26.8-29.7 / 42-47 Hz; 94.6-108.7 Hz D-185 mode) plus the FC-site note.
- `proofs/claims_a2_struct.py` CL-A-VIB-GM and CL-A-VIB-GM-SHIFT `how`: sentence added: design has the FC 75 mm off centre (-y); model pitch GM there 2.52-4.00 (T-091); claim still evaluates the FC-at-centre model (P:sim.gm_nominal) and stays FAIL; benefit credited only after T-A-TAP / tether (D-239). No claim value changed; `fu_cage.py` not edited.

## 4. R15 rib tube (T-088): no switch
Easy Composites US page https://www.easycomposites.us/25mm-23mm-woven-finish-carbon-fiber-tube (read 2026-11-23 via fetch, no saved capture): 25 x 23 mm woven-finish roll-wrapped prepreg tube, wall 1 mm, **113.1 g/m**, **$59.05 per 1 m** (more than the Carbonwebshop $50.09), "more than 50 units" in stock, handling surcharge because the packed length exceeds 1 m, US shipping "from the cart calculator". I did not run the guest cart (the fetch tool cannot add to a cart; no browser session used), so shipping is "—". Landed price is therefore at least $59.05 + "—" vs $50.09 + $25 EST = $75.09: switch only if the cart shows < $16 shipping. Spec is the same (25/23, 1 mm, roll-wrapped). The stock risk is not a reason on this evidence (Carbonwebshop line is a quote). **BOM-A.csv / bom_a.py unchanged**; `python -I bom_a.py`: total $1,939.17 (cap $2,000). No ZIP used or written.

## 5. Evidence files
`T092_data/`: `pre/`, `post/` (changed files), `gates/` (outputs, summary), `gates_run1_wirefold/`, `run_gates_t092.sh`, `cad_mass_stdout.txt`, `mission_gate_stdout.txt`, `patch1-3.py`, `k3.py` (fold check), `wwd.py` (wire-wire distance). Changed repo files: `cad/amodel/electrical.py`, `cad/amodel/printed_mass.json`, `cad/a_build_steps.py`, `cad/a_assembly_plan.py`, `cad/parts_links_a.py`, `A.param`, `proofs/claims_a0_base.py`, `proofs/claims_a2_struct.py`, regenerated: `BUILD-GUIDE-A.md`, `cad/out/*`, `cad/model/*/interfaces.json`, `drawings/out/*`, `sitl/cad_mass.json`, `proofs/out/*`.

## 6. Open items / not done
1. The FC benefit is a beam-FE result at node s+0.075 (symmetric +y); the -y side, real mode shape, IMU chip offset and the FC mount flexibility are unmeasured: T-A-TAP / tether (D-239). Pitch GM 2.52-4.00 is the model number, not credited.
2. [R4] A.param l.102 reworded by the conductor (model result, unconfirmed); electrical.py AVN-007 text fixed; a grep found no other "spar centre" FC text in REQUIREMENTS / MISSION.
3. INS_POS reference point to verify (s1); servo lead stock length "—".
4. Lateral CG -3.32 mm uses 66 % of the 5 mm limit; pack y-trim or mirroring the FC to +y recovers it.
5. R15 Easy Composites shipping not read: moved to T-093 (the cart needs a delivery address, which only Dillon can enter) [R4].
6. `proofs` explain text (`explain_a.py`) not touched.

## 7. Proposed CHANGE-LOG entry
| **D-240 T-092: FC 75 mm off centre implemented in the CAD (2026-11-23)** | Implements D-239: Kakute H743-Wing hard-mounted at y -75 mm (left), bosses, pads, screws moved; cover AVN-008 gets a FC annex (x 22.5-72.2, y -26.5 to -99, +5.6 g EST); ESC bundle, both servo leads, GPS, RX and I2C routes re-run inside the cover / grooves, exposed strand length 0.597 m unchanged, no open wire ends, folds 0 (one fake kink fixed by a 6 mm radius); left servo slit at y -80, right lead +74 mm (+0.6 g splice EST). Side -y chosen for a single enclosed annex and shorter RX / I2C / left-servo leads; cost lateral CG -1.66 -> -3.32 mm (limit 5). Mass 1,633.0 -> 1,641.0 g, CG 21.95 -> 22.05 mm, SM 7.65 -> 7.61 % (tallied CG about 23.22, SM about 7.13 %). INS_POS1 -0.0250 / -0.0717 / -0.0111 m (IMU chip offset "—"). Gates: collide pose 21 + 18 linkage poses PASS, a_assembly 0 blocked, build_a only the mass gate, run_all the same 12 STRICT FAILs; claims text notes the FC benefit is credited only after T-A-TAP / tether. R15: Easy Composites US $59.05 / m, 113.1 g/m, shipping not read, no change (Carbonwebshop kept). Ladder: rung 3 (rearrange). | `redesign/qp/A/mechanism/out/T092_report.md`; T-092 |
