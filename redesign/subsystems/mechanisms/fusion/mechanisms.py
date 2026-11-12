"""K09-L mechanisms (MEC, D6, revision D6-R2): elevon drive, one servo per side for two linked panels.

Per side (built for the right side, mirrored through DP-SYM with k9.pair):

  MEC-008 servo frame     printed PETG tray bonded in a core pocket opening on the LOWER skin, x 0.172-0.208; the
                          top plate is a 4 mm rim with a window over the case (D6-R2); the servo ears sit in slots
                          in its end walls (captured, no screws along y: there is no tool
                          access along the span inside the pocket)
  MEC-001 servo           Savox SH-0255MG+ laid on its side, shaft along y, case base flush with the lower skin
  MEC-002 servo arm       supplied single arm, hole at 15.6 mm (0.61 x the horn radius)
  MEC-003 pushrod         2-56 steel rod, Z-bend in the arm, steel clevis + keeper on the horn, below the lower skin
  MEC-004 control horn    printed PETG through-panel horn in the INBOARD panel at y 0.285: blade in a 2.5 mm slot,
                          lower flange, upper backplate, clevis hole 25.5 mm below the hinge axis, and a boss holding
                          the inter-panel rod 16.5 mm below the axis
  MEC-005 inter-panel rod 1/8 in pultruded CF rod (D6-R2, was music wire) on the hinge-parallel line 16.5 mm below the axis, bonded in the bosses of
                          MEC-004 and MEC-006: a rigid bridge that turns with both panels, through D3's 24 x 12 mm
                          notch in the lower half-fin root (fins/params.json#link_slot)
  MEC-006 link horn       the same horn without the clevis hole, in the OUTBOARD panel at y 0.355
  MEC-007 servo cover     printed PETG plate on the lower skin, slot for the arm (its ends are the TE-up stops),
                          2 x M2 screws into the frame
  MEC-009 torque tube     CF 5 x 4 mm along each panel just aft of the bevel (-RI, -RO), through the horn blade:
                          stiffens the tape-skinned foam panel in torsion (one-end drive). The inboard tube covers
                          70 % of the horn-to-root length (mec.tube.cover_frac), the outboard tube the whole panel
  MEC-010 hinge tape      one 25 mm strip per panel on the upper skin (lumped part per side, carried)

Kinematics (team/D6/mech_calcs.py): servo shaft S, arm hole P, horn hole Q, hinge axis A form a four-bar in the x-z
plane at y 0.285. +/-25 deg surface needs -42.9 / +44.7 deg servo. Mechanical stops 5 deg beyond: the panel
bevel (TE down, D1 30 deg) and the arm at the cover slot end (TE up), both at 30 deg.

Edges to wing parts (WNG-001 core, WNG-003 skin, WNG-011/012 panels) are registered only when the wing declares those
parts (same test as make_mechanisms.py, which parks the edges under edges_pending until then).

UNVERIFIED-IN-FUSION: the revolute pair pushrod-arm / pushrod-horn with the wing hinge (closed loop: Fusion may need
the pushrod joints as rigid for the static model); the pushrod loft between two circles; horn prisms with hole loops.
"""
import math
import os

import k09kit as k9

SIDE_R = 'R'
RGB_SERVO, RGB_PRINT, RGB_STEEL, RGB_CF, RGB_TAPE = (0.15, 0.15, 0.18), (0.95, 0.50, 0.10), (0.70, 0.70, 0.72), \
    (0.10, 0.10, 0.10), (0.85, 0.85, 0.70)
WING = {'core': 'WNG-001', 'skin': 'WNG-003', 'in': 'WNG-011', 'out': 'WNG-012'}


# ----------------------------------------------------------------------------- numbers
def lval(LP, key, unit=None):
    d = LP['mec']
    for k in key.split('.'):
        d = d[k]
    if unit is not None and d.get('unit') != unit:
        raise KeyError('mechanisms/params.json mec.%s is in %s, not %s' % (key, d.get('unit'), unit))
    return d['value']


