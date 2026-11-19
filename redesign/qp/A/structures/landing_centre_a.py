"""T-071b Part A: centre reaction of the landing pitch torque (concept A).   python -I landing_centre_a.py [--recompute]
Categories: rigid-body dynamics (landing_a.py foot-force histories, 23 cases, D2 pad; hub-side wrench from the SAME point-mass model the sim uses) + HAND CALCULATION (bearing, bond, plate, pin).  No FEA.
Frames: body x aft, y span, z up (cruise).  Interface point P = bridge bore mouth (x = HUB_X1, y 0, z BR_Z).
Allowables are EST unless a source is named (same values as landing_path_a.py: PETG bearing 20 MPa, epoxy 2.0 MPa, CF 350 / 30 MPa).  KF 1.725 / KP 2.156 are never relaxed.
"""
import sys, os, math, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import landing_path_a as P
L, W, C, E = P.L, P.W, P.C, P.E
KF, KP = P.KF, P.KP
OUT = os.environ.get('LAND_OUT_DIR') or os.path.join(HERE, '..', 'mechanism', 'out', 'T071b_data')   # T-074: LAND_OUT_DIR keeps new runs out of the committed cache (default unchanged)
CACHE = os.path.join(OUT, 'demand.json')

# ---------------------------------------------------------------- 1. demand: wrench transmitted to the hub side and to each wing half (rigid-body, sim point-mass model)
PX, PY, PZ = W.HUB_X1, 0.0, W.BR_Z
HUB_SIDE = {0: 'motors 4 x 88.26 g', 1: 'arms 64 g (4 lumps)', 2: 'hub 46 g', 3: 'pack 270 g'}
def sim_items(scale_to=L.M_GATE):
    """landing_a.ITEMS expanded to point masses exactly as landing_a.mass_props does, with a tag: 'hub' (motors, arms, hub, pack), 'wing' (everything else, split to the +y / -y half by y sign; y = 0 lumps 50 / 50)."""
    pts = []
    for idx, (g, x, y, z) in enumerate(L.ITEMS):
        ys = (y, -y) if y else (0,); zs = (z, -z) if z else (0,); n = len(ys)*len(zs)
        for yy in ys:
            for zz in zs: pts.append((g/n, x, yy, zz, idx))
    k = scale_to*1000/sum(p[0] for p in pts)
    return [(g*k/1000, x, y, z, idx) for g, x, y, z, idx in pts]
def wrench_split(FBt, hub_idx=(2, 3, 4, 6), P0=(PX, PY, PZ)):
    """FBt (n,4,3) body-frame foot forces (fin 0 = +y: feet 0, 1; fin 1 = -y: feet 2, 3).  Returns dict body -> (F (n,3), M (n,3)): the wrench the CENTRE exerts on that sub-body, about P0:
    'hub' = hub side (ITEMS indices hub_idx: motors, arms, hub, pack), 'R' / 'L' = the +y / -y wing half with its fin and feet (all other items; y = 0 lumps split 50 / 50).
    Rigid body: a_i = a_cg + alpha x rho_i, alpha = I^-1 M_cg (I of the translated point-mass model; gyroscopic terms, gravity and rotor thrust neglected: small against the impact forces, EST).
    The three wrenches sum to zero (checked by the caller).  ITEMS: 0 wing 213 g, 1 fins 125 g, 2 motors, 3 arms, 4 hub 46 g, 5 bridge/struts 20 g, 6 pack 270 g, 7 110 g, 8 elevons 30 g, 9 40 g."""
    g_ = L.geom(); cg = np.array(g_['cg'], float); pts = sim_items()
    mm_, cg_items, _ = L.mass_props(L.M_GATE); dsh = cg-np.array(cg_items)       # the sim puts the body CG at the CAD CG with the ITEMS inertia: translate the whole point-mass model by the offset so Newton / Euler close
    pts = [(g, x+dsh[0], y+dsh[1], z+dsh[2], idx) for g, x, y, z, idx in pts]
    m = sum(p[0] for p in pts); xf, zf, yf = P.XF, P.ZF, P.YF
    feet = np.array([[xf, sy*yf, sz*zf] for sy in (1, -1) for sz in (1, -1)]); rf = feet-cg
    Ib = np.zeros((3, 3))
    for g, x, y, z, idx in pts:
        r = np.array([x, y, z])-cg; Ib += g*((r@r)*np.eye(3)-np.outer(r, r))
    Ibi = np.linalg.inv(Ib)
    Ftot = FBt.sum(axis=1); Mcg = np.zeros_like(Ftot)
    for i in range(4): Mcg += np.cross(np.broadcast_to(rf[i], FBt[:, i, :].shape), FBt[:, i, :])
    a_cg = Ftot/m; alpha = Mcg@Ibi.T; P0 = np.array(P0, float); z0 = np.zeros_like(Ftot)
    Fo = {'hub': z0.copy(), 'R': z0.copy(), 'L': z0.copy()}; Mo = {'hub': z0.copy(), 'R': z0.copy(), 'L': z0.copy()}
    for g, x, y, z, idx in pts:
        rho = np.array([x, y, z])-cg; s = np.array([x, y, z])-P0
        f = g*(a_cg+np.cross(alpha, np.broadcast_to(rho, alpha.shape))); mom = np.cross(np.broadcast_to(s, f.shape), f)
        if idx in hub_idx: Fo['hub'] += f; Mo['hub'] += mom
        else:
            w_ = 1.0 if y > 1e-9 else (0.0 if y < -1e-9 else 0.5)
            Fo['R'] += w_*f; Mo['R'] += w_*mom; Fo['L'] += (1-w_)*f; Mo['L'] += (1-w_)*mom
    for k_, key in ((0, 'R'), (1, 'L')):
        for j in (0, 1):
            f = FBt[:, 2*k_+j, :]; s = feet[2*k_+j]-P0; Fo[key] -= f; Mo[key] -= np.cross(np.broadcast_to(s, f.shape), f)
    return {k: (Fo[k], Mo[k]) for k in Fo}
