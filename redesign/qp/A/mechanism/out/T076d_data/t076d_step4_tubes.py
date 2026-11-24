"""T-076d step 4 (D-222 s4.3 item 4): FEA of the Al hub with the CF arm tubes and the sleeve bond judged by the LR-4 rule, partition B, on the step-2 / step-3 demand.
CATEGORY: FEA (linear elastic tet10, direct solve through MATLAB chol as fea_arm.solve) fed by rigid-body dynamics (RB) and the D-1 modal transient (dynamic wrenches).
    python -I t076d_step4_tubes.py --tag NAME --geom G0|G1 [--p k=v ...]       (mesh 8-25 min, solve 6-60 min, judging minutes: the stress response of every combo is a GEMM on precomputed per-Gauss-point functionals)
Geometry (GEO, imported from fea_hub_d.py = fea_hub_c6.py copy with three switches off by default): base = the T-076c H-A1 geometry (S_END 60, SLV_W 1.5, FIL 2.0, BR_CH 0.8, COL_E 21, X_BR0 15, X_HUB1 45, BR_GAP 0.5, MS 1.1);
  G0 = base (L_SLV 24, doubler s 11-25 ends 1 mm past the sleeve end, no chamfer);
  G1 = base + P1 + P2 of D-222 s4.2: DBL_S1 40 with the outer end tapered over 5 mm to a 0.4 mm tip (DBL_TAP 5, DBL_TIP 0.4: EST), SLV_CH 1.5 (45 deg internal chamfer at the sleeve mouth, modelled as a VOID: the epoxy fillet is not modelled, conservative), L_SLV 32.
Materials: hub = 6061-T6 (E 69,000 MPa, nu 0.33, rho 2.70, yield minimum 240 MPa: Wikipedia '6061 aluminium alloy', read 2026-11-20, T076c_hub_al.md s4; secondary source), tubes = the fea_arm CF orthotropic tube model, pins 70 GPa EST.
Demand (partition B): arm group (motors + arms) through the four stub ends, hub group (hub + pack) as a wrench on the hub aft face (RBE3), exactly the T-076 land_combos_sim recipe; candidate time steps = extremes of every arm-group
wrench component of each case + the 5 largest |M| (rank spacing 20).  Sets: RB (rigid body, step 2 sims at the chosen pad, CAD mass, pad-zeta 0.02 / 0.05 / 0.10) judged at x1.0 and x1.5, and D-1 dynamic histories (step 3, as-built bridge, kd / nom / hi, damping 1 %).
Tube rows (LR-4): Gauss points within 0.5 mm (EST) of a tied re-entrant ring (sleeve mouth, doubler start / end / taper start, in the (s, r) plane) are excluded from the 'judged' maxima; raw maxima over ALL points (old definition) are reported beside them.
 axial / hoop / in-plane shear tau_s,theta vs 350 / 40 / 30 MPa EST (x KF 1.725); interlaminar tau_s,r: value only (allowable '-': no coupon or data sheet), with the allowable it would need; old 'shear' = hypot(tau_s,r, tau_s,theta) raw max kept.
Bond: hub Gauss points within 0.35 mm of the bonded surface, |s| < L_SLV: mean tangential traction over each arm's bonded length (the lap-shear quantity), x KP 2.156 vs 2.0 MPa EST. Two definitions: 'T-076c' (surface r = 6.35 mm only: the direct hub-tube contact |s| < 11, as fea_hub_c6.evaluate) and 'full' (surface at the doubler radius where a doubler is bonded, the whole sleeve length).
Hub: von Mises max over Gauss points excluding 0.5 mm from tied re-entrant edges (t076c_judge.corner_nodes), vs 240 / KF = 139.1 MPa (the p99.9 weighted rows are not repeated here)."""
import argparse, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); T76 = os.path.abspath(os.path.join(HERE, '..', 'T076_data')); T76C = os.path.abspath(os.path.join(HERE, '..', 'T076c_data'))
S_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures'))
sys.path.insert(0, HERE); sys.path.insert(0, T76C); sys.path.insert(0, T76); sys.path.insert(0, S_DIR); sys.dont_write_bytecode = True
os.environ['LAND_MASS_KG'] = '1.64'
import numpy as np
import fea_hub_d as H
import t076c_judge as J
import t076b_run as TB            # regions() only
FEA = os.path.join(HERE, 'fea'); os.makedirs(FEA, exist_ok=True)
KF, KP = H.FA.KF, H.FA.KP; AL = H.FA.ALLOW
E_AL, NU_AL, SY_AL = 69000.0, 0.33, 240.0
BASE = dict(S_END=60.0, SLV_W=1.5, MS=1.1, FIL=2.0, BR_CH=0.8, COL_E=21.0, X_BR0=15.0, X_HUB1=45.0, BR_GAP=0.5)
G1 = dict(DBL_S1=40.0, DBL_TAP=5.0, DBL_TIP=0.4, SLV_CH=1.5, L_SLV=32.0)
EXCL, EXCL_TUBE = 0.5, 0.5
STS = ('UR', 'LL', 'LR', 'UL')


