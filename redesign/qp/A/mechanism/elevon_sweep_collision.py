"""T-020 swept collision through the elevon linkage motion (category: interference during motion), ANALYTIC geometry.
    python -I redesign/qp/A/mechanism/elevon_sweep_collision.py        (about 1 min)
WHY ANALYTIC: no triangle mesh of the linkage parts exists without a build. The CAD is built on the stub backend (no geometry) and the
collision checker runs inside Blender (collide_a.py -> a_collide_blender.py, `bpy`), which is not part of this environment; trimesh and
manifold3d are not installed (checked: ModuleNotFoundError). So the parts are rebuilt here from the SAME CAD constants and drawing calls
(amodel/electrical.py:944-978, wing.py, common.py) as convex solids (arm hull, circle polygons of 32 sides circumscribed on the true
radius, boxes, rounded-rectangle prism) and posed at every step of the T-018 solution (delta every 0.5 deg over +-21 deg, both sides, theta from
the closed form). Convex-convex separation / penetration = separating-axis test over all face normals and edge-edge axes (exact for
penetration depth of convex polytopes; for separated pairs it is a LOWER BOUND of the clearance, equal to it when the closest features are
face-face or edge-edge). Holes (arm hub bore, arm hole, horn hole, cheek pin holes) are not subtracted (solid hulls = conservative), so joints
that are seated through a hole are excluded from the pair list and named below.
Static solids: servo case box, servo lead boot, core pocket walls (fore, two sides) and the core aft block, each as a hull (conservative, adds
material in concave places); skin thickness is "-" in the CAD (no skin part) and not modelled. Also a 2-D section check of the elevon panel
against the core (cove) at the horn station, polygon distance/containment.
CRITERION (fixed before the run): no penetration > 0.05 mm (project gate tolerance, collide_a.py --tol-mm default) for any listed pair at any
pose; pairs excluded as seated joints or bonded/designed contacts are listed with their values.
"""
import csv
import itertools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np                              # noqa: E402
import scipy                                    # noqa: E402
from scipy.spatial import ConvexHull            # noqa: E402
import linkage_core as k                        # noqa: E402

e, w, c = k._e, k._w, k._c
MM = 1e-3
TOL_MM = 0.05
NCIRC = 32
STEP_DEG = 0.5


# ------------------------------------------------------------------ convex solids as vertex clouds
def circle_pts(center, axis, radius, n=NCIRC):
    axis = np.asarray(axis, float)
    axis = axis / np.linalg.norm(axis)
    a = np.array([1.0, 0, 0]) if abs(axis[0]) < 0.9 else np.array([0, 1.0, 0])
    p = np.cross(axis, a)
    p /= np.linalg.norm(p)
    q = np.cross(axis, p)
    r = radius / math.cos(math.pi / n)                       # circumscribed polygon: contains the true circle
    return [np.asarray(center) + r * (math.cos(2 * math.pi * i / n) * p + math.sin(2 * math.pi * i / n) * q) for i in range(n)]


def cyl(p0, p1, radius):
    ax = np.asarray(p1, float) - np.asarray(p0, float)
    return np.array(circle_pts(p0, ax, radius) + circle_pts(p1, ax, radius))


def box_frame(origin, e1, e2, e3, lo, hi):
    """box with local ranges lo..hi along the orthonormal frame (e1, e2, e3) at origin"""
    pts = []
    for a, b, d in itertools.product((lo[0], hi[0]), (lo[1], hi[1]), (lo[2], hi[2])):
        pts.append(np.asarray(origin) + a * e1 + b * e2 + d * e3)
    return np.array(pts)


def aabb(lo, hi):
    return box_frame(np.zeros(3), np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0]), lo, hi)


def prism_y(poly_xz, y0, y1):
    return np.array([(x, y, z) for x, z in poly_xz for y in (y0, y1)])


def prism_z(poly_xy, z0, z1):
    return np.array([(x, y, z) for x, y in poly_xy for z in (z0, z1)])


