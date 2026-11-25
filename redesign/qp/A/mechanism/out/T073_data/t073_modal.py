"""T-073 step 5 (A-P10, D-216 s7 step 5): wing modal / forced response with the glass torsion skin, at both 1P bands incl. the lower hover band of a 10x4.5 prop.
CATEGORY: FEA-class modal analysis (beam-frame FE, fe_a.py, as iter3_run.py) + flight-dynamics-class flutter (flutter_a.py Theodorsen Ritz model; flutter_d205*.py cases).  EST inputs flagged.
Run: python -I t073_modal.py > modal_out.txt   (numpy, scipy; the elevon-flutter part uses 3 processes).  Nothing in structures/ is edited: skin is added by patching the built frame and
flutter_a at run time (monkeypatch, module level so spawned workers see it).
Skin model (T-071 laminate: 1 ply 48 g/m2 glass + 40 g/m2 resin, t 0.054 mm, +-45, G 7.7 GPa, Ex 8.7 GPa, EST scaled from ACP PDS Dec 2014): GJ = 4 A^2 G t / perimeter over |y| <= 0.40 m,
corner scale on the skin G and E: kd 0.7 / nom 1.0 / hi 1.3 (EST, same spread idea as T-071 V3); mass 0.088 kg/m2 x perimeter, plates 5 g + cove strip 3.7 g (T-070/T-071)."""
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.abspath(os.path.join(HERE, "..", "..", "..", "structures")); sys.path.insert(0, S); sys.path.insert(0, os.path.join(S, "..", "sitl"))
sys.dont_write_bytecode = True
import numpy as np
import fe_a, flutter_a as FA
from scipy.linalg import eigh
import landing_path_a as LP
from iter2_eval import BANDS as BANDS9, RPM_HOVER, RPM_CRUISE
SK_PLIES = float(os.environ.get("T073_PLIES", "1"))
SKIN_ON = os.environ.get("T073_SKIN", "1") == "1"
SKIN_SCALE = float(os.environ.get("T073_SKSCALE", "1.0"))        # extra skin stiffness factor on top of the corner scale (sensitivity)
EIIN = os.environ.get("T073_EIIN", "spar")                          # in-plane skin EI: spar = about the spar axis (upper bound), own = about the skin centroid (lower), none
SK_OPEN = float(os.environ.get("T073_OPEN", "0.0"))               # skin absent for |y| < SK_OPEN (open centre cell, tray slot 0.057)
CORNER_SK = {"kd": 0.7, "nom": 1.0, "hi": 1.3}

# ------------------------------------------------------------------ skin section properties from the CAD airfoil (landing_path_a helpers)
_S, _CG = LP.sec_cell(); _A = _S['foam']['enclosed']; _PER = _CG['S0']
_lam = LP.skin_laminate(n=1); T1 = _lam['t']
def skin_out_of_plane_I():
    Pl = LP._poly(); I = 0.0; zs = []
    for i in range(len(Pl)):
        a, b = Pl[i], Pl[(i+1) % len(Pl)]; n = max(int(np.hypot(*(b-a))/0.05e-3), 1)
        u = (np.arange(n)+0.5)/n; xm = a[0]+(b[0]-a[0])*u; zm = a[1]+(b[1]-a[1])*u; ds = np.hypot(*(b-a))/n
        m = xm <= LP.XH; I += ds*(zm[m]**2).sum(); zs += list(zm[m])
    hc = _CG['cove_h']; I += hc**3/12
    return I                                                     # per unit thickness: I = t * this (about z = 0 of the airfoil frame; the cell is nearly symmetric about z = 0.0)
I_OUT_PER_T = skin_out_of_plane_I()
def skin_props(corner, plies=None, scale=None):
    plies = SK_PLIES if plies is None else plies; k = CORNER_SK[corner]*(SKIN_SCALE if scale is None else scale)
    t = plies*T1; G_ = _lam['G']*k; Ex = _lam['Ex']*k
    GJ = 4*_A*_A*G_*t/_PER
    EI_out = Ex*t*I_OUT_PER_T
    EI_in = Ex*t*(_CG['S2']-2*LP.SX*_CG['S1']+LP.SX**2*_CG['S0'])       # about the spar axis (bound; composite NA offset ignored)
    if EIIN == "own": EI_in = Ex*t*(_CG['S2']-_CG['S1']**2/_CG['S0'])
    if EIIN == "none": EI_in = 0.0
    mass_per_m = 0.088*plies*_PER                                        # kg/m of span (0.088 kg/m2 per ply)
    return dict(GJ=GJ, EI_out=EI_out, EI_in=EI_in, mass_per_m=mass_per_m, t=t, G=G_, Ex=Ex)

