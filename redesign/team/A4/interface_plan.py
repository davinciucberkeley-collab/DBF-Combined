"""A4 interface plan for the K09-L quad tailsitter: every expected part id and interface, who declares it, who
acknowledges it, who sizes it and what data it must carry.

Run (repo root):
    python -I redesign/team/A4/interface_plan.py             # write interface_plan.json, check the plan, render the
                                                             # register into INTERFACE-PLAN.md, write claims.json
    python -I redesign/team/A4/interface_plan.py --compare   # also compare the subsystems' interfaces.json files
                                                             # against the plan -> PLAN-STATUS.md (run at each gate)

The plan reuses redesign/interfaces/merge_check.py (same Graph, same floating / electrical / one-sided checks), so a
plan that passes here becomes a merged graph that passes there once the owners fill in their data blocks.
Python 3 standard library only. Edit the plan in this file (build_parts / build_edges / RENAME; declared subsystems via --rebaseline); never edit the generated
interface_plan.json, PLAN-STATUS.md or the register section of INTERFACE-PLAN.md by hand.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
sys.path.insert(0, str(REDESIGN / "interfaces"))
sys.path.insert(0, str(REDESIGN / "proofs"))
import merge_check as mc  # noqa: E402

PLAN_JSON = HERE / "interface_plan.json"
PARAMS = json.loads((REDESIGN / "params" / "params.json").read_text(encoding="utf-8"))
PLAN_MD = HERE / "INTERFACE-PLAN.md"
STATUS_MD = HERE / "PLAN-STATUS.md"
BEGIN, END = "<!-- BEGIN GENERATED REGISTER (interface_plan.py) -->", "<!-- END GENERATED REGISTER -->"

# ----------------------------------------------------------------------------- subsystems (README, TEAM.md)
SUBS = {  # key: (prefix, designer, folder exists for parts)
    "wing": ("WNG", "D1"), "fins": ("FIN", "D3"), "pod": ("POD", "D2"), "landing": ("GER", "D5"),
    "propulsion": ("PRP", "E1"), "power": ("PWR", "F1"), "avionics": ("AVN", "F3"), "harness": ("HRN", "F2"),
    "mechanisms": ("MEC", "D6"), "transport": ("TRN", "D7"), "ground": ("GND", "F5"), "flight-software": ("FSW", "F4"),
}
STATIONS = ("UR", "UL", "LR", "LL")          # params.json#propulsion.stations.ids: Upper/Lower, Right/Left
SIDES = ("L", "R")
SIDE_FAMILY = ("L", "R", "C")                # C = centre (A4-R3)


def side(st):
    return st[1]


# ----------------------------------------------------------------------------- connection types
# A4-R3 (D-46): the 19 plan types, CT-AS150U, CT-GEL-PAD and CT-ELRS-RF are now in redesign/interfaces/
# connection_types.json (owner text verbatim where an owner declared first). Types used by one subsystem stay local.
LIB_ADDED = ["CT-TAPE-SKIN", "CT-LABEL", "CT-TAPE-FOAM", "CT-TAPE-TIE", "CT-TIE", "CT-WIRE-CHANNEL", "CT-STRAP-SLOT",
             "CT-HATCH-HL", "CT-CRADLE-CONTACT", "CT-PROP-ADAPTER", "CT-PROP-NUT", "CT-SERVO-SPLINE", "CT-CLEVIS",
             "CT-PLUG-IN", "CT-PITOT-TUBING", "CT-SOLDER-DC", "CT-BULLET-3", "CT-JST-GH-4", "CT-THERMAL-CONTACT",
             "CT-AS150U", "CT-GEL-PAD", "CT-ELRS-RF"]

# ----------------------------------------------------------------------------- data each method must carry
# Schema-required blocks are checked by merge_check.py; the A4 blocks are checked by --compare (WARN until filled).
REQUIRED = {
    "fastened": ("joint_stack", "schema: 13 fields; add max_engagement_mm where a screw can bottom on windings or a servo"),
    "clamped": ("joint_stack+clamp", "joint_stack for the closing screws; clamp {bore_mm, part_od_mm, slip_load_n, sized_by}"),
    "bonded": ("bond", "bond {adhesive, area_mm2, prep, cure, load_n, load_case, sized_by}"),
    "taped": ("retention", "retention {item, count, load_n, inspection}"),
    "strapped": ("retention", "retention {item, count, load_n, inspection}"),
    "slid": ("retention", "retention {item, count, load_n, inspection}"),
    "press_fit": ("retention", "retention {item, count, load_n, inspection}"),
    "hinged": ("motion+clearance", "schema motion {axis, range_deg}; clearance_mm at both stops; hinge_moment_nmm (B2)"),
    "connector": ("wire+elec", "schema wire (7 fields); power: current_a {cont, peak}; signal: signal {fc_port, protocol, i2c_addr}"),
    "soldered": ("wire+elec", "schema wire (7 fields); power: current_a {cont, peak}; signal: signal {fc_port, protocol, i2c_addr}"),
    "conductive": ("thermal", "thermal {heat_w, t_max_c, t_ambient_c, path, sized_by}"),
    "radio": ("signal", "signal {protocol, band, tx_power_mw}; no wire block"),
}
A4_BLOCKS = {"clamp": ("clamped",), "bond": ("bonded",), "retention": ("taped", "strapped", "slid", "press_fit"),
             "thermal": ("conductive",)}


# ----------------------------------------------------------------------------- R3 baseline (declared subsystems)
# A4-R3: a subsystem that has published interfaces.json is planned by its declaration, frozen here as a baseline
# (configuration control). Later changes by the owner show up in --compare as deviations until A4 re-baselines with
# `python -I redesign/team/A4/interface_plan.py --rebaseline` after reviewing them. Edges parked in `edges_pending`
# are part of the baseline. A4 overrides (target ids, flags) and additions are applied on top, below.
BASELINE = HERE / "baseline-R3.json"
BASELINED = ("fins", "landing", "pod", "propulsion", "transport")
FIELD_JOINTS = {"E-PRP-05", "E-PRP-06", "E-PRP-07", "E-PRP-08", "E-POD-05", "E-AVN-05"}   # README field steps


def rebaseline(root=REDESIGN / "subsystems"):
    """Snapshot the declared parts, local connection types and edges (incl. edges_pending) of BASELINED."""
    out = {"schema": "a4-baseline/1", "revision": "A4-R3", "taken_from": {}, "parts": [], "connection_types": [],
           "edges": []}
    for sub in BASELINED:
        path = root / sub / "interfaces.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        out["taken_from"][sub] = {"file": "redesign/subsystems/%s/interfaces.json" % sub,
                                  "parts": len(doc.get("parts", [])), "edges": len(doc.get("edges", [])),
                                  "edges_pending": len(doc.get("edges_pending", []))}
        for p in doc.get("parts", []):
            out["parts"].append({k: p[k] for k in ("id", "name", "subsystem", "make_or_buy", "electrical", "flight", "carried")
                                 if k in p})
        out["connection_types"] += doc.get("connection_types", [])
        for e in doc.get("edges", []) + doc.get("edges_pending", []):
            d = {k: e[k] for k in ("id", "part_a", "part_b", "via", "owner", "signal_only", "stowed", "field_joint")
                 if k in e}
            d["carries"] = re.sub(r"\s+", " ", e.get("notes", ""))[:200]
            if e in doc.get("edges_pending", []):
                d["pending"] = e.get("waits_for", [])
            out["edges"].append(d)
    BASELINE.write_text(mc.dump_lines(out), encoding="utf-8")
    return out


def baseline():
    return json.loads(BASELINE.read_text(encoding="utf-8"))


# A4 target ids that differ from a declaration (the owner renames; --compare shows it until then)
RENAME = {"TRN-006-A": "TRN-006-L", "TRN-006-B": "TRN-006-R"}   # CR-A4-24: one suffix family (side) per part number

# Local connection types for plan-only subsystems (the owner declares them in its own file; not library material)
PLAN_LOCAL_CTS = [
    {"id": "CT-CONN-PARK", "kind": "mechanical", "method": "slid",
     "spec": "connector half parked in a printed slot that takes the plug/unplug force; cable tie over it as secondary retention"},
    {"id": "CT-CARD-SLOT", "kind": "mechanical", "method": "press_fit",
     "spec": "memory card pushed into the board's spring-latched slot"},
]

# ----------------------------------------------------------------------------- parts (ids reserved by this plan)
# Id rule (README, CR-A3-09, SCHEMA.md): <PREFIX>-NNN for a single part; a multi-instance part has one node per
# instance, <PREFIX>-NNN-<UR|UL|LR|LL|L|R|C>[I|O], all instances one parts.csv line (mass_g per unit, line =
# qty x mass_g). NNN 001-899; 9xx is reserved for fusion/skeleton/ (CR-A5-04). Two different parts on one side get
# two numbers. A4-R3 widens the rule by C (centre, side family) and a face letter I/O (the same part twice at one
# station: FIN-011 edge strips inboard/outboard).
def build_parts():
    P = []

    def part(pid, name, sub, mob, elec=None, flight=True, note="", carried=False):
        d = {"id": pid, "name": name, "subsystem": sub, "make_or_buy": mob}
        if elec:
            d["electrical"] = elec
        if not flight:
            d["flight"] = False
        if carried:
            d["carried"] = True
        if note:
            d["notes"] = note
        P.append(d)

    for p in baseline()["parts"]:
        d = dict(p, id=RENAME.get(p["id"], p["id"]))
        d["declared"] = True
        P.append(d)
    w = "wing"
    part("WNG-001", "Wing core, one piece (XPS)", w, "make",
         note="features: spar slot; tube holes and through-core block cut-outs x 0.028-0.097 at y = +/-0.320; "
              "brace-anchor pockets 20 x 16 mm at y = +/-0.242 top and bottom; root fillets for 4 half-fins; servo "
              "pockets; pod recess; two ESC-lead surface grooves (F1)")
    part("WNG-002", "Spar CF 22x20x1000", w, "buy", note="z +0.0066 (D-43)")
    part("WNG-003", "Tape skin", w, "make")
    for s in SIDES:
        part(f"WNG-004-{s}", f"Spar plug under the through-core block {s} (PETG)", w, "make", note="C2; A3 WNG-E06")
        part(f"WNG-005-{s}", f"Spar plug at the brace anchors {s} (PETG)", w, "make",
             note="C2; A3 WNG-E07 books 4 x 4 g: count to confirm (CR-A4-27)")
    for s in SIDES:
        part(f"WNG-011-{s}", f"Elevon inboard {s}", w, "make", note="y 0.07-0.30, hinge x 0.2496")
        part(f"WNG-012-{s}", f"Elevon outboard {s}", w, "make", note="y 0.34-0.56, hinge x 0.2496")
    part("WNG-020", "FAA registration label", w, "make", carried=True)
    v = "power"
    part("PWR-001", "Flight pack 4S (re-terminated AS150U)", v, "buy", elec="source",
         note="second pack is a ground spare (not in the graph); pack leads >= 10 AWG, 0.10 m (F1)")
    part("PWR-002", "Main disconnect AS150U, aircraft half + 8 AWG pigtail", v, "buy", elec="bus", note="D-32")
    part("PWR-003", "Power module: CoreWing V2 power board (V/I sense)", v, "buy", elec="bus",
         note="mass carried in AVN-001 (CR-F3-04); 0 g in power")
    part("PWR-004", "Power distribution (PDB)", v, "buy", elec="bus")
    part("PWR-005", "UBEC 6 V 8 A class for servos (fitted, D-32)", v, "buy", elec="bus", note="5 A fuse in its feed E-HRN-21")
    a = "avionics"
    part("AVN-001", "Flight controller CoreWing F405 Wing APP V2", a, "buy", elec="sink")
    part("AVN-002", "GPS + compass HGLRC M100-5883", a, "buy", elec="sink")
    part("AVN-003", "RC receiver RadioMaster RP3 V2 (ELRS 2.4 GHz)", a, "buy", elec="sink")
    part("AVN-004", "Airspeed sensor MS4525DO (I2C 0x28)", a, "buy", elec="sink")
    part("AVN-005", "Pitot boom (plug-in)", a, "buy", note="removed for transport; tip `P:avionics.pitot_tip_xyz_m` %s" % (_p("avionics.pitot_tip_xyz_m"),))
    part("AVN-006", "Isolation and retention set: gel pads, foam tape, ties", a, "buy",
         note="consumables lumped as one node (5 g EST); the medium of E-AVN-01..04")
    part("AVN-007", "microSD 16-32 GB (logging)", a, "buy")
    h = "harness"
    part("HRN-001", "Pod harness bundle (lumped mass)", h, "make", carried=True,
         note="mass/CG holder; wires themselves are the electrical edges; \"carried\": true (D-46)")
    for s in SIDES:
        part(f"HRN-002-{s}", f"Wing-fin harness bundle {s} (lumped mass)", h, "make", carried=True)
    m = "mechanisms"
    for s in SIDES:
        part(f"MEC-001-{s}", f"Elevon servo {s}", m, "buy", elec="sink")
        part(f"MEC-002-{s}", f"Servo arm {s}", m, "buy")
        part(f"MEC-003-{s}", f"Pushrod {s}", m, "buy")
        part(f"MEC-004-{s}", f"Control horn {s} (inboard panel)", m, "buy")
        part(f"MEC-005-{s}", f"Inter-panel link {s}", m, "make",
             note="passes the lower half-fin root slot x 0.2376-0.2616 (CR-D3-05): OI-03")
        part(f"MEC-007-{s}", f"Servo cover {s}", m, "make")
        part(f"MEC-008-{s}", f"Servo frame {s}", m, "make")
    part("GND-001", "RC transmitter (ELRS 2.4 GHz, 25 mW)", "ground", "buy", flight=False,
         note="F5; ground equipment: not in mass, floating or power checks (CR-F5-10)")
    return P


# ----------------------------------------------------------------------------- edges
# carries: the data (beyond the per-method block) this joint must state; by: roles that design / size it.
# Ids are fixed once declared: a joint that survives a layout change keeps its id, new joints get the next free
# number, retired ids are listed in RETIRED and never reused. The R2 plan numbers for E-FIN-* and E-TRN-08..12
# were never declared; the first declarations (D3, D7) set them (A4-R3, see INTERFACE-PLAN.md).
RETIRED = {
    "FIN-001-L": "split into half-fins FIN-001-UL / -LL (D-04)", "FIN-001-R": "split into FIN-001-UR / -LR (D-04)",
    "FIN-005-L": "clip set per half-fin (R2), retired in R3", "FIN-005-R": "clip set per half-fin (R2), retired in R3",
    "FIN-005-UR": "clip sets retired in R3: station collars FIN-008 + edge strips FIN-011 (D3)",
    "FIN-005-UL": "clip sets retired in R3", "FIN-005-LR": "clip sets retired in R3", "FIN-005-LL": "clip sets retired in R3",
    "TRN-004": "hold-down strap replaced by lid pillars TRN-004-L/R (CR-D7-03)",
    "TRN-006-A": "rename to TRN-006-L (side family, CR-A4-24)", "TRN-006-B": "rename to TRN-006-R (CR-A4-24)",
}
DESIGNER = None   # filled from SUBS below


def _p(key):
    """A params.json value for the 'carries' text (text only; the claims read params through proofkit)."""
    d = PARAMS
    for k in key.split("."):
        d = d[k]
    return d["value"] if isinstance(d, dict) and "value" in d else d


def build_edges():
    E = []

    def edge(eid, a, b, via, owner, by, carries, oi=None, field=False, motion=None, signal_only=False,
             field_joint=False, stowed=False, declared=False, pending=None):
        d = {"id": eid, "part_a": a, "part_b": b, "via": via, "owner": owner, "by": by, "carries": carries}
        for k, v in (("signal_only", signal_only), ("stowed", stowed), ("field_disconnect", field),
                     ("field_joint", field_joint or eid in FIELD_JOINTS), ("declared", declared)):
            if v:
                d[k] = True
        if pending is not None:
            d["pending"] = pending
        if oi:
            d["open"] = oi
        if motion:
            d["motion"] = motion
        E.append(d)

    def n(prefix, i):
        return f"E-{prefix}-{i:02d}"

    # --- baselined declarations (D2 pod, D3 fins, D5 landing, D7 transport, E1 propulsion)
    oi_of = {"E-FIN-05": "OI-01", "E-FIN-06": "OI-01", "E-FIN-07": "OI-01", "E-FIN-08": "OI-01",
             "E-FIN-49": "OI-02", "E-FIN-50": "OI-02", "E-FIN-51": "OI-02", "E-FIN-52": "OI-02",
             "E-FIN-57": "OI-13", "E-FIN-58": "OI-13", "E-FIN-59": "OI-13", "E-FIN-60": "OI-13",
             "E-GER-01": "OI-05", "E-GER-02": "OI-05", "E-GER-03": "OI-05", "E-GER-04": "OI-05",
             "E-AVN-05": "OI-12", "E-POD-07": "OI-12"}
    for e in baseline()["edges"]:
        edge(e["id"], RENAME.get(e["part_a"], e["part_a"]), RENAME.get(e["part_b"], e["part_b"]), e["via"], e["owner"],
             SUBS[e["owner"]][1], e.get("carries", ""), oi=oi_of.get(e["id"]), signal_only=e.get("signal_only", False),
             field_joint=e.get("field_joint", False), stowed=e.get("stowed", False), declared=True,
             pending=e.get("pending"))

    hinge_x = _p("wing.chord_m") * (1 - _p("wing.elevon.chord_frac"))
    elevon = {"axis": "Y", "range_deg": [-25, 25], "source": "P:wing.elevon.deflection_deg"}
    # --- wing (D-20: the elevon hinge is a wing edge; D6 designs it)
    edge(n("WNG", 1), "WNG-002", "WNG-001", "CT-EPOXY", "wing", "D1 · C2",
         "slot fit (22.2 mm `EST`), bond length 1 000 mm, spar centre z +0.0066 m (D-43), spar bending load into core; "
         "blocks threaded on the spar before it is bonded (E-FIN-49/50)")
    edge(n("WNG", 2), "WNG-003", "WNG-001", "CT-TAPE-SKIN", "wing", "D1 · G2", "strip layout, overlap 10 %, wrap at LE/TE; laps 15 mm up the half-fin roots")
    edge(n("WNG", 3), "WNG-020", "WNG-003", "CT-LABEL", "wing", "D1 · H3", "position visible without tools (FAA)")
    i = 4
    for s in SIDES:
        for pid, ys in ((f"WNG-011-{s}", "0.07–0.30"), (f"WNG-012-{s}", "0.34–0.56")):
            edge(n("WNG", i), pid, "WNG-001", "CT-TAPE-HINGE", "wing", "D6 designs · B2 hinge moment",
                 "hinge line x %.4f m, panel y %s m, end gap to the half-fin, throw ±25° to stops" % (hinge_x, ys),
                 oi="OI-03", motion=elevon)
            i += 1
    for s in SIDES:
        edge(n("WNG", i), f"WNG-004-{s}", "WNG-002", "CT-EPOXY", "wing", "C2 · D1",
             "plug 19.8 × 36 mm inside the spar under the block at |y| 0.320 (bearing for E-FIN-49/50)", oi="OI-13"); i += 1
    for s in SIDES:
        edge(n("WNG", i), f"WNG-005-{s}", "WNG-002", "CT-EPOXY", "wing", "C2 · D1",
             "plug 19.8 × 20 mm inside the spar at the anchor station |y| 0.242 (E-FIN-57…60)", oi="OI-13"); i += 1

    # --- A4 additions to the baselined subsystems
    # thermal (E3, CR-E3-11): conduction paths E3 relies on; fins/pod/avionics declare them with a thermal block
    for k, st in enumerate(STATIONS, 81):
        edge(n("FIN", k), f"PRP-001-{st}", f"FIN-003-{st}", "CT-THERMAL-CONTACT", "fins", "E3 · D3",
             "four 4 × 4 mm pads; base 66.3 °C design (hover-only, 30 °C, `CL-E3-MOUNT-ASA`) vs 83 °C ASA limit; "
             "PETG fails (`CL-E3-MOUNT-PETG`, D-42)")
    for k, st in enumerate(STATIONS, 85):
        edge(n("FIN", k), f"PRP-002-{st}", f"FIN-007-{st}", "CT-THERMAL-CONTACT", "fins", "E3 · D3",
             "hook-and-loop, treated as insulating; ESC 61.6 °C design (`CL-E3-ESC-PEAK`) vs 85 °C; ASA pad (D-42)")
    edge("E-POD-12", "PWR-001", "POD-002", "CT-THERMAL-CONTACT", "pod", "E3 · D2",
         "insulating; pack 47.1 °C at landing (`CL-E3-PACK-END`) vs 50 °C life; take-off ≤ 34 °C; two pod vents")
    # stowed transport edges (CR-D7-09, CR-A5-10): flight parts removed for transport, not touch-checked
    for k, st in enumerate(STATIONS, 17):
        edge(n("TRN", k), f"PRP-003-{st}", "TRN-003", "CT-TRN-POCKET", "transport", "D7 · E1",
             "prop in its tray slot 285 × 30 × 40 mm (prop Ø 279 mm)", stowed=True)
    edge("E-TRN-21", "AVN-005", "TRN-003", "CT-TRN-POCKET", "transport", "D7 · F3",
         "pitot boom in its 220 × 25 × 25 mm slot, PE tip plug", stowed=True)

    # --- power mounts (D-20: power owns the boxes, harness the wires)
    edge(n("PWR", 1), "PWR-002", "POD-002", "CT-CONN-PARK", "power", "F1 · F2 · D2",
         "AS150U parked in a 60 mm slot x 0.030…0.090 in the left channel (CR-F1-13); the slot, not a tie, takes the "
         "≈ 30–50 N `EST` unplug force at every field set-up; plug reachable with the pack in")
    edge(n("PWR", 2), "PWR-003", "POD-002", "CT-TAPE-FOAM", "power", "F1 · F3", "CoreWing power board beside the FC")
    edge(n("PWR", 3), "PWR-004", "POD-002", "CT-M3-SHCS-INSERT", "power", "F1 · C6", "only if the PDB is a PCB (C6 stack); nylon spacers")
    edge(n("PWR", 4), "PWR-005", "POD-002", "CT-TAPE-FOAM", "power", "F1", "away from the GPS mast")
    # --- avionics mounts (F3 R3, CR-F3-08)
    edge(n("AVN", 1), "AVN-001", "POD-002", "CT-GEL-PAD", "avionics", "F3 · C6",
         "2 gel pads 5 mm, no screws, f_n ≈ 35 Hz; secondary tie with slack (C6 retention); arrow toward -x; "
         "beside the pack, never its stop (CR-C5-07)")
    edge(n("AVN", 2), "AVN-002", "POD-005", "CT-TAPE-FOAM", "avionics", "F3",
         "45° pad toward the nose; no steel within 50 mm (brass E-POD-06); 0.154 m from the nearest power item")
    edge(n("AVN", 3), "AVN-003", "POD-002", "CT-TAPE-FOAM", "avionics", "F3 · F5",
         "antennas out through the hatch, one along z, one along y, ≥ 30 mm from spar and tubes, ≥ 60 mm from the GPS")
    edge(n("AVN", 4), "AVN-004", "POD-002", "CT-TAPE-FOAM", "avionics", "F3", "left channel front, behind the socket; tubes ≤ 60 mm")
    edge(n("AVN", 5), "AVN-005", "POD-006", "CT-PLUG-IN", "avionics", "F3 · B4 · D2",
         "plug-in at every field set-up, tip %s m (`P:avionics.pitot_tip_xyz_m`, D-25) aligned to x, keyed so total/static "
         "cannot swap" % (_p("avionics.pitot_tip_xyz_m"),), oi="OI-12")
    edge(n("AVN", 6), "AVN-005", "AVN-004", "CT-PITOT-TUBING", "avionics", "F3",
         "barbed couplers at the boom root part when the boom is pulled; lines labelled, no kinks", oi="OI-12")
    edge(n("AVN", 7), "AVN-006", "POD-002", "CT-GEL-PAD", "avionics", "F3", "consumables set lumped on the tray (mass holder)")
    edge(n("AVN", 8), "AVN-007", "AVN-001", "CT-CARD-SLOT", "avionics", "F3", "16–32 GB SDHC, FAT32; logging (R-FC-STABLE)")
    edge(n("AVN", 9), "GND-001", "AVN-003", "CT-ELRS-RF", "avionics", "F5",
         "signal {protocol ELRS 2.4 GHz → CRSF 420 kbaud, tx_power_mw 25, telemetry through ELRS, no separate radio}; "
         "range test `T-F5-RANGE`")
    edge(n("AVN", 10), "AVN-001", "POD-002", "CT-THERMAL-CONTACT", "avionics", "E3 · F3",
         "gel pads + vents; FC 57.0 °C design (`CL-E3-FC-PEAK`), 70.7 °C hover-only, vs 85 °C")
    # --- mechanisms
    i = 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-008-{s}", "WNG-001", "CT-EPOXY", "mechanisms", "D6 · D1", "servo pocket; frame ≥ 720 mm² into XPS (CR-C6-13)"); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-001-{s}", f"MEC-008-{s}", "CT-M2-SCREW-PLASTIC", "mechanisms", "D6 · C6", "servo ear screws into bosses (C6 stack)"); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-002-{s}", f"MEC-001-{s}", "CT-SERVO-SPLINE", "mechanisms", "D6", "arm centred at servo neutral"); i += 1
    arm = {"axis": "Y", "range_deg": [-25, 25], "source": "P:wing.elevon.deflection_deg (linkage ratio per D6)"}
    for s in SIDES:
        edge(n("MEC", i), f"MEC-003-{s}", f"MEC-002-{s}", "CT-CLEVIS", "mechanisms", "D6", "arm hole radius, pushrod clear of skin", motion=arm); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-003-{s}", f"MEC-004-{s}", "CT-CLEVIS", "mechanisms", "D6", "horn hole radius (linkage ratio)", motion=arm); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-004-{s}", f"WNG-011-{s}", "CT-EPOXY", "mechanisms", "D6 · B2", "through-panel horn, ≥ 720 mm² bond, hinge moment"); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-005-{s}", f"WNG-011-{s}", "CT-EPOXY", "mechanisms", "D6", "link bonded in inboard panel", oi="OI-03"); i += 1
        edge(n("MEC", i), f"MEC-005-{s}", f"WNG-012-{s}", "CT-EPOXY", "mechanisms", "D6", "link bonded in outboard panel", oi="OI-03"); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-007-{s}", "WNG-003", "CT-TAPE-SKIN", "mechanisms", "D6", "removable for servo service"); i += 1
    # --- harness: bundle supports
    edge(n("HRN", 1), "HRN-001", "POD-002", "CT-TIE", "harness", "F2", "tie points on the tray")
    i = 2
    for s in SIDES:
        edge(n("HRN", i), f"HRN-002-{s}", "WNG-001", "CT-WIRE-CHANNEL", "harness", "F2 · D1",
             "ESC leads in two taped surface grooves 5 mm apart, not buried, ≥ 0.12 m from the mast top (F1); route "
             "clear of the spar slot and the anchor pockets", oi="OI-04"); i += 1
        edge(n("HRN", i), f"HRN-002-{s}", f"FIN-002-{s}", "CT-TIE", "harness", "F2 · D3", "ties along the tube, clear of the prop discs"); i += 1
    # --- harness: wires (D-20: harness owns every wire; part_a = supply side; the edge is the installation)
    pw = ("current_a {cont: `P:performance.hover_current_a` %.0f A hover, peak: `P:electrical.peak_current_a` %.0f A < 5 s}" % (
        _p("performance.hover_current_a"), _p("electrical.peak_current_a")))
    i = 10
    edge(n("HRN", i), "PWR-001", "PWR-002", "CT-AS150U", "harness", "F1 · F2",
         "THE field disconnect; AS150U 70 A cont / 140 A momentary ≥ 37.8 A required (%.2f ×, `CL-F1-AS150U-CONT`, "
         "D-32); %s" % (_p("requirements.disconnect_factor"), pw), field=True); i += 1
    edge(n("HRN", i), "PWR-002", "PWR-003", "CT-SOLDER-DC", "harness", "F1 · F2", "8 AWG ≤ 0.15 m twisted (`CL-F1-MAIN-RISE`); " + pw); i += 1
    edge(n("HRN", i), "PWR-003", "PWR-004", "CT-SOLDER-DC", "harness", "F1 · F2", "8 AWG, same run; " + pw); i += 1
    for st in STATIONS:
        edge(n("HRN", i), "PWR-004", f"PRP-002-{st}", "CT-SOLDER-DC", "harness", "F1 · F2",
             "ESC lead 16 AWG 0.5 m (`CL-F1-ESC-RISE`); current_a {cont: hover share, peak: "
             "`P:propulsion.current_max_per_motor_a` %.1f A}; route pod → wing groove → fin" %
             _p("propulsion.current_max_per_motor_a"), oi="OI-04"); i += 1
    for st in STATIONS:
        edge(n("HRN", i), f"PRP-002-{st}", f"PRP-001-{st}", "CT-BULLET-3", "harness", "F2 · E1",
             "phase extension ≤ 100 mm if the factory leads are short; phase order sets rotation (F4 map)", oi="OI-06"); i += 1
    edge(n("HRN", i), "PWR-004", "PWR-005", "CT-SOLDER-DC", "harness", "F1",
         "UBEC feed through an inline 5 A fuse + holder (bus → fuse → UBEC, CR-F1-06); fuse rating in the wire block"); i += 1
    edge(n("HRN", i), "PWR-005", "AVN-001", "CT-SERVO-JR", "harness", "F1 · F3",
         "servo rail 6 V; 5.2 A required > FC BEC 4.5 A (`CL-F1-SERVO-BEC-REQ`); stall current `UNVERIFIED`"); i += 1
    edge(n("HRN", i), "PWR-003", "AVN-001", "CT-JST-GH-6", "harness", "F1 · F3 · F4",
         "signal {BATT_* scaling of the CoreWing board: 64 A/V (`CL-F3-SENSE-*`)}"); i += 1
    for st in STATIONS:
        edge(n("HRN", i), "AVN-001", f"PRP-002-{st}", "CT-SERVO-JR", "harness", "F2 · F3 · F4",
             f"signal {{fc_port per F4 motor map for {st}, protocol DShot}}; ground reference; no power (ESC has no BEC)",
             signal_only=True); i += 1
    for s in SIDES:
        edge(n("HRN", i), "AVN-001", f"MEC-001-{s}", "CT-SERVO-JR", "harness", "F2 · F4",
             f"signal {{fc_port elevon {s}}}; servo power from the rail; extension through the wing groove", oi="OI-04"); i += 1
    edge(n("HRN", i), "AVN-001", "AVN-002", "CT-JST-GH-6", "harness", "F3 · F4",
         "signal {fc_port SERIAL5 (UART5) + I2C1, protocol UBX, compass i2c_addr 0x0D/0x2C}"); i += 1
    edge(n("HRN", i), "AVN-001", "AVN-003", "CT-JST-GH-4", "harness", "F3 · F5 · F4",
         "signal {fc_port SERIAL6, protocol CRSF 420 kbaud}; ≤ 150 mm twisted, away from ESC power leads (CR-F5-04)"); i += 1
    edge(n("HRN", i), "AVN-001", "AVN-004", "CT-JST-GH-4", "harness", "F3 · F4",
         "signal {fc_port I2C1, protocol I2C, i2c_addr 0x28}; ≤ 0.5 m"); i += 1
    return E


# ----------------------------------------------------------------------------- C6 joint stacks (CR-C6-15)
C6_STACKS = REDESIGN / "team" / "C6" / "joint_stacks.json"


def c6_blocks():
    """{edge id: {block name: block}} from C6; owners copy them into their interfaces.json."""
    try:
        return json.loads(C6_STACKS.read_text(encoding="utf-8"))["edges"]
    except (OSError, ValueError, KeyError):
        return {}


# ----------------------------------------------------------------------------- plan -> graph
def library():
    """Shared library + the owners' local types in the baseline + local types of plan-only subsystems."""
    with open(REDESIGN / "interfaces" / "connection_types.json", encoding="utf-8") as fh:
        lib = json.load(fh)["connection_types"]
    out = {c["id"]: c for c in baseline()["connection_types"] + PLAN_LOCAL_CTS}
    out.update({c["id"]: c for c in lib})
    return out


