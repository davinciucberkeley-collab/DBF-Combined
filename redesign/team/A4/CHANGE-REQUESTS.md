# Change requests from A4 (configuration / interface manager)

Edge and part ids refer to `redesign/team/A4/INTERFACE-PLAN.md`. Answer by changing your `interfaces.json` (or the
file named) and noting the CR id; A4 updates the plan and re-runs `interface_plan.py --compare`.

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-A4-01 | A1 | README joint table: (a) elevon hinge owner → `wing` (declares; D6 designs), because an owner must hold one side; (b) ESC power leads → `harness` only, `power` owns the boxes (pack, disconnect, power module, PDB, UBEC); (c) add the rule "electrical `part_a` = supply side". | 4 hinge edges `E-WNG-04…07` would warn `owner`; leads `E-HRN-13…16` are listed under two owners today |
| CR-A4-02 | A1, D5, C5 | Wing TE ground clearance in stance equals the foot height: TE at x = 0.300 m, foot tips at 0.310 m (`P:cg.foot_height_m` = 0.01 m). A crushed foot or 10–20 mm of grass `EST` puts the whole TE on the ground. Set foot height ≥ crush stroke + grass allowance, then re-run `CL-A1-TIPOVER` and `CL-A1-BOX-FIT` (feet lengthen the 0.445 m dimension; that axis has 55 mm slack, height 10 mm). | OI-05; landing damage is the recurring mode (`CONFIGURATION.md`) |
| CR-A4-03 | D3, D1, C4 | Decide (a) fin through a core slot vs upper/lower half-fins and the fin-tube junction (P25); (b) how the saddle carries the 0.18 m tube-to-spar offset and the core cut-out that exposes the spar at y = ±0.32 m. Tell A4 if parts split (ids `FIN-001-LU/LD…`). | OI-01, OI-02; `E-FIN-01…12` |
| CR-A4-04 | D6, D3, B3 | The inter-panel link crosses the fin at y = 0.32 m on the hinge line (panels end at 0.30 / 0.34 m). Size a fin slot for ±25° sweep, or drop the inboard panels (CR-A1-06) and retire `WNG-011-*`, `MEC-005-*`, `E-MEC-13…16`. | OI-03 |
| CR-A4-05 | F2, D1 | Wire channel pod → fin root per side: 2 ESC power, 2 ESC signal, 1 servo lead. Give its x position (clear of the spar slot at x = 0.080 m) and cross-section before D1 freezes the core. | OI-04; `E-HRN-02…05` |
| CR-A4-06 | E1, E3 | E1: X3108S bolt pattern, max screw length clear of windings, prop-adapter type and thread, motor lead length (decides a phase extension). E3: motor base temperature at hover on a printed mount (PETG HDT ~70 °C `EST`), ESC cooling on a fin pad in the prop wash. | OI-06; `E-FIN-17…20`, `E-FIN-25…32`, `E-PRP-01…08` |
| CR-A4-07 | B4, F3, D2 | Pitot at the pod nose (`POD-006`, baseline) or wing LE at y ≈ 0.15 m (30 mm from the 0.18 m disc edge). If LE, A4 re-points `E-AVN-05` to `WNG-001` and retires `POD-006`. | OI-07 |
| CR-A4-08 | F3, F5 | Confirm the MS5525 I2C address against the chosen board's barometer (both 0x76 `UNVERIFIED`); minimum compass distance from power leads, PDB and UBEC; antenna placement clear of the CF spar and tubes; telemetry through ELRS or a separate radio. | OI-08, OI-10; `E-HRN-30…32`, `E-AVN-02/03` |
| CR-A4-09 | F1 | Choose XT60 or AS150U for `E-HRN-10` (≥ 1.25 × 24 A = 30 A continuous, `R-DISCONNECT`); say whether `PWR-005` UBEC is needed or the FC's servo BEC carries two servos at stall. | OI-09 |
| CR-A4-10 | C6, C4 | Joint stacks for the 19 fastened edges (`E-FIN-17…20`, `E-PRP-01…08`, `E-PWR-03`, `E-AVN-01`, `E-AVN-04`, `E-MEC-03…06`) and the 8 clamps (`E-FIN-07/08/10/11`, `E-FIN-13…16`, closing screws + slip load). Few sizes: M2, M3. | P24; merge_check fails without them |
| CR-A4-11 | A5 | `check.py`: (a) transport parts are `flight: false` but their edges to the wing and props are still touch-checked, so D7 must model the box at the aircraft's transport position; confirm that is intended; (b) harness bundle parts `HRN-001`, `HRN-002-L/R` need bodies; (c) thermal edges `E-FIN-29…32` register as `ctx.contact`. | framework behaviour the designers rely on |
| CR-A4-12 | F4 | Read motor and servo ports from `signal.fc_port` on `E-HRN-24…29` instead of a second table; publish the station → motor number → rotation map back to E1/F2. | one source for the output map |
| CR-A4-13 | A2 | Give P24 (design method: every part connected and on an interface) an `R-…` id so `CL-A4-PLAN-CONNECTED` and `CL-A4-PLAN-POWERED` verify it; today only `CL-A4-FIELD-DISCONNECTS` verifies a requirement (`R-TRANSPORT`). | traceability |
| CR-A4-14 | all designers | Declare your parts and edges with the ids, owners and acknowledgements in the register; keep ids, retire unused ones, explain any type change in `notes`. | `--compare` matches by id first, then by part pair |

