"""Concept A fin-tip landing: static tip-over + 3-D rigid-body touchdown on four crush feet.  python -I landing_a.py
Adapted (scaled, standalone) from team/C5/sim/landing_sim3d.py: 6 dof, full inertia from the A mass list, four feet at the fin
corners, elasto-plastic crush (elastic ramp to a plateau, rigid stop at the usable stroke), Coulomb friction mu, rotor lift lam*W
held 0.3 s then ramped to 0 at 0.6 s (C1 convention).  Not the K09-L cartridge: A's foot is a PETG shoe on an EVA/PE foam pad (EST).
Frames: body x aft (down in stance), y right, z cruise-up (world +X in stance).  World Z up."""
import math, sys, os, json
import numpy as np
G = 9.81
M_GATE = float(os.environ.get("LAND_MASS_KG", 1.50))   # T-074: env override for the F-5 re-runs at the predicted mass; default 1.50 kg unchanged
# rib-root check constants (CAD wing.py RIB_OD/RIB_ID/RIB_X0; factors and allowables as structures_a.py, EST)
RIB_OD, RIB_ID, RIB_X0 = float(os.environ.get('LAND_RIB_OD', 0.014)), float(os.environ.get('LAND_RIB_ID', 0.012)), 0.0705     # T-066: env override LAND_RIB_OD / LAND_RIB_ID (the CAD rib is 25x23 since T-077 p8 / D-226); defaults unchanged so the T-064 / AR-008 numbers reproduce
RIB_A = math.pi/4*(RIB_OD**2-RIB_ID**2); RIB_I = math.pi/64*(RIB_OD**4-RIB_ID**4); RIB_Z = RIB_I/(RIB_OD/2); RIB_J = 2*RIB_I
KF_RIB = 1.5*1.15; SIG_RIB = 350e6; TAU_RIB = 30e6
MU = 0.40          # pad friction cap (K09-L D-105 pad_mu_max, carried)
CASES_HARD, CASES_NORM = 1.2, 0.5        # m/s sink: hard landing (K09-L landing_sink_ms 1.2) and normal touchdown (K09-L v_normal 0.5)
ATT_ERR = 10.0                           # deg attitude error at touchdown (K09-L landing_attitude_err_deg)
# mass list: (g, x aft of LE, y, z) ; scaled to M_GATE; from structures_a mass roll-up and MASS-GATE s2
ITEMS = [(213, 0.095, 0, 0), (125, 0.24, 0.38, 0), (4*88.26, -0.075, 0.228, 0.156), (64, -0.075, 0.114, 0.078), (46, -0.045, 0, 0),
         (20, 0.05, 0, 0), (270, -0.020, 0, 0), (110, 0.06, 0, 0), (30, 0.20, 0.30, 0), (40, 0.10, 0, 0)]


# ---- ground / CG geometry (T-064r, F2): default = the CAD; GEOM_LEGACY=1 in the environment (or --legacy) restores the pre-T064r hand values
# (x_foot 0.30, z_foot 0.18, CG from ITEMS) so the AR-008 / AR-012 numbers of 2026-11-19 stay reproducible.
HERE = os.path.dirname(os.path.abspath(__file__))
LEGACY = bool(os.environ.get("GEOM_LEGACY")) or ("--legacy" in sys.argv)
if "--legacy" in sys.argv: sys.argv.remove("--legacy")
_CADG = None
def cad_geom():
    """CAD ground plane and CG.  x_ground, YFIN, FIN_H, pad box and rib tube from redesign/qp/A/cad/amodel (electrical.py X_GROUND, common.py YFIN/FIN_H,
    wing.py RIB_*); pad z span = FIN_H-0.009 .. FIN_H+0.003 (electrical.py build_landing 'foot pad' box, centre FIN_H-0.003); CG from
    redesign/qp/A/sitl/cad_mass.json (written 2026-11-18 by sitl/cad_mass.py from the CAD part table; regenerated 2026-11-19 gives CG x 21.366 mm,
    z 6.364 mm, i.e. identical to 0.01 mm; mass_basic 1.2733 kg = CAD declared masses, no growth)."""
    global _CADG
    if _CADG is None:
        cad = os.path.join(HERE, "..", "cad")
        if cad not in sys.path: sys.path.insert(0, cad)
        from amodel import electrical as E, wing as W, common as C
        cm = json.load(open(os.path.join(HERE, "..", "sitl", "cad_mass.json")))
        assert abs(cm["x_ground_m"]-E.X_GROUND) < 1e-9 and abs(cm["fin_y_m"]-C.YFIN) < 1e-9
        zlo, zhi = C.FIN_H-0.009, C.FIN_H+0.003
        _CADG = dict(x_foot=E.X_GROUND, y_foot=C.YFIN, z_foot=0.5*(zlo+zhi), z_edge=zhi, pad_x0=C.XFIN_T+0.0135, pad_dy=0.015, pad_dz=zhi-zlo,
                     cg=np.array([float(os.environ["LAND_CG_X_MM"])*1e-3 if "LAND_CG_X_MM" in os.environ else cm["cg_x_m"], cm["cg_y_m"], cm["cg_z_m"]]), mass_basic=cm["mass_basic_kg"], I_cad=cm["I_cad_axes_kgm2"],
                     rib=(W.RIB_OD, W.RIB_ID, W.RIB_X0), fin_h=C.FIN_H)
    return _CADG
