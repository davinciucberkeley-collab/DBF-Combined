"""A5 CAD lead: integration check over everything the designers delivered (redesign/subsystems/*).

Run:  python -I redesign/team/A5/integration_check.py
Writes team/A5/integration.json (snapshot read by cad_claims.py) and team/A5/INTEGRATION.md (tables).

What it does (stdlib only, about 2 s):
  1. fusion/check.py on redesign/subsystems (stub build + every merge_check graph check), issues grouped by the
     role that must act (designer of the subsystem; A1/A3/B3 for the aircraft CG);
  2. mass roll-up three ways per subsystem: allocation (params/mass_budget.json), declared flight mass
     (interfaces.json, what check.py and merge_check use) and parts.csv (qty x per-unit mass_g, flight rows), plus
     each subsystem's CG and its share of the aircraft CG shift from the allocation layout (the R3 skeleton);
  3. model integrity: declared part CG (cg_xyz_m) against the CAD body centroid (uniform density) of the same
     component, flagged when they differ by more than CG_TOL_M (a declared CG that is not where the part is);
  4. parts.csv <-> interfaces.json: every flight node has a parts.csv row and the masses agree (instance rule:
     node <id>-<UR|UL|LR|LL|L|R|C...> = row <id>, line mass = qty x mass_g).
"""
import contextlib
import csv
import io
import json
import math
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REDESIGN, 'fusion'))
import build_all      # noqa: E402
import check          # noqa: E402
import merge_check    # noqa: E402

CG_TOL_M = 0.010          # declared CG vs CAD centroid; bought envelopes and lumped bundles may differ by design
MASS_TOL_G = 0.5
OWNER = {'wing': 'D1', 'fins': 'D3', 'pod': 'D2', 'landing': 'D5', 'propulsion': 'E1', 'mechanisms': 'D6',
         'power': 'F1', 'avionics': 'F3', 'harness': 'F2', 'transport': 'D7'}
SUFFIX = re.compile(r'^(.*?)-(UR|UL|LR|LL|L|R|C|U|D)([OI])?$')


def run(root, lst, datums=True):
    with contextlib.redirect_stdout(io.StringIO()):
        ctx, results, issues = check.run_checks(root, lst, datums=datums)
    g = merge_check.check(merge_check.load(root))
    return ctx, results, issues, g


def base_id(pid):
    m = SUFFIX.match(pid)
    return m.group(1) if m else pid


def parts_csv(sub):
    path = os.path.join(REDESIGN, 'subsystems', sub, 'parts.csv')
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f))


PREFIX = {'WNG': 'wing', 'FIN': 'fins', 'POD': 'pod', 'GER': 'landing', 'PRP': 'propulsion', 'MEC': 'mechanisms',
          'PWR': 'power', 'AVN': 'avionics', 'HRN': 'harness', 'TRN': 'transport'}


def owner_of(g, item):
    p = g.parts.get(item)
    if p:
        return OWNER.get(p.get('subsystem'), '?')
    e = g.edges.get(item)
    if e:
        return OWNER.get(e.get('owner') or '', '?')
    m = re.match(r'^E-([A-Z]{3})-', item)                 # an edge only the CAD registers: the module's owner
    if m and m.group(1) in PREFIX:
        return OWNER[PREFIX[m.group(1)]]
    return OWNER.get(item, '?')


def acting_role(g, sev, code, item, msg):
    """The role that must act on a check.py issue (not always the owner of the part named)."""
    first = item.split(',')[0].strip()
    if code == 'graph:cg':
        return 'A1'                                       # configuration-level: A1 decides, A3/B3 inform
    if code == 'graph:mass':
        return OWNER.get(item, '?')
    if code == 'graph:one-sided':                         # "... ; <sub> has not acknowledged it"
        m = re.search(r'; (\S+) has not acknowledged', msg)
        return OWNER.get(m.group(1), '?') if m else owner_of(g, first)
    if code in ('graph:unconnected', 'graph:unpowered'):
        return 'F2'                                       # the harness declares every wire (WIRE-LIST)
    if code == 'transport':
        m = re.search(r'overlaps (\S+)', msg)
        return owner_of(g, m.group(1)) if m else 'D7'     # the ground item's owner holds the edge
    return owner_of(g, first)


