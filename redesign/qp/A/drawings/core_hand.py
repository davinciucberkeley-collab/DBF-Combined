"""core_hand.py - the wing core (WNG-001) drawing as a hand-cut set, called by compose_drawings.py for WNG-001.

The core is made as the build guide says (BUILD-GUIDE-A step A1): two foam halves split at the spar centre plane (z = 0), cut
separately, then bonded. Every cut is measured from three datums a person can find on the bench: the flat split face (z = 0),
the leading edge (x) and the centreline (y). Nothing here is typed in: every outline, depth and section comes from the CAD
(qp/A/cad/amodel wing.py + common.py for the airfoil, the drawing job's cut list for the cuts, the shop mesh
out/_work/WNG-001.stl for the 1:1 sections).

Sheets (17 x 11 in):
  1  How to make it: halves, datums, order of work, methods
  2  1:1 templates for the two halves (hot wire or sanding block) and the airfoil coordinates
  3  Upper half: plan of the top-face cuts and of the split-face cuts (1:2.5)
  4  Lower half: plan of the split-face cuts and of the bottom-face cuts (1:2.5)
  5+ Cut table: one line per cut and half (position from the datums, depth, method)
  .. 1:1 sections through every group of cuts (cut out and hold against the part)
  .. Every CAD cut and the line of the cut table that makes it (nothing left out)
"""
import datetime
import math
import os
import struct
import sys
import textwrap

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                    # noqa: E402
from matplotlib.patches import Polygon, Rectangle, Circle   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.join(os.path.dirname(HERE), 'cad')
if CAD not in sys.path:
    sys.path.insert(0, CAD)
from amodel import common as AC   # noqa: E402
from amodel import wing as AW     # noqa: E402

W_IN, H_IN = 17.0, 11.0
MM = 1 / 25.4
INK, MUTED, RULE, ACC = '#111111', '#555555', '#999999', '#1f5fa8'
FOAM, THRU = '#e9e6dc', '#bdbdbd'
XH = AC.XH * 1000.0                 # hinge = aft end of the core (183.75)
XL = AW.XL * 1000.0                 # foot of the slanted back face (cove for the elevon nose)
HALF_SPAN = AC.B * 500.0            # 450
TOL = 0.6                           # mm: a cut counts as inside another when it is inside it to this tolerance


# ----------------------------------------------------------------------------- airfoil (mm)
def zu(x):
    return AC.zu(min(max(x, 0.0), XH) / 1000.0) * 1000.0


def zlo(x):
    """Lower boundary of the core: S5010 lower surface to the cove foot XL, then the straight slanted back face up to the hinge."""
    x = min(max(x, 0.0), XH)
    if x <= XL:
        return AC.zl(x / 1000.0) * 1000.0
    z0, z1 = AC.zl(XL / 1000.0) * 1000.0, zu(XH)
    return z0 + (z1 - z0) * (x - XL) / (XH - XL)


def _root(f, a, b):
    for _ in range(80):
        m = (a + b) / 2
        if (f(a) > 0) == (f(m) > 0):
            a = m
        else:
            b = m
    return (a + b) / 2


XU0 = _root(zu, 0.0, 20.0)          # where the upper surface crosses the split plane: the upper half starts here (the nose is all in the lower half)
XZ0 = _root(zlo, XL, XH)            # where the back face crosses the split plane: aft of it the lower half has no foam


def core_outline():
    return [(x * 1000, z * 1000) for x, z in AW.core_loop()]


def half_outline(half):
    """Profile of one half (x, z mm), closed: U = between z 0 and the upper skin, L = between the lower boundary and min(0, upper skin)."""
    xs = sorted(set([p[0] for p in core_outline()] + list(np.linspace(0, XH, 400))))
    if half == 'U':
        xs = [x for x in xs if x >= XU0]
        top = [(x, max(zu(x), 0.0)) for x in xs]
        return [(XU0, 0.0)] + top[1:] + [(XH, 0.0)]
    top = [(x, min(0.0, zu(x))) for x in xs if x <= XZ0]
    bot = [(x, zlo(x)) for x in reversed(xs) if x <= XZ0]
    return top + [(XZ0, 0.0)] + bot


# ----------------------------------------------------------------------------- cuts
NICE = {'WNG-002': 'spar bore 12 mm (spar WNG-002)', 'FIN-002': 'fin rib tube channel 14 mm (FIN-002)', 'CGE-004': 'bridge tube 16 mm (CGE-004)',
        'CGE-005': 'V strut 6 mm (CGE-005)', 'CGE-006': 'bridge saddle (CGE-006)', 'CGE-007': 'strut clamp (CGE-007)', 'FIN-005': 'rib saddle (FIN-005)',
        'CGE-008': 'pack tray (CGE-008)', 'HRN-003': 'phase-lead raceway (HRN-003)', 'HWC-001': 'FC screw tips (HWC-001)', 'HWC-003': 'FC nuts (HWC-003)',
        'MEC-001': 'servo body (MEC-001)'}


def nice_name(f):
    n = f['name']
    if n.startswith('groove / bore / pocket cut in the core for '):
        pid = n.rsplit(' ', 1)[-1]
        base = '-'.join(pid.split('-')[:2])
        if base == 'AVN-006':
            if f['kind'] == 'revolve' and f['d_out'] >= 2.9:
                return 'pitot tube 3 mm (AVN-006)'
            return 'pitot block / line stub (AVN-006)'
        return NICE.get(base, pid)
    for sep in (':', ' ('):
        n = n.split(sep)[0]
    return n.strip()


def strut_loop(sg):
    S, E = AW.STRUT_S, AW.STRUT_E
    d = (E[0] - S[0], E[1] - S[1])
    L_ = math.hypot(*d)
    ux, uy = d[0] / L_, d[1] / L_
    nx, ny = -uy * 0.0050, ux * 0.0050
    p0 = (-0.012, S[1] + (-0.012 - S[0]) / ux * uy)
    p1 = (E[0], E[1])
    lp = [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)]
    return [(x * 1000, sg * y * 1000) for x, y in lp]


