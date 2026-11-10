"""B2 verification round (B2-R3): 2-D RANS (SU2 8.5 INC_RANS, Spalart-Allmaras) of the as-designed S5010 section
with the 22 % elevon, to check the two XFOIL inputs that drive requirements and that XFOIL cannot settle alone:

  1. section clmax at the stall Re (drives R-STALL through the trimmed CLmax; XFOIL clmax is unvalidated at Re 2.6e5)
  2. elevon hinge moment at full travel (drives R-SERVO-TORQUE; XFOIL viscous up-elevon cases do not converge, so the
     R2 design value was XFOIL inviscid)

Why CFD here and nowhere else: the spanwise loading, NP and trim are attached-flow quantities that AVL resolves
(3 lattice levels agree to 0.1 %); the two numbers above are viscous, separated-flow numbers. 2-D is enough: the
critical-section method takes section clmax as its input, and the hinge moment is a section integral times span.

Run from the repo root (about 1-2 h on 20 cores; finished cases are cached by config hash):
    python -I redesign/team/B2/sim/cfd2d_section.py           # mesh, run, post
    python -I redesign/team/B2/sim/cfd2d_section.py --post    # post-process cached cases only

Geometry: team/B2/airfoils/s5010.dat re-panelled by XFOIL (PPAR N 260) and deflected by XFOIL GDES FLAP with the
same hinge as xfoil_wing.py (x/c 1 - wing.elevon.chord_frac, 90 % of local thickness = upper-skin tape hinge), so
XFOIL and SU2 see the same contour. Chord-normalised (c = 1); Re = V c / nu with c = wing.chord_m.
Mesh: gmsh, quad boundary layer (BoundaryLayer field, fan at the TE), triangles outside, far field circle R 50 c.
Three levels, uniform refinement ratio r = sqrt(2) in surface spacing, first-cell height, wake and far-field size
(growth ratio^(1/r)): L1 coarse, L2 medium, L3 fine. Convergence by Roache GCI (Fs 1.25) on 3 grid cases.
Outputs: sim/out/cfd/<case>/ (cfg, history, surface CSV, log), sim/out/cfd2d_results.json.
"""
from __future__ import annotations

import concurrent.futures as cf
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
B2 = HERE.parent
REDESIGN = B2.parents[1]
OUT = HERE / "out" / "cfd3"
MESH = HERE / "out" / "mesh3"
OUT.mkdir(parents=True, exist_ok=True)
MESH.mkdir(parents=True, exist_ok=True)
SU2 = Path("C:/Users/dillo/tools/su2/bin/bin/SU2_CFD.exe")
XFOIL = Path("C:/Users/dillo/tools/xfoil/xfoil.exe")
P = json.loads((REDESIGN / "params" / "params.json").read_text(encoding="utf-8"))


def v(path):
    d = P
    for k in path.split("."):
        d = d[k]
    return d["value"]


CHORD = v("wing.chord_m")
XH = 1.0 - v("wing.elevon.chord_frac")
HINGE_YT = 0.9                                 # same as xfoil_wing.py
NU = 1.48e-5                                   # ASM-B2-NU
V_VA = 20.5                                    # m/s, full elevon travel limit (params requirements.vd_ms note, F4 CR-F4-12)
V_VD = v("requirements.vd_ms")                    # 27.2 m/s
V_STALL = v("requirements.stall_max_ms")
RE_STALL = round(V_STALL * CHORD / NU / 1e4) * 1e4      # 2.6e5 at c 0.32
RE_VA = round(V_VA * CHORD / NU / 1e4) * 1e4            # 4.4e5
RE_VD = round(V_VD * CHORD / NU / 1e4) * 1e4            # 5.9e5
D_VD = round(25.0 / 3.0, 2)                             # <= 1/3 travel at VD (F4 envelope, params requirements.vd_ms note)
R_FAR = 50.0
NPAN = 260
R = math.sqrt(2.0)
LEVELS = {1: 0.5, 2: 1 / R, 3: 1.0}                      # refinement factor (L1 ~8k, L2 ~16k, L3 ~32k cells)
BASE = dict(n_surf=1.0, h1=4.0e-5, ratio=1.10, bl_thick=0.025, wake=0.03, far=6.0, surf_max=0.012)
POST = "--post" in sys.argv
THREADS = {1: 1, 2: 1, 3: 1}   # SU2 OpenMP threads per case by level (20-core machine)
WORKERS = 9


