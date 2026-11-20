"""T-076 row 1: builds fea_hub_c6.py = a copy of structures/fea_hub.py (unmodified, committed) with five textual patches
(collar box, mesh-refine box, OUT dir, HERE, new main).  python -I make_fea_hub_c6.py"""
import os, re
D = os.path.dirname(os.path.abspath(__file__))
S = os.path.abspath(os.path.join(D, '..', '..', '..', 'structures'))
t = open(os.path.join(S, 'fea_hub.py'), encoding='utf8').read()
def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (a, t.count(a)); t = t.replace(a, b)
rep("HERE = os.path.dirname(os.path.abspath(__file__))", "HERE = r'%s'" % S)
rep("OUT = FA.OUT\n", "OUT = os.path.join(r'%s', 'fea'); FA.OUT = OUT   # T-076: committed out_fea untouched\n" % D)
rep("GEO = dict(XA=-6.5,", "GEO = dict(COL_E=0.0, COL_Y=12.0, COL_ZLO=-16.0, COL_ZHI=8.0, XA=-6.5,")   # collar: extension length, half width y, z range (hub frame mm)
rep("    if g.get('FIL', 0) > 0:\n        hub = staged_fillet",
    "    if g['COL_E'] > 0:   # T-076 C6 collar (T-071b H3): box from the block aft face\n        hub_parts.append((3, occ.addBox(xb1, -g['COL_Y'], g['COL_ZLO'], g['COL_E'], 2 * g['COL_Y'], g['COL_ZHI'] - g['COL_ZLO'])))\n    if g.get('FIL', 0) > 0:\n        hub = staged_fillet")
rep("(xb1 - 1, g['X_HUB1'] + 1, -9, 9, -9, 9)", "((xb1 - 1, g['X_HUB1'] + 1, -13, 13, -17, 9) if g['COL_E'] > 0 else (xb1 - 1, g['X_HUB1'] + 1, -9, 9, -9, 9))")
rep("    RHS = np.column_stack(basis)\n", "    hubn = np.unique(E[M == 0]); pl = hubn[(np.abs(X[hubn, 0] - GEO['X_HUB1']) < 0.05) & (np.hypot(X[hubn, 1], X[hubn, 2] - GEO['BR_Z']) > GEO['BR_RO'] + 0.05)]\n    print('hub aft-face nodes for the hub-group load: %d' % len(pl), flush=True)\n    refp = np.array([24.0, 0.0, GEO['BR_Z']])\n    for k in range(6):\n        F = np.zeros(3); Mo = np.zeros(3); (F if k < 3 else Mo)[k % 3] = 1.0\n        f = np.zeros((len(X), 3)); f[pl] = FA.rbe3_loads(X, pl, F, Mo, refp); basis.append(f.ravel()[free])\n    RHS = np.column_stack(basis)\n")
rep("    for j in range(len(basis)):\n        st = sts[j // 6]", "    for j in range(24):\n        st = sts[j // 6]")
i = t.index("if __name__ == '__main__':")
t = t[:i] + "sys.path.insert(0, r'%s')\nfrom t076_main import main   # noqa: E402\nif __name__ == '__main__':\n    main(sys.modules[__name__])\n" % D
open(os.path.join(D, 'fea_hub_c6.py'), 'w', encoding='utf8').write(t)
print('written fea_hub_c6.py', len(t))
