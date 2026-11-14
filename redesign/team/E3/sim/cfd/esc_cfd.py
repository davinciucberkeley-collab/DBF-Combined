"""E3 simulation round: 2-D SU2 conjugate-free RANS section of the ESC on its fin pad, in the prop slipstream.

Why CFD here: the ESC film coefficient is the input with the widest band in the thermal model (ASM-E3-WAKE, local
velocity factor 0.5 design / 0.7 nominal, a judgement). On the as-designed fin (subsystems/fins/params.json) the ESC
sits on a 1.2 mm ASA pad on the 9.6 mm two-layer board, 33-79 mm behind the centre of the 22 mm motor tube. The tube
overhangs the board by 6.2 mm on each side, so the shear layer that leaves the tube reattaches on the board right where
the ESC is (a backward step of 6.2 mm reattaches 5-7 step heights downstream), and the 7.2 mm ESC + pad stands up
into that shear layer as a forward step. No flat-plate or cylinder correlation covers this, XFOIL/VLM cannot, and the
answer moves the ESC temperature by +-10 K. A 2-D section (x along the chord = slipstream direction, y normal to the
fin) is enough: the slipstream is locally parallel to the fin plane and the tube is long (L/D ~ 8).

Physics: incompressible RANS (SST, inflow Tu 5 %, nu_t/nu 10: prop slipstream), energy equation with a passive
temperature (constant density), ESC faces isothermal at T_amb + 30 K, every other wall adiabatic. Output: the
average film coefficient h on the three exposed ESC faces of the section (front 6 mm, top 45 mm, rear 6 mm) and the
equivalent local-velocity factor f_eq = (h_CFD / h_lam(U))^2, the quantity the lumped model (thermal.py, Incropera
eq. 7.30 at f U) uses. Cases: hover (U = slipstream at the pad, from thermal.py's design hover) and cruise
(16 m/s), each on three meshes (L1 coarse, L2, L3 fine; wall sizes scale 1.5 per level) -> Richardson / GCI
(Roache, Celik et al. 2008). Sensitivity on L2: inflow Tu 1 % (hover) and SA instead of SST (hover).

Run (numpy-free; gmsh + SU2; ~15-30 min on 16 threads):
  python redesign/team/E3/sim/cfd/esc_cfd.py mesh          build the meshes
  python redesign/team/E3/sim/cfd/esc_cfd.py run [case]    run every case (or one, e.g. hov_sst_L2)
  python redesign/team/E3/sim/cfd/esc_cfd.py summary       -> results.json (read by thermal.py, stdlib)
Geometry from params.json + subsystems/fins/params.json + subsystems/propulsion/params.json (no typed dimensions).
"""
import csv
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
THREADS = int(os.environ.get("SU2_THREADS", "16"))
RHO, MU, CP, PR, PRT = 1.225, 1.81e-5, 1005.0, 0.71, 0.90
NU = MU / RHO
K_AIR = MU * CP / PR                                   # 0.0256 W/m K, consistent with the solver
T_AMB, DT_ESC = 303.15, 30.0                           # 30 degC ambient, ESC 30 K above (design hover ~ +31 K)


def _p(d, path):
    for k in path.split("."):
        d = d[k]
    return d["value"] if isinstance(d, dict) and "value" in d else d


PAR = json.loads((RD / "params" / "params.json").read_text(encoding="utf-8"))
FIN = json.loads((RD / "subsystems" / "fins" / "params.json").read_text(encoding="utf-8"))
PRP = json.loads((RD / "subsystems" / "propulsion" / "params.json").read_text(encoding="utf-8"))
_esc = _p(PRP, "propulsion_detail.esc.size_m")         # [x along fin, y off the pad, z across]
GEOM = {
    "D": _p(PAR, "fins.tube.od_m"),                                       # 0.022
    "t": _p(PAR, "fins.board_t_m") * _p(PAR, "fins.layers"),             # 0.0096
    "x_tube": _p(PAR, "fins.tube.x_m"),                                   # 0.045
    "x_te": _p(PAR, "fins.te_x_m"),                                       # 0.320
    "pad_x0": _p(FIN, "fin_detail.esc_pad.x0_m"),                         # 0.078
    "pad_len": _p(FIN, "fin_detail.esc_pad.len_m"),                       # 0.046
    "pad_t": _p(FIN, "fin_detail.esc_pad.t_m"),                           # 0.0012
    "esc_len": _esc[0],                                                   # 0.045
    "esc_t": _esc[1],                                                     # 0.006
}


