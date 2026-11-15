"""QP-4 FIXES2 (D6/C2/A5): elevon flutter robust to hinge stiffness K and free play.  python -I fixes2_run.py -> fixes2_run.md   (numpy, scipy; 3 processes, ~5 min)
Method: the repo's 3-DOF Theodorsen-Garrick section (flutter_a.py, unchanged) re-solved as a p-method (stability of an 8-state system: 3 DOF + 2 Jones lag states,
C(k) ~ 0.5 + 0.165 a1/(s+a1) + 0.335 a2/(s+a2), a1 = 0.0455 V/b, a2 = 0.3 V/b; about 2 % off Theodorsen, printed).  No mode tracking, so no tracker artefacts.
Cross-checked against flutter_a.py's k-method (printed).  g_s = 0 unless a hinge damper c is stated.
"Unstable at V" = an oscillatory root (> 3 Hz) with Re(s) > 0 at that V.  zeta_req = largest Re(s)/|s| for V <= 28.8 (the viscous damping ratio that would stop it)."""
import sys, os, math, functools, multiprocessing as mp
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flutter_a as F
pi = math.pi
def aero_gen(d1,d2,V,Cv,b,a,c,rho=F.RHO):
    T=F.Tc(c,a)
    Q=np.array([d1,V+b*(0.5-a)*d1,V*T[10]/pi+b*T[11]/(2*pi)*d1],dtype=complex)
    cP=-2*pi*rho*V*b; cM=2*pi*rho*V*b*b*(a+0.5); cB=-rho*V*b*b*T[12]
    P=-rho*b*b*np.array([d2*pi,V*pi*d1-pi*b*a*d2,-V*T[4]*d1-T[1]*b*d2])
    Ma=rho*b*b*np.array([pi*a*b*d2,-V*b*pi*(0.5-a)*d1-b*b*pi*(1/8+a*a)*d2,-V*V*T[15]-V*b*T[16]*d1+b*b*(T[7]+(c-a)*T[1])*d2])
    Mb=rho*b*b*np.array([T[1]*b*d2,-2*T[13]*b*b*d2-V*b*T[17]*d1,(T[3]/pi)*b*b*d2-(V*V*T[18]/pi)+F.SB*(V*b*T[19]/pi)*d1])
    return P,Ma,Mb,Q,np.array([cP,cM,cB]),
def parts(V,b,a,c):
    f=lambda d1,d2: np.array(aero_gen(d1,d2,V,0,b,a,c)[:3]).real
    B0=f(0,0);B1=f(1,0)-B0;B2=f(0,1)-B0
    _,_,_,Qv,cv=aero_gen(0,0,V,0,b,a,c); Q0=Qv.real; Q1=(aero_gen(1,0,V,0,b,a,c)[3]-Qv).real
    return B0,B1,B2,Q0,Q1,cv

@functools.lru_cache(maxsize=None)
def cparts(V, c): return parts(V, F.B, F.A_EA, c)
def eigs2(M,K,V,c,Cd=None):
    B0,B1,B2,Q0,Q1,cv=cparts(V,c)
    a1,a2=0.0455*V/F.B,0.3*V/F.B; r1,r2=0.165*a1,0.335*a2
    Mi=np.linalg.inv(M-B2)
    Kc=-K+B0+0.5*np.outer(cv,Q0); Dc=B1+0.5*np.outer(cv,Q1)
    if Cd is not None: Dc=Dc-Cd
    A=np.zeros((8,8)); A[0:3,3:6]=np.eye(3)
    A[3:6,0:3]=Mi@Kc; A[3:6,3:6]=Mi@Dc; A[3:6,6]=Mi@(r1*cv); A[3:6,7]=Mi@(r2*cv)
    A[6,0:3]=Q0; A[6,3:6]=Q1; A[6,6]=-a1; A[7,0:3]=Q0; A[7,3:6]=Q1; A[7,7]=-a2
    return np.linalg.eigvals(A)

VGRID = np.arange(2.0, 60.01, 0.5)
def zeta_req(M, K, c, vmax=28.8, Cd=None):
    best = -1.0
    for V in VGRID:
        if V > vmax + 1e-9: break
        e = eigs2(M, K, V, c, Cd); m = np.abs(e) > 2*pi*3.0
        if m.any(): best = max(best, float((e.real[m]/np.abs(e[m])).max()))
    return best
