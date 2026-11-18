"""amodel/electrical.py - LANE C (avionics, power, mechanisms, harness, hardware): pack (PWR-001) + strap (PWR-002), avionics plate +
FC stack / RX / GPS / airspeed / pitot (AVN-*), servos / arms / pushrods / horns (MEC-*), landing feet (GER-*, kept here so the
PARTS/EDGES registration order stays identical), harness wires (real gauges), XT60 female + tail (HRN-002), modelled hardware sets
(HWC-*), the remaining lumps (HRN-001, HRD-001), electrical edges, and builders build_power / build_avionics / build_mechanisms /
build_landing / build_harness / build_assembly (the generic joint pass over EDGES). Lane C also owns gen_interfaces.py.

CAD FIDELITY ROUND (2026-11-15, QP-5 CAD-FIDELITY-AUDIT.md lane C). Source labels in comments:
  V  = vendor page read 2026-11-15 (URL given); DOC = repo document; CALC = computed here; ISO = standard value;
  EST = estimate / CAD interpretation, NOT published: every EST dimension is "measure on arrival" and is listed in the lane C report;
  "-" = not published, not drawn.
Lane C edits only this file. It reads shared constants from common.py (PACK_X, TRIM, TRAY_X1, SERVO_Y, SV_Z1, PLATE_*/ZP, FIN_*,
YFIN, XFIN_T, ELEV_POSE ...) and imports ESC_PADS / ESC_TOP from propulsion.py (lane B): every wire route that ends on the ESC uses
those names, so moving the ESC pads moves the routes. IMPORT ORDER MATTERS: amodel/__init__.py imports wing, propulsion,
electrical in that order.
"""
import math

from .common import *   # noqa: F401,F403
from .wing import BR_Z, BR_RO, HINGE_Z, RHO_PETG, TUBE_RO, TUBE_RI, TUBE_HL, SLV_L, SLV_R, DBL_S0, DBL_S1, DBL_RO, HOLE_S, HOLE_R, STN_S   # noqa: F401  (read only: hinge axis height for the horn hole radius; D-202 tube / hub geometry)
from .propulsion import ESC_PADS, ESC_TOP   # noqa: F401  (harness wires land on the ESC pads; lane B owns them)

MM = 0.001


# ------------------------------------------------------------------ small geometry helpers (2-D loops, 3-D vectors)
def _ring(cx, cy, r, n=14, ph=0.0):
    return [(cx + r * math.cos(ph + 2 * math.pi * i / n), cy + r * math.sin(ph + 2 * math.pi * i / n)) for i in range(n)]


