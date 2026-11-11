"""fusionkit - one CAD vocabulary for every subsystem module, many backends.

A subsystem module (redesign/subsystems/<name>/fusion/<name>.py) exposes build(ctx) and only talks to `ctx`:

    def build(ctx):
        P = ctx.local                                   # <subsystem>/params.json   (ctx.params = redesign/params/params.json)
        box = ctx.part('FUS-001')                       # name, material, mass, status come from interfaces.json
        box.box((0, -0.06, -0.06), (0.60, 0.06, 0.06))  # metres, aircraft frame: x aft, y right, z up
        bat = ctx.part('FUS-002'); bat.box(...)
        ctx.rigid('E-FUS-01', 'FUS-002', 'FUS-001', at=(0.22, 0, -0.06))   # registers interface edge E-FUS-01
        ctx.revolute('E-WNG-03', 'WNG-004', 'WNG-001', at=(...), axis='Y', limits=(-25, 25))
        ctx.wire('E-FUS-03', [(...), (...)])            # electrical edge = a routed wire, not a drawn line
        ctx.contact('E-XXX-01')                         # edge held by tape/bond already shown by geometry
        ctx.mirror('WNG-001', 'WNG-002', plane='XZ')   # right panel = mirrored left panel
        ctx.value('wing.span_m', 'm'); ctx.D('DP-SPAR')  # params.json value (unit-checked); named datum (DATUMS.md)
        ctx.keepout_cylinder('KO-PROP-UR', 'X', hub, r, half, exempt=(...))   # volume no other part may enter

Everything is recorded here as plain data (shapes in metres, joints, wires) and passed to a BACKEND as it is made:
    backends/stub_backend.py    pure python, used by check.py (seconds)
    backends/fusion_backend.py  Autodesk Fusion (adsk.core / adsk.fusion), run through build_all.py inside Fusion
    (Blender)                   redesign/blender/ - implement the Backend methods below.

Geometry is three canonical kinds so a backend implements only three builders:
    prism   : closed 2-D loops (first = outer, rest = holes) on an axis-aligned plane, extruded along the plane normal
    revolve : closed (a, r) profile revolved 360 deg about an axis-aligned line through `center`
    loft    : closed 2-D loops on parallel axis-aligned planes, lofted in order
box / cylinder / tube are built from these. Planes are axis-aligned on purpose: mirroring stays exact and every
backend can place a sketch without construction geometry. Rotate a whole component with ctx.part(..., rotate=).

Plane coordinates: a plane normal to axis N uses (u, v) = UV[N]: X -> (y, z), Y -> (x, z), Z -> (x, y).
Python 3 stdlib only.
"""
import json
import math
import os

AX = {'X': 0, 'Y': 1, 'Z': 2}
UV = {'X': (1, 2), 'Y': (0, 2), 'Z': (0, 1)}       # plane normal -> indices of (u, v)
MIRROR = {'YZ': 0, 'XZ': 1, 'XY': 2}               # mirror plane -> coordinate index that flips
JOINT_KINDS = ('rigid', 'revolute', 'slider')


# ----------------------------------------------------------------------------- small math
def to3d(axis, offset, uv):
    """Plane point (u, v) on the plane normal to `axis` at `offset` -> (x, y, z)."""
    p = [0.0, 0.0, 0.0]
    p[AX[axis]] = offset
    iu, iv = UV[axis]
    p[iu], p[iv] = uv[0], uv[1]
    return tuple(p)


def poly_area_centroid(loop):
    """Signed-area-safe shoelace: returns (area >= 0, (cu, cv))."""
    a = cx = cy = 0.0
    n = len(loop)
    for i in range(n):
        x0, y0 = loop[i]
        x1, y1 = loop[(i + 1) % n]
        c = x0 * y1 - x1 * y0
        a += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
    if abs(a) < 1e-18:
        return 0.0, (sum(p[0] for p in loop) / n, sum(p[1] for p in loop) / n)
    return abs(a) / 2.0, (cx / (3.0 * a), cy / (3.0 * a))


def revolve_volume_centroid(profile):
    """Solid of revolution of the closed (a, r) profile about the a axis: (volume, axial centroid).
    Pappus for the volume; the axial centroid is r-weighted (int a r dA / int r dA), not the profile's area centroid."""
    n = len(profile)
    s1 = s2 = 0.0                                   # signed int r dA, int a r dA (Green's theorem)
    for i in range(n):
        a0, r0 = profile[i]
        a1, r1 = profile[(i + 1) % n]
        c = a0 * r1 - a1 * r0
        s1 += c * (r0 + r1) / 6.0
        s2 += c * (a0 * r1 + 2 * a0 * r0 + 2 * a1 * r1 + a1 * r0) / 24.0
    if abs(s1) < 1e-18:
        return 0.0, sum(p[0] for p in profile) / n
    return 2 * math.pi * abs(s1), s2 / s1


