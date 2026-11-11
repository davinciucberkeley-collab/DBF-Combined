"""C4 simulation and verification round: 3-D solid FE of the as-designed fin quarters (SU2 + in-house hex8).

What it checks against the R4 shell/beam model (fin_structures_d3.py, fin_fe.py):
  A. Solver verification: SU2 ELASTICITY on a cantilever, 3 meshes, against Euler-Bernoulli + Timoshenko, and the
     element-wise material file (two materials).
  B. SU2 on the quarter: solver trials (CG/ILU, restarted FGMRES/ILU) against the hex8 direct solve on the same mesh;
     SU2 does not converge on the laminate (no PaStiX in this build), so C-E use the hex8 (SU2's element, see A).
  C. Fin face stress at the D5 shoe under L4 (the R4 FAIL item): SU2, 3 meshes, D5 shoe as drawn (legs 7 mm below the
     step, P:landing.shoe.leg_depth_m) and as proposed in CR-C4-30 (to |z| 0.171 m); hot-spot stress (IIW 0.4 t / 1.0 t
     surface extrapolation) and the raw peak, against the shell model on the same shoe.
  D. Station modes of the as-designed quarters with the A3 roll-up masses: in-house hex8 eigen solve, 3 meshes,
     Richardson extrapolation, against the shell model with the same masses; separation from 1P/2P (R-VIBRATION).
  E. Model-form check: station compliance (Fx, Fy, Tz at the tube end) and the foot deflection of the 3-D model
     against the shell model with matched tube properties.
Mesh: gmsh all-quad planform (OpenCASCADE) extruded through the two-board laminate (sim/mesh_quarter.py).

Run:  python -I redesign/team/C4/sim_fin.py   (cold ~3 h on a shared 20-core machine; cached in sim/out/cache, < 2 min)
      parallel cold run: sim/run_part.py stress | modes, sim/run_trial.py 0 | 1, then sim_fin.py
Then: python redesign/team/C4/sim/sim_plots.py (not -I, matplotlib)  and  python -I redesign/proofs/build_graph.py
Writes claims.sim.json, sim/out/sim_results.json.
"""
import hashlib
import itertools
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "sim"))
import numpy as np  # noqa: E402
from scipy.interpolate import griddata  # noqa: E402

import fin_fe as fe  # noqa: E402
import fin_structures_d3 as d3  # noqa: E402
import hexfe as hx  # noqa: E402
import mesh_quarter as mq  # noqa: E402
import proofkit as pk  # noqa: E402
import su2io  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/fins/params.json",
                               "../../subsystems/landing/params.json"], out="claims.sim.json")
P = "P:"
OUT = HERE / "sim" / "out"
RUNS = HERE / "sim" / "runs"
CACHE = OUT / "cache"
CODE = "C4-SIM-1"
STRESS_LEVELS = {1: (0.008, 0.002), 2: (0.008, 0.001), 3: (0.008, 0.0005)}   # global, tip-region element size
STRESS_LEVELS["G"] = (0.004, 0.001)  # global refinement check at the level-2 tip size
SU2_LEVELS = ()                     # SU2 CG/ILU does not converge on the quarter (CALC-C4-SIM-CODES)
SU2_TOL, SU2_ITERS = 1e-9, 6000
MODAL_LEVELS = {1: 0.008, 2: 0.008 / 2 ** 0.5, 3: 0.004}                        # ratio sqrt 2 (eigen solve cost)
THREADS = 6


# ====================================================================== sources and assumptions
kit.source("SRC-C4-IIW", "IIW fatigue recommendations: hot-spot stress", "standard",
           url="https://link.springer.com/book/10.1007/978-3-319-23757-2",
           where="Hobbacher, IIW doc. XIII-2460-13, 2016, sec. 2.2.3: surface stress read at 0.4 t and 1.0 t from "
                 "the discontinuity, sigma_hs = 1.67 s(0.4t) - 0.67 s(1.0t)")
kit.source("SRC-C4-ROACHE", "Roache: grid convergence index", "paper",
           url="https://doi.org/10.1115/1.2910291",
           where="Roache, J. Fluids Eng. 116 (1994) 405; Fs = 1.25 for three grids")
kit.source("SRC-C4-SU2", "SU2 v8.5.0 ELASTICITY solver", "web", url="https://su2code.github.io/docs_v7/Theory/",
           where="linear elasticity, hex8 full integration, MARKER_LOAD = traction x area, FEA_FILENAME materials")


def asm(id, title, text, basis, value, unit, status="UNVERIFIED", cites=()):
    kit.assumption(id, title, text, basis, value=value, unit=unit, status=status, cites=cites)


asm("ASM-C4-SIM-LINK-E", "Tube wall + LE fillet zone modulus 3 GPa",
    "Isotropic 3 GPa (nu 0.35) for the zone between the square bar face and the board LE (tube wall + epoxy fillet)",
    "Stands in for the shell model's rigid LE link: 100x stiffer in shear than the paper faces over 5.7 mm, adds "
    "0.6 % to the tube's out-of-plane EI", 3e9, "Pa", status="PROPOSED")
asm("ASM-C4-SIM-SHOE-E", "D5 shoe region modulus 50 GPa (rigid)",
    "Shoe legs, cheeks, glue and the board inside them as one stiff isotropic block (50 GPa), as the shell model's "
    "rigid shoe", "Same idealisation as fin_fe rigid_fin; real PETG legs (2 GPa, 0.8 mm) are softer, so the stress "
    "jump at the leg edge is not lower than in the real part", 50e9, "Pa", status="PROPOSED")
asm("ASM-C4-SIM-TAIL-E", "Station-collar tail tongue modulus 1 GPa (PETG, 45 % fill)",
    "Isotropic 1 GPa (nu 0.35) for the printed tail tongue that replaces the board in the notched LE-top corner, "
    "from the tube surface to 40 mm aft, strip band + 1 mm deep; the CF edge strips run on over it to the tube",
    "PETG about 2.0 GPa solid x P:fin_detail.station_collar.tongue_fill 0.45 (perimeters carry more): 1 GPa. The R4 "
    "shell model had the strips ending on a rigid LE link; the first 3-D pass ended them at the board LE and put "
    "26 MPa into the paper faces at the LE (artefact, removed by this zone)", 1e9, "Pa", status="PROPOSED")
asm("ASM-C4-SIM-HOTSPOT-T", "Hot-spot read distances 0.4 t and 1.0 t, t = laminate 9.6 mm",
    "Face stress at the shoe edge = linear surface extrapolation from 0.4 t and 1.0 t (IIW type a), t = two-board "
    "laminate thickness", "the peak at a rigid-insert edge is singular and grows with mesh refinement; the hot-spot "
    "value converges and is the structural stress the faces carry", 0.0096, "m", status="PROPOSED",
    cites=["SRC-C4-IIW"])
asm("ASM-C4-A3-STATION-MASS", "As-designed station masses: motor 84.2 g, ESC 7.6 g, bullets 4 g",
    "A3-R6a roll-up items: PRP-001 motor with its four M3 screws 84.2 g (params 81 g), PRP-002 stripped ESC 7.6 g "
    "(params 6.6 g), HRN-E03 phase bullets and short leads 4 g at 0.8 z_st on the tube",
    "team/A3/mass_model.csv and subsystems/propulsion/parts.csv (2026-11-10)", [0.0842, 0.0076, 0.004], "kg",
    status="PROPOSED")

