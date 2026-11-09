"""A4 interface plan for the K09-L quad tailsitter: every expected part id and interface, who declares it, who
acknowledges it, who sizes it and what data it must carry.

Run (repo root):
    python -I redesign/team/A4/interface_plan.py             # write interface_plan.json, check the plan, render the
                                                             # register into INTERFACE-PLAN.md, write claims.json
    python -I redesign/team/A4/interface_plan.py --compare   # also compare the subsystems' interfaces.json files
                                                             # against the plan -> PLAN-STATUS.md (run at each gate)

The plan reuses redesign/interfaces/merge_check.py (same Graph, same floating / electrical / one-sided checks), so a
plan that passes here becomes a merged graph that passes there once the owners fill in their data blocks.
Python 3 standard library only. Edit the plan in this file (PARTS / EDGES / NEW_CTS); never edit the generated
interface_plan.json, PLAN-STATUS.md or the register section of INTERFACE-PLAN.md by hand.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
sys.path.insert(0, str(REDESIGN / "interfaces"))
sys.path.insert(0, str(REDESIGN / "proofs"))
import merge_check as mc  # noqa: E402

PLAN_JSON = HERE / "interface_plan.json"
PLAN_MD = HERE / "INTERFACE-PLAN.md"
STATUS_MD = HERE / "PLAN-STATUS.md"
BEGIN, END = "<!-- BEGIN GENERATED REGISTER (interface_plan.py) -->", "<!-- END GENERATED REGISTER -->"

# ----------------------------------------------------------------------------- subsystems (README, TEAM.md)
SUBS = {  # key: (prefix, designer, folder exists for parts)
    "wing": ("WNG", "D1"), "fins": ("FIN", "D3"), "pod": ("POD", "D2"), "landing": ("GER", "D5"),
    "propulsion": ("PRP", "E1"), "power": ("PWR", "F1"), "avionics": ("AVN", "F3"), "harness": ("HRN", "F2"),
    "mechanisms": ("MEC", "D6"), "transport": ("TRN", "D7"), "flight-software": ("FSW", "F4"),
}
STATIONS = ("UR", "UL", "LR", "LL")          # params.json#propulsion.stations.ids: Upper/Lower, Right/Left
SIDES = ("L", "R")


def side(st):
    return st[1]


# ----------------------------------------------------------------------------- connection types not in the library
# Proposed for redesign/interfaces/connection_types.json (A4 adds them when the interfaces/ step is assigned).
NEW_CTS = [
    {"id": "CT-TAPE-SKIN", "kind": "mechanical", "method": "taped",
     "spec": "packing-tape skin or cover, spanwise strips, 10 % overlap"},
    {"id": "CT-LABEL", "kind": "mechanical", "method": "taped", "spec": "adhesive label on the skin (FAA number)"},
    {"id": "CT-TAPE-FOAM", "kind": "mechanical", "method": "taped",
     "spec": "double-sided foam tape (3M VHB-class) + one cable tie as secondary retention"},
    {"id": "CT-TAPE-TIE", "kind": "mechanical", "method": "taped",
     "spec": "double-sided foam tape + two cable ties around pad and part; heat-sink face left uncovered"},
    {"id": "CT-TIE", "kind": "mechanical", "method": "strapped", "spec": "cable tie to a tie point or round a tube"},
    {"id": "CT-WIRE-CHANNEL", "kind": "mechanical", "method": "taped",
     "spec": "wires laid in a hot-wired or routed channel in the core, closed with tape"},
    {"id": "CT-STRAP-SLOT", "kind": "mechanical", "method": "slid", "spec": "strap threaded through slots in a printed part"},
    {"id": "CT-HATCH-HL", "kind": "mechanical", "method": "strapped",
     "spec": "hatch held by hook-and-loop strips; no magnets (compass on the GPS mast)"},
    {"id": "CT-CRADLE-CONTACT", "kind": "mechanical", "method": "slid",
     "spec": "aircraft rests in a foam-lined cradle, no fastening (transport only)"},
    {"id": "CT-PROP-ADAPTER", "kind": "mechanical", "method": "fastened",
     "spec": "prop adapter on the motor (bolt-on or collet), screws per the motor maker"},
    {"id": "CT-PROP-NUT", "kind": "mechanical", "method": "fastened", "spec": "prop clamped on the adapter by its nut"},
    {"id": "CT-SERVO-SPLINE", "kind": "mechanical", "method": "fastened",
     "spec": "servo arm on the output spline, M2 retaining screw"},
    {"id": "CT-CLEVIS", "kind": "kinematic", "method": "hinged",
     "spec": "steel pushrod end (Z-bend or clevis) in a horn or arm hole"},
    {"id": "CT-PITOT-TUBING", "kind": "mechanical", "method": "press_fit",
     "spec": "silicone tubing pushed on the pitot and sensor barbs, total and static lines (pneumatic)"},
    {"id": "CT-SOLDER-DC", "kind": "electrical", "method": "soldered", "spec": "soldered DC power joint, heat-shrink"},
    {"id": "CT-BULLET-3", "kind": "electrical", "method": "connector",
     "spec": "3 x gold bullet connectors, motor phases (size per E1)"},
    {"id": "CT-JST-GH-4", "kind": "electrical", "method": "connector", "spec": "JST-GH 4-pin (UART or I2C)"},
    {"id": "CT-THERMAL-CONTACT", "kind": "thermal", "method": "conductive",
     "spec": "dry contact, metal motor base on a printed mount face (conduction path)"},
]

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
}
A4_BLOCKS = {"clamp": ("clamped",), "bond": ("bonded",), "retention": ("taped", "strapped", "slid", "press_fit"),
             "thermal": ("conductive",)}


# ----------------------------------------------------------------------------- parts (ids reserved by this plan)
def build_parts():
    P = []

    def part(pid, name, sub, mob, elec=None, flight=True, note=""):
        d = {"id": pid, "name": name, "subsystem": sub, "make_or_buy": mob}
        if elec:
            d["electrical"] = elec
        if not flight:
            d["flight"] = False
        if note:
            d["notes"] = note
        P.append(d)

    w = "wing"
    part("WNG-001", "Wing core, one piece (XPS)", w, "make", note="spar slot, servo pockets, pod recess, saddle cut-outs, wire channels are features")
    part("WNG-002", "Spar CF 22x20x1000", w, "buy")
    part("WNG-003", "Tape skin", w, "make")
    for s in SIDES:
        part(f"WNG-011-{s}", f"Elevon inboard {s}", w, "make")
        part(f"WNG-012-{s}", f"Elevon outboard {s}", w, "make")
    part("WNG-020", "FAA registration label", w, "make")
    f = "fins"
    for s in SIDES:
        part(f"FIN-001-{s}", f"Fin {s} (foam board)", f, "make", note="one piece through a core slot or two halves: OI-01")
        part(f"FIN-002-{s}", f"Motor tube {s} CF 22x20x420", f, "buy")
        part(f"FIN-004-{s}", f"Tube-to-spar saddle {s}", f, "make", note="carries the 0.18 m tube-to-spar offset: OI-02")
        part(f"FIN-005-{s}", f"Fin-to-tube clip set {s}", f, "make", note="clip count per D3; one node per set")
    for st in STATIONS:
        part(f"FIN-003-{st}", f"Motor mount {st}", f, "make")
        part(f"FIN-007-{st}", f"ESC pad {st}", f, "make")
    p = "pod"
    part("POD-001", "Pod shell", p, "make")
    part("POD-002", "Pod tray", p, "make")
    part("POD-003", "Hatch", p, "make")
    part("POD-004", "Pack strap", p, "buy")
    part("POD-005", "GPS mast", p, "make")
    part("POD-006", "Pitot mount (pod nose)", p, "make", note="only if B4/F3 put the pitot at the pod nose: OI-07")
    for st in STATIONS:
        part(f"GER-001-{st}", f"Crushable foot {st}", "landing", "make")
    q = "propulsion"
    for st in STATIONS:
        part(f"PRP-001-{st}", f"Motor {st} X3108S", q, "buy", elec="sink")
        part(f"PRP-002-{st}", f"ESC {st} 45 A", q, "buy", elec="bus")
        part(f"PRP-003-{st}", f"Prop {st} 11x4.5MR", q, "buy", note="CW/CCW per E1/F4 map")
        part(f"PRP-004-{st}", f"Prop adapter and nut {st}", q, "buy")
    v = "power"
    part("PWR-001", "Flight pack 4S 6500", v, "buy", elec="source", note="second pack is a ground spare (not in the graph)")
    part("PWR-002", "Main disconnect, aircraft side + pigtail", v, "buy", elec="bus", note="XT60 or AS150U: OI-09")
    part("PWR-003", "Power module (V/I sensor)", v, "buy", elec="bus")
    part("PWR-004", "Power distribution (PDB or splice)", v, "buy", elec="bus")
    part("PWR-005", "UBEC 5-6 V for servos", v, "buy", elec="bus", note="delete if the FC's servo BEC suffices (F1/F3)")
    a = "avionics"
    part("AVN-001", "Flight controller", a, "buy", elec="sink")
    part("AVN-002", "GPS + compass", a, "buy", elec="sink")
    part("AVN-003", "RC receiver ELRS", a, "buy", elec="sink")
    part("AVN-004", "Airspeed sensor MS5525", a, "buy", elec="sink")
    part("AVN-005", "Pitot tube", a, "buy")
    h = "harness"
    part("HRN-001", "Pod harness bundle (lumped mass)", h, "make", note="mass/CG holder; wires themselves are the electrical edges")
    for s in SIDES:
        part(f"HRN-002-{s}", f"Wing-fin harness bundle {s} (lumped mass)", h, "make")
    m = "mechanisms"
    for s in SIDES:
        part(f"MEC-001-{s}", f"Elevon servo {s}", m, "buy", elec="sink")
        part(f"MEC-002-{s}", f"Servo arm {s}", m, "buy")
        part(f"MEC-003-{s}", f"Pushrod {s}", m, "buy")
        part(f"MEC-004-{s}", f"Control horn {s} (inboard panel)", m, "buy")
        part(f"MEC-005-{s}", f"Inter-panel link {s}", m, "make", note="crosses the fin at y = 0.32 m: OI-03")
        part(f"MEC-007-{s}", f"Servo cover {s}", m, "make")
        part(f"MEC-008-{s}", f"Servo frame {s}", m, "make")
    t = "transport"
    part("TRN-001", "Transport box", t, "make", flight=False)
    for s in SIDES:
        part(f"TRN-002-{s}", f"Spar cradle {s}", t, "make", flight=False)
    part("TRN-003", "Prop tray", t, "make", flight=False)
    part("TRN-004", "Hold-down strap", t, "buy", flight=False)
    return P


# ----------------------------------------------------------------------------- edges
# carries: the data (beyond the per-method block) this joint must state; by: roles that design / size it.
def build_edges():
    E = []

    def edge(eid, a, b, via, owner, by, carries, oi=None, field=False, motion=None, signal_only=False):
        d = {"id": eid, "part_a": a, "part_b": b, "via": via, "owner": owner, "by": by, "carries": carries}
        if signal_only:
            d["signal_only"] = True
        if oi:
            d["open"] = oi
        if field:
            d["field_disconnect"] = True
        if motion:
            d["motion"] = motion
        E.append(d)

    def n(prefix, i):
        return f"E-{prefix}-{i:02d}"

    elevon = {"axis": "Y", "range_deg": [-25, 25], "source": "P:wing.elevon.deflection_deg"}
    # --- wing
    edge(n("WNG", 1), "WNG-002", "WNG-001", "CT-EPOXY", "wing", "D1 · C2", "slot fit (22.2 mm `EST`), bond length 1 000 mm, spar bending load into core")
    edge(n("WNG", 2), "WNG-003", "WNG-001", "CT-TAPE-SKIN", "wing", "D1 · G2", "strip layout, overlap 10 %, wrap at LE/TE")
    edge(n("WNG", 3), "WNG-020", "WNG-003", "CT-LABEL", "wing", "D1 · H3", "position visible without tools (FAA)")
    i = 4
    for s in SIDES:
        for pid in (f"WNG-011-{s}", f"WNG-012-{s}"):
            edge(n("WNG", i), pid, "WNG-001", "CT-TAPE-HINGE", "wing", "D6 designs · B2 hinge moment",
                 "hinge line x 0.234 m, gap to fin board, throw ±25° to stops", oi="OI-03", motion=elevon)
            i += 1
    # --- fins
    i = 1
    for s in SIDES:
        edge(n("FIN", i), f"FIN-001-{s}", "WNG-001", "CT-EPOXY", "fins", "D3 · C4 · D1",
             "core slot or half-fin roots, bond area, fin-tip landing load into core", oi="OI-01"); i += 1
    for s in SIDES:
        edge(n("FIN", i), f"FIN-005-{s}", f"FIN-002-{s}", "CT-EPOXY", "fins", "D3 · C4", "clip bore on 22 mm OD, spacing along the tube", oi="OI-01"); i += 1
        edge(n("FIN", i), f"FIN-005-{s}", f"FIN-001-{s}", "CT-EPOXY", "fins", "D3 · C4", "clip to foam-board faces, 22 mm spacer or wedge", oi="OI-01"); i += 1
    for s in SIDES:
        edge(n("FIN", i), f"FIN-004-{s}", f"FIN-002-{s}", "CT-TUBE-CLAMP", "fins", "D3 · C4 · C6",
             "clamp on tube at z = 0, hover thrust 4 × table max into the saddle", oi="OI-02"); i += 1
        edge(n("FIN", i), f"FIN-004-{s}", "WNG-002", "CT-TUBE-CLAMP", "fins", "D3 · C4 · C2 · C6",
             "spar access cut-out in core at y = ±0.32 m, 0.18 m offset moment", oi="OI-02"); i += 1
        edge(n("FIN", i), f"FIN-004-{s}", "WNG-001", "CT-EPOXY", "fins", "D3 · C2", "bearing pad area on core (foam bearing stress)", oi="OI-02"); i += 1
    for st in STATIONS:
        edge(n("FIN", i), f"FIN-003-{st}", f"FIN-002-{side(st)}", "CT-TUBE-CLAMP", "fins", "D3 · C4 · C6",
             "mount at z = ±0.19 m, face at x = -0.10 m, anti-rotation on the tube"); i += 1
    for st in STATIONS:
        edge(n("FIN", i), f"PRP-001-{st}", f"FIN-003-{st}", "CT-M3-SHCS-MOTOR", "fins", "D3 · E1 · C6",
             "motor bolt pattern (E1), max screw length clear of windings, threadlocker"); i += 1
    for st in STATIONS:
        edge(n("FIN", i), f"FIN-007-{st}", f"FIN-001-{side(st)}", "CT-EPOXY", "fins", "D3", "pad position in the prop wash, near the motor"); i += 1
    for st in STATIONS:
        edge(n("FIN", i), f"PRP-002-{st}", f"FIN-007-{st}", "CT-TAPE-TIE", "fins", "D3 · E3",
             "heat-sink face to the air stream, not taped over; vibration retention", oi="OI-06"); i += 1
    for st in STATIONS:
        edge(n("FIN", i), f"PRP-001-{st}", f"FIN-003-{st}", "CT-THERMAL-CONTACT", "fins", "E3 · G3",
             "motor base temperature at hover vs printed-mount softening (PETG HDT ~70 °C `EST`)", oi="OI-06"); i += 1
    # --- pod
    edge(n("POD", 1), "POD-001", "WNG-001", "CT-EPOXY", "pod", "D2 · C3", "pod recess, bond area, crash load of pack mass")
    edge(n("POD", 2), "POD-002", "POD-001", "CT-EPOXY", "pod", "D2 · C3", "tray datum for all avionics mounts")
    edge(n("POD", 3), "POD-003", "POD-001", "CT-HATCH-HL", "pod", "D2", "opened every flight: tool-free, no magnets")
    edge(n("POD", 4), "POD-004", "POD-002", "CT-STRAP-SLOT", "pod", "D2", "strap slot width, two slots")
    edge(n("POD", 5), "PWR-001", "POD-002", "CT-STRAP-VELCRO", "pod", "D2 · C3 · C1",
         "pack 0.55 kg `UNVERIFIED` at crash g (C1); ±0.03 m slide for CG trim; hover attitude pulls pack toward -x")
    edge(n("POD", 6), "POD-005", "POD-001", "CT-EPOXY", "pod", "D2 · F3", "mast height for compass distance from power leads")
    edge(n("POD", 7), "POD-006", "POD-001", "CT-EPOXY", "pod", "D2 · B4", "pitot position out of the prop wash", oi="OI-07")
    # --- landing
    for k, st in enumerate(STATIONS, 1):
        edge(n("GER", k), f"GER-001-{st}", f"FIN-001-{side(st)}", "CT-EPOXY", "landing", "D5 · C5",
             "cap on fin TE tip at x = 0.30 m, crush stroke, replaceable after a hard landing", oi="OI-05")
    # --- propulsion
    for k, st in enumerate(STATIONS, 1):
        edge(n("PRP", k), f"PRP-004-{st}", f"PRP-001-{st}", "CT-PROP-ADAPTER", "propulsion", "E1", "adapter type and screws per the motor maker")
    for k, st in enumerate(STATIONS, 5):
        edge(n("PRP", k), f"PRP-003-{st}", f"PRP-004-{st}", "CT-PROP-NUT", "propulsion", "E1 · F4",
             "prop nut thread and torque; fitted at every field set-up; CW/CCW per station")
    # --- power mounts
    edge(n("PWR", 1), "PWR-002", "POD-002", "CT-TIE", "power", "F1 · F2", "pigtail exit inside the hatch, plug reachable with pack in")
    edge(n("PWR", 2), "PWR-003", "POD-002", "CT-TAPE-FOAM", "power", "F1", "")
    edge(n("PWR", 3), "PWR-004", "POD-002", "CT-M3-SHCS-INSERT", "power", "F1 · C6", "nylon standoffs if a PCB")
    edge(n("PWR", 4), "PWR-005", "POD-002", "CT-TAPE-FOAM", "power", "F1", "away from the GPS mast")
    # --- avionics mounts
    edge(n("AVN", 1), "AVN-001", "POD-002", "CT-M3-SHCS-INSERT", "avionics", "F3 · C6",
         "soft-mount grommets (washer_nut), arrow forward = -x in cruise, board orientation for F4 (AHRS_ORIENTATION)")
    edge(n("AVN", 2), "AVN-002", "POD-005", "CT-TAPE-FOAM", "avionics", "F3", "compass arrow direction for F4; distance to power leads")
    edge(n("AVN", 3), "AVN-003", "POD-002", "CT-TAPE-FOAM", "avionics", "F3 · F5", "antennas clear of CF spar and tubes", oi="OI-10")
    edge(n("AVN", 4), "AVN-004", "POD-002", "CT-M2-SCREW-PLASTIC", "avionics", "F3", "")
    edge(n("AVN", 5), "AVN-005", "POD-006", "CT-EPOXY", "avionics", "F3 · B4", "probe tip ahead of the pod nose, aligned to x", oi="OI-07")
    edge(n("AVN", 6), "AVN-005", "AVN-004", "CT-PITOT-TUBING", "avionics", "F3", "total/static lines labelled, no kinks, length")
    # --- mechanisms
    i = 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-008-{s}", "WNG-001", "CT-EPOXY", "mechanisms", "D6 · D1", "servo pocket size and position"); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-001-{s}", f"MEC-008-{s}", "CT-M2-SCREW-PLASTIC", "mechanisms", "D6 · C6", "servo ear screws"); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-002-{s}", f"MEC-001-{s}", "CT-SERVO-SPLINE", "mechanisms", "D6", "arm centred at servo neutral"); i += 1
    arm = {"axis": "Y", "range_deg": [-25, 25], "source": "P:wing.elevon.deflection_deg (linkage ratio per D6)"}
    for s in SIDES:
        edge(n("MEC", i), f"MEC-003-{s}", f"MEC-002-{s}", "CT-CLEVIS", "mechanisms", "D6", "arm hole radius, pushrod clear of skin", motion=arm); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-003-{s}", f"MEC-004-{s}", "CT-CLEVIS", "mechanisms", "D6", "horn hole radius (linkage ratio)", motion=arm); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-004-{s}", f"WNG-011-{s}", "CT-EPOXY", "mechanisms", "D6 · B2", "horn root bond, hinge moment"); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-005-{s}", f"WNG-011-{s}", "CT-EPOXY", "mechanisms", "D6", "link bonded in inboard panel", oi="OI-03"); i += 1
        edge(n("MEC", i), f"MEC-005-{s}", f"WNG-012-{s}", "CT-EPOXY", "mechanisms", "D6", "link bonded in outboard panel", oi="OI-03"); i += 1
    for s in SIDES:
        edge(n("MEC", i), f"MEC-007-{s}", "WNG-003", "CT-TAPE-SKIN", "mechanisms", "D6", "removable for servo service"); i += 1
    # --- harness: bundle supports
    edge(n("HRN", 1), "HRN-001", "POD-002", "CT-TIE", "harness", "F2", "tie points on the tray")
    i = 2
    for s in SIDES:
        edge(n("HRN", i), f"HRN-002-{s}", "WNG-001", "CT-WIRE-CHANNEL", "harness", "F2 · D1", "channel route pod → fin root, size", oi="OI-04"); i += 1
        edge(n("HRN", i), f"HRN-002-{s}", f"FIN-002-{s}", "CT-TIE", "harness", "F2 · D3", "ties along the tube, clear of the prop discs"); i += 1
    # --- harness: wires (electrical edges; the edge is the installation)
    pw = ("current_a {cont: `P:performance.hover_current_a` 24 A total, peak: `P:electrical.peak_current_a` 120 A}; "
          "connector ≥ 1.25 × cont (`P:requirements.disconnect_factor`)")
    i = 10
    edge(n("HRN", i), "PWR-001", "PWR-002", "CT-XT60", "harness", "F1 · F2",
         "THE field disconnect; " + pw + "; anti-spark choice", oi="OI-09", field=True); i += 1
    edge(n("HRN", i), "PWR-002", "PWR-003", "CT-SOLDER-DC", "harness", "F1 · F2", pw); i += 1
    edge(n("HRN", i), "PWR-003", "PWR-004", "CT-SOLDER-DC", "harness", "F1 · F2", pw); i += 1
    for st in STATIONS:
        edge(n("HRN", i), "PWR-004", f"PRP-002-{st}", "CT-SOLDER-DC", "harness", "F1 · F2",
             "current_a {cont: hover share, peak: `P:propulsion.current_max_per_motor_a` 30 A}; route pod → wing channel → fin", oi="OI-04"); i += 1
    for st in STATIONS:
        edge(n("HRN", i), f"PRP-002-{st}", f"PRP-001-{st}", "CT-BULLET-3", "harness", "F2 · E1",
             "motor lead length vs pad position (extension or not); phase order sets rotation (F4)", oi="OI-06"); i += 1
    edge(n("HRN", i), "PWR-004", "PWR-005", "CT-SOLDER-DC", "harness", "F1", "UBEC input"); i += 1
    edge(n("HRN", i), "PWR-005", "AVN-001", "CT-SERVO-JR", "harness", "F1 · F3", "servo-rail voltage within servo rating; stall current of 2 servos"); i += 1
    edge(n("HRN", i), "PWR-003", "AVN-001", "CT-JST-GH-6", "harness", "F1 · F3 · F4", "signal {BATT_* scaling: V and A per volt for F4}"); i += 1
    for st in STATIONS:
        edge(n("HRN", i), "AVN-001", f"PRP-002-{st}", "CT-SERVO-JR", "harness", "F2 · F3 · F4",
             f"signal {{fc_port per F4 motor map for {st}, protocol DShot/PWM}}; ground reference; no power (ESC has no BEC)",
             signal_only=True); i += 1
    for s in SIDES:
        edge(n("HRN", i), "AVN-001", f"MEC-001-{s}", "CT-SERVO-JR", "harness", "F2 · F4",
             f"signal {{fc_port elevon {s}}}; extension through the wing channel", oi="OI-04"); i += 1
    edge(n("HRN", i), "AVN-001", "AVN-002", "CT-JST-GH-6", "harness", "F3 · F4", "signal {UART + I2C, compass address}"); i += 1
    edge(n("HRN", i), "AVN-001", "AVN-003", "CT-JST-GH-4", "harness", "F3 · F5 · F4", "signal {UART, CRSF/ELRS, telemetry}", oi="OI-10"); i += 1
    edge(n("HRN", i), "AVN-001", "AVN-004", "CT-JST-GH-4", "harness", "F3 · F4", "signal {I2C, i2c_addr vs board baro}", oi="OI-08"); i += 1
    # --- transport (flight: false; not in mass or floating checks)
    i = 1
    for s in SIDES:
        edge(n("TRN", i), f"TRN-002-{s}", "TRN-001", "CT-EPOXY", "transport", "D7", ""); i += 1
    edge(n("TRN", i), "TRN-003", "TRN-001", "CT-EPOXY", "transport", "D7", ""); i += 1
    edge(n("TRN", i), "TRN-004", "TRN-001", "CT-STRAP-SLOT", "transport", "D7", ""); i += 1
    for s in SIDES:
        edge(n("TRN", i), f"TRN-002-{s}", "WNG-001", "CT-CRADLE-CONTACT", "transport", "D7 · C1",
             "cradle under the spar line; fins and tubes never pressed (`P:transport.cradle`)"); i += 1
    edge(n("TRN", i), "TRN-004", "WNG-001", "CT-STRAP-VELCRO", "transport", "D7 · C1", "strap over the centre section only"); i += 1
    for st in STATIONS:
        edge(n("TRN", i), f"PRP-003-{st}", "TRN-003", "CT-CRADLE-CONTACT", "transport", "D7", "props off for transport, one slot each"); i += 1
    return E


# ----------------------------------------------------------------------------- plan -> graph
def library():
    with open(REDESIGN / "interfaces" / "connection_types.json", encoding="utf-8") as fh:
        lib = json.load(fh)["connection_types"]
    return {c["id"]: c for c in lib + NEW_CTS}


def sub_of(pid, parts):
    return parts[pid]["subsystem"]


def build_plan():
    parts = {p["id"]: p for p in build_parts()}
    edges = build_edges()
    for e in edges:
        subs = {sub_of(e["part_a"], parts), sub_of(e["part_b"], parts)} if e["part_a"] in parts and e["part_b"] in parts else set()
        e["acknowledged_by"] = sorted(subs - {e["owner"]})
    return {"schema": "a4-interface-plan/1", "configuration": "K09-L", "generated_by": "redesign/team/A4/interface_plan.py",
            "subsystems": {k: {"prefix": v[0], "designer": v[1]} for k, v in SUBS.items()},
            "parts": list(parts.values()), "new_connection_types": NEW_CTS, "edges": edges}


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
    # Harness owns every electrical edge although neither end is a harness part (the wire is the installation,
    # README joint table). merge_check warns 'owner' for these until A4 adds that rule there (INTERFACE-PLAN.md).
    harness_owned = {e["id"] for e in plan["edges"] if e["owner"] == "harness" and g.kind(g.edges[e["id"]]) == "electrical"}
    errors = [i for i in g.issues if i[1] not in OWED_CODES and not (i[1] == "owner" and i[2] in harness_owned)]
    owed = [i for i in g.issues if i[1] in OWED_CODES]
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
    touched = {x for e in plan["edges"] for x in (e["part_a"], e["part_b"])}
    for p in plan["parts"]:
        if p["id"] not in touched:
            errors.append(("ERROR", "no-edge", p["id"], "part has no interface"))
    errors += load_path(plan, g) + power_path(plan, g)
    if sum(1 for e in plan["edges"] if e.get("field_disconnect")) != 1:
        errors.append(("ERROR", "field-disconnect", "plan", "exactly one field disconnect expected (P18)"))
    return g, errors, owed


# Edges that locate a part but carry no flight load: a harness tie must not be what holds a fin on.
NONSTRUCT_CTS = ("CT-TIE", "CT-WIRE-CHANNEL", "CT-LABEL", "CT-PITOT-TUBING")


def load_path(plan, g):
    """Structural clusters without the non-load-bearing edges. Parts held only by such edges (harness bundles, the
    label) are carried items; any other part outside the main cluster has no load path (merge_check cannot see this)."""
    load = [e for e in plan["edges"] if e["via"] not in NONSTRUCT_CTS]
    touched = {x for e in load if g.kind(g.edges[e["id"]]) in mc.STRUCTURAL for x in (e["part_a"], e["part_b"])}
    h = mc.Graph()
    h.ctypes = g.ctypes
    h.parts = {k: v for k, v in g.flight_parts().items() if k in touched}
    h.edges = {e["id"]: g.edges[e["id"]] for e in load}
    groups = mc.clusters(h, parts=h.parts)
    return [("ERROR", "load-path", ", ".join(sorted(grp)), "held to the aircraft only by ties, tape channels or tubing")
            for grp in groups[1:]]


def power_path(plan, g):
    """Every electrical part reached from the pack through power-carrying wires, followed upstream -> downstream
    (part_a -> part_b), signal-only leads excluded.
    merge_check's 'unpowered' accepts any electrical edge, so an ESC fed only by its signal lead would pass there."""
    elec = {k for k, p in g.flight_parts().items() if p.get("electrical")}
    adj = {k: set() for k in elec}
    for e in plan["edges"]:
        if g.kind(g.edges[e["id"]]) == "electrical" and not e.get("signal_only") and e["part_a"] in adj and e["part_b"] in adj:
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
    groups = mc.clusters(g)
    outside = set().union(*groups[1:]) if len(groups) > 1 else set()
    for i in load_path(plan, g):
        outside |= set(i[2].split(", "))
    elec = [k for k, p in flight.items() if p.get("electrical")]
    unpowered = {i[2] for i in g.issues if i[1] in ("unpowered", "unconnected")} | {i[2] for i in power_path(plan, g)}
    cross = [e for e in plan["edges"] if e["acknowledged_by"]]
    return {"parts": len(plan["parts"]), "flight_parts": len(flight), "edges": len(plan["edges"]),
            "cross_edges": len(cross), "connected_frac": (len(flight) - len(outside)) / len(flight) if flight else 0.0,
            "powered_frac": (len(elec) - len(unpowered)) / len(elec) if elec else 0.0,
            "field_disconnects": sum(1 for e in plan["edges"] if e.get("field_disconnect")),
            "errors": len(errors), "owed": sum(1 for i in owed if i[1] != "no-mass"),
            "owed_mass": sum(1 for i in owed if i[1] == "no-mass")}


