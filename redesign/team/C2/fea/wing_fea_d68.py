"""C2-R3 FEA re-run on the D-68 wing fixes, by global-local submodelling.

D-68 (A1 decision log, from CR-C2-11 / CR-C2-13):
  * the through-core PETG block's four vertical edges rounded R 3 mm, the core pocket cut to match;
  * a thickened-epoxy (microballoon) fillet bead >= 3 mm along the inboard and outboard pocket edges, both surfaces;
  * the elevon cut-out corners at the fin-root tab (|y| 0.30 / 0.34, at the hinge line) rounded R >= 3 mm.
D1 has not yet drawn these in wing.py (D1-R1 geometry is read live); the radii and bead are applied here exactly as
D-68 states them. Re-run when D1 publishes the revised pocket.

Why a submodel: the R2 full-wing meshes are 2-10 mm at the pocket's front corner (x 0.028), far too coarse for a
3 mm radius. Refining the whole extruded wing to < 1 mm there is ~5 M dofs. Standard practice is global-local:
  1. GLOBAL: the R2 level-2 wing (458 k dofs, set O orthotropic tube, clamped at the root, C1-R4 loads) with extra
     span layers at the cut planes; displacements saved on the cut planes.
  2. LOCAL: the span y_c0 .. y_c1 round the fin station (default 0.27 .. 0.37 m: >= 30 mm, one section depth,
     from every changed feature), re-meshed with 3 local refinement levels at the pocket edges, the skin over the
     pocket, and the hinge-line corners; D-68 geometry built in; the global displacement imposed on both cut
     planes (St Venant), the same skin tractions as the global model on every skin patch in between.
  Checks: (a) the cut planes moved 10 mm closer (0.28 .. 0.36) at the middle level; (b) the as-drawn (R2) geometry
  run through the same local model, compared with the R2 full-model peaks; (c) equilibrium of the local model.

Geometry construction (on the extruded mesh, so every node stays on its span layer):
  * corner rounding: for a convex plan-view corner (x0, y0) of region A (the PETG block, or the elevon cut-out void)
    with A on the sx / sy side, every node is shifted in x by sx * delta(y) * w(x). delta(y) = R - sqrt(R^2 -
    (R - eta)^2) for 0 <= eta = sy (y - y0) <= R (the arc), tapering linearly to 0 over 2R outside A (eta < 0),
    zero beyond eta = R. w(x) is a hat, 1 at x0, 0 at x0 + sx d_in and x0 - sx d_out (both > R: monotone map, no
    inverted element). The material of each element is fixed before the shift, so the A / not-A interface follows
    the arc through the layers (piecewise linear between layers). z is rescaled with the local section thickness.
  * bead: the foam elements with x in the pocket's x range, outside an inboard/outboard pocket face by dy >= 0 and
    below the skin by ds >= 0 with dy + ds <= 3 mm (a 3 x 3 mm triangular fillet) become epoxy-microballoon.

Run (repo root):  python -I redesign/team/C2/fea/wing_fea_d68.py [--levels 1 2 3] [--geoms d68 asdrawn]
Writes team/C2/fea/out/d68_submodel.json.
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import su2fea as sf                 # noqa: E402
import wing_fea as wf               # noqa: E402
import wing_fea_direct as wfd       # noqa: E402
import wing_struct as ws            # noqa: E402

OUT = HERE / "out"
FOAM, CF, PETG, BEAD = 0, 1, 2, 3

R_POCKET = 0.003           # D-68: block vertical edges R 3 mm, pocket cut to match
R_CUT = 0.003              # D-68: elevon cut-out corners R >= 3 mm (minimum modelled)
BEAD_LEG = 0.003           # D-68: fillet bead >= 3 mm (minimum modelled)
BEAD_E, BEAD_NU = 1.5e9, 0.35    # ASM-C2-BEAD: glass-microballoon-thickened epoxy, 1:1 by volume
CUTS = (0.27, 0.37)
CUTS_NEAR = (0.28, 0.36)
LOCAL_H = {1: 1.6e-3, 2: 1.1e-3, 3: 0.75e-3}       # local element size at the corners and over the pocket skin
HY_BASE = 0.0025                                     # span layer size elsewhere in the local model
GLOBAL_LEVEL = 2
CLIP = 0.006               # results within this distance of a cut plane are not reported
AVG_R = 0.0010             # volume-average radius for the foam peaks (a few XPS cells; see SIMULATION-REPORT)


def zu(x):
    return np.interp(x, ws.XA, ws.ZU)


def zl(x):
    return np.interp(x, ws.XA, ws.ZL)


# ------------------------------------------------------------------------------------------------ geometry helpers
def breaks_with(g, extra):
    br = sorted(list(wf.span_breaks(g)) + list(extra))
    out = [br[0]]
    for v in br[1:]:
        if v - out[-1] > 0.0006:
            out.append(v)
        elif v in extra:
            out[-1] = v                 # keep the requested plane exactly
    return out


def face_y(breaks, y):
    """Span layer that carries a pocket face (span_breaks merges planes < 0.6 mm apart)."""
    return min(breaks, key=lambda b: abs(b - y))


def corners(g, breaks):
    """Convex plan-view corners to round: (x0, y0, sx, sy, R, d_in, d_out, kind)."""
    bx0, bx1 = g["blk_x"]
    by0, by1 = face_y(breaks, g["blk_y"][0]), face_y(breaks, g["blk_y"][1])
    xs, rs = g["xs"], g["rs"]
    d_in_aft = min(2.5 * R_POCKET, (bx1 - (xs + rs)) - 0.0004)      # stop short of the tube's outer wall
    c = [(bx0, by0, +1, +1, R_POCKET, 2.5 * R_POCKET, 2.5 * R_POCKET, "pocket"),
         (bx0, by1, +1, -1, R_POCKET, 2.5 * R_POCKET, 2.5 * R_POCKET, "pocket"),
         (bx1, by0, -1, +1, R_POCKET, d_in_aft, 2.5 * R_POCKET, "pocket"),
         (bx1, by1, -1, -1, R_POCKET, d_in_aft, 2.5 * R_POCKET, "pocket")]
    # elevon cut-outs: the corners at the fin-root tab only (inner span ends, outer span starts)
    (a0, a1), (b0, b1) = g["spans"]
    c += [(g["xh"], a1, +1, -1, R_CUT, 2.5 * R_CUT, 2.5 * R_CUT, "cutout"),
          (g["xh"], b0, +1, +1, R_CUT, 2.5 * R_CUT, 2.5 * R_CUT, "cutout")]
    return c


def morph(X, cs, tube=None):
    x, y, z = X[:, 0].copy(), X[:, 1], X[:, 2]
    shift = np.zeros(len(X))
    for x0, y0, sx, sy, R, d_in, d_out, _ in cs:
        eta = sy * (y - y0)
        delta = np.zeros(len(X))
        arc = (eta >= 0) & (eta <= R)
        delta[arc] = R - np.sqrt(np.maximum(R * R - (R - eta[arc]) ** 2, 0.0))
        tap = (eta < 0) & (eta > -2 * R)
        delta[tap] = R * (1 + eta[tap] / (2 * R))
        s = sx * (x - x0)                      # > 0 on the A side
        w = np.where(s >= 0, np.clip(1 - s / d_in, 0, 1), np.clip(1 + s / d_out, 0, 1))
        shift += sx * delta * w
    if tube is not None:
        xc, zc, r_out = tube
        shift[np.hypot(x - xc, z - zc) <= r_out + 1e-6] = 0.0
    xn = x + shift
    t0 = zu(x) - zl(x)
    t1 = zu(xn) - zl(xn)
    zn = zl(xn) + (z - zl(x)) * np.where(t0 > 0, t1 / np.where(t0 > 0, t0, 1), 1.0)
    Xn = X.copy()
    Xn[:, 0] = xn
    Xn[:, 2] = np.where(np.abs(shift) > 0, zn, z)
    return Xn, float(np.abs(shift).max())


def make_mat_fn(g, breaks, geom):
    base = wf.make_mat_fn(g)
    if geom != "d68":
        return base
    bx0, bx1 = g["blk_x"]
    by0, by1 = face_y(breaks, g["blk_y"][0]), face_y(breaks, g["blk_y"][1])

    def fn(x, z, y):
        m = base(x, z, y)
        if m != FOAM or not (bx0 <= x <= bx1):
            return m
        dy = by0 - y if y < by0 else (y - by1 if y > by1 else -1.0)
        if dy < 0:
            return m
        ds = min(zu(x) - z, z - zl(x))
        if ds >= 0 and dy + ds <= BEAD_LEG:
            return BEAD
        return m
    return fn


# ------------------------------------------------------------------------------------------------ global model
def global_solve(g, msets, cases, intro_list, extra_planes):
    t0 = time.time()
    orig = wf.span_breaks
    br = breaks_with(g, extra_planes)
    wf.span_breaks = lambda g_: br
    try:
        model = wf.build(GLOBAL_LEVEL, g)
    finally:
        wf.span_breaks = orig
    X, blocks, mk = model["X"], model["blocks"], model["markers"]
    root = sorted({n for _, nd in mk["root"] for n in nd})
    E, nu = msets["O"]
    K = sf.assemble(X, blocks, E, nu)
    pc = wfd.TwoLevelPCG(K, X, model["ys"], root, (g["xs"], g["zs"]))
    print(f"global L{GLOBAL_LEVEL}: {model['stats']['nodes']} nodes, {pc.ndof:,} dofs, setup {time.time() - t0:.0f} s",
          flush=True)
    out = {}
    for intro in intro_list:
        for cs in cases:
            tr, chk = wf.tractions(model, cases[cs]["rows"], g["xs"], intro=intro)
            f = sf.traction_vector(X, mk, tr)
            U, sol = pc.solve(f)
            R_, F_ = wfd.reactions_check(K, U, root, f)
            planes = {}
            for yc in extra_planes:
                sel = np.abs(X[:, 1] - yc) < 1e-9
                planes[yc] = (X[sel][:, [0, 2]], U[sel])
            out[(intro, cs)] = {"tractions": {n: (tx, ty, tz) for n, tx, ty, tz in tr}, "planes": planes,
                                "tip_w_mm": float(U[np.abs(X[:, 1] - X[:, 1].max()) < 1e-9, 2].mean() * 1e3),
                                "cg_iter": sol["cg_iter"], "rel_residual": sol["rel_residual"],
                                "root_reaction_N": R_, "applied_N": F_}
            print(f"  global {intro} {cs[0]}: CG {sol['cg_iter']} it, res {sol['rel_residual']:.1e}, "
                  f"tip w {out[(intro, cs)]['tip_w_mm']:.3f} mm", flush=True)
    del pc, K
    return out, model["strips"], br, {"nodes": model["stats"]["nodes"], "level": GLOBAL_LEVEL,
                                      "setup_and_solve_s": round(time.time() - t0, 1)}


# ------------------------------------------------------------------------------------------------ local model
def local_layers(br_local, cs, h, y_c0, y_c1):
    """Span layers: fine (h) within the corner zones, HY_BASE elsewhere; every break kept."""
    zones = []
    pts = set(br_local)
    for x0, y0, sx, sy, R, *_ in cs:
        lo, hi = sorted((y0 - sy * 2 * R, y0 + sy * R))
        zones.append((lo - 0.0015, hi + 0.0015))
        pts.update([y0, y0 + sy * R, y0 - sy * 2 * R])
    pts.update(v for z_ in zones for v in z_)
    # bead: y0 - 3 mm / y1 + 3 mm are inside the pocket zones already
    pts = sorted(p for p in pts if y_c0 <= p <= y_c1)
    clean = [pts[0]]
    for v in pts[1:]:
        if v - clean[-1] > 0.0002:
            clean.append(v)
    ys = [clean[0]]
    for a, b_ in zip(clean[:-1], clean[1:]):
        fine = any(lo - 1e-9 <= 0.5 * (a + b_) <= hi + 1e-9 for lo, hi in zones)
        n = max(1, math.ceil((b_ - a) / (h if fine else HY_BASE) - 1e-9))
        ys.extend(np.linspace(a, b_, n + 1)[1:])
    return np.array(ys)


def local_build(g, h, strips, br_all, cuts, geom):
    y_c0, y_c1 = cuts
    p = wf.LEVELS[2]
    bx0, bx1 = g["blk_x"]
    xh = g["xh"]
    cs_all = corners(g, br_all)
    cs = cs_all if geom == "d68" else []
    d = 2.5 * R_POCKET + 0.001
    zb = lambda x: (float(zl(x)) - 0.001, float(zu(x)) + 0.001)
    boxes = [(bx0 - d, bx0 + d, -0.02, 0.03, h, 0.004),
             (bx1 - d, bx1 + d, -0.02, 0.03, h, 0.004),
             (xh - d, xh + d, -0.02, 0.03, h, 0.004)]
    # skin over the pocket (bead), in 6 chordwise boxes that follow the surface 5 mm deep
    xe = np.linspace(bx0, bx1, 7)
    for a, b_ in zip(xe[:-1], xe[1:]):
        xx = np.linspace(a, b_, 9)
        boxes.append((a, b_, float(zu(xx).min()) - 0.005, float(zu(xx).max()) + 0.001, h, 0.003))
        boxes.append((a, b_, float(zl(xx).min()) - 0.001, float(zl(xx).max()) + 0.005, h, 0.003))
    nodes2d, elems2d, on_out = sf.section_mesh(wf.outline_poly(), wf.cut_lines(g), (g["xs"], g["zs"], [g["ri"], g["rs"]]),
                                               p["nth"], p["nr"], p["h_near"], p["h_far"], boxes=boxes)
    br_local = [b_ for b_ in br_all if y_c0 - 1e-12 <= b_ <= y_c1 + 1e-12]
    ys = local_layers(br_local, cs_all, h, y_c0, y_c1)
    X, blocks, _, _ = sf.extrude(nodes2d, elems2d, ys, make_mat_fn(g, br_all, geom))
    outline_flag = np.tile(on_out, len(ys))
    X, blocks, used = sf.compact(X, blocks)
    outline_flag = outline_flag[used]
    max_shift = 0.0
    X0 = X.copy()                      # patch classification on the unshifted mesh (same patches as the global model)
    if cs:
        X, max_shift = morph(X, cs, tube=(g["xs"], g["zs"], g["rs"]))
    vols = sf.element_volumes(X, blocks)
    faces = sf.boundary_faces(blocks)
    zc_of = lambda x: 0.5 * (zu(x) + zl(x))
    mk = {"cut0": [], "cut1": []}
    for ft, nd in faces:
        P = X0[list(nd)]
        if np.all(np.abs(P[:, 1] - y_c0) < 1e-9):
            mk["cut0"].append((ft, nd))
            continue
        if np.all(np.abs(P[:, 1] - y_c1) < 1e-9):
            mk["cut1"].append((ft, nd))
            continue
        if np.all(outline_flag[list(nd)]) and np.ptp(P[:, 1]) > 0:
            cx, cy, cz = P.mean(0)
            k = next(i for i, (a, b_) in enumerate(strips) if a - 1e-12 <= cy <= b_ + 1e-12)
            key = f"S{k:02d}{'U' if cz >= zc_of(cx) else 'L'}{'F' if cx < g['xs'] else 'A'}{wf.hard_class(g, strips[k], cx)}"
            mk.setdefault(key, []).append((ft, nd))
    mats = np.concatenate([m for _, _, m in blocks])
    stats = {"h_local_mm": h * 1e3, "section_nodes": int(len(nodes2d)), "layers": int(len(ys) - 1),
             "nodes": int(len(X)), "elements": int(len(mats)), "bead_elements": int((mats == BEAD).sum()),
             "min_signed_volume": float(vols.min()), "max_morph_shift_mm": max_shift * 1e3, "cuts": list(cuts)}
    return {"X": X, "blocks": blocks, "markers": mk, "ys": ys, "stats": stats, "corners": cs_all}


def interp_plane(XZg, Ug, XZl):
    from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
    lin = LinearNDInterpolator(XZg, Ug)
    v = lin(XZl)
    bad = np.isnan(v).any(1)
    if bad.any():
        v[bad] = NearestNDInterpolator(XZg, Ug)(XZl[bad])
    return v, int(bad.sum())


def element_stress(X, U, blocks, E, nu):
    """Per element: centroid, volume, material, s1, s3, tau_max, von Mises (centroid strain; tube axial-modulus
    recovery as in wing_fea.post)."""
    recs = []
    for vtk, conn, m in blocks:
        eps = sf.centroid_strain(X, U, vtk, conn)
        cen = X[conn].mean(1)
        vol = np.abs(sf.element_volumes(X, [(vtk, conn, m)]))
        for mid in np.unique(m):
            sel = m == mid
            s = sf.hooke(eps[sel], E[mid], nu[mid])
            ev = np.linalg.eigvalsh(s)
            vm = np.sqrt(0.5 * ((ev[:, 0] - ev[:, 1]) ** 2 + (ev[:, 1] - ev[:, 2]) ** 2 + (ev[:, 2] - ev[:, 0]) ** 2))
            recs.append(np.column_stack([cen[sel], vol[sel], np.full(sel.sum(), mid), ev[:, 2], ev[:, 0],
                                         0.5 * (ev[:, 2] - ev[:, 0]), vm]))
    return np.vstack(recs)       # cols: x y z vol mat s1 s3 tau vm


def zone_peaks(R, g, cs, cuts):
    y_c0, y_c1 = cuts
    ok = (R[:, 1] > y_c0 + CLIP) & (R[:, 1] < y_c1 - CLIP)
    R = R[ok]
    bx0, bx1 = g["blk_x"]
    by0, by1 = g["blk_y"]
    m = 0.008
    zones = {"pocket": (R[:, 0] > bx0 - m) & (R[:, 0] < bx1 + m) & (R[:, 1] > by0 - m) & (R[:, 1] < by1 + m),
             "cutout": (R[:, 0] > g["xh"] - m) & (R[:, 0] < g["xh"] + m) & (R[:, 1] > g["spans"][0][1] - m)
             & (R[:, 1] < g["spans"][1][0] + m),
             "all": np.ones(len(R), bool)}
    out = {}
    for zn, zsel in zones.items():
        for mat, name in ((FOAM, "foam"), (BEAD, "bead"), (PETG, "petg")):
            S = R[zsel & (R[:, 4] == mat)]
            if not len(S):
                continue
            d = {}
            for col, key, fn in ((5, "s1", np.argmax), (6, "s3", np.argmin), (7, "tau", np.argmax), (8, "vm", np.argmax)):
                i = int(fn(S[:, col]))
                d[key + "_pa"] = float(S[i, col])
                d[key + "_at"] = S[i, :3].tolist()
                if mat == FOAM:
                    # volume average over a sphere of radius AVG_R round the peak element (same material)
                    near = np.linalg.norm(S[:, :3] - S[i, :3], axis=1) <= AVG_R
                    d[key + "_avg_pa"] = float(np.sum(S[near, col] * S[near, 3]) / np.sum(S[near, 3]))
                    d[key + "_avg_n"] = int(near.sum())
            out[f"{zn}/{name}"] = d
    return out


def local_solve(model, E, nu, glob, cases_sel, cuts):
    X, blocks, mk = model["X"], model["blocks"], model["markers"]
    t0 = time.time()
    K = sf.assemble(X, blocks, E, nu)
    nodes_c = {c: sorted({n for _, nd in mk[f"cut{i}"] for n in nd}) for i, c in enumerate(cuts)}
    fixed = sorted(set(nodes_c[cuts[0]]) | set(nodes_c[cuts[1]]))
    pc = wfd.TwoLevelPCG(K, X, model["ys"], fixed, (0.08, 0.0066))
    t_set = time.time() - t0
    res = {}
    for key in cases_sel:
        g_ = glob[key]
        up = np.zeros((len(X), 3))
        n_near = 0
        for c in cuts:
            ids = np.array(nodes_c[c])
            XZg, Ug = g_["planes"][c]
            v, nb = interp_plane(XZg, Ug, X[ids][:, [0, 2]])
            up[ids] = v
            n_near += nb
        tr = [(n, *g_["tractions"].get(n, (0.0, 0.0, 0.0))) for n in mk if n.startswith("S")]
        missing = [n for n in mk if n.startswith("S") and n not in g_["tractions"]]
        f = sf.traction_vector(X, mk, tr)
        f_eff = f - K @ up.ravel()
        t1 = time.time()
        du, sol = pc.solve(f_eff)
        U = du + up
        # equilibrium: reactions on the two cut planes + applied skin load = 0
        Rv = (K @ U.ravel() - f).reshape(-1, 3)
        r_sum = Rv[fixed].sum(0) + f.reshape(-1, 3).sum(0)
        Rr = element_stress(X, U, blocks, E, nu)
        res[key] = {"solve_s": round(time.time() - t1, 1), **sol, "plane_nodes_outside_hull": n_near,
                    "patches_without_global_traction": missing, "applied_N": f.reshape(-1, 3).sum(0).tolist(),
                    "equilibrium_residual_N": r_sum.tolist(), "peaks": zone_peaks(Rr, G, model["corners"], cuts)}
        pk = res[key]["peaks"].get("pocket/foam", {})
        pc_ = res[key]["peaks"].get("cutout/foam", {})
        print(f"    {key[0]} {key[1][0]}: CG {sol['cg_iter']} it res {sol['rel_residual']:.1e}; pocket foam s1 "
              f"{pk.get('s1_pa', 0) / 1e3:.1f} (avg {pk.get('s1_avg_pa', 0) / 1e3:.1f}) s3 {pk.get('s3_pa', 0) / 1e3:.1f} "
              f"tau {pk.get('tau_pa', 0) / 1e3:.1f} kPa at {np.round(pk.get('s1_at', [0, 0, 0]), 4).tolist()}; "
              f"cutout foam s1 {pc_.get('s1_pa', 0) / 1e3:.1f} tau {pc_.get('tau_pa', 0) / 1e3:.1f} kPa; "
              f"eq {np.abs(r_sum).max():.2e} N", flush=True)
    del pc, K
    return res, round(t_set, 1)


G = None


def setup():
    g = wf.d1_geometry()
    msets = dict(wf.materials(g))
    Eb, nub = msets["B"]
    tube = {"Ea": ws.M["spar_E_lo_pa"], "Et": 8.0e9, "Gat": ws.M["spar_G_lo_pa"], "nu_at": 0.30, "nu_tt": 0.40,
            "center": (g["xs"], g["zs"])}
    E = [Eb[0], tube, Eb[2], BEAD_E]
    nu = [nub[0], nub[1], nub[2], BEAD_NU]
    msets["O"] = ([Eb[0], tube, Eb[2]], list(nub))
    return g, msets, E, nu


CASE_SETS = {"block": [cs for cs in wf.CASES],
             "distributed": [cs for cs in wf.CASES if cs[0] in ("L4-CORNER-SIDE-Y", "G2-HANG-MOTOR")]}


def phase_global(intro):
    """One process per load introduction; caches the cut-plane displacements and the patch tractions."""
    import pickle
    g, msets, E, nu = setup()
    cases = ws.read_spanwise()
    sel = {cs: cases[cs] for cs in CASE_SETS[intro]}
    planes = sorted(set(CUTS) | set(CUTS_NEAR))
    glob, strips, br_all, gstats = global_solve(g, msets, sel, [intro], planes)
    with open(OUT / f"d68_global_{intro}.pkl", "wb") as f:
        pickle.dump({"glob": glob, "strips": strips, "br_all": br_all, "stats": gstats}, f)
    print("global done", intro, flush=True)


def phase_local(job):
    """job = 'd68/1', 'asdrawn/3', 'd68/2/near'."""
    import pickle
    global G
    g, msets, E, nu = setup()
    G = g
    glob = {}
    gstats = {}
    for intro in ("block", "distributed"):
        with open(OUT / f"d68_global_{intro}.pkl", "rb") as f:
            d = pickle.load(f)
        glob.update(d["glob"])
        strips, br_all = d["strips"], d["br_all"]
        gstats[intro] = d["stats"]
    parts = job.split("/")
    geom, lev = parts[0], int(parts[1])
    cuts = CUTS_NEAR if len(parts) > 2 and parts[2] == "near" else CUTS
    tag = f"{geom}/L{lev}" + ("" if cuts == CUTS else "/near")
    t0 = time.time()
    model = local_build(g, LOCAL_H[lev], strips, br_all, cuts, geom)
    print(f"local {tag}: {model['stats']}", flush=True)
    full = geom == "d68" and cuts == CUTS
    sel = [(intro, cs) for intro in ("block", "distributed") for cs in CASE_SETS[intro]
           if full or (intro == "block" and cs[0] in ("L4-CORNER-SIDE-Y", "G2-HANG-MOTOR"))]
    runs, t_set = local_solve(model, E, nu, glob, sel, cuts)
    rec = {"tag": tag, "stats": {**model["stats"], "setup_s": t_set, "wall_s": round(time.time() - t0, 1)},
           "runs": {f"{k[0]}/{k[1][0]}/{k[1][1]}": v for k, v in runs.items()},
           "global": {intro: {**gstats[intro], "runs": {f"{k[0]}/{k[1][0]}/{k[1][1]}": {kk: v[kk] for kk in (
               "tip_w_mm", "cg_iter", "rel_residual", "root_reaction_N", "applied_N")} for k, v in glob.items()
               if k[0] == intro}} for intro in gstats}}
    (OUT / f"d68_local_{tag.replace('/', '_')}.json").write_text(json.dumps(rec, indent=1, default=float))
    print("local done", tag, flush=True)


def phase_merge(out_name="d68_submodel.json"):
    result = {"inputs": {"geometry_source": "team/D1/wing_data.py -> subsystems/wing/fusion/wing.py (D1-R1) + D-68 "
                                            "as decided (R 3 mm pocket edges, 3 mm bead, R 3 mm cut-out corners)",
                         "loads": "team/C1/data/wing_spanwise.csv (C1-R4)", "material_set": "O (orthotropic tube)",
                         "E_bead_pa": BEAD_E, "nu_bead": BEAD_NU, "R_pocket_m": R_POCKET, "R_cutout_m": R_CUT,
                         "bead_leg_m": BEAD_LEG, "cuts_m": list(CUTS), "cuts_near_m": list(CUTS_NEAR),
                         "local_h_m": LOCAL_H, "clip_m": CLIP, "avg_radius_m": AVG_R, "global_level": GLOBAL_LEVEL},
              "local": {}}
    for f in sorted(OUT.glob("d68_local_*.json")):
        r = json.loads(f.read_text())
        result["local"][r["tag"]] = {"stats": r["stats"], "runs": r["runs"]}
        result["global"] = r["global"]
    (OUT / out_name).write_text(json.dumps(result, indent=1, default=float))
    print("merged", sorted(result["local"]))


def main_phased():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["global", "local", "merge", "all"], default="all")
    ap.add_argument("--intro", default="block")
    ap.add_argument("--job", default="d68/1")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.phase == "global":
        phase_global(a.intro)
    elif a.phase == "local":
        phase_local(a.job)
    elif a.phase == "merge":
        phase_merge()
    else:
        main()


def main():
    global G
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--geoms", nargs="+", default=["d68", "asdrawn"])
    ap.add_argument("--no-cut-check", action="store_true")
    ap.add_argument("--out", default="d68_submodel.json")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    g = wf.d1_geometry()
    G = g
    msets = dict(wf.materials(g))
    Eb, nub = msets["B"]
    tube = {"Ea": ws.M["spar_E_lo_pa"], "Et": 8.0e9, "Gat": ws.M["spar_G_lo_pa"], "nu_at": 0.30, "nu_tt": 0.40,
            "center": (g["xs"], g["zs"])}
    E = [Eb[0], tube, Eb[2], BEAD_E]
    nu = [nub[0], nub[1], nub[2], BEAD_NU]
    msets["O"] = ([Eb[0], tube, Eb[2]], list(nub))          # as wing_fea_direct.py set O
    cases = ws.read_spanwise()
    planes = sorted(set(CUTS) | set(CUTS_NEAR))
    glob, strips, br_all, gstats = global_solve(g, msets, cases, ["block", "distributed"], planes)
    pth = OUT / a.out
    result = {"inputs": {"geometry_source": "team/D1/wing_data.py -> subsystems/wing/fusion/wing.py (D1-R1) + D-68 "
                                            "as decided (R 3 mm pocket edges, 3 mm bead, R 3 mm cut-out corners)",
                         "loads": "team/C1/data/wing_spanwise.csv (C1-R4)", "material_set": "O (orthotropic tube)",
                         "E": [E[0], "tube", E[2], E[3]], "nu": nu, "R_pocket_m": R_POCKET, "R_cutout_m": R_CUT,
                         "bead_leg_m": BEAD_LEG, "cuts_m": list(CUTS), "cuts_near_m": list(CUTS_NEAR),
                         "local_h_m": LOCAL_H, "clip_m": CLIP, "avg_radius_m": AVG_R},
              "global": {**gstats, "runs": {f"{k[0]}/{k[1][0]}/{k[1][1]}": {kk: v[kk] for kk in
                                                                              ("tip_w_mm", "cg_iter", "rel_residual",
                                                                               "root_reaction_N", "applied_N")}
                                             for k, v in glob.items()}},
              "local": {}}
    case_all = [("block", cs) for cs in wf.CASES] + [("distributed", cs) for cs in wf.CASES
                                                     if cs[0] in ("L4-CORNER-SIDE-Y", "G2-HANG-MOTOR")]
    jobs = [(geom, lev, CUTS) for geom in a.geoms for lev in a.levels]
    if not a.no_cut_check and "d68" in a.geoms:
        jobs.append(("d68", 2, CUTS_NEAR))
    for geom, lev, cuts in jobs:
        tag = f"{geom}/L{lev}" + ("" if cuts == CUTS else "/near")
        t0 = time.time()
        model = local_build(g, LOCAL_H[lev], strips, br_all, cuts, geom)
        print(f"local {tag}: {model['stats']}", flush=True)
        sel = case_all if (geom == "d68" and cuts == CUTS) else [("block", cs) for cs in wf.CASES
                                                                  if cs[0] in ("L4-CORNER-SIDE-Y", "G2-HANG-MOTOR")]
        runs, t_set = local_solve(model, E, nu, glob, sel, cuts)
        result["local"][tag] = {"stats": {**model["stats"], "setup_s": t_set, "wall_s": round(time.time() - t0, 1)},
                                "runs": {f"{k[0]}/{k[1][0]}/{k[1][1]}": v for k, v in runs.items()}}
        pth.write_text(json.dumps(result, indent=1, default=float))
    print("done")


if __name__ == "__main__":
    main_phased()
