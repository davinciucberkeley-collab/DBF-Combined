"""T-101 U2 Task B: node geometry old vs new from the live wing.py (hand scaling support). python -I (reads cad/amodel via structures/landing_path_a)."""
import os, sys, math
S = r"C:\Users\dillo\Downloads\Berkeley\Fall\Capstone\DBF-Combined\redesign\qp\A\structures"
sys.path.insert(0, S); sys.dont_write_bytecode = True
os.environ['LAND_MASS_KG'] = '1.913'; os.environ['LAND_CG_X_MM'] = '24.41'; os.environ['LAND_MASS_MODEL'] = 'cad'
import numpy as np
import landing_path_a as P
W, C = P.W, P.C
print("FNB_X1 %.5f FNP_X %s FNP_HY %.4f RIB_X0 %.5f RIB_OD %.4f XH %.5f" % (W.FNB_X1, W.FNP_X, W.FNP_HY, W.RIB_X0, W.RIB_OD, C.XH))
def poly_area(l): return abs(sum(l[i][0]*l[(i+1)%len(l)][1]-l[(i+1)%len(l)][0]*l[i][1] for i in range(len(l)))/2)
def clip_x(loop, x1):
    out = []
    for i in range(len(loop)):
        a, b = loop[i-1], loop[i]; ia, ib = a[0] <= x1, b[0] <= x1
        if ib:
            if not ia:
                t = (x1-a[0])/(b[0]-a[0]); out.append((x1, a[1]+t*(b[1]-a[1])))
            out.append(b)
        elif ia:
            t = (x1-a[0])/(b[0]-a[0]); out.append((x1, a[1]+t*(b[1]-a[1])))
    return out
N_PLY = 3
INNER = W._offset_loop(W.core_loop(), N_PLY*W.SKIN_T)
for xe in (0.17625, 0.176, W.FNB_X1):
    print("A_FIN clip at x %.4f: %.0f mm2" % (xe, poly_area(clip_x(INNER, xe))*1e6))
# cell thickness at 164..176 on the current inner loop
def grid_props(pred, x0, x1, z0, z1, xc, zc, h=0.25e-3):
    xs = np.arange(x0+h/2, x1, h); zs = np.arange(z0+h/2, z1, h); X, Zg = np.meshgrid(xs, zs, indexing='ij'); m = pred(X, Zg)
    dx, dz = X[m]-xc, Zg[m]-zc; a = h*h
    return dict(A=m.sum()*a, J=((dx**2+dz**2).sum())*a, rmax=float(np.sqrt(dx**2+dz**2).max()))
ro_ = W.RIB_OD/2*0+W.RIB_OD; RX0 = W.RIB_X0
for lab, px in (("old x 58-168", (0.058, 0.168)), ("new", tuple(W.FNP_X))):
    g = grid_props(lambda X, Yg: ~((np.abs(Yg) < ro_/2) & (X >= RX0)), px[0], px[1], -W.FNP_HY, W.FNP_HY, sum(px)/2, 0.0)
    print("plate %s: length %.2f mm, A %.0f mm2, J %.3e mm4, rmax %.2f mm" % (lab, (px[1]-px[0])*1e3, g['A']*1e6, g['J']*1e12, g['rmax']*1e3))
