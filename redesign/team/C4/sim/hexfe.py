"""C4 simulation round: in-house 8-node hexahedron (hex8) linear FE, used beside SU2 on the SAME gmsh mesh.

Library only. SI units. Why it exists: SU2 ELASTICITY solves static linear elasticity only (isotropic materials, no
eigenvalue solver, no rigid ties or springs). This module
  * assembles the same hex8 stiffness SU2 uses (full 2x2x2 Gauss) so the two codes can be compared node for node
    (code verification: identical mesh, materials, clamps and tractions -> identical displacements);
  * adds what SU2 cannot do: orthotropic materials (the CF tube's low shear modulus), rigid ties of node sets to
    6-DOF master nodes (station, tube root, collar), springs (mount rocking, root, brace), lumped and rigid-body
    masses, and a generalised eigenvalue solve for the station modes.
Element: VTK hex ordering (bottom 0-3 counter-clockwise seen from the top, then top 4-7).
"""
import math

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

SG = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
               [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], float)
GP = SG / math.sqrt(3.0)
FACES = np.array([[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]])


# ------------------------------------------------------------------ materials
def d_iso(E, nu):
    lam = E * nu / ((1 + nu) * (1 - 2 * nu))
    mu = E / (2 * (1 + nu))
    D = np.zeros((6, 6))
    D[:3, :3] = lam
    D[np.arange(3), np.arange(3)] += 2 * mu
    D[3:, 3:] = np.eye(3) * mu
    return D


def d_ortho(Ex, Ey, Ez, nuyz, nuxz, nuxy, Gyz, Gxz, Gxy):
    """Orthotropic stiffness, Voigt order (xx, yy, zz, yz, xz, xy); nu_ij = -eps_j / eps_i under sigma_i."""
    S = np.zeros((6, 6))
    S[0, 0], S[1, 1], S[2, 2] = 1 / Ex, 1 / Ey, 1 / Ez
    S[0, 1] = S[1, 0] = -nuxy / Ex
    S[0, 2] = S[2, 0] = -nuxz / Ex
    S[1, 2] = S[2, 1] = -nuyz / Ey
    S[3, 3], S[4, 4], S[5, 5] = 1 / Gyz, 1 / Gxz, 1 / Gxy
    return np.linalg.inv(S)


# ------------------------------------------------------------------ element kernels
def _dN(xi):
    """dN_i/dxi_a, (8, 3), at one natural point."""
    t = 1 + SG * xi
    return 0.125 * np.stack([SG[:, 0] * t[:, 1] * t[:, 2], SG[:, 1] * t[:, 0] * t[:, 2],
                             SG[:, 2] * t[:, 0] * t[:, 1]], axis=1)


def _N(xi):
    return 0.125 * np.prod(1 + SG * xi, axis=1)


def _bmat(dNdx):
    """B (ne, 6, 24) from dN/dx (ne, 8, 3)."""
    ne = dNdx.shape[0]
    B = np.zeros((ne, 6, 24))
    for i in range(8):
        c = 3 * i
        B[:, 0, c] = dNdx[:, i, 0]
        B[:, 1, c + 1] = dNdx[:, i, 1]
        B[:, 2, c + 2] = dNdx[:, i, 2]
        B[:, 3, c + 1] = dNdx[:, i, 2]
        B[:, 3, c + 2] = dNdx[:, i, 1]
        B[:, 4, c] = dNdx[:, i, 2]
        B[:, 4, c + 2] = dNdx[:, i, 0]
        B[:, 5, c] = dNdx[:, i, 1]
        B[:, 5, c + 1] = dNdx[:, i, 0]
    return B


def _jac(X, xi):
    dN = _dN(xi)
    J = np.einsum("ia,eib->eab", dN, X)
    det = np.linalg.det(J)
    inv = np.linalg.inv(J)
    return np.einsum("eab,ib->eia", inv, dN), det


def element_volumes(nodes, hexes):
    X = nodes[hexes]
    return sum(_jac(X, xi)[1] for xi in GP)


