"""K09-L centre pod (D2, revision D2-R5 on params A1-R4): shell with the 15 mm longer nose (D-47), tray with the forward
and aft stops and guides, hatch with antenna tube, pack straps and pads, crush block, spreader and aft spacers (three
parts), GPS mast with the 45 deg pad, pitot socket with flange, carry handle on the spar.
R5 (D-47, CR-A1-43, CR-A3-22, CR-A5-27): pod nose x -0.130, length 0.225; XPS nose block A deleted, the forward stop
and the tray front sit on a 1 mm epoxy line against the nose wall (nose skin to stop face 8.8 mm); whole pack bay 21 mm
forward (forward stop -0.1212, aft stop 0.056 now on the tray rear piece with 2 gussets, handle bridge no longer a
stop); pack nominal centroid = params pod.pack_x_nominal_m (-0.022), per-pack stations and spacer stacks in
pack_x_per_pack_m; straps to -0.054 / 0.016; the wire channel to -0.0245 (the forward strap now sits over -0.0655);
crush block POD-009 and spreader POD-010 split from the spacer set POD-008 so each declared CG is its body centroid.
R4 (CR-F2-03, CR-F3-12, CR-F1-17, CR-C6-17/18/19, CR-A4-23): side-wall harness exits, the wire channel (tray split,
guides notched), JR tie bar, UBEC plate, FC strap slots, tie posts 21 mm apart, keyed pitot bore, GPS cable path, PA66
mast screw, the forward stop derived from the nose. The AS150U park cradle is F1's (PWR-006, CR-F1-16).

Frame and datums: redesign/fusion/DATUMS.md (x aft, y right, z up, cruise attitude, metres).
Shared numbers from params.json (pod LE, L x W x H, base, board thickness, pack size, spar, pitot tip); pod-only
numbers from subsystems/pod/params.json. `layout()` is a pure function of those numbers and the wing section;
team/D2/pod_data.py (masses, CGs, interfaces.json) and team/D2/pod_claims.py (proof chain) import it, so the CAD,
the mass roll-up and the claims cannot disagree.

Arrangement (SPEC.md): the pack bay runs down the middle. From the nose aft: foam-board nose wall (x_le -0.130) ->
1 mm epoxy line -> 3 mm printed forward stop on the tray (aft face x -0.1212) -> removable XPS crush block cut per pack
(POD-009) -> 1.5 mm spreader (POD-010) -> pack (nominal centroid x -0.022) -> printed U-spacers (POD-008) -> 3 mm aft
stop at x 0.056 on the tray rear piece. The pack sits wholly on the tray (aft face <= 0.056, recess end 0.065).
FC on gel pads in the right channel, UBEC behind it; airspeed sensor, receiver, PDB, fuse and the AS150U park in the
left channel; pitot socket with its flange at the left of the nose; ram-air vent over the pack; two antenna exits.

UNVERIFIED-IN-FUSION: Y-normal prisms whose loops follow the S5010 upper surface (side walls with the exit holes, LE
filler, saddle tongues); prisms with many hole loops (tray, deck, nose wall, JR bar, FC end stops); the 45 deg
GPS pad (Y-normal prism with a rotated rectangle); the keyhole loops of the right-leg windows. None of it uses booleans.
Not modelled as bodies (STANDARDS section 3): fasteners, ties, glue, hook-and-loop, tape, label, the 1 mm strap
groove cut in the foam floor, the mast cross-screw counterbore; heat-set inserts are the boss bores.
"""
import math

import k09kit as k9


def _lv(L, key):
    d = L[key]
    return d['value'] if isinstance(d, dict) and 'value' in d else d


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _circle(cu, cv, r, n=12):
    return [(cu + r * math.cos(2 * math.pi * i / n), cv + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _notched(y0, y1, z0, z1, nw, nd):
    """(y, z) outline of a section y0..y1 x z0..z1 with a centred top notch nw wide, nd deep (vent path)."""
    return [(y0, z0), (y1, z0), (y1, z1), (nw / 2, z1), (nw / 2, z1 - nd), (-nw / 2, z1 - nd), (-nw / 2, z1), (y0, z1)]


def _unotch(y0, y1, z0, z1, yc, nw, nd):
    """(y, z) outline of a wall y0..y1 x z0..z1 (y0 < y1) with a top notch nw wide, nd deep, centred at yc."""
    return [(y0, z0), (y1, z0), (y1, z1), (yc + nw / 2, z1), (yc + nw / 2, z1 - nd), (yc - nw / 2, z1 - nd),
            (yc - nw / 2, z1), (y0, z1)]


def _keyhole(cx, cy, h, r, side, n=8):
    """(x, y) outline of a square leg (half side h) whose bore (radius r) is opened to the +y (side=1) or -y face."""
    s = side
    pts = [(cx - h, cy - s * h), (cx + h, cy - s * h), (cx + h, cy + s * h), (cx + r, cy + s * h), (cx + r, cy)]
    for i in range(1, n):                                  # arc round the closed side of the bore
        a = -s * math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts += [(cx - r, cy), (cx - r, cy + s * h), (cx - h, cy + s * h)]
    return pts if s > 0 else pts[::-1]


def _net_area(loops):
    """Area of the first (outer) loop less the others (holes), shoelace, m2."""
    a = lambda p: abs(sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1] for i in range(len(p)))) / 2
    return a(loops[0]) - sum(a(h) for h in loops[1:])


