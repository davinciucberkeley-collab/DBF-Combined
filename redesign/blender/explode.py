"""explode.py - exploded views along assembly vectors, computed from the interface graph (no per-aircraft tables).

How a vector is chosen (configuration-independent):
  1. The parts and their structural edges (rigid / revolute / slider joints and contacts) form a graph. The root is
     the part with the most structural edges (ties: heaviest), or the one you name.
  2. Walking out from the root, each child part (with everything hanging off it) moves away from its parent along
     the axis direction (+-x, +-y, +-z) that frees it with the shortest travel - computed from the bounding boxes, so
     a motor sitting on a boom lifts straight up and a servo in a wing pocket drops out of its pocket.
  3. Travel = that clearance + `gap`. Offsets add up along the tree, so sub-assemblies move as one.
  4. Bonded edges (connection type method "bonded": epoxy, CA) do not separate: a bonded part is one piece with its
     parent. Override any direction with overrides={'FUS-002': (0, 0, 1)} (unit axis or any vector).
Every part gets a custom property explode_m = [dx, dy, dz] (aircraft frame, metres at factor 1), so the GLB carries
the vectors and the web viewer can animate its own explode.
"""
from mathutils import Vector

DIRS = [Vector(v) for v in ((0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0))]   # tie order


def world_bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return (Vector((min(p[i] for p in pts) for i in range(3))), Vector((max(p[i] for p in pts) for i in range(3))))


def _clearance(child, parent, d):
    """Travel along unit axis d that takes box `child` clear of box `parent` (0 if already clear on that side)."""
    k = next(i for i in range(3) if d[i])
    if d[k] > 0:
        return max(0.0, parent[1][k] - child[0][k])
    return max(0.0, child[1][k] - parent[0][k])


def structural_edges(ctx, graph):
    """[(part_a, part_b, bonded)] for every registered joint or contact between built parts."""
    out = []
    for j in ctx.joints:
        out.append((j.a, j.b, False))
    for eid in ctx.contacts:
        e = graph.edges.get(eid, {})
        ct = graph.ctypes.get(e.get('via'), {})
        out.append((e.get('part_a'), e.get('part_b'), ct.get('method') == 'bonded'))
    return [(a, b, bd) for a, b, bd in out if a in ctx.components and b in ctx.components]


def vectors(be, ctx, graph, root=None, gap=0.06, overrides=None):
    """{part id: Vector offset} at factor 1. Parts not connected to the root's group get no offset."""
    overrides = {k: Vector(v).normalized() for k, v in (overrides or {}).items()}
    adj = {}
    for a, b, bonded in structural_edges(ctx, graph):
        adj.setdefault(a, []).append((b, bonded))
        adj.setdefault(b, []).append((a, bonded))
    if root is None:
        root = max(adj, key=lambda p: (len(adj[p]), ctx.components[p].mass_g or 0)) if adj else None
    # tree by breadth-first walk; bonded children are visited first so they join their parent's piece
    parent, order, seen = {}, [root], {root}
    i = 0
    while i < len(order):
        p = order[i]
        i += 1
        for q, bonded in sorted(adj.get(p, []), key=lambda t: not t[1]):
            if q not in seen:
                seen.add(q)
                parent[q] = (p, bonded)
                order.append(q)
    kids = {}
    for q, (p, _) in parent.items():
        kids.setdefault(p, []).append(q)

    def subtree(p):
        out, stack = [], [p]
        while stack:
            x = stack.pop()
            out.append(x)
            stack += kids.get(x, [])
        return out

    off = {root: Vector()}
    for q in order[1:]:
        p, bonded = parent[q]
        if bonded:
            off[q] = off[p].copy()
            continue
        cb = world_bbox([be.objects[x] for x in subtree(q)])
        pb = world_bbox([be.objects[p]])
        if q in overrides:
            d = overrides[q]
            ax = max(range(3), key=lambda k: abs(d[k]))
            unit = Vector([1.0 if k == ax else 0.0 for k in range(3)]) * (1 if d[ax] > 0 else -1)
            travel = _clearance(cb, pb, unit) + gap
        else:
            d = min(DIRS, key=lambda u: _clearance(cb, pb, u) + 1e-6 * DIRS.index(u))
            travel = _clearance(cb, pb, d) + gap
        off[q] = off[p] + d * travel
    return off


def apply(be, offsets, factor=1.0, hide_wires=True):
    """Move parts by factor x offset (from their modelled place). factor 0 = assembled. Records explode_m."""
    for pid, ob in be.objects.items():
        if '_home' not in ob:
            ob['_home'] = list(ob.matrix_world.translation)
        v = offsets.get(pid, Vector())
        ob['explode_m'] = [round(c, 4) for c in v]
        ob.matrix_world.translation = Vector(ob['_home']) + v * factor
    for ob in be.wires.values():
        ob.hide_render = ob.hide_viewport = bool(hide_wires and factor)
    for ob, j in be.joints.values():
        ob.location = Vector(j.origin) + offsets.get(j.a, Vector()) * factor
