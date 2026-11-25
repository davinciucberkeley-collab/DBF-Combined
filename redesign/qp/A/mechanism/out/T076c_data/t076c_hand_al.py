"""T-076c step 4 hand rows for the aluminium hub (audit s3.2 'Rows that move'); python -I t076c_hand_al.py.  CATEGORY: hand calculation on the step 1 / D-1 demand.  EST allowables as the repo (CF transverse 40 MPa, epoxy 2.0 MPa), Al yield 240 MPa (Wikipedia 6061 aluminium alloy, read 2026-11-20).
Rows at max(DAF, 1.5) with DAF = 1.0 .. 1.5 (D-1 hub-root Mz / bridge ratios vs the sim RB are 0.90 / 0.91 enveloped, 1.21 / 1.08 case-max: floor 1.5 governs), plus the D-1 dynamic peaks directly."""
import json, os, math
import numpy as np
D = os.path.dirname(os.path.abspath(__file__))
s1 = json.load(open(os.path.join(D, 'step1_demand.json'))); s2 = json.load(open(os.path.join(D, 'step2_d1.json')))
KF, KP = 1.725, 1.725*1.25
SY, CF_T, BOND, DBR = 240.0, 40.0, 2.0, 16.0
gl = s1['global_P0']; Mz, Mx, My = gl['Mz'], gl['Mx'], gl['My']; Fy, Fz = gl['Fy'], gl['Fz']
dyn = {k: v for k, v in s2['runs'].items() if k.startswith('asbuilt') and k.endswith('|1|summary')}
dm = max(v['components']['Mz']['env_dyn'] for v in dyn.values()); dmy = max(v['components']['My']['env_dyn'] for v in dyn.values()); dmx = max(v['components']['Mx']['env_dyn'] for v in dyn.values())
dfy = max(v['components']['Fy']['env_dyn'] for v in dyn.values()); dfz = max(v['components']['Fz']['env_dyn'] for v in dyn.values())
rows = []
def p(*a): print(*a)
for label, Mzs, Mys, Mxs, Fys, Fzs in (('RB x1.0', Mz, My, Mx, Fy, Fz), ('RB x1.5 (floor)', 1.5*Mz, 1.5*My, 1.5*Mx, 1.5*Fy, 1.5*Fz), ('D-1 dynamic env (as-built, zeta 1 %, enveloped over kd/nom/hi)', dm, dmy, dmx, dfy, dfz)):
    # (a) Al block net section 20 x 20 solid, bending about z (y width 20): sigma = Mz / Z, KF, vs yield (no hole subtraction: upper bound on capacity; holes reduce it: '—')
    Z = 20.0*20.0**2/6.0; sig = Mzs*1e3/Z; rf_blk = SY/(KF*sig)
    # (b) same section with the 16 mm bore subtracted (I of a 20 x 20 box minus a 16 mm circle, bending about z) as a lower bound
    I = 20.0*20.0**3/12 - math.pi*16**4/64; Zb = I/10.0; rf_blk2 = SY/(KF*Mzs*1e3/Zb)
    # (c) CF bridge transverse bearing in the Al bore, bonded L 30 mm, triangular pressure about mid-length, moment |(My, Mz)|, EST 40 MPa transverse
    Lb = 30.0; Mb = math.hypot(Mzs, Mys)*1e3; V = math.hypot(Fys, Fzs); pb = (6*Mb/(DBR*Lb**2) + V/(DBR*Lb)); rf_b = CF_T/(KF*pb)
    # (d) bridge-bore bond, torsion Mx: tau = T / (2 pi r^2 L), x KP vs 2.0 MPa EST
    tau = Mxs*1e3/(2*math.pi*8.0**2*Lb); rf_bond = BOND/(KP*tau)
    # (e) bridge tube bending 16x14 at the mouth
    zt = math.pi/64*(16**4-14**4)/8; rf_t = 350/(KF*math.hypot(Mzs, Mys)*1e3/zt)
    rows.append((label, Mzs, sig, rf_blk, rf_blk2, pb, rf_b, tau, rf_bond, rf_t))
p('| demand | Mz N m | block sigma MPa (solid 20x20) | RF block solid | RF block with 16 mm bore removed | CF bridge bearing p MPa (L 30) | RF bearing (40 MPa EST) | bore bond tau MPa | RF bond (2.0 MPa EST, KP) | RF bridge tube bending |')
p('|---|---|---|---|---|---|---|---|---|---|')
for r in rows: p('| %s | %.1f | %.1f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f |' % r)
json.dump([list(r) for r in rows], open(os.path.join(D, 'hand_al_rows.json'), 'w'))
