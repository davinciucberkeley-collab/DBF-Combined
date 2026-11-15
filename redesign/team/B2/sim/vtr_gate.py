"""B2 design round 2026-11-14: CL-B2R3-VTR-GATE-FWD (1.3 Vs at 2.6 kg, forward CG, CG height) re-check and levers.

Run from the repo root (after avl_wing.py, xfoil_wing.py, stall_zcg.py; about 3-5 min):
    python -I redesign/team/B2/sim/vtr_gate.py        -> team/B2/sim/out/vtr_gate.json

Read-only for every shared file: it writes only out/vtr_gate.json, new AVL cases (tag prefix "vg_") in out/avl and
new XFOIL polars in out/xfoil. It does not write params.zcg.json or claims (wave-1 rule).

Why: the claim reads the AVL grid of stall_zcg.py by bilinear interpolation, but that grid starts at x 0.0446 m.
Since D-120 the forward limit is 0.0394 m, so the claim value is a 5.2 mm linear extrapolation, and the trimmed
elevon there (-15.9 deg) is beyond the -15 deg end of the XFOIL clmax(delta) table. This script
  1. runs AVL directly at every CG point of the range (Xref = x + dprop, Zref = z, same model as stall_zcg.py);
  2. refines the S5010 up-elevon clmax(delta) at the stall Re (XFOIL, -6 .. -20 deg, 220 and 300 panels);
  3. quantifies the wing-side levers: section table (envelope vs stall-Re), CG height, inboard / outboard elevon
     gearing, washout, Re.
Stall speed and Re correction are the same as sim_claims.py CALC-B2R4-STALL-Z.
"""
from __future__ import annotations

import concurrent.futures as cf
import importlib.util
import json
import math
import sys
from pathlib import Path

import threading

import numpy as np

LOCK = threading.Lock()

HERE = Path(__file__).resolve().parent
B2 = HERE.parent
REDESIGN = B2.parents[1]
sys.argv = [sys.argv[0]]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SZ = load("stall_zcg", HERE / "stall_zcg.py")          # AVL helpers, DPROP, F (s5010 block of avl_results.json)
AW = SZ.AW
XW = load("xfoil_wing", B2 / "xfoil_wing.py")
P = json.loads((REDESIGN / "params" / "params.json").read_text(encoding="utf-8"))
B2P = json.loads((B2 / "params.json").read_text(encoding="utf-8"))
SIMP = json.loads((HERE / "params.json").read_text(encoding="utf-8"))


def v(d, path):
    for k in path.split("."):
        d = d[k]
    return d["value"]


M = v(P, "requirements.mtow_gate_kg")
G, RHO = v(P, "env.g_ms2"), v(P, "env.rho_kgm3")
B, C = v(P, "wing.span_m"), v(P, "wing.chord_m")
K = v(P, "requirements.transition_factor")
XR = v(P, "cg.x_range_m")
XT, ZT, ZR = v(P, "cg.x_target_m"), v(P, "cg.z_target_m"), v(P, "cg.z_range_m")
SLOPE = v(SIMP, "b2sim.xfoil.clmax_re_slope_per_1e5")
REX = v(B2P, "b2.xfoil.re_stall")
TRIP = v(SIMP, "b2sim.xfoil.clmax_tripped") / v(B2P, "b2.xfoil.clmax_2d_stall")     # CL-B2R3-CLMAX-TRIP-RATIO
NU = 1.48e-5
KD = 1.0                                                                            # ASM-B2-CLMAX-KD (checked below)

X_PTS = [XR[0], 0.0420, 0.0446, 0.0466, XT, XR[1]]
Z_PTS = [ZR[0], ZT, 0.025]
CLS = [0.55, 0.65, 0.70, 0.72, 0.74, 0.76, 0.78, 0.80, 0.82, 0.84, 0.86, 0.88, 0.90]
FLAPS = [-6.0, -8.0, -10.0, -12.0, -14.0, -16.0, -18.0, -20.0]


def vs_of(cl, m=M):
    vs = math.sqrt(2 * m * G / (RHO * B * C * cl))
    re_s = vs * C / NU
    clc = cl * (1 + SLOPE * (re_s - REX) / 1e5)
    return math.sqrt(2 * m * G / (RHO * B * C * clc)), re_s


# ---------------------------------------------------------------- 1. XFOIL up-elevon clmax at the stall Re
def xfoil_table():
    jobs = [(d, n) for d in FLAPS for n in (220, 300)] + [(0.0, 300)]
    rows = {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(XW.polar, "s5010", REX, 9.0, d, n): (d, n) for d, n in jobs}
        for fu in cf.as_completed(futs):
            d, n = futs[fu]
            _, a = fu.result()
            s = XW.summarize(a)
            rows[(d, n)] = {"clmax": s.get("clmax"), "alpha": s.get("alpha_clmax"), "n": s.get("n")}
    existing = {d: AW.polar("s5010", AW.RE_STALL, d)[1] for d in (-15.0, -10.0, -5.0, 0.0)}
    for d, s in existing.items():
        rows[(d, 220)] = {"clmax": s["clmax"], "alpha": s["alpha_clmax"], "n": s["n"]}
    return rows


