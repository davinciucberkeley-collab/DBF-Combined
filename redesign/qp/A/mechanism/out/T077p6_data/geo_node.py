import os, sys, numpy as np, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geo_probe as G
A = G.A
ctx = G.build(); h = 0.25e-3; out = {}
for pid in ['CGE-006', 'FIN-005-R']:
    c = ctx.components[pid]; S, lo = A.solid_grid(c, h); out[pid] = (S, lo)
    print(pid, S.shape)
pickle.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fea', 'node_cradle_vox.pkl'), 'wb'))
S, lo = out['CGE-006']
def sl(S, lo, axis, v_mm, step=1.0):
    k = int(round((v_mm * 1e-3 - lo[axis]) / h)); s = np.take(S, k, axis=axis)
    return s
# x-slices: y (rows) vs z
for xmm in (35, 45, 52, 60, 68):
    s = sl(S, lo, 0, xmm); ys = np.where(s.any(1))[0]; zs = np.where(s.any(0))[0]
    print('x=%d: area %.1f mm2, y %.1f..%.1f, z %.1f..%.1f' % (xmm, s.sum() * h * h * 1e6, (lo[1] + ys.min() * h) * 1e3, (lo[1] + (ys.max() + 1) * h) * 1e3, (lo[2] + zs.min() * h) * 1e3, (lo[2] + (zs.max() + 1) * h) * 1e3))
# y-slices : x vs z occupancy by columns at y = 0, 12, 14.5, 16, 17.5
for ymm in (0, 9, 12, 14, 16, 17.5):
    s = sl(S, lo, 1, ymm); print('y=%.1f: area %.1f mm2' % (ymm, s.sum() * h * h * 1e6), 'x extent', np.round([(lo[0] + np.where(s.any(1))[0].min() * h) * 1e3, (lo[0] + (np.where(s.any(1))[0].max() + 1) * h) * 1e3], 2) if s.any() else '-')
