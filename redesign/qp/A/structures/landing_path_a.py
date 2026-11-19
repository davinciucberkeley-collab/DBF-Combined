"""T-064r F1/F10: every part on the CAD foot load path, checked on CAD dimensions at the loads of the rigid-body landing sim.
    python -I landing_path_a.py [--legacy] [--quick] > out.txt          (about 2-3 min; --quick = fewer cases)
Categories: rigid-body dynamics (landing_a.py force histories, CAD ground plane and CG) + hand-calculation part checks (statics, beam / tube / bond theory).  No FEA.
Load path (CAD, redesign/qp/A/cad/amodel): foot pad GER-002 (EVA/PE 12x15x30, PSA to the shoe plate) -> shoe GER-001 (PETG: plate 5.5x21x15, ring 12 long on the fin tube, epoxy)
-> fin tube FIN-001 16x14 -> root block FIN-003 (PETG: ring 60 long on the tube, socket 19x19 over x 0.255-0.286) -> rib FIN-002 14x12 -> saddle FIN-005 (PETG: socket
over x 0.0665-0.0905, ring 60 long on the spar) -> spar WNG-002 12x10.  Dimensions are read from wing.py / electrical.py / common.py; the few that are only in the build
code (shoe plate, pad box) are taken from electrical.py build_landing and checked against the stub-built part boxes below.
Factors: KF 1.5x1.15 (CF) and KP 1.5x1.15x1.25 (printed / bonded) as structures_a.py.  Criterion RF >= 1.0 (KF / KP already carry the margin; F6).
Allowable labels: EST = project estimate carried from structures_a.py (K09-L C2 / C4 / C6 values, no coupon); PSA allowables have no source in the repo: EST.
Frames: body x aft (normal to the ground in the stance), y span, z cruise-up; foot forces fb from landing_a.simulate(trace=True)."""
import math, sys, os, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import landing_a as L
cadg = L.cad_geom()
from amodel import electrical as E, wing as W, common as C        # noqa: E402  (landing_a.cad_geom put the CAD folder on sys.path)

KF = 1.5*1.15; KP = KF*1.25
SIG, TAU = 350e6, 30e6                    # CF tube EST (structures_a.py SPAR_SIG / SPAR_TAU)
PETG_ILAY, PETG_BEAR = 9.5e6, 20e6        # EST (structures_a.py)
BOND = 2.0e6                              # neat epoxy on CF / PETG EST (structures_a.py BOND_TAU)
PSA = 0.10e6                              # EST: project foam-bond value (C6, D-213 shoe bond); no PSA / double-sided-tape data sheet in the repo
SPAR_HOOP = 40e6                          # EST (structures_a.py)
XF, YF, ZF = cadg['x_foot'], C.YFIN, cadg['z_foot']
XT, FH = C.XFIN_T, C.FIN_H
FOD, FID = C.FIN_OD, C.FIN_ID
ROD, RID, RX0, RX1 = W.RIB_OD, W.RIB_ID, W.RIB_X0, W.RIB_X1
SX, SOD, SID = C.SPAR_X, C.SPAR_OD, C.SPAR_ID
# printed-part dimensions (electrical.py build_landing; wing.py build_fins)
PAD_Y, PAD_Z, PAD_X = 0.015, 0.012, XF-(XT+0.0135)
PLATE_X = XT+0.008                        # shoe plate front face; ring outer radius 10.5 mm
RING_SH_L, RING_SH_RO = 0.012, 0.0105
RING_BL_L, RING_BL_RO = 0.060, 0.0115
BLK_X0, BLK_W = 0.2550, 0.019
SAD_X0, SAD_X1, SAD_W, SAD_RO, SAD_L = 0.0665, 0.0905, 0.019, 0.0105, 0.060


def tube(od, id_):
    A = math.pi/4*(od**2-id_**2); I = math.pi/64*(od**4-id_**4); return A, I, I/(od/2)
A_F, I_F, Z_F = tube(FOD, FID); A_R, I_R, Z_R = tube(ROD, RID); A_S, I_S, Z_S = tube(SOD, SID)
SECT = {}                                  # name -> (name, label, [fin][rf array over time]) filled below


def feet_pos(k, j):                        # fin k (0 = +y), foot j (0 = +z, 1 = -z) -> contact point at the pad centre
    return np.array([XF, (1 if k == 0 else -1)*YF, (1 if j == 0 else -1)*ZF])
def M_about(FBt, k, S, feet=(0, 1)):
    """force and moment at point S (n,3) from the listed feet of fin k; FBt: (n,4,3)."""
    F = 0; M = 0
    for j in feet:
        f = FBt[:, 2*k+j, :]; r = feet_pos(k, j)-np.array(S)
        F = F+f; M = M+np.cross(np.broadcast_to(r, f.shape), f)
    return F, M
def S_(k, x, z=0.0): return (x, (1 if k == 0 else -1)*YF, z)
n_ = lambda v: np.linalg.norm(v, axis=1)
def comb(*pairs): return 1.0/np.maximum(np.sqrt(sum((a/b)**2 for a, b in pairs)), 1e-12)


def bond_rf(axial, torque, Mb, V, D, Lb, tau_a=BOND, K=KP):
    """epoxy sleeve bond on a tube of diameter D, length Lb.  Returns three RF arrays: shear (axial + torsion, vs tau_a), bearing on the compression side
    (6M/(D L^2) + V/(D L) vs PETG_BEAR) and peel on the tension side (same stress vs BOND, EST lower bound: no peel allowable exists in the repo)."""
    r = D/2; tau = np.hypot(np.abs(axial)/(math.pi*D*Lb), np.abs(torque)/(2*math.pi*r*r*Lb))*K
    sg = (6*np.abs(Mb)/(D*Lb**2)+np.abs(V)/(D*Lb))*K
    return (tau_a/np.maximum(tau, 1e-9), PETG_BEAR/np.maximum(sg, 1e-9), BOND/np.maximum(sg, 1e-9))
def rect_rf(Fn, V, Mt, Mb1, Mb2, a, b, tau_a, sig_a, K=KP, beta=0.21):
    """rectangular section a (along u) x b (along v): normal Fn, shear V, torsion Mt, bending Mb1 (about u: stress varies over b), Mb2 (about v: varies over a)."""
    A = a*b; s = (np.abs(Mb1)/(a*b*b/6)+np.abs(Mb2)/(b*a*a/6)+np.abs(Fn)/A)*K
    t = (np.abs(V)/A+np.abs(Mt)/(beta*max(a, b)*min(a, b)**2))*K
    return comb((s, sig_a), (t, tau_a))
def tube_rf(F_ax, Mt, Mb, A, Z, K=KF):
    s = K*(Mb/Z+np.abs(F_ax)/A); t = K*np.abs(Mt)/(2*Z); return comb((s, SIG), (t, TAU))
