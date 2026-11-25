"""T-077 p6 geometry probe: voxel sections and masses of the as-drawn parts (stub build, same route as t077p5_mass_audit).  Category: geometry arithmetic."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
P5 = os.path.abspath(os.path.join(HERE, '..', 'T077p5_data')); sys.path.insert(0, P5)
sys.argv = [sys.argv[0]] + sys.argv[1:]
import t077p5_mass_audit as A
b, m = A.b, A.m
def build():
    ctx, _, res = b.build_all.build(b.StubBackend(), b.MODEL, os.path.join(b.MODEL, 'modules.txt'), log=lambda *a: None)
    return ctx
if __name__ == '__main__':
    ctx = build(); ids = sys.argv[1:] or ['CGE-006', 'FIN-005-R', 'CGE-013', 'CGE-007-R', 'AVN-010']
    for pid in ids:
        c = ctx.components[pid]; S, lo = A.solid_grid(c, 0.25e-3); h = 0.25e-3
        idx = np.argwhere(S); mn = lo + idx.min(0) * h; mx = lo + (idx.max(0) + 1) * h
        print(pid, 'vol %.3f cm3' % (S.sum() * h ** 3 * 1e6), 'bbox min', np.round(mn * 1e3, 2), 'max', np.round(mx * 1e3, 2), 'listed', m.PARTS[pid]['mass_g'], m.PARTS[pid]['material'][:30])
