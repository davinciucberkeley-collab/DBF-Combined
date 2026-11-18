"""fea_hub.py - 3-D FEA of the D-202 hub: two continuous 12 x 10 carbon arm tubes (UR-LL and UL-LR) crossing through a printed
PETG hub block, with the bridge-tube socket behind it.

    python -I redesign/qp/A/structures/fea_hub.py [--level 0|1] [--tag NAME] [--p k=v ...]

Why: FEA-ARM.md (D-201) showed the 0.8 mm webs of the D-193 hub fail; printed-only fixes could not pass under the 1.47 kg gate,
so the user chose continuous carbon arms (2026-11-16). With each opposite pair one tube, the balanced arm moments stay in the
carbon; the hub only carries the net force and the unbalanced (differential-thrust) moments into the bridge tube.

Model (mm, N, MPa; hub frame: x = hub axis (thrust is -x), y = span, z = up, origin = hub centre). Parameters in GEO, overridable:
  - tube A along uA = (0, cos phi, sin phi) at x = XA (UR at +s, LL at -s); tube B along uB = (0, cos phi, -sin phi) at x = XB (LR +s, UL -s);
    phi = PHI['UR'] from common.py (34.4 deg); stubs to s = +-S_END, the outer arm (to the motors) replaced by its exact end loads;
  - hub: a sleeve (wall SLV_W) round each tube over s = +-L_SLV, a centre block (x XA-R..XB+R, |y|, |z| <= CB), the bridge boss
    (r R_BR) from the block's aft face to HUB_X1 with the bridge bore (BR_RO; D-206: 16 mm, axis z BR_Z -2 mm) from X_BR0;
  - phase-lead exits: a 4.8 mm hole through the tube wall and the sleeve wall at s = +-S_HOLE on each tube, on the tangential face
    (the neutral axis of thrust bending);
  - support: the bridge bore is fixed (the strut sockets, tray and saddle are left out: every net load goes into the bridge: conservative).
Loads: for each motor, thrust along its axis n(st) (mrot = rotX(PHI) rotY(CANT), as the CAD), shaft torque by spin direction (MRP:
UR, LL clockwise), the gyroscopic moment I w x Omega for a body rate about y or z (both signs), 1P; carried from the motor base point to
the stub end exactly (force + moment). Combinations: every thrust pattern with each motor at idle (0) or at the spin cap (16), x torque
sign x gyro axis/sign x 1P direction. Ground cases: 30 N strike on one prop (3 directions) and the blade stop.
Same element, materials, allowables and factors as fea_arm.py (imported).
"""
import argparse
import itertools
import json
import math
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fea_arm as FA  # noqa: E402
C, W = FA.C, FA.W
OUT = FA.OUT

PHI_D = C.PHI['UR']
GEO = dict(XA=-6.5, XB=6.5, S_END=100.0, L_SLV=24.0, SLV_W=2.0, CB=10.0, R_BR=W.R_BR * 1e3, BR_RO=W.BR_RO * 1e3, BR_RI=W.BR_RI * 1e3, BR_Z=W.BR_Z * 1e3, X_BR0=15.0, X_HUB1=(W.HUB_X1 - C.HUB[0]) * 1e3,
           S_HOLE=18.0, HOLE_R=2.4, TUBE_RO=6.0, TUBE_RI=5.0, DBL=1.0, DBL_T=1.0, DBL_S0=11.0, DBL_S1=25.0, BR_L=40.0, R_CB=3.0, PIN_R=1.5, PIN_C=1.0, PIN_S=8.0, E_PIN=70000.0)   # PIN_*: 3 mm pins along x (D-202): one through both tubes at the crossing (PIN_C), one through each tube at s = +-PIN_S (0 = none); E_PIN pultruded CF rod, isotropic EST   # R_CB: edge radius of the centre block   # BR_L: modelled bridge tube aft of HUB_X1, fixed at its end   # DBL: carbon doubler sleeve 14 x 12 over each lead hole
STATIONS = {'UR': ('A', 1), 'LL': ('A', -1), 'LR': ('B', 1), 'UL': ('B', -1)}
SPIN = {s: (-1 if s in ('UR', 'LL') else 1) for s in STATIONS}        # propulsion.py MRP: UR, LL clockwise (-1), others CCW (+1)


def axes():
    p = math.radians(PHI_D)
    return {'A': np.array([0.0, math.cos(p), math.sin(p)]), 'B': np.array([0.0, math.cos(p), -math.sin(p)])}


def tube_x(t):
    return GEO['XA'] if t == 'A' else GEO['XB']


