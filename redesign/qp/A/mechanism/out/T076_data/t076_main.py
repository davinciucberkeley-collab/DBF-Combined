"""T-076 row 1 driver (FEA, linear elastic tet10, direct solve).  Called from fea_hub_c6.py (a patched copy of structures/fea_hub.py).

  python -I fea_hub_c6.py --tag NAME [--land DIR_WITH_demand_series.npz] [--p k=v ...]

One solve gives the 24 unit-load responses (6 components at each of the 4 arm stub ends).  Every load case is a linear
combination of them, so the same solve evaluates (a) the standard D-209 flight / strike cases (F1, F2, S1-S3, via fea_hub.evaluate)
and (b) the landing wrench cases of T-071b / T-074 (rigid-body demand, 23 cases, hub side of the centre, base partition).

Landing load model (rigid-body dynamics demand, FEA response): the centre exerts a wrench (F, M about the original bore mouth P0)
on the hub side.  d'Alembert: the hub-side inertia loads are -(F, M).  They are applied to the model as a rigid-body inertia field on the
four equal motor+arm masses (F_i = m (a + alpha x (P_i - P0)), 6 unknowns solved so the sum and moment match), carried to the
stub ends exactly; the bridge-tube far end is the support (reaction = the centre wrench).  The pack / hub / tray inertia is NOT
applied where it acts (the tray is not in the model): the whole wrench is forced through the arms and sleeves into the block and the
bore, a bound for the sleeves and block and a fair load for the bore / collar (the collar sees the same wrench either way).
"""
import argparse
import json
import os
import time

import numpy as np


def land_combos(H, npz, tag='base', n_top=5):
    """-> list of (label, loads dict), the candidate time steps per case (signed extremes of the 6 wrench components + top by |M|)."""
    d = np.load(npz, allow_pickle=True)
    names = [str(n) for n in d['names']]
    P0 = np.array([24.0, 0.0, H.GEO['BR_Z']])      # original bore mouth, hub frame mm (HUB_X1 - HUB[0] = 24.0, BR_Z -2.0)
    sts = ('UR', 'LL', 'LR', 'UL')
    Pm = {st: H.motor_frame(st)[3] for st in sts}
    # mass-weighted rigid-body field matrix (unit masses): [a(3); alpha(3)] -> [sum F; sum r x F about P0]
    A = np.zeros((6, 6))
    for k in range(6):
        v = np.zeros(6); v[k] = 1.0
        a, al = v[:3], v[3:]
        F = np.zeros(3); Mo = np.zeros(3)
        for st in sts:
            r = Pm[st] - P0
            f = a + np.cross(al, r)
            F += f; Mo += np.cross(r, f)
        A[:, k] = np.concatenate([F, Mo])
    Ainv = np.linalg.inv(A)
    out, meta = [], []
    for nm in names:
        F = d[f'{tag}|hub|F|{nm}'].astype(float)          # N, body frame, force of the centre on the hub side
        M = d[f'{tag}|hub|M|{nm}'].astype(float) * 1e3    # N mm about P0
        W = np.concatenate([F, M], axis=1)
        idx = set()
        for k in range(6):
            idx.add(int(np.argmax(W[:, k]))); idx.add(int(np.argmin(W[:, k])))
        nrm = np.linalg.norm(M, axis=1) + 25.0 * np.linalg.norm(F, axis=1)
        for j in np.argsort(-nrm)[:n_top * 20:20][:n_top]:
            idx.add(int(j))
        for j in sorted(idx):
            tgt = -W[j]                                     # d'Alembert inertia loads
            sol = Ainv @ tgt
            a, al = sol[:3], sol[3:]
            loads = {}
            for st in sts:
                r = Pm[st] - P0
                f = a + np.cross(al, r)
                loads[st] = H.to_stub(st, f, np.zeros(3), Pm[st])
            out.append((nm + '@%d' % j, loads)); meta.append((nm, j, W[j].tolist()))
    return out, meta



