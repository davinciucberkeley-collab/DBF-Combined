"""T-076b row 1 driver: C6-family hub FEA (same solver, element, materials, loads, p99 convention as T-076 `t076_main.py`) plus a hot-spot location analysis.

  python -I t076b_run.py --tag NAME [--p k=v ...]      (cwd T076_data; imports the committed-unchanged patched copy fea_hub_c6.py)

Differences from t076_main.main: (1) the 301 landing combos (coefficients, geometry independent) are cached in fea/land164_combos.npz, so a second geometry skips the 23 rigid-body sims;
(2) the x1.5 rows are the RB rows scaled (the response is linear and the principal stress scales exactly: p99 x1.5, RF / 1.5, checked against the T-076 C6 numbers);
(3) after the solve the governing combo (whole-hub p99, partition A and B) is expanded to per-Gauss-point first principal stress and attributed to regions (hot-spot location).
Hub frame mm, N, MPa.  Category: FEA (linear elastic tet10, direct solve) fed by rigid-body dynamics.
"""
import argparse, json, os, sys, time
import numpy as np
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import fea_hub_c6 as H           # noqa: E402  (patched copy of structures/fea_hub.py; __main__ guard keeps it from running)
import t076_main as T            # noqa: E402

CACHE = os.path.join(D, 'fea', 'land164_combos.npz')


def combos_cached():
    if os.path.exists(CACHE):
        z = np.load(CACHE, allow_pickle=True)
        print('landing combos from cache', len(z['labs']), flush=True)
        return z['CA'], z['CB'], [str(s) for s in z['labs']]
    os.environ.setdefault('LAND_MASS_KG', '1.64')
    outA, outB, meta = T.land_combos_sim(H)
    CA = np.array([H.coeffs(c) for _, c in outA]); CB = np.array([T.coeffs30(H, c, hw) for _, c, hw in outB])
    labs = [l for l, _ in outA]
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    np.savez(CACHE, CA=CA, CB=CB, labs=np.array(labs), meta=np.array([json.dumps(m) for m in meta]))
    print('landing combos computed and cached:', len(labs), flush=True)
    return CA, CB, labs


def regions(xh):
    g = H.GEO
    x, y, z = xh[:, 0], xh[:, 1], xh[:, 2]
    U = H.axes()
    cb, bz = g['CB'], g.get('BLK_Z', 0.0)
    xa0 = g['XA'] - g['TUBE_RO'] - g['SLV_W']; xb1 = g['XB'] + g['TUBE_RO'] + g['SLV_W'] + g.get('BLK_AFT', 0.0)
    rs = g['TUBE_RO'] + g['SLV_W'] + g['DBL'] * g['DBL_T']
    rax = np.full(len(x), 1e9)
    for t in ('A', 'B'):
        d = xh - np.array([H.tube_x(t), 0.0, 0.0]); s = d @ U[t]
        rax = np.minimum(rax, np.linalg.norm(d - s[:, None] * U[t][None, :], axis=1))
    inblk = (x >= xa0) & (x <= xb1) & (np.abs(y) <= cb) & (z >= -cb + bz) & (z <= cb + bz)
    rbore = np.hypot(y, z - g['BR_Z'])
    xtb = g['XB'] + g['TUBE_RO']                                        # aft surface of tube B (x = 12.5)
    names = ['collar (x > 24)', 'aft block / bore wall (x > floor+2, <= 24)', 'floor band (tube-B surface to floor+2 mm, r < bore+2)', 'sleeves outside the block box', 'block forward of the floor band']
    lab = np.full(len(x), 4)
    lab[inblk] = 4
    lab[(~inblk) & (rax <= rs + 0.5)] = 3
    lab[(x >= xtb - 0.5) & (x <= g['X_BR0'] + 2.0) & (rbore < g['BR_RO'] + 2.0)] = 2
    lab[(x > g['X_BR0'] + 2.0) & (x <= 24.0)] = 1
    lab[x > 24.0] = 0
    return lab, names