def build_mesh(level, path):
    import gmsh
    g = GEO
    U = axes()
    gmsh.initialize(['-noenv'])
    gmsh.option.setNumber('General.Terminal', 0)
    occ = gmsh.model.occ
    hub_parts, tubes = [], {}
    ro, ri = g['TUBE_RO'], g['TUBE_RI']
    for t in ('A', 'B'):
        u, x0 = U[t], tube_x(t)
        L = g['L_SLV']
        hub_parts.append((3, occ.addCylinder(x0 - L * u[0], -L * u[1], -L * u[2], 2 * L * u[0], 2 * L * u[1], 2 * L * u[2], ro + g['SLV_W'] + g['DBL'] * g['DBL_T'])))
    cb = g['CB']
    xa0, xb1 = g['XA'] - ro - g['SLV_W'], g['XB'] + ro + g['SLV_W']
    bx = occ.addBox(xa0, -cb, -cb, xb1 - xa0, 2 * cb, 2 * cb)
    if g['R_CB'] > 0:                                     # round the four block edges that run along x (FEA peak there, D-202)
        occ.synchronize()
        ed = [e for d_, e in occ.getEntities(1) if d_ == 1 and (lambda b: abs(b[3] - b[0]) > 1 and abs(b[4] - b[1]) < 0.1 and abs(b[5] - b[2]) < 0.1)(occ.getBoundingBox(1, e))
              and e in [c[1] for c in gmsh.model.getBoundary(gmsh.model.getBoundary([(3, bx)], combined=False, oriented=False), combined=False, oriented=False) if c[0] == 1]]
        bx = occ.fillet([bx], ed, [g['R_CB']])[0][1]
    hub_parts.append((3, bx))
    hub_parts.append((3, occ.addCylinder(xb1 - 0.5, 0, g['BR_Z'], g['X_HUB1'] - xb1 + 0.5, 0, 0, g['R_BR'])))
    hub, _ = occ.fuse([hub_parts[0]], hub_parts[1:])
    cuts = [(3, occ.addCylinder(g['X_BR0'], 0, g['BR_Z'], g['X_HUB1'] - g['X_BR0'] + 1, 0, 0, g['BR_RO']))]
    for t in ('A', 'B'):
        u, x0 = U[t], tube_x(t)
        S = g['S_END'] + 1
        cuts.append((3, occ.addCylinder(x0 - S * u[0], -S * u[1], -S * u[2], 2 * S * u[0], 2 * S * u[1], 2 * S * u[2], ro)))
    if g['DBL']:
        for t in ('A', 'B'):
            u, x0 = U[t], tube_x(t)
            for sg in (1, -1):
                a0, a1 = sorted((sg * g['DBL_S0'], sg * g['DBL_S1']))
                cuts.append((3, occ.addCylinder(x0 + a0 * u[0], a0 * u[1], a0 * u[2], (a1 - a0) * u[0], (a1 - a0) * u[1], (a1 - a0) * u[2], ro + g['DBL_T'])))
    hub, _ = occ.cut(hub, cuts, removeTool=True)
    dbls = []
    if g['DBL']:
        for t in ('A', 'B'):
            u, x0 = U[t], tube_x(t)
            for sg in (1, -1):
                a0, a1 = sorted((sg * g['DBL_S0'], sg * g['DBL_S1']))
                o = occ.addCylinder(x0 + a0 * u[0], a0 * u[1], a0 * u[2], (a1 - a0) * u[0], (a1 - a0) * u[1], (a1 - a0) * u[2], ro + g['DBL_T'])
                i = occ.addCylinder(x0 + (a0 - 1) * u[0], (a0 - 1) * u[1], (a0 - 1) * u[2], (a1 - a0 + 2) * u[0], (a1 - a0 + 2) * u[1], (a1 - a0 + 2) * u[2], ro)
                dd, _ = occ.cut([(3, o)], [(3, i)])
                dbls.append((t, dd))
    for t in ('A', 'B'):
        u, x0 = U[t], tube_x(t)
        S = g['S_END']
        o = occ.addCylinder(x0 - S * u[0], -S * u[1], -S * u[2], 2 * S * u[0], 2 * S * u[1], 2 * S * u[2], ro)
        i = occ.addCylinder(x0 - (S + 1) * u[0], -(S + 1) * u[1], -(S + 1) * u[2], 2 * (S + 1) * u[0], 2 * (S + 1) * u[1], 2 * (S + 1) * u[2], ri)
        tubes[t], _ = occ.cut([(3, o)], [(3, i)])
    o = occ.addCylinder(g['X_BR0'], 0, g['BR_Z'], g['X_HUB1'] + g['BR_L'] - g['X_BR0'], 0, 0, g['BR_RO'])   # bridge tube (D-206: 16 x 14 at z -2), bonded in the bore
    i = occ.addCylinder(g['X_BR0'] - 1, 0, g['BR_Z'], g['X_HUB1'] + g['BR_L'] - g['X_BR0'] + 2, 0, 0, g['BR_RI'])
    tubes['BR'], _ = occ.cut([(3, o)], [(3, i)])
    # pins along x (D-202): cut their volume out of hub and tubes, add them as their own bodies (bonded)
    pins = []
    xa0p, xb1p = g['XA'] - ro - g['SLV_W'], g['XB'] + ro + g['SLV_W']
    if g['PIN_C']:
        pins.append(occ.addCylinder(xa0p, 0, 0, xb1p - xa0p, 0, 0, g['PIN_R']))
    if g['PIN_S']:
        for t in ('A', 'B'):
            u, x0 = U[t], tube_x(t)
            for sg in (1, -1):
                c = np.array([x0, 0, 0]) + sg * g['PIN_S'] * u
                h = ro + g['SLV_W']
                pins.append(occ.addCylinder(c[0] - h, c[1], c[2], 2 * h, 0, 0, g['PIN_R']))
    if pins:
        pv = [(3, q) for q in pins]
        hub, _ = occ.cut(hub, pv, removeTool=False)
        for t in ('A', 'B'):
            tubes[t], _ = occ.cut(tubes[t], pv, removeTool=False)
    tubes['PIN'] = [(3, q) for q in pins]
    # phase-lead exit holes (tube wall + sleeve wall), tangential face tA = x_hat x u
    holes = []
    for t in ('A', 'B'):
        u, x0 = U[t], tube_x(t)
        tv = np.cross([1.0, 0, 0], u)
        for sgn in (1, -1):
            c = np.array([x0, 0, 0]) + sgn * g['S_HOLE'] * u
            holes.append((3, occ.addCylinder(*c, *(tv * (ro + g['SLV_W'] + g['DBL_T'] + 1)), g['HOLE_R'])))
    hub, _ = occ.cut(hub, holes, removeTool=False)
    for t in ('A', 'B'):
        tubes[t], _ = occ.cut(tubes[t], holes, removeTool=False)
    for k, (t, dd) in enumerate(dbls):
        dd2, _ = occ.cut(dd, holes, removeTool=False)
        tubes[t] = tubes[t] + dd2
    occ.remove(holes, recursive=True)
    allin = hub + tubes['A'] + tubes['B'] + tubes['BR'] + tubes['PIN']
    _, mp = occ.fragment(allin, [])
    occ.synchronize()
    groups = {'hub': [], 'A': [], 'B': [], 'BR': [], 'PIN': []}
    for (d, tg), kids in zip(allin, mp[:len(allin)]):
        k = 'hub' if (d, tg) in hub else 'A' if (d, tg) in tubes['A'] else 'B' if (d, tg) in tubes['B'] else 'BR' if (d, tg) in tubes['BR'] else 'PIN'
        groups[k] += [kk[1] for kk in kids]
    hub_vol = sum(occ.getMass(3, tg) for tg in set(groups['hub']))
    for i, (k, v) in enumerate(groups.items()):
        gmsh.model.addPhysicalGroup(3, sorted(set(v)), i + 1, name=k)
    f = gmsh.model.mesh.field
    s = {0: 1.0, 1: 0.78}[level] * g.get('MS', 1.0)       # MS: mesh-size scale (memory: the direct solve must fit in 64 GB)
    b1 = f.add('Ball'); f.setNumber(b1, 'Radius', g['L_SLV'] + 10); f.setNumber(b1, 'VIn', 0.65 * s); f.setNumber(b1, 'VOut', 1.6 * s)
    f.setNumber(b1, 'Thickness', 15)
    b2 = f.add('Box'); f.setNumber(b2, 'VIn', 0.65 * s); f.setNumber(b2, 'VOut', 1.6 * s)
    for k, v in zip(('XMin', 'XMax', 'YMin', 'YMax', 'ZMin', 'ZMax'), (xb1 - 1, g['X_HUB1'] + 1, -9, 9, -9, 9)):
        f.setNumber(b2, k, v)
    mn = f.add('Min'); f.setNumbers(mn, 'FieldsList', [b1, b2]); f.setAsBackgroundMesh(mn)
    for k, v in (('Mesh.MeshSizeExtendFromBoundary', 0), ('Mesh.MeshSizeFromPoints', 0), ('Mesh.MeshSizeFromCurvature', 0),
                 ('Mesh.ElementOrder', 2), ('Mesh.HighOrderOptimize', 1), ('General.NumThreads', 16)):
        gmsh.option.setNumber(k, v)
    gmsh.model.mesh.generate(3)
    nt, xyz, _ = gmsh.model.mesh.getNodes()
    X = xyz.reshape(-1, 3)
    idx = {int(tg): i for i, tg in enumerate(nt)}
    els, mat = [], []
    for i, k in enumerate(groups):
        for v in sorted(set(groups[k])):
            et, _, en = gmsh.model.mesh.getElements(3, v)
            for tt, e in zip(et, en):
                if tt == 11:
                    a = np.array([idx[int(n)] for n in e]).reshape(-1, 10)
                    els.append(a); mat.append(np.full(len(a), i))
    E = np.vstack(els); M = np.concatenate(mat)
    used = np.unique(E)
    remap = -np.ones(len(X), int); remap[used] = np.arange(len(used))
    gmsh.finalize()
    print('hub block volume %.0f mm3 = %.2f g PETG' % (hub_vol, hub_vol * 1.27e-3), flush=True)
    np.savez_compressed(path, X=X[used], E=remap[E], M=M, hub_vol=hub_vol)


