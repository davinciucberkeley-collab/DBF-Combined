"""D5 landing designer: crushable fin-tip feet (GER) for the K09-L quad tailsitter, revision D5-R4 (CR-A1-34, D-30; C5-R3 cartridges).

Run:  python -I redesign/team/D5/feet_calc.py
Writes claims.json beside this file. Every number is a pure function of params.json (P:...), the landing subsystem
params (P:landing.*, redesign/subsystems/landing/params.json), other roles' claims and the assumptions below. The foot
geometry and body volumes come from the CAD module's own geometry() (subsystems/landing/fusion/landing.py), so the
calc and the CAD cannot drift; __main__ also builds the module on the stub backend and asserts the volumes agree.

R3 asks (CR-A1-34): foot 48 mm, >= 38 mm stroke (flange-to-rim gap), biased cartridges colour-marked (x1.077 upper,
x0.923 lower), shoe for the 9.6 mm board plus the edge-strip ends, >= 6 mm snap fingers, TE corner caps, pad contact
at z +/-0.218, mass against 43 g, FIN-001-<st> ids, CG-jig patch at |y| 0.45 left free.
R4 (CR-C5-10 revised at C5-R3): every cartridge segment pre-crushed 1 mm (peak = plateau, ASM-C5-PRECRUSH-PEAK), plateau
upper 39.4 N / lower 35.6 N (mean 37.5 N, bias x1.05): type U 17.3 x 13.3 mm solid, type L the same with a 7/32 in bore.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RED = HERE.parents[1]
sys.path.insert(0, str(RED / "proofs"))                          # python -I adds no paths
sys.path.insert(0, str(RED / "fusion"))
sys.path.insert(0, str(RED / "subsystems" / "landing" / "fusion"))
import proofkit as pk  # noqa: E402
import k09kit as k9  # noqa: E402
import landing  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/landing/params.json"])
P = "P:"
LP = "P:landing."

# ---------------------------------------------------------------- sources and assumptions
kit.source("SRC-D5-OC-F250", "Owens Corning FOAMULAR 250 XPS product data sheet (compressive strength 25 psi, ASTM D1621)",
           "datasheet", url="https://www.owenscorning.com/en-us/insulation/products/foamular-250",
           note="25 psi = 172 kPa at yield or 10 % deformation, through the board thickness; not yet compared with "
                "the sheet for the board the team buys", status="UNVERIFIED")
kit.source("SRC-D5-TOOLBOX-MU", "Engineering ToolBox, friction coefficients (rubber on dry concrete 0.6-0.85)",
           "web", url="https://www.engineeringtoolbox.com/friction-coefficients-d_778.html", status="UNVERIFIED")
kit.source("SRC-D5-NEOPRENE", "Neoprene rubber sheet 1/16 in, 40A, adhesive back (McMaster-Carr neoprene sheets)",
           "web", url="https://www.mcmaster.com/neoprene-rubber-sheets/", status="UNVERIFIED",
           note="density ~1.3 g/cm3; choose a 12 x 12 in adhesive-back sheet; part number at order time (I1)")
kit.source("SRC-D5-PETG", "Generic PETG filament data (density 1.27 g/cm3, printed XY tensile ~40-50 MPa)",
           "web", url="https://www.prusa3d.com/page/petg_234/", status="UNVERIFIED")
kit.source("SRC-D5-TPU", "Generic TPU 95A filament data (density 1.21 g/cm3)", "web",
           url="https://www.prusa3d.com/page/flexible-materials_243/", status="UNVERIFIED")
kit.source("SRC-D5-SNAP", "Bayer/Covestro snap-fit design guide: cantilever strain eps = 1.5 t y / L^2", "handbook",
           url="https://www.covestro.com/en/products/brands/makrolon", status="UNVERIFIED",
           note="same formula as C6's CALC-C6-SNAP")

kit.assumption("ASM-D5-XPS-PLATEAU", "XPS crush plateau 172 kPa",
               "Crush plateau stress of F-250 XPS loaded through the board thickness equals its 10 % compressive "
               "strength and stays flat to the densification strain",
               basis="FOAMULAR 250 datasheet 25 psi; closed-cell XPS plateau is flat within ~10 % from 5 to 50 % "
                     "strain. The coupon test T-D5-COUPON replaces it; the cartridge section is the tuning knob",
               value=172000.0, unit="Pa", status="UNVERIFIED", cites=["SRC-D5-OC-F250", "SRC-XPS-F250"])
kit.assumption("ASM-D5-YIELD-STRAIN", "Strain to reach the plateau 5 %",
               "Elastic ramp of the XPS column ends at 5 % strain; half of that ramp is lost against a flat-force model",
               basis="XPS modulus ~8-10 MPa vs 172 kPa plateau gives ~2 %; 5 % covers the knee", value=0.05, unit="-",
               status="UNVERIFIED")
kit.assumption("ASM-D5-XPS-ELASTIC-STRAIN", "Recoverable strain of the pre-crushed XPS column 2 %",
               "Below the plateau the pre-crushed XPS column is elastic to ~2 % strain and springs back; only that "
               "energy is returned in a normal landing, the rest is permanent crush",
               basis="plateau 172 kPa / modulus ~8-10 MPa (XPS) = 1.7-2.2 %; R3 credited the 5 % knee (ASM-D5-YIELD-"
                     "STRAIN), which includes plastic crush and over-stated the life. H2 landing log replaces it",
               value=0.02, unit="-", status="UNVERIFIED")
kit.assumption("ASM-D5-DENSIFY", "Usable strain before densification 0.55",
               "The XPS force stays on its plateau to 55 % strain", basis="closed-cell XPS densifies at 0.6-0.7",
               value=0.55, unit="-", status="UNVERIFIED")
kit.assumption("ASM-D5-NORMAL-SINK", "Normal touchdown 0.5 m/s with rotor lift = weight",
               "Routine landings touch down at Q_LAND_SPEED 0.5 m/s with the rotors still carrying the weight",
               basis="params requirements.landing_sink_ms note (3 x Q_LAND_SPEED 0.5 m/s); F4 sets it",
               value=0.5, unit="m/s", status="PROPOSED")
kit.assumption("ASM-D5-PAD-MU", "Neoprene pad friction 0.7 on dry concrete/asphalt",
               "Static friction of a 40A neoprene pad on dry concrete or asphalt", basis="Engineering ToolBox rubber/"
               "concrete 0.6-0.85; grass is lower and unmeasured. Tilt-board slide test T-D5-PAD-MU",
               value=0.7, unit="-", status="UNVERIFIED", cites=["SRC-D5-TOOLBOX-MU"])
kit.assumption("ASM-D5-PETG-SIGMA", "Printed PETG allowable 40 MPa", "Printed PETG bending allowable (XY, 100 % walls)",
               basis="filament data 40-50 MPa; low end for layer adhesion", value=40.0e6, unit="Pa", status="UNVERIFIED",
               cites=["SRC-D5-PETG"])
kit.assumption("ASM-D5-BOND-TAU", "Epoxy to paper-faced foam board 0.20 MPa shear",
               "Failure of an epoxy bond on foam-board paper facing occurs in the paper/foam at ~0.2 MPa shear",
               basis="estimate; C6 halves it (ASM-C6-FOAM-KD) for design, CR-C6-12", value=0.20e6, unit="Pa",
               status="UNVERIFIED")
kit.assumption("ASM-D5-FIT-FACTOR", "Printed/bonded fitting factor 1.4375 on ultimate",
               "C1 printed/bonded design value = ultimate x 1.15 x 1.25", basis="team/C1/data/envelope.json#joints.J-FOOT "
               "(86.8 N / 60.4 N)", value=1.4375, unit="-", status="PROPOSED")
kit.assumption("ASM-D5-ULT-FACTOR", "Ultimate = 1.5 x limit", "Ultimate load factor on limit loads",
               basis="C1 LOADS.md convention", value=1.5, unit="-", status="PROPOSED")
kit.assumption("ASM-D5-REPLACE-MIN", "Insert swap 3 min",
               "Press the two snap fingers through the windows, pull the insert out, push a pre-glued spare in until "
               "both click", basis="no tools, no cure; estimate until timed (T-D5-REPLACE)", value=3.0, unit="min",
               status="UNVERIFIED")


# ---------------------------------------------------------------- geometry (the CAD module's own stack)
GEOM_IN = {k: P + key for k, key in landing.SHARED.items()}
GEOM_IN.update({k: LP + key for k, key in landing.LOCAL.items()})
GEOM_IN.update({"airfoil": P + "wing.airfoil", "t_c": P + "wing.t_c"})
GEOM_UNITS = {k: "m" for k in GEOM_IN if k not in ("layers", "segs", "airfoil", "t_c")}


def _n(kw):
    return {k: kw[k] for k in list(landing.SHARED) + list(landing.LOCAL)}


def _coords(kw):
    return k9.section({"wing": {"airfoil": {"value": kw["airfoil"]}, "t_c": {"value": kw["t_c"]}}})[0]


@kit.calc("CALC-D5-GEOM", title="Foot stack, fin step and sizes (landing.py geometry())", inputs=GEOM_IN,
          units=GEOM_UNITS,
          equation="x_g = c + foot ; flange = x_g - pad - t_fl ; rim end = flange - stroke ; tine open = rim end - "
                   "engage ; back wall = open - stroke - 1 mm ; L_cart = flange - back wall ; sections: cartridge + 2 cf "
                   "-> tine + 2 w -> sleeve + 2 cs + 2 w ; sleeve roof = z_outer - lip, floor = roof - sleeve z ; fin "
                   "step z = floor - glue, x = back wall - glue ; z_eff = z_outer - r ; TE clear = foot - stroke")
def geom(**kw):
    s = landing.stack(_n(kw))
    return {"x_ground_m": s["x_g"], "x_flange0_m": s["x_flange"][0], "x_sleeve_end_m": s["x_slv_end"],
            "x_piston_open_m": s["x_open"], "x_back_wall_in_m": s["x_bw_in"], "x_shoe_front_m": s["x_bw"][0],
            "cart_len_m": s["L_cart"], "piston_out_m": list(s["pist_out"]), "sleeve_out_m": list(s["slv_out"]),
            "z_sleeve_m": list(s["z_slv"]), "z_step_m": s["z_step"], "x_step_m": s["x_notch"],
            "step_depth_m": s["notch_depth"], "shoe_len_on_fin_m": s["shoe_len_on_fin"],
            "flange_overhang_m": kw["z_outer"] - s["z_bore"][1], "z_contact_eff_m": kw["z_outer"] - kw["edge_r"],
            "t_fin_m": s["t_fin"], "sleeve_len_m": s["x_slv_end"] - s["x_bw_in"],
            "tine_len_m": s["x_flange"][0] - s["x_open"], "window_len_m": s["x_win"][1] - s["x_win"][0],
            "lever_m": s["x_g"] - s["x_slv_end"], "te_clear_crushed_m": s["te_clear_crushed"],
            "stroke_m": kw["stroke"], "rim_clear_of_te_m": s["x_rim"][0] - kw["te"],
            "pad_y_m": s["slv_out"][0], "pad_z_m": kw["z_outer"] - s["z_slv"][0]}


# ---------------------------------------------------------------- crush energy, biased cartridges
CRUSH_IN = {"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "v": P + "requirements.landing_sink_ms",
            "lam": "ASM-C1-LAND-LIFT", "sigma": "ASM-D5-XPS-PLATEAU", "k_pk": "ASM-C5-PRECRUSH-PEAK",
            "eps_y": "ASM-D5-YIELD-STRAIN", "eps_d": "ASM-D5-DENSIFY", "fy": LP + "cartridge.section_y_m",
            "fz": LP + "cartridge.section_z_m", "d": LP + "cartridge.bore_lower_d_m", "L": "CL-D5-CART-LEN",
            "s_max": "CL-D5-STROKE-AVAIL", "v_norm": "ASM-D5-NORMAL-SINK", "mark": LP + "piston.replace_mark_m",
            "eps_e": "ASM-D5-XPS-ELASTIC-STRAIN", "guard": "ASM-C5-DROP-GUARD", "s_pair": "CL-C5-DROP-PAIR-PITCH", "bias_t": "CL-C5-CART-BIAS-UPPER",
            "k_ult": "ASM-D5-ULT-FACTOR", "pre": LP + "cartridge.precrush_m", "F_t": "ASM-C5-F-PLATEAU-PROP"}


@kit.calc("CALC-D5-CRUSH", title="Constant-force crush, biased cartridges (type U upper, type L lower)",
          inputs=CRUSH_IN,
          units={"m": "kg", "g": "m/s2", "v": "m/s", "fy": "m", "fz": "m", "d": "m", "L": "m", "s_max": "m",
                 "sigma": "Pa", "v_norm": "m/s", "mark": "m", "guard": "m", "s_pair": "m", "pre": "m", "F_t": "N"},
          equation="A_U = fy fz ; A_L = A_U - pi d^2/4 ; F_U,L = sigma A ; F_mean = (F_U + F_L)/2 ; bias = F_U / F_mean ; "
                   "level: 4 F_mean (s - eps_y L/2) = m v^2/2 + (1 - lam) m g s ; n = 4 k F_mean / (m g) ; usable = "
                   "s_max - guard >= C5 pair-first stroke ; normal set = (m v_n^2/2 - 4 F_mean eps_e L/2) / (4 F_mean) ; "
                   "no-set sink = sqrt(2 E_el / m) ; strain = (pre + s_max) / (L + pre) (pre-crush counted) ; mark margin = "
                   "s_max - guard - mark - s_pair ; landings = mark / set ; mean error = F_mean / F_C5 - 1")
def crush(m, g, v, lam, sigma, k_pk, eps_y, eps_e, eps_d, fy, fz, d, L, s_max, v_norm, mark, guard, s_pair, bias_t, k_ult,
          pre, F_t):
    W = m * g
    A_U = fy * fz
    A_L = A_U - math.pi * d * d / 4
    F_U, F_L = sigma * A_U, sigma * A_L
    F_p = (F_U + F_L) / 2
    F_pk = k_pk * F_p
    KE = 0.5 * m * v * v
    s = (KE + 4 * F_p * eps_y * L / 2) / (4 * F_p - (1 - lam) * W)
    eta = 4 * F_p * (s - eps_y * L / 2) / (4 * F_pk * s)
    E_el = 4 * 0.5 * F_p * eps_e * L                          # recoverable energy, four columns to the plateau
    set_norm = max(0.0, (0.5 * m * v_norm ** 2 - E_el) / (4 * F_p))
    bias = F_U / F_p
    return {"area_upper_m2": A_U, "area_lower_m2": A_L, "F_upper_N": F_U, "F_lower_N": F_L,
            "F_plateau_N": F_p, "F_peak_N": F_pk, "F_peak_upper_N": k_pk * F_U, "F_ult_upper_N": k_ult * k_pk * F_U,
            "bias_upper": bias, "bias_err": abs(bias - bias_t), "ratio_UL": F_U / F_L, "KE_J": KE,
            "stroke_used_m": s, "eta": eta, "n_land": 4 * F_pk / W, "usable_m": s_max - guard,
            "strain_full": (pre + s_max) / (L + pre), "strain_margin": eps_d - (pre + s_max) / (L + pre),
            "set_normal_m": set_norm, "E_elastic_J": E_el, "v_no_set_ms": math.sqrt(2 * E_el / m), "mean_err": abs(F_p / F_t - 1), "cut_seg_len_m": L / 2 + pre / 2,
            "mark_margin_m": s_max - guard - mark - s_pair, "landings_per_cartridge": mark / set_norm
            if set_norm > 0 else 999.0}


# ---------------------------------------------------------------- tip-over
@kit.calc("CALC-D5-TIPOVER", title="Narrow-axis tip-over about the pad edges, z_cg subtracted (CR-C5-01)",
          inputs={"c": P + "wing.chord_m", "foot": P + "cg.foot_height_m", "x_cg": P + "cg.x_target_m",
                  "z_cg": P + "cg.z_target_m", "x_rng": P + "cg.x_range_m", "z_rng": P + "cg.z_range_m",
                  "z_eff": "CL-D5-CONTACT-Z", "y_fin": P + "fins.y_m"},
          units={"c": "m", "foot": "m", "x_cg": "m", "z_cg": "m", "x_rng": "m", "z_rng": "m", "z_eff": "m",
                 "y_fin": "m"},
          equation="h = c + foot - x_cg ; narrow = atan((z_eff - z_cg) / h) ; worst = atan((z_eff - z_cg,max) / "
                   "(c + foot - x_cg,min)) ; wide = atan(y_fin / h)")
def tipover(c, foot, x_cg, z_cg, x_rng, z_rng, z_eff, y_fin):
    h = c + foot - x_cg
    hc = c + foot - min(x_rng)
    return {"cg_height_m": h, "narrow_deg": math.degrees(math.atan((z_eff - z_cg) / h)),
            "corner_deg": math.degrees(math.atan((z_eff - max(z_rng)) / hc)),
            "wide_deg": math.degrees(math.atan(y_fin / h))}


# ---------------------------------------------------------------- mass (volumes from the CAD bodies)
MASS_IN = dict(GEOM_IN)
MASS_IN.update({"rho_petg": LP + "materials.petg_density_kgm3", "rho_tpu": LP + "materials.tpu_density_kgm3",
                "rho_neo": LP + "materials.neoprene_density_kgm3", "rho_xps": P + "wing.core.density_kgm3",
                "glue_g": LP + "materials.glue_g_per_foot", "tape": LP + "cap.tape_g",
                "alloc": P + "mass.allocation_g.landing"})
MASS_UNITS = dict(GEOM_UNITS)
MASS_UNITS.update({"rho_petg": "kg/m3", "rho_tpu": "kg/m3", "rho_neo": "kg/m3", "rho_xps": "kg/m3",
                   "glue_g": "g", "tape": "g", "alloc": "g"})


@kit.calc("CALC-D5-MASS", title="Landing mass from the CAD body volumes", inputs=MASS_IN, units=MASS_UNITS,
          equation="m = rho V (V = landing.volume(bodies)) ; shoe + epoxy 0.35 g ; cartridge + CA 0.05 g ; cap + tape ; "
                   "total = 2 upper feet + 2 lower feet + 2 caps")
def mass(**kw):
    B = landing.bodies(_n(kw), _coords(kw))
    V = {k: landing.volume(v) for k, v in B.items() if not k.startswith("_")}
    g = 1000.0
    epoxy, ca = kw["glue_g"] - 0.05, 0.05
    shoe = V["GER-001"] * kw["rho_petg"] * g + epoxy
    piston = V["GER-002"] * kw["rho_petg"] * g
    cart_u = V["GER-003"] * kw["rho_xps"] * g + ca
    cart_l = V["GER-008"] * kw["rho_xps"] * g + ca
    pad = V["GER-004"] * kw["rho_neo"] * g
    cap = V["GER-007"] * kw["rho_tpu"] * g + kw["tape"]
    up, lo = shoe + piston + cart_u + pad, shoe + piston + cart_l + pad
    tot = 2 * up + 2 * lo + 2 * cap
    return {"shoe_g": shoe, "piston_g": piston, "cartridge_upper_g": cart_u, "cartridge_lower_g": cart_l,
            "pad_g": pad, "cap_g": cap, "foot_upper_g": up, "foot_lower_g": lo, "feet_g": 2 * up + 2 * lo,
            "caps_g": 2 * cap, "total_g": tot, "alloc_margin_g": kw["alloc"] - tot,
            "insert_upper_g": piston + cart_u + pad, "insert_lower_g": piston + cart_l + pad}


# ---------------------------------------------------------------- strength of the printed parts and the bond
@kit.calc("CALC-D5-FLANGE", title="Flange overhang bending at the ultimate upper-foot load on its edge",
          inputs={"F": "CL-D5-F-ULT-UPPER", "F_c1": "CL-C1-FOOT-F-ULT", "a": "CL-D5-FLANGE-OVERHANG",
                  "b": "CL-D5-SLEEVE-OUT", "t": LP + "piston.flange_t_m", "allow": "ASM-D5-PETG-SIGMA"},
          units={"F": "N", "F_c1": "N", "a": "m", "b": "m", "t": "m", "allow": "Pa"},
          equation="F = max(D5 upper ult, C1 ult) ; M = F a ; sigma = 6 M / (b t^2) ; SF = allow / sigma")
def flange(F, F_c1, a, b, t, allow):
    Fu = max(F, F_c1)
    sig = 6 * Fu * a / (b[0] * t * t)
    return {"F_N": Fu, "sigma_Pa": sig, "sf": allow / sig}


BOND_IN = dict(GEOM_IN)
BOND_IN.update({"F": "CL-D5-F-ULT-UPPER", "F_c1": "CL-C1-FOOT-F-ULT", "ff": "ASM-D5-FIT-FACTOR",
                "tau": "ASM-D5-BOND-TAU", "kd": "ASM-C6-FOAM-KD"})
BOND_UNITS = dict(GEOM_UNITS)
BOND_UNITS.update({"F": "N", "F_c1": "N", "tau": "Pa"})


@kit.calc("CALC-D5-BOND", title="Shoe-to-half-fin bond at the printed/bonded design load", inputs=BOND_IN,
          units=BOND_UNITS,
          equation="A = floor on the step edge (L t_fin) + legs 2 L d + back wall on the step front t_fin h_step + "
                   "collar cheeks on the strip ends 2 l (w_strip + 2 mm) ; design = max(F, F_c1) ff ; "
                   "allow = tau kd (C6) ; RF = allow A / design")
def bond(F, F_c1, ff, tau, kd, **kw):
    s = landing.stack(_n(kw))
    L = kw["te"] - s["x_bw"][0]
    A = (L * s["t_fin"] + 2 * L * kw["leg_depth"] + s["t_fin"] * s["notch_depth"]
         + 2 * kw["collar_len"] * (kw["strip_w"] + 0.002))
    design = max(F, F_c1) * ff
    return {"area_m2": A, "design_N": design, "tau_Pa": design / A, "allow_Pa": tau * kd, "sf": tau * kd * A / design}


SIDE_IN = dict(GEOM_IN)
SIDE_IN.update({"F_lim": "CL-C5-FOOT-SIDE-LOAD", "k_ult": "ASM-D5-ULT-FACTOR", "eps_y": "ASM-D5-YIELD-STRAIN",
                "allow": "ASM-D5-PETG-SIGMA"})
SIDE_UNITS = dict(GEOM_UNITS)
SIDE_UNITS.update({"F_lim": "N", "allow": "Pa"})


@kit.calc("CALC-D5-SIDE", title="Side load at the pad: tine-in-sleeve bearing at the rim and tine bending",
          inputs=SIDE_IN, units=SIDE_UNITS,
          equation="F = 1.5 F_side (C5, mu 0.7 on the mat) ; s0 = eps_y L_cart (plateau reached) ; lip reaction R = "
                   "F (a + e) / (e + s0) ; rim as a fixed-ended beam over the wider sleeve span b: M = R b / 12, "
                   "S = l_rim (w + t_rim)^2 / 6 + (b/2) w^2 / 6 ; tine at the rim: M = F a, windowed section S_min")
def side(F_lim, k_ult, eps_y, allow, **kw):
    s = landing.stack(_n(kw))
    F = k_ult * F_lim
    a = s["x_g"] - s["x_slv_end"]
    e = kw["engage"]
    s0 = eps_y * s["L_cart"]
    R = F * (a + e) / (e + s0)
    b = max(s["slv_out"])
    w, tr = kw["w"], kw["rim_t"]
    S_rim = kw["rim_len"] * (w + tr) ** 2 / 6 + (b / 2) * w * w / 6
    sig_rim = R * b / 12 / S_rim
    py, pz = s["pist_out"]
    r = w + kw["rail"]                                            # each z-wall keeps a rail r wide at both y edges
    # bending about y (load along z): webs = y walls (full height), flanges = z-wall rails
    I_y = 2 * (w * pz ** 3 / 12) + 4 * (r * w) * ((pz - w) / 2) ** 2
    # bending about z (load along y): webs = rails of the z walls, flanges = y walls
    I_z = 2 * (pz * w ** 3 / 12 + pz * w * ((py - w) / 2) ** 2) + 4 * (w * r ** 3 / 12)
    S_t = min(I_y / (pz / 2), I_z / (py / 2))
    sig_t = F * a / S_t
    return {"F_N": F, "R_lip_N": R, "sigma_rim_Pa": sig_rim, "sf_rim": allow / sig_rim, "sigma_tine_Pa": sig_t,
            "sf_tine": allow / sig_t}


@kit.calc("CALC-D5-SNAP", title="Snap finger strain at full release deflection",
          inputs={"t": LP + "wall_t_m", "y": LP + "piston.hook_protrusion_m", "L": LP + "piston.finger_len_m",
                  "eps_max": "ASM-C6-SNAP-STRAIN", "L_min": "CL-C6-SNAP-L-MIN"},
          units={"t": "m", "y": "m", "L": "m", "L_min": "m"}, cites=["SRC-D5-SNAP"],
          equation="eps = 1.5 t y / L^2 (cantilever of constant section) ; L margin = L - L_min")
def snap(t, y, L, eps_max, L_min):
    eps = 1.5 * t * y / (L * L)
    return {"strain": eps, "strain_margin": eps_max - eps, "len_m": L, "len_margin_m": L - L_min}


@kit.calc("CALC-D5-BOX", title="Feet and corner caps in the transport envelope and box",
          inputs={"ext": P + "requirements.box_external_m", "wall": "ASM-A1-WALL", "z_out": LP + "pad.z_outer_m",
                  "env": P + "transport.envelope_props_off_m", "span": P + "wing.span_m", "cw": LP + "cap.wall_t_m"},
          units={"ext": "m", "wall": "m", "z_out": "m", "env": "m", "span": "m", "cw": "m"},
          equation="height slack = (H_ext - 2 wall) - 2 z_outer ; height growth = 2 z_outer - envelope z ; span growth "
                   "= span + 2 cap wall - envelope span")
def box(ext, wall, z_out, env, span, cw):
    return {"slack_m": (ext[2] - 2 * wall) - 2 * z_out, "growth_m": max(0.0, 2 * z_out - env[2]),
            "span_growth_m": max(0.0, span + 2 * cw - env[0])}


# ---------------------------------------------------------------- claims
FEET = ["GER-00%d-%s" % (n, s) for n in (1, 2, 4) for s in ("UR", "UL", "LR", "LL")] + \
       ["GER-003-UR", "GER-003-UL", "GER-008-LR", "GER-008-LL"]
CARTS = ["GER-003-UR", "GER-003-UL", "GER-008-LR", "GER-008-LL"]
SHOES = ["GER-001-%s" % s for s in ("UR", "UL", "LR", "LL")]
PISTONS = ["GER-002-%s" % s for s in ("UR", "UL", "LR", "LL")]
PADS = ["GER-004-%s" % s for s in ("UR", "UL", "LR", "LL")]
CAPS = ["GER-007-R", "GER-007-L"]


def G(id, title, out, unit="m", **k):
    kit.claim(id, title, calc="CALC-D5-GEOM", output=out, unit=unit, **k)


G("CL-D5-CART-LEN", "Crush cartridge length", "cart_len_m", parts=CARTS,
  how="Measure the cut cartridge pair: 2 x 44.5 mm incl. 0.5 mm preload.")
G("CL-D5-SLEEVE-OUT", "Sleeve outside y x z", "sleeve_out_m", parts=SHOES, how="Calipers on the printed shoe.")
G("CL-D5-PISTON-OUT", "Tine outside y x z", "piston_out_m", parts=PISTONS,
  how="Calipers on the printed piston; it slides in the sleeve by hand without play.")
G("CL-D5-SLEEVE-LEN", "Sleeve length (back wall to rim end)", "sleeve_len_m", parts=SHOES, how="Calipers.")
G("CL-D5-SKIRT-LEN", "Tine length (open end to flange)", "tine_len_m", parts=PISTONS, how="Calipers.")
G("CL-D5-LEG-LEN", "Shoe length on the half-fin (step front to TE)", "shoe_len_on_fin_m", parts=SHOES,
  how="Calipers on the printed shoe; D3 keeps this length of the tip clear (CR-D5-11).")
G("CL-D5-WINDOW-LEN", "Snap window length", "window_len_m", parts=SHOES,
  how="Calipers; the hook runs the full stroke without touching the window front edge.")
G("CL-D5-FLANGE-Z", "Flange and pad height (z)", "pad_z_m", parts=PISTONS + PADS, how="Calipers.")
G("CL-D5-FLANGE-OVERHANG", "Flange overhang outboard of the tine", "flange_overhang_m", parts=PISTONS,
  how="Calipers on the printed piston.")
G("CL-D5-T-FIN", "Fin board thickness the shoe straddles", "t_fin_m",
  how="Measure the laminated two-layer half-fin at the step; the leg gap is this + 2 x 0.2 mm.")
G("CL-D5-FIN-STEP-Z", "Half-fin step edge |z| (D3 cuts the tip down to it)", "z_step_m",
  how="Ruler from the chord plane to the step edge on the half-fin template.")
G("CL-D5-FIN-STEP-X", "Half-fin step front x (step runs from here to the TE)", "x_step_m",
  how="Ruler from the wing LE station along the half-fin template.")
G("CL-D5-FIN-STEP-DEPTH", "Half-fin step depth below the 0.21 m tip", "step_depth_m", limit=("<=", 0.010),
  note="<= the 10 mm edge-strip width: only the strip zone of the tip is removed",
  how="Template check before cutting (D3).")
G("CL-D5-STROKE-AVAIL", "Crush stroke available (flange to rim gap)", "stroke_m",
  limit=(">=", P + "requirements.foot_crush_stroke_min_m"), parts=SHOES + PISTONS,
  note="D-30: >= 38 mm flange-to-sleeve gap; usable (gap - 3 mm guard) is CL-D5-STROKE-USABLE",
  how="Assembled foot: gap between the flange and the rim, calipers.")
G("CL-D5-CONTACT-Z", "Tip-over pivot (pad outboard edge less the edge round)", "z_contact_eff_m",
  limit=(">=", 0.21), parts=PADS, note="D-30 keeps it at +/-0.218 with the 0.21 m half-fins",
  how="Measure pad edge to the wing chord plane on the built aircraft.")
G("CL-D5-TE-CLEAR-CRUSHED", "Wing TE above the ground with a fully crushed foot", "te_clear_crushed_m",
  limit=(">=", 0.010), note="D-11 rule; equals C5's CL-C5-TE-CLEAR-PROP",
  how="Stand the aircraft on the rims (inserts removed, a 38 mm spacer) and measure the TE height.")
G("CL-D5-RIM-AFT-OF-TE", "Rim starts aft of the fin TE", "rim_clear_of_te_m", limit=(">=", 0.0), parts=SHOES,
  how="Shoe drawing: the thickened rim never overlaps the fin.")
G("CL-D5-LEVER", "Pad to rim lever arm at rest", "lever_m", parts=PISTONS, how="Calipers on the assembled foot.")

C = "CALC-D5-CRUSH"
kit.claim("CL-D5-F-PLATEAU", "Crush plateau per foot, mean of the upper and lower types", calc=C,
          output="F_plateau_N", unit="N", parts=CARTS,
          note="C5 applies the bias to this mean (CR-C5-10); per type: CL-D5-F-PLATEAU-UPPER/-LOWER",
          how="T-D5-COUPON: crush 3 pre-crushed pairs of each type 40 mm in a printed shoe + piston over a load cell.")
kit.claim("CL-D5-F-MEAN-ERR", "Mean plateau vs C5-R3's 37.5 N", calc=C, output="mean_err", unit="-",
          limit=("<=", 0.01), parts=CARTS, how="Mean of the type-U and type-L coupon plateaus.")
kit.claim("CL-D5-F-PLATEAU-UPPER", "Crush plateau, type U (UR, UL; orange, solid)", calc=C, output="F_upper_N",
          unit="N", parts=["GER-003-UR", "GER-003-UL"], how="T-D5-COUPON, type U; pass 38.2-40.2 N (C5-R3 39.4 N -3/+2 %).")
kit.claim("CL-D5-F-PLATEAU-LOWER", "Crush plateau, type L (LR, LL; blue, 5.56 mm bore)", calc=C, output="F_lower_N",
          unit="N", parts=["GER-008-LR", "GER-008-LL"], how="T-D5-COUPON, type L; pass 34.6-36.3 N (C5-R3 35.6 N -3/+2 %).")
kit.claim("CL-D5-BIAS-UPPER", "Upper-foot plateau / mean plateau", calc=C, output="bias_upper", unit="-",
          parts=CARTS, how="Ratio of the coupon plateaus.")
kit.claim("CL-D5-BIAS-ERR", "Bias error against C5-R3's x1.05 target", calc=C, output="bias_err", unit="-",
          limit=("<=", 0.01), parts=CARTS, how="Ratio of the coupon plateaus; change the bore tube (3/16 or 1/4 in) if off by > 1 %.")
kit.claim("CL-D5-F-PEAK", "Mean peak foot force (limit) in the 1.5 m/s landing", calc=C, output="F_peak_N",
          unit="N", limit=("<=", "CL-C1-FOOT-MAX"), parts=FEET, how="T-D5-COUPON peak; drop test T-C1-FOOT-DROP.")
kit.claim("CL-D5-F-PEAK-UPPER", "Peak force on an upper foot (limit)", calc=C, output="F_peak_upper_N", unit="N",
          limit=("<=", "CL-C1-FOOT-MAX"), parts=FEET,
          note="C1 R3 bound; C1 to carry the per-type split (CR-D5-14)",
          how="T-D5-COUPON type U peak.")
kit.claim("CL-D5-F-ULT-UPPER", "Ultimate force on an upper foot (1.5 x peak)", calc=C, output="F_ult_upper_N",
          unit="N", parts=FEET, how="Proof load a printed piston + shoe on a fin offcut to 88 N (T-D5-PROOF).")
kit.claim("CL-D5-N-LAND", "Landing load factor, level 1.5 m/s, four feet", calc=C, output="n_land", unit="-",
          limit=("<=", P + "requirements.landing_n_design"), parts=FEET,
          how="T-C5-AIRCRAFT-DROP level, accelerometer at the CG.")
kit.claim("CL-D5-STROKE-USED", "Stroke used, level 1.5 m/s landing (hand energy balance)", calc=C,
          output="stroke_used_m", unit="m", limit=("<=", "CL-D5-STROKE-USABLE"), parts=FEET,
          how="Flange gap before and after the level drop.")
kit.claim("CL-D5-STROKE-USABLE", "Usable stroke (gap less C5's 3 mm guard) vs C5's pair-first landing", calc=C,
          output="usable_m", unit="m", limit=(">=", "CL-C5-DROP-PAIR-PITCH"), parts=FEET,
          how="T-C5-AIRCRAFT-DROP pitched 4 deg: each pair within 3 mm of the model.")
kit.claim("CL-D5-ETA", "Crush efficiency (energy / peak force x stroke)", calc=C, output="eta", unit="-",
          limit=(">=", 0.8), how="Integrate the T-D5-COUPON force-stroke record.")
kit.claim("CL-D5-STRAIN-MARGIN", "Cartridge strain margin to densification at the full 38 mm", calc=C,
          output="strain_margin", unit="-", limit=(">=", 0.0), parts=CARTS,
          how="T-D5-COUPON: force still flat at 44 % strain (incl. the 1 mm pre-crush per segment).")
kit.claim("CL-D5-CUT-SEG-LEN", "Cartridge segment cut length before the 1 mm pre-crush", calc=C, output="cut_seg_len_m",
          unit="m", limit=("<=", 0.0508), note="<= the 2 in board thickness (crush axis = through-thickness)",
          parts=CARTS, how="Calipers on the cut stick before pressing.")
kit.claim("CL-D5-SET-NORMAL", "Permanent crush per normal 0.5 m/s landing", calc=C, output="set_normal_m", unit="m",
          how="Measure the flange gap after each of the first 10 hover landings (H2).")
kit.claim("CL-D5-V-NO-SET", "Touchdown sink below which a landing leaves no permanent crush", calc=C,
          output="v_no_set_ms", unit="m/s", note="Q_LAND_SPEED at or below this keeps the cartridges for hard "
          "landings (CR-D5-21 to F4)", how="H2: gap before/after 10 landings at Q_LAND_SPEED 30 cm/s.")
kit.claim("CL-D5-MARK-MARGIN", "Replace mark leaves C5's pair-first stroke", calc=C, output="mark_margin_m",
          unit="m", limit=(">=", 0.0), parts=PISTONS,
          how="With the groove at the rim the remaining gap less the 3 mm guard must be >= CL-C5-DROP-PAIR-PITCH.")
kit.claim("CL-D5-LANDINGS-PER-CART", "Normal landings before the replace mark", calc=C,
          output="landings_per_cartridge", unit="-", how="H2 landing log (T-C5-DRIFT-LOG).")

T = "CALC-D5-TIPOVER"
kit.claim("CL-D5-TIPOVER-NARROW", "Tip-over, narrow axis, CG at the target", calc=T, output="narrow_deg", unit="deg",
          limit=(">=", P + "requirements.tipover_min_deg"), parts=PADS,
          how="C5 tilting-board test: angle at which the built aircraft tips about the pad edges.")
kit.claim("CL-D5-TIPOVER-CORNER", "Tip-over at the worst flying CG (forward limit, z +0.03)", calc=T,
          output="corner_deg", unit="deg", limit=(">=", P + "requirements.tipover_min_deg"), verifies=["R-TIPOVER"],
          parts=PADS, how="Tilting board with the pack at its forward stop and ballast at the z limit.")

M = "CALC-D5-MASS"
kit.claim("CL-D5-MASS-FOOT", "Mass of one complete upper foot (heavier type)", calc=M, output="foot_upper_g",
          unit="g", parts=FEET, how="Weigh one assembled foot (T-A3-WEIGH-PARTS).")
kit.claim("CL-D5-MASS-INSERT", "Mass of one spare insert (piston + type-U cartridge + pad)", calc=M,
          output="insert_upper_g", unit="g", how="Weigh one pre-glued insert.")
kit.claim("CL-D5-MASS-CAP", "Mass of one wingtip corner cap with tape", calc=M, output="cap_g", unit="g",
          limit=("<=", 1.0), note="CR-C5-04: <= 1 g", parts=CAPS, how="Weigh the printed cap.")
kit.claim("CL-D5-MASS-TOTAL", "Landing subsystem flying mass (4 feet + 2 caps)", calc=M, output="total_g", unit="g",
          limit=("<=", P + "mass.allocation_g.landing"), parts=FEET + CAPS,
          how="Weigh the four feet and two caps with glue and tape.")

kit.claim("CL-D5-FLANGE-SF", "Flange overhang bending, SF at ultimate", calc="CALC-D5-FLANGE", output="sf",
          unit="-", limit=(">=", 1.0), parts=PISTONS, how="Load a printed flange edge to 61 N; no crack (T-D5-PROOF).")
kit.claim("CL-D5-BOND-AREA", "Shoe bond area on the half-fin", calc="CALC-D5-BOND", output="area_m2", unit="m2",
          parts=SHOES, how="Shoe drawing; C6 copies it into the E-GER-01..04 bond block.")
kit.claim("CL-D5-BOND-SF", "Shoe-to-fin bond RF at the printed/bonded design load (C6 allowable)",
          calc="CALC-D5-BOND", output="sf", unit="-", limit=(">=", 1.0), parts=SHOES,
          how="Pull test of a shoe bonded on a stepped two-layer offcut to 88 N along x (T-D5-PROOF, C6 coupon).")
kit.claim("CL-D5-SIDE-RIM-SF", "Rim bending under the tine lip reaction (side load at the pad)", calc="CALC-D5-SIDE",
          output="sf_rim", unit="-", limit=(">=", 1.0), parts=SHOES,
          how="T-D5-SIDE: 32 N sideways at the pad of a foot crushed 4 mm, both axes; no crack at the rim.")
kit.claim("CL-D5-SIDE-TINE-SF", "Tine bending at the rim under the side load", calc="CALC-D5-SIDE",
          output="sf_tine", unit="-", limit=(">=", 1.0), parts=PISTONS, how="T-D5-SIDE.")
kit.claim("CL-D5-SNAP-STRAIN", "Snap finger strain at release", calc="CALC-D5-SNAP", output="strain", unit="-",
          limit=("<=", "ASM-C6-SNAP-STRAIN"), parts=PISTONS, how="50 release cycles on one piston; no whitening.")
kit.claim("CL-D5-SNAP-LEN", "Snap finger free length vs C6 minimum", calc="CALC-D5-SNAP", output="len_m", unit="m",
          limit=(">=", "CL-C6-SNAP-L-MIN"), parts=PISTONS, how="Calipers on the slots.")
kit.claim("CL-D5-BOX-SLACK", "Box height slack with the splayed feet", calc="CALC-D5-BOX", output="slack_m", unit="m",
          limit=(">=", 0.0), verifies=["R-TRANSPORT"], how="D7: close the lid on the built aircraft.")
kit.claim("CL-D5-ENVELOPE-GROWTH", "Props-off envelope height growth from the feet", calc="CALC-D5-BOX",
          output="growth_m", unit="m", how="A1 envelope 0.438 m already includes the pads.")
kit.claim("CL-D5-ENVELOPE-SPAN-GROWTH", "Props-off envelope span growth from the corner caps", calc="CALC-D5-BOX",
          output="span_growth_m", unit="m", parts=CAPS, how="Measure tip to tip over the caps (CR-D5-16).")
kit.claim("CL-D5-PAD-MU", "Pad friction vs the friction to stand in 8 m/s", value=0.7, unit="-",
          limit=(">=", "CL-C1-STANCE-MU-REQ"), assumes=["ASM-D5-PAD-MU"], verifies=["R-WIND"], parts=PADS,
          how="T-D5-PAD-MU tilt-board slide test.")
kit.claim("CL-D5-REPLACE-TIME", "Field replacement of a crushed foot insert", value=3.0, unit="min",
          limit=("<=", P + "requirements.foot_replace_max_min"), assumes=["ASM-D5-REPLACE-MIN"],
          parts=PISTONS + CARTS + PADS, how="T-D5-REPLACE, stopwatch.")

kit.test("T-D5-COUPON", "Cartridge crush coupon, both types", verifies=["CL-D5-F-PLATEAU-UPPER",
         "CL-D5-F-PLATEAU-LOWER", "CL-D5-BIAS-ERR", "CL-D5-F-PEAK", "CL-D5-ETA", "CL-D5-STRAIN-MARGIN"],
         procedure="Pre-crush every segment 1 mm (drill-press stop). Crush 3 type-U and 3 type-L cartridge pairs in a printed "
         "piston + shoe on the drill press over the H1 load cell, 40 mm at < 10 mm/s; record force every 2 mm. Pass "
         "(C5-R3, mean force 5-35 mm): U 38.2-40.2 N, L 34.6-36.3 N, ratio U/L 1.09-1.14, peak <= 1.05 x plateau, "
         "flat to 40 mm. Off target: change section_y_m (both types) by the force ratio, or the bore tube (ratio), and "
         "re-run feet_calc.py.")
kit.test("T-D5-PAD-MU", "Pad slide on a tilt board", verifies=["CL-D5-PAD-MU"],
         procedure="Foot with pad, 0.65 kg on it, on a board faced with concrete paver / asphalt shingle / the landing "
                   "mat; tilt until it slides; mu = tan(angle). Pass >= 0.7 dry.")
kit.test("T-D5-REPLACE", "Timed foot-insert swap", verifies=["CL-D5-REPLACE-TIME"],
         procedure="One student, field kit only, swap a crushed insert for a spare on the built aircraft; pass <= 10 min.")
kit.test("T-D5-PROOF", "Shoe bond and flange proof load", verifies=["CL-D5-BOND-SF", "CL-D5-FLANGE-SF"],
         procedure="Shoe bonded (24 h) on a stepped two-layer foam-board offcut with strip ends; load the pad along x "
                   "to 88 N through a 10 mm steel block at the pad edge; hold 3 s. Pass: no bond crack, no flange crack.")
kit.test("T-D5-SIDE", "Side load at the pad", verifies=["CL-D5-SIDE-RIM-SF", "CL-D5-SIDE-TINE-SF"],
         procedure="Same specimen, insert pushed 4 mm in; 32 N at the pad sideways along y, then along z; pass: no crack "
                   "at the rim or tine, insert still slides.")


def _cad_crosscheck():
    """The CAD module built on the stub backend must give the same stack and volumes as the calcs."""
    import json
    import fusionkit as fk
    from backends.stub_backend import StubBackend
    params = json.loads((RED / "params" / "params.json").read_text(encoding="utf-8"))
    parts = {}
    sub = RED / "subsystems" / "landing"
    for p in json.loads((sub / "interfaces.json").read_text(encoding="utf-8"))["parts"]:
        parts[p["id"]] = p
    ctx = fk.Context(StubBackend(), parts=parts, params=params)
    k9.build_datums(ctx)
    ctx.begin_module("landing", str(sub))
    landing.build(ctx)
    n = landing.inputs(ctx.value, ctx.local)
    B = landing.bodies(n, k9.section(ctx)[0])
    for pid, c in ctx.components.items():
        base = pid.rsplit("-", 1)[0]
        V_cad = c.volume_centroid()[0]
        V_calc = landing.volume(B[base])
        assert abs(V_cad - V_calc) <= 1e-9 + 1e-6 * V_calc, (pid, V_cad, V_calc)
    out = kit.nodes["CALC-D5-GEOM"]["outputs"]
    s = B["_stack"]
    for k, o in (("x_slv_end", "x_sleeve_end_m"), ("x_open", "x_piston_open_m"), ("x_bw_in", "x_back_wall_in_m"),
                 ("L_cart", "cart_len_m"), ("z_step", "z_step_m")):
        assert abs(s[k] - out[o]) < 1e-12, (k, s[k], out[o])
    print("CAD stack and volumes == CALC-D5-GEOM / CALC-D5-MASS: OK (%d components)" % len(ctx.components))


if __name__ == "__main__":
    kit.write()
    _cad_crosscheck()
