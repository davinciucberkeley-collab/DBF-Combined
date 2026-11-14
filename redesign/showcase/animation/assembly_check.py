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
SWING_STEP_DEG = 0.25
SPIN_TURNS = 3.0         # screw turns shown (and checked, for non-round bodies) over the thread length
THREAD_MM = 6.0
PAIR_CAP = 250           # crossing triangles sampled in full per body pair and pose; above this every crossing
#                          triangle is tested at its centroid and an even subset of PAIR_CAP in full (pen_eff.points)
MAX_SECONDS = 40.0       # per motion: past this the planner stops trying directions too
VERBOSE = bool(os.environ.get('ASSEMBLY_VERBOSE'))
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

    class Sub:
        """Part of a body: the triangles tri_ids of base (same part id, cutters and wire attributes). Used for the run
        of a wire held back until its end part is on (a parked tail), and for a hinge-tape strip split at the fold
        line (each half bonded to its own side)."""

        def __init__(self, base, tri_ids, tag):
            self.pid, self.idx, self.name = base.pid, base.idx, '%s %s' % (base.name, tag)
            for k in ('wire', 'r', 'ends', 'terms', 'inline', 'outs'):
                if hasattr(base, k):
                    setattr(self, k, getattr(base, k))
            self.V = [base.V[3 * i + j].copy() for i in tri_ids for j in range(3)]
            self.F = [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(tri_ids))]
            self.tris = [(self.V[i], self.V[i + 1], self.V[i + 2]) for i in range(0, len(self.V), 3)]
            self.bvh = BVHTree.FromPolygons(self.V, self.F, all_triangles=True)
            self.lo = [min(v[i] for v in self.V) for i in range(3)]
            self.hi = [max(v[i] for v in self.V) for i in range(3)]
            self.probe = self.V[0] if self.V else None
            self.vol = base.vol * len(tri_ids) / max(1, len(base.V) // 3)
            self.cutters = base.cutters
            self.axis, self.round = None, False
            self.centre = Vector([(self.lo[i] + self.hi[i]) / 2 for i in range(3)])
            self.open_surface = True                  # a piece of a closed body: no inside test (contained())

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

    def convex(c):
        """Cutter c is convex: every vertex on or behind every face plane (0.01 mm), computed once per cutter."""
        base = getattr(c, 'base', c)
        if not hasattr(base, 'is_convex'):
            import numpy as np
            V = np.array([tuple(v) for v in base.V], dtype=float)
            T = V.reshape(-1, 3, 3)
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
            ln = np.linalg.norm(n, axis=1)
            keep = ln > 1e-12
            n = n[keep] / ln[keep, None]
            d = np.einsum('ij,ij->i', n, T[keep, 0])
            planes = np.unique(np.round(np.c_[n, d], 3), axis=0)
            U = np.unique(np.round(V, 4), axis=0)
            ok_ = 0 < len(planes) <= 4000
            for k0 in range(0, len(planes) if ok_ else 0, 32):
                P = planes[k0:k0 + 32]
                if ((U @ P[:, :3].T - P[:, 3]) > 0.01).any():
                    ok_ = False
                    break
            base.is_convex = ok_
            base.planes = planes if ok_ else None
        return base.is_convex

    def cut_planes(c):
        """World face planes (n, d: n.x <= d inside) of a convex cutter c (moved with its part when posed), else None."""
        import numpy as np
        if not convex(c):
            return None
        P = getattr(c, 'base', c).planes
        M = getattr(c, 'M', None)
        if M is None:
            return P
        R = np.array([list(r) for r in M.to_3x3()])
        n = P[:, :3] @ R.T
        return np.c_[n, P[:, 3] + n @ np.array(list(M.translation))]

    def np_tris(body):
        """Triangle corners of a body as a (k, 3, 3) array, cached; a posed body maps its base's array."""
        import numpy as np
        if getattr(body, '_np', None) is None:
            base = getattr(body, 'base', None)
            if base is not None and getattr(body, 'M', None) is not None:
                R = np.array([list(r) for r in body.M.to_3x3()])
                body._np = np_tris(base) @ R.T + np.array(list(body.M.translation))
            else:
                body._np = np.array([tuple(v) for v in body.V], dtype=float).reshape(-1, 3, 3)
        return body._np

    STAT = {'cut': 0.0, 'n0': 0, 'n1': 0}
    import numpy as np
    GRID_W = np.array([(1.0 - u - v, u, v) for u, v in cb.GRID])     # the 15 barycentric samples of tri_samples

    def pen_eff(m, o, pairs, early):
        """Deepest point of either surface in the other part's material (outside its cuts, outside the gate's wire
        exemptions): (depth, point) or None. early: return the first point deeper than tol."""
        best = None

        def points(src, dst, ids):
            """Sample points of the crossing triangles: 15 per triangle (collide_blender.penetration's rule), minus the
            points inside a CONVEX cutter of dst or src (removed material; exact plane test, vectorised: a spar in its
            slot, a screw in its hole). For a long sliding contact in the early test (more than PAIR_CAP triangles
            with points left) the centroid of every such triangle, then all points of an even subset of PAIR_CAP."""
            import numpy as np
            if not ids:
                return
            T = np_tris(src)[ids]                                       # k, 3, 3
            P = np.einsum('gj,kjc->kgc', GRID_W, T)                     # k, 15, 3
            keep = np.ones(P.shape[:2], bool)
            flat = P.reshape(-1, 3)
            kf = keep.reshape(-1)
            tolc = cb.CUT_TOL_MM
            for body in (dst, src):
                for c in body.cutters:
                    lo, hi = np.array(c.lo) - tolc, np.array(c.hi) + tolc
                    inb = kf & ((flat >= lo) & (flat <= hi)).all(axis=1)
                    if not inb.any():
                        continue
                    PL = cut_planes(c)
                    if PL is None:
                        continue
                    sel = np.nonzero(inb)[0]
                    ins = ((flat[sel] @ PL[:, :3].T - PL[:, 3]) <= tolc).all(axis=1)
                    kf[sel[ins]] = False
            keep = kf.reshape(P.shape[:2])
            rows = np.nonzero(keep.any(axis=1))[0]
            STAT['n1'] += int(keep.sum())
            if early and len(rows) > PAIR_CAP:
                cen = T[rows].mean(axis=1)
                for q in cen:
                    yield Vector(q)
                rows = rows[::len(rows) // PAIR_CAP + 1]
            for r_ in rows:
                for q in P[r_][keep[r_]]:
                    yield Vector(q)

        for src, dst, ids in ((m, o, {i for i, _j in pairs}), (o, m, {j for _i, j in pairs})):
            STAT['n0'] += len(ids)
            t_c = time.time()
            pts = list(points(src, dst, sorted(ids)))
            STAT['cut'] += time.time() - t_c
            for i in (0,):
                for p in pts:
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
            if getattr(y, 'open_surface', False) or getattr(getattr(y, 'base', None), 'open_surface', False):
                continue
            if x.probe is not None and all(y.lo[i] <= x.lo[i] and x.hi[i] <= y.hi[i] for i in range(3)) \
                    and cb.depth_inside(x.probe, y) > tol and not cb.removed(x.probe, y) and not cb.removed(x.probe, x):
                return min(x.hi[i] - x.lo[i] for i in range(3)) / 2, x.probe
        return None

    CUR = {'allow': [], 'used': {}}               # elastic allowances of the action being planned (see elastic_rows)

    def allow_lim(b, o):
        """Elastic allowance for mover body b against blocker body o: the computed deflection limit (mm) when an
        assembly_plan.ELASTIC row names exactly this pair of bodies, else None."""
        for row in CUR['allow']:
            if fnmatch.fnmatch(b.pid, row['mover']) and fnmatch.fnmatch(b.name or '', row['mover_body'])                     and fnmatch.fnmatch(o.pid, row['blocker']) and fnmatch.fnmatch(o.name or '', row['blocker_body']):
                return row
        return None

    def test_pose(movers, Ms, obst, exempt, collect=None):
        """Movers at world motions Ms (one per mover) against obstacles: first hit dict or None. With collect (a
        dict), every hit is recorded there as {(mover, blocker): deepest hit} and None is returned. No pair is ever
        skipped by name; the only tolerance is an elastic row (allow_lim): the named flexing body may pass into the
        named body by at most the deflection its strain limit allows, and the deepest such pass is logged."""
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
                t_pair = time.time()
                ov = p.bvh.overlap(o.bvh)
                r = fast_pen(p, o, ov) if ov else contained(p, o)
                if VERBOSE and time.time() - t_pair > 0.5:
                    print('        slow pair %s/%s x %s/%s: %d crossings, %.1f s (point setup %.2f s, %d triangles, %d points left after cutters)' % (
                        b.pid, b.name, o.pid, o.name, len(ov), time.time() - t_pair, STAT['cut'], STAT['n0'],
                        STAT['n1']), flush=True)
                STAT.update(cut=0.0, n0=0, n1=0)
                if r and CUR['allow']:
                    row = allow_lim(b, o)
                    if row is not None:
                        deep = (pen_eff(p, o, ov, False) or r)[0] if ov else r[0]
                        if deep <= row['limit_mm']:
                            k_ = (row['id'], b.pid, b.name, o.pid, o.name)
                            CUR['used'][k_] = max(CUR['used'].get(k_, 0.0), deep)
                            continue
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

    def key_M(t, deg, rot):
        """World motion of a keyframe: rotate deg about the hinge line rot = (axis, origin), then translate t (mm)."""
        T = Matrix.Translation(Vector(t))
        return T @ rot_about(rot[0], rot[1], deg) if (rot and deg) else T

    def sweep_keys(movers, obst, rot, keys):
        """Keyframed motion, keys = [(t, deg), ...] from the start pose to the seated pose (last key (0, 0)):
        translation and hinge angle interpolated linearly between keys, sampled every 0.25 mm and 0.5 deg (finer
        than both the gate's tolerance on a 100 mm lever and the straight-path samples), seated end first.
        First hit (with 'key_seg' and 'deg') or None, and the sample count."""
        n = 0
        for i in range(len(keys) - 2, -1, -1):
            (t0, a0), (t1, a1) = keys[i], keys[i + 1]
            t0, t1 = Vector(t0), Vector(t1)
            m = max(1, int(math.ceil(max((t1 - t0).length / 0.25, abs(a1 - a0) / 0.5))))
            for j in range(m - 1, -1, -1):
                f = j / m
                t, a = t0.lerp(t1, f), a0 + (a1 - a0) * f
                n += 1
                h = test_pose(movers, [key_M(t, a, rot)] * len(movers), obst, set())
                if h:
                    h.update(dist_mm=round(t.length, 2), deg=round(a, 2), key_seg=i)
                    return h, n
        return None, n

    def in_place(movers, obst):
        """A wet, laid or cut-in-place item appears in its final pose: every pair it overlaps there (deepest hit per
        pair, the same test as a swept sample), [] when it lies clear of everything already placed."""
        coll = {}
        test_pose(movers, [Matrix.Identity(4)] * len(movers), obst, set(), coll)
        return sorted(coll.values(), key=lambda h: -h['depth_mm'])

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

    def plan_rigid(ids, movers, obst, kind, exempt, max_s=MAX_SECONDS):
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
            if samples > MAX_SAMPLES or time.time() - t_plan > max_s:
                break
            tried += 1
            T = clear_dist(lo, hi, u, obst, {o for (_m, o) in exempt}) + MARGIN_MM
            if T > MAX_TRAVEL_MM:
                continue
            t_dir = time.time()
            h, n = sweep(movers, obst, u, Vector(), 0.0, T, exempt, spin)
            samples += n
            if os.environ.get('ASSEMBLY_VERBOSE'):
                print('      dir %s travel %.0f mm: %s, %d samples, %.1f s' % (
                    ', '.join('%.2f' % c for c in u), T, 'clear' if h is None else 'hit %s %.2f mm at %s mm' % (
                        h['blocker'], h['depth_mm'], h['dist_mm']), n, time.time() - t_dir), flush=True)
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

    # ---------------------------------------------------------------- motions that are not one straight push
    def elastic_rows(mover_pids):
        """assembly_plan.ELASTIC rows for the moving parts, each with its deflection limit from the strain allowable:
        a cantilever finger of free length L and thickness t deflected d at its tip has a root strain
        eps = 3 t d / (2 L^2) (Roark, cantilever with an end load; the snap-fit formula of the Bayer/Covestro guide),
        so d_allow = 2 eps_allow L^2 / (3 t). The limit is the smaller of that and the row's geometric cap."""
        out = []
        for row in ap.ELASTIC:
            if not any(fnmatch.fnmatch(m, row['mover']) for m in mover_pids):
                continue
            d_allow = 2.0 * row['eps_allow'] * row['L_mm'] ** 2 / (3.0 * row['t_mm'])
            out.append(dict(row, limit_mm=min(d_allow, row.get('cap_mm', d_allow)), d_allow_mm=d_allow))
        return out

    def elastic_report(used):
        rows = {r_['id']: r_ for r_ in elastic_rows([k[1] for k in used])}
        out = []
        for (rid, mp, mb, bp, bb), d in sorted(used.items()):
            row = rows[rid]
            eps = 3.0 * row['t_mm'] * d / (2.0 * row['L_mm'] ** 2)
            out.append({'id': rid, 'mover': mp, 'mover_body': mb, 'blocker': bp, 'blocker_body': bb,
                        'deflection_mm': round(d, 3), 'strain_pct': round(100 * eps, 2),
                        'allow_pct': round(100 * row['eps_allow'], 2), 'limit_mm': round(row['limit_mm'], 3),
                        'L_mm': row['L_mm'], 't_mm': row['t_mm'], 'ok': eps <= row['eps_allow'] + 1e-9,
                        'source': row['source']})
        return out

    def boxdist(pt, b):
        return math.sqrt(sum(max(b.lo[i] - pt[i], 0.0, pt[i] - b.hi[i]) ** 2 for i in range(3)))

    def arclen(c, L, cum):
        best, sbest = 1e18, 0.0
        for i in range(len(L) - 1):
            ab = L[i + 1] - L[i]
            l2 = ab.length_squared
            t = 0.0 if l2 < 1e-12 else max(0.0, min(1.0, (c - L[i]).dot(ab) / l2))
            d = (L[i] + ab * t - c).length
            if d < best:
                best, sbest = d, cum[i] + t * math.sqrt(l2)
        return sbest

    def split_tail(wid, end):
        """The run of wire wid from its loose end (part `end`, not yet on) back to the middle of the first in-line
        connector met along the route (a JR pair, a splice sleeve): that run stays coiled off the aircraft until
        `end` is placed and is laid then ('tails' item). None when no connector lies on the route (then the whole
        lead waits). Per strand: the triangles of the tail, the Sub body, and the curve fraction."""
        w = wire_job[wid]
        inl_b = [b for i in w.get('inline', []) for b in bodies.get(i.split(':')[0], [])]
        if not inl_b or end not in bodies:
            return None
        eb = bodies[end]
        out = {'tail': [], 'tail_tris': {}, 'span': None, 'split_at': None}
        for sb in wb[wid]:
            line = [Vector(q) * 1000.0 for q in w['strands'][sb.idx][0]]
            rev = min(boxdist(line[-1], b) for b in eb) < min(boxdist(line[0], b) for b in eb)
            L = line[::-1] if rev else line
            cum = [0.0]
            for i in range(1, len(L)):
                cum.append(cum[-1] + (L[i] - L[i - 1]).length)
            tot = cum[-1]
            s_in = s_out = who = None
            sd, seg = 0.0, 0
            while sd <= tot:
                while seg < len(L) - 2 and cum[seg + 1] < sd:
                    seg += 1
                ls = cum[seg + 1] - cum[seg]
                pt = L[seg].lerp(L[seg + 1], (sd - cum[seg]) / ls if ls > 0 else 0.0)
                inside = next((b for b in inl_b if all(b.lo[k] <= pt[k] <= b.hi[k] for k in range(3))), None)
                if inside is not None and s_in is None:
                    s_in, who = sd, inside.pid
                if s_in is not None and (inside is None or inside.pid != who):
                    s_out = sd
                    break
                sd += 0.5
            if s_in is None:
                continue
            s_cut = (s_in + (s_out if s_out is not None else tot)) / 2.0
            tris = set()
            for i in range(len(sb.V) // 3):
                c = (sb.V[3 * i] + sb.V[3 * i + 1] + sb.V[3 * i + 2]) / 3.0
                if arclen(c, L, cum) <= s_cut:
                    tris.add(i)
            if not tris:
                continue
            out['tail_tris'][sb.idx] = tris
            out['tail'].append(Sub(sb, sorted(tris), '(run to %s)' % end))
            if out['span'] is None:
                f = s_cut / tot
                out['span'] = [round(1.0 - f, 4), 1.0] if rev else [0.0, round(f, 4)]
                out['split_at'] = who
        return out if out['tail'] else None

    def plan_built(ids, movers, obst):
        """A part glued up from flat pieces (the foam-board pod box): each body is its own rigid motion, planned and
        swept like any part against everything placed and the pieces already glued; the order is the CAD body order,
        and a piece that cannot go in yet waits for the next round (greedy). Pieces that never get in are listed."""
        remaining, done, res, samples, ok = list(movers), [], [], 0, True
        while remaining:
            pick = None
            for b in remaining:
                x = plan_rigid(ids, [b], obst + done, 'slide', set(), max_s=12.0)
                samples += x['samples']
                if x['ok']:
                    pick = (b, x)
                    break
            if pick is None:
                b = remaining[0]
                pick = (b, plan_rigid(ids, [b], obst + done, 'slide', set()))
                ok = False
            b, x = pick
            res.append({'idx': b.idx, 'name': b.name, 'ok': x['ok'], 'violation': x.get('violation'),
                        'path': [[round(c, 3) for c in q] for q in x['path']],
                        'dir': [round(c, 4) for c in x['dir']] if x.get('dir') else None,
                        'travel_mm': x.get('travel_mm'),
                        'box_mm': [[round(c, 2) for c in b.lo], [round(c, 2) for c in b.hi]]})
            done.append(b)
            remaining.remove(b)
            print('      built: %-28s %s %s' % (b.name[:28], 'ok ' if x['ok'] else 'HIT',
                                                   ', '.join('%.2f' % c for c in (x.get('dir') or []))), flush=True)
        gaps, _n = contacts(movers, obst)
        return dict(ok=ok, violation=next((q['violation'] for q in res if not q['ok']), None), samples=samples,
                    touched=supported_by(ids, gaps), ov=ap.override(ids[0]), path=[[0, 0, 0]], spin=None, dir=None,
                    built=res, motion='built body by body')

    def plan_hinge(ids, movers, obst, spec):
        """A part hooked under a lip and swung down onto its seat (the hatch): the hinge line is the lip's free
        edge on its underside (from the geometry of the named lip body, along its long side). The part comes in
        open at angle th from above, slides along its own plane until its tongue is under the lip, then turns
        about the hinge line to closed. Every pose is tested (sweep_keys). Opening angles are tried in the order
        the row gives; the first that passes is the motion."""
        tongue = next(b for b in movers if fnmatch.fnmatch(b.name or '', spec['body']))
        lip = next(o for o in obst if o.pid == spec['host'] and fnmatch.fnmatch(o.name or '', spec['host_body']))
        ext = [lip.hi[i] - lip.lo[i] for i in range(2)]
        ai = 0 if ext[0] > ext[1] else 1
        j = 1 - ai
        axis = Vector((0, 0, 0))
        axis[ai] = 1.0
        mlo, mhi = union_box(movers)
        mc = (Vector(mlo) + Vector(mhi)) / 2
        lc = (Vector(lip.lo) + Vector(lip.hi)) / 2
        out_sgn = 1.0 if mc[j] > lc[j] else -1.0
        origin = Vector(lc)
        origin[j] = lip.hi[j] if out_sgn > 0 else lip.lo[j]
        origin[2] = lip.lo[2]
        d = Vector((0, 0, 0))
        d[j] = out_sgn
        far = max((v for b in movers for v in b.V), key=lambda v: (v - origin).dot(d))
        sg = 1.0 if (rot_about(axis, origin, 10.0) @ far).z > far.z else -1.0
        engage = max(0.0, (origin - Vector(tongue.lo if out_sgn > 0 else tongue.hi)).dot(d))
        n_all, tried = 0, []
        for th in spec['angles']:
            R = rot_about(axis, origin, sg * th).to_3x3()
            sdir = R @ d
            t1 = sdir * (engage + spec.get('clear_mm', 2.0))
            t0 = t1 + Vector((0, 0, spec.get('lift_mm', 40.0)))
            keys = [(list(t0), sg * th), (list(t1), sg * th), ([0, 0, 0], sg * th), ([0, 0, 0], 0.0)]
            h, n = sweep_keys(movers, obst, (axis, origin), keys)
            n_all += n
            tried.append({'deg': th, 'hit': h})
            if h is None:
                break
        gaps, _n = contacts(movers, obst)
        rot = {'axis': [round(c, 6) for c in axis], 'origin_mm': [round(c, 3) for c in origin]}
        return dict(ok=h is None, violation=h, samples=n_all, touched=supported_by(ids, gaps),
                    ov=ap.override(ids[0]), spin=None, dir=[round(c, 4) for c in sdir], rot=rot,
                    keys=[[[round(c, 3) for c in t], round(a, 3)] for t, a in keys],
                    path=[[round(c, 3) for c in Vector(t)] for t, _a in keys[:3]],
                    travel_mm=round(Vector(keys[0][0]).length, 1), open_deg=th, engage_mm=round(engage, 2),
                    hinge_tried=tried, motion='hooked under the lip, then turned %g deg about the hinge line' % th)

    # ---------------------------------------------------------------- the sequence
    acts, unnamed = ap.sequence(sorted(bodies), sorted(wb))
    only = set(s for s in a.steps.split(',') if s)
    placed, obst = [], []                          # aircraft: ids placed, their bodies
    bench = {}                                     # group -> [ids]
    lay_bodies = []                                # bodies of tapes laid so far
    results = []
    poses = {p['name']: p for p in job['poses']}
    swaps = []

    made_in = {}                                   # id(solder-joint body) -> the build step it is made at
    pending_tails, tails_done, wire_span = [], [], {}   # held wire runs, laid ones, curve span of each wire

    def place(ids):
        for pid in ids:
            placed.append(pid)
            bs = bodies.get(pid) or wb.get(pid) or []
            obst.extend(bs)
            for b in bs:
                if 'solder joint' in (b.name or ''):
                    made_in[id(b)] = act['step']

    def step_obst(step):
        """Obstacles for a part moved in `step`: a solder joint is made with the iron at the end of the step its part
        is placed in (after the screws that hold the part; BUILD-GUIDE order), so it is not yet there for the other
        parts of that same step (D-89c). From the next step on it is an obstacle like any body."""
        return [o for o in obst if made_in.get(id(o)) != step]

    snaps, reordered, moved_once, k = [], set(), set(), 0
    while k < len(acts):
        act = acts[k]
        del snaps[k:]
        snaps.append((len(placed), len(obst), len(lay_bodies), {g: len(v) for g, v in bench.items()},
                      len(pending_tails), len(tails_done)))
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
            # the hinge tape (gate: skip_with) is not skipped: each strip is split at the hinge line, the half on a
            # panel's side turns with that panel (it is bonded to it), the other half stays on the core; the film
            # folds along the line between them (a tape hinge, BUILD-GUIDE 7.1)
            tape_split, tape_mov, tape_fix = {}, [], []
            pans = [m for m in members if m.startswith(('WNG-011', 'WNG-012'))]
            for tp in sorted(skip & set(placed)):
                for tb in [o for o in obst if o.pid == tp]:
                    pan = max(pans, key=lambda m: min(tb.hi[1], max(v.hi[1] for v in bodies[m]))
                              - max(tb.lo[1], min(v.lo[1] for v in bodies[m])), default=None)
                    if pan is None:
                        tape_fix.append(tb)
                        continue
                    ax_, o_ = Vector(sw[pan]['axis']), Vector(sw[pan]['origin_mm'])
                    plo, phi = union_box(bodies[pan])
                    pc = (Vector(plo) + Vector(phi)) / 2 - o_
                    pc -= ax_ * pc.dot(ax_)
                    side = [i for i in range(len(tb.V) // 3)
                            if ((((tb.V[3 * i] + tb.V[3 * i + 1] + tb.V[3 * i + 2]) / 3 - o_)) -
                                ax_ * (((tb.V[3 * i] + tb.V[3 * i + 1] + tb.V[3 * i + 2]) / 3 - o_).dot(ax_))).dot(pc) > 0]
                    rest = sorted(set(range(len(tb.V) // 3)) - set(side))
                    if side:
                        sb_ = Sub(tb, side, '(on %s)' % pan)
                        sb_.swing_with = pan
                        tape_mov.append(sb_)
                    if rest:
                        tape_fix.append(Sub(tb, rest, '(on the core)'))
                    tape_split.setdefault(tp, []).append({'body': tb.name, 'panel': pan, 'tris_on_panel': len(side),
                                                          'tris_on_core': len(rest)})
            r['tape_split'] = tape_split
            r['not_swept_against'] = []
            if run and members:
                mv = [b for m in members for b in bodies[m]] + tape_mov
                fixed = [b for b in obst if b.pid not in members and b.pid not in skip] + tape_fix
                deg = max(abs(s['deg']) for s in sw.values())
                hit, n = None, 0
                for j in range(1, int(math.ceil(deg / SWING_STEP_DEG)) + 1):
                    f = min(1.0, j * SWING_STEP_DEG / deg)
                    Ms = [rot_about(sw[getattr(b, 'swing_with', b.pid)]['axis'],
                                    sw[getattr(b, 'swing_with', b.pid)]['origin_mm'],
                                    sw[getattr(b, 'swing_with', b.pid)]['deg'] * f) for b in mv]
                    n += 1
                    hit = test_pose(mv, Ms, fixed, set())
                    if hit:
                        hit['dist_mm'] = round(f * deg, 1)
                        break
                r.update(ok=hit is None, violation=hit, samples=n)
            else:
                r.update(ok=True, samples=0)
            r['support'], r['fixture'] = sorted(set(placed) & {'WNG-001'}), None
        elif typ in ('wire', 'tails'):
            if typ == 'wire':
                wid = act['id']
                w = wire_job[wid]
                loose = [e for e in w['ends'] if e and e not in placed]
                held = []
                for e in loose:                         # the run from a loose end to its first in-line connector
                    sp = split_tail(wid, e)             # waits, coiled off the aircraft, until its part is on
                    if sp:
                        held.append((e, sp))
                lay_b = []
                for sb in wb[wid]:
                    drop = set()
                    for _e, sp in held:
                        drop |= sp['tail_tris'].get(sb.idx, set())
                    if not drop:
                        lay_b.append(sb)
                        continue
                    keep = [i for i in range(len(sb.V) // 3) if i not in drop]
                    if keep:
                        lay_b.append(Sub(sb, keep, '(laid run)'))
                for e, sp in held:
                    pending_tails.append(dict(wire=wid, end=e, bodies=sp['tail'], span=sp['span']))
                span = [0.0, 1.0]
                for e, sp in held:
                    lo_, hi_ = sp['span']
                    if lo_ <= 0.0:
                        span[0] = max(span[0], hi_)
                    else:
                        span[1] = min(span[1], lo_)
                r.update(kind='wire', members=[wid], ends=w['ends'], inline=w.get('inline', []), span=span,
                         held_tails=[{'end': e, 'span': sp['span'], 'split_at': sp['split_at']} for e, sp in held])
                r['support'] = [e for e in w['ends'] if e in placed]
                r['loose_ends'] = [e for e in loose if e not in [h[0] for h in held]]
            else:
                todo = [t for t in pending_tails if t['end'] in placed and fnmatch.fnmatch(t['wire'], act['id'])
                        and id(t) not in tails_done]
                lay_b = [x for t in todo for x in t['bodies']]
                spans = {}
                for t in todo:                          # the curve grows from its laid run out to the end
                    prev = (spans.get(t['wire']) or {}).get('to') or wire_span.get(t['wire'], [0.0, 1.0])
                    lo_, hi_ = t['span']
                    new = [min(prev[0], lo_), max(prev[1], hi_)]
                    spans[t['wire']] = {'from': (spans.get(t['wire']) or {}).get('from') or prev, 'to': new,
                                        'end': t['end']}
                    wire_span[t['wire']] = new
                    tails_done.append(id(t))
                r.update(kind='wire', type='wire', members=sorted(spans), tails=spans,
                         id=', '.join(sorted(spans)) or act['id'], tail_action=True)
                r['support'] = sorted({t['end'] for t in todo})
                r['loose_ends'] = []
            bad = None
            hits = in_place(lay_b, step_obst(act['step'])) if (run and lay_b) else []
            if hits:
                bad = dict(hits[0], why='lead lies in a part already placed')
            if run and not bad:
                for sb in lay_b:
                    for lb in lay_bodies:
                        if not ov_box(sb.lo, sb.hi, lb, CONTACT_MM):
                            continue
                        for v in sb.V[::max(1, len(sb.V) // 3000)]:
                            loc, _n, _i, d = lb.bvh.find_nearest(v, CONTACT_MM)
                            if loc is not None and not cb.removed(v, lb):
                                bad = {'mover': sb.pid, 'blocker': lb.pid, 'depth_mm': 0.0,
                                       'at_mm': [round(c, 1) for c in v], 'dist_mm': 0.0,
                                       'why': 'lead laid after the tape it lies against (it would run under or on '
                                              'the tape)'}
                                break
                        if bad:
                            break
                    if bad:
                        break
            r.update(ok=bad is None, violation=bad, samples=1 if lay_b else 0, path=None, motion='laid in place')
            if typ == 'wire':
                wire_span[wid] = r['span']
                placed.append(wid)
            obst.extend(lay_b)
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
                oset = step_obst(act['step'])
            exempt = set()                              # no pair is ever skipped by name
            CUR['allow'] = elastic_rows([b.pid for b in movers])
            CUR['used'] = {}
            if kind in ('lay', 'fill', 'fixture'):
                # laid, wet or cut in place: no motion through anything; it must appear clear of what is placed
                hits = in_place(movers, oset) if run else []
                touched = supported_by(ids, contacts(movers, oset)[0])
                r.update(ok=not hits, violation=hits[0] if hits else None, hits=hits, samples=1, path=[[0, 0, 0]],
                         touched=touched, ov=ap.override(act['id']), spin=None, dir=None,
                         motion={'lay': 'laid in place (wiped on in strips)', 'fill': 'applied in place (wet)',
                                 'fixture': 'cut in place in its fixture'}[kind])
                if kind == 'lay' and 'tape' in (info.get(act['id'], {}).get('material') or '').lower():
                    lay_bodies.extend(movers)
            elif run and kind == 'built':
                r.update(plan_built(ids, movers, oset))
            elif run and kind == 'hinge':
                r.update(plan_hinge(ids, movers, oset, ap.override(act['id'])['hinge']))
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
            if CUR['used']:
                r['elastic'] = elastic_report(CUR['used'])
            CUR['allow'], CUR['used'] = [], {}
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
                n_p, n_o, n_l, nb, _pt, _td = snaps[j]
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
                n_p, n_o, n_l, nb, n_pt, n_td = snaps[j]
                del placed[n_p:]
                del pending_tails[n_pt:]
                del tails_done[n_td:]
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

    # ---------------------------------------------------------------- bowing the brace in: the strain it would take
    bow = None
    B = getattr(ap, 'BOW', None)
    if B and B['part'] in comps:
        secs = comps[B['part']]['bodies'][0]['sections']
        cs = [Vector((sum(q[0] for q in lp) / len(lp), y, sum(q[1] for q in lp) / len(lp))) * 1000.0 for y, lp in secs]
        Lb = (cs[-1] - cs[0]).length
        Lf = Lb - 2 * B['embed_mm']
        D = B['embed_mm'] + B['clear_mm']
        amp = 2.0 / math.pi * math.sqrt(Lf * D)       # clamped-clamped first mode, chord shortening D = pi^2 a^2 / (4 L)
        eps = math.pi ** 2 * amp * B['t_mm'] / Lf ** 2  # max curvature 2 pi^2 a / L^2 times t / 2
        bow = dict(part=B['part'], length_mm=round(Lb, 1), free_mm=round(Lf, 1), shorten_mm=D, bow_mm=round(amp, 1),
                   strain_pct=round(100 * eps, 2), ult_pct=round(100 * B['eps_ult'], 2), ok=eps <= B['eps_ult'],
                   source=B['source'])
    rep = {'actions': results, 'unnamed': unnamed, 'swaps': swaps, 'tol_mm': tol, 'contact_mm': CONTACT_MM, 'legacy': legacy,
           'seconds': round(time.time() - t_start, 1), 'bow': bow,
           'elastic_rows': [{k: v for k, v in row.items()} for row in ap.ELASTIC],
           'overrides': [[g, {k: v for k, v in row.items()}] for g, row in ap.OVERRIDES]}
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1, default=lambda o: list(o) if hasattr(o, '__iter__') else str(o))
    print('ASSEMBLY_DONE %.0f s' % (time.time() - t_start), flush=True)


# =====================================================================================================================
# driver (system Python, -I is fine)
# =====================================================================================================================
def how(r):
    """One plain phrase for how an action was checked."""
    k, t = r.get('kind'), r['type']
    if t == 'swing':
        return 'rotated about the hinge joints'
    if k == 'wire':
        return 'held run laid in place' if r.get('tail_action') else 'laid in place'
    if k == 'hinge':
        return 'slid, then rotated about the lip edge'
    if k == 'built':
        return 'built body by body (%d pieces swept)' % len(r.get('built') or [])
    if k in ('lay', 'fill', 'fixture'):
        return {'lay': 'laid in place', 'fill': 'applied in place (wet)', 'fixture': 'cut in place'}[k]
    seg = len(r.get('path') or []) - 1
    s = 'swept, %s' % ('two segments' if seg >= 2 else 'straight')
    if k == 'screw':
        s += ', turning'
    if r.get('elastic'):
        s += ', elastically checked'
    if r.get('skipped'):
        s = 'not checked this run (--steps)'
    return s


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
    rot = [r for r in acts if r.get('kind') in ('hinge', 'swing')]
    built = [r for r in acts if r.get('kind') == 'built']
    ela = [e for r in acts for e in (r.get('elastic') or [])]
    inpl = [r for r in acts if r.get('kind') in ('lay', 'fill', 'fixture')]
    wires = [r for r in acts if r.get('kind') == 'wire']
    skipped = [r for r in acts if r.get('skipped')]
    lg = rep.get('legacy')
    L = ['# Build sequence: swept-path physics check', '',
         'Generated by `showcase/animation/assembly_check.py` on %s from the collision gate\'s CAD job '
         '(`collision/collide.py --job-only`, stub-backend bodies and cuts, the drawn wires). Order: '
         '`assembly_plan.STEPS` = BUILD-GUIDE.md step by step. Penetration threshold %g mm (the gate\'s); contact '
         'within %g mm counts as support.' % (datetime.date.today().isoformat(), tol, rep['contact_mm']), '',
         '**%s.** %d actions, %d violations, %d exempted part pairs, %d unsupported placements. %.0f s.%s'
         % ('PASS' if not viol and not known else ('PASS except known open blockers' if not viol else 'FAIL'),
            len(acts), len(viol), 0, len(uns), rep['seconds'],
            (' Partial run: %d actions not checked (--steps).' % len(skipped)) if skipped else ''), '',
         'No pair of parts is exempted from the test by name. Every action is one of these, and the film '
         '(`render_build.py`) animates exactly that motion:', '',
         '| How it was checked | Actions | What was tested |', '|---|---|---|',
         '| Swept, straight or two-segment (rigid parts, screws turning, bench sub-assemblies) | %d (%d two-segment) | '
         'the part re-meshed at every sample along its path and tested against every body already placed |'
         % (len(rigid), len(two)),
         '| Rotated | %d | the hatch: slid under the nose lip, then turned about the lip edge (every 0.5 deg); the '
         'elevon swing about the gate\'s hinge joints (every %g deg), the hinge-tape half on each panel turning with it |'
         % (len(rot), SWING_STEP_DEG),
         '| Built body by body | %d part, %d pieces | each foam-board piece of the pod box swept on its own path '
         'against the tray, the inserts and the pieces already glued |' % (len(built), sum(len(r.get('built') or [])
                                                                                          for r in built)),
         '| Elastically checked | %d body pairs | interference allowed only between the named flexing body and the '
         'body it rides over, only up to the deflection its strain limit gives (table below) |' % len(ela),
         '| Laid, wet or cut in place | %d | no motion: the item appears where it lies (film: wiped on) and is tested '
         'there against every body already placed |' % len(inpl),
         '| Wires laid along their route | %d | tested in place against every body placed; a lead whose end part '
         'is not on yet is laid to its first connector and its held run laid when that part is on |' % len(wires), '']
    L += ['| Check | Result | Rule |', '|---|---|---|',
          '| Swept paths and in-place items | %d violations | no point deeper than %g mm inside a part already placed, '
          'outside cut-away material |' % (len(viol), tol),
          '| Support | %d unsupported | each placed item touches something already placed, or a named fixture |'
          % len(uns),
          '| First-choice direction | %d of %d blocked | the first data-derived direction tried was blocked and the '
          'planner moved on (listed below) |' % (len(first), len(rigid)),
          '| Old fly-in film | %s | the same check on the pre-2026-11-12 film (parts fly in from 220 mm out) |'
          % ('%d of %d parts pass through a placed part' % (lg['violating'], lg['parts']) if lg else '— (run with --legacy)'),
          '']
    if viol:
        L += ['## Violations', '',
              'Nothing gets these parts in without passing more than %g mm into a part already placed. Each is a '
              'genuine blocker for the CAD owner; "Reading" is a first diagnosis (assembly_plan.FINDINGS), not a '
              'verified cause.' % tol, '',
              '| Step | Action | Mover | Blocked by (body) | Depth mm | mm out along the path | Reading |',
              '|---|---|---|---|---|---|---|']
        for r in viol:
            v = r.get('violation') or {}
            L.append('| %s | %s %s | %s (%s) | %s (%s) | %s | %s | %s |' % (
                r['step'], r['type'], r['id'], v.get('mover', '—'), v.get('mover_body', '—'), v.get('blocker', '—'),
                v.get('blocker_body', '—'), '%.3f' % v['depth_mm'] if 'depth_mm' in v else '—',
                v.get('dist_mm', '—'), v.get('why') or ap.note(ap.FINDINGS, r['id']) or '—'))
        L.append('')
    if known:
        L += ['## Known open blockers the check reproduces', '',
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
    if ela:
        L += ['## Elastic checks', '',
              'A flexing feature may pass into the body it rides over only by the deflection its strain limit allows: '
              'cantilever finger of free length L and thickness t, tip deflection d, root strain eps = 3 t d / (2 L^2) '
              '(Roark, end-loaded cantilever; the snap-fit relation of the Bayer / Covestro snap-fit guide). d is the '
              'deepest interference the sweep measured between exactly these two bodies (assembly_plan.ELASTIC). EST: '
              'stand-in geometry, print-dependent allowable.', '',
              '| Step | Action | Flexing body | Rides over | d mm | L x t mm | Strain % | Allowable % | Limit mm | OK | Source |',
              '|---|---|---|---|---|---|---|---|---|---|---|']
        for r in acts:
            for e in r.get('elastic') or []:
                L.append('| %s | %s %s | %s (%s) | %s (%s) | %.3f | %g x %g | %.2f | %.2f | %.3f | %s | %s |' % (
                    r['step'], r['type'], r['id'], e['mover'], e['mover_body'], e['blocker'], e['blocker_body'],
                    e['deflection_mm'], e['L_mm'], e['t_mm'], e['strain_pct'], e['allow_pct'], e['limit_mm'],
                    'yes' if e['ok'] else '**no**', e['source']))
        L.append('')
    bow = rep.get('bow')
    if bow:
        L += ['## Why the brace is not bowed in', '',
              'BUILD-GUIDE 4.5 said the brace `FIN-009` is "bowed into its slots, anchor end first, then sprung into the '
              'collar ear". Both ends sit %g mm deep in blind slots cut to the strip section. With the anchor end '
              'seated, the strip must bow until its chord is %.1f mm shorter to clear the ear. Clamped at both ends '
              '(first buckling mode), free length %.1f mm of %.1f mm: bow amplitude a = (2/pi) sqrt(L d) = %.1f mm, peak '
              'strain eps = pi^2 a t / L^2 = **%.2f %%** against %.2f %% ultimate for pultruded carbon (%s). %s'
              % (ap.BOW['embed_mm'], bow['shorten_mm'], bow['free_mm'], bow['length_mm'], bow['bow_mm'],
                 bow['strain_pct'], bow['ult_pct'], bow['source'],
                 'It would pass, but the bench route below is used anyway.' if bow['ok'] else
                 'It would break the strip, so the check does not allow it. Instead the brace goes into the anchor and '
                 'the collar ear on the bench, each slid along the brace axis, and the three go on as one rigid '
                 'sub-assembly: the collar down the motor tube while the anchor drops into its pocket on the spar '
                 '(step 4.5a, swept).'), '']
    hg = [r for r in acts if r.get('kind') == 'hinge']
    if hg or [r for r in acts if r['type'] == 'swing']:
        L += ['## Rotations', '', '| Step | Part | Hinge line (axis; point mm) | Motion | Samples | Result |',
              '|---|---|---|---|---|---|']
        for r in hg:
            ro = r.get('rot') or {}
            L.append('| %s | %s | %s; %s | open %s deg, slid %s mm along its own plane until the tongue is under the '
                     'lip, then turned to closed (keys: %s) | %d | %s |' % (
                         r['step'], r['id'], ', '.join('%.2f' % c for c in ro.get('axis', [])),
                         ', '.join('%.1f' % c for c in ro.get('origin_mm', [])), r.get('open_deg'),
                         r.get('engage_mm'), '; '.join('(%s) %g deg' % (', '.join('%.1f' % c for c in k[0]), k[1])
                                                     for k in r.get('keys') or []),
                         r.get('samples', 0), 'ok' if r.get('ok') else 'FAIL'))
        for r in acts:
            if r['type'] != 'swing':
                continue
            ts = '; '.join('%s: %s' % (tp, ', '.join('%s %d on panel / %d on core' % (q['body'], q['tris_on_panel'],
                                                                                    q['tris_on_core']) for q in v))
                           for tp, v in (r.get('tape_split') or {}).items())
            L.append('| %s | %s | gate hinge joints | panels and what is bonded to them to the TE-up limit; hinge tape '
                     'split at the hinge line, each half with its side (%s) | %d | %s |' % (
                         r['step'], ', '.join(r.get('members') or []), ts or '—', r.get('samples', 0),
                         'ok' if r.get('ok') else 'FAIL'))
        L.append('')
    if built:
        L += ['## Built body by body', '', '| Step | Part | # | Piece | dir (removal) | Travel mm | Path segments | Result |',
              '|---|---|---|---|---|---|---|---|']
        for r in built:
            for n, q in enumerate(r.get('built') or []):
                L.append('| %s | %s | %d | %s | %s | %s | %d | %s |' % (
                    r['step'], r['id'], n + 1, q['name'], ', '.join('%.2f' % c for c in q['dir']) if q.get('dir') else '—',
                    q.get('travel_mm', '—'), len(q.get('path') or []) - 1, 'ok' if q['ok'] else 'FAIL'))
        L.append('')
    L += ['## Laid, wet or cut in place', '',
          'No motion: each appears where it lies (the film wipes it on, slice by slice) and is tested there against '
          'every body already placed.', '', '| Step | Part | Kind | Overlaps | Support |', '|---|---|---|---|---|']
    for r in inpl:
        L.append('| %s | %s | %s | %s | %s |' % (r['step'], r['id'], r.get('motion') or r['kind'],
                                                 'none' if r.get('ok') else 'see violations',
                                                 ', '.join(r.get('support') or []) or r.get('fixture') or '—'))
    L.append('')
    ht = [r for r in wires if r.get('held_tails') or r.get('tail_action')]
    if ht:
        L += ['## Leads laid in two parts', '',
              'A lead whose end part is not on yet is laid only up to its first in-line connector; the run beyond it '
              'waits coiled off the aircraft and is laid (and tested in place) once that part is on.', '',
              '| Step | Wire | Held run | Laid at |', '|---|---|---|---|']
        laid_at = {}
        for r in wires:
            for m, sp in (r.get('tails') or {}).items():
                laid_at[(m, sp['end'])] = r['step']
        for r in wires:
            for t in r.get('held_tails') or []:
                L.append('| %s | %s | from %s back to %s (curve %s) | step %s |' % (
                    r['step'], r['id'], t['end'], t['split_at'], '-'.join('%.2f' % c for c in t['span']),
                    laid_at.get((r['id'], t['end']), '— (never laid)')))
        L.append('')
    L += ['## Special cases (assembly_plan.OVERRIDES)', '', 'Each row names a real motion; none exempts a pair.', '',
          '| Part glob | Motion | Fixture | Source |', '|---|---|---|---|']
    for g, row in rep['overrides']:
        L.append('| %s | %s | %s | %s |' % (g, row.get('kind', 'swept (preferred directions %s)' % row.get('dirs')
                                                            if row.get('dirs') else 'swept'),
                                             row.get('fixture', '—'), row.get('why', '—')))
    L.append('')
    L += ['## Order changes against BUILD-GUIDE.md', '', '| Guide steps | Change | Why (found by this check) |',
          '|---|---|---|'] + ['| %s | %s | %s |' % d for d in ap.DEVIATIONS] + ['']
    if rep.get('swaps'):
        L += ['## Order changes inside a step (found by the check)', '',
              'The listed order in `assembly_plan.STEPS` was blocked; the planner put the part before the one that '
              'blocked it and re-planned.', '',
              '| Step | Moved | Now before | Was blocked by | Depth mm |', '|---|---|---|---|---|']
        for w in rep['swaps']:
            L.append('| %s | %s | %s | %s | %.3f |' % (w['step'], w['moved'], w['before'], w['blocker'],
                                                       w['depth_mm']))
        L.append('')
    if loose:
        L += ['## Wire ends waiting for a later part', '',
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
    L += ['## Every action', '',
          'dir = the direction the part is REMOVED along (it arrives moving the opposite way), aircraft frame x aft, '
          'y right, z up. Support = parts it touches when placed.', '',
          '| # | Step | Action | Id | Checked as | dir | Travel mm | Samples | Support / fixture | Result |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for r in acts:
        sup = ', '.join(r.get('support') or []) or (('fixture: ' + r['fixture']) if r.get('fixture') else '—')
        if r['type'] == 'wire' and r.get('loose_ends'):
            sup += ' (end parked: %s)' % ', '.join(r['loose_ends'])
        L.append('| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['i'], r['step'], r['type'], r['id'], how(r),
            ', '.join('%.2f' % c for c in r['dir']) if r.get('dir') else '—',
            r.get('travel_mm', '—'), r.get('samples', 0), sup if len(sup) < 90 else sup[:87] + '...',
            'ok' if r.get('ok') else 'FAIL'))
    L.append('')
    L += ['## What this check does not prove', '',
          '- The final pose of every part: that is the collision gate (`collision/collide.py`, `--glb`). This check '
          'starts 0.05 mm off the seat.',
          '- Tape, straps and wires are flexible: they are tested where they lie, not as a rigid sweep; a wire is '
          'also failed if it is laid after a tape it lies against.',
          '- Hands, tools and clearance for them (a hex key on a pinch bolt, a soldering iron): not modelled.',
          '- Gravity: no dynamics; a part counts as supported when it touches something placed or a named fixture.',
          '- Bench sub-assemblies are checked against their bench-mates only, then moved on as one body.',
          '- A solder joint is made at the end of the step its part goes on (BUILD-GUIDE order), so it is not an '
          'obstacle for the other parts of that same step.',
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
