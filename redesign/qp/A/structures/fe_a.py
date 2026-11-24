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
        self.rot = {}; self.springs = []; self.se = []        # T-085: rotary-inertia lumps, diagonal global springs, superelements (all empty by default: T-066 / T-084 numbers unchanged)
    def node(self, name, xyz): self.n[name] = np.array(xyz, float)
    def beam(self, a, b, EA, EIy, EIz, GJ, rhoA, vref, grp, nseg=4):
        pa, pb = self.n[a], self.n[b]
        names = [a]+[f"{a}>{b}#{i}" for i in range(1, nseg)]+[b]
        for i in range(1, nseg): self.n[names[i]] = pa+(pb-pa)*i/nseg
        for i in range(nseg): self.el.append((names[i], names[i+1], EA, EIy, EIz, GJ, rhoA, np.array(vref, float), grp))
    def lump(self, name, m):
        self.mass[name] = self.mass.get(name, 0.0)+m
    def lump_rot(self, name, Ix, Iy, Iz):
        """T-085: rotary inertia (kg m2, global axes) added on a node, on top of the default m * 1e-5 lump rotary term."""
        a = self.rot.get(name, np.zeros(3)); self.rot[name] = a+np.array([Ix, Iy, Iz], float)
    def spring(self, a, b, k, grp, kr=(0.0, 0.0, 0.0)):
        """T-085: grounded-free translational (kx, ky, kz in N/m) + rotational (N m/rad) springs between nodes a and b, global axes, no offset."""
        self.springs.append((a, b, np.array(list(k)+list(kr), float), grp))
    def superelement(self, names, K, grp):
        """T-085: a symmetric 6 n x 6 n stiffness (SI, global axes) over the listed nodes (hub joint from the solid hub FEA)."""
        self.se.append((list(names), np.array(K, float), grp))
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
        for nm, Ir in self.rot.items():
            i = idx[nm]
            for q in range(3): M[6*i+3+q, 6*i+3+q] += Ir[q]
        for (a, b, k6, grp) in self.springs:
            ia, ib = idx[a], idx[b]
            for q in range(6):
                for (p1, p2, sg) in ((ia, ia, 1), (ib, ib, 1), (ia, ib, -1), (ib, ia, -1)): K[6*p1+q, 6*p2+q] += sg*k6[q]
        for (names_, Kse, grp) in self.se:
            dof = [6*idx[nm]+q for nm in names_ for q in range(6)]; K[np.ix_(dof, dof)] += Kse
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
            for (a, b, k6, grp) in self.springs:
                ia, ib = idx[a], idx[b]; du = v[6*ia:6*ia+6]-v[6*ib:6*ib+6]; e[grp] = e.get(grp, 0.0)+0.5*float(k6@(du*du))
            for (names_, Kse, grp) in self.se:
                dof = [6*idx[nm]+q for nm in names_ for q in range(6)]; ue = v[dof]; e[grp] = e.get(grp, 0.0)+0.5*float(ue@Kse@ue)
            tot = sum(e.values())
            cy = math.sqrt(sum(v[6*idx[m]+1]**2+v[6*idx[m]+2]**2 for m in names if m.startswith("m+") or m.startswith("m-") and ">" not in m))
            cx = math.sqrt(sum(v[6*idx[m]]**2 for m in names if (m.startswith("m+") or m.startswith("m-")) and ">" not in m))
            res.append((f[i], {g: x/tot for g, x in e.items()}, v, cx, cy))
        return res


