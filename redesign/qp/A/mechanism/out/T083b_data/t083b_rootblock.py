"""T-083b: root block FIN-003 redesign, strength rows on the T-083 landing demand (T083_data/demand_t083.json + the git-ignored T083_data/fea/demand_t083.npz:
1.913 kg, CG 24.41 mm, pad Fp 36 N / 24 mm, 23 cases x pad zeta 0.02 / 0.05 / 0.10 x face mu 0.40 / 0.30). Nothing is written to the demand folder.
Category: rigid-body dynamics (the T-083 demand, NOT re-run) + HAND CALCULATION (statics at section planes, thin-wall bending / torsion, bonded-joint formulas of
landing_path_a.py). No FEA.
    python -I t083b_rootblock.py [--zetas 0.02,0.05] [--tag T] [--tr mm] [--hr mm] [--tp mm] [--te mm] [--rd mm] [--petg]   -> rb_<tag>.json / printed table
--petg: the drawn PETG block (t083_path.py P5-P8 rows, unchanged formulas) for the root-cause comparison.

New part (default): machined 6061-T6 root fitting, Tormach / knee mill, two setups.
  ring   : tube about z on the fin tube axis (XFIN_T, YFIN), bore 16.0 + 2 x FB_GAP (fin tube, bonded), wall TR, height HR (z +-HR/2)
  plug   : tube about x on the rib axis (RIB_Y, z 0), OD = rib ID 23.0 - 2 x FB_GAP (bonded INSIDE the 25x23 rib), wall TP, x BLK_X0 .. RIB_X1 (31 mm engagement, unchanged)
  plate  : disc radius RD about the rib axis, x RIB_X1 .. RIB_X1 + TE (the rib end bears on it), notched by the 16 mm fin bore (the fin tube front is at RIB_X1)
  cut    : rib-wall annulus r 11.5..12.55 for x < RIB_X1 (the ring front bulge clears the rib wall)
Factors and limits (CLAUDE.md, D-223, never relaxed): KF 1.725 (metal, CF), KP 2.156 (bonds), RF >= 1.0 at max(DAF, 1.5) = 2.23 on every row (D-223 wing / fin value).
Allowables: 6061-T6 tensile yield 240 MPa minimum (en.wikipedia.org/wiki/6061_aluminium_alloy, read 2026-11-20, T-080 s1, secondary), von Mises x KF <= 240 (as CGE-006 C1);
6061-T6 bearing yield 386 MPa (aerospacemetals.com ASM data sheet, read 2026-11-21, t083_path.py BEAR_6061); epoxy bond 2.0 MPa EST (landing_path_a.BOND; on abraded 6061: EST,
same value the repo uses for the CGE-006 flange bond C3); CF tube 350 / 30 MPa EST (landing_path_a SIG / TAU). CF tube wall bearing allowable: "-" (recorded, TP-4 coupon, as B2).
Each row = minimum over all cases, zeta, mu, both fins and time steps of the concurrent per-time-step combination."""
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.environ.get('T083B_DEMAND_DIR', os.path.abspath(os.path.join(HERE, '..', 'T083_data')))
S_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'structures'))
os.environ['LAND_MASS_KG'] = os.environ.get('T083_MASS', '1.913'); os.environ['LAND_CG_X_MM'] = os.environ.get('T083_CG', '24.41'); os.environ['LAND_MASS_MODEL'] = 'cad'
sys.path.insert(0, S_DIR); sys.dont_write_bytecode = True
import numpy as np
import landing_path_a as P
W, C = P.W, P.C
A = sys.argv


def arg(k, d):
    return A[A.index(k) + 1] if k in A else d


