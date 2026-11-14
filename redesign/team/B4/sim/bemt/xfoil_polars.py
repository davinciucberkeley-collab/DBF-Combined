"""XFOIL polars of the blade section for the B4 blade-element model (sim/bemt/bemt.py).

APC thin-electric / multirotor blades use a thin cambered section close to NACA 4412 / Clark-Y over the outer blade
(the BEMT literature on APC props uses one of these; UIUC publishes chord and twist only). We run NACA 4412 as the
baseline and NACA 4409 as the thin-section sensitivity, at the blade Reynolds numbers of interest
(Re_0.75R = 4e4..2e5 for 4 000..9 000 rpm), Ncrit 5 (rotor blades see a turbulent, unsteady inflow).

Run: python -I redesign/team/B4/sim/bemt/xfoil_polars.py   (~1 min) -> polars.json beside this file
"""
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
XFOIL = Path("C:/Users/dillo/tools/xfoil/xfoil.exe")
RES = [30000, 50000, 80000, 120000, 200000]
FOILS = {"naca4412": "NACA 4412", "naca4409": "NACA 4409", "naca3410": "NACA 3410", "naca2410": "NACA 2410"}
NCRIT = 5


def run(foil, re):
    with tempfile.TemporaryDirectory() as td:
        out = []
        for seq in (("0", "18"), ("0", "-8")):            # two sweeps from 0 so each starts converged
            p = Path(td) / f"p{seq[1]}.txt"
            cmds = ["PLOP", "G F", "", FOILS[foil], "PPAR", "N 200", "", "", "OPER", f"VISC {re}", "VPAR",
                    f"N {NCRIT}", "", "ITER 300", "PACC", p.name, "", f"ASEQ {seq[0]} {seq[1]} {0.5 if seq[1] == '18' else -0.5}",
                    "PACC", "", "QUIT"]
            subprocess.run([str(XFOIL)], input="\n".join(cmds) + "\n", text=True, capture_output=True, cwd=td,
                           timeout=300)
            if p.exists():
                for line in p.read_text().splitlines()[12:]:
                    s = line.split()
                    if len(s) >= 5:
                        out.append((float(s[0]), float(s[1]), float(s[2])))
        out = sorted({round(a, 2): (a, cl, cd) for a, cl, cd in out}.values())
        return out


def main():
    data = {"_note": "XFOIL 6.x, Ncrit %d, 200 panels; rows alpha_deg, cl, cd (converged points only)" % NCRIT,
            "foils": {}}
    for foil in FOILS:
        data["foils"][foil] = {}
        for re in RES:
            pts = run(foil, re)
            data["foils"][foil][str(re)] = pts
            amax = max(pts, key=lambda r: r[1]) if pts else None
            print(foil, re, len(pts), "pts", "clmax %.3f at %.1f" % (amax[1], amax[0]) if amax else "")
    (HERE / "polars.json").write_text(json.dumps(data, indent=0), encoding="utf-8")


if __name__ == "__main__":
    main()
