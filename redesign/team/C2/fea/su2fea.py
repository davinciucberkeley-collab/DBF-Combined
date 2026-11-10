"""Small FEA toolkit for C2: a 2-D section mesh (gmsh) extruded along the span into prisms and hexahedra,
written as an SU2 mesh + element-property file, solved with SU2_CFD (SOLVER= ELASTICITY, linear elastic, small
deformations, multi-material through FEA_FILENAME), and post-processed in NumPy (element-centroid strain and
stress, which avoids SU2's nodal stress averaging across the CF / foam interface).

Conventions: aircraft frame (params.json#frame): x aft, y right (span), z up, metres. The section lives in the
x-z plane and is extruded along +y. Element node order is VTK (SU2): wedge 13 = (bottom tri, top tri),
hexahedron 12 = (bottom quad, top quad), each bottom face ordered so its right-hand normal points to the top face.
"""
import math
import os
import subprocess
from pathlib import Path

import numpy as np

SU2 = Path("C:/Users/dillo/tools/su2/bin/bin/SU2_CFD.exe")
VTK_TRI, VTK_QUAD, VTK_WEDGE, VTK_HEX = 5, 9, 13, 12


# ------------------------------------------------------------------------------------------------ 2-D section
def section_mesh(outline, cuts, circles, n_theta, n_rad, h_near, h_far, dist=(0.002, 0.04), extra_lines=()):
    """Mesh a closed outline (polyline, x-z) partitioned by straight cut lines, with concentric circles round one
    centre structured as quads (n_theta around, n_rad layers between consecutive circles; the innermost disk is
    triangulated). Returns nodes (N, 2), list of (vtk_type, conn ndarray) 2-D elements, and the set of node ids
    lying on the outline.
    outline : (M, 2) closed polyline (first point not repeated)
    cuts    : list of ((x0, z0), (x1, z1)) segments; they may overhang the outline (the overhang is dropped)
    circles : (xc, zc, [r_0 < r_1 < ...]); r_0 is the inner disk, the ring r_{k} .. r_{k+1} is structured
    """
    import gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("sec")
    occ = gmsh.model.occ
    outline = np.asarray(outline, float)
    x_, z_ = outline[:, 0], outline[:, 1]
    if 0.5 * (x_ * np.roll(z_, -1) - np.roll(x_, -1) * z_).sum() < 0:
        outline = outline[::-1]                           # counter-clockwise, or OCC builds an empty face
    pts = [occ.addPoint(x, z, 0) for x, z in outline]
    lines = [occ.addLine(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    face = occ.addPlaneSurface([occ.addWire(lines)])      # addCurveLoop rejects the 160-point S5010 loop
    xc, zc, radii = circles
    disks = [occ.addDisk(xc, zc, 0, r, r) for r in radii]
    cut_lines = []
    for (a, b_) in list(cuts) + list(extra_lines):
        p0, p1 = occ.addPoint(a[0], a[1], 0), occ.addPoint(b_[0], b_[1], 0)
        cut_lines.append(occ.addLine(p0, p1))
    occ.fragment([(2, face)], [(2, d) for d in disks] + [(1, l_) for l_ in cut_lines])
    occ.synchronize()
    # transfinite circles (same start angle, same count -> aligned nodes)
    circ_tags = {}
    for dim, tag in gmsh.model.getEntities(1):
        bb = gmsh.model.getBoundingBox(1, tag)
        w = bb[3] - bb[0]
        for r in radii:
            cxb, czb = 0.5 * (bb[0] + bb[3]), 0.5 * (bb[1] + bb[4])
            if abs(w - 2 * r) < 5e-5 and abs(bb[4] - bb[1] - 2 * r) < 5e-5 and abs(cxb - xc) < 5e-5 and abs(czb - zc) < 5e-5:
                circ_tags[r] = tag
    for r, t in circ_tags.items():
        gmsh.model.mesh.setTransfiniteCurve(t, n_theta + 1)
    f1 = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(f1, "CurvesList", [circ_tags[radii[-1]]])
    f2 = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(f2, "InField", f1)
    gmsh.model.mesh.field.setNumber(f2, "SizeMin", h_near)
    gmsh.model.mesh.field.setNumber(f2, "SizeMax", h_far)
    gmsh.model.mesh.field.setNumber(f2, "DistMin", dist[0])
    gmsh.model.mesh.field.setNumber(f2, "DistMax", dist[1])
    gmsh.model.mesh.field.setAsBackgroundMesh(f2)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.MeshSizeMax", h_far)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.model.mesh.generate(2)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    xyz = xyz.reshape(-1, 3)[:, :2]
    tmap = {int(t): i for i, t in enumerate(tags)}
    # circle nodes, sorted by angle
    ring_nodes = {}
    for r, t in circ_tags.items():
        nt, nx, _ = gmsh.model.mesh.getNodes(1, t, includeBoundary=True)
        ids = np.array([tmap[int(v)] for v in nt])
        ang = np.mod(np.arctan2(xyz[ids, 1] - zc, xyz[ids, 0] - xc) + 1e-7, 2 * np.pi) - 1e-7
        o = np.argsort(ang)
        ids, ang = ids[o], ang[o]
        keep = np.concatenate([[True], np.diff(ang) > 1e-9])
        ring_nodes[r] = (ids[keep], ang[keep])
    # 2-D triangles outside the structured rings and inside the inner disk
    tris = []
    for dim, tag in gmsh.model.getEntities(2):
        et, _, en = gmsh.model.mesh.getElements(2, tag)
        for t_, n_ in zip(et, en):
            if t_ != 2:
                continue
            conn = np.array([tmap[int(v)] for v in n_]).reshape(-1, 3)
            cen = xyz[conn].mean(1)
            rr = np.hypot(cen[:, 0] - xc, cen[:, 1] - zc)
            keep = (rr < radii[0]) | (rr > radii[-1])
            tris.append(conn[keep])
    gmsh.finalize()
    tris = np.vstack(tris)
    nodes = [xyz]
    nn = len(xyz)
    quads = []
    for k in range(len(radii) - 1):
        ri, ro = radii[k], radii[k + 1]
        ii, ai = ring_nodes[ri]
        io, ao = ring_nodes[ro]
        if not (len(ii) == len(io) == n_theta and np.allclose(ai, ao, atol=1e-6)):
            raise AssertionError(f"circle nodes not aligned: {len(ii)} {len(io)} {n_theta} "
                                 f"{np.degrees(ai[:4])} {np.degrees(ao[:4])}")
        layers = [ii]
        for j in range(1, n_rad):
            rj = ri + (ro - ri) * j / n_rad
            new = np.stack([xc + rj * np.cos(ai), zc + rj * np.sin(ai)], 1)
            nodes.append(new)
            layers.append(np.arange(nn, nn + n_theta))
            nn += n_theta
        layers.append(io)
        for j in range(n_rad):
            a_, b2 = layers[j], layers[j + 1]
            for m in range(n_theta):
                m2 = (m + 1) % n_theta
                quads.append([a_[m], a_[m2], b2[m2], b2[m]])
    nodes = np.vstack(nodes)
    # orient every 2-D element counter-clockwise in (x, z)
    def ccw(conn):
        p = nodes[conn]
        x, z = p[..., 0], p[..., 1]
        area = 0.5 * (x * np.roll(z, -1, 1) - np.roll(x, -1, 1) * z).sum(1)
        conn = conn.copy()
        conn[area < 0] = conn[area < 0][:, ::-1]
        return conn
    elems = [(VTK_TRI, ccw(tris)), (VTK_QUAD, ccw(np.array(quads, dtype=int)))]
    on_outline = nodes_on_polyline(nodes, outline)
    return nodes, elems, on_outline


def nodes_on_polyline(nodes, poly, tol=1e-7):
    P = np.asarray(poly)
    Q = np.roll(P, -1, 0)
    d = np.full(len(nodes), np.inf)
    for a, b_ in zip(P, Q):
        ab = b_ - a
        t = np.clip(((nodes - a) @ ab) / (ab @ ab), 0, 1)
        d = np.minimum(d, np.linalg.norm(nodes - (a + t[:, None] * ab), axis=1))
    return d < tol


# ------------------------------------------------------------------------------------------------ extrusion
def extrude(nodes2d, elems2d, ys, mat_fn):
    """Extrude along +y through the layer coordinates ys. mat_fn(x, z, y) -> material index or None (void),
    evaluated at each 2-D element centroid and layer mid-plane. Returns nodes (N, 3), elements [(vtk, conn, mat)].
    The (x, z) -> (x, y, z) map: with the 2-D element counter-clockwise in (x, z), its normal is -y, so the bottom
    face is reversed to point its normal at the top face (+y)."""
    n2 = len(nodes2d)
    nl = len(ys)
    X = np.zeros((n2 * nl, 3))
    for k, y in enumerate(ys):
        X[k * n2:(k + 1) * n2, 0] = nodes2d[:, 0]
        X[k * n2:(k + 1) * n2, 1] = y
        X[k * n2:(k + 1) * n2, 2] = nodes2d[:, 1]
    out = []
    for vtk2, conn in elems2d:
        cen = nodes2d[conn].mean(1)
        # VTK: hexahedron base (0-3) normal points to the top face; wedge base (0-2) normal points away from it.
        # Counter-clockwise in (x, z) has normal -y (x cross z = -y), i.e. away from the next layer.
        bot = conn[:, ::-1] if vtk2 == VTK_QUAD else conn
        for k in range(nl - 1):
            ym = 0.5 * (ys[k] + ys[k + 1])
            mats = np.array([(-1 if (m := mat_fn(cx, cz, ym)) is None else m) for cx, cz in cen])
            sel = mats >= 0
            if not sel.any():
                continue
            b0 = bot[sel] + k * n2
            t0 = bot[sel] + (k + 1) * n2
            vtk3 = VTK_WEDGE if vtk2 == VTK_TRI else VTK_HEX
            out.append((vtk3, np.hstack([b0, t0]), mats[sel]))
    types = np.concatenate([np.full(len(c), v) for v, c, _ in out])
    mats = np.concatenate([m for _, _, m in out])
    return X, out, types, mats


def compact(X, blocks):
    used = np.unique(np.concatenate([c.ravel() for _, c, _ in blocks]))
    remap = -np.ones(len(X), dtype=int)
    remap[used] = np.arange(len(used))
    return X[used], [(v, remap[c], m) for v, c, m in blocks], used


def element_volumes(X, blocks):
    vols = []
    for vtk, conn, _ in blocks:
        p = X[conn]
        if vtk == VTK_HEX:
            d = p[:, [6]] - p[:, [0]]
            v = (np.einsum("ij,ij->i", (p[:, 1] - p[:, 0]), np.cross(p[:, 3] - p[:, 0], p[:, 4] - p[:, 0])))
        else:
            v = np.einsum("ij,ij->i", (p[:, 1] - p[:, 0]), np.cross(p[:, 2] - p[:, 0], p[:, 3] - p[:, 0])) / 2
        vols.append(v)
    return np.concatenate(vols)


def boundary_faces(blocks):
    """All element faces that belong to exactly one element: list of (vtk_face_type, node tuple)."""
    faces = {}
    for vtk, conn, _ in blocks:
        if vtk == VTK_WEDGE:
            fl = [((0, 2, 1), VTK_TRI), ((3, 4, 5), VTK_TRI), ((0, 1, 4, 3), VTK_QUAD), ((1, 2, 5, 4), VTK_QUAD),
                  ((2, 0, 3, 5), VTK_QUAD)]
        else:
            fl = [((0, 3, 2, 1), VTK_QUAD), ((4, 5, 6, 7), VTK_QUAD), ((0, 1, 5, 4), VTK_QUAD),
                  ((1, 2, 6, 5), VTK_QUAD), ((2, 3, 7, 6), VTK_QUAD), ((3, 0, 4, 7), VTK_QUAD)]
        for loc, ft in fl:
            f = conn[:, list(loc)]
            for row in f:
                key = tuple(sorted(row.tolist()))
                if key in faces:
                    faces[key] = None
                else:
                    faces[key] = (ft, tuple(row.tolist()))
    return [v for v in faces.values() if v is not None]


# ------------------------------------------------------------------------------------------------ SU2 I/O
def write_su2(path, X, blocks, markers):
    with open(path, "w") as f:
        f.write("NDIME= 3\n")
        ne = sum(len(c) for _, c, _ in blocks)
        f.write(f"NELEM= {ne}\n")
        e = 0
        lines = []
        for vtk, conn, _ in blocks:
            for row in conn:
                lines.append(f"{vtk} " + " ".join(map(str, row)) + f" {e}\n")
                e += 1
        f.writelines(lines)
        f.write(f"NPOIN= {len(X)}\n")
        f.writelines(f"{p[0]:.10e} {p[1]:.10e} {p[2]:.10e} {i}\n" for i, p in enumerate(X))
        f.write(f"NMARK= {len(markers)}\n")
        for name, fl in markers.items():
            f.write(f"MARKER_TAG= {name}\nMARKER_ELEMS= {len(fl)}\n")
            f.writelines(f"{ft} " + " ".join(map(str, nd)) + "\n" for ft, nd in fl)


def write_props(path, blocks):
    mats = np.concatenate([m for _, _, m in blocks])
    with open(path, "w") as f:
        f.write("ID MAT EL DEN DV\n")
        f.writelines(f"{i} {m} 0 {m} 0\n" for i, m in enumerate(mats))


def write_cfg(path, mesh, props, E, nu, clamped, loads, restart="restart.csv", tol=1e-8, iters=80000, prec="LU_SGS"):
    """loads: list of (marker, tx, ty, tz) tractions in Pa.
    Preconditioner LU_SGS: SU2 8.5's ILU diverges on these meshes (tube test 2026-11-10: CG+ILU(0) and ILU(2)
    residual grows, w_tip ~ 0 after 40 000 iterations; CG+LU_SGS reaches 1e-8 in 2 830 iterations and matches the
    direct solve). Always check linsol_info() for the final residual."""
    # SU2's parser splits on ':' and reads '\' as a continuation: use paths relative to the run folder
    here = Path(path).resolve().parent
    mesh = Path(os.path.relpath(Path(mesh).resolve(), here)).as_posix()
    props = Path(os.path.relpath(Path(props).resolve(), here)).as_posix()
    mk = []
    for name, tx, ty, tz in loads:
        mag = math.sqrt(tx * tx + ty * ty + tz * tz)
        if mag == 0:
            mk.append(f"{name}, 1.0, 0.0, 0.0, 0.0, 1.0")
        else:
            mk.append(f"{name}, 1.0, {mag:.9e}, {tx / mag:.9f}, {ty / mag:.9f}, {tz / mag:.9f}")
    txt = f"""SOLVER= ELASTICITY
MATH_PROBLEM= DIRECT
GEOMETRIC_CONDITIONS= SMALL_DEFORMATIONS
MATERIAL_MODEL= LINEAR_ELASTIC
ELASTICITY_MODULUS= ({', '.join(f'{v:.6e}' for v in E)})
POISSON_RATIO= ({', '.join(f'{v:.4f}' for v in nu)})
MATERIAL_DENSITY= ({', '.join('1000.0' for _ in E)})
MATERIAL_THERMAL_EXPANSION_COEFF= ({', '.join('0.0' for _ in E)})
FEA_FILENAME= {props}
MARKER_CLAMPED= ( {', '.join(clamped)} )
MARKER_LOAD= ( {', '.join(mk)} )
INNER_ITER= 1
LINEAR_SOLVER= CONJUGATE_GRADIENT
LINEAR_SOLVER_PREC= {prec}
LINEAR_SOLVER_ERROR= {tol:.1e}
LINEAR_SOLVER_ITER= {iters}
MESH_FILENAME= {mesh}
MESH_FORMAT= SU2
OUTPUT_FILES= (RESTART_ASCII)
RESTART_FILENAME= {restart}
VOLUME_OUTPUT= (COORDINATES, SOLUTION)
SCREEN_OUTPUT= (INNER_ITER, LINSOL_ITER, LINSOL_RESIDUAL, VMS)
CONV_FIELD= RMS_UTOL
"""
    Path(path).write_text(txt)


def run_su2(cfg, cwd, log="su2.log", threads=None):
    env = dict(os.environ)
    if threads:
        env["OMP_NUM_THREADS"] = str(threads)
    with open(Path(cwd) / log, "w") as f:
        # one OpenMP thread per process: this SU2 8.5 Windows build stalls in the FEA solver with the default
        # thread count (seen 2026-11-10); parallelism comes from running load cases side by side instead
        r = subprocess.run([str(SU2), "-t", str(threads or 1), Path(cfg).name], cwd=cwd, stdout=f,
                           stderr=subprocess.STDOUT, env=env)
    txt = (Path(cwd) / log).read_text(errors="ignore")
    if r.returncode != 0 or "Exit Success" not in txt:
        raise RuntimeError(f"SU2 failed in {cwd}: see {log}\n" + txt[-1500:])
    return txt


def linsol_info(txt):
    """Last linear-solver iteration count and residual from the SU2 screen output, if printed."""
    rows = [l_ for l_ in txt.splitlines() if l_.strip().startswith("|") and l_.count("|") >= 4]
    for l_ in reversed(rows):
        parts = [p.strip() for p in l_.strip().strip("|").split("|")]
        try:
            return {"iter": int(float(parts[1])), "resid_log10": float(parts[2])}
        except (ValueError, IndexError):
            continue
    return {}


def read_restart(path, n):
    import csv
    with open(path) as f:
        r = csv.reader(f)
        h = [x.strip().strip('"') for x in next(r)]
        a = np.array([[float(v) for v in row] for row in r])
    ids = a[:, h.index("PointID")].astype(int)
    U = np.zeros((n, 3))
    U[ids] = a[:, [h.index("Displacement_x"), h.index("Displacement_y"), h.index("Displacement_z")]]
    return U


# ------------------------------------------------------------------------------------------------ post-processing
def _dN_centroid(vtk):
    if vtk == VTK_HEX:
        s = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                      [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], float)
        return s / 8.0                                          # dN/dxi at xi = 0
    # wedge: N = L_i(r, s) (1 -/+ t)/2, at r = s = 1/3, t = 0
    dN = np.zeros((6, 3))
    dL = np.array([[-1, -1], [1, 0], [0, 1]], float)
    for i in range(3):
        dN[i, :2] = dL[i] * 0.5
        dN[i + 3, :2] = dL[i] * 0.5
        dN[i, 2] = -(1 / 3) * 0.5
        dN[i + 3, 2] = (1 / 3) * 0.5
    return dN


def centroid_strain(X, U, vtk, conn):
    """Small-strain tensor (n, 3, 3) at the element centroid."""
    dNdxi = _dN_centroid(vtk)
    P = X[conn]                                   # (n, a, 3)
    J = np.einsum("nai,aj->nij", P, dNdxi)        # dx_i / dxi_j
    Jinv = np.linalg.inv(J)
    dNdx = np.einsum("aj,nji->nai", dNdxi, Jinv)
    G = np.einsum("nai,naj->nij", U[conn], dNdx)  # du_i / dx_j
    return 0.5 * (G + np.transpose(G, (0, 2, 1)))


def hooke(eps, E, nu):
    if isinstance(E, dict):            # tube: axial stress governs; isotropic recovery with the axial modulus
        E, nu = E["Ea"], E["nu_at"]
    lam = E * nu / ((1 + nu) * (1 - 2 * nu))
    mu = E / (2 * (1 + nu))
    tr = np.trace(eps, axis1=1, axis2=2)
    return lam * tr[:, None, None] * np.eye(3) + 2 * mu * eps


# ------------------------------------------------------------------------------------------------ direct solver
# Same discretisation as SU2's FEA solver (linear hexahedra 2x2x2 Gauss, linear wedges 3 x 2 Gauss, isotropic
# linear elasticity, clamped markers, uniform traction markers), assembled in SciPy and solved with SuperLU.
# Used for the levels where SU2's Krylov solvers do not converge in reasonable time (see SIMULATION-REPORT.md).
def _gauss(vtk):
    if vtk == VTK_HEX:
        a = 1 / math.sqrt(3)
        pts = np.array([[i, j, k] for k in (-a, a) for j in (-a, a) for i in (-a, a)])
        return pts, np.ones(8)
    tri = np.array([[1 / 6, 1 / 6], [2 / 3, 1 / 6], [1 / 6, 2 / 3]])
    a = 1 / math.sqrt(3)
    pts = np.array([[r, s, t] for t in (-a, a) for r, s in tri])
    return pts, np.full(6, 1 / 6)


def _dN(vtk, p):
    r, s, t = p
    if vtk == VTK_HEX:
        sg = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                       [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], float)
        d = np.zeros((8, 3))
        for a_ in range(8):
            xr, xs_, xt = sg[a_]
            d[a_] = [xr * (1 + xs_ * s) * (1 + xt * t) / 8, xs_ * (1 + xr * r) * (1 + xt * t) / 8,
                     xt * (1 + xr * r) * (1 + xs_ * s) / 8]
        return d
    L = [1 - r - s, r, s]
    dL = [(-1, -1), (1, 0), (0, 1)]
    d = np.zeros((6, 3))
    for i in range(3):
        d[i] = [dL[i][0] * (1 - t) / 2, dL[i][1] * (1 - t) / 2, -L[i] / 2]
        d[i + 3] = [dL[i][0] * (1 + t) / 2, dL[i][1] * (1 + t) / 2, L[i] / 2]
    return d


