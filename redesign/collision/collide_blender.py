"""collide_blender.py - runs INSIDE Blender (bpy) for collide.py; not meant to be run by hand:

    blender -b --factory-startup --python-exit-code 1 -P collide_blender.py -- <_job.json> <report.json>

Every CAD body is meshed by manufacturing/blender_mesh.py's body_object (the same builders as the GLB and the shop
STLs), placed in world millimetres. Candidate pairs (bodies of different parts whose boxes overlap) get a BVH triangle
overlap test; where surfaces cross, 15 points per crossing triangle are tested for depth inside the other solid
(nearest-surface sign confirmed by ray parity). A pair whose surfaces do not cross is tested for one body lying wholly
inside the other. Cuts (fusionkit Component.cut / Context.seat) are honoured without booleans: points inside a part's
own cutters are removed material. No mesh boolean is needed, so no boolean failure can hide an overlap.
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(HERE)
for _p in (os.path.join(REDESIGN, 'manufacturing'), os.path.join(REDESIGN, 'blender'), os.path.join(REDESIGN, 'fusion')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bmesh                                  # noqa: E402
import bpy                                    # noqa: E402
from mathutils import Matrix, Vector          # noqa: E402
from mathutils.bvhtree import BVHTree         # noqa: E402

import blender_mesh as bm_                     # noqa: E402

EPS_BOX = 1e-4                                 # mm: boxes must overlap by more than this to be a candidate
MAX_EDGE_MM = 4.0                              # longest triangle edge after refinement (float32 nearest queries)
CUT_TOL_MM = 0.02                             # a point this close to a cutter's surface counts as removed


class Body:
    def __init__(self, pid, idx, name, ob):
        self.pid, self.idx, self.name, self.ob = pid, idx, name, ob
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.transform(ob.matrix_world)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        # float32 BVH / mathutils cannot resolve the nearest point on sliver triangles (a 505 mm x 3 mm skin side
        # face read 0.1 mm away from a point lying on it): split long edges so every triangle is well shaped
        for _ in range(12):
            long_e = [e for e in bm.edges if e.calc_length() > MAX_EDGE_MM]
            if not long_e:
                break
            bmesh.ops.subdivide_edges(bm, edges=long_e, cuts=1, use_grid_fill=False)
            bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.normal_update()
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        self.bvh = BVHTree.FromBMesh(bm)
        self.tris = [tuple(v.co.copy() for v in f.verts) for f in bm.faces]   # same index order as the BVH
        co = [v.co for v in bm.verts]
        self.lo = [min(c[i] for c in co) for i in range(3)]
        self.hi = [max(c[i] for c in co) for i in range(3)]
        self.probe = bm.verts[0].co.copy() if len(bm.verts) else None
        self.vol = abs(bm.calc_volume(signed=True))
        bm.free()


def boxes_overlap(a, b):
    return all(a.lo[i] < b.hi[i] - EPS_BOX and b.lo[i] < a.hi[i] - EPS_BOX for i in range(3))


def inside(point, body):
    """Point inside a closed body: the nearest surface normal points away from the point."""
    loc, nrm, _i, _d = body.bvh.find_nearest(point)
    return loc is not None and (point - loc).dot(nrm) < -1e-6


def depth_inside(point, body):
    """Penetration depth (mm) of a point inside a closed body, 0 when outside. The nearest-normal sign is confirmed
    by ray parity along +x (robust at concave edges)."""
    loc, nrm, _i, d = body.bvh.find_nearest(point)
    if loc is None or (point - loc).dot(nrm) >= -1e-9:
        return 0.0
    n, p, ray = 0, point.copy(), Vector((1.0, 0.0, 0.0))
    for _ in range(64):
        hit = body.bvh.ray_cast(p, ray)
        if hit[0] is None:
            break
        n += 1
        p = hit[0] + ray * 1e-3                       # mm; float32 BVH: 1e-6 re-hits the same face
    return d if n % 2 == 1 else 0.0


GRID = [(i / 4.0, j / 4.0) for i in range(5) for j in range(5 - i)]     # 15 barycentric samples per triangle


def tri_samples(t):
    a, b, c = t
    return [a + (b - a) * u + (c - a) * v for u, v in GRID]


def removed(p, body):
    """p lies in material the body's part has had cut away (a seat, hole or pocket), or within CUT_TOL_MM of a
    cutter's surface (a seat is an exact fit: the guest's own surface lies on it)."""
    for c in body.cutters:
        if not all(c.lo[i] - CUT_TOL_MM <= p[i] <= c.hi[i] + CUT_TOL_MM for i in range(3)):
            continue
        loc, _n, _i, d = c.bvh.find_nearest(p)
        if loc is not None and (d <= CUT_TOL_MM or depth_inside(p, c) > 0):
            return True
    return False


def penetration(a, b, pairs):
    """Deepest point of either surface inside the other solid, over the triangles whose surfaces cross. Cuts are
    honoured without booleans: a surface point inside its own part's cutters no longer exists, and a point inside the
    other part's cutters is in removed material."""
    deep, at = 0.0, None
    for src, dst, ids in ((a, b, {i for i, _j in pairs}), (b, a, {j for _i, j in pairs})):
        for i in ids:
            for p in tri_samples(src.tris[i]):
                d = depth_inside(p, dst)
                if d > deep and not removed(p, src) and not removed(p, dst) and not at_terminal(p, a, b):
                    deep, at = d, p
    return deep, at


