"""C4 finite-element model of one half-fin + motor tube + motor station (K09-L).

Library only (no I/O, no proofkit): fin_structures.py builds the inputs from params.json and the C4 assumptions.

Model (one quarter of the fin group, e.g. upper-right `UR`; the other three are mirror images):
  * motor tube: 3-D Euler-Bernoulli frame elements along z from the through-core block face (z_clamp) to the tube
    end, consistent mass. Root at the block: clamped, or rotational springs k_rx / k_ry (block + wing compliance).
  * half-fin: flat shell in the x-z plane, 4-node rectangles. Membrane = plane-stress Q4 (2x2 Gauss); plate =
    Mindlin Q4 with selective reduced integration (bending 2x2, transverse shear 1 point). Foam board is a
    sandwich (paper faces + PS foam core); n layers bonded face to face.
  * bond fin LE -> tube: every fin LE node is a rigid slave of the tube node at the same height (offset = tube
    radius in x). Drilling rotation of the other fin nodes is not a DOF (removed).
  * fin root (wing skin): translations fixed; rotations free ("pinned", taped root) or fixed ("clamped").
  * motor + prop + mount: rigid body lumped on the tube node at the station height with its true offsets
    (6x6 rigid-body mass); ESC and foot lumped on the nearest fin nodes.
  * optional brace: an axial-only strut from a point on the motor station to a fixed anchor on the wing.
  * gyroscopic matrix of the spinning prop + rotor for a Campbell diagram (modal reduction).
Units SI. Aircraft frame: x aft, y right (out of the fin plane), z up.
"""
import math

import numpy as np
import scipy.linalg as sla
import scipy.sparse as sp
import scipy.sparse.linalg as spla

NDOF = 6   # ux uy uz rx ry rz


# ------------------------------------------------------------------ materials
def board_props(layers, t_board, t_face, E_face, nu_face, E_core, G_core, areal_mass):
    """Equivalent shell properties of `layers` foam boards bonded face to face (isotropic faces, PS core)."""
    t_core = t_board - 2 * t_face
    h = layers * t_board
    plies = []                                    # (E, t, z_mid)
    z0 = -h / 2
    for _ in range(layers):
        for E, t in ((E_face, t_face), (E_core, t_core), (E_face, t_face)):
            plies.append((E, t, z0 + t / 2))
            z0 += t
    c = 1.0 / (1 - nu_face ** 2)
    A = c * sum(E * t for E, t, z in plies)                       # membrane stiffness N/m
    D = c * sum(E * (t * z * z + t ** 3 / 12) for E, t, z in plies)   # bending stiffness N m
    S = G_core * h * h / (layers * t_core)                        # transverse shear stiffness N/m (sandwich)
    return {"A": A, "D": D, "S": S, "nu": nu_face, "h": h, "rho_h": areal_mass * layers,
            "z_face_out": h / 2 - t_face / 2}


# ------------------------------------------------------------------ elements
def frame_element(p1, p2, E, G, A, Iy, Iz, J, rho, ref=(1.0, 0.0, 0.0)):
    """12x12 stiffness and consistent mass of a 3-D frame element, global axes."""
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    L = np.linalg.norm(p2 - p1)
    e1 = (p2 - p1) / L
    r = np.asarray(ref, float)
    if abs(np.dot(r, e1)) > 0.9:
        r = np.array([0.0, 1.0, 0.0]) if abs(e1[1]) < 0.9 else np.array([0.0, 0.0, 1.0])
    e2 = r - np.dot(r, e1) * e1
    e2 /= np.linalg.norm(e2)
    e3 = np.cross(e1, e2)
    R = np.vstack([e1, e2, e3])
    k = np.zeros((12, 12))
    # axial (0,6), torsion (3,9)
    for (a, b), s in (((0, 6), E * A / L), ((3, 9), G * J / L)):
        k[np.ix_([a, b], [a, b])] += s * np.array([[1, -1], [-1, 1]])
    # bending in local x-y (v: 1,7 ; theta_z: 5,11), EIz
    kb = np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                   [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]]) / L ** 3
    k[np.ix_([1, 5, 7, 11], [1, 5, 7, 11])] += E * Iz * kb
    # bending in local x-z (w: 2,8 ; theta_y: 4,10), EIy, sign-flipped coupling
    S = np.diag([1, -1, 1, -1])
    k[np.ix_([2, 4, 8, 10], [2, 4, 8, 10])] += E * Iy * (S @ kb @ S)
    m = np.zeros((12, 12))
    mL = rho * A * L
    m[np.ix_([0, 6], [0, 6])] += mL / 6 * np.array([[2, 1], [1, 2]])
    m[np.ix_([3, 9], [3, 9])] += rho * J * L / 6 * np.array([[2, 1], [1, 2]])
    mb = mL / 420 * np.array([[156, 22 * L, 54, -13 * L], [22 * L, 4 * L * L, 13 * L, -3 * L * L],
                              [54, 13 * L, 156, -22 * L], [-13 * L, -3 * L * L, -22 * L, 4 * L * L]])
    m[np.ix_([1, 5, 7, 11], [1, 5, 7, 11])] += mb
    m[np.ix_([2, 4, 8, 10], [2, 4, 8, 10])] += S @ mb @ S
    T = np.zeros((12, 12))
    for i in range(4):
        T[3 * i:3 * i + 3, 3 * i:3 * i + 3] = R
    return T.T @ k @ T, T.T @ m @ T