def rot_xz(pts, delta):
    """rotate 3-D points about the hinge axis (parallel to y through x = XH, z = HINGE_Z) by delta (rad), CAD sense"""
    p = np.array(pts, float)
    vx, vz = p[:, 0] - k.XH, p[:, 2] - k.HINGE_Z
    cd, sd = math.cos(delta), math.sin(delta)
    p[:, 0] = k.XH + vx * cd + vz * sd
    p[:, 2] = k.HINGE_Z - vx * sd + vz * cd
    return p


# ------------------------------------------------------------------ SAT
class Hull:
    def __init__(self, pts):
        pts = np.asarray(pts, float)
        h = ConvexHull(pts)
        self.v = pts[h.vertices]
        nrm = h.equations[:, :3]
        self.normals = np.unique(np.round(nrm, 7), axis=0)
        ed = set()
        dirs = []
        for s in h.simplices:
            for i in range(3):
                d = pts[s[(i + 1) % 3]] - pts[s[i]]
                n = np.linalg.norm(d)
                if n < 1e-12:
                    continue
                d = d / n
                if (d[0], d[1], d[2]) < (0, 0, 0):
                    d = -d
                key = tuple(np.round(d, 6))
                if key not in ed:
                    ed.add(key)
                    dirs.append(d)
        self.edges = np.array(dirs)


def sep(A, B):
    """signed separation: > 0 gap (lower bound of the distance), < 0 penetration depth (minimum translation over the SAT axes)"""
    axes = [A.normals, B.normals]
    cr = np.cross(A.edges[:, None, :], B.edges[None, :, :]).reshape(-1, 3)
    n = np.linalg.norm(cr, axis=1)
    cr = cr[n > 1e-9] / n[n > 1e-9, None]
    axes.append(cr)
    ax = np.vstack(axes)
    pa, pb = A.v @ ax.T, B.v @ ax.T
    gap = np.maximum(pb.min(0) - pa.max(0), pa.min(0) - pb.max(0))
    return float(gap.max())


# ------------------------------------------------------------------ 2-D polygons (elevon panel vs core)
def seg_dist(P, Q):
    """min distance between the boundary polylines of closed polygons P and Q (N x 2), brute force"""
    a, b = P, np.roll(P, -1, axis=0)
    cc, dd = Q, np.roll(Q, -1, axis=0)

    def pt_seg(p, s0, s1):
        v = s1 - s0
        t = np.clip(((p[:, None, :] - s0[None]) * v[None]).sum(-1) / (v * v).sum(-1)[None], 0, 1)
        proj = s0[None] + t[..., None] * v[None]
        return np.linalg.norm(p[:, None, :] - proj, axis=-1)
    return float(min(pt_seg(P, cc, dd).min(), pt_seg(Q, a, b).min()))


def inside(pt, poly):
    x, y = pt[:, 0], pt[:, 1]
    x1, y1 = np.roll(poly[:, 0], -1), np.roll(poly[:, 1], -1)
    x0, y0 = poly[:, 0], poly[:, 1]
    res = np.zeros(len(pt), bool)
    for i in range(len(poly)):
        cond = ((y0[i] > y) != (y1[i] > y)) & (x < (x1[i] - x0[i]) * (y - y0[i]) / (y1[i] - y0[i] + 1e-30) + x0[i])
        res ^= cond
    return res


def poly_sep(P, Q):
    d = seg_dist(P, Q)
    ip, iq = inside(P, Q), inside(Q, P)
    if ip.any() or iq.any():
        return -_depth(P, Q, ip, iq)
    return d


def _depth(P, Q, ip, iq):
    def pd(pts, poly):
        a, b = poly, np.roll(poly, -1, axis=0)
        v = b - a
        t = np.clip(((pts[:, None, :] - a[None]) * v[None]).sum(-1) / (v * v).sum(-1)[None], 0, 1)
        return np.linalg.norm(pts[:, None, :] - (a[None] + t[..., None] * v[None]), axis=-1).min(1)
    m = 0.0
    if ip.any():
        m = max(m, pd(P[ip], Q).max())
    if iq.any():
        m = max(m, pd(Q[iq], P).max())
    return m