# ----------------------------------------------------------------------------- claims (proof chain)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])


@kit.calc("CALC-A4-PLAN-GRAPH", title="Interface plan graph checks",
          equation="connected = |main structural cluster| / |flight parts| ; powered = electrical parts reached from "
                   "a source / all ; field = count(edges with field_disconnect)", inputs={"n_motors": "P:propulsion.n_motors"})
def plan_graph_checks(n_motors):
    """Reads the plan defined in this file; build_graph.py re-runs it, so an edited plan without a re-run is DRIFT."""
    if len(STATIONS) != n_motors:
        raise ValueError("plan has %d motor stations, params.json says %s" % (len(STATIONS), n_motors))
    m = metrics(build_plan())
    return {"connected_frac": m["connected_frac"], "powered_frac": m["powered_frac"],
            "field_disconnects": m["field_disconnects"], "edges": m["edges"], "parts": m["parts"]}


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
kit.claim("CL-A4-PLAN-EDGES", "Planned interfaces", calc="CALC-A4-PLAN-GRAPH", output="edges", unit="-",
          how="interface_plan.py --compare: every planned edge declared and acknowledged")


# ----------------------------------------------------------------------------- rendering
def _pp(pid):
    return "`%s`" % pid


def render(plan):
    parts = {p["id"]: p for p in plan["parts"]}
    cts = library()
    m = metrics(plan)
    L = [BEGIN, "", "Generated by `python -I redesign/team/A4/interface_plan.py` from the plan in that script. Do not edit by hand.", ""]
    L += ["| Parts (flight) | Interfaces | Cross-subsystem | Connected (load path) | Powered (power wires) | Field disconnects | Plan errors | Schema blocks owed | Masses owed |",
          "|---|---|---|---|---|---|---|---|---|",
          "| %d (%d) | %d | %d | %.0f %% | %.0f %% | %d | %d | %d | %d |" % (
              m["parts"], m["flight_parts"], m["edges"], m["cross_edges"], 100 * m["connected_frac"],
              100 * m["powered_frac"], m["field_disconnects"], m["errors"], m["owed"], m["owed_mass"]), ""]
    # N2 matrix
    keys = [k for k in SUBS if k != "flight-software"]
    cnt = {}
    for e in plan["edges"]:
        a, b = parts[e["part_a"]]["subsystem"], parts[e["part_b"]]["subsystem"]
        cnt[(a, b)] = cnt.get((a, b), 0) + 1
        if a != b:
            cnt[(b, a)] = cnt.get((b, a), 0) + 1
    L += ["## N² matrix", "", "Interfaces between each pair of subsystems (diagonal: internal joints). Read a row: who this subsystem must agree with. Wires count under the two subsystems they join; harness (`HRN`) declares all 23 of them.", "",
          "| | " + " | ".join(SUBS[k][0] for k in keys) + " |", "|---|" + "---|" * len(keys)]
    for a in keys:
        L.append("| **%s** | " % SUBS[a][0] + " | ".join(str(cnt.get((a, b), "")) if cnt.get((a, b)) else "·" for b in keys) + " |")
    L += [""]
    # part ids
    L += ["## Part ids reserved", "", "One node per physical instance. Stations `UR UL LR LL` = upper/lower, right/left (`params.json#propulsion.stations.ids`).", "",
          "| Subsystem | Designer | Prefix | Parts | Ids |", "|---|---|---|---|---|"]
    for k in keys:
        ids = [p["id"] for p in plan["parts"] if p["subsystem"] == k]
        L.append("| `%s` | %s | `%s` | %d | %s |" % (k, SUBS[k][1], SUBS[k][0], len(ids), " ".join(_pp(x) for x in ids)))
    L += ["| `flight-software` | F4 | `FSW` | 0 | no parts: data interfaces below |", ""]
    # register
    L += ["## Interface register", "",
          "Declared by the owner in `subsystems/<owner>/interfaces.json`; each subsystem in *Ack* lists the id under `acknowledges`. "
          "*By* = designs · sizes. *Must carry* is in addition to the per-method block above. `OI-nn` = open issue below.", ""]
    for k in keys:
        rows = [e for e in plan["edges"] if e["owner"] == k]
        if not rows:
            continue
        L += ["### %s (%s, %d)" % (k, SUBS[k][1], len(rows)), "",
              "| Edge | Side A | Side B | Kind · method · type | Ack | By | Must carry |", "|---|---|---|---|---|---|---|"]
        for e in rows:
            ct = cts[e["via"]]
            extra = e["carries"]
            if e.get("motion"):
                extra = ("motion %s %s°; " % (e["motion"]["axis"], e["motion"]["range_deg"])) + extra
            if e.get("open"):
                extra += " (%s)" % e["open"]
            L.append("| `%s` | `%s` %s | `%s` %s | %s · %s · `%s` | %s | %s | %s |" % (
                e["id"], e["part_a"], parts[e["part_a"]]["name"], e["part_b"], parts[e["part_b"]]["name"],
                ct["kind"], ct["method"], e["via"], ", ".join(e["acknowledged_by"]) or "—", e["by"], extra.strip() or "—"))
        L.append("")
    # acknowledgements owed
    L += ["## Acknowledgements owed", "", "| Subsystem | Must list under `acknowledges` |", "|---|---|"]
    for k in keys:
        ids = [e["id"] for e in plan["edges"] if k in e["acknowledged_by"]]
        L.append("| `%s` | %s |" % (k, " ".join(_pp(x) for x in ids) or "—"))
    L += ["", "## Connection types to add to the library", "", "| Id | Kind | Method | Spec |", "|---|---|---|---|"]
    for c in NEW_CTS:
        L.append("| `%s` | %s | %s | %s |" % (c["id"], c["kind"], c["method"], c["spec"]))
    L += ["", END]
    return "\n".join(L)


