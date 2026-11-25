"""T-077 p8 (D-226 implementation, AM-016): strength table of every NEW and CHANGED part of the torsion-cell landing path, on the T-077 p6 landing demand
(T077p6_data/demand_p6.json + the git-ignored T077p6_data/fea/demand_p6.npz: 23 cases x pad zeta 0.02 / 0.05 / 0.10 x face mu 0.40 / 0.30, 1.705 kg, CG 23.91 mm).
Category: rigid-body dynamics (the p6 demand, NOT re-run) + HAND CALCULATION (statics, thin-wall torsion, bonded-joint line loads, beam bending). No FEA.
    python -I t077p8_path.py [--tag T] [--slv_a A_mm] [--fil_w W_mm] [--rib OD,ID]       -> strength_<tag>.json / .txt   (about 1 min)
Defaults = the drawn tree (cad/amodel/wing.py constants: RIB_OD/ID, RIB_Y, FNB_*, CN_*, STRAP_*).
Factors and limits (CLAUDE.md, D-223, never relaxed): KF 1.725 (CF, 6061), KP 2.156 (bonds, printed), RF >= 1.0 at max(DAF, 1.5) = 2.23 for every row here
(D-223: bridge and interim wing / saddle / fin value; the new node parts are wing / saddle class, the audit judged them at 2.23; 1.97 would be the tube / bond value: 2.23 used throughout, conservative).
Allowables (EST unless a source is named): epoxy bond 2.0 MPa (structures_a.py BOND_TAU, landing_path_a.BOND); CF tube 350 / 30 MPa (landing_path_a SIG / TAU);
skin laminate = landing_path_a.skin_laminate(n=3): ACP Composites PDS Dec 2014 (read 2026-11-19) +-45 S 100 MPa x Vf scaling 0.70 = 70 MPa per ply, wet ply 0.0537 mm;
0/90 glass strap X 425 x 0.70 = 297 MPa (same PDS, same scaling); CF bulkhead / plate in-plane shear: no CF plate allowable in the repo -> the glass +-45 S 70 MPa is used as a LOWER BOUND (EST, D-226 s3);
6061-T6 yield 240 MPa minimum (en.wikipedia.org/wiki/6061_aluminium_alloy, read 2026-11-20, T-080 s1; secondary), judged von Mises x KF <= 240;
6061-T6 BEARING yield: see BEAR_6061 below (source and date there).
Each row is the minimum over all cases, zeta, mu, fins and time steps of the CONCURRENT per-time-step combination (not an envelope of separate maxima)."""
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
P6 = os.path.abspath(os.path.join(HERE, '..', 'T077p6_data'))
S_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures'))
os.environ['LAND_MASS_KG'] = '1.705'; os.environ['LAND_CG_X_MM'] = '23.91'; os.environ['LAND_MASS_MODEL'] = 'cad'
sys.path.insert(0, S_DIR); sys.dont_write_bytecode = True
import numpy as np
import landing_path_a as P
W, C = P.W, P.C
A = sys.argv


def arg(k, d):
    return A[A.index(k) + 1] if k in A else d


TAG = arg('--tag', 'drawn')
KF, KP, BOND = P.KF, P.KP, P.BOND
DAF = 2.23                                     # D-223 interim wing / bridge value = max(DAF, 1.5) for every row here
Y6061 = 240e6                                  # 6061-T6 tensile yield, minimum (T-080 s1, secondary source)
BEAR_6061 = 386e6                              # 6061-T6 bearing yield, typical, e/D = 2.0: Aerospace Specification Metals "Aluminum 6061-T6; 6061-T651" data sheet (MatWeb data),
                                               # https://www.aerospacemetals.com/wp-content/uploads/2023/06/Aluminum-6061-T6-6061-T651.pdf read 2026-11-21 (PDF text: "Bearing Yield Strength 386 MPa ... Edge distance/pin
                                               # diameter = 2.0"); a pin-bearing value applied to the socket wall: EST applicability. asm.matweb.com refused the connection 2026-11-21.
