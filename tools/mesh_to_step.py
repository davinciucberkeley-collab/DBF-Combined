"""Triangle mesh -> ISO-10303-21 AP214 STEP (faceted B-rep), pure Python, mm.

Usage: python -I tools/mesh_to_step.py mesh.json out.step "product name" [--no-merge]
mesh.json: {"v": [[x,y,z],...] (mm), "f": [[i,j,k],...]}.

Coplanar adjacent triangles (normal within 0.5 deg of the seed triangle, every vertex within 0.001 mm of the seed
plane) are merged into one planar ADVANCED_FACE on a PLANE with an outer loop (FACE_OUTER_BOUND) and hole loops
(FACE_BOUND). Curved regions stay triangles. --no-merge writes one face per triangle (the first version).
Each connected component is its own body: closed -> FACETED_BREP over a CLOSED_SHELL, otherwise -> SHELL_BASED_SURFACE_MODEL
over an OPEN_SHELL. Triangles on non-manifold edges are never merged.
"""
import json, math, sys
from collections import Counter


def is_closed(F):
    c = Counter()
    for a, b, d in F:
        for u, v in ((a, b), (b, d), (d, a)):
            c[(u, v)] += 1
    return all(n == 1 and c.get((v, u), 0) == 1 for (u, v), n in c.items())


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def tri_normals(V, F):
    N = []
    for a, b, c in F:
        n = _cross(_sub(V[b], V[a]), _sub(V[c], V[a]))
        ln = _dot(n, n) ** 0.5
        N.append((n[0] / ln, n[1] / ln, n[2] / ln) if ln > 1e-12 else None)
    return N


def merge_planar(V, F, ang_deg=0.5, tol=0.001):
    """Returns [(normal, loops)] with loops[0] the outer loop (CCW about normal) and the rest hole loops (CW);
    loops are lists of mesh vertex indices (no new points)."""
    cosmin = math.cos(math.radians(ang_deg))
    N = tri_normals(V, F)
    edge_tri = {}
    dcount = Counter()
    for t, (a, b, c) in enumerate(F):
        for u, v in ((a, b), (b, c), (c, a)):
            edge_tri[(u, v)] = t
            dcount[(u, v)] += 1
    # triangles on a non-manifold edge (a directed edge used twice) are never merged
    nm = set()
    for t, (a, b, c) in enumerate(F):
        if any(dcount[(u, v)] > 1 for u, v in ((a, b), (b, c), (c, a))):
            nm.add(t)
            for u, v in ((a, b), (b, c), (c, a)):
                o = edge_tri.get((v, u))
                if o is not None:
                    nm.add(o)
    region = [-1] * len(F)
    regions = []
    for s in range(len(F)):
        if region[s] >= 0:
            continue
        rid = len(regions)
        region[s] = rid
        tris = [s]
        ns = N[s]
        if ns is not None and s not in nm:
            p0 = V[F[s][0]]
            stack = [s]
            while stack:
                t = stack.pop()
                a, b, c = F[t]
                for u, v in ((a, b), (b, c), (c, a)):
                    o = edge_tri.get((v, u))
                    if o is None or region[o] >= 0 or N[o] is None or o in nm:
                        continue
                    if _dot(N[o], ns) < cosmin:
                        continue
                    if any(abs(_dot(ns, _sub(V[i], p0))) > tol for i in F[o]):
                        continue
                    region[o] = rid
                    tris.append(o)
                    stack.append(o)
        regions.append((ns, tris))
    out = []
    for ns, tris in regions:
        tset = set(tris)
        outs = {}
        for t in tris:
            a, b, c = F[t]
            for u, v in ((a, b), (b, c), (c, a)):
                o = edge_tri.get((v, u))
                if o is None or o not in tset:
                    outs.setdefault(u, []).append(v)
        if ns is None:
            ns = (0.0, 0.0, 1.0)
        ref = (1.0, 0.0, 0.0) if abs(ns[0]) < 0.9 else (0.0, 1.0, 0.0)
        ex = _cross(ref, ns)
        el = _dot(ex, ex) ** 0.5
        ex = (ex[0] / el, ex[1] / el, ex[2] / el)
        ey = _cross(ns, ex)

        def p2(i):
            return (_dot(V[i], ex), _dot(V[i], ey))

        loops = []
        used = set()
        for u0 in sorted(outs):
            for v0 in outs[u0]:
                if (u0, v0) in used:
                    continue
                loop = [u0]
                u, v = u0, v0
                used.add((u, v))
                while v != u0:
                    loop.append(v)
                    pu, pv = p2(u), p2(v)
                    din = (pv[0] - pu[0], pv[1] - pu[1])
                    best, bt = None, -9.0
                    for w in outs.get(v, []):
                        if (v, w) in used:
                            continue
                        pw = p2(w)
                        dout = (pw[0] - pv[0], pw[1] - pv[1])
                        th = math.atan2(din[0] * dout[1] - din[1] * dout[0], din[0] * dout[0] + din[1] * dout[1])
                        if th > bt:
                            best, bt = w, th
                    if best is None:
                        break
                    used.add((v, best))
                    u, v = v, best
                loops.append(loop)

        def area(l):
            q = [p2(i) for i in l]
            return 0.5 * sum(q[k][0] * q[(k + 1) % len(q)][1] - q[(k + 1) % len(q)][0] * q[k][1] for k in range(len(q)))

        def inside(pt, l):
            q = [p2(i) for i in l]
            c = False
            for k in range(len(q)):
                (x1, y1), (x2, y2) = q[k], q[(k + 1) % len(q)]
                if (y1 > pt[1]) != (y2 > pt[1]) and pt[0] < (x2 - x1) * (pt[1] - y1) / (y2 - y1) + x1:
                    c = not c
            return c

        areas = [area(l) for l in loops]
        outers = sorted([(a, l) for a, l in zip(areas, loops) if a > 0], key=lambda x: x[0])
        holes = [l for a, l in zip(areas, loops) if a <= 0]
        groups = [[l] for _, l in outers]
        if not groups:  # zero-area sliver triangle: keep it as its own face so neighbours still pair up
            groups = [[l] for l in loops]
            holes = []
        for h in holes:
            host = None
            for g in groups:
                if any(i not in g[0] and inside(p2(i), g[0]) for i in h):
                    host = g
                    break
            if host is None and groups:
                host = groups[-1]
            if host is not None:
                host.append(h)
        for g in groups:
            out.append((ns, g))
    return out