def write_md(plan):
    text = PLAN_MD.read_text(encoding="utf-8")
    a, b = text.index(BEGIN), text.index(END) + len(END)
    PLAN_MD.write_text(text[:a] + render(plan) + text[b:], encoding="utf-8")


# ----------------------------------------------------------------------------- compare the real graph with the plan
def compare(plan, root=REDESIGN / "subsystems"):
    g = mc.check(mc.load(str(root)))
    parts = {p["id"]: p for p in plan["parts"]}
    planned = {e["id"]: e for e in plan["edges"]}
    pair = {frozenset((e["part_a"], e["part_b"])): e for e in plan["edges"]}
    rows = []                              # (severity, code, item, detail)
    for pid, p in parts.items():
        if pid not in g.parts:
            rows.append(("OPEN", "part-missing", pid, "%s has not declared it" % p["subsystem"]))
        elif g.parts[pid]["subsystem"] != p["subsystem"]:
            rows.append(("WARN", "part-owner", pid, "declared by %s, plan says %s" % (g.parts[pid]["subsystem"], p["subsystem"])))
    for pid in sorted(set(g.parts) - set(parts)):
        rows.append(("INFO", "unplanned", pid, "declared by %s; A4 adds it to the plan or asks why" % g.parts[pid]["subsystem"]))
    matched = set()
    for eid, e in sorted(g.edges.items()):
        pe = planned.get(eid) or pair.get(frozenset((e.get("part_a"), e.get("part_b"))))
        if pe is None:
            rows.append(("INFO", "unplanned", eid, "edge %s-%s not in the plan" % (e.get("part_a"), e.get("part_b"))))
            continue
        matched.add(pe["id"])
        if pe["id"] != eid:
            rows.append(("WARN", "edge-id", eid, "plan calls this joint %s" % pe["id"]))
        ct, pct = g.ctypes.get(e.get("via")), library()[pe["via"]]
        if ct and (ct["kind"], ct["method"]) != (pct["kind"], pct["method"]):
            rows.append(("WARN", "edge-type", eid, "declared %s/%s, plan %s/%s: owner states why in notes" % (
                ct["kind"], ct["method"], pct["kind"], pct["method"])))
        if e.get("owner") != pe["owner"]:
            rows.append(("WARN", "edge-owner", eid, "owner %s, plan %s" % (e.get("owner"), pe["owner"])))
        meth = ct["method"] if ct else pct["method"]
        for block, methods in A4_BLOCKS.items():
            if meth in methods and not e.get(block):
                rows.append(("OWED", "data", eid, "%s block missing (%s)" % (block, REQUIRED[meth][1])))
        if meth == "clamped" and not e.get("joint_stack"):
            rows.append(("OWED", "data", eid, "joint_stack for the clamp screws missing"))
        if ct and ct["kind"] == "electrical" and not (e.get("current_a") or e.get("signal")):
            rows.append(("OWED", "data", eid, "current_a or signal block missing"))
        if meth == "hinged" and "clearance_mm" not in e:
            rows.append(("OWED", "data", eid, "clearance_mm at the stops missing"))
    for eid in sorted(set(planned) - matched):
        rows.append(("OPEN", "edge-missing", eid, "%s has not declared it" % planned[eid]["owner"]))
    return g, rows