def move_my(F, M, P_from, P_to):
    """y-moment of the same wrench (force F, moment M about P_from) taken about P_to: M + (P_from - P_to) x F."""
    d = np.array(P_from, float)-np.array(P_to, float); return (M+np.cross(np.broadcast_to(d, F.shape), F))[:, 1]

def demand(recompute=False):
    """-> dict of per-case arrays; cached in T071b_data/demand_series.npz (written by --recompute)."""
    f = os.path.join(OUT, 'demand_series.npz')
    if os.path.exists(f) and not recompute:
        z = np.load(f, allow_pickle=True); return {k: z[k] for k in z.files}
    P.set_pad(P.PAD_D2['x_foot'], P.PAD_D2['z_foot']); d = {}; names = []; t0 = time.time()
    for name, kw in P.cases(False):
        FBt = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, **dict(kw, **P.PAD_D2))['trace'].reshape(-1, 4, 3)
        names.append(name)
        for tag, hub_idx in (('base', (2, 3, 4, 6)), ('nopack', (2, 3, 4))):
            w = wrench_split(FBt, hub_idx)
            tot = sum(np.abs(w[k][1]).max() for k in w); chk = np.abs(w['hub'][1]+w['R'][1]+w['L'][1]).max()+np.abs(w['hub'][0]+w['R'][0]+w['L'][0]).max()
            assert chk < 1e-6, (name, chk)
            for k in w:
                d[f'{tag}|{k}|F|{name}'] = w[k][0].astype(np.float32); d[f'{tag}|{k}|M|{name}'] = w[k][1].astype(np.float32)
        # step-2 style single-fin foot moment about the span axis (the 2T bound input)
        for k in (0, 1): d[f'foot|{k}|{name}'] = P.M_about(FBt, k, P.S_(k, P.SX, 0.0))[1][:, 1].astype(np.float32)
        print('  %-34s [%.0f s]' % (name, time.time()-t0), flush=True)
    d['names'] = np.array(names); np.savez_compressed(f, **d); return d


