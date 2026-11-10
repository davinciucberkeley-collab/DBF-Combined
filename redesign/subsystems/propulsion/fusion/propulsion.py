"""K09-L propulsion subsystem (PRP), owner E1. Four motor stations UR / UL / LR / LL on the fin mounts (D3).

    build(ctx)               Fusion / stub module (fusionkit), cruise attitude, aircraft frame (DATUMS.md)
    geometry(P, LP)          every derived dimension and the per-station placement (shared with make_propulsion.py)

Per station: PRP-001 motor SunnySky X3108S KV900 (envelope: base boss, bell, shaft stub, rear E-clip, lead exit),
PRP-004 bolt-on prop adapter (base with the 4 mm pilot bore, M6x1 post) with its washer and nut, PRP-003 APC
11x5.5MR/MRP (hub with the LPAR06E bore, two blades as twisted flat-plate lofts, parked spanwise), PRP-002 LANRC
45 A ESC (45 x 20 x 6 mm box) flat on the outboard face of D3's ASA pad FIN-007.

Cant (D-27, 7 deg tangential): the motor base sits flat on D3's canted plate. The motor, adapter and prop of a station
are one rigid stack, so each is its own component placed with ctx.part(at=motor point, rotate=(axis, 7 deg)): local
x' is the shaft axis (thrust toward -x'), the base face is the local plane x' = 0 through the motor point
(DP-MOTOR-FACE on the axis, k09kit.motor_face_x), which is D3's canted face. The rotation takes -x to the forward
normal of D3's plate at that station (fins.py geometry: face_x_at, mirrored per station), so the stack follows the
plate exactly; ctx.mirror cannot copy a rotated component, so the four stations are built one by one.

Prop plane: on the motor axis, base face + body 26.5 + adapter base 6.35 + hub 8.89 / 2 = 37.3 mm (E1's stack,
CL-E1-STACK-PROP-PLANE). Its x is -0.0062 m, not the datum DP-PROP -0.0082 (D-28 carried D3's 39 mm stack):
the keep-outs are registered on the modelled hubs; CR-E1-22 / CR-E1-29 settle the datum on the measured motor.

Joints registered here (interfaces.json, owner propulsion): E-PRP-01..04 adapter -> motor (rigid at the bell top),
E-PRP-05..08 prop -> adapter (rigid at the hub centre, field joint). Registered by fins (D3): E-FIN-61..64 motor ->
mount, E-FIN-65..68 ESC -> pad. By harness (F2): E-HRN-17..20 phase leads ESC -> motor (wire ends on the ESC phase
end and the motor lead exit). Keep-outs KO-PROP-<st>: disc radius D/2 + clearance, axially the swept envelope
10 mm forward / 6 mm aft of the hub mid-plane (ASM-E1-BLADE-ENV) + clearance on each face, on the canted shaft axis (k9.prop_keepout rotate=, CR-A5-21), so check.py tests the tilted cylinder.

UNVERIFIED-IN-FUSION: a rigid joint aligns both joint frames; E-FIN-61..64 join an unrotated mount to a rotated motor,
so Fusion may turn the stack back to 0 deg cant (fusion_backend.py docstring; CR-E1-31 to A5). Twisted blade lofts
(ruled, rotated rectangles). Bodies of bought parts are envelopes for fit, clearance and CG, not for manufacture.
"""
import math

import k09kit as k9

STATIONS = ('UR', 'UL', 'LR', 'LL')
ROT = {'UR': 'CW', 'LL': 'CW', 'UL': 'CCW', 'LR': 'CCW'}      # seen from the nose (F4 motor map, CR-E1-21)
BLADE_FWD_M, BLADE_AFT_M = 0.010, 0.006   # swept blade envelope about the hub mid-plane (ASM-E1-BLADE-ENV)
# KO-PROP-<st> (rev 7, CR-D3-26 option b, CR-E1-45): the keep-out is the swept envelope -6 / +10 mm plus the
# clearance on every face (k9.prop_keepout fwd= / aft=, A5). It replaces the symmetric +-10 mm (ASM-E1-BLADE-HALF),
# which put 4 mm of phantom blade aft of the disc.
# Mount-chain exemption (A5 / D3 action item, rev 7): NOT taken. The parts that enter are not behind the hub: the
# motor tube's nearest point is 4 mm OUTBOARD of the blade tip (r 143.8 vs 139.7 mm), 26.8 mm aft of the mid-plane
# (team/E1/prop_clearance.py). An exemption or a hub-radius annulus would hide a real tip-to-structure gap of 21.2 mm
# against the 25 mm requirement (CL-E1-TIP-GAP-TUBE). The exempt list stays the station's own stack.


