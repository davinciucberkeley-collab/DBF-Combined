# Change requests from A5 (CAD lead)

Round 1 (CR-A5-01 … 09) status after `params/CHANGE-LOG.md` (A1-R2):

| # | To | Status | Note |
|---|---|---|---|
| CR-A5-01 | A1 | closed (D-03) | spar z 0.0066 m; `CL-A5-SPAR-COVER` 4.3 mm (≥ 2 mm) on the S5010 |
| CR-A5-02 | B2 | closed | `subsystems/wing/s5010.dat` copied from `team/B2/airfoils/` (byte-identical, UIUC URL and checked date in its header line); D1 owns the copy |
| CR-A5-03 | A3, B3, A1 | superseded (D-04, D-08, D-17) | layout CG now 0.053 m with the pack centred; see CR-A5-11 |
| CR-A5-04 | A4 | open (CR-A1-18) | SCHEMA frame text, 9xx reserved |
| CR-A5-05 | A1 | closed (D-15) | `fins.board_t_m` read by `k09kit.board_t()` and `CALC-A5-ELEVON-GAPS` |
| CR-A5-06 | E1 | open | prop hub thickness, shaft + adapter length |
| CR-A5-07 | designers | open, endorsed | start from `fusion/skeleton/<key>/` (now R1) |
| CR-A5-08 | team lead | open (CR-A1-21) | the skeleton is at R1 now: BuildAll can be run |
| CR-A5-09 | J3 | open | `k09kit.hover_pose()` (lift is now 0.365 m) |