# ---------------------------------------------------------------- 2. constants (CAD: wing.py / common.py), allowables (EST unless sourced)
PETG_BEAR, PETG_IN, PETG_IL = 20e6, 20e6, 9.5e6        # EST: bearing / in-layer (ASM-A-PETG-ALLOW, fea_arm.py ALLOW) and interlayer (structures_a.py l.16)
BOND = 2.0e6                                          # EST epoxy on CF / PETG (structures_a.py BOND_TAU)
PIN_TAU = 30e6                                        # EST CF rod shear (structures_a.py TAU)
BR_OD, BR_ID = W.BR_OD, W.BR_ID
Z_BR = math.pi/64*(BR_OD**4-BR_ID**4)/(BR_OD/2)
X_MOUTH0, X_FLOOR0 = W.HUB_X1, W.BORE_X0              # -0.045, -0.054
X_SAD_FWD0, X_SAD_AFT = 0.030, 0.0535                 # CGE-006 bridge socket (wing.py box)
BLK_Y, BLK_H, BLK_Z0 = 2*W.CB, 2*W.CB, W.BLK_Z        # hub centre block 20 x 20 mm centred on the bridge axis (z -2 mm)
RHO_PETG = W.RHO_PETG*1.0                             # g/cm3
ACP_CF = dict(S090=90e6, S45=260e6, X090=600e6, E090=70e9, G090=5e9)   # ACP PDS Dec 2014 (read 2026-11-19): Std CF fabric Vf 50 % dry RT, 120 C cure, 0/90 axes and +-45 to the load axis
CF_SHEET = 0.70                                       # EST knock-down: a bought cured sheet or wet lay-up against the ACP dry-prepreg datum (no coupon)
DAF = 1.5                                             # EST dynamic factor on the rigid-body wrench (no transient FE run: see the record)


def series(d, tag='base'):
    """per case: (F_hub, M_hub about P, wing-half wrenches) -> lists"""
    out = []
    for n in d['names']:
        out.append((str(n), d[f'{tag}|hub|F|{n}'].astype(float), d[f'{tag}|hub|M|{n}'].astype(float), d[f'{tag}|R|F|{n}'].astype(float), d[f'{tag}|R|M|{n}'].astype(float),
                    d[f'{tag}|L|F|{n}'].astype(float), d[f'{tag}|L|M|{n}'].astype(float)))
    return out
P0 = (PX, PY, PZ)
def bearing_p(M, V, Lb, D=BR_OD, K=KP):
    """peak mean bearing stress of a rigid tube in a socket of length Lb under end moment M (triangular, 6M/(D Lb^2)) plus shear V (V/(D Lb)): stress x K."""
    return K*(6*np.abs(M)/Lb**2+np.abs(V)/Lb)/D
def collar_Mc(M, V, Lb, a, D=BR_OD, K=KP, n=40):
    """bending moment (x K) at the block face of the aft extension e = Lb - a (a = bore length inside the existing block): pressure on the compress side over the extension,
    p(xi) = A (2 xi / Lb - 1) + B, xi from the floor, clipped at 0; line load p D; moment about xi = a."""
    A = 6*np.abs(M)/(D*Lb**2); B = np.abs(V)/(D*Lb); e = Lb-a
    if e <= 1e-9: return np.zeros_like(A)
    xs = a+(np.arange(n)+0.5)/n*e; Mc = 0
    for xi in xs: Mc = Mc+np.maximum(A*(2*xi/Lb-1)+B, 0)*D*(xi-a)*e/n
    return K*Mc
def hub_rows(S, geom, daf=1.0, bound=None):
    """geom: dict x_mouth, x_floor, x_sad_fwd, e_block (aft extension beyond the 9 mm-class block face; 0 = none), blk_h.  Min RF over all cases and times.
    bound (N m): replace the series by the step-2 constant-moment bound (V = 0)."""
    xm, xf, xs = geom['x_mouth'], geom['x_floor'], geom['x_sad_fwd']; Lh = xm-xf; Ls = X_SAD_AFT-xs; a0 = X_MOUTH0-xf
    r = dict(bridge=1e9, hub_bear=1e9, sad_bear=1e9, collar_il=1e9, collar_in=1e9)
    bb, hh = geom.get('blk_b', BLK_Y), geom.get('blk_h', BLK_H)
    Zc = (bb*hh**3/12-math.pi*BR_OD**4/64)/(hh/2)                           # extension section (y width bb x z height hh) minus the 16 mm bore, bending about y
    for nm, F, M, FR, MR, FL, ML in S:
        if bound is None:
            Mm = daf*move_my(F, M, P0, (xm, 0, PZ)); Ms = daf*move_my(F, M, P0, (xs, 0, PZ)); V = daf*F[:, 2]
        else: Mm = Ms = np.full(3, bound); V = np.zeros(3)
        r['bridge'] = min(r['bridge'], float((350e6/(KF*np.maximum(np.maximum(np.abs(Mm), np.abs(Ms)), 1e-9)/Z_BR)).min()))
        r['hub_bear'] = min(r['hub_bear'], float((PETG_BEAR/bearing_p(Mm, V, Lh)).min()))
        r['sad_bear'] = min(r['sad_bear'], float((PETG_BEAR/bearing_p(Ms, V, Ls)).min()))
        if geom.get('e_block', 0) > 0:
            Mc = collar_Mc(Mm, V, Lh, a0)
            r['collar_il'] = min(r['collar_il'], float((PETG_IL*Zc/np.maximum(Mc, 1e-9)).min())); r['collar_in'] = min(r['collar_in'], float((PETG_IN*Zc/np.maximum(Mc, 1e-9)).min()))
    return r