_GP = (-1 / math.sqrt(3), 1 / math.sqrt(3))
_XI = ((-1, -1), (1, -1), (1, 1), (-1, 1))


def _dN(xi, eta, a, b):
    """d N_i / dx, d N_i / dz on an a x b rectangle (nodes counter-clockwise from (-,-))."""
    dx = np.array([0.25 * xs * (1 + eta * es) * 2 / a for xs, es in _XI])
    dz = np.array([0.25 * es * (1 + xi * xs) * 2 / b for xs, es in _XI])
    N = np.array([0.25 * (1 + xi * xs) * (1 + eta * es) for xs, es in _XI])
    return N, dx, dz


def shell_element(a, b, pr):
    """24x24 stiffness and lumped mass of a rectangular flat shell in the x-z plane (DOF order per node ux..rz)."""
    A, D, S, nu = pr["A"], pr["D"], pr["S"], pr["nu"]
    Cm = A * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    Cb = D * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    Cs = S * np.eye(2)
    k = np.zeros((24, 24))
    J = a * b / 4
    for xi in _GP:
        for eta in _GP:
            N, dx, dz = _dN(xi, eta, a, b)
            Bm = np.zeros((3, 24))
            Bb = np.zeros((3, 24))
            for i in range(4):
                o = 6 * i
                Bm[0, o + 0] = dx[i]
                Bm[1, o + 2] = dz[i]
                Bm[2, o + 0] = dz[i]
                Bm[2, o + 2] = dx[i]
                # beta_x = -rz, beta_z = rx
                Bb[0, o + 5] = -dx[i]
                Bb[1, o + 3] = dz[i]
                Bb[2, o + 5] = -dz[i]
                Bb[2, o + 3] = dx[i]
            k += J * (Bm.T @ Cm @ Bm + Bb.T @ Cb @ Bb)
    N, dx, dz = _dN(0.0, 0.0, a, b)
    Bs = np.zeros((2, 24))
    for i in range(4):
        o = 6 * i
        Bs[0, o + 1] = dx[i]
        Bs[0, o + 5] = -N[i]
        Bs[1, o + 1] = dz[i]
        Bs[1, o + 3] = N[i]
    k += 4 * J * (Bs.T @ Cs @ Bs)
    m = np.zeros(24)
    mt = pr["rho_h"] * a * b / 4
    mr = mt * pr["h"] ** 2 / 12
    for i in range(4):
        m[6 * i:6 * i + 3] = mt
        m[6 * i + 3] = m[6 * i + 5] = mr
        m[6 * i + 4] = mr * 1e-3
    return k, np.diag(m)


def shell_resultants(a, b, pr, ue):
    """Membrane forces (Nx, Nz, Nxz) N/m and moments (Mx, Mz, Mxz) N m/m at the element centre."""
    A, D, nu = pr["A"], pr["D"], pr["nu"]
    Cm = A * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    Cb = D * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    N, dx, dz = _dN(0.0, 0.0, a, b)
    Bm = np.zeros((3, 24))
    Bb = np.zeros((3, 24))
    for i in range(4):
        o = 6 * i
        Bm[0, o], Bm[1, o + 2], Bm[2, o], Bm[2, o + 2] = dx[i], dz[i], dz[i], dx[i]
        Bb[0, o + 5], Bb[1, o + 3], Bb[2, o + 5], Bb[2, o + 3] = -dx[i], dz[i], -dz[i], dx[i]
    return Cm @ (Bm @ ue), Cb @ (Bb @ ue)


def rigid_mass(parts):
    """6x6 mass matrix about a node of rigid parts [(m, (cx,cy,cz) offset from the node, (Jx,Jy,Jz) about own CG)]."""
    M = np.zeros((6, 6))
    for m, c, Jc in parts:
        c = np.asarray(c, float)
        cx = np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]])
        M[:3, :3] += m * np.eye(3)
        M[:3, 3:] += -m * cx
        M[3:, :3] += m * cx
        M[3:, 3:] += np.diag(Jc) + m * (np.dot(c, c) * np.eye(3) - np.outer(c, c))
    return M


# ------------------------------------------------------------------ model
class Model:
    """Assembled quarter-fin model. Build with `build(cfg)`."""


