"""D5-R6: SU2 linear-elastic FEA of the foot shoe GER-001 sleeve end under C5's 59.0 N ultimate side load (CR-C5-18,
CR-A1-65). Derived from C5's team/C5/sim/fea_shoe.py (same section-sweep hex mesh, same clamp and lever boundary
conditions, same SU2 driver su2fea.py, imported read-only from team/C5/sim), changed for the R6 shoe:

  * sleeve walls shoe.wall_t_m (ws) are separate from the 0.8 mm tine and legs (C5 used one w for all three);
  * the snap windows are short (hook + replace mark + 1 mm, landing.stack x_win), not the 41 mm stroke-long slots;
  * the legs are meshed at their drawn 0.8 mm (C5 meshed them at the sleeve wall), with the drawn R 1.0 leg-to-floor (6 chords)
    fillet on their outboard side (the sharp corner carried the h 0.32 peak next to the TE clamp end);
  * the rim's roof side is level with the pad edge (lip = rim_t) and the inside fillet is the drawn shoe.inside_fillet_r_m.

Geometry comes from subsystems/landing/fusion/landing.py stack() on the live params (P: + P:landing.*), optionally
overridden by D5_FEA_VARIANT="ws=0.0012,rim_t=0.0028" (m; rim_t also sets lip). The side load is the live
CL-C5-SIM3D-SIDE-ULT (team/C5/claims.sim.json); the model is linear, so the result is stored per newton of side load.

Run (repo root):  python -I redesign/team/D5/sim/fea_shoe_d5.py --one 0.4 +y      (one mesh level x case)
                  D5_FEA_VARIANT=... python -I redesign/team/D5/sim/fea_shoe_d5.py --one 0.4 +z
                  python -I redesign/team/D5/sim/fea_shoe_d5.py --xcheck-c5 0.4 +y  (C5's wall 2.0 / rim 3.0 / R 1 /
                  25 mm variant on C5's own rules: must give C5's 16.36 MPa)
Writes team/D5/sim/out/fea_d5_<tag>.json; feet_calc.py reads the governing stress per newton (ASM-D5-FEA-SHOE-K).
"""
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RED = HERE.parents[2]
sys.path.insert(0, str(RED / "team" / "C5" / "sim"))                 # su2fea (C5's SU2 driver, used read-only)
sys.path.insert(0, str(RED / "fusion"))
sys.path.insert(0, str(RED / "subsystems" / "landing" / "fusion"))
import gmsh  # noqa: E402
import su2fea  # noqa: E402
import landing  # noqa: E402

E_PETG, NU_PETG = 2000.0, 0.38          # MPa, - (stress does not depend on E in this linear model)
R_OUT = 0.4                             # mm printed outside corner radius (one extrusion width); CAD corners are sharp
LEG_FILLET_SEGS = 6                     # straight chords approximating the R6 leg-to-floor fillet arc
PATCH = 2.0                             # mm axial length of each tine bearing patch (C5)
EPS_Y = 0.05                            # ASM-D5-YIELD-STRAIN: piston pushed s0 = eps_y L_cart in (C5 lever)
OUT = HERE / "out"
RUNS = HERE / "runs"


def _params():
    P = json.loads((RED / "params" / "params.json").read_text("utf-8"))
    L = json.loads((RED / "subsystems" / "landing" / "params.json").read_text("utf-8"))

    def v(key, unit=None):
        d = P
        for k in key.split("."):
            d = d[k]
        return d["value"] if isinstance(d, dict) and "value" in d else d
    return landing.inputs(v, L)


def side_ult():
    nodes = {n["id"]: n for n in json.loads((RED / "team" / "C5" / "claims.sim.json").read_text("utf-8"))["nodes"]}
    return nodes["CL-C5-SIM3D-SIDE-ULT"]["value"]