def sub_of(pid, parts):
    return parts[pid]["subsystem"]


def build_plan():
    plist = build_parts()
    parts = {p["id"]: p for p in plist}
    dup_parts = sorted({p["id"] for p in plist if sum(q["id"] == p["id"] for q in plist) > 1})
    edges = build_edges()
    c6 = c6_blocks()
    for e in edges:
        subs = {sub_of(e["part_a"], parts), sub_of(e["part_b"], parts)} if e["part_a"] in parts and e["part_b"] in parts else set()
        e["acknowledged_by"] = sorted(subs - {e["owner"]})
        blocks = sorted(k for k in c6.get(e["id"], {}) if k != "field_joint")
        if blocks:
            e["c6"] = blocks
    return {"schema": "a4-interface-plan/1", "revision": "A4-R3", "configuration": "K09-L",
            "generated_by": "redesign/team/A4/interface_plan.py",
            "baseline": {k: v for k, v in baseline()["taken_from"].items()},
            "subsystems": {k: {"prefix": v[0], "designer": v[1]} for k, v in SUBS.items()},
            "parts": list(parts.values()), "duplicate_parts": dup_parts, "library_added": LIB_ADDED,
            "local_connection_types": PLAN_LOCAL_CTS, "edges": edges}


def plan_graph(plan):
    """A merge_check.Graph holding the plan (no masses, no data blocks yet)."""
    g = mc.Graph()
    for cid, ct in library().items():
        mc._add_ctype(g, ct, "library+plan")
    for p in plan["parts"]:
        g.parts[p["id"]] = dict(p, status="PROPOSED", mass_g=None, cg_xyz_m=None, material="TBD", _src="plan")
    for e in plan["edges"]:
        g.edges[e["id"]] = dict(e, notes="", _src="plan", _sub=e["owner"])
        for s in e["acknowledged_by"]:
            g.acks.setdefault(s, set()).add(e["id"])
    return g