def load_local(path=None):
    import json
    path = path or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'params.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def geometry(P, LP, coords):
    """Every derived dimension of the right side (m). Shared by build(), make_mechanisms.py and the D6 calcs."""
    v = lambda k, u=None: k9.val(P, k, u)
    l = lambda k, u=None: lval(LP, k, u)
    c = v('wing.chord_m', 'm')
    hf = k9.hinge_frac(P)
    G = {'c': c, 'hf': hf}
    G['xh'] = hf * c
    G['zh'] = k9.surface_z(coords, c, hf, 'upper')
    zu = lambda x: k9.surface_z(coords, c, min(max(x / c, 0.0), 1.0), 'upper')
    zl = lambda x: k9.surface_z(coords, c, min(max(x / c, 0.0), 1.0), 'lower')
    G['zu'], G['zl'] = zu, zl
    G['yin'], G['yout'] = v('wing.elevon.inboard_y_m', 'm'), v('wing.elevon.outboard_y_m', 'm')
    G['yf'], G['t_fin'] = v('fins.y_m', 'm'), k9.fin_thickness(P)
    # servo
    L, W, H = l('servo.case_m', 'm')
    G['case'] = (L, W, H)
    G['boss'] = l('servo.spline_boss_m', 'm')
    G['ear_span'], G['ear_t'], G['ear_y'] = l('servo.ear_span_m', 'm'), l('servo.ear_t_m', 'm'), \
        l('servo.ear_y_from_base_m', 'm')
    xs = l('station.shaft_x_m', 'm')
    G['xs'] = xs
    G['ya'] = l('station.arm_plane_y_m', 'm')
    G['yo'] = l('station.outboard_horn_y_m', 'm')
    G['at'], G['aw'], G['rs'] = l('arm.t_m', 'm'), l('arm.w_m', 'm'), l('arm.r_m', 'm')
    aft = l('servo.shaft_from_aft_end_m', 'm')
    G['cx0'], G['cx1'] = xs + aft - L, xs + aft                       # case x range (shaft near the aft end)
    G['cz0'] = zl(xs)                                                  # case base on the lower skin
    G['zs'] = G['cz0'] + l('station.shaft_above_skin_m', 'm')
    G['cz1'] = G['cz0'] + W
    G['cy1'] = G['ya'] - G['at'] / 2 - G['boss']                       # case top (toward the arm)
    G['cy0'] = G['cy1'] - H
    G['ex0'], G['ex1'] = (G['cx0'] + G['cx1']) / 2 - G['ear_span'] / 2, (G['cx0'] + G['cx1']) / 2 + G['ear_span'] / 2
    G['ey0'] = G['cy0'] + G['ear_y']
    # horn / link
    G['rh'], G['rb'] = l('horn.r_m', 'm'), l('horn.bridge_r_m', 'm')
    G['ht'] = l('horn.plate_t_m', 'm')
    G['boss_r'], G['boss_len'] = l('horn.boss_od_m', 'm') / 2, l('horn.boss_len_m', 'm')
    G['pin_r'], G['bore_r'] = l('horn.pin_hole_d_m', 'm') / 2, l('horn.bore_d_m', 'm') / 2
    G['outline'] = [(x / 1000.0, z / 1000.0) for x, z in l('horn.outline_mm', 'mm')]
    G['blade_x'] = [x / 1000.0 for x in l('horn.blade_x_mm', 'mm')]
    G['blade_gap'] = l('horn.blade_bevel_gap_m', 'm')
    th = zu(G['xh']) - zl(G['xh'])                                       # same bevel as wing.py elevon_section
    G['bevel'] = th * math.tan(math.radians(k9.lval(k9.local('wing'), 'elevon.bevel_deg', 'deg')))
    G['flange'] = [x / 1000.0 for x in l('horn.flange_mm', 'mm')]
    G['backplate'] = [x / 1000.0 for x in l('horn.backplate_mm', 'mm')]
    G['Q'] = (G['xh'], G['zh'] - G['rh'])                               # clevis pin (x, z), neutral
    G['B'] = (G['xh'], G['zh'] - G['rb'])                               # bridge rod centre
    G['P'] = (xs, G['zs'] - G['rs'])                                    # arm hole, neutral (arm straight down)
    G['rod_r'] = l('link.d_m', 'm') / 2
    G['rod_y'] = (G['ya'] + G['ht'] / 2 + 0.0003, G['yo'] - G['ht'] / 2 - 0.0003)
    # pushrod, clevis
    G['pr_r'] = l('pushrod.d_m', 'm') / 2
    G['clevis'] = [x / 1000.0 for x in l('pushrod.clevis_mm', 'mm')]
    # torque tubes
    od, idia = l('tube.od_id_m', 'm')
    G['tube_r'], G['tube_ri'] = od / 2, idia / 2
    G['xt'] = G['xh'] + l('tube.x_aft_of_hinge_m', 'm')
    G['zt'] = (zu(G['xt']) + zl(G['xt'])) / 2
    ins = l('tube.end_inset_m', 'm')
    a_in, a_out = l('tube.cover_frac', '-')
    G['tube_in'] = (max(G['yin'][0] + ins, G['ya'] - a_in * (G['ya'] - G['yin'][0])), G['yin'][1] - ins)
    G['tube_out'] = (G['yout'][0] + ins, min(G['yout'][1] - ins, G['yo'] + a_out * (G['yout'][1] - G['yo'])))
    # frame and cover
    G['fw'], G['fc'] = l('frame.wall_m', 'm'), l('frame.clear_m', 'm')
    G['f_rim'] = l('frame.window_rim_m', 'm')
    G['fx0'], G['fx1'] = G['ex0'] - G['fw'], G['ex1'] + G['fw']        # frame outer x (ears in end-wall slots)
    G['fy0'] = G['cy0'] - G['fc'] - G['fw']                            # inboard wall
    G['fy1'] = G['ya'] + G['at'] / 2 + 0.0015                          # open toward the arm; pocket ends here
    G['fz1'] = G['cz1'] + G['fc'] + G['fw']                            # frame top plate upper face
    G['ct'], G['lip'] = l('cover.t_m', 'm'), l('cover.lip_m', 'm')
    stop = l('mech_stop_deg', 'deg')
    lk = (G['xh'], G['zh'], G['rh'], xs, G['zs'], G['rs'])
    th_dn, th_up = theta_of_delta(lk, stop), theta_of_delta(lk, -stop)  # servo angles at the mechanical stops
    G['theta_stop'] = (th_dn, th_up)
    # cover slot: the arm (half width aw/2 at the skin) stops on the slot ends at the mechanical stops
    zsk = G['cz0']
    reach = lambda th: G['xs'] + (G['zs'] - zsk) * math.tan(math.radians(th))
    hw = G['aw'] / 2
    G['slot_x'] = (min(reach(th_dn), reach(th_up)) - hw, max(reach(th_dn), reach(th_up)) + hw)
    G['tape_w'] = l('tape.width_m', 'm')
    return G