def _Dmat(E, nu):
    lam = E * nu / ((1 + nu) * (1 - 2 * nu))
    mu = E / (2 * (1 + nu))
    D = np.zeros((6, 6))
    D[:3, :3] = lam
    D[np.arange(3), np.arange(3)] += 2 * mu
    D[3:, 3:] = np.eye(3) * mu
    return D


VOIGT = [(0, 0), (1, 1), (2, 2), (0, 1), (1, 2), (2, 0)]   # same order as the B rows below (engineering shear)


def tube_D(cen, mat):
    """Element stiffness (n, 6, 6) of a roll-wrapped tube along +y, transversely isotropic about its own axis:
    mat = {"Ea", "Et", "Gat", "nu_at", "nu_tt", "center": (xc, zc)}. Local axes 1 = axial (y), 2 = hoop, 3 = radial,
    taken at each element centroid, rotated to the global frame as a 4th-order tensor."""
    Ea, Et, Gat, nat, ntt = mat["Ea"], mat["Et"], mat["Gat"], mat["nu_at"], mat["nu_tt"]
    S = np.zeros((6, 6))
    S[:3, :3] = [[1 / Ea, -nat / Ea, -nat / Ea], [-nat / Ea, 1 / Et, -ntt / Et], [-nat / Ea, -ntt / Et, 1 / Et]]
    S[3, 3], S[4, 4], S[5, 5] = 1 / Gat, 2 * (1 + ntt) / Et, 1 / Gat     # 12 axial-hoop, 23 hoop-radial, 31 radial-axial
    C = np.linalg.inv(S)
    c = np.zeros((3, 3, 3, 3))
    for I, (i, j) in enumerate(VOIGT):
        for J, (k, l) in enumerate(VOIGT):
            for a, b_ in ((i, j), (j, i)):
                for cc, d in ((k, l), (l, k)):
                    c[a, b_, cc, d] = C[I, J]
    xc, zc = mat["center"]
    dx, dz = cen[:, 0] - xc, cen[:, 2] - zc
    r = np.hypot(dx, dz)
    er = np.stack([dx / r, np.zeros_like(r), dz / r], 1)
    ey = np.tile([0.0, 1.0, 0.0], (len(r), 1))
    eh = np.cross(ey, er)
    R = np.stack([ey, eh, er], 1)                 # R[n, local, global]
    cg = np.einsum("npi,nqj,nrk,nsl,pqrs->nijkl", R, R, R, R, c, optimize=True)
    D = np.empty((len(r), 6, 6))
    for I, (i, j) in enumerate(VOIGT):
        for J, (k, l) in enumerate(VOIGT):
            D[:, I, J] = cg[:, i, j, k, l]
    return D