def onset(M, K, c, Cd=None, vmax=60.0):
    for V in VGRID:
        if V > vmax: break
        e = eigs2(M, K, V, c, Cd); m = (np.abs(e) > 2*pi*3.0) & (e.real > 1e-6)
        if m.any(): return V
    return None
KG = np.logspace(-2, math.log10(20), 600)        # 0.01-20 N m/rad, 600 log points (about 180 per decade)
SPAN = 0.31
def setup(me, cf):
    F.FOAM_RHO = 25.0; F.EL_Y1 = 0.35; F.ME_EL = me; F.EL_CF = cf; F.C_H = ((1-cf)*F.CH-0.5*F.CH)/F.B
def wing_modes(corner, lead, arm):
    f, _ = F.wing_flutter(corner, lumps=(((lead+0.5+2.0)*1e-3, 0.18375-arm, 0.285),)); return f[0], f[1]
def run_case(args):
    name, corner, me, lead, arm, cf, cdamp = args
    setup(me, cf); fh, fa = wing_modes(corner, lead, arm)
    Cd = None
    if cdamp: Cd = np.zeros((3, 3)); Cd[2, 2] = cdamp/SPAN
    zr, kz, nunst, band = -1.0, None, 0, []
    vmin, kv = 99.0, None
    for i, Kb in enumerate(KG):
        M, K = F.elevon_section(fh, fa, Kb, xb_bal=arm, mbal=(lead+0.5)*1e-3/SPAN)
        z = zeta_req(M, K, F.C_H, Cd=Cd)
        if z > 1e-9: nunst += 1; band.append(Kb)
        if z > zr: zr, kz = z, Kb
        if i % 3 == 0:
            o = onset(M, K, F.C_H, Cd)
            if o is not None and o < vmin: vmin, kv = o, Kb
    return dict(name=name, corner=corner, fh=fh, fa=fa, zr=zr, kz=kz, nunst=nunst, band=(min(band), max(band)) if band else None, vmin=vmin, kv=kv)
def fmt(r):
    return "| %s | %s | %.1f / %.1f | %s | %s | %s | %s |" % (r["name"], r["corner"], r["fh"], r["fa"], "**PASS**" if r["nunst"] == 0 else "FAIL (%d of %d K points)" % (r["nunst"], len(KG)),
        "%.2f-%.2f" % r["band"] if r["band"] else "-", "%.1e at K %.2f" % (r["zr"], r["kz"]) if r["nunst"] else "<= 0", ("%.1f at K %.2f" % (r["vmin"], r["kv"])) if r["kv"] else ">60")
def zmax(args):
    corner, lead, cdamp, vmax = args
    setup(0.0096, 0.25); fh, fa = wing_modes(corner, lead, 0.02); Cd = np.zeros((3, 3)); Cd[2, 2] = cdamp/SPAN; w = -1
    for Kb in KG[::2]:
        M, K = F.elevon_section(fh, fa, Kb, xb_bal=0.02, mbal=(lead+0.5)*1e-3/SPAN); w = max(w, zeta_req(M, K, F.C_H, vmax=vmax, Cd=Cd))
    return w
def cmin(args):
    corner, lead, vmax = args; lo, hi = 0.0, 3e-3
    for _ in range(11):
        mid = (lo+hi)/2
        if zmax((corner, lead, mid, vmax)) > 1e-9: lo = mid
        else: hi = mid
    return hi
