"""B1 design round 2026-11-14: XFOIL check of fin-board edge treatments (scratch-level evidence, writes only here).

Section: 9.6 mm board (fins.board_t_m x fins.layers) on the 0.275 m fin chord (t/c 3.49 %), semicircular LE.
TE: blunt (9.6 mm base, as built) or a straight bevel over the last 55 mm (or 30 mm) down to 1 mm.
Fully turbulent like the SU2 fin runs: transition forced at 2 % c both sides. alpha 0 and 0.5 deg.
Re 2.9e5 (16 m/s) and 3.2e5 (17 m/s) on the fin chord (nu 1.48e-5 m2/s, ASM-B2-NU).
Run:  python -I redesign/team/B1/round-2026-11-14/xf_fin_edges.py   (needs C:/Users/dillo/tools/xfoil/xfoil.exe)
"""
import json, math, os, re, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = HERE / "xfoil"
XF = Path("C:/Users/dillo/tools/xfoil/xfoil.exe")          # same executable as team/B1/vlm_xfoil.py
C, T = 0.275, 0.0096
NUM = re.compile(r"^\s+-?\d+\.\d+\s+-?\d")


def section(te_mode, bevel_len=0.055, te_t=0.001):
    t = T / C
    r = t / 2
    xb = 1.0 - (bevel_len / C if te_mode == "bevel" else 0.0)
    tt = te_t / C if te_mode == "bevel" else t
    up = []
    for i in range(121):
        x = 1.0 - i / 120 * (1.0 - r)
        y = tt / 2 + (r - tt / 2) * (1.0 - x) / (1.0 - xb) if (xb < 1.0 and x >= xb) else r
        up.append((x, y))
    for i in range(1, 41):
        a = math.pi / 2 * i / 40
        up.append((r - r * math.sin(a), r * math.cos(a)))
    return up + [(x, -y) for x, y in reversed(up[:-1])]


def run(name, pts, re_):
    tag = f"{name}_re{re_/1e5:.1f}e5"
    dat, pol = OUT / f"{tag}.dat", OUT / f"{tag}.pol"
    dat.write_text(name + "\n" + "".join(f"{x:.6f} {y:.6f}\n" for x, y in pts))
    if pol.exists():
        pol.unlink()
    cmds = (f"PLOP\nG F\n\nLOAD {dat.name}\nPPAR\nN 240\n\n\nOPER\nVISC {re_:.0f}\nVPAR\nXTR 0.02 0.02\nN 9\n\n"
            f"ITER 300\nPACC\n{pol.name}\n\nALFA 0\nALFA 0.5\n\nQUIT\n")
    subprocess.run([str(XF)], input=cmds, capture_output=True, text=True, timeout=180, cwd=OUT)
    rows = [l.split() for l in pol.read_text().splitlines() if NUM.match(l)] if pol.exists() else []
    return [{"alpha": float(r[0]), "cl": float(r[1]), "cd": float(r[2]), "cdp": float(r[3])} for r in rows]


if __name__ == "__main__":
    res = {"_note": "Written by xf_fin_edges.py. cd on the fin chord; xtr 0.02 both sides.", "cases": {}}
    for nm, sec in [("blunt", section("blunt")), ("bevel55", section("bevel", 0.055)), ("bevel30", section("bevel", 0.030))]:
        for re_ in (2.9e5, 3.2e5):
            res["cases"][f"{nm}_{re_:.0f}"] = run(nm, sec, re_)
            print(nm, re_, res["cases"][f"{nm}_{re_:.0f}"])
    (HERE / "xf_fin_edges_results.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
