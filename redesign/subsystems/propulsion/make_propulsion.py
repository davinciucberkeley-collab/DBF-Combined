"""Write subsystems/propulsion/interfaces.json from the CAD module and parts.csv (one source). Owner: E1.

    python -I redesign/team/E1/propulsion.py               # masses -> parts.csv, claims (run first after a change)
    python -I redesign/subsystems/propulsion/make_propulsion.py

Builds fusion/propulsion.py on the stub backend, takes each instance's CG from the CAD (volume centroid of the
envelope; bought parts, so the declared mass is parts.csv's per-unit mass, not volume x density), and writes the
16 instance nodes, the two connection types, the eight E-PRP edges with their full joint stacks and the
acknowledgements of every edge another subsystem declares on a PRP part (fins E-FIN-61..68, harness E-HRN-17..20,
and any added later). Re-run after a params change, then check.py and merge_check.py.
"""
import csv
import glob
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REDESIGN, 'fusion'))

import fusionkit                                 # noqa: E402
import k09kit as k9                              # noqa: E402
from backends.stub_backend import StubBackend    # noqa: E402

STATIONS = ('UR', 'UL', 'LR', 'LL')
ROT = {'UR': 'CW', 'LL': 'CW', 'UL': 'CCW', 'LR': 'CCW'}
SKU = {'CW': '11x5.5MRP (LP11055MRP)', 'CCW': '11x5.5MR (LP11055MR)'}
THREAD = {'CW': 'LH', 'CCW': 'RH'}
PRINT = {'UR': 'A', 'LL': 'A', 'UL': 'B', 'LR': 'B'}


