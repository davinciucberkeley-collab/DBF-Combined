"""D6 mechanisms claims for the proof chain (K09-L, revision D6-R2: mass reduction, CF bridge rod).

Run from the repo root after subsystems/mechanisms/make_mechanisms.py:
    python -I redesign/team/D6/mech_calcs.py
then python -I redesign/proofs/build_graph.py. Every calculation is a pure function of its named inputs; the four-bar
solver is the one in subsystems/mechanisms/fusion/mechanisms.py (same code as the CAD).

Sign convention (hinge frame, x-z plane): delta > 0 = trailing edge DOWN; theta > 0 = servo arm hole moving aft.
Hinge moment model: H(delta) = Ch_max (delta / 25 deg) q c^2 b (ASM-D6-CH-LINEAR), Ch_max = B2's inviscid bound.
"""
import importlib.util
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
sys.path.insert(0, str(REDESIGN / "proofs"))
import proofkit as pk  # noqa: E402

_spec = importlib.util.spec_from_file_location("mec_cad", REDESIGN / "subsystems" / "mechanisms" / "fusion" /
                                               "mechanisms.py")
sys.path.insert(0, str(REDESIGN / "fusion"))
MEC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MEC)

kit = pk.Kit(__file__, params=["../../params/params.json", "../B2/params.json",
                               "../../subsystems/mechanisms/params.json", "../../subsystems/fins/params.json"])
G0 = 9.80665
SERVOS = ["MEC-001-L", "MEC-001-R"]
LINK = ["MEC-002-L", "MEC-002-R", "MEC-003-L", "MEC-003-R", "MEC-004-L", "MEC-004-R"]
BRIDGE = ["MEC-004-L", "MEC-004-R", "MEC-005-L", "MEC-005-R", "MEC-006-L", "MEC-006-R"]
TUBES = ["MEC-009-LI", "MEC-009-LO", "MEC-009-RI", "MEC-009-RO"]

# ---------------------------------------------------------------- sources and assumptions
kit.source("SRC-D6-SH0255", "Savox SH-0255MG+ listing (3.1/3.9 kgf cm at 4.8/6 V, 15.8 g, 22.8 x 12.0 x 29.4 mm)",
           "web", url="https://lindinger.at/en/RC-ELECTRONICS/Servos-Accessories/Servos-Digital-Low-Voltage/"
                      "SAVOEX-SH-0255MG-6V-3-9KG-0-13s-Digital-Micro-Servo/9795255",
           where="spec table; distributor sheet https://www.cmldistribution.co.uk/product/SAV-SH0255MG+/ gives 16 g",
           note="retailer data, not the maker's sheet; weigh and bench the delivered servo", status="UNVERIFIED")
kit.source("SRC-D6-SH0255-STALL", "SH-0255MG stall current 1.2 A / 1.4 A at 4.8 / 6.0 V", "web",
           url="https://www.rcjaz.com/savox-sh0255mg-metal-gear-digital-servo-micro-p-90039418.html",
           where="retailer spec list", status="UNVERIFIED")
kit.source("SRC-D6-SH0255-PRICE", "SH-0255MG+ price $41.99 (US retailers, Nov 2026)", "web",
           url="https://www.whiterosehobbies.com/products/savox-sh0255mgp-micro-digital-mg-servo-with-soft-start",
           status="UNVERIFIED")
kit.source("SRC-D6-ES3054", "EMAX ES3054 listing (3.0/3.5 kgf cm, 17 g class, 20.1 g measured by one seller)",
           "web", url="https://alofthobbies.com/products/emax-es3054-servo-3-5kg-48-6-oz-in-13-sec-17-grams",
           note="fallback servo, cheaper; fails the unprotected VD case", status="UNVERIFIED")
kit.source("SRC-D6-WIRE", "Music wire ASTM A228: E 200 GPa, G 79 GPa, 7.85 g/cm3, UTS >= 1 700 MPa at 1/8 in",
           "web", url="https://www.astm.org/a0228_a0228m-16.html", status="UNVERIFIED")
kit.source("SRC-D6-CFROD", "Pultruded unidirectional carbon rod 1/8 in: E 110-140 GPa, 1.55-1.6 g/cm3, flexural "
           "strength >= 1 000 MPa", "web", url="https://www.cstsales.com/carbon_rods.html",
           where="rod table; low-end modulus used (110 GPa)", note="weigh and bend-test one rod (T-D6-TWIST)",
           status="UNVERIFIED")
kit.source("SRC-D6-CLEVIS", "Du-Bro 2-56 threaded rod (0.072 in) and 2-56 steel clevis", "web",
           url="https://www.dubro.com/collections/pushrods-and-control-rods", status="UNVERIFIED")
kit.source("SRC-D6-CFTUBE", "Roll-wrapped CF tube 5 x 4 mm x 1 000 mm, 1.55 g/cm3", "web",
           url="https://www.dragonplate.com/", note="any hobby roll-wrapped 5 x 4 tube; G unknown, see ASM-D6-TUBE-G",
           status="UNVERIFIED")
kit.source("SRC-D6-PETG", "PETG filament density 1.27 g/cm3 (maker data sheets)", "web",
           url="https://www.prusa3d.com/product/prusament-petg-jet-black-1kg/", status="UNVERIFIED")

kit.assumption("ASM-D6-CH-LINEAR", "Hinge moment linear in deflection",
               "H(delta) = Ch_max * delta / 25 deg * q c^2 b; Ch_max is B2's inviscid bound at 25 deg",
               basis="XFOIL inviscid HMOM grows close to linearly with deflection (FIG B2-04); the bound at 25 deg is "
                     "kept, so mid-travel values are slightly conservative", status="UNVERIFIED")
