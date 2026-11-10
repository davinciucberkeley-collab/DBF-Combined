"""B1 verification round: 2-D RANS (SU2 8.5, INC_RANS, SA fully turbulent) of the three cruise sections whose drag the
performance model takes from hand estimates or from XFOIL alone.

Why CFD here (SIM-TOOLS.md: CFD only where VLM/XFOIL is not enough):
  finA  fin section through the motor tube: 22 mm CF tube + 9.6 mm two-layer foam board, square trailing edge.
        Hand model: board Cf FF + tube Cd 0.30 on its diameter. A tube that stands 6.2 mm proud of the board and a
        blunt 9.6 mm base are separated flows that XFOIL cannot run and AVL does not see.
  finB  fin section above the tube end (|z| 0.172-0.21 m): bare board, square LE and TE (0.5 mm edge radius).
  s5010 wing section at the as-designed cruise cl, fully turbulent: the upper bound of the tape-seam roughness
        factor (ASM-B1-WING-ROUGH), compared like-for-like with XFOIL forced transition at the LE.

Geometry in metres from redesign/params/params.json (fins.chord_m, fins.tube.od_m, fins.board_t_m x fins.layers,
wing.chord_m) and the S5010 file B2 checked (team/B2/airfoils/s5010.dat). Flow: rho, V cruise, mu from nu 1.48e-5
(B2's ASM-B2-NU). Three grid levels per section, uniform refinement ratio sqrt(2) in every size (surface, first cell,
wake, far field), GCI after Celik et al. (2008). Meshes are deleted after each run (re-made by this script);
case.cfg, history.csv, surface_flow.csv and the log stay in sim/cfd/<case>/.

Usage: python -I redesign/team/B1/cfd_sections.py [--parse-only]      (~10-20 min on 16 threads)
Writes sim/cfd/cfd_results.json. Requires gmsh (Python API) and numpy, SU2_CFD.exe from SIM-TOOLS.md.
"""
import json
import math
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RED = HERE.parents[1]
OUT = HERE / "sim" / "cfd"
OUT.mkdir(parents=True, exist_ok=True)
SU2 = Path("C:/Users/dillo/tools/su2/bin/bin/SU2_CFD.exe")
PRM = json.loads((RED / "params" / "params.json").read_text(encoding="utf-8"))


def pv(path):
    d = PRM
    for k in path.split("."):
        d = d[k]
    return d["value"]


RHO = pv("env.rho_kgm3")
V = pv("performance.cruise_ms")
NU = 1.48e-5                                   # m2/s, B2 ASM-B2-NU (15 degC)
MU = RHO * NU
C_WING = pv("wing.chord_m")
C_FIN = pv("fins.chord_m")                     # from the tube axis (fins.le_x_m = fins.tube.x_m) to the TE
R_TUBE = pv("fins.tube.od_m") / 2
T_FIN = pv("fins.board_t_m") * pv("fins.layers")
R_FILLET = 0.003                               # m, tube-board epoxy fillet radius (fins.fin.le_gap_m filled, ASM-B1-CFD-EDGE)
R_EDGE = 0.0                                    # m: board edges modelled sharp and square (ASM-B1-CFD-EDGE)
LEVELS = {1: 2.0, 2: math.sqrt(2.0), 3: 1.0}   # size factor f; ratio sqrt(2) between levels
N_JOBS, THREADS = 3, 4
ALPHA_WING = 2.5                               # deg; gives cl ~0.42-0.45 in SA (as-designed cruise cl 0.41)


def s5010_pts():
    rows = []
    for line in (HERE.parent / "B2" / "airfoils" / "s5010.dat").read_text().splitlines()[1:]:
        p = line.split()
        if len(p) == 2:
            rows.append((float(p[0]) * C_WING, float(p[1]) * C_WING))
    return rows


