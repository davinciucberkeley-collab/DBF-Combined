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
def hover_authority(m, g, download, n_up_split, tmax_motor_N, y_m, z_m, z_cg, kq, cant_deg, I, dist, dfrac=1.0):
    """Hover control power per axis with total thrust held at hover.
    n_up_split = upper/lower thrust ratio needed for pitch trim. tmax_motor_N already includes sag.
    I = (Ixx, Iyy, Izz) about the CG in cruise axes. dist = (M_pitch, M_roll, M_yaw) disturbance N m.
    Differential dT per motor is limited by dfrac x hover thrust, the least-loaded motor (>= 0 thrust) and the
    most-loaded (<= Tmax)."""
    W = m * g * download
    Tm = W / 4
    Tl = 2 * Tm / (1 + n_up_split)                  # lower pair, per motor
    Tu = n_up_split * Tl                            # upper pair
    dT = min(dfrac * Tm, Tl, tmax_motor_N - Tu)     # usable symmetric differential per motor (dfrac: cap as a
                                                    # fraction of hover thrust, R-HOVER-AUTHORITY uses 0.30)
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
                     f_post=0.25, m_hub=0.0, np_scale=1.0, np_min=0.0):
    """Level, unaccelerated flight at speed V with the body pitched alpha (= theta). Unknowns alpha, T:
    T cos(a) = D, T sin(a) + L = W. Pitch moment from the wing (CP from x_np in attached flow, moving to
    0.5 c at 90 deg post-stall) and the props' normal force; the motors' differential thrust must cancel it.
    Elevons first: up to d_pitch deg at cmd_eff (per deg, about the CG), effectiveness falling linearly from 1 at
    the stall angle to f_post at 90 deg. The motors carry the rest. Returns the equilibrium and the fraction of
    the available pitch differential used.
    Prop normal force (design round 2026-11-14, D-149): Np = max(np_scale x Ribner, np_min), signed: it acts at the
    hubs, ahead of the CG, nose-up (the same sense as the Ribner term). np_scale = B4 BEMT dH/di over the Ribner slope
    (smaller nose-up term, conservative against the nose-down wing moment); np_min = n x B4's H-force (N, total).
    m_hub (old unsigned bound, adds to |M_aero|) is kept for back-compatibility and defaults to 0."""
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
        Np = max(np_scale * Np, np_min)
        M_prop = Np * (x_cg - x_prop)          # props ahead: nose-up
        M_aero = M_wing + M_prop
        f = 1.0 if alpha <= a_s else 1.0 - (1.0 - f_post) * (alpha - a_s) / (math.pi / 2 - a_s)
        M_elev = abs(cmd_eff) * d_pitch * f * q * S * c
    if V < 0.05:
        M_elev = 0.0
        M_prop = 0.0
    M_mot = max(0.0, abs(M_aero) + m_hub - M_elev)   # m_hub >= 0: prop hub (H-force) moment, no sign credit
    Tm = T / 4 if T > 0 else 0.0
    dT = min(Tm, tmax_motor_N - Tm)
    M_avail = 2 * dT * (2 * z_m)              # upper vs lower pair, arm about the CG ~ 2 z_m total per pair
    return {"V": V, "alpha_deg": math.degrees(alpha), "T_N": T, "TW": T / W, "M_aero_Nm": M_aero,
            "M_avail_Nm": M_avail, "M_elev_Nm": M_elev, "M_motor_Nm": M_mot,
            "use": M_mot / M_avail if M_avail > 0 else (0.0 if M_mot == 0 else float("inf")),
            "cl": cl, "cd": cd, "M_prop_Nm": M_prop}


