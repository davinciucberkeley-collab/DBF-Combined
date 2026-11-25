"""linkage_poses_report.py - tables for T-020 linkage-poses mesh sweep (reads cad/out/report_<tag>.json and the AR-003 analytic CSVs).
    python -I redesign/qp/A/mechanism/linkage_poses_report.py [tag]      -> prints markdown; also writes cad/out/linkage_poses_tables_<tag>.md
Category: interference during motion (mesh clearance vs analytic separating-axis clearance).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.normpath(os.path.join(HERE, '..', 'cad'))
sys.dont_write_bytecode = True
sys.path.insert(0, CAD)
import linkage_poses_a as lp          # noqa: E402

TAG = sys.argv[1] if len(sys.argv) > 1 else 'linkage_poses'
OUT = os.path.join(HERE, 'out')
rep = json.load(open(os.path.join(CAD, 'out', 'report_%s.json' % TAG), encoding='utf-8'))
tol = rep['tol_mm']
L = []
poses = [p for p in rep['poses'] if p.get('delta') is not None]
states = rep['states']
angles = rep['angles']

# 1. pairs over tolerance per state/angle
L += ['### Pairs over %g mm per angle (mesh, all parts in)' % tol, '', '| delta deg | ' + ' | '.join('zj=%s' % s for s in states) + ' |', '|---|' + '---|' * len(states)]
for d in angles:
    row = []
    for s in states:
        pz = next(p for p in poses if p['state'] == s and abs(p['delta'] - d) < 1e-9)
        n = sum(1 for h in pz['hits'] if h['depth_mm'] > tol)
        deep = max([h['depth_mm'] for h in pz['hits']] or [0.0])
        row.append('%d (deepest %.3f)' % (n, deep))
    L.append('| %+g | %s |' % (d, ' | '.join(row)))
L.append('')


INVALID = ('WNG-001', 'WNG-006')      # parts whose pockets / slots are cutters, not faces: an unsigned surface distance to them is not a clearance


def pkey(k):
    a, b = k.split('|')
    return tuple(sorted((lp.part_key(a), lp.part_key(b))))


# 2. min clearance per part pair (mesh) and like-for-like comparison with the analytic sweep at body level
def table(state):
    best = {}
    byang = {}
    for pz in poses:
        if pz['state'] != state:
            continue
        for k, v in pz['clear'].items():
            c = -v['penetration_mm'] if 'penetration_mm' in v else v['d_mm']
            key = pkey(k)
            if any(x in INVALID for x in key):
                continue
            byang.setdefault(key, {})
            byang[key][pz['delta']] = min(byang[key].get(pz['delta'], 1e9), c)
            if key not in best or c < best[key][0]:
                best[key] = (c, pz['delta'], v['same_group'])
    return best, byang


A2B = {'arm': ('MEC-002', 'servo arm'), 'keeper spacer': ('MEC-008', 'keeper spacer'), 'keeper bridge': ('MEC-008', 'keeper bridge'),
       'rod': ('MEC-003', 'pushrod'), 'rod Z-bend pin': ('MEC-003', 'rod Z-bend leg'), 'clevis sleeve': ('MEC-003', 'clevis sleeve'),
       'clevis cheek -1': ('MEC-003', 'clevis cheek'), 'clevis cheek +1': ('MEC-003', 'clevis cheek'), 'horn blade': ('MEC-004', 'horn'),
       'horn rib': ('MEC-004', 'horn'), 'clevis pin': ('MEC-005', 'clevis pin'), 'elevon slab': ('WNG-006', 'elevon'),
       'servo case': ('MEC-001', 'servo case'), 'servo boot': ('MEC-001', 'servo lead strain-relief boot'),
       'pocket wall fore': ('WNG-001', 'core'), 'pocket wall side outboard': ('WNG-001', 'core'),
       'pocket wall side inboard': ('WNG-001', 'core'), 'core aft block': ('WNG-001', 'core')}


def analytic_solid_pairs(state):
    import csv
    suf = '' if state == 'mid' else '_z' + state
    out = {}
    with open(os.path.join(OUT, 'linkage_sweep_collision%s.csv' % suf), newline='') as f:
        for r in csv.DictReader(f):
            if r['side'] == 'R':
                out.setdefault((r['part_a'], r['part_b']), {})[float(r['delta_deg'])] = float(r['separation_mm (negative = penetration)'])
    return out


def mesh_body_min(state, pa, na, pb, nb):
    """mesh min distance per angle (side R pids) between bodies whose names start with na (part pa) and nb (part pb)"""
    res = {}
    for pz in poses:
        if pz['state'] != state:
            continue
        for k, v in pz['clear'].items():
            p, q = k.split('|')
            if not (p.endswith('-R') and q.endswith('-R') or q.startswith('WNG-001') and p.endswith('-R') or p.startswith('WNG-001') and q.endswith('-R')):
                continue
            for bk, d in v['bodies'].items():
                x, y = bk.split(' || ')
                for (pp, nn), (qq, mm) in (((pa, na), (pb, nb)), ((pb, nb), (pa, na))):
                    if lp.part_key(p) == pp and x.startswith(nn) and lp.part_key(q) == qq and y.startswith(mm):
                        res[pz['delta']] = min(res.get(pz['delta'], 1e9), d)
    return res


for s in states:
    best, byang = table(s)
    L += ['### Minimum mesh clearance per part pair, zj=%s (mm; negative = penetration depth from the hit list; only pairs under 2 mm)' % s, '',
          '| Part pair | mesh min mm | at delta | same group (constant) | declared contact |', '|---|---|---|---|---|']
    for key, (c, dl, same) in sorted(best.items(), key=lambda kv: kv[1][0]):
        if c > 2.0:
            continue
        L.append('| %s / %s | %.3f | %+g | %s | %s |' % (key[0], key[1], c, dl, 'yes' if same else 'no', lp.DECLARED.get(key, '-')))
    L.append('')
    ana = analytic_solid_pairs(s)
    L += ['### Mesh vs analytic (AR-003), like for like at body level, zj=%s, side R, chosen angles (mm)' % s, '',
          '| Analytic pair (solids) | CAD bodies compared | analytic min | at delta | mesh min | at delta | max abs(mesh - analytic) over angles | note |', '|---|---|---|---|---|---|---|---|']
    rows = []
    for (a_, b_), v in ana.items():
        if a_ not in A2B or b_ not in A2B or A2B[a_][0] in INVALID or A2B[b_][0] in INVALID:
            continue
        sel = {d: x for d, x in v.items() if any(abs(d - q) < 1e-9 for q in angles)}
        if not sel or min(sel.values()) > 3.0:
            continue
        (pa, na), (pb, nb) = A2B[a_], A2B[b_]
        mm = mesh_body_min(s, pa, na, pb, nb)
        ad, av = min(sel.items(), key=lambda t: t[1])
        if mm:
            md, mv = min(mm.items(), key=lambda t: t[1])
            common = [d for d in sel if d in mm]
            mx = max(abs(mm[d] - sel[d]) for d in common) if common else float('nan')
            rows.append((av, '| %s / %s | %s %s / %s %s | %.3f | %+g | %.3f | %+g | %.3f | %s |' % (a_, b_, pa, na, pb, nb, av, ad, mv, md, mx,
                         'analytic hull bound' if mv > av + 0.02 else '')))
        else:
            rows.append((av, '| %s / %s | %s %s / %s %s | %.3f | %+g | > 3 (none within cap) | - | - | |' % (a_, b_, pa, na, pb, nb, av, ad)))
    L += [r for _a, r in sorted(rows)]
    L.append('')

# 3. per-angle clearance of the principal pairs, state mid
PRINC = [('MEC-002', 'MEC-003'), ('MEC-003', 'MEC-008'), ('MEC-003', 'MEC-004'), ('MEC-004', 'MEC-005'), ('MEC-001', 'MEC-003'),
         ('MEC-001', 'MEC-002'), ('MEC-002', 'MEC-008'), ('HWC-002', 'MEC-002'), ('MEC-003', 'MEC-005')]
for s in states:
    best, byang = table(s)
    L += ['### Per-angle clearance, zj=%s (mm, min of R and L; negative = penetration)' % s, '', '| delta | ' + ' | '.join('%s / %s' % k for k in PRINC) + ' |', '|---|' + '---|' * len(PRINC)]
    for d in angles:
        L.append('| %+g | %s |' % (d, ' | '.join('%.3f' % byang[k][d] if k in byang and d in byang[k] else '>2' for k in PRINC)))
    L.append('')
txt = '\n'.join(L)
open(os.path.join(CAD, 'out', 'linkage_poses_tables_%s.md' % TAG), 'w', encoding='utf-8').write(txt)
print(txt)
