"""QP-4 C1/C2: concept A wing divergence, bending-torsion flutter, elevon flutter and reversal.  python -I flutter_a.py  (numpy, scipy; ~1 min)
Method: (1) Bredt torsion of the tape-skinned foam box + spar, divergence of a clamped semispan rod.  (2) Ritz modal (3 cantilever bending + 3 torsion
modes, spar EI, lumps for fins) with Theodorsen strip aerodynamics, k-method.  (3) 3-DOF (h, alpha, beta) typical section with Theodorsen-Garrick
constants T1..T19 for the elevon.  (4) Torsion-rod control reversal.  All inputs EST unless a source is named; see FLUTTER.md.
Self-checks run first (steady thin-airfoil integration; c = a = -1 flap equals pitch)."""
import math, numpy as np
from scipy.special import hankel2
from scipy.linalg import eig
RHO = 1.225; VD = 24.0; VREQ = 1.2*VD
CH, S_SEMI = 0.245, 0.45; B = CH/2; X_SPAR = 0.060; X_AC = 0.25*CH
A_EA = (X_SPAR-B)/B                   # elastic axis (spar) in semichords from midchord
EL_CF, EL_Y0, EL_Y1 = 0.25, 0.04, 0.34   # BOARD s3 / CAD elevon; chord fraction EST (a_model.py ELEV_FRAC)
C_H = 1-2*EL_CF*1.0                    # hinge position from midchord in semichords: x = (0.75c - 0.5c)/b -> 0.5
C_H = (0.75*CH-0.5*CH)/B
def tube(od, id_):
    I = math.pi/64*(od**4-id_**4); return math.pi/4*(od**2-id_**2), I
CORN = {"kd": dict(E=61e9, G=3e9, Gt=0.4e9, Gf=5e6), "nom": dict(E=70e9, G=3e9, Gt=0.8e9, Gf=7e6), "hi": dict(E=90e9, G=4.5e9, Gt=1.0e9, Gf=9e6)}
# E, G CF: STRUCTURES.md / fe_a.py (kd 61/3, nom 70/3, hi 90/4.5 GPa).  Gt: packing-tape (BOPP) shear = E/2.8, E 2.3 GPa MD (patent 5118566 / US 9745431 class, searched 2026-11-15) -> 0.8; kd x0.5 (wrinkles, adhesive creep).
# Gf: XPS shear 7 MPa (Ravago XPS LB datasheet, analog product, searched 2026-11-15), +-30 %.
A12, I12 = tube(12e-3, 10e-3)
T_TAPE = 0.05e-3*1.0                     # one layer per side, 0.05 mm film (EST; 65 g/m2 incl. adhesive in K09 sizing.py TAPE_KG_M2)
def GJ_parts(k, box_eff=1.0, hinge_cut=True):
    p = CORN[k]
    J_s = 2*I12; GJ_spar = p["G"]*J_s
    # closed tape box from LE to elevon hinge (0.75 c) in the elevon zone; full chord outside it.  Section 9.5 % t, 23 mm: perimeter of the box
    chord_box = 0.75*CH if hinge_cut else CH
    t_loc = 0.0233*(0.9 if hinge_cut else 1.0)
    Am = 0.68*chord_box*t_loc
    perim = 2*chord_box*1.02 + 2*t_loc
    GJ_box = box_eff*4*Am**2/(perim/(p["Gt"]*T_TAPE))
    return GJ_spar, GJ_box
# ---------------------------------------------------------------- Theodorsen
def Ck(k):
    h1, h0 = hankel2(1, k), hankel2(0, k); return h1/(h1+1j*h0)