def footprint(f):
    """Plan outline (x, y mm) of a cut."""
    lo, hi = f['lo'], f['hi']
    if f['name'].startswith('strut slot'):
        return strut_loop(1 if lo[1] > 0 else -1)
    if f['kind'] == 'revolve':
        a, s, r, L_ = f['axis'], f['start'], f['d_out'] / 2, f['length']
        if abs(a[2]) > 0.9:
            return [(s[0] - r, s[1] - r), (s[0] + r, s[1] - r), (s[0] + r, s[1] + r), (s[0] - r, s[1] + r)]
        n = math.hypot(a[0], a[1])
        ux, uy = a[0] / n, a[1] / n
        e = (s[0] + ux * L_, s[1] + uy * L_)
        return [(s[0] - uy * r, s[1] + ux * r), (e[0] - uy * r, e[1] + ux * r), (e[0] + uy * r, e[1] - ux * r), (s[0] + uy * r, s[1] - ux * r)]
    return [(lo[0], lo[1]), (hi[0], lo[1]), (hi[0], hi[1]), (lo[0], hi[1])]


def _inside(p, poly, tol):
    x, y = p
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    if c:
        return True
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[i - 1]
        dx, dy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy or 1)))
        if math.hypot(x - x1 - t * dx, y - y1 - t * dy) <= tol:
            return True
    return False


def clip_x(poly, xa, xb):
    """Sutherland-Hodgman clip of a plan polygon (x, y) to xa <= x <= xb."""
    def cut(pl, keep, xc):
        out = []
        for i in range(len(pl)):
            p, q = pl[i - 1], pl[i]
            if keep(q):
                if not keep(p):
                    out.append((xc, p[1] + (q[1] - p[1]) * (xc - p[0]) / (q[0] - p[0])))
                out.append(q)
            elif keep(p):
                out.append((xc, p[1] + (q[1] - p[1]) * (xc - p[0]) / (q[0] - p[0])))
        return out
    pl = cut(list(poly), lambda p: p[0] >= xa, xa)
    return cut(pl, lambda p: p[0] <= xb, xb) if pl else pl


def _edge_pts(poly, n=24):
    pts = []
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i - 1], poly[i]
        pts += [(x1 + (x2 - x1) * t / n, y1 + (y2 - y1) * t / n) for t in range(n)]
    return [p for p in pts if -1e-6 <= p[0] <= XH + 1e-6 and abs(p[1]) <= HALF_SPAN + 1e-6]


def is_box(f):
    return f['kind'] == 'prism' and f.get('axis') == 'Z' and not f['name'].startswith('groove / bore')


def is_container(f):
    return is_box(f) or f['name'].startswith('strut slot')


_FOLLOW = []


def follow_depth():
    """(foam over, floor depth) below the upper skin of the servo-lead run along x (electrical.py: servo_zc(x) +- 1.6 mm), at x 80-110."""
    if not _FOLLOW:
        from amodel import electrical as E
        v = [((AC.zu(x) - E.servo_zc(x) - 0.0016) * 1000, (AC.zu(x) - E.servo_zc(x) + 0.0016) * 1000) for x in (0.080, 0.097, 0.110)]
        _FOLLOW.append((min(a for a, b in v), max(b for a, b in v)))
    return _FOLLOW[0]


def x_range(f):
    pts = _edge_pts(footprint(f))
    if not pts:
        return None
    return max(min(p[0] for p in pts), 0.0), min(max(p[0] for p in pts), XH)


def skin_range(fun, x0, x1):
    v = [fun(x) for x in np.linspace(x0, x1, 41)]
    return min(v), max(v)


def make_inside(c, tol):
    """Point-in-cut test (mm) from the CAD shape: boxes by their extent, the strut slot by its plan outline, the elevon balance
    pocket by its section outline (wing.bal_sweep_loop), revolves by distance to the axis."""
    f = c['f']
    lo, hi = f['lo'], f['hi']
    if f['name'].startswith('strut slot'):
        poly = c['fp']
        return lambda p: lo[2] - tol <= p[2] <= hi[2] + tol and _inside((p[0], p[1]), poly, tol)
    if f['name'].startswith('elevon balance pocket'):
        loop = [(x * 1000, z * 1000) for x, z in AW.bal_sweep_loop()]
        return lambda p: lo[1] - tol <= p[1] <= hi[1] + tol and _inside((p[0], p[2]), loop, tol)
    if f['kind'] == 'revolve':
        a, s0, L_, r = np.array(f['axis']), np.array(f['start']), f['length'], f['d_out'] / 2

        def inside_rev(p):
            d = np.array(p) - s0
            t = float(d @ a)
            return -tol <= t <= L_ + tol and float(np.linalg.norm(d - t * a)) <= r + tol
        return inside_rev
    return lambda p: all(lo[k] - tol <= p[k] <= hi[k] + tol for k in range(3))