S_PM45 = 70e6                                  # glass +-45 in-plane shear per landing_path_a.skin_laminate (ACP x 0.70): LOWER BOUND for the 0.5 mm CF sheet (EST)
X_090 = P.ACP['c090']['X'] * 0.70              # 0/90 glass strap tension allowable (ACP x 0.70) = 297.5 MPa
T_PLY = P.skin_laminate(1)['t']                # 0.0537 mm wet ply
DEM = json.load(open(os.path.join(P6, 'demand_p6.json'))); Z = np.load(os.path.join(P6, 'fea', 'demand_p6.npz'), allow_pickle=True)
NAMES = [str(n) for n in Z['names']]; ZETAS = (0.02, 0.05, 0.10); MUS = (0.40, 0.30)
P.set_pad(DEM['xf'], DEM['zf'])
P0 = np.array([-0.045 + C.CAGE_DX, 0.0, -0.002])  # = T2.ctx P0 at demand time (W.HUB_X1, 0, W.BR_Z): the hub / R / L wrenches are about it

# ---------------------------------------------------------------- geometry (drawn tree from wing.py; switches for sizing)
SX = C.SPAR_X
ro_, ri_ = [float(v) * 1e-3 for v in arg('--rib', '%g,%g' % (W.RIB_OD * 1e3, W.RIB_ID * 1e3)).split(',')]
RIB_Y = W.RIB_Y                                # rib axis |y| (YFIN + 3 mm, hinge-damper clearance)
RX0, XE = W.RIB_X0, W.FNB_X1                   # rib front end, end of the bulkhead / fillet bond (node exit)
LB = XE - RX0                                  # rib-to-bulkhead bond length
FIL_W = float(arg('--fil_w', W.FNB_FIL_W * 1e3)) * 1e-3   # flox fillet width per rib flank (EST: cusp filled to |dz| <= 6 mm)
D_FIL = 2 * (ro_ / 2 + W.FNB_GAP)              # fillet line spacing (rib flank to flank)
LAP = 0.008                                    # bulkhead / strap lap on the skin (D-226 s3: 2-ply 1080 tape, 8 mm)
N_PLY = W.SKIN_N                               # skin plies over the torsion bay
LAM = P.skin_laminate(n=N_PLY)
TB = W.FNB_T                                   # CF bulkhead / plate thickness 0.5 mm
STRAP_PLY = 4                                  # rib strap: 4 plies 0/90 1080 over the rib top and bottom (D-226 s3 "4-ply 0/90 wrap")
PL_X, PL_HY = W.FNP_X, W.FNP_HY                # in-plane plates x range, half width
# centre node CGE-006 (one machined 6061 part): octagonal sleeve, end flanges, bridge socket boss
SLV_A = float(arg('--slv_a', W.CN_SLV_A * 1e3)) * 1e-3
SLV_RB = W.CN_BORE / 2
FL_T, FL_X, FL_Z = W.CN_FL_T, W.CN_FL_X, W.CN_FL_Z
SK_X0, SK_X1, SK_RO, SK_RI = W.CN_SK_X0, W.BR_X1, W.CN_SK_RO, W.BR_RO + 0.00005
BR_OD, BR_ID, BR_Z = W.BR_OD, W.BR_ID, W.BR_Z
Z_BR = math.pi / 64 * (BR_OD ** 4 - BR_ID ** 4) / (BR_OD / 2)


def poly_area(l):
    return abs(sum(l[i][0] * l[(i + 1) % len(l)][1] - l[(i + 1) % len(l)][0] * l[i][1] for i in range(len(l))) / 2)


def clip_x(loop, x1):
    """Sutherland-Hodgman clip of a closed (x, z) loop to x <= x1."""
    out = []
    for i in range(len(loop)):
        a, b = loop[i - 1], loop[i]
        ia, ib = a[0] <= x1, b[0] <= x1
        if ib:
            if not ia:
                t = (x1 - a[0]) / (b[0] - a[0]); out.append((x1, a[1] + t * (b[1] - a[1])))
            out.append(b)
        elif ia:
            t = (x1 - a[0]) / (b[0] - a[0]); out.append((x1, a[1] + t * (b[1] - a[1])))
    return out