def _u_hover():
    """Slipstream speed at the pad in the design hover, from thermal.py's last run (phase log, hover 1)."""
    try:
        r = json.loads((RD / "team" / "E3" / "thermal_results.json").read_text(encoding="utf-8"))
        for row in r["mission"]["phase_log_des"]:
            if row[0] == "hover 1":
                return round(row[3]["v_local_ms"], 1)
    except (OSError, KeyError, TypeError):
        pass
    return 10.9


U_HOV, U_CRU = _u_hover(), _p(PAR, "performance.cruise_ms")
# quad-layer thickness per level: gmsh 4.15 fails ("edge not recovered") at the ESC/board concave corners for other
# values; the quad region always covers the ESC thermal boundary layer (laminar delta_T ~ 1.3 mm at 11 m/s, 45 mm)
BL_THICK, MESH_ALG, BL_RATIO, BLK_OVL = {1: 0.0015, 2: 0.0015, 3: 0.0012}, 6, 1.2, 0.0
BL_EXTRA = {}
LEVELS = {1: 2.25, 2: 1.5, 3: 1.0}                     # size factor (x base sizes)
CASES = {}
for tag, U in (("hov", U_HOV), ("cru", U_CRU)):
    CASES.update({f"{tag}_sst_L{lv}": (lv, "SST", U, 0.05) for lv in LEVELS})
CASES["hov_sst_tu1_L2"] = (2, "SST", U_HOV, 0.01)
CASES["hov_sa_L2"] = (2, "SA", U_HOV, 0.05)
CASES["hov_lm_L2"] = (2, "SST_LM", U_HOV, 0.05)        # Langtry-Menter transition, Tu 5 %
CASES["hov_lm_tu1_L2"] = (2, "SST_LM", U_HOV, 0.01)    # transition, quiet inflow: lower bracket
CASES["cru_lm_tu1_L2"] = (2, "SST_LM", U_CRU, 0.01)


