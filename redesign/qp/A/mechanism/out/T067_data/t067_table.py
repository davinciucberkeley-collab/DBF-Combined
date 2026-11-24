"""T-067 combine: 0.25 mm rows (all printed parts except the hub) + 0.50 mm hub row -> table, new CAD basic mass, gate predictions.
Run: python -I t067_table.py   (reads the two json files and t067_dims.json in this folder; arithmetic only)"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
fine = {r['id']: r for r in json.load(open(os.path.join(HERE, 't067_rows_h0.25_only.json')))['rows']}
coarse = {r['id']: r for r in json.load(open(os.path.join(HERE, 't067_rows_h0.50_all.json')))['rows']}
lf = {r['id']: r for r in json.load(open(os.path.join(HERE, 't067_rows_h0.25_lean_only.json')))['rows']}
lf.update({r['id']: r for r in json.load(open(os.path.join(HERE, 't067_rows_h0.50_lean_only.json')))['rows']})
dims = json.load(open(os.path.join(HERE, 't067_dims.json')))
rows = []
for pid, c in coarse.items():
    r = dict(fine.get(pid, c))
    r['h_mm'] = 0.25 if pid in fine else 0.50
    r['solid_g_050'] = c['solid_g']
    r['computed_g_050'] = c['computed_g']
    r['bbox'] = dims[pid]['bbox_mm']
    r['adopt_g'] = r['listed_g'] if pid.startswith('WNG-009') else r['computed_g']   # damper stator: listed 2.0 g includes silicone fluid + strips (not in CAD)
    r['lean_g'] = r['listed_g'] if pid.startswith('WNG-009') else lf[pid]['computed_g']
    rows.append(r)
BASIC_NOW = 1274.3                     # CAD basic mass, g (task brief: T-022b +1.0 g, T068 decision s11)
tot = lambda k: sum(r[k] for r in rows)
L, S, Cc, A = tot('listed_g'), tot('solid_g'), tot('computed_g'), tot('adopt_g')
out = dict(n_parts=len(rows), listed_g=L, solid_g=S, computed_g=Cc, adopt_g=A, delta_adopt=A - L, delta_solid=S - L)
GATE = 1470.0
def flat(basic): return basic * 1.1174 + 0.032 * GATE
def itemised(basic, d, g=0.20): return basic + (145.0 + g * d) + 48.0 if False else None
out['basic_now'] = BASIC_NOW
LEAN = sum(r['lean_g'] for r in rows)
out['lean_g'] = LEAN
for name, d in (('as_listed', 0.0), ('lean_basis', LEAN - L), ('computed_basis', A - L), ('solid_cad', S - L)):
    b = BASIC_NOW + d
    out[name] = dict(basic=b, flat=flat(b), flat_margin=GATE - flat(b),
                     itemised_g20=b + 145.0 + 0.20 * d + 48.0, itemised_g10=b + 145.0 + 0.10 * d + 48.0)
# by class and by group
grp = {}
for r in rows:
    g = r['id'].split('-')[0] + ('-' + r['id'].split('-')[1] if r['id'][:3] in ('GER', 'CGE', 'FIN', 'WNG', 'AVN', 'HRN', 'MEC') else '')
    grp.setdefault(r['id'][:3], [0, 0, 0])
    grp[r['id'][:3]][0] += r['listed_g']; grp[r['id'][:3]][1] += r['adopt_g']; grp[r['id'][:3]][2] += r['solid_g']
out['by_prefix'] = grp
json.dump(dict(summary=out, rows=rows), open(os.path.join(HERE, 't067_merged.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
for r in rows:
    print('| %s | %.2f | %.2f | %s | %.2f | %+.2f | %.2f | %.2f |' % (r['id'], r['listed_g'], r['solid_g'], r['cls'], r['computed_g'], r['adopt_g'] - r['listed_g'], abs(r['computed_g'] - r['computed_g_050']), r['lean_g']))
