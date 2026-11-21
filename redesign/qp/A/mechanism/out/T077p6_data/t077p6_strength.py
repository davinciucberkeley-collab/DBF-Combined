"""T-077 p6 step 2: strength check of the DRAWN node (CGE-006 / 011 / 012 / 013), clamshell (FIN-005 / 007 / 008), R4 clamps (CGE-007) on the D-223 landing demand.
(R3fix cups: t077p6_cups.py; R2 bosses: t077p6_bosses.py.)
Category: rigid-body dynamics (demand, t077p6_demand.py) + HAND CALCULATION (landing_path_a / landing_nodes_b / landing_centre_a patterns, drawn dimensions from wing.py).  No FEA.
    python -I t077p6_strength.py [--variant V0|V1|V2|V12] > strength_<variant>.txt
RF = allowable / (KF or KP x demand), same formulas as landing_path_a.py; demand = RB x D (D = 1.0 shown, 1.5 floor, DAF 1.97 arm / bond rows, 2.23 bridge / node / saddle / clamshell / wing rows = DAF ruling s1.3).
Minimum over 23 cases x pad zeta 0.02 / 0.05 / 0.10 x face mu 0.40 / 0.30.  Allowables EST as the repo (PETG 20 in-layer / 9.5 interlayer, Onyx the same (T-080 s1), epoxy 2.0, CF pin 30, CF 350 / 30; plate ACP x 0.70); '-' = no source.
Variants (lightening candidates, geometry through GEO): V0 as drawn; V1 cradle socket round OD 18 with flats at z +-8.0 mm; V2 node saddle ring wall 2.0 mm (OD 16); V12 both."""
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
S_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures'))
os.environ['LAND_MASS_KG'] = '1.705'; os.environ['LAND_CG_X_MM'] = '23.91'; os.environ['LAND_MASS_MODEL'] = 'cad'
sys.path.insert(0, S_DIR); sys.dont_write_bytecode = True
import numpy as np
import landing_path_a as P
W, C = P.W, P.C
KF, KP = P.KF, P.KP
VAR = sys.argv[sys.argv.index('--variant') + 1] if '--variant' in sys.argv else 'V0'
DEM = json.load(open(os.path.join(HERE, 'demand_p6.json'))); Z = np.load(os.path.join(HERE, 'fea', 'demand_p6.npz'), allow_pickle=True)
NAMES = [str(n) for n in Z['names']]; ZETAS = (0.02, 0.05, 0.10); MUS = (0.40, 0.30)
P.set_pad(DEM['xf'], DEM['zf'])
DAF_ARM, DAF_BRIDGE, FLOOR = 1.97, 2.23, 1.5
# ---------------------------------------------------------------- geometry (drawn: wing.py constants), variants through GEO
GEO = dict(sock_W=0.018, flat_z=None, ring_RO_node=0.0105, ring_RO_cradle=W.CLAM_RING_R, pl_x=W.CLAM_PL_X, pl_hy=W.CLAM_PL_HY)
if VAR in ('V1', 'V12'): GEO['flat_z'] = 0.008
if VAR in ('V2', 'V12'): GEO['ring_RO_node'] = 0.008
if VAR in ('L1', 'L1V2'): GEO['pl_x'] = (0.0645, 0.108); GEO['pl_hy'] = 0.016      # plate trimmed to the socket face + 2 mm (x 64.5..108) and y +-16 mm
if VAR == 'L1V2': GEO['ring_RO_node'] = 0.008
if VAR.startswith('PL'):          # PL<x0 mm>_<halfwidth mm>, e.g. PL66.5_10 : plate x 66.5..108, y +-10
    a_, b_ = VAR[2:].split('_'); GEO['pl_x'] = (float(a_) * 1e-3, 0.108); GEO['pl_hy'] = float(b_) * 1e-3