def main():
    ctx, results, issues, g = run(*build_all.roots())
    sk_ctx, _, sk_issues, sk_g = run(*build_all.roots(skeleton=True))
    budget = json.load(open(os.path.join(REDESIGN, 'params', 'mass_budget.json'), encoding='utf-8'))
    alloc = budget['allocations_g']
    subs, tot = merge_check.rollup(g)
    sk_subs, sk_tot = merge_check.rollup(sk_g)

    # 2. mass three ways + CG shift decomposition against the allocation layout (skeleton)
    rows = []
    M, Msk = tot['mass_g'], sk_tot['mass_g']
    for sub in [r[0] for r in results if r[0] in OWNER]:
        s, k = subs.get(sub), sk_subs.get(sub)
        csv_rows = parts_csv(sub) or []
        flight = {pid for pid, p in g.parts.items() if p.get('subsystem') == sub and p.get('flight', True)}
        flight_base = {base_id(p) for p in flight} | flight
        csv_m = sum(float(r['qty'] or 0) * float(r['mass_g'] or 0) for r in csv_rows if r['part_id'] in flight_base)
        x = s['cg'][0] if s and s['cg'] else None
        xs = k['cg'][0] if k and k['cg'] else None
        # share of the aircraft CG shift: this subsystem's moment change over the actual mass, minus the effect of
        # the total-mass change on the skeleton CG (sums to x_cg - x_cg_skeleton)
        dmom = ((s['m_cg'][0] if s else 0) - (k['m_cg'][0] if k else 0)) / M
        dmass = ((s['mass_g'] if s else 0) - (k['mass_g'] if k else 0)) * sk_tot['cg'][0] / M
        rows.append({'sub': sub, 'owner': OWNER[sub], 'alloc_g': alloc.get(sub), 'declared_g': round(s['mass_g'], 1) if s else 0,
                     'csv_g': round(csv_m, 1), 'skeleton_g': round(k['mass_g'], 1) if k else 0,
                     'cg_x_m': x, 'skeleton_cg_x_m': xs, 'dcg_x_mm': round((dmom - dmass) * 1000, 2)})
    cg = tot['cg']
    cg_sk = sk_tot['cg']

    # 3. declared CG vs CAD centroid
    cg_diff = []
    for pid, c in sorted(ctx.components.items()):
        p = g.parts.get(pid) or {}
        if not p.get('flight', True) or not p.get('cg_xyz_m') or not c.shapes:
            continue
        V, cen = c.volume_centroid()
        if not V:
            continue
        d = math.dist(cen, p['cg_xyz_m'])
        if d > CG_TOL_M:
            cg_diff.append({'part': pid, 'owner': owner_of(g, pid), 'declared': p['cg_xyz_m'],
                            'cad': [round(v, 4) for v in cen], 'diff_mm': round(d * 1000, 1),
                            'mass_g': p.get('mass_g'), 'moment_err_gm': round(d * float(p.get('mass_g') or 0) * 1000, 1)})

    # 4. parts.csv <-> interfaces.json
    csv_issues = []
    for sub in OWNER:
        rows_ = parts_csv(sub)
        if rows_ is None:
            csv_issues.append({'owner': OWNER[sub], 'item': sub, 'msg': 'no parts.csv'})
            continue
        by_id = {r['part_id']: r for r in rows_}
        nodes = {}
        for pid, p in g.parts.items():
            if p.get('subsystem') == sub and p.get('flight', True):     # spares/ground kit: not in the roll-up
                nodes.setdefault(pid if pid in by_id else base_id(pid), []).append(p)
        for bid, ps in sorted(nodes.items()):
            r = by_id.get(bid)
            if r is None:
                csv_issues.append({'owner': OWNER[sub], 'item': bid, 'msg': 'interfaces.json node(s) %s have no parts.csv row'
                                   % ', '.join(sorted(p['id'] for p in ps))})
                continue
            line = float(r['qty'] or 0) * float(r['mass_g'] or 0)
            node = sum(float(p.get('mass_g') or 0) for p in ps)
            if abs(line - node) > MASS_TOL_G:
                csv_issues.append({'owner': OWNER[sub], 'item': bid, 'msg': 'parts.csv %g x %s g = %.1f g, interfaces.json '
                                   '%d node(s) = %.1f g' % (float(r['qty'] or 0), r['mass_g'], line, len(ps), node)})

    by_role = {}
    for sev, code, item, msg in issues:
        role = acting_role(g, sev, code, item, msg)
        by_role.setdefault(role, []).append([sev, code, item, msg])

    snap = {'_note': 'GENERATED by team/A5/integration_check.py; read by team/A5/cad_claims.py', 'date': str(date.today()),
            'modules': [[r[0], bool(r[2])] for r in results],
            'errors': sum(1 for i in issues if i[0] == 'ERROR'), 'warnings': sum(1 for i in issues if i[0] == 'WARN'),
            'skeleton_errors': sum(1 for i in sk_issues if i[0] == 'ERROR'),
            'mass_g': round(M, 1), 'cg_m': [round(v, 5) for v in cg], 'skeleton_mass_g': round(Msk, 1),
            'skeleton_cg_m': [round(v, 5) for v in cg_sk], 'subsystems': rows, 'cg_vs_cad': cg_diff,
            'parts_csv': csv_issues, 'issues_by_role': by_role}
    with open(os.path.join(HERE, 'integration.json'), 'w', encoding='utf-8') as f:
        json.dump(snap, f, indent=1)
    write_md(snap)
    print('integration: %d modules, %d errors, %d warnings; %.1f g, CG x %.4f m (skeleton %.4f); %d CG mismatches, '
          '%d parts.csv mismatches' % (len(results), snap['errors'], snap['warnings'], M, cg[0], cg_sk[0],
                                        len(cg_diff), len(csv_issues)))
    return snap


