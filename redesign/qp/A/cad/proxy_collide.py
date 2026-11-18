"""proxy_collide.py - Blender-free interpenetration SCREEN of the concept A CAD (sampling on the analytic shapes). NOT a gate: collide_a.py (Blender, 0.05 mm) is the gate.
    python -I redesign/qp/A/cad/proxy_collide.py [--watch CGE,HRN] [--n 60000] [--min-mm3 0.05] [--wires]
Method: the part solids are exactly what collide_a.py meshes (bodies = prism / revolve / loft in the part frame, minus the cuts incl. the seats). For every part whose id starts with one
of the --watch prefixes (default: the cage and the harness conduits) and every other part with an overlapping bounding box, N random points are drawn inside each body of the watched
part (rejection sampling in the body's bounding box); a point that is inside the watched solid AND inside the other solid counts as overlap volume (count x bbox volume / N).
Also --wires: every phase-lead strand sample point must lie inside an enclosing part cavity (not tested here) - instead it reports strand points that lie INSIDE a solid.
Sampling finds overlaps of volume >~ (bbox volume / N); thin faces that merely touch (bond lines, seats) give 0. Random seed fixed."""
import argparse
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for p in (os.path.join(REDESIGN, 'fusion'), os.path.join(REDESIGN, 'interfaces'), HERE):
    sys.path.insert(0, p)
import fusionkit as fk                # noqa: E402
import build_all                      # noqa: E402
from backends.stub_backend import StubBackend   # noqa: E402

MODEL = os.path.join(HERE, 'model')
AX, UV = fk.AX, fk.UV