def put(out, name, lab, arr): out.setdefault(name, (lab, []))[1].append(arr)
def putb(out, name, lab, rfs):
    put(out, name+' - shear (axial + torsion)', lab, rfs[0]); put(out, name+' - bearing, compression side', 'EST PETG_BEAR 20 MPa', rfs[1])
    put(out, name+' - BOND INTEGRITY (coupon, outside RF minimum; T-069 F-3)', 'EST BOND 2.0 MPa', rfs[2])
def chord(Ro, dx): return 2*math.sqrt(max(Ro*Ro-dx*dx, 0.0))


def checks(FBt):
    """-> {name: (label, rf array (2 fins min))}.  Axis conventions: tube z, rib x, spar y."""
    out = {}
    for k in (0, 1):
        # P1 pad PSA (pad -> shoe plate), interface plane x = XT + 0.0135, 15 (y) x 12 (z); loads of one foot about the interface centre
        for j in (0, 1):
            f = FBt[:, 2*k+j, :]; ft = f[:, 1:]; lever = PAD_X
            Mz_i = np.abs(f[:, 1])*lever; My_i = np.abs(f[:, 2])*lever             # friction force at the aft face acts PAD_X from the interface
            A = PAD_Y*PAD_Z; tau = n_(ft)/A*KP
            peel = (Mz_i/(PAD_Z*PAD_Y**2/6)+My_i/(PAD_Y*PAD_Z**2/6))*KP            # tension at the edge, no compressive relief (conservative)
        # P2 shoe plate to ring junction (PETG), plane x = PLATE_X; chord 13.6 mm (y) x 12 (z); loads about its centre
        for j in (0, 1):
            Sj = S_(k, PLATE_X, (1 if j == 0 else -1)*(FH-0.006))
            F, M = M_about(FBt, k, Sj, (j,)); a = chord(RING_SH_RO, PLATE_X-XT)
            out.setdefault('P2 shoe plate-to-ring junction, PETG (13.6 x 12 mm)', ('EST PETG_ILAY 9.5 MPa', []))[1].append(
                rect_rf(F[:, 0], np.hypot(F[:, 1], F[:, 2]), M[:, 0], M[:, 1], M[:, 2], a, RING_SH_L, PETG_ILAY, PETG_ILAY))
        # P3 shoe ring bond on the tube end (epoxy, D 16, L 12): axis z
        for j in (0, 1):
            Sj = S_(k, XT, (1 if j == 0 else -1)*(FH-0.006))
            F, M = M_about(FBt, k, Sj, (j,))
            putb(out, 'P3 shoe ring epoxy bond on fin tube (D16 x 12)', 'EST BOND 2.0 MPa',
                bond_rf(F[:, 2], M[:, 2], np.hypot(M[:, 0], M[:, 1]), np.hypot(F[:, 0], F[:, 1]), FOD, RING_SH_L))
        # P4 fin tube 16x14 at the root block edge (z = +-0.03), one foot per half
        for j in (0, 1):
            Sj = S_(k, XT, (1 if j == 0 else -1)*0.030)
            F, M = M_about(FBt, k, Sj, (j,))
            out.setdefault('P4 fin tube 16x14 at root-block edge', ('EST 350 / 30 MPa', []))[1].append(tube_rf(F[:, 2], M[:, 2], np.hypot(M[:, 0], M[:, 1]), A_F, Z_F))
        # P5 root block ring bond on the tube (D16 x 60), both feet about the block centre
        S0 = S_(k, XT, 0.0); F, M = M_about(FBt, k, S0)
        putb(out, 'P5 root-block ring epoxy bond on fin tube (D16 x 60)', 'EST BOND 2.0 MPa', 
            bond_rf(F[:, 2], M[:, 2], np.hypot(M[:, 0], M[:, 1]), np.hypot(F[:, 0], F[:, 1]), FOD, RING_BL_L))
        # P6 root block ring-to-socket junction (PETG): plane x = RX1, chord y x 19 (z)
        Sj = S_(k, RX1, 0.0); F, M = M_about(FBt, k, Sj); a = chord(RING_BL_RO, XT-RX1)
        out.setdefault('P6 root-block ring-to-socket junction, PETG (%.1f x 19 mm)' % (a*1e3), ('EST PETG_ILAY 9.5 MPa', []))[1].append(
            rect_rf(F[:, 0], np.hypot(F[:, 1], F[:, 2]), M[:, 0], M[:, 1], M[:, 2], a, BLK_W, PETG_ILAY, PETG_ILAY))
        # P7 root block socket: rib bond (D14 x 31) at the socket mouth x = BLK_X0 (rib leaves the socket aft end) -> loads about S(RX1) already include the lever; use the mouth
        Sm = S_(k, BLK_X0, 0.0); F, M = M_about(FBt, k, Sm)
        Lb = RX1-BLK_X0
        putb(out, 'P7 root-block socket: rib epoxy bond / bearing (D14 x 31)', 'EST BOND 2.0 MPa', 
            bond_rf(F[:, 0], M[:, 0], np.hypot(M[:, 1], M[:, 2]), np.hypot(F[:, 1], F[:, 2]), ROD, Lb))
        # P8 root block socket wall (PETG box 19x19 with 14 bore) bending + torsion at the mouth
        Ib = BLK_W**4/12-math.pi*ROD**4/64; Zb = Ib/(BLK_W/2); tw = (BLK_W-ROD)/2; Tb = 2*((BLK_W+ROD)/2)**2*tw
        s = (np.hypot(M[:, 1], M[:, 2])/Zb+np.abs(F[:, 0])/(BLK_W**2-math.pi*ROD**2/4))*KP; t = (np.abs(M[:, 0])/Tb+n_(F[:, 1:])/(4*BLK_W*tw))*KP
        out.setdefault('P8 root-block socket wall, PETG box 19x19 / bore 14, bending + torsion', ('EST PETG_ILAY 9.5 MPa', []))[1].append(comb((s, PETG_ILAY), (t, PETG_ILAY)))
        # P9 rib tube 14x12: free span first section x = SAD_X1 (0.0905) and the AR-012 section x = RX0 (0.0705)
        for nm, x in (('P9a rib tube 14x12 at saddle mouth x 0.0905', SAD_X1), ('P9b rib tube 14x12 at x 0.0705 (AR-012 section)', RX0)):
            F, M = M_about(FBt, k, S_(k, x, 0.0))
            out.setdefault(nm, ('EST 350 / 30 MPa', []))[1].append(tube_rf(F[:, 0], M[:, 0], np.hypot(M[:, 1], M[:, 2]), A_R, Z_R))
        # P10 saddle socket: rib epoxy bond / bearing (D14 x 20) at the mouth x = SAD_X1
        Sm = S_(k, SAD_X1, 0.0); F, M = M_about(FBt, k, Sm); Lb = SAD_X1-RX0
        putb(out, 'P10 saddle socket: rib epoxy bond / bearing (D14 x 20)', 'EST BOND 2.0 MPa', 
            bond_rf(F[:, 0], M[:, 0], np.hypot(M[:, 1], M[:, 2]), np.hypot(F[:, 1], F[:, 2]), ROD, Lb))
        # P11 saddle socket wall (PETG box) bending + torsion at the mouth
        Ibs = SAD_W**4/12-math.pi*ROD**4/64; Zbs = Ibs/(SAD_W/2); tws = (SAD_W-ROD)/2; Tbs = 2*((SAD_W+ROD)/2)**2*tws      # T-069 F-5: P11 section from SAD_W
        s = (np.hypot(M[:, 1], M[:, 2])/Zbs+np.abs(F[:, 0])/(SAD_W**2-math.pi*ROD**2/4))*KP; t = (np.abs(M[:, 0])/Tbs+n_(F[:, 1:])/(4*SAD_W*tws))*KP
        out.setdefault('P11 saddle socket wall, PETG box 19x19 / bore 14, bending + torsion', ('EST PETG_ILAY 9.5 MPa', []))[1].append(comb((s, PETG_ILAY), (t, PETG_ILAY)))
        # P12 saddle socket-to-ring junction (PETG): plane x = SAD_X0, chord z x 19 (y); loads about its centre
        Sj = S_(k, SAD_X0, 0.0); F, M = M_about(FBt, k, Sj); a = chord(SAD_RO, SAD_X0-SX)
        out.setdefault('P12 saddle socket-to-ring junction, PETG (%.1f x 19 mm)' % (a*1e3), ('EST PETG_ILAY 9.5 MPa', []))[1].append(
            rect_rf(F[:, 0], np.hypot(F[:, 1], F[:, 2]), M[:, 0], M[:, 1], M[:, 2], SAD_W, a, PETG_ILAY, PETG_ILAY))   # T-069 F-4: u = y (19 mm), v = z (chord): My (stress over z, Mb1), Mz (stress over y, Mb2)
        # P13 saddle ring epoxy bond on the spar (D12 x 60), axis y; loads about the saddle centre (SX, YF, 0)
        Ss = S_(k, SX, 0.0); F, M = M_about(FBt, k, Ss)
        putb(out, 'P13 saddle ring epoxy bond on spar (D12 x 60)', 'EST BOND 2.0 MPa', 
            bond_rf(F[:, 1], M[:, 1], np.hypot(M[:, 0], M[:, 2]), np.hypot(F[:, 0], F[:, 2]), SOD, SAD_L))
        # P14 spar wall under the saddle: bending + torsion (foot loads only, wing loads not added) and ring crush (diametral, hoop allowable EST)
        Sx = M_about(FBt, k, (SX, (1 if k == 0 else -1)*YF-0.0, 0.0))
        out.setdefault('P14a spar 12x10 bending + torsion under the saddle (foot loads only)', ('EST 350 / 30 MPa', []))[1].append(tube_rf(F[:, 1], M[:, 1], np.hypot(M[:, 0], M[:, 2]), A_S, Z_S))
        tw_s = (SOD-SID)/2; Rm = (SOD+SID)/4; P = np.hypot(F[:, 0], F[:, 2])
        crush = 6*0.318*P*Rm/(SAD_L*tw_s**2)*KF
        out.setdefault('P14b spar wall diametral crush under the saddle ring (hoop EST 40 MPa)', ('EST 40 MPa', []))[1].append(SPAR_HOOP/np.maximum(crush, 1e-9))
    return {k: (v[0], np.minimum.reduce(v[1])) for k, v in out.items()}


