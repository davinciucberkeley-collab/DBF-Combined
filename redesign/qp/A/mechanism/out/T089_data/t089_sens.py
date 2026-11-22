"""T-089 part 1 support: validation of the harness against the stored iter3 values, decomposition (plant vs structure), limiting pole, and ILLUSTRATIVE sensitivities
(rate-gain scale, harmonic notch).  Nothing here feeds a claim except the validation rows; the claim values come from t089_gm.py.
Category: linear control analysis (illustrative sensitivities labelled as such).   python -I t089_sens.py -> t089_sens.json, stdout"""
import os, sys, math, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); QPA = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'T085_data')); sys.path.insert(0, os.path.join(HERE, '..', 'T084_data'))
sys.path.insert(0, os.path.join(QPA, 'sitl')); sys.path.insert(0, os.path.join(QPA, 'structures')); sys.dont_write_bytecode = True
import warnings; warnings.filterwarnings('ignore')
import numpy as np
import t089_gm as G
import fu_cage as FC

STORED = {'gm_nominal': [4.19, 4.25, 5.88, 2.37, 2.56, 3.32, 2.19, 2.23, 2.23], 'gm_shifted': [2.81, 2.68, 4.06, 2.16, 2.16, 2.30, 2.16, 2.16, 2.19], 'gm_shifted_up': [6.06, 5.70, 2.89, 3.22, 3.88, 6.06, 2.23, 2.26, 2.26]}
KEYS = [(ax, k) for ax in ('pit', 'rll', 'yaw') for k in G.KINDS]      # the stored order is "pit / rll / yaw x kd, nom, hi" (gen_params_a.py)


def gm_min(c, ax, sc, ks=1.0, notch=None, tsc=G.TSCALES, zet=G.ZETAS):
    modes = [(ff * sc if ff >= 1.0 else ff, gg) for ff, gg in c['modes']]
    gm = 99.0
    for z in zet:
        for ts in tsc:
            L = FC.loop(modes, ax, z, tfull_scale=ts, kscale=ks, notch=notch, **FC.A_PARAM_D191[ax])
            g = 1.0 if FC.maxre(L) >= -1e-6 else G.gm_scan(L)
            gm = min(gm, g)
    return gm


def limiting_pole(c, ax, sc, z, ts):
    """closed-loop pole (Hz) that first crosses into the RHP as the gain is raised (D-191 scan), and the gain factor"""
    modes = [(ff * sc if ff >= 1.0 else ff, gg) for ff, gg in c['modes']]
    L = FC.loop(modes, ax, z, tfull_scale=ts, **FC.A_PARAM_D191[ax]); A, B, C, D = L; BC = B @ C
    for k in np.geomspace(1.0, 100, 300):
        ev = np.linalg.eigvals(A - k * BC)
        if ev.real.max() >= -1e-9:
            e = ev[np.argmax(ev.real)]; return float(k), float(abs(e.imag) / 2 / math.pi)
    return None, None


def rigid_pm(c, ax, ks=1.0, notch=None):
    rig = [m for m in c['modes'] if m[0] < 1.0]
    L = FC.loop(rig, ax, 0.01, tfull_scale=1.0, kscale=ks, notch=notch, **FC.A_PARAM_D191[ax]); f, pm = FC.pm_first(L); return f, pm


NOTCHES = {'none': None, 'notch 113 Hz Q 2.8 att 20 dB': (113.0, 113.0 / 40.0, 0.1), 'notch 113 Hz Q 2.8 att 40 dB': (113.0, 113.0 / 40.0, 0.01)}


def sens_group(g):
    cell, hub, nm = g
    FC.configure('t089'); T, _ = G.groups(); part = {}
    for kind in G.KINDS:
        F, res = T.solve(kind, cell, hub, nm)
        for c in FC.cases_frame(F, kind):
            if c['node'] != 'spar centre': continue
            ax = c['ax']
            for ks in (1.0, 0.7, 0.5, 0.4):
                for nn, nt in (NOTCHES.items() if ks == 1.0 else [('none', None)]):
                    for sc in (1.0, 0.8, 1.2):
                        key = f'{ax}|ks{ks}|{nn}'; part[key] = min(part.get(key, 99.0), gm_min(c, ax, sc, ks=ks, notch=nt))
    return part