YF = C.YFIN; SX = W.SPAR_X; ROD = W.RIB_OD
P.RX0 = W.RIB_X0; P.SAD_X0 = W.CLAM_X0; P.SAD_X1 = W.CLAM_X1; P.SAD_W = GEO['sock_W']; P.SAD_RO = GEO['ring_RO_cradle']; P.SAD_L = 0.060
ONYX_IN, ONYX_IL, ONYX_BEAR = 20e6, 9.5e6, 20e6          # EST, = PETG values (T-080 s1: Onyx only rows)
CF_PL = 600e6 * 0.70                                      # ACP PDS Dec 2014 x 0.70 EST (T-071b A.4)
BR_OD, BR_ID, BR_Z, XB0 = W.BR_OD, W.BR_ID, W.BR_Z, 0.030
P_Z_BR = math.pi / 64 * (BR_OD ** 4 - BR_ID ** 4) / (BR_OD / 2)
R = {}                                                    # (part, row) -> dict(rb=min RF at RB, case=...)
NODE_INFO = None


def put(part, row, arr, case):
    k = (part, row); v = float(np.min(arr))
    if k not in R or v < R[k]['rb']: R[k] = dict(rb=v, case=case)


def sock_section(W_=0.018, flat=None, D=0.014):
    """socket section W_ wide: box (flat None) or round OD W_ with flats at z +-flat; bore D.  A, Iy (about y, stress varies with z), Iz, extents, min wall."""
    h = 0.05e-3; xs = np.arange(-W_ / 2, W_ / 2, h) + h / 2; Y, Zg = np.meshgrid(xs, xs, indexing='ij')
    if flat is None: sol = (np.abs(Y) <= W_ / 2) & (np.abs(Zg) <= W_ / 2)
    else: sol = (Y ** 2 + Zg ** 2 <= (W_ / 2) ** 2) & (np.abs(Zg) <= flat)
    sec = sol & (Y ** 2 + Zg ** 2 >= (D / 2) ** 2); dA = h * h
    return dict(A=float(sec.sum() * dA), Iy=float((sec * Zg ** 2).sum() * dA), Iz=float((sec * Y ** 2).sum() * dA), zmax=float(np.abs(Zg[sec]).max()), ymax=float(np.abs(Y[sec]).max()),
                tw=(flat - D / 2) if flat is not None else (W_ - D) / 2)


SOCK = sock_section(GEO['sock_W'], GEO['flat_z'])


