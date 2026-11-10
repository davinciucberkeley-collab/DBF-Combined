"""B4 simulation round: 2-D SU2 section of the motor tube with the half-fin board behind it, in the prop slipstream.

Why CFD here: the hover-download and cruise-items models (team/B4/props.py) treat the 22 mm CF tube as a bare
cylinder (Cd 1.1, ASM-B4-CD-TUBE) and add the half-fin board's friction separately. On the as-designed fin
(subsystems/fins/params.json: board LE 0.5 mm behind the tube, filled by the epoxy fillet) most of the tube span has
the 9.6 mm board directly behind it, so the section is a round-nosed plate with a blunt TE, not a cylinder. Its drag
(nose separation bubble + friction + base) is a separated viscous flow that XFOIL/VLM cannot give and that no
handbook value covers for this thickness ratio. A 2-D section is enough: the slipstream is locally parallel to the
fin plane (fin chord along x, the wake travels +x) and the tube is long (L/D ~ 8).

Cases (all incompressible, rho 1.225 kg/m3, mu 1.81e-5 Pa s, 2-D, per metre of span, Cd on the tube diameter D):
  val    bare cylinder, Re_D 40, laminar steady    -> solver/mesh/force check vs published Cd 1.50-1.53
  hov    tube + 2-layer board, U 10 m/s (hover slipstream at the tube), laminar and SA RANS
  cru    tube + 2-layer board, U 16 m/s (cruise), laminar and SA RANS
Each on three meshes (L1 coarse, L2, L3 fine; wall sizes scale by 1.5 per level) -> Richardson / GCI (Roache).

Run (numpy + gmsh + SU2; ~10-20 min on 20 threads):
  python redesign/team/B4/sim/cfd/tubefin.py mesh        build the meshes
  python redesign/team/B4/sim/cfd/tubefin.py run [case]  run every case (or one, e.g. hov_lam_L2)
  python redesign/team/B4/sim/cfd/tubefin.py summary     -> results.json (read by sim_claims.py, stdlib)
Geometry from params.json + subsystems/fins/params.json (no typed dimensions).
"""
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RD = HERE.parents[3]                                   # redesign/
SU2 = Path(os.environ.get("SU2_CFD", r"C:\Users\dillo\tools\su2\bin\bin\SU2_CFD.exe"))
THREADS = int(os.environ.get("SU2_THREADS", "8"))
RHO, MU = 1.225, 1.81e-5
NU = MU / RHO
RF = 0.003                                              # epoxy fillet radius at the tube-board junction (B4 assumption)


def _p(d, path):
    for k in path.split("."):
        d = d[k]
    return d["value"] if isinstance(d, dict) and "value" in d else d


PAR = json.loads((RD / "params" / "params.json").read_text(encoding="utf-8"))
FIN = json.loads((RD / "subsystems" / "fins" / "params.json").read_text(encoding="utf-8"))
GEOM = {
    "D": _p(PAR, "fins.tube.od_m"),                                       # 0.022
    "t": _p(PAR, "fins.board_t_m") * _p(PAR, "fins.layers"),             # 0.0096
    "x_tube": _p(PAR, "fins.tube.x_m"),                                   # 0.045
    "x_te": _p(PAR, "fins.te_x_m"),                                       # 0.320
    "le_gap": _p(FIN, "fin_detail.fin.le_gap_m"),                         # 0.0005, filled with epoxy
}
LEVELS = {0: 3.375, 1: 2.25, 2: 1.5, 3: 1.0}           # size factor (x base sizes); fin study on L0/L1/L2, cylinder on L1/L2/L3
CASES = {}
CASES.update({f"val_lam_L{lv}": ("cyl", lv, "lam", 40 * NU / GEOM["D"]) for lv in (1, 2, 3)})
for tag, U in (("hov", 10.0), ("cru", 16.0)):
    for turb in ("sa",):
        CASES.update({f"{tag}_{turb}_L{lv}": ("fin", lv, turb, U) for lv in (0, 1, 2)})


