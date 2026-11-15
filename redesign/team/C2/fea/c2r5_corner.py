"""C2-R5 (design round 2026-11-14): block-pocket corner fail (CL-C2-FEA-FOAM-CORNER-*), measure and fixes.

Imports the D-68 global-local submodel (wing_fea_d68.py) unchanged and adds:
  1. a field dump: every element within the pocket zone (centroid, volume, material, s1, s3, tau) to an .npz, so the
     corner stress can be read with any measure afterwards (c2r5_measure.py) without another solve;
  2. design variants built into the local model:
     base    the D-68 geometry as in wing_fea_d68 (R 3 mm block edges, 3 mm microballoon bead), for the measure study;
     band    a woven-glass/epoxy doubler band on the skin: an offset layer t_model thick inside the outline, from the
             upper surface at x = band_x round the LE to the lower surface at x = band_x, spanwise over the block
             +/- band_dy. Isotropic E_eq = (E t)_laminate / t_model, so the layer has the laminate's membrane stiffness;
     collar  a denser-foam collar of plan-view width collar_m round the block pocket (full depth), E collar_E.
  3. optional wider cut planes (0.255 / 0.385 m) from a new global solve (phase "global"), so the band ends sit >= 22 mm
     from the cuts.
Writes only in team/C2/fea/out/c2r5/ (or --out-dir). Nothing shared is edited.

Wave 2 (D-153, 2026-11-14) options: --geom d68g builds the local model with the ESC-lead grooves and open slot seams
(-CUTS case); the tape skin layer is kept over the removed foam (the as-drawn skin bridges the grooves and seams:
subsystems/harness/SPEC.md "tape tabs, then the skin"; team/C2/sizing.json "tape continuous over the spar slot").
--global-pkl reads another global solve (the G 4.31 GPa one: out/d68_global_block_g431.pkl, with C2_TUBE_G=4.31e9
in the environment so the local tube matches). --dump-servo widens the field dump to the lower-skin servo-pocket
opening (subsystems/wing/params.json servo_pocket). --out-dir keeps new runs out of the repo.

Run (repo root):
  python -I redesign/team/C2/fea/c2r5_corner.py global                      (wide-cut global, block intro, ~15 min)
  python -I redesign/team/C2/fea/c2r5_corner.py local --variant base --level 1 [--cuts narrow|wide] [--cases L4 G2]
  python -I redesign/team/C2/fea/c2r5_corner.py local --variant band --level 2 --cuts wide --Et 2.8e6 ...
"""
import argparse
import json
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import wing_fea_d68 as d6          # noqa: E402
import wing_fea as wf              # noqa: E402
import su2fea as sf                # noqa: E402
import wing_struct as ws           # noqa: E402

OUT = HERE / "out" / "c2r5"
FOAM, CF, PETG, BEAD, GLASS, COLLAR, DBL = 0, 1, 2, 3, 4, 5, 6
WIDE = (0.255, 0.385)
CASE_KEYS = {"L4": ("L4-CORNER-SIDE-Y", "MC-C"), "G2": ("G2-HANG-MOTOR", "MC-P"),
             "L1": ("L1-LEVEL", "MC-C"), "F1": ("F1-PULLUP-VD", "MC-C")}
DUMP_M = 0.030          # dump elements within this plan-view distance of the block footprint


