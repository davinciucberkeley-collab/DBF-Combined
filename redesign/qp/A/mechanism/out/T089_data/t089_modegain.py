"""T-089 support: pitch / roll / yaw modal gain (relative to the rigid gain) of the strong modes 20-130 Hz at the spar centre, base group (nominal cell, 6061 hub, 50 A pad, tray 24), kd / nom / hi.
Category: FEA-lite modal data.  python -I t089_modegain.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); QPA = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'T085_data')); sys.path.insert(0, os.path.join(HERE, '..', 'T084_data'))
sys.path.insert(0, os.path.join(QPA, 'sitl')); sys.path.insert(0, os.path.join(QPA, 'structures')); sys.dont_write_bytecode = True
import warnings; warnings.filterwarnings('ignore')
import t089_gm as G, fu_cage as FC
FC.configure('t089'); T, GR = G.groups()
base = [g for g in GR if g[0] == 'nominal' and g[1] == 'al6061' and g[2].startswith('pad nom (50A') and 'K 0.25' not in g[2]][0]
for kind in G.KINDS:
    F, res = T.solve(kind, *base)
    for c in FC.cases_frame(F, kind):
        if c['node'] != 'spar centre': continue
        print(kind, c['ax'], [(round(ff, 1), round(gg / c['inv_I'], 3)) for ff, gg in c['flex'] if 20 < ff < 130 and abs(gg / c['inv_I']) > 0.01])
