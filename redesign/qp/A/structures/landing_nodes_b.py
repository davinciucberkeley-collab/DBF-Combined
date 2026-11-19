"""T-071b Part B steps 2 and 4: clamshell saddle (FIN-005), enlarged root block (FIN-003) and the foot path re-run around the glass skin.   python -I landing_nodes_b.py > out.txt   (about 1.5 min)
Categories: rigid-body dynamics (landing_a.py force histories, 23 cases, T-068 D2 pad, mu 0.30 face) + HAND CALCULATION (clamshell first-order model below).  No FEA.  Allowables EST unless sourced.
Geometry through module constants of landing_path_a (as landing_path_options_a.py):
  root block FIN-003 enlarged (T-068 D4): ring OD 25 x 60, socket 22 x 22 over x 0.235..0.286 (51 mm), printed with z up so the junction bending is in-layer (20 MPa EST, ASM-A-PETG-ALLOW) instead of interlayer 9.5.
  saddle FIN-005 as clamshell (T-068 D4): printed socket rows P11 / P12 (thin PETG sections) are REPLACED by plate rows; rib engagement 40 mm (SAD_X1 0.1105); 2 x 3 mm CF cross-pins; plates 50 (x) x 75 (y) x tp (z +-8.25 mm).
Clamshell first-order model (all EST; bonded interface areas and the cradle frame fraction are NOT drawn, coupon needed): loads at the crossing S = (SX, +-YF, 0) from the two feet of one fin:
  rib bending My (x-z plane = wing torque) is carried as a couple of x-forces in the two plates, arm a_z = 16.5 mm; rib axial Fx splits half to each plate; Mx (rib torque, spar bending) as a couple of y-forces, arm a_z, with Fy split half / half;
  Mz is in-plane bending of the plate pair (Z = 2 tp w^2 / 6, T-068 indicative); the plate-to-cradle bond (area 0.5 x 50 x 75 mm2 EST: the cradle is a frame) takes the resultant plate shear plus Mz as a torque of the plate;  Fz peels the plates.
  Plate laminate: ACP Composites PDS Dec 2014 (read 2026-11-19, pypdf text of the PDF): Std CF fabric, Vf 50 %, dry, RT: Xt 600 / Xc 570 MPa, S 90 MPa (0/90 axes), x 0.70 EST for a cured bought sheet.  Bearing in the plate: no source, '-'."""
import sys, os, math, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import landing_path_a as P
L, W, C = P.L, P.W, P.C
KF, KP = P.KF, P.KP
XC, SC, KNOCK = 570e6, 90e6, 0.70
def clamshell_rows(FBt, tp=0.0015, wx=0.050, ly=0.075, az=0.0165, frame=0.5, n_pin=2):
    out = {}
    for k in (0, 1):
        F, M = P.M_about(FBt, k, P.S_(k, P.SX, 0.0)); Fx, Fy, Fz = [np.abs(F[:, i]) for i in range(3)]; Mx, My, Mz = [np.abs(M[:, i]) for i in range(3)]
        Zin = 2*tp*wx**2/6
        sx = (My/az+Fx/2)/(ly*tp)+Mz/Zin; sy = (Mx/az+Fy/2)/(wx*tp)+Mz/Zin
        out.setdefault('CS1 plate, x-direction (My couple, Fx half, Mz in-plane), CF %.1f mm vs %.0f MPa' % (tp*1e3, XC*KNOCK/1e6), []).append(XC*KNOCK/(KF*np.maximum(sx, 1e-9)))
        out.setdefault('CS2 plate, y-direction (Mx couple, Fy half, Mz in-plane)', []).append(XC*KNOCK/(KF*np.maximum(sy, 1e-9)))
        Ab = frame*wx*ly; Jp = wx*ly*(wx**2+ly**2)/12; r = 0.5*math.hypot(wx, ly)
        tau = np.hypot(My/az+Fx/2, Mx/az+Fy/2)/Ab+(Mz/2)*r/Jp
        out.setdefault('CS3 plate-to-cradle bond shear (area %.0f mm2 EST, epoxy 2.0 MPa EST)' % (Ab*1e6), []).append(P.BOND/(KP*np.maximum(tau, 1e-9)))
        out.setdefault('CS3p plate-to-cradle PEEL by Fz (bond integrity, outside the minimum)', []).append(P.BOND/(KP*np.maximum(Fz/2/Ab, 1e-9)))
        V = Mx/P.ROD/n_pin
        out.setdefault('CS5 CF cross-pins %d x 3 mm, double shear, rib torque Mx (EST 30 MPa)' % n_pin, []).append(P.PIN_TAU/np.maximum(V/(2*P.PIN_A)*KP, 1e-9))
        out.setdefault('CS5b pin bearing in PETG cradle wall 3 x 2 mm (20 MPa EST)', []).append(P.PETG_BEAR/np.maximum(V/(P.PIN_D*0.002)*KP, 1e-9))
    return {kk: np.minimum.reduce(v) for kk, v in out.items()}


