"""K09-L wing (D1, revision D1-R2 on params A1-R5): one-piece hot-wired XPS core with every cut the build needs, CF spar
in a bonded bore, four PETG spar plugs, four elevon panels on upper-surface tape hinges, the packing-tape skin with its
seam-free LE strip, doublers, tab-edge and tip layers, the block-pocket lip beads, the pod recess-step fillet and the
FAA label.

R2 (D-68, D-69): block-pocket corners R 3.15 mm round D3's R 3 mm block; 3 x 3 mm microballoon lip beads along the
inboard and outboard pocket edges, both surfaces (WNG-006); elevon cut-out corners R 3 mm at the fin-root tabs with
the panel corners relieved and the tab tape folded round; one 100 mm LE strip with both edges aft of x/c 0.10; F2's
18 x 10 x 5 mm JR recess on the servo branch; D6-R2 torque-tube groove lengths; no recess-step fillet (D-103 deleted WNG-007).
Plan-form radii and the 45 deg bead chamfer are drawn as n spanwise steps (block_pocket.corner_steps) of Y-normal
prisms, always on the safe side (pocket contains the block, bead circumscribes the triangle, panel clear of the fill);
the shop cuts the true radius from the template.

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

Not modelled as geometry (build data in BUILD.md): the lower-surface slot cut line (closed by the cap), fillets at the half-fin roots (fins), hinge tape (mechanisms).
The servo lead hole is modelled as a 4 mm square pass (drilled 5 mm round). The 45 deg P1 lead hole (F2, drilled 8 mm
with a guide block) is a cut through the core and the tape (p1_holes).

Elevon panels: Y-normal prisms of the bevelled section with D6's torque-tube groove; at each horn the panel is split
round the 2.5 mm blade slot.

UNVERIFIED-IN-FUSION: about 70 Y-normal prisms with spline-free polyline loops (many points), thin (0.1 mm) tape bodies
that follow the skin by a z offset, and touching (not combined) core bodies. If Fusion is slow, combine the core
bodies after BuildAll (Modify > Combine, Join); masses are declared, not taken from Fusion.
"""
import math

import fusionkit as fk
import k09kit as k9

N_SURF = 96          # surface samples per full chord (cosine spaced); cut edges are added exactly. 96 (was 48): mid-
#                      chord stations ~5 mm apart, chord sag ~0.025 mm, so the skin and core tessellations never cross
#                      by more than the collision tolerance (collision/collide.py, 0.05 mm)
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
    # D-68 (CR-C2-11): pocket corners follow D3's R 3 mm block edges (pocket radius = block radius + bond gap, same
    # centre); microballoon fillet beads along the inboard and outboard pocket lips, both surfaces
    g['blk_rp'] = k9.lval(F, 'fin_detail.block.edge_r_m', 'm', 0.003) + gap_f
    g['bead_leg'] = lv('block_pocket.bead_leg_m', 'm')
    g['n_step'] = int(lv('block_pocket.corner_steps', '-'))
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
    # F2's JR in-line recess on the servo branch (CR-F2-14): x from harness params, width along y and depth local
    g['jr_x'] = tuple(k9.lval(H, 'harness.groove.jr_recess_x_m', 'm', [0.150, 0.168]))
    jw = lv('jr_recess.width_y_m', 'm')
    g['jr_y'] = (g['sgroove_y'][1] - jw / 2, g['sgroove_y'][1] + jw / 2)
    g['jr_d'] = lv('jr_recess.depth_m', 'm')
    # servo pocket
    g['sp_x'], g['sp_y'] = tuple(lv('servo_pocket.x_m', 'm')), tuple(lv('servo_pocket.y_m', 'm'))
    g['sp_zc'] = lv('servo_pocket.ceiling_z_m', 'm')
    g['lead_x'] = tuple(lv('servo_pocket.lead_hole_x_m', 'm'))
    g['sp_dbl'] = lv('servo_pocket.doubler_w_m', 'm')
    # elevons
    g['spans'] = [s for s in k9.elevon_spans(P) if s[0] > 0]                # right: inboard, outboard
    g['e_gap'] = lv('elevon.end_gap_m', 'm')
    g['tab_y'] = (g['spans'][0][1], g['spans'][1][0])                      # fin-root tab faces (CR-C2-13)
    g['ecr'] = lv('elevon.cutout_corner_r_m', 'm')
    th =surf(g, g['xh'], 'upper') - surf(g, g['xh'], 'lower')
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
    g['tube_groove_y'] = [tuple(r) for r in lv('elevon.tube_groove_y_m', 'm')]      # D6-R2 (CR-D6-14)
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
    # seam-free LE (CR-B2-17): one wide strip laid last, centred so both edges sit aft of x/c 0.10
    le_w, le_up, lap = lv('skin.le_strip_w_m', 'm'), lv('skin.le_strip_upper_arc_m', 'm'), lv('skin.overlap_m', 'm')
    g['le_edge'] = {'upper': x_at_arc(g, le_up, 'upper'), 'lower': x_at_arc(g, le_w - le_up, 'lower')}
    g['skin_lap'] = {'upper': x_at_arc(g, le_up - lap, 'upper'), 'lower': x_at_arc(g, le_w - le_up - lap, 'lower')}
    g['le_clean_x'] = lv('skin.le_clean_xc', '-') * c
    g['tab_tape_w'] = lv('skin.tab_edge_tape_w_m', 'm')
    # recess-step fillet (D-69, CR-C3-17): legs along the floor and up the step (capped by the step height)
    lf, lw = lv('recess.step_fillet_legs_m', 'm')
    # also capped at the pod floor board (D2: pod floor = fins.board_t_m foam board), whose bevelled aft edge sits on
    # the fillet: a 5 mm leg stood 0.2 mm proud of the 4.8 mm floor, into the tray (collision check)
    g['rf_legs'] = (lf, min(lw, surf(g, g['x_rec1'], 'upper') - g['z_rec'], v('fins.board_t_m', 'm')))
    return g