def _lv(LP, key, unit=None):
    """Value of a propulsion/params.json leaf under propulsion_detail (unit-checked)."""
    return k9.val(LP['propulsion_detail'], key, unit)


def _fv(F, key, unit=None):
    return k9.val(F['fin_detail'], key, unit)


def geometry(P, LP, F=None):
    """All dimensions (m) and the station placements. P = params.json, LP = propulsion/params.json,
    F = fins/params.json (D3: motor face, cant sense, ESC pad)."""
    v = lambda k, u=None: k9.val(P, k, u)
    l = lambda k, u=None: _lv(LP, k, u)
    F = F or k9.local('fins')
    G = {}
    G['yf'], G['zm'] = v('propulsion.stations.y_m', 'm'), v('propulsion.stations.z_m', 'm')
    G['cant'] = v('propulsion.stations.cant_deg', 'deg')
    G['x_face'] = k9.motor_face_x(P)                                   # DP-MOTOR-FACE (D-28)
    G['sense'] = _fv(F, 'mount.cant_sense_UR', '-')
    G['D'] = v('propulsion.prop_diameter_m', 'm')
    G['clr'] = v('requirements.prop_clearance_min_m', 'm')

    # motor envelope (local, base face at x' = 0, thrust toward -x')
    G['bell_r'] = v('propulsion.motor_diameter_m', 'm') / 2
    G['body'] = l('motor.body_len_m', 'm')
    G['base_r'], G['base_h'] = l('motor.base_d_m', 'm') / 2, l('motor.base_h_m', 'm')
    G['bell0'] = G['base_h'] + l('motor.bell_gap_m', 'm')
    G['shaft_r'], G['shaft_ahead'] = l('motor.shaft_d_m', 'm') / 2, l('motor.shaft_ahead_m', 'm')
    G['clip_r'], G['clip_h'] = l('motor.circlip_d_m', 'm') / 2, l('motor.circlip_h_m', 'm')
    G['lead_r'], G['lead_w'], G['lead_h'] = (l('motor.lead_exit_r_m', 'm'), l('motor.lead_exit_w_m', 'm'),
                                             l('motor.lead_exit_h_m', 'm'))
    # adapter, washer, nut
    G['ad_r'], G['ad_t'] = l('adapter.base_d_m', 'm') / 2, l('adapter.base_t_m', 'm')
    G['post_r'], G['post_len'] = l('adapter.post_d_m', 'm') / 2, l('adapter.post_len_m', 'm')
    G['pilot_r'], G['pilot_depth'] = l('adapter.pilot_d_m', 'm') / 2, l('adapter.pilot_depth_m', 'm')
    G['wash_r'], G['wash_t'] = l('adapter.washer_od_m', 'm') / 2, l('adapter.washer_t_m', 'm')
    G['nut_af'], G['nut_h'] = l('adapter.nut_af_m', 'm'), l('adapter.nut_h_m', 'm')
    # prop
    G['hub_r'], G['hub_t'] = l('prop.hub_d_m', 'm') / 2, l('prop.hub_t_m', 'm')
    G['bore_r'], G['pitch'] = l('prop.bore_d_m', 'm') / 2, l('prop.pitch_m', 'm')
    G['blade'] = list(zip(l('prop.blade_r_frac', '-'), l('prop.blade_chord_m', 'm'), l('prop.blade_t_frac', '-')))

    # axial stations along -x' from the base face
    G['a_bell_top'] = G['body']                                        # adapter base seats here (E-PRP-0n origin)
    G['a_hub0'] = G['body'] + G['ad_t']                                # prop hub rear face on the adapter shoulder
    G['a_hub'] = G['a_hub0'] + G['hub_t'] / 2                          # prop mid-plane (CL-E1-STACK-PROP-PLANE)
    G['a_wash'] = G['a_hub0'] + G['hub_t']
    G['a_nut'] = G['a_wash'] + G['wash_t']
    G['a_post_tip'] = G['body'] + G['ad_t'] + G['post_len']
    G['nut_margin'] = G['a_post_tip'] - (G['a_nut'] + G['nut_h'])    # >= 0: nut fully on the thread

    # station placement: forward normal of D3's canted plate, mirrored per station (fins.py face_x_at)
    n = math.hypot(G['yf'], G['zm'])
    t_hat = (-G['zm'] / n, G['yf'] / n)                                # (y, z) of x_hat x r_hat at UR
    tc = math.tan(math.radians(G['cant']))
    G['st'] = {}
    for s in STATIONS:
        sy, sz = k9.SIGNS[s]
        ay, az = G['sense'] * tc * t_hat[0] * sy, G['sense'] * tc * t_hat[1] * sz   # plate: x = x_face + ay dy + az dz
        nn = math.sqrt(1 + ay * ay + az * az)
        thrust = (-1 / nn, ay / nn, az / nn)                           # unit thrust (shaft) direction, world
        at = (G['x_face'], sy * G['yf'], sz * G['zm'])
        ang = math.degrees(math.atan(math.hypot(ay, az)))              # = cant
        hub = tuple(at[i] + G['a_hub'] * thrust[i] for i in range(3))
        G['st'][s] = {'sy': sy, 'sz': sz, 'at': at, 'axis': (0.0, az, -ay), 'deg': ang, 'thrust': thrust,
                      'hub': hub, 'bell_top': tuple(at[i] + G['a_bell_top'] * thrust[i] for i in range(3)),
                      'rot': ROT[s]}
    G['hub_x'] = G['st']['UR']['hub'][0]

    # ESC on the outboard face of the pad (D3 fin_detail.esc_pad), long side along x
    t_fin = v('fins.board_t_m', 'm') * v('fins.layers')
    ex, ey, ez = _lv(LP, 'esc.size_m', 'm')
    x0, plen = _fv(F, 'esc_pad.x0_m', 'm'), _fv(F, 'esc_pad.len_m', 'm')
    xc = x0 + plen / 2
    y_pad_out = G['yf'] + t_fin / 2 + _fv(F, 'esc_pad.t_m', 'm')
    G['esc_lo'] = (xc - ex / 2, y_pad_out, _fv(F, 'esc_pad.z_m', 'm') - ez / 2)
    G['esc_hi'] = (xc + ex / 2, y_pad_out + ey, _fv(F, 'esc_pad.z_m', 'm') + ez / 2)
    return G


