"""mesh_ops.py - STL read/write and the print-prep geometry: weld, islands, watertight test, volume/area, print
orientation, footprint yaw, identity test between variants. numpy only (also importable inside Blender).

Orientation rule (documented in README.md): candidate bed faces are the planes of the mesh that the WHOLE part
rests on (every vertex on one side: a support plane), grouped by normal and offset. Area of mesh faces lying in
each plane is summed; the largest wins (ties within 2 %: the lower resulting height, then the lower index).
shopconfig may force a direction ('down') or restrict the candidate normals to axes ('axes'). The part is then
turned about the vertical so its footprint bounding box is smallest (0.5 deg steps, long side along X) and placed
with its footprint centred on X = Y = 0, Z = 0 on the bed.
"""
import math
import struct

import numpy as np

WELD_MM = 1e-4                    # > float32 noise at 1 m (6e-5 mm), far below any feature


# ----------------------------------------------------------------------------- STL io
def write_stl(path, tris, header=''):
    """Binary STL; header is fixed text (no time stamp) so re-runs are byte-identical."""
    h = ('K09-L shop file: ' + header)[:80].encode('ascii', 'replace').ljust(80, b' ')
    with open(path, 'wb') as f:
        f.write(h)
        f.write(struct.pack('<I', len(tris)))
        for t in tris:
            a, b, c = (np.asarray(p, dtype=float) for p in t)
            n = np.cross(b - a, c - a)
            ln = float(np.linalg.norm(n))
            n = n / ln if ln > 0 else n
            f.write(struct.pack('<12fH', *n, *a, *b, *c, 0))


def read_stl(path):
    """-> (N, 3, 3) float64 triangles (binary or ASCII)."""
    with open(path, 'rb') as f:
        data = f.read()
    if data[:5] == b'solid' and b'facet' in data[:400]:
        vals = [list(map(float, l.split()[1:4])) for l in data.decode('ascii', 'replace').splitlines()
                if l.strip().startswith('vertex')]
        return np.array(vals, dtype=float).reshape(-1, 3, 3)
    n = struct.unpack('<I', data[80:84])[0]
    arr = np.frombuffer(data, dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]), count=n, offset=84)
    return arr['v'].astype(float).reshape(-1, 3, 3)


# ----------------------------------------------------------------------------- topology
def weld(tris, tol=WELD_MM):
    """-> (verts (V,3), faces (F,3) int). Vertices closer than tol merge (grid snap)."""
    pts = tris.reshape(-1, 3)
    key = np.round(pts / tol).astype(np.int64)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    verts = np.zeros((len(uniq), 3))
    np.add.at(verts, inv.ravel(), pts)
    cnt = np.bincount(inv.ravel(), minlength=len(uniq))[:, None]
    verts /= cnt
    faces = inv.reshape(-1, 3)
    faces = faces[(faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])]
    return verts, faces


def islands(faces, nverts):
    """Connected components of faces (shared vertices) -> list of face index arrays, largest first."""
    parent = np.arange(nverts)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for f in faces:
        r0, r1, r2 = find(f[0]), find(f[1]), find(f[2])
        parent[r1] = r0
        parent[find(r2)] = r0
    roots = np.array([find(f[0]) for f in faces])
    out = [np.nonzero(roots == r)[0] for r in np.unique(roots)]
    return sorted(out, key=lambda ix: (-len(ix), int(ix[0])))


def watertight(faces):
    """(ok, n_open_or_nonmanifold_edges, n_misoriented). Closed 2-manifold: each undirected edge in exactly 2 faces,
    and the two uses run in opposite directions."""
    e = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    und = np.sort(e, axis=1)
    _u, cnt = np.unique(und, axis=0, return_counts=True)
    bad = int(np.sum(cnt != 2))
    _d, dcnt = np.unique(e, axis=0, return_counts=True)
    mis = int(np.sum(dcnt > 1))
    return bad == 0 and mis == 0, bad, mis


