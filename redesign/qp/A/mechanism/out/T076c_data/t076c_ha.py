"""T-076c step 4 (hub escalation s3.3 H-A1 / H-A2, D-220): machined-aluminium hub body, FEA (linear elastic tet10, direct solve) with the corrected judging code (t076c_judge.py).
  python -I t076c_ha.py --tag NAME [--p k=v ...]      (cwd anywhere; imports the committed-unchanged patched copy T076_data/fea_hub_c6.py; ~15-30 min per geometry)
CATEGORY: FEA (rigid-body dynamics demand: sim wrench combos; dynamic-transient wrenches: D-1 modal run).
Hub material: aluminium 6061-T6 (E 69 GPa, nu 0.33, rho 2.70 g/cm3, yield minimum 240 MPa; source and date in the evidence file, Wikipedia '6061 aluminium alloy', read 2026-11-20; secondary source, flagged).
Judging: von Mises, volume-weighted p99.9 per zone and max excluding 0.5 mm from tied corners, each x KF 1.725 against yield 240 MPa (KF never relaxed); old unweighted principal p99 kept alongside.
Load sets: RB = the 301 landing combos (T-076 cache, partitions A = whole wrench through the arms, B = arm group / hub group split), judged at scales 1.0, 1.5 (the audit floor) and DAF (D-1); DYN = hub-side wrench histories of D-1 (as-built bridge, kd / nom / hi, zeta 1 %)
selected like land_combos_sim (extremes of each component + top 5 by |M|), partition A; standard F1 / F2 (KF) and S1-S3 (factor 1.0, damage cases).  CF tube rows, bond rows from fea_hub_c6.evaluate (A partition).
"""
import argparse, json, os, sys, time, math
D = os.path.dirname(os.path.abspath(__file__)); T76 = os.path.abspath(os.path.join(D, '..', 'T076_data'))
sys.path.insert(0, T76); sys.path.insert(0, D); sys.dont_write_bytecode = True
import numpy as np
import fea_hub_c6 as H
import t076_main as T
import t076b_run as TB
import t076c_judge as J

E_AL, NU_AL, RHO_AL, SY_AL = 69000.0, 0.33, 2.70, 240.0          # MPa, -, g/cm3, MPa (Wikipedia 6061 aluminium alloy, read 2026-11-20: 69 GPa, 0.33, 2.70, yield at least 240 MPa)
KF = H.FA.KF; KP = H.FA.KP
H.FA.E_PETG, H.FA.NU_PETG = E_AL, NU_AL                          # the hub material slot of fea_hub_c6.run (Ds[0]); PETG is not used elsewhere
FEA = os.path.join(T76, 'fea')
DAF_FLOOR = 1.5


def dyn_combos(res_unused, n_top=5):
    """D-1 hub-side wrench histories -> candidate steps -> stub-end loads (partition A), exactly the land_combos_sim recipe."""
    z = np.load(os.path.join(FEA, 't076c_d1_hubwrench.npz'))
    sts = ('UR', 'LL', 'LR', 'UL'); Pm = {st: H.motor_frame(st)[3] for st in sts}; P0 = np.array([24.0, 0.0, H.GEO['BR_Z']])
    A = np.zeros((6, 6))
    for k in range(6):
        v = np.zeros(6); v[k] = 1.0; a, al = v[:3], v[3:]; F = np.zeros(3); Mo = np.zeros(3)
        for st in sts:
            r = Pm[st] - P0; f = a + np.cross(al, r); F += f; Mo += np.cross(r, f)
        A[:, k] = np.concatenate([F, Mo])
    Ainv = np.linalg.inv(A); C, labs = [], []
    for key in z.files:
        Wt = z[key].astype(float); Wt = np.hstack([Wt[:, :3], Wt[:, 3:] * 1e3])        # N, N mm about P0, centre on hub side (same sign as the sim wrench)
        idx = set()
        for k in range(6): idx.add(int(np.argmax(Wt[:, k]))); idx.add(int(np.argmin(Wt[:, k])))
        nrm = np.linalg.norm(Wt[:, 3:], axis=1) + 25.0 * np.linalg.norm(Wt[:, :3], axis=1)
        for j in np.argsort(-nrm)[:n_top * 20:20][:n_top]: idx.add(int(j))
        for j in sorted(idx):
            sol = Ainv @ (-Wt[j]); a, al = sol[:3], sol[3:]; loads = {}
            for st in sts:
                r = Pm[st] - P0; f = a + np.cross(al, r); loads[st] = H.to_stub(st, f, np.zeros(3), Pm[st])
            C.append(H.coeffs(loads)); labs.append('DYN %s@%d' % (key, j))
    return np.array(C), labs