def loops_area_centroid(loops):
    """Outer loop minus hole loops."""
    A, (cu, cv) = poly_area_centroid(loops[0])
    mu, mv = A * cu, A * cv
    for h in loops[1:]:
        a, (hu, hv) = poly_area_centroid(h)
        A -= a
        mu -= a * hu
        mv -= a * hv
    return A, ((mu / A, mv / A) if A > 0 else (cu, cv))


def rot_matrix(axis, deg):
    """Rotation matrix about 'X'|'Y'|'Z' or a 3-vector, right-hand rule, degrees."""
    if isinstance(axis, str):
        k = [0.0, 0.0, 0.0]
        k[AX[axis]] = 1.0
    else:
        n = math.sqrt(sum(c * c for c in axis))
        k = [c / n for c in axis]
    t = math.radians(deg)
    c, s, C = math.cos(t), math.sin(t), 1 - math.cos(t)
    x, y, z = k
    return [[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
            [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
            [z * x * C - y * s, z * y * C + x * s, c + z * z * C]]


def mat_vec(R, p):
    return tuple(sum(R[i][j] * p[j] for j in range(3)) for i in range(3))


def bbox_gap(b1, b2):
    """Distance between two axis-aligned boxes ((lo), (hi)); 0 if they touch/overlap."""
    d = [max(0.0, b2[0][i] - b1[1][i], b1[0][i] - b2[1][i]) for i in range(3)]
    return math.sqrt(sum(v * v for v in d))


def point_gap(p, b):
    return bbox_gap((p, p), b)


# ----------------------------------------------------------------------------- airfoils
def naca4_line(code, x):
    """(camber yc, half-thickness yt) of NACA 4-digit `code` at chord fraction x (0..1)."""
    m, p, t = int(code[0]) / 100.0, int(code[1]) / 10.0, int(code[2:]) / 100.0
    yt = 5 * t * (0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1015 * x ** 4)
    if m == 0 or p == 0:
        yc = 0.0
    elif x < p:
        yc = m / p ** 2 * (2 * p * x - x * x)
    else:
        yc = m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x * x)
    return yc, yt


def airfoil(code, chord, le=(0.0, 0.0), x0=0.0, x1=1.0, n=24, aft=1.0):
    """Closed NACA 4-digit loop (simplified: thickness added vertically) as 2-D points for a Y-normal plane,
    i.e. (x, z) in the aircraft frame. le = leading-edge (x, z). x0..x1 = chord fractions kept (e.g. 0..0.75 for the
    wing box, 0.75..1 for an aileron). aft=+1: chord runs towards +x (x aft frame). Order: upper x1 -> x0, then
    lower x0 -> x1, so the first and last points are the trailing-edge-side corners."""
    xs = [x0 + (x1 - x0) * (1 - math.cos(math.pi * i / n)) / 2 for i in range(n + 1)]
    up, lo = [], []
    for x in xs:
        yc, yt = naca4_line(code, x)
        up.append((le[0] + aft * x * chord, le[1] + (yc + yt) * chord))
        lo.append((le[0] + aft * x * chord, le[1] + (yc - yt) * chord))
    loop = list(reversed(up)) + (lo[1:] if x0 == 0 else lo)    # at the LE both surfaces share a point
    return loop


# ----------------------------------------------------------------------------- shapes (pure data)
class Shape:
    """kind 'prism' : axis, offset, loops, depth
       kind 'revolve': axis, center, profile [(a, r)] (a along the axis from center, r >= 0)
       kind 'loft'   : axis, sections [(offset, loop)], smooth
    All coordinates are component-local metres."""

    def __init__(self, kind, name=None, **kw):
        self.kind, self.name = kind, name
        self.__dict__.update(kw)

    # --- derived data used by check.py / build_all.py (backends do not need these)
    def points(self):
        if self.kind == 'prism':
            return [to3d(self.axis, o, uv) for o in (self.offset, self.offset + self.depth) for uv in self.loops[0]]
        if self.kind == 'loft':
            return [to3d(self.axis, o, uv) for o, loop in self.sections for uv in loop]
        k = AX[self.axis]
        rmax = max(r for _, r in self.profile)
        pts = []
        for a, _ in self.profile:
            for du in (-rmax, rmax):
                for dv in (-rmax, rmax):
                    p = list(self.center)
                    p[k] += a
                    i, j = [q for q in range(3) if q != k]
                    p[i] += du
                    p[j] += dv
                    pts.append(tuple(p))
        return pts

    def hull_points(self, n=24):
        """Points whose convex hull contains the body (component-local), for the keep-out vertex test (CR-E1-45).
        prism / loft: their vertices (exact hull of a convex section; a concave section's hull is a superset; a
        smooth loft through 3+ sections may bulge slightly past it in Fusion). revolve: each profile point swept as
        a regular n-gon circumscribing its circle (radius r / cos(pi/n)), so the hull contains the solid and is at
        most 0.9 % of r larger (n = 24), instead of the square box points() uses."""
        if self.kind != 'revolve':
            return self.points()
        k = AX[self.axis]
        i, j = [q for q in range(3) if q != k]
        s = 1.0 / math.cos(math.pi / n)
        pts = []
        for a, r in self.profile:
            for m in range(n if r > 0 else 1):
                t = 2 * math.pi * m / n
                p = list(self.center)
                p[k] += a
                p[i] += r * s * math.cos(t)
                p[j] += r * s * math.sin(t)
                pts.append(tuple(p))
        return pts

    def volume_centroid(self):
        if self.kind == 'prism':
            A, (cu, cv) = loops_area_centroid(self.loops)
            return A * abs(self.depth), to3d(self.axis, self.offset + self.depth / 2.0, (cu, cv))
        if self.kind == 'revolve':
            V, ca = revolve_volume_centroid(self.profile)
            c = list(self.center)
            c[AX[self.axis]] += ca
            return V, tuple(c)
        V, m = 0.0, [0.0, 0.0, 0.0]          # loft: trapezoidal rule between consecutive sections
        secs = [(o, loops_area_centroid([loop])) for o, loop in self.sections]
        for (o1, (a1, c1)), (o2, (a2, c2)) in zip(secs, secs[1:]):
            v = (a1 + a2) / 2.0 * abs(o2 - o1)
            p = to3d(self.axis, (o1 + o2) / 2.0, ((c1[0] + c2[0]) / 2.0, (c1[1] + c2[1]) / 2.0))
            V += v
            m = [m[i] + v * p[i] for i in range(3)]
        return V, (tuple(v / V for v in m) if V > 0 else self.points()[0])

    # --- exact transforms (keep planes axis-aligned)
    def mirrored(self, k):
        """Mirror through the coordinate plane where coordinate k = 0."""
        def m2(axis, loop):
            iu, iv = UV[axis]
            return [(-u if iu == k else u, -v if iv == k else v) for u, v in loop]
        if self.kind == 'prism':
            n = AX[self.axis] == k
            return Shape('prism', self.name, axis=self.axis, offset=-self.offset if n else self.offset,
                         depth=-self.depth if n else self.depth, loops=[m2(self.axis, l) for l in self.loops])
        if self.kind == 'loft':
            n = AX[self.axis] == k
            return Shape('loft', self.name, axis=self.axis, smooth=self.smooth,
                         sections=[(-o if n else o, m2(self.axis, l)) for o, l in self.sections])
        c = list(self.center)
        c[k] = -c[k]
        prof = [(-a, r) for a, r in self.profile] if AX[self.axis] == k else list(self.profile)
        return Shape('revolve', self.name, axis=self.axis, center=tuple(c), profile=prof)


# ----------------------------------------------------------------------------- component
class Component:
    """One physical part (one interfaces.json part id). Bodies are added with the builder methods."""

    def __init__(self, ctx, part_id, info, at=(0.0, 0.0, 0.0), rotate=None, rgb=None, cg=None, proxy=False):
        self.ctx, self.id = ctx, part_id
        self.subsystem = ctx.sub
        self.name = info.get('name', part_id)
        self.material = info.get('material')
        self.mass_g = info.get('mass_g')
        self.status = info.get('status')
        self.flight = info.get('flight', True)               # False: ground item (box, cradles), not in the roll-up
        # mass proxy: a lumped-mass stand-in (harness bundles) whose mass and CG count, but which no backend shows
        # (Fusion: hidden component named "... (mass proxy)"; Blender / GLB: an empty carrying the part's extras)
        self.proxy = bool(proxy or info.get('mass_proxy', False))
        self.make_or_buy = info.get('make_or_buy')
        self.cg_declared = cg or info.get('cg_xyz_m')
        self.rgb = rgb
        self.at = tuple(float(v) for v in at)
        self.rotate = rotate                                  # ('X'|'Y'|'Z'|vector, degrees) about `at`
        self.R = rot_matrix(*rotate) if rotate else [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self.shapes = []
        self.native = None                                    # backend handle (Fusion occurrence, Blender object)

    def matrix(self):
        """4x4 row-major local->world transform (metres)."""
        R, t = self.R, self.at
        return [R[0] + [t[0]], R[1] + [t[1]], R[2] + [t[2]], [0, 0, 0, 1]]

    def to_world(self, p):
        q = mat_vec(self.R, p)
        return tuple(q[i] + self.at[i] for i in range(3))

    def to_local(self, p):
        d = [p[i] - self.at[i] for i in range(3)]
        return tuple(sum(self.R[j][i] * d[j] for j in range(3)) for i in range(3))   # R^T d

    def _add(self, shape):
        self.shapes.append(shape)
        self.ctx.backend.body(self, shape)
        return shape

    # --- canonical builders
    def prism(self, axis, offset, loops, depth, name=None):
        """Closed loops (first outer, rest holes) on the plane normal to axis at offset; extrude by depth (signed)."""
        loops = [[tuple(map(float, p)) for p in l] for l in (loops if isinstance(loops[0][0], (list, tuple)) else [loops])]
        return self._add(Shape('prism', name, axis=axis, offset=float(offset), loops=loops, depth=float(depth)))

    def revolve(self, axis, center, profile, name=None):
        """Closed (a, r) profile, r >= 0, revolved 360 deg about the axis-aligned line through center."""
        if min(r for _, r in profile) < 0:
            raise ValueError('revolve profile radius must be >= 0')
        return self._add(Shape('revolve', name, axis=axis, center=tuple(map(float, center)),
                               profile=[tuple(map(float, p)) for p in profile]))

    def loft(self, axis, sections, smooth=False, name=None):
        """sections = [(offset, loop), ...] on planes normal to axis, in loft order. smooth=True asks the backend
        for splines (each loop drawn as a spline from first to last point + a straight closing line)."""
        return self._add(Shape('loft', name, axis=axis, smooth=smooth,
                               sections=[(float(o), [tuple(map(float, p)) for p in l]) for o, l in sections]))

    # --- convenience
    def box(self, lo, hi, name=None):
        """Axis-aligned box between corners lo and hi."""
        return self.prism('Z', lo[2], [(lo[0], lo[1]), (hi[0], lo[1]), (hi[0], hi[1]), (lo[0], hi[1])],
                          hi[2] - lo[2], name)

    def cylinder(self, axis, start, length, r, name=None):
        """Solid cylinder from point `start` along +axis (negative length = -axis)."""
        return self.tube(axis, start, length, r, 0.0, name)

    def tube(self, axis, start, length, r_out, r_in, name=None):
        a0, a1 = sorted((0.0, float(length)))
        return self.revolve(axis, start, [(a0, r_in), (a1, r_in), (a1, r_out), (a0, r_out)], name)

    def bbox(self):
        """World axis-aligned bounding box ((lo), (hi)) of all bodies."""
        pts = [self.to_world(p) for s in self.shapes for p in s.points()]
        if not pts:
            return None
        return (tuple(min(p[i] for p in pts) for i in range(3)), tuple(max(p[i] for p in pts) for i in range(3)))

    def volume_centroid(self):
        """Geometric volume (m^3) and world centroid (uniform density) of all bodies."""
        V, m = 0.0, [0.0, 0.0, 0.0]
        for s in self.shapes:
            v, c = s.volume_centroid()
            c = self.to_world(c)
            V += v
            m = [m[i] + v * c[i] for i in range(3)]
        return V, (tuple(x / V for x in m) if V > 0 else None)

    def cg(self):
        """CG used for roll-ups: declared cg_xyz_m if present, else geometric centroid. Returns (cg, source)."""
        if self.cg_declared:
            return tuple(self.cg_declared), 'declared'
        return self.volume_centroid()[1], 'geometry'


class Joint:
    def __init__(self, edge, kind, a, b, origin, axis=None, limits=None, sub=None):
        self.edge, self.kind, self.a, self.b = edge, kind, a, b      # a, b are part ids
        self.origin, self.axis, self.limits, self.sub = tuple(map(float, origin)), axis, limits, sub
        self.native = None


class Wire:
    """Routed edge: `points` = centreline polyline (touch checks, Fusion sketch); `strands` = optional list of
    (polyline, diameter) the mesh backends draw instead (each conductor of a pair in its own groove, a servo ribbon)."""

    def __init__(self, edge, points, dia, sub=None, strands=None):
        self.edge, self.points, self.dia, self.sub = edge, [tuple(map(float, p)) for p in points], dia, sub
        self.strands = [([tuple(map(float, p)) for p in pts], float(d)) for pts, d in (strands or [])]
        self.native = None


class Datum:
    """Named reference geometry every designer builds from (redesign/fusion/DATUMS.md).
    kind 'plane': axis ('X'|'Y'|'Z' = plane normal) + offset (m). kind 'point': p = (x, y, z) m.
    kind 'axis': p = a point on the line, axis = direction. `key` = the params.json key it comes from."""

    def __init__(self, name, kind, axis=None, offset=None, p=None, key='', note=''):
        self.name, self.kind, self.axis, self.key, self.note = name, kind, axis, key, note
        self.offset = None if offset is None else float(offset)
        self.p = None if p is None else tuple(map(float, p))
        self.native = None


class Keepout:
    """Volume no other part may enter (check.py: body box as a pre-filter, then the body's convex hull, CR-E1-45).
    kind 'cylinder': axis, center (world m), r, half (half-length along the axis) - e.g. a prop disc + clearance.
    kind 'halfspace': axis, at, side (+1: nothing beyond `at` in +axis, -1: nothing below) - e.g. the hover ground
    plane at the feet. `exempt` = part ids allowed inside (the prop itself, its motor, the feet)."""

    def __init__(self, name, kind, axis, exempt=(), sub=None, center=None, r=None, half=None, at=None, side=1):
        self.name, self.kind, self.axis, self.exempt, self.sub = name, kind, axis, set(exempt), sub
        self.center = None if center is None else tuple(map(float, center))
        self.r, self.half, self.at, self.side = r, half, at, side
        self.clearance = None              # set by k9.prop_keepout: the zone = swept blade volume + this on every face

    def hits(self, box):
        """True if the axis-aligned box ((lo), (hi)) enters this keep-out volume (coarse: whole bbox).
        A cylinder axis may be 'X'|'Y'|'Z' or a 3-vector (a canted prop disc, CR-E1-31b): the tilted case is solved
        exactly as a convex feasibility problem (alternating projections between the box and the cylinder)."""
        lo, hi = box
        if self.kind == 'cylinder' and not isinstance(self.axis, str):
            return self._hits_tilted(lo, hi)
        k = AX[self.axis]
        if self.kind == 'halfspace':
            return hi[k] > self.at + 1e-9 if self.side > 0 else lo[k] < self.at - 1e-9
        c = self.center
        if hi[k] <= c[k] - self.half or lo[k] >= c[k] + self.half:
            return False
        d2 = 0.0
        for i in range(3):
            if i == k:
                continue
            q = min(max(c[i], lo[i]), hi[i])          # closest point of the box to the axis, per coordinate
            d2 += (q - c[i]) ** 2
        return d2 < self.r ** 2 - 1e-12

    def _hits_tilted(self, lo, hi, iters=2000, shrink=1e-6):
        """Box vs finite cylinder of unit axis n: both are convex with exact projections (box: clamp; cylinder:
        clamp the axial coordinate to +-half and the radial vector to r), so alternating projections converge to a
        common point when they intersect and to the closest pair when they do not. The cylinder is shrunk by 1 um
        so that touching is not a hit, as in the axis-aligned test."""
        n = [float(v) for v in self.axis]
        L = math.sqrt(sum(v * v for v in n))
        n = [v / L for v in n]
        c, r, half = self.center, self.r - shrink, self.half - shrink

        def clamp_cyl(p):
            d = [p[i] - c[i] for i in range(3)]
            t = sum(d[i] * n[i] for i in range(3))
            rad = [d[i] - t * n[i] for i in range(3)]
            rr = math.sqrt(sum(v * v for v in rad))
            t = min(max(t, -half), half)
            s = 1.0 if rr <= r else r / rr
            return tuple(c[i] + t * n[i] + s * rad[i] for i in range(3))

        p = tuple(min(max(c[i], lo[i]), hi[i]) for i in range(3))
        last = None
        for _ in range(iters):
            q = clamp_cyl(p)
            p = tuple(min(max(q[i], lo[i]), hi[i]) for i in range(3))
            gap = math.sqrt(sum((p[i] - q[i]) ** 2 for i in range(3)))
            if gap < 1e-9:
                return True
            if last is not None and last - gap < 1e-13:
                return False               # stalled at a positive gap: disjoint
            last = gap
        return False

    # --- vertex (convex-hull) test, CR-E1-45: the box test above is the coarse pre-filter
    def hull_hits(self, pts, inset=0.0):
        """True if the convex hull of world points `pts` enters this keep-out shrunk by `inset` m on every face.
        Exact for convex bodies (a brace, a tube, a prism of a convex section); for a concave body the hull is a
        superset, so a hit is still conservative and a miss is certain. Touching (< 1 um) is not a hit."""
        if self.kind == 'halfspace':
            k = AX[self.axis]
            return (max(p[k] for p in pts) > self.at + inset + 1e-9 if self.side > 0
                    else min(p[k] for p in pts) < self.at - inset - 1e-9)
        r, half = self.r - inset - 1e-6, self.half - inset - 1e-6
        if r <= 0 or half <= 0:
            return False
        return _hull_cyl_dist2(pts, self.center, _unit_axis(self.axis), r, half) == 0.0

    def hull_depth(self, pts, resolution=1e-5):
        """How far the hull enters (m): the largest uniform inset of the keep-out's faces (radial and axial; for a
        half-space the plane) that the hull still enters. 0 = clear. For a prop zone with clearance c, a depth below
        c means the body is in the clearance band but not in the swept blade volume."""
        if not self.hull_hits(pts):
            return 0.0
        if self.kind == 'halfspace':
            k = AX[self.axis]
            return (max(p[k] for p in pts) - self.at) if self.side > 0 else (self.at - min(p[k] for p in pts))
        lo, hi = 0.0, min(self.r, self.half)
        while hi - lo > resolution:
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if self.hull_hits(pts, mid) else (lo, mid)
        return lo


    def core_distance(self, pts):
        """Distance (m) from the convex hull of `pts` to the keep-out less its clearance (the swept blade volume of
        a prop zone); None when no clearance is registered or for a half-space."""
        if self.kind != 'cylinder' or not self.clearance:
            return None
        d2 = _hull_cyl_dist2(pts, self.center, _unit_axis(self.axis), self.r - self.clearance,
                             self.half - self.clearance, exact=True)
        return math.sqrt(d2)


def _unit_axis(axis):
    n = [0.0, 0.0, 0.0]
    if isinstance(axis, str):
        n[AX[axis]] = 1.0
    else:
        n = [float(v) for v in axis]
    L = math.sqrt(sum(v * v for v in n))
    return [v / L for v in n]


def _hull_cyl_dist2(pts, c, n, r, half, exact=False, iters=6000, tol2=1e-14, eps=2e-6, cap_tol=2e-5):
    """Squared distance between conv(pts) and the finite cylinder (centre c, unit axis n, radius r, half-length
    half); 0.0 if they meet. Pairwise Frank-Wolfe over the hull weights (linear convergence on a polytope)
    minimising f(x) = |x - P(x)|^2 (P = projection on the cylinder; f convex, gradient 2 (x - P(x))), with exact
    line search. Stops on f <= tol2 (meet). Not exact: also stops as soon as the duality-gap lower bound f - gap is
    positive (certainly apart; the returned f is then an upper bound). exact=True: runs until the bound brackets
    the distance to eps (2 um). At the iteration cap a distance under cap_tol (20 um) counts as a meet."""
    def proj(p):
        d = [p[i] - c[i] for i in range(3)]
        t = sum(d[i] * n[i] for i in range(3))
        rad = [d[i] - t * n[i] for i in range(3)]
        rr = math.sqrt(sum(v * v for v in rad))
        t = min(max(t, -half), half)
        s = 1.0 if rr <= r else r / rr
        return [c[i] + t * n[i] + s * rad[i] for i in range(3)]

    def f_g(x):
        q = proj(x)
        g = [x[i] - q[i] for i in range(3)]
        return sum(v * v for v in g), g

    pts = [tuple(p) for p in pts]
    k0 = min(range(len(pts)), key=lambda k: f_g(pts[k])[0])
    w = {k0: 1.0}                                     # active vertex weights
    x = list(pts[k0])
    f = None
    for _ in range(iters):
        f, g = f_g(x)
        if f <= tol2:
            return 0.0
        dot = lambda k: g[0] * pts[k][0] + g[1] * pts[k][1] + g[2] * pts[k][2]
        ks = min(range(len(pts)), key=dot)            # toward vertex
        kv = max(w, key=dot)                          # away vertex (active)
        gap = 2.0 * (sum(g[i] * x[i] for i in range(3)) - dot(ks))     # FW duality gap >= f - f*
        lower = f - gap
        if not exact and lower > tol2:
            return f                                  # apart
        if exact and (gap <= 1e-18 or (lower > 0 and math.sqrt(f) - math.sqrt(lower) <= eps)):
            return f
        d = [pts[ks][i] - pts[kv][i] for i in range(3)]
        amax = w[kv]
        if sum(v * v for v in d) == 0.0:
            break
        a, b = 0.0, amax                              # exact line search on the directional derivative
        for _ in range(40):
            m = (a + b) / 2
            _, gm = f_g([x[i] + m * d[i] for i in range(3)])
            if sum(gm[i] * d[i] for i in range(3)) > 0:
                b = m
            else:
                a = m
        if a <= 0.0:
            break
        x = [x[i] + a * d[i] for i in range(3)]
        w[ks] = w.get(ks, 0.0) + a
        w[kv] -= a
        if w[kv] <= 1e-15:
            del w[kv]
    f, _ = f_g(x)
    return 0.0 if f <= cap_tol ** 2 else f


# ----------------------------------------------------------------------------- backend interface
class Backend:
    """Implement these to drive a CAD/render tool. All lengths are metres in the aircraft frame
    (x aft, y right, z up). Convert units inside the backend (Fusion: cm)."""
    name = 'abstract'

    def begin(self, title):                 # open/clear a document
        pass

    def component(self, comp):              # create an empty component placed by comp.matrix(); set comp.native
        pass

    def body(self, comp, shape):            # add one Shape (component-local coordinates) to comp
        pass

    def joint(self, joint, comp_a, comp_b):  # after all modules: rigid/revolute/slider at joint.origin (world)
        pass

    def wire(self, wire):                   # after all modules: wire.points = world polyline, wire.dia metres
        pass

    def datum(self, datum):                 # optional: named construction plane / point / axis (world metres)
        pass

    def end(self, ctx):                     # finish; return a short text summary or None
        return None


# ----------------------------------------------------------------------------- context
class Context:
    """Shared by all modules of one build. build_all.py calls begin_module() before each module's build(ctx)."""

    def __init__(self, backend, parts=None, params=None):
        self.backend = backend
        self.parts_info = parts or {}        # part id -> interfaces.json part dict
        self.params = params or {}           # redesign/params/params.json
        self.local = {}                      # <subsystem>/params.json of the module being built
        self.sub = None
        self.dir = None
        self.components = {}                 # part id -> Component
        self.joints = []
        self.wires = []
        self.contacts = {}                   # edge id -> note
        self.issues = []                     # (severity, code, item, message) found while building
        self.datums = {}                     # name -> Datum (k09kit.build_datums; DATUMS.md)
        self.keepouts = []                   # Keepout volumes registered by modules (prop discs, hover ground)
        self.envelope = None                 # ((lo), (hi)) aircraft envelope in m; check.py warns outside it

    # --- module bookkeeping
    def begin_module(self, sub, sub_dir):
        self.sub, self.dir = sub, sub_dir
        path = os.path.join(sub_dir, 'params.json')
        self.local = {}
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                self.local = json.load(f)

    def param(self, dotted):
        """ctx.param('wing.span_m') from params.json, with a clear error when missing."""
        d = self.params
        for k in dotted.split('.'):
            if not isinstance(d, dict) or k not in d:
                raise KeyError('params.json has no "%s" (needed by %s)' % (dotted, self.sub))
            d = d[k]
        return d

    def value(self, dotted, unit=None):
        """The number (or list/text) of a params.json leaf: ctx.value('wing.span_m', 'm') -> 1.15.
        params.json leaves are {value, unit, source, ...}; `unit` given -> KeyError if the leaf's unit differs
        (catches mm-vs-m before it becomes geometry)."""
        d = self.param(dotted)
        if isinstance(d, dict) and 'value' in d:
            if unit is not None and d.get('unit') != unit:
                raise KeyError('params.json "%s" is in %s, %s asked for %s' % (dotted, d.get('unit'), self.sub, unit))
            return d['value']
        return d

    # --- datums and keep-outs
    def datum(self, name, kind, **kw):
        """Register a named datum (plane / point / axis); the backend draws it (Fusion: construction geometry)."""
        if name in self.datums:
            raise ValueError('datum %s defined twice' % name)
        d = Datum(name, kind, **kw)
        self.datums[name] = d
        self.backend.datum(d)
        return d

    def D(self, name):
        """A datum's value: plane -> offset (m), point -> (x, y, z), axis -> point on the line."""
        d = self.datums.get(name)
        if d is None:
            raise KeyError('no datum %s (see redesign/fusion/DATUMS.md)' % name)
        return d.offset if d.kind == 'plane' else d.p

    def keepout_cylinder(self, name, axis, center, r, half, exempt=()):
        self.keepouts.append(Keepout(name, 'cylinder', axis, exempt, self.sub, center=center, r=r, half=half))

    def keepout_halfspace(self, name, axis, at, side=1, exempt=()):
        self.keepouts.append(Keepout(name, 'halfspace', axis, exempt, self.sub, at=at, side=side))

    def log(self, *a):
        print(*a)

    def issue(self, sev, code, item, msg):
        self.issues.append((sev, code, item, msg))

    # --- parts
    def part(self, part_id, at=(0, 0, 0), rotate=None, rgb=None, cg=None, proxy=False):
        """New component for interfaces.json part `part_id` (name/material/mass/status come from there).
        proxy=True (or "mass_proxy": true in interfaces.json): mass-only stand-in, kept in the roll-up and the checks
        but not shown by any backend (Component.proxy)."""
        if part_id in self.components:
            raise ValueError('component %s already built by %s' % (part_id, self.components[part_id].subsystem))
        info = self.parts_info.get(part_id)
        if info is None:
            self.issue('ERROR', 'unknown-part', part_id, 'built by %s but not declared in any interfaces.json' % self.sub)
            info = {}
        c = Component(self, part_id, info, at, rotate, rgb, cg, proxy)
        self.components[part_id] = c
        self.backend.component(c)
        return c

    def mirror(self, src_id, new_id, plane='XZ', at=0.0, rgb=None):
        """New component new_id = src_id mirrored through `plane` ('XZ' flips y) located at coordinate `at`."""
        src = self.components[src_id]
        if src.rotate:
            raise ValueError('mirror() needs an unrotated source component (%s)' % src_id)
        k = MIRROR[plane]
        t = list(src.at)
        t[k] = 2 * at - t[k]
        c = self.part(new_id, at=t, rgb=rgb or src.rgb, proxy=src.proxy)
        for s in src.shapes:
            c._add(s.mirrored(k))
        return c

    # --- registrations of interfaces.json edges (realised after all modules ran)
    def rigid(self, edge, a, b, at):
        self.joints.append(Joint(edge, 'rigid', a, b, at, sub=self.sub))

    def revolute(self, edge, a, b, at, axis, limits=None):
        """Part a turns about `axis` ('X'|'Y'|'Z' in b's frame) through world point `at`; limits in degrees."""
        self.joints.append(Joint(edge, 'revolute', a, b, at, axis, limits, sub=self.sub))

    def slider(self, edge, a, b, at, axis, limits=None):
        """limits in metres."""
        self.joints.append(Joint(edge, 'slider', a, b, at, axis, limits, sub=self.sub))

    def contact(self, edge, note=''):
        """Edge held by bond/tape/strap/thermal pad that the geometry already shows touching; no CAD joint."""
        self.contacts[edge] = (note, self.sub)

    def wire(self, edge, points, dia=0.004, strands=None):
        """Electrical edge as a routed wire: world polyline from part_a's connector to part_b's connector.
        strands = [(polyline, diameter), ...]: what mesh backends draw (default: the polyline at `dia`)."""
        self.wires.append(Wire(edge, points, dia, sub=self.sub, strands=strands))

    def finish(self):
        """Realise joints and wires in the backend once every module has built its components."""
        for j in self.joints:
            ca, cb = self.components.get(j.a), self.components.get(j.b)
            if ca is None or cb is None:
                self.issue('ERROR', 'joint', j.edge, '%s joint needs components %s and %s; missing %s' % (
                    j.kind, j.a, j.b, ', '.join(p for p, c in ((j.a, ca), (j.b, cb)) if c is None)))
                continue
            try:
                self.backend.joint(j, ca, cb)
            except Exception as e:
                self.issue('ERROR', 'joint', j.edge, 'backend: %s' % e)
        for w in self.wires:
            try:
                self.backend.wire(w)
            except Exception as e:
                self.issue('ERROR', 'wire', w.edge, 'backend: %s' % e)

    # --- registration lookup used by check.py
    def registrations(self):
        """edge id -> list of (kind, object): kind in rigid|revolute|slider|contact|wire."""
        reg = {}
        for j in self.joints:
            reg.setdefault(j.edge, []).append((j.kind, j))
        for e, n in self.contacts.items():
            reg.setdefault(e, []).append(('contact', n))
        for w in self.wires:
            reg.setdefault(w.edge, []).append(('wire', w))
        return reg

    def rollup(self):
        """Declared mass and CG (declared, else geometric) over all flight components -> (mass_g, cg or None).
        Parts with "flight": false (transport box, cradles, fixtures) are left out, as in merge_check."""
        M, m = 0.0, [0.0, 0.0, 0.0]
        for c in self.components.values():
            if not c.flight:
                continue
            cg, _ = c.cg()
            if c.mass_g and cg:
                M += c.mass_g
                m = [m[i] + c.mass_g * cg[i] for i in range(3)]
        return M, (tuple(v / M for v in m) if M else None)
