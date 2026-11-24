"""T-077 p8: spanwise wing-cell torque envelope between the centre bulkheads (|y| 60) and the fin node (|y| 370), to decide where the skin needs 3 plies and where 2 suffice.
Category: rigid-body dynamics (the p6 demand, not re-run: foot forces, a_cg, alpha per time step) + d'Alembert cut wrench on the p6 point-mass model (demand_p6.json 'pts',
the same model and CG shift as t077p6_demand.split3). Hand calculation, no FEA.
T(y_s) = |My| about the spar axis (worse of x = SPAR_X and mid-chord, as landing_path_a.wing_checks_skin) of the wrench that the inboard wing exerts on the outboard free body
(fin feet + every non-hub point mass with y beyond y_s): W_cut = sum m a - F_feet.  Hub group idx 2, 3, 4, 6 (motors, arms, hub, pack) is excluded: it hangs on the bridge, not the cell.
    python -I t077p8_span_torque.py   -> span_torque.json / stdout"""
import os, sys, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P6 = os.path.join(HERE, '..', 'T077p6_data')
DEM = json.load(open(os.path.join(P6, 'demand_p6.json'))); Z = np.load(os.path.join(P6, 'fea', 'demand_p6.npz'), allow_pickle=True)
NAMES = [str(n) for n in Z['names']]
pts = np.array([p[:4] for p in DEM['pts']]); idx = np.array([p[4] for p in DEM['pts']])
m = pts[:, 0]; pos = pts[:, 1:4]; cg = np.array(DEM['cg'])
cgp = (m[:, None] * pos).sum(0) / m.sum(); pos = pos + (cg - cgp)                 # same CG shift as split3 (model translated so its CG sits at the CAD CG)
xf, zf, yf = DEM['xf'], DEM['zf'], 0.38
feet = np.array([[xf, sy * yf, sz * zf] for sy in (1, -1) for sz in (1, -1)])
SX, CH = 0.060, 0.245
wing = ~np.isin(idx, (2, 3, 4, 6))
YS = (0.060, 0.080, 0.100, 0.125, 0.150, 0.175, 0.200, 0.250, 0.300, 0.350, 0.370)
env = {y: 0.0 for y in YS}; arg = {}
for zeta in (0.02, 0.05, 0.10):
    for mu in (0.40, 0.30):
        for nm in NAMES:
            key = '%.2f|%.2f|%s' % (zeta, mu, nm)
            FB = Z[key + '|FB'].astype(float); a = Z[key + '|a_cg'].astype(float); al = Z[key + '|alpha'].astype(float)
            for side, sg in (('R', 1), ('L', -1)):
                kf = (0, 1) if sg > 0 else (2, 3)
                for ys in YS:
                    sel = wing & (sg * pos[:, 1] > ys)
                    best = 0.0
                    for xr in (SX, 0.5 * CH):
                        S = np.array([xr, sg * ys, 0.0])
                        My = np.zeros(len(a))
                        for mi, pi in zip(m[sel], pos[sel]):
                            rho = pi - cg; f = mi * (a + np.cross(al, np.broadcast_to(rho, al.shape))); r = pi - S
                            My += r[2] * f[:, 0] - r[0] * f[:, 2]
                        for j in kf:
                            r = feet[j] - S; f = FB[:, j, :]
                            My -= r[2] * f[:, 0] - r[0] * f[:, 2]
                        best = max(best, float(np.abs(My).max()))
                    if best > env[ys]: env[ys] = best; arg[ys] = '%s %s' % (key, side)
print('| station |y| m | max cell torque N m (RB) | case |\n|---|---|---|')
for ys in YS: print('| %.3f | %.2f | %s |' % (ys, env[ys], arg[ys]))
json.dump(dict(env={str(k): v for k, v in env.items()}, arg={str(k): v for k, v in arg.items()}), open(os.path.join(HERE, 'span_torque.json'), 'w'), indent=1)
