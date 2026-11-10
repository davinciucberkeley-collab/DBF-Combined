"""C2 verification FEA of the as-designed wing (K09-L) with gmsh + SU2 ELASTICITY.

Model: right half wing, y 0 -> 0.575 m, clamped at the centreline (as the beam model). The S5010 section (LE to
TE) is meshed in 2-D with gmsh, the CF spar wall as structured hexahedra, and extruded along the span through
layers that start and stop at every as-designed cut (D1 geometry read live from team/D1/wing_data.py ->
subsystems/wing/fusion/wing.py):
    pod recess and saddle windows, brace-anchor pockets (PETG saddles), through-core blocks (PETG) with the 36 mm
    spar plugs, anchor plugs, servo pockets (void), elevon cut-outs aft of the hinge (void), spar end at |y| 0.50.
Materials: XPS (E 10 MPa, nu 0.25 -> G 4 MPa), PETG printed (E 1.1 GPa), CF tube as two equivalent-isotropic
sets, because SU2's linear-elastic model is isotropic:
    set B (bending): E = spar_E_lo 70 GPa  -> deflection, in-plane deflection, spar and foam stresses
    set T (torsion): E = 2 G (1 + nu) with spar_G_lo 3 GPa -> twist
Tape skin is not modelled (stiffness-conservative; compared with the beam model at tape 0 %).
Loads: C1-R4 cut loads (team/C1/data/wing_spanwise.csv) differenced into strip loads (<= 25 mm strips, same as
the beam FE) and applied as uniform tractions on four skin patches per strip (upper/lower x fore/aft of the spar),
least-norm so each strip reproduces its 3 forces and 3 moments about the spar axis exactly.
Mesh convergence: 3 levels (2-D size, spar wall divisions and span layers refined together).
Validation: tube-only cantilever (bending and torsion) against closed-form beam theory.

Run (about 10-25 min on 20 cores):  python -I redesign/team/C2/fea/wing_fea.py [--levels 1 2 3]
Writes team/C2/fea/out/wing_fea.json (+ runs/ scratch, not needed afterwards).
"""
import argparse
import contextlib
import io
import importlib.util
import json
import math
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
C2 = HERE.parent
RD = C2.parents[1]
sys.path.insert(0, str(C2))
sys.path.insert(0, str(HERE))
import su2fea as sf                     # noqa: E402
import wing_struct as ws                # noqa: E402  (pure at import: reads params, C1 data, airfoil)

OUT = HERE / "out"
RUNS = HERE / "runs"

LEVELS = {
    1: dict(nth=32, nr=2, h_near=0.0022, h_far=0.010, hy=0.0125),
    2: dict(nth=64, nr=3, h_near=0.0011, h_far=0.005, hy=0.00625),
    3: dict(nth=96, nr=4, h_near=0.00075, h_far=0.0033, hy=0.0042),
}
FOAM, CF, PETG = 0, 1, 2
CASES = [("L1-LEVEL", "MC-C"), ("G2-HANG-MOTOR", "MC-P"), ("L4-CORNER-SIDE-Y", "MC-C"), ("F1-PULLUP-VD", "MC-C")]
STRIP_MAX = 0.025
COL_HALF = 0.012          # anchor / window column half-width (D1 slot 11.2 mm; +0.8 mm so it clears the tube)