def run():
    for zeta in ZETAS:
        for mu in MUS:
            for nm in NAMES:
                key = '%.2f|%.2f|%s' % (zeta, mu, nm); FB = Z[key + '|FB'].astype(float); case = '%s z%.2f mu%.2f' % (nm, zeta, mu)
                # ---------------- CLAMSHELL / CRADLE (FIN-005, 007, 008): foot loads of one fin about the crossing S = (SX, +-YF, 0)
                for k in (0, 1):
                    F, M = P.M_about(FB, k, P.S_(k, SX, 0.0)); Fx, Fy, Fz = [np.abs(F[:, i]) for i in range(3)]; Mx, My, Mz = [np.abs(M[:, i]) for i in range(3)]
                    tp, wx, ly = W.CLAM_PL_T, GEO['pl_x'][1] - GEO['pl_x'][0], 2 * GEO['pl_hy']
                    zpl = W.CLAM_PL_Z if GEO['flat_z'] is None else GEO['flat_z']
                    az = 2 * (zpl + tp / 2)                                  # distance between the two plate mid-planes
                    Zin = 2 * tp * wx ** 2 / 6
                    sx = (My / az + Fx / 2) / (ly * tp) + Mz / Zin; sy = (Mx / az + Fy / 2) / (wx * tp) + Mz / Zin
                    put('Clamshell plates FIN-007 (CF 0.5)', 'CS1 plate x-direction stress (My couple, Fx/2, Mz in-plane)', CF_PL / (KF * np.maximum(sx, 1e-9)), case)
                    put('Clamshell plates FIN-007 (CF 0.5)', 'CS2 plate y-direction stress (Mx couple, Fy/2, Mz in-plane)', CF_PL / (KF * np.maximum(sy, 1e-9)), case)
                    # plate-to-cradle bond: contact = socket face (width sock_W, or the flat chord) x (CLAM_X1 - CLAM_X0) less the 3 boss holes (R 4, plates are cut round the bosses)
                    lx = W.CLAM_X1 - W.CLAM_X0
                    wface = GEO['sock_W'] if GEO['flat_z'] is None else 2 * math.sqrt((GEO['sock_W'] / 2) ** 2 - GEO['flat_z'] ** 2)
                    Ab = wface * lx - 3 * math.pi * min(W.CLAM_BR, wface / 2) ** 2
                    Jp = wface * lx * (wface ** 2 + lx ** 2) / 12; r = 0.5 * math.hypot(wface, lx)
                    tau = np.hypot(My / az + Fx / 2, Mx / az + Fy / 2) / Ab + (Mz / 2) * r / Jp
                    put('Clamshell plates FIN-007 (CF 0.5)', 'CS3 plate-to-cradle bond shear (contact %.0f mm2 per plate; T-071b used 1,875)' % (Ab * 1e6), P.BOND / (KP * np.maximum(tau, 1e-9)), case)
                    put('Clamshell plates FIN-007 (CF 0.5)', 'CS3p plate-to-cradle PEEL by Fz (integrity class, outside the minimum)', P.BOND / (KP * np.maximum(Fz / 2 / Ab, 1e-9)), case)
                    npin = len(W.CLAM_PX); V = Mx / ROD / npin
                    put('Clamshell pins FIN-008 (3 x 3 mm CF)', 'CS5 pin shear, double shear, rib torque Mx (3 pins)', P.PIN_TAU / np.maximum(V / (2 * P.PIN_A) * KP, 1e-9), case)
                    put('Cradle FIN-005 (PETG)', 'CS5b pin bearing in the 4 mm boss wall (3 pins)', P.PETG_BEAR / np.maximum(V / (P.PIN_D * W.CLAM_BR) * KP, 1e-9), case)
                    # cradle rows: landing_path_a P10 / P13 / P14 with the drawn constants (in-layer 20 MPa, build z-up)
                    sv = P.PETG_ILAY; P.PETG_ILAY = 20e6; res = P.checks(FB); P.PETG_ILAY = sv
                    for rk, (lab, a) in res.items():
                        if rk.startswith(('P10', 'P13', 'P14b')): put('Cradle FIN-005 (PETG)', rk + ' [in-layer]', a, case)
                    put('Cradle FIN-005 (PETG)', 'P14a spar 12x10 under the cradle ring with the skin torque share %.3f (bending in full), KF' % NODE_INFO['sh_spar'], P.tube_rf(F[:, 1], NODE_INFO['sh_spar'] * M[:, 1], np.hypot(M[:, 0], M[:, 2]), P.A_S, P.Z_S), case)
                    # socket wall at the mouth (P11 form on the drawn section) and the ring junction (P12 chord)
                    Sm = P.S_(k, W.CLAM_X1, 0.0); Fm, Mm = P.M_about(FB, k, Sm); tws = SOCK['tw']
                    Tb = 2 * math.pi * ((ROD / 2 + tws / 2) ** 2) * tws if GEO['flat_z'] else 2 * ((GEO['sock_W'] + ROD) / 2) ** 2 * tws
                    Zb = min(SOCK['Iy'] / SOCK['zmax'], SOCK['Iz'] / SOCK['ymax']); Mbn = np.hypot(Mm[:, 1], Mm[:, 2])
                    s_ = (Mbn / Zb + np.abs(Fm[:, 0]) / SOCK['A']) * KP; t_ = (np.abs(Mm[:, 0]) / Tb + np.hypot(Fm[:, 1], Fm[:, 2]) / (4 * GEO['sock_W'] * tws)) * KP
                    put('Cradle FIN-005 (PETG)', 'P11 socket wall at the mouth (wall %.2f mm, Z %.0f mm3), in-layer 20' % (tws * 1e3, Zb * 1e9), P.comb((s_, 20e6), (t_, 20e6)), case)
                    put('Cradle FIN-005 (PETG)', 'P11 same, interlayer 9.5 (shown only)', P.comb((s_, 9.5e6), (t_, 9.5e6)), case)
                    Sj = P.S_(k, W.CLAM_X0, 0.0); Fj, Mj = P.M_about(FB, k, Sj); a = P.chord(P.SAD_RO, P.SAD_X0 - SX)
                    for il, tag in ((20e6, 'in-layer 20'), (9.5e6, 'interlayer 9.5 (shown only)')):
                        rr = P.rect_rf(Fj[:, 0], np.hypot(Fj[:, 1], Fj[:, 2]), Mj[:, 0], Mj[:, 1], Mj[:, 2], GEO['sock_W'], a, il, il)
                        put('Cradle FIN-005 (PETG)', 'P12 socket-to-ring junction (%.1f x %.0f mm), %s' % (a * 1e3, GEO['sock_W'] * 1e3, tag), rr, case)
                    put('Rib FIN-002 (not a changed part, shown)', 'P9a rib tube 14x12 at the socket mouth x 108', P.tube_rf(Fm[:, 0], Mm[:, 0], np.hypot(Mm[:, 1], Mm[:, 2]), P.A_R, P.Z_R), case)
                # ---------------- R4 STRUT CLAMPS (CGE-007): strut axial from the same sims, bond over the drawn 25 mm socket
                sc = P.strut_checks(FB, Lb_clamp=0.025)
                for rk, (lab, a) in sc.items():
                    if rk.startswith(('STRUT bond at clamp', 'STRUT Euler pinned', 'STRUT tube')): put('Strut clamp CGE-007 R4 (PETG) + strut', rk, a, case)
                ux, uy, Ls = P._strut_geom()
                for k in (0, 1):
                    N = np.abs(np.sum([FB[:, 2 * k + j, 0] for j in (0, 1)], axis=0) / ux)
                    put('Strut clamp CGE-007 R4 (PETG) + strut', 'R4 socket wall axial (A 35.3 mm2: OD 9 / bore 6), in-layer 20 (axis in the print plane)', 20e6 / np.maximum(KP * N / 35.3e-6, 1e-9), case)
                    put('Strut clamp CGE-007 R4 (PETG) + strut', 'R4 socket wall axial, interlayer 9.5 (if printed standing; shown only)', 9.5e6 / np.maximum(KP * N / 35.3e-6, 1e-9), case)
                    Aj = math.pi / 4 * ((9e-3 + 2 * W.CLAMP_FIL * 1e-3) ** 2 - 6e-3 ** 2)
                    put('Strut clamp CGE-007 R4 (PETG) + strut', 'R4 socket-to-ring junction at the R %.1f fillet base (annulus OD %.0f / bore 6, Kt 2.0 EST), interlayer 9.5' % (W.CLAMP_FIL, 9 + 2 * W.CLAMP_FIL), 9.5e6 / np.maximum(KP * 2.0 * N / Aj, 1e-9), case)
                    Nx, Ny = N * ux, N * uy
                    tau_r = np.hypot(Ny / (math.pi * 0.012 * 0.016), (Nx * 0.010) / (2 * math.pi * 0.006 ** 2 * 0.016)) * KP
                    put('Strut clamp CGE-007 R4 (PETG) + strut', 'R4 ring bond on the spar (D12 x 16, Ny + torque Nx x 10 mm lever EST)', P.BOND / np.maximum(tau_r, 1e-9), case)
                # ---------------- NODE (X7): wing-half wrench into the node and hub-side wrench through the saddle bridge socket
                P0 = np.array([W.HUB_X1, 0.0, BR_Z])
                for half, k in (('R', 0), ('L', 1)):
                    Fh, Mh = Z[key + '|%s|F' % half].astype(float), Z[key + '|%s|M' % half].astype(float)

                    def My_at(x, zz=0.0):
                        d = P0 - np.array([x, 0.0, zz]); return (Mh + np.cross(np.broadcast_to(d, Fh.shape), Fh))[:, 1]
                    T = np.maximum(np.abs(My_at(SX)), np.abs(My_at(0.5 * C.C)))
                    Tsk = NODE_INFO['sh_skin'] * T; q = Tsk / (2 * NODE_INFO['A_cell'])
                    put('Node CGE-006/011/013 (X7 + CF plate)', 'N1 skin-to-plate lap bond (lap 5 mm EST; integrity class)', P.BOND / np.maximum(KP * q / 0.005, 1e-9), case)
                    pp = np.array(W.NODE_PINS); cen = pp.mean(0); rr = np.hypot(*(pp - cen).T); Fp = Tsk * rr.max() / (rr ** 2).sum()
                    put('Node pins CGE-012 (4 x 3 mm CF per side)', 'N3 pin shear, double shear, skin torque couple (r %.2f mm)' % (rr.max() * 1e3), P.PIN_TAU / np.maximum(Fp / (2 * P.PIN_A) * KP, 1e-9), case)
                    t_out, t_in = W.NODE_EAR_OUT[1] - W.NODE_EAR_OUT[0], W.NODE_EAR_IN[1] - W.NODE_EAR_IN[0]
                    put('Node ears CGE-006 inner / CGE-013 outer (Onyx)', 'N4 pin bearing in the %.1f mm outer clevis ear (F/2 per ear, Onyx 20)' % (t_out * 1e3), ONYX_BEAR / np.maximum((Fp / 2) / (P.PIN_D * t_out) * KP, 1e-9), case)
                    put('Node ears CGE-006 inner / CGE-013 outer (Onyx)', 'N4b pin bearing in the %.1f mm inner ear' % (t_in * 1e3), ONYX_BEAR / np.maximum((Fp / 2) / (P.PIN_D * t_in) * KP, 1e-9), case)
                    ax, az_ = W.NODE_X[1] - W.NODE_X[0], 2 * W.NODE_Z; Jp = ax * az_ * (ax ** 2 + az_ ** 2) / 12; rmax = 0.5 * math.hypot(ax, az_)
                    put('Node plate CGE-011 (CF 0.5) / ear bond', 'N2 plate-to-ear bond, 2 faces (%.1f x %.0f mm), polar moment (epoxy on Onyx "-": integrity class)' % (ax * 1e3, az_ * 1e3), P.BOND / np.maximum(KP * (Tsk / 2) * rmax / Jp, 1e-9), case)
                    Zear = t_in * az_ ** 2 / 6
                    put('Node ears CGE-006 inner / CGE-013 outer (Onyx)', 'N5 inner ear in-plane bending at the ring front x 49.5 (pins carry the couple; section %.0f x %.0f mm; the ear forward of the ring is joined only through the ring), in-layer 20' % (t_in * 1e3, az_ * 1e3), ONYX_IN / np.maximum(KP * Tsk / Zear, 1e-9), case)
                Fh, Mh = Z[key + '|hub|F'].astype(float), Z[key + '|hub|M'].astype(float)
                dN = P0 - np.array([SX, 0.0, 0.0]); MN = Mh + np.cross(np.broadcast_to(dN, Fh.shape), Fh)          # hub-side wrench at the node ring centre (the ring reacts it into the spar)
                Lr = 0.030; rb = P.bond_rf(Fh[:, 1], MN[:, 1], np.hypot(MN[:, 0], MN[:, 2]), np.hypot(Fh[:, 0], Fh[:, 2]), P.SOD, Lr)
                put('Node ring CGE-006 (Onyx) on the spar', 'N8 ring epoxy bond on spar D12 x 30: shear (axial + torsion)', rb[0], case)
                put('Node ring CGE-006 (Onyx) on the spar', 'N8 ring bond on spar D12 x 30: bearing, compression side (Onyx 20)', rb[1], case)
                put('Node ring CGE-006 (Onyx) on the spar', 'N8 ring bond on spar D12 x 30: BOND INTEGRITY / peel (epoxy on Onyx "-"; integrity class)', rb[2], case)
                Rm_ = (P.SOD + P.SID) / 4; tw_ = (P.SOD - P.SID) / 2; Pc = np.hypot(Fh[:, 0], Fh[:, 2])
                put('Node ring CGE-006 (Onyx) on the spar', 'N8c spar wall diametral crush under the 30 mm ring (hoop 40 MPa EST)', P.SPAR_HOOP / np.maximum(6 * 0.318 * Pc * Rm_ / (Lr * tw_ ** 2) * KF, 1e-9), case)
                dJ = P0 - np.array([0.0535, 0.0, BR_Z]); MJ = Mh + np.cross(np.broadcast_to(dJ, Fh.shape), Fh); aJ = P.chord(GEO['ring_RO_node'], 0.0535 - SX)
                put('Node ring CGE-006 (Onyx) on the spar', 'N9 socket-to-ring junction at x 53.5 (%.1f x 21 mm: ring chord x socket width), in-layer 20' % (aJ * 1e3), P.rect_rf(Fh[:, 0], np.hypot(Fh[:, 1], Fh[:, 2]), MJ[:, 0], MJ[:, 1], MJ[:, 2], 0.021, aJ, ONYX_IN, ONYX_IN), case)
                for xs_, lab in ((XB0, 'forward end x 30'), (0.050, 'ring face x 50')):
                    d = P0 - np.array([xs_, 0.0, BR_Z]); Ms = Mh + np.cross(np.broadcast_to(d, Fh.shape), Fh); Mt = np.hypot(Ms[:, 1], Ms[:, 2]); Vt = np.hypot(Fh[:, 1], Fh[:, 2])
                    if lab.startswith('forward'):
                        Lb = 0.0235
                        put('Node bridge socket CGE-006 (Onyx)', 'N6 bridge bearing in the 23.5 mm socket (6M/(D L^2)+V/(D L), M at the mouth, Onyx 20)', ONYX_BEAR / np.maximum(KP * (6 * Mt / Lb ** 2 + Vt / Lb) / BR_OD, 1e-9), case)
                        put('Node bridge socket CGE-006 (Onyx)', 'N6b bridge-in-socket bond, axial + torque (epoxy on Onyx "-", integrity class)', P.BOND / np.maximum(KP * np.hypot(np.abs(Fh[:, 0]) / (math.pi * BR_OD * Lb), np.abs(Ms[:, 0]) / (2 * math.pi * (BR_OD / 2) ** 2 * Lb)), 1e-9), case)
                    Zs = (21e-3 ** 4 / 12 - math.pi * BR_OD ** 4 / 64) / (10.5e-3)
                    put('Node bridge socket CGE-006 (Onyx)', 'N7 socket net section under M at the %s (box 21 x 21 less bore 16, Z %.0f mm3; ears not effective), in-layer 20, no fibre' % (lab, Zs * 1e9), ONYX_IN / np.maximum(KP * Mt / Zs, 1e-9), case)
                    put('Bridge tube 16x14 (CF, not a changed part)', 'B1 bridge bending at the %s (350 MPa EST, KF)' % lab, 350e6 / np.maximum(KF * Mt / P_Z_BR, 1e-9), case)
                    if lab.startswith('forward'): put('Hub-side wrench (demand record)', 'max |M| (My, Mz) at x 30 [N m, x1000 in the RF columns: not an RF]', 1e3 / np.maximum(Mt, 1e-9), case)