def coef(a, b):
    """Voigt (xx, yy, zz, yz, xz, xy) coefficient rows c (n,6) with a^T T b = sum c_k sigma_k, a and b (n,3)."""
    return np.stack([a[:, 0] * b[:, 0], a[:, 1] * b[:, 1], a[:, 2] * b[:, 2], a[:, 1] * b[:, 2] + a[:, 2] * b[:, 1], a[:, 0] * b[:, 2] + a[:, 2] * b[:, 0], a[:, 0] * b[:, 1] + a[:, 1] * b[:, 0]], 1)


def make_stubs():
    sts = STS; Pm = {st: H.motor_frame(st)[3] for st in sts}; P0 = np.array([24.0, 0.0, H.GEO['BR_Z']]); A = np.zeros((6, 6))
    for k in range(6):
        v = np.zeros(6); v[k] = 1.0; a, al = v[:3], v[3:]; F = np.zeros(3); Mo = np.zeros(3)
        for st in sts:
            r = Pm[st] - P0; f = a + np.cross(al, r); F += f; Mo += np.cross(r, f)
        A[:, k] = np.concatenate([F, Mo])
    Ainv = np.linalg.inv(A)
    def stubs(W6):
        sol = Ainv @ (-np.asarray(W6)); a, al = sol[:3], sol[3:]; loads = {}
        for st in sts:
            r = Pm[st] - P0; f = a + np.cross(al, r); loads[st] = H.to_stub(st, f, np.zeros(3), Pm[st])
        return loads
    return stubs


def candidates(Wa, n_top=5):
    idx = set()
    for k in range(6): idx.add(int(np.argmax(Wa[:, k]))); idx.add(int(np.argmin(Wa[:, k])))
    nrm = np.linalg.norm(Wa[:, 3:], axis=1) + 25.0 * np.linalg.norm(Wa[:, :3], axis=1)
    for j in np.argsort(-nrm)[:n_top * 20:20][:n_top]: idx.add(int(j))
    return sorted(idx)


def build_sets(stubs):
    """-> {set name: (C (n,30), labels)}, partition B coefficients (24 stub + 6 hub-group)."""
    sets = {}
    for zp in ('0.02', '0.05', '0.10'):
        f = os.path.join(FEA, 'rb_wrench_zeta%s.npz' % zp)
        if not os.path.exists(f): continue
        z = np.load(f); names = [str(n) for n in z['names']]; C, lab = [], []
        for nm in names:
            Wa = z[nm + '|Wa'].astype(float); Wh = z[nm + '|Wh'].astype(float); Wa = np.hstack([Wa[:, :3], Wa[:, 3:] * 1e3]); Wh = np.hstack([Wh[:, :3], Wh[:, 3:] * 1e3])
            for j in candidates(Wa): C.append(np.concatenate([H.coeffs(stubs(Wa[j])), -Wh[j]])); lab.append('RB z%s %s@%d' % (zp, nm, j))
        sets['RB z%s' % zp] = (np.array(C), lab)
        f = os.path.join(FEA, 'd1_wrench_zeta%s.npz' % zp)
        if os.path.exists(f):
            z = np.load(f); C, lab = [], []
            for key in z.files:
                if not key.endswith('|Wa'): continue
                base = key[:-3]; Wa = z[key].astype(float); Wh = z[base + '|Wh'].astype(float); Wa = np.hstack([Wa[:, :3], Wa[:, 3:] * 1e3]); Wh = np.hstack([Wh[:, :3], Wh[:, 3:] * 1e3])
                for j in candidates(Wa): C.append(np.concatenate([H.coeffs(stubs(Wa[j])), -Wh[j]])); lab.append('D1 z%s %s@%d' % (zp, base, j))
            sets['D1 z%s' % zp] = (np.array(C), lab)
    return sets