OWED_CODES = ("joint-stack", "motion", "wire", "no-mass")   # data the owners still have to write (mass counted apart)


def check_plan(plan):
    """Run merge_check's checks on the plan plus plan rules. Returns (graph, errors, owed) lists of tuples."""
    g = plan_graph(plan)
    mc.check(g)
    # Since D-46 merge_check itself exempts harness-owned wires from 'owner', skips "structural": false types in
    # the floating check and follows power wires part_a -> part_b; the plan adds the rules below.
    errors = [i for i in g.issues if i[1] not in OWED_CODES]
    owed = [i for i in g.issues if i[1] in OWED_CODES]
    errors += [("ERROR", "duplicate", pid, "part id twice in the plan") for pid in plan.get("duplicate_parts", [])]
    seen = set()
    for p in plan["parts"]:
        pre = SUBS[p["subsystem"]][0]
        if not p["id"].startswith(pre + "-"):
            errors.append(("ERROR", "prefix", p["id"], "part prefix != %s" % pre))
    for e in plan["edges"]:
        if e["id"] in seen:
            errors.append(("ERROR", "duplicate", e["id"], "edge id twice"))
        seen.add(e["id"])
        if not e["id"].startswith("E-%s-" % SUBS[e["owner"]][0]):
            errors.append(("ERROR", "prefix", e["id"], "edge id prefix != owner %s" % e["owner"]))
    errors += id_rule(plan)
    touched = {x for e in plan["edges"] for x in (e["part_a"], e["part_b"])}
    for p in plan["parts"]:
        if p["id"] not in touched:
            errors.append(("ERROR", "no-edge", p["id"], "part has no interface"))
    errors += load_path(plan, g) + power_path(plan, g)
    if sum(1 for e in plan["edges"] if e.get("field_disconnect")) != 1:
        errors.append(("ERROR", "field-disconnect", "plan", "exactly one field disconnect expected (P18)"))
    return g, errors, owed