MEMBRANE = ()                                  # D-86: none. The tape skin is a solid like any other: a lead passes it
#                                                only through a slit drawn in WNG-003 (F2 cad.skin_slots), which the
#                                                cut handling treats as removed material (was ('WNG-003',), D-85)
JOINT_MM = 0.0                                 # D-86: no shared bench joint; every conductor lands on its own pad
END_SEAT_MM = 0.5                              # D-86: each strand end (its surface: axis within radius + this) must lie
#                                                in or on one of its own terminal parts or an in-line connector on it
WIRE_END_MM = 6.0                              # a wire may sit in its terminal part this close to its end: the solder
#                                                pad or cup plus its adhesive heat-shrink tail (ESC leads leave the
#                                                heat-shrunk ESC body from inside it)


def make_wires(wires, col):
    """Every routed wire strand as the GLB draws it (blender_backend.wire: filleted polyline at the declared bend
    radius, round section at the strand diameter), as Bodies whose part id is the wire's edge id."""
    import blender_backend as bbk
    out = []
    for w in wires:
        ends = []
        for k, (line, dia) in enumerate(w['strands']):
            pts = bbk.fillet_polyline([tuple(p) for p in line], w['bend'])
            cu = bpy.data.curves.new('%s s%d' % (w['id'], k), 'CURVE')
            cu.dimensions, cu.bevel_depth, cu.bevel_resolution, cu.use_fill_caps = '3D', 1.0, 3, True
            sp = cu.splines.new('POLY')
            sp.points.add(len(pts) - 1)
            for p, q in zip(sp.points, pts):
                p.co = (q.x, q.y, q.z, 1.0)
                p.radius = dia / 2
            tmp = bpy.data.objects.new(cu.name, cu)
            bpy.context.scene.collection.objects.link(tmp)
            dg = bpy.context.evaluated_depsgraph_get()
            me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
            bpy.data.objects.remove(tmp)
            bpy.data.curves.remove(cu)
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
            bm.transform(Matrix.Scale(1000.0, 4))
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(me)
            bm.free()
            ob = bpy.data.objects.new(me.name, me)
            col.objects.link(ob)
            b = Body(w['id'], k, 'wire strand %d (%.1f mm)' % (k, dia * 1000), ob)
            b.cutters, b.wire = [], True
            b.r = dia * 500.0                         # strand radius, mm
            b.ends = [Vector(line[0]) * 1000.0, Vector(line[-1]) * 1000.0]
            b.terms = {t for t in w['ends'] if t}
            b.inline = set(w.get('inline', []))
            out.append(b)
    return out