# ---------------------------------------------------------------- 3. wing-end node: skin -> centre bulkhead plate -> saddle ear -> saddle (CGE-006)
def node_demand(S, sh_k):
    """T_skin per side (N m, limit load): R / L half-body wrench y-moment about the worse of the spar line (x 0.060) and mid-chord (x 0.1225), z 0 (as landing_path_a), x skin share sh_k.  Returns max |T_c| over cases and times (both sides)."""
    best = 0.0; arr = []
    for nm, F, M, FR, MR, FL, ML in S:
        for FF, MM in ((FR, MR), (FL, ML)):
            t = np.maximum(np.abs(move_my(FF, MM, P0, (P.SX, 0, 0))), np.abs(move_my(FF, MM, P0, (0.5*C.C, 0, 0)))); arr.append(t); best = max(best, float(t.max()))
    return best, arr
def zlim(x):
    """airfoil z extent at chord station x (m), WING_DZ-shifted (common.zu / zl)"""
    return C.zl(x), C.zu(x)
def node_rows(Tsk, A_cell, opt):
    """one side.  opt keys: lap (m, skin bond width), plate_t, plate_S (Pa or None: no allowable '—'), ear (a along x, b along z), faces (1 butt / 2 clevis), pins (n, r_p, shear planes), K."""
    K = opt.get('K', KP); q = Tsk/(2*A_cell); a, b = opt['ear']; Jp = a*b*(a*a+b*b)/12; rmax = 0.5*math.hypot(a, b); r = {}
    r['skin->plate bond, lap %.1f mm' % (opt['lap']*1e3)] = BOND*opt['lap']/(K*q)
    req = math.sqrt(a*b/math.pi); qp = Tsk/(2*math.pi*req**2)
    r['plate shear flow at the ear edge (r_eq %.1f mm)' % (req*1e3)] = (opt['plate_S']*opt['plate_t']/(K*qp)) if opt.get('plate_S') else float('nan')
    tau = Tsk*rmax/Jp/opt.get('faces', 1)
    r['plate->ear bond, ear %.1f x %.1f mm, %d face(s)' % (a*1e3, b*1e3, opt.get('faces', 1))] = BOND/(K*tau)
    n, rp, planes = opt['pins']
    if n > 0:
        F = Tsk/(n*rp); r['CF pins: %d x 3 mm at r %.0f mm, %d shear plane(s), %.0f N each' % (n, rp*1e3, planes, F)] = PIN_TAU*planes*math.pi/4*0.003**2/(K*F)
    return r
def spar_ring(Tsp, K=KP, D=0.012, Lb=0.030):
    """saddle ring bond on the spar carries the spar torque share (GJ share) across the saddle: tau = T/(2 pi r^2 L)"""
    return BOND/(K*Tsp/(2*math.pi*(D/2)**2*Lb))


# ---------------------------------------------------------------- 4. options, ladder order; envelope check; main
def g_ext(e, bb, hh):   # g of PETG (solid, EST: infill / shell factor unknown) of an aft block extension e long, section bb x hh (m) minus the 16 mm bore
    return ((bb*1e3)*(hh*1e3)-math.pi/4*(BR_OD*1e3)**2)*(e*1e3)/1e3*RHO_PETG
