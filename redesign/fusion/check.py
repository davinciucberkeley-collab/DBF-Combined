"""check.py - build every module on the stub backend and check CAD against interfaces.json. Runs in about a second.

    python -I redesign/fusion/check.py              # redesign/subsystems
    python -I redesign/fusion/check.py --skeleton   # K09-L reference layout (redesign/fusion/skeleton)
    python -I redesign/fusion/check.py --examples   # generic test aircraft (redesign/fusion/examples)
    python -I redesign/fusion/check.py --root DIR [--strict] [--tol-mm 2]

Proves (exit 1 on any ERROR; --strict: on any WARN too):
  module    every module imports and build(ctx) runs
  part      every component has a declared part id, material, mass > 0 and at least one body
  missing   every MODELLED/CHECKED/VERIFIED part has a component (PROPOSED ones are listed as missing, WARN)
  register  every edge whose parts are both modelled is registered: electrical -> ctx.wire, hinged -> revolute/
            slider, mechanical/thermal -> rigid joint or ctx.contact
  touch     the two parts of every structural or thermal edge touch (bounding boxes within --tol-mm), joint
            origins lie on both parts, wire ends lie on their parts. Ground items ("flight": false) are modelled in
            the aircraft frame at their transport position, so cradle-to-wing edges are touch-checked too; an edge
            marked "stowed": true (a flight part removed for transport, e.g. a prop in its tray slot) is not
  transport ground-item bodies (each wall, cradle, tray) must not overlap a flight part they have no edge with:
            a cradle pressing a fin, or a part that does not fit inside the box (WARN; stowed parts exempt). A
            transport edge may list "also_contacts": [ids] of parts bonded to its flight partner (the tape skin on
            the core) that the ground item also bears on; each must share a load-bearing edge with that partner
  floating  no modelled group of parts is cut off from the rest (unless it attaches to a part not modelled yet);
            same rule as merge_check: "structural": false types (tie, label) do not hold a part, and a part
            flagged "carried": true located only by them (label, harness bundle) is exempt
  keepout   no body enters a registered keep-out (prop disc + clearance, hover ground plane) unless the keep-out
            exempts it (ERROR, with the depth in mm). Per body: the axis-aligned box is the pre-filter, then the
            convex hull of the body's vertices is tested against the (canted) cylinder (CR-E1-45), so a diagonal
            brace or a full-chord core box no longer over-reports. Exact for convex bodies; a concave body's hull is
            a superset (a hit there is conservative). A prop zone (k9.prop_keepout) is the swept blade volume plus
            the clearance on every face; its corners are square, so the final test is the hull's distance to the
            blade volume against the clearance (the requirement itself). Cleared boxes are listed as a note
  envelope  (K09-L roots) every flight part lies inside the aircraft envelope from params.json (WARN: unit slips)
  datums    (K09-L roots) the datum sheet built and DATUMS.md is not stale against params.json (WARN)
  graph     everything merge_check.py checks (schema, dangling edges, joint stacks, wires, mass budget...)
Does NOT prove (UNVERIFIED-IN-FUSION): that Fusion's kernel builds the sketches/lofts, that joints solve, that
bodies do not interpenetrate, real masses. Bounding boxes are coarse: touching boxes do not prove a glue line.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import build_all                                   # noqa: E402  (also puts redesign/interfaces on sys.path)
import merge_check                                 # noqa: E402
from fusionkit import bbox_gap, point_gap          # noqa: E402
from backends.stub_backend import StubBackend     # noqa: E402

ALLOWED = {'electrical': ('wire',), 'hinged': ('revolute', 'slider'),
           'mechanical': ('rigid', 'contact'), 'thermal': ('rigid', 'contact'), 'kinematic': ('revolute', 'slider')}


def run_checks(root, list_file, tol=0.002, budget=None, log=lambda *a: None, datums=None):
    ctx, _, results = build_all.build(StubBackend(), root, list_file, log=log, datums=datums)
    g = merge_check.check(merge_check.load(root))
    subs, tot = merge_check.rollup(g)
    merge_check.check_budget(g, merge_check.load_budget(budget), subs, tot)   # None -> params/mass_budget.json or MASS-CG.md
    issues = list(ctx.issues) + [(s, 'graph:' + c, i, m) for s, c, i, m in g.issues]
    add = lambda *i: issues.append(i)
    comps = ctx.components

    # part: component data
    for pid, c in sorted(comps.items()):
        if not c.material:
            add('ERROR', 'part', pid, 'no material')
        if not c.mass_g or c.mass_g <= 0:
            add('ERROR', 'part', pid, 'no mass (mass_g in interfaces.json)')
        if not c.shapes:
            add('ERROR', 'part', pid, 'component has no bodies')
        if c.status == 'PROPOSED':
            add('WARN', 'status', pid, 'modelled but status is PROPOSED (set MODELLED)')
        geo = c.volume_centroid()[1] if c.shapes else None
        if c.cg_declared and geo:
            d = point_gap(geo, (tuple(c.cg_declared),) * 2)
            if d > 0.030:
                add('WARN', 'cg', pid, 'declared CG is %.0f mm from the CAD centroid' % (d * 1000))

    # missing: declared parts without a component
    for pid, p in sorted(g.parts.items()):
        if pid not in comps:
            sev = 'WARN' if p['status'] == 'PROPOSED' else 'ERROR'
            add(sev, 'missing', pid, '%s part has no component (%s)' % (p['status'], p['subsystem']))

    # register + touch
    reg = ctx.registrations()
    for eid, e in sorted(g.edges.items()):
        a, b = comps.get(e.get('part_a')), comps.get(e.get('part_b'))
        kind, method = g.kind(e), g.method(e)
        regs = reg.pop(eid, [])
        if a is None or b is None:
            if regs:
                add('WARN', 'register', eid, 'registered but a part is not modelled yet')
            continue
        if not regs:
            add('ERROR', 'register', eid, '%s edge %s-%s has no joint/contact/wire in CAD' % (kind, a.id, b.id))
            continue
        allowed = ALLOWED.get('hinged' if method == 'hinged' else kind, ())
        for rk, obj in regs:
            if rk not in allowed:
                add('ERROR', 'register', eid, '%s edge registered as %s (allowed: %s)' % (kind, rk, '/'.join(allowed)))
            if rk in ('rigid', 'revolute', 'slider') and {obj.a, obj.b} != {a.id, b.id}:
                add('ERROR', 'register', eid, 'joint joins %s-%s but the edge is %s-%s' % (obj.a, obj.b, a.id, b.id))
        ba, bb = a.bbox(), b.bbox()
        if not (ba and bb):
            continue
        if e.get('stowed'):
            continue                       # flight part sits at its flight station in CAD, not in the box
        if kind in merge_check.STRUCTURAL or kind == 'thermal':
            gap = bbox_gap(ba, bb)
            if gap > tol:
                add('ERROR', 'touch', eid, '%s and %s are %.1f mm apart' % (a.id, b.id, gap * 1000))
        for rk, obj in regs:
            if rk in ('rigid', 'revolute', 'slider'):
                off = max(point_gap(obj.origin, ba), point_gap(obj.origin, bb))
                if off > tol:
                    add('ERROR', 'touch', eid, 'joint origin is %.1f mm off a part' % (off * 1000))
            if rk == 'wire':
                p0, p1 = obj.points[0], obj.points[-1]
                off = min(max(point_gap(p0, ba), point_gap(p1, bb)), max(point_gap(p0, bb), point_gap(p1, ba)))
                # D-88: a lead that runs whole inside one part's own connector (the pack's lead into its AS150U
                # half) reaches the other part through the mated contacts: both ends on one part, the parts touching
                if off > tol and bbox_gap(ba, bb) <= tol:
                    off = min(off, max(point_gap(p0, ba), point_gap(p1, ba)), max(point_gap(p0, bb), point_gap(p1, bb)))
                if off > tol:
                    add('ERROR', 'touch', eid, 'wire end is %.1f mm off its part' % (off * 1000))
    for eid, regs in sorted(reg.items()):
        add('ERROR', 'register', eid, 'CAD registers an edge that no interfaces.json declares')

    # floating: modelled structure split into groups that do not reach a not-yet-modelled part
    # Same rule as merge_check (D-46): only load-bearing edges join groups, and "carried": true items (labels,
    # harness bundles) located by a non-structural type only (tie, label) are exempt, not floating.
    modelled = {k: g.parts[k] for k in comps if k in g.parts and g.parts[k].get('flight', True)}
    for p in merge_check.carried(g, dict(modelled)) | {k for k in modelled if comps[k].proxy}:
        modelled.pop(p)                    # carried items and mass proxies (Component.proxy) never float
    groups = merge_check.clusters(g, parts=modelled)
    anchored = set()
    for e in g.edges.values():
        if g.kind(e) in merge_check.STRUCTURAL and g.load_bearing(e):
            ends = (e.get('part_a'), e.get('part_b'))
            if any(x not in comps for x in ends):          # declared-not-modelled or not declared yet (dangling)
                anchored.update(x for x in ends if x in comps)
    for grp in groups[1:]:
        if not grp & anchored:
            add('ERROR', 'floating', ', '.join(sorted(grp)), 'modelled parts not connected to the main structure')

    # keepout: prop discs, hover ground (registered by the owning modules)
    # Per-body world boxes, not one box per component: a canted plate's component box has corners where no body
    # is (CR-E1-31b; tilted prop discs are exact cylinders, fusionkit.Keepout._hits_tilted).
    def boxes(c):                          # per-body world boxes: a multi-leg bundle is not one big box
        out = []
        for sh in c.shapes:
            pts = [c.to_world(p) for p in sh.points()]
            out.append((sh, (tuple(min(p[i] for p in pts) for i in range(3)),
                             tuple(max(p[i] for p in pts) for i in range(3)))))
        return out
    flying = {pid: c for pid, c in comps.items() if (g.parts.get(pid) or {}).get('flight', True) and c.shapes}
    fly_boxes = {pid: boxes(c) for pid, c in flying.items()}
    # CR-E1-45: a body whose box enters is then tested by the convex hull of its vertices (fusionkit.Keepout.
    # hull_hits): a diagonal brace or a wing core whose box spans the whole chord no longer reports its empty box
    # corners. Real hits report the depth (uniform inset of the zone's faces the hull still enters); the
    # box-only cases are kept in ctx.keepout_box_only so the report can show what the hull cleared.
    ctx.keepout_box_only = []
    for ko in ctx.keepouts:
        for pid in sorted(flying):
            if pid in ko.exempt:
                continue
            c = flying[pid]
            hit, cleared = {}, []
            for sh, b in fly_boxes[pid]:
                if not ko.hits(b):
                    continue
                name = sh.name or sh.kind
                pts = [c.to_world(p) for p in sh.hull_points()]
                d = ko.core_distance(pts) if ko.hull_hits(pts) else None
                if ko.clearance and d is not None and d >= ko.clearance - 1e-6:
                    cleared.append(name)                 # in the zone's square corner, >= clearance from the blades
                elif ko.clearance and d is not None:
                    hit[name] = min(hit.get(name, 9.0), d)
                elif ko.hull_hits(pts):
                    hit[name] = max(hit.get(name, 0.0), ko.hull_depth(pts))
                else:
                    cleared.append(name)
            if hit:
                if ko.clearance:
                    worst = min(hit.values())
                    how = '%.1f mm from the swept blade volume, clearance %.0f mm' % (worst * 1000, ko.clearance * 1000)
                else:
                    how = 'by %.1f mm' % (max(hit.values()) * 1000)
                add('ERROR', 'keepout', pid, 'body (%s) enters %s: %s (convex hull; registered by %s)' % (
                    ', '.join(sorted(hit)[:3]), ko.name, how, ko.sub))
            if cleared:
                ctx.keepout_box_only.append((pid, ko.name, sorted(set(cleared))))

    # transport: ground-item bodies vs flight parts (cradles never press fins or tubes; everything fits the box)
    ground = {pid: c for pid, c in comps.items() if not (g.parts.get(pid) or {}).get('flight', True) and c.shapes}
    if ground:
        partners, stowed = {}, set()
        for e in g.edges.values():
            a, b = e.get('part_a'), e.get('part_b')
            partners.setdefault(a, set()).add(b)
            partners.setdefault(b, set()).add(a)
            if e.get('stowed'):
                stowed.update(x for x in (a, b) if (g.parts.get(x) or {}).get('flight', True))
        # CR-D7-19: a transport edge may name "also_contacts": flight parts bonded on its flight partner that the
        # ground item bears on too (a cradle on the tape skin over the core). Each must share a load-bearing edge
        # with that partner, so the list cannot hide an unrelated part.
        for e in g.edges.values():
            extra = e.get('also_contacts') or []
            if not extra:
                continue
            a, b = e.get('part_a'), e.get('part_b')
            gnd = [x for x in (a, b) if not (g.parts.get(x) or {}).get('flight', True)]
            fl = [x for x in (a, b) if x not in gnd]
            for x in extra:
                ok = gnd and fl and any(g.load_bearing(f) and {f.get('part_a'), f.get('part_b')} == {x, fl[0]}
                                        for f in g.edges.values())
                if not ok:
                    add('ERROR', 'transport', e['id'], 'also_contacts %s: not bonded to %s by a load-bearing edge, '
                        'or the edge has no ground item' % (x, fl[0] if fl else '?'))
                    continue
                partners.setdefault(gnd[0], set()).add(x)
        fboxes = {pid: boxes(c) for pid, c in flying.items() if pid not in stowed}
        for gid, gc in sorted(ground.items()):
            hits = {}
            for sh, sb in boxes(gc):
                for pid, fbs in fboxes.items():
                    if pid in partners.get(gid, ()):
                        continue
                    for _, fb in fbs:
                        depth = min(min(sb[1][i], fb[1][i]) - max(sb[0][i], fb[0][i]) for i in range(3))
                        if depth > tol and depth > hits.get(pid, (0,))[0]:
                            hits[pid] = (depth, sh.name or 'body')
            for pid, (depth, name) in sorted(hits.items()):
                add('WARN', 'transport', pid, 'overlaps %s (%s) by %.0f mm: pressed, or does not fit the box' % (
                    gid, name, depth * 1000))

    # envelope + datums (K09-L roots only: build_datums set ctx.envelope)
    if ctx.envelope:
        lo, hi = ctx.envelope
        for pid, c in sorted(flying.items()):
            b = c.bbox()
            out = max(max(lo[i] - b[0][i], b[1][i] - hi[i]) for i in range(3))
            if out > 0:
                add('WARN', 'envelope', pid, '%.0f mm outside the aircraft envelope (unit slip? see DATUMS.md)' % (out * 1000))
        try:
            import k09kit
            if k09kit.datums_md_stale(ctx.params):
                add('WARN', 'datums', 'DATUMS.md', 'stale against params.json: python -I redesign/fusion/k09kit.py --datums-md')
        except Exception as e:
            add('WARN', 'datums', 'DATUMS.md', 'could not compare: %s' % e)
    return ctx, results, issues


def main(argv=None):
    ap = argparse.ArgumentParser(description='Stub-build all modules and check them against interfaces.json.')
    ap.add_argument('--examples', action='store_true')
    ap.add_argument('--skeleton', action='store_true')
    ap.add_argument('--root')
    ap.add_argument('--strict', action='store_true')
    ap.add_argument('--tol-mm', type=float, default=2.0)
    a = ap.parse_args(argv)
    root, lst = build_all.roots(a.examples, a.root, a.skeleton)
    budget = os.path.join(root, 'mass_budget.json')
    ctx, results, issues = run_checks(root, lst, a.tol_mm / 1000.0, budget if os.path.exists(budget) else None,
                                     log=lambda m: print(m) if m.startswith('not built') else None)

    per = {}
    for sev, code, item, msg in issues:
        sub = next((c.subsystem for c in ctx.components.values() if c.id in str(item)), None) or \
            (item if any(r[0] == item for r in results) else '-')
        per.setdefault(sub, [0, 0])[0 if sev == 'ERROR' else 1] += 1
    print('%-14s %-4s %6s %5s %6s %6s %5s %8s %4s %4s' % ('module', 'ok', 'ms', 'parts', 'bodies', 'joints',
                                                          'wires', 'mass g', 'err', 'warn'))
    for sub, f, ok, ms, _ in results:
        cs = [c for c in ctx.components.values() if c.subsystem == sub]
        e, w = per.get(sub, [0, 0])
        print('%-14s %-4s %6.1f %5d %6d %6d %5d %8.0f %4d %4d' % (
            sub, 'ok' if ok else 'FAIL', ms, len(cs), sum(len(c.shapes) for c in cs),
            sum(1 for j in ctx.joints if j.sub == sub), sum(1 for x in ctx.wires if x.sub == sub),
            sum(c.mass_g or 0 for c in cs), e, w))
    M, cg = ctx.rollup()
    print('TOTAL %.0f g, CG %s m (declared mass; CG declared or CAD centroid); %d datums, %d keep-outs' % (
        M, ', '.join('%.3f' % v for v in cg) if cg else '-', len(ctx.datums), len(ctx.keepouts)))
    box_only = getattr(ctx, 'keepout_box_only', [])
    if box_only:
        print('note: %d body boxes enter a keep-out but their convex hulls do not (box artefacts, not issues): %s' % (
            len(box_only), '; '.join('%s/%s (%s)' % (p, k, ', '.join(n[:2])) for p, k, n in box_only[:8])
            + ('; ...' if len(box_only) > 8 else '')))
    for sev, code, item, msg in sorted(issues, key=lambda i: (i[0] != 'ERROR', i[1])):
        print('  %-5s %-16s %-16s %s' % (sev, code, item, msg))
    nerr = sum(1 for i in issues if i[0] == 'ERROR')
    nwarn = len(issues) - nerr
    fail = nerr or (a.strict and nwarn) or not results
    print('check: %s (%d modules, %d errors, %d warnings%s)' % ('FAIL' if fail else 'PASS', len(results), nerr, nwarn,
                                                              ', strict' if a.strict else ''))
    if not results:
        print('  no modules found under %s' % root)
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