# ----------------------------------------------------------------------------- four-bar (x-z plane, y = arm plane)
# lk = (xh, zh, rh, xs, zs, rs): hinge axis A, horn radius, servo shaft S, arm radius (m). Angles in degrees.
# delta > 0 = trailing edge DOWN (horn hole swings forward); theta > 0 = arm hole aft (pushes the horn: TE up).
def horn_hole(lk, delta):
    xh, zh, rh = lk[0], lk[1], lk[2]
    d = math.radians(delta)
    return (xh - rh * math.sin(d), zh - rh * math.cos(d))


def arm_hole(lk, theta):
    xs, zs, rs = lk[3], lk[4], lk[5]
    t = math.radians(theta)
    return (xs + rs * math.sin(t), zs - rs * math.cos(t))


def rod_length(lk):
    p, q = arm_hole(lk, 0.0), horn_hole(lk, 0.0)
    return math.hypot(p[0] - q[0], p[1] - q[1])


def delta_of_theta(lk, theta):
    """Surface angle for a servo angle (bisection on the branch through neutral)."""
    L, p = rod_length(lk), arm_hole(lk, theta)
    f = lambda d: math.hypot(p[0] - horn_hole(lk, d)[0], p[1] - horn_hole(lk, d)[1]) - L
    lo, hi = -80.0, 80.0
    flo = f(lo)
    for _ in range(80):
        mid = (lo + hi) / 2
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


