"""T-077 p7: strength table (part, row, RB, x1.5, x1.97, x2.23, verdict at x2.23 = max(DAF, 1.5) for saddle / bridge / strut / clamp rows) from strength_adopted.json. Output strength_table_p7.md.
Category: hand calculation on rigid-body demand (see t077p7_strength.py)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(H, 'strength_adopted.json')))
out = ['Geometry (mm): %s; strut %s' % (d['geometry'], d['strut']), '',
       '| Part | Row | RB | x1.5 | x1.97 | x2.23 | Verdict at x2.23 | Governing case |', '|---|---|---|---|---|---|---|---|']
for r in sorted(d['rows'], key=lambda r: (r['part'], r['rb'])):
    if 'shown only' in r['row']: continue
    v = r['verdict'].replace('integrity / shown', 'integrity class (outside the RF minimum)')
    if v == 'FAIL': v = '**FAIL**'
    out.append('| %s | %s | %.2f | %.2f | %.2f | %.2f | %s | %s |' % (r['part'], r['row'].replace('|', '/'), r['rb'], r['x15'], r['x197'], r['x223'], v, r['case']))
open(os.path.join(H, 'strength_table_p7.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
