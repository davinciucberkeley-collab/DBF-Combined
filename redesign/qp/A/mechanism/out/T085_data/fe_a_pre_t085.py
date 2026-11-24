"""Concept A structure: 3-D beam frame FE (free-free modes) vs rotor orders.  Reproduce: python -I fe_a.py
Method scaled from team/C4 (beam/FE vs 1P/2P at hover and cruise rpm, 20 % separation, knock-down properties) and team/C2
(wing modes).  Euler-Bernoulli beams, 6 dof/node, lumped masses; stdlib + numpy + scipy.  All inputs labelled; EST = estimate.
Axes: x aft of the wing LE, y right, z cruise-up.  Hover = nose up (x down).  Frame is free-free (the aircraft in flight)."""
import math, sys
import numpy as np
from scipy.linalg import eigh

# ---------------- material (nominal, knock-down) -----------------------------------------------------------------
E_CF = {"hi": 90e9, "nom": 70e9, "kd": 61e9}      # CF tube axial E.  70 = C2 low-corner tube value (ASM-C2); kd = 0.87 (C4 GT-16 shell pass line) EST
G_CF = {"hi": 4.5e9, "nom": 3e9, "kd": 3e9}        # C2 low-corner tube G (3 GPa)
E_PETG = {"hi": 2.4e9, "nom": 2.1e9, "kd": 1.6e9}  # printed PETG, XY; kd = layer/thin-wall knock-down EST (C4 used ASA 1.8 GPa low)
G_PETG = {"hi": 0.89e9, "nom": 0.78e9, "kd": 0.58e9}
RHO_CF, RHO_PETG = 1600.0, 1270.0
# ---------------- geometry (CAD numbers proposed here, EST) -------------------------------------------------------
X_SPAR = 0.060                          # main spar x aft of LE (0.245 c)
Y_M, Z_M, X_M = 0.228, 0.156, -0.075    # motor grid (arm x1.2, D-184), prop plane 0.075 m ahead of the LE (SIZING-A: disk 0.085 ahead, hub x -0.075)
X_HUB = X_M
Y_FIN, X_FIN, H_FIN = 0.38, 0.240, 0.180   # fin y, fin mid-chord x (chord 0.12: x 0.18-0.30), half height
TUBE = dict(OD=16e-3, ID=14e-3)
A_T = math.pi/4*(TUBE["OD"]**2-TUBE["ID"]**2); I_T = math.pi/64*(TUBE["OD"]**4-TUBE["ID"]**4)
J_T = 2*I_T


def prop_box(w, h, t):
    """thin rectangular PETG box: returns (area, I about axis along w-dim..., ) -> Iy (bending, load across h), Iz (across w), J"""
    ai, hi = w-2*t, h-2*t
    A = w*h-ai*hi
    Iz = (h*w**3-hi*ai**3)/12      # bending with displacement across w
    Iy = (w*h**3-ai*hi**3)/12      # bending with displacement across h
    Am, s = (w-t)*(h-t), 2*((w-t)+(h-t))
    J = 4*Am**2*t/s
    return A, Iy, Iz, J