# ======================================================================= T-069 P1: wing torsion (P15), wing in-plane bending (P16), pin and cup rows
# Section: S5010 (common.COORDS, WING_DZ-shifted, chord C 0.245), spar 12x10 CF at x 0.060 z 0, XPS 25 kg/m3 core (BOM R01 / BUILD-GUIDE l.135).  Tape skin: product and thickness "-" (BUILD-GUIDE l.149) -> skin-less bound.
# Foam stiffness: E 30 MPa, G 8 MPa = structures_a.py l.254 (Ec 30, Gc 8 MPa, EST, for 30 kg/m3 XPS; 25 kg/m3 is softer: EST, sensitivity x0.5 / x2 given).
# Foam strengths: comp 103 kPa (Owens Corning FOAMULAR 150 data sheet, 15 psi min ASTM D1621, read 2026-11-19 via search result), tension 129 kPa and shear 86 kPa EST (foam_103.py l.2-5).
# Spar: G 3.0e9 (fe_a.py l.11 C2 low-corner tube G), E 70e9 (iter2_margins.py l.13 / structures_a.py l.103), allowables SIG 350 / TAU 30 MPa EST, KF.  Foam KP (as foam_103.py).
E_F, G_F = 30e6, 8e6; E_S, G_S = 70e9, 3e9
F_COMP, F_TENS, F_SHEAR = 103e3, 129e3, 86e3
R_BORE = 0.006
def _poly():
    return np.array([(x_*C.C, z_*C.C) for x_, z_ in C.COORDS], float)
def _inside(P, X, Z):
    ins = np.zeros(X.shape, bool); n = len(P)
    for i in range(n):
        x1, y1 = P[i]; x2, y2 = P[(i+1) % n]
        if y1 == y2: continue
        c = ((y1 > Z) != (y2 > Z)) & (X < (x2-x1)*(Z-y1)/(y2-y1)+x1); ins ^= c
    return ins
def section_props(h=0.4e-3, xmax=None):
    """foam section area, centroid x, Iz about its centroid (in-plane), x extent; Prandtl torsion constant J on a 0.4 mm grid: 'solid' (no bore: upper bound) and 'bored' (bore disc = phi 0 boundary: lower bound)."""
    import scipy.sparse as sp, scipy.sparse.linalg as sla
    Pl = _poly(); xs = np.arange(0, C.C+h, h); zs = np.arange(Pl[:, 1].min()-h, Pl[:, 1].max()+2*h, h)
    X, Z = np.meshgrid(xs, zs, indexing='ij'); ins = _inside(Pl, X, Z)
    if xmax is not None: ins &= X <= xmax      # T-071: cell ahead of the hinge only
    bore = (X-C.SPAR_X)**2+Z**2 <= R_BORE**2
    out = {}
    for tag, dom in (('solid', ins), ('bored', ins & ~bore)):
        n = int(dom.sum()); idx = -np.ones(dom.shape, int); idx[dom] = np.arange(n)
        rows, cols, vals = [], [], []
        ii, jj = np.nonzero(dom)
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = ii+di, jj+dj; ok = (ni >= 0) & (ni < dom.shape[0]) & (nj >= 0) & (nj < dom.shape[1])
            ok[ok] = dom[ni[ok], nj[ok]]
            rows += list(idx[ii[ok], jj[ok]]); cols += list(idx[ni[ok], nj[ok]]); vals += [-1.0/h**2]*int(ok.sum())
        rows += list(range(n)); cols += list(range(n)); vals += [4.0/h**2]*n
        A = sp.csr_matrix((vals, (rows, cols)), shape=(n, n)); phi = np.zeros(dom.shape); phi[dom] = sla.spsolve(A.tocsc(), 2*np.ones(n))
        J = 2*phi.sum()*h*h; gx, gz = np.gradient(phi, h); g = np.hypot(gx, gz)
        out[tag] = dict(J=float(J), gmax=float(np.percentile(g[dom], 99.5)), area=float(n*h*h))     # 99.5 percentile of |grad phi|: avoids the staircase-boundary spike
    dom = ins & ~bore; A = dom.sum()*h*h; xc = X[dom].sum()*h*h/A
    out['foam'] = dict(A=float(A), xc=float(xc), Iz=float((((X[dom]-xc)**2).sum())*h*h), x0=0.0, x1=(C.C if xmax is None else xmax), enclosed=float(ins.sum()*h*h))
    return out
