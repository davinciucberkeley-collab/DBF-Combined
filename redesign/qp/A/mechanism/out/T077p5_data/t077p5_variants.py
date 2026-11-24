"""T-077 p5: CG / mass / window of the four D-221 variants (clamshell on/off x node on/off), geometry arithmetic + the prop_a EST model. Each variant is built in its own process (env P5_VARIANT).
   python -I t077p5_variants.py            (prints a table; no file is written into the CAD tree)"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CHILD = r'''
import os, sys, json
A = sys.argv[1]; sys.path.insert(0, os.path.join(A, 'cad')); sys.path.insert(0, A); sys.dont_write_bytecode = True
os.chdir(os.path.join(A, 'cad'))
import build_a as b, a_model as m
old = json.load(open(sys.argv[2]))                      # part-4 printed masses (for the parts whose geometry reverts)
v = os.environ.get('P5_VARIANT', '')
if v in ('noclam', 'none'):
    for s in 'RL': m.PARTS['FIN-005-' + s]['mass_g'] = old['FIN-005-' + s]
if v in ('nonode', 'none'): m.PARTS['CGE-006']['mass_g'] = old['CGE-006']
cg = b.centroids(); M = 0; Mx = 0
for pid, p in m.PARTS.items():
    c = cg.get(pid) or p.get('cg'); M += p['mass_g']; Mx += p['mass_g'] * c[0]
print(json.dumps(dict(M=M, cg=Mx / M * 1000)))
'''
open(os.path.join(HERE, '_child_variant.py'), 'w').write(CHILD)
sys.path.insert(0, A); sys.dont_write_bytecode = True
os.chdir(A)
import prop_a as P
NP, C = 40.7, 245.0
UND = [(12.2, 283.1), (7.0, 298.1)]
rows = []
for v in ('', 'noclam', 'nonode', 'none'):
    env = dict(os.environ); env['P5_VARIANT'] = v
    r = subprocess.run([sys.executable, '-I', os.path.join(HERE, '_child_variant.py'), A, os.path.join(HERE, 'printed_mass_p4_backup.json')], capture_output=True, text=True, env=env)
    j = json.loads(r.stdout.strip().splitlines()[-1]); M, cg = j['M'], j['cg']
    M2 = M + sum(u[0] for u in UND); cg2 = (M * cg + sum(u[0] * u[1] for u in UND)) / M2
    mp = M2 / 1000 * 1.1174 + 0.032 * 1.47
    sg = P.tw_state(14.92, P.cap_sched(14.92, mp), mp, 0.93)[0] * 0.97
    fr = P.tw_state(16.8, P.cap_sched(16.8, mp), mp, 0.93)[0] * 0.97
    rows.append((v or 'both (D-221)', M, cg, M2, cg2, 100 * (NP - cg2) / C, mp, fr, sg, P.window_pct(sg)))
    print('variant %-14s drawn %.1f g CG %.2f | tallied %.1f g CG %.2f SM %.2f %% | predicted %.4f kg, T/W fresh(dl) %.3f sag(dl) %.3f, window %.2f %% (with download)' % rows[-1], flush=True)
