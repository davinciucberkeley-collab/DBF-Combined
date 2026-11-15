"""F4 follow-up 2: does the attitude / rate loop couple with the cage flex modes (9-11 Hz, STRUCTURES iteration 2)?
Takes the iteration-2 FE (qp/A/structures fe_a.py + iter2_eval.py CFG, free-free, kd / nom / hi corners), builds the modal transfer function
 motor-pair torque (N m) -> body rate at the IMU node (rigid modes + flexible modes, damping zeta), closes the A.param rate loop around it
(P, I, D, D filter, gyro LPF, motor lag, delay) and reports closed-loop stability, gain margin, peak sensitivity, with and without a notch.
python -I fu_cage.py   (numpy, scipy; about 1 min).  All EST: FE inputs are STRUCTURES EST, zeta 1 % is a guess, T_full / lag / delay are plant EST.
Axes: copter pitch = about y (spar), lever arm Z_M, input = x-force pairs on the motors at +-z; copter roll = about z (belly), arm Y_M."""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "structures")); sys.path.insert(0, HERE)
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import fe_a
from iter2_eval import FIN
import a_aero as AE

CFG = dict(spar_tube=(12e-3, 10e-3), arm_tube=(12e-3, 10e-3), rib_tube=(14e-3, 12e-3), bridge_cfg="single+V", bridge_tube=(12e-3, 10e-3),
           vtube=(6e-3, 4.5e-3), bridge_yv=0.30, fin_strip=None, fin_tube=(16e-3, 14e-3, 3e-3, 0.055), x_fin=0.294, foot_pad_m=0.0025)
YM, ZM = fe_a.Y_M, fe_a.Z_M
RATE = dict(pit=dict(P=0.25, I=0.25, D=0.004, arm=ZM, dof=4), rll=dict(P=0.25, I=0.25, D=0.004, arm=YM, dof=5),
            yaw=dict(P=0.40, I=0.04, D=0.0, arm=math.hypot(YM, ZM) * math.sin(math.radians(16.0)) + 0.0204, dof=3, flte=2.5))   # A.param section 3
FLTD = 32.0; GYRO_LPF = 40.0; TAU_M = 0.04; DELAY = 0.004     # Q_A_RAT_*_FLTD, INS_GYRO_FILTER, plant TAU_M (EST), DShot + loop delay (EST)
rpm, T, Q, I = AE.motor(0.90 * 16.0, 0.0); TFULL = T * AE.DER * AE.DOWNLOAD   # per-motor full-scale thrust (0.90 cap, 16 V bus, x0.93 x0.97), N


CANT_TAN = True


def modal(F, node, dof_out, torque_split):
    idx = F._idx; V = F._V; K = F._K
    lam = np.einsum("ij,ij->j", V, K @ V)                 # V^T K V (V is M-orthonormal from eigh)
    mot = [m for m in idx if (m.startswith("m+") or m.startswith("m-")) and ">" not in m]
    b = np.zeros(V.shape[0])
    for m in mot:
        sy = 1 if m[1] == "+" else -1; sz = 1 if m[3] == "+" else -1
        q = torque_split(sy, sz)                                           # x-force on this motor (N per N m of demanded torque)
        b[6 * idx[m]] += q
        if CANT_TAN:                                                       # 16 deg cant: the tangential (swirl) component acts in y, z (derivation in the report)
            rho = math.hypot(YM, ZM); tc = math.tan(math.radians(16.0))
            b[6 * idx[m] + 1] += -q * tc * sy * ZM / rho; b[6 * idx[m] + 2] += q * tc * sz * YM / rho
            b[6 * idx[m] + 3] += sy * sz * 0.0204 * q                      # shaft reaction torque about x (KQ 0.0204 m, plant)
    gin = V.T @ b; gout = V[6 * idx[node] + dof_out, :]
    return np.sqrt(np.maximum(lam, 0.0)) / (2 * math.pi), gin * gout


def ss_series(s1, s2):
    """series connection, y = s2(s1(u)); each = (A, B, C, D)"""
    A1, B1, C1, D1 = s1; A2, B2, C2, D2 = s2; n1, n2 = A1.shape[0], A2.shape[0]
    A = np.block([[A1, np.zeros((n1, n2))], [B2 @ C1, A2]]); B = np.vstack([B1, B2 @ D1]); C = np.hstack([D2 @ C1, C2]); D = D2 @ D1
    return A, B, C, D


