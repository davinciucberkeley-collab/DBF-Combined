"""K09-L wing (D1, revision D1-R1 on params A1-R3): one-piece hot-wired XPS core with every cut the build needs, CF spar
in a bonded bore, four PETG spar plugs, four elevon panels on upper-surface tape hinges, the packing-tape skin with its
doublers and tip edge layer, and the FAA label.

Frame and datums: redesign/fusion/DATUMS.md (x aft from the LE, y right, z up, cruise attitude, metres). Section:
subsystems/wing/s5010.dat through k09kit.section(). Every number comes from params/params.json (ctx.value / ctx.D),
this folder's params.json (ctx.local) or the mating subsystem's params.json (fins: block, anchor, bond gap; pod: saddle
feet, tie, cheek; harness: grooves; mechanisms: torque-tube groove and horn slots in the panels) so a change on either
side moves the cut. The servo pocket is sized to D6's MEC-008 frame (team/D1/wing_selfcheck.py compares the two).

How the core is modelled: the section is constant (no taper, twist or sweep), so the core is a row of Y-normal prisms,
one per span segment between feature boundaries. Each segment's loop is the S5010 section with that segment's cuts
(pod recess, saddle windows and tie channels, brace-anchor pockets, through-core block pockets, ESC and servo lead
grooves, lead hole, servo pocket open below, elevon cut-out) and the spar bore as a hole. A full-depth cut splits the loop into a front and an
aft piece. The finished core is what the shop has after the slot cap is re-bonded: foam everywhere except the 22.4 mm
bore round the spar (C2: the slot is cut from the lower surface and the strip re-bonded as the cap).

Not modelled as geometry (build data in BUILD.md): the 45 deg P1 lead hole (F2, drilled with a guide block), the
lower-surface slot cut line (closed by the cap), fillets at the half-fin roots (fins), hinge tape (mechanisms).
The servo lead hole is modelled as a 4 mm square pass (drilled 5 mm round).

Elevon panels: Y-normal prisms of the bevelled section with D6's torque-tube groove; at each horn the panel is split
round the 2.5 mm blade slot.

UNVERIFIED-IN-FUSION: about 70 Y-normal prisms with spline-free polyline loops (many points), thin (0.1 mm) tape bodies
that follow the skin by a z offset, and touching (not combined) core bodies. If Fusion is slow, combine the core
bodies after BuildAll (Modify > Combine, Join); masses are declared, not taken from Fusion.
"""
import math

import k09kit as k9

N_SURF = 48          # surface samples per full chord (cosine spaced); cut edges are added exactly
N_ARC = 28           # points on a full circle