def hub_superelement(Fl, pts_mm, pb_mm):
    """T-085: stiffness (SI, 36 x 36, global axes) of the hub as a superelement from the solid hub FEA flexibility.
    Fl: 30 x 30 generalised flexibility of five masters (four stub ends UR, LL, LR, UL and the hub centre), load = N and N mm, displacement = mm and rad (work conjugates),
    bridge bore fixed.  The sixth node is the bore (fixed in the FEA, free here): K = T^T Kq T with the rigid-body transfer T of that node (rigid motions strain nothing)."""
    P = np.diag([1, 1, 1, 1e3, 1e3, 1e3]); Q = np.diag([1e-3, 1e-3, 1e-3, 1, 1, 1]); n = Fl.shape[0]//6
    Fs = np.zeros_like(Fl)
    for i in range(n):
        for j in range(n): Fs[6*i:6*i+6, 6*j:6*j+6] = Q@Fl[6*i:6*i+6, 6*j:6*j+6]@P
    Fs = 0.5*(Fs+Fs.T); Kq = np.linalg.inv(Fs); Kq = 0.5*(Kq+Kq.T)
    T = np.zeros((6*n, 6*(n+1)))
    for i in range(n):
        r = (np.array(pts_mm[i], float)-np.array(pb_mm, float))*1e-3
        sk = np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]])
        T[6*i:6*i+6, 6*i:6*i+6] = np.eye(6); T[6*i:6*i+3, 6*n:6*n+3] = -np.eye(3); T[6*i:6*i+3, 6*n+3:6*n+6] = sk; T[6*i+3:6*i+6, 6*n+3:6*n+6] = -np.eye(3)
    K = T.T@Kq@T; return 0.5*(K+K.T)


def _link(F, a, b, grp="rigid"):
    """T-085: stiff massless link between two nodes (EA 1e7 N, EI 2e2 N m2: at least 80x the soft springs it joins; the nodes carry small lumps)."""
    d = F.n[b]-F.n[a]; ax = int(np.argmin(np.abs(d))); vref = [0, 0, 0]; vref[ax] = 1
    F.beam(a, b, 1e7, 2e2, 2e2, 2e2, 0.0, tuple(vref), grp, nseg=1)


def add_pack(F, x_hubnode, kind, pack_g, c):
    """T-085: the pack (pack_g = 295.7 g incl. tray CGE-008 13.3 g, straps 8.9 g, pad 3.5 g) on the drawn tray, instead of a lump on the hub node.
    c['mode'] = 'rigid': one lump at (x, 0, z) rigid on the hub (T-084 pack_place; c['rot'] adds the pack's box rotary inertia).
    c['mode'] = 'tray':  tray plate as a cantilever beam from the hub aft face (x_face) to the pack x (section: width c['w'] x t x solid fraction, PETG corner modulus),
        pack cell (pack_g - tray_g) lumped at its CG (x, 0, z) with the box rotary inertia of 107 (y) x 33 (x) x 46 (z) mm, tied to the hub / tray by pad springs
        (collar-top patch to the hub, four plate patches to the tray; stiffness E_pad A / t, shear E_pad / 3; strap preload assumed to keep contact)."""
    x, z = c['x'], c['z']; mt = c.get('tray_g', 13.3); mp = pack_g-mt
    Ix, Iy, Iz = [mp*1e-3/12*v for v in ((0.107**2+0.046**2), (0.033**2+0.046**2), (0.107**2+0.033**2))]
    if c['mode'] == 'rigid':
        F.node('pack', (x, 0, z)); F.beam(c.get('anchor', 'hub'), 'pack', 1e9, 1e5, 1e5, 1e5, 0.0, (0, 0, 1), 'tray', nseg=1); F.lump('pack', pack_g*1e-3)
        if c.get('rot'): F.lump_rot('pack', Ix, Iy, Iz)
        return
    E_ = E_PETG[kind]; G_ = G_PETG[kind]; w, t, s = c['w'], c.get('t', 1.2e-3), c['solid']
    zt = 0.0074; xf = x_hubnode+0.024                     # plate mid-plane (plate 6.8..8.0 on the 2.0 mm root pad), hub aft face (hub x + 24 mm)
    F.node('tr0', (xf, 0, zt)); F.node('trc', (x, 0, zt)); F.node('pk', (x, 0, z))
    _link(F, c.get('anchor', 'hub'), 'tr0'); F.lump('tr0', 0.15*mt*1e-3)
    F.beam('tr0', 'trc', E_*w*t*s, E_*w*t**3/12*s, E_*t*w**3/12*s, G_*w*t**3/3*s, 0.0, (0, 0, 1), 'tray', nseg=1); F.lump('trc', 0.85*mt*1e-3)

    def pad(nameH, posH, rigidH, nameP, posP, k):
        F.node(nameH, posH); F.node(nameP, posP); _link(F, c.get('anchor', 'hub') if rigidH == 'hub' else rigidH, nameH); _link(F, 'pk', nameP); F.lump(nameH, 3e-4); F.lump(nameP, 3e-4)
        F.spring(nameH, nameP, k, 'pad')
    Ep, tp = c['pad_E'], c.get('pad_t', 1.0e-3); xc = c['collar_x']; A_c = c['collar_A']
    zm = c.get('z_mult', 1.0)      # T-085: compression-stiffness multiplier of the thin pad (shape factor / bulk limit, see T085_report s3.1); default 1 = E A / t
    pad('cpH', (xc, 0, 0.008), 'hub', 'cpP', (xc, 0, 0.009), (Ep/3*A_c/tp, Ep/3*A_c/tp, zm*Ep*A_c/tp))
    A_p = c['pad_A']-A_c; kz = zm*Ep*A_p/4/tp; kx = Ep/3*A_p/4/tp
    for i, (dx, dy) in enumerate(((-7.5e-3, -26e-3), (7.5e-3, -26e-3), (-7.5e-3, 26e-3), (7.5e-3, 26e-3))):
        pad('ppH%d' % i, (x+dx, dy, 0.008), 'trc', 'ppP%d' % i, (x+dx, dy, 0.009), (kx, kx, kz))
    F.lump('pk', mp*1e-3-3.0e-3); F.lump_rot('pk', Ix, Iy, Iz)       # 3.0 g = the ten light pad-node lumps (3e-4 kg each), taken from the pack cell