def theta_of_delta(lk, delta):
    lo, hi = -85.0, 85.0
    g = lambda t: delta_of_theta(lk, t) - delta
    glo = g(lo)
    for _ in range(60):
        mid = (lo + hi) / 2
        gm = g(mid)
        if (gm > 0) == (glo > 0):
            lo, glo = mid, gm
        else:
            hi = mid
    return (lo + hi) / 2


def circle(cx, cy, r, n=20):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ----------------------------------------------------------------------------- bodies
def build_servo(part, G):
    L, W, H = G['case']
    part.box((G['cx0'], G['cy0'], G['cz0']), (G['cx1'], G['cy1'], G['cz1']), name='servo case')
    part.box((G['ex0'], G['ey0'], G['cz0']), (G['ex1'], G['ey0'] + G['ear_t'], G['cz1']), name='mounting ears')
    part.cylinder('Y', (G['xs'], G['cy1'], G['zs']), G['boss'], 0.0025, name='spline boss')


def build_arm(part, G):
    xs, zs, w = G['xs'], G['zs'], G['aw']
    loop = [(xs - w / 2, zs + w / 2), (xs + w / 2, zs + w / 2), (xs + w / 2 * 0.6, zs - G['rs'] - w / 2 * 0.6),
            (xs - w / 2 * 0.6, zs - G['rs'] - w / 2 * 0.6)]
    hole = circle(xs, zs - G['rs'], 0.0008, 12)
    part.prism('Y', G['ya'] - G['at'] / 2, [loop, hole], G['at'], name='servo arm')


def build_pushrod(part, G):
    (x0, z0), (x1, z1) = G['P'], G['Q']
    cl_len, cl_w, cl_h = G['clevis'][:3]
    ux, uz = (x0 - x1), (z0 - z1)
    n = math.hypot(ux, uz)
    ux, uz = ux / n, uz / n
    xc, zc = x1 + ux * cl_len, z1 + uz * cl_len                         # clevis end toward the servo
    y = G['ya']
    part.loft('X', [(x0, circle(y, z0, G['pr_r'], 10)), (xc, circle(y, zc, G['pr_r'], 10))], name='pushrod wire')
    part.loft('X', [(x1 - 0.0015, rect(y - cl_w / 2, z1 - cl_h / 2, y + cl_w / 2, z1 + cl_h / 2)),
                    (xc, rect(y - cl_w / 4, zc - cl_h / 4, y + cl_w / 4, zc + cl_h / 4))], name='clevis')


def clip_above(loop, zc):
    """Sutherland-Hodgman clip of a closed (x, z) loop to z >= zc; drops repeated and collinear points."""
    out = []
    for i, p in enumerate(loop):
        q = loop[i - 1]
        if p[1] >= zc:
            if q[1] < zc:
                out.append((q[0] + (p[0] - q[0]) * (zc - q[1]) / (p[1] - q[1]), zc))
            out.append(p)
        elif q[1] >= zc:
            out.append((q[0] + (p[0] - q[0]) * (zc - q[1]) / (p[1] - q[1]), zc))
    pts = [p for i, p in enumerate(out) if math.dist(p, out[i - 1]) > 1e-7]
    keep = []
    for i, p in enumerate(pts):
        a, c = pts[i - 1], pts[(i + 1) % len(pts)]
        if abs((p[0] - a[0]) * (c[1] - a[1]) - (p[1] - a[1]) * (c[0] - a[0])) > 1e-12:
            keep.append(p)
    return keep