# ------------------------------------------------------------------ geometry (XFOIL)
def xfoil_coords(delta):
    f = MESH / f"s5010_f{delta:+.2f}.dat"
    if f.exists():
        return np.loadtxt(f, skiprows=1)
    (MESH / "s5010.dat").write_bytes((B2 / "airfoils" / "s5010.dat").read_bytes())   # XFOIL names <= 64 chars
    cmd = f"PLOP\nG\n\nLOAD s5010.dat\nPPAR\nN {NPAN}\n\n\n"
    if delta:
        cmd += f"GDES\nFLAP\n{XH:.4f}\n999\n{HINGE_YT}\n{delta}\nX\n\nPANE\n"
    cmd += f"PSAV {f.name}\n\nQUIT\n"
    subprocess.run([str(XFOIL)], input=cmd, text=True, capture_output=True, cwd=str(MESH), timeout=60)
    return np.loadtxt(f, skiprows=1)


def hinge_point(delta):
    """Hinge (x, y) as XFOIL places it: x = XH, y = lower + HINGE_YT * (upper - lower) on the undeflected section."""
    c = xfoil_coords(0.0)
    ile = int(np.argmin(c[:, 0]))
    up, lo = c[: ile + 1][::-1], c[ile:]
    yu = float(np.interp(XH, up[:, 0], up[:, 1]))
    yl = float(np.interp(XH, lo[:, 0], lo[:, 1]))
    return XH, yl + HINGE_YT * (yu - yl)


def is_flap(pts, delta):
    """Points that belong to the elevon: rotated back by -delta about the hinge they lie aft of the hinge x."""
    xh, yh = hinge_point(delta)
    t = math.radians(delta)                  # XFOIL: +delta = TE down = clockwise in (x aft, y up)
    dx, dy = pts[:, 0] - xh, pts[:, 1] - yh
    xb = xh + dx * math.cos(t) - dy * math.sin(t)   # rotate counter-clockwise by delta (undo)
    return xb >= xh - 1e-4