def write_status(plan, g, rows):
    order = {"WARN": 0, "OWED": 1, "OPEN": 2, "INFO": 3}
    n = lambda s: sum(1 for r in rows if r[0] == s)
    me = sum(1 for i in g.issues if i[0] == "ERROR")
    mw = sum(1 for i in g.issues if i[0] == "WARN")
    L = ["# Interface plan status", "",
         "Generated by `python -I redesign/team/A4/interface_plan.py --compare`. Do not edit by hand.", "",
         "| Planned edges | Declared (matched) | Missing | Unplanned | Data owed | Deviations | merge_check errors / warnings |",
         "|---|---|---|---|---|---|---|",
         "| %d | %d | %d | %d | %d | %d | %d / %d |" % (
             len(plan["edges"]), len(plan["edges"]) - sum(1 for r in rows if r[1] == "edge-missing"),
             sum(1 for r in rows if r[1] == "edge-missing"), n("INFO"), n("OWED"), n("WARN"), me, mw), "",
         "| Severity | Check | Item | Detail |", "|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (order[r[0]], r[1], r[2])):
        L.append("| %s | %s | `%s` | %s |" % r)
    STATUS_MD.write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv):
    plan = build_plan()
    PLAN_JSON.write_text(mc.dump_lines(plan), encoding="utf-8")
    g, errors, owed = check_plan(plan)
    m = metrics(plan)
    write_md(plan)
    kit.write()
    for sev, code, item, msg in errors:
        print("  %-5s %-16s %-14s %s" % (sev, code, item, msg))
    print("interface_plan: %d parts (%d flight), %d edges (%d cross-subsystem), connected %.0f %%, powered %.0f %%, "
          "field disconnects %d, schema data blocks owed %d, masses owed %d -> %s" % (
              m["parts"], m["flight_parts"], m["edges"], m["cross_edges"], 100 * m["connected_frac"],
              100 * m["powered_frac"], m["field_disconnects"], m["owed"], m["owed_mass"], "FAIL" if errors else "PASS"))
    if "--compare" in argv:
        gg, rows = compare(plan)
        write_status(plan, gg, rows)
        print("compare: %d sources; %d missing edges, %d owed data blocks, %d deviations, %d unplanned -> %s" % (
            len(gg.sources), sum(1 for r in rows if r[1] == "edge-missing"), sum(1 for r in rows if r[0] == "OWED"),
            sum(1 for r in rows if r[0] == "WARN"), sum(1 for r in rows if r[0] == "INFO"),
            os.path.relpath(STATUS_MD, REDESIGN).replace("\\", "/")))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
