"""K09-L power (PWR, F1, revision PWR-R1 + D-74): flight pack, main disconnect, power board, bus, ESC caps.

Envelopes of the bought parts plus the made parts as the shop cuts or prints them. Everything sits in the pod's
left channel except the four ESC capacitors (on the half-fins). D-74: no UBEC and no fuse; the power board's servo
BEC (6 V jumper) feeds the servos through the FC's Vx rail, and the deck is drawn to the keep-out KO-PWR-BOARD.

  PWR-001 flight pack      LiPo envelope at the D-24 station on the EVA pads + its own 10 AWG leads over the aft
                           stop + the AS150U pack half (re-terminated, D-32) seated in the park
  PWR-002 AS150U aircraft  aircraft half (cups facing -x) in the frame's cradle + the two 10 AWG main jumpers
  PWR-003 power board      CoreWing F405 Wing V2 power board (V/I sense, servo BEC on the 6 V jumper), separated
                           from the FC stack (case S), foam-taped on the frame deck, pads aft at the deck window;
                           52 x 32 mm (manual), height UNVERIFIED (BOARD-CHECK.md)
  PWR-004 bus board        FR4 strip with two tinned 8 AWG bus bars, foam-taped on D2's PDB plate between the boss
                           rows, under the deck: 4 ESC pigtails (XT30U at the side exits) leave from its bars
  PWR-006 power frame      printed PETG: deck (56 x 34 mm board seat = KO-PWR-BOARD footprint) on 4 nylon spacers
                           over D2's four M3 inserts (one screw stack per corner), wire window, AS150U cradle
                           (housing bonded + 1 tie), two legs, lead tunnel
  PWR-008 ESC capacitor    680 uF 25 V low-ESR, foam-taped on each half-fin beside the ESC power end (x4, quad)

Stack in the left channel, bottom up (z, m): pod floor 0.0198 | PDB plate 0.0208 | bus board 0.0224, bars to 0.0257 |
bosses to 0.0268 | 10 mm nylon spacers | deck 0.0368-0.0388 | power board to 0.0488. The AS150U sits on the cradle
floor (deck plane) so its contacts line up with the power board pads: the main jumpers run level, the output pair
drops 24.8 mm through the window to the bars (2 x 2 x OD, ASM-PWR-BEND).

Registers (one per edge this module owns): E-PWR-03 rigid at the frame screw pattern centre; E-PWR-01, -02, -05
and E-PWR-11..14 contacts. No wires: every wire is a harness edge (F2). Positions come from params.json,
subsystems/pod/params.json (read-only) and subsystems/power/params.json; no literal duplicates a shared number.

UNVERIFIED-IN-FUSION: nothing beyond boxes and one notched prism; the rigid joint on a component placed at the
origin. The power board and AS150U envelopes are UNVERIFIED until measured (T-PWR-ARRIVAL).
"""
import json
import os

import k09kit as k9

ST = ('UR', 'UL', 'LR', 'LL')


def _pod_params(ctx):
    """subsystems/pod/params.json (D2), read-only: the plate, bosses, channels and park the power parts sit on."""
    path = os.path.join(os.path.dirname(ctx.dir), 'pod', 'params.json')
    with open(path, encoding='utf-8') as f:
        d = json.load(f)
    return {k: v['value'] for k, v in d.items() if isinstance(v, dict) and 'value' in v}