def stall_re_table(rows, npan):
    """Stall-Re clmax(delta) for delta <= 0, conservative: lower of 220/300 panels where both exist, then made
    non-increasing towards up-elevon (same monotone rule as avl_wing.clmax_vs_flap, without the cruise-Re minimum)."""
    ds = sorted({d for d, _ in rows if d <= 0}, reverse=True)           # 0, -5, -6, ...
    tab = []
    for d in ds:
        vals = [rows[(d, n)]["clmax"] for n in npan if (d, n) in rows and rows[(d, n)]["clmax"]
                and rows[(d, n)]["n"] >= 20]
        if vals:
            tab.append([d, min(vals)])
    for i in range(1, len(tab)):
        tab[i][1] = min(tab[i][1], tab[i - 1][1])
    pos = [list(r) for r in SZ.F["clmax_vs_flap"] if r[0] > 0]
    return [tuple(r) for r in sorted(tab + pos)]


# ---------------------------------------------------------------- 2. AVL cases
def write_case(tag, xref, zref, r_in=1.0, r_out=1.0, twist=0.0):
    f = AW.OUT / f"{tag}.avl"
    AW.write_avl(f, SZ.FOIL, SZ.F["eta"], twist=twist)
    t = f.read_text().splitlines()
    t[4] = f"{xref:.5f} 0.0 {zref:.5f}"
    eta = SZ.F["eta"]
    out, y = [], None
    for line in t:
        if y is not None and line.startswith("elevator "):
            r = r_in if AW.YIN[0] - 1e-6 <= y <= AW.YIN[1] + 1e-6 else r_out
            line = line.replace(f"elevator {eta:.4f}", f"elevator {eta * r:.4f}")
        parts = line.split()
        if len(parts) >= 5 and out and out[-1] == "SECTION":
            y = float(parts[1])
        out.append(line)
    f.write_text("\n".join(out) + "\n")
    return f


def run_case(tag, xref, zref, r_in=1.0, r_out=1.0, twist=0.0, cls=CLS):
    have = all((AW.OUT / f"{tag}_{k}_cl{c:.2f}.txt").exists() for c in cls for k in ("ft", "fs"))
    if not have:                         # complete earlier runs are re-used (same inputs; delete vg_* after a change)
        _avl(tag, xref, zref, r_in, r_out, twist, cls)
    return read_case(tag, cls)


def _avl(tag, xref, zref, r_in, r_out, twist, cls):
    with LOCK:                           # write_avl copies the airfoil file: a parallel copy lost a case, so serialise
        f = write_case(tag, xref, zref, r_in, r_out, twist)
    for old in AW.OUT.glob(f"{tag}_*.txt"):
        old.unlink()
    cmds = "OPER\n"
    for c in cls:
        cmds += f"A C {c}\nD1 PM {SZ.F['cm_t']:.5f}\nX\nFT\n{tag}_ft_cl{c:.2f}.txt\nFS\n{tag}_fs_cl{c:.2f}.txt\n"
    cmds += "\nQUIT\n"
    AW.run_avl(f, cmds)


def read_case(tag, cls):
    res = {"trim": {}}
    for c in cls:
        ft = (AW.OUT / f"{tag}_ft_cl{c:.2f}.txt").read_text()
        d = {k: AW.grab(ft, k) for k in ("Alpha", "CLtot", "Cmtot")}
        m = AW.re.search(r"elevator\s*=\s*([-+0-9.Ee]+)", ft)
        d["elevator"] = float(m.group(1)) if m else None
        d["strips"] = AW.parse_fs_text(AW.OUT / f"{tag}_fs_cl{c:.2f}.txt")
        res["trim"][f"{c:.2f}"] = d
    return res