def volume_area(verts, faces):
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    vol = float(np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6.0)
    area = float(np.linalg.norm(np.cross(b - a, c - a), axis=1).sum() / 2.0)
    return vol, area


def compact(verts, faces):
    used = np.unique(faces)
    remap = -np.ones(len(verts), dtype=np.int64)
    remap[used] = np.arange(len(used))
    return verts[used], remap[faces]


# ----------------------------------------------------------------------------- orientation
def _rot_to(a, b):
    """Rotation matrix taking unit vector a onto unit vector b."""
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    v, c = np.cross(a, b), float(np.dot(a, b))
    if c < -1 + 1e-12:                                   # opposite: turn 180 deg about any perpendicular axis
        p = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
        k = np.cross(a, p)
        k /= np.linalg.norm(k)
        return 2 * np.outer(k, k) - np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx / (1 + c)


def support_planes(verts, faces, tol=0.02):
    """[(area mm2, outward normal n, offset d)] for planes the part rests on (n.v <= d + tol for every vertex)."""
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    cr = np.cross(b - a, c - a)
    ar = np.linalg.norm(cr, axis=1)
    ok = ar > 1e-9
    n = np.zeros_like(cr)
    n[ok] = cr[ok] / ar[ok, None]
    d = np.einsum('ij,ij->i', n, a)
    key = np.concatenate([np.round(n * 2000), np.round(d[:, None] / 0.05)], axis=1).astype(np.int64)
    uk, inv = np.unique(key[ok], axis=0, return_inverse=True)
    areas = np.bincount(inv.ravel(), weights=ar[ok] / 2.0)
    out = []
    idx_ok = np.nonzero(ok)[0]
    for g in np.argsort(-areas, kind='stable'):
        if areas[g] < 1.0:
            break
        members = idx_ok[inv.ravel() == g]
        nn = n[members].mean(axis=0)
        nn /= np.linalg.norm(nn)
        dd = float(np.max(verts @ nn))
        if float(np.mean(d[members])) >= dd - tol:          # nothing sticks out past this plane
            out.append((float(areas[g]), nn, dd))
        if len(out) >= 40:
            break
    return out


def orient(verts, faces, rule=None):
    """-> (R 3x3, note). R maps aircraft-frame mm to bed frame (bed = -Z)."""
    rule = rule or {}
    down = np.array([0, 0, -1.0])
    if 'down' in rule:
        want = np.array(rule['down'], dtype=float)
        want /= np.linalg.norm(want)
        cands = [c for c in support_planes(verts, faces) if np.dot(c[1], want) > math.cos(math.radians(3))]
        n = cands[0][1] if cands else want
        R = _rot_to(n, down)
        note = 'face %s on the bed (shopconfig)' % _axname(want)
        return R, note + ('' if cands else ' - no flat face there, check supports')
    cands = support_planes(verts, faces)
    if 'axes' in rule:
        axes = [np.eye(3)[{'X': 0, 'Y': 1, 'Z': 2}[a]] for a in rule['axes']]
        cands = [c for c in cands if any(abs(np.dot(c[1], ax)) > math.cos(math.radians(3)) for ax in axes)]
    if not cands:
        return np.eye(3), 'as modelled (no support plane found)'
    best = cands[0][0]
    pool = [c for c in cands if c[0] >= 0.98 * best]

    def height(c):
        return float(np.ptp(verts @ c[1]))
    c = min(pool, key=height)
    return _rot_to(c[1], down), 'largest flat face %s on the bed (%.0f mm2)' % (_axname(c[1]), c[0])


def _axname(n):
    n = np.asarray(n, dtype=float)
    k = int(np.argmax(np.abs(n)))
    if abs(n[k]) > 0.999:
        return ('+' if n[k] > 0 else '-') + 'XYZ'[k]
    return '(%.2f %.2f %.2f)' % tuple(n)