def analyse(job):
    """For every CAD cut: 'outside' (removes no foam), 'inside' another cut, or the per-half operations it needs.
    Returns (cuts, rows): cuts[i] = dict(f, status, host); rows = cut-table lines (merged R/L pairs)."""
    F = job['cut_features']
    cuts = []
    for i, f in enumerate(F):
        c = dict(i=i, f=f, name=nice_name(f), fp=footprint(f), status=None, host=None, ops=[])
        xr = x_range(f)
        z0, z1 = f['lo'][2], f['hi'][2]
        if xr is None or xr[1] - xr[0] < 0.05:
            c['status'] = 'outside'
        else:
            x0, x1 = xr
            if z0 >= skin_range(zu, x0, x1)[1] - 0.05 or z1 <= skin_range(zlo, x0, x1)[0] + 0.05:
                c['status'] = 'outside'
        c['xr'] = xr
        cuts.append(c)
    for c in cuts:                                       # points of the cut that are in the foam
        c['inside'] = make_inside(c, TOL)
        if c['status']:
            c['pts'] = []
            continue
        own = make_inside(c, 0.0)
        lo, hi = c['f']['lo'], c['f']['hi']
        g = [np.linspace(lo[k] + 1e-3, hi[k] - 1e-3, 9) for k in range(3)]
        c['pts'] = [(x, y, z) for x in g[0] for y in g[1] for z in g[2]
                    if 0 <= x <= XH and abs(y) <= HALF_SPAN and zlo(x) < z < zu(x) and own((x, y, z))]
        if not c['pts']:
            c['status'] = 'outside'
    for c in cuts:                                       # inside another cut that removes all of it
        if c['status']:
            continue
        for h in cuts:
            if h is c or h['status'] == 'outside':
                continue
            if all(h['inside'](p) for p in c['pts']):
                if h['i'] > c['i'] and all(c['inside'](p) for p in h['pts']):
                    continue                             # the same volume twice: the first one hosts
                c['status'], c['host'] = 'inside', h
                break
    rows = []
    for c in cuts:
        if c['status']:
            continue
        f = c['f']
        x0, x1 = c['xr']
        pts = _edge_pts(c['fp'])
        y0, y1 = max(min(p[1] for p in pts), -HALF_SPAN), min(max(p[1] for p in pts), HALF_SPAN)
        z0, z1 = f['lo'][2], f['hi'][2]
        rev = f['kind'] == 'revolve'
        vert = rev and abs(f['axis'][2]) > 0.9
        flat_rev = rev and not vert and abs(f['start'][2]) < 0.3
        for half in ('U', 'L'):
            if half == 'U':
                xa, xb = max(x0, XU0), x1
                if xb - xa < 0.05 or z1 <= 0.05:
                    continue
                smin, smax = skin_range(zu, xa, xb)
                if z0 >= smax - 0.05:
                    continue
                from_split, open_sk = z0 <= 0.05, z1 >= smax - 0.05
                part = (not open_sk) and z1 > smin + 0.05
                depth_sk = (smin - z0, smax - z0)
            else:
                xa, xb = x0, min(x1, XZ0)
                if xb - xa < 0.05 or z0 >= -0.05:
                    continue
                smin, smax = skin_range(zlo, xa, xb)          # most negative, least negative
                if z1 <= smin + 0.05:
                    continue
                from_split, open_sk = z1 >= -0.05, z0 <= smin + 0.05
                part = (not open_sk) and z0 < smax - 0.05
                depth_sk = (z1 - smax, z1 - smin)
            r = dict(cut=c, half=half, x0=xa, x1=xb, y0=y0, y1=y1, z0=z0, z1=z1, name=c['name'], rev=rev)
            if 'following the skin' in f['name']:
                pass
            elif flat_rev:
                rad = f['d_out'] / 2
                r['type'] = 'R'
                r['depth'] = 'half-round R%.1f: %.1f deep in the split face' % (rad, rad)
                skin = zu if half == 'U' else (lambda x: -zlo(x))
                brk = [x for x in np.linspace(xa, xb, 200) if skin(x) < rad - 0.05]
                if brk:
                    r['depth'] += '; breaks through the %s skin for x %.0f-%.0f' % ('upper' if half == 'U' else 'lower', min(brk), max(brk))
            elif from_split and open_sk:
                r['type'], r['depth'] = ('H' if vert else 'K'), 'through this half'
                r['face'] = 'both'
            elif from_split:
                d = z1 if half == 'U' else -z0
                r['type'] = 'H' if vert else 'P'
                r['face'] = 'split'
                r['depth'] = '%.1f deep from the split face' % d
                if part:
                    r['depth'] += ' (where the skin is lower than that, this goes right through)'
            elif open_sk or part:
                fl = z0 if half == 'U' else -z1
                r['type'] = 'H' if vert else 'P'
                r['face'] = 'skin'
                r['depth'] = 'leave %.1f of foam above the split face (%.1f-%.1f deep from the top skin)' % (fl, max(depth_sk[0], 0), depth_sk[1]) if half == 'U' else \
                    'leave %.1f of foam below the split face (%.1f-%.1f deep from the bottom skin)' % (fl, max(depth_sk[0], 0), depth_sk[1])
                if part:
                    r['depth'] += '; ends under the skin where the skin is higher (see section)'
            if 'following the skin' in f['name']:
                r['type'], r['face'] = 'S', 'skin'
                r['depth'] = 'buried in the CAD: runs %.1f under the skin (floor %.1f below it) and rises into the servo pocket wall: knife slit to %.1f along the skin, press the lead in' % (
                    follow_depth()[0], follow_depth()[1], follow_depth()[1])
            elif r.get('type'):
                pass
            else:
                r['type'] = 'S'
                r['face'] = 'skin'
                r['depth'] = 'buried in the CAD (foam %.1f above, floor %.1f below the skin): knife slit to %.1f, press the lead in' % (
                    (smin - z1) if half == 'U' else (z0 - smax), depth_sk[1], depth_sk[1])
            if 'face' not in r:
                r['face'] = 'split' if r['type'] == 'R' else 'both'
            rows.append(r)
            c['ops'].append(r)
    # merge mirror pairs (same cut, same numbers, opposite y)
    merged = []
    for r in rows:
        key = (r['name'].replace(' R', '').replace(' L', ''), r['half'], r['type'], r['face'], round(r['x0'], 1), round(r['x1'], 1),
               round(min(abs(r['y0']), abs(r['y1'])), 1), round(max(abs(r['y0']), abs(r['y1'])), 1), round(r['z0'], 1), round(r['z1'], 1))
        for m in merged:
            if m['key'] == key and (m['y0'] + m['y1']) * (r['y0'] + r['y1']) < 0:
                m['pair'] = r
                break
        else:
            r['key'] = key
            merged.append(r)
    order = {('U', 'split'): 0, ('U', 'skin'): 2, ('U', 'both'): 1, ('L', 'split'): 3, ('L', 'both'): 4, ('L', 'skin'): 5}
    merged.sort(key=lambda r: (order[(r['half'], r['face'])], r['type'] == 'S', r['x0'], abs(r['y0'] + r['y1'])))
    cnt = {}
    for r in merged:
        cnt[r['half']] = cnt.get(r['half'], 0) + 1
        r['tag'] = '%s%d' % (r['half'], cnt[r['half']])
        for rr in (r, r.get('pair')):
            if rr:
                rr['tag'] = r['tag']
    return cuts, merged


