"""T-083 COPY of T077p7_data/t077p7_strength.py, run for the STRUT CGE-005 and R4 CLAMP CGE-007 rows only (the part-4 saddle rows it also prints are obsolete since
T-077 p8 and are ignored), on the T-083 demand (demand_t083.json / fea/demand_t083.npz, 1.912 kg, CG 25.92, Fp 36 N); --zetas added.
T-077 p7 (D-225): strength re-judgement of the PART-4 printed saddles (rib saddle FIN-005, bridge saddle CGE-006), the strut CGE-005 and the R4 strut clamp CGE-007
on the D-223 landing demand, with the T-077 p6 method (t077p6_strength.py: same formulas, same EST allowables, same demand file).
Category: rigid-body dynamics (demand: T077p6_data/demand_p6.json + fea/demand_p6.npz, landing_a.simulate, 1.705 kg, CG 23.91 mm, 23 cases x pad zeta 0.02/0.05/0.10 x mu 0.40/0.30)
+ HAND CALCULATION (landing_path_a formulas).  No FEA.
    python -I t077p7_strength.py [--tag T] [--strut OD,ID] [--rsock OD] [--rbore D] [--rfil R] [--rring L] [--sbond L] [--sad_ring L] [--sad_ro R] [--sad_box W] [--rsad_w W] [--rsad_ro R] [--rsad_x1 X]
      (all mm; defaults = the drawn tree read from wing.py: flags False = part-4 saddles).  Output strength_<tag>.json / .txt.
RF = allowable / (KF or KP x demand); demand = RB x D.  Columns: RB, x1.5 (floor), x1.97 (D-223 arm tube / bond), x2.23 (D-223 bridge and interim wing / saddle).
Judgement DAF per part (T-077 p6 rule, never lower): saddles, bridge, R4 clamp and strut 2.23 (none of them is in the D-1 frame model: the largest moment DAF, as p6).
Allowables (EST, as the repo): PETG 20 in-layer / 9.5 interlayer (structures_a.py; build axis z-up as p6), epoxy 2.0 MPa, CF 350 / 30 MPa, spar hoop 40 MPa, bearing 20 MPa."""
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
P6 = HERE
S_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures'))
os.environ['LAND_MASS_KG'] = os.environ.get('T083_MASS', '1.913'); os.environ['LAND_CG_X_MM'] = os.environ.get('T083_CG', '24.41'); os.environ['LAND_MASS_MODEL'] = 'cad'
sys.path.insert(0, S_DIR); sys.dont_write_bytecode = True
import numpy as np
import landing_path_a as P
W, C = P.W, P.C
assert not W.P5_CLAMSHELL and not W.P5_NODE, 'D-225: the part-4 saddles must be drawn (P5 flags False)'
KF, KP = P.KF, P.KP
A = sys.argv


def arg(k, d):
    return A[A.index(k) + 1] if k in A else d


TAG = arg('--tag', 'drawn')
DEM = json.load(open(os.path.join(P6, 'demand_t083.json'))); Z = np.load(os.path.join(P6, 'fea', 'demand_t083.npz'), allow_pickle=True)
NAMES = [str(n) for n in Z['names']]; ZETAS = tuple(float(z) for z in arg('--zetas', '0.02,0.05,0.10').split(',')); MUS = (0.40, 0.30)
P.set_pad(DEM['xf'], DEM['zf'])
FLOOR, DAF_ARM, DAF_W = 1.5, 1.97, 2.23
# ---------------------------------------------------------------- geometry (drawn: wing.py; overrides for sizing studies)
so, si = [float(v) * 1e-3 for v in arg('--strut', '%g,%g' % (W.STRUT_OD * 1e3, W.STRUT_ID * 1e3)).split(',')]
W.STRUT_OD, W.STRUT_ID = so, si                                        # P.strut_checks reads W.STRUT_OD / ID
CP = W.clamp_params()
G = dict(rsock=float(arg('--rsock', 2 * CP['RS'])) * 1e-3, rbore=float(arg('--rbore', so * 1e3)) * 1e-3, rfil=float(arg('--rfil', CP['FIL'])) * 1e-3,
         rring=float(arg('--rring', CP['y1'] - CP['y0'])) * 1e-3, sbond=float(arg('--sbond', CP['SL'])) * 1e-3,
         sad_ring=float(arg('--sad_ring', 30.0)) * 1e-3, sad_ro=float(arg('--sad_ro', 10.5)) * 1e-3, sad_box=float(arg('--sad_box', 2 * (W.BR_RO * 1e3 + 2.5))) * 1e-3,
         rsad_w=float(arg('--rsad_w', 19.0)) * 1e-3, rsad_ro=float(arg('--rsad_ro', 10.5)) * 1e-3, rsad_x1=float(arg('--rsad_x1', 90.5)) * 1e-3)
