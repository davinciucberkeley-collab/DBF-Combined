"""B2 wing aero: AVL 3.52 model of the K09-L wing + fins; lift distribution, trimmed CLmax, stall progression.

Run from the repo root after xfoil_wing.py (about 30 s):
    python -I redesign/team/B2/avl_wing.py

Model (repo frame = AVL frame: x aft from the root LE, y right, z up; params.json#frame):
  wing  rectangular wing.span_m x wing.chord_m (1.15 x 0.32 m at A1-R2), section from airfoils/<foil>.dat (AFILE),
        profile drag by CDCL from XFOIL at the cruise Re; strip boundaries at the pod (0.05), elevon ends
        (0.07, 0.30, 0.34, 0.56) and the fin (0.32)
  fins  flat plates at y = fins.y_m, x fins.le_x_m..fins.te_x_m, z +/- fins.half_height_m
        (A1-R2: y +/-0.32, x 0.045..0.32 (chord 0.275), z -0.19..+0.19; params.json#fins)
  controls  'elevator' (symmetric) and 'aileron' (antisymmetric) on both elevon panels per side, hinge at
        1 - wing.elevon.chord_frac; gain = XFOIL/thin-airfoil effectiveness eta so AVL degrees = physical degrees
  not modelled: pod (0.20 x 0.10 x 0.06 m body), props and slipstream (B4), motor tubes. Props-off, Mach 0.
Cases: clean alpha sweep (with / without fins); trim Cm = 0 at CL 0.2..1.2 for CG x = 0.045 / 0.060 / 0.075 m;
        twist 0 and -2 deg (linear washout); lattice convergence 3 levels.
Trimmed CLmax by the critical-section method: CL at which the first strip reaches its local clmax (XFOIL at the
stall Re and the cruise Re, the lower of the two, at that strip's elevon deflection).
Outputs: out/avl/* (inputs and raw outputs), out/avl_results.json, out/loads_inputs.json (for C1/C2).
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
OUT = HERE / "out" / "avl"
OUT.mkdir(parents=True, exist_ok=True)
AVL = Path("C:/Users/dillo/tools/avl/avl352.exe")
P = json.loads((REDESIGN / "params" / "params.json").read_text(encoding="utf-8"))
X = json.loads((HERE / "out" / "xfoil_results.json").read_text())


def v(path):
    d = P
    for k in path.split("."):
        d = d[k]
    return d["value"]


SPAN, CHORD = v("wing.span_m"), v("wing.chord_m")
S = SPAN * CHORD
EF = v("wing.elevon.chord_frac")
XH = 1.0 - EF
YIN, YOUT = v("wing.elevon.inboard_y_m"), v("wing.elevon.outboard_y_m")
YFIN, HFIN, FIN_X0, FIN_X1 = v("fins.y_m"), v("fins.half_height_m"), v("fins.le_x_m"), v("fins.te_x_m")
POD_HALF = v("pod.size_m")[1] / 2
XCG, XCG_RANGE = v("cg.x_target_m"), v("cg.x_range_m")
RHO, G = v("env.rho_kgm3"), v("env.g_ms2")
M_GATE = v("requirements.mtow_gate_kg")
RE_STALL, RE_CRUISE = X["re_stall"], X["re_cruise"]       # follow the chord (xfoil_wing.py)
FOILS = ["mh45", "mh60", "s5010", "e186"]
CLS = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]


def polar(foil, re_, flap=0.0, ncrit=9, npan=220):
    tag = f"{foil}_re{re_/1e5:.1f}e5_n{ncrit:g}_f{flap:+g}_p{npan}"
    p = X["polars"].get(tag)
    return (np.array(p["table"]), p["summary"]) if p else (None, None)


def eta_from_xfoil(foil):
    """Elevon effectiveness on the trim side: XFOIL d(cm)/d(delta) at cl 0.5 between -10 and 0 deg, mean of
    the stall and cruise Re (cm at fixed cl is less Re-noisy than cm0), over thin-airfoil theory for the same hinge."""
    th = math.acos(1 - 2 * XH)
    dcm_thin = -0.5 * math.sin(th) * (1 - math.cos(th)) * math.pi / 180     # per deg, about c/4
    vals, rejected = [], []
    for re_ in (RE_STALL, RE_CRUISE):
        if not all(smooth_at(polar(foil, re_, d)[0]) for d in (-10.0, 0.0)):
            rejected.append(re_)
            continue
        cm = {d: polar(foil, re_, d)[1]["cm_at_cl"]["0.50"] for d in (-10.0, 0.0)}
        vals.append((cm[0.0] - cm[-10.0]) / 10.0)
    if not vals:                       # no smooth polar: use them all and say so (candidate comparison only)
        for re_ in (RE_STALL, RE_CRUISE):
            cm = {d: polar(foil, re_, d)[1]["cm_at_cl"]["0.50"] for d in (-10.0, 0.0)}
            vals.append((cm[0.0] - cm[-10.0]) / 10.0)
        rejected = ["none smooth, all used"]
    dcm_x = sum(vals) / len(vals)
    ETA_REJECTED[foil] = rejected
    return dcm_x / dcm_thin, dcm_x, dcm_thin


ETA_REJECTED = {}


def smooth_at(a, cl=0.5, half_window=2.0, tol=0.01):
    """True when the attached polar is on one smooth branch around cl: a straight-line fit of cl(alpha) within
    +/- half_window deg of the cl point leaves no residual above tol. XFOIL's up-elevon polars sometimes jump
    between a lower-surface-separated and an attached branch (s5010 Re 3.5e5, -10 deg: cl steps 0.025-0.056 per
    0.5 deg near cl 0.5, cm +0.02 off its neighbours); such a polar is left out of eta."""
    if a is None or len(a) < 8:
        return False
    att = a[: int(np.argmax(a[:, 1])) + 1]
    al0 = float(np.interp(cl, np.sort(att[:, 1]), att[np.argsort(att[:, 1]), 0]))
    w = att[np.abs(att[:, 0] - al0) <= half_window]
    if len(w) < 5:
        return False
    k, c0 = np.polyfit(w[:, 0], w[:, 1], 1)
    return float(np.abs(w[:, 1] - (k * w[:, 0] + c0)).max()) <= tol


def cm_section(foil, cl="0.70"):
    """XFOIL section cm about c/4 at cl 0.7 (stall-relevant), stall Re, elevon neutral."""
    return polar(foil, RE_STALL)[1]["cm_at_cl"][cl]


def clmax_vs_flap(foil):
    """[(delta, clmax)] conservative envelope: at each deflection the lower of the stall and cruise Re (converged sets
    only), then made non-increasing from 0 deg towards -15 deg (XFOIL's up-elevon clmax is noisy, +/- 0.07)."""
    rows = []
    for d in (-15.0, -10.0, -5.0, 0.0, 5.0, 10.0):
        vals = []
        for re_ in (RE_STALL, RE_CRUISE):
            a, s = polar(foil, re_, d)
            if s and s.get("n", 0) >= 20 and s["clmax"] > 0.5:
                vals.append(s["clmax"])
        if vals:
            rows.append([d, min(vals)])
    neg = sorted([r for r in rows if r[0] <= 0], key=lambda r: -r[0])     # 0, -5, -10, -15
    for i in range(1, len(neg)):
        neg[i][1] = min(neg[i][1], neg[i - 1][1])
    return [tuple(r) for r in sorted(neg + [r for r in rows if r[0] > 0])]


def cdcl(foil):
    a, _ = polar(foil, RE_CRUISE)
    b = a[: int(np.argmax(a[:, 1])) + 1]
    b = b[np.argsort(b[:, 1])]
    pts = []
    for c in (-0.2, 0.45, 1.1):
        c = float(np.clip(c, b[:, 1].min(), b[:, 1].max()))
        pts.append((c, float(np.interp(c, b[:, 1], b[:, 2]))))
    return " ".join(f"{c:.4f} {d:.5f}" for c, d in pts)


def write_avl(path, foil, eta, fins=True, twist=0.0, nc=12, ns_scale=1.0):
    shutil.copy(HERE / "airfoils" / f"{foil}.dat", OUT / f"{foil}.dat")
    b2 = SPAN / 2
    ys = [0.0, POD_HALF, YIN[0], YIN[1], YFIN, YOUT[0], YOUT[1], b2]
    ctrl = {(YIN[0], YIN[1]), (YOUT[0], YOUT[1])}
    nseg = [max(1, round(n * ns_scale)) for n in (2, 1, 10, 1, 1, 10, 1)]
    nseg[3] = nseg[4] = 1                                   # one strip each side of the fin plane (no control point on it)
    # B2-R3: since D-25 the pod half-width (0.07) equals the inboard elevon end (0.07). A zero-width segment hangs
    # AVL 3.52, so a coincident station is dropped and its segment merged into the one before it.
    i = 1
    while i < len(ys):
        if ys[i] - ys[i - 1] < 1e-6:
            ys.pop(i)
            nseg.pop(i - 1 if i - 1 < len(nseg) else -1)
        else:
            i += 1
    s = [f"K09-L wing + fins ({foil}, eta {eta:.3f}, twist {twist:+.1f} deg, fins {fins}) - team/B2/avl_wing.py",
         "0.0", "0 0 0.0", f"{S:.5f} {CHORD:.5f} {SPAN:.5f}", f"{XCG:.5f} 0.0 0.0", "0.0",
         "#", "SURFACE", "Wing", f"{nc} 1.0", "YDUPLICATE", "0.0", "CDCL", cdcl(foil)]
    for i, y in enumerate(ys):
        tw = twist * y / b2
        xle = (XH * CHORD) * (1 - math.cos(math.radians(tw)))   # twist about the hinge line keeps the TE straight
        line = f"{xle:.5f} {y:.5f} 0.0 {CHORD:.5f} {tw:.4f}"
        if i < len(nseg):
            line += f"  {nseg[i]} 1.0"
        s += ["SECTION", line, "AFILE", f"{foil}.dat"]
        in_ctrl = any(a - 1e-9 <= y <= b + 1e-9 for a, b in ctrl)
        if in_ctrl:
            s += ["CONTROL", f"elevator {eta:.4f} {XH:.4f} 0 0 0 1.0",
                  "CONTROL", f"aileron {eta:.4f} {XH:.4f} 0 0 0 -1.0"]
    if fins:
        nz = max(2, 2 * round(6 * ns_scale))
        s += ["#", "SURFACE", "Fin", f"{max(6, nc - 4)} 1.0 {nz} 0.0", "YDUPLICATE", "0.0",
              "SECTION", f"{FIN_X0:.4f} {YFIN:.4f} {-HFIN:.4f} {FIN_X1 - FIN_X0:.4f} 0.0",
              "SECTION", f"{FIN_X0:.4f} {YFIN:.4f} {HFIN:.4f} {FIN_X1 - FIN_X0:.4f} 0.0"]
    path.write_text("\n".join(s) + "\n")


def run_avl(avl_file, cmds):
    p = subprocess.run([str(AVL), avl_file.name], input=cmds, text=True, capture_output=True, cwd=str(OUT), timeout=120)
    return p.stdout


def grab(t, key):
    m = re.search(rf"(?<![\w']){re.escape(key)}\s*=\s*([-+0-9.Ee]+)", t)
    return float(m.group(1)) if m else None


def parse_fs_text(path):
    """Wing strips of the right half from an AVL 3.52 FS file, by column position:
    j Xle Yle Zle Chord Area c_cl ai cl_norm cl cd cdv cm_c/4 cm_LE C.P.x/c."""
    t = path.read_text().splitlines()
    out, active = [], False
    for line in t:
        if "Surface #" in line:
            active = ("Wing" in line) and ("YDUP" not in line)
            continue
        if active and re.match(r"\s*\d+\s+[-+0-9.]", line):
            f = [float(x) for x in line.split()]
            if len(f) >= 15:
                out.append({"y": f[2], "chord": f[4], "c_cl": f[6], "cl": f[9], "cd": f[10], "cm_c4": f[12],
                            "area": f[5]})
    return [r for r in out if r["y"] > 0]


def case(foil, eta, tag, fins=True, twist=0.0, nc=12, ns=1.0, xcg=None, cls=CLS, cm_t=0.0):
    """cm_t: AVL pitching moment the elevons trim to = -(viscous cm correction), so that the real
    aircraft (AVL + correction) has Cm = 0."""
    f = OUT / f"{tag}.avl"
    write_avl(f, foil, eta, fins, twist, nc, ns)
    if xcg is not None:
        txt = f.read_text().splitlines()
        txt[4] = f"{xcg:.5f} 0.0 0.0"
        f.write_text("\n".join(txt) + "\n")
    for old in OUT.glob(f"{tag}_*.txt"):
        old.unlink()
    cmds = "OPER\n"
    # clean alpha 0 and 4 (lift slope, Cm0, NP); then trims
    for a in (0.0, 4.0):
        cmds += f"A A {a}\nD1 D1 0\nX\nST\n{tag}_st_a{a:g}.txt\nFT\n{tag}_ft_a{a:g}.txt\n"
    for c in cls:
        cmds += f"A C {c}\nD1 PM {cm_t:.5f}\nX\nFT\n{tag}_ft_cl{c:.2f}.txt\nFS\n{tag}_fs_cl{c:.2f}.txt\n"
    cmds += "\nQUIT\n"
    log = run_avl(f, cmds)
    (OUT / f"{tag}.log").write_text(log[-30000:])
    res = {"clean": {}, "trim": {}}
    for a in (0.0, 4.0):
        st = (OUT / f"{tag}_st_a{a:g}.txt").read_text()
        res["clean"][f"a{a:g}"] = {k: grab(st, k) for k in ("CLtot", "CDind", "Cmtot", "CLa", "Cma", "Xnp", "e",
                                                             "Clb", "Cnb", "Clp", "Cld02", "Cmd01", "CLd01")}
    for c in cls:
        ft = (OUT / f"{tag}_ft_cl{c:.2f}.txt").read_text()
        d = {k: grab(ft, k) for k in ("Alpha", "CLtot", "CDtot", "CDind", "Cmtot", "e")}
        m = re.search(r"elevator\s*=\s*([-+0-9.Ee]+)", ft)
        d["elevator"] = float(m.group(1)) if m else None
        d["strips"] = parse_fs_text(OUT / f"{tag}_fs_cl{c:.2f}.txt")
        res["trim"][f"{c:.2f}"] = d
    return res


def critical_section(res, foil, cl_flap):
    """First CL at which a strip's cl reaches its local clmax(delta) (linear interpolation between trim CLs)."""
    dl = np.array([r[0] for r in cl_flap])
    cm = np.array([r[1] for r in cl_flap])
    in_el = lambda y: (YIN[0] <= y <= YIN[1]) or (YOUT[0] <= y <= YOUT[1])
    prev = None
    hist = []
    for k in sorted(res["trim"], key=float):
        d = res["trim"][k]
        de = d["elevator"]
        ratios = []
        for s in d["strips"]:
            lim = float(np.interp(de, dl, cm)) if in_el(s["y"]) else float(np.interp(0.0, dl, cm))
            ratios.append((s["cl"] / lim, s["y"], s["cl"], lim))
        r = max(ratios)
        hist.append({"CL": d["CLtot"], "elevator": de, "alpha": d["Alpha"], "max_ratio": r[0], "y_first": r[1],
                     "order": [round(x[1], 3) for x in sorted(ratios, reverse=True)[:5]]})
        if r[0] >= 1.0 and prev is not None:
            f = (1.0 - prev["max_ratio"]) / (r[0] - prev["max_ratio"])
            return {"CLmax_trim": prev["CL"] + f * (d["CLtot"] - prev["CL"]),
                    "elevator_deg": prev["elevator"] + f * (de - prev["elevator"]),
                    "alpha_deg": prev["alpha"] + f * (d["Alpha"] - prev["alpha"]),
                    "y_first_stall": r[1], "history": hist}
        prev = hist[-1]
    return {"CLmax_trim": None, "history": hist}


CHOSEN = "s5010"          # recommended section (WING-AERO.md section 2); MH 45 kept as the compared baseline
SM_TARGET = 0.05          # static margin used for the design trim cases (R-STATIC-MARGIN floor)


def oswald_fit(res):
    """Parabolic fit CD = CD0 + k CL^2 over the trimmed cases CL 0.3..0.9 -> e_oswald = 1 / (pi AR k)."""
    pts = [(d["CLtot"], d["CDtot"]) for k, d in res["trim"].items() if 0.29 <= float(k) <= 0.91]
    cl = np.array([p[0] for p in pts])
    cd = np.array([p[1] for p in pts])
    k, cd0 = np.polyfit(cl ** 2, cd, 1)
    return {"CD0_wing": float(cd0), "k": float(k), "e_oswald": float(1 / (math.pi * SPAN ** 2 / S * k)),
            "note": f"wing + fins (flat plates, no fin profile drag), trimmed, section drag from XFOIL CDCL at Re {RE_CRUISE:.3g}"}


def span_loads(strips, cl_total):
    """Right half: unit loading, shear and bending moment per unit half-span lift, torsion about the spar."""
    xs = v("wing.spar.x_m") / CHORD
    ys = np.array([r["y"] for r in strips])
    a = np.array([r["area"] for r in strips])
    cl = np.array([r["cl"] for r in strips])
    cm4 = np.array([r["cm_c4"] for r in strips])
    lift = cl * a
    lh = lift.sum()
    ybar = float((lift * ys).sum() / lh)
    stations = [0.0, 0.05, 0.10, 0.20, 0.30, 0.32, 0.40, 0.50, 0.575]
    shear = [float(lift[ys > y].sum() / lh) for y in stations]
    bend = [float((lift[ys > y] * (ys[ys > y] - y)).sum() / lh) for y in stations]
    cm_spar = cm4 + cl * (xs - 0.25)
    torsion = [float((cm_spar[ys > y] * a[ys > y] * CHORD).sum() / lh) for y in stations]
    return {"CL": cl_total, "y_m": ys.round(4).tolist(), "cl": cl.round(4).tolist(),
            "cl_over_CL": (cl / cl_total).round(4).tolist(), "cm_c4": cm4.round(4).tolist(),
            "cm_spar": cm_spar.round(4).tolist(), "ybar_m": ybar, "ybar_frac_semispan": ybar / (SPAN / 2),
            "stations_y_m": stations, "shear_frac": shear, "bending_m_per_N": bend, "torsion_m_per_N": torsion}


def main():
    out = {"tool": "AVL 3.52 (https://web.mit.edu/drela/Public/web/avl/)", "S_m2": S, "cref": CHORD, "bref": SPAN,
           "xref_cg": XCG, "chosen": CHOSEN,
           "fins": {"y_m": YFIN, "half_height_m": HFIN, "le_x_m": FIN_X0, "te_x_m": FIN_X1, "chord_m": FIN_X1 - FIN_X0},
           "re_stall": RE_STALL, "re_cruise": RE_CRUISE, "foils": {}}
    for foil in FOILS:
        eta, dcmx, dcmt = eta_from_xfoil(foil)
        cfl = clmax_vs_flap(foil)
        r0 = case(foil, eta, f"{foil}_thin", cls=[0.5])
        c0 = r0["clean"]["a0"]
        cm_ac_thin = c0["Cmtot"] + c0["CLtot"] * (c0["Xnp"] - XCG) / CHORD     # AVL (thin-airfoil) Cm about the NP
        dcm = cm_section(foil) - cm_ac_thin                                     # viscous correction, added to AVL
        r = case(foil, eta, f"{foil}_base", cm_t=-dcm)
        cs = critical_section(r, foil, cfl)
        cl05 = r["trim"]["0.50"]
        out["foils"][foil] = {"eta": eta, "eta_re_rejected": ETA_REJECTED.get(foil, []), "dcm_ddelta_xfoil_per_deg": dcmx, "dcm_ddelta_thin_per_deg": dcmt,
                              "clmax_vs_flap": cfl, "re_stall": RE_STALL, "re_cruise": RE_CRUISE, "critical_section": cs,
                              "CLa_per_rad": r["clean"]["a0"]["CLa"], "Xnp_m": r["clean"]["a0"]["Xnp"],
                              "Cm0": r["clean"]["a0"]["Cmtot"], "CL0": r["clean"]["a0"]["CLtot"],
                              "e_trefftz_cl0.5": cl05["e"], "CD_trim_cl0.5": cl05["CDtot"],
                              "elev_trim_cl0.5": cl05["elevator"], "oswald": oswald_fit(r),
                              "derivs_a4": r["clean"]["a4"], "cm_ac_thin": cm_ac_thin,
                              "cm_section_cl0.7": cm_section(foil), "dcm_visc": dcm, "cm_t": -dcm}
        print(f"{foil:6} eta {eta:.2f}  CLa {r['clean']['a0']['CLa']:.3f}  Xnp {r['clean']['a0']['Xnp']:.4f}  "
              f"CLmax_trim {cs['CLmax_trim'] and round(cs['CLmax_trim'], 3)}  at y {cs.get('y_first_stall')}  "
              f"CD@0.5 {cl05['CDtot']:.4f} e {cl05['e']:.3f} e_osw {out['foils'][foil]['oswald']['e_oswald']:.3f} "
              f"de {cl05['elevator']:+.2f} dCm {dcm:+.4f}")
    foil = CHOSEN
    F = out["foils"][foil]
    eta, cfl = F["eta"], F["clmax_vs_flap"]
    x_sm = round(F["Xnp_m"] - SM_TARGET * CHORD, 4)
    out["x_cg_sm5_m"] = x_sm
    out["cg_sweep"] = {}
    design = None
    for xc in sorted({XCG_RANGE[0], XCG, XCG_RANGE[1], x_sm}):
        r = case(foil, eta, f"{foil}_cg{xc*1000:.1f}", xcg=xc, cm_t=F["cm_t"])
        cs = critical_section(r, foil, cfl)
        out["cg_sweep"][f"{xc:.4f}"] = {"static_margin": (F["Xnp_m"] - xc) / CHORD, "CLmax_trim": cs["CLmax_trim"],
                                        "elevator_at_clmax": cs.get("elevator_deg"), "alpha_at_clmax": cs.get("alpha_deg"),
                                        "y_first": cs.get("y_first_stall"),
                                        "elev_trim": {k: r["trim"][k]["elevator"] for k in r["trim"]},
                                        "alpha_trim": {k: r["trim"][k]["Alpha"] for k in r["trim"]},
                                        "history": cs["history"]}
        if abs(xc - x_sm) < 1e-9:
            design = (r, cs)
        print(f"  cg {xc:.4f} (SM {(F['Xnp_m'] - xc) / CHORD:+.3f}): CLmax_trim {cs['CLmax_trim']}  first {cs.get('y_first_stall')}")
    # trimmed CLmax against static margin (props-off NP of this model): the stall-speed claims read it at the aft
    # (SM floor) and forward ends of the CG range, since a forward CG needs more up-elevon and stalls the inboard
    # elevon strip earlier
    out["sm_sweep"] = []
    for sm in (0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12):
        xc = round(F["Xnp_m"] - sm * CHORD, 5)
        r = case(foil, eta, f"{foil}_sm{sm*100:.0f}", xcg=xc, cm_t=F["cm_t"])
        cs = critical_section(r, foil, cfl)
        out["sm_sweep"].append([sm, cs["CLmax_trim"], cs.get("elevator_deg"), cs.get("y_first_stall")])
        print(f"  SM {sm:.2f} (x {xc:.4f}): CLmax_trim {cs['CLmax_trim']:.4f}  elev {cs.get('elevator_deg'):+.2f}")
    out["twist"] = {}
    for tw in (0.0, -2.0, -4.0):
        r = case(foil, eta, f"{foil}_tw{abs(tw):g}", twist=tw, xcg=x_sm, cm_t=F["cm_t"])
        cs = critical_section(r, foil, cfl)
        out["twist"][f"{tw:+.1f}"] = {"CLmax_trim": cs["CLmax_trim"], "y_first": cs.get("y_first_stall"),
                                      "CD_cl0.5": r["trim"]["0.50"]["CDtot"], "e_cl0.5": r["trim"]["0.50"]["e"],
                                      "elev_cl0.5": r["trim"]["0.50"]["elevator"], "history": cs["history"]}
        print(f"  twist {tw}: CLmax_trim {cs['CLmax_trim']}  first {cs.get('y_first_stall')}  CD0.5 {r['trim']['0.50']['CDtot']:.4f}")
    rn = case(foil, eta, f"{foil}_nofins", fins=False, cls=[0.5], cm_t=F["cm_t"])
    out["nofins"] = {"e_cl0.5": rn["trim"]["0.50"]["e"], "CLa": rn["clean"]["a0"]["CLa"], "Xnp": rn["clean"]["a0"]["Xnp"]}
    out["convergence"] = {}
    for lvl, (nc, ns) in enumerate(((8, 0.6), (12, 1.0), (18, 1.6))):
        r = case(foil, eta, f"{foil}_L{lvl}", nc=nc, ns=ns, cls=[0.5, 1.0], cm_t=F["cm_t"])
        out["convergence"][f"L{lvl}"] = {"nc": nc, "ns_scale": ns, "CLa": r["clean"]["a0"]["CLa"],
                                         "Xnp": r["clean"]["a0"]["Xnp"], "e": r["trim"]["0.50"]["e"],
                                         "elev_cl1.0": r["trim"]["1.00"]["elevator"]}
    print("  convergence", json.dumps(out["convergence"]))
    print("  no fins", out["nofins"])
    r, cs = design
    loads = {"_note": "Inputs for C1 (load cases) and C2 (spar, core). Props-off AVL 3.52 + XFOIL, section " + foil
             + f", CG x = {x_sm:.4f} m (5 % static margin), trimmed with the elevons. Loading per unit lift: multiply"
             " by the case lift (n m g / 2 per half). Not included: pod, prop slipstream, fin side loads (B3/B4).",
             "foil": foil, "x_cg_m": x_sm, "Xnp_m": F["Xnp_m"], "CLa_per_rad": r["clean"]["a0"]["CLa"],
             "CLmax_trim": cs["CLmax_trim"], "cases": {}}
    for k in ("0.30", "0.50", "0.80", "0.90", "1.00"):
        d = r["trim"][k]
        loads["cases"][f"CL{k}"] = {"alpha_deg": d["Alpha"], "elevator_deg": d["elevator"],
                                    **span_loads(d["strips"], d["CLtot"])}
    out["design_trim"] = {k: {"alpha": d["Alpha"], "elevator": d["elevator"], "CD": d["CDtot"], "e": d["e"]}
                          for k, d in r["trim"].items()}
    out["design_oswald"] = oswald_fit(r)
    (HERE / "out" / "avl_results.json").write_text(json.dumps(out, indent=1))
    (HERE / "out" / "loads_spanwise.json").write_text(json.dumps(loads, indent=1))


if __name__ == "__main__":
    main()