def main():
    global NODE_INFO
    np.seterr(all='ignore'); key0 = '0.05|0.40|%s' % NAMES[0]
    NODE_INFO = P.wing_checks_skin(Z[key0 + '|FB'].astype(float), P.skin_variants()[0][1])[1]
    print('# T-077 p6 strength rows, variant %s. Demand: chosen pad Fp %.0f N / %.0f mm, mass %.3f kg, CG %.2f mm, 23 cases x zeta 0.02/0.05/0.10 x mu 0.40/0.30; KF %.3f KP %.3f' % (VAR, DEM['Fp'], DEM['smax'] * 1e3, DEM['mass'], DEM['cg'][0] * 1e3, KF, KP))
    print('# skin torque share %.3f, cell area %.0f mm2; socket section %s' % (NODE_INFO['sh_skin'], NODE_INFO['A_cell'] * 1e6, {k: float('%.5g' % v) for k, v in SOCK.items()}))
    run()
    out = []
    print('\n| part | row | RB | x1.5 | x1.97 | x2.23 | governing case |\n|---|---|---|---|---|---|---|')
    for (part, row), v in sorted(R.items(), key=lambda kv: (kv[0][0], kv[1]['rb'])):
        rb = v['rb']
        if row.startswith('max |M|'): print('| %s | peak hub-side |M| at x 30 = %.2f N m (RB) | | | | %s |' % (part, 1e3 / rb, v['case'])); continue
        print('| %s | %s | %.2f | %.2f | %.2f | %.2f | %s |' % (part, row, rb, rb / FLOOR, rb / DAF_ARM, rb / DAF_BRIDGE, v['case']))
        out.append(dict(part=part, row=row, rb=rb, case=v['case']))
    json.dump(out, open(os.path.join(HERE, 'strength_%s.json' % VAR), 'w'), indent=1)


if __name__ == '__main__': main()
