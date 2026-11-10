# interfaces.json schema (`dbf-interfaces/1`)

Each subsystem writes `redesign/subsystems/<name>/interfaces.json`. `merge_check.py` merges them (plus the shared
`connection_types.json`) into `redesign/interfaces/interfaces.json` and writes `REPORT.md`. Working example: the
generic test aircraft in `redesign/fusion/examples/*/interfaces.json` (merged output in `example-output/`).

The graph: **parts** are nodes, **connection types** are nodes (`M3 SHCS into heat-set insert`, `epoxy bond`,
`JST-GH 6-pin`, `tape hinge`), **edges** join two parts *via* a connection type.

**Frame**: the aircraft frame in [`params/params.json#frame`](../params/params.json) (datum names in
[`fusion/DATUMS.md`](../fusion/DATUMS.md)); every `cg_xyz_m` uses it. For K09-L: metres, right-handed, origin at the
wing root leading edge on the chord line, x aft, y to the right wing tip, z up in cruise (in hover +x points at the
ground). Never model or report in the hover attitude.

**Subsystems and ids (K09-L)**: folder names and prefixes are the README table: `wing` `WNG`, `fins` `FIN`, `pod`
`POD`, `landing` `GER`, `propulsion` `PRP`, `power` `PWR`, `avionics` `AVN`, `harness` `HRN`, `mechanisms` `MEC`,
`transport` `TRN`, `ground` `GND` (ground equipment, every part `"flight": false`; F5, D-46/CR-F5-10)
(`flight-software` `FSW` has no parts). Part numbers `NNN` are 001–899; **`9xx` is reserved for
`fusion/skeleton/`** so the skeleton can be merged with real subsystems without an id clash. The planned ids, owners
and edges are in [`team/A4/INTERFACE-PLAN.md`](../team/A4/INTERFACE-PLAN.md); use them.

## File

```json
{
  "schema": "dbf-interfaces/1",
  "subsystem": "wing",                         // = folder name; every part below has this subsystem
  "parts": [ ... ],
  "connection_types": [ ... ],                 // optional: types not in the shared library
  "edges": [ ... ],                            // edges THIS subsystem owns/declares
  "acknowledges": ["E-BMS-01"],                // edges declared by another subsystem that touch our parts
  "edges_pending": [ ... ]                     // optional: complete edges to parts nobody has declared yet
}
```

`edges_pending` (D3 practice, adopted A4-R3): an edge whose other side does not exist yet would be a `dangling`
ERROR, so the owner parks it here with `"waits_for": [part ids]`. `merge_check.py` ignores the list; `--compare`
counts these edges as declared-pending, not missing. Move each one into `edges` as soon as its part is declared.

## Part

| Field | Required | Values | Notes |
|---|---|---|---|
| `id` | yes | `WNG-001`, `PRP-001-UR`, `FIN-011-URO` | `<PREFIX>-NNN` for a single part. A multi-instance part has **one node per instance**, id `<PREFIX>-NNN-<UR\|UL\|LR\|LL\|L\|R\|C>[I\|O]` (motor stations upper/lower right/left, or side left/right/centre; the optional `I`/`O` = inboard/outboard face when the same part sits twice at one station, A4-R3), each with its own `cg_xyz_m`; one part number uses one suffix family. Two different parts on one side get two numbers, not a new suffix (CR-A3-09) |
| `name` | yes | text | |
| `subsystem` | yes | folder name | |
| `status` | yes | `PROPOSED` `MODELLED` `CHECKED` `VERIFIED` | proposal / in a Fusion script / passes check.py or calc / bench evidence |
| `mass_g` | yes (may be `null` while PROPOSED) | number | mass of **this one instance** = `parts.csv` `mass_g`, which is per unit (line mass = qty × `mass_g`, qty = number of instance nodes). Authoritative for the roll-up |
| `material` | yes | `6061-T6`, `PETG`, `XPS foam`, `LiPo`... | |
| `cg_xyz_m` | yes (may be `null` while PROPOSED) | `[x, y, z]` | aircraft frame |
| `make_or_buy` | yes | `make` `buy` | |
| `electrical` | if electrical | `source` `bus` `sink` | battery = source; PDB/ESC = bus; motor/servo/FC = sink |
| `flight` | optional | `false` for ground tools/fixtures | excluded from mass and floating checks |
| `carried` | optional | `true` for a lumped or carried item held only by non-structural types (harness bundle, label, consumables set) | exempt from the floating check; without it, a part held only by ties floats (D-46) |
| `notes` | optional | text | |