def Tc(c, a):
    s = math.sqrt(1-c*c); ac = math.acos(c); T = {}
    T[1] = -(1/3)*s*(2+c*c)+c*ac
    T[3] = -(1/8+c*c)*ac**2+0.25*c*s*ac*(7+2*c*c)-(1/8)*(1-c*c)*(5*c*c+4)
    T[4] = -ac+c*s
    T[5] = -(1-c*c)-ac**2+2*c*s*ac
    T[7] = -(1/8+c*c)*ac+(1/8)*c*s*(7+2*c*c)
    T[8] = -(1/3)*s*(2*c*c+1)+c*ac
    T[9] = 0.5*((1/3)*s**3+a*T[4])
    T[10] = s+ac
    T[11] = (2-c)*s+(1-2*c)*ac
    T[12] = (2+c)*s-(2*c+1)*ac
    T[13] = -0.5*(T[7]+(c-a)*T[1])
    T[15] = T[4]+T[10]
    T[16] = T[1]-T[8]-(c-a)*T[4]+0.5*T[11]
    T[17] = -2*T[9]-T[1]+(a-0.5)*T[4]
    T[18] = T[5]-T[4]*T[10]
    T[19] = -0.5*T[4]*T[11]
    return T
SB = -1.0
def aero3(k, b, a, c, rho=RHO):
    """Aerodynamic generalised-force matrix per unit span, F = omega^2 * Ahat @ [h, alpha, beta]  (h down, alpha nose-up, beta TE-down;
    P down-positive, M about EA nose-up, M_beta about the hinge in the beta sense).  V = omega b / k, evaluated at omega = 1."""
    V = b/k; w = 1.0; T = Tc(c, a); C = Ck(k); pi = math.pi
    # coefficient rows over q = [h, alpha, beta] with h''=-h, x' = i x, x''=-x (omega = 1)
    d1 = 1j; d2 = -1.0
    Q = np.array([d1, V, V*T[10]/pi + b*T[11]/(2*pi)*d1], dtype=complex)    # downwash vector: h' + V alpha + b(1/2-a) alpha' + ...
    Q[1] = V + b*(0.5-a)*d1
    P = -rho*b*b*np.array([d2*pi, V*pi*d1-pi*b*a*d2, -V*T[4]*d1-T[1]*b*d2]) - 2*pi*rho*V*b*C*Q
    Ma = rho*b*b*np.array([pi*a*b*d2, -V*b*pi*(0.5-a)*d1-b*b*pi*(1/8+a*a)*d2, -V*V*T[15]-V*b*T[16]*d1+b*b*(T[7]+(c-a)*T[1])*d2]) + 2*pi*rho*V*b*b*(a+0.5)*C*Q
    Mb = rho*b*b*np.array([T[1]*b*d2, -2*T[13]*b*b*d2 - V*b*T[17]*d1, (T[3]/pi)*b*b*d2 - (V*V*T[18]/pi) + SB*(V*b*T[19]/pi)*d1]) - rho*V*b*b*T[12]*C*Q
    return np.array([P, Ma, Mb])
def steady_check(c, a, b=1.0, V=1.0):
    """steady thin-airfoil integration vs the T-formulas (beta = 1 rad, alpha = 0)."""
    n = 4000; th = (np.arange(n)+0.5)*math.pi/n; x = -b*np.cos(th); xh = c*b
    slope = np.where(x > xh, -1.0, 0.0)
    A0 = -(1/math.pi)*np.sum(slope)*math.pi/n
    An = [(2/math.pi)*np.sum(slope*np.cos(m*th))*math.pi/n for m in range(1, 12)]
    dcp = 4*(A0/np.tan(th/2)+sum(An[m-1]*np.sin(m*th) for m in range(1, 12)))
    dp = 0.5*RHO*V*V*dcp; dx = b*np.sin(th)*math.pi/n
    xa = a*b
    Ma_num = np.sum(dp*(xa-x)*dx); Mb_num = -np.sum(np.where(x > xh, dp*(x-xh), 0)*dx)
    Am = aero3(1e-6, b, a, c)   # k -> 0 (steady), column beta
    # at tiny k, omega=1, V=b/k huge; normalise to V=1: forces scale V^2
    scale = (1.0/(b/1e-6))**2
    return Ma_num, Am[1, 2].real*scale, Mb_num, Am[2, 2].real*scale
