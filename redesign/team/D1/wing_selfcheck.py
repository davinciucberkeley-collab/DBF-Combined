"""D1 self-check of the wing CAD geometry (what check.py's bounding boxes cannot see).

    python -I redesign/team/D1/wing_selfcheck.py     # exit 1 on any FAIL

Checks every body of every wing component built by subsystems/wing/fusion/wing.py on the stub backend:
  1. each sketch loop is a simple polygon (no self-intersection, no repeated points) with area > 0;
  2. each hole loop lies inside its outer loop and does not cross it;
  3. the core bodies tile the span with no gap and no overlap (|y| 0 ... 0.575) and are exact mirrors left/right;
  4. every core segment keeps >= 2 mm of foam round the spar bore where the bore is closed (ASM-A5-MIN-COVER);
  5. the elevon panels sit in the core cut-outs with the declared end gap and never overlap a core body;
  6. the cut list matches the mating parts: block pocket (R corners) vs fins block, lip beads, anchor pocket vs fins
     anchor, recess vs pod;
  7. D6's servo frame, torque tubes and horn blades sit in the pocket, grooves and slots;
  8. D-68 / D-69 / CR-F2-14 rules: LE strip edges aft of x/c 0.10, recess-step fillet legs, JR recess wall.
These are geometric facts of the sketches Fusion will receive, not proof that Fusion builds them (UNVERIFIED-IN-FUSION).
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'fusion'))
import wing_data as wd   # noqa: E402

FAILS = []


def check(ok, what):
    print('  %-4s %s' % ('ok' if ok else 'FAIL', what))
    if not ok:
        FAILS.append(what)


def seg_x(p, q, r, s):
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2, d3, d4 = orient(r, s, p), orient(r, s, q), orient(p, q, r), orient(p, q, s)
    return (d1 * d2 < -1e-18) and (d3 * d4 < -1e-18)


def simple(loop):
    n = len(loop)
    if len(set((round(x, 9), round(z, 9)) for x, z in loop)) != n:
        return False
    E = [(loop[i], loop[(i + 1) % n]) for i in range(n)]
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if seg_x(E[i][0], E[i][1], E[j][0], E[j][1]):
                return False
    return True


def area(loop):
    return 0.5 * abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(loop, loop[1:] + loop[:1])))


def inside(pt, loop):
    x, z = pt
    c = False
    for (x1, z1), (x2, z2) in zip(loop, loop[1:] + loop[:1]):
        if (z1 > z) != (z2 > z) and x < x1 + (z - z1) * (x2 - x1) / (z2 - z1):
            c = not c
    return c


def mating(g):
    """7. The mechanisms parts (D6) built by their own module sit in the wing's cuts (skipped if D6 has no module)."""
    import contextlib
    import io
    import build_all
    from backends.stub_backend import StubBackend
    with contextlib.redirect_stdout(io.StringIO()):
        ctx, _f, _r = build_all.build(StubBackend(), *build_all.roots(), log=lambda *a: None)
    C = ctx.components
    if 'MEC-008-R' not in C:
        print('  --   7  mechanisms not modelled yet: pocket, groove and slot not compared')
        return
    (lo, hi), tol = C['MEC-008-R'].bbox(), 1e-6
    ok = g['sp_x'][0] - tol <= lo[0] and hi[0] <= g['sp_x'][1] + tol and g['sp_y'][0] - tol <= lo[1] and hi[1] <= g['sp_y'][1] + tol         and hi[2] <= g['sp_zc'] + tol
    check(ok, '7  servo frame MEC-008-R x %.4f-%.4f y %.4f-%.4f top z %.4f inside the pocket x %.4f-%.4f y %.4f-%.4f ceiling %.4f' % (
        lo[0], hi[0], lo[1], hi[1], hi[2], g['sp_x'][0], g['sp_x'][1], g['sp_y'][0], g['sp_y'][1], g['sp_zc']))
    gx0, gx1, gzc = g['tube_groove']
    ok = True
    for pid in ('MEC-009-RI', 'MEC-009-RO'):
        if pid in C:
            lo, hi = C[pid].bbox()
            ok = ok and gx0 - tol <= lo[0] and hi[0] <= gx1 + tol and hi[2] <= gzc + tol
    for pid in ('MEC-009-RI', 'MEC-009-RO'):
        if pid in C:
            lo, hi = C[pid].bbox()
            ok = ok and any(a - tol <= lo[1] and hi[1] <= b + tol for a, b in g['tube_groove_y'])
    check(ok, '7  torque tubes MEC-009-RI/RO inside the panel groove x %.4f-%.4f under z %.4f, |y| %s' % (
        gx0, gx1, gzc, ' / '.join('%.3f-%.3f' % r for r in g['tube_groove_y'])))
    ok = True
    for pid, (ya, yb) in (('MEC-004-R', g['horn_y'][0]), ('MEC-006-R', g['horn_y'][1])):
        if pid in C:
            for sh in C[pid].shapes:
                if 'blade' in (sh.name or ''):
                    pts = [C[pid].to_world(p) for p in sh.points()]
                    ok = ok and ya - tol <= min(p[1] for p in pts) and max(p[1] for p in pts) <= yb + tol and                         g['horn_x'][0] - tol <= min(p[0] for p in pts) and max(p[0] for p in pts) <= g['horn_x'][1] + tol
    check(ok, '7  horn blades MEC-004-R / MEC-006-R inside the 2.5 mm panel slots y %.4f-%.4f / %.4f-%.4f' % (
        g['horn_y'][0] + g['horn_y'][1]))


