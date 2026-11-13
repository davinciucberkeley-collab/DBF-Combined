"""C3 pod FEA (verification round): gmsh meshes + SU2 ELASTICITY on the as-designed pod (D2-R5a CAD, A3-R6a masses).

Run:  python -I redesign/team/C3/pod_fea.py            (all parts in sequence, then combine; ~1.5 h single-thread)
      python -I redesign/team/C3/pod_fea.py --part m1f   (one part: bench, m1f, m1b, m2, m2x; parts can run in parallel)
      python -I redesign/team/C3/pod_fea.py --combine    (merge fea/parts/*.json into fea/fea_results.json + figures)
      python -I redesign/team/C3/pod_fea.py --plots    (re-draw the figures from fea/fea_results.json only)
then  python -I redesign/team/C3/pod_structures.py      (reads fea/fea_results.json into ASM-C3-FEA-*, writes the claims)

Models (SIMULATION-REPORT.md section 2):
  M1  pod-on-wing longitudinal section (x-z), 2.5-D plane stress: every region carries E x (its depth / 0.14 m), so
      the foam under the pod (depth 0.14 m) reads true stress and the side walls / floor / nose wall carry their real
      in-plane stiffness. Pod geometry from subsystems/pod/fusion/pod.py layout() (the CAD's own numbers), wing section
      from subsystems/wing/s5010.dat, spar slot clamped. Load cases: unit Fx, unit Fz, unit My on the floor top
      (superposed for any C1 row) and two crash distributions built from the A3 roll-up items (down, pack at the most
      forward station; up, pack load at the strap stations). Outputs: peel / shear along the pod-to-wing bond, overhang
      wall-top face stress at the LE.
  M2  pack stops (plane strain, x-z through the stop): PETG stop on the 1 mm tray, foam-board floor with explicit
      paper faces, XPS under it (aft stop) or a fixed floor (forward stop). Variants: sharp root (as drawn), 2 mm root
      fillets (C3 spec), section through the tray window (y 0) or through the solid tray edge. Outputs: stop root
      stress (section-linearised and fillet peak), tray-to-board peel.
Every run: 4 mesh levels (h, h/2, h/4, h/8), Richardson extrapolation and GCI on the reported quantities.
SU2 is run single-threaded (-t 1): the design machine is shared with other SU2 jobs and OpenMP oversubscription stalls.
Large files (.su2 meshes, restarts) are deleted after post-processing; configs, logs and per-run summaries are kept in
fea/runs/. Units SI; aircraft frame x aft, z up (2-D model plane x-z).
"""
import csv
import json
import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RED = HERE.parents[1]
OUT = HERE / "fea"
RUNS = OUT / "runs"
SU2 = Path("C:/Users/dillo/tools/su2/bin/bin/SU2_CFD.exe")
sys.path.insert(0, str(RED / "fusion"))
sys.path.insert(0, str(RED / "subsystems" / "pod" / "fusion"))
import k09kit as k9  # noqa: E402
import pod as podcad  # noqa: E402

G0 = 9.80665
LEVELS = [1.0, 0.5, 0.25, 0.125]          # mesh scale factors (h = base x factor)


# ============================================================================ inputs
def _load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


PAR = _load(RED / "params" / "params.json")
LOC = _load(RED / "subsystems" / "pod" / "params.json")
COORDS, AIRFOIL_SRC = k9.section(PAR)
GEO = podcad.layout(lambda k, u=None: k9.val(PAR, k, u), LOC, COORDS)
gv = lambda k: k9.val(PAR, k)
lv = lambda k: LOC[k]["value"]

_NODES = {}


def node(nid):
    """Value of a proof-graph node (assumption/claim value, or calculation outputs) from any team claims file."""
    if not _NODES:
        for f in list((RED / "team").glob("*/claims*.json")) + [RED / "params" / "claims.json"]:
            try:
                d = _load(f)
            except (OSError, ValueError):
                continue
            for n in (d.get("nodes", []) if isinstance(d, dict) else d):
                if isinstance(n, dict) and "id" in n:
                    _NODES.setdefault(n["id"], n)
    n = _NODES[nid]
    return n["outputs"] if n.get("type") == "calculation" else n.get("value")


# materials (assumption ids in brackets; C3-local ones are declared in pod_structures.py)
MAT = {
    "E_face": node("ASM-C4-FACE-E"), "t_face": node("ASM-C4-FACE-T"), "E_core": node("ASM-C4-CORE-E"),
    "E_xps": 20.0e6, "nu_xps": 0.25,          # ASM-C3-XPS-E: 2 G (1 + nu), G 8 MPa (ASM-D6-XPS-G)
    "E_petg": 1.8e9, "nu_petg": 0.38,         # ASM-C3-PETG-E: printed PETG, Prusament class 1.5-2.0 GPa
    "nu_board": 0.30, "nu_core": 0.10,
    "E_epoxy": 3.0e9, "nu_epoxy": 0.35,       # ASM-C3-EPOXY-E: laminating epoxy with microballoons, 2.5-3.5 GPa
}
TB = gv("fins.board_t_m")
MAT["E_board"] = (2 * MAT["E_face"] * MAT["t_face"] + MAT["E_core"] * (TB - 2 * MAT["t_face"])) / TB
ALLOW = {"xps_t": node("ASM-D2-XPS-ALLOW"), "xps_s": node("CL-C3-ALLOW-XPS-SHEAR"),
         "paper_s": node("CL-C3-ALLOW-PAPER-SHEAR"), "board_flat": node("CL-C3-ALLOW-BOARD-FLAT"),
         "face": node("ASM-C4-FACE-SIGMA"), "petg": node("ASM-C4-PETG-TENSILE")}
D0 = 0.002                                     # ASM-C3-FEA-D0: averaging length for bond peaks at bi-material corners
K_DESIGN = gv("requirements.safety_factor_ult") * node("ASM-C1-FITTING-FACTOR") * node("ASM-C1-PRINTED-FACTOR")
N_CRASH = node("CL-C1-CRASH-N")
N_DESIGN_OVH = node("CL-C1-N-LIMIT-POS") * K_DESIGN

# A3 roll-up items that load the pod-to-wing bond (the handle group sits on the spar: E-POD-09)
SPAR_MOUNTED = {"POD-005", "POD-007", "AVN-002"}
_A3 = _load(RED / "team" / "A3" / "rollup" / "mass_items.json")["a3"]["rollup"]["items"]["value"]
GROUP = [(r[0], r[3] / 1000, r[4], r[6]) for r in _A3
         if r[1] in ("pod", "avionics", "power", "harness") and r[0] not in SPAR_MOUNTED
         and abs(r[5]) < 0.07 and r[0] != "PWR-001" and not r[0].startswith("HRN-002")]
PACK_MAX = max(node("ASM-A3-PACK-RANGE")) / 1000
PACK_X_FWD = node("CL-D2-PACK-X-FWD-MIN")
PACK_L = gv("battery.size_m")[0]


# ============================================================================ mesh + SU2 helpers
def mesh_to_arrays(gmsh, surf_mat):
    """Nodes (N,2), triangles (M,3), material per triangle, from the current gmsh model."""
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    xyz = xyz.reshape(-1, 3)[:, :2]
    pos = {int(t): i for i, t in enumerate(tags)}
    raw, mats = [], []
    for s, m in surf_mat.items():
        et, _, en = gmsh.model.mesh.getElements(2, s)
        for t, nn in zip(et, en):
            if t != 2:
                raise RuntimeError("non-triangle element type %d" % t)
            for tri in np.asarray(nn).reshape(-1, 3):
                raw.append([int(n) for n in tri])
                mats.append(m)
    used = sorted({n for tri in raw for n in tri})          # drop nodes that belong to no triangle
    idx = {t: i for i, t in enumerate(used)}
    xyz = xyz[[pos[t] for t in used]]
    tris = np.array([[idx[n] for n in tri] for tri in raw])
    # orient counter-clockwise
    p = xyz[tris]
    a2 = (p[:, 1, 0] - p[:, 0, 0]) * (p[:, 2, 1] - p[:, 0, 1]) - (p[:, 2, 0] - p[:, 0, 0]) * (p[:, 1, 1] - p[:, 0, 1])
    neg = a2 < 0
    tris[neg] = tris[neg][:, [0, 2, 1]]
    return xyz, tris, np.array(mats), idx


def curve_edges(gmsh, idx, curves):
    lines = []
    for c in curves:
        _, _, en = gmsh.model.mesh.getElements(1, c)
        for nn in en:
            lines += [[idx[int(n)] for n in l] for l in np.asarray(nn).reshape(-1, 2)]
    return lines


def write_su2(path, xyz, tris, markers):
    with open(path, "w") as f:
        f.write("NDIME= 2\nNELEM= %d\n" % len(tris))
        for i, e in enumerate(tris):
            f.write("5 %d %d %d %d\n" % (e[0], e[1], e[2], i))
        f.write("NPOIN= %d\n" % len(xyz))
        for i, p in enumerate(xyz):
            f.write("%.12e %.12e %d\n" % (p[0], p[1], i))
        f.write("NMARK= %d\n" % len(markers))
        for name, lines in markers.items():
            f.write("MARKER_TAG= %s\nMARKER_ELEMS= %d\n" % (name, len(lines)))
            for l in lines:
                f.write("3 %d %d\n" % (l[0], l[1]))


def run_su2(rundir, xyz, tris, emat, mats, markers, clamped, loads, plane):
    """mats: list of (E, nu); loads: {marker: (tx, tz)} traction in Pa (markers not listed get zero load).
    Returns nodal displacement (N,2) and the wall time."""
    rundir.mkdir(parents=True, exist_ok=True)
    write_su2(rundir / "mesh.su2", xyz, tris, markers)
    with open(rundir / "props.dat", "w") as f:
        f.write("ID MATERIAL ELEMENT DV\n")
        for i, m in enumerate(emat):
            f.write("%d %d 0 0\n" % (i, m))
    ld = []
    for m in markers:
        if m in clamped:
            continue
        tx, tz = loads.get(m, (0.0, 0.0))
        mag = math.hypot(tx, tz)
        d = (tx / mag, tz / mag) if mag > 0 else (0.0, -1.0)
        ld.append("%s, 1.0, %.10e, %.10f, %.10f, 0.0" % (m, mag, d[0], d[1]))
    fmt = lambda v: "(" + ", ".join("%.6e" % x for x in v) + ")"
    cfg = "\n".join([
        "SOLVER= ELASTICITY", "MATH_PROBLEM= DIRECT", "GEOMETRIC_CONDITIONS= SMALL_DEFORMATIONS",
        "MATERIAL_MODEL= LINEAR_ELASTIC", "FORMULATION_ELASTICITY_2D= %s" % plane,
        "ELASTICITY_MODULUS= " + fmt([m[0] for m in mats]), "POISSON_RATIO= " + fmt([m[1] for m in mats]),
        "MATERIAL_DENSITY= " + fmt([1000.0] * len(mats)),
        "MATERIAL_THERMAL_EXPANSION_COEFF= " + fmt([0.0] * len(mats)), "FEA_FILENAME= props.dat",
        "MARKER_CLAMPED= ( %s )" % ", ".join(clamped), "MARKER_LOAD= ( %s )" % ", ".join(ld),
        "INNER_ITER= 1", "LINEAR_SOLVER= CONJUGATE_GRADIENT", "LINEAR_SOLVER_PREC= ILU",
        "LINEAR_SOLVER_ERROR= 1E-10", "LINEAR_SOLVER_ITER= 200000", "LINEAR_SOLVER_ILU_FILL_IN= 3",
        "MESH_FILENAME= mesh.su2", "MESH_FORMAT= SU2", "OUTPUT_FILES= (RESTART_ASCII)",
        "RESTART_FILENAME= restart.csv", "VOLUME_OUTPUT= (COORDINATES, SOLUTION)",
        "SCREEN_OUTPUT= (INNER_ITER, RMS_UTOL)", ""])
    (rundir / "case.cfg").write_text(cfg, encoding="ascii")
    t0 = time.time()
    with open(rundir / "log.txt", "w") as log:
        rc = subprocess.run([str(SU2), "-t", "1", "case.cfg"], cwd=rundir, stdout=log, stderr=subprocess.STDOUT,
                            timeout=3600).returncode
    dt = time.time() - t0
    if rc != 0 or not (rundir / "restart.csv").exists():
        raise RuntimeError("SU2 failed in %s (rc %d), see log.txt" % (rundir, rc))
    with open(rundir / "restart.csv") as f:
        rd = csv.reader(f)
        head = [h.strip().strip('"') for h in next(rd)]
        ix, iy = head.index("Displacement_x"), head.index("Displacement_y")
        ip = head.index("PointID")
        u = np.zeros((len(xyz), 2))
        for row in rd:
            u[int(float(row[ip]))] = (float(row[ix]), float(row[iy]))
    for big in ("mesh.su2", "restart.csv", "props.dat"):
        (rundir / big).unlink(missing_ok=True)
    return u, dt


