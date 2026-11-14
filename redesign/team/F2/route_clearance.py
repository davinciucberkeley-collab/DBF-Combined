"""F2 route clearance: does any routed wire pass through a solid part, a groove wall, or another wire?

    blender -b --factory-startup -P redesign/team/F2/route_clearance.py -- [--json OUT.json] [--clear-mm 1.0]
                                                                            [--params harness-params.json]

Builds the aircraft with the Blender backend (same geometry as the CAD, the renders and the GLB: the wing core has
its grooves, P1 straw holes and lead holes cut, the pod side walls their exit windows), turns every body of every
flight part into a world-space BVH tree (mass proxies HRN-001/-002 excluded) and samples, every 0.5 mm, every strand
the CAD draws (subsystems/harness/params.json cad.wire_strands: the 16 AWG pairs and the servo ribbon conductor by
conductor, other rows as one bundle tube; older params: the wire_table polyline at the drawn diameter), corners
rounded to the edge bend radius exactly as blender_backend draws them.
  solid    inside a body (ray parity) -> penetration = radius + depth; outside but closer than the radius ->
           penetration = radius - distance; closer than radius + --clear-mm (default 1 mm) -> "tight"
  wire     two strands of DIFFERENT edges closer than the sum of their radii -> penetration (sum - distance)

Not counted (declared passages; each one has a hole in the CAD or is a stated contact):
    L  liner: P1 straw (WNG-001), fin lead hole + grommet (FIN-001), servo lead hole (WNG-001), handle leg window and
       bore (POD-007), under-pack channel (POD-001 floor / POD-002 tray)
    P  runs taped to the pod floor and tray (POD-001 floor bodies, POD-002) - not the side or aft walls
    M  GPS cable in the grip groove / mast (POD-005, POD-007)
    F/L  the tape skin (WNG-003) where a lead goes under it at a groove or straw mouth
    E  the first / last 12 mm of a strand (landing on its pad, pin or connector; for wire-vs-wire both strands)
    own lead  W-PACK inside PWR-001 (the pack part models its own 10 AWG lead); each W-PWR-<st> inside its own XT30U
              HRN-113-<st> (D-74: the pair is soldered into it). Other wires against the XT30U bodies are checked
The groove walls and floors (WNG-001) are NOT exempt: a conductor in its groove must clear them.
Exit code 0 always (a report); prints the tables and writes JSON when --json is given.
"""
import fnmatch
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RED, 'blender'))

import bmesh                                   # noqa: E402
from mathutils import Vector                   # noqa: E402
from mathutils.bvhtree import BVHTree          # noqa: E402
from mathutils.kdtree import KDTree            # noqa: E402
import blender_backend as bb                   # noqa: E402

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
out_json = argv[argv.index('--json') + 1] if '--json' in argv else None
params = argv[argv.index('--params') + 1] if '--params' in argv else os.path.join(RED, 'subsystems/harness/params.json')
CLEAR = float(argv[argv.index('--clear-mm') + 1]) / 1000 if '--clear-mm' in argv else 0.001
STEP = 0.0005
END_ZONE = 0.012
OWN_LEAD = {'W-PACK': 'PWR-001'}               # pack lead: PWR-001 models it (bodies "pack leads 10 AWG ...")
OWN_LEAD.update({'W-PWR-' + s: 'HRN-113-' + s for s in ('UR', 'UL', 'LR', 'LL')})   # each ESC pair through its XT30U

# (segment code, part pattern, body pattern): declared passages (see the docstring)
PASSAGES = [('L', 'WNG-001', '*'), ('L', 'FIN-001-*', '*'), ('T', 'FIN-001-*', '*'),
            ('L', 'POD-007', '*'), ('M', 'POD-007', '*'), ('M', 'POD-005', '*'),
            ('L', 'POD-001', 'fb floor*'), ('L', 'POD-002', '*'),
            ('P', 'POD-001', 'fb floor*'), ('P', 'POD-002', '*'),
            ('F', 'WNG-003', '*'), ('L', 'WNG-003', '*')]


