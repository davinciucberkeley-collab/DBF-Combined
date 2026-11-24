"""bridge_torsion_d206.py - D-206: bridge tube sizing for torsion (roll moment of the cage about the bridge axis).
    python -I bridge_torsion_d206.py   -> bridge_torsion_d206.md
Found by the hub FEA field map (review/QP-5/FEA-HUB.md): the 12 x 10 bridge was over its shear allowable in torsion. Earlier
checks (structures_a.py) covered the bridge in bending only.
Loads: the hub FEA load set (fea_hub.flight_combos / ground_combos), summed about the bridge axis (x through the hub).
Load path: the two 6 x 4.5 V struts lie in the z = 0 plane; their stiffness against hub roll is estimated below and is about
1 % of the bridge's, so the bridge is taken to carry the whole roll moment (static, no inertia relief, no tray pad).
Inertia relief is shown for information only. Allowables EST (fea_arm.ALLOW): CFRP shear 30 MPa; factors structures_a.py."""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = sys.argv[:1]
sys.path.insert(0, HERE)
import fea_hub as H                                   # noqa: E402
FA = H.FA
for kv in ('S_END=60', 'SLV_W=1.5', 'MS=1.1'):
    k, v = kv.split('='); H.GEO[k] = float(v)

L = []
def P(s=''): print(s); L.append(s)


def mx(loads):
    M = np.zeros(3)
    for st, (F, Mo) in loads.items():
        M += Mo + np.cross(H.stub_end(st), F)
    return M[0] / 1e3                                  # N m about x


M_F1 = max(abs(mx(c)) for c in H.flight_combos(FA.T_CAP, FA.Q_CAP))
M_F2 = max(abs(mx(c)) for c in H.flight_combos(FA.T_UNC, FA.Q_UNC))
gc = H.ground_combos()
M_S = {k: max(abs(mx(c)) for kk, c in gc if kk == k) for k in ('S1', 'S2', 'S3')}

# strut share. Hub roll theta about x. Each strut leaves its hub socket at y +-23 mm along d = (0.115, 0.262)/|d| (z = 0 plane).
#  (a) socket end moves z = 23 theta: strut bends as a cantilever-guided beam, k = 3 E I / L^3 x 0.023^2 (pinned sockets: lower bound)
#  (b) a rigid socket also turns the strut end by theta: bending about the in-plane normal (theta x |sin|, sin = d_y) with the far end held
#      by the spar clamp, k = 4 E I / L x d_y^2, and twist theta x d_x, k = G J / L x d_x^2 (rigid sockets and clamp: upper bound)
E_CF, G_CF = 70e9, 5e9                                 # EST round values (a stiffness ratio only)
dx_, dy_ = 0.050 + 0.065, 0.285 - 0.0229
Ls = math.hypot(dx_, dy_); cx, cy = dx_ / Ls, dy_ / Ls
I_s = math.pi / 64 * (0.006 ** 4 - 0.0045 ** 4)
k_pin = 2 * 3 * E_CF * I_s / Ls ** 3 * 0.0229 ** 2
k_rig = k_pin + 2 * (4 * E_CF * I_s / Ls * cy ** 2 + G_CF * 2 * I_s / Ls * cx ** 2)
def J(od, idd): return math.pi / 32 * (od ** 4 - idd ** 4)
L_br = 0.108
def k_br(od, idd): return G_CF * J(od, idd) / L_br
KF = 1.5 * 1.15; ALLOW = 30.0

P('# D-206 bridge tube in torsion: sizing')
P()
P('Structures engineer, 2026-11-17. `CALC`. Script `qp/A/structures/bridge_torsion_d206.py`. Found by the hub FEA map (review/QP-5/FEA-HUB.md).')
P()
P('## Roll moment about the bridge axis (hub FEA load set, worst pattern)')
P()
P('| Case | Roll moment (N m) | Factor |')
P('|---|---|---|')
P('| F1 thrust at the spin cap | %.2f | 1.725 |' % M_F1)
P('| F2 uncapped motor fault | %.2f | 1.725 |' % M_F2)
for k, t in (('S1', 'strike along the motor axis'), ('S2', 'strike in the disc plane'), ('S3', 'strike torque')):
    P('| %s %s | %.2f | 1.0 (damage case, D-202) |' % (k, t, M_S[k]))
P()
P('Struts against hub roll (two 6 x 4.5, %.0f mm, z = 0 plane): %.2f N m/rad with pinned sockets, %.0f N m/rad with rigid hub sockets and spar clamps. '
  'Bridge in torsion (G %.0f GPa EST, %.0f mm): 12 x 10 %.0f N m/rad, 16 x 14 %.0f N m/rad. Strut share of the roll moment: 12 x 10 %.0f-%.0f %%, 16 x 14 %.0f-%.0f %%. '
  'The real share sits between the bounds and depends on the printed sockets and the spar clamps (not modelled). The bridge is therefore sized to carry '
  'the whole roll moment (static: no inertia relief, no struts, no tray pad). Open item: if the struts do take their upper-bound share, their hub sockets '
  'see bending that no analysis has checked (about %.1f N m per socket in the S2 strike with the 16 x 14 bridge).' % (
    Ls * 1e3, k_pin, k_rig, G_CF / 1e9, L_br * 1e3, k_br(0.012, 0.010), k_br(0.016, 0.014),
    100 * k_pin / (k_pin + k_br(0.012, 0.010)), 100 * k_rig / (k_rig + k_br(0.012, 0.010)),
    100 * k_pin / (k_pin + k_br(0.016, 0.014)), 100 * k_rig / (k_rig + k_br(0.016, 0.014)),
    M_S['S2'] * k_rig / (k_rig + k_br(0.016, 0.014)) / 2))
P()
P('## Shear stress tau = T r / J and the options (limit load, MPa; allowable 30 at the factor)')
P()
P('| Tube | J/r (mm3) | F2 tau | F2 x 1.725 | S2 tau (x 1.0) | Result | Mass, 108 mm (g) |')
P('|---|---|---|---|---|---|---|')
rows = [('12 x 10 (D-202)', 0.012, 0.010), ('14 x 12', 0.014, 0.012), ('12 x 8 (same OD; not stocked by RMRC)', 0.012, 0.008), ('16 x 14 (D-206)', 0.016, 0.014)]
for n, od, idd in rows:
    Zt = J(od, idd) / (od / 2) * 1e9
    tf = M_F2 * 1e3 / Zt; ts = M_S['S2'] * 1e3 / Zt
    ok = tf * KF <= ALLOW and ts <= ALLOW
    m = math.pi / 4 * (od ** 2 - idd ** 2) * L_br * 1600 * 1000
    P('| %s | %.0f | %.1f | %.1f | %.1f | %s | %.1f |' % (n, Zt, tf, tf * KF, ts, 'PASS' if ok else 'FAIL', m))
P()
P('Choice: **16 x 14** (passes both statically, without relying on inertia relief, friction or the tray pad). Stock: BOM R02 (RMRC 16 x 14, 1 m) '
  'leaves a 0.28 m offcut after the two 0.36 m fin tubes; the bridge needs 0.108 m: no purchase. CAD: bridge axis 2 mm below the hub axis '
  '(16 mm top stays tangent to the tray plate underside z 6.0), boss r 10.0 (2.0 mm wall), saddle socket and core slot widened, strap under z -10.')
open(os.path.join(HERE, 'bridge_torsion_d206.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