def selfcheck():
    out = []
    for c, a in ((0.5, -0.5), (0.2, -0.3)):
        r = steady_check(c, a); out.append((c, a, r))
    A = aero3(0.4, 1.0, -1.0, -1.0)
    sym = np.max(np.abs(A[2, :2]-A[1, :2])) , abs(A[1, 2]-A[1, 1]), abs(A[2, 2]-A[1, 1])
    return out, sym
# ---------------------------------------------------------------- flutter solver (k-iteration continuation per mode, V upward)
def track_modes(M, K, ndof, amat, Vgrid, b):
    """amat(k) -> ndof x ndof aerodynamic matrix (omega = 1 normalisation).  Returns {mode: [(V, g, f_Hz)]}."""
    w0 = np.sqrt(np.abs(np.sort(np.real(eig(K, M)[0])))); out = {}
    for j in range(len(w0)):
        w = w0[j]; rows = []
        for V in Vgrid:
            gi = 0.0
            for it in range(80):
                k = max(w*b/V, 1e-3)
                lam, _ = eig(K, M+amat(k))
                g_all = -lam.imag/lam.real; w_all = np.sqrt(np.abs(lam.real)*(1+g_all**2))
                i = int(np.argmin(np.abs(w_all-w))); gi = g_all[i]
                if abs(w_all[i]-w) < 1e-6*w: w = w_all[i]; break
                w = 0.5*w+0.5*w_all[i]
            rows.append((V, gi, w/(2*math.pi)))
        out[j] = rows
    return out
def first_flutter(tr):
    best = None
    for j, rows in tr.items():
        if rows[0][1] > 0.0 and (best is None or rows[0][0] < best[0]): best = (rows[0][0], rows[0][2], j)   # already unstable at the lowest V
        for r0, r1 in zip(rows[:-1], rows[1:]):
            if r0[1] < 0 <= r1[1] and (r1[1]-r0[1]) < 0.6:
                t = -r0[1]/(r1[1]-r0[1]); V = r0[0]+(r1[0]-r0[0])*t; f = r0[2]+(r1[2]-r0[2])*t
                if best is None or V < best[0]: best = (V, f, j)
    return best
# ---------------------------------------------------------------- wing data (EST; STRUCTURES.md iteration-2 masses, CAD positions)
def wing_mass():
    """(m' kg/m, S' = m'(xcg-xea), I'_EA kg m, xcg m from LE); components (g, x_cg from LE, extent); EA at the spar."""
    comp = [(A12*1600*0.9*1e3, X_SPAR, 0.012), (95.3, 0.098, 0.245), (24.2, 0.122, 0.245), (14.0, 0.15, 0.03), (8.0, 0.08, 0.05)]
    mt = sum(c[0] for c in comp); m = mt*1e-3/0.9
    xcg = sum(c[0]*c[1] for c in comp)/mt
    I = sum(c[0]*1e-3/0.9*(c[2]**2/12+(c[1]-X_SPAR)**2) for c in comp)
    return m, m*(xcg-X_SPAR), I, xcg
def fin_lump():
    A16, _ = tube(16e-3, 14e-3); A14, _ = tube(14e-3, 12e-3)
    comp = [(A16*1600*0.36*1e3, 0.294), (0.0432*3e-3*30*1e3, 0.255), (2*0.0432*55, 0.255), (5.0, 0.30), (4.0, 0.24), (A14*1600*0.227*1e3, 0.177)]
    mt = sum(c[0] for c in comp); xcg = sum(c[0]*c[1] for c in comp)/mt
    I = sum(c[0]*1e-3*(c[1]-X_SPAR)**2 for c in comp)
    return mt*1e-3, xcg, I
