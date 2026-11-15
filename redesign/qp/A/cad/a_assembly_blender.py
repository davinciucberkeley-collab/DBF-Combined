"""a_assembly_blender.py - INSIDE Blender: swept-path check of a_assembly_plan.STEPS on the collide_a job (same meshes, cuts,
tolerance and penetration rule as the collision gate; inside-out fix of a_collide_blender).
    blender -b --factory-startup -P a_assembly_blender.py -- <_job.json> <plan.json> <result.json> [tol_mm]"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a_collide_blender as ac    # noqa: E402  (installs the orientation fix)
import collide_blender as cb      # noqa: E402
import bpy                        # noqa: E402


def clear(col):
    for ob in list(col.objects):
        me = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)


def run():
    argv = sys.argv[sys.argv.index('--') + 1:]
    job = json.load(open(argv[0], encoding='utf-8'))
    plan = json.load(open(argv[1], encoding='utf-8'))
    tol = float(argv[3]) if len(argv) > 3 else 0.05
    comps = {c['id']: c for c in job['comps']}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    static = bpy.data.collections.new('placed')
    bpy.context.scene.collection.children.link(static)
    temp = bpy.data.collections.new('temp')
    bpy.context.scene.collection.children.link(temp)
    placed, out = [], []
    for st in plan:
        parts = [p for p in st['parts'] if p in comps]
        res = {'id': st['id'], 'parts': parts, 'worst_mm': 0.0, 'first_hit_t_mm': None, 'pairs': []}
        if st['dir'] and parts:
            d = st['dir']
            n = int(st['travel'] // st['step']) + 1
            ts = {float(st['travel']), 0.0, 0.25, 0.5}
            ts |= {i * float(st['step']) for i in range(n)}
            worst = {}
            for t in sorted(ts, reverse=True):
                T = [[1, 0, 0, -d[0] * t / 1000.0], [0, 1, 0, -d[1] * t / 1000.0],
                     [0, 0, 1, -d[2] * t / 1000.0], [0, 0, 0, 1]]
                mv = []
                for pid in parts:
                    M = cb.Matrix(T) @ cb.Matrix(comps[pid]['matrix'])
                    mv += cb.make_bodies(comps[pid], [list(r) for r in M], temp, '@', R=T)
                hits = cb.check(((a, b) for a in mv for b in placed if cb.boxes_overlap(a, b)), job['report_mm'])
                for h in hits:
                    if h['depth_mm'] > tol:
                        key = (h['a'], h['b'])
                        if key not in worst or h['depth_mm'] > worst[key][0]:
                            worst[key] = (h['depth_mm'], t, h['at_mm'])
                        if res['first_hit_t_mm'] is None:
                            res['first_hit_t_mm'] = t
                clear(temp)
            res['pairs'] = [{'a': k[0], 'b': k[1], 'depth_mm': v[0], 'at_t_mm': v[1], 'at_mm': v[2]}
                            for k, v in sorted(worst.items(), key=lambda kv: -kv[1][0])]
            res['worst_mm'] = max([v[0] for v in worst.values()] or [0.0])
        for pid in parts:
            placed += cb.make_bodies(comps[pid], comps[pid]['matrix'], static)
        out.append(res)
        print('step %-3s %-7s worst %.3f mm' % (st['id'], 'ok' if res['worst_mm'] <= tol else 'BLOCKED', res['worst_mm']))
        sys.stdout.flush()
    json.dump({'steps': out, 'tol_mm': tol, 'flipped': len(ac.FLIPPED)}, open(argv[2], 'w'), indent=1)


run()