LEG_GEOM = dict(x_foot=0.30, y_foot=0.38, z_foot=0.18, z_edge=0.18, cg=None)
def geom(): return LEG_GEOM if LEGACY else cad_geom()


MASS_MODEL = os.environ.get("LAND_MASS_MODEL", "items")      # T-076d (D-222 LR-3): "cad" = landing_mass_cad.py (CAD part table, vendor items unscaled, wing / fins distributed); default "items" = the roll-up above, unchanged


def mass_props(scale_to=M_GATE, items=ITEMS):
    if MASS_MODEL == "cad" and items is ITEMS:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import landing_mass_cad as _LM
        return _LM.mass_props(scale_to)
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
             mu=MU, dt=1e-4, T=1.5, y_foot=None, z_foot=None, x_foot=None, zeta=0.05, k_stop=5e5, cgdx=0.0, cg_override=None, trace=False, hist=None):
    g_ = geom(); y_foot = g_['y_foot'] if y_foot is None else y_foot; z_foot = g_['z_foot'] if z_foot is None else z_foot; x_foot = g_['x_foot'] if x_foot is None else x_foot
    mm, cg, I = mass_props(m)
    if cg_override is None and g_['cg'] is not None: cg_override = g_['cg']      # CAD CG (x, y, z); inertia stays the ITEMS roll-up about its own CG (same as AR-008)
    if cg_override is not None: cg = np.array(cg_override, float)
    cg = cg+np.array([cgdx, 0, 0])
    Ib = I; Ibi = np.linalg.inv(Ib)
    feet = [np.array([x_foot, sy*y_foot, sz*z_foot])-cg for sy in (1, -1) for sz in (1, -1)]
    R = rot((0, 1, 0), math.radians(th_n))@rot((1, 0, 0), math.radians(th_w))@R0
    # start height: lowest foot touches
    zs = [(R@r)[2] for r in feet]; p = np.array([0, 0, -min(zs)+1e-4])
    v = np.array([drift*math.cos(drift_dir), drift*math.sin(drift_dir), -v_sink]); w = np.zeros(3)
    ke = Fp/s_y; sp = np.zeros(4); dmax = np.zeros(4); fside = np.zeros(4); nmax = 0.0; Fmax = np.zeros(4); rib_idx = 0.0; tors_max = 0.0
    feet_b = [np.array([x_foot-RIB_X0, 0.0, sz*z_foot]) for sy in (1, -1) for sz in (1, -1)]      # foot arm from the rib root, body frame
    c_d = 2*zeta*math.sqrt(ke*mm/4)
    W = mm*G; t = 0.0; nst = int(T/dt); TRC = []
    for _ in range(nst):
        lw = lam if t < 0.3 else max(0.0, lam*(1-(t-0.3)/0.3))
        F = np.array([0, 0, -W+lw*W]); tau = np.zeros(3); wb = R.T@w
        Mrib = np.zeros((2, 3)); Nrib = np.zeros(2); FBs = np.zeros((4, 3))
        if hist is not None: dcur = np.zeros(4); fcur = np.zeros(4)      # T-105 LAND_TRACE: per-step record only; nothing below depends on it
        for i, r in enumerate(feet):
            rw = R@r; P = p+rw
            d = -P[2]
            if hist is not None: dcur[i] = max(0.0, d)
            if d <= 0: continue
            vp = v+np.cross(w, rw)
            fe = ke*(d-sp[i])
            if fe > Fp: sp[i] = d-Fp/ke; fe = Fp
            if d > s_max: fe += k_stop*(d-s_max)
            fn = max(0.0, fe+(c_d*(-vp[2]) if -vp[2] > 0 else 0.0))
            if hist is not None: fcur[i] = fn
            if fn <= 0: continue
            vt = vp[:2]; sp_ = np.linalg.norm(vt)
            ft = -mu*fn*vt/max(sp_, 0.02)*min(1.0, sp_/0.02) if sp_ > 1e-9 else np.zeros(2)
            f = np.array([ft[0], ft[1], fn]); F += f; tau += np.cross(rw, f)
            fb = R.T@f; FBs[i] = fb; Mrib[i//2] += np.cross(feet_b[i], fb); Nrib[i//2] += abs(fb[0])      # both feet of one rib add (feet 0,1 = +y rib; 2,3 = -y rib)
            dmax[i] = max(dmax[i], d); fside[i] = max(fside[i], np.linalg.norm(ft)); Fmax[i] = max(Fmax[i], fn)
        for k in range(2):
            Mb = Mrib[k]; sig = KF_RIB*(math.hypot(Mb[1], Mb[2])/RIB_Z+Nrib[k]/RIB_A); tq = KF_RIB*abs(Mb[0])*(RIB_OD/2)/RIB_J
            rib_idx = max(rib_idx, math.hypot(sig/SIG_RIB, tq/TAU_RIB)); tors_max = max(tors_max, abs(Mb[0]))
        if trace: TRC.append(FBs.ravel().copy())
        if hist is not None: hist.append((t, p.copy(), R.copy(), dcur.copy(), fcur.copy(), sp.copy(), (F[2]+W-lw*W)/W, lw))
        v = v+F/mm*dt
        tb = R.T@tau
        wb_dot = Ibi@(tb-np.cross(wb, Ib@wb))
        wb = wb+wb_dot*dt; w = R@wb
        R = rot(w, np.linalg.norm(w)*dt)@R if np.linalg.norm(w) > 1e-12 else R
        p = p+v*dt; t += dt
        nmax = max(nmax, (F[2]+W-lw*W)/W)
    tilt = math.degrees(math.acos(max(-1, min(1, -(R[:, 0])[2]))))     # body +x vs down; upright => body x = -Z => 0 deg
    return dict(dmax_mm=dmax*1e3, sp_mm=sp*1e3, F=Fmax, side=fside, n_peak=nmax, tilt_end=tilt, drift_end=np.linalg.norm(p[:2]), rib_rf=1.0/max(rib_idx, 1e-9), rib_T=tors_max,
                v_end=np.linalg.norm(v), trace=(np.array(TRC) if trace else None))


def _quat(R):
    """rotation matrix -> unit quaternion (w, x, y, z), body -> world (T-105 LAND_TRACE)."""
    t = R[0, 0]+R[1, 1]+R[2, 2]
    if t > 0:
        s = 0.5/math.sqrt(t+1.0); q = [0.25/s, (R[2, 1]-R[1, 2])*s, (R[0, 2]-R[2, 0])*s, (R[1, 0]-R[0, 1])*s]
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0*math.sqrt(1.0+R[0, 0]-R[1, 1]-R[2, 2]); q = [(R[2, 1]-R[1, 2])/s, 0.25*s, (R[0, 1]+R[1, 0])/s, (R[0, 2]+R[2, 0])/s]
    elif R[1, 1] > R[2, 2]:
        s = 2.0*math.sqrt(1.0+R[1, 1]-R[0, 0]-R[2, 2]); q = [(R[0, 2]-R[2, 0])/s, (R[0, 1]+R[1, 0])/s, 0.25*s, (R[1, 2]+R[2, 1])/s]
    else:
        s = 2.0*math.sqrt(1.0+R[2, 2]-R[0, 0]-R[1, 1]); q = [(R[1, 0]-R[0, 1])/s, (R[0, 2]+R[2, 0])/s, (R[1, 2]+R[2, 1])/s, 0.25*s]
    return q


def write_trace(path, name, Fp, kw, r, hist, dt=1e-4, rate_hz=200.0, extra=None):
    """T-105: write one case's time history (sampled at <= rate_hz) as JSON. Only called when LAND_TRACE is set; peaks are over the full-rate record."""
    step = max(1, int(round(1.0/(rate_hz*dt)))); idx = list(range(0, len(hist), step))
    if idx[-1] != len(hist)-1: idx.append(len(hist)-1)
    rd = lambda x, n=5: [round(float(v), n) for v in x]
    H = [hist[i] for i in idx]
    allf = np.array([h[4] for h in hist]); alld = np.array([h[3] for h in hist]); nn = np.array([h[6] for h in hist])
    out = dict(
        meta=dict(case=name, Fp_N=Fp, kwargs=kw, mass_kg=M_GATE, mass_model=MASS_MODEL, geom="legacy" if LEGACY else "CAD", dt_s=dt, rate_hz=1.0/(step*dt),
                  rib_od_m=RIB_OD, rib_id_m=RIB_ID, units="t s; p m; crush_mm mm; force_N N; load_factor g; tilt deg",
                  frame="world Z up (touchdown ground plane z=0); body x aft (down in stance), y right, z cruise-up (world +X in stance). R0 maps the upright stance to body->world.",
                  p="CG position in world axes [x, y, z]", quat_wxyz="unit quaternion, body -> world", tilt_deg="angle of body +x from world down; 0 = upright stance (as tilt_end)",
                  pads="order = landing_a feet: (sy,sz) = (+1,+1), (+1,-1), (-1,+1), (-1,-1); y = sy*y_foot (+y right wing fin), z_body = sz*z_foot",
                  crush_mm="penetration depth d of the pad (elastic + plastic); capped only by the stop spring beyond s_max", set_mm="permanent (plastic) set of each pad",
                  load_factor_g="sum of pad normal forces / (m g): same definition as n_peak (rotor lift excluded)", rotor_lift_frac="lam ramp: 0.667 until 0.3 s, to 0 at 0.6 s (C1 convention)",
                  limits=dict(stroke_mm=20.0, tilt_deg=3.0, load_factor_g=12.0)),
        peaks=dict(stroke_mm=float(r["dmax_mm"].max()), n_g=float(r["n_peak"]), tilt_end_deg=float(r["tilt_end"]), Fmax_N=float(r["F"].max()), side_N=float(r["side"].max()),
                   rib_rf=float(r["rib_rf"]), drift_end_mm=float(r["drift_end"]*1e3), set_mm_max=float(r["sp_mm"].max()),
                   stroke_mm_fullrate=float(alld.max()*1e3), Fmax_N_fullrate=float(allf.max()), n_g_fullrate=float(nn.max())),
        t=rd([h[0] for h in H], 4), p=[rd(h[1]) for h in H], quat_wxyz=[rd(_quat(h[2]), 6) for h in H],
        tilt_deg=[round(math.degrees(math.acos(max(-1, min(1, -h[2][2, 0])))), 3) for h in H],
        crush_mm=[rd(h[3]*1e3, 3) for h in H], force_N=[rd(h[4], 3) for h in H], set_mm=[rd(h[5]*1e3, 3) for h in H],
        load_factor_g=rd([h[6] for h in H], 4), rotor_lift_frac=rd([h[7] for h in H], 4))
    if extra: out["meta"].update(extra)
    with open(path, "w", encoding="utf-8") as f: json.dump(out, f, separators=(",", ":"))


def static():
    """Static tip-over.  CAD geometry: ground plane x 0.3375 (electrical.py X_GROUND), CG from cad_mass.json (x, y, z).  narrow axis = tip about a pad in body z
    (lean about body y); wide axis = tip about the fin in y.  'edge' = outer pad edge (z 0.183), 'ctr' = pad centre (z 0.177); +z / -z = tipping toward the
    side the CG is offset to / away from it."""
    m, cg, I = mass_props(); g_ = geom()
    if g_['cg'] is not None: cg = np.array(g_['cg'], float)
    xf = g_['x_foot']; h = xf-cg[0]
    d = lambda w: math.degrees(math.atan2(w, h))
    out = dict(cg_x=cg[0], cg_y=cg[1], cg_z=cg[2], h=h, geom="legacy" if LEGACY else "CAD", I=np.diag(I),
               tip_narrow=d(g_['z_foot']), tip_wide=d(g_['y_foot']))
    out["tip_narrow_ctr_toward_cg"] = d(g_['z_foot']-cg[2]); out["tip_narrow_ctr_away"] = d(g_['z_foot']+cg[2])
    out["tip_narrow_edge_toward_cg"] = d(g_['z_edge']-cg[2]); out["tip_narrow_edge_away"] = d(g_['z_edge']+cg[2])
    out["tip_wide_toward_cg"] = d(g_['y_foot']-cg[1]); out["tip_wide_away"] = d(g_['y_foot']+cg[1])
    rho = 1.225; S = 0.22; W = m*G; half = 0.18; hcp = xf-0.5*0.245
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
            _tr = os.environ.get("LAND_TRACE")                      # T-105: opt-in time histories into the directory named by LAND_TRACE; unset = unchanged
            _h = [] if _tr else None
            r = simulate(Fp=Fp, hist=_h, **kw)
            if _tr:
                os.makedirs(_tr, exist_ok=True)
                write_trace(os.path.join(_tr, "landing_%s%s.json" % (name.replace(" ", "_").replace("+", "plus").replace("/", "-").replace(".", "p"), "_%gN" % Fp if len(sweep) > 1 else "")), name, Fp, kw, r, _h)
            print(f"{name:28s} stroke max {r['dmax_mm'].max():5.1f} mm  n {r['n_peak']:.2f}  Fmax {r['F'].max():5.1f} N  side {r['side'].max():5.1f} N  tilt_end {r['tilt_end']:5.1f}  drift {r['drift_end']*1e3:5.0f} mm  set {r['sp_mm'].max():.1f}  rib RF {r['rib_rf']:.2f}")