def p14a_skin(FBt, sh_s):
    """P14a with the glass skin: torsion share sh_s of the wing torque stays on the spar (V0: 0.056), the bending moments stay on the spar in full (conservative: skin and foam share out-of-plane bending, P16 handles the in-plane share)."""
    r = []
    for k in (0, 1):
        F, M = P.M_about(FBt, k, P.S_(k, P.SX, 0.0)); r.append(P.tube_rf(F[:, 1], sh_s*M[:, 1], np.hypot(M[:, 0], M[:, 2]), P.A_S, P.Z_S))
    return np.minimum.reduce(r)
def pin_option_rows(FBt, n, wall, d=0.003):
    """n cross-pins of diameter d in a socket wall of thickness wall (root block: (22-14)/2 = 4 mm; as drawn 2.5 mm; clamshell cradle 2 mm): shear (double) and bearing, torque Mx on the rib shared n ways, couple arm = rib OD."""
    out = {}
    for k in (0, 1):
        for nm, x in (('root block', P.BLK_X0), ('saddle', 0.1105)):
            Fm, M = P.M_about(FBt, k, P.S_(k, x, 0.0)); V = np.abs(M[:, 0])/P.ROD/n; A = math.pi/4*d*d
            out.setdefault('PIN %s: %d x %.0f mm, double shear' % (nm, n, d*1e3), []).append(P.PIN_TAU/np.maximum(V/(2*A)*P.KP, 1e-9))
            out.setdefault('PIN %s: %d x %.0f mm, bearing in %.1f mm PETG wall' % (nm, n, d*1e3, wall*1e3), []).append(P.PETG_BEAR/np.maximum(V/(d*wall)*P.KP, 1e-9))
    return {kk: np.minimum.reduce(v) for kk, v in out.items()}

