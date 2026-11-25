"""T-076d step 2 (D-222 s4.3 item 2): landing demand table, rigid-body, 21 cases (+3 drift 0.70 cases) x {old ITEMS mass, CAD mass (maturity placement), CAD mass (class-E-only placement)} x pad grid.
CATEGORY: rigid-body dynamics (landing_a.simulate, unchanged) + hand-calculation proxies for the sleeve-exit moment and beam stresses (the audit's rc_levers / rc_hand method, rebuilt here).  No FEA.
    python -I t076d_step2_table.py [--workers 10]      (cwd anywhere; about 5-10 min with 10 workers; 1.5 s per sim)
Grid: Fp {26, 28, 30} N x usable stroke {22, 24, 26} mm x zeta {0.02, 0.05, 0.10}.  Plateau ramp s_y 1.5 mm, mu 0.40 (landing_a defaults), mass 1.64 kg, dt 0.2 ms, T 1.5 s.
Pad geometry follows the stroke as D-222 s4.1 recommends: free foam = 1.5 x usable (the present 2/3 usable ratio, EST), so x_foot = 0.3415 m + 1.5 (s_max - 0.020) and the pad edge is moved out to hold the A-P9 design target 30.5 deg
(z_edge = tan 30.5 deg (x_foot - cg_x) + cg_z, z_foot = z_edge - 0.006, pad dz 0.012 as electrical.py).  The baseline (s_max 20 mm) is exactly PAD_D2 (0.3415, 0.189).
Columns per grid point (max over the 21 cases): arm-group wrench Mz and |M| about the bore mouth P0 (arm group = motors + arms = idx 2, 3; the wrench the centre exerts), sleeve-exit moment (the audit proxy: the arm-group wrench mapped to four motor points with the
t076_main d'Alembert inverse, moment at s = 25 mm; approximate motor points as rc_levers.py), beam sigma / tau at s = 25 mm (FE motor points, as rc_hand.py), pad stroke, stroke reserve, end tilt, peak n, peak foot force.
Wrench split generalised to any point-mass list (the old model reproduces landing_centre_a.wrench_split to 1e-9: checked in main)."""
import os, sys, json, math, time, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
S_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures'))
os.environ['LAND_MASS_KG'] = '1.64'
sys.path.insert(0, S_DIR); sys.dont_write_bytecode = True
import numpy as np

MASS = 1.64
CASES_DRIFT70 = [("hard 10 wide + drift .7 y", dict(v_sink=1.2, th_w=10, drift=0.7, drift_dir=math.pi / 2)), ("hard 10 narrow + drift .7", dict(v_sink=1.2, th_n=10, drift=0.7, drift_dir=0.0)),
                 ("hard 7/7 + drift .7 diag", dict(v_sink=1.2, th_n=7, th_w=7, drift=0.7, drift_dir=math.pi / 4))]
FP = (26.0, 28.0, 30.0); SMAX = (0.022, 0.024, 0.026); ZETA = (0.02, 0.05, 0.10)
MODELS = ('items', 'cad', 'cad_E')
CTX = {}


def ctx():
    if CTX: return CTX
    import landing_a as L, landing_path_a as P, landing_centre_a as LC, landing_mass_cad as LM
    W = LC.W; cg = np.array(L.geom()['cg'], float); g = L.geom()
    CTX.update(L=L, P=P, LC=LC, LM=LM, cg=cg, geom=g, P0=np.array([W.HUB_X1, 0.0, W.BR_Z]))
    # sleeve-exit proxies (rc_levers / rc_hand): arm directions from the motor station (y 0.228, z 0.156), hub x -0.069
    phi = math.atan2(0.156, 0.228); uA = np.array([0, math.cos(phi), math.sin(phi)]); uB = np.array([0, math.cos(phi), -math.sin(phi)])
    RM = math.hypot(0.228, 0.156); XH = -0.069
    sts = {'UR': (uA, 1), 'LL': (uA, -1), 'LR': (uB, 1), 'UL': (uB, -1)}
    Pm = {k: np.array([XH, 0, 0]) + sg * RM * u for k, (u, sg) in sts.items()}
    HUBC = np.array([XH, 0.0, 0.0]); PmFE = {'UR': [-17.98, 226.02, 158.9], 'LL': [-17.98, -226.02, -158.9], 'LR': [-4.98, 229.98, -153.1], 'UL': [-4.98, -229.98, 153.1]}
    PmF = {k: HUBC + np.array(v) * 1e-3 for k, v in PmFE.items()}; TX = {'UR': -6.5, 'LL': -6.5, 'LR': 6.5, 'UL': 6.5}
    def inv(Pmx):
        A = np.zeros((6, 6))
        for k in range(6):
            v = np.zeros(6); v[k] = 1; a, al = v[:3], v[3:]; F = np.zeros(3); Mo = np.zeros(3)
            for st in sts:
                r = Pmx[st] - CTX['P0']; f = a + np.cross(al, r); F += f; Mo += np.cross(r, f)
            A[:, k] = np.concatenate([F, Mo])
        return np.linalg.inv(A)
    CTX.update(sts=sts, Pm=Pm, PmF=PmF, TX=TX, HUBC=HUBC, Ainv=inv(Pm), AinvF=inv(PmF))
    return CTX