# ------------------------------------------------------------------------------------------------------------ mesh
def build_mesh(lv):
    import gmsh
    g = GEOM
    D, t = g["D"], g["t"]
    R = D / 2
    L = g["x_te"] - g["x_tube"]                         # tube centre to fin TE, 0.275 m (origin at tube centre)
    x0 = g["pad_x0"] - g["x_tube"] + (g["pad_len"] - g["esc_len"]) / 2   # ESC front, centred on the pad
    x1 = x0 + g["esc_len"]
    y_pad = t / 2 + g["pad_t"]
    y_top = y_pad + g["esc_t"]
    f = LEVELS[lv]
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add(f"esc_L{lv}")
    occ = gmsh.model.occ
    box = occ.addRectangle(-1.0, -1.0, 0, 3.3, 2.0)
    disk = occ.addDisk(0, 0, 0, R, R)
    plate = occ.addRectangle(0.0, -t / 2, 0, L, t)
    pad = occ.addRectangle(x0, t / 2 - BLK_OVL, 0, x1 - x0, y_pad - t / 2 + BLK_OVL)   # 1.2 mm ASA pad (adiabatic)
    blk = occ.addRectangle(x0, y_pad, 0, x1 - x0, y_top - y_pad)                     # ESC (isothermal faces)
    body, _ = occ.fuse([(2, disk)], [(2, plate), (2, pad), (2, blk)])
    fluid, _ = occ.cut([(2, box)], body)
    occ.synchronize()
    curves = gmsh.model.getBoundary(fluid, oriented=False)
    wall, far, esc = [], [], []
    eps = 1e-6
    for dim, tag in curves:
        xmin, ymin, _, xmax, ymax, _ = gmsh.model.getBoundingBox(dim, tag)
        if xmax > 2.2 or xmin < -0.9 or ymax > 0.9 or ymin < -0.9:
            far.append(abs(tag))
        elif ymax > y_pad + eps and xmin > x0 - eps and xmax < x1 + eps:
            esc.append(abs(tag))                       # ESC front and rear (OCC merges them with the 1.2 mm pad face), top
        else:
            wall.append(abs(tag))
    gmsh.model.addPhysicalGroup(1, wall, name="body")
    gmsh.model.addPhysicalGroup(1, esc, name="esc")
    gmsh.model.addPhysicalGroup(1, far, name="farfield")
    gmsh.model.addPhysicalGroup(2, [fluid[0][1]], name="fluid")
    h_wall = 0.0006 * f
    h_esc = 0.00035 * f                                # on and around the ESC
    h_far = 0.08 * f
    y1 = 1.2e-5 * f                                    # first-layer height (y+ < 1 at 16 m/s on L3)
    fld = gmsh.model.mesh.field
    bl = fld.add("BoundaryLayer")
    fld.setNumbers(bl, "CurvesList", wall + esc)
    fld.setNumber(bl, "Size", y1)
    fld.setNumber(bl, "Ratio", BL_RATIO)
    fld.setNumber(bl, "Thickness", BL_THICK[lv])
    fld.setNumber(bl, "Quads", 1)
    for k_, v_ in BL_EXTRA.items():
        fld.setNumber(bl, k_, v_)
    fld.setAsBoundaryLayer(bl)
    dist = fld.add("Distance")
    fld.setNumbers(dist, "CurvesList", wall + esc)
    fld.setNumber(dist, "Sampling", 600)
    th = fld.add("Threshold")
    fld.setNumber(th, "InField", dist)
    fld.setNumber(th, "SizeMin", h_wall)
    fld.setNumber(th, "SizeMax", h_far)
    fld.setNumber(th, "DistMin", 0.002)
    fld.setNumber(th, "DistMax", 0.6)
    wk = fld.add("Box")                                # shear layer, reattachment and wake region
    fld.setNumber(wk, "VIn", 0.0025 * f)
    fld.setNumber(wk, "VOut", h_far)
    fld.setNumber(wk, "XMin", -0.02)
    fld.setNumber(wk, "XMax", L + 0.15)
    fld.setNumber(wk, "YMin", -0.03)
    fld.setNumber(wk, "YMax", 0.035)
    fld.setNumber(wk, "Thickness", 0.05)
    eb = fld.add("Box")                                # ESC neighbourhood
    fld.setNumber(eb, "VIn", h_esc)
    fld.setNumber(eb, "VOut", h_far)
    fld.setNumber(eb, "XMin", R - 0.002)
    fld.setNumber(eb, "XMax", x1 + 0.03)
    fld.setNumber(eb, "YMin", t / 2)
    fld.setNumber(eb, "YMax", y_top + 0.012)
    fld.setNumber(eb, "Thickness", 0.02)
    mn = fld.add("Min")
    fld.setNumbers(mn, "FieldsList", [th, wk, eb])
    fld.setAsBackgroundMesh(mn)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.Algorithm", MESH_ALG)
    gmsh.model.mesh.generate(2)
    out = HERE / "mesh"
    out.mkdir(exist_ok=True)
    fn = out / f"esc_L{lv}.su2"
    gmsh.write(str(fn))
    n = sum(len(t_) for t_ in gmsh.model.mesh.getElements(2)[1])
    gmsh.finalize()
    return fn, n