# ------------------------------------------------------------------ mesh (gmsh)
def build_mesh(delta, level):
    import gmsh
    tag = f"s5010_f{delta:+.2f}_L{level}"
    out = MESH / f"{tag}.su2"
    info_f = MESH / f"{tag}.json"
    if out.exists() and info_f.exists():
        return json.loads(info_f.read_text())
    k = LEVELS[level]
    p = dict(h1=BASE["h1"] / k, ratio=BASE["ratio"] ** (1 / k), wake=BASE["wake"] / k, far=BASE["far"] / k,
             surf_max=BASE["surf_max"] / k)
    c = xfoil_coords(delta)
    c = c[:-1] if np.hypot(*(c[0] - c[-1])) < 1e-9 else c        # closed TE: one TE point
    n = len(c)
    # split the closed contour at the TE (index 0), the LE and every kink (turning > 6 deg)
    vec_in = c - np.roll(c, 1, axis=0)
    vec_out = np.roll(c, -1, axis=0) - c
    ang = np.degrees(np.abs(np.arctan2(vec_in[:, 0] * vec_out[:, 1] - vec_in[:, 1] * vec_out[:, 0],
                                       (vec_in * vec_out).sum(1))))
    ile = int(np.argmin(c[:, 0]))
    brk = [0, ile]     # XFOIL PANE after FLAP rounds the hinge break over 3-4 panels, so no kink needs its own curve
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add(tag)
    geo = gmsh.model.geo
    ptag = [geo.addPoint(x, y, 0) for x, y in c]
    curves, seg_pts = [], []
    for a, b in zip(brk, brk[1:] + [n]):
        idx = list(range(a, b + 1))
        idx[-1] = idx[-1] % n
        curves.append(geo.addSpline([ptag[i] for i in idx]))
        seg_pts.append(c[[i % n for i in range(a, b + 1)]])
    loop = geo.addCurveLoop(curves)
    pc = geo.addPoint(0.5, 0, 0)
    pe = [geo.addPoint(0.5 + R_FAR * math.cos(t), R_FAR * math.sin(t), 0) for t in (0, math.pi / 2, math.pi, 1.5 * math.pi)]
    arcs = [geo.addCircleArc(pe[i], pc, pe[(i + 1) % 4]) for i in range(4)]
    far = geo.addCurveLoop(arcs)
    surf = geo.addPlaneSurface([far, loop])
    geo.synchronize()
    gmsh.model.addPhysicalGroup(1, curves, name="airfoil")    # elevon panels are picked out geometrically in post
    gmsh.model.addPhysicalGroup(1, arcs, name="farfield")
    gmsh.model.addPhysicalGroup(2, [surf], name="fluid")
    # surface spacing: transfinite with the XFOIL panel clustering (control points per spline x level factor)
    for cv, sp in zip(curves, seg_pts):
        L = float(np.hypot(*np.diff(sp, axis=0).T).sum())
        nn = max(int(round((len(sp) - 1) * k)) + 1, int(math.ceil(L / p["surf_max"])) + 1, 4)
        gmsh.model.mesh.setTransfiniteCurve(cv, nn)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    F = gmsh.model.mesh.field
    fd = F.add("Distance")
    F.setNumbers(fd, "CurvesList", curves)
    F.setNumber(fd, "Sampling", 600)
    ft = F.add("Threshold")
    F.setNumber(ft, "InField", fd)
    F.setNumber(ft, "SizeMin", p["wake"] * 0.6)
    F.setNumber(ft, "SizeMax", p["far"])
    F.setNumber(ft, "DistMin", 0.3)
    F.setNumber(ft, "DistMax", 25.0)
    fb = F.add("Box")
    F.setNumber(fb, "VIn", p["wake"])
    F.setNumber(fb, "VOut", p["far"])
    for kk, val in (("XMin", -0.2), ("XMax", 4.0), ("YMin", -0.8), ("YMax", 1.0), ("Thickness", 2.0)):
        F.setNumber(fb, kk, val)
    fm = F.add("Min")
    F.setNumbers(fm, "FieldsList", [ft, fb])
    F.setAsBackgroundMesh(fm)
    fbl = F.add("BoundaryLayer")
    F.setNumbers(fbl, "CurvesList", curves)
    F.setNumbers(fbl, "FanPointsList", [ptag[0]])
    F.setNumber(fbl, "Size", p["h1"])
    F.setNumber(fbl, "Ratio", p["ratio"])
    F.setNumber(fbl, "Quads", 1)
    F.setNumber(fbl, "Thickness", BASE["bl_thick"])
    F.setAsBoundaryLayer(fbl)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.option.setNumber("Mesh.Smoothing", 5)
    t0 = time.time()
    gmsh.model.mesh.generate(2)
    _, etags, _ = gmsh.model.mesh.getElements(2)
    ncell = int(sum(len(t) for t in etags))
    gmsh.option.setNumber("Mesh.SaveAll", 0)
    gmsh.write(str(out))
    gmsh.finalize()
    nl = math.log(1 + BASE["bl_thick"] * (p["ratio"] - 1) / p["h1"]) / math.log(p["ratio"])
    info = {"tag": tag, "level": level, "delta": delta, "cells": ncell, "h1": p["h1"], "ratio": p["ratio"],
            "bl_layers": round(nl, 1), "surf_max": p["surf_max"], "wake": p["wake"], "far": p["far"], "R_far": R_FAR,
            "splines": len(curves), "mesh_s": round(time.time() - t0, 1)}
    info_f.write_text(json.dumps(info))
    print(f"  mesh {tag}: {ncell} cells, BL {info['bl_layers']} layers, {info['mesh_s']} s", flush=True)
    return info