Round 2 (CR-A1-12 and CR-A4-11 work):

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-A5-10 | A4 | (a) Add the optional edge key `"stowed": true` to `interfaces/SCHEMA.md`: a transport edge whose flight part is removed for transport (props in the tray, pitot boom); `check.py` does not touch-check it. Set it on `E-TRN-08…11`. (b) Re-point the fins register to R1: half-fins `FIN-001-UR/UL/LR/LL` (station codes, README instance rule), through-core block `FIN-004-L/R` replacing the saddle (edges to tube, spar and core: bonded, not clamped), fin-to-tube clip set `FIN-005-L/R`; mounts at x 0.034 m, not −0.10. (c) Answer to CR-A4-11 is below. | CR-A4-11; the R0 register (saddle, 0.18 m offset, face at −0.10) no longer matches `params.json` |
| CR-A5-11 | A1 (B3, D2, A3 informed) | D-17 input: the R1 skeleton puts the layout CG at **0.053 m** (16.6 % c) with the pack centred, 4 mm aft of the 0.049 aft limit; the CG target needs the pack centre at −0.041 m, a **36 mm forward shift, beyond D2's ±30 mm slide**. A3's bottom-up 0.051 / −29 mm differs mainly by the harness route (CR-A5-12). If B3's re-derived aft limit stays < 0.053, the pod move to −0.125 (D-17) is needed with an aft wire channel. | `CL-A5-LAYOUT-CG-X` `FAIL` (−8 %), `CL-A5-PACK-SHIFT` −0.036 m; closed form and CAD roll-up agree to 0.0 mm |
| CR-A5-12 | F2, D1 (A3 informed) | Decide the pod → fin wire channel (CR-A4-05) with its CG cost: the skeleton route (channel 14 mm aft of the spar, x 0.105, then along the tube) puts the 105 g harness at x 0.072 m; A3 carries it at ~0.03 m. Aft channel = +2 mm aircraft CG. A route through the through-core block or ahead of the spar (13 mm gap between tube and spar faces) recovers it. Model the bundles with `k9.bundle()`. | harness is the largest placement difference between A3 and the CAD |
| CR-A5-13 | E1 | `CL-E1-HOVER-T` lists parts `PRP-901…904` (old skeleton ids, now `PRP-901-UR`… in the skeleton). Point it at the register ids `PRP-001-UR/UL/LR/LL`. | `build_graph.py` warns "part not in any interfaces.json" |
| CR-A5-14 | D7 | Model the box around the aircraft in the aircraft frame (`k9.box_frame()`, centre `DX-BOX`; skeleton `transport/`), every part `"flight": false`, props with `"stowed": true` edges to the tray. `check.py` touch-checks the cradle edges and warns if a cradle or wall overlaps a flight part. Your current module passes; confirm the cradle station (skeleton y ±0.20 m, C1's assumption behind the 70 mm foam, D-22). | CR-A4-11a, CR-A1-19 |
| CR-A5-15 | A1 | `params.json#fins.pieces_per_fin` note names half-fin ids `FIN-nnn-LU/LD/RU/RD`; the README instance rule allows `UR UL LR LL L R`. Use the station codes (`FIN-001-UR` = upper right) in the note. | one id rule |

Round 2 status after `params/CHANGE-LOG.md` (A1-R3):

| # | Status | Note |
|---|---|---|
| CR-A5-10 | closed (D-46) | A4's `merge_check.py` change is in; A5 re-ran `fusion/tests` (27 OK) and `check.py --skeleton --strict` (PASS) |
| CR-A5-11 | closed (D-24) | range 0.050–0.055; R3 layout CG 0.0521 m is inside (see CR-A5-17) |
| CR-A5-12 | forwarded to F2, D1 | open |
| CR-A5-13 | forwarded to E1 | open |
| CR-A5-14 | forwarded to D7 (D-31) | D7's module passes `check.py` (0 errors, 0 warnings) |
| CR-A5-15 | closed (D-26) | station codes |
| CR-D3-14, CR-D3-21, CR-D5-02 (to A5) | done | skeleton at R3, `DX-COLLAR-*`, `DX-ANCHOR-*`, `DX-FOOT-*` at the pad contact, `DP-GROUND` 0.368, hover lift 0.368, box 0.54 |

Round 3 (R3 skeleton and datums):

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-A5-16 | A1 | Promote the four shared R3 stations to `params.json` so they stop living only in designer files: the brace collar end (x 0.045, \|y\| 0.3023, \|z\| 0.1535), the brace anchor (\|y\| 0.242 on the spar line), the foot pad contact \|z\| 0.218 (D5 publishes `CL-D5-CONTACT-Z`), the motor plate face x 0.0309 (D-28 already quotes it). Until then `k09kit` reads `subsystems/fins/params.json#fin_detail` and `subsystems/landing/params.json#landing.pad`, and `check.py` warns when DATUMS.md goes stale against them. | D5, D7, C4, C5 and `CALC-A1-TIPOVER` depend on these numbers; the datum rule says a datum moves only when `params.json` changes |
| CR-A5-17 | A1, A3 (B3 informed) | The allocation-based layout CG is **0.0521 m** (16.3 % c): `CL-A5-LAYOUT-CG-X` +5 % to the aft limit, `CL-A5-LAYOUT-CG-X-FWD` +4 % to the forward limit, range use 0.15; the pack sits at the D-24 station x −0.001 and the target needs it at +0.001 (+2 mm). This does not close `R-CG-RANGE`: A3's bottom-up 0.0556 m (`CL-A3-CG-X-RANGE` FAIL) carries the designers' real masses (fins 417 / 408 g, harness 112.6 / 105 g) and positions (feet at x 0.33, braces, pod handle). The skeleton moves the pack with D2's `pack_aft_face_m` as soon as D-24 is changed (A3's CR-A3-15 asks for −0.012). | lets A1 see that the shift is from mass growth aft of the CG, not from the layout |
| CR-A5-18 | A1 | Two stale notes: `wing.elevon.inboard_y_m` says "20 mm clear of the pod (y = 0.05)"; the pod is 0.14 m wide since D-25, so the panel end is 0 mm outboard of the pod side. The gap is still real because the pod ends at x 0.095, 155 mm ahead of the hinge (`CALC-A5-ELEVON-GAPS` now measures the corner distance). And `DP-MOUNT` is the tube front face (0.034), not the motor face (0.0309, D-28). | a designer reading the note would widen the centre strip for nothing |
| CR-A5-19 | D3, D5 | The datums read these keys of yours; rename or remove them only with a heads-up to A5: D3 `fin_detail.bond_gap_m`, `mount.grip_m`, `mount.collar_wall_m`, `mount.face_ahead_m`, `station_collar.gap_m`, `station_collar.ear_h_m`, `station_collar.ring_wall_m`, `station_collar.ear_len_m`, `brace.anchor_y_m`, `anchor.proud_m`; D5 `landing.pad.z_outer_m`, `landing.pad.edge_r_m`. `tests/test_framework.py` checks `DX-COLLAR`, `DX-ANCHOR` and `DP-MOTOR-FACE` against D3's `fins.geometry()` (`brace_ends`, `x_face`), so keep those names too. | a renamed key falls back to the R3 default without warning in the skeleton |

## Answer to CR-A4-11 (A4)

