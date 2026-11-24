"""T-091 runner: python -I t091_run.py <candidate-prefix-or-list-file> <out.json> <groups: nominal|worst|all> <forced: 0|1> [nodes: s+0.000,hub,...]
Per (candidate, group, corner): strong modes (cx or cy >= 0.5, 60-400 Hz), D-185 verdict (strong mode in 94-321 Hz), pitch GM (D-191 method of t089_gm.py: zeta 0.3 / 1 %, thrust 0.77 / 1 / 1.25,
modes x 1.0 / 0.8 / 1.2, loop gain rescaled to I_T0 + (I_fe - I_fe_base), i.e. the CAD inertia basis of T-089 plus the model's own change), limiting pole, forced response (t089_fvib Modal / summarize)."""
import sys, os, json, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import t091_lib as L
import t091_cands as C
BAND = (94.0, 321.0)
WORST = ('lower', 'al6061', L.PAD_NAMES[0])      # placeholder, replaced by choose_worst() results (see report)
_BASE = {}


def i_base(group, kind):
    k = (group, kind)
    if k not in _BASE:
        F, res = L.solve(kind, group[0], group[1], group[2], None, nmodes=40)
        _BASE[k] = 1.0 / L.pit_case(F, kind)['inv_I']
    return _BASE[k]


def do(task):
    name, group, kind, nodes, want_f = task
    cand = dict(C.CANDS[name]); cell, hub, pad = group
    if cand.get('cell'): cand['cell'] = (lambda cl, kind_, f=C.CANDS[name]['cell'], lower=(cell == 'lower'): f(cl, kind_, lower))
    F, res = L.solve(kind, cell, hub, pad, cand, nmodes=(400 if want_f else 150))
    out = dict(name=name, group=list(group), kind=kind)
    strong = [(float(f), float(cx), float(cy)) for (f, e, v, cx, cy) in res if (cx >= 0.5 or cy >= 0.5) and 60 <= f <= 400]
    out['strong'] = strong; out['d185_fail'] = any(BAND[0] <= f <= BAND[1] for f, cx, cy in strong)
    out['first_modes'] = [(float(f), float(cx), float(cy)) for (f, e, v, cx, cy) in res if f < 135 and (max(cx, cy) > 0.3)]
    out['gm'] = {}; out['flex'] = {}; out['lim'] = {}
    Ib = i_base(group, kind)
    for nd in nodes:
        c = L.pit_case(F, kind, nd); I_t = L.I_T0 + (1.0/c['inv_I'] - Ib)
        out['I_fe'] = 1.0/c['inv_I']; out['dI'] = 1.0/c['inv_I'] - Ib
        g = L.gm_pitch(c, I_t); out['gm'][nd] = {str(k): v[0] for k, v in g.items()}
        out['flex'][nd] = [(float(a), float(b/c['inv_I'])) for a, b in c['flex'] if a < 135 and abs(b/c['inv_I']) > 0.03]
        out['lim'][nd] = L.limiting(c, 1.0, 0.003, 1.25, (1.0/c['inv_I'])/I_t)
        if want_f: out.setdefault('forced', {})[nd] = {str(z): v for z, v in L.forced(F, res, nd).items()}
    return out


def pick(spec):
    if os.path.exists(spec): return [l.strip() for l in open(spec) if l.strip()]
    return [n for n in C.CANDS if n.startswith(spec) or spec == 'all']


if __name__ == '__main__':
    spec, outp, grp, wf = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == '1'
    nodes = sys.argv[5].split(',') if len(sys.argv) > 5 else ['s+0.000']
    names = pick(spec)
    if grp == 'nominal': groups = [('nominal', 'al6061', L.PAD_NOM)]
    elif grp == 'worst': groups = [tuple(x.split('@')) for x in os.environ['T091_WORST'].split(';')]
    else: groups = L.GROUPS
    tasks = [(n, g, k, nodes, wf) for n in names for g in groups for k in L.KINDS]
    t0 = time.time(); print('%d tasks' % len(tasks), flush=True)
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(min(os.cpu_count() or 1, 18)) as ex: res = list(ex.map(do, tasks, chunksize=1))
    json.dump(res, open(outp, 'w'), indent=0, default=str)
    print('done %.0f s' % (time.time()-t0))
