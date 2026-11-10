"""C4 R3: fin / motor-tube structures on D3's as-designed geometry (CR-D3-10), K09-L, params A1-R3.

R3 (2026-11-09): 0.21 m half-fins, two layers, tube 0.344, 7 deg tangential cant (thrust side component on the
mount, collar and tube, prop spin axis tilted in the whirl model), foot side load at the pad friction 0.7
(CR-C5-09), station-collar torsion from the tube torque jump with the LE fillet intact and cracked (CR-C6-03),
edge-strip-to-paper shear flow from the FE (CR-C6-02a), brace 10 x 2 vs 10 x 3 trade (CR-C4-16).

Run:  python -I redesign/team/C4/fin_structures_d3.py      (about 20 s)
Writes claims.d3.json beside this file (proof chain), out/results_d3.json and fig-c4-02-campbell-d3.svg.
Then: python -I redesign/proofs/build_graph.py

What changed against R1 (fin_structures.py, kept for the concept study and for D3's ratio calc):
  * cambered wing: the tube leaves the skin at +19.8 / -7.9 mm (S5010 at x 0.045), so the lower quarter has the
    longer free tube; both quarters are modelled (upper UR, lower LR = mirror in z with the lower skin);
  * clamp at the ends of D3's 47 mm bore (bosses 8 mm proud of the skin, CF plug inside), root rotational spring;
  * tube ends at 0.172 m (CR-D3-01): the printed mount carries the motor 18 mm beyond the tube end; the mount is a
    rotational spring (rocking and twist) between the tube end and the motor/prop/mount rigid body (CAD CG);
  * brace (fin_detail.brace.t_m: 10 x 2 since R3, CR-C4-16) on a station collar at z 0.1535 (ear 17.8 mm inboard of the tube axis) to an anchor on the spar
    at y 0.242, anchor/spar compliance in series;
  * fin = one board, mapped mesh between the curved skin root and the straight top edge (collar top 0.1595 m at the
    LE to the TE tip at the half height), edge strips on the top edge, lower root free over the link slot.
Shell element: fin_fe.shell_q4 (general quad; identical to the R1 rectangle on rectangles, checked below).
"""
import itertools
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

import fin_fe as fe  # noqa: E402
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/fins/params.json"], out="claims.d3.json")
P = "P:"


# ====================================================================== sources and assumptions (new in R2)
def asm(id, title, text, basis, value, unit, status="UNVERIFIED", cites=()):
    kit.assumption(id, title, text, basis, value=value, unit=unit, status=status, cites=cites)


kit.source("SRC-C4-S5010", "Selig S5010 coordinates as used by the wing CAD", "file",
           where="redesign/subsystems/wing/s5010.dat read with redesign/fusion/k09kit.surface_z at chord 0.32 m",
           note="the same file and helper D3's fins.py uses for the boss and root geometry")
asm("ASM-C4-SKIN-PTS", "Wing skin heights along the fin root (S5010, c 0.32 m)",
    "[x, z_upper, z_lower] in metres at the fin plane; the fin roots follow these, the bosses start from them",
    "k09kit.surface_z on subsystems/wing/s5010.dat (SRC-C4-S5010); 14 stations from x 0.0335 to the TE",
    [[0.0335, 0.01775, -0.00731], [0.045, 0.0198, -0.00791], [0.0565, 0.02119, -0.00829], [0.07, 0.0222, -0.00857],
     [0.08, 0.02259, -0.00865], [0.1, 0.02263, -0.00862], [0.13, 0.02111, -0.00815], [0.16, 0.01814, -0.00736],
     [0.19, 0.01422, -0.00636], [0.22, 0.00982, -0.0052], [0.25, 0.00555, -0.00393], [0.28, 0.00214, -0.00265],
     [0.3, 0.00074, -0.00166], [0.32, 0.0003, -0.0003]], "m", status="PROPOSED", cites=["SRC-C4-S5010"])
asm("ASM-C4-BORE-Z", "Block bore ends (boss tops) +30.4 / -16.6 mm",
    "z of the upper and lower ends of D3's 47.0 mm tube bore: highest upper skin (lowest lower skin) under the "
    "keyhole boss footprint plus the 8 mm boss height",
    "subsystems/fins/fusion/fins.py G['boss_u'], G['boss_l'] evaluated with params A1-R2 and fin_detail (C4 re-ran "
    "the same expressions)", [0.03043, -0.01662], "m", status="PROPOSED", cites=["SRC-C4-S5010"])
asm("ASM-C4-MOUNT-CAD", "Motor mount 11.3 g, CG 4.6 mm ahead, 9.7 mm below the motor axis",
    "[mass kg, dx, dy (+ outboard), dz (+ away from the wing)] of FIN-003-UR from the motor station "
    "(0.045, 0.32, 0.19)", "subsystems/fins/interfaces.json FIN-003-UR mass_g 11.28, cg_xyz_m (0.0404, 0.3218, "
    "0.1803) (D3 CAD centroid)", [0.01128, -0.0046, 0.0018, -0.0097], "kg, m", status="PROPOSED")
asm("ASM-C4-COLLAR-BRACE-MASS", "Station collar 5.7 g, brace 7.4 g",
    "[collar kg, brace kg]; collar lumped on the tube at the collar, half the brace at the ear",
    "subsystems/fins/SPEC.md parts table (FIN-008, FIN-009)", [0.0057, 0.0074], "kg", status="PROPOSED")
asm("ASM-C4-MOUNT-K-ROCK", "Mount rocking stiffness 3 000 N m/rad",
    "Rotational stiffness of the printed mount about x and y between the tube end and the motor base",
    "12 mm slit collar on the tube as an elastic foundation: k = (E_PETG / t_wall) d l^3 / 12 = (2 GPa / 2 mm) "
    "x 0.022 x 0.012^3 / 12 = 3 200 N m/rad; the lip cap on the tube end adds to it; range 1 000-10 000. "
    "Static test T-C4-MOUNT-STIFF replaces it", 3000.0, "N m/rad")
asm("ASM-C4-MOUNT-K-TWIST", "Mount twist stiffness 30 000 N m/rad",
    "Rotational stiffness of the clamped collar about the tube axis below the slip torque",
    "collar wall in shear: (G_PETG / t_wall) 2 pi r^3 l = (0.75 GPa / 2 mm) 2 pi 0.011^3 0.012 = 3.8e4 N m/rad", 3.0e4,
    "N m/rad")
asm("ASM-C4-ROOT-K", "Root rotational stiffness 10 000 N m/rad",
    "Tube fixity at the bore end (block + bosses + core), about x and y",
    "R1 foundation estimate 3 000 N m/rad for a 27 mm PETG bore x (47/27)^3 = 5.3 for the 47 mm bore with bosses, "
    "halved because the bosses are 2.4 mm C-rings: ~10 000; swept 3 000-rigid", 1.0e4, "N m/rad")
asm("ASM-C4-ANCHOR-K", "Anchor + spar local stiffness 3e7 N/m along the brace",
    "Series spring of the printed anchor (bond line, 8 mm saddle) and the local spar/core under it",
    "PETG saddle 20 x 16 mm, 8 mm: E A / t = 2 GPa x 3.2e-4 / 0.008 = 8e7 N/m; spar ring and core about the same; "
    "series ~3e7 (the 10 x 3 brace alone is EA/L 2.2e7 N/m)", 3.0e7, "N/m")
asm("ASM-C4-PEEL-KD", "Peel knock-down 0.5 on bond allowables for joints loaded in pull-off",
    "Factor on ASM-C4-BOND-SHEAR for the anchor on the spar and the collar ear", "PETG bonds peel at a fraction of "
    "lap shear; C6 coupons replace it", 0.5, "-")

asm("ASM-C4-D3-MASS-BASIS", "Basis of CL-D3-MASS: two board layers, half height 0.21 m, 10 x 2 braces (D3 R3)",
    "[layers, half height m, brace strip t m] that D3's make_fins.py mass (CL-D3-MASS) was computed with; C4 corrects "
    "the boards and braces from this basis to the params values until D3 re-runs at R3",
    "team/D3/fins_calcs.py CL-D3-MASS 'Fins subsystem flying mass, design R3' (416.8 g, 2026-11-09 15:03): two layers, "
    "0.21 m, 10 x 2 braces, 16 mm collars with 40 mm tails, strip pins; R2 basis was (1, 0.19, 0.003)",
    [2, 0.21, 0.002], "-, m, m", status="UNVERIFIED")
asm("ASM-C4-BRACE-T-3", "Brace strip option 10 x 3 mm", "Thicker pultruded CF strip of the CR-C4-16 trade",
    "stock pultruded strip sizes 10 x 1/2/3 mm", 0.003, "m", status="PROPOSED")
asm("ASM-C4-BRACE-T-2", "Brace strip option 10 x 2 mm", "Thinner pultruded CF strip of the CR-C4-16 trade",
    "stock pultruded strip sizes 10 x 1/2/3 mm", 0.002, "m", status="PROPOSED")

LIMIT_SEP = P + "requirements.vibration_sep_frac"
SF, FIT, PRT = P + "requirements.safety_factor_ult", "ASM-C1-FITTING-FACTOR", "ASM-C1-PRINTED-FACTOR"

# ====================================================================== named inputs
GEOM = {"tube_x": P + "fins.tube.x_m", "y_fin": P + "fins.y_m", "od": P + "fins.tube.od_m", "idd": P + "fins.tube.id_m",
        "mu": P + "wing.spar.mass_per_m_kgm", "tube_len": P + "fin_detail.tube_length_m",
        "z_st": P + "propulsion.stations.z_m", "x_face": "CL-D3-X-FACE", "x_prop": "CL-D3-X-PROP",
        "x_te": P + "fins.te_x_m", "hh": P + "fins.half_height_m", "le_gap": P + "fin_detail.fin.le_gap_m",
        "grip": P + "fin_detail.mount.grip_m", "sc_gap": P + "fin_detail.station_collar.gap_m",
        "sc_h": P + "fin_detail.station_collar.height_m", "sc_wall": P + "fin_detail.station_collar.ring_wall_m",
        "ear_len": P + "fin_detail.station_collar.ear_len_m", "bond_gap": P + "fin_detail.bond_gap_m",
        "skin": "ASM-C4-SKIN-PTS", "bore_z": "ASM-C4-BORE-Z",
        "m_motor": P + "propulsion.motor_mass_kg", "d_motor": P + "propulsion.motor_diameter_m",
        "l_motor": P + "propulsion.motor_length_m", "m_prop": P + "propulsion.prop_mass_kg",
        "m_adapt": "ASM-C1-ADAPTER-MASS", "ip": "ASM-C4-PROP-IP", "i_bell": "ASM-C1-BELL-INERTIA",
        "mount": "ASM-C4-MOUNT-CAD", "cb_mass": "ASM-C4-COLLAR-BRACE-MASS", "m_esc": P + "propulsion.esc_mass_kg",
        "esc_x0": P + "fin_detail.esc_pad.x0_m", "esc_len": P + "fin_detail.esc_pad.len_m",
        "esc_z": P + "fin_detail.esc_pad.z_m", "landing_g": P + "mass.allocation_g.landing",
        "cant": P + "propulsion.stations.cant_deg",
        "t_board": P + "fins.board_t_m", "areal": P + "fins.areal_mass_kgm2", "layers": P + "fin_detail.layers",
        "t_face": "ASM-C4-FACE-T", "e_face": "ASM-C4-FACE-E", "e_core": "ASM-C4-CORE-E", "g_core": "ASM-C4-CORE-G",
        "x_spar": P + "wing.spar.x_m", "y_anchor": P + "fin_detail.brace.anchor_y_m",
        "proud": P + "fin_detail.anchor.proud_m", "b_w": P + "fin_detail.brace.w_m", "b_t": P + "fin_detail.brace.t_m",
        "e_strip": "ASM-C4-CF-E-STRIP", "e_w": P + "fin_detail.edge_strip.w_m", "e_t": P + "fin_detail.edge_strip.t_m",
        "rho_cf": "ASM-C4-CF-RHO", "chord": P + "wing.chord_m", "el_frac": P + "wing.elevon.chord_frac",
        "slot_hw": P + "fin_detail.link_slot.half_width_m", "k_rock": "ASM-C4-MOUNT-K-ROCK",
        "k_twist": "ASM-C4-MOUNT-K-TWIST", "k_root": "ASM-C4-ROOT-K", "k_anchor": "ASM-C4-ANCHOR-K"}
