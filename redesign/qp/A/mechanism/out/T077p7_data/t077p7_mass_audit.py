"""T-077 p7 COPY of the p6 audit (unchanged). T-077 p5 COPY of the T-077 audit (selects PETG and Onyx parts; Onyx rho 1.20 g/cm3 (Markforged datasheet via T-080 s1); basis S for CGE-013 / AVN-010 / FIN-005 / CGE-006; CF plates and pins are not printed: mass = analytic area x thickness x 1.6, see t077p5_write_printed_mass.py) of the T-077 re-run of the T-067 printed-part mass audit (unchanged method, output renamed) (R-CAD-05, R-OPT-05). Run: python -I t067_mass_audit.py [h_mm]
Category: geometry arithmetic (CAD solid volume by voxel, 0.25 mm default) + EST print-basis model. Not a simulation.
Reads the CAD through the stub build (same route as sitl/cad_mass.py); edits nothing."""
import os, sys, json, math
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'cad'))
sys.path.insert(0, CAD)
import build_a as b, a_model as m

H = float(sys.argv[1]) * 1e-3 if len(sys.argv) > 1 else 0.25e-3
RHO = 1.27                        # g/cm3, Prusament PETG TDS v1.1 2022-02-16 (ISO 1183), checked 2026-11-19; = wing.py RHO_PETG
LW, LH = 0.42e-3, 0.2e-3          # EST line width / layer height, 0.4 mm nozzle
# print basis classes (EST, see T067_mass_audit.md s3): perimeters, top/bottom layers, infill fraction
BASIS = {'S': dict(per=4, tb=5, infill=0.40),
         'M': dict(per=3, tb=4, infill=0.25),
         'C': dict(per=2, tb=3, infill=0.10)}
if os.environ.get('T067_LEAN'):      # sensitivity: lighter basis (3 perimeters / 4 layers / 25 %, 2 / 3 / 15 %, 2 / 3 / 10 %)
    BASIS = {'S': dict(per=3, tb=4, infill=0.25), 'M': dict(per=2, tb=3, infill=0.15), 'C': dict(per=2, tb=3, infill=0.10)}
TAG = '_lean' if os.environ.get('T067_LEAN') else ''


def klass(pid):
    if pid.startswith(('AVN-010', 'CGE-013', 'FIN-003', 'FIN-005', 'GER-001', 'CGE-001', 'CGE-003', 'CGE-006', 'CGE-007', 'WNG-003', 'WNG-004',
                       'WNG-005', 'MEC-004', 'MEC-008')):
        return 'S'
    if pid.startswith(('AVN-001', 'CGE-008', 'WNG-009', 'WNG-010')):
        return 'M'
    return 'C'     # AVN-008, HRN-003, HRN-004, WNG-008


class MPath:
    def __init__(s, poly):
        s.p = np.asarray(poly, float)

    def contains_points(s, pts):
        x, y = pts[:, 0], pts[:, 1]
        ins = np.zeros(len(pts), bool)
        P = s.p
        n = len(P)
        for i in range(n):
            x1, y1 = P[i]
            x2, y2 = P[(i + 1) % n]
            if y1 == y2:
                continue
            ins ^= ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1)
        return ins