# ------------------------------------------------------------------ geometry from the CAD constants
def static_set(sy):
    yc = sy * k.SERVO_Y
    S = {}
    S['servo case'] = Hull(aabb((e.SV_X0, yc - e.SV_DY, e.SV_Z0), (e.SV_X1, yc + e.SV_DY, e.SV_Z1)))
    S['servo boot'] = Hull(cyl((0.1305, yc, e.SV_Z1), (0.1305, yc, e.SV_Z1 + 0.0020), 0.003))
    px0, px1, zp = 0.1245, 0.1655, c.SV_Z1
    ya, yb = yc - 0.0225, yc + 0.0225
    xs_f = np.linspace(0.05, px0, 20)
    S['pocket wall fore'] = Hull(prism_y([(x, c.zu(x)) for x in xs_f] + [(x, zp) for x in xs_f], ya, yb))
    for tag, (ys0, ys1) in (('outboard', (yb, yb + 0.05)), ('inboard', (ya - 0.05, ya))):
        if sy < 0:
            ys0, ys1 = -ys1, -ys0
        xs_s = np.linspace(px0, px1, 20)
        zt = np.array([max(c.zu(x), zp) for x in xs_s])
        S['pocket wall side %s' % tag] = Hull(prism_y([(x, z) for x, z in zip(xs_s, zt)] + [(x, zp) for x in xs_s], min(ys0, ys1), max(ys0, ys1)))
    xs_a = np.linspace(px1, k.XH, 20)
    S['core aft block'] = Hull(prism_y([(x, c.zu(x)) for x in xs_a] + [(x, -0.012) for x in xs_a], ya, yb))
    return S


def elevon_slab_poly():
    loop = c.k9.section_loop(c.COORDS, c.C, (0.0, 0.0), 1 - c.ELEV_FRAC, 1.0, 8)
    return [(p[0], p[1]) for p in loop]


def horn_blade_poly():
    zb = max(c.zu(e.HORN_X0 - 0.002), c.zu(e.HORN_X0), c.zu(e.HORN_X1))
    return zb, e._rrect(e.HORN_X0, zb + 1.0 * MM, e.HORN_X1, e.HORN_TOP, 1.5 * MM, 3)


def moving_set(theta, delta, sy):
    """world hulls of every moving part at (theta, delta); side sy"""
    yc = sy * k.SERVO_Y
    P = {}
    # --- servo side: arm turns about z at (SV_XS, yc)
    ux, uy = -sy * (-math.sin(theta)) * 0 + sy * math.sin(theta), -sy * math.cos(theta)    # Rz(theta) (0, -sy)
    loop = e._arm_loop(k.SV_XS, yc, ux, uy)
    P['arm'] = Hull(prism_z(loop, e.ARM_Z0, e.ARM_Z1))
    pa = k.arm_pt(theta, sy)
    ph = k.horn_pt(delta, sy)
    u = (ph - pa) / np.linalg.norm(ph - pa)
    P['rod Z-bend pin'] = Hull(cyl((pa[0], pa[1], e.ARM_Z0 + 0.0001), (pa[0], pa[1], k.ROD_Z), k.ROD_D / 2))
    q = ph - 4 * MM * u                                       # clevis body starts 4 mm before the hole (electrical.py:967)
    P['rod'] = Hull(cyl(pa, q, k.ROD_D / 2))
    P['clevis sleeve'] = Hull(cyl(q, q + 2 * MM * u, 1.5 * MM))
    e2 = np.array([0, 1.0, 0]) - u[1] * u
    e2 /= np.linalg.norm(e2)
    e3 = np.cross(u, e2)
    for sg in (-1, 1):
        P['clevis cheek %+d' % sg] = Hull(box_frame(q, u, e2, e3, (2 * MM, sg * 1.5 * MM - 0.4 * MM, -1.6 * MM), (5.5 * MM, sg * 1.5 * MM + 0.4 * MM, 1.6 * MM)))
    # --- elevon side (rotates by delta about the hinge)
    hy = sy * (k.SERVO_Y - k.ARM_R)
    zb, blade = horn_blade_poly()
    P['horn plate'] = Hull(rot_xz(aabb((e.HORN_X0 - 0.002, hy - 4 * MM, zb), (e.HORN_X1, hy + 4 * MM, zb + 1.0 * MM)), delta))
    P['horn blade'] = Hull(rot_xz(prism_y(blade, hy - 1.0 * MM, hy + 1.0 * MM), delta))
    P['clevis pin'] = Hull(rot_xz(cyl((k.HORN_XH, hy - 2.2 * MM, k.ROD_Z), (k.HORN_XH, hy + 2.2 * MM, k.ROD_Z), 0.5 * MM), delta))
    P['elevon slab'] = Hull(rot_xz(prism_y(elevon_slab_poly(), hy - 0.015, hy + 0.015), delta))
    return P