def dmat(E, nu, plane):
    if plane == "PLANE_STRESS":
        return E / (1 - nu * nu) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    return E / ((1 + nu) * (1 - 2 * nu)) * np.array([[1 - nu, nu, 0], [nu, 1 - nu, 0], [0, 0, (1 - 2 * nu) / 2]])


def tri_strain_stress(xyz, tris, emat, mats, u, plane):
    """Constant-strain triangle: strain [exx, ezz, gxz] and stress [sxx, szz, sxz] per element."""
    p = xyz[tris]
    x, z = p[:, :, 0], p[:, :, 1]
    A2 = (x[:, 1] - x[:, 0]) * (z[:, 2] - z[:, 0]) - (x[:, 2] - x[:, 0]) * (z[:, 1] - z[:, 0])
    b = np.stack([z[:, 1] - z[:, 2], z[:, 2] - z[:, 0], z[:, 0] - z[:, 1]], 1) / A2[:, None]
    c = np.stack([x[:, 2] - x[:, 1], x[:, 0] - x[:, 2], x[:, 1] - x[:, 0]], 1) / A2[:, None]
    ue = u[tris]
    exx = (b * ue[:, :, 0]).sum(1)
    ezz = (c * ue[:, :, 1]).sum(1)
    gxz = (c * ue[:, :, 0]).sum(1) + (b * ue[:, :, 1]).sum(1)
    eps = np.stack([exx, ezz, gxz], 1)
    sig = np.zeros_like(eps)
    for m, (E, nu) in enumerate(mats):
        k = emat == m
        sig[k] = eps[k] @ dmat(E, nu, plane).T
    return eps, sig, p.mean(1), np.abs(A2) / 2


def nodal_interface_force(xyz, tris, emat, sig, area, side_a, side_b):
    """Exact interface resultant (per unit depth): internal nodal forces of the side_a elements summed over the nodes
    shared with side_b (variationally consistent, unlike integrating element-centroid tractions)."""
    p = xyz[tris]
    x, z = p[:, :, 0], p[:, :, 1]
    A2 = (x[:, 1] - x[:, 0]) * (z[:, 2] - z[:, 0]) - (x[:, 2] - x[:, 0]) * (z[:, 1] - z[:, 0])
    b = np.stack([z[:, 1] - z[:, 2], z[:, 2] - z[:, 0], z[:, 0] - z[:, 1]], 1) / A2[:, None]
    c = np.stack([x[:, 2] - x[:, 1], x[:, 0] - x[:, 2], x[:, 1] - x[:, 0]], 1) / A2[:, None]
    fx = (b * sig[:, 0:1] + c * sig[:, 2:3]) * area[:, None]
    fz = (c * sig[:, 1:2] + b * sig[:, 2:3]) * area[:, None]
    ina, inb = np.isin(emat, list(side_a)), np.isin(emat, list(side_b))
    shared = np.intersect1d(np.unique(tris[ina]), np.unique(tris[inb]))
    f = np.zeros((len(xyz), 2))
    for k in range(3):
        np.add.at(f[:, 0], tris[ina, k], fx[ina, k])
        np.add.at(f[:, 1], tris[ina, k], fz[ina, k])
    return f[shared].sum(0)


def interface_tractions(xyz, tris, emat, sig, side_a, side_b):
    """Edges shared by an element of materials side_a and one of side_b. Traction on the side_a element, normal
    pointing out of side_a. Returns rows (s_mid_x, s_mid_z, length, sigma_n, tau, nx, nz)."""
    edges = {}
    for e, t in enumerate(tris):
        for i, j in ((0, 1), (1, 2), (2, 0)):
            key = (min(t[i], t[j]), max(t[i], t[j]))
            edges.setdefault(key, []).append(e)
    rows = []
    for (i, j), es in edges.items():
        if len(es) != 2:
            continue
        ea, eb = es
        if emat[ea] in side_b and emat[eb] in side_a:
            ea, eb = eb, ea
        if not (emat[ea] in side_a and emat[eb] in side_b):
            continue
        p, q = xyz[i], xyz[j]
        L = np.linalg.norm(q - p)
        t = (q - p) / L
        n = np.array([t[1], -t[0]])
        cen = xyz[tris[ea]].mean(0)
        if np.dot(n, (p + q) / 2 - cen) < 0:
            n = -n
        S = np.array([[sig[ea, 0], sig[ea, 2]], [sig[ea, 2], sig[ea, 1]]])
        tr = S @ n
        tt = np.array([-n[1], n[0]])
        if tt[0] < 0:
            tt = -tt
        rows.append(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, L, float(tr @ n), float(tr @ tt), n[0], n[1], tt[0], tt[1],
                     float(emat[eb])))
    rows.sort(key=lambda r: (round(r[0], 9), r[1]))
    rows = np.array(rows)
    arc = np.cumsum(rows[:, 2]) - rows[:, 2] / 2           # arc length along the chain (sorted by x, then z)
    return np.column_stack([rows, arc])


def window_avg(s, v, w, d0):
    """Max over positions of the length-weighted mean of v over a window d0 along the coordinate s."""
    best = -1e300
    for k in range(len(s)):
        m = np.abs(s - s[k]) <= d0 / 2
        best = max(best, float((v[m] * w[m]).sum() / w[m].sum()))
    return best


def richardson(h, q):
    """Order, extrapolated value and GCI (fine grid, Fs 1.25) from the three finest levels (h ascending)."""
    q1, q2, q3 = q[0], q[1], q[2]       # fine, medium, coarse
    r = h[1] / h[0]
    e21, e32 = q2 - q1, q3 - q2
    if e21 == 0 or e32 == 0 or e32 / e21 <= 0:
        return {"p": None, "q_ext": q1, "gci_pct": None, "note": "non-monotone: report the spread"}
    p = math.log(abs(e32 / e21)) / math.log(r)
    q_ext = q1 + (q1 - q2) / (r ** p - 1)
    gci = 1.25 * abs((q1 - q2) / q1) / (r ** p - 1) * 100 if q1 else None
    return {"p": p, "q_ext": q_ext, "gci_pct": gci}


# ============================================================================ M1: pod on the wing
B_REF = gv("pod.size_m")[1]                   # 0.14 m: reference depth (pod width = foam depth under the pod)
# WNG-007 recess-step fillet legs (D-69, CR-C3-17), capped as subsystems/wing/fusion/wing.py geometry() rf_legs does
_WL = _load(RED / "subsystems" / "wing" / "params.json")["recess"]["step_fillet_legs_m"]["value"]
FILLET_LEGS = (_WL[0], min(_WL[1], k9.surface_z(COORDS, gv("wing.chord_m"), GEO["x_rec1"] / gv("wing.chord_m"), "upper")
                           - GEO["zb"], TB))
HEEL = (LOC["strut_chord_m"]["value"] if "strut_chord_m" in LOC else [0.040, 0.0015, 0.008])  # width y, chord t, bridge lap
SCARF_X = None                                 # study override of the fillet / floor-scarf run along x (part m1tfl10)
E_FILLET_SOFT = 1.0e9                        # sensitivity: light microballoon mix (C3 choice, 1/3 of ASM-C3-EPOXY-E)
SEG = 0.005                                    # floor-top load segment length


def m1_geometry(bonded=True, stepgap=False):
    """bonded: the side walls aft of the recess end are bonded to the wing skin line (as drawn, E-POD-01).
    bonded=False: a 0.3 mm gap there, so the pod reaches the wing only through the floor / LE filler footprint (the
    hand calc's footprint; the wall-edge bonds are assumed already peeled)."""
    gap = 0.0 if bonded else 0.0003
    g = GEO
    c = gv("wing.chord_m")
    surf = lambda x: k9.surface_z(COORDS, c, x / c, "upper")
    low = lambda x: k9.surface_z(COORDS, c, x / c, "lower")
    x_cut = 0.16
    n = 60
    xs_ = lambda a, b, k: [a + (b - a) * (1 - math.cos(math.pi * i / k)) / 2 for i in range(k + 1)]
    x_aft = [g["x_rec1"] + i * (g["x1"] - g["x_rec1"]) / 8 for i in range(9)]           # walls bond line (pod.py)
    x_aft += [x for x in xs_(g["x1"], x_cut, 16)[1:]]
    up_aft = [(x, surf(x)) for x in reversed(x_aft)]
    up_fwd = [(x, surf(x)) for x in reversed(xs_(0.0, g["x_rec0"], 16))]
    lo = [(x, low(x)) for x in xs_(0.0, x_cut, n)]
    wing = up_aft + [(g["x_rec1"], g["zb"]), (g["x_rec0"], g["zb"])] + up_fwd[1:] + lo[1:]
    filler = [(0.0, g["zb"]), (g["x_rec0"], g["zb"])] + up_fwd[1:]
    aft = [(x, surf(x)) for x in x_aft[:9]]
    if bonded:
        walls = [(g["xn"], g["zf"]), (g["x_rec1"], g["zf"])] + aft + [(g["x1"], g["zh"]), (g["xn"], g["zh"])]
    else:
        walls = [(g["xn"], g["zf"]), (g["x_rec1"] - gap, g["zf"]), (g["x_rec1"] - gap, aft[0][1] + gap)] +                 [(x, z + gap) for x, z in aft] + [(g["x1"], g["zh"]), (g["xn"], g["zh"])]
    nseg = max(1, round((g["x_rec1"] - g["xn"]) / SEG))
    # stepgap (C3-R3 detail fix): the floor's aft end face is kept 0.3 mm off the recess step (release tape), so the
    # floor bonds to the recess floor only and the re-entrant step corner carries nothing
    segx = np.linspace(g["xn"], g["x_rec1"] - (0.0003 if stepgap else 0.0), nseg + 1)
    return {"wing": wing, "filler": filler, "walls": walls, "segx": segx, "x_cut": x_cut}


SADDLE_X = (0.0688, 0.0912)                    # wing saddle windows (subsystems/wing SPEC: x 0.0688-0.0912, y 0.029-0.053)
SADDLE_FRAC = 2 * (0.053 - 0.029) / gv("pod.size_m")[1]   # share of the 0.14 m model depth the two printed feet fill