# ---------------- rotated transversely isotropic stiffness ----------------
VI = [(0, 0), (1, 1), (2, 2), (1, 2), (0, 2), (0, 1)]


def to_tensor(Cv):
    T = np.zeros((3, 3, 3, 3))
    for a, (i, j) in enumerate(VI):
        for b, (k, l) in enumerate(VI):
            for (p, q) in {(i, j), (j, i)}:
                for (r, s) in {(k, l), (l, k)}:
                    T[p, q, r, s] = Cv[a, b]
    return T


def to_voigt(T):
    return np.array([[T[i, j, k, l] for (k, l) in VI] for (i, j) in VI])


def D_tube(u):
    """FA.D_ti_y() has the fibre along y; rotate y -> u (u in the y-z plane: rotation about x)."""
    ang = math.atan2(u[2], u[1])
    c, s = math.cos(ang), math.sin(ang)
    R = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    T = np.einsum('pi,qj,rk,sl,ijkl->pqrs', R, R, R, R, to_tensor(FA.D_ti_y()))
    return to_voigt(T)


# ---------------- loads ----------------
def motor_frame(st):
    phi = math.radians(C.PHI[st]); cant = math.radians(C.CANT)
    rx = np.array([[1, 0, 0], [0, math.cos(phi), -math.sin(phi)], [0, math.sin(phi), math.cos(phi)]])
    ry = np.array([[math.cos(cant), 0, math.sin(cant)], [0, 1, 0], [-math.sin(cant), 0, math.cos(cant)]])
    R = rx @ ry
    n = R @ np.array([-1.0, 0, 0])                         # plate -> motor = thrust direction on the airframe
    t, sg = STATIONS[st]
    u = axes()[t] * sg                                     # outward arm direction
    station = np.array([tube_x(t), 0, 0]) + C.R_M * 1e3 * u
    P = station + 12.0 * n
    return n, u, station, P