def horn_blade_loop(G):
    """Blade outline skin to skin from the panel's bevel (D-82, shifted aft by blade_gap) to xh + blade_x[1]."""
    xh, b, gap = G['xh'], G['bevel'], G['blade_gap']
    xa = xh + G['blade_x'][0]
    xb = xh + G['blade_x'][1]
    xu, xl = max(xa, xh + gap), max(xa, xh + b + gap)                  # front edge on upper and lower skin
    n = 10
    up = [(xu + (xb - xu) * i / n, G['zu'](xu + (xb - xu) * i / n)) for i in range(n + 1)]
    lo = [(xl + (xb - xl) * i / n, G['zl'](xl + (xb - xl) * i / n)) for i in range(n, -1, -1)]
    return up + lo


def band(G, x0, x1, upper, t):
    """Thin plate following the skin from x0 to x1 (outside the skin by t)."""
    n = 6
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    s = G['zu'] if upper else G['zl']
    sign = 1 if upper else -1
    return [(x, s(x)) for x in xs] + [(x, s(x) + sign * t) for x in reversed(xs)]


def build_horn(part, G, y, clevis, boss_dir):
    """Horn plate centred on y; boss on the side boss_dir (+1 outboard, -1 inboard)."""
    xh, zh, ht = G['xh'], G['zh'], G['ht']
    arm = [(xh + X, zh + Z) for X, Z in G['outline']]
    if not clevis:                                                   # link horn: cut the arm off below the boss
        arm = clip_above(arm, zh - G['rb'] - G['boss_r'] - 0.0015)  # true clip (the old z clamp left a spike)
    holes = [circle(G['B'][0], G['B'][1], G['bore_r'], 16)]
    if clevis:
        holes.append(circle(G['Q'][0], G['Q'][1], G['pin_r'], 12))
    part.prism('Y', y - ht / 2, [arm] + holes, ht, name='horn arm')
    part.prism('Y', y - ht / 2, [horn_blade_loop(G), circle(G['xt'], G['zt'], G['tube_r'] + 0.0001, 16)], ht,
               name='horn blade')
    fx0, fx1, fw, ft = G['flange']
    part.prism('Y', y - fw / 2, [band(G, xh + fx0, xh + fx1, False, ft)], fw, name='lower flange')
    bx0, bx1, bw, bt = G['backplate']
    part.prism('Y', y - bw / 2, [band(G, xh + bx0, xh + bx1, True, bt)], bw, name='upper backplate')
    y0 = y + boss_dir * ht / 2
    part.tube('Y', (G['B'][0], y0, G['B'][1]), boss_dir * G['boss_len'], G['boss_r'], G['bore_r'], name='rod boss')


def build_frame(part, G):
    fw = G['fw']
    x0, x1, y0, y1, z0, z1 = G['fx0'], G['fx1'], G['fy0'], G['fy1'], G['cz0'], G['fz1']
    rim = G['f_rim']
    part.prism('Z', z1 - fw, [rect(x0, y0, x1, y1), rect(x0 + rim, y0 + rim, x1 - rim, y1 - rim)], fw,
               name='top plate (rim, window over the case)')
    part.box((x0, y0, z0), (x1, y0 + fw, z1), name='inboard wall')
    part.box((x0, y0, z0), (x0 + fw, y1, z1), name='front end wall (ear slot)')
    part.box((x1 - fw, y0, z0), (x1, y1, z1), name='aft end wall (ear slot)')
    for xa, xb in ((x0, x0 + 0.004), (x1 - 0.004, x1)):                 # cover-screw bosses on the end walls
        part.box((xa, y0 + fw, z0), (xb, y0 + fw + 0.005, z0 + 0.006), name='M2 boss')


