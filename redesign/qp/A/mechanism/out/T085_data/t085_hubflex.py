"""T-085 (FEA, solid tet10): stub-end flexibility of the hub, from the existing D-209 hub FEA mesh (structures/out_fea/hub_mesh_L0_d209_*.npz, fea_hub.py, same
elements, tie-bonded tube / sleeve / pins, bridge bore fixed 40 mm aft of the block). The hub FEA's saved results are stresses only (no displacement), so the
stiffness is re-derived here: unit generalised loads (RBE3 as fea_hub.run) at the four stub ends (s = 60 mm, mm / N frame) and at a hub-centre master (RBE3 over the
centre-block nodes); Fl = RHS^T U (30 x 30, generalised displacement = work conjugate of the load at the point: translation mm, rotation rad).
Hub block material: PETG (as the d209 run: soft bound) or 6061-T6 (E 69 GPa, nu 0.33, repo AL basis; D-209 geometry, which is NOT the drawn D-220 octagonal sleeve).
python -I t085_hubflex.py petg|al6061      (about 5-8 min each, MATLAB CHOLMOD through fea_arm.solve)"""
import os, sys, json, time
import numpy as np
sys.dont_write_bytecode = True
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'structures'))
sys.path.insert(0, S)
import fea_hub as FH
FA = FH.FA
HERE = os.path.dirname(os.path.abspath(__file__))
mat = sys.argv[1] if len(sys.argv) > 1 else 'petg'
geo = json.load(open(os.path.join(FH.OUT, 'hub_result_L0_d209.json')))['geo']
FH.GEO.update(geo); G = FH.GEO
import hashlib
gh = hashlib.md5(json.dumps(G, sort_keys=True).encode()).hexdigest()[:8]
mp = os.path.join(FH.OUT, 'hub_mesh_L0_d209_%s.npz' % gh)
print('mesh', mp, os.path.exists(mp), flush=True)
d = np.load(mp); X, E, M = d['X'], d['E'], d['M']
U = FH.axes()
Rx = np.array([[0, 1.0, 0], [-1.0, 0, 0], [0, 0, 1.0]])
D_br = FH.to_voigt(np.einsum('pi,qj,rk,sl,ijkl->pqrs', Rx, Rx, Rx, Rx, FH.to_tensor(FA.D_ti_y())))
D_hub = FA.D_iso(FA.E_PETG, FA.NU_PETG) if mat == 'petg' else FA.D_iso(69000.0, 0.33)
Ds = [D_hub, FH.D_tube(U['A']), FH.D_tube(U['B']), D_br, FA.D_iso(G['E_PIN'], 0.3)]
t0 = time.time()
K, Bs, dof, dets = FA.assemble(X, E, M, Ds)
fix = FH.fixed_nodes(X); fd = np.zeros(3 * len(X), bool); fd[(3 * fix[:, None] + np.arange(3)).ravel()] = True
free = np.where(~fd)[0]; Kf = K[free][:, free].tocsc()
basis, pts = [], []
for st in ('UR', 'LL', 'LR', 'UL'):
    nodes = FH.end_nodes(X, st); e = FH.stub_end(st); pts.append(e)
    for k in range(6):
        F = np.zeros(3); Mo = np.zeros(3); (F if k < 3 else Mo)[k % 3] = 1.0
        f = np.zeros((len(X), 3)); f[nodes] = FA.rbe3_loads(X, nodes, F, Mo, e); basis.append(f.ravel()[free])
# hub-centre master: M == 0 nodes inside the centre block (|y| <= CB, z in [BLK_Z - 10, BLK_Z + 10], x in [-14, X_HUB1])
hn = np.where((M[:, None] == 0).any(1) if False else np.isin(np.arange(len(X)), np.unique(E[M == 0])) & (np.abs(X[:, 1]) <= G['CB']) & (np.abs(X[:, 2] - G['BLK_Z']) <= 10.0) & (X[:, 0] >= -14.0) & (X[:, 0] <= G['X_HUB1']))[0]
print('hub master nodes', len(hn), flush=True); e0 = np.zeros(3); pts.append(e0)
for k in range(6):
    F = np.zeros(3); Mo = np.zeros(3); (F if k < 3 else Mo)[k % 3] = 1.0
    f = np.zeros((len(X), 3)); f[hn] = FA.rbe3_loads(X, hn, F, Mo, e0); basis.append(f.ravel()[free])
RHS = np.column_stack(basis)
Uf = FA.solve(Kf, RHS)
Fl = RHS.T @ Uf
Xb = X[fix].mean(0)
np.savez(os.path.join(HERE, 'hubflex_%s.npz' % mat), Fl=Fl, pts=np.array(pts), fix_centroid=Xb, nfix=len(fix), nel=len(E))
asym = np.abs(Fl - Fl.T).max() / np.abs(Fl).max()
print('mat %s: Fl symmetry err %.2e, diag UR tip (mm/N, mm/N, mm/N, rad/Nmm..):' % (mat, asym), np.diag(Fl)[:6], 'fixed centroid', Xb, '%.0f s' % (time.time() - t0), flush=True)