def assemble(X, blocks, E, nu):
    """E[m] is a Young's modulus (isotropic with nu[m]) or a tube_D material dict."""
    import scipy.sparse as sp
    K = None
    for vtk, conn, mats in blocks:
        na = conn.shape[1]
        pts, wts = _gauss(vtk)
        P = X[conn]
        chunks = []
        for m in np.unique(mats):
            idx = np.where(mats == m)[0]
            chunks.extend((m, idx[i:i + 60000]) for i in range(0, len(idx), 60000))
        for m, sel in chunks:
            Pm, cm = P[sel], conn[sel]
            if isinstance(E[m], dict):
                D = tube_D(Pm.mean(1), E[m])
            else:
                D = np.broadcast_to(_Dmat(E[m], nu[m]), (len(cm), 6, 6))
            Ke = np.zeros((len(cm), 3 * na, 3 * na))
            for p, w in zip(pts, wts):
                dN = _dN(vtk, p)
                J = np.einsum("nai,aj->nij", Pm, dN)
                det = np.abs(np.linalg.det(J))
                dNdx = np.einsum("aj,nji->nai", dN, np.linalg.inv(J))
                B = np.zeros((len(cm), 6, 3 * na))
                B[:, 0, 0::3] = dNdx[:, :, 0]
                B[:, 1, 1::3] = dNdx[:, :, 1]
                B[:, 2, 2::3] = dNdx[:, :, 2]
                B[:, 3, 0::3] = dNdx[:, :, 1]
                B[:, 3, 1::3] = dNdx[:, :, 0]
                B[:, 4, 1::3] = dNdx[:, :, 2]
                B[:, 4, 2::3] = dNdx[:, :, 1]
                B[:, 5, 0::3] = dNdx[:, :, 2]
                B[:, 5, 2::3] = dNdx[:, :, 0]
                Ke += np.einsum("nki,nkl,nlj->nij", B, D, B, optimize=True) * (w * det)[:, None, None]
            dof = (3 * cm[:, :, None] + np.arange(3)).reshape(len(cm), -1).astype(np.int32)
            # sum each chunk into CSR at once: keeps the peak memory to one chunk's COO triplets (level 3: 1.3 M dofs)
            part = sp.csr_matrix((Ke.ravel(), (np.repeat(dof, 3 * na, 1).ravel(), np.tile(dof, (1, 3 * na)).ravel())),
                                 shape=(3 * len(X), 3 * len(X)))
            del Ke
            K = part if K is None else K + part
    return K.tocsr()