_SEC = None
def sec():
    global _SEC
    if _SEC is None: _SEC = section_props()
    return _SEC
def wing_stations():
    return (('y 0.38 (fin station)', YF), ('y 0.228 (motor station)', 0.228), ('y 0.060 (outboard of tray slot end 0.057)', 0.060))

def wing_checks(FBt, EF=E_F, GF=G_F, variant='bored', skin=None):
    """P15 torsion + P16 in-plane bending of the wing at three stations, for one fin's two feet (outboard free body; hub, pack and motor masses are inboard of every station;
    wing-foam inertia ignored, ~0.08 kg x short arm, EST).  Reference line x0 = spar axis or mid-chord (worse taken).  Torsion: spar and foam share by GJ; bending: by EI."""
    if skin is not None: return wing_checks_skin(FBt, skin, EF=EF, GF=GF, variant=variant)
    S = sec(); J_s = 2*I_S; res = {}
    GJf = GF*S[variant]['J']; GJs = G_S*J_s; sh_s = GJs/(GJs+GJf); sh_f = 1-sh_s
    tau_f_unit = S[variant]['gmax']/S[variant]['J']
    fo = S['foam']; EAs, EAf = E_S*A_S, EF*fo['A']; xn = (EAs*SX+EAf*fo['xc'])/(EAs+EAf)
    EIs = E_S*I_S+EAs*(SX-xn)**2; EIf = EF*fo['Iz']+EAf*(fo['xc']-xn)**2; EI = EIs+EIf
    for lab, ys in wing_stations():
        rt, rb = [], []
        for k in (0, 1):
            for x0 in (SX, 0.5*C.C):
                F, M = M_about(FBt, k, S_(k, x0, 0.0)); T = np.abs(M[:, 1])
                ts = KF*sh_s*T*(SOD/2)/J_s; tf = KP*sh_f*T*tau_f_unit
                rt.append(np.minimum(TAU/np.maximum(ts, 1e-9), F_SHEAR/np.maximum(tf, 1e-9)))
                Fs, Ms = M_about(FBt, k, (x0, (1 if k == 0 else -1)*ys, 0.0)); Mz = np.abs(Ms[:, 2])
                kap = Mz/EI; sg_s = KF*E_S*kap*(abs(SX-xn)+SOD/2); d_f = max(xn-fo['x0'], fo['x1']-xn); sg_f = KP*EF*kap*d_f
                rb.append(np.minimum(SIG/np.maximum(sg_s, 1e-9), F_COMP/np.maximum(sg_f, 1e-9)))
        res['P15 wing torsion, spar + foam by GJ share, skin-less, %s' % lab] = ('EST spar 30 MPa / foam 86 kPa', np.minimum.reduce(rt))
        res['P16 wing in-plane bending, spar + foam by EI share, skin-less, %s' % lab] = ('EST spar 350 MPa / foam 103 kPa', np.minimum.reduce(rb))
    info = dict(sh_spar=sh_s, sh_foam=sh_f, GJs=GJs, GJf=GJf, J_s=J_s, J_f=S[variant]['J'], tau_unit=tau_f_unit, xn=xn, EIs=EIs, EIf=EIf, Jsolid=S['solid']['J'], Jbored=S['bored']['J'], foam=fo)
    return res, info

# ======================================================================= T-071 Phase 1 step 1: wing GLASS TORSION SKIN option (D-216 / T-070 s3, s7)
# wing_checks(..., skin=dict) -> wing_checks_skin: torsion cell = skin + foam ahead of the hinge (x <= XH) + spar; the skin-less path above is unchanged (skin=None).
# Laminate allowables: ACP Composites, "Mechanical Properties of Carbon Fiber Composite Materials, Fiber / Epoxy resin (120 C cure)", PDS Dec 2014,
#   https://acpcomposites.com/wp-content/uploads/2024/05/Mechanical-Properties-of-Carbon-Fiber-Composite-Materials.pdf, text extracted and read 2026-11-19.  E-glass FABRIC, Vf 50 %, dry, room temperature,
#   NOT a wet lay-up datasheet: 0/90 loading: E 25 GPa, G12 4 GPa, nu 0.2, Xt 440 / Xc 425 MPa, S 40 MPa;  fibres at +-45 to the loading axis: E 12.3 GPa, G12 11 GPa, Xt = Xc 90 MPa, S 100 MPa.
#   Our wet ply (48 g/m2 cloth + 40 g/m2 resin, EST from T-070) has Vf = (48/2540)/(48/2540 + 40/1150) = 0.35, so every ACP value is scaled by Vf/0.50 = 0.70 (EST, linear scaling; no wet lay-up coupon exists).
# Wrinkling: sigma_cr = c (E_f E_c G_c)^(1/3), c = 0.5 (Hoff and Mautner's empirical value; theory 0.91).  Source: web search 2026-11-19 (Cambridge Aeronautical Journal "Theory of wrinkling in sandwich construction",
#   MDPI Materials 14(17) 5043); neither result printed the formula in one line, so it stays EST (re-read Allen or Zenkert before relying on it).
ACP_SRC = 'ACP Composites PDS Dec 2014, read 2026-11-19'
ACP = dict(vf=0.50, pm45=dict(Ex=12.3e9, G=11e9, X=90e6, S=100e6, E1=25e9), c090=dict(Ex=25e9, G=4e9, X=425e6, S=40e6, E1=25e9))
RHO_GLASS, RHO_EPOXY = 2540.0, 1150.0      # EST (E-glass 2.54-2.60 g/cm3, laminating epoxy 1.1-1.2 g/cm3)
XH = C.C*(1-C.ELEV_FRAC)                   # hinge station, 0.18375 m (common.py)
Y_CLAMP = 0.285                            # strut end on the spar (wing.py STRUT_E)
FIN_M = 0.083                              # fin mass 83 g (T-070 V7, T-067 basis); Iyy from cad_mass.json (relief = I_fin / Iyy)
def skin_laminate(n=1, orient='pm45', awt=0.048, rwt=0.040, stiff=1.0):
    t1 = awt/RHO_GLASS+rwt/RHO_EPOXY; vf = (awt/RHO_GLASS)/t1; k = vf/ACP['vf']; a = ACP[orient]
    return dict(n=n, orient=orient, t=n*t1, vf=vf, k=k, Ex=a['Ex']*k*stiff, G=a['G']*k*stiff, X=a['X']*k, S=a['S']*k, E1=a['E1']*k, mass_m2=n*(awt+rwt), stiff=stiff)