def build_cover(part, G):
    x0, x1 = G['fx0'] - G['lip'], G['fx1'] + G['lip']
    y0, y1 = G['fy0'] - G['lip'], G['fy1'] + 0.002
    z = G['zl'](G['xs'])
    slot = rect(G['slot_x'][0], G['ya'] - G['at'] / 2 - 0.0005, G['slot_x'][1], G['ya'] + G['at'] / 2 + 0.0005)
    part.prism('Z', z - G['ct'], [rect(x0, y0, x1, y1), slot], G['ct'], name='cover plate')


def build_tube(part, G, span):
    y0, y1 = span
    part.tube('Y', (G['xt'], y0, G['zt']), y1 - y0, G['tube_r'], G['tube_ri'], name='CF torque tube')


def build_tape(part, G):
    """Hinge tape on the upper skin: follows the S5010 upper surface over the tape skin (collision fix: the flat
    strip at the hinge z sat up to 1.7 mm inside the core ahead of the hinge, where the surface rises)."""
    xh, w = G['xh'], G['tape_w']
    off, t = k9.lval(k9.local('wing'), 'skin.model_t_m', 'm'), 0.0001
    n = 100                                       # 0.25 mm stations: chord sag << the skin's, no skin vertex pokes through
    xs = [xh - w / 2 + w * i / n for i in range(n + 1)]
    loop = [(x, G['zu'](x) + off) for x in xs] + [(x, G['zu'](x) + off + t) for x in reversed(xs)]
    for y0, y1 in (G['yin'], G['yout']):
        part.prism('Y', y0, [loop], y1 - y0, name='hinge tape strip')


# ----------------------------------------------------------------------------- module
PARTS_R = ['MEC-001-R', 'MEC-002-R', 'MEC-003-R', 'MEC-004-R', 'MEC-005-R', 'MEC-006-R', 'MEC-007-R', 'MEC-008-R',
           'MEC-009-RI', 'MEC-009-RO', 'MEC-010-R']


def mirror_id(pid):
    return pid.replace('-R', '-L', 1) if pid.endswith(('-R', '-RI', '-RO')) else pid


def build(ctx):
    P, LP = ctx.params, (ctx.local or load_local())
    coords, _ = k9.section(P)
    G = geometry(P, LP, coords)
    build_servo(ctx.part('MEC-001-R', rgb=RGB_SERVO), G)
    build_arm(ctx.part('MEC-002-R', rgb=RGB_PRINT), G)
    build_pushrod(ctx.part('MEC-003-R', rgb=RGB_STEEL), G)
    build_horn(ctx.part('MEC-004-R', rgb=RGB_PRINT), G, G['ya'], True, +1)
    ctx.part('MEC-005-R', rgb=RGB_STEEL).cylinder('Y', (G['B'][0], G['rod_y'][0], G['B'][1]),
                                                   G['rod_y'][1] - G['rod_y'][0], G['rod_r'], name='1/8 in CF rod')
    build_horn(ctx.part('MEC-006-R', rgb=RGB_PRINT), G, G['yo'], False, -1)
    build_cover(ctx.part('MEC-007-R', rgb=RGB_PRINT), G)
    build_frame(ctx.part('MEC-008-R', rgb=RGB_PRINT), G)
    build_tube(ctx.part('MEC-009-RI', rgb=RGB_CF), G, G['tube_in'])
    build_tube(ctx.part('MEC-009-RO', rgb=RGB_CF), G, G['tube_out'])
    build_tape(ctx.part('MEC-010-R', rgb=RGB_TAPE), G)
    for pid in PARTS_R:
        k9.pair(ctx, pid, mirror_id(pid))
    register(ctx, G)
    build_hardware(ctx, G)