def tube_functionals(res, t):
    """per-Gauss-point functional matrices Q (30, nGP) for axial, hoop, tau_s,theta, tau_s,r, tau_theta,r of tube t (material 1 / 2), the GP coordinates and their (s, r)."""
    S, M, xg = res['S'], res['M'], res['xg']; mi = 1 if t == 'A' else 2; sel = M == mi
    St = S[:, sel].reshape(S.shape[0], -1, 6); xt = xg[sel].reshape(-1, 3); u = H.axes()[t]; x0 = np.array([H.tube_x(t), 0, 0])
    d = xt - x0; s = d @ u; rv = d - np.outer(s, u); r = np.linalg.norm(rv, axis=1); rn = rv / np.maximum(r, 1e-9)[:, None]; th = np.cross(u, rn); U = np.broadcast_to(u, rn.shape)
    Q = {nm: np.einsum('gk,bgk->bg', coef(a, b), St) for nm, (a, b) in (('axial', (U, U)), ('hoop', (th, th)), ('tau_st', (U, th)), ('tau_sr', (U, rn)), ('tau_tr', (th, rn)))}
    return Q, s, r


def rings(g):
    """(|s|, r) of the tied re-entrant rings on the tube / doubler outer surface (hub-frame mm)."""
    ro, dt = g['TUBE_RO'], g['DBL_T']; R = []
    L = g['L_SLV']; r_at = lambda s: ro + (dt if (g['DBL'] and g['DBL_S0'] <= s <= g['DBL_S1']) else 0.0)
    R.append((L, r_at(L)))
    if g.get('SLV_CH', 0.0) > 0: R.append((L - g['SLV_CH'], r_at(L - g['SLV_CH'])))
    R.append((g['DBL_S0'], ro + dt)); R.append((g['DBL_S1'], ro + (g.get('DBL_TIP', 0.4) if g.get('DBL_TAP', 0.0) > 0 else dt)))
    if g.get('DBL_TAP', 0.0) > 0: R.append((g['DBL_S1'] - g['DBL_TAP'], ro + dt))
    return R


def judge_tubes(res, Cs, labs, g):
    out = {}; Cs = np.asarray(Cs)
    for t in ('A', 'B'):
        Q, s, r = tube_functionals(res, t); keep_far = np.abs(s) < g['S_END'] - 15                       # skip the load-application zone at the stub ends
        near = np.zeros(len(s), bool)
        for (se, re_) in rings(g): near |= np.hypot(np.abs(s) - se, r - re_) < EXCL_TUBE
        sets = dict(raw=keep_far, judged=keep_far & ~near)
        rows = {}
        for nm in ('axial', 'hoop', 'tau_st', 'tau_sr', 'tau_tr'):
            for sn, m in sets.items():
                Qm = Q[nm][:, m]; bv, bj, bg = 0.0, 0, 0
                for ci in range(0, len(Cs), 48):
                    A = np.abs(Cs[ci:ci + 48] @ Qm); mx = A.max(1); j = int(np.argmax(mx))
                    if mx[j] > bv: bv, bj, bg = float(mx[j]), ci + j, int(np.argmax(A[j]))
                rows['%s|%s' % (nm, sn)] = dict(value=bv, case=labs[bj], at_s=float(s[m][bg]), at_r=float(r[m][bg]))
        # old definition: hypot(tau_sr, tau_st), raw max
        m = sets['raw']; best = 0.0
        for ci in range(0, len(Cs), 64):
            a = Cs[ci:ci + 64] @ Q['tau_sr'][:, m]; b = Cs[ci:ci + 64] @ Q['tau_st'][:, m]; best = max(best, float(np.hypot(a, b).max()))
        rows['old_shear|raw'] = dict(value=best)
        rows['_excluded_frac_gp'] = float((keep_far & near).sum() / keep_far.sum())
        out[t] = rows
    return out