def ritz(corner="nom", GJ=None, fins=True, motors=False, nb=3, nt=3, n=600):
    p = CORN[corner]; EI = p["E"]*I12
    if GJ is None: GJ = sum(GJ_parts(corner, hinge_cut=False))
    y = (np.arange(n)+0.5)*S_SEMI/n; dy = S_SEMI/n; L = S_SEMI
    bl = [1.8751041, 4.6940911, 7.8547574][:nb]; ph, phpp = [], []
    for bi in bl:
        sg = (math.cosh(bi)+math.cos(bi))/(math.sinh(bi)+math.sin(bi)); z = bi*y/L
        ph.append(np.cosh(z)-np.cos(z)-sg*(np.sinh(z)-np.sin(z)))
        phpp.append((bi/L)**2*(np.cosh(z)+np.cos(z)-sg*(np.sinh(z)+np.sin(z))))
    ps, psp = [], []
    for j in range(nt):
        kk = (2*j+1)*math.pi/(2*L); ps.append(np.sin(kk*y)); psp.append(kk*np.cos(kk*y))
    m, Sa, Ia, xcg = wing_mass(); N = nb+nt; M = np.zeros((N, N)); K = np.zeros((N, N))
    z = np.zeros(n); sh = np.array(ph+[z]*nt); st = np.array([z]*nb+ps)
    M += (sh*m*dy)@sh.T+(sh*Sa*dy)@st.T+(st*Sa*dy)@sh.T+(st*Ia*dy)@st.T
    for i in range(nb):
        for j in range(nb): K[i, j] = np.sum(EI*phpp[i]*phpp[j])*dy
    for i in range(nt):
        for j in range(nt): K[nb+i, nb+j] = np.sum(GJ*psp[i]*psp[j])*dy
    def at(yv):
        i = min(int(yv/dy), n-1); return np.array([f[i] for f in ph]+[0]*nt), np.array([0]*nb+[f[i] for f in ps])
    if fins:      # one fin per semispan (symmetric mode)
        mf, xf, If = fin_lump(); hv, tv = at(0.38); d = xf-X_SPAR
        M += mf*np.outer(hv, hv)+mf*d*(np.outer(hv, tv)+np.outer(tv, hv))+If*np.outer(tv, tv)
    if motors:    # 2 x 81 g per semispan at y 0.228, x -0.075, rigid on the wing (optimistic: really on the soft cage)
        hv, tv = at(0.228); mm = 2*0.081; d = -0.075-X_SPAR
        M += mm*np.outer(hv, hv)+mm*d*(np.outer(hv, tv)+np.outer(tv, hv))+mm*d*d*np.outer(tv, tv)
    return dict(M=M, K=K, sh=sh, st=st, dy=dy, N=N)
def wing_flutter(corner="nom", a=A_EA, cl_scale=1.0, GJ=None, **kw):
    R = ritz(corner, GJ=GJ, **kw); M, K, sh, st, dy, N = R["M"], R["K"], R["sh"], R["st"], R["dy"], R["N"]
    f = np.sqrt(np.abs(np.sort(np.real(eig(K, M)[0]))))/(2*math.pi)
    def Amod(k):
        A2 = aero3(k, B, a, C_H)[:2, :2]*cl_scale
        return (sh*dy)@sh.T*A2[0, 0]+(sh*dy)@st.T*A2[0, 1]+(st*dy)@sh.T*A2[1, 0]+(st*dy)@st.T*A2[1, 1]
    tr = track_modes(M, K, N, Amod, np.arange(4, 100.1, 1.0), B)
    return f, first_flutter(tr)
# ---------------------------------------------------------------- divergence and reversal
CLA3D = 3.7; CLA2D = 2*math.pi      # a_aero.py Helmbold 3.7 /rad (qp/A/sitl/a_aero.py CLA); 2-D strip 2 pi is the conservative bound
def q_div(GJ, e_frac, cla=CLA3D, s=S_SEMI):
    e = e_frac*CH
    return float("inf") if e <= 0 else (math.pi/2)**2*GJ/(CH**2*e*cla*s**2)