# ------------------------------------------------------------------ meshing
def _rounded_outline(occ, corners, radii):
    """Closed polygon (counter-clockwise) with an arc of radius r at each corner (r 0: sharp). Returns curve tags."""
    n = len(corners)
    pts_in, pts_out, centres = [], [], []
    for i in range(n):
        p0, p1, p2 = (np.array(corners[(i - 1) % n]), np.array(corners[i]), np.array(corners[(i + 1) % n]))
        r = radii[i]
        if r <= 0:
            t = occ.addPoint(*p1, 0)
            pts_in.append(t); pts_out.append(t); centres.append(None)
            continue
        a, b = (p0 - p1) / np.linalg.norm(p0 - p1), (p2 - p1) / np.linalg.norm(p2 - p1)
        half = math.acos(np.clip(a @ b, -1, 1)) / 2
        d = r / math.tan(half)
        bis = (a + b) / np.linalg.norm(a + b)
        c = p1 + bis * r / math.sin(half)
        pts_in.append(occ.addPoint(*(p1 + a * d), 0))
        pts_out.append(occ.addPoint(*(p1 + b * d), 0))
        centres.append(occ.addPoint(*c, 0))
    curves = []
    for i in range(n):
        if centres[i] is not None:
            curves.append(occ.addCircleArc(pts_in[i], centres[i], pts_out[i]))
        curves.append(occ.addLine(pts_out[i], pts_in[(i + 1) % n]))
    return curves


def build_mesh(case, level):
    import gmsh
    f = LEVELS[level]
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", int(__import__("os").environ.get("GMSH_VERBOSE", "0")))
    gmsh.model.add(f"{case}_L{level}")
    occ = gmsh.model.occ
    fans = []
    if case == "s5010":
        c = C_WING
        pts = s5010_pts()
        i_le = min(range(len(pts)), key=lambda i: pts[i][0])
        tags = [occ.addPoint(x, y, 0) for x, y in pts[:-1]]
        up = occ.addSpline(tags[: i_le + 1])
        lo = occ.addSpline(tags[i_le:] + [tags[0]])
        wall = [up, lo]
        fans = [tags[0]]
        n_side = int(round(180 / f))
    else:
        c = C_FIN
        h = T_FIN / 2
        if case == "finA":
            rf = R_FILLET                          # epoxy fillet between tube and board (concave, both faces)
            xc = math.sqrt((R_TUBE + rf) ** 2 - (h + rf) ** 2)
            k = R_TUBE / (R_TUBE + rf)
            ctr = occ.addPoint(0, 0, 0)
            p_le = occ.addPoint(-R_TUBE, 0, 0)
            ft_t, fl_t = occ.addPoint(xc * k, (h + rf) * k, 0), occ.addPoint(xc, h, 0)
            ft_b, fl_b = occ.addPoint(xc * k, -(h + rf) * k, 0), occ.addPoint(xc, -h, 0)
            fc_t, fc_b = occ.addPoint(xc, h + rf, 0), occ.addPoint(xc, -h - rf, 0)
            tb, tt = occ.addPoint(C_FIN, -h, 0), occ.addPoint(C_FIN, h, 0)
            wall = [occ.addCircleArc(ft_t, ctr, p_le), occ.addCircleArc(p_le, ctr, ft_b),
                    occ.addCircleArc(ft_b, fc_b, fl_b), occ.addLine(fl_b, tb), occ.addLine(tb, tt),
                    occ.addLine(tt, fl_t), occ.addCircleArc(fl_t, fc_t, ft_t)]
            fans = [tb, tt]
        else:
            x0 = R_TUBE + 0.0005
            q = [occ.addPoint(x, y, 0) for x, y in [(x0, -h), (C_FIN, -h), (C_FIN, h), (x0, h)]]
            wall = [occ.addLine(q[i], q[(i + 1) % 4]) for i in range(4)]
            fans = q
        n_side = None
    loop = occ.addCurveLoop(wall)
    R_far = 20 * c
    circ = occ.addCircle(c / 2, 0, 0, R_far)
    surf = occ.addPlaneSurface([occ.addCurveLoop([circ]), loop])
    occ.synchronize()
    gmsh.model.addPhysicalGroup(1, wall, name="wall")
    gmsh.model.addPhysicalGroup(1, [circ], name="farfield")
    gmsh.model.addPhysicalGroup(2, [surf], name="fluid")
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    s_wall = 0.0012 * f * c / 0.3                 # surface size, m
    s_edge = 0.00025 * f                          # at the blunt edges and the tube junction
    h1 = 1.2e-5 * f                               # first cell, m (y+ ~0.6-1.2 at L3-L2 for u_tau ~0.8 m/s)
    fd = gmsh.model.mesh.field
    dist = fd.add("Distance"); fd.setNumbers(dist, "CurvesList", wall); fd.setNumber(dist, "Sampling", 600)
    thr = fd.add("Threshold"); fd.setNumber(thr, "InField", dist)
    fd.setNumber(thr, "SizeMin", s_wall); fd.setNumber(thr, "SizeMax", 0.6 * f * c)
    fd.setNumber(thr, "DistMin", 0.02 * c); fd.setNumber(thr, "DistMax", 8 * c)
    box = fd.add("Box")
    fd.setNumber(box, "VIn", 0.004 * f * c / 0.3 * (2.0 if case == "s5010" else 1.0)); fd.setNumber(box, "VOut", 0.6 * f * c)
    fd.setNumber(box, "XMin", -0.1 * c); fd.setNumber(box, "XMax", 3.0 * c)
    fd.setNumber(box, "YMin", -0.25 * c); fd.setNumber(box, "YMax", 0.25 * c); fd.setNumber(box, "Thickness", c)
    fields = [thr, box]
    if case != "s5010":                            # fine spacing at the separation edges, through the 1-D mesh
        for w in wall:
            L = gmsh.model.occ.getMass(1, w)
            if L < 0.03:                           # blunt base, LE face, tube arcs: uniform s_edge
                gmsh.model.mesh.setTransfiniteCurve(w, max(6, int(round(L / s_edge)) + 1))
            else:                                  # board faces: clustered to s_edge at both ends
                gmsh.model.mesh.setTransfiniteCurve(w, max(20, int(round(1.6 * L / s_wall)) + 1), "Bump", 0.12)
    mn = fd.add("Min"); fd.setNumbers(mn, "FieldsList", fields); fd.setAsBackgroundMesh(mn)
    bl = fd.add("BoundaryLayer"); fd.setNumbers(bl, "CurvesList", wall)
    if fans:
        fd.setNumbers(bl, "FanPointsList", fans)
    ratio = 1.15 ** (f ** -0.0)                    # same growth on every level; layer count follows h1
    t_bl = 0.004 if case == "s5010" else 0.0015      # m; on the fins below the 3 mm fillet radius (concave corner)
    nl = int(round(math.log(1 + t_bl * (ratio - 1) / h1) / math.log(ratio)))
    fd.setNumber(bl, "Size", h1); fd.setNumber(bl, "Ratio", ratio); fd.setNumber(bl, "Quads", 1)
    fd.setNumber(bl, "Thickness", h1 * (ratio ** nl - 1) / (ratio - 1))
    fd.setAsBoundaryLayer(bl)
    if n_side:
        gmsh.model.mesh.setTransfiniteCurve(wall[0], n_side, "Bump", 0.25)
        gmsh.model.mesh.setTransfiniteCurve(wall[1], n_side, "Bump", 0.25)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.option.setNumber("Mesh.Smoothing", 5)
    gmsh.model.mesh.generate(2)
    _, etags, _ = gmsh.model.mesh.getElements(2)
    ncell = int(sum(len(t) for t in etags))
    d = OUT / f"{case}_L{level}"
    d.mkdir(exist_ok=True)
    gmsh.option.setNumber("Mesh.SaveAll", 0)
    gmsh.write(str(d / "mesh.su2"))
    gmsh.finalize()
    return {"cells": ncell, "h1_m": h1, "s_wall_m": s_wall, "bl_layers": nl, "R_far_m": R_far}