def hub_functionals(res):
    return None


def judge_bond(res, Cs, g):
    """mean tangential traction on the bonded surface (hub Gauss points within 0.35 mm of it), each arm's bonded length, worst arm; two surface definitions."""
    S, M, xg = res['S'], res['M'], res['xg']; sel0 = M == 0; Sh = S[:, sel0].reshape(S.shape[0], -1, 6); xh = xg[sel0].reshape(-1, 3); Cs = np.asarray(Cs); ro, dt = g['TUBE_RO'], g['DBL_T']; out = {}
    for defn in ('T076c', 'full'):
        best = 0.0; peak = 0.0
        for t in ('A', 'B'):
            u = H.axes()[t]; x0 = np.array([H.tube_x(t), 0, 0]); d = xh - x0; s = d @ u; rv = d - np.outer(s, u); r = np.linalg.norm(rv, axis=1)
            if defn == 'T076c': rb = np.full(len(s), ro)
            else: rb = np.where((np.abs(s) >= g['DBL_S0']) & (np.abs(s) <= g['DBL_S1']) & (g['DBL'] > 0), ro + dt, ro)
            sel = (r < rb + 0.35) & (r >= rb - 0.05) & (np.abs(s) < g['L_SLV'])
            rn = rv[sel] / r[sel, None]; th = np.cross(u, rn); U = np.broadcast_to(u, rn.shape)
            Qa = np.einsum('gk,bgk->bg', coef(U, rn), Sh[:, sel]); Qb = np.einsum('gk,bgk->bg', coef(th, rn), Sh[:, sel])
            for sg_ in (1, -1):
                w = (s[sel] * sg_) > 0
                if not w.any(): continue
                ts = np.hypot(Cs @ Qa[:, w], Cs @ Qb[:, w]); best = max(best, float(ts.mean(1).max())); peak = max(peak, float(ts.max()))
        out[defn] = dict(mean_worst_arm=best, rf_KP=AL['bond'] / (KP * best), peak=peak)
    return out


