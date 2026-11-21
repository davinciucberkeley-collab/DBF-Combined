
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
