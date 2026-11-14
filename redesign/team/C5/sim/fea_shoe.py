"""C5 simulation round: SU2 linear-elastic FEA of the foot shoe GER-001 (sleeve end + rim) under the landing side load.

Run:  python -I redesign/team/C5/sim/fea_shoe.py --one 0.4 +y     (one level x case; 3 levels x 2 cases, run in
      parallel: 7-60 min each on the 20-core machine, see sim/run_fea.sh)
      python -I redesign/team/C5/sim/fea_shoe.py --collect        (merge, strip verification, convergence)
      C5-R6: with C5_FEA_VARIANT set, --one and --collect run / merge that geometry (out/fea_shoe<suffix>.json);
      the D-65 stack is C5_FEA_VARIANT="w=0.002,rim_t=0.003,r_in=0.001,engage=0.025" (sim/run_d65.sh)
Writes sim/out/fea_shoe.json (every level, every case, verification strip) and the run logs in sim/runs/.
landing_sim_claims.py reads the JSON summary into the proof chain.

Why FEA here: D5's CALC-D5-SIDE checks the rim with a fixed-ended beam (M = R b / 12) and gets SF 1.05, the thinnest
margin in the landing load path. The beam ignores the snap-finger windows (6 mm tall, 41 mm long) cut through both
y walls ahead of the rim, the corner fillets and the sleeve cantilevering 6.8 mm past the fin TE.

Geometry (as designed, D5-R5 stack from subsystems/landing/fusion/landing.py `stack()` with D5's CALC-D5-GEOM inputs;
mm, x aft along the foot axis, y outboard from the fin plane, z up):
  sleeve 21.1 x 17.1 outside, 0.8 wall, x 275.8-326.8; back wall 1.0 (x 274.8-275.8); rim +1.2 all round over the
  last 6.0 mm; snap windows 6.0 mm (z 206.25-212.25) through both y walls over x 276.3-317.3; two 0.8 mm legs on the
  fin faces (|y| 5.0-5.8, 7 mm deep) to the fin TE x 320.0. Printed corners: inside radius 0.4 mm, outside 1.2 mm
  (rim 2.4 mm) = one 0.4 mm extrusion width; the CAD boxes are sharp, a print is not.
Boundary conditions: bonded faces clamped (floor on the fin step |y| <= 5.0, legs' inner faces, back wall on the step
  front and strip ends |y| <= 5.8, z <= 210). Collar cheeks left out (conservative).
Loads (D5's lever, CALC-D5-SIDE): side force F at the pad, piston pushed s0 = eps_y L_cart into the sleeve; tine
  bears on the sleeve end (R = F (a + e) / (e + s0), last 2 mm of the inner face) and on the opposite wall at its open
  end (R - F, 2 mm). Cases: +y (outboard wall), +z (roof), -z (floor past the TE). Linear, so stress per newton is
  reported and scaled in the claims script.
Elements: trilinear hexahedra, a quad-meshed section (gmsh) swept along x. The verification strip below shows why:
  linear tetrahedra with 5.7 elements through a 0.8 mm wall were still 14 % too stiff and 17 % low in bending stress.
"""
import json
import math
import sys
import time
from pathlib import Path

import gmsh
import numpy as np

HERE = Path(__file__).resolve().parent
RED = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RED / "fusion"))
sys.path.insert(0, str(RED / "subsystems" / "landing" / "fusion"))
import su2fea  # noqa: E402

E_PETG, NU_PETG = 2000.0, 0.38          # MPa, - (printed PETG XY; stress does not depend on E in this linear model)
R_IN, R_OUT, R_RIM = 0.4, 1.2, 2.4      # mm printed corner radii (one 0.4 mm extrusion width)
PATCH = 2.0                              # mm, axial length of each tine bearing patch
LEVELS = [0.4, 0.32, 0.2667]             # mm element size in the wall: 2, 2.5, 3 elements through 0.8 mm (r 1.25, 1.2)
CASES = ["+y", "+z"]                     # -z (floor past the TE, on the fin) is not critical and was dropped


# design-fix study: C5_FEA_VARIANT="w=0.0016,rim_t=0.002" overrides D5 inputs (m); outputs get a _v suffix
import os  # noqa: E402
VARIANT = {k: float(v) for k, v in (kv.split("=") for kv in os.environ.get("C5_FEA_VARIANT", "").split(",") if kv)}
if "r_in" in VARIANT:                                     # printed inside corner radius (m), not a D5 input
    R_IN = VARIANT.pop("r_in") * 1000.0
    _RTAG = "_rin%g" % R_IN
