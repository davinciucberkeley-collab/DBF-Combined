"""B3 hover rate loops with the first wing torsion modes (CR-C2-03, CHANGE-LOG D-45). Standard library only.

Linear single-axis models, rate output (gyro on the pod), input = differential thrust per motor dT (N).
Controller shape = F4's ArduPilot rate PID ratios (subsystems/flight-software/K09L.param), overall gain scaled
so the RIGID loop crosses over at f_c. Elements in the loop: PID (D through a 1st-order FLTD filter), 2nd-order
Pade transport delay, motor/prop first-order lag, structure, 2nd-order Butterworth gyro low-pass.

Pitch (hover, about cruise y): upper vs lower pairs. The differential torque 4 z dT acts on the two fin stations
(motors, mounts, fins; I_s each about the spar), which are tied to the rest of the airframe (I_b = Iyy - 2 I_s)
by the wing torsion spring; the gyro sits on the body. Two-inertia, free-free symmetric mode f_sym:
    q_b / M = (c s + K) / [s (I_b I_st s^2 + c (I_b + I_st) s + K (I_b + I_st))],  I_st = 2 I_s,
    K = w^2 I_b I_st / (I_b + I_st),  c = 2 zeta w I_b I_st / (I_b + I_st).
Yaw (hover, about cruise x, the thrust axis): diagonal pairs. The same dT pattern twists the two stations in
opposite senses (antisymmetric torsion f_anti, node at the centreline, so the pod gyro sees no twist), and the
twist tilts each station's thrust by theta, giving F_z = 2 T theta per station at +/-y: a yaw moment 4 T y theta.
    r / dT = [k_y + sigma 16 T y z / (I_st (s^2 + 2 zeta w s + w^2))] / (Ixx s)
sigma = +1 when the twist moment adds to the rigid control moment (F4 motor map: UR/LL CW seen from the nose,
cant aiding the reaction torque -> +1; derivation in S-AND-C.md); -1 is kept as the map-swap case.
Polynomials are lists of coefficients, highest power first.
"""
from __future__ import annotations

import cmath
import math


def pmul(*ps):
    out = [1.0]
    for p in ps:
        r = [0.0] * (len(out) + len(p) - 1)
        for i, a in enumerate(out):
            for j, b in enumerate(p):
                r[i + j] += a * b
        out = r
    return out


def padd(a, b):
    n = max(len(a), len(b))
    a = [0.0] * (n - len(a)) + list(a)
    b = [0.0] * (n - len(b)) + list(b)
    return [x + y for x, y in zip(a, b)]


def pscale(a, k):
    return [k * x for x in a]


def polyval(p, s):
    v = 0j
    for c in p:
        v = v * s + c
    return v


def roots(p, w0=100.0):
    """Durand-Kerner, after scaling s = w0 u so the coefficients are of similar size (leading zeros stripped)."""
    while abs(p[0]) == 0.0:
        p = p[1:]
    n = len(p) - 1
    q = [c * w0 ** (n - k) for k, c in enumerate(p)]
    a = [x / q[0] for x in q]
    rad = 1 + max(abs(x) for x in a[1:])
    r = [rad * cmath.exp(1j * (2 * math.pi * k / n + 0.4)) for k in range(n)]
    for _ in range(5000):
        new = []
        for i, ri in enumerate(r):
            den = 1
            for j, rj in enumerate(r):
                if j != i:
                    den *= (ri - rj)
            new.append(ri - polyval(a, ri) / den)
        done = max(abs(x - y) for x, y in zip(new, r)) < 1e-13 * rad
        r = new
        if done:
            break
    return [w0 * x for x in r]


def elements(tau_m, delay, f_gyro, kp, ki, kd, f_d):
    """Numerator/denominator of controller x motor x delay x gyro filter."""
    wd = 2 * math.pi * f_d
    # C = kp + ki/s + kd s wd/(s + wd) = [kp s (s+wd) + ki (s+wd) + kd wd s^2] / [s (s+wd)]
    c_num = padd(padd(pscale([1.0, wd, 0.0], kp), pscale([1.0, wd], ki)), [kd * wd, 0.0, 0.0])
    c_den = [1.0, wd, 0.0]
    T = delay
    d_num, d_den = [T * T / 12, -T / 2, 1.0], [T * T / 12, T / 2, 1.0]
    wg = 2 * math.pi * f_gyro
    return (pmul(c_num, d_num, [wg * wg]),
            pmul(c_den, [tau_m, 1.0], d_den, [1.0, math.sqrt(2) * wg, wg * wg]))