METHOD = {
    'K': 'Through: knife against a steel rule, blade square to the face; long straight sides can be hot-wired. Cut from the face the table names, then check the other face.',
    'P': 'Pocket: score the outline to depth with a knife (tape on the blade at the depth), lift the foam out in layers, sand the floor flat with a small block; '
         'measure the floor with a depth gauge or a marked stick.',
    'R': 'Half-round groove: score both edge lines, scoop out, then sand with a dowel or tube of the groove diameter wrapped in 120-grit until the part lies in flush.',
    'S': 'Slit: the CAD draws this lead groove under the skin (foam above it), which a knife or a router cannot cut as a tunnel. Knife a slit along the line '
         'to the floor depth and press the lead to the bottom with a blunt spreader; the foam closes over it (D-211).',
    'H': 'Hole: push a sharpened brass tube of the diameter in by hand, twisting, to the depth; pull out the plug.',
}


# ----------------------------------------------------------------------------- shop mesh slices (1:1 sections)
def read_stl(path):
    with open(path, 'rb') as fh:
        fh.read(80)
        n = struct.unpack('<I', fh.read(4))[0]
        a = np.frombuffer(fh.read(n * 50), dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), count=n)
    return a['v'].astype(float)


def slice_y(tris, yc):
    """Closed loops (x, z) of the mesh cut by the plane y = yc."""
    segs = []
    for t in tris:
        d = t[:, 1] - yc
        if (d > 0).all() or (d < 0).all():
            continue
        p = []
        for i in range(3):
            a, b = t[i], t[(i + 1) % 3]
            da, db = d[i], d[(i + 1) % 3]
            if (da > 0) != (db > 0):
                s = da / (da - db)
                q = a + (b - a) * s
                p.append((round(q[0], 4), round(q[2], 4)))
        if len(p) == 2 and p[0] != p[1]:
            segs.append(tuple(p))
    adj = {}
    for a, b in segs:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    used, loops = set(), []
    for a, b in segs:
        if (a, b) in used or (b, a) in used:
            continue
        loop, prev, cur = [a], a, b
        used.add((a, b))
        while cur != a and len(loop) < 100000:
            loop.append(cur)
            nxt = [n for n in adj.get(cur, []) if (cur, n) not in used and (n, cur) not in used]
            if not nxt:
                break
            used.add((cur, nxt[0]))
            prev, cur = cur, nxt[0]
        loops.append(loop)
    return loops


# ----------------------------------------------------------------------------- sheet furniture
def frame(fig):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.add_patch(plt.Rectangle((0.25 / W_IN, 0.25 / H_IN), 1 - 0.5 / W_IN, 1 - 0.5 / H_IN, fill=False, lw=1.2, ec=INK))


def title(fig, job, sheet, nsheets, rev, scale, what):
    x0, y0, w, h = 12.4, 0.35, 4.25, 1.95
    ax = fig.add_axes([x0 / W_IN, y0 / H_IN, w / W_IN, h / H_IN])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(INK)
        sp.set_linewidth(1.0)
    ax.text(0.1, h - 0.1, 'WNG-001  wing core', fontsize=13, weight='bold', va='top', color=INK)
    ax.text(0.1, h - 0.42, what, fontsize=8.5, va='top', color=INK, weight='bold')
    lines = ['Hand-cut set. %s; CAD mass %s g with skin and glue.' % (job['material'], job['mass_g']),
             'Units mm. Scale %s. Datums: split face (z 0), leading edge (x), centreline (y).' % scale,
             'Tolerance: hand cutting about +-0.5 mm (EST); fit pockets for bought parts to the part.',
             'Source: qp/A/cad (commit %s); drawings/core_hand.py, %s.' % (rev, datetime.date.today().isoformat()),
             'Sheet %d of %d.' % (sheet, nsheets)]
    ax.text(0.1, h - 0.72, '\n'.join(lines), fontsize=6.6, va='top', color=INK, linespacing=1.5)


def mm_axes(fig, x_in, y_in, w_mm, h_mm, xlim, ylim):
    """Axes at true scale: (w_mm, h_mm) of paper show xlim / ylim of data mm."""
    ax = fig.add_axes([x_in / W_IN, y_in / H_IN, w_mm * MM / W_IN, h_mm * MM / H_IN])
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_axis_off()
    return ax


def para(fig, x_in, y_in, text, width, size=7.6, bold_first=False, gap=0.06):
    """Wrapped text block from the top at (x_in, y_in); returns the y below it."""
    y = y_in
    for k, block in enumerate(text):
        lines = textwrap.wrap(block, width)
        fig.text(x_in / W_IN, y / H_IN, '\n'.join(lines), fontsize=size, va='top', color=INK, linespacing=1.38,
                 weight='bold' if (bold_first and k == 0) else 'normal')
        y -= len(lines) * size * 1.38 / 72 + gap
    return y