def arc(g, x0, x1, side, n=200):
    """Surface arc length (m) from x0 to x1 on one side (cosine-spaced polyline)."""
    s, xp, zp = 0.0, None, None
    for i in range(n + 1):
        x = x0 + (x1 - x0) * (1 - math.cos(math.pi * i / n)) / 2
        z = surf(g, x, side)
        if xp is not None:
            s += math.hypot(x - xp, z - zp)
        xp, zp = x, z
    return s


def x_at_arc(g, s, side):
    """Station x (m) where the surface arc from the LE reaches s (one cumulative table over the front 40 % of the
    chord, 400 cosine-spaced points, linear between them)."""
    n, xe = 400, 0.4 * g['c']
    acc, xp, zp = 0.0, None, None
    for i in range(n + 1):
        x = xe * (1 - math.cos(math.pi * i / n)) / 2
        z = surf(g, x, side)
        if xp is not None:
            d = math.hypot(x - xp, z - zp)
            if acc + d >= s:
                return xp + (x - xp) * (s - acc) / d
            acc += d
        xp, zp = x, z
    raise ValueError('arc %.4f m is past 40 %% of the chord' % s)


def corner_ext(r, u):
    """x extent aft of the hinge of the R r foam fill at distance u from the tab face (0 at u >= r)."""
    return 0.0 if u >= r else r - math.sqrt(max(r * r - (r - u) ** 2, 0.0))


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
                if abs(x - (b if descending else a)) < 1e-9:              # first end: (skin), then the floor polyline
                    if interior:
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
    # the core outline's stations inside [x0, x1] are added, so the strip's inner face never chords inside the core
    # (collision check: the LE strip's 2 mm first chord sat 0.32 mm inside the foam at the nose)
    xs = _xs(x0, x1, [x for x in _xs(0.0, g['c']) if x0 < x < x1])

    def off(x, d):
        """Point on the section at x moved d along the outward surface normal (a vertical offset grazed the foam
        where the nose is near vertical: collision check, LE strip 0.1 mm into the core at x 0.7 mm)."""
        h = 1e-5
        za, zb = surf(g, max(x - h, 0.0), side), surf(g, min(x + h, g['c']), side)
        dz = (zb - za) / (min(x + h, g['c']) - max(x - h, 0.0))
        n = math.hypot(1.0, dz)
        return (x - s * dz / n * d, surf(g, x, side) + s * d / n)
    inner = [off(x, z_off) for x in xs]
    outer = [off(x, z_off + t) for x in reversed(xs)]
    return _dedupe(inner + outer)