def _tray_loops(g, border, a, b, wa, wz, slots):
    """(x, y) loops of a tray floor piece a..b: outer rectangle, the strap slots inside it, and lightening windows in the
    free stretches of wa..wz between the slots (border from ends and slots in x, from the guides in y)."""
    wb, wy = border
    half = g['bw'] / 2 + g['tg']
    mine = [s for s in slots if a < s[0][0] and s[1][0] < b]
    free, x = [], wa
    for s0, s1 in sorted((s0, s1) for s0, s1 in g['strap_slots'] if s1 > wa and s0 < wz):
        if s0 > x:
            free.append((x, s0))
        x = max(x, s1)
    if wz > x:
        free.append((x, wz))
    wins = [_rect(f0 + wb, -(g['bw'] / 2 - wy), f1 - wb, g['bw'] / 2 - wy) for f0, f1 in free if f1 - f0 > 2 * wb + 0.006]
    return [_rect(a, -half, b, half)] + mine + wins


def _surf(coords, c, x):
    return k9.surface_z(coords, c, x / c, 'upper')


def layout(get, L, coords):
    """All pod geometry (m) from params getter `get(key, unit)`, pod-local params `L` and the wing section."""
    g = {}
    lv = lambda k: _lv(L, k)
    c = get('wing.chord_m', 'm')
    x0 = get('pod.x_le_m', 'm')
    Lp, W, H = get('pod.size_m', 'm')
    zb = get('pod.z_base_m', 'm')
    tb = get('fins.board_t_m', 'm')
    xs, zs = get('wing.spar.x_m', 'm'), get('wing.spar.z_m', 'm')
    rs = get('wing.spar.od_m', 'm') / 2
    pk = get('battery.size_m', 'm')
    g.update(x0=x0, x1=x0 + Lp, W=W, yi=W / 2 - tb, H=H, zb=zb, ztop=zb + H, tb=tb, xs=xs, zs=zs, rs=rs, chord=c, pack=pk)
    g['xn'] = x0 + tb                                   # nose wall inner face
    g['zh'] = g['ztop'] - tb                            # side-wall tops = hatch underside
    g['zf'] = zb + tb                                   # foam floor top = tray underside
    g['zt'] = g['zf'] + lv('tray_floor_t_m')            # tray top
    g['zp'] = g['zt'] + lv('pad_t_m')                   # pack underside (on the pads)
    g['x_slot_f'], g['x_slot_a'] = xs - rs, xs + rs     # spar slot faces
    g['x_rec1'] = g['x_slot_f'] - lv('slot_wall_m')     # recess end = tray aft end
    lo, hi = 0.0, xs                                    # recess start: upper surface = pod base
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _surf(coords, c, mid) < zb else (lo, mid)
    g['x_rec0'] = (lo + hi) / 2
    g['bw'] = lv('bay_min_m')[1]
    g['tg'], g['hg'] = lv('guide_t_m'), lv('guide_h_m')
    # forward end: nose wall | fixed nose block | forward stop | crush block | spreader | pack
    fs_t, fs_h, fs_w = lv('fwd_stop_m')
    g['nose_block'] = lv('nose_block_l_m')              # fixed XPS block A
    g['x_fs0'] = g['xn'] + g['nose_block']              # forward stop fore face = nose block aft face = tray front
    g['x_fs'] = g['x_fs0'] + fs_t                       # forward stop aft face (-0.1002 at x_le -0.115)
    # aft end: pack | spacers | aft stop (R5: on the tray rear piece, 9 mm ahead of the recess end)
    g['x_as'] = lv('aft_stop_x_m')
    as_t, as_top = lv('aft_stop_m')
    g['as_t'] = as_t
    g['z_as_top'] = g['zp'] + as_top
    a_nom, a_hvy = lv('pack_aft_face_m')
    x_nom_shared = get('pod.pack_x_nominal_m', 'm')     # D-47: A1's nominal centroid; the local aft face must agree
    if abs((a_nom - pk[0] / 2) - x_nom_shared) > 0.0005:
        raise ValueError('pod params pack_aft_face_m[0] %.4f does not put the pack centroid at pod.pack_x_nominal_m %.4f'
                         % (a_nom, x_nom_shared))
    g['pack_aft_nom'], g['pack_aft_hvy'] = a_nom, a_hvy
    g['pack_c_nom'] = a_nom - pk[0] / 2
    g['pack_c_hvy'] = a_hvy - pk[0] / 2
    g['pack_fore_nom'] = a_nom - pk[0]
    g['pack_fwd_c'] = g['x_fs'] + pk[0] / 2             # centroid with the pack against the forward stop (no block)
    g['travel'] = g['x_as'] - g['x_fs'] - pk[0]         # stop-to-stop room beyond the pack length
    g['spacer_nom'] = g['x_as'] - a_nom
    g['spacer_hvy'] = g['x_as'] - a_hvy
    g['sp_t'] = lv('spreader_t_m')
    g['block_nom'] = g['pack_fore_nom'] - g['sp_t'] - g['x_fs']
    g['bay'] = (g['x_as'] - g['x_fs'], g['bw'], g['zh'] - g['zp'])
    # D-47 stations per weighed pack: spacer rounded to the 2 mm set, centroid achieved, crush block B cut length
    step = min(lv('spacer_set_m'))
    g['stations'] = {}
    for m, x_t in sorted(lv('pack_x_per_pack_m').items(), key=lambda kv: float(kv[0])):
        sp = max(0.0, round((g['x_as'] - (x_t + pk[0] / 2)) / step) * step)
        x_a = g['x_as'] - sp - pk[0] / 2
        g['stations'][m] = {'target': x_t, 'spacer': sp, 'x': x_a, 'block': (x_a - pk[0] / 2 - g['sp_t']) - g['x_fs']}
    g['tray_front_solid'] = lv('tray_front_solid_m')
    g['pod_c'] = x0 + Lp / 2
    g['pack_z_c'] = g['zp'] + pk[2] / 2
    # wing surface under the pack overhang and under the handle
    # R5: the pack no longer overhangs the recess end; overhang_clr is the margin of the most aft pack face (680 g, no
    # spacer) ahead of the recess end (>= 0: the pack sits wholly on the tray)
    g['overhang_surf'] = _surf(coords, c, g['x_rec1'])
    g['overhang_clr'] = g['x_rec1'] - a_hvy
    xa = [g['x_rec1'] + i * (g['x1'] - g['x_rec1']) / 8 for i in range(9)]
    g['aft_surf'] = [(x, _surf(coords, c, x)) for x in xa]
    g['z_aft'] = max(z for _, z in g['aft_surf'])
    g['xf'] = (g['x_slot_f'] - 0.002, g['x1'] - tb)     # handle foot x range (ends at the aft wall)
    g['zfoot'] = g['z_aft'] + lv('foot_plate_t_m')      # handle foot / bridge top
    g['z_cheek'] = zs + lv('tongue_cheek_frac') * rs
    g['x_hatch1'] = lv('hatch_aft_x_m')
    g['x_lip1'] = g['xn'] + lv('lip_m')[0]
    gx, gz = lv('grip_m')
    g['z_grip0'] = g['ztop'] + lv('grip_gap_m')
    g['z_grip1'] = g['z_grip0'] + gz
    sb = lv('socket_boss_m')
    g['z_sock1'] = g['z_grip1'] + sb[1]
    ms = lv('mast_m')
    g['z_mast1'] = g['z_grip1'] + ms[2]                 # mast top
    gp, gpt, _ct = lv('gps_plate_m')
    h = gp / (2 * math.sqrt(2))
    zb0 = g['z_mast1']                                  # wedge cheeks stand on the mast top
    n = (-1 / math.sqrt(2), 1 / math.sqrt(2))           # pad normal in (x, z): toward the nose and up
    A, C = (xs - h, zb0), (xs + h, zb0 + 2 * h)
    g['gps_wedge'] = (A, (xs + h, zb0), C, n, h, zb0)
    mid = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)
    g['gps_c'] = (mid[0] + n[0] * (gpt + 0.004), 0.0, mid[1] + n[1] * (gpt + 0.004))
    tip = get('avionics.pitot_tip_xyz_m', 'm')
    py, pz = tip[1], tip[2]
    so = lv('socket_m')
    g['pitot_axis'] = (py, pz)
    g['socket_x'] = (x0 - so[3], g['xn'] + so[2])
    g['pitot_tip'] = tuple(tip)
    g['boom_len'] = g['socket_x'][1] - tip[0]
    g['ch_y'] = (g['bw'] / 2 + g['tg'], g['yi'], (g['bw'] / 2 + g['tg'] + g['yi']) / 2)  # side channel inner, outer, centre
    g['strap_x'] = list(lv('strap_x_m'))
    # antenna A (hatch tube) and B (nose tube), GPS clearances, for the claims
    ax, ay = lv('ant_tube_xy_m')
    od, _bore, ztube = lv('ant_tube_m')
    g['ant_a'] = (ax, ay, ztube)
    ci = g['ch_y'][0]
    g['ant_a_pack_clr'] = math.hypot(abs(ay) - pk[1] / 2, ztube - (g['zp'] + pk[2]))
    ny, nz = lv('nose_ant_m')[:2]
    g['ant_b'] = (x0, ny, nz)
    g['ant_b_pack_clr'] = g['pack_fore_nom'] - x0       # element starts at the nose skin, pack fore face behind it
    g['ant_b_boom_clr'] = abs(pz - nz)
    zone = lambda x0_, x1_, ysign: [(x, ysign * g['ch_y'][2], g['zf'] + 0.012) for x in (x0_, x1_)]
    gc = g['gps_c']
    dist = lambda p: math.sqrt(sum((p[i] - gc[i]) ** 2 for i in range(3)))
    g['gps_clr'] = {'PDB': min(dist(p) for p in zone(*lv('pdb_plate_x_m'), -1)),
                    'AS150U park': min(dist(p) for p in zone(*lv('park_x_m'), -1)),
                    'UBEC': min(dist(p) for p in zone(*lv('ubec_zone_x_m'), 1))}
    g['ci'] = ci
    # R4: wire channel across the bay (tray split), crossing behind the aft stop, park pocket, forward-stop tray bond
    chx, chw, chh = lv('floor_channel_m')
    g['ch_x'] = (chx - chw / 2, chx + chw / 2)
    g['ch_h'] = g['zp'] - g['zf']                       # foam-board floor to pack underside in the channel
    g['ch_notch'] = chh
    lg = lv('leg_m')[0]
    g['cross_gap'] = (g['x1'] - tb) - (xs + lg / 2)     # handle-leg aft face to aft-wall inner face
    g['cross_h'] = g['zh'] - g['zfoot']                 # bridge top to deck underside
    g['tray_front_area'] = min(g['tray_front_solid'], g['ch_x'][0] - g['x_fs0']) * (g['bw'] + 2 * g['tg'])
    # tray floor pieces (R5): strap slots in whichever piece they fall, lightening windows only between the solid zones
    sl, sw = lv('strap_slot_m')
    g['strap_yo'] = g['bw'] / 2 - 0.0002
    ys0 = g['strap_yo'] - lv('strap_t_m') / 2           # slot centre under the strap leg
    g['strap_slots'] = [(xc - sl / 2, xc + sl / 2) for xc in g['strap_x']]
    slots = [_rect(a, s * ys0 - sw / 2, b, s * ys0 + sw / 2) for a, b in g['strap_slots'] for s in (1, -1)]
    c0, c1 = g['ch_x']
    pieces = (('petg bay floor front', (g['x_fs0'], c0), (g['x_fs0'] + g['tray_front_solid'], c0)),
              ('petg bay floor rear', (c1, g['x_rec1']), (c1, g['x_as'])))
    g['tray_loops'] = [(nm, _tray_loops(g, lv('window_border_m'), a, b, wa, wz, slots)) for nm, (a, b), (wa, wz) in pieces]
    g['tray_rear_area'] = _net_area(g['tray_loops'][1][1])  # net bond area of the piece that carries the aft stop
    g['nose_ant_in'] = lv('nose_ant_tube_in_m')
    return g


