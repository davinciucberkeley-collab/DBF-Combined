"""B1 verification round: AVL 3.52 (vortex lattice) + XFOIL 6.99 strip polars on the as-designed geometry and mass.

What it answers for the performance model (team/B1/performance.py uses B2's props-off polar at the 2.6 kg gate):
  1. trimmed cruise at the as-designed mass (A3 roll-up, predicted 2.436 kg) and the A3 CG (x 0.0536 m): alpha,
     elevon deflection, induced drag, span efficiency e, CL_alpha, neutral point;
  2. wing profile drag by strip integration: each AVL strip's cl and elevon deflection -> XFOIL cd at the strip Re
     (free transition Ncrit 9 and 5, and forced transition at the LE for the like-for-like check against SU2 SA);
  3. trimmed CLmax by the critical-section method: CL at which the first strip reaches its XFOIL clmax at the stall Re
     with its own elevon deflection;
  4. convergence: AVL on 3 lattices (chordwise x spanwise ~1.5x per level), XFOIL on 3 panel counts (160/240/320).

Geometry from redesign/params/params.json (wing, elevon spans and chord fraction, fins); mass and CG from
team/A3/claims.json (CL-A3-MASS-PREDICTED, CL-A3-CG-X-PRED). The elevon effectiveness in AVL is B2's eta (P:b2.*)
so the deflections compare with B2. Props off, pod not modelled in AVL (its lift is small; its drag is in the
build-up). Run:  python -I redesign/team/B1/vlm_xfoil.py   (~2 min). Writes sim/vlm_xfoil_results.json.
"""
import json
import math
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RED = HERE.parents[1]
OUT = HERE / "sim" / "vlm_xfoil"
OUT.mkdir(parents=True, exist_ok=True)
XFOIL = Path("C:/Users/dillo/tools/xfoil/xfoil.exe")
AVL = Path("C:/Users/dillo/tools/avl/avl352.exe")
PRM = json.loads((RED / "params" / "params.json").read_text(encoding="utf-8"))
B2P = json.loads((RED / "team" / "B2" / "params.json").read_text(encoding="utf-8"))
A3 = {n["id"]: n for n in json.loads((RED / "team" / "A3" / "claims.json").read_text(encoding="utf-8"))["nodes"]}


def pv(path, src=PRM):
    d = src
    for k in path.split("."):
        d = d[k]
    return d["value"]


SPAN, CHORD = pv("wing.span_m"), pv("wing.chord_m")
S = SPAN * CHORD
EF = pv("wing.elevon.chord_frac")
XH = 1 - EF
YIN, YOUT = pv("wing.elevon.inboard_y_m"), pv("wing.elevon.outboard_y_m")
YFIN, HFIN, CFIN, XFIN = pv("fins.y_m"), pv("fins.half_height_m"), pv("fins.chord_m"), pv("fins.le_x_m")
POD_HALF = pv("pod.size_m")[1] / 2
RHO, G, V = pv("env.rho_kgm3"), pv("env.g_ms2"), pv("performance.cruise_ms")
NU = 1.48e-5                                       # B2 ASM-B2-NU
ETA = next(v["elevon_eta"]["value"] for v in B2P["b2"].values() if isinstance(v, dict) and "elevon_eta" in v)
M_PRED = A3["CL-A3-MASS-PREDICTED"]["value"]
M_BASIC = A3["CL-A3-MASS-BASIC"]["value"]
XCG = A3["CL-A3-CG-X-PRED"]["value"]
ZCG = 0.018                                        # A3 rollup.json cg_pred z (m); AVL result insensitive to it
CL_CRUISE = 2 * M_PRED * G / (RHO * V * V * S)
RE_CRUISE = V * CHORD / NU
V_STALL = pv("requirements.stall_max_ms")
RE_STALL = V_STALL * CHORD / NU
LATTICES = {1: (8, 0.67), 2: (12, 1.0), 3: (18, 1.5)}      # (chordwise vortices, spanwise scale)
PANELS = (160, 240, 320)
FLAPS = (-15.0, -10.0, -5.0, 0.0, 5.0)                     # deg, + TE down (XFOIL and AVL sign)


