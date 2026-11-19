"""a_linkage_blender.py - runs INSIDE Blender for `collide_a.py --linkage-poses` (T-020). Uses collision/collide_blender.py (unmodified) through
a_collide_blender.py (inside-out fix) and its own pose loop: one Blender session, every pose of the job, with
  * every moved part against every fixed part (all bodies, cuts honoured as in the static gate),
  * moved parts of different groups (elevon / arm / rod) against each other (rod x arm, rod x keeper, rod x clevis pin, ...),
  * per pose the minimum surface-to-surface distance (clearance) of the linkage parts to every neighbour within CAP_MM.
Clearance = min over sample points of the target mesh (vertices and 15 points per triangle) of the distance to the neighbour's BVH, refined
by alternating nearest-point projection (an upper bound of the true mesh distance, converging to a local minimum); where the pair also
penetrates (hit above the report threshold) the penetration depth is the figure.
    blender -b --factory-startup -P a_linkage_blender.py -- <_job_linkage.json> <report_linkage_poses.json>
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a_collide_blender as acb       # noqa: E402  (applies the inside-out fix, imports collide_blender)
import bpy                             # noqa: E402

cb = acb.cb
TARGET_PARTS = ('MEC-002', 'MEC-003', 'MEC-004', 'MEC-005', 'MEC-008', 'HWC-002')
CAP_MM = 3.0


def pk(pid):
    return pid.rsplit('-', 1)[0] if pid[-2:] in ('-R', '-L') else pid


def min_dist(a, b, cap=CAP_MM, top=4):
    """Min distance (mm) between meshes a and b, None when farther than cap. Samples from a (always) and from b (when small)."""
    best = None
    for src, dst in ((a, b), (b, a)):
        if src is b and len(b.tris) > 3000:
            continue
        lo = [dst.lo[i] - cap for i in range(3)]
        hi = [dst.hi[i] + cap for i in range(3)]
        cand = []
        for t in src.tris:
            if not all(min(v[i] for v in t) <= hi[i] and max(v[i] for v in t) >= lo[i] for i in range(3)):
                continue
            for p in cb.tri_samples(t):
                loc, _n, _i, d = dst.bvh.find_nearest(p, cap)
                if loc is not None:
                    cand.append((d, p))
        cand.sort(key=lambda c: c[0])
        for d, p in cand[:top]:
            for _ in range(6):                                   # alternating projection: p on src, q on dst
                q, _n, _i, _d = dst.bvh.find_nearest(p)
                p2, _n2, _i2, _d2 = src.bvh.find_nearest(q)
                d2 = (p2 - q).length
                if d2 >= d - 1e-9:
                    break
                d, p = d2, p2
            if best is None or d < best:
                best = d
    return best


def clearances(mvb, mv, fixed, groups, hits):
    """Per target part and neighbour part: min distance (mm); negative = penetration depth from the hit list."""
    depth = {}
    for h in hits:
        depth[frozenset((h['a'], h['b']))] = h['depth_mm']
    allb = mv + fixed
    out = {}
    for pid, bodies in mvb.items():
        if pk(pid) not in TARGET_PARTS:
            continue
        for a in bodies:
            for b in allb:
                if b.pid == pid or (b.pid in mvb and pid in mvb and pk(b.pid) in TARGET_PARTS and b.pid < pid):
                    continue                                      # target-target pairs once
                if not all(a.lo[i] - CAP_MM < b.hi[i] and b.lo[i] < a.hi[i] + CAP_MM for i in range(3)):
                    continue
                d = min_dist(a, b)
                if d is None:
                    continue
                key = '%s|%s' % (pid, b.pid)
                same = groups.get(pid) is not None and groups.get(pid) == groups.get(b.pid)
                cur = out.get(key)
                if cur is None:
                    cur = out[key] = {'d_mm': round(d, 4), 'a': a.name, 'b': b.name, 'same_group': bool(same), 'bodies': {}}
                elif d < cur['d_mm']:
                    cur.update({'d_mm': round(d, 4), 'a': a.name, 'b': b.name})
                bk = '%s || %s' % (a.name, b.name)
                cur['bodies'][bk] = round(min(d, cur['bodies'].get(bk, 1e9)), 4)
    for key, v in out.items():
        p, q = key.split('|')
        dp = depth.get(frozenset((p, q)))
        if dp is not None:
            v['penetration_mm'] = dp
    return out


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    with open(argv[0], encoding='utf-8') as f:
        job = json.load(f)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    col = bpy.data.collections.new('static')
    bpy.context.scene.collection.children.link(col)
    comps = {c['id']: c for c in job['comps']}
    t0 = time.time()
    static = []
    for c in job['comps']:
        static += cb.make_bodies(c, c['matrix'], col)
    wires = cb.make_wires(job.get('wires', []), col)
    static += wires
    print('linkage: %d bodies in %d parts, %d wire strands (%.0f s)' % (len(static), len(comps), len(wires), time.time() - t0), flush=True)
    rep = {'bodies': len(static), 'parts': len(comps), 'wire_strands': len(wires), 'poses': [], 'defects': sorted(set(cb.bm_.DEFECTS)),
           'report_mm': job['report_mm'], 'flipped_inside_out': len(acb.FLIPPED)}
    rmm = job['report_mm']
    for pz in job['poses']:
        t1 = time.time()
        entry = {'name': pz['name'], 'delta': pz.get('delta'), 'state': pz.get('state'), 'theta_deg': pz.get('theta_deg'), 'moved': pz.get('moved')}
        if not pz['over']:
            hits = cb.check(cb.sweep_pairs(static), rmm)
            entry['clear'] = {}
        else:
            moved = set(pz['over'])
            skip = set(pz.get('skip_with') or ())
            grp = pz['groups']
            pcol = bpy.data.collections.new(pz['name'][:50])
            bpy.context.scene.collection.children.link(pcol)
            mvb = {pid: cb.make_bodies(comps[pid], M, pcol, '@', R=pz['R'][pid]) for pid, M in pz['over'].items()}
            mv = [b for bs in mvb.values() for b in bs]
            fixed = [b for b in static if b.pid not in moved and b.pid not in skip]
            hits = cb.check(((a, b) for a in mv for b in fixed), rmm)
            cross = ((a, b) for a in mv for b in mv if grp[a.pid] != grp[b.pid] and a.pid < b.pid)
            hits += cb.check(cross, rmm)
            entry['clear'] = clearances(mvb, mv, fixed, grp, hits)
        entry['hits'] = hits
        entry['seconds'] = round(time.time() - t1, 1)
        rep['poses'].append(entry)
        print('linkage: %-34s %2d overlapping part pairs, %d clearance pairs, %.0f s' % (pz['name'][:34], len(hits), len(entry['clear']), time.time() - t1), flush=True)
    rep['wire_ends'] = cb.end_seats(wires, [b for b in static if not getattr(b, 'wire', False)], require_term=True)
    print('linkage: %d wire ends not seated' % len(rep['wire_ends']), flush=True)
    with open(argv[1], 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1)


if __name__ == '__main__':
    main()
