"""C5 simulation round: 3-D rigid-body touchdown on the four crushable fin-tip feet (K09-L), as designed.

Run:  python -I redesign/team/C5/sim/landing_sim3d.py        (about 30 min, single thread)
C5-R6 (2026-11-10): sink from requirements.landing_sink_ms (1.2 m/s, D-65); a lightest-mass case (A3 basic with the
D-64 546 g pack) and a mu 0.5 envelope at the gate mass are added.
Writes sim/out/sim3d.json; landing_sim_claims.py carries the results into the proof chain.

What it adds over landing_calc.py CALC-C5-DROP-DYN (planar, 2 contacts, frictionless, pitch and roll separately):
  * 6 degrees of freedom, full A3-R6a inertia, CG offsets in x, y and z (A3 roll-up as designed);
  * four feet, each a piston (mass m_f) on an elastic-plastic crusher (D5-R4 as delivered: plateau upper / lower,
    elastic ramp to the plateau over eps_y L/2, rigid stop at the 38 mm rim), with the pad as four corner contacts
    (neoprene k_p each, edges at the D5 pad outline) so a tilted foot lands and pivots on its edge;
  * Coulomb friction (mu 0.7, regularised) at every corner: horizontal drift, sliding and the foot side load;
  * combined pitch + roll touchdown errors, drift in any direction, steady wind or a lull, rotor lift lam W held to
    0.3 s then ramped to 0 at 0.6 s (C1 convention: vertical, through the CG; no attitude control = conservative).
Outputs per case: stroke per foot, peak load factor at the CG, peak transverse (side) load per foot, wingtip TE
corner height, largest tilt, tipped or not.

Frames: body = aircraft frame (x aft, y right, z up in cruise; params.json#frame). World: Z up, ground Z = 0. In the
upright stance body x points down (-Z), body y = world Y, body z = world X. "Narrow" axis tilt = rotation about world
Y (moves the +/-z pad lines; +theta lowers the +z (pod-side) pads). "Wide" axis = rotation about world X.
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RED = HERE.parents[2]
G0 = 9.80665


# ------------------------------------------------------------------ inputs (node values from the proof chain)
def _nodes():
    out = {}
    for f in RED.glob("team/*/claims*.json"):
        try:
            for n in json.loads(f.read_text("utf-8")).get("nodes", []):
                out[n["id"]] = n
        except (ValueError, KeyError):
            pass
    return out


def _param(p, key):
    v = p
    for k in key.split("."):
        v = v[k]
    return v["value"] if isinstance(v, dict) and "value" in v else v


def _cg_y():
    """Lateral CG (m) of A3's as-designed item list (rows: id, subsystem, discipline, mass_g, x, y, z)."""
    items = json.loads((RED / "team" / "A3" / "rollup" / "mass_items.json").read_text("utf-8"))
    rows = items["a3"]["rollup"]["items"]
    rows = rows["value"] if isinstance(rows, dict) else rows
    m = sum(r[3] for r in rows)
    return sum(r[3] * r[5] for r in rows) / m


