# interfaces.json schema (`dbf-interfaces/1`)

Each subsystem writes `redesign/subsystems/<name>/interfaces.json`. `merge_check.py` merges them (plus the shared
`connection_types.json`) into `redesign/interfaces/interfaces.json` and writes `REPORT.md`. Working example: the
generic test aircraft in `redesign/fusion/examples/*/interfaces.json` (merged output in `example-output/`).

The graph: **parts** are nodes, **connection types** are nodes (`M3 SHCS into heat-set insert`, `epoxy bond`,
`JST-GH 6-pin`, `tape hinge`), **edges** join two parts *via* a connection type.

**Frame** (until `params.json` defines one, see CHANGE-REQUESTS.md): metres, x aft from the nose datum, y to the right
wing, z up. Right-handed.

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
| `id` | yes | `WNG-001` | prefix per subsystem (BRIEF.md); one node per physical instance (`-L`/`-R` ok) |
| `name` | yes | text | |
| `subsystem` | yes | folder name | |
| `status` | yes | `PROPOSED` `MODELLED` `CHECKED` `VERIFIED` | proposal / in a Fusion script / passes check.py or calc / bench evidence |
| `mass_g` | yes (may be `null` while PROPOSED) | number | declared mass; authoritative for the roll-up |
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
| `id` | yes | `E-<PREFIX>-NN` |
| `part_a`, `part_b` | yes | part ids (any subsystem) |
| `via` | yes | connection type id |
| `owner` | yes | subsystem responsible for the joint (normally the declaring one) |
| `notes` | yes (may be `""`) | |
| `joint_stack` | if `via.method = fastened` | table below |
| `motion` | if `via.method = hinged` | `{"axis": "Y", "range_deg": [-25, 25]}` |
| `wire` | if `via.kind = electrical` | table below |

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
| WARN | floating parts (no structural edge path to the main aircraft); electrical part unconnected or unpowered (no path to a `source`); one-sided interface (other side has not acknowledged); missing mass/CG; subsystem over its allocation; owner not a side |

`--strict` makes warnings fail (use at integration gates). Mass budget is read from `redesign/params/mass_budget.json`
(`{"limit_g": 7750, "allocations_g": {"wing": 1200}, "cg_x_m": [lo, hi]}`) or else the first table in
`redesign/MASS-CG.md` with a `subsystem` and an `alloc` column (row `total` = limit).

## Minimal example

```json
{"schema": "dbf-interfaces/1", "subsystem": "booms",
 "parts": [
  {"id": "BMS-001", "name": "Boom L", "subsystem": "booms", "status": "MODELLED", "mass_g": 45,
   "material": "CF tube 16x14", "cg_xyz_m": [0.275, -0.35, 0.05], "make_or_buy": "buy"},
  {"id": "BMS-003", "name": "Lift motor L", "subsystem": "booms", "status": "MODELLED", "mass_g": 120,
   "material": "motor (bought)", "cg_xyz_m": [-0.05, -0.35, 0.073], "make_or_buy": "buy", "electrical": "sink"}],
 "edges": [
  {"id": "E-BMS-03", "part_a": "BMS-003", "part_b": "BMS-001", "via": "CT-M3-SHCS-MOTOR", "owner": "booms", "notes": "",
   "joint_stack": {"fastener": "M3x8 SHCS", "count": 4, "grade": "A2-70", "hole": "3.4 mm clearance in mount",
    "insert": "none (motor base tapped)", "engagement_mm": 4.0, "min_engagement_mm": 3.0, "washer_nut": "none",
    "torque": "snug + threadlocker", "tool": "2.5 mm hex key", "access": "from below (-z)",
    "install_order": 3, "removal_order": 1}}],
 "acknowledges": ["E-PWR-04"]}
```
