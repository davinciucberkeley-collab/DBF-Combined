"""K09-L centre pod (D2): shell, tray, hatch, pack straps, GPS mast, pitot socket, carry handle, trim spacers.

Frame and datums: redesign/fusion/DATUMS.md (x aft, y right, z up, cruise attitude, metres).
Shared numbers from params.json (pod LE, length, height, base, board thickness, pack size, spar, pitot tip x/z);
pod-only numbers from subsystems/pod/params.json. `layout()` is a pure function of those numbers and the wing
section; team/D2/pod_data.py (masses, CGs, interfaces.json) and team/D2/pod_claims.py (proof chain) import it,
so the CAD, the mass roll-up and the claims cannot disagree.

Arrangement (SPEC.md): the pack bay runs down the middle on a printed tray; the nose wall is the forward stop and
a printed wall at the recess end is the aft stop; three printed spacers fill the 23 mm between them in front of
or behind the pack (aft-only trim). The FC sits in the right side channel, the airspeed sensor, RX and power
items in the left one, the pitot socket in the left channel at the nose. Aft of the bay a printed carry handle
stands on two feet that saddle the spar top and are tied round the spar: the carry point is on the spar
(CHANGE-LOG D-23); the GPS mast plugs into the handle grip.

UNVERIFIED-IN-FUSION: Y-normal prisms whose loops follow the S5010 upper surface (side walls, LE filler, saddle
tongues); prisms with many hole loops (tray, deck); none of it uses booleans.
Not modelled as bodies (STANDARDS section 3): fasteners, ties, glue, hook-and-loop, label, the 1 mm strap groove
cut in the foam floor; heat-set inserts are the boss bores.
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


def _surf(coords, c, x):
    return k9.surface_z(coords, c, x / c, 'upper')


def layout(get, L, coords):
    """All pod geometry (m) from params getter `get(key, unit)`, pod-local params `L` and the wing section."""
    g = {}
    lv = lambda k: _lv(L, k)
    c = get('wing.chord_m', 'm')
    x0 = get('pod.x_le_m', 'm')
    Lp, _w_shared, H = get('pod.size_m', 'm')
    zb = get('pod.z_base_m', 'm')
    W = lv('width_m')
    tb = get('fins.board_t_m', 'm')
    xs, zs = get('wing.spar.x_m', 'm'), get('wing.spar.z_m', 'm')
    rs = get('wing.spar.od_m', 'm') / 2
    pk = get('battery.size_m', 'm')
    g.update(x0=x0, x1=x0 + Lp, W=W, yi=W / 2 - tb, H=H, zb=zb, ztop=zb + H, tb=tb, xs=xs, zs=zs, rs=rs, chord=c,
             pack=pk, W_shared=_w_shared)
    g['xn'] = x0 + tb                                   # nose wall inner face = pack forward stop
    g['zh'] = g['ztop'] - tb                            # side-wall tops = hatch underside
    g['x_slot_f'], g['x_slot_a'] = xs - rs, xs + rs     # spar slot faces
    g['x_rec1'] = g['x_slot_f'] - lv('slot_wall_m')     # recess end
    lo, hi = 0.0, xs                                    # recess start: upper surface = pod base
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _surf(coords, c, mid) < zb else (lo, mid)
    g['x_rec0'] = (lo + hi) / 2
    g['zf'] = zb + tb                                   # foam floor top = tray underside
    g['zt'] = g['zf'] + lv('tray_floor_t_m')            # tray top
    g['zp'] = g['zt'] + lv('pad_t_m')                   # pack underside
    g['bw'] = lv('bay_min_m')[1]
    g['tg'], g['hg'] = lv('guide_t_m'), lv('guide_h_m')
    g['x_stop0'] = g['x_rec1'] - lv('stop_wall_t_m')    # aft stop face
    g['pack_fwd_c'] = g['xn'] + pk[0] / 2               # pack centroid at the forward stop
    g['pack_aft_face_fwd'] = g['xn'] + pk[0]
    g['travel'] = g['x_stop0'] - g['pack_aft_face_fwd']
    g['bay'] = (g['x_stop0'] - g['xn'], g['bw'], g['zh'] - g['zp'])
    g['pod_c'] = x0 + Lp / 2
    g['pack_z_c'] = g['zp'] + pk[2] / 2
    # aft region: wing surface under the feet / aft wall
    xa = [g['x_rec1'] + i * (g['x0'] + Lp - g['x_rec1']) / 8 for i in range(9)]
    g['aft_surf'] = [(x, _surf(coords, c, x)) for x in xa]
    g['z_aft'] = max(z for _, z in g['aft_surf'])
    g['xf'] = (g['x_slot_f'] - 0.002, g['x1'] - tb)     # handle foot x range (ends at the aft wall)
    g['zfoot'] = g['z_aft'] + lv('foot_plate_t_m')      # handle foot top
    g['z_cheek'] = zs + lv('tongue_cheek_frac') * rs
    g['x_hatch1'] = lv('hatch_aft_x_m')
    g['x_lip1'] = g['xn'] + lv('lip_m')[0]
    gg, gz = lv('grip_m')
    g['z_grip0'] = g['ztop'] + lv('grip_gap_m')
    g['z_grip1'] = g['z_grip0'] + gz
    sb = lv('socket_boss_m')
    g['z_sock1'] = g['z_grip1'] + sb[1]
    ms = lv('mast_m')
    g['z_mast1'] = g['z_grip1'] + ms[2]                 # mast top (inserted sb[1] into the socket)
    gp = lv('gps_plate_m')
    g['gps_c'] = (xs, 0.0, g['z_mast1'] + gp[1] + 0.004)
    py, pz = lv('pitot_y_m'), get('avionics.pitot_tip_xyz_m', 'm')[2]
    so = lv('socket_m')
    g['pitot_axis'] = (py, pz)
    g['socket_x'] = (x0 - so[3], g['xn'] + so[2])
    g['pitot_tip'] = (get('avionics.pitot_tip_xyz_m', 'm')[0], py, pz)
    g['boom_len'] = (g['socket_x'][1] - g['pitot_tip'][0])
    y_ch = (g['bw'] / 2 + g['tg'] + g['yi']) / 2
    g['ch_y'] = (g['bw'] / 2 + g['tg'], g['yi'], y_ch)  # side channel inner, outer, centre
    g['strap_x'] = [g['xn'] + s for s in lv('strap_from_front_m')]
    return g


def build(ctx):
    v, L = ctx.value, ctx.local
    lv = lambda k: _lv(L, k)
    coords, _src = k9.section(ctx)
    G = layout(v, L, coords)
    x0, x1, W, yi, tb = G['x0'], G['x1'], G['W'], G['yi'], G['tb']
    zb, ztop, zh, zf, zt, zp = G['zb'], G['ztop'], G['zh'], G['zf'], G['zt'], G['zp']
    xn, xr0, xr1, xst = G['xn'], G['x_rec0'], G['x_rec1'], G['x_stop0']
    bw, tg, hg = G['bw'], G['tg'], G['hg']
    xs, zs, rs = G['xs'], G['zs'], G['rs']
    pk = G['pack']
    c = G['chord']

    # ---------------------------------------------------------------- POD-001 shell (foam board + XPS filler + printed lip)
    sh = ctx.part('POD-001')
    sh.box((xn, -yi, zb), (xr1, yi, zf), name='fb floor')
    side = [(x0, zb), (xr1, zb)] + [(x, z) for x, z in G['aft_surf']] + [(x1, zh), (x0, zh)]
    sh.prism('Y', yi, side, tb, name='fb side wall R')
    sh.prism('Y', -W / 2, side, tb, name='fb side wall L')
    py, pz = G['pitot_axis']
    sq = lv('socket_m')[0] / 2
    sh.prism('X', x0, [_rect(-yi, zb, yi, ztop), _rect(py - sq, pz - sq, py + sq, pz + sq)], tb, name='fb nose wall')
    lip_l, lip_t = lv('lip_m')
    sh.box((xn, -yi + 0.02, ztop - lip_t), (G['x_lip1'], yi - 0.02, ztop), name='petg nose lip')
    n = 8
    filler = [(0.0, zb)] + [(xr0 * i / n, _surf(coords, c, xr0 * i / n)) for i in range(n + 1)]
    sh.prism('Y', -W / 2, filler, W, name='xps LE filler')
    ex = lv('cable_exit_m')
    aft_holes = [_rect(ex[0], ex[2], ex[1], ex[3]), _rect(-ex[1], ex[2], -ex[0], ex[3])]
    sh.prism('X', x1 - tb, [_rect(-yi, G['z_aft'], yi, ztop)] + aft_holes, tb, name='fb aft wall')
    lg, _lb = lv('leg_m')
    ly = lv('leg_y_m')
    h = lg / 2 + 0.0004
    deck = [_rect(G['x_hatch1'], -yi, x1 - tb, yi),
            _rect(xs - h, ly - h, xs + h, ly + h), _rect(xs - h, -ly - h, xs + h, -ly + h)]
    sh.prism('Z', zh, deck, tb, name='fb aft deck')

    # ---------------------------------------------------------------- POD-002 tray (printed PETG: bay tray, FC plate, avionics plate)
    tr = ctx.part('POD-002')
    sw, sl = lv('strap_slot_m')[1], lv('strap_slot_m')[0]
    ts, ws = lv('strap_t_m'), lv('strap_w_m')
    yo = bw / 2 - 0.0002                                # strap leg outer face, just inside the guide
    ys0 = yo - ts / 2                                   # slot centre under the strap leg
    slots = []
    for xc in G['strap_x']:
        for s in (1, -1):
            slots.append(_rect(xc - sl / 2, s * ys0 - sw / 2, xc + sl / 2, s * ys0 + sw / 2))
    wb, wy = lv('window_border_m')
    xs_cut = [xn] + [x for xc in G['strap_x'] for x in (xc - sl / 2, xc + sl / 2)] + [xst]
    wins = [_rect(a0 + wb, -(bw / 2 - wy), a1 - wb, bw / 2 - wy)
            for a0, a1 in zip(xs_cut[0::2], xs_cut[1::2]) if a1 - a0 > 2 * wb + 0.01]
    tray = [_rect(xn, -(bw / 2 + tg), xr1, bw / 2 + tg)] + slots + wins
    tr.prism('Z', zf, tray, lv('tray_floor_t_m'), name='petg bay floor')
    for s in (1, -1):
        y_in = s * bw / 2
        tr.box((xn, min(y_in, y_in + s * tg), zt), (xst, max(y_in, y_in + s * tg), zt + hg), name='petg guide')
    a = bw / 2 + tg
    nw, nz = lv('lead_notch_m')
    hs = lv('stop_wall_h_m')
    u = [(-a, zt), (a, zt), (a, zt + hs), (nw / 2, zt + hs), (nw / 2, zt + nz), (-nw / 2, zt + nz),
         (-nw / 2, zt + hs), (-a, zt + hs)]
    tr.prism('X', xst, u, lv('stop_wall_t_m'), name='petg aft stop')
    ci, co, cy = G['ch_y']
    tp = lv('plate_t_m')
    bd, bh = lv('boss_d_m'), lv('boss_h_m')
    fx, fl, fp = lv('fc_centre_x_m'), lv('fc_plate_len_m'), lv('fc_pattern_m')
    win = _rect(fx - fp / 2 + bd, cy - fp / 2 + bd, fx + fp / 2 - bd, cy + fp / 2 - bd)
    tr.prism('Z', zf, [_rect(fx - fl / 2, ci + 0.0005, fx + fl / 2, co - 0.0005), win], tp, name='petg FC plate')
    for dx in (-fp / 2, fp / 2):
        for dy in (-fp / 2, fp / 2):
            tr.prism('Z', zf + tp, [_circle(fx + dx, cy + dy, bd / 2), _circle(fx + dx, cy + dy, 0.002, 8)], bh,
                     name='petg FC boss')
    ax0, ax1 = lv('avn_plate_x_m')
    tr.prism('Z', zf, [_rect(ax0, -co + 0.0005, ax1, -ci - 0.0005)], tp, name='petg avionics plate')
    m2 = lv('m2_boss_pitch_m')
    for dx in (0.0, m2):
        bx = ax0 + 0.012 + dx
        tr.prism('Z', zf + tp, [_circle(bx, -cy, 0.0025), _circle(bx, -cy, 0.0008, 8)], 0.004, name='petg M2 boss')

    # ---------------------------------------------------------------- POD-003 hatch (foam board + printed tongue + latch tab)
    ha = ctx.part('POD-003')
    ha.box((G['x_lip1'], -W / 2, zh), (G['x_hatch1'], W / 2, ztop), name='fb hatch')
    ha.box((xn + 0.0005, -yi + 0.02, zh), (G['x_lip1'], yi - 0.02, zh + lv('tongue_t_m')), name='petg hatch tongue')
    lt = lv('latch_tab_m')
    ha.box((G['x_hatch1'], -lt[1] / 2, ztop), (G['x_hatch1'] + lt[0], lt[1] / 2, ztop + 0.001), name='petg latch tab')

    # ---------------------------------------------------------------- POD-004 pack straps (2) + anti-slip pad
    st = ctx.part('POD-004')
    ztop_pack = zp + pk[2]
    for xc in G['strap_x']:
        ring = [_rect(-yo, zf - ts, yo, ztop_pack + ts), _rect(-yo + ts, zf, yo - ts, ztop_pack)]
        st.prism('X', xc - ws / 2, ring, ws, name='strap')
    pl = lv('pad_len_m')
    for xc in G['strap_x']:
        st.box((xc - pl / 2, -(bw / 2 - 0.002), zt), (xc + pl / 2, bw / 2 - 0.002, zp), name='rub pad')

    # ---------------------------------------------------------------- POD-008 trim spacers (all behind the pack = forward stop)
    sp = ctx.part('POD-008')
    hsp, bar = lv('spacer_h_m'), lv('spacer_bar_m')
    ya = bw / 2 - 0.001
    xcur = G['pack_aft_face_fwd']
    for t in lv('spacer_set_m'):
        uu = [(-ya, zp), (ya, zp), (ya, zp + hsp), (ya - bar, zp + hsp), (ya - bar, zp + bar * 0.6),
              (-ya + bar, zp + bar * 0.6), (-ya + bar, zp + hsp), (-ya, zp + hsp)]
        sp.prism('X', xcur, uu, t, name='petgb spacer %.0f mm' % (t * 1000))
        xcur += t

    # ---------------------------------------------------------------- POD-006 pitot socket (printed, through the nose wall)
    so = ctx.part('POD-006')
    sx0, sx1 = G['socket_x']
    so.prism('X', sx0, [_rect(py - sq, pz - sq, py + sq, pz + sq), _circle(py, pz, lv('socket_m')[1] / 2)], sx1 - sx0,
             name='petgb pitot socket')

    # ---------------------------------------------------------------- POD-007 carry handle on the spar (feet, legs, grip, mast socket)
    hd = ctx.part('POD-007')
    xf0, xf1 = G['xf']
    fy0, fy1 = lv('foot_y_m')
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
        hd.box((xf0, ylo, G['z_aft']), (xf1, yhi, G['zfoot']), name='petgb foot plate')
        hd.prism('Y', ylo, tongue, yhi - ylo, name='petgb saddle tongue')
        hd.prism('Z', G['zfoot'], [_rect(xs - lg / 2, s * ly - lg / 2, xs + lg / 2, s * ly + lg / 2),
                                   _circle(xs, s * ly, lv('leg_m')[1] / 2, 8)], G['z_grip0'] - G['zfoot'], name='petg leg')
    gx, gz = lv('grip_m')
    hd.box((xs - gx / 2, -ly - lg / 2, G['z_grip0']), (xs + gx / 2, ly + lg / 2, G['z_grip1']), name='petgb grip')
    sb = lv('socket_boss_m')
    hd.prism('Z', G['z_grip1'], [_rect(xs - sb[0] / 2, -sb[0] / 2, xs + sb[0] / 2, sb[0] / 2),
                                 _rect(xs - sb[2] / 2, -sb[2] / 2, xs + sb[2] / 2, sb[2] / 2)], sb[1], name='petg mast socket')

    # ---------------------------------------------------------------- POD-005 GPS mast (plugs into the grip socket)
    ma = ctx.part('POD-005')
    ms = lv('mast_m')
    ma.prism('Z', G['z_grip1'], [_rect(xs - ms[0] / 2, -ms[0] / 2, xs + ms[0] / 2, ms[0] / 2),
                                 _rect(xs - ms[1] / 2, -ms[1] / 2, xs + ms[1] / 2, ms[1] / 2)], ms[2], name='petg mast')
    gp = lv('gps_plate_m')
    ma.box((xs - gp[0] / 2, -gp[0] / 2, G['z_mast1']), (xs + gp[0] / 2, gp[0] / 2, G['z_mast1'] + gp[1]), name='petg GPS plate')

    # ---------------------------------------------------------------- joints (interfaces.json edges owned by pod)
    ctx.contact('E-POD-01', 'shell floor, LE filler and side walls bonded to bare foam in the pod recess (tape skin off)')
    ctx.contact('E-POD-02', 'tray and plates bonded to the foam-board floor')
    ctx.contact('E-POD-03', 'hatch tongue under the nose lip + hook-and-loop tab on the aft deck')
    ctx.contact('E-POD-04', 'straps through the tray slots, under the tray in a floor groove')
    ctx.contact('E-POD-05', 'pack strapped on the pad between the guides; nose wall / spacers / aft stop fore-aft')
    ctx.rigid('E-POD-06', 'POD-005', 'POD-007', at=(xs, 0.0, G['z_grip1'] + sb[1] / 2))
    ctx.contact('E-POD-07', 'pitot socket bonded through the nose wall')
    ctx.contact('E-POD-08', 'handle legs bonded in the aft-deck slots')
    ctx.contact('E-POD-09', 'handle feet bonded on the spar top in the open slot, one tie each round foot + spar')
    ctx.contact('E-POD-10', 'spacers stand on the tray between the guides')
