"""T-085 s4: every strong mode in and near the band (60-400 Hz) with shape and strain-energy split, defaults check.  python -I t085_detail.py > detail_t085.txt"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.dont_write_bytecode = True
import t085_bounds as B
T = B.T; BAND = T.BAND
for k, v in B.CASES.items(): T.PACKS[k] = v
print('## defaults check (no T-085 option), expected T-066 / T-084')
for kind in T.KINDS:
    F, res = T.solve(kind, 'spar'); inb = T.summary(res)[0]; print('spar-only', kind, [(round(f, 1), round(cx, 2), round(cy, 2)) for f, cx, cy, e, v in inb], '(T-084 s2.4: 201.0 / 215.3 / 244.2, cx 0.02, cy 0.52)')
for kind in T.KINDS:
    F, res = T.solve(kind, 'nominal'); inb = T.summary(res)[0]; st = [s for s in T.strong(res) if 60 < s[0] < 200]
    print('cell nominal', kind, 'governing', round(max(s[0] for s in st), 1), 'in band', [(round(f, 1), round(cx, 2), round(cy, 2)) for f, cx, cy, e, v in inb], '(T-084: 84.6 / 88.0 / 96.2)')
SEL = [('nominal', 'al6061', 'pad soft (30A, E 1.142, Ec=E), tray 24'), ('nominal', 'al6061', [k for k in B.CASES if k.startswith('pad nom (50A') and 'K' not in k][0]),
       ('nominal', 'al6061', [k for k in B.CASES if k.startswith('pad stiff (70A') and 'tray 112' in k][0]), ('lower', 'al6061', [k for k in B.CASES if k.startswith('pad nom (50A') and 'K' not in k][0]),
       ('nominal', 'petg', [k for k in B.CASES if k.startswith('pad nom (50A') and 'K' not in k][0]), ('lower', 'petg', [k for k in B.CASES if k.startswith('pad stiff (70A') and 'tray 112' in k][0])]
for cell, hub, pk in SEL:
    for kind in T.KINDS:
        F, res = T.solve(kind, cell, hub, pk); rows = [(f, cx, cy, e, v) for (f, e, v, cx, cy) in res if (cx >= 0.5 or cy >= 0.5) and 60 <= f <= 400]
        print(f'\n### {cell} cell / hub {hub} / {pk} / {kind}: {len(rows)} strong mode(s)')
        for f, cx, cy, e, v in rows:
            print(f'- {f:.1f} Hz{" IN BAND" if BAND[0] <= f <= BAND[1] else ""}: cx {cx:.2f} cy {cy:.2f}; {T.parity(F, v)}; strain energy {T.top(e, 4)}; {T.shape(F, v)}')
        near = [(f, cx, cy) for (f, e, v, cx, cy) in res if 0.3 <= max(cx, cy) < 0.5 and 60 <= f <= 400]
        if near: print('- below the 0.5 rule (0.3-0.5): ' + '; '.join(f'{f:.0f} Hz ({cx:.2f} / {cy:.2f})' for f, cx, cy in near))