## Connection type

| Field | Values |
|---|---|
| `id` | `CT-...` (shared ones in `connection_types.json`; duplicates must be identical) |
| `kind` | `mechanical` `electrical` `thermal` `kinematic` |
| `method` | `fastened` `bonded` `clamped` `press_fit` `taped` `strapped` `hinged` `slid` `connector` `soldered` `conductive` `radio` (electrical, no wire: a radio link, D-46) |
| `spec` | one line, e.g. `M3 SHCS into M3 brass heat-set insert`, `JST-GH 6-pin`, `revolute hinge` |
| `structural` | optional; `false` on a type that locates a part but never carries its flight load (`CT-TIE`, `CT-WIRE-CHANNEL`, `CT-LABEL`, `CT-PITOT-TUBING`). Such edges do not join parts in the floating check, and a part flagged `"carried": true` held only by them is not floating; any other part held only by them is (D-46) |

## Edge

| Field | Required | Notes |
|---|---|---|
| `id` | yes | `E-<PREFIX of owner>-NN`; ids in the A4 plan are fixed, retired ids are never reused |
| `part_a`, `part_b` | yes | part ids (any subsystem). **Electrical: `part_a` is the supply side, `part_b` the load** (pack → disconnect → power module → PDB → ESC → motor; FC → servo for signals) |
| `via` | yes | connection type id |
| `owner` | yes | subsystem responsible for the joint; it declares the edge and the other side lists it under `acknowledges`. Rules (CHANGE-LOG D-20): the owner holds one side of every edge it declares, except **`harness`, which owns every electrical edge** (every wire and connector, incl. the ESC power and motor leads; `power` owns the boxes: pack, disconnect, power module, PDB, UBEC; `merge_check.py` does not warn `owner` on them, D-46); the **elevon hinge is a `wing` edge** (D6 designs it); no edge under two owners |
| `notes` | yes (may be `""`) | |
| `joint_stack` | if `via.method = fastened` | table below |
| `motion` | if `via.method = hinged` | `{"axis": "Y", "range_deg": [-25, 25]}` |
| `wire` | if `via.kind = electrical` (not on `method: radio`) | table below |
| `signal_only` | optional, electrical | `true` on a lead that carries no power (ESC signal); the power-path check skips it |
| `stowed` | optional, transport | `true` on a transport edge whose flight part is removed for transport and stored in the box (props, pitot boom in the tray). The part stays at its flight station in CAD, so `fusion/check.py` does not touch-check the edge and exempts the part from the box-overlap check (CR-A5-10, D-31) |

**A4 data blocks** (optional fields on the same edge; `merge_check.py` ignores them, `team/A4/interface_plan.py
--compare` reports each as owed until filled; numbers carry units, unknown is `"—"`):

| Block | On method | Fields |
|---|---|---|
| `clamp` (+ `joint_stack` for the closing screws) | `clamped` | `bore_mm`, `part_od_mm`, `slip_load_n`, `sized_by` |
| `bond` | `bonded` | `adhesive`, `area_mm2`, `prep`, `cure`, `load_n`, `load_case`, `sized_by` |
| `retention` | `taped` `strapped` `slid` `press_fit` | `item`, `count`, `load_n`, `inspection` |
| `clearance_mm` | `hinged` | clearance at both stops, plus `hinge_moment_nmm` |
| `current_a` | electrical, power | `{"cont": A, "peak": A}` |
| `signal` | electrical, signal or radio | `fc_port`, `protocol`, `i2c_addr` (radio: `band`, `tx_power_mw`) |
| `thermal` | `conductive` | `heat_w`, `t_max_c`, `t_ambient_c`, `path`, `sized_by` (E3 adds `t_design_c` and the claim id) |
| `field_joint` | any | `true` on a joint made at every field set-up (prop nuts, pitot boom, pack strap, pack plug) |

**Joint stack** (every field required; text is fine where a number does not fit):

| Field | Example |
|---|---|
| `fastener` | `M3x12 SHCS` |
| `count` | `2` |
| `grade` | `A2-70` / `12.9` |
| `hole` | `3.4 mm clearance in part_a; insert bore 4.0 mm in part_b` |
| `insert` | `M3x5.7 brass heat-set` / `none` |
| `engagement_mm`, `min_engagement_mm` | `5.0`, `4.5` (check fails if engagement < minimum; minimum = 1.5 x d into insert/plastic, 1 x d into metal unless cited) |
| `washer_nut` | `none` / `M3 nyloc + washer` |
| `torque` | `0.5 N m` / `snug + threadlocker` |
| `tool` | `2.5 mm hex key` |
| `access` | `from below (-z), through hatch` |
| `install_order`, `removal_order` | integers within the subsystem build |

