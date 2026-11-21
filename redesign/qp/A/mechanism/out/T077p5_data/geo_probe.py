"""T-077 p5 geometry probe (no solve): build the hub FEA mesh coarse (MS 2.0) for given fillet radii and print hub volume / mass. python -I geo_probe.py SH_R MO_R"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); T76 = os.path.abspath(os.path.join(HERE, '..', 'T076_data')); T76C = os.path.abspath(os.path.join(HERE, '..', 'T076c_data')); S_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures'))
sys.path.insert(0, HERE); sys.path.insert(0, T76C); sys.path.insert(0, T76); sys.path.insert(0, S_DIR); sys.dont_write_bytecode = True
os.environ['LAND_MASS_KG'] = '1.64'
import numpy as np, fea_hub_e as H
BASE = dict(S_END=60.0, SLV_W=1.5, MS=2.0, FIL=2.0, BR_CH=0.8, COL_E=21.0, X_BR0=15.0, X_HUB1=45.0, BR_GAP=0.5)
G1 = dict(DBL_S1=40.0, DBL_TAP=5.0, DBL_TIP=0.4, SLV_CH=1.5, L_SLV=32.0)
H.GEO.update(BASE); H.GEO['BLK_AFT'] = 10.0; H.GEO.update(G1); H.GEO.update(RC_R=9.25, RC_X0=15.5, SH_R=float(sys.argv[1]), MO_R=float(sys.argv[2]), SH_FMS=0.0, MO_FMS=0.0)
p = os.path.join(HERE, 'fea', 'probe_%s_%s.npz' % (sys.argv[1], sys.argv[2])); H.build_mesh(0, p)
d = np.load(p); print('SH_R %s MO_R %s: hub %.1f mm3 = %.2f g Al, nodes %d, tets %d' % (sys.argv[1], sys.argv[2], float(d['hub_vol']), float(d['hub_vol']) * 2.7e-3, len(d['X']), len(d['E'])))
