"""hub_body.py - the outer body of the printed hub (CGE-001) as a watertight triangle mesh, built with gmsh / OpenCASCADE exactly as
qp/A/structures/fea_hub.py staged_fillet builds the FEA geometry: the centre block with its R_CB x-parallel edge radii, a sleeve of outer
radius R_SLV over s = +-L_SLV about each tube axis, sleeve B fused and its block junction filleted at FIL, then sleeve A fused and
filleted at FIL_A. NO bores, pin holes, doublers, pins or bridge (the CAD cuts those itself). The CAD kernel (fusionkit prism / revolve /
loft) cannot fillet, so wing.py draws this body as one fusionkit 'mesh' shape (D-207: the CAD must look like the printed part).

    hub_outer_mesh(params) -> dict(verts (n,3) metres in the CAD frame, tris (m,3) outward-wound, vol_fillet_mm3, vol_sharp_mm3)

params (mm, deg; hub frame x aft from the hub axis, y right, z up): XA, XB (tube axis x), PHI_A, PHI_B (tube direction from +y in the y-z plane),
L_SLV, R_SLV, CB, R_CB, BLK_Z, BLK_X0, BLK_X1 (block x range), BOSS (None or (x0, x1, z, r) cylinder fused without a fillet), FIL, FIL_A,
HUB_X (m, hub axis x in the CAD frame). Optional: MS_FIL (surface element size on the fillet faces, default 0.4 mm), MS (elsewhere, 1.5 mm).

The result is cached in hub_body_cache.npz next to this file, keyed by a SHA-1 of the params and VERSION (bump VERSION when the geometry code changes);
gmsh is imported only when the cache misses (so Blender's Python, which has no gmsh, reads the committed cache). Run this file to refresh
and print the stats. Light: a few seconds, one thread, no solve."""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'hub_body_cache.npz')
VERSION = 'hub_body v4 (octagonal sleeves, collar, T-077 p3; RC lightening cut, T-077 p4)'


def _params_key(p):
    return hashlib.sha1((json.dumps(p, sort_keys=True, default=float) + VERSION).encode()).hexdigest()


