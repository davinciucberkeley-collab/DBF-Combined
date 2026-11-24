"""T-085 s6 extra: combined stiffness-reduction levers (not applied).  python -I t085_levers2.py > levers2_t085.txt"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.dont_write_bytecode = True
import t085_levers as L
T = L.T
T.PACKS['base'] = L.B.CASES[[k for k in L.B.CASES if k.startswith('pad nom (50A') and 'K' not in k][0]]
OPT = [('C5 arms 10x8 + C1 bridge z x0.25', dict(arm_tube=(0.010, 0.008), bridge_f=(0.25, 1, 1))),
       ('C5 arms 10x8 + C1 x0.25 + C2 pack on centre node', dict(arm_tube=(0.010, 0.008), bridge_f=(0.25, 1, 1), _spar=1)),
       ('C5b arms 9x7', dict(arm_tube=(0.009, 0.007))),
       ('C5b arms 9x7 + C1 x0.25', dict(arm_tube=(0.009, 0.007), bridge_f=(0.25, 1, 1)))]
T.PACKS['base spar'] = dict(T.PACKS['base'], anchor='s+0.000')
print('| option | cell | corner | strong modes 60-400 Hz (* in band; A / B coupling) | D-185 (a) |'); print('|---|---|---|---|---|')
for lab, ov in OPT:
    pk = 'base'
    if ov.pop('_spar', 0): pk = 'base spar'
    for cell in ('nominal', 'lower'):
        for kind in T.KINDS:
            F, res, rows = L.run(kind, cell, pk, **ov); print(f'| {lab} | {cell} | {kind} | {L.fmt(rows)} | {L.verdict(rows)} |', flush=True)
