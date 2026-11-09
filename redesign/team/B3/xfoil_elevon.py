"""B3: XFOIL check of the two section inputs the trim analysis needs (B2 owns the airfoil and replaces these).

  1. viscous cm of the MH 45 vs thin-airfoil theory on its camber line  -> ASM-B3-DCM-VISC
  2. elevon (plain flap, hinge 0.78 c) lift effectiveness vs thin-airfoil theory -> ASM-B3-FLAP-EFF

Run: python -I redesign/team/B3/xfoil_elevon.py   (needs C:/Users/dillo/tools/xfoil/xfoil.exe; ~1 min)
Writes team/B3/xfoil/polar_d<deg>.txt and team/B3/xfoil/summary.json. Re 3e5, Ncrit 9, alpha -4..14 deg.
"""
import json
import math
import subprocess
import tempfile
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
XFOIL = Path("C:/Users/dillo/tools/xfoil/xfoil.exe")
OUT = HERE / "xfoil"
AF = HERE / "avl" / "mh45.dat"
HINGE = 0.78
RE = 3.0e5
FLAPS = [0, 5, 10, -5, -10, -15, -20]


def run(defl):
    tmp = Path(tempfile.mkdtemp(prefix="b3xf_"))
    try:
        shutil.copy(AF, tmp / "af.dat")
        cmds = ["PLOP", "G F", "", "LOAD af.dat", "PANE", "GDES", "FLAP", f"{HINGE}", "999", "0.5", f"{defl}", "X",
                "EXEC", "", "OPER", f"VISC {RE:.0f}", "ITER 200", "PACC", "p.txt", "", "ASEQ -4 14 1", "PACC", "",
                "QUIT"]
        subprocess.run([str(XFOIL)], input="\n".join(cmds) + "\n", text=True, capture_output=True, cwd=str(tmp),
                       timeout=180)
        txt = (tmp / "p.txt").read_text()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    (OUT / f"polar_d{defl:+d}.txt").write_text(txt)
    rows = []
    for line in txt.splitlines()[12:]:
        p = line.split()
        if len(p) >= 5:
            rows.append([float(p[0]), float(p[1]), float(p[2]), float(p[4])])   # alpha, cl, cd, cm
    return rows


def thin_cm_c4(path):
    """Thin-airfoil cm c/4 of the camber line: pi/4 (A2 - A1)."""
    pts = [tuple(map(float, l.split())) for l in path.read_text().splitlines()[1:] if l.strip()]
    i = min(range(len(pts)), key=lambda k: pts[k][0])
    up, lo = pts[:i + 1][::-1], pts[i:]

    def interp(arr, x):
        for (x0, z0), (x1, z1) in zip(arr, arr[1:]):
            if x0 <= x <= x1:
                return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
        return arr[-1][1]
    N = 4000
    A = {1: 0.0, 2: 0.0}
    for k in range(1, N):
        th0, th1 = math.pi * (k - 1) / N, math.pi * k / N
        th = 0.5 * (th0 + th1)
        xa, xb = (1 - math.cos(th0)) / 2, (1 - math.cos(th1)) / 2
        za = 0.5 * (interp(up, xa) + interp(lo, xa))
        zb = 0.5 * (interp(up, xb) + interp(lo, xb))
        dz = (zb - za) / max(xb - xa, 1e-12)
        for n in A:
            A[n] += 2 / math.pi * dz * math.cos(n * th) * (th1 - th0)
    return math.pi / 4 * (A[2] - A[1])


def at(rows, alpha):
    for r in rows:
        if abs(r[0] - alpha) < 1e-6:
            return r
    return None


def main():
    OUT.mkdir(exist_ok=True)
    pol = {d: run(d) for d in FLAPS}
    cm_thin = thin_cm_c4(AF)
    base = [r for r in pol[0] if 0.3 <= r[1] <= 0.7]
    cm_visc = sum(r[3] for r in base) / len(base)
    # thin-airfoil flap lift effectiveness for a plain flap at HINGE
    th = math.acos(1 - 2 * HINGE)
    dcl_thin = 2 * math.pi * (1 - (th - math.sin(th)) / math.pi) * math.pi / 180     # per deg
    eff = {}
    for d in FLAPS:
        if d == 0:
            continue
        vals = []
        for a in (4.0, 5.0, 6.0):
            r0, r1 = at(pol[0], a), at(pol[d], a)
            if r0 and r1:
                vals.append((r1[1] - r0[1]) / d / dcl_thin)
        if vals:
            eff[str(d)] = sum(vals) / len(vals)
    up = [eff[k] for k in eff if int(k) < 0]
    clmax = max(r[1] for r in pol[0])
    summ = {"Re": RE, "hinge_xc": HINGE, "cm_thin_c4": cm_thin, "cm_visc_mean_cl_0.3_0.7": cm_visc,
            "dcm_visc": cm_visc - cm_thin, "dcl_ddelta_thin_per_deg": dcl_thin, "flap_eff_by_deflection": eff,
            "flap_eff_up_mean": sum(up) / len(up), "clmax_2d_clean": clmax,
            "note": "Laminar-bubble noise at Re 3e5 makes single points unreliable; B2 re-runs with finer alpha steps"}
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