def build(cfg):
    """cfg keys (SI): tube {E, G, od, id, rho, z_clamp, z_end}, z_station, fin {x_le, x_te, z_root, z_top, props
    or None}, nx, nz, n_ext, root ('pinned'|'clamped'), k_root_rx, k_root_ry (None = clamped), station parts
    [(m, offset, J)], point masses [(m, (x, z))] on the fin, strut {ax, az, ay (attach offset from the station
    node), anchor (x, y, z), EA} or None, spin_Ip (kg m2, spinning inertia about the shaft x)."""
    tb, fn = cfg["tube"], cfg["fin"]
    x_t = tb["x"]
    r_o, r_i = tb["od"] / 2, tb["id"] / 2
    A_t = math.pi * (r_o ** 2 - r_i ** 2)
    I_t = math.pi / 4 * (r_o ** 4 - r_i ** 4) * tb.get("I_factor", 1.0)
    J_t = 2 * math.pi / 4 * (r_o ** 4 - r_i ** 4) * tb.get("I_factor", 1.0)
    rho_t = tb["rho"] * tb.get("mass_factor", 1.0)
    z0, zs, zend = tb["z_clamp"], cfg["z_station"], tb["z_end"]
    nz, nx = cfg["nz"], cfg["nx"]
    has_fin = fn.get("props") is not None
    zf = np.linspace(z0, zs, nz + 1)                       # fin rows = tube nodes up to the station
    zt = list(zf) + list(np.linspace(zs, zend, cfg["n_ext"] + 1)[1:])
    nodes = [(x_t, 0.0, z) for z in zt]                    # tube nodes 0..len(zt)-1
    i_station = nz
    i_end = len(zt) - 1
    fin_id = {}
    if has_fin:
        xf = np.linspace(fn["x_le"], fn["x_te"], nx + 1)
        for j, z in enumerate(zf):
            for i, x in enumerate(xf):
                fin_id[(i, j)] = len(nodes)
                nodes.append((x, 0.0, z))
    struts = list(cfg.get("struts") or ([cfg["strut"]] if cfg.get("strut") else []))
    strut_nodes = []
    for st in struts:
        strut_nodes.append(len(nodes))
        p = nodes[i_station]
        nodes.append((p[0] + st["ax"], p[1] + st["ay"], p[2] + st["az"]))
    strut_node = strut_nodes[0] if strut_nodes else None
    nn = len(nodes)
    N = NDOF * nn
    rows, cols, kv, mv = [], [], [], []

    def add(dofs, ke, me):
        for a, da in enumerate(dofs):
            for b, db in enumerate(dofs):
                if ke[a, b] != 0.0 or me[a, b] != 0.0:
                    rows.append(da)
                    cols.append(db)
                    kv.append(ke[a, b])
                    mv.append(me[a, b])

    def dofs_of(*ns):
        return [NDOF * n + d for n in ns for d in range(NDOF)]

    for e in range(len(zt) - 1):
        ke, me = frame_element(nodes[e], nodes[e + 1], tb["E"], tb["G"], A_t, I_t, I_t, J_t, rho_t)
        add(dofs_of(e, e + 1), ke, me)
        sv = cfg.get("sleeve")
        if sv and 0.5 * (nodes[e][2] + nodes[e + 1][2]) < sv["z_top"]:
            ro, ri = sv["od"] / 2, sv["id"] / 2
            As, Is = math.pi * (ro ** 2 - ri ** 2), math.pi / 4 * (ro ** 4 - ri ** 4)
            ke, me = frame_element(nodes[e], nodes[e + 1], sv["E"], sv["G"], As, Is, Is, 2 * Is, sv["rho"])
            add(dofs_of(e, e + 1), ke, me)
    shells = []
    if has_fin:
        pr = fn["props"]
        a = (fn["x_te"] - fn["x_le"]) / nx
        b = (zs - z0) / nz
        ke, me = shell_element(a, b, pr)
        for j in range(nz):
            for i in range(nx):
                ns = (fin_id[(i, j)], fin_id[(i + 1, j)], fin_id[(i + 1, j + 1)], fin_id[(i, j + 1)])
                add(dofs_of(*ns), ke, me)
                shells.append(ns)
    # chordwise CF strip pair bonded on both fin faces along one fin row (out-of-plane flange beam)
    stf_elems = []
    for stf in cfg.get("stiffeners", []) if has_fin else []:
        j = int(round(stf["row_frac"] * nz))
        for i in range(nx):
            stf_elems.append((fin_id[(i, j)], fin_id[(i + 1, j)], stf))
            n1, n2 = fin_id[(i, j)], fin_id[(i + 1, j)]
            ke, me = frame_element(nodes[n1], nodes[n2], stf["E"], stf["G"], stf["A"], 1e-15, stf["I_out"],
                                   stf["J"], stf["rho"])
            add(dofs_of(n1, n2), ke, me)
    # station rigid mass
    Ms = rigid_mass(cfg["station_parts"])
    add(dofs_of(i_station), np.zeros((6, 6)), Ms)
    # point masses on the fin (nearest node), translations + tiny rotary
    for m, (x, z) in cfg.get("fin_masses", []):
        if has_fin:
            best = min(fin_id.values(), key=lambda n: (nodes[n][0] - x) ** 2 + (nodes[n][2] - z) ** 2)
        else:
            best = i_station
        add(dofs_of(best), np.zeros((6, 6)), np.diag([m, m, m, 0, 0, 0]))
    # strut (axial only) from the strut node to a fixed anchor
    k_strut = None
    strut_info = []
    for st, sn in zip(struts, strut_nodes):
        p = np.array(nodes[sn])
        d = np.array(st["anchor"]) - p
        L = np.linalg.norm(d)
        n_ = d / L
        k_strut = st["EA"] / L
        strut_info.append({"node": sn, "n": n_, "L": L, "k": k_strut, "EA": st["EA"]})
        ke = np.zeros((6, 6))
        ke[:3, :3] = k_strut * np.outer(n_, n_)
        add(dofs_of(sn), ke, np.diag([1e-6] * 3 + [1e-12] * 3))
    # root springs at the clamp
    if cfg.get("k_root_rx") is not None:
        ke = np.diag([0, 0, 0, cfg["k_root_rx"], cfg["k_root_ry"], cfg.get("k_root_rz", 1e9)])
        add(dofs_of(0), ke, np.zeros((6, 6)))
    K = sp.coo_matrix((kv, (rows, cols)), shape=(N, N)).tocsr()
    M = sp.coo_matrix((mv, (rows, cols)), shape=(N, N)).tocsr()

    # ---- constraints: transformation full = T @ reduced
    fixed = set()
    if cfg.get("k_root_rx") is None:
        fixed.update(dofs_of(0))
    else:
        fixed.update(NDOF * 0 + d for d in (0, 1, 2))
    slave = {}                                             # node -> (master node, offset r)
    if has_fin:
        for j in range(nz + 1):
            n = fin_id[(0, j)]
            slave[n] = (j, np.array(nodes[n]) - np.array(nodes[j]))
        for i in range(1, nx + 1):
            n = fin_id[(i, 0)]
            fixed.update(NDOF * n + d for d in (0, 1, 2))
            if cfg["root"] == "clamped":
                fixed.update(NDOF * n + d for d in (3, 5))
        for (i, j), n in fin_id.items():
            if i > 0:
                fixed.add(NDOF * n + 4)                     # no drilling DOF in the shell
    for sn in strut_nodes:
        slave[sn] = (i_station, np.array(nodes[sn]) - np.array(nodes[i_station]))
    red = {}
    for n in range(nn):
        if n in slave:
            continue
        for d in range(NDOF):
            g = NDOF * n + d
            if g not in fixed:
                red[g] = len(red)
    Tr, Tc, Tv = [], [], []
    for g, c in red.items():
        Tr.append(g)
        Tc.append(c)
        Tv.append(1.0)
    for n, (mstr, r) in slave.items():
        # u_s = u_m + theta_m x r ; theta_s = theta_m
        rx = np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]])
        Tn = np.zeros((6, 6))
        Tn[:3, :3] = np.eye(3)
        Tn[:3, 3:] = -rx
        Tn[3:, 3:] = np.eye(3)
        for a in range(6):
            for b in range(6):
                gm = NDOF * mstr + b
                if Tn[a, b] != 0 and gm in red:
                    Tr.append(NDOF * n + a)
                    Tc.append(red[gm])
                    Tv.append(Tn[a, b])
    T = sp.coo_matrix((Tv, (Tr, Tc)), shape=(N, len(red))).tocsr()
    mdl = Model()
    mdl.__dict__.update(dict(cfg=cfg, nodes=np.array(nodes), K=K, M=M, T=T, Kr=(T.T @ K @ T).tocsc(),
                             Mr=(T.T @ M @ T).tocsc(), i_station=i_station, i_end=i_end, fin_id=fin_id,
                             shells=shells, Ms=Ms, strut_node=strut_node, k_strut=k_strut, strut_info=strut_info, stf_elems=stf_elems, has_fin=has_fin,
                             n_tube=len(zt), A_t=A_t, I_t=I_t, J_t=J_t))
    return mdl