kit.assumption("ASM-D6-SERVO-THROW", "Servo throw +/-45 deg at 1000-2000 us",
               "The SH-0255MG+ turns at least +/-45 deg between 1000 and 2000 us (ArduPilot SERVOn_MIN/MAX)",
               basis="typical of digital micro servos; not published for this servo (T-D6-THROW)", value=45.0,
               unit="deg", status="UNVERIFIED")
kit.assumption("ASM-D6-BACKLASH", "Servo output backlash 1 deg", "Free play at the metal-gear output, new servo",
               basis="hobby metal-gear micro servos measure 0.5-1 deg; upper value used", value=1.0, unit="deg",
               status="UNVERIFIED")
kit.assumption("ASM-D6-TUBE-G", "Torque-tube shear modulus 5 GPa", "In-plane shear modulus of a 0/90 roll-wrapped CF "
               "tube", basis="0/90 laminates 4-6 GPa; +/-45 wraps reach 20 GPa; low end used", value=5.0e9, unit="Pa",
               status="UNVERIFIED")
kit.assumption("ASM-D6-XPS-G", "XPS shear modulus 8 MPa", "F-250 class XPS, 25-35 kg/m3",
               basis="published XPS shear moduli 5-12 MPa", value=8.0e6, unit="Pa", status="UNVERIFIED")
kit.assumption("ASM-D6-CLEAR-MIN", "Minimum running clearance 1 mm", "Gap between a moving part and anything it passes, "
               "through the full mechanical travel", basis="print and cut tolerance 0.3-0.5 mm, foam dents",
               value=0.001, unit="m")
kit.assumption("ASM-D6-SLOP-MAX", "Surface free play <= 1 deg", "Worst-case sum of linkage free play at the surface",
               basis="hobby practice for stabilised flying wings; ArduPilot rate loops limit-cycle with more",
               value=1.0, unit="deg")
kit.assumption("ASM-D6-EFF-LOSS-MAX", "Elevon effectiveness loss <= 10 % at VA",
               "Mean panel lag (rod bending + twist) at full travel and VA, as a fraction of the 25 deg travel",
               basis="the loss scales with q: about 6 % at cruise; B3 to confirm against its roll-rate and trim "
                     "margins (CR-D6-08)", value=0.10, unit="-")
kit.assumption("ASM-D6-TAPE-G", "Closed tape skin effective shear modulus 0.5 GPa", "BOPP packing tape, one layer, "
               "LE bevel face taped so the panel skin is a closed cell", basis="BOPP G about 1 GPa; 50 % credit for "
               "adhesive shear lag and overlaps", value=0.5e9, unit="Pa", status="UNVERIFIED")
kit.assumption("ASM-D6-TORQUE-AT-SERVO", "R-SERVO-TORQUE applies at the servo output",
               "The 1.5 x hinge moment is compared with the servo stall torque after the linkage ratio dDelta/dTheta "
               "(virtual work), at the worst point of the travel",
               basis="the servo sees the hinge moment through the four-bar; B2's 3.93 kgf cm assumed 1:1; A2 to "
                     "confirm (CR-D6-07)", status="PROPOSED")


# ---------------------------------------------------------------- helpers (pure)
def interp(xs, ys, x):
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return ys[0] if x < xs[0] else ys[-1]


def rot(X, Z, delta):
    """Rotate a hinge-frame point by delta (TE down positive moves points below the axis forward)."""
    d = math.radians(delta)
    return (X * math.cos(d) + Z * math.sin(d), -X * math.sin(d) + Z * math.cos(d))


def sweep(lo, hi, n=121):
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]


def linkage(xh, sx, szl, rh, rs, xs, above):
    zh = interp(sx, szl[0], xh)
    zs = interp(sx, szl[1], xs) + above
    return (xh, zh, rh, xs, zs, rs)


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-D6-HINGE", title="Elevon hinge moment per servo (two panels)",
          equation="H = Ch_max (delta/25) q c^2 (b_in + b_out), q = rho V^2 / 2",
          inputs={"ch": "P:b2.xfoil.hinge_coef_max", "rho": "P:env.rho_kgm3", "c": "P:wing.chord_m",
                  "yin": "P:wing.elevon.inboard_y_m", "yout": "P:wing.elevon.outboard_y_m", "vd": "P:requirements.vd_ms",
                  "va": "ASM-F4-VA-SCHED", "vc": "P:performance.cruise_ms", "trim": "CL-B3-ELEVON-TRIM-CRUISE",
                  "defl": "P:wing.elevon.deflection_deg"},
          units={"rho": "kg/m3", "c": "m", "yin": "m", "yout": "m", "vd": "m/s", "va": "m/s", "vc": "m/s"},
          assumes=["ASM-D6-CH-LINEAR", "ASM-B2-HINGE-INVISCID"])
def hinge(ch, rho, c, yin, yout, vd, va, vc, trim, defl):
    bi, bo = yin[1] - yin[0], yout[1] - yout[0]
    dmax = max(abs(defl[0]), abs(defl[1]))
    H = lambda v, d: ch * (abs(d) / 25.0) * 0.5 * rho * v * v * c * c * (bi + bo)
    return {"H_vd_full_Nm": H(vd, dmax), "H_va_full_Nm": H(va, dmax), "H_cruise_trim_Nm": H(vc, trim),
            "share_out": bo / (bi + bo), "b_in_m": bi, "b_out_m": bo, "q_vd_Pa": 0.5 * rho * vd * vd}


@kit.calc("CALC-D6-KIN", title="Servo-to-elevon four-bar: throw, ratio, torque factor",
          equation="|P(theta) - Q(delta)| = L0; k(theta) = d delta / d theta; worst servo torque / H25 = "
                   "max over travel of (delta/25) k",
          inputs={"xh": "CL-A5-HINGE-X", "sx": "P:mec.section.x_m", "szu": "P:mec.section.zu_m",
                  "szl": "P:mec.section.zl_m", "rh": "P:mec.horn.r_m", "rs": "P:mec.arm.r_m",
                  "xs": "P:mec.station.shaft_x_m", "above": "P:mec.station.shaft_above_skin_m",
                  "defl": "P:wing.elevon.deflection_deg", "stop": "P:mec.mech_stop_deg"},
          units={"xh": "m", "rh": "m", "rs": "m", "xs": "m", "above": "m"})