else:
    _RTAG = ""
SUFFIX = (("_v_" + "_".join("%s%g" % (k, v * 1000) for k, v in sorted(VARIANT.items()))) if VARIANT else "") + _RTAG


def d5_inputs():
    """D5's CALC-D5-GEOM / CALC-D5-SIDE inputs and outputs (the as-designed foot) from team/D5/claims.json."""
    nodes = {n["id"]: n for n in json.loads((RED / "team" / "D5" / "claims.json").read_text("utf-8"))["nodes"]}
    side = nodes["CALC-D5-SIDE"]
    return side["input_values"], side["outputs"], nodes["CALC-D5-GEOM"]["outputs"]


def geometry():
    import landing                                         # D5's CAD module: stack() is pure
    n, side_out, geo_out = d5_inputs()
    n = dict(n)
    n.setdefault("ws", n["w"])                            # D5-R6 stack(): separate sleeve wall ws (R5: ws = w)
    n.update(VARIANT)
    if "w" in VARIANT and "ws" not in VARIANT:            # R5-style variant: one wall for sleeve, tine and legs
        n["ws"] = n["w"]
    s = landing.stack(n)
    mm = 1000.0
    g = {
        "x_bw0": s["x_bw"][0] * mm, "x_bw1": s["x_bw"][1] * mm, "x_end": s["x_slv_end"] * mm,
        "x_rim0": s["x_rim"][0] * mm, "x_te": n["te"] * mm, "x_win0": s["x_win"][0] * mm, "x_win1": s["x_win"][1] * mm,
        "x_open": s["x_open"] * mm, "x_g": s["x_g"] * mm, "L_cart": s["L_cart"] * mm,
        "hy_o": s["slv_out"][0] / 2 * mm, "hz_o": s["slv_out"][1] / 2 * mm, "w": n["ws"] * mm, "rim_t": n["rim_t"] * mm,
        "z0": s["z_slv"][0] * mm, "z1": s["z_slv"][1] * mm, "zw0": s["z_win"][0] * mm, "zw1": s["z_win"][1] * mm,
        "leg_in": s["leg_gap"] * mm, "leg_depth": n["leg_depth"] * mm, "engage": n["engage"] * mm,
        "bond_hy": (s["collar_gap"]) * mm, "z_hh": n["hh"] * mm,
    }
    # cross-check against D5's stored geometry
    if not VARIANT:
        assert abs(g["x_end"] - geo_out["x_sleeve_end_m"] * mm) < 1e-6
        assert abs(2 * g["hy_o"] - geo_out["sleeve_out_m"][0] * mm) < 1e-6
    return g, n, side_out


def lever(F, g, eps_y):
    """D5's tine lever (CALC-D5-SIDE): lip reaction R at the sleeve end and R - F at the tine open end."""
    s0 = eps_y * g["L_cart"]
    a = g["x_g"] - g["x_end"]
    R = F * (a + g["engage"]) / (g["engage"] + s0)
    return R, R - F, g["x_open"] - s0