def pts_for(model):
    """point masses (kg, x, y, z, idx) for the wrench split and the same model for the sim (L.MASS_MODEL / LM.PLACEMENT set)."""
    c = ctx(); L, LC, LM = c['L'], c['LC'], c['LM']
    if model == 'items':
        L.MASS_MODEL = 'items'; return [(g, x, y, z, i) for g, x, y, z, i in LC.sim_items(MASS)]
    L.MASS_MODEL = 'cad'; LM.PLACEMENT = 'maturity' if model == 'cad' else 'E'
    return [(m, x, y, z, i) for m, x, y, z, i, _ in LM.points(MASS)]


def wrench_split_pts(FBt, pts, hub_idx, x_foot, y_foot, z_foot):
    """generalised landing_centre_a.wrench_split for the 'hub' group only: wrench the CENTRE exerts on the sub-body (idx in hub_idx), about P0, rigid-body d'Alembert on a model translated so its CG sits at the CAD CG."""
    c = ctx(); cg = c['cg']; P0 = c['P0']
    m = sum(p[0] for p in pts); cgp = np.array([sum(p[0] * p[i] for p in pts) / m for i in (1, 2, 3)]); dsh = cg - cgp
    feet = np.array([[x_foot, sy * y_foot, sz * z_foot] for sy in (1, -1) for sz in (1, -1)]); rf = feet - cg
    Ib = np.zeros((3, 3))
    for g, x, y, z, idx in pts:
        r = np.array([x, y, z]) + dsh - cg; Ib += g * ((r @ r) * np.eye(3) - np.outer(r, r))
    Ibi = np.linalg.inv(Ib)
    Ftot = FBt.sum(axis=1); Mcg = np.zeros_like(Ftot)
    for i in range(4): Mcg += np.cross(np.broadcast_to(rf[i], FBt[:, i, :].shape), FBt[:, i, :])
    a_cg = Ftot / m; alpha = Mcg @ Ibi.T
    F = np.zeros_like(Ftot); Mo = np.zeros_like(Ftot)
    for g, x, y, z, idx in pts:
        if idx not in hub_idx: continue
        pos = np.array([x, y, z]) + dsh; rho = pos - cg; s = pos - P0
        f = g * (a_cg + np.cross(alpha, np.broadcast_to(rho, alpha.shape))); F += f; Mo += np.cross(np.broadcast_to(s, f.shape), f)
    return F, Mo


def exit_moment(Wt):
    """audit proxy (rc_levers.exit_moment): max over arms of |M| at s = 0.025 m on the arm; Wt (n,6) = (F, M) arm-group wrench the centre exerts."""
    c = ctx(); sts, Pm, P0, XH = c['sts'], c['Pm'], c['P0'], -0.069
    sol = (-Wt) @ c['Ainv'].T; a, al = sol[:, :3], sol[:, 3:]; Mmax = np.zeros(len(Wt))
    for st, (u, sg) in sts.items():
        r = Pm[st] - P0; f = a + np.cross(al, r); pe = np.array([XH, 0, 0]) + sg * 0.025 * u
        mm = np.cross(Pm[st] - pe, f); Mmax = np.maximum(Mmax, np.linalg.norm(mm, axis=1))
    return Mmax


Z_T = math.pi / 64 * (12**4 - 10**4) / 6; J_T = math.pi / 32 * (12**4 - 10**4); A_T = math.pi / 4 * (12**2 - 10**2)       # mm3, mm4, mm2 (12x10 tube)
def beam_rows(Wt):
    """audit hand rows (rc_hand.hand): sigma and tau (MPa) at s = 25 mm on each arm, FE motor points, 12 mm motor-point x offset torsion."""
    c = ctx(); sts, Pm, P0, HUBC, TX = c['sts'], c['PmF'], c['P0'], c['HUBC'], c['TX']
    sol = (-Wt) @ c['AinvF'].T; a, al = sol[:, :3], sol[:, 3:]; sig = 0; tau = 0
    for st, (u, sg) in sts.items():
        r = Pm[st] - P0; f = a + np.cross(al, r); pe = HUBC + np.array([TX[st] * 1e-3, 0, 0]) + sg * 0.025 * u
        m = np.cross(Pm[st] - pe, f) * 1e3; T = np.abs(m @ u); Mb = np.linalg.norm(m - np.outer(m @ u, u), axis=1); N = np.abs(f @ u); V = np.linalg.norm(f - np.outer(f @ u, u), axis=1)
        sig = np.maximum(sig, Mb / Z_T + N / A_T); tau = np.maximum(tau, T * 6 / J_T + 2 * V / A_T)
    return sig, tau