def g_floor(dz): return math.pi/4*(BR_OD*1e3)**2*(dz*1e3)/1e3*RHO_PETG     # g removed by deepening the bore dz
HUBOPT = [   # label, ladder rung, geometry dict, dmass g
 ('H0 as drawn: bore 9.0 mm, no extension', 0, dict(x_floor=X_FLOOR0, x_mouth=X_MOUTH0, e_block=0), 0.0),
 ('H1 bore floor 1.5 mm deeper (limit: 1.0 mm web left over the aft surface of tube B at x -0.0565), no extension', 2, dict(x_floor=-0.0555, x_mouth=X_MOUTH0, e_block=0), -g_floor(0.0015)),
 ('H2 H1 + block aft extension 10 mm, section 20 x 20 (= the block)', 2, dict(x_floor=-0.0555, x_mouth=X_MOUTH0+0.010, e_block=10, blk_b=0.020, blk_h=0.020), g_ext(0.010, 0.020, 0.020)-g_floor(0.0015)),
 ('H3 H1 + block aft extension 12 mm, section 24 (y) x 24 (z -16..+8) flared collar', 2, dict(x_floor=-0.0555, x_mouth=X_MOUTH0+0.012, e_block=12, blk_b=0.024, blk_h=0.024), g_ext(0.012, 0.024, 0.024)-g_floor(0.0015)),
 ('H4 arm tube B moved 12.5 mm forward, bore floor to x -0.068, + 6 mm aft extension 20 x 20 (L 29 mm)', 3, dict(x_floor=-0.068, x_mouth=X_MOUTH0+0.006, e_block=6, blk_b=0.020, blk_h=0.020), 5.0),
]
SADOPT = [('S0 as drawn: socket x 0.030..0.0535 (23.5 mm)', X_SAD_FWD0, 0.0),
          ('S1 socket extended 5.3 mm forward to x 0.0245 (core saddle slot cut 5.3 mm longer)', 0.0245, ((2*(BR_OD/2+0.0025)*1e3)**2-math.pi/4*(BR_OD*1e3)**2)*5.3/1e3*RHO_PETG)]
def envelope_check(box):
    """CAD part boxes (stub build, world bbox from the 8 local corners): parts whose box overlaps the test box (x0, y0, z0), (x1, y1, z1)."""
    import itertools, build_a as b
    ctx, _, res = b.build_all.build(b.StubBackend(), b.MODEL, os.path.join(b.MODEL, 'modules.txt'), log=lambda *a: None)
    hits = []
    for pid, c in ctx.components.items():
        lo, hi = c.bbox(); pts = np.array([c.to_world(tuple(p)) for p in itertools.product(*[(lo[i], hi[i]) for i in range(3)])]); lo_w, hi_w = pts.min(0), pts.max(0)
        if all(lo_w[i] < box[1][i] and hi_w[i] > box[0][i] for i in range(3)): hits.append((pid, np.round(lo_w*1e3, 1).tolist(), np.round(hi_w*1e3, 1).tolist()))
    return hits


SAD_LONG_G = (23.5*21-math.pi/4*16**2)*12/1e3*RHO_PETG      # saddle box lengthened from y +-10.5 to +-16.5 mm (12 mm total), 23.5 x 21 section minus the 16 mm bridge hole, solid PETG EST (upper bound)
def cg_shift_mm(dm_g, x_m):
    cm = json.load(open(os.path.join(HERE, '..', 'sitl', 'cad_mass.json'))); cg_x = cm['cg_x_m']; M_g = cm['mass_basic_kg']*1e3
    return dm_g*(x_m-cg_x)/(M_g+dm_g)*1e3
def _arc(cond):
    Pl = P._poly(); s_ = 0.0
    for i in range(len(Pl)):
        a, b_ = Pl[i], Pl[(i+1) % len(Pl)]; n = max(int(math.hypot(*(b_-a))/1e-4), 1)
        for k in range(n):
            p = a+(b_-a)*((k+.5)/n)
            if cond(p): s_ += math.hypot(*(b_-a))/n
    return s_*1e3
def _zup(p): return abs(p[1]-C.zu(p[0])) < abs(p[1]-C.zl(p[0]))