GU = {"tube_x": "m", "y_fin": "m", "od": "m", "idd": "m", "mu": "kg/m", "tube_len": "m", "z_st": "m", "x_face": "m",
      "x_prop": "m", "x_te": "m", "hh": "m", "le_gap": "m", "grip": "m", "sc_gap": "m", "sc_h": "m", "sc_wall": "m",
      "ear_len": "m", "bond_gap": "m", "skin": "m", "bore_z": "m", "m_motor": "kg", "d_motor": "m", "l_motor": "m",
      "m_prop": "kg", "m_adapt": "kg", "ip": "kg m2", "i_bell": "kg m2", "mount": "kg, m", "cb_mass": "kg",
      "m_esc": "kg", "esc_x0": "m", "esc_len": "m", "esc_z": "m", "landing_g": "g", "cant": "deg", "t_board": "m", "areal": "kg/m2",
      "layers": "-", "t_face": "m", "e_face": "Pa", "e_core": "Pa", "g_core": "Pa", "x_spar": "m", "y_anchor": "m",
      "proud": "m", "b_w": "m", "b_t": "m", "e_strip": "Pa", "e_w": "m", "e_t": "m", "rho_cf": "kg/m3", "chord": "m",
      "el_frac": "-", "slot_hw": "m", "k_rock": "N m/rad", "k_twist": "N m/rad", "k_root": "N m/rad",
      "k_anchor": "N/m"}
RPM = {"rpm_h": "CL-B4-HOVER-RPM", "rpm_c": "CL-B4-CRUISE-RPM", "rpm_x": "CL-B4-RPM-MAX"}
RU = {k: "rpm" for k in RPM}
TUBE = {"E": "ASM-J1-E-TUBE", "G": "ASM-C4-G-TUBE"}
TU = {"E": "Pa", "G": "Pa"}
MESH = (24, 20)
REC, REC_U = {"lay_rec": P + "fins.layers"}, {"lay_rec": "-"}
SIDES = ("upper", "lower")
ST_PART = 0.10


def geometry(g, side):
    """Derived points of one quarter in the local frame (y + outboard, z + away from the wing)."""
    sk = np.array(g["skin"], float)
    zs = sk[:, 1] if side == "upper" else -sk[:, 2]
    z_clamp = g["bore_z"][0] if side == "upper" else -g["bore_z"][1]
    z_end = g["tube_len"] / 2
    z_sc = z_end - g["grip"] - g["sc_gap"] - g["sc_h"] / 2                       # station-collar mid height
    z_top_le = z_end - g["grip"] - g["sc_gap"]                                   # collar top = fin LE top
    ear_dy = -(g["od"] / 2 + g["bond_gap"] + g["sc_wall"] + g["ear_len"] / 2)
    z_anchor = float(np.interp(g["x_spar"], sk[:, 0], zs)) + g["proud"] / 2
    anchor = (g["x_spar"], -(g["y_fin"] - g["y_anchor"]), z_anchor)
    x_le = g["tube_x"] + g["od"] / 2 + g["le_gap"]
    x_hinge = g["chord"] * (1 - g["el_frac"])
    return {"root": [(float(x), float(z)) for x, z in zip(sk[:, 0], zs)], "z_clamp": z_clamp, "z_end": z_end,
            "z_sc": z_sc, "z_top_le": z_top_le, "ear": (0.0, ear_dy, 0.0), "anchor": anchor, "x_le": x_le,
            "root_free": [(x_hinge - g["slot_hw"], x_hinge + g["slot_hw"])] if side == "lower" else []}


def model_cfg(g, E, G, side, mesh=MESH, brace=True, edge=True, k_rock="nom", k_root="nom", hh=None, layers=None,
              le_cracked=False):
    geo = geometry(g, side)
    A = math.pi / 4 * (g["od"] ** 2 - g["idd"] ** 2)
    dz_st = g["z_st"] - geo["z_end"]                                             # motor axis above the tube end
    x_motor = g["x_face"] - g["l_motor"] / 2
    rm = g["d_motor"] / 2
    jm_ax = g["m_motor"] * rm * rm / 2
    jm_tr = g["m_motor"] * (3 * rm * rm + g["l_motor"] ** 2) / 12
    ip = g["ip"]
    mm, mdx, mdy, mdz = g["mount"]
    parts = [(g["m_motor"], (x_motor - g["tube_x"], 0, dz_st), (jm_ax, jm_tr, jm_tr)),
             (g["m_prop"] + g["m_adapt"], (g["x_prop"] - g["tube_x"], 0, dz_st), (ip, ip / 2, ip / 2)),
             (mm, (mdx, mdy, dz_st + mdz), (1e-6, 1e-6, 1e-6))]
    lay = g["layers"] if layers is None else layers
    pr = fe.board_props(int(lay), g["t_board"], g["t_face"], g["e_face"], 0.3, g["e_core"], g["g_core"], g["areal"]) \
        if lay > 0 else None
    m_col, m_br = g["cb_mass"]
    kr = g["k_rock"] if k_rock == "nom" else k_rock
    cfg = {"tube": {"x": g["tube_x"], "E": E, "G": G, "od": g["od"], "id": g["idd"], "rho": g["mu"] / A,
                    "z_clamp": geo["z_clamp"], "z_end": geo["z_end"]},
           "n_free": 2, "n_ext": 2, "k_root": g["k_root"] if k_root == "nom" else k_root,
           "fin": {"props": pr, "x_le": geo["x_le"], "x_te": g["x_te"], "root": geo["root"],
                   "z_top_le": geo["z_top_le"], "z_top_te": g["hh"] if hh is None else hh,
                   "root_free": geo["root_free"],
                   "le_bonds": [(geo["z_top_le"] - g["sc_h"], geo["z_top_le"])] if le_cracked else None},
           "nx": mesh[0], "nz": mesh[1],
           "station": {"parts": parts, "k_rock": kr, "k_twist": None if kr is None else g["k_twist"]},
           "tube_masses": [(m_col + (m_br / 2 if brace else 0.0), geo["z_sc"])],
           "fin_masses": [(g["m_esc"], (g["esc_x0"] + g["esc_len"] / 2, g["esc_z"])),
                          (g["landing_g"] / 4 / 1000.0, (g["x_te"], g["hh"] if hh is None else hh))],
           "struts": [], "stiffeners": []}
    if brace:
        cfg["struts"] = [{"z_attach": geo["z_sc"], "ear": geo["ear"], "anchor": geo["anchor"],
                          "EA": g["e_strip"] * g["b_w"] * g["b_t"], "k_anchor": g["k_anchor"]}]
    if edge and pr is not None:
        d = lay * g["t_board"] + g["e_t"]
        cfg["stiffeners"] = [{"E": g["e_strip"], "G": 5e9, "A": 2 * g["e_w"] * g["e_t"],
                              "I_out": g["e_w"] * g["e_t"] * d * d / 2, "J": 2 * g["e_w"] * g["e_t"] ** 3 / 3,
                              "rho": g["rho_cf"], "d": d}]
    return cfg


def forcing(rpm_h, rpm_c, rpm_x):
    return {"1P hover": rpm_h / 60, "2P hover": rpm_h / 30, "1P cruise": rpm_c / 60, "2P cruise": rpm_c / 30,
            "1P max": rpm_x / 60}


def sep_band(f, lo, hi):
    if f < lo:
        return 1 - f / lo
    if f > hi:
        return f / hi - 1
    return -min(f / lo - 1, 1 - f / hi)


def station_modes(mdl, n=16):
    f, Phi, _ = fe.modes(mdl, n)
    cl = fe.classify(mdl, Phi)
    st = [(float(x), c["kind"]) for x, c in zip(f, cl) if c["ke_station"] >= ST_PART]
    pn = [float(x) for x, c in zip(f, cl) if c["ke_station"] < ST_PART]
    dom = [float(x) for x, c in zip(f, cl) if c["ke_station"] >= 0.5]
    return {"f_st": [x for x, _ in st], "kinds": [k for _, k in st], "f_st1": st[0][0], "f_st2": st[1][0] if len(st) > 1
            else st[0][0], "f_panel": pn[0] if pn else float(f[-1]), "f_dom": dom,
            "all": [(float(x), c["kind"], round(c["ke_station"], 3)) for x, c in zip(f, cl)]}


def summary(g, E, G, side, rpm, lo=80.0, hi=330.0, **kw):
    r = station_modes(fe.build_q(model_cfg(g, E, G, side, **kw)))
    pts = forcing(*rpm)
    best = (9.0, "")
    for f in r["f_st"]:
        for k, v in pts.items():
            s = abs(f / v - 1)
            if s < best[0]:
                best = (s, f"{k} vs {f:.0f} Hz")
    r.update({"sep_op": best[0], "nearest": best[1], "sep_band": min(sep_band(f, lo, hi) for f in r["f_st"])})
    return r


# ====================================================================== calculations
@kit.calc("CALC-C4-D3-Q4-CHECK", title="General quad shell element checks",
          inputs={"t_board": P + "fins.board_t_m", "areal": P + "fins.areal_mass_kgm2", "t_face": "ASM-C4-FACE-T",
                  "e_face": "ASM-C4-FACE-E", "e_core": "ASM-C4-CORE-E"},
          units={"t_board": "m", "areal": "kg/m2", "t_face": "m", "e_face": "Pa", "e_core": "Pa"},
          equation="(a) shell_q4 = shell_element on a 20 x 30 mm rectangle (max relative entry difference); "
                   "(b) cantilever 0.2 x 0.2 m plate on a 16 x 16 mesh with interior nodes skewed by up to 20 % of an "
                   "element, f1 vs Leissa lambda^2 = 3.492 (stiff core)", cites=["SRC-C4-LEISSA"], tol=1e-4)