# ------------------------------------------------------------------ rpm bases (9x4.5 repo table; 10x4.5 APC PER3_10x45MR.dat static rows, read 2026-11-19 via WebFetch: Thrust lbf, V = 0)
T9 = {5000: 2.674, 6000: 3.859, 7000: 5.264, 8000: 6.892, 9000: 8.746, 10000: 10.830, 11000: 13.149, 12000: 15.706}      # N, prop_a.py (PER3_9x45MR.dat)
T10 = {5000: 0.852*4.4482, 6000: 1.231*4.4482, 7000: 1.679*4.4482, 8000: 2.200*4.4482, 9000: 2.795*4.4482, 10000: 3.464*4.4482}   # lbf -> N (4.4482)
P10 = {5000: 0.040, 6000: 0.068, 7000: 0.108, 8000: 0.160, 9000: 0.227, 10000: 0.311}          # hp
P9 = {5000: 20.063, 6000: 34.224, 7000: 53.842, 8000: 79.836, 9000: 113.149, 10000: 154.758}   # W
def interp(tab, n):
    ks = sorted(tab); n = max(ks[0], min(ks[-1], n))
    for a, b in zip(ks, ks[1:]):
        if a <= n <= b: return tab[a]+(n-a)/(b-a)*(tab[b]-tab[a])
def inv(tab, y, lo=3000.0, hi=12000.0):
    for _ in range(80):
        m = 0.5*(lo+hi)
        if interp(tab, m) < y: lo = m
        else: hi = m
    return 0.5*(lo+hi)
DER = 0.93
def rpm10_equal_thrust(n9): return inv(T10, interp(T9, n9))          # same table thrust (same x0.93 derate on both) -> same real thrust
def rpm10_equal_power(n9):
    p9 = interp(P9, n9); P10w = {k: v*745.7 for k, v in P10.items()}; return inv(P10w, p9)
PROP = os.environ.get("T073_PROP", "9")
if PROP == "10":
    HOV = tuple(rpm10_equal_thrust(r) for r in RPM_HOVER)
    CRU = RPM_CRUISE                                                   # pitch-set (both 4.5 in pitch): EST, unchanged
    RPM_CAP = rpm10_equal_power(9349.0); RPM_UNC = rpm10_equal_power(10142.0)
    RPM_H_MID = HOV[1]
else:
    HOV, CRU, RPM_CAP, RPM_UNC, RPM_H_MID = RPM_HOVER, RPM_CRUISE, 9349.0, 10142.0, RPM_HOVER[1]
BANDS = [("hover 1P", HOV[0]/60, HOV[2]/60), ("hover 2P", HOV[0]/30, HOV[2]/30), ("cruise 1P", CRU[0]/60, CRU[2]/60), ("cruise 2P", CRU[0]/30, CRU[2]/30)]
LO_LIM = min(b[1] for b in BANDS)/1.2; HI_LIM = 1.2*max(b[2] for b in BANDS)
T_HOV = 3.94
def thr(rpm): return T_HOV*(rpm/RPM_H_MID)**2
CFG = dict(spar_tube=(12e-3, 10e-3), arm_tube=(12e-3, 10e-3), rib_tube=(14e-3, 12e-3), bridge_cfg="single+V", bridge_tube=(12e-3, 10e-3),
           vtube=(6e-3, 4.5e-3), bridge_yv=0.30, fin_strip=None, fin_tube=(16e-3, 14e-3, 3e-3, 0.055), x_fin=0.294, foot_pad_m=0.0025)