# ------------------------------------------------------------------ section mesh (gmsh, quads)
def section(g, h):
    """Quad mesh of the y-z section with region labels. Returns nodes (N,2), quads (Q,4), labels (Q,) in
    {wall, window, rim, core, leg}."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    occ = gmsh.model.occ
    hy, hz, w, zc = g["hy_o"], g["hz_o"], g["w"], 0.5 * (g["z0"] + g["z1"])
    S_out = occ.addRectangle(-hy, zc - hz, 0, 2 * hy, 2 * hz, roundedRadius=R_OUT)
    S_in = occ.addRectangle(-hy + w, zc - hz + w, 0, 2 * (hy - w), 2 * (hz - w), roundedRadius=R_IN)
    rt = g["rim_t"]
    R_o = occ.addRectangle(-hy - rt, zc - hz - rt, 0, 2 * (hy + rt), 2 * (hz + rt), roundedRadius=R_RIM)
    tools = []
    for sg in (1, -1):                                   # window bands through both y walls (slightly oversize)
        y0 = sg * (hy - w - 0.3) if sg > 0 else -(hy + 0.3)
        tools.append(occ.addRectangle(y0, g["zw0"], 0, w + 0.6, g["zw1"] - g["zw0"]))
        ly = g["leg_in"] if sg > 0 else -g["leg_in"] - w
        tools.append(occ.addRectangle(ly, g["z0"] - g["leg_depth"], 0, w, g["leg_depth"]))
    tools.append(occ.addRectangle(-g["bond_hy"], g["z0"], 0, 2 * g["bond_hy"], g["z_hh"] - g["z0"]))
    occ.fragment([(2, R_o)], [(2, S_out), (2, S_in)] + [(2, t) for t in tools])
    occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeMin", 2 * h)        # all-quad subdivision halves the size
    gmsh.option.setNumber("Mesh.MeshSizeMax", 2 * h)
    gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.RecombineAll", 1)
    gmsh.option.setNumber("Mesh.RecombinationAlgorithm", 1)
    gmsh.option.setNumber("Mesh.Algorithm", 8)
    gmsh.model.mesh.generate(2)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    xy = np.asarray(xyz).reshape(-1, 3)[:, :2]
    idx = {int(t): i for i, t in enumerate(tags)}
    quads, tris = [], []
    for _, s in gmsh.model.getEntities(2):
        et, _, en = gmsh.model.mesh.getElements(2, s)
        for t, c in zip(et, en):
            c = [idx[int(v)] for v in c]
            if t == 3:
                quads += [c[i:i + 4] for i in range(0, len(c), 4)]
            elif t == 2:
                tris += [c[i:i + 3] for i in range(0, len(c), 3)]
    gmsh.finalize()
    if tris:
        raise RuntimeError("section mesh has %d triangles (subdivision should give quads only)" % len(tris))
    quads = np.array(quads)
    c = xy[quads].mean(axis=1)
    lab = np.empty(len(quads), dtype=object)
    y, z = np.abs(c[:, 0]), c[:, 1]

    def inside(y_, z_, hy_, hz_, r):                     # rounded rectangle centred (0, zc)
        dy, dz = np.maximum(np.abs(y_) - (hy_ - r), 0), np.maximum(np.abs(z_ - zc) - (hz_ - r), 0)
        return dy * dy + dz * dz <= r * r + 1e-12
    in_core = inside(y, z, hy - w, hz - w, R_IN)
    in_out = inside(y, z, hy, hz, R_OUT)
    in_rim = inside(y, z, hy + rt, hz + rt, R_RIM)
    leg = (y > g["leg_in"]) & (y < g["leg_in"] + w) & (z < g["z0"])
    lab[:] = "void"
    lab[in_rim & ~in_out] = "rim"
    lab[in_out & ~in_core] = "wall"
    lab[in_out & ~in_core & (y > hy - w) & (z > g["zw0"]) & (z < g["zw1"])] = "window"
    lab[in_core] = "core"
    lab[leg] = "leg"
    if (lab == "void").any():
        raise RuntimeError("unlabelled section quads")
    return xy, quads, lab


def build(g, h, x_open_patch):
    xy, quads, lab = section(g, h)
    br = sorted(set([g["x_bw0"], g["x_bw1"], g["x_win0"], x_open_patch, x_open_patch + PATCH, g["x_win1"],
                     g["x_te"], g["x_rim0"], g["x_end"] - PATCH, g["x_end"]]))
    xs = [br[0]]
    for a, b in zip(br[:-1], br[1:]):
        fine = (a >= g["x_win1"] - 1.0) or (a >= x_open_patch - 1e-9 and b <= x_open_patch + PATCH + 1e-9)
        hx = h if fine else 3 * h
        n = max(1, int(math.ceil((b - a) / hx - 1e-9)))
        xs += list(np.linspace(a, b, n + 1)[1:])
    xs = np.array(xs)

    def present(label, xm):
        if label == "core":
            return xm < g["x_bw1"]
        if label == "leg":
            return xm < g["x_te"]
        if label == "rim":
            return xm > g["x_rim0"]
        if label == "window":
            return not (g["x_win0"] < xm < g["x_win1"])
        return True                                       # wall
    N2 = len(xy)
    nodes = np.column_stack([np.repeat(xs, N2), np.tile(xy[:, 0], len(xs)), np.tile(xy[:, 1], len(xs))])
    hexes = []
    for k in range(len(xs) - 1):
        xm = 0.5 * (xs[k] + xs[k + 1])
        keep = np.array([present(L, xm) for L in lab])
        q = quads[keep]
        hexes.append(np.hstack([q + k * N2, q + (k + 1) * N2]))
    hexes = np.vstack(hexes)
    # orientation: (p1-p0) x (p3-p0) . (p4-p0) > 0
    p = nodes[hexes]
    vol = np.einsum("ij,ij->i", np.cross(p[:, 1] - p[:, 0], p[:, 3] - p[:, 0]), p[:, 4] - p[:, 0])
    flip = vol < 0
    hexes[flip] = hexes[flip][:, [0, 3, 2, 1, 4, 7, 6, 5]]
    used = np.unique(hexes)
    remap = -np.ones(len(nodes), int)
    remap[used] = np.arange(len(used))
    nodes, hexes = nodes[used], remap[hexes]
    # boundary faces (outward ordering: faces listed so the right-hand normal points out of a positive hex)
    F = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    faces = np.vstack([hexes[:, f] for f in F])
    key = np.sort(faces, axis=1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    bnd = faces[cnt[inv.ravel()] == 1]
    return nodes, hexes, bnd, xs


def classify(nodes, bnd, g, case, x_open_patch):
    """Markers: clamp (bonded faces), load_rim, load_open, free."""
    c = nodes[bnd].mean(axis=1)
    a, b, d = nodes[bnd[:, 0]], nodes[bnd[:, 1]], nodes[bnd[:, 3]]
    nrm = np.cross(b - a, d - a)
    nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    x, y, z = c[:, 0], c[:, 1], c[:, 2]
    tol = 1e-6
    hy, w = g["hy_o"], g["w"]
    zi0, zi1 = g["z0"] + w, g["z1"] - w
    clamp = ((np.abs(z - g["z0"]) < tol) & (nrm[:, 2] < -0.99) & (np.abs(y) < g["leg_in"]) & (x < g["x_te"])) | \
            ((np.abs(np.abs(y) - g["leg_in"]) < tol) & (np.abs(nrm[:, 1]) > 0.99) & (y * nrm[:, 1] < 0) &
             (z < g["z0"])) | \
            ((np.abs(x - g["x_bw0"]) < tol) & (nrm[:, 0] < -0.99) & (np.abs(y) < g["bond_hy"]) & (z < g["z_hh"]))
    rim_x = x > g["x_end"] - PATCH
    open_x = (x > x_open_patch) & (x < x_open_patch + PATCH)
    flat_y = (z > zi0 + R_IN) & (z < zi1 - R_IN)
    flat_z = np.abs(y) < hy - w - R_IN
    if case == "+y":
        rim = rim_x & (np.abs(y - (hy - w)) < tol) & (nrm[:, 1] < -0.99) & flat_y
        opn = open_x & (np.abs(y + (hy - w)) < tol) & (nrm[:, 1] > 0.99) & flat_y
        d_rim, d_open = (0, 1, 0), (0, -1, 0)
    elif case == "+z":
        rim = rim_x & (np.abs(z - zi1) < tol) & (nrm[:, 2] < -0.99) & flat_z
        opn = open_x & (np.abs(z - zi0) < tol) & (nrm[:, 2] > 0.99) & flat_z
        d_rim, d_open = (0, 0, 1), (0, 0, -1)
    else:                                                # -z
        rim = rim_x & (np.abs(z - zi0) < tol) & (nrm[:, 2] > 0.99) & flat_z
        opn = open_x & (np.abs(z - zi1) < tol) & (nrm[:, 2] < -0.99) & flat_z
        d_rim, d_open = (0, 0, -1), (0, 0, 1)
    rim &= ~clamp
    opn &= ~clamp & ~rim
    free = ~(clamp | rim | opn)
    return {"clamp": bnd[clamp], "load_rim": bnd[rim], "load_open": bnd[opn], "free": bnd[free]}, d_rim, d_open


def run_case(g, h, case, R, R_open, x_open_patch, mesh=None):
    nodes, hexes, bnd, xs = mesh or build(g, h, x_open_patch)
    mk, d_rim, d_open = classify(nodes, bnd, g, case, x_open_patch)
    A_rim, A_open = su2fea.face_area(nodes, mk["load_rim"]), su2fea.face_area(nodes, mk["load_open"])
    t0 = time.time()
    tag = "h%03d_%s%s" % (round(h * 1000), {"+y": "py", "+z": "pz", "-z": "mz"}[case], SUFFIX)
    r = su2fea.run(HERE / "runs" / tag, nodes, hexes, mk, E_PETG, NU_PETG, ["clamp"],
                   [("load_rim", R / A_rim, d_rim), ("load_open", R_open / A_open, d_open)], ["free"])
    xyz, vm, u = r["xyz"], r["Von_Mises_Stress"], r["Displacement"]
    x = xyz[:, 0]
    zones = {"rim": x > g["x_rim0"] + 1.0,                                   # >= 1 mm from the rim step
             "aft box": (x > g["x_win1"] + 1.0) & (x < g["x_rim0"] - 1.0),     # between window end and rim step
             "window strips": (x > g["x_win0"] + 1.0) & (x < g["x_win1"] - 1.0),
             "whole shoe": np.ones(len(x), bool)}                              # includes sharp corners (singular)
    zr = {}
    for k, m in zones.items():
        i = np.argmax(np.where(m, vm, -1))
        zr[k] = {"vm_max_MPa": float(vm[i]), "at_mm": [round(float(v), 3) for v in xyz[i]]}
    ax = {"+y": 1, "+z": 2, "-z": 2}[case]
    tip = x > g["x_end"] - 1e-6
    return {"h_mm": h, "case": case, "hexes": int(len(hexes)), "nodes": int(len(nodes)),
            "A_rim_mm2": A_rim, "A_open_mm2": A_open, "R_N": R, "R_open_N": R_open,
            "u_end_max_mm": float(np.abs(u[tip, ax]).max()), "zones": zr,
            "linsol_iter": r["linsol_iter"], "linsol_log_res": r["linsol_log_res"], "wall_s": time.time() - t0}


# ------------------------------------------------------------------ verification: cantilever strip
def strip_check():
    """0.8 x 6 x 20 mm PETG strip, tip load 0.1 N: SU2 hexes vs Euler-Bernoulli (deflection, root-side stress)."""
    L, b, t, P = 20.0, 6.0, 0.8, 0.1
    out = []
    for nz in (2, 3, 4):
        h = t / nz
        nx, ny = int(round(L / h)), int(round(b / h))
        xs, ys, zs = np.linspace(0, L, nx + 1), np.linspace(0, b, ny + 1), np.linspace(0, t, nz + 1)
        X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
        nodes = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
        I = np.arange(len(nodes)).reshape(nx + 1, ny + 1, nz + 1)
        h8 = np.stack([I[:-1, :-1, :-1], I[1:, :-1, :-1], I[1:, 1:, :-1], I[:-1, 1:, :-1],
                       I[:-1, :-1, 1:], I[1:, :-1, 1:], I[1:, 1:, 1:], I[:-1, 1:, 1:]], -1).reshape(-1, 8)
        F = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
        faces = np.vstack([h8[:, f] for f in F])
        _, inv, cnt = np.unique(np.sort(faces, 1), axis=0, return_inverse=True, return_counts=True)
        bnd = faces[cnt[inv.ravel()] == 1]
        cx = nodes[bnd].mean(1)[:, 0]
        mk = {"clamp": bnd[cx < 1e-9], "tip": bnd[cx > L - 1e-9], "free": bnd[(cx > 1e-9) & (cx < L - 1e-9)]}
        r = su2fea.run(HERE / "runs" / ("strip_nz%d" % nz), nodes, h8, mk, E_PETG, NU_PETG, ["clamp"],
                       [("tip", P / (b * t), (0, 0, -1))], ["free"])
        x = r["xyz"]
        uz = float(r["Displacement"][np.abs(x[:, 0] - L) < 1e-6, 2].mean())
        xm = float(x[np.argmin(np.abs(x[:, 0] - L / 2)), 0])          # node plane nearest mid-span
        sx = float(r["Sxx"][(np.abs(x[:, 0] - xm) < 1e-6) & (x[:, 2] > t - 1e-6) & (np.abs(x[:, 1] - b / 2) < 1.5)]
                   .mean())
        I_ = b * t ** 3 / 12
        out.append({"nz": nz, "hexes": int(len(h8)), "uz_mm": uz, "uz_beam_mm": -P * L ** 3 / (3 * E_PETG * I_),
                    "x_mid_mm": xm, "sxx_mid_MPa": sx, "sxx_beam_MPa": P * (L - xm) * (t / 2) / I_})
    return out


def richardson(f1, f2, f3, r12, r23):
    """Observed order and extrapolated value from three levels (f3 finest), non-uniform ratios (Roache)."""
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 or e32 == 0 or e21 * e32 < 0:
        return {"p": None, "f_ext": None, "gci_fine": None, "monotone": False}
    p = abs(math.log(abs(e21 / e32))) / math.log(r23)
    for _ in range(50):                                    # fixed point for unequal ratios
        q = math.log((r12 ** p - 1) / (r23 ** p - 1)) if r12 != r23 else 0.0
        p = abs(math.log(abs(e21 / e32)) + q) / math.log(r23)
    f_ext = f3 + (f3 - f2) / (r23 ** p - 1)
    return {"p": p, "f_ext": f_ext, "gci_fine": 1.25 * abs((f3 - f2) / f3) / (r23 ** p - 1), "monotone": True}


def one(h, case):
    """One level, one case -> out/fea_<h>_<case>.json (run several of these in parallel)."""
    g, n, side_out = geometry()
    F = side_out["F_N"]                                    # D5's ultimate side load (1.5 x C5 side load)
    R, R_open, x_open_patch = lever(F, g, n["eps_y"])
    assert VARIANT or abs(R - side_out["R_lip_N"]) < 1e-6 * R, (R, side_out["R_lip_N"])
    r = run_case(g, h, case, R, R_open, x_open_patch)
    r["inputs"] = {"geometry_mm": g, "F_side_ult_N": F, "R_lip_N": R, "R_open_N": R_open,
                   "x_open_patch_mm": x_open_patch, "E_MPa": E_PETG, "nu": NU_PETG, "radii_mm": [R_IN, R_OUT, R_RIM],
                   "patch_mm": PATCH, "d5_sigma_rim_MPa": side_out["sigma_rim_Pa"] / 1e6, "d5_sf_rim": side_out["sf_rim"]}
    tag = "h%03d_%s%s" % (round(h * 1000), {"+y": "py", "+z": "pz", "-z": "mz"}[case], SUFFIX)
    r["variant"] = VARIANT
    (HERE / "out" / ("fea_%s.json" % tag)).write_text(json.dumps(r, indent=1))
    print(tag, json.dumps(r["zones"]), "%.0f s" % r["wall_s"], flush=True)


def collect():
    """Merge the per-run files, add the strip verification and the three-level convergence."""
    res = {"levels": [], "strip": strip_check()}
    for h in LEVELS:
        for case in CASES:
            tag = "h%03d_%s%s" % (round(h * 1000), {"+y": "py", "+z": "pz", "-z": "mz"}[case], SUFFIX)
            res["levels"].append(json.loads((HERE / "out" / ("fea_%s.json" % tag)).read_text()))
    res["inputs"] = res["levels"][0].pop("inputs")
    for r in res["levels"][1:]:
        r.pop("inputs", None)
    conv = {}
    hs = LEVELS
    for case in CASES:
        rows = [r for r in res["levels"] if r["case"] == case]
        for key in ("rim", "aft box", "window strips", "whole shoe"):
            f = [r["zones"][key]["vm_max_MPa"] for r in rows]
            conv["%s|%s" % (case, key)] = dict(values=f, **richardson(*f, hs[0] / hs[1], hs[1] / hs[2]))
        f = [r["u_end_max_mm"] for r in rows]
        conv["%s|end deflection" % case] = dict(values=f, **richardson(*f, hs[0] / hs[1], hs[1] / hs[2]))
    res["convergence"] = conv
    res["variant"] = res["levels"][0].get("variant", {})
    res["r_in_mm"] = R_IN
    (HERE / "out" / ("fea_shoe%s.json" % SUFFIX)).write_text(json.dumps(res, indent=1))
    print(json.dumps(conv, indent=1))


if __name__ == "__main__":
    if "--collect" in sys.argv:
        collect()
    elif "--one" in sys.argv:
        i = sys.argv.index("--one")
        one(float(sys.argv[i + 1]), sys.argv[i + 2])
    else:
        print("usage: fea_shoe.py --one <h_mm> <+y|+z>   (each level x case; run in parallel)  then  --collect")