def _rrect(x0, y0, x1, y1, r, n=4):
    """Counter-clockwise rounded rectangle."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _hex(cx, cy, af, ph=math.pi / 6):
    return _ring(cx, cy, af / math.sqrt(3), 6, ph)


def _sub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def _add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def _mul(a, k):
    return tuple(a[i] * k for i in range(3))


def _dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a):
    n = math.sqrt(_dot(a, a))
    return tuple(c / n for c in a)


def _strands(P, d, offs):
    """Round strands of diameter d laid along polyline P. offs: list of (a, b) offsets (m) along (side, up), constant, or a list of (a, b)
    per vertex. Rotation-minimising frame per segment; each corner is MITRED (the two offset lines are intersected), so strands of one
    bundle keep their spacing round a bend (D-194: the old per-vertex offsets let strands cross by 0.4-0.5 mm at corners).
    Returns [(polyline, d), ...] for ctx.wire(strands=)."""
    n = len(P)
    segs = [_unit(_sub(P[i + 1], P[i])) for i in range(n - 1)]
    ref = (0.0, 0.0, 1.0) if abs(segs[0][2]) < 0.9 else (1.0, 0.0, 0.0)
    side = _unit(_cross(ref, segs[0]))
    fr = [(side, _cross(segs[0], side))]
    for i in range(1, n - 1):
        e0, e1 = segs[i - 1], segs[i]
        ax = _cross(e0, e1)
        if _dot(ax, ax) < 1e-12:
            fr.append(fr[-1])
            continue
        ax = _unit(ax)
        cth, sth = _dot(e0, e1), _dot(_cross(e0, e1), ax)

        def rot(v):          # Rodrigues rotation about ax by the bend angle
            return _add(_add(_mul(v, cth), _mul(_cross(ax, v), sth)), _mul(ax, _dot(ax, v) * (1 - cth)))
        sd = rot(fr[-1][0])
        fr.append((sd, _cross(e1, sd)))
    out = []
    for o in offs:
        off = []
        for i in range(n - 1):
            a_, b_ = o[i] if isinstance(o, list) else o
            off.append(_add(_mul(fr[i][0], a_), _mul(fr[i][1], b_)))
        line = [_add(P[0], off[0])]
        for i in range(1, n - 1):
            q1, q2 = _add(P[i], off[i - 1]), _add(P[i], off[i])
            e0, e1 = segs[i - 1], segs[i]
            w = _sub(q2, q1)
            c = _dot(e0, e1)
            den = 1 - c * c
            if den < 1e-9:
                line.append(q1)
                continue
            sct = (_dot(w, e0) - c * _dot(w, e1)) / den       # q1 + s e0 meets q2 + u e1 (coplanar for a rotation-minimising frame)
            line.append(_add(q1, _mul(e0, sct)))
        line.append(_add(P[-1], off[-1]))
        out.append((line, d))
    return out


# ------------------------------------------------------------------ D-199 smooth wire geometry (silicone wire as installed, not mitred rods)
def _smooth(P, R=0.006, step=0.003, sag=None):
    """Waypoints -> dense centre line. Every interior corner is rounded with a circular arc of radius R (scalar or one value per interior vertex),
    limited so the two tangent lengths of a leg never exceed 90 % of it; straight legs are subdivided to <= step; sag = {leg index: (amount m, unit
    direction)} adds a gentle drape sin(pi s) * amount to a free leg. Returns (points, effective radii of the corners)."""
    n = len(P)
    Rl = list(R) if isinstance(R, (list, tuple)) else [R] * (n - 2)
    u = [_unit(_sub(P[i + 1], P[i])) for i in range(n - 1)]
    L = [math.dist(P[i], P[i + 1]) for i in range(n - 1)]
    ang, t = [0.0] * n, [0.0] * n
    for i in range(1, n - 1):
        c = max(-1.0, min(1.0, _dot(u[i - 1], u[i])))
        ang[i] = math.acos(c)
        t[i] = Rl[i - 1] * math.tan(ang[i] / 2) if ang[i] > 1e-3 else 0.0
    for _ in range(3):
        for i in range(1, n - 1):
            lim_a = 0.5 * L[i - 1] if i > 1 else 0.9 * L[i - 1]
            lim_b = 0.5 * L[i] if i < n - 2 else 0.9 * L[i]
            t[i] = min(t[i], lim_a, lim_b)
    reff = [(t[i] / math.tan(ang[i] / 2)) if ang[i] > 1e-3 and t[i] > 0 else 9.0 for i in range(1, n - 1)]
    out = [P[0]]
    for i in range(0, n - 1):
        a0 = _sub(P[i], _mul(u[i - 1], 0)) if i == 0 else None
        s0 = P[i] if i == 0 else _add(P[i], _mul(u[i], t[i]))
        s1 = P[i + 1] if i == n - 2 else _sub(P[i + 1], _mul(u[i], t[i + 1]))
        ln = math.dist(s0, s1)
        k = max(1, int(math.ceil(ln / step)))
        amt, dr = (sag or {}).get(i, (0.0, (0, 0, -1)))
        for q in range(1, k + 1):
            f = q / k
            pt = _add(s0, _mul(_sub(s1, s0), f))
            if amt and q < k:
                pt = _add(pt, _mul(dr, amt * math.sin(math.pi * f)))
            out.append(pt)
        if i + 1 < n - 1 and t[i + 1] > 0:                    # arc round vertex i + 1
            j = i + 1
            A = _sub(P[j], _mul(u[j - 1], t[j]))
            perp = _unit(_sub(u[j], _mul(u[j - 1], _dot(u[j], u[j - 1]))))
            r = t[j] / math.tan(ang[j] / 2)
            C = _add(A, _mul(perp, r))
            m = max(2, int(math.ceil(ang[j] / 0.15)))
            for q in range(1, m + 1):
                th = ang[j] * q / m
                out.append(_add(C, _add(_mul(perp, -r * math.cos(th)), _mul(u[j - 1], r * math.sin(th)))))
    return out, reff


def _strands_s(P, d, offs, lay=None, th0=0.0):
    """Strands of diameter d along the smooth dense line P (parallel-transport frame, no mitring). offs = [(a, b)] constant offsets (side, up) m;
    lay = lay length (m) of a light twist: the offsets rotate once per lay length (phase-lead triples as tied / heat-shrunk). -> [(polyline, d)]"""
    n = len(P)
    T = []
    for i in range(n):
        a = P[max(i - 1, 0)]
        b = P[min(i + 1, n - 1)]
        T.append(_unit(_sub(b, a)))
    ref = (0.0, 0.0, 1.0) if abs(T[0][2]) < 0.9 else (1.0, 0.0, 0.0)
    N = _unit(_cross(ref, T[0]))
    fr = [(N, _cross(T[0], N))]
    for i in range(1, n):
        Ni = _sub(fr[-1][0], _mul(T[i], _dot(fr[-1][0], T[i])))
        Ni = _unit(Ni)
        fr.append((Ni, _cross(T[i], Ni)))
    sacc = [0.0]
    for i in range(1, n):
        sacc.append(sacc[-1] + math.dist(P[i], P[i - 1]))
    out = []
    for a_, b_ in offs:
        line = []
        for i in range(n):
            th = th0 + (2 * math.pi * sacc[i] / lay if lay else 0.0)
            ca, sa = math.cos(th), math.sin(th)
            aa, bb = a_ * ca - b_ * sa, a_ * sa + b_ * ca
            line.append(_add(P[i], _add(_mul(fr[i][0], aa), _mul(fr[i][1], bb))))
        out.append((line, d))
    return out


def _slen(line):
    return sum(math.dist(line[i], line[i + 1]) for i in range(len(line) - 1))


def _terms(ctx, eid, margin=0.0003):
    """Solder joint / crimp block (EST) on the host part at each strand end of the wire just registered, so the strand ends sit in a part
    (a wire end must be seated). Block = strand diameter + 2 x margin, centred on the end point."""
    w = ctx.wires[-1]
    ed = [e for e in EDGES if e['id'] == eid][0]
    pa, pb = ed['part_a'], ed['part_b']
    for line, d in (w.strands or [(w.points, w.dia)]):
        for pt in (line[0], line[-1]):
            def _dist(pid):                                  # distance from the end point to the part's world bounding box
                (l0, l1) = ctx.components[pid].bbox()
                return math.sqrt(sum(max(l0[k] - pt[k], 0.0, pt[k] - l1[k]) ** 2 for k in range(3)))
            host = pa if _dist(pa) <= _dist(pb) else pb
            h = ctx.components.get(host)
            if h is None:
                continue
            r = d / 2 + margin
            pt = h.to_local(pt)
            h.box((pt[0] - r, pt[1] - r, pt[2] - r), (pt[0] + r, pt[1] + r, pt[2] + r), name='solder joint / crimp at the wire end (EST)')


def _tri(d):
    r = d / math.sqrt(3)
    return [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in (90, 210, 330)]


def _legs(part, P, d, name, ext=True):
    """Round wire body along an axis-aligned polyline P (cylinders; interior ends extended by the radius so corners close)."""
    r = d / 2
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        k = [j for j in range(3) if abs(b[j] - a[j]) > 1e-9]
        assert len(k) == 1, 'wire leg not axis-aligned'
        k = k[0]
        s = 1.0 if b[k] > a[k] else -1.0
        p0, p1 = list(a), list(b)
        if ext and i > 0:
            p0[k] -= s * r
        if ext and i < len(P) - 2:
            p1[k] += s * r
        part.cylinder('XYZ'[k], tuple(p0), p1[k] - p0[k], r, name=name)


def _pcb(part, x0, y0, x1, y1, z0, t, holes=(), hole_r=1.1 * MM, r=1.0 * MM, name='PCB'):
    loops = [_rrect(x0, y0, x1, y1, r, 3)] + [_ring(hx, hy, hole_r, 12) for hx, hy in holes]
    part.prism('Z', z0, loops, t, name=name)


def _pad(part, x, y, z, name, s=1.6 * MM, h=0.25 * MM):
    part.box((x - s / 2, y - s / 2, z), (x + s / 2, y + s / 2, z + h), name=name)


RHO_STEEL, RHO_PA66, RHO_BRASS = 7.9, 1.14, 8.5          # g/cm3 ISO / catalogue (A2 stainless 7.9, nylon PA66 1.14)


def _g_screw(d, L, dk, k, rho=RHO_STEEL):
    """CALC: pan-head screw mass g (shank + 0.85 x head disc for the dome and recess)."""
    return rho * (math.pi / 4 * d * d * L + 0.85 * math.pi / 4 * dk * dk * k) * 1e6


def _g_nut(af, m, d, rho=RHO_STEEL):
    return rho * ((math.sqrt(3) / 2 * af * af - math.pi / 4 * d * d) * m) * 1e6


# ------------------------------------------------------------------ D-198 bay cover (AVN-008) and servo-lead grooves
COV_X0, COV_X1 = 0.0225, 0.1265             # cover roof from the tray end to just ahead of the plate end (plate x 40.8..127.0)
COV_Y = 0.0265                              # half width: clear of the GPS board (y >= 27.5) with a 0.6 mm wall
COV_T = 0.0006                              # printed single wall 0.6 mm (same basis as the lens caps WNG-008, EST)
COV_ZH1, COV_ZH2 = 0.0450, 0.0325           # roof heights: over the FC stack (screw heads to 38.5, sensor leads at 40.5 +- 0.5) and over the ESC with the phase bundles (z 29)
SRV_YD = 0.024                              # servo leads drop through the plate window (x 80..122, y 21..40) at |y| 24 mm
SRV_XD = 0.083
SRV_YG = 0.190                              # groove end: 10 mm inboard of the servo centre line
RHO_PETG_ = 1.27


def cov_outer():
    """Roof outer profile (x, z) from the skin at the front, ramp, flat over the FC, step, flat over the ESC, aft wall down to the plate."""
    return [(COV_X0, zu(COV_X0)), (0.040, COV_ZH1), (0.080, COV_ZH1), (0.0833, COV_ZH2), (COV_X1, COV_ZH2), (COV_X1, ZP)]


def cov_loops():
    o = cov_outer()
    i = [(o[0][0] + 0.0012, zu(COV_X0 + 0.0012))] + [(x, z - COV_T) for x, z in o[1:-2]] + [(o[-2][0] - COV_T, o[-2][1] - COV_T), (COV_X1 - COV_T, ZP)]
    return o + i[::-1]


def cov_side_loop():
    """End wall: region under the roof outer line, down to the skin (ahead of the plate) and the plate top (over it)."""
    o = cov_outer()
    bot = [(COV_X1, ZP), (PLATE_X0, ZP), (PLATE_X0, zu(PLATE_X0))] + [(COV_X0 + (PLATE_X0 - COV_X0) * (1 - k / 4.0), zu(COV_X0 + (PLATE_X0 - COV_X0) * (1 - k / 4.0))) for k in range(1, 5)]
    return o[:-1] + bot[:-1] if False else o + [(PLATE_X0, ZP), (PLATE_X0, zu(PLATE_X0))] + [(COV_X0 + (PLATE_X0 - COV_X0) * k / 4.0, zu(COV_X0 + (PLATE_X0 - COV_X0) * k / 4.0)) for k in range(3, 0, -1)][::-1][::-1]


def _poly_area_(l):
    return sum(l[i][0] * l[(i + 1) % len(l)][1] - l[(i + 1) % len(l)][0] * l[i][1] for i in range(len(l))) / 2


def cover_mass_g():
    arch = abs(_poly_area_(cov_loops())) * (2 * COV_Y)
    wall = abs(_poly_area_(cov_side_loop())) * COV_T * 2
    return round((arch + wall) * 1e6 * RHO_PETG_, 1)


def servo_zc(x):
    return max(zu(x) - 0.0030, 0.0073)


# ------------------------------------------------------------------ D-199 phase-lead raceway parts (constants in common.py); D-202 hub conduits
# D-202: each phase-lead bundle leaves its arm tube through the 4.8 mm hole at s = +-18 mm (wing.py HOLE_S), enters a printed conduit HRN-004-<station> that hugs the hub sleeve
# (the sleeve and tube are seat cuts in it), rises 12 mm along the hole axis (t), runs aft along x at (y1, z1) clear of the hub, steps sideways to its raceway lane (y), and drops
# (upper arms, from above) or rises (lower arms, from below) at x = XV through a window in the raceway wall into HRN-003. The lower-arm holes are on the -t face (see D-202 CAD note):
# on the +t face the lead would leave at z -3 mm, level with the strut socket boss CGE-001 (x -65.8..-52, |z| <= 3.8, y >= 21 mm), which blocks every aft route at lane height.
CD_HW = 0.0026                              # conduit interior half width: bundle envelope radius 1.94 mm + 0.66 mm clearance (EST)
CD_T = RW_T                                 # conduit wall 0.6 mm (EST, as the raceway)
CD_TT = 0.012                               # bundle height above the tube axis at the top of the chimney (t, m)
CD_FL = 0.0064                              # conduit outer floor at t = 6.4 mm (inside the sleeve where the sleeve is: seat cut); interior from t = 7.0 mm
CD_UOFF = 0.0004                            # the bundle leaves the tube 0.4 mm inboard of the hole axis (u), so that its 4 mm bend (which hugs the outboard side) is centred in the 4.8 mm hole
CD_XCUT = 0.0045                            # the sideways step starts 4.5 mm ahead of the drop column (corner arcs of the bundle, r 4 mm)
XV = -0.053 + CD_DX                         # D-205: 3.8 mm aft (common.CD_DX); x of the drop column (bundle centre line)
XVH = XV + 0.0035                           # +x limit of the column interior (the 6 mm bend into the raceway swings the bundle 0.6..1.0 mm aft while it crosses the wall; strand radius 0.9)
CD_WX = (XV - CD_HW, XVH)           # raceway window x range (the 6 mm bend of the bundle moves it 0.6..1.0 mm aft over the wall thickness)


def _cd_ut_yz(phi_deg, u, t):
    a = math.radians(phi_deg)
    return (u * math.cos(a) - t * math.sin(a), u * math.sin(a) + t * math.cos(a))


def cd_spec(st):
    """Geometry of conduit st (world metres): rotated-rectangle chimney + aft run (prism along x), corner box (sideways step), drop column, as outer and interior pieces."""
    T = TUBE_OF[st]
    xt, phi, sg, sig = TUBE_X[T], TUBE_PHI[T], STN_S[st], SIG[st]
    sy, sz = ST[st]
    u0 = sg * HOLE_S
    hw, w = CD_HW, CD_T
    y1, z1 = _cd_ut_yz(phi, u0, sig * CD_TT)
    yl = sy * (RW_YU if sz > 0 else RW_YL)
    t0o, t1o = sig * CD_FL, sig * (CD_TT + hw + w)
    t0i, t1i = sig * 0.0070, sig * (CD_TT + hw)
    po = [_cd_ut_yz(phi, u, t) for u, t in ((u0 - hw - w, t0o), (u0 + hw + w, t0o), (u0 + hw + w, t1o), (u0 - hw - w, t1o))]
    pi_ = [_cd_ut_yz(phi, u, t) for u, t in ((u0 - hw, t0i), (u0 + hw, t0i), (u0 + hw, t1i), (u0 - hw, t1i))]
    ya, yb = sorted((y1, yl))
    xr = XV - CD_XCUT
    up = sz > 0
    col_o_z = (RW_ZO[1], z1 + hw + w) if up else (z1 - hw - w, RW_ZO[0])
    col_i_z = (RW_ZO[1] - 0.0001, z1 + hw) if up else (z1 - hw, RW_ZO[0] + 0.0001)
    return dict(T=T, xt=xt, phi=phi, y1=y1, z1=z1, yl=yl, u0=u0, sig=sig,
                run_o=(po, xt - hw - w, xr), run_i=(pi_, xt - hw, xr + 0.0010),
                cor_o=((xr - w, ya - hw - w, z1 - hw - w), (XVH + w, yb + hw + w, z1 + hw + w)), cor_i=((xr, ya - hw, z1 - hw), (XVH, yb + hw, z1 + hw)),
                col_o=((XV - hw - w, yl - hw - w, col_o_z[0]), (XVH + w, yl + hw + w, col_o_z[1])), col_i=((XV - hw, yl - hw, col_i_z[0]), (XVH, yl + hw, col_i_z[1])))


CD = {st: cd_spec(st) for st in ST}


def _cd_masks(st, X, Y, Z):
    """Boolean arrays (outer union, interior union) of conduit st on points X, Y, Z (numpy)."""
    import numpy as np
    c = CD[st]
    out = np.zeros(X.shape, dtype=bool)
    inn = np.zeros(X.shape, dtype=bool)
    cp, sp = math.cos(math.radians(c['phi'])), math.sin(math.radians(c['phi']))
    U, Tt = Y * cp + Z * sp, -Y * sp + Z * cp
    hw, w, sig = CD_HW, CD_T, c['sig']
    for key, (a_lo, a_hi, t_lo, t_hi) in (('o', (c['u0'] - hw - w, c['u0'] + hw + w, CD_FL, CD_TT + hw + w)), ('i', (c['u0'] - hw, c['u0'] + hw, 0.0070, CD_TT + hw))):
        x0, x1 = (c['run_o'][1], c['run_o'][2]) if key == 'o' else (c['run_i'][1], c['run_i'][2])
        m = (X >= x0) & (X <= x1) & (U >= a_lo) & (U <= a_hi) & (sig * Tt >= t_lo) & (sig * Tt <= t_hi)
        if key == 'o':
            out |= m
        else:
            inn |= m
    for kk in ('cor', 'col'):
        for key in ('o', 'i'):
            lo, hi = c[kk + '_' + key]
            m = (X >= lo[0]) & (X <= hi[0]) & (Y >= lo[1]) & (Y <= hi[1]) & (Z >= lo[2]) & (Z <= hi[2])
            if key == 'o':
                out |= m
            else:
                inn |= m
    return out, inn


def cd_interior(st, p):
    import numpy as np
    return bool(_cd_masks(st, np.array([p[0]]), np.array([p[1]]), np.array([p[2]]))[1][0])


def cd_mass_g(st, h=0.0002):
    """Drawn conduit mass: (outer union - interior union - the sleeve, tube and doubler the conduit hugs) x 1.27, integrated on a grid of pitch h."""
    import numpy as np
    c = CD[st]
    lo = [c['run_o'][1]] + [min(c[k][0][i] for k in ('cor_o', 'col_o')) for i in (1, 2)]
    pts = [q for q in c['run_o'][0]]
    ys = [q[0] for q in pts] + [c['cor_o'][0][1], c['cor_o'][1][1], c['col_o'][0][1], c['col_o'][1][1]]
    zs = [q[1] for q in pts] + [c['cor_o'][0][2], c['cor_o'][1][2], c['col_o'][0][2], c['col_o'][1][2]]
    xs = np.arange(c['run_o'][1] + h / 2, c['col_o'][1][0], h)
    yy = np.arange(min(ys) + h / 2, max(ys), h)
    zz = np.arange(min(zs) + h / 2, max(zs), h)
    Y, Z = np.meshgrid(yy, zz, indexing='ij')
    cp, sp = math.cos(math.radians(c['phi'])), math.sin(math.radians(c['phi']))
    U, Tt = Y * cp + Z * sp, -Y * sp + Z * cp
    tot = 0
    for x in xs:
        X = np.full(Y.shape, x)
        o, i_ = _cd_masks(st, X, Y, Z)
        d2 = Tt * Tt + (x - c['xt']) ** 2
        hub = ((np.abs(U) <= SLV_L) & (d2 <= SLV_R ** 2)) | (d2 <= TUBE_RO ** 2) | ((np.abs(U) >= DBL_S0) & (np.abs(U) <= DBL_S1) & (d2 <= DBL_RO ** 2))
        tot += int(np.count_nonzero(o & ~i_ & ~hub))
    return tot * h ** 3 * 1e6 * RHO_PETG


def _rect_loop(a0, a1, b0, b1):
    return [(a0, b0), (a1, b0), (a1, b1), (a0, b1)]


def _area(l):
    return abs(_poly_area_(l))


def raceway_mass_g():
    wall = (RW_YO[1] - RW_YO[0]) * (RW_ZO[1] - RW_ZO[0]) - (RW_YI[1] - RW_YI[0]) * (RW_ZI[1] - RW_ZI[0])
    v = wall * (RW_X1 - RW_XI0) + (RW_YO[1] - RW_YO[0]) * (RW_ZO[1] - RW_ZO[0]) * (RW_XI0 - RW_XO0)
    v -= 2 * (CD_WX[1] - CD_WX[0]) * (2 * CD_HW) * RW_T          # windows for the upper and the lower bundle (D-202)
    return round(v * 1e6 * RHO_PETG, 2)


def hubhop_mass_g(st):
    return round(cd_mass_g(st), 2)


def enclosure_class(p):
    """'ARM' if the point is inside an arm tube bore or its 4.8 mm exit hole, 'RACE' if inside a printed raceway / hub conduit interior, 'GROOVE' in the foam ditch, else None
    (D-199, D-202). Mirror-symmetric in y for the raceway and ditch."""
    x, y, z = p
    ya = abs(y)
    e = 5e-5
    if RW_XI0 - e <= x <= RW_X1 + e and RW_YI[0] - e <= ya <= RW_YI[1] + e and RW_ZI[0] - e <= z <= RW_ZI[1] + e:
        return 'RACE'
    for st in ST:
        if cd_interior(st, p):
            return 'RACE'
    for st in ST:                                    # tube bore and exit hole
        T, sg, sig = TUBE_OF[st], STN_S[st], SIG[st]
        a = math.radians(TUBE_PHI[T])
        u, t = y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a)
        dx = x - TUBE_X[T]
        if dx * dx + t * t <= (TUBE_RI + e) ** 2 and abs(u) <= TUBE_HL:
            return 'ARM'
        if dx * dx + (u - sg * HOLE_S) ** 2 <= (HOLE_R + e) ** 2 and 0.0045 <= sig * t <= 0.0100:
            return 'ARM'
    if RW_X1 < x <= DITCH_X1 + e and RW_YI[0] - e <= ya <= RW_YI[1] + e and RW_ZI[0] - e <= z < zu(x):
        return 'GROOVE'
    return None


def build_raceway(ctx):
    """HRN-003-R / -L: closed printed channel under the tray plate; HRN-004-<station>: hub conduits (D-199, D-202)."""
    rw = ctx.part('HRN-003-R', rgb=(0.95, 0.75, 0.2))
    rw.prism('X', RW_XI0, [_rect_loop(RW_YO[0], RW_YO[1], RW_ZO[0], RW_ZO[1]), _rect_loop(RW_YI[0], RW_YI[1], RW_ZI[0], RW_ZI[1])], RW_X1 - RW_XI0, name='phase-lead raceway, 0.6 mm walls, closed section (D-199)')
    rw.box((RW_XO0, RW_YO[0], RW_ZO[0]), (RW_XI0, RW_YO[1], RW_ZO[1]), name='raceway front wall (D-199)')
    rw.cut_box((CD_WX[0], RW_YI[0], RW_ZI[1] - 0.0001), (CD_WX[1], RW_YU + CD_HW, RW_ZO[1] + 0.0001), name='window for the upper bundle drop (D-202)')
    rw.cut_box((CD_WX[0], RW_YL - CD_HW, RW_ZO[0] - 0.0001), (CD_WX[1], RW_YI[1], RW_ZI[0] + 0.0001), name='window for the lower bundle rise (D-202)')
    ctx.mirror('HRN-003-R', 'HRN-003-L', plane='XZ')
    for st in ST:
        c = CD[st]
        h = ctx.part('HRN-004-' + st, rgb=(0.95, 0.75, 0.2))
        po, x0o, x1o = c['run_o']
        pi_, x0i, x1i = c['run_i']
        h.prism('X', x0o, [po], x1o - x0o, name='hub conduit chimney and aft run, outer (D-202)')
        h.box(c['cor_o'][0], c['cor_o'][1], name='hub conduit sideways step, outer (D-202)')
        h.box(c['col_o'][0], c['col_o'][1], name='hub conduit drop column, outer (D-202)')
        h.cut_prism('X', x0i, [pi_], x1i - x0i, name='conduit chimney and run interior (D-202)')
        h.cut_box(c['cor_i'][0], c['cor_i'][1], name='conduit step interior (D-202)')
        h.cut_box(c['col_i'][0], c['col_i'][1], name='conduit column interior, open to the raceway window (D-202)')
        ctx.seat('HRN-004-' + st, 'CGE-001', 'conduit floor hugs the hub sleeve (D-202)')
        sy_ = 1 if c.get('y1', 1) >= 0 else -1
        yr = sorted((sy_ * 0.0136, sy_ * 0.0400))
        h.cut_box((HUB[0] + 0.024 - 0.0012, yr[0], 0.003), (HUB[0] + 0.024, yr[1], 0.011),
                  name='relief beside the tray pad flange (D-208: keeps the D-202 conduit shape the old 80 mm flange cut, so the conduit still slides past the flange corner)')
        ctx.seat('HRN-004-' + st, 'CGE-002-' + c['T'], 'conduit floor over the arm tube (D-202)')
        ctx.seat('HRN-004-' + st, 'CGE-009-' + st, 'conduit floor over the doubler (D-202)')


# ------------------------------------------------------------------ lane C constants (m)
PACK_L, PACK_W, PACK_H = 0.105, 0.035, 0.029                    # V RMRC Tattu 2300 4S 105 x 35 x 29 (readymaderc.com/products/details/tattu-2300-75c-4s1p-xt60, 2026-11-15; EU retailers list 105 x 33 x 28)
PAD_T = 1.0 * MM                            # D-199: anti-slip pad on the tray floor, 1.0 mm EST (silicone rubber sheet cut to 100 x 30 mm: thickness and density are EST, measure on arrival)
PACK_Z0 = 0.008 + PAD_T                     # the pack now stands on the drawn pad (tray plate top z 8.0)
PACK_R = 3.0 * MM                           # EST pouch corner radius under the shrink (not published): measure
LEAD_D = 3.0 * MM                           # EST 14 AWG silicone insulation OD (V: Tattu page lists "14 AWG", no OD): measure
LEAD_LEN = 0.100                            # V nextfpv / gravesrc "about 100 mm" (audit; one retailer says 35/60 mm): measure on arrival
LEAD_PITCH = 7.2 * MM                       # EST XT60 pin pitch (Amass XT60: two 3.5 mm pins; not fetched): measure
XT60_W, XT60_H = 15.5 * MM, 8.1 * MM        # V Pololu 2174/2175 listing "15.5 x 8.1 x 20.5" (pololu.com/product/2174, 2026-11-15); Amass drawing not readable (components101 PDF is an image)
XT60_L = 12.0 * MM                          # EST: each half 12 mm so a mated pair is 24 mm (V Fingertech listing, robotshop.com, "mated length 24 mm"); Pololu 20.5 mm probably includes solder cups
XT60_CH = 2.0 * MM                          # EST keying chamfer on the lower corners
BAL_X = PACK_X[1] - 0.0009                  # D-199: balance lead leaves the end face at x 6.6 mm (2.5 mm aft of the nearer power lead, wires 3.0 / 1.2 mm)
PACK_XL = 0.0025                            # EST: power leads leave the pack end face in its aft 10 mm (x -2.5..7.5), clear of the 25 mm strap (x -27.5..-2.5)
PACK_ZL = PACK_Z0 + PACK_H / 2              # lead exit height: mid thickness (EST)
LEAD_Y1 = 0.0635                            # EST: leads leave the end face (y +52.5 mm) 11 mm, then run aft on the skin outboard of the plate (half width 55)
_xt0 = 0.085                                # male housing starts here (EST), female to _xt0 + 2 XT60_L
XT_Z = max(zu(x) for x in (_xt0, _xt0 + 2 * XT60_L)) + XT60_H / 2 + 0.0002          # CALC: connector centre height, sits on the skin
STRAP_W, STRAP_T = 20 * MM, 1.6 * MM        # D-199: BOM W08 = STRIX Non-Slip Battery Strap 20 x 300 mm (V readymaderc, 2026-11-15; was 25 mm hook-and-loop EST); thickness EST
STRAP_X0 = PACK_X[0]                        # strap fore edge (nominal pack position): strap x -27.5..-2.5 (pack at trim 0)
X_GROUND = 0.3375                           # EST: pad aft face (pad 30 mm DOC)
FC_X0 = 0.045                                                          # QP-4: FC hard-mounted ON the spar centre (spar axis x 0.060 = FC centre); ESC moved aft of it
GEL = 0.0030                                                           # EST foam tape 3.0 mm (was 1.5; D-194 stock-screw stack height): FC HARD-MOUNTED (BOARD s3 D-186, s1 item 5)
T_PCB = 1.6 * MM                            # EST PCB thickness (not published): measure
FC_CX = FC_X0 + 0.015
FC_HOLES = [(FC_CX + sx * 0.010, sy * 0.010) for sx in (-1, 1) for sy in (-1, 1)]   # V Holybro 20 x 20 mm M2 pattern (phone-readable on retailer pages, 2026-11-15)
GEL_XY = FC_HOLES                           # tape pads sit under the four M2 holes (was 24 x 19 EST)
FC_TOP = ZP + GEL + 0.020                   # V Holybro stack height 20 mm (envelope kept: bottom board on the pads, top board at the top)
FC_B = ((FC_X0, -0.0125, ZP + GEL), (FC_X0 + 0.030, 0.0125, FC_TOP))   # V Holybro 30 x 25 x 20 stack (holybro.com/products/kakute-f405-wing-mini)
FC_ZB = ZP + GEL                            # bottom board underside
FC_ZB_TOP = FC_ZB + T_PCB
FC_STANDOFF = (FC_TOP - T_PCB) - FC_ZB_TOP  # CALC 16.8 mm: ASSUMES the two boards are at the bottom and top of the 20 mm stack: spacing is NOT published ("-")
# solder pad layout (EST: the Holybro pinout page gives pad names only, board images not readable): (x, y, z)
FC_PADS = {'ESC': (0.0475, 0.0, FC_ZB_TOP), 'S5': (0.0725, 0.005, FC_ZB_TOP), 'S6': (0.0725, -0.005, FC_ZB_TOP),
           'GPS': (0.0475, 0.005, FC_TOP), 'I2C': (0.0475, -0.005, FC_TOP), 'RX': (0.0725, 0.0, FC_TOP)}
RX_B = ((0.102, -0.0525), (0.124, -0.0395))  # V RadioMaster RP3 V2 22 x 13 x 4 mm (readymaderc 85670, 2026-11-15): 22 along x, 13 along y
RX_T = 4.0 * MM
GPS_B = ((0.045, 0.0275), (0.070, 0.0525))   # V TBS M10Q 25 x 25 x 7.7 mm (readymaderc 86501)
GPS_T = 7.7 * MM
AS_T = 8.0 * MM                             # EST
# D-208 pitot (AVN-006), its two short pneumatic lines (AVN-009-T / -S) and the airspeed board (AVN-005), all at the LEFT wing tip.
# RMRC publishes the kit contents and the tubing only (readymaderc RMRC-PIX-AIR-SEN, 2026-11-18: "Tubing Size: 2mm ID / 4mm OD", "approx. 0.5m";
# the replacement pitot page: "Pitot Tube (Prandtl Tube) with plastic attachment point"). Probe length, OD, the attachment block, the barbs and the
# board size are NOT published: every such dimension below is EST and must be measured on arrival (BUILD step E1).
# The board sits next to the probe (user 2026-11-18, "move the sensor board"): 2 x 39 mm of tubing instead of 2 x 388 mm (saves 7.6 g of silicone);
# the light 4-wire I2C lead runs inboard in a foam-core groove instead.
PIT_Y = -0.420                              # probe axis: 10 mm outboard of the fin rib saddle ring (|y| 0.35..0.41), 30 mm in from the tip; prop discs end at |y| 0.309
PIT_X0, PIT_X1 = -0.130, 0.030              # EST probe 160 mm, tip 130 mm ahead of the LE; rear end in the plastic attachment block
PIT_R, PIT_RI = 0.0015, 0.0010              # EST 3 mm brass probe
PIT_B = (0.030, 0.038, 0.0045, 0.0030)      # EST plastic attachment block: x 30..38, half width 4.5 (y), half height 3.0 (z)
PIT_NR = 0.0010                             # EST barb OD 2.0 mm = the tubing bore (V RMRC 2 mm ID); a real barb is a slight press fit: measure
PIT_DY = {'T': 0.0022, 'S': -0.0022}        # EST barb positions on the block's rear face (+-2.2 mm in y: two 4 mm tubes side by side)
PT_D = 0.004                                # V RMRC silicone tubing OD 4 mm (ID 2 mm)
PT_XR, PT_ZT = 0.049, 0.0090                # tubes rise at x 49 (spar from x 54) and run aft at z 9 over the spar (top z 6; skin z 12.3 at x 60)
AS_B = ((0.069, PIT_Y - 0.0075), (0.084, PIT_Y + 0.0075))   # EST board 15 x 15 in a pocket aft of the spar (x <= 66), y -427.5..-412.5 (saddle ring to -410)
AS_ZB = 0.0035                              # board underside z 3.5 (sensor top z 11.5, skin z 12.3 at x 75)
AS_SX = (0.0715, 0.0785)                    # EST sensor body x range; its barbs point -x (forward) from x 71.5 to 66.5 at z PT_ZT
I2C_X = 0.095                               # I2C lead groove x: aft of the rib socket (x <= 90.5), ahead of the servo pockets (x >= 127)
I2C_ZD = zu(I2C_X) - 0.0065                 # deep under the servo-lead groove that crosses at |y| 0.19 (its bottom z ~6.9)
I2C_ZS = zu(I2C_X) - 0.0025                 # shallow over the fin rib tube at |y| 0.38 (its top z 7.0)
SV_X0, SV_X1, SV_DY, SV_Z0 = 0.1270, 0.1554, 0.01335, -0.0013 - WING_DZ    # SERVO.md: EMAX ES3054HV 28.4 x 13.0 x 26.7 (servodatabase / getfpv, 2026-11-15); ears, output boss: "-" (no drawing)
SV_XS = 0.1405                              # spline axis x (kept; spline axis is vertical, arm turns in the x-y plane)
ARM_R = 12.0 * MM                           # FIXES2 s1.3: servo arm 12 mm to the pushrod hole
ARM_Z0 = SV_Z1                              # arm sits on the case top (output boss height "-": measure; a real boss lifts the arm)
ARM_T = 2.0 * MM                            # EST arm thickness
ARM_Z1 = ARM_Z0 + ARM_T
ROD_D = 1.2 * MM                            # V RMRC linkage set 1.2 mm rods
ROD_Z = ARM_Z1 + ROD_D / 2                  # rod rests on the arm top, Z-bent down through the arm hole
HORN_R = 12.9 * MM                          # FIXES2 s1.3: rod hole radius from the hinge axis
HORN_XH = XH + math.sqrt(HORN_R ** 2 - (ROD_Z - HINGE_Z) ** 2)     # CALC hole x on the 12.9 mm radius
HORN_X0, HORN_X1 = HORN_XH - 0.0015, HORN_XH + 0.0135      # EST blade 15 mm long (horn size "-": RMRC lists "20 mm horns"); D-194: blade starts 1.5 mm ahead of the hole, the clevis sleeve ends 2.0 mm ahead of it
ROD_Y = lambda sy: sy * (SERVO_Y - ARM_R)   # arm tip (neutral) and horn hole share this y: the rod runs parallel to x
HORN_TOP = ROD_Z + 0.0022                   # EST blade top 2.2 mm above the hole axis
SPLINE_TEETH = 23                           # V readymaderc 85975 "23T output gear spline" (read 2026-11-15); the old stack said 25T (ES3352 copy): RESOLVED to 23T

# hardware masses CALC (HW_DIMS M2: pan dk 3.8 k 1.6; thin nut af 4.0 m 1.2; nut ISO 4035/DIN 439 EST)
FCS_L = {}                                  # per-hole screw length, filled below
_NUT_M = 1.2 * MM


def _nut_bottom(x):
    return max(zu(x + dx) for dx in (-2.4 * MM, 0.0, 2.4 * MM)) + 0.0001


FCS_STOCK = 0.025                                              # D-194: stock M2 x 25 pan screw (stock lengths 20/22/25/30); pads 3.0 mm (generic 3 mm double-sided foam tape, EST) set the stack height
FCS_L = {h: FCS_STOCK for h in FC_HOLES}      # stock M2 x 25: tips end 0.1 mm short of to 0.6 mm past the nut bottom (the core carries 4 shop relief holes for the tips: HWC-001 is a core seat guest)
M_FC_SCREWS = round(sum(_g_screw(2.0 * MM, L, 3.8 * MM, 1.6 * MM) for L in FCS_L.values()), 2)
M_FC_NUTS = round(4 * _g_nut(4.0 * MM, _NUT_M, 2.0 * MM), 2)
M_FC_SET = round(M_FC_SCREWS + M_FC_NUTS, 2)    # HWC-001 screws + HWC-003 nuts (nuts are seated in the plate before the plate goes on the skin: separate build step)
M_ARM_SCREW = round(_g_screw(2.0 * MM, 6.0 * MM, 3.8 * MM, 1.6 * MM), 2)     # M2 x 6 pan (kept from the old stack)
M_STANDOFFS = 4 * RHO_PA66 * math.pi / 4 * (4.0 ** 2 - 2.2 ** 2) * FC_STANDOFF   # g, nylon standoffs (part of AVN-002's 17 g)
M_XT60_F = 3.0                              # EST g: XT60 female half
M_TAIL = 5.0   # EST 2 x 0.10 m of 14 AWG at 25 g/m (V: RMRC wire page lists no mass) = 5 g
M_STRAP = 5.5                               # V 5.5 g each: readymaderc STRIX Non-Slip Battery Strap 20 x 300 mm (page read 2026-11-15; was EST 3.0 g for a 25 mm hook-and-loop)


# ------------------------------------------------------------------ parts
# power / avionics
P('PWR-001', 'Pack Tattu 2300 mAh 4S 75C', 'power', 270.0, 'LiPo', 'buy', 'source')
P('PWR-002', 'Pack strap 20 x 300 mm with buckle (STRIX, BOM W08; round pack and tray)', 'power', M_STRAP, 'nylon webbing + plastic buckle', 'buy')
PAD_M = round(0.100 * 0.030 * PAD_T * 1.15 * 1e6, 1)     # g: 100 x 30 x 1 mm, silicone rubber 1.15 g/cm3 (EST)
P('PWR-003', 'Anti-slip pad 100 x 30 x 1.0 mm silicone rubber sheet on the tray floor (BOM W09; thickness, size and density EST)', 'power', PAD_M, 'silicone rubber', 'buy')
P('AVN-001', 'Avionics plate', 'avionics', 8.0, 'PETG (printed)')   # QP-4 FIXES 12 -> 8 g: 4 lightening windows (now drawn)
P('AVN-002', 'Flight controller Kakute F405 Wing Mini', 'avionics', 17.0, 'PCB', 'buy', 'bus')
P('AVN-007', 'Foam-tape pads x4 (FC hard mount, 3.0 mm)', 'avionics', 1.0, 'VHB-class foam tape', 'buy')
P('AVN-003', 'Receiver RP3 V2 ELRS', 'avionics', 4.6, 'PCB', 'buy', 'sink')       # V 4.6 g with antennas (readymaderc 85670)
P('AVN-004', 'GPS TBS M10Q + compass', 'avionics', 13.5, 'PCB', 'buy', 'sink')
P('AVN-005', 'Airspeed sensor MS4525 board', 'avionics', 3.0, 'PCB', 'buy', 'sink')
P('AVN-006', 'Pitot-static probe (RMRC kit; size not published: EST 166 x 3 mm, measure)', 'avionics', 5.0, 'brass tube', 'buy')
for _k, _n in (('T', 'total'), ('S', 'static')):    # D-208: mass and length set after pitot_paths() exists (end of file)
    P('AVN-009-' + _k, 'Pitot line, %s pressure: silicone tubing 2 / 4 mm (V RMRC)' % _n, 'avionics', 0.0, 'silicone rubber', 'buy')
P('AVN-008', 'Bay cover (D-198): 0.6 mm printed PETG hood over the FC stack, ESC and the phase-lead runs from the foam ditch to the ESC pads; notches for the sensor leads and the battery tail', 'avionics', cover_mass_g(), 'PETG (printed)')
P('HWC-001', 'FC mounting screws: 4 x M2 x 25 pan screw (stock)', 'avionics', M_FC_SCREWS, 'A2 stainless', 'buy')
P('HWC-003', 'FC mounting nuts: 4 x M2 thin nut (DIN 439 1.2 mm) in the plate hex pockets', 'avionics', M_FC_NUTS, 'A2 stainless', 'buy')
# mechanisms (30 g with linkage)
for s in 'RL':
    P('MEC-001-' + s, 'Servo EMAX ES3054HV (%s)' % s, 'mechanisms', 20.5, 'plastic / metal gear', 'buy', 'sink')
    P('MEC-002-' + s, 'Servo arm (%s)' % s, 'mechanisms', 1.0, 'nylon', 'buy')
    P('MEC-003-' + s, 'Pushrod 1.2 mm with Z-bend and clevis (%s)' % s, 'mechanisms', 0.97, 'steel', 'buy')
    P('MEC-005-' + s, 'Clevis pin 1.0 x 4.4 mm (%s); mass CALC steel, carried inside the 1.0 g rod before D-194' % s, 'mechanisms', 0.03, 'steel', 'buy')
    P('MEC-004-' + s, 'Control horn (%s)' % s, 'mechanisms', 1.0, 'nylon', 'buy')
    P('HWC-002-' + s, 'Servo arm screw M2 x 6 pan (%s)' % s, 'mechanisms', M_ARM_SCREW, 'A2 stainless', 'buy')
# D-199 phase-lead raceway: printed, mass = drawn wall volume x 1.27 (walls 0.6 mm, EST basis as AVN-008)
for s_ in 'RL':
    P('HRN-003-' + s_, 'Phase-lead raceway (D-199, %s): closed 0.6 mm PETG channel under the tray plate, hub pad slot to the tray end, two bundles side by side' % s_, 'harness', raceway_mass_g(), 'PETG (printed)')
for s_ in ST:
    P('HRN-004-' + s_, 'Hub conduit (D-199, D-202, %s): 0.6 mm PETG tunnel over the 4.8 mm tube exit hole, aft run, sideways step, then the drop / rise into the raceway window' % s_, 'harness', hubhop_mass_g(s_), 'PETG (printed)')
# landing
for s in ST:
    P('GER-001-' + s, 'Foot shoe (%s)' % s, 'landing', 1.4, 'PETG (printed)')
    P('GER-002-' + s, 'Foot pad EVA/PE 12x15x30 (%s)' % s, 'landing', 0.7, 'EVA / PE foam')
# harness: XT60 female + tail (modelled), remaining lump
P('HRN-002', 'XT60 female + 14 AWG tail to the ESC (modelled)', 'harness', M_XT60_F + M_TAIL, 'copper / silicone / nylon', 'buy', 'bus', carried=True)
P('HRN-001', 'Harness remainder (wire, connectors, ties, tubing; MASS-GATE avionics 110 g less itemised parts) - lumped',
  'harness', None, 'copper / silicone', cg=[0.030, 0.0, 0.020], mass_proxy=True, carried=True)
HRD_BASE_G = 30.0                           # QP-4 FIXES 37 -> 30 g (before this round)
HRD_C_MODELLED_G = round(M_FC_SET + 2 * M_ARM_SCREW, 2)    # lane C hardware now drawn (lanes A and B subtract theirs)
P('HRD-001', 'Hardware: screws, nuts, epoxy fillets, paint (MASS-GATE 40 g less rib saddles) - lumped, less modelled sets', 'assembly',
  round(HRD_BASE_G - HRD_C_MODELLED_G, 2), 'steel / epoxy', cg=[0.100, 0.0, 0.0], mass_proxy=True, carried=True)
HRN_BASE_G = 106.0                          # old MASS-GATE avionics allocation (110 g less itemised parts): superseded by the bottom-up list below (D-198)
PARTS['HRN-001']['mass_g'] = 0.0            # set after phase_route() exists, see HRN_ITEMS


# ------------------------------------------------------------------ edges
# power
E(en('PWR'), 'PWR-002', 'CGE-008', 'CT-STRAP-VELCRO', 'power', 'buckle strap round pack and tray: over the pack top, outside the tray end walls, under the tray plate AND the 16 mm bridge tube CGE-004 (D-206) (tangent to the plate underside, z -6..6)',
  retention=dict(item='20 mm strap', count=1, load_n=38.8), field_joint=True)
E(en('PWR'), 'PWR-001', 'CGE-008', 'CT-STRAP-VELCRO', 'power', 'pack sits on the anti-slip pad PWR-003 on the tray floor, between the integral lips; strap PWR-002 holds it',
  retention=dict(item='anti-slip pad + strap', count=1), field_joint=True)
E(en('PWR'), 'PWR-003', 'CGE-008', 'CT-TAPE-FOAM', 'power', 'pad stuck on the tray plate (adhesive-backed sheet, EST)')
E(en('PWR'), 'PWR-002', 'PWR-001', 'CT-STRAP-VELCRO', 'power', 'strap bears on the pack top face')
# avionics
E(en('AVN'), 'AVN-001', 'WNG-001', CA, 'avionics', 'plate base follows the upper skin (same vertices as the core)')
E(en('AVN'), 'AVN-007', 'AVN-001', 'CT-GEL-PAD', 'avionics', 'four thin foam-tape pads on the plate (FC on the wing centre, not on the cage hub: SITL-FLIGHT follow-up 2; hard mount, BOARD D-186)')
E(en('AVN'), 'AVN-002', 'AVN-007', 'CT-GEL-PAD', 'avionics', 'FC on the tape pads, M2 screws (hard mount; gel only if its frequency is measured at 40-70 Hz)')
E(en('AVN'), 'AVN-005', 'WNG-001', TAPEF, 'avionics', 'airspeed board in its pocket in the left wing core next to the pitot, foam tape; pocket taped over (D-208)', retention=dict(item='VHB-class tape', count=1))
for pid in ('AVN-003', 'AVN-004'):
    E(en('AVN'), pid, 'AVN-001', TAPEF, 'avionics', 'foam tape + tie', retention=dict(item='VHB-class tape', count=1))
E(en('AVN'), 'AVN-006', 'WNG-001', EPX, 'avionics', 'pitot in a groove in the LE at y = -0.42 (D-208: left wing, the sensor board side; 0.11 m outboard of the prop discs, EST)')
for _k, _n, _p in (('T', 'total', 'P1'), ('S', 'static', 'P2')):
    _ret = dict(item='push-on silicone on the barb', count=1, load_n='none (pneumatic)', inspection='set-up: line on the barb to the shoulder; blow test reads > 0')
    E(en('AVN'), 'AVN-009-' + _k, 'AVN-006', 'CT-PITOT-TUBING', 'avionics', _n + ' line on the probe ' + _n + ' outlet barb (D-208)', retention=_ret)
    E(en('AVN'), 'AVN-009-' + _k, 'AVN-005', 'CT-PITOT-TUBING', 'avionics', _n + ' line on board port ' + _p + ' (ARSPD_TUBE_ORDR 2: a swap is harmless; D-208)', retention=_ret)
    E(en('AVN'), 'AVN-009-' + _k, 'WNG-001', TAPEF, 'avionics', _n + ' line in its foam-core groove, laid in from above through a slit in the skin, slit taped (as the servo grooves; D-208)')
E(en('AVN'), 'AVN-008', 'AVN-001', TAPEF, 'avionics', 'cover stands on the plate (and its front ramp on the skin ahead of the plate), foam tape + two ties; removable for FC access (D-198)', retention=dict(item='VHB-class tape + ties', count=1))
_e_fc = en('AVN')
EDGES.append(dict(id=_e_fc, part_a='HWC-001', part_b='AVN-002', via='CT-HW-SEATED', owner='avionics', hardware=True,
                  notes='four M2 screws through the stack standoffs (hardware of E-AVN-03)',
                  joint_stack=STACK('M2 x 25 pan screw (stock)', 4, 'boards 2.2 mm clearance (EST), standoffs ID 2.2', 30,
                                    eng=1.2, mineng=1.0)))
_e_fs = en('AVN')
EDGES.append(dict(id=_e_fs, part_a='HWC-001', part_b='HWC-003', via='CT-HW-SEATED', owner='avionics', hardware=True,
                  notes='screw threads into the nut (stock M2 x 25: tip 0.1 mm short of to 0.6 mm past the nut bottom)',
                  joint_stack=STACK('M2 x 25 pan screw into M2 thin nut', 4, 'nut thread', 31, eng=1.1, mineng=1.0)))
_e_fp = en('AVN')
EDGES.append(dict(id=_e_fp, part_a='HWC-003', part_b='AVN-001', via='CT-HW-SEATED', owner='avionics', hardware=True,
                  notes='four M2 thin nuts trapped in hex pockets on the plate underside (seated before the plate goes on the skin)',
                  joint_stack=STACK('M2 pan screw + M2 thin nut (DIN 439, 1.2 mm)', 4, '2.2 mm hole + hex pocket in the plate (plate 1.5-2.1 mm)', 30,
                                    eng=1.2, mineng=1.0)))
# mechanisms
for s in 'RL':
    E(en('MEC'), 'MEC-001-' + s, 'WNG-001', EPX, 'mechanisms', 'servo in its pocket')
    E(en('MEC'), 'MEC-002-' + s, 'MEC-001-' + s, 'CT-SERVO-SPLINE', 'mechanisms', 'arm on the 23T output spline (V readymaderc 85975; the old 25T was an ES3352 copy)',
      joint_stack=STACK('M2x6 retaining screw', 1, 'arm bore on the 23T spline', 20, eng=4.0, mineng=3.0))
    E(en('MEC'), 'MEC-003-' + s, 'MEC-002-' + s, 'CT-CLEVIS', 'mechanisms', 'rod Z-bend in the arm tip hole (vertical pin)',
      motion=dict(axis='Z', range_deg=[-30, 30]))
    E(en('MEC'), 'MEC-003-' + s, 'MEC-004-' + s, 'CT-CLEVIS', 'mechanisms', 'rod clevis on the horn hole (horizontal pin)',
      motion=dict(axis='Y', range_deg=[-ELEV_POSE, ELEV_POSE]))
    E(en('MEC'), 'MEC-004-' + s, 'WNG-006-' + s, EPX, 'mechanisms', 'horn bonded on the elevon upper skin')
    EDGES.append(dict(id='E-MEC-PIN-%s4' % s, part_a='MEC-005-' + s, part_b='MEC-004-' + s, via='CT-HW-SEATED', owner='mechanisms', hardware=True,
                      notes='clevis pin through the horn hole (pressed in along y after the clevis is lowered onto the blade); moves with the horn',
                      joint_stack=STACK('1.0 mm clevis pin', 1, 'horn hole 1.5 mm', 40, eng=2.0, mineng=2.0)))
    EDGES.append(dict(id='E-MEC-PIN-%s3' % s, part_a='MEC-005-' + s, part_b='MEC-003-' + s, via='CT-CLEVIS', owner='mechanisms',
                      notes='clevis pin through the cheek holes of the rod (the rod turns on it); linkage path not modelled in the poses',
                      motion=dict(axis='Y', range_deg=[-ELEV_POSE, ELEV_POSE])))
    for tgt in ('MEC-002-', 'MEC-001-'):
        EDGES.append(dict(id='E-MEC-HW-%s%s' % (s, tgt[6]), part_a='HWC-002-' + s, part_b=tgt + s, via='CT-HW-SEATED', owner='mechanisms',
                          hardware=True, notes='arm retaining screw (hardware of the spline joint)',
                          joint_stack=STACK('M2x6 pan', 1, 'arm bore / output-shaft thread', 20, eng=4.0, mineng=3.0)))
# landing
for s in ST:
    tube = 'FIN-001-' + ('R' if ST[s][0] > 0 else 'L')
    E(en('GER'), 'GER-001-' + s, tube, EPX, 'landing', 'shoe cap on the tube end')
    E(en('GER'), 'GER-002-' + s, 'GER-001-' + s, TAPEF, 'landing', 'pad PSA on the shoe plate')
# lumps (non-structural: located by ties)
E('E-HRN-30', 'HRN-003-R', 'CGE-008', EPX, 'harness', 'raceway bonded to the tray plate underside (top face z 6.0), lowered from above before the tray, in its foam groove (D-199)')
E('E-HRN-32', 'HRN-003-R', 'WNG-001', TAPEF, 'harness', 'raceway taped in its foam groove (D-199)')
E('E-HRN-33', 'HRN-003-L', 'WNG-001', TAPEF, 'harness', 'raceway taped in its foam groove (D-199)')
E('E-HRN-31', 'HRN-003-L', 'CGE-008', EPX, 'harness', 'raceway bonded to the tray plate underside (top face z 6.0), lowered from above before the tray, in its foam groove (D-199)')
for _i, s_ in enumerate(ST):
    E('E-HRN-4%d' % _i, 'HRN-004-' + s_, 'CGE-001', EPX, 'harness', 'hub conduit floor bonded on the hub sleeve and the tube (D-199, D-202)')
    E('E-HRN-5%d' % _i, 'HRN-004-' + s_, 'HRN-003-' + ('R' if ST[s_][0] > 0 else 'L'), EPX, 'harness', 'conduit drop column bonded on the raceway wall round its window (D-199, D-202)')
E('E-HRN-21', 'HRN-002', 'WNG-001', TAPEF, 'harness', 'XT60 pair and tail taped on the skin (foam tape) and tied', retention=dict(item='VHB-class tape', count=1))
E('E-HRN-20', 'HRN-001', 'WNG-001', 'CT-TIE', 'harness', 'harness lump: ties and tape on the wing')
E('E-ASM-01', 'HRD-001', 'WNG-001', 'CT-TIE', 'assembly', 'hardware lump')
# electrical (owner harness); ELEC[eid] = wire diameter in the CAD (bundle envelope; strands carry the real diameters)
EDGES.append(dict(id='E-HRN-01', part_a='PWR-001', part_b='HRN-002', via='CT-XT60', owner='harness',
                  notes='pack lead XT60 male mated to the ESC-side XT60 female (disconnect); both lead pairs run outboard of the plate',
                  wire=WIRE(14, 'XT60', 'R-A-01', ['tape on the skin'], 6, 'heat-shrink + tie', True),
                  current_a=dict(cont=11, peak=41)))
ELEC['E-HRN-01'] = 0.003
EDGES.append(dict(id='E-HRN-12', part_a='HRN-002', part_b='PRP-003', via='CT-SOLDER-DC', owner='harness',
                  notes='14 AWG tail from the XT60 female to the ESC battery pads (flat pair, inboard over the ESC)',
                  wire=WIRE(14, 'solder + heat-shrink', 'R-A-12', ['tie at the plate edge'], 6, 'heat-shrink + tie'),
                  current_a=dict(cont=11, peak=41)))
ELEC['E-HRN-12'] = 0.0063
EDGES.append(dict(id='E-HRN-13', part_a='PWR-001', part_b='HRN-002', via='CT-SOLDER-DC', owner='harness',
                  notes='D-199: pack power leads (vendor, 14 AWG about 100 mm) from the pack end face through the tray end-wall notch, down to the skin and along it to the XT60 male; taped on the skin',
                  wire=WIRE(14, 'vendor leads to XT60 male', 'R-A-13', ['tray end-wall notch', 'tape on the skin'], 6, 'vendor heat-shrink'),
                  current_a=dict(cont=11, peak=41)))
ELEC['E-HRN-13'] = 0.0063
EDGES.append(dict(id='E-HRN-14', part_a='PWR-001', part_b='HRN-002', via='CT-SOLDER-DC', owner='harness',
                  notes='D-199: pack balance lead (5 conductors, EST 1.2 mm bundle) from the end face over the top edge to the JST-XH plug on the pack top',
                  wire=WIRE(26, 'JST-XH 5-pin', 'R-A-14', ['pack top'], 4, 'vendor lead')))
ELEC['E-HRN-14'] = 0.0012
for i, s in enumerate(ST):
    eid = 'E-HRN-%02d' % (2 + i)
    EDGES.append(dict(id=eid, part_a='PRP-003', part_b='PRP-001-' + s, via='CT-SOLDER-PHASE', owner='harness',
                      notes='motor phase leads %s (3 x 20 AWG, OD 1.8 mm, V T-Motor / Pimoroni): out of the motor base through the cup lead hole into the cup collar, inside the arm bore to the hub end, out through the socket floor hole, then exposed over the hub and wing (D-198) to the ESC pad' % s,
                      wire=WIRE(20, 'solder + heat-shrink', 'R-A-%02d' % (2 + i),
                                ['cup collar', 'inside the arm tube', 'hub socket floor hole', 'tie at the hub aft face', 'tie at the plate edge'], 4,
                                'heat-shrink + tie at the floor hole'),
                      current_a=dict(cont=10.9, peak=12.1)))
    ELEC[eid] = 0.0039
EDGES.append(dict(id='E-HRN-06', part_a='PRP-003', part_b='AVN-002', via='CT-JST-GH-6', owner='harness',
                  notes='ESC lead to the FC (VBAT, signals, telemetry): 6 conductors, soldered to the FC pads (the Kakute has pads, not sockets: docs.holybro.com pinout 2026-11-15)',
                  wire=WIRE(26, 'JST-GH 6-pin', 'R-A-06', ['tie on the plate'], 3, 'strain loop')))
ELEC['E-HRN-06'] = 0.0078
for i, s in enumerate('RL'):
    eid = 'E-HRN-%02d' % (7 + i)
    EDGES.append(dict(id=eid, part_a='AVN-002', part_b='MEC-001-' + s, via='CT-SERVO-JR', owner='harness',
                      notes='servo lead %s: 3-conductor ribbon, soldered to the FC pad M5/M6 (JR plug cut off; the FC has pads only), laid on the skin to the servo' % s,
                      wire=WIRE(26, 'JR 3-pin', 'R-A-%02d' % (7 + i), ['tie at the plate edge', 'tape on the skin'], 3,
                                'strain loop')))
    ELEC[eid] = 0.0036
for eid, a, b, ct, nm, nc in (('E-HRN-09', 'AVN-002', 'AVN-003', 'CT-JST-GH-4', 'RX UART (CRSF wire soldered at the RX pads)', 4),
                              ('E-HRN-10', 'AVN-002', 'AVN-004', 'CT-JST-GH-6', 'GPS (plug on the GPS board, other end soldered to the FC)', 6),
                              ('E-HRN-11', 'AVN-002', 'AVN-005', 'CT-JST-GH-4', 'airspeed I2C (plug on the MS4525 board, other end soldered to the FC)', 4)):
    EDGES.append(dict(id=eid, part_a=a, part_b=b, via=ct, owner='harness', notes=nm + ' lead',
                      wire=WIRE(28, ct, 'R-' + eid[2:], ['tie on the plate'], 3, 'strain loop')))
    ELEC[eid] = 1.0 * MM * nc               # ribbon width (flat ribbon of nc x 1.0 mm)


# ------------------------------------------------------------------ geometry builders
def _xt60_loop(cx, cz, w=XT60_W, h=XT60_H, ch=XT60_CH):
    """XT60 housing outline in the (y, z) plane (EST keying: the two lower corners chamfered)."""
    return [(cx - w / 2 + ch, cz - h / 2), (cx + w / 2 - ch, cz - h / 2), (cx + w / 2, cz - h / 2 + ch), (cx + w / 2, cz + h / 2),
            (cx - w / 2, cz + h / 2), (cx - w / 2, cz - h / 2 + ch)]


def _lead_path(k):
    """Centre line of pack lead k (+-1: outer / inner) from the end face to the male housing back (axis-aligned legs)."""
    dx = k * LEAD_D * 0.53
    y1 = LEAD_Y1 + k * LEAD_PITCH / 2
    return [(PACK_XL + dx, PACK_L / 2, PACK_ZL), (PACK_XL + dx, y1, PACK_ZL), (PACK_XL + dx, y1, XT_Z), (_xt0, y1, XT_Z)]


def build_power(ctx):
    pk = ctx.part('PWR-001', rgb=(0.15, 0.15, 0.6))
    pk.prism('Y', -PACK_L / 2, [_rrect(PACK_X[0], PACK_Z0, PACK_X[1], PACK_Z0 + PACK_H, PACK_R, 4)], PACK_L, name='pack cells (shrink-wrapped pouch)')
    # D-199: the vendor power leads are drawn as wires (E-HRN-13, harness build) so they follow the skin and are counted in the exposure inventory
    yc = LEAD_Y1
    pk.prism('X', _xt0, [_xt60_loop(yc, XT_Z)], XT60_L, name='XT60 male housing')
    # balance lead: 5 x 26 AWG-class (EST 1.2 mm OD), leaves the end face aft of the strap, up over the top edge and inboard along the pack top, JST-XH 5-pin plug
    bx = BAL_X
    zt = PACK_Z0 + PACK_H
    pts = [(bx, PACK_L / 2, PACK_ZL), (bx, PACK_L / 2 + 0.0015, PACK_ZL), (bx, PACK_L / 2 + 0.0015, zt + 0.0006), (bx, 0.017, zt + 0.0006)]
    # balance lead drawn as a wire (E-HRN-14, harness build, D-199)
    pk.box((bx - 2.9 * MM, 0.017 - 14.8 * MM, zt), (bx + 2.9 * MM, 0.017, zt + 9.8 * MM - 2.6 * MM), name='JST-XH 5-pin plug (EST height; V octopart 14.8 x 5.7 mm)')   # housing 14.8 x 5.7 V (octopart/JST XHP-5 listing 2026-11-15); height listing 9.8 mm is the mounted height: 7.2 EST drawn
    pd = ctx.part('PWR-003', rgb=(0.35, 0.35, 0.38))
    pd.box((PACK_X[0] + 0.0025, -0.050, 0.008), (PACK_X[0] + 0.0325, 0.050, 0.008 + PAD_T), name='anti-slip pad 100 x 30 x 1.0 mm (EST)')
    # strap loop: axis x, ring around tray + pack
    ctx_strap = ctx.part('PWR-002', rgb=(0.1, 0.1, 0.1))
    yi = 0.0545
    zb_ = BR_Z - BR_RO                            # D-206: under the 16 mm bridge (axis z -2): z -10 (was -6 under the 12 mm bridge)
    ctx_strap.prism('X', STRAP_X0, [_rrect(-yi - STRAP_T, zb_ - STRAP_T, yi + STRAP_T, PACK_Z0 + PACK_H + STRAP_T, 0.0012, 3),
                                    [(-yi, zb_), (yi, zb_), (yi, PACK_Z0 + PACK_H), (-yi, PACK_Z0 + PACK_H)]], STRAP_W, name='strap loop')


def build_avionics(ctx):
    # ---- plate with the four lightening windows (QP-4 FIXES: the 8 g assumes them)
    pl = ctx.part('AVN-001', rgb=(0.9, 0.9, 0.9))
    loop = [(XS[i], zu(XS[i])) for i in range(PLATE_I0, PLATE_I1 + 1)] + [(PLATE_X1, ZP), (PLATE_X0, ZP)]
    pl.prism('Y', -PLATE_Y, [loop], 2 * PLATE_Y, name='plate')
    for (wx0, wx1, wy0, wy1) in ((0.080, 0.122, 0.021, 0.040), (0.080, 0.122, -0.040, -0.021),
                                 (0.049, 0.072, 0.0155, 0.026), (0.049, 0.072, -0.026, -0.0155)):
        pl.cut_box((wx0, wy0, -0.05), (wx1, wy1, ZP + 0.01), name='lightening window')       # EST layout, clear of the boards
    for hx, hy in FC_HOLES:
        pl.cut_cylinder('Z', (hx, hy, -0.05), ZP + 0.05, 1.1 * MM, name='M2 clearance hole')
        nb = _nut_bottom(hx)
        pl.cut_prism('Z', nb - 0.0001, [_hex(hx, hy, 4.2 * MM)], _NUT_M + 0.0003, name='M2 nut pocket')
    # ---- foam-tape pads (one per M2 hole)
    gl = ctx.part('AVN-007', rgb=(0.6, 0.8, 0.9))
    for gx, gy in GEL_XY:
        gl.prism('Z', ZP, [[(gx - 3 * MM, gy - 3 * MM), (gx + 3 * MM, gy - 3 * MM), (gx + 3 * MM, gy + 3 * MM), (gx - 3 * MM, gy + 3 * MM)],
                           _ring(gx, gy, 1.1 * MM, 12)], GEL, name='foam tape pad')
    # ---- FC stack: bottom (power) board, 4 nylon standoffs, top (FC) board, solder pads
    fc = ctx.part('AVN-002', rgb=(0.1, 0.1, 0.5))
    _pcb(fc, FC_X0, -0.0125, FC_X0 + 0.030, 0.0125, FC_ZB, T_PCB, FC_HOLES, r=1.5 * MM, name='Kakute power board (EST 1.6 mm)')
    _pcb(fc, FC_X0, -0.0125, FC_X0 + 0.030, 0.0125, FC_TOP - T_PCB, T_PCB, FC_HOLES, r=1.5 * MM, name='Kakute FC board (EST 1.6 mm)')
    for hx, hy in FC_HOLES:
        k9.hw_washer(fc, 'Z', (hx, hy, FC_ZB_TOP), 1, 'M2', od=4.0 * MM, t=FC_STANDOFF, idia=2.2 * MM, name='nylon standoff (EST 4 mm OD)')
    for k, (x, y, z) in FC_PADS.items():
        _pad(fc, x, y, z, {'S5': 'servo pad S5', 'S6': 'servo pad S6', 'ESC': 'ESC signal pad', 'GPS': 'GPS pad', 'I2C': 'I2C pad', 'RX': 'RX pad'}[k])
    # ---- FC mounting hardware set (screws from the top board down to a thin nut under the plate)
    hw = ctx.part('HWC-001', rgb=(0.7, 0.7, 0.75))
    for hx, hy in FC_HOLES:
        L = FCS_L[(hx, hy)]
        k9.hw_screw(hw, 'Z', (hx, hy, FC_TOP), -1, 'M2', L, 'pan', name='M2 pan screw')
    hn = ctx.part('HWC-003', rgb=(0.7, 0.7, 0.75))
    for hx, hy in FC_HOLES:
        nb = _nut_bottom(hx)
        hex_ = _hex(hx, hy, 4.0 * MM)
        hn.prism('Z', nb, [hex_, _ring(hx, hy, 1.0 * MM, 12)], _NUT_M, name='M2 thin nut')
    # ---- receiver RP3 V2: PCB, RF shield, solder pads, 2 antennas (65 mm class, drawn 50 mm: hinge at x 183.75)
    rx = ctx.part('AVN-003', rgb=(0.2, 0.2, 0.2))
    (rx0, ry0), (rx1, ry1) = RX_B
    _pcb(rx, rx0, ry0, rx1, ry1, ZP, 1.2 * MM, r=1.0 * MM, name='RP3 V2 PCB (EST 1.2 mm)')
    rx.box((rx0 + 6 * MM, ry0 + 2.5 * MM, ZP + 1.2 * MM), (rx0 + 16 * MM, ry1 - 2.5 * MM, ZP + RX_T), name='RF shield / SoC (EST: total height 4 mm V)')
    for j in range(4):
        _pad(rx, rx0 + 1.2 * MM, ry0 + 2.2 * MM + j * 2.8 * MM, ZP + 1.2 * MM, 'CRSF pad %d' % j)
    for j, ya in enumerate((ry0 + 2.5 * MM, ry1 - 2.5 * MM)):
        ant = [(rx1, ya, ZP + 0.6 * MM), (rx1 + 0.050, ya, ZP + 0.6 * MM)]
        _legs(rx, ant, 1.1 * MM, 'antenna %d (EST OD 1.1 mm, 65 mm V, drawn 50 mm)' % (j + 1))
    # ---- GPS TBS M10Q: PCB, patch, JST-SH plug, cable stub
    gp = ctx.part('AVN-004', rgb=(0.3, 0.3, 0.3))
    (gx0, gy0), (gx1, gy1) = GPS_B
    _pcb(gp, gx0, gy0, gx1, gy1, ZP, T_PCB, r=1.0 * MM, name='M10Q PCB (EST 1.6 mm)')
    gcx, gcy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
    gp.box((gcx - 9 * MM, gcy - 9 * MM, ZP + T_PCB), (gcx + 9 * MM, gcy + 9 * MM, ZP + GPS_T), name='GNSS patch (EST 18 x 18; total height 7.7 V)')
    gp.box((gcx - 3.9 * MM, gy0, ZP + T_PCB), (gcx + 3.9 * MM, gy0 + 4.2 * MM, ZP + T_PCB + 3.5 * MM), name='JST-SH 6-pin plug (ASSUMED connector, EST size)')
    # ---- airspeed board MS4525 (EST 15 x 15): PCB, sensor, 2 barbed ports, JST-GH plug; D-208: in a pocket in the left wing next to the pitot
    asd = ctx.part('AVN-005', rgb=(0.3, 0.3, 0.3))
    (ax0, ay0), (ax1, ay1) = AS_B
    _pcb(asd, ax0, ay0, ax1, ay1, AS_ZB, T_PCB, r=1.0 * MM, name='MS4525 board (EST 15 x 15 x 1.6)')
    asd.box((AS_SX[0], PIT_Y - 0.0050, AS_ZB + T_PCB), (AS_SX[1], PIT_Y + 0.0050, AS_ZB + AS_T), name='MS4525DO sensor body (EST)')
    for j_, k in enumerate(('T', 'S')):          # ports point -x towards the probe (EST layout: RMRC gives no drawing)
        asd.cylinder('X', (AS_SX[0], PIT_Y + PIT_DY[k], PT_ZT), -0.0050, PIT_NR, name='barbed port P%d (%s), EST OD 2.0' % (j_ + 1, 'total' if k == 'T' else 'static'))
    asd.box((ax1 - 0.0040, PIT_Y - 0.0032, AS_ZB + T_PCB), (ax1, PIT_Y + 0.0032, AS_ZB + T_PCB + 4.2 * MM), name='JST-GH 4-pin plug (EST size), opening +x')
    # ---- D-198 bay cover: roof band with the ramp / step profile, two 0.6 mm end walls, notches for the bundles that leave at |y| 26.5 mm
    cv = ctx.part('AVN-008', rgb=(0.85, 0.9, 0.95))
    cv.prism('Y', -COV_Y, [cov_loops()], 2 * COV_Y, name='cover roof band (0.6 mm)')
    for sy in (1, -1):
        y0 = COV_Y if sy > 0 else -COV_Y - COV_T
        cv.prism('Y', y0, [cov_side_loop()], COV_T, name='cover end wall (0.6 mm)')
    for sy in (1, -1):
        ya, yb = sorted((sy * (COV_Y - 0.001), sy * (COV_Y + COV_T + 0.001)))
        zf_ = 0.044 - WING_DZ + 0.0015           # = _ZF, height of the FC-top sensor leads
        for xn, wn, sgn in ((0.0725, 0.0040, -1), (0.0512, 0.0043, -1)):
            if sgn == sy:
                cv.cut_box((xn - wn, ya, zf_ - 0.0028), (xn + wn, yb, 0.050), name='sensor lead notch (GPS / RX / airspeed), open to the roof (D-198)')
        if sy > 0:      # D-199: GPS lead slot, open at the bottom
            cv.cut_box((0.0575 - 0.0038, ya, ZP - 0.001), (0.0575 + 0.0038, yb, 0.0198), name='GPS lead slot, open at the bottom, closed roof (D-199)')
            # D-199: slot open at the bottom (the cover is lowered over the tail lying on the plate), closed at the top
            cv.cut_box((0.1160 - 0.0041, ya, ZP - 0.001), (0.1160 + 0.0041, yb, 0.0198), name='battery tail slot, open at the bottom, closed roof (D-199)')
    # ---- pitot: brass probe + silicone tube stub on its rear
    pt = ctx.part('AVN-006', rgb=(0.8, 0.7, 0.2))
    pt.tube('X', (PIT_X0, PIT_Y, 0.0), PIT_X1 + 0.0005 - PIT_X0, PIT_R, PIT_RI, name='pitot-static probe (EST 160 x 3 mm: RMRC publishes no size; measure)')
    bx0, bx1, bhy, bhz = PIT_B
    pt.box((bx0, PIT_Y - bhy, -bhz), (bx1, PIT_Y + bhy, bhz), name='plastic attachment block (RMRC: "with plastic attachment point"; size EST)')
    for k in ('T', 'S'):
        pt.cylinder('X', (bx1 - 0.0005, PIT_Y + PIT_DY[k], 0.0), 0.0065, PIT_NR, name='%s outlet barb on the block rear face (EST position and OD 2.0)' % ('total-pressure' if k == 'T' else 'static'))
    build_pitot_lines(ctx)


def pitot_paths():
    """D-208: waypoints of the total (T) and static (S) lines: block barb -> aft 11 mm -> up to z 9 -> aft over the spar -> board port (4 mm onto each barb)."""
    out = {}
    for k in ('T', 'S'):
        y = PIT_Y + PIT_DY[k]
        out[k] = [(PIT_B[1] + 0.0015, y, 0.0), (PT_XR, y, 0.0), (PT_XR, y, PT_ZT), (AS_SX[0] - 0.0020, y, PT_ZT)]
    return out


def i2c_path():
    """D-208: airspeed I2C lead, FC I2C pad -> up and out through the cover's airspeed notch -> down beside the cover wall to the plate -> aft on
    the plate (taped) -> down through the left plate window into the core -> outboard in a groove at x 95 (deep under the servo-lead groove,
    shallow over the fin rib tube) -> forward into the board plug."""
    x, y, z = FC_PADS['I2C']
    zpl = ZP + 0.0026                           # bundle on the plate (2 x 2 strands of 1.0 mm)
    return [(x, y, z + 0.0006), (x, y, _ZF), (0.0512, -0.0300, _ZF), (0.0512, -0.0300, zpl), (I2C_X, -0.0300, zpl), (I2C_X, -0.0300, I2C_ZD),
            (I2C_X, -0.150, I2C_ZD), (I2C_X, -0.230, I2C_ZD), (I2C_X, -0.280, I2C_ZS), (I2C_X, PIT_Y, I2C_ZS),
            (AS_B[1][0] - 0.0025, PIT_Y, AS_ZB + T_PCB + 2.1 * MM)]


def _tube_mesh(P, ro, ri, n=16):
    """Closed hollow tube (outer ro, inner ri) swept along the dense centre line P with parallel-transport frames; annular end faces. Outward wound."""
    T = [_unit(_sub(P[min(i + 1, len(P) - 1)], P[max(i - 1, 0)])) for i in range(len(P))]
    a = (1.0, 0.0, 0.0) if abs(T[0][0]) < 0.9 else (0.0, 1.0, 0.0)
    N = _unit(_cross(T[0], a))
    frames = []
    for i in range(len(P)):
        if i:
            N = _unit(_sub(N, _mul(T[i], _dot(N, T[i]))))
        frames.append((N, _cross(T[i], N)))
    V = []
    for (N_, B_), p in zip(frames, P):
        for r in (ro, ri):
            for j in range(n):
                th = 2 * math.pi * j / n
                V.append(_add(p, _add(_mul(N_, r * math.cos(th)), _mul(B_, r * math.sin(th)))))

    def idx(i, o, j):                                   # o = 0 outer ring, 1 inner ring
        return i * 2 * n + o * n + (j % n)
    F = []
    for i in range(len(P) - 1):
        for j in range(n):
            a0, a1, b0, b1 = idx(i, 0, j), idx(i, 0, j + 1), idx(i + 1, 0, j), idx(i + 1, 0, j + 1)
            F += [(a0, a1, b1), (a0, b1, b0)]
            a0, a1, b0, b1 = idx(i, 1, j), idx(i, 1, j + 1), idx(i + 1, 1, j), idx(i + 1, 1, j + 1)
            F += [(a0, b1, a1), (a0, b0, b1)]
    for i, sgn in ((0, -1), (len(P) - 1, 1)):
        for j in range(n):
            o0, o1, i0, i1 = idx(i, 0, j), idx(i, 0, j + 1), idx(i, 1, j), idx(i, 1, j + 1)
            F += [(o0, i1, o1), (o0, i0, i1)] if sgn < 0 else [(o0, o1, i1), (o0, i1, i0)]
    return V, F


def build_pitot_lines(ctx):
    """The two lines as parts (silicone swept along the route, bend radius 4 mm) and their pockets in the foam core (shop cuts, routed from above)."""
    for k in ('T', 'S'):
        P_, _r = _smooth(pitot_paths()[k], 0.004)
        v, t = _tube_mesh(P_, PT_D / 2, 0.0010)          # V RMRC 2 mm ID
        ctx.part('AVN-009-' + k, rgb=(0.85, 0.85, 0.8)).mesh(v, t, name='silicone tubing 2 / 4 mm along the CAD route (D-208)')
    core = ctx.components['WNG-001']
    bx0, bx1, bhy, bhz = PIT_B
    core.cut_box((-0.003, PIT_Y - bhy - 0.0005, -bhz - 0.0005), (bx0, PIT_Y + bhy + 0.0005, bhz + 0.0005),
                 name='pitot nose channel: the attachment block slides in from the front, filled with foam and epoxy after (D-208)')
    yl, yh = PIT_Y - 0.0055, PIT_Y + 0.0055
    core.cut_box((bx0, yl, -0.0035), (PT_XR + 0.0025, yh, 0.0170), name='pitot line pocket behind the probe, open through the upper skin, taped after (D-208)')
    core.cut_box((PT_XR + 0.0025, yl, PT_ZT - 0.0023), (AS_B[0][0] + 0.0005, yh, 0.0170), name='pitot line slot over the spar, open through the upper skin (D-208)')
    (ax0, ay0), (ax1, ay1) = AS_B
    core.cut_box((ax0 - 0.0005, ay0 - 0.0005, AS_ZB - 0.0005), (ax1 + 0.0005, ay1 + 0.0005, 0.0170), name='airspeed board pocket, open through the upper skin, taped after (D-208)')


def _arm_loop(cx, cy, ux, uy):
    """Tapered servo arm outline (hub r 4, tip r 2, EST) from the hub centre towards unit (ux, uy), tip at ARM_R."""
    ph = math.atan2(uy, ux)
    pts = [(cx + 4.0 * MM * math.cos(ph + math.radians(90 + 180 * i / 8)), cy + 4.0 * MM * math.sin(ph + math.radians(90 + 180 * i / 8)))
           for i in range(9)]
    tx, ty = cx + ux * ARM_R, cy + uy * ARM_R
    pts += [(tx + 2.0 * MM * math.cos(ph + math.radians(-90 + 180 * i / 8)), ty + 2.0 * MM * math.sin(ph + math.radians(-90 + 180 * i / 8)))
            for i in range(9)]
    return pts


def build_mechanisms(ctx):
    for s, sy in (('R', 1), ('L', -1)):
        yc = sy * SERVO_Y
        sv = ctx.part('MEC-001-' + s, rgb=(0.2, 0.2, 0.2))
        sv.box((SV_X0, yc - SV_DY, SV_Z0), (SV_X1, yc + SV_DY, SV_Z1), name='servo case (overall 28.4 x 26.7 x 13.0; ears and output boss "-")')
        sv.cylinder('Z', (0.1305, yc, SV_Z1), 0.003, 0.0020, name='servo lead strain-relief boot (EST)')
        # arm: neutral tip points inboard, perpendicular to the rod (rod parallel to x)
        ux, uy = 0.0, -sy
        ar = ctx.part('MEC-002-' + s, rgb=(0.9, 0.9, 0.9))
        loops = [_arm_loop(SV_XS, yc, ux, uy), _ring(SV_XS, yc, 1.1 * MM, 12), _ring(SV_XS, yc + uy * ARM_R, 0.75 * MM, 12)]
        ar.prism('Z', ARM_Z0, loops, ARM_T, name='servo arm (hub bore for the 23T spline; hole row beyond the used hole "-")')
        # screw
        hw = ctx.part('HWC-002-' + s, rgb=(0.7, 0.7, 0.75))
        k9.hw_screw(hw, 'Z', (SV_XS, yc, ARM_Z1), -1, 'M2', 0.006, 'pan', name='M2x6 pan screw')
        ctx.seat('MEC-001-' + s, 'HWC-002-' + s, 'output-shaft thread for the arm screw', bodies=('shank',))
        # horn: base plate + blade with the rod hole
        zb = max(zu(HORN_X0 - 0.002), zu(HORN_X0), zu(HORN_X1))      # D-194: base plate flat on the highest skin point it covers (epoxy fills the rest)
        hy = ROD_Y(sy)
        hn = ctx.part('MEC-004-' + s, rgb=(0.9, 0.9, 0.9))
        hn.box((HORN_X0 - 0.002, hy - 4 * MM, zb), (HORN_X1, hy + 4 * MM, zb + 1.0 * MM), name='horn base plate (EST 20 x 8 x 1.0)')
        blade = _rrect(HORN_X0, zb + 1.0 * MM, HORN_X1, HORN_TOP, 1.5 * MM, 3)
        hn.prism('Y', hy - 1.0 * MM, [blade, _ring(HORN_XH, ROD_Z, 0.75 * MM, 12)], 2.0 * MM, name='horn blade 2 mm (hole at R 12.9 from the hinge)')
        # pushrod: Z-bend pin in the arm hole, rod to the horn, clevis straddling the blade
        tipx, tipy = SV_XS, yc + uy * ARM_R
        rd = ctx.part('MEC-003-' + s, rgb=(0.6, 0.6, 0.6))
        rd.cylinder('Z', (tipx, tipy, ARM_Z0 + 0.0001), ROD_Z - ARM_Z0 - 0.0001, ROD_D / 2, name='rod Z-bend pin (flush with the arm underside)')
        xe = HORN_XH - 0.0040                                   # clevis body starts here (4 mm before the hole)
        rd.cylinder('X', (tipx, tipy, ROD_Z), xe - tipx, ROD_D / 2, name='pushrod')
        rd.tube('X', (xe, tipy, ROD_Z), 0.0020, 1.5 * MM, ROD_D / 2, name='clevis sleeve (EST OD 3.0, 2 mm; fork cheeks follow)')
        for sg in (-1, 1):
            yb = tipy + sg * 1.5 * MM
            rd.box((xe + 0.0020, yb - 0.4 * MM, ROD_Z - 1.6 * MM), (HORN_XH + 1.5 * MM, yb + 0.4 * MM, ROD_Z + 1.6 * MM), name='clevis cheek (EST 0.8 x 3.2)')
        pn = ctx.part('MEC-005-' + s, rgb=(0.8, 0.8, 0.85))
        pn.cylinder('Y', (HORN_XH, tipy - 2.2 * MM, ROD_Z), 4.4 * MM, 0.5 * MM, name='clevis pin 1.0 mm (EST)')
        ctx.seat('MEC-003-' + s, 'MEC-005-' + s, 'pin holes in the clevis cheeks')


def build_landing(ctx):
    sh = ctx.part('GER-001-UR', rgb=(0.9, 0.9, 0.9))
    sh.tube('Z', (XFIN_T, YFIN, FIN_H - 0.012), 0.012, 0.0105, FIN_OD / 2, name='shoe ring')
    sh.cylinder('Z', (XFIN_T, YFIN, FIN_H), 0.003, 0.0105, name='shoe cap')
    sh.box((XFIN_T + 0.0080, YFIN - 0.0105, FIN_H - 0.012), (XFIN_T + 0.0135, YFIN + 0.0105, FIN_H + 0.003), name='shoe plate')
    pd = ctx.part('GER-002-UR', rgb=(0.1, 0.1, 0.1))
    pd.box((XFIN_T + 0.0135, YFIN - 0.0075, FIN_H - 0.009), (X_GROUND, YFIN + 0.0075, FIN_H + 0.003), name='foot pad')
    for pre in ('GER-001-', 'GER-002-'):
        ctx.mirror(pre + 'UR', pre + 'UL', plane='XZ')
        ctx.mirror(pre + 'UR', pre + 'LR', plane='XY')
        ctx.mirror(pre + 'UL', pre + 'LL', plane='XY')
    for st in ST:
        ctx.seat('GER-001-' + st, 'FIN-001-' + ('R' if ST[st][0] > 0 else 'L'), 'shoe bore on the tube end')
    ctx.keepout_halfspace('KO-GROUND', 'X', X_GROUND, 1, tuple('GER-002-' + s for s in ST))


def _arm_line(st):
    """Wire points along the arm (aft side), then through the cup hole to the motor lead exit."""
    ys = (R_M - 0.085)
    a0 = mworld(st, (0.020, -ys, 0.0135))
    h1 = mworld(st, (0.020, 0.0, 0.0135))
    h2 = mworld(st, (-0.0145, 0.0, 0.0135))
    return a0, h1, h2


# D-194: the harness routes were tuned at absolute heights for the old datum; they follow the skin (-WING_DZ) and the FC stack (+1.5 mm pads)
_DZ = -WING_DZ
_ZF = 0.044 - WING_DZ + 0.0015


PH_LAY = 0.080                              # EST light twist of each phase triple, one turn per 80 mm (as tied with the heat-shrink / ties; not a datasheet value)
Z_RUN = 0.017                               # height of the bundles over the plate beside the FC (bundle bottom 2.1 mm over the plate top, 0.8 mm of drape fits)


def phase_route(st, px, py, z_pad):
    """D-199 / D-202 phase-lead bundle (tri of 1.8 mm strands), motor to ESC pad, ENCLOSED over its whole length. Waypoints and the bend radius at each interior
    vertex (m). Cup frame: motor base (inside the ring) -> +x through the cup lead hole (y 5.5 mm) -> 4 mm bend in the cup collar -> -y inside the arm tube bore to
    y -0.150 -> down the bore (offset PH_DT on the exit side) to s = +-18 mm -> 4 mm bend out through the 4.8 mm tube / doubler / sleeve hole -> 4 mm bend aft inside the hub
    conduit HRN-004 (12 mm above the tube axis) -> aft along x to the drop column (x -53) -> 4 mm sideways step to the raceway lane (y 17 upper arms / 21 lower arms) -> 4 mm bend
    into the drop (upper arms) or rise (lower arms) -> 6 mm bend aft into the raceway HRN-003 (z 2.7) -> aft under the tray plate to the tray end (x 22.5) -> open foam ditch under
    the bay cover to x 29 -> up to z 17 inside the cover, aft over the plate beside the FC (|y| >= 15) -> up to z 28 under the roof over the ESC -> slanting down to the ESC pad.
    Smoothed by _smooth (>= 4 mm everywhere). Returns (points, radii, index of the vertex whose following leg is the free run over the plate)."""
    sy, sz = ST[st]
    c = CD[st]
    xa, za = ph_arm_xz(st)
    k = arm_up_sign(st)
    pts = [mworld(st, (-0.0135, PH_Y, 0.0)), mworld(st, (PH_XC, PH_Y, 0.0)), mworld(st, (PH_XC, -0.150, 0.0)),
           a2w(st, (xa, HOLE_S + 0.020, za)), a2w(st, (xa, HOLE_S - CD_UOFF, za)), a2w(st, (xa, HOLE_S - CD_UOFF, SIG[st] * k * CD_TT))]
    rad = [0.004, 0.040, 0.040, 0.004, 0.004]
    yl = c['yl']
    pts += [(XV, c['y1'], c['z1']), (XV, yl, c['z1']), (XV, yl, RW_ZB), (RW_XR, yl, RW_ZB), (RW_XR, yl, Z_RUN)]
    rad += [0.004, 0.004, 0.006, 0.006, 0.006]
    i_sag = len(pts) - 1
    if sz > 0:
        pts += [(0.068, yl, Z_RUN), (0.068, yl, 0.028), (0.078, yl, 0.028)]
    else:
        pts += [(0.074, yl, Z_RUN), (0.074, yl, 0.028), (0.088, yl, 0.028)]
    rad += [0.006, 0.0045, 0.008]
    pts += [(px, py, z_pad)]
    return pts, rad, i_sag


def phase_path(st, px, py, z_pad):
    """Dense smooth centre line of the bundle (with the drape on the free run over the plate) and the effective bend radii."""
    pts, rad, i_sag = phase_route(st, px, py, z_pad)
    return _smooth(pts, rad, sag={i_sag: (0.0008, (0, 0, -1))})


# D-198 bottom-up mass of the lumped harness remainder HRN-001 (replaces the 50.9 g "110 g allocation less itemised parts"). The 400 mm stock leads of the
# motors are inside the 65 g motor mass (T-Motor page: 55 g without cables, 65 g with), so only the length beyond 0.40 m (+ 30 mm splice overlap) is added.
WIRE_G_PER_M = {20: 7.1, 26: 2.0, 28: 1.2}   # V 20 AWG: Pimoroni dual silicone 14.2 g per metre for 2 conductors (shop.pimoroni.com/en-us/products/dual-silicone-wire-per-metre, 2026-11-15); 26 / 28 AWG: EST (copper 1.15 / 0.72 g/m + insulation)


def _plen(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def hrn_items():
    ext = 0.0
    for st in ST:
        px, py = ESC_PADS[st]
        ext += 3 * max(0.0, _plen(phase_path(st, px, py, ESC_TOP + 0.002)[0]) - 0.40 + 0.030)
    return [('phase-lead extensions: 12 strands of 20 AWG, CAD route beyond the 0.40 m stock lead + 30 mm splice (%.2f m)' % ext, round(ext * WIRE_G_PER_M[20], 1)),
            ('12 splices: solder + 15 mm heat-shrink, 0.15 g each (EST)', 1.8),
            ('ESC signal ribbon 6 x 26 AWG x 73 mm (CAD) at 2.0 g/m (EST)', round(6 * 0.073 * WIRE_G_PER_M[26], 1)),
            ('RX / GPS leads: 10 conductors of 28 AWG x about 70 mm at 1.2 g/m (EST) + 2 JST plugs 0.5 g each (EST)', round(10 * 0.070 * WIRE_G_PER_M[28] + 1.0, 1)),
            ('airspeed I2C lead (D-208): 4 conductors of 28 AWG x %.0f mm (CAD route to the left wing tip) at 1.2 g/m (EST) + JST plug 0.5 g (EST)' % (_plen(i2c_path()) * 1e3),
             round(4 * _plen(i2c_path()) * WIRE_G_PER_M[28] + 0.5, 1)),
            ('servo leads: the 3-wire leads are in the 20.5 g servo mass (EST: stock length reaches the FC pads), plus 2 groove fish-wire ties', 0.2),
            ('heat-shrink sleeves at the cup collar / floor hole, ties, foam tape, solder (EST)', 5.0)]


HRN_ITEMS = hrn_items()
PARTS['HRN-001']['mass_g'] = round(sum(g for _n, g in HRN_ITEMS), 1)
PARTS['HRN-001']['name'] = 'Harness remainder, bottom-up (D-198): phase-lead extensions, splices, ESC ribbon, sensor leads, servo ties, sleeves / ties / tape / solder - lumped'


def _wire_s(ctx, eid, wp, R, d, offs, lay=None, sag=None, th0=0.0, extra=None):
    """Register a smooth wire: waypoints wp, radii R, strands of diameter d at offsets offs (optionally lightly twisted). Returns (dense line, r_eff list)."""
    P, reff = _smooth(wp, R, sag=sag)
    st = _strands_s(P, d, offs, lay, th0)
    if extra:
        st = st + extra
    ctx.wire(eid, P, dia=ELEC[eid], strands=st)
    _terms(ctx, eid)
    return P, reff


def build_harness(ctx):
    build_raceway(ctx)
    h = ctx.part('HRN-001', proxy=True)
    h.cylinder('X', (0.030, 0.0, 0.005), 0.002, 0.001, name='harness lump')
    z_pad = ESC_TOP + 0.002
    bx, by = ESC_PADS['BAT']
    # XT60 female half (mated to the male on the pack lead), tail to the ESC battery pads
    hf = ctx.part('HRN-002', rgb=(0.15, 0.15, 0.15))
    hf.prism('X', _xt0 + XT60_L, [_xt60_loop(LEAD_Y1, XT_Z)], XT60_L, name='XT60 female housing')
    xe = _xt0 + 2 * XT60_L
    m = 0.5 * MM
    ctx.wire('E-HRN-01', [(_xt0 + XT60_L - m, LEAD_Y1, XT_Z), (_xt0 + XT60_L + m, LEAD_Y1, XT_Z)], dia=0.003)
    # D-199 battery tail (14 AWG pair, strands +-1.6 mm side by side): out of the female housing back, aft 7 mm, a smooth 6 mm turn inboard along y at x 116 on the plate level THROUGH THE BOTTOM-OPEN SLOT in the cover end wall (the
    # cover is lowered over it), climbing inside the cover to z 23.5 over the ESC aft edge, then forward and down onto the BAT pad. Under the cover from y 26.5 on.
    tx = 0.1160
    tail = [(xe - 0.0005, LEAD_Y1, XT_Z), (tx, LEAD_Y1, XT_Z), (tx, 0.030, XT_Z), (tx, by, 0.0235), (bx, by, z_pad)]
    off = [(LEAD_D * 0.53, 0.0), (-LEAD_D * 0.53, 0.0)]
    P_t, r_t = _wire_s(ctx, 'E-HRN-12', tail, [0.006, 0.006, 0.006], LEAD_D, off)
    # D-199 vendor pack power leads (14 AWG, about 100 mm): from the pack end face, out through the tray end-wall notch, down to the skin and along it to the XT60
    # male; they follow the skin (taped), drawn as wires so the exposure count sees them
    leads = []
    for k in (-1, 1):
        dx = k * LEAD_D * 0.53
        xk = PACK_XL + dx
        y1 = LEAD_Y1 + k * LEAD_PITCH / 2
        sk = lambda x_: zu(x_) + LEAD_D / 2 + 0.0024            # on the skin, taped (chord of the convex skin under the arcs: 0.9 mm of lift)
        wp = [(xk, PACK_L / 2 - 0.0001, PACK_ZL), (xk, y1, PACK_ZL), (xk, y1, sk(xk) + 0.002)]
        wp += [(x_, y1, sk(x_)) for x_ in (0.018, 0.030, 0.042, 0.054, 0.066, 0.076)]
        wp += [(_xt0, y1, XT_Z)]
        Pk, rk = _smooth(wp, [0.004, 0.005] + [0.04] * (len(wp) - 3))
        leads.append((Pk, rk))
    ctx.wire('E-HRN-13', leads[1][0], dia=ELEC['E-HRN-13'], strands=[(leads[0][0], LEAD_D), (leads[1][0], LEAD_D)])
    _terms(ctx, 'E-HRN-13')
    # balance lead (5 conductors bundled, 1.2 mm class): end face aft of the strap, over the top edge, inboard along the pack top, JST-XH plug
    bxl = BAL_X
    zt = PACK_Z0 + PACK_H
    wpb = [(bxl, PACK_L / 2 - 0.0001, PACK_ZL), (bxl, PACK_L / 2 + 0.0020, PACK_ZL), (bxl, PACK_L / 2 + 0.0020, zt + 0.0012), (bxl, 0.017, zt + 0.0012)]
    Pb, rb = _smooth(wpb, 0.0015)
    ctx.wire('E-HRN-14', Pb, dia=ELEC['E-HRN-14'], strands=[(Pb, 1.2 * MM)])
    _terms(ctx, 'E-HRN-14')
    # phase leads: smooth, lightly twisted triples (D-199)
    for i, st in enumerate(ST):
        px, py = ESC_PADS[st]
        eid = 'E-HRN-%02d' % (2 + i)
        P, reff = phase_path(st, px, py, z_pad)
        sts = _strands_s(P, PH_D, _tri(PH_D), PH_LAY, 0.7 * i)
        ctx.wire(eid, P, dia=ELEC[eid], strands=sts)
        _terms(ctx, eid)
    sx, sy_ = ESC_PADS['SIG']
    fx, fy, fz = FC_PADS['ESC']
    # D-194: ESC signal ribbon straight inboard along y = 0 over the ESC at 24 mm, down at x 78 (4 mm ahead of the ESC), into the FC stack between the
    # boards at 19.1 mm to the ESC pad on the bottom board. 6 x 26 AWG as a 3 x 2 bundle (not a flat ribbon: no in-plane inner strand shortening). D-199: smooth, drape 1 mm
    _zr = ESC_TOP + 0.0046
    pts = [(sx, sy_, z_pad), (sx - 0.007, sy_, _zr), (0.0905, sy_, _zr), (0.0800, sy_, fz + 0.0020), (fx, fy, fz + 0.0016)]
    wd = 1.3 * MM                                              # EST 26 AWG silicone OD
    rib = [((j % 3 - 1) * wd, (j // 3 - 0.5) * wd) for j in range(6)]
    _wire_s(ctx, 'E-HRN-06', pts, [0.004, 0.008, 0.008], wd, rib, sag={1: (0.0010, (0, 0, -1))})
    core = ctx.components['WNG-001']
    for i, (key, sg) in enumerate((('S5', 1), ('S6', -1))):
        x, y, z = FC_PADS[key]
        yc = sg * SERVO_Y
        z0 = z + 0.0006
        # D-198: out of the FC aft between the boards, over the plate to the window at |y| 24 mm, down through the plate window and a slit in the skin into a
        # groove in the foam core 3 mm under the upper skin (ribbon 3 x 1.2 mm), outboard along y at x 83 mm, then aft along the skin to the servo pocket wall.
        # Only the last 6 mm (pocket wall to the lead boot) is exposed.
        zg1 = servo_zc(SRV_XD)
        xs_ = [0.083, 0.097, 0.110, 0.1215]
        pts = [(x, y, z0), (0.0775, y, z0), (SRV_XD, sg * SRV_YD, z0), (SRV_XD, sg * SRV_YD, zg1), (SRV_XD, sg * SRV_YG, zg1)]
        pts += [(xx, sg * SRV_YG, servo_zc(xx)) for xx in xs_[1:]]
        pts += [(0.1265, sg * SRV_YG, 0.0083), (0.1305, yc, SV_Z1 + 0.003)]
        _wire_s(ctx, 'E-HRN-%02d' % (7 + i), pts, 0.003, 1.2 * MM, [(-1.2 * MM, 0.0), (0.0, 0.0), (1.2 * MM, 0.0)])
        # grooves in the core (routed, shop cuts): drop slot, y run, x run following the skin
        ya, yb = sorted((sg * (SRV_YD - 0.0045), sg * (SRV_YD + 0.0045)))
        core.cut_box((SRV_XD - 0.0035, ya, zg1 - 0.0020), (SRV_XD + 0.0035, yb, 0.0150), name='servo lead drop slot through the skin (D-198)')
        ya, yb = sorted((sg * (SRV_YD - 0.0045), sg * (SRV_YG + 0.0030)))
        core.cut_box((SRV_XD - 0.0030, ya, zg1 - 0.0016), (SRV_XD + 0.0030, yb, zg1 + 0.0016), name='servo lead groove along y, 3 mm under the skin (D-198)')
        loop = [(xx, servo_zc(xx) - 0.0016) for xx in [0.0800, 0.083, 0.097, 0.110, 0.1215, 0.1250]] + [(xx, servo_zc(xx) + 0.0016) for xx in [0.1250, 0.1215, 0.110, 0.097, 0.083, 0.0800]]
        ya, yb = sorted((sg * (SRV_YG - 0.0030), sg * (SRV_YG + 0.0030)))
        core.cut_prism('Y', ya, [loop], yb - ya, name='servo lead groove along x, following the skin (D-198)')
    # RX CRSF wire: FC top board RX pad -> RX pads
    x, y, z = FC_PADS['RX']
    (rx0, ry0), _ = RX_B
    rpx, rpy = rx0 + 1.2 * MM, ry0 + 2.2 * MM + 1.5 * 2.8 * MM
    pts = [(x, y, z + 0.0006), (x, y, _ZF), (x, rpy, _ZF), (rpx, rpy, _ZF), (rpx, rpy, ZP + 1.2 * MM + 0.0006)]
    wd = 1.0 * MM
    _wire_s(ctx, 'E-HRN-09', pts, 0.0025, wd, [((j % 2 - 0.5) * wd, (j // 2 - 0.5) * wd) for j in range(4)], lay=0.100)
    # GPS cable: GPS plug (inner edge) -> FC GPS pad
    x, y, z = FC_PADS['GPS']
    (gx0, gy0), (gx1, gy1) = GPS_B
    gcx = (gx0 + gx1) / 2
    zp_ = ZP + T_PCB + 1.8 * MM
    pts = [(gcx, gy0 + 2.0 * MM, zp_), (gcx, 0.0243, zp_), (gcx, 0.0243, _ZF), (x, y, _ZF), (x, y, z + 0.0006)]    # D-199: leaves the plug inboard (the old route rose through the GNSS patch footprint), crosses the cover wall low through a bottom-open slot
    _wire_s(ctx, 'E-HRN-10', pts, 0.0025, wd, [((j % 3 - 1) * wd, (j // 3 - 0.5) * wd) for j in range(6)], lay=0.100)
    # airspeed cable: FC I2C pad -> JST-GH plug on the board at the left wing tip (D-208)
    _wire_s(ctx, 'E-HRN-11', i2c_path(), 0.004, wd, [((j % 2 - 0.5) * wd, (j // 2 - 0.5) * wd) for j in range(4)], lay=0.100)
    hg = 0.0017                                  # groove half width / height round the 2 x 2 bundle (envelope 1.4 mm) + 0.3 mm
    core = ctx.components['WNG-001']
    core.cut_box((I2C_X - hg, -0.0345, I2C_ZD - hg), (I2C_X + hg, -0.0280, 0.0150), name='I2C lead drop slot through the skin under the left plate window (D-208)')
    core.cut_box((I2C_X - hg, -0.2300, I2C_ZD - hg), (I2C_X + hg, -0.0280, I2C_ZD + hg), name='I2C lead groove along y, deep (under the servo-lead groove) (D-208)')
    core.cut_prism('X', I2C_X - hg, [[(-0.2300, I2C_ZD - hg), (-0.2300, I2C_ZD + hg), (-0.2800, I2C_ZS + hg), (-0.2800, I2C_ZS - hg)]], 2 * hg,
                   name='I2C lead groove ramp (D-208)')
    core.cut_box((I2C_X - hg, PIT_Y - hg, I2C_ZS - hg), (I2C_X + hg, -0.2800, I2C_ZS + hg), name='I2C lead groove along y, shallow (over the fin rib tube) (D-208)')
    core.cut_box((AS_B[1][0], PIT_Y - hg, AS_ZB + T_PCB), (I2C_X + hg, PIT_Y + hg, I2C_ZS + hg), name='I2C lead groove into the board pocket (D-208)')


def build_assembly(ctx):
    """Joints and contacts for every mechanical edge, after all parts exist (wires are registered by the harness)."""
    hw = ctx.part('HRD-001', proxy=True)
    hw.cylinder('X', (0.100, 0.0, 0.0), 0.002, 0.001, name='hardware lump')
    comps = ctx.components
    for e in EDGES:
        via = e['via']
        if e['owner'] == 'harness' and e['id'] in ELEC:
            continue
        a, b = comps.get(e['part_a']), comps.get(e['part_b'])
        if a is None or b is None:
            continue
        ba, bb = a.bbox(), b.bbox()
        lo = [max(ba[0][i], bb[0][i]) for i in range(3)]
        hi = [min(ba[1][i], bb[1][i]) for i in range(3)]
        at = tuple((lo[i] + hi[i]) / 2 if lo[i] <= hi[i] else (min(ba[1][i], bb[1][i]) + max(ba[0][i], bb[0][i])) / 2
                   for i in range(3))
        if via == 'CT-TAPE-HINGE':
            sgn = 1 if e['part_a'].endswith('R') else -1
            ctx.revolute(e['id'], e['part_a'], e['part_b'], (XH, sgn * (ELEV_Y0 + ELEV_Y1) / 2, zu(XH)), 'Y',
                         limits=(-ELEV_POSE, ELEV_POSE))
        elif via == 'CT-CLEVIS':
            ctx.revolute(e['id'], e['part_a'], e['part_b'], at, e['motion']['axis'])
        elif via in ('CT-A-M25-SHCS-MOTOR', 'CT-A-PROP-NUT', 'CT-A-PROP-ADAPTER', 'CT-SERVO-SPLINE') or e.get('hardware'):
            ctx.rigid(e['id'], e['part_a'], e['part_b'], at)
        else:
            ctx.contact(e['id'], via)


# D-208: pitot line lengths and masses from the CAD route (silicone rubber 1.15 g/cm3 EST; 2 / 4 mm V RMRC)
PITOT_LINE_M = {}
for _k in ('T', 'S'):
    _P, _r = _smooth(pitot_paths()[_k], 0.004)
    PITOT_LINE_M[_k] = sum(math.dist(_P[i], _P[i + 1]) for i in range(len(_P) - 1))
    PARTS['AVN-009-' + _k]['mass_g'] = round(math.pi / 4 * (PT_D ** 2 - 0.002 ** 2) * PITOT_LINE_M[_k] * 1.15e6, 1)
    PARTS['AVN-009-' + _k]['name'] += ', %.0f mm (CAD route)' % (PITOT_LINE_M[_k] * 1e3)