def _cell_geom():
    """perimeter integrals of the closed cell ahead of the hinge (airfoil skin LE -> x = XH on both surfaces + the vertical cove face): S0 = perimeter, S1 = int x ds, S2 = int x2 ds, cove height."""
    Pl = _poly(); S0 = S1 = S2 = 0.0; zs = []
    for i in range(len(Pl)):
        a, b = Pl[i], Pl[(i+1) % len(Pl)]; n = max(int(np.hypot(*(b-a))/0.05e-3), 1)
        u = (np.arange(n)+0.5)/n; xm = a[0]+(b[0]-a[0])*u; ds = np.hypot(*(b-a))/n
        m = xm <= XH; S0 += ds*m.sum(); S1 += ds*xm[m].sum(); S2 += ds*(xm[m]**2).sum()
        if (a[0]-XH)*(b[0]-XH) < 0: zs.append(a[1]+(b[1]-a[1])*(XH-a[0])/(b[0]-a[0]))
    hc = max(zs)-min(zs); return dict(S0=S0+hc, S1=S1+XH*hc, S2=S2+XH*XH*hc, cove_h=hc)
_SECC = {}
def sec_cell():
    if 'v' not in _SECC: _SECC['v'] = section_props(xmax=XH); _SECC['g'] = _cell_geom()
    return _SECC['v'], _SECC['g']
def set_pad(x, z):
    """T-068 D2 pad geometry for the force-point arms (feet_pos): x_foot, z of the pad centre."""
    global XF, ZF; XF, ZF = x, z
PAD_D2 = dict(x_foot=0.3415, z_foot=0.189)     # T-068 s4: X_GROUND 0.3375 -> ~0.3415; pad edge z >= 0.195 -> centre 0.189 (pad dz 0.012, electrical.py)

def _strut_geom():
    d = (W.STRUT_E[0]-W.STRUT_S[0], W.STRUT_E[1]-W.STRUT_S[1]); Ls = math.hypot(*d); return d[0]/Ls, d[1]/Ls, Ls
def wing_checks_skin(FBt, skin, EF=E_F, GF=G_F, variant='bored'):
    """P15 torsion / P16 in-plane bending with the glass skin.  skin keys: lam (skin_laminate), K (skin factor, default KP), relief (fraction of My taken by the loaded fin's inertia, EST),
    strip_A (cove CF strip area m2), E_strip, truss (strut + spar truss inboard of y 0.285, T-070 F-3a).  In-plane moment is taken about the neutral axis of the composite section (axial force acts there)."""
    lam = skin['lam']; Ks = skin.get('K', KP); rel = skin.get('relief', 0.0); Acap = skin.get('strip_A', 0.0); Ecap = skin.get('E_strip', 120e9); truss = skin.get('truss', True)
    S, cg = sec_cell(); fo = S['foam']; J_s = 2*I_S; t = lam['t']; A = fo['enclosed']; per = cg['S0']
    GJs, GJf, GJk = G_S*J_s, GF*S[variant]['J'], 4*A*A*lam['G']*t/per; GJ = GJs+GJf+GJk; sh_s, sh_f, sh_k = GJs/GJ, GJf/GJ, GJk/GJ
    tau_u = S[variant]['gmax']/S[variant]['J']
    EAs, EAf, EAk, EAc = E_S*A_S, EF*fo['A'], lam['Ex']*t*cg['S0'], Ecap*Acap; xk = cg['S1']/cg['S0']
    EA = EAs+EAf+EAk+EAc; xn = (EAs*SX+EAf*fo['xc']+EAk*xk+EAc*XH)/EA
    EI = E_S*I_S+EAs*(SX-xn)**2+EF*fo['Iz']+EAf*(fo['xc']-xn)**2+lam['Ex']*t*(cg['S2']-2*xn*cg['S1']+xn*xn*cg['S0'])+EAc*(XH-xn)**2
    d_sp = abs(SX-xn)+SOD/2; d_f = max(xn, XH-xn); d_sk = max(xn, XH-xn); d_c = abs(XH-xn)
    wr1 = 0.5*(lam['E1']*EF*GF)**(1/3); wr2 = 0.5*(lam['Ex']*EF*GF)**(1/3)
    ux, uy, Ls = _strut_geom(); res = {}
    stations = (('y 0.35', 0.35, False), ('y 0.285 (clamp node, outboard side, no truss)', Y_CLAMP, False), ('y 0.228', 0.228, True), ('y 0.060', 0.060, True), ('y 0.040', 0.040, True))
    for lab, ys, tr in stations:
        acc = {}
        for k in (0, 1):
            sg = 1 if k == 0 else -1
            T = np.abs(M_about(FBt, k, S_(k, SX, 0.0))[1][:, 1])
            T = np.maximum(T, np.abs(M_about(FBt, k, S_(k, 0.5*C.C, 0.0))[1][:, 1]))*(1-rel)        # worse of the two reference lines (as T-069)
            q = sh_k*T/(2*A); tk = Ks*q/t
            Fs, Ms = M_about(FBt, k, (xn, sg*ys, 0.0)); Mz = Ms[:, 2]; Fx, Fy = Fs[:, 0], Fs[:, 1]; Sax = -Fy
            if truss and tr:
                N = Fx/ux; xs = W.STRUT_S[0]+(ys-W.STRUT_S[1])*ux/uy; Lv = xn-xs
                Mc = -(Mz+Lv*N*sg*uy); Sax = N*sg*uy-Fy
            else: Mc = -Mz
            kap = np.abs(Mc)/EI; eps0 = np.abs(Sax)/EA
            sgk = Ks*lam['Ex']*(kap*d_sk+eps0)
            rows = {
             'P15 spar torsion': TAU/np.maximum(KF*sh_s*T*(SOD/2)/J_s, 1e-9),
             'P15 foam shear (cell)': F_SHEAR/np.maximum(KP*sh_f*T*tau_u, 1e-9),
             'P15 skin shear': lam['S']/np.maximum(tk, 1e-9),
             'P15 skin shear+axial interaction': 1/np.maximum(np.sqrt((sgk/lam['X'])**2+(tk/lam['S'])**2), 1e-9),
             'P15 skin wrinkling, torsion only (E_f fibre)': wr1/np.maximum(tk, 1e-9),
             'P15 skin wrinkling, torsion + bending (E_f = E_x)': wr2/np.maximum(sgk/2+np.sqrt((sgk/2)**2+tk**2), 1e-9),
             'P16 spar bending + axial': SIG/np.maximum(KF*E_S*(kap*d_sp+eps0), 1e-9),
             'P16 foam bending + axial': F_COMP/np.maximum(KP*EF*(kap*d_f+eps0), 1e-9)}
            if Acap > 0: rows['P16 cove CF strip'] = SIG/np.maximum(KF*Ecap*(kap*d_c+eps0), 1e-9)
            for nm, v in rows.items(): acc[nm] = np.minimum(acc[nm], v) if nm in acc else v
        for nm, v in acc.items(): res['%s, %s' % (nm, lab)] = ('see ACP_SRC / EST', v)
    info = dict(sh_spar=sh_s, sh_foam=sh_f, sh_skin=sh_k, GJs=GJs, GJf=GJf, GJk=GJk, GJ=GJ, A_cell=A, per=per, cove_h=cg['cove_h'], t=t, vf=lam['vf'], xn=xn, EI=EI, d_sk=d_sk,
                wr1=wr1, wr2=wr2, J_foam=S[variant]['J'], tau_unit=tau_u, foamA=fo['A'], Ex=lam['Ex'], G=lam['G'], S=lam['S'], X=lam['X'])
    return res, info

