"""T-077 p6 step 2: R2 bosses (AVN-010) strength / mount rows on the D-223 landing demand.  Category: rigid-body dynamics (peak a_cg from t077p6_demand.py) + HAND CALCULATION (as T-073 R2).
    python -I t077p6_bosses.py > bosses_p6_stdout.txt
Rows: (1) mount frequency vs 304 Hz (T-073 R2 method: foam-limited rigid square punch, E 30 MPa, G 8 MPa, nu 0.2 EST); (2) landing: board inertial load n_peak x DAF acts along body x (the stance direction, in the board plane),
overturning moment about the boss line on the foam under the skin (foam compression 103 kPa, Owens Corning FOAMULAR 150 data sheet via foam_103.py), bond peel of the boss base (epoxy 2.0 MPa EST), M2 screw shear.  KP 2.156 on printed / bonded rows, KF 1.725 on the steel screw."""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(A, 'cad')); sys.dont_write_bytecode = True
import numpy as np
from amodel import common as C
KF, KP = 1.725, 2.156
Z = np.load(os.path.join(HERE, 'fea', 'demand_p6.npz'), allow_pickle=True)
npk = max(float(np.linalg.norm(Z[k].astype(float), axis=1).max()) for k in Z.files if k.endswith('|a_cg')) / 9.81
print('peak rigid-body |a_cg| over 23 cases x zeta x mu: %.2f g (t077p6_demand.py)' % npk)
FOAM_COMP, BOND, STEEL = 103e3, 2.0e6, 450e6
Ez, Gz, nu = 30e6, 8e6, 0.2
a = 3e-3                                           # half side of the 6 mm square (equivalent circle radius 6/sqrt(pi) mm)
r_eq = 6e-3 / math.sqrt(math.pi); kz = 4 * Gz * r_eq / (1 - nu); kh = 8 * Gz * r_eq / (2 - nu) * 1.0   # vertical / horizontal stiffness of a rigid punch on a half-space (Gz = shear modulus): EST
print('foam punch per boss: kz %.3f MN/m, kh %.3f MN/m (T-073: 0.21 / 0.12 with its own constants)' % (kz / 1e6, kh / 1e6))
kz_T, kh_T = 0.21e6, 0.12e6                         # T-073 R2 values used for the frequency (kept: same method, same numbers)
rows = []
boards = [('FC Kakute H743-Wing 28 g, 4 bosses 6x6 on the 25 x 25 pattern, x 34.5 / 59.5', 0.028, 4, 0.025, 'FC'),
          ('ESC SpeedyBee 4-in-1 20 g, 4 bosses 6x6 on the 20 x 20 pattern', 0.020, 4, 0.020, 'ESC')]
for nm, m, nb, arm, tag in boards:
    f_z = math.sqrt(nb * kz_T / m) / (2 * math.pi); f_h = math.sqrt(nb * kh_T / m) / (2 * math.pi)
    rows.append((nm, 'mount f_z %.0f Hz / f_horizontal %.0f Hz vs 304 Hz (A-P10(a) 1.2 x top 2P band)' % (f_z, f_h), min(f_z, f_h) / 304.0, 'EST'))
    for dafn, daf in (('RB x1.5', 1.5), ('x1.97', 1.97), ('x2.23', 2.23)):
        n = npk * daf; F = m * n * 9.81
        zc = {'FC': 0.003 + 0.0008 + 0.0, 'ESC': 0.003 + 0.0028}[tag]          # board centroid above the boss tops: 3.0 mm tape + half the PCB (FC 1.6 mm) / half the 5.5 mm ESC stack
        hb = {'FC': (C.ZP - C.zu(0.0345)), 'ESC': (C.ZP - C.zu(0.080))}[tag]    # boss height at the front boss (skin follows the airfoil)
        M = F * (zc + hb * 0.0 + 0.0)                                           # moment about the boss-top plane (boss shear carries F at the base: lever to the base adds the boss height)
        M_base = F * (zc + hb)
        dN = M_base / arm / (nb / 2)                                            # extra compressive / tensile force per boss of the loaded pair
        sig_foam = dN / (6e-3 * 6e-3) * KP; sig_peel = dN / (6e-3 * 6e-3) * KP
        rows.append((nm, 'landing %s (n %.1f g, F %.1f N along x, lever %.1f mm): foam bearing under one boss (dN %.2f N, 6 x 6 mm punch, no skin spreading)' % (dafn, n, F, (zc + hb) * 1e3, dN), FOAM_COMP / sig_foam, 'EST foam 103 kPa'))
        rows.append((nm, 'landing %s: boss base bond peel / tension (epoxy 2.0 MPa)' % dafn, BOND / sig_peel, 'EST'))
        rows.append((nm, 'landing %s: M2 screw shear (FC: 4 screws; ESC held by tape + tie: not a screw row)' % dafn, (0.6 * STEEL) / (F / 4 * KF / 3.39e-6) if tag == 'FC' else float('nan'), 'EST'))
print('| board | row | RF | basis |\n|---|---|---|---|')
for r in rows: print('| %s | %s | %s | %s |' % (r[0][:48], r[1], '%.2f' % r[2] if r[2] == r[2] else '-', r[3]))
json.dump([dict(board=r[0], row=r[1], rf=(None if r[2] != r[2] else r[2])) for r in rows], open(os.path.join(HERE, 'bosses_p6.json'), 'w'), indent=1)
