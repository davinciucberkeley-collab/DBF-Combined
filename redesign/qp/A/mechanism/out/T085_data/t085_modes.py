"""T-085 D-185 re-judgement (FEA-lite: 3-D Euler-Bernoulli beam frame fe_a.py with T-085 options; free-free eigen-analysis; no shell model).
Band 94-321 Hz and strong coupling (cx or cy >= 0.5) UNCHANGED (T-066 / T-084).  Options added to fe_a (defaults reproduce T-066 / T-084):
  wing_cell (T-084, D-226 cell credited), pack_cfg (pack on the drawn tray CGE-008), hub_se (hub superelement from the solid hub FEA, t085_hubflex.py).
Sections: 0 validation, 1 hub joint (from the hub FEA), 2 modelling bounds x corners x wing cell, 3 strong modes + shapes, 4 design-option sketches (D-233 C).
python -I t085_modes.py > modes_t085.txt"""
import os, sys, math, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); T84 = os.path.join(HERE, '..', 'T084_data')
sys.path.insert(0, T84); sys.path.insert(0, HERE); sys.dont_write_bytecode = True
from t084_modes_probe import fe_a, fekw, BAND, m
import t084_cell_props as CP
KINDS = ('kd', 'nom', 'hi')

# ---------------- hub joint (superelement) from the hub FEA flexibility
HUB = {}
for mat in ('al6061', 'petg'):
    p = os.path.join(HERE, 'hubflex_%s.npz' % mat)
    if os.path.exists(p):
        d = np.load(p); pts = d['pts']; pb = d['fix_centroid']
        K = fe_a.hub_superelement(d['Fl'], pts, pb)
        HUB[mat] = dict(K=K, pts_mm={'UR': pts[0], 'LL': pts[1], 'LR': pts[2], 'UL': pts[3], 'hub': pts[4], 'bb': pb}, s_end_mm=60.0, Fl=d['Fl'])

# ---------------- pack on the tray: geometry from the CAD (common / wing: PACK_X, TRAY plate, hub collar) + EST pad
XP = 0.5*(m.PACK_X[0]+m.PACK_X[1]); ZP = 0.008+0.001+0.023            # tray top z 8 mm + pad 1.0 mm (PWR-003) + half the 46 mm pack
SOL = 1.0-m.tray_stats()['window_frac']
X_C0, X_C1 = m.HUB[0]+m.BLK_X[1], m.HUB[0]+m.COL_X1                      # collar top x range (flush with the plate top z 8)
PAD_X0, PAD_X1 = XP-0.015, XP+0.015                                       # PWR-003 pad 100 (y) x 30 (x) x 1.0 mm, centred on the pack
OV = max(0.0, min(PAD_X1, X_C1)-max(PAD_X0, X_C0)); COLLAR_X = 0.5*(max(PAD_X0, X_C0)+min(PAD_X1, X_C1)); COLLAR_A = OV*2*m.COL_HY
PACKS = {
    'lump':        None,
    'rigid':       dict(mode='rigid', x=XP, z=0.031),                     # T-084 pack_place (z as there)
    'rigid+rot':   dict(mode='rigid', x=XP, z=ZP, rot=True),
    'tray stiff':  dict(mode='tray', x=XP, z=ZP, w=0.112, solid=SOL, pad_E=4e6, pad_A=3.0e-3, collar_x=COLLAR_X, collar_A=COLLAR_A),
    'tray nom':    dict(mode='tray', x=XP, z=ZP, w=0.024, solid=SOL, pad_E=2e6, pad_A=3.0e-3, collar_x=COLLAR_X, collar_A=COLLAR_A),
    'rigid+rot spar': dict(mode='rigid', x=XP, z=ZP, rot=True, anchor='s+0.000'),      # option C2 sketch: pack carried by the wing centre node (rigid carrier)
    'tray nom spar':  dict(mode='tray', x=XP, z=ZP, w=0.024, solid=SOL, pad_E=2e6, pad_A=3.0e-3, collar_x=COLLAR_X, collar_A=COLLAR_A, anchor='s+0.000'),
    'tray soft':   dict(mode='tray', x=XP, z=ZP, w=0.024, solid=SOL, pad_E=0.5e6, pad_A=3.0e-3, collar_x=COLLAR_X, collar_A=COLLAR_A),
}