def strut_checks(FBt, Lb_clamp=None, Lb_hub=0.030, EF=E_F):
    """T-070 F-3a: strut axial force N = Fx_fin / ux (strut takes the chordwise shear inboard of the clamp, tension +).  Euler pinned-pinned without foam support (the groove is open below and 0.5 mm clear: not credited),
    an upper bound with the foam bedding it (Winkler k = E_foam D / 5 mm, EST, not credited), strut strength, bond at the clamp (length from wing.py: strut enters the clamp box face y 0.272) and at the hub socket (30 mm, HUB_STRUT_S)."""
    ux, uy, Ls = _strut_geom(); D, d = W.STRUT_OD, W.STRUT_ID; A_st = math.pi/4*(D*D-d*d); I_st = math.pi/64*(D**4-d**4); EIst = E_S*I_st
    if Lb_clamp is None: Lb_clamp = (W.STRUT_E[1]-0.272)/uy
    Pe = math.pi**2*EIst/Ls**2; kf = EF*D/0.005; Pf = min(2*math.sqrt(kf*EIst), SIG*A_st); out = {}
    for k in (0, 1):
        N = np.sum([FBt[:, 2*k+j, 0] for j in (0, 1)], axis=0)/ux; Nc = np.maximum(-N, 0.0); Na = np.abs(N)
        for nm, v in (('STRUT Euler pinned, no foam support (%.0f N)' % Pe, Pe/np.maximum(KF*Nc, 1e-9)),
                      ('STRUT Euler bound with foam bedding, not credited (%.0f N)' % Pf, Pf/np.maximum(KF*Nc, 1e-9)),
                      ('STRUT tube strength, 6x4.5 CF 350 MPa EST', SIG*A_st/np.maximum(KF*Na, 1e-9)),
                      ('STRUT bond at clamp (D6 x %.1f mm, epoxy 2.0 MPa EST)' % (Lb_clamp*1e3), BOND/np.maximum(KP*Na/(math.pi*D*Lb_clamp), 1e-9)),
                      ('STRUT bond at hub socket (D6 x %.0f mm)' % (Lb_hub*1e3), BOND/np.maximum(KP*Na/(math.pi*D*Lb_hub), 1e-9))):
            out[nm] = ('EST', np.minimum(out[nm][1], v) if nm in out else v)
    return out

# --- pin and cup rows (D-215 D3 / D4 geometry as PROPOSED, not built): 3 mm CF cross-pin (BOM R14); cup 4 mm deep, 1.5 mm walls on the shoe plate
PIN_D = 0.003; PIN_A = math.pi/4*PIN_D**2; PIN_TAU = 30e6      # EST: CF rod shear (structures_a.py TAU 30 MPa; Tap Plastics 41.3 MPa is a sensitivity, landing_side_a.py l.66)
CUP_D, CUP_T, CUP_L = 0.004, 0.0015, 0.030                    # cup depth, wall, free foam length (D-215 s0 / s6)
EVA_BEAR = 0.17e6                                             # EST: crush plateau of the foot design (30 N / 180 mm2) used as the foam bearing limit; EVA data "-"
def pin_cup_checks(FBt):
    out = {}
    for k in (0, 1):
        for nm, x in (('root block', BLK_X0), ('saddle', SAD_X1)):
            F, M = M_about(FBt, k, S_(k, x, 0.0)); V = np.abs(M[:, 0])/ROD                # force per shear plane, couple arm = rib OD
            out.setdefault('PIN %s: 1 x 3 mm CF cross-pin shear (double shear, rib torsion)' % nm, ('EST CF rod 30 MPa', []))[1].append(PIN_TAU/np.maximum(V/(2*PIN_A)*KP, 1e-9))
            out.setdefault('PIN %s: bearing in PETG socket wall (3 mm x 2.5 mm)' % nm, ('EST PETG_BEAR 20 MPa', []))[1].append(PETG_BEAR/np.maximum(V/(PIN_D*0.0025)*KP, 1e-9))
        for j in (0, 1):
            f = FBt[:, 2*k+j, :]; Fs = n_(f[:, 1:]); R_rim = Fs*(CUP_L+CUP_D)/CUP_D
            out.setdefault('CUP wall bending (printed, in-layer 20 MPa EST; 4 mm cantilever, 15 x 1.5 mm)', ('EST 20 MPa', []))[1].append(20e6/np.maximum(R_rim*CUP_D*0.5/(0.015*CUP_T**2/6)*KP, 1e-9))
            out.setdefault('CUP EVA bearing at rim (15 x 2 mm contact) vs crush plateau', ('EST 0.17 MPa', []))[1].append(EVA_BEAR/np.maximum(R_rim/(0.015*0.002)*KP, 1e-9))
            out.setdefault('CUP pin shear (1 x 3 mm CF, double shear)', ('EST CF rod 30 MPa', []))[1].append(PIN_TAU/np.maximum(Fs/(2*PIN_A)*KP, 1e-9))
            out.setdefault('CUP EVA bearing at pin hole (3 x 12 mm) vs crush plateau', ('EST 0.17 MPa', []))[1].append(EVA_BEAR/np.maximum(Fs/(PIN_D*0.012)*KP, 1e-9))
    return {k: (v[0], np.minimum.reduce(v[1])) for k, v in out.items()}


