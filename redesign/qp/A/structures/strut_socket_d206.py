"""strut_socket_d206.py - T-025 follow-up to D-206 open item (5): bending of the V-strut hub sockets if the struts take their share of the hub roll moment.
    python -I strut_socket_d206.py   -> out/strut_socket_d206.json
CATEGORY: hand calculation, structures (static, linear). Not FEA. Every allowable and the socket wall are EST.
Why: D-206 sized the 16 x 14 bridge to carry the whole cage roll moment alone. The V struts (6 x 4.5, z = 0 plane) also resist hub roll; their share is unknown
(bridge_torsion_d206.py: about 0 % pinned sockets to 37 % rigid sockets for the 16 x 14 bridge). At the upper bound each hub strut socket sees about 1.5 N m in the
S2 strike (D-206 open item 5, review T-025 finding 4). No check existed. This script resolves that share into the end loads of one strut and checks the printed socket.
Inputs and their sources:
  roll moments F1, F2, S1, S2, S3 about the bridge axis, strut / bridge stiffness model, E, G, geometry of the strut: bridge_torsion_d206.py (imported: same load set, same model).
  socket: CAD amodel/wing.py HUB_W 0.8 mm printed wall (EST, 2 perimeters), strut OD 6 / ID 4.5 (DOC 6x4.5), bore depth HUB_STRUT_S[1] 32 mm (+2 mm bore beyond the mouth), boss R = 3 + 0.8 mm.
  allowables and factors as used in structures/fea_arm.py: cf_axial 350, petg 20, petg_ilay 9.5, bond 2.0 MPa (all EST); factors KF 1.725 (CFRP / metal), KP 2.156 (printed / bonded)
  at the flight cases; the strike cases S1..S3 are damage cases at factor 1.0 (D-202).
Model (EST, labelled): hub roll theta (rad) from a roll-moment share f: theta = f M / k_rigid. Per strut, free span L = 286 mm (the model of bridge_torsion_d206.py, conservative on
  the load: a shorter free span would be stiffer and take more), cantilever far end held by the spar clamp:
    V = 3 E I / L^3 * (0.0229 theta)   vertical force at the socket mouth (socket end moves z = 23 mm x theta)
    Mb = 4 E I / L * cy * theta        bending moment about the in-plane normal (rigid socket turns the strut end by theta cy)
    T  = G J / L * cx * theta          twist about the strut axis
  Check sum: V x 0.0229 + Mb cy + T cx = k_rigid/2 x theta (half of the roll stiffness, one strut).
Socket checks (EST models):
  a) strut tube bending: sigma = Mb r / I vs cf_axial x factor.
  b) bearing pressure of the rigid tube on the socket wall from Mb, linear contact over the engaged depth D, p_max = 6 Mb / (d D^2) (d = 6 mm), then wall hoop tension
     sigma_h = p_max r_i / t (thin ring, r_i 3 mm, t 0.8 mm), vs petg 20 (in-layer) and petg_ilay 9.5 (if the print puts the hoop across layers; print orientation of the hub is "-").
  c) bond shear: tau_T = T / (2 pi r^2 D) from the twist, tau_V = V / (d D) from the force; combined sqrt(tau_T^2 + tau_V^2) vs bond 2.0 x factor. Mean values; the peak at the mouth is not modelled.
Not modelled: stress concentration at the mouth, printed-wall anisotropy, boss to block fillet, bond peel. A pass here is a hand-calculation pass with EST allowables; it does not replace an FEA of the socket.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = sys.argv[:1]
sys.path.insert(0, HERE)
import bridge_torsion_d206 as B                       # noqa: E402  (loads, strut model; also rewrites bridge_torsion_d206.md with identical text)

KF, KP = B.KF, B.KF * 1.25                            # 1.725, 2.156 (fea_arm.py)
ALLOW = dict(cf_axial=350.0, petg=20.0, petg_ilay=9.5, bond=2.0)
E, G = B.E_CF, B.G_CF
OD, ID = 0.006, 0.0045
I = B.I_s
Jp = 2 * I
L, cx, cy = B.Ls, B.cx, B.cy
ZL = 0.0229                                           # strut socket lever about the roll axis (STRUT_S y)
D_ENG, T_WALL, R_I = 0.032, 0.0008, 0.003             # CAD: bore depth, HUB_W, bore radius
k_rig, k_pin = B.k_rig, B.k_pin
k_br16 = B.k_br(0.016, 0.014)
f_up = k_rig / (k_rig + k_br16)                       # upper bound strut share, 16 x 14 bridge

cases = [('F1', B.M_F1, KF, KP), ('F2', B.M_F2, KF, KP), ('S1', B.M_S['S1'], 1.0, 1.0), ('S2', B.M_S['S2'], 1.0, 1.0), ('S3', B.M_S['S3'], 1.0, 1.0)]


def socket_loads(M_roll_Nm, f):
    th = f * M_roll_Nm / k_rig                        # rad
    V = 3 * E * I / L ** 3 * ZL * th                  # N
    Mb = 4 * E * I / L * cy * th                      # N m
    T = G * Jp / L * cx * th                          # N m
    chk = V * ZL + Mb * cy + T * cx                   # N m, must equal half of the share
    return th, V, Mb, T, chk


def checks(Mb, V, T, fcf, fpr):
    sig_tube = Mb * (OD / 2) / I / 1e6                # MPa
    p = 6 * Mb * 1e3 / (6.0 * (D_ENG * 1e3) ** 2)     # N mm / (mm mm2) = MPa
    sig_h = p * (R_I * 1e3) / (T_WALL * 1e3)
    tau_T = T * 1e3 / (2 * math.pi * (R_I * 1e3) ** 2 * (D_ENG * 1e3))
    tau_V = V / (6.0 * D_ENG * 1e3)
    tau = math.hypot(tau_T, tau_V)
    return dict(sigma_tube_MPa=sig_tube, util_tube=sig_tube * fcf / ALLOW['cf_axial'],
                p_bearing_MPa=p, hoop_MPa=sig_h, util_petg_inlayer=sig_h * fpr / ALLOW['petg'], util_petg_across_layers=sig_h * fpr / ALLOW['petg_ilay'],
                tau_twist_MPa=tau_T, tau_force_MPa=tau_V, tau_bond_MPa=tau, util_bond=tau * fpr / ALLOW['bond'])


out = dict(
    category='hand calculation, structures (static); EST models and allowables; not FEA',
    inputs=dict(strut_span_mm=L * 1e3, cx=cx, cy=cy, E_GPa=E / 1e9, G_GPa=G / 1e9, I_mm4=I * 1e12, socket_wall_mm=T_WALL * 1e3, engaged_depth_mm=D_ENG * 1e3, bore_r_mm=R_I * 1e3,
                k_pinned_Nm_rad=k_pin, k_rigid_Nm_rad=k_rig, k_bridge16x14_Nm_rad=k_br16, share_upper_bound_16x14=f_up, KF=KF, KP=KP, allow=ALLOW),
    cases={}, breakeven={})
for name, M, fcf, fpr in cases:
    row = {}
    for tag, f in (('upper_bound_rigid_sockets', f_up), ('pinned_sockets', k_pin / (k_pin + k_br16))):
        th, V, Mb, T, chk = socket_loads(M, f)
        c = checks(Mb, V, T, fcf, fpr)
        row[tag] = dict(share=f, M_roll_Nm=M, M_share_per_strut_Nm=f * M / 2, theta_mrad=th * 1e3, V_N=V, Mb_Nm=Mb, T_Nm=T, sum_check_Nm=chk, **c)
    out['cases'][name] = row
# breakeven share (utilisation 1) for the governing check, per case
for name, M, fcf, fpr in cases:
    lo, hi = 0.0, 1.0
    r = lambda f: max(v for k, v in checks(*socket_loads(M, f)[1:4], fcf, fpr).items() if k.startswith('util') and k != 'util_petg_across_layers')
    if r(1.0) <= 1.0: out['breakeven'][name] = '>= 1.0 (never governs)'
    else:
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if r(mid) < 1.0 else (lo, mid)
        out['breakeven'][name] = round(hi, 3)
gov = {n: float(max(v for k, v in c['upper_bound_rigid_sockets'].items() if k.startswith('util') and k != 'util_petg_across_layers')) for n, c in out['cases'].items()}
gov_ilay = {n: c['upper_bound_rigid_sockets']['util_petg_across_layers'] for n, c in out['cases'].items()}
out['governing_utilisation_upper_bound_in_layer'] = gov
out['util_petg_if_hoop_across_layers_upper_bound'] = gov_ilay
out['verdict'] = ('PASS (hand calculation, EST allowables, every governing utilisation <= 1.0)' if max(gov.values()) <= 1.0 else 'FAIL: see the cases')
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
json.dump(out, open(os.path.join(HERE, 'out', 'strut_socket_d206.json'), 'w'), indent=1)
for n, c in out['cases'].items():
    u = c['upper_bound_rigid_sockets']
    print('%s: share %.2f, per-strut roll share %.2f N m (V %.1f N, Mb %.2f N m, T %.2f N m; sum check %.2f); tube %.2f bond %.2f petg %.2f (across layers %.2f)' % (
        n, u['share'], u['M_share_per_strut_Nm'], u['V_N'], u['Mb_Nm'], u['T_Nm'], u['sum_check_Nm'], u['util_tube'], u['util_bond'], u['util_petg_inlayer'], u['util_petg_across_layers']))
print('governing (in layer):', {k: round(v, 2) for k, v in gov.items()}, out['verdict']); print('breakeven share:', out['breakeven'])