def solve(kind, model='nominal', hub='rigid', pack='lump', **over):
    cell = None if model == 'spar' else CP.cell_for(kind, lower=(model == 'lower'))
    kw = fekw(wing_cell=cell, **over)
    if hub != 'rigid': kw['hub_se'] = HUB[hub]
    if PACKS[pack] is not None: kw['pack_cfg'] = PACKS[pack]
    F, info = fe_a.build(kind, **kw); return F, F.solve(150)


def strong(res, fmax=800): return [(f, cx, cy, e, v) for (f, e, v, cx, cy) in res if (cx >= 0.5 or cy >= 0.5) and f < fmax]


def summary(res):
    st = strong(res); inb = [s for s in st if BAND[0] <= s[0] <= BAND[1]]
    lo = max([s[0] for s in st if s[0] < BAND[0]] or [0.0]); hi = min([s[0] for s in st if s[0] > BAND[1]] or [float('nan')])
    trk = max([(max(cx, cy), f, cx, cy) for (f, e, v, cx, cy) in res if 120 <= f <= 330])
    return inb, lo, hi, trk


def top(e, n=3): return ', '.join(f'{g} {100*x:.0f}%' for g, x in sorted(e.items(), key=lambda kv: -kv[1])[:n])


def shape(F, v):
    """rms translation (mass-normalised units) of node groups, per axis; and the three groups with the largest motion."""
    idx = F._idx; G = {'wing spar': [k for k in idx if k.startswith('s') and '>' not in k and k[1] in '+-'], 'hub': ['hub'], 'pack': [k for k in idx if k in ('pack', 'pk')],
                       'motors': [k for k in idx if k[:2] in ('m+', 'm-') and '>' not in k], 'fin tips': [k for k in idx if k.startswith('f') and '>' not in k and k[1] in '+-' and k[-1] != 'r'],
                       'tray': [k for k in idx if k in ('trc',)]}
    out = []
    for g, ns in G.items():
        if not ns: continue
        a = np.array([[v[6*idx[n]+q] for q in range(3)] for n in ns]); r = np.sqrt((a**2).mean(0)); out.append((g, r))
    return '; '.join(f'{g} (x {r[0]:.2f} y {r[1]:.2f} z {r[2]:.2f})' for g, r in out)


def parity(F, v):
    """symmetric (wing flap-like, y-even uz) or antisymmetric, from the spar centre line."""
    idx = F._idx
    a = v[6*idx['s+0.150']+2]; b = v[6*idx['s-0.150']+2]; ay = v[6*idx['s+0.150']+0]; by = v[6*idx['s-0.150']+0]
    if max(abs(a), abs(b)) > 0.05: return 'symmetric in y (uz even)' if a*b > 0 else 'antisymmetric in y (uz odd)'
    return 'symmetric in y (ux even)' if ay*by > 0 else 'antisymmetric in y (ux odd)'