def ss_par(s1, s2):
    A1, B1, C1, D1 = s1; A2, B2, C2, D2 = s2; n1, n2 = A1.shape[0], A2.shape[0]
    return (np.block([[A1, np.zeros((n1, n2))], [np.zeros((n2, n1)), A2]]), np.vstack([B1, B2]), np.hstack([C1, C2]), D1 + D2)


def tfss(num, den):
    from scipy.signal import tf2ss
    A, B, C, D = tf2ss(np.atleast_1d(num), np.atleast_1d(den)); return A, B, C, D


def plant(modes, zeta):
    """theta_dot / M: parallel modal sum (rigid f < 1 Hz is g / s since theta_dot = s theta, theta = g / s^2)"""
    sysm = None
    for f, g in modes:
        w = 2 * math.pi * f
        blk = tfss([g], [1.0, 0.0]) if f < 1.0 else tfss([g, 0.0], [1.0, 2 * zeta * w, w * w])
        sysm = blk if sysm is None else ss_par(sysm, blk)
    return sysm


def loop(modes, ax, zeta=0.01, notch=None, tfull_scale=1.0, kscale=1.0, gyro_lpf=GYRO_LPF, fltd=FLTD, P=None, D=None, notch2=None):
    r = RATE[ax]; kt = 2 * TFULL * tfull_scale * r["arm"] * kscale      # N m per unit controller output (mixer factors +-0.5, four motors)
    A, B, C, Dm = plant(modes, zeta); sysl = (A, B * kt, C, Dm)
    p = r["P"] if P is None else P; d_ = r["D"] if D is None else D
    wd = 2 * math.pi * fltd
    # PID with first-order D filter: P + I/s + D s wd/(s + wd)
    cn = np.polyadd(np.polyadd(p * np.polymul([1, 0], [1 / wd, 1]), r["I"] * np.array([1 / wd, 1])), d_ * np.polymul([1, 0], [1, 0]))
    ctrl = tfss(cn, np.polymul([1, 0], [1 / wd, 1]))
    wg = 2 * math.pi * gyro_lpf
    chain = [ctrl, tfss([wg * wg], [1, math.sqrt(2) * wg, wg * wg]), tfss([1.0], [TAU_M, 1.0]), tfss([-DELAY / 2, 1.0], [DELAY / 2, 1.0])]
    for nt in (notch, notch2):
        if nt:
            fn, q, depth = nt; wn = 2 * math.pi * fn                      # notch: (s^2 + depth (wn/q) s + wn^2) / (s^2 + (wn/q) s + wn^2)
            chain.append(tfss([1, depth * wn / q, wn * wn], [1, wn / q, wn * wn]))
    sysL = sysl
    if r.get("flte"): chain.insert(0, tfss([1.0], [1 / (2 * math.pi * r["flte"]), 1.0]))     # yaw error filter (ArduPilot default Q_A_RAT_YAW_FLTE 2.5 Hz)
    for blk in chain: sysL = ss_series(sysL, blk)
    return sysL


def maxre(sysL, k=1.0):
    A, B, C, D = sysL
    return float(np.max(np.linalg.eigvals(A - k * (B @ C)).real))


def freq(sysL, w):
    A, B, C, D = sysL; n = A.shape[0]
    return np.array([(C @ np.linalg.solve(1j * x * np.eye(n) - A, B))[0, 0] + D[0, 0] for x in w])


def margins(sysL):
    up = float("inf"); lo = 0.0
    for k in np.geomspace(1.0, 100, 300):
        if maxre(sysL, k) >= -1e-9: up = float(k); break
    for k in np.geomspace(1.0, 0.01, 300):
        if maxre(sysL, k) >= -1e-9: lo = float(k); break
    w = 2 * math.pi * np.geomspace(0.3, 200, 3000); L = freq(sysL, w); Ms = float(np.max(1 / np.abs(1 + L)))
    a = np.abs(L); cr = [float(w[i] / 2 / math.pi) for i in range(1, len(w)) if (a[i - 1] - 1) * (a[i] - 1) < 0]
    band = (w / 2 / math.pi > 3) & (w / 2 / math.pi < 30); pk = float(np.max(a[band]))
    return up, lo, Ms, cr, pk


