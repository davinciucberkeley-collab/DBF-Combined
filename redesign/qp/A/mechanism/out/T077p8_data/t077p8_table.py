"""T-077 p8: strength table (part, row, RB, x1.5, x2.23, verdict at x2.23 = max(DAF, 1.5)) and per-part minimum from strength_adopted.json -> strength_table_p8.md.
Category: hand calculation on the rigid-body demand (see t077p8_path.py)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); d = json.load(open(os.path.join(H, 'strength_adopted.json')))
out = ['Geometry: %s' % d['geom'], '', '| Part | Row | RB | x1.5 | x2.23 | Verdict at x2.23 | Governing case |', '|---|---|---|---|---|---|---|']
mins = {}
for r in sorted([r for r in d['rows'] if r['cls'] != 'record'], key=lambda r: (r['part'], r['rb'])):
    v = r['verdict'].replace('FAIL', '**FAIL**')
    out.append('| %s | %s | %.2f | %.2f | %.2f | %s | %s |' % (r['part'], r['row'].replace('|', '/'), r['rb'], r['x15'], r['x223'], v, r['case']))
    if r['cls'] == 'RF': mins[r['part']] = min(mins.get(r['part'], 9e9), r['x223'])
out += ['', '| Record | Value | Case |', '|---|---|---|'] + ['| %s: %s | %.2f | %s |' % (r['part'], r['row'].replace('|', '/'), r['value'], r['case']) for r in d['rows'] if r['cls'] == 'record']
out += ['', '| Part | min RF at x2.23 (RF class only) |', '|---|---|'] + ['| %s | %.2f |' % (k, v) for k, v in sorted(mins.items())]
open(os.path.join(H, 'strength_table_p8.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out[-12:]))