def cover_screw_points(G):
    """(x, y) of the two M2 x 6 cover screws (right side): centre of the frame's M2 bosses on the end walls."""
    y = G['fy0'] + G['fw'] + 0.0025
    return [(G['fx0'] + 0.002, y), (G['fx1'] - 0.002, y)]


def build_hardware(ctx, G):
    """Fasteners as components (only when declared, k09kit.hw_part; C6 FASTENERS-CAD), right side then mirrored:
    MEC-011 cover screw pair (E-MEC-35/36 and the retention of E-MEC-03/04): M2 x 6 self-tapping pan heads from below
    (-z) through the cover into the frame bosses; MEC-012 supplied M2 x 4 arm screw into the output shaft (E-MEC-05/06)."""
    cs = k9.hw_part(ctx, 'MEC-011-R')
    if cs is None:
        return
    zc = G['zl'](G['xs']) - G['ct']                                   # cover lower face
    for x, y in cover_screw_points(G):
        k9.hw_screw(cs, 'Z', (x, y, zc), 1, 'M2', 0.006, 'pan', name='M2 x 6 self-tapping pan head')
    arm = k9.hw_part(ctx, 'MEC-012-R')
    ya = G['ya'] + G['at'] / 2
    k9.hw_screw(arm, 'Y', (G['xs'], ya, G['zs']), -1, 'M2', 0.004, 'pan', name='M2 x 4 arm screw (supplied)')
    k9.pair(ctx, 'MEC-011-R', 'MEC-011-L')
    k9.pair(ctx, 'MEC-012-R', 'MEC-012-L')
    x, y = cover_screw_points(G)[0]
    for sd, s in (('R', 1), ('L', -1)):
        k9.hw_join(ctx, 'MEC-011-' + sd, 'MEC-007-' + sd, (x, s * y, zc + G['ct'] / 2))
        k9.hw_join(ctx, 'MEC-011-' + sd, 'MEC-008-' + sd, (x, s * y, G['cz0'] + 0.003))
        k9.hw_join(ctx, 'MEC-012-' + sd, 'MEC-002-' + sd, (G['xs'], s * G['ya'], G['zs']))
        k9.hw_join(ctx, 'MEC-012-' + sd, 'MEC-001-' + sd, (G['xs'], s * (G['cy1'] + G['boss'] / 2), G['zs']))