O4 = os.environ.get("T073_O4", "0") == "1"      # O4 mass changes: pack 232 g (CNHL 2000 100C `U`), tray -16 g (R1), avionics plate out (R2 -17 g), props +3 g each (EST)
if O4: CFG.update(pack_g=232.0-16.0, avionics_g=110.0-17.0, motor_g=65.0+11.06+5.0+4.3+2.9+3.0)
# wing torsional inertia about the elastic axis (flutter_a.wing_mass I'_EA, kg m per m of span) added at the spar nodes as theta_y inertia (fe_a lumps carry none: 1e-5 m)
_m, _Sa, _Ia, _xcg = FA.wing_mass()
def build_variant(corner):
    kind = corner
    F, info = fe_a.build(kind, **CFG)
    sp = skin_props(corner) if SKIN_ON else None
    ys_nodes = sorted(float(n[1:]) for n in F.n if n.startswith("s") and ">" not in n)
    Jadd = {}
    new = []
    for el in F.el:
        a, b, EA, EIy, EIz, GJ, rA, vref, grp = el
        if grp == "spar" and sp is not None:
            pa, pb = F.n[a], F.n[b]; ym = abs(0.5*(pa[1]+pb[1]))
            if ym <= 0.40 and ym >= SK_OPEN:
                PARTS = os.environ.get("T073_PARTS", "gj,eo,ei,m").split(",")
                if "gj" in PARTS: GJ = GJ+sp['GJ']
                if "eo" in PARTS: EIy = EIy+sp['EI_out']
                if "ei" in PARTS: EIz = EIz+sp['EI_in']
                if "m" in PARTS: rA = rA+sp['mass_per_m']
        new.append((a, b, EA, EIy, EIz, GJ, rA, vref, grp))
    F.el = new
    if sp is not None:
        for nm in F.n:
            if nm.startswith("s") and ">" not in nm and abs(float(nm[1:])) <= 0.40:
                F.lump(nm, 0.0*1e-3)
        F.lump("s+0.000", (5.0+3.7)*1e-3)
    return F, sp
_orig_eigh = fe_a.eigh
_CUR = {}
def eigh_patched(K, M):
    F = _CUR['F']; names = list(F.n); idx = {k: i for i, k in enumerate(names)}
    M = M.copy()
    # rotary inertia about y (dof 4) from the wing section inertia, at spar nodes (tributary length)
    ys = sorted((float(F.n[n][1]), n) for n in names if n.startswith("s") and abs(F.n[n][0]-fe_a.X_SPAR) < 1e-9 and abs(F.n[n][2]) < 1e-12)
    for i, (y, n) in enumerate(ys):
        lo = ys[i-1][0] if i > 0 else y; hi = ys[i+1][0] if i < len(ys)-1 else y
        dy = 0.5*(hi-lo) if 0 < i < len(ys)-1 else (0.5*(hi-y) if i == 0 else 0.5*(y-lo))
        if abs(y) > 0.45: continue
        Ia = _Ia + (skin_props(_CUR['corner'])['mass_per_m']*0.05**2 if SKIN_ON else 0.0)       # skin centroid about 0.05 m from the spar: parallel-axis EST
        if os.environ.get('T073_ROT', '1') == '1': M[6*idx[n]+4, 6*idx[n]+4] += Ia*dy
    return _orig_eigh(K, M)
fe_a.eigh = eigh_patched

U = 1e-6; LIM = 30.0
def ok(f): return all((f <= lo/1.2) or (f >= 1.2*hi) for n, lo, hi in BANDS)
def run_fe(corner):
    F, sp = build_variant(corner); _CUR['F'] = F; _CUR['corner'] = corner
    res = F.solve(100); return F, res, sp
def forced(F, res, rpm, thrust, zeta=0.01):
    idx = F._idx; imu = idx["s+0.000"]; MOT = [m for m in idx if (m.startswith("m+") or m.startswith("m-")) and ">" not in m]
    ax = np.zeros(3); om = rpm/60*2*math.pi
    for m in MOT:
        for mult, fm in ((1, U*om**2), (2, 0.05*thrust)):
            w = mult*om
            for (f, e, v, cx, cy) in res:
                wi = 2*math.pi*f
                g = fm*(abs(v[6*idx[m]+1])+abs(v[6*idx[m]+2])) if mult == 1 else fm*abs(v[6*idx[m]])
                h = 1/math.sqrt((wi*wi-w*w)**2+(2*zeta*wi*w)**2)
                ax += w*w*g*h*np.abs(v[6*imu:6*imu+3])
    return ax

