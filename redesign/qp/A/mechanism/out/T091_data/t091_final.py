"""T-091 confirmation: python -I t091_final.py <list-file> <out.json>  : all 24 T-085 bound groups x kd / nom / hi, 3 axes GM (spar centre), forced response (FC, zeta 1 / 0.5 %), D-185 strong modes, FE mass."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import t091_lib as L, t091_cands as C
import t091_run as R
_B = {}


def base_I(group, kind):
    k = (group, kind)
    if k not in _B:
        F, res = L.solve(kind, *group, None, nmodes=40)
        _B[k] = {c['ax']: 1.0/c['inv_I'] for c in L.FC.cases_frame(F, kind) if c['node'] == 'spar centre'}
    return _B[k]


def do(task):
    name, group, kind = task
    cand = dict(C.CANDS[name]); cell, hub, pad = group
    if cand.get('cell'): cand['cell'] = (lambda cl, kind_, f=C.CANDS[name]['cell'], lower=(cell == 'lower'): f(cl, kind_, lower))
    F, res = L.solve(kind, cell, hub, pad, cand, nmodes=400)
    bi = base_I(group, kind)
    out = dict(name=name, group=list(group), kind=kind)
    strong = [(float(f), float(cx), float(cy)) for (f, e, v, cx, cy) in res if (cx >= 0.5 or cy >= 0.5) and 60 <= f <= 400]
    out['strong'] = strong; out['d185_fail'] = any(94 <= f <= 321 for f, cx, cy in strong)
    out['mass_fe'] = float(sum(F.mass.values()) + sum(el[6]*float(np.linalg.norm(F.n[el[1]]-F.n[el[0]])) for el in F.el))
    dI = {ax: 0.0 for ax in bi}
    cs = {c['ax']: c for c in L.FC.cases_frame(F, kind) if c['node'] == 'spar centre'}
    dI = {ax: 1.0/cs[ax]['inv_I'] - bi[ax] for ax in bi}
    g = L.gm_axes(F, kind, dI); out['gm'] = {ax: {str(k): v for k, v in g[ax].items()} for ax in ('pit', 'rll', 'yaw')}
    out['forced'] = {str(z): v for z, v in L.forced(F, res, 's+0.000').items()}
    return out


if __name__ == '__main__':
    names = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    tasks = [(n, g, k) for n in names for g in L.GROUPS for k in L.KINDS]
    print(len(tasks), 'tasks', flush=True); t0 = time.time()
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(min(os.cpu_count() or 1, 18)) as ex: res = list(ex.map(do, tasks, chunksize=2))
    json.dump(res, open(sys.argv[2], 'w'), default=str); print('done %.0f s' % (time.time()-t0))