def edge_specs(G=None):
    """(id, part_a, part_b, via, kind of registration, notes, needs) for the RIGHT and LEFT sides.
    kind: 'contact' | ('rigid', point) | ('revolute', point, axis); points are right-side and mirrored for L."""
    out = []

    def add(n_r, n_l, a, b, via, reg, notes):
        for n, s in ((n_r, 'R'), (n_l, 'L')):
            fa = a if s == 'R' else mirror_id(a)
            fb = b if s == 'R' else mirror_id(b)
            out.append({'id': 'E-MEC-%02d' % n, 'part_a': fa, 'part_b': fb, 'via': via, 'reg': reg, 'side': s,
                        'notes': notes})
    add(2, 1, 'MEC-008-R', WING['core'] + '!', 'CT-EPOXY', 'contact',
        'servo frame bonded in the lower-skin pocket (top plate + walls, epoxy + microballoons), tape cut back 3 mm')
    add(4, 3, 'MEC-001-R', 'MEC-008-R', 'CT-SERVO-EAR-SLOT', 'contact',
        'servo ears captured in the frame end-wall slots; the cover holds the servo up into the frame')
    add(6, 5, 'MEC-002-R', 'MEC-001-R', 'CT-SERVO-SPLINE', ('rigid', 'spline'), 'arm on the spline at servo neutral, '
        'supplied M2 screw + Loctite 222')
    add(8, 7, 'MEC-003-R', 'MEC-002-R', 'CT-CLEVIS', ('revolute', 'P'), 'Z-bend in the arm hole drilled 1.6 mm')
    add(10, 9, 'MEC-003-R', 'MEC-004-R', 'CT-CLEVIS', ('revolute', 'Q'), 'steel 2-56 clevis on the horn pin hole, '
        'silicone keeper')
    add(12, 11, 'MEC-004-R', WING['in'] + '!', 'CT-EPOXY', 'contact',
        'through-panel horn: blade in a 2.5 mm slot, lower flange and upper backplate on bare foam, bore on the tube')
    add(18, 17, 'MEC-007-R', WING['skin'] + '!', 'CT-TAPE-SKIN', 'contact', 'cover edges taped to the skin (service: '
        'peel, remove 2 screws)')
    add(20, 19, 'MEC-005-R', 'MEC-004-R', 'CT-EPOXY', 'contact', 'rod bonded over 10 mm in the inboard horn boss')
    add(22, 21, 'MEC-005-R', 'MEC-006-R', 'CT-EPOXY', 'contact', 'rod bonded over 10 mm in the link horn boss')
    add(24, 23, 'MEC-006-R', WING['out'] + '!', 'CT-EPOXY', 'contact', 'through-panel link horn in the outboard panel')
    add(26, 25, 'MEC-009-RI', WING['in'] + '!', 'CT-EPOXY', 'contact', 'torque tube in a routed groove, epoxy + '
        'microballoon fill, taped over')
    add(28, 27, 'MEC-009-RO', WING['out'] + '!', 'CT-EPOXY', 'contact', 'torque tube in a routed groove, epoxy + '
        'microballoon fill, taped over')
    add(30, 29, 'MEC-004-R', 'MEC-009-RI', 'CT-EPOXY', 'contact', 'horn blade bore bonded on the torque tube')
    add(32, 31, 'MEC-006-R', 'MEC-009-RO', 'CT-EPOXY', 'contact', 'link horn blade bore bonded on the torque tube')
    add(34, 33, 'MEC-010-R', WING['core'] + '!', 'CT-TAPE-SKIN', 'contact', 'hinge tape on the core side of the hinge '
        '(the panel side is the wing hinge edge E-WNG-04..07)')
    add(36, 35, 'MEC-007-R', 'MEC-008-R', 'CT-M2-SCREW-PLASTIC', ('rigid', 'cover'), 'cover screwed to the frame '
        'bosses, 2 x M2 x 6')
    for e in out:                                                    # '!' marks a wing part: same id both sides
        for k in ('part_a', 'part_b'):
            p = e[k]
            if p.endswith('!'):
                base = p[:-1]
                e[k] = base if base in (WING['core'], WING['skin']) else base + '-' + e['side']
        e['needs'] = [p for p in (e['part_a'], e['part_b']) if p.startswith('WNG')]
    return sorted(out, key=lambda e: e['id'])


def reg_point(G, which):
    if which == 'spline':
        return (G['xs'], G['ya'] - G['at'] / 2, G['zs'])
    if which == 'P':
        return (G['P'][0], G['ya'], G['P'][1])
    if which == 'Q':
        return (G['Q'][0], G['ya'], G['Q'][1])
    if which == 'cover':
        return ((G['fx0'] + G['fx1']) / 2, (G['fy0'] + G['fy1']) / 2, G['cz0'])
    raise KeyError(which)


def register(ctx, G):
    known = ctx.parts_info
    for e in edge_specs(G):
        if e['part_a'] not in known or e['part_b'] not in known:
            continue                                                 # edge waits in edges_pending (wing not declared)
        reg = e['reg']
        if reg == 'contact':
            ctx.contact(e['id'], e['notes'])
            continue
        p = reg_point(G, reg[1])
        if e['side'] == 'L':
            p = (p[0], -p[1], p[2])
        if reg[0] == 'rigid':
            ctx.rigid(e['id'], e['part_a'], e['part_b'], at=p)
        else:
            ctx.revolute(e['id'], e['part_a'], e['part_b'], at=p, axis='Y')