GEOM, GU = dict(d3.GEOM), dict(d3.GU)
SHOE = {"tail_len": P + "fin_detail.station_collar.tail_m", "tongue_depth": P + "fin_detail.station_collar.tongue_depth_m",
        "leg_depth": P + "landing.shoe.leg_depth_m", "glue": P + "landing.shoe.glue_gap_m",
        "collar_len": P + "landing.shoe.collar_len_m", "z0_prop": "ASM-C4-SHOE-Z0-PROP"}
SHOE_U = {"tail_len": "m", "tongue_depth": "m", "leg_depth": "m", "glue": "m", "collar_len": "m", "z0_prop": "m"}
MATS = {"e_tail": "ASM-C4-SIM-TAIL-E", "e_link": "ASM-C4-SIM-LINK-E", "e_shoe": "ASM-C4-SIM-SHOE-E", "E": "ASM-J1-E-TUBE", "G": "ASM-C4-G-TUBE"}
MATS_U = {"e_tail": "Pa", "e_link": "Pa", "e_shoe": "Pa", "E": "Pa", "G": "Pa"}
LOADS = {"f_corner": "CL-C1-FOOT-CORNER", "mu_hi": "ASM-C1-FRICTION", "side_c5": "CL-C5-SIM3D-SIDE-LOAD",
         "foot_h": P + "cg.foot_height_m", "z_pad": P + "landing.pad_contact_z_m", "sf": P + "requirements.safety_factor_ult",
         "s_face": "ASM-C4-FACE-SIGMA", "hs_t": "ASM-C4-SIM-HOTSPOT-T", "s_cf": "ASM-C4-CF-SIGMA"}
LOADS_U = {"f_corner": "N", "mu_hi": "-", "side_c5": "N", "foot_h": "m", "z_pad": "m", "sf": "-", "s_face": "Pa",
           "hs_t": "m", "s_cf": "Pa"}


# ====================================================================== cache
def _key(name, obj):
    s = json.dumps([CODE, name, obj], sort_keys=True, default=lambda v: np.asarray(v).tolist())
    return name + "-" + hashlib.sha1(s.encode()).hexdigest()[:12]


def cached(name, obj, fn):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (_key(name, obj) + ".json")
    if f.exists():
        return json.loads(f.read_text())
    t0 = time.time()
    r = fn()
    r["_wall_s"] = round(time.time() - t0, 1)
    f.write_text(json.dumps(r, default=float))
    print(f"  {name}: {r['_wall_s']} s", flush=True)
    return r


# ====================================================================== shared model pieces
def tube_equiv(g, E, G):
    """Square bar a x a (laminate + both outer layers) with the CF tube's EI; GJ matched only in the in-house
    orthotropic bar. Returns bar E, the isotropic bar's G and J, the tube I and J."""
    a = g["layers"] * g["t_board"] + 2 * g["e_t"]
    r_o, r_i = g["od"] / 2, g["idd"] / 2
    I_t = math.pi / 4 * (r_o ** 4 - r_i ** 4)
    J_t = 2 * I_t
    I_sq, J_sq = a ** 4 / 12, 0.1406 * a ** 4
    E_bar = E * I_t / I_sq
    return {"a": a, "E_bar": E_bar, "G_iso": E_bar / 2.6, "J_sq": J_sq, "I_t": I_t, "J_t": J_t,
            "G_ortho": G * J_t / J_sq, "G_plate_matched": E_bar / 2.6 * J_sq / J_t}


def materials(g, k, eq, brace_E=None, ortho_bar=False):
    """D matrices in mesh_quarter.MAT order; isotropic list (E, nu) for SU2."""
    nu_core = k["e_core"] / (2 * k["g_core"]) - 1
    iso = [(k["e_face"], 0.3), (k["e_core"], nu_core), (k["e_strip"], 0.3), (eq["E_bar"], 0.3),
           (k["e_link"], 0.35), (k["e_shoe"], 0.3), (brace_E or k["e_strip"], 0.3), (k["e_tail"], 0.35)]
    D = [hx.d_iso(E, nu) for E, nu in iso]
    if ortho_bar:
        Eb = eq["E_bar"]
        D[3] = hx.d_ortho(Eb, Eb, Eb, 0.3, 0.3, 0.3, eq["G_ortho"], eq["G_ortho"], Eb / 2.6)
    return iso, D


def shoe_rects(g, k, geo, z_stp, variant):
    """D5 shoe as rigid rectangles (x0, z0, x1, z1) in the quarter's local frame."""
    x_s, x_te, hh = geo["x_step"], g["x_te"], g["hh"]
    if variant == "drawn":            # legs from the step down leg_depth (+ glue), cheeks over the strip ends
        z_leg = z_stp + k["glue"] - k["leg_depth"]
        return [(x_s, z_leg, x_te, z_stp + 1e-3), (x_s - k["collar_len"], hh - g["e_w"] - 0.002, x_s, hh + 0.01)]
    if variant == "proposed":         # CR-C4-30: cheeks to |z| z0_prop from x tip_clear (0.2666) to the TE
        return [(g["shoe_x0"], k["z0_prop"], x_te, hh + 0.01)]
    raise ValueError(variant)


def shoe_edges(g, k, geo, z_stp, variant):
    """Lower edges of the shoe on the bare board, [(x0, x1, z)] for the hot-spot read lines."""
    r = shoe_rects(g, k, geo, z_stp, variant)
    if variant == "drawn":
        return [(r[0][0], r[0][2], r[0][1]), (r[1][0], r[1][2], r[1][1])]
    return [(r[0][0], r[0][2], r[0][1])]


def quarter(g, k, side, h, h_loc, variant, brace_mode):
    geo = d3.geometry(g, side)
    top, z_stp, _ = d3.fin_top(g, geo, 10)
    s = d3.model_cfg(g, k["E"], k["G"], side)["struts"][0]
    ear = (g["tube_x"] + s["ear"][0], s["ear"][1], s["z_attach"])
    L = math.dist(ear, s["anchor"])
    kb = 1 / (L / s["EA"] + 1 / s["k_anchor"])
    br = {"z_ear": geo["z_ear"], "anchor": s["anchor"], "k": kb, "h": h} if brace_mode == "hex" else None
    m = mq.build(g, geo, top, z_stp, side=side, h=h, h_loc=h_loc, shoes=shoe_rects(g, k, geo, z_stp, variant),
                 brace=br, root_free=geo["root_free"], t_face=k["t_face"], z_split=[geo["z_ear"]],
                 tail=(g["tube_x"] + g["od"] / 2 + k["tail_len"], k["tongue_depth"]))
    m.update({"geo": geo, "z_stp": z_stp, "brace_spring": {"ear": ear, "anchor": s["anchor"], "k": kb, "L": L}})
    return m


def pad_cases(g, k, m):
    """L4 foot load at the C1 ground point split into its in-plane (x) and side (y) parts, limit values."""
    fc = k["f_corner"]
    fs = max(k["mu_hi"] * fc, k["side_c5"])
    Ppad = (g["x_te"] + k["foot_h"], 0.0, k["z_pad"])
    names = [n for n in m["markers"] if n.startswith("SHOE_")]
    out = {}
    for tag, F in (("PAD_X", (-fc, 0.0, 0.0)), ("PAD_Y", (0.0, fs, 0.0))):
        tr, res = mq.pad_tractions(m, F, Ppad, names)
        out[tag] = {"tractions": tr, "F": F, "resid": res}
    return out, fc, fs, Ppad


def su2_loads(tractions):
    out = []
    for name, t in tractions:
        mag = float(np.linalg.norm(t))
        if mag > 0:
            out.append((name, mag, tuple(np.asarray(t) / mag)))
    return out