if __name__ == "__main__":
    L = []
    def P(s=""): print(s, flush=True); L.append(s)
    b = F.B; a = F.A_EA; c = ((0.75*F.CH)-0.5*F.CH)/F.B; w = 100.0
    errs = []
    for k in (0.2, 0.5, 1.0):
        V = w*b/k; s = 1j*w; out = []
        for Cv in (F.Ck(k), 0.5+0.165*0.0455*V/b/(s+0.0455*V/b)+0.335*0.3*V/b/(s+0.3*V/b)):
            Pp, Ma, Mb, Q, cv = aero_gen(s, s*s, V, 0, b, a, c); out.append(np.array([Pp, Ma, Mb])+np.outer(cv, Q)*Cv)
        errs.append(np.max(np.abs(out[0]-out[1]))/np.max(np.abs(out[0])))
    P("Jones-lag aero vs Theodorsen C(k), max matrix error at k 0.2 / 0.5 / 1.0: %s" % " / ".join("%.1f %%" % (100*e) for e in errs)); P()
    setup(0.0096, 0.25); fh, fa = wing_modes("nom", 15.6, 0.02); chk = []
    for Kb in (0.5, 1.0, 1.3, 2.0):
        M, K = F.elevon_section(fh, fa, Kb, xb_bal=0.02, mbal=16.1e-3/SPAN); ff = F.elevon_flutter(fh, fa, Kb, xb_bal=0.02, mbal=16.1e-3/SPAN)
        chk.append("K %.1f: p-method %s, k-method %.1f" % (Kb, onset(M, K, F.C_H), ff[0]))
    P("Cross-check, onset speed (m/s), reference balance, nom: " + "; ".join(chk)); P()
    me0 = 0.0096
    def lead_for(ob, me, arm, cf=0.25): return ob*me*0.35*cf*F.CH/arm*1e3
    cases = [("0 D-187 v2 as drawn: 15.6 g at 20 mm (ob 1.56), elevon 9.6 g", me0, 15.6, 0.020, 0.25, 0),
             ("1 overbalance 2.5 (25.7 g at 20 mm)", me0, lead_for(2.5, me0, 0.02), 0.020, 0.25, 0),
             ("2 overbalance 4 at 14 mm (58.8 g)", me0, lead_for(4, me0, 0.014), 0.014, 0.25, 0),
             ("3 overbalance 5 at 14 mm (73.5 g)", me0, lead_for(5, me0, 0.014), 0.014, 0.25, 0),
             ("4 lighter elevon 6.0 g, ob 2.5, 20 mm (12.9 g)", 0.0060, lead_for(2.5, 0.006, 0.02), 0.020, 0.25, 0),
             ("5 lighter elevon 4.5 g, ob 6, 14 mm (41 g)", 0.0045, lead_for(6, 0.0045, 0.014), 0.014, 0.25, 0),
             ("6 chord 0.20 c (hinge 0.80 c), 8.3 g, ob 2.5", 0.0083, lead_for(2.5, 0.0083, 0.02, 0.20), 0.020, 0.20, 0),
             ("7 chord 0.30 c (hinge 0.70 c), 10.9 g, ob 2.5", 0.0109, lead_for(2.5, 0.0109, 0.02, 0.30), 0.020, 0.30, 0),
             ("8 D-187 v2 + hinge damper c = 8e-4 N m s/rad", me0, 15.6, 0.020, 0.25, 8e-4)]
    tasks = [(n, k, me, ld, ar, cf, cd) for (n, me, ld, ar, cf, cd) in cases for k in ("kd", "nom", "hi")]
    with mp.Pool(3) as pool: res = pool.map(run_case, tasks)
    P("## 1 K sweep 0.01-20 N m/rad (%d log points), g_s = 0, V <= 28.8 m/s; wing corners kd / nom / hi" % len(KG)); P()
    P("| design | corner | wing f_h / f_a (Hz) | no instability <= 28.8 at any K | unstable K band | worst damping ratio needed (V <= 28.8) | lowest onset over the grid (m/s) |"); P("|---|---|---|---|---|---|---|")
    for r in res: P(fmt(r))
    P()
    P("## 2 Hinge damper needed (viscous, across the hinge, per elevon, N m s/rad; lead strip at 20 mm)"); P(); P("| lead per elevon (g) | corner | c for no instability <= 28.8 | c for <= 37 (1.54 VD, the QP-4 target) |"); P("|---|---|---|---|")
    jobs = [(l, k) for l in (12.8, 15.6, 20.0) for k in ("kd", "nom", "hi")]
    with mp.Pool(3) as pool: c1 = pool.map(cmin, [(k, l, 28.8) for l, k in jobs]); c2 = pool.map(cmin, [(k, l, 37.0) for l, k in jobs])
    for (l, k), x, y in zip(jobs, c1, c2): P("| %.1f | %s | %.1e | %.1e |" % (l, k, x, y))
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixes2_run.md"), "w").write("\n".join(L))