# ----------------------------------------------------------------------------- sheets
def sheet_overview(fig, job, cuts, rows):
    fig.text(0.6 / W_IN, 10.55 / H_IN, 'How to make the wing core by hand', fontsize=15, weight='bold', va='top', color=INK)
    fig.text(0.6 / W_IN, 10.18 / H_IN, 'Two foam halves split at the spar centre, every cut measured from the flat split face, the leading edge and the centreline; then bond the halves.',
             fontsize=8.5, va='top', color=MUTED)
    # datum sketch at 1.5:1
    s = 1.5
    ax = mm_axes(fig, 0.6, 6.15, 200 * s, 34 * s, (-8, 192), (-17, 17))
    out = core_outline()
    for half, col in (('U', '#dfe8f3'), ('L', FOAM)):
        ax.add_patch(Polygon(half_outline(half), closed=True, fc=col, ec=INK, lw=0.9))
    ax.plot([-6, 190], [0, 0], color=ACC, lw=1.1, ls=(0, (6, 3)))
    ax.add_patch(Circle((AC.SPAR_X * 1000, 0), 6.0, fc='white', ec=INK, lw=0.8))
    ax.text(95, 4.0, 'UPPER HALF (slab U)', fontsize=8, ha='center', color=INK, weight='bold')
    ax.text(95, -6.5, 'LOWER HALF (slab L)', fontsize=8, ha='center', color=INK, weight='bold')
    ax.text(190.5, 0.6, 'split face  z = 0', fontsize=7.5, color=ACC, va='bottom', ha='right')
    ax.annotate('spar bore 12 mm, centre x %.0f on the split face' % (AC.SPAR_X * 1000), (AC.SPAR_X * 1000 + 4, 4.4), (78, 14.5), fontsize=7, color=INK,
                arrowprops=dict(arrowstyle='-', lw=0.6, color=INK))
    ax.annotate('leading edge: x = 0', (0, -5.3), (-6, -15.5), fontsize=7, color=INK, arrowprops=dict(arrowstyle='-', lw=0.6, color=INK))
    ax.annotate('hinge line x %.2f (core ends; elevons are separate parts)' % XH, (XH, 0.3), (112, -15.5), fontsize=7, color=INK,
                arrowprops=dict(arrowstyle='-', lw=0.6, color=INK))
    ax.annotate('upper half starts at x %.1f' % XU0, (XU0, 0), (8, 11.5), fontsize=7, color=INK, arrowprops=dict(arrowstyle='-', lw=0.6, color=INK))
    fig.text(0.6 / W_IN, 6.05 / H_IN, 'Section of the core, scale 1.5:1. x runs aft from the leading edge, y runs along the span from the centreline (+ = right wing, as seen from above, nose up), z up from the split face.',
             fontsize=7, color=MUTED, va='top')
    steps = [
        'ORDER OF WORK',
        '1. Templates (sheet 2). Print sheet 2 at 100 % (check the 100 mm bar), glue it to 3 mm ply, cut and sand to the lines: two U templates and two L templates. '
        'The flat edge of each template is the split face.',
        '2. Slabs. Two XPS slabs at least 960 x 280 x 15 mm (BUILD-GUIDE-A step A1). The flat underside of each slab is its split face: do not cut it.',
        '3. Profile. Pin a template to each end of a slab, flat edges on the slab underside and leading edges in line. Hot-wire round the templates (D-203 backup), '
        'or rough-cut with a long knife and sand with a long block riding on both templates. Upper half: %.0f mm long in x (from x %.1f to the hinge); lower half: from the '
        'leading edge to x %.1f.' % (XH - XU0, XU0, XZ0),
        '4. Datums. On each split face draw the centreline (y 0) square to the leading edge, the spar line (x %.0f) and lines every 50 mm along y; write R and L on the '
        'ends. Turning a half over swaps R and L as you look at it: always go by the R / L marks and the y numbers, never by "left of the picture".' % (AC.SPAR_X * 1000),
        '5. Split-face cuts (sheets 3-4, lines U..-split and L..-split in the table), with the half lying skin side down on a towel: the face is flat, so every depth is '
        'a plain depth from the face.',
        '6. Skin-side cuts and through cuts, half lying split face down on a flat board: a floor height "leave h of foam above the split face" is h above the board.',
        '7. Dry fit: lay the spar in the lower half groove, close the upper half, check each pocket against the 1:1 sections and its part. Then bond and tape (BUILD-GUIDE-A A1).',
    ]
    y = para(fig, 0.6, 5.45, steps, 118, 7.6, bold_first=True)
    meth = ['METHODS (column "how" in the cut table)'] + ['%s  %s' % (k, v) for k, v in METHOD.items()]
    para(fig, 9.0, 9.7, meth, 92, 7.4, bold_first=True)
    n_in = sum(1 for c in cuts if c['status'] == 'inside')
    n_out = sum(1 for c in cuts if c['status'] == 'outside')
    notes = ['CHECKS AND CARE',
             'Count: the CAD has %d cuts in the core; %d of them lie inside a bigger cut and %d remove no foam (last sheets list each one). The rest make the %d lines of the cut table.'
             % (len(cuts), n_in, n_out, len(rows)),
             'Thin edge: the upper half is only %.1f mm thick at the hinge (x %.0f). Cut the aft edge last and keep it supported on the board.' % (zu(XH), XH),
             'The 1:1 sections (sheets near the end) are cut from the CAD shop mesh: print at 100 %, cut one out and hold it against the core at its y to check depths and shapes.',
             'Pockets for bought parts (servo, airspeed board, pitot): the CAD sizes are vendor sizes, some EST. Fit each pocket to the real part before you go to full depth.']
    para(fig, 9.0, 5.45, notes, 92, 7.4, bold_first=True)


def sheet_templates(fig):
    fig.text(0.6 / W_IN, 10.55 / H_IN, 'Templates, full size (1:1). PRINT AT 100 %, no "fit to page".', fontsize=14, weight='bold', va='top', color=INK)
    fig.text(0.6 / W_IN, 10.2 / H_IN, 'Glue to 3 mm ply, cut and sand to the outline. Make two of each. The straight edge is the split face (z 0); the half-circle is the spar groove (R6) for alignment.',
             fontsize=8.2, va='top', color=MUTED)
    for k, (half, yb, lab) in enumerate((('U', 7.4, 'TEMPLATE U: upper half'), ('L', 4.5, 'TEMPLATE L: lower half'))):
        ax = mm_axes(fig, 0.9, yb, 230, 50, (-15, 215), (-25, 25))
        pl = half_outline(half)
        ax.add_patch(Polygon(pl, closed=True, fc='#f4f1e8', ec=INK, lw=0.8))
        sgn = 1 if half == 'U' else -1
        th = np.linspace(0, math.pi, 40)
        ax.plot(AC.SPAR_X * 1000 + 6 * np.cos(th), sgn * 6 * np.sin(th), color=INK, lw=0.7)
        for x in range(0, 190, 10):
            ax.plot([x, x], [0, -sgn * 2.2 if x % 50 else -sgn * 3.5], color=INK, lw=0.5)
            if x % 20 == 0:
                ax.text(x, -sgn * 5.5, str(x), fontsize=6, ha='center', va='center', color=MUTED)
        ax.plot([-10, 195], [0, 0], color=ACC, lw=0.6, ls=(0, (4, 2)))
        ax.text(-12, sgn * 17, lab, fontsize=8.5, weight='bold', color=INK, va='center')
        ax.text(XH, -sgn * 9, 'hinge x %.2f' % XH, fontsize=6.3, ha='right', color=MUTED)
        ax.text(0, -sgn * 9, 'LE x 0', fontsize=6.3, ha='left', color=MUTED)
    # 100 mm check bar
    ax = mm_axes(fig, 0.9, 3.6, 120, 14, (-5, 115), (-7, 7))
    ax.add_patch(Rectangle((0, -1.5), 100, 3, fc=INK))
    ax.text(50, 3.5, '100 mm: measure this bar before cutting the templates', fontsize=7.2, ha='center', color=INK)
    # coordinate table
    xs = [0, 1, 2.5, 5, 7.5] + list(range(10, 180, 10)) + [XL, XH]
    hdr = 'x from LE   z upper skin   z lower skin   (mm, from the split face; z lower = back face aft of x %.1f)' % XL
    rows = ['%8.2f   %10.2f   %12.2f' % (x, zu(x), zlo(x)) for x in xs]
    fig.text(10.4 / W_IN, 9.7 / H_IN, 'COORDINATES (no printer? plot these on the ply)', fontsize=8.5, weight='bold', va='top', color=INK)
    fig.text(10.4 / W_IN, 9.4 / H_IN, '\n'.join(textwrap.wrap(hdr, 60)), fontsize=6.8, va='top', color=MUTED)
    fig.text(10.4 / W_IN, 8.95 / H_IN, '\n'.join(rows), fontsize=7.2, va='top', family='monospace', color=INK, linespacing=1.35)
    fig.text(0.9 / W_IN, 3.0 / H_IN, '\n'.join(textwrap.wrap(
        'Airfoil: Selig S5010 (redesign/subsystems/wing/s5010.dat), chord %.0f mm, datum lowered %.1f mm so the spar centre is on the split face (D-194); the core stops at the hinge '
        '(x %.2f) and its lower aft face slants up from x %.1f to clear the elevon nose at %.0f deg (D-194). Upper half: x %.1f to %.2f; lower half: x 0 to %.1f.'
        % (AC.C * 1000, AC.WING_DZ * 1000, XH, XL, AC.ELEV_STOP + 6, XU0, XH, XZ0), 150)), fontsize=7.2, va='top', color=INK)