# ----------------------------------------------------------------------------- bodies (component-local, x' = shaft)
def build_motor(part, G, sy):
    """Base boss on the plate, bell (rotating can), shaft stub ahead of the bell, rear E-clip, lead exit outboard."""
    part.revolve('X', (0, 0, 0), [(0, 0), (0, G['base_r']), (-G['base_h'], G['base_r']), (-G['base_h'], 0)],
                 name='base boss')
    part.revolve('X', (0, 0, 0), [(-G['bell0'], 0), (-G['bell0'], G['bell_r']), (-G['body'], G['bell_r']),
                                  (-G['body'], 0)], name='bell')
    part.cylinder('X', (-G['body'], 0, 0), -G['shaft_ahead'], G['shaft_r'], name='shaft')
    part.cylinder('X', (0, 0, 0), G['clip_h'], G['clip_r'], name='rear shaft and E-clip')
    y0, y1 = sorted((sy * G['base_r'] * 0.8, sy * G['lead_r']))
    part.box((-G['base_h'], y0, -G['lead_w'] / 2), (-G['base_h'] + G['lead_h'], y1, G['lead_w'] / 2),
             name='phase lead exit')


def build_adapter(part, G):
    """Base (pilot bore on the shaft, 4 x M3x4 into the bell top), M6x1 post, washer, ISO 4032 nut."""
    a0, a1 = -G['body'], -G['body'] - G['ad_t']
    part.revolve('X', (0, 0, 0), [(a0, G['pilot_r']), (a0, G['ad_r']), (a1, G['ad_r']), (a1, G['pilot_r'])],
                 name='adapter base')
    tip = -G['a_post_tip']
    part.revolve('X', (0, 0, 0), [(a1, 0), (a1, G['post_r']), (tip, G['post_r']), (tip, 0)], name='M6 post')
    part.revolve('X', (0, 0, 0), [(-G['a_wash'], G['post_r']), (-G['a_wash'], G['wash_r']),
                                  (-G['a_nut'], G['wash_r']), (-G['a_nut'], G['post_r'])], name='washer')
    r = G['nut_af'] / math.sqrt(3)                                     # hexagon corner radius
    hexa = [(r * math.cos(math.radians(30 + 60 * i)), r * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    hole = [(G['post_r'] * math.cos(math.radians(60 * i)), G['post_r'] * math.sin(math.radians(60 * i)))
            for i in range(6)]
    part.prism('X', -G['a_nut'], [hexa, hole], -G['nut_h'], name='M6 nut ISO 4032')


def build_prop(part, G, cw):
    """Hub on the adapter shoulder (LPAR06E bore) + two blades along local +-y (parked spanwise), twisted flat-plate
    sections beta = atan(p / 2 pi r); leading edge forward (-x') on the side the blade moves toward."""
    a_mid = -G['a_hub']
    part.revolve('X', (0, 0, 0), [(-G['a_hub0'], G['bore_r']), (-G['a_hub0'], G['hub_r']),
                                  (-G['a_hub0'] - G['hub_t'], G['hub_r']), (-G['a_hub0'] - G['hub_t'], G['bore_r'])],
                 name='prop hub')
    R = G['D'] / 2
    w = 1 if cw else -1                       # spin about +x' (CW from the nose) or -x'
    for side in (1, -1):                      # blade along +y' moves +z' when w = +1
        secs = []
        for f, c, tf in G['blade']:
            r = max(f * R, G['bore_r'] + 0.001)
            beta = math.atan(G['pitch'] / (2 * math.pi * r))
            t = max(tf * c, 0.0006)
            mv = side * w                     # +1: this blade moves toward +z'
            cb, sb = math.cos(beta), math.sin(beta)
            # chord unit (x', z') from TE to LE: LE ahead (-x') and toward the motion
            ux, uz = -sb, mv * cb
            nx, nz = cb, mv * sb               # thickness direction, perpendicular
            pts = [(a_mid + s1 * ux * c / 2 + s2 * nx * t / 2, s1 * uz * c / 2 + s2 * nz * t / 2)
                   for s1, s2 in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
            secs.append((side * r, pts))      # Y-normal plane: (u, v) = (x', z')
        part.loft('Y', secs, smooth=False, name='blade %s' % ('+y' if side > 0 else '-y'))


# ----------------------------------------------------------------------------- module
def build(ctx):
    P, LP = ctx.params, ctx.local
    G = geometry(P, LP)
    for i, s in enumerate(STATIONS):
        S = G['st'][s]
        rot = (S['axis'], S['deg'])
        build_motor(ctx.part('PRP-001-' + s, at=S['at'], rotate=rot), G, S['sy'])
        build_adapter(ctx.part('PRP-004-' + s, at=S['at'], rotate=rot), G)
        build_prop(ctx.part('PRP-003-' + s, at=S['at'], rotate=rot), G, S['rot'] == 'CW')
        ctx.rigid('E-PRP-%02d' % (i + 1), 'PRP-004-' + s, 'PRP-001-' + s, at=S['bell_top'])
        ctx.rigid('E-PRP-%02d' % (i + 5), 'PRP-003-' + s, 'PRP-004-' + s, at=S['hub'])
        k9.prop_keepout(ctx, 'KO-PROP-' + s, S['hub'], G['D'], G['clr'],
                        exempt=('PRP-001-' + s, 'PRP-003-' + s, 'PRP-004-' + s),
                        rotate=rot, fwd=BLADE_FWD_M, aft=BLADE_AFT_M)   # canted with the stack (CR-A5-21)
    ctx.part('PRP-002-UR').box(G['esc_lo'], G['esc_hi'], name='ESC 45 x 20 x 6 in heat-shrink')
    k9.quad(ctx, {s: 'PRP-002-' + s for s in STATIONS})