def m1_mesh(gmsh, h, bonded=True, tied=False, stepgap=False, fillet=False, heel=False):
    """tied (C3-R3 fix candidate, CR-C3-16): the handle feet in the saddle windows are bonded to the pod side walls,
    so the pod reaches the spar through printed PETG (smeared over the model depth) as well as through the XPS."""
    g, G = GEO, m1_geometry(bonded, stepgap)
    o = gmsh.model.occ
    gmsh.model.add("m1")

    def poly(pts):
        ps = [o.addPoint(x, z, 0) for x, z in pts]
        ls = [o.addLine(ps[i], ps[(i + 1) % len(ps)]) for i in range(len(ps))]
        return o.addPlaneSurface([o.addCurveLoop(ls)])

    wing = poly(G["wing"])
    hole = o.addDisk(gv("wing.spar.x_m"), gv("wing.spar.z_m"), 0, gv("wing.spar.od_m") / 2, gv("wing.spar.od_m") / 2)
    wing = o.cut([(2, wing)], [(2, hole)])[0][0][1]
    filler = poly(G["filler"])
    walls = poly(G["walls"])
    nose = o.addRectangle(g["x0"], g["zb"], 0, g["xn"] - g["x0"], g["zh"] - g["zb"])
    segs = [o.addRectangle(a, g["zb"], 0, b - a, g["zf"] - g["zb"]) for a, b in zip(G["segx"][:-1], G["segx"][1:])]
    inputs = [(2, wing), (2, filler), (2, walls), (2, nose)] + [(2, s) for s in segs]
    kinds = ["wing", "filler", "walls", "nose"] + ["floor"] * len(segs)
    if fillet:
        # C3-R4 (CR-C3-17, D-69, D-84 d): WNG-007 microballoon fillet in the recess-step corner (legs: wing.py
        # geometry rf_legs, 5 mm along the floor, the step leg capped at the 4.8 mm floor board) and the pod floor's
        # aft lower edge bevelled 45 deg onto it (pod.py floor_bevel_m, capped at the board). The fillet is sanded to
        # the floor bevel (subsystems/wing/params.json recess.step_fillet_legs_m note), so the modelled fillet is the
        # triangle the bevel removes from the floor: (x_rec1 - bv, zb), (x_rec1, zb), (x_rec1, zb + lw); the 0.2 mm
        # of floor leg beyond the bevel foot lies inside the bond-line tolerance.
        bv = SCARF_X if SCARF_X else (lv("floor_bevel_run_m") if "floor_bevel_run_m" in LOC else min(lv("floor_bevel_m"), TB))
        lw = FILLET_LEGS[1]
        x1 = g["x_rec1"]
        tri_pts = [(x1 - bv, g["zb"]), (x1, g["zb"]), (x1, g["zb"] + lw)]
        segs2 = []
        for s_, (a_, b_) in zip(segs, zip(G["segx"][:-1], G["segx"][1:])):
            if b_ <= x1 - bv + 1e-9:
                segs2.append(s_)
            else:                                   # only the segments the bevel reaches lose its triangle
                segs2 += [t_ for _, t_ in o.cut([(2, s_)], [(2, poly(tri_pts))])[0]]
        segs = segs2
        inputs = [(2, wing), (2, filler), (2, walls), (2, nose)] + [(2, s_) for s_ in segs] + [(2, poly(tri_pts))]
        kinds = ["wing", "filler", "walls", "nose"] + ["floor"] * len(segs) + ["fillet"]
    if heel:
        # C3-R4 fix candidate for the crash peel at the recess-step top (CR-C3-17 as drawn does not reach it): a
        # PETG lower chord under the aft-stop strut ribs (printed with POD-007), bonded on the tray rear piece from
        # the aft stop's back face to the floor's aft end, crossing the step 0.3 mm clear of the wing skin and
        # joining the foot bridge, which is bonded on the slot fill / spar with the feet. Smeared over its width.
        x_a = lv("aft_stop_x_m") + lv("aft_stop_m")[0]
        x_b0 = lv("bridge_x0_m")
        x_b1 = x_b0 + HEEL[2]
        c_ = gv("wing.chord_m")
        sf_ = lambda x: k9.surface_z(COORDS, c_, x / c_, "upper")
        z_g = max(sf_(g["x_rec1"] + (x_b0 - g["x_rec1"]) * i / 20) for i in range(21)) + 0.0003
        z_top = z_g + HEEL[1]
        pts = [(x_a, g["zf"]), (g["x_rec1"], g["zf"]), (g["x_rec1"], z_g), (x_b0, z_g)]
        pts += [(x_b0 + (x_b1 - x_b0) * i / 6, sf_(x_b0 + (x_b1 - x_b0) * i / 6)) for i in range(7)]
        pts += [(x_b1, z_top), (x_a, z_top)]
        inputs = [(2, poly(pts))] + inputs
        kinds = ["heel"] + kinds
    if tied:
        zs_ = gv("wing.spar.z_m")
        top = [(x, k9.surface_z(COORDS, gv("wing.chord_m"), x / gv("wing.chord_m"), "upper") + (0.0 if bonded else 0.0003))
               for x in np.linspace(SADDLE_X[1], SADDLE_X[0], 9)]
        sad = poly([(SADDLE_X[0], zs_), (SADDLE_X[1], zs_)] + top)
        sad = o.cut([(2, sad)], [(2, o.addDisk(gv("wing.spar.x_m"), zs_, 0, gv("wing.spar.od_m") / 2,
                                               gv("wing.spar.od_m") / 2))])[0][0][1]
        inputs = [(2, sad)] + inputs
        kinds = ["saddle"] + kinds
    _, omap = o.fragment(inputs, [])
    o.synchronize()
    kind_of = {}
    for k, children in zip(kinds, omap):
        for d, t in children:
            kind_of.setdefault(t, k)          # first owner wins (walls overlap nose/floor only by touching)
    MID = {"wing": 0, "filler": 1, "walls": 2, "floor": 3, "nose": 4, "saddle": 5, "fillet": 6, "heel": 7}
    surf_mat = {t: MID[k] for t, k in kind_of.items()}
    # curves
    xs, zs, rs = gv("wing.spar.x_m"), gv("wing.spar.z_m"), gv("wing.spar.od_m") / 2
    spar, interface, segtop = [], [], {}
    wing_s = {t for t, k in kind_of.items() if k == "wing"}
    for _, cv in gmsh.model.getEntities(1):
        bb = gmsh.model.getBoundingBox(1, cv)
        cx, cz = (bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2
        if abs(cx - xs) < rs * 1.01 and abs(cz - zs) < rs * 1.01:
            lo_, hi_ = gmsh.model.getParametrizationBounds(1, cv)
            pts = gmsh.model.getValue(1, cv, list(np.linspace(lo_[0], hi_[0], 5))).reshape(-1, 3)
            if np.all(np.abs(np.hypot(pts[:, 0] - xs, pts[:, 1] - zs) - rs) < 1e-6):
                spar.append(cv)
                continue
        up, _ = gmsh.model.getAdjacencies(1, cv)
        ks = {kind_of.get(int(s)) for s in up}
        if len(up) == 2 and "wing" in ks and len(ks) == 2:
            interface.append(cv)
        if abs(bb[1] - g["zf"]) < 2e-6 and abs(bb[4] - g["zf"]) < 2e-6:
            for j, (a, b) in enumerate(zip(G["segx"][:-1], G["segx"][1:])):
                if bb[0] >= a - 2e-5 and bb[3] <= b + 2e-5 and (bb[0] + bb[3]) / 2 > a and (bb[0] + bb[3]) / 2 < b:
                    segtop.setdefault(j, []).append(cv)
    if not spar or len(segtop) != len(segs):
        raise RuntimeError("M1 curve classification failed (spar %d, segments %d/%d)" % (len(spar), len(segtop), len(segs)))
    f = gmsh.model.mesh.field
    f.add("Distance", 1)
    f.setNumbers(1, "CurvesList", interface)
    f.setNumber(1, "Sampling", 400)
    f.add("Threshold", 2)
    f.setNumber(2, "InField", 1)
    f.setNumber(2, "SizeMin", h / 8)
    f.setNumber(2, "SizeMax", h)
    f.setNumber(2, "DistMin", 0.0015)
    f.setNumber(2, "DistMax", 0.012)
    f.setAsBackgroundMesh(2)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.MeshSizeMax", h)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.model.mesh.generate(2)
    xyz, tris, emat, idx = mesh_to_arrays(gmsh, surf_mat)
    markers = {"spar": curve_edges(gmsh, idx, spar)}
    for j in range(len(segs)):
        markers["seg%02d" % j] = curve_edges(gmsh, idx, segtop[j])
    return xyz, tris, emat, markers, G["segx"]


def m1_mats(fillet_soft=False):
    Eb, nb = MAT["E_board"], MAT["nu_board"]
    e_sad = SADDLE_FRAC * MAT["E_petg"] + (1 - SADDLE_FRAC) * MAT["E_xps"]
    # index 6: the WNG-007 fillet runs the full recess width (|y| <= 0.070 = B_REF / 2), so no depth scaling
    return [(MAT["E_xps"], MAT["nu_xps"]), (MAT["E_xps"], MAT["nu_xps"]),
            (Eb * 2 * TB / B_REF, nb), (Eb * GEO["W"] / B_REF, nb), (Eb * GEO["W"] / B_REF, nb), (e_sad, 0.35),
            (E_FILLET_SOFT if fillet_soft else MAT["E_epoxy"], MAT["nu_epoxy"]),
            (MAT["E_petg"] * HEEL[0] / B_REF, MAT["nu_petg"])]          # 7: strut lower chord, smeared over its width


def seg_forces_from_items(segx, items):
    """items: (mass kg, x0, x1) spread uniformly over [x0, x1] clipped to the floor; returns per-segment mass."""
    m = np.zeros(len(segx) - 1)
    lo, hi = segx[0], segx[-1]
    for mass, a, b in items:
        a, b = max(a, lo), min(b, hi)
        if b <= a:
            a, b = (lo, lo + SEG) if b <= lo else (hi - SEG, hi)
        for j in range(len(m)):
            ov = max(0.0, min(b, segx[j + 1]) - max(a, segx[j]))
            m[j] += mass * ov / (b - a)
    return m


def m1_cases(segx):
    """Per-segment real forces (N) [(Fx_j, Fz_j)] for the unit and crash cases."""
    L = np.diff(segx)
    xm = (segx[:-1] + segx[1:]) / 2
    xc = float((xm * L).sum() / L.sum())
    cases = {"U_FX": [(l / L.sum(), 0.0) for l in L], "U_FZ": [(0.0, l / L.sum()) for l in L]}
    w = -(xm - xc) * L
    w = w / float(-((xm - xc) * w).sum())       # My = -sum (x - xc) Fz = +1 N m
    cases["U_MY"] = [(0.0, v) for v in w]
    spread = 0.010
    base = [(m, x - spread, x + spread) for _, m, x, _ in GROUP]
    pack_dn = [(PACK_MAX, PACK_X_FWD - PACK_L / 2, PACK_X_FWD + PACK_L / 2)]
    sx = lv("strap_x_m")
    sw = lv("strap_w_m") / 2 + 0.010
    pack_up = [(PACK_MAX / 2, s - sw, s + sw) for s in sx]
    mdn = seg_forces_from_items(segx, base + pack_dn)
    mup = seg_forces_from_items(segx, base + pack_up)
    cases["CRASH_DN"] = [(0.0, -v * N_CRASH * G0) for v in mdn]
    cases["CRASH_UP"] = [(0.0, v * N_CRASH * G0) for v in mup]
    return cases, xc, float(mdn.sum())


def run_m1(level_factor, bonded=True, h0=0.004, tied=False, stepgap=False, fillet=False, fillet_soft=False,
           heel=False):
    import gmsh
    h = h0 * level_factor
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    try:
        xyz, tris, emat, markers, segx = m1_mesh(gmsh, h, bonded, tied, stepgap, fillet, heel)
    finally:
        gmsh.finalize()
    mats = m1_mats(fillet_soft)
    if not (fillet or heel):
        mats = mats[:6]
    cases, xc, m_dn = m1_cases(segx)
    L = np.diff(segx)
    res = {"h_m": h, "n_elem": int(len(tris)), "n_node": int(len(xyz)), "cases": {}}
    for name, F in cases.items():
        loads = {"seg%02d" % j: (F[j][0] / (B_REF * L[j]), F[j][1] / (B_REF * L[j])) for j in range(len(L))}
        tag = (("M1-TIED" if bonded else "M1-TIED-FP-GAP" if stepgap else "M1-TIED-FP") if tied else "M1-BONDED" if bonded else "M1-FOOTPRINT")
        if fillet:
            tag = ("M1-TIED-FP-FILLET" + ("-SOFT" if fillet_soft else "") + ("-HEEL" if heel else "")
                   + ("-SCARF%d" % round(SCARF_X * 1000) if SCARF_X else ""))
        rd = RUNS / tag / ("L%d" % LEVELS.index(level_factor)) / name
        u, dt = run_su2(rd, xyz, tris, emat, mats, markers, ["spar"], loads, "PLANE_STRESS")
        eps, sig, cen, area = tri_strain_stress(xyz, tris, emat, mats, u, "PLANE_STRESS")
        pod_side = {1, 2, 3, 4, 6}                 # 6: the WNG-007 fillet (laid on the core, carries the floor end)
        it = interface_tractions(xyz, tris, emat, sig, {0}, pod_side)
        Fint = nodal_interface_force(xyz, tris, emat, sig, area, {0}, pod_side) * B_REF
        Ftr = np.array([((it[:, 3] * it[:, 5] + it[:, 4] * it[:, 7]) * it[:, 2]).sum(),
                        ((it[:, 3] * it[:, 6] + it[:, 4] * it[:, 8]) * it[:, 2]).sum()]) * B_REF
        # wall-top / floor-bottom face stress at the LE (x = 0): linear fit of exx over the section (walls + floor)
        col = (np.abs(cen[:, 0]) < 0.0015) & np.isin(emat, [2, 3])
        A = np.vstack([np.ones(col.sum()), cen[col, 1]]).T
        coef = np.linalg.lstsq(A, eps[col, 0], rcond=None)[0]
        face_top = MAT["E_face"] * (coef[0] + coef[1] * GEO["zh"])
        face_bot = MAT["E_face"] * (coef[0] + coef[1] * GEO["zb"])
        if fillet:    # floor board's bevelled end on the fillet face (board side, normal out of the board)
            rec_ff = interface_tractions(xyz, tris, emat, sig, {3}, {6}).tolist()
        rec = {"interface": it.tolist(), "F_interface_N": Fint.tolist(), "F_interface_traction_N": Ftr.tolist(),
               "F_applied_N": [float(sum(f[0] for f in F)), float(sum(f[1] for f in F))],
               "face_top_pa": float(face_top), "face_bot_pa": float(face_bot), "su2_s": dt,
               "u_max_m": float(np.abs(u).max())}
        if fillet:
            rec["interface_ff"] = rec_ff
        if tied:      # force the pod puts into the saddle (walls -> printed feet), real N
            rec["F_saddle_N"] = (nodal_interface_force(xyz, tris, emat, sig, area, {5}, {2, 3, 4}) * B_REF).tolist()
        (rd / "summary.json").write_text(json.dumps({k: v for k, v in rec.items() if k not in ("interface", "interface_ff")}, indent=1))
        res["cases"][name] = rec
        print("  M1 %s L%d %-9s %6d el  %5.1f s  F_int %s vs %s" % ("B" if bonded else "F", LEVELS.index(level_factor), name, len(tris), dt,
              np.round(Fint, 3), np.round(rec["F_applied_N"], 3)), flush=True)
    res["xc_seg"] = xc
    res["m_crash_dn_kg"] = m_dn
    return res


def m1_combine(cases, coeffs):
    """Linear combination of interface traction rows (same mesh) and face stresses."""
    base = np.array(cases[next(iter(coeffs))]["interface"])
    sn = sum(c * np.array(cases[k]["interface"])[:, 3] for k, c in coeffs.items())
    tau = sum(c * np.array(cases[k]["interface"])[:, 4] for k, c in coeffs.items())
    top = sum(c * cases[k]["face_top_pa"] for k, c in coeffs.items())
    bot = sum(c * cases[k]["face_bot_pa"] for k, c in coeffs.items())
    return base, sn, tau, top, bot


def bond_metrics(base, sn, tau):
    s, w = base[:, 10], base[:, 2]                  # arc length along the bond line, edge length
    # where the pod side is the side walls alone (aft of the recess end) the bond is the two 4.8 mm wall edges, not the
    # 0.14 m model depth: real stress = model traction x b_ref / (2 t_board)
    k = np.where(base[:, 9] == 2, B_REF / (2 * TB), 1.0)
    sn, tau = sn * k, tau * k
    R = np.maximum(sn, 0) / ALLOW["xps_t"] + np.abs(tau) / ALLOW["xps_s"]
    return {"sigma_peak_raw": float(sn.max()), "tau_peak_raw": float(np.abs(tau).max()),
            "sigma_peak_d0": window_avg(s, sn, w, D0), "tau_peak_d0": window_avg(s, np.abs(tau), w, D0),
            "R_peak_d0": window_avg(s, R, w, D0), "R_peak_raw": float(R.max()),
            "sigma_peak_5mm": window_avg(s, sn, w, 0.005), "R_peak_5mm": window_avg(s, R, w, 0.005),
            "x_R_peak": float(base[int(np.argmax(R)), 0]), "z_R_peak": float(base[int(np.argmax(R)), 1])}


def c1_design_row():
    calc = node("CALC-C3-BOND")
    case = calc["case"]
    for r in node("ASM-C3-POD-LOADS"):
        if r[0] == case:
            return case, [K_DESIGN * v for v in r[1:]]
    raise KeyError(case)


def hand_inplane(Fx, Fz, My_ref):
    """C3's hand formula restricted to the in-plane components (same footprint x 0 ... recess end, b 0.14 m)."""
    b = B_REF
    L = GEO["x_rec1"]
    x_ref = GEO["x0"] + gv("pod.size_m")[0] / 2
    Myc = My_ref - (x_ref - L / 2) * Fz
    A, Iy = b * L, b * L ** 3 / 12
    sig = max(Fz, 0) / A + abs(Myc) * (L / 2) / Iy
    tau = abs(Fx) / A
    return sig, tau, sig / ALLOW["xps_t"] + tau / ALLOW["xps_s"]


def m1_post(levels):
    """Load combinations per level: C1 design row (in-plane part), crash +z / -z / +-x, overhang."""
    case, F = c1_design_row()
    Fx, Fz, My = F[0], F[2], F[4]
    x_ref = GEO["x0"] + gv("pod.size_m")[0] / 2
    zb, zf = GEO["zb"], GEO["zf"]
    m_grp = sum(m for _, m, _, _ in GROUP) + PACK_MAX
    xcg = (sum(m * x for _, m, x, _ in GROUP) + PACK_MAX * PACK_X_FWD) / m_grp
    zcg = (sum(m * z for _, m, _, z in GROUP) + PACK_MAX * node("CL-D2-PACK-Z")) / m_grp
    Fc = m_grp * N_CRASH * G0
    out = {"design_case": case, "design_inplane_N_Nm": [Fx, Fz, My], "group_mass_kg": m_grp,
           "group_cg_xz_m": [xcg, zcg], "crash_F_N": Fc, "levels": []}

    def coeffs_for(Fx_, Fz_, My_ref_, xc):
        # unit cases act on the floor top (z = zf); My about C1's point (x_ref, zb)
        return {"U_FX": Fx_, "U_FZ": Fz_, "U_MY": My_ref_ - (zf - zb) * Fx_ + (xc - x_ref) * Fz_}

    for lev in levels:
        cs, xc = lev["cases"], lev["xc_seg"]
        row = {"h_m": lev["h_m"], "n_elem": lev["n_elem"]}
        base, sn, tau, _, _ = m1_combine(cs, coeffs_for(Fx, Fz, My, xc))
        row["design"] = bond_metrics(base, sn, tau)
        if lev is levels[-1]:
            out["profile_design"] = {"x": base[:, 0].tolist(), "z": base[:, 1].tolist(), "sigma": sn.tolist(),
                                     "tau": tau.tolist()}
        base, sn, tau, top, bot = m1_combine(cs, {"CRASH_UP": 1.0})
        row["crash_up"] = bond_metrics(base, sn, tau)
        if lev is levels[-1]:
            out["profile_crash_up"] = {"x": base[:, 0].tolist(), "sigma": sn.tolist(), "tau": tau.tolist()}
        base, sn, tau, top, bot = m1_combine(cs, {"CRASH_DN": 1.0})
        row["crash_dn"] = bond_metrics(base, sn, tau)
        row["overhang_crash_top_pa"] = abs(top)
        row["overhang_crash_bot_pa"] = abs(bot)
        row["overhang_design_top_pa"] = abs(top) * N_DESIGN_OVH / N_CRASH
        for sgn, nm in ((1, "crash_px"), (-1, "crash_mx")):
            base, sn, tau, _, _ = m1_combine(cs, coeffs_for(sgn * Fc, 0.0, sgn * Fc * (zcg - zb), xc))
            row[nm] = bond_metrics(base, sn, tau)
        if "F_saddle_N" in next(iter(cs.values())):
            # force the walls put into the handle feet through the brackets (real N): design row and limit (/ K_DESIGN)
            def sad(coeffs):
                return [float(sum(c * cs[k]["F_saddle_N"][i] for k, c in coeffs.items())) for i in (0, 1)]
            row["F_saddle_design_N"] = sad(coeffs_for(Fx, Fz, My, xc))
            row["F_saddle_limit_N"] = [f / K_DESIGN for f in row["F_saddle_design_N"]]
            row["F_saddle_crash_dn_N"] = sad({"CRASH_DN": 1.0})
            row["F_saddle_crash_up_N"] = sad({"CRASH_UP": 1.0})
            for sgn, nm in ((1, "px"), (-1, "mx")):
                row["F_saddle_crash_%s_N" % nm] = sad(coeffs_for(sgn * Fc, 0.0, sgn * Fc * (zcg - zb), xc))
        if "interface_ff" in next(iter(cs.values())):
            # floor-end-on-fillet bond (board paper face): R = peel / board flat-wise + |tau| / paper shear (C6 nodes)
            def ff(coeffs):
                b_ = np.array(cs[next(iter(coeffs))]["interface_ff"])
                sn_ = sum(c * np.array(cs[k]["interface_ff"])[:, 3] for k, c in coeffs.items())
                tau_ = sum(c * np.array(cs[k]["interface_ff"])[:, 4] for k, c in coeffs.items())
                Rf = np.maximum(sn_, 0) / ALLOW["board_flat"] + np.abs(tau_) / ALLOW["paper_s"]
                s_ = np.cumsum(b_[:, 2]) - b_[:, 2] / 2
                i_ = int(np.argmax(Rf))
                # the bevel is a cut through the board: the epoxy wets the polystyrene core (paper only at its two
                # 0.1 mm edges), so the failure plane is core foam: foam allowables (ASM-D2-XPS-ALLOW tension,
                # CL-C3-ALLOW-XPS-SHEAR shear), not the paper-to-core flat-wise value that governs intact faces
                Rc = np.maximum(sn_, 0) / ALLOW["xps_t"] + np.abs(tau_) / ALLOW["xps_s"]
                return {"R_peak_d0": window_avg(s_, Rf, b_[:, 2], D0), "R_peak_raw": float(Rf.max()),
                        "Rcore_peak_d0": window_avg(s_, Rc, b_[:, 2], D0),
                        "Rcore_peak_5mm": window_avg(s_, Rc, b_[:, 2], 0.005),
                        "Rcore_mean": float((Rc * b_[:, 2]).sum() / b_[:, 2].sum()),
                        "R_peak_5mm": window_avg(s_, Rf, b_[:, 2], 0.005),
                        "R_mean": float((Rf * b_[:, 2]).sum() / b_[:, 2].sum()),
                        "sigma_peak_d0": window_avg(s_, sn_, b_[:, 2], D0),
                        "xz_R_peak": [float(b_[i_, 0]), float(b_[i_, 1])]}
            row["ff_design"] = ff(coeffs_for(Fx, Fz, My, xc))
            row["ff_crash_up"] = ff({"CRASH_UP": 1.0})
            row["ff_crash_dn"] = ff({"CRASH_DN": 1.0})
            for sgn, nm in ((1, "crash_px"), (-1, "crash_mx")):
                row["ff_" + nm] = ff(coeffs_for(sgn * Fc, 0.0, sgn * Fc * (zcg - zb), xc))
        row["equilibrium_err"] = max(abs(c["F_interface_N"][i] - c["F_applied_N"][i]) / max(1.0, max(map(abs, c["F_applied_N"])))
                                     for c in cs.values() for i in (0, 1))
        out["levels"].append(row)
    # hand calcs on the same in-plane resultants
    hs = hand_inplane(Fx, Fz, My)
    out["hand_design_inplane"] = {"sigma": hs[0], "tau": hs[1], "R": hs[2]}
    # crash +z resultant at the group CG about C1's point: Fz = Fc, My = -(xcg - x_ref) Fc
    hc = hand_inplane(0.0, Fc, -(xcg - x_ref) * Fc)
    out["hand_crash_up_inplane"] = {"sigma": hc[0], "tau": hc[1], "R": hc[2]}
    for sgn, nm in ((1, "crash_px"), (-1, "crash_mx")):
        hx = hand_inplane(sgn * Fc, 0.0, sgn * Fc * (zcg - zb))
        out["hand_" + nm] = {"sigma": hx[0], "tau": hx[1], "R": hx[2]}
    return out


# ============================================================================ M2: pack stops
def m2_variants():
    zt = GEO["zt"]
    pad = lv("pad_t_m")
    aft_h = GEO["z_as_top"] - zt
    fs_t, fs_h, _ = lv("fwd_stop_m")
    win = lv("window_border_m")[0]
    return {
        # name: (stop t, stop h above tray, load z0, z1 above tray, tray ahead, tray behind, xps under?, fillet r)
        "AFT_SHARP_WIN": dict(t=lv("aft_stop_m")[0], h=aft_h, z0=pad, z1=aft_h, ahead=win, behind=0.065 - 0.063,
                              xps=True, r=0.0, F=None),
        "AFT_FILLET_WIN": dict(t=lv("aft_stop_m")[0], h=aft_h, z0=pad, z1=aft_h, ahead=win, behind=0.002, xps=True,
                               r=0.002, F=None),
        "AFT_FILLET_SOLID": dict(t=lv("aft_stop_m")[0], h=aft_h, z0=pad, z1=aft_h, ahead=0.060 - 0.0345,
                                 behind=0.002, xps=True, r=0.002, F=None),
        # C3 fix candidate: 2 mm PETG heel printed on the tray rear piece, x 0.040 ... 0.065 (no window there), under
        # the stop; the pack (on 2.5 mm pads) clears it by 0.5 mm, so the stop root rises 2 mm and its top stays put
        "AFT_HEEL_FILLET": dict(t=lv("aft_stop_m")[0], h=aft_h - 0.002, z0=pad - 0.002, z1=aft_h - 0.002, ahead=0.020,
                                behind=0.002, xps=True, r=0.002, tt=lv("tray_floor_t_m") + 0.002, F=None),
        # C3 fix candidate: back the aft stop with a printed strut to the handle foot bridge (x 0.077, on the spar):
        # the strut bears on the stop back face from the bridge underside to its top, z 0.026 ... 0.040 (CR-C3-14)
        "AFT_PROPPED_WIN": dict(t=lv("aft_stop_m")[0], h=aft_h, z0=pad, z1=aft_h, ahead=win, behind=0.002, xps=True,
                                r=0.002, prop=(0.026 - zt, 0.040 - zt), F=None),
        "FWD_FILLET": dict(t=fs_t, h=fs_h, z0=0.002, z1=fs_h, ahead=lv("tray_front_solid_m") - fs_t, behind=0.0,
                           xps=False, r=0.002, F=None),
        # as built (CR-D2-11c, D2-R5): the forward stop's fore face bonded to the 4.8 mm board nose wall with the 1 mm
        # epoxy bed; the wall stands on the floor end (butt bond) and is free at the top (hatch and side walls left out:
        # conservative in 2-D); floor underside held (the overhang is checked in M1)
        "FWD_BEDDED": dict(t=fs_t, h=fs_h, z0=0.002, z1=fs_h, ahead=lv("tray_front_solid_m") - fs_t, behind=0.0,
                           xps=False, r=0.002, wall=lv("nose_block_l_m"), F=None),
    }


M2X = ("FWD_BEDDED",)                           # added in C3-R3: run as part "m2x", merged into M2 by combine()


def m2f_variants():
    """C3-R4 (2026-11-13): the D2-R6 forward-stop T as drawn (D-69, CR-C3-15; subsystems/pod/fusion/pod.py layout()
    fs_flange, BUILD.md steps 6 and 9). Upright fwd_stop_m[0] thick from the flange foot to fwd_stop_m[1] above the
    tray, through the floor notch; flange fwd_stop_flange_m (length from the fore face x thickness) under the floor,
    epoxied to the floor underside and the upright epoxied to the notch edge (floor end face). The tray front piece
    starts at the upright's aft face; it is NOT credited as bonded to the upright (0.2 mm gap): the pack pushes the
    upright away from it. The nose wall and its 1 mm bed are NOT credited (the wall stands on the floor only outside
    the notch, |y| > fwd_stop_m[2]/2, which a y = 0 plane-strain section cannot carry): conservative.
    BCs (the floor here is part of the nose box, which a 2-D strip cannot carry, so two bounds): HELD = floor
    underside held aft of the flange (the C3-R3 M2 rule): the whole stop force crosses the core in shear within
    ~36 mm, which over-states core shear and peel at the hold edge; BOX = the floor strip's aft end section clamped
    30 mm behind the tray front piece and its underside free: the force stays in the paper faces as membrane and the
    root moment bends the floor strip alone (no side walls, no nose wall), which over-states the floor curvature next
    to the stop. Local checks at the T take the worse of the two."""
    fs_t, fs_h, _ = lv("fwd_stop_m")
    fl_l, fl_t = lv("fwd_stop_flange_m")
    base = dict(t=fs_t, h=fs_h, z0=0.002, z1=fs_h, ahead=lv("tray_front_solid_m") - fs_t, behind=0.0, xps=False,
                r=0.0, flange=(fl_l, fl_t), tray_gap=0.0002, F=None)
    # C3-R4 fix (if the as-drawn T peels the floor's top face at the tray/upright notch): epoxy the tray front piece's
    # front edge to the upright and run a thickened-epoxy fillet (leg r) along the upright foot on the pack side
    fix = dict(base, tray_gap=0.0, r=lv("fwd_stop_fillet_m") if "fwd_stop_fillet_m" in LOC else 0.002)
    # As built (BUILD.md step 9): the 1 mm microballoon bed fills the gap to the nose wall "so the wall backs the
    # stop"; the wall's foot is held (in 3-D it stands on the floor outside the 54 mm notch and the side walls hold its
    # edges). The tray stays un-credited at the upright (0.2 mm gap).
    return {"FWD_FLANGE_HELD": dict(base, hold="aft_of_flange"),
            "FWD_FLANGE_BOX": dict(base, hold="box"),
            "FWD_FLANGE_BED_HELD": dict(base, hold="aft_of_flange", bed=True),
            "FWD_FLANGE_BED_BOX": dict(base, hold="box", bed=True)}
    _unused = fix                                # the tray-bond + fillet option (studied 2026-11-13, not adopted)


def m2f_mesh(gmsh, v, h):
    """Local frame as m2_mesh: s toward the load (the nose), upright aft face at s = 0, fore face s = t; z from the
    tray top. Regions: tray (PETG) s in [-ahead, -gap]; board faces + core s in [s0 - 0.015, 0]; upright (PETG)
    s in [0, t] from the flange bottom to h; flange (PETG) s in [t - fl_l, t] under the board."""
    o = gmsh.model.occ
    gmsh.model.add("m2f")
    tf, tb = MAT["t_face"], TB
    tt = lv("tray_floor_t_m")
    t, hh = v["t"], v["h"]
    fl_l, fl_t = v["flange"]
    zf = -tt
    zc = zf - tb
    zfl = zc - fl_t
    s_tray0 = -v["ahead"]
    b0 = s_tray0 - 0.030
    layers = [("face", o.addRectangle(b0, zc, 0, -b0, tf)), ("core", o.addRectangle(b0, zc + tf, 0, -b0, tb - 2 * tf)),
              ("face", o.addRectangle(b0, zf - tf, 0, -b0, tf))]
    tray = o.addRectangle(s_tray0, zf, 0, -v["tray_gap"] - s_tray0, tt)
    r = v.get("r", 0.0)
    cuts = sorted({zfl, zc, zf, 0.0, v["z0"], hh} | ({r} if r > 0 else set()))
    up = [o.addRectangle(0.0, a, 0, t, b - a) for a, b in zip(cuts[:-1], cuts[1:]) if b - a > 1e-9]
    flange = o.addRectangle(t - fl_l, zfl, 0, fl_l - t, fl_t)        # aft of the upright (the upright owns s 0..t)
    petg = [(2, tray)] + [(2, u) for u in up] + [(2, flange)]
    all_in = [(2, t_) for _, t_ in layers] + petg
    kinds = [k for k, _ in layers] + ["petg"] * len(petg)
    sw0 = None
    if v.get("bed"):                             # BUILD step 9: 1 mm microballoon bed, T fore face -> nose wall
        bed = lv("nose_block_l_m")
        sw0 = t + bed
        hw = GEO["zh"] - GEO["zb"]
        all_in += [(2, o.addRectangle(t, zc, 0, bed, hh - zc)),
                   (2, o.addRectangle(sw0, zc, 0, tf, hw)), (2, o.addRectangle(sw0 + tf, zc, 0, tb - 2 * tf, hw)),
                   (2, o.addRectangle(sw0 + tb - tf, zc, 0, tf, hw))]
        kinds += ["epoxy", "face", "core", "face"]
    if r > 0:                                    # concave epoxy fillet in the upright / tray-top corner (pack side)
        sq = o.addRectangle(-r, 0.0, 0, r, r)
        fil = o.cut([(2, sq)], [(2, o.addDisk(-r, r, 0, r, r))])[0]
        all_in += fil
        kinds += ["epoxy"] * len(fil)
    _, omap = o.fragment(all_in, [])
    o.synchronize()
    MID = {"petg": 0, "face": 1, "core": 2, "epoxy": 3}
    surf_mat = {}
    for k, ch in zip(kinds, omap):
        for _, tg in ch:
            surf_mat.setdefault(tg, MID[k])
    s_hold = t - fl_l
    load, bottom = [], []
    for _, cv in gmsh.model.getEntities(1):
        bb = gmsh.model.getBoundingBox(1, cv)
        if abs(bb[0]) < 2e-6 and abs(bb[3]) < 2e-6 and bb[1] >= v["z0"] - 2e-6 and bb[4] <= v["z1"] + 2e-6 \
                and bb[4] - bb[1] > 1e-6:
            load.append(cv)
        if sw0 is not None and abs(bb[1] - zc) < 2e-6 and abs(bb[4] - zc) < 2e-6 and bb[0] >= sw0 - 1e-7:
            bottom.append(cv)          # nose-wall foot: in 3-D it stands on the floor outside the notch (and the
            continue                   # side walls hold its edges); held here
        if v["hold"] == "box":
            if abs(bb[0] - b0) < 2e-6 and abs(bb[3] - b0) < 2e-6:          # aft end section of the floor strip
                bottom.append(cv)
        elif abs(bb[1] - zc) < 2e-6 and abs(bb[4] - zc) < 2e-6 and bb[3] <= s_hold + 1e-6:
            bottom.append(cv)
    if not load or not bottom:
        raise RuntimeError("M2F curve classification failed: load %s bottom %s" % (load, bottom))
    f = gmsh.model.mesh.field
    f.add("Box", 2)                              # upright foot, flange and the board around them
    f.setNumber(2, "VIn", h / 4)
    f.setNumber(2, "VOut", h * 4)
    f.setNumber(2, "XMin", t - fl_l - 0.002)
    f.setNumber(2, "XMax", t + 0.001)
    f.setNumber(2, "YMin", zfl - 0.0005)
    f.setNumber(2, "YMax", 0.6 * t + 0.002)
    f.setNumber(2, "Thickness", 0.004)
    f.add("Box", 3)                              # board faces along the tray
    f.setNumber(3, "VIn", h / 2)
    f.setNumber(3, "VOut", h * 4)
    f.setNumber(3, "XMin", s_tray0 - 0.002)
    f.setNumber(3, "XMax", t + 0.002)
    f.setNumber(3, "YMin", zc - 0.0005)
    f.setNumber(3, "YMax", 0.0004)
    f.add("Min", 4)
    f.setNumbers(4, "FieldsList", [2, 3])
    f.setAsBackgroundMesh(4)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.MeshSizeMax", h * 4)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.model.mesh.generate(2)
    xyz, tris, emat, idx = mesh_to_arrays(gmsh, surf_mat)
    mk = {"load": curve_edges(gmsh, idx, load), "bottom": curve_edges(gmsh, idx, bottom)}
    return xyz, tris, emat, mk, (zf, zc, zfl)


def _sec_lin(sig, cen, area, emat, h, axis, at, lo, hi):
    """Section-linearised bending + membrane stress across a PETG section: cut normal to `axis` (0: section at
    s = at, stress sxx; 1: section at z = at, stress szz) spanning lo..hi in the other coordinate."""
    o = 1 - axis
    band = (emat == 0) & (np.abs(cen[:, axis] - at) < h / 2) & (cen[:, o] > lo - 1e-9) & (cen[:, o] < hi + 1e-9)
    if band.sum() < 3:
        return 0.0
    d = hi - lo
    y = cen[band, o] - (lo + hi) / 2
    st = sig[band, 0 if axis == 0 else 1]
    M = float((st * y * area[band]).sum() / h)
    N = float((st * area[band]).sum() / h)
    return abs(6 * M / d ** 2) + abs(N / d)


def run_m2f(name, v, level_factor):
    """Forward-stop T (D2-R6) under the pack crash load: upright and flange section stresses, board flat-wise peel
    on both paper-face-to-core planes and flange-to-face bond tractions, 2 mm means (ASM-C3-FEA-D0)."""
    import gmsh
    h = v["t"] / 4 * level_factor * 2
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    try:
        xyz, tris, emat, markers, (zf, zc, zfl) = m2f_mesh(gmsh, v, h)
    finally:
        gmsh.finalize()
    mats = [(MAT["E_petg"], MAT["nu_petg"]), (MAT["E_face"], MAT["nu_board"]), (MAT["E_core"], MAT["nu_core"]),
            (MAT["E_epoxy"], MAT["nu_epoxy"])]
    b = lv("bay_min_m")[1] + 2 * lv("guide_t_m")
    F = m2_force("FWD")
    p = F / (b * (v["z1"] - v["z0"]))
    rd = RUNS / "M2F" / name / ("L%d" % LEVELS.index(level_factor))
    u, dt = run_su2(rd, xyz, tris, emat, mats, markers, ["bottom"], {"load": (p, 0.0)}, "PLANE_STRAIN")
    eps, sig, cen, area = tri_strain_stress(xyz, tris, emat, mats, u, "PLANE_STRAIN")
    t = v["t"]
    fl_l = v["flange"][0]
    # upright: section-linearised at 0.5 t above the tray top, at the board top and at mid-board; flange at 0.5 t aft
    # of the upright (its root)
    s_up = max(_sec_lin(sig, cen, area, emat, h, 1, zz, 0.0, t) for zz in (0.5 * t, zf - 0.5 * h, (zf + zc) / 2))
    s_fl = _sec_lin(sig, cen, area, emat, h, 0, -0.5 * t, zfl, zc)
    sxx, szz, sxz = sig[:, 0], sig[:, 1], sig[:, 2]
    s1 = (sxx + szz) / 2 + np.sqrt(((sxx - szz) / 2) ** 2 + sxz ** 2)
    petg = emat == 0
    peak = float(s1[petg].max())
    zone = (-v["ahead"] - 0.004, t + 0.004)
    it = interface_tractions(xyz, tris, emat, sig, {2}, {1})            # core side, normal out of the core
    it = it[(it[:, 0] > zone[0]) & (it[:, 0] < zone[1])]
    top = it[np.abs(it[:, 1] - (zf - MAT["t_face"])) < 1e-7]
    bot = it[np.abs(it[:, 1] - (zc + MAT["t_face"])) < 1e-7]
    peel_top = window_avg(top[:, 0], top[:, 3], top[:, 2], D0)
    peel_bot = window_avg(bot[:, 0], bot[:, 3], bot[:, 2], D0)
    sh_bot = window_avg(bot[:, 0], np.abs(bot[:, 4]), bot[:, 2], D0)
    sh_top = window_avg(top[:, 0], np.abs(top[:, 4]), top[:, 2], D0)
    fb = interface_tractions(xyz, tris, emat, sig, {0}, {1})            # flange (PETG) side of the flange-to-face bond
    fb = fb[(np.abs(fb[:, 1] - zc) < 1e-7) & (fb[:, 0] > t - fl_l - 1e-6)]   # flange-to-floor underside line
    bond_n = window_avg(fb[:, 0], fb[:, 3], fb[:, 2], D0) if len(fb) else 0.0
    bond_s = window_avg(fb[:, 0], np.abs(fb[:, 4]), fb[:, 2], D0) if len(fb) else 0.0
    rec = {"h_m": h, "n_elem": int(len(tris)), "F_N": F, "b_m": b, "p_pa": p, "su2_s": dt,
           "upright_lin_pa": s_up, "flange_lin_pa": s_fl, "peak_s1_pa": peak,
           "peel_top_d0_pa": peel_top, "peel_bot_d0_pa": peel_bot, "peel_peak_d0_pa": max(peel_top, peel_bot),
           "shear_bot_d0_pa": sh_bot, "shear_top_d0_pa": sh_top, "shear_peak_d0_pa": max(sh_bot, sh_top),
           "flange_bond_peel_d0_pa": bond_n, "flange_bond_shear_d0_pa": bond_s,
           "peel_peak_raw_pa": float(max(top[:, 3].max(), bot[:, 3].max())),
           "peel_top_at_s_m": float(top[int(np.argmax(top[:, 3])), 0]),
           "peel_bot_at_s_m": float(bot[int(np.argmax(bot[:, 3])), 0]),
           "u_tip_m": float(np.abs(u[:, 0]).max())}
    if v.get("bed"):
        sw0_ = t + lv("nose_block_l_m")
        bd = interface_tractions(xyz, tris, emat, sig, {3}, {0})          # bed (epoxy) side of the T fore face
        bd = bd[np.abs(bd[:, 0] - t) < 1e-7]
        fx = float((bd[:, 3] * bd[:, 5] * bd[:, 2]).sum())                # force the T pushes into the bed, N/m
        rec["bed_share"] = fx / (F / b)
        rec["bed_force_n"] = fx * b
        rec["bed_z_m"] = float((bd[:, 1] * np.abs(bd[:, 3]) * bd[:, 2]).sum() / max((np.abs(bd[:, 3]) * bd[:, 2]).sum(), 1e-12))
        rec["wall_foot_moment_nm"] = rec["bed_force_n"] * (rec["bed_z_m"] - zc)
        rec["bed_peel_d0_pa"] = window_avg(bd[:, 1], bd[:, 3], bd[:, 2], D0)   # tension across the bed (> 0)
        # nose wall: its inner paper face peeling off the core (vertical face-to-core plane behind the bed)
        wl = interface_tractions(xyz, tris, emat, sig, {2}, {1})
        wl = wl[np.abs(wl[:, 0] - (sw0_ + MAT["t_face"])) < 1e-7]
        rec["wall_peel_d0_pa"] = window_avg(wl[:, 1], wl[:, 3], wl[:, 2], D0)
        rec["wall_peel_at_z_m"] = float(wl[int(np.argmax(wl[:, 3])), 1])
        rec["wall_shear_d0_pa"] = window_avg(wl[:, 1], np.abs(wl[:, 4]), wl[:, 2], D0)
    (rd / "summary.json").write_text(json.dumps(rec, indent=1))
    print("  M2F %-19s L%d %6d el %5.1f s  upright %.2f  flange %.2f MPa  peel top %.1f (s %.1f mm) bot %.1f (s %.1f"
          " mm) kPa  core shear top %.1f bot %.1f kPa" % (
              name, LEVELS.index(level_factor), len(tris), dt, s_up / 1e6, s_fl / 1e6, peel_top / 1e3,
              rec["peel_top_at_s_m"] * 1e3, peel_bot / 1e3, rec["peel_bot_at_s_m"] * 1e3, sh_top / 1e3, sh_bot / 1e3),
          flush=True)
    return rec


def m2_mesh(gmsh, v, h):
    """Local frame: s along the tray toward the load direction (stop fore face at s = 0, pack side s < 0); z from the
    tray top. Layers: XPS (optional) | board (face, core, face) | tray | stop."""
    o = gmsh.model.occ
    gmsh.model.add("m2")
    tf, tb = MAT["t_face"], TB
    tt = v.get("tt", lv("tray_floor_t_m"))
    t, hh, r = v["t"], v["h"], v["r"]
    s0, s1 = -v["ahead"], t + v["behind"]
    board_s0, board_s1 = s0 - 0.015, s1 + (0.0 if v["behind"] > 0 else 0.0)
    if v["behind"] == 0:
        board_s1 = s1 + 0.005                      # floor continues past the tray front (nose wall line)
    bed = v.get("wall")
    sw0 = t + bed if bed else None                  # nose wall inner face
    if bed:
        board_s1 = sw0
    zf = 0.0 - tt
    layers = []
    zc = zf - tb
    if v["xps"]:
        layers.append(("xps", o.addRectangle(board_s0, zc - 0.010, 0, board_s1 - board_s0, 0.010)))
    layers.append(("face", o.addRectangle(board_s0, zc, 0, board_s1 - board_s0, tf)))
    layers.append(("core", o.addRectangle(board_s0, zc + tf, 0, board_s1 - board_s0, tb - 2 * tf)))
    layers.append(("face", o.addRectangle(board_s0, zf - tf, 0, board_s1 - board_s0, tf)))
    if bed:
        hw = GEO["zh"] - GEO["zb"]
        layers.append(("face", o.addRectangle(sw0, zc, 0, tf, hw)))
        layers.append(("core", o.addRectangle(sw0 + tf, zc, 0, tb - 2 * tf, hw)))
        layers.append(("face", o.addRectangle(sw0 + tb - tf, zc, 0, tf, hw)))
        layers.append(("epoxy", o.addRectangle(t, zf, 0, bed, hh - zf)))
    tray = o.addRectangle(s0, zf, 0, s1 - s0, tt)
    # stop split at the load start height so the loaded face is its own curve
    cuts = sorted({0.0, v["z0"], hh} | set(v.get("prop", ())))
    petg = [(2, tray)] + [(2, o.addRectangle(0.0, a, 0, t, b - a)) for a, b in zip(cuts[:-1], cuts[1:]) if b - a > 1e-9]
    if r > 0:
        fl = []
        for side in (-1, 1):
            if side == 1 and v["behind"] < r - 1e-9:
                continue
            sx = 0.0 if side == -1 else t
            sq = o.addRectangle(sx - r if side == -1 else sx, 0.0, 0, r, r)
            cx = sx - r if side == -1 else sx + r
            disk = o.addDisk(cx, r, 0, r, r)
            fl.append(o.cut([(2, sq)], [(2, disk)])[0][0])
        petg += fl
    petg_f = petg
    all_in = [(2, t_) for _, t_ in layers] + petg_f
    kinds = [k for k, _ in layers] + ["petg"] * len(petg_f)
    _, omap = o.fragment(all_in, [])
    o.synchronize()
    MID = {"petg": 0, "face": 1, "core": 2, "xps": 3, "epoxy": 4}
    surf_mat = {}
    for k, ch in zip(kinds, omap):
        for _, tg in ch:
            surf_mat.setdefault(tg, MID[k])
    load, bottom, prop = [], [], []
    pz = v.get("prop")
    zbot = (zc - 0.010) if v["xps"] else zc
    for _, cv in gmsh.model.getEntities(1):
        bb = gmsh.model.getBoundingBox(1, cv)
        if abs(bb[0]) < 2e-6 and abs(bb[3]) < 2e-6 and bb[1] >= v["z0"] - 2e-6 and bb[4] <= v["z1"] + 2e-6 \
                and bb[4] - bb[1] > 1e-6:
            load.append(cv)
        if abs(bb[1] - zbot) < 2e-6 and abs(bb[4] - zbot) < 2e-6 and (not bed or bb[3] <= sw0 + 1e-6):
            bottom.append(cv)
        if pz and abs(bb[0] - t) < 2e-6 and abs(bb[3] - t) < 2e-6 and bb[1] >= pz[0] - 2e-6 and bb[4] <= pz[1] + 2e-6:
            prop.append(cv)
    if not load or not bottom:
        raise RuntimeError("M2 curve classification failed: load %s bottom %s; vertical curves at s=0: %s" % (load, bottom, [gmsh.model.getBoundingBox(1, c) for _, c in gmsh.model.getEntities(1) if abs(gmsh.model.getBoundingBox(1, c)[0]) < 1e-6]))
    f = gmsh.model.mesh.field
    f.add("Box", 2)                              # stop root zone, both corners and the fillets
    f.setNumber(2, "VIn", h / 4)
    f.setNumber(2, "VOut", h * 4)
    f.setNumber(2, "XMin", -max(r, 0.0005) - 0.001)
    f.setNumber(2, "XMax", t + max(r, 0.0005) + 0.001)
    f.setNumber(2, "YMin", zf - 0.0005)
    f.setNumber(2, "YMax", max(r, 0.0005) + 0.6 * t)
    f.setNumber(2, "Thickness", 0.004)
    f.add("Box", 3)                              # tray / board interface band along the whole tray
    f.setNumber(3, "VIn", h / 2)
    f.setNumber(3, "VOut", h * 4)
    f.setNumber(3, "XMin", s0 - 0.002)
    f.setNumber(3, "XMax", s1 + 0.002)
    f.setNumber(3, "YMin", zf - 0.0012)
    f.setNumber(3, "YMax", 0.0004)
    f.add("Min", 4)
    f.setNumbers(4, "FieldsList", [2, 3])
    f.setAsBackgroundMesh(4)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.MeshSizeMax", h * 4)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.model.mesh.generate(2)
    xyz, tris, emat, idx = mesh_to_arrays(gmsh, surf_mat)
    mk = {"load": curve_edges(gmsh, idx, load), "bottom": curve_edges(gmsh, idx, bottom)}
    if pz:
        if not prop:
            raise RuntimeError("M2 prop face not found")
        mk["prop"] = curve_edges(gmsh, idx, prop)
    return xyz, tris, emat, mk, zf, sw0


def m2_force(name):
    st = node("CALC-C3-STOPS")
    return st["F_aft_n"] if name.startswith("AFT") else st["F_fwd_n"]


def run_m2(name, v, level_factor):
    import gmsh
    h = v["t"] / 4 * level_factor * 2          # L0: t/2 at the root ... L3: t/16
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    try:
        xyz, tris, emat, markers, zf, sw0 = m2_mesh(gmsh, v, h)
    finally:
        gmsh.finalize()
    mats = [(MAT["E_petg"], MAT["nu_petg"]), (MAT["E_face"], MAT["nu_board"]), (MAT["E_core"], MAT["nu_core"]),
            (MAT["E_xps"], MAT["nu_xps"]), (MAT["E_epoxy"], MAT["nu_epoxy"])]
    b = lv("bay_min_m")[1] + 2 * lv("guide_t_m")
    F = m2_force(name)
    p = F / (b * (v["z1"] - v["z0"]))
    rd = RUNS / "M2" / name / ("L%d" % LEVELS.index(level_factor))
    u, dt = run_su2(rd, xyz, tris, emat, mats, markers, [m for m in ("bottom", "prop") if m in markers],
                    {"load": (p, 0.0)}, "PLANE_STRAIN")
    eps, sig, cen, area = tri_strain_stress(xyz, tris, emat, mats, u, "PLANE_STRAIN")
    t = v["t"]
    # section-linearised root stress (equilibrium) at z = r + 0.5 t above the tray top (clear of the fillet)
    zs = v["r"] + 0.5 * t
    band = (emat == 0) & (np.abs(cen[:, 1] - zs) < h / 2) & (cen[:, 0] > -1e-9) & (cen[:, 0] < t + 1e-9)
    s_ = cen[band, 0] - t / 2
    M = float((sig[band, 1] * s_ * area[band]).sum() / (h))   # per unit depth, band height h
    N = float((sig[band, 1] * area[band]).sum() / h)
    sig_lin = abs(6 * M / t ** 2) + abs(N / t)
    M_exact = F / b * ((v["z0"] + v["z1"]) / 2 - zs)
    # peak max principal stress in the PETG near the root (fillet or sharp corner)
    sxx, szz, sxz = sig[:, 0], sig[:, 1], sig[:, 2]
    s1 = (sxx + szz) / 2 + np.sqrt(((sxx - szz) / 2) ** 2 + sxz ** 2)
    root = (emat == 0) & (cen[:, 1] < v["r"] + 0.6 * t) & (cen[:, 1] > -1e-9)
    peak = float(s1[root].max())
    trayel = (emat == 0) & (cen[:, 1] < 0)
    tray_peak = float(np.abs(sxx[trayel]).max())     # tray bending along the raster (tray printed flat)
    s_tray = cen[trayel, 0][int(np.argmax(np.abs(sxx[trayel])))]
    # board flat-wise peel: paper face to core (core side, normal up out of the core), the C6 50 kPa failure plane
    ztf = zf - MAT["t_face"]
    it = interface_tractions(xyz, tris, emat, sig, {2}, {1})
    it = it[(np.abs(it[:, 1] - ztf) < 1e-7) & (it[:, 0] > -v["ahead"] - 0.004) & (it[:, 0] < t + v["behind"] + 0.004)]
    peel = it[:, 3]                                 # traction on the core, normal out of the core: tension > 0
    # tray-to-face epoxy line (tray side) for reference
    it2 = interface_tractions(xyz, tris, emat, sig, {0}, {1})
    it2 = it2[np.abs(it2[:, 1] - zf) < 1e-7]
    rec = {"h_m": h, "n_elem": int(len(tris)), "F_N": F, "b_m": b, "p_pa": p, "su2_s": dt,
           "sigma_lin_pa": sig_lin, "sigma_lin_exact_pa": 6 * M_exact / t ** 2, "M_fea_Nm_per_m": M,
           "M_exact_Nm_per_m": M_exact, "peak_s1_pa": peak, "tray_peak_pa": tray_peak, "tray_peak_s_m": float(s_tray),
           "peel_peak_raw_pa": float(peel.max()), "peel_peak_d0_pa": window_avg(it[:, 0], peel, it[:, 2], D0),
           "peel_tray_line_d0_pa": window_avg(it2[:, 0], it2[:, 3], it2[:, 2], D0),
           "shear_peak_d0_pa": window_avg(it[:, 0], np.abs(it[:, 4]), it[:, 2], D0),
           "profile": {"s": it[:, 0].tolist(), "peel": peel.tolist(), "tau": it[:, 4].tolist()}}
    if sw0 is not None:
        wf = (emat == 1) & (cen[:, 0] > sw0 - 1e-9)                      # nose wall paper faces (vertical)
        rec["wall_face_peak_pa"] = float(np.abs(szz[wf]).max())
        bd = emat == 4                                                  # epoxy bed: normal stress across it (s)
        rec["bed_peel_peak_pa"] = float(max(sxx[bd].max(), 0.0))
        rec["bed_comp_mean_pa"] = float(-(sxx[bd] * area[bd]).sum() / area[bd].sum())
        # wall-to-floor butt joint: shear along the joint line (floor end), wall side
        # share of the stop load that reaches the floor through the tray (the rest goes through the bed into the wall)
        ft = nodal_interface_force(xyz, tris, emat, sig, area, {0}, {1})
        rec["tray_path_share"] = float(abs(ft[0]) / (F / b))
    (rd / "summary.json").write_text(json.dumps({k: v_ for k, v_ in rec.items() if k != "profile"}, indent=1))
    print("  M2 %-17s L%d %6d el %5.1f s  lin %.2f MPa (exact %.2f)  stop peak %.2f  tray peak %.2f MPa  peel %.0f "
          "kPa (raw %.0f)" % (name, LEVELS.index(level_factor), len(tris), dt, sig_lin / 1e6,
                              rec["sigma_lin_exact_pa"] / 1e6, peak / 1e6, tray_peak / 1e6,
                              rec["peel_peak_d0_pa"] / 1e3, rec["peel_peak_raw_pa"] / 1e3), flush=True)
    return rec


# ============================================================================ benchmark
def benchmark():
    """Cantilever, two materials, plane stress: SU2 + this post-processing vs Timoshenko beam (tip, root stress)."""
    import gmsh
    out = []
    for lf in LEVELS:
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        o = gmsh.model.occ
        gmsh.model.add("bm")
        L, H = 0.10, 0.01
        a = o.addRectangle(0, 0, 0, L / 2, H)
        b_ = o.addRectangle(L / 2, 0, 0, L / 2, H)
        _, om = o.fragment([(2, a), (2, b_)], [])
        o.synchronize()
        sm = {om[0][0][1]: 0, om[1][0][1]: 1}
        lc, rc = [], []
        for _, cv in gmsh.model.getEntities(1):
            bb = gmsh.model.getBoundingBox(1, cv)
            if bb[3] < 2e-6:
                lc.append(cv)
            if bb[0] > L - 2e-6:
                rc.append(cv)
        h = 0.002 * lf
        gmsh.option.setNumber("Mesh.MeshSizeMax", h)
        gmsh.model.mesh.generate(2)
        xyz, tris, emat, idx = mesh_to_arrays(gmsh, sm)
        mk = {"left": curve_edges(gmsh, idx, lc), "right": curve_edges(gmsh, idx, rc)}
        gmsh.finalize()
        E1, E2, nu, q = 2.0e9, 4.0e9, 0.3, 1000.0
        u, dt = run_su2(RUNS / "BENCH" / ("L%d" % LEVELS.index(lf)), xyz, tris, emat, [(E1, nu), (E2, nu)], mk,
                        ["left"], {"right": (0.0, -q)}, "PLANE_STRESS")
        P = q * H
        I = H ** 3 / 12
        # tip deflection: two-segment Euler-Bernoulli + shear
        a_ = L / 2
        def defl(E1, E2):
            # unit-load method: integrate M m / EI over both halves
            x = np.linspace(0, L, 20001)
            Ex = np.where(x < a_, E1, E2)
            M = P * (L - x)
            Gx = Ex / (2 * (1 + nu))
            return np.trapezoid(M * (L - x) / (Ex * I), x) + np.trapezoid(P / (5 / 6 * H * Gx), x)
        tip = float(np.mean(u[np.abs(xyz[:, 0] - L) < 1e-9, 1]))
        eps, sig, cen, area = tri_strain_stress(xyz, tris, emat, [(E1, nu), (E2, nu)], u, "PLANE_STRESS")
        band = np.abs(cen[:, 0] - 0.03) < h
        A = np.vstack([np.ones(band.sum()), cen[band, 1] - H / 2]).T
        c = np.linalg.lstsq(A, sig[band, 0], rcond=None)[0]
        out.append({"h_m": h, "n_elem": int(len(tris)), "tip_fea_m": -tip, "tip_beam_m": defl(E1, E2),
                    "sigma_top_x30_fea_pa": float(c[0] + c[1] * H / 2), "sigma_top_x30_beam_pa": P * (L - 0.03) * (H / 2) / I})
        print("  BENCH L%d tip %.4e vs %.4e  sigma %.0f vs %.0f" % (LEVELS.index(lf), out[-1]["tip_fea_m"], out[-1]["tip_beam_m"],
              out[-1]["sigma_top_x30_fea_pa"], out[-1]["sigma_top_x30_beam_pa"]), flush=True)
    return out


# ============================================================================ main
def conv_table(hs, qs):
    hs, qs = list(hs), list(qs)
    order = np.argsort(hs)
    hs, qs = [hs[i] for i in order], [qs[i] for i in order]
    return dict(richardson(hs, qs), h=hs, q=qs)


def _inputs():
    return {"materials": MAT, "allowables": ALLOW, "d0_m": D0, "k_design": K_DESIGN, "n_crash": N_CRASH,
            "n_design_overhang": N_DESIGN_OVH, "b_ref_m": B_REF, "airfoil": AIRFOIL_SRC,
            "group_items": [[i, m, x, z] for i, m, x, z in GROUP], "pack_max_kg": PACK_MAX,
            "pack_x_fwd_m": PACK_X_FWD, "spar_mounted_excluded": sorted(SPAR_MOUNTED),
            "geometry": {k: GEO[k] for k in ("x0", "xn", "x1", "x_rec0", "x_rec1", "zb", "zf", "zt", "zp", "zh",
                                             "x_as", "z_as_top", "x_fs0", "x_fs")},
            "solver": "SU2 v8.5.0 ELASTICITY, linear elastic, small deformations, P1 triangles, CG + ILU(3), relative residual 1e-10",
            "mesher": "gmsh (Python API) Frontal-Delaunay, size fields at the bond line / stop root"}


def run_part(name):
    """One independent part of the campaign (the parts can run in parallel processes): bench, m1f, m1b, m2."""
    t0 = time.time()
    if name == "bench":
        out = benchmark()
    elif name in ("m1f", "m1b"):
        bonded = name == "m1b"
        print("%s pod on the wing:" % ("M1_BONDED" if bonded else "M1_FOOTPRINT"), flush=True)
        out = m1_variant([run_m1(f, bonded) for f in LEVELS])
    elif name in ("m1t", "m1tf", "m1tg"):
        print("%s pod on the wing (3 levels):" % PARTS_X[name], flush=True)
        lv3 = [run_m1(f, name == "m1t", tied=True, stepgap=name == "m1tg") for f in LEVELS[:3]]
        out = m1_variant(lv3)
        out["F_saddle_N"] = {c: lv3[-1]["cases"][c]["F_saddle_N"] for c in lv3[-1]["cases"]}
    elif name in ("m2", "m2x"):
        out = {}
        for nm, v in m2_variants().items():
            if (nm in M2X) != (name == "m2x"):
                continue
            recs = [run_m2(nm, v, f) for f in LEVELS]
            hs = [r["h_m"] for r in recs]
            out[nm] = {"variant": {k: v.get(k) for k in ("t", "h", "z0", "z1", "ahead", "behind", "xps", "r", "tt")},
                       "levels": [{k: r[k] for k in r if k != "profile"} for r in recs],
                       "profile_finest": recs[-1]["profile"],
                       "convergence": {k: conv_table(hs, [r[k] for r in recs])
                                       for k in ("sigma_lin_pa", "peak_s1_pa", "tray_peak_pa", "peel_peak_d0_pa",
                                                 "peel_peak_raw_pa", "wall_face_peak_pa", "bed_peel_peak_pa",
                                                 "tray_path_share") if k in recs[0]}}
    elif name == "m2f":
        out = {}
        for nm, v in m2f_variants().items():
            recs = [run_m2f(nm, v, f) for f in LEVELS]
            hs = [r["h_m"] for r in recs]
            out[nm] = {"variant": {k: v.get(k) for k in ("t", "h", "z0", "z1", "ahead", "flange", "tray_gap", "hold")},
                       "levels": recs,
                       "convergence": {k: conv_table(hs, [r[k] for r in recs])
                                       for k in ("upright_lin_pa", "flange_lin_pa", "peak_s1_pa", "peel_top_d0_pa",
                                                 "peel_bot_d0_pa", "peel_peak_d0_pa", "shear_peak_d0_pa",
                                                 "flange_bond_peel_d0_pa",
                                                 "flange_bond_shear_d0_pa", "bed_share", "wall_foot_moment_nm",
                                                 "bed_peel_d0_pa", "wall_peel_d0_pa", "wall_shear_d0_pa")
                                       if k in recs[0]}}
    elif name in ("m1tfl", "m1tfl1", "m1tflh", "m1tfl10", "m1tfl15"):
        soft, heel = name == "m1tfl1", name == "m1tflh"
        global SCARF_X
        if name in ("m1tfl10", "m1tfl15"):
            SCARF_X = 0.010 if name == "m1tfl10" else 0.015
        print("%s (3 levels):" % PARTS_X[name], flush=True)
        lv3 = [run_m1(f, False, tied=True, fillet=True, fillet_soft=soft, heel=heel) for f in LEVELS[:3]]
        out = m1_variant(lv3)
        out["F_saddle_N"] = {c: lv3[-1]["cases"][c]["F_saddle_N"] for c in lv3[-1]["cases"]}
    else:
        raise SystemExit("unknown part " + name)
    (OUT / "parts").mkdir(parents=True, exist_ok=True)
    (OUT / "parts" / (name + ".json")).write_text(json.dumps({"wall_s": time.time() - t0, "result": out},
                                                             default=float) + "\n", encoding="utf-8")
    print("part %s done (%.0f s)" % (name, time.time() - t0), flush=True)


PARTS = {"bench": "benchmark", "m1f": "M1_FOOTPRINT", "m1b": "M1_BONDED", "m2": "M2"}
# C3-R3 fix studies (3 levels each): handle feet tied to the pod walls (with / without the wall-edge bonds), and the
# same with the floor end face released from the recess step
PARTS_X = {"m1t": "M1_TIED", "m1tf": "M1_TIED_FOOTPRINT", "m1tg": "M1_TIED_STEPGAP", "m2x": "M2 (FWD_BEDDED)",
           # C3-R4 (2026-11-13): the drawn D2-R6 / D-69 fixes: recess-step fillet (CR-C3-17) with the feet tied and no
           # wall-edge credit, its soft-fill sensitivity, and the forward-stop T with its flange (CR-C3-15)
           "m1tfl": "M1_TIED_FILLET", "m1tfl1": "M1_TIED_FILLET_SOFT", "m1tflh": "M1_TIED_FILLET_CHORD",
           "m1tfl10": "M1_TIED_SCARF10", "m1tfl15": "M1_TIED_SCARF15", "m2f": "M2F"}


def combine():
    res = {"_note": "GENERATED by redesign/team/C3/pod_fea.py; do not edit. SI units. See SIMULATION-REPORT.md.",
           "inputs": _inputs(), "wall_s": {}}
    for part, key in PARTS.items():
        d = _load(OUT / "parts" / (part + ".json"))
        res[key] = d["result"]
        res["wall_s"][part] = d["wall_s"]
    for part, key in PARTS_X.items():
        if not part.startswith("m1"):
            continue
        pt = OUT / "parts" / (part + ".json")
        if pt.exists():
            d = _load(pt)
            res[key] = d["result"]
            res["wall_s"][part] = d["wall_s"]
    pf = OUT / "parts" / "m2f.json"
    if pf.exists():
        d = _load(pf)
        res["M2F"] = d["result"]
        res["wall_s"]["m2f"] = d["wall_s"]
    px = OUT / "parts" / "m2x.json"
    if px.exists():
        d = _load(px)
        res["M2"].update(d["result"])
        res["wall_s"]["m2x"] = d["wall_s"]
    # keep the results file small: drop the raw interface rows of every level (profiles of the finest mesh stay)
    for key in ("M1_FOOTPRINT", "M1_BONDED"):
        res[key].pop("raw", None)
    (OUT / "fea_results.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")
    print("wrote %s" % (OUT / "fea_results.json"))
    import pod_fea_plots
    pod_fea_plots.draw(res, OUT)


def main():
    OUT.mkdir(exist_ok=True)
    for part in list(PARTS) + list(PARTS_X):
        run_part(part)
    combine()


def m1_variant(lv_):
    m1 = m1_post(lv_)
    hs = [r["h_m"] for r in m1["levels"]]
    m1["convergence"] = {}
    for key, get in {"design_R_d0": lambda r: r["design"]["R_peak_d0"],
                     "design_sigma_d0": lambda r: r["design"]["sigma_peak_d0"],
                     "design_sigma_raw": lambda r: r["design"]["sigma_peak_raw"],
                     "crash_up_R_d0": lambda r: r["crash_up"]["R_peak_d0"],
                     "crash_up_sigma_d0": lambda r: r["crash_up"]["sigma_peak_d0"],
                     "crash_dn_R_d0": lambda r: r["crash_dn"]["R_peak_d0"],
                     "crash_px_R_d0": lambda r: r["crash_px"]["R_peak_d0"],
                     "crash_mx_R_d0": lambda r: r["crash_mx"]["R_peak_d0"],
                     "overhang_crash_top": lambda r: r["overhang_crash_top_pa"]}.items():
        m1["convergence"][key] = conv_table(hs, [get(r) for r in m1["levels"]])
    for c in ("design", "crash_up", "crash_dn", "crash_px", "crash_mx"):
        m1["convergence"][c + "_R_5mm"] = conv_table(hs, [r[c]["R_peak_5mm"] for r in m1["levels"]])
        if "ff_" + c in m1["levels"][0]:
            m1["convergence"]["ff_%s_R_d0" % c] = conv_table(hs, [r["ff_" + c]["R_peak_d0"] for r in m1["levels"]])
            m1["convergence"]["ff_%s_R_5mm" % c] = conv_table(hs, [r["ff_" + c]["R_peak_5mm"] for r in m1["levels"]])
            m1["convergence"]["ff_%s_R_mean" % c] = conv_table(hs, [r["ff_" + c]["R_mean"] for r in m1["levels"]])
            for q in ("Rcore_peak_d0", "Rcore_peak_5mm", "Rcore_mean"):
                m1["convergence"]["ff_%s_%s" % (c, q)] = conv_table(hs, [r["ff_" + c][q] for r in m1["levels"]])
    return m1


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    if "--plots" in sys.argv:
        import pod_fea_plots
        pod_fea_plots.draw(_load(OUT / "fea_results.json"), OUT)
    elif "--part" in sys.argv:
        run_part(sys.argv[sys.argv.index("--part") + 1])
    elif "--combine" in sys.argv:
        combine()
    else:
        main()
