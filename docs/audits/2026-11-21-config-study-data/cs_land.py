"""Config study 2026-11-21: landing demand vs design touchdown speed / pad plateau, and feet-on-hub (legs) split.
Imports the repo modules unchanged (t077p6_demand.split3 basis, landing_a.simulate, landing_path_a.cases); writes only to argv[1].
Usage: python -I cs_land.py OUT.json [variant ...]   variant = v:Fp:smax  (v = hard-case sink m/s)"""
import os, sys, json, math, time
REPO = r"C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/mechanism/out/T077p6_data"
sys.path.insert(0, REPO)
import t077p6_demand as D            # sets LAND_MASS_KG 1.705, CG 23.91, cad mass model
import numpy as np
T2 = D.T2
c = T2.ctx(); P, L = c['P'], c['L']
L.MASS_MODEL = 'cad'; pts = T2.pts_for('cad')
P0 = c['P0']; S = np.array([0.060, 0.0, 0.0])           # spar axis point (common.SPAR_X)
yf = c['geom']['y_foot']

def wrenches(FB, xf, zf, feet_on_hub=False):
    """as D.split3; if feet_on_hub, the foot forces are external loads on the hub group (legs from the hub) instead of on the R / L halves."""
    w, chk, a_cg, alpha, dsh = D.split3(FB, pts, xf, yf, zf)
    feet = np.array([[xf, sy * yf, sz * zf] for sy in (1, -1) for sz in (1, -1)])
    out = {k: [w[k][0].copy(), w[k][1].copy()] for k in w}
    if feet_on_hub:
        for k_, key in ((0, 'R'), (1, 'L')):
            for j in (0, 1):
                f = FB[:, 2 * k_ + j, :]; s = feet[2 * k_ + j] - P0
                m = np.cross(np.broadcast_to(s, f.shape), f)
                out[key][0] += f; out[key][1] += m          # undo the subtraction in split3
                out['hub'][0] -= f; out['hub'][1] -= m
    res = {}
    for k in out:
        F, M = out[k]
        Ms = M + np.cross(np.broadcast_to(P0 - S, F.shape), F)   # moment about the spar-axis point
        res[k] = dict(My_P0=float(np.abs(M[:, 1]).max()), My_S=float(np.abs(Ms[:, 1]).max()), Mz_P0=float(np.abs(M[:, 2]).max()), Mx=float(np.abs(M[:, 0]).max()))
    return res, chk

def run(v_hard, Fp, smax, zetas=(0.02, 0.10), mus=(0.40, 0.30)):
    xf, zf, _ = T2.pad_geometry(smax); P.set_pad(xf, zf)
    agg = {}
    for zeta in zetas:
        for mu in mus:
            st = dict(stroke=0, n=0, tilt=0, Ffoot=0)
            mx = {'fins': {}, 'legs': {}}
            for name, kw in P.cases(False):
                kw = dict(kw)
                if abs(kw['v_sink'] - 1.2) < 1e-9: kw['v_sink'] = v_hard
                elif kw['v_sink'] > v_hard: kw['v_sink'] = v_hard
                r = L.simulate(Fp=Fp, s_max=smax, zeta=zeta, mu=mu, dt=2e-4, T=1.5, trace=True, **dict(kw, x_foot=xf, z_foot=zf))
                FB = r['trace'].reshape(-1, 4, 3)
                st['stroke'] = max(st['stroke'], float(r['dmax_mm'].max())); st['n'] = max(st['n'], float(r['n_peak']))
                st['tilt'] = max(st['tilt'], float(r['tilt_end'])); st['Ffoot'] = max(st['Ffoot'], float(r['F'].max()))
                for tag, foh in (('fins', False), ('legs', True)):
                    res, chk = wrenches(FB, xf, zf, foh)
                    for k in res:
                        for q, val in res[k].items():
                            key = k + '|' + q
                            if val > mx[tag].get(key, (0, ''))[0]: mx[tag][key] = (val, name)
            agg['%.2f|%.2f' % (zeta, mu)] = dict(stats=st, fins=mx['fins'], legs=mx['legs'])
            print('v %.2f Fp %.1f s %.0f zeta %.2f mu %.2f: %s hubMyS %.2f halfMyS %.2f | legs halfMyS %.2f' % (v_hard, Fp, smax * 1e3, zeta, mu, {k: round(v, 2) for k, v in st.items()},
                  mx['fins']['hub|My_S'][0], max(mx['fins']['R|My_S'][0], mx['fins']['L|My_S'][0]), max(mx['legs']['R|My_S'][0], mx['legs']['L|My_S'][0])), flush=True)
    return dict(xf=xf, zf=zf, agg=agg)

if __name__ == '__main__':
    out = sys.argv[1]; vs = sys.argv[2:] or ['1.2:30:0.024']
    allr = {}
    t0 = time.time()
    for v in vs:
        a, b, s = map(float, v.split(':'))
        allr[v] = run(a, b, s)
        json.dump(allr, open(out, 'w'), indent=1)
    print('done %.0f s' % (time.time() - t0))