# ------------------------------------------------------------------ XFOIL
def xfoil_polar(re_, ncrit=9.0, flap=0.0, npan=240, xtr=None, amin=-4.0, amax=16.0, da=0.5):
    tag = f"re{re_ / 1e3:.0f}k_n{ncrit:g}_f{flap:+g}_p{npan}" + ("_trip" if xtr else "")
    f = OUT / f"polar_{tag}.txt"
    if f.exists():
        f.unlink()
    cmd = f"PLOP\nG\n\nLOAD s5010.dat\nPPAR\nN {npan}\n\n\n"
    if flap:
        cmd += f"GDES\nFLAP\n{XH:.4f}\n999\n0.9\n{flap}\nX\n\nPANE\n"
    cmd += f"OPER\nVISC {re_:.0f}\nITER 150\nVPAR\nN {ncrit}\n"
    if xtr:
        cmd += f"XTR {xtr} {xtr}\n"
    cmd += f"\nPACC\n{f.name}\n\n"
    cmd += f"ASEQ 0 {amax} {da}\nINIT\nASEQ {-da} {amin} {-da}\nPACC\n\nQUIT\n"
    try:
        subprocess.run([str(XFOIL)], input=cmd, text=True, capture_output=True, cwd=str(OUT), timeout=240)
    except subprocess.TimeoutExpired:          # a non-converging point can hang XFOIL: keep the points saved so far
        (OUT / f"{f.stem}.timeout").write_text("xfoil killed after 240 s; polar file holds the converged points")
    rows = []
    for line in f.read_text().splitlines():
        p = line.split()
        if len(p) >= 7 and re.match(r"^-?\d", p[0]):
            try:
                rows.append([float(x) for x in p[:5]])
            except ValueError:
                pass
    a = np.array(sorted({r[0]: r for r in rows}.values()))
    return a                                            # alpha, cl, cd, cdp, cm


def cd_at_cl(polar, cl):
    """cd at cl on the attached branch (below clmax)."""
    b = polar[: int(np.argmax(polar[:, 1])) + 1]
    b = b[np.argsort(b[:, 1])]
    return float(np.interp(cl, b[:, 1], b[:, 2]))


def clmax(polar):
    return float(polar[:, 1].max())


# ------------------------------------------------------------------ AVL
def write_avl(path, nc, ns):
    b2 = SPAN / 2
    ys = sorted({round(y, 5) for y in (0.0, POD_HALF, YIN[0], YIN[1], YFIN, YOUT[0], YOUT[1], b2)})
    nseg = [max(1, round((b - a) / 0.0192 * ns)) for a, b in zip(ys, ys[1:])]    # ~0.019 m strips at L2
    ctrl = [(YIN[0], YIN[1]), (YOUT[0], YOUT[1])]
    s = ["K09-L as designed (B1 verification) - team/B1/vlm_xfoil.py", "0.0", "0 0 0.0",
         f"{S:.5f} {CHORD:.5f} {SPAN:.5f}", f"{XCG:.5f} 0.0 {ZCG:.4f}", "0.0",
         "#", "SURFACE", "Wing", f"{nc} 1.0", "YDUPLICATE", "0.0"]
    for i, y in enumerate(ys):
        line = f"0.0 {y:.5f} 0.0 {CHORD:.5f} 0.0" + (f"  {nseg[i]} 1.0" if i < len(nseg) else "")
        s += ["SECTION", line, "AFILE", "s5010.dat"]
        if any(a - 1e-9 <= y <= b + 1e-9 for a, b in ctrl):
            s += ["CONTROL", f"elevator {ETA:.4f} {XH:.4f} 0 0 0 1.0"]
    nz = max(4, 2 * round(6 * ns))
    s += ["#", "SURFACE", "Fin", f"{max(6, nc - 4)} 1.0 {nz} 1.0", "YDUPLICATE", "0.0",
          "SECTION", f"{XFIN:.4f} {YFIN:.4f} {-HFIN:.4f} {CFIN:.4f} 0.0",
          "SECTION", f"{XFIN:.4f} {YFIN:.4f} {HFIN:.4f} {CFIN:.4f} 0.0"]
    path.write_text("\n".join(s) + "\n")


