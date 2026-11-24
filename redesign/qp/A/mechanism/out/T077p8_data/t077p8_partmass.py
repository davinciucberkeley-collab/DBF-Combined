"""T-077 p8: per-part mass (g) and centroid (mm) of a concept A CAD tree by stub build (geometry arithmetic). python -I t077p8_partmass.py <cad_dir> <out.json ABSOLUTE path>; used on git HEAD (p7, extracted with git archive into the scratchpad) and on the p8 tree for the CG delta table P8.4"""
import os, sys, json
CAD = os.path.abspath(sys.argv[1]); sys.path.insert(0, CAD); os.chdir(CAD); sys.dont_write_bytecode = True
import build_a, build_all, a_model as m
from backends.stub_backend import StubBackend
ctx, _, res = build_all.build(StubBackend(), build_a.MODEL, os.path.join(build_a.MODEL, 'modules.txt'), log=lambda *a: None)
out = {}
for pid, p in m.PARTS.items():
    c = ctx.components.get(pid)
    cg = None
    if c is not None and c.shapes:
        cg = c.cg()[0]
    out[pid] = dict(g=p['mass_g'], x=(cg[0] * 1e3 if cg else None), y=(cg[1] * 1e3 if cg else None), z=(cg[2] * 1e3 if cg else None))
json.dump(out, open(sys.argv[2], 'w'), indent=0)
print(len(out), 'parts, total %.1f g' % sum(v['g'] for v in out.values()))