def _build(p):
    import gmsh
    gmsh.initialize(['-noenv'])
    try:
        gmsh.option.setNumber('General.Terminal', 0)
        gmsh.option.setNumber('General.NumThreads', 1)
        occ = gmsh.model.occ
        ph = {'A': math.radians(p['PHI_A']), 'B': math.radians(p['PHI_B'])}
        U = {t: np.array([0.0, math.cos(ph[t]), math.sin(ph[t])]) for t in 'AB'}
        X0 = {'A': p['XA'], 'B': p['XB']}
        rs, L, cb, bz, rc = p['R_SLV'], p['L_SLV'], p['CB'], p['BLK_Z'], p['R_CB']
        xa0, xb1 = p['BLK_X0'], p['BLK_X1']

        def sleeve(t):
            u, x0 = U[t], X0[t]
            if not p.get('OCT'):
                return (3, occ.addCylinder(x0 - L * u[0], -L * u[1], -L * u[2], 2 * L * u[0], 2 * L * u[1], 2 * L * u[2], rs))
            # D-221 s7.1.1: octagonal (prismatic) sleeve, apothem rs (= across flats / 2) = regular octagon as the intersection of a square and the same
            # square turned 45 deg about the tube axis; flats face +-x and +-t. Built along +y, then turned about x by PHI and moved to the tube axis.
            b1 = occ.addBox(-rs, -L, -rs, 2 * rs, 2 * L, 2 * rs)
            b2 = occ.addBox(-rs, -L, -rs, 2 * rs, 2 * L, 2 * rs)
            occ.rotate([(3, b2)], 0, 0, 0, 0, 1, 0, math.pi / 4)
            o, _ = occ.intersect([(3, b1)], [(3, b2)])
            occ.rotate(o, 0, 0, 0, 1, 0, 0, ph[t])
            occ.translate(o, x0, 0, 0)
            return o[0]

        def block():
            bx = occ.addBox(xa0, -cb, -cb + bz, xb1 - xa0, 2 * cb, 2 * cb)
            if rc > 0:                                  # the four x-parallel edges (as fea_hub.build_mesh)
                occ.synchronize()
                bnd = [c[1] for c in gmsh.model.getBoundary(gmsh.model.getBoundary([(3, bx)], combined=False, oriented=False),
                                                              combined=False, oriented=False) if c[0] == 1]
                ed = [e for d_, e in occ.getEntities(1) if d_ == 1 and e in bnd
                      and (lambda b: abs(b[3] - b[0]) > 1 and abs(b[4] - b[1]) < 0.1 and abs(b[5] - b[2]) < 0.1)(occ.getBoundingBox(1, e))]
                bx = occ.fillet([bx], ed, [rc])[0][1]
            return (3, bx)

        def boss():
            if not p.get('BOSS'):
                return []
            b0, b1, bzz, br = p['BOSS']
            return [(3, occ.addCylinder(b0, 0, bzz, b1 - b0, 0, 0, br))]

        def collar():                               # D-220 collar: box (x0, x1, y half, z0, z1), its four x-parallel edges rounded R_CB, fused to the block's aft face (no junction fillet)
            if not p.get('COLLAR'):
                return []
            c0, c1, chy, cz0, cz1 = p['COLLAR']
            cb_ = occ.addBox(c0, -chy, cz0, c1 - c0, 2 * chy, cz1 - cz0)
            if rc > 0:
                occ.synchronize()
                bnd = [c[1] for c in gmsh.model.getBoundary(gmsh.model.getBoundary([(3, cb_)], combined=False, oriented=False), combined=False, oriented=False) if c[0] == 1]
                ed = [e for d_, e in occ.getEntities(1) if d_ == 1 and e in bnd and (lambda b: abs(b[3] - b[0]) > 1 and abs(b[4] - b[1]) < 0.1 and abs(b[5] - b[2]) < 0.1)(occ.getBoundingBox(1, e))]
                cb_ = occ.fillet([cb_], ed, [rc])[0][1]
            return [(3, cb_)]

        def rc_cut(v):                                  # T-077 p4 (D-224 hub pockets): turn the block aft of RC x0 and the collar to a cylinder of radius RC r about the bridge axis (everything outside it is removed)
            if not p.get('RC'):
                return v
            rcr, rcx0, rcz = p['RC']
            xe_ = p['COLLAR'][1] + 3.0 if p.get('COLLAR') else rcx0 + 40.0
            bx_ = occ.addBox(rcx0, -40.0, rcz - 40.0, xe_ - rcx0, 80.0, 80.0)
            cy_ = occ.addCylinder(rcx0 - 1.0, 0, rcz, xe_ - rcx0 + 2.0, 0, 0, rcr)
            cut_, _ = occ.cut([(3, bx_)], [(3, cy_)])
            out_, _ = occ.cut(v, cut_, removeTool=True)
            occ.synchronize()
            return out_

        # --- sharp reference body (same pieces, plain fuse) -> volume
        parts = [sleeve('A'), sleeve('B'), block()] + boss() + collar()
        v, _ = occ.fuse([parts[0]], parts[1:])
        occ.synchronize()
        v = rc_cut(v)
        vol_sharp = sum(occ.getMass(3, t) for _, t in v)
        occ.remove(v, recursive=True)
        occ.synchronize()

        # --- staged fillet (fea_hub.staged_fillet)
        def on_sleeve(q, t):
            u = U[t]
            d = np.array(q) - np.array([X0[t], 0.0, 0.0])
            if p.get('OCT'):
                tt = np.cross([1.0, 0.0, 0.0], u)          # tangential direction t = x_hat cross u
                a, b = d[0], d @ tt
                return abs(max(abs(a), abs(b), (abs(a) + abs(b)) / math.sqrt(2.0)) - rs) < 0.02
            return abs(np.linalg.norm(d - (d @ u) * u) - rs) < 0.02

        def in_block(q):
            return xa0 - 0.05 <= q[0] <= xb1 + 0.05 and abs(q[1]) <= cb + 0.05 and abs(q[2] - bz) <= cb + 0.05

        sA, sB, bk = sleeve('A'), sleeve('B'), block()
        extra = boss()
        vol = bk[1]
        for t, part, r in (('B', sB, p['FIL']), ('A', sA, p['FIL_A'])):
            v, _ = occ.fuse([(3, vol)], [part])
            occ.synchronize()
            vol = v[0][1]
            sel = []
            for d_, e in gmsh.model.getBoundary(gmsh.model.getBoundary([(3, vol)], combined=False, oriented=False), combined=False, oriented=False):
                if d_ != 1 or e in sel:
                    continue
                lo, hi = gmsh.model.getParametrizationBounds(1, e)
                pts = [gmsh.model.getValue(1, e, [lo[0] + (hi[0] - lo[0]) * f]) for f in (0.2, 0.5, 0.8)]
                if all(on_sleeve(q, t) and in_block(q) for q in pts):
                    if p.get('OCT') and t == 'A' and all(on_sleeve(q, 'B') for q in pts):
                        continue                                   # A / B crease (not a block junction): OCC cannot fillet it with the octagons
                    sel.append(e)
            out = occ.fillet([vol], sel, [r], removeVolume=False)
            occ.remove([(3, vol)], recursive=True)
            vol = out[0][1]
            print('hub_body: sleeve %s, %d junction edges at r %.1f mm' % (t, len(sel), r), flush=True)
        if extra:
            v, _ = occ.fuse([(3, vol)], extra)
            vol = v[0][1]
        for cq in collar():
            v, _ = occ.fuse([(3, vol)], [cq])
            vol = v[0][1]
        occ.synchronize()
        vol = rc_cut([(3, vol)])[0][1]
        vol_fil = occ.getMass(3, vol)

        # --- surface mesh: fine on the blend faces (not plane / cylinder / cone), coarse elsewhere
        ms, msf = p.get('MS', 1.5), p.get('MS_FIL', 0.4)
        faces = [(d, s) for d, s in gmsh.model.getBoundary([(3, vol)], combined=False, oriented=True)]
        f = gmsh.model.mesh.field
        bl = sorted({abs(s) for _, s in faces if gmsh.model.getType(2, abs(s)) not in ('Plane', 'Cylinder', 'Cone')})
        dd = f.add('Distance')
        f.setNumbers(dd, 'SurfacesList', bl)
        th = f.add('Threshold')
        for k, val in (('InField', dd), ('SizeMin', msf), ('SizeMax', ms), ('DistMin', 0.3), ('DistMax', 2.0)):
            f.setNumber(th, k, val)
        f.setAsBackgroundMesh(th)
        for k, val in (('Mesh.MeshSizeExtendFromBoundary', 0), ('Mesh.MeshSizeFromPoints', 0), ('Mesh.MeshSizeFromCurvature', 0), ('Mesh.ElementOrder', 1)):
            gmsh.option.setNumber(k, val)
        gmsh.model.mesh.generate(2)
        tags, xyz, _ = gmsh.model.mesh.getNodes()
        pos = {int(t): xyz[3 * i:3 * i + 3] for i, t in enumerate(tags)}
        T = []
        for _, s in faces:
            sf = abs(s)
            for et, _, en in zip(*gmsh.model.mesh.getElements(2, sf)):
                if et != 2:
                    continue
                for a, b, c in np.array(en, dtype=np.int64).reshape(-1, 3):
                    T.append((a, b, c) if s > 0 else (a, c, b))
        used = sorted({int(q) for t in T for q in t})
        remap = {q: i for i, q in enumerate(used)}
        V = np.array([pos[q] for q in used], dtype=float)
        Tr = np.array([[remap[int(q)] for q in t] for t in T], dtype=np.int64)
    finally:
        gmsh.finalize()
    return V, Tr, vol_fil, vol_sharp