# ------------------------------------------------------------------------------------------------------------ SU2
CFG = """% generated by redesign/team/E3/sim/cfd/esc_cfd.py ({name})
SOLVER= INC_RANS
KIND_TURB_MODEL= {turb}
KIND_TRANS_MODEL= {trans}
MATH_PROBLEM= DIRECT
RESTART_SOL= NO
INC_NONDIM= DIMENSIONAL
INC_DENSITY_MODEL= CONSTANT
INC_DENSITY_INIT= {rho}
INC_VELOCITY_INIT= ( {U:.8f}, 0.0, 0.0 )
INC_ENERGY_EQUATION= YES
INC_TEMPERATURE_INIT= {tamb}
FLUID_MODEL= CONSTANT_DENSITY
SPECIFIC_HEAT_CP= {cp}
VISCOSITY_MODEL= CONSTANT_VISCOSITY
MU_CONSTANT= {mu}
CONDUCTIVITY_MODEL= CONSTANT_PRANDTL
PRANDTL_LAM= {pr}
TURBULENT_CONDUCTIVITY_MODEL= CONSTANT_PRANDTL_TURB
PRANDTL_TURB= {prt}
FREESTREAM_TURBULENCEINTENSITY= {tu}
FREESTREAM_TURB2LAMVISCRATIO= 10.0
REF_LENGTH= {D}
REF_AREA= {D}
MARKER_HEATFLUX= ( body, 0.0 )
MARKER_ISOTHERMAL= ( esc, {tesc} )
MARKER_FAR= ( farfield )
MARKER_PLOTTING= ( esc )
MARKER_MONITORING= ( esc )
NUM_METHOD_GRAD= WEIGHTED_LEAST_SQUARES
CFL_NUMBER= 5
CFL_ADAPT= YES
CFL_ADAPT_PARAM= ( 0.5, 1.2, 1.0, 100 )
CONV_NUM_METHOD_FLOW= FDS
MUSCL_FLOW= YES
SLOPE_LIMITER_FLOW= VENKATAKRISHNAN
VENKAT_LIMITER_COEFF= 0.05
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
CONV_FIELD= ( TOTAL_HEATFLUX )
CONV_CAUCHY_ELEMS= 300
CONV_CAUCHY_EPS= 1E-5
CONV_STARTITER= 400
MESH_FILENAME= {mesh}
MESH_FORMAT= SU2
SCREEN_OUTPUT= ( INNER_ITER, RMS_PRESSURE, RMS_VELOCITY-X, RMS_TEMPERATURE, TOTAL_HEATFLUX, DRAG )
HISTORY_OUTPUT= ( ITER, RMS_RES, AERO_COEFF, HEAT, CAUCHY )
VOLUME_OUTPUT= ( COORDINATES, SOLUTION, PRIMITIVE )
OUTPUT_FILES= ( SURFACE_CSV, SURFACE_PARAVIEW_ASCII, PARAVIEW )
SURFACE_FILENAME= surface_flow
VOLUME_FILENAME= flow
CONV_FILENAME= history
OUTPUT_WRT_FREQ= 100000
SCREEN_WRT_FREQ_INNER= 100
"""


def run_case(name):
    lv, turb, U, tu = CASES[name]
    d = HERE / "cases" / name
    d.mkdir(parents=True, exist_ok=True)
    mesh = HERE / "mesh" / f"esc_L{lv}.su2"
    trans = "NONE"
    if turb == "SST_LM":
        turb, trans = "SST", "LM"
    cfg = CFG.format(name=name, turb=turb, trans=trans, rho=RHO, U=U, tamb=T_AMB, cp=CP, mu=MU, pr=PR, prt=PRT, tu=tu,
                     D=GEOM["D"], tesc=T_AMB + DT_ESC, iters=3000, mesh=f"../../mesh/esc_L{lv}.su2")
    (d / "case.cfg").write_text(cfg, encoding="utf-8")
    t0 = time.time()
    for attempt in range(4):                           # shared machine: a run killed from outside is restarted
        with open(d / "log.txt", "w") as log:
            subprocess.run([str(SU2), "-t", str(THREADS), "case.cfg"], cwd=str(d), stdout=log, stderr=subprocess.STDOUT)
        if "Exit Success" in (d / "log.txt").read_text(errors="ignore"):
            break
        print(f"  {name}: no 'Exit Success' (attempt {attempt + 1}), restarting", flush=True)
    return time.time() - t0