def q4_check(t_board, areal, t_face, e_face, e_core):
    pr = fe.board_props(1, t_board, t_face, e_face, 0.3, e_core, 4e6, areal)
    k1, m1 = fe.shell_element(0.02, 0.03, pr)
    k2, m2 = fe.shell_q4([[0, 0], [0.02, 0], [0.02, 0.03], [0, 0.03]], pr)
    err_rect = float(np.abs(k1 - k2).max() / np.abs(k1).max())
    pr = fe.board_props(1, t_board, t_face, e_face, 0.3, e_core, 1e9, areal)
    a, n = 0.2, 16
    h = a / n
    xy = {}
    for j in range(n + 1):
        for i in range(n + 1):
            x, z = i * h, j * h
            if 0 < i < n and 0 < j < n:
                x += 0.2 * h * math.sin(2.1 * i + 1.3 * j)
                z += 0.2 * h * math.cos(1.7 * i + 0.9 * j)
            xy[(i, j)] = (x, z)
    idx = {k: q for q, k in enumerate(sorted(xy))}
    N = 6 * len(idx)
    K, M = np.zeros((N, N)), np.zeros((N, N))
    for j in range(n):
        for i in range(n):
            ns = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            ke, me = fe.shell_q4([xy[q] for q in ns], pr)
            d = [6 * idx[q] + r for q in ns for r in range(6)]
            K[np.ix_(d, d)] += ke
            M[np.ix_(d, d)] += me
    keep = [6 * idx[q] + r for q in idx for r in range(6) if q[1] > 0 and r != 4]
    import scipy.linalg as sla
    w2 = sla.eigh(K[np.ix_(keep, keep)], M[np.ix_(keep, keep)], eigvals_only=True, subset_by_index=[0, 0])
    f_fe = float(np.sqrt(w2[0]) / (2 * math.pi))
    f_l = 3.492 / (2 * math.pi * a * a) * math.sqrt(pr["D"] / pr["rho_h"])
    return {"err_rect": err_rect, "f_skew_fe": f_fe, "f_leissa": f_l, "err_skew": abs(f_fe / f_l - 1)}


def _ins(extra=None, extra_u=None):
    return {**GEOM, **RPM, **TUBE, **(extra or {})}, {**GU, **RU, **TU, **(extra_u or {})}


INS, UNS = _ins({"lo": "ASM-C4-BAND-LO", "hi": "ASM-C4-BAND-HI"}, {"lo": "Hz", "hi": "Hz"})


@kit.calc("CALC-C4-D3-MODES", title="Station modes, one board layer (rejected option CR-D3-02) on the R3 geometry, upper "
          "UR and lower LR, nominal E/G",
          inputs={**INS, "lay_1l": "ASM-C4-ONE-LAYER"}, units={**UNS, "lay_1l": "-"}, tol=1e-4,
          equation="FE (fin_fe.build_q): tube frame + 1-layer board (mapped Q4 shell) + edge strips + brace (EA/L in "
                   "series with the anchor) + mount springs + motor/prop/mount rigid body; station mode = >= 10 % of "
                   "kinetic energy in the rigid body; sep = min |f/f_k - 1| over 1P/2P hover, 1P/2P cruise, 1P cap",
          assumes=["ASM-C4-MOUNT-K-ROCK", "ASM-C4-ROOT-K", "ASM-C4-ANCHOR-K", "ASM-C4-PROP-IP", "ASM-C4-FACE-E"],
          cites=["SRC-C4-ALLEN"])
def modes_d3(**k):
    g = {n: k[n] for n in GEOM}
    rpm = (k["rpm_h"], k["rpm_c"], k["rpm_x"])
    out = {}
    for side in SIDES:
        r = summary(g, k["E"], k["G"], side, rpm, k["lo"], k["hi"], layers=k["lay_1l"])
        s = side[:2]
        out.update({f"f1_{s}": r["f_st1"], f"f2_{s}": r["f_st2"], f"panel_{s}": r["f_panel"], f"sep_{s}": r["sep_op"],
                    f"band_{s}": r["sep_band"]})
    out["f1_min"] = min(out["f1_up"], out["f1_lo"])
    out["sep_op"] = min(out["sep_up"], out["sep_lo"])
    out["sep_band"] = min(out["band_up"], out["band_lo"])
    return out


INS2, UNS2 = {**INS, **REC}, {**UNS, **REC_U}


@kit.calc("CALC-C4-D3-MODES-REC", title="Station modes, recommended: D3 geometry with fins.layers boards (params), "
          "brace and edge strips, nominal E/G", inputs=INS2, units=UNS2, tol=1e-4,
          equation="as CALC-C4-D3-MODES with the board layers from params.json (fins.layers)",
          assumes=["ASM-C4-MOUNT-K-ROCK", "ASM-C4-ROOT-K", "ASM-C4-ANCHOR-K", "ASM-C4-PROP-IP", "ASM-C4-FACE-E"],
          cites=["SRC-C4-ALLEN"])
def modes_rec(**k):
    g = {n: k[n] for n in GEOM}
    rpm = (k["rpm_h"], k["rpm_c"], k["rpm_x"])
    out = {}
    for side in SIDES:
        r = summary(g, k["E"], k["G"], side, rpm, k["lo"], k["hi"], layers=k["lay_rec"])
        s = side[:2]
        out.update({f"f1_{s}": r["f_st1"], f"f2_{s}": r["f_st2"], f"panel_{s}": r["f_panel"], f"sep_{s}": r["sep_op"],
                    f"band_{s}": r["sep_band"]})
    out["f1_min"] = min(out["f1_up"], out["f1_lo"])
    out["sep_op"] = min(out["sep_up"], out["sep_lo"])
    out["sep_band"] = min(out["band_up"], out["band_lo"])
    return out


@kit.calc("CALC-C4-D3-WORST", title="Separation over the tube E/G corners, recommended design",
          inputs={**GEOM, **RPM, **REC, "E0": "ASM-J1-E-TUBE", "E_lo": "ASM-C4-E-TUBE-LO", "E_hi": "ASM-C4-E-TUBE-HI",
                  "G0": "ASM-C4-G-TUBE", "G_lo": "ASM-C4-G-TUBE-LO", "G_hi": "ASM-C4-G-TUBE-HI"},
          units={**GU, **RU, **REC_U, "E0": "Pa", "E_lo": "Pa", "E_hi": "Pa", "G0": "Pa", "G_lo": "Pa", "G_hi": "Pa"},
          tol=1e-4,
          equation="min over side x E {lo, nom, hi} x G {lo, nom, hi} of sep_op (18 FE runs), mount and root at "
                   "their nominal springs",
          assumes=["ASM-C4-E-TUBE-LO", "ASM-C4-E-TUBE-HI", "ASM-C4-G-TUBE-LO", "ASM-C4-G-TUBE-HI"])
def worst_d3(**k):
    g = {n: k[n] for n in GEOM}
    rpm = (k["rpm_h"], k["rpm_c"], k["rpm_x"])
    worst, f_min, at = 9.0, 1e9, ""
    for side, E, G in itertools.product(SIDES, (k["E_lo"], k["E0"], k["E_hi"]), (k["G_lo"], k["G0"], k["G_hi"])):
        r = summary(g, E, G, side, rpm, layers=k["lay_rec"])
        f_min = min(f_min, r["f_st1"])
        worst = min(worst, r["sep_op"])
    return {"sep_op_worst": worst, "f_station_min": f_min}


K_SWEEP = (500.0, 1000.0, 1500.0, 2000.0, 3000.0, 5000.0, 10000.0, 30000.0)


@kit.calc("CALC-C4-D3-MOUNT-K", title="Mount rocking stiffness needed for the separation rule, recommended design",
          inputs={**GEOM, **RPM, **TUBE, **REC, "sep_min": LIMIT_SEP, "E_lo": "ASM-C4-E-TUBE-LO",
                  "G_lo": "ASM-C4-G-TUBE-LO"},
          units={**GU, **RU, **TU, **REC_U, "sep_min": "-", "E_lo": "Pa", "G_lo": "Pa"}, tol=1e-3,
          equation="sweep k_rock over 500-30 000 N m/rad (k_twist fixed) on both quarters at nominal and low E/G; "
                   "k_req = smallest k with sep_op >= sep_min at every larger k (log interpolation)")
def mount_k(**k):
    g = {n: k[n] for n in GEOM}
    rpm = (k["rpm_h"], k["rpm_c"], k["rpm_x"])

    def sep_at(kr, E, G):
        return min(summary(g, E, G, s, rpm, k_rock=kr, layers=k["lay_rec"])["sep_op"] for s in SIDES)

    out = {}
    for tag, E, G in (("nom", k["E"], k["G"]), ("lo", k["E_lo"], k["G_lo"])):
        seps = [sep_at(kr, E, G) for kr in K_SWEEP]
        req = K_SWEEP[-1] * 10
        for i in range(len(K_SWEEP) - 1, -1, -1):
            if seps[i] < k["sep_min"]:
                if i == len(K_SWEEP) - 1:
                    break
                a, b = seps[i], seps[i + 1]
                t = (k["sep_min"] - a) / (b - a) if b != a else 0.0
                req = math.exp(math.log(K_SWEEP[i]) + t * (math.log(K_SWEEP[i + 1]) - math.log(K_SWEEP[i])))
                break
        else:
            req = K_SWEEP[0]
        out[f"k_req_{tag}"] = req
        out[f"seps_{tag}"] = seps
    out["k_req"] = max(out["k_req_nom"], out["k_req_lo"])
    return out


@kit.calc("CALC-C4-D3-CONVERGENCE", title="Mesh convergence, recommended design (both sides)",
          inputs={**GEOM, **TUBE, **RPM, **REC}, units={**GU, **TU, **RU, **REC_U}, tol=1e-4,
          equation="first dominant station mode f1 (>= 50 % kinetic energy in the motor body) and sep_op at fin meshes "
                   "12x10, 24x20 (used), 36x30; change = max over sides of |f1(24x20)/f1(36x30) - 1| and "
                   "|sep(24x20)/sep(36x30) - 1| (f2 reported only: near 360-600 Hz it swaps between coupled modes)")
def convergence_d3(**k):
    g = {n: k[n] for n in GEOM}
    rpm = (k["rpm_h"], k["rpm_c"], k["rpm_x"])
    out, ch = {}, 0.0
    for side in SIDES:
        fs = {}
        for tag, mesh in (("coarse", (12, 10)), ("used", MESH), ("fine", (36, 30))):
            r = summary(g, k["E"], k["G"], side, rpm, mesh=mesh, layers=k["lay_rec"])
            fs[tag] = (r["f_dom"][0], r["sep_op"])
            s = side[:2]
            out[f"f1_{s}_{tag}"], out[f"f2_{s}_{tag}"], out[f"sep_{s}_{tag}"] = r["f_dom"][0], r["f_dom"][1], r["sep_op"]
        ch = max([ch] + [abs(a / b - 1) for a, b in zip(fs["used"], fs["fine"])])
    out["change"] = ch
    return out


def spin_axis(g):
    """Prop spin axis in the quarter frame with the tangential cant (thrust along -x, tilted toward the tangent)."""
    ty, tz = tangent(g)
    c = math.radians(g["cant"])
    return (-math.cos(c), math.sin(c) * ty, math.sin(c) * tz)


def tangent(g):
    """Unit tangent of the motor circle at the station, (y, z) in the quarter frame (D3 CR-D3-07 sense)."""
    r = math.hypot(g["y_fin"], g["z_st"])
    return -g["z_st"] / r, g["y_fin"] / r