def table_for(label):
    print(f"\n### {label}")
    print(f"prop {PROP} in; hover rpm {HOV[0]:.0f}/{HOV[1]:.0f}/{HOV[2]:.0f}, cruise {CRU[0]:.0f}-{CRU[2]:.0f}; bands (Hz): " + "; ".join(f"{n} {lo:.1f}-{hi:.1f}" for n, lo, hi in BANDS) + f"; exclusion (strongly coupled) {LO_LIM:.1f}-{HI_LIM:.1f} Hz; cap rpm {RPM_CAP:.0f} (1P {RPM_CAP/60:.0f} Hz), uncapped {RPM_UNC:.0f}")
    stop = []
    for k in ("kd", "nom", "hi"):
        F, res, sp = run_fe(k)
        idx = F._idx; MOT = [m for m in idx if (m.startswith("m+") or m.startswith("m-")) and ">" not in m]
        rows = []
        for (f, e, v, cx, cy) in res:
            if f < 2 or f > 700: continue
            c = max(cx, cy); dom = max(e, key=e.get)
            if (LO_LIM*0.8 < f < HI_LIM*1.1 and c >= 0.05) or (c >= 0.5 and f < LO_LIM):
                rows.append((f, dom, e[dom], cx, cy, c))
        sg = f"skin GJ {sp['GJ']:.1f} N m2 (EI_out {sp['EI_out']:.1f}, EI_in {sp['EI_in']:.0f}, +{sp['mass_per_m']*0.8*1e3:.1f} g)" if sp else "no skin"
        print(f"- corner {k} ({sg}): {len(res)} modes solved")
        print("  | f (Hz) | dominant part | cx | cy | coupling | in exclusion? | within 20 % of a 1P band? | verdict |"); print("  |---|---|---|---|---|---|---|---|")
        for f, dom, ee, cx, cy, c in rows:
            inb = LO_LIM < f < HI_LIM
            p1 = [(n, lo, hi) for n, lo, hi in BANDS if n.endswith("1P")]
            near1 = any(lo/1.2 < f < 1.2*hi for n, lo, hi in p1)
            verdict = "STRONG in band: FAIL" if (inb and c >= 0.5) else ("weak in band (forced response)" if inb else "outside: pass")
            if inb and c >= 0.5: stop.append((k, f, c, near1))
            print(f"  | {f:.1f} | {dom} {100*ee:.0f}% | {cx:.2f} | {cy:.2f} | {c:.2f} | {'yes' if inb else 'no'} | {'yes' if near1 else 'no'} | {verdict} |")
        below = max([f for (f, e, v, cx, cy) in res if 2 < f < LO_LIM and max(cx, cy) >= 0.5] or [0]); above = min([f for (f, e, v, cx, cy) in res if f >= HI_LIM and max(cx, cy) >= 0.5] or [1e9])
        print(f"  highest strongly coupled mode below the exclusion zone {below:.0f} Hz (limit {LO_LIM:.1f}); lowest above {above:.0f} Hz (limit {HI_LIM:.0f})")
        # forced response sweep
        lo_r, hi_r = (6000, 10500) if PROP == "9" else (4800, 9000)
        sweep = list(range(lo_r, hi_r+1, 25))
        out = []
        for zeta in (0.01, 0.005):
            curve = [(forced(F, res, r, thr(r), zeta), r) for r in sweep]
            wc = max(curve, key=lambda t: t[0].sum()); phys = max((a.sum(), r) for a, r in curve if r <= RPM_CAP)
            cr = max((forced(F, res, r, 0.5, zeta).sum(), r) for r in range(7300, 7601, 25))
            one = forced(F, res, RPM_CAP, 8.75 if PROP == "9" else thr(RPM_CAP), zeta)
            out.append((zeta, wc[0].sum(), wc[1], phys, cr, one.sum()))
        for zeta, w_, r_, ph, cr, one in out:
            print(f"  forced response zeta {zeta*100:.1f} %: worst sum-of-axes {w_:.1f} m/s2 at {r_} rpm (sweep {lo_r}-{hi_r}); all four <= cap {ph[0]:.1f} at {ph[1]} rpm; cruise 7,300-7,600 {cr[0]:.1f} at {cr[1]}; one motor at cap {one:.1f}; limit 30 -> MS {LIM/ph[0]-1:+.2f} (physical envelope)")
    return stop

if __name__ == "__main__":
    lab = f"EIin {EIIN}; {'skin ' + str(SK_PLIES) + ' ply, open<' + str(SK_OPEN) + ' skx' + str(SKIN_SCALE) if SKIN_ON else 'NO SKIN (iter3 CFG baseline)'}; O4 masses {O4}; prop {PROP} in"
    stop = table_for(lab)
    print("\nSTOP-RULE hits (strong coupling >= 0.5 in the exclusion zone):", stop if stop else "none")
