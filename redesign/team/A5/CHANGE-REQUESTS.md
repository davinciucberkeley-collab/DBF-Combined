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

## Answer to CR-A4-11 (A4)

| Item | Answer | Where |
|---|---|---|
| (a) transport touch checks | Intended for cradles and straps: D7 models the box around the aircraft in the aircraft frame (`DX-BOX`), so a cradle-to-wing touch is a real fit check. Not intended for flight parts removed for transport: those edges carry `"stowed": true` and are not touch-checked. New `transport` check: a box wall, cradle or tray body overlapping a flight part it has no edge with is a WARN (pressed, or does not fit). Ground parts are now also left out of `ctx.rollup()`. | `fusion/check.py`, `fusionkit.Context.rollup`, `STANDARDS.md` §5–6, tests `test_transport_stowed_and_pressed` |
| (b) harness bundle bodies | Yes, every modelled part needs a body. `k09kit.bundle(part, legs, dia)` builds axis-aligned cylinder legs along the route; the skeleton harness uses it. | `fusion/k09kit.py`, `skeleton/harness/` |
| (c) thermal edges | `ctx.contact` is the right registration (thermal allows rigid or contact), and the parts must touch (bbox ≤ 2 mm). The skeleton carries `E-FIN-923…926` motor → mount `CT-THERMAL-PAD` beside the bolted edge. | `STANDARDS.md` §6, test `test_thermal_contact_and_bundle` |