## Round 1 dispositions (from `params/CHANGE-LOG.md`)

| CR | Result |
|---|---|
| CR-A4-01 | accepted as D-20; applied to the plan and `interfaces/SCHEMA.md` in A4-R2 (CR-A1-18) |
| CR-A4-02 | accepted (D-11 feet 45 mm, D-16 box 0.50 m); OI-05 stays open for the 5 mm left after a full crush |
| CR-A4-03 | closed by D-04 (half-fins, tube through the core, through-core block); ids split in A4-R2 |
| CR-A4-07 | accepted (D-15, pitot on the pod nose); OI-07 closed, OI-12 opened for the plug-in boom |
| CR-A4-04, 05, 06, 08, 09, 11, 12, 14 | forwarded by A1 to the named roles; still open |
| CR-A4-10 | forwarded; numbers changed in A4-R2, see CR-A4-20 |
| CR-A4-13 | closed (A2 `R-NO-FLOATING`) |

## Round 2 (plan A4-R2, 2026-11-09)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-A4-15 | A1 | (a) Assign A4 the four queued shared-tooling changes in `redesign/interfaces/`: add the 19 plan connection types to `connection_types.json`; in `merge_check.py` exempt `harness`-owned electrical edges from the `owner` warning (D-20), skip non-structural types in the floating check, and follow power wires `part_a` → `part_b` without `signal_only` leads. (b) In `params.json#fins.pieces_per_fin` change the note "ids FIN-nnn-LU/LD/RU/RD" to `FIN-001-UR/UL/LR/LL` (station suffixes, CR-A3-09 rule). | (a) the 23 harness wires each raise a `owner` WARN, so `merge_check.py --strict` cannot pass at a gate; `fusion/check.py`, `build_all.py` and the Blender backend import this module, so A4 does not change it unassigned. (b) `LU/LD/RU/RD` breaks the one suffix family rule that `mass_rollup.py` relies on |
| CR-A4-16 | B4 | Replace the retired ids `FIN-001-L`, `FIN-001-R` in `props.py` / `claims.json` (`CL-B4-DOWNLOAD`, `-DOWNLOAD-HIGH`, `-SWIRL-FIN`, `-SWIRL-FIN-M`, `-TUBE-LOAD`, `-WING-GAP` and others) with the half-fins `FIN-001-UR/UL/LR/LL`. | `build_graph.py` warns "part not in any interfaces.json" today and will keep warning once `fins` declares the half-fins |
| CR-A4-17 | A3 (copy D6) | `mass_model.csv`: (a) `FIN-E04` (through-core block, 2 × 20 g) already matches `FIN-004-L/R`; no change. (b) `MEC-E02` counts 4 horns; the plan has one horn per side on the inboard panel (`MEC-004-L/R`), the outboard panel being driven by the link `MEC-005`. If D6 adds outboard horns they are `MEC-006-L/R`, not a third suffix. (c) `FIN-E05` (2 × 30 g) becomes one clip set per half-fin (`FIN-005-<station>`, qty 4 × 15 g) so the line maps onto four instance nodes. | ids and quantities must match the instance nodes the designers will declare, or `mass_rollup.py` cannot map them |
| CR-A4-18 | D3 (copy C4) | Declare the fins exactly as the A4-R2 register: half-fins `FIN-001-<station>`, block `FIN-004-L/R` with `E-FIN-07…12` all bonded (a tube clamp at `E-FIN-07/10` is an allowed deviation, say why in `notes`), lower-half edges `E-FIN-33…38`. Put the link slot (OI-03) in `FIN-001-LR/LL`. | 38 fins edges, the largest single set; `--compare` matches by id |
| CR-A4-19 | D2, F3 | Pitot boom: socket `POD-006` with keyed total/static ports that part when the boom is pulled (`CT-PLUG-IN`, `E-AVN-05`), sized for the boom's bending load in a nose-first tip-over; carry point and "do not lift by the motors" label `POD-007` (D-23). | OI-12; README field step "plug in the pitot boom" needs a tool-free pneumatic break |
| CR-A4-20 | C6, C4 | Joint stacks now owed for 19 fastened edges (`E-FIN-17…20`, `E-PRP-01…08`, `E-PWR-03`, `E-AVN-01`, `E-AVN-04`, `E-MEC-03…06`) and 4 clamps (`E-FIN-13…16`, closing screws + slip load above the 3.2 N·m prop-nut case and below tube damage, D-23). The R0 saddle clamps `E-FIN-07/08/10/11` are bonds now: C4 gives the `bond` block for the block joints against C1 case G2 10.7 N·m. Supersedes the numbers in CR-A4-10. | `merge_check.py` fails without the 19 stacks |
| CR-A4-21 | D7 | Add a pitot-boom slot to the prop tray (`E-TRN-12`, tip protected) and put the spar cradles at y = ±0.20 m (`E-TRN-05/06`). | box contents per README: props off, pitot boom off |
