import sys, math, numpy as np
sys.path.insert(0, r'C:\Users\dillo\Downloads\Berkeley\Fall\Capstone\DBF-Combined\redesign\qp\A\cad')
sys.dont_write_bytecode=True
from amodel import wing as W
from amodel.wing import *
from scipy import ndimage as ndi
h=0.0005
x0,x1=HUB[0]+BLK_X[0]-0.001, HUB[0]+COL_X1+0.001
ext=0.034
xs=np.arange(x0+h/2,x1,h); ys=np.arange(-ext+h/2,ext,h)
Y,Z=np.meshgrid(ys,ys,indexing='ij')
vol=np.zeros((len(xs),len(ys),len(ys)),bool)
for i,x in enumerate(xs):
    dx_rel=x-HUB[0]
    inside=np.zeros(Y.shape,bool)
    if BLK_X[0]<=dx_rel<=BLK_X[1]:
        ay,az=np.abs(Y),np.abs(Z-BLK_Z); cy,cz=np.maximum(ay-(CB-R_CB),0),np.maximum(az-(CB-R_CB),0)
        inside|=(ay<=CB)&(az<=CB)&(cy*cy+cz*cz<=R_CB**2)
    if BLK_X[1]<=dx_rel<=COL_X1:
        zc=0.5*(COL_Z[0]+COL_Z[1]); hz=0.5*(COL_Z[1]-COL_Z[0]); ay=np.abs(Y)
        cy2=np.maximum(ay-(COL_HY-R_CB),0); cz2=np.maximum(np.abs(Z-zc)-(hz-R_CB),0)
        inside|=(ay<=COL_HY)&(np.abs(Z-zc)<=hz)&(cy2*cy2+cz2*cz2<=R_CB**2)
    sub=np.zeros(Y.shape,bool)
    for T in 'AB':
        xt,phi=TUBE_X[T],TUBE_PHI[T]
        U,Tt=W._yz_ut(phi,Y,Z)
        d2=Tt*Tt+(x-xt)**2
        inside|=(np.abs(U)<=SLV_L)&(np.maximum(np.maximum(abs(x-xt),np.abs(Tt)),(abs(x-xt)+np.abs(Tt))/math.sqrt(2))<=SLV_R)
        sub|=d2<=TUBE_RO**2
        sub|=(np.abs(U)>=DBL_S0)&(np.abs(U)<=DBL_S1)&(d2<=DBL_RO**2)
    if dx_rel>=BORE_X0-HUB[0]:
        sub|=(Y*Y+(Z-BR_Z)**2<=BR_RO**2)
    vol[i]=inside&~sub
print('solid cm3',vol.sum()*h**3*1e6, 'mass g', vol.sum()*h**3*1e6*2.7)
# distance (mm) to nearest void (outside the solid, incl. bores)
pad=np.pad(vol,1,constant_values=False)
d=ndi.distance_transform_edt(pad,sampling=h*1000)[1:-1,1:-1,1:-1]
np.savez_compressed(r'C:\Users\dillo\AppData\Local\Temp\claude\1dc032cbc6faa005\7cb35b0a-c71b-43ed-9be1-fbe0a7ff151f\scratchpad\medial.npz',vol=vol,d=d,xs=xs,ys=ys)
for t in (1.0,1.5,2.0,2.5,3.0):
    m=d>t
    print('wall %.1f: region with distance > t: %.2f cm3 = %.1f g' % (t, m.sum()*h**3*1e6, m.sum()*h**3*1e6*2.7))
# by x region
for (a,b) in ((-14,-7),(-7,0),(0,7),(7,14.5),(14.5,24),(24,45)):
    sel=(xs-HUB[0]>=a/1000)&(xs-HUB[0]<b/1000)
    print('x %5.1f..%5.1f solid %.2f g ; core(d>2) %.2f g' % (a,b,vol[sel].sum()*h**3*1e6*2.7,(d[sel]>2).sum()*h**3*1e6*2.7))
print('--- distance to bores only')
bore=np.zeros_like(vol)
for i,x in enumerate(xs):
    dx_rel=x-HUB[0]
    sub=np.zeros(Y.shape,bool)
    for T in 'AB':
        xt,phi=TUBE_X[T],TUBE_PHI[T]
        U,Tt=W._yz_ut(phi,Y,Z)
        d2=Tt*Tt+(x-xt)**2
        sub|=(d2<=TUBE_RO**2)&(np.abs(U)<=SLV_L+0.02)
        sub|=(np.abs(U)>=DBL_S0)&(np.abs(U)<=DBL_S1)&(d2<=DBL_RO**2)
    if dx_rel>=BORE_X0-HUB[0]:
        sub|=(Y*Y+(Z-BR_Z)**2<=BR_RO**2)
    bore[i]=sub
db=ndi.distance_transform_edt(~bore,sampling=h*1000)
for t in (2.0,2.5,3.0,3.5,4.0):
    m=vol&(db>t)
    print('wall to bore %.1f: %.2f cm3 = %.1f g' % (t,m.sum()*h**3*1e6,m.sum()*h**3*1e6*2.7))
for t in (2.5,3.0):
  for (a,b) in ((-14,-7),(-7,0),(0,7),(7,14.5),(14.5,24),(24,45)):
    sel=(xs-HUB[0]>=a/1000)&(xs-HUB[0]<b/1000)
    print('t %.1f x %5.1f..%5.1f : %.2f g' % (t,a,b,(vol[sel]&(db[sel]>t)).sum()*h**3*1e6*2.7))
np.save(r'C:\Users\dillo\AppData\Local\Temp\claude\1dc032cbc6faa005\7cb35b0a-c71b-43ed-9be1-fbe0a7ff151f\scratchpad\db.npy',db)
