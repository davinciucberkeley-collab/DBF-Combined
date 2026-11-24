import sys,os,math
sys.argv=['x']
R='C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/'
sys.path.insert(0,R+'qp/A/cad'); sys.path.insert(0,R+'collision')
import wire_inventory as wi
import importlib.util
spec=importlib.util.spec_from_file_location('cc',R+'collision/collide.py'); cc=importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
ctx,g,r=wi.build_all.build(wi.StubBackend(), os.path.join(wi.CAD,'model'), os.path.join(wi.CAD,'model','modules.txt'), log=lambda *a: None)
ws=[]
for w in ctx.wires:
    blk=getattr(w,'block',None) or {}
    ws.append(dict(id=w.edge,bend=getattr(w,'bend',None) or 5*w.dia, strands=w.strands or [(w.points,w.dia)]))
print(cc.kinks(ws))