# ------------------------------------------------------------------ analyses
def modes(mdl, n=10):
    """Undamped non-rotating modes: (f_Hz array, full-DOF shapes N x n), mass-normalised."""
    k = min(n, mdl.Kr.shape[0] - 2)
    if mdl.Kr.shape[0] < 400:
        w2, V = sla.eigh(mdl.Kr.toarray(), mdl.Mr.toarray())
        w2, V = w2[:k], V[:, :k]
    else:
        w2, V = spla.eigsh(mdl.Kr, k=k, M=mdl.Mr, sigma=0.0, which="LM")
        o = np.argsort(w2)
        w2, V = w2[o], V[:, o]
    f = np.sqrt(np.maximum(w2, 0)) / (2 * math.pi)
    return f, mdl.T @ V, V


def classify(mdl, Phi_full):
    """Per mode: kinetic-energy fractions (station, tube, fin) and the station's dominant motion."""
    out = []
    Mfull = mdl.M
    ist = mdl.i_station
    sd = list(range(NDOF * ist, NDOF * ist + 6))
    tube_d = [NDOF * n + d for n in range(mdl.n_tube) for d in range(6) if n != ist]
    for c in range(Phi_full.shape[1]):
        u = Phi_full[:, c]
        tot = float(u @ (Mfull @ u))
        us = u[sd]
        ke_st = float(us @ mdl.Ms @ us)
        Mt = Mfull[tube_d][:, tube_d]
        ke_tube = float(u[tube_d] @ (Mt @ u[tube_d]))
        ke_fin = max(tot - ke_st - ke_tube, 0.0)
        # station motion at the motor CG-ish reference: translations and rotation about z (tube axis)
        comp = {"x (fore-aft, in fin plane)": abs(us[0]), "y (lateral, out of fin plane)": abs(us[1]),
                "z (axial)": abs(us[2])}
        rot = {"rx": abs(us[3]), "ry": abs(us[4]), "rz (tube torsion)": abs(us[5])}
        # torsion vs lateral: compare rotational KE about z with translational KE in y
        Jz = mdl.Ms[5, 5]
        e_y = mdl.Ms[1, 1] * us[1] ** 2
        e_x = mdl.Ms[0, 0] * us[0] ** 2
        e_rz = Jz * us[5] ** 2
        e_ry = mdl.Ms[4, 4] * us[4] ** 2
        if ke_fin / tot > 0.5:
            kind = "fin panel"
        elif max(e_y, e_rz) >= max(e_x, e_ry):
            kind = "lateral-torsion (y + tube twist)"
        else:
            kind = "fore-aft bending (x, in fin plane)"
        out.append({"kind": kind, "ke_station": ke_st / tot, "ke_tube": ke_tube / tot, "ke_fin": ke_fin / tot,
                    "e_y": e_y, "e_x": e_x, "e_rz": e_rz})
    return out