def phase_global(a):
    """Global solve, block intro. --variant base: planes at WIDE (cut-plane sensitivity). --variant band with
    --band-y0: the band built into the global model too (a band that runs to the root changes the global torsion
    path, so the local model needs a global solution that has it); planes at the standard cuts."""
    g, msets, E, nu = d6.setup()
    cases = ws.read_spanwise()
    sel = {cs: cases[cs] for cs in wf.CASES}
    variant = Variant(a)
    if a.variant == "base":
        planes, name = list(WIDE), "global_block_wide.pkl"
    else:
        planes = sorted(set(d6.CUTS) | set(d6.CUTS_NEAR) | set(variant.extra_planes(g)))
        name = f"global_block_{a.tag}.pkl"
    E6 = [E[0], msets["O"][0][1], E[2], E[3], a.Et / a.t_model, a.collar_E]
    nu6 = list(nu) + [0.30, 0.30]
    msets["O"] = (E6, nu6)
    h = wf.LEVELS[d6.GLOBAL_LEVEL]["h_near"]
    orig_mesh, orig_mat = sf.section_mesh, wf.make_mat_fn

    def mesh_patch(outline, cuts_, circles, *args, boxes=(), **kw):
        return orig_mesh(outline, list(cuts_) + variant.extra_lines(g), circles, *args,
                         boxes=list(boxes) + variant.boxes(g, h), **kw)

    sf.section_mesh = mesh_patch
    wf.make_mat_fn = lambda g_: variant.wrap(orig_mat(g_), g_)
    try:
        glob, strips, br_all, gstats = d6.global_solve(g, msets, sel, ["block"], planes)
    finally:
        sf.section_mesh, wf.make_mat_fn = orig_mesh, orig_mat
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / name, "wb") as f:
        pickle.dump({"glob": glob, "strips": strips, "br_all": br_all, "stats": gstats}, f)
    print("global done", name, gstats, flush=True)


# ------------------------------------------------------------------------------------------------ variant geometry
def outline_dense(step=2.5e-4):
    P = wf.outline_poly()
    P = np.vstack([P, P[:1]])
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = np.arange(0, s[-1], step)
    return np.stack([np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])], 1)


def band_lines(xb, t):
    """Offset polyline t inside the outline for x <= xb (upper -> LE -> lower), clipped at x = xb, plus the two
    closing segments at x = xb (overhanging the outline)."""
    P = wf.outline_poly()             # CCW or CW; recompute inward normals from the signed area
    area = 0.5 * (P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]).sum()
    if area < 0:
        P = P[::-1]                    # CCW: inward normal = left of the tangent
    n = len(P)
    tg = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    tg /= np.linalg.norm(tg, axis=1)[:, None]
    nin = np.stack([-tg[:, 1], tg[:, 0]], 1)
    Q = P + t * nin
    # walk the CCW loop starting at the point with x > xb on the lower surface... simpler: take the run of points with
    # x <= xb that contains the LE (min x)
    i_le = int(np.argmin(P[:, 0]))
    inside = P[:, 0] <= xb
    idx = [i_le]
    j = i_le
    while inside[(j - 1) % n]:
        j = (j - 1) % n
        idx.insert(0, j)
    j = i_le
    while inside[(j + 1) % n]:
        j = (j + 1) % n
        idx.append(j)
    pts = Q[idx]
    # extend each end to x = xb along the offset polyline direction
    ends = []
    for a, b_ in ((idx[0], (idx[0] - 1) % n), (idx[-1], (idx[-1] + 1) % n)):
        qa, qb = Q[a], Q[b_]
        f = (xb - qa[0]) / (qb[0] - qa[0])
        ends.append(qa + f * (qb - qa))
    pts = np.vstack([ends[0], pts, ends[1]])
    keep = np.concatenate([[True], np.linalg.norm(np.diff(pts, axis=0), axis=1) > 2e-5])
    pts = pts[keep]
    lines = [((float(pts[i, 0]), float(pts[i, 1])), (float(pts[i + 1, 0]), float(pts[i + 1, 1])))
             for i in range(len(pts) - 1)]
    for e in ends:
        zs = float(d6.zu(xb)) if e[1] > 0.5 * (float(d6.zu(xb)) + float(d6.zl(xb))) else float(d6.zl(xb))
        over = zs + (0.001 if zs > e[1] else -0.001)
        lines.append(((xb, float(e[1])), (xb, over)))
    return lines