def traction_vector(X, markers, loads):
    f = np.zeros(3 * len(X))
    a = 1 / math.sqrt(3)
    for name, tx, ty, tz in loads:
        t = np.array([tx, ty, tz])
        for ft, nd in markers.get(name, []):
            P = X[list(nd)]
            if ft == VTK_TRI:
                A = 0.5 * np.linalg.norm(np.cross(P[1] - P[0], P[2] - P[0]))
                w = np.full(3, A / 3)
            else:
                w = np.zeros(4)
                for r in (-a, a):
                    for s in (-a, a):
                        N = np.array([(1 - r) * (1 - s), (1 + r) * (1 - s), (1 + r) * (1 + s), (1 - r) * (1 + s)]) / 4
                        dr = np.array([-(1 - s), (1 - s), (1 + s), -(1 + s)]) / 4
                        ds = np.array([-(1 - r), -(1 + r), (1 + r), (1 - r)]) / 4
                        w += N * np.linalg.norm(np.cross(dr @ P, ds @ P))
            for k, node in enumerate(nd):
                f[3 * node:3 * node + 3] += w[k] * t
    return f


def solve_direct(K, f, fixed_nodes):
    import scipy.sparse.linalg as spla
    n = K.shape[0]
    fixed = np.zeros(n, bool)
    for node in fixed_nodes:
        fixed[3 * node:3 * node + 3] = True
    free = ~fixed
    Kff = K[free][:, free].tocsc()
    lu = spla.splu(Kff, permc_spec="MMD_AT_PLUS_A")
    return lu, free


def apply_lu(lu, free, f):
    u = np.zeros(len(f))
    u[free] = lu.solve(f[free])
    return u.reshape(-1, 3)