P.SAD_W, P.SAD_RO, P.SAD_X1 = G['rsad_w'], G['rsad_ro'], G['rsad_x1']; P.SAD_X0 = 0.0665; P.SAD_L = 0.060; P.RX0 = W.RIB_X0
ROD = W.RIB_OD; SX = W.SPAR_X
BR_OD, BR_ID, BR_Z, XB0 = W.BR_OD, W.BR_ID, W.BR_Z, 0.030
P_Z_BR = math.pi / 64 * (BR_OD ** 4 - BR_ID ** 4) / (BR_OD / 2)
R = {}
NODE_INFO = None
PS = 'Rib saddle FIN-005 (PETG, part 4: ring R %.1f x 60 on the spar, socket %.0f x %.0f x %.0f mm, rib 20 mm in)' % (G['rsad_ro'] * 1e3, G['rsad_w'] * 1e3, G['rsad_w'] * 1e3, (G['rsad_x1'] - 0.0665) * 1e3)
PB = 'Bridge saddle CGE-006 (PETG, part 4: ring R %.1f x %.0f on the spar, socket box %.0f x %.0f round the 16 mm bridge, 23.5 mm deep)' % (G['sad_ro'] * 1e3, G['sad_ring'] * 1e3, G['sad_box'] * 1e3, G['sad_box'] * 1e3)
PR = 'Strut %.0fx%.1f CGE-005 + R4 clamp CGE-007 (PETG: ring OD %.0f x %.0f, socket OD %.1f / bore %.1f, bond %.0f, fillet R %.1f)' % (so * 1e3, si * 1e3, 2 * CP['RR'], G['rring'] * 1e3, G['rsock'] * 1e3, G['rbore'] * 1e3, G['sbond'] * 1e3, G['rfil'] * 1e3)


def put(part, row, arr, case):
    k = (part, row); v = float(np.min(arr))
    if k not in R or v < R[k]['rb']: R[k] = dict(rb=v, case=case)