ID_RE = re.compile(r"^(?P<pre>[A-Z]{3})-(?P<num>\d{3})(?:-(?P<inst>UR|UL|LR|LL|L|R|C)(?P<face>[IO])?)?$")


def id_rule(plan):
    """Part-id rule (README, CR-A3-09, CR-A5-04, A4-R3): <PREFIX>-NNN[-UR|UL|LR|LL|L|R|C][I|O], NNN 001-899 (9xx = skeleton);
    a multi-instance part uses one instance-suffix family only, so parts.csv qty = number of nodes; retired ids
    are never reused."""
    out, fam = [], {}
    for p in plan["parts"]:
        m = ID_RE.match(p["id"])
        if not m:
            out.append(("ERROR", "id-rule", p["id"], "not <PREFIX>-NNN[-UR|UL|LR|LL|L|R|C][I|O]"))
            continue
        if not 1 <= int(m["num"]) <= 899:
            out.append(("ERROR", "id-rule", p["id"], "NNN outside 001-899 (9xx reserved for fusion/skeleton)"))
        if p["id"] in RETIRED:
            out.append(("ERROR", "id-retired", p["id"], "retired: " + RETIRED[p["id"]]))
        fam.setdefault("%s-%s" % (m["pre"], m["num"]), set()).add(m["inst"])
    for base, insts in sorted(fam.items()):
        if None in insts and len(insts) > 1:
            out.append(("ERROR", "id-rule", base, "both a bare id and instance ids"))
        elif insts & set(STATIONS) and insts & set(SIDE_FAMILY):
            out.append(("ERROR", "id-rule", base, "mixes station (UR..LL) and side (L/R) suffixes"))
    return out


