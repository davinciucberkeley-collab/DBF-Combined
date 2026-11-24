"""T-084: shoe GER-001 (T2' pad outboard + pad pocket) and fin-tube-end rows on the T-083 landing demand (T083_data/demand_t083.json + the git-ignored
T083_data/fea/demand_t083.npz: 1.913 kg, CG 24.41 mm, pad Fp 36 N / 24 mm, 21 cases x pad zeta 0.02 / 0.05 / 0.10 x face mu 0.40 / 0.30; foot forces FB in the body frame).
Category: rigid-body dynamics (the T-083 demand, NOT re-run) + HAND CALCULATION (statics at section planes, rectangle / thin-wall bending and shear, bonded-sleeve formulas
of structures/landing_path_a.py bond_rf / rect_rf / tube_rf / comb, unchanged).  No FEA.
    python -I t084_shoe.py [--old] [--toe mm] [--tw mm] [--wall mm] [--depth mm] [--ring mm] [--tag T]   -> shoe_<tag>.json + printed table
--old: the drawn T-083b shoe (pad centre z FIN_H - 3 mm on the 5.5 mm plate, PSA) for comparison.
Factors (CLAUDE.md, D-223, never relaxed): KP 2.156 on printed / bonded rows, KF 1.725 on CF; RF >= 1.0 at max(DAF, 1.5) = 2.23 (the D-223 wing / fin value, as the
FIN-003 rows of T-083b) for pad zeta <= 0.05.
Allowables (repo values, EST, no coupon): Onyx in-layer 20 MPa / interlayer 9.5 MPa (T077_cad.md P6.2 header: PETG / Onyx 20 in-layer / 9.5 interlayer), bearing 20 MPa
(landing_path_a PETG_BEAR, used for Onyx as T-077 p8 did); epoxy bond 2.0 MPa (landing_path_a BOND); CF tube 350 / 30 MPa (landing_path_a SIG / TAU).
Print orientation (build step C7): ring axis (z) vertical, so every z-plane is an interlayer plane (toe root S1 and ring section S2 use 9.5 MPa for normal AND shear);
pocket-wall roots are x-planes (normal stress in-layer, 20 MPa; shear taken at 9.5, conservative).
Load point: the pad aft face centre, x = max(demand xf, drawn X_GROUND) = the demand 0.3475 m (longer friction lever than the drawn 0.3375: conservative); z = the demand zf
0.19073 m, which is the drawn pad centre.  Pocket walls take ALL pad friction (no floor friction credited, conservative); the 3 mm CF pin is retention only (no landing load credited)."""
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__)); QPA = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DD = os.path.abspath(os.path.join(HERE, '..', 'T083_data'))
os.environ['LAND_MASS_KG'] = '1.913'; os.environ['LAND_CG_X_MM'] = '24.41'; os.environ['LAND_MASS_MODEL'] = 'cad'
sys.path.insert(0, os.path.join(QPA, 'structures')); sys.dont_write_bytecode = True
import numpy as np
import landing_path_a as P
C, E = P.C, P.E
A = sys.argv
def arg(k, d): return float(A[A.index(k)+1]) if k in A else d
OLD = '--old' in A; TAG = A[A.index('--tag')+1] if '--tag' in A else ('old' if OLD else 'new')
KF, KP, DAF = P.KF, P.KP, 2.23
ILAY, INLAY = 9.5e6, 20e6
XT, YF, FH, FR = C.XFIN_T, C.YFIN, C.FIN_H, C.FIN_OD/2
DEM = json.load(open(os.path.join(DD, 'demand_t083.json'))); Z = np.load(os.path.join(DD, 'fea', 'demand_t083.npz'), allow_pickle=True)
XC = max(DEM['xf'], E.X_GROUND)
ZC = DEM['zf'] if not OLD else FH-0.003
RING_L = arg("--ring", 12.0)*1e-3; RING_RO = arg("--ro", 10.5)*1e-3; CAP_T = 0.003
TOE_X0 = XT+arg('--toe', 1.5)*1e-3
TOE_TW = arg('--tw', 9.0)*1e-3
WALL = arg('--wall', 1.5)*1e-3; DEPTH = arg('--depth', 4.0)*1e-3
X_AFT = XT+0.0135; PAD_DZ, PAD_HY = 0.012, 0.0075
Z_TOE0 = FH+CAP_T; Z_PAD0 = ZC-PAD_DZ/2
FLOOR_ZIN = Z_PAD0-Z_TOE0
NAMES = sorted({k.rsplit('|', 1)[0] for k in Z.files if k.endswith('|FB')})