def land_combos_sim(H, n_top=5):
    """Same candidate-step selection as land_combos, but from the rigid-body sims directly (LAND_MASS_KG env must be set by the caller), so the hub-side wrench can be split
    into the arm group (motors 4 x 88 g + arms: ITEMS 2, 3) and the hub group (hub + pack: ITEMS 4, 6).  Returns lists of (label, loads24, loads30_B): case A = whole wrench through the arms (24 coeffs),
    case B = arm group through the stub ends, hub group through an RBE3 on the hub aft-face nodes (30 coeffs)."""
    import landing_path_a as P, landing_a as L, landing_centre_a as LC
    P.set_pad(P.PAD_D2['x_foot'], P.PAD_D2['z_foot'])
    P0 = np.array([24.0, 0.0, H.GEO['BR_Z']]); sts = ('UR', 'LL', 'LR', 'UL')
    Pm = {st: H.motor_frame(st)[3] for st in sts}
    A = np.zeros((6, 6))
    for k in range(6):
        v = np.zeros(6); v[k] = 1.0; a, al = v[:3], v[3:]; F = np.zeros(3); Mo = np.zeros(3)
        for st in sts:
            r = Pm[st] - P0; f = a + np.cross(al, r); F += f; Mo += np.cross(r, f)
        A[:, k] = np.concatenate([F, Mo])
    Ainv = np.linalg.inv(A)
    def stubs(W6):                                          # d'Alembert loads of a wrench W6 (F N, M N mm about P0) on the four motor masses -> stub-end loads
        sol = Ainv @ (-np.asarray(W6)); a, al = sol[:3], sol[3:]; loads = {}
        for st in sts:
            r = Pm[st] - P0; f = a + np.cross(al, r); loads[st] = H.to_stub(st, f, np.zeros(3), Pm[st])
        return loads
    outA, outB, meta = [], [], []
    for name, kw in P.cases(False):
        FBt = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, **dict(kw, **P.PAD_D2))['trace'].reshape(-1, 4, 3)
        wa = LC.wrench_split(FBt, (2, 3))['hub']; wh = LC.wrench_split(FBt, (4, 6))['hub']
        Wa = np.concatenate([wa[0], wa[1] * 1e3], 1); Wh = np.concatenate([wh[0], wh[1] * 1e3], 1); W = Wa + Wh
        idx = set()
        for k in range(6): idx.add(int(np.argmax(W[:, k]))); idx.add(int(np.argmin(W[:, k])))
        nrm = np.linalg.norm(W[:, 3:], axis=1) + 25.0 * np.linalg.norm(W[:, :3], axis=1)
        for j in np.argsort(-nrm)[:n_top * 20:20][:n_top]: idx.add(int(j))
        for j in sorted(idx):
            lab = name + '@%d' % j
            outA.append((lab, stubs(W[j]))); cB = stubs(Wa[j]); outB.append((lab, cB, -Wh[j])); meta.append((lab, W[j].tolist(), Wa[j].tolist(), Wh[j].tolist()))
    return outA, outB, meta

def coeffs30(H, loads, hubw):
    return np.concatenate([H.coeffs(loads), hubw])

def eval_gen(H, res, Cs, labels, scale):
    nb = res['S'].shape[0]
    S, M, xg = res['S'], res['M'], res['xg']
    hub = M == 0
    Sh = S[:, hub].reshape(nb, -1, 6); xh = xg[hub].reshape(-1, 3)
    Z = {k: z for k, z in zones(H, xh).items() if z.any()}
    Cs = np.asarray(Cs) * scale
    mx = {k: np.zeros(len(Cs)) for k in Z}; p99 = {k: np.zeros(len(Cs)) for k in Z}
    for ci in range(0, len(Cs), 32):
        sig = np.einsum('ck,kps->cps', Cs[ci:ci + 32], Sh)
        p1, _ = H.FA.principal(sig)
        for k, z in Z.items():
            mx[k][ci:ci + 32] = p1[:, z].max(1); p99[k][ci:ci + 32] = np.percentile(p1[:, z], 99, axis=1)
    allow = H.FA.ALLOW['petg'] / H.FA.KP; rows = {}
    for k in Z:
        j99 = int(np.argmax(p99[k])); jmx = int(np.argmax(mx[k]))
        rows[k] = dict(p99_MPa=float(p99[k][j99]), p99_case=labels[j99], max_MPa=float(mx[k][jmx]), max_case=labels[jmx], RF_p99=allow / float(p99[k][j99]), RF_max_singular=allow / float(mx[k][jmx]), allow_MPa=allow)
    return rows

def zones(H, xh):
    g = H.GEO
    x_old = 24.0
    x_mouth = g['X_HUB1']
    return {'whole hub': np.ones(len(xh), bool),
            'aft of block face (D-209 "bridge boss" definition)': xh[:, 0] > g['XB'] + g['TUBE_RO'] + g['SLV_W'],
            'last 12 mm before the bore mouth (collar in C6; block in base)': xh[:, 0] > x_mouth - 12.0,
            'collar extension only (x > 24)': xh[:, 0] > x_old + 0.01}