# ----------------------------------------------------------------------------- span plan of the core
def features(g):
    """Right-hand features: (kind, y0, y1). The left hand is the exact mirror."""
    f = [('recess', 0.0, g['y_pod']), ('window', g['win_y'][0], g['win_y'][1]),
         ('tie', g['tie_y'] - g['tie_w'] / 2, g['tie_y'] + g['tie_w'] / 2),
         ('anchor', g['anc_y'][0], g['anc_y'][1]), ('block', g['blk_y'][0], g['blk_y'][1]),
         ('groove', g['groove_y'][0], g['groove_y'][1]), ('sgroove', g['sgroove_y'][0], g['sgroove_y'][1]),
         ('sbranch', g['sgroove_y'][1] - g['sgroove'][1] / 2, g['sgroove_y'][1] + g['sgroove'][1] / 2),
         ('pocket', g['sp_y'][0], g['sp_y'][1]), ('spar', 0.0, g['spar_half']), ('jr', g['jr_y'][0], g['jr_y'][1])]
    f += [('elevon', a, b) for a, b in g['spans']]
    # stepped zones (n spanwise steps each): pocket corners R, lip beads, elevon cut-out corners R
    (b0, b1), rp, lb, (t0, t1), r = g['blk_y'], g['blk_rp'], g['bead_leg'], g['tab_y'], g['ecr']
    for kind, a, b in (('bstep', b0, b0 + rp), ('bstep', b1 - rp, b1), ('bead', b0 - lb, b0), ('bead', b1, b1 + lb),
                       ('ecorner', t0 - r, t0), ('ecorner', t1, t1 + r)):
        n = g['n_step']
        f += [(kind, a + (b - a) * i / n, a + (b - a) * (i + 1) / n) for i in range(n)]
    return f


def bead_depth(g, y0, y1):
    """Depth of the stepped lip bead in span step y0..y1 (circumscribes the 45 deg triangle: never under the leg)."""
    dist = max(g['blk_y'][0] - y1, y0 - g['blk_y'][1])                 # from the pocket wall to the step's near end
    return g['bead_leg'] - max(dist, 0.0)


def pocket_x(g, y0, y1):
    """Block-pocket x range in span step y0..y1: narrowed in the R corner zones, evaluated at the step's inner end so
    the pocket always contains D3's rounded block."""
    xa, xb = g['blk_x']
    rp = g['blk_rp']
    d = min(y1 - g['blk_y'][0], g['blk_y'][1] - y0)
    if d < rp - 1e-9:
        dx = rp - math.sqrt(max(rp * rp - (rp - d) ** 2, 0.0))
        xa, xb = xa + dx, xb - dx
    return xa, xb


def core_corner_x(g, y0, y1):
    """Core aft end in span step y0..y1 of an elevon cut-out: hinge line plus the R fill at the tab, taken at the
    step's far end from the tab (less foam than the true radius)."""
    u = max(g['tab_y'][0] - y0, y1 - g['tab_y'][1])
    return g['xh'] + corner_ext(g['ecr'], u)


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