def station_whirl(mdl, ip_spin, rpm, n_modes=16, axis=(-1.0, 0.0, 0.0)):
    f0, Phi, _ = fe.modes(mdl, n_modes)
    cl = fe.classify(mdl, Phi)
    keep = [i for i, c in enumerate(cl) if c["ke_station"] >= ST_PART]
    w = 2 * math.pi * f0
    Gm = Phi.T @ (fe.gyro_matrix(mdl, ip_spin, axis) @ Phi)
    n = len(w)
    Om = rpm * 2 * math.pi / 60
    A = np.zeros((2 * n, 2 * n))
    A[:n, n:] = np.eye(n)
    A[n:, :n] = -np.diag(w ** 2)
    A[n:, n:] = -Om * Gm
    lam, vec = np.linalg.eig(A)
    out = []
    for j in range(2 * n):
        if lam[j].imag > 1e-6 and int(np.argmax(np.abs(vec[:n, j]))) in keep:
            out.append(float(lam[j].imag / (2 * math.pi)))
    return sorted(out)


@kit.calc("CALC-C4-D3-CAMPBELL", title="Gyroscopic whirl separation, recommended design (both sides)",
          inputs={**GEOM, **RPM, **TUBE, **REC}, units={**GU, **RU, **TU, **REC_U}, tol=1e-4,
          equation="M q'' + Omega G q' + K q = 0 on 16 modes, G = -[Ip_spin e_shaft]x at the station, e_shaft = (-cos c, "
                   "sin c t_y, sin c t_z) with the tangential cant c; sep over 1P/2P "
                   "at hover and cruise and 1P at the cap, station whirl modes only",
          assumes=["ASM-C4-PROP-IP", "ASM-C1-BELL-INERTIA"])
def campbell_d3(**k):
    g = {n: k[n] for n in GEOM}
    worst = 9.0
    for side in SIDES:
        mdl = fe.build_q(model_cfg(g, k["E"], k["G"], side, layers=k["lay_rec"]))
        for name, rpm in (("hover", k["rpm_h"]), ("cruise", k["rpm_c"]), ("max", k["rpm_x"])):
            for f in station_whirl(mdl, g["ip"] + g["i_bell"], rpm, axis=spin_axis(g)):
                for p in ((1,) if name == "max" else (1, 2)):
                    worst = min(worst, abs(f / (p * rpm / 60) - 1))
    return {"sep_whirl": worst}


STAT_IN = {"f_level": "CL-C1-FOOT-LEVEL", "f_corner": "CL-C1-FOOT-CORNER", "mu_hi": "ASM-D5-PAD-MU",
           "side_c5": "CL-C5-FOOT-SIDE-LOAD",
           "n_h": "ASM-C1-HANDLING-N", "m_gate": P + "requirements.mtow_gate_kg", "grav": P + "env.g_ms2",
           "t_lim": "CL-C1-T-LIMIT", "q_mot": "CL-C1-MOTOR-TORQUE", "sf": SF, "fit": FIT, "prt": PRT,
           "s_face": "ASM-C4-FACE-SIGMA", "s_cf": "ASM-C4-CF-SIGMA", "patch": "ASM-C4-FOOT-PATCH",
           "s_bond": "ASM-C4-BOND-SHEAR", "peel": "ASM-C4-PEEL-KD", "engage": P + "fin_detail.brace.engage_m",
           "a_lx": P + "fin_detail.anchor.len_x_m", "a_ly": P + "fin_detail.anchor.len_y_m",
           "d_spar": P + "wing.spar.od_m", "ear_w": P + "fin_detail.station_collar.ear_w_m",
           "s_ten": "ASM-C4-PETG-TENSILE", "kd_foam": "ASM-C6-FOAM-KD", "tau_board": "ASM-D5-BOND-TAU",
           "pin_pitch": P + "fin_detail.edge_strip.pin_pitch_m"}
STAT_U = {"f_level": "N", "f_corner": "N", "mu_hi": "-", "side_c5": "N", "n_h": "-", "m_gate": "kg", "grav": "m/s2",
          "t_lim": "N", "q_mot": "N m", "sf": "-", "fit": "-", "prt": "-", "s_face": "Pa", "s_cf": "Pa", "patch": "m",
          "s_bond": "Pa", "peel": "-", "engage": "m", "a_lx": "m", "a_ly": "m", "d_spar": "m", "ear_w": "m",
          "s_ten": "Pa", "kd_foam": "-", "tau_board": "Pa", "pin_pitch": "m"}


def tube_torques(mdl, u, E, G):
    """Internal torque (global Mz) in each tube element, bottom to top."""
    nodes, out = mdl.nodes, []
    for e in range(mdl.n_tube - 1):
        ke, _ = fe.frame_element(nodes[e], nodes[e + 1], E, G, mdl.A_t, mdl.I_t, mdl.I_t, mdl.J_t, 1.0)
        out.append(float((ke @ np.concatenate([u[6 * e:6 * e + 6], u[6 * e + 6:6 * e + 12]]))[11]))
    return out


def fin_static(g, k, side, le_cracked=False):
    """One quarter, every limit case. Returns per-case results and the brace length."""
    mdl = fe.build_q(model_cfg(g, k["E"], k["G"], side, layers=k["lay_rec"], le_cracked=le_cracked))
    pr = mdl.cfg["fin"]["props"]
    nodes = mdl.nodes
    geo = geometry(g, side)
    corner = np.array([g["x_te"], 0.0, g["hh"]])
    foot = [n for n in mdl.fin_id.values() if np.linalg.norm(nodes[n] - corner) <= k["patch"] + 1e-9]
    nf, fc = len(foot), k["f_corner"]
    fs = max(k["mu_hi"] * fc, k["side_c5"])                                     # foot side load at the pad friction
    G2 = k["n_h"] * k["m_gate"] * k["grav"]
    T, Q, c = k["t_lim"], k["q_mot"], math.radians(g["cant"])
    ty, tz = tangent(g)
    r = np.array([g["x_prop"] - g["tube_x"], 0.0, g["z_st"] - geo["z_end"]])    # prop centre from the station node
    cases = {"L1": [(n, (-k["f_level"] / nf, 0, 0, 0, 0, 0)) for n in foot],
             "L4+": [(n, (-fc / nf, fs / nf, 0, 0, 0, 0)) for n in foot],
             "L4-": [(n, (-fc / nf, -fs / nf, 0, 0, 0, 0)) for n in foot],
             "L5": [(n, (-fc / nf, 0, -fs / nf, 0, 0, 0)) for n in foot],
             "G2+": [(mdl.i_end, (0, G2, 0, 0, 0, 0))],
             "G2-": [(mdl.i_end, (0, -G2, 0, 0, 0, 0))]}
    for s_c, s_q in itertools.product((1, -1), (1, -1)):                        # H2 with the 7 deg cant, both prints
        F = np.array([-T * math.cos(c), s_c * T * math.sin(c) * ty, s_c * T * math.sin(c) * tz])
        M = np.cross(r, F) + s_q * Q * F / np.linalg.norm(F)
        cases[f"H2c{'+' if s_c > 0 else '-'}{'+' if s_q > 0 else '-'}"] = [(mdl.i_station, (*F, *M))]
    nu = pr["nu"]
    Qf = g["e_face"] / (1 - nu * nu) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    C3 = np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    s = mdl.strut_info[0]
    zt = [float(nodes[i][2]) for i in range(mdl.n_tube)]
    z_bot, z_top = geo["z_top_le"] - g["sc_h"], geo["z_top_le"]
    e_lo = min(i for i, z in enumerate(zt) if z >= z_bot - 1e-4) - 1                # element just below the collar
    e_hi = max(i for i, z in enumerate(zt) if z <= z_top + 1e-4)                   # element just above the collar
    top_row = [mdl.fin_id[(i, mdl.cfg["nz"])] for i in range(mdl.cfg["nx"] + 1)]
    res = {}
    for cname, loads in cases.items():
        u = fe.static(mdl, loads)
        smax = 0.0
        for ns, xz, pe in mdl.shells:
            ue = np.concatenate([u[6 * n:6 * n + 6] for n in ns])
            Nv, Mv = fe.shell_q4_resultants(xz, pe, ue)
            e0, kap = np.linalg.solve(pe["A"] * C3, Nv), np.linalg.solve(pe["D"] * C3, Mv)
            for z in (pe["z_face_out"], -pe["z_face_out"]):
                sx, sz, txz = Qf @ (e0 + z * kap)
                smax = max(smax, abs((sx + sz) / 2) + math.hypot((sx - sz) / 2, txz))
        ke, _ = fe.frame_element(nodes[0], nodes[1], k["E"], k["G"], mdl.A_t, mdl.I_t, mdl.I_t, mdl.J_t, 1.0)
        fn = ke @ np.concatenate([u[0:6], u[6:12]])
        m_root = math.hypot(fn[3], fn[4])
        f_br = -s["k"] * float(np.dot(s["n"], u[6 * s["node"]:6 * s["node"] + 3]))      # + = compression
        tt = tube_torques(mdl, u, k["E"], k["G"])
        t_collar = abs(tt[e_lo] - tt[e_hi])                                         # torque the collar band puts in
        # edge strips: axial N, out-of-plane shear V and moment M per element (both faces together)
        s_edge, Ns, Vs, Ls, M0, d = 0.0, [], [], [], 0.0, None
        for n1, n2, stf in mdl.stf_elems:
            ke, _ = fe.frame_element(nodes[n1], nodes[n2], stf["E"], stf["G"], stf["A"], 1e-15, stf["I_out"], stf["J"],
                                     1.0)
            fe_ = ke @ np.concatenate([u[6 * n1:6 * n1 + 6], u[6 * n2:6 * n2 + 6]])
            s_edge = max(s_edge, max(abs(fe_[5]), abs(fe_[11])) * stf["d"] / 2 / stf["I_out"] + abs(fe_[0]) / stf["A"])
            e1 = (nodes[n2] - nodes[n1]) / np.linalg.norm(nodes[n2] - nodes[n1])
            Ns.append(float(np.dot(fe_[6:9], e1)))
            Vs.append(abs(float(fe_[7])))
            Ls.append(float(np.linalg.norm(nodes[n2] - nodes[n1])))
            if n1 == top_row[0]:
                M0, d = abs(float(fe_[5])), stf["d"]
        q_face = 0.0                                                                # per face, paper interface, N/m
        for i in range(1, len(Ns)):
            if top_row[i] in foot:
                continue                                                            # foot shoe wraps the strip ends
            q = abs(Ns[i] - Ns[i - 1]) / 2 / ((Ls[i] + Ls[i - 1]) / 2) + max(Vs[i], Vs[i - 1]) / d
            q_face = max(q_face, q)
        res[cname] = {"face": smax, "edge": s_edge, "tube": m_root * g["od"] / 2 / mdl.I_t, "mroot": m_root,
                      "brace": f_br, "t_collar": t_collar, "t_root": abs(tt[0]), "q_face": q_face,
                      "strip_end": abs(Ns[0]) / 2 + M0 / d,
                      "dfoot": max(float(np.linalg.norm(u[6 * n:6 * n + 3])) for n in foot)}
    return res, s["L"]


