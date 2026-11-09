"""B3 hand models that AVL does not cover: propeller and tube terms, trimmed CLmax, hover authority, transition.

Pure functions (standard library only). Units SI, frame of params.json (x aft, y right, z up in cruise).
Hover axes follow ArduPilot tailsitter convention: hover pitch = about cruise y, hover roll = about cruise z,
hover yaw = about cruise x (the thrust axis).
"""
from __future__ import annotations

import math


# ------------------------------------------------------------------------------------ propeller and drag terms
def prop_terms(n, D, x_prop, x_ref, S, c, b, cn_alpha_disk, upwash):
    """Ribner propeller normal force for n tractor props at x_prop, reduced to the wing reference.
    cn_alpha_disk = dCN/dalpha per prop based on disk area and freestream q (per rad).
    Returns dCLa (pitch plane, with upwash factor), dCmA about x_ref, dCYb, dCnb (no sidewash factor)."""
    A = math.pi * D * D / 4
    dCN = n * cn_alpha_disk * A / S              # per rad, on S
    arm = x_ref - x_prop                         # > 0: props ahead of the reference
    return {"dCLa": dCN * upwash, "dCma": dCN * upwash * arm / c,          # nose-up per rad (destabilising)
            "dCYb": -dCN, "dCnb": -dCN * arm / b}


def drag_items_dCnb(items, x_ref, S, b):
    """Side force from drag of bluff items rotating with the wind in sideslip: dCY/dbeta = -sum(CD A)/S each at x.
    items = [(CD*A m2, x m)]. Items ahead of x_ref are directionally destabilising."""
    return sum(-cda / S * (x_ref - x) / b for cda, x in items)


def pod_dCma(vol, S, c, k=1.0):
    """Munk slender-body destabilising pitch moment of the pod, dCm/dalpha = 2 k vol / (S c) per rad."""
    return 2 * k * vol / (S * c)


# ------------------------------------------------------------------------------------ trimmed lift
def trimmed_clmax(clmax_clean, cm_ac, sm, cld, cmd_ref, x_cg, x_ref, c):
    """Max trimmed CL with elevons. Cm = cm_ac - CL*sm + Cmd(x_cg)*delta = 0 ; CLmax_t = clmax + CLd*delta.
    cld, cmd per deg (already scaled by flap effectiveness). Returns (CLmax_t, delta_deg; negative = TE up)."""
    cmd = cmd_ref + cld * (x_cg - x_ref) / c          # elevon moment about the actual CG
    # delta = (CL*sm - cm_ac)/cmd ; CL = clmax + cld*delta -> linear in CL
    # CL = clmax + cld*(CL*sm - cm_ac)/cmd  ->  CL (1 - cld*sm/cmd) = clmax - cld*cm_ac/cmd
    CL = (clmax_clean - cld * cm_ac / cmd) / (1 - cld * sm / cmd)
    return CL, (CL * sm - cm_ac) / cmd


def stall_speed(m, g, rho, S, CL):
    return math.sqrt(2 * m * g / (rho * S * CL))


# ------------------------------------------------------------------------------------ hover
def hover_authority(m, g, download, n_up_split, tmax_motor_N, y_m, z_m, z_cg, kq, cant_deg, I, dist):
    """Hover control power per axis with total thrust held at hover.
    n_up_split = upper/lower thrust ratio needed for pitch trim. tmax_motor_N already includes sag.
    I = (Ixx, Iyy, Izz) about the CG in cruise axes. dist = (M_pitch, M_roll, M_yaw) disturbance N m.
    Differential dT per motor is limited by the least-loaded motor (>= 0 thrust) and the most-loaded (<= Tmax)."""
    W = m * g * download
    Tm = W / 4
    Tl = 2 * Tm / (1 + n_up_split)                  # lower pair, per motor
    Tu = n_up_split * Tl                            # upper pair
    dT = min(Tl, tmax_motor_N - Tu)                 # usable symmetric differential per motor
    au, al = z_m - z_cg, z_m + z_cg                 # arms of upper / lower pair to the CG
    r = math.hypot(y_m, z_m)
    M = {"pitch": 2 * dT * (au + al),
         "roll": 4 * dT * y_m,
         "yaw": 4 * dT * (kq + r * math.sin(math.radians(cant_deg)))}
    Iax = {"pitch": I[1], "roll": I[2], "yaw": I[0]}
    D = dict(zip(("pitch", "roll", "yaw"), dist))
    out = {"T_hover_N": Tm, "T_upper_N": Tu, "T_lower_N": Tl, "dT_N": dT,
           "trim_use_pitch": (Tu - Tm) / dT}
    for k in M:
        out[f"M_{k}_Nm"] = M[k]
        out[f"acc_{k}_rads2"] = M[k] / Iax[k]
        out[f"ratio_{k}"] = M[k] / D[k] if D[k] > 0 else float("inf")
    return out


def hover_disturbance(rho, V, S, c, x_cg, cn90, xcp_frac, fin_area, fin_x, asym, b):
    """5 m/s wind on the hovering tailsitter. Pitch: wind on the wing face, normal force at xcp_frac*c.
    Roll (hover): wind on the fin faces at the fin centroid. Yaw (hover): spanwise asymmetry asym of the wing
    normal force acting at b/4."""
    q = 0.5 * rho * V * V
    Fw = q * S * cn90
    Ff = q * fin_area * cn90
    return {"q_Pa": q, "F_wing_N": Fw,
            "M_pitch": Fw * abs(xcp_frac * c - x_cg),
            "M_roll": Ff * abs(fin_x - x_cg),
            "M_yaw": asym * Fw * b / 4}


