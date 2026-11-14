"""jigs.py - shop jigs, drawn with the same fusionkit shapes as the aircraft and sized from the CAD + params.

Every number is read from the built CAD (ctx: tube, block, fin laminate, motor stack) or params.json, so the jigs move
when D3/E1 move the stations. Jigs are `flight: false` shop aids; nothing here goes into the aircraft model.

JIG-01  Tube-bore / block clocking jig (MF-06, SW: blocks free to rotate on the round spar; tubes must be vertical
        and parallel within 0.5 deg). Two printed tube posts (STL) bolted on a laser-cut base board at the motor-tube
        stations, plus a laser-cut top bar with two tube holes. Dummy tubes stand in the posts, pass through both
        through-core blocks, and the top bar ties their upper ends: both bores are then vertical, parallel and at
        the station spacing while the spar + block bond cures.
JIG-02  Fin-alignment collar (MF-08 / fins BUILD step 11 root bond). A C-collar that slides on the motor tube with a
        slot one laminate thick (+0.3 mm) in the plane through the tube axis: the half-fin cures coplanar with the
        tube, i.e. square to the wing.
JIG-03  Cant gauge (MF-07, D-61: 7 deg tangential cant). Sits flat on the outboard fin face (relieved over the LE
        edge strip) and against the motor tube. Its datum face D is parallel to the motor bell top of THAT station
        as modelled (from the CAD motor rotation). Zero an angle cube on D, move it to the bell top: it must read
        0.0 +/- 0.5 deg in two directions. Variant A = UR/LL, B = UL/LR (like the mounts).
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cad_source as cs           # noqa: E402  (sets the fusion path)
import fusionkit as fk            # noqa: E402

BORE_CLEAR_M = 0.0003             # fins/BUILD.md step 5: "22.3 mm bores slide on the tube"
SLOT_CLEAR_M = 0.0003             # laminate slot clearance (9.6 + 0.3)


class _Ctx:
    """Minimal context so fusionkit.Component can record shapes (no backend)."""
    sub = 'jigs'

    class backend:                # noqa: N801
        @staticmethod
        def body(comp, shape):
            return None


def _part(pid, name):
    return fk.Component(_Ctx(), pid, {'name': name, 'material': 'PETG (printed)', 'flight': False})


def circle(cx, cy, r, n=48, phase=0.0):
    return [(cx + r * math.cos(phase + 2 * math.pi * i / n), cy + r * math.sin(phase + 2 * math.pi * i / n))
            for i in range(n)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def geometry(ctx, P):
    """Numbers the jigs need, from the built CAD (metres)."""
    v = lambda k, u=None: _val(P, k, u)
    g = {}
    g['tube_r'] = v('fins.tube.od_m', 'm') / 2
    g['tube_x'] = v('fins.tube.x_m', 'm')
    g['tube_y'] = v('fins.y_m', 'm')
    g['t_fin'] = v('fins.layers') * v('fins.board_t_m', 'm')
    g['cant'] = v('propulsion.stations.cant_deg', 'deg')
    tube = ctx.components.get('FIN-002-R')
    if tube is not None:                                   # the modelled tube wins over params if they differ
        lo, hi = tube.bbox()
        g['tube_x'], g['tube_y'] = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
        g['tube_r'] = (hi[0] - lo[0]) / 2
        g['tube_z'] = (lo[2], hi[2])
    fin = ctx.components.get('FIN-001-UR')
    if fin is not None:
        lam = next(s for s in fin.shapes if s.kind == 'prism' and s.axis == 'Y')
        g['fin_y0'], g['fin_y1'] = sorted((lam.offset, lam.offset + lam.depth))
        g['t_fin'] = abs(lam.depth)
    else:
        g['fin_y0'], g['fin_y1'] = g['tube_y'] - g['t_fin'] / 2, g['tube_y'] + g['t_fin'] / 2
    g['shaft'] = {}
    for st in ('UR', 'UL', 'LR', 'LL'):
        m = ctx.components.get('PRP-001-' + st)
        if m is not None:
            R = m.R
            g['shaft'][st] = (-R[0][0], -R[1][0], -R[2][0])     # R . (-x): thrust axis (local -x = forward)
    return g


def _val(P, key, unit=None):
    d = P
    for k in key.split('.'):
        d = d[k]
    if isinstance(d, dict) and 'value' in d:
        if unit and d.get('unit') != unit:
            raise KeyError('%s unit %s != %s' % (key, d.get('unit'), unit))
        return d['value']
    return d


# ----------------------------------------------------------------------------- JIG-01 posts + board + bar
POST = dict(flange=0.064, flange_t=0.006, ring_r=0.0155, ring_h=0.045, bolt=0.0225, bolt_r=0.00225)


def jig01_post(g, side):
    """Printed tube post at the station (x, side*y): solid flange (the tube bottoms on it) + socket ring."""
    x, y = g['tube_x'], side * g['tube_y']
    p = _part('JIG-01-' + ('R' if side > 0 else 'L'), 'tube post')
    f, b = POST['flange'] / 2, POST['bolt']
    holes = [circle(x + sx * b, y + sy * b, POST['bolt_r'], 24) for sx in (-1, 1) for sy in (-1, 1)]
    p.prism('Z', 0.0, [rect(x - f, y - f, x + f, y + f)] + holes, POST['flange_t'], name='post flange')
    bore = g['tube_r'] + BORE_CLEAR_M / 2
    p.prism('Z', POST['flange_t'], [circle(x, y, POST['ring_r'], 64), circle(x, y, bore, 64)], POST['ring_h'],
            name='post socket')
    return p


def jig01_flat(g):
    """Laser-cut parts of JIG-01 (mm, board frame: origin at the tube midpoint, u along the span, v along x).
    Returns [(name, loops_cut, marks, texts)]."""
    ty = g['tube_y'] * 1000
    f, b, br = POST['flange'] * 500, POST['bolt'] * 1000, POST['bolt_r'] * 1000
    W, H = 2 * ty + 2 * 70.0, 170.0
    board = [rect(-W / 2, -H / 2, W / 2, H / 2)]
    marks = []
    for s in (-1, 1):
        cx = s * ty
        board += [circle(cx + sx * b, sy * b, br, 24) for sx in (-1, 1) for sy in (-1, 1)]
        marks.append(rect(cx - f, -f, cx + f, f))
        marks.append([(cx - 6, 0), (cx + 6, 0)])
        marks.append([(cx, -6), (cx, 6)])
    marks.append([(0, -H / 2 + 5), (0, H / 2 - 5)])          # aircraft centre line y = 0
    le = -g['tube_x'] * 1000                                  # wing LE line (x = 0) relative to the tube line
    marks.append([(-W / 2 + 5, le), (W / 2 - 5, le)])
    texts = [(-W / 2 + 8, H / 2 - 14, 6, 'JIG-01 BASE  post centres %.1f mm' % (2 * ty)),
             (-W / 2 + 8, le + 2, 4, 'wing LE line (x 0)'), (4, -H / 2 + 8, 4, 'centre line y 0')]
    bw, bh = 2 * ty + 80.0, 50.0
    hole_r = g['tube_r'] * 1000 + 0.2
    bar = [rect(-bw / 2, -bh / 2, bw / 2, bh / 2), circle(-ty, 0, hole_r, 72), circle(ty, 0, hole_r, 72)]
    bar_texts = [(-bw / 2 + 50, -bh / 2 + 6, 5, 'JIG-01 TOP BAR  holes %.1f mm at %.1f mm' % (2 * hole_r, 2 * ty))]
    return [('JIG-01 base board', board, marks, texts), ('JIG-01 top bar', bar, [], bar_texts)]


# ----------------------------------------------------------------------------- JIG-02 fin-alignment collar
def jig02_collar(g):
    x, y = g['tube_x'], g['tube_y']
    zt = g.get('tube_z', (-0.172, 0.172))[1]
    z0, h = zt - 0.027, 0.025
    rb = g['tube_r'] + BORE_CLEAR_M / 2
    ro, wall, arm = 0.017, 0.004, 0.060
    yc = (g['fin_y0'] + g['fin_y1']) / 2 - y                   # fin mid-plane offset from the tube axis
    hs = g['t_fin'] / 2 + SLOT_CLEAR_M / 2
    yo = hs + wall
    a_in = math.asin(hs / rb)
    a_out = math.asin(yo / ro)
    loop = [(math.sqrt(rb * rb - hs * hs), yc + hs), (arm, yc + hs), (arm, yc + yo),
            (math.sqrt(ro * ro - yo * yo), yc + yo)]
    n = 56
    for i in range(1, n):                                      # outer arc, +a_out -> 2pi - a_out
        a = a_out + (2 * math.pi - 2 * a_out) * i / n
        loop.append((ro * math.cos(a), yc + ro * math.sin(a)))
    loop += [(math.sqrt(ro * ro - yo * yo), yc - yo), (arm, yc - yo), (arm, yc - hs),
             (math.sqrt(rb * rb - hs * hs), yc - hs)]
    for i in range(1, n):                                      # bore arc back, -a_in -> -(2pi - a_in)
        a = -a_in - (2 * math.pi - 2 * a_in) * i / n
        loop.append((rb * math.cos(a), rb * math.sin(a)))
    loop = [(x + u, y + w) for u, w in loop]
    p = _part('JIG-02-R', 'fin-alignment collar')
    p.prism('Z', z0, [loop], h, name='fin collar')
    return p


# ----------------------------------------------------------------------------- JIG-03 cant gauge
def jig03_gauge(g, st):
    """Gauge for station st, built in place on the outboard fin face. Loft along Z (two sections) so the datum
    face D can carry the full 3-D tilt of the motor axis while every other face stays square to the tube."""
    sy, sz = cs.SIGNS[st]
    s = g['shaft'].get(st)
    if s is None:
        return None
    x, y = g['tube_x'], sy * g['tube_y']
    rb = g['tube_r'] + 0.00015
    wf = (g['fin_y1'] - g['tube_y'])                         # outboard fin face, from the tube axis (m)
    relief = 0.0015                                          # over the 10 x 1 mm LE edge strip
    u_rel, u_end, w_out = 0.023, 0.042, 0.036
    w_d0 = rb + 0.0005                                       # face D spans w_d0 .. w_out
    zc, h = sz * 0.072, 0.024
    n = (s[0], s[1] * sy, s[2])                              # normal of D in (u, w, z): w outboard, z world
    u0, wc = -0.016, (w_d0 + w_out) / 2

    def uD(w, z):
        return u0 - (n[1] * (w - wc) + n[2] * (z - zc)) / n[0]

    wr = wf + relief
    a1 = math.asin(min(wr / rb, 1.0))
    arc = [(rb * math.cos(math.pi / 2 - (math.pi / 2 - a1) * i / 16), rb * math.sin(math.pi / 2 - (math.pi / 2 - a1) * i / 16))
           for i in range(17)]                               # (0, rb) -> (.., wr) on the tube

    def section(z):
        pts = [(uD(w_out, z), w_out), (uD(w_d0, z), w_d0), (0.0, w_d0)] + arc + \
              [(u_rel, wr), (u_rel, wf), (u_end, wf), (u_end, w_out)]
        return [(x + u, y + sy * w) for u, w in pts]

    secs = [(zc - h / 2, section(zc - h / 2)), (zc + h / 2, section(zc + h / 2))]
    p = _part('JIG-03-' + st, 'cant gauge')
    p.loft('Z', secs, smooth=False, name='cant gauge')
    ang = math.degrees(math.acos(max(-1.0, min(1.0, -s[0]))))
    return p, ang


def jobs(ctx, P, issues):
    """Mesh jobs for the printed jigs + the flat (laser) jig parts."""
    g = geometry(ctx, P)
    parts = [(jig01_post(g, 1), 'JIG-01', 'R'), (jig01_post(g, -1), 'JIG-01', 'L'), (jig02_collar(g), 'JIG-02', 'R')]
    angles = {}
    for st in ('UR', 'UL', 'LR', 'LL'):
        r = jig03_gauge(g, st)
        if r is None:
            issues.append('JIG-03-%s: no motor PRP-001-%s in the CAD, gauge not made' % (st, st))
            continue
        parts.append((r[0], 'JIG-03', st))
        angles[st] = r[1]
    out = []
    for comp, base, st in parts:
        spec = JIG_PRINT[base]
        out.append({'id': comp.id, 'part': comp.id, 'base': base, 'station': st, 'group': '',
                    'material': 'PETG', 'colour': '', 'orient': dict(spec['orient']),
                    'matrix': comp.matrix(), 'bodies': [cs.shape_to_json(s) for s in comp.shapes],
                    'cad_volume_mm3': sum(s.volume_centroid()[0] for s in comp.shapes) * 1e9})
    return out, jig01_flat(g), g, angles


JIG_PRINT = {
    'JIG-01': dict(orient={'down': (0, 0, -1)}, perimeters='4', infill='40 %', layer='0.2', supports='none',
                   qty_extra=0, note='flange on the bed; bore = tube OD + 0.3 mm; bolt to the base board with 4 x M4'),
    'JIG-02': dict(orient={'axes': 'Z'}, perimeters='3', infill='30 %', layer='0.2', supports='none',
                   qty_extra=3, note='4 total: one per half-fin root bond'),
    'JIG-03': dict(orient={'axes': 'Z'}, perimeters='3', infill='40 %', layer='0.2', supports='none', qty_extra=0,
                   note='face D is the cant datum: do not sand it; write A or B on the part'),
}
