"""T-084 D-185 study (FEA-lite: 3-D Euler-Bernoulli beam frame, structures/fe_a.py, free-free eigen-analysis; no shell / solid model).
Band and coupling metric UNCHANGED (structures_a.py / T-066: strongly coupled = cx or cy >= 0.5, excluded band 94-321 Hz = min hover 1P / 1.2 .. max 2P x 1.2).
Sections:
 1. Root cause of the coupling growth 0.45 (iter3) -> 0.52 (T-066): cumulative path from the iter3 inputs (structures/iter3_run.py CFG + fe_a defaults) to the current CAD, spar-only model.
 2. The in-band mode shape (spar-only model, nom).
 3. Three corners x three wing models on the T-084 CAD (FIN_H 0.1937): (a) spar only (T-066 model), (b) D-226 cell credited, nominal, (c) cell lower bound
    (cell properties: t084_cell_props.py, same section model as the landing rows; corners scale the CF parts only).
 4. Levers on the governing mode of model (b) (cage bounce on the bridge against the symmetric wing flap) at all corners.
python -I t084_modes_final.py > modes_final.txt   (about 2 min)"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.dont_write_bytecode = True
from t084_modes_probe import fe_a, fekw, BAND, m
import t084_cell_props as CP
KINDS = ('kd', 'nom', 'hi')


def solve(kind, model='spar', **over):
    cell = None if model == 'spar' else CP.cell_for(kind, lower=(model == 'lower'))
    F, info = fe_a.build(kind, **fekw(wing_cell=cell, **over)); return F, F.solve(130)


def strong(res): return [(f, cx, cy, e) for (f, e, v, cx, cy) in res if (cx >= 0.5 or cy >= 0.5) and f < 800]


def summary(res):
    st = strong(res); inb = [s for s in st if BAND[0] <= s[0] <= BAND[1]]
    lo = max([s[0] for s in st if s[0] < BAND[0]] or [0.0]); hi = min([s[0] for s in st if s[0] > BAND[1]] or [float('nan')])
    trk = max([(max(cx, cy), f, cx, cy) for (f, e, v, cx, cy) in res if 120 <= f <= 330])
    return inb, lo, hi, trk


def top(e): return ', '.join(f'{g} {100*x:.0f}%' for g, x in sorted(e.items(), key=lambda kv: -kv[1])[:3])


if __name__ == '__main__':
    print('# T-084 D-185 study (FEA-lite beam FE). Band %.0f-%.0f Hz, strong = cx or cy >= 0.5 (unchanged).' % BAND)
    # ---------------- 1. cumulative path (nom, spar only)
    cur = fekw(); it3 = dict(spar_tube=(0.012, 0.010), arm_tube=(0.012, 0.010), rib_tube=(0.014, 0.012), bridge_cfg='single+V', bridge_tube=(0.012, 0.010), vtube=(0.006, 0.0045),
                             bridge_yv=0.30, fin_strip=None, fin_tube=(0.016, 0.014, 3e-3, 0.055), x_fin=0.294, foot_pad_m=0.0025, x_hub=None, h_fin=None,
                             wing_g=212.0, pack_g=270.0, motor_g=65.0+11.06+5.0+4.3+2.9, avionics_g=110.0, centre_extra_g=65.0, hub_extra_g=20.0, root_g=6.0)
    steps = [('iter3 inputs (iter3_run.py CFG + fe_a defaults)', {}),
             ('+ rib 25x23 (T-077 p8, D-226)', dict(rib_tube=cur['rib_tube'])), ('+ bridge 16x14 (D-206)', dict(bridge_tube=cur['bridge_tube'])),
             ('+ struts 8x6 (T-077 p7, D-225)', dict(vtube=cur['vtube'])), ('+ strut end y 0.300 -> 0.285 (strut clamp, wing.py STRUT_E)', dict(bridge_yv=cur['bridge_yv'])),
             ('+ hub x -0.075 -> -0.078 (T-077 p4 / T-083b cage shifts)', dict(x_hub=cur['x_hub'])),
             ('+ wing group 212 -> %.0f g (D-226 cell, skins, bulkheads)' % cur['wing_g'], dict(wing_g=cur['wing_g'])),
             ('+ fin-root lumps 6 -> %.1f g (D-226 node, D-229 6061 fitting)' % cur['root_g'], dict(root_g=cur['root_g'])),
             ('+ centre 65 -> %.0f g (6061 centre node), avionics 110 -> %.0f g' % (cur['centre_extra_g'], cur['avionics_g']), dict(centre_extra_g=cur['centre_extra_g'], avionics_g=cur['avionics_g'])),
             ('+ hub 20 -> %.0f g (6061 hub), pack 270 -> %.0f g' % (cur['hub_extra_g'], cur['pack_g']), dict(hub_extra_g=cur['hub_extra_g'], pack_g=cur['pack_g'])),
             ('+ motor station 88.3 -> %.1f g (X2216, D-227 / D-228)' % cur['motor_g'], dict(motor_g=cur['motor_g'])),
             ('+ feet %.1f g, fin tip at FIN_H %.4f (T-084)' % (cur['foot_pad_m']*1e3, cur['h_fin']), dict(foot_pad_m=cur['foot_pad_m'], h_fin=cur['h_fin']))]
    print('\n## 1. Coupling growth, cumulative (spar-only model, nom corner): the mode with the largest motor coupling in 120-330 Hz')
    print('| step | f (Hz) | cx | cy | strong + in band? | top strain-energy groups |'); print('|---|---|---|---|---|---|')
    kw = dict(it3)
    for lab, d in steps:
        kw.update(d); F, info = fe_a.build('nom', **kw); res = F.solve(130)
        c, f, cx, cy = max([(max(cx, cy), f, cx, cy) for (f, e, v, cx, cy) in res if 120 <= f <= 330]); e = [r[1] for r in res if r[0] == f][0]
        print(f'| {lab} | {f:.1f} | {cx:.3f} | {cy:.3f} | {"YES" if c >= 0.5 else "no"} | {top(e)} |', flush=True)
    # ---------------- 2. mode shape (spar only, nom)
    F, res = solve('nom'); idx = F._idx
    c, f0, cx0, cy0 = summary(res)[3]; v = [r[2] for r in res if r[0] == f0][0]; e0 = [r[1] for r in res if r[0] == f0][0]
    print(f'\n## 2. Shape of the in-band mode, spar-only model, nom: {f0:.1f} Hz, cx {cx0:.3f}, cy {cy0:.3f}, {top(e0)} (mass-normalised translations; r = rotation)')
    print('| node | ux | uy | uz | rz |'); print('|---|---|---|---|---|')
    for nm in ['s+0.000', 's+0.150', 's+0.228', 's+0.285', 's+0.380', 's+0.450', 'hub', 'm+1+1', 'm+1-1', 'f+1r', 'f+1+1']:
        i = idx[nm]; print(f'| {nm} | {v[6*i]:+.3f} | {v[6*i+1]:+.3f} | {v[6*i+2]:+.3f} | {v[6*i+5]:+.2f} |')
    # ---------------- 3. corners x models
    print('\n## 3. Strongly coupled modes vs the band, T-084 CAD (FIN_H %.4f), three corners x three wing models' % m.FIN_H)
    print('| wing model | corner | strong modes IN the band (f, cx, cy) | highest strong below (Hz, margin to %.1f) | lowest strong above (Hz, margin to %.0f) | the 120-330 Hz mode with the largest coupling (f, max(cx,cy)) | D-185 (a) |' % BAND)
    print('|---|---|---|---|---|---|---|')
    OUT = {}
    for model, lab in (('spar', 'spar only (T-066 model)'), ('nominal', 'D-226 cell, nominal'), ('lower', 'D-226 cell, lower bound')):
        for kind in KINDS:
            F, res = solve(kind, model); inb, lo, hi, trk = summary(res); OUT[(model, kind)] = (inb, lo, hi, trk)
            print(f"| {lab} | {kind} | {'; '.join(f'{f:.1f} ({cx:.2f} / {cy:.2f})' for f, cx, cy, e in inb) or 'none'} | {lo:.1f} ({100*(BAND[0]/lo-1):+.0f} %) | {hi:.1f} ({100*(hi/BAND[1]-1):+.0f} %) | {trk[1]:.1f} ({trk[0]:.2f}) | {'FAIL' if inb else 'PASS'} |", flush=True)
    # governing mode shape in the cell model, hi
    F, res = solve('hi', 'nominal'); st = [s for s in strong(res) if s[0] < 150]
    f1, cx1, cy1, e1 = max(st, key=lambda s: s[0]); v = [r[2] for r in res if r[0] == f1][0]; idx = F._idx
    print(f'\nGoverning mode of the cell model at hi: {f1:.1f} Hz, cx {cx1:.2f} cy {cy1:.2f}, {top(e1)}:')
    print('| node | ux | uy | uz | ry |'); print('|---|---|---|---|---|')
    for nm in ['s+0.000', 's+0.150', 's+0.285', 's+0.450', 'hub', 'm+1+1', 'm+1-1', 'f+1r']:
        i = idx[nm]; print(f'| {nm} | {v[6*i]:+.3f} | {v[6*i+1]:+.3f} | {v[6*i+2]:+.3f} | {v[6*i+4]:+.2f} |')
    # ---------------- 4. levers on that mode (cell nominal; all corners)
    print('\n## 4. Levers on the cage-bounce mode (cell nominal / lower; f of the strong mode nearest the band low edge; in band = FAIL)')
    print('| lever | kd nom-cell | nom nom-cell | hi nom-cell | hi lower-cell | note |'); print('|---|---|---|---|---|---|')
    LV = [('as drawn (T-084)', {}, ''), ('bridge 12x10', dict(bridge_tube=(0.012, 0.010)), 'fails D-206 bridge torsion (bridge_torsion_d206.md)'),
          ('bridge 20x18', dict(bridge_tube=(0.020, 0.018)), 'not in the BOM'), ('struts 10x8', dict(vtube=(0.010, 0.008)), 'not in the BOM'),
          ('arms 14x12', dict(arm_tube=(0.014, 0.012)), 'R09 stock; +mass'), ('strut end y 0.300', dict(bridge_yv=0.30), 'strut Euler / R4 rows'),
          ('spar 14x12', dict(spar_tube=(0.014, 0.012)), 'R09'), ('pack 30 g lighter (info)', dict(pack_g=fekw()['pack_g']-30), 'not a design option')]
    for lab, ov, note in LV:
        vals = []
        for kind, model in (('kd', 'nominal'), ('nom', 'nominal'), ('hi', 'nominal'), ('hi', 'lower')):
            F, res = solve(kind, model, **ov); st = [s for s in strong(res) if 60 < s[0] < 200]
            f = max(s[0] for s in st) if st else float('nan'); vals.append(f'{f:.1f}{" IN" if BAND[0] <= f <= BAND[1] else ""}')
        print(f'| {lab} | ' + ' | '.join(vals) + f' | {note} |', flush=True)
