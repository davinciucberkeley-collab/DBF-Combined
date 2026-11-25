"""T-085 (FEA-lite beam FE, fe_a.py): D-185 (a) at kd / nom / hi for the credible bounds of every EST stiffness (pack pad PWR-003, tray CGE-008, hub joint, wing cell).
Band 94-321 Hz and coupling >= 0.5 unchanged.   python -I t085_bounds.py > bounds_t085.txt
Pad basis (T085_report s3.1): PWR-003 silicone sheet 100 x 30 x 1.0 mm (CAD; hardness '—').  Young's modulus from Gent's relation (Shore 30 / 50 / 70 A -> 1.142 / 2.456 / 5.520 MPa).
Compression of a thin pad: Ec_inc = E (1 + 2 S^2), S = loaded / force-free area = 3000 / 260 = 11.5; finite bulk modulus K (EST, '—', 1 GPa used, 0.25-4 GPa swept): Ec = Ec_inc K / (Ec_inc + K).
soft = unbonded slipping faces: Ec = E (no enhancement), 30 A; nominal = 50 A with enhancement, tray root 24 mm; stiff = 70 A with enhancement, full 112 mm plate."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.dont_write_bytecode = True
import t085_modes as T
from t085_modes import KINDS, BAND
S_SH = 3.0e-3/(2*(0.100+0.030)*1.0e-3)
def zmult(E, K=1.0e9, enh=True):
    if not enh: return 1.0
    ec = E*(1+2*S_SH**2); return ec*K/(ec+K)/E
def pk(E, w, enh=True, K=1.0e9, **kw):
    return dict(T.PACKS['tray nom'], pad_E=E, w=w, z_mult=zmult(E, K, enh), **kw)
CASES = {
 'pad soft (30A, E 1.142, Ec=E), tray 24': pk(1.142e6, 0.024, enh=False),
 'pad nom (50A, E 2.456, zm %.0f), tray 24' % zmult(2.456e6): pk(2.456e6, 0.024),
 'pad stiff (70A, E 5.52, zm %.0f), tray 112' % zmult(5.52e6): pk(5.52e6, 0.112),
 'pad stiff (70A, E 5.52, zm %.0f), tray 24' % zmult(5.52e6): pk(5.52e6, 0.024),
 'pad nom, K 0.25 GPa (zm %.0f), tray 24' % zmult(2.456e6, 0.25e9): pk(2.456e6, 0.024, K=0.25e9),
}
def strongrows(res, lo=60, hi=400): return [(f, cx, cy, e, v) for (f, e, v, cx, cy) in res if (cx >= 0.5 or cy >= 0.5) and lo <= f <= hi]
def fmt(rows, F):
    return '; '.join(f"{f:.1f}{'*' if BAND[0] <= f <= BAND[1] else ''} ({cx:.2f}/{cy:.2f})" for f, cx, cy, e, v in rows) or 'none'
if __name__ == '__main__':
    for k, v in CASES.items(): T.PACKS[k] = v
    T.PACKS['rigid+rot'] = T.PACKS['rigid+rot']
    print('S = %.2f; zmult 30A %.0f 50A %.0f 70A %.0f (K 1 GPa)' % (S_SH, zmult(1.142e6), zmult(2.456e6), zmult(5.52e6)))
    print('| cell | hub | pad / tray case | corner | strong modes 60-400 Hz (f Hz, * = in band 94-321; cx / cy) | D-185 (a) |'); print('|---|---|---|---|---|---|')
    names = list(CASES) + ['rigid+rot']
    for cell in ('nominal', 'lower'):
        for hub in ('al6061', 'petg'):
            for nm in names:
                for kind in KINDS:
                    F, res = T.solve(kind, cell, hub, nm); rows = strongrows(res); inb = [r for r in rows if BAND[0] <= r[0] <= BAND[1]]
                    lab = nm if nm != 'rigid+rot' else 'pack rigid on hub (limit, no pad)'
                    print(f"| {cell} | {hub} | {lab} | {kind} | {fmt(rows, F)} | {'FAIL' if inb else 'PASS'} |", flush=True)
