# T-071 supplementary scans (rigid-body histories + hand calculation; analysis only). python -I t071_scans.py
import sys, math, time
sys.path.insert(0, 'C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/structures')
import numpy as np, landing_path_a as P
L = P.L; t0 = time.time(); P.set_pad(P.PAD_D2['x_foot'], P.PAD_D2['z_foot'])
FBs = []
for name, kw in P.cases(False):
    q = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, **dict(kw, **P.PAD_D2)); FBs.append((name, q['trace'].reshape(-1, 4, 3)))
def mins(sk, fs=1.0):
    m = {}
    for name, FBt in FBs:
        r, _ = P.wing_checks_skin(FBt, sk, EF=P.E_F*fs, GF=P.G_F*fs)
        for key, (lab, a) in r.items():
            f = key.split(',')[0]; v = float(a.min())
            if f not in m or v < m[f][0]: m[f] = (v, name)
    return m
print('## robustness matrix: min over stations and 23 cases (P15 rows, P16 rows)')
for n in (1, 2):
    for stiff in (1.0, 0.7):
        for fs in (1.0, 0.5):
            for Acap in (3e-6,):
                sk = dict(lam=P.skin_laminate(n=n, stiff=stiff), strip_A=Acap, relief=0.0, truss=True)
                m = mins(sk, fs); p15 = min((v[0], k) for k, v in m.items() if k.startswith('P15')); p16 = min((v[0], k) for k, v in m.items() if k.startswith('P16'))
                print(f'n={n} skin stiffness x{stiff} foam x{fs}: P15 {p15[0]:.2f} ({p15[1]})  P16 {p16[0]:.2f} ({p16[1]})  skin mass {n*0.088*0.383095*0.80*1e3:.1f} g')
print('\n## fine cap-strip scan (n=1): P16 min')
for Acap in (0.1e-6, 0.2e-6, 0.3e-6, 0.4e-6, 0.5e-6, 0.75e-6, 1e-6):
    m = mins(dict(lam=P.skin_laminate(), strip_A=Acap)); print(f'strip {Acap*1e6:.2f} mm2 ({Acap*0.8*1550*1e3:.2f} g): P16 {min(v[0] for k, v in m.items() if k.startswith("P16")):.2f}')
print('\n## strut: peak compression and Euler options (hand calc, E 70 GPa EST (iter2_margins.py), pinned-pinned, L %.4f m)' % P._strut_geom()[2])
ux, uy, Ls = P._strut_geom(); Nmax = 0
for name, FBt in FBs:
    for k in (0, 1):
        N = np.sum([FBt[:, 2*k+j, 0] for j in (0, 1)], axis=0)/ux; Nmax = max(Nmax, float(np.max(-N)))
print('peak strut compression, limit load, over 23 cases: %.1f N; x KF = %.1f N' % (Nmax, Nmax*P.KF))
rho = 1550.0
for D, d in ((6e-3, 4.5e-3), (6e-3, 4.0e-3), (7e-3, 5e-3), (8e-3, 6e-3), (8e-3, 6.5e-3)):
    I = math.pi/64*(D**4-d**4); A = math.pi/4*(D*D-d*d)
    for kl, lab in ((1.0, 'pinned'), (0.7, 'fixed-pinned (K 0.7, NOT credited)')):
        Pc = math.pi**2*P.E_S*I/(kl*Ls)**2; print(f'{D*1e3:.0f}x{d*1e3:.1f} {lab}: Pcr {Pc:.0f} N, RF {Pc/(P.KF*Nmax):.2f}; two struts {2*A*Ls*rho*1e3:.1f} g (CF 1.55 g/cm3 EST), delta vs 6x4.5 {2*(A-math.pi/4*(36-20.25)*1e-6)*Ls*rho*1e3:+.1f} g')
print('wall %.0f s' % (time.time()-t0))
