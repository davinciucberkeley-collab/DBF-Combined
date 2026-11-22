"""T-085 s6 extra sketch (not applied): C3 = a softer pack-to-tray mount (pad E scaled down, EST, pad thickness / foam choice is the real lever) so that the pack-on-pad modes
sit below the 94 Hz band edge, plus the reference with the pack mass removed from the cage. Credible model: nominal cell, hub al6061.   python -I t085_sketch3.py > sketch3_t085.txt"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.dont_write_bytecode = True
import t085_modes as T
print('| case | corner | strong modes IN the band (f, cx / cy) | highest strong below | lowest strong above | D-185 (a) |'); print('|---|---|---|---|---|---|')
for E in (0.25e6, 0.15e6, 0.10e6, 0.05e6):
    T.PACKS['c3'] = dict(T.PACKS['tray nom'], pad_E=E)
    for kind in T.KINDS:
        F, res = T.solve(kind, 'nominal', 'al6061', 'c3'); inb, lo, hi, trk = T.summary(res)
        lowm = sorted([(round(float(f), 1), round(float(cx), 2), round(float(cy), 2)) for f, cx, cy, e, v in T.strong(res) if 30 < f < 94])
        print(f"| C3 pad E {E/1e6:.2f} MPa (EST; 2 MPa drawn-nominal) | {kind} | {'; '.join(f'{f:.1f} ({cx:.2f} / {cy:.2f})' for f, cx, cy, e, v in inb) or 'none'} | {lo:.1f} | {hi:.1f} | {'FAIL' if inb else 'PASS'} |", flush=True)
for kind in T.KINDS:
    F, res = T.solve(kind, 'nominal', 'al6061', 'lump', pack_g=13.3)       # tray only (13.3 g) left on the hub node: the pack mass removed from the cage
    inb, lo, hi, trk = T.summary(res); st = sorted([(round(float(f), 1), round(float(cx), 2), round(float(cy), 2)) for f, cx, cy, e, v in T.strong(res) if 30 < f < 400])
    print(f"| reference: pack mass removed from the cage (13.3 g tray on the hub) | {kind} | {'; '.join(f'{f:.1f} ({cx:.2f} / {cy:.2f})' for f, cx, cy, e, v in inb) or 'none'} | {lo:.1f} | {hi:.1f} | {'FAIL' if inb else 'PASS'} |", flush=True)
