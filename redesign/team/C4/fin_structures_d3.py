"""C4 R2: fin / motor-tube structures on D3's as-designed geometry (CR-D3-10), K09-L.

Run:  python -I redesign/team/C4/fin_structures_d3.py      (about 20 s)
Writes claims.d3.json beside this file (proof chain), out/results_d3.json and fig-c4-02-campbell-d3.svg.
Then: python -I redesign/proofs/build_graph.py

What changed against R1 (fin_structures.py, kept for the concept study and for D3's ratio calc):
  * cambered wing: the tube leaves the skin at +19.8 / -7.9 mm (S5010 at x 0.045), so the lower quarter has the
    longer free tube; both quarters are modelled (upper UR, lower LR = mirror in z with the lower skin);
  * clamp at the ends of D3's 47 mm bore (bosses 8 mm proud of the skin, CF plug inside), root rotational spring;
  * tube ends at 0.172 m (CR-D3-01): the printed mount carries the motor 18 mm beyond the tube end; the mount is a
    rotational spring (rocking and twist) between the tube end and the motor/prop/mount rigid body (CAD CG);
  * brace 10 x 3 mm on a station collar at z 0.1535 (ear 17.8 mm inboard of the tube axis) to an anchor on the spar
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
      "m_esc": "kg", "esc_x0": "m", "esc_len": "m", "esc_z": "m", "landing_g": "g", "t_board": "m", "areal": "kg/m2",
      "layers": "-", "t_face": "m", "e_face": "Pa", "e_core": "Pa", "g_core": "Pa", "x_spar": "m", "y_anchor": "m",
      "proud": "m", "b_w": "m", "b_t": "m", "e_strip": "Pa", "e_w": "m", "e_t": "m", "rho_cf": "kg/m3", "chord": "m",
      "el_frac": "-", "slot_hw": "m", "k_rock": "N m/rad", "k_twist": "N m/rad", "k_root": "N m/rad",
      "k_anchor": "N/m"}
RPM = {"rpm_h": "CL-B4-HOVER-RPM", "rpm_c": "CL-B4-CRUISE-RPM", "rpm_x": "CL-B4-RPM-MAX"}
RU = {k: "rpm" for k in RPM}
TUBE = {"E": "ASM-J1-E-TUBE", "G": "ASM-C4-G-TUBE"}
TU = {"E": "Pa", "G": "Pa"}
MESH = (12, 10)
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


def model_cfg(g, E, G, side, mesh=MESH, brace=True, edge=True, k_rock="nom", k_root="nom", hh=None, layers=None):
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
                   "root_free": geo["root_free"]},
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
    return {"f_st": [x for x, _ in st], "kinds": [k for _, k in st], "f_st1": st[0][0], "f_st2": st[1][0] if len(st) > 1
            else st[0][0], "f_panel": pn[0] if pn else float(f[-1]),
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


@kit.calc("CALC-C4-D3-MODES", title="Station modes, D3 as-designed quarter (upper UR and lower LR), nominal E/G",
          inputs=INS, units=UNS, tol=1e-4,
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
        r = summary(g, k["E"], k["G"], side, rpm, k["lo"], k["hi"])
        s = side[:2]
        out.update({f"f1_{s}": r["f_st1"], f"f2_{s}": r["f_st2"], f"panel_{s}": r["f_panel"], f"sep_{s}": r["sep_op"],
                    f"band_{s}": r["sep_band"]})
    out["f1_min"] = min(out["f1_up"], out["f1_lo"])
    out["sep_op"] = min(out["sep_up"], out["sep_lo"])
    out["sep_band"] = min(out["band_up"], out["band_lo"])
    return out


@kit.calc("CALC-C4-D3-WORST", title="Separation over the tube E/G corners and the mount/root stiffness range",
          inputs={**GEOM, **RPM, "E0": "ASM-J1-E-TUBE", "E_lo": "ASM-C4-E-TUBE-LO", "E_hi": "ASM-C4-E-TUBE-HI",
                  "G0": "ASM-C4-G-TUBE", "G_lo": "ASM-C4-G-TUBE-LO", "G_hi": "ASM-C4-G-TUBE-HI"},
          units={**GU, **RU, "E0": "Pa", "E_lo": "Pa", "E_hi": "Pa", "G0": "Pa", "G_lo": "Pa", "G_hi": "Pa"}, tol=1e-4,
          equation="min over side x E {lo, nom, hi} x G {lo, nom, hi} of sep_op (18 FE runs), mount and root at "
                   "their nominal springs",
          assumes=["ASM-C4-E-TUBE-LO", "ASM-C4-E-TUBE-HI", "ASM-C4-G-TUBE-LO", "ASM-C4-G-TUBE-HI"])
def worst_d3(**k):
    g = {n: k[n] for n in GEOM}
    rpm = (k["rpm_h"], k["rpm_c"], k["rpm_x"])
    worst, f_min, at = 9.0, 1e9, ""
    for side, E, G in itertools.product(SIDES, (k["E_lo"], k["E0"], k["E_hi"]), (k["G_lo"], k["G0"], k["G_hi"])):
        r = summary(g, E, G, side, rpm)
        f_min = min(f_min, r["f_st1"])
        worst = min(worst, r["sep_op"])
    return {"sep_op_worst": worst, "f_station_min": f_min}


K_SWEEP = (500.0, 1000.0, 1500.0, 2000.0, 3000.0, 5000.0, 10000.0, 30000.0)


@kit.calc("CALC-C4-D3-MOUNT-K", title="Mount rocking stiffness needed for the separation rule (governing side)",
          inputs={**GEOM, **RPM, **TUBE, "sep_min": LIMIT_SEP, "E_lo": "ASM-C4-E-TUBE-LO", "G_lo": "ASM-C4-G-TUBE-LO"},
          units={**GU, **RU, **TU, "sep_min": "-", "E_lo": "Pa", "G_lo": "Pa"}, tol=1e-3,
          equation="sweep k_rock over 500-30 000 N m/rad (k_twist fixed) on both quarters at nominal and low E/G; "
                   "k_req = smallest k with sep_op >= sep_min at every larger k (log interpolation)")
def mount_k(**k):
    g = {n: k[n] for n in GEOM}
    rpm = (k["rpm_h"], k["rpm_c"], k["rpm_x"])

    def sep_at(kr, E, G):
        return min(summary(g, E, G, s, rpm, k_rock=kr)["sep_op"] for s in SIDES)

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


@kit.calc("CALC-C4-D3-CONVERGENCE", title="Mesh convergence, D3 quarter (both sides)",
          inputs={**GEOM, **TUBE}, units={**GU, **TU}, tol=1e-4,
          equation="first two station modes at fin meshes 6x5, 12x10 (used), 24x20; change = max |f(12x10)/f(24x20) - 1|")
def convergence_d3(**k):
    g = {n: k[n] for n in GEOM}
    out, ch = {}, 0.0
    for side in SIDES:
        fs = {}
        for tag, mesh in (("coarse", (6, 5)), ("used", MESH), ("fine", (24, 20))):
            r = station_modes(fe.build_q(model_cfg(g, k["E"], k["G"], side, mesh=mesh)))
            fs[tag] = (r["f_st1"], r["f_st2"])
            out[f"f1_{side[:2]}_{tag}"], out[f"f2_{side[:2]}_{tag}"] = r["f_st1"], r["f_st2"]
        ch = max(ch, abs(fs["used"][0] / fs["fine"][0] - 1), abs(fs["used"][1] / fs["fine"][1] - 1))
    out["change"] = ch
    return out


def station_whirl(mdl, ip_spin, rpm, n_modes=16):
    f0, Phi, _ = fe.modes(mdl, n_modes)
    cl = fe.classify(mdl, Phi)
    keep = [i for i, c in enumerate(cl) if c["ke_station"] >= ST_PART]
    w = 2 * math.pi * f0
    Gm = Phi.T @ (fe.gyro_matrix(mdl, ip_spin) @ Phi)
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


@kit.calc("CALC-C4-D3-CAMPBELL", title="Gyroscopic whirl separation, D3 quarter (both sides)",
          inputs={**GEOM, **RPM, **TUBE}, units={**GU, **RU, **TU}, tol=1e-4,
          equation="M q'' + Omega G q' + K q = 0 on 16 modes, G = -[Ip_spin e_shaft]x at the station; sep over 1P/2P "
                   "at hover and cruise and 1P at the cap, station whirl modes only",
          assumes=["ASM-C4-PROP-IP", "ASM-C1-BELL-INERTIA"])
def campbell_d3(**k):
    g = {n: k[n] for n in GEOM}
    worst = 9.0
    for side in SIDES:
        mdl = fe.build_q(model_cfg(g, k["E"], k["G"], side))
        for name, rpm in (("hover", k["rpm_h"]), ("cruise", k["rpm_c"]), ("max", k["rpm_x"])):
            for f in station_whirl(mdl, g["ip"] + g["i_bell"], rpm):
                for p in ((1,) if name == "max" else (1, 2)):
                    worst = min(worst, abs(f / (p * rpm / 60) - 1))
    return {"sep_whirl": worst}


STAT_IN = {"f_level": "CL-C1-FOOT-LEVEL", "f_corner": "CL-C1-FOOT-CORNER", "mu_g": "ASM-C1-FRICTION",
           "n_h": "ASM-C1-HANDLING-N", "m_gate": P + "requirements.mtow_gate_kg", "grav": P + "env.g_ms2",
           "t_lim": "CL-C1-T-LIMIT", "q_mot": "CL-C1-MOTOR-TORQUE", "sf": SF, "fit": FIT, "prt": PRT,
           "s_face": "ASM-C4-FACE-SIGMA", "s_cf": "ASM-C4-CF-SIGMA", "patch": "ASM-C4-FOOT-PATCH",
           "s_bond": "ASM-C4-BOND-SHEAR", "peel": "ASM-C4-PEEL-KD", "engage": P + "fin_detail.brace.engage_m",
           "a_lx": P + "fin_detail.anchor.len_x_m", "a_ly": P + "fin_detail.anchor.len_y_m",
           "d_spar": P + "wing.spar.od_m"}
STAT_U = {"f_level": "N", "f_corner": "N", "mu_g": "-", "n_h": "-", "m_gate": "kg", "grav": "m/s2", "t_lim": "N",
          "q_mot": "N m", "sf": "-", "fit": "-", "prt": "-", "s_face": "Pa", "s_cf": "Pa", "patch": "m", "s_bond": "Pa",
          "peel": "-", "engage": "m", "a_lx": "m", "a_ly": "m", "d_spar": "m"}


def fin_static(g, k, side):
    mdl = fe.build_q(model_cfg(g, k["E"], k["G"], side))
    pr = mdl.cfg["fin"]["props"]
    nodes = mdl.nodes
    corner = np.array([g["x_te"], 0.0, g["hh"]])
    foot = [n for n in mdl.fin_id.values() if np.linalg.norm(nodes[n] - corner) <= k["patch"] + 1e-9]
    nf, fc, mu = len(foot), k["f_corner"], k["mu_g"]
    G2 = k["n_h"] * k["m_gate"] * k["grav"]
    cases = {"L1": [(n, (-k["f_level"] / nf, 0, 0, 0, 0, 0)) for n in foot],
             "L4+": [(n, (-fc / nf, mu * fc / nf, 0, 0, 0, 0)) for n in foot],
             "L4-": [(n, (-fc / nf, -mu * fc / nf, 0, 0, 0, 0)) for n in foot],
             "L5": [(n, (-fc / nf, 0, -mu * fc / nf, 0, 0, 0)) for n in foot],
             "G2+": [(mdl.i_end, (0, G2, 0, 0, 0, 0))],
             "G2-": [(mdl.i_end, (0, -G2, 0, 0, 0, 0))],
             "H2": [(mdl.i_station, (-k["t_lim"], 0, 0, k["q_mot"], 0, 0))]}
    nu = pr["nu"]
    Qf = g["e_face"] / (1 - nu * nu) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    Cm = pr["A"] * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    Cb = pr["D"] * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    zf = pr["z_face_out"]
    s = mdl.strut_info[0]
    le_top = mdl.fin_id[(0, mdl.cfg["nz"])]
    ear = np.array(nodes[s["node"]]) - np.array([g["tube_x"], 0.0, nodes[s["node"]][2]])
    res = {}
    for cname, loads in cases.items():
        u = fe.static(mdl, loads)
        smax = 0.0
        for ns, xz in mdl.shells:
            ue = np.concatenate([u[6 * n:6 * n + 6] for n in ns])
            Nv, Mv = fe.shell_q4_resultants(xz, pr, ue)
            e0, kap = np.linalg.solve(Cm, Nv), np.linalg.solve(Cb, Mv)
            for z in (zf, -zf):
                sx, sz, txz = Qf @ (e0 + z * kap)
                smax = max(smax, abs((sx + sz) / 2) + math.hypot((sx - sz) / 2, txz))
        ke, _ = fe.frame_element(nodes[0], nodes[1], k["E"], k["G"], mdl.A_t, mdl.I_t, mdl.I_t, mdl.J_t, 1.0)
        fn = ke @ np.concatenate([u[0:6], u[6:12]])
        m_root = math.hypot(fn[3], fn[4])
        f_br = -s["k"] * float(np.dot(s["n"], u[6 * s["node"]:6 * s["node"] + 3]))      # + = compression
        s_edge, mz_strip = 0.0, 0.0
        for n1, n2, stf in mdl.stf_elems:
            ke, _ = fe.frame_element(nodes[n1], nodes[n2], stf["E"], stf["G"], stf["A"], 1e-15, stf["I_out"], stf["J"],
                                     1.0)
            fe_ = ke @ np.concatenate([u[6 * n1:6 * n1 + 6], u[6 * n2:6 * n2 + 6]])
            s_edge = max(s_edge, max(abs(fe_[5]), abs(fe_[11])) * stf["d"] / 2 / stf["I_out"] + abs(fe_[0]) / stf["A"])
            if n1 == le_top:
                mz_strip = abs(fe_[5])
        f_vec = -f_br * s["n"]                                                       # brace force on the ear
        t_collar = mz_strip + abs(ear[0] * f_vec[1] - ear[1] * f_vec[0])
        res[cname] = {"face": smax, "edge": s_edge, "tube": m_root * g["od"] / 2 / mdl.I_t, "mroot": m_root,
                      "brace": f_br, "t_collar": t_collar,
                      "dfoot": max(float(np.linalg.norm(u[6 * n:6 * n + 3])) for n in foot)}
    return res, s["L"]


@kit.calc("CALC-C4-D3-STATIC", title="Fin, tube, brace, collar and anchor strength, D3 quarter (both sides)",
          inputs={**GEOM, **TUBE, **STAT_IN}, units={**GU, **TU, **STAT_U}, tol=1e-4,
          equation="FE static, cases L1, L4 (both friction senses), L5, G2 (both senses, n_h m g at the tube end), H2; "
                   "ultimate = sf x limit (joints x fit x prt); face = Q_f (eps0 + z kappa); brace Pcr = pi^2 E w t^3 "
                   "/ (12 L^2); brace-end bond tau = F / (2 (w + t) engage); collar bond tau = T / (2 pi r^2 h) + F / "
                   "(pi d h); anchor tau = F / (len_y pi d_spar / 4) vs peel x bond allowable",
          assumes=["ASM-C4-FACE-SIGMA", "ASM-C4-BOND-SHEAR", "ASM-C4-PEEL-KD", "ASM-C4-FOOT-PATCH"],
          cites=["SRC-C4-ALLEN", "SRC-C4-ROARK"])
def static_d3(**k):
    g = {n: k[n] for n in GEOM}
    jf = k["sf"] * k["fit"] * k["prt"]
    out = {}
    agg = {"face": 0.0, "edge": 0.0, "tube": 0.0, "comp": 0.0, "tens": 0.0, "t_collar": 0.0, "f_collar": 0.0,
           "dfoot_L4": 0.0, "mroot": 0.0}
    for side in SIDES:
        res, L = fin_static(g, k, side)
        out[f"brace_len_{side[:2]}_m"] = L
        for c, r in res.items():
            agg["face"] = max(agg["face"], r["face"])
            agg["edge"] = max(agg["edge"], r["edge"])
            agg["tube"] = max(agg["tube"], r["tube"])
            agg["mroot"] = max(agg["mroot"], r["mroot"])
            agg["comp"] = max(agg["comp"], r["brace"])
            agg["tens"] = max(agg["tens"], -r["brace"])
            agg["t_collar"] = max(agg["t_collar"], r["t_collar"])
            agg["f_collar"] = max(agg["f_collar"], abs(r["brace"]))
            if c.startswith("L4"):
                agg["dfoot_L4"] = max(agg["dfoot_L4"], r["dfoot"])
            out[f"face_{side[:2]}_{c}_mpa"] = r["face"] * k["sf"] / 1e6
            out[f"brace_{side[:2]}_{c}_n"] = r["brace"]
    L = max(out["brace_len_up_m"], out["brace_len_lo_m"])
    face_u, edge_u, tube_u = agg["face"] * k["sf"], agg["edge"] * k["sf"], agg["tube"] * k["sf"]
    comp_d, tens_d = agg["comp"] * k["sf"] * k["fit"], agg["tens"] * k["sf"] * k["fit"]
    pcr = math.pi ** 2 * g["e_strip"] * g["b_w"] * g["b_t"] ** 3 / 12 / L ** 2
    f_end = max(agg["comp"], agg["tens"]) * jf
    tau_end = f_end / (2 * (g["b_w"] + g["b_t"]) * k["engage"])
    r_t, h_c = g["od"] / 2, g["sc_h"]
    tau_collar = agg["t_collar"] * jf / (2 * math.pi * r_t ** 2 * h_c) + agg["f_collar"] * jf / (math.pi * g["od"] * h_c)
    tau_anchor = agg["tens"] * jf / (k["a_ly"] * math.pi * k["d_spar"] / 4)
    ms = {"ms_face": k["s_face"] / face_u - 1, "ms_edge": k["s_cf"] / edge_u - 1, "ms_tube": k["s_cf"] / tube_u - 1,
          "ms_brace_buckling": pcr / max(comp_d, 1e-9) - 1, "ms_brace_end_bond": k["s_bond"] / tau_end - 1,
          "ms_collar_bond": k["s_bond"] / tau_collar - 1,
          "ms_anchor_bond": k["s_bond"] * k["peel"] / max(tau_anchor, 1.0) - 1}
    out.update({"face_ult_pa": face_u, "edge_ult_pa": edge_u, "tube_ult_pa": tube_u, "root_m_lim_nm": agg["mroot"],
                "brace_comp_design_n": comp_d, "brace_tens_design_n": tens_d, "brace_pcr_n": pcr,
                "brace_len_m": L, "collar_t_lim_nm": agg["t_collar"], "tau_collar_pa": tau_collar,
                "tau_anchor_pa": tau_anchor, "tau_brace_end_pa": tau_end, "dfoot_L4_m": agg["dfoot_L4"], **ms,
                "ms_min": min(ms.values())})
    return out


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
kit.claim("CL-C4-D3-F1-UP", "First station mode, upper quarter (as designed)", calc="CALC-C4-D3-MODES", output="f1_up",
          unit="Hz", parts=TUBES + HALF[:2] + BRACE[:2] + MOUNT[:2], how=TAP)
kit.claim("CL-C4-D3-F1-LO", "First station mode, lower quarter (as designed)", calc="CALC-C4-D3-MODES", output="f1_lo",
          unit="Hz", parts=TUBES + HALF[2:] + BRACE[2:] + MOUNT[2:], how=TAP,
          note="The lower tube is 14 mm longer outside the bore (cambered wing); the lower quarter governs.")
kit.claim("CL-C4-D3-PANEL", "First fin-panel mode (TE tip with the foot), upper quarter", calc="CALC-C4-D3-MODES",
          output="panel_up", unit="Hz", parts=HALF, how="Tap the TE tip with the foot fitted.",
          note="Below the forcing band; < 10 % of its energy reaches the station.")
kit.claim("CL-C4-D3-SEP", "Mode separation from 1P/2P operating points, as designed (nominal)", calc="CALC-C4-D3-MODES",
          output="sep_op", unit="-", limit=(">=", LIMIT_SEP), verifies=R_VIB, parts=TUBES + HALF + BRACE + MOUNT, how=TAP)
kit.claim("CL-C4-D3-SEP-WORST", "Mode separation, as designed, worst tube E/G corner", calc="CALC-C4-D3-WORST",
          output="sep_op_worst", unit="-", limit=(">=", LIMIT_SEP), verifies=R_VIB, parts=TUBES,
          how="T-C4-TUBE-BEND and T-C4-TUBE-TORSION on the bought tube (I1, H1), then T-C4-TAP.")
kit.claim("CL-C4-D3-SEP-WHIRL", "Whirl separation incl. prop gyroscopics, as designed", calc="CALC-C4-D3-CAMPBELL",
          output="sep_whirl", unit="-", limit=(">=", LIMIT_SEP), verifies=R_VIB, parts=TUBES, how=TAP)
kit.claim("CL-C4-D3-SEP-BAND", "Separation from the whole 80-330 Hz band (B4 rule), as designed",
          calc="CALC-C4-D3-MODES", output="sep_band", unit="-", limit=(">=", LIMIT_SEP), parts=TUBES,
          how="Needs every station mode >= 396 Hz; R-VIBRATION (operating points) is the criterion of record (CR-C4-06).")
kit.claim("CL-C4-D3-MOUNT-K-REQ", "Mount rocking stiffness needed for 20 % separation (worst of nominal / low E,G)",
          calc="CALC-C4-D3-MOUNT-K", output="k_req", unit="N m/rad", limit=("<=", "ASM-C4-MOUNT-K-ROCK"),
          verifies=R_VIB, parts=MOUNT,
          how="T-C4-MOUNT-STIFF: 5 N side load at the prop nut on a mount clamped on a tube stub; rotation from two dial "
              "gauges; k = F a / theta.")
kit.claim("CL-C4-D3-MS-FACE", "Fin face margin, as designed, worst case and side", calc="CALC-C4-D3-STATIC",
          output="ms_face", unit="-", limit=(">=", 0.0), verifies=R_SM, parts=HALF,
          how="T-C4-BOARD-COUPON for the face allowable; T-C4-FIN-PROOF at 1.5 x L4.")
kit.claim("CL-C4-D3-MS-EDGE", "Edge-strip margin, as designed", calc="CALC-C4-D3-STATIC", output="ms_edge", unit="-",
          limit=(">=", 0.0), verifies=R_SM, parts=HALF, how="T-C4-FIN-PROOF.")
kit.claim("CL-C4-D3-MS-TUBE", "Motor tube bending margin at the bore end", calc="CALC-C4-D3-STATIC", output="ms_tube",
          unit="-", limit=(">=", 0.0), verifies=R_SM, parts=TUBES, how="T-C4-FIN-PROOF (G2 at the tube end).")
kit.claim("CL-C4-D3-MS-BRACE", "Brace buckling margin (10 x 3 strip, design load incl. fitting factor)",
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
kit.claim("CL-C4-D3-FOOT-DEFL", "Foot deflection under L4 (limit), as designed", calc="CALC-C4-D3-STATIC",
          output="dfoot_L4_m", unit="m", parts=HALF, how="T-C4-FIN-PROOF: dial gauge at the foot.")
kit.claim("CL-C4-D3-BLOCK-MS", "Through-core block minimum margin, D3 geometry", calc="CALC-C4-D3-BLOCK",
          output="ms_min", unit="-", limit=(">=", 0.0), verifies=R_JNT + R_SM, parts=BLOCK,
          how="T-C4-BLOCK-PROOF (30 N m for 1 min on a block in a core offcut).")
kit.claim("CL-C4-D3-SPAR-COUPLE", "Bearing couple on the spar at each block (design), D3 geometry",
          calc="CALC-C4-D3-BLOCK", output="spar_couple_n", unit="N", parts=BLOCK, how="C2 spar crushing check (CR-C4-02).")

kit.test("T-C4-MOUNT-STIFF", "Mount rocking stiffness on the bench", verifies=["CL-C4-D3-MOUNT-K-REQ"],
         procedure="Mount with motor clamped on a 60 mm tube stub held in a vice; 0.5 kg over a pulley at the prop nut, "
                   "sideways (y) and fore-aft (z); dial gauges at the motor can top and at the collar; theta = "
                   "(d_can - d_collar) / spacing; k = F a / theta. Pass: k >= the CL-C4-D3-MOUNT-K-REQ value in both "
                   "directions.")
kit.test("T-C4-TAP-D3", "Tap test, as-built upper and lower quarter",
         verifies=["CL-C4-D3-SEP", "CL-C4-D3-F1-UP", "CL-C4-D3-F1-LO", "CL-C4-D3-SEP-WHIRL", "CL-C4-D3-PANEL"],
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
    variants = {"as designed": {}, "no brace, no strips": {"brace": False, "edge": False},
                "brace, no strips": {"edge": False}, "rigid mount": {"k_rock": None},
                "rigid root": {"k_root": None}, "root 3 000 N m/rad": {"k_root": 3000.0},
                "2 board layers": {"layers": 2}, "half height 0.21 m (CR-B3-14)": {"hh": 0.21}}
    for name, kw in variants.items():
        for side in SIDES:
            r = summary(g, E0, G0, side, rpm, **kw)
            res["configs"][f"{name} / {side}"] = r
            print(f"{name:32s} {side:5s} station {[round(x) for x in r['f_st'][:3]]} {r['kinds'][:1]} "
                  f"panel {r['f_panel']:5.1f}  sep {r['sep_op']:+.2f} ({r['nearest']})  band {r['sep_band']:+.2f}")
    for side in SIDES:
        rows = []
        for E, G in itertools.product((70e9, 100e9, 135e9), (3e9, 5e9, 10e9)):
            r = summary(g, E, G, side, rpm)
            rows.append({"E_GPa": E / 1e9, "G_GPa": G / 1e9, "f_st1": r["f_st1"], "f_st2": r["f_st2"],
                         "sep": r["sep_op"], "nearest": r["nearest"]})
        res["sensitivity"][side] = rows
    rpms = np.linspace(0, 10000, 41)
    curves = {}
    for label, side, colour, dash in (("upper quarter", "upper", "#9AA4B1", None),
                                      ("lower quarter (governs)", "lower", "#1F5FC7", None)):
        mdl = fe.build_q(model_cfg(g, E0, G0, side))
        fr = [(station_whirl(mdl, g["ip"] + g["i_bell"], r) + [np.nan] * 4)[:4] for r in rpms]
        curves[label] = (rpms, np.array(fr, float), colour, dash)
        res.setdefault("campbell", {})[label] = {"rpm": rpms.tolist(), "f_hz": np.array(fr, float).tolist()}
    campbell_svg(HERE / "fig-c4-02-campbell-d3.svg", curves, {"hover": rpm[0], "cruise": rpm[1], "F4 cap": rpm[2]})
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "results_d3.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")
    print("wrote out/results_d3.json and fig-c4-02-campbell-d3.svg")