def load_path(plan, g):
    """Structural clusters without the non-load-bearing edges. Parts held only by such edges must be flagged
    "carried" (harness bundles, the label); any other part outside the main cluster has no load path."""
    load = [e for e in plan["edges"] if g.load_bearing(g.edges[e["id"]])]     # "structural": false types excluded
    touched = {x for e in load for x in (e["part_a"], e["part_b"])}
    h = mc.Graph()
    h.ctypes = g.ctypes
    h.parts = {k: v for k, v in g.flight_parts().items() if k in touched}
    h.edges = {e["id"]: g.edges[e["id"]] for e in load}
    groups = mc.clusters(h, parts=h.parts)
    out = [("ERROR", "load-path", ", ".join(sorted(grp)), "held to the aircraft only by ties, tape channels or tubing")
           for grp in groups[1:]]
    located = {x for e in plan["edges"] if g.kind(g.edges[e["id"]]) in mc.STRUCTURAL for x in (e["part_a"], e["part_b"])}
    for pid in sorted(set(g.flight_parts()) & located - touched):
        if not g.parts[pid].get("carried"):
            out.append(("ERROR", "load-path", pid, "held only by ties, tape channels, labels or tubing and not flagged carried"))
    return out


def power_path(plan, g):
    """Every electrical part reached from the pack through power-carrying wires, followed upstream -> downstream
    (part_a -> part_b), signal-only leads excluded.
    merge_check's 'unpowered' accepts any electrical edge, so an ESC fed only by its signal lead would pass there."""
    elec = {k for k, p in g.flight_parts().items() if p.get("electrical")}
    adj = {k: set() for k in elec}
    for e in plan["edges"]:
        if g.carries_power(g.edges[e["id"]]) and e["part_a"] in adj and e["part_b"] in adj:
            adj[e["part_a"]].add(e["part_b"])          # directed: part_a is the upstream (supply) side
    live = {k for k in elec if g.parts[k]["electrical"] == "source"}
    stack = list(live)
    while stack:
        for q in adj[stack.pop()] - live:
            live.add(q)
            stack.append(q)
    return [("ERROR", "power-path", k, "no power-carrying wire path from the pack") for k in sorted(elec - live)]


