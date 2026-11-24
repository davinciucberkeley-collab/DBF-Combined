import sys,os,json
import numpy as np
sys.path.insert(0,'C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/mechanism/out/T067_data/../../../cad')
import build_a as b, a_model as m
ctx,_,res=b.build_all.build(b.StubBackend(), b.MODEL, os.path.join(b.MODEL,'modules.txt'), log=lambda *a: None)
out={}
for pid,p in m.PARTS.items():
    if 'PETG' in p['material'] and 'lead' not in p['material']:
        c=ctx.components[pid]
        pts=np.array([q for s in c.shapes for q in s.points()])
        out[pid]=dict(bbox_mm=[round(float(x),1) for x in (pts.max(0)-pts.min(0))*1000], shapes=[ (s.kind,(s.name or '')[:60]) for s in c.shapes][:8], ncuts=len(c.cuts))
json.dump(out,open('C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/mechanism/out/T067_data/t067_dims.json','w'),indent=1)
for k,v in out.items(): print(k,v['bbox_mm'],v['ncuts'])