def remove_slivers(V, F, area2_tol=1e-6):
    """Remove zero-area (collinear) triangles: the vertex B lying between A and C splits the neighbour across edge A-C
    into two triangles, so the mesh stays closed and conforming. Returns (F, number removed)."""
    F = [tuple(t) for t in F]
    removed = 0
    for _ in range(50):
        edge_tri = {}
        for t, (a, b, c) in enumerate(F):
            for u, v in ((a, b), (b, c), (c, a)):
                edge_tri.setdefault((u, v), []).append(t)
        kill, add_t = set(), []
        for t, (a, b, c) in enumerate(F):
            if t in kill:
                continue
            n = _cross(_sub(V[b], V[a]), _sub(V[c], V[a]))
            if _dot(n, n) ** 0.5 > area2_tol:
                continue
            # the middle vertex lies on the longest edge, i.e. it is opposite that edge
            pts = {a: (b, c), b: (c, a), c: (a, b)}
            far = max(pts, key=lambda i: _dot(_sub(V[pts[i][0]], V[pts[i][1]]), _sub(V[pts[i][0]], V[pts[i][1]])))
            m = far
            p, q = pts[m]  # triangle is (.., m, ..) cyclic: edge p->q is opposite m
            # directed edge opposite m in this triangle is (p, q); its twin (q, p) belongs to the neighbour to split
            tw = edge_tri.get((q, p), [])
            if len(tw) != 1 or tw[0] in kill or tw[0] == t:
                continue
            o = tw[0]
            x = [i for i in F[o] if i != p and i != q]
            if len(x) != 1:
                continue
            x = x[0]
            # neighbour has edge q->p; split it at m into (q,m,x) and (m,p,x) keeping orientation
            kill.add(t)
            kill.add(o)
            add_t.append((q, m, x))
            add_t.append((m, p, x))
            removed += 1
        if not kill:
            break
        F = [t for i, t in enumerate(F) if i not in kill] + add_t
    return [list(t) for t in F], removed


def components(V, F):
    """Edge/vertex-connected triangle groups (each becomes its own body)."""
    par = list(range(len(V)))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for a, b, c in F:
        par[f(a)] = f(b)
        par[f(b)] = f(c)
    g = {}
    for t in F:
        g.setdefault(f(t[0]), []).append(t)
    return list(g.values())


def solid_volume(V, F):
    return sum(_dot(V[a], _cross(V[b], V[c])) for a, b, c in F) / 6.0


