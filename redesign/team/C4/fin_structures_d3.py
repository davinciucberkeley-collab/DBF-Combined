"""C4 R4: fin / motor-tube structures on D3's as-designed geometry (CR-D3-10), K09-L, params A1-R3/R4.

R4 (2026-11-09, evening): D5 tip step (straight top edge to the half height at x_te - tip_square, flat step at
tip_step_z to the TE, edge strips end at the step front; foot load through the shoe at the C1 ground point), brace
ear at params fins.stations.collar_end_xyz_m (z 0.1535, was the collar mid height), station collar from
fin_detail.station_collar.height_m (12 mm at R4, 16 mm kept as a sensitivity), friction ASM-C1-FRICTION 0.7 on
CL-C1-FOOT-CORNER (CR-C1-21), level foot at CL-C1-FOOT-MAX, L5 both senses, B4 swirl on the half-fin in flight
(CR-B4-19: misbuilt 1.43 N scaled to T_lim, with H2c), G3 set-down 23.2 N on the lower can (CR-C1-24), section-
torque equilibrium check against C1 (CR-C1-21), both cant senses in the whirl model (D-52), brace edge-rounding
trade (CR-B1-18), fixed ARPACK start vector and a singular-matrix guard (CR-C6-20), part ids FIN-001-UR/UL/LR/LL
(CR-A4-47), T-C4-FIN-PROOF on a test article (CR-H1-17).

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
asm("ASM-C4-G3-CAN-F", "Set-down force on each lower motor can, G3, limit 23.2 N",
    "Ground reaction on a lower motor can when the aircraft is set down flat on the lower cans and lower feet at the "
    "2 g handling factor; acts along the tube axis toward the wing, at the motor body x",
    "team/C1/LOADS.md G3 row and CR-C1-24 (C1 loads.py case G3-BENCH, R_a); C1 has not published it as a claim "
    "(CR-C4-29 asks for CL-C1-G3-CAN-F)", 23.2, "N", status="UNVERIFIED")
asm("ASM-C4-SWIRL-MISBUILT-N", "Swirl side force on a half-fin, misbuilt (wrong cant sense), hover, 1.43 N",
    "B4's wrong-sense case of CL-B4-SWIRL-FIN (0.57 N as built); same centre of pressure",
    "team/B4/CHANGE-REQUESTS.md CR-B4-19 (number given in the request, not a B4 claim)", 1.43, "N",
    status="UNVERIFIED")
asm("ASM-C4-SWIRL-SCALE", "Swirl side force scales with thrust (exponent 1)",
    "F_swirl(T) = F_swirl(T_hover) (T / T_hover)^1, T_hover = m_gate g / 4",
    "fixed prop: thrust and torque both go as n^2, and the swirl momentum flux goes as the torque; C4 choice, "
    "conservative against B4's hover-only number", 1.0, "-", status="PROPOSED")
asm("ASM-C4-SHOE-Z0", "D5 shoe cheeks reach down to |z| 0.196 m",
    "Lowest |z| of the D5 shoe cheeks bonded to both board faces; with fin_detail.fin.tip_clear_x_m (x >= 0.2666) it "
    "bounds the region modelled as one rigid body with the strip ends bonded into the shoe back wall",
    "team/D5/CHANGE-REQUESTS.md CR-D5-11 ('nothing else on x >= 0.2666 m, |z| >= 0.196 m', cheeks 17 x 51 mm, strip "
    "termination bonded into the shoe); subsystems/fins/params.json fin_detail.fin.tip_clear_x_m note", 0.196, "m",
    status="PROPOSED")
asm("ASM-C4-SHOE-Z0-PROP", "Proposed D5 shoe cheeks down to |z| 0.171 m (CR-C4-30)",
    "C4 sizing proposal: the two D5 shoe cheeks (x >= fin_detail.fin.tip_clear_x_m) extended 25 mm toward the wing, bonded to both board faces, so the foot side load enters the board below the strip ends",
    "C4 R4 sweep (out/results_d3.json shoe_sweep, mesh 36 x 30): |z| 0.196 (as drawn) MS -0.5, 0.176 about 0, 0.171 positive with the LE root governing; a D5 printed part, D5 confirms fit and mass", 0.171, "m", status="PROPOSED")
asm("ASM-C4-ASA-BEARING", "ASA printed bearing allowable 30 MPa",
    "Compressive bearing allowable of the printed ASA lip cap on the tube end",
    "ASA filament TDS compressive strength 50-60 MPa x 0.5 for layer lines and voids; G3 coupon not planned "
    "(margin is large)", 30e6, "Pa")
asm("ASM-C4-TAPE-AREAL", "Fairing tape areal mass 0.06 kg/m2",
    "Clear polyester packing tape (50 um film + adhesive) wrapped over the brace strip as an aero fairing",
    "typical 2 mil packing tape 55-65 g/m2; weigh 1 m before use", 0.06, "kg/m2")

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
        "k_twist": "ASM-C4-MOUNT-K-TWIST", "k_root": "ASM-C4-ROOT-K", "k_anchor": "ASM-C4-ANCHOR-K",
        "tip_sq": P + "fin_detail.fin.tip_square_m", "z_step": P + "fin_detail.fin.tip_step_z_m",
        "ear_xyz": P + "fins.stations.collar_end_xyz_m", "shoe_x0": P + "fin_detail.fin.tip_clear_x_m",
        "shoe_z0": "ASM-C4-SHOE-Z0"}
GU = {"tube_x": "m", "y_fin": "m", "od": "m", "idd": "m", "mu": "kg/m", "tube_len": "m", "z_st": "m", "x_face": "m",
      "x_prop": "m", "x_te": "m", "hh": "m", "le_gap": "m", "grip": "m", "sc_gap": "m", "sc_h": "m", "sc_wall": "m",
      "ear_len": "m", "bond_gap": "m", "skin": "m", "bore_z": "m", "m_motor": "kg", "d_motor": "m", "l_motor": "m",
      "m_prop": "kg", "m_adapt": "kg", "ip": "kg m2", "i_bell": "kg m2", "mount": "kg, m", "cb_mass": "kg",
      "m_esc": "kg", "esc_x0": "m", "esc_len": "m", "esc_z": "m", "landing_g": "g", "cant": "deg", "t_board": "m", "areal": "kg/m2",
      "layers": "-", "t_face": "m", "e_face": "Pa", "e_core": "Pa", "g_core": "Pa", "x_spar": "m", "y_anchor": "m",
      "proud": "m", "b_w": "m", "b_t": "m", "e_strip": "Pa", "e_w": "m", "e_t": "m", "rho_cf": "kg/m3", "chord": "m",
      "el_frac": "-", "slot_hw": "m", "k_rock": "N m/rad", "k_twist": "N m/rad", "k_root": "N m/rad",
      "k_anchor": "N/m", "tip_sq": "m", "z_step": "m", "ear_xyz": "m", "shoe_x0": "m", "shoe_z0": "m"}
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
    ex, ey, ez = g["ear_xyz"]                                                    # brace end on the ear (params, A5)
    ear_dy = -(g["y_fin"] - ey)                                                  # inboard of the tube axis
    z_anchor = float(np.interp(g["x_spar"], sk[:, 0], zs)) + g["proud"] / 2
    anchor = (g["x_spar"], -(g["y_fin"] - g["y_anchor"]), z_anchor)
    x_le = g["tube_x"] + g["od"] / 2 + g["le_gap"]
    x_hinge = g["chord"] * (1 - g["el_frac"])
    return {"root": [(float(x), float(z)) for x, z in zip(sk[:, 0], zs)], "z_clamp": z_clamp, "z_end": z_end,
            "z_sc": z_sc, "z_ear": abs(ez), "z_top_le": z_top_le, "ear": (ex - g["tube_x"], ear_dy, 0.0),
            "anchor": anchor, "x_le": x_le, "x_step": g["x_te"] - g["tip_sq"],
            "root_free": [(x_hinge - g["slot_hw"], x_hinge + g["slot_hw"])] if side == "lower" else []}


def fin_top(g, geo, nx, hh=None):
    """D5 tip (R4): straight from the collar top at the LE to the half height at the step front, then the flat step
    (tip_step_z) to the TE. Returns the top-edge points, the step height and nx + 1 mesh columns with one column on
    the step front (the element after it carries the 9.5 mm step as a chamfer one element wide)."""
    h = g["hh"] if hh is None else hh
    zs = h - (g["hh"] - g["z_step"])                                             # same step depth if hh is varied
    xs, xl, xt = geo["x_step"], geo["x_le"], g["x_te"]
    pts = [(xl, geo["z_top_le"]), (xs, h), (xs + 1e-6, zs), (xt, zs)]
    n2 = max(1, round(nx * (xt - xs) / (xt - xl)))
    cols = list(np.linspace(xl, xs, nx - n2 + 1)) + list(np.linspace(xs, xt, n2 + 1)[1:])
    return pts, zs, cols


def model_cfg(g, E, G, side, mesh=MESH, brace=True, edge=True, k_rock="nom", k_root="nom", hh=None, layers=None,
              le_cracked=False, shoe="nom"):
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
    top, z_stp, cols = fin_top(g, geo, mesh[0], hh)
    cfg = {"tube": {"x": g["tube_x"], "E": E, "G": G, "od": g["od"], "id": g["idd"], "rho": g["mu"] / A,
                    "z_clamp": geo["z_clamp"], "z_end": geo["z_end"]},
           "n_free": 2, "n_ext": 2, "k_root": g["k_root"] if k_root == "nom" else k_root,
           "fin": {"props": pr, "x_le": geo["x_le"], "x_te": g["x_te"], "root": geo["root"],
                   "z_top_le": geo["z_top_le"], "z_top_te": z_stp, "top_pts": top, "x_cols": cols,
                   "root_free": geo["root_free"],
                   "le_bonds": [(geo["z_top_le"] - g["sc_h"], geo["z_top_le"])] if le_cracked else None},
           "nx": mesh[0], "nz": mesh[1],
           "station": {"parts": parts, "k_rock": kr, "k_twist": None if kr is None else g["k_twist"]},
           "tube_masses": [(m_col + (m_br / 2 if brace else 0.0), geo["z_sc"])],
           "fin_masses": [(g["m_esc"], (g["esc_x0"] + g["esc_len"] / 2, g["esc_z"])),
                          (g["landing_g"] / 4 / 1000.0, (g["x_te"] - g["tip_sq"] / 2, z_stp))],   # foot on the shoe
           "struts": [], "stiffeners": [], "x_step": geo["x_step"],
           "rigid_fin": [] if shoe is None else [(g["shoe_x0"], g["shoe_z0"]) if shoe == "nom" else shoe]}
    if brace:
        cfg["struts"] = [{"z_attach": geo["z_ear"], "ear": geo["ear"], "anchor": geo["anchor"],
                          "EA": g["e_strip"] * g["b_w"] * g["b_t"], "k_anchor": g["k_anchor"]}]
    if edge and pr is not None:
        d = lay * g["t_board"] + g["e_t"]
        cfg["stiffeners"] = [{"E": g["e_strip"], "G": 5e9, "A": 2 * g["e_w"] * g["e_t"],
                              "I_out": g["e_w"] * g["e_t"] * d * d / 2, "J": 2 * g["e_w"] * g["e_t"] ** 3 / 3,
                              "rho": g["rho_cf"], "d": d, "x_end": geo["x_step"]}]
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


def spin_axis(g, sense=1):
    """Prop spin axis in the quarter frame with the tangential cant (thrust along -x, tilted toward +/- the tangent;
    D-52 set cant_sense_UR = -1, the whirl check runs both senses)."""
    ty, tz = tangent(g)
    c = math.radians(g["cant"])
    return (-math.cos(c), sense * math.sin(c) * ty, sense * math.sin(c) * tz)


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
                   "s sin c t_y, s sin c t_z) with the tangential cant c and both senses s = +/-1; sep over 1P/2P "
                   "at hover and cruise and 1P at the cap, station whirl modes only; f_whirl_* = whirl frequencies "
                   "of the first station mode at hover and cruise rpm (lowest over sides and senses)",
          assumes=["ASM-C4-PROP-IP", "ASM-C1-BELL-INERTIA"])
def campbell_d3(**k):
    g = {n: k[n] for n in GEOM}
    worst, fw = 9.0, {"hover": 1e9, "cruise": 1e9}
    for side in SIDES:
        mdl = fe.build_q(model_cfg(g, k["E"], k["G"], side, layers=k["lay_rec"]))
        for sense in (1, -1):
            for name, rpm in (("hover", k["rpm_h"]), ("cruise", k["rpm_c"]), ("max", k["rpm_x"])):
                fs = station_whirl(mdl, g["ip"] + g["i_bell"], rpm, axis=spin_axis(g, sense))
                if name in fw and fs:
                    fw[name] = min(fw[name], fs[0])
                for f in fs:
                    for p in ((1,) if name == "max" else (1, 2)):
                        worst = min(worst, abs(f / (p * rpm / 60) - 1))
    return {"sep_whirl": worst, "f_whirl_hover_hz": fw["hover"], "f_whirl_cruise_hz": fw["cruise"],
            "f_2p_hover_hz": k["rpm_h"] / 30, "f_2p_cruise_hz": k["rpm_c"] / 30}


STAT_IN = {"f_level": "CL-C1-FOOT-MAX", "f_corner": "CL-C1-FOOT-CORNER", "mu_hi": "ASM-C1-FRICTION",
           "foot_h": P + "cg.foot_height_m", "z_pad": P + "landing.pad_contact_z_m",
           "sw_f": "CL-B4-SWIRL-FIN", "sw_m": "CL-B4-SWIRL-FIN-M", "sw_bad": "ASM-C4-SWIRL-MISBUILT-N",
           "sw_exp": "ASM-C4-SWIRL-SCALE", "g3": "ASM-C4-G3-CAN-F", "t_c1": "CL-C1-FINHALF-T-WINGPLANE-LIM",
           "side_c5": "CL-C5-FOOT-SIDE-LOAD",
           "n_h": "ASM-C1-HANDLING-N", "m_gate": P + "requirements.mtow_gate_kg", "grav": P + "env.g_ms2",
           "t_lim": "CL-C1-T-LIMIT", "q_mot": "CL-C1-MOTOR-TORQUE", "sf": SF, "fit": FIT, "prt": PRT,
           "s_face": "ASM-C4-FACE-SIGMA", "s_cf": "ASM-C4-CF-SIGMA", "patch": "ASM-C4-FOOT-PATCH",
           "s_bond": "ASM-C4-BOND-SHEAR", "peel": "ASM-C4-PEEL-KD", "engage": P + "fin_detail.brace.engage_m",
           "a_lx": P + "fin_detail.anchor.len_x_m", "a_ly": P + "fin_detail.anchor.len_y_m",
           "d_spar": P + "wing.spar.od_m", "ear_w": P + "fin_detail.station_collar.ear_w_m",
           "s_ten": "ASM-C4-PETG-TENSILE", "kd_foam": "ASM-C6-FOAM-KD", "tau_board": "ASM-D5-BOND-TAU",
           "pin_pitch": P + "fin_detail.edge_strip.pin_pitch_m"}
STAT_U = {"f_level": "N", "f_corner": "N", "mu_hi": "-", "side_c5": "N", "foot_h": "m", "z_pad": "m", "sw_f": "N",
          "sw_m": "N*m", "sw_bad": "N", "sw_exp": "-", "g3": "N", "t_c1": "N m", "n_h": "-", "m_gate": "kg", "grav": "m/s2",
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


def shoe_loads(nodes, shoe, F, P_app):
    """Rigid-shoe distribution of a force F applied at P_app onto the shoe nodes: equal shares of F plus nodal forces
    that carry the moment about the shoe centroid (out-of-plane Mx, Mz as y forces linear in (dx, dz); in-plane My
    as an in-plane couple). Exact resultant and moment."""
    xyz = np.array([nodes[n] for n in shoe])
    C = xyz.mean(axis=0)
    M = np.cross(np.asarray(P_app) - C, F)
    dx, dz = xyz[:, 0] - C[0], xyz[:, 2] - C[2]
    A = np.array([[np.sum(dx * dx), np.sum(dx * dz)], [np.sum(dx * dz), np.sum(dz * dz)]])
    c1, c2 = np.linalg.solve(A, [M[2], -M[0]])                                   # sum dx fy = Mz, -sum dz fy = Mx
    s2 = np.sum(dx * dx + dz * dz)
    out = []
    for i, n in enumerate(shoe):
        fy = c1 * dx[i] + c2 * dz[i]
        fx_m, fz_m = M[1] * dz[i] / s2, -M[1] * dx[i] / s2                       # in-plane couple for My
        out.append((n, (F[0] / len(shoe) + fx_m, F[1] / len(shoe) + fy, F[2] / len(shoe) + fz_m, 0, 0, 0)))
    return out


def section_torque(mdl, u, loads, g):
    """Torque about the tube axis carried across the wing plane, from the FE reactions (CR-C1-21 check): constrained
    fin-root and boss nodes, the tube root spring and the brace anchor. Returns (total, tube, fin root, brace) with the
    sign of the applied torque."""
    R = fe.reactions(mdl, u, loads)
    fixed = np.asarray(mdl.T.getnnz(axis=1) == 0)
    nodes, xt = mdl.nodes, g["tube_x"]
    t_fin = 0.0
    for n in mdl.fin_id.values():
        o = fe.NDOF * n
        if fixed[o + 1]:
            t_fin += (nodes[n][0] - xt) * R[o + 1]
        if fixed[o + 0]:
            t_fin -= nodes[n][1] * R[o]
        if fixed[o + 5]:
            t_fin += R[o + 5]
    t_tube = 0.0
    if fixed[5]:
        t_tube += R[5]
    elif mdl.cfg.get("k_root") is not None:
        t_tube += -1e9 * u[5]                                                    # rz spring at the clamp (build_q)
    t_br = 0.0
    for s in mdl.strut_info:
        us = u[fe.NDOF * s["node"]:fe.NDOF * s["node"] + 3]
        Fr = -s["k"] * float(np.dot(s["n"], us)) * s["n"]                        # anchor spring on the structure
        p = nodes[s["node"]]
        t_br += (p[0] - xt) * Fr[1] - p[1] * Fr[0]
    tot = t_fin + t_tube + t_br
    return -tot, -t_tube, -t_fin, -t_br


def applied_torque(mdl, loads, g):
    """Torque of the applied loads about the tube axis (for the equilibrium residual)."""
    t = 0.0
    for n, f in loads:
        p = mdl.nodes[n]
        t += (p[0] - g["tube_x"]) * f[1] - p[1] * f[0] + f[5]
    return t


def fin_static(g, k, side, le_cracked=False, mesh=MESH):
    """One quarter, every limit case. Returns per-case results and the brace length."""
    mdl = fe.build_q(model_cfg(g, k["E"], k["G"], side, mesh=mesh, layers=k["lay_rec"], le_cracked=le_cracked))
    pr = mdl.cfg["fin"]["props"]
    nodes = mdl.nodes
    geo = geometry(g, side)
    nz = mdl.cfg["nz"]
    # D5 shoe: every fin node on the square tip (x >= step front) within the foot patch below the top edge
    shoe = [n for (i, j), n in mdl.fin_id.items() if nodes[n][0] >= geo["x_step"] - 1e-9
            and nodes[n][2] >= nodes[mdl.fin_id[(i, nz)]][2] - k["patch"] - 1e-9]
    foot = shoe
    P_pad = np.array([g["x_te"] + k["foot_h"], 0.0, k["z_pad"]])                 # C1 ground point (CALC-C1-LANDING)
    fc = k["f_corner"]
    fs = max(k["mu_hi"] * fc, k["side_c5"])                                     # foot side load at the pad friction
    G2 = k["n_h"] * k["m_gate"] * k["grav"]
    T, Q, c = k["t_lim"], k["q_mot"], math.radians(g["cant"])
    ty, tz = tangent(g)
    r = np.array([g["x_prop"] - g["tube_x"], 0.0, g["z_st"] - geo["z_end"]])    # prop centre from the station node
    cases = {"L1": shoe_loads(nodes, shoe, np.array([-k["f_level"], 0, 0]), P_pad),
             "L4+": shoe_loads(nodes, shoe, np.array([-fc, fs, 0]), P_pad),
             "L4-": shoe_loads(nodes, shoe, np.array([-fc, -fs, 0]), P_pad),
             "L5+": shoe_loads(nodes, shoe, np.array([-fc, 0, fs]), P_pad),
             "L5-": shoe_loads(nodes, shoe, np.array([-fc, 0, -fs]), P_pad),
             "G2+": [(mdl.i_end, (0, G2, 0, 0, 0, 0))],
             "G2-": [(mdl.i_end, (0, -G2, 0, 0, 0, 0))]}
    # B4 swirl (CR-B4-19): misbuilt side force scaled from hover to T_lim, line load on the row nearest the B4 centre
    # of pressure (CL-B4-SWIRL-FIN-M / CL-B4-SWIRL-FIN above the skin) over every column, same sense on the half-fin
    h_cp = k["sw_m"] / k["sw_f"]
    t_hov = k["m_gate"] * k["grav"] / 4
    f_sw = k["sw_bad"] * (T / t_hov) ** k["sw_exp"]
    nx = mdl.cfg["nx"]
    row = []
    for i in range(nx + 1):
        zr = nodes[mdl.fin_id[(i, 0)]][2]
        row.append(min((mdl.fin_id[(i, j)] for j in range(nz + 1)),
                       key=lambda n: abs(nodes[n][2] - (zr + h_cp))))
    for s_c, s_q in itertools.product((1, -1), (1, -1)):                        # H2 with the 7 deg cant, both prints
        F = np.array([-T * math.cos(c), s_c * T * math.sin(c) * ty, s_c * T * math.sin(c) * tz])
        M = np.cross(r, F) + s_q * Q * F / np.linalg.norm(F)
        tag = f"{'+' if s_c > 0 else '-'}{'+' if s_q > 0 else '-'}"
        cases[f"H2c{tag}"] = [(mdl.i_station, (*F, *M))]
        for s_w in (1, -1):
            cases[f"H2s{tag}{'+' if s_w > 0 else '-'}"] = [(mdl.i_station, (*F, *M))] + \
                [(n, (0, s_w * f_sw / len(row), 0, 0, 0, 0)) for n in row]
    if side == "lower":                                                         # G3 set-down on the lower can (CR-C1-24)
        x_m = g["x_face"] - g["l_motor"] / 2
        rg = np.array([x_m - g["tube_x"], 0.0, g["z_st"] - geo["z_end"]])
        Fg = np.array([0.0, 0.0, -k["g3"]])                                      # toward the wing
        cases["G3"] = [(mdl.i_station, (*Fg, *np.cross(rg, Fg)))]
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
            if top_row[i] in foot or nodes[top_row[i]][0] >= g["shoe_x0"] - 1e-9:
                continue                                    # strip end inside the D5 shoe: bonded into the shoe walls
            q = abs(Ns[i] - Ns[i - 1]) / 2 / ((Ls[i] + Ls[i - 1]) / 2) + max(Vs[i], Vs[i - 1]) / d
            q_face = max(q_face, q)
        t_sec, t_tu, t_fi, t_bra = section_torque(mdl, u, loads, g)
        res[cname] = {"face": smax, "edge": s_edge, "tube": m_root * g["od"] / 2 / mdl.I_t, "mroot": m_root,
                      "brace": f_br, "t_collar": t_collar, "t_root": abs(tt[0]), "q_face": q_face,
                      "strip_end": abs(Ns[0]) / 2 + M0 / d,
                      "dfoot": max(float(np.linalg.norm(u[6 * n:6 * n + 3])) for n in foot),
                      "t_sec": t_sec, "t_sec_tube": t_tu, "t_sec_fin": t_fi, "t_sec_brace": t_bra,
                      "t_app": applied_torque(mdl, loads, g), "f_swirl": f_sw, "h_cp": h_cp}
    return res, s["L"]


@kit.calc("CALC-C4-D3-STATIC", title="Fin, tube, brace, collar, edge-strip bond and anchor strength, recommended "
          "design (both sides, LE fillet intact and cracked)",
          inputs={**GEOM, **TUBE, **STAT_IN, **REC}, units={**GU, **TU, **STAT_U, **REC_U}, tol=1e-4,
          equation="FE static, limit cases L1 (C1 peak foot), L4 (side = max(mu F_corner, C5 side load), both senses), "
                   "L5 (both senses), foot loads at the C1 ground point (x_te + foot_h, z_pad) through a rigid D5 shoe "
                   "on the square tip; G2 (both "
                   "senses, n_h m g at the tube end), H2c (T_lim along the 7 deg canted shaft at the prop centre + Q "
                   "about the shaft, 4 sign combinations), H2s = H2c + B4 misbuilt swirl x (T_lim/T_hover)^exp as a "
                   "line load at the B4 centre of pressure, both senses; G3 (lower quarter) set-down force at the "
                   "motor body toward the wing; envelope over upper/lower quarter and LE fillet intact / "
                   "cracked between the boss and the collar; section torque at the wing plane from the FE reactions "
                   "(fin root + boss nodes, tube root spring, brace anchor) vs C1's wing-plane torque, equilibrium "
                   "residual vs the applied torque; ultimate = sf x limit (joints x fit x prt); face MS = min(intact at "
                   "ultimate, LE fillet cracked at limit (fail-safe)), face stress = Q_f "
                   "(eps0 + z kappa); collar torque = jump of the tube torque across the collar band; strip-to-paper "
                   "shear flow per face q = |dN|/2/ds + |V|/d (nodes inside the D5 shoe, x >= tip_clear_x, excluded), tau = q/w vs kd tau_board; "
                   "strip end force per face = |N0|/2 + |M0|/d; pin force = q jf pitch; brace Pcr = pi^2 E w t^3 / (12 L^2); brace-end bond "
                   "tau = F / (2 (w + t) engage); ear root s = 6 F (ear/2) / (w_ear h^2) + F / (w_ear h); collar bond "
                   "tau = T / (2 pi r^2 h) + F / (pi d h), h_req at MS 0; anchor tau = F / (len_y pi d_spar / 4) vs "
                   "peel x bond allowable",
          assumes=["ASM-C4-FACE-SIGMA", "ASM-C4-BOND-SHEAR", "ASM-C4-PEEL-KD", "ASM-C4-FOOT-PATCH",
                   "ASM-C4-SWIRL-MISBUILT-N", "ASM-C4-SWIRL-SCALE", "ASM-C4-G3-CAN-F"],
          cites=["SRC-C4-ALLEN", "SRC-C4-ROARK"])
def static_d3(**k):
    g = {n: k[n] for n in GEOM}
    jf = k["sf"] * k["fit"] * k["prt"]
    out = {}
    agg = {"face": 0.0, "edge": 0.0, "tube": 0.0, "comp": 0.0, "tens": 0.0, "t_collar": 0.0, "f_collar": 0.0,
           "dfoot_L4": 0.0, "mroot": 0.0, "t_root": 0.0, "q_face": 0.0, "strip_end": 0.0, "t_collar_intact": 0.0,
           "q_face_intact": 0.0, "face_intact": 0.0, "face_cracked": 0.0, "eq_resid": 0.0, "t_sec_L4": 0.0, "brace_g3": 0.0,
           "tube_g3": 0.0, "face_sw": 0.0, "brace_sw": 0.0, "t_collar_sw": 0.0}
    gov = {}
    for side, cr in itertools.product(SIDES, (False, True)):
        res, L = fin_static(g, k, side, le_cracked=cr, mesh=k.get("_mesh", MESH))
        tag = side[:2] + ("_cr" if cr else "")
        out[f"brace_len_{side[:2]}_m"] = L
        for c, r in res.items():
            for key in ("face", "edge", "tube", "mroot", "t_collar", "t_root", "q_face", "strip_end"):
                if r[key] > agg[key]:
                    gov[key] = f"{c} {tag}"
                agg[key] = max(agg[key], r[key])
            agg["eq_resid"] = max(agg["eq_resid"], abs(r["t_sec"] - r["t_app"]) / max(abs(r["t_app"]), 1e-3))
            if c.startswith("L4") and abs(r["t_sec"]) > agg["t_sec_L4"]:
                agg["t_sec_L4"] = abs(r["t_sec"])
                out.update({"t_sec_L4_tube_nm": abs(r["t_sec_tube"]), "t_sec_L4_fin_nm": abs(r["t_sec_fin"]),
                            "t_sec_L4_brace_nm": abs(r["t_sec_brace"]), "t_sec_L4_case": f"{c} {tag}"})
            if c == "G3":
                agg["brace_g3"] = max(agg["brace_g3"], abs(r["brace"]))
                agg["tube_g3"] = max(agg["tube_g3"], r["tube"])
            if c.startswith("H2s"):
                agg["face_sw"] = max(agg["face_sw"], r["face"])
                agg["brace_sw"] = max(agg["brace_sw"], abs(r["brace"]))
                agg["t_collar_sw"] = max(agg["t_collar_sw"], r["t_collar"])
                out["swirl_force_lim_n"], out["swirl_cp_m"] = r["f_swirl"], r["h_cp"]
            if not cr:
                agg["t_collar_intact"] = max(agg["t_collar_intact"], r["t_collar"])
                agg["q_face_intact"] = max(agg["q_face_intact"], r["q_face"])
                agg["face_intact"] = max(agg["face_intact"], r["face"])
            else:
                agg["face_cracked"] = max(agg["face_cracked"], r["face"])
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
    # face criterion (R4): intact at ultimate; LE fillet cracked = fail-safe case at limit (its peak sits at the end
    # of the bonded LE band, a corner that does not converge with mesh; T-C4-FIN-PROOF builds that quarter)
    ms_face_int = k["s_face"] / (agg["face_intact"] * k["sf"]) - 1
    ms_face_fs = k["s_face"] / agg["face_cracked"] - 1
    ms = {"ms_face": min(ms_face_int, ms_face_fs), "ms_edge": k["s_cf"] / edge_u - 1, "ms_tube": k["s_cf"] / tube_u - 1,
          "ms_brace_buckling": pcr / max(comp_d, 1e-9) - 1, "ms_brace_end_bond": k["s_bond"] / tau_end - 1,
          "ms_collar_bond": k["s_bond"] / tau_collar - 1,
          "ms_anchor_bond": k["s_bond"] * k["peel"] / max(tau_anchor, 1.0) - 1,
          "ms_ear_root": k["s_ten"] / s_ear - 1}
    ms_strip = k["kd_foam"] * k["tau_board"] / tau_strip - 1
    out.update({"face_ult_pa": face_u, "face_ult_intact_pa": agg["face_intact"] * k["sf"],
                "face_lim_cracked_pa": agg["face_cracked"], "ms_face_intact_ult": ms_face_int,
                "ms_face_failsafe_lim": ms_face_fs, "ms_face_envelope_ult": k["s_face"] / face_u - 1, "edge_ult_pa": edge_u,
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
                "dfoot_L4_m": agg["dfoot_L4"], **ms, "ms_min": min(ms.values()),
                "eq_resid": agg["eq_resid"], "t_sec_L4_lim_nm": agg["t_sec_L4"],
                "t_sec_vs_c1": abs(agg["t_sec_L4"] / k["t_c1"] - 1),
                "brace_g3_lim_n": agg["brace_g3"], "tube_g3_ult_pa": agg["tube_g3"] * k["sf"],
                "face_swirl_ult_pa": agg["face_sw"] * k["sf"], "brace_swirl_lim_n": agg["brace_sw"],
                "collar_t_swirl_lim_nm": agg["t_collar_sw"],
                "collar_bond_per_h_npm": per_h,
                "ms_collar_bond_16mm": k["s_bond"] / (per_h / 0.016) - 1,
                "governing": "; ".join(f"{a}: {b}" for a, b in sorted(gov.items()))})
    return out


@kit.calc("CALC-C4-D3-BRACE-TRADE", title="Brace strip 10 x 2 against 10 x 3 (CR-C4-16), recommended design",
          inputs={**GEOM, **TUBE, **RPM, **REC, "t3": "ASM-C4-BRACE-T-3", "t2": "ASM-C4-BRACE-T-2",
                  "n_h": "ASM-C1-HANDLING-N", "tape": "ASM-C4-TAPE-AREAL",
                  "m_gate": P + "requirements.mtow_gate_kg", "grav": P + "env.g_ms2", "sf": SF, "fit": FIT},
          units={**GU, **TU, **RU, **REC_U, "t3": "m", "t2": "m", "n_h": "-", "m_gate": "kg", "grav": "m/s2", "sf": "-",
                 "fit": "-", "tape": "kg/m2"}, tol=1e-4,
          equation="for t in (10 x 3, 10 x 2): sep_op (both quarters, nominal E/G); G2 brace force from the FE (limit, both "
                   "quarters) x sf x fit vs Pcr = pi^2 E w t^3 / (12 L^2); mass of four braces = 4 rho w t L_mean; "
                   "CR-B1-18 edge rounding of the 10 x 2 (both 2 mm edges full round, r = t/2): A and I_weak lose "
                   "2 (2 r^2 - pi r^2 / 2) and 2 (r (2r)^3 / 12 - pi r^4 / 8), Pcr scales with I; tape fairing = "
                   "4 x areal x perimeter (2 w + pi t) x 1.5 overlap x L_mean")
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
    # CR-B1-18: 10 x 2 strip with both 2 mm edges sanded to a full round (r = t/2) vs a tape fairing
    w, t, rr = g0["b_w"], k["t2"], k["t2"] / 2
    a_loss = 2 * (2 * rr * rr - math.pi * rr * rr / 2)                     # two ends: rectangle r x 2r minus half disc
    i_loss = 2 * (rr * (2 * rr) ** 3 / 12 - math.pi * rr ** 4 / 8)          # about the weak axis (mid-thickness)
    a_frac, i_frac = 1 - a_loss / (w * t), 1 - i_loss / (w * t ** 3 / 12)
    out.update({"round_area_frac": a_frac, "round_i_frac": i_frac,
                "ms_buckle_t2_round": out["pcr_t2_n"] * i_frac / out["f_design_t2_n"] - 1,
                "tape_mass4_g": 4 * k["tape"] * (2 * w + math.pi * t) * 1.5 * sum(Ls) / len(Ls) * 1000})
    return out


SHOE_MESH = (36, 30)


@kit.calc("CALC-C4-D3-SHOE", title="Fin face with the D5 shoe cheeks extended (CR-C4-30), recommended design",
          inputs={**GEOM, **TUBE, **STAT_IN, **REC, "z0_prop": "ASM-C4-SHOE-Z0-PROP"},
          units={**GU, **TU, **STAT_U, **REC_U, "z0_prop": "m"}, tol=1e-4,
          equation="CALC-C4-D3-STATIC envelope re-run on a 36 x 30 fin mesh with the rigid D5 shoe region x >= "
                   "tip_clear_x, |z| >= z0_prop instead of ASM-C4-SHOE-Z0; reports the face, strip and collar "
                   "margins and the face stress with the cheeks as drawn on the same mesh",
          assumes=["ASM-C4-SHOE-Z0-PROP", "ASM-C4-FACE-SIGMA"])
def shoe_d3(**k):
    base = {n: v for n, v in k.items() if n != "z0_prop"}
    r_p = static_d3(**{**base, "shoe_z0": k["z0_prop"], "_mesh": SHOE_MESH})
    r_d = static_d3(**{**base, "_mesh": SHOE_MESH})
    return {"ms_face_prop": r_p["ms_face"], "face_ult_prop_pa": r_p["face_ult_pa"],
            "ms_face_intact_prop": r_p["ms_face_intact_ult"], "ms_face_failsafe_prop": r_p["ms_face_failsafe_lim"],
            "ms_face_envelope_prop": r_p["ms_face_envelope_ult"],
            "ms_face_drawn_fine": r_d["ms_face"], "face_ult_drawn_fine_pa": r_d["face_ult_pa"],
            "ms_min_prop": r_p["ms_min"], "ms_strip_paper_prop": r_p["ms_strip_paper"],
            "collar_t_lim_prop_nm": r_p["collar_t_lim_nm"], "dfoot_L4_prop_m": r_p["dfoot_L4_m"],
            "governing_prop": r_p["governing"], "cheek_extension_m": k["shoe_z0"] - k["z0_prop"]}


@kit.calc("CALC-C4-D3-MOUNT-CANT", title="Motor mount on the tube end with the 7 deg tangential cant",
          inputs={"T": "CL-C1-T-LIMIT", "Q": "CL-C1-MOTOR-TORQUE", "cant": P + "propulsion.stations.cant_deg",
                  "y_fin": P + "fins.y_m", "z_st": P + "propulsion.stations.z_m", "x_prop": "CL-D3-X-PROP",
                  "tube_x": P + "fins.tube.x_m", "tube_len": P + "fin_detail.tube_length_m", "od": P + "fins.tube.od_m",
                  "slip": P + "fin_detail.mount.slip_torque_nm", "m_c1": "CL-C1-MOUNT-M-ULT",
                  "f_c1": "CL-C1-MOUNT-F-ULT", "sf": SF, "fit": FIT, "prt": PRT, "g3": "ASM-C4-G3-CAN-F",
                  "x_face": "CL-D3-X-FACE", "l_motor": P + "propulsion.motor_length_m", "idd": P + "fins.tube.id_m",
                  "s_brg": "ASM-C4-ASA-BEARING"},
          units={"T": "N", "Q": "N m", "cant": "deg", "y_fin": "m", "z_st": "m", "x_prop": "m", "tube_x": "m",
                 "tube_len": "m", "od": "m", "slip": "N m", "m_c1": "N m", "f_c1": "N", "sf": "-", "fit": "-",
                 "prt": "-", "g3": "N", "x_face": "m", "l_motor": "m", "idd": "m", "s_brg": "Pa"}, tol=1e-6,
          equation="t = (-z_st, y_fin)/|.| (motor-circle tangent); F = T (-cos c, sin c t_y, sin c t_z) at r = (x_prop - "
                   "x_tube, 0, z_st - L_tube/2) from the tube end; side = T sin c; axial = T sin c |t_z|; twist "
                   "about the tube = |r_x| T sin c |t_y| + Q sin c |t_z|; rocking = |r x F| in x-y (worst sign) + Q cos c; design "
                   "= limit x sf x fit x prt; slip-clamp use = sqrt((F_ax,d / (T_slip / r))^2 + ((M_tw,d + M_C1,ult "
                   "fit prt) / T_slip)^2) (C1's mount moment taken wholly about the tube: conservative); G3 set-down "
                   "(CR-C1-24): axial push F_g3 on the lip cap, bearing on the tube-wall annulus s = F_g3 jf / (pi/4 "
                   "(od^2 - id^2)); rocking F_g3 |x_motor - x_tube|, x_motor = x_face - l_motor/2; rocking envelope = "
                   "max(H2c, G3)")
def mount_cant(T, Q, cant, y_fin, z_st, x_prop, tube_x, tube_len, od, slip, m_c1, f_c1, sf, fit, prt, g3, x_face,
               l_motor, idd, s_brg):
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
    rock_g3 = g3 * abs(x_face - l_motor / 2 - tube_x)
    s_cap = g3 * jf / (math.pi / 4 * (od ** 2 - idd ** 2))
    return {"side_frac": math.sin(c), "side_lim_n": side, "axial_lim_n": ax, "lateral_lim_n": lat,
            "twist_lim_nm": tw, "rock_lim_nm": rock, "axial_design_n": ax * jf, "twist_design_nm": tw * jf,
            "rock_design_nm": rock * jf, "shear_design_n": math.hypot(T * math.cos(c), lat) * jf,
            "c1_force_ratio": T * jf / max(f_c1 * fit * prt, 1e-9), "slip_use": use, "ms_slip_hold": 1 / use - 1,
            "rock_g3_lim_nm": rock_g3, "rock_g3_design_nm": rock_g3 * jf, "g3_design_n": g3 * jf,
            "rock_env_design_nm": max(rock, rock_g3) * jf, "cap_bearing_g3_pa": s_cap,
            "ms_cap_bearing_g3": s_brg / s_cap - 1}


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
HALF = ["FIN-001-UR", "FIN-001-UL", "FIN-001-LR", "FIN-001-LL"]                   # CR-A4-47 (was RU/LU/RD/LD)
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
kit.claim("CL-C4-D3-MS-FACE", "Fin face margin as drawn (D5 cheeks to |z| 0.196): min(intact at ultimate, LE fillet "
          "cracked at limit), both quarters", calc="CALC-C4-D3-STATIC",
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
          note="Published for C6 (CR-C6-03, CR-C1-21): C6 reads this claim instead of ASM-C6-C4-COLLAR-T (9.3 N m, not "
               "a C4 output) and sizes the collar to the larger of it and C1's section torque, plus CL-C4-D3-BRACE-F "
               "as shear.")
kit.claim("CL-C4-D3-COLLAR-T-INTACT", "Station-collar torsion, limit, LE fillet intact", calc="CALC-C4-D3-STATIC",
          output="collar_t_lim_intact_nm", unit="N m", parts=COLLAR, how="As CL-C4-D3-COLLAR-T.")
kit.claim("CL-C4-D3-COLLAR-H-REQ", "Station-collar height needed for MS 0 on the envelope torsion + brace shear",
          calc="CALC-C4-D3-STATIC", output="collar_h_req_m", unit="m", limit=("<=", COLLAR_H), verifies=R_JNT,
          parts=COLLAR, how="C6 lap-shear coupon on scuffed CF; T-C4-FIN-PROOF.")
kit.claim("CL-C4-D3-TUBE-T-ROOT", "Tube torsion at the bore end, limit (for C1's J-FINHALF comparison)",
          calc="CALC-C4-D3-STATIC", output="tube_t_root_lim_nm", unit="N m", parts=TUBES, how="T-C4-FIN-PROOF.")
kit.claim("CL-C4-D3-SIDE-LOAD", "Foot side load used (friction 0.7 x CL-C1-FOOT-CORNER, CR-C1-21)",
          calc="CALC-C4-D3-STATIC",
          output="side_load_n", unit="N", parts=HALF, how="D5 pad friction coupon (ASM-C1-FRICTION, ASM-D5-PAD-MU).")
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
kit.claim("CL-C4-D3-MOUNT-ROCK", "Mount rocking moment, design, envelope of H2c with the cant and G3 set-down",
          calc="CALC-C4-D3-MOUNT-CANT",
          output="rock_env_design_nm", unit="N m", parts=MOUNT, how="T-C4-MOUNT-STIFF (load to 1.5 x limit).")
kit.claim("CL-C4-D3-MOUNT-G3-ROCK", "Mount rocking moment from the G3 set-down on a lower can, design (CR-C1-24)",
          calc="CALC-C4-D3-MOUNT-CANT", output="rock_g3_design_nm", unit="N m", parts=MOUNT[2:],
          how="T-C4-FIN-PROOF G3 step on the test article.")
kit.claim("CL-C4-D3-MS-CAP-G3", "Mount lip cap bearing on the tube end under G3 set-down (CR-C1-24)",
          calc="CALC-C4-D3-MOUNT-CANT", output="ms_cap_bearing_g3", unit="-", limit=(">=", 0.0), verifies=R_SM,
          parts=MOUNT[2:] + TUBES, how="T-C4-FIN-PROOF G3 step: no cap crush, mount does not slide down the tube.")
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

kit.claim("CL-C4-D3-SEC-T-L4", "Half-fin torsion about the tube axis at the wing plane, L4, limit (FE reactions)",
          calc="CALC-C4-D3-STATIC", output="t_sec_L4_lim_nm", unit="N m", parts=HALF + TUBES + BRACE,
          how="T-C4-FIN-PROOF L4 step: load cell on the foot.",
          note="Section total (tube root + fin root + brace anchor). The collar torque CL-C4-D3-COLLAR-T is an internal "
               "path quantity and is smaller; C6 sizes the collar to the larger of the two (CR-C1-21).")
kit.claim("CL-C4-D3-SEC-T-VS-C1", "FE wing-plane torsion vs C1's CL-C1-FINHALF-T-WINGPLANE-LIM, |ratio - 1|",
          calc="CALC-C4-D3-STATIC", output="t_sec_vs_c1", unit="-", limit=("<=", 0.05), parts=HALF,
          how="Re-run fin_structures_d3.py after any C1 or D5 foot-geometry change.",
          note="CR-C1-21 equilibrium check: same foot load and ground point as C1 within 5 %.")
kit.claim("CL-C4-D3-EQ-RESID", "FE equilibrium: wing-plane reaction torque vs applied torque, worst case",
          calc="CALC-C4-D3-STATIC", output="eq_resid", unit="-", limit=("<=", 1e-3), parts=HALF,
          how="Re-run fin_structures_d3.py.")
kit.claim("CL-C4-D3-SWIRL-F", "Swirl side force per half-fin used with H2c (B4 misbuilt, scaled to T_lim), limit",
          calc="CALC-C4-D3-STATIC", output="swirl_force_lim_n", unit="N", parts=HALF,
          how="B4 tuft/flow check in hover; T-C4-FIN-PROOF covers it (L4 side load is 4 x larger).")
kit.claim("CL-C4-D3-BRACE-G3", "Brace force under the G3 set-down, lower quarter, limit", calc="CALC-C4-D3-STATIC",
          output="brace_g3_lim_n", unit="N", parts=BRACE[2:], how="T-C4-FIN-PROOF G3 step.")
kit.claim("CL-C4-D3-MS-COLLAR-16", "Station-collar bond margin if the collar stays 16 mm (R3) instead of 12 mm",
          calc="CALC-C4-D3-STATIC", output="ms_collar_bond_16mm", unit="-", limit=(">=", 0.0), parts=COLLAR,
          how="As CL-C4-D3-MS-COLLAR.", note="Torsion from the 12 mm model; the 16 mm band changes it by < 3 % "
                                            "(results_d3.json collar_16mm).")
kit.claim("CL-C4-D3-F-WHIRL-CRUISE", "Lowest station whirl frequency at cruise rpm (both cant senses)",
          calc="CALC-C4-D3-CAMPBELL", output="f_whirl_cruise_hz", unit="Hz", parts=TUBES + MOUNT, how=TAP)
kit.claim("CL-C4-D3-BRACE-ROUND-I", "Weak-axis I of the 10 x 2 brace with both edges sanded full round, fraction",
          calc="CALC-C4-D3-BRACE-TRADE", output="round_i_frac", unit="-", parts=BRACE,
          how="Calipers on a sanded offcut.", note="CR-B1-18: rounding changes the 10 x 2 stiffness, so C4 asks for "
                                                    "a tape fairing instead (CR-C4-31).")
kit.claim("CL-C4-D3-BRACE-ROUND-MS", "Brace buckling margin if the 10 x 2 edges are sanded round (G2 design)",
          calc="CALC-C4-D3-BRACE-TRADE", output="ms_buckle_t2_round", unit="-", limit=(">=", 0.0), parts=BRACE,
          how="T-C4-FIN-PROOF G2 both senses.")
kit.claim("CL-C4-D3-MS-FACE-SHOE", "Fin face margin with the D5 shoe cheeks to |z| 0.171 m (CR-C4-30), 36 x 30 mesh",
          calc="CALC-C4-D3-SHOE", output="ms_face_prop", unit="-", limit=(">=", 0.0), verifies=R_SM, parts=HALF,
          how="T-C4-FIN-PROOF with the extended shoe; T-C4-BOARD-COUPON for the face allowable.")
kit.claim("CL-C4-D3-MS-FACE-SHOE-INTACT", "Fin face margin, cheeks to |z| 0.171 m, LE fillet intact, ultimate",
          calc="CALC-C4-D3-SHOE", output="ms_face_intact_prop", unit="-", limit=(">=", 0.0), parts=HALF,
          how="T-C4-FIN-PROOF (bonded quarter) at 1.5 x L4.")
kit.claim("CL-C4-D3-MS-FACE-SHOE-FS", "Fin face margin, cheeks to |z| 0.171 m, LE fillet cracked (fail-safe), limit",
          calc="CALC-C4-D3-SHOE", output="ms_face_failsafe_prop", unit="-", limit=(">=", 0.0), parts=HALF,
          how="T-C4-FIN-PROOF: the test-article quarter is built with the LE fillet unbonded.",
          note="Peak at the end of the bonded LE band (x 0.060, z 0.033 / 0.149): a corner that does not converge "
               "with mesh (24 x 20: 7.9, 36 x 30: 9.9 MPa limit); the test decides.")
kit.claim("CL-C4-D3-MS-FACE-DRAWN-FINE", "Fin face margin with the shoe cheeks as drawn (|z| 0.196), 36 x 30 mesh",
          calc="CALC-C4-D3-SHOE", output="ms_face_drawn_fine", unit="-", limit=(">=", 0.0), parts=HALF,
          how="Mesh check of CL-C4-D3-MS-FACE (24 x 20); both fail.")
kit.claim("CL-C4-D3-SHOE-EXT", "D5 shoe cheek extension toward the wing needed (CR-C4-30)", calc="CALC-C4-D3-SHOE",
          output="cheek_extension_m", unit="m", parts=HALF, how="D5 CAD: cheek lower edge at |z| <= 0.171 m.")
kit.claim("CL-C4-D3-BRACE-TAPE-MASS", "Tape fairing on four braces (CR-B1-18), mass", calc="CALC-C4-D3-BRACE-TRADE",
          output="tape_mass4_g", unit="g", parts=BRACE, how="Weigh the tape for one brace.")

kit.test("T-C4-FIN-PROOF", "Ultimate proof of one TEST-ARTICLE fin quarter (not a flight fin; CR-H1-17)",
         verifies=["CL-C4-D3-MS-FACE", "CL-C4-D3-MS-EDGE", "CL-C4-D3-MS-TUBE", "CL-C4-D3-MS-BRACE",
                   "CL-C4-D3-MS-BRACE-END", "CL-C4-D3-MS-COLLAR", "CL-C4-D3-MS-EAR", "CL-C4-D3-MS-ANCHOR",
                   "CL-C4-D3-FOOT-DEFL", "CL-C4-D3-MS-STRIP-PAPER", "CL-C4-D3-STRIP-PIN-F", "CL-C4-D3-MS-CAP-G3",
                   "CL-C4-D3-SEC-T-L4", "CL-C4-D3-COLLAR-H-REQ", "CL-C4-D3-MS-FACE-SHOE"],
         procedure="Test article built with flight processes but never flown: one LOWER quarter (it carries G3 and "
                   "the longer free tube) = one 0.21 m half-fin cut from the flight board batch (two 4.8 mm layers "
                   "laminated), CF 22 x 20 tube offcut 0.20 m, PETG through-core block bonded on a 0.15 m spar "
                   "offcut in a 0.15 m core offcut, plug, station collar (as drawn, 12 mm), CF 10 x 2 brace 0.16 m "
                   "with anchor saddle on the same spar offcut, CF 10 x 1 edge strips x 2 with 2 mm CF pins at 15 mm, "
                   "ASA mount with a dummy motor (steel slug at the motor CG, M3 x 8 into the plate), D5 shoe (cheeks "
                   "to |z| 0.171 m, CR-C4-30) and foot, LE fillet LEFT UNBONDED (fail-safe case), 30 min epoxy as in BUILD. Steps, each held 30 s, "
                   "loads at 1.5 x limit through a hand-held spring scale or hung weights: (1) L4 at the C1 ground "
                   "point 49 N along + 34 N across, both senses; (2) G2 77 N lateral at the tube end, both senses; "
                   "(3) G3 35 N on the dummy can toward the wing. Pass: no crack, face wrinkle, strip lift, pin "
                   "push-out or bond-line movement (witness lines on collar, strip ends, brace ends, anchor); foot "
                   "deflection at 1.0 x L4 <= 1.2 x CL-C4-D3-FOOT-DEFL. Then load step (1) to failure and record the "
                   "load and the failed part. Flight fins get a 1.0 x limit L4 hand check only.")
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
    # station collar 16 mm (R3) against the params value (R4: 12 mm), full static envelope
    st_in = {**GEOM, **TUBE, **STAT_IN, **REC}
    kw = {n: kit.value(r) for n, r in st_in.items()}
    for h in (0.012, 0.016):
        r_h = static_d3(**{**kw, "sc_h": h})
        res.setdefault("collar_sweep", {})[f"{h * 1000:.0f} mm"] = {
            key: r_h[key] for key in ("collar_t_lim_nm", "collar_t_lim_intact_nm", "ms_collar_bond", "collar_h_req_m",
                                      "ms_face", "ms_strip_paper", "strip_end_face_design_n", "t_sec_L4_lim_nm")}
        print(f"collar {h * 1000:.0f} mm: T {r_h['collar_t_lim_nm']:.2f} N m (intact {r_h['collar_t_lim_intact_nm']:.2f}),"
              f" MS bond {r_h['ms_collar_bond']:+.2f}, h_req {r_h['collar_h_req_m'] * 1000:.1f} mm, MS face "
              f"{r_h['ms_face']:+.2f}")
    # D5 shoe cheek depth (CR-C4-30): face margin vs the lowest |z| of the cheeks, 36 x 30 mesh
    for z0 in (0.196, 0.186, 0.181, 0.176, 0.171, 0.166):
        r_z = static_d3(**{**kw, "shoe_z0": z0, "_mesh": SHOE_MESH})
        res.setdefault("shoe_sweep", {})[f"{z0:.3f} m"] = {key: r_z[key] for key in (
            "ms_face", "ms_face_intact_ult", "ms_face_failsafe_lim", "face_ult_pa", "ms_min", "ms_strip_paper", "dfoot_L4_m", "governing")}
        print(f"shoe cheeks to |z| {z0:.3f}: face {r_z['face_ult_pa'] / 1e6:5.1f} MPa ult, MS {r_z['ms_face']:+.2f} "
              f"({r_z['governing'].split('face: ')[1].split(';')[0]})")
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