def layout(get, L, pod):
    """All power geometry (m). get(key, unit) reads params.json; L = power-local values; pod = pod-local values."""
    g = {}
    zb = get('pod.z_base_m', 'm')
    tb = get('fins.board_t_m', 'm')
    W = get('pod.size_m', 'm')[1]
    pk = get('battery.size_m', 'm')
    zf = zb + tb                                        # foam floor top
    zt = zf + pod['tray_floor_t_m']                     # tray / plate top (plates are as thick as the tray floor)
    zplate = zf + pod['plate_t_m']
    zboss = zplate + pod['boss_h_m']                    # boss top = insert face
    yi = W / 2 - tb                                     # channel outer wall (inner face)
    ci = pod['bay_min_m'][1] / 2 + pod['guide_t_m']     # channel inner edge (bay guide outer face)
    cy = (ci + yi) / 2                                  # channel centre line
    g.update(zf=zf, zt=zt, zplate=zplate, zboss=zboss, yi=yi, ci=ci, cy=cy)

    # ---- pack (D-24 station: aft face at the nominal 550 g position, on the EVA pads)
    a_nom = pod['pack_aft_face_m'][0]
    zp = zt + pod['pad_t_m']
    g['pack'] = ((a_nom - pk[0], -pk[1] / 2, zp), (a_nom, pk[1] / 2, zp + pk[2]))
    g['pack_c'] = ((2 * a_nom - pk[0]) / 2, 0.0, zp + pk[2] / 2)

    # ---- PDB plate, bosses (D2), bus board in the strip between the boss rows
    p0, p1 = pod['pdb_plate_x_m']
    pcx, pp = (p0 + p1) / 2, pod['pdb_pattern_m']
    g['bosses'] = [(pcx + dx, -cy + dy) for dx in (-pp / 2, pp / 2) for dy in (-pp / 2, pp / 2)]
    g['screw_c'] = (pcx, -cy, zboss)
    bl, bw, bt = L['bus_board_m']
    g['bus'] = ((pcx - bl / 2, -cy - bw / 2, zplate), (pcx + bl / 2, -cy + bw / 2, zplate + bt))
    bar_len, bar_d, bar_p = L['bar_m']
    zbar = zplate + bt + bar_d / 2
    g['bars'] = [((pcx - bar_len / 2, -cy + s * bar_p / 2 - bar_d / 2, zplate + bt),
                  (pcx + bar_len / 2, -cy + s * bar_p / 2 + bar_d / 2, zplate + bt + bar_d)) for s in (-1, 1)]
    g['zbar'] = zbar

    # ---- frame: deck on spacers, window, cradle, legs. D-74: the deck's board seat is the keep-out KO-PWR-BOARD
    # footprint (x from its forward end to the window, 34 mm wide); the board sits pads-aft at the window.
    park0, park1 = pod['park_x_m']
    dz0 = zboss + L['spacer_h_m']
    dz1 = dz0 + L['deck_t_m']
    blen, bwid, bh = L['board_env_m']
    m = L['deck_margin_m']
    wt = L['wall_t_m']
    win = L['window_x_m']
    ko = L['ko_board_m']
    x_deck1 = park0                                    # deck ends where the park starts (cradle front wall)
    x_board1 = x_deck1 - win                           # power board aft edge (pads over the window)
    x_board0 = x_board1 - blen
    x_deck0 = min(ko['x_m'][0], x_board0 - m)          # deck forward end = keep-out forward end
    g['deck'] = ((x_deck0, -cy - bwid / 2 - m, dz0), (x_deck1, -cy + bwid / 2 + m, dz1))
    g['window'] = (x_board1, x_deck1)
    g['board'] = ((x_board0, -cy - bwid / 2, dz1 + 0.001), (x_board1, -cy + bwid / 2, dz1 + 0.001 + bh))
    g['ko'] = ((ko['x_m'][0], -cy - ko['w_m'] / 2, dz1), (ko['x_m'][1], -cy + ko['w_m'] / 2, ko['z_top_m']))
    hl, hw, hh = L['as150u_half_m']
    cw = hw / 2 + wt                                    # cradle half width
    g['cradle_floor'] = ((x_deck1, -cy - cw, dz0), (park1, -cy + cw, dz1))
    g['front_wall'] = ((x_deck1, -cy - cw, dz1), (x_deck1 + wt, -cy + cw, dz1 + L['cradle_wall_h_m']))
    g['side_walls'] = [((x_deck1, -cy + s * cw - (wt if s > 0 else 0), dz1),
                        (park1, -cy + s * cw + (0 if s > 0 else wt), dz1 + L['cradle_wall_h_m'])) for s in (-1, 1)]
    xa = x_deck1 + wt + hl                              # aircraft half mating end
    lx, ly = L['leg_m']
    lb = L.get('leg_setback_m', 0.0)                    # D-74: legs forward of the aft end (left XT30U turn)
    g['legs'] = [((park1 - lb - lx, -cy + s * cw - (ly if s > 0 else 0), zf), (park1 - lb, -cy + s * cw + (0 if s > 0 else ly), dz0))
                 for s in (-1, 1)]
    g['dz0'], g['dz1'] = dz0, dz1
    # AS150U halves: aircraft half in the cradle, pack half behind it (inside the pack's mass)
    g['as_air'] = ((x_deck1 + wt, -cy - hw / 2, dz1), (xa, -cy + hw / 2, dz1 + hh))
    g['as_pack'] = ((xa, -cy - hw / 2, dz1), (park1, -cy + hw / 2, dz1 + hh))
    g['pin_z'] = dz1 + hh / 2
    # pack's own leads: aft face over the stop, turn left, forward into the pack half
    zl = zp + pod['aft_stop_m'][1]                     # top of the aft stop: the leads lie on it
    lead_t = 0.006
    xturn = a_nom + 0.005
    g['lead_a'] = ((a_nom - 0.001, -0.020, zl), (xturn, -0.008, zl + lead_t))
    g['lead_b'] = ((park1, -cy - 0.005, g['pin_z'] - 0.003), (xturn, -0.008, zl + lead_t))
    return g


