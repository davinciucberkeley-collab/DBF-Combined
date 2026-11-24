"""T-073 step 5b: flutter_d205 / flutter_d205_wing re-run with the glass torsion skin (flight-dynamics-class model: flutter_a.py Theodorsen Ritz wing + 3-DOF elevon section, p-method fixes2_run.py).
Method: flutter_a / fixes2_run are NOT edited; the skin is added by patching flutter_a.GJ_parts (torsion), flutter_a.I12 (out-of-plane EI) and flutter_a.wing_mass (mass, inertia) at module level.
Skin: 1 ply (T073_PLIES) +-45 glass, GJ = 4 A^2 G t / perimeter over |y| <= 0.40 (series with the bare spar GJ over the last 0.05 m), corner scale kd 0.7 / nom 1.0 / hi 1.3 on the skin G and E (EST),
elevon, lead, lens-cap lumps exactly as flutter_d205_wing.py / flutter_d205.py.  Run: python -I t073_flutter.py [wing|elevon|both]  (elevon: 3 processes, about 5-8 min)."""
import os, sys, math, json, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.abspath(os.path.join(HERE, "..", "..", "..", "structures")); sys.path.insert(0, S); sys.path.insert(0, os.path.join(S, "..", "sitl"))
sys.dont_write_bytecode = True
import numpy as np
import flutter_a as F
import fixes2_run as R
import landing_path_a as LP
SK = os.environ.get("T073_FSKIN", "1") == "1"
PLIES = float(os.environ.get("T073_PLIES", "1"))
_S, _CG = LP.sec_cell(); _A = _S['foam']['enclosed']; _PER = _CG['S0']; _lam = LP.skin_laminate(n=1); T1 = _lam['t']
CSC = {"kd": 0.7, "nom": 1.0, "hi": 1.3}
def I_out_per_t():
    Pl = LP._poly(); I = 0.0
    for i in range(len(Pl)):
        a, b = Pl[i], Pl[(i+1) % len(Pl)]; n = max(int(np.hypot(*(b-a))/0.05e-3), 1)
        u = (np.arange(n)+0.5)/n; xm = a[0]+(b[0]-a[0])*u; zm = a[1]+(b[1]-a[1])*u; ds = np.hypot(*(b-a))/n
        m = xm <= LP.XH; I += ds*(zm[m]**2).sum()
    return I+_CG['cove_h']**3/12
IOUT = I_out_per_t()
def skin(corner):
    k = CSC[corner]; t = PLIES*T1
    return dict(GJ=4*_A*_A*_lam['G']*k*t/_PER, EIo=_lam['Ex']*k*t*IOUT, mpm=0.088*PLIES*_PER, xk=_CG['S1']/_CG['S0'])
_gjp = F.GJ_parts; _wm = F.wing_mass; _ritz = F.ritz
CUR = {"c": "nom"}
def GJ_parts_p(k, box_eff=1.0, hinge_cut=True):
    gs, gb = _gjp(k, box_eff, hinge_cut)
    if SK and not hinge_cut:
        sk = skin(k); L = 0.45
        eff = L/(0.40/(gs+gb+sk['GJ'])+0.05/(gs+gb))
        return gs, eff-gs          # sum = series-effective GJ over the semispan
    return gs, gb
def wing_mass_p():
    m, Sa, Ia, xcg = _wm()
    if not SK: return m, Sa, Ia, xcg
    sk = skin(CUR["c"]); ms = (sk['mpm']*0.8+(5.0+3.7)*1e-3)/0.9                   # kg per m of semispan basis (0.9 m), plates + strip added
    xs = sk['xk']; d = xs-F.X_SPAR
    mt = m+ms; Sa2 = Sa+ms*(xs-F.X_SPAR); Ia2 = Ia+ms*(0.18**2/12+d*d)
    return mt, Sa2+m*(xcg-F.X_SPAR)*0, Ia2, (m*xcg+ms*xs)/mt
def ritz_p(corner="nom", **kw):
    CUR["c"] = corner
    if SK:
        sk = skin(corner); F.I12 = _I12*(1.0+sk['EIo']/(F.CORN[corner]["E"]*_I12))
    return _ritz(corner, **kw)
_I12 = F.I12
F.GJ_parts = GJ_parts_p; F.wing_mass = wing_mass_p; F.ritz = ritz_p

def wing_cases():
    L = []
    def P(s=""): print(s, flush=True); L.append(s)
    R.setup(0.0067, 0.25)
    lump = (((12.8+0.5+2*3.98+2.5)*1e-3, 0.18375-0.020, 0.285),)
    P(f"| skin {'on, '+str(PLIES)+' ply' if SK else 'OFF'} | corner | skin GJ N m2 / effective semispan GJ | f1 / f2 / f3 (Hz) | flutter V (m/s) | x 28.8 line |"); P("|---|---|---|---|---|---|")
    for nm, kw in (("fin on tip (base)", dict()), ("fins off (worst sensitivity)", dict(fins=False))):
        for k in ("kd", "nom", "hi"):
            CUR["c"] = k
            f, ff = F.wing_flutter(k, lumps=lump, **kw)
            sk = skin(k) if SK else dict(GJ=0.0); gsum = sum(F.GJ_parts(k, hinge_cut=False))
            P("| %s | %s | %.1f / %.2f | %.1f / %.1f / %.1f | %s | %s |" % (nm, k, sk['GJ'], gsum, f[0], f[1], f[2], "%.1f" % ff[0] if ff else ">100", ("PASS" if (not ff or ff[0] >= F.VREQ) else "FAIL")))
    return L
def elevon_cases():
    L = []
    def P(s=""): print(s, flush=True); L.append(s)
    me, lead, arm = 0.0067, 12.8, 0.020; C0 = 1.0297e-3
    cases = [("A no damper, lead 12.8 g, elevon 6.7 g", me, 12.8, arm, 0.25, 0.0), ("B damper hot 50 C (EST x0.6), lead 12.8 g", me, 12.8, arm, 0.25, 0.6*C0),
             ("C damper nominal 25 C, lead 12.8 g", me, 12.8, arm, 0.25, C0), ("D damper cold 0 C (EST x2), lead 12.8 g", me, 12.8, arm, 0.25, 2*C0),
             ("E damper half-hot (leak / half fill), lead 12.8 g", me, 12.8, arm, 0.25, 0.3*C0)]
    tasks = [(n, k, m_, ld, ar, cf, cd) for (n, m_, ld, ar, cf, cd) in cases for k in ("kd", "nom", "hi")]
    with mp.Pool(3) as pool: res = pool.map(R.run_case, tasks)
    P("| case | corner | wing f_h / f_a (Hz) | no instability <= 28.8 m/s at any K (0.01-20 N m/rad) | unstable K band | worst damping ratio needed | lowest onset over the grid (m/s) |"); P("|---|---|---|---|---|---|---|")
    for r in res: P(R.fmt(r))
    return L
if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "both"
    if what in ("wing", "both"): wing_cases()
    if what in ("elevon", "both"): elevon_cases()
