"""occ_bodies.py - T-077 p5: small OpenCASCADE (gmsh OCC) bodies drawn as one fusionkit 'mesh' shape, built the way hub_body.py builds the hub (the CAD kernel's prism / tube /
revolve cannot fillet or turn a tube about a skew axis). Cached in occ_bodies_cache.npz next to this file keyed by a SHA-1 of (name, params, VERSION); gmsh is imported only on a cache
miss (Blender's Python reads the committed cache). Bodies are OUTER bodies only: bores, slots and seats are cut by the caller (ctx.seat / cut_box) as for the hub.

    body_mesh(name, params) -> dict(verts (n,3) metres, tris (m,3) outward, vol_mm3)
    params['kind'] = 'strut_clamp': right-hand R4 clamp (x, y, z mm in the CAD frame): ring about the spar (axis y, centre (SPAR_X, z 0), y0..y1, outer radius RR) and a socket cylinder of radius RS
        along the strut axis (unit vector (ux, uy, 0) through the strut end E = (ex, ey, 0)) from s = -SL to s = +SE (inside the ring wall), junction edges filleted at FIL."""
import hashlib
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'occ_bodies_cache.npz')
VERSION = 'occ_bodies v1 (strut_clamp, T-077 p5)'


def _key(name, p):
    return hashlib.sha1((name + json.dumps(p, sort_keys=True, default=float) + VERSION).encode()).hexdigest()[:16]


def _build_strut_clamp(p):
    import gmsh
    gmsh.initialize(['-noenv'])
    try:
        gmsh.option.setNumber('General.Terminal', 0)
        gmsh.option.setNumber('General.NumThreads', 1)
        occ = gmsh.model.occ
        ring = occ.addCylinder(p['sx'], p['y0'], 0.0, 0.0, p['y1'] - p['y0'], 0.0, p['RR'])
        u = np.array([p['ux'], p['uy'], 0.0])
        a = np.array([p['ex'], p['ey'], 0.0]) - p['SL'] * u
        L = p['SL'] + p['SE']
        sock = occ.addCylinder(a[0], a[1], 0.0, L * u[0], L * u[1], 0.0, p['RS'])
        v, _ = occ.fuse([(3, ring)], [(3, sock)])
        occ.synchronize()
        vol_sharp = sum(occ.getMass(3, t) for _, t in v)
        # junction edges = edges shared by a socket-cylinder face and a ring face: take every edge whose points lie on both surfaces
        sel = []
        for d_, e in gmsh.model.getBoundary(gmsh.model.getBoundary(v, combined=False, oriented=False), combined=False, oriented=False):
            if d_ != 1 or e in sel:
                continue
            lo, hi = gmsh.model.getParametrizationBounds(1, e)
            pts = [gmsh.model.getValue(1, e, [lo[0] + (hi[0] - lo[0]) * f]) for f in (0.15, 0.5, 0.85)]
            ok = True
            for q in pts:
                q = np.array(q)
                ds = q - np.array([p['ex'], p['ey'], 0.0])
                rs = np.linalg.norm(ds - (ds @ u) * u)
                on_sock = abs(rs - p['RS']) < 0.02 and -p['SL'] - 0.05 <= ds @ u <= p['SE'] + 0.05
                rr = math.hypot(q[0] - p['sx'], q[2])
                on_ring = (abs(rr - p['RR']) < 0.02) or (abs(q[1] - p['y0']) < 0.02 and rr <= p['RR'] + 0.02) or (abs(q[1] - p['y1']) < 0.02 and rr <= p['RR'] + 0.02)
                ok &= on_sock and on_ring
            if ok:
                sel.append(e)
        occ.synchronize()
        if p['FIL'] > 0 and sel:
            out = occ.fillet([v[0][1]], sel, [p['FIL']], removeVolume=True)
            v = out
            occ.synchronize()
        vol = sum(occ.getMass(3, t) for _, t in v)
        faces = gmsh.model.getBoundary(v, combined=False, oriented=True)
        f = gmsh.model.mesh.field
        bl = sorted({abs(s) for _, s in faces if gmsh.model.getType(2, abs(s)) not in ('Plane', 'Cylinder', 'Cone')})
        if bl:
            dd = f.add('Distance'); f.setNumbers(dd, 'SurfacesList', bl)
            th = f.add('Threshold')
            for k, val in (('InField', dd), ('SizeMin', 0.3), ('SizeMax', 1.2), ('DistMin', 0.3), ('DistMax', 2.0)):
                f.setNumber(th, k, val)
            f.setAsBackgroundMesh(th)
        for k, val in (('Mesh.MeshSizeExtendFromBoundary', 0), ('Mesh.MeshSizeFromPoints', 0), ('Mesh.MeshSizeFromCurvature', 0), ('Mesh.ElementOrder', 1), ('Mesh.MeshSizeMax', 1.2)):
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
                for a_, b_, c_ in np.array(en, dtype=np.int64).reshape(-1, 3):
                    T.append((a_, b_, c_) if s > 0 else (a_, c_, b_))
        used = sorted({int(q) for t in T for q in t})
        remap = {q: i for i, q in enumerate(used)}
        V = np.array([pos[q] for q in used], dtype=float)
        Tr = np.array([[remap[int(q)] for q in t] for t in T], dtype=np.int64)
    finally:
        gmsh.finalize()
    return V, Tr, vol, vol_sharp, len(sel)


def body_mesh(name, p, rebuild=False):
    from . import hub_body as hb
    k = _key(name, p)
    store = {}
    if os.path.exists(CACHE):
        try:
            z = np.load(CACHE, allow_pickle=False)
            store = {n: z[n] for n in z.files}
        except Exception:
            store = {}
    if not rebuild and (k + '_v') in store:
        return dict(verts=store[k + '_v'], tris=store[k + '_t'], vol_mm3=float(store[k + '_vol']))
    if p['kind'] != 'strut_clamp':
        raise ValueError(p['kind'])
    V, T, vol, vs, nsel = _build_strut_clamp(p)
    V = V / 1000.0
    T = hb.orient_consistently(T)
    closed, outward, sv = hb.check_mesh(V, T)
    if not closed:
        raise RuntimeError('occ_bodies %s: surface mesh not closed / consistently wound' % name)
    if not outward:
        T = T[:, ::-1].copy()
    store[k + '_v'], store[k + '_t'], store[k + '_vol'] = V, T, np.array(vol)
    np.savez_compressed(CACHE, **store)
    print('occ_bodies %s: %d junction edges filleted, vol %.1f mm3 (sharp %.1f)' % (name, nsel, vol, vs), flush=True)
    return dict(verts=V, tris=T, vol_mm3=float(vol))