@kit.calc("CALC-C4-D3-STATIC", title="Fin, tube, brace, collar, edge-strip bond and anchor strength, recommended "
          "design (both sides, LE fillet intact and cracked)",
          inputs={**GEOM, **TUBE, **STAT_IN, **REC}, units={**GU, **TU, **STAT_U, **REC_U}, tol=1e-4,
          equation="FE static, limit cases L1, L4 (side = max(mu_pad F_corner, C5 side load), both senses), L5, G2 (both "
                   "senses, n_h m g at the tube end), H2c (T_lim along the 7 deg canted shaft at the prop centre + Q "
                   "about the shaft, 4 sign combinations); envelope over upper/lower quarter and LE fillet intact / "
                   "cracked between the boss and the collar; ultimate = sf x limit (joints x fit x prt); face = Q_f "
                   "(eps0 + z kappa); collar torque = jump of the tube torque across the collar band; strip-to-paper "
                   "shear flow per face q = |dN|/2/ds + |V|/d (foot-shoe nodes excluded), tau = q/w vs kd tau_board; "
                   "strip end force per face = |N0|/2 + |M0|/d; pin force = q jf pitch; brace Pcr = pi^2 E w t^3 / (12 L^2); brace-end bond "
                   "tau = F / (2 (w + t) engage); ear root s = 6 F (ear/2) / (w_ear h^2) + F / (w_ear h); collar bond "
                   "tau = T / (2 pi r^2 h) + F / (pi d h), h_req at MS 0; anchor tau = F / (len_y pi d_spar / 4) vs "
                   "peel x bond allowable",
          assumes=["ASM-C4-FACE-SIGMA", "ASM-C4-BOND-SHEAR", "ASM-C4-PEEL-KD", "ASM-C4-FOOT-PATCH"],
          cites=["SRC-C4-ALLEN", "SRC-C4-ROARK"])
def static_d3(**k):
    g = {n: k[n] for n in GEOM}
    jf = k["sf"] * k["fit"] * k["prt"]
    out = {}
    agg = {"face": 0.0, "edge": 0.0, "tube": 0.0, "comp": 0.0, "tens": 0.0, "t_collar": 0.0, "f_collar": 0.0,
           "dfoot_L4": 0.0, "mroot": 0.0, "t_root": 0.0, "q_face": 0.0, "strip_end": 0.0, "t_collar_intact": 0.0,
           "q_face_intact": 0.0, "face_intact": 0.0}
    for side, cr in itertools.product(SIDES, (False, True)):
        res, L = fin_static(g, k, side, le_cracked=cr)
        tag = side[:2] + ("_cr" if cr else "")
        out[f"brace_len_{side[:2]}_m"] = L
        for c, r in res.items():
            for key in ("face", "edge", "tube", "mroot", "t_collar", "t_root", "q_face", "strip_end"):
                agg[key] = max(agg[key], r[key])
            if not cr:
                agg["t_collar_intact"] = max(agg["t_collar_intact"], r["t_collar"])
                agg["q_face_intact"] = max(agg["q_face_intact"], r["q_face"])
                agg["face_intact"] = max(agg["face_intact"], r["face"])
            agg["comp"] = max(agg["comp"], r["brace"])
            agg["tens"] = max(agg["tens"], -r["brace"])
            agg["f_collar"] = max(agg["f_collar"], abs(r["brace"]))
            if c.startswith("L4"):
                agg["dfoot_L4"] = max(agg["dfoot_L4"], r["dfoot"])
            out[f"face_{tag}_{c}_mpa"] = r["face"] * k["sf"] / 1e6
            out[f"brace_{tag}_{c}_n"] = r["brace"]
            out[f"tcollar_{tag}_{c}_nm"] = r["t_collar"]
            out[f"qface_{tag}_{c}_npm"] = r["q_face"]
    L = max(out["brace_len_up_m"], out["brace_len_lo_m"])
    face_u, edge_u, tube_u = agg["face"] * k["sf"], agg["edge"] * k["sf"], agg["tube"] * k["sf"]
    comp_d, tens_d = agg["comp"] * k["sf"] * k["fit"], agg["tens"] * k["sf"] * k["fit"]
    pcr = math.pi ** 2 * g["e_strip"] * g["b_w"] * g["b_t"] ** 3 / 12 / L ** 2
    f_end = max(agg["comp"], agg["tens"]) * jf
    tau_end = f_end / (2 * (g["b_w"] + g["b_t"]) * k["engage"])
    r_t, h_c = g["od"] / 2, g["sc_h"]
    per_h = agg["t_collar"] * jf / (2 * math.pi * r_t ** 2) + agg["f_collar"] * jf / (math.pi * g["od"])
    tau_collar = per_h / h_c
    tau_anchor = agg["tens"] * jf / (k["a_ly"] * math.pi * k["d_spar"] / 4)
    f_ear = max(agg["comp"], agg["tens"]) * jf                       # brace force on the collar ear, design
    s_ear = 6 * f_ear * g["ear_len"] / 2 / (k["ear_w"] * g["sc_h"] ** 2) + f_ear / (k["ear_w"] * g["sc_h"])
    tau_strip = agg["q_face"] * jf / g["e_w"]
    ms = {"ms_face": k["s_face"] / face_u - 1, "ms_edge": k["s_cf"] / edge_u - 1, "ms_tube": k["s_cf"] / tube_u - 1,
          "ms_brace_buckling": pcr / max(comp_d, 1e-9) - 1, "ms_brace_end_bond": k["s_bond"] / tau_end - 1,
          "ms_collar_bond": k["s_bond"] / tau_collar - 1,
          "ms_anchor_bond": k["s_bond"] * k["peel"] / max(tau_anchor, 1.0) - 1,
          "ms_ear_root": k["s_ten"] / s_ear - 1}
    ms_strip = k["kd_foam"] * k["tau_board"] / tau_strip - 1
    out.update({"face_ult_pa": face_u, "face_ult_intact_pa": agg["face_intact"] * k["sf"], "edge_ult_pa": edge_u,
                "tube_ult_pa": tube_u, "root_m_lim_nm": agg["mroot"],
                "brace_comp_design_n": comp_d, "brace_tens_design_n": tens_d, "brace_pcr_n": pcr,
                "brace_len_m": L, "collar_t_lim_nm": agg["t_collar"], "collar_t_lim_intact_nm": agg["t_collar_intact"],
                "collar_t_design_nm": agg["t_collar"] * jf, "collar_f_lim_n": agg["f_collar"],
                "tau_collar_pa": tau_collar, "collar_h_req_m": per_h / k["s_bond"],
                "tube_t_root_lim_nm": agg["t_root"], "side_load_n": max(k["mu_hi"] * k["f_corner"], k["side_c5"]),
                "strip_q_lim_npm": agg["q_face"], "strip_q_lim_intact_npm": agg["q_face_intact"],
                "strip_tau_design_pa": tau_strip, "ms_strip_paper": ms_strip,
                "strip_end_face_design_n": agg["strip_end"] * jf,
                "strip_pin_design_n": agg["q_face"] * jf * k["pin_pitch"],
                "tau_anchor_pa": tau_anchor, "s_ear_pa": s_ear, "tau_brace_end_pa": tau_end,
                "dfoot_L4_m": agg["dfoot_L4"], **ms, "ms_min": min(ms.values())})
    return out


@kit.calc("CALC-C4-D3-BRACE-TRADE", title="Brace strip 10 x 2 against 10 x 3 (CR-C4-16), recommended design",
          inputs={**GEOM, **TUBE, **RPM, **REC, "t3": "ASM-C4-BRACE-T-3", "t2": "ASM-C4-BRACE-T-2",
                  "n_h": "ASM-C1-HANDLING-N",
                  "m_gate": P + "requirements.mtow_gate_kg", "grav": P + "env.g_ms2", "sf": SF, "fit": FIT},
          units={**GU, **TU, **RU, **REC_U, "t3": "m", "t2": "m", "n_h": "-", "m_gate": "kg", "grav": "m/s2", "sf": "-",
                 "fit": "-"}, tol=1e-4,
          equation="for t in (10 x 3, 10 x 2): sep_op (both quarters, nominal E/G); G2 brace force from the FE (limit, both "
                   "quarters) x sf x fit vs Pcr = pi^2 E w t^3 / (12 L^2); mass of four braces = 4 rho w t L_mean")
def brace_trade(**k):
    g0 = {n: k[n] for n in GEOM}
    rpm = (k["rpm_h"], k["rpm_c"], k["rpm_x"])
    G2 = k["n_h"] * k["m_gate"] * k["grav"]
    out = {}
    for tag, t in (("t3", k["t3"]), ("t2", k["t2"])):
        g = {**g0, "b_t": t}
        sep, fmax, Ls = 9.0, 0.0, []
        for side in SIDES:
            sep = min(sep, summary(g, k["E"], k["G"], side, rpm, layers=k["lay_rec"])["sep_op"])
            mdl = fe.build_q(model_cfg(g, k["E"], k["G"], side, layers=k["lay_rec"]))
            st = mdl.strut_info[0]
            for sgn in (1, -1):
                u = fe.static(mdl, [(mdl.i_end, (0, sgn * G2, 0, 0, 0, 0))])
                fmax = max(fmax, abs(st["k"] * float(np.dot(st["n"], u[6 * st["node"]:6 * st["node"] + 3]))))
            Ls.append(st["L"])
        pcr = math.pi ** 2 * g["e_strip"] * g["b_w"] * t ** 3 / 12 / max(Ls) ** 2
        f_d = fmax * k["sf"] * k["fit"]
        out.update({f"sep_{tag}": sep, f"pcr_{tag}_n": pcr, f"f_design_{tag}_n": f_d, f"ms_buckle_{tag}": pcr / f_d - 1,
                    f"mass4_{tag}_g": 4 * g["rho_cf"] * g["b_w"] * t * sum(Ls) / len(Ls) * 1000})
    out["mass_saving_g"] = out["mass4_t3_g"] - out["mass4_t2_g"]
    out["sep_loss"] = out["sep_t3"] - out["sep_t2"]
    return out


@kit.calc("CALC-C4-D3-MOUNT-CANT", title="Motor mount on the tube end with the 7 deg tangential cant",
          inputs={"T": "CL-C1-T-LIMIT", "Q": "CL-C1-MOTOR-TORQUE", "cant": P + "propulsion.stations.cant_deg",
                  "y_fin": P + "fins.y_m", "z_st": P + "propulsion.stations.z_m", "x_prop": "CL-D3-X-PROP",
                  "tube_x": P + "fins.tube.x_m", "tube_len": P + "fin_detail.tube_length_m", "od": P + "fins.tube.od_m",
                  "slip": P + "fin_detail.mount.slip_torque_nm", "m_c1": "CL-C1-MOUNT-M-ULT",
                  "f_c1": "CL-C1-MOUNT-F-ULT", "sf": SF, "fit": FIT, "prt": PRT},
          units={"T": "N", "Q": "N m", "cant": "deg", "y_fin": "m", "z_st": "m", "x_prop": "m", "tube_x": "m",
                 "tube_len": "m", "od": "m", "slip": "N m", "m_c1": "N m", "f_c1": "N", "sf": "-", "fit": "-",
                 "prt": "-"}, tol=1e-6,
          equation="t = (-z_st, y_fin)/|.| (motor-circle tangent); F = T (-cos c, sin c t_y, sin c t_z) at r = (x_prop - "
                   "x_tube, 0, z_st - L_tube/2) from the tube end; side = T sin c; axial = T sin c |t_z|; twist "
                   "about the tube = |r_x| T sin c |t_y| + Q sin c |t_z|; rocking = |r x F| in x-y (worst sign) + Q cos c; design "
                   "= limit x sf x fit x prt; slip-clamp use = sqrt((F_ax,d / (T_slip / r))^2 + ((M_tw,d + M_C1,ult "
                   "fit prt) / T_slip)^2) (C1's mount moment taken wholly about the tube: conservative)")