CFG = """% B1 verification, {case} L{level}: SU2 8.5 incompressible RANS, SA fully turbulent (team/B1/cfd_sections.py)
SOLVER= INC_RANS
KIND_TURB_MODEL= SA
MATH_PROBLEM= DIRECT
RESTART_SOL= NO
INC_DENSITY_MODEL= CONSTANT
INC_DENSITY_INIT= {rho}
INC_VELOCITY_INIT= ( {vx:.6f}, {vy:.6f}, 0.0 )
INC_NONDIM= INITIAL_VALUES
VISCOSITY_MODEL= CONSTANT_VISCOSITY
MU_CONSTANT= {mu:.8e}
FREESTREAM_TURBULENCEINTENSITY= 0.001
FREESTREAM_TURB2LAMVISCRATIO= 10.0
AOA= {alpha}
REF_ORIGIN_MOMENT_X= {xm}
REF_ORIGIN_MOMENT_Y= 0.0
REF_ORIGIN_MOMENT_Z= 0.0
REF_LENGTH= {c}
REF_AREA= {c}
MARKER_HEATFLUX= ( wall, 0.0 )
MARKER_FAR= ( farfield )
MARKER_PLOTTING= ( wall )
MARKER_MONITORING= ( wall )
NUM_METHOD_GRAD= WEIGHTED_LEAST_SQUARES
CFL_NUMBER= {cfl0}
CFL_ADAPT= YES
CFL_ADAPT_PARAM= ( 0.5, 1.1, {cfl0}, {cflmax} )
ITER= {iters}
LINEAR_SOLVER= FGMRES
LINEAR_SOLVER_PREC= LU_SGS
LINEAR_SOLVER_ERROR= 1E-5
LINEAR_SOLVER_ITER= 10
CONV_NUM_METHOD_FLOW= FDS
MUSCL_FLOW= YES
SLOPE_LIMITER_FLOW= VENKATAKRISHNAN
VENKAT_LIMITER_COEFF= 0.05
LIMITER_ITER= 800
TIME_DISCRE_FLOW= EULER_IMPLICIT
CONV_NUM_METHOD_TURB= SCALAR_UPWIND
MUSCL_TURB= NO
TIME_DISCRE_TURB= EULER_IMPLICIT
CONV_FIELD= ( RMS_PRESSURE )
CONV_RESIDUAL_MINVAL= -10
MESH_FILENAME= mesh.su2
MESH_FORMAT= SU2
TABULAR_FORMAT= CSV
CONV_FILENAME= history
SURFACE_FILENAME= surface_flow
OUTPUT_FILES= ( SURFACE_CSV )
OUTPUT_WRT_FREQ= 100000
HISTORY_OUTPUT= ( ITER, RMS_RES, AERO_COEFF )
SCREEN_OUTPUT= ( INNER_ITER, RMS_PRESSURE, LIFT, DRAG )
SCREEN_WRT_FREQ_INNER= 200
"""