# ----------------------------------------------------------------------------- numbers
def layout(ctx):
    """Every derived number the module, wing_data.py and wing_claims.py use (one place)."""
    v, L, P = ctx.value, ctx.local, ctx.params
    lv = lambda k, u=None, d=None: k9.lval(L, k, u, d)
    F, PD, H = k9.local('fins'), k9.local('pod'), k9.local('harness')
    coords, src = k9.section(ctx)
    c = v('wing.chord_m', 'm')
    g = {'coords': coords, 'src': src, 'c': c, 'half': v('wing.span_m', 'm') / 2}
    g['xh'] = ctx.D('DP-HINGE')
    g['xs'], g['zs'] = ctx.D('DP-SPAR'), v('wing.spar.z_m', 'm')
    g['rs'] = v('wing.spar.od_m', 'm') / 2
    g['ri'] = v('wing.spar.id_m', 'm') / 2
    g['rb'] = g['rs'] + lv('slot.bond_gap_m', 'm')                      # bore = slot width / 2
    g['spar_half'] = v('wing.spar.length_m', 'm') / 2
    g['x_slot'] = (g['xs'] - g['rb'], g['xs'] + g['rb'])
    # pod recess (CR-D2-04): floor at the pod base, ends slot_wall ahead of the spar, full pod width
    zb = v('pod.z_base_m', 'm')
    g['z_rec'] = zb
    g['y_pod'] = v('pod.size_m', 'm')[1] / 2
    g['x_rec1'] = g['xs'] - g['rs'] - lv('recess.slot_wall_m', 'm')
    lo, hi = 0.0, g['xs']
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if surf(g, mid, 'upper') < zb else (lo, mid)
    g['x_rec0'] = (lo + hi) / 2
    # pod handle saddle windows and ties (pod params, D2)
    g['win_y'] = tuple(k9.lval(PD, 'foot_y_m', 'm', [0.029, 0.053]))
    g['z_cheek'] = g['zs'] + k9.lval(PD, 'tongue_cheek_frac', '-', 0.8) * g['rs']
    g['tie_y'] = k9.lval(PD, 'tie_y_m', 'm', 0.036)
    g['tie_w'], g['tie_d'] = lv('saddle_window.tie_channel_m', 'm')
    # through-core block pocket (fins: tube bore and spar bore + wall, bond gap)
    gap_f = k9.lval(F, 'fin_detail.bond_gap_m', 'm', 0.00015)
    wall = k9.lval(F, 'fin_detail.block.wall_m', 'm', 0.006)
    bw = k9.lval(F, 'fin_detail.block.width_m', 'm', 0.036)
    g['y_fin'] = v('fins.y_m', 'm')
    xt, rt = v('fins.tube.x_m', 'm'), v('fins.tube.od_m', 'm') / 2
    g['blk_x'] = (xt - rt - wall - gap_f, g['xs'] + g['rs'] + wall + gap_f)
    g['blk_y'] = (g['y_fin'] - bw / 2 - gap_f, g['y_fin'] + bw / 2 + gap_f)
    # brace-anchor pockets (fins anchor), upper and lower, slot width along x
    ya = k9.lval(F, 'fin_detail.brace.anchor_y_m', 'm', 0.242)
    aw = k9.lval(F, 'fin_detail.anchor.len_y_m', 'm', 0.016) / 2 + lv('anchor_pocket.gap_m', 'm')
    g['anc_y'] = (ya - aw, ya + aw)
    g['y_anchor'] = ya
    # grooves (harness params, F2 CR-F2-04)
    gs = k9.lval(H, 'harness.groove_size_mm', 'mm', {'power': [3.0, 3.1], 'signal': [2.5, 2.4], 'servo': [4.0, 1.6]})
    mm = lambda wd: (wd[0] / 1000.0, wd[1] / 1000.0)
    g['grooves'] = [(k9.lval(H, 'harness.groove.x_sig_m', 'm', 0.0543),) + mm(gs['signal']),
                    (k9.lval(H, 'harness.groove.x_pos_m', 'm', 0.0593),) + mm(gs['power']),
                    (k9.lval(H, 'harness.groove.x_neg_m', 'm', 0.0643),) + mm(gs['power'])]
    g['groove_y'] = tuple(lv('grooves.y_m', 'm'))
    g['sgroove'] = (k9.lval(H, 'harness.groove.x_servo_m', 'm', 0.1082),) + mm(gs['servo'])
    g['sgroove_y'] = tuple(lv('grooves.servo_y_m', 'm'))
    # servo pocket
    g['sp_x'], g['sp_y'] = tuple(lv('servo_pocket.x_m', 'm')), tuple(lv('servo_pocket.y_m', 'm'))
    g['sp_zc'] = lv('servo_pocket.ceiling_z_m', 'm')
    g['lead_x'] = tuple(lv('servo_pocket.lead_hole_x_m', 'm'))
    g['sp_dbl'] = lv('servo_pocket.doubler_w_m', 'm')
    # elevons
    g['spans'] = [s for s in k9.elevon_spans(P) if s[0] > 0]                # right: inboard, outboard
    g['e_gap'] = lv('elevon.end_gap_m', 'm')
    th = surf(g, g['xh'], 'upper') - surf(g, g['xh'], 'lower')
    g['t_hinge'] = th
    g['bevel'] = th * math.tan(math.radians(lv('elevon.bevel_deg', 'deg')))
    g['defl'] = tuple(v('wing.elevon.deflection_deg', 'deg'))
    # mechanisms features in the panels (D6 params): torque-tube groove, horn-blade slots
    M = k9.local('mechanisms')
    od = k9.lval(M, 'mec.tube.od_id_m', 'm', [0.005, 0.004])[0]
    xt = g['xh'] + k9.lval(M, 'mec.tube.x_aft_of_hinge_m', 'm', 0.0075)
    zt = (surf(g, xt, 'upper') + surf(g, xt, 'lower')) / 2
    gt = lv('elevon.tube_groove_gap_m', 'm')
    g['tube_groove'] = (xt - od / 2 - gt, xt + od / 2 + gt, zt + od / 2 + gt)      # x0, x1, ceiling (open below)
    g['tube_xz'] = (xt, zt, od / 2)
    bx = k9.lval(M, 'mec.horn.blade_x_mm', 'mm', [6.0, 40.0])
    hs = lv('elevon.horn_slot_m', 'm')
    g['horn_x'] = (min(g['xh'] + bx[0] / 1000.0, g['tube_groove'][0]), g['xh'] + bx[1] / 1000.0)
    g['horn_y'] = [(y - hs / 2, y + hs / 2) for y in (k9.lval(M, 'mec.station.arm_plane_y_m', 'm', 0.285),
                                                       k9.lval(M, 'mec.station.outboard_horn_y_m', 'm', 0.355))]
    # skin, label, plugs
    g['t_skin'] = lv('skin.model_t_m', 'm')
    g['untaped_x'] = tuple(lv('skin.untaped_upper_x_m', 'm'))
    g['dbl_x'] = lv('skin.block_doubler_x_m', 'm')
    g['lab_x'], g['lab_y'], g['lab_t'] = tuple(lv('label.x_m', 'm')), tuple(lv('label.y_m', 'm')), lv('label.t_m', 'm')
    g['plug_r'] = lv('plugs.od_m', 'm') / 2
    g['plug_blk'], g['plug_anc'] = lv('plugs.block_len_m', 'm'), lv('plugs.anchor_len_m', 'm')
    return g