def stub_end(st):
    t, sg = STATIONS[st]
    return np.array([tube_x(t), 0, 0]) + sg * GEO['S_END'] * axes()[t]


def to_stub(st, F, Mo, at):
    """Force F (N) and moment Mo (N mm) applied at point `at` -> equivalent at the stub end."""
    e = stub_end(st)
    return F, Mo + np.cross(at - e, F)


def flight_combos(T_hi, Q_hi):
    gy = FA.M_GYRO * 1e3
    out = []
    for pattern in itertools.product((0, 1), repeat=4):
        for qs in (1, -1):
            for gax, gs in itertools.product((np.array([0, 1.0, 0]), np.array([0, 0, 1.0])), (1, -1)):
                for pd in (0, 1, 2, 3):
                    loads = {}
                    for k, st in enumerate(('UR', 'LL', 'LR', 'UL')):
                        n, u, station, P = motor_frame(st)
                        on = pattern[k]
                        T, Q = T_hi * on, Q_hi * on
                        F = T * n
                        Mo = qs * SPIN[st] * Q * 1e3 * n + (gs * gy * SPIN[st] * on) * np.cross(n, gax)
                        t1 = u - (u @ n) * n; t1 /= np.linalg.norm(t1); t2 = np.cross(n, t1)
                        pdir = [t1, t2, -t1, -t2][pd]
                        Fp = FA.F_1P * on * pdir
                        Pp = station + FA.X_PROP * n
                        F1, M1 = to_stub(st, F, Mo, P)
                        F2, M2 = to_stub(st, Fp, np.zeros(3), Pp)
                        loads[st] = (F1 + F2, M1 + M2)
                    out.append(loads)
    return out


def ground_combos():
    out = []
    for st in ('UR',):
        n, u, station, P = motor_frame(st)
        t1 = u - (u @ n) * n; t1 /= np.linalg.norm(t1); t2 = np.cross(n, t1)
        Pp = station + FA.X_PROP * n
        for d in (t1, t2, -t1, -t2):
            out.append(('S2', {st: to_stub(st, FA.F_STRIKE * d, np.zeros(3), Pp)}))
        for sg in (1, -1):
            out.append(('S3', {st: to_stub(st, np.zeros(3), sg * FA.F_STRIKE * FA.R_BLADE * 1e3 * n, P)}))
            out.append(('S1', {st: to_stub(st, sg * FA.F_STRIKE * n, np.zeros(3), P)}))
    return out


def end_nodes(X, st):
    t, sg = STATIONS[st]
    u = axes()[t]
    s = (X - np.array([tube_x(t), 0, 0])) @ u
    r = np.linalg.norm((X - np.array([tube_x(t), 0, 0])) - np.outer(s, u), axis=1)
    return np.where((np.abs(s - sg * GEO['S_END']) < 0.02) & (r > GEO['TUBE_RI'] - 0.02))[0]


def fixed_nodes(X):
    r = np.hypot(X[:, 1], X[:, 2] - GEO['BR_Z'])
    return np.where((r > GEO['BR_RI'] - 0.02) & (r < GEO['BR_RO'] + 0.02) & (np.abs(X[:, 0] - (GEO['X_HUB1'] + GEO['BR_L'])) < 0.02))[0]


RELEASE = False          # --release: glue between the hub sleeves and the arm tubes has let go (pins-only case, D-202)
K_PEN = 1.0e5            # N/mm per node pair: normal-only tie (bearing kept, no glue shear or torsion; separation not modelled)