def inputs():
    N = _nodes()
    P = json.loads((RED / "params" / "params.json").read_text("utf-8"))
    L = json.loads((RED / "subsystems" / "landing" / "params.json").read_text("utf-8"))
    v = lambda i: N[i]["value"]                                                   # noqa: E731
    geo = N["CALC-D5-GEOM"]["outputs"]
    d5m = N["CALC-D5-MASS"]["outputs"] if "CALC-D5-MASS" in N else {}
    m_piston = 0.0
    for k in ("piston_g", "pad_g"):
        m_piston += d5m.get(k, 0.0) / 1000.0
    if m_piston == 0.0:
        m_piston = (3.14 + 0.80) / 1000.0                                        # parts.csv GER-002 + GER-004
    m_piston += 0.5 * 0.63 / 1000.0                                               # half a cartridge moves with it
    return {
        "m_a3": v("CL-A3-MASS-BASIC"), "m_pred": v("CL-A3-MASS-PREDICTED"), "m_gate": _param(P, "requirements.mtow_gate_kg"),
        "m_light": v("CL-A3-MASS-BASIC") - (_param(P, "battery.mass_kg") - min(v("ASM-A1-PACK-CASES-G")) / 1000.0),
        "I_a3": [v("CL-A3-IXX"), v("CL-A3-IYY"), v("CL-A3-IZZ")],
        "x_cg": geo["x_ground_m"] - v("CL-C5-CG-H-R1"), "z_cg": v("CL-C5-CG-Z-R1"), "y_cg": _cg_y(),
        "x_g": geo["x_ground_m"], "y_fin": _param(P, "fins.y_m"), "z_pad_out": _param(L, "landing.pad.z_outer_m"),
        "edge_r": _param(L, "landing.pad.edge_r_m"), "pad_y": geo["pad_y_m"], "pad_z": geo["pad_z_m"],
        "F_up": v("CL-D5-F-PLATEAU-UPPER"), "F_lo": v("CL-D5-F-PLATEAU-LOWER"), "pk": v("ASM-C5-PRECRUSH-PEAK"),
        "s_av": v("CL-D5-STROKE-AVAIL"), "guard": v("ASM-C5-DROP-GUARD"), "L_cart": v("CL-D5-CART-LEN"),
        "eps_y": v("ASM-D5-YIELD-STRAIN"), "lam": v("ASM-C1-LAND-LIFT"), "mu": v("ASM-D5-PAD-MU"),
        "v_sink": _param(P, "requirements.landing_sink_ms"), "v_normal": 0.5, "err": _param(P, "requirements.landing_attitude_err_deg"),
        "v_td": v("ASM-C5-TD-DRIFT"), "rho": _param(P, "env.rho_kgm3"), "cd90": v("ASM-B1-CD90"),
        "span": _param(P, "wing.span_m"), "chord": _param(P, "wing.chord_m"), "foot": _param(P, "cg.foot_height_m"),
        "fin_c": _param(P, "fins.chord_m"), "fin_hh": _param(P, "fins.half_height_m"),
        "v_card": _param(P, "requirements.wind_limit_ms"), "v_gust": _param(P, "requirements.gust_survive_ms"),
        "m_piston": m_piston, "side_claim": v("CL-C5-FOOT-SIDE-LOAD"), "n_max": _param(P, "requirements.landing_n_design"),
        "planar": {k: N["CALC-C5-DROP-DYN"]["outputs"][k] for k in
                   ("cur_level_design_m", "cur_pair_design_m", "cur_pitch_design_m", "cur_roll_design_m",
                    "cur_level_free_n", "cur_n_tilted")},
        "hand_free_m": N["CALC-C5-DROP"]["outputs"]["stroke_free_m"],
        "static_v_land_broadside": N["CALC-C5-WIND"]["outputs"]["v_land_broadside_ms"],
        "static_v_land_spanwise": N["CALC-C5-WIND"]["outputs"]["v_land_spanwise_ms"],
        "static_beta_narrow": N["CALC-C5-WIND"]["outputs"]["beta_narrow_deg"],
    }


# ------------------------------------------------------------------ model
K_PAD = 1.0e5        # N/m per pad corner (1.6 mm 40A neoprene, 385 mm2 pad: E A / t ~ 3.6e5 N/m over 4 corners)
ZETA_PAD = 0.3       # damping ratio of a corner contact against the piston mass
EPS_V = 0.01         # m/s, friction regularisation (Coulomb above ~3 eps)
K_STOP = 5.0e5       # N/m, flange on the sleeve rim after the full stroke


def quat_mul(a, b):
    w1, x1, y1, z1 = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    w2, x2, y2, z2 = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    return np.stack([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2], -1)


