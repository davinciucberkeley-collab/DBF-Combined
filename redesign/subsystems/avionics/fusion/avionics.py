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
                 tube A), the two pitot lines from the sensor ports up to the couplers on the probe root barbs
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

    # microSD in the FC's fore-edge slot, standing proud by sd_proud_m
    sl, sw, sh = a('sd_m')
    pr = a('sd_proud_m')
    x0 = g['fc_lo'][0] - pr
    g['sd_lo'] = (x0, cy - sw / 2, g['fc_lo'][2] + 0.001)
    g['sd_hi'] = (x0 + sl, cy + sw / 2, g['fc_lo'][2] + 0.001 + sh)

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
    bd, bln = a('barb_m')
    dy = a('aspd_port_m')[1]
    g['barbs'] = [((sx1, ya + s * dy / 2, za), bd / 2, bln) for s in (-1, 1)]
    g['coupler_x'] = sx1 + bln                             # couplers sit on the barb ends
    g['tip_on_axis'] = (abs(tip[1] - ya), abs(tip[2] - za))

    # the two pitot lines: up from the sensor ports to coupler height, then forward to the couplers
    tod = a('tube_m')[0]
    pxp = g['aspd_lo'][0] + a('aspd_port_m')[0]
    g['tubes'] = []
    for s in (-1, 1):
        yy = -cy + s * dy / 2
        g['tubes'].append({'riser': ((pxp, yy, g['aspd_hi'][2]), za - g['aspd_hi'][2]),
                           'run': ((pxp, yy, za), g['coupler_x'] - pxp), 'r': tod / 2})
    g['tube_path'] = (za - g['aspd_hi'][2]) + abs(g['coupler_x'] - pxp)

    # RX crosswise behind the aft tie post, under antenna tube A
    rl, rw, rh = a('rx_m')
    post_aft = ax0 + dx1 + pw / 2
    rx0 = post_aft + a('rx_gap_m')
    g['rx_lo'] = (rx0, -cy - rw / 2, zplate + tape)
    g['rx_hi'] = (rx0 + rl, -cy + rw / 2, zplate + tape + rh)
    g['rx_overhang'] = max(0.0, g['rx_hi'][0] - p('avn_plate_x_m')[1])
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
    fc.box(g['fc_lo'], g['fc_hi'], name='FC board envelope')

    # ---------------------------------------------------------------- AVN-006 isolation and retention set: four gel cubes (body)
    iso = ctx.part('AVN-006')
    for lo, hi in g['pads']:
        iso.box(lo, hi, name='gel cube')

    # ---------------------------------------------------------------- AVN-007 microSD in the FC slot
    sd = ctx.part('AVN-007')
    sd.box(g['sd_lo'], g['sd_hi'], name='microSD')

    # ---------------------------------------------------------------- AVN-004 airspeed board + its two silicone lines
    asp = ctx.part('AVN-004')
    asp.box(g['aspd_lo'], g['aspd_hi'], name='MS4525DO board envelope')
    for tb in g['tubes']:
        (p0, L0), r = tb['riser'], tb['r']
        asp.cylinder('Z', p0, L0, r, name='silicone line riser')
        p1, L1 = tb['run']
        asp.cylinder('X', p1, L1, r, name='silicone line run')

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
        bm.cylinder('X', start, ln, r, name='probe root barb + coupler')

    # ---------------------------------------------------------------- AVN-003 receiver (crosswise, under antenna tube A)
    rx = ctx.part('AVN-003')
    rx.box(g['rx_lo'], g['rx_hi'], name='RP3 V2 envelope')

    # ---------------------------------------------------------------- AVN-002 GPS + compass on the 45 deg pad
    gps = ctx.part('AVN-002')
    gps.prism('Y', -g['gps_w'] / 2, [g['gps_loop']], g['gps_w'], name='M100-5883 envelope 45 deg')

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