# ------------------------------------------------------------------------------------------------------------ mesh
def build_mesh(shape, lv):
    import gmsh
    D, t = GEOM["D"], GEOM["t"]
    R = D / 2
    L = GEOM["x_te"] - GEOM["x_tube"]                  # tube centre to fin TE, 0.275 m
    f = LEVELS[lv]
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add(f"{shape}_L{lv}")
    occ = gmsh.model.occ
    box = occ.addRectangle(-1.0, -1.0, 0, 3.3, 2.0)
    disk = occ.addDisk(0, 0, 0, R, R)
    fan = []
    if shape == "fin":
        occ.remove([(2, disk)], recursive=True)
        # tube + board outline with the epoxy fillet (radius RF) in the two concave corners where the board meets
        # the tube (fin_detail.fin.le_gap_m "filled by the epoxy fillet"); square blunt TE (cut board edge)
        h = t / 2
        xc = math.sqrt((R + RF) ** 2 - (h + RF) ** 2)
        k = R / (R + RF)
        P = lambda x, y: occ.addPoint(x, y, 0)  # noqa: E731
        o = P(0, 0)
        tu, tl = P(xc * k, (h + RF) * k), P(xc * k, -(h + RF) * k)        # tangent points on the tube
        fu, fl = P(xc, h + RF), P(xc, -(h + RF))                           # fillet centres
        pu, pl = P(xc, h), P(xc, -h)                                       # tangent points on the board
        eu, el = P(L, h), P(L, -h)
        nose = P(-R, 0)
        cs = [occ.addCircleArc(tu, o, nose), occ.addCircleArc(nose, o, tl), occ.addCircleArc(tl, fl, pl),
              occ.addLine(pl, el), occ.addLine(el, eu), occ.addLine(eu, pu), occ.addCircleArc(pu, fu, tu)]
        body = [(2, occ.addPlaneSurface([occ.addCurveLoop(cs)]))]
        fan = [eu, el]
    else:
        body = [(2, disk)]
    fluid, _ = occ.cut([(2, box)], body)
    occ.synchronize()
    curves = gmsh.model.getBoundary(fluid, oriented=False)
    wall, far = [], []
    for dim, tag in curves:
        xmin, ymin, _, xmax, ymax, _ = gmsh.model.getBoundingBox(dim, tag)
        (far if (xmax > 2.2 or xmin < -0.9 or ymax > 0.9 or ymin < -0.9) else wall).append(abs(tag))
    gmsh.model.addPhysicalGroup(1, wall, name="body")
    gmsh.model.addPhysicalGroup(1, far, name="farfield")
    gmsh.model.addPhysicalGroup(2, [fluid[0][1]], name="fluid")
    h_wall = 0.0003 * f                                    # surface size on the tube / plate
    h_te = 0.0002 * f                                      # at the blunt TE corners
    h_far = 0.08 * f
    y1 = 1.5e-5 * f                                        # first-layer height (y+ ~ 0.5-1 for SA at 16 m/s)
    fld = gmsh.model.mesh.field
    bl = fld.add("BoundaryLayer")
    fld.setNumbers(bl, "CurvesList", wall)
    fld.setNumber(bl, "Size", y1)
    fld.setNumber(bl, "Ratio", 1.15)
    fld.setNumber(bl, "Thickness", 0.0025)
    fld.setNumber(bl, "Quads", 1)
    if fan:
        pts = []
        for c in wall:
            for _, p in gmsh.model.getBoundary([(1, c)], oriented=False):
                x, y, _ = gmsh.model.getValue(0, abs(p), [])
                if abs(x - L) < 1e-9:
                    pts.append(abs(p))
        fld.setNumbers(bl, "FanPointsList", sorted(set(pts)))
        fld.setNumbers(bl, "FanPointsSizesList", [5] * len(set(pts)))
    fld.setAsBoundaryLayer(bl)
    dist = fld.add("Distance")
    fld.setNumbers(dist, "CurvesList", wall)
    fld.setNumber(dist, "Sampling", 400)
    th = fld.add("Threshold")
    fld.setNumber(th, "InField", dist)
    fld.setNumber(th, "SizeMin", h_wall)
    fld.setNumber(th, "SizeMax", h_far)
    fld.setNumber(th, "DistMin", 0.002)
    fld.setNumber(th, "DistMax", 0.6)
    # wake box: keep the near wake resolved (bare cylinder: 12 D; fin: 0.15 m behind the TE)
    wk = fld.add("Box")
    x_end = (L + 0.15) if shape == "fin" else 12 * D
    fld.setNumber(wk, "VIn", 0.0015 * f)
    fld.setNumber(wk, "VOut", h_far)
    fld.setNumber(wk, "XMin", -0.02)
    fld.setNumber(wk, "XMax", x_end)
    fld.setNumber(wk, "YMin", -0.03 if shape == "fin" else -1.5 * D)
    fld.setNumber(wk, "YMax", 0.03 if shape == "fin" else 1.5 * D)
    fld.setNumber(wk, "Thickness", 0.05)
    te = fld.add("Ball")
    fld.setNumber(te, "Radius", t)
    fld.setNumber(te, "Thickness", t)
    fld.setNumber(te, "VIn", h_te)
    fld.setNumber(te, "VOut", h_far)
    fld.setNumber(te, "XCenter", L if shape == "fin" else 0.0)
    fld.setNumber(te, "YCenter", 0.0)
    mn = fld.add("Min")
    fld.setNumbers(mn, "FieldsList", [th, wk, te])
    fld.setAsBackgroundMesh(mn)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.Algorithm", 5)
    gmsh.model.mesh.generate(2)
    out = HERE / "mesh"
    out.mkdir(exist_ok=True)
    fn = out / f"{shape}_L{lv}.su2"
    gmsh.write(str(fn))
    n = sum(len(t_) for t_ in gmsh.model.mesh.getElements(2)[1])
    gmsh.finalize()
    return fn, n