def run():
    for zeta in ZETAS:
        for mu in MUS:
            for nm in NAMES:
                key = '%.2f|%.2f|%s' % (zeta, mu, nm); FB = Z[key + '|FB'].astype(float); case = '%s z%.2f mu%.2f' % (nm, zeta, mu)
                # ---------------- RIB SADDLE FIN-005 (part 4): landing_path_a P9a-P14 with the drawn constants; P11 / P12 in-layer 20 (build z-up, as p6), interlayer shown
                sv = P.PETG_ILAY; P.PETG_ILAY = 20e6; res = P.checks(FB); P.PETG_ILAY = sv
                for rk, (lab, a) in res.items():
                    if rk.startswith(('P10', 'P13', 'P14b')): put(PS, rk + ' [in-layer]', a, case)
                    if rk.startswith(('P11', 'P12')): put(PS, rk + ', in-layer 20', a, case)
                    if rk.startswith('P9a'): put('Rib FIN-002 (not a changed part, shown)', rk, a, case)
                res9 = P.checks(FB)
                for rk, (lab, a) in res9.items():
                    if rk.startswith(('P11', 'P12')): put(PS, rk + ', interlayer 9.5 (shown only)', a, case)
                for k in (0, 1):
                    F, M = P.M_about(FB, k, P.S_(k, SX, 0.0))
                    put(PS, 'P14a spar 12x10 under the saddle ring with the skin torque share %.3f (bending in full), KF' % NODE_INFO['sh_spar'],
                        P.tube_rf(F[:, 1], NODE_INFO['sh_spar'] * M[:, 1], np.hypot(M[:, 0], M[:, 2]), P.A_S, P.Z_S), case)
                # ---------------- STRUT + R4 CLAMP
                sc = P.strut_checks(FB, Lb_clamp=G['sbond'])
                for rk, (lab, a) in sc.items():
                    if rk.startswith(('STRUT bond at clamp', 'STRUT Euler pinned', 'STRUT tube', 'STRUT bond at hub')): put(PR, rk.replace('6x4.5', '%.0fx%.1f' % (so * 1e3, si * 1e3)).replace('(D6 x', '(D%.0f x' % (so * 1e3)), a, case)
                ux, uy, Ls = P._strut_geom()
                As = math.pi / 4 * (G['rsock'] ** 2 - G['rbore'] ** 2); Aj = math.pi / 4 * ((G['rsock'] + 2 * G['rfil']) ** 2 - G['rbore'] ** 2)
                for k in (0, 1):
                    N = np.abs(np.sum([FB[:, 2 * k + j, 0] for j in (0, 1)], axis=0) / ux)
                    put(PR, 'R4 socket wall axial (A %.1f mm2: OD %.1f / bore %.1f), in-layer 20 (axis in the print plane)' % (As * 1e6, G['rsock'] * 1e3, G['rbore'] * 1e3), 20e6 / np.maximum(KP * N / As, 1e-9), case)
                    put(PR, 'R4 socket-to-ring junction at the R %.1f fillet base (annulus OD %.1f / bore %.1f, Kt 2.0 EST), interlayer 9.5' % (G['rfil'] * 1e3, (G['rsock'] + 2 * G['rfil']) * 1e3, G['rbore'] * 1e3),
                        9.5e6 / np.maximum(KP * 2.0 * N / Aj, 1e-9), case)
                    Nx, Ny = N * ux, N * uy; Lr = G['rring']
                    tau_r = np.hypot(Ny / (math.pi * 0.012 * Lr), (Nx * 0.010) / (2 * math.pi * 0.006 ** 2 * Lr)) * KP
                    put(PR, 'R4 ring bond on the spar (D12 x %.0f, Ny + torque Nx x 10 mm lever EST)' % (Lr * 1e3), P.BOND / np.maximum(tau_r, 1e-9), case)
                # ---------------- BRIDGE SADDLE CGE-006 (part 4): hub-side wrench through the bridge socket into the ring and the spar (p6 N6-N9 rows without the ears)
                P0 = np.array([W.HUB_X1, 0.0, BR_Z])
                Fh, Mh = Z[key + '|hub|F'].astype(float), Z[key + '|hub|M'].astype(float)
                dN = P0 - np.array([SX, 0.0, 0.0]); MN = Mh + np.cross(np.broadcast_to(dN, Fh.shape), Fh)
                Lr = G['sad_ring']; rb = P.bond_rf(Fh[:, 1], MN[:, 1], np.hypot(MN[:, 0], MN[:, 2]), np.hypot(Fh[:, 0], Fh[:, 2]), P.SOD, Lr)
                put(PB, 'N8 ring epoxy bond on spar D12 x %.0f: shear (axial + torsion)' % (Lr * 1e3), rb[0], case)
                put(PB, 'N8 ring bond on spar D12 x %.0f: bearing, compression side (PETG 20)' % (Lr * 1e3), rb[1], case)
                put(PB, 'N8 ring bond on spar D12 x %.0f: BOND INTEGRITY / peel (integrity class)' % (Lr * 1e3), rb[2], case)
                Rm_ = (P.SOD + P.SID) / 4; tw_ = (P.SOD - P.SID) / 2; Pc = np.hypot(Fh[:, 0], Fh[:, 2])
                put(PB, 'N8c spar wall diametral crush under the %.0f mm ring (hoop 40 MPa EST), KF' % (Lr * 1e3), P.SPAR_HOOP / np.maximum(6 * 0.318 * Pc * Rm_ / (Lr * tw_ ** 2) * KF, 1e-9), case)
                xj = 0.0535; dJ = P0 - np.array([xj, 0.0, BR_Z]); MJ = Mh + np.cross(np.broadcast_to(dJ, Fh.shape), Fh); aJ = P.chord(G['sad_ro'], xj - SX)
                for il, tg in ((20e6, 'in-layer 20'), (9.5e6, 'interlayer 9.5 (shown only)')):
                    put(PB, 'N9 socket-to-ring junction at x 53.5 (%.1f x %.0f mm: ring chord x socket width), %s' % (aJ * 1e3, G['sad_box'] * 1e3, tg),
                        P.rect_rf(Fh[:, 0], np.hypot(Fh[:, 1], Fh[:, 2]), MJ[:, 0], MJ[:, 1], MJ[:, 2], G['sad_box'], aJ, il, il), case)
                for xs_, lab in ((XB0, 'forward end x 30'), (SX - G['sad_ro'], 'ring face x %.1f' % ((SX - G['sad_ro']) * 1e3))):
                    d = P0 - np.array([xs_, 0.0, BR_Z]); Ms = Mh + np.cross(np.broadcast_to(d, Fh.shape), Fh); Mt = np.hypot(Ms[:, 1], Ms[:, 2]); Vt = np.hypot(Fh[:, 1], Fh[:, 2])
                    if lab.startswith('forward'):
                        Lb = 0.0235
                        put(PB, 'N6 bridge bearing in the 23.5 mm socket (6M/(D L^2)+V/(D L), M at the mouth, PETG 20)', 20e6 / np.maximum(KP * (6 * Mt / Lb ** 2 + Vt / Lb) / BR_OD, 1e-9), case)
                        put(PB, 'N6b bridge-in-socket bond, axial + torque (integrity class)', P.BOND / np.maximum(KP * np.hypot(np.abs(Fh[:, 0]) / (math.pi * BR_OD * Lb), np.abs(Ms[:, 0]) / (2 * math.pi * (BR_OD / 2) ** 2 * Lb)), 1e-9), case)
                    bw = G['sad_box']; Zs = (bw ** 4 / 12 - math.pi * BR_OD ** 4 / 64) / (bw / 2)
                    put(PB, 'N7 socket net section under M at the %s (box %.0f x %.0f less bore 16, Z %.0f mm3), in-layer 20' % (lab, bw * 1e3, bw * 1e3, Zs * 1e9), 20e6 / np.maximum(KP * Mt / Zs, 1e-9), case)
                    put('Bridge tube CGE-004 16x14 (CF, not a changed part)', 'B1 bridge bending at the %s (350 MPa EST, KF)' % lab, 350e6 / np.maximum(KF * Mt / P_Z_BR, 1e-9), case)
                    if lab.startswith('forward'): put('Hub-side wrench (demand record)', 'max |M| (My, Mz) at x 30 [N m, x1000 in the RF columns: not an RF]', 1e3 / np.maximum(Mt, 1e-9), case)
                    if lab.startswith('forward'): put('Hub-side wrench (demand record)', 'max |My| at the spar axis (ring torque) [N m, x1000: not an RF]', 1e3 / np.maximum(np.abs(MN[:, 1]), 1e-9), case)


