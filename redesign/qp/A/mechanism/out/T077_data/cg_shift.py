"""T-077: which mass changes move the CAD CG aft. Category: illustrative arithmetic on the CAD part table (declared masses at CAD centroids)."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, R + '/qp/A/cad'); sys.path.insert(0, R + '/fusion'); sys.path.insert(0, R + '/interfaces')
import build_all, a_model as m
from backends.stub_backend import StubBackend
M = R + '/qp/A/cad/model'
ctx, _, res = build_all.build(StubBackend(), M, M + '/modules.txt', log=lambda *a: None)
pm = json.load(open(R + '/qp/A/cad/amodel/printed_mass.json'))
rows = []; tot = 0.0; mx = 0.0
for pid, p in m.PARTS.items():
    c = ctx.components.get(pid)
    if c is None: continue
    cg, src = c.cg()
    if cg is None: continue
    tot += p['mass_g']; mx += p['mass_g'] * cg[0]
xcg = mx / tot
# listed (pre-adoption) mass: the value given to P() before the json override = recompute by reading the source default through a flag
import importlib
print('total g %.1f  CG x %.2f mm (this script, declared masses at centroids)' % (tot, xcg * 1e3))
for pid, g in sorted(pm.items(), key=lambda kv: -abs(kv[1])):
    c = ctx.components.get(pid)
    if c is None: continue
    cg, _ = c.cg()
    rows.append((pid, g, cg[0] * 1e3))
# listed masses before: from T-067 merged
lst = {r['id']: r['listed_g'] for r in json.load(open(HERE + '/../T067_data/t067_merged.json'))['rows']}
print('part, listed g, adopted g, x mm, d(m*(x-xcg)) g*mm')
agg = 0.0
for pid, g, x in rows:
    d = g - lst.get(pid, g)
    agg += d * (x - xcg * 1e3)
    if abs(d * (x - xcg * 1e3)) > 40:
        print('%-12s %6.2f %6.2f %7.1f %8.0f' % (pid, lst.get(pid, g), g, x, d * (x - xcg * 1e3)))
print('sum of the shifts %.0f g*mm  = %.1f mm of CG at %.0f g' % (agg, agg / tot, tot))