def critical(res, table, r_in=1.0, r_out=1.0):
    """avl_wing.critical_section with a per-panel deflection (r_in, r_out times the trim variable)."""
    dl = np.array([r[0] for r in table])
    cm = np.array([r[1] for r in table])
    prev = None
    for k in sorted(res["trim"], key=float):
        d = res["trim"][k]
        de = d["elevator"]
        best = (0, None)
        for s in d["strips"]:
            if AW.YIN[0] <= s["y"] <= AW.YIN[1]:
                lim = float(np.interp(r_in * de, dl, cm))
            elif AW.YOUT[0] <= s["y"] <= AW.YOUT[1]:
                lim = float(np.interp(r_out * de, dl, cm))
            else:
                lim = float(np.interp(0.0, dl, cm))
            best = max(best, (s["cl"] / lim, s["y"]))
        cur = {"CL": d["CLtot"], "de": de, "alpha": d["Alpha"], "ratio": best[0], "y": best[1]}
        if cur["ratio"] >= 1.0 and prev is not None:
            f = (1.0 - prev["ratio"]) / (cur["ratio"] - prev["ratio"])
            de_s = prev["de"] + f * (de - prev["de"])
            return {"CLmax": prev["CL"] + f * (cur["CL"] - prev["CL"]), "elev_var_deg": de_s,
                    "elev_in_deg": r_in * de_s, "elev_out_deg": r_out * de_s,
                    "alpha_deg": prev["alpha"] + f * (cur["alpha"] - prev["alpha"]), "y_first": cur["y"]}
        prev = cur
    return {"CLmax": None}


def main():
    rows = xfoil_table()
    env_tab = [tuple(r) for r in SZ.F["clmax_vs_flap"]]                 # what the claim uses
    sre_tab = stall_re_table(rows, (220, 300))
    print("XFOIL S5010 Re %.2g clmax(delta):" % REX)
    for (d, n), r in sorted(rows.items()):
        print(f"  d {d:+5.1f} p{n}: clmax {r['clmax']}  a {r['alpha']}  n {r['n']}")
    print("  envelope (claim):", env_tab)
    print("  stall-Re table   :", sre_tab)

    cases = {}
    jobs = {}
    for x in X_PTS:
        for z in Z_PTS:
            jobs[f"vg_x{x*1e4:.0f}_z{z*1e4:.0f}"] = dict(xref=x + SZ.DPROP, zref=z)
    xf = XR[0]
    for r_in in (0.5, 0.75):
        jobs[f"vg_split{r_in*100:.0f}_x{xf*1e4:.0f}"] = dict(xref=xf + SZ.DPROP, zref=ZT, r_in=r_in)
    for r_out in (0.75,):
        jobs[f"vg_osplit{r_out*100:.0f}_x{xf*1e4:.0f}"] = dict(xref=xf + SZ.DPROP, zref=ZT, r_out=r_out)
    for tw in (+2.0, -2.0):
        jobs[f"vg_tw{tw:+.0f}_x{xf*1e4:.0f}"] = dict(xref=xf + SZ.DPROP, zref=ZT, twist=tw)
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run_case, tag, **kw): tag for tag, kw in jobs.items()}
        for fu in cf.as_completed(futs):
            cases[futs[fu]] = fu.result()

    def point(tag, table, **kw):
        cs = critical(cases[tag], table, kw.get("r_in", 1.0), kw.get("r_out", 1.0))
        vs, re_s = vs_of(cs["CLmax"])
        return {**cs, "Vs": vs, "Vtr": K * vs, "Re_stall": re_s, "Vs_trip": vs / math.sqrt(TRIP),
                "Vtr_trip": K * vs / math.sqrt(TRIP)}

    out = {"_note": "team/B2/sim/vtr_gate.py (design round 2026-11-14)", "m_kg": M, "k": K, "dprop_m": SZ.DPROP,
           "trip_ratio": TRIP, "xfoil_rows": {f"{d:+g}_p{n}": r for (d, n), r in sorted(rows.items())},
           "table_envelope": env_tab, "table_stall_re": sre_tab, "grid": [], "levers": {}}
    for x in X_PTS:
        for z in Z_PTS:
            tag = f"vg_x{x*1e4:.0f}_z{z*1e4:.0f}"
            e, s = point(tag, env_tab), point(tag, sre_tab)
            out["grid"].append({"x": x, "z": z, "env": e, "stall_re": s})
            print(f"x {x:.4f} z {z:.4f}: ENV CLmax {e['CLmax']:.4f} de {e['elev_var_deg']:+.2f} Vs {e['Vs']:.3f} "
                  f"1.3Vs {e['Vtr']:.3f} trip {e['Vtr_trip']:.3f} | SRE CLmax {s['CLmax']:.4f} Vs {s['Vs']:.3f} "
                  f"1.3Vs {s['Vtr']:.3f} | y1 {e['y_first']}")
    for tag, kw in jobs.items():
        if tag.startswith("vg_x"):
            continue
        kk = {k: v_ for k, v_ in kw.items() if k in ("r_in", "r_out")}
        e, s = point(tag, env_tab, **kk), point(tag, sre_tab, **kk)
        out["levers"][tag] = {"kw": kw, "env": e, "stall_re": s}
        print(f"{tag}: ENV CLmax {e['CLmax']:.4f} in {e['elev_in_deg']:+.2f} out {e['elev_out_deg']:+.2f} "
              f"1.3Vs {e['Vtr']:.3f} y1 {e['y_first']} | SRE 1.3Vs {s['Vtr']:.3f}")
    (HERE / "out" / "vtr_gate.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