# pairs that are seated through a hole, bonded, or the same part: excluded (reason given)
EXCLUDED = {
    ('arm', 'rod Z-bend pin'): 'pin seated in the arm hole (ctx.seat / E-MEC rod Z-bend in the arm tip hole; hole not subtracted)',
    ('clevis pin', 'clevis cheek -1'): 'pin through the cheek holes (E-MEC-PIN-*3)', ('clevis pin', 'clevis cheek +1'): 'pin through the cheek holes (E-MEC-PIN-*3)',
    ('clevis pin', 'horn blade'): 'pin through the horn hole (E-MEC-PIN-*4)',
    ('horn plate', 'horn blade'): 'one part (MEC-004)', ('horn plate', 'elevon slab'): 'horn bonded on the elevon upper skin (E-MEC horn edge)',
    ('horn blade', 'elevon slab'): 'horn bonded on the elevon upper skin', ('clevis pin', 'horn plate'): 'pin and horn are one rigid group; pin sits 9 mm above the plate',
    ('clevis pin', 'elevon slab'): 'pin is part of the elevon-side group (rigid with the slab)',
    ('rod', 'clevis sleeve'): 'one part (MEC-003)', ('rod', 'clevis cheek -1'): 'one part (MEC-003)', ('rod', 'clevis cheek +1'): 'one part (MEC-003)',
    ('clevis sleeve', 'clevis cheek -1'): 'one part (MEC-003)', ('clevis sleeve', 'clevis cheek +1'): 'one part (MEC-003)',
    ('clevis cheek -1', 'clevis cheek +1'): 'one part (MEC-003)', ('rod', 'rod Z-bend pin'): 'one part (MEC-003)',
    ('rod Z-bend pin', 'clevis sleeve'): 'one part (MEC-003)', ('rod Z-bend pin', 'clevis cheek -1'): 'one part (MEC-003)', ('rod Z-bend pin', 'clevis cheek +1'): 'one part (MEC-003)',
}
STATIC_EXCL = {('elevon slab', 'core aft block'): 'hull artifact: the convex hull of the elevon section fills the cove that the hull of the core aft block also fills; the elevon-core pair is checked on the non-convex 2-D sections instead'}
DESIGN_CONTACT = {('arm', 'servo case'): 'arm bottom sits on the case top (ARM_Z0 = SV_Z1, boss height "-")',
                  ('rod', 'arm'): 'rod bottom tangent to the arm top (ROD_Z = ARM_Z1 + D/2): zero clearance by construction'}