class Variant:
    def __init__(self, a):
        self.a = a
        self.kind = a.variant
        self._dist_cache = {}
        self._dense = outline_dense()

    def dist_out(self, x, z):
        k = (round(x, 7), round(z, 7))
        v = self._dist_cache.get(k)
        if v is None:
            v = float(np.min(np.hypot(self._dense[:, 0] - x, self._dense[:, 1] - z)))
            self._dist_cache[k] = v
        return v

    def extra_planes(self, g):
        by0, by1 = g["blk_y"]
        if self.kind == "band":
            pl = [p for p in (self.y0(g), by1 + self.a.band_dy) if p > 1e-6]
            if self.a.dbl_mult > 0:
                pl += list(self.a.dbl_y)
            return pl
        if self.kind == "collar":
            return [by0 - self.a.collar_m, by1 + self.a.collar_m]
        return []

    def y0(self, g):
        return g["blk_y"][0] - self.a.band_dy if self.a.band_y0 is None else self.a.band_y0

    def extra_lines(self, g):
        if self.kind == "band":
            L = band_lines(self.a.band_x, self.a.t_model)
            if self.a.dbl_mult > 0:
                xd = self.a.dbl_x
                for zs in (float(d6.zu(xd)), float(d6.zl(xd))):
                    sg = 1 if zs > 0.005 else -1
                    L.append(((xd, zs + sg * 0.001), (xd, zs - sg * 3 * self.a.t_model)))
            return L
        if self.kind == "collar":
            bx0, bx1 = g["blk_x"]
            m = self.a.collar_m
            return [((bx0 - m, -0.03), (bx0 - m, 0.04)), ((bx1 + m, -0.03), (bx1 + m, 0.04))]
        return []

    def boxes(self, g, h):
        if self.kind == "band":
            xb = self.a.band_x
            hb = max(h, 0.0012)
            xx = np.linspace(0, xb, 40)
            return [(-0.001, xb + 0.003, float(d6.zu(xx).min()) - 0.002, float(d6.zu(xx).max()) + 0.001, hb, 0.003),
                    (-0.001, xb + 0.003, float(d6.zl(xx).min()) - 0.001, float(d6.zl(xx).max()) + 0.002, hb, 0.003),
                    (-0.001, 0.006, -0.01, 0.015, hb, 0.003),
                    (xb - 0.003, xb + 0.003, -0.02, 0.03, h, 0.003)]
        if self.kind == "collar":
            bx0, bx1 = g["blk_x"]
            m = self.a.collar_m
            return [(bx0 - m - 0.004, bx0 - m + 0.004, -0.02, 0.03, h, 0.003),
                    (bx1 + m - 0.004, bx1 + m + 0.004, -0.02, 0.03, h, 0.003)]
        return []

    def wrap(self, base, g, ref=None):
        """ref: the d68 material function when base is d68g; where d68g removed foam (grooves, open seams) inside
        the skin layer, the skin is kept (it bridges the cut, as built)."""
        if self.kind == "base":
            return base
        bx0, bx1 = g["blk_x"]
        by0, by1 = g["blk_y"]
        a = self.a

        def fn(x, z, y):
            m = base(x, z, y)
            if m is None and ref is not None and self.kind == "band":
                m = ref(x, z, y)
                if m is None or m == CF or not (self.y0(g) <= y <= by1 + a.band_dy and x <= a.band_x
                                                 and self.dist_out(x, z) <= a.t_model):
                    return None
            if m is None or m == CF:
                return m
            if self.kind == "band":
                if self.y0(g) <= y <= by1 + a.band_dy and x <= a.band_x and self.dist_out(x, z) <= a.t_model:
                    if a.dbl_mult > 0 and a.dbl_y[0] <= y <= a.dbl_y[1] and x <= a.dbl_x:
                        return DBL
                    return GLASS
                return m
            if self.kind == "collar":
                if m == FOAM and bx0 - a.collar_m <= x <= bx1 + a.collar_m and by0 - a.collar_m <= y <= by1 + a.collar_m:
                    return COLLAR
                return m
            return m
        return fn