TAG = arg('--tag', 'al')
PETG = '--petg' in A
KF, KP, BOND, DAF = P.KF, P.KP, P.BOND, 2.23
Y6061, BEAR_6061 = 240e6, 386e6
# defaults = the drawn fitting (wing.py FB_*); switches for sizing
TR = float(arg('--tr', W.FB_TR * 1e3)) * 1e-3; HR = float(arg('--hr', W.FB_HR * 1e3)) * 1e-3; TP = float(arg('--tp', W.FB_TP * 1e3)) * 1e-3; TE = float(arg('--te', W.FB_TE * 1e3)) * 1e-3
RD = float(arg('--rd', W.FB_RD * 1e3)) * 1e-3; GAP = W.FB_GAP
XT, YF, FR = C.XFIN_T, C.YFIN, C.FIN_OD / 2 + GAP      # FR = ring bore radius (fin tube + bond gap)
RIB_Y, RX1, BX0 = W.RIB_Y, W.RIB_X1, W.BLK_X0
RP = W.RIB_ID / 2 - GAP                                 # plug outer radius = rib inner radius less the bond gap
RR = FR + TR                                            # ring outer radius
DEM = json.load(open(os.path.join(DD, 'demand_t083.json'))); Z = np.load(os.path.join(DD, 'fea', 'demand_t083.npz'), allow_pickle=True)
NAMES = [str(n) for n in Z['names']]; ZETAS = tuple(float(z) for z in arg('--zetas', '0.02,0.05,0.10').split(',')); MUS = (0.40, 0.30)
P.set_pad(DEM['xf'], DEM['zf'])
R, REC = {}, {}
TAU_KNOCK = 1.10   # solver check (this file, run in T083b_data/prandtl_check.txt): circle r 10 J +1.5 %, tau +14 %; rectangle 5 x 20 tau -5 % vs Roark T(3a+1.8b)/(8a^2b^2): x1.10 covers it


def put(row, arr, case, cls='RF'):
    v = float(np.nanmin(arr))
    if row not in R or v < R[row]['rb']: R[row] = dict(rb=v, case=case, cls=cls)


def rec(row, arr, case):
    v = float(np.nanmax(arr))
    if row not in REC or v > REC[row]['val']: REC[row] = dict(val=v, case=case)


def vm(s, t):
    return np.sqrt(s ** 2 + 3 * t ** 2)


def tube_sec(ro, ri):
    a = math.pi * (ro ** 2 - ri ** 2); i = math.pi / 4 * (ro ** 4 - ri ** 4); return a, i / ro


def plane_section(xs, h=0.1e-3):
    """section of the fitting in the plane x = xs (y-z grid about the fin side +y): returns props and the connected pieces (split by empty y columns)."""
    ys = np.arange(RIB_Y - 0.015, RIB_Y + 0.015, h) + h / 2; zs = np.arange(-HR / 2 - 0.001, HR / 2 + 0.001, h) + h / 2
    Yg, Zg = np.meshgrid(ys, zs, indexing='ij')
    d2f = (xs - XT) ** 2 + (Yg - YF) ** 2
    ring = (d2f <= RR ** 2) & (np.abs(Zg) <= HR / 2)
    plate = ((Yg - RIB_Y) ** 2 + Zg ** 2 <= RD ** 2) if RX1 <= xs <= RX1 + TE else np.zeros_like(ring)
    m = (ring | plate) & (d2f >= FR ** 2)
    a = h * h; Aa = m.sum() * a; yc = (Yg[m]).mean(); zc = (Zg[m]).mean()
    Iy = ((Zg[m] - zc) ** 2).sum() * a; Iz = ((Yg[m] - yc) ** 2).sum() * a
    zmax = np.abs(Zg[m] - zc).max(); ymax = np.abs(Yg[m] - yc).max()
    col = m.any(axis=1); pieces = []; i = 0
    while i < len(ys):
        if col[i]:
            j = i
            while j < len(ys) and col[j]: j += 1
            pieces.append(((j - i) * h, m[i:j].any(axis=0).sum() * h)); i = j
        else:
            i += 1
    J, tJ = prandtl(m, h)
    return dict(A=Aa, Iy=Iy, Iz=Iz, zmax=zmax, ymax=ymax, yc=yc, zc=zc, pieces=pieces, J=J, tJ=tJ)


def prandtl(m, h):
    """Saint-Venant torsion of the grid section m (pieces simply connected): solve lap(phi) = -2, phi = 0 outside, 5-point finite differences.
    J = 2 int(phi) dA, tau_max / T = max|grad phi| / J. (Prandtl stress function; standard elasticity, e.g. Timoshenko & Goodier ch. 10.)"""
    import scipy.sparse as sp, scipy.sparse.linalg as sl
    idx = -np.ones(m.shape, dtype=np.int64); n = int(m.sum()); idx[m] = np.arange(n)
    I, Jc = np.nonzero(m); rows = [np.arange(n)]; cols = [np.arange(n)]; vals = [np.full(n, -4.0)]
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = I + di, Jc + dj; ok = (a >= 0) & (a < m.shape[0]) & (b >= 0) & (b < m.shape[1])
        nb = np.full(n, -1); nb[ok] = idx[a[ok], b[ok]]; k = nb >= 0
        rows.append(np.arange(n)[k]); cols.append(nb[k]); vals.append(np.ones(k.sum()))
    Amat = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
    phi = sl.spsolve(Amat.tocsc(), np.full(n, -2.0 * h * h))
    F = np.zeros(m.shape); F[m] = phi
    J = 2 * phi.sum() * h * h
    gy, gz = np.gradient(np.pad(F, 1), h); g = np.hypot(gy, gz)[1:-1, 1:-1]
    return J, TAU_KNOCK * float(g.max()) / J