def audit_wires(wires_job, wire_bodies, solids, others_wires):
    """Per wire strand: walk the drawn centreline (filleted, as the GLB) in 1 mm steps, test 8 points round the
    circumference against every solid and every other wire, and report each clash as a range of the ROUTE's waypoint
    segments (team/F2 wire_table indices) with the part, the deepest point and its depth. Terminal joints exempt."""
    import blender_backend as bbk
    out = {}
    allb = solids + others_wires
    for w in wires_job:
        for k, (line, dia) in enumerate(w['strands']):
            body = next(b for b in wire_bodies if b.pid == w['id'] and b.idx == k)
            P = [Vector(p) * 1000.0 for p in line]
            F = [Vector(q) * 1000.0 for q in bbk.fillet_polyline([tuple(p) for p in line], w['bend'])]
            r = dia * 1000.0 / 2
            cand = [b for b in allb if b.pid != w['id'] and boxes_overlap(body, b)]
            hits = []
            for i in range(len(F) - 1):
                a_, b_ = F[i], F[i + 1]
                L = (b_ - a_).length
                if L < 1e-6:
                    continue
                t = (b_ - a_) / L
                u = t.orthogonal().normalized()
                v = t.cross(u)
                n = max(1, int(L))
                for j in range(n + 1):
                    c = a_ + t * (L * j / n)
                    for q in range(8):
                        ang = q * math.pi / 4
                        p = c + (u * math.cos(ang) + v * math.sin(ang)) * r
                        for o in cand:
                            if not all(o.lo[m] <= p[m] <= o.hi[m] for m in range(3)):
                                continue
                            d = depth_inside(p, o)
                            if d > 0.05 and not removed(p, o) and o.pid not in w.get('inline', []) and                                     ('%s:%s' % (o.pid, o.name)) not in w.get('inline', []) and                                     o.pid not in MEMBRANE and not (getattr(o, 'wire', False) and set(w['ends']) & o.terms
                                        and min((c - e).length for e in [P[0], P[-1]] + o.ends) <= JOINT_MM) and not (
                                    o.pid in w['ends'] and min((c - P[0]).length, (c - P[-1]).length) <= WIRE_END_MM):
                                seg = min(range(len(P) - 1), key=lambda s_: _seg_d(c, P[s_], P[s_ + 1]))
                                hits.append((seg, o.pid, o.name, d, [round(x, 1) for x in c]))
            # merge consecutive hits per (segment, part)
            agg = {}
            for seg, pid, nm, d, c in hits:
                key = (seg, pid)
                if key not in agg or d > agg[key][2]:
                    agg[key] = (nm, c, round(d, 2))
            out.setdefault(w['id'], []).extend([{'strand': k, 'seg': key[0], 'part': key[1], 'body': v[0], 'at': v[1],
                                                 'depth': v[2]} for key, v in sorted(agg.items())])
    return out


def _seg_d(p, a, b):
    ab = b - a
    L2 = ab.length_squared
    t = 0.0 if L2 < 1e-12 else max(0.0, min(1.0, (p - a).dot(ab) / L2))
    return (a + ab * t - p).length


def at_terminal(p, a, b):
    """p is where a wire enters one of its own terminal parts (within WIRE_END_MM of the wire's end), or lies in a
    connector fitted in-line on that wire (an XT30U pair: its pins carry the circuit through the housing)."""
    for w, o in ((a, b), (b, a)):
        if not getattr(w, 'wire', False):
            continue
        if o.pid in w.inline or ('%s:%s' % (o.pid, o.name)) in w.inline or o.pid in MEMBRANE:
            return True
        if o.pid in w.terms and any((p - e).length <= WIRE_END_MM for e in w.ends):
            return True
        if getattr(o, 'wire', False) and (w.terms & o.terms) and                 any((p - e).length <= JOINT_MM for e in w.ends + o.ends):
            return True                               # wires sharing a terminal part meet in one solder joint
    return False


def end_seats(wire_bodies, solids):
    """D-86: every drawn strand end must be seated: inside, or within END_SEAT_MM of, a body of one of the wire's
    terminal parts or of a connector fitted in-line on it. A lead that stops in mid-air (an undrawn connector) fails."""
    byp = {}
    for b in solids:
        byp.setdefault(b.pid, []).append(b)
    bad = []
    for w in wire_bodies:
        hosts = set(w.terms) | {i.split(':')[0] for i in w.inline}
        for e in w.ends:
            best = 1e9
            for pid in hosts:
                for b in byp.get(pid, []):
                    if not all(b.lo[i] - 5 <= e[i] <= b.hi[i] + 5 for i in range(3)):
                        continue
                    if all(b.lo[i] <= e[i] <= b.hi[i] for i in range(3)) and inside(e, b):
                        best = 0.0
                        break
                    r = b.bvh.find_nearest(e, 5.0)
                    if r[0] is not None:
                        best = min(best, r[3])
                if best == 0.0:
                    break
            if best > w.r + END_SEAT_MM:             # the conductor's surface on the pad: axis one radius off
                bad.append({'wire': w.pid, 'strand': w.idx, 'end_mm': [round(c, 1) for c in e],
                            'gap_mm': None if best > 1e8 else round(best, 2), 'hosts': sorted(hosts)})
    return bad


def make_bodies(comp, matrix, col, tag='', R=None):
    """Bodies of one part in world mm, each carrying the part's cutters (exact; see CUT_TOL_MM) as Bodies of their own;
    R: extra 4x4 world motion (sweep pose) applied to the cutters as well."""
    M = Matrix(matrix)
    cutters = []
    if comp.get('cuts'):
        cutcol = bpy.data.collections.new('%s%s cutters' % (comp['id'], tag))
        bpy.context.scene.collection.children.link(cutcol)
        for k, (s, Mc) in enumerate(comp['cuts']):
            Mc = Matrix(Mc) if R is None else Matrix(R) @ Matrix(Mc)
            ob = bm_._body('%s%s cut%d' % (comp['id'], tag, k), s, Mc, cutcol, 0.0)
            if len(ob.data.vertices):
                c = Body(comp['id'], -1 - k, s.get('name') or 'cut %d' % k, ob)
                c.cutters = []
                cutters.append(c)
    out = []
    for i, s in enumerate(comp['bodies']):
        ob = bm_.body_object('%s%s#%d' % (comp['id'], tag, i), s, M, col)
        if len(ob.data.vertices):
            b = Body(comp['id'], i, s.get('name') or 'body %d' % i, ob)
            b.cutters = [c for c in cutters if all(c.lo[j] - CUT_TOL_MM < b.hi[j] and c.hi[j] + CUT_TOL_MM > b.lo[j] for j in range(3))]
            out.append(b)
    return out