def cases(quick=False):
    s = math.pi/2
    c = [("hard level", dict(v_sink=1.2)), ("hard 10 narrow", dict(v_sink=1.2, th_n=10)), ("hard 10 narrow neg", dict(v_sink=1.2, th_n=-10)),
         ("hard 10 wide", dict(v_sink=1.2, th_w=10)), ("hard 7/7 combo", dict(v_sink=1.2, th_n=7, th_w=7)),
         ("hard 10 narrow + drift .5", dict(v_sink=1.2, th_n=10, drift=0.5, drift_dir=0.0)), ("hard 10 wide + drift .5 y", dict(v_sink=1.2, th_w=10, drift=0.5, drift_dir=s)),
         ("normal level .5", dict(v_sink=0.5)), ("normal 10 narrow .5", dict(v_sink=0.5, th_n=10)), ("normal 10 wide .5 + drift", dict(v_sink=0.5, th_w=10, drift=0.5, drift_dir=s))]
    if not quick:
        for n_, lean, lat, sink in (("Tb_h5", 16.5, 0.09, 0.31), ("Ta_h5", 18.8, 0.11, 0.30), ("Z5_b45", 17.2, 0.21, 0.32), ("Lb_5e", 12.1, 0.45, 0.32), ("Z5_gb45", 11.0, 0.50, 0.32)):
            c.append((f"SITL {n_} wide (y drift)", dict(v_sink=sink, th_w=lean, drift=lat, drift_dir=s)))
            c.append((f"SITL {n_} narrow (z drift)", dict(v_sink=sink, th_n=lean, drift=lat, drift_dir=0.0)))
        c.append(("hard 16 wide + drift .5 y", dict(v_sink=1.2, th_w=16, drift=0.5, drift_dir=s)))
    return c


def volumes():
    """F10: volume of FIN-005 / FIN-003 / GER-001 / GER-002 from the stub-built CAD shapes (voxel union minus cuts, 0.25 mm), solid PETG at RHO_PETG, listed mass."""
    import build_a as b
    class MPath:                                   # numpy even-odd ray casting (no matplotlib under python -I)
        def __init__(self, poly): self.p = np.asarray(poly, float)
        def contains_points(self, pts):
            x, y = pts[:, 0], pts[:, 1]; ins = np.zeros(len(pts), bool); P = self.p; n = len(P)
            for i in range(n):
                x1, y1 = P[i]; x2, y2 = P[(i+1) % n]
                if y1 == y2: continue
                c = ((y1 > y) != (y2 > y)) & (x < (x2-x1)*(y-y1)/(y2-y1)+x1); ins ^= c
            return ins
    ctx, _, res = b.build_all.build(b.StubBackend(), b.MODEL, os.path.join(b.MODEL, 'modules.txt'), log=lambda *a: None)
    res_ = {}
    def inside(shape, X, Y, Z):
        P = np.stack([X, Y, Z], 1)
        if shape.kind == 'revolve':
            k = {'X': 0, 'Y': 1, 'Z': 2}[shape.axis]; i, j = [q for q in range(3) if q != k]; c = shape.center
            a = P[:, k]-c[k]; rho = np.hypot(P[:, i]-c[i], P[:, j]-c[j])
            return MPath(np.array(shape.profile)).contains_points(np.stack([a, rho], 1))
        if shape.kind == 'prism':
            k = {'X': 0, 'Y': 1, 'Z': 2}[shape.axis]; uv = {'X': (1, 2), 'Y': (0, 2), 'Z': (0, 1)}[shape.axis]
            lo, hi = sorted((shape.offset, shape.offset+shape.depth)); m = (P[:, k] >= lo) & (P[:, k] <= hi)
            ins = np.zeros(len(P), bool)
            for lp in shape.loops: ins ^= MPath(np.array(lp)).contains_points(P[:, list(uv)])
            return m & ins
        raise ValueError(shape.kind)
    for pid in ('FIN-005-R', 'FIN-003-R', 'GER-001-UR', 'GER-002-UR'):
        c = ctx.components[pid]; assert c.at == (0.0, 0.0, 0.0) and not c.rotate
        bb = c.bbox(); h = 0.25e-3
        xs = [np.arange(bb[0][i]-h, bb[1][i]+2*h, h)+h/2 for i in range(3)]
        X, Y, Z = [a.ravel() for a in np.meshgrid(*xs, indexing='ij')]
        ins = np.zeros(len(X), bool)
        for s in c.shapes: ins |= inside(s, X, Y, Z)
        for s, m, nm, shop in c.cuts: ins &= ~inside(s, X, Y, Z)
        V = ins.sum()*h**3
        res_[pid] = (V*1e6, V*1e6*W.RHO_PETG, c.mass_g, sum(sh.volume_centroid()[0] for sh in c.shapes)*1e6)
    return res_


def skin_variants():
    l1 = skin_laminate(); base = dict(lam=l1, strip_A=3e-6, relief=0.0, truss=True)
    return [('V0 GATE: 1 ply 48 g/m2 +-45, strip 3 mm2, no relief, truss, K=KP', base, 1.0),
            ('V1 + fin inertia relief 20 % (EST)', dict(base, relief=0.20), 1.0),
            ('V2 truss credit OFF', dict(base, truss=False), 1.0),
            ('V3 skin E,G x0.7 (stiffness robustness)', dict(base, lam=skin_laminate(stiff=0.7)), 1.0),
            ('V4 foam E,G x0.5', base, 0.5),
            ('V5 no cap strip', dict(base, strip_A=0.0), 1.0),
            ('V6 skin factor KF instead of KP', dict(base, K=KF), 1.0),
            ('V7 2 plies +-45', dict(base, lam=skin_laminate(n=2)), 1.0),
            ('V8 1 ply 0/90 (comparison)', dict(base, lam=skin_laminate(orient='c090')), 1.0)]