def metrics(plan):
    g, errors, owed = check_plan(plan)
    flight = g.flight_parts()
    keep = {k: v for k, v in flight.items() if k not in mc.carried(g, flight)}
    groups = mc.clusters(g, parts=keep)
    outside = set().union(*groups[1:]) if len(groups) > 1 else set()
    for i in load_path(plan, g):
        outside |= set(i[2].split(", "))
    elec = [k for k, p in flight.items() if p.get("electrical")]
    unpowered = {i[2] for i in g.issues if i[1] in ("unpowered", "unconnected")} | {i[2] for i in power_path(plan, g)}
    cross = [e for e in plan["edges"] if e["acknowledged_by"]]
    kinds = {}
    for e in plan["edges"]:
        k = g.kind(g.edges[e["id"]])
        kinds[k] = kinds.get(k, 0) + 1
    return {"parts": len(plan["parts"]), "flight_parts": len(flight), "edges": len(plan["edges"]),
            "cross_edges": len(cross), "connected_frac": (len(flight) - len(outside)) / len(flight) if flight else 0.0,
            "powered_frac": (len(elec) - len(unpowered)) / len(elec) if elec else 0.0,
            "field_disconnects": sum(1 for e in plan["edges"] if e.get("field_disconnect")),
            "field_joints": sum(1 for e in plan["edges"] if e.get("field_joint") or e.get("field_disconnect")),
            "id_violations": len(id_rule(plan)),
            "wires": sum(1 for e in plan["edges"] if g.kind(g.edges[e["id"]]) == "electrical"),
            "kinds": kinds, "declared_edges": sum(1 for e in plan["edges"] if e.get("declared")),
            "pending_edges": sum(1 for e in plan["edges"] if "pending" in e),
            "declared_parts": sum(1 for p in plan["parts"] if p.get("declared")),
            "stowed": sum(1 for e in plan["edges"] if e.get("stowed")),
            "c6_edges": sum(1 for e in plan["edges"] if e.get("c6")),
            "errors": len(errors), "owed": sum(1 for i in owed if i[1] != "no-mass"),
            "owed_mass": sum(1 for i in owed if i[1] == "no-mass")}


# ----------------------------------------------------------------------------- claims (proof chain)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])


@kit.calc("CALC-A4-PLAN-GRAPH", title="Interface plan graph checks",
          equation="connected = |main structural cluster| / |flight parts| ; powered = electrical parts reached from "
                   "a source / all ; field = count(edges with field_disconnect) ; id_violations = count(id-rule breaches)", inputs={"n_motors": "P:propulsion.n_motors"})
def plan_graph_checks(n_motors):
    """Reads the plan defined in this file; build_graph.py re-runs it, so an edited plan without a re-run is DRIFT."""
    if len(STATIONS) != n_motors:
        raise ValueError("plan has %d motor stations, params.json says %s" % (len(STATIONS), n_motors))
    m = metrics(build_plan())
    return {"connected_frac": m["connected_frac"], "powered_frac": m["powered_frac"],
            "field_disconnects": m["field_disconnects"], "edges": m["edges"], "parts": m["parts"],
            "id_violations": m["id_violations"]}


kit.claim("CL-A4-PLAN-CONNECTED", "Planned parts all connected", calc="CALC-A4-PLAN-GRAPH", output="connected_frac",
          unit="-", limit=(">=", 1.0),
          how="python -I redesign/team/A4/interface_plan.py; then merge_check.py on the real subsystems reports no 'floating'")
kit.claim("CL-A4-PLAN-POWERED", "Planned electrical parts all powered", calc="CALC-A4-PLAN-GRAPH",
          output="powered_frac", unit="-", limit=(">=", 1.0),
          how="interface_plan.py; merge_check.py reports no 'unpowered'/'unconnected'; bench power-up per H1")
kit.claim("CL-A4-FIELD-DISCONNECTS", "One field disconnect (pack plug)", calc="CALC-A4-PLAN-GRAPH",
          output="field_disconnects", unit="-", limit=("<=", "P:electrical.field_disconnects"),
          verifies=["R-TRANSPORT"], parts=["PWR-001", "PWR-002"],
          how="count field-disconnect joints in the merged graph; field set-up timed by H2 (one plug, four prop nuts)")
kit.claim("CL-A4-PLAN-ID-RULE", "Planned part ids follow the instance-id rule", calc="CALC-A4-PLAN-GRAPH",
          output="id_violations", unit="-", limit=("<=", 0),
          how="interface_plan.py id_rule(): <PREFIX>-NNN[-UR|UL|LR|LL|L|R], NNN 001-899, no retired id; "
              "--compare lists any declared id outside the plan; A3 mass_rollup.py maps instances to parts.csv lines by it")
kit.claim("CL-A4-PLAN-EDGES", "Planned interfaces", calc="CALC-A4-PLAN-GRAPH", output="edges", unit="-",
          how="interface_plan.py --compare: every planned edge declared and acknowledged")


# ----------------------------------------------------------------------------- rendering
def _pp(pid):
    return "`%s`" % pid


def _decl(e):
    if "pending" in e:
        return "pending"
    return "yes" if e.get("declared") else "—"