| Item | Answer | Where |
|---|---|---|
| (a) transport touch checks | Intended for cradles and straps: D7 models the box around the aircraft in the aircraft frame (`DX-BOX`), so a cradle-to-wing touch is a real fit check. Not intended for flight parts removed for transport: those edges carry `"stowed": true` and are not touch-checked. New `transport` check: a box wall, cradle or tray body overlapping a flight part it has no edge with is a WARN (pressed, or does not fit). Ground parts are now also left out of `ctx.rollup()`. | `fusion/check.py`, `fusionkit.Context.rollup`, `STANDARDS.md` §5–6, tests `test_transport_stowed_and_pressed` |
| (b) harness bundle bodies | Yes, every modelled part needs a body. `k09kit.bundle(part, legs, dia)` builds axis-aligned cylinder legs along the route; the skeleton harness uses it. | `fusion/k09kit.py`, `skeleton/harness/` |
| (c) thermal edges | `ctx.contact` is the right registration (thermal allows rigid or contact), and the parts must touch (bbox ≤ 2 mm). The skeleton carries `E-FIN-923…926` motor → mount `CT-THERMAL-PAD` beside the bolted edge. | `STANDARDS.md` §6, test `test_thermal_contact_and_bundle` |

## Round 4: integration check over the ten delivered modules (2026-11-09)

Requests to A5 answered this round (framework changes in `redesign/fusion/`, 31 tests OK, skeleton and examples
`--strict` PASS):

| # | From | Status | What changed |
|---|---|---|---|
| CR-D1-01, CR-F2-09, CR-A4-32 | D1, F2, A4 | done | `check.py` floating uses `merge_check.carried()` and load-bearing edges only: `WNG-020` and `HRN-001/002-L/R` no longer float (3 ERRORs gone). Test `test_carried_items_do_not_float` |
| CR-D7-19 | D7 | done (D7 to apply, CR-A5-22) | transport edges may list `"also_contacts"`; each listed part must share a load-bearing edge with the flight partner, else ERROR. Test `test_transport_also_contacts`; trial on the real `subsystems/` clears both `WNG-003` WARNs |
| CR-E1-31a | E1 | done, `UNVERIFIED-IN-FUSION` | `fusion_backend.joint()` makes an as-built joint whenever a part is rotated (rigid: no geometry; revolute/slider: axis point in the unrotated partner). Fake-adsk run on the real subsystems: 37 joints, 0 warnings. Test `test_rotated_parts_get_as_built_joints` |
| CR-E1-31b | E1 | done (E1 to apply, CR-A5-21) | `Keepout` takes a vector axis and tests the tilted cylinder exactly (alternating projections, agrees with the axis-aligned test on 500 random boxes); `k9.prop_keepout(..., rotate=, blade_half=)`; `check.py` tests keep-outs against each body's box, not the component box. Trial with the 7° cant and E1's 10 mm half: 0 hits (the component box of the canted mount `FIN-003` over-reported 4 hits). Test `test_tilted_keepout` |
| CR-E1-16 (A5 part) | E1 | done | the hub half-thickness is E1's number: pass `blade_half` (default stays 8 mm) |