def zone_fine(variant, g, h):
    """Extra fine span zones (y0, y1) at the variant's spanwise edges."""
    return [(p - 0.003, p + 0.003) for p in variant.extra_planes(g)]


# ------------------------------------------------------------------------------------------------ local run
def run_local(a):
    g, msets, E, nu = d6.setup()
    d6.G = g
    variant = Variant(a)
    # skin layer = the foam it replaces plus the laminate / tape membrane stiffness spread over t_model
    E = list(E) + [E[0] + a.Et / a.t_model, a.collar_E, E[0] + a.Et * max(a.dbl_mult, 1.0) / a.t_model]
    nu = list(nu) + [0.30, 0.30, 0.30]
    if a.global_pkl:
        with open(a.global_pkl, "rb") as f:
            d = pickle.load(f)
        glob, strips, br_all = d["glob"], d["strips"], d["br_all"]
        cuts = d6.CUTS
    elif a.global_tag:
        with open(OUT / f"global_block_{a.global_tag}.pkl", "rb") as f:
            d = pickle.load(f)
        glob, strips, br_all = d["glob"], d["strips"], d["br_all"]
        cuts = d6.CUTS
    elif a.cuts == "wide":
        with open(OUT / "global_block_wide.pkl", "rb") as f:
            d = pickle.load(f)
        glob, strips, br_all = d["glob"], d["strips"], d["br_all"]
        cuts = WIDE
    else:
        with open(d6.OUT / "d68_global_block.pkl", "rb") as f:
            d = pickle.load(f)
        glob, strips, br_all = d["glob"], d["strips"], d["br_all"]
        cuts = d6.CUTS
    br_all = sorted(set(br_all) | set(variant.extra_planes(g)))
    if a.intro != "block":            # closure round: e.g. "c4split" (fin root fillet split, wing_fea.py), patch classes
        d6.wf.INTRO = a.intro
    h = d6.LOCAL_H[a.level]
    # patch the section mesher (extra lines, boxes), the material function and the span layering
    orig_mesh, orig_mat, orig_layers = sf.section_mesh, d6.make_mat_fn, d6.local_layers

    def mesh_patch(outline, cuts_, circles, *args, boxes=(), **kw):
        return orig_mesh(outline, list(cuts_) + variant.extra_lines(g), circles, *args,
                         boxes=list(boxes) + variant.boxes(g, h), **kw)

    def mat_patch(g_, breaks, geom):
        ref = orig_mat(g_, breaks, "d68") if geom == "d68g" else None
        return variant.wrap(orig_mat(g_, breaks, geom), g_, ref)

    def layers_patch(br_local, cs, h_, y_c0, y_c1):
        ys = orig_layers(br_local, cs, h_, y_c0, y_c1)
        extra = []
        for lo, hi in zone_fine(variant, g, h_):
            lo, hi = max(lo, y_c0), min(hi, y_c1)
            if hi > lo:
                extra.extend(np.linspace(lo, hi, max(2, math.ceil((hi - lo) / h_)) + 1))
        if not extra:
            return ys
        allp = np.unique(np.round(np.concatenate([ys, extra]), 9))
        out = [allp[0]]
        for v in allp[1:]:
            if v - out[-1] > 0.0002:
                out.append(v)
        return np.array(out)

    sf.section_mesh, d6.make_mat_fn, d6.local_layers = mesh_patch, mat_patch, layers_patch
    d6.sf.section_mesh = mesh_patch
    try:
        t0 = time.time()
        model = d6.local_build(g, h, strips, br_all, cuts, a.geom)
    finally:
        sf.section_mesh, d6.make_mat_fn, d6.local_layers = orig_mesh, orig_mat, orig_layers
    mats = np.concatenate([m for _, _, m in model["blocks"]])
    model["stats"].update({"glass_elements": int((mats == GLASS).sum()), "collar_elements": int((mats == COLLAR).sum())})
    print(f"local {a.variant} L{a.level} {a.cuts}: {model['stats']}  build {time.time() - t0:.0f} s", flush=True)
    sel = [(a.intro, CASE_KEYS[c]) for c in a.cases]
    res = solve_dump(model, E, nu, glob, sel, cuts, g, a)
    tag = a.tag or f"{a.variant}_L{a.level}_{a.cuts}"
    rec = {"tag": tag, "args": {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(a).items()}, "E": [e if not isinstance(e, dict) else "tube" for e in E], "nu": nu,
           "stats": {**model["stats"], "wall_s": round(time.time() - t0, 1)}, "runs": res}
    (a.out_dir / f"{tag}.json").write_text(json.dumps(rec, indent=1, default=float))
    print("done", tag, round(time.time() - t0, 1), "s", flush=True)