def lv(d):
    return d['value'] if isinstance(d, dict) and 'value' in d else d


be, ctx, graph, results = bb.build(False, None, log=lambda *a: None)
H = json.load(open(params, encoding='utf-8'))['harness']
rows = lv(H['wire_table'])
DIA = lv(H.get('cad', {}).get('wire_draw_dia_m', {}))
STRANDS = lv(H.get('cad', {}).get('wire_strands', {}))

trees = {}                                       # (part id, body index) -> (tree, lo, hi, body name)
for pid, comp in ctx.components.items():
    if not comp.flight or getattr(comp, 'proxy', False) or pid.startswith(('HRN-001', 'HRN-002')) or pid not in be.objects:
        continue
    M = be.objects[pid].matrix_world
    for k, shape in enumerate(comp.shapes):          # one tree per body: a closed shell each, so ray parity holds
        bm = bmesh.new()
        bb.BUILDERS[shape.kind](bm, shape)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
        bm.transform(M)
        if not bm.verts:
            bm.free()
            continue
        lo = Vector([min(v.co[i] for v in bm.verts) for i in range(3)])
        hi = Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
        trees[(pid, k)] = (BVHTree.FromBMesh(bm), lo, hi, shape.name or shape.kind)
        bm.free()

RAY = Vector((1.0, 0.0123, 0.0071)).normalized()


def inside(tree, p):
    n, q = 0, p.copy()
    for _ in range(64):
        loc, _nrm, _i, _d = tree.ray_cast(q, RAY)
        if loc is None:
            break
        n += 1
        q = loc + RAY * 1e-5
    return n % 2 == 1


def exempt(code, pid, body, wid):
    if any(c == code and fnmatch.fnmatchcase(pid, pp) and fnmatch.fnmatchcase(body, bp) for c, pp, bp in PASSAGES):
        return True
    return OWN_LEAD.get(wid) == pid


def near_segs(P, p, tol=0.003):
    """Centreline segments a drawn sample belongs to: the nearest, plus a neighbour when the sample is on the rounded
    corner between them (within `tol` of both)."""
    d = []
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)) if ab.length_squared > 0 else 0.0
        d.append((a + ab * t - p).length)
    k = min(range(len(d)), key=d.__getitem__)
    return k, [i for i in (k - 1, k, k + 1) if 0 <= i < len(d) and d[i] < d[k] + tol]


# ---- samples of every drawn strand: (point, radius, wire id, edge, strand index, centreline seg codes, in end zone)
samples = []
for r in rows:
    wid, eid, awg, pts = r[0], r[1], r[2], r[9]
    e = graph.edges.get(eid, {})
    strands = STRANDS.get(wid) or [[DIA.get(eid, 0.003 if awg >= 26 else 0.006), [p[:3] for p in pts]]]
    P = [Vector(p[:3]) for p in pts]
    for si, (dia, line) in enumerate(strands):
        bend = e.get('wire', {}).get('bend_radius_mm', 5 * dia * 1000) / 1000.0
        Q = bb.fillet_polyline(line, bend)
        a_end, b_end = Vector(line[0]), Vector(line[-1])
        sp = []
        for i in range(len(Q) - 1):
            a, b = Q[i], Q[i + 1]
            n = max(1, int((b - a).length / STEP))
            sp += [a.lerp(b, s / n) for s in range(n)]
        sp.append(Q[-1])
        for p in sp:
            k, ks = near_segs(P, p)
            samples.append((p, dia / 2, wid, eid, si, k, [pts[i][3] for i in ks],
                            min((p - a_end).length, (p - b_end).length) < END_ZONE))

