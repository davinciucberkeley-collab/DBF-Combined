"""assembly_check.py - plans how a person puts K09-L together and checks every motion as a swept path.

    python -I redesign/showcase/animation/assembly_check.py              # plan + check, about 25 min
    python -I redesign/showcase/animation/assembly_check.py --report-only  # rewrite the report from the last run
    python -I redesign/showcase/animation/assembly_check.py --legacy     # also score the old fly-in film
    python -I redesign/showcase/animation/assembly_check.py --steps 2.1,2.3,2.4,2.5   # debug a few steps

Writes (next to the film, redesign/showcase/animation/build/):
    assembly_plan.json   every action in order with its checked motion (read by render_build.py)
    ASSEMBLY-CHECK.md    the report: violations, support, exceptions, overrides used
Exit 1 when any motion passes through a part already placed (or through a bench-mate), deeper than --tol-mm.

Order: assembly_plan.STEPS (BUILD-GUIDE.md step by step). Geometry: the collision gate's own job
(collision/collide.py --job-only: the stub-backend CAD bodies and cuts, the drawn wires) meshed by the gate's own
collide_blender.make_bodies / make_wires, so drilled holes, bores, slots and seats (cutters) count as empty exactly as
in the gate, and the in-line / terminal exemptions for wires are the gate's (collide_blender.at_terminal).

Motion of each rigid part (or bench sub-assembly), found from the geometry, not hand-placed:
  1. removal directions to try, in this order: OVERRIDES 'dirs'; the normal of the face the part mounts on (mean of the
     surface normals of already-placed parts within CONTACT_MM of it; a part in a pocket or bore sees the cutter's
     faces, so the mean points out of the pocket); the axes of its own bodies (revolve axis of a tube, pin or screw,
     extrusion axis of a prism), heaviest first; then the six world axes. Both signs; the side away from what it
     touches first.
  2. straight path: from the seated pose outward along the direction until its bodies' boxes clear every placed
     body's box (+ MARGIN_MM). Sampled at 0.05-0.5 mm for the first 6 mm, then every min(1 mm, half the part's own
     length along the path). At each sample the part is re-meshed at that pose (BVH) and tested against every placed
     body it can reach: surface crossings sampled 15 points per triangle (collide_blender.penetration's rule), depth
     beyond --tol-mm in material that is not cut away = a hit.
  3. if the straight path is blocked further out than 3 mm, a two-segment path: out along the direction to just
     short of the hit, then sideways along another axis until clear.
  The first collision-free candidate is the motion. Screws turn while they travel their last thread length.
  Tape ('lay'), wet epoxy ('fill') and wires are not rigid: they are laid in place, so their final pose is what the
  collision gate already checks; here they get the support check, and a wire laid AFTER a tape that it touches
  (a lead under the skin) is a violation. Elevon panels swing about the gate's hinge joints, sampled every 1 deg.
Support: every placed item must touch (within CONTACT_MM, or seated in a cut) something already placed, or be held by
a fixture named in assembly_plan.OVERRIDES; the first part of a bench group is held on the bench. Others are listed.
"""
import argparse
import datetime
import fnmatch
import json
import math
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(HERE))
COLL = os.path.join(REDESIGN, 'collision')
OUT = os.path.join(HERE, 'build')
BLENDER_DEFAULT = r'C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe'
for _p in (HERE, COLL):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import assembly_plan as ap                  # noqa: E402