def solve_dump(model, E, nu, glob, cases_sel, cuts, g, a):
    X, blocks, mk = model["X"], model["blocks"], model["markers"]
    K = sf.assemble(X, blocks, E, nu)
    nodes_c = {c: sorted({n for _, nd in mk[f"cut{i}"] for n in nd}) for i, c in enumerate(cuts)}
    fixed = sorted(set(nodes_c[cuts[0]]) | set(nodes_c[cuts[1]]))
    pc = d6.wfd.TwoLevelPCG(K, X, model["ys"], fixed, (0.08, 0.0066))
    # nodes of the stiff (non-foam, non-tube) elements: distance reference for the critical-distance measures
    stiff_nodes = set()
    tube_nodes = set()
    for vtk, conn, m in blocks:
        for mid in (PETG, BEAD, GLASS, COLLAR, DBL):
            sel = m == mid
            if sel.any():
                stiff_nodes.update(np.unique(conn[sel]).tolist())
        sel = m == CF
        if sel.any():
            tube_nodes.update(np.unique(conn[sel]).tolist())
    from scipy.spatial import cKDTree
    tree = cKDTree(X[sorted(stiff_nodes)])
    ttree = cKDTree(X[sorted(tube_nodes)])
    bx0, bx1 = g["blk_x"]
    by0, by1 = g["blk_y"]
    out = {}
    for key in cases_sel:
        g_ = glob[key]
        up = np.zeros((len(X), 3))
        for c in cuts:
            ids = np.array(nodes_c[c])
            XZg, Ug = g_["planes"][c]
            v, _ = d6.interp_plane(XZg, Ug, X[ids][:, [0, 2]])
            up[ids] = v
        tr = [(n, *g_["tractions"].get(n, (0.0, 0.0, 0.0))) for n in mk if n.startswith("S")]
        f = sf.traction_vector(X, mk, tr)
        t1 = time.time()
        du, sol = pc.solve(f - K @ up.ravel())
        U = du + up
        Rv = (K @ U.ravel() - f).reshape(-1, 3)
        r_sum = Rv[fixed].sum(0) + f.reshape(-1, 3).sum(0)
        R = d6.element_stress(X, U, blocks, E, nu)
        ok = (R[:, 1] > cuts[0] + d6.CLIP) & (R[:, 1] < cuts[1] - d6.CLIP)
        dx = np.maximum(np.maximum(bx0 - R[:, 0], R[:, 0] - bx1), 0)
        dy = np.maximum(np.maximum(by0 - R[:, 1], R[:, 1] - by1), 0)
        near = np.hypot(dx, dy) <= DUMP_M
        if a.dump_servo:
            (sx0, sx1), (sy0, sy1) = g["sp_x"], g["sp_y"]
            sdx = np.maximum(np.maximum(sx0 - R[:, 0], R[:, 0] - sx1), 0)
            sdy = np.maximum(np.maximum(sy0 - R[:, 1], R[:, 1] - sy1), 0)
            near |= np.hypot(sdx, sdy) <= 0.015
        zone = ok & near & (R[:, 4] != CF)
        Z = R[zone]
        dist = tree.query(Z[:, :3])[0]
        dtube = ttree.query(Z[:, :3])[0]
        zsurf = np.minimum(d6.zu(Z[:, 0]) - Z[:, 2], Z[:, 2] - d6.zl(Z[:, 0]))
        name = f"{key[1][0]}"
        tag = a.tag or f"{a.variant}_L{a.level}_{a.cuts}"
        np.savez_compressed(a.out_dir / f"{tag}_{name}.npz", R=Z, dist=dist, dtube=dtube, zsurf=zsurf,
                            h=d6.LOCAL_H[a.level])
        pk = d6.zone_peaks(R, g, model["corners"], cuts)
        out[f"{key[0]}/{key[1][0]}/{key[1][1]}"] = {"solve_s": round(time.time() - t1, 1), **sol,
                                                     "equilibrium_residual_N": r_sum.tolist(), "peaks": pk}
        p = pk.get("pocket/foam", {})
        print(f"  {name}: CG {sol['cg_iter']} res {sol['rel_residual']:.1e} pocket foam s1 {p.get('s1_pa', 0)/1e3:.1f} "
              f"(avg {p.get('s1_avg_pa', 0)/1e3:.1f}) s3 {p.get('s3_pa', 0)/1e3:.1f} tau {p.get('tau_pa', 0)/1e3:.1f} kPa "
              f"at {np.round(p.get('s1_at', [0, 0, 0]), 4).tolist()} eq {np.abs(r_sum).max():.1e}", flush=True)
    del pc, K
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["global", "local"])
    ap.add_argument("--variant", default="base", choices=["base", "band", "collar"])
    ap.add_argument("--level", type=int, default=1)
    ap.add_argument("--cuts", default="narrow", choices=["narrow", "wide"])
    ap.add_argument("--cases", nargs="+", default=["L4"])
    ap.add_argument("--band-x", dest="band_x", type=float, default=0.12)
    ap.add_argument("--band-dy", dest="band_dy", type=float, default=0.025)
    ap.add_argument("--band-y0", dest="band_y0", type=float, default=None, help="inboard band end (0 = root)")
    ap.add_argument("--global-tag", dest="global_tag", default="", help="use out/c2r5/global_block_<tag>.pkl")
    ap.add_argument("--t-model", dest="t_model", type=float, default=0.35e-3)
    ap.add_argument("--Et", type=float, default=2.6e6, help="laminate membrane stiffness E*t, N/m")
    ap.add_argument("--collar-m", dest="collar_m", type=float, default=0.010)
    ap.add_argument("--collar-E", dest="collar_E", type=float, default=60e6)
    ap.add_argument("--dbl-mult", dest="dbl_mult", type=float, default=0.0,
                    help="skin doubler zone: E t multiplied by this inside dbl_y x [LE, dbl_x] (0 = none)")
    ap.add_argument("--dbl-y", dest="dbl_y", type=float, nargs=2, default=[0.29, 0.35])
    ap.add_argument("--dbl-x", dest="dbl_x", type=float, default=0.12)
    ap.add_argument("--tag", default="")
    ap.add_argument("--geom", default="d68", choices=["d68", "d68g"], help="d68g: grooves + open seams (-CUTS)")
    ap.add_argument("--global-pkl", dest="global_pkl", default="", help="global solve file (e.g. the G 4.31 one)")
    ap.add_argument("--intro", default="block", help="load introduction of the global solve read (closure round: c4split)")
    ap.add_argument("--dump-servo", dest="dump_servo", action="store_true",
                    help="also dump the elements within 15 mm of the servo-pocket opening")
    ap.add_argument("--out-dir", dest="out_dir", type=Path, default=OUT)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    if a.phase == "global":
        phase_global(a)
    else:
        run_local(a)


if __name__ == "__main__":
    main()
