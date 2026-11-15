"""Concept A fin-tip landing: static tip-over + 3-D rigid-body touchdown on four crush feet.  python -I landing_a.py
Adapted (scaled, standalone) from team/C5/sim/landing_sim3d.py: 6 dof, full inertia from the A mass list, four feet at the fin
corners, elasto-plastic crush (elastic ramp to a plateau, rigid stop at the usable stroke), Coulomb friction mu, rotor lift lam*W
held 0.3 s then ramped to 0 at 0.6 s (C1 convention).  Not the K09-L cartridge: A's foot is a PETG shoe on an EVA/PE foam pad (EST).
Frames: body x aft (down in stance), y right, z cruise-up (world +X in stance).  World Z up."""
import math, sys
import numpy as np
G = 9.81
M_GATE = 1.50
MU = 0.40          # pad friction cap (K09-L D-105 pad_mu_max, carried)
CASES_HARD, CASES_NORM = 1.2, 0.5        # m/s sink: hard landing (K09-L landing_sink_ms 1.2) and normal touchdown (K09-L v_normal 0.5)
ATT_ERR = 10.0                           # deg attitude error at touchdown (K09-L landing_attitude_err_deg)
# mass list: (g, x aft of LE, y, z) ; scaled to M_GATE; from structures_a mass roll-up and MASS-GATE s2
ITEMS = [(213, 0.095, 0, 0), (125, 0.24, 0.38, 0), (4*81.06, -0.075, 0.228, 0.156), (64, -0.075, 0.114, 0.078), (46, -0.045, 0, 0),
         (20, 0.05, 0, 0), (270, -0.020, 0, 0), (110, 0.06, 0, 0), (30, 0.20, 0.30, 0), (40, 0.10, 0, 0)]


def mass_props(scale_to=M_GATE, items=ITEMS):
    pts = []
    for g, x, y, z in items:
        ys = (y, -y) if y else (0,); zs = (z, -z) if z else (0,)
        n = len(ys)*len(zs)
        for yy in ys:
            for zz in zs: pts.append((g/n, x, yy, zz))
    tot = sum(p[0] for p in pts); k = scale_to*1000/tot
    pts = [(g*k/1000, x, y, z) for g, x, y, z in pts]
    m = sum(p[0] for p in pts)
    cg = np.array([sum(p[0]*p[i] for p in pts)/m for i in (1, 2, 3)])
    I = np.zeros((3, 3))
    for g, x, y, z in pts:
        r = np.array([x, y, z])-cg
        I += g*((r@r)*np.eye(3)-np.outer(r, r))
    I[0, 0] += 0.0; return m, cg, I


R0 = np.array([[0, 0, 1.0], [0, 1, 0], [-1, 0, 0]])     # body->world in the upright stance


def rot(axis, a):
    axis = np.asarray(axis, float); n = np.linalg.norm(axis)
    if n < 1e-15: return np.eye(3)
    k = axis/n; K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3)+math.sin(a)*K+(1-math.cos(a))*K@K