New requests:

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-A5-20 | A1 (A3, B3, D2, F1 informed) | **Assembled CG x 0.0577 m is 2.7 mm aft of the 0.055 aft limit** (`CL-A5-ASSY-CG-X` FAIL, range use 2.06; A3's roll-up gives the same 0.0577, and B3's latest aft limit is 0.0549). It is 5.5 mm aft of the allocation layout (0.0521). Shares (`INTEGRATION.md`): power +3.2 mm (F1's boxes sit at mean x +0.017, the layout had them at the pod nose), avionics +1.4 (43 g lighter forward: the FC power board moved to power), propulsion +1.2 (motor stack 6 mm further aft), mechanisms +1.1 (+17 g at x 0.22), pod +0.4; wing −0.8, fins −0.6, landing −0.4. Decide the lever: move the power boxes forward (79 g by 0.1 m ≈ −3.4 mm), the pod group (A3: −14.7 mm), or ballast | `ERROR graph:cg` in `check.py` and `merge_check.py`; the only configuration-level error |
| CR-A5-21 | E1 | In `propulsion.py` call `k9.prop_keepout(ctx, ..., rotate=rot, blade_half=0.010)` (your −6 / +10 mm about the mid-plane with coning). Today the keep-out is the untilted x cylinder, so the 7° cant is not checked | trial: 0 parts in the canted keep-outs with the per-body test |
| CR-A5-22 | D7 | Add `"also_contacts": ["WNG-003"]` to `E-TRN-06` and `E-TRN-07` (saddle on the tape skin) | clears the two 8 mm `transport` WARNs; validated |
| CR-A5-23 | A4 | Document the optional edge key `also_contacts` in `interfaces/SCHEMA.md` next to `stowed` (transport edges only; parts bonded to the flight partner by a load-bearing edge) | `check.py` reads it; `merge_check.py` can ignore it |
| CR-A5-24 | F2 | Re-run `team/F2/harness.py`: every id in `edges-pending.json#waiting_for` is declared now (`WNG-001`, `AVN-001…004`, `MEC-001-L/R`, `PWR-001…005`), so the 21 pending edges move into `interfaces.json` and `fusion/harness.py` must register them | 16 `unconnected` + 8 `unpowered` WARNs: no motor, servo or FC has a power path in the graph |
| CR-A5-25 | D5 | Re-run `team/D5/make_interfaces.py`: `WNG-001` is declared, so `landing.py` builds `GER-007-R/L` and registers `E-GER-21/22`, but `interfaces.json` still has the caps `PROPOSED` and no edges | 4 ERRORs (2 register, 2 floating) + 4 WARNs |
| CR-A5-26 | D3 / F3 | D3: acknowledge `E-PWR-11…14` (ESC caps taped on `FIN-001-<st>`). F3: acknowledge `E-TRN-21` (pitot boom stowed in the tray) | 5 `one-sided` WARNs |
| CR-A5-27 | F2, D2 | Declared CG vs CAD centroid differs by > 10 mm: `HRN-002-R/L` 22.9 mm (declared y 0.260, bundle bodies 0.238), `POD-008` 29.9 mm (declared x −0.052, body −0.082), `POD-003` 10.5 mm. Recompute `cg_xyz_m` from the bodies or fix the bodies | aircraft CG effect ≤ 0.2 mm each; a declared CG must describe the modelled part |
| CR-A5-28 | A1 (A3 informed) | Re-balance the allocations to where the mass went: avionics 36.5 / 80 g (the 28 g FC power board is `PWR-003`), power 638 / 620, harness 122.5 / 105, mechanisms 82 / 65, fins 417 / 408, pod 128 / 122. Sum 2 330 g vs 2 324 allocated | five `graph:mass` WARNs; the total is inside the 2 600 g gate (`CL-A5-ASSY-MASS` +10 %) |
| CR-A5-29 | C3 (D2 informed) | `team/C3/pod_structures.py` fails in `build_graph.py`: `KeyError: 'stop_wall_h_m'` (line 33) in all eight `CALC-C3-*`; `subsystems/pod/params.json` (D2) no longer has any `stop*` key; C3 re-points or D2 restores it | found while re-running the proof graph |

Round 4 (2026-11-10, A5 action items: keep-out false positives, stale DATUMS.md, layout CG drift):

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-E1-45 | E1 | **done** (framework). `check.py` now tests each body's convex hull (revolves as a circumscribed 24-gon) after the box pre-filter, and for a `k9.prop_keepout` zone reports a hit only when the hull is closer than `clearance` to the swept blade volume, with that distance. `k9.prop_keepout(..., fwd=, aft=)` takes your asymmetric envelope (E1 already calls it with 0.010 / 0.006). Tests `test_hull_keepout`, `test_prop_keepout_fwd_aft` | Box artefacts cleared: `FIN-009-*` braces (9.9 mm outside the zone), `WNG-001` core (≥ 7.1 mm), `WNG-003` skin and doubler (≥ 6.0 mm), and with the fwd/aft envelope `FIN-004`/`FIN-006` (≥ 27 mm from the blades) |
| CR-A5-30 | A1 (D3, E1, B4 informed) | Decide CR-D3-26 for the one real hit left: **`FIN-002-R/L` motor tube is 21.0 mm from the swept blade volume of all four props, against `requirements.prop_clearance_min_m` 0.025** (exact hull distance; E1's sampled `CL-E1-TIP-GAP-TUBE` 21.2 mm agrees). It is not behind the hub: the nearest point is near the blade tip where the 7° cant swings the disc aft over the tube. Options: prop plane ≥ 4 mm further forward (`face_ahead_m`), or a reasoned lower structural clearance for a fixed CF tube | `check.py` on `subsystems/`: 4 keep-out ERRORs, nothing else; `CL-A5-ASSY-CHECK-ERRORS` 4. A5 does not exempt it |
| CR-A5-31 | A2 (A1, A3, B3 informed) | `CL-A5-LAYOUT-CG-X` no longer verifies `R-CG-RANGE` and `CL-A5-LAYOUT-CG-X-FWD` is withdrawn. Use **`CL-A5-ASSY-CG-X` (aft), new `CL-A5-ASSY-CG-X-FWD` (forward) and `CL-A5-ASSY-CG-X-RANGE-USE`** on the delivered CAD, next to A3's `CL-A3-CG-X-RANGE`. VERIFICATION-MATRIX and CR-A2-19 still quote the old 0.0531 m against 0.049 m | With the D-47 bay (pack −0.022) and D-48 allocations the allocation layout sits at 0.0466 m, 4.3 mm ahead of the D-60 forward limit 0.0509, while the delivered aircraft is at 0.0521 m (range use 0.37). The 5.5 mm difference is where the allocation lumps sit, not the aircraft |