def main():
    np.seterr(all='ignore'); t0 = time.time(); recompute = '--recompute' in sys.argv; d = demand(recompute); S = series(d); Sn = series(d, 'nopack')
    print('# T-071b Part A: centre reaction of the landing pitch torque (concept A).  Categories: rigid-body dynamics (demand) + hand calculation (parts).  KF %.3f KP %.3f' % (KF, KP))
    print('# interface point P = bridge bore mouth x %.4f, z %.4f; pad D2 (x %.4f, z %.3f), 23 cases, plateau 30 N, mu 0.40 (sim default; Part B reruns at 0.30)' % (PX, PZ, P.PAD_D2['x_foot'], P.PAD_D2['z_foot']))
    print('\n## 1. Demand (limit load, N m; moments about the span axis y)')
    rows = []
    for (nm, F, M, FR, MR, FL, ML), (_, Fn, Mn, *_r) in zip(S, Sn):
        f = [float(np.abs(d['foot|%d|%s' % (k, nm)]).max()) for k in (0, 1)]
        mp = float(np.abs(move_my(F, M, P0, P0)).max()); ms = float(np.abs(move_my(F, M, P0, (X_SAD_FWD0, 0, PZ))).max()); mpn = float(np.abs(move_my(Fn, Mn, P0, P0)).max())
        tr = [float(np.maximum(np.abs(move_my(FF, MM, P0, (P.SX, 0, 0))), np.abs(move_my(FF, MM, P0, (0.5*C.C, 0, 0)))).max()) for FF, MM in ((FR, MR), (FL, ML))]
        rows.append((nm, f, mp, ms, float(np.abs(F[:, 2]).max()), tr, mpn))
    print('| case | foot torque fin R / fin L (feet about the span axis) | hub-side M at the bore mouth | hub-side M at the saddle fwd end (x 0.030) | hub-side Fz N | wing-half torque R / L (worse of spar line, mid-chord) | hub M, pack counted wing-side |')
    print('|---|---|---|---|---|---|---|')
    for nm, f, mp, ms, fz, tr, mpn in rows: print('| %s | %.2f / %.2f | %.2f | %.2f | %.1f | %.2f / %.2f | %.2f |' % (nm, f[0], f[1], mp, ms, fz, tr[0], tr[1], mpn))
    M2 = 2*max(max(r[1]) for r in rows)
    print('MAX: hub M at mouth %.2f, at saddle %.2f, hub Fz %.1f N, wing-half torque %.2f; no-pack variant %.2f; step-2 bound 2 x single-fin max = %.2f (T-071 step 2: 20.5)' % (
        max(r[2] for r in rows), max(r[3] for r in rows), max(r[4] for r in rows), max(max(r[5]) for r in rows), max(r[6] for r in rows), M2))
    print('Check: hub + R + L wrench sums to zero in every case and time step (assert in demand(); residual < 1e-6 N, N m).')
    print('\n## 2. Hub end (bridge bore) options. RF = min over 23 cases and all time steps. Demand columns: RB (rigid-body wrench), RB x %.1f (EST dynamic factor), 2T (step-2 bound, constant moment, V 0)' % DAF)
    print('| Option | rung | L bore mm | dmass g (solid PETG EST) | bridge bending RB | hub bore bearing RB / RBx%.1f / 2T | collar bending, interlayer 9.5 MPa: RB / RBx%.1f / 2T | collar in-layer 20 MPa: RB / RBx%.1f |' % (DAF, DAF, DAF))
    print('|---|---|---|---|---|---|---|---|')
    f_ = lambda v: ('%.2f' % v) if v < 1e8 else '-'
    for lab, rung, g, dm in HUBOPT:
        g = dict(g, x_sad_fwd=X_SAD_FWD0); r1 = hub_rows(S, g); r2 = hub_rows(S, g, daf=DAF); r3 = hub_rows(S, g, bound=M2)
        print('| %s | %d | %.1f | %+.1f | %.2f | %.2f / %.2f / %.2f | %s / %s / %s | %s / %s |' % (lab, rung, (g['x_mouth']-g['x_floor'])*1e3, dm, r1['bridge'], r1['hub_bear'], r2['hub_bear'], r3['hub_bear'],
              f_(r1['collar_il']), f_(r2['collar_il']), f_(r3['collar_il']), f_(r1['collar_in']), f_(r2['collar_in'])))
    print('\nRequired bore length for hub bearing RF 1.0 (mean-bearing triangular model, KP, PETG 20 MPa EST):')
    for lab, kw in (('RB', {}), ('RB x %.1f' % DAF, dict(daf=DAF)), ('2T bound', dict(bound=M2))):
        lo, hi = 0.005, 0.2
        for _ in range(40):
            mid = 0.5*(lo+hi); g = dict(x_floor=X_MOUTH0-mid, x_mouth=X_MOUTH0, e_block=0, x_sad_fwd=X_SAD_FWD0)
            if hub_rows(S, g, **kw)['hub_bear'] >= 1.0: hi = mid
            else: lo = mid
        print('  %s: %.1f mm' % (lab, hi*1e3))
    print('\n## 3. Wing end: saddle bridge socket bearing (CGE-006)')
    print('| Option | dmass g | bearing RB / RBx%.1f / 2T |' % DAF); print('|---|---|---|')
    for lab, xs, dm in SADOPT:
        g = dict(x_floor=X_FLOOR0, x_mouth=X_MOUTH0, e_block=0, x_sad_fwd=xs)
        print('| %s | %+.1f | %.2f / %.2f / %.2f |' % (lab, dm, hub_rows(S, g)['sad_bear'], hub_rows(S, g, daf=DAF)['sad_bear'], hub_rows(S, g, bound=M2)['sad_bear']))
    FBt0 = L.simulate(Fp=30.0, dt=2e-4, T=0.2, trace=True, v_sink=1.2, **P.PAD_D2)['trace'].reshape(-1, 4, 3)
    _, inf = P.wing_checks_skin(FBt0, P.skin_variants()[0][1]); shk, shs, A_cell = inf['sh_skin'], inf['sh_spar'], inf['A_cell']; Tc, _a = node_demand(S, shk)
    print('\n## 4. Wing-end node (skin -> bulkhead plate -> saddle ear -> saddle).  V0 skin torque shares: skin %.3f spar %.3f foam %.3f; enclosed cell A %.0f mm2' % (shk, shs, inf['sh_foam'], A_cell*1e6))
    print('Max wing-half torque (RB) %.2f N m -> T_skin %.2f N m per side; x%.1f -> %.2f; step 2 used 10.24 x 0.890 = 9.12' % (Tc, shk*Tc, DAF, shk*Tc*DAF))
    cf = ACP_CF['S090']*CF_SHEET
    NODE = [('N0 step 2 as drawn: lite-ply 0.5 mm plate, butt bond 0.5 mm, face 23.5 x 21, 2 pins at arm 18 mm, double shear as step 2', dict(lap=0.0005, plate_t=0.0005, plate_S=None, ear=(0.0235, 0.021), faces=1, pins=(2, 0.009, 2)), 0.0),
            ('N0b same, pins in single shear (one interface plane)', dict(lap=0.0005, plate_t=0.0005, plate_S=None, ear=(0.0235, 0.021), faces=1, pins=(2, 0.009, 1)), 0.0),
            ('N1 rung 2: 5 mm glass-tape lap, one-piece saddle with ears to y +-16.5 (ear 41.5 x 19 mm, 1.5 mm PETG), 4 pins at r 17 mm single shear, plate still lite-ply', dict(lap=0.005, plate_t=0.0005, plate_S=None, ear=(0.0415, 0.019), faces=1, pins=(4, 0.017, 1)), 2*1.5+SAD_LONG_G),
            ('N2 rung 4: N1 + CF plate 0.5 mm (ACP S 90 MPa x 0.70) instead of lite-ply, ear on both faces of the plate (clevis), pins double shear', dict(lap=0.005, plate_t=0.0005, plate_S=cf, ear=(0.0415, 0.019), faces=2, pins=(4, 0.017, 2)), 4*1.5+2*(2.7-1.0)+SAD_LONG_G)]
    print('| Option | dmass g (both sides, vs T-070 2 g lite-ply plates; EST) | demand | rows (RF) | min | additive bound (bond + pins in parallel) |'); print('|---|---|---|---|---|---|')
    for lab, o, dm in NODE:
        for sc, nm in ((1.0, 'RB'), (DAF, 'RBx%.1f' % DAF)):
            r = node_rows(shk*Tc*sc, A_cell, o); fin = [v for v in r.values() if not math.isnan(v)]
            bond = [v for k, v in r.items() if k.startswith('plate->ear')][0]; pins = [v for k, v in r.items() if k.startswith('CF pins')]
            print('| %s | %s | %s | %s | %.2f%s | %.2f |' % (lab if sc == 1.0 else '', ('%+.1f' % dm) if sc == 1.0 else '', nm, '; '.join('%s %s' % (k, ('%.2f' % v) if not math.isnan(v) else '"-" (no allowable)') for k, v in r.items()), min(fin), ' (plate shear unknown)' if any(math.isnan(v) for v in r.values()) else '', bond+(pins[0] if pins else 0)))
    sad_shear = lambda sc: PETG_IN/math.sqrt(3)/(KP*shk*Tc*sc/(2*(0.0235-0.0025)*(0.021-0.0025)*0.0025))
    print('Printed saddle body, shear flow between ear and bridge socket (box walls 2.5 mm, 21 x 18.5 mm mean cell, PETG 20/sqrt(3) in-layer EST): RF %.2f (RB), %.2f (RBx%.1f)' % (sad_shear(1), sad_shear(DAF), DAF))
    print('Saddle ring bond on the spar carries the spar torque share (%.3f x %.2f N m, ring D12 x 30 mm, epoxy 2.0 MPa EST): RF %.1f' % (shs, Tc, spar_ring(shs*Tc)))
    print('\n## 5. CAD cuts that interrupt the torsion cell (cell perimeter ahead of the hinge 383 mm = 372.6 airfoil + 8.6 cove face; wing.py core cuts)')
    a1 = _arc(lambda p: p[0] <= 0.0225 and p[1] > 0.0055); a2 = _arc(lambda p: 0.0295 <= p[0] <= 0.071 and not _zup(p)); a3 = _arc(lambda p: 0 <= p[0] <= 0.056 and not _zup(p)); a4 = _arc(lambda p: 0.1245 <= p[0] <= 0.1655 and _zup(p))
    print('- tray slot (x -0.010..0.0225, |y| <= 0.057, open above z > 5.5 mm): top skin arc removed %.1f mm (%.1f %%).' % (a1, a1/3.83))
    print('- saddle slot (x 0.0295..0.071, |y| <= 0.0165, open below, up to z 0.0115): bottom skin arc removed %.1f mm and the foam below z 11.5 mm (almost the full depth; airfoil zu 9.4..12.4 mm there).' % a2)
    print('- bridge slot (x 0..0.056, |y| <= 0.0085, open below): bottom skin arc removed %.1f mm.' % a3)
    print('- servo pocket (x 0.1245..0.1655, |y - 0.200| <= 0.0225, open to the upper skin): top skin arc removed %.1f mm (%.1f %%) at y 0.1775..0.2225 (inside the T-071 cell, not in my scope).' % (a4, a4/3.83))
    print('=> a bulkhead plate inside the saddle slot (|y| < 0.0165) has no closed skin perimeter. The plate station must be y >= 0.0165 (foam and skin resume), so the saddle ears reach y = +-0.0165, 6 mm beyond the saddle box end face (0.0105) used in step 2.')
    print('\n## 6. CAD envelope check of the hub-end option H3 (read-only stub build of amodel; world part boxes)')
    box = ((X_MOUTH0, -0.012, -0.016), (X_MOUTH0+0.012, 0.012, 0.008)); hits = envelope_check(box)
    print('test box x %.3f..%.3f, y +-0.012, z -0.016..+0.008. Parts whose boxes overlap it (mm, lo / hi):' % (box[0][0], box[1][0]))
    for h in hits: print('  ', h)
    print('  expected: CGE-004 (the bridge itself, in the bore) and CGE-008 (tray: plate z 6..8 over x -0.045..-0.033 needs a 24 x 12 mm notch; the pack front lip is at x -0.0355..-0.0335, z >= 8, above the extension top z = 8). Nothing else lies in the box.')
    print('  y clearance: raceway notches beside the hub pad flange start at |y| = 13.6 mm (wing.py PADN_Y); 24 mm width leaves 1.6 mm per side. Hub CG not re-solved.')
    for lab, rung, g, dm in HUBOPT[1:4]:
        xm = X_MOUTH0+0.5*g['e_block']*1e-3 if g['e_block'] else -0.050
        print('  CG shift of %s: %+.2f mm (dm %+.1f g at x %.4f; CAD CG 21.37 mm, 1273 g; forward trim end limit 19.3 mm, CL-A-CG-TRIM-FWD, trim fwd 6 mm is about -1.27 mm EST)' % (lab[:2], cg_shift_mm(dm, xm), dm, xm))
    dcg = -2*88.26*0.0125/1273*1e3
    print('  H4 (tube B 12.5 mm forward): 2 x 88.26 g motors move 12.5 mm forward: CG %+.2f mm -> forward trim end about %.1f mm (limit 19.3): FAILS by about %.1f mm (EST)' % (dcg, 21.369-1.27+dcg, 19.3-(21.369-1.27+dcg)))
    print('\nwall %.0f s' % (time.time()-t0))
if __name__ == '__main__': main()