def case_list():
    only = [a for a in sys.argv[1:] if not a.startswith("--")]     # e.g. finA s5010: re-run those sections only
    return [(c, L) for c in ("finA", "finB", "s5010") for L in (1, 2, 3) if not only or c in only]


NUMERICS = [(1.0, 20.0, 5000), (0.5, 5.0, 9000)]   # (CFL start, CFL max, iterations): first try, safe retry


def _converged(d):
    try:
        lines = (d / "history.csv").read_text().splitlines()
        head = [h.strip().strip('"') for h in lines[0].split(",")]
        last = [float(x) for x in lines[-1].split(",")]
        r = last[head.index("rms[P]")]
        return math.isfinite(r) and r < -7.0 and abs(last[head.index("CD")]) < 1.0
    except (OSError, ValueError, IndexError):
        return False


def run(case, level, iters=None, info=None):
    """Mesh (main thread only: gmsh) unless info is given, then run SU2. A run that ends without convergence
    (diverged, or the process was killed) is repeated once with the safe numerics."""
    d = OUT / f"{case}_L{level}"
    t0 = time.time()
    info = info or build_mesh(case, level)
    alpha = ALPHA_WING if case == "s5010" else 0.0
    c = C_WING if case == "s5010" else C_FIN
    a = math.radians(alpha)
    rc, attempt = None, 0
    for attempt, (cfl0, cflmax, it) in enumerate(NUMERICS, 1):
        (d / "case.cfg").write_text(CFG.format(case=case, level=level, rho=RHO, vx=V * math.cos(a), vy=V * math.sin(a),
                                               mu=MU, alpha=alpha, xm=0.25 * c, c=c, iters=iters or it, cfl0=cfl0,
                                               cflmax=cflmax))
        with open(d / "su2.log", "w") as log:
            rc = subprocess.run([str(SU2), "-t", str(THREADS), "case.cfg"], cwd=str(d), stdout=log,
                                stderr=subprocess.STDOUT).returncode
        if _converged(d):
            break
    (d / "mesh.su2").unlink(missing_ok=True)
    for p in d.glob("restart*"):
        p.unlink()
    info.update({"rc": rc, "attempt": attempt, "converged": _converged(d), "wall_s": round(time.time() - t0, 1),
                 "alpha_deg": alpha, "chord_m": c})
    (d / "mesh_info.json").write_text(json.dumps(info, indent=1))
    return info