def simulate(m=M_GATE, Fp=45.0, s_y=0.0015, s_max=0.020, v_sink=1.2, th_n=0.0, th_w=0.0, drift=0.0, drift_dir=0.0, lam=0.667,
             mu=MU, dt=1e-4, T=1.5, y_foot=0.38, z_foot=0.18, x_foot=0.30, zeta=0.05, k_stop=5e5, cgdx=0.0):
    mm, cg, I = mass_props(m)
    cg = cg+np.array([cgdx, 0, 0])
    Ib = I; Ibi = np.linalg.inv(Ib)
    feet = [np.array([x_foot, sy*y_foot, sz*z_foot])-cg for sy in (1, -1) for sz in (1, -1)]
    R = rot((0, 1, 0), math.radians(th_n))@rot((1, 0, 0), math.radians(th_w))@R0
    # start height: lowest foot touches
    zs = [(R@r)[2] for r in feet]; p = np.array([0, 0, -min(zs)+1e-4])
    v = np.array([drift*math.cos(drift_dir), drift*math.sin(drift_dir), -v_sink]); w = np.zeros(3)
    ke = Fp/s_y; sp = np.zeros(4); dmax = np.zeros(4); fside = np.zeros(4); nmax = 0.0; Fmax = np.zeros(4)
    c_d = 2*zeta*math.sqrt(ke*mm/4)
    W = mm*G; t = 0.0; nst = int(T/dt)
    for _ in range(nst):
        lw = lam if t < 0.3 else max(0.0, lam*(1-(t-0.3)/0.3))
        F = np.array([0, 0, -W+lw*W]); tau = np.zeros(3); wb = R.T@w
        for i, r in enumerate(feet):
            rw = R@r; P = p+rw
            d = -P[2]
            if d <= 0: continue
            vp = v+np.cross(w, rw)
            fe = ke*(d-sp[i])
            if fe > Fp: sp[i] = d-Fp/ke; fe = Fp
            if d > s_max: fe += k_stop*(d-s_max)
            fn = max(0.0, fe+(c_d*(-vp[2]) if -vp[2] > 0 else 0.0))
            if fn <= 0: continue
            vt = vp[:2]; sp_ = np.linalg.norm(vt)
            ft = -mu*fn*vt/max(sp_, 0.02)*min(1.0, sp_/0.02) if sp_ > 1e-9 else np.zeros(2)
            f = np.array([ft[0], ft[1], fn]); F += f; tau += np.cross(rw, f)
            dmax[i] = max(dmax[i], d); fside[i] = max(fside[i], np.linalg.norm(ft)); Fmax[i] = max(Fmax[i], fn)
        v = v+F/mm*dt
        tb = R.T@tau
        wb_dot = Ibi@(tb-np.cross(wb, Ib@wb))
        wb = wb+wb_dot*dt; w = R@wb
        R = rot(w, np.linalg.norm(w)*dt)@R if np.linalg.norm(w) > 1e-12 else R
        p = p+v*dt; t += dt
        nmax = max(nmax, (F[2]+W-lw*W)/W)
    tilt = math.degrees(math.acos(max(-1, min(1, -(R[:, 0])[2]))))     # body +x vs down; upright => body x = -Z => 0 deg
    return dict(dmax_mm=dmax*1e3, sp_mm=sp*1e3, F=Fmax, side=fside, n_peak=nmax, tilt_end=tilt, drift_end=np.linalg.norm(p[:2]),
                v_end=np.linalg.norm(v))


def static():
    m, cg, I = mass_props()
    h = 0.30-cg[0]
    out = dict(cg_x=cg[0], h=h, tip_narrow=math.degrees(math.atan2(0.18, h)), tip_wide=math.degrees(math.atan2(0.38, h)),
               I=np.diag(I))
    rho = 1.225; S = 0.22; W = m*G; half = 0.18; hcp = 0.30-0.5*0.245
    out["v_tip_parked"] = math.sqrt(W*half/(0.5*rho*S*2.0*hcp))
    f5 = 0.5*rho*25*S*2.0
    out["restore_ratio_5ms"] = W*half/(f5*hcp)
    return out


if __name__ == "__main__":
    print(static())
    sweep = sys.argv[1:] and [float(x) for x in sys.argv[1:]] or [45.0]
    for Fp in sweep:
        print(f"\n### plateau {Fp} N per foot, usable stroke 20 mm")
        cases = [("hard level", dict(v_sink=1.2)), ("hard 10 narrow", dict(v_sink=1.2, th_n=10)), ("hard 10 narrow neg", dict(v_sink=1.2, th_n=-10)),
                 ("hard 10 wide", dict(v_sink=1.2, th_w=10)), ("hard 7/7 combo", dict(v_sink=1.2, th_n=7, th_w=7)),
                 ("hard 10 narrow + drift .5", dict(v_sink=1.2, th_n=10, drift=0.5, drift_dir=0.0)),
                 ("hard 10 wide + drift .5 y", dict(v_sink=1.2, th_w=10, drift=0.5, drift_dir=math.pi/2)),
                 ("normal level .5", dict(v_sink=0.5)), ("normal 10 narrow .5", dict(v_sink=0.5, th_n=10)), ("normal 10 wide .5 + drift", dict(v_sink=0.5, th_w=10, drift=0.5, drift_dir=math.pi/2))]
        for name, kw in cases:
            r = simulate(Fp=Fp, **kw)
            print(f"{name:28s} stroke max {r['dmax_mm'].max():5.1f} mm  n {r['n_peak']:.2f}  Fmax {r['F'].max():5.1f} N  side {r['side'].max():5.1f} N  tilt_end {r['tilt_end']:5.1f}  drift {r['drift_end']*1e3:5.0f} mm  set {r['sp_mm'].max():.1f}")
