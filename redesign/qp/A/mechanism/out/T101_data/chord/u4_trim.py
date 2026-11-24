import sys, math, json; sys.path.insert(0,'.')  # run from redesign/qp/A/sitl: python -I -c "...runpy..."
import a_aero as A
def trim(m, V=17.0, cg=None):
    if cg is not None: A.set_cg(cg)
    W=m*9.80665
    # solve alpha, d (TE down +) for Fz=-W (lift up = -z) and My=0, u=V cos a, w=V sin a
    a=0.1; d=0.0
    for _ in range(200):
        def f(a,d):
            F,T,_=A.airframe(V*math.cos(a),0,V*math.sin(a),0,0,0,d,d)
            return (F[2]*math.cos(a)-F[0]*math.sin(a))+W*math.cos(0)*0 + 0, T[1]
        # lift = -(Fz cos a - Fx sin a) wind-axis; use body: need Fz_body component balance incl. thrust ignored
        def g(a,d):
            F,T,_=A.airframe(V*math.cos(a),0,V*math.sin(a),0,0,0,d,d)
            Lw=-(F[2]*math.cos(a)-F[0]*math.sin(a))
            return Lw-W, T[1]
        h=1e-6
        r=g(a,d); ja=[(x-y)/h for x,y in zip(g(a+h,d),r)]; jd=[(x-y)/h for x,y in zip(g(a,d+h),r)]
        det=ja[0]*jd[1]-jd[0]*ja[1]
        da=(-r[0]*jd[1]+jd[0]*r[1])/det; dd=(-ja[0]*r[1]+ja[1]*r[0])/det
        a+=da; d+=dd
        if abs(da)+abs(dd)<1e-12: break
    return math.degrees(a), -math.degrees(d), (A.NP_X-A.CG_X)/A.C_W*100

def chord(cf, tau):
    A.EL_CF=cf; A.EL_TAU=tau; A.EL_S=2*(A.EL_Y1-A.EL_Y0)*cf*A.C_W; A.CLD=A.CLA*tau*(A.EL_S/A.S_W)
new_cf, new_tau = A.EL_CF, A.EL_TAU
OLDCG, NEWCG = 0.022049, json.load(open('cad_mass.json'))['cg_x_m']
for m in (1.881, 1.883):
  for lab, cf, tau, cg in (("old chord, old CG", 0.25, 0.5, OLDCG), ("old chord, new CG", 0.25, 0.5, NEWCG), ("new chord, new CG", new_cf, new_tau, NEWCG)):
    chord(cf, tau); a, d, sm = trim(m, cg=cg)
    print("m %.3f | %-18s | CG %.3f mm | alpha %.2f deg | trim %.2f deg TE up | SM %.2f %% | CLD %.4f /rad | EL_X %.1f mm" % (m, lab, cg*1e3, a, d, sm, A.CLD, A.EL_X*1e3))