def kinematics(xh, sx, szu, szl, rh, rs, xs, above, defl, stop):
    lk = linkage(xh, sx, (szu, szl), rh, rs, xs, above)
    dmax = max(abs(defl[0]), abs(defl[1]))
    th_dn, th_up = MEC.theta_of_delta(lk, dmax), MEC.theta_of_delta(lk, -dmax)
    ratio = lambda t, h=0.05: abs(MEC.delta_of_theta(lk, t + h) - MEC.delta_of_theta(lk, t - h)) / (2 * h)
    worst = 0.0
    for t in sweep(min(th_dn, th_up), max(th_dn, th_up), 181):
        worst = max(worst, abs(MEC.delta_of_theta(lk, t)) / 25.0 * ratio(t))
    return {"theta_dn_deg": th_dn, "theta_up_deg": th_up, "theta_need_deg": max(abs(th_dn), abs(th_up)),
            "theta_stop_dn_deg": MEC.theta_of_delta(lk, stop), "theta_stop_up_deg": MEC.theta_of_delta(lk, -stop),
            "k_neutral": ratio(0.0), "k_end_dn": ratio(th_dn), "k_end_up": ratio(th_up), "torque_factor": worst,
            "rod_len_m": MEC.rod_length(lk)}


@kit.calc("CALC-D6-SERVO", title="Servo torque required at the output vs rating",
          equation="T = SF x H x torque_factor (four-bar, worst point); kgf cm = N m / g x 100",
          inputs={"hvd": "CL-D6-H-VD-FULL", "hva": "CL-D6-H-VA-FULL", "tf": "CL-D6-TORQUE-FACTOR",
                  "sf": "P:requirements.servo_torque_factor"}, units={"hvd": "N*m", "hva": "N*m"},
          assumes=["ASM-D6-TORQUE-AT-SERVO"])
def servo_torque(hvd, hva, tf, sf):
    t = lambda h: sf * h * tf / G0 * 100
    return {"T_req_vd_kgfcm": t(hvd), "T_req_va_kgfcm": t(hva), "T_hold_vd_kgfcm": hvd * tf / G0 * 100,
            "T_req_1to1_vd_kgfcm": sf * hvd / G0 * 100}


@kit.calc("CALC-D6-PUSHROD", title="Pushrod force, buckling and horn bond area",
          equation="F = H / (r_h sin phi) worst; Pcr = pi^2 E I / L^2; A_min = F sf ff pf / (kd sigma_XPS)",
          inputs={"hvd": "CL-D6-H-VD-FULL", "xh": "CL-A5-HINGE-X", "sx": "P:mec.section.x_m",
                  "szu": "P:mec.section.zu_m", "szl": "P:mec.section.zl_m", "rh": "P:mec.horn.r_m",
                  "rs": "P:mec.arm.r_m", "xs": "P:mec.station.shaft_x_m", "above": "P:mec.station.shaft_above_skin_m",
                  "d": "P:mec.pushrod.d_m", "E": "P:mec.pushrod.e_pa", "sf": "P:requirements.safety_factor_ult",
                  "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR", "kd": "ASM-C6-FOAM-KD",
                  "s_xps": "ASM-D3-XPS-TENSILE", "flange": "P:mec.horn.flange_mm", "back": "P:mec.horn.backplate_mm",
                  "blade": "P:mec.horn.blade_x_mm", "defl": "P:wing.elevon.deflection_deg"},
          units={"hvd": "N*m", "xh": "m", "rh": "m", "rs": "m", "xs": "m", "above": "m", "d": "m", "E": "Pa"})
def pushrod(hvd, xh, sx, szu, szl, rh, rs, xs, above, d, E, sf, ff, pf, kd, s_xps, flange, back, blade, defl):
    lk = linkage(xh, sx, (szu, szl), rh, rs, xs, above)
    L0 = MEC.rod_length(lk)
    dmax = max(abs(defl[0]), abs(defl[1]))
    fmax = 0.0
    for dl in sweep(-dmax, dmax, 101):
        th = MEC.theta_of_delta(lk, dl)
        p, q = MEC.arm_hole(lk, th), MEC.horn_hole(lk, dl)
        ux, uz = (p[0] - q[0]) / L0, (p[1] - q[1]) / L0
        ax, az = q[0] - lk[0], q[1] - lk[1]                         # horn arm vector
        lever = abs(ax * uz - az * ux)                              # r_h sin(phi)
        fmax = max(fmax, hvd * abs(dl) / 25.0 / lever)
    I = math.pi * d ** 4 / 64
    pcr = math.pi ** 2 * E * I / L0 ** 2
    fd = fmax * sf * ff * pf
    a_min = fd / (kd * s_xps) * 1e6
    zu = lambda x: interp(sx, szu, x)
    zl = lambda x: interp(sx, szl, x)
    t_blade = sum(zu(xh + x / 1000) - zl(xh + x / 1000) for x in sweep(blade[0], blade[1], 21)) / 21
    area = (flange[1] - flange[0]) * flange[2] + (back[1] - back[0]) * back[2] + \
        2 * (blade[1] - blade[0]) * t_blade * 1000
    return {"F_max_N": fmax, "F_design_N": fd, "Pcr_N": pcr, "buckling_sf": pcr / fmax, "A_min_mm2": a_min,
            "A_horn_mm2": area, "rod_len_m": L0}