def orient_consistently(T):
    """Flip triangles (BFS over shared edges) until every shared edge is traversed once in each direction; the caller then fixes the global sign."""
    T = [list(t) for t in T]
    adj = {}
    for i, t in enumerate(T):
        for u, w in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            adj.setdefault(frozenset((u, w)), []).append(i)
    seen = [False] * len(T)
    for s0 in range(len(T)):
        if seen[s0]:
            continue
        seen[s0] = True
        stack = [s0]
        while stack:
            i = stack.pop()
            t = T[i]
            for u, w in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                for j in adj[frozenset((u, w))]:
                    if seen[j]:
                        continue
                    n = T[j]
                    if (u, w) in ((n[0], n[1]), (n[1], n[2]), (n[2], n[0])):      # same direction: neighbour must flip
                        n[1], n[2] = n[2], n[1]
                    seen[j] = True
                    stack.append(j)
    return np.array(T, dtype=np.int64)


def check_mesh(V, T):
    """(closed, outward, signed volume): every edge shared by exactly two triangles, one in each direction (consistent winding), signed volume > 0."""
    e = {}
    for a, b, c in T:
        for u, w in ((a, b), (b, c), (c, a)):
            e[(u, w)] = e.get((u, w), 0) + 1
    closed = all(n == 1 and (w, u) in e for (u, w), n in e.items())
    P = V[T]
    vol = float(np.einsum('ij,ij->', P[:, 0], np.cross(P[:, 1], P[:, 2])) / 6.0)
    return closed, vol > 0, vol


