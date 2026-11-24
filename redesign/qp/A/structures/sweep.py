import sys, math; sys.path.insert(0,'.')
import fe_a
FIN=(5e-3,1e-3,110e9,10e-3,0.055)
def ev(label, thr=0.3, **kw):
    kw.setdefault('fin_strip',FIN)
    out=[]; bad=0
    for k in ('kd','nom','hi'):
        F,i=fe_a.build(k,**kw); r=F.solve(100)
        co=[(f,cx,cy,e) for (f,e,v,cx,cy) in r if (cx>=thr or cy>=thr) and f>2]
        viol=[(round(f),round(cx,1),round(cy,1)) for f,cx,cy,e in co if 83.3<f<420]
        fin=[round(f) for (f,e,v,cx,cy) in r if e.get('fin',0)>0.5][:1]
        lo=[round(f) for f,cx,cy,e in co][:6]
        out.append((k,lo,viol,fin)); bad+=len(viol)
    print(label,'VIOL',bad)
    for o in out: print('   ',o)
if __name__=='__main__':
    ev('base iter1-ish spar16 rib14 br8x6 single', spar_tube=(16e-3,14e-3), rib_tube=(14e-3,12e-3))
    ev('spar12x10 rib10x8 br8x6 single', spar_tube=(12e-3,10e-3), rib_tube=(10e-3,8e-3))
    ev('spar12x10 rib10x8 br8x6 V', spar_tube=(12e-3,10e-3), rib_tube=(10e-3,8e-3), bridge_cfg='V')
    ev('spar12x10 rib10x8 br10x8 V', spar_tube=(12e-3,10e-3), rib_tube=(10e-3,8e-3), bridge_cfg='V', bridge_tube=(10e-3,8e-3))
    ev('spar10x8 rib10x8 br8x6 V', spar_tube=(10e-3,8e-3), rib_tube=(10e-3,8e-3), bridge_cfg='V')