def plan_axes(fig, y_in, label):
    s = 2.5
    w, h = 2 * HALF_SPAN / s, XH / s
    ax = fig.add_axes([1.1 / W_IN, y_in / H_IN, w * MM / W_IN, h * MM / H_IN])
    ax.set_xlim(-HALF_SPAN, HALF_SPAN)
    ax.set_ylim(-XH, 0)
    ax.set_axis_off()
    fig.text(1.1 / W_IN, (y_in + h * MM + 0.42) / H_IN, label, fontsize=9.5, weight='bold', va='bottom', color=INK)
    return ax


def draw_plan(ax, half, rows, faces, note):
    xa = XU0 if half == 'U' else 0.0
    xb = XH if half == 'U' else XZ0
    ax.add_patch(Rectangle((-HALF_SPAN, -xb), 2 * HALF_SPAN, xb - xa, fc=FOAM, ec=INK, lw=0.8))
    for y in range(-450, 451, 50):
        ax.plot([y, y], [0, 4 if y % 100 else 7], color=INK, lw=0.5, clip_on=False)
        if y % 100 == 0:
            ax.text(y, 9, ('%+d' % y) if y else '0', fontsize=6.3, ha='center', color=MUTED, clip_on=False)
    for x in range(0, int(XH) + 1, 20):
        ax.plot([-HALF_SPAN - 7, -HALF_SPAN], [-x, -x], color=INK, lw=0.5, clip_on=False)
        ax.text(-HALF_SPAN - 9, -x, str(x), fontsize=6, ha='right', va='center', color=MUTED, clip_on=False)
    ax.plot([0, 0], [0, -XH], color=ACC, lw=0.6, ls=(0, (4, 2)))
    ax.plot([-HALF_SPAN, HALF_SPAN], [-AC.SPAR_X * 1000] * 2, color=ACC, lw=0.5, ls=(0, (2, 2)))
    ax.text(HALF_SPAN + 5, -AC.SPAR_X * 1000, 'spar line x %.0f' % (AC.SPAR_X * 1000), fontsize=6, va='center', color=ACC, clip_on=False)
    ax.text(HALF_SPAN + 5, 2, 'R (+y)', fontsize=7, color=INK, clip_on=False, weight='bold')
    ax.text(-HALF_SPAN - 5, 9, 'L (-y)', fontsize=7, color=INK, clip_on=False, ha='right', weight='bold')
    ax.text(-HALF_SPAN - 40, -XH / 2, 'x from LE', fontsize=6.5, rotation=90, va='center', color=MUTED, clip_on=False)
    ax.text(HALF_SPAN + 5, -XH + 4, note, fontsize=6.3, color=MUTED, clip_on=False, va='bottom', wrap=True)
    placed = []
    for r in rows:
        if r['half'] != half or r['face'] not in faces:
            continue
        for rr in (r, r.get('pair')):
            if not rr:
                continue
            pts = clip_x(rr['cut']['fp'], rr['x0'], rr['x1'])
            if len(pts) < 3:
                continue
            poly = [(max(min(p[1], HALF_SPAN), -HALF_SPAN), -p[0]) for p in pts]
            fc = THRU if rr['face'] == 'both' else ('#ffffff' if rr['type'] != 'S' else '#fff4cc')
            ax.add_patch(Polygon(poly, closed=True, fc=fc, ec=INK, lw=0.7, hatch='////' if rr['type'] == 'R' else None, zorder=3))
            cx = sum(p[0] for p in poly) / len(poly)
            cy = sum(p[1] for p in poly) / len(poly)
            for (px, py) in placed:                          # nudge labels that would overlap
                if abs(px - cx) < 16 and abs(py - cy) < 9:
                    cy -= 10
            placed.append((cx, cy))
            ax.text(cx, cy, rr['tag'], fontsize=6.4, ha='center', va='center', color=INK, weight='bold', zorder=5,
                    bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.85))