found, tight = [], []
hits, near = {}, {}
for (pid, _k), (tree, lo, hi, body) in trees.items():
    for p, rad, wid, eid, si, k, codes, endz in samples:
        if endz or any(p[i] < lo[i] - rad - CLEAR or p[i] > hi[i] + rad + CLEAR for i in range(3)):
            continue
        loc, _nrm, _i, d = tree.find_nearest(p)
        if loc is None:
            continue
        ins = inside(tree, p)
        if not ins and d >= rad + CLEAR:
            continue
        if any(exempt(c, pid, body, wid) for c in codes):
            continue
        depth = rad + d if ins else rad - d
        rec = {'kind': 'solid', 'wire': wid, 'edge': eid, 'strand': si, 'seg': k, 'code': codes[0], 'part': pid,
               'body': body, 'depth_mm': round(depth * 1000, 2), 'centre_inside': ins,
               'dia_mm': round(rad * 2000, 2), 'at': [round(v, 4) for v in p]}
        tgt = hits if depth > 0 else near
        key = (wid, k, pid, body)
        if key not in tgt or depth * 1000 > tgt[key]['depth_mm']:
            tgt[key] = rec

# ---- wire against wire (different edges)
kd = KDTree(len(samples))
for i, s in enumerate(samples):
    kd.insert(s[0], i)
kd.balance()
rmax = max(s[1] for s in samples)
for i, (p, rad, wid, eid, si, k, codes, endz) in enumerate(samples):
    if endz:
        continue
    for q, j, d in kd.find_range(p, rad + rmax + CLEAR):
        s2 = samples[j]
        if s2[3] == eid or s2[7] or j < i:
            continue
        depth = rad + s2[1] - d
        if depth <= -CLEAR:
            continue
        rec = {'kind': 'wire', 'wire': wid, 'edge': eid, 'strand': si, 'seg': k, 'code': codes[0], 'part': s2[2],
               'body': 'strand %d' % s2[4], 'depth_mm': round(depth * 1000, 2), 'centre_inside': False,
               'dia_mm': round(rad * 2000, 2), 'at': [round(v, 4) for v in p]}
        tgt = hits if depth > 0 else near
        key = (wid, k, s2[2], 'wire')
        if key not in tgt or depth * 1000 > tgt[key]['depth_mm']:
            tgt[key] = rec

found = sorted(hits.values(), key=lambda h: (h['wire'], h['seg'], -h['depth_mm']))
tight = sorted((h for kk, h in near.items() if kk not in hits), key=lambda h: (h['wire'], h['seg'], -h['depth_mm']))
nw = sum(1 for h in found if h['kind'] == 'wire')
print('\nroute clearance: %d wire rows, %d strands samples, %d bodies: %d penetrations (%d solid, %d wire-wire), '
      '%d tight (< %.1f mm)' % (len(rows), len(samples), len(trees), len(found), len(found) - nw, nw, len(tight),
                                CLEAR * 1000))
print('%-5s %-12s %-8s %3s %s %-12s %-28s %7s %s' % ('kind', 'wire', 'edge', 'seg', 'c', 'part/wire', 'body', 'mm', 'at'))
for h in found:
    print('%-5s %-12s %-8s %3d %s %-12s %-28s %7.2f %s' % (h['kind'], h['wire'], h['edge'], h['seg'], h['code'],
                                                         h['part'], h['body'][:28], h['depth_mm'], h['at']))
print('tight (no overlap, clearance < %.1f mm; mm = -clearance):' % (CLEAR * 1000))
for h in tight:
    print('%-5s %-12s %-8s %3d %s %-12s %-28s %7.2f' % (h['kind'], h['wire'], h['edge'], h['seg'], h['code'],
                                                      h['part'], h['body'][:28], h['depth_mm']))
if out_json:
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump({'params': os.path.relpath(params, RED).replace(os.sep, '/'), 'clear_mm': CLEAR * 1000,
                   'penetrations': found, 'tight': tight}, f, indent=1)
