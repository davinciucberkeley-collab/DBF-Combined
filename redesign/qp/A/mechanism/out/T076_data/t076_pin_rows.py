"""T-076 row 2: pin fix rows at the landing mass.  Category: rigid-body dynamics (landing_a traces, 23 cases, D2 pad, mu 0.30, 1.64 kg via LAND_MASS_KG) + hand calculation.
Rows: root block / saddle socket pins from landing_nodes_b.pin_option_rows (3 x 3 mm in a 4 mm wall; 2 x 3 in 2.5 mm as the as-drawn reference),
and the clamshell cradle pins (CS5 / CS5b with 3 pins and a 4 mm boss wall instead of 2 pins in 2 mm).   python -I t076_pin_rows.py"""
import sys, os
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'structures')); sys.path.insert(0, S)
import numpy as np
import landing_path_a as P
import landing_nodes_b as N
L = P.L
P.set_pad(P.PAD_D2['x_foot'], P.PAD_D2['z_foot'])
FBs = [(n, L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, mu=0.30, **dict(kw, **P.PAD_D2))['trace'].reshape(-1, 4, 3)) for n, kw in P.cases(False)]
print('mass %.3f kg, 23 cases, KP %.3f' % (L.M_GATE, P.KP))
def mn(f):
    r = {}
    for name, FBt in FBs:
        for k, a in f(FBt).items():
            if k not in r or a.min() < r[k][0]: r[k] = (float(a.min()), name)
    return r
print('| Row | min RF | governing case |\n|---|---|---|')
for n, wall in ((1, 0.0025), (2, 0.0025), (3, 0.004)):
    for k, (v, nm) in sorted(mn(lambda F: N.pin_option_rows(F, n, wall)).items()): print('| %s | %.2f | %s |' % (k, v, nm))
# cradle (clamshell): torque Mx at the crossing shared by n pins; bearing wall 2 mm (as drawn, 2 pins) vs 4 mm boss with 3 pins
def cradle(FBt, n, wall):
    out = {}
    for k in (0, 1):
        F, M = P.M_about(FBt, k, P.S_(k, P.SX, 0.0)); V = np.abs(M[:, 0]) / P.ROD / n
        out['CRADLE %d x 3 mm CF pins, double shear' % n] = P.PIN_TAU / np.maximum(V / (2 * P.PIN_A) * P.KP, 1e-9)
        out['CRADLE %d pins, bearing in %.0f mm PETG wall' % (n, wall * 1e3)] = P.PETG_BEAR / np.maximum(V / (P.PIN_D * wall) * P.KP, 1e-9)
    return {kk: np.minimum.reduce([out[kk]]) for kk in out}
for n, wall in ((2, 0.002), (3, 0.004)):
    for k, (v, nm) in sorted(mn(lambda F: cradle(F, n, wall)).items()): print('| %s | %.2f | %s |' % (k, v, nm))