def run():
    A_F, Z_F = tube_sec(C.FIN_OD / 2, C.FIN_ID / 2); A_R, Z_R = tube_sec(RR, FR); A_P, Z_P = tube_sec(RP, RP - TP)
    SEC = {xs: plane_section(xs) for xs in (RX1 + TE / 2, RX1 + TE)}
    zc_root = RD if RD < HR / 2 else HR / 2
    for zeta in ZETAS:
        for mu in MUS:
            for nm in NAMES:
                key = '%.2f|%.2f|%s' % (zeta, mu, nm); FB = Z[key + '|FB'].astype(float); case = '%s z%.2f mu%.2f' % (nm, zeta, mu)
                for k in (0, 1):
                    sg = 1 if k == 0 else -1; yr, yf = sg * RIB_Y, sg * YF
                    if PETG:                                                   # the drawn block, t083_path.py rows P6 / P8 (unchanged formulas)
                        Bw = 2 * W.BLK_SH; ro_ = W.RIB_OD
                        F6, M6 = P.M_about(FB, k, (RX1, yr, 0.0)); a6 = P.chord(P.RING_BL_RO, XT - RX1)
                        s6 = (np.abs(M6[:, 1]) / (a6 * Bw * Bw / 6)) * KP; s6b = (np.abs(M6[:, 2]) / (Bw * a6 * a6 / 6)) * KP; s6c = np.abs(F6[:, 0]) / (a6 * Bw) * KP
                        t6 = (np.hypot(F6[:, 1], F6[:, 2]) / (a6 * Bw) + np.abs(M6[:, 0]) / (0.21 * max(a6, Bw) * min(a6, Bw) ** 2)) * KP
                        put('P6 ring-to-socket junction PETG %.1f x %.0f, interlayer 9.5' % (a6 * 1e3, Bw * 1e3), P.comb((s6 + s6b + s6c, P.PETG_ILAY), (t6, P.PETG_ILAY)), case)
                        for lab_, arr_ in (('My (sigma)', s6), ('Mz (sigma)', s6b), ('Fx (sigma)', s6c), ('Mx + V (tau)', t6)):
                            rec('P6 stress part %s at RB [MPa]' % lab_, arr_ * 1e-6, case)
                        Fm, Mm = P.M_about(FB, k, (BX0, yr, 0.0))
                        Ib = Bw ** 4 / 12 - math.pi * ro_ ** 4 / 64; Zb = Ib / (Bw / 2); tw = (Bw - ro_) / 2; Tb = 2 * ((Bw + ro_) / 2) ** 2 * tw
                        s = (np.hypot(Mm[:, 1], Mm[:, 2]) / Zb + np.abs(Fm[:, 0]) / (Bw ** 2 - math.pi * ro_ ** 2 / 4)) * KP; t = (np.abs(Mm[:, 0]) / Tb + np.hypot(Fm[:, 1], Fm[:, 2]) / (4 * Bw * tw)) * KP
                        put('P8 socket wall PETG box %.0f / bore %.0f, interlayer 9.5' % (Bw * 1e3, ro_ * 1e3), P.comb((s, P.PETG_ILAY), (t, P.PETG_ILAY)), case)
                        rec('P8 sigma at RB [MPa]', s * 1e-6, case); rec('P8 tau at RB [MPa]', t * 1e-6, case)
                        rec('max |My| at the junction x %.0f [N m, RB]' % (RX1 * 1e3), np.abs(M6[:, 1]), case)
                        continue
                    # Q1 ring bond on the fin tube (both feet about the block centre)
                    F5, M5 = P.M_about(FB, k, (XT, yf, 0.0))
                    tau = np.hypot(np.abs(F5[:, 2]) / (math.pi * C.FIN_OD * HR), np.abs(M5[:, 2]) / (2 * math.pi * (C.FIN_OD / 2) ** 2 * HR)) * KP
                    sb = (6 * np.hypot(M5[:, 0], M5[:, 1]) / (C.FIN_OD * HR ** 2) + np.hypot(F5[:, 0], F5[:, 1]) / (C.FIN_OD * HR)) * KP
                    put('Q1a ring epoxy bond on the fin tube (D16 x %.0f): shear (axial + torsion), epoxy 2.0' % (HR * 1e3), BOND / np.maximum(tau, 1e-9), case)
                    put('Q1b ring bearing on the 6061 bore (6M/(D L^2) + V/(D L), KP), bearing yield 386' % (), BEAR_6061 / np.maximum(sb, 1e-9), case)
                    put('Q1c ring bond peel, same stress vs epoxy 2.0 (integrity class, outside the RF minimum as T-069 F-3)', BOND / np.maximum(sb, 1e-9), case, cls='integrity')
                    rec('Q1d CF fin-tube wall bearing in the ring at x2.23 [MPa]; CF bearing allowable "-" (TP-4 coupon)', DAF * sb * 1e-6, case)
                    # Q2 fin tube at the ring edge, one foot per half (landing_path_a P4 formula at the new edge)
                    for j in (0, 1):
                        zz = (1 if j == 0 else -1) * HR / 2
                        Fq, Mq = P.M_about(FB, k, (XT, yf, zz), (j,))
                        put('Q2 fin tube 16x14 at the ring edge z +-%.0f mm (P4 formula), CF 350 / 30, KF' % (HR * 5e2), P.tube_rf(Fq[:, 2], Mq[:, 2], np.hypot(Mq[:, 0], Mq[:, 1]), A_F, Z_F), case)
                        # Q3 ring alone at the collar root z = +-RD (all the foot wrench in the ring, the fin tube ignored: conservative)
                        zz = (1 if j == 0 else -1) * zc_root
                        Fq, Mq = P.M_about(FB, k, (XT, yf, zz), (j,))
                        s = KF * (np.hypot(Mq[:, 0], Mq[:, 1]) / Z_R + np.abs(Fq[:, 2]) / A_R); t = KF * (np.abs(Mq[:, 2]) / (2 * Z_R) + 2 * np.hypot(Fq[:, 0], Fq[:, 1]) / A_R)
                        put('Q3 ring %.1f/16 alone at the collar root z +-%.1f (one foot; fin tube share ignored), 6061 von Mises x KF' % (2 * RR * 1e3, zc_root * 1e3), Y6061 / np.maximum(vm(s, t), 1e-9), case)
                    # Q4 / Q5 plate mid-plane and plate aft face (both feet; everything crosses the plane: conservative)
                    for xs, lab in ((RX1 + TE / 2, 'Q4 plate mid-plane x %.2f'), (RX1 + TE, 'Q5 plate aft face x %.2f (ring side strips + plate)')):
                        S = SEC[xs]; Fq, Mq = P.M_about(FB, k, (xs, sg * S['yc'], S['zc']))
                        s = KF * (np.abs(Mq[:, 1]) * S['zmax'] / S['Iy'] + np.abs(Mq[:, 2]) * S['ymax'] / S['Iz'] + np.abs(Fq[:, 0]) / S['A'])
                        t = KF * (np.abs(Mq[:, 0]) * S['tJ'] + 1.5 * np.hypot(Fq[:, 1], Fq[:, 2]) / S['A'])
                        put((lab % (xs * 1e3)) + ': bending + axial, torsion by the Prandtl stress function, 6061 von Mises x KF', Y6061 / np.maximum(vm(s, t), 1e-9), case)
                    # Q6 plug section at the plug root x = RIB_X1 (the rib has ended: the plug carries all) and at the mouth
                    for xs, lab in ((RX1, 'Q6a plug at its root x %.0f'), (BX0, 'Q6b plug at the mouth x %.0f')):
                        Fq, Mq = P.M_about(FB, k, (xs, yr, 0.0))
                        s = KF * (np.hypot(Mq[:, 1], Mq[:, 2]) / Z_P + np.abs(Fq[:, 0]) / A_P); t = KF * (np.abs(Mq[:, 0]) / (2 * Z_P) + 2 * np.hypot(Fq[:, 1], Fq[:, 2]) / A_P)
                        put((lab % (xs * 1e3)) + ' (OD %.1f / ID %.1f), 6061 von Mises x KF' % (2 * RP * 1e3, 2 * (RP - TP) * 1e3), Y6061 / np.maximum(vm(s, t), 1e-9), case)
                    # Q7 plug bond inside the rib (D23 x 31), loads at the mouth (landing_path_a P7 formula)
                    Fm, Mm = P.M_about(FB, k, (BX0, yr, 0.0)); Lb = RX1 - BX0; D = 2 * RP
                    tau = np.hypot(np.abs(Fm[:, 0]) / (math.pi * D * Lb), np.abs(Mm[:, 0]) / (2 * math.pi * RP ** 2 * Lb)) * KP
                    sb = (6 * np.hypot(Mm[:, 1], Mm[:, 2]) / (D * Lb ** 2) + np.hypot(Fm[:, 1], Fm[:, 2]) / (D * Lb)) * KP
                    put('Q7a plug epoxy bond inside the rib (D%.0f x %.0f): shear, epoxy 2.0' % (D * 1e3, Lb * 1e3), BOND / np.maximum(tau, 1e-9), case)
                    put('Q7b plug bearing on the 6061 (KP), bearing yield 386', BEAR_6061 / np.maximum(sb, 1e-9), case)
                    put('Q7c plug bond peel vs epoxy 2.0 (integrity class)', BOND / np.maximum(sb, 1e-9), case, cls='integrity')
                    rec('Q7d CF rib-wall bearing on the plug at x2.23 [MPa]; allowable "-" (TP-4 coupon); the PETG block put the same stress into the rib wall', DAF * sb * 1e-6, case)
                    # Q8 rib end on the plate (axial Fx through the rib-end annulus + plug), 6061 bearing
                    Fq, Mq = P.M_about(FB, k, (RX1, yr, 0.0))
                    ann = math.pi * (W.RIB_OD ** 2 - W.RIB_ID ** 2) / 4
                    sbe = KF * (np.abs(Fq[:, 0]) / ann + np.hypot(Mq[:, 1], Mq[:, 2]) / tube_sec(W.RIB_OD / 2, W.RIB_ID / 2)[1])
                    put('Q8 rib end bearing on the plate face (Fx + bending of the rib-end annulus, KF), bearing yield 386', BEAR_6061 / np.maximum(sbe, 1e-9), case)
                    rec('max |My| at the junction x %.0f [N m, RB]' % (RX1 * 1e3), np.abs(Mq[:, 1]), case)
    return SEC


