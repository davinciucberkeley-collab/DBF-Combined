# T-071 Phase 1 step 2 (D-216 s7 step 2, F-4): bridge bending at 2T, CGE-006 centre node, hub bridge bore.  Rigid-body histories (23 cases, D2 pad) + HAND CALCULATION. python -I step2.py
import sys, math, time
sys.path.insert(0, 'C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/structures')
import numpy as np, landing_path_a as P
L, W, C = P.L, P.W, P.C; t0 = time.time(); P.set_pad(P.PAD_D2['x_foot'], P.PAD_D2['z_foot'])
KF, KP = P.KF, P.KP
BR_OD, BR_ID = W.BR_OD, W.BR_ID; Zb = math.pi/64*(BR_OD**4-BR_ID**4)/(BR_OD/2)
L_SOCK = 0.0535-0.030                       # CGE-006 saddle bridge socket, wing.py box x 0.030..0.0535
L_BORE = W.HUB_X1-W.BORE_X0                 # hub bridge bore depth, wing.py: aft face -0.045 minus floor (HUB x -0.069 + 0.015)
HUB_SHARE = 0.37                            # T-070 s3.1: hub-side (motors + hub) share of Iyy, EST; NOT credited in the gate column
Mmax = {}; M2 = 0.0; Msum = 0.0; Tskin_frac = 0.89025   # skin share of the torque, V0 (skin_run.txt)
for name, kw in P.cases(False):
    FBt = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, **dict(kw, **P.PAD_D2))['trace'].reshape(-1, 4, 3)
    my = [P.M_about(FBt, k, P.S_(k, P.SX, 0.0))[1][:, 1] for k in (0, 1)]
    Msum = max(Msum, float(np.abs(my[0]+my[1]).max())); M2 = max(M2, 2*max(float(np.abs(my[0]).max()), float(np.abs(my[1]).max())))
    Mmax[name] = float(np.abs(my[0]+my[1]).max())
w = max(Mmax, key=Mmax.get)
print('limit-load pitch moment into the bridge (|My_fin0 + My_fin1| about the span axis): max over 23 cases %.2f N m (%s); bound 2 x max single fin %.2f N m' % (Msum, w, M2))
rows = []
for lab, M in (('2T (bound, 2 x single-fin max)', M2), ('sum of both fins at the same instant', Msum)):
    s = KF*M/Zb; rows.append((f'Bridge tube 16x14 bending, {lab}: Z {Zb*1e9:.0f} mm3, sigma x KF {s/1e6:.0f} MPa vs 350 EST', 350e6/s))
    sb = 6*M/(BR_OD*L_SOCK**2); rows.append((f'CGE-006 saddle socket bearing, PETG 20 MPa EST, {lab}: L {L_SOCK*1e3:.1f} mm, 6M/(D L^2) x KP {sb*KP/1e6:.1f} MPa', 20e6/(sb*KP)))
    sh = 6*M/(BR_OD*L_BORE**2); rows.append((f'HUB bridge bore bearing, PETG 20 MPa EST, {lab}: L {L_BORE*1e3:.1f} mm, 6M/(D L^2) x KP {sh*KP/1e6:.1f} MPa', 20e6/(sh*KP)))
    Lreq = math.sqrt(6*M*KP/(BR_OD*20e6)); rows.append((f'  bore depth needed for RF 1 ({lab})', Lreq*1e3))
    Msh = M*HUB_SHARE; sh2 = 6*Msh/(BR_OD*L_BORE**2); rows.append((f'HUB bore bearing with hub-side inertia share {HUB_SHARE:.2f} (EST, T-070 s3.1), {lab}: {sh2*KP/1e6:.1f} MPa', 20e6/(sh2*KP)))
# skin torque into the two centre bulkhead plates: each plate takes one wing's skin torque
Tsk = Tskin_frac*max(Mmax.values())/2*1.0   # per-side skin torque from the single-fin maximum is below; use single-fin max
T1 = M2/2; Tsk = Tskin_frac*T1; A = 3.3891e-3; q = Tsk/(2*A)
rows.append((f'Skin shear flow at the centre bulkhead q = T_skin/(2A) = {Tsk:.2f} N m / (2 x {A*1e6:.0f} mm2) = {q:.0f} N/m limit', float('nan')))
for tw in (0.0005, 0.0015, 0.003):
    rows.append((f'Bulkhead plate to skin bond, width {tw*1e3:.1f} mm (butt edge / flange), epoxy 2.0 MPa EST: tau x KP {q*KP/tw/1e6:.2f} MPa', P.BOND*tw/(q*KP)))
a_x, a_z = L_SOCK, 0.021                      # plate-to-saddle interface in the plate plane: saddle socket length x box height (2 x (8 + 2.5) mm)
tau = Tsk/(0.21*a_x*a_z**2) if False else Tsk/(0.246*max(a_x, a_z)*min(a_x, a_z)**2)   # rectangle torsion (beta ~0.246 at ratio 1.1, Roark)
rows.append((f'Plate-to-saddle face bond in torsion (face {a_x*1e3:.1f} x {a_z*1e3:.0f} mm, T_skin {Tsk:.2f} N m): tau x KP {tau*KP/1e6:.2f} MPa vs 2.0 EST', P.BOND/(tau*KP)))
arm = 0.018; F = Tsk/arm; Ap = math.pi/4*0.003**2
rows.append((f'CF cross-pin 3 mm, pair at {arm*1e3:.0f} mm arm (assumed layout, not drawn), double shear: force {F:.0f} N x KP vs 30 MPa EST', P.PIN_TAU*2*Ap/(F*KP)))
rows.append((f'Pin bearing in a 0.5 mm ply plate: allowable "—" (no source); stress would be {F*KP/(0.003*0.0005)/1e6:.0f} MPa', float('nan')))
for r, v in rows: print(f'| {r} | {v:.2f} |')
print('wall %.0f s' % (time.time()-t0))