def static(mdl, loads):
    """loads = [(node index, (Fx,Fy,Fz,Mx,My,Mz))]. Returns full displacement vector."""
    F = np.zeros(mdl.K.shape[0])
    for n, f in loads:
        F[NDOF * n:NDOF * n + 6] += f
    ur = spla.spsolve(mdl.Kr, mdl.T.T @ F)
    return mdl.T @ ur


def gyro_matrix(mdl, Ip, spin_axis=(-1.0, 0.0, 0.0)):
    """Full-size gyroscopic matrix per unit spin speed (rad/s): G_ww = -[Ip e]x at the station node."""
    e = np.asarray(spin_axis, float)
    H = Ip * e
    Hx = np.array([[0, -H[2], H[1]], [H[2], 0, -H[0]], [-H[1], H[0], 0]])
    N = mdl.K.shape[0]
    G = sp.lil_matrix((N, N))
    o = NDOF * mdl.i_station + 3
    G[o:o + 3, o:o + 3] = -Hx
    return G.tocsr()


def campbell(mdl, Ip, rpms, n_modes=12):
    """Whirl frequencies (Hz) vs rpm by modal reduction on the first n_modes non-rotating modes."""
    f0, Phi_full, V = modes(mdl, n_modes)
    w = 2 * math.pi * f0
    G = gyro_matrix(mdl, Ip)
    Gm = Phi_full.T @ (G @ Phi_full)
    n = len(w)
    res = []
    for rpm in rpms:
        Om = rpm * 2 * math.pi / 60.0
        A = np.zeros((2 * n, 2 * n))
        A[:n, n:] = np.eye(n)
        A[n:, :n] = -np.diag(w ** 2)
        A[n:, n:] = -Om * Gm
        lam = np.linalg.eigvals(A)
        fr = np.sort(np.abs(lam.imag[lam.imag > 1e-6])) / (2 * math.pi)
        res.append(fr[:n])
    return f0, np.array(res)


def plate_cantilever(a, b, n, pr, n_modes=3):
    """Validation: a x b plate in the x-z plane clamped along z = 0, other edges free. First frequencies (Hz)."""
    nx = nz = n
    idx = {(i, j): j * (nx + 1) + i for j in range(nz + 1) for i in range(nx + 1)}
    N = NDOF * len(idx)
    ke, me = shell_element(a / nx, b / nz, pr)
    K = np.zeros((N, N))
    M = np.zeros((N, N))
    for j in range(nz):
        for i in range(nx):
            ns = (idx[(i, j)], idx[(i + 1, j)], idx[(i + 1, j + 1)], idx[(i, j + 1)])
            d = [NDOF * q + r for q in ns for r in range(NDOF)]
            K[np.ix_(d, d)] += ke
            M[np.ix_(d, d)] += me
    keep = [NDOF * q + r for (i, j), q in idx.items() for r in range(NDOF) if j > 0 and r != 4]
    w2 = sla.eigh(K[np.ix_(keep, keep)], M[np.ix_(keep, keep)], eigvals_only=True,
                  subset_by_index=[0, n_modes - 1])
    return np.sqrt(np.maximum(w2, 0)) / (2 * math.pi)