def mount_cant(T, Q, cant, y_fin, z_st, x_prop, tube_x, tube_len, od, slip, m_c1, f_c1, sf, fit, prt):
    c = math.radians(cant)
    rr = math.hypot(y_fin, z_st)
    ty, tz = -z_st / rr, y_fin / rr
    rx, rz = x_prop - tube_x, z_st - tube_len / 2
    side, ax, lat = T * math.sin(c), T * math.sin(c) * abs(tz), T * math.sin(c) * abs(ty)
    tw = abs(rx) * lat + Q * math.sin(c) * abs(tz)
    rock = math.hypot(abs(rz) * lat, abs(rz) * T * math.cos(c) + abs(rx) * ax) + Q * math.cos(c)   # worst print sense
    jf = sf * fit * prt
    r = od / 2
    use = math.hypot(ax * jf / (slip / r), (tw * jf + m_c1 * fit * prt) / slip)
    return {"side_frac": math.sin(c), "side_lim_n": side, "axial_lim_n": ax, "lateral_lim_n": lat,
            "twist_lim_nm": tw, "rock_lim_nm": rock, "axial_design_n": ax * jf, "twist_design_nm": tw * jf,
            "rock_design_nm": rock * jf, "shear_design_n": math.hypot(T * math.cos(c), lat) * jf,
            "c1_force_ratio": T * jf / max(f_c1 * fit * prt, 1e-9), "slip_use": use, "ms_slip_hold": 1 / use - 1}


@kit.calc("CALC-C4-D3-BLOCK", title="Through-core block on D3's geometry (bosses not credited for strength)",
          inputs={"m_des_c1": "CL-C1-FINJOINT-M-DESIGN", "m_task": "ASM-C4-FINJOINT-M-TASK",
                  "f_ult": "CL-C1-FINJOINT-F-ULT", "my_lim": "ASM-C4-FINJOINT-MY", "sf": SF, "fit": FIT, "prt": PRT,
                  "d": P + "fins.tube.od_m", "d_spar": P + "wing.spar.od_m", "skin": "ASM-C4-SKIN-PTS",
                  "x_t": P + "fins.tube.x_m", "W": P + "fin_detail.block.width_m", "s_brg": "ASM-C4-PETG-BEARING",
                  "s_ten": "ASM-C4-PETG-TENSILE", "s_sh": "ASM-C4-PETG-SHEAR", "s_bond": "ASM-C4-BOND-SHEAR"},
          units={"m_des_c1": "N m", "m_task": "N m", "f_ult": "N", "my_lim": "N m", "sf": "-", "fit": "-", "prt": "-",
                 "d": "m", "d_spar": "m", "skin": "m", "x_t": "m", "W": "m", "s_brg": "Pa", "s_ten": "Pa", "s_sh": "Pa",
                 "s_bond": "Pa"},
          equation="as CALC-C4-BLOCK with h = core depth at the tube (z_upper - z_lower at x_t): tube bore s = 6M/(d h^2)"
                   " + F/(d h); shear-out tau = (1.5 M / h)/(e h), e = (W - d)/2; spar bore s = 6M/(d W^2) + F/(d W); "
                   "web s = 6M/(W h^2), tau = M/(0.21 W h^2); bond torsion tau = 2 My sf fit prt/(pi d^2 W)",
          cites=["SRC-C4-ROARK"], tol=1e-6)
def block_d3(m_des_c1, m_task, f_ult, my_lim, sf, fit, prt, d, d_spar, skin, x_t, W, s_brg, s_ten, s_sh, s_bond):
    sk = np.array(skin, float)
    h = float(np.interp(x_t, sk[:, 0], sk[:, 1]) - np.interp(x_t, sk[:, 0], sk[:, 2]))
    M = max(m_des_c1, m_task * sf * fit * prt)
    F = f_ult * fit * prt
    s_tb = 6 * M / (d * h * h) + F / (d * h)
    tau_so = (1.5 * M / h) / ((W - d) / 2 * h)
    s_sb = 6 * M / (d_spar * W * W) + F / (d_spar * W)
    s_web, tau_web = 6 * M / (W * h * h), M / (0.21 * W * h * h)
    tau_bt = 2 * my_lim * sf * fit * prt / (math.pi * d_spar ** 2 * W)
    ms = {"ms_tube_bore": s_brg / s_tb - 1, "ms_shear_out": s_sh / tau_so - 1, "ms_spar_bore": s_brg / s_sb - 1,
          "ms_web_bend": s_ten / s_web - 1, "ms_web_torsion": s_sh / tau_web - 1, "ms_bond_torsion": s_bond / tau_bt - 1}
    return {"h_core_m": h, "M_design_nm": M, "F_design_n": F, "s_tube_bore_pa": s_tb, "tau_shear_out_pa": tau_so,
            "s_spar_bore_pa": s_sb, **ms, "ms_min": min(ms.values()), "spar_couple_n": 1.5 * M / W,
            "tube_couple_n": 1.5 * M / h}


@kit.calc("CALC-C4-D3-MASS", title="Fins mass, recommended design (D3's CAD corrected to two layers, the 0.21 m half "
          "height and the brace strip as drawn)",
          inputs={**GEOM, "m_d3": "CL-D3-MASS", "basis": "ASM-C4-D3-MASS-BASIS", "lay_rec": P + "fins.layers",
                  "adh": P + "fin_detail.fin.adhesive_kgm2"},
          units={**GU, "m_d3": "g", "basis": "-, m, m", "lay_rec": "-", "adh": "kg/m2"},
          equation="half-fin area A(hh) = integral over x_le..x_te of (z_top(x) - z_skin(x)), z_top linear from the "
                   "collar top to hh, 2 upper + 2 lower; boards = (areal + adh) [lay_rec A(hh) - lay_b A(hh_b)]; braces "
                   "= rho_cf w (t - t_b) sum of the four lengths (ear to anchor); (lay_b, hh_b, t_b) = CL-D3-MASS "
                   "basis; total = CL-D3-MASS + boards + braces", tol=1e-6)
def fins_mass_d3(**k):
    g = {n: k[n] for n in GEOM}
    sk = np.array(g["skin"], float)
    x_le = g["tube_x"] + g["od"] / 2 + g["le_gap"]
    z_top_le = g["tube_len"] / 2 - g["grip"] - g["sc_gap"]
    xs = np.linspace(x_le, g["x_te"], 201)

    def areas(h):
        top = z_top_le + (h - z_top_le) * (xs - x_le) / (g["x_te"] - x_le)
        return (float(np.trapezoid(top - np.interp(xs, sk[:, 0], sk[:, 1]), xs)),
                float(np.trapezoid(top + np.interp(xs, sk[:, 0], sk[:, 2]), xs)))
    lay_b, hh_b, t_b = k["basis"]
    a_up, a_lo = areas(g["hh"])
    b_up, b_lo = areas(hh_b)
    boards = (g["areal"] + k["adh"]) * 2 * (k["lay_rec"] * (a_up + a_lo) - lay_b * (b_up + b_lo)) * 1000
    L = 0.0
    for side in SIDES:
        geo = geometry(g, side)
        ear = np.array([g["tube_x"], geo["ear"][1], geo["z_sc"]])
        L += 2 * float(np.linalg.norm(np.array(geo["anchor"]) - ear))
    braces = g["rho_cf"] * g["b_w"] * (g["b_t"] - t_b) * L * 1000
    return {"area_up_m2": a_up, "area_lo_m2": a_lo, "added_g": boards, "brace_delta_g": braces,
            "total_g": k["m_d3"] + boards + braces}


# ====================================================================== claims
R_VIB, R_SM, R_JNT = ["R-VIBRATION"], ["R-STRUCT-MARGIN"], ["R-FIN-TUBE-JOINT"]
TUBES = ["FIN-002-R", "FIN-002-L"]
HALF = ["FIN-001-RU", "FIN-001-LU", "FIN-001-RD", "FIN-001-LD"]
BRACE = ["FIN-009-UR", "FIN-009-UL", "FIN-009-LR", "FIN-009-LL"]
COLLAR = ["FIN-008-UR", "FIN-008-UL", "FIN-008-LR", "FIN-008-LL"]
ANCHOR = ["FIN-010-UR", "FIN-010-UL", "FIN-010-LR", "FIN-010-LL"]
MOUNT = ["FIN-003-UR", "FIN-003-UL", "FIN-003-LR", "FIN-003-LL"]
BLOCK = ["FIN-004-R", "FIN-004-L"]
TAP = ("Tap test of one finished quarter, upper and lower (T-C4-TAP): FFT of the FC raw IMU; then hover VIBE < 30 m/s2, "
       "Clip 0.")

kit.claim("CL-C4-D3-Q4-RECT", "Quad shell = R1 rectangle element on a rectangle", calc="CALC-C4-D3-Q4-CHECK",
          output="err_rect", unit="-", limit=("<=", 1e-9), how="Re-run fin_structures_d3.py.")
kit.claim("CL-C4-D3-Q4-SKEW", "Skewed-mesh cantilever plate vs Leissa", calc="CALC-C4-D3-Q4-CHECK", output="err_skew",
          unit="-", limit=("<=", 0.02), cites=["SRC-C4-LEISSA"], how="Re-run fin_structures_d3.py (16 x 16, 20 % skew).")
kit.claim("CL-C4-D3-MESH-CONV", "Mesh convergence of the station modes, D3 quarter", calc="CALC-C4-D3-CONVERGENCE",
          output="change", unit="-", limit=("<=", 0.03), how="Meshes 6x5, 12x10, 24x20 on both quarters.")
kit.claim("CL-C4-D3-SEP-1L", "Mode separation with one board layer (rejected option), R3 geometry, nominal",
          calc="CALC-C4-D3-MODES",
          output="sep_op", unit="-", limit=(">=", LIMIT_SEP), parts=TUBES + HALF + BRACE + MOUNT, how=TAP,
          note="FAILS: motor twist about the tube coupled with fore-aft nodding near 2P cruise (200 Hz); the one-layer "
               "board stores 45-70 % of the strain energy. Not the design of record: see CL-C4-D3-SEP.")
kit.claim("CL-C4-D3-F1-1L", "First station mode with one board layer (rejected option), lower quarter",
          calc="CALC-C4-D3-MODES", output="f1_lo", unit="Hz", parts=TUBES + HALF, how=TAP)
kit.claim("CL-C4-D3-F1-UP", "First station mode, recommended (two layers), upper quarter", calc="CALC-C4-D3-MODES-REC",
          output="f1_up", unit="Hz", parts=TUBES + HALF[:2] + BRACE[:2] + MOUNT[:2], how=TAP)
kit.claim("CL-C4-D3-F1-LO", "First station mode, recommended (two layers), lower quarter", calc="CALC-C4-D3-MODES-REC",
          output="f1_lo", unit="Hz", parts=TUBES + HALF[2:] + BRACE[2:] + MOUNT[2:], how=TAP,
          note="The lower tube is 14 mm longer outside the bore (cambered wing); the lower quarter governs.")
