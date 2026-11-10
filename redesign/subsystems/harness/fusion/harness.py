"""K09-L harness (F2): three lumped bundle parts with real route bodies, and one routed wire per declared electrical
edge (centreline polylines from the wire table).

Everything comes from subsystems/harness/params.json, written by team/F2/harness.py from params.json, the fins,
pod and propulsion data: re-run that script after any change, then this module follows.

Bodies: HRN-001 (pod runs: left channel, crossing behind the aft stop, right channel, under-pack channel, GPS cable
in the right handle leg) and HRN-002-R (grooves ahead of the spar slot, servo groove aft of it, outboard fin-face
legs to the ESCs and the phase legs past the collar), mirrored to HRN-002-L. Legs are axis-aligned cylinders
(k09kit.bundle), each sized by the wire mass it carries so the body centroid is the declared CG (CR-A5-27); the
wires themselves are drawn as polylines (ctx.wire), 22 AWG cap legs and 10 AWG jumpers included.
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
        part = ctx.part(pid)
        for a, b, d in legs[key]:                             # one leg per call: each has its own diameter
            k9.bundle(part, [(tuple(a), tuple(b))], d)
    k9.pair(ctx, 'HRN-002-R', 'HRN-002-L')

    by_edge = {}
    for row in _lv(H['wire_table']):
        by_edge.setdefault(row[1], []).append(row)
    for eid, e in sorted(declared.items()):
        if 'wire' not in e:                                   # mechanical: tie / wire channel
            ctx.contact(eid, e.get('notes', ''))
            continue
        rows = by_edge.get(eid, [])
        pts = []
        for r in rows:                                        # pigtail + extension joined into one polyline
            pts += [tuple(p[:3]) for p in r[9]]
        if len(pts) >= 2:
            ctx.wire(eid, pts, dia=0.003 if rows[-1][2] >= 26 else 0.006)