@kit.calc("CALC-D6-CLEAR", title="Clearances through the full mechanical travel",
          equation="min over delta in [-stop, stop] of the gaps: bridge rod to fin notch sides, bottom and the "
                   "fixed-core skin; horn arm to the core lower skin; pushrod to the lower skin; clevis to the boss; "
                   "horn plate to the clevis slot bottom",
          inputs={"xh": "CL-A5-HINGE-X", "sx": "P:mec.section.x_m", "szu": "P:mec.section.zu_m",
                  "szl": "P:mec.section.zl_m", "rb": "P:mec.horn.bridge_r_m", "rod_d": "P:mec.link.d_m",
                  "hw": "P:fin_detail.link_slot.half_width_m", "depth": "P:fin_detail.link_slot.depth_m",
                  "outline": "P:mec.horn.outline_mm", "flange": "P:mec.horn.flange_mm", "rh": "P:mec.horn.r_m",
                  "rs": "P:mec.arm.r_m", "xs": "P:mec.station.shaft_x_m", "above": "P:mec.station.shaft_above_skin_m",
                  "pr_d": "P:mec.pushrod.d_m", "clevis": "P:mec.pushrod.clevis_mm", "boss_od": "P:mec.horn.boss_od_m",
                  "cover_t": "P:mec.cover.t_m", "stop": "P:mec.mech_stop_deg"},
          units={"xh": "m", "rb": "m", "rod_d": "m", "hw": "m", "depth": "m", "rh": "m", "rs": "m", "xs": "m",
                 "above": "m", "pr_d": "m", "boss_od": "m", "cover_t": "m"})
def clearances(xh, sx, szu, szl, rb, rod_d, hw, depth, outline, flange, rh, rs, xs, above, pr_d, clevis, boss_od,
               cover_t, stop):
    zl = lambda x: interp(sx, szl, x)
    lk = linkage(xh, sx, (szu, szl), rh, rs, xs, above)
    zh = lk[1]
    r = rod_d / 2
    notch_bottom = zl(xh) - depth
    side = bottom = skin = horn = rodp = clev = slot = 1.0
    pts = [(X / 1000, Z / 1000) for X, Z in outline]
    edge_pts = []
    for (a, b), (c, d) in zip(pts, pts[1:] + pts[:1]):
        edge_pts += [(a + (c - a) * i / 10, b + (d - b) * i / 10) for i in range(10)]
    fx0 = flange[0] / 1000
    edge_pts += [(fx0, zl(xh + fx0) - zh - flange[3] / 1000)]
    L0 = MEC.rod_length(lk)
    cl_len, cl_h, cl_slot = clevis[0] / 1000, clevis[2] / 1000, clevis[3] / 1000
    for dl in sweep(-stop, stop, 121):
        bx, bz = rot(0.0, -rb, dl)
        x, z = xh + bx, zh + bz
        side = min(side, hw - abs(bx) - r)
        bottom = min(bottom, (z - r) - notch_bottom)
        skin = min(skin, zl(x) - (z + r))
        if dl > 0:                                                  # TE down: arm swings under the core
            for X, Z in edge_pts:
                px, pz = rot(X, Z, dl)
                if px < 0:
                    horn = min(horn, zl(xh + px) - (zh + pz))
        th = MEC.theta_of_delta(lk, dl)
        p, q = MEC.arm_hole(lk, th), MEC.horn_hole(lk, dl)
        for i in range(1, 20):
            t = i / 20
            x_, z_ = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
            if x_ > xs + rs + 0.002:                                   # outside the arm slot
                rodp = min(rodp, (zl(x_) - cover_t) - (z_ + pr_d / 2))
        ux, uz = (p[0] - q[0]) / L0, (p[1] - q[1]) / L0
        cx, cz = xh + bx - q[0], zh + bz - q[1]                     # boss centre from the pin
        along = max(0.0, min(cl_len, cx * ux + cz * uz))
        dist = math.hypot(cx - along * ux, cz - along * uz)
        clev = min(clev, dist - cl_h / 2 - boss_od / 2)
        for X, Z in pts:                                            # horn plate inside the clevis slot
            px, pz = rot(X, Z, dl)
            vx, vz = xh + px - q[0], zh + pz - q[1]
            al, pe = vx * ux + vz * uz, abs(-vx * uz + vz * ux)
            if al > 0 and pe < cl_h / 2:
                slot = min(slot, cl_slot - al)
    return {"rod_notch_side_m": side, "rod_notch_bottom_m": bottom, "rod_core_skin_m": skin, "horn_core_m": horn,
            "pushrod_skin_m": rodp, "clevis_boss_m": clev,
            "clevis_slot_m": slot, "min_m": min(side, bottom, skin, horn, rodp, clev, slot)}


@kit.calc("CALC-D6-SLOP", title="Surface free play, worst-case sum",
          equation="slop = backlash x k_neutral + (play_arm + play_horn) / r_h (rad -> deg)",
          inputs={"bl": "ASM-D6-BACKLASH", "k": "CL-D6-K-NEUTRAL", "play": "P:mec.pushrod.hole_play_mm",
                  "rh": "P:mec.horn.r_m"}, units={"bl": "deg", "rh": "m"})
def slop(bl, k, play, rh):
    gear = bl * k
    holes = math.degrees((play[0] + play[1]) / 1000 / rh)
    return {"slop_deg": gear + holes, "gear_deg": gear, "holes_deg": holes}