# ------------------------------------------------------------------ SU2
def cfg_text(mesh_name, alpha, re_):
    a = math.radians(alpha)
    return f"""% B2-R3 SU2 8.5 INC_RANS SA, S5010 + 22 % elevon, chord 1, Re {re_:.0f} (team/B2/sim/cfd2d_section.py)
SOLVER= INC_RANS
KIND_TURB_MODEL= SA
MATH_PROBLEM= DIRECT
RESTART_SOL= NO
INC_DENSITY_MODEL= CONSTANT
INC_DENSITY_INIT= 1.0
INC_VELOCITY_INIT= ( {math.cos(a):.8f}, {math.sin(a):.8f}, 0.0 )
INC_NONDIM= INITIAL_VALUES
VISCOSITY_MODEL= CONSTANT_VISCOSITY
MU_CONSTANT= {1.0 / re_:.8e}
FREESTREAM_TURBULENCEINTENSITY= 0.001
FREESTREAM_TURB2LAMVISCRATIO= 10.0
AOA= {alpha}
REF_ORIGIN_MOMENT_X= 0.25
REF_ORIGIN_MOMENT_Y= 0.0
REF_ORIGIN_MOMENT_Z= 0.0
REF_LENGTH= 1.0
REF_AREA= 1.0
MARKER_HEATFLUX= ( airfoil, 0.0 )
MARKER_FAR= ( farfield )
MARKER_PLOTTING= ( airfoil )
MARKER_MONITORING= ( airfoil )
NUM_METHOD_GRAD= WEIGHTED_LEAST_SQUARES
CFL_NUMBER= 5.0
CFL_ADAPT= YES
CFL_ADAPT_PARAM= ( 0.5, 1.2, 1.0, 30.0 )
ITER= 2000
LINEAR_SOLVER= FGMRES
LINEAR_SOLVER_PREC= ILU
LINEAR_SOLVER_ERROR= 1E-4
LINEAR_SOLVER_ITER= 15
CONV_NUM_METHOD_FLOW= FDS
MUSCL_FLOW= YES
SLOPE_LIMITER_FLOW= VENKATAKRISHNAN
VENKAT_LIMITER_COEFF= 0.05
TIME_DISCRE_FLOW= EULER_IMPLICIT
CONV_NUM_METHOD_TURB= SCALAR_UPWIND
MUSCL_TURB= NO
TIME_DISCRE_TURB= EULER_IMPLICIT
CONV_FIELD= ( LIFT, DRAG, MOMENT_Z )
CONV_STARTITER= 300
CONV_CAUCHY_ELEMS= 200
CONV_CAUCHY_EPS= 1E-5
MESH_FILENAME= {mesh_name}
MESH_FORMAT= SU2
TABULAR_FORMAT= CSV
CONV_FILENAME= history
SURFACE_FILENAME= surface_flow
OUTPUT_FILES= ( SURFACE_CSV )
VOLUME_OUTPUT= ( COORDINATES, SOLUTION, PRIMITIVE )
OUTPUT_WRT_FREQ= 100000
HISTORY_OUTPUT= ( ITER, RMS_RES, AERO_COEFF, CAUCHY )
SCREEN_OUTPUT= ( INNER_ITER, RMS_PRESSURE, LIFT, DRAG )
SCREEN_WRT_FREQ_INNER= 200
"""


def case_dir(delta, alpha, re_, level):
    return OUT / f"f{delta:+.2f}_a{alpha:+05.1f}_re{re_/1e5:.1f}e5_L{level}"