if __name__ == '__main__':
    out = {}
    T, GR = G.groups()
    # ---- 1. validation: legacy iter2 FE + legacy plant + D-191 gains vs the stored gm_* (iter3_run.md D-195 rerun)
    FC.configure('iter2'); C = FC.cases(); val = {}
    for sc, key in ((1.0, 'gm_nominal'), (0.8, 'gm_shifted'), (1.2, 'gm_shifted_up')):
        row = []
        for ax, k in KEYS:
            c = [x for x in C if x['ax'] == ax and x['k'] == k and x['node'] == 'spar centre'][0]
            row.append(gm_min(c, ax, sc, tsc=(0.77, 1.0, 1.25)))
        val[key] = row
    out['validation'] = dict(now=val, stored=STORED)
    print('VALIDATION (legacy plant + iteration-2 FE, current fe_a.py): now vs stored')
    for key in val: print(' ', key, [round(x, 2) for x in val[key]], 'stored', STORED[key], flush=True)
    # ---- 2. decomposition, base group (nominal cell, 6061 hub, pad 50 A / tray 24), kd / nom / hi, pit and yaw, modes x 1.0 and x 0.8 / x 1.2
    base = [g for g in GR if g[0] == 'nominal' and g[1] == 'al6061' and g[2].startswith('pad nom (50A') and 'K 0.25' not in g[2]][0]
    out['base'] = base; dec = {}
    framesN = {}
    for kind in G.KINDS:
        F, res = T.solve(kind, *base); framesN[kind] = F
    for plant in ('iter2', 't089'):
        for fe in ('iter2 FE', 'T-085 FE'):
            FC.configure(plant)
            for kind in G.KINDS:
                if fe == 'iter2 FE':
                    import fe_a
                    F, info = fe_a.build(kind, **FC.CFG); F.solve(60)
                else: F = framesN[kind]
                for c in FC.cases_frame(F, kind):
                    if c['node'] != 'spar centre': continue
                    dec[(plant, fe, c['ax'], kind)] = [gm_min(c, c['ax'], sc) for sc in (1.0, 0.8, 1.2)]
    out['decomp'] = {'|'.join(k): v for k, v in dec.items()}
    print('DECOMPOSITION base group (min GM over zeta, thrust scale; modes x1.0 / x0.8 / x1.2; FE inertia)')
    for k, v in dec.items():
        if k[2] in ('pit', 'yaw'): print(' ', k, [round(x, 2) for x in v])
    # ---- 3. limiting pole, T-085 frame, base group, zeta 0.003, ts 1.0 and 1.25
    FC.configure('t089'); lp = {}
    for kind in G.KINDS:
        for c in FC.cases_frame(framesN[kind], kind):
            if c['node'] != 'spar centre': continue
            for sc in (1.0, 0.8, 1.2):
                lp[f'{c["ax"]}|{kind}|{sc}'] = limiting_pole(c, c['ax'], sc, 0.003, 1.25)
    out['limiting'] = lp
    print('LIMITING POLE (gain factor, Hz) base group, zeta 0.3 %, thrust x1.25:'); print(' ', {k: (round(v[0], 2) if v[0] else None, round(v[1], 1) if v[1] else None) for k, v in lp.items() if k.startswith('pit') or k.startswith('yaw')}, flush=True)
    # ---- 4. ILLUSTRATIVE sensitivities over ALL 24 groups: rate-gain scale ks (all axes), and a harmonic notch (not credited by D-191)
    notches = NOTCHES
    sens = {}
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(min(os.cpu_count() or 1, 8)) as ex:
        for part in ex.map(sens_group, GR):
            for k, v in part.items(): sens[k] = min(sens.get(k, 99.0), v)
    out['sens_FE'] = sens
    print('SENSITIVITY (min over 24 groups x kd/nom/hi x modes 0.8/1.0/1.2 x zeta x thrust scale; FE inertia):')
    for k, v in sorted(sens.items()): print(' ', k, round(v, 2))
    # rigid crossover and PM, base group nominal corner, per axis, for the gain scales
    pm = {}
    for c in FC.cases_frame(framesN['nom'], 'nom'):
        if c['node'] != 'spar centre': continue
        for ks in (1.0, 0.7, 0.5, 0.4):
            pm[f'{c["ax"]}|ks{ks}'] = rigid_pm(c, c['ax'], ks)
        pm[f'{c["ax"]}|ks1.0|notch40'] = rigid_pm(c, c['ax'], 1.0, notches['notch 113 Hz Q 2.8 att 40 dB'])
    out['rigid_pm'] = pm
    print('RIGID crossover Hz / PM deg (zeta 1 %, thrust x1.0, nominal corner):', {k: (round(v[0], 2), round(v[1], 0)) for k, v in pm.items()})
    json.dump(out, open(os.path.join(HERE, 't089_sens.json'), 'w'), indent=1, default=str)