def main():
    res = dict(git_head=k.git_head(), engine='analytic convex solids + separating-axis test (numpy, scipy.spatial.ConvexHull); NOT mesh-based',
               versions=dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__), tol_mm=TOL_MM, step_deg=STEP_DEG,
               trimesh_manifold3d='not installed; Blender not available here')
    degs = np.round(np.arange(-k.ELEV_STOP, k.ELEV_STOP + 1e-9, STEP_DEG), 6)
    table = {}                                   # (side, pair) -> list of (delta, sep_mm)
    for sy in (1, -1):
        stat = static_set(sy)
        for dd in degs:
            d = math.radians(dd)
            th = k.theta_of_delta(d, sy)
            mov = moving_set(th, d, sy)
            for a_, A in mov.items():
                for b_, B in stat.items():
                    if (a_, b_) in STATIC_EXCL:
                        continue
                    table.setdefault((sy, a_, b_), []).append((float(dd), sep(A, B) * 1e3))
            for a_, b_ in itertools.combinations(mov, 2):
                if (a_, b_) in EXCLUDED or (b_, a_) in EXCLUDED:
                    continue
                table.setdefault((sy, a_, b_), []).append((float(dd), sep(mov[a_], mov[b_]) * 1e3))
    pairs = []
    worst_pen = 0.0
    for (sy, a_, b_), v in sorted(table.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        arr = np.array(v)
        i = int(arr[:, 1].argmin())
        dc = (a_, b_) in DESIGN_CONTACT or (b_, a_) in DESIGN_CONTACT
        pairs.append(dict(side='R' if sy > 0 else 'L', a=a_, b=b_, min_sep_mm=float(arr[i, 1]), at_delta_deg=float(arr[i, 0]),
                          neutral_sep_mm=float(arr[len(arr) // 2, 1]), max_penetration_mm=float(max(0.0, -arr[:, 1].min())), design_contact=dc,
                          penetrating_deltas_deg=[float(x) for x in arr[arr[:, 1] < -1e-6, 0]],
                          first_delta_deg_over_tol=(float(arr[arr[:, 1] < -TOL_MM, 0][0]) if (arr[:, 1] < -TOL_MM).any() else None),
                          sep_mm_at_pm20_pm21={str(int(q_)): float(arr[np.argmin(abs(arr[:, 0] - q_)), 1]) for q_ in (-21, -20, 20, 21)}))
    # side R summary and worst
    pen = [p for p in pairs if p['max_penetration_mm'] > 1e-6]
    worst = max(pairs, key=lambda p: p['max_penetration_mm'])
    clear = [p for p in pairs if p['max_penetration_mm'] <= 1e-6 and p['min_sep_mm'] > 1e-6]
    res['pairs'] = pairs
    res['n_pairs_evaluated'] = len(pairs)
    res['n_poses_per_side'] = len(degs)
    res['penetrating_pairs'] = [dict(side=p['side'], pair=p['a'] + ' / ' + p['b'], depth_mm=p['max_penetration_mm'], at_delta_deg=p['at_delta_deg'],
                                     range_deg=[min(p['penetrating_deltas_deg']), max(p['penetrating_deltas_deg'])], design_contact=p['design_contact'],
                                     first_delta_deg_over_tol=p['first_delta_deg_over_tol'], sep_mm_at_pm20_pm21=p['sep_mm_at_pm20_pm21']) for p in pen]
    res['worst_penetration_mm'] = worst['max_penetration_mm']
    res['worst_pair'] = worst['a'] + ' / ' + worst['b']
    res['min_positive_clearance_mm'] = min(p['min_sep_mm'] for p in clear) if clear else None
    res['min_clearance_pair'] = min(clear, key=lambda p: p['min_sep_mm'])['a'] + ' / ' + min(clear, key=lambda p: p['min_sep_mm'])['b'] if clear else None
    res['min_clearance_excl_design_contact_mm'] = min([p['min_sep_mm'] for p in clear if not p['design_contact']] or [None])
    res['excluded_pairs'] = {' / '.join(kk): v for kk, v in {**EXCLUDED, **STATIC_EXCL}.items()}
    res['design_contacts'] = {' / '.join(kk): v for kk, v in DESIGN_CONTACT.items()}
    # cap / balance pocket distance by y (not swept: far away)
    hy = k.SERVO_Y - k.ARM_R
    res['y_gap_horn_plate_to_cap_flange_mm'] = (w.CAP_Y0 - (hy + 0.004)) * 1e3
    # 2-D elevon panel vs core section at the horn station
    core = np.array(w.core_loop())
    ev0 = np.array(elevon_slab_poly())
    sec = []
    for dd in degs:
        d = math.radians(dd)
        pts = np.array([[k.XH + (x - k.XH) * math.cos(d) + (z - k.HINGE_Z) * math.sin(d), k.HINGE_Z - (x - k.XH) * math.sin(d) + (z - k.HINGE_Z) * math.cos(d)] for x, z in ev0])
        sec.append((float(dd), poly_sep(pts, core) * 1e3))
    sa = np.array(sec)
    nose = []                                                  # nose lower part (below the hinge line) against the core cove face
    for dd in degs:
        d = math.radians(dd)
        pts = np.array([[k.XH + (x - k.XH) * math.cos(d) + (z - k.HINGE_Z) * math.sin(d), k.HINGE_Z - (x - k.XH) * math.sin(d) + (z - k.HINGE_Z) * math.cos(d)] for x, z in ev0 if z < k.HINGE_Z - 0.5 * MM and x < k.XH + 0.01])
        a_, b_ = core, np.roll(core, -1, axis=0)
        v = b_ - a_
        t = np.clip(((pts[:, None, :] - a_[None]) * v[None]).sum(-1) / (v * v).sum(-1)[None], 0, 1)
        dist = np.linalg.norm(pts[:, None, :] - (a_[None] + t[..., None] * v[None]), axis=-1).min()
        nose.append((float(dd), float(dist * 1e3) * (-1 if inside(pts, core).any() else 1)))
    na = np.array(nose)
    res['elevon_vs_core_2d'] = dict(min_sep_mm=float(sa[:, 1].min()), at_delta_deg=float(sa[sa[:, 1].argmin(), 0]), neutral_mm=float(sa[len(sa) // 2, 1]),
                                    nose_below_hinge_to_core_min_mm=float(na[:, 1].min()), nose_below_hinge_min_at_delta_deg=float(na[na[:, 1].argmin(), 0]),
                                    note='elevon nose touches the core corner at the hinge at neutral by construction (0 mm); sections only (no balance pocket, caps, tape)')
    # criteria
    crit_pen = [p for p in pairs if p['max_penetration_mm'] > TOL_MM]
    res['pass_no_penetration_gt_tol'] = bool(len(crit_pen) == 0 and sa[:, 1].min() > -TOL_MM and na[:, 1].min() > -TOL_MM)
    res['pairs_failing'] = [dict(side=p['side'], pair=p['a'] + ' / ' + p['b'], depth_mm=p['max_penetration_mm'], at_delta_deg=p['at_delta_deg'], first_delta_deg_over_tol=p['first_delta_deg_over_tol']) for p in crit_pen]
    os.makedirs(k.OUT, exist_ok=True)
    with open(os.path.join(k.OUT, 'linkage_sweep_collision.json'), 'w') as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(k.OUT, 'linkage_sweep_collision.csv'), 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['side', 'part_a', 'part_b', 'delta_deg', 'separation_mm (negative = penetration)'])
        for (sy, a_, b_), v in sorted(table.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
            for dd, s_ in v:
                if abs(dd * 2 - round(dd * 2)) < 1e-9:
                    wr.writerow(['R' if sy > 0 else 'L', a_, b_, dd, round(s_, 5)])
    plt = k.get_plt()
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    keys = sorted({(a_, b_) for (sy, a_, b_) in table if sy == 1}, key=lambda t: min(v[1] for v in table[(1,) + t]))[:8]
    for t in keys:
        v = np.array(table[(1,) + t])
        ax[0].plot(v[:, 0], v[:, 1], label=' / '.join(t))
    ax[0].axhline(-TOL_MM, c='r', ls=':')
    ax[0].axhline(0, c='k', lw=.5)
    ax[0].set_xlabel('elevon delta (deg)')
    ax[0].set_ylabel('separation (mm), SAT, R side; dotted = -0.05 mm gate')
    ax[0].set_ylim(-0.5, 3)
    ax[0].legend(fontsize=6)
    ax[0].grid(alpha=.3)
    ax[1].plot(sa[:, 0], sa[:, 1])
    ax[1].set_xlabel('elevon delta (deg)')
    ax[1].set_ylabel('2-D elevon panel to core section distance (mm)')
    ax[1].grid(alpha=.3)
    fig.suptitle('Swept clearance of the linkage and horn (analytic convex solids)')
    fig.tight_layout()
    fig.savefig(os.path.join(k.OUT, 'linkage_sweep_collision.png'), dpi=110)
    print(json.dumps({kk: res[kk] for kk in ('n_pairs_evaluated', 'penetrating_pairs', 'worst_penetration_mm', 'worst_pair', 'min_positive_clearance_mm', 'min_clearance_pair',
                                             'min_clearance_excl_design_contact_mm', 'elevon_vs_core_2d', 'y_gap_horn_plate_to_cap_flange_mm', 'pass_no_penetration_gt_tol', 'pairs_failing')}, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