def hub_outer_mesh(p, rebuild=False):
    """Cached outer hub body. verts in metres in the CAD frame (x = HUB_X + x_mm / 1000)."""
    k = _params_key(p)
    if not rebuild and os.path.exists(CACHE):
        try:
            z = np.load(CACHE, allow_pickle=False)
            if str(z['key']) == k:
                return dict(verts=z['verts'], tris=z['tris'], vol_fillet_mm3=float(z['vol_fillet']), vol_sharp_mm3=float(z['vol_sharp']))
        except Exception:
            pass
    V, T, vf, vs = _build(p)
    V = V / 1000.0
    V[:, 0] += p['HUB_X']
    T = orient_consistently(T)
    closed, outward, sv = check_mesh(V, T)
    if not closed:
        raise RuntimeError('hub_body: surface mesh is not closed / consistently wound')
    if not outward:
        T = T[:, ::-1].copy()
    np.savez_compressed(CACHE, key=k, verts=V, tris=T, vol_fillet=vf, vol_sharp=vs)
    return dict(verts=V, tris=T, vol_fillet_mm3=vf, vol_sharp_mm3=vs)


def cad_params():
    """The CAD constants (wing.py / common.py) as hub_outer_mesh params, mm."""
    from . import wing as W
    from . import common as C
    mm = 1e3
    return dict(XA=-C.TUBE_DX * mm, XB=C.TUBE_DX * mm, PHI_A=C.TUBE_PHI['A'], PHI_B=C.TUBE_PHI['B'],
                L_SLV=W.SLV_L * mm, R_SLV=W.SLV_R * mm, CB=W.CB * mm, R_CB=W.R_CB * mm, BLK_Z=W.BLK_Z * mm,
                BLK_X0=W.BLK_X[0] * mm, BLK_X1=W.BLK_X[1] * mm,
                BOSS=None if (W.HUB_X1 - C.HUB[0] - W.BLK_X[1]) <= 0.001 else ((W.BLK_X[1] - 0.0005) * mm, (W.HUB_X1 - C.HUB[0]) * mm, W.BR_Z * mm, W.R_BR * mm),
                FIL=W.HUB_FIL, FIL_A=W.HUB_FIL_A, MS=1.5, MS_FIL=0.4, HUB_X=C.HUB[0], OCT=True, COLLAR=(W.BLK_X[1] * mm - 0.0005 * 0, W.COL_X1 * mm, W.COL_HY * mm, W.COL_Z[0] * mm, W.COL_Z[1] * mm),
                RC=(W.POCKET_R * mm, W.POCKET_X0 * mm, W.BR_Z * mm) if W.POCKET_R > 0 else None)


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(HERE))
    import importlib
    pk = importlib.import_module('amodel.hub_body')
    r = pk.hub_outer_mesh(pk.cad_params(), rebuild='--rebuild' in sys.argv)
    c, o, sv = check_mesh(r['verts'], r['tris'])
    print('verts %d tris %d closed %s outward %s signed vol %.1f mm3 (OCC filleted %.1f, sharp %.1f, fillet material %.2f mm3)' % (
        len(r['verts']), len(r['tris']), c, o, sv * 1e9, r['vol_fillet_mm3'], r['vol_sharp_mm3'], r['vol_fillet_mm3'] - r['vol_sharp_mm3']))