def write_md(s):
    f = lambda v, n=4: '—' if v is None else ('%.*f' % (n, v))
    L = ['# Integration check (A5)', '',
         'Generated by `python -I redesign/team/A5/integration_check.py` on %s. Do not edit; re-run.' % s['date'], '',
         '| Run | Result |', '|---|---|',
         '| `fusion/check.py` on `redesign/subsystems` | %d modules built, **%d errors, %d warnings** |' % (
             len(s['modules']), s['errors'], s['warnings']),
         '| Assembly (declared masses) | %.1f g, CG (%.4f, %.4f, %.4f) m |' % ((s['mass_g'],) + tuple(s['cg_m'])),
         '| Allocation layout (R3 skeleton) | %.1f g, CG x %.4f m |' % (s['skeleton_mass_g'], s['skeleton_cg_m'][0]),
         '', '## Mass and CG by subsystem', '',
         '| Subsystem | Owner | Allocation g | Declared g | parts.csv g | CG x m | Skeleton CG x m | Share of CG shift mm |',
         '|---|---|---|---|---|---|---|---|']
    for r in s['subsystems']:
        L.append('| `%s` | %s | %s | %.1f | %.1f | %s | %s | %+.2f |' % (
            r['sub'], r['owner'], r['alloc_g'], r['declared_g'], r['csv_g'], f(r['cg_x_m']), f(r['skeleton_cg_x_m']),
            r['dcg_x_mm']))
    L += ['', 'Share of CG shift: this subsystem\'s x-moment change from the skeleton over the assembly mass, less the '
          'effect of its mass change on the skeleton CG; the column sums to the CG shift (%+.1f mm).' % (
              (s['cg_m'][0] - s['skeleton_cg_m'][0]) * 1000), '',
          '## Declared CG vs CAD centroid (> %d mm)' % (CG_TOL_M * 1000), '',
          '| Part | Owner | Mass g | Declared CG m | CAD centroid m | Diff mm | Moment error g·m |', '|---|---|---|---|---|---|---|']
    for c in sorted(s['cg_vs_cad'], key=lambda c: -c['moment_err_gm']):
        L.append('| `%s` | %s | %s | %s | %s | %.1f | %.1f |' % (c['part'], c['owner'], c['mass_g'],
                 ', '.join('%.4f' % v for v in c['declared']), ', '.join('%.4f' % v for v in c['cad']), c['diff_mm'],
                 c['moment_err_gm']))
    L += ['', '## parts.csv vs interfaces.json', '', '| Owner | Item | Problem |', '|---|---|---|']
    L += ['| %s | `%s` | %s |' % (c['owner'], c['item'], c['msg']) for c in s['parts_csv']] or ['| — | — | none |']
    L += ['', '## check.py issues by role', '', '| Role | Severity | Check | Item | Detail |', '|---|---|---|---|---|']
    for role in sorted(s['issues_by_role']):
        for sev, code, item, msg in s['issues_by_role'][role]:
            L.append('| %s | %s | %s | `%s` | %s |' % (role, sev, code, item, msg))
    with open(os.path.join(HERE, 'INTEGRATION.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