def render(plan):
    parts = {p["id"]: p for p in plan["parts"]}
    cts = library()
    m = metrics(plan)
    L = [BEGIN, "", "Generated by `python -I redesign/team/A4/interface_plan.py` from the plan in that script and "
         "`baseline-R3.json`. Do not edit by hand.", ""]
    L += ["| Parts (flight) | Interfaces | Cross-subsystem | Declared (pending) | Mech · elec · kin · thermal | Connected (load path) | Powered (power wires) | Field disconnects (field joints) | Stowed | Id-rule breaches | Plan errors | Schema blocks owed | Masses owed |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
          "| %d (%d) | %d | %d | %d (%d) | %d · %d · %d · %d | %.0f %% | %.0f %% | %d (%d) | %d | %d | %d | %d | %d |" % (
              m["parts"], m["flight_parts"], m["edges"], m["cross_edges"], m["declared_edges"], m["pending_edges"],
              m["kinds"].get("mechanical", 0), m["kinds"].get("electrical", 0), m["kinds"].get("kinematic", 0),
              m["kinds"].get("thermal", 0), 100 * m["connected_frac"], 100 * m["powered_frac"],
              m["field_disconnects"], m["field_joints"], m["stowed"], m["id_violations"], m["errors"], m["owed"],
              m["owed_mass"]), ""]
    # N2 matrix
    keys = [k for k in SUBS if k != "flight-software"]
    cnt = {}
    for e in plan["edges"]:
        a, b = parts[e["part_a"]]["subsystem"], parts[e["part_b"]]["subsystem"]
        cnt[(a, b)] = cnt.get((a, b), 0) + 1
        if a != b:
            cnt[(b, a)] = cnt.get((b, a), 0) + 1
    L += ["## N² matrix", "", "Interfaces between each pair of subsystems (diagonal: internal joints). Read a row: who this subsystem must agree with. Wires count under the two subsystems they join; harness (`HRN`) declares all %d of them (D-20); the radio link `E-AVN-09` is an avionics edge." % sum(1 for e in plan["edges"] if e["owner"] == "harness" and cts[e["via"]]["kind"] == "electrical"), "",
          "| | " + " | ".join(SUBS[k][0] for k in keys) + " |", "|---|" + "---|" * len(keys)]
    for a in keys:
        L.append("| **%s** | " % SUBS[a][0] + " | ".join(str(cnt.get((a, b), "")) if cnt.get((a, b)) else "·" for b in keys) + " |")
    L += [""]
    # part ids
    L += ["## Part ids reserved", "", "One node per physical instance, id `<PREFIX>-NNN-<UR|UL|LR|LL|L|R|C>[I|O]`; all instances of a part are one `parts.csv` line with `mass_g` per unit (CR-A3-09). Stations `UR UL LR LL` = upper/lower, right/left (`params.json#propulsion.stations.ids`); a half-fin takes the station it carries; `C` = centre; `I`/`O` = inboard/outboard face of the same part at one station (A4-R3). `NNN` 001–899; `9xx` is reserved for `fusion/skeleton/` (CR-A5-04). *Declared* = taken from the owner's `interfaces.json` into `baseline-R3.json`.", "",
          "| Subsystem | Designer | Prefix | Parts | Declared | Ids |", "|---|---|---|---|---|---|"]
    for k in keys:
        ids = [p["id"] for p in plan["parts"] if p["subsystem"] == k]
        nd = sum(1 for p in plan["parts"] if p["subsystem"] == k and p.get("declared"))
        L.append("| `%s` | %s | `%s` | %d | %d | %s |" % (k, SUBS[k][1], SUBS[k][0], len(ids), nd, " ".join(_pp(x) for x in ids)))
    L += ["| `flight-software` | F4 | `FSW` | 0 | — | no parts: data interfaces below |", "",
          "Retired ids (never reuse): " + "; ".join("`%s` %s" % kv for kv in RETIRED.items()) + ".", ""]
    # register
    L += ["## Interface register", "",
          "Declared by the owner in `subsystems/<owner>/interfaces.json`; each subsystem in *Ack* lists the id under `acknowledges`. "
          "*By* = designs · sizes. *Decl.* = in the R3 baseline (`yes`), parked in the owner's `edges_pending` (`pending`), or still to declare (`—`). "
          "*C6* = blocks C6 has written in `team/C6/joint_stacks.json` for the owner to copy. *Must carry* is in addition to the per-method block above (for declared edges: the owner's notes, shortened). `OI-nn` = open issue below.", ""]
    for k in keys:
        rows = sorted((e for e in plan["edges"] if e["owner"] == k), key=lambda e: e["id"])
        if not rows:
            continue
        L += ["### %s (%s, %d)" % (k, SUBS[k][1], len(rows)), "",
              "| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |", "|---|---|---|---|---|---|---|---|---|"]
        for e in rows:
            ct = cts[e["via"]]
            extra = e["carries"].replace("|", "/")
            if e.get("motion"):
                extra = ("motion %s %s°; " % (e["motion"]["axis"], e["motion"]["range_deg"])) + extra
            if e.get("stowed"):
                extra = "stowed; " + extra
            if e.get("signal_only"):
                extra = "signal only; " + extra
            if e.get("field_joint"):
                extra = "field joint; " + extra
            if e.get("open"):
                extra += " (%s)" % e["open"]
            L.append("| `%s` | `%s` %s | `%s` %s | %s · %s · `%s` | %s | %s | %s | %s | %s |" % (
                e["id"], e["part_a"], parts[e["part_a"]]["name"], e["part_b"], parts[e["part_b"]]["name"],
                ct["kind"], ct["method"], e["via"], ", ".join(e["acknowledged_by"]) or "—", e["by"], _decl(e),
                " ".join(e.get("c6", [])) or "—", extra.strip() or "—"))
        L.append("")
    # acknowledgements owed
    L += ["## Acknowledgements owed", "", "| Subsystem | Must list under `acknowledges` |", "|---|---|"]
    for k in keys:
        ids = [e["id"] for e in plan["edges"] if k in e["acknowledged_by"]]
        L.append("| `%s` | %s |" % (k, " ".join(_pp(x) for x in ids) or "—"))
    used = sorted({e["via"] for e in plan["edges"]})
    L += ["", "## Connection types used", "",
          "*Where*: `library` = `redesign/interfaces/connection_types.json` (A4-R3 additions marked +), else the subsystem that declares it locally.", "",
          "| Id | Kind | Method | Where | Spec |", "|---|---|---|---|---|"]
    with open(REDESIGN / "interfaces" / "connection_types.json", encoding="utf-8") as fh:
        lib = {c["id"] for c in json.load(fh)["connection_types"]}
    local = {}
    for e in plan["edges"]:
        if e["via"] not in lib:
            local.setdefault(e["via"], set()).add(e["owner"])
    for c in used:
        ct = cts[c]
        where = ("library" + (" +" if c in LIB_ADDED else "")) if c in lib else ", ".join(sorted(local.get(c, [])))
        L.append("| `%s` | %s | %s | %s | %s%s |" % (c, ct["kind"], ct["method"], where, ct["spec"],
                                                    "; not a load path" if ct.get("structural") is False else ""))
    L += ["", END]
    return "\n".join(L)


def write_md(plan):
    text = PLAN_MD.read_text(encoding="utf-8")
    a, b = text.index(BEGIN), text.index(END) + len(END)
    PLAN_MD.write_text(text[:a] + render(plan) + text[b:], encoding="utf-8")


# ----------------------------------------------------------------------------- compare the real graph with the plan
STACK_KEYS = ("count", "engagement_mm", "min_engagement_mm")
SIZE_RE = re.compile(r"M\d+(?:x[\d.]+)?")


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def stack_diff(have, c6):
    """Differences that matter between a declared joint stack and C6's: thread size, count, and the engagement
    numbers where both sides give a number (C6 text such as 'E1 measures' is not a conflict)."""
    out = []
    a, b = SIZE_RE.search(str(have.get("fastener", ""))), SIZE_RE.search(str(c6.get("fastener", "")))
    if a and b and a.group() != b.group():
        out.append("fastener %s vs C6 %s" % (a.group(), b.group()))
    for k in STACK_KEYS:
        x, y = _num(have.get(k)), _num(c6.get(k))
        if x is not None and y is not None and abs(x - y) > 1e-6:
            out.append("%s %s vs C6 %s" % (k, have.get(k), c6.get(k)))
    if "nylon" in str(c6.get("fastener", "")).lower() + str(have.get("fastener", "")).lower() and             ("nylon" in str(c6.get("fastener", "")).lower()) != ("nylon" in str(have.get("fastener", "")).lower()):
        out.append("material: %s vs C6 %s" % (have.get("fastener"), c6.get("fastener")))
    return out