def geometry(variant=None, c5_rules=False):
    n = _params()
    if variant:
        n.update(variant)
        if "rim_t" in variant and "lip" not in variant:
            n["lip"] = variant["rim_t"]
    s = landing.stack(n)
    mm = 1000.0
    win = s["x_win"]
    if c5_rules:                                   # C5's R5 stack rules: long windows, legs at the sleeve wall
        win = (s["x_hook"][0] - n["stroke"] - 0.001, s["x_hook"][1])
    g = {"x_bw0": s["x_bw"][0] * mm, "x_bw1": s["x_bw"][1] * mm, "x_end": s["x_slv_end"] * mm,
         "x_rim0": s["x_rim"][0] * mm, "x_te": n["te"] * mm, "x_win0": win[0] * mm, "x_win1": win[1] * mm,
         "x_open": s["x_open"] * mm, "x_g": s["x_g"] * mm, "L_cart": s["L_cart"] * mm,
         "hy_o": s["slv_out"][0] / 2 * mm, "hz_o": s["slv_out"][1] / 2 * mm, "w": n["ws"] * mm,
         "w_leg": (n["ws"] if c5_rules else n["w"]) * mm, "rim_t": n["rim_t"] * mm,
         "z0": s["z_slv"][0] * mm, "z1": s["z_slv"][1] * mm, "zw0": s["z_win"][0] * mm, "zw1": s["z_win"][1] * mm,
         "leg_in": s["leg_gap"] * mm, "leg_depth": n["leg_depth"] * mm, "engage": n["engage"] * mm,
         "bond_hy": s["collar_gap"] * mm, "z_hh": n["hh"] * mm, "r_in": n["r_in"] * mm,
         "r_out": R_OUT, "r_rim": R_OUT + n["rim_t"] * mm, "r_leg": 0.0 if c5_rules else n["r_in"] * mm}
    return g, n


def lever(F, g):
    """C5's / CALC-D5-SIDE lever: lip reaction R at the sleeve end, R - F at the tine open end (pushed in s0)."""
    s0 = EPS_Y * g["L_cart"]
    a = g["x_g"] - g["x_end"]
    R = F * (a + g["engage"]) / (g["engage"] + s0)
    return R, R - F, g["x_open"] - s0