def main():
    np.seterr(all='ignore')
    SEC = run()
    print('# T-083b root block rows (%s), tag %s, zetas %s. Demand: Fp %.0f N / %.0f mm, %.3f kg, CG %.2f mm; KF %.3f KP %.3f; verdict at x%.2f'
          % ('drawn PETG block' if PETG else '6061 fitting TR %.1f HR %.0f TP %.1f TE %.1f RD %.1f mm' % (TR * 1e3, HR * 1e3, TP * 1e3, TE * 1e3, RD * 1e3), TAG, ZETAS, DEM['Fp'], DEM['smax'] * 1e3, DEM['mass'], DEM['cg'][0] * 1e3, KF, KP, DAF))
    if not PETG:
        for xs, S in SEC.items():
            print('# plane x %.2f: A %.1f mm2, Iy %.0f mm4, Iz %.0f mm4, pieces (t x b mm) %s, J %.1f mm4' % (xs * 1e3, S['A'] * 1e6, S['Iy'] * 1e12, S['Iz'] * 1e12,
                  [(round(t * 1e3, 2), round(b * 1e3, 2)) for t, b in S['pieces']], S['J'] * 1e12))
    out = []
    print('\n| row | RB | x1.5 | x2.23 | verdict at x2.23 | governing case |\n|---|---|---|---|---|---|')
    for row, v in sorted(R.items(), key=lambda kv: kv[1]['rb']):
        rb = v['rb']; vd = ('integrity class: %s' % ('>= 1' if rb / DAF >= 1 else '< 1')) if v['cls'] == 'integrity' else ('PASS' if rb / DAF >= 1 else 'FAIL')
        print('| %s | %.2f | %.2f | %.2f | %s | %s |' % (row, rb, rb / 1.5, rb / DAF, vd, v['case'])); out.append(dict(row=row, rb=rb, x223=rb / DAF, cls=v['cls'], verdict=vd, case=v['case']))
    for row, v in sorted(REC.items()):
        print('| %s = %.2f | | | | record | %s |' % (row, v['val'], v['case'])); out.append(dict(row=row, value=v['val'], cls='record', case=v['case']))
    mins = [o['x223'] for o in out if o.get('cls') == 'RF']
    print('\nmin RF at x2.23 (RF class): %.2f' % min(mins))
    json.dump(dict(tag=TAG, petg=PETG, zetas=ZETAS, geom=dict(TR=TR * 1e3, HR=HR * 1e3, TP=TP * 1e3, TE=TE * 1e3, RD=RD * 1e3), min_x223=min(mins), rows=out),
              open(os.path.join(HERE, 'rb_%s.json' % TAG), 'w'), indent=1)


if __name__ == '__main__': main()