# ------------------------------------------------------------------------------------------------------------ post
def read_history(name):
    fn = HERE / "cases" / name / "history.csv"
    rows = list(csv.reader(open(fn)))
    head = [h.strip().strip('"') for h in rows[0]]
    data = [[float(x) for x in r] for r in rows[1:] if r]
    return head, data, {h: i for i, h in enumerate(head)}


def read_surface(name):
    """Per-node wall heat flux and y+ on the ESC marker, from the legacy ASCII surface_flow.vtk (the surface CSV of
    the incompressible solver carries only the solution variables)."""
    lines = (HERE / "cases" / name / "surface_flow.vtk").read_text(errors="ignore").splitlines()
    i, n, xy, fields = 0, 0, [], {}
    while i < len(lines):
        ln = lines[i].split()
        if ln and ln[0] == "POINTS":
            n = int(ln[1])
            vals = []
            while len(vals) < 3 * n:
                i += 1
                vals += [float(v) for v in lines[i].split()]
            xy = [(vals[3 * j], vals[3 * j + 1]) for j in range(n)]
        elif ln and ln[0] == "SCALARS" and ln[1] in ("Heat_Flux", "Y_Plus"):
            i += 1                                     # LOOKUP_TABLE line
            vals = []
            while len(vals) < n:
                i += 1
                vals += [float(v) for v in lines[i].split()]
            fields[ln[1]] = vals
        i += 1
    col = {"x": 0, "y": 1, "Heat_Flux": 2, "Y_Plus": 3}
    pts = [[xy[j][0], xy[j][1], fields.get("Heat_Flux", [0.0] * n)[j], fields.get("Y_Plus", [0.0] * n)[j]]
           for j in range(n)]
    return pts, col


def esc_perimeter():
    """Heated section perimeter: top + front and rear faces, which include the 1.2 mm pad face (OCC merges them)."""
    return GEOM["esc_len"] + 2 * (GEOM["esc_t"] + GEOM["pad_t"])


def h_lam(U, L):
    """Incropera eq. 7.30 laminar flat plate, average over L (same as thermal.py's film())."""
    re = U * L / NU
    return 0.664 * re ** 0.5 * PR ** (1 / 3) * K_AIR / L


def h_turb(U, L):
    """Incropera eq. 7.38, fully turbulent flat plate from the leading edge (upper bound for a tripped plate)."""
    re = U * L / NU
    return 0.037 * re ** 0.8 * PR ** (1 / 3) * K_AIR / L