def grab(t, key):
    m = re.search(rf"(?<![\w']){re.escape(key)}\s*=\s*([-+0-9.Ee]+)", t)
    return float(m.group(1)) if m else None


def strips(path):
    out, active = [], False
    for line in path.read_text().splitlines():
        if "Surface #" in line:
            active = ("Wing" in line) and ("YDUP" not in line)
            continue
        if active and re.match(r"\s*\d+\s+[-+0-9.]", line):
            f = [float(x) for x in line.split()]
            if len(f) >= 15:
                out.append({"y": f[2], "chord": f[4], "area": f[5], "cl": f[9]})
    return [r for r in out if r["y"] > 0]


def avl_trim(level, cls):
    nc, ns = LATTICES[level]
    tag = f"L{level}"
    f = OUT / f"k09l_{tag}.avl"
    write_avl(f, nc, ns)
    (OUT / "s5010.dat").write_text((RED / "team" / "B2" / "airfoils" / "s5010.dat").read_text())
    for old in OUT.glob(f"{tag}_*.txt"):
        old.unlink()
    cmd = "OPER\n"
    for i, c in enumerate(cls):
        cmd += f"A C {c:.4f}\nD1 PM 0\nX\nFT\n{tag}_ft_{i}.txt\nFS\n{tag}_fs_{i}.txt\nST\n{tag}_st_{i}.txt\n"
    cmd += "\nQUIT\n"
    subprocess.run([str(AVL), f.name], input=cmd, text=True, capture_output=True, cwd=str(OUT), timeout=120)
    res = []
    for i, c in enumerate(cls):
        ft = (OUT / f"{tag}_ft_{i}.txt").read_text()
        st = (OUT / f"{tag}_st_{i}.txt").read_text()
        m = re.search(r"elevator\s*=\s*([-+0-9.Ee]+)", ft)
        res.append({"CL": grab(ft, "CLtot"), "alpha_deg": grab(ft, "Alpha"), "CDi": grab(ft, "CDind"),
                    "e": grab(ft, "e"), "elevon_deg": float(m.group(1)), "CLa": grab(st, "CLa"),
                    "Xnp": grab(st, "Xnp"), "strips": strips(OUT / f"{tag}_fs_{i}.txt")})
    return res


def in_elevon(y):
    return YIN[0] <= y <= YIN[1] or YOUT[0] <= y <= YOUT[1]


def profile_cd(trim, polars):
    """Strip-integrated profile drag of the whole wing on S: polars[flap] -> cd at the strip cl (interpolated
    linearly in flap for elevon strips)."""
    flaps = sorted(polars)
    tot = 0.0
    for s in trim["strips"]:
        d = trim["elevon_deg"] if in_elevon(s["y"]) else 0.0
        d = min(max(d, flaps[0]), flaps[-1])
        hi = next(f for f in flaps if f >= d)
        lo = max(f for f in flaps if f <= d)
        c_lo, c_hi = cd_at_cl(polars[lo], s["cl"]), cd_at_cl(polars[hi], s["cl"])
        cd = c_lo if hi == lo else c_lo + (c_hi - c_lo) * (d - lo) / (hi - lo)
        tot += cd * s["area"]
    return 2 * tot / S