# ------------------------------------------------------------------------------------------------ inputs
def d1_geometry():
    sys.path.insert(0, str(RD / "team" / "D1"))
    spec = importlib.util.spec_from_file_location("wd", RD / "team" / "D1" / "wing_data.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    with contextlib.redirect_stdout(io.StringIO()):
        _, _, g, _ = m.build_wing()
    return g


def materials(g):
    Mi = ws.M
    E_petg = 2.0e9 * 0.55          # PETG 2.0 GPa x fill factor 0.55 (subsystems/fins fin_detail.block.fill_factor)
    nu_cf = 0.30
    sets = {
        "B": ([Mi["xps_E_pa"], Mi["spar_E_lo_pa"], E_petg], [0.25, nu_cf, 0.35]),
        "T": ([Mi["xps_E_pa"], 2 * Mi["spar_G_lo_pa"] * (1 + nu_cf), E_petg], [0.25, nu_cf, 0.35]),
    }
    return sets


def inside(y, a, b_):
    return a <= y <= b_


def make_mat_fn(g):
    xs, zs, rs, ri = g["xs"], g["zs"], g["rs"], g["ri"]
    yf, yan = g["y_fin"], g["y_anchor"]
    pb, pa = g["plug_blk"], g["plug_anc"]
    spans = g["spans"]

    def fn(x, z, y):
        r = math.hypot(x - xs, z - zs)
        inspar = y < g["spar_half"]
        if r < ri:
            if not inspar:
                return FOAM
            if abs(y - yf) <= pb / 2 or abs(y - yan) <= pa / 2:
                return PETG
            return None
        if r < rs:
            return CF if inspar else FOAM
        if x > g["xh"]:
            return None if any(inside(y, a, b_) for a, b_ in spans) else FOAM
        if inspar and inside(y, *g["blk_y"]) and g["blk_x"][0] < x < g["blk_x"][1]:
            return PETG
        if inspar and inside(y, *g["anc_y"]) and abs(x - xs) < COL_HALF:
            return PETG
        if inside(y, *g["win_y"]) and abs(x - xs) < COL_HALF and z > zs + rs + 0.0005:
            return None
        if y < g["y_pod"] and g["x_rec0"] < x < g["x_rec1"] and z > g["z_rec"]:
            return None
        if inside(y, *g["sp_y"]) and g["sp_x"][0] < x < g["sp_x"][1] and z < g["sp_zc"]:
            return None
        return FOAM
    return fn


def outline_poly():
    """S5010 closed polyline LE -> TE upper, TE -> LE lower (wing_struct's airfoil, 160 + 160 points)."""
    xg = ws.XA
    idx = np.unique(np.round(np.linspace(0, len(xg) - 1, 161)).astype(int))
    up = np.stack([xg[idx], ws.ZU[idx]], 1)
    lo = np.stack([xg[idx], ws.ZL[idx]], 1)[::-1]
    poly = np.vstack([up, lo[1:-1]])
    return poly


def cut_lines(g):
    zlo, zhi = -0.03, 0.04
    xs, zs, rs = g["xs"], g["zs"], g["rs"]
    L = [((g["xh"], zlo), (g["xh"], zhi)),
         ((g["blk_x"][0], zlo), (g["blk_x"][0], zhi)), ((g["blk_x"][1], zlo), (g["blk_x"][1], zhi)),
         ((xs - COL_HALF, zlo), (xs - COL_HALF, zhi)), ((xs + COL_HALF, zlo), (xs + COL_HALF, zhi)),
         ((xs - COL_HALF, zs + rs + 0.0005), (xs + COL_HALF, zs + rs + 0.0005)),
         ((g["x_rec0"], g["z_rec"]), (g["x_rec0"], zhi)), ((g["x_rec1"], g["z_rec"]), (g["x_rec1"], zhi)),
         ((g["x_rec0"], g["z_rec"]), (g["x_rec1"], g["z_rec"])),
         ((g["sp_x"][0], zlo), (g["sp_x"][0], g["sp_zc"])), ((g["sp_x"][1], zlo), (g["sp_x"][1], g["sp_zc"])),
         ((g["sp_x"][0], g["sp_zc"]), (g["sp_x"][1], g["sp_zc"]))]
    return L


def span_breaks(g):
    br = [0.0, *g["win_y"], g["y_pod"], *[v for s in g["spans"] for v in s], *g["anc_y"],
          g["y_anchor"] - g["plug_anc"] / 2, g["y_anchor"] + g["plug_anc"] / 2, *g["sp_y"], *g["blk_y"],
          g["y_fin"] - g["plug_blk"] / 2, g["y_fin"] + g["plug_blk"] / 2, g["spar_half"], g["half"]]
    br = sorted(br)
    out = [br[0]]
    for v in br[1:]:
        if v - out[-1] > 0.0006:
            out.append(v)
    out[-1] = g["half"]
    return out


def strips_from(breaks):
    st = []
    for a, b_ in zip(breaks[:-1], breaks[1:]):
        n = max(1, math.ceil((b_ - a) / STRIP_MAX - 1e-9))
        e = np.linspace(a, b_, n + 1)
        st.extend(zip(e[:-1], e[1:]))
    return st


def layers_from(breaks, hy):
    ys = [breaks[0]]
    for a, b_ in zip(breaks[:-1], breaks[1:]):
        n = max(1, math.ceil((b_ - a) / hy - 1e-9))
        ys.extend(np.linspace(a, b_, n + 1)[1:])
    return np.array(ys)


# ------------------------------------------------------------------------------------------------ model build
def build(level, g):
    p = LEVELS[level]
    poly = outline_poly()
    nodes2d, elems2d, on_out = sf.section_mesh(poly, cut_lines(g), (g["xs"], g["zs"], [g["ri"], g["rs"]]),
                                               p["nth"], p["nr"], p["h_near"], p["h_far"])
    breaks = span_breaks(g)
    ys = layers_from(breaks, p["hy"])
    X, blocks, types, mats = sf.extrude(nodes2d, elems2d, ys, make_mat_fn(g))
    n2 = len(nodes2d)
    outline_flag = np.tile(on_out, len(ys))
    X, blocks, used = sf.compact(X, blocks)
    outline_flag = outline_flag[used]
    faces = sf.boundary_faces(blocks)
    strips = strips_from(breaks)
    zc_of = lambda x: 0.5 * (np.interp(x, ws.XA, ws.ZU) + np.interp(x, ws.XA, ws.ZL))
    markers = {"root": []}
    patch = {}
    free = []
    for ft, nd in faces:
        P = X[list(nd)]
        if np.all(np.abs(P[:, 1]) < 1e-12):
            markers["root"].append((ft, nd))
            continue
        if np.all(outline_flag[list(nd)]) and np.ptp(P[:, 1]) > 0:
            cx, cy, cz = P.mean(0)
            k = next(i for i, (a, b_) in enumerate(strips) if a - 1e-12 <= cy <= b_ + 1e-12)
            key = f"S{k:02d}{'U' if cz >= zc_of(cx) else 'L'}{'F' if cx < g['xs'] else 'A'}"
            patch.setdefault(key, []).append((ft, nd))
        else:
            free.append((ft, nd))
    markers.update(patch)
    markers["free"] = free
    stats = {"level": level, **p, "nodes": int(len(X)), "elements": int(sum(len(c) for _, c, _ in blocks)),
             "hex": int(sum(len(c) for v, c, _ in blocks if v == sf.VTK_HEX)),
             "wedge": int(sum(len(c) for v, c, _ in blocks if v == sf.VTK_WEDGE)),
             "layers": int(len(ys) - 1), "section_nodes": int(n2), "patches": len(patch)}
    return {"X": X, "blocks": blocks, "markers": markers, "strips": strips, "ys": ys, "stats": stats}


def patch_geom(X, faces):
    A, S = 0.0, np.zeros(3)
    for ft, nd in faces:
        P = X[list(nd)]
        if ft == sf.VTK_TRI:
            tri = [(0, 1, 2)]
        else:
            tri = [(0, 1, 2), (0, 2, 3)]
        for i, j, k in tri:
            a = 0.5 * np.linalg.norm(np.cross(P[j] - P[i], P[k] - P[i]))
            A += a
            S += a * (P[i] + P[j] + P[k]) / 3
    return A, S


def strip_loads(rows, strips, xs):
    """C1 cut loads (right side) -> resultant force and moment per strip about (xs, y_mid, 0)."""
    r = ws.side(rows, 1)
    P = np.array([[xs, v, 0.0] for v in r[:, 0]])
    Fc, Mc = r[:, 1:4], r[:, 4:7]
    out = [[np.zeros(3), np.zeros(3)] for _ in strips]
    for i in range(len(r)):
        if i + 1 < len(r):
            F_ext = Fc[i] - Fc[i + 1]
            M_ext = Mc[i] - (Mc[i + 1] + np.cross(P[i + 1] - P[i], Fc[i + 1]))
            y_app = 0.5 * (r[i, 0] + r[i + 1, 0])
        else:
            F_ext, M_ext, y_app = Fc[i], Mc[i], r[i, 0]
        k = min(range(len(strips)), key=lambda j: 0 if strips[j][0] <= y_app <= strips[j][1]
                else min(abs(y_app - strips[j][0]), abs(y_app - strips[j][1])))
        ref = np.array([xs, 0.5 * (strips[k][0] + strips[k][1]), 0.0])
        out[k][0] += F_ext
        out[k][1] += M_ext + np.cross(P[i] - ref, F_ext)
    return out, r


def tractions(model, rows, xs):
    X, mk, strips = model["X"], model["markers"], model["strips"]
    loads_k, r = strip_loads(rows, strips, xs)
    res = []
    resid = 0.0
    totF = np.zeros(3)
    for k, (F, Mo) in enumerate(loads_k):
        ref = np.array([xs, 0.5 * (strips[k][0] + strips[k][1]), 0.0])
        names = [n for n in mk if n.startswith(f"S{k:02d}")]
        if not names:
            if np.linalg.norm(F) + np.linalg.norm(Mo) > 1e-9:
                raise RuntimeError(f"strip {k} has load but no skin patch")
            continue
        B = np.zeros((6, 3 * len(names)))
        w = np.zeros(3 * len(names))
        for j, n in enumerate(names):
            A, S = patch_geom(X, mk[n])
            B[:3, 3 * j:3 * j + 3] = A * np.eye(3)
            B[3:, 3 * j:3 * j + 3] = ws.skew(S - A * ref)
            w[3 * j:3 * j + 3] = A
        rhs = np.concatenate([F, Mo])
        Winv = np.diag(1 / w)
        t = Winv @ B.T @ np.linalg.lstsq(B @ Winv @ B.T, rhs, rcond=None)[0]
        resid = max(resid, float(np.abs(B @ t - rhs).max()))
        totF += F
        for j, n in enumerate(names):
            res.append((n, *t[3 * j:3 * j + 3]))
    return res, {"max_resultant_residual": resid, "root_cut_F_N": r[0, 1:4].tolist(), "sum_strip_F_N": totF.tolist()}


# ------------------------------------------------------------------------------------------------ solve + post
def run_case(model, level, case, mset, mats_sets, rows, xs):
    d = RUNS / f"L{level}" / f"{case[0]}_{case[1]}_{mset}"
    d.mkdir(parents=True, exist_ok=True)
    mesh = RUNS / f"L{level}" / "wing.su2"
    props = RUNS / f"L{level}" / "props.dat"
    E, nu = mats_sets[mset]
    loads, chk = tractions(model, rows, xs)
    loads.append(("free", 0.0, 0.0, 0.0))
    sf.write_cfg(d / "run.cfg", str(mesh), str(props), E, nu, ["root"], loads)
    t0 = time.time()
    txt = sf.run_su2(d / "run.cfg", d)
    U = sf.read_restart(d / "restart.csv", len(model["X"]))
    return U, {"seconds": round(time.time() - t0, 1), "linsol": sf.linsol_info(txt), **chk}


def post(model, U, g, E, nu, stations):
    X, blocks, ys = model["X"], model["blocks"], model["ys"]
    xs, zs, rs, ri = g["xs"], g["zs"], g["rs"], g["ri"]
    rr = np.hypot(X[:, 0] - xs, X[:, 2] - zs)
    out = {"y": [], "w": [], "u": [], "twist": [], "sigma_spar": []}
    on_skin = None
    for yq in stations:
        k = int(np.argmin(np.abs(ys - yq)))
        lay = np.abs(X[:, 1] - ys[k]) < 1e-9
        core = lay & (rr <= rs + 1e-9)
        if not core.any():
            continue
        w = float(U[core, 2].mean())
        u = float(U[core, 0].mean())
        box = lay & (X[:, 0] <= g["xh"]) & (X[:, 0] >= 0.005)
        A = np.stack([np.ones(box.sum()), X[box, 0] - xs], 1)
        coef = np.linalg.lstsq(A, U[box, 2], rcond=None)[0]
        out["y"].append(float(ys[k]))
        out["w"].append(w)
        out["u"].append(u)
        out["twist"].append(float(-coef[1]))
    # spar axial stress: per span layer, fit sigma_yy = a + b (x - xs) + c (z - zs) over the tube elements,
    # evaluate on the outer circle (beam outer fibre)
    sig_rows = []
    foam = []
    petg = []
    for vtk, conn, m in blocks:
        eps = sf.centroid_strain(X, U, vtk, conn)
        cen = X[conn].mean(1)
        for mid, store in ((CF, "cf"), (FOAM, "foam"), (PETG, "petg")):
            sel = m == mid
            if not sel.any():
                continue
            s = sf.hooke(eps[sel], E[mid], nu[mid])
            if mid == CF:
                sig_rows.append((cen[sel], s[:, 1, 1]))
            else:
                ev = np.linalg.eigvalsh(s)
                vm = np.sqrt(0.5 * ((ev[:, 0] - ev[:, 1]) ** 2 + (ev[:, 1] - ev[:, 2]) ** 2 + (ev[:, 2] - ev[:, 0]) ** 2))
                rec = np.column_stack([cen[sel], ev[:, 2], ev[:, 0], 0.5 * (ev[:, 2] - ev[:, 0]), vm])
                (foam if mid == FOAM else petg).append(rec)
    if sig_rows:
        C = np.vstack([c_ for c_, _ in sig_rows])
        S = np.concatenate([s_ for _, s_ in sig_rows])
        yl = np.round(C[:, 1], 7)
        prof = []
        for yv in np.unique(yl):
            sel = yl == yv
            A = np.stack([np.ones(sel.sum()), C[sel, 0] - xs, C[sel, 2] - zs], 1)
            a, b_, c_ = np.linalg.lstsq(A, S[sel], rcond=None)[0]
            prof.append((float(yv), float(abs(a) + rs * math.hypot(b_, c_)), float(np.abs(S[sel]).max())))
        out["spar_profile"] = prof
    def summary(recs, clip_root=0.010):
        if not recs:
            return {}
        R = np.vstack(recs)
        R = R[R[:, 1] > clip_root]
        i1, i3, it, iv = int(np.argmax(R[:, 3])), int(np.argmin(R[:, 4])), int(np.argmax(R[:, 5])), int(np.argmax(R[:, 6]))
        return {"s1_max_pa": float(R[i1, 3]), "s1_at": R[i1, :3].tolist(),
                "s3_min_pa": float(R[i3, 4]), "s3_at": R[i3, :3].tolist(),
                "tau_max_pa": float(R[it, 5]), "tau_at": R[it, :3].tolist(),
                "s1_p995_pa": float(np.percentile(R[:, 3], 99.5)), "tau_p995_pa": float(np.percentile(R[:, 5], 99.5)),
                "vm_max_pa": float(R[iv, 6]), "vm_at": R[iv, :3].tolist()}
    out["foam"] = summary(foam)
    out["petg"] = summary(petg)
    return out


def beam_reference(rows, stations, tape=0.0):
    """wing_struct beam FE (96 elements per half) at tape effectiveness 0 (like the FEA) and 0.5 (design basis)."""
    out = {}
    for name, (E_, G_) in {"B": (ws.M["spar_E_lo_pa"], ws.M["spar_G_lo_pa"]), "T": (ws.M["spar_E_lo_pa"], ws.M["spar_G_lo_pa"])}.items():
        sec = ws.sec_factory(E_s=E_, G_s=G_, tape_eff=tape)
        ys, u = ws.static_fe(rows, 96, sec)
        out[name] = {"y": ys.tolist(), "w": u[2::6].tolist(), "u": u[0::6].tolist(), "twist": u[4::6].tolist()}
    return out


# ------------------------------------------------------------------------------------------------ validation
def validation(level=2):
    """Tube-only cantilever, L 0.50 m, clamped: tip shear 10 N (z) and tip torque 1 N m, vs beam theory."""
    g = {"xs": 0.0, "zs": 0.0}
    Ro, Ri = ws.D_sp / 2, ws.d_sp / 2
    E, nu = ws.M["spar_E_lo_pa"], 0.3
    G = E / (2 * (1 + nu))
    sq = np.array([[-0.02, -0.02], [0.02, -0.02], [0.02, 0.02], [-0.02, 0.02]])
    p = LEVELS[level]
    nodes2d, elems2d, _ = sf.section_mesh(sq, [], (0.0, 0.0, [Ri, Ro]), p["nth"], p["nr"], 0.003, 0.006)
    elems2d = [(v, c) for v, c in elems2d if v == sf.VTK_QUAD]
    Lb = 0.5
    ys = np.linspace(0, Lb, int(round(Lb / p["hy"])) + 1)
    X, blocks, _, _ = sf.extrude(nodes2d, elems2d, ys, lambda x, z, y: 0)
    X, blocks, _ = sf.compact(X, blocks)
    faces = sf.boundary_faces(blocks)
    mk = {"root": [], "q_top": [], "q_bot": [], "q_fwd": [], "q_aft": [], "free": []}
    for ft, nd in faces:
        P = X[list(nd)]
        if np.all(np.abs(P[:, 1]) < 1e-12):
            mk["root"].append((ft, nd))
        elif np.all(np.abs(P[:, 1] - Lb) < 1e-12):
            c = P.mean(0)
            ang = math.degrees(math.atan2(c[2], c[0]))
            q = "q_aft" if -45 <= ang < 45 else "q_top" if 45 <= ang < 135 else "q_bot" if -135 <= ang < -45 else "q_fwd"
            mk[q].append((ft, nd))
        else:
            mk["free"].append((ft, nd))
    d = RUNS / "validation"
    d.mkdir(parents=True, exist_ok=True)
    sf.write_su2(d / "tube.su2", X, blocks, mk)
    sf.write_props(d / "props.dat", blocks)
    res = {}
    I = math.pi / 64 * ((2 * Ro) ** 4 - (2 * Ri) ** 4)
    J = 2 * I
    A_ = math.pi * (Ro ** 2 - Ri ** 2)
    for name, F, Mo in (("shear", np.array([0, 0, 10.0]), np.zeros(3)), ("torque", np.zeros(3), np.array([0, 1.0, 0]))):
        ref = np.array([0, Lb, 0])
        names = [n for n in ("q_top", "q_bot", "q_fwd", "q_aft")]
        B = np.zeros((6, 12))
        w = np.zeros(12)
        for j, n in enumerate(names):
            Ap, S = patch_geom(X, mk[n])
            B[:3, 3 * j:3 * j + 3] = Ap * np.eye(3)
            B[3:, 3 * j:3 * j + 3] = ws.skew(S - Ap * ref)
            w[3 * j:3 * j + 3] = Ap
        Winv = np.diag(1 / w)
        t = Winv @ B.T @ np.linalg.lstsq(B @ Winv @ B.T, np.concatenate([F, Mo]), rcond=None)[0]
        loads = [(n, *t[3 * j:3 * j + 3]) for j, n in enumerate(names)] + [("free", 0, 0, 0)]
        dd = d / name
        dd.mkdir(exist_ok=True)
        sf.write_cfg(dd / "run.cfg", str(d / "tube.su2"), str(d / "props.dat"), [E], [nu], ["root"], loads)
        sf.run_su2(dd / "run.cfg", dd)
        U = sf.read_restart(dd / "restart.csv", len(X))
        tip = np.abs(X[:, 1] - Lb) < 1e-12
        if name == "shear":
            w_fe = float(U[tip, 2].mean())
            w_th = 10 * Lb ** 3 / (3 * E * I) + 10 * Lb / (0.5 * G * A_)
            # root stress from the layer-fit at y = 0.25 (mid, away from the clamp): M = 10 * 0.25
            k = int(np.argmin(np.abs(ys - 0.25)))
            sel_e = []
            for vtk, conn, m in blocks:
                cen = X[conn].mean(1)
                eps = sf.centroid_strain(X, U, vtk, conn)
                s = sf.hooke(eps, E, nu)[:, 1, 1]
                band = np.abs(cen[:, 1] - 0.5 * (ys[k] + ys[k + 1])) < 1e-9
                Afit = np.stack([np.ones(band.sum()), cen[band, 0], cen[band, 2]], 1)
                a, b_, c_ = np.linalg.lstsq(Afit, s[band], rcond=None)[0]
                sel_e.append(abs(a) + Ro * math.hypot(b_, c_))
            ymid = 0.5 * (ys[k] + ys[k + 1])
            s_th = 10 * (Lb - ymid) * Ro / I
            res[name] = {"w_fe_mm": w_fe * 1e3, "w_beam_mm": w_th * 1e3, "err": w_fe / w_th - 1,
                         "sigma_fe_mpa": sel_e[0] / 1e6, "sigma_beam_mpa": s_th / 1e6, "sigma_err": sel_e[0] / s_th - 1}
        else:
            rr = np.hypot(X[tip, 0], X[tip, 2])
            # rotation about +y from the tangential displacement of the outer ring
            th = float(np.mean((X[tip, 2] * U[tip, 0] - X[tip, 0] * U[tip, 2]) / rr ** 2))
            th_th = 1.0 * Lb / (G * J)
            res[name] = {"twist_fe_deg": math.degrees(th), "twist_beam_deg": math.degrees(th_th), "err": th / th_th - 1}
    res["mesh"] = {"level": level, "elements": int(sum(len(c) for _, c, _ in blocks)), "nodes": int(len(X))}
    return res


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--keep-runs", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    g = d1_geometry()
    msets = materials(g)
    cases = ws.read_spanwise()
    stations = list(np.round(np.arange(0.025, 0.5751, 0.025), 4))
    prev = {}
    pth = OUT / "wing_fea.json"
    if pth.exists():
        prev = json.loads(pth.read_text())
    result = {"inputs": {"geometry_source": "team/D1/wing_data.py -> subsystems/wing/fusion/wing.py (D1-R1)",
                         "loads": "team/C1/data/wing_spanwise.csv (C1-R4)", "materials": {k: v for k, v in msets.items()},
                         "geometry": {k: g[k] for k in ("xs", "zs", "rs", "ri", "xh", "y_fin", "blk_x", "blk_y", "anc_y",
                                                         "win_y", "y_pod", "x_rec0", "x_rec1", "z_rec", "sp_x", "sp_y",
                                                         "sp_zc", "spans", "spar_half", "half", "plug_blk", "plug_anc")},
                         "span_breaks": span_breaks(g), "col_half_m": COL_HALF},
              "levels": prev.get("levels", {}), "validation": prev.get("validation")}
    t0 = time.time()
    result["validation"] = validation(2)
    print("validation", json.dumps(result["validation"]), flush=True)
    for lev in a.levels:
        model = build(lev, g)
        st = model["stats"]
        print(f"level {lev}: {st}", flush=True)
        d = RUNS / f"L{lev}"
        d.mkdir(parents=True, exist_ok=True)
        sf.write_su2(d / "wing.su2", model["X"], model["blocks"], model["markers"])
        sf.write_props(d / "props.dat", model["blocks"])
        vols = sf.element_volumes(model["X"], model["blocks"])
        st["min_signed_volume"] = float(vols.min())
        jobs = [(cs, ms) for cs in CASES for ms in ("B", "T")]

        def job(j):
            cs, ms = j
            rows = cases[cs]["rows"]
            U, info = run_case(model, lev, cs, ms, msets, rows, g["xs"])
            E, nu = msets[ms]
            pr = post(model, U, g, E, nu, stations)
            return f"{cs[0]}/{cs[1]}/{ms}", {"info": info, "post": pr}
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            outs = dict(ex.map(job, jobs))
        result["levels"][str(lev)] = {"stats": st, "runs": outs}
        for k, v in outs.items():
            p = v["post"]
            print(f"  L{lev} {k}: w_tip {p['w'][-1] * 1e3:.3f} mm, u_tip {p['u'][-1] * 1e3:.3f} mm, "
                  f"twist_tip {math.degrees(p['twist'][-1]):.3f} deg, {v['info']['seconds']} s", flush=True)
        pth.write_text(json.dumps(result, indent=1, default=float))
    result["beam"] = {f"{cs[0]}/{cs[1]}": {"tape0": beam_reference(cases[cs]["rows"], stations, 0.0),
                                            "tape50": beam_reference(cases[cs]["rows"], stations, 0.5)} for cs in CASES}
    result["wall_s"] = round(time.time() - t0, 1)
    pth.write_text(json.dumps(result, indent=1, default=float))
    if not a.keep_runs:
        shutil.rmtree(RUNS, ignore_errors=True)
    print("done", result["wall_s"], "s")


if __name__ == "__main__":
    main()