def reversal(GJ, e_frac, scale=1.0, qs=None, K_hinge=None):
    """roll effectiveness vs q, elevon y 0.04-0.34, torsion rod clamped at the root. Returns (q_reversal, curve)."""
    n = 150; y = np.linspace(0, S_SEMI, n+1); h = y[1]-y[0]; e = e_frac*CH; T = Tc(C_H, A_EA)
    f3 = (CLA3D/CLA2D)*scale
    cla = CLA3D*scale; cld = 2*T[10]*f3; cm = 0.5*(-T[15]+2*(A_EA+0.5)*T[10])*f3
    eff = 1.0
    el = ((y >= EL_Y0) & (y <= EL_Y1)).astype(float)
    qs = np.linspace(5, 4000, 300) if qs is None else qs; out = []
    for q in qs:
        Mx = np.zeros((n, n)); r = np.zeros(n)
        for ii in range(n):
            i = ii+1
            Mx[ii, ii] = -2*GJ/h**2+q*CH*e*cla
            if ii > 0: Mx[ii, ii-1] = GJ/h**2
            if i < n: Mx[ii, ii+1] = GJ/h**2
            else: Mx[ii, ii-1] = 2*GJ/h**2
            r[ii] = -q*CH*CH*cm*el[i]
        th = np.concatenate([[0], np.linalg.solve(Mx, r)]); lift = q*CH*(cla*th+cld*el)
        out.append((q, np.sum(y*lift)*h))
    arr = np.array(out); qr = float("inf")
    for i in range(len(arr)-1):
        if arr[i, 1] > 0 >= arr[i+1, 1]:
            qr = arr[i, 0]+(arr[i+1, 0]-arr[i, 0])*arr[i, 1]/(arr[i, 1]-arr[i+1, 1]); break
    return qr, arr
# ---------------------------------------------------------------- elevon 3-DOF typical section at 0.7 span
ME_EL = 0.010   # elevon mass each, kg (foam 4.4 + tape 2.4 + hinge/horn block 3 g, structures_a.py block 3 g; EST)
def elevon_section(fh, fa, Kb, xb_bal=0.0, mbal=0.0, a=A_EA):
    """per unit span; Kb = hinge stiffness per elevon (N m/rad), spread over the 0.30 m elevon; mbal kg per m span at xb_bal m ahead of the hinge."""
    m, Sa, Ia, xcg = wing_mass(); span_e = EL_Y1-EL_Y0; me = ME_EL/span_e
    xh_le = B+C_H*B; xe_le = xh_le+0.35*EL_CF*CH; xea = a*B
    mw = m-me; xw = (m*xcg-me*xe_le)/mw
    d_w = np.array([1.0, (xw-B)-xea, 0.0]); d_e = np.array([1.0, (xe_le-B)-xea, (xe_le-B)-C_H*B])
    Ie = me*(EL_CF*CH)**2/12
    M = mw*np.outer(d_w, d_w)+me*np.outer(d_e, d_e)+Ie*np.outer([0, 1, 1], [0, 1, 1])
    M[1, 1] += max(Ia-(mw*(xw-X_SPAR)**2+me*(xe_le-X_SPAR)**2), 0)   # remaining own inertia of the wing parts
    if mbal > 0:
        d_b = np.array([1.0, (xh_le-xb_bal-B)-xea, -xb_bal]); M += mbal*np.outer(d_b, d_b)
    K = np.diag([M[0, 0]*(2*math.pi*fh)**2, M[1, 1]*(2*math.pi*fa)**2, Kb/span_e])
    return M, K
def elevon_flutter(fh, fa, Kb, **kw):
    M, K = elevon_section(fh, fa, Kb, **kw)
    tr = track_modes(M, K, 3, lambda k: aero3(k, B, A_EA, C_H), np.arange(4, 100.1, 1.0), B)
    return first_flutter(tr)