def critical_section(trims, polars_stall):
    """Lowest trimmed CL at which a strip reaches its clmax (stall Re, its own elevon deflection)."""
    flaps = sorted(polars_stall)
    cmax = {f: clmax(polars_stall[f]) for f in flaps}
    prev = None
    for t in trims:
        worst = 0.0
        for s in t["strips"]:
            d = t["elevon_deg"] if in_elevon(s["y"]) else 0.0
            d = min(max(d, flaps[0]), flaps[-1])
            worst = max(worst, s["cl"] / float(np.interp(d, flaps, [cmax[f] for f in flaps])))
        if worst >= 1.0:
            if prev is None:
                return t["CL"], t["elevon_deg"]
            f = (1.0 - prev[1]) / (worst - prev[1])
            return prev[0]["CL"] + f * (t["CL"] - prev[0]["CL"]), prev[0]["elevon_deg"] + f * (
                t["elevon_deg"] - prev[0]["elevon_deg"])
        prev = (t, worst)
    return None, None


def main():
    res = {"_note": "Written by team/B1/vlm_xfoil.py. CL_cruise at the A3 predicted mass, 16 m/s.",
           "inputs": {"m_pred_kg": M_PRED, "m_basic_kg": M_BASIC, "xcg_m": XCG, "S_m2": S, "AR": SPAN ** 2 / S,
                      "cl_cruise": CL_CRUISE, "re_cruise": RE_CRUISE, "re_stall": RE_STALL, "eta": ETA}}
    # --- AVL lattice convergence at cruise CL
    conv = {}
    for L in LATTICES:
        t = avl_trim(L, [CL_CRUISE])[0]
        conv[f"L{L}"] = {k: t[k] for k in ("alpha_deg", "CDi", "e", "elevon_deg", "CLa", "Xnp")}
        conv[f"L{L}"]["n_strips_half"] = len(t["strips"])
    res["avl_convergence"] = conv
    print("AVL", {k: (round(v["e"], 4), round(v["elevon_deg"], 2), round(v["Xnp"], 4)) for k, v in conv.items()})
    # --- all XFOIL polars, run concurrently (each is its own xfoil.exe process and file)
    (OUT / "s5010.dat").write_text((RED / "team" / "B2" / "airfoils" / "s5010.dat").read_text())
    jobs = {("pan", n): (RE_CRUISE, 9.0, 0.0, n, None) for n in PANELS}
    jobs.update({("pol", nc, f): (RE_CRUISE, nc, f, 240, None) for nc in (9.0, 5.0) for f in FLAPS
                 if (nc, f) != (9.0, 0.0)})                     # that one is ("pan", 240): same file
    jobs.update({("trip", f): (RE_CRUISE, 9.0, f, 240, 0.02) for f in FLAPS})
    jobs.update({("stall", f): (RE_STALL, 9.0, f, 240, None) for f in FLAPS})
    with ThreadPoolExecutor(8) as ex:
        futs = {k: ex.submit(xfoil_polar, *a) for k, a in jobs.items()}
        P_ = {k: fu.result() for k, fu in futs.items()}
    P_[("pol", 9.0, 0.0)] = P_[("pan", 240)]
    # --- XFOIL panel convergence at cruise Re, cruise cl, flap 0
    pc = {}
    for n in PANELS:
        p = P_[("pan", n)]
        pc[n] = {"cd_at_cl": cd_at_cl(p, CL_CRUISE), "clmax": clmax(p)}
    res["xfoil_panel_convergence"] = {str(k): v for k, v in pc.items()}
    print("XFOIL panels", pc)
    # --- polars on the medium panel count
    pol = {(nc, f): P_[("pol", nc, f)] for nc in (9.0, 5.0) for f in FLAPS}
    trip = {f: P_[("trip", f)] for f in FLAPS}
    stall = {f: P_[("stall", f)] for f in FLAPS}
    # --- trimmed polar on the medium lattice
    cls = [0.25, 0.30, 0.35, CL_CRUISE, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]
    trims = avl_trim(2, cls)
    rows = []
    for t in trims:
        cdp9 = profile_cd(t, {f: pol[(9.0, f)] for f in FLAPS})
        cdp5 = profile_cd(t, {f: pol[(5.0, f)] for f in FLAPS})
        cdpt = profile_cd(t, trip)
        rows.append([t["CL"], t["alpha_deg"], t["elevon_deg"], t["CDi"], t["e"], cdp9, cdp5, cdpt])
    res["trim_polar_cols"] = ["CL", "alpha deg", "elevon deg", "CDi", "e", "CDp Ncrit9", "CDp Ncrit5", "CDp tripped"]
    res["trim_polar"] = rows
    # fit CD_wing = A + K CL^2 over CL 0.3-0.7 (cruise and transition-end range), Ncrit 9 (base) and Ncrit 5
    sel = [r for r in rows if 0.29 <= r[0] <= 0.71]
    X = np.array([[1.0, r[0] ** 2] for r in sel])
    fits = {}
    for name, col in (("ncrit9", 5), ("ncrit5", 6), ("tripped", 7)):
        y = np.array([r[3] + r[col] for r in sel])
        A, K = np.linalg.lstsq(X, y, rcond=None)[0]
        fits[name] = {"cd0_wing": float(A), "k_wing": float(K), "e_equiv": float(1 / (math.pi * SPAN ** 2 / S * K)),
                      "rms": float(np.sqrt(np.mean((X @ [A, K] - y) ** 2)))}
    res["fit_CDwing_A_plus_K_CL2"] = fits
    cr = next(t for t in trims if abs(t["CL"] - CL_CRUISE) < 1e-3)
    res["cruise"] = {"alpha_deg": cr["alpha_deg"], "elevon_deg": cr["elevon_deg"], "CDi": cr["CDi"], "e": cr["e"],
                     "CLa": cr["CLa"], "Xnp": cr["Xnp"], "SM": (cr["Xnp"] - XCG) / CHORD,
                     "CDp_ncrit9": profile_cd(cr, {f: pol[(9.0, f)] for f in FLAPS}),
                     "CDp_ncrit5": profile_cd(cr, {f: pol[(5.0, f)] for f in FLAPS}),
                     "CDp_tripped": profile_cd(cr, trip),
                     "cd2d_tripped_at_cl": cd_at_cl(trip[0.0], CL_CRUISE),
                     "cd2d_ncrit9_at_cl": cd_at_cl(pol[(9.0, 0.0)], CL_CRUISE),
                     "alpha2d_tripped_at_2p5": float(np.interp(2.5, trip[0.0][:, 0], trip[0.0][:, 1]))}
    clm, dm = critical_section(trims, stall)
    res["clmax_trimmed"] = {"CLmax": clm, "elevon_deg": dm, "xcg_m": XCG,
                            "clmax_2d_stall_by_flap": {str(f): clmax(stall[f]) for f in FLAPS}}
    # trip comparison point for SU2 (alpha 2.5 deg)
    res["xfoil_trip_alpha2p5"] = {"cl": float(np.interp(2.5, trip[0.0][:, 0], trip[0.0][:, 1])),
                                  "cd": float(np.interp(2.5, trip[0.0][:, 0], trip[0.0][:, 2])),
                                  "re": RE_CRUISE}
    res["xfoil_free_alpha2p5"] = {"cl": float(np.interp(2.5, pol[(9.0, 0.0)][:, 0], pol[(9.0, 0.0)][:, 1])),
                                  "cd": float(np.interp(2.5, pol[(9.0, 0.0)][:, 0], pol[(9.0, 0.0)][:, 2]))}
    res["polar_flap0"] = {"ncrit9": pol[(9.0, 0.0)].tolist(), "tripped": trip[0.0].tolist()}
    print(json.dumps({k: res[k] for k in ("cruise", "clmax_trimmed", "fit_CDwing_A_plus_K_CL2")}, indent=1))
    (HERE / "sim" / "vlm_xfoil_results.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
