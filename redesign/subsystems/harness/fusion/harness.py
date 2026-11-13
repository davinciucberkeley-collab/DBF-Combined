"""K09-L harness (F2): three lumped bundle parts as mass-only proxies, and one routed wire per declared electrical
edge (centreline polylines from the wire table) - the wires are what the CAD shows.

Everything comes from subsystems/harness/params.json, written by team/F2/harness.py from params.json, the fins,
pod and propulsion data: re-run that script after any change, then this module follows.

Bodies: HRN-113-UR/UL/LR/LL, the four XT30U mated pairs (D-74, real bodies); HRN-105-1..6 and -SL / -SR, the
JR mated pairs on the tray and in the servo recesses (D-86); HRN-001 (pod runs: left channel, crossing behind the aft stop, right channel, under-pack channel, GPS cable
in the right handle leg) and HRN-002-R (grooves ahead of the spar slot, servo groove aft of it, outboard fin-face
legs to the ESCs and the phase legs past the collar), mirrored to HRN-002-L. Legs are axis-aligned cylinders
(k09kit.bundle), each sized by the wire mass it carries so the body centroid is the declared CG (CR-A5-27). The
three parts are MASS PROXIES (ctx.part(..., proxy=True)): their part ids, mass and CG stay in interfaces, parts
and the roll-up, but no backend shows them (Fusion: hidden "(mass proxy)" component; Blender / GLB: an empty with
the part's extras), so the harness is not drawn twice. The wires are drawn as tubes (ctx.wire) of the diameter
team/F2/harness.py writes per edge (cad.wire_draw_dia_m: bundle OD), 22 AWG cap legs and 10 AWG jumpers included;
team/F2/route_clearance.py checks them against every solid (ROUTE-CLEARANCE.md).
Registers only edges declared in subsystems/harness/interfaces.json; edges in edges-pending.json wait for their
other part's owner. UNVERIFIED-IN-FUSION: wire polylines (fusion_backend draws sketch lines / pipes).
"""
import json
import os

import k09kit as k9


def _lv(d):
    return d['value'] if isinstance(d, dict) and 'value' in d else d


def build(ctx):
    H = ctx.local['harness']
    legs = _lv(H['cad']['bundle_legs'])                      # {key: [[start, end, diameter], ...]}
    with open(os.path.join(ctx.dir, 'interfaces.json'), encoding='utf-8') as f:
        iface = json.load(f)
    declared = {e['id']: e for e in iface['edges']}

    for pid, key in (('HRN-001', 'pod'), ('HRN-002-R', 'side_R')):
        part = ctx.part(pid, proxy=True)
        for a, b, d in legs[key]:                             # one leg per call: each has its own diameter
            k9.bundle(part, [(tuple(a), tuple(b))], d)
    k9.pair(ctx, 'HRN-002-R', 'HRN-002-L')

    # D-74: the four Amass XT30U mated pairs as bodies (HRN-113-<st>), so the clearance check and the graph see them
    for pid, x in sorted(_lv(H['cad'].get('xt30u', {})).items()):
        c, (ln, wd, th), (ux, uy) = x['centre'], x['size_m'], x['axis']   # axis: unit (x, y) along the wire
        loop = [(c[0] + su * ln / 2 * ux - sw * wd / 2 * uy, c[1] + su * ln / 2 * uy + sw * wd / 2 * ux)
                for su, sw in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        ctx.part(pid).prism('Z', c[2] - th / 2, [loop], th, name='XT30U mated pair')

    # D-86: the JR mated pairs (HRN-105-*): male shroud + the female housing showing behind it, along x. Edge: pins
    # vertical (tray row, shroud 4.0 mm thick in y); flat: pins across y (servo recess, bottom following the floor)
    for pid, j in sorted(_lv(H['cad'].get('jr', {})).items()):
        (x0, xm, x1), yc, (zb0, zb1) = j['x'], j['y'], j['zb']
        (_l, sw, st), (_lf, fw, ft) = j['shroud_m'], j['female_m']
        th, wd = (sw, st) if j['orient'] == 'edge' else (st, sw)          # height (z), width (y) of the shroud
        fth, fwd = (fw, ft) if j['orient'] == 'edge' else (ft, fw)
        zb = lambda x: zb0 + (zb1 - zb0) * (x - xm) / (x1 - xm)
        p = ctx.part(pid)
        p.prism('Y', yc - wd / 2, [[(xm, zb(xm)), (x1, zb(x1)), (x1, zb(x1) + th), (xm, zb(xm) + th)]], wd,
                name='JR male shroud')
        zc = lambda x: zb(x) + th / 2
        p.prism('Y', yc - fwd / 2, [[(x0, zc(x0) - fth / 2), (xm, zc(xm) - fth / 2), (xm, zc(xm) + fth / 2),
                                     (x0, zc(x0) + fth / 2)]], fwd, name='JR female housing')

    # D-83: the four fin-hole grommets (HRN-110-<st>): barrel through the 8 mm hole + lip inboard, flange outboard
    for pid, gm in sorted(_lv(H['cad'].get('grommet', {})).items()):
        (x, y, z), s, tb = gm['centre'], gm['out'], gm['board_t']
        lip = gm['length'] - tb - gm['flange_t']                       # barrel proud of the inboard face
        p = ctx.part(pid)
        y_in = y - s * (tb / 2 + lip)                                  # barrel start (inboard end)
        p.tube('Y', (x, y_in, z), s * (tb + lip), gm['barrel_od'] / 2, gm['bore'] / 2, name='grommet barrel')
        p.tube('Y', (x, y + s * tb / 2, z), s * gm['flange_t'], gm['flange_od'] / 2, gm['bore'] / 2,
               name='grommet flange')

    # D-88: heat-shrink sleeves (HRN-107-*) on the soldered ends, tubes along x from the part face, shrunk on the lead
    for pid, v in sorted(_lv(H['cad'].get('sleeves', {})).items()):
        ctx.part(pid).tube('X', tuple(v['start']), v['axis'] * v['length'], v['r_out'], v['r_in'],
                           name='heat-shrink sleeve')

    dia = _lv(H['cad'].get('wire_draw_dia_m', {}))
    strands = _lv(H['cad'].get('wire_strands', {}))           # {wire id: [[diameter, polyline], ...]}
    by_edge = {}
    for row in _lv(H['wire_table']):
        by_edge.setdefault(row[1], []).append(row)
    for eid, e in sorted(declared.items()):
        if 'wire' not in e:                                   # mechanical: tie / wire channel
            ctx.contact(eid, e.get('notes', ''))
            continue
        rows = by_edge.get(eid, [])
        pts, st = [], []
        for r in rows:                                        # pigtail + extension joined into one polyline
            pts += [tuple(p[:3]) for p in r[9]]
            st += [(line, d) for d, line in strands.get(r[0], [])]
        if len(pts) >= 2:
            ctx.wire(eid, pts, dia=dia.get(eid, 0.003 if rows[-1][2] >= 26 else 0.006), strands=st or None)
