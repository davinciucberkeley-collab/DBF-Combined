"""K09-L avionics (F3, revision F3-R2 on params A1-R3): flight controller on four gel pads, GPS + compass on the 45 deg
mast pad, ELRS receiver, MS4525DO airspeed sensor with its two pitot lines, plug-in pitot boom, microSD, and the
isolation/retention set. Telemetry runs over the ELRS link (no separate radio, no part).

Frame and datums: redesign/fusion/DATUMS.md (x aft, y right, z up, cruise attitude, metres).
Every station is read from the pod as D2 built it: `subsystems/pod/fusion/pod.py#layout()` (imported by path, a pure
function) and `subsystems/pod/params.json`, plus the avionics-local `subsystems/avionics/params.json`. `layout()` here
is a pure function too; team/F3/avn_data.py imports it for masses, CGs, interfaces.json and the claims, so the CAD,
the roll-up and the claims cannot disagree.

Arrangement (SPEC.md):
  right channel  FC top board, arrow -x, on 4 gel cubes on D2's FC plate between D2's end stops
  left channel   airspeed board between D2's tie posts (ports up), RX crosswise behind the aft post (under antenna
                 tube A), the two pitot lines from the sensor ports up to the probe root barbs (pushed on)
  nose           pitot boom: bought pitot-static probe bonded in a printed keyed sleeve, shoulder on the socket collar
  mast           GPS on 1 mm foam tape on the 45 deg pad, arrow toward the nose (down-forward along the pad)

Bought parts are envelopes plus their mounting face (STANDARDS section 3). Tape, ties and the FC strap have no body;
their mass is in AVN-006, whose body is the four gel cubes (they carry the FC).
UNVERIFIED-IN-FUSION: the GPS body is a Y-normal prism with a 45 deg rotated rectangle; the keyed sleeve is an
X-normal prism with a D-shaped loop and a round hole; no booleans.
"""
import importlib.util
import json
import math
import os


def _lv(L, key):
    d = L[key]
    return d['value'] if isinstance(d, dict) and 'value' in d else d