@kit.calc("CALC-D6-BRIDGE", title="Inter-panel rod lag, panel twist and elevon effectiveness loss",
          equation="rod: fixed-guided beam, d = F L^3 / (12 E I), F = H_out / r_b, lag = d / r_b; panel: uniform "
                   "torque m from the drive point, tube over the first a L (GJ_h), skin + foam beyond (GJ_l): tip = "
                   "m L^2 [(a - a^2/2)/GJ_h + (1-a)^2/(2 GJ_l)], mean = m L^2 [(a^2/2 - a^3/6 + (a - a^2/2)(1-a))/GJ_h "
                   "+ (1-a)^3/(3 GJ_l)] (a = 1: tip m L^2/2GJ, mean 2/3 tip); GJ = G_tube J_tube + "
                   "4 A^2 G_skin t / s (closed tape box) + G_xps c_e t^3 / 12; loss = mean lag / 25 deg",
          inputs={"hva": "CL-D6-H-VA-FULL", "hvd": "CL-D6-H-VD-FULL", "share": "CL-D6-SHARE-OUT",
                  "rb": "P:mec.horn.bridge_r_m", "d": "P:mec.link.d_m", "E": "P:mec.link.e_pa",
                  "ya": "P:mec.station.arm_plane_y_m", "yo": "P:mec.station.outboard_horn_y_m",
                  "boss": "P:mec.horn.boss_len_m", "ht": "P:mec.horn.plate_t_m", "tube": "P:mec.tube.od_id_m",
                  "gt": "ASM-D6-TUBE-G", "gf": "ASM-D6-XPS-G", "ts": "P:mec.panel.skin_t_m",
                  "gs": "P:mec.panel.skin_g_eff_pa", "c": "P:wing.chord_m", "cf": "P:wing.elevon.chord_frac",
                  "xh": "CL-A5-HINGE-X", "sx": "P:mec.section.x_m", "szu": "P:mec.section.zu_m",
                  "szl": "P:mec.section.zl_m", "yin": "P:wing.elevon.inboard_y_m",
                  "yout": "P:wing.elevon.outboard_y_m", "defl": "P:wing.elevon.deflection_deg",
                  "afrac": "P:mec.tube.cover_frac"},
          units={"hva": "N*m", "hvd": "N*m", "rb": "m", "d": "m", "E": "Pa", "ya": "m", "yo": "m", "boss": "m",
                 "ht": "m", "c": "m", "xh": "m", "gt": "Pa", "gf": "Pa", "ts": "m", "gs": "Pa"},
          assumes=["ASM-D6-TAPE-G"])
def bridge(hva, hvd, share, rb, d, E, ya, yo, boss, ht, tube, gt, gf, ts, gs, c, cf, xh, sx, szu, szl, yin, yout,
           defl, afrac):
    L = (yo - ya) - ht - 2 * boss
    EI = E * math.pi * d ** 4 / 64
    lag = lambda h: math.degrees(h * share / rb * L ** 3 / (12 * EI) / rb)
    sigma = hvd * share / rb * L / 2 / (math.pi * d ** 3 / 32)
    xs_ = sweep(xh, c, 41)
    th = [interp(sx, szu, x) - interp(sx, szl, x) for x in xs_]
    A = sum((th[i] + th[i + 1]) / 2 * (xs_[i + 1] - xs_[i]) for i in range(40))
    seg = lambda z: sum(math.hypot(xs_[i + 1] - xs_[i], interp(sx, z, xs_[i + 1]) - interp(sx, z, xs_[i]))
                        for i in range(40))
    s = seg(szu) + seg(szl) + th[0] / math.cos(math.radians(30.0))
    t_h = th[0]
    GJ_tube = gt * math.pi * (tube[0] ** 4 - tube[1] ** 4) / 32
    GJ_skin = 4 * A * A * gs * ts / s
    GJ_foam = gf * c * cf * t_h ** 3 / 12
    GJ = GJ_tube + GJ_skin + GJ_foam
    b_in, b_out = yin[1] - yin[0], yout[1] - yout[0]
    l_in = ya - yin[0]                                              # inboard panel driven near its outer end
    l_out = yout[1] - yo                                            # outboard panel driven near its inner end
    GJ_l = GJ_skin + GJ_foam                                        # panel beyond the end of the tube

    def tw(h, b, l, a, gjh, gjl):
        k = h / b * l * l
        tip = k * ((a - a * a / 2) / gjh + (1 - a) ** 2 / (2 * gjl))
        mean = k * ((a * a / 2 - a ** 3 / 6 + (a - a * a / 2) * (1 - a)) / gjh + (1 - a) ** 3 / (3 * gjl))
        return math.degrees(tip), math.degrees(mean)
    dmax = max(abs(defl[0]), abs(defl[1]))
    a_in, a_out = afrac
    tw_out, m_out = tw(hva * share, b_out, l_out, a_out, GJ, GJ_l)
    tw_in, m_in = tw(hva * (1 - share), b_in, l_in, a_in, GJ, GJ_l)
    return {"lag_va_deg": lag(hva), "lag_vd_deg": lag(hvd), "rod_sigma_vd_Pa": sigma, "rod_free_len_m": L,
            "twist_out_va_deg": tw_out, "twist_in_va_deg": tw_in,
            "twist_out_va_foam_only_deg": tw(hva * share, b_out, l_out, 1.0, GJ_foam, GJ_foam)[0],
            "out_total_va_deg": lag(hva) + tw_out, "GJ_Nm2": GJ, "GJ_tube_Nm2": GJ_tube, "GJ_skin_Nm2": GJ_skin,
            "loss_out_va": (lag(hva) + m_out) / dmax, "loss_in_va": m_in / dmax,
            "loss_in_va_full_tube": tw(hva * (1 - share), b_in, l_in, 1.0, GJ, GJ_l)[1] / dmax,
            "loss_in_va_no_tube": tw(hva * (1 - share), b_in, l_in, 0.0, GJ, GJ_l)[1] / dmax}


@kit.calc("CALC-D6-ROD-TRADE", title="Bridge-rod choice: outboard effectiveness loss and mass per rod",
          equation="lag_alt = lag x (E d^4) / (E_alt d_alt^4) (same fixed-guided beam); loss_alt = loss + (lag_alt - "
                   "lag) / 25 deg; m = pi d^2 / 4 x L_cut x rho",
          inputs={"lag": "CL-D6-BRIDGE-LAG-VA", "loss": "CL-D6-EFF-LOSS-OUT", "d": "P:mec.link.d_m",
                  "E": "P:mec.link.e_pa", "alt": "P:mec.link.trade_d_e", "rho_cf": "P:mec.link.rod_gcc",
                  "rho_st": "P:mec.link.steel_gcc", "defl": "P:wing.elevon.deflection_deg",
                  "ya": "P:mec.station.arm_plane_y_m", "yo": "P:mec.station.outboard_horn_y_m"},
          units={"lag": "deg", "d": "m", "E": "Pa", "rho_cf": "g/cm3", "rho_st": "g/cm3", "ya": "m", "yo": "m"})
