"""B3 verification round: 2-D RANS (SU2 8.5) cross-check of the elevon effectiveness eta on the S5010 section.

Why CFD here. The forward CG limit (CL-B3-CG-FWD) is set by the elevon trim budget at the trimmed stall, and its
largest single sensitivity is the elevon effectiveness eta = (dcm/ddelta)_viscous / (dcm/ddelta)_thin-airfoil
(CL-B2-ELEVON-ETA 0.606, XFOIL). A -20 % eta closes the CG range (S-AND-C.md, CR-B3-13). XFOIL is the only source
for that number, and XFOIL is known to under-predict plain-flap effectiveness when a laminar bubble sits at the
hinge kink. An independent viscous method on the same geometry is therefore the highest-fidelity check the decision
justifies. Everything else in the S&C chain is either linear (VLM is adequate) or set by measured hardware.

Method
  geometry  XFOIL GDES FLAP on the S5010 (UIUC coordinates, team/B3/avl/s5010.dat), hinge x/c 0.78 at 90 % of the local
            thickness (tape hinge on the upper skin, same as B2), then PANE 300: the SAME paneled geometry feeds XFOIL
            and the SU2 mesh, so the comparison isolates the flow model.
  mesh      gmsh, chord 1, circular far field R 50 c, quad boundary layer (first cell 8e-5 / 5.7e-5 / 4e-5 c, y+ < 1.1
            at Re 2.6e5), triangles outside, wake box to 5 c. Three levels, surface and field spacing refined by
            sqrt(2) per level (cells x ~2), so r = sqrt(2) for the GCI (Celik et al. 2008).
  solver    SU2 INC_RANS, SA fully turbulent (mesh study and main result) and SST + Langtry-Menter LM (transition
            sensitivity, medium mesh), Re 2.6e5 (the stall speed 12 m/s on c 0.32 m, where the forward limit binds),
            alpha 4 deg (and 8 deg on the medium mesh for the cl = 0.5 interpolation), elevon 0 and -10 deg (TE up).
  output    cm about c/4 (aero sign: cm = -CMz of SU2), cl, cd per case; eta_cm at fixed alpha and at cl 0.5;
            eta_cl; GCI of each; XFOIL at the same Re / alpha / geometry with 3 panel counts (160 / 240 / 320).

Run: python -I redesign/team/B3/cfd_elevon.py           (~40-60 min on 20 cores the first time; then cached)
     python -I redesign/team/B3/cfd_elevon.py --parse   (re-read finished cases only)
Writes team/B3/cfd/geom/*.dat, cfd/mesh/*.su2 (git-ignored), cfd/cases/<case>/{case.cfg,history.csv,
surface_flow.csv,done.txt}, cfd/cfd_results.json.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "cfd"
GEOM, MESH, CASES = OUT / "geom", OUT / "mesh", OUT / "cases"
XFOIL = Path("C:/Users/dillo/tools/xfoil/xfoil.exe")
SU2 = Path("C:/Users/dillo/tools/su2/bin/bin/SU2_CFD.exe")
AIRFOIL = HERE / "avl" / "s5010.dat"

PARAMS = json.loads((HERE.parents[1] / "params" / "params.json").read_text())
CHORD = PARAMS["wing"]["chord_m"]["value"]                          # 0.32 m
HINGE_X = 1.0 - PARAMS["wing"]["elevon"]["chord_frac"]["value"]     # 0.78
HINGE_YT = 0.9                                                       # tape hinge on the upper skin (B2 uses 0.9)
V_STALL = PARAMS["requirements"]["stall_max_ms"]["value"]           # 12 m/s
RHO, MU_AIR = 1.225, 1.789e-5                                        # ISA sea level
RE = round(RHO * V_STALL * CHORD / MU_AIR / 1e4) * 1e4              # 2.6e5
V_CFD = 12.0                                                          # any V: Re is set through MU on chord 1
MU_CFD = RHO * V_CFD * 1.0 / RE
R_FAR = 50.0
DELTAS = [0.0, -10.0]
NCRIT = 9.0

LEVELS = {   # surface nodes per side, first cell, BL growth, layers, near-wall/wake size, far size
    1: dict(n_side=110, h1=8.0e-5, ratio=1.22, nlayers=24, wake=0.028, far=5.0),
    2: dict(n_side=156, h1=5.7e-5, ratio=1.17, nlayers=31, wake=0.020, far=3.5),
    3: dict(n_side=220, h1=4.0e-5, ratio=1.12, nlayers=42, wake=0.014, far=2.5),
}
THIN_CMD = -0.5 * math.sin(math.acos(1 - 2 * HINGE_X)) * (1 - math.cos(math.acos(1 - 2 * HINGE_X)))  # /rad
_th = math.acos(1 - 2 * HINGE_X)
THIN_CLD = 2 * (math.pi - _th + math.sin(_th))                                                       # /rad


# ------------------------------------------------------------------------------------------- geometry (XFOIL)
def geometry(delta: float) -> list:
    """Paneled S5010 with the elevon at delta (deg, + TE down), 300 points, TE closed. Cached in cfd/geom."""
    GEOM.mkdir(parents=True, exist_ok=True)
    f = GEOM / f"s5010_d{delta:+.0f}.dat"
    if not f.exists():
        tmp = Path(tempfile.mkdtemp(prefix="b3g_"))
        try:
            shutil.copy(AIRFOIL, tmp / "af.dat")
            cmd = ["PLOP", "G", "", "LOAD af.dat", "PPAR", "N 300", "", ""]
            if delta:
                cmd += ["GDES", "FLAP", f"{HINGE_X}", "999", f"{HINGE_YT}", f"{delta}", "X", ""]
            cmd += ["PANE", "SAVE g.dat", "Y", "QUIT"]
            subprocess.run([str(XFOIL)], input="\n".join(cmd) + "\n", text=True, capture_output=True, cwd=str(tmp),
                           timeout=60)
            txt = (tmp / "g.dat").read_text().splitlines()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        f.write_text("\n".join([f"S5010 elevon {delta:+.0f} deg, hinge {HINGE_X} c / {HINGE_YT} t (XFOIL GDES FLAP + PANE)"]
                               + txt[1:]) + "\n")
    pts = [tuple(map(float, l.split())) for l in f.read_text().splitlines()[1:] if l.strip()]
    return pts


# ------------------------------------------------------------------------------------------- mesh (gmsh)
def mesh(delta: float, level: int) -> dict:
    import gmsh
    MESH.mkdir(parents=True, exist_ok=True)
    out = MESH / f"s5010_d{delta:+.0f}_L{level}.su2"
    info_f = out.with_suffix(".json")
    if out.exists() and info_f.exists():
        return json.loads(info_f.read_text())
    p = LEVELS[level]
    pts = geometry(delta)
    # close the TE exactly (average of the first and last point), drop the duplicate
    te = ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2)
    pts = [te] + pts[1:-1]
    i_le = min(range(len(pts)), key=lambda k: pts[k][0])
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add(out.stem)
    occ = gmsh.model.occ
    tags = [occ.addPoint(x, y, 0) for x, y in pts]
    up = occ.addSpline(tags[: i_le + 1])
    lo = occ.addSpline(tags[i_le:] + [tags[0]])
    foil = occ.addCurveLoop([up, lo])
    circ = occ.addCircle(0.5, 0, 0, R_FAR)
    surf = occ.addPlaneSurface([occ.addCurveLoop([circ]), foil])
    occ.synchronize()
    gmsh.model.addPhysicalGroup(1, [up, lo], name="airfoil")
    gmsh.model.addPhysicalGroup(1, [circ], name="farfield")
    gmsh.model.addPhysicalGroup(2, [surf], name="fluid")
    for k, v in (("Mesh.MeshSizeExtendFromBoundary", 0), ("Mesh.MeshSizeFromPoints", 0),
                 ("Mesh.MeshSizeFromCurvature", 0)):
        gmsh.option.setNumber(k, v)
    fld = gmsh.model.mesh.field
    f_dist = fld.add("Distance")
    fld.setNumbers(f_dist, "CurvesList", [up, lo])
    fld.setNumber(f_dist, "Sampling", 600)
    f_thr = fld.add("Threshold")
    fld.setNumber(f_thr, "InField", f_dist)
    fld.setNumber(f_thr, "SizeMin", p["wake"] * 0.6)
    fld.setNumber(f_thr, "SizeMax", p["far"])
    fld.setNumber(f_thr, "DistMin", 0.4)
    fld.setNumber(f_thr, "DistMax", 20.0)
    f_box = fld.add("Box")
    fld.setNumber(f_box, "VIn", p["wake"])
    fld.setNumber(f_box, "VOut", p["far"])
    for k, v in (("XMin", -0.3), ("XMax", 5.0), ("YMin", -0.8), ("YMax", 1.0), ("Thickness", 2.5)):
        fld.setNumber(f_box, k, v)
    f_min = fld.add("Min")
    fld.setNumbers(f_min, "FieldsList", [f_thr, f_box])
    fld.setAsBackgroundMesh(f_min)
    f_bl = fld.add("BoundaryLayer")
    fld.setNumbers(f_bl, "CurvesList", [up, lo])
    fld.setNumbers(f_bl, "FanPointsList", [tags[0]])
    fld.setNumber(f_bl, "Size", p["h1"])
    fld.setNumber(f_bl, "Ratio", p["ratio"])
    fld.setNumber(f_bl, "Quads", 1)
    thick = p["h1"] * (p["ratio"] ** p["nlayers"] - 1) / (p["ratio"] - 1)
    fld.setNumber(f_bl, "Thickness", thick)
    fld.setAsBoundaryLayer(f_bl)
    gmsh.model.mesh.setTransfiniteCurve(up, p["n_side"], "Bump", 0.12)
    gmsh.model.mesh.setTransfiniteCurve(lo, p["n_side"], "Bump", 0.12)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.option.setNumber("Mesh.Smoothing", 5)
    t0 = time.time()
    gmsh.model.mesh.generate(2)
    _, etags, _ = gmsh.model.mesh.getElements(2)
    info = {"level": level, "delta": delta, "cells": int(sum(len(t) for t in etags)),
            "nodes": int(len(gmsh.model.mesh.getNodes()[0])), "bl_thickness_c": thick, **p, "R_far_c": R_FAR,
            "mesh_s": round(time.time() - t0, 1), "file": out.name}
    gmsh.option.setNumber("Mesh.SaveAll", 0)
    gmsh.write(str(out))
    gmsh.finalize()
    info_f.write_text(json.dumps(info, indent=1))
    print(f"  mesh d{delta:+.0f} L{level}: {info['cells']} cells")
    return info


# ------------------------------------------------------------------------------------------- SU2
CFG = """% B3 cfd_elevon.py: S5010 elevon {delta:+.0f} deg, alpha {alpha} deg, Re {Re:.0f}, {model}, mesh L{level}
SOLVER= INC_RANS
KIND_TURB_MODEL= {turb}
{trans}
MATH_PROBLEM= DIRECT
RESTART_SOL= NO
INC_DENSITY_MODEL= CONSTANT
INC_DENSITY_INIT= {rho}
INC_VELOCITY_INIT= ( {vx:.6f}, {vy:.6f}, 0.0 )
INC_NONDIM= INITIAL_VALUES
VISCOSITY_MODEL= CONSTANT_VISCOSITY
MU_CONSTANT= {mu:.8e}
FREESTREAM_TURBULENCEINTENSITY= {ti}
FREESTREAM_TURB2LAMVISCRATIO= {tlr}
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
CFL_NUMBER= {cfl}
CFL_ADAPT= YES
CFL_ADAPT_PARAM= ( 0.5, 1.2, 1.0, {cflmax} )
ITER= {iters}
LINEAR_SOLVER= FGMRES
LINEAR_SOLVER_PREC= LU_SGS
LINEAR_SOLVER_ERROR= 1E-5
LINEAR_SOLVER_ITER= 10
CONV_NUM_METHOD_FLOW= FDS
MUSCL_FLOW= YES
SLOPE_LIMITER_FLOW= VENKATAKRISHNAN
VENKAT_LIMITER_COEFF= 0.05
LIMITER_ITER= {limfreeze}
TIME_DISCRE_FLOW= EULER_IMPLICIT
CONV_NUM_METHOD_TURB= SCALAR_UPWIND
MUSCL_TURB= NO
TIME_DISCRE_TURB= EULER_IMPLICIT
CONV_FIELD= ( RMS_PRESSURE, LIFT, MOMENT_Z )
CONV_RESIDUAL_MINVAL= -9
CONV_STARTITER= 300
CONV_CAUCHY_ELEMS= 200
CONV_CAUCHY_EPS= 2E-6
MESH_FILENAME= {mesh}
MESH_FORMAT= SU2
TABULAR_FORMAT= CSV
CONV_FILENAME= history
SURFACE_FILENAME= surface_flow
OUTPUT_FILES= ( SURFACE_CSV )
OUTPUT_WRT_FREQ= 100000
HISTORY_OUTPUT= ( ITER, RMS_RES, AERO_COEFF, CAUCHY )
SCREEN_OUTPUT= ( INNER_ITER, RMS_PRESSURE, LIFT, DRAG, MOMENT_Z )
SCREEN_WRT_FREQ_INNER= 200
"""


def case_list():
    c = [(L, d, 4.0, "SA") for L in (1, 2, 3) for d in DELTAS]
    c += [(2, d, 8.0, "SA") for d in DELTAS]
    c += [(2, d, 4.0, "SSTLM") for d in DELTAS]
    return c


def case_name(level, delta, alpha, model):
    return f"L{level}_{model}_d{delta:+.0f}_a{alpha:.0f}".replace("+", "p").replace("-", "m")


def case_cfg(level, delta, alpha, model, safe=False):
    a = math.radians(alpha)
    if model == "SA":
        turb, trans, ti, tlr = "SA", "", 0.001, 10.0
    else:   # Tu 0.07 % ~ Ncrit 9 (Mack 1977)
        turb, trans, ti, tlr = "SST", "KIND_TRANS_MODEL= LM", 0.0007, 1.0
    cfl, cflmax, lim, it = (0.5, 10.0, 1500, 8000) if safe else (2.0, 50.0, 400, 5000)
    return CFG.format(delta=delta, alpha=alpha, Re=RE, model=model, level=level, turb=turb, trans=trans, rho=RHO,
                      vx=V_CFD * math.cos(a), vy=V_CFD * math.sin(a), mu=MU_CFD, ti=ti, tlr=tlr, cfl=cfl,
                      cflmax=cflmax, iters=it, limfreeze=lim, mesh=f"s5010_d{delta:+.0f}_L{level}.su2")


def _num(v):
    try:
        return float(v)
    except ValueError:
        return float("nan")


def parse(d: Path) -> dict:
    h = d / "history.csv"
    if not h.exists():
        return {"usable": False, "reason": "no history"}
    rows = list(csv.reader(open(h)))
    hdr = [x.strip().strip('"') for x in rows[0]]
    data = [[_num(v) for v in r] for r in rows[1:] if len(r) == len(hdr)]
    if len(data) < 50:
        return {"usable": False, "reason": "short history"}
    col = {k: i for i, k in enumerate(hdr)}
    tail = data[-300:]
    mean = lambda k: sum(r[col[k]] for r in tail) / len(tail)   # noqa: E731
    std = lambda k: (sum((r[col[k]] - mean(k)) ** 2 for r in tail) / len(tail)) ** 0.5   # noqa: E731
    rp0, rp1 = data[0][col["rms[P]"]], data[-1][col["rms[P]"]]
    cl, cd, cmz = mean("CL"), mean("CD"), mean("CMz")
    ok = all(math.isfinite(x) for x in (cl, cd, cmz)) and cd > 0 and abs(cl) < 2.5 and rp1 < rp0
    done = json.loads((d / "done.json").read_text()) if (d / "done.json").exists() else {}
    return {"cl": cl, "cd": cd, "cm": -cmz, "cl_std": std("CL"), "cm_std": std("CMz"), "iters": len(data),
            "rmsP_drop": rp0 - rp1, "steady": std("CL") < 2e-3 and std("CMz") < 5e-4, "usable": bool(ok),
            "reason": None if ok else "diverged or non-physical", "wall_s": done.get("wall_s"),
            "attempt": done.get("attempt")}


def run_case(spec, threads=2, parse_only=False):
    level, delta, alpha, model = spec
    d = CASES / case_name(*spec)
    d.mkdir(parents=True, exist_ok=True)
    for safe in (False, True):
        cfg = case_cfg(level, delta, alpha, model, safe)
        key = hashlib.sha1(cfg.encode()).hexdigest()[:12]
        done = json.loads((d / "done.json").read_text()) if (d / "done.json").exists() else {}
        if done.get("key") == key or (parse_only and done):
            r = parse(d)
            if r["usable"] or safe or parse_only:
                return {**r, "case": d.name}
            continue
        if parse_only:
            return {"usable": False, "reason": "not run", "case": d.name}
        (d / "case.cfg").write_text(cfg)
        shutil.copy(MESH / f"s5010_d{delta:+.0f}_L{level}.su2", d / f"s5010_d{delta:+.0f}_L{level}.su2")
        t0 = time.time()
        with open(d / "su2.log", "w") as log:
            p = subprocess.run([str(SU2), "-t", str(threads), "case.cfg"], cwd=str(d), stdout=log,
                               stderr=subprocess.STDOUT, text=True)
        for f in list(d.glob("*.su2")) + list(d.glob("restart*")) + list(d.glob("*.vtu")):
            f.unlink()
        (d / "done.json").write_text(json.dumps({"key": key, "rc": p.returncode, "wall_s": round(time.time() - t0),
                                                 "attempt": 2 if safe else 1}))
        r = parse(d)
        print(f"  {d.name}: cl {r.get('cl', float('nan')):.4f} cm {r.get('cm', float('nan')):.4f} "
              f"usable {r['usable']} {time.time() - t0:.0f} s")
        if r["usable"]:
            return {**r, "case": d.name}
    return {**r, "case": d.name}


# ------------------------------------------------------------------------------------------- XFOIL reference
def xfoil(delta, npan, alphas=(2.0, 4.0, 6.0, 8.0)):
    """XFOIL on the same flapped geometry file (re-paneled to npan), Re, Ncrit 9. Returns {alpha: (cl, cd, cm)}."""
    f = OUT / "xfoil" / f"d{delta:+.0f}_p{npan}.txt"
    f.parent.mkdir(parents=True, exist_ok=True)
    if not f.exists():
        geometry(delta)
        tmp = Path(tempfile.mkdtemp(prefix="b3x_"))
        try:
            shutil.copy(GEOM / f"s5010_d{delta:+.0f}.dat", tmp / "g.dat")
            cmd = ["PLOP", "G", "", "LOAD g.dat", "PPAR", f"N {npan}", "", "", "OPER", f"VISC {RE:.0f}", "VPAR",
                   f"N {NCRIT}", "", "ITER 300", "PACC", "p.txt", ""]
            for a in (0.0, 1.0) + tuple(alphas):
                cmd += [f"A {a}"]
            cmd += ["PACC", "", "QUIT"]
            subprocess.run([str(XFOIL)], input="\n".join(cmd) + "\n", text=True, capture_output=True, cwd=str(tmp),
                           timeout=120)
            f.write_text((tmp / "p.txt").read_text())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    out = {}
    for line in f.read_text().splitlines()[12:]:
        p = line.split()
        if len(p) >= 5:
            out[float(p[0])] = (float(p[1]), float(p[2]), float(p[4]))
    return out


# ------------------------------------------------------------------------------------------- post-processing
def gci(f1, f2, f3, r=math.sqrt(2.0), Fs=1.25):
    """Celik et al. 2008: f1 fine, f2 medium, f3 coarse, constant r."""
    e21, e32 = f2 - f1, f3 - f2
    if abs(e21) < 1e-12 or abs(e32) < 1e-12 or e32 / e21 <= 0:
        return {"p": None, "f_ext": None, "GCI_fine_pct": None, "note": "oscillatory or flat; GCI undefined",
                "spread_pct": 100 * (max(f1, f2, f3) - min(f1, f2, f3)) / abs(f1)}
    p = abs(math.log(abs(e32 / e21))) / math.log(r)
    f_ext = (r ** p * f1 - f2) / (r ** p - 1)
    return {"p": p, "f_ext": f_ext, "GCI_fine_pct": 100 * Fs * abs(e21 / f1) / (r ** p - 1)}


def eta_cm(cm_d, cm_0, delta):
    return (cm_d - cm_0) / math.radians(delta) / THIN_CMD


def eta_cl(cl_d, cl_0, delta):
    return (cl_d - cl_0) / math.radians(delta) / THIN_CLD


def cm_at_cl(pairs, cl_t=0.5):
    """Linear interpolation of cm at cl_t from [(cl, cm), ...] (two or more points)."""
    pairs = sorted(pairs)
    for (c0, m0), (c1, m1) in zip(pairs, pairs[1:]):
        if c0 <= cl_t <= c1 or (c1 == pairs[-1][0]):
            return m0 + (m1 - m0) * (cl_t - c0) / (c1 - c0)
    return None


def main(parse_only=False):
    OUT.mkdir(parents=True, exist_ok=True)
    (MESH / ".gitignore").parent.mkdir(parents=True, exist_ok=True)
    (MESH / ".gitignore").write_text("*.su2\n")
    for d in DELTAS:
        geometry(d)
    if not parse_only:
        for L in (1, 2, 3):
            for d in DELTAS:
                mesh(d, L)
    specs = case_list()
    if parse_only:
        res = [run_case(s, parse_only=True) for s in specs]
    else:
        with ThreadPoolExecutor(max_workers=len(specs)) as ex:
            res = list(ex.map(lambda s: run_case(s, threads=2), specs))
    R = {case_name(*s): {**r, "level": s[0], "delta": s[1], "alpha": s[2], "model": s[3]} for s, r in zip(specs, res)}
    meshes = {f"d{d:+.0f}_L{L}": json.loads((MESH / f"s5010_d{d:+.0f}_L{L}.json").read_text())
              for L in (1, 2, 3) for d in DELTAS if (MESH / f"s5010_d{d:+.0f}_L{L}.json").exists()}

    def g(L, d, a=4.0, m="SA"):
        return R[case_name(L, d, a, m)]

    out = {"Re": RE, "alpha_deg": 4.0, "hinge": [HINGE_X, HINGE_YT], "thin_cmd_per_rad": THIN_CMD,
           "thin_cld_per_rad": THIN_CLD, "thin_cmd_per_deg": THIN_CMD * math.pi / 180, "cases": R, "meshes": meshes}
    lv = {}
    for L in (1, 2, 3):
        a, b = g(L, 0.0), g(L, -10.0)
        if a.get("usable") and b.get("usable"):
            lv[L] = {"eta_cm": eta_cm(b["cm"], a["cm"], -10.0), "eta_cl": eta_cl(b["cl"], a["cl"], -10.0),
                     "cm0": a["cm"], "cl0": a["cl"], "cells": meshes.get(f"d+0_L{L}", {}).get("cells")}
    out["levels_SA"] = lv
    if len(lv) == 3:
        out["gci_eta_cm"] = gci(lv[3]["eta_cm"], lv[2]["eta_cm"], lv[1]["eta_cm"])
        out["gci_eta_cl"] = gci(lv[3]["eta_cl"], lv[2]["eta_cl"], lv[1]["eta_cl"])
        out["gci_cm0"] = gci(lv[3]["cm0"], lv[2]["cm0"], lv[1]["cm0"])
        out["gci_cl0"] = gci(lv[3]["cl0"], lv[2]["cl0"], lv[1]["cl0"])
    # eta at cl 0.5 (B2's definition) on L2 SA from alpha 4 and 8
    try:
        cm05 = {d: cm_at_cl([(g(2, d, a)["cl"], g(2, d, a)["cm"]) for a in (4.0, 8.0)]) for d in DELTAS}
        out["eta_cm_cl05_L2_SA"] = eta_cm(cm05[-10.0], cm05[0.0], -10.0)
        out["dcm_dcl_L2_SA"] = {d: (g(2, d, 8.0)["cm"] - g(2, d, 4.0)["cm"]) / (g(2, d, 8.0)["cl"] - g(2, d, 4.0)["cl"])
                                for d in DELTAS}
    except (KeyError, TypeError, ZeroDivisionError):
        pass
    try:
        a, b = g(2, 0.0, 4.0, "SSTLM"), g(2, -10.0, 4.0, "SSTLM")
        if a.get("usable") and b.get("usable"):
            out["eta_cm_L2_SSTLM"] = eta_cm(b["cm"], a["cm"], -10.0)
            out["eta_cl_L2_SSTLM"] = eta_cl(b["cl"], a["cl"], -10.0)
    except KeyError:
        pass
    # XFOIL on the same geometry, panel study
    xf = {}
    for n in (160, 240, 320):
        p0, p1 = xfoil(0.0, n), xfoil(-10.0, n)
        row = {"polar_d0": p0, "polar_dm10": p1}
        if 4.0 in p0 and 4.0 in p1:
            row["eta_cm_a4"] = eta_cm(p1[4.0][2], p0[4.0][2], -10.0)
            row["eta_cl_a4"] = eta_cl(p1[4.0][0], p0[4.0][0], -10.0)
        try:
            c0 = cm_at_cl([(v[0], v[2]) for v in p0.values()])
            c1 = cm_at_cl([(v[0], v[2]) for v in p1.values()])
            row["eta_cm_cl05"] = eta_cm(c1, c0, -10.0)
        except (TypeError, ZeroDivisionError):
            pass
        xf[n] = {k: (v if not isinstance(v, dict) else {str(a): x for a, x in v.items()}) for k, v in row.items()}
    out["xfoil"] = xf
    (OUT / "cfd_results.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k not in ("cases", "meshes", "xfoil")}, indent=1, default=str))
    print({n: {k: v for k, v in r.items() if k.startswith("eta")} for n, r in xf.items()})


if __name__ == "__main__":
    main(parse_only="--parse" in sys.argv)