def hex_force_vector(m, tractions):
    f = np.zeros(m["nodes"].shape)
    for name, t in tractions:
        f += hx.quad_traction_forces(m["nodes"], m["markers"][name], t)
    return f.ravel()


def clamp_nodes(m, names):
    return np.unique(np.concatenate([m["markers"][n].ravel() for n in names if n in m["markers"]]))


CLAMPS = ["ROOT_PIN", "LE_BOSS", "BAR_BOT", "BRACE_END"]


# ====================================================================== A. SU2 cantilever benchmark
def _beam(nz):
    L, b, hgt = 0.1, 0.01, 0.01
    nx, ny = 10 * nz, nz
    xs, ys, zs = np.linspace(0, L, nx + 1), np.linspace(0, b, ny + 1), np.linspace(0, hgt, nz + 1)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    nodes = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    nid = np.arange(len(nodes)).reshape(nx + 1, ny + 1, nz + 1)
    i, j, kk = np.meshgrid(np.arange(nx), np.arange(ny), np.arange(nz), indexing="ij")
    i, j, kk = i.ravel(), j.ravel(), kk.ravel()
    hexes = np.column_stack([nid[i, j, kk], nid[i + 1, j, kk], nid[i + 1, j + 1, kk], nid[i, j + 1, kk],
                             nid[i, j, kk + 1], nid[i + 1, j, kk + 1], nid[i + 1, j + 1, kk + 1], nid[i, j + 1, kk + 1]])
    bq, _ = hx.boundary_quads(hexes)
    xq = nodes[bq][:, :, 0]
    mk = {"root": bq[np.all(xq < 1e-12, axis=1)], "tip": bq[np.all(xq > L - 1e-12, axis=1)]}
    return nodes, hexes, mk, (L, b, hgt)


asm("ASM-C4-SIM-BENCH-LOAD", "Benchmark tip load 10 N on the 100 x 10 x 10 mm two-modulus cantilever",
    "Solver benchmark only (not aircraft data): steel/aluminium halves, 10 N tip shear", "closed-form reference "
    "exists (Euler-Bernoulli + Timoshenko shear)", 10.0, "N", status="PROPOSED")


@kit.calc("CALC-C4-SIM-BENCH", title="SU2 ELASTICITY cantilever benchmark, 3 meshes",
          inputs={"P_tip": "ASM-C4-SIM-BENCH-LOAD"}, units={"P_tip": "N"},
          equation="tip deflection, 10 N tip shear on a 100 x 10 x 10 mm cantilever, E 70/210 GPa halves; "
                   "reference d = P (7 L^3/(24 E1 I) + L^3/(24 E2 I)) + P L/(k G A), k = 5/6; meshes 2/4/8 elements "
                   "through the depth (aspect 1); Richardson on the three; hex8 in-house on the same meshes",
          cites=["SRC-C4-SU2", "SRC-C4-ROACHE"], tol=1e-6)
def bench(P_tip):
    def run():
        E1, E2, nu, P_ = 70e9, 210e9, 0.3, P_tip
        out = {"levels": []}
        for nz in (2, 4, 8):
            nodes, hexes, mk, (L, b, hgt) = _beam(nz)
            mat = (nodes[hexes][:, :, 0].mean(axis=1) > L / 2).astype(int)
            t = P_ / (b * hgt)
            u, info = su2io.run(RUNS / f"bench_{nz}", nodes, hexes, mat, [(E1, nu), (E2, nu)], mk, ["root"],
                                [("tip", t, (0, 0, 1))], threads=1)
            tip = np.isclose(nodes[:, 0], L)
            d_su2 = float(u[tip, 2].mean())
            K, _ = hx.assemble(nodes, hexes, [hx.d_iso(E1, nu), hx.d_iso(E2, nu)], mat)
            mdl = hx.Model(nodes, K)
            mdl.fix_nodes(np.unique(mk["root"]))
            mdl.build()
            uh = mdl.solve(hex_force_vector({"nodes": nodes, "markers": mk}, [("tip", (0, 0, t))])).reshape(-1, 3)
            out["levels"].append({"nz": nz, "n_hex": int(len(hexes)), "d_su2": d_su2,
                                  "d_hex": float(uh[tip, 2].mean()), "su2": info})
        I = 0.01 * 0.01 ** 3 / 12
        G2 = E2 / (2 * (1 + nu))
        G1 = E1 / (2 * (1 + nu))
        L = 0.1
        ref = P_ * (7 * L ** 3 / (24 * E1 * I) + L ** 3 / (24 * E2 * I)) + P_ * (L / 2) * (1 / G1 + 1 / G2) / (5 / 6 * 1e-4)
        out["ref"] = ref
        return out
    r = cached("bench", {} if P_tip == 10.0 else {"P": P_tip}, run)
    d = [lv["d_su2"] for lv in r["levels"]]
    p, ext, gci = richardson(d, 2.0)
    return {"err_coarse": d[0] / r["ref"] - 1, "err_mid": d[1] / r["ref"] - 1, "err_fine": d[2] / r["ref"] - 1,
            "err_extrap": ext / r["ref"] - 1, "order": p, "gci_fine": gci,
            "code_diff": max(abs(lv["d_hex"] / lv["d_su2"] - 1) for lv in r["levels"])}


def richardson(f, r):
    """Observed order, extrapolated value and fine-grid GCI (Fs 1.25) from coarse -> fine values f[0..2]."""
    f1, f2, f3 = f[2], f[1], f[0]
    e21, e32 = f2 - f1, f3 - f2
    if abs(e21) < 1e-300 or e32 / e21 <= 0:
        return -1.0, f1, abs(e21 / f1) if f1 else 0.0
    p = math.log(abs(e32 / e21)) / math.log(r)
    p = min(max(p, 0.5), 4.0)
    ext = f1 + (f1 - f2) / (r ** p - 1)
    gci = 1.25 * abs((f1 - f2) / f1) / (r ** p - 1)
    return p, ext, gci


# ====================================================================== B + C. SU2 statics on the quarter
def face_field(m, D, u):
    """In-plane principal |stress| in the two outer paper faces (centroids): returns x, z, sigma, side (-1/+1)."""
    lay, mat = m["layer"], m["mat"]
    last = len(m["levels"]) - 2
    sel = np.where(((lay == 0) | (lay == last)) & (mat == mq.MAT["FACE"]))[0]
    s = hx.centroid_stress(m["nodes"], m["hexes"], D, mat, u.ravel(), sel)
    sx, sz, txz = s[:, 0], s[:, 2], s[:, 4]
    c = (sx + sz) / 2
    r = np.hypot((sx - sz) / 2, txz)
    sig = np.maximum(np.abs(c + r), np.abs(c - r))
    cen = m["nodes"][m["hexes"][sel]].mean(axis=1)
    return cen[:, 0], cen[:, 2], sig, np.sign(cen[:, 1]), sel


def hotspot(xs, zs, sig, side, edges, t, n=41):
    """IIW hot-spot along each shoe lower edge: max over x and both faces of 1.67 s(0.4t) - 0.67 s(1.0t)."""
    best = (0.0, None)
    for sd in (-1, 1):
        msk = side == sd
        pts = np.column_stack([xs[msk], zs[msk]])
        for x0, x1, ze in edges:
            xq = np.linspace(x0 + 0.02 * (x1 - x0), x1 - 0.02 * (x1 - x0), n)
            s4 = griddata(pts, sig[msk], np.column_stack([xq, np.full(n, ze - 0.4 * t)]), method="linear")
            s10 = griddata(pts, sig[msk], np.column_stack([xq, np.full(n, ze - 1.0 * t)]), method="linear")
            hs = 1.67 * s4 - 0.67 * s10
            i = int(np.nanargmax(hs))
            if hs[i] > best[0]:
                best = (float(hs[i]), {"x": float(xq[i]), "z_edge": ze, "face": int(sd), "s04": float(s4[i]),
                                       "s10": float(s10[i])})
    return best