# ------------------------------------------------------------------------------------------------------------ SU2
CFG = """% generated by redesign/team/B4/sim/cfd/tubefin.py ({name})
SOLVER= {solver}
{turb}
MATH_PROBLEM= DIRECT
RESTART_SOL= {restart}
SOLUTION_FILENAME= restart_flow.dat
RESTART_FILENAME= restart_flow.dat
INC_NONDIM= DIMENSIONAL
INC_DENSITY_MODEL= CONSTANT
INC_DENSITY_INIT= {rho}
INC_VELOCITY_INIT= ( {U:.8f}, 0.0, 0.0 )
VISCOSITY_MODEL= CONSTANT_VISCOSITY
MU_CONSTANT= {mu}
REF_ORIGIN_MOMENT_X= 0.0
REF_ORIGIN_MOMENT_Y= 0.0
REF_ORIGIN_MOMENT_Z= 0.0
REF_LENGTH= {D}
REF_AREA= {D}
MARKER_HEATFLUX= ( body, 0.0 )
MARKER_FAR= ( farfield )
MARKER_PLOTTING= ( body )
MARKER_MONITORING= ( body )
NUM_METHOD_GRAD= WEIGHTED_LEAST_SQUARES
CFL_NUMBER= {cfl}
CFL_ADAPT= YES
CFL_ADAPT_PARAM= ( 0.5, 1.2, 1.0, {cflmax} )
CONV_NUM_METHOD_FLOW= FDS
MUSCL_FLOW= YES
SLOPE_LIMITER_FLOW= {lim}
VENKAT_LIMITER_COEFF= 0.03
CONV_NUM_METHOD_TURB= SCALAR_UPWIND
MUSCL_TURB= NO
TIME_DISCRE_FLOW= EULER_IMPLICIT
TIME_DISCRE_TURB= EULER_IMPLICIT
LINEAR_SOLVER= FGMRES
LINEAR_SOLVER_PREC= ILU
LINEAR_SOLVER_ERROR= 1E-6
LINEAR_SOLVER_ITER= 20
ITER= {iters}
CONV_RESIDUAL_MINVAL= -11
CONV_FIELD= ( DRAG )
CONV_CAUCHY_ELEMS= 300
CONV_CAUCHY_EPS= 2E-6
CONV_STARTITER= 500
MESH_FILENAME= {mesh}
MESH_FORMAT= SU2
SCREEN_OUTPUT= ( INNER_ITER, RMS_PRESSURE, RMS_VELOCITY-X, DRAG, LIFT )
HISTORY_OUTPUT= ( ITER, RMS_RES, AERO_COEFF, CAUCHY )
VOLUME_OUTPUT= ( COORDINATES, SOLUTION, PRIMITIVE )
OUTPUT_FILES= ( RESTART, SURFACE_CSV )
SURFACE_FILENAME= surface_flow
CONV_FILENAME= history
BREAKDOWN_FILENAME= forces_breakdown.dat
WRT_FORCES_BREAKDOWN= YES
OUTPUT_WRT_FREQ= 100
SCREEN_WRT_FREQ_INNER= 50
"""