kit.claim("CL-C4-D3-PANEL", "First fin-panel mode (TE tip with the foot), recommended, upper quarter",
          calc="CALC-C4-D3-MODES-REC", output="panel_up", unit="Hz", parts=HALF, how="Tap the TE tip with the foot fitted.",
          note="Below the forcing band; < 10 % of its energy reaches the station.")
kit.claim("CL-C4-D3-SEP", "Mode separation from the 1P/2P operating points, recommended design (nominal)",
          calc="CALC-C4-D3-MODES-REC", output="sep_op", unit="-", limit=(">=", LIMIT_SEP), verifies=R_VIB,
          parts=TUBES + HALF + BRACE + MOUNT, how=TAP)
kit.claim("CL-C4-D3-SEP-WORST", "Mode separation, recommended design, worst tube E/G corner", calc="CALC-C4-D3-WORST",
          output="sep_op_worst", unit="-", limit=(">=", LIMIT_SEP), verifies=R_VIB, parts=TUBES,
          how="T-C4-TUBE-BEND and T-C4-TUBE-TORSION on the bought tube (I1, H1), then T-C4-TAP-D3.")
kit.claim("CL-C4-D3-SEP-WHIRL", "Whirl separation incl. prop gyroscopics, recommended design", calc="CALC-C4-D3-CAMPBELL",
          output="sep_whirl", unit="-", limit=(">=", LIMIT_SEP), verifies=R_VIB, parts=TUBES, how=TAP)
kit.claim("CL-C4-D3-SEP-BAND", "Separation from the whole 80-330 Hz band (B4 rule), recommended design",
          calc="CALC-C4-D3-MODES-REC", output="sep_band", unit="-", limit=(">=", LIMIT_SEP), parts=TUBES,
          how="Needs every station mode >= 396 Hz; R-VIBRATION (operating points) is the criterion of record (CR-C4-06).",
          note="FAILS by design intent: no buildable 22 mm tube station reaches 396 Hz; rpm-tracking notch is the backup.")
kit.claim("CL-C4-D3-MOUNT-K-REQ", "Mount rocking stiffness needed for 20 % separation (worst of nominal / low E,G)",
          calc="CALC-C4-D3-MOUNT-K", output="k_req", unit="N m/rad", limit=("<=", "ASM-C4-MOUNT-K-ROCK"),
          verifies=R_VIB, parts=MOUNT,
          how="T-C4-MOUNT-STIFF: side load at the prop nut on a mount clamped on a tube stub; rotation from two dial "
              "gauges; k = F a / theta.")
kit.claim("CL-C4-D3-MS-FACE", "Fin face margin, recommended design, worst case and side", calc="CALC-C4-D3-STATIC",
          output="ms_face", unit="-", limit=(">=", 0.0), verifies=R_SM, parts=HALF,
          how="T-C4-BOARD-COUPON for the face allowable; T-C4-FIN-PROOF at 1.5 x L4.")
kit.claim("CL-C4-D3-MS-EDGE", "Edge-strip margin, recommended design", calc="CALC-C4-D3-STATIC", output="ms_edge", unit="-",
          limit=(">=", 0.0), verifies=R_SM, parts=HALF, how="T-C4-FIN-PROOF.")
kit.claim("CL-C4-D3-MS-TUBE", "Motor tube bending margin at the bore end", calc="CALC-C4-D3-STATIC", output="ms_tube",
          unit="-", limit=(">=", 0.0), verifies=R_SM, parts=TUBES, how="T-C4-FIN-PROOF (G2 at the tube end).")
kit.claim("CL-C4-D3-MS-BRACE", "Brace buckling margin (strip as drawn, fin_detail.brace.t_m; design load incl. fitting "
          "factor)",
          calc="CALC-C4-D3-STATIC", output="ms_brace_buckling", unit="-", limit=(">=", 0.0), verifies=R_SM, parts=BRACE,
          how="T-C4-FIN-PROOF G2 both senses; no visible bow.")
kit.claim("CL-C4-D3-BRACE-F", "Brace design force (compression, incl. 1.5 x 1.15)", calc="CALC-C4-D3-STATIC",
          output="brace_comp_design_n", unit="N", parts=BRACE + ANCHOR, how="C2 checks the spar under the anchor.")
kit.claim("CL-C4-D3-MS-BRACE-END", "Brace-end bond margin (10 mm engagement in the ear and anchor slots)",
          calc="CALC-C4-D3-STATIC", output="ms_brace_end_bond", unit="-", limit=(">=", 0.0), verifies=R_SM + R_JNT,
          parts=BRACE + COLLAR + ANCHOR, how="C6 lap-shear coupons; T-C4-FIN-PROOF.")
kit.claim("CL-C4-D3-MS-COLLAR", "Station-collar bond margin on the tube (torsion + brace shear)",
          calc="CALC-C4-D3-STATIC", output="ms_collar_bond", unit="-", limit=(">=", 0.0), verifies=R_SM + R_JNT,
          parts=COLLAR, how="T-C4-FIN-PROOF at 1.5 x L4; witness line across collar and tube does not move.")
kit.claim("CL-C4-D3-MS-ANCHOR", "Anchor bond margin on the spar (brace tension, peel knock-down)",
          calc="CALC-C4-D3-STATIC", output="ms_anchor_bond", unit="-", limit=(">=", 0.0), verifies=R_SM + R_JNT,
          parts=ANCHOR, how="T-C4-FIN-PROOF G2 in the tension sense; C6 peel coupon PETG on CF.")
kit.claim("CL-C4-D3-MS-EAR", "Station-collar ear root margin (brace force, interlayer bending)", calc="CALC-C4-D3-STATIC",
          output="ms_ear_root", unit="-", limit=(">=", 0.0), verifies=R_SM, parts=COLLAR,
          how="T-C4-FIN-PROOF G2 both senses; print the collar with layers in x-y (ear bending loads the layer lines).")
COLLAR_H = P + "fin_detail.station_collar.height_m"
kit.claim("CL-C4-D3-COLLAR-T", "Station-collar torsion into the tube, limit (envelope: LE fillet intact or cracked, "
          "both quarters, every case)", calc="CALC-C4-D3-STATIC", output="collar_t_lim_nm", unit="N m", parts=COLLAR,
          how="T-C4-FIN-PROOF with the LE fillet left unbonded on one quarter; witness line across collar and tube.",
          note="The number C6 sizes the collar bond to (CR-C6-03). Supersedes the 9.3 N m C6 carried in "
               "ASM-C6-C4-COLLAR-T, which is not a C4 output.")
kit.claim("CL-C4-D3-COLLAR-T-INTACT", "Station-collar torsion, limit, LE fillet intact", calc="CALC-C4-D3-STATIC",
          output="collar_t_lim_intact_nm", unit="N m", parts=COLLAR, how="As CL-C4-D3-COLLAR-T.")
kit.claim("CL-C4-D3-COLLAR-H-REQ", "Station-collar height needed for MS 0 on the envelope torsion + brace shear",
          calc="CALC-C4-D3-STATIC", output="collar_h_req_m", unit="m", limit=("<=", COLLAR_H), verifies=R_JNT,
          parts=COLLAR, how="C6 lap-shear coupon on scuffed CF; T-C4-FIN-PROOF.")
kit.claim("CL-C4-D3-TUBE-T-ROOT", "Tube torsion at the bore end, limit (for C1's J-FINHALF comparison)",
          calc="CALC-C4-D3-STATIC", output="tube_t_root_lim_nm", unit="N m", parts=TUBES, how="T-C4-FIN-PROOF.")
kit.claim("CL-C4-D3-SIDE-LOAD", "Foot side load used (pad friction 0.7, CR-C5-09)", calc="CALC-C4-D3-STATIC",
          output="side_load_n", unit="N", parts=HALF, how="D5 pad friction coupon (ASM-D5-PAD-MU).")
kit.claim("CL-C4-D3-STRIP-Q", "Edge-strip-to-paper shear flow per face, limit, FE (CR-C6-02a)", calc="CALC-C4-D3-STATIC",
          output="strip_q_lim_npm", unit="N/m", parts=HALF, how="T-C4-FIN-PROOF: no strip lift; T-C6-BOARD-LAP.")
kit.claim("CL-C4-D3-MS-STRIP-PAPER", "Edge strip bonded to the paper face only (no pins): margin on the paper-to-foam "
          "shear", calc="CALC-C4-D3-STATIC", output="ms_strip_paper", unit="-", limit=(">=", 0.0), verifies=R_SM,
          parts=HALF, how="T-C6-BOARD-LAP for the allowable; T-C4-FIN-PROOF at 1.5 x L4.")
kit.claim("CL-C4-D3-STRIP-END-F", "Edge-strip force per face at the collar end, design (for C6's tail anchorage)",
          calc="CALC-C4-D3-STATIC", output="strip_end_face_design_n", unit="N", parts=COLLAR + HALF,
          how="T-C6-STRIP-ANCHOR.", note="Replaces the 1 348 N C6 derived from the strip allowable (CR-C6-01).")
kit.claim("CL-C4-D3-STRIP-PIN-F", "Through-pin shear per pin if the pins carry the whole strip shear flow, design "
          "(CR-C6-02b)", calc="CALC-C4-D3-STATIC", output="strip_pin_design_n", unit="N", parts=HALF,
          how="T-C4-FIN-PROOF with pins fitted; C6 pin coupon.",
          note="C6 sized the pins to 77 N (CL-C6-STRIP-PIN-RF 1.41); the FE load is lower.")
kit.claim("CL-C4-D3-BRACE-10X2-SEP", "Mode separation with a 10 x 2 brace", calc="CALC-C4-D3-BRACE-TRADE",
          output="sep_t2", unit="-", limit=(">=", LIMIT_SEP), parts=BRACE, how="T-C4-TAP-D3 on a 10 x 2 quarter.")
kit.claim("CL-C4-D3-BRACE-10X2-MS", "Brace buckling margin with a 10 x 2 strip (G2 design)",
          calc="CALC-C4-D3-BRACE-TRADE", output="ms_buckle_t2", unit="-", limit=(">=", 0.0), parts=BRACE,
          how="T-C4-FIN-PROOF G2 both senses.")
kit.claim("CL-C4-D3-BRACE-10X3-SEP", "Mode separation with a 10 x 3 brace", calc="CALC-C4-D3-BRACE-TRADE",
          output="sep_t3", unit="-", limit=(">=", LIMIT_SEP), parts=BRACE, how="T-C4-TAP-D3.")
kit.claim("CL-C4-D3-BRACE-SAVE", "Mass saved by 10 x 2 braces instead of 10 x 3 (four braces)",
          calc="CALC-C4-D3-BRACE-TRADE", output="mass_saving_g", unit="g", parts=BRACE, how="Weigh the strips.")
kit.claim("CL-C4-D3-CANT-SIDE", "Thrust side component at 7 deg cant (fraction of thrust)", calc="CALC-C4-D3-MOUNT-CANT",
          output="side_frac", unit="-", parts=MOUNT, how="Check the printed plate angle with a protractor.")
kit.claim("CL-C4-D3-MOUNT-AXIAL", "Mount pull-off load along the tube from the cant, design", calc="CALC-C4-D3-MOUNT-CANT",
          output="axial_design_n", unit="N", parts=MOUNT, how="T-D3-SLIP.")