def parse(case, level):
    d = OUT / f"{case}_L{level}"
    lines = (d / "history.csv").read_text().splitlines()
    head = [h.strip().strip('"') for h in lines[0].split(",")]
    rows = np.array([[float(x) for x in l.split(",")] for l in lines[1:] if l.strip()])
    col = {h: i for i, h in enumerate(head)}
    n = len(rows)
    win = rows[max(0, n - 200):]                           # last 200 iterations (cases stop at rms[P] -10)
    cd, cl = win[:, col["CD"]], win[:, col["CL"]]
    info = json.loads((d / "mesh_info.json").read_text())
    return {"cells": info["cells"], "iters": n, "rms_p_final": float(rows[-1, col["rms[P]"]]),
            "rms_p_drop": float(rows[-1, col["rms[P]"]] - rows[:, col["rms[P]"]].max()),
            "cd": float(cd.mean()), "cd_osc": float(cd.max() - cd.min()), "cl": float(cl.mean()),
            "cl_osc": float(cl.max() - cl.min()), "alpha_deg": info["alpha_deg"], "chord_m": info["chord_m"],
            "wall_s": info["wall_s"], "h1_m": info["h1_m"], "converged": info.get("converged", info["rc"] == 0),
            "attempt": info.get("attempt", 1)}


def gci(f1, f2, f3, n1, n2, n3, Fs=1.25):
    """Celik et al., J. Fluids Eng. 130 (2008) 078001; f1 fine. r from 2-D cell counts."""
    r21, r32 = math.sqrt(n1 / n2), math.sqrt(n2 / n3)
    e21, e32 = f2 - f1, f3 - f2
    if abs(e21) < 1e-12 or e32 / e21 <= 0:
        spread = max(f1, f2, f3) - min(f1, f2, f3)
        return {"p": None, "f_ext": f1, "gci_fine_pct": 100 * Fs * spread / abs(f1), "r21": r21, "r32": r32,
                "note": "oscillatory convergence: GCI taken as Fs x the spread of the three levels"}
    s = 1.0
    p = abs(math.log(abs(e32 / e21))) / math.log(r21)
    for _ in range(200):
        p = abs(math.log(abs(e32 / e21)) + math.log((r21 ** p - s) / (r32 ** p - s))) / math.log(r21)
    f_ext = (r21 ** p * f1 - f2) / (r21 ** p - 1)
    return {"p": p, "f_ext": f_ext, "gci_fine_pct": 100 * Fs * abs(e21 / f1) / (r21 ** p - 1), "r21": r21,
            "r32": r32, "note": "monotonic"}


def main():
    if "--parse-only" not in sys.argv:
        meshes = {}
        for c, L in case_list():                 # gmsh is not thread-safe: mesh first, in the main thread
            meshes[(c, L)] = build_mesh(c, L)
            print(f"mesh {c} L{L}: {meshes[(c, L)]['cells']} cells", flush=True)
        with ThreadPoolExecutor(N_JOBS) as ex:
            futs = {ex.submit(run, c, L, None, meshes[(c, L)]): (c, L) for c, L in case_list()}
            for fu, (c, L) in futs.items():
                r = fu.result()
                print(f"{c} L{L}: {r['cells']} cells, rc {r['rc']}, attempt {r['attempt']}, converged {r['converged']}, "
                      f"{r['wall_s']} s", flush=True)
    res = {"_note": "Written by team/B1/cfd_sections.py. Coefficients per unit span on the section chord; averages of "
                    "the last 200 iterations; *_osc = max - min over that window.",
           "flow": {"rho": RHO, "V_ms": V, "mu": MU, "Re_fin": RHO * V * C_FIN / MU, "Re_wing": RHO * V * C_WING / MU},
           "geometry": {"c_fin_m": C_FIN, "r_tube_m": R_TUBE, "t_fin_m": T_FIN, "r_edge_m": R_EDGE, "r_fillet_m": R_FILLET, "c_wing_m": C_WING},
           "cases": {}, "gci": {}}
    for c in ("finA", "finB", "s5010"):
        lv = {L: parse(c, L) for L in (1, 2, 3)}
        res["cases"][c] = {f"L{L}": lv[L] for L in lv}
        res["gci"][c] = {q: gci(lv[3][q], lv[2][q], lv[1][q], lv[3]["cells"], lv[2]["cells"], lv[1]["cells"])
                         for q in ("cd", "cl")}
        print(c, {f"L{L}": (lv[L]["cells"], round(lv[L]["cd"], 5), round(lv[L]["cl"], 4)) for L in lv},
              "GCI cd %.1f %%" % res["gci"][c]["cd"]["gci_fine_pct"])
    (OUT / "cfd_results.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