def quat_to_R(q):
    w, x, y, z = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    return np.stack([np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], -1),
                     np.stack([2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)], -1),
                     np.stack([2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], -1)], -2)


def axis_quat(axis, ang):
    axis = np.asarray(axis, float)
    return np.concatenate([[math.cos(ang / 2)], math.sin(ang / 2) * axis / np.linalg.norm(axis)])


Q0 = None


def upright_quat():
    """Body -> world for the upright stance: x_b -> -Z, y_b -> Y, z_b -> X."""
    R = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], float)      # columns = images of body axes
    w = math.sqrt(1 + R[0, 0] + R[1, 1] + R[2, 2]) / 2
    return np.array([w, (R[2, 1] - R[1, 2]) / (4 * w), (R[0, 2] - R[2, 0]) / (4 * w), (R[1, 0] - R[0, 1]) / (4 * w)])


def geometry(inp, m, I_scale=1.0):
    """Body-frame points relative to the CG. Feet order UR, UL, LR, LL (U = +z pod side, R = +y)."""
    cg_b = np.array([inp["x_cg"], inp["y_cg"], inp["z_cg"]])  # body CG position (x from the root LE)
    z_o = inp["z_pad_out"] - inp["edge_r"]                     # pivot edge (D5 contact z)
    z_i = inp["z_pad_out"] - inp["pad_z"] + inp["edge_r"]
    dy = inp["pad_y"] / 2 - inp["edge_r"]
    feet, corners = [], []
    for sz in (1, -1):
        for sy in (1, -1):
            yc = sy * inp["y_fin"]
            feet.append([inp["x_g"], yc, sz * 0.5 * (z_o + z_i)])
            corners.append([[inp["x_g"], yc + a * dy, sz * zz] for a in (1, -1) for zz in (z_o, z_i)])
    feet = np.array(feet) - cg_b
    corners = np.array(corners) - cg_b
    tips = np.array([[inp["chord"], s * inp["span"] / 2, 0.0] for s in (1, -1)]) - cg_b
    F = np.array([inp["F_up"], inp["F_up"], inp["F_lo"], inp["F_lo"]])
    I = np.array(inp["I_a3"]) * I_scale
    return {"m": m, "I": I, "feet": feet, "corners": corners, "tips": tips, "F": F, "cg_b": cg_b}


