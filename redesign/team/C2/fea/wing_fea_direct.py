"""C2 verification FEA, second-solver path: the SAME gmsh mesh, materials, loads and post-processing as wing_fea.py
(gmsh + SU2 ELASTICITY), solved with an in-house assembly of the same linear-elastic hexahedra and wedges
(su2fea.assemble, full Gauss integration) and preconditioned conjugate gradients to a 1e-10 relative residual.
Preconditioner (two-level additive Schwarz, built for a slender extruded mesh): exact sparse LU of every span layer
(one node plane each, all its dofs) + a coarse space of 12 section motions per layer (rigid body, in-plane affine,
camber, warping: the long-wavelength modes that make plain CG / SGS slow). SuperLU of the whole level-1 matrix (110 k dofs) did not finish in 20 min (band fill), so the
global direct solve is used only on the tube validation.

Why a second solver: SU2 8.5's FEA path is conjugate-gradient + ILU only. With a 7 000 : 1 stiffness contrast
(CF 70 GPa against XPS 10 MPa) and 0.33 mm tube-wall layers it needs tens of thousands of iterations per case; on
the shared design machine (about 30 other SU2 processes on 20 cores during this round) the level-3 runs would
take many hours each. The direct path factorises once per material set and back-substitutes every load case,
so it runs all three levels and all cases. SU2 is run on the validation tube and on the level-1 wing (same mesh
file), and the two solvers are compared there (wing_fea.json vs wing_fea_direct.json): that comparison is what
lets the direct results stand in for SU2 at levels 2 and 3.

Run:  python -I redesign/team/C2/fea/wing_fea_direct.py [--levels 1 2 3]
Writes team/C2/fea/out/wing_fea_direct.json.
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
import su2fea as sf          # noqa: E402
import wing_fea as wf        # noqa: E402
import wing_struct as ws     # noqa: E402

OUT = HERE / "out"


def tube_validation(level=2):
    """Same tube cantilever as wing_fea.validation, solved directly (checks the in-house element against theory)."""
    Ro, Ri = ws.D_sp / 2, ws.d_sp / 2
    E, nu = ws.M["spar_E_lo_pa"], 0.3
    G = E / (2 * (1 + nu))
    sq = np.array([[-0.02, -0.02], [0.02, -0.02], [0.02, 0.02], [-0.02, 0.02]])
    p = wf.LEVELS[level]
    nodes2d, elems2d, _ = sf.section_mesh(sq, [], (0.0, 0.0, [Ri, Ro]), p["nth"], p["nr"], 0.003, 0.006)
    elems2d = [(v, c) for v, c in elems2d if v == sf.VTK_QUAD]
    Lb = 0.5
    ys = np.linspace(0, Lb, int(round(Lb / p["hy"])) + 1)
    X, blocks, _, _ = sf.extrude(nodes2d, elems2d, ys, lambda x, z, y: 0)
    X, blocks, _ = sf.compact(X, blocks)
    K = sf.assemble(X, blocks, [E], [nu])
    root = np.where(np.abs(X[:, 1]) < 1e-12)[0]
    tip = np.where(np.abs(X[:, 1] - Lb) < 1e-12)[0]
    lu, free = sf.solve_direct(K, None, root)
    I = math.pi / 64 * ((2 * Ro) ** 4 - (2 * Ri) ** 4)
    J = 2 * I
    A_ = math.pi * (Ro ** 2 - Ri ** 2)
    # tip shear 10 N as equal nodal loads on the tip face; tip torque 1 N m as tangential nodal forces ~ r
    f = np.zeros(3 * len(X))
    f[3 * tip + 2] = 10.0 / len(tip)
    U = sf.apply_lu(lu, free, f)
    w_fe = float(U[tip, 2].mean())
    w_th = 10 * Lb ** 3 / (3 * E * I) + 10 * Lb / (0.5 * G * A_)
    f = np.zeros(3 * len(X))
    r = np.hypot(X[tip, 0], X[tip, 2])
    s = 1.0 / np.sum(r * r)                           # F_i = T r_i t_i / sum r^2, t = (z, -x) / r for +y rotation
    f[3 * tip + 0] = s * X[tip, 2]
    f[3 * tip + 2] = -s * X[tip, 0]
    U = sf.apply_lu(lu, free, f)
    th = float(np.mean((X[tip, 2] * U[tip, 0] - X[tip, 0] * U[tip, 2]) / r ** 2))
    th_th = 1.0 * Lb / (G * J)
    return {"shear": {"w_fe_mm": w_fe * 1e3, "w_beam_mm": w_th * 1e3, "err": w_fe / w_th - 1},
            "torque": {"twist_fe_deg": math.degrees(th), "twist_beam_deg": math.degrees(th_th), "err": th / th_th - 1},
            "mesh": {"level": level, "nodes": int(len(X)), "elements": int(sum(len(c) for _, c, _ in blocks))}}


def layer_index(X, ys):
    k = np.searchsorted(ys, X[:, 1] - 1e-9)
    k = np.clip(k, 0, len(ys) - 1)
    k = np.where(np.abs(ys[np.clip(k - 1, 0, None)] - X[:, 1]) < np.abs(ys[k] - X[:, 1]), np.clip(k - 1, 0, None), k)
    assert np.all(np.abs(ys[k] - X[:, 1]) < 1e-9), "node off the extrusion layers"
    return k


class TwoLevelPCG:
    """CG on K_ff with M^-1 = P Kc^-1 P^T + sum_k R_k^T K_kk^-1 R_k (layer blocks + layer rigid-body coarse space)."""

    def __init__(self, K, X, ys, fixed_nodes, ref_xz):
        import scipy.linalg as sla
        import scipy.sparse as sp
        import scipy.sparse.linalg as spla
        n = K.shape[0]
        fixed = np.zeros(n, bool)
        for node in fixed_nodes:
            fixed[3 * node:3 * node + 3] = True
        self.free = ~fixed
        fidx = np.where(self.free)[0]
        self.K = K[self.free][:, self.free].tocsr()
        lay_node = layer_index(X, ys)
        lay = lay_node[fidx // 3]
        self.blocks = []
        for k in np.unique(lay):
            idx = np.where(lay == k)[0]
            self.blocks.append((idx, spla.splu(self.K[idx][:, idx].tocsc(), permc_spec="MMD_AT_PLUS_A")))
        # coarse space, per layer (local x' = x - x_ref, z' = z - z_ref, scaled by 0.1 m): 3 translations, spanwise
        # u_y = x', z' (bending slopes), in-plane affine u_x, u_z = x', z' (includes twist), camber u_z = x'^2, x'^3,
        # warping u_y = x' z'. 12 modes per layer: the long-wavelength section motions plain CG resolves slowly.
        layers = np.unique(lay)
        col = {k: j for j, k in enumerate(layers)}
        node = fidx // 3
        comp = fidx % 3
        xp = (X[node, 0] - ref_xz[0]) / 0.1
        zp = (X[node, 2] - ref_xz[1]) / 0.1
        one = np.ones(len(fidx))
        modes = [(0, one), (1, one), (2, one), (1, xp), (1, zp), (0, xp), (0, zp), (2, xp), (2, zp),
                 (2, xp ** 2), (2, xp ** 3), (1, xp * zp)]
        nm = len(modes)
        lcol = np.array([col[k] for k in lay])
        rows, cols, vals = [], [], []
        for j, (cmp_, f_) in enumerate(modes):
            sel = comp == cmp_
            rows.append(np.where(sel)[0]); cols.append(nm * lcol[sel] + j); vals.append(f_[sel])
        self.P = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                               shape=(len(fidx), nm * len(layers)))
        Kc = (self.P.T @ (self.K @ self.P)).toarray()
        self.cho = sla.cho_factor(Kc)
        self._sla = sla
        self.M = spla.LinearOperator(self.K.shape, matvec=self._apply, dtype=float)
        self.ndof = len(fidx)

    def _apply(self, r):
        r = np.ravel(r)
        z = self.P @ self._sla.cho_solve(self.cho, self.P.T @ r)
        for idx, lu in self.blocks:
            z[idx] += lu.solve(r[idx])
        return z

    def solve(self, f, rtol=1e-10, maxiter=5000):
        import scipy.sparse.linalg as spla
        it = [0]
        b = f[self.free]
        x, info = spla.cg(self.K, b, rtol=rtol, maxiter=maxiter, M=self.M,
                          callback=lambda xk: it.__setitem__(0, it[0] + 1))
        res = float(np.linalg.norm(self.K @ x - b) / np.linalg.norm(b))
        u = np.zeros(len(f))
        u[self.free] = x
        return u.reshape(-1, 3), {"cg_iter": it[0], "cg_info": int(info), "rel_residual": res}


def reactions_check(K, U, root, f):
    """Sum of root reactions vs applied load (equilibrium of the solved system)."""
    R = (K @ U.ravel()) - f
    Rn = R.reshape(-1, 3)[root].sum(0)
    return Rn.tolist(), f.reshape(-1, 3).sum(0).tolist()


def run_level(lev, g, msets, cases, stations, sets=("B", "T"), case_names=None):
    t0 = time.time()
    model = wf.build(lev, g)
    st = model["stats"]
    X, blocks, mk = model["X"], model["blocks"], model["markers"]
    root_nodes = sorted({n for _, nd in mk["root"] for n in nd})
    vols = sf.element_volumes(X, blocks)
    st["min_signed_volume"] = float(vols.min())
    st["build_s"] = round(time.time() - t0, 1)
    print(f"level {lev}: {st}", flush=True)
    sel_cases = [cs for cs in wf.CASES if case_names is None or cs[0] in case_names]
    loads = {}
    for cs in sel_cases:
        tr, chk = wf.tractions(model, cases[cs]["rows"], g["xs"])
        loads[cs] = (sf.traction_vector(X, mk, tr), chk)
    runs = {}
    for ms in sets:
        E, nu = msets[ms]
        t1 = time.time()
        K = sf.assemble(X, blocks, E, nu)
        pc = TwoLevelPCG(K, X, model["ys"], root_nodes, (g["xs"], g["zs"]))
        t_fac = time.time() - t1
        print(f"  L{lev} set {ms}: assembled + preconditioner {t_fac:.0f} s, {pc.ndof:,} dofs", flush=True)
        for cs in sel_cases:
            f, chk = loads[cs]
            t2 = time.time()
            U, sol = pc.solve(f)
            Rsum, Fsum = reactions_check(K, U, root_nodes, f)
            pr = wf.post(model, U, g, E, nu, stations)
            key = f"{cs[0]}/{cs[1]}/{ms}"
            runs[key] = {"info": {"setup_s": round(t_fac, 1), "solve_s": round(time.time() - t2, 1), **sol,
                                  "root_reaction_N": Rsum, "applied_N": Fsum, **chk}, "post": pr}
            print(f"  L{lev} {key}: w_tip {pr['w'][-1] * 1e3:.3f} mm, u_tip {pr['u'][-1] * 1e3:.3f} mm, "
                  f"twist_tip {math.degrees(pr['twist'][-1]):.3f} deg, CG {sol['cg_iter']} it, res {sol['rel_residual']:.1e}", flush=True)
        del pc, K
    st["wall_s"] = round(time.time() - t0, 1)
    return {"stats": st, "runs": runs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--sets", nargs="+", default=["B", "T"],
                    help="material sets: B bending-exact, T torsion-exact (both isotropic tube, as SU2), O orthotropic tube")
    ap.add_argument("--cases", nargs="+", default=None, help="C1 case names (default: all four)")
    ap.add_argument("--out", default="wing_fea_direct.json", help="output file in fea/out (merge parallel runs)")
    ap.add_argument("--no-validation", action="store_true")
    ap.add_argument("--intro", default="block", choices=["block", "distributed"],
                    help="station-load introduction (wing_fea.INTRO)")
    a = ap.parse_args()
    wf.INTRO = a.intro
    OUT.mkdir(exist_ok=True)
    g = wf.d1_geometry()
    msets = dict(wf.materials(g))
    # set O: the CF tube as what it is, transversely isotropic about its own axis (E axial = spar_E_lo, G = spar_G_lo,
    # transverse 8 GPa: ASM-C2-TUBE-ET). Only the in-house assembly can do this (SU2's elasticity is isotropic);
    # B (bending-exact) and T (torsion-exact) bracket it.
    Eb, nub = msets["B"]
    tube = {"Ea": ws.M["spar_E_lo_pa"], "Et": 8.0e9, "Gat": ws.M["spar_G_lo_pa"], "nu_at": 0.30, "nu_tt": 0.40,
            "center": (g["xs"], g["zs"])}
    msets["O"] = ([Eb[0], tube, Eb[2]], nub)
    cases = ws.read_spanwise()
    stations = list(np.round(np.arange(0.025, 0.5751, 0.025), 4))
    pth = OUT / a.out
    prev = json.loads(pth.read_text()) if pth.exists() else {}
    result = {"intro": a.intro, "solver": "in-house linear-elastic hex/wedge assembly (su2fea.assemble) + two-level PCG (layer LU + layer rigid-body coarse space), rtol 1e-10",
              "inputs": {"geometry_source": "team/D1/wing_data.py -> subsystems/wing/fusion/wing.py (D1-R1)",
                         "loads": "team/C1/data/wing_spanwise.csv (C1-R4)",
                         "materials": {k: v for k, v in msets.items()}},
              "levels": prev.get("levels", {})}
    if not a.no_validation:
        result["validation"] = tube_validation(2)
        print("validation", json.dumps(result["validation"]), flush=True)
    for lev in a.levels:
        result["levels"][str(lev)] = run_level(lev, g, msets, cases, stations, a.sets, a.cases)
        pth.write_text(json.dumps(result, indent=1, default=float))
    result["beam"] = {f"{cs[0]}/{cs[1]}": {"tape0": wf.beam_reference(cases[cs]["rows"], stations, 0.0),
                                            "tape50": wf.beam_reference(cases[cs]["rows"], stations, 0.5)}
                      for cs in wf.CASES}
    pth.write_text(json.dumps(result, indent=1, default=float))
    print("done")


if __name__ == "__main__":
    main()