def pip(u, v, poly):
    """Even-odd point in polygon, arrays u, v (N), poly list of (x, y)."""
    inside = np.zeros(u.shape, dtype=bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if y1 == y2:
            continue
        cond = (y1 > v) != (y2 > v)
        xi = (x2 - x1) * (v - y1) / (y2 - y1) + x1
        inside ^= cond & (u < xi)
    return inside


def inside_mesh(sh, P):
    """Even-odd ray parity along +x for a closed triangle mesh (kind 'mesh'); candidate points per triangle are
    found by a sorted-y window, so it stays fast for a tens-of-thousands-triangle body."""
    V = np.array(sh.verts, dtype=float)
    T = np.array(sh.tris, dtype=int)
    lo, hi = V.min(axis=0), V.max(axis=0)
    cand = np.flatnonzero(np.all((P >= lo) & (P <= hi), axis=1))
    res = np.zeros(len(P), dtype=bool)
    if not len(cand):
        return res
    Q = P[cand]
    order = np.argsort(Q[:, 1])
    ys = Q[order, 1]
    par = np.zeros(len(Q), dtype=np.int32)
    A, B, C = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    for a, b, c in zip(A, B, C):
        y0, y1 = min(a[1], b[1], c[1]), max(a[1], b[1], c[1])
        i0, i1 = np.searchsorted(ys, y0), np.searchsorted(ys, y1, side='right')
        if i1 <= i0:
            continue
        idx = order[i0:i1]
        q = Q[idx]
        z0, z1 = min(a[2], b[2], c[2]), max(a[2], b[2], c[2])
        m = (q[:, 2] >= z0) & (q[:, 2] <= z1)
        if not m.any():
            continue
        idx, q = idx[m], q[m]
        # barycentric coordinates of (y, z) in the triangle projected on the yz plane
        d = (b[1] - a[1]) * (c[2] - a[2]) - (c[1] - a[1]) * (b[2] - a[2])
        if abs(d) < 1e-18:
            continue
        w1 = ((q[:, 1] - a[1]) * (c[2] - a[2]) - (c[1] - a[1]) * (q[:, 2] - a[2])) / d
        w2 = ((b[1] - a[1]) * (q[:, 2] - a[2]) - (q[:, 1] - a[1]) * (b[2] - a[2])) / d
        w0 = 1.0 - w1 - w2
        ok = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not ok.any():
            continue
        xh = w0[ok] * a[0] + w1[ok] * b[0] + w2[ok] * c[0]
        hit = xh > q[ok, 0]
        par[idx[ok][hit]] ^= 1
    res[cand[np.flatnonzero(par)]] = True
    return res


def inside_shape(sh, P):
    if sh.kind == 'mesh':
        return inside_mesh(sh, P)
    ax = AX[sh.axis]
    if sh.kind == 'prism':
        iu, iv = UV[sh.axis]
        t = P[:, ax] - sh.offset
        d = sh.depth
        m = (t >= min(0.0, d)) & (t <= max(0.0, d))
        if not m.any():
            return m
        ins = pip(P[:, iu], P[:, iv], sh.loops[0])
        for h in sh.loops[1:]:
            ins &= ~pip(P[:, iu], P[:, iv], h)
        return m & ins
    if sh.kind == 'revolve':
        i, j = [q for q in range(3) if q != ax]
        a = P[:, ax] - sh.center[ax]
        r = np.hypot(P[:, i] - sh.center[i], P[:, j] - sh.center[j])
        return pip(a, r, sh.profile)
    # loft
    iu, iv = UV[sh.axis]
    t = P[:, ax]
    res = np.zeros(len(P), dtype=bool)
    secs = sh.sections
    for k in range(len(secs) - 1):
        o0, L0 = secs[k]
        o1, L1 = secs[k + 1]
        lo, hi = min(o0, o1), max(o0, o1)
        m = (t >= lo) & (t <= hi)
        if not m.any() or o1 == o0:
            continue
        f = (t[m] - o0) / (o1 - o0)
        u, v = P[m, iu], P[m, iv]
        ins = np.zeros(len(u), dtype=bool)
        n = len(L0)
        for e in range(n):
            e2 = (e + 1) % n
            x1 = L0[e][0] + f * (L1[e][0] - L0[e][0])
            y1 = L0[e][1] + f * (L1[e][1] - L0[e][1])
            x2 = L0[e2][0] + f * (L1[e2][0] - L0[e2][0])
            y2 = L0[e2][1] + f * (L1[e2][1] - L0[e2][1])
            dy = y2 - y1
            ok = dy != 0
            cond = ((y1 > v) != (y2 > v)) & ok
            with np.errstate(divide='ignore', invalid='ignore'):
                xi = (x2 - x1) * (v - y1) / np.where(ok, dy, 1.0) + x1
            ins ^= cond & (u < xi)
        res[np.flatnonzero(m)] = ins
    return res


def inv_matrix(M):
    return np.linalg.inv(np.array(M, dtype=float))


def to_local(Minv, W):
    return (Minv[:3, :3] @ W.T).T + Minv[:3, 3]


class Solid:
    def __init__(self, comp):
        self.c = comp
        self.M = np.array(comp.matrix(), dtype=float)
        self.Minv = inv_matrix(comp.matrix())
        self.cuts = [(s, inv_matrix(M)) for s, M in comp.world_cuts()]
        pts = np.array([comp.to_world(p) for s in comp.shapes for p in s.points()])
        self.lo, self.hi = pts.min(axis=0), pts.max(axis=0)

    def contains_world(self, W):
        """Boolean mask: points inside the solid (union of bodies minus cuts)."""
        L = to_local(self.Minv, W)
        ins = np.zeros(len(W), dtype=bool)
        for s in self.c.shapes:
            ins |= inside_shape(s, L)
        if ins.any():
            idx = np.flatnonzero(ins)
            for cs_, Ci in self.cuts:
                Lc = to_local(Ci, W[idx])
                k = inside_shape(cs_, Lc)
                ins[idx[k]] = False
                idx = idx[~k]
                if not len(idx):
                    break
        return ins


def sample_part(sol, n, rng):
    """World points inside the watched solid: n draws per body in the body's local bbox."""
    out = []
    for s in sol.c.shapes:
        pts = np.array(s.points())
        if s.kind == 'revolve':
            ax = AX[s.axis]
            i, j = [q for q in range(3) if q != ax]
            rm = max(r for _, r in s.profile)
            lo = np.array(s.center, dtype=float)
            hi = lo.copy()
            lo[ax] += min(a for a, _ in s.profile)
            hi[ax] += max(a for a, _ in s.profile)
            lo[i] -= rm
            hi[i] += rm
            lo[j] -= rm
            hi[j] += rm
        else:
            lo, hi = pts.min(axis=0), pts.max(axis=0)
        vol = float(np.prod(np.maximum(hi - lo, 1e-9)))
        Pl = lo + rng.random((n, 3)) * (hi - lo)
        k = inside_shape(s, Pl)
        Pl = Pl[k]
        if not len(Pl):
            continue
        W = (sol.M[:3, :3] @ Pl.T).T + sol.M[:3, 3]
        keep = sol.contains_world(W)
        out.append((W[keep], vol / n))
    return out


def sweep(sols, a, rng):
    """Mirror of a_assembly.py: main run (steps not in BENCH, in order) and bench run (BENCH steps only, nothing else placed). A step's parts, as one rigid group, are moved from
    seat - dir * travel to the seat in `step` mm samples; points drawn inside the moving solids (n per body) must not lie inside any part placed earlier (cuts count as empty)."""
    import a_assembly_plan as ap
    want = None if a.sweep == 'ALL' else set(a.sweep.split(','))
    bench = set(getattr(ap, 'BENCH', ()))
    bad = 0
    for run, pick in (('bench', lambda sid: sid in bench), ('main', lambda sid: sid not in bench)):
        placed = []
        for sid, cap, parts, d, travel, stp, *rest in ap.STEPS:
            if not pick(sid) or not parts:
                continue
            parts = [p for p in parts if p in sols]
            if d and (want is None or sid in want):
                samples = []
                for pid in parts:
                    samples += [W for W, w in sample_part(sols[pid], a.n, rng) if len(W)]
                P = np.vstack(samples) if samples else np.zeros((0, 3))
                worst = {}
                ts = sorted({float(travel), 0.0} | {i * float(stp or 1) for i in range(int(travel // (stp or 1)) + 1)}, reverse=True)
                for t in ts:
                    Q = P - np.array(d) * t / 1000.0
                    for oid in placed:
                        if oid in parts:
                            continue
                        sb = sols[oid]
                        m = np.all((Q >= sb.lo - 1e-9) & (Q <= sb.hi + 1e-9), axis=1)
                        if m.any():
                            k = sb.contains_world(Q[m])
                            if k.any():
                                worst[(oid, t)] = int(k.sum())
                if worst:
                    bad += 1
                    top = sorted(worst.items(), key=lambda kv: -kv[1])[:3]
                    print('%-5s %-6s BLOCKED by %s' % (run, sid, '; '.join('%s at t=%g mm (%d pts)' % (k[0], k[1], v) for k, v in top)))
                else:
                    print('%-5s %-6s ok    (%d samples, %d poses)' % (run, sid, len(P), len(ts)))
            placed += [p for p in parts if p not in placed]
    print('sweep: %d blocked steps' % bad)
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--watch', default='CGE-001,CGE-002,CGE-009,CGE-010,CGE-004,HRN-004,HRN-003')
    ap.add_argument('--n', type=int, default=60000)
    ap.add_argument('--min-mm3', type=float, default=0.05)
    ap.add_argument('--sweep', default='', help='sweep the D-202 steps of a_assembly_plan (comma list of step ids, or ALL = every step that has parts) against the parts placed before them')
    ap.add_argument('--wires', action='store_true', help='also test every wire strand (centre line + a ring of its radius) against every part solid')
    a = ap.parse_args()
    ctx, graph, results = build_all.build(StubBackend(), MODEL, os.path.join(MODEL, 'modules.txt'), log=lambda *x: None)
    pref = tuple(a.watch.split(','))
    sols = {pid: Solid(c) for pid, c in ctx.components.items() if c.shapes and not c.proxy}
    rng = np.random.default_rng(1)
    if a.sweep:
        return sweep(sols, a, rng)
    watched = [pid for pid in sols if pid.startswith(pref)]
    hits = []
    for pid in sorted(watched):
        sa = sols[pid]
        samples = sample_part(sa, a.n, rng)
        for oid, sb in sols.items():
            if oid == pid or (oid in watched and oid < pid):
                continue
            if np.any(sa.lo > sb.hi + 1e-6) or np.any(sb.lo > sa.hi + 1e-6):
                continue
            vol = 0.0
            allp = []
            for W, w in samples:
                if not len(W):
                    continue
                m = np.all((W >= sb.lo - 1e-9) & (W <= sb.hi + 1e-9), axis=1)
                if not m.any():
                    continue
                k = sb.contains_world(W[m])
                if k.any():
                    vol += float(k.sum()) * w
                    allp.append(W[m][k])
            if allp and vol * 1e9 >= a.min_mm3:
                P = np.vstack(allp)
                hits.append((pid, oid, vol * 1e9, P.min(axis=0) * 1e3, P.max(axis=0) * 1e3))
    if a.wires:
        for w in ctx.wires:
            if not w.edge.startswith('E-HRN-0') or w.edge[-1] not in '2345':
                continue                                       # the four phase bundles (the route this change touched)
            for line, d in (w.strands or [(w.points, w.dia)]):
                L = np.array(line)
                pts = []
                for i in range(len(L) - 1):
                    n = max(1, int(np.linalg.norm(L[i + 1] - L[i]) / 0.0003))
                    for k in range(n):
                        pts.append(L[i] + (L[i + 1] - L[i]) * k / n)
                pts = np.array(pts)
                T = np.gradient(pts, axis=0)
                T /= np.linalg.norm(T, axis=1)[:, None] + 1e-12
                ref = np.where(np.abs(T[:, 2:3]) < 0.9, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
                N1 = np.cross(T, ref)
                N1 /= np.linalg.norm(N1, axis=1)[:, None]
                N2 = np.cross(T, N1)
                ring = [pts] + [pts + (d / 2) * (np.cos(th) * N1 + np.sin(th) * N2) for th in np.linspace(0, 2 * np.pi, 6, endpoint=False)]
                for oid, sb in sols.items():
                    if oid.startswith(('PRP-001', 'PRP-004', 'PRP-005')) and False:
                        continue
                    for R in ring:
                        m = np.all((R >= sb.lo - 1e-9) & (R <= sb.hi + 1e-9), axis=1)
                        if m.any():
                            k = sb.contains_world(R[m])
                            if k.any():
                                q = R[m][k]
                                hits.append((w.edge, oid, float(k.sum()), q.min(axis=0) * 1e3, q.max(axis=0) * 1e3))
                                break
    hits.sort(key=lambda h: -h[2])
    for pid, oid, v, lo, hi in hits:
        print('%-12s x %-12s %9.3f mm3  at x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f mm' % (pid, oid, v, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    print('proxy_collide: %d watched parts, %d overlapping pairs >= %g mm3' % (len(watched), len(hits), a.min_mm3))
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(main())