kit.claim("CL-C4-D3-MOUNT-TWIST", "Mount twist about the tube from the cant, design", calc="CALC-C4-D3-MOUNT-CANT",
          output="twist_design_nm", unit="N m", parts=MOUNT, how="T-D3-SLIP.")
kit.claim("CL-C4-D3-MOUNT-ROCK", "Mount rocking moment at T_lim with the cant, design", calc="CALC-C4-D3-MOUNT-CANT",
          output="rock_design_nm", unit="N m", parts=MOUNT, how="T-C4-MOUNT-STIFF (load to 1.5 x limit).")
kit.claim("CL-C4-D3-MS-MOUNT-SLIP", "Slip clamp holds in flight with the cant (C1 moment + cant twist + pull-off)",
          calc="CALC-C4-D3-MOUNT-CANT", output="ms_slip_hold", unit="-", limit=(">=", 0.0), verifies=R_SM,
          parts=MOUNT, how="T-D3-SLIP: set 2.5 N m; witness line checked before every flight.")
kit.claim("CL-C4-D3-FOOT-DEFL", "Foot deflection under L4 (limit), recommended design", calc="CALC-C4-D3-STATIC",
          output="dfoot_L4_m", unit="m", parts=HALF, how="T-C4-FIN-PROOF: dial gauge at the foot.")
kit.claim("CL-C4-D3-BLOCK-MS", "Through-core block minimum margin, D3 geometry", calc="CALC-C4-D3-BLOCK",
          output="ms_min", unit="-", limit=(">=", 0.0), verifies=R_JNT + R_SM, parts=BLOCK,
          how="T-C4-BLOCK-PROOF (30 N m for 1 min on a block in a core offcut).")
kit.claim("CL-C4-D3-SPAR-COUPLE", "Bearing couple on the spar at each block (design), D3 geometry",
          calc="CALC-C4-D3-BLOCK", output="spar_couple_n", unit="N", parts=BLOCK, how="C2 spar crushing check (CR-C4-02).")

kit.claim("CL-C4-D3-FINS-MASS", "Fins subsystem mass, recommended design (D3 CAD + second board layer)",
          calc="CALC-C4-D3-MASS", output="total_g", unit="g", limit=("<=", P + "mass.allocation_g.fins"),
          parts=HALF, how="T-D3-WEIGH; A3 roll-up.",
          note="Allocation 408 g since D-26/D-38 (CR-C4-15 closed). Falls back to CL-D3-MASS alone once D3 re-runs "
               "make_fins.py at R3 and ASM-C4-D3-MASS-BASIS is set to (2, 0.21).")
kit.claim("CL-C4-D3-LAYER-ADD", "Board mass added to CL-D3-MASS: second layer and 0.21 m half height, four half-fins",
          calc="CALC-C4-D3-MASS",
          output="added_g", unit="g", parts=HALF, how="Weigh the boards before and after laminating.")

kit.test("T-C4-MOUNT-STIFF", "Mount rocking stiffness on the bench", verifies=["CL-C4-D3-MOUNT-K-REQ"],
         procedure="Mount with motor clamped on a 60 mm tube stub held in a vice; 0.5 kg over a pulley at the prop nut, "
                   "sideways (y) and fore-aft (z); dial gauges at the motor can top and at the collar; theta = "
                   "(d_can - d_collar) / spacing; k = F a / theta. Pass: k >= the CL-C4-D3-MOUNT-K-REQ value in both "
                   "directions.")
kit.test("T-C4-TAP-D3", "Tap test, as-built upper and lower quarter",
         verifies=["CL-C4-D3-SEP", "CL-C4-D3-F1-UP", "CL-C4-D3-F1-LO", "CL-C4-D3-SEP-WHIRL", "CL-C4-D3-PANEL",
                   "CL-C4-D3-SEP-WORST"],
         procedure="Finished wing on foam blocks, props on; tap each motor bell in y and in z; FC raw IMU at 1 kHz (or a "
                   "phone accelerometer taped to the can); FFT peaks vs 1P/2P at hover, cruise and the cap.")


# ====================================================================== figure + results
def campbell_svg(path, curves, rpm_ops, rpm_max=10000.0, f_max=500.0):
    W, H, L, R, T, B = 1200, 560, 90, 40, 30, 60
    sx = lambda r: L + (W - L - R) * r / rpm_max
    sy = lambda f: H - B - (H - B - T) * f / f_max
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, system-ui, sans-serif">']
    for p in (1, 2):
        pts = [(sx(r), sy(p * r / 60 * 1.2)) for r in (0, rpm_max)] + [(sx(r), sy(p * r / 60 * 0.8)) for r in (rpm_max, 0)]
        o.append('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) +
                 '" fill="#E2E6EC" fill-opacity="0.6" stroke="none"/>')
    for f in range(0, int(f_max) + 1, 100):
        o.append(f'<line x1="{L}" y1="{sy(f):.1f}" x2="{W - R}" y2="{sy(f):.1f}" stroke="#E3E7ED" stroke-width="0.75"/>')
        o.append(f'<text x="{L - 10}" y="{sy(f) + 4:.1f}" font-size="12" font-family="IBM Plex Mono, monospace" '
                 f'fill="#6B7280" text-anchor="end">{f} Hz</text>')
    for r in range(0, int(rpm_max) + 1, 2000):
        o.append(f'<text x="{sx(r):.1f}" y="{H - B + 20}" font-size="12" font-family="IBM Plex Mono, monospace" '
                 f'fill="#6B7280" text-anchor="middle">{r:,}'.replace(",", " ") + '</text>')
    o.append(f'<text x="{(L + W - R) / 2}" y="{H - 12}" font-size="12" fill="#4B5563" text-anchor="middle">rotor speed, rpm</text>')
    for p in (1, 2):
        r1 = min(rpm_max, f_max * 60 / p)
        o.append(f'<line x1="{sx(0):.1f}" y1="{sy(0):.1f}" x2="{sx(r1):.1f}" y2="{sy(p * r1 / 60):.1f}" stroke="#4B5563" '
                 f'stroke-width="1.25"/>')
        o.append(f'<text x="{sx(r1) - 6:.1f}" y="{sy(p * r1 / 60) + 16:.1f}" font-size="12" font-family="IBM Plex Mono, '
                 f'monospace" fill="#4B5563" text-anchor="end">{p}P ± 20 %</text>')
    for name, r in rpm_ops.items():
        o.append(f'<line x1="{sx(r):.1f}" y1="{T}" x2="{sx(r):.1f}" y2="{H - B}" stroke="#9AA4B1" stroke-width="0.75" '
                 f'stroke-dasharray="6 4"/>')
        o.append(f'<text x="{sx(r) + 4:.1f}" y="{T + 12}" font-size="11" fill="#6B7280">{name}</text>')
    for label, (rpms, fr, colour, dash) in curves.items():
        for j in range(fr.shape[1]):
            pts = " ".join(f"{sx(r):.1f},{sy(f):.1f}" for r, f in zip(rpms, fr[:, j]) if np.isfinite(f) and f <= f_max)
            if pts:
                o.append(f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="2" '
                         + (f'stroke-dasharray="{dash}"' if dash else "") + "/>")
        y_lab = sy(min(fr[-1, 0], f_max)) - 8
        o.append(f'<text x="{W - R - 4}" y="{y_lab:.1f}" font-size="12" fill="{colour}" text-anchor="end">{label}</text>')
    o.append(f'<line x1="{L}" y1="{H - B}" x2="{W - R}" y2="{H - B}" stroke="#9AA4B1" stroke-width="1"/>')
    o.append("</svg>")
    path.write_text("\n".join(o) + "\n", encoding="utf-8")


if __name__ == "__main__":
    kit.write()
    g = {n: kit.value(r) for n, r in GEOM.items()}
    E0, G0 = kit.value("ASM-J1-E-TUBE"), kit.value("ASM-C4-G-TUBE")
    rpm = tuple(kit.value(RPM[k]) for k in ("rpm_h", "rpm_c", "rpm_x"))
    res = {"inputs": {k: v for k, v in g.items() if k != "skin"}, "geometry": {s: geometry(g, s) for s in SIDES},
           "configs": {}, "sensitivity": {}}
    variants = {"1 layer (CR-D3-02, rejected)": {"layers": 1},
                "recommended (2 layers)": {"layers": 2},
                "2 layers, brace 10 x 3": {"layers": 2, "_g": {"b_t": 0.003}},
                "2 layers, no brace": {"layers": 2, "brace": False},
                "2 layers, no edge strips": {"layers": 2, "edge": False},
                "2 layers, no brace, no strips": {"layers": 2, "brace": False, "edge": False},
                "2 layers, rigid mount": {"layers": 2, "k_rock": None},
                "2 layers, mount 1 000 N m/rad": {"layers": 2, "k_rock": 1000.0},
                "2 layers, rigid root": {"layers": 2, "k_root": None},
                "2 layers, root 3 000 N m/rad": {"layers": 2, "k_root": 3000.0},
                "2 layers, half height 0.19 m (R2)": {"layers": 2, "hh": 0.19},
                "2 layers, LE fillet cracked": {"layers": 2, "le_cracked": True},
                "1 layer, rigid mount and root": {"layers": 1, "k_rock": None, "k_root": None}}
    for name, kw in variants.items():
        for side in SIDES:
            kw2 = {a: b for a, b in kw.items() if a != "_g"}
            r = summary({**g, **kw.get("_g", {})}, E0, G0, side, rpm, **kw2)
            res["configs"][f"{name} / {side}"] = r
            print(f"{name:40s} {side:5s} station {[round(x) for x in r['f_st'][:3]]} "
                  f"panel {r['f_panel']:5.1f}  sep {r['sep_op']:+.2f} ({r['nearest']})  band {r['sep_band']:+.2f}")
    for side in SIDES:
        rows = []
        for E, G in itertools.product((70e9, 100e9, 135e9), (3e9, 5e9, 10e9)):
            r = summary(g, E, G, side, rpm, layers=2)
            rows.append({"E_GPa": E / 1e9, "G_GPa": G / 1e9, "f_st1": r["f_st1"], "f_st2": r["f_st2"],
                         "sep": r["sep_op"], "nearest": r["nearest"]})
        res["sensitivity"][side] = rows
    rpms = np.linspace(0, 10000, 41)
    curves = {}
    for label, side, lay, colour, dash in (("1 layer (rejected), lower", "lower", 1, "#6B7280", "8 5"),
                                           ("recommended, 2 layers, upper", "upper", 2, "#9AA4B1", None),
                                           ("recommended, 2 layers, lower (governs)", "lower", 2, "#1F5FC7", None)):
        mdl = fe.build_q(model_cfg(g, E0, G0, side, layers=lay))
        fr = [(station_whirl(mdl, g["ip"] + g["i_bell"], r, axis=spin_axis(g)) + [np.nan] * 4)[:4] for r in rpms]
        curves[label] = (rpms, np.array(fr, float), colour, dash)
        res.setdefault("campbell", {})[label] = {"rpm": rpms.tolist(), "f_hz": np.array(fr, float).tolist()}
    campbell_svg(HERE / "fig-c4-02-campbell-d3.svg", curves, {"hover": rpm[0], "cruise": rpm[1], "F4 cap": rpm[2]})
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "results_d3.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")
    print("wrote out/results_d3.json and fig-c4-02-campbell-d3.svg")