if __name__ == '__main__':
    print('# T-085 D-185 re-judgement (FEA-lite beam FE with the T-085 options). Band %.0f-%.0f Hz, strong = cx or cy >= 0.5 (unchanged).' % BAND)
    print('Pack geometry from the CAD: pack CG x %.4f z %.4f m; plate solid fraction %.3f (windows %.1f %%); collar top x %.4f..%.4f, pad / collar overlap %.1f mm x %.0f mm = %.0f mm2 (centre x %.4f)' % (XP, ZP, SOL, 100*(1-SOL), X_C0, X_C1, OV*1e3, 2*m.COL_HY*1e3, COLLAR_A*1e6, COLLAR_X))
    # ---------------- 0. validation
    print('\n## 0. Validation')
    print('| check | result | expected |'); print('|---|---|---|')
    out = []
    for kind in KINDS:
        F, res = solve(kind, 'nominal'); st = [s for s in strong(res) if 60 < s[0] < 200]; out.append(max(s[0] for s in st) if st else float('nan'))
    print('| default build + cell, governing mode kd / nom / hi (T-084 s2.4) | %s | 84.6 / 88.0 / 96.2 |' % ' / '.join('%.1f' % x for x in out))
    out = []
    for kind in KINDS:
        F, res = solve(kind, 'nominal', pack='rigid'); st = [s for s in strong(res) if 60 < s[0] < 200]; out.append(max(s[0] for s in st) if st else float('nan'))
    print('| pack rigid at drawn x (pack_cfg rigid) + cell, nominal (t084_pack_place) | %s | 94.0 / 97.9 / 106.6 |' % ' / '.join('%.1f' % x for x in out))
    F, res = solve('nom', 'spar'); inb = summary(res)[0]
    print('| default build, spar-only, nom, strong in band (T-066 / T-084 s2.4) | %s | 215.3 Hz (0.02 / 0.52) |' % ('; '.join('%.1f (%.2f / %.2f)' % (f, cx, cy) for f, cx, cy, e, v in inb) or 'none'))
    for mat in HUB:
        K = HUB[mat]['K']; w = np.linalg.eigvalsh(K); sym = np.abs(HUB[mat]['Fl']-HUB[mat]['Fl'].T).max()/np.abs(HUB[mat]['Fl']).max()
        print(f'| superelement {mat}: Fl symmetry error, K rigid-body null space (6 smallest |eig| / largest), K min eig | {sym:.1e}; {np.sort(np.abs(w))[:6].max()/np.abs(w).max():.1e}; {w.min()/np.abs(w).max():.1e} | 0 / ~1e-12 / >= -1e-9 |')
    # ---------------- 1. hub joint
    print('\n## 1. Hub joint from the hub FEA (re-solved flexibility of the existing D-209 mesh, t085_hubflex.py)')
    from fe_a import E_CF
    Ea = E_CF['nom']; Ia = math.pi/64*(0.012**4-0.010**4)
    print('Cantilever of the 60 mm stub (12x10 CF, E 70 GPa): %.2e mm/N at the tip.' % (60.0**3/(3*Ea*1e-6*Ia*1e12)*1e0 if False else (0.06**3/(3*Ea*Ia))*1e3))
    for mat in HUB:
        Fl = HUB[mat]['Fl']; print(f'{mat}: UR stub-end translation flexibility (mm/N) x {Fl[0,0]:.3e}, y {Fl[1,1]:.3e}, z {Fl[2,2]:.3e}; rotation about x (rad per N mm) {Fl[3,3]:.3e}, y {Fl[4,4]:.3e}, z {Fl[5,5]:.3e}; hub centre: x {Fl[24,24]:.3e} y {Fl[25,25]:.3e} z {Fl[26,26]:.3e} mm/N')
    # ---------------- 2. bounds
    print('\n## 2. Strong modes vs the band: modelling bounds x corners x wing cell')
    print('Hub: rigid = T-084; al6061 = hub FEA with a 6061 hub (D-209 geometry, tie-bonded); petg = hub FEA as run (PETG block: soft bound).  Pack: lump = T-084 default (on the hub node); rigid = at the drawn x on the hub; tray stiff / nom / soft = pack on the tray CGE-008 with pad E 4 / 2 / 0.5 MPa (EST, unknown "—") and plate width 112 / 24 / 24 mm.')
    print('| wing cell | hub | pack | corner | strong modes IN the band (f, cx / cy) | highest strong below (Hz, margin to %.0f) | lowest strong above (Hz, margin to %.0f) | strongest 120-330 Hz mode (f, max c) | D-185 (a) |' % BAND)
    print('|---|---|---|---|---|---|---|---|---|')
    ALL = {}
    combos = [('nominal', 'rigid', 'lump'), ('nominal', 'rigid', 'rigid'), ('nominal', 'rigid', 'rigid+rot')]
    for pk in ('tray stiff', 'tray nom', 'tray soft'): combos.append(('nominal', 'rigid', pk))
    for hb in HUB:
        for pk in ('lump', 'rigid+rot', 'tray stiff', 'tray nom', 'tray soft'): combos.append(('nominal', hb, pk))
    for hb in HUB:
        for pk in ('lump', 'rigid+rot', 'tray nom', 'tray soft'): combos.append(('lower', hb, pk))
    for pk in ('lump', 'rigid+rot', 'tray nom'): combos.append(('lower', 'rigid', pk))
    for (model, hb, pk) in combos:
        for kind in KINDS:
            F, res = solve(kind, model, hb, pk); inb, lo, hi, trk = summary(res); ALL[(model, hb, pk, kind)] = (inb, lo, hi, trk, res, F)
            print(f"| {model} | {hb} | {pk} | {kind} | {'; '.join(f'{f:.1f} ({cx:.2f} / {cy:.2f})' for f, cx, cy, e, v in inb) or 'none'} | {lo:.1f} ({100*(BAND[0]/lo-1) if lo else float('nan'):+.0f} %) | {hi:.1f} ({100*(hi/BAND[1]-1):+.0f} %) | {trk[1]:.1f} ({trk[0]:.2f}) | {'FAIL' if inb else 'PASS'} |", flush=True)
    # ---------------- 3. strong modes and shapes
    print('\n## 3. Every strong mode (cx or cy >= 0.5) between 60 and 400 Hz, with shape')
    for key in [('nominal', 'rigid', 'rigid+rot'), ('nominal', 'al6061', 'tray nom'), ('nominal', 'al6061', 'rigid+rot'), ('nominal', 'petg', 'tray soft'), ('lower', 'petg', 'tray soft'), ('nominal', 'al6061', 'tray soft')]:
        if key[1] != 'rigid' and key[1] not in HUB: continue
        for kind in KINDS:
            inb, lo, hi, trk, res, F = ALL[key + (kind,)]
            rows = [(f, cx, cy, e, v) for (f, e, v, cx, cy) in res if (cx >= 0.5 or cy >= 0.5) and 60 <= f <= 400]
            print(f'\n### {key[0]} cell / hub {key[1]} / pack {key[2]} / {kind}: {len(rows)} strong mode(s)' + ('' if rows else ' (none)'))
            for f, cx, cy, e, v in rows:
                print(f'- {f:.1f} Hz{" IN BAND" if BAND[0] <= f <= BAND[1] else ""}: cx {cx:.2f} cy {cy:.2f}; {parity(F, v)}; strain energy {top(e, 4)}; rms translations {shape(F, v)}')
            near = [(f, cx, cy) for (f, e, v, cx, cy) in res if 0.3 <= max(cx, cy) < 0.5 and 60 <= f <= 400]
            if near: print('- below the 0.5 rule (0.3-0.5) in 60-400 Hz: ' + '; '.join(f'{f:.0f} Hz (cx {cx:.2f} / cy {cy:.2f})' for f, cx, cy in near))
    # ---------------- 4. option sketches (D-233 C; not applied to the CAD; no mass / CG / BOM change counted)
    print('\n## 4. Design-option sketches on the credible model (nominal cell, hub al6061, pack tray nom; and pack rigid+rot): strong modes in the band')
    print('| option | corner | strong modes IN band (f, cx / cy) | highest strong below | lowest strong above | D-185 (a) |'); print('|---|---|---|---|---|---|')
    OPT = [('as drawn', 'tray nom', {}), ('C1 bridge z-bending EI x0.5, torsion unchanged', 'tray nom', dict(bridge_f=(0.5, 1.0, 1.0))), ('C1 bridge z-bending EI x0.25, torsion unchanged', 'tray nom', dict(bridge_f=(0.25, 1.0, 1.0))),
           ('C2 pack and tray carried by the wing centre node (pack CG unchanged)', 'tray nom spar', {}), ('C2 as above, pack rigid on the carrier', 'rigid+rot spar', {}),
           ('C1 x0.5 + C2', 'tray nom spar', dict(bridge_f=(0.5, 1.0, 1.0)))]
    for lab, pk, ov in OPT:
        for kind in KINDS:
            F, res = solve(kind, 'nominal', 'al6061' if 'al6061' in HUB else 'rigid', pk, **ov); inb, lo, hi, trk = summary(res)
            print(f"| {lab} | {kind} | {'; '.join(f'{f:.1f} ({cx:.2f} / {cy:.2f})' for f, cx, cy, e, v in inb) or 'none'} | {lo:.1f} | {hi:.1f} | {'FAIL' if inb else 'PASS'} |", flush=True)
    json.dump({'|'.join(k): dict(inband=[(float(f), float(cx), float(cy)) for f, cx, cy, e, v in x[0]], below=float(x[1]), above=float(x[2])) for k, x in ALL.items()}, open(os.path.join(HERE, 'modes_t085.json'), 'w'), indent=1)
