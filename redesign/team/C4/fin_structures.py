"""C4 fin / motor-tube structures: modes, fin and tube strength, through-core block (K09-L).

Run:  python -I redesign/team/C4/fin_structures.py      (about 5 s)
Writes claims.json beside this file (proof chain), out/results.json (every number in BOOM-STRUCTURES.md) and
fig-c4-campbell.svg. Then: python -I redesign/proofs/build_graph.py

Model: fin_fe.py (tube frame elements + foam-board shell + rigid motor/prop + optional strut), one quarter
(the UR station; the other three are mirror images). Loads: C1 claims (limit), ultimate = 1.5 x limit,
joints x 1.15 fitting x 1.25 printed/bonded. Forcing: B4 rpm claims (hover, cruise, F4 cap).
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

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"

# ====================================================================== sources and assumptions
kit.source("SRC-C4-LEISSA", "Leissa, Vibration of Plates, NASA SP-160 (1969), table 4.27", "book",
           where="cantilever square plate, nu 0.3: lambda^2 = omega a^2 sqrt(rho h / D) = 3.492, 8.525, 21.43")
kit.source("SRC-C4-BLEVINS", "Blevins, Formulas for Natural Frequency and Mode Shape (1979), table 8-1", "book",
           where="cantilever with tip mass: f = (1/2pi) sqrt(3EI / (L^3 (M + 0.24 m_beam)))")
kit.source("SRC-C4-ROARK", "Young & Budynas, Roark's Formulas for Stress and Strain, 7th ed., ch. 9 and 10", "book",
           where="torsion of rectangular sections tau = T / (alpha b c^2); thin-ring bearing (ch. 9) motivates the "
                 "internal plug at every bore")
kit.source("SRC-C4-ALLEN", "Allen, Analysis and Design of Structural Sandwich Panels (1969), ch. 2 and 8", "book",
           where="sandwich bending D = E_f t_f d^2 / 2 per face pair, core shear S = G_c d^2 / t_c, face wrinkling")
kit.source("SRC-C4-PETG", "Prusament PETG technical data sheet (2023)", "datasheet",
           url="https://prusament.com/media/2023/06/PETG_TDS_2023_EN.pdf",
           where="tensile yield 47 MPa (XY), 30 MPa (Z, interlayer); flexural 60 MPa", status="UNVERIFIED",
           note="not re-opened in this session; allowables below are taken at about 40-70 % of these")

ASM = {}


def asm(id, title, text, basis, value, unit, status="UNVERIFIED", cites=()):
    ASM[id] = value
    kit.assumption(id, title, text, basis, value=value, unit=unit, status=status, cites=cites)


asm("ASM-C4-G-TUBE", "Tube shear modulus 5 GPa",
    "In-plane shear modulus of the roll-wrapped 22 x 20 mm CF tube (sets tube torsion)",
    "Roll-wrapped hobby tubes are mostly 0 deg UD with a woven outer ply: G 3-10 GPa. Torsion test T-C4-TUBE-TORSION "
    "replaces it", 5.0e9, "Pa")
asm("ASM-C4-E-TUBE-LO", "Tube modulus, low corner 70 GPa", "Lower bound of the hobby-tube axial modulus",
    "J1: hobby tubes 50-140 GPa; 70 GPa = woven-heavy roll-wrapped tube", 70e9, "Pa")
asm("ASM-C4-E-TUBE-HI", "Tube modulus, high corner 135 GPa", "Upper bound of the hobby-tube axial modulus",
    "standard-modulus UD-dominant pultruded or roll-wrapped tube", 135e9, "Pa")
asm("ASM-C4-G-TUBE-LO", "Tube shear modulus, low corner 3 GPa", "Lower bound", "pure UD tube, G12 ~ 3-4 GPa", 3e9, "Pa")
asm("ASM-C4-G-TUBE-HI", "Tube shear modulus, high corner 10 GPa", "Upper bound", "woven/+-45 outer plies", 10e9, "Pa")
asm("ASM-C4-CORE-T-TUBE", "Core thickness at the tube station 27 mm",
    "Wing thickness at x = 0.045 m, y = 0.32 m = height of the through-core block and of the tube bore",
    "B3 CR-B3-02 (27 mm at x 0.045 for S5010, c 0.32); D1 confirms from the hot-wire templates", 0.027, "m")
asm("ASM-C4-FACE-T", "Foam-board face 0.10 mm", "Paper face thickness of 3/16 in foam board, each side",
    "board 0.2 kg/m2 (params) = 2 faces ~0.05 kg/m2 each + PS core; measure with a micrometer (T-C4-BOARD-COUPON)",
    1.0e-4, "m")
asm("ASM-C4-FACE-E", "Foam-board face modulus 4 GPa", "Paper/clay-coat face modulus, MD/CD mean",
    "paperboard 2-7 GPa (CD-MD); coupon bend test T-C4-BOARD-COUPON", 4.0e9, "Pa")
asm("ASM-C4-FACE-SIGMA", "Foam-board face allowable 10 MPa", "Compressive (governing) allowable of the paper face",
    "paperboard compression 10-20 MPa; face wrinkling on a ~25 kg/m3 core ~25 MPa; take the lower", 10e6, "Pa")
asm("ASM-C4-CORE-E", "Foam-board core modulus 10 MPa", "PS foam core, ~25 kg/m3", "Gibson-Ashby for PS", 10e6, "Pa")
asm("ASM-C4-CORE-G", "Foam-board core shear 4 MPa", "PS foam core shear modulus", "Gibson-Ashby for PS", 4e6, "Pa")
asm("ASM-C4-PROP-IP", "Prop polar inertia 7.5e-5 kg m2", "APC 11x5.5MR about the shaft (17 g, R 0.140 m)",
    "m R^2 / 4.4 for a tapered 2-blade prop; bifilar swing of one prop replaces it (T-C4-PROP-SWING)", 7.5e-5, "kg m2")
asm("ASM-C4-MOUNT-DX", "Mount centroid 5 mm ahead of the tube axis", "Printed mount mass centre offset in x",
    "mount plate at x 0.034, clamp around the tube; D3's CAD replaces it", -0.005, "m")
asm("ASM-C4-STRUT-DY", "Strut anchor 0.12 m inboard", "Brace anchor on the spar line, inboard of the fin",
    "keeps the anchor off the elevon (x < 0.2496) and the pod (|y| > 0.10); 0.12 m gives a 37 deg strut", 0.12, "m")
asm("ASM-C4-STRUT-DZ", "Strut attach 25 mm below the motor axis", "Strut collar on the tube just below the mount",
    "mount clamps z 0.17-0.21 (D3); collar at z = station - 0.025", 0.025, "m")
asm("ASM-C4-STRUT-W", "Strut strip width 10 mm", "Pultruded CF flat strip 10 x 2 mm, 10 mm side along the flow",
    "stock size; streamwise strip keeps cruise drag ~0.02 N per strut", 0.010, "m")
asm("ASM-C4-STRUT-T", "Strut strip thickness 2 mm", "see ASM-C4-STRUT-W", "stock size", 0.002, "m")
asm("ASM-C4-EDGE-W", "Fin edge strips 10 mm wide", "Pultruded CF strip 10 x 1 mm bonded on both outer faces of each "
    "half-fin, chordwise from the tube collar to the foot", "carries the L4 side load at the foot to the tube; stock size",
    0.010, "m", status="PROPOSED")
asm("ASM-C4-EDGE-T", "Fin edge strips 1 mm thick", "see ASM-C4-EDGE-W", "stock size", 0.001, "m", status="PROPOSED")
asm("ASM-C4-EDGE-DZ", "Edge strips on the fin top edge (0 mm below the station)",
    "Strip line = fin top edge; the fin top-LE corner is notched under the mount and the strips end in the station collar "
    "directly below the mount (z 0.150-0.170), so no free fin band is left above the strips",
    "FE: a 25-35 mm free band above the strips gives a 170-260 Hz panel mode that moves the motor (out/results.json)",
    0.0, "m", status="PROPOSED")
asm("ASM-C4-CF-E-STRIP", "Pultruded CF strip modulus 110 GPa", "Axial modulus of a pultruded UD strip",
    "pultruded UD 110-135 GPa; take the low end", 110e9, "Pa")
asm("ASM-C4-CF-SIGMA", "CF tube/strip allowable 400 MPa", "Allowable bending/axial stress of roll-wrapped CF",
    "hobby tube flexural strength 600-1000 MPa; 400 MPa covers crushing near clamps", 400e6, "Pa")
asm("ASM-C4-CF-RHO", "CF density 1550 kg/m3", "Pultruded/roll-wrapped CF", "datasheet range 1500-1600", 1550.0,
    "kg/m3", status="PROPOSED")
asm("ASM-C4-STRUT-FIT-MASS", "Strut end fittings 4 g each", "Printed collar/ear and spar saddle per strut end",
    "PETG, ~3 cm3 at 1.27 g/cm3", 0.004, "kg")
asm("ASM-C4-BLOCK-W", "Block spar-bore length 36 mm", "Spanwise length of the through-core block (= spar bore)",
    "C4 sizing choice: 7 mm walls each side of the 22 mm tube bore", 0.036, "m", status="PROPOSED")
asm("ASM-C4-BLOCK-FILL", "Block effective fill 0.55", "Printed solid fraction: 4 perimeters + 40 % gyroid",
    "G3 sets the slicer profile; walls carry the bearing", 0.55, "-", status="PROPOSED")
asm("ASM-C4-PETG-RHO", "PETG density 1270 kg/m3", "Prusament PETG", "datasheet", 1270.0, "kg/m3", status="PROPOSED",
    cites=["SRC-C4-PETG"])
asm("ASM-C4-PETG-BEARING", "Printed PETG bearing allowable 20 MPa", "Bearing on a bore wall, layers in the x-y plane",
    "~45 % of the XY yield; creep under the bonded preload", 20e6, "Pa", cites=["SRC-C4-PETG"])
asm("ASM-C4-PETG-TENSILE", "Printed PETG tensile allowable 15 MPa", "Tension/bending, interlayer (worst) direction",
    "50 % of the Z yield 30 MPa", 15e6, "Pa", cites=["SRC-C4-PETG"])
asm("ASM-C4-PETG-SHEAR", "Printed PETG shear allowable 10 MPa", "Shear-out and web torsion",
    "~0.6 x tensile allowable rounded", 10e6, "Pa", cites=["SRC-C4-PETG"])
asm("ASM-C4-BOND-SHEAR", "Epoxy bond on abraded PETG/CF 2 MPa", "Lap-shear allowable, 30-min epoxy, 80-grit both sides",
    "PETG bonds poorly (2-5 MPa lap shear); C6 coupons replace it", 2e6, "Pa")
asm("ASM-C4-FINJOINT-M-TASK", "Fin-joint moment 10.7 N m (C1 rev A, G2)",
    "The fin-joint limit moment named in the A1 action item; C1 now reports 9.4 N m. The block is sized to the larger",
    "team/C1/LOADS.md rev A finding 5; params/CHANGE-LOG.md D-23", 10.7, "N m", status="PROPOSED")
asm("ASM-C4-FINJOINT-MY", "Fin-group pitching moment about the spar 5.2 N m (limit)",
    "Largest |My| of J-FIN-R over the sizing families (F7 rolling pull-up, MC-P)",
    "team/C1/data/joints.csv; torsion of the block on the round spar is carried by the bond", 5.17, "N m")
asm("ASM-C4-FOOT-PATCH", "Foot load spread over 30 mm", "The printed foot cap spreads the foot load over the fin "
    "nodes within 30 mm of the TE tip", "D5 cap length 45 mm; C5 confirms", 0.030, "m")

LIMIT_SEP = P + "requirements.vibration_sep_frac"
SF, FIT, PRT = P + "requirements.safety_factor_ult", "ASM-C1-FITTING-FACTOR", "ASM-C1-PRINTED-FACTOR"

# ====================================================================== shared inputs
GEOM = {"tube_x": P + "fins.tube.x_m", "od": P + "fins.tube.od_m", "idd": P + "fins.tube.id_m",
        "mu": P + "wing.spar.mass_per_m_kgm", "tube_len": P + "fins.tube.length_m",
        "z_st": P + "propulsion.stations.z_m", "x_mount": P + "propulsion.stations.x_mount_m",
        "x_prop": P + "propulsion.stations.x_prop_plane_m", "x_te": P + "fins.te_x_m",
        "hh": P + "fins.half_height_m", "core_t": "ASM-C4-CORE-T-TUBE",
        "m_motor": P + "propulsion.motor_mass_kg", "d_motor": P + "propulsion.motor_diameter_m",
        "l_motor": P + "propulsion.motor_length_m", "m_prop": P + "propulsion.prop_mass_kg",
        "m_adapt": "ASM-C1-ADAPTER-MASS", "ip": "ASM-C4-PROP-IP", "i_bell": "ASM-C1-BELL-INERTIA",
        "m_mount": "ASM-J1-MOUNT-MASS", "mount_dx": "ASM-C4-MOUNT-DX", "m_esc": P + "propulsion.esc_mass_kg",
        "landing_g": P + "mass.allocation_g.landing",
        "t_board": P + "fins.board_t_m", "areal": P + "fins.areal_mass_kgm2", "t_face": "ASM-C4-FACE-T",
        "e_face": "ASM-C4-FACE-E", "e_core": "ASM-C4-CORE-E", "g_core": "ASM-C4-CORE-G",
        "x_spar": P + "wing.spar.x_m", "s_dy": "ASM-C4-STRUT-DY", "s_dz": "ASM-C4-STRUT-DZ",
        "s_w": "ASM-C4-STRUT-W", "s_t": "ASM-C4-STRUT-T", "e_strip": "ASM-C4-CF-E-STRIP",
        "e_w": "ASM-C4-EDGE-W", "e_t": "ASM-C4-EDGE-T", "e_dz": "ASM-C4-EDGE-DZ", "rho_cf": "ASM-C4-CF-RHO"}
GEOM_UNITS = {"tube_x": "m", "od": "m", "idd": "m", "mu": "kg/m", "tube_len": "m", "z_st": "m", "x_mount": "m",
              "x_prop": "m", "x_te": "m", "hh": "m", "core_t": "m", "m_motor": "kg", "d_motor": "m", "l_motor": "m",
              "m_prop": "kg", "m_adapt": "kg", "ip": "kg m2", "i_bell": "kg m2", "m_mount": "kg", "mount_dx": "m",
              "m_esc": "kg", "landing_g": "g", "t_board": "m", "areal": "kg/m2", "t_face": "m", "e_face": "Pa",
              "e_core": "Pa", "g_core": "Pa", "x_spar": "m", "s_dy": "m", "s_dz": "m", "s_w": "m", "s_t": "m",
              "e_strip": "Pa", "e_w": "m", "e_t": "m", "e_dz": "m", "rho_cf": "kg/m3"}
RPM = {"rpm_h": "CL-B4-HOVER-RPM", "rpm_c": "CL-B4-CRUISE-RPM", "rpm_x": "CL-B4-RPM-MAX"}
RPM_UNITS = {"rpm_h": "rpm", "rpm_c": "rpm", "rpm_x": "rpm"}
TUBE = {"E": "ASM-J1-E-TUBE", "G": "ASM-C4-G-TUBE"}
TUBE_UNITS = {"E": "Pa", "G": "Pa"}
MESH = (12, 10)


def model_cfg(g, E, G, layers, strut, mesh=MESH, edge=None):
    """fin_fe config from the named inputs (dict g) for one quarter station."""
    A = math.pi / 4 * (g["od"] ** 2 - g["idd"] ** 2)
    z_cl = g["core_t"] / 2
    x_motor = g["x_mount"] - g["od"] / 2 - g["l_motor"] / 2
    rm = g["d_motor"] / 2
    jm_ax = g["m_motor"] * rm * rm / 2
    jm_tr = g["m_motor"] * (3 * rm * rm + g["l_motor"] ** 2) / 12
    ip = g["ip"]
    parts = [(g["m_motor"], (x_motor - g["tube_x"], 0, 0), (jm_ax, jm_tr, jm_tr)),
             (g["m_prop"] + g["m_adapt"], (g["x_prop"] - g["tube_x"], 0, 0), (ip, ip / 2, ip / 2)),
             (g["m_mount"], (g["mount_dx"], 0, 0), (1e-6, 1e-6, 1e-6))]
    pr = None
    if layers > 0:
        pr = fe.board_props(int(layers), g["t_board"], g["t_face"], g["e_face"], 0.3, g["e_core"], g["g_core"],
                            g["areal"])
    cfg = {"tube": {"x": g["tube_x"], "E": E, "G": G, "od": g["od"], "id": g["idd"], "rho": g["mu"] / A,
                    "z_clamp": z_cl, "z_end": g["tube_len"] / 2},
           "z_station": g["z_st"],
           "fin": {"props": pr, "x_le": g["tube_x"] + g["od"] / 2, "x_te": g["x_te"], "z_root": z_cl,
                   "z_top": g["hh"]},
           "nx": mesh[0], "nz": mesh[1], "n_ext": 2, "root": "pinned", "k_root_rx": None, "k_root_ry": None,
           "station_parts": parts,
           "fin_masses": [(g["m_esc"], (g["tube_x"] + 0.04, 0.6 * g["z_st"])),      # A3 mass_model placement
                          (g["landing_g"] / 4 / 1000.0, (g["x_te"], g["hh"]))],
           "struts": []}
    if edge is None:
        edge = strut
    if edge and layers > 0:
        d = layers * g["t_board"] + g["e_t"]
        cfg["stiffeners"] = [{"row_frac": (g["z_st"] - g["e_dz"] - z_cl) / (g["z_st"] - z_cl), "E": g["e_strip"],
                              "G": 5e9, "A": 2 * g["e_w"] * g["e_t"], "I_out": g["e_w"] * g["e_t"] * d * d / 2,
                              "J": 2 * g["e_w"] * g["e_t"] ** 3 / 3, "rho": g["rho_cf"], "d": d}]
    if strut:
        cfg["struts"] = [{"ax": -g["od"] / 2, "ay": -g["od"] / 2, "az": -g["s_dz"],
                          "anchor": (g["x_spar"], -g["s_dy"], z_cl + 0.002), "EA": g["e_strip"] * g["s_w"] * g["s_t"]}]
    return cfg


def forcing(rpm_h, rpm_c, rpm_x):
    return {"1P hover": rpm_h / 60, "2P hover": rpm_h / 30, "1P cruise": rpm_c / 60, "2P cruise": rpm_c / 30,
            "1P max": rpm_x / 60}


def sep_points(f, pts):
    s = {k: abs(f / v - 1) for k, v in pts.items()}
    k = min(s, key=s.get)
    return s[k], k


def sep_band(f, lo, hi):
    if f < lo:
        return 1 - f / lo
    if f > hi:
        return f / hi - 1
    return -min(f / lo - 1, 1 - f / hi)


ST_PART = 0.10      # a mode "moves the motor" when >= 10 % of its kinetic energy is in the station rigid body


def station_modes(mdl, n=16):
    """Modes up to n; station modes = >= ST_PART of the kinetic energy in the motor/prop/mount body."""
    f, Phi, _ = fe.modes(mdl, n)
    cl = fe.classify(mdl, Phi)
    st = [(float(x), c["kind"]) for x, c in zip(f, cl) if c["ke_station"] >= ST_PART]
    lt = [x for x, k in st if k.startswith("lateral")]
    fa = [x for x, k in st if k.startswith("fore")]
    pn = [float(x) for x, c in zip(f, cl) if c["ke_station"] < ST_PART]
    return {"f_st": [x for x, k in st], "f_st1": st[0][0], "kind_st1": st[0][1], "f_st2": st[1][0] if len(st) > 1 else st[0][0],
            "f_lt": lt[0] if lt else float(f[-1]), "f_fa": fa[0] if fa else float(f[-1]),
            "f_panel": pn[0] if pn else float(f[-1]), "f_top": float(f[-1]),
            "all": [(float(x), c["kind"], round(c["ke_station"], 3)) for x, c in zip(f, cl)]}


def modal_summary(g, E, G, layers, strut, rpm_h, rpm_c, rpm_x, lo=80.0, hi=330.0, mesh=MESH):
    mdl = fe.build(model_cfg(g, E, G, layers, strut, mesh))
    r = station_modes(mdl)
    pts = forcing(rpm_h, rpm_c, rpm_x)
    best = (9.0, "")
    for f in r["f_st"]:
        s, k = sep_points(f, pts)
        if s < best[0]:
            best = (s, f"{k} vs {f:.0f} Hz")
    r.update({"sep_op": best[0], "nearest": best[1],
              "sep_band": min(sep_band(f, lo, hi) for f in r["f_st"])})
    return r


# ====================================================================== calculations
@kit.calc("CALC-C4-FE-CHECK", title="FE model checks against closed forms",
          equation="(a) bare tube + tip mass vs Blevins f = sqrt(3EI/(L^3 (M + 0.24 m))) / 2pi ; "
                   "(b) cantilever foam-board plate 0.2 x 0.2 m vs Leissa lambda^2 = 3.492 (Kirchhoff limit, stiff core)",
          inputs={**{k: GEOM[k] for k in ("od", "idd", "mu", "hh", "m_motor", "m_prop", "m_mount", "t_board",
                                           "areal", "t_face", "e_face", "e_core")}, "E": "ASM-J1-E-TUBE"},
          units={**{k: GEOM_UNITS[k] for k in ("od", "idd", "mu", "hh", "m_motor", "m_prop", "m_mount", "t_board",
                                              "areal", "t_face", "e_face", "e_core")}, "E": "Pa"},
          cites=["SRC-C4-BLEVINS", "SRC-C4-LEISSA"], tol=1e-4)
def fe_check(od, idd, mu, hh, m_motor, m_prop, m_mount, t_board, areal, t_face, e_face, e_core, E):
    A = math.pi / 4 * (od ** 2 - idd ** 2)
    M = m_motor + m_prop + m_mount
    cfg = {"tube": {"x": 0.0, "E": E, "G": 5e9, "od": od, "id": idd, "rho": mu / A, "z_clamp": 0.0, "z_end": hh},
           "z_station": hh, "fin": {"props": None}, "nx": 1, "nz": 20, "n_ext": 0, "root": "pinned",
           "k_root_rx": None, "k_root_ry": None, "station_parts": [(M, (0, 0, 0), (0, 0, 0))]}
    f_fe = float(fe.modes(fe.build(cfg), 2)[0][0])
    I = math.pi / 64 * (od ** 4 - idd ** 4)
    f_cf = math.sqrt(3 * E * I / (hh ** 3 * (M + 0.24 * mu * hh))) / (2 * math.pi)
    pr = fe.board_props(1, t_board, t_face, e_face, 0.3, e_core, 1e9, areal)
    a = 0.2
    fp = float(fe.plate_cantilever(a, a, 16, pr, 1)[0])
    fl = 3.492 / (2 * math.pi * a * a) * math.sqrt(pr["D"] / pr["rho_h"])
    return {"f_tube_fe": f_fe, "f_tube_cf": f_cf, "err_tube": abs(f_fe / f_cf - 1),
            "f_plate_fe": fp, "f_plate_leissa": fl, "err_plate": abs(fp / fl - 1)}


def _modal_calc(cid, title, layers_ref, strut, extra_note):
    ins = {**GEOM, **RPM, **TUBE, "layers": layers_ref, "lo": "ASM-C4-BAND-LO", "hi": "ASM-C4-BAND-HI"}
    uns = {**GEOM_UNITS, **RPM_UNITS, **TUBE_UNITS, "layers": "-", "lo": "Hz", "hi": "Hz"}

    def calc(**k):
        g = {n: k[n] for n in GEOM}
        r = modal_summary(g, k["E"], k["G"], k["layers"], strut, k["rpm_h"], k["rpm_c"], k["rpm_x"], k["lo"], k["hi"])
        return {"f_st1": r["f_st1"], "f_st2": r["f_st2"], "f_panel": r["f_panel"], "sep_op": r["sep_op"],
                "sep_band": r["sep_band"]}
    calc.__name__ = "modes_" + cid.split("-")[-1].lower()
    globals()[calc.__name__] = calc
    kit.calc(cid, title=title, inputs=ins, units=uns, tol=1e-4,
              equation="FE modes of tube + half-fin + motor/prop rigid body" + extra_note +
                       "; sep_op = min |f/f_k - 1| over 1P/2P hover, 1P/2P cruise, 1P max ; sep_band vs [lo, hi]",
              assumes=["ASM-C4-G-TUBE", "ASM-C4-FACE-T", "ASM-C4-FACE-E", "ASM-C4-PROP-IP"],
              cites=["SRC-C4-ALLEN"])(calc)
    return calc


asm("ASM-C4-BAND-LO", "Forcing band low edge 80 Hz", "B4's excitation band, CR-B4-07", "1P hover 90 Hz less 11 %",
    80.0, "Hz", status="PROPOSED")
asm("ASM-C4-BAND-HI", "Forcing band high edge 330 Hz", "B4's excitation band, CR-B4-07", "2P at the F4 cap 311 Hz + 6 %",
    330.0, "Hz", status="PROPOSED")
asm("ASM-C4-ONE-LAYER", "One foam-board layer per half-fin", "The -40 g option in MASS-CG.md", "A3 lever", 1, "-",
    status="PROPOSED")

_modal_calc("CALC-C4-MODES-2L", "Modes, current design: 2-layer fin, no brace", P + "fins.layers", False, "")
_modal_calc("CALC-C4-MODES-1L", "Modes, 1-layer fin, no brace", "ASM-C4-ONE-LAYER", False, "")
_modal_calc("CALC-C4-MODES-REC", "Modes, braced design: fin (layers per params.json) + CF brace + edge strips",
            P + "fins.layers", True, " + axial brace from the station to the spar")
_modal_calc("CALC-C4-MODES-1LB", "Modes, recommended: 1-layer fin + CF brace + edge strips", "ASM-C4-ONE-LAYER", True,
            " + axial brace from the station to the spar")


def _worst_calc(cid, title, layers_ref, strut):
    ins = {**GEOM, **RPM, "layers": layers_ref, "E0": "ASM-J1-E-TUBE", "E_lo": "ASM-C4-E-TUBE-LO",
           "E_hi": "ASM-C4-E-TUBE-HI", "G0": "ASM-C4-G-TUBE", "G_lo": "ASM-C4-G-TUBE-LO", "G_hi": "ASM-C4-G-TUBE-HI"}
    uns = {**GEOM_UNITS, **RPM_UNITS, "layers": "-", "E0": "Pa", "E_lo": "Pa", "E_hi": "Pa", "G0": "Pa", "G_lo": "Pa",
           "G_hi": "Pa"}

    def calc(**k):
        g = {n: k[n] for n in GEOM}
        worst, f_min, at = 9.0, 1e9, ""
        for E, G in itertools.product((k["E_lo"], k["E0"], k["E_hi"]), (k["G_lo"], k["G0"], k["G_hi"])):
            r = modal_summary(g, E, G, k["layers"], strut, k["rpm_h"], k["rpm_c"], k["rpm_x"])
            f_min = min(f_min, r["f_st1"])
            if r["sep_op"] < worst:
                worst = r["sep_op"]
        return {"sep_op_worst": worst, "f_station_min": f_min}
    calc.__name__ = "worst_" + cid.split("-")[-1].lower()
    globals()[calc.__name__] = calc
    kit.calc(cid, title=title, inputs=ins, units=uns, tol=1e-4,
             equation="min over E in {lo, nominal, hi} x G in {lo, nominal, hi} of sep_op (9 FE runs)",
             assumes=["ASM-C4-E-TUBE-LO", "ASM-C4-E-TUBE-HI", "ASM-C4-G-TUBE-LO", "ASM-C4-G-TUBE-HI"])(calc)


_worst_calc("CALC-C4-WORST-REC", "Separation over the tube E/G range, braced design (layers per params.json)", P + "fins.layers", True)
_worst_calc("CALC-C4-WORST-1LB", "Separation over the tube E/G range, 1-layer fin + brace", "ASM-C4-ONE-LAYER", True)


@kit.calc("CALC-C4-CONVERGENCE", title="Mesh convergence, braced design (layers per params.json)",
          inputs={**GEOM, **TUBE, "layers": P + "fins.layers"}, units={**GEOM_UNITS, **TUBE_UNITS, "layers": "-"},
          equation="first two station modes at fin meshes 6x5, 12x10 (used), 24x20 ; change = max |f(12x10)/f(24x20) - 1|",
          tol=1e-4)
def convergence(**k):
    g = {n: k[n] for n in GEOM}
    out = {}
    for tag, mesh in (("coarse", (6, 5)), ("used", MESH), ("fine", (24, 20))):
        r = station_modes(fe.build(model_cfg(g, k["E"], k["G"], k["layers"], True, mesh)))
        out[f"f1_{tag}"], out[f"f2_{tag}"] = r["f_st1"], r["f_st2"]
    out["change"] = max(abs(out["f1_used"] / out["f1_fine"] - 1), abs(out["f2_used"] / out["f2_fine"] - 1))
    return out


@kit.calc("CALC-C4-CAMPBELL", title="Gyroscopic whirl separation at the operating points, braced design (layers per params.json)",
          inputs={**GEOM, **RPM, **TUBE, "layers": P + "fins.layers"},
          units={**GEOM_UNITS, **RPM_UNITS, **TUBE_UNITS, "layers": "-"}, tol=1e-4,
          equation="M q'' + Omega G q' + K q = 0 on the first 12 modes; G = -[Ip_spin e_shaft]x at the station; "
                   "sep = min |f_whirl/f_k - 1| over 1P, 2P at hover, cruise and the F4 cap, station whirl modes only",
          assumes=["ASM-C4-PROP-IP", "ASM-C1-BELL-INERTIA"])
def campbell_sep(**k):
    g = {n: k[n] for n in GEOM}
    mdl = fe.build(model_cfg(g, k["E"], k["G"], k["layers"], True))
    worst, at = 9.0, ""
    for name, rpm in (("hover", k["rpm_h"]), ("cruise", k["rpm_c"]), ("max", k["rpm_x"])):
        fw = _station_whirl(mdl, g["ip"] + g["i_bell"], rpm)
        for f in fw:
            for p, fk in ((1, rpm / 60), (2, rpm / 30)):
                if name == "max" and p == 2:
                    continue                       # 2P at full throttle is a transient (same rule as sep_op)
                s = abs(f / fk - 1)
                if s < worst:
                    worst = s
    return {"sep_whirl": worst}


def _station_whirl(mdl, ip_spin, rpm, n_modes=16):
    """Whirl frequencies (Hz) of the station-dominated modes at one rpm (modal reduction)."""
    f0, Phi, _ = fe.modes(mdl, n_modes)
    cl = fe.classify(mdl, Phi)
    keep = [i for i, c in enumerate(cl) if c["ke_station"] >= ST_PART]
    w = 2 * math.pi * f0
    G = fe.gyro_matrix(mdl, ip_spin)
    Gm = Phi.T @ (G @ Phi)
    n = len(w)
    Om = rpm * 2 * math.pi / 60
    A = np.zeros((2 * n, 2 * n))
    A[:n, n:] = np.eye(n)
    A[n:, :n] = -np.diag(w ** 2)
    A[n:, n:] = -Om * Gm
    lam, vec = np.linalg.eig(A)
    out = []
    for j in range(2 * n):
        if lam[j].imag <= 1e-6:
            continue
        q = np.abs(vec[:n, j])
        dom = int(np.argmax(q))
        if dom in keep:
            out.append(float(lam[j].imag / (2 * math.pi)))
    return sorted(out)


def _static_calc(cid, title, layers_ref):
    ins = {**GEOM, **TUBE, "layers": layers_ref, "f_level": "CL-C1-FOOT-LEVEL", "f_corner": "CL-C1-FOOT-CORNER",
           "mu_g": "ASM-C1-FRICTION", "n_h": "ASM-C1-HANDLING-N", "m_gate": P + "requirements.mtow_gate_kg",
           "grav": P + "env.g_ms2", "t_lim": "CL-C1-T-LIMIT", "q_mot": "CL-C1-MOTOR-TORQUE", "sf": SF,
           "fit": FIT, "s_face": "ASM-C4-FACE-SIGMA", "s_cf": "ASM-C4-CF-SIGMA", "patch": "ASM-C4-FOOT-PATCH"}
    uns = {**GEOM_UNITS, **TUBE_UNITS, "layers": "-", "f_level": "N", "f_corner": "N", "mu_g": "-", "n_h": "-",
           "m_gate": "kg", "grav": "m/s2", "t_lim": "N", "q_mot": "N m", "sf": "-", "fit": "-", "s_face": "Pa",
           "s_cf": "Pa", "patch": "m"}

    def calc(**k):
        g = {n: k[n] for n in GEOM}
        return fin_static(g, k)
    calc.__name__ = "static_" + cid.split("-")[-1].lower()
    globals()[calc.__name__] = calc
    kit.calc(cid, title=title, inputs=ins, units=uns, tol=1e-4,
              equation="FE static, recommended brace fitted; cases L1 (level foot), L4 (foot + friction across the fin), "
                       "L5 (foot + friction along), G2 (n_h m g lateral at the tube end), H2 (T_lim + torque at the "
                       "station); ultimate = sf x limit; face stress = Q_f (N/A + z M/D); MS = allowable / ultimate - 1",
              assumes=["ASM-C4-FACE-SIGMA", "ASM-C4-FACE-T", "ASM-C4-FACE-E", "ASM-C4-FOOT-PATCH"],
              cites=["SRC-C4-ALLEN"])(calc)


def fin_static(g, k):
    mdl = fe.build(model_cfg(g, k["E"], k["G"], k["layers"], True))
    pr = mdl.cfg["fin"]["props"]
    nodes = mdl.nodes
    corner = np.array([g["x_te"], 0.0, g["hh"]])
    foot = [n for n in mdl.fin_id.values() if np.linalg.norm(nodes[n] - corner) <= k["patch"] + 1e-9]
    fc, mu = k["f_corner"], k["mu_g"]
    cases = {"L1": [(n, (-k["f_level"] / len(foot), 0, 0, 0, 0, 0)) for n in foot],
             "L4": [(n, (-fc / len(foot), -mu * fc / len(foot), 0, 0, 0, 0)) for n in foot],
             "L5": [(n, (-fc / len(foot), 0, -mu * fc / len(foot), 0, 0, 0)) for n in foot],
             "G2": [(mdl.i_end, (0, k["n_h"] * k["m_gate"] * k["grav"], 0, 0, 0, 0))],
             "H2": [(mdl.i_station, (-k["t_lim"], 0, 0, k["q_mot"], 0, 0))]}
    a = (mdl.cfg["fin"]["x_te"] - mdl.cfg["fin"]["x_le"]) / mdl.cfg["nx"]
    b = (mdl.cfg["z_station"] - mdl.cfg["tube"]["z_clamp"]) / mdl.cfg["nz"]
    nu = pr["nu"]
    Qf = g["e_face"] / (1 - nu * nu) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    Cm = pr["A"] * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    Cb = pr["D"] * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    zf = pr["z_face_out"]
    s = mdl.strut_info[0]
    out = {}
    worst_face, worst_case = 0.0, ""
    for cname, loads in cases.items():
        u = fe.static(mdl, loads)
        smax = 0.0
        for ns in mdl.shells:
            ue = np.concatenate([u[6 * n:6 * n + 6] for n in ns])
            Nv, Mv = fe.shell_resultants(a, b, pr, ue)
            e0, kap = np.linalg.solve(Cm, Nv), np.linalg.solve(Cb, Mv)
            for z in (zf, -zf):
                sx, sz, txz = Qf @ (e0 + z * kap)
                c, r = (sx + sz) / 2, math.hypot((sx - sz) / 2, txz)
                smax = max(smax, abs(c) + r)
        # tube: bending stress at the root element
        ke, _ = fe.frame_element(nodes[0], nodes[1], k["E"], k["G"], mdl.A_t, mdl.I_t, mdl.I_t, mdl.J_t, 1.0)
        fn = ke @ np.concatenate([u[0:6], u[6:12]])
        m_root = math.hypot(fn[3], fn[4])
        st_tube = m_root * g["od"] / 2 / mdl.I_t
        f_strut = -s["k"] * float(np.dot(s["n"], u[6 * s["node"]:6 * s["node"] + 3]))   # + = compression
        d_foot = max(float(np.linalg.norm(u[6 * n:6 * n + 3])) for n in foot)
        s_edge = 0.0
        for n1, n2, stf in mdl.stf_elems:
            ke, _ = fe.frame_element(nodes[n1], nodes[n2], stf["E"], stf["G"], stf["A"], 1e-15, stf["I_out"], stf["J"], 1.0)
            fe_ = ke @ np.concatenate([u[6 * n1:6 * n1 + 6], u[6 * n2:6 * n2 + 6]])
            m_out = max(abs(fe_[5]), abs(fe_[11]))
            s_edge = max(s_edge, m_out * stf["d"] / 2 / stf["I_out"] + abs(fe_[0]) / stf["A"])
        out[f"edge_{cname}"] = s_edge * k["sf"]
        out[f"face_{cname}"] = smax * k["sf"]
        out[f"tube_{cname}"] = st_tube * k["sf"]
        out[f"mroot_{cname}"] = m_root
        out[f"strut_{cname}"] = f_strut
        out[f"dfoot_{cname}"] = d_foot
        if smax > worst_face:
            worst_face, worst_case = smax, cname
    face_ult = max(out[f"face_{c}"] for c in cases)
    tube_ult = max(out[f"tube_{c}"] for c in cases)
    edge_ult = max(out[f"edge_{c}"] for c in cases)
    strut_c = max(max(out[f"strut_{c}"] for c in cases), 0.0) * k["sf"] * k["fit"]
    strut_t = max(-min(out[f"strut_{c}"] for c in cases), 0.0) * k["sf"] * k["fit"]
    I_s = g["s_w"] * g["s_t"] ** 3 / 12
    L_s = s["L"]
    p_cr = math.pi ** 2 * g["e_strip"] * I_s / L_s ** 2
    return {"face_ult_pa": face_ult, "ms_face": k["s_face"] / face_ult - 1,
            "face_L4_pa": out["face_L4"], "face_L1_pa": out["face_L1"], "face_G2_pa": out["face_G2"],
            "tube_ult_pa": tube_ult, "ms_tube": k["s_cf"] / tube_ult - 1,
            "edge_ult_pa": edge_ult, "ms_edge": k["s_cf"] / max(edge_ult, 1.0) - 1,
            "strut_comp_design_n": strut_c, "strut_tens_design_n": strut_t, "strut_pcr_n": p_cr,
            "ms_strut_buckling": p_cr / max(strut_c, 1e-9) - 1, "strut_len_m": L_s,
            "dfoot_L4_m": out["dfoot_L4"], "mroot_G2_nm": out["mroot_G2"], "mroot_L4_nm": out["mroot_L4"],
            "strut_G2_n": out["strut_G2"], "strut_L4_n": out["strut_L4"]}


_static_calc("CALC-C4-STATIC-2L", "Fin, tube and brace strength, 2-layer fin", P + "fins.layers")
_static_calc("CALC-C4-STATIC-1L", "Fin, tube and brace strength, 1-layer fin", "ASM-C4-ONE-LAYER")


@kit.calc("CALC-C4-BLOCK", title="Through-core block: tube bore, spar bore, web, bonds",
          inputs={"m_des_c1": "CL-C1-FINJOINT-M-DESIGN", "m_task": "ASM-C4-FINJOINT-M-TASK", "f_ult": "CL-C1-FINJOINT-F-ULT",
                  "my_lim": "ASM-C4-FINJOINT-MY", "sf": SF, "fit": FIT, "prt": PRT, "d": P + "fins.tube.od_m",
                  "d_spar": P + "wing.spar.od_m", "h": "ASM-C4-CORE-T-TUBE", "W": "ASM-C4-BLOCK-W",
                  "x_t": P + "fins.tube.x_m", "x_s": P + "wing.spar.x_m", "s_brg": "ASM-C4-PETG-BEARING",
                  "s_ten": "ASM-C4-PETG-TENSILE", "s_sh": "ASM-C4-PETG-SHEAR", "s_bond": "ASM-C4-BOND-SHEAR",
                  "rho": "ASM-C4-PETG-RHO", "fill": "ASM-C4-BLOCK-FILL"},
          units={"m_des_c1": "N m", "m_task": "N m", "f_ult": "N", "my_lim": "N m", "sf": "-", "fit": "-", "prt": "-",
                 "d": "m", "d_spar": "m", "h": "m", "W": "m", "x_t": "m", "x_s": "m", "s_brg": "Pa", "s_ten": "Pa",
                 "s_sh": "Pa", "s_bond": "Pa", "rho": "kg/m3", "fill": "-"},
          equation="M = max(C1 design, m_task sf fit prt); F = f_ult fit prt ; tube bore: s = 6M/(d h^2) + F/(d h); "
                   "shear-out tau = (1.5 M / h)/(e h), e = (W - d)/2 ; spar bore: s = 6M/(d W^2) + F/(d W); "
                   "web (W x h): s = 6M/(W h^2), tau = M/(0.21 W h^2) ; bond torsion tau = 2 My sf fit prt/(pi d^2 W); "
                   "bond axial tau = F/(pi d h)", cites=["SRC-C4-ROARK"], tol=1e-6,
          assumes=["ASM-C4-PETG-BEARING", "ASM-C4-PETG-SHEAR", "ASM-C4-BOND-SHEAR", "ASM-C4-BLOCK-W"])
def block(m_des_c1, m_task, f_ult, my_lim, sf, fit, prt, d, d_spar, h, W, x_t, x_s, s_brg, s_ten, s_sh, s_bond, rho,
          fill):
    M = max(m_des_c1, m_task * sf * fit * prt)
    F = f_ult * fit * prt
    s_tb = 6 * M / (d * h * h) + F / (d * h)
    e = (W - d) / 2
    tau_so = (1.5 * M / h) / (e * h)
    s_sb = 6 * M / (d_spar * W * W) + F / (d_spar * W)
    s_web = 6 * M / (W * h * h)
    tau_web = M / (0.21 * W * h * h)
    tau_bt = 2 * my_lim * sf * fit * prt / (math.pi * d_spar ** 2 * W)
    tau_ba = F / (math.pi * d * h)
    L = (x_s - x_t) + d / 2 + d_spar / 2 + 2 * 0.006           # 6 mm wall outside each bore
    vol = L * W * h - math.pi / 4 * d * d * h - math.pi / 4 * d_spar ** 2 * W
    ms = {"ms_tube_bore": s_brg / s_tb - 1, "ms_shear_out": s_sh / tau_so - 1, "ms_spar_bore": s_brg / s_sb - 1,
          "ms_web_bend": s_ten / s_web - 1, "ms_web_torsion": s_sh / tau_web - 1, "ms_bond_torsion": s_bond / tau_bt - 1,
          "ms_bond_axial": s_bond / tau_ba - 1}
    return {"M_design_nm": M, "F_design_n": F, "s_tube_bore_pa": s_tb, "tau_shear_out_pa": tau_so,
            "s_spar_bore_pa": s_sb, "s_web_pa": s_web, "tau_web_pa": tau_web, "tau_bond_torsion_pa": tau_bt,
            "tau_bond_axial_pa": tau_ba, **ms, "ms_min": min(ms.values()), "block_len_m": L,
            "mass_kg": vol * rho * fill, "spar_couple_n": 1.5 * M / W, "tube_couple_n": 1.5 * M / h}


@kit.calc("CALC-C4-MASS", title="Fins mass change for the recommended design",
          inputs={"areal": P + "fins.areal_mass_kgm2", "chord": P + "fins.chord_m", "hh": P + "fins.half_height_m",
                  "s_w": "ASM-C4-STRUT-W", "s_t": "ASM-C4-STRUT-T", "rho_cf": "ASM-C4-CF-RHO",
                  "m_fit": "ASM-C4-STRUT-FIT-MASS", "L_s": "CL-C4-STRUT-LEN", "m_block": "CL-C4-BLOCK-MASS",
                  "e_w": "ASM-C4-EDGE-W", "e_t": "ASM-C4-EDGE-T", "x_t": P + "fins.tube.x_m", "od": P + "fins.tube.od_m",
                  "x_te": P + "fins.te_x_m"},
          units={"areal": "kg/m2", "chord": "m", "hh": "m", "s_w": "m", "s_t": "m", "rho_cf": "kg/m3", "m_fit": "kg",
                 "L_s": "m", "m_block": "kg", "e_w": "m", "e_t": "m", "x_t": "m", "od": "m", "x_te": "m"},
          equation="layer = areal c 2hh x 2 fins ; braces = 4 (w t L rho + 2 m_fit) ; edge strips = 8 e_w e_t "
                   "(x_te - x_t - od/2) rho ; blocks = 2 (m_block - 0.020 allocated)",
          tol=1e-6)
def fins_mass(areal, chord, hh, s_w, s_t, rho_cf, m_fit, L_s, m_block, e_w, e_t, x_t, od, x_te):
    layer = areal * chord * 2 * hh * 2
    braces = 4 * (s_w * s_t * L_s * rho_cf + 2 * m_fit)
    edges = 8 * e_w * e_t * (x_te - x_t - od / 2) * rho_cf
    blocks = 2 * (m_block - 0.020)
    add = braces + edges + blocks
    return {"one_layer_saving_g": layer * 1000, "braces_g": braces * 1000, "edges_g": edges * 1000,
            "blocks_delta_g": blocks * 1000, "rec_delta_g": add * 1000, "rec_1l_delta_g": (add - layer) * 1000}


# ====================================================================== claims
R_VIB, R_SM, R_JNT = ["R-VIBRATION"], ["R-STRUCT-MARGIN"], ["R-FIN-TUBE-JOINT"]
TUBES, HALF = ["FIN-002-L", "FIN-002-R"], ["FIN-001-UR", "FIN-001-UL", "FIN-001-LR", "FIN-001-LL"]
TAP = "Tap test of one finished fin quarter on the bench (T-C4-TAP): FFT of the FC IMU raw log; hover VIBE < 30 m/s2, Clip 0."

kit.claim("CL-C4-FE-CHECK-TUBE", "FE vs closed form, bare tube + tip mass", calc="CALC-C4-FE-CHECK",
          output="err_tube", unit="-", limit=("<=", 0.01), cites=["SRC-C4-BLEVINS"],
          how="Re-run fin_structures.py; reproduces J1's CALC-J1-TUBE-MODE formula with the clamp at the chord plane.")
kit.claim("CL-C4-FE-CHECK-PLATE", "FE vs Leissa, cantilever plate", calc="CALC-C4-FE-CHECK", output="err_plate", unit="-",
          limit=("<=", 0.02), cites=["SRC-C4-LEISSA"], how="Re-run fin_structures.py (16 x 16 mesh).")
kit.claim("CL-C4-MESH-CONV", "Mesh convergence of the station modes", calc="CALC-C4-CONVERGENCE", output="change",
          unit="-", limit=("<=", 0.03), how="Three meshes 6x5, 12x10, 24x20; 12x10 is used for every claim.")
kit.claim("CL-C4-F1-1LB", "First station mode, recommended 1-layer fin + brace + edge strips", calc="CALC-C4-MODES-1LB",
          output="f_st1", unit="Hz", parts=TUBES + HALF, how=TAP)

kit.claim("CL-C4-F-LT-2L", "First station mode (lateral-torsion), current design (2-layer fin, no brace)",
          calc="CALC-C4-MODES-2L", output="f_st1", unit="Hz", parts=TUBES + HALF, how=TAP,
          note="Tube bends out of the fin plane and twists; the foam-board fin adds < 3 % here.")
kit.claim("CL-C4-F-FA-2L", "Second station mode (fore-aft, fin as shear web), current design", calc="CALC-C4-MODES-2L",
          output="f_st2",
          unit="Hz", parts=TUBES + HALF, how=TAP, note="Bare tube 180 Hz; the bonded fin lifts it to ~330 Hz.")
kit.claim("CL-C4-SEP-2L", "Mode separation, current design", calc="CALC-C4-MODES-2L", output="sep_op", unit="-",
          limit=(">=", LIMIT_SEP), verifies=R_VIB, parts=TUBES + HALF, how=TAP,
          note="FAILS: the lateral-torsion mode sits at ~149 Hz, 4 % from 1P at the F4 cap and 17 % below 2P hover.")
kit.claim("CL-C4-SEP-1L", "Mode separation, 1-layer fin, no brace", calc="CALC-C4-MODES-1L", output="sep_op", unit="-",
          limit=(">=", LIMIT_SEP), verifies=R_VIB, parts=TUBES + HALF, how=TAP)
kit.claim("CL-C4-F-LT-REC", "First station mode, braced design (layers per params.json)", calc="CALC-C4-MODES-REC", output="f_st1",
          unit="Hz", parts=TUBES + HALF, how=TAP)
kit.claim("CL-C4-F-FA-REC", "Second station mode, braced design (layers per params.json)", calc="CALC-C4-MODES-REC", output="f_st2", unit="Hz",
          parts=TUBES + HALF, how=TAP)
kit.claim("CL-C4-F-PANEL-REC", "First fin-panel mode (TE tip with the foot)", calc="CALC-C4-MODES-REC", output="f_panel",
          unit="Hz", parts=HALF, how="Tap the fin TE tip with the foot fitted; expect 50-70 Hz, below the 1P band.",
          note="Local flapping of the free TE corner; < 2 % of its energy reaches the station. Below the forcing band.")
kit.claim("CL-C4-SEP-REC", "Mode separation, braced design, layers per params.json (nominal E, G)", calc="CALC-C4-MODES-REC",
          output="sep_op", unit="-", limit=(">=", LIMIT_SEP), verifies=R_VIB, parts=TUBES + HALF, how=TAP)
kit.claim("CL-C4-SEP-REC-WORST", "Mode separation, braced design, layers per params.json, worst tube E/G corner", calc="CALC-C4-WORST-REC",
          output="sep_op_worst", unit="-", limit=(">=", LIMIT_SEP), verifies=R_VIB, parts=TUBES,
          how="T-C4-TUBE-BEND and T-C4-TUBE-TORSION on the US-stock tube (I1), then T-C4-TAP.")
kit.claim("CL-C4-SEP-REC-WHIRL", "Whirl separation incl. prop gyroscopics, braced design (layers per params.json)", calc="CALC-C4-CAMPBELL",
          output="sep_whirl", unit="-", limit=(">=", LIMIT_SEP), verifies=R_VIB, parts=TUBES, how=TAP)
kit.claim("CL-C4-SEP-BAND-REC", "Separation from the whole 80-330 Hz band (B4 target)", calc="CALC-C4-MODES-REC",
          output="sep_band", unit="-", limit=(">=", LIMIT_SEP), parts=TUBES,
          how="Needs every station mode >= 396 Hz. R-VIBRATION (A2) is met on the operating points instead, with an "
              "rpm-tracking harmonic notch as the backup (F4).",
          note="With 2 layers the first station mode is 392 Hz: 1 % short of the band rule. A2's R-VIBRATION is the basis.")
kit.claim("CL-C4-SEP-BAND-1LB", "Separation from the 80-330 Hz band, recommended 1-layer design", calc="CALC-C4-MODES-1LB",
          output="sep_band", unit="-", limit=(">=", LIMIT_SEP), parts=TUBES,
          how="As CL-C4-SEP-BAND-REC.", note="FAILS (first station mode ~296 Hz inside the band); passes R-VIBRATION.")
kit.claim("CL-C4-SEP-1LB", "Mode separation, recommended 1-layer fin + brace + edge strips (nominal)", calc="CALC-C4-MODES-1LB", output="sep_op",
          unit="-", limit=(">=", LIMIT_SEP), verifies=R_VIB, parts=TUBES + HALF, how=TAP)
kit.claim("CL-C4-SEP-1LB-WORST", "Mode separation, recommended 1-layer fin + brace + edge strips, worst tube E/G corner",
          calc="CALC-C4-WORST-1LB", output="sep_op_worst", unit="-", limit=(">=", LIMIT_SEP), verifies=R_VIB,
          parts=TUBES, how="Passes only if the measured tube E and G are near nominal (T-C4-TUBE-BEND/TORSION).")

for tag, cid in (("2L", "CALC-C4-STATIC-2L"), ("1L", "CALC-C4-STATIC-1L")):
    kit.claim(f"CL-C4-MS-FACE-{tag}", f"Fin face margin, {tag} fin with brace + edge strips, worst of L1/L4/L5/G2/H2",
              calc=cid, output="ms_face",
              unit="-", limit=(">=", 0.0), verifies=R_SM, parts=HALF,
              how="Foam-board coupon bend test (T-C4-BOARD-COUPON) for the face allowable; proof-load one fin quarter "
                  "to 1.5 x L4 at the foot (T-C4-FIN-PROOF).")
kit.claim("CL-C4-MS-EDGE", "Fin edge-strip margin (1-layer fin, L4 governs)", calc="CALC-C4-STATIC-1L", output="ms_edge",
          unit="-", limit=(">=", 0.0), verifies=R_SM, parts=HALF, how="T-C4-FIN-PROOF.")
kit.claim("CL-C4-MS-TUBE", "Motor tube bending margin at the block face", calc="CALC-C4-STATIC-1L", output="ms_tube",
          unit="-", limit=(">=", 0.0), verifies=R_SM, parts=TUBES, how="T-C4-FIN-PROOF (G2 load at the tube end).")
kit.claim("CL-C4-MS-STRUT", "Brace buckling margin (design load incl. fitting factor)", calc="CALC-C4-STATIC-2L",
          output="ms_strut_buckling", unit="-", limit=(">=", 0.0), verifies=R_SM, parts=TUBES,
          how="Proof-load G2 at the tube end with the brace fitted; no visible bow.")
kit.claim("CL-C4-STRUT-LEN", "Brace length", calc="CALC-C4-STATIC-2L", output="strut_len_m", unit="m",
          how="D3 CAD.")
kit.claim("CL-C4-FOOT-DEFL-L4", "Foot deflection under L4 (limit), 1-layer fin", calc="CALC-C4-STATIC-1L", output="dfoot_L4_m",
          unit="m", parts=HALF, how="T-C4-FIN-PROOF: dial gauge at the foot.")
kit.claim("CL-C4-BLOCK-M-DESIGN", "Through-core block design moment", calc="CALC-C4-BLOCK", output="M_design_nm",
          unit="N m", parts=["FIN-004-L", "FIN-004-R"], how="C1 G2 / the A1 action value, x 1.5 x 1.15 x 1.25.")
kit.claim("CL-C4-BLOCK-MS", "Through-core block minimum margin", calc="CALC-C4-BLOCK", output="ms_min", unit="-",
          limit=(">=", 0.0), verifies=R_JNT + R_SM, parts=["FIN-004-L", "FIN-004-R"],
          how="Proof test: hang 2 x 1.5 x 51 N (G2 ultimate, printed factor) from one upper tube end of a block bonded "
              "in a core offcut (T-C4-BLOCK-PROOF); C6 bond coupons for ASM-C4-BOND-SHEAR.")
kit.claim("CL-C4-BLOCK-MASS", "Through-core block mass, each", calc="CALC-C4-BLOCK", output="mass_kg", unit="kg",
          parts=["FIN-004-L", "FIN-004-R"], how="Weigh the first print (T-A3-WEIGH-PARTS).")
kit.claim("CL-C4-SPAR-COUPLE", "Bearing couple force on the spar at each block (design)", calc="CALC-C4-BLOCK",
          output="spar_couple_n", unit="N", parts=["FIN-004-L", "FIN-004-R"],
          how="C2 checks spar wall crushing with the internal plug (CR-C4-02).")
kit.claim("CL-C4-FINS-DELTA", "Fins mass change, braced design, 2 layers kept", calc="CALC-C4-MASS",
          output="rec_delta_g", unit="g", how="A3 roll-up; weigh the braces and blocks.")
kit.claim("CL-C4-FINS-DELTA-1L", "Fins mass change, recommended 1-layer fin + braces + edge strips + blocks", calc="CALC-C4-MASS",
          output="rec_1l_delta_g", unit="g", how="A3 roll-up.")

# ====================================================================== tests (planned)
kit.test("T-C4-TUBE-BEND", "Three-point bend of the US-stock 22 x 20 tube (I1 buys, H1 runs)",
         verifies=["CL-C4-SEP-REC-WORST", "CL-C4-SEP-1LB-WORST"],
         procedure="Span 0.80 m on two 22 mm dowels, load at centre in 0.5 kg steps to 4 kg, dial gauge to 0.01 mm; "
                   "E = F L^3 / (48 I delta) with I = 3.645e-9 m4. Pass band for the recommended design: E >= 70 GPa.")
kit.test("T-C4-TUBE-TORSION", "Torsion of the same tube", verifies=["CL-C4-SEP-REC-WORST", "CL-C4-SEP-1LB-WORST"],
         procedure="Clamp 0.40 m of tube in two printed V-blocks at one end, 0.30 m lever arm at the other, 0.5-2 kg, "
                   "measure twist with a laser pointer on a wall 3 m away; G = T L / (J theta), J = 7.29e-9 m4.")
kit.test("T-C4-TAP", "Tap test of one fin quarter (tube + block + half-fin + motor + prop + brace)",
         verifies=["CL-C4-SEP-REC", "CL-C4-SEP-1LB", "CL-C4-F1-1LB", "CL-C4-F-LT-REC", "CL-C4-F-FA-REC", "CL-C4-F-PANEL-REC"],
         procedure="Block clamped in a vice via a core offcut; tap the motor bell in y and x; phone accelerometer or FC "
                   "raw IMU at 1 kHz; FFT peaks vs 1P/2P at hover, cruise, max.")
kit.test("T-C4-BOARD-COUPON", "Foam-board face coupon", verifies=["CL-C4-MS-FACE-2L", "CL-C4-MS-FACE-1L"],
         procedure="Three 50 x 300 mm strips per layer count, four-point bend, span 250 mm, load to failure: face "
                   "allowable and D. Weigh 0.1 m2 for the areal mass.")
kit.test("T-C4-FIN-PROOF", "Proof load of one fin quarter", verifies=["CL-C4-MS-FACE-2L", "CL-C4-MS-FACE-1L", "CL-C4-MS-TUBE", "CL-C4-MS-EDGE",
                                                                       "CL-C4-FOOT-DEFL-L4", "CL-C4-MS-STRUT"],
         procedure="1.5 x L4 at the foot (49 N along the fin + 25 N across), then 1.5 x G2 (77 N lateral at the tube "
                   "end); no cracking or face wrinkle; record the foot deflection.")
kit.test("T-C4-BLOCK-PROOF", "Block proof in a core offcut", verifies=["CL-C4-BLOCK-MS"],
         procedure="Block bonded on a spar stub in a 0.15 m core offcut; 0.30 m tube in the bore; hang 18 kg at 0.17 m "
                   "lever (30 N m > design 20.3 N m) for 1 min; no creak, no bond line crack.")
kit.test("T-C4-PROP-SWING", "Bifilar swing of one prop", verifies=["CL-C4-SEP-REC-WHIRL"],
         procedure="Two 0.5 m threads at the blade tips; period of 20 swings; I = m g d^2 T^2 / (16 pi^2 L).")


# ====================================================================== report data + figure
def _inputs():
    v = {n: kit.value(r) for n, r in GEOM.items()}
    return v


def campbell_svg(path, curves, rpm_ops, rpm_max_plot=10000.0, f_max=500.0):
    W, H, L, R, T, B = 1200, 560, 90, 40, 30, 60
    sx = lambda r: L + (W - L - R) * r / rpm_max_plot
    sy = lambda f: H - B - (H - B - T) * f / f_max
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, system-ui, sans-serif">']
    for p in (1, 2):                                                  # +-20 % bands around 1P and 2P
        pts = [(sx(r), sy(p * r / 60 * 1.2)) for r in (0, rpm_max_plot)] + \
              [(sx(r), sy(p * r / 60 * 0.8)) for r in (rpm_max_plot, 0)]
        o.append('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) +
                 '" fill="#E2E6EC" fill-opacity="0.6" stroke="none"/>')
    for f in range(0, int(f_max) + 1, 100):
        o.append(f'<line x1="{L}" y1="{sy(f):.1f}" x2="{W - R}" y2="{sy(f):.1f}" stroke="#E3E7ED" stroke-width="0.75"/>')
        o.append(f'<text x="{L - 10}" y="{sy(f) + 4:.1f}" font-size="12" font-family="IBM Plex Mono, monospace" '
                 f'fill="#6B7280" text-anchor="end">{f} Hz</text>')
    for r in range(0, int(rpm_max_plot) + 1, 2000):
        o.append(f'<text x="{sx(r):.1f}" y="{H - B + 20}" font-size="12" font-family="IBM Plex Mono, monospace" '
                 f'fill="#6B7280" text-anchor="middle">{r:,}'.replace(",", " ") + '</text>')
    o.append(f'<text x="{(L + W - R) / 2}" y="{H - 12}" font-size="12" fill="#4B5563" text-anchor="middle">rotor speed, rpm</text>')
    for p in (1, 2):
        r1 = min(rpm_max_plot, f_max * 60 / p)
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
            pts = " ".join(f"{sx(r):.1f},{sy(f):.1f}" for r, f in zip(rpms, fr[:, j]) if f <= f_max)
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
    nodes = {n["id"]: n for n in json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["nodes"]}
    g = _inputs()
    E0, G0 = kit.value("ASM-J1-E-TUBE"), kit.value("ASM-C4-G-TUBE")
    rpm = {k: kit.value(v) for k, v in RPM.items()}
    res = {"inputs": {**g, "E": E0, "G": G0, **rpm}, "configs": {}, "sensitivity": {}}
    configs = {"bare tube": (0, False), "1-layer fin": (1, False), "2-layer fin (current)": (2, False),
               "1-layer fin + brace + edge strips (recommended)": (1, True), "2-layer fin + brace + edge strips": (2, True)}
    for name, (lay, st) in configs.items():
        r = modal_summary(g, E0, G0, lay, st, rpm["rpm_h"], rpm["rpm_c"], rpm["rpm_x"])
        res["configs"][name] = r
        print(f"{name:36s} station modes {[round(x) for x in r['f_st'][:4]]}  panel {r['f_panel']:6.1f}  "
              f"sep {r['sep_op']:+.2f} ({r['nearest']})  band {r['sep_band']:+.2f}")
    for name, (lay, st) in (("2-layer fin (current)", (2, False)), ("1-layer fin + brace + edge strips (recommended)", (1, True)),
                            ("2-layer fin + brace + edge strips", (2, True))):
        rows = []
        for E, G in itertools.product((70e9, 100e9, 135e9), (3e9, 5e9, 10e9)):
            r = modal_summary(g, E, G, lay, st, rpm["rpm_h"], rpm["rpm_c"], rpm["rpm_x"])
            rows.append({"E_GPa": E / 1e9, "G_GPa": G / 1e9, "f_st1": r["f_st1"], "f_st2": r["f_st2"], "sep": r["sep_op"],
                         "nearest": r["nearest"]})
        res["sensitivity"][name] = rows
    # root fixity sensitivity of the recommended design (block + wing compliance)
    res["root_springs"] = []
    for lay in (2, 1):
        for kr in (2e3, 5e3, 1e4, 3e4, None):
            c = model_cfg(g, E0, G0, lay, True)
            c["k_root_rx"], c["k_root_ry"] = kr, kr
            r = station_modes(fe.build(c))
            res["root_springs"].append({"layers": lay, "k_root_nm_per_rad": kr, "f_st1": r["f_st1"],
                                        "f_st2": r["f_st2"]})
            print(f"root spring {lay}L k {kr}: station modes {r['f_st1']:.0f} / {r['f_st2']:.0f} Hz")
    # Campbell curves (station whirl) for the figure
    rpms = np.linspace(0, 10000, 41)
    curves = {}
    for label, lay, st, colour, dash in (("current: 2-layer fin, no brace", 2, False, "#6B7280", "8 5"),
                                         ("2-layer fin + brace + edge strips", 2, True, "#9AA4B1", None),
                                         ("recommended: 1-layer fin + brace + edge strips", 1, True, "#1F5FC7", None)):
        mdl = fe.build(model_cfg(g, E0, G0, lay, st))
        fr = [(_station_whirl(mdl, g["ip"] + g["i_bell"], r) + [np.nan] * 4)[:4] for r in rpms]
        curves[label] = (rpms, np.array(fr), colour, dash)
        res.setdefault("campbell", {})[label] = {"rpm": rpms.tolist(), "f_hz": np.array(fr).tolist()}
    campbell_svg(HERE / "fig-c4-campbell.svg", curves,
                 {"hover": rpm["rpm_h"], "cruise": rpm["rpm_c"], "F4 cap": rpm["rpm_x"]})
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "results.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")
    print("wrote out/results.json and fig-c4-campbell.svg")