INNER = W._offset_loop(W.core_loop(), N_PLY * W.SKIN_T)       # skin inner face over the torsion bay
A_FIN = poly_area(clip_x(INNER, XE))                          # cell area closed by the fin bulkheads (to x 176: they stop ahead of the hinge-damper notch)
A_CEN = poly_area(INNER)                                      # cell area at the centre bulkheads (full section to the cove)
A_FIN_AUDIT = 3389e-6


def grid_props(pred, x0, x1, z0, z1, xc, zc, h=0.25e-3):
    """area, polar J about (xc, zc), Ixx (about the x-axis line: int (z-zc)^2), Izz (int (x-xc)^2), r_max of a 2-D region pred(X, Z) by grid."""
    xs = np.arange(x0 + h / 2, x1, h); zs = np.arange(z0 + h / 2, z1, h); X, Zg = np.meshgrid(xs, zs, indexing='ij'); m = pred(X, Zg)
    dx, dz = X[m] - xc, Zg[m] - zc; a = h * h
    return dict(A=m.sum() * a, Ix=(dz ** 2).sum() * a, Iz=(dx ** 2).sum() * a, J=((dx ** 2 + dz ** 2).sum()) * a, rmax=float(np.sqrt(dx ** 2 + dz ** 2).max()),
                xmax=float(np.abs(dx).max()), zmax=float(np.abs(dz).max()))


# flange outline: section interior (skin + 0.3 mm), x FL_X, |z| <= FL_Z, minus the sleeve bore and the I2C hole (left flange; taken on both: conservative)
def _flange(X, Zg):
    zu_ = np.vectorize(C.zu)(X[:, 0])[:, None]; zl_ = np.vectorize(C.zl)(X[:, 0])[:, None]
    m = (Zg <= np.minimum(FL_Z, zu_ - N_PLY * W.SKIN_T - 0.0003)) & (Zg >= np.maximum(-FL_Z, zl_ + N_PLY * W.SKIN_T + 0.0003))
    m &= (X - SX) ** 2 + Zg ** 2 > SLV_RB ** 2
    m &= (X - W.CN_I2C[0]) ** 2 + (Zg - W.CN_I2C[1]) ** 2 > (W.CN_I2C_D / 2) ** 2
    return m


FLG = grid_props(_flange, FL_X[0], FL_X[1], -0.012, 0.013, SX, 0.0)
# plate (FIN-009): x PL_X, y +-PL_HY about the rib axis, less the rib notch (full rib width: worst case, x from RX0)
PLT = grid_props(lambda X, Yg: ~((np.abs(Yg) < ro_ / 2) & (X >= RX0)), PL_X[0], PL_X[1], -PL_HY, PL_HY, sum(PL_X) / 2, 0.0)
PLT_C = None