def eval_land(H, res, combos, scale):
    S, M, xg = res['S'], res['M'], res['xg']
    hub = M == 0
    Sh = S[:, hub].reshape(24, -1, 6); xh = xg[hub].reshape(-1, 3)
    Z = {k: z for k, z in zones(H, xh).items() if z.any()}
    Cs = np.array([H.coeffs(c) for _, c in combos]) * scale
    mx = {k: np.zeros(len(Cs)) for k in Z}; p99 = {k: np.zeros(len(Cs)) for k in Z}
    for ci in range(0, len(Cs), 32):
        sig = np.einsum('ck,kps->cps', Cs[ci:ci + 32], Sh)
        p1, _ = H.FA.principal(sig)
        for k, z in Z.items():
            mx[k][ci:ci + 32] = p1[:, z].max(1); p99[k][ci:ci + 32] = np.percentile(p1[:, z], 99, axis=1)
    allow = H.FA.ALLOW['petg'] / H.FA.KP
    rows = {}
    for k in Z:
        j99 = int(np.argmax(p99[k])); jmx = int(np.argmax(mx[k]))
        rows[k] = dict(p99_MPa=float(p99[k][j99]), p99_case=combos[j99][0], max_MPa=float(mx[k][jmx]), max_case=combos[jmx][0],
                       RF_p99=allow / float(p99[k][j99]), RF_max_singular=allow / float(mx[k][jmx]), allow_MPa=allow)
    worst = np.argsort(-p99['last 12 mm before the bore mouth (collar in C6; block in base)'] if 'last 12 mm before the bore mouth (collar in C6; block in base)' in p99 else -mx['whole hub'])[:12]
    return rows, [int(w) for w in worst]


def main(H):
    ap = argparse.ArgumentParser()
    ap.add_argument('--level', type=int, default=0)
    ap.add_argument('--tag', default='c6')
    ap.add_argument('--p', nargs='*', default=[])
    ap.add_argument('--land', default='', help='demand_series.npz of the landing wrench (landing_centre_a.py --recompute)')
    ap.add_argument('--skip-std', action='store_true')
    a = ap.parse_args()
    for kv in a.p:
        k, v = kv.split('=')
        H.GEO[k] = float(v)
    t0 = time.time()
    res = H.run(a.level, a.tag)
    print('mesh %d elements, %d free dof, hub block %.2f g, %.0f s' % (res['nel'], res['ndof'], res['hub_vol'] * 1.27e-3, time.time() - t0), flush=True)
    results = dict(geo=H.GEO, hub_g=res['hub_vol'] * 1.27e-3, equilibrium=res['eq'], elements=res['nel'], dof=res['ndof'], solve_wall_s=time.time() - t0)
    outA, outB, meta = land_combos_sim(H)
    print('landing combos:', len(outA), flush=True)
    results['landing_meta_first'] = meta[:3]
    res24 = dict(res); res24['S'] = res['S'][:24]
    CA = [H.coeffs(c) for _, c in outA]; CB = [coeffs30(H, c, hw) for _, c, hw in outB]
    labs = [l for l, _ in outA]
    results['landing'] = {}
    for scale, lab in ((1.0, 'RB'), (1.5, 'RBx1.5')):
        results['landing']['A_all_through_arms ' + lab] = eval_gen(H, res24, CA, labs, scale)
        results['landing']['B_partition ' + lab] = eval_gen(H, res, CB, labs, scale)
        print('LANDING', lab, json.dumps({k: v for k, v in results['landing'].items() if lab in k}, indent=1), flush=True)
    results['landing_B_peak_pack_hub_wrench'] = [max(abs(np.array(m[3])[k]) for m in meta) for k in range(6)]
    results['landing_B_peak_arm_group_wrench'] = [max(abs(np.array(m[2])[k]) for m in meta) for k in range(6)]
    if not a.skip_std:
        for name, cb in (('F1', H.flight_combos(H.FA.T_CAP, H.FA.Q_CAP)), ('F2', H.flight_combos(H.FA.T_UNC, H.FA.Q_UNC))):
            results[name] = H.evaluate(res24, cb)
            print(name, json.dumps(results[name])[:700], flush=True)
        for case in ('S1', 'S2', 'S3'):
            results[case] = H.evaluate(res24, [c for k, c in H.ground_combos() if k == case])
            print(case, json.dumps(results[case])[:500], flush=True)
    results['total_wall_s'] = time.time() - t0
    json.dump(results, open(os.path.join(H.OUT, '..', 't076_hub_result_%s.json' % a.tag), 'w'), indent=1)
    print('done %.0f s' % (time.time() - t0), flush=True)