def release_interface(X, E, M):
    """Duplicate the hub-side nodes on each arm-tube / hub interface (not at the pins) and return the node pairs with their
    radial normals; the pairs are later tied in the normal direction only (frictionless, no glue)."""
    U = axes(); pairs = []
    pinn = np.unique(E[M == 4]) if (M == 4).any() else np.array([], int)
    for t, mi in (('A', 1), ('B', 2)):
        hubn = np.unique(E[M == 0]); tn = np.unique(E[M == mi])
        itf = np.setdiff1d(np.intersect1d(hubn, tn), pinn)
        new = np.arange(len(X), len(X) + len(itf))
        X = np.vstack([X, X[itf]])
        lut = np.full(len(X), -1); lut[itf] = new
        Eh = E[M == 0]; m = np.isin(Eh, itf); Eh[m] = lut[Eh[m]]; E[M == 0] = Eh
        u = U[t]; d = X[itf] - np.array([tube_x(t), 0, 0]); rv = d - np.outer(d @ u, u)
        pairs.append((itf, new, rv / np.linalg.norm(rv, axis=1)[:, None]))
        print('released %d interface nodes on tube %s' % (len(itf), t), flush=True)
    return X, E, pairs


def penalty(n_nodes, pairs):
    from scipy.sparse import coo_matrix
    R, Cc, V = [], [], []
    for a, b, nv in pairs:
        nn = K_PEN * np.einsum('ei,ej->eij', nv, nv)
        for (p_, q_, sg) in ((a, a, 1), (b, b, 1), (a, b, -1), (b, a, -1)):
            for i in range(3):
                for j in range(3):
                    R.append(3 * p_ + i); Cc.append(3 * q_ + j); V.append(sg * nn[:, i, j])
    return coo_matrix((np.concatenate(V), (np.concatenate(R), np.concatenate(Cc))), shape=(3 * n_nodes, 3 * n_nodes)).tocsr()