def octagon(a):
    rc = a / math.cos(math.pi / 8)
    return [(rc * math.cos(math.pi / 8 + k * math.pi / 4), rc * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]


def slv_props(a, rb):
    """thin-wall closed-section torsion (Bredt) + bending of the octagonal sleeve less the round bore."""
    t = a - rb                                                 # wall at the flats (thinnest)
    am = a - t / 2; Am = 8 * am * am * math.tan(math.pi / 8)
    g = grid_props(lambda X, Yg: (np.maximum(np.maximum(np.abs(X), np.abs(Yg)), (np.abs(X) + np.abs(Yg)) / math.sqrt(2)) <= a) & (X * X + Yg * Yg > rb * rb),
                   -a * 1.1, a * 1.1, -a * 1.1, a * 1.1, 0.0, 0.0, h=0.05e-3)
    return dict(t=t, Am=Am, A=g['A'], I=g['Ix'], Z=g['Ix'] / (a / math.cos(math.pi / 8)))


SLV = slv_props(SLV_A, SLV_RB)
BOSS_A = math.pi * (SK_RO ** 2 - SK_RI ** 2); BOSS_Z = math.pi / 4 * (SK_RO ** 4 - SK_RI ** 4) / SK_RO
R = {}
REC = {}


def rec(part, row, arr, case):
    k = (part, row); v = float(np.nanmax(arr))
    if k not in REC or v > REC[k]['val']: REC[k] = dict(val=v, case=case)


def put(part, row, arr, case, cls='RF'):
    k = (part, row); v = float(np.nanmin(arr))
    if k not in R or v < R[k]['rb']: R[k] = dict(rb=v, case=case, cls=cls)


PN = 'Fin node FIN-005 (2 CF bulkheads 0.5 mm) + FIN-009 (2 CF in-plane plates 0.5 mm) + rib straps (4-ply 0/90 glass, undrawn laminate)'
PR = 'Rib FIN-002 %.0fx%.0f CF' % (ro_ * 1e3, ri_ * 1e3)
PS = 'Skin WNG-011 + WNG-014: %d plies 48 g/m2 glass +-45 over |y| 0.052-0.400' % N_PLY
PC = 'Centre node CGE-006 (one machined 6061-T6 part: octagonal sleeve apothem %.1f mm, bore %.1f, flanges %.1f mm, bridge socket boss OD %.1f) + bulkheads WNG-013' % (SLV_A * 1e3, SLV_RB * 2e3, FL_T * 1e3, SK_RO * 2e3)
PB = 'Bridge CGE-004 16x14 (CF; shortened to x %.1f)' % (SK_X1 * 1e3)
PK = 'Root block FIN-003 (PETG, socket %.0f x %.0f for the %.0f mm rib; drawn block, not the tallied enlargement)' % (2 * W.BLK_SH * 1e3, 2 * W.BLK_SH * 1e3, ro_ * 1e3)


def My_cell(FB, k, y):
    """torque about the y axis put into the cell by fin k: the worse of the spar axis and mid-chord reference lines (as landing_path_a.wing_checks_skin)."""
    a = np.abs(P.M_about(FB, k, (SX, y, 0.0))[1][:, 1]); b = np.abs(P.M_about(FB, k, (0.5 * C.C, y, 0.0))[1][:, 1])
    return np.maximum(a, b)


def run():
    A_R = math.pi / 4 * (ro_ ** 2 - ri_ ** 2); Z_R = math.pi / 32 * (ro_ ** 4 - ri_ ** 4) / ro_
    lam = LAM; tsk = lam['t']; wr1 = 0.5 * (lam['E1'] * P.E_F * P.G_F) ** (1 / 3)
    slv_skin = P.skin_variants()[0][1]; slv_skin = dict(slv_skin, lam=lam)
    for zeta in ZETAS:
        for mu in MUS:
            for nm in NAMES:
                key = '%.2f|%.2f|%s' % (zeta, mu, nm); FB = Z[key + '|FB'].astype(float); case = '%s z%.2f mu%.2f' % (nm, zeta, mu)
                for k in (0, 1):
                    sg = 1 if k == 0 else -1; yr = sg * RIB_Y
                    T = My_cell(FB, k, yr)
                    # ---- fin node: torque into the cell through the two bulkheads
                    q = KP * DAF * T / (2 * A_FIN)
                    put(PN, 'N1 bulkhead-to-skin tape lap (2 bulkheads, 8 mm lap each, q / 2 per bulkhead), epoxy 2.0 MPa', BOND / np.maximum(q / 2 / LAP, 1e-9) * DAF, case)
                    put(PN, 'N2 bulkhead in-plane shear (2 x 0.5 mm CF), glass +-45 S 70 MPa as the lower bound (EST)', S_PM45 / np.maximum(q / (2 * TB), 1e-9) * DAF, case)
                    F, M = P.M_about(FB, k, (XE, yr, 0.0))
                    wz = 0.5 * (6 * np.abs(M[:, 1]) / LB ** 2 + np.abs(F[:, 2]) / LB) + np.abs(M[:, 0]) / (D_FIL * LB)
                    put(PN, 'N3 rib-to-bulkhead flox fillet, per flank (My, Fz, rib torsion Mx as a z-couple), L %.1f mm, width %.0f mm (EST), epoxy 2.0' % (LB * 1e3, FIL_W * 1e3),
                        BOND / np.maximum(KP * wz / FIL_W, 1e-9), case)
                    wy = 6 * np.abs(M[:, 2]) / LB ** 2 + np.abs(F[:, 1]) / LB
                    put(PN, 'N4a rib strap laps on the skin (Mz, Fy; one 8 mm lap per strap, 2 straps), epoxy 2.0', BOND / np.maximum(KP * wy / (2 * LAP), 1e-9), case)
                    put(PN, 'N4b rib strap tension (4 plies 0/90, X %.0f MPa, ACP x 0.70), half of w_y per strap' % (X_090 * 1e-6), X_090 * STRAP_PLY * T_PLY / np.maximum(KP * wy / 2, 1e-9), case)
                    Fp, Mp = P.M_about(FB, k, (sum(PL_X) / 2, yr, 0.0))
                    put(PN, 'N5 in-plane plates bonded on the skin, polar group (Mz at the plate centroid; 2 plates, area %.0f mm2 each less the rib notch, J %.2e mm4)' % (PLT['A'] * 1e6, PLT['J'] * 1e12),
                        BOND / np.maximum(KP * np.abs(Mp[:, 2]) * PLT['rmax'] / (2 * PLT['J']) + KP * np.hypot(Fp[:, 0], Fp[:, 1]) / (2 * PLT['A']), 1e-9), case)
                    put(PN, 'N6 skin + plate in-plane shear at the strap lap line (w_y spread both ways, 2 surfaces, 3-ply skin + 0.5 mm plate), S 70 MPa lower bound (EST)',
                        S_PM45 / np.maximum(KP * wy / (2 * 2 * (tsk + TB)), 1e-9), case)
                    # ---- rib tube at the node exit and at the root-block mouth
                    put(PR, 'R1 rib tube at the node exit x %.0f (axial Fx, torsion Mx, bending hypot(My, Mz)), CF 350 / 30, KF' % (XE * 1e3), P.tube_rf(F[:, 0], M[:, 0], np.hypot(M[:, 1], M[:, 2]), A_R, Z_R), case)
                    Fm, Mm = P.M_about(FB, k, (W.BLK_X0, yr, 0.0))
                    put(PR, 'R2 rib tube at the root-block mouth x %.0f, KF' % (W.BLK_X0 * 1e3), P.tube_rf(Fm[:, 0], Mm[:, 0], np.hypot(Mm[:, 1], Mm[:, 2]), A_R, Z_R), case)
                    # ---- root block with the new rib (landing_path_a P5-P8 formulas, drawn block)
                    Bw = 2 * W.BLK_SH; RX1 = W.RIB_X1; XT = C.XFIN_T
                    S0 = P.S_(k, XT, 0.0); F5, M5 = P.M_about(FB, k, S0)
                    b5 = P.bond_rf(F5[:, 2], M5[:, 2], np.hypot(M5[:, 0], M5[:, 1]), np.hypot(F5[:, 0], F5[:, 1]), C.FIN_OD, P.RING_BL_L)
                    put(PK, 'P5 ring epoxy bond on the fin tube (D16 x 60): shear', b5[0], case)
                    put(PK, 'P5 ring bond: bearing, compression side (PETG 20)', b5[1], case)
                    F6, M6 = P.M_about(FB, k, (RX1, yr, 0.0)); a6 = P.chord(P.RING_BL_RO, XT - RX1)
                    put(PK, 'P6 ring-to-socket junction (%.1f x %.0f mm), interlayer 9.5' % (a6 * 1e3, Bw * 1e3), P.rect_rf(F6[:, 0], np.hypot(F6[:, 1], F6[:, 2]), M6[:, 0], M6[:, 1], M6[:, 2], a6, Bw, P.PETG_ILAY, P.PETG_ILAY), case)
                    b7 = P.bond_rf(Fm[:, 0], Mm[:, 0], np.hypot(Mm[:, 1], Mm[:, 2]), np.hypot(Fm[:, 1], Fm[:, 2]), ro_, RX1 - W.BLK_X0)
                    put(PK, 'P7 socket: rib epoxy bond (D%.0f x %.0f): shear' % (ro_ * 1e3, (RX1 - W.BLK_X0) * 1e3), b7[0], case)
                    put(PK, 'P7 socket: rib bearing, compression side (PETG 20)', b7[1], case)
                    Ib = Bw ** 4 / 12 - math.pi * ro_ ** 4 / 64; Zb = Ib / (Bw / 2); tw = (Bw - ro_) / 2; Tb = 2 * ((Bw + ro_) / 2) ** 2 * tw
                    s = (np.hypot(Mm[:, 1], Mm[:, 2]) / Zb + np.abs(Fm[:, 0]) / (Bw ** 2 - math.pi * ro_ ** 2 / 4)) * KP; t = (np.abs(Mm[:, 0]) / Tb + np.hypot(Fm[:, 1], Fm[:, 2]) / (4 * Bw * tw)) * KP
                    put(PK, 'P8 socket wall, PETG box %.0f / bore %.0f, bending + torsion, interlayer 9.5' % (Bw * 1e3, ro_ * 1e3), P.comb((s, P.PETG_ILAY), (t, P.PETG_ILAY)), case)
                    # ---- skin cell at the fin node (all the torque in the skin: the bulkheads put it into the cell; GJ share ignored = conservative)
                    tk = KP * T / (2 * A_FIN) / tsk
                    put(PS, 'K1 skin shear at the fin node (T / 2A, all torque in the skin), S %.0f MPa' % (lam['S'] * 1e-6), lam['S'] / np.maximum(tk, 1e-9), case)
                    put(PS, 'K2 skin wrinkling, torsion (0.5 (E1 Ef Gf)^(1/3) = %.2f MPa, EST formula)' % (wr1 * 1e-6), wr1 / np.maximum(tk, 1e-9), case)
                # ---- centre: half-wing wrenches (R, L) and hub wrench about the spar axis
                Fh, Mh = Z[key + '|hub|F'].astype(float), Z[key + '|hub|M'].astype(float)
                Sx = np.array([SX, 0.0, 0.0]); dN = P0 - Sx
                MH = Mh + np.cross(np.broadcast_to(dN, Fh.shape), Fh)
                for side in ('R', 'L'):
                    Fs, Ms = Z[key + '|%s|F' % side].astype(float), Z[key + '|%s|M' % side].astype(float)
                    MS = Ms + np.cross(np.broadcast_to(dN, Fs.shape), Fs); Th = np.abs(MS[:, 1])
                    tau = Th / (2 * SLV['Am'] * SLV['t']); sb = 0.5 * np.hypot(MH[:, 0], MH[:, 2]) / SLV['Z']
                    put(PC, 'C1 sleeve: torsion (Bredt, wall %.2f mm at the flats) + bending (half the hub Mx, Mz at the spar axis), von Mises x KF <= 240' % (SLV['t'] * 1e3),
                        Y6061 / np.maximum(KF * np.sqrt(sb ** 2 + 3 * tau ** 2), 1e-9), case)
                    tj = Th / (2 * math.pi * SLV_A ** 2 * FL_T)
                    put(PC, 'C2 sleeve-to-flange junction (integral, %.1f mm flange round the sleeve), von Mises x KF' % (FL_T * 1e3), Y6061 / np.maximum(KF * math.sqrt(3) * tj, 1e-9), case)
                    put(PC, 'C3 flange-to-bulkhead bond, polar shear (T_half; flange area %.0f mm2, J %.2e mm4, r %.1f mm), epoxy 2.0' % (FLG['A'] * 1e6, FLG['J'] * 1e12, FLG['rmax'] * 1e3),
                        BOND / np.maximum(KP * Th * FLG['rmax'] / FLG['J'], 1e-9), case)
                    sp = KP * (0.5 * np.abs(MH[:, 2]) * FLG['xmax'] / FLG['Iz'] + 0.5 * np.abs(MH[:, 0]) * FLG['zmax'] / FLG['Ix'])
                    put(PC, 'C3p flange bond peel from the out-of-plane share (half the hub Mz, Mx; integrity class)', BOND / np.maximum(sp, 1e-9), case, cls='integrity')
                    qc = KP * Th / (2 * A_CEN)
                    put(PC, 'C4 centre bulkhead-to-skin tape lap (one bulkhead per side, 8 mm lap; outboard lap only below: the flange slit), epoxy 2.0', BOND / np.maximum(qc / LAP, 1e-9), case)
                    put(PC, 'C5 centre bulkhead in-plane shear (0.5 mm CF), S 70 MPa lower bound (EST)', S_PM45 / np.maximum(qc / TB, 1e-9), case)
                    tkc = qc / tsk
                    put(PS, 'K3 skin shear at the centre bulkheads (T_half / 2A), S %.0f MPa' % (lam['S'] * 1e-6), lam['S'] / np.maximum(tkc, 1e-9), case)
                # bridge socket boss and bridge
                for xs_, lab in ((SK_X0, 'mouth x %.1f' % (SK_X0 * 1e3)), (SK_X1, 'socket end x %.1f' % (SK_X1 * 1e3))):
                    d = P0 - np.array([xs_, 0.0, BR_Z]); Mx_ = Mh + np.cross(np.broadcast_to(d, Fh.shape), Fh); Mt = np.hypot(Mx_[:, 1], Mx_[:, 2]); Vt = np.hypot(Fh[:, 1], Fh[:, 2])
                    if lab.startswith('mouth'):
                        Lb = SK_X1 - SK_X0; sbear = 6 * Mt / (BR_OD * Lb ** 2) + Vt / (BR_OD * Lb)
                        put(PC, 'C7 6061 socket wall bearing under the bridge (6M/(D L^2) + V/(D L), D 16, L %.0f), bearing yield 386 MPa (ASM / aerospacemetals.com data sheet, typical, e/D 2.0, read 2026-11-21), KF' % (Lb * 1e3),
                            BEAR_6061 / np.maximum(KF * sbear, 1e-9), case)
                        rec(PB, 'B2 bridge CF wall bearing stress in the 6061 socket at x2.23 x KF [MPa]; CF bearing allowable "-" (TP-4 coupon)', DAF * KF * sbear * 1e-6, case)
                        put(PB, 'B1 bridge bending at the socket %s (350 MPa EST, KF)' % lab, 350e6 / np.maximum(KF * Mt / Z_BR, 1e-9), case)
                        put(PB, 'B3 bridge-in-socket bond, axial + torque (integrity class)', BOND / np.maximum(KP * np.hypot(np.abs(Fh[:, 0]) / (math.pi * BR_OD * Lb), np.abs(Mx_[:, 0]) / (2 * math.pi * (BR_OD / 2) ** 2 * Lb)), 1e-9), case, cls='integrity')
                    else:
                        put(PC, 'C6 socket boss annulus (OD %.1f / %.1f) at the %s: bending hypot(My, Mz) + axial, von Mises x KF' % (SK_RO * 2e3, SK_RI * 2e3, lab),
                            Y6061 / np.maximum(KF * (Mt / BOSS_Z + np.abs(Fh[:, 0]) / BOSS_A), 1e-9), case)
                rec('Demand record', 'max hub |My| at the spar axis [N m, RB]', np.abs(MH[:, 1]), case)
                for side in ('R', 'L'):
                    Fs, Ms = Z[key + '|%s|F' % side].astype(float), Z[key + '|%s|M' % side].astype(float)
                    rec('Demand record', 'max half-wing |My| at the spar axis (sleeve / flange torque T_half) [N m, RB]', np.abs((Ms + np.cross(np.broadcast_to(dN, Fs.shape), Fs))[:, 1]), case)
                for k in (0, 1):
                    rec('Demand record', 'max fin |My| into the cell at the rib axis [N m, RB]', My_cell(FB, k, (1 if k == 0 else -1) * RIB_Y), case)
                    F_, M_ = P.M_about(FB, k, (XE, (1 if k == 0 else -1) * RIB_Y, 0.0))
                    for j_, n_ in enumerate(('Mx', 'My', 'Mz')): rec('Demand record', 'max rib %s at the node exit x %.0f [N m, RB]' % (n_, XE * 1e3), np.abs(M_[:, j_]), case)
                # wing cell P15 / P16 with the n-ply skin (landing_path_a.wing_checks_skin, V0 settings: no relief, strip, truss)
                res, info = P.wing_checks_skin(FB, slv_skin)
                for rk, (lab, a) in res.items():
                    if any(s_ in rk for s_ in ('P15 spar torsion', 'P15 foam shear', 'P16 spar', 'P16 foam', 'P16 cove', 'P15 skin shear+axial')):
                        put('Wing section (landing_path_a P15 / P16, %d-ply skin, GJ share; outboard stations unchanged)' % N_PLY, rk, a, case)


def main():
    np.seterr(all='ignore')
    print('# T-077 p8 torsion-cell path rows, tag %s. Demand (T-077 p6, not re-run): Fp %.0f N / %.0f mm, %.3f kg, CG %.2f mm; KF %.3f KP %.3f; verdict at x%.2f' % (TAG, DEM['Fp'], DEM['smax'] * 1e3, DEM['mass'], DEM['cg'][0] * 1e3, KF, KP, DAF))
    print('# cell area fin (to x %.0f) %.0f mm2 (audit 3,389 to the hinge), centre %.0f mm2; skin %d plies t %.3f mm S %.0f MPa; flange area %.0f mm2 J %.3e mm4 rmax %.1f; plate area %.0f mm2 J %.3e rmax %.1f; sleeve a %.2f t %.2f Am %.1f mm2 Z %.1f mm3 area %.1f mm2'
          % (XE * 1e3, A_FIN * 1e6, A_CEN * 1e6, N_PLY, LAM['t'] * 1e3, LAM['S'] * 1e-6, FLG['A'] * 1e6, FLG['J'] * 1e12, FLG['rmax'] * 1e3, PLT['A'] * 1e6, PLT['J'] * 1e12, PLT['rmax'] * 1e3,
             SLV_A * 1e3, SLV['t'] * 1e3, SLV['Am'] * 1e6, SLV['Z'] * 1e9, SLV['A'] * 1e6))
    run()
    out = []
    print('\n| part | row | RB | x1.5 | x2.23 | verdict at x2.23 | governing case |\n|---|---|---|---|---|---|---|')
    for (part, row), v in sorted(R.items(), key=lambda kv: (kv[0][0], kv[1]['rb'])):
        rb = v['rb']
        vd = ('integrity class: %s' % ('>= 1' if rb / DAF >= 1 else '< 1')) if v['cls'] == 'integrity' else ('PASS' if rb / DAF >= 1 else 'FAIL')
        print('| %s | %s | %.2f | %.2f | %.2f | %s | %s |' % (part, row, rb, rb / 1.5, rb / DAF, vd, v['case']))
        out.append(dict(part=part, row=row, rb=rb, x15=rb / 1.5, x223=rb / DAF, cls=v['cls'], verdict=vd, case=v['case']))
    for (part, row), v in sorted(REC.items()):
        print('| %s | %s = %.2f | | | | record | %s |' % (part, row, v['val'], v['case'])); out.append(dict(part=part, row=row, value=v['val'], cls='record', case=v['case']))
    json.dump(dict(tag=TAG, daf=DAF, geom=dict(rib=[ro_ * 1e3, ri_ * 1e3], fil_w=FIL_W * 1e3, slv_a=SLV_A * 1e3, A_fin=A_FIN * 1e6, A_cen=A_CEN * 1e6, n_ply=N_PLY,
                                               flange=dict(A=FLG['A'] * 1e6, J=FLG['J'] * 1e12), plate=dict(A=PLT['A'] * 1e6, J=PLT['J'] * 1e12), sleeve=dict(t=SLV['t'] * 1e3, Am=SLV['Am'] * 1e6, Z=SLV['Z'] * 1e9, A=SLV['A'] * 1e6)),
              rows=out), open(os.path.join(HERE, 'strength_%s.json' % TAG), 'w'), indent=1)


if __name__ == '__main__': main()