def pad_geometry(s_max):
    """x_foot, z_foot of the pad for usable stroke s_max (m): foam grows 1.5 x the stroke change (EST ratio), pad edge moved to hold A-P9 30.5 deg."""
    c = ctx(); P = c['P']; cg = c['cg']
    if abs(s_max - 0.020) < 1e-9: return P.PAD_D2['x_foot'], P.PAD_D2['z_foot'], 30.5
    x = P.PAD_D2['x_foot'] + 1.5 * (s_max - 0.020); edge = math.tan(math.radians(30.5)) * (x - cg[0]) + cg[2]
    return x, edge - 0.006, 30.5


def ap9(x, z_edge):
    c = ctx(); cg = c['cg']; return math.degrees(math.atan2(z_edge - cg[2], x - cg[0]))


def one(job):
    model, Fp, smax, zeta, name, kw = job
    c = ctx(); L, P = c['L'], c['P']; pts = pts_for(model)
    xf, zf, _ = pad_geometry(smax); P.set_pad(xf, zf)
    r = L.simulate(Fp=Fp, s_max=smax, zeta=zeta, dt=2e-4, T=1.5, trace=True, **dict(kw, x_foot=xf, z_foot=zf))
    FBt = r['trace'].reshape(-1, 4, 3)
    F, M = wrench_split_pts(FBt, pts, (2, 3), xf, c['geom']['y_foot'], zf); Wt = np.concatenate([F, M], 1)
    sig, tau = beam_rows(Wt)
    return dict(model=model, Fp=Fp, smax=smax, zeta=zeta, case=name, Mz_arm=float(np.abs(M[:, 2]).max()), M_arm=float(np.linalg.norm(M, axis=1).max()), F_arm=float(np.linalg.norm(F, axis=1).max()),
                Mexit=float(exit_moment(Wt).max()), sigma=float(sig.max()), tau=float(tau.max()), stroke=float(r['dmax_mm'].max()), tilt=float(r['tilt_end']), n=float(r['n_peak']), Ffoot=float(r['F'].max()),
                side=float(r['side'].max()))


def main():
    import concurrent.futures as cf
    nw = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 10
    c = ctx(); P = c['P']; P.set_pad(P.PAD_D2['x_foot'], P.PAD_D2['z_foot']); cases = list(P.cases(False)); L = c['L']
    # reproduction check of the generalised split against landing_centre_a.wrench_split (old model, baseline pad, one case)
    L.MASS_MODEL = 'items'; nm, kw = cases[6]
    r = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, **dict(kw, **P.PAD_D2)); FBt = r['trace'].reshape(-1, 4, 3)
    w = c['LC'].wrench_split(FBt, (2, 3))['hub']; F2, M2 = wrench_split_pts(FBt, pts_for('items'), (2, 3), P.PAD_D2['x_foot'], c['geom']['y_foot'], P.PAD_D2['z_foot'])
    chk = max(float(np.abs(w[0] - F2).max()), float(np.abs(w[1] - M2).max())); print('generalised wrench split vs landing_centre_a.wrench_split (old ITEMS, %s): max abs diff %.2e' % (nm, chk), flush=True)
    assert chk < 1e-6
    jobs = []
    for model in MODELS:
        for Fp, smax, zeta in itertools.product(FP, SMAX, ZETA):
            for name, kw in cases + CASES_DRIFT70: jobs.append((model, Fp, smax, zeta, name, kw))
        # baseline pad (30 N, 20 mm) for every zeta (old record: zeta 0.05)
        for zeta in ZETA:
            for name, kw in cases + CASES_DRIFT70: jobs.append((model, 30.0, 0.020, zeta, name, kw))
    print('%d sims, %d workers' % (len(jobs), nw), flush=True); t0 = time.time(); rows = []
    with cf.ProcessPoolExecutor(max_workers=nw) as ex:
        for i, rr in enumerate(ex.map(one, jobs, chunksize=8)):
            rows.append(rr)
            if i % 200 == 0: print('  %d / %d  [%.0f s]' % (i, len(jobs), time.time() - t0), flush=True)
    json.dump(rows, open(os.path.join(HERE, 'step2_rows.json'), 'w'), default=float)
    print('sims done %.0f s' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