def build(ctx):
    v = ctx.value
    L = {k: d['value'] for k, d in ctx.local['power'].items()}
    pod = _pod_params(ctx)
    G = layout(v, L, pod)

    # PWR-001 flight pack + its leads + AS150U pack half
    pk = ctx.part('PWR-001')
    pk.box(*G['pack'], name='LiPo 4S 6500 envelope')
    pk.box(*G['lead_a'], name='pack leads 10 AWG over the aft stop')
    pk.box(*G['lead_b'], name='pack leads 10 AWG into the park')
    pk.box(*G['as_pack'], name='AS150U pack half')

    # PWR-006 power frame (printed PETG)
    fr = ctx.part('PWR-006')
    (dx0, dy0, dz0), (dx1, dy1, dz1) = G['deck']
    w0, w1 = G['window']
    bl = G['board'][0][1], G['board'][1][1]
    deck = [[(dx0, dy0), (dx1, dy0), (dx1, dy1), (dx0, dy1)],
            [(w0, bl[0] + 0.002), (w1 - 0.0005, bl[0] + 0.002), (w1 - 0.0005, bl[1] - 0.002), (w0, bl[1] - 0.002)]]
    fr.prism('Z', dz0, deck, dz1 - dz0, name='petg deck with wire window')
    fr.box(*G['cradle_floor'], name='petg cradle floor')
    fr.box(*G['front_wall'], name='petg cradle front wall (cup slots)')
    for i, b in enumerate(G['side_walls']):
        fr.box(*b, name='petg cradle side wall %d' % i)
    for i, b in enumerate(G['legs']):
        fr.box(*b, name='petg cradle leg %d' % i)

    # PWR-003 power board on the deck; PWR-002 AS150U aircraft half in the cradle
    ctx.part('PWR-003').box(*G['board'], name='power board envelope')
    ctx.part('PWR-002').box(*G['as_air'], name='AS150U aircraft half')

    # PWR-004 bus board on the PDB plate
    bus = ctx.part('PWR-004')
    bus.box(*G['bus'], name='FR4 bus carrier')
    for i, b in enumerate(G['bars']):
        bus.box(*b, name='bus bar %s' % ('+' if i == 0 else '-'))

    # PWR-008 ESC capacitors on the half-fins beside the ESC power end (UR built, quad mirrors)
    cl, cd = L['cap_m']
    yf = v('fins.y_m', 'm')
    face = yf + v('fins.layers', '-') * v('fins.board_t_m', 'm') / 2   # outboard face of the two-layer half-fin
    esc = _esc_pad(ctx)
    x0 = esc['x1'] + L['cap_gap_x_m']
    zc = (esc['z0'] + esc['z1']) / 2
    cap = ctx.part('PWR-008-UR')
    cap.box((x0, face, zc - cd / 2), (x0 + cl, face + cd, zc + cd / 2), name='680 uF cap')
    k9.quad(ctx, {s: 'PWR-008-' + s for s in ST})

    build_frame_hardware(ctx, G)

    # ---- registrations (edges declared in subsystems/power/interfaces.json)
    ctx.rigid('E-PWR-03', 'PWR-006', 'POD-002', at=G['screw_c'])
    ctx.contact('E-PWR-01', 'AS150U aircraft half seated in the cradle: sanded housing epoxied in, front wall takes the push, 1 tie over')
    ctx.contact('E-PWR-02', 'power board on 3M foam tape + 1 tie on the deck')
    ctx.contact('E-PWR-05', 'bus board on foam tape on the PDB plate, under the deck')
    for i, s in enumerate(ST):
        ctx.contact('E-PWR-%d' % (11 + i), 'ESC cap %s foam-taped on the half-fin face' % s)