def run(level, tag):
    os.makedirs(OUT, exist_ok=True)
    import hashlib                                       # cache key includes the geometry, so --p never reuses a stale mesh
    gh = hashlib.md5(json.dumps(GEO, sort_keys=True).encode()).hexdigest()[:8]
    mp = os.path.join(OUT, 'hub_mesh_L%d_%s_%s.npz' % (level, tag, gh))
    if not os.path.exists(mp):
        build_mesh(level, mp)
    d = np.load(mp); X, E, M = d['X'], d['E'], d['M']; hub_vol = float(d['hub_vol'])
    U = axes()
    Rx = np.array([[0, 1.0, 0], [-1.0, 0, 0], [0, 0, 1.0]])               # y -> x
    D_br = to_voigt(np.einsum('pi,qj,rk,sl,ijkl->pqrs', Rx, Rx, Rx, Rx, to_tensor(FA.D_ti_y())))
    Ds = [FA.D_iso(FA.E_PETG, FA.NU_PETG), D_tube(U['A']), D_tube(U['B']), D_br, FA.D_iso(GEO['E_PIN'], 0.3)]
    if RELEASE:
        E = E.copy(); X, E, pairs = release_interface(X, E, M)
    K, Bs, dof, dets = FA.assemble(X, E, M, Ds)
    if RELEASE:
        K = (K + penalty(len(X), pairs)).tocsr()
    fix = fixed_nodes(X)
    fd = np.zeros(3 * len(X), bool); fd[(3 * fix[:, None] + np.arange(3)).ravel()] = True
    free = np.where(~fd)[0]
    Kf = K[free][:, free].tocsc()
    sts = ('UR', 'LL', 'LR', 'UL')
    basis = []
    for st in sts:
        nodes = end_nodes(X, st)
        e = stub_end(st)
        for k in range(6):
            F = np.zeros(3); Mo = np.zeros(3)
            (F if k < 3 else Mo)[k % 3] = 1.0
            f = np.zeros((len(X), 3)); f[nodes] = FA.rbe3_loads(X, nodes, F, Mo, e)
            basis.append(f.ravel()[free])
    RHS = np.column_stack(basis)
    Uf = FA.solve(Kf, RHS)
    Ub = np.zeros((RHS.shape[1], 3 * len(X))); Ub[:, free] = Uf.T
    Rf = (K @ Ub.T).T.reshape(len(basis), -1, 3)
    eq = []
    for j in range(len(basis)):
        st = sts[j // 6]; e = stub_end(st); k = j % 6
        F = np.zeros(3); Mo = np.zeros(3); (F if k < 3 else Mo)[k % 3] = 1.0
        Rs = -Rf[j, fix].sum(0); Mr = -np.cross(X[fix] - e, Rf[j, fix]).sum(0)
        eq.append(max(np.linalg.norm(Rs - F), np.linalg.norm(Mr - Mo) / 100))
    print('equilibrium max error %.1e' % max(eq), flush=True)
    XE = X[E]
    xg = np.stack([np.einsum('a,eai->ei', FA.Nq(FA.GP[g]), XE) for g in range(4)], 1)
    S = np.zeros((len(basis), len(E), 4, 6))
    for g in range(4):
        for m, D in enumerate(Ds):
            sm = M == m
            S[:, sm, g] = np.einsum('kl,elj,bej->bek', D, Bs[g][sm], Ub[:, dof[sm]])
    return dict(X=X, E=E, M=M, S=S, xg=xg, hub_vol=hub_vol, eq=max(eq), nel=len(E), ndof=len(free))


def coeffs(loads):
    c = np.zeros(24)
    for i, st in enumerate(('UR', 'LL', 'LR', 'UL')):
        if st in loads:
            F, Mo = loads[st]
            c[6 * i:6 * i + 3] = F; c[6 * i + 3:6 * i + 6] = Mo
    return c


def tube_stress(sig, xr, t):
    """Axial, hoop, shear (axial planes) in the frame of tube t."""
    u = axes()[t]; x0 = np.array([tube_x(t), 0, 0])
    d = xr - x0; s = d @ u; rv = d - np.outer(s, u); rn = rv / np.maximum(np.linalg.norm(rv, axis=1), 1e-9)[:, None]
    th = np.cross(u, rn)
    T = FA_tensor(sig)
    ax = np.einsum('i,eij,j->e', u, T, u)
    hp = np.einsum('ei,eij,ej->e', th, T, th)
    tr = np.einsum('i,eij,ej->e', u, T, rn); tt = np.einsum('i,eij,ej->e', u, T, th)
    return ax, hp, np.hypot(tr, tt), s


def FA_tensor(sig):
    xx, yy, zz, yz, xz, xy = [sig[:, i] for i in range(6)]
    return np.stack([np.stack([xx, xy, xz], -1), np.stack([xy, yy, yz], -1), np.stack([xz, yz, zz], -1)], -2)


def evaluate(res, combos):
    S, M, xg = res['S'], res['M'], res['xg']
    Cs = np.array([coeffs(c) for c in combos])                 # (ncombo, 24)
    out = {}
    hub = M == 0
    Sh = S[:, hub].reshape(24, -1, 6)
    xh = xg[hub].reshape(-1, 3)
    best = None
    for ci in range(0, len(Cs), 64):
        sig = np.einsum('ck,kps->cps', Cs[ci:ci + 64], Sh)
        p1, vm = FA.principal(sig)
        m = p1.max(1)
        j = int(np.argmax(m))
        if best is None or m[j] > best[0]:
            best = (float(m[j]), ci + j, p1[j])
    out['hub_peak'] = best[0]
    p1b = best[2]
    zones = {'bridge boss (aft of the block)': xh[:, 0] > GEO['XB'] + GEO['TUBE_RO'] + GEO['SLV_W'],
             'centre block / crossing': (np.abs(xh[:, 1]) < GEO['CB']) & (np.abs(xh[:, 2]) < GEO['CB']) & (xh[:, 0] <= GEO['XB'] + GEO['TUBE_RO'] + GEO['SLV_W']),
             'sleeves outside the block': ~((np.abs(xh[:, 1]) < GEO['CB']) & (np.abs(xh[:, 2]) < GEO['CB'])) & (xh[:, 0] <= GEO['XB'] + GEO['TUBE_RO'] + GEO['SLV_W'])}
    out['hub_zones_worst_combo'] = {k: dict(max=float(p1b[z].max()), p99=float(np.percentile(p1b[z], 99)), p95=float(np.percentile(p1b[z], 95))) for k, z in zones.items() if z.any()}
    out['hub_peak_at'] = xh[int(np.argmax(p1b))].round(2).tolist()
    # envelope p99 / max per zone over all combos
    env = {k: [0.0, 0.0] for k in zones}
    for ci in range(0, len(Cs), 64):
        sig = np.einsum('ck,kps->cps', Cs[ci:ci + 64], Sh)
        p1, _ = FA.principal(sig)
        for k, z in zones.items():
            if z.any():
                env[k][0] = max(env[k][0], float(p1[:, z].max()))
                env[k][1] = max(env[k][1], float(np.percentile(p1[:, z], 99, axis=1).max()))
    out['hub_zones_envelope'] = {k: dict(max=v[0], p99=v[1]) for k, v in env.items()}
    for t, mi in (('A', 1), ('B', 2)):
        sel = M == mi
        St = S[:, sel].reshape(24, -1, 6); xt = xg[sel].reshape(-1, 3)
        worst = [0.0, 0.0, 0.0, None, None]
        u_ = axes()[t]; keep = np.abs((xt - np.array([tube_x(t), 0, 0])) @ u_) < GEO['S_END'] - 15   # skip the load-application zone at the stub ends
        for ci in range(0, len(Cs), 32):
            sig = np.einsum('ck,kps->cps', Cs[ci:ci + 32], St)
            for c in range(sig.shape[0]):
                ax, hp, sh, s = tube_stress(sig[c], xt, t)
                ax, hp, sh, s = ax[keep], hp[keep], sh[keep], s[keep]
                if np.abs(ax).max() > worst[0]:
                    worst[0] = float(np.abs(ax).max()); worst[3] = float(s[np.argmax(np.abs(ax))])
                worst[1] = max(worst[1], float(np.abs(hp).max()))
                if sh.max() > worst[2]:
                    worst[2] = float(sh.max()); worst[4] = float(s[np.argmax(sh)])
        out['tube_' + t] = dict(axial=worst[0], axial_at_s=worst[3], hoop=worst[1], shear=worst[2], shear_at_s=worst[4])
    # bond: PETG gauss points within 0.35 mm of a tube's outer surface, inside the sleeve
    bmax = [0.0, 0.0, 0.0]
    for t in ('A', 'B'):
        u = axes()[t]; x0 = np.array([tube_x(t), 0, 0])
        d = xh - x0; s = d @ u; rv = d - np.outer(s, u); r = np.linalg.norm(rv, axis=1)
        sel = (r < GEO['TUBE_RO'] + 0.35) & (np.abs(s) < GEO['L_SLV'])
        nr = rv[sel] / r[sel, None]
        for ci in range(0, len(Cs), 64):
            sig = np.einsum('ck,kps->cps', Cs[ci:ci + 64], Sh[:, sel])
            for c in range(sig.shape[0]):
                T = FA_tensor(sig[c]); tv = np.einsum('eij,ej->ei', T, nr); tn = np.einsum('ei,ei->e', tv, nr)
                ts = np.linalg.norm(tv - tn[:, None] * nr, axis=1)
                bmax[0] = max(bmax[0], float(ts.max())); bmax[1] = max(bmax[1], float(tn.max())); bmax[2] = max(bmax[2], float(np.percentile(ts, 99)))
                for sg_ in (1, -1):                         # mean shear over each arm's bonded length (the quantity a lap-shear allowable is for)
                    w = (s[sel] * sg_) > 0
                    if w.any(): bmax.append(float(ts[w].mean()))
    out['bond'] = dict(shear=bmax[0], peel=bmax[1], shear_p99=bmax[2], shear_mean_worst_arm=max(bmax[3:]) if len(bmax) > 3 else None)
    pin = M == 4                                            # pin von Mises (max, p99) over all combos
    if pin.any():
        Sp = S[:, pin].reshape(24, -1, 6); pm = [0.0, 0.0]
        for ci in range(0, len(Cs), 64):
            sig = np.einsum('ck,kps->cps', Cs[ci:ci + 64], Sp)
            _, vm = FA.principal(sig)
            pm[0] = max(pm[0], float(vm.max())); pm[1] = max(pm[1], float(np.percentile(vm, 99, axis=1).max()))
        out['pin_vm'] = dict(max=pm[0], p99=pm[1])
    return out


ALLOW = FA.ALLOW                     # cf_axial 350, cf_hoop 40, cf_shear 30, petg 20 MPa (fea_arm.py, EST)


def element_fields(res, combos, fac_petg, fac_cf):
    """Per element, enveloped over the combos and the 4 Gauss points: utilisation = stress x required factor / allowable
    (PETG: max principal / 20; CFRP tubes and bridge: max of |axial| / 350, |hoop or transverse| / 40, shear / 30) and the
    governing stress (MPa). Pins: von Mises only (no allowable in the analysis, utilisation NaN). NaN where the model is not
    judged: tube stubs within 15 mm of the loaded ends, and the last 10 mm of the bridge at its fixed end."""
    S, M, xg = res['S'], res['M'], res['xg']
    ne = len(M); U = np.zeros(ne); SG = np.zeros(ne)
    Cs = np.array([coeffs(c) for c in combos])
    xgf = xg.reshape(-1, 3)
    for ci in range(0, len(Cs), 4):
        for c in Cs[ci:ci + 4]:
            sig = np.einsum('k,kegs->egs', c, S)                       # (ne, 4, 6)
            for m in range(5):
                sel = M == m
                if not sel.any():
                    continue
                sg = sig[sel]
                if m == 0:
                    p1, _ = FA.principal(sg); u = p1 * fac_petg / ALLOW['petg']; s_ = p1
                elif m in (1, 2):
                    ax, hp, sh, _ = tube_stress(sg.reshape(-1, 6), xg[sel].reshape(-1, 3), 'A' if m == 1 else 'B')
                    ax, hp, sh = (v.reshape(-1, 4) for v in (ax, hp, sh))
                    r = np.stack([np.abs(ax) / ALLOW['cf_axial'], np.abs(hp) / ALLOW['cf_hoop'], sh / ALLOW['cf_shear']])
                    k = r.argmax(0); u = r.max(0) * fac_cf
                    s_ = np.choose(k, [np.abs(ax), np.abs(hp), sh])
                elif m == 3:
                    ax = np.abs(sg[..., 0]); tr = np.maximum(np.abs(sg[..., 1]), np.abs(sg[..., 2])); sh = np.hypot(sg[..., 4], sg[..., 5])
                    r = np.stack([ax / ALLOW['cf_axial'], tr / ALLOW['cf_hoop'], sh / ALLOW['cf_shear']])
                    k = r.argmax(0); u = r.max(0) * fac_cf; s_ = np.choose(k, [ax, tr, sh])
                else:
                    _, vm = FA.principal(sg); u = np.full(vm.shape, np.nan); s_ = vm
                ue = np.nanmax(u, 1) if m != 4 else u[:, 0]
                U[sel] = np.fmax(U[sel], ue) if m != 4 else np.nan
                SG[sel] = np.maximum(SG[sel], s_.max(1))
    xc = xg.mean(1)
    for m, t in ((1, 'A'), (2, 'B')):
        sel = M == m; d = xc[sel] - np.array([tube_x(t), 0, 0]); s = d @ axes()[t]
        far = np.abs(s) > GEO['S_END'] - 15
        U[np.where(sel)[0][far]] = np.nan; SG[np.where(sel)[0][far]] = np.nan
    far = (M == 3) & (xc[:, 0] > GEO['X_HUB1'] + GEO['BR_L'] - 10)
    U[far] = np.nan; SG[far] = np.nan
    return U, SG


def save_fields(res, path):
    """Surface skin of each material (corner nodes of the tet10 faces not shared with an element of the same material),
    with per-vertex utilisation and stress (max over the adjacent elements), for F1, F2 (flight, required factors) and
    S1, S2 (30 N prop strike, damage case at factor 1.0, D-202). Coordinates in mm, hub frame (x aft from the hub axis)."""
    X, E, M = res['X'], res['E'], res['M']
    cases = [('F1', flight_combos(FA.T_CAP, FA.Q_CAP), FA.KP, FA.KF), ('F2', flight_combos(FA.T_UNC, FA.Q_UNC), FA.KP, FA.KF)]
    for k in ('S1', 'S2'):
        cases.append((k, [c for kk, c in ground_combos() if kk == k], 1.0, 1.0))
    fields = {}
    for name, combos, fp, fc in cases:
        fields[name] = element_fields(res, combos, fp, fc)
        print('fields %s: max utilisation %.2f' % (name, np.nanmax(fields[name][0])), flush=True)
    out = {'cases': np.array([c[0] for c in cases])}
    C4 = E[:, :4]
    for m in range(5):
        el = np.where(M == m)[0]
        if not len(el):
            continue
        f = np.concatenate([C4[el][:, [0, 1, 2]], C4[el][:, [0, 1, 3]], C4[el][:, [0, 2, 3]], C4[el][:, [1, 2, 3]]])
        opp = np.concatenate([C4[el][:, 3], C4[el][:, 2], C4[el][:, 1], C4[el][:, 0]])
        fe = np.tile(el, 4)
        key = np.sort(f, 1)
        _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
        b = cnt[inv.ravel()] == 1
        f, opp, fe = f[b], opp[b], fe[b]
        a, bb, cc = X[f[:, 0]], X[f[:, 1]], X[f[:, 2]]
        flip = np.einsum('ij,ij->i', np.cross(bb - a, cc - a), X[opp] - a) > 0
        f[flip] = f[flip][:, [0, 2, 1]]
        vid, tri = np.unique(f.ravel(), return_inverse=True)
        tri = tri.reshape(-1, 3)
        out['V%d' % m] = X[vid].astype(np.float32); out['T%d' % m] = tri.astype(np.int32)
        for name in fields:
            for j, lab in enumerate(('U', 'S')):
                v = np.full(len(vid), -np.inf)
                fv = fields[name][j][fe]
                np.maximum.at(v, tri.ravel(), np.repeat(np.nan_to_num(fv, nan=-np.inf), 3))
                v[~np.isfinite(v)] = np.nan
                out['%s_%s_%d' % (lab, name, m)] = v.astype(np.float32)
        print('skin material %d: %d vertices, %d triangles' % (m, len(vid), len(tri)), flush=True)
    np.savez_compressed(path, **out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--level', type=int, default=0)
    ap.add_argument('--tag', default='base')
    ap.add_argument('--p', nargs='*', default=[])
    ap.add_argument('--release', action='store_true', help='glue released between hub sleeves and arm tubes: pins and bearing only')
    ap.add_argument('--fields', action='store_true', help='also save per-material surface skins with utilisation / stress fields (figures, Explorer 3-D view)')
    a = ap.parse_args()
    RELEASE = a.release
    for kv in a.p:
        k, v = kv.split('='); GEO[k] = float(v)
    t0 = time.time()
    res = run(a.level, a.tag)
    print('mesh %d elements, %d free dof, hub block %.2f g, %.0f s' % (res['nel'], res['ndof'], res['hub_vol'] * 1.27e-3, time.time() - t0), flush=True)
    results = dict(geo=GEO, hub_g=res['hub_vol'] * 1.27e-3, equilibrium=res['eq'], elements=res['nel'], dof=res['ndof'])
    for name, combos in (('F1 spin cap, any thrust pattern', flight_combos(FA.T_CAP, FA.Q_CAP)),
                         ('F2 uncapped fault, any pattern', flight_combos(FA.T_UNC, FA.Q_UNC))):
        results[name] = evaluate(res, combos)
        print(name, json.dumps(results[name], indent=0)[:1400], flush=True)
    for case in ('S1', 'S2', 'S3'):
        cs = [c for k, c in ground_combos() if k == case]
        results[case + ' strike on UR (ground)'] = evaluate(res, cs)
        print(case, json.dumps(results[case + ' strike on UR (ground)'])[:600], flush=True)
    json.dump(results, open(os.path.join(OUT, 'hub_result_L%d_%s.json' % (a.level, a.tag)), 'w'), indent=1)
    if a.fields:
        save_fields(res, os.path.join(OUT, 'hub_fields_L%d_%s.npz' % (a.level, a.tag)))