def segment_loops(g, act, y0=None, y1=None):
    """Loops for one segment y0..y1: [(outer, [holes])...] (two entries when a full-depth cut splits the section).
    y0, y1 (right-hand, >= 0) set the stepped zones; without them the plain cut is drawn."""
    xf, xa = g['x_slot']
    stepped = y0 is not None
    x_end = g['xh'] if 'elevon' in act else g['c']
    if 'elevon' in act and 'ecorner' in act and stepped:
        x_end = core_corner_x(g, y0, y1)
    up, lo, holes_at = [], [], []
    if 'bead' in act and stepped:
        d = bead_depth(g, y0, y1)
        bx0, bx1 = g['blk_x']
        up.append((bx0, bx1, lambda x, d=d: surf(g, x, 'upper') - d))
        lo.append((bx0, bx1, lambda x, d=d: surf(g, x, 'lower') + d))
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
    j0, j1 = g['jr_x']
    if 'sbranch' in act:
        xc, w, d = g['sgroove']
        up = [u for u in up if abs(u[0] - (xc - w / 2)) > 1e-9]                # the branch replaces the groove here
        xb0, xb1 = xc - w / 2, g['lead_x'][0]
        if 'jr' in act:                                                        # branch floor dropping into the JR recess
            fl = [(x, surf(g, x, 'upper') - d) for x in reversed(_xs(j1, xb1))]
            fl += [(j1, surf(g, j1, 'upper') - g['jr_d'])]
            fl += [(x, surf(g, x, 'upper') - g['jr_d']) for x in reversed(_xs(j0, j1))][1:]
            fl += [(x, surf(g, x, 'upper') - d) for x in reversed(_xs(xb0, j0))]
            up.append((xb0, xb1, fl))
        else:
            up.append((xb0, xb1, lambda x, d=d: surf(g, x, 'upper') - d))
        split.append(g['lead_x'])                                              # lead hole down into the pocket
    elif 'jr' in act:
        up.append((j0, j1, lambda x: surf(g, x, 'upper') - g['jr_d']))
    if 'pocket' in act:
        lo.append((g['sp_x'][0], g['sp_x'][1], g['sp_zc']))
    spar = 'spar' in act
    if 'block' in act:
        split.append(pocket_x(g, y0, y1) if stepped else g['blk_x'])
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
    # outer panels (right; mirrored): the spanwise strips stop under the LE strip (10 % overlap), the LE strip is laid
    # last over both faces in one piece so no edge lies ahead of x/c 0.10 (CR-B2-17)
    plan += [('skin upper', 'upper', g['skin_lap']['upper'], xh, yp, g['half'], 1),
             ('skin lower', 'lower', g['skin_lap']['lower'], xh, yp, g['half'], 1),
             ('LE strip upper', 'upper', 0.0, g['le_edge']['upper'], yp, g['half'], 1),
             ('LE strip lower', 'lower', 0.0, g['le_edge']['lower'], yp, g['half'], 1)]
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


def p1_holes(g, d=0.008, n=24):
    """F2's P1 pass-through (harness params groove.p1_y_*_m, x between the + / - grooves): an 8 mm hole drilled at
    45 deg outboard from the upper mouth to the lower mouth, as a straight Y-loft of the hole's elliptical sections
    (a cylinder whose axis lies in the y-z plane), run 6 mm past each surface. Right and left. Cuts only."""
    H = k9.local('harness')
    gv = lambda k: k9.lval(H, 'harness.groove.' + k, 'm', None)
    try:
        ya, yb = gv('p1_y_upper_m'), gv('p1_y_lower_m')
        holes = [((gv('x_pos_m') + gv('x_neg_m')) / 2, d, 'P1 lead hole'),
                 (gv('x_sig_m') - 0.0045, 0.004, 'P1s signal hole')]  # D-85: lower-station ESC signal lead
    except (KeyError, TypeError):
        return []
    out = []
    for x, dd, nm in holes:
        za, zb = surf(g, x, 'upper'), surf(g, x, 'lower')
        dy, dz = yb - ya, zb - za
        L = math.hypot(dy, dz)
        rz = (dd / 2) * L / abs(dy)                          # section of the slanted hole by a y-plane
        ext = 0.006 * abs(dy) / L
        for s in (1, -1):
            secs = []
            for y in (ya - ext, yb + ext):
                zc = za + dz * (y - ya) / dy
                loop = [(x + dd / 2 * math.cos(2 * math.pi * i / n), zc + rz * math.sin(2 * math.pi * i / n))
                        for i in range(n)]
                secs.append((s * y, loop))
            out.append(fk.Shape('loft', nm, axis='Y', smooth=False, sections=sorted(secs)))
    return out