def build_frame_hardware(ctx, G):
    """E-PWR-03 stack at each of the four bosses as components (only when declared, k09kit.hw_part; C6
    FASTENERS-CAD): PWR-107 brass insert flush in D2's boss, PWR-102 10 mm nylon spacer boss -> deck, PWR-103 0.5 mm
    nylon washer on the deck, PWR-101 M3x18 PA66 pan head down through deck and spacer into the insert."""
    ins = k9.hw_part(ctx, 'PWR-107')
    if ins is None:
        return
    sp, wa, sc = k9.hw_part(ctx, 'PWR-102'), k9.hw_part(ctx, 'PWR-103'), k9.hw_part(ctx, 'PWR-101')
    zb, dz0, dz1 = G['screw_c'][2], G['dz0'], G['dz1']
    for x, y in G['bosses']:
        k9.hw_insert(ins, 'Z', (x, y, zb), -1, 'M3')
        k9.hw_washer(sp, 'Z', (x, y, zb), 1, 'M3', od=0.006, t=dz0 - zb, idia=0.0032, name='nylon spacer 10 mm')
        k9.hw_washer(wa, 'Z', (x, y, dz1), 1, 'M3', t=0.0005, name='nylon washer 0.5 mm')
        k9.hw_screw(sc, 'Z', (x, y, dz1 + 0.0005), -1, 'M3', 0.018, 'pan', name='M3x18 PA66 pan head')
    x, y = G['bosses'][0]
    k9.hw_join(ctx, 'PWR-107', 'POD-002', (x, y, zb - 0.003))
    k9.hw_join(ctx, 'PWR-101', 'PWR-107', (x, y, zb - 0.002))
    k9.hw_join(ctx, 'PWR-101', 'PWR-006', (x, y, (dz0 + dz1) / 2))
    k9.hw_join(ctx, 'PWR-102', 'PWR-006', (x, y, dz0))
    k9.hw_join(ctx, 'PWR-102', 'POD-002', (x, y, zb))
    k9.hw_join(ctx, 'PWR-103', 'PWR-006', (x, y, dz1))


def _esc_pad(ctx):
    """ESC pad station on the UR half-fin from subsystems/fins/params.json#fin_detail.esc_pad (D3), read-only."""
    path = os.path.join(os.path.dirname(ctx.dir), 'fins', 'params.json')
    with open(path, encoding='utf-8') as f:
        e = json.load(f)['fin_detail']['esc_pad']
    x0, ln, h, zc = (e[k]['value'] for k in ('x0_m', 'len_m', 'h_m', 'z_m'))
    return {'x1': x0 + ln, 'z0': zc - h / 2, 'z1': zc + h / 2}