def simulate(inp, cases, dt=4e-5, t_end=0.3, k_pad=K_PAD, m_f=None, eps_v=EPS_V, record=None):
    """Vectorised over cases. Each case: dict(m, I_scale, theta, phi, v_sink, drift=(vx, vy), lam, wind=(Fx, Fy),
    mu). Returns per-case results."""
    n = len(cases)
    m_f = inp["m_piston"] if m_f is None else m_f
    geos = [geometry(inp, c["m"], c.get("I_scale", 1.0)) for c in cases]
    m = np.array([g["m"] for g in geos])
    I = np.array([g["I"] for g in geos])
    feet = geos[0]["feet"]
    corners = geos[0]["corners"]                     # (4 feet, 4 corners, 3)
    tips = geos[0]["tips"]
    Fp = np.array([g["F"] for g in geos])            # (n, 4)
    s_y = inp["eps_y"] * inp["L_cart"] / 2
    k_c = Fp * inp["pk"] / s_y                        # elastic ramp to the (pre-crushed) peak = plateau
    s_av = inp["s_av"]
    mu = np.array([c.get("mu", inp["mu"]) for c in cases])
    lam = np.array([c["lam"] for c in cases])
    wind = np.array([list(c.get("wind", (0.0, 0.0))) + [0.0] for c in cases])
    q0 = upright_quat()
    q = np.zeros((n, 4))
    for i, c in enumerate(cases):
        qt = quat_mul(axis_quat([0, 1, 0], math.radians(c["theta"])), axis_quat([1, 0, 0], math.radians(c["phi"])))
        q[i] = quat_mul(qt, q0)
    R = quat_to_R(q)
    a_b = np.array([1.0, 0, 0])                         # foot axis, body (toward the ground)
    lowest = np.einsum("nij,fkj->nfki", R, corners)[..., 2].min(axis=(1, 2))
    r = np.zeros((n, 3))
    r[:, 2] = -lowest + 1e-9
    v = np.array([[c.get("drift", (0, 0))[0], c.get("drift", (0, 0))[1], -c["v_sink"]] for c in cases])
    w = np.zeros((n, 3))                              # body rates
    s = np.zeros((n, 4))
    sd = np.zeros((n, 4))
    sp = np.zeros((n, 4))                             # plastic part of the crush
    c_pad = 2 * ZETA_PAD * math.sqrt(k_pad * m_f)
    out = {"s_max": np.zeros((n, 4)), "n_peak": np.zeros(n), "side_peak": np.zeros((n, 4)),
           "tip_min": np.full(n, np.inf), "tilt_max": np.zeros(n), "slide_max": np.zeros(n),
           "side_1ms": np.zeros((n, 4))}
    side_f = np.zeros((n, 4))
    r0 = r.copy()
    t = 0.0
    steps = int(round(t_end / dt))
    for k in range(steps):
        R = quat_to_R(q)
        lam_t = lam * (1.0 if t < 0.3 else max(0.0, 1.0 - (t - 0.3) / 0.3))
        u = -np.einsum("nij,j->ni", R, a_b)                         # unit, foot axis up (world), same for all feet
        rho = corners[None] - s[:, :, None, None] * a_b              # (n,4,4,3) body, pistons pushed in
        rw = np.einsum("nij,nfkj->nfki", R, rho)
        P = r[:, None, None, :] + rw
        w_w = np.einsum("nij,nj->ni", R, w)
        vel = v[:, None, None, :] + np.cross(w_w[:, None, None, :], rw) + sd[:, :, None, None] * u[:, None, None, :]
        pen = -P[..., 2]
        touch = pen > 0
        Nn = np.where(touch, np.maximum(0.0, k_pad * pen - c_pad * vel[..., 2]), 0.0)
        vt = vel[..., :2]
        sp_t = np.sqrt((vt ** 2).sum(-1) + eps_v ** 2)
        T = -(mu[:, None, None] * Nn / sp_t)[..., None] * vt
        G = np.concatenate([T, Nn[..., None]], -1)                 # (n,4,4,3) ground force on each corner
        Gf = G.sum(2)                                               # per foot
        f_ax = np.einsum("nfj,nj->nf", Gf, u)
        # crusher: elastic-plastic, plateau F_p, rigid stop after s_av
        Fe = k_c * (s - sp)
        yld = Fe > Fp
        sp = np.where(yld, s - Fp / k_c, sp)
        Fc = np.clip(k_c * (s - sp), 0.0, None) + np.where(s > s_av, K_STOP * (s - s_av), 0.0)
        # piston (relative motion along the axis)
        sdd = (f_ax - Fc) / m_f
        sd = sd + sdd * dt
        s = s + sd * dt
        neg = s < 0
        s = np.where(neg, 0.0, s)
        sd = np.where(neg & (sd < 0), 0.0, sd)
        # forces on the airframe: crusher along the axis + the transverse part of the ground force
        lat = Gf - f_ax[..., None] * u[:, None, :]
        Fb = Fc[..., None] * u[:, None, :] + lat
        fw = np.einsum("nij,fj->nfi", R, feet)
        Fz = np.zeros((n, 3))
        Fz[:, 2] = -(1.0 - lam_t) * m * G0
        F = Fb.sum(1) + Fz + wind
        M_w = np.cross(fw, Fb).sum(1)
        if np.any(wind):
            arm = np.einsum("nij,j->ni", R, np.array([inp["chord"] / 2, 0, 0]) - geos[0]["cg_b"])
            M_w += np.cross(arm, wind)
        M_b = np.einsum("nji,nj->ni", R, M_w)
        acc = F / m[:, None]
        wdot = (M_b - np.cross(w, I * w)) / I
        v = v + acc * dt
        r = r + v * dt
        w = w + wdot * dt
        dq = np.concatenate([np.zeros((n, 1)), w], 1)
        q = q + 0.5 * quat_mul(q, dq) * dt
        q /= np.linalg.norm(q, axis=1)[:, None]
        t += dt
        # records
        out["s_max"] = np.maximum(out["s_max"], s)
        out["n_peak"] = np.maximum(out["n_peak"], (Fb.sum(1)[:, 2]) / (m * G0))
        sl = np.linalg.norm(lat, axis=-1)
        out["side_peak"] = np.maximum(out["side_peak"], sl)
        side_f += (sl - side_f) * min(1.0, dt / 1e-3)          # 1 ms first-order filter: the sustained side load
        out["side_1ms"] = np.maximum(out["side_1ms"], side_f)
        tz = (r[:, None, :] + np.einsum("nij,tj->nti", R, tips))[..., 2].min(1)
        out["tip_min"] = np.minimum(out["tip_min"], tz)
        tilt = np.degrees(np.arccos(np.clip(u[:, 2], -1, 1)))
        out["tilt_max"] = np.maximum(out["tilt_max"], tilt)
        out["slide_max"] = np.maximum(out["slide_max"], np.linalg.norm((r - r0)[:, :2], axis=1))
        if record is not None and k % record["every"] == 0:
            record.setdefault("t", []).append(t)
            record.setdefault("s", []).append(s[record["case"]].tolist())
            record.setdefault("n", []).append(float(Fb.sum(1)[record["case"], 2] / (m[record["case"]] * G0)))
            record.setdefault("tilt", []).append(float(tilt[record["case"]]))
            record.setdefault("side", []).append(np.linalg.norm(lat, axis=-1)[record["case"]].tolist())
    R = quat_to_R(q)
    u = -np.einsum("nij,j->ni", R, a_b)
    out["tilt_end"] = np.degrees(np.arccos(np.clip(u[:, 2], -1, 1)))
    out["tipped"] = out["tilt_end"] > 50.0                  # past every static tip angle (32-45 deg)
    return {k: v_.tolist() for k, v_ in out.items()}