def far_max(m, xs, zs, sig, shoes, t):
    """Largest face stress at least one laminate thickness away from the shoe and from the root / boss clamps."""
    zr = np.vectorize(m["zr"])(xs)
    ok = (zs - zr > t) & ~((xs < m["geo"]["x_le"] + t) & (zs < m["geo"]["z_clamp"] + t))
    for (xa, za, xb, zb) in shoes:
        dx = np.maximum(np.maximum(xa - xs, xs - xb), 0)
        dz = np.maximum(np.maximum(za - zs, zs - zb), 0)
        ok &= np.hypot(dx, dz) > t
    i = int(np.argmax(np.where(ok, sig, 0)))
    return float(sig[i]), (float(xs[i]), float(zs[i]))


def su2_quarter(g, k, side, level, variant):
    """One quarter, one mesh level, both L4 parts (PAD_X in-plane, PAD_Y side). Displacements from the in-house hex8
    (direct solve, same element as SU2) on every level; SU2 ELASTICITY on the levels in SU2_LEVELS (drawn shoe), its
    field compared node by node and its hot-spot reported beside the hex8 one."""
    h, h_loc = STRESS_LEVELS[level]
    run_su2 = level in SU2_LEVELS and variant == "drawn"
    key = {"g": {a: b for a, b in g.items()}, "k": k, "side": side, "level": level, "variant": variant,
           "su2": run_su2}

    def run():
        m = quarter(g, k, side, h, h_loc, variant, "hex")
        eq = tube_equiv(g, k["E"], k["G"])
        iso, D = materials(g, k, eq, brace_E=m["brace"]["E_eq"])
        cases, fc, fs, Ppad = pad_cases(g, k, m)
        res = {"n_nodes": int(len(m["nodes"])), "n_hex": int(len(m["hexes"])), "fc": fc, "fs": fs, "cases": {},
               "h": h, "h_loc": h_loc}
        foot_n = np.unique(np.concatenate([m["markers"][n].ravel() for n in m["markers"] if n.startswith("SHOE_")]))
        K, _ = hx.assemble(m["nodes"], m["hexes"], D, m["mat"])
        mdl = hx.Model(m["nodes"], K)
        mdl.fix_nodes(clamp_nodes(m, CLAMPS))
        mdl.build()
        res["n_dof"] = int(mdl.Kr.shape[0])
        U, US = {}, {}
        for cname, cs in cases.items():
            uh = mdl.solve(hex_force_vector(m, cs["tractions"])).reshape(-1, 3)[:len(m["nodes"])]
            U[cname] = uh
            r = {"foot": uh[foot_n].mean(axis=0).tolist(), "resid_load": float(cs.get("resid", 0.0)),
                 "resid_solve": mdl.last_resid}
            if run_su2:
                u, info = su2io.run(RUNS / f"q_{side}_{variant}_L{level}_{cname}", m["nodes"], m["hexes"], m["mat"],
                                    iso, m["markers"], [c for c in CLAMPS if c in m["markers"]],
                                    su2_loads(cs["tractions"]), threads=THREADS, tol=SU2_TOL, iters=SU2_ITERS)
                US[cname] = u
                r["su2"] = info
                r["max_rel_diff"] = float(np.max(np.abs(uh - u)) / np.max(np.abs(uh)))
                r["foot_su2"] = u[foot_n].mean(axis=0).tolist()
            res["cases"][cname] = r
        t = k["hs_t"]
        shoes = shoe_rects(g, k, m["geo"], m["z_stp"], variant)
        edges = shoe_edges(g, k, m["geo"], m["z_stp"], variant)

        def l4(Uc):
            out = {}
            for sgn in (1, -1):
                u = Uc["PAD_X"] + sgn * Uc["PAD_Y"]
                xs, zs, sig, sd, _ = face_field(m, D, u)
                hs, where = hotspot(xs, zs, sig, sd, edges, t)
                ins = np.ones(len(xs), bool)
                for (xa, za, xb, zb) in shoes:
                    ins &= ~((xs > xa) & (xs < xb) & (zs > za) & (zs < zb))
                ipk = int(np.argmax(np.where(ins, sig, 0)))
                fm, fwhere = far_max(m, xs, zs, sig, shoes, t)
                st = np.where(np.isin(m["layer"], (-100, 100)) & (m["mat"] == mq.MAT["STRIP"]))[0]
                ss = hx.centroid_stress(m["nodes"], m["hexes"], D, m["mat"], u.ravel(), st)
                cst = m["nodes"][m["hexes"][st]].mean(axis=1)
                ssx, ssz, sxz = ss[:, 0], ss[:, 2], ss[:, 4]
                s_ip = np.abs((ssx + ssz) / 2) + np.hypot((ssx - ssz) / 2, sxz)
                tau = np.hypot(ss[:, 3], ss[:, 5])          # yz, xy: shear on the strip-to-face bond plane
                aft = cst[:, 0] < shoes[-1][0] - 1e-9 if variant == "drawn" else cst[:, 0] < g["shoe_x0"] - 1e-9
                i_s, i_t = int(np.argmax(np.where(aft, s_ip, 0))), int(np.argmax(np.where(aft, tau, 0)))
                out["+" if sgn > 0 else "-"] = {
                    "strip_lim": float(s_ip[i_s]), "strip_at": cst[i_s, [0, 2]].tolist(),
                    "strip_tau_lim": float(tau[i_t]), "strip_tau_at": cst[i_t, [0, 2]].tolist(),
                    "hotspot_lim": hs, "hotspot_at": where, "peak_lim": float(sig[ipk]),
                    "peak_at": [float(xs[ipk]), float(zs[ipk])], "far_lim": fm, "far_at": fwhere,
                    "foot_defl": float(np.linalg.norm(u[foot_n].mean(axis=0)))}
                if sgn > 0 and Uc is U:
                    res["field"] = {"x": xs[sd > 0].tolist(), "z": zs[sd > 0].tolist(), "s": sig[sd > 0].tolist(),
                                    "fin_poly": m["fin_poly"].tolist(), "shoes": shoes, "edges": edges}
            return out
        res["L4"] = l4(U)
        if US:
            res["L4_su2"] = l4(US)
        return res
    return cached("su2q", key, run)