def main():
    ctx, P, g, mod = wd.build_wing()
    print('wing_selfcheck: section %s' % g['src'])
    bad = []
    for pid, c in sorted(ctx.components.items()):
        if not pid.startswith('WNG'):
            continue
        for s in c.shapes:
            if s.kind != 'prism':
                continue
            outer, holes = s.loops[0], s.loops[1:]
            if not simple(outer) or area(outer) <= 0:
                bad.append('%s %s outer' % (pid, s.name))
            for h in holes:
                if not simple(h) or not all(inside(p, outer) for p in h) or any(
                        seg_x(a, b, p, q) for a, b in zip(h, h[1:] + h[:1]) for p, q in zip(outer, outer[1:] + outer[:1])):
                    bad.append('%s %s hole' % (pid, s.name))
    check(not bad, '1-2 every loop simple, every hole inside its outer loop (%s)' % (', '.join(bad[:4]) or 'all bodies'))

    core = [s for s in ctx.components['WNG-001'].shapes]
    spans = sorted({(round(min(s.offset, s.offset + s.depth), 7), round(max(s.offset, s.offset + s.depth), 7)) for s in core})
    tiled = abs(spans[0][0] + g['half']) < 1e-6 and abs(spans[-1][1] - g['half']) < 1e-6 and all(
        abs(a[1] - b[0]) < 1e-6 for a, b in zip(spans, spans[1:]))
    check(tiled, '3  core segments tile y %.3f ... %.3f with no gap or overlap (%d spans, %d bodies)' % (-g['half'], g['half'], len(spans), len(core)))
    pos = sorted((round(s.offset, 7), round(s.depth, 7), len(s.loops[0])) for s in core if s.offset > 0)
    neg = sorted((round(-s.offset, 7), round(-s.depth, 7), len(s.loops[0])) for s in core if s.offset < 0 and s.offset + s.depth <= 1e-9)
    check(pos == neg, '3  left half is the exact mirror of the right half (%d bodies each)' % len(pos))

    worst, foam_bead = 1.0, 1.0
    for y0, y1, act in mod.segments(g):
        if 'spar' in act and not ({'block', 'anchor', 'window'} & act):
            plain = mod.segment_loops(g, act)                                   # skin line (a lip bead is cover too)
            for (loop, holes), (ploop, _ph) in zip(mod.segment_loops(g, act, y0, y1), plain):
                for h in holes:
                    for p in h:
                        worst = min(worst, min(math.hypot(p[0] - a[0], p[1] - a[1]) for a in ploop))
                        if 'bead' in act:
                            foam_bead = min(foam_bead, min(math.hypot(p[0] - a[0], p[1] - a[1]) for a in loop))
    check(worst >= 0.002, '4  cover round the closed spar bore >= 2 mm: min %.2f mm' % (worst * 1000))
    check(foam_bead >= 0.001, '4  foam left between the bore and a lip bead >= 1 mm (bead is epoxy, cover counted to the skin): min %.2f mm' % (foam_bead * 1000))

    # 5. panels against the core: over a panel's y range a core body may reach aft of the hinge only in the R corner
    #    fill at the fin-root tab, and then the panel front there is at least the end gap further aft
    ok5, worst5 = True, 1.0
    for pid in ('WNG-011-R', 'WNG-012-R', 'WNG-011-L', 'WNG-012-L'):
        es = ctx.components[pid].shapes
        ey = [min(min(e.offset, e.offset + e.depth) for e in es), max(max(e.offset, e.offset + e.depth) for e in es)]
        for s in core:
            cy = sorted((s.offset, s.offset + s.depth))
            cx = max(p[0] for p in s.loops[0])
            if cx <= g['xh'] + 1e-6:
                continue
            for e in es:
                py = sorted((e.offset, e.offset + e.depth))
                if cy[0] < py[1] - 1e-9 and py[0] < cy[1] - 1e-9:
                    sep = min(p[0] for p in e.loops[0]) - cx
                    worst5 = min(worst5, sep)
                    if sep < g['e_gap'] - 1e-6:
                        ok5 = False
        a, b = [sp for sp in g['spans']][0 if '011' in pid else 1]
        lo, hi = (a, b) if pid.endswith('R') else (-b, -a)
        if abs(ey[0] - (lo + g['e_gap'])) > 1e-6 or abs(ey[1] - (hi - g['e_gap'])) > 1e-6:
            ok5 = False
    check(ok5, '5  elevons in the core cut-outs, end gap %.1f mm; at the R %.0f mm tab corners the panel front stays >= %.2f mm aft of the core fill' % (
        g['e_gap'] * 1000, g['ecr'] * 1000, worst5 * 1000))

    F = wd.k9.local('fins')
    bw = wd.k9.lval(F, 'fin_detail.block.width_m', 'm', 0.036)
    check(g['blk_y'][1] - g['blk_y'][0] >= bw and g['blk_x'][0] <= 0.028 + 1e-6 and g['blk_x'][1] >= 0.097 - 1e-6,
          '6  block pocket y %.4f-%.4f x %.4f-%.4f covers the fins block (%.0f mm wide, x 0.028-0.097)' % (
              g['blk_y'][0], g['blk_y'][1], g['blk_x'][0], g['blk_x'][1], bw * 1000))
    ax = wd.k9.lval(F, 'fin_detail.anchor.len_x_m', 'm', 0.02)
    check(g['x_slot'][1] - g['x_slot'][0] >= ax and g['anc_y'][1] - g['anc_y'][0] >= wd.k9.lval(F, 'fin_detail.anchor.len_y_m', 'm', 0.016),
          '6  anchor pocket %.1f x %.1f mm holds the %.0f x 16 mm anchor saddle' % (
              (g['x_slot'][1] - g['x_slot'][0]) * 1000, (g['anc_y'][1] - g['anc_y'][0]) * 1000, ax * 1000))
    check(abs(g['x_rec1'] - 0.065) < 0.0005 and abs(g['z_rec'] - wd.k9.val(P, 'pod.z_base_m', 'm')) < 1e-9,
          '6  pod recess x %.4f-%.4f, floor z %.3f matches CR-D2-04 (x 0.0226-0.065, z 0.015)' % (g['x_rec0'], g['x_rec1'], g['z_rec']))
    # 6. D-68 pocket corners against D3's rounded block (radius edge_r, same centre, bond gap)
    r_b = wd.k9.lval(F, 'fin_detail.block.edge_r_m', 'm', 0.003)
    gap_f = g['blk_rp'] - r_b
    bx0, bx1 = g['blk_x'][0] + gap_f, g['blk_x'][1] - gap_f
    by0, by1 = g['blk_y'][0] + gap_f, g['blk_y'][1] - gap_f
    ok6, min_gap = True, 1.0
    for y0, y1, act in mod.segments(g):
        if 'block' not in act:
            continue
        xa, xb = mod.pocket_x(g, y0, y1)
        for i in range(11):
            y = y0 + (y1 - y0) * i / 10
            d = min(y - by0, by1 - y)
            if d < 0:
                continue
            dx = r_b - math.sqrt(max(r_b ** 2 - (r_b - d) ** 2, 0.0)) if d < r_b else 0.0
            min_gap = min(min_gap, (bx0 + dx) - xa, xb - (bx1 - dx))
    ok6 = min_gap >= -1e-9
    check(ok6, '6  stepped R %.2f mm pocket corners contain the R %.0f mm block everywhere (min clearance %.2f mm)' % (
        g['blk_rp'] * 1000, r_b * 1000, min_gap * 1000))
    beads = [s for s in ctx.components['WNG-006-R'].shapes]
    cover = sum(abs(s.depth) for s in beads if 'upper' in s.name), sum(abs(s.depth) for s in beads if 'lower' in s.name)
    deep = max(mod.bead_depth(g, y0, y1) for y0, y1, act in mod.segments(g) if 'bead' in act)
    check(all(abs(c - 2 * g['bead_leg']) < 1e-7 for c in cover) and deep >= g['bead_leg'] - 1e-9,
          '6  lip beads cover %.1f mm of span per surface per side (2 x %.0f mm, inboard + outboard), %.1f mm deep at the pocket wall' % (
              cover[0] * 1000, g['bead_leg'] * 1000, deep * 1000))
    # 8. LE seams (CR-B2-17), recess fillet (CR-C3-17), JR recess (CR-F2-14)
    le = min(g['le_edge'].values()), min(g['skin_lap'].values())
    check(le[0] >= g['le_clean_x'] and le[1] >= g['le_clean_x'] - 1e-9 or le[0] >= g['le_clean_x'],
          '8  LE strip edges x %.4f upper / %.4f lower, aft of x/c 0.10 (%.3f); strip seams under it from x %.4f' % (
              g['le_edge']['upper'], g['le_edge']['lower'], g['le_clean_x'], le[1]))
    check(g['rf_legs'][0] >= 0.005 - 1e-9 and g['rf_legs'][1] >= g['rf_legs'][0] - 0.0005,
          '8  recess-step fillet legs %.1f mm on the floor x %.1f mm up the step (full step height)' % (g['rf_legs'][0] * 1000, g['rf_legs'][1] * 1000))
    wall = g['sp_x'][0] - g['jr_x'][1]
    check(wall >= 0.003 and g['jr_y'][0] < g['sgroove_y'][1] < g['jr_y'][1],
          '8  JR recess x %.3f-%.3f y %.3f-%.3f %.0f mm deep on the servo branch; %.1f mm foam to the servo pocket' % (
              g['jr_x'] + g['jr_y'] + (g['jr_d'] * 1000, wall * 1000)))
    mating(g)
    print('wing_selfcheck: %s' % ('PASS' if not FAILS else 'FAIL (%d)' % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