def rod_trade(lag, loss, d, E, alt, rho_cf, rho_st, defl, ya, yo):
    dmax = max(abs(defl[0]), abs(defl[1]))
    L_cut = yo - ya - 0.003                                         # 67 mm: the rod stops short of each horn face
    out = {"mass_chosen_g": math.pi / 4 * d * d * L_cut * 1e6 * rho_cf}
    for key, (da, Ea) in zip(("steel_3_32", "cf_2mm", "steel_1_8"), alt):
        la = lag * (E * d ** 4) / (Ea * da ** 4)
        out["loss_out_" + key] = loss + (la - lag) / dmax
        out["mass_" + key + "_g"] = math.pi / 4 * da * da * L_cut * 1e6 * (rho_st if Ea > 150e9 else rho_cf)
    return out


@kit.calc("CALC-D6-FRAME-BOND", title="Servo frame bonded area and the area its load needs",
          equation="A = rim (Lx Ly - (Lx - 2r)(Ly - 2r)) + inboard wall Lx Hz + 2 end walls Ly Hz; Lx = ear span + "
                   "2 w, Ly = H + boss + t_arm + c + w (1.5 mm arm gap left out: conservative), Hz = W + c + w; "
                   "F = T_stall / r_arm + T_stall / Lx; A_min = F sf ff pf / (kd sigma_XPS) (C6 method)",
          inputs={"case": "P:mec.servo.case_m", "boss": "P:mec.servo.spline_boss_m", "ear": "P:mec.servo.ear_span_m",
                  "at": "P:mec.arm.t_m", "w": "P:mec.frame.wall_m", "cl": "P:mec.frame.clear_m",
                  "rim": "P:mec.frame.window_rim_m", "T": "P:mec.servo.stall_torque_6v_kgfcm", "rs": "P:mec.arm.r_m",
                  "sf": "P:requirements.safety_factor_ult", "ff": "ASM-C1-FITTING-FACTOR",
                  "pf": "ASM-C1-PRINTED-FACTOR", "kd": "ASM-C6-FOAM-KD", "s_xps": "ASM-D3-XPS-TENSILE"},
          units={"case": "m", "boss": "m", "ear": "m", "at": "m", "w": "m", "cl": "m", "rim": "m", "T": "kgf*cm",
                 "rs": "m"})
def frame_bond(case, boss, ear, at, w, cl, rim, T, rs, sf, ff, pf, kd, s_xps):
    L, W, H = case
    Lx, Ly, Hz = ear + 2 * w, H + boss + at + cl + w, W + cl + w
    a_rim = Lx * Ly - (Lx - 2 * rim) * (Ly - 2 * rim)
    area = (a_rim + Lx * Hz + 2 * Ly * Hz) * 1e6
    Tn = T * G0 / 100
    F = Tn / rs + Tn / Lx
    return {"A_frame_mm2": area, "A_min_mm2": F * sf * ff * pf / (kd * s_xps) * 1e6, "F_design_N": F,
            "A_rim_mm2": a_rim * 1e6}


@kit.calc("CALC-D6-SUPPLY", title="Servo supply demand for F1",
          equation="I_req = k_bec x n_servo x I_stall", inputs={"k": "P:requirements.ubec_factor",
                                                               "i": "P:mec.servo.stall_current_6v_a"},
          units={"i": "A"})
def supply(k, i):
    return {"i_req_a": k * 2 * i, "i_bus_stall_a": 2 * i}


@kit.calc("CALC-D6-MASS", title="Mechanisms mass vs allocation", equation="sum of the declared part masses",
          inputs={"m": "P:mec.mass_total_g", "alloc": "P:mass.allocation_g.mechanisms"}, units={"m": "g", "alloc": "g"})
def mass(m, alloc):
    return {"mass_g": m, "over_g": m - alloc}


# ---------------------------------------------------------------- claims
kit.claim("CL-D6-H-VD-FULL", "Hinge moment per servo, full 25 deg at VD 27.2 m/s", calc="CALC-D6-HINGE",
          output="H_vd_full_Nm", unit="N*m", parts=SERVOS, how="T-B2-HINGE bench load scaled to q at VD")
kit.claim("CL-D6-H-VA-FULL", "Hinge moment per servo, full 25 deg at VA 20.5 m/s", calc="CALC-D6-HINGE",
          output="H_va_full_Nm", unit="N*m", parts=SERVOS, how="T-B2-HINGE")
kit.claim("CL-D6-H-CRUISE", "Hinge moment per servo at cruise trim", calc="CALC-D6-HINGE", output="H_cruise_trim_Nm",
          unit="N*m", parts=SERVOS, how="Information: holding load in cruise")
kit.claim("CL-D6-SHARE-OUT", "Outboard panel share of the hinge moment", calc="CALC-D6-HINGE", output="share_out",
          unit="-", parts=BRIDGE, how="Information: span ratio")
kit.claim("CL-D6-THROW-NEED", "Servo angle needed for +/-25 deg surface", calc="CALC-D6-KIN",
          output="theta_need_deg", unit="deg", limit=("<=", "ASM-D6-SERVO-THROW"), parts=LINK,
          how="T-D6-THROW: protractor on the panel, set SERVOn_MIN/MAX/TRIM for +/-25 deg, read the arm angle")
kit.claim("CL-D6-K-NEUTRAL", "Linkage ratio at neutral (surface deg per servo deg)", calc="CALC-D6-KIN",
          output="k_neutral", unit="-", parts=LINK, how="T-D6-THROW slope at neutral")