def fillet_trims(ctx, g, inset=0.0005, below=0.0005, above=0.0012):
    """D-88: the tape trimmed square along the fin root fillets' edges (skin laid after the fins, BUILD-GUIDE stage 6;
    interfaces/seats.json WNG-003 / FIN-001): per fin face and fillet zone, an X-loft of the (y, z) rectangle from
    inset inside the board face to the fillet's edge (its leg), below / above the surface, on the wing's own section
    stations. The fillet itself cuts the tape too, but a cut against its feather edge left 0.075-0.094 mm tape slivers
    in the exported model (GLB gate); this cut ends the tape on a square edge instead. Zones from the fins module
    (fins.py geometry()['fillet_zones']), so the trim follows any fillet change. Right and left, upper and lower."""
    import importlib.util
    import os
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            'fins', 'fusion', 'fins.py')
        spec = importlib.util.spec_from_file_location('fins_for_wing_trim', path)
        fm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fm)
        G = fm.geometry(ctx.params, k9.local('fins'), g['coords'])
    except (OSError, KeyError, NameError, ImportError) as e:
        print('wing: fillet_trims skipped (%s)' % e)
        return []
    out = []
    for upper in (True, False):
        side, s = ('upper', 1) if upper else ('lower', -1)
        for x0, x1, leg in G['fillet_zones'](upper):
            if x1 - x0 < 1e-4:
                continue
            xs = _xs(0.0, g['c'])
            xs = sorted(set([x0, x1] + [x for x in xs if x0 + 1e-6 < x < x1 - 1e-6]))
            for d in (1, -1):
                yF = G['yf'] + d * G['t_fin'] / 2
                ya, yb = sorted((yF - d * inset, yF + d * leg))
                for m in (1, -1):
                    secs = []
                    for x in xs:
                        z = surf(g, x, side)
                        za, zb = sorted((z - s * below, z + s * above))
                        secs.append((x, [(m * ya, za), (m * yb, za), (m * yb, zb), (m * ya, zb)][::m]))
                    out.append(fk.Shape('loft', 'tape trim at fillet edge', axis='X', smooth=False, sections=secs))
    return out


def p1s_jog(g, n=6):
    """D-86 (F2 groove.p1s_jog_m): a groove in the lower surface from the P1s lower mouth across to the signal groove,
    so the lower-station signal lead stays under the tape: the signal-groove section (width x depth) along the segment
    (x0, y0) -> (x1, y1), right and left, as Z-prisms from 1 mm below the skin line up to the groove floor."""
    H = k9.local('harness')
    try:
        x0, y0, x1, y1 = k9.lval(H, 'harness.groove.p1s_jog_m', 'm')
        w, d = [v / 1000.0 for v in k9.lval(H, 'harness.groove_size_mm', 'mm')['signal']]
    except (KeyError, TypeError, ValueError):
        return []
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L * w / 2, (x1 - x0) / L * w / 2
    zs = [surf(g, x0 + (x1 - x0) * i / n, 'lower') for i in range(n + 1)]
    z0, z1 = min(zs) - 0.001, max(zs) + d
    out = []
    for s in (1, -1):
        loop = [(x0 + nx, s * (y0 + ny)), (x1 + nx, s * (y1 + ny)), (x1 - nx, s * (y1 - ny)), (x0 - nx, s * (y0 - ny))]
        out.append(fk.Shape('prism', 'P1s jog groove', axis='Z', offset=z0, depth=z1 - z0,
                            loops=[loop if s > 0 else loop[::-1]]))
    return out