def feet_pos(k, j):
    return np.array([XC, (1 if k == 0 else -1)*YF, (1 if j == 0 else -1)*ZC])


def wrench(FB, k, j, S):
    f = FB[:, 2*k+j, :]; r = feet_pos(k, j)-np.array(S); return f, np.cross(np.broadcast_to(r, f.shape), f)


R = {}


def put(row, arr, case, cls='RF'):
    v = float(np.nanmin(arr))
    for zk in ('all', case.split('|')[0]):
        key = (row, zk)
        if key not in R or v < R[key]['rb']: R[key] = dict(rb=v, case=case, cls=cls)


def grid_section():
    """shoe section in the z-plane just under the cap: ring annulus r 8..10.5 + plate x XT+8..XT+13.5, |y-YF| <= 10.5 (outside the tube): A, centroid x, Iy, Ix, extreme fibres"""
    h = 0.1e-3; xs = np.arange(XT-0.013, XT+0.0140, h); ys = np.arange(-0.013, 0.013, h); X, Y = np.meshgrid(xs, ys, indexing='ij'); r = np.hypot(X-XT, Y)
    dom = ((r >= FR) & (r <= RING_RO)) | ((X >= XT+0.008) & (X <= XT+0.0135) & (np.abs(Y) <= RING_RO) & (r >= FR))
    a = h*h; Aa = dom.sum()*a; xc = (X[dom]).sum()*a/Aa
    return dict(A=float(Aa), xc=float(xc), Iy=float(((X[dom]-xc)**2).sum()*a), Ix=float((Y[dom]**2).sum()*a), cx=float(np.abs(X[dom]-xc).max()), cy=float(np.abs(Y[dom]).max()))


SEC2 = grid_section()
Jring = math.pi/2*(RING_RO**4-FR**4)
for nm in NAMES:
    FB = Z[nm+'|FB'].astype(float)
    for k in (0, 1):
        for j in (0, 1):
            sz = 1 if j == 0 else -1; sy = 1 if k == 0 else -1
            if not OLD:
                a_ = X_AFT-TOE_X0; b_ = 2*TOE_TW; S1 = ((TOE_X0+X_AFT)/2, sy*YF, sz*Z_TOE0)
                f, M = wrench(FB, k, j, S1)
                put('S1 toe root (z-plane, interlayer 9.5), %.1f x %.1f mm' % (a_*1e3, b_*1e3), P.rect_rf(f[:, 2], np.hypot(f[:, 0], f[:, 1]), M[:, 2], M[:, 0], M[:, 1], a_, b_, ILAY, ILAY), nm)
                Fy, Fz = np.abs(f[:, 1]), np.abs(f[:, 2])
                for lab, F_, w_, t_ in (('S4y pocket side walls (y), %.1f mm' % (WALL*1e3), Fy, PAD_DZ, WALL),
                                        ('S4z pocket outer / inner z walls, %.1f / %.2f mm' % (WALL*1e3, FLOOR_ZIN*1e3), Fz, 2*PAD_HY, min(WALL, FLOOR_ZIN))):
                    sg = KP*6*F_*DEPTH/2/(w_*t_*t_); tu = KP*F_/(w_*t_)
                    put(lab + ': bending at the floor plane (in-layer 20) + shear (9.5)', P.comb((sg, INLAY), (tu, ILAY)), nm)
                put('S4b EVA pad bearing on a pocket wall [record, MPa at x2.23; EVA allowable "-"]', 1.0/np.maximum(np.maximum(Fy/(PAD_DZ*DEPTH), Fz/(2*PAD_HY*DEPTH))*DAF/1e6, 1e-12), nm, cls='record')
            else:
                f = FB[:, 2*k+j, :]; A_ = 0.015*0.012
                tau = np.hypot(f[:, 1], f[:, 2])/A_*KP; put('P1 pad PSA shear on the plate (0.10 MPa EST, landing_path_a PSA)', 0.10e6/np.maximum(tau, 1e-9), nm)
            S2 = (SEC2['xc'], sy*YF, sz*FH); f, M = wrench(FB, k, j, S2)
            sg = KP*(np.abs(f[:, 2])/SEC2['A']+np.abs(M[:, 1])*SEC2['cx']/SEC2['Iy']+np.abs(M[:, 0])*SEC2['cy']/SEC2['Ix'])
            tu = KP*(np.abs(M[:, 2])*RING_RO/Jring+np.hypot(f[:, 0], f[:, 1])/(SEC2['A']/2))
            put('S2 shoe ring + plate section under the cap (z-plane, interlayer 9.5)', P.comb((sg, ILAY), (tu, ILAY)), nm)
            S3 = (XT, sy*YF, sz*(FH-RING_L/2)); f, M = wrench(FB, k, j, S3)
            rf = P.bond_rf(f[:, 2], M[:, 2], np.hypot(M[:, 0], M[:, 1]), np.hypot(f[:, 0], f[:, 1]), C.FIN_OD, RING_L)
            put('S3 ring epoxy bond on the fin tube D16 x %.0f: shear (axial + torsion), 2.0 MPa' % (RING_L*1e3), rf[0], nm)
            put('S3 ring on the fin tube: bearing, compression side (20 MPa)', rf[1], nm)
            put('S3 ring bond PEEL (integrity class, outside the RF minimum; T-069 F-3)', rf[2], nm, cls='integrity')
            S5 = (XT, sy*YF, sz*(FH-RING_L)); f, M = wrench(FB, k, j, S5)
            put('S5 fin tube 16x14 at the shoe ring edge (CF 350 / 30, KF)', P.tube_rf(f[:, 2], M[:, 2], np.hypot(M[:, 0], M[:, 1]), P.A_F, P.Z_F), nm)