# ====================================================================== R2: as-designed (D3) geometry
# General flat 4-node shell (isoparametric, any convex quad in the x-z plane), a mapped half-fin mesh between a
# curved root (wing skin) and a sloped top edge, a separate motor-station node joined to the tube end by the
# printed mount (rotational springs), a brace attached to a tube node through an offset ear, and root springs.
def _dN_q4(xi, eta, xz):
    """Shape functions and global derivatives at (xi, eta) for a quad with corner coords xz (4 x 2)."""
    N = np.array([0.25 * (1 + xi * xs) * (1 + eta * es) for xs, es in _XI])
    dxi = np.array([0.25 * xs * (1 + eta * es) for xs, es in _XI])
    deta = np.array([0.25 * es * (1 + xi * xs) for xs, es in _XI])
    J = np.array([[dxi @ xz[:, 0], dxi @ xz[:, 1]], [deta @ xz[:, 0], deta @ xz[:, 1]]])
    detJ = float(np.linalg.det(J))
    inv = np.linalg.inv(J)
    dx = inv[0, 0] * dxi + inv[0, 1] * deta
    dz = inv[1, 0] * dxi + inv[1, 1] * deta
    return N, dx, dz, detJ


def _B_q4(N, dx, dz):
    Bm, Bb, Bs = np.zeros((3, 24)), np.zeros((3, 24)), np.zeros((2, 24))
    for i in range(4):
        o = 6 * i
        Bm[0, o], Bm[1, o + 2], Bm[2, o], Bm[2, o + 2] = dx[i], dz[i], dz[i], dx[i]
        Bb[0, o + 5], Bb[1, o + 3], Bb[2, o + 5], Bb[2, o + 3] = -dx[i], dz[i], -dz[i], dx[i]
        Bs[0, o + 1], Bs[0, o + 5], Bs[1, o + 1], Bs[1, o + 3] = dx[i], -N[i], dz[i], N[i]
    return Bm, Bb, Bs


def shell_q4(xz, pr):
    """24x24 stiffness and lumped mass of a general flat quad shell in the x-z plane (same DOF order and
    formulation as shell_element: Q4 membrane, Mindlin plate, 2x2 / 1-point selective integration)."""
    xz = np.asarray(xz, float)
    A, D, S, nu = pr["A"], pr["D"], pr["S"], pr["nu"]
    Cm = A * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    Cb = D * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    k = np.zeros((24, 24))
    area = 0.0
    for xi in _GP:
        for eta in _GP:
            N, dx, dz, dJ = _dN_q4(xi, eta, xz)
            Bm, Bb, _ = _B_q4(N, dx, dz)
            k += dJ * (Bm.T @ Cm @ Bm + Bb.T @ Cb @ Bb)
            area += dJ
    N, dx, dz, dJ = _dN_q4(0.0, 0.0, xz)
    _, _, Bs = _B_q4(N, dx, dz)
    k += 4 * dJ * S * (Bs.T @ Bs)
    m = np.zeros(24)
    mt = pr["rho_h"] * area / 4
    mr = mt * pr["h"] ** 2 / 12
    for i in range(4):
        m[6 * i:6 * i + 3] = mt
        m[6 * i + 3] = m[6 * i + 5] = mr
        m[6 * i + 4] = mr * 1e-3
    return k, np.diag(m)


def shell_q4_resultants(xz, pr, ue):
    """Membrane forces (N/m) and moments (N m/m) at the centre of a general quad."""
    A, D, nu = pr["A"], pr["D"], pr["nu"]
    Cm = A * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    Cb = D * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    N, dx, dz, _ = _dN_q4(0.0, 0.0, np.asarray(xz, float))
    Bm, Bb, _ = _B_q4(N, dx, dz)
    return Cm @ (Bm @ ue), Cb @ (Bb @ ue)


