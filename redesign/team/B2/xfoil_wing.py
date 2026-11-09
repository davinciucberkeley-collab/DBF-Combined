"""B2 wing aero: XFOIL 6.99 polars, elevon effectiveness and hinge moments for the K09-L wing section.

Run from the repo root (about 3-6 min, runs XFOIL in parallel):
    python -I redesign/team/B2/xfoil_wing.py            # cached cases are re-used when inputs are unchanged
    python -I redesign/team/B2/xfoil_wing.py --force    # re-run every case

Inputs: redesign/params/params.json (chord, elevon chord fraction, rho), airfoils/*.dat (UIUC coordinates).
Cases (Re = V c / nu, c = params wing.chord_m, nu = 1.48e-5 m2/s at 15 degC sea level). The three design Re
follow the chord (rounded to 0.1e5): stall RE_STALL at requirements.stall_max_ms, cruise RE_CRUISE at
performance.cruise_ms, dive RE_DIVE at 1.3 x cruise. c 0.32 m: 2.6e5 / 3.5e5 / 4.5e5 (c 0.30 m was 2.3/3.0/4.0e5).
  A  candidates MH 45, MH 60, S5010, E186 at Re 2.0/2.3/3.0/4.0e5 + the three design Re, Ncrit 9; Ncrit 5 at RE_STALL
  B  every candidate with a 22 % elevon (hinge on the upper surface) at -15..+10 deg, RE_STALL and RE_CRUISE
  C  MH 45 and S5010 hinge moments, elevon -25..+25 deg, alpha -4..8 deg, RE_DIVE, viscous and inviscid
  N  negative stall (CLmin) S5010 and MH 45, RE_CRUISE, alpha -16..4 deg
  G  panel-count convergence MH 45, RE_CRUISE: 160 / 220 / 300 panels
Outputs: out/xfoil/*.txt (raw polars and logs), out/xfoil_results.json. Plots: plots_wing.py.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
OUT = HERE / "out" / "xfoil"
OUT.mkdir(parents=True, exist_ok=True)
XFOIL = Path("C:/Users/dillo/tools/xfoil/xfoil.exe")
P = json.loads((REDESIGN / "params" / "params.json").read_text(encoding="utf-8"))
CHORD = P["wing"]["chord_m"]["value"]
EF = P["wing"]["elevon"]["chord_frac"]["value"]
X_HINGE = 1.0 - EF                     # hinge line x/c
HINGE_YT = 0.9                         # hinge at 90 % of local thickness (tape hinge on the upper skin)
NU = 1.48e-5                           # m2/s, 15 degC sea level (ISA mu 1.79e-5 / rho 1.225); ASM-B2-NU
FOILS = ["mh45", "mh60", "s5010", "e186"]
V_STALL = P["requirements"]["stall_max_ms"]["value"]
V_CRUISE = P["performance"]["cruise_ms"]["value"]
DIVE_FACTOR = 1.3                      # ASM-B2-DIVE-FACTOR
RE_STALL, RE_CRUISE, RE_DIVE = (round(V * CHORD / NU / 1e4) * 1e4
                                for V in (V_STALL, V_CRUISE, DIVE_FACTOR * V_CRUISE))
RES = sorted({2.0e5, 2.3e5, 3.0e5, 4.0e5, RE_STALL, RE_CRUISE, RE_DIVE})
FLAPS = [-15.0, -10.0, -5.0, 0.0, 5.0, 10.0]
HM_FLAPS = [-25.0, -20.0, -15.0, -10.0, -5.0, 5.0, 10.0, 15.0, 20.0, 25.0]
HM_ALPHAS = [-4.0, -2.0, 0.0, 2.0, 4.0, 6.0, 8.0]
HM_FOILS = ["mh45", "s5010"]          # baseline and the recommended section
FORCE = "--force" in sys.argv
NPAN = 220


def run(cmds: str, timeout=240) -> str:
    try:
        p = subprocess.run([str(XFOIL)], input=cmds, text=True, capture_output=True, cwd=str(OUT), timeout=timeout)
        return p.stdout
    except subprocess.TimeoutExpired as e:
        so = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return so + "\n*** TIMEOUT ***\n"


def geom(foil, flap, npan):
    s = f"PLOP\nG\n\nLOAD ../../airfoils/{foil}.dat\nPPAR\nN {npan}\n\n\n"
    if flap:
        s += f"GDES\nFLAP\n{X_HINGE:.4f}\n999\n{HINGE_YT}\n{flap}\nX\n\nPANE\n"
    return s


def parse_polar(path: Path):
    rows, started = [], False
    if not path.exists():
        return np.zeros((0, 7))
    for line in path.read_text().splitlines():
        if re.match(r"\s*-+\s+-+", line):
            started = True
            continue
        if started:
            v = line.split()
            if len(v) >= 7:
                try:
                    rows.append([float(x) for x in v[:7]])
                except ValueError:
                    pass
    a = np.array(rows) if rows else np.zeros((0, 7))
    if len(a):
        a = a[np.argsort(a[:, 0])]
        _, i = np.unique(a[:, 0], return_index=True)
        a = a[i]
    return a


def polar(foil, re_, ncrit=9.0, flap=0.0, npan=NPAN, amin=-6.0, amax=16.0, da=0.5):
    """Merged +/- alpha sweeps (each from 0 in its own process so a hang on one side keeps the other)."""
    tag = f"{foil}_re{re_/1e5:.1f}e5_n{ncrit:g}_f{flap:+g}_p{npan}" + ("" if amin == -6.0 else f"_neg{abs(amin):g}")
    out = OUT / f"pol_{tag}.txt"
    key = OUT / f"pol_{tag}.key"
    want = f"{foil} Re={re_:.0f} ncrit={ncrit} flap={flap} xh={X_HINGE:.4f} yt={HINGE_YT} npan={npan} a={amin},{amax},{da}"
    if out.exists() and key.exists() and key.read_text().strip() == want and not FORCE:
        return tag, np.loadtxt(out, ndmin=2)
    res = []
    for side, a1, step in (("p", amax, da), ("n", amin, -da)):
        f = OUT / f"raw_{tag}_{side}.txt"
        if f.exists():
            f.unlink()
        cmd = geom(foil, flap, npan) + f"OPER\nVISC {re_:.0f}\nITER 200\nVPAR\nN {ncrit}\n\nPACC\n{f.name}\n\n"
        cmd += f"ASEQ 0 {a1} {step}\nPACC\n\nQUIT\n"
        log = run(cmd)
        (OUT / f"log_{tag}_{side}.txt").write_text(log[-20000:])
        res.append(parse_polar(f))
    a = np.vstack(res)
    if len(a):
        a = a[np.argsort(a[:, 0])]
        _, i = np.unique(a[:, 0], return_index=True)
        a = a[i]
    np.savetxt(out, a, fmt="%10.5f", header="XFOIL 6.99: alpha CL CD CDp Cm xtr_top xtr_bot")
    key.write_text(want + "\n")
    return tag, a


def hinge_case(foil, re_, flap, visc=True, npan=NPAN):
    """Hinge moment coefficient HMOM/(q c^2) at each alpha in HM_ALPHAS (FMOM; NaN where unconverged)."""
    tag = f"hm_{foil}_re{re_/1e5:.1f}e5_f{flap:+g}_{'v' if visc else 'i'}"
    out = OUT / f"{tag}.json"
    want = f"{foil} Re={re_:.0f} flap={flap} visc={visc} xh={X_HINGE:.4f} yt={HINGE_YT} npan={npan} a={HM_ALPHAS}"
    if out.exists() and not FORCE:
        d = json.loads(out.read_text())
        if d.get("key") == want:
            return tag, d
    cmd = geom(foil, flap, npan) + "OPER\n" + (f"VISC {re_:.0f}\nITER 200\n" if visc else "")
    for a in HM_ALPHAS:
        cmd += f"ALFA {a}\nFMOM\n"
    cmd += "\nQUIT\n"
    log = run(cmd)
    (OUT / f"log_{tag}.txt").write_text(log[-40000:])
    # split the log at each FMOM output; a block is converged unless XFOIL said so
    blocks = re.split(r"Flap hinge x,y", log)[1:]
    ch, cl, conv = [], [], []
    pre = log.split("Flap hinge x,y")
    for i, b in enumerate(blocks):
        m = re.search(r"Hinge moment/span =\s*([-+0-9.Ee]+)", b)
        ch.append(float(m.group(1)) if m else float("nan"))
        cls = re.findall(r"CL =\s*([-+0-9.Ee]+)", pre[i])
        cl.append(float(cls[-1]) if cls else float("nan"))
        conv.append(("Convergence failed" not in pre[i]) if visc else True)
    d = {"key": want, "alpha": HM_ALPHAS[: len(ch)], "hmom_qc2": ch, "cl": cl, "converged": conv}
    out.write_text(json.dumps(d))
    return tag, d


def summarize(a):
    if len(a) < 8:
        return {"n": int(len(a))}
    al, cl, cd, cm = a[:, 0], a[:, 1], a[:, 2], a[:, 4]
    i = int(np.argmax(cl))
    lin = (al >= -2) & (al <= 4)
    slope, icpt = np.polyfit(np.radians(al[lin]), cl[lin], 1)
    att = a[: i + 1]
    att = att[np.argsort(att[:, 1])]

    def cd_at(c):
        return float(np.interp(c, att[:, 1], att[:, 2])) if att[0, 1] <= c <= att[-1, 1] else float("nan")

    # post-stall: CL drop over 3 deg beyond alpha_clmax (gentle < 0.1)
    post = a[(al > al[i]) & (al <= al[i] + 3.0)]
    drop = float(cl[i] - post[:, 1].min()) if len(post) else float("nan")
    return {"n": int(len(a)), "clmax": float(cl[i]), "alpha_clmax": float(al[i]),
            "cla_per_rad": float(slope), "alpha0_deg": float(np.degrees(-icpt / slope)),
            "cm0": float(np.interp(-icpt / slope, np.radians(al), cm)),
            "cm_at_cl": {f"{c:.2f}": float(np.interp(c, att[:, 1], att[:, 4])) for c in (0.3, 0.5, 0.7)},
            "cd_at_cl": {f"{c:.2f}": cd_at(c) for c in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)},
            "cdmin": float(cd.min()), "ldmax": float((cl / cd).max()),
            "cl_drop_3deg_post_stall": drop, "alpha_max_converged": float(al.max())}


def main():
    t0 = time.time()
    jobs = []
    for f in FOILS:
        for r in RES:
            jobs.append(("A", (f, r, 9.0, 0.0)))
        jobs.append(("A", (f, RE_STALL, 5.0, 0.0)))
        for r in (RE_STALL, RE_CRUISE):
            for d in FLAPS:
                if d:
                    jobs.append(("B", (f, r, 9.0, d)))
    jobs.append(("N", ("s5010", RE_CRUISE, 9.0, 0.0, NPAN, -16.0, 4.0)))   # negative stall (CLmin) for C1
    jobs.append(("N", ("mh45", RE_CRUISE, 9.0, 0.0, NPAN, -16.0, 4.0)))
    for n in (160, 300):
        jobs.append(("G", ("mh45", RE_CRUISE, 9.0, 0.0, n)))
    hjobs = [(f, RE_DIVE, d, v) for f in HM_FOILS for d in HM_FLAPS for v in (True, False)]
    pol = {}
    hm = {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(polar, *args): k for k, args in jobs}
        hfuts = {ex.submit(hinge_case, *a): a for a in hjobs}
        for fu in cf.as_completed(futs):
            tag, a = fu.result()
            pol[tag] = a
        for fu in cf.as_completed(hfuts):
            tag, d = fu.result()
            hm[tag] = d
    res = {"tool": "XFOIL 6.99 (https://web.mit.edu/drela/Public/web/xfoil/)", "nu_m2s": NU, "chord_m": CHORD,
           "re_stall": RE_STALL, "re_cruise": RE_CRUISE, "re_dive": RE_DIVE,
           "x_hinge_c": X_HINGE, "hinge_y_t": HINGE_YT, "npan": NPAN, "polars": {}, "hinge": hm,
           "wall_s": None}
    for tag, a in sorted(pol.items()):
        res["polars"][tag] = {"summary": summarize(a),
                              "table": [[round(float(v), 5) for v in row] for row in a]}
    res["wall_s"] = round(time.time() - t0, 1)
    (HERE / "out" / "xfoil_results.json").write_text(json.dumps(res, indent=0))
    print(f"XFOIL: {len(pol)} polars, {len(hm)} hinge cases in {res['wall_s']} s")
    for tag in sorted(pol):
        s = res["polars"][tag]["summary"]
        if "clmax" in s:
            print(f"  {tag:<34} clmax {s['clmax']:.3f} @ {s['alpha_clmax']:5.1f}  cm0 {s['cm0']:+.4f}  "
                  f"cd@0.5 {s['cd_at_cl']['0.50']:.4f}  drop {s['cl_drop_3deg_post_stall']:.3f}  n {s['n']}")
        else:
            print(f"  {tag:<34} too few points ({s['n']})")


if __name__ == "__main__":
    main()