def main():
    t0 = time.time(); P.set_pad(P.PAD_D2['x_foot'], P.PAD_D2['z_foot']); MU = 0.30
    FBs = []
    for name, kw in P.cases(False):
        FBs.append((name, L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, mu=MU, **dict(kw, **P.PAD_D2))['trace'].reshape(-1, 4, 3)))
    print('# T-071b Part B: D2 pad (x %.4f, z %.3f), mu %.2f, 23 cases, plateau 30 N, KF %.3f KP %.3f [%.0f s]' % (P.XF, P.ZF, MU, KF, KP, time.time()-t0))
    cfgs = {'A0 as drawn (printed saddle SAD_X1 0.0905, block 19 x 19, interlayer 9.5)': dict(),
            'B1 T-071b geometry: block ring OD 25 x 60, socket 22 x 22 from x 0.235, saddle engagement 40 mm; P6 / P8 in-layer rule': dict(BLK_X0=0.2350, BLK_W=0.022, RING_BL_RO=0.0125, SAD_X1=0.1105)}
    res = {}
    for cname, cfg in cfgs.items():
        saved = {k: getattr(P, k) for k in cfg}
        for k, v in cfg.items(): setattr(P, k, v)
        allr = {}
        for ilay in ((9.5e6,) if cname.startswith('A0') else (9.5e6, 20e6)):
            sv = P.PETG_ILAY; P.PETG_ILAY = ilay
            for name, FBt in FBs:
                for key, (lab, a) in P.checks(FBt).items():
                    allr.setdefault((key, ilay), []).append((float(a.min()), name))
            P.PETG_ILAY = sv
        res[cname] = {k: min(v) for k, v in allr.items()}
        for k, v in saved.items(): setattr(P, k, v)
    # report rows
    print('\n## Printed-part rows (landing_path_a.checks, minimum RF over 23 cases; interlayer 9.5 MPa / in-layer 20 MPa where both run)')
    A0 = res[list(cfgs)[0]]; B1 = res[list(cfgs)[1]]
    keys = sorted({k for k, _ in A0} | {k for k, _ in B1}, key=lambda s: (int(''.join(c for c in s.split(' ')[0] if c.isdigit()) or 0), s))
    print('| Row | A0 as drawn, mu 0.30 | B1 T-071b geometry, interlayer | B1 in-layer rule (P6 / P8 / P11 / P12 are the in-layer-print rows) |'); print('|---|---|---|---|')
    for key in keys:
        a = A0.get((key, 9.5e6)); b = B1.get((key, 9.5e6)); c = B1.get((key, 20e6))
        print('| %s | %s | %s | %s |' % (key, '%.2f' % a[0] if a else '-', '%.2f' % b[0] if b else '-', '%.2f' % c[0] if c else '-'))
    # clamshell rows, tp scan
    print('\n## Clamshell saddle first-order rows (replace P11 / P12; engagement 40 mm P9a / P10 / P13 above)')
    for tp in (0.0010, 0.0015):
        cs = {}
        for name, FBt in FBs:
            for key, a in clamshell_rows(FBt, tp=tp).items(): cs[key] = min(cs.get(key, (1e9, ''))[0], float(a.min())), name
        for key, (rf, nm) in sorted(cs.items()): print('| plate t %.1f mm | %s | %.2f | %s |' % (tp*1e3, key, rf, nm))
    # wing + strut rows and pin / cup rows
    allw = {}
    for name, FBt in FBs:
        r, _ = P.wing_checks_skin(FBt, P.skin_variants()[0][1]); r.update(P.strut_checks(FBt, id_=4.0e-3)); r.update(P.pin_cup_checks(FBt))
        for key, (lab, a) in r.items():
            allw[key] = min(allw.get(key, (1e9, ''))[0], float(a.min())), name
    fam = {}
    for key, (rf, nm) in allw.items():
        f = key.split(',')[0] if (key.startswith('P15') or key.startswith('P16')) else key
        if f not in fam or rf < fam[f][0]: fam[f] = (rf, key, nm)
    print('\n## Wing (V0 skin, 1 ply 48 g/m2 +-45, strip 3 mm2, KP), strut 6x4.0, pin / cup rows with D2 pad and mu 0.30: min over 23 cases and stations')
    for f, (rf, key, nm) in sorted(fam.items(), key=lambda kv: kv[1][0]): print('| %s | %.2f | %s | %s |' % (f, rf, key, nm))
    sh_s = P.wing_checks_skin(FBs[0][1], P.skin_variants()[0][1])[1]['sh_spar']
    m14 = min(float(p14a_skin(FBt, sh_s).min()) for _, FBt in FBs)
    print('\n## P14a spar under the saddle with the skin: torsion share %.3f on the spar, bending in full (conservative), KF: min RF %.2f (the skin-less P14a above is the superseded bound)' % (sh_s, m14))
    print('\n## PIN options (torque Mx on the rib shared by n pins; D4 chose 1 pin at the root block and 2 at the saddle)')
    for n, wall in ((1, 0.0025), (2, 0.0025), (2, 0.004), (3, 0.004), (4, 0.004)):
        pr = {}
        for name, FBt in FBs:
            for key, a in pin_option_rows(FBt, n, wall).items(): pr[key] = min(pr.get(key, 1e9), float(a.min()))
        print('| ' + ' | '.join('%s %.2f' % (k, v) for k, v in sorted(pr.items())) + ' |')
    print('\nwall %.0f s' % (time.time()-t0))
if __name__ == '__main__': main()
