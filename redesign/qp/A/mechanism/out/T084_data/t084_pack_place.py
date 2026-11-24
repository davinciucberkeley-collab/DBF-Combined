"""T-084 (FEA-lite, beam FE): sensitivity of the strong modes to the pack lump placement. The FE puts the pack (+ tray, straps, pad: pack_g) on the hub node;
here it sits at its drawn x (common.PACK_X centre) and z (tray top 8 mm + half the 46 mm pack height, EST), joined rigidly to the hub (the tray CGE-008 is cantilevered from the hub flange).
python -I t084_pack_place.py > pack_place.txt"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.dont_write_bytecode = True
from t084_modes_final import fe_a, fekw, BAND, CP, strong, m
import numpy as np
for model in ('spar', 'nominal', 'lower'):
  for kind in ('kd','nom','hi'):
    cell = None if model=='spar' else CP.cell_for(kind, lower=(model=='lower'))
    kw = fekw(wing_cell=cell); pk = kw['pack_g']; kw['pack_g'] = 0.0
    F, info = fe_a.build(kind, **kw)
    xp = (m.PACK_X[0]+m.PACK_X[1])/2
    F.node('pack', (xp, 0, 0.008+0.023)); F.beam('hub', 'pack', 1e9, 1e5, 1e5, 1e5, 0.0, (0,0,1), 'tray', nseg=1); F.lump('pack', pk*1e-3)
    res = F.solve(130); st = [(round(f,1), round(cx,2), round(cy,2)) for f,cx,cy,e in strong(res) if 60 < f < 330]
    print(model, kind, 'pack at x %.3f rigid to hub:' % xp, st)
