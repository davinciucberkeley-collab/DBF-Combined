"""collide_glb_blender.py - the no-phasing gate on the EXPORTED model (runs inside Blender for collide.py --glb):

    blender -b --factory-startup --python-exit-code 1 -P collide_glb_blender.py -- <_job.json> <assembly.glb> <out.json>

collide_blender.py checks the CAD with each part's holes taken from its cutters (removed material by definition). That
cannot see a boolean that failed in the exported model: a 45 deg lead hole that came out uncut showed a wire through
solid foam in the 3-D explorer while the CAD check passed (D-88). Here every part is the mesh the explorer shows, cuts
baked in, and NO cutter is honoured: a wire that runs through foam where a hole should be fails. Wires are meshed from
the same strands as the GLB (job file). Same depth test, tolerance and wire rules as collide_blender (terminal end,
in-line connector, strands of one wire checked against each other), plus the wire-entry rule:

  entry   where a strand enters its terminal part (or an in-line connector) it must cross ONE face, square to it
          (strand axis within 25 deg of the face normal), with the face flat for the strand's radius + RING_MM round
          the crossing (the whole lead lands on the face, not over an edge or a corner), and it may run at most
          WIRE_END_MM past that face.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import collide_blender as cb  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.geometry import intersect_ray_tri  # noqa: E402

ENTRY_DEG = 25.0
FLAT_DEG = 10.0
RING_MM = 0.1                  # D-88: the lead's whole section on the face, 0.1 mm clear of its edges


RAYS = (Vector((1.0, 0.31, 0.17)).normalized(), Vector((-0.23, 1.0, 0.41)).normalized(),
        Vector((0.37, -0.29, 1.0)).normalized(), Vector((-0.71, -0.43, -0.59)).normalized(),
        Vector((0.13, -0.83, -0.47)).normalized())     # skewed: never along a modelled face, edge or bore axis


WALL_MM = 2e-3                 # faces this close along a ray are one crossing place (a wall of two touching faces)


def crossings(body, point, ray):
    """Surfaces a ray from `point` crosses. Where two bodies of a part touch face to face (tape layers on each other,
    a block on its boss) the exported solid can keep both faces, a zero-thickness wall with opposite normals; the
    BVH returns one of them and the next step skips the other, so a plain hit count is off by one. At each hit
    every triangle the ray crosses within WALL_MM is found; facing the ray and facing away count as one crossing
    each (two triangles of one surface meeting at an edge the ray passes through face the same way: one)."""
    n, p = 0, point.copy()
    for _ in range(64):
        hit = body.bvh.ray_cast(p, ray)
        if hit[0] is None:
            break
        h = hit[0]
        sides = set()
        for _l, _n, i, _d in body.bvh.find_nearest_range(h, WALL_MM):
            a, b, c = body.tris[i]
            x = intersect_ray_tri(a, b, c, ray, h - ray * WALL_MM, False)
            if x is not None and (x - h).length <= WALL_MM:
                sides.add((b - a).cross(c - a).dot(ray) > 0)
        n += max(1, len(sides))
        p = h + ray * (1.5 * WALL_MM)                  # mm; float32 BVH: 1e-6 re-hits the same face
    return n


def depth_inside(point, body):
    """collide_blender.depth_inside with a parity test that holds on exact fits. There the parity ray runs along +x;
    with no cutters honoured, a bolt's surface point lies ON its hole wall, and for a bore along x (pinch bolt
    FIN-101 through the FIN-003 ears, nut FIN-102) the +x ray grazes along that wall and its hit count is noise, while
    the nearest face is the hole's rim edge, whose normal reads either sign: a point 2 mm outside the ear read 2 mm deep.
    Here: a point is outside when the nearest-face normal clearly says so ((p - loc).n >= d / 2, away from any edge);
    otherwise inside = odd crossings (crossings(): touching faces counted) on at least three of five skewed rays.
    Returns the distance to the surface when inside."""
    loc, nrm, _i, d = body.bvh.find_nearest(point)
    if loc is None or (point - loc).dot(nrm) >= 0.5 * d:
        return 0.0
    odd = even = 0
    for ray in RAYS:
        if crossings(body, point, ray) % 2:
            odd += 1
        else:
            even += 1
        if odd == 3 or even == 3:
            break
    return d if odd >= 3 else 0.0


def parity_inside(point, body):
    """Odd crossings on three of five rays (no nearest-face shortcut: for points just under a surface)."""
    odd = even = 0
    for ray in RAYS:
        if crossings(body, point, ray) % 2:
            odd += 1
        else:
            even += 1
        if odd == 3 or even == 3:
            break
    return odd >= 3


BACK_MM = 0.01                 # material must lie this far behind a surface sample for it to count


def penetration(a, b, pairs):
    """collide_blender.penetration, plus: a surface sample of one part counts only where its own part has material
    behind it (BACK_MM under the surface). Where two bodies of a part touch, the exported solid can keep a wall of
    zero thickness: the tape skin keeps one on a cover screw's bearing face, inside the screw head. It holds no
    material and read as the skin 0.8 mm deep in the head."""
    deep, at = 0.0, None
    for src, dst, ids in ((a, b, {i for i, _j in pairs}), (b, a, {j for _i, j in pairs})):
        for i in ids:
            t = src.tris[i]
            nrm = (t[1] - t[0]).cross(t[2] - t[0])
            if nrm.length == 0:
                continue
            nrm.normalize()
            for p in cb.tri_samples(t):
                d = depth_inside(p, dst)
                if d > deep and not cb.at_terminal(p, a, b) and (getattr(src, 'wire', False)
                                                                   or parity_inside(p - nrm * BACK_MM, src)):
                    deep, at = d, p
    return deep, at


cb.depth_inside = depth_inside                         # used by cb.check / penetration / end_seats in this run only
cb.penetration = penetration


def part_bodies(col, flight):
    out = []
    for ob in list(bpy.data.objects):
        if ob.type != 'MESH' or not len(ob.data.vertices):
            continue
        pid = ob.get('part_id') or ob.name.split('.')[0]
        if str(pid).startswith('E-') or pid.startswith('JOINT'):
            continue                                       # wires come from the job (same strands)
        if pid not in flight:
            continue                                       # transport box, ground kit: as collide_blender
        ob.matrix_world = Matrix.Scale(1000.0, 4) @ ob.matrix_world   # millimetres, as collide_blender
        b = cb.Body(str(pid), len(out), ob.name, ob)       # one solid per part (blender_backend._unite, D-88)
        b.cutters = []
        out.append(b)
    return out


def entry_check(wires, solids):
    """For each strand end that lies inside one of its terminal / in-line parts: walk back along the strand to where
    it crosses that part's surface and test the crossing."""
    byp = {}
    for b in solids:
        byp.setdefault(b.pid, []).append(b)
    bad = []
    for w in wires:
        hosts = set(w.terms) | {i.split(':')[0] for i in w.inline}
        tris = w.tris
        pts = [w.ends[0], w.ends[1]]
        for k, e in enumerate(pts):
            host = None
            for pid in hosts:
                for b in byp.get(pid, []):
                    if all(b.lo[i] - 0.01 <= e[i] <= b.hi[i] + 0.01 for i in range(3)) and cb.inside(e, b):
                        host = b
                        break
                if host:
                    break
            if host is None:
                continue                                    # end on the surface (seated by end_seats) or outside
            # direction into the part: from the strand's other points toward this end
            line = w.line
            seq = line if k == 1 else list(reversed(line))  # ... -> end
            cross, tdir, run = None, None, 0.0
            for a, bpt in zip(reversed(seq[:-1]), reversed(seq[1:])):     # walk back from the end
                run += (bpt - a).length
                if not cb.inside(a, host):
                    # bisect the crossing on segment a (outside) -> bpt (inside)
                    lo_, hi_ = a.copy(), bpt.copy()
                    for _ in range(30):
                        m = (lo_ + hi_) / 2
                        if cb.inside(m, host):
                            hi_ = m
                        else:
                            lo_ = m
                    cross, tdir = (lo_ + hi_) / 2, (bpt - a).normalized()
                    run -= (bpt - cross).length
                    break
            if cross is None:
                bad.append({'wire': w.pid, 'strand': w.idx, 'end_mm': [round(c, 1) for c in e], 'part': host.pid,
                            'why': 'the whole strand lies inside %s' % host.pid})
                continue
            loc, nrm, _i, _d = host.bvh.find_nearest(cross)
            ang = math.degrees(math.acos(max(-1.0, min(1.0, abs(tdir.dot(nrm))))))
            # flat round the crossing: normals within FLAT_DEG over a ring of radius r + RING_MM on the face
            r = getattr(w, 'r', 0.5) + RING_MM
            u = nrm.orthogonal().normalized()
            v = nrm.cross(u).normalized()
            flat = True
            for j in range(8):
                q = loc + (u * math.cos(j * math.pi / 4) + v * math.sin(j * math.pi / 4)) * r
                l2, n2, _i2, _d2 = host.bvh.find_nearest(q)
                if l2 is None or n2.dot(nrm) < math.cos(math.radians(FLAT_DEG)) or (l2 - q).length > 0.3:
                    flat = False
                    break
            depth = (e - cross).length
            why = []
            if ang > ENTRY_DEG:
                why.append('enters %.0f deg off square' % ang)
            if not flat:
                why.append('enters at an edge or corner')
            if depth > cb.WIRE_END_MM + 0.01 and host.pid in w.terms:
                why.append('runs %.1f mm into %s' % (depth, host.pid))
            if why:
                bad.append({'wire': w.pid, 'strand': w.idx, 'end_mm': [round(c, 1) for c in e], 'part': host.pid,
                            'at_mm': [round(c, 1) for c in cross], 'why': '; '.join(why)})
    return bad


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    job = json.load(open(argv[0], encoding='utf-8'))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=argv[1])
    col = bpy.data.collections.new('wires')
    bpy.context.scene.collection.children.link(col)
    solids = part_bodies(col, {c['id'] for c in job['comps']})
    wires = cb.make_wires(job.get('wires', []), col)
    lines = {}
    for wj in job.get('wires', []):
        import blender_backend as bbk
        for k, (line, dia) in enumerate(wj['strands']):
            lines[(wj['id'], k)] = [v * 1000.0 for v in bbk.fillet_polyline([tuple(p) for p in line], wj['bend'])]
    for w in wires:
        w.line = lines[(w.pid, w.idx)]
    print('collide-glb: %d part bodies, %d wire strands' % (len(solids), len(wires)))
    hits = cb.check(cb.sweep_pairs(solids + wires), job['report_mm'])
    rep = {'bodies': len(solids), 'wire_strands': len(wires), 'hits': hits,
           'wire_ends': cb.end_seats(wires, solids), 'entries': entry_check(wires, solids)}
    with open(argv[2], 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1)
    print('collide-glb: %d overlapping pairs, %d unseated ends, %d bad entries' % (
        sum(1 for h in hits if h['depth_mm'] > 0.05), len(rep['wire_ends']), len(rep['entries'])))


if __name__ == '__main__':
    main()