def write_step(V, F, name, path, schema="AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }", merge=True):
    L = []
    n = [0]

    def add(s):
        n[0] += 1
        L.append(f"#{n[0]}={s};")
        return n[0]

    q = name.replace("'", "''")
    ac = add("APPLICATION_CONTEXT('automotive design')")
    add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2001,#{ac})")
    pc = add(f"PRODUCT_CONTEXT('',#{ac},'mechanical')")
    pr = add(f"PRODUCT('{q}','{q}','',(#{pc}))")
    pdf = add(f"PRODUCT_DEFINITION_FORMATION('','',#{pr})")
    pdc = add(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{ac},'design')")
    pd = add(f"PRODUCT_DEFINITION('design','',#{pdf},#{pdc})")
    pds = add(f"PRODUCT_DEFINITION_SHAPE('','',#{pd})")
    pts = [add(f"CARTESIAN_POINT('',({x:.6f},{y:.6f},{z:.6f}))") for x, y, z in V]
    F, nslivers = remove_slivers(V, F) if merge else (F, 0)
    bodies = []
    nfaces = 0
    nclosed = 0
    for Fc in components(V, F):
        cl = is_closed(Fc)
        nclosed += cl
        if merge:
            regs = merge_planar(V, Fc)
        else:
            regs = [(tri_normals(V, [t])[0] or (0.0, 0.0, 1.0), [list(t)]) for t in Fc]
        faces = []
        for nrm, loops in regs:
            i0, i1 = loops[0][0], loops[0][1]
            ux, uy, uz = _sub(V[i1], V[i0])
            ul = (ux * ux + uy * uy + uz * uz) ** 0.5 or 1.0
            bnds = []
            for k, lp in enumerate(loops):
                pl = add("POLY_LOOP('',(" + ",".join("#%d" % pts[i] for i in lp) + "))")
                bnds.append(add(f"FACE_OUTER_BOUND('',#{pl},.T.)" if k == 0 else f"FACE_BOUND('',#{pl},.T.)"))
            dn = add(f"DIRECTION('',({nrm[0]:.9f},{nrm[1]:.9f},{nrm[2]:.9f}))")
            dr = add(f"DIRECTION('',({ux/ul:.9f},{uy/ul:.9f},{uz/ul:.9f}))")
            pa = add(f"AXIS2_PLACEMENT_3D('',#{pts[i0]},#{dn},#{dr})")
            pln = add(f"PLANE('',#{pa})")
            faces.append(add("ADVANCED_FACE('',(" + ",".join("#%d" % b for b in bnds) + f"),#{pln},.T.)"))
        nfaces += len(faces)
        fl = ",".join(f"#{i}" for i in faces)
        if cl:
            sh = add(f"CLOSED_SHELL('',({fl}))")
            bodies.append(add(f"FACETED_BREP('{q}',#{sh})"))
        else:
            sh = add(f"OPEN_SHELL('',({fl}))")
            bodies.append(add(f"SHELL_BASED_SURFACE_MODEL('{q}',(#{sh}))"))
    closed = nclosed == len(bodies)
    rtype = "ADVANCED_BREP_SHAPE_REPRESENTATION" if closed else "MANIFOLD_SURFACE_SHAPE_REPRESENTATION"
    ax = add("CARTESIAN_POINT('',(0.,0.,0.))")
    d1 = add("DIRECTION('',(0.,0.,1.))")
    d2 = add("DIRECTION('',(1.,0.,0.))")
    a2 = add(f"AXIS2_PLACEMENT_3D('',#{ax},#{d1},#{d2})")
    u1 = add("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
    u2 = add("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
    u3 = add("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
    un = add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-05),#{u1},'distance_accuracy_value','')")
    gc = add(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{un}))GLOBAL_UNIT_ASSIGNED_CONTEXT((#{u1},#{u2},#{u3}))REPRESENTATION_CONTEXT('',''))")
    rep = add(f"{rtype}('',(#{a2}," + ",".join('#%d' % b for b in bodies) + f"),#{gc})")
    add(f"SHAPE_DEFINITION_REPRESENTATION(#{pds},#{rep})")
    hdr = ("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('" + q + "'),'2;1');\n"
           "FILE_NAME('" + q + ".step','2026-11-23',('Claude'),(''),'mesh_to_step.py','mesh_to_step.py','');\n"
           f"FILE_SCHEMA(('{schema}'));\nENDSEC;\nDATA;\n")
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(hdr + "\n".join(L) + "\nENDSEC;\nEND-ISO-10303-21;\n")
    return {"closed": closed, "vertices": len(V), "triangles": len(F), "faces": nfaces, "bodies": len(bodies), "slivers_removed": nslivers, "closed_bodies": nclosed, "entities": n[0]}


if __name__ == "__main__":
    m = json.load(open(sys.argv[1]))
    print(write_step(m["v"], m["f"], sys.argv[3], sys.argv[2], merge="--no-merge" not in sys.argv))