# ------------------------------------------------------------------ case sets
def lean_deg(inp, V, area, m):
    return math.degrees(math.atan(0.5 * inp["rho"] * V * V * area * inp["cd90"] / (m * G0)))


def disc_cases(inp, m, I_scale, lam, v, mags=(0.0, 2.5, 5.0, 7.5, 10.0), n_az=24):
    """Touchdown attitude errors inside the requirement: tilt magnitude <= err in any azimuth (theta = narrow,
    phi = wide component)."""
    out = []
    for a in mags:
        for k in range(1 if a == 0 else n_az):
            az = 2 * math.pi * k / n_az
            out.append(dict(m=m, I_scale=I_scale, theta=a * math.cos(az), phi=a * math.sin(az), v_sink=v, lam=lam))
    return out


def summarise(cases, res):
    s = np.array(res["s_max"])
    smax = s.max(1)
    i = int(np.argmax(smax))
    sd = np.array(res["side_1ms"]).max(1)
    j = int(np.argmax(sd))
    return {"n_cases": len(cases), "worst_case": cases[i], "stroke_max_m": float(smax[i]),
            "stroke_by_foot_m": s[i].tolist(), "n_peak_max": float(np.max(res["n_peak"])),
            "side_peak_max_N": float(np.max(res["side_peak"])), "side_1ms_max_N": float(sd[j]),
            "side_worst_case": cases[j], "tip_min_m": float(np.min(res["tip_min"])),
            "tilt_max_deg": float(np.max(res["tilt_max"])), "tipped": int(np.sum(res["tipped"]))}


