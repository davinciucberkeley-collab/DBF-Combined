"""B2-R3: XFOIL with transition forced at 2 % chord on both surfaces, the like-for-like reference for the fully
turbulent SU2 runs (cfd2d_section.py). Same section, panelling and elevon hinge as xfoil_wing.py.

    python -I redesign/team/B2/sim/xfoil_tripped.py     -> team/B2/sim/out/xfoil_tripped.json   (~5 min: above 9.5 deg the tripped case stops converging and the sweep runs to the XFOIL timeout,
                                                                 so clmax_tripped is the last converged point, a lower bound)

Cases: clean S5010 at the stall Re (alpha 0..16 deg), free (Ncrit 9) and tripped, so the SU2-vs-XFOIL lift gap
can be split into "transition" and "solver". (A tripped elevon -25 deg hinge case was tried and did not converge in
XFOIL (one point, 10x the inviscid value) and was dropped; the hinge comparison uses the free-transition viscous and inviscid cases of xfoil_wing.py.)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
B2 = HERE.parent
sys.argv = [sys.argv[0]]
spec = importlib.util.spec_from_file_location("xfoil_wing", B2 / "xfoil_wing.py")
XW = importlib.util.module_from_spec(spec)
spec.loader.exec_module(XW)
CFD = importlib.util.spec_from_file_location("cfd2d_section", HERE / "cfd2d_section.py")
XTR = 0.02


def tripped_polar(re_, flap=0.0, amax=16.0, da=0.5):
    f = XW.OUT / f"raw_trip_s5010_re{re_/1e5:.1f}e5_f{flap:+g}.txt"
    if f.exists():
        f.unlink()
    cmd = XW.geom("s5010", flap, XW.NPAN) + f"OPER\nVISC {re_:.0f}\nITER 200\nVPAR\nXTR {XTR} {XTR}\n\nPACC\n{f.name}\n\n"
    cmd += f"ASEQ 0 {amax} {da}\nPACC\n\nQUIT\n"
    XW.run(cmd)
    return XW.parse_polar(f).tolist()


def main():
    m = importlib.util.module_from_spec(CFD)
    CFD.loader.exec_module(m)
    res = {"xtr": XTR, "re_stall": m.RE_STALL, "re_va": m.RE_VA,
           "clean_tripped": tripped_polar(m.RE_STALL)}
    t = res["clean_tripped"]
    res["clmax_tripped"] = max(r[1] for r in t) if t else None
    res["alpha_clmax_tripped"] = max(t, key=lambda r: r[1])[0] if t else None
    (HERE / "out" / "xfoil_tripped.json").write_text(json.dumps(res, indent=1))
    print("tripped clmax", res["clmax_tripped"], "at", res["alpha_clmax_tripped"])
    for r in t:
        if r[0] in (4.0, 8.0, 10.0, 12.0, 14.0):
            print("  a", r[0], "cl", r[1], "cd", r[2])


if __name__ == "__main__":
    main()
