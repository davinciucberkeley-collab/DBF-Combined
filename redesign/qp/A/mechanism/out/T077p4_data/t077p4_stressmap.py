"""T-077 part 4 step 1a: von Mises envelope map of the G1 Al hub (no pockets) for choosing the lightening pockets.  CATEGORY: FEA post-processing (reuses the T-076d G1 model, partition B, MS 1.1).
Per hub Gauss point: envelope vm over the RB sets (x DAF 1.97, worst pad zeta) and over the D-1 sets (/ r_m 0.84, D-223 rule), plus volume weight and coordinates.  Saved to fea/stressmap_<tag>.npz.
    python -I t077p4_stressmap.py --tag g1base [--geom G1] [--p k=v ...]"""
import argparse, os, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.abspath(os.path.join(HERE, '..', 'T076d_data')); sys.path.insert(0, D)
import t076d_step4_tubes as T4
import numpy as np
H, J = T4.H, T4.J
FEA = os.path.join(HERE, 'fea'); os.makedirs(FEA, exist_ok=True)
T4.FEA = FEA
DAF, RM = 1.97, 0.84

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tag', required=True); ap.add_argument('--geom', default='G1'); ap.add_argument('--p', nargs='*', default=[]); a = ap.parse_args()
    H.GEO.update(T4.BASE); H.GEO['BLK_AFT'] = 10.0   # T-077 p4: the FEA GEO reads W.BLK_AFT from the CAD; T-077 p3 octagon (apothem 8.0) made it 9.5 and silently moved the block aft end 24.0 -> 23.5 (collar 44.5, RBE3 patch on a 1.5 mm annulus): pin it to 10.0 = the T-076d geometry (block to the tray face x 24, collar 24..45)
    if a.geom == 'G1': H.GEO.update(T4.G1)
    for kv in a.p:
        k, v = kv.split('='); H.GEO[k] = float(v)
    H.FA.E_PETG, H.FA.NU_PETG = T4.E_AL, T4.NU_AL; H.FA.OUT = FEA; H.OUT = FEA
    t0 = time.time(); res = H.run(0, a.tag)
    stubs = T4.make_stubs(); sets = T4.build_sets(stubs)
    hub = res['M'] == 0; S = res['S']; Sh = S[:, hub].reshape(S.shape[0], -1, 6); xh = res['xg'][hub].reshape(-1, 3)
    w = J.gauss_weights(H.FA, res['X'], res['E'], hub)
    edge = J.corner_nodes(res['X'], res['E'], res['M']); keep = J.exclusion_mask(res['X'], xh, edge, T4.EXCL)
    env = {}
    for name, (C, labs) in sets.items():
        C = np.asarray(C); m = np.zeros(len(xh))
        for ci in range(0, len(C), 8):
            vm = J.von_mises(np.einsum('cb,bgk->cgk', C[ci:ci + 8], Sh)); m = np.maximum(m, vm.max(0))
        env[name] = m; print(name, 'max %.1f max excl %.1f' % (m.max(), m[keep].max()), flush=True)
    rb = np.max([v for k, v in env.items() if k.startswith('RB')], axis=0) * DAF
    d1 = np.max([v for k, v in env.items() if k.startswith('D1')], axis=0) / RM
    np.savez_compressed(os.path.join(FEA, 'stressmap_%s.npz' % a.tag), xh=xh, w=w, keep=keep, rb=rb, d1=d1, hub_vol=res['hub_vol'])
    print('hub vol %.0f mm3, RF (139.1 / max excl of max(rb, d1)): %.3f ; wall %.0f s' % (res['hub_vol'], 139.1 / max(rb[keep].max(), d1[keep].max()), time.time() - t0))

if __name__ == '__main__': main()