def main():
    t0 = time.time()
    inp = inputs()
    k_I = lambda m: m / inp["m_a3"]                                                   # noqa: E731
    out = {"inputs": inp, "model": {"K_PAD": K_PAD, "ZETA_PAD": ZETA_PAD, "EPS_V": EPS_V, "K_STOP": K_STOP,
                                    "dt": 4e-5}}
    masses = {"A3 basic": inp["m_a3"], "A3 predicted": inp["m_pred"], "gate": inp["m_gate"],
              "lightest": inp["m_light"]}          # C5-R6: A3 basic with the D-64 546 g pack (lightest flying mass)
    e = inp["err"]

    # 1. hard landing envelope: sink requirements.landing_sink_ms (1.2 m/s since D-65), lift lam W, tilt <= err in
    #    any direction, four masses in one batch
    cs, tags = [], []
    for tag, m in masses.items():
        c = disc_cases(inp, m, k_I(m), inp["lam"], inp["v_sink"])
        cs += c
        tags += [tag] * len(c)
    res = simulate(inp, cs)
    env = {}
    for tag in masses:
        idx = [i for i, t_ in enumerate(tags) if t_ == tag]
        sub = {k: [res[k][i] for i in idx] for k in res}
        cc = [cs[i] for i in idx]
        env[tag] = dict(summarise(cc, sub),
                        rows=[[c["theta"], c["phi"], max(sm), n_, max(sd), tm] for c, sm, n_, sd, tm in
                              zip(cc, sub["s_max"], sub["n_peak"], sub["side_1ms"], sub["tip_min"])])
        strike = [math.hypot(r_[0], r_[1]) for r_ in env[tag]["rows"] if r_[5] < 0]
        env[tag]["strike_tilt_min_deg"] = min(strike) if strike else None
        print("hard %-13s stroke %.4f m  n %.2f  side %.1f/%.1f N  tip %.4f m  strike from %s deg  (%.0f s)" % (
            tag, env[tag]["stroke_max_m"], env[tag]["n_peak_max"], env[tag]["side_1ms_max_N"],
            env[tag]["side_peak_max_N"], env[tag]["tip_min_m"], env[tag]["strike_tilt_min_deg"], time.time() - t0),
            flush=True)
    out["hard_envelope"] = env
    # 1b. pad friction option (CR-C5-16): the same envelope at the gate mass with a pad face of mu 0.5 on the mat
    c_mu = [dict(c, mu=0.5) for c in disc_cases(inp, inp["m_gate"], k_I(inp["m_gate"]), inp["lam"], inp["v_sink"])]
    r_mu = simulate(inp, c_mu)
    out["hard_envelope_mu05_gate"] = dict(summarise(c_mu, r_mu), rows=[
        [c["theta"], c["phi"], max(sm), n_, max(sd), tm] for c, sm, n_, sd, tm in
        zip(c_mu, r_mu["s_max"], r_mu["n_peak"], r_mu["side_1ms"], r_mu["tip_min"])])
    print("hard gate mu 0.5   stroke %.4f m  side %.1f N" % (out["hard_envelope_mu05_gate"]["stroke_max_m"],
                                                          out["hard_envelope_mu05_gate"]["side_1ms_max_N"]), flush=True)
    # level references and the beyond-requirement square corners (pitch and roll both at err)
    mg = inp["m_gate"]
    ref_cases = [dict(m=mg, I_scale=k_I(mg), theta=0, phi=0, v_sink=inp["v_sink"], lam=inp["lam"]),
                 dict(m=mg, I_scale=k_I(mg), theta=0, phi=0, v_sink=inp["v_sink"], lam=0.0)] + \
                [dict(m=mg, I_scale=k_I(mg), theta=a * e, phi=b * e, v_sink=inp["v_sink"], lam=inp["lam"])
                 for a in (1, -1) for b in (1, -1)]
    ref = simulate(inp, ref_cases)
    out["level_gate"] = {"design_stroke_m": max(ref["s_max"][0]), "free_stroke_m": max(ref["s_max"][1]),
                         "design_n": ref["n_peak"][0], "free_n": ref["n_peak"][1],
                         "design_by_foot_m": ref["s_max"][0], "free_by_foot_m": ref["s_max"][1],
                         "side_level_1ms_N": max(ref["side_1ms"][0])}
    out["square_corners_gate"] = [{"theta": c["theta"], "phi": c["phi"], "stroke_m": max(s_), "n": n_,
                                   "side_1ms_N": max(sd), "side_peak_N": max(sp), "tip_min_m": tm}
                                  for c, s_, n_, sd, sp, tm in zip(ref_cases[2:], ref["s_max"][2:], ref["n_peak"][2:],
                                                                   ref["side_1ms"][2:], ref["side_peak"][2:],
                                                                   ref["tip_min"][2:])]
    print("level gate", out["level_gate"], flush=True)

    # 2. drift: 0.3 m/s in 8 directions at 8 boundary attitudes (|tilt| = err), sink 1.5 and 0.5 m/s, A3 predicted
    mp = inp["m_pred"]
    atts = [(e * math.cos(k * math.pi / 4), e * math.sin(k * math.pi / 4)) for k in range(8)]
    dirs = [(math.cos(k * math.pi / 4), math.sin(k * math.pi / 4)) for k in range(8)]
    cs = [dict(m=mp, I_scale=k_I(mp), theta=a, phi=b, v_sink=vs, lam=inp["lam"],
               drift=(inp["v_td"] * dx, inp["v_td"] * dy)) for vs in (inp["v_sink"], inp["v_normal"])
          for (a, b) in atts for (dx, dy) in dirs]
    res = simulate(inp, cs, t_end=1.2)
    out["drift"] = dict(summarise(cs, res), tilt_end=res["tilt_end"])
    print("drift: stroke %.4f  side %.1f N  tipped %d  tilt_max %.1f  (%.0f s)" % (
        out["drift"]["stroke_max_m"], out["drift"]["side_1ms_max_N"], out["drift"]["tipped"],
        out["drift"]["tilt_max_deg"], time.time() - t0), flush=True)

    # 3. wind: touchdown tilted by the hover lean + err toward the narrow +z pad line (broadside) or a wide pad line
    #    (span into wind), drift v_td toward it; lull (wind gone at touchdown) and steady wind; sink 0.5 and 1.5 m/s
    m1 = inp["m_a3"]
    S_b = inp["span"] * inp["chord"]
    S_s = 2 * inp["fin_c"] * 2 * inp["fin_hh"]
    Vs = [0.5 * k for k in range(0, 25)]
    cs, keys = [], []
    for axis, S in (("broadside", S_b), ("spanwise", S_s)):
        for mode in ("lull", "steady"):
            for vs in (inp["v_normal"], inp["v_sink"]):
                for V in Vs:
                    tilt = lean_deg(inp, V, S, m1) + e
                    D = 0.5 * inp["rho"] * V * V * S * inp["cd90"] if mode == "steady" else 0.0
                    if axis == "broadside":       # lean toward +z (world +X); the wind pushes back toward -X
                        cs.append(dict(m=m1, I_scale=1.0, theta=tilt, phi=0.0, v_sink=vs, lam=inp["lam"],
                                       drift=(inp["v_td"], 0.0), wind=(-D, 0.0)))
                    else:                         # lean toward world -Y about world X (wide axis)
                        cs.append(dict(m=m1, I_scale=1.0, theta=0.0, phi=tilt, v_sink=vs, lam=inp["lam"],
                                       drift=(0.0, -inp["v_td"]), wind=(0.0, D)))
                    keys.append(("%s/%s/%.1f" % (axis, mode, vs), V, tilt))
    res = simulate(inp, cs, t_end=2.0)
    wind = {}
    for i, (key, V, tilt) in enumerate(keys):
        w_ = wind.setdefault(key, {"V": [], "tilt0_deg": [], "tipped": [], "tilt_max": [], "tilt_end": []})
        w_["V"].append(V)
        w_["tilt0_deg"].append(tilt)
        w_["tipped"].append(res["tipped"][i])
        w_["tilt_max"].append(res["tilt_max"][i])
        w_["tilt_end"].append(res["tilt_end"][i])
    for key, w_ in wind.items():
        first = next((j for j, tp in enumerate(w_["tipped"]) if tp), None)
        w_["v_limit_ms"] = w_["V"][-1] if first is None else (w_["V"][first - 1] if first > 0 else 0.0)
        w_["tilt_limit_deg"] = None if first is None else w_["tilt0_deg"][first]
        print("wind %-24s limit %.1f m/s, tips from a %s deg touchdown tilt" % (key, w_["v_limit_ms"],
                                                                              w_["tilt_limit_deg"]), flush=True)
    out["wind"] = wind
    print("(%.0f s)" % (time.time() - t0), flush=True)

    # 4. convergence: time-step ladder on the governing hard-landing case and on the tip-over threshold
    wc = env["gate"]["worst_case"]
    sc = env["gate"]["side_worst_case"]
    ladder = {}
    for dt in (8e-5, 4e-5, 2e-5, 1e-5, 5e-6):
        r1 = simulate(inp, [wc, sc], dt=dt)
        ladder[str(dt)] = {"stroke_m": max(r1["s_max"][0]), "n": r1["n_peak"][0],
                           "side_1ms_N": max(r1["side_1ms"][1]), "side_peak_N": max(r1["side_peak"][1])}
    out["dt_ladder"] = ladder
    kb = "broadside/lull/0.5"
    t_lim = wind[kb]["tilt_limit_deg"] or 30.0
    tl = {}
    for dt in (8e-5, 4e-5, 2e-5, 1e-5):
        cs = [dict(m=m1, I_scale=1.0, theta=t_lim - 2.0 + 0.25 * j, phi=0.0, v_sink=inp["v_normal"],
                   lam=inp["lam"], drift=(inp["v_td"], 0.0)) for j in range(13)]
        r1 = simulate(inp, cs, dt=dt, t_end=2.0)
        first = next((c["theta"] for c, tp in zip(cs, r1["tipped"]) if tp), None)
        tl[str(dt)] = {"tilts": [c["theta"] for c in cs], "tipped": r1["tipped"], "tip_threshold_deg": first}
    out["dt_ladder_tip"] = tl
    print("ladders done (%.0f s)" % (time.time() - t0), flush=True)
    # 5. sensitivity of the governing cases to the contact-model parameters
    sens = {}
    for name, kw in (("baseline", {}), ("k_pad x0.5", dict(k_pad=K_PAD / 2)), ("k_pad x2", dict(k_pad=K_PAD * 2)),
                     ("m_piston x2", dict(m_f=2 * inp["m_piston"])), ("eps_v x0.5", dict(eps_v=EPS_V / 2))):
        r1 = simulate(inp, [wc, sc], **kw)
        sens[name] = {"stroke_m": max(r1["s_max"][0]), "n": r1["n_peak"][0], "side_1ms_N": max(r1["side_1ms"][1]),
                      "side_peak_N": max(r1["side_peak"][1])}
    out["sensitivity"] = sens
    # 6. time histories for the plots
    for name, case in (("history_worst", wc), ("history_side", sc)):
        rec = {"case": 0, "every": 10}
        simulate(inp, [case], record=rec)
        out[name] = rec
    out["runtime_s"] = time.time() - t0
    (HERE / "out" / "sim3d.json").write_text(json.dumps(out, indent=1))
    print("wrote sim3d.json in %.0f s" % out["runtime_s"])


if __name__ == "__main__":
    main()