def check(pairs, report_mm):
    """pairs: iterable of (Body, Body). Returns one hit per part pair whose bodies penetrate deeper than report_mm:
    depth (mm, deepest sampled point), where, and the body pairs."""
    hits = {}
    for a, b in pairs:
        if not boxes_overlap(a, b):
            continue
        ov = a.bvh.overlap(b.bvh)
        if ov:
            depth, at = penetration(a, b, ov)
        else:                                          # no crossing surfaces: one wholly inside the other?
            depth, at = 0.0, None
            for x, y in ((a, b), (b, a)):
                if x.probe is not None and all(y.lo[i] <= x.lo[i] and x.hi[i] <= y.hi[i] for i in range(3)) \
                        and depth_inside(x.probe, y) > 0 and not removed(x.probe, y) and not removed(x.probe, x):
                    depth = min(x.hi[i] - x.lo[i] for i in range(3)) / 2       # half its thinnest size
                    at = x.probe
                    break
        if depth <= report_mm:
            continue
        key = tuple(sorted((a.pid, b.pid)))
        h = hits.setdefault(key, {'a': key[0], 'b': key[1], 'depth_mm': 0.0, 'at_mm': None, 'bodies': []})
        if depth > h['depth_mm']:
            h['depth_mm'], h['at_mm'] = round(depth, 3), [round(v, 2) for v in at]
        h['bodies'].append('%s "%s" x %s "%s" %.2f mm' % (a.pid, a.name, b.pid, b.name, depth))
    for h in hits.values():
        h['bodies'].sort(key=lambda s: -float(s.split()[-2]))
    return list(hits.values())


def sweep_pairs(bodies):
    """All pairs of bodies of different parts with overlapping boxes (sort and sweep on x)."""
    order = sorted(bodies, key=lambda b: b.lo[0])
    act = []
    for b in order:
        act = [a for a in act if a.hi[0] > b.lo[0] + EPS_BOX]
        for a in act:
            if a.pid != b.pid:
                yield a, b
        act.append(b)


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    with open(argv[0], encoding='utf-8') as f:
        job = json.load(f)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    col = bpy.data.collections.new('static')
    bpy.context.scene.collection.children.link(col)
    comps = {c['id']: c for c in job['comps']}
    static = []
    for c in job['comps']:
        static += make_bodies(c, c['matrix'], col)
    wires = make_wires(job.get('wires', []), col)
    static += wires
    print('collide: %d bodies in %d parts, %d wire strands' % (len(static), len(comps), len(wires)))
    rep = {'bodies': len(static), 'parts': len(comps), 'wire_strands': len(wires), 'poses': [], 'defects': sorted(set(bm_.DEFECTS))}
    for pz in job['poses']:
        rmm = job['report_mm']
        if not pz['over']:
            hits = check(sweep_pairs(static), rmm)
        else:
            moved = set(pz['over'])
            skip = set(pz.get('skip_with') or ())
            pcol = bpy.data.collections.new(pz['name'][:50])
            bpy.context.scene.collection.children.link(pcol)
            mv = []
            for pid, M in pz['over'].items():
                mv += make_bodies(comps[pid], M, pcol, '@', R=pz['R'][pid])
            fixed = [b for b in static if b.pid not in moved and b.pid not in skip]
            hits = check(((a, b) for a in mv for b in fixed), rmm)
        rep['poses'].append({'name': pz['name'], 'moved': pz.get('moved'), 'not_swept_against': pz.get('skip_with'),
                             'hits': hits})
        print('collide: %-50s %d overlapping part pairs' % (pz['name'][:50], len(hits)))
    rep['wire_ends'] = end_seats(wires, [b for b in static if not getattr(b, 'wire', False)])
    print('collide: %d wire ends not seated' % len(rep['wire_ends']))
    if job.get('audit'):
        solids = [b for b in static if not getattr(b, 'wire', False)]
        rep['wire_audit'] = audit_wires(job.get('wires', []), wires, solids, wires)
    with open(argv[1], 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1)


if __name__ == '__main__':
    main()