def load_module():
    spec = importlib.util.spec_from_file_location('propulsion_module', os.path.join(HERE, 'fusion', 'propulsion.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_parts():
    with open(os.path.join(HERE, 'parts.csv'), encoding='utf-8', newline='') as f:
        return {r['part_id']: r for r in csv.DictReader(f)}


def stub_build(mod, P):
    ids = ['PRP-%03d-%s' % (k, s) for k in (1, 2, 3, 4) for s in STATIONS]
    draft = {i: {'id': i, 'name': i, 'material': 'x', 'mass_g': 1.0, 'status': 'MODELLED'} for i in ids}
    ctx = fusionkit.Context(StubBackend(), parts=draft, params=P)
    k9.build_datums(ctx)
    ctx.begin_module('propulsion', HERE)
    mod.build(ctx)
    return ctx


def foreign_edges():
    """Edges declared by other subsystems on a PRP part: propulsion acknowledges them."""
    out = []
    for path in sorted(glob.glob(os.path.join(REDESIGN, 'subsystems', '*', 'interfaces.json'))):
        if os.path.dirname(path) == HERE:
            continue
        with open(path, encoding='utf-8') as f:
            doc = json.load(f)
        for e in doc.get('edges', []):
            if any(str(e.get(k, '')).startswith('PRP-') for k in ('part_a', 'part_b')):
                out.append(e['id'])
    return sorted(set(out))


def planned_edges():
    """Edges A4's interface plan assigns to another owner on a PRP part (team/A4/interface_plan.json). Those not yet
    declared go under acknowledges_pending (D1's convention, CR-D1-09) and move to acknowledges on the next run after
    the owner declares them (CR-A1-48: E-HRN-13..16, -24..27, -34..37, E-FIN-81..88)."""
    path = os.path.join(REDESIGN, 'team', 'A4', 'interface_plan.json')
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        plan = json.load(f)
    return sorted({e['id'] for e in plan.get('edges', []) if e.get('owner') != 'propulsion'
                   and any(str(e.get(k, '')).startswith('PRP-') for k in ('part_a', 'part_b'))})


def main():
    P = k9.load_params()
    mod = load_module()
    ctx = stub_build(mod, P)
    G = mod.geometry(P, ctx.local)
    rows = read_parts()
    m = {k: float(rows[k]['mass_g']) for k in ('PRP-001', 'PRP-002', 'PRP-003', 'PRP-004')}
    r4 = lambda v: [round(c, 4) for c in v]                                   # noqa: E731
    cg = {pid: r4(c.volume_centroid()[1]) for pid, c in ctx.components.items()}
    parts, edges = [], []
    for i, s in enumerate(STATIONS):
        rot, th = ROT[s], THREAD[ROT[s]]
        parts += [
            {'id': 'PRP-001-' + s, 'name': 'Motor %s SunnySky X3108S KV900 (%s from the nose)' % (s, rot),
             'subsystem': 'propulsion', 'status': 'MODELLED', 'mass_g': m['PRP-001'], 'material': 'motor (bought)',
             'cg_xyz_m': cg['PRP-001-' + s], 'make_or_buy': 'buy', 'electrical': 'sink',
             'notes': '81.0 g with factory leads + 4 x M3x8 screws 3.2 g (PRP-005); envelope OD %.1f x %.1f mm, '
                      'base on D3 canted plate print %s (7 deg tangential, D-27), shaft along the canted axis; '
                      'CG = CAD centroid; UNVERIFIED (T-E1-MOTOR-RM)' % (2000 * G['bell_r'], 1000 * G['body'], PRINT[s])},
            {'id': 'PRP-002-' + s, 'name': 'ESC %s LANRC 45 A' % s, 'subsystem': 'propulsion', 'status': 'MODELLED',
             'mass_g': m['PRP-002'], 'material': 'electronics (bought)', 'cg_xyz_m': cg['PRP-002-' + s],
             'make_or_buy': 'buy', 'electrical': 'bus',
             'notes': '%.1f g EST, stripped: factory power leads removed, F2 solders 16 AWG to the pads (D-48); '
                      '45 x 20 x 6 mm body (ASM-E3-ESC), 7.5 mm proud of the pad at the strap (CL-E1-ESC-PROUD), flat '
                      'on the outboard face of FIN-007-%s, FET side out, phase end forward (x %.4f), power end aft; '
                      'CG = CAD centroid' % (m['PRP-002'], s, G['esc_lo'][0])},
            {'id': 'PRP-003-' + s, 'name': 'Prop %s APC %s' % (s, SKU[rot]), 'subsystem': 'propulsion',
             'status': 'MODELLED', 'mass_g': m['PRP-003'], 'material': 'glass-filled nylon',
             'cg_xyz_m': cg['PRP-003-' + s], 'make_or_buy': 'buy',
             'notes': 'hub centre %.1f mm from the motor face on the canted axis (x %.4f; datum DP-PROP %.4f, CR-E1-29); '
                      'removed for transport; blades parked spanwise in CAD' % (1000 * G['a_hub'], G['st'][s]['hub'][0],
                                                                                  k9.val(P, 'propulsion.stations.x_prop_plane_m', 'm'))},
            {'id': 'PRP-004-' + s, 'name': 'Prop adapter %s M6x1 %s + nut + washer' % (s, th), 'subsystem': 'propulsion',
             'status': 'MODELLED', 'mass_g': m['PRP-004'], 'material': '6061 aluminium / steel',
             'cg_xyz_m': cg['PRP-004-' + s], 'make_or_buy': 'buy',
             'notes': '%s thread: prop drag tightens the nut on a %s motor (CR-E1-21); CG = CAD centroid' % (th, rot)},
        ]
        edges += [
            {'id': 'E-PRP-%02d' % (i + 1), 'part_a': 'PRP-004-' + s, 'part_b': 'PRP-001-' + s, 'via': 'CT-PROP-ADAPTER',
             'owner': 'propulsion',
             'notes': 'adapter pilot bore (4 mm x 8.5 mm) on the shaft stub, base flat on the bell top, four M3x4 on '
                      'the 12 mm circle (vendor fit list names the X3108S KV900); bench joint, never a field joint',
             'joint_stack': {'fastener': 'M3x4 SHCS (4 supplied with the adapter)', 'count': 4, 'grade': '12.9 (vendor)',
                             'hole': 'counterbored clearance in the adapter base; M3 tapped in the bell top by the maker',
                             'insert': 'none (aluminium bell)', 'engagement_mm': 2.5, 'min_engagement_mm': 2.0,
                             'min_engagement_basis': 'deviation D-58 (a) from the 1.0 d rule (D-41), granted on '
                                                     'CL-E1-ADAPTER-STRIP (RF 1.70 at 2.0 mm vs the 0.5 N m preload) '
                                                     'and conditional on T-E1-MOTOR-RM measuring >= 2.5 mm of bell-top '
                                                     'thread (CL-E1-ADAPTER-THREAD-D58); if the bell has >= 3.0 mm of '
                                                     'thread and >= 4.0 mm free depth, M3x5 (3.5 mm, no deviation, '
                                                     'CL-E1-ADAPTER-M3X5-ENGAGE) replaces it (CR-A4-43); tip >= 0.5 mm '
                                                     'short of the windings',
                             'washer_nut': 'none', 'torque': '0.5 N m + Loctite 243 on the tip threads (C6; vendor '
                                                             'value wins if printed)',
                             'tool': '2.0 mm hex key (vendor set)', 'access': 'from the front (-x), prop and nut off',
                             'install_order': 1, 'removal_order': 3},
             'retention': {'item': 'Loctite 243', 'count': 4,
                           'load_n': 'prop torque 0.33 N m at full throttle on a 6 mm radius = 14 N per screw in shear; '
                                     'thrust 16 N / 4 = 4 N axial; preload 0.5 N m / (0.2 x 3 mm) = 0.83 kN',
                           'inspection': 'witness mark on each head; checked at every field set-up'}},
            {'id': 'E-PRP-%02d' % (i + 5), 'part_a': 'PRP-003-' + s, 'part_b': 'PRP-004-' + s, 'via': 'CT-PROP-NUT',
             'owner': 'propulsion', 'field_joint': True,
             'notes': '%s on a %s post; LPAR06E ring centres the 1/4 in bore on the M6 post; hub rear face on the adapter '
                      'shoulder; prop off for transport (pouch spanner, D-40)' % (SKU[rot], th),
             'joint_stack': {'fastener': 'M6x1 hex nut ISO 4032 (%s, steel, from the adapter set) + M6 washer 6 x 12 x '
                                         '1.0' % th, 'count': 1, 'grade': '8 (steel)',
                             'hole': '6.35 mm prop bore with LPAR06E ring to 6 mm',
                             'insert': 'none (threaded aluminium post)',
                             'engagement_mm': round(1000 * (G['post_len'] - G['hub_t'] - G['wash_t']), 2),
                             'min_engagement_mm': round(1000 * G['nut_h'], 2),
                             'min_engagement_basis': 'full ISO 4032 nut height (nut strength >= the post); post tip '
                                                     'at least flush with the nut face (CL-E1-NUT-ENGAGE); a 1.6 mm '
                                                     'washer fails this',
                             'washer_nut': 'M6 washer 1.0 mm under the nut', 'torque': '1.5 N m, bell held by hand '
                                                                                        '(C6 CR-C6-05, T-C6-PROPNUT)',
                             'tool': '10 mm spanner (the one field tool, box pouch)', 'access': 'from the front (-x)',
                             'install_order': 2, 'removal_order': 1}},
        ]
    doc = {'schema': 'dbf-interfaces/1', 'subsystem': 'propulsion',
           '_note': 'Written by subsystems/propulsion/make_propulsion.py from fusion/propulsion.py and parts.csv '
                    '(team/E1/propulsion.py writes parts.csv). Do not hand-edit. Instance nodes per station '
                    '(UR UL LR LL). Motor-to-mount (E-FIN-61..64) and ESC-to-pad (E-FIN-65..68) edges are D3\'s; '
                    'every electrical edge (ESC power, phase, signal) is harness\'s (D-20); both acknowledged here.',
           'parts': parts,
           'connection_types': [
               {'id': 'CT-PROP-ADAPTER', 'kind': 'mechanical', 'method': 'fastened',
                'spec': 'bolt-on prop adapter, 4 x M3x4 SHCS into the motor bell, pilot on the shaft'},
               {'id': 'CT-PROP-NUT', 'kind': 'mechanical', 'method': 'fastened',
                'spec': 'M6x1 nut and washer clamp the prop hub on the adapter post (field joint)'}],
           'edges': edges,
           'acknowledges': foreign_edges()}
    doc['acknowledges_pending'] = [e for e in planned_edges() if e not in doc['acknowledges']]
    out = os.path.join(HERE, 'interfaces.json')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(json.dumps(doc, indent=1) + '\n')
    tot = sum(p['mass_g'] for p in parts)
    print('subsystems/propulsion/interfaces.json: %d parts, %d edges, %d acknowledged, %d pending, %.1f g' % (
        len(parts), len(edges), len(doc['acknowledges']), len(doc['acknowledges_pending']), tot))
    print('hub x %.4f (datum %.4f), nut margin %.2f mm, motor face %.4f' % (
        G['hub_x'], k9.val(P, 'propulsion.stations.x_prop_plane_m', 'm'), 1000 * G['nut_margin'], G['x_face']))
    for s in STATIONS:
        print(s, 'thrust dir', tuple(round(c, 4) for c in G['st'][s]['thrust']), 'hub', r4(G['st'][s]['hub']))


if __name__ == '__main__':
    main()
    if '--check' not in __import__('sys').argv:     # C6 FASTENERS-CAD: re-apply the modelled fastener parts
        import os as _o, runpy as _r
        _r.run_path(_o.path.join(_o.path.abspath(__file__).rsplit(_o.sep + 'redesign' + _o.sep, 1)[0], 'redesign', 'team',
                                 'C6', 'fastener_parts.py'), run_name='c6_hook')['run']()