def build(kind="nom", y_fin=Y_FIN, rib_wall=0.8e-3, rib_wh=(30e-3, 14e-3), arm_len_scale=1.0, hub_bridge=(24e-3, 30e-3, 1.5e-3),
          foot_pad_m=0.003, wing_g=212.0, pack_g=270.0, motor_g=65.0+11.06+5.0+4.3+2.9, avionics_g=110.0, fin_skin_t=0.1e-3, fin_core=15e-3,
          fin_E_skin=50e9, root_fix=None, verbose=False, arm_tube=(14e-3, 12e-3), bridge_cf=True, bridge_tube=(8e-3, 6e-3), spar_tube=(16e-3, 14e-3), rib_tube=None, bridge_cfg='single', bridge_yv=0.12, vtube=(8e-3, 6e-3), fin_strip=None, arm_E_scale=1.0, fin_tube=None, x_fin=None, root_g=6.0, centre_extra_g=65.0, x_hub=None, hub_extra_g=20.0, wing_cell=None, h_fin=None, hub_se=None, pack_cfg=None, bridge_f=(1.0, 1.0, 1.0), motor_mount=None):
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
        if hub_se is None:
            F.beam("hub", "s+0.000", E*A_b, E*I_b*bridge_f[0], E*I_b*bridge_f[1], G*2*I_b*bridge_f[2], RHO_CF*A_b, (0, 0, 1), "bridge", nseg=3)   # T-085: bridge_f scales (z-bending, y-bending, torsion) for the option sketches; default 1
        else:   # T-085: the bridge starts at the superelement's fixed-bore node 'bb' (hub FEA models the block and 40 mm of bridge); hub -> bb is inside the superelement
            pb = hub_se["pts_mm"]["bb"]; XH0 = X_HUB if x_hub is None else x_hub
            F.node("bb", (XH0+pb[0]*1e-3, pb[1]*1e-3, pb[2]*1e-3))
            F.beam("bb", "s+0.000", E*A_b, E*I_b*bridge_f[0], E*I_b*bridge_f[1], G*2*I_b*bridge_f[2], RHO_CF*A_b, (0, 0, 1), "bridge", nseg=3)
            F.lump("bb", 0.5*RHO_CF*A_b*pb[0]*1e-3); F.lump("hub", 0.5*RHO_CF*A_b*pb[0]*1e-3)     # the bridge length hub -> bb as lumps
        A_v = math.pi/4*(vtube[0]**2-vtube[1]**2); I_v = math.pi/64*(vtube[0]**4-vtube[1]**4)
        for sy in (1, -1):
            F.beam("hub", f"s{sy*bridge_yv:+.3f}", E*A_v, E*I_v, E*I_v, G*2*I_v, RHO_CF*A_v, (0, 0, 1), "bridge", nseg=3)
    else:   # V: two struts hub -> spar at y = +-bridge_yv
        for sy in (1, -1):
            F.beam("hub", f"s{sy*bridge_yv:+.3f}", E*A_b, E*I_b, E*I_b, G*2*I_b, RHO_CF*A_b, (0, 0, 1), "bridge", nseg=3)
    if pack_cfg is None:
        F.lump("hub", pack_g*1e-3+hub_extra_g*1e-3)              # pack + hub print 20 g
    else:                                                          # T-085: pack on the drawn tray (see add_pack); hub_extra_g stays on the hub node
        F.lump("hub", hub_extra_g*1e-3); add_pack(F, XH_ if x_hub is not None else X_M, kind, pack_g, pack_cfg)
    arm_mass_extra = 0
    for sy in (1, -1):
        for sz in (1, -1):
            nm = f"m{sy:+d}{sz:+d}"; F.node(nm, (XH_ if x_hub is not None else X_M, sy*Y_M*arm_len_scale, sz*Z_M*arm_len_scale))
            nm_m = nm
            if motor_mount is not None:   # T-085 sketch C4 (default None: unchanged): motor + prop (fraction mf of motor_g) on a translational spring (kx, ky, kz N/m) to the arm tip 'a..'
                kx_, ky_, kz_, mf_ = motor_mount; nm = f"a{sy:+d}{sz:+d}"; F.node(nm, F.n[nm_m].copy())
                F.spring(nm, nm_m, (kx_, ky_, kz_), "mount", kr=(50.0, 50.0, 50.0))
            if hub_se is None:
                F.beam("hub", nm, E*A_a, E*I_a, E*I_a, G*2*I_a, RHO_CF*A_a, (1, 0, 0), "arm", nseg=5)
            else:   # T-085: the arm starts at the stub end of the hub FEA (s = S_END along the tube); the stub (tube, sleeve, block) is in the superelement
                st = {(1, 1): "UR", (-1, -1): "LL", (1, -1): "LR", (-1, 1): "UL"}[(sy, sz)]; pe = hub_se["pts_mm"][st]; XH0 = X_HUB if x_hub is None else x_hub
                F.node("h_"+st, (XH0+pe[0]*1e-3, pe[1]*1e-3, pe[2]*1e-3))
                F.beam("h_"+st, nm, E*A_a, E*I_a, E*I_a, G*2*I_a, RHO_CF*A_a, (1, 0, 0), "arm", nseg=5)
                F.lump("h_"+st, RHO_CF*A_a*hub_se["s_end_mm"]*1e-3)                # the stub tube mass (hub centre -> stub end) as a lump
            if motor_mount is None: F.lump(nm, motor_g*1e-3)
            else: F.lump(nm_m, mf_*motor_g*1e-3); F.lump(nm, (1-mf_)*motor_g*1e-3)
            if hasattr(F, "_pending_braces"):
                EAb, EIb, GJb, rAb = F._pending_braces
                F.beam(nm, f"s{sy*Y_M:+.3f}", EAb, EIb, EIb, GJb, rAb, (1, 0, 0), "bridge", nseg=3)
    if hub_se is not None:
        F.superelement(["h_UR", "h_LL", "h_LR", "h_UL", "hub", "bb"], hub_se["K"], "hubjoint")
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