class Frame:
    def __init__(self):
        self.n = {}; self.el = []; self.mass = {}
    def node(self, name, xyz): self.n[name] = np.array(xyz, float)
    def beam(self, a, b, EA, EIy, EIz, GJ, rhoA, vref, grp, nseg=4):
        pa, pb = self.n[a], self.n[b]
        names = [a]+[f"{a}>{b}#{i}" for i in range(1, nseg)]+[b]
        for i in range(1, nseg): self.n[names[i]] = pa+(pb-pa)*i/nseg
        for i in range(nseg): self.el.append((names[i], names[i+1], EA, EIy, EIz, GJ, rhoA, np.array(vref, float), grp))
    def lump(self, name, m):
        self.mass[name] = self.mass.get(name, 0.0)+m
    def solve(self, nmodes=14):
        names = list(self.n); idx = {k: i for i, k in enumerate(names)}; N = len(names)
        K = np.zeros((6*N, 6*N)); M = np.zeros((6*N, 6*N)); Kg = {}
        for (a, b, EA, EIy, EIz, GJ, rA, vref, grp) in self.el:
            pa, pb = self.n[a], self.n[b]; L = np.linalg.norm(pb-pa); ex = (pb-pa)/L
            ey = np.cross(vref, ex); ey /= np.linalg.norm(ey); ez = np.cross(ex, ey)
            R = np.array([ex, ey, ez]); T = np.zeros((12, 12))
            for i in range(4): T[3*i:3*i+3, 3*i:3*i+3] = R
            k = np.zeros((12, 12))
            k[0, 0] = k[6, 6] = EA/L; k[0, 6] = k[6, 0] = -EA/L
            k[3, 3] = k[9, 9] = GJ/L; k[3, 9] = k[9, 3] = -GJ/L
            c = EIz/L**3                      # v (local y), theta_z
            for (i, j, v) in ((1, 1, 12), (1, 5, 6*L), (1, 7, -12), (1, 11, 6*L), (5, 5, 4*L*L), (5, 7, -6*L), (5, 11, 2*L*L),
                              (7, 7, 12), (7, 11, -6*L), (11, 11, 4*L*L)):
                k[i, j] = k[j, i] = c*v
            c = EIy/L**3                      # w (local z), theta_y
            for (i, j, v) in ((2, 2, 12), (2, 4, -6*L), (2, 8, -12), (2, 10, -6*L), (4, 4, 4*L*L), (4, 8, 6*L), (4, 10, 2*L*L),
                              (8, 8, 12), (8, 10, 6*L), (10, 10, 4*L*L)):
                k[i, j] = k[j, i] = c*v
            kg = T.T@k@T
            ia, ib = idx[a], idx[b]; dof = list(range(6*ia, 6*ia+6))+list(range(6*ib, 6*ib+6))
            K[np.ix_(dof, dof)] += kg
            me = rA*L
            for nd in (ia, ib):
                for q in range(3): M[6*nd+q, 6*nd+q] += me/2
                for q in range(3, 6): M[6*nd+q, 6*nd+q] += me/2*L*L/50   # small rotary inertia
        for nm, m in self.mass.items():
            i = idx[nm]
            for q in range(3): M[6*i+q, 6*i+q] += m
            for q in range(3, 6): M[6*i+q, 6*i+q] += m*1e-5
        w2, V = eigh(K, M)
        f = np.sqrt(np.abs(w2))/(2*math.pi); keep = [i for i in range(len(f)) if f[i] > 2.0][:nmodes]
        self._names, self._idx, self._K, self._V = names, idx, K, V
        res = []
        for i in keep:
            v = V[:, i]; e = {}
            for (a, b, EA, EIy, EIz, GJ, rA, vref, grp) in self.el:   # strain energy by group (element-wise, local)
                pa, pb = self.n[a], self.n[b]; L = np.linalg.norm(pb-pa)
                ia, ib = idx[a], idx[b]; dof = list(range(6*ia, 6*ia+6))+list(range(6*ib, 6*ib+6))
                ue = v[dof]; ex = (pb-pa)/L; ey = np.cross(vref, ex); ey /= np.linalg.norm(ey); ez = np.cross(ex, ey)
                R = np.array([ex, ey, ez]); T = np.zeros((12, 12))
                for q in range(4): T[3*q:3*q+3, 3*q:3*q+3] = R
                ul = T@ue
                # energy from local stiffness (rebuild cheaply by quadratic form)
                kk = np.zeros((12, 12))
                kk[3, 3] = kk[9, 9] = GJ/L; kk[3, 9] = kk[9, 3] = -GJ/L
                c = EIz/L**3
                for (p, q, vv) in ((1, 1, 12), (1, 5, 6*L), (1, 7, -12), (1, 11, 6*L), (5, 5, 4*L*L), (5, 7, -6*L), (5, 11, 2*L*L), (7, 7, 12), (7, 11, -6*L), (11, 11, 4*L*L)):
                    kk[p, q] = kk[q, p] = c*vv
                c = EIy/L**3
                for (p, q, vv) in ((2, 2, 12), (2, 4, -6*L), (2, 8, -12), (2, 10, -6*L), (4, 4, 4*L*L), (4, 8, 6*L), (4, 10, 2*L*L), (8, 8, 12), (8, 10, 6*L), (10, 10, 4*L*L)):
                    kk[p, q] = kk[q, p] = c*vv
                kk[0, 0] = kk[6, 6] = EA/L; kk[0, 6] = kk[6, 0] = -EA/L
                e[grp] = e.get(grp, 0.0)+0.5*ul@kk@ul
            tot = sum(e.values())
            cy = math.sqrt(sum(v[6*idx[m]+1]**2+v[6*idx[m]+2]**2 for m in names if m.startswith("m+") or m.startswith("m-") and ">" not in m))
            cx = math.sqrt(sum(v[6*idx[m]]**2 for m in names if (m.startswith("m+") or m.startswith("m-")) and ">" not in m))
            res.append((f[i], {g: x/tot for g, x in e.items()}, v, cx, cy))
        return res