def judge_hub(res, Cs, labs, allow, Jmask):
    S, M, xg = res['S'], res['M'], res['xg']; hub = M == 0; Sh = S[:, hub].reshape(S.shape[0], -1, 6); xh = xg[hub].reshape(-1, 3); Cs = np.asarray(Cs); best = (0.0, None, None); keep = Jmask
    for ci in range(0, len(Cs), 8):
        sig = np.einsum('cb,bgk->cgk', Cs[ci:ci + 8], Sh); vm = J.von_mises(sig); vm = np.where(keep[None, :], vm, 0.0)
        mx = vm.max(1); j = int(np.argmax(mx))
        if mx[j] > best[0]: best = (float(mx[j]), labs[ci + j], xh[int(np.argmax(vm[j]))].round(2).tolist())
    return dict(max_excl_vm=best[0], case=best[1], at=best[2], rf=allow / best[0])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tag', required=True); ap.add_argument('--geom', default='G0'); ap.add_argument('--p', nargs='*', default=[]); ap.add_argument('--daf', type=float, default=1.5); a = ap.parse_args()
    H.GEO.update(BASE)
    if a.geom == 'G1': H.GEO.update(G1)
    for kv in a.p: k, v = kv.split('='); H.GEO[k] = float(v)
    H.FA.E_PETG, H.FA.NU_PETG = E_AL, NU_AL; H.FA.OUT = FEA; H.OUT = FEA        # fea_arm is shared with the fea_hub_c6 imported by t076b_run, which resets FA.OUT to T076_data/fea: pin the solver scratch (sys/) to this directory
    t0 = time.time(); g = H.GEO
    print('# T-076d step 4: tag %s geometry %s GEO %s' % (a.tag, a.geom, json.dumps({k: g[k] for k in ('L_SLV', 'DBL_S0', 'DBL_S1', 'SLV_W', 'MS', 'S_END')} | {k: g.get(k, 0) for k in ('DBL_TAP', 'DBL_TIP', 'SLV_CH')})), flush=True)
    res = H.run(0, a.tag)
    print('mesh %d elements, %d free dof, hub volume %.0f mm3 = %.1f g Al, equilibrium error %.1e, wall %.0f s' % (res['nel'], res['ndof'], res['hub_vol'], res['hub_vol'] * 2.70e-3, res['eq'], time.time() - t0), flush=True)
    stubs = make_stubs(); sets = build_sets(stubs)
    print('demand sets: %s' % {k: len(v[1]) for k, v in sets.items()}, flush=True)
    edge = J.corner_nodes(res['X'], res['E'], res['M']); hub = res['M'] == 0; xh = res['xg'][hub].reshape(-1, 3); Jmask = J.exclusion_mask(res['X'], xh, edge, EXCL)
    out = dict(tag=a.tag, geom=a.geom, GEO=g, elements=res['nel'], dof=res['ndof'], hub_mm3=res['hub_vol'], hub_g_Al=res['hub_vol'] * 2.70e-3, eq=res['eq'], solve_wall_s=time.time() - t0, rows={})
    for name, (C, labs) in sets.items():
        tr = judge_tubes(res, C, labs, g); bd = judge_bond(res, C, g); hb = judge_hub(res, C, labs, SY_AL / KF, Jmask)
        out['rows'][name] = dict(tubes=tr, bond=bd, hub=hb, n_combos=len(labs))
        rf = lambda al, v: al / (KF * v)
        for t in ('A', 'B'):
            r = tr[t]
            print('%-9s tube %s judged(scale 1.0): axial %.1f MPa (RF %.2f) hoop %.1f (RF %.2f) tau_s,theta %.2f (RF %.2f) tau_s,r %.2f MPa (allowable -, needs >= %.1f for RF 1) | raw: axial %.1f hoop %.1f tau_st %.2f tau_sr %.2f old-shear %.2f (RF %.2f) | at s %.1f mm  excl-frac %.3f' % (
                name, t, r['axial|judged']['value'], rf(AL['cf_axial'], r['axial|judged']['value']), r['hoop|judged']['value'], rf(AL['cf_hoop'], r['hoop|judged']['value']), r['tau_st|judged']['value'], rf(AL['cf_shear'], r['tau_st|judged']['value']),
                r['tau_sr|judged']['value'], KF * r['tau_sr|judged']['value'], r['axial|raw']['value'], r['hoop|raw']['value'], r['tau_st|raw']['value'], r['tau_sr|raw']['value'], r['old_shear|raw']['value'], rf(AL['cf_shear'], r['old_shear|raw']['value']), r['tau_sr|judged']['at_s'], r['_excluded_frac_gp']), flush=True)
        print('%-9s bond mean shear (worst arm): T-076c definition %.3f MPa (RF %.2f at scale 1.0) | full bonded length %.3f MPa (RF %.2f) | hub von Mises max excl %.1f MPa (RF %.2f) at %s [%s]  [%.0f s]' % (
            name, bd['T076c']['mean_worst_arm'], bd['T076c']['rf_KP'], bd['full']['mean_worst_arm'], bd['full']['rf_KP'], hb['max_excl_vm'], hb['rf'], hb['at'], hb['case'], time.time() - t0), flush=True)
    out['total_wall_s'] = time.time() - t0
    json.dump(out, open(os.path.join(HERE, 'step4_%s.json' % a.tag), 'w'), indent=1, default=float)
    print('done %.0f s' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