def skin_main():
    """T-071: all 23 landing cases with the D-215 / T-068 D2 pad geometry; skin variants; strut rows; strip scan."""
    t0 = time.time(); set_pad(PAD_D2["x_foot"], PAD_D2["z_foot"]); FBs = []
    print(f"# T-071 skin run: pad x {XF:.4f} z {ZF:.4f} (T-068 D2), CG {L.geom()['cg']}, mass {L.M_GATE} kg, KF {KF:.3f} KP {KP:.3f}; laminate source {ACP_SRC}")
    for name, kw in cases(False):
        q = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, **dict(kw, **PAD_D2)); FBs.append((name, q['trace'].reshape(-1, 4, 3)))
        print(f"  case {name:34s} side {q['side'].max():5.1f} N Fmax {q['F'].max():5.1f} N [{time.time()-t0:.0f} s]", flush=True)
    Sc, cg = sec_cell(); print("\n## cell ahead of the hinge:", {k: (round(float(v), 6)) for k, v in cg.items()}, 'enclosed A', Sc['foam']['enclosed'], 'foam A', Sc['foam']['A'], 'J bored/solid', Sc['bored']['J'], Sc['solid']['J'])
    ish = FBs[0][1]; res_, inf = wing_checks_skin(ish, skin_variants()[0][1]); print('## V0 info:', {k: (round(float(v), 6) if not isinstance(v, dict) else '') for k, v in inf.items()})
    allr = {}
    for vn, sk, fs in skin_variants():
        for name, FBt in FBs:
            r, _ = wing_checks_skin(FBt, sk, EF=E_F*fs, GF=G_F*fs)
            if vn.startswith('V0'): r.update(strut_checks(FBt))
            for key, (lab, a) in r.items():
                cur = allr.setdefault((vn, key), (1e9, ''))
                if float(a.min()) < cur[0]: allr[(vn, key)] = (float(a.min()), name)
    for name, FBt in FBs:      # skin-less with the D2 pad, for the effect of the pad geometry
        r, _ = wing_checks(FBt)
        for key, (lab, a) in r.items():
            cur = allr.setdefault(('SKIN-LESS (D2 pad)', key), (1e9, ''))
            if float(a.min()) < cur[0]: allr[('SKIN-LESS (D2 pad)', key)] = (float(a.min()), name)
    print("\n## Minimum RF over 23 cases per variant (rows listed: the minimum per row family over stations)")
    for vn in dict.fromkeys(k[0] for k in allr):
        print(f"\n### {vn}")
        fam = {}
        for (v, key), (rf, nm) in allr.items():
            if v != vn: continue
            f = key.split(',')[0] if v.startswith('V') and not key.startswith('STRUT') else key
            if f not in fam or rf < fam[f][0]: fam[f] = (rf, key, nm)
        for f, (rf, key, nm) in sorted(fam.items(), key=lambda kv: kv[1][0]): print(f"| {f} | {rf:.2f} | {key} | {nm} |")
        if vn.startswith('V') or vn.startswith('SKIN'):
            p15 = min(v[0] for (a, k), v in allr.items() if a == vn and k.startswith('P15')); p16 = min(v[0] for (a, k), v in allr.items() if a == vn and k.startswith('P16'))
            print(f"MIN P15 {p15:.2f}   MIN P16 {p16:.2f}")
    print("\n## all V0 rows by station")
    for (v, key), (rf, nm) in sorted(allr.items(), key=lambda kv: kv[1][0]):
        if v.startswith('V0'): print(f"| {key} | {rf:.2f} | {nm} |")
    print("\n## cap strip scan (V0 otherwise): min P16 / min P15 vs strip area")
    for Acap in (0, 1e-6, 2e-6, 3e-6, 4e-6, 6e-6, 8e-6, 12e-6, 16e-6, 24e-6):
        m16 = m15 = 1e9
        for name, FBt in FBs:
            r, _ = wing_checks_skin(FBt, dict(skin_variants()[0][1], strip_A=Acap))
            for key, (lab, a) in r.items():
                if key.startswith('P16'): m16 = min(m16, float(a.min()))
                if key.startswith('P15'): m15 = min(m15, float(a.min()))
        print(f"strip {Acap*1e6:5.1f} mm2: mass {Acap*0.80*1550*1e3:5.2f} g (0.80 m, 1.55 g/cm3 EST)  min P16 {m16:.2f}  min P15 {m15:.2f}")
    print("\n## ply scan (V0 otherwise, strip 3 mm2)")
    for n in (1, 2, 3):
        m16 = m15 = 1e9
        for name, FBt in FBs:
            r, _ = wing_checks_skin(FBt, dict(skin_variants()[0][1], lam=skin_laminate(n=n)))
            for key, (lab, a) in r.items():
                if key.startswith('P16'): m16 = min(m16, float(a.min()))
                if key.startswith('P15'): m15 = min(m15, float(a.min()))
        print(f"{n} ply: t {n*skin_laminate()['t']*1e3:.3f} mm  skin mass {n*0.088*cg['S0']*0.80*1e3:.1f} g (perimeter {cg['S0']*1e3:.0f} mm x 0.80 m)  min P16 {m16:.2f}  min P15 {m15:.2f}")
    print(f"\nwall time {time.time()-t0:.0f} s")

if __name__ == "__main__":
    if "--skin" in sys.argv: skin_main(); sys.exit(0)
    quick = "--quick" in sys.argv
    print(f"# landing_path_a.py, geometry {'legacy' if L.LEGACY else 'CAD'}: x_ground {XF:.4f} y {YF:.3f} z pad centre {ZF:.4f} m, CG {L.geom()['cg']}, mass {L.M_GATE} kg, plateau 30 N, mu {L.MU}")
    print(f"# KF {KF:.3f} KP {KP:.3f}; sections: fin tube {FOD*1e3:.0f}x{FID*1e3:.0f} Z {Z_F*1e9:.0f} mm3; rib {ROD*1e3:.0f}x{RID*1e3:.0f} Z {Z_R*1e9:.0f} mm3; spar {SOD*1e3:.0f}x{SID*1e3:.0f} Z {Z_S*1e9:.0f} mm3")
    allrf = {}; t0 = time.time()
    for name, kw in cases(quick):
        q = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, **kw)
        FBt = q['trace'].reshape(-1, 4, 3)
        rf = checks(FBt); rf.update(pin_cup_checks(FBt)); wrf, WINFO = wing_checks(FBt); rf.update(wrf)
        for key, (lab, a) in rf.items(): allrf.setdefault(key, []).append((float(a.min()), name, lab))
        print(f"  case {name:34s} side {q['side'].max():5.1f} N Fmax {q['F'].max():5.1f} N  rib RF (landing_a) {q['rib_rf']:.2f}  tilt_end {q['tilt_end']:.1f}  min path RF {min(float(v.min()) for _, (l, v) in rf.items()):.2f}  [{time.time()-t0:.0f} s]", flush=True)
    print("\n## Wing section / share data (T-069):", {k: (round(v, 6) if isinstance(v, float) else v) for k, v in WINFO.items()})
    print("\n## Minimum RF per check over all cases (criterion RF >= 1.0)")
    print("| Check | Allowable | min RF | governing case | demand stress = allowable / RF |\n|---|---|---|---|---|")
    rows = []
    for key, v in allrf.items():
        m = min(v); rows.append((m[0], key, m[2], m[1]))
    import re as _re
    def _dem(lab, rf):
        m = _re.search(r"([0-9.]+) MPa", lab)
        return f"{float(m.group(1))/rf:.1f} MPa" if m and rf > 0 else "-"
    for rf, key, lab, nm in sorted(rows): print(f"| {key} | {lab} | {rf:.2f} | {nm} | {_dem(lab, rf)} |")
    print(f"\nMINIMUM over all rows: {min(rows)[1]} RF {min(rows)[0]:.2f} ({min(rows)[3]})")
    firm = [r for r in rows if "BOND INTEGRITY" not in r[1] and "P1 " not in r[1]]
    print(f"MINIMUM excluding the peel rows and the PSA rows (allowable with no repo source): {min(firm)[1]} RF {min(firm)[0]:.2f} ({min(firm)[3]})")
    print("Rows below 1.0:", "; ".join(f"{r[1]} {r[0]:.2f}" for r in sorted(rows) if r[0] < 1.0))
    print("\n## F10 volumes (voxel 0.25 mm of the stub-built CAD shapes, minus cuts; solid PETG at RHO_PETG %.2f g/cm3)" % W.RHO_PETG)
    for pid, (v, mg, ml, vs) in volumes().items():
        print(f"{pid}: voxel volume {v:.2f} cm3 -> solid {mg:.2f} g; listed {ml} g; sum of shape volumes before cuts {vs:.2f} cm3 -> {vs*W.RHO_PETG:.2f} g; listed / solid {ml/mg:.2f}")