def yaw_and_place(verts):
    """Rotate about Z for the smallest footprint box (long side on X), centre XY, Z min = 0. -> (R, t).
    Near-ties (within 0.1 %) go to the smallest angle, so mirror/rotated twins land the same way."""
    xy = verts[:, :2]
    res = []
    for k in range(360):
        a = math.radians(k * 0.5)
        ca, sa = math.cos(a), math.sin(a)
        r = xy @ np.array([[ca, sa], [-sa, ca]])
        w, h = float(np.ptp(r[:, 0])), float(np.ptp(r[:, 1]))
        res.append((w * h, a, w, h))
    m = min(r[0] for r in res)
    _s, a, w, h = next(r for r in res if r[0] <= m * 1.001 + 1e-9)
    a = a + (math.pi / 2 if h > w * 1.0005 else 0.0)
    ca, sa = math.cos(a), math.sin(a)
    R = np.array([[ca, sa, 0], [-sa, ca, 0], [0, 0, 1.0]])
    v = verts @ R.T
    lo, hi = v.min(axis=0), v.max(axis=0)
    t = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    return R, t


def mass_props(verts, faces):
    """Volume, centroid and second-moment covariance (uniform solid) of a closed mesh."""
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    det = np.einsum('ij,ij->i', a, np.cross(b, c))
    V = det.sum() / 6.0
    s = a + b + c
    cen = (det[:, None] * s).sum(axis=0) / 24.0 / V
    M2 = np.einsum('i,ij,ik->jk', det, a, a) + np.einsum('i,ij,ik->jk', det, b, b) +         np.einsum('i,ij,ik->jk', det, c, c) + np.einsum('i,ij,ik->jk', det, s, s)
    M2 = M2 / 120.0 / V
    return abs(V), cen, M2 - np.outer(cen, cen)


def signature(verts, faces):
    """Placed-part descriptor for same_shape(): volume, area, footprint-centred centroid and covariance."""
    V, cen, C = mass_props(verts, faces)
    _v, area = volume_area(verts, faces)
    return {'V': V, 'area': area, 'cen': cen, 'C': C, 'ext': np.ptp(verts, axis=0)}


def same_shape(a, b, tol=0.05):
    """True if b is a quarter-turn (about Z) copy of a. Uses volume, area, extents, centroid and the second-moment
    tensor, so triangulation differences do not matter and a mirror image (centroid / products of inertia change
    sign) is not taken for the same part unless the part is itself symmetric."""
    if abs(a['V'] - b['V']) > 0.003 * a['V'] + 0.5 or abs(a['area'] - b['area']) > 0.003 * a['area'] + 0.5:
        return False
    sc = max(np.abs(a['C']).max(), 1.0)
    for k in range(4):
        q = k * math.pi / 2
        R = np.array([[math.cos(q), -math.sin(q), 0], [math.sin(q), math.cos(q), 0], [0, 0, 1.0]]).round(12)
        ext = np.abs(R) @ b['ext']
        if np.any(np.abs(ext - a['ext']) > tol * 2):
            continue
        if np.all(np.abs(R @ b['cen'] - a['cen']) < tol) and np.all(np.abs(R @ b['C'] @ R.T - a['C']) < 0.002 * sc + 0.01):
            return True
    return False


def overhang_area(verts, faces, max_deg=50.0, bed_tol=0.05):
    """Area (mm2) of down-facing faces steeper than max_deg from vertical that are not on the bed."""
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    cr = np.cross(b - a, c - a)
    ar = np.linalg.norm(cr, axis=1)
    ok = ar > 1e-12
    nz = np.zeros(len(faces))
    nz[ok] = cr[ok, 2] / ar[ok]
    zmin = np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2])
    zmax = np.maximum(np.maximum(a[:, 2], b[:, 2]), c[:, 2])
    on_bed = zmax < bed_tol
    over = (nz < -math.cos(math.radians(90 - max_deg))) & ~on_bed & (zmin > bed_tol)
    return float(ar[over].sum() / 2.0)