def mesh_inside(sh, P):
    """parity ray cast along +z for a closed mesh (sample points P Nx3)."""
    V = np.asarray(sh.verts, float)
    T = np.asarray(sh.tris, int)
    out = np.zeros(len(P), bool)
    ux = np.unique(P[:, 0])
    uy = np.unique(P[:, 1])
    ny = len(uy)
    ix = np.searchsorted(ux, P[:, 0])
    iy = np.searchsorted(uy, P[:, 1])
    inv = ix * ny + iy                     # full regular grid: column id
    cxy = np.stack([np.repeat(ux, ny), np.tile(uy, len(ux))], 1)
    zhits = [[] for _ in range(len(cxy))]
    for t in T:
        a, bb, c = V[t[0]], V[t[1]], V[t[2]]
        i0, i1 = np.searchsorted(ux, min(a[0], bb[0], c[0])), np.searchsorted(ux, max(a[0], bb[0], c[0]), side='right')
        j0, j1 = np.searchsorted(uy, min(a[1], bb[1], c[1])), np.searchsorted(uy, max(a[1], bb[1], c[1]), side='right')
        if i1 <= i0 or j1 <= j0:
            continue
        sel = (np.arange(i0, i1)[:, None] * ny + np.arange(j0, j1)[None, :]).ravel()
        d = (bb[1] - c[1]) * (a[0] - c[0]) + (c[0] - bb[0]) * (a[1] - c[1])
        if abs(d) < 1e-18:
            continue
        px, py = cxy[sel, 0], cxy[sel, 1]
        l1 = ((bb[1] - c[1]) * (px - c[0]) + (c[0] - bb[0]) * (py - c[1])) / d
        l2 = ((c[1] - a[1]) * (px - c[0]) + (a[0] - c[0]) * (py - c[1])) / d
        l3 = 1 - l1 - l2
        ok = (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
        zz = l1 * a[2] + l2 * bb[2] + l3 * c[2]
        for k, z in zip(sel[ok], zz[ok]):
            zhits[k].append(z)
    z = P[:, 2]
    for ci, zs in enumerate(zhits):
        if len(zs) < 2:
            continue
        zs = np.sort(zs)
        if len(zs) % 2:
            zs = zs[:-1]
        idx = np.where(inv == ci)[0]
        out[idx] = (np.searchsorted(zs, z[idx], side='right') % 2) == 1
    return out


def loft_inside(sh, P):
    k = {'X': 0, 'Y': 1, 'Z': 2}[sh.axis]
    uv = {'X': (1, 2), 'Y': (0, 2), 'Z': (0, 1)}[sh.axis]
    ins = np.zeros(len(P), bool)
    for (o1, l1), (o2, l2) in zip(sh.sections, sh.sections[1:]):
        lo, hi = sorted((o1, o2))
        sel = (P[:, k] >= lo) & (P[:, k] <= hi)
        if not sel.any():
            continue
        idx = np.where(sel)[0]
        zq = np.round(P[idx, k] / 1e-9)
        order = np.argsort(zq, kind='stable')
        idx, zq = idx[order], zq[order]
        cuts = np.flatnonzero(np.diff(zq)) + 1
        for g_idx, g_zq in zip(np.split(idx, cuts), np.split(zq, cuts)):
            z = g_zq[0] * 1e-9
            t = (z - o1) / (o2 - o1) if o2 != o1 else 0.0
            lp = (1 - t) * np.asarray(l1) + t * np.asarray(l2) if len(l1) == len(l2) else np.asarray(l1 if t < 0.5 else l2)
            ins[g_idx] = MPath(lp).contains_points(P[g_idx][:, list(uv)])
    return ins


def inside(sh, P):
    if sh.kind == 'revolve':
        k = {'X': 0, 'Y': 1, 'Z': 2}[sh.axis]
        i, j = [q for q in range(3) if q != k]
        c = sh.center
        a = P[:, k] - c[k]
        rho = np.hypot(P[:, i] - c[i], P[:, j] - c[j])
        return MPath(np.array(sh.profile)).contains_points(np.stack([a, rho], 1))
    if sh.kind == 'prism':
        k = {'X': 0, 'Y': 1, 'Z': 2}[sh.axis]
        uv = {'X': (1, 2), 'Y': (0, 2), 'Z': (0, 1)}[sh.axis]
        lo, hi = sorted((sh.offset, sh.offset + sh.depth))
        mk = (P[:, k] >= lo) & (P[:, k] <= hi)
        ins = np.zeros(len(P), bool)
        for lp in sh.loops:
            ins ^= MPath(np.array(lp)).contains_points(P[:, list(uv)])
        return mk & ins
    if sh.kind == 'loft':
        return loft_inside(sh, P)
    if sh.kind == 'mesh':
        return mesh_inside(sh, P)
    raise ValueError(sh.kind)


def solid_grid(c, h):
    pts = np.array([p for s in c.shapes for p in s.points()])
    lo, hi = pts.min(0) - 2 * h, pts.max(0) + 2 * h
    n = np.ceil((hi - lo) / h).astype(int)
    xs = [lo[i] + (np.arange(n[i]) + 0.5) * h + 1.3e-9 * (i + 1) for i in range(3)]     # tiny offsets avoid exact-edge ties
    X, Y, Z = np.meshgrid(*xs, indexing='ij')
    P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    ins = np.zeros(len(P), bool)
    for s in c.shapes:
        ins |= inside(s, P)
    Mc = np.array(c.matrix())
    for s, mat, nm, shop in c.cuts:
        if mat is None:
            ins &= ~inside(s, P)
        else:
            T = np.linalg.inv(np.array(mat)) @ Mc
            ins &= ~inside(s, (T[:3, :3] @ P.T).T + T[:3, 3])
    return ins.reshape(n), lo


def shell_model(S, h, cls, axis_z):
    """S solid bool grid; axis_z = grid axis used as the layer direction. Returns solid, shell and core voxel counts."""
    S = np.moveaxis(S, axis_z, 2)
    B = BASIS[cls]
    wp = B['per'] * LW
    tb = int(round(B['tb'] * LH / h))
    d = ndi.distance_transform_edt(np.pad(S, 1), sampling=(h, h, 1e3))[1:-1, 1:-1, 1:-1]   # per-layer 2-D distance to the nearest void
    st = np.ones((1, 1, 2 * tb + 1), bool)
    ez = ndi.binary_erosion(np.pad(S, ((0, 0), (0, 0), (tb + 1, tb + 1))), structure=st)[:, :, tb + 1:-(tb + 1)]
    core = S & ez & (d > wp)
    return int(S.sum()), int(S.sum() - core.sum()), int(core.sum())


if __name__ == '__main__':
    ctx, _, res = b.build_all.build(b.StubBackend(), b.MODEL, os.path.join(b.MODEL, 'modules.txt'), log=lambda *a: None)
    only = sys.argv[2:] if len(sys.argv) > 2 else None
    rows = []
    for pid, p in m.PARTS.items():
        if not ((('PETG' in p['material'] and 'lead' not in p['material']) or 'Onyx' in p['material'])):
            continue
        if only and not any(pid.startswith(o) for o in only):
            continue
        c = ctx.components[pid]
        S, lo = solid_grid(c, H)
        occ = [np.ptp(np.where(S.any(axis=tuple(q for q in range(3) if q != a)))[0]) + 1 for a in range(3)]
        az = int(np.argmin(occ))          # build axis = smallest occupied extent (flat on the bed), EST
        cls = klass(pid)
        nS, nShell, nCore = shell_model(S, H, cls, az)
        v = nS * H ** 3 * 1e6
        B = BASIS[cls]
        rows.append(dict(id=pid, listed_g=p['mass_g'], vol_cm3=v, solid_g=v * (1.20 if 'Onyx' in p['material'] else RHO), cls=cls, build_axis='xyz'[az],
                         core_frac=nCore / max(nS, 1), computed_g=(nShell + B['infill'] * nCore) * H ** 3 * 1e6 * (1.20 if 'Onyx' in p['material'] else RHO),
                         name=p['name'][:70], material=p['material']))
        r = rows[-1]
        print(f"{pid:12s} listed {r['listed_g']:6.2f}  solid {r['solid_g']:6.2f}  basis {cls}  computed {r['computed_g']:6.2f}  core {r['core_frac']:.2f}", flush=True)
    tag = TAG + ('_only' if only else '')
    json.dump(dict(h_mm=H * 1e3, rho=RHO, rows=rows), open(os.path.join(HERE, 't077_rows_h%.2f%s.json' % (H * 1e3, tag)), 'w'), indent=1)
