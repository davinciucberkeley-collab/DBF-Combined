"""D5 landing designer: crushable fin-tip feet (GER) for the K09-L quad tailsitter.

Run:  python -I redesign/team/D5/feet_calc.py
Writes claims.json beside this file. Every number is a pure function of params.json (P:...), the landing
subsystem params (P:landing.*, redesign/subsystems/landing/params.json), C1 claims and the assumptions below.
__main__ also asserts that the foot stack here equals the one the CAD module builds (fusion/landing.py stack()).

Answers CR-A1-20 (D-11): >= 25 mm constant-force stroke, <= 10 g per foot, replaceable in <= 10 min,
contact points splayed to z >= +/-0.21 m (tip-over >= 33 deg), pads mu >= 0.7 (CR-C1-02).
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

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

kit.assumption("ASM-D5-XPS-PLATEAU", "XPS crush plateau 172 kPa",
               "Crush plateau stress of F-250 XPS loaded through the board thickness equals its 10 % compressive "
               "strength and stays flat to the densification strain",
               basis="FOAMULAR 250 datasheet 25 psi; closed-cell XPS plateau is flat within ~10 % from 5 to 50 % "
                     "strain. The coupon test T-D5-COUPON replaces it; the cartridge section is the tuning knob",
               value=172000.0, unit="Pa", status="UNVERIFIED", cites=["SRC-D5-OC-F250", "SRC-XPS-F250"])
kit.assumption("ASM-D5-PEAK-FACTOR", "Initial crush peak 1.10 x plateau",
               "The first-yield peak of the XPS column is 10 % above the plateau", basis="typical XPS curve; coupon test",
               value=1.10, unit="-", status="UNVERIFIED")
kit.assumption("ASM-D5-YIELD-STRAIN", "Strain to reach the plateau 5 %",
               "Elastic ramp of the XPS column ends at 5 % strain; half of that ramp is lost against a flat-force model",
               basis="XPS modulus ~8-10 MPa vs 172 kPa plateau gives ~2 %; 5 % covers the knee", value=0.05, unit="-",
               status="UNVERIFIED")
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
               basis="estimate; C6 owns bonded-joint allowables (CR-D5-04)", value=0.20e6, unit="Pa",
               status="UNVERIFIED")
kit.assumption("ASM-D5-FIT-FACTOR", "Printed/bonded fitting factor 1.4375 on ultimate",
               "C1 printed/bonded design value = ultimate x 1.15 x 1.25", basis="team/C1/data/envelope.json#joints.J-FOOT "
               "(86.8 N / 60.4 N)", value=1.4375, unit="-", status="PROPOSED")
kit.assumption("ASM-D5-REPLACE-MIN", "Cartridge + piston swap 3 min",
               "Press two snap hooks, pull the piston out, push a pre-glued spare in until both hooks click",
               basis="no tools, no cure; estimate until timed (T-D5-REPLACE)", value=3.0, unit="min", status="UNVERIFIED")


# ---------------------------------------------------------------- geometry (mirrors fusion/landing.py stack())
GEOM_IN = {"te": P + "fins.te_x_m", "hh": P + "fins.half_height_m", "c": P + "wing.chord_m",
           "foot": P + "cg.foot_height_m", "board_t": P + "fins.board_t_m", "layers": P + "fins.layers",
           "w": LP + "wall_t_m", "cs": LP + "slide_clear_m", "cf": LP + "cartridge.clear_m",
           "fy": LP + "cartridge.section_y_m", "fz": LP + "cartridge.section_z_m",
           "pad_t": LP + "pad.t_m", "flange_t": LP + "piston.flange_t_m", "stroke": LP + "stroke_max_m",
           "engage": LP + "piston.engage_m", "bw_t": LP + "shoe.back_wall_t_m", "z_outer": LP + "pad.z_outer_m",
           "edge_r": LP + "pad.edge_r_m", "leg_depth": LP + "shoe.leg_depth_m", "glue_gap": LP + "shoe.glue_gap_m",
           "win_z": LP + "shoe.window_z_m", "hook_len": LP + "piston.hook_len_m",
           "hook_p": LP + "piston.hook_protrusion_m"}
GEOM_UNITS = {k: "m" for k in GEOM_IN if k != "layers"}


@kit.calc("CALC-D5-GEOM", title="Foot stack and sizes", inputs=GEOM_IN, units=GEOM_UNITS,
          equation="x_g = c + foot ; flange = x_g - pad - t_fl ; sleeve end = flange - stroke ; piston open = "
                   "sleeve end - engage ; back wall = open - stroke - 1 mm ; L_cart = flange - back wall ; "
                   "sections: cartridge + 2 cf -> piston + 2 w -> sleeve + 2 cs + 2 w ; z_eff = z_outer - r ; "
                   "TE clearance at full stroke = foot - stroke")
def geom(te, hh, c, foot, board_t, layers, w, cs, cf, fy, fz, pad_t, flange_t, stroke, engage, bw_t, z_outer,
         edge_r, leg_depth, glue_gap, win_z, hook_len, hook_p):
    x_g = c + foot
    pist_out = (fy + 2 * cf + 2 * w, fz + 2 * cf + 2 * w)
    slv_out = (pist_out[0] + 2 * cs + 2 * w, pist_out[1] + 2 * cs + 2 * w)
    x_flange0 = x_g - pad_t - flange_t
    x_slv_end = x_flange0 - stroke
    x_open = x_slv_end - engage
    x_bw_in = x_open - stroke - 0.001
    x_bw0 = x_bw_in - bw_t
    z_bore_top = hh + w + cs + pist_out[1]
    return {"x_ground_m": x_g, "x_flange0_m": x_flange0, "x_sleeve_end_m": x_slv_end, "x_piston_open_m": x_open,
            "x_back_wall_in_m": x_bw_in, "x_shoe_front_m": x_bw0, "cart_len_m": x_flange0 - x_bw_in,
            "piston_out_m": list(pist_out), "sleeve_out_m": list(slv_out), "z_sleeve_top_m": hh + slv_out[1],
            "z_piston_top_m": z_bore_top, "flange_overhang_m": z_outer - z_bore_top,
            "z_contact_eff_m": z_outer - edge_r, "leg_len_m": te - x_bw0, "t_fin_m": layers * board_t,
            "sleeve_len_m": x_slv_end - x_bw_in, "skirt_len_m": x_flange0 - x_open,
            "window_len_m": stroke + 0.001 + hook_len, "te_clear_crushed_m": foot - stroke, "stroke_m": stroke,
            "flange_z_m": z_outer - hh, "box_half_needed_m": z_outer}


# ---------------------------------------------------------------- crush energy
@kit.calc("CALC-D5-CRUSH", title="Constant-force crush of one landing",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "v": P + "requirements.landing_sink_ms",
                  "lam": "ASM-C1-LAND-LIFT", "sigma": "ASM-D5-XPS-PLATEAU", "k_pk": "ASM-D5-PEAK-FACTOR",
                  "eps_y": "ASM-D5-YIELD-STRAIN", "eps_d": "ASM-D5-DENSIFY", "fy": LP + "cartridge.section_y_m",
                  "fz": LP + "cartridge.section_z_m", "L": "CL-D5-CART-LEN", "s_max": "CL-D5-STROKE-AVAIL",
                  "v_norm": "ASM-D5-NORMAL-SINK", "mark": LP + "piston.replace_mark_m"},
          units={"m": "kg", "g": "m/s2", "v": "m/s", "fy": "m", "fz": "m", "L": "m", "s_max": "m", "sigma": "Pa",
                 "v_norm": "m/s", "mark": "m"},
          equation="F_p = sigma fy fz ; F_pk = k F_p ; KE = m v^2 / 2 ; 4 F_p (s - eps_y L / 2) = KE + (1 - lam) m g s ; "
                   "eta = 4 F_p (s - eps_y L/2) / (4 F_pk s) ; n_L = 4 F_pk / (m g) ; strain = s / L ; "
                   "normal set = max(0, (m v_n^2/2 - 4 F_p eps_y L / 2) / (4 F_p))")
def crush(m, g, v, lam, sigma, k_pk, eps_y, eps_d, fy, fz, L, s_max, v_norm, mark):
    W = m * g
    F_p = sigma * fy * fz
    F_pk = k_pk * F_p
    KE = 0.5 * m * v * v
    s = (KE + 4 * F_p * eps_y * L / 2) / (4 * F_p - (1 - lam) * W)
    eta = 4 * F_p * (s - eps_y * L / 2) / (4 * F_pk * s)
    E_el = 4 * 0.5 * F_p * eps_y * L
    set_norm = max(0.0, (0.5 * m * v_norm ** 2 - E_el) / (4 * F_p))
    return {"F_plateau_N": F_p, "F_peak_N": F_pk, "KE_J": KE, "stroke_used_m": s, "eta": eta,
            "n_land": 4 * F_pk / W, "strain": s / L, "strain_margin": eps_d - s / L, "stop_margin_m": s_max - s,
            "set_normal_m": set_norm, "mark_margin_m": (s_max - s) - mark}


# ---------------------------------------------------------------- tip-over
@kit.calc("CALC-D5-TIPOVER", title="Narrow-axis tip-over on the splayed pads",
          inputs={"c": P + "wing.chord_m", "foot": P + "cg.foot_height_m", "x_cg": P + "cg.x_target_m",
                  "x_rng": P + "cg.x_range_m", "z_rng": P + "cg.z_range_m", "z_eff": "CL-D5-CONTACT-Z",
                  "y_fin": P + "fins.y_m"},
          units={"c": "m", "foot": "m", "x_cg": "m", "x_rng": "m", "z_rng": "m", "z_eff": "m", "y_fin": "m"},
          equation="h = c + foot - x_cg ; narrow = atan(z_eff / h) ; corner = atan((z_eff - z_cg,max) / "
                   "(c + foot - x_cg,min)) ; wide = atan(y_fin / h)")
def tipover(c, foot, x_cg, x_rng, z_rng, z_eff, y_fin):
    h = c + foot - x_cg
    hc = c + foot - min(x_rng)
    zc = z_eff - max(abs(z) for z in z_rng)
    return {"cg_height_m": h, "narrow_deg": math.degrees(math.atan(z_eff / h)),
            "corner_deg": math.degrees(math.atan(zc / hc)), "wide_deg": math.degrees(math.atan(y_fin / h))}


# ---------------------------------------------------------------- mass
@kit.calc("CALC-D5-MASS", title="Foot mass from the printed and cut geometry",
          inputs={"w": LP + "wall_t_m", "bw_t": LP + "shoe.back_wall_t_m", "leg_depth": LP + "shoe.leg_depth_m",
                  "win_z": LP + "shoe.window_z_m", "flange_t": LP + "piston.flange_t_m", "pad_t": LP + "pad.t_m",
                  "hook_len": LP + "piston.hook_len_m", "hook_p": LP + "piston.hook_protrusion_m",
                  "fy": LP + "cartridge.section_y_m", "fz": LP + "cartridge.section_z_m",
                  "slv": "CL-D5-SLEEVE-OUT", "pist": "CL-D5-PISTON-OUT", "L_slv": "CL-D5-SLEEVE-LEN",
                  "L_sk": "CL-D5-SKIRT-LEN", "L_leg": "CL-D5-LEG-LEN", "L_cart": "CL-D5-CART-LEN",
                  "L_win": "CL-D5-WINDOW-LEN", "fl_z": "CL-D5-FLANGE-Z",
                  "rho_petg": LP + "materials.petg_density_kgm3", "rho_neo": LP + "materials.neoprene_density_kgm3",
                  "rho_xps": P + "wing.core.density_kgm3", "glue": LP + "materials.glue_g_per_foot",
                  "alloc": P + "mass.allocation_g.landing"},
          units={k: "m" for k in ("w", "bw_t", "leg_depth", "win_z", "flange_t", "pad_t", "hook_len", "hook_p", "fy",
                                  "fz", "slv", "pist", "L_slv", "L_sk", "L_leg", "L_cart", "L_win", "fl_z")} |
                {"rho_petg": "kg/m3", "rho_neo": "kg/m3", "rho_xps": "kg/m3", "glue": "g", "alloc": "g"},
          equation="V_shoe = back wall + floor/roof + windowed y walls + 2 legs ; V_piston = skirt + flange + hooks ; "
                   "m = rho V ; glue (epoxy 0.30 g on the shoe, CA 0.05 g on the cartridge) in the part it joins")
def mass(w, bw_t, leg_depth, win_z, flange_t, pad_t, hook_len, hook_p, fy, fz, slv, pist, L_slv, L_sk, L_leg, L_cart,
         L_win, fl_z, rho_petg, rho_neo, rho_xps, glue, alloc):
    sy, sz = slv
    py, pz = pist
    V_shoe = (sy * sz * bw_t + 2 * L_slv * sy * w + 2 * (L_slv * (sz - 2 * w) - L_win * win_z) * w
              + 2 * L_leg * leg_depth * w)
    V_pist = 2 * L_sk * py * w + 2 * L_sk * (pz - 2 * w) * w + sy * fl_z * flange_t + 2 * hook_len * hook_p * (win_z - 0.002)
    g = 1000.0
    shoe = V_shoe * rho_petg * g + 0.30
    piston = V_pist * rho_petg * g
    cart = fy * fz * L_cart * rho_xps * g + (glue - 0.30)
    pad = sy * fl_z * pad_t * rho_neo * g
    foot = shoe + piston + cart + pad
    return {"shoe_g": shoe, "piston_g": piston, "cartridge_g": cart, "pad_g": pad, "foot_g": foot,
            "total_g": 4 * foot, "alloc_margin_g": alloc - 4 * foot}


# ---------------------------------------------------------------- strength of the printed parts
@kit.calc("CALC-D5-FLANGE", title="Flange overhang bending under the ultimate foot load at its edge",
          inputs={"F": "CL-C1-FOOT-F-ULT", "a": "CL-D5-FLANGE-OVERHANG", "b": "CL-D5-SLEEVE-OUT",
                  "t": LP + "piston.flange_t_m", "allow": "ASM-D5-PETG-SIGMA"},
          units={"F": "N", "a": "m", "b": "m", "t": "m", "allow": "Pa"},
          equation="M = F a ; sigma = 6 M / (b t^2) ; SF = allow / sigma (b = sleeve width y)")
def flange(F, a, b, t, allow):
    sig = 6 * F * a / (b[0] * t * t)
    return {"sigma_Pa": sig, "sf": allow / sig}


@kit.calc("CALC-D5-BOND", title="Shoe-to-fin bond shear at the printed/bonded design load",
          inputs={"F": "CL-C1-FOOT-F-ULT", "ff": "ASM-D5-FIT-FACTOR", "L": "CL-D5-LEG-LEN",
                  "d": LP + "shoe.leg_depth_m", "t_fin": "CL-D5-T-FIN", "tau": "ASM-D5-BOND-TAU"},
          units={"F": "N", "L": "m", "d": "m", "t_fin": "m", "tau": "Pa"},
          equation="A = L (2 d + t_fin) ; tau_d = F ff / A ; SF = tau_allow / tau_d")
def bond(F, ff, L, d, t_fin, tau):
    A = L * (2 * d + t_fin)
    td = F * ff / A
    return {"area_m2": A, "tau_Pa": td, "sf": tau / td}


@kit.calc("CALC-D5-BOX", title="Splayed feet in the transport box height",
          inputs={"ext": P + "requirements.box_external_m", "wall": "ASM-A1-WALL", "z_out": LP + "pad.z_outer_m",
                  "env": P + "transport.envelope_props_off_m"},
          units={"ext": "m", "wall": "m", "z_out": "m", "env": "m"},
          equation="slack = (H_ext - 2 wall) - 2 z_outer ; growth = 2 z_outer - envelope height")
def box(ext, wall, z_out, env):
    return {"slack_m": (ext[2] - 2 * wall) - 2 * z_out, "growth_m": max(0.0, 2 * z_out - env[2])}


# ---------------------------------------------------------------- claims
FEET = ["GER-00%d-%s" % (n, s) for n in (1, 2, 3, 4) for s in ("UR", "UL", "LR", "LL")]
FEET_PRINT = [p for p in FEET if p[:7] in ("GER-001", "GER-002")]

kit.claim("CL-D5-CART-LEN", "Crush cartridge length", calc="CALC-D5-GEOM", output="cart_len_m", unit="m",
          parts=[p for p in FEET if p.startswith("GER-003")], how="Measure the cut cartridge pair: 77 mm + 0.5 mm preload.")
kit.claim("CL-D5-SLEEVE-OUT", "Sleeve outside y x z", calc="CALC-D5-GEOM", output="sleeve_out_m", unit="m",
          how="Calipers on the printed shoe.")
kit.claim("CL-D5-PISTON-OUT", "Piston outside y x z", calc="CALC-D5-GEOM", output="piston_out_m", unit="m",
          how="Calipers on the printed piston; it slides in the sleeve by hand without play.")
kit.claim("CL-D5-SLEEVE-LEN", "Sleeve length (back wall to end)", calc="CALC-D5-GEOM", output="sleeve_len_m", unit="m",
          how="Calipers on the printed shoe.")
kit.claim("CL-D5-SKIRT-LEN", "Piston skirt length", calc="CALC-D5-GEOM", output="skirt_len_m", unit="m",
          how="Calipers on the printed piston.")
kit.claim("CL-D5-LEG-LEN", "Shoe bond length on the fin tip", calc="CALC-D5-GEOM", output="leg_len_m", unit="m",
          how="Calipers on the printed shoe.")
kit.claim("CL-D5-WINDOW-LEN", "Snap-hook window length", calc="CALC-D5-GEOM", output="window_len_m", unit="m",
          how="Calipers; the hook must run the full stroke without touching the window front edge.")
kit.claim("CL-D5-FLANGE-Z", "Flange and pad height (z)", calc="CALC-D5-GEOM", output="flange_z_m", unit="m",
          how="Calipers on the printed piston.")
kit.claim("CL-D5-FLANGE-OVERHANG", "Flange overhang outboard of the piston", calc="CALC-D5-GEOM",
          output="flange_overhang_m", unit="m", how="Calipers on the printed piston.")
kit.claim("CL-D5-T-FIN", "Fin thickness the shoe straddles", calc="CALC-D5-GEOM", output="t_fin_m", unit="m",
          how="Measure the bonded two-layer fin at the TE tip; the shoe slot is this + 2 x 0.2 mm.")
kit.claim("CL-D5-STROKE-AVAIL", "Crush stroke available (flange to sleeve end)", calc="CALC-D5-GEOM",
          output="stroke_m", unit="m", limit=(">=", 0.025), parts=FEET_PRINT,
          note="CR-C1-01 constant-force option: >= 25 mm at eta >= 0.8",
          how="Assembled foot: gap between the flange and the sleeve end, feeler/calipers.")
kit.claim("CL-D5-CONTACT-Z", "Tip-over pivot (pad outboard edge less the edge round)", calc="CALC-D5-GEOM",
          output="z_contact_eff_m", unit="m", limit=(">=", 0.21), parts=[p for p in FEET if p.startswith("GER-004")],
          note="CR-A1-20 asks z >= +/-0.21 m", how="Measure pad edge to the wing chord plane on the built aircraft.")
kit.claim("CL-D5-TE-CLEAR-CRUSHED", "Wing TE above the ground with a fully crushed foot", calc="CALC-D5-GEOM",
          output="te_clear_crushed_m", unit="m", limit=(">=", 0.010),
          note="A4 OI-05: grass and a crushed foot must not put the TE down",
          how="Stand the aircraft on fully crushed spare cartridges (or the stop) and measure the TE height.")

kit.claim("CL-D5-F-PLATEAU", "Crush plateau force per foot", calc="CALC-D5-CRUSH", output="F_plateau_N", unit="N",
          parts=[p for p in FEET if p.startswith("GER-003")],
          how="T-D5-COUPON: crush one cartridge pair 30 mm in the piston on a bench press over a scale.")
kit.claim("CL-D5-F-PEAK", "Peak foot force (limit) in the 1.5 m/s landing", calc="CALC-D5-CRUSH", output="F_peak_N",
          unit="N", limit=("<=", "CL-C1-FOOT-MAX"), parts=FEET, how="T-D5-COUPON peak; drop test T-C1-FOOT-DROP.")
kit.claim("CL-D5-N-LAND", "Landing load factor with the crush feet", calc="CALC-D5-CRUSH", output="n_land", unit="-",
          limit=("<=", P + "requirements.landing_n_design"), parts=FEET,
          how="T-C1-FOOT-DROP (C5 plans it): 0.115 m drop, accelerometer at the CG, n <= 6.")
kit.claim("CL-D5-STROKE-USED", "Stroke used in the 1.5 m/s landing", calc="CALC-D5-CRUSH", output="stroke_used_m",
          unit="m", limit=("<=", "CL-D5-STROKE-AVAIL"), parts=FEET,
          how="Measure the flange-to-sleeve gap before and after the drop test.")
kit.claim("CL-D5-ETA", "Crush efficiency (energy / peak force x stroke)", calc="CALC-D5-CRUSH", output="eta", unit="-",
          limit=(">=", 0.8), note="CR-C1-01 constant-force option", how="Integrate the T-D5-COUPON force-stroke record.")
kit.claim("CL-D5-STRAIN-MARGIN", "Cartridge strain margin to densification", calc="CALC-D5-CRUSH",
          output="strain_margin", unit="-", limit=(">=", 0.0), how="T-D5-COUPON: force still flat at 33 % strain.")
kit.claim("CL-D5-SET-NORMAL", "Permanent crush per normal 0.5 m/s landing", calc="CALC-D5-CRUSH",
          output="set_normal_m", unit="m", how="Measure the flange gap after each of the first 10 hover landings (H2).")
kit.claim("CL-D5-MARK-MARGIN", "Replace mark leaves the full design stroke", calc="CALC-D5-CRUSH",
          output="mark_margin_m", unit="m", limit=(">=", 0.0),
          how="With the groove at the sleeve end, the remaining gap must be >= the stroke used (CL-D5-STROKE-USED).")

kit.claim("CL-D5-TIPOVER-NARROW", "Tip-over angle, narrow axis, splayed pads, CG at target", calc="CALC-D5-TIPOVER",
          output="narrow_deg", unit="deg", limit=(">=", P + "requirements.tipover_min_deg"), verifies=["R-TIPOVER"],
          parts=[p for p in FEET if p.startswith("GER-004")],
          how="C5 tilting-board test: angle at which the built aircraft tips about the pad edges.")
kit.claim("CL-D5-TIPOVER-CR-TARGET", "Tip-over vs the CR-A1-20 target 33 deg", calc="CALC-D5-TIPOVER",
          output="narrow_deg", unit="deg", limit=(">=", 33.0), how="As CL-D5-TIPOVER-NARROW.")
kit.claim("CL-D5-TIPOVER-CORNER", "Tip-over at the worst CG corner (x fwd limit, |z| max)", calc="CALC-D5-TIPOVER",
          output="corner_deg", unit="deg", limit=(">=", P + "requirements.tipover_min_deg"),
          how="Tilting board with the pack slid to its forward stop and ballast at the z limit.")

kit.claim("CL-D5-MASS-FOOT", "Mass of one complete foot", calc="CALC-D5-MASS", output="foot_g", unit="g",
          limit=("<=", 10.0), note="CR-A1-20: <= 10 g each", parts=FEET, how="Weigh one assembled foot (T-A3-WEIGH-PARTS).")
kit.claim("CL-D5-MASS-TOTAL", "Landing subsystem flying mass", calc="CALC-D5-MASS", output="total_g", unit="g",
          limit=("<=", P + "mass.allocation_g.landing"), parts=FEET, how="Weigh the four feet with glue.")
kit.claim("CL-D5-FLANGE-SF", "Flange overhang bending, safety factor at ultimate", calc="CALC-D5-FLANGE", output="sf",
          unit="-", limit=(">=", 1.0), parts=[p for p in FEET if p.startswith("GER-002")],
          how="Load a printed piston flange edge to 60 N on a vice-held skirt; no crack.")
kit.claim("CL-D5-BOND-SF", "Shoe-to-fin bond, safety factor at the printed/bonded design load", calc="CALC-D5-BOND",
          output="sf", unit="-", limit=(">=", 1.0), parts=[p for p in FEET if p.startswith("GER-001")],
          how="Pull test of a shoe bonded on a foam-board offcut to 87 N along x (C6 to confirm the allowable).")
kit.claim("CL-D5-BOX-SLACK", "Box height slack with the splayed feet", calc="CALC-D5-BOX", output="slack_m", unit="m",
          limit=(">=", 0.0), verifies=["R-TRANSPORT"], how="D7: close the lid on the built aircraft.")
kit.claim("CL-D5-ENVELOPE-GROWTH", "Props-off envelope height growth from the splay", calc="CALC-D5-BOX",
          output="growth_m", unit="m", how="A1 updates transport.envelope_props_off_m (CR-D5-01).")
kit.claim("CL-D5-PAD-MU", "Pad friction vs the friction to stand in 8 m/s", value=0.7, unit="-",
          limit=(">=", "CL-C1-STANCE-MU-REQ"), assumes=["ASM-D5-PAD-MU"], verifies=["R-WIND"],
          parts=[p for p in FEET if p.startswith("GER-004")], how="T-D5-PAD-MU tilt-board slide test.")
kit.claim("CL-D5-REPLACE-TIME", "Field replacement of a crushed foot insert", value=3.0, unit="min",
          limit=("<=", P + "requirements.foot_replace_max_min"), assumes=["ASM-D5-REPLACE-MIN"],
          parts=[p for p in FEET if p[:7] in ("GER-002", "GER-003", "GER-004")], how="T-D5-REPLACE, stopwatch.")

kit.test("T-D5-COUPON", "Cartridge crush coupon", verifies=["CL-D5-F-PLATEAU", "CL-D5-F-PEAK", "CL-D5-ETA",
         "CL-D5-STRAIN-MARGIN"], procedure="Crush 3 cartridge pairs in a printed piston + shoe on a drill-press over a "
         "kitchen scale (or the H1 thrust-stand load cell), 30 mm at < 10 mm/s; record force every 2 mm. Pass: plateau "
         "30-37 N, peak <= 38 N. Off target: change cartridge.section_z_m by the force ratio and re-run feet_calc.py.")
kit.test("T-D5-PAD-MU", "Pad slide on a tilt board", verifies=["CL-D5-PAD-MU"],
         procedure="Foot with pad, 0.65 kg on it, on a board faced with concrete paver / asphalt shingle / turf; tilt "
                   "until it slides; mu = tan(angle). Pass >= 0.7 dry.")
kit.test("T-D5-REPLACE", "Timed foot-insert swap", verifies=["CL-D5-REPLACE-TIME"],
         procedure="One student, field kit only, swap a crushed insert for a spare on the built aircraft; pass <= 10 min.")


def _cad_crosscheck():
    """The CAD module's stack() must give the same numbers as CALC-D5-GEOM."""
    import json
    red = HERE.parents[1]
    sys.path.insert(0, str(red / "fusion"))
    sys.path.insert(0, str(red / "subsystems" / "landing" / "fusion"))
    import k09kit as k9
    import landing
    params = json.loads((red / "params" / "params.json").read_text(encoding="utf-8"))
    local = json.loads((red / "subsystems" / "landing" / "params.json").read_text(encoding="utf-8"))
    s = landing.stack(lambda k, u=None: k9.val(params, k, u), local, k9.fin_thickness(params))
    out = kit.nodes["CALC-D5-GEOM"]["outputs"]
    pairs = [("x_flange", 0, "x_flange0_m"), ("x_slv_end", None, "x_sleeve_end_m"),
             ("x_pist_open", None, "x_piston_open_m"), ("x_bw_in", None, "x_back_wall_in_m"),
             ("L_cart", None, "cart_len_m"), ("x_bw", 0, "x_shoe_front_m")]
    for k, i, o in pairs:
        a = s[k][i] if i is not None else s[k]
        assert abs(a - out[o]) < 1e-9, (k, a, out[o])
    assert abs(s["slv_out"][0] - out["sleeve_out_m"][0]) < 1e-9 and abs(s["slv_out"][1] - out["sleeve_out_m"][1]) < 1e-9
    print("CAD stack == CALC-D5-GEOM: OK")


if __name__ == "__main__":
    kit.write()
    _cad_crosscheck()
