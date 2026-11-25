import sys,os,math
import numpy as np
sys.argv=['x']
sys.path.insert(0,'C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/cad')
import wire_inventory as wi
ctx,graph,results=wi.build_all.build(wi.StubBackend(), os.path.join(wi.CAD,'model'), os.path.join(wi.CAD,'model','modules.txt'), log=lambda *a: None)
def dense(line):
    out=[]
    for a,b in zip(line,line[1:]):
        n=max(1,int(math.dist(a,b)/0.0003))
        for k in range(n): out.append([a[j]+(b[j]-a[j])*k/n for j in range(3)])
    out.append(list(line[-1])); return np.array(out)
W=[]
for w in ctx.wires:
    for line,d in (w.strands or [(w.points,w.dia)]):
        W.append((w.edge,d/2,dense(line)))
res={}
for i in range(len(W)):
    for j in range(i+1,len(W)):
        if W[i][0]==W[j][0]: continue
        a,b=W[i][2],W[j][2]
        # bbox prune
        if (a.min(0)-b.max(0)).max()>0.01 or (b.min(0)-a.max(0)).max()>0.01: continue
        d=np.sqrt(((a[:,None,:]-b[None,:,:])**2).sum(-1)).min()-W[i][1]-W[j][1]
        k=tuple(sorted((W[i][0],W[j][0])))
        res[k]=min(res.get(k,9),d)
for k,v in sorted(res.items(), key=lambda kv: kv[1]):
    if v<0.002: print(k, round(v*1e3,2),'mm')
