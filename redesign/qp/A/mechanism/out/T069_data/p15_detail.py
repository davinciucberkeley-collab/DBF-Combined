import sys, os, math
sys.path.insert(0, 'C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/structures')
import numpy as np, landing_path_a as P
L = P.L
q = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, v_sink=1.2, th_n=7, th_w=7)
FBt = q['trace'].reshape(-1, 4, 3)
for var in ('bored', 'solid'):
  for scale in (0.5, 1, 2):
    r, info = P.wing_checks(FBt, EF=P.E_F*scale, GF=P.G_F*scale, variant=var)
    print(var, 'foam E,G x', scale, {k: round(float(v), 4) for k, v in info.items() if k != 'foam'})
    print('   ', [(k[:3] + k.split(',')[-1][:14], round(float(v[1].min()), 3)) for k, v in r.items()])
print(info['foam'])
# torque at the station, worst
for k in (0, 1):
    for x0 in (P.SX, 0.1225):
        F, M = P.M_about(FBt, k, P.S_(k, x0, 0.0)); print('fin', k, 'x0', x0, 'max |My| %.2f max|Mx| %.2f max|Mz| %.2f' % tuple(np.abs(M).max(0)[[1, 0, 2]]))
# skin bound: torque needed from skin at RF 1
S = P.sec(); r, info = P.wing_checks(FBt)
Tmax = max(float(np.abs(P.M_about(FBt, k, P.S_(k, P.SX, 0.0))[1][:, 1]).max()) for k in (0, 1))
sh_s, sh_f = info['sh_spar'], info['sh_foam']
cap_s = P.TAU/P.KF*info['J_s']/(P.SOD/2); cap_f = P.F_SHEAR/P.KP/info['tau_unit']
print('Tmax limit', Tmax, 'cap spar alone (limit N m)', cap_s, 'cap foam alone', cap_f, 'sum', cap_s+cap_f, 'elastic-share cap', min(cap_s/sh_s, cap_f/sh_f))
Aenc = S['foam']['enclosed']; need = Tmax - min(cap_s/sh_s, cap_f/sh_f)
print('enclosed area', Aenc, 'skin torque needed (limit) from share-cap', need, 'q N/m', need/(2*Aenc))
# --- bounds that do not depend on the share model
print('\n## bounds')
worst = {}
for case, kw in P.cases():
    if case not in ('hard 7/7 combo', 'hard 10 wide + drift .5 y', 'hard 16 wide + drift .5 y', 'SITL Tb_h5 wide (y drift)'): continue
    q = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, **kw); FB = q['trace'].reshape(-1, 4, 3)
    for lab, ys in P.wing_stations():
        for x0 in (P.SX, 0.1225):
            Mz = max(float(np.abs(P.M_about(FB, k, (x0, (1 if k == 0 else -1)*ys, 0.0))[1][:, 2]).max()) for k in (0, 1))
            T = max(float(np.abs(P.M_about(FB, k, P.S_(k, x0, 0.0))[1][:, 1]).max()) for k in (0, 1))
            w = worst.setdefault(lab, [0, 0]); w[0] = max(w[0], Mz); w[1] = max(w[1], T)
Zs = P.I_S/(P.SOD/2); capz = P.SIG*Zs/P.KF
print('spar alone in-plane M cap (limit N m) %.2f ; torsion cap %.2f' % (capz, cap_s))
for lab, (Mz, T) in worst.items():
    print(f'{lab}: max Mz {Mz:.2f} N m, max T {T:.2f} N m (limit)  -> spar-alone in-plane RF {capz/Mz:.2f}, spar-alone torsion RF {cap_s/T:.2f}, spar+foam ductile-sum torsion RF {(cap_s+cap_f)/T:.2f}')
# foam extreme fiber at a point where thickness >= 3 mm (sensitivity: ignores the sharp TE tip)
Pl = P._poly(); xs = np.linspace(0, P.C.C, 2000)
up = np.interp(xs, Pl[:len(Pl)//2+1][::-1, 0], Pl[:len(Pl)//2+1][::-1, 1]) if False else None