TOL_MM = 0.05            # penetration that counts (collision gate: collide.py --tol-mm default)
CONTACT_MM = 0.1         # a vertex this close to a placed surface (or to the face of its cut) is in contact
BOND_GAP_MM = 0.6        # a bond line (epoxy, foam tape, gel pad) may leave up to this gap where interfaces.json joins
#                          the two parts (an edge); further apart is not support
MARGIN_MM = 4.0          # extra travel beyond the first free position (where the hand starts the motion)
CLEAR_PAD_MM = 5.0       # the part counts as free when its box is this far from every placed body's box
MAX_TRAVEL_MM = 650.0
FINE = [0.05, 0.15, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
SWING_STEP_DEG = 1.0
SPIN_TURNS = 3.0         # screw turns shown (and checked, for non-round bodies) over the thread length
THREAD_MM = 6.0
PAIR_CAP = 1500          # crossing triangles tested per body pair and pose (more: an even subset; a real clash
#                          crosses many triangles, a bore wall sliding on its tube crosses thousands at ~0 depth)
MAX_SECONDS = 40.0       # per motion: past this the planner stops trying directions too
MAX_SAMPLES = 2500       # per action: past this the planner stops trying directions and reports the best it found

# The film before this check: every part flew in from a point 220 mm out from the aircraft centre (render_build.py up
# to 2026-11-12, commit 5f3a032). Kept only to score it (--legacy).
LEGACY_STAGES = [
    ['WNG-001', 'WNG-002', 'WNG-004*', 'WNG-005*', 'FIN-004*', 'WNG-006*'],
    ['WNG-011*', 'WNG-012*', 'MEC-009*', 'MEC-010*'],
    ['FIN-002*', 'FIN-006*', 'FIN-001*', 'FIN-011*', 'FIN-012*', 'FIN-008*', 'FIN-009*', 'FIN-010*', 'FIN-007*'],
    ['POD-001', 'POD-002', 'POD-004', 'POD-005', 'POD-006', 'POD-007', 'POD-008', 'POD-010', 'POD-011', 'POD-012',
     'PWR-002', 'PWR-003', 'PWR-004', 'PWR-006', 'PWR-1*'],
    ['HRN-*', 'PWR-008*', 'WNG-003', 'WNG-020'],
    ['MEC-001*', 'MEC-002*', 'MEC-003*', 'MEC-004*', 'MEC-005*', 'MEC-006*', 'MEC-007*', 'MEC-008*', 'MEC-011*',
     'MEC-012*'],
    ['FIN-003*', 'FIN-1*', 'PRP-*'],
    ['AVN-*', 'POD-003'],
    ['GER-*'],
    ['PWR-001'],
]


# =====================================================================================================================
# inside Blender
# =====================================================================================================================
def bl_main(argv):
    import bpy
    from mathutils import Matrix, Vector
    from mathutils.bvhtree import BVHTree
    import collide_blender as cb

    a = argparse.ArgumentParser()
    a.add_argument('job')
    a.add_argument('out')
    a.add_argument('--steps', default='')
    a.add_argument('--legacy', action='store_true')
    a.add_argument('--tol-mm', type=float, default=TOL_MM)
    a = a.parse_args(argv)
    tol = a.tol_mm
    t_start = time.time()
    with open(a.job, encoding='utf-8') as f:
        job = json.load(f)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    col = bpy.data.collections.new('static')
    bpy.context.scene.collection.children.link(col)
    comps = {c['id']: c for c in job['comps']}
    info = ap.part_info()
    BONDED = ap.bonded_pairs()
    TRIMS = ap.tape_trims(info)

    def prep(b):
        if hasattr(b, 'V'):
            return
        b.V = [v.copy() for t in b.tris for v in t]
        b.F = [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(b.tris))]
        for c in b.cutters:
            prep(c)

    bodies = {}
    for pid, c in comps.items():
        bodies[pid] = cb.make_bodies(c, c['matrix'], col)
        for b in bodies[pid]:
            prep(b)
    wire_job = {w['id']: w for w in job['wires']}
    wb = {}
    for b in cb.make_wires(job['wires'], col):
        prep(b)
        wb.setdefault(b.pid, []).append(b)
    print('assembly: %d parts, %d wires meshed in %.0f s' % (len(bodies), len(wb), time.time() - t_start), flush=True)

    class Posed:
        """A Body moved by a world-mm 4x4 M (BVH rebuilt from the moved triangles); cutters follow lazily."""

        def __init__(self, base, M):
            self.base, self.M = base, M
            self.pid, self.idx, self.name = base.pid, base.idx, base.name
            for k in ('wire', 'r', 'ends', 'terms', 'inline'):
                if hasattr(base, k):
                    setattr(self, k, getattr(base, k))
            self.V = [M @ v for v in base.V]
            self.F = base.F
            self.bvh = BVHTree.FromPolygons(self.V, base.F, all_triangles=True)
            xs = [v.x for v in self.V]
            ys = [v.y for v in self.V]
            zs = [v.z for v in self.V]
            self.lo, self.hi = [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]
            self.probe = self.V[0]
            self.vol = base.vol
            self._t = self._c = None

        @property
        def tris(self):
            if self._t is None:
                V = self.V
                self._t = [(V[i], V[i + 1], V[i + 2]) for i in range(0, len(V), 3)]
            return self._t

        @property
        def cutters(self):
            if self._c is None:
                self._c = [Posed(c, self.M) for c in self.base.cutters]
            return self._c

    def ov_box(alo, ahi, b, pad=0.0):
        return all(alo[i] < b.hi[i] + pad and b.lo[i] < ahi[i] + pad for i in range(3))

    def union_box(bs):
        return ([min(b.lo[i] for b in bs) for i in range(3)], [max(b.hi[i] for b in bs) for i in range(3)])

    def eff_depth(p, body, d):
        """Depth of p in body's MATERIAL: the distance to the uncut surface, capped by the distance to the nearest of
        the body's cut faces (a seat, bore or hole). A point 0.05 mm past the wall of the pocket it is leaving is
        0.05 mm deep, not as deep as the pocket is from the outside (the gate's depth is the uncut one; it only meets
        points inside cuts, which it removes)."""
        for c in body.cutters:
            if all(c.lo[i] - d <= p[i] <= c.hi[i] + d for i in range(3)):
                loc, _n, _i, dc = c.bvh.find_nearest(p, d)
                if loc is not None and dc < d:
                    d = dc
        return d

    def pen_eff(m, o, pairs, early):
        """Deepest point of either surface in the other part's material (outside its cuts, outside the gate's wire
        exemptions): (depth, point) or None. early: return the first point deeper than tol."""
        best = None
        for src, dst, ids in ((m, o, {i for i, _j in pairs}), (o, m, {j for _i, j in pairs})):
            ids = sorted(ids)
            if early and len(ids) > PAIR_CAP:            # long sliding contacts: every k-th crossing triangle
                ids = ids[::len(ids) // PAIR_CAP + 1]
            for i in ids:
                for p in cb.tri_samples(src.tris[i]):
                    loc, nrm, _i, d = dst.bvh.find_nearest(p)
                    if loc is None or d <= tol or (p - loc).dot(nrm) >= 0:
                        continue
                    if best is not None and d <= best[0]:
                        continue
                    if cb.depth_inside(p, dst) <= tol or cb.removed(p, src) or cb.removed(p, dst)                             or cb.at_terminal(p, m, o):
                        continue
                    d = eff_depth(p, dst, d)
                    if d > tol and (best is None or d > best[0]):
                        best = (d, p)
                        if early:
                            return best
        return best

    def fast_pen(m, o, pairs):
        return pen_eff(m, o, pairs, True)

    def contained(m, o):
        """m wholly inside o with no surface crossing (collide_blender.check's second test)."""
        for x, y in ((m, o), (o, m)):
            if x.probe is not None and all(y.lo[i] <= x.lo[i] and x.hi[i] <= y.hi[i] for i in range(3)) \
                    and cb.depth_inside(x.probe, y) > tol and not cb.removed(x.probe, y) and not cb.removed(x.probe, x):
                return min(x.hi[i] - x.lo[i] for i in range(3)) / 2, x.probe
        return None

    def test_pose(movers, Ms, obst, exempt, collect=None):
        """Movers at world motions Ms (one per mover) against obstacles: first hit dict or None. With collect (a
        dict), every hit is recorded there as {(mover, blocker): deepest hit} and None is returned."""
        for b, M in zip(movers, Ms):
            cs = [M @ Vector((x, y, z)) for x in (b.lo[0], b.hi[0]) for y in (b.lo[1], b.hi[1])
                  for z in (b.lo[2], b.hi[2])]
            lo = [min(c[i] for c in cs) for i in range(3)]
            hi = [max(c[i] for c in cs) for i in range(3)]
            near = [o for o in obst if (b.pid, o.pid) not in exempt and ov_box(lo, hi, o)]
            if not near:
                continue
            p = Posed(b, M)
            for o in near:
                if not cb.boxes_overlap(p, o):
                    continue
                ov = p.bvh.overlap(o.bvh)
                r = fast_pen(p, o, ov) if ov else contained(p, o)
                if r:
                    deep, at = (pen_eff(p, o, ov, False) or r) if (ov and collect is None) else r
                    h = {'mover': b.pid, 'blocker': o.pid, 'mover_body': b.name, 'blocker_body': o.name,
                         'depth_mm': round(deep, 3), 'at_mm': [round(c, 1) for c in at]}
                    if collect is None:
                        return h
                    k = (b.pid, o.pid)
                    if k not in collect or h['depth_mm'] > collect[k]['depth_mm']:
                        collect[k] = h
        return None

    def rot_about(axis, origin, deg):
        o = Vector(origin)
        return Matrix.Translation(o) @ Matrix.Rotation(math.radians(deg), 4, Vector(axis)) @ Matrix.Translation(-o)

    def spin_Ms(movers, base_T, spin, d_from_final):
        """Per-body motion: base translation, plus the screw turn about each body's own axis line (non-round bodies
        only: a body of revolution turning about its own axis occupies the same space)."""
        if not spin:
            return [base_T] * len(movers)
        ang = 360.0 * SPIN_TURNS * min(1.0, d_from_final / THREAD_MM)
        out = []
        for b in movers:
            if getattr(b, 'round', False) or ang == 0:
                out.append(base_T)
            else:
                out.append(base_T @ rot_about(spin['axis'], b.centre, ang))
        return out

    def dists(a0, b0, step):
        out = [d for d in FINE if a0 < d < b0]
        d = max(a0, FINE[-1])
        while d + step < b0:
            d += step
            out.append(d)
        out.append(b0)
        return sorted(set(round(x, 4) for x in out if x > a0))

    def clear_dist(lo, hi, u, obst, exempt_ids=(), pad=CLEAR_PAD_MM):
        """First distance along u at which box [lo, hi], grown by pad, overlaps no obstacle box (slab test): where the
        part is free in the hand. Obstacles further along the line are never reached, so they do not count."""
        lo = [c - pad for c in lo]
        hi = [c + pad for c in hi]
        iv = []
        for o in obst:
            if o.pid in exempt_ids:
                continue
            t0, t1, ok = -1e18, 1e18, True
            for k in range(3):
                if abs(u[k]) < 1e-9:
                    if hi[k] <= o.lo[k] or lo[k] >= o.hi[k]:
                        ok = False
                        break
                else:
                    x1, x2 = (o.lo[k] - hi[k]) / u[k], (o.hi[k] - lo[k]) / u[k]
                    t0, t1 = max(t0, min(x1, x2)), min(t1, max(x1, x2))
            if ok and t0 < t1 and t1 > 0:
                iv.append((t0, t1))
        d = 0.0
        for t0, t1 in sorted(iv):
            if t0 > d:
                break
            d = max(d, t1)
        return d

    def extent(movers, u):
        lo, hi = union_box(movers)
        corners = [Vector((x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        pr = [c.dot(u) for c in corners]
        return max(pr) - min(pr)

    def sweep(movers, obst, u, P0, d0, d1, exempt, spin=None, spin_from=None):
        """Translate movers from P0 + u*d0 to P0 + u*d1 (mm), sampled; first hit with its distance, or None."""
        step = max(0.2, min(1.0, 0.5 * max(extent(movers, u), 0.4)))
        n = 0
        for d in dists(d0, d1, step):
            n += 1
            off = P0 + u * d
            T = Matrix.Translation(off)
            dd = (spin_from if spin_from is not None else 0.0) + d
            h = test_pose(movers, spin_Ms(movers, T, spin, dd), obst, exempt)
            if h:
                h['dist_mm'] = round((P0 + u * d).length, 2)
                return h, n
        return None, n

    def contacts(movers, obst):
        """Placed parts touching the movers: {part: smallest gap mm} for gaps up to BOND_GAP_MM (a vertex near a
        surface, or near the face of that part's cut it is seated in), and the mean outward normal of the faces
        within CONTACT_MM (the mount face normal; for a seated part the cut's faces, so it points out of the pocket)."""
        gaps, acc, n = {}, Vector(), 0
        for m in movers:
            V = m.V
            stride = max(1, len(V) // 1500)
            pts = V[::stride]
            for o in obst:
                if not ov_box(m.lo, m.hi, o, BOND_GAP_MM + 0.05):
                    continue
                g = gaps.get(o.pid, 1e9)
                for v in pts:
                    if not all(o.lo[i] - BOND_GAP_MM <= v[i] <= o.hi[i] + BOND_GAP_MM for i in range(3)):
                        continue
                    loc, nrm, _i, d = o.bvh.find_nearest(v, BOND_GAP_MM)
                    if loc is not None and not cb.removed(v, o):
                        g = min(g, d)
                        if d <= CONTACT_MM:
                            acc += nrm
                            n += 1
                        continue
                    for c in o.cutters:
                        if not all(c.lo[i] - BOND_GAP_MM <= v[i] <= c.hi[i] + BOND_GAP_MM for i in range(3)):
                            continue
                        loc, nrm, _i, d = c.bvh.find_nearest(v, BOND_GAP_MM)
                        if loc is not None:
                            g = min(g, d)
                            if d <= CONTACT_MM:
                                acc -= nrm
                                n += 1
                            break
                if g < 1e9:
                    gaps[o.pid] = g
        nrm = None
        if n and (acc / n).length > 0.3:
            nrm = (acc / n).normalized()
        return gaps, nrm

    def supported_by(ids, gaps):
        """Contact within CONTACT_MM, or a bond line up to BOND_GAP_MM where interfaces.json joins the two parts."""
        out = {}
        for pid, g in gaps.items():
            if g <= CONTACT_MM or any(frozenset((m, pid)) in BONDED for m in ids):
                out[pid] = round(g, 3)
        return out

    AX = {'X': Vector((1, 0, 0)), 'Y': Vector((0, 1, 0)), 'Z': Vector((0, 0, 1))}

    def tag_bodies(pid):
        """Body axis (world) and centre; round = a body of revolution (turning about its axis changes nothing)."""
        c = comps[pid]
        R = Matrix(c['matrix']).to_3x3()
        Mw = Matrix(c['matrix'])
        for b in bodies[pid]:
            s = c['bodies'][b.idx]
            ax = s.get('axis')
            v = AX.get(ax.upper()) if isinstance(ax, str) else (Vector(ax) if ax else None)
            b.axis = (R @ v).normalized() if v is not None else None
            b.round = s['kind'] == 'revolve'
            if s['kind'] == 'revolve':
                b.centre = (Mw @ Vector(s['center'])) * 1000.0
            else:
                b.centre = Vector([(b.lo[i] + b.hi[i]) / 2 for i in range(3)])

    for pid in bodies:
        tag_bodies(pid)

    def geo_axes(movers):
        w = []
        for b in movers:
            if b.axis is None:
                continue
            for i, (ax, wt) in enumerate(w):
                if abs(ax.dot(b.axis)) > 0.999:
                    w[i] = (ax, wt + b.vol)
                    break
            else:
                w.append((b.axis.copy(), b.vol))
        w.sort(key=lambda t: -t[1])
        return [ax for ax, _w in w]

    WORLD = [Vector(v) for v in ((0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0))]

    def candidates(ids, movers, obst, kind):
        ov = {}
        for pid in ids:
            ov.update(ap.override(pid))
        lo, hi = union_box(movers)
        ctr = (Vector(lo) + Vector(hi)) / 2
        gaps, nrm = contacts(movers, obst)
        touched = supported_by(ids, gaps)
        tb = [b for b in obst if b.pid in touched]
        sc = None
        if tb:
            slo, shi = union_box(tb)
            sc = (Vector(slo) + Vector(shi)) / 2
        out = []

        def add(v):
            v = Vector(v).normalized()
            if all(v.dot(x) < 0.99999 for x in out):
                out.append(v)

        for d in ov.get('dirs', []):
            add(d)
        axes = geo_axes(movers)
        big = max(movers, key=lambda b: b.vol) if movers else None
        if big is not None and big.round and big.axis is not None and kind != 'screw':
            for s in sorted((big.axis, -big.axis), key=lambda v: -(v.dot(ctr - sc) if sc else 0)):
                add(s)                                  # a tube, pin, plug or adapter goes on along its own axis
        if kind == 'screw':
            spun = [b.axis for b in movers if b.round and b.axis is not None]
            axes = (spun[:1] + axes) if spun else axes
            for ax in axes[:1]:
                for s in sorted((ax, -ax), key=lambda v: -(v.dot(ctr - sc) if sc else 0)):
                    add(s)
        if nrm is not None:
            add(nrm)
        for ax in axes + WORLD:
            pair = (ax, -ax)
            if sc is not None:
                pair = sorted(pair, key=lambda v: -v.dot(ctr - sc))
            elif nrm is not None:
                pair = sorted(pair, key=lambda v: -v.dot(nrm))
            for s in pair:
                add(s)
        return out, touched, nrm, ov

    def screw_clusters(movers):
        """Bodies of a screw / pin set grouped per fastener: round bodies on one axis line (head + shank) together."""
        out = []
        for b in movers:
            if not (b.round and b.axis is not None):
                return [movers]
            for c in out:
                a = c[0]
                d = b.centre - a.centre
                if abs(a.axis.dot(b.axis)) > 0.999 and (d - a.axis * d.dot(a.axis)).length < 0.6:
                    c.append(b)
                    break
            else:
                out.append([b])
        return out

    def plan_rigid(ids, movers, obst, kind, exempt):
        cand, touched, nrm, ov = candidates(ids, movers, obst, kind)
        spin = None
        if kind == 'screw':
            sp = [b.axis for b in movers if b.round and b.axis is not None]
            spin = {'axis': list(sp[0])} if sp else None
        lo, hi = union_box(movers)
        best_fail, tried, samples = None, 0, 0
        first_fail, attempts = None, []
        t_plan = time.time()
        for u in cand:
            if samples > MAX_SAMPLES or time.time() - t_plan > MAX_SECONDS:
                break
            tried += 1
            T = clear_dist(lo, hi, u, obst, {o for (_m, o) in exempt}) + MARGIN_MM
            if T > MAX_TRAVEL_MM:
                continue
            h, n = sweep(movers, obst, u, Vector(), 0.0, T, exempt, spin)
            samples += n
            if h is None:
                return dict(ok=True, dir=list(u), path=[list(u * T), [0, 0, 0]], travel_mm=round(T, 1),
                            spin=spin, tried=tried, samples=samples, touched=touched, mount_normal=nrm,
                            first_fail=first_fail, ov=ov)
            attempts.append({'dir': [round(c, 3) for c in u], 'blocker': h['blocker'], 'mover_body': h['mover_body'],
                             'blocker_body': h['blocker_body'], 'dist_mm': h['dist_mm'], 'depth_mm': h['depth_mm']})
            if first_fail is None:
                first_fail = dict(h, dir=[round(c, 3) for c in u])
            if best_fail is None or h['dist_mm'] > best_fail['dist_mm']:
                best_fail = dict(h, dir=[round(c, 3) for c in u])
            if h['dist_mm'] >= 3.0:                     # two segments: out short of the hit, then sideways
                P1 = u * (h['dist_mm'] - 1.0)
                lo1 = [lo[i] + P1[i] for i in range(3)]
                hi1 = [hi[i] + P1[i] for i in range(3)]
                blk_axes = geo_axes([o for o in obst if o.pid == h['blocker'] and getattr(o, 'axis', None) is not None])
                lat = []
                for e in [x for ax in blk_axes for x in (ax, -ax)] + WORLD + geo_axes(movers):
                    if abs(e.dot(u)) < 0.999 and all(e.dot(x) < 0.999 for x in lat):
                        lat.append(e)
                for e in lat:
                    T2 = clear_dist(lo1, hi1, e, obst, {o for (_m, o) in exempt}) + MARGIN_MM
                    if T2 > MAX_TRAVEL_MM:
                        continue
                    h2, n2 = sweep(movers, obst, e, P1, 0.0, T2, exempt, spin, spin_from=P1.length)
                    samples += n2
                    if h2 is None:
                        return dict(ok=True, dir=list(u), path=[list(P1 + e * T2), list(P1), [0, 0, 0]],
                                    travel_mm=round(P1.length + T2, 1), spin=spin, tried=tried, samples=samples,
                                    touched=touched, mount_normal=nrm, first_fail=first_fail, ov=ov)
        # nothing passes: keep the first (data-preferred) straight path and list everything it goes through
        u = cand[0]
        T = min(clear_dist(lo, hi, u, obst, {o for (_m, o) in exempt}) + MARGIN_MM, MAX_TRAVEL_MM)
        coll, firsts = {}, {}
        step = max(0.2, min(1.0, 0.5 * max(extent(movers, u), 0.4)), T / 60.0)
        for d in dists(0.0, T, step):
            test_pose(movers, spin_Ms(movers, Matrix.Translation(u * d), spin, d), obst, exempt, coll)
            for k, v in coll.items():
                firsts.setdefault(k, round(d, 2))
                if 'dist_mm' not in v:
                    v['dist_mm'] = round(d, 2)          # where along the path it is deepest
                v['first_mm'] = firsts[k]
            samples += 1
        hits = sorted(coll.values(), key=lambda h: -h['depth_mm'])
        return dict(ok=False, violation=hits[0] if hits else best_fail, hits=hits, attempts=attempts, tried=tried,
                    samples=samples,
                    touched=touched, mount_normal=nrm, first_fail=first_fail, ov=ov, path=[list(u * T), [0, 0, 0]],
                    travel_mm=round(T, 1), spin=spin, dir=list(u))

    # ---------------------------------------------------------------- the sequence
    acts, unnamed = ap.sequence(sorted(bodies), sorted(wb))
    only = set(s for s in a.steps.split(',') if s)
    placed, obst = [], []                          # aircraft: ids placed, their bodies
    bench = {}                                     # group -> [ids]
    lay_bodies = []                                # bodies of tapes laid so far
    results = []
    poses = {p['name']: p for p in job['poses']}
    swaps = []

    def place(ids):
        for pid in ids:
            placed.append(pid)
            obst.extend(bodies.get(pid) or wb.get(pid) or [])

    snaps, reordered, moved_once, k = [], set(), set(), 0
    while k < len(acts):
        act = acts[k]
        del snaps[k:]
        snaps.append((len(placed), len(obst), len(lay_bodies), {g: len(v) for g, v in bench.items()}))
        t0 = time.time()
        r = dict(i=k, stage=act['stage'], step=act['step'], caption=act['caption'], type=act['type'], id=act['id'],
                 group=act.get('group'))
        typ = act['type']
        run = not only or act['step'] in only
        if typ == 'swing':
            r.update(kind='swing', members=[])
            lim = [p for n, p in poses.items() if p.get('moved') and n.startswith('elevons at')]
            pick = None
            for p in lim:                              # the limit that raises the trailing edge (max x of a panel)
                pid = next((m for m in p['moved'] if m.startswith('WNG-011')), None)
                if not pid:
                    continue
                te = max((v for b in bodies[pid] for v in b.V), key=lambda v: v.x)
                R = Matrix(p['R'][pid])
                R.translation = R.translation * 1000.0
                if (R @ te).z > te.z:
                    pick = p
            members = [m for m in (pick['moved'] if pick else []) if m in placed]
            skip = set(pick.get('skip_with') or []) if pick else set()
            r['members'] = members
            r['not_swept_against'] = sorted(skip & set(placed))
            sw = {}
            for m in members:
                R = Matrix(pick['R'][m])
                q = R.to_quaternion()
                ax, ang = q.to_axis_angle()
                t = R.translation * 1000.0
                # origin on the axis: t = (I - R) o, o perpendicular to the axis
                o = 0.5 * (t + (1.0 / math.tan(ang / 2)) * ax.cross(t)) if abs(ang) > 1e-9 else Vector()
                sw[m] = {'axis': list(ax), 'origin_mm': list(o), 'deg': math.degrees(ang)}
            r['swing'] = sw
            if run and members:
                mv = [b for m in members for b in bodies[m]]
                fixed = [b for b in obst if b.pid not in members and b.pid not in skip]
                deg = max(abs(s['deg']) for s in sw.values())
                hit, n = None, 0
                for j in range(1, int(math.ceil(deg / SWING_STEP_DEG)) + 1):
                    f = min(1.0, j * SWING_STEP_DEG / deg)
                    Ms = [rot_about(sw[b.pid]['axis'], sw[b.pid]['origin_mm'], sw[b.pid]['deg'] * f) for b in mv]
                    n += 1
                    hit = test_pose(mv, Ms, fixed, set())
                    if hit:
                        hit['dist_mm'] = round(f * deg, 1)
                        break
                r.update(ok=hit is None, violation=hit, samples=n)
            else:
                r.update(ok=True, samples=0)
            r['support'], r['fixture'] = sorted(set(placed) & {'WNG-001'}), None
        elif typ == 'wire':
            w = wire_job[act['id']]
            r.update(kind='wire', members=[act['id']], ends=w['ends'], inline=w.get('inline', []))
            r['support'] = [e for e in w['ends'] if e in placed]
            r['loose_ends'] = [e for e in w['ends'] if e and e not in placed]
            bad = None
            if run:
                for sb in wb[act['id']]:
                    for lb in lay_bodies:
                        if not ov_box(sb.lo, sb.hi, lb, CONTACT_MM):
                            continue
                        for v in sb.V[::max(1, len(sb.V) // 3000)]:
                            loc, _n, _i, d = lb.bvh.find_nearest(v, CONTACT_MM)
                            if loc is not None and not cb.removed(v, lb):
                                bad = {'mover': act['id'], 'blocker': lb.pid, 'depth_mm': 0.0,
                                       'at_mm': [round(c, 1) for c in v], 'dist_mm': 0.0,
                                       'why': 'lead laid after the tape it lies against (it would run under or on '
                                              'the tape)'}
                                break
                        if bad:
                            break
                    if bad:
                        break
            r.update(ok=bad is None, violation=bad, samples=0, path=None)
            place([act['id']])
        else:
            ids = act['members'] if typ == 'install' else [act['id']]
            movers = [b for pid in ids for b in bodies[pid]]
            kind = 'install' if typ == 'install' else ap.kind_of(act['id'], info)
            r.update(kind=kind, members=ids)
            if typ == 'bench':
                g = act['group']
                mates = [b for pid in bench.get(g, []) for b in bodies[pid]]
                oset = mates
            else:
                oset = obst
            exempt = set()
            flex = {pid for pid in placed if ap.override(pid).get('flexible')}
            for pid in ids:
                for host in (ap.override(pid).get('cut_by') or {}):
                    for h2 in [h for h in placed if fnmatch.fnmatch(h, host)] or [host]:
                        exempt.add((pid, h2))
                for h2 in flex:                         # a strap is pushed aside, not passed through
                    exempt.add((pid, h2))
                for tape, guests in TRIMS.items():
                    if typ != 'bench' and tape in placed and (pid in guests or any(m in guests for m in ids)):
                        exempt.add((pid, tape))         # a sub-assembly passes the opening cut for its members
                        r.setdefault('tape_trimmed', []).append('%s round %s' % (tape, pid))
            if kind in ('lay', 'fill', 'fixture', 'clip', 'built'):
                touched = supported_by(ids, contacts(movers, oset)[0])
                ovr = ap.override(act['id'])
                r.update(ok=True, samples=0, path=[[0, 0, -40.0], [0, 0, 0]] if (kind == 'fixture' and not oset)
                         else [[0, 0, 0]], touched=touched, ov=ovr, spin=None, dir=None)
                if kind == 'lay' and 'tape' in (info.get(act['id'], {}).get('material') or '').lower():
                    lay_bodies.extend(movers)
            elif run and kind == 'screw' and len(screw_clusters(movers)) > 1:
                # a set of screws: each screw is driven on its own, one after another
                cl, done_b, res = screw_clusters(movers), [], []
                for c in cl:
                    x = plan_rigid(ids, c, oset + done_b, kind, exempt)
                    x['centre_mm'] = [round(v, 2) for v in c[0].centre]
                    x['path'] = [[round(v, 3) for v in q] for q in x['path']]
                    res.append(x)
                    done_b += c
                bad = [x for x in res if not x['ok']]
                gaps, _n = contacts(movers, oset)
                r.update(ok=not bad, violation=bad[0]['violation'] if bad else None,
                         hits=[h for x in bad for h in (x.get('hits') or [])],
                         attempts=[t for x in bad for t in (x.get('attempts') or [])],
                         samples=sum(x['samples'] for x in res), tried=sum(x['tried'] for x in res),
                         touched=supported_by(ids, gaps), ov=ap.override(act['id']), spin=res[0]['spin'],
                         path=res[0]['path'], dir=res[0].get('dir'), travel_mm=res[0].get('travel_mm'),
                         first_fail=next((x['first_fail'] for x in res if x.get('first_fail')), None),
                         clusters=[{'centre_mm': x['centre_mm'], 'path': x['path'], 'ok': x['ok'],
                                    'dir': [round(v, 4) for v in x['dir']] if x.get('dir') else None}
                                   for x in res])
                if not r['ok']:
                    hs = r.get('hits') or ([r['violation']] if r.get('violation') else [])
                    kn = [dict(h, **ap.known(h['mover'], h['blocker'])) for h in hs if ap.known(h['mover'], h['blocker'])]
                    if hs and len(kn) == len(hs):
                        r['known'] = kn
            elif run:
                r.update(plan_rigid(ids, movers, oset, kind, exempt))
                if not r.get('ok'):
                    hs = r.get('hits') or ([r['violation']] if r.get('violation') else [])
                    kn = [dict(h, **ap.known(h['mover'], h['blocker'])) for h in hs if ap.known(h['mover'], h['blocker'])]
                    if hs and len(kn) == len(hs):
                        r['known'] = kn
            else:
                touched = supported_by(ids, contacts(movers, oset)[0])
                r.update(ok=True, skipped=True, samples=0, touched=touched, ov={}, path=[[0, 0, 60.0], [0, 0, 0]],
                         spin=None, dir=None)
            touched = r.pop('touched')
            ovr = r.pop('ov') or {}
            r['support'] = sorted(touched)
            r['gaps_mm'] = touched
            r['fixture'] = None
            if not touched:
                if typ == 'bench' and not bench.get(act['group']):
                    r['fixture'] = ovr.get('fixture') or 'bench'
                elif ovr.get('fixture') and typ != 'bench':
                    r['fixture'] = ovr['fixture']
                elif ovr.get('fixture'):
                    r['fixture'] = ovr['fixture']
            r['unsupported'] = not touched and not r['fixture']
            r['cut_by'] = {p: ap.override(p).get('cut_by') for p in ids if ap.override(p).get('cut_by')}
            for key in ('mount_normal',):
                if r.get(key) is not None:
                    r[key] = [round(c, 3) for c in r[key]]
            if r.get('dir') is not None:
                r['dir'] = [round(c, 4) for c in r['dir']]
            if r.get('path'):
                r['path'] = [[round(c, 3) for c in p] for p in r['path']]
            blo, bhi = union_box(movers) if movers else ([0] * 3, [0] * 3)
            r['box_mm'] = [[round(c, 2) for c in blo], [round(c, 2) for c in bhi]]
            if typ == 'bench':
                bench.setdefault(act['group'], []).append(act['id'])
            else:
                place(ids)
        r['seconds'] = round(time.time() - t0, 1)
        print('%-5s %-8s %-14s %-8s %s %s%s  (%.1f s, %d samples)' % (
            r['step'], typ, r['id'][:14], r.get('kind', ''), 'ok ' if r.get('ok') else 'HIT',
            ('-> %s %.2f mm at %s mm out' % (r['violation']['blocker'], r['violation']['depth_mm'],
                                             r['violation'].get('dist_mm'))) if r.get('violation') else '',
            ('  UNSUPPORTED' if r.get('unsupported') else ''), r['seconds'], r.get('samples', 0)), flush=True)
        # order iteration: blocked by a part placed earlier in the SAME step (or bench group)? Put this action
        # before that part and re-plan from there (once per pair). The guide's step order is kept; only the order
        # inside a step changes, and the report lists every such swap.
        if run and not r.get('ok') and not r.get('known') and r.get('violation'):
            j, blk = None, None
            for cand_blk in [r['violation'].get('blocker')] + [t['blocker'] for t in r.get('attempts') or []]:
                j = next((x for x in range(k - 1, -1, -1) if acts[x]['step'] == act['step']
                          and cand_blk in (acts[x].get('members') or [acts[x]['id']])
                          and acts[x]['type'] in ('part', 'bench')
                          and (act['type'] != 'bench' or acts[x].get('group') == act.get('group'))), None)
                if j is not None and frozenset((act['id'], acts[j]['id'])) not in reordered:
                    blk = cand_blk
                    break
                j = None
            pair = frozenset((act['id'], acts[j]['id'])) if j is not None else None
            trial_ok = False
            if j is not None and pair not in reordered and act['id'] not in moved_once and typ in ('part', 'bench'):
                # try it first: does this part get in cleanly at the earlier position?
                n_p, n_o, n_l, nb = snaps[j]
                if typ == 'bench':
                    t_obst = [b for pid in bench.get(act['group'], [])[:nb.get(act['group'], 0)] for b in bodies[pid]]
                else:
                    t_obst = obst[:n_o]
                trial_ok = plan_rigid(ids, movers, t_obst, kind, exempt).get('ok', False)
                if trial_ok:                            # and the part it now goes before still gets in after it
                    b_ids = acts[j].get('members') or [acts[j]['id']]
                    b_mov = [b for pid in b_ids for b in bodies[pid]]
                    b_kind = ap.kind_of(acts[j]['id'], info)
                    if b_kind in ('slide', 'screw'):
                        trial_ok = plan_rigid(b_ids, b_mov, t_obst + movers, b_kind, set()).get('ok', False)
                reordered.add(pair)
                if not trial_ok:
                    print('      (putting %s before %s does not clear it either; order kept)'
                          % (act['id'], acts[j]['id']), flush=True)
            if trial_ok:
                moved_once.add(act['id'])
                n_p, n_o, n_l, nb = snaps[j]
                del placed[n_p:]
                del obst[n_o:]
                del lay_bodies[n_l:]
                for g in list(bench):
                    if g in nb:
                        del bench[g][nb[g]:]
                    else:
                        del bench[g]
                del results[j:]
                acts.insert(j, acts.pop(k))
                swaps.append({'step': act['step'], 'moved': act['id'], 'before': acts[j + 1]['id'], 'blocker': blk,
                              'depth_mm': r['violation']['depth_mm']})
                print('      reorder: %s goes before %s (it was blocked by %s); re-planning from there'
                      % (act['id'], acts[j + 1]['id'], blk), flush=True)
                k = j
                continue
        r['i'] = k
        results.append(r)
        with open(a.out + '.partial.jsonl', 'a', encoding='utf-8') as pf:
            pf.write(json.dumps(r, default=lambda o: list(o) if hasattr(o, '__iter__') else str(o)) + '\n')
        k += 1

    # ---------------------------------------------------------------- bench positions (from the install motion)
    for r in results:
        if r['type'] != 'install':
            continue
        g = r['id']
        mem = [x for x in results if x['type'] == 'bench' and x['group'] == g]
        start = Vector(r['path'][0])
        u = Vector(r['path'][0]) - Vector(r['path'][1])
        u = u.normalized() if u.length > 1e-9 else Vector((0, 0, -1))
        # bench swept box: members at final and along their own paths
        boxes = []
        for x in mem:
            lo, hi = union_box(bodies[x['id']])
            for p in x['path'] or [[0, 0, 0]]:
                boxes.append(([lo[i] + p[i] for i in range(3)], [hi[i] + p[i] for i in range(3)]))
        blo = [min(b[0][i] for b in boxes) for i in range(3)]
        bhi = [max(b[1][i] for b in boxes) for i in range(3)]
        i0 = min(x['i'] for x in mem)
        window = [x for x in results if i0 < x['i'] < r['i'] and x['type'] in ('part', 'install') and x.get('path')]
        extra = 0.0
        at_install = set()
        for x in results:
            if x['i'] < r['i'] and x['type'] in ('part', 'install', 'wire'):
                at_install.update(x['members'])
        abodies = [b for pid in at_install for b in (bodies.get(pid) or wb.get(pid) or [])]
        for _ in range(40):
            B = start + u * extra
            lo = [blo[i] + B[i] for i in range(3)]
            hi = [bhi[i] + B[i] for i in range(3)]
            clash = any(ov_box(lo, hi, b) for b in abodies)
            if not clash:
                for x in window:
                    for pid in x['members']:
                        plo, phi = union_box(bodies[pid])
                        for p in x['path']:
                            if all(lo[i] < phi[i] + p[i] and plo[i] + p[i] < hi[i] for i in range(3)):
                                clash = True
            if not clash:
                break
            extra += 25.0
        B = start + u * extra
        r['bench_mm'] = [round(c, 2) for c in B]
        r['path'] = [[round(c, 3) for c in B]] + r['path'] if extra > 0 else r['path']
        for x in mem:
            x['bench_mm'] = r['bench_mm']

    # ---------------------------------------------------------------- the old film, scored the same way (--legacy)
    legacy = None
    if a.legacy:
        allb = [b for bs in bodies.values() for b in bs]
        lo, hi = union_box(allb)
        centre = (Vector(lo) + Vector(hi)) / 2
        done, legacy = [], {'parts': 0, 'violating': 0, 'hits': []}
        for si, globs in enumerate(LEGACY_STAGES):
            stage_ids = [p for p in sorted(bodies) if any(fnmatch.fnmatch(p, g) for g in globs)
                         and not any(p in s for s in done)]
            ob_ = [b for s in done for pid in s for b in bodies[pid]]
            for pid in stage_ids:
                mv = bodies[pid]
                if not mv:
                    continue
                plo, phi = union_box(mv)
                c = (Vector(plo) + Vector(phi)) / 2
                size = (Vector(phi) - Vector(plo)).length
                if size > 500:
                    off = Vector((0, 0, -180.0)) if si <= 1 else Vector((0, 0, 120.0))
                else:
                    v = c - centre
                    v.z += 150 * (1 if c.z >= 0 else -1)
                    off = v.normalized() * 220.0
                L = off.length
                h, _n = sweep(mv, ob_, off / L, Vector(), 0.0, L, set())
                legacy['parts'] += 1
                if h:
                    legacy['violating'] += 1
                    legacy['hits'].append(dict(h, part=pid, stage=si + 2))
            done.append(stage_ids)
        print('legacy film: %d of %d parts pass through a part already placed' % (legacy['violating'],
                                                                                  legacy['parts']))

    rep = {'actions': results, 'unnamed': unnamed, 'swaps': swaps, 'tol_mm': tol, 'contact_mm': CONTACT_MM, 'legacy': legacy,
           'seconds': round(time.time() - t_start, 1), 'overrides': [[g, {k: v for k, v in row.items()}]
                                                                      for g, row in ap.OVERRIDES]}
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1, default=lambda o: list(o) if hasattr(o, '__iter__') else str(o))
    print('ASSEMBLY_DONE %.0f s' % (time.time() - t_start), flush=True)


# =====================================================================================================================
# driver (system Python, -I is fine)
# =====================================================================================================================
def write_md(rep, path, tol):
    acts = rep['actions']
    viol = [r for r in acts if not r.get('ok') and not r.get('known')]
    known = [r for r in acts if r.get('known')]
    uns = [r for r in acts if r.get('unsupported')]
    fix = [r for r in acts if r.get('fixture')]
    loose = [r for r in acts if r.get('loose_ends')]
    rigid = [r for r in acts if r.get('kind') in ('slide', 'screw', 'install')]
    two = [r for r in rigid if r.get('path') and len(r['path']) >= 3]
    first = [r for r in rigid if r.get('first_fail')]
    lg = rep.get('legacy')
    L = ['# Build sequence: swept-path physics check', '',
         'Generated by `showcase/animation/assembly_check.py` on %s from the collision gate\'s CAD job '
         '(`collision/collide.py --job-only`, stub-backend bodies and cuts, the drawn wires). Order: '
         '`assembly_plan.STEPS` = BUILD-GUIDE.md step by step. Penetration threshold %g mm (the gate\'s); contact '
         'within %g mm counts as support.' % (datetime.date.today().isoformat(), tol, rep['contact_mm']), '',
         '**%s.** %d actions (%d rigid motions, %d of them two-segment), %d unexplained swept-path violations, '
         '%d known open design blockers reproduced, %d unsupported placements, %d placements held by a fixture, %d '
         'wires with an end waiting for a later part. %.0f s.'
         % ('PASS' if not viol and not known else ('PASS except known open blockers' if not viol else 'FAIL'),
            len(acts), len(rigid), len(two), len(viol), len(known), len(uns), len(fix), len(loose),
            rep['seconds']), '']
    L += ['| Check | Result | Rule |', '|---|---|---|',
          '| Swept paths | %d violations | every moving part (or bench sub-assembly) sampled along its path; no '
          'point deeper than %g mm inside a part already placed, outside cut-away material |' % (len(viol), tol),
          '| Support | %d unsupported | each placed item touches something already placed, or a named fixture |'
          % len(uns),
          '| First-choice direction | %d of %d blocked | the first data-derived direction tried was blocked and the '
          'planner moved on (listed below) |' % (len(first), len(rigid)),
          '| Old fly-in film | %s | the same check on the pre-2026-11-12 film (parts fly in from 220 mm out) |'
          % ('%d of %d parts pass through a placed part' % (lg['violating'], lg['parts']) if lg else '— (run with --legacy)'),
          '']
    if viol:
        L += ['## Violations', '',
              'No direction and no two-segment path gets these parts in without passing more than %g mm into a part '
              'already placed (each tried direction is in assembly_check.json "attempts"). The film still shows '
              'them, on the data-preferred straight path, tinted like every moving part. "Reading" is a first '
              'diagnosis from the attempt log (assembly_plan.FINDINGS), not a verified cause.' % tol, '',
              '| Step | Action | Part | Blocked by (deepest) | Depth mm | mm out along the path | Reading |',
              '|---|---|---|---|---|---|---|']
        for r in viol:
            v = r.get('violation') or {}
            L.append('| %s | %s %s | %s | %s | %s | %s | %s |' % (
                r['step'], r['type'], r['id'], v.get('mover', '—'), v.get('blocker', '—'),
                '%.3f' % v['depth_mm'] if 'depth_mm' in v else '—', v.get('dist_mm', '—'),
                ap.note(ap.FINDINGS, r['id']) or '—'))
        L.append('')
    if known:
        L += ['## Known open blockers the check reproduces', '',
              'No motion gets these parts in: the planner tried every candidate direction and two-segment path. '
              'The film shows the intended motion from the guide; the rows are the parts it passes through. They clear '
              'when the named fix lands in CAD (then delete the row from `assembly_plan.KNOWN`).', '',
              '| Step | Action | Moving part (body) | Passes into (body) | Depth mm | First at mm out | Finding | Source |',
              '|---|---|---|---|---|---|---|---|']
        for r in known:
            for h in r['known']:
                L.append('| %s | %s %s | %s (%s) | %s (%s) | %.3f | %s | %s | %s |' % (
                    r['step'], r['type'], r['id'], h['mover'], h.get('mover_body', ''), h['blocker'],
                    h.get('blocker_body', ''), h['depth_mm'], h.get('dist_mm', '—'), h['finding'], h['why']))
        L.append('')
    if uns:
        L += ['## Unsupported placements', '', '| Step | Part | Why it floats |', '|---|---|---|']
        for r in uns:
            L.append('| %s | %s | %s |' % (r['step'], r['id'], ap.note(ap.SUPPORT_NOTES, r['id']) or
                                           'touches nothing placed before it and no fixture is named'))
        L.append('')
    L += ['## Fixtures and build-time cuts (assembly_plan.OVERRIDES)', '', '| Part glob | Fixture | Cut by | Source |',
          '|---|---|---|---|']
    for g, row in rep['overrides']:
        L.append('| %s | %s | %s | %s |' % (g, row.get('fixture', '—'),
                                             '; '.join('%s: %s' % kv for kv in (row.get('cut_by') or {}).items()) or '—',
                                             row.get('why', '—')))
    L.append('')
    L += ['## Order changes against BUILD-GUIDE.md', '', '| Guide steps | Change | Why (found by this check) |',
          '|---|---|---|'] + ['| %s | %s | %s |' % d for d in ap.DEVIATIONS] + ['']
    nsw = [r for r in acts if r.get('kind') in ('clip', 'built', 'lay', 'fill')]
    if nsw:
        L += ['## Placed, not swept (flexible or built in place)', '',
              '| Step | Part | Kind | Why | Support |', '|---|---|---|---|---|']
        for r in nsw:
            why = (ap.override(r['id']).get('why') or {'lay': 'tape / strap, laid in strips (flexible)',
                                                         'fill': 'wet epoxy, applied in place'}.get(r['kind'], '—'))
            L.append('| %s | %s | %s | %s | %s |' % (r['step'], r['id'], r['kind'], why,
                                                     ', '.join(r.get('support') or []) or r.get('fixture') or '—'))
        L.append('')
    tt = [(r['step'], t) for r in acts if r['type'] != 'bench' for t in (r.get('tape_trimmed') or [])]
    if tt:
        L += ['## Tape cut round a part as it goes in', '',
              'interfaces/seats.json says the tape is trimmed round these parts; the tape is cut with a blade on the '
              'bench (BUILD-GUIDE 6.5), so the part may pass the tape on its way in (the pair is not tested during '
              'that motion; the part is still tested against everything else).', '',
              ', '.join('%s (step %s)' % (t, st) for st, t in tt) + '.', '']
    if rep.get('swaps'):
        L += ['## Order changes inside a step (found by the check)', '',
              'The listed order in `assembly_plan.STEPS` was blocked; the planner put the part before the one that '
              'blocked it and re-planned. Consider writing the new order into the STEPS row.', '',
              '| Step | Moved | Now before | Was blocked by | Depth mm |', '|---|---|---|---|---|']
        for w in rep['swaps']:
            L.append('| %s | %s | %s | %s | %.3f |' % (w['step'], w['moved'], w['before'], w['blocker'],
                                                       w['depth_mm']))
        L.append('')
    if loose:
        L += ['## Wire ends waiting for a later part', '',
              'Laid along the route with that end parked (coiled or taped) until its part goes on.', '',
              '| Step | Wire | End not yet placed |', '|---|---|---|']
        for r in loose:
            L.append('| %s | %s | %s |' % (r['step'], r['id'], ', '.join(r['loose_ends'])))
        L.append('')
    if first:
        L += ['## First-choice direction blocked (planner tried the next one)', '',
              '| Step | Part | First direction | Blocked by | Depth mm | Used direction | Path segments |',
              '|---|---|---|---|---|---|---|']
        for r in first:
            f = r['first_fail']
            L.append('| %s | %s | %s | %s | %.3f | %s | %d |' % (
                r['step'], r['id'], ', '.join('%.2f' % c for c in f['dir']), f['blocker'], f['depth_mm'],
                ', '.join('%.2f' % c for c in r['dir']) if r.get('dir') else '—', len(r['path']) - 1))
        L.append('')
    if rep.get('unnamed'):
        L += ['## Parts no BUILD-GUIDE step names', '', ', '.join(rep['unnamed']) + '. Placed in a catch-all last step.',
              '']
    sw = [r for r in acts if r['type'] == 'swing']
    L += ['## Every action', '',
          'dir = the direction the part is REMOVED along (it arrives moving the opposite way), aircraft frame x aft, '
          'y right, z up. Support = parts it touches when placed.', '',
          '| # | Step | Action | Id | Kind | dir | Travel mm | Samples | Support / fixture | Result |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for r in acts:
        sup = ', '.join(r.get('support') or []) or (('fixture: ' + r['fixture']) if r.get('fixture') else '—')
        if r['type'] == 'wire' and r.get('loose_ends'):
            sup += ' (end parked: %s)' % ', '.join(r['loose_ends'])
        L.append('| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['i'], r['step'], r['type'], r['id'], r.get('kind', ''),
            ', '.join('%.2f' % c for c in r['dir']) if r.get('dir') else '—',
            r.get('travel_mm', '—'), r.get('samples', 0), sup if len(sup) < 90 else sup[:87] + '...',
            'ok' if r.get('ok') else 'FAIL'))
    L.append('')
    if sw:
        L += ['Elevon swing: panels and what is bonded to them turned about the gate\'s hinge joints (collision job '
              'poses) in %g° steps; not swept against (flexible / linkage, as in the gate): %s.'
              % (SWING_STEP_DEG, ', '.join(sw[0].get('not_swept_against') or []) or '—'), '']
    L += ['## What this check does not prove', '',
          '- The final pose of every part: that is the collision gate (`collision/collide.py`, `--glb`). This check '
          'starts 0.05 mm off the seat.',
          '- Tape, wet epoxy and wires are laid in place, not swept: flexible, so the swept-solid test does not apply. '
          'They get the support check and the "no lead laid after the tape it touches" rule.',
          '- Hands, tools and clearance for them (a hex key on a pinch bolt, a soldering iron): not modelled.',
          '- Gravity: no dynamics; a part counts as supported when it touches something placed or a named fixture.',
          '- Bench sub-assemblies are checked against their bench-mates only, then moved on as one body.',
          '- Real Fusion geometry (UNVERIFIED-IN-FUSION, as the gate).', '']
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))


def driver():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--blender', default=os.environ.get('BLENDER', BLENDER_DEFAULT))
    p.add_argument('--work', default=os.path.join(os.environ.get('TEMP', '/tmp'), 'k09l_assembly'))
    p.add_argument('--steps', default='', help='comma list of BUILD-GUIDE steps to check (others pass unchecked)')
    p.add_argument('--legacy', action='store_true', help='also score the old fly-in film with the same check')
    p.add_argument('--tol-mm', type=float, default=TOL_MM)
    p.add_argument('--report-only', action='store_true',
                   help='rewrite build/ASSEMBLY-CHECK.md from the last run in --work (no Blender)')
    a = p.parse_args()
    if a.report_only:
        with open(os.path.join(a.work, 'assembly_check.json'), encoding='utf-8') as f:
            rep = json.load(f)
        write_md(rep, os.path.join(OUT, 'ASSEMBLY-CHECK.md'), rep['tol_mm'])
        print('assembly: report rewritten from', os.path.join(a.work, 'assembly_check.json'))
        return
    os.makedirs(a.work, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    q = subprocess.run([sys.executable, '-I', os.path.join(COLL, 'collide.py'), '--job-only', '--out', a.work],
                       capture_output=True, text=True)
    if q.returncode != 0:
        sys.exit('assembly: collide.py --job-only failed:\n' + q.stdout + q.stderr)
    jp, rp = os.path.join(a.work, '_job.json'), os.path.join(a.work, 'assembly_check.json')
    for x in (rp, rp + '.partial.jsonl'):
        if os.path.exists(x):
            os.remove(x)
    cmd = [a.blender, '-b', '--factory-startup', '--python-exit-code', '1', '-P', os.path.abspath(__file__), '--',
           jp, rp, '--tol-mm', str(a.tol_mm)]
    if a.steps:
        cmd += ['--steps', a.steps]
    if a.legacy:
        cmd += ['--legacy']
    log = open(os.path.join(a.work, 'assembly_blender.log'), 'w', encoding='utf-8', buffering=1)
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace',
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    for line in pr.stdout:
        log.write(line)
        if not line.startswith(('Blender', 'Read', 'Warning')) and line.strip():
            print(line.rstrip(), flush=True)
    pr.wait()
    log.close()
    if pr.returncode != 0 or not os.path.exists(rp):
        sys.exit('assembly: Blender run failed (exit %s); see %s' % (pr.returncode, log.name))
    with open(rp, encoding='utf-8') as f:
        rep = json.load(f)
    plan = {'generated': datetime.date.today().isoformat(), 'units': 'mm, aircraft frame (x aft, y right, z up)',
            'tol_mm': rep['tol_mm'], 'actions': rep['actions']}
    with open(os.path.join(OUT, 'assembly_plan.json'), 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=1)
    write_md(rep, os.path.join(OUT, 'ASSEMBLY-CHECK.md'), rep['tol_mm'])
    viol = [r for r in rep['actions'] if not r.get('ok') and not r.get('known')]
    uns = [r for r in rep['actions'] if r.get('unsupported')]
    for r in rep['actions']:
        for h in r.get('known') or []:
            print('KNOWN BLOCKER %s, step %s %s %s: %s passes %.3f mm into %s (%s)' % (
                h['finding'], r['step'], r['type'], r['id'], h['mover'], h['depth_mm'], h['blocker'],
                h.get('blocker_body', '')), flush=True)
    for r in viol:
        v = r.get('violation') or {}
        print('VIOLATION step %s %s %s: %s passes %.3f mm into %s, %s mm out along its path, at %s' % (
            r['step'], r['type'], r['id'], v.get('mover'), v.get('depth_mm', 0), v.get('blocker'), v.get('dist_mm'),
            v.get('at_mm')), flush=True)
    for r in uns:
        print('UNSUPPORTED step %s %s: touches nothing placed and no fixture named' % (r['step'], r['id']))
    print('assembly: %s, %d actions, %d violations, %d unsupported, %.1f min; report %s' % (
        'PASS' if not viol else 'FAIL', len(rep['actions']), len(viol), len(uns), (time.time() - t0) / 60,
        os.path.relpath(os.path.join(OUT, 'ASSEMBLY-CHECK.md'), os.getcwd())))
    sys.exit(1 if viol else 0)


if __name__ == '__main__':
    try:
        import bpy  # noqa: F401
        IN_BLENDER = True
    except ImportError:
        IN_BLENDER = False
    if IN_BLENDER:
        bl_main(sys.argv[sys.argv.index('--') + 1:])
    else:
        driver()