def plate_face(g, k, side, z0, mesh=(36, 30)):
    """Shell model on the same rigid shoe rectangle (x >= tip_clear_x, z >= z0): hot-spot and peak, L4 limit."""
    g2 = dict(g, shoe_z0=z0)
    G_m = tube_equiv(g, k["E"], k["G"])["G_plate_matched"]          # same isotropic bar as the SU2 model
    mdl = fe.build_q(d3.model_cfg(g2, k["E"], G_m, side, mesh=mesh, layers=g["layers"], k_root=None))
    pr = mdl.cfg["fin"]["props"]
    nodes = mdl.nodes
    geo = d3.geometry(g2, side)
    nz = mdl.cfg["nz"]
    shoe = [n for (i, j), n in mdl.fin_id.items() if nodes[n][0] >= geo["x_step"] - 1e-9
            and nodes[n][2] >= nodes[mdl.fin_id[(i, nz)]][2] - k["patch"] - 1e-9]
    Ppad = np.array([g["x_te"] + k["foot_h"], 0.0, k["z_pad"]])
    fc = k["f_corner"]
    fs = max(k["mu_hi"] * fc, k["side_c5"])
    nu = pr["nu"]
    Qf = k["e_face"] / (1 - nu * nu) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    C3 = np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    out = {}
    for sgn in (1, -1):
        u = fe.static(mdl, d3.shoe_loads(nodes, shoe, np.array([-fc, sgn * fs, 0]), Ppad))
        xs, zs, sg, sd = [], [], [], []
        for ns, xz, pe in mdl.shells:
            ue = np.concatenate([u[6 * n:6 * n + 6] for n in ns])
            Nv, Mv = fe.shell_q4_resultants(xz, pe, ue)
            e0, kap = np.linalg.solve(pe["A"] * C3, Nv), np.linalg.solve(pe["D"] * C3, Mv)
            for zf, s_ in ((pe["z_face_out"], 1), (-pe["z_face_out"], -1)):
                sx, sz, txz = Qf @ (e0 + zf * kap)
                xs.append(xz[:, 0].mean()), zs.append(xz[:, 1].mean()), sd.append(s_)
                sg.append(abs((sx + sz) / 2) + math.hypot((sx - sz) / 2, txz))
        xs, zs, sg, sd = map(np.array, (xs, zs, sg, sd))
        x0 = g["shoe_x0"]
        hs, where = hotspot(xs, zs, sg, sd, [(x0, g["x_te"], z0)], k["hs_t"])
        ins = ~((xs > x0) & (zs > z0))
        out["+" if sgn > 0 else "-"] = {"hotspot_lim": hs, "hotspot_at": where, "peak_lim": float(sg[ins].max())}
    return out


FACE_IN = {**GEOM, **SHOE, **MATS, **LOADS, "patch": "ASM-C4-FOOT-PATCH"}
FACE_U = {**GU, **SHOE_U, **MATS_U, **LOADS_U, "patch": "m"}


def _split(kw):
    g = {n: kw[n] for n in GEOM}
    k = {n: kw[n] for n in kw if n not in GEOM and n != "s_cf"}      # s_cf only in face(): keeps cache keys
    for n in ("e_face", "e_core", "g_core", "e_strip", "t_face"):
        k[n] = g[n]
    return g, k


SU2_TRIALS = [("CONJUGATE_GRADIENT", 1, 1500), ("RESTARTED_FGMRES", 2, 1500)]   # (solver, ILU fill-in, iterations)


def su2_trial(g, k, solver, fill, iters):
    """SU2 ELASTICITY on the level-1 upper quarter (shoe as drawn), L4 side part PAD_Y, against the hex8 direct solve
    on the same mesh. Records SU2's final log10 linear residual, iterations, wall time and the field difference."""
    key = {"g": g, "k": k, "solver": solver, "fill": fill, "iters": iters}

    def run():
        h, h_loc = STRESS_LEVELS[1]
        m = quarter(g, k, "upper", h, h_loc, "drawn", "hex")
        eq = tube_equiv(g, k["E"], k["G"])
        iso, D = materials(g, k, eq, brace_E=m["brace"]["E_eq"])
        cases, _, _, _ = pad_cases(g, k, m)
        K, _ = hx.assemble(m["nodes"], m["hexes"], D, m["mat"])
        mdl = hx.Model(m["nodes"], K)
        mdl.fix_nodes(clamp_nodes(m, CLAMPS))
        mdl.build()
        uh = mdl.solve(hex_force_vector(m, cases["PAD_Y"]["tractions"])).reshape(-1, 3)[:len(m["nodes"])]
        u, info = su2io.run(RUNS / f"trial_{solver}_ilu{fill}", m["nodes"], m["hexes"], m["mat"], iso, m["markers"],
                            [c for c in CLAMPS if c in m["markers"]], su2_loads(cases["PAD_Y"]["tractions"]),
                            threads=THREADS, tol=1e-9, iters=iters, fill=fill, solver=solver)
        hist = info.get("history", {})
        return {"linres_log10": float(hist.get("LinSolRes", "nan")), "iters": int(float(hist.get("LinSolIter", 0))),
                "wall_s": info["wall_s"], "n_dof": int(mdl.Kr.shape[0]),
                "max_rel_diff": float(np.max(np.abs(uh - u)) / np.max(np.abs(uh))),
                "hex_resid": mdl.last_resid}
    return cached("su2trial", key, run)


@kit.calc("CALC-C4-SIM-CODES", title="SU2 ELASTICITY on the fin quarter: solver trials against the hex8 direct solve",
          inputs=FACE_IN, units=FACE_U, tol=1e-3, cites=["SRC-C4-SU2"],
          equation="upper quarter, mesh level 1 (8 mm / 2 mm, 71 k DOF), D5 shoe as drawn, L4 side part; SU2 v8 "
                   "linear solvers available in this build (no PaStiX): CG + ILU(1) and restarted FGMRES(200) + ILU(2), 1500 it each, "
                   "tol 1e-9; converged when log10 residual <= -6; field difference max |u_hex - u_su2| / max |u_hex|")
def codes(**kw):
    g, k = _split(kw)
    out = {}
    for solver, fill, iters in SU2_TRIALS:
        r = su2_trial(g, k, solver, fill, iters)
        tag = f"{solver.lower()}_ilu{fill}"
        out[f"{tag}_linres_log10"] = r["linres_log10"]
        out[f"{tag}_iters"] = r["iters"]
        out[f"{tag}_wall_s"] = r["wall_s"]
        out[f"{tag}_rel_diff"] = r["max_rel_diff"]
    out["best_rel_diff"] = min(out[f"{s.lower()}_ilu{f}_rel_diff"] for s, f, _ in SU2_TRIALS)
    out["converged"] = any(out[f"{s.lower()}_ilu{f}_linres_log10"] <= -6 for s, f, _ in SU2_TRIALS)
    return out


@kit.calc("CALC-C4-SIM-FACE", title="Fin face hot-spot stress at the D5 shoe, SU2, 3 meshes",
          inputs=FACE_IN, units=FACE_U, tol=2e-3, cites=["SRC-C4-SU2", "SRC-C4-IIW", "SRC-C4-ROACHE"],
          assumes=["ASM-C4-SIM-SHOE-E", "ASM-C4-SIM-LINK-E", "ASM-C4-SIM-HOTSPOT-T", "ASM-C4-FACE-SIGMA"],
          equation="hex8 direct solve (identical to SU2 ELASTICITY, CALC-C4-SIM-CODES); L4 limit: F = (-F_corner, +/- max(mu F_corner, F_C5), 0) at the C1 ground point through the rigid "
                   "shoe (least-norm tractions on its outer faces, exact force and moment); face stress = in-plane "
                   "principal |sigma| at the outer-face element centroids (sigma = D B u); hot-spot = 1.67 s(0.4t) - "
                   "0.67 s(1.0t) below each shoe lower edge, max over x, both faces, both senses; ultimate = sf x "
                   "limit; MS = s_face / s_ult - 1; meshes 8 mm global, 2/1/0.5 mm in the tip box; Richardson r 2")