# ------------------------------------------------------------------------------------ transition (time domain)
def pitchover_td(p, x_cg, T0_W=None, rate=12.0, ang_done=70.0, v_assist=14.0, wn=6.0, zeta=1.0, kprop=1.0,
                 alt_hold=False, dt=0.002, t_end=14.0, gust_w=3.0, record=0.05, fw_thr=0.70 / 0.49, keep_hist=False,
                 w0=0.0):
    """Longitudinal pitch-over that follows ArduPilot's tailsitter forward transition (ArduPlane/tailsitter.cpp,
    tag Plane-4.7.2, state ANGLE_WAIT_FW): nav pitch ramped at Q_TAILSIT_RAT_FW (rate, deg/s); throttle held at
    MAX(hover throttle, throttle_in at entry) = T0 (frozen); VTOL control until the tilt exceeds Q_TAILSIT_ANGLE
    (ang_done); then the plane controller flies the level attitude and the motors still stabilise below
    Q_ASSIST_SPEED (v_assist). Moved here from team/B3/round1114.py (design round 2026-11-14, D-149).

    2-D rigid body; theta = thrust axis above the horizon (90 = hover). Attitude follows the ramp through a 2nd-order
    loop (wn, zeta: EST). Thrust = T0 (1 - V_axial / Vp), Vp fitted to B4's fixed-rpm thrust at 45 deg inflow. The
    motor pitch moment needed = Iyy theta_dd - M_aero (inverse dynamics); pitch damping omitted (conservative).
    Wing and prop moments as transition_point; prop normal force kprop x Ribner, nose-up (props ahead of the CG).
    w0: vertical speed (m/s, up +) at the mode change; 0 = from a steady hover (closure round 2026-11-14).
    p: dict with m g rho S c b e a0(rad) CLa clmax cd0 cn90 n D x_prop cna cm_ac xnp dl tmax(N, sagged) z dfrac Iyy
    Vp Cmd_ref CLd xref eta lo li va slop fpost. Returns the summary (and the history if keep_hist)."""
    m, g, rho, S, c = p["m"], p["g"], p["rho"], p["S"], p["c"]
    W = m * g
    a0, CLa, clmax = p["a0"], p["CLa"], p["clmax"]
    k_ind = 1 / (math.pi * p["e"] * p["b"] ** 2 / S)
    A_disk = math.pi * p["D"] ** 2 / 4
    a_s = a0 + clmax / CLa
    Th = W * p["dl"] / 4
    M30 = 2 * (p["dfrac"] * Th) * (2 * p["z"])
    Iyy = p["Iyy"]

    def aero_moment(V, alpha):
        if V < 0.05:
            return 0.0, 0.0, 0.0
        q = 0.5 * rho * V * V
        al = max(min(alpha, math.pi / 2), -10 * math.pi / 180)
        cl, cd, cn, post, a_s_ = wing_coeffs(al, CLa, a0, clmax, p["cd0"], k_ind, p["cn90"])
        if not post:
            Cm = p["cm_ac"] - cl * (p["xnp"] - x_cg) / c
        else:
            xcp = 0.25 + 0.25 * (al - a_s_) / (math.pi / 2 - a_s_)
            Cm = -cn * (xcp * c - x_cg) / c
        Np = kprop * p["n"] * p["cna"] * A_disk * q * math.sin(al) * math.cos(al)
        return q * S * c * Cm + Np * (x_cg - p["x_prop"]), cl, cd

    def elevon_moment(V, alpha, defl, fpost_flat=None):
        cmd = (p["Cmd_ref"] + p["CLd"] * (x_cg - p["xref"]) / c) * p["eta"] * (
            1 - max(p["lo"], p["li"]) * (V / p["va"]) ** 2)
        if alpha <= a_s:
            f = 1.0
        elif fpost_flat is not None:
            f = fpost_flat
        else:
            f = 1.0 - (1.0 - p["fpost"]) * (alpha - a_s) / (math.pi / 2 - a_s)
        return abs(cmd) * max(defl - p["slop"], 0.0) * f * 0.5 * rho * V * V * S * c

    T_hover = W * p["dl"]
    T0 = max(T_hover, (T0_W or 0) * W)
    T0 = min(T0, 4 * p["tmax"] - 4 * 0.30 * Th)          # leave the 30 % differential headroom
    u = h = 0.0
    wv = w0                                               # vertical speed at entry (closure round: pre-climb)
    th, thd, tt = math.pi / 2, 0.0, 0.0
    phase, t_done, v_switch = "pitchover", None, None
    hist, peak = [], {"use": 0.0}
    nrec = max(1, int(round(record / dt)))
    k = 0
    while tt < t_end:
        V = math.hypot(u, wv)
        gam = math.atan2(wv, u) if V > 0.05 else 0.0
        al = th - gam
        Ma, cl, cd = aero_moment(V, al)
        qS = 0.5 * rho * V * V * S
        L, D = qS * cl, qS * cd
        lapse = max(0.0, 1 - max(0.0, V * math.cos(al)) / p["Vp"])
        if alt_hold:
            lz = L * math.cos(gam) - D * math.sin(gam)
            T = min(max(0.0, (m * (g - 1.0 * h - 2.0 * wv) - lz) / max(math.sin(th), 0.05)), T0 * 2)
        else:
            T = T0 * lapse
        if phase == "fw":
            T = max(T0, fw_thr * T_hover) * lapse
        ax = (T * math.cos(th) - L * math.sin(gam) - D * math.cos(gam)) / m
        az = (T * math.sin(th) + L * math.cos(gam) - D * math.sin(gam)) / m - g
        if phase == "pitchover":
            th_cmd = (90.0 - rate * tt) * math.pi / 180
            if (math.pi / 2 - th) > ang_done * math.pi / 180:
                phase, t_done, v_switch = "fw", tt, V
        if phase == "fw":
            cl_need = max(0.0, (W - T * math.sin(th)) / max(qS, 1e-6))
            a_need = min(cl_need / CLa + a0, a_s - 2 * math.pi / 180)
            th_cmd = max(a_need + gam, 0.0)
        thdd = wn * wn * (th_cmd - th) - 2 * zeta * wn * thd
        M_need = Iyy * thdd - Ma
        if V > 1.0:
            da = math.atan(gust_w / V)
            Mg = max(abs(aero_moment(V, al + da)[0] - Ma), abs(aero_moment(V, al - da)[0] - Ma))
        else:
            Mg = 0.0
        motors_on_pitch = phase == "pitchover" or V < v_assist
        el_cons = elevon_moment(V, al, 15.0, fpost_flat=p["fpost"])
        if phase == "fw":
            el_fw = elevon_moment(V, al, 15.0) if al <= a_s else 0.0
            M_mot = max(0.0, abs(M_need) - el_fw)
        else:
            M_mot = abs(M_need)
        use = M_mot / M30 if motors_on_pitch else 0.0
        rec = {"t": round(tt, 3), "V": round(V, 2), "theta_deg": round(math.degrees(th), 1),
               "alpha_deg": round(math.degrees(al), 1), "gamma_deg": round(math.degrees(gam), 1), "h": round(h, 2),
               "T_W": round(T / W, 3), "M_aero": round(Ma, 3), "M_dyn": round(Iyy * thdd, 4),
               "M_need": round(M_need, 3), "use30": round(use, 3),
               "use30_gust": round((M_mot + Mg) / M30, 3) if motors_on_pitch else 0.0,
               "use30_elev_cons": round(max(0.0, abs(M_need) - el_cons) / M30, 3) if motors_on_pitch else 0.0,
               "M_gust": round(Mg, 3), "phase": phase}
        if use > peak["use"]:
            peak = dict(rec, use=use)
        if k % nrec == 0:
            hist.append(rec)
        k += 1
        u += ax * dt
        wv += az * dt
        h += wv * dt
        thd += thdd * dt
        th += thd * dt
        tt += dt
        if phase == "fw" and V >= 17.0:
            break
    trim = [r for r in hist if r["phase"] == "pitchover" or r["V"] < v_assist]
    nwin = max(1, int(round(0.5 / record)))
    sus = max((min(r["use30"] for r in trim[i:i + nwin]) for i in range(max(1, len(trim) - nwin + 1))), default=0.0)
    po = [r for r in hist if r["phase"] == "pitchover"]
    fa = [r for r in hist if r["phase"] == "fw" and r["V"] < v_assist]
    pk = max(po, key=lambda r: r["use30"]) if po else None
    lower = (pk["T_W"] * W / 4 - pk["use30"] * M30 / (4 * p["z"])) if pk else None
    sus_po = max((min(r["use30"] for r in po[i:i + nwin]) for i in range(max(1, len(po) - nwin + 1))), default=0.0)
    out = {"peak": peak, "t_done_s": t_done, "sustained_0p5s_use30": round(sus, 3),
           "peak_pitchover": max((r["use30"] for r in po), default=0.0), "sustained_pitchover": round(sus_po, 3),
           "pitchover_peak_state": pk, "lower_motor_N_at_peak": lower,
           "max_trim_only_pitchover": max((abs(r["M_aero"]) / M30 for r in po), default=0.0),
           "peak_fw_assist": max((r["use30"] for r in fa), default=0.0),
           "t_fw_assist_above_0p60_s": round(sum(record for r in fa if r["use30"] > 0.60), 2),
           "t_stalled_fw_s": round(sum(record for r in fa if math.radians(r["alpha_deg"]) > a_s), 2),
           "V_done": next((r["V"] for r in hist if r["phase"] == "fw"), v_switch),   # final re-run: V at the switch if the 17 m/s break comes first
           "t_above_0p60_s": round(sum(record for r in hist if r["use30"] > 0.60), 2),
           "t_above_0p80_s": round(sum(record for r in hist if r["use30"] > 0.80), 2),
           "peak_use30_gust": max((r["use30_gust"] for r in trim), default=0.0),
           "peak_use30_elev_cons": max((r["use30_elev_cons"] for r in trim), default=0.0),
           "alt_change_m": round(hist[-1]["h"], 1) if hist else 0.0,
           "V_end": hist[-1]["V"] if hist else 0.0, "t_end": hist[-1]["t"] if hist else 0.0,
           "m_cap30_Nm": M30, "T0_N": T0}
    if keep_hist:
        out["hist"] = hist
    return out