def surf(g, x, side):
    """Skin height (m) at station x on the S5010 section (TE opened to k9.TE_MIN_M)."""
    return k9.surface_z(g['coords'], g['c'], min(max(x / g['c'], 0.0), 1.0), side)


# ----------------------------------------------------------------------------- loops
def _xs(x0, x1, extra=()):
    n = max(4, int(N_SURF * (x1 - x0) / 0.32 + 0.5))
    pts = {round(x0 + (x1 - x0) * (1 - math.cos(math.pi * i / n)) / 2, 7) for i in range(n + 1)}
    pts.update(round(e, 7) for e in extra if x0 <= e <= x1)
    return sorted(pts)


def _dedupe(loop):
    out = []
    for p in loop:
        if not out or abs(p[0] - out[-1][0]) > 1e-7 or abs(p[1] - out[-1][1]) > 1e-7:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-7 and abs(out[0][1] - out[-1][1]) < 1e-7:
        out.pop()
    return out


def _arc(xc, zc, r, a0, a1, n=None):
    n = n or max(3, int(N_ARC * abs(a1 - a0) / (2 * math.pi) + 0.5))
    return [(xc + r * math.cos(a0 + (a1 - a0) * i / n), zc + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def bore_floor(g, xa, xb, zf, r):
    """Upper cut whose floor zf lies inside the bore: floor from xb to the bore, round the bore BELOW the spar
    (foam boundary), on to xa. Returns the polyline from xb to xa."""
    t = math.asin(max(-1.0, min(1.0, (zf - g['zs']) / r)))
    return [(xb, zf)] + _arc(g['xs'], g['zs'], r, t, -math.pi - t) + [(xa, zf)]


def outline(g, x0, x1, ucuts=(), lcuts=()):
    """Closed (x, z) loop of the section between x0 and x1 with notches. ucuts / lcuts: (xa, xb, floor) where floor
    is a number (flat), a function of x, or a polyline list (upper: from xb to xa; lower: from xa to xb)."""
    def side_pts(cuts, side, descending):
        edges = [e for a, b, _f in cuts for e in (a, b)]
        xs = _xs(x0, x1, edges)
        if descending:
            xs = xs[::-1]
        out, skip = [], None
        for x in xs:
            cut = next((cu for cu in cuts if cu[0] - 1e-9 <= x <= cu[1] + 1e-9), None)
            if cut is None:
                out.append((x, surf(g, x, side)))
                continue
            a, b, f = cut
            interior = x0 + 1e-9 < x < x1 - 1e-9          # at a piece edge the loop starts / ends on the floor
            enter = interior and abs(x - (b if descending else a)) < 1e-9
            leave = interior and abs(x - (a if descending else b)) < 1e-9
            if isinstance(f, list):
                if enter:
                    out.append((x, surf(g, x, side)))
                    out.extend(f)
                elif leave:
                    out.append((x, surf(g, x, side)))
                continue
            z = f(x) if callable(f) else f
            if enter:
                out += [(x, surf(g, x, side)), (x, z)]
            elif leave:
                out += [(x, z), (x, surf(g, x, side))]
            else:
                out.append((x, z))
        return out
    key = lambda cu: (cu[0], cu[1])
    up = side_pts(sorted(ucuts, key=key), 'upper', True)
    lo = side_pts(sorted(lcuts, key=key), 'lower', False)
    if x0 <= 1e-9:
        lo = lo[1:]                                                        # LE point shared
    return _dedupe(up + lo)


def circle(xc, zc, r, n=N_ARC):
    return [(xc + r * math.cos(2 * math.pi * i / n), zc + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def skin_strip(g, x0, x1, side, z_off, t):
    """Thin body following the upper or lower skin from x0 to x1, z_off outside the foam, thickness t."""
    s = 1.0 if side == 'upper' else -1.0
    xs = _xs(x0, x1)
    inner = [(x, surf(g, x, side) + s * z_off) for x in xs]
    outer = [(x, surf(g, x, side) + s * (z_off + t)) for x in reversed(xs)]
    return _dedupe(inner + outer)


# ----------------------------------------------------------------------------- span plan of the core
def features(g):
    """Right-hand features: (kind, y0, y1). The left hand is the exact mirror."""
    f = [('recess', 0.0, g['y_pod']), ('window', g['win_y'][0], g['win_y'][1]),
         ('tie', g['tie_y'] - g['tie_w'] / 2, g['tie_y'] + g['tie_w'] / 2),
         ('anchor', g['anc_y'][0], g['anc_y'][1]), ('block', g['blk_y'][0], g['blk_y'][1]),
         ('groove', g['groove_y'][0], g['groove_y'][1]), ('sgroove', g['sgroove_y'][0], g['sgroove_y'][1]),
         ('sbranch', g['sgroove_y'][1] - g['sgroove'][1] / 2, g['sgroove_y'][1] + g['sgroove'][1] / 2),
         ('pocket', g['sp_y'][0], g['sp_y'][1]), ('spar', 0.0, g['spar_half'])]
    f += [('elevon', a, b) for a, b in g['spans']]
    return f


def segments(g):
    """[(y0, y1, set of active feature kinds)] from y = 0 to the tip."""
    f = features(g)
    ys = sorted({0.0, g['half']} | {round(y, 7) for _k, a, b in f for y in (a, b) if 0.0 <= y <= g['half']})
    out = []
    for y0, y1 in zip(ys, ys[1:]):
        if y1 - y0 < 1e-6:
            continue
        ym = (y0 + y1) / 2
        out.append((y0, y1, {k for k, a, b in f if a < ym < b}))
    return out


def segment_loops(g, act):
    """Loops for one segment: [(outer, [holes])...] (two entries when a full-depth cut splits the section)."""
    xf, xa = g['x_slot']
    x_end = g['xh'] if 'elevon' in act else g['c']
    up, lo, holes_at = [], [], []
    if 'recess' in act:
        up.append((g['x_rec0'], g['x_rec1'], g['z_rec']))
    if 'groove' in act:
        for xc, w, d in g['grooves']:
            up.append((xc - w / 2, xc + w / 2, surf(g, xc, 'upper') - d))
            lo.append((xc - w / 2, xc + w / 2, surf(g, xc, 'lower') + d))
    if 'sgroove' in act:
        xc, w, d = g['sgroove']
        up.append((xc - w / 2, xc + w / 2, surf(g, xc, 'upper') - d))
    split = []
    if 'sbranch' in act:
        xc, w, d = g['sgroove']
        up = [u for u in up if abs(u[0] - (xc - w / 2)) > 1e-9]                # the branch replaces the groove here
        up.append((xc - w / 2, g['lead_x'][0], lambda x, d=d: surf(g, x, 'upper') - d))
        split.append(g['lead_x'])                                              # lead hole down into the pocket
    if 'pocket' in act:
        lo.append((g['sp_x'][0], g['sp_x'][1], g['sp_zc']))
    spar = 'spar' in act
    if 'block' in act:
        split.append(g['blk_x'])
    elif 'anchor' in act and spar:
        split.append((xf, xa))
    elif 'window' in act and spar:
        r = g['rb'] + (g['tie_d'] if 'tie' in act else 0.0)
        up.append((xf, xa, bore_floor(g, xf, xa, g['z_cheek'], r)))
    elif spar:
        holes_at.append(circle(g['xs'], g['zs'], g['rb']))
    # pieces between the full-depth cuts
    pieces, x = [], 0.0
    for a, b in sorted(split):
        pieces.append((x, a))
        x = b
    pieces.append((x, x_end))
    out = []
    for p0, p1 in pieces:
        inside = lambda cu: cu[0] < p1 - 1e-9 and cu[1] > p0 + 1e-9               # a cut may run past a piece edge
        loop = outline(g, p0, p1, [u for u in up if inside(u)], [l for l in lo if inside(l)])
        holes = [h for h in holes_at if p0 < g['xs'] - g['rb'] and g['xs'] + g['rb'] < p1]
        out.append((loop, holes))
    return out


def skin_plan(g):
    """Right-hand (and centre) tape pieces: (name, side, x0, x1, y0, y1, layers). Used for the bodies and the mass."""
    xh, c, yp = g['xh'], g['c'], g['y_pod']
    ux0, ux1 = g['untaped_x']
    plan = []
    # centre strip |y| <= pod half width (built once, spans both sides)
    plan += [('skin centre upper', 'upper', ux1, xh, -yp, yp, 1), ('skin centre lower', 'lower', 0.0, xh, -yp, yp, 1),
             ('skin centre aft upper', 'upper', xh, c, -yp, yp, 1), ('skin centre aft lower', 'lower', xh, c, -yp, yp, 1)]
    # outer panels (right; mirrored)
    plan += [('skin upper', 'upper', 0.0, xh, yp, g['half'], 1), ('skin lower', 'lower', 0.0, xh, yp, g['half'], 1)]
    (i0, i1), (o0, o1) = g['spans']
    gaps = [(a, b) for a, b in ((yp, i0), (i1, o0), (o1, g['half'])) if b - a > 1e-9]
    for a, b in gaps:
        plan += [('skin aft upper', 'upper', xh, c, a, b, 1), ('skin aft lower', 'lower', xh, c, a, b, 1)]
    # doublers (C2): over each block pocket (wrapped round the LE) and over the servo pocket edges (upper)
    w = g['sp_dbl']
    plan += [('doubler block upper', 'upper', 0.0, g['dbl_x'], g['y_fin'] - w / 2, g['y_fin'] + w / 2, 1),
             ('doubler block lower', 'lower', 0.0, g['dbl_x'], g['y_fin'] - w / 2, g['y_fin'] + w / 2, 1)]
    ys = (g['sp_y'][0] + g['sp_y'][1]) / 2
    plan += [('doubler servo lower', 'lower', g['dbl_x'], xh, ys - w / 2, ys + w / 2, 1)]
    return plan


def elevon_section(g):
    """Panel section: upper skin TE -> hinge, 30 deg lower bevel, D6's torque-tube groove open below, lower skin -> TE."""
    xh, c, b = g['xh'], g['c'], g['bevel']
    gx0, gx1, gzc = g['tube_groove']
    zu0, zl1 = surf(g, xh, 'upper'), surf(g, xh + b, 'lower')
    zbev = lambda x: zu0 + (x - xh) / b * (zl1 - zu0)
    up = [(x, surf(g, x, 'upper')) for x in reversed(_xs(xh, c))]
    if gx0 < xh + b:
        mid = [(gx0, zbev(gx0)), (gx0, gzc), (gx1, gzc), (gx1, surf(g, gx1, 'lower'))]
        lo = [(x, surf(g, x, 'lower')) for x in _xs(gx1, c)][1:]
    else:
        mid = [(xh + b, zl1)] + [(x, surf(g, x, 'lower')) for x in _xs(xh + b, gx0)][1:] + [(gx0, gzc), (gx1, gzc)]
        lo = [(x, surf(g, x, 'lower')) for x in _xs(gx1, c)]
    return _dedupe(up + mid + lo)


def clip_x(loop, lo, hi):
    """Sutherland-Hodgman clip of a closed loop to lo <= x <= hi (each piece here is one connected region)."""
    def clip(pts, keep, xc):
        out = []
        for i, p in enumerate(pts):
            q = pts[i - 1]
            if keep(p):
                if not keep(q):
                    out.append((xc, q[1] + (p[1] - q[1]) * (xc - q[0]) / (p[0] - q[0])))
                out.append(p)
            elif keep(q):
                out.append((xc, q[1] + (p[1] - q[1]) * (xc - q[0]) / (p[0] - q[0])))
        return out
    pts = clip(loop, lambda p: p[0] >= lo - 1e-12, lo)
    return _dedupe(clip(pts, lambda p: p[0] <= hi + 1e-12, hi))


def elevon_pieces(g, y0, y1):
    """[(y_from, y_to, loop)] for one right-hand panel between y0 and y1 (gaps applied by the caller): full sections,
    and at a horn-blade slot the section minus the blade x range."""
    sec = elevon_section(g)
    slots = [(a, b) for a, b in g['horn_y'] if y0 < a and b < y1]
    out, y = [], y0
    for a, b in slots:
        out.append((y, a, sec))
        out.append((a, b, clip_x(sec, g['xh'], g['horn_x'][0])))
        out.append((a, b, clip_x(sec, g['horn_x'][1], g['c'])))
        y = b
    out.append((y, y1, sec))
    return out


# ----------------------------------------------------------------------------- build
def build(ctx):
    g = layout(ctx)
    v = ctx.value

    # WNG-001 core: right-hand segments, then the exact mirror into the same component
    core = ctx.part('WNG-001')
    right = []
    for y0, y1, act in segments(g):
        for i, (loop, holes) in enumerate(segment_loops(g, act)):
            nm = 'xps core y%.3f-%.3f%s' % (y0, y1, '' if i == 0 else ' aft')
            if y0 == 0.0:                                     # centre segment spans y -y1 .. +y1 as one body
                right.append(core.prism('Y', -y1, [loop] + holes, 2 * y1, name=nm))
            else:
                right.append(core.prism('Y', y0, [loop] + holes, y1 - y0, name=nm))
    for s in [s for s in right if s.offset >= 0.0]:
        core._add(s.mirrored(1))

    # WNG-002 spar and the four plugs inside it (C2)
    k9.spar_y(ctx.part('WNG-002'), g['xs'], g['zs'], g['spar_half'], 2 * g['rs'], 2 * g['ri'])
    ctx.contact('E-WNG-01', 'spar bonded in the 22.4 mm bore: slot cut from below, epoxy + microballoons, cap re-bonded')
    ctx.part('WNG-004-R').cylinder('Y', (g['xs'], g['y_fin'] - g['plug_blk'] / 2, g['zs']), g['plug_blk'], g['plug_r'], name='petg plug')
    k9.pair(ctx, 'WNG-004-R', 'WNG-004-L')
    ctx.part('WNG-005-R').cylinder('Y', (g['xs'], g['y_anchor'] - g['plug_anc'] / 2, g['zs']), g['plug_anc'], g['plug_r'], name='petg plug')
    k9.pair(ctx, 'WNG-005-R', 'WNG-005-L')
    for e in ('E-WNG-08', 'E-WNG-09', 'E-WNG-10', 'E-WNG-11'):
        ctx.contact(e, 'PETG plug bonded inside the spar (thickened epoxy), pushed in from the spar end before the spar bond')

    # WNG-003 tape skin (thin bodies; mass from arc length in wing_data.py)
    skin = ctx.part('WNG-003')
    t = g['t_skin']
    for name, side, x0, x1, y0, y1, _n in skin_plan(g):
        off = t if name.startswith('doubler') else 0.0
        s = skin.prism('Y', y0, [skin_strip(g, x0, x1, side, off, t)], y1 - y0, name='tape ' + name)
        if y0 > 0:
            skin._add(s.mirrored(1))
    tip = skin.prism('Y', g['half'], [outline(g, 0.0, g['c'])], 2 * t, name='tape tip edge')
    skin._add(tip.mirrored(1))
    ctx.contact('E-WNG-02', 'tape skin on the core (spanwise strips, 10 % overlap, 15 mm round the LE)')

    # WNG-020 FAA label on the upper skin, right wing
    lab = ctx.part('WNG-020')
    (lx0, lx1), (ly0, ly1) = g['lab_x'], g['lab_y']
    lab.prism('Y', ly0, [skin_strip(g, lx0, lx1, 'upper', 2 * t, g['lab_t'])], ly1 - ly0, name='label')
    ctx.contact('E-WNG-03', 'adhesive label on the upper skin')

    # elevon panels: right inboard / outboard, mirrored left; tape hinge on the upper skin at DP-HINGE
    lim = g['defl']
    edges = {('WNG-011', 'R'): 'E-WNG-06', ('WNG-012', 'R'): 'E-WNG-07',
             ('WNG-011', 'L'): 'E-WNG-04', ('WNG-012', 'L'): 'E-WNG-05'}
    for (y0, y1), pid in zip(g['spans'], ('WNG-011', 'WNG-012')):
        e = ctx.part(pid + '-R')
        for ya, yb, loop in elevon_pieces(g, y0 + g['e_gap'], y1 - g['e_gap']):
            e.prism('Y', ya, [loop], yb - ya, name='xps elevon')
        k9.pair(ctx, pid + '-R', pid + '-L')
        ym = (y0 + y1) / 2
        hp = k9.hinge_point(g['coords'], g['c'], g['xh'] / g['c'], ym)
        ctx.revolute(edges[(pid, 'R')], pid + '-R', 'WNG-001', at=hp, axis='Y', limits=lim)
        ctx.revolute(edges[(pid, 'L')], pid + '-L', 'WNG-001', at=(hp[0], -hp[1], hp[2]), axis='Y', limits=lim)
    return g