def hinge_stiffness_aero(V):
    T = Tc(C_H, A_EA); return RHO*V*V*B*B*(-T[18]-T[12]*T[10])/math.pi      # d(M_beta)/d(beta) steady, per unit span (negative = restoring)
def run_all():
    L = []
    def P(s=""): print(s, flush=True); L.append(s)
    o, s = selfcheck()
    P("Self-checks (steady thin-airfoil integration / T-formula): " + "; ".join("c=%.1f a=%.1f: M_alpha %.4f/%.4f, M_beta %.4f/%.4f" % (c, a, r[0], r[1], r[2], r[3]) for c, a, r in o)
      + ". c = a = -1 flap-equals-pitch residuals %.1e, %.1e, %.1e." % tuple(s)); P()
    qreq = 0.5*RHO*VREQ**2
    P("## 1 GJ and divergence"); P("| corner | GJ spar | GJ tape box (hinge-cut) | GJ elevon zone | GJ full box | e/c at which q_D = q(28.8) | V_D-div at e/c 0.02 / 0.05 / 0.10 (m/s) |"); P("|---|---|---|---|---|---|---|")
    for k in CORN:
        gs, gb = GJ_parts(k); gs2, gb2 = GJ_parts(k, hinge_cut=False); GJ = gs+gb
        ecrit = (math.pi/2)**2*GJ/(CH**2*CLA3D*S_SEMI**2*qreq)/CH
        vd = [math.sqrt(2*q_div(GJ, e)/RHO) for e in (0.02, 0.05, 0.10)]
        P("| %s | %.2f | %.2f | %.2f | %.2f | %.3f | %.0f / %.0f / %.0f |" % (k, gs, gb, GJ, gs2+gb2, ecrit, *vd))
    P("q(28.8 m/s) = %.0f Pa; GJ in N m2." % qreq); P()
    P("## 2 Wing flutter (Ritz + strip Theodorsen)")
    m, Sa, Ia, xcg = wing_mass(); mf, xf, If = fin_lump()
    P("wing m' %.3f kg/m, CG %.3f m from LE (%.2f semichord aft of EA), I'_EA %.2e kg m; fin each %.1f g, CG x %.3f m (%.2f semichord aft of EA), I_EA %.2e; EA a = %.2f; b = %.4f m" % (m, xcg, (xcg-X_SPAR)/B, Ia, mf*1e3, xf, (xf-X_SPAR)/B, If, A_EA, B))
    P("| case | corner | f1..f3 in vacuo (Hz) | flutter V (m/s) | f (Hz) | x VD | G8 |"); P("|---|---|---|---|---|---|---|")
    cases = [("base: fin on tip, no motor credit", dict()), ("fins off", dict(fins=False)), ("motors on the wing (optimistic)", dict(motors=True)), ("EA at a = -0.30", dict(a=-0.30)), ("strip lift x0.59 (3-D CLa)", dict(cl_scale=0.59))]
    for nm, kw in cases:
        for k in ("kd", "nom", "hi"):
            f, ff = wing_flutter(k, **kw)
            P("| %s | %s | %.1f / %.1f / %.1f | %s | %s | %s | %s |" % (nm, k, f[0], f[1], f[2], "%.1f" % ff[0] if ff else ">100", "%.1f" % ff[1] if ff else "-", "%.2f" % (ff[0]/VD) if ff else ">4", "PASS" if (not ff or ff[0] >= VREQ) else "FAIL"))
    P()
    P("## 3 Torsion needed (nom corner, base case): flutter V vs GJ"); P("| GJ (N m2) | flutter V (m/s) | x VD |"); P("|---|---|---|")
    for gj in (2.0, 3.0, 4.5, 6.0, 8.0, 12.0, 20.0):
        f, ff = wing_flutter("nom", GJ=gj); P("| %.1f | %s | %s |" % (gj, "%.1f" % ff[0] if ff else ">100", "%.2f" % (ff[0]/VD) if ff else ">4"))
    P()
    P("## 4 Elevon flutter (3-DOF section at 0.7 span; wing f_h, f_a from section 2 nominal base)")
    f, _ = wing_flutter("nom"); fh, fa = f[0], f[1]
    P("f_h %.1f Hz, f_alpha %.1f Hz (modal, nom); elevon %.0f g, CG 0.35 of its chord aft of the hinge; hinge at %.2f semichord" % (fh, fa, ME_EL*1e3, C_H))
    P("| K_hinge per elevon (N m/rad) | f_beta in vacuo (Hz) | flutter V (m/s) | f (Hz) | x VD |"); P("|---|---|---|---|---|")
    for Kb in (0.0, 0.02, 0.05, 0.2, 1.0, 5.0):
        M, K = elevon_section(fh, fa, Kb); fb = math.sqrt(K[2, 2]/M[2, 2])/(2*math.pi) if Kb > 0 else 0
        ff = elevon_flutter(fh, fa, Kb); P("| %.2f | %.0f | %s | %s | %s |" % (Kb, fb, "%.1f" % ff[0] if ff else ">100", "%.1f" % ff[1] if ff else "-", "%.2f" % (ff[0]/VD) if ff else ">4"))
    P("Mass-balanced (lead ahead of the hinge so elevon + lead CG sits on the hinge), floating (K = 0.02) and servo-held (0.2):"); P("| lead per elevon (g) | arm ahead of hinge (mm) | K = 0.02 | K = 0.2 | K = 5 |"); P("|---|---|---|---|---|")
    xe = 0.35*EL_CF*CH; span_e = EL_Y1-EL_Y0
    for arm, ob in ((0.030, 1.0), (0.030, 1.5), (0.045, 1.5)):
        gl = ME_EL*xe/arm*1e3*ob
        row = []
        for Kb in (0.02, 0.2, 5.0):
            ff = elevon_flutter(fh, fa, Kb, xb_bal=arm, mbal=gl*1e-3/span_e); row.append("%.1f" % ff[0] if ff else ">100")
        P("| %.1f (x%.1f) | %.0f | %s |" % (gl, ob, arm*1e3, " | ".join(row)))
    P()
    P("## 5 Control reversal (torsion rod, elevon y 0.04-0.34)"); P("| corner | GJ | e/c | 3-D lift: q_R (Pa) / V_R (m/s) | 2-D strip: V_R (m/s) |"); P("|---|---|---|---|---|")
    for k in ("kd", "nom", "hi"):
        GJ = sum(GJ_parts(k))
        for e in (0.0, 0.05, 0.10):
            q3, _ = reversal(GJ, e); q2, _ = reversal(GJ, e, scale=CLA2D/CLA3D)
            P("| %s | %.2f | %.2f | %s | %s |" % (k, GJ, e, "%.0f / %.0f" % (q3, math.sqrt(2*q3/RHO)) if q3 < 1e9 else "none below 4000 Pa", "%.0f" % math.sqrt(2*q2/RHO) if q2 < 1e9 else "none <4000 Pa"))
    P()
    P("Aerodynamic hinge stiffness at 24 / 28.8 m/s per elevon (steady, thin airfoil): %.3f / %.3f N m/rad (negative = restoring)" % (hinge_stiffness_aero(24)*(EL_Y1-EL_Y0), hinge_stiffness_aero(28.8)*(EL_Y1-EL_Y0)))
    T = Tc(C_H, A_EA); Hd = RHO*28.8**2*B*B*(T[18]/-math.pi)*(0)  # placeholder not used
    return L
if __name__ == "__main__":
    out = run_all()
    import os; open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "flutter_run.md"), "w").write("\n".join(out))