def assemble(nodes, hexes, Dmats, mat, rho=None, chunk=20000):
    """Global K (and consistent M when rho per material is given), 3 DOF per node, CSR."""
    nn = len(nodes)
    N = 3 * nn
    K = sp.csr_matrix((N, N))
    M = sp.csr_matrix((N, N)) if rho is not None else None
    Dall = np.asarray(Dmats)
    for s in range(0, len(hexes), chunk):
        H = hexes[s:s + chunk]
        X = nodes[H]
        D = Dall[mat[s:s + chunk]]
        ke = np.zeros((len(H), 24, 24))
        me = np.zeros((len(H), 8, 8)) if rho is not None else None
        for xi in GP:
            dNdx, det = _jac(X, xi)
            if np.any(det <= 0):
                raise ValueError("hexfe.assemble: non-positive Jacobian")
            B = _bmat(dNdx)
            ke += np.einsum("eki,ekl,elj->eij", B, D, B) * det[:, None, None]
            if rho is not None:
                Nv = _N(xi)
                me += np.outer(Nv, Nv)[None] * (np.asarray(rho)[mat[s:s + chunk]] * det)[:, None, None]
        dof = (3 * H[:, :, None] + np.arange(3)[None, None]).reshape(len(H), 24)
        r = np.repeat(dof, 24, axis=1).ravel()
        c = np.tile(dof, (1, 24)).ravel()
        K = K + sp.csr_matrix((ke.ravel(), (r, c)), shape=(N, N))
        if rho is not None:
            me3 = np.zeros((len(H), 24, 24))
            for a in range(3):
                me3[:, a::3, a::3] = me
            M = M + sp.csr_matrix((me3.ravel(), (r, c)), shape=(N, N))
    return K, M


def centroid_stress(nodes, hexes, Dmats, mat, u, sel=None):
    """Stress (Voigt) at the element centroid for the selected elements."""
    idx = np.arange(len(hexes)) if sel is None else np.asarray(sel)
    H = hexes[idx]
    X = nodes[H]
    dNdx, _ = _jac(X, np.zeros(3))
    B = _bmat(dNdx)
    ue = u.reshape(-1, 3)[H].reshape(len(H), 24)
    eps = np.einsum("eij,ej->ei", B, ue)
    D = np.asarray(Dmats)[mat[idx]]
    return np.einsum("eij,ej->ei", D, eps)


def quad_traction_forces(nodes, quads, t_vec):
    """Consistent nodal forces (2x2 Gauss) of a uniform traction t_vec (Pa, 3-vector) on bilinear quads."""
    f = np.zeros(nodes.shape)
    g = 1 / math.sqrt(3)
    S = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], float)
    X = nodes[quads]
    for a, b in ((-g, -g), (g, -g), (g, g), (-g, g)):
        Nq = 0.25 * (1 + S[:, 0] * a) * (1 + S[:, 1] * b)
        dNa = 0.25 * S[:, 0] * (1 + S[:, 1] * b)
        dNb = 0.25 * S[:, 1] * (1 + S[:, 0] * a)
        xa = np.einsum("i,eik->ek", dNa, X)
        xb = np.einsum("i,eik->ek", dNb, X)
        dA = np.linalg.norm(np.cross(xa, xb), axis=1)
        np.add.at(f, quads.ravel(), (Nq[None, :, None] * dA[:, None, None] * np.asarray(t_vec)[None, None, :]
                                     ).reshape(-1, 3))
    return f


def quad_areas_centroids(nodes, quads):
    X = nodes[quads]
    a1 = 0.5 * np.linalg.norm(np.cross(X[:, 1] - X[:, 0], X[:, 2] - X[:, 0]), axis=1)
    a2 = 0.5 * np.linalg.norm(np.cross(X[:, 2] - X[:, 0], X[:, 3] - X[:, 0]), axis=1)
    return a1 + a2, X.mean(axis=1)


def boundary_quads(hexes):
    """Boundary faces (outward VTK orientation), (nf, 4), and the owning element."""
    F = hexes[:, FACES].reshape(-1, 4)
    key = np.sort(F, axis=1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    once = cnt[inv.ravel()] == 1
    owner = np.repeat(np.arange(len(hexes)), 6)
    return F[once], owner[once]


# ------------------------------------------------------------------ constrained model (ties, springs, masses)
def skew(r):
    return np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]])