rows = sorted({r for r, _ in R})
out = dict(tag=TAG, geom=dict(XC=XC, ZC=ZC, TOE_X0=TOE_X0, TOE_TW=TOE_TW, WALL=WALL, DEPTH=DEPTH, RING_L=RING_L, FLOOR_ZIN=FLOOR_ZIN, sec2=SEC2), rows={})
print(f"# T-084 shoe rows ({TAG}): contact x {XC:.4f} z {ZC:.5f}; RB = rigid-body demand min over all zeta; x2.23 = RB / 2.23 (D-223); record rows in MPa at x2.23")
print("| Row | class | RB min (all zeta) | x2.23 zeta 0.02 | **x2.23 zeta 0.05** | x2.23 zeta 0.10 | governing case (zeta 0.05) |"); print("|---|---|---|---|---|---|---|")
for r in rows:
    def g(zk): return R.get((r, zk), dict(rb=float('nan')))['rb']
    cls = R[(r, 'all')]['cls']
    if cls == 'record':
        v = [1/g(z) for z in ('0.02', '0.05', '0.10')]; print(f"| {r} | record | | {v[0]:.2f} | {v[1]:.2f} | {v[2]:.2f} | {R[(r, '0.05')]['case']} |")
    else:
        print(f"| {r} | {cls} | {g('all'):.2f} | {g('0.02')/DAF:.2f} | **{g('0.05')/DAF:.2f}** | {g('0.10')/DAF:.2f} | {R[(r, '0.05')]['case']} |")
    out['rows'][r] = {zk: R[(r, zk)] for zk in ('all', '0.02', '0.05', '0.10') if (r, zk) in R}
rfmin = {zk: min(R[(r, zk)]['rb'] for r in rows if R[(r, 'all')]['cls'] == 'RF' and (r, zk) in R)/DAF for zk in ('0.02', '0.05', '0.10')}
print(f"\nMinimum RF-class row at x2.23: zeta 0.02 {rfmin['0.02']:.2f}, zeta 0.05 {rfmin['0.05']:.2f}, zeta 0.10 {rfmin['0.10']:.2f}")
out['rfmin'] = rfmin
json.dump(out, open(os.path.join(HERE, 'shoe_%s.json' % TAG), 'w'), indent=1, default=float)