kit.claim("CL-D6-TORQUE-FACTOR", "Worst servo torque / hinge moment at 25 deg over the travel", calc="CALC-D6-KIN",
          output="torque_factor", unit="-", parts=LINK, how="Bench: spring scale on the arm vs weight on the panel")
kit.claim("CL-D6-SERVO-TORQUE-REQ", "Servo stall torque required at the output, VD full travel x 1.5",
          calc="CALC-D6-SERVO", output="T_req_vd_kgfcm", unit="kgf*cm", limit=("<=", "P:mec.servo.stall_torque_6v_kgfcm"),
          verifies=["R-SERVO-TORQUE"], parts=SERVOS,
          how="T-B2-HINGE at the VD hinge moment: the servo holds 25 deg on the 6 V rail; T-D6-THROW")
kit.claim("CL-D6-SERVO-TORQUE-48V", "Servo torque required, VA full travel x 1.5, against the 4.8 V rating",
          calc="CALC-D6-SERVO", output="T_req_va_kgfcm", unit="kgf*cm",
          limit=("<=", "P:mec.servo.stall_torque_48v_kgfcm"), parts=SERVOS,
          how="Margin if the rail sags: bench at 4.8 V")
kit.claim("CL-D6-SERVO-TORQUE-1TO1", "Servo torque if the linkage were 1:1 (B2's basis), VD full x 1.5",
          calc="CALC-D6-SERVO", output="T_req_1to1_vd_kgfcm", unit="kgf*cm", parts=SERVOS,
          how="Information: why the four-bar ratio matters")
kit.claim("CL-D6-PUSHROD-F", "Pushrod force, VD full travel (limit)", calc="CALC-D6-PUSHROD", output="F_max_N",
          unit="N", parts=LINK, how="Spring scale at the clevis during T-B2-HINGE")
kit.claim("CL-D6-PUSHROD-BUCKLING", "Pushrod Euler buckling factor at the limit force", calc="CALC-D6-PUSHROD",
          output="buckling_sf", unit="-", limit=(">=", 3.0), parts=["MEC-003-L", "MEC-003-R"],
          how="Pushrod does not bow visibly at the T-B2-HINGE load")
kit.claim("CL-D6-BOND-HORN", "Horn bonded area into XPS (flange + backplate + slot walls)", calc="CALC-D6-PUSHROD",
          output="A_horn_mm2", unit="mm2", limit=(">=", "CL-C6-LINK-BOND-AREA-MIN"),
          parts=["MEC-004-L", "MEC-004-R", "MEC-006-L", "MEC-006-R"], how="T-C6-XPS-PULL; horn pull-off coupon")
kit.claim("CL-D6-BOND-HORN-NEED", "Horn bond area needed at the D6 pushrod force (C6 method)", calc="CALC-D6-PUSHROD",
          output="A_min_mm2", unit="mm2", limit=("<=", "CL-D6-BOND-HORN"), parts=["MEC-004-L", "MEC-004-R"],
          how="T-C6-XPS-PULL")
kit.claim("CL-D6-CLEAR-MIN", "Smallest running clearance through +/-30 deg", calc="CALC-D6-CLEAR", output="min_m",
          unit="m", limit=(">=", "ASM-D6-CLEAR-MIN"), parts=BRIDGE + LINK,
          how="T-D6-THROW: drive to both stops, feeler gauge at the notch, horn and pushrod")
for key, title in (("rod_notch_side_m", "Bridge rod to fin notch sides"), ("rod_notch_bottom_m", "Bridge rod to "
                   "notch bottom"), ("rod_core_skin_m", "Bridge rod to the fixed-core lower skin"),
                   ("horn_core_m", "Horn arm to the core lower skin (TE down)"),
                   ("pushrod_skin_m", "Pushrod to the lower skin"), ("clevis_boss_m", "Clevis to the rod boss"),
                   ("clevis_slot_m", "Horn plate to the clevis slot bottom")):
    kit.claim("CL-D6-CLEAR-" + key.split("_m")[0].upper().replace("_", "-"), title, calc="CALC-D6-CLEAR", output=key,
              unit="m", limit=(">=", "ASM-D6-CLEAR-MIN"), parts=BRIDGE, how="T-D6-THROW feeler gauge")
kit.claim("CL-D6-SLOP", "Surface free play, worst-case sum", calc="CALC-D6-SLOP", output="slop_deg", unit="deg",
          limit=("<=", "ASM-D6-SLOP-MAX"), parts=LINK + ["MEC-001-L", "MEC-001-R"],
          how="T-D6-SLOP: servo powered at neutral, dial or protractor at the panel TE, push both ways")
kit.claim("CL-D6-BRIDGE-LAG-VA", "Outboard panel lag from rod bending, VA full", calc="CALC-D6-BRIDGE",
          output="lag_va_deg", unit="deg", parts=BRIDGE, how="T-D6-TWIST")
kit.claim("CL-D6-TWIST-OUT-VA", "Outboard panel far-end lag (rod + panel twist), VA full", calc="CALC-D6-BRIDGE",
          output="out_total_va_deg", unit="deg", parts=BRIDGE + TUBES,
          how="T-D6-TWIST: weight on the panel tip TE, protractor at both ends")
kit.claim("CL-D6-TWIST-IN-VA", "Inboard panel far-end twist, VA full", calc="CALC-D6-BRIDGE",
          output="twist_in_va_deg", unit="deg", parts=TUBES, how="T-D6-TWIST")
kit.claim("CL-D6-EFF-LOSS-OUT", "Outboard panel effectiveness loss at VA (mean lag / travel)", calc="CALC-D6-BRIDGE",
          output="loss_out_va", unit="-", limit=("<=", "ASM-D6-EFF-LOSS-MAX"), parts=BRIDGE + TUBES,
          how="T-D6-TWIST")
