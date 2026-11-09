"""Seeded-fault self-test for interface_plan.py: the plan is clean, and each injected fault is caught.

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


def codes(plan):
    return {(i[1], i[2]) for i in ip.check_plan(plan)[1]}


def main():
    base = ip.build_plan()
    cases = [
        ("baseline is clean", base, lambda c: not c),
        ("pack strap removed -> pack floats", without(base, "E-POD-05"), lambda c: ("floating", "PWR-001") in c),
        ("fin L held only by harness ties -> load path",
         without(base, "E-FIN-01", "E-FIN-07", "E-FIN-08", "E-FIN-09"),
         lambda c: any(k == "load-path" and "FIN-001-L" in item for k, item in c)),
        ("power module -> PDB cut -> ESCs unpowered (not fed back through UBEC/FC)", without(base, "E-HRN-12"),
         lambda c: ("power-path", "PRP-002-UR") in c and ("power-path", "PWR-004") in c),
        ("ESC UR power lead cut -> ESC UR unpowered although its signal lead exists", without(base, "E-HRN-13"),
         lambda c: ("power-path", "PRP-002-UR") in c),
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