def run_case(name):
    shape, lv, turb, U = CASES[name]
    d = HERE / "cases" / name
    d.mkdir(parents=True, exist_ok=True)
    mesh = HERE / "mesh" / f"{shape}_L{lv}.su2"
    cfg = CFG.format(name=name, solver="INC_RANS" if turb == "sa" else "INC_NAVIER_STOKES",
                     turb="KIND_TURB_MODEL= SA" if turb == "sa" else "KIND_TURB_MODEL= NONE",
                     rho=RHO, U=U, mu=MU, D=GEOM["D"], mesh=f"../../mesh/{shape}_L{lv}.su2",
                     cfl=2 if turb == "sa" else 3, cflmax=25 if turb == "sa" else 10, lim="VENKATAKRISHNAN" if turb == "sa" else "NONE",
                     iters="{iters}", restart="{restart}")
    t0 = time.time()
    # Resume after an external kill: SU2 writes restart_flow.dat every 100 iterations; each leg's history is kept
    # (history_leg<k>.csv) and read back in order. A leg that ends with forces_breakdown.dat has finished.
    for f in d.glob("history*.csv"):
        f.unlink()
    for f in (d / "restart_flow.dat", d / "forces_breakdown.dat"):
        if f.exists():
            f.unlink()
    total = 2500 if shape == "fin" else 4000
    done = 0
    for leg in range(20):
        restart = "YES" if (d / "restart_flow.dat").exists() and leg > 0 else "NO"
        (d / "case.cfg").write_text(cfg.format(iters=total - done, restart=restart), encoding="utf-8")
        with open(d / f"log_leg{leg}.txt", "w") as log:
            rc = subprocess.run([str(SU2), "-t", str(THREADS), "case.cfg"], cwd=str(d), stdout=log,
                                stderr=subprocess.STDOUT).returncode
        if (d / "history.csv").exists():
            n = sum(1 for _ in open(d / "history.csv")) - 1
            (d / "history.csv").rename(d / f"history_leg{leg:02d}.csv")
            done += (n // 100) * 100 if rc != 0 else n
        if rc == 0 and (d / "forces_breakdown.dat").exists():
            break
        if done >= total:
            break
    return time.time() - t0


def read_history(name):
    import csv
    legs = sorted((HERE / "cases" / name).glob("history_leg*.csv"))
    data, head = [], None
    for k, fn in enumerate(legs):
        rows = list(csv.reader(open(fn)))
        head = [h.strip().strip('"') for h in rows[0]]
        body = [[float(x) for x in r] for r in rows[1:] if r]
        if k < len(legs) - 1:                      # a killed leg resumes from its last 100-iteration restart
            body = body[: (len(body) // 100) * 100]
        data += body
    col = {h: i for i, h in enumerate(head)}
    return head, data, col


def breakdown(name):
    """Pressure and friction drag from forces_breakdown.dat."""
    txt = (HERE / "cases" / name / "forces_breakdown.dat").read_text(errors="ignore")
    out = {}
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith("Total CD:"):
            # 'Total CD: 0.6 | Pressure (55.2%): 0.33 | Friction (44.8%): 0.27 | ...'
            parts = [p.strip() for p in s.split("|")]
            out["cd"] = float(parts[0].split(":")[1])
            for p in parts[1:]:
                k, v = p.split(":")
                if k.startswith("Pressure"):
                    out["cd_p"] = float(v)
                elif k.startswith("Friction"):
                    out["cd_f"] = float(v)
            break
    return out


def summarise(name):
    head, data, col = read_history(name)
    cd_i = col.get("CD")
    rms = col.get("rms[P]")
    n = len(data)
    last = [r[cd_i] for r in data[-500:]]
    mean = sum(last) / len(last)
    amp = (max(last) - min(last)) / 2
    res = {"iters": n, "cd_mean_last500": mean, "cd_halfamp_last500": amp,
           "cd_final": data[-1][cd_i], "rms_p_final": data[-1][rms] if rms is not None else None,
           "rms_p_drop": (data[0][rms] - data[-1][rms]) if rms is not None else None}
    res.update({f"bd_{k}": v for k, v in breakdown(name).items()})
    return res


def gci(f1, f2, f3, r21, r32, Fs=1.25):
    """Roache GCI on the fine grid; f1 fine, f3 coarse. Celik et al. (2008) fixed-point for p with unequal r."""
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 or e32 == 0 or e21 * e32 < 0:
        p = None
        osc = True
    else:
        osc = False
        s = 1.0 if e32 / e21 > 0 else -1.0
        p = 2.0
        for _ in range(200):
            q = math.log((r21 ** p - s) / (r32 ** p - s))
            p = abs(math.log(abs(e32 / e21)) + q) / math.log(r21)
    if p is None or p < 0.5:
        # oscillatory or non-asymptotic: Roache's conservative band = Fs x the largest spread, no extrapolation
        band = 3.0 * max(abs(e21), abs(e32)) / abs(f1) if osc else Fs * abs(e21 / f1)
        return {"p": p, "f_ext": None, "gci_fine": band, "oscillatory": osc}
    f_ext = (r21 ** p * f1 - f2) / (r21 ** p - 1)
    ea = abs(e21 / f1)
    return {"p": p, "f_ext": f_ext, "gci_fine": Fs * ea / (r21 ** p - 1), "oscillatory": osc}


def summary():
    meshes = json.loads((HERE / "mesh" / "cells.json").read_text())
    out = {"geometry": GEOM, "rho": RHO, "mu": MU, "cases": {}, "studies": {}}
    for name in CASES:
        if any((HERE / "cases" / name).glob("history_leg*.csv")):
            shape, lv, turb, U = CASES[name]
            r = summarise(name)
            r.update({"shape": shape, "level": lv, "model": turb, "U_ms": U, "Re_D": U * GEOM["D"] / NU,
                      "cells": meshes[f"{shape}_L{lv}"]})
            out["cases"][name] = r
    for study in ("val_lam", "hov_sa", "cru_sa"):
        lvs = (3, 2, 1) if study.startswith("val") else (2, 1, 0)
        c = [out["cases"].get(f"{study}_L{lv}") for lv in lvs]
        if not all(c):
            continue
        r21 = (c[0]["cells"] / c[1]["cells"]) ** 0.5
        r32 = (c[1]["cells"] / c[2]["cells"]) ** 0.5
        f = [x["cd_mean_last500"] for x in c]
        g = gci(f[0], f[1], f[2], r21, r32)
        g.update({"cd_fine_mid_coarse": f, "levels": list(lvs), "r21": r21, "r32": r32,
                  "unsteady_halfamp_L3": c[0]["cd_halfamp_last500"]})
        out["studies"][study] = g
    (HERE / "results.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["studies"], indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    if cmd == "mesh":
        cells = {}
        for shape in ("cyl", "fin"):
            for lv in ((1, 2, 3) if shape == "cyl" else (0, 1, 2)):
                fn, n = build_mesh(shape, lv)
                cells[f"{shape}_L{lv}"] = n
                print(fn.name, n, "cells")
        (HERE / "mesh" / "cells.json").write_text(json.dumps(cells, indent=1))
    elif cmd == "run":
        names = sys.argv[2:] or list(CASES)
        for nm in names:
            print(nm, f"{run_case(nm):.0f} s", flush=True)
    else:
        summary()