**Wire** (wiring is an installation, not a line between nodes):

| Field | Example |
|---|---|
| `gauge_awg` | `12` |
| `connector` | `XT60` |
| `route_id` | `R-FUS-01` (the CAD wire path registered with the same edge id) |
| `support_points` | `["tie at FUS frame 2", "clip at spar"]` |
| `bend_radius_mm` | `15` |
| `strain_relief` | `heat-shrink + tie at connector` |
| `disconnect` | `true` at every removable joint (wing for transport) |
| `slack_mm` | optional; required by practice across moving surfaces |

## What merge_check.py reports

| Severity | Check |
|---|---|
| ERROR | broken JSON; missing/invalid fields; duplicate part/edge ids; differing duplicate connection types; dangling edge (unknown part or `via`); missing joint-stack / motion / wire fields; thread engagement below minimum; aircraft mass over `limit_g`; CG outside `cg_x_m` |
| WARN | floating parts (no load-bearing edge path to the main aircraft; types with `"structural": false` do not count; a part held only by them floats unless flagged `"carried": true`); electrical part unconnected (no wire) or unpowered (no power-carrying wire path from a `source`, followed `part_a` → `part_b`, `signal_only` leads and radio links skipped); one-sided interface (other side has not acknowledged); missing mass/CG; subsystem over its allocation; owner not a side (never on a `harness` electrical edge, D-20/D-46) |

`--strict` makes warnings fail (use at integration gates). Mass budget is read from `redesign/params/mass_budget.json`
(written by `team/A1/frame_claims.py` from `params.json#mass.allocation_g`; K09-L: `{"limit_g": 2600,
"allocations_g": {"wing": 405, ...}, "cg_x_m": [0.040, 0.049]}`) or else the first table in `redesign/MASS-CG.md`
with a `subsystem` and an `alloc` column (row `total` = limit).

Checks that `merge_check.py` does not make (A4, `team/A4/interface_plan.py`): the part-id rule above; exactly one
field disconnect (the pack plug); every planned edge declared and acknowledged, with its data blocks
(`--compare`, which also reads `edges_pending` and `team/C6/joint_stacks.json`). Since D-46 the load-path and
power-path rules run in `merge_check.py` itself.

## Minimal example

K09-L motor UR on its mount (R3: D3 declaration, C6 stack in `team/C6/joint_stacks.json`). The motor is a
`propulsion` part; the mount and the joint belong to `fins`, so `propulsion` lists `E-FIN-61` under `acknowledges`,
and `fins` lists the foot edge `E-GER-01` that `landing` declares on half-fin `FIN-001-UR`:

```json
{"schema": "dbf-interfaces/1", "subsystem": "fins",
 "parts": [
  {"id": "FIN-003-UR", "name": "Motor mount UR, ASA, 7 deg canted plate, slip clamp", "subsystem": "fins",
   "status": "MODELLED", "mass_g": 11.0, "material": "ASA (printed)", "cg_xyz_m": [0.0396, 0.3215, 0.181],
   "make_or_buy": "make"}],
 "edges": [
  {"id": "E-FIN-61", "part_a": "PRP-001-UR", "part_b": "FIN-003-UR", "via": "CT-M3-SHCS-MOTOR", "owner": "fins", "notes": "",
   "joint_stack": {"fastener": "M3x8 SHCS ISO 4762", "count": 4, "grade": "A2-70",
    "hole": "3.4 mm drilled square to the canted plate face on the measured motor pattern",
    "insert": "none (motor base tapped M3)", "engagement_mm": 3.5, "min_engagement_mm": 3.0,
    "max_engagement_mm": "probed hole depth - 0.5", "washer_nut": "none", "torque": "0.20 N m + Loctite 243",
    "tool": "2.5 mm hex key", "access": "from behind the plate (+x)", "install_order": 3, "removal_order": 1}}],
 "acknowledges": ["E-GER-01"]}
```

`mass_g` 11.0 is one mount: `parts.csv` carries `FIN-003, qty 4, mass_g 11.0` and `interfaces.json` four nodes
`FIN-003-UR/UL/LR/LL`, each with its own `cg_xyz_m`.