def build(kind="nom", y_fin=Y_FIN, rib_wall=0.8e-3, rib_wh=(30e-3, 14e-3), arm_len_scale=1.0, hub_bridge=(24e-3, 30e-3, 1.5e-3),
          foot_pad_m=0.003, wing_g=212.0, pack_g=270.0, motor_g=65.0+11.06+5.0+4.3+2.9, avionics_g=110.0, fin_skin_t=0.1e-3, fin_core=15e-3,
          fin_E_skin=50e9, root_fix=None, verbose=False, arm_tube=(14e-3, 12e-3), bridge_cf=True, bridge_tube=(8e-3, 6e-3), spar_tube=(16e-3, 14e-3), rib_tube=None, bridge_cfg='single', bridge_yv=0.12, vtube=(8e-3, 6e-3), fin_strip=None, arm_E_scale=1.0, fin_tube=None, x_fin=None, root_g=6.0, centre_extra_g=65.0, x_hub=None, hub_extra_g=20.0, wing_cell=None, h_fin=None):
    E = E_CF[kind]; G = G_CF[kind]; Ep = E_PETG[kind]; Gp = G_PETG[kind]
    F = Frame()
    A_a = math.pi/4*(arm_tube[0]**2-arm_tube[1]**2); I_a = math.pi/64*(arm_tube[0]**4-arm_tube[1]**4)
    # --- spar along y at x = X_SPAR
    A_s = math.pi/4*(spar_tube[0]**2-spar_tube[1]**2); I_s = math.pi/64*(spar_tube[0]**4-spar_tube[1]**4)
    rt = rib_tube or arm_tube; A_r = math.pi/4*(rt[0]**2-rt[1]**2); I_r = math.pi/64*(rt[0]**4-rt[1]**4)
    ys = sorted(set([-bridge_yv, bridge_yv, -0.45, -y_fin, -0.30, -Y_M, -0.15, -0.075, 0.0, 0.075, 0.15, Y_M, 0.30, y_fin, 0.45]))
    for y in ys: F.node(f"s{y:+.3f}", (X_SPAR, y, 0.0))
    rho_spar = RHO_CF*A_s
    for a, b in zip(ys, ys[1:]):
        if wing_cell is None:
            F.beam(f"s{a:+.3f}", f"s{b:+.3f}", E*A_s, E*I_s, E*I_s, G*2*I_s, rho_spar, (0, 0, 1), "spar", nseg=3)
        else:   # T-084: wing torsion cell credited (spar + foam + skin + cove strip, structures/../T084_data/t084_cell_props.py); zone by the segment mid |y|; corner factor E/70 GPa on all of it
            ym = abs(0.5*(a+b)); z_ = next(z for z in wing_cell["zones"] if ym <= z[0]); s_ = wing_cell.get("scale", {"hi": 90/70, "nom": 1.0, "kd": 61/70}[kind])
            F.beam(f"s{a:+.3f}", f"s{b:+.3f}", s_*z_[1], s_*z_[2], s_*z_[3], s_*z_[4], rho_spar, (0, 0, 1), "spar", nseg=3)
    # wing (foam, tape, elevons, plugs) mass as lumps on the spar nodes, uniform in y, with 0.25 chord-ish offsets ignored
    wing_extra = wing_g*1e-3-RHO_CF*A_s*0.90
    for a, b in zip(ys, ys[1:]):
        for y in (a, b): F.lump(f"s{y:+.3f}", wing_extra*(b-a)/0.90/2)
    # avionics + servos + misc at centre
    F.lump("s+0.000", avionics_g*1e-3+centre_extra_g*1e-3)   # T-066: centre_extra_g default 65 g = the old 30 + 35 g servo / misc lump (unchanged default)
    # --- hub, bridge, arms, motors
    XH_ = X_HUB if x_hub is None else x_hub          # T-066: x_hub / x_motor override (default unchanged)
    F.node("hub", (XH_, 0, 0))
    bw, bh, bt = hub_bridge
    A, Iy, Iz, J = prop_box(bw, bh, bt)           # displacement across h = z -> Iy; across w = y -> Iz
    A_b = math.pi/4*(bridge_tube[0]**2-bridge_tube[1]**2); I_b = math.pi/64*(bridge_tube[0]**4-bridge_tube[1]**4)
    if bridge_cfg == 'single':
        F.beam("hub", "s+0.000", E*A_b, E*I_b, E*I_b, G*2*I_b, RHO_CF*A_b, (0, 0, 1), "bridge", nseg=3)
    elif bridge_cfg in ('direct', 'direct+single'):   # 4 braces motor -> spar point (X_SPAR, +-Y_M, 0) (+ optional single bridge)
        if bridge_cfg == 'direct+single':
            F.beam("hub", "s+0.000", E*A_b, E*I_b, E*I_b, G*2*I_b, RHO_CF*A_b, (0, 0, 1), "bridge", nseg=3)
        F._pending_braces = (E*A_b, E*I_b, G*2*I_b, RHO_CF*A_b)
    elif bridge_cfg == 'single+V':
        F.beam("hub", "s+0.000", E*A_b, E*I_b, E*I_b, G*2*I_b, RHO_CF*A_b, (0, 0, 1), "bridge", nseg=3)
        A_v = math.pi/4*(vtube[0]**2-vtube[1]**2); I_v = math.pi/64*(vtube[0]**4-vtube[1]**4)
        for sy in (1, -1):
            F.beam("hub", f"s{sy*bridge_yv:+.3f}", E*A_v, E*I_v, E*I_v, G*2*I_v, RHO_CF*A_v, (0, 0, 1), "bridge", nseg=3)
    else:   # V: two struts hub -> spar at y = +-bridge_yv
        for sy in (1, -1):
            F.beam("hub", f"s{sy*bridge_yv:+.3f}", E*A_b, E*I_b, E*I_b, G*2*I_b, RHO_CF*A_b, (0, 0, 1), "bridge", nseg=3)
    F.lump("hub", pack_g*1e-3+hub_extra_g*1e-3)              # pack + hub print 20 g
    arm_mass_extra = 0
    for sy in (1, -1):
        for sz in (1, -1):
            nm = f"m{sy:+d}{sz:+d}"; F.node(nm, (XH_ if x_hub is not None else X_M, sy*Y_M*arm_len_scale, sz*Z_M*arm_len_scale))
            F.beam("hub", nm, E*A_a, E*I_a, E*I_a, G*2*I_a, RHO_CF*A_a, (1, 0, 0), "arm", nseg=5)
            F.lump(nm, motor_g*1e-3)
            if hasattr(F, "_pending_braces"):
                EAb, EIb, GJb, rAb = F._pending_braces
                F.beam(nm, f"s{sy*Y_M:+.3f}", EAb, EIb, EIb, GJb, rAb, (1, 0, 0), "bridge", nseg=3)
    # --- fins: rib (PETG box) from spar to fin root, fin beams along z, feet
    Ar, Iyr, Izr, Jr = prop_box(rib_wh[0], rib_wh[1], rib_wall)   # w = y-dim 30, h = z-dim 14
    # fin section properties (out-of-plane = y-bending, in-plane = x-bending)
    b = 0.12; t = fin_skin_t; core = fin_core
    EI_out = 2*fin_E_skin*t*b*((core+t)/2)**2*{"hi": 1.1, "nom": 1.0, "kd": 0.87}[kind]
    EI_in = 2*fin_E_skin*t*b**3/12*0.5          # half effectiveness (cut-outs, foam shear) EST
    mu = b*(2*t*1600+core*30)
    xf = x_fin or X_FIN
    if fin_tube:
        od_, id_, foam_t, tape_ = fin_tube
        A_f = math.pi/4*(od_**2-id_**2); I_f = math.pi/64*(od_**4-id_**4)
        EI_out = E*I_f; EI_in = E*I_f; mu = RHO_CF*A_f + 0.12*foam_t*30 + 2*0.12*tape_
    if fin_strip:
        w_s, t_s, E_s, core_s, tape = fin_strip
        kk_ = {'hi': 1.1, 'nom': 1.0, 'kd': 0.87}[kind]
        EI_out = 4*E_s*kk_*w_s*t_s*((core_s+t_s)/2)**2 + 0.12*core_s**3/12*10e6
        EI_in = 0.5*4*E_s*kk_*w_s*t_s*(b/2-w_s/2)**2
        mu = 4*w_s*t_s*1600 + b*core_s*30 + 2*b*tape
    for sy in (1, -1):
        yf = sy*y_fin; root = f"f{sy:+d}r"
        F.node(root, (xf, yf, 0.0))
        # rib: ex = +x ; vref = z -> ey = cross(z,x) = +y, ez = +z.  EIz = y-bending (Izr), EIy = z-bending (Iyr)
        F.beam(f"s{yf:+.3f}", root, E*A_r, E*I_r, E*I_r, G*2*I_r, RHO_CF*A_r, (0, 0, 1), "rib", nseg=3)   # rib = CF 14x12 tube (was PETG box)
        for sz in (1, -1):
            tip = f"f{sy:+d}{sz:+d}"; F.node(tip, (xf, yf, sz*(H_FIN if h_fin is None else h_fin)))   # T-084: h_fin override (default H_FIN 0.180 unchanged)
            # fin beam along z from root: ex = sz*z ; vref = y -> ey = cross(y, ex)
            ex = np.array([0, 0, sz]); vref = np.array([0, 1.0, 0]); ey = np.cross(vref, ex); ey /= np.linalg.norm(ey)
            # ey = +/-x (in-plane), ez = cross(ex, ey) = +/- y (out-of-plane): local z bending (EIy) = out-of-plane
            F.beam(root, tip, 1e8, EI_out, EI_in, 20.0, mu, vref, "fin", nseg=5)
            F.lump(tip, foot_pad_m)
        F.lump(root, root_g*1e-3)                           # root block / bond
    return F, dict(EI_out=EI_out, EI_in=EI_in, mu=mu, Jr=Jr, GJ_rib=G*2*I_a, EIy_rib=E*I_a, EIz_rib=E*I_a, A_rib=Ar, A_s=A_s, I_s=I_s, A_r=A_r, I_r=I_r, A_b=A_b, I_b=I_b,
                   m_rib=RHO_CF*A_a*(X_FIN-X_SPAR), m_arm=RHO_CF*A_a*math.hypot(Y_M, Z_M), A_a=A_a, I_a=I_a)


def classify(res):
    out = []
    for f, e, v, cx, cy in res:
        top = sorted(e.items(), key=lambda kv: -kv[1])[:2]
        out.append((f, ", ".join(f"{g} {100*x:.0f}%" for g, x in top)))
    return out


if __name__ == "__main__":
    for kind in ("nom", "kd"):
        F, info = build(kind)
        res = F.solve(16)
        print(f"\n## {kind}: info", {k: round(v, 5) for k, v in info.items()})
        for f, c in classify(res): print(f"  {f:7.1f} Hz  {c}")
