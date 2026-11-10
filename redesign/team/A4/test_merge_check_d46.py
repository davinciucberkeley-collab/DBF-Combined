"""Seeded test of the D-46 changes A4 made to redesign/interfaces/merge_check.py (CR-A4-15a, CR-A1-38).

Each case builds a tiny graph in memory, runs merge_check.check() and asserts one rule:
  1. a harness-owned wire raises no 'owner' warning; a non-harness edge whose owner holds neither side still does;
  2. a part flagged "carried" held only by a "structural": false type (tie) is not floating;
  3. a tie does not join two structural groups (the group it would join still floats);
  4. power is followed part_a -> part_b: a wire declared backwards leaves its load unpowered;
  5. a signal-only lead does not power its load;
  6. a radio link needs no wire block and does not power the receiver;
  7. a radio link between ground equipment and an aircraft part raises no 'electrical role' warning.

Run (repo root):  python -I redesign/team/A4/test_merge_check_d46.py      (exit 1 on any failure)
"""
import sys
from pathlib import Path

REDESIGN = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REDESIGN / "interfaces"))
import merge_check as mc  # noqa: E402

CTS = [
    {"id": "CT-EPOXY", "kind": "mechanical", "method": "bonded", "spec": "epoxy"},
    {"id": "CT-TIE", "kind": "mechanical", "method": "strapped", "spec": "tie", "structural": False},
    {"id": "CT-SOLDER-DC", "kind": "electrical", "method": "soldered", "spec": "solder"},
    {"id": "CT-SERVO-JR", "kind": "electrical", "method": "connector", "spec": "JR"},
    {"id": "CT-ELRS-RF", "kind": "electrical", "method": "radio", "spec": "radio"},
]
WIRE = {"gauge_awg": 16, "connector": "-", "route_id": "R-1", "support_points": ["-"], "bend_radius_mm": 10,
        "strain_relief": "-", "disconnect": False}


def part(pid, sub, elec=None, flight=True, carried=False):
    p = {"id": pid, "name": pid, "subsystem": sub, "status": "PROPOSED", "mass_g": 10, "material": "-",
         "cg_xyz_m": None, "make_or_buy": "make"}
    if carried:
        p["carried"] = True
    if elec:
        p["electrical"] = elec
    if not flight:
        p["flight"] = False
    return p


def edge(eid, a, b, via, owner, **kw):
    e = {"id": eid, "part_a": a, "part_b": b, "via": via, "owner": owner, "notes": "", "_src": "t", "_sub": owner}
    if via in ("CT-SOLDER-DC", "CT-SERVO-JR"):
        e["wire"] = WIRE
    e.update(kw)
    return e


def graph(parts, edges):
    g = mc.Graph()
    for c in CTS:
        mc._add_ctype(g, c, "test")
    for p in parts:
        g.parts[p["id"]] = dict(p, _src="t")
    for e in edges:
        g.edges[e["id"]] = e
        for s in ("part_a", "part_b"):
            sub = g.parts[e[s]]["subsystem"]
            if sub != e["owner"]:
                g.acks.setdefault(sub, set()).add(e["id"])
    return mc.check(g)


def issues(g, code):
    return {i[2] for i in g.issues if i[1] == code}


def base():
    parts = [part("WNG-001", "wing"), part("POD-001", "pod"), part("PWR-001", "power", "source"),
             part("PWR-004", "power", "bus"), part("PRP-002", "propulsion", "bus"), part("AVN-001", "avionics", "sink"),
             part("AVN-003", "avionics", "sink"), part("PRP-001", "propulsion", "sink"),
             part("HRN-001", "harness", carried=True), part("GND-001", "ground", flight=False)]
    edges = [edge("E-POD-01", "POD-001", "WNG-001", "CT-EPOXY", "pod"),
             edge("E-POD-05", "PWR-001", "POD-001", "CT-EPOXY", "pod"),
             edge("E-PWR-03", "PWR-004", "POD-001", "CT-EPOXY", "power"),
             edge("E-AVN-01", "AVN-001", "POD-001", "CT-EPOXY", "avionics"),
             edge("E-AVN-03", "AVN-003", "POD-001", "CT-EPOXY", "avionics"),
             edge("E-FIN-65", "PRP-002", "WNG-001", "CT-EPOXY", "propulsion"),
             edge("E-FIN-61", "PRP-001", "WNG-001", "CT-EPOXY", "propulsion"),
             edge("E-HRN-01", "HRN-001", "POD-001", "CT-TIE", "harness"),
             edge("E-HRN-12", "PWR-001", "PWR-004", "CT-SOLDER-DC", "harness"),
             edge("E-HRN-13", "PWR-004", "PRP-002", "CT-SOLDER-DC", "harness"),
             edge("E-HRN-17", "PRP-002", "PRP-001", "CT-SOLDER-DC", "harness"),
             edge("E-HRN-22", "PWR-004", "AVN-001", "CT-SOLDER-DC", "harness"),
             edge("E-HRN-31", "AVN-001", "AVN-003", "CT-SERVO-JR", "harness"),
             edge("E-AVN-09", "GND-001", "AVN-003", "CT-ELRS-RF", "avionics")]
    return parts, edges


def replace(edges, eid, **kw):
    return [dict(e, **kw) if e["id"] == eid else e for e in edges]


def drop(edges, *ids):
    return [e for e in edges if e["id"] not in ids]


def main():
    P, E = base()
    g0 = graph(P, E)
    cases = [
        ("baseline: no warnings or errors", not g0.issues),
        ("1 harness-owned wires raise no 'owner' warning", not issues(g0, "owner")),
        ("1 a non-harness edge whose owner holds neither side still warns",
         "E-POD-05" in issues(graph(P, replace(E, "E-POD-05", owner="landing", _sub="landing")), "owner")),
        ("2 harness bundle held only by a tie is a carried item, not floating", not issues(g0, "floating")),
        ("3 a tie does not hold the pack on: strap cut, pack tied to the pod -> pack floats (no carried flag)",
         "PWR-001" in issues(graph(P, drop(E, "E-POD-05") + [edge("E-HRN-02", "PWR-001", "POD-001", "CT-TIE", "harness")]),
                             "floating")),
        ("3 the same tie on a part without the flag: bundle unflagged -> floats",
         "HRN-001" in issues(graph([dict(q, carried=False) for q in P], E), "floating")),
        ("4 ESC lead declared backwards (load as part_a) -> ESC and motor unpowered",
         {"PRP-002", "PRP-001"} <= issues(graph(P, replace(E, "E-HRN-13", part_a="PRP-002", part_b="PWR-004")), "unpowered")),
        ("5 FC fed only by a signal-only lead -> unpowered",
         "AVN-001" in issues(graph(P, replace(E, "E-HRN-22", signal_only=True)), "unpowered")),
        ("6 radio link: no wire block demanded", not issues(g0, "wire")),
        ("6 radio link does not power the receiver: FC lead cut -> receiver unconnected",
         "AVN-003" in issues(graph(P, drop(E, "E-HRN-31")), "unconnected")),
        ("7 ground transmitter on a radio link raises no electrical-role warning", not issues(g0, "electrical")),
    ]
    bad = 0
    for name, ok in cases:
        bad += not ok
        print("  %-4s %s" % ("ok" if ok else "FAIL", name))
    if g0.issues:
        print("  baseline issues:", g0.issues)
    print("test_merge_check_d46: %s (%d cases, %d failed)" % ("PASS" if not bad else "FAIL", len(cases), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