def sheet_plan(fig, half, rows):
    nm = 'UPPER' if half == 'U' else 'LOWER'
    fig.text(0.6 / W_IN, 10.55 / H_IN, '%s HALF (slab %s): where every cut goes, scale 1:2.5' % (nm, half), fontsize=14, weight='bold', va='top', color=INK)
    fig.text(0.6 / W_IN, 10.2 / H_IN, 'Both views are drawn as seen from ABOVE the finished wing (nose up the page, right wing on the right), so the numbers match the cut table. '
             'Labels are the cut-table lines. White = pocket, grey = through this half, hatched = half-round groove, yellow = slit for a lead.', fontsize=7.8, va='top', color=MUTED)
    if half == 'U':
        a1 = plan_axes(fig, 6.05, 'A. Upper half, SPLIT FACE (cut these first, the half lying skin side down; you see the face mirrored: go by R / L)')
        draw_plan(a1, 'U', rows, ('split',), 'split face')
        a2 = plan_axes(fig, 2.45, 'B. Upper half, TOP SKIN and THROUGH cuts (half lying split face down)')
        draw_plan(a2, 'U', rows, ('skin', 'both'), 'top skin')
    else:
        a1 = plan_axes(fig, 6.05, 'C. Lower half, SPLIT FACE (the half lying skin side down; the face is up, as drawn)')
        draw_plan(a1, 'L', rows, ('split',), 'split face')
        a2 = plan_axes(fig, 2.45, 'D. Lower half, BOTTOM SKIN and THROUGH cuts (half lying split face down; you see it mirrored: go by R / L)')
        draw_plan(a2, 'L', rows, ('skin', 'both'), 'bottom skin')


def fmt_y(r):
    p = r.get('pair')
    a, b = sorted((abs(r['y0']), abs(r['y1'])))
    if r['y0'] < 0 < r['y1']:
        return '%.1f to %.1f' % (r['y0'], r['y1'])
    if p:
        return 'R and L: %.1f to %.1f' % (a, b)
    return '%s: %.1f to %.1f' % ('R' if r['y0'] > 0 else 'L', a, b)


def table_rows(rows):
    out = []
    for r in rows:
        face = {'split': 'split face', 'skin': 'top skin' if r['half'] == 'U' else 'bottom skin', 'both': 'through'}[r['face']]
        if r['type'] == 'R':
            face = 'split face'
        f = r['cut']['f']
        xtxt = '%.1f to %.1f' % (r['x0'], r['x1'])
        dep = r['depth']
        if f['name'].startswith('strut slot'):
            S, E = AW.STRUT_S, AW.STRUT_E
            dep += '. Slanted: 10 wide, centre line from (x %.1f, y %.1f) to (x %.1f, y %.1f), %.1f deg off the y axis (draw it on the face with a rule)' % (
                0.0, (S[1] + (0 - S[0]) / (E[0] - S[0]) * (E[1] - S[1])) * 1000, E[0] * 1000, E[1] * 1000, math.degrees(math.atan2(E[0] - S[0], E[1] - S[1])))
        out.append((r['tag'], r['name'], face, xtxt, fmt_y(r), dep, r['type'], '2' if r.get('pair') else '1'))
    return out


def sheet_table(fig, trs, start, first):
    fig.text(0.6 / W_IN, 10.55 / H_IN, 'Cut table%s' % ('' if first else ' (continued)'), fontsize=14, weight='bold', va='top', color=INK)
    fig.text(0.6 / W_IN, 10.2 / H_IN, 'x from the leading edge, y from the centreline (R = right wing, + y), mm. Depths from the split face unless the line says skin. '
             'Do the lines in order. How: K through, P pocket, R half-round groove, S slit, H hole (sheet 1).', fontsize=7.8, va='top', color=MUTED)
    cols = [(0.6, 'line'), (1.1, 'cut (CAD name)'), (4.15, 'half: face'), (5.3, 'x from LE'), (7.1, 'y from centreline'), (8.75, 'depth / floor'), (15.55, 'how'), (16.0, 'qty')]
    y = 9.75
    for x, t in cols:
        fig.text(x / W_IN, y / H_IN, t, fontsize=7, color=MUTED, va='top', weight='bold')
    y -= 0.2
    fig.add_artist(plt.Line2D([0.6 / W_IN, 16.6 / W_IN], [y / H_IN] * 2, color=RULE, lw=0.6))
    y -= 0.07
    i = start
    while i < len(trs):
        t = trs[i]
        dl = textwrap.wrap(t[5], 98)
        nl = textwrap.wrap(t[1], 42)
        need = 0.15 * max(len(dl), len(nl)) + 0.07
        if y - need < (2.45 if first is False or True else 0.6):
            break
        vals = [t[0], None, t[0][0] + ': ' + t[2], t[3], t[4], None, t[6], t[7]]
        for (x, _), v in zip(cols, vals):
            if v is not None:
                fig.text(x / W_IN, y / H_IN, v, fontsize=6.9, va='top', color=INK, weight='bold' if x == 0.6 else 'normal')
        fig.text(1.1 / W_IN, y / H_IN, '\n'.join(nl), fontsize=6.9, va='top', color=INK, linespacing=1.3)
        fig.text(8.75 / W_IN, y / H_IN, '\n'.join(dl), fontsize=6.9, va='top', color=INK, linespacing=1.3)
        y -= need
        fig.add_artist(plt.Line2D([0.6 / W_IN, 16.6 / W_IN], [(y + 0.03) / H_IN] * 2, color='#dddddd', lw=0.4))
        i += 1
    return i


STATIONS = [(0.3, 'centre: bridge slot, saddle slot, pack tray slot'), (19.0, 'raceway groove and ditch (R; L the same)'),
            (100.0, 'servo-lead slit (R; L also has the I2C slit, see y -100)'), (-100.0, 'servo-lead and I2C slits (L)'),
            (190.0, 'servo lead run along x (R; L the same)'), (200.0, 'servo pocket, stepped (R; L the same)'),
            (230.0, 'V strut slot (R; L the same)'), (250.0, 'stop-boss pockets and balance window (R; L the same)'),
            (280.0, 'strut slot end, clamp slot, balance window (R; L the same)'), (300.0, 'strut clamp slot and balance window (R; L the same)'),
            (-300.0, 'clamp slot and I2C slit, shallow (L)'), (359.0, 'elevon-tip damper notch (R; L the same)'),
            (380.0, 'rib saddle slot and rib tube channel (R; L the same)'), (-420.0, 'pitot: tube, block, line pocket, board pocket (L only)')]