def hotspot(res, C, label, tag_part):
    S, M, xg = res['S'], res['M'], res['xg']
    hub = M == 0
    nb = C.shape[0] if False else S.shape[0]
    Sh = S[:, hub].reshape(nb, -1, 6); xh = xg[hub].reshape(-1, 3)
    sig = np.einsum('k,kps->ps', C, Sh)
    p1, _ = H.FA.principal(sig[None])
    p1 = p1[0]
    allow = H.FA.ALLOW['petg'] / H.FA.KP
    lab, names = regions(xh)
    out = dict(case=label, partition=tag_part, allow_MPa=allow, n_gp=int(len(p1)), p99_whole=float(np.percentile(p1, 99)), max=float(p1.max()),
               n_over_allow=int((p1 > allow).sum()), regions={})
    print('--- hot-spot %s (%s): whole-hub p99 %.2f MPa, max %.1f, %d GP above allow %.2f of %d (1%% = %d)' % (label, tag_part, out['p99_whole'], out['max'], out['n_over_allow'], allow, len(p1), len(p1) // 100), flush=True)
    for k, nm in enumerate(names):
        s = lab == k
        if not s.any():
            continue
        r = dict(n_gp=int(s.sum()), p99=float(np.percentile(p1[s], 99)), p999=float(np.percentile(p1[s], 99.9)), max=float(p1[s].max()), n_over=int((p1[s] > allow).sum()))
        out['regions'][nm] = r
        print('  %-62s n %7d  p99 %6.2f  p99.9 %6.2f  max %7.1f  >allow %5d' % (nm, r['n_gp'], r['p99'], r['p999'], r['max'], r['n_over']), flush=True)
    # element-level (each GP group of 4 is one element): peak position list, de-duplicated by 1 mm cell
    top = np.argsort(-p1)[:4000]
    seen, rows = set(), []
    for j in top:
        key = tuple(np.round(xh[j] / 1.5).astype(int))
        if key in seen:
            continue
        seen.add(key); rows.append(dict(x=float(xh[j, 0]), y=float(xh[j, 1]), z=float(xh[j, 2]), p1=float(p1[j]), region=names[lab[j]]))
        if len(rows) >= 14:
            break
    out['top_cells_1p5mm'] = rows
    for r in rows:
        print('  top cell x %6.2f y %6.2f z %6.2f  p1 %6.1f  %s' % (r['x'], r['y'], r['z'], r['p1'], r['region']), flush=True)
    # p99 over the whole hub with the failing region masked (shows what sets the p99 elsewhere)
    for k, nm in enumerate(names):
        s = lab != k
        out['regions'].setdefault(nm, {})['whole_hub_p99_without_region'] = float(np.percentile(p1[s], 99))
    print('  whole-hub p99 with region removed:', {nm[:18]: round(out['regions'][nm]['whole_hub_p99_without_region'], 2) for nm in names if nm in out['regions']}, flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', required=True)
    ap.add_argument('--p', nargs='*', default=[])
    a = ap.parse_args()
    for kv in a.p:
        k, v = kv.split('='); H.GEO[k] = float(v)
    t0 = time.time()
    res = H.run(0, a.tag)
    print('mesh %d elements, %d free dof, hub block %.2f g, %.0f s' % (res['nel'], res['ndof'], res['hub_vol'] * 1.27e-3, time.time() - t0), flush=True)
    results = dict(geo=H.GEO, hub_g=res['hub_vol'] * 1.27e-3, equilibrium=res['eq'], elements=res['nel'], dof=res['ndof'], solve_wall_s=time.time() - t0)
    CA, CB, labs = combos_cached()
    res24 = dict(res); res24['S'] = res['S'][:24]
    results['landing'] = {}
    for nm, rr, CC in (('A_all_through_arms', res24, CA), ('B_partition', res, CB)):
        rows = T.eval_gen(H, rr, CC, labs, 1.0)
        results['landing'][nm + ' RB'] = rows
        results['landing'][nm + ' RBx1.5'] = {k: dict(v, p99_MPa=v['p99_MPa'] * 1.5, max_MPa=v['max_MPa'] * 1.5, RF_p99=v['RF_p99'] / 1.5, RF_max_singular=v['RF_max_singular'] / 1.5, note='RB row scaled by 1.5 (linear)') for k, v in rows.items()}
        print('LANDING', nm, json.dumps({k: (round(v['p99_MPa'], 2), round(v['RF_p99'], 3), v['p99_case']) for k, v in rows.items()}), flush=True)
    results['hotspot'] = {}
    for nm, rr, CC in (('A', res24, CA), ('B', res, CB)):
        gl = results['landing'][('A_all_through_arms' if nm == 'A' else 'B_partition') + ' RB']['whole hub']['p99_case']
        j = labs.index(gl)
        results['hotspot'][nm] = hotspot(rr, CC[j], gl, nm)
    results['total_wall_s'] = time.time() - t0
    json.dump(results, open(os.path.join(D, 't076b_hub_result_%s.json' % a.tag), 'w'), indent=1)
    print('done %.0f s' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