def plant_pitch(k_m, I_tot, I_st, f_mode, zeta, rigid=False):
    if rigid:
        return [k_m], [I_tot, 0.0]
    I_b = I_tot - I_st
    w = 2 * math.pi * f_mode
    mu = I_b * I_st / I_tot
    K, c = w * w * mu, 2 * zeta * w * mu
    return [k_m * c, k_m * K], [I_b * I_st, c * I_tot, K * I_tot, 0.0]


def plant_yaw(k_y, Ixx, I_st, f_mode, zeta, T, y, z, sigma, rigid=False):
    if rigid:
        return [k_y], [Ixx, 0.0]
    w = 2 * math.pi * f_mode
    md = [I_st, I_st * 2 * zeta * w, I_st * w * w]
    return padd(pscale(md, k_y), [sigma * 16 * T * y * z]), pmul([Ixx, 0.0], md)


def _grid(f_lo=0.05, f_hi=400.0, n=6000):
    a, b = math.log10(f_lo), math.log10(f_hi)
    return [10 ** (a + (b - a) * i / (n - 1)) for i in range(n)]


GRID = _grid()


def resp(num, den, f):
    s = 2j * math.pi * f
    return polyval(num, s) / polyval(den, s)


def margins(num, den, closed_loop=True):
    """GM (dB, minimum over every -180 deg crossing), PM (deg, minimum over every 0 dB crossing), closed-loop
    stability from the roots of den + num."""
    mag, ph, prev = [], [], None
    for f in GRID:
        L = resp(num, den, f)
        p = cmath.phase(L)
        if prev is not None:
            while p - prev > math.pi:
                p -= 2 * math.pi
            while p - prev < -math.pi:
                p += 2 * math.pi
        prev = p
        mag.append(abs(L))
        ph.append(p)
    gm, f_gm, pm, f_c = math.inf, None, math.inf, None
    for i in range(len(GRID) - 1):
        k0 = math.floor((ph[i] + math.pi) / (2 * math.pi))
        k1 = math.floor((ph[i + 1] + math.pi) / (2 * math.pi))
        if k0 != k1:
            g = -20 * math.log10(0.5 * (mag[i] + mag[i + 1]))
            if g < gm:
                gm, f_gm = g, GRID[i]
        if (mag[i] >= 1.0) != (mag[i + 1] >= 1.0):
            pmg = math.degrees((ph[i] + math.pi) % (2 * math.pi))
            if pmg < pm:
                pm, f_c = pmg, GRID[i]
    out = {"gm_db": gm, "f_gm_hz": f_gm, "pm_deg": pm, "f_c_hz": f_c}
    if closed_loop:
        cl = roots(padd(den, num))
        out["cl_max_real"] = max(z.real for z in cl)
        out["stable"] = out["cl_max_real"] < 0
    return out


def mode_peak_db(num, den, f_mode, band=0.25, n=401):
    fs = [f_mode * (1 - band + 2 * band * i / (n - 1)) for i in range(n)] if band > 0 else [f_mode]
    return max(20 * math.log10(abs(resp(num, den, f))) for f in fs)


def loop(axis, f_c, f_mode, zeta, ctrl, filt, phys, sigma=1.0, rigid_margins=True):
    """Open loop for one axis. ctrl = (kp, ki, kd) shape (scaled), filt = (tau_m, delay, f_gyro, f_d),
    phys = dict(k, I, I_st[, T, y, z]). Returns rigid and flexible margins and the mode-band peak of |L|."""
    kp, ki, kd = ctrl
    tau_m, delay, f_g, f_d = filt
    e_num, e_den = elements(tau_m, delay, f_g, kp, ki, kd, f_d)
    if axis == "pitch":
        r_num, r_den = plant_pitch(phys["k"], phys["I"], phys["I_st"], f_mode, zeta, rigid=True)
        x_num, x_den = plant_pitch(phys["k"], phys["I"], phys["I_st"], f_mode, zeta)
    else:
        args = (phys["k"], phys["I"], phys["I_st"], f_mode, zeta, phys["T"], phys["y"], phys["z"], sigma)
        r_num, r_den = plant_yaw(*args, rigid=True)
        x_num, x_den = plant_yaw(*args)
    rn, rd = pmul(e_num, r_num), pmul(e_den, r_den)
    g = 1.0 / abs(resp(rn, rd, f_c))
    rn = pscale(rn, g)
    xn, xd = pscale(pmul(e_num, x_num), g), pmul(e_den, x_den)
    return {"gain": g, "rigid": margins(rn, rd, closed_loop=False) if rigid_margins else None,
            "flex": margins(xn, xd), "mode_peak_db": mode_peak_db(xn, xd, f_mode)}