def face(**kw):
    g, k = _split(kw)
    out = {}
    for variant in ("drawn", "proposed"):
        hs, pk_, far = [], [], []
        for lv in (1, 2, 3):
            r = su2_quarter(g, k, "upper", lv, variant)
            hs.append(max(r["L4"][s]["hotspot_lim"] for s in "+-"))
            pk_.append(max(r["L4"][s]["peak_lim"] for s in "+-"))
            far.append(max(r["L4"][s]["far_lim"] for s in "+-"))
        p, ext, gci = richardson(hs, 2.0)
        ult = k["sf"] * max(ext, hs[2])
        out[f"hs_{variant}_lim_pa"] = hs
        out[f"peak_{variant}_lim_pa"] = pk_
        out[f"far_{variant}_lim_pa"] = far
        out[f"hs_{variant}_ext_lim_pa"] = ext
        out[f"hs_{variant}_gci"] = gci
        out[f"hs_{variant}_order"] = p
        out[f"face_{variant}_ult_pa"] = ult
        out[f"ms_{variant}"] = k["s_face"] / ult - 1
        out[f"ms_far_{variant}"] = k["s_face"] / (k["sf"] * far[2]) - 1
    rg = su2_quarter(g, k, "upper", "G", "drawn")
    out["hs_drawn_global4_lim_pa"] = max(rg["L4"][s_]["hotspot_lim"] for s_ in "+-")
    out["global_check_rel"] = out["hs_drawn_global4_lim_pa"] / out["hs_drawn_lim_pa"][1] - 1
    for variant in ("drawn", "proposed"):
        rl = su2_quarter(g, k, "lower", 2, variant)
        out[f"hs_{variant}_lower_L2_lim_pa"] = max(rl["L4"][s_]["hotspot_lim"] for s_ in "+-")
    out["levels"] = {str(lv): list(STRESS_LEVELS[lv]) for lv in (1, 2, 3)}
    geo = d3.geometry(g, "upper")
    _, z_stp, _ = d3.fin_top(g, geo, 10)
    z_leg = z_stp + k["glue"] - k["leg_depth"]
    fs = max(k["mu_hi"] * k["f_corner"], k["side_c5"])
    m_tot = fs * (k["z_pad"] - z_leg)                                  # side-load moment about the leg edge, N m
    lever = g["layers"] * g["t_board"] - g["t_face"]
    width = g["x_te"] - geo["x_step"]
    out["m_side_leg_nm"] = m_tot
    for variant in ("drawn", "proposed"):
        r3 = su2_quarter(g, k, "upper", 3, variant)
        out[f"strip_{variant}_lim_pa"] = max(r3["L4"][s_]["strip_lim"] for s_ in "+-")
        out[f"strip_tau_{variant}_lim_pa"] = [max(su2_quarter(g, k, "upper", lv, variant)["L4"][s_]["strip_tau_lim"]
                                                  for s_ in "+-") for lv in (1, 2, 3)]
        out[f"ms_strip_{variant}"] = kw["s_cf"] / (k["sf"] * out[f"strip_{variant}_lim_pa"]) - 1
        out[f"foot_defl_{variant}_m"] = max(r3["L4"][s_]["foot_defl"] for s_ in "+-")
    out["board_share_3d"] = out["hs_drawn_ext_lim_pa"] * g["t_face"] * lever * width / m_tot
    for variant, z0 in (("drawn", None), ("proposed", k["z0_prop"])):
        geo = d3.geometry(g, "upper")
        _, z_stp, _ = d3.fin_top(g, geo, 10)
        zz = z_stp + k["glue"] - k["leg_depth"] if z0 is None else z0
        pf = plate_face(g, k, "upper", zz)
        out[f"plate_hs_{variant}_lim_pa"] = max(pf[s]["hotspot_lim"] for s in "+-")
        out[f"plate_peak_{variant}_lim_pa"] = max(pf[s]["peak_lim"] for s in "+-")
    out["board_share_shell"] = out["plate_hs_drawn_lim_pa"] * g["t_face"] * lever * width / m_tot
    return out


# ====================================================================== D + E. in-house hex8 modes and stiffness
def hex_quarter_model(g, k, side, h, as_designed=True, matched_plate=False, masses=None):
    """Constrained 3-D quarter like the shell model: tube root master (springs), tube-end master, station rigid body
    on mount springs, collar master with the brace spring at the ear, root pinned on the mid-plane, boss clamp."""
    m = quarter(g, k, side, h, h, "drawn", None)
    eq = tube_equiv(g, k["E"], k["G"])
    iso, D = materials(g, k, eq, ortho_bar=not matched_plate)
    rho_board = g["areal"] / g["t_board"]
    a = eq["a"]
    rho_bar = g["mu"] / (a * a)
    rho = [rho_board, rho_board, g["rho_cf"], rho_bar, 0.0, rho_board, 0.0, rho_board]
    K, M = hx.assemble(m["nodes"], m["hexes"], D, m["mat"], rho)
    nodes = m["nodes"]
    geo = m["geo"]
    x_t = g["tube_x"]
    cfg = d3.model_cfg(g, k["E"], k["G"], side)
    # lumped masses on hex nodes: ESC pad, foot (shoe)
    lump = np.zeros(len(nodes))
    for i_m, (mass, (xm, zm)) in enumerate(cfg["fin_masses"]):
        if masses and i_m == 0:
            mass = masses["esc"]
        dd = np.hypot(nodes[:, 0] - xm, nodes[:, 2] - zm)
        sel = np.where(np.abs(dd - dd.min()) < 1e-9)[0]
        lump[sel] += mass / len(sel)
    M = M + hx.sp.diags(np.repeat(lump, 3))
    mdl = hx.Model(nodes, K, M)
    z0, z_end = geo["z_clamp"], geo["z_end"]
    in_bar = np.abs(nodes[:, 0] - x_t) <= a / 2 + 1e-9
    m_root = mdl.add_master((x_t, 0, z0))
    m_end = mdl.add_master((x_t, 0, z_end))
    m_col = mdl.add_master((x_t, 0, geo["z_ear"]))
    mdl.tie(np.where(in_bar & np.isclose(nodes[:, 2], z0))[0], m_root)
    mdl.tie(np.where(in_bar & np.isclose(nodes[:, 2], z_end))[0], m_end)
    col = np.where(in_bar & np.isclose(nodes[:, 2], geo["z_ear"]))[0]
    if len(col) < 4:
        raise RuntimeError("no bar node row at the ear height")
    mdl.tie(col, m_col)
    fixed = clamp_nodes(m, ["ROOT_PIN", "LE_BOSS"])
    link_bot = np.where((nodes[:, 0] > x_t + a / 2 + 1e-9) & np.isclose(nodes[:, 2], z0))[0]
    mdl.fix_nodes(np.setdiff1d(np.concatenate([fixed, link_bot]), np.where(in_bar)[0]))
    if as_designed:
        mdl.fix_master(m_root, (0, 1, 2))
        mdl.spring_ground(m_root, [0, 0, 0, g["k_root"], g["k_root"], 1e9])
    else:
        mdl.fix_master(m_root)
    bs = m["brace_spring"]
    n = (np.asarray(bs["anchor"]) - np.asarray(bs["ear"])) / bs["L"]
    mdl.spring_point_axial(m_col, bs["ear"], n, bs["k"])
    m_c, m_b = g["cb_mass"]
    mdl.point_mass_master(m_col, m_c + m_b / 2, (x_t, 0, geo["z_ear"]))
    st = None
    parts = cfg["station"]["parts"]
    if masses:
        parts = [(masses["motor"], parts[0][1], parts[0][2])] + parts[1:]
        mdl.point_mass_master(m_col, masses["bullets"], (x_t + 0.01, 0, 0.8 * g["z_st"]))
    Ms = fe.rigid_mass(parts)
    if as_designed:
        st = mdl.add_master((x_t, 0, z_end))
        mdl.spring_between(m_end, st, [1e8, 1e8, 1e8, g["k_rock"], g["k_rock"], g["k_twist"]])
        mdl.mass_master(st, Ms)
    else:
        mdl.mass_master(m_end, Ms)
    mdl.build()
    mdl.Ms, mdl.st, mdl.m_end, mdl.mesh = Ms, (st if st is not None else m_end), m_end, m
    return mdl