def build(ctx):
    v, L = ctx.value, ctx.local
    lv = lambda k: _lv(L, k)
    coords, _src = k9.section(ctx)
    G = layout(v, L, coords)
    x0, x1, W, yi, tb = G['x0'], G['x1'], G['W'], G['yi'], G['tb']
    zb, ztop, zh, zf, zt, zp = G['zb'], G['ztop'], G['zh'], G['zf'], G['zt'], G['zp']
    xn, xr0, xr1 = G['xn'], G['x_rec0'], G['x_rec1']
    x_fs, x_fs0, x_as = G['x_fs'], G['x_fs0'], G['x_as']
    bw, tg, hg = G['bw'], G['tg'], G['hg']
    xs, zs, rs = G['xs'], G['zs'], G['rs']
    pk = G['pack']
    c = G['chord']
    py, pz = G['pitot_axis']
    vw, vh = lv('vent_m')
    ny, nz, nod, nbore = lv('nose_ant_m')

    # ---------------------------------------------------------------- POD-001 shell (foam board, XPS LE filler and nose block, printed lip and antenna tube)
    sh = ctx.part('POD-001')
    sh.box((xn, -yi, zb), (xr1, yi, zf), name='fb floor')
    side = [(x0, zb), (xr1, zb)] + [(x, z) for x, z in G['aft_surf']] + [(x1, zh), (x0, zh)]
    se = lv('side_exit_m')                              # R4 (CR-F2-03 a): power + DShot exits, both sides
    side_exit = _rect(se[0], se[2], se[1], se[3])
    sh.prism('Y', yi, [side, side_exit], tb, name='fb side wall R')
    sh.prism('Y', -W / 2, [side, side_exit], tb, name='fb side wall L')
    sq = lv('socket_m')[0] / 2
    nose = [_rect(-yi, zb, yi, ztop), _rect(py - sq, pz - sq, py + sq, pz + sq),
            _rect(-vw / 2, zh - vh, vw / 2, zh), _circle(ny, nz, nod / 2 + 0.0002, 10)]
    sh.prism('X', x0, nose, tb, name='fb nose wall')
    # R5 (D-47): no XPS nose block A; the forward stop and tray front sit on a 1 mm epoxy line against the nose wall.
    # Antenna B tube: 4 mm out of the nose, through the wall, nose_ant_tube_in_m behind it, bonded in the wall hole
    sh.prism('X', x0 - 0.004, [_circle(ny, nz, nod / 2), _circle(ny, nz, nbore / 2, 8)], (xn + G['nose_ant_in']) - (x0 - 0.004),
             name='petg nose antenna tube')
    lip_l, lip_t = lv('lip_m')
    sh.box((xn, -yi + 0.02, ztop - lip_t), (G['x_lip1'], yi - 0.02, ztop), name='petg nose lip')
    n = 8
    filler = [(0.0, zb)] + [(xr0 * i / n, _surf(coords, c, xr0 * i / n)) for i in range(n + 1)]
    sh.prism('Y', -W / 2, filler, W, name='xps LE filler')
    ex = lv('cable_exit_m')
    aft_holes = [_rect(ex[0], ex[2], ex[1], ex[3]), _rect(-ex[1], ex[2], -ex[0], ex[3]), _rect(-vw / 2, zh - vh, vw / 2, zh)]
    sh.prism('X', x1 - tb, [_rect(-yi, G['z_aft'], yi, ztop)] + aft_holes, tb, name='fb aft wall')
    lg, _lb = lv('leg_m')
    ly = lv('leg_y_m')
    hh = lg / 2 + 0.0004
    deck = [_rect(G['x_hatch1'], -yi, x1 - tb, yi),
            _rect(xs - hh, ly - hh, xs + hh, ly + hh), _rect(xs - hh, -ly - hh, xs + hh, -ly + hh)]
    sh.prism('Z', zh, deck, tb, name='fb aft deck')

    # ---------------------------------------------------------------- POD-002 tray (printed PETG: bay tray + forward stop + guides, FC, avionics and PDB plates)
    tr = ctx.part('POD-002')
    ts, ws = lv('strap_t_m'), lv('strap_w_m')
    yo = G['strap_yo']                                  # strap leg outer face, just inside the guide
    c0, c1 = G['ch_x']                                  # R4 (CR-F2-03 d): wire channel splits the tray floor
    # R5: both pieces carry strap slots; the front piece is solid for tray_front_solid_m behind the forward stop, the
    # rear piece solid from the aft stop to its end (CL-D2-FWD-STOP-BOND, CL-D2-AFT-STOP-BOND)
    for name, loops in G['tray_loops']:
        tr.prism('Z', zf, loops, lv('tray_floor_t_m'), name=name)
    fs_t, fs_h, fs_w = lv('fwd_stop_m')
    tr.prism('X', x_fs0, [_rect(-fs_w / 2, zt, fs_w / 2, zt + fs_h)], fs_t, name='petg forward stop')
    gn = G['ch_notch']
    guide = [(x_fs, zt), (c0, zt), (c0, zt + gn), (c1, zt + gn), (c1, zt), (x_as, zt), (x_as, zt + hg), (x_fs, zt + hg)]
    for s in (1, -1):                                   # guides span the channel, notched 3 mm at the base; end at the aft stop
        tr.prism('Y', bw / 2 if s > 0 else -(bw / 2 + tg), guide, tg, name='petg guide')
    # R5 (D-47): aft stop on the tray rear piece (it was on the handle bridge at x 0.077), full bay + guide width, and
    # two gussets behind it to the tray end
    a_w = bw / 2 + tg
    as_t = G['as_t']
    tr.prism('X', x_as, [_rect(-a_w, zt, a_w, G['z_as_top'])], as_t, name='petg aft stop')
    gl, gt = lv('gusset_m')
    gl = min(gl, xr1 - (x_as + as_t))
    tri = [(x_as + as_t, zt), (x_as + as_t + gl, zt), (x_as + as_t, G['z_as_top'] - 0.004)]
    for s in (1, -1):
        tr.prism('Y', a_w - gt if s > 0 else -a_w, tri, gt, name='petg stop gusset')
    ci, co, cy = G['ch_y']
    tp = lv('plate_t_m')
    fx, fl_len = lv('fc_centre_x_m'), lv('fc_plate_len_m')
    bx = lv('fc_board_m')[0]
    tr.prism('Z', zf, [_rect(fx - fl_len / 2, ci + 0.0005, fx + fl_len / 2, co - 0.0005)], tp, name='petg FC plate')
    jb = lv('jr_bar_m')                                 # R4 (CR-F2-03 f): JR tie bar, 3 tie slots at its foot
    jx = (jb[0] + jb[1]) / 2 - jb[2] / 2
    jy0, jy1 = ci + 0.0005, co - 0.0005
    jslots = [_rect(jy0 + (jy1 - jy0) * k / 4 - jb[4] / 2, zf + 0.0005, jy0 + (jy1 - jy0) * k / 4 + jb[4] / 2,
                    zf + 0.0005 + jb[5]) for k in (1, 2, 3)]
    tr.prism('X', jx, [_rect(jy0, zf, jy1, zf + jb[3])] + jslots, jb[2], name='petg JR tie bar')
    u0, u1 = lv('ubec_zone_x_m')                        # R4 (CR-F1-17): UBEC on foam tape on a plate, not on the paper
    tr.prism('Z', zf, [_rect(u0, ci + 0.0005, u1, co - 0.0005)], tp, name='petg UBEC plate')
    st_t, st_h, st_w = lv('fc_stop_m')
    ssw, ssh = lv('fc_strap_slot_m')                    # R4 (CR-F3-12 c, CR-C6-19): strap slot at each stop root
    stop_sec = [_rect(cy - st_w / 2, zf + tp, cy + st_w / 2, zf + tp + st_h),
                _rect(cy - ssw / 2, zf + tp + 0.0005, cy + ssw / 2, zf + tp + 0.0005 + ssh)]
    for s in (1, -1):
        xa = fx + s * (bx / 2 + 0.002)
        tr.prism('X', min(xa, xa + s * st_t), stop_sec, st_t, name='petg FC end stop')
    ax0, ax1 = lv('avn_plate_x_m')
    tr.prism('Z', zf, [_rect(ax0, -co + 0.0005, ax1, -ci - 0.0005)], tp, name='petg avionics plate')
    pw, pd, ph = lv('tie_post_m')
    for dx in lv('tie_post_x_m'):                       # R4 (CR-F3-12 a): inner faces 21 mm apart
        tr.box((ax0 + dx - pw / 2, -cy - pd / 2, zf + tp), (ax0 + dx + pw / 2, -cy + pd / 2, zf + tp + ph), name='petg tie post')
    p0, p1 = lv('pdb_plate_x_m')
    tr.prism('Z', zf, [_rect(p0, -co + 0.0005, p1, -ci - 0.0005)], tp, name='petg PDB plate')
    bd, bh, pp = lv('boss_d_m'), lv('boss_h_m'), lv('pdb_pattern_m')
    pcx = (p0 + p1) / 2
    for dx in (-pp / 2, pp / 2):
        for dy in (-pp / 2, pp / 2):
            tr.prism('Z', zf + tp, [_circle(pcx + dx, -cy + dy, bd / 2), _circle(pcx + dx, -cy + dy, 0.002, 8)], bh,
                     name='petg PDB boss')

    # ---------------------------------------------------------------- POD-003 hatch (foam board, printed tongue, latch tab, antenna tube A)
    ha = ctx.part('POD-003')
    ax, ay, ztube = G['ant_a']
    aod, abore, _zt = lv('ant_tube_m')
    ha.prism('Z', zh, [_rect(G['x_lip1'], -W / 2, G['x_hatch1'], W / 2), _circle(ax, ay, aod / 2 + 0.0002, 10)], tb, name='fb hatch')
    ha.box((xn + 0.0005, -yi + 0.02, zh), (G['x_lip1'], yi - 0.02, zh + lv('tongue_t_m')), name='petg hatch tongue')
    lt = lv('latch_tab_m')
    ha.box((G['x_hatch1'], -lt[1] / 2, ztop), (G['x_hatch1'] + lt[0], lt[1] / 2, ztop + 0.001), name='petg latch tab')
    ha.prism('Z', zh - 0.004, [_circle(ax, ay, aod / 2), _circle(ax, ay, abore / 2, 8)], ztube - (zh - 0.004), name='petg antenna tube')

    # ---------------------------------------------------------------- POD-004 pack straps (2) + EVA pads
    st = ctx.part('POD-004')
    ztop_pack = zp + pk[2]
    for xc in G['strap_x']:
        ring = [_rect(-yo, zf - ts, yo, ztop_pack + ts), _rect(-yo + ts, zf, yo - ts, ztop_pack)]
        st.prism('X', xc - ws / 2, ring, ws, name='strap')
    pl = lv('pad_len_m')
    for xc in G['strap_x']:
        st.box((xc - pl / 2, -(bw / 2 - 0.002), zt), (xc + pl / 2, bw / 2 - 0.002, zp), name='eva pad')

    # ---------------------------------------------------------------- R5 (CR-A5-27): the trim kit is three single-material parts, so
    # each declared CG is both the mass centroid and the body centroid. POD-009 crush block, POD-010 spreader, POD-008 aft
    # spacers (nominal 550 g pack: one 8 mm blue spacer)
    gw, gd = lv('block_groove_m')
    sec = _notched(-bw / 2 + 0.0003, bw / 2 - 0.0003, zt, zh - 0.0005, gw, gd)
    ctx.part('POD-009').prism('X', x_fs, [sec], G['block_nom'], name='xps crush block')
    ctx.part('POD-010').prism('X', x_fs + G['block_nom'], [sec], G['sp_t'], name='petg spreader')
    tk = ctx.part('POD-008')
    hsp, bar = lv('spacer_h_m'), lv('spacer_bar_m')
    ya = bw / 2 - 0.001
    xcur = G['pack_aft_nom']
    for t in lv('spacer_flown_m'):
        uu = [(-ya, zp), (ya, zp), (ya, zp + hsp), (ya - bar, zp + hsp), (ya - bar, zp + bar * 0.6),
              (-ya + bar, zp + bar * 0.6), (-ya + bar, zp + hsp), (-ya, zp + hsp)]
        tk.prism('X', xcur, uu, t, name='petgb spacer %.0f mm' % (t * 1000))
        xcur += t

    # ---------------------------------------------------------------- POD-006 pitot socket with flange (printed, through the nose wall)
    so = ctx.part('POD-006')
    sx0, sx1 = G['socket_x']
    rbo = lv('socket_m')[1] / 2                         # R4 (CR-F3-12 d): bore keyed by a flat on +z, 5.8 mm across
    zk = pz - rbo + lv('pitot_key_flat_m')
    ak = math.asin((zk - pz) / rbo)                     # D-shaped bore: arc below the flat, then the flat
    bore = [(py + rbo * math.cos(ak + (math.pi - 2 * ak) + (math.pi + 2 * ak) * i / 14),
             pz + rbo * math.sin(ak + (math.pi - 2 * ak) + (math.pi + 2 * ak) * i / 14)) for i in range(15)]
    so.prism('X', sx0, [_rect(py - sq, pz - sq, py + sq, pz + sq), bore], sx1 - sx0, name='petgb pitot socket')
    fl, ft = lv('flange_m')
    so.prism('X', xn, [_rect(py - fl / 2, pz - fl / 2, py + fl / 2, pz + fl / 2), _rect(py - sq, pz - sq, py + sq, pz + sq)], ft,
             name='petg socket flange')

    # ---------------------------------------------------------------- POD-007 carry handle on the spar: feet, bridge + aft stop + gussets, legs, grip, mast socket
    hd = ctx.part('POD-007')
    xf0, xf1 = G['xf']
    fy0, fy1 = lv('foot_y_m')
    ty0, ty1 = lv('tongue_y_m')
    xt1 = min(G['x_slot_a'], xf1)
    arc = []
    for i in range(25):
        x = G['x_slot_f'] + (xt1 - G['x_slot_f']) * i / 24
        d = x - xs
        zc = zs + math.sqrt(max(rs * rs - d * d, 0.0))
        arc.append((x, max(zc, G['z_cheek'])))
    tongue = [(G['x_slot_f'], G['z_aft'])] + arc + [(xt1, G['z_aft'])]
    for s in (1, -1):
        ylo, yhi = (fy0, fy1) if s > 0 else (-fy1, -fy0)
        tlo, thi = (ty0, ty1) if s > 0 else (-ty1, -ty0)
        hd.box((xf0, ylo, G['z_aft']), (xf1, yhi, G['zfoot']), name='petgb foot plate')
        hd.prism('Y', tlo, tongue, thi - tlo, name='petgb saddle tongue')
        sq_leg = [_rect(xs - lg / 2, s * ly - lg / 2, xs + lg / 2, s * ly + lg / 2), _circle(xs, s * ly, lv('leg_m')[1] / 2, 8)]
        if s < 0:                                       # left leg: carries nothing (CR-F2-03 e)
            hd.prism('Z', G['zfoot'], sq_leg, G['z_grip0'] - G['zfoot'], name='petg leg')
            continue
        # right leg: the GPS cable enters a window on the outboard face at z ~0.06 and leaves at the top, inboard,
        # into the groove under the grip
        w0, w1 = lv('leg_window_m')
        t0 = G['z_grip0'] - 0.012
        rb = lv('leg_m')[1] / 2
        for z0_, z1_, op in ((G['zfoot'], w0, None), (w0, w1, 1), (w1, t0, None), (t0, G['z_grip0'], -1)):
            loops = sq_leg if op is None else [_keyhole(xs, ly, lg / 2, rb, op)]
            hd.prism('Z', z0_, loops, z1_ - z0_, name='petg leg')
    # R5: the aft stop moved to the tray (x 0.056); the bridge stays as the tie between the two feet, on the slot fill
    hd.box((lv('bridge_x0_m'), -fy0, G['z_aft']), (xf1, fy0, G['zfoot']), name='petg foot bridge')
    gx, gz = lv('grip_m')
    sb = lv('socket_boss_m')
    gb = lv('grip_bore_m')                              # R4: GPS cable groove under the grip, right leg -> mast socket
    gz0, gz1 = G['z_grip0'], G['z_grip1']
    grip_sec = [(xs - gx / 2, gz0), (xs - gb / 2, gz0), (xs - gb / 2, gz0 + 0.003), (xs + gb / 2, gz0 + 0.003),
                (xs + gb / 2, gz0), (xs + gx / 2, gz0), (xs + gx / 2, gz1), (xs - gx / 2, gz1)]
    yc0 = sb[2] / 2                                     # centre block under the socket: hole up into the mast bore
    hd.prism('Y', -ly - lg / 2, [(xs - gx / 2, gz0), (xs + gx / 2, gz0), (xs + gx / 2, gz1), (xs - gx / 2, gz1)],
             ly + lg / 2 - yc0, name='petgb grip')
    hd.prism('Z', gz0, [_rect(xs - gx / 2, -yc0, xs + gx / 2, yc0), _circle(xs, 0.0, gb / 2, 8)], gz1 - gz0, name='petgb grip')
    hd.prism('Y', yc0, grip_sec, ly - lg / 2 - yc0, name='petgb grip')
    hd.box((xs - gx / 2, ly - lg / 2, gz0), (xs + gx / 2, ly + lg / 2, gz1), name='petgb grip')
    hd.prism('Z', G['z_grip1'], [_rect(xs - sb[0] / 2, -sb[0] / 2, xs + sb[0] / 2, sb[0] / 2),
                                 _rect(xs - sb[2] / 2, -sb[2] / 2, xs + sb[2] / 2, sb[2] / 2)], sb[1], name='petg mast socket')

    # ---------------------------------------------------------------- POD-005 GPS mast with the 45 deg pad (plugs into the grip socket)
    ma = ctx.part('POD-005')
    ms = lv('mast_m')
    ma.prism('Z', G['z_grip1'], [_rect(xs - ms[0] / 2, -ms[0] / 2, xs + ms[0] / 2, ms[0] / 2),
                                 _rect(xs - ms[1] / 2, -ms[1] / 2, xs + ms[1] / 2, ms[1] / 2)], ms[2], name='petg mast')
    gp, gpt, ct = lv('gps_plate_m')
    A, B, C, nrm, h, zb0 = G['gps_wedge']
    for yy in (-ms[0] / 2, ms[0] / 2 - ct):             # cheeks stand on the mast top faces
        ma.prism('Y', yy, [A, B, C], ct, name='petg GPS cheek')
    pad = [A, C, (C[0] + nrm[0] * gpt, C[1] + nrm[1] * gpt), (A[0] + nrm[0] * gpt, A[1] + nrm[1] * gpt)]
    ma.prism('Y', -gp / 2, pad, gp, name='petg GPS pad 45 deg')

    # ---------------------------------------------------------------- joints (interfaces.json edges owned by pod)
    ctx.contact('E-POD-01', 'shell floor, LE filler and side walls bonded to bare foam in the pod recess (tape skin off)')
    ctx.contact('E-POD-02', 'tray and plates epoxied full-area to the foam-board floor')
    ctx.contact('E-POD-03', 'hatch tongue under the nose lip + hook-and-loop tab on the aft deck')
    ctx.contact('E-POD-04', 'straps through the tray slots, under the tray in a floor groove')
    ctx.contact('E-POD-05', 'pack strapped on the pads between the guides; crush block ahead, spacers and aft stop behind')
    ctx.rigid('E-POD-06', 'POD-005', 'POD-007', at=(xs, 0.0, G['z_grip1'] + sb[1] / 2))
    ctx.contact('E-POD-07', 'pitot socket through the nose wall, flange bonded to its inside face')
    ctx.contact('E-POD-08', 'handle legs bonded in the aft-deck slots')
    ctx.contact('E-POD-09', 'handle feet and stop bridge bonded on the spar / slot fill, one tie each round foot + spar')
    ctx.contact('E-POD-10', 'aft spacers trapped between the pack and the aft stop on the tray')
    ctx.contact('E-POD-11', 'crush block against the forward stop, between the guides')
    ctx.contact('E-POD-12', 'pack on the EVA pads on the tray: insulating thermal contact (E3); heat leaves by the pod air and vents')
    ctx.contact('E-POD-13', 'spreader trapped between the crush block and the pack fore face')