def cases():
    res = []
    for k in ("kd", "nom", "hi"):
        F, info = fe_a.build(k, **CFG); F.solve(60)
        for ax in ("pit", "rll", "yaw"):
            r = RATE[ax]
            if ax == "pit": sg = lambda sy, sz, a=r["arm"]: sz / (4 * a)
            elif ax == "rll": sg = lambda sy, sz, a=r["arm"]: -sy / (4 * a)
            else: sg = lambda sy, sz, a=r["arm"]: sy * sz * math.cos(math.radians(16.0)) / (4 * a)     # unit yaw torque: th = -sy sz / (4 (rho sin c + KQ cos c)) per motor
            for node, nname in (("s+0.000", "spar centre"), ("hub", "cage hub")):
                f, g = modal(F, node, r["dof"], sg)
                rig = [(0.0, sum(gg for ff, gg in zip(f, g) if ff < 1.0))]       # the six rigid modes collapse to one gain 1 / I
                flex = [(ff, gg) for ff, gg in zip(f, g) if 1.0 <= ff < 250 and abs(gg) > 1e-9]
                res.append(dict(k=k, ax=ax, node=nname, modes=rig + flex, inv_I=sum(gg for ff, gg in rig), flex=flex))
    return res


if __name__ == "__main__":
    out = []

    def P(s=""): print(s); out.append(s)
    C = cases()
    P("Rigid inertia from the FE (1 / sum of rigid-mode gains), kg m2: " + ", ".join("%s %s %s %.4f" % (c["k"], c["ax"], c["node"], 1 / c["inv_I"]) for c in C if c["node"] == "cage hub"))
    P("TFULL per motor %.2f N" % TFULL)
    P("| axis | IMU at | corner | flex modes 3-30 Hz (Hz: gain / rigid gain) | zeta | thrust scale | notch | max Re(closed pole) | GM up / down | Ms | crossovers Hz | peak abs L in 3-30 Hz |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in C:
        shown = ", ".join("%.1f: %+.2f" % (ff, gg / c["inv_I"]) for ff, gg in c["flex"] if 3 < ff < 30)
        for zeta in (0.01, 0.003):
            for ts in (1.0, 0.77):
                L = loop(c["modes"], c["ax"], zeta, None, ts)
                up, lo, Ms, cr, pk = margins(L)
                P("| %s | %s | %s | %s | %.3f | %.2f | - | %.3g | %.2f / %.2f | %.2f | %s | %.2f |" % (c["ax"], c["node"], c["k"], shown, zeta, ts, maxre(L), up, lo, Ms, ", ".join("%.1f" % x for x in cr), pk))
        # rigid-only baseline
    for c in C:
        if c["node"] == "hub" and c["k"] == "nom":
            L = loop([m for m in c["modes"] if m[0] < 1.0], c["ax"], 0.01, None, 1.0)
            up, lo, Ms, cr, pk = margins(L)
            P("rigid-only %s: GM up %.2f down %.2f Ms %.2f crossover %s Hz" % (c["ax"], up, lo, Ms, ", ".join("%.1f" % x for x in cr)))
    open(os.path.join(HERE, "fu_cage.md"), "w").write("\n".join(out))


# ---------------------------------------------------------------------------------------------- design sweep (python -I fu_cage.py sweep)
def pm_first(sysL):
    w = 2 * math.pi * np.geomspace(0.3, 100, 2500); L = freq(sysL, w); a = np.abs(L)
    for i in range(1, len(w)):
        if (a[i - 1] - 1) * (a[i] - 1) < 0:
            ph = math.degrees(np.angle(L[i])); return w[i] / 2 / math.pi, 180.0 + ph if ph < 0 else ph - 180.0
    return float("nan"), float("nan")


def evaluate(C, **kw):
    """worst case over every case: (min GM up over zeta 0.003 / 0.01 and thrust scales 0.77 / 1.0, min PM of the rigid crossover, min crossover Hz, any unstable)"""
    gm = 99.0; pmn = 999.0; fc = 99.0; bad = 0; msw = 0.0
    for c in C:
        for zeta in (0.003, 0.01):
            for ts in (0.77, 1.0):
                L = loop(c["modes"], c["ax"], zeta, tfull_scale=ts, **kw)
                if maxre(L) >= -1e-6: bad += 1; gm = min(gm, 1.0); continue
                up = margins(L)[0]; gm = min(gm, up)
                if zeta == 0.01:
                    f, pm = pm_first(L); pmn = min(pmn, pm); fc = min(fc, f)
                    w = 2 * math.pi * np.geomspace(0.3, 100, 1500); msw = max(msw, float(np.max(1 / np.abs(1 + freq(L, w)))))
    return gm, pmn, fc, bad, msw


if len(sys.argv) > 1 and sys.argv[1] == "sweep":
    C = cases(); out = []
    def P(s=""): print(s); out.append(s)
    P("| gyro LPF Hz | FLTD Hz | P | D | notch | min GM up (zeta 0.003-0.01, thrust x0.77-1.0) | min rigid PM deg | min crossover Hz | unstable cases of %d | max Ms |" % (len(C) * 4))
    P("|---|---|---|---|---|---|---|---|---|---|")
    for glp, fd, pp, dd, nt in ((40, 32, 0.25, 0.004, None), (40, 32, 0.25, 0.002, None), (30, 20, 0.20, 0.002, None), (20, 20, 0.20, 0.002, None), (20, 20, 0.15, 0.002, None),
                                (20, 15, 0.15, 0.0015, None), (15, 15, 0.15, 0.0015, None), (20, 20, 0.20, 0.002, (13.5, 1.2, 0.1)), (20, 20, 0.15, 0.002, (13.5, 1.2, 0.1)),
                                (40, 32, 0.25, 0.004, (13.5, 1.2, 0.1)), (30, 32, 0.20, 0.003, (13.5, 1.2, 0.1))):
        gm, pm, fc, bad, ms = evaluate(C, gyro_lpf=glp, fltd=fd, P=pp, D=dd, notch=nt)
        P("| %d | %d | %.2f | %.4f | %s | %.2f | %.0f | %.1f | %d | %.1f |" % (glp, fd, pp, dd, nt if nt else "-", gm, pm, fc, bad, ms))
    open(os.path.join(HERE, "fu_cage_sweep.md"), "w").write("\n".join(out))


# ---------------------------------------------------------------------------------------------- baseline vs final (python -I fu_cage.py final)
if len(sys.argv) > 1 and sys.argv[1] == "final":
    C = cases(); out = []
    def P(s=""): print(s); out.append(s)
    SETS = {"A.param before (P .25 / D .004 / FLTD 32, gyro 40)": {a: dict(gyro_lpf=40, fltd=32) for a in ("pit", "rll", "yaw")},
            "A.param now (pit .15 / .002 / 40, roll .20 / .003 / 32, yaw as before, gyro 60)": {"pit": dict(gyro_lpf=60, fltd=40, P=0.15, D=0.002), "rll": dict(gyro_lpf=60, fltd=32, P=0.20, D=0.003), "yaw": dict(gyro_lpf=60, fltd=32)}}
    P("Worst case over kd / nom / hi corners, zeta 0.3 % and 1 %, thrust scale 0.77 / 1.0 / 1.25 (36 loops per row). GM = factor on the loop gain before the first closed-loop pole crosses into the right half plane (1.00 = already unstable somewhere);")
    P("PM and crossover at zeta 1 %, thrust x1.0, worst corner. `unstable` counts the loops (of 18 per axis and IMU position) with a right-half-plane pole.\n")
    P("| settings | axis | IMU at | min GM | unstable loops of 18 | rigid PM deg | crossover Hz |"); P("|---|---|---|---|---|---|---|")
    for name, kw in SETS.items():
        for ax in ("pit", "rll", "yaw"):
            for nd in ("spar centre", "cage hub"):
                cs = [c for c in C if c["ax"] == ax and c["node"] == nd]
                gm = 99.0; bad = 0; pmn = 999.0; fcn = 99.0
                for c in cs:
                    for z in (0.003, 0.01):
                        for ts in (0.77, 1.0, 1.25):
                            L = loop(c["modes"], ax, z, tfull_scale=ts, **kw[ax])
                            if maxre(L) >= -1e-6: bad += 1; gm = min(gm, 1.0); continue
                            gm = min(gm, margins(L)[0])
                            if z == 0.01 and ts == 1.0:
                                f, pm = pm_first(L); pmn = min(pmn, pm); fcn = min(fcn, f)
                P("| %s | %s | %s | %.2f | %d | %s | %s |" % (name, ax, nd, gm, bad, "-" if pmn > 900 else "%.0f" % pmn, "-" if fcn > 90 else "%.1f" % fcn))
    open(os.path.join(HERE, "fu_cage_final.md"), "w").write("\n".join(out))
