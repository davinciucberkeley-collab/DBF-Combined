"""A-P15 directional stability (AM-065, D-260): Cn_beta and the lateral-directional modes of concept A in cruise.
Reproduce: python -I latdir_a.py [V m/s, default 18] [cg mm, default 23.49] [prop dCN/dbeta per disc, default 0.3]
Derivatives Y_beta, L_beta, N_beta, L_p, N_r(fin) come from the SITL aero model a_aero.airframe() by central differences at the trimmed cruise state
(wing + elevons + fins as flown in SITL). Terms the plant does not model are added by shown strip-theory formulas (EST):
  wing Clr = CL/3 (rectangular unswept wing: dL(y) = q c CL 2 r y / V  ->  Cl = (c b / 3 S) CL r_hat = CL/3 r_hat),
  wing Cnp = -CL/8 (classical unswept-wing textbook estimate, induced drag tilt; source not opened, EST),
  wing Cnr = -CD0/3 (profile drag, same strip integral; EST).
Propellers (4 x APC 9x4.5MR, disc 0.041 m2 each, about 0.10 m ahead of the CG in cruise) act as a forward fin: dN/dbeta = -4 kp q A_disc x_p,
kp = prop normal-force slope per rad on disc area, EST 0.3 (range 0-0.6 reported). Inertias from cad_mass.json (Ixz not available: 0, '-'). Not modelled: a roll arm on the fin side force (the plant's Cl_beta is CLB only) and the
induced-drag part of wing Cn_r; see D-260 for the bound.
Pass lines (A-P15): Cn_beta >= 0.03 /rad; no spiral divergence (spiral root < 0), else its time to double is reported."""
import sys, os, math, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a_aero as A
V = float(sys.argv[1]) if len(sys.argv) > 1 else 18.0
CG = (float(sys.argv[2]) if len(sys.argv) > 2 else 23.49) * 1e-3
KP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
M = 1.881; G = 9.80665
A.set_cg(CG)
cm = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cad_mass.json")))["I_cad_axes_kgm2"]
IXX, IZZ = cm["Ixx"], cm["Izz"]

def trim():
    a, d = 0.1, 0.0
    for _ in range(100):
        def g(a, d):
            F, T, _ = A.airframe(V*math.cos(a), 0, V*math.sin(a), 0, 0, 0, d, d)
            return -(F[2]*math.cos(a) - F[0]*math.sin(a)) - M*G, T[1]
        r = g(a, d); h = 1e-6
        ja = [(x-y)/h for x, y in zip(g(a+h, d), r)]; jd = [(x-y)/h for x, y in zip(g(a, d+h), r)]
        det = ja[0]*jd[1]-jd[0]*ja[1]
        da = (-r[0]*jd[1]+jd[0]*r[1])/det; dd = (-ja[0]*r[1]+ja[1]*r[0])/det
        a += da; d += dd
        if abs(da)+abs(dd) < 1e-12: break
    return a, d
al, de = trim()
u, w = V*math.cos(al), V*math.sin(al)
q = 0.5*A.RHO*V*V; S, b = A.S_W, A.B_W
def FT(v=0, p=0, r=0): return A.airframe(u, v, w, p, 0, r, de, de)
def d(i, j, k, h):  # derivative of force/moment i (0 F / 1 T), component j, wrt input k
    kw = {k: h}; P = FT(**kw); kw = {k: -h}; Mn = FT(**kw)
    return (P[i][j] - Mn[i][j]) / (2*h)
hv, hp = 1e-3, 1e-3
Yv, Lv, Nv = d(0, 1, "v", hv), d(1, 0, "v", hv), d(1, 2, "v", hv)
Lp, Np = d(1, 0, "p", hp), d(1, 2, "p", hp)
Lr, Nr, Yr = d(1, 0, "r", hp), d(1, 2, "r", hp), d(0, 1, "r", hp)
CL = M*G/(q*S); CD0 = A.CD0
# per-rad coefficient conversions: beta = v / V; p_hat = p b / 2V
Cnb_model = Nv*V/(q*S*b); Clb_model = Lv*V/(q*S*b); Cyb_model = Yv*V/(q*S)
Clp = Lp*2*V/(q*S*b*b); Cnp_model = Np*2*V/(q*S*b*b); Clr_model = Lr*2*V/(q*S*b*b); Cnr_model = Nr*2*V/(q*S*b*b)
Clr = Clr_model + CL/3; Cnp = Cnp_model - CL/8; Cnr = Cnr_model - CD0/3
XP = abs(-0.075 - CG) + 0.0   # props: hub plane x -0.075 m in the CAD frame (landing_a ITEMS), ahead of the CG
AD = math.pi*(9*0.0254/2)**2
Cnb_prop = -4*KP*AD*XP/(S*b); Cyb_prop = 4*KP*AD/S * (-1)
Cnb = Cnb_model + Cnb_prop; Cyb = Cyb_model + Cyb_prop; Clb = Clb_model
# dimensional lateral model, states [beta, p, r, phi] (stability-ish axes, small alpha, Ixz = 0)
Yb, Lb, Nb = q*S*Cyb/(M*V), q*S*b*Clb/IXX, q*S*b*Cnb/IZZ
LP, NP_ = q*S*b*b*Clp/(2*V*IXX), q*S*b*b*Cnp/(2*V*IZZ)
LR, NR = q*S*b*b*Clr/(2*V*IXX), q*S*b*b*Cnr/(2*V*IZZ)
Amat = np.array([[Yb, math.sin(al), -math.cos(al), G*math.cos(al)/V],
                 [Lb, LP, LR, 0.0],
                 [Nb, NP_, NR, 0.0],
                 [0.0, 1.0, math.tan(al), 0.0]])
ev = np.linalg.eigvals(Amat)
out = dict(V=V, cg_mm=CG*1e3, alpha_deg=math.degrees(al), elevon_trim_deg=-math.degrees(de), CL=CL, kp=KP,
           Cn_beta_model=Cnb_model, Cn_beta_prop=Cnb_prop, Cn_beta=Cnb, Cl_beta=Clb, Cy_beta=Cyb, Cl_p=Clp, Cn_p=Cnp, Cl_r=Clr, Cn_r=Cnr,
           Cl_r_model=Clr_model, Cn_p_model=Cnp_model, Cn_r_model=Cnr_model, eig=[[float(e.real), float(e.imag)] for e in ev])
real = [e for e in ev if abs(e.imag) < 1e-9]; cplx = [e for e in ev if e.imag > 1e-9]
sp = max(real, key=lambda e: e.real) if real else None
out["spiral_root"] = float(sp.real) if sp is not None else None
out["spiral_t_double_s"] = (math.log(2)/sp.real) if sp is not None and sp.real > 0 else None
out["spiral_t_half_s"] = (math.log(2)/-sp.real) if sp is not None and sp.real < 0 else None
if cplx:
    dr = cplx[0]; wn = abs(dr); out["dutch_roll_wn"] = float(wn); out["dutch_roll_zeta"] = float(-dr.real/wn)
print(json.dumps(out, indent=1))