def run_case(delta, alpha, re_, level):
    d = case_dir(delta, alpha, re_, level)
    d.mkdir(exist_ok=True)
    info = build_mesh(delta, level)
    mesh = MESH / f"{info['tag']}.su2"
    cfg = cfg_text(mesh.name, alpha, re_)      # SU2 rejects a drive-letter path: the mesh is copied in for the run
    sha = hashlib.sha1((cfg + str(mesh.stat().st_size)).encode()).hexdigest()[:16]
    done = d / "done.json"
    if done.exists() and json.loads(done.read_text()).get("sha") == sha:
        return
    if POST:
        return
    (d / "case.cfg").write_text(cfg)
    (d / mesh.name).write_bytes(mesh.read_bytes())
    t0 = time.time()
    with open(d / "su2.log", "w") as log:
        p = subprocess.run([str(SU2), "-t", str(THREADS[level]), "case.cfg"], cwd=str(d), stdout=log,
                           stderr=subprocess.STDOUT, text=True)
    for f in list(d.glob("restart*")) + list(d.glob("*.su2")):
        f.unlink()
    done.write_text(json.dumps({"sha": sha, "rc": p.returncode, "wall_s": round(time.time() - t0, 1)}))
    print(f"  done {d.name} rc {p.returncode} {time.time() - t0:.0f} s", flush=True)


# ------------------------------------------------------------------ post-processing
def num(s):
    try:
        return float(s)
    except ValueError:
        return float("nan")


def read_history(d):
    f = d / "history.csv"
    if not f.exists():
        return None
    rows = list(csv.reader(f.open()))
    head = [h.strip().strip('"') for h in rows[0]]
    data = np.array([[num(x) for x in r] for r in rows[1:] if len(r) == len(head)])
    return head, data


def contour_order(delta, pts):
    """Order surface points along the XFOIL contour (TE -> upper -> LE -> lower -> TE) by nearest arc length."""
    c = xfoil_coords(delta)
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(c, axis=0).T))])
    # dense resample of the contour for the nearest-point search
    sd = np.linspace(0, s[-1], 20000)
    cd = np.c_[np.interp(sd, s, c[:, 0]), np.interp(sd, s, c[:, 1])]
    j = np.array([int(np.argmin((cd[:, 0] - x) ** 2 + (cd[:, 1] - y) ** 2)) for x, y in pts])
    return np.argsort(sd[j], kind="stable")


def integrate(delta, alpha, d):
    """cl, cd, cm(c/4) of the whole section and hinge moment coefficient H/(q c^2) of the elevon (positive = TE down,
    XFOIL sign) from the surface CSV (pressure + skin friction), by trapezoid panels between ordered surface nodes."""
    f = d / "surface_flow.csv"
    rows = list(csv.reader(f.open()))
    head = [h.strip().strip('"') for h in rows[0]]
    a = np.array([[num(x) for x in r] for r in rows[1:]])
    col = {h: i for i, h in enumerate(head)}
    xy = a[:, [col["x"], col["y"]]]
    # SU2 8.5 SURFACE_CSV (INC) carries gauge pressure only; with INC_NONDIM INITIAL_VALUES (rho 1, V 1) q = 0.5,
    # so Cp = 2 p. Skin friction is left out: its moment arm about the hinge is the local half-thickness
    # (<= 0.012 c), so it changes ch by < 1e-5 (Cf 0.005 x 0.22 c x 0.01 c); cd is taken from SU2's own CD
    cp = 2.0 * a[:, col["Pressure"]]
    cfx = np.zeros_like(cp)
    cfy = np.zeros_like(cp)
    o = contour_order(delta, xy)
    xy, cp, cfx, cfy = xy[o], cp[o], cfx[o], cfy[o]
    flap = is_flap(xy, delta) if delta else xy[:, 0] > XH
    xh, yh = hinge_point(delta)
    # panels i -> i+1 (closed); outward normal for a clockwise-ordered contour (TE -> upper -> LE -> lower)
    x2, y2 = np.roll(xy[:, 0], -1), np.roll(xy[:, 1], -1)
    dx, dy = x2 - xy[:, 0], y2 - xy[:, 1]
    ds = np.hypot(dx, dy)
    nx, ny = -dy / ds, dx / ds
    xm, ym = 0.5 * (xy[:, 0] + x2), 0.5 * (xy[:, 1] + y2)
    cpm = 0.5 * (cp + np.roll(cp, -1))
    fx = (-cpm * nx + 0.5 * (cfx + np.roll(cfx, -1))) * ds
    fy = (-cpm * ny + 0.5 * (cfy + np.roll(cfy, -1))) * ds
    # orientation check: the outward normal must point away from the centroid on average
    if np.mean((xm - xm.mean()) * nx + (ym - ym.mean()) * ny) < 0:
        fx, fy = (cpm * nx + 0.5 * (cfx + np.roll(cfx, -1))) * ds, (cpm * ny + 0.5 * (cfy + np.roll(cfy, -1))) * ds
    ar = math.radians(alpha)
    cl = float((fy * math.cos(ar) - fx * math.sin(ar)).sum())
    cdv = float((fx * math.cos(ar) + fy * math.sin(ar)).sum())
    cm = float((-((xm - 0.25) * fy - ym * fx)).sum())                 # nose-up positive
    pf = flap & np.roll(flap, -1)
    ch = float((-((xm[pf] - xh) * fy[pf] - (ym[pf] - yh) * fx[pf])).sum())   # TE-up nose-up sense = XFOIL HMOM sign
    return {"cl_int": cl, "cd_int": cdv, "cm_int": cm, "ch": ch, "n_surf": int(len(xy)), "n_flap": int(flap.sum())}