def build_q(cfg):
    """As-designed quarter model. cfg keys (SI, local frame: x aft, y out of the fin plane (+ outboard), z away from
    the wing, so the lower quarter is the mirror image in z):
      tube {x, E, G, od, id, rho, z_clamp (bore end = boss top), z_end (tube end)}, n_free (tube elements between
      the clamp and the first fin LE node), n_ext (tube elements above the fin top), k_root (rx = ry spring at the
      clamp, N m/rad, None = clamped);
      fin {props or None, x_le, x_te, root [(x, z)] skin profile, z_top_le, z_top_te, root_free [(x0, x1)]}, nx, nz;
      station {parts [(m, offset from the station node, J)], k_rock (rx, ry), k_twist (rz), N m/rad, None = rigid};
      the station node sits on the tube axis at the tube end;
      tube_masses [(m, z)], fin_masses [(m, (x, z))];
      struts [{z_attach, ear (dx, dy, dz) from the tube axis at z_attach, anchor (x, y, z), EA, k_anchor}];
      stiffeners [{E, G, A, I_out, J, rho, d}] along the fin top row (edge strips)."""
    tb, fn = cfg["tube"], cfg["fin"]
    x_t = tb["x"]
    r_o, r_i = tb["od"] / 2, tb["id"] / 2
    A_t = math.pi * (r_o ** 2 - r_i ** 2)
    I_t = math.pi / 4 * (r_o ** 4 - r_i ** 4)
    J_t = 2 * I_t
    z0, zend = tb["z_clamp"], tb["z_end"]
    nx, nz = cfg["nx"], cfg["nz"]
    has_fin = fn.get("props") is not None
    grid = {}
    le_z = []
    if has_fin:
        root_x = np.array([p[0] for p in fn["root"]])
        root_z = np.array([p[1] for p in fn["root"]])
        zr = lambda x: float(np.interp(x, root_x, root_z))
        xf = np.linspace(fn["x_le"], fn["x_te"], nx + 1)
        for i, x in enumerate(xf):
            ztop = fn["z_top_le"] + (fn["z_top_te"] - fn["z_top_le"]) * (x - fn["x_le"]) / (fn["x_te"] - fn["x_le"])
            for j in range(nz + 1):
                grid[(i, j)] = (float(x), zr(x) + (ztop - zr(x)) * j / nz)
        le_z = [grid[(0, j)][1] for j in range(nz + 1)]
    above = [z for z in le_z if z > z0 + 1e-4]
    z_first = above[0] if above else min(zend, z0 + 0.03)
    zt = list(np.linspace(z0, z_first, cfg.get("n_free", 2) + 1))
    zt += [z for z in above[1:]]
    if zend > zt[-1] + 1e-4:
        zt += list(np.linspace(zt[-1], zend, cfg.get("n_ext", 2) + 1)[1:])
    for zx in [st["z_attach"] for st in cfg.get("struts", [])] + [z for _, z in cfg.get("tube_masses", [])]:
        if min(abs(zx - z) for z in zt) > 1e-4 and z0 < zx < zend:
            zt.append(zx)                                     # brace collar / lumped mass exactly on a tube node
    zt = sorted(zt)
    nodes = [(x_t, 0.0, float(z)) for z in zt]
    n_tube = len(nodes)
    i_end = n_tube - 1
    fin_id = {}
    for (i, j), (x, z) in sorted(grid.items(), key=lambda t: (t[0][1], t[0][0])):
        fin_id[(i, j)] = len(nodes)
        nodes.append((x, 0.0, z))
    i_station = len(nodes)
    nodes.append((x_t, 0.0, float(zend)))

    def nearest_tube(z):
        return min(range(n_tube), key=lambda n: abs(nodes[n][2] - z))

    strut_nodes = []
    for st in cfg.get("struts", []):
        strut_nodes.append(len(nodes))
        e = st["ear"]
        nodes.append((x_t + e[0], e[1], st["z_attach"] + e[2]))
    nn = len(nodes)
    N = NDOF * nn
    rows, cols, kv, mv = [], [], [], []

    def add(dofs, ke, me):
        for a, da in enumerate(dofs):
            for b, db in enumerate(dofs):
                if ke[a, b] != 0.0 or me[a, b] != 0.0:
                    rows.append(da)
                    cols.append(db)
                    kv.append(ke[a, b])
                    mv.append(me[a, b])

    def dofs_of(*ns):
        return [NDOF * n + d for n in ns for d in range(NDOF)]

    for e in range(n_tube - 1):
        ke, me = frame_element(nodes[e], nodes[e + 1], tb["E"], tb["G"], A_t, I_t, I_t, J_t, tb["rho"])
        add(dofs_of(e, e + 1), ke, me)
    shells = []
    if has_fin:
        for j in range(nz):
            for i in range(nx):
                ns = (fin_id[(i, j)], fin_id[(i + 1, j)], fin_id[(i + 1, j + 1)], fin_id[(i, j + 1)])
                xz = np.array([[nodes[n][0], nodes[n][2]] for n in ns])
                pr = fn["props"]
                db = fn.get("doubler")                      # {props, x1, z0}: thicker board where x < x1, z > z0
                if db and xz[:, 0].mean() < db["x1"] and xz[:, 1].mean() > db["z0"]:
                    pr = db["props"]
                ke, me = shell_q4(xz, pr)
                add(dofs_of(*ns), ke, me)
                shells.append((ns, xz, pr))
    stf_elems = []
    for stf in (cfg.get("stiffeners") or []) if has_fin else []:
        for i in range(nx):
            n1, n2 = fin_id[(i, nz)], fin_id[(i + 1, nz)]
            ke, me = frame_element(nodes[n1], nodes[n2], stf["E"], stf["G"], stf["A"], 1e-15, stf["I_out"],
                                   stf["J"], stf["rho"])
            add(dofs_of(n1, n2), ke, me)
            stf_elems.append((n1, n2, stf))
    stn = cfg["station"]
    Ms = rigid_mass(stn["parts"])
    add(dofs_of(i_station), np.zeros((6, 6)), Ms)
    for m, z in cfg.get("tube_masses", []):
        add(dofs_of(nearest_tube(z)), np.zeros((6, 6)), np.diag([m, m, m, 0, 0, 0]))
    for m, (x, z) in cfg.get("fin_masses", []):
        best = min(fin_id.values(), key=lambda n: (nodes[n][0] - x) ** 2 + (nodes[n][2] - z) ** 2) if has_fin \
            else i_end
        add(dofs_of(best), np.zeros((6, 6)), np.diag([m, m, m, 0, 0, 0]))
    mount_rigid = stn.get("k_rock") is None
    if not mount_rigid:
        kt = 1e8
        kr = np.diag([kt, kt, kt, stn["k_rock"], stn["k_rock"], stn["k_twist"]])
        add(dofs_of(i_end, i_station), np.block([[kr, -kr], [-kr, kr]]), np.zeros((12, 12)))
    strut_info = []
    for st, sn in zip(cfg.get("struts", []), strut_nodes):
        p = np.array(nodes[sn])
        d = np.array(st["anchor"]) - p
        L = float(np.linalg.norm(d))
        n_ = d / L
        k_ax = st["EA"] / L
        k = 1.0 / (1.0 / k_ax + 1.0 / st["k_anchor"]) if st.get("k_anchor") else k_ax
        strut_info.append({"node": sn, "n": n_, "L": L, "k": k, "EA": st["EA"], "master": nearest_tube(st["z_attach"])})
        ke = np.zeros((6, 6))
        ke[:3, :3] = k * np.outer(n_, n_)
        add(dofs_of(sn), ke, np.diag([1e-6] * 3 + [1e-12] * 3))
    if cfg.get("k_root") is not None:
        add(dofs_of(0), np.diag([0, 0, 0, cfg["k_root"], cfg["k_root"], 1e9]), np.zeros((6, 6)))
    K = sp.coo_matrix((kv, (rows, cols)), shape=(N, N)).tocsr()
    M = sp.coo_matrix((mv, (rows, cols)), shape=(N, N)).tocsr()

    fixed = set(dofs_of(0) if cfg.get("k_root") is None else [0, 1, 2])
    slave = {}
    if mount_rigid:
        slave[i_station] = (i_end, np.zeros(3))
    if has_fin:
        free = fn.get("root_free") or []
        for j in range(nz + 1):
            n = fin_id[(0, j)]
            z = nodes[n][2]
            if z <= z0 + 1e-4:
                fixed.update(dofs_of(n))                      # board LE in the boss slot, bonded
            else:
                m = nearest_tube(z)
                slave[n] = (m, np.array(nodes[n]) - np.array(nodes[m]))
        for i in range(1, nx + 1):
            n = fin_id[(i, 0)]
            fixed.add(NDOF * n + 4)
            if not any(a <= nodes[n][0] <= b for a, b in free):
                fixed.update(NDOF * n + d for d in (0, 1, 2))  # root on the skin: pinned
        for (i, j), n in fin_id.items():
            if i > 0 and j > 0:
                fixed.add(NDOF * n + 4)                     # no drilling DOF in the shell
    for si, sn in zip(strut_info, strut_nodes):
        slave[sn] = (si["master"], np.array(nodes[sn]) - np.array(nodes[si["master"]]))
    red = {}
    for n in range(nn):
        if n in slave:
            continue
        for d in range(NDOF):
            g = NDOF * n + d
            if g not in fixed:
                red[g] = len(red)
    Tr, Tc, Tv = [], [], []
    for g, c in red.items():
        Tr.append(g)
        Tc.append(c)
        Tv.append(1.0)
    for n, (mstr, r) in slave.items():
        rx = np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]])
        Tn = np.eye(6)
        Tn[:3, 3:] = -rx
        for a in range(6):
            for b in range(6):
                gm = NDOF * mstr + b
                if Tn[a, b] != 0 and gm in red:
                    Tr.append(NDOF * n + a)
                    Tc.append(red[gm])
                    Tv.append(Tn[a, b])
    T = sp.coo_matrix((Tv, (Tr, Tc)), shape=(N, len(red))).tocsr()
    mdl = Model()
    mdl.__dict__.update(dict(cfg=cfg, nodes=np.array(nodes), K=K, M=M, T=T, Kr=(T.T @ K @ T).tocsc(),
                             Mr=(T.T @ M @ T).tocsc(), i_station=i_station, i_end=i_end, fin_id=fin_id,
                             shells=shells, Ms=Ms, strut_info=strut_info, stf_elems=stf_elems, has_fin=has_fin,
                             n_tube=n_tube, A_t=A_t, I_t=I_t, J_t=J_t, nearest_tube=nearest_tube))
    return mdl