def hex_modes(mdl, n=14):
    f, V = mdl.modes(n, shift_hz=40.0)
    sd = mdl.mdofs(mdl.st)
    out = []
    for i in range(V.shape[1]):
        v = V[:, i]
        tot = float(v @ (mdl.Mx @ v))
        us = v[sd]
        ke = float(us @ mdl.Ms @ us) / tot
        ey, ex, erz = mdl.Ms[1, 1] * us[1] ** 2, mdl.Ms[0, 0] * us[0] ** 2, mdl.Ms[5, 5] * us[5] ** 2
        ery = mdl.Ms[4, 4] * us[4] ** 2
        kind = "fin panel" if ke < 0.10 else ("lateral-torsion" if max(ey, erz) >= max(ex, ery) else "fore-aft")
        out.append((float(f[i]), round(ke, 3), kind))
    return out


MODE_IN = {**GEOM, **MATS, **SHOE, **d3.RPM, "a3": "ASM-C4-A3-STATION-MASS", "sep_min": d3.LIMIT_SEP}
MODE_U = {**GU, **MATS_U, **SHOE_U, **d3.RU, "a3": "kg", "sep_min": "-"}


def modes_level(g, k, side, level, a3):
    h = MODAL_LEVELS[level]
    key = {"g": g, "k": k, "side": side, "level": level, "a3": a3}

    def run():
        masses = {"motor": a3[0], "esc": a3[1], "bullets": a3[2]}
        mdl = hex_quarter_model(g, k, side, h, as_designed=True, masses=masses)
        md = hex_modes(mdl)
        r = {"modes": md, "n_dof": int(mdl.Kr.shape[0]), "n_hex": int(len(mdl.mesh["hexes"]))}
        # E: model-form statics against the shell model, matched tube (isotropic bar), clamped root, rigid mount
        mdm = hex_quarter_model(g, k, side, h, as_designed=False, matched_plate=True)
        comp = {}
        for name, dof, val in (("x", 0, 1.0), ("y", 1, 1.0), ("tz", 5, 0.1)):
            F = np.zeros(mdm.N)
            F[mdm.mdofs(mdm.m_end)[dof]] = val
            u = mdm.solve(F)
            comp[name] = float(u[mdm.mdofs(mdm.m_end)[dof]] / val)
        r["compliance_hex"] = comp
        return r
    return cached("modes", key, run)


def plate_station(g, k, side, a3=None, matched=False):
    """Shell model station modes (R4 mesh) and, when matched, the station compliance with the isotropic-bar tube."""
    g2 = dict(g)
    if a3 is not None:
        g2["m_motor"], g2["m_esc"] = a3[0], a3[1]
    eq = tube_equiv(g, k["E"], k["G"])
    G = eq["G_plate_matched"] if matched else k["G"]
    cfg = d3.model_cfg(g2, k["E"], G, side, layers=g["layers"], k_root=None if matched else "nom",
                       k_rock=None if matched else "nom")
    if a3 is not None:
        cfg["tube_masses"].append((a3[2], 0.8 * g["z_st"]))
    mdl = fe.build_q(cfg)
    if not matched:
        return d3.station_modes(mdl)
    comp = {}
    for name, dof, val in (("x", 0, 1.0), ("y", 1, 1.0), ("tz", 5, 0.1)):
        ld = [0.0] * 6
        ld[dof] = val
        u = fe.static(mdl, [(mdl.i_end, tuple(ld))])
        comp[name] = float(u[6 * mdl.i_end + dof] / val)
    return comp


def sep_of(fs, rpm):
    pts = d3.forcing(*rpm)
    return min(abs(f / v - 1) for f in fs for v in pts.values())


@kit.calc("CALC-C4-SIM-MODES", title="Station modes, 3-D solid quarters with A3 masses, 3 meshes",
          inputs=MODE_IN, units=MODE_U, tol=2e-3, cites=["SRC-C4-ROACHE"],
          assumes=["ASM-C4-SIM-LINK-E", "ASM-C4-SIM-SHOE-E", "ASM-C4-A3-STATION-MASS", "ASM-C4-MOUNT-K-ROCK",
                   "ASM-C4-ROOT-K", "ASM-C4-ANCHOR-K"],
          equation="hex8 laminate (faces, cores, strips, shoe), CF tube as an orthotropic square bar (E_z I = E I_tube, "
                   "G_xz J_sq = G J_tube), rigid ties to the tube root (k_root springs), tube end, collar (brace "
                   "spring k = 1/(L/EA + 1/k_anchor) at the ear); station rigid body (A3 motor 84.2 g) on the mount "
                   "springs; consistent mass; eigsh shift-invert; station mode = KE share >= 0.10; meshes 8/5.7/4 mm "
                   "(bar and link at half size), Richardson r sqrt 2; separation = min |f/f_forcing - 1| over 1P/2P hover/cruise and 1P max")
def modes3d(**kw):
    g = {n: kw[n] for n in GEOM}
    k = {n: kw[n] for n in MATS}
    k.update({n: g[n] for n in ("e_face", "e_core", "g_core", "e_strip")})
    for n in ("e_tail", "e_link", "e_shoe", "glue", "leg_depth", "collar_len", "z0_prop", "tail_len", "tongue_depth"):
        k[n] = kw[n]
    k["t_face"] = g["t_face"]
    rpm = (kw["rpm_h"], kw["rpm_c"], kw["rpm_x"])
    out = {}
    for side in d3.SIDES:
        f1 = []
        for lv in (1, 2, 3):
            r = modes_level(g, k, side, lv, kw["a3"])
            st = [f for f, ke, kind in r["modes"] if ke >= 0.10]
            f1.append(st[0])
            out[f"f_{side[:2]}_L{lv}"] = [round(f, 2) for f, _, _ in r["modes"][:6]]
            out[f"ndof_{side[:2]}_L{lv}"] = r["n_dof"]
            if lv == 3:
                hc = r["compliance_hex"]
        p, ext, gci = richardson(f1, 2 ** 0.5)
        out[f"f1_{side[:2]}"] = f1
        out[f"f1_{side[:2]}_ext"] = ext
        out[f"f1_{side[:2]}_gci"] = gci
        out[f"f1_{side[:2]}_order"] = p
        r3 = modes_level(g, k, side, 3, kw["a3"])
        st3 = [f for f, ke, kind in r3["modes"] if ke >= 0.10]
        out[f"kinds_{side[:2]}"] = [kind for f, ke, kind in r3["modes"] if ke >= 0.10][:3]
        out[f"sep_{side[:2]}"] = sep_of([ext] + st3[1:3], rpm)
        pm = plate_station(g, k, side, a3=kw["a3"])
        p0 = plate_station(g, k, side)
        out[f"plate_f1_{side[:2]}_a3"] = pm["f_st1"]
        out[f"plate_f1_{side[:2]}_r4"] = p0["f_st1"]
        out[f"plate_sep_{side[:2]}_a3"] = sep_of(pm["f_st"][:3], rpm)
        out[f"ratio_{side[:2]}"] = ext / pm["f_st1"]
        pc = plate_station(g, k, side, matched=True)
        for d_ in ("x", "y", "tz"):
            out[f"k_ratio_{side[:2]}_{d_}"] = pc[d_] / hc[d_]          # 3-D stiffness / shell stiffness
    out["f1_min"] = min(out["f1_up_ext"], out["f1_lo_ext"])
    out["sep_min"] = min(out["sep_up"], out["sep_lo"])
    out["plate_sep_min_a3"] = min(out["plate_sep_up_a3"], out["plate_sep_lo_a3"])
    return out