def skin_slits(g):
    """D-86 (F2 cad.skin_slots): the tape opened round a lead where the drawn lead passes the skin, as on the bench
    (lead laid, tape cut round it): a Z-prism over [x0, x1] x [y0, y1], 4 mm either side of that surface."""
    H = k9.local('harness')
    try:
        slots = H['harness']['cad']['skin_slots']['value']
    except (KeyError, TypeError):
        return []
    out = []
    for x0, x1, y0, y1, side in slots:
        zs = [surf(g, min(max(x, 0.0), g['c']), side) for x in (x0, (x0 + x1) / 2, x1)]
        out.append(fk.Shape('prism', 'tape slit', axis='Z', offset=min(zs) - 0.004, depth=max(zs) - min(zs) + 0.008,
                            loops=[[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]))
    return out


def elevon_section(g, groove=True):
    """Panel section: upper skin TE -> hinge, 30 deg lower bevel, D6's torque-tube groove open below (where the tube
    runs), lower skin -> TE."""
    xh, c, b = g['xh'], g['c'], g['bevel']
    gx0, gx1, gzc = g['tube_groove']
    zu0, zl1 = surf(g, xh, 'upper'), surf(g, xh + b, 'lower')
    zbev = lambda x: zu0 + (x - xh) / b * (zl1 - zu0)
    up = [(x, surf(g, x, 'upper')) for x in reversed(_xs(xh, c))]
    if not groove:
        lo = [(xh + b, zl1)] + [(x, surf(g, x, 'lower')) for x in _xs(xh + b, c)][1:]
        return _dedupe(up + lo)
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


def panel_start_x(g, ya, yb):
    """Panel front in span step ya..yb near the fin-root tab: the core's R fill plus the end gap in x, taken at the
    step's near end to the tab (more relief than the true radius, so the panel never meets the fill)."""
    gap, r, n = g['e_gap'], g['ecr'], g['n_step']
    u_near = (ya - g['tab_y'][1]) if ya >= g['tab_y'][1] - 1e-9 else (g['tab_y'][0] - yb)   # outboard / inboard panel
    w = u_near - gap                                                       # past the end gap
    if w >= r - 1e-9:
        return g['xh']
    k = int(max(w, 0.0) / (r / n) + 1e-6)                                   # panel step k faces core steps k, k+1
    return g['xh'] + corner_ext(r, k * r / n) + gap


def elevon_pieces(g, y0, y1):
    """[(y_from, y_to, loop)] for one right-hand panel between y0 and y1 (gaps applied by the caller): the section
    with D6's torque-tube groove where the tube runs (D6-R2 y ranges), without it elsewhere; at a horn-blade slot the
    section minus the blade x range; at the fin-root tab end the front corner relieved round the core's R fill
    (CR-C2-13), stepped like the core."""
    r, n, gap = g['ecr'], g['n_step'], g['e_gap']
    t0, t1 = g['tab_y']
    br = {y0, y1}
    br |= {v for a, b in g['horn_y'] for v in (a, b)}
    br |= {v for a, b in g['tube_groove_y'] for v in (a, b)}
    br |= {t0 - gap - r * i / n for i in range(n + 1)} | {t1 + gap + r * i / n for i in range(n + 1)}
    ys = sorted(round(v, 7) for v in br if y0 - 1e-9 <= v <= y1 + 1e-9)
    out = []
    for a, b in zip(ys, ys[1:]):
        if b - a < 1e-7:
            continue
        ym = (a + b) / 2
        grooved = any(p <= ym <= q for p, q in g['tube_groove_y'])
        sec = elevon_section(g, grooved)
        xs = panel_start_x(g, a, b)
        if xs > g['xh'] + 1e-9:
            sec = clip_x(sec, xs, g['c'])
        if any(p < ym < q for p, q in g['horn_y']):
            if g['horn_x'][0] - max(xs, g['xh']) > 1e-4:          # D-82: slot open from the hinge, no front sliver
                out.append((a, b, clip_x(sec, max(xs, g['xh']), g['horn_x'][0])))
            out.append((a, b, clip_x(sec, g['horn_x'][1], g['c'])))
        else:
            out.append((a, b, sec))
    return out


# ----------------------------------------------------------------------------- build
def build(ctx):
    g = layout(ctx)
    v = ctx.value

    # WNG-001 core: right-hand segments, then the exact mirror into the same component
    core = ctx.part('WNG-001')
    right = []
    for y0, y1, act in segments(g):
        for i, (loop, holes) in enumerate(segment_loops(g, act, y0, y1)):
            nm = 'xps core y%.3f-%.3f%s' % (y0, y1, '' if i == 0 else ' aft')
            if y0 == 0.0:                                     # centre segment spans y -y1 .. +y1 as one body
                right.append(core.prism('Y', -y1, [loop] + holes, 2 * y1, name=nm))
            else:
                right.append(core.prism('Y', y0, [loop] + holes, y1 - y0, name=nm))
    for s in [s for s in right if s.offset >= 0.0]:
        core._add(s.mirrored(1))
    for cutter in p1_holes(g):                                # F2's 45 deg P1 lead hole, both sides (core and skin)
        core.cut(cutter, note='P1 lead pass-through, 8 mm drilled with a guide block (harness BUILD step 4)')
    xc, w, d = g['sgroove']                                   # D-87: 3 mm relief at the inside corner where the servo
    xr, yb = xc + w / 2, g['sgroove_y'][1] - w / 2            # groove turns into its branch (the 3.6 mm ribbon turns
    zr = surf(g, xr, 'upper')                                 # on its 3.9 mm bend there)
    for s_ in (1, -1):
        tri = [(xr, s_ * (yb - 0.003)), (xr + 0.003, s_ * yb), (xr, s_ * yb)]
        core.cut(fk.Shape('prism', 'servo groove corner relief', axis='Z', offset=zr - d, depth=d + 0.002,
                          loops=[tri if s_ > 0 else tri[::-1]]), note='servo groove corner relief (D-87)')
    for cutter in p1s_jog(g):                                 # D-86: lower-surface jog P1s mouth -> signal groove
        core.cut(cutter, note='jog groove from the P1s lower mouth to the signal groove (hand-cut with the grooves)')

    # WNG-006 block-pocket lip beads (D-68): microballoon epoxy in the stepped 45 deg chamfer along the inboard and
    # outboard pocket lips, upper and lower surface, sanded flush; the 60 mm tape doubler runs over them
    bead = ctx.part('WNG-006-R')
    for y0, y1, act in segments(g):
        if 'bead' in act:
            d = bead_depth(g, y0, y1)
            for side in ('upper', 'lower'):
                bead.prism('Y', y0, [skin_strip(g, g['blk_x'][0], g['blk_x'][1], side, -d, d)], y1 - y0,
                           name='bead pocket lip %s' % side)
    k9.pair(ctx, 'WNG-006-R', 'WNG-006-L')
    for e in ('E-WNG-12', 'E-WNG-13'):
        ctx.contact(e, 'lip bead bonded in the chamfer of the core pocket lip (laid wet, sanded flush)')
    for e in ('E-WNG-14', 'E-WNG-15'):
        ctx.contact(e, 'lip bead wets the through-core block side face (laid in the block bond)')

    # D-103 (CR-C3-17 superseded): no recess-step fillet (was WNG-007) and no floor bevel; the pod floor end sits square
    # on the step (C3-R4 FEA: the fillet did not lower the crash peak and the bevel failed in flight)

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
    for cutter in p1_holes(g):                                # the tape is cut at both P1 mouths
        skin.cut(cutter, note='tape opened over the P1 mouths')
    for cutter in skin_slits(g):                              # D-86: slit round each lead where it passes the tape
        skin.cut(cutter, note='tape slit round a lead (F2 cad.skin_slots)', shop=False)
    for cutter in fillet_trims(ctx, g):                       # D-88: trimmed square along the fin root fillets
        skin.cut(cutter, note='tape trimmed along the fin root fillet edge (skin laid after the fins)', shop=False)
    t = g['t_skin']
    layer = {'doubler block': 2, 'doubler servo': 1, 'LE strip': 1}          # layers under each piece
    for name, side, x0, x1, y0, y1, _n in skin_plan(g):
        off = t * next((v for k, v in layer.items() if name.startswith(k)), 0)
        s = skin.prism('Y', y0, [skin_strip(g, x0, x1, side, off, t)], y1 - y0, name='tape ' + name)
        if y0 > 0:
            skin._add(s.mirrored(1))
    tip = skin.prism('Y', g['half'], [outline(g, 0.0, g['c'])], 2 * t, name='tape tip edge')
    skin._add(tip.mirrored(1))
    # tab tape carried round the elevon cut-out edges (CR-C2-13): a strip folded over each tab side face, round the
    # R fill at the hinge (flat face drawn from the end of the radius to the TE)
    t0, t1 = g['tab_y']
    face = outline(g, g['xh'] + g['ecr'], g['c'])
    for ya in (t0 - t, t1):
        s = skin.prism('Y', ya, [face], t, name='tape tab edge')
        skin._add(s.mirrored(1))
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
