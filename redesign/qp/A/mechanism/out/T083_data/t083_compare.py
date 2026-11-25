"""T-083: D-226 rows re-judged on the T-083 demand, side by side with T-077 p8 (strength_adopted.json, 1.705 kg label / 1.64 kg sim, Fp 30 N).
Category: hand calculation on the rigid-body demand (t083_path.py = t077p8_path.py method). Reads strength_<tag>.json; writes strength_table_t083.md.
python -I t083_compare.py"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
P8 = json.load(open(os.path.join(H, '..', 'T077p8_data', 'strength_adopted.json')))
TAGS = [('all', 'T-083 all zeta'), ('z002', 'zeta 0.02'), ('z005', 'zeta 0.05'), ('z010', 'zeta 0.10'), ('all_rib1412', 'all zeta, rib 14x12'), ('z002_rib1412', 'zeta 0.02, rib 14x12')]
D = {t: {(r['part'], r['row']): r for r in json.load(open(os.path.join(H, 'strength_%s.json' % t)))['rows']} for t, _ in TAGS}
p8 = {(r['part'], r['row']): r for r in P8['rows']}
keys = [k for k in D['all'] if D['all'][k]['cls'] != 'record']
keys.sort(key=lambda k: (k[0], D['all'][k]['x223']))
out = ['# T-083 strength rows at x2.23 (D-223 DAF, KF 1.725, KP 2.156; RF >= 1.0 required for class RF; integrity rows outside the minimum)', '',
       'Demand: T-083 re-run (t083_demand.py): 1.913 kg simulated (the p6 demand was simulated at 1.64 kg, see T083_report s5), tallied CG 24.41 mm (after the 3 mm cage shift), pad Fp 36 N / 24 mm, 23 cases x zeta 0.02 / 0.05 / 0.10 x mu 0.40 / 0.30.', '',
       '| Part | Row | class | p8 x2.23 | ' + ' | '.join(l for _, l in TAGS) + ' | verdict (all zeta, 25x23) |', '|---' * (5 + len(TAGS)) + '|']
mins = {}
for k in keys:
    r = D['all'][k]
    vals = []
    for t, _ in TAGS:
        q = D[t].get(k)
        vals.append('%.2f' % q['x223'] if q else '-')
    old = p8.get(k)
    v = r['verdict']
    if r['cls'] == 'RF' and r['x223'] < 1.0:
        v = '**FAIL**'
    out.append('| %s | %s | %s | %s | %s | %s |' % (k[0], k[1].replace('|', '/'), r['cls'], '%.2f' % old['x223'] if old else '-', ' | '.join(vals), v))
    if r['cls'] == 'RF':
        for t, _ in TAGS:
            q = D[t].get(k)
            if q: mins.setdefault(t, {}); mins[t][k[0]] = min(mins[t].get(k[0], 9e9), q['x223'])
out += ['', '| Part | ' + ' | '.join(l for _, l in TAGS) + ' |', '|---' * (1 + len(TAGS)) + '|']
for part in sorted(mins['all']):
    out.append('| %s | %s |' % (part, ' | '.join('%.2f' % mins[t].get(part, float('nan')) for t, _ in TAGS)))
out += ['', '| Record (RB) | p8 | T-083 all | zeta 0.02 | zeta 0.10 | case (all) |', '|---|---|---|---|---|---|']
for k, r in D['all'].items():
    if r['cls'] == 'record':
        o = p8.get(k)
        out.append('| %s: %s | %s | %.2f | %.2f | %.2f | %s |' % (k[0], k[1], '%.2f' % o['value'] if o else '-', r['value'], D['z002'][k]['value'], D['z010'][k]['value'], r['case']))
open(os.path.join(H, 'strength_table_t083.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
