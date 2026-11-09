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
`transport` `TRN` (`flight-software` `FSW` has no parts). Part numbers `NNN` are 001–899; **`9xx` is reserved for
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
  "acknowledges": ["E-BMS-01"]                 // edges declared by another subsystem that touch our parts
}
```

## Part

| Field | Required | Values | Notes |
|---|---|---|---|
| `id` | yes | `WNG-001`, `PRP-001-UR` | `<PREFIX>-NNN` for a single part. A multi-instance part has **one node per instance**, id `<PREFIX>-NNN-<UR\|UL\|LR\|LL\|L\|R>` (motor stations upper/lower right/left, or side), each with its own `cg_xyz_m`; one part number uses one suffix family. Two different parts on one side get two numbers, not a new suffix (CR-A3-09) |
| `name` | yes | text | |
| `subsystem` | yes | folder name | |
| `status` | yes | `PROPOSED` `MODELLED` `CHECKED` `VERIFIED` | proposal / in a Fusion script / passes check.py or calc / bench evidence |
| `mass_g` | yes (may be `null` while PROPOSED) | number | mass of **this one instance** = `parts.csv` `mass_g`, which is per unit (line mass = qty × `mass_g`, qty = number of instance nodes). Authoritative for the roll-up |
| `material` | yes | `6061-T6`, `PETG`, `XPS foam`, `LiPo`... | |
| `cg_xyz_m` | yes (may be `null` while PROPOSED) | `[x, y, z]` | aircraft frame |
| `make_or_buy` | yes | `make` `buy` | |
| `electrical` | if electrical | `source` `bus` `sink` | battery = source; PDB/ESC = bus; motor/servo/FC = sink |
| `flight` | optional | `false` for ground tools/fixtures | excluded from mass and floating checks |
| `notes` | optional | text | |

## Connection type

| Field | Values |
|---|---|
| `id` | `CT-...` (shared ones in `connection_types.json`; duplicates must be identical) |
| `kind` | `mechanical` `electrical` `thermal` `kinematic` |
| `method` | `fastened` `bonded` `clamped` `press_fit` `taped` `strapped` `hinged` `slid` `connector` `soldered` `conductive` |
| `spec` | one line, e.g. `M3 SHCS into M3 brass heat-set insert`, `JST-GH 6-pin`, `revolute hinge` |

## Edge

| Field | Required | Notes |
|---|---|---|
| `id` | yes | `E-<PREFIX of owner>-NN`; ids in the A4 plan are fixed, retired ids are never reused |
| `part_a`, `part_b` | yes | part ids (any subsystem). **Electrical: `part_a` is the supply side, `part_b` the load** (pack → disconnect → power module → PDB → ESC → motor; FC → servo for signals) |
| `via` | yes | connection type id |
| `owner` | yes | subsystem responsible for the joint; it declares the edge and the other side lists it under `acknowledges`. Rules (CHANGE-LOG D-20): the owner holds one side of every edge it declares, except **`harness`, which owns every electrical edge** (every wire and connector, incl. the ESC power and motor leads; `power` owns the boxes: pack, disconnect, power module, PDB, UBEC); the **elevon hinge is a `wing` edge** (D6 designs it); no edge under two owners |
| `notes` | yes (may be `""`) | |
| `joint_stack` | if `via.method = fastened` | table below |
| `motion` | if `via.method = hinged` | `{"axis": "Y", "range_deg": [-25, 25]}` |
| `wire` | if `via.kind = electrical` | table below |
| `signal_only` | optional, electrical | `true` on a lead that carries no power (ESC signal); A4's power-path check skips it |

**A4 data blocks** (optional fields on the same edge; `merge_check.py` ignores them, `team/A4/interface_plan.py
--compare` reports each as owed until filled; numbers carry units, unknown is `"—"`):

| Block | On method | Fields |
|---|---|---|
| `clamp` (+ `joint_stack` for the closing screws) | `clamped` | `bore_mm`, `part_od_mm`, `slip_load_n`, `sized_by` |
| `bond` | `bonded` | `adhesive`, `area_mm2`, `prep`, `cure`, `load_n`, `load_case`, `sized_by` |
| `retention` | `taped` `strapped` `slid` `press_fit` | `item`, `count`, `load_n`, `inspection` |
| `clearance_mm` | `hinged` | clearance at both stops, plus `hinge_moment_nmm` |
| `current_a` | electrical, power | `{"cont": A, "peak": A}` |
| `signal` | electrical, signal | `fc_port`, `protocol`, `i2c_addr` |
| `thermal` | `conductive` | `heat_w`, `t_max_c`, `t_ambient_c`, `path`, `sized_by` |
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
| WARN | floating parts (no structural edge path to the main aircraft); electrical part unconnected or unpowered (no path to a `source`); one-sided interface (other side has not acknowledged); missing mass/CG; subsystem over its allocation; owner not a side (expected today on every `harness` wire, D-20: `merge_check.py` does not yet exempt them; A4's `--compare` does) |

`--strict` makes warnings fail (use at integration gates). Mass budget is read from `redesign/params/mass_budget.json`
(written by `team/A1/frame_claims.py` from `params.json#mass.allocation_g`; K09-L: `{"limit_g": 2600,
"allocations_g": {"wing": 405, ...}, "cg_x_m": [0.040, 0.049]}`) or else the first table in `redesign/MASS-CG.md`
with a `subsystem` and an `alloc` column (row `total` = limit).

Checks that `merge_check.py` does not make (A4, `team/A4/interface_plan.py`): the part-id rule above; a load path
that does not rely on ties, tape channels, labels or pitot tubing; power reach along power wires `part_a` → `part_b`
with `signal_only` leads excluded; exactly one field disconnect (the pack plug).

## Minimal example

K09-L motor UR on its mount (values illustrative until C6 sizes the joint). The motor is a `propulsion` part; the
mount and the joint belong to `fins`, so `propulsion` lists `E-FIN-17` under `acknowledges`, and `fins` lists the
foot edge `E-GER-02` that `landing` declares on half-fin `FIN-001-UL`:

```json
{"schema": "dbf-interfaces/1", "subsystem": "fins",
 "parts": [
  {"id": "FIN-003-UR", "name": "Motor mount UR (3 deg cant)", "subsystem": "fins", "status": "PROPOSED", "mass_g": 18,
   "material": "PETG", "cg_xyz_m": [0.040, 0.32, 0.19], "make_or_buy": "make"}],
 "edges": [
  {"id": "E-FIN-17", "part_a": "PRP-001-UR", "part_b": "FIN-003-UR", "via": "CT-M3-SHCS-MOTOR", "owner": "fins", "notes": "",
   "joint_stack": {"fastener": "M3x6 SHCS", "count": 4, "grade": "A2-70", "hole": "3.4 mm clearance in the mount plate",
    "insert": "none (motor base tapped)", "engagement_mm": 3.0, "min_engagement_mm": 3.0, "washer_nut": "none",
    "torque": "snug + threadlocker", "tool": "2.5 mm hex key", "access": "from the tube side (+x)",
    "install_order": 3, "removal_order": 1}}],
 "acknowledges": ["E-GER-02"]}
```

`mass_g` 18 is one mount: `parts.csv` carries `FIN-003, qty 4, mass_g 18` and `interfaces.json` four nodes
`FIN-003-UR/UL/LR/LL`, each with its own `cg_xyz_m`.