def post_case(delta, alpha, re_, level):
    d = case_dir(delta, alpha, re_, level)
    h = read_history(d)
    if h is None or not (d / "surface_flow.csv").exists():
        return None
    head, data = h
    ci = {k: i for i, k in enumerate(head)}
    last = data[-200:] if len(data) > 200 else data
    r = {"delta": delta, "alpha": alpha, "re": re_, "level": level, "iters": int(data[-1, ci["Inner_Iter"]]) + 1,
         "CL": float(data[-1, ci["CL"]]), "CD": float(data[-1, ci["CD"]]), "CMz": float(data[-1, ci["CMz"]]),
         "CL_osc_last200": float(last[:, ci["CL"]].max() - last[:, ci["CL"]].min()),
         "rms_p": float(data[-1, ci["rms[P]"]]), "rms_p_drop": float(data[0, ci["rms[P]"]] - data[-1, ci["rms[P]"]])}
    r.update(integrate(delta, alpha, d))
    r["usable"] = bool(np.isfinite(r["CL"]) and r["CL_osc_last200"] < 0.01 and abs(r["CL"] - r["cl_int"]) < 0.02)
    info = json.loads((MESH / f"s5010_f{delta:+.2f}_L{level}.json").read_text())
    r["cells"] = info["cells"]
    dj = d / "done.json"
    if dj.exists():
        r["wall_s"] = json.loads(dj.read_text()).get("wall_s")
    return r


def gci(f1, f2, f3, r=R):
    """Roache GCI on fine (f1), medium (f2), coarse (f3): observed order p, Richardson value, GCI_fine (Fs 1.25)."""
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 or e32 == 0 or e32 / e21 <= 0:
        return {"p": None, "f_exact": None, "gci_fine": abs(e21) * 1.25 * 3 / max(abs(f1), 1e-9), "monotone": False,
                "note": "oscillatory or flat: GCI = 3 Fs |e21| (Roache, conservative)"}
    p = math.log(e32 / e21) / math.log(r)
    p_use = min(max(p, 0.5), 2.0)
    fx = f1 + (f1 - f2) / (r ** p_use - 1)
    return {"p": p, "p_used": p_use, "f_exact": fx, "gci_fine": 1.25 * abs(e21 / f1) / (r ** p_use - 1), "monotone": True}