def fmt(r):
    return {k: (round(v['value'], 2), v.get('rf') and round(v['rf'], 3), v['case']) for k, v in r.items() if isinstance(v, dict) and 'value' in v and v['value'] > 0}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tag', required=True); ap.add_argument('--p', nargs='*', default=[]); ap.add_argument('--daf', type=float, default=1.5)
    ap.add_argument('--excl', type=float, default=0.5); a = ap.parse_args()
    os.environ.setdefault('LAND_MASS_KG', '1.64')
    for kv in a.p:
        k, v = kv.split('='); H.GEO[k] = float(v)
    t0 = time.time(); res = H.run(0, a.tag)
    mass_g = res['hub_vol'] * RHO_AL * 1e-3
    print('mesh %d elements, %d free dof, hub volume %.0f mm3 = %.1f g aluminium (2.70 g/cm3), %.0f s; equilibrium err %.1e' % (res['nel'], res['ndof'], res['hub_vol'], mass_g, time.time() - t0, res['eq']), flush=True)
    CA, CB, labs = TB.combos_cached(); CD, labD = dyn_combos(None)
    print('combos: landing %d (A 24 / B 30 coeffs), dynamic D-1 %d' % (len(labs), len(CD)), flush=True)
    res24 = dict(res); res24['S'] = res['S'][:24]
    allow = SY_AL / KF
    out = dict(geo=H.GEO, hub_mm3=res['hub_vol'], hub_g_Al=mass_g, elements=res['nel'], dof=res['ndof'], eq=res['eq'], allow_vm_MPa=allow, yield_MPa=SY_AL, KF=KF, E=E_AL, nu=NU_AL, rho=RHO_AL, excl_mm=a.excl, daf_used=a.daf, rows={})
    for nm, rr, CC, lb in (('A_RB', res24, CA, labs), ('B_RB', res, CB, labs), ('A_DYN', res24, CD, labD)):
        r = J.judge(H, H.FA, rr, CC, lb, TB.regions, 'metal', allow, excl=a.excl, old=(nm != 'A_DYN')); out['rows'][nm] = r
        w = r['whole hub']; print('%s whole hub: old p99 %.1f | vol-weighted p99 %.1f p99.9 %.1f | max excl %.1f (RF at scale 1: %.2f / %.2f / %.2f)  [%.0f s]' % (nm, w.get('old_p99', {'value': float('nan')})['value'], w['w_p99']['value'], w['w_p999']['value'], w['max_excl']['value'], w['w_p999']['rf'], w['max_excl']['rf'], w['max_all']['rf'], time.time() - t0), flush=True)
        for zk, zr in r.items():
            print('   %-60s old p99 %6.1f  w p99 %6.1f  w p99.9 %6.1f  max excl %6.1f  max %6.1f  RF(p99.9, max excl) %.2f / %.2f  (excluded vol %.2f %%)' % (zk[:60], zr.get('old_p99', {'value': float('nan')})['value'], zr['w_p99']['value'], zr['w_p999']['value'], zr['max_excl']['value'], zr['max_all']['value'], zr['w_p999']['rf'], zr['max_excl']['rf'], 100 * zr['_zone']['excluded_vol_frac']), flush=True)
    # standard cases: flight F1/F2 (KF), strike S1-S3 (damage, factor 1.0)
    for name, cmb, fac in (('F1', H.flight_combos(H.FA.T_CAP, H.FA.Q_CAP), KF), ('F2', H.flight_combos(H.FA.T_UNC, H.FA.Q_UNC), KF)):
        Cc = np.array([H.coeffs(c) for c in cmb]); r = J.judge(H, H.FA, res24, Cc, [name + '#%d' % i for i in range(len(Cc))], TB.regions, 'metal', SY_AL / fac, excl=a.excl, verbose=False, old=False)
        out['rows'][name] = r; w = r['whole hub']; print('%s whole hub: w p99.9 %.1f max excl %.1f -> RF %.2f / %.2f' % (name, w['w_p999']['value'], w['max_excl']['value'], w['w_p999']['rf'], w['max_excl']['rf']), flush=True)
    for case in ('S1', 'S2', 'S3'):
        cmb = [c for k, c in H.ground_combos() if k == case]; Cc = np.array([H.coeffs(c) for c in cmb])
        r = J.judge(H, H.FA, res24, Cc, [case + '#%d' % i for i in range(len(Cc))], TB.regions, 'metal', SY_AL, excl=a.excl, verbose=False, old=False)
        out['rows'][case] = r; w = r['whole hub']; print('%s whole hub (factor 1.0): w p99.9 %.1f max excl %.1f -> RF %.2f / %.2f' % (case, w['w_p999']['value'], w['max_excl']['value'], w['w_p999']['rf'], w['max_excl']['rf']), flush=True)
    # tubes, bond, pins: fea_hub_c6.evaluate on the A-partition landing + dynamic combos (it expects load dicts: patch coeffs to identity on arrays)
    _c = H.coeffs; H.coeffs = lambda c: c
    try:
        ev_land = H.evaluate(res24, list(CA)); ev_dyn = H.evaluate(res24, list(CD))
    finally:
        H.coeffs = _c
    ev_f = {nm: H.evaluate(res24, cmb) for nm, cmb in (('F1', H.flight_combos(H.FA.T_CAP, H.FA.Q_CAP)), ('F2', H.flight_combos(H.FA.T_UNC, H.FA.Q_UNC)))}
    ev_s = {case: H.evaluate(res24, [c for k, c in H.ground_combos() if k == case]) for case in ('S1', 'S2', 'S3')}
    out['evaluate'] = dict(landing_RB=ev_land, dyn=ev_dyn, **ev_f, **ev_s)
    AL = H.FA.ALLOW
    def tube_rf(ev, scale, fac):
        rows = {}
        for t in ('A', 'B'):
            e = ev['tube_' + t]; rows['tube ' + t] = dict(axial=AL['cf_axial'] / (fac * e['axial'] * scale), hoop=AL['cf_hoop'] / (fac * e['hoop'] * scale), shear=AL['cf_shear'] / (fac * e['shear'] * scale))
        b = ev['bond']; rows['bond (mean shear, worst arm; x KP)'] = AL['bond'] / (KP * b['shear_mean_worst_arm'] * scale) if b.get('shear_mean_worst_arm') else None
        return rows
    out['tube_bond_rf'] = {'landing RB x1.0': tube_rf(ev_land, 1.0, KF), 'landing RB x1.5': tube_rf(ev_land, 1.5, KF), 'landing RB x%.2f' % a.daf: tube_rf(ev_land, a.daf, KF), 'D-1 dynamic wrenches': tube_rf(ev_dyn, 1.0, KF),
                           'F1': tube_rf(ev_f['F1'], 1.0, KF), 'F2': tube_rf(ev_f['F2'], 1.0, KF), 'S1 (factor 1.0)': tube_rf(ev_s['S1'], 1.0, 1.0), 'S2 (factor 1.0)': tube_rf(ev_s['S2'], 1.0, 1.0), 'S3 (factor 1.0)': tube_rf(ev_s['S3'], 1.0, 1.0)}
    for k, v in out['tube_bond_rf'].items(): print('TUBE/BOND RF', k, json.dumps({kk: (round(x, 2) if isinstance(x, float) else {a_: round(b_, 2) for a_, b_ in x.items()} if x else x) for kk, x in v.items()}), flush=True)
    out['total_wall_s'] = time.time() - t0
    json.dump(out, open(os.path.join(D, 'ha_result_%s.json' % a.tag), 'w'), indent=1, default=float)
    print('done %.0f s' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