def slipstream_gap(D, z_m, t_half, ef, c, defl_deg):
    """Distance between the inner edge of the fully contracted slipstream (radius D/2/sqrt 2) of a prop centred
    at |z| = z_m and the outermost point of a fully deflected elevon. > 0: the elevon is outside the wash."""
    r_wake = D / 2 / math.sqrt(2)
    reach = t_half + ef * c * math.sin(math.radians(defl_deg))
    return (z_m - r_wake) - reach


# ------------------------------------------------------------------------------------ transition (quasi-steady)
def wing_coeffs(alpha, cla, a0, clmax, cd0, k_ind, cn90):
    """Lift/drag/normal coefficients 0..90 deg. Attached: linear lift capped at CLmax; post-stall: flat plate
    CN = cn90 sin(alpha). The larger normal force of the two (attached branch decays past stall) is used, a
    standard low-order blend (Viterna-type)."""
    cl_att = cla * (alpha - a0)
    a_s = a0 + clmax / cla
    if alpha <= a_s:
        cl = cl_att
        cd = cd0 + k_ind * cl * cl
        cn = cl * math.cos(alpha) + cd * math.sin(alpha)
        post = False
    else:
        cn_fp = cn90 * math.sin(alpha)
        cl_stall = clmax
        cn_st = cl_stall * math.cos(alpha) + (cd0 + k_ind * clmax ** 2) * math.sin(alpha)
        cn = max(cn_fp, cn_st * math.cos(alpha - a_s))
        cl = cn * math.cos(alpha)
        cd = cn * math.sin(alpha) + cd0
        post = True
    return cl, cd, cn, post, a_s


def transition_point(V, m, g, rho, S, c, x_cg, x_np, cm_ac, cla, a0, clmax, cd0, k_ind, cn90,
                     n, D, x_prop, cn_alpha_disk, tmax_motor_N, z_m, z_cg, download, cmd_eff=0.0, d_pitch=0.0,
                     f_post=0.25):
    """Level, unaccelerated flight at speed V with the body pitched alpha (= theta). Unknowns alpha, T:
    T cos(a) = D, T sin(a) + L = W. Pitch moment from the wing (CP from x_np in attached flow, moving to
    0.5 c at 90 deg post-stall) and the props' normal force; the motors' differential thrust must cancel it.
    Elevons first: up to d_pitch deg at cmd_eff (per deg, about the CG), effectiveness falling linearly from 1 at
    the stall angle to f_post at 90 deg. The motors carry the rest. Returns the equilibrium and the fraction of
    the available pitch differential used."""
    W = m * g
    q = 0.5 * rho * V * V
    if V < 0.05:
        alpha = math.pi / 2
        T = W * download
        M_aero = 0.0
        cl = cd = cn = 0.0
    else:
        lo, hi = math.radians(0.0), math.radians(90.0)

        def resid(a):
            cl_, cd_, _, _, _ = wing_coeffs(a, cla, a0, clmax, cd0, k_ind, cn90)
            L, Dg = q * S * cl_, q * S * cd_
            T_ = Dg / max(math.cos(a), 1e-6)
            return T_ * math.sin(a) + L - W

        # pick the lowest alpha that satisfies the equations (the branch the autopilot flies)
        grid = [math.radians(x / 4) for x in range(0, 361)]
        alpha = None
        for a1, a2 in zip(grid, grid[1:]):
            if resid(a1) <= 0 <= resid(a2) or resid(a1) >= 0 >= resid(a2):
                for _ in range(60):
                    am = 0.5 * (a1 + a2)
                    if (resid(a1) <= 0) == (resid(am) <= 0):
                        a1 = am
                    else:
                        a2 = am
                alpha = 0.5 * (a1 + a2)
                break
        if alpha is None:
            alpha = math.pi / 2
        cl, cd, cn, post, a_s = wing_coeffs(alpha, cla, a0, clmax, cd0, k_ind, cn90)
        T = q * S * cd / max(math.cos(alpha), 1e-6)
        T = max(T, 0.0)
        # wing pitching moment about the CG (nose-up +)
        if not post:
            Cm = cm_ac - cl * (x_np - x_cg) / c
        else:
            xcp = 0.25 + 0.25 * (alpha - a_s) / (math.pi / 2 - a_s)
            Cm = -cn * (xcp * c - x_cg) / c
        M_wing = q * S * c * Cm
        # props: in-plane normal force ~ crossflow; linear Ribner term, saturating with sin
        Np = n * cn_alpha_disk * (math.pi * D * D / 4) * q * math.sin(alpha) * math.cos(alpha)
        M_prop = Np * (x_cg - x_prop)          # props ahead: nose-up
        M_aero = M_wing + M_prop
        f = 1.0 if alpha <= a_s else 1.0 - (1.0 - f_post) * (alpha - a_s) / (math.pi / 2 - a_s)
        M_elev = abs(cmd_eff) * d_pitch * f * q * S * c
    if V < 0.05:
        M_elev = 0.0
    M_mot = max(0.0, abs(M_aero) - M_elev)
    Tm = T / 4 if T > 0 else 0.0
    dT = min(Tm, tmax_motor_N - Tm)
    M_avail = 2 * dT * (2 * z_m)              # upper vs lower pair, arm about the CG ~ 2 z_m total per pair
    return {"V": V, "alpha_deg": math.degrees(alpha), "T_N": T, "TW": T / W, "M_aero_Nm": M_aero,
            "M_avail_Nm": M_avail, "M_elev_Nm": M_elev, "M_motor_Nm": M_mot,
            "use": M_mot / M_avail if M_avail > 0 else (0.0 if M_mot == 0 else float("inf")),
            "cl": cl, "cd": cd}