def section(g, h):
    """Quad mesh of the y-z section with labels {wall, window, rim, core, leg} (C5's construction)."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    occ = gmsh.model.occ
    hy, hz, w, zc, rt, ri = g["hy_o"], g["hz_o"], g["w"], 0.5 * (g["z0"] + g["z1"]), g["rim_t"], g["r_in"]
    S_out = occ.addRectangle(-hy, zc - hz, 0, 2 * hy, 2 * hz, roundedRadius=g["r_out"])
    S_in = occ.addRectangle(-hy + w, zc - hz + w, 0, 2 * (hy - w), 2 * (hz - w), roundedRadius=ri)
    R_o = occ.addRectangle(-hy - rt, zc - hz - rt, 0, 2 * (hy + rt), 2 * (hz + rt), roundedRadius=g["r_rim"])
    tools = []
    for sg in (1, -1):
        y0 = sg * (hy - w - 0.3) if sg > 0 else -(hy + 0.3)
        tools.append(occ.addRectangle(y0, g["zw0"], 0, w + 0.6, g["zw1"] - g["zw0"]))
        ly = g["leg_in"] if sg > 0 else -g["leg_in"] - g["w_leg"]
        tools.append(occ.addRectangle(ly, g["z0"] - g["leg_depth"], 0, g["w_leg"], g["leg_depth"]))
    tools.append(occ.addRectangle(-g["bond_hy"], g["z0"], 0, 2 * g["bond_hy"], g["z_hh"] - g["z0"]))
    lf = g.get("r_leg", 0.0)                             # R6 leg-to-floor fillet (outboard corner of each leg)
    n_tools = len(tools)
    if lf > 0:
        for sg in (1, -1):
            lo = g["leg_in"] + g["w_leg"]
            # the arc as LEG_FILLET_SEGS straight chords (an exact arc meshed at 2h, then subdivided, puts the
            # subdivision midpoints back on the arc and tangles the quads in this 0.4 mm-thick, cusp-ended sliver)
            yc, zc_ = sg * (lo + lf), g["z0"] - lf
            pts = [(sg * lo, g["z0"])] + [(yc - sg * lf * math.cos(a), zc_ + lf * math.sin(a))
                                          for a in np.linspace(0.0, math.pi / 2, LEG_FILLET_SEGS + 1)]
            pt = [occ.addPoint(y_, z_, 0) for y_, z_ in pts]
            ln = [occ.addLine(pt[i], pt[(i + 1) % len(pt)]) for i in range(len(pt))]
            tools.append(occ.addPlaneSurface([occ.addCurveLoop(ln)]))
    _, frag_map = occ.fragment([(2, R_o)], [(2, S_out), (2, S_in)] + [(2, t) for t in tools])
    occ.synchronize()
    # the fillet pieces end in zero-angle cusps where a quad centroid can fall on the wrong side of the arc, so the
    # fillet quads are labelled by the gmsh surface they belong to, not by a centroid test (a centroid test left
    # 8 cusp quads labelled 'rim': inverted slivers that stopped SU2 converging)
    fillet_surfs = {s for m in frag_map[3 + n_tools:] for _, s in m}
    gmsh.option.setNumber("Mesh.MeshSizeMin", 2 * h)
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
    quads, tris, q_fil = [], [], []
    for _, sid in gmsh.model.getEntities(2):
        et, _, en = gmsh.model.mesh.getElements(2, sid)
        for t, c in zip(et, en):
            c = [idx[int(v)] for v in c]
            if t == 3:
                quads += [c[i:i + 4] for i in range(0, len(c), 4)]
                q_fil += [sid in fillet_surfs] * (len(c) // 4)
            elif t == 2:
                tris += [c[i:i + 3] for i in range(0, len(c), 3)]
    gmsh.finalize()
    if tris:
        raise RuntimeError("section mesh has %d triangles" % len(tris))
    quads = np.array(quads)
    c = xy[quads].mean(axis=1)
    y, z = np.abs(c[:, 0]), c[:, 1]

    def inside(y_, z_, hy_, hz_, r):
        dy, dz = np.maximum(np.abs(y_) - (hy_ - r), 0), np.maximum(np.abs(z_ - zc) - (hz_ - r), 0)
        return dy * dy + dz * dz <= r * r + 1e-12
    in_core = inside(y, z, hy - w, hz - w, ri)
    in_out = inside(y, z, hy, hz, g["r_out"])
    in_rim = inside(y, z, hy + rt, hz + rt, g["r_rim"])
    leg = (y > g["leg_in"]) & (y < g["leg_in"] + g["w_leg"]) & (z < g["z0"])
    lf, lo = g.get("r_leg", 0.0), g["leg_in"] + g["w_leg"]
    if lf > 0:
        leg |= np.array(q_fil, bool)
    lab = np.empty(len(quads), dtype=object)
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
    br = sorted(set([g["x_bw0"], g["x_bw1"], g["x_win0"], g["x_win1"], x_open_patch, x_open_patch + PATCH,
                     g["x_te"], g["x_rim0"], g["x_end"] - PATCH, g["x_end"]]))
    xs = [br[0]]
    for a, b in zip(br[:-1], br[1:]):
        fine = (a >= min(g["x_win1"], x_open_patch) - 1.0) or (a >= x_open_patch - 1e-9 and b <= x_open_patch + PATCH + 1e-9)
        hx = h if fine else 3 * h
        k = max(1, int(math.ceil((b - a) / hx - 1e-9)))
        xs += list(np.linspace(a, b, k + 1)[1:])
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
        return True
    N2 = len(xy)
    nodes = np.column_stack([np.repeat(xs, N2), np.tile(xy[:, 0], len(xs)), np.tile(xy[:, 1], len(xs))])
    hexes = []
    for k in range(len(xs) - 1):
        xm = 0.5 * (xs[k] + xs[k + 1])
        keep = np.array([present(L, xm) for L in lab])
        q = quads[keep]
        hexes.append(np.hstack([q + k * N2, q + (k + 1) * N2]))
    hexes = np.vstack(hexes)
    p = nodes[hexes]
    vol = np.einsum("ij,ij->i", np.cross(p[:, 1] - p[:, 0], p[:, 3] - p[:, 0]), p[:, 4] - p[:, 0])
    flip = vol < 0
    hexes[flip] = hexes[flip][:, [0, 3, 2, 1, 4, 7, 6, 5]]
    used = np.unique(hexes)
    remap = -np.ones(len(nodes), int)
    remap[used] = np.arange(len(used))
    nodes, hexes = nodes[used], remap[hexes]
    F = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    faces = np.vstack([hexes[:, f] for f in F])
    _, inv, cnt = np.unique(np.sort(faces, axis=1), axis=0, return_inverse=True, return_counts=True)
    bnd = faces[cnt[inv.ravel()] == 1]
    return nodes, hexes, bnd


def classify(nodes, bnd, g, case, x_open_patch):
    """Markers: clamp (bonded faces: floor on the step, legs' inner faces, back wall on the step front and strip
    ends), load_rim (last 2 mm of the inner face), load_open (2 mm at the tine open end, opposite wall), free."""
    c = nodes[bnd].mean(axis=1)
    a, b, d = nodes[bnd[:, 0]], nodes[bnd[:, 1]], nodes[bnd[:, 3]]
    nrm = np.cross(b - a, d - a)
    nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    x, y, z = c[:, 0], c[:, 1], c[:, 2]
    tol = 1e-6
    hy, w, ri = g["hy_o"], g["w"], g["r_in"]
    zi0, zi1 = g["z0"] + w, g["z1"] - w
    clamp = ((np.abs(z - g["z0"]) < tol) & (nrm[:, 2] < -0.99) & (np.abs(y) < g["leg_in"]) & (x < g["x_te"])) | \
            ((np.abs(np.abs(y) - g["leg_in"]) < tol) & (np.abs(nrm[:, 1]) > 0.99) & (y * nrm[:, 1] < 0) &
             (z < g["z0"])) | \
            ((np.abs(x - g["x_bw0"]) < tol) & (nrm[:, 0] < -0.99) & (np.abs(y) < g["bond_hy"]) & (z < g["z_hh"]))
    rim_x = x > g["x_end"] - PATCH
    open_x = (x > x_open_patch) & (x < x_open_patch + PATCH)
    flat_y = (z > zi0 + ri) & (z < zi1 - ri)
    flat_z = np.abs(y) < hy - w - ri
    if case == "+y":
        rim = rim_x & (np.abs(y - (hy - w)) < tol) & (nrm[:, 1] < -0.99) & flat_y
        opn = open_x & (np.abs(y + (hy - w)) < tol) & (nrm[:, 1] > 0.99) & flat_y
        d_rim, d_open = (0, 1, 0), (0, -1, 0)
    else:                                                # +z: rim reaction on the roof, open end on the floor
        rim = rim_x & (np.abs(z - zi1) < tol) & (nrm[:, 2] < -0.99) & flat_z
        opn = open_x & (np.abs(z - zi0) < tol) & (nrm[:, 2] > 0.99) & flat_z
        d_rim, d_open = (0, 0, 1), (0, 0, -1)
    rim &= ~clamp
    opn &= ~clamp & ~rim
    free = ~(clamp | rim | opn)
    return {"clamp": bnd[clamp], "load_rim": bnd[rim], "load_open": bnd[opn], "free": bnd[free]}, d_rim, d_open


def run_case(g, h, case, R, R_open, x_open_patch, tag):
    nodes, hexes, bnd = build(g, h, x_open_patch)
    mk, d_rim, d_open = classify(nodes, bnd, g, case, x_open_patch)
    A_rim, A_open = su2fea.face_area(nodes, mk["load_rim"]), su2fea.face_area(nodes, mk["load_open"])
    t0 = time.time()
    r = su2fea.run(RUNS / tag, nodes, hexes, mk, E_PETG, NU_PETG, ["clamp"],
                   [("load_rim", R / A_rim, d_rim), ("load_open", R_open / A_open, d_open)], ["free"])
    if not r["linsol_log_res"] < -6:                     # converged runs reach ~ -9; never store an unconverged field
        raise RuntimeError("SU2 linear solver did not converge in %s (log10 residual %s after %s iterations)"
                           % (RUNS / tag, r["linsol_log_res"], r["linsol_iter"]))
    xyz, vm, u = r["xyz"], r["Von_Mises_Stress"], r["Displacement"]
    x = xyz[:, 0]
    zones = {"rim": x > g["x_rim0"] + 1.0,
             "aft box": (x > g["x_win1"] + 1.0) & (x < g["x_rim0"] - 1.0),
             "window and open-end zone": (x > g["x_bw1"] + 1.0) & (x < g["x_win1"] + 1.0),
             "whole shoe": np.ones(len(x), bool)}
    # bonded clamp edges (floor and legs ending at the fin TE, the step front) are rigid-clamp corners (singular in a
    # linear model; the real support is epoxy on paper-faced foam): excluded within 2 mm of the TE in the floor band
    # and 1 mm of the back wall, reported as clamp_edge_excluded (C5 excluded the same edges)
    sing = ((np.abs(x - g["x_te"]) < 2.0) & (xyz[:, 2] < g["z0"] + g["w"] + 0.5)) | (x < g["x_bw0"] + 1.0)
    i_s = np.argmax(np.where(sing, vm, -1))
    clamp_edge = {"vm_max_MPa": float(vm[i_s]), "at_mm": [round(float(v), 3) for v in xyz[i_s]]}
    zr = {}
    for k, m in zones.items():
        mm_ = m & ~sing if k != "whole shoe" else m
        i = np.argmax(np.where(mm_, vm, -1))
        zr[k] = {"vm_max_MPa": float(vm[i]), "at_mm": [round(float(v), 3) for v in xyz[i]]}
    ax = {"+y": 1, "+z": 2}[case]
    tip = x > g["x_end"] - 1e-6
    return {"h_mm": h, "case": case, "hexes": int(len(hexes)), "nodes": int(len(nodes)), "A_rim_mm2": A_rim,
            "A_open_mm2": A_open, "R_N": R, "R_open_N": R_open, "u_end_max_mm": float(np.abs(u[tip, ax]).max()),
            "zones": zr, "clamp_edge_excluded": clamp_edge, "linsol_iter": r["linsol_iter"], "linsol_log_res": r["linsol_log_res"],
            "wall_s": time.time() - t0}


def one(h, case, xcheck=False):
    if xcheck:                                          # C5 variant: w 2.0 for sleeve AND tine, rim 3.0, R 1, e 25
        var = {"w": 0.002, "ws": 0.002, "rim_t": 0.003, "lip": 0.0012, "r_in": 0.001, "engage": 0.025,
               "fy": 0.0173, "fz": 0.0133}
        F = 34.34994                                    # C5's study basis (D5-R5 CALC-D5-SIDE F_N)
        g, n = geometry(var, c5_rules=True)
        g["r_out"], g["r_rim"] = 1.2, 2.4                # C5's printed radii
        tag = "xcheck_c5_v4_h%03d_%s" % (round(h * 1000), {"+y": "py", "+z": "pz"}[case])
    else:
        var = {k: float(v) for k, v in (kv.split("=") for kv in os.environ.get("D5_FEA_VARIANT", "").split(",") if kv)}
        F = side_ult()
        g, n = geometry(var or None)
        tag = "h%03d_%s" % (round(h * 1000), {"+y": "py", "+z": "pz"}[case]) + (
            ("_v_" + "_".join("%s%g" % (k, v * 1000) for k, v in sorted(var.items()))) if var else "")
    R, R_open, x_open_patch = lever(F, g)
    r = run_case(g, h, case, R, R_open, x_open_patch, tag)
    gov = max(r["zones"][k]["vm_max_MPa"] for k in ("rim", "aft box", "window and open-end zone"))
    r.update({"variant": var, "F_side_N": F, "geometry_mm": g, "x_open_patch_mm": x_open_patch,
              "governing_vm_MPa": gov, "k_MPa_per_N_side": gov / F, "radii_mm": [g["r_in"], g["r_out"], g["r_rim"]],
              "E_MPa": E_PETG, "nu": NU_PETG, "patch_mm": PATCH, "eps_y": EPS_Y})
    OUT.mkdir(exist_ok=True)
    (OUT / ("fea_d5_%s.json" % tag)).write_text(json.dumps(r, indent=1))
    print(tag, "gov %.2f MPa (k %.4f MPa/N)" % (gov, gov / F), json.dumps(r["zones"]), "%.0f s" % r["wall_s"],
          flush=True)


if __name__ == "__main__":
    if "--one" in sys.argv:
        i = sys.argv.index("--one")
        one(float(sys.argv[i + 1]), sys.argv[i + 2])
    elif "--xcheck-c5" in sys.argv:
        i = sys.argv.index("--xcheck-c5")
        one(float(sys.argv[i + 1]), sys.argv[i + 2], xcheck=True)
    else:
        print(__doc__)