def summarise(name):
    lv, turb, U, tu = CASES[name]
    head, data, col = read_history(name)
    q_i = col.get("TOTAL_HEATFLUX") or col.get("HF")
    n = len(data)
    last = [abs(r[q_i]) for r in data[-500:]]
    q_mean = sum(last) / len(last)
    q_amp = (max(last) - min(last)) / 2
    rms_keys = [k for k in col if k.startswith("rms[")]
    h = q_mean / (esc_perimeter() * DT_ESC)
    out = {"iters": n, "q_wpm_mean_last500": q_mean, "q_halfamp_last500": q_amp,
           "h_wm2k": h, "rms_final": {k: data[-1][col[k]] for k in rms_keys},
           "rms_drop": {k: data[0][col[k]] - data[-1][col[k]] for k in rms_keys}}
    try:
        pts, sc = read_surface(name)
        yp = sc.get("Y_Plus")
        if yp is not None:
            out["yplus_max"] = max(p[yp] for p in pts)
            out["yplus_mean"] = sum(p[yp] for p in pts) / len(pts)
        hf = sc.get("Heat_Flux")
        x, y = sc.get("x"), sc.get("y")
        if hf is not None:
            t = GEOM["t"]
            y_top = t / 2 + GEOM["pad_t"] + GEOM["esc_t"]
            top = [abs(p[hf]) for p in pts if abs(p[y] - y_top) < 1e-5]
            out["h_top_face_wm2k"] = (sum(top) / len(top)) / DT_ESC if top else None
            prof = sorted((p[x], abs(p[hf]) / DT_ESC) for p in pts if abs(p[y] - y_top) < 1e-5)
            out["h_top_profile"] = [[round(a, 5), round(b, 2)] for a, b in prof[:: max(1, len(prof) // 60)]]
    except (OSError, ValueError):
        pass
    L = GEOM["esc_len"]
    out["h_lam_U"] = h_lam(U, L)
    out["h_turb_U"] = h_turb(U, L)
    out["f_eq"] = (h / h_lam(U, L)) ** 2               # local-velocity factor the lumped model would need
    return out


def gci(f1, f2, f3, r21, r32, Fs=1.25):
    """Roache GCI on the fine grid; f1 fine, f3 coarse. Celik et al. (2008) fixed-point for p with unequal r."""
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 or e32 == 0 or e21 * e32 < 0:
        return {"p": None, "f_ext": None, "gci_fine": 3.0 * max(abs(e21), abs(e32)) / abs(f1), "oscillatory": True}
    s = 1.0
    p = 2.0
    for _ in range(200):
        q = math.log((r21 ** p - s) / (r32 ** p - s))
        p = abs(math.log(abs(e32 / e21)) + q) / math.log(r21)
    if p < 0.5:
        return {"p": p, "f_ext": None, "gci_fine": Fs * abs(e21 / f1), "oscillatory": False}
    f_ext = (r21 ** p * f1 - f2) / (r21 ** p - 1)
    return {"p": p, "f_ext": f_ext, "gci_fine": Fs * abs(e21 / f1) / (r21 ** p - 1), "oscillatory": False}


def summary():
    meshes = json.loads((HERE / "mesh" / "cells.json").read_text())
    out = {"geometry": GEOM, "U_hov_ms": U_HOV, "U_cru_ms": U_CRU, "rho": RHO, "mu": MU, "cp": CP, "pr": PR,
           "prt": PRT, "T_amb_K": T_AMB, "dT_esc_K": DT_ESC, "perimeter_m": esc_perimeter(), "cases": {},
           "studies": {}}
    for name, (lv, turb, U, tu) in CASES.items():
        if (HERE / "cases" / name / "history.csv").exists():
            r = summarise(name)
            r.update({"level": lv, "model": turb, "U_ms": U, "Tu": tu, "cells": meshes[f"esc_L{lv}"],
                      "Re_D": U * GEOM["D"] / NU, "Re_L": U * GEOM["esc_len"] / NU})
            out["cases"][name] = r
    for study in ("hov_sst", "cru_sst"):
        c = [out["cases"].get(f"{study}_L{lv}") for lv in (3, 2, 1)]
        if not all(c):
            continue
        r21 = (c[0]["cells"] / c[1]["cells"]) ** 0.5
        r32 = (c[1]["cells"] / c[2]["cells"]) ** 0.5
        f = [x["h_wm2k"] for x in c]
        g = gci(f[0], f[1], f[2], r21, r32)
        U = c[0]["U_ms"]
        L = GEOM["esc_len"]
        h_best = g["f_ext"] if g["f_ext"] else f[0]
        g.update({"h_L3_L2_L1": f, "r21": r21, "r32": r32, "unsteady_halfamp_L3": c[0]["q_halfamp_last500"] /
                  c[0]["q_wpm_mean_last500"], "h_best": h_best, "f_eq_best": (h_best / h_lam(U, L)) ** 2,
                  "h_low_band": h_best * (1 - g["gci_fine"]),
                  "f_eq_low_band": (h_best * (1 - g["gci_fine"]) / h_lam(U, L)) ** 2})
        out["studies"][study] = g
    (HERE / "results.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "h_top_profile"} for k, v in out["cases"].items()},
                     indent=1))
    print(json.dumps(out["studies"], indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    if cmd == "mesh":
        cells = {}
        for lv in LEVELS:
            fn, n = build_mesh(lv)
            cells[f"esc_L{lv}"] = n
            print(fn.name, n, "cells", flush=True)
        (HERE / "mesh").mkdir(exist_ok=True)
        (HERE / "mesh" / "cells.json").write_text(json.dumps(cells, indent=1))
    elif cmd == "run":
        names = sys.argv[2:] or list(CASES)
        for nm in names:
            print(nm, f"{run_case(nm):.0f} s", flush=True)
    else:
        summary()