def _rect(u0, v0, u1, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def _circle(cu, cv, r, n=16):
    return [(cu + r * math.cos(2 * math.pi * i / n), cv + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _d_shape(cu, cv, r, flat, n=24):
    """(u, v) loop of a circle radius r with a flat at v = cv + flat (key flat on +v)."""
    a0 = math.asin(min(1.0, flat / r))
    span = math.pi + 2 * a0                    # arc below the flat
    return [(cu + r * math.cos(a0 - span * i / n), cv + r * math.sin(a0 - span * i / n)) for i in range(n + 1)]


def pod_geometry(get, sub_dir):
    """Pod layout G and pod-local params L, from D2's module and params (sibling folder)."""
    pod_dir = os.path.join(os.path.dirname(os.path.abspath(sub_dir)), 'pod')
    spec = importlib.util.spec_from_file_location('dbf_pod_layout_for_avionics', os.path.join(pod_dir, 'fusion', 'pod.py'))
    pod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pod)
    with open(os.path.join(pod_dir, 'params.json'), encoding='utf-8') as f:
        L = json.load(f)
    return pod, L


def gh_side(m, n, axis, s, face, yc, z0):
    """JST-GH side-entry header (SMnB-GHS-TB) on a board edge with its mated plug (GHR-nV-S) overhanging the edge.
    axis 'x': the edge is the face x = `face`, outward direction s (+1 / -1); yc: centre along the edge; z0: top of
    the board the header stands on. Returns header box, plug box (lo, hi) and the cable entry (point on the plug's rear
    face, unit direction OUT of the plug). Sizes: gh_side_m (JST GH catalogue pp. 27, 29)."""
    bh = m['hdr_b0'] + m['pitch'] * (n - 1)
    bp = m['plug_b0'] + m['pitch'] * (n - 1)
    zc = z0 + m['hdr_h'] / 2
    xh = sorted((face, face - s * m['hdr_d']))
    xp = sorted((face, face + s * m['plug_over']))
    hdr = ((xh[0], yc - bh / 2, z0), (xh[1], yc + bh / 2, z0 + m['hdr_h']))
    plug = ((xp[0], yc - bp / 2, zc - m['plug_t'] / 2), (xp[1], yc + bp / 2, zc + m['plug_t'] / 2))
    return {'hdr': hdr, 'plug': plug, 'entry': ((face + s * m['plug_over'], yc, zc), (s, 0.0, 0.0)), 'n': n}


def layout(get, A, L, G):
    """All avionics geometry (m). get: params getter; A: avionics params; L: pod params; G: pod.layout()."""
    a = lambda k: _lv(A, k)
    p = lambda k: _lv(L, k)
    g = {}
    zplate = G['zf'] + p('plate_t_m')                      # top of D2's FC and avionics plates
    ci, co, cy = G['ch_y']                                 # side channel inner |y|, outer |y|, centre |y|
    g['zplate'], g['cy'] = zplate, cy
    tape = a('tape_t_m')

    # FC on four gel cubes, right channel, centred on D2's FC plate
    bl, bw, bh = a('fc_board_m')
    px, py_, pt = a('pad_m')
    fx = p('fc_centre_x_m')
    g['fc_lo'] = (fx - bl / 2, cy - bw / 2, zplate + pt)
    g['fc_hi'] = (fx + bl / 2, cy + bw / 2, zplate + pt + bh)
    ins = a('pad_inset_m')
    g['pads'] = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            cxp = fx + sx * (bl / 2 - ins - px / 2)
            cyp = cy + sy * (bw / 2 - ins - py_ / 2)
            g['pads'].append(((cxp - px / 2, cyp - py_ / 2, zplate), (cxp + px / 2, cyp + py_ / 2, zplate + pt)))
    st_t = p('fc_stop_m')[0]
    g['fc_stop_clear'] = (fx + bl / 2 + 0.002) - g['fc_hi'][0]          # D2's stops are 2 mm clear of the board ends
    g['fc_in_channel'] = (cy - bw / 2 >= ci, cy + bw / 2 <= co, st_t)

    # D-89: the FC as its PCB + a component envelope set back from the two connector strips (aft: output field and
    # GPS socket; fore: SERIAL6 socket), so every lead lands on something real (fc_pcb_t_m, fc_strip_m: EST)
    pcb_t = a('fc_pcb_t_m')
    s_aft, s_fore = a('fc_strip_m')
    zt = g['fc_lo'][2] + pcb_t                             # PCB top
    g['fc_pcb_top'] = zt
    g['fc_pcb'] = (g['fc_lo'], (g['fc_hi'][0], g['fc_hi'][1], zt))
    g['fc_comp'] = ((g['fc_lo'][0] + s_fore, g['fc_lo'][1], zt), (g['fc_hi'][0] - s_aft, g['fc_hi'][1], g['fc_hi'][2]))
    of = a('fc_out_field')
    g['fc_holes'] = {}                                     # (output n, row 'S' / 'V' / 'G') -> hole centre on the PCB top
    for n, used in enumerate(of['used'], start=1):
        yn = of['y_out5'] + of['pitch'] * (n - 5)
        for k, row in enumerate('SVG'):
            if row in used:
                g['fc_holes'][(n, row)] = (g['fc_hi'][0] - of['row_in'] - k * of['pitch'], yn, zt)
    g['fc_joint'] = (of['joint_d'], of['joint_h'])
    gh = a('gh_side_m')
    fp = a('fc_ports')
    g['gh'] = {'GPS': gh_side(gh, 6, 'x', +1, g['fc_hi'][0], fp['gps_y'], zt),       # aft edge, cable leaves +x
               'RX': gh_side(gh, 4, 'x', -1, g['fc_lo'][0], fp['rx_y'], zt)}         # fore edge, cable leaves -x
    lk = a('fc_link_m')
    g['fc_link'] = ((lk['x'][0], lk['y'][0], g['fc_lo'][2] - lk['h']), (lk['x'][1], lk['y'][1], g['fc_lo'][2]))

    # microSD in the FC's fore-edge slot (on the PCB top), standing proud by sd_proud_m
    sl, sw, sh = a('sd_m')
    pr = a('sd_proud_m')
    x0 = g['fc_lo'][0] - pr
    g['sd_lo'] = (x0, cy - sw / 2, zt)
    g['sd_hi'] = (x0 + sl, cy + sw / 2, zt + sh)

    # airspeed board between D2's tie posts (left channel), ports up
    ax0 = p('avn_plate_x_m')[0]
    dx0, dx1 = a('aspd_post_dx_m')
    pw = p('tie_post_m')[0]
    post_in0, post_in1 = ax0 + dx0 + pw / 2, ax0 + dx1 - pw / 2       # inner faces of the two posts
    al, aw, ah = a('aspd_m')
    axc = (post_in0 + post_in1) / 2
    g['post_gap'] = post_in1 - post_in0
    g['aspd_lo'] = (axc - al / 2, -cy - aw / 2, zplate + tape)
    g['aspd_hi'] = (axc + al / 2, -cy + aw / 2, zplate + tape + ah)
    # D-89: its GH-4 socket on the aft face, the mated plug standing out aft above the tie post (aspd_gh_z, EST)
    zb = a('aspd_gh_z')
    g['gh']['ASPD'] = gh_side(gh, 4, 'x', +1, g['aspd_hi'][0], -cy, zb + gh['plug_t'] / 2 - gh['hdr_h'] / 2)

    # pitot boom: probe tip at params avionics.pitot_tip_xyz_m, on the pod socket axis
    tip = get('avionics.pitot_tip_xyz_m', 'm')
    ya, za = G['pitot_axis']
    sx0, sx1 = G['socket_x']                               # socket collar front face, socket inner end
    od, flat, ahead = a('sleeve_m')
    sho, shl = a('shoulder_m')
    g['tip'] = tuple(tip)
    g['axis'] = (ya, za)
    g['sleeve_x'] = (sx0 - shl - ahead, sx1)               # from ahead of the shoulder to the socket inner end
    g['shoulder_x'] = (sx0 - shl, sx0)
    g['sleeve_od'], g['sleeve_flat'], g['shoulder_od'] = od, flat, sho
    g['probe_x'] = (tip[0], sx1)
    g['probe_r'] = a('probe_od_m') / 2
    bd, bln = a('barb_m')[:2]
    dy = a('aspd_port_m')[1]
    dyb = a('barb_m')[2] if len(a('barb_m')) > 2 else dy  # D-89b: barb spacing (fits the socket bore)
    g['barb_r'] = bd / 2
    g['port_h'] = a('aspd_port_m')[2] if len(a('aspd_port_m')) > 2 else 0.0
    g['barbs'] = [((sx1, ya + s * dyb / 2, za), bd / 2, bln) for s in (-1, 1)]
    g['coupler_x'] = sx1 + bln                             # the barb ends (the lines are pushed on; no couplers)
    g['tip_on_axis'] = (abs(tip[1] - ya), abs(tip[2] - za))

    # the two pitot lines: up from the sensor ports to coupler height, then forward to the couplers
    tod = a('tube_m')[0]
    pxp = g['aspd_lo'][0] + a('aspd_port_m')[0]
    g['tubes'] = []
    for s in (-1, 1):
        yy = -cy + s * dy / 2
        g['tubes'].append({'riser': ((pxp, yy, g['aspd_hi'][2]), za - g['aspd_hi'][2]),
                           'run': ((pxp, ya + s * dyb / 2, za), g['coupler_x'] - pxp), 'r': tod / 2})
        #   D-89: the run on its barb's line (probe axis y), so the line's end slides straight over the barb
    g['tube_path'] = (za - g['aspd_hi'][2]) + abs(g['coupler_x'] - pxp)
    g['tube_id'] = a('tube_m')[1]

    # RX crosswise behind the aft tie post, under antenna tube A
    rl, rw, rh = a('rx_m')
    post_aft = ax0 + dx1 + pw / 2
    rx0 = post_aft + a('rx_gap_m')
    g['rx_lo'] = (rx0, -cy - rw / 2, zplate + tape)
    g['rx_hi'] = (rx0 + rl, -cy + rw / 2, zplate + tape + rh)
    g['rx_overhang'] = max(0.0, g['rx_hi'][0] - p('avn_plate_x_m')[1])
    rp = a('rx_pads')                                      # D-89: 5 V, GND, TX, RX solder pads on the RX top (EST)
    g['rx_pads'] = [((rp['x0'] + i * rp['pitch'] - 0.0006, rp['y'][0], g['rx_hi'][2]),
                     (rp['x0'] + i * rp['pitch'] + 0.0006, rp['y'][1], g['rx_hi'][2] + rp['t'])) for i in range(4)]
    g['ant_a_xy'] = tuple(p('ant_tube_xy_m'))

    # GPS on the 45 deg pad (pad from D2: A -> C line, normal n, thickness gpt)
    A0, _B, C0, n, _h, _zb0 = G['gps_wedge']
    gpt = p('gps_plate_m')[1]
    gl, gw, gh = a('gps_m')
    t = ((C0[0] - A0[0]), (C0[1] - A0[1]))
    tl = math.hypot(*t)
    t = (t[0] / tl, t[1] / tl)
    mid = ((A0[0] + C0[0]) / 2 + n[0] * gpt, (A0[1] + C0[1]) / 2 + n[1] * gpt)
    c = (mid[0] + n[0] * (tape + gh / 2), mid[1] + n[1] * (tape + gh / 2))
    g['gps_c'] = (c[0], 0.0, c[1])
    g['gps_loop'] = [(c[0] + su * t[0] * gl / 2 + sv * n[0] * gh / 2, c[1] + su * t[1] * gl / 2 + sv * n[1] * gh / 2)
                     for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    g['gps_w'] = gw
    g['gps_on_pad'] = (gl <= p('gps_plate_m')[0], gw <= p('gps_plate_m')[0])
    g['gps_arrow'] = (-t[0], 0.0, -t[1])                   # forward and down along the pad: points at the nose
    g['gps_tilt_deg'] = math.degrees(math.atan2(-n[0], n[1]))
    # D-89: GH-6 plug on the module's aft-upper end face (+t end), standing out along +t; cable leaves it along +t
    gg, ghm = a('gps_gh_m'), a('gh_side_m')
    v0 = (gg['v'] - 0.5) * gh                              # across the module height (n), from its centre
    u0, u1 = gl / 2, gl / 2 + ghm['plug_over']             # along t: from the end face out
    pt_ = ghm['plug_t']
    g['gps_plug_loop'] = [(c[0] + su * t[0] + sv * n[0], c[1] + su * t[1] + sv * n[1])
                          for su, sv in ((u0, v0 - pt_ / 2), (u1, v0 - pt_ / 2), (u1, v0 + pt_ / 2), (u0, v0 + pt_ / 2))]
    g['gps_plug_w'] = ghm['plug_b0'] + ghm['pitch'] * 5    # GHR-06V-S: B = 8.75 mm
    g['gps_plug_entry'] = ((c[0] + u1 * t[0] + v0 * n[0], 0.0, c[1] + u1 * t[1] + v0 * n[1]), (t[0], 0.0, t[1]))
    # connector ends for F2 (harness): FC GPS port aft edge, FC fore edge, GPS aft edge, RX aft edge, airspeed side
    g['ports'] = {
        'FC aft edge (GPS SERIAL5+I2C, outputs, servo rail)': (g['fc_hi'][0] - 0.002, cy, g['fc_lo'][2] + 0.004),
        'FC fore edge (SERIAL6 RX, power-board link)': (g['fc_lo'][0] + 0.002, cy, g['fc_lo'][2] + 0.004),
        'GPS connector (aft-upper edge of the module)': (c[0] + t[0] * gl / 2 * 0.8, 0.0, c[1] + t[1] * gl / 2 * 0.8),
        'RX pads (aft edge)': (g['rx_hi'][0] - 0.002, -cy, g['rx_hi'][2] - 0.001),
        'Airspeed JST-GH (aft edge)': (g['aspd_hi'][0] - 0.002, -cy, g['aspd_lo'][2] + 0.004),
    }
    return g


def build(ctx):
    v, A = ctx.value, ctx.local
    pod, L = pod_geometry(v, ctx.dir)
    import k09kit as k9
    coords, _src = k9.section(ctx)
    G = pod.layout(v, L, coords)
    g = layout(v, A, L, G)
    ya, za = g['axis']

    # ---------------------------------------------------------------- AVN-001 flight controller (envelope, arrow -x)
    fc = ctx.part('AVN-001')
    # D-89: PCB + component envelope; the leads land on solder joints and GH plugs on the PCB strips (no lead may end
    # in a bare envelope)
    fc.box(*g['fc_pcb'], name='FC PCB')
    fc.box(*g['fc_comp'], name='FC component envelope')
    jd, jh = g['fc_joint']
    for (n, row), (x, y, z) in sorted(g['fc_holes'].items()):
        fc.cylinder('Z', (x, y, z), jh, jd / 2, name='output %d %s solder joint' % (n, row))
    for port, s in sorted(g['gh'].items()):
        if port == 'ASPD':
            continue
        fc.box(*s['hdr'], name='JST-GH %d header (%s)' % (s['n'], port))
        fc.box(*s['plug'], name='JST-GH %d plug, mated (%s)' % (s['n'], port))
    fc.box(*g['fc_link'], name='board-link 2 x 5 header + ribbon plug (W-PMOD)')

    # ---------------------------------------------------------------- AVN-006 isolation and retention set: four gel cubes (body)
    iso = ctx.part('AVN-006')
    for lo, hi in g['pads']:
        iso.box(lo, hi, name='gel cube')

    # ---------------------------------------------------------------- AVN-007 microSD in the FC slot
    sd = ctx.part('AVN-007')
    sd.box(g['sd_lo'], g['sd_hi'], name='microSD')

    # ---------------------------------------------------------------- AVN-004 airspeed board + its two silicone lines
    asp = ctx.part('AVN-004')
    # D-89: the body below the two port nipples; each silicone line is pushed over its nipple (hollow end) and over
    # its probe-root barb (hollow end, 5 mm), so neither line ends flat against a box or a barb
    ph, rid = g['port_h'], g['tube_id'] / 2 + 0.00002
    zb = g['aspd_hi'][2] - ph
    asp.box(g['aspd_lo'], (g['aspd_hi'][0], g['aspd_hi'][1], zb), name='MS4525DO board envelope')
    asp.box(*g['gh']['ASPD']['plug'], name='JST-GH 4 plug, mated (I2C)')        # D-89: header inside the envelope
    for tb in g['tubes']:
        (p0, L0), r = tb['riser'], tb['r']
        x, y, _z = p0
        asp.cylinder('Z', (x, y, zb), ph, g['tube_id'] / 2, name='port nipple')
        asp.tube('Z', (x, y, zb + 0.0005), ph - 0.001, r, rid, name='silicone line end on the nipple')
        asp.cylinder('Z', (x, y, zb + ph - 0.0005), L0 + 0.0005, r, name='silicone line riser')
        p1, L1 = tb['run']
        asp.cylinder('X', p1, L1, r, name='silicone line run')
        asp.tube('X', (p1[0] + L1, p1[1], p1[2]), -0.005, r, g['barb_r'] + 0.00002,
                 name='silicone line end on the barb (stretched)')

    # ---------------------------------------------------------------- AVN-005 pitot boom: keyed sleeve + shoulder + probe + root barbs
    bm = ctx.part('AVN-005')
    s0, s1 = g['sleeve_x']
    r_out, flat = g['sleeve_od'] / 2, g['sleeve_flat'] - g['sleeve_od'] / 2
    bm.prism('X', s0, [_d_shape(ya, za, r_out, flat), _circle(ya, za, g['probe_r'] + 0.00005, 12)], s1 - s0, name='petg keyed sleeve')
    h0, h1 = g['shoulder_x']
    bm.prism('X', h0, [_circle(ya, za, g['shoulder_od'] / 2), _d_shape(ya, za, r_out, flat)], h1 - h0,
             name='petg shoulder')
    p0, p1 = g['probe_x']
    bm.cylinder('X', (p0, ya, za), p1 - p0, g['probe_r'], name='pitot-static probe')
    for (start, r, ln) in g['barbs']:
        bm.cylinder('X', start, ln, r, name='probe root barb')

    # ---------------------------------------------------------------- AVN-003 receiver (crosswise, under antenna tube A)
    rx = ctx.part('AVN-003')
    rx.box(g['rx_lo'], g['rx_hi'], name='RP3 V2 envelope')
    for i, (lo, hi) in enumerate(g['rx_pads']):             # D-89: the four solder pads with their joints
        rx.box(lo, hi, name='RX %s solder pad + joint' % ('5V', 'GND', 'TX', 'RX')[i])
    for ax, a0, a1, loop in lap_joints(ctx, 'AVN-003'):           # D-89: solder fillets over the conductor tips
        rx.prism(ax, a0, [loop], a1 - a0, name='lap solder joint')

    # ---------------------------------------------------------------- AVN-002 GPS + compass on the 45 deg pad
    gps = ctx.part('AVN-002')
    gps.prism('Y', -g['gps_w'] / 2, [g['gps_loop']], g['gps_w'], name='M100-5883 envelope 45 deg')
    gps.prism('Y', -g['gps_plug_w'] / 2, [g['gps_plug_loop']], g['gps_plug_w'], name='JST-GH 6 plug, mated (GPS)')

    # ---------------------------------------------------------------- joints (edges owned by avionics; none is fastened)
    ctx.contact('E-AVN-01', 'FC on 4 gel cubes on the FC plate between the end stops; 10 mm strap over the board with 1-2 mm slack')
    ctx.contact('E-AVN-02', 'GPS on 1 mm foam tape on the 45 deg mast pad, arrow toward the nose; cable tied to the mast')
    ctx.contact('E-AVN-03', 'RX on 1 mm foam tape on the avionics plate, crosswise behind the aft tie post')
    ctx.contact('E-AVN-04', 'airspeed board on 1 mm foam tape between the tie posts + 1 tie through the post slots')
    ctx.contact('E-AVN-05', 'keyed sleeve plugged into the pitot socket, shoulder on the collar; drag and hover gravity push it home')
    ctx.contact('E-AVN-06', 'two silicone lines from the sensor ports to the couplers on the probe root barbs (total, static)')
    ctx.contact('E-AVN-07', 'gel cubes stuck to the scuffed FC plate')
    ctx.contact('E-AVN-08', 'microSD in the FC card slot')
    ctx.contact('E-AVN-10', 'FC heat path: gel cubes (insulating) and vented pod air; board on its pads above the plate')


def lap_joints(ctx, part_id):
    """D-89: the solder fillets at the lap-soldered conductor ends on this part, as the harness router wrote them
    (subsystems/harness/params.json cad.lap_joints, team/F2/harness.py lap_joints): [(axis, a0, a1, loop)]."""
    import json as _json
    import os as _os
    p = _os.path.join(_os.path.dirname(_os.path.abspath(ctx.dir)), 'harness', 'params.json')
    if not _os.path.exists(p):
        return []
    with open(p, encoding='utf-8') as f:
        tab = _json.load(f).get('harness', {}).get('cad', {}).get('lap_joints', {}).get('value', [])
    return [(j['axis'], j['a'][0], j['a'][1], [tuple(q) for q in j['loop']]) for j in tab if j['part'] == part_id]