INTEG = ('integrity', 'peel', 'N6b', 'shown only')


def main():
    global NODE_INFO
    np.seterr(all='ignore'); key0 = '0.05|0.40|%s' % NAMES[0]
    NODE_INFO = P.wing_checks_skin(Z[key0 + '|FB'].astype(float), P.skin_variants()[0][1])[1]
    print('# T-077 p7 strength rows, tag %s. Demand (T-077 p6): Fp %.0f N / %.0f mm, mass %.3f kg, CG %.2f mm; KF %.3f KP %.3f; geometry %s' % (TAG, DEM['Fp'], DEM['smax'] * 1e3, DEM['mass'], DEM['cg'][0] * 1e3, KF, KP, {k: round(v * 1e3, 2) for k, v in G.items()}))
    print('# strut %.1fx%.1f, length %.1f mm; skin torque share %.3f, spar share %.3f' % (so * 1e3, si * 1e3, P._strut_geom()[2] * 1e3, NODE_INFO['sh_skin'], NODE_INFO['sh_spar']))
    run()
    out = []
    print('\n| part | row | RB | x1.5 | x1.97 | x2.23 | verdict at x2.23 | governing case |\n|---|---|---|---|---|---|---|---|')
    for (part, row), v in sorted(R.items(), key=lambda kv: (kv[0][0], kv[1]['rb'])):
        rb = v['rb']
        if row.startswith('max |M'): print('| %s | %s = %.2f N m (RB) | | | | | | %s |' % (part, row.split('[')[0], 1e3 / rb, v['case'])); continue
        integ = any(k.lower() in row.lower() for k in INTEG)
        vd = ('integrity / shown: %s' % ('>= 1' if rb / DAF_W >= 1 else '< 1')) if integ else ('PASS' if rb / DAF_W >= 1 else 'FAIL')
        print('| %s | %s | %.2f | %.2f | %.2f | %.2f | %s | %s |' % (part, row, rb, rb / FLOOR, rb / DAF_ARM, rb / DAF_W, vd, v['case']))
        out.append(dict(part=part, row=row, rb=rb, x15=rb / FLOOR, x197=rb / DAF_ARM, x223=rb / DAF_W, integrity=integ, verdict=vd, case=v['case']))
    json.dump(dict(tag=TAG, geometry={k: v * 1e3 for k, v in G.items()}, strut=[so * 1e3, si * 1e3], rows=out), open(os.path.join(HERE, 'strength_%s.json' % TAG), 'w'), indent=1)


if __name__ == '__main__': main()