class Model:
    """Hex nodes (3 DOF) + master nodes (6 DOF). Ties: hex node -> master (rigid offset). Fixed DOFs removed."""

    def __init__(self, nodes, K, M=None):
        self.nodes = np.asarray(nodes, float)
        self.nn = len(nodes)
        self.Kh, self.Mh = K, M
        self.masters = []            # positions
        self.fixed = set()           # full-DOF indices
        self.slave = {}              # hex node -> master index
        self.kblocks = []            # (dofs, k matrix)
        self.mblocks = []            # (dofs, m matrix)

    def add_master(self, xyz):
        self.masters.append(np.asarray(xyz, float))
        return len(self.masters) - 1

    def mdofs(self, m):
        return [3 * self.nn + 6 * m + d for d in range(6)]

    def tie(self, hex_nodes, m):
        for n in hex_nodes:
            self.slave[int(n)] = m

    def fix_nodes(self, hex_nodes):
        for n in hex_nodes:
            self.fixed.update(3 * int(n) + d for d in range(3))

    def fix_master(self, m, comps=range(6)):
        self.fixed.update(self.mdofs(m)[c] for c in comps)

    def spring_ground(self, m, kdiag):
        self.kblocks.append((self.mdofs(m), np.diag(kdiag)))

    def spring_between(self, m1, m2, kdiag):
        k = np.diag(kdiag)
        self.kblocks.append((self.mdofs(m1) + self.mdofs(m2), np.block([[k, -k], [-k, k]])))

    def spring_point_axial(self, m, point, n, k):
        """Axial spring to ground acting at a point rigidly attached to master m, along unit vector n."""
        r = np.asarray(point) - self.masters[m]
        Tp = np.hstack([np.eye(3), -skew(r)])
        kk = k * np.outer(n, n)
        self.kblocks.append((self.mdofs(m), Tp.T @ kk @ Tp))

    def mass_master(self, m, M6):
        self.mblocks.append((self.mdofs(m), np.asarray(M6, float)))

    def point_mass_master(self, m, mass, point):
        r = np.asarray(point) - self.masters[m]
        Tp = np.hstack([np.eye(3), -skew(r)])
        self.mblocks.append((self.mdofs(m), mass * Tp.T @ Tp))

    def build(self):
        nn, nm = self.nn, len(self.masters)
        N = 3 * nn + 6 * nm
        Kx = sp.block_diag([self.Kh, sp.csr_matrix((6 * nm, 6 * nm))]).tocsr() if nm else self.Kh
        rows, cols, vals = [], [], []
        for d, k in self.kblocks:
            for a, da in enumerate(d):
                for b, db in enumerate(d):
                    if k[a, b] != 0:
                        rows.append(da), cols.append(db), vals.append(k[a, b])
        Kx = Kx + sp.csr_matrix((vals, (rows, cols)), shape=(N, N))
        if self.Mh is not None:
            Mx = sp.block_diag([self.Mh, sp.csr_matrix((6 * nm, 6 * nm))]).tocsr() if nm else self.Mh
            rows, cols, vals = [], [], []
            for d, mm in self.mblocks:
                for a, da in enumerate(d):
                    for b, db in enumerate(d):
                        if mm[a, b] != 0:
                            rows.append(da), cols.append(db), vals.append(mm[a, b])
            Mx = Mx + sp.csr_matrix((vals, (rows, cols)), shape=(N, N))
        else:
            Mx = None
        dep = np.zeros(N, bool)
        for n in self.slave:
            dep[3 * n:3 * n + 3] = True
        fixed = np.zeros(N, bool)
        fixed[list(self.fixed)] = True
        indep = np.where(~dep & ~fixed)[0]
        red = -np.ones(N, int)
        red[indep] = np.arange(len(indep))
        Tr, Tc, Tv = list(indep), list(range(len(indep))), [1.0] * len(indep)
        for n, m in self.slave.items():
            Tn = np.hstack([np.eye(3), -skew(self.nodes[n] - self.masters[m])])
            md = self.mdofs(m)
            for a in range(3):
                for b in range(6):
                    if Tn[a, b] != 0 and red[md[b]] >= 0:
                        Tr.append(3 * n + a), Tc.append(red[md[b]]), Tv.append(Tn[a, b])
        T = sp.csr_matrix((Tv, (Tr, Tc)), shape=(N, len(indep)))
        self.N, self.T = N, T
        self.Kr = (T.T @ Kx @ T).tocsc()
        self.Mr = (T.T @ Mx @ T).tocsc() if Mx is not None else None
        self.Kx, self.Mx = Kx, Mx
        return self

    def solve(self, F):
        """F: full-length load vector (hex DOFs then master DOFs). Returns the full displacement vector."""
        ur = spla.spsolve(self.Kr, self.T.T @ F)
        return self.T @ ur

    def modes(self, n=12, shift_hz=30.0):
        sig = (2 * math.pi * shift_hz) ** 2
        v0 = np.ones(self.Kr.shape[0])
        w2, V = spla.eigsh(self.Kr, k=n, M=self.Mr, sigma=sig, which="LM", v0=v0)
        o = np.argsort(w2)
        w2, V = w2[o], V[:, o]
        return np.sqrt(np.abs(w2)) / (2 * math.pi), self.T @ V