def compare(plan, root=REDESIGN / "subsystems"):
    g = mc.check(mc.load(str(root)))
    parts = {p["id"]: p for p in plan["parts"]}
    planned = {e["id"]: e for e in plan["edges"]}
    pair = {frozenset((e["part_a"], e["part_b"])): e for e in plan["edges"]}
    c6 = c6_blocks()
    pending = {}                           # edge id -> (subsystem, waits_for, edge)
    for path in mc.find_sources(str(root)):
        try:
            doc = json.loads(Path(path).read_text(encoding="utf-8"))
        except ValueError:
            continue
        for e in doc.get("edges_pending", []):
            pending[e.get("id")] = (doc.get("subsystem"), e.get("waits_for", []), e)
    rows = []                              # (severity, code, item, detail)
    inv = {v: k for k, v in RENAME.items()}
    for pid, p in parts.items():
        if pid not in g.parts:
            if inv.get(pid) in g.parts:
                rows.append(("WARN", "part-id", inv[pid], "declared as %s; plan id %s (%s)" % (inv[pid], pid, RETIRED.get(inv[pid], ""))))
            else:
                rows.append(("OPEN", "part-missing", pid, "%s has not declared it" % p["subsystem"]))
        elif g.parts[pid]["subsystem"] != p["subsystem"]:
            rows.append(("WARN", "part-owner", pid, "declared by %s, plan says %s" % (g.parts[pid]["subsystem"], p["subsystem"])))
    for pid in sorted(set(g.parts) - set(parts) - set(RENAME)):
        rows.append(("INFO", "unplanned", pid, "declared by %s; A4 adds it to the plan or asks why" % g.parts[pid]["subsystem"]))
    matched = set()
    declared = dict(g.edges)
    for eid, (sub, waits, e) in pending.items():
        if eid not in declared:
            declared[eid] = dict(e, _pending=True)
    for eid, e in sorted(declared.items()):
        pa, pb = RENAME.get(e.get("part_a"), e.get("part_a")), RENAME.get(e.get("part_b"), e.get("part_b"))
        pe = planned.get(eid) or pair.get(frozenset((pa, pb)))
        if pe is None:
            rows.append(("INFO", "unplanned", eid, "edge %s-%s not in the plan" % (e.get("part_a"), e.get("part_b"))))
            continue
        matched.add(pe["id"])
        if e.get("_pending"):
            rows.append(("PEND", "edge-pending", eid, "in %s edges_pending, waits for %s" % (pending[eid][0], ", ".join(pending[eid][1]) or "?")))
        if pe["id"] != eid:
            rows.append(("WARN", "edge-id", eid, "plan calls this joint %s" % pe["id"]))
        elif frozenset((pa, pb)) != frozenset((pe["part_a"], pe["part_b"])):
            rows.append(("WARN", "edge-parts", eid, "declared %s-%s, plan %s-%s" % (e.get("part_a"), e.get("part_b"), pe["part_a"], pe["part_b"])))
        ct, pct = g.ctypes.get(e.get("via")), library()[pe["via"]]
        if ct and (ct["kind"], ct["method"]) != (pct["kind"], pct["method"]):
            rows.append(("WARN", "edge-type", eid, "declared %s/%s, plan %s/%s: owner states why in notes" % (
                ct["kind"], ct["method"], pct["kind"], pct["method"])))
        if e.get("owner") != pe["owner"]:
            rows.append(("WARN", "edge-owner", eid, "owner %s, plan %s" % (e.get("owner"), pe["owner"])))
        for flag in ("stowed", "signal_only", "field_joint"):
            if pe.get(flag) and not e.get(flag):
                rows.append(("WARN", "edge-flag", eid, '"%s": true missing' % flag))
        meth = ct["method"] if ct else pct["method"]
        for block, methods in A4_BLOCKS.items():
            if meth in methods and not e.get(block):
                src = " (C6 has it: copy from team/C6/joint_stacks.json)" if block in c6.get(pe["id"], {}) else ""
                rows.append(("OWED", "data", eid, "%s block missing (%s)%s" % (block, REQUIRED[meth][1], src)))
        if meth == "clamped" and not e.get("joint_stack"):
            rows.append(("OWED", "data", eid, "joint_stack for the clamp screws missing"))
        if ct and ct["kind"] == "electrical" and not (e.get("current_a") or e.get("signal")):
            rows.append(("OWED", "data", eid, "current_a or signal block missing"))
        if meth == "hinged" and "clearance_mm" not in e:
            rows.append(("OWED", "data", eid, "clearance_mm at the stops missing"))
        for block, val in c6.get(pe["id"], {}).items():         # CR-C6-15: C6 blocks merged as owners adopt them
            if block == "field_joint" or block in A4_BLOCKS:
                continue
            have = e.get(block)
            if not have:
                rows.append(("OWED", "c6", eid, "%s from C6 not copied into the declaration" % block))
            elif block == "joint_stack":
                diff = stack_diff(have, val)
                if diff:
                    rows.append(("WARN", "c6", eid, "joint_stack differs from C6: " + "; ".join(diff)))
                eng, mn = _num(have.get("engagement_mm")), _num(val.get("min_engagement_mm"))
                if eng is not None and mn is not None and eng < mn:
                    rows.append(("WARN", "engagement", eid, "declared engagement %s mm < C6 minimum %s mm (D-41)" % (eng, mn)))
    for eid in sorted(set(planned) - matched):
        rows.append(("OPEN", "edge-missing", eid, "%s has not declared it" % planned[eid]["owner"]))
    return g, rows


def write_status(plan, g, rows):
    order = {"WARN": 0, "OWED": 1, "PEND": 2, "OPEN": 3, "INFO": 4}
    n = lambda s: sum(1 for r in rows if r[0] == s)
    me = sum(1 for i in g.issues if i[0] == "ERROR")
    mw = sum(1 for i in g.issues if i[0] == "WARN")
    missing = sum(1 for r in rows if r[1] == "edge-missing")
    L = ["# Interface plan status", "",
         "Generated by `python -I redesign/team/A4/interface_plan.py --compare`. Do not edit by hand.", "",
         "| Sources | Planned edges | Declared (matched) | Pending | Missing | Unplanned | Data owed | Deviations | merge_check errors / warnings |",
         "|---|---|---|---|---|---|---|---|---|",
         "| %d | %d | %d | %d | %d | %d | %d | %d | %d / %d |" % (
             len(g.sources), len(plan["edges"]), len(plan["edges"]) - missing, n("PEND"), missing, n("INFO"),
             n("OWED"), n("WARN"), me, mw), "",
         "Severities: WARN = the declaration deviates from the plan (owner explains or A4 re-baselines); OWED = a data "
         "block still to write or copy; PEND = declared in `edges_pending`; OPEN = not declared yet; INFO = declared but "
         "not planned.", "",
         "| Severity | Check | Item | Detail |", "|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (order[r[0]], r[1], r[2])):
        L.append("| %s | %s | `%s` | %s |" % (r[0], r[1], r[2], r[3].replace("|", "/")))
    STATUS_MD.write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv):
    if "--rebaseline" in argv:
        b = rebaseline()
        print("rebaseline: %s" % ", ".join("%s %d parts / %d edges / %d pending" % (k, v["parts"], v["edges"], v["edges_pending"])
                                           for k, v in b["taken_from"].items()))
    plan = build_plan()
    PLAN_JSON.write_text(mc.dump_lines(plan), encoding="utf-8")
    g, errors, owed = check_plan(plan)
    m = metrics(plan)
    write_md(plan)
    kit.write()
    for sev, code, item, msg in errors:
        print("  %-5s %-16s %-14s %s" % (sev, code, item, msg))
    print("interface_plan: %d parts (%d flight), %d edges (%d cross-subsystem, %d declared, %d pending), connected %.0f %%, "
          "powered %.0f %%, field disconnects %d, schema data blocks owed %d, masses owed %d -> %s" % (
              m["parts"], m["flight_parts"], m["edges"], m["cross_edges"], m["declared_edges"], m["pending_edges"],
              100 * m["connected_frac"], 100 * m["powered_frac"], m["field_disconnects"], m["owed"], m["owed_mass"],
              "FAIL" if errors else "PASS"))
    if "--compare" in argv:
        gg, rows = compare(plan)
        write_status(plan, gg, rows)
        cnt = lambda s: sum(1 for r in rows if r[0] == s)
        print("compare: %d sources; %d missing edges, %d pending, %d owed data blocks, %d deviations, %d unplanned -> %s" % (
            len(gg.sources), sum(1 for r in rows if r[1] == "edge-missing"), cnt("PEND"), cnt("OWED"), cnt("WARN"),
            cnt("INFO"), os.path.relpath(STATUS_MD, REDESIGN).replace("\\", "/")))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