def sheet_sections(fig, tris, rows, stations, first):
    fig.text(0.6 / W_IN, 10.55 / H_IN, 'Sections, full size (1:1)%s: PRINT AT 100 %%' % ('' if first else ', continued'), fontsize=14, weight='bold', va='top', color=INK)
    fig.text(0.6 / W_IN, 10.2 / H_IN, 'Cuts through the finished core (CAD shop mesh) at the y shown, as seen from the LEFT wing tip (leading edge on the left, top skin up). '
             'Foam is shaded; white inside the outline is cut away. Blue dashed: split face. Cut a section out and hold it against the core to check depth and shape.',
             fontsize=7.6, va='top', color=MUTED)
    slots = [(0.55, 8.62 - k * 1.38) for k in range(6)] + [(8.85, 8.62 - k * 1.38) for k in range(5)]
    for (x_in, y_in), (yc, lab) in zip(slots, stations):
        ax = mm_axes(fig, x_in, y_in, 200, 32, (-8, 192), (-16, 16))
        loops = slice_y(tris, yc)
        for lp in loops:
            if len(lp) > 2:
                ax.add_patch(Polygon(lp, closed=True, fc=FOAM, ec=INK, lw=0.7))
        # holes inside the outer loop are drawn white on top (loops are filled in order of decreasing area)
        loops = sorted([l for l in loops if len(l) > 2], key=lambda l: -abs(_area(l)))
        for lp in loops[1:]:
            if _inside(lp[0], loops[0], 0.0):
                ax.add_patch(Polygon(lp, closed=True, fc='white', ec=INK, lw=0.7))
        ax.plot([-5, 190], [0, 0], color=ACC, lw=0.6, ls=(0, (4, 2)))
        tags = sorted({r['tag'] for r in rows for rr in (r, r.get('pair')) if rr and min(rr['y0'], rr['y1']) <= yc <= max(rr['y0'], rr['y1'])})
        ax.text(-8, 14.5, 'y = %+.1f   %s' % (yc, lab), fontsize=7, color=INK, weight='bold', va='bottom')
        ax.text(192, -15.5, ('lines: ' + ', '.join(tags)) if tags else '', fontsize=6.3, color=MUTED, ha='right', va='bottom')
        for x in range(0, 190, 10):
            ax.plot([x, x], [-13.6, -12.6 if x % 50 else -12.0], color=RULE, lw=0.5)
        ax.text(0, -15.5, 'x 0', fontsize=5.8, color=MUTED, va='bottom')


def _area(l):
    return 0.5 * sum(l[i - 1][0] * l[i][1] - l[i][0] * l[i - 1][1] for i in range(len(l)))


def sheet_trace(fig, cuts, start, first):
    fig.text(0.6 / W_IN, 10.55 / H_IN, 'Every CAD cut and where it is made%s' % ('' if first else ' (continued)'), fontsize=14, weight='bold', va='top', color=INK)
    fig.text(0.6 / W_IN, 10.2 / H_IN, 'All %d cuts the CAD makes in the core (wing.py, electrical.py and the shop cuts for the parts that sit in it), in CAD order. '
             '"inside" = lies inside a bigger cut (to 0.6 mm), nothing extra to do; "no foam" = the cut is above the skin or ahead of the leading edge.' % len(cuts),
             fontsize=7.6, va='top', color=MUTED)
    colx = [0.6, 8.7]
    i = start
    for cx in colx:
        y = 9.75
        while i < len(cuts):
            c = cuts[i]
            f = c['f']
            if c['status'] == 'outside':
                res = 'no foam'
            elif c['status'] == 'inside':
                h = c['host']
                res = 'inside ' + (', '.join(sorted({o['tag'] for o in h['ops']})) or h['name'])
            else:
                res = ', '.join(o['tag'] for o in c['ops'])
            txt = '%2d  %s' % (i + 1, textwrap.shorten(f['name'], 70, placeholder='...'))
            pos = 'x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f' % (f['lo'][0], f['hi'][0], f['lo'][1], f['hi'][1], f['lo'][2], f['hi'][2])
            if y < (2.5 if cx > 8 else 0.6):
                break
            fig.text(cx / W_IN, y / H_IN, txt, fontsize=6.4, va='top', color=INK)
            fig.text((cx + 0.25) / W_IN, (y - 0.13) / H_IN, pos, fontsize=5.9, va='top', color=MUTED, family='monospace')
            fig.text((cx + 7.95) / W_IN, y / H_IN, res, fontsize=6.6, va='top', color=INK, ha='right', weight='bold')
            y -= 0.31
            i += 1
    return i


def sheets(job, rev, stl_path):
    """All figures of the hand-cut set, title blocks drawn. Returns (figs, cuts, rows)."""
    cuts, rows = analyse(job)
    tris = read_stl(stl_path)
    trs = table_rows(rows)
    plan = []
    plan.append(('How to make it (overview)', '1:1.5 sketch', lambda f: sheet_overview(f, job, cuts, rows)))
    plan.append(('Templates for the halves', '1:1', sheet_templates))
    plan.append(('Upper half: where the cuts go', '1:2.5', lambda f: sheet_plan(f, 'U', rows)))
    plan.append(('Lower half: where the cuts go', '1:2.5', lambda f: sheet_plan(f, 'L', rows)))
    # table sheets
    figs, labels = [], []
    for what, sc, fn in plan:
        fig = plt.figure(figsize=(W_IN, H_IN))
        frame(fig)
        fn(fig)
        figs.append(fig)
        labels.append((what, sc))
    i, first = 0, True
    while i < len(trs):
        fig = plt.figure(figsize=(W_IN, H_IN))
        frame(fig)
        i = sheet_table(fig, trs, i, first)
        first = False
        figs.append(fig)
        labels.append(('Cut table', 'not to scale'))
    for k in range(0, len(STATIONS), 11):
        fig = plt.figure(figsize=(W_IN, H_IN))
        frame(fig)
        sheet_sections(fig, tris, rows, STATIONS[k:k + 11], k == 0)
        figs.append(fig)
        labels.append(('Sections 1:1', '1:1'))
    i, first = 0, True
    while i < len(cuts):
        fig = plt.figure(figsize=(W_IN, H_IN))
        frame(fig)
        i = sheet_trace(fig, cuts, i, first)
        first = False
        figs.append(fig)
        labels.append(('Every CAD cut, traced', 'not to scale'))
    for n, (fig, (what, sc)) in enumerate(zip(figs, labels)):
        title(fig, job, n + 1, len(figs), rev, sc, what)
    return figs, cuts, rows
