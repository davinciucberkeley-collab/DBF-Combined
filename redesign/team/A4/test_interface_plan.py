"""Seeded-fault self-test for interface_plan.py (plan A4-R3): the plan is clean, and each injected fault is caught.

Run (repo root):  python -I redesign/team/A4/test_interface_plan.py      (exit 1 on any miss)
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import interface_plan as ip  # noqa: E402


def without(plan, *ids):
    p = copy.deepcopy(plan)
    p["edges"] = [e for e in p["edges"] if e["id"] not in ids]
    return p


def with_part(plan, pid, sub):
    """Add a part tied by one bond to the core, so only the id rule can object to it."""
    p = copy.deepcopy(plan)
    p["parts"].append({"id": pid, "name": "seeded", "subsystem": sub, "make_or_buy": "make"})
    p["edges"].append({"id": "E-FIN-99", "part_a": pid, "part_b": "WNG-001", "via": "CT-EPOXY", "owner": sub,
                       "by": "", "carries": "", "acknowledged_by": ["wing"]})
    return p


def uncarried(plan, pid):
    p = copy.deepcopy(plan)
    for q in p["parts"]:
        if q["id"] == pid:
            q.pop("carried", None)
    return p


def codes(plan):
    return {(i[1], i[2]) for i in ip.check_plan(plan)[1]}


def main():
    base = ip.build_plan()
    cases = [
        ("baseline is clean", base, lambda c: not c),
        ("pack strap removed -> pack floats (its thermal edge does not hold it)", without(base, "E-POD-05"),
         lambda c: ("floating", "PWR-001") in c),
        ("tube L cut from block and both collars -> tube, mounts, motors reach the aircraft only by harness ties",
         without(base, "E-FIN-02", "E-FIN-14", "E-FIN-16"),
         lambda c: any(k == "load-path" and "FIN-002-L" in item for k, item in c)),
        ("shoe LR bond to the half-fin cut -> foot LR group floats", without(base, "E-GER-03"),
         lambda c: any(k == "floating" and "GER-001-LR" in item for k, item in c)),
        ("harness bundle without the carried flag -> held only by ties, load path", uncarried(base, "HRN-001"),
         lambda c: ("load-path", "HRN-001") in c),
        ("skeleton id FIN-901 in the plan -> id rule", with_part(base, "FIN-901", "fins"),
         lambda c: ("id-rule", "FIN-901") in c),
        ("retired id FIN-001-L reused -> id rule", with_part(base, "FIN-001-L", "fins"),
         lambda c: ("id-retired", "FIN-001-L") in c),
        ("FIN-003 with both station and side suffixes -> id rule", with_part(base, "FIN-003-L", "fins"),
         lambda c: ("id-rule", "FIN-003") in c),
        ("face letter other than I/O (FIN-011-URX) -> id rule", with_part(base, "FIN-011-URX", "fins"),
         lambda c: ("id-rule", "FIN-011-URX") in c),
        ("letter suffix A (as TRN-006-A was declared) -> id rule", with_part(base, "TRN-009-A", "transport"),
         lambda c: ("id-rule", "TRN-009-A") in c),
        ("power module -> PDB cut -> ESCs unpowered (not fed back through UBEC/FC)", without(base, "E-HRN-12"),
         lambda c: ("power-path", "PRP-002-UR") in c and ("power-path", "PWR-004") in c),
        ("ESC UR power lead cut -> ESC UR unpowered although its signal lead exists", without(base, "E-HRN-13"),
         lambda c: ("power-path", "PRP-002-UR") in c),
        ("FC -> receiver lead cut -> receiver unpowered although the radio link exists", without(base, "E-HRN-31"),
         lambda c: ("power-path", "AVN-003") in c),
        ("pack plug removed -> no field disconnect", without(base, "E-HRN-10"),
         lambda c: ("field-disconnect", "plan") in c),
    ]
    bad = 0
    for name, plan, ok in cases:
        passed = ok(codes(plan))
        bad += not passed
        print("  %-4s %s" % ("ok" if passed else "MISS", name))
    print("test_interface_plan: %s (%d cases, %d missed)" % ("PASS" if not bad else "FAIL", len(cases), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
