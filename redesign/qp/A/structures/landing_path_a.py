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
    put(out, name+' - peel, tension side [EST lower bound]', 'EST BOND 2.0 MPa', rfs[2])
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
            put(out, 'P1 pad PSA to shoe plate (180 mm2) - shear', 'EST PSA 0.10 MPa', PSA/np.maximum(tau, 1e-9))
            put(out, 'P1 pad PSA to shoe plate (180 mm2) - peel (30 mm lever, no foam compliance)', 'EST PSA 0.10 MPa', PSA/np.maximum(peel, 1e-9))
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
        s = (np.hypot(M[:, 1], M[:, 2])/Zb+np.abs(F[:, 0])/(SAD_W**2-math.pi*ROD**2/4))*KP; t = (np.abs(M[:, 0])/Tb+n_(F[:, 1:])/(4*SAD_W*tw))*KP
        out.setdefault('P11 saddle socket wall, PETG box 19x19 / bore 14, bending + torsion', ('EST PETG_ILAY 9.5 MPa', []))[1].append(comb((s, PETG_ILAY), (t, PETG_ILAY)))
        # P12 saddle socket-to-ring junction (PETG): plane x = SAD_X0, chord z x 19 (y); loads about its centre
        Sj = S_(k, SAD_X0, 0.0); F, M = M_about(FBt, k, Sj); a = chord(SAD_RO, SAD_X0-SX)
        out.setdefault('P12 saddle socket-to-ring junction, PETG (%.1f x 19 mm)' % (a*1e3), ('EST PETG_ILAY 9.5 MPa', []))[1].append(
            rect_rf(F[:, 0], np.hypot(F[:, 1], F[:, 2]), M[:, 0], M[:, 2], M[:, 1], SAD_W, a, PETG_ILAY, PETG_ILAY))
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


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    print(f"# landing_path_a.py, geometry {'legacy' if L.LEGACY else 'CAD'}: x_ground {XF:.4f} y {YF:.3f} z pad centre {ZF:.4f} m, CG {L.geom()['cg']}, mass {L.M_GATE} kg, plateau 30 N, mu {L.MU}")
    print(f"# KF {KF:.3f} KP {KP:.3f}; sections: fin tube {FOD*1e3:.0f}x{FID*1e3:.0f} Z {Z_F*1e9:.0f} mm3; rib {ROD*1e3:.0f}x{RID*1e3:.0f} Z {Z_R*1e9:.0f} mm3; spar {SOD*1e3:.0f}x{SID*1e3:.0f} Z {Z_S*1e9:.0f} mm3")
    allrf = {}; t0 = time.time()
    for name, kw in cases(quick):
        q = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, **kw)
        FBt = q['trace'].reshape(-1, 4, 3)
        rf = checks(FBt)
        for key, (lab, a) in rf.items(): allrf.setdefault(key, []).append((float(a.min()), name, lab))
        print(f"  case {name:34s} side {q['side'].max():5.1f} N Fmax {q['F'].max():5.1f} N  rib RF (landing_a) {q['rib_rf']:.2f}  tilt_end {q['tilt_end']:.1f}  min path RF {min(float(v.min()) for _, (l, v) in rf.items()):.2f}  [{time.time()-t0:.0f} s]", flush=True)
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
    firm = [r for r in rows if "peel" not in r[1] and "P1 " not in r[1]]
    print(f"MINIMUM excluding the peel rows and the PSA rows (allowable with no repo source): {min(firm)[1]} RF {min(firm)[0]:.2f} ({min(firm)[3]})")
    print("Rows below 1.0:", "; ".join(f"{r[1]} {r[0]:.2f}" for r in sorted(rows) if r[0] < 1.0))
    print("\n## F10 volumes (voxel 0.25 mm of the stub-built CAD shapes, minus cuts; solid PETG at RHO_PETG %.2f g/cm3)" % W.RHO_PETG)
    for pid, (v, mg, ml, vs) in volumes().items():
        print(f"{pid}: voxel volume {v:.2f} cm3 -> solid {mg:.2f} g; listed {ml} g; sum of shape volumes before cuts {vs:.2f} cm3 -> {vs*W.RHO_PETG:.2f} g; listed / solid {ml/mg:.2f}")