# ====================================================================== claims
kit.claim("CL-C4-SIM-BENCH-ERR", "SU2 cantilever error, extrapolated", calc="CALC-C4-SIM-BENCH", output="err_extrap",
          unit="-", limit=("<=", 0.01), how="Re-run sim_fin.py; compare with the closed-form two-modulus cantilever.")
kit.claim("CL-C4-SIM-BENCH-CODES", "In-house hex8 vs SU2, cantilever", calc="CALC-C4-SIM-BENCH", output="code_diff",
          unit="-", limit=("<=", 1e-3), how="Re-run sim_fin.py (same meshes in both codes).")
kit.claim("CL-C4-SIM-CODE-DIFF", "In-house hex8 vs SU2, fin quarter (best SU2 solver trial)", calc="CALC-C4-SIM-CODES",
          output="best_rel_diff", unit="-", parts=["FIN-001-UR"],
          how="Re-run sim_fin.py; SU2 needs a direct solver (PaStiX build) or a stronger preconditioner to converge here.")
kit.claim("CL-C4-SIM-FACE-DRAWN", "Face hot-spot stress, D5 shoe as drawn, ult", calc="CALC-C4-SIM-FACE",
          output="face_drawn_ult_pa", unit="Pa", limit=("<=", "ASM-C4-FACE-SIGMA"),
          parts=["FIN-001-UR", "FIN-001-UL", "FIN-001-LR", "FIN-001-LL"],
          how="T-C4-FIN-PROOF on the test article (CR-C4-33) decides; strain gauge 5 mm below the leg edge.")
kit.claim("CL-C4-SIM-MS-FACE-DRAWN", "Face MS at the D5 shoe as drawn (3-D)", calc="CALC-C4-SIM-FACE",
          output="ms_drawn", unit="-", limit=(">=", 0.0), parts=["FIN-001-UR"],
          how="T-C4-FIN-PROOF (CR-C4-33).")
kit.claim("CL-C4-SIM-MS-FACE-PROP", "Face MS with the CR-C4-30 cheeks (3-D)", calc="CALC-C4-SIM-FACE",
          output="ms_proposed", unit="-", limit=(">=", 0.0), parts=["FIN-001-UR"],
          how="T-C4-FIN-PROOF with the extended cheeks (CR-C4-33).")
kit.claim("CL-C4-SIM-F1-UP", "First station mode, upper, 3-D, A3 masses", calc="CALC-C4-SIM-MODES",
          output="f1_up_ext", unit="Hz", parts=["FIN-001-UR", "FIN-002-R"], how="T-C4-TAP-D3 on the finished wing.")
kit.claim("CL-C4-SIM-F1-LO", "First station mode, lower, 3-D, A3 masses", calc="CALC-C4-SIM-MODES",
          output="f1_lo_ext", unit="Hz", parts=["FIN-001-LR", "FIN-002-R"], how="T-C4-TAP-D3 on the finished wing.")
kit.claim("CL-C4-SIM-SEP", "Station-mode separation from 1P/2P, 3-D", calc="CALC-C4-SIM-MODES", output="sep_min",
          unit="-", limit=(">=", d3.LIMIT_SEP), verifies=["R-VIBRATION"],
          parts=["FIN-001-UR", "FIN-001-LR", "FIN-002-R"],
          how="T-C4-TAP-D3: tap each motor bell, FFT; first station peak at least 20 % from 90/98/181/197/155 Hz.")
kit.claim("CL-C4-SIM-SEP-PLATE-A3", "Separation, shell model with A3 masses", calc="CALC-C4-SIM-MODES",
          output="plate_sep_min_a3", unit="-", limit=(">=", d3.LIMIT_SEP), parts=["FIN-001-LR"],
          how="Re-run sim_fin.py; T-C4-TAP-D3.")

kit.claim("CL-C4-SIM-MS-FACE-FAR", "Face MS away from the shoe and clamps, shoe as drawn (3-D)", calc="CALC-C4-SIM-FACE",
          output="ms_far_drawn", unit="-", limit=(">=", 0.0), parts=["FIN-001-UR"],
          how="T-C4-FIN-PROOF (CR-C4-33); largest face element at least one laminate thickness from the shoe edge.")
kit.claim("CL-C4-SIM-MS-STRIP", "Edge-strip MS under L4, shoe as drawn (3-D)", calc="CALC-C4-SIM-FACE",
          output="ms_strip_drawn", unit="-", limit=(">=", 0.0), parts=["FIN-001-UR"],
          how="T-C4-FIN-PROOF; strain gauge on a strip 10 mm forward of the collar cheek.")
kit.claim("CL-C4-SIM-FOOT-DEFL", "Foot deflection under L4 limit, shoe as drawn (3-D)", calc="CALC-C4-SIM-FACE",
          output="foot_defl_drawn_m", unit="m", parts=["FIN-001-UR"],
          how="T-C4-FIN-PROOF dial gauge at the pad (R4 shell 9.3 mm).")
kit.claim("CL-C4-SIM-BOARD-SHARE", "Share of the foot side-load moment carried by the bare board below the shoe legs",
          calc="CALC-C4-SIM-FACE", output="board_share_3d", unit="-", parts=["FIN-001-UR"],
          how="T-C4-FIN-PROOF: gauges 5 mm below the leg edge and on both strips; R4 shell carries all of it in the board.")
kit.claim("CL-C4-SIM-FACE-GCI", "Fine-mesh GCI of the face hot-spot, shoe as drawn", calc="CALC-C4-SIM-FACE",
          output="hs_drawn_gci", unit="-", how="Re-run sim_fin.py (three tip meshes, Roache Fs 1.25).")
kit.claim("CL-C4-SIM-F1-GCI-UP", "Fine-mesh GCI of the first upper station mode", calc="CALC-C4-SIM-MODES",
          output="f1_up_gci", unit="-", limit=("<=", 0.05), how="Re-run sim_fin.py (three meshes, Roache Fs 1.25).")
kit.claim("CL-C4-SIM-F1-GCI-LO", "Fine-mesh GCI of the first lower station mode", calc="CALC-C4-SIM-MODES",
          output="f1_lo_gci", unit="-", limit=("<=", 0.05), how="Re-run sim_fin.py (three meshes, Roache Fs 1.25).")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    kit.write()
    vals = {}
    for cid in ("CALC-C4-SIM-BENCH", "CALC-C4-SIM-CODES", "CALC-C4-SIM-FACE", "CALC-C4-SIM-MODES"):
        vals[cid] = kit._run(cid)
    kw = {a: kit.value(r) for a, r in kit.nodes["CALC-C4-SIM-FACE"]["inputs"].items()}
    g_, k_ = _split(kw)
    fields, det = {}, {}
    for var in ("drawn", "proposed"):
        fields[var] = su2_quarter(g_, k_, "upper", 2, var)["field"]
        det[var] = {}
        for lv in (1, 2, 3):
            r_ = su2_quarter(g_, k_, "upper", lv, var)
            det[var][str(lv)] = {"L4": r_["L4"], "n_dof": r_["n_dof"], "n_hex": r_["n_hex"]}
    vals["detail"] = det
    (OUT / "field_L2.json").write_text(json.dumps(fields, default=float), encoding="utf-8")
    (OUT / "sim_results.json").write_text(json.dumps(vals, indent=1, default=float) + "\n", encoding="utf-8")
    print("wrote claims.sim.json and sim/out/sim_results.json")