# ------------------------------------------------------------------ cases
# Scope is set by cost: on the shared design machine (14 other SU2 jobs running on 2026-11-10) SU2 ran at
# 3-10 s per iteration per 32k cells, so the grid study is the one case that sets the servo requirement (3 levels)
# and the rest is one L2 case each where a requirement reads it. A first campaign at 16k/32k/64k cells (out/cfd,
# out/mesh) was stopped after ~170 iterations and is not used. A second one (out/cfd2: base growth 1.20, so
# L1/L2 grew at 1.44/1.29 per layer) gave cd 0.026 at alpha 4 (XFOIL 0.010) and a stalled alpha 12: the wall-normal
# resolution was too coarse, so it is discarded and the base growth is 1.10 (L1 1.21, L2 1.14, L3 1.10).
CONV = [(-25.0, 0.0, RE_VA)]
SWEEP_CLEAN = [(0.0, a, RE_STALL) for a in (4.0, 8.0, 11.0, 13.0)]
SWEEP_HINGE = [(-25.0, -4.0, RE_VA), (25.0, 4.0, RE_VA), (-D_VD, 2.0, RE_VD)]


def main():
    t0 = time.time()
    jobs = [(d, a, r, L) for (d, a, r) in CONV for L in (1, 2, 3)] + \
           [(d, a, r, 2) for (d, a, r) in SWEEP_CLEAN + SWEEP_HINGE]
    for dl in sorted({j[0] for j in jobs}):
        xfoil_coords(dl)
        for L in sorted({j[3] for j in jobs if j[0] == dl}):
            build_mesh(dl, L)
    if not POST:
        with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
            list(ex.map(lambda j: run_case(*j), sorted(jobs, key=lambda j: -j[3])))
    res = {"tool": "SU2 8.5.0 INC_RANS SA (https://su2code.github.io), gmsh 4.15 (https://gmsh.info)",
           "chord_m": CHORD, "x_hinge_c": XH, "hinge_y_t": HINGE_YT, "re": {"stall": RE_STALL, "va": RE_VA, "vd": RE_VD},
           "v_ms": {"stall": V_STALL, "va": V_VA, "vd": V_VD}, "d_vd_deg": D_VD, "levels": LEVELS, "base": BASE,
           "cases": [], "gci": {}}
    for j in jobs:
        r = post_case(*j)
        if r:
            res["cases"].append(r)
    for (dl, a, re_) in CONV:
        rs = {c["level"]: c for c in res["cases"] if c["delta"] == dl and c["alpha"] == a and c["re"] == re_}
        if all(L in rs for L in (1, 2, 3)):
            key = f"f{dl:+g}_a{a:g}_re{re_/1e5:.1f}e5"
            res["gci"][key] = {q: {"L1": rs[1][q], "L2": rs[2][q], "L3": rs[3][q], **gci(rs[3][q], rs[2][q], rs[1][q])}
                               for q in ("CL", "CD", "CMz", "ch")}
            res["gci"][key]["cells"] = [rs[L]["cells"] for L in (1, 2, 3)]
    res["wall_s"] = round(time.time() - t0, 1)
    (HERE / "out" / "cfd2d_results.json").write_text(json.dumps(res, indent=1))
    for c in res["cases"]:
        print(f"  d {c['delta']:+6.2f} a {c['alpha']:+5.1f} Re {c['re']:.2e} L{c['level']}: CL {c['CL']:.4f} "
              f"(int {c['cl_int']:.4f}) CD {c['CD']:.5f} CM {c['CMz']:+.4f} (int {c['cm_int']:+.4f}) ch {c['ch']:+.5f} "
              f"osc {c['CL_osc_last200']:.4f} it {c['iters']} usable {c['usable']}")
    for k, g in res["gci"].items():
        print(f"  GCI {k}: " + "  ".join(f"{q} {g[q]['L3']:.4f} gci {g[q]['gci_fine']*100:.2f}%" for q in ("CL", "CD", "CMz", "ch")))


if __name__ == "__main__":
    if "--mesh" in sys.argv:
        for dl in (0.0, -25.0, 25.0):
            for L in (1, 2, 3):
                build_mesh(dl, L)
    else:
        main()