kit.claim("CL-D6-EFF-LOSS-IN", "Inboard panel effectiveness loss at VA (mean lag / travel)", calc="CALC-D6-BRIDGE",
          output="loss_in_va", unit="-", limit=("<=", "ASM-D6-EFF-LOSS-MAX"), parts=TUBES, how="T-D6-TWIST")
kit.claim("CL-D6-EFF-LOSS-IN-FULL-TUBE", "Inboard panel loss if its tube ran the full panel (R1)",
          calc="CALC-D6-BRIDGE", output="loss_in_va_full_tube", unit="-", parts=TUBES,
          how="Information: cost of the 30 % shorter inboard tube (D6-R2, -1.7 g)")
kit.claim("CL-D6-EFF-LOSS-IN-NO-TUBE", "Inboard panel loss with no tube (closed tape skin only)",
          calc="CALC-D6-BRIDGE", output="loss_in_va_no_tube", unit="-", parts=TUBES,
          how="Information: why both panels keep a tube (above the 10 % limit)")
kit.claim("CL-D6-ROD-MASS", "Bridge rod mass, 1/8 in pultruded CF, 67 mm", calc="CALC-D6-ROD-TRADE",
          output="mass_chosen_g", unit="g", parts=["MEC-005-L", "MEC-005-R"], how="T-D6-WEIGH")
kit.claim("CL-D6-EFF-LOSS-OUT-332-STEEL", "Outboard loss with a 3/32 in music-wire rod (A1 D-48 fallback)",
          calc="CALC-D6-ROD-TRADE", output="loss_out_steel_3_32", unit="-", parts=["MEC-005-L", "MEC-005-R"],
          how="Information: rejected option (heavier and more lag than CF 1/8 in)")
kit.claim("CL-D6-EFF-LOSS-OUT-2MM-CF", "Outboard loss with a 2 mm CF rod (A3 suggestion)", calc="CALC-D6-ROD-TRADE",
          output="loss_out_cf_2mm", unit="-", parts=["MEC-005-L", "MEC-005-R"],
          how="Information: rejected option (above the 10 % limit)")
kit.claim("CL-D6-ROD-MASS-R1", "Bridge rod mass, 1/8 in music wire (R1)", calc="CALC-D6-ROD-TRADE",
          output="mass_steel_1_8_g", unit="g", parts=["MEC-005-L", "MEC-005-R"], how="Information: R1 baseline")
kit.claim("CL-D6-BOND-FRAME", "Servo frame bonded area into XPS (top-plate rim + three walls)",
          calc="CALC-D6-FRAME-BOND", output="A_frame_mm2", unit="mm2", limit=(">=", "CL-C6-LINK-BOND-AREA-MIN"),
          parts=["MEC-008-L", "MEC-008-R"], how="T-C6-XPS-PULL; frame pull-off coupon")
kit.claim("CL-D6-BOND-FRAME-NEED", "Frame bond area needed at servo stall (C6 method)", calc="CALC-D6-FRAME-BOND",
          output="A_min_mm2", unit="mm2", limit=("<=", "CL-D6-BOND-FRAME"), parts=["MEC-008-L", "MEC-008-R"],
          how="T-C6-XPS-PULL")
kit.claim("CL-D6-TWIST-FOAM-ONLY", "Outboard panel twist with bare foam (no tube, open skin), VA full",
          calc="CALC-D6-BRIDGE", output="twist_out_va_foam_only_deg", unit="deg", parts=TUBES,
          how="Information: why the tubes and the closed skin are needed")
kit.claim("CL-D6-ROD-STRESS", "Bridge rod bending stress, VD full", calc="CALC-D6-BRIDGE", output="rod_sigma_vd_Pa",
          unit="Pa", limit=("<=", 1.0e9), parts=["MEC-005-L", "MEC-005-R"], how="No set in the rod after T-B2-HINGE")
kit.claim("CL-D6-SERVO-SUPPLY", "Servo supply rating required (2 servos stalled x 2)", calc="CALC-D6-SUPPLY",
          output="i_req_a", unit="A", limit=("<=", "CL-F1-UBEC-RATING"), parts=SERVOS,
          how="T-F1-SERVO-STALL")
kit.claim("CL-D6-MASS", "Mechanisms mass", calc="CALC-D6-MASS", output="mass_g", unit="g",
          limit=("<=", "P:mass.allocation_g.mechanisms"), parts=SERVOS, how="T-D6-WEIGH: weigh every part on arrival")

kit.test("T-D6-THROW", "Servo throw, ratio and stops", verifies=["CL-D6-THROW-NEED", "CL-D6-CLEAR-MIN"],
         procedure="Wing on the bench, servo on the 6 V rail: set SERVOn_MIN/MAX for +/-25 deg (protractor on the TE), "
                   "read the arm angle, then drive to the 30 deg stops by hand: feeler gauge >= 1 mm at the notch, "
                   "horn and pushrod")
kit.test("T-D6-SLOP", "Surface free play", verifies=["CL-D6-SLOP"],
         procedure="Servo powered at neutral; push the TE up and down with 0.5 N; dial gauge at the TE; play / "
                   "elevon chord -> deg; <= 1.0 deg per panel")
kit.test("T-D6-TWIST", "Panel twist and lag under load", verifies=["CL-D6-EFF-LOSS-OUT", "CL-D6-EFF-LOSS-IN"],
         procedure="Servo at +25 deg; hang the VA hinge moment share as weights at the far-end TE of each panel; "
                   "protractor at both ends; mean lag <= 2.5 deg (10 %)")
kit.test("T-D6-WEIGH", "Weigh the mechanisms parts", verifies=["CL-D6-MASS"],
         procedure="Kitchen scale 0.1 g: servo, arm, horns, rods, tubes, frames, covers; update parts.csv")

if __name__ == "__main__":
    kit.write()
