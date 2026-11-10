"""Write subsystems/mechanisms/interfaces.json and parts.csv from the CAD module (one source). Owner: D6. D6-R2.

    python -I redesign/subsystems/mechanisms/make_mechanisms.py

Builds fusion/mechanisms.py on the stub backend, takes each part's volume and centroid from the CAD, turns volume
into a declared mass (rules below), and writes parts, edges (mechanisms.edge_specs) and acknowledgements. It also
writes the section table mec.section (skin heights near the hinge, from k09kit.surface_z) into params.json so that
team/D6/mech_calcs.py stays a pure function of named inputs.

An edge to a wing part goes under "edges" only when the wing declares that part; until then it waits, complete,
under "edges_pending" (merge_check ignores that key). Re-run after a params change or when the wing declares its
parts, then check.py and merge_check.py.

Mass rules (UNVERIFIED until weighed, T-D6-WEIGH):
  bought   datasheet (servo), estimate (arm, clevis)
  printed  CAD volume x PETG density x fill + epoxy per bonded part (+ 2 x M2 screws on the cover)
  rod      CAD volume x pultruded CF density (mec.link.rod_gcc)
  steel    CAD volume x 7.85 g/cm3 (+ clevis on the pushrod)
  CF tube  CAD volume x 1.55 g/cm3 + groove fill per metre
  tape     strip area x areal mass
"""
import csv
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(HERE))
for p in (os.path.join(REDESIGN, 'fusion'), os.path.join(REDESIGN, 'interfaces')):
    if p not in sys.path:
        sys.path.insert(0, p)

import fusionkit                                 # noqa: E402
import k09kit as k9                              # noqa: E402
from backends.stub_backend import StubBackend    # noqa: E402

SIDES = ('R', 'L')
SIDE_NAME = {'R': 'right', 'L': 'left'}
# number -> (name, material, make_or_buy, mass rule, vendor/file, process)
CATALOG = {
    'MEC-001': ('Elevon servo Savox SH-0255MG+', 'servo (bought)', 'buy', 'servo', 'Savox SH-0255MG+ (SRC-D6-SH0255)',
                'bought'),
    'MEC-002': ('Servo arm, single, hole at 15.6 mm', 'nylon (supplied with servo)', 'buy', 'arm',
                'supplied with MEC-001; hole drilled 1.6 mm', 'trim + drill'),
    'MEC-003': ('Pushrod 2-56 steel, Z-bend + steel clevis + keeper', 'steel (bought)', 'buy', 'pushrod',
                'Du-Bro 2-56 threaded rod + 2-56 steel clevis (SRC-D6-CLEVIS)', 'cut, Z-bend'),
    'MEC-004': ('Control horn, inboard panel (clevis + rod boss)', 'PETG (printed)', 'make', 'printed',
                'subsystems/mechanisms/fusion/mechanisms.py#build_horn', 'FDM PETG 100 %'),
    'MEC-005': ('Inter-panel rod, 1/8 in pultruded CF', 'CF rod pultruded (bought)', 'buy', 'rod',
                '1/8 in (3.18 mm) pultruded carbon rod (SRC-D6-CFROD)', 'cut 67 mm (abrasive disc), scuff'),
    'MEC-006': ('Link horn, outboard panel (rod boss)', 'PETG (printed)', 'make', 'printed',
                'subsystems/mechanisms/fusion/mechanisms.py#build_horn', 'FDM PETG 100 %'),
    'MEC-007': ('Servo cover with arm slot', 'PETG (printed)', 'make', 'cover',
                'subsystems/mechanisms/fusion/mechanisms.py#build_cover', 'FDM PETG'),
    'MEC-008': ('Servo frame (ear slots, cover bosses)', 'PETG (printed)', 'make', 'printed',
                'subsystems/mechanisms/fusion/mechanisms.py#build_frame', 'FDM PETG'),
    'MEC-009': ('Elevon torque tube CF 5 x 4 mm', 'CF tube 5x4 roll-wrapped (bought)', 'buy', 'tube',
                'CF tube 5 x 4 x 1000 mm (SRC-D6-CFTUBE)', 'cut, scuff'),
    'MEC-010': ('Elevon hinge tape, two strips', 'packing tape BOPP', 'buy', 'tape', 'clear packing tape 48 mm, '
                'slit to 25 mm', 'cut'),
}


def load_module():
    spec = importlib.util.spec_from_file_location('mechanisms_module', os.path.join(HERE, 'fusion', 'mechanisms.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def all_ids(mod):
    out = []
    for pid in mod.PARTS_R:
        out += [pid, mod.mirror_id(pid)]
    return out


def number(pid):
    return '-'.join(pid.split('-')[:2])


def suffix(pid):
    return pid.split('-')[2]


def part_name(pid):
    s = suffix(pid)
    side = SIDE_NAME[s[0]]
    extra = {'I': ', inboard panel', 'O': ', outboard panel'}.get(s[1:], '')
    return '%s %s%s' % (CATALOG[number(pid)][0], side, extra)


def stub_build(mod, P):
    draft = {pid: {'id': pid, 'name': pid, 'material': 'x', 'mass_g': 1.0, 'status': 'MODELLED'} for pid in all_ids(mod)}
    ctx = fusionkit.Context(StubBackend(), parts=draft, params=P)
    k9.build_datums(ctx)
    ctx.begin_module('mechanisms', HERE)
    mod.build(ctx)
    return ctx


def masses(ctx, mod, LP):
    l = lambda k, u=None: mod.lval(LP, k, u)
    petg, fill, bond = l('print.petg_gcc', 'g/cm3'), l('print.fill'), l('print.bond_g', 'g')
    steel, cf = l('link.steel_gcc', 'g/cm3'), l('tube.cf_gcc', 'g/cm3')
    out = {}
    for pid, c in ctx.components.items():
        V, cg = c.volume_centroid()
        cm3 = V * 1e6
        rule = CATALOG[number(pid)][3]
        if rule == 'servo':
            m, basis = l('servo.mass_g', 'g'), 'datasheet 15.8 g'
        elif rule == 'arm':
            m, basis = l('arm.mass_g', 'g'), 'estimate'
        elif rule == 'pushrod':
            wire = c.shapes[0].volume_centroid()[0] * 1e6 * steel
            m, basis = wire + l('pushrod.clevis_g', 'g') + 0.1, 'wire %.2f g + clevis + keeper' % wire
        elif rule == 'printed':
            m, basis = cm3 * petg * fill + bond, '%.2f cm3 PETG x %.2f + epoxy' % (cm3, fill)
        elif rule == 'cover':
            m, basis = cm3 * petg * fill + 0.2, '%.2f cm3 PETG x %.2f + 2 M2 screws' % (cm3, fill)
        elif rule == 'rod':
            m, basis = cm3 * l('link.rod_gcc', 'g/cm3'), '%.2f cm3 CF rod' % cm3
        elif rule == 'steel':
            m, basis = cm3 * steel, '%.2f cm3 steel' % cm3
        elif rule == 'tube':
            ln = c.bbox()[1][1] - c.bbox()[0][1]
            m, basis = cm3 * cf + l('tube.fill_g_per_m', 'g/m') * ln, '%.2f cm3 CF + groove fill' % cm3
        elif rule == 'tape':
            area = sum(abs((b.points()[1][0] - b.points()[0][0]) * (b.points()[2][1] - b.points()[0][1]))
                       for b in c.shapes)
            m, basis = area * l('tape.areal_kgm2', 'kg/m2') * 1000, '%.0f cm2 tape' % (area * 1e4)
        out[pid] = (round(m, 2), [round(v, 4) for v in cg], basis)
    return out


def declared_elsewhere():
    have, edges = set(), set()
    subs = os.path.join(REDESIGN, 'subsystems')
    for d in os.listdir(subs):
        if d == 'mechanisms':
            continue
        f = os.path.join(subs, d, 'interfaces.json')
        if os.path.exists(f):
            try:
                doc = json.load(open(f, encoding='utf-8'))
            except ValueError:
                continue
            have.update(p.get('id') for p in doc.get('parts', []))
            edges.update(e.get('id') for e in doc.get('edges', []))
    return have, edges


def blocks(e, G, LP, mod):
    """A4 data blocks per edge (joint_stack / motion / bond / retention)."""
    eid = int(e['id'].split('-')[2])
    out = {}
    if e['via'] == 'CT-SERVO-SPLINE':
        out['joint_stack'] = {'fastener': 'servo arm screw M2 x 4 (supplied)', 'count': 1, 'grade': 'as supplied',
                              'hole': 'arm hub on the 25T spline, screw into the output shaft thread',
                              'insert': 'none (servo output shaft tapped)', 'engagement_mm': 3.0,
                              'min_engagement_mm': 2.0, 'washer_nut': 'none', 'torque': 'snug + Loctite 222',
                              'tool': 'Phillips #0', 'access': 'from outboard (+y R / -y L) before the cover goes on',
                              'install_order': 3, 'removal_order': 2}
    elif e['via'] == 'CT-M2-SCREW-PLASTIC':
        out['joint_stack'] = {'fastener': 'M2 x 6 self-tapping pan head', 'count': 2, 'grade': 'A2 stainless',
                              'hole': '2.4 mm clearance in the cover; 1.6 mm pilot in the frame boss, 6 mm deep',
                              'insert': 'none', 'engagement_mm': 5.2, 'min_engagement_mm': 4.0,
                              'washer_nut': 'none', 'torque': 'snug, head seated (plastic)', 'tool': 'Phillips #1',
                              'access': 'from below (-z), wing on its back', 'install_order': 6, 'removal_order': 1}
    elif e['via'] == 'CT-CLEVIS':
        th = G['theta_stop']
        out['motion'] = {'axis': 'Y', 'range_deg': [-60, 60]}
        out['clearance_mm'] = {'note': 'team/D6/mech_calcs.py CL-D6-CLEAR-*: min gap through +/-28 deg',
                               'hinge_moment_nmm': 'CL-D6-H-VD-FULL', 'servo_at_stops_deg': [round(th[0], 1),
                                                                                            round(th[1], 1)]}
    elif e['via'] == 'CT-SERVO-EAR-SLOT':
        out['retention'] = {'item': 'ears in 2.7 mm end-wall slots + screwed cover under the case', 'count': 2,
                            'load_n': 'servo reaction couple 0.31 N m / 22.8 mm = 14 N per slot at the VD case',
                            'inspection': 'servo does not rock when the arm is pushed by hand (pre-flight)'}
    elif e['via'] == 'CT-TAPE-SKIN':
        out['retention'] = {'item': 'packing tape, 10 mm overlap all round' if eid in (17, 18)
                            else '25 mm strip, 12 mm each side of the hinge line', 'count': 1,
                            'load_n': '-', 'inspection': 'edges not lifting (every flight)'}
    elif e['via'] == 'CT-EPOXY':
        area = {1: 'frame', 2: 'frame', 11: 'horn', 12: 'horn', 23: 'horn', 24: 'horn'}.get(eid)
        out['bond'] = {'adhesive': '30 min epoxy + microballoons (foam); 30 min epoxy (rod, tube)',
                       'area_mm2': 'CL-D6-BOND-%s' % area.upper() if area else '-',
                       'prep': 'tape cut back, foam scuffed, PETG sanded 120 grit, rod/tube scuffed + IPA',
                       'cure': '24 h at >= 20 C before load', 'load_n': 'CL-D6-PUSHROD-F' if area else '-',
                       'load_case': 'full travel at VD (R-SERVO-TORQUE)', 'sized_by': 'D6 (method of C6 CALC-C6-LINKAGE)'}
    return out


def section_table(P, coords):
    c = k9.val(P, 'wing.chord_m', 'm')
    xs = [round(0.17 + 0.0025 * i, 4) for i in range(int((0.32 - 0.17) / 0.0025) + 1)]
    zu = [round(k9.surface_z(coords, c, x / c, 'upper'), 6) for x in xs]
    zl = [round(k9.surface_z(coords, c, x / c, 'lower'), 6) for x in xs]
    note = 'GENERATED by make_mechanisms.py from k09kit.surface_z (subsystems/wing/s5010.dat, chord wing.chord_m)'
    return {'x_m': {'value': xs, 'unit': 'm', 'source': 'k09kit.surface_z', 'status': 'CHECKED', 'note': note},
            'zu_m': {'value': zu, 'unit': 'm', 'source': 'k09kit.surface_z', 'status': 'CHECKED', 'note': note},
            'zl_m': {'value': zl, 'unit': 'm', 'source': 'k09kit.surface_z', 'status': 'CHECKED', 'note': note}}


def main():
    P = k9.load_params()
    mod = load_module()
    path_lp = os.path.join(HERE, 'params.json')
    LP = mod.load_local(path_lp)
    coords, src = k9.section(P)
    LP['mec']['section'] = section_table(P, coords)
    with open(path_lp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(LP, f, indent=1, ensure_ascii=False)
        f.write('\n')
    G = mod.geometry(P, LP, coords)
    ctx = stub_build(mod, P)
    M = masses(ctx, mod, LP)
    LP['mec']['mass_total_g'] = {'value': round(sum(m for m, _, _ in M.values()), 2), 'unit': 'g',
                                 'source': 'subsystems/mechanisms/make_mechanisms.py', 'status': 'UNVERIFIED',
                                 'note': 'GENERATED: sum of the 22 declared part masses (EST until weighed, T-D6-WEIGH)'}
    with open(path_lp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(LP, f, indent=1, ensure_ascii=False)
        f.write('\n')
    parts = []
    for pid in all_ids(mod):
        name, mat, mob, rule, vendor, proc = CATALOG[number(pid)]
        m, cg, basis = M[pid]
        d = {'id': pid, 'name': part_name(pid), 'subsystem': 'mechanisms', 'status': 'MODELLED', 'mass_g': m,
             'material': mat, 'cg_xyz_m': cg, 'make_or_buy': mob,
             'notes': 'mass EST (%s); CG = CAD centroid' % basis}
        if number(pid) == 'MEC-001':
            d['electrical'] = 'sink'
        if number(pid) == 'MEC-010':
            d['carried'] = True
        parts.append(d)
    have, other_edges = declared_elsewhere()
    edges, pending = [], []
    for e in mod.edge_specs(G):
        d = {k: e[k] for k in ('id', 'part_a', 'part_b', 'via', 'notes')}
        d['owner'] = 'mechanisms'
        d.update(blocks(e, G, LP, mod))
        missing = [x for x in e['needs'] if x not in have]
        if missing:
            d['waits_for'] = missing
            pending.append(d)
        else:
            edges.append(d)
    acks = [x for x in ('E-HRN-28', 'E-HRN-29') if x in other_edges]
    ctypes = [{'id': 'CT-SERVO-EAR-SLOT', 'kind': 'mechanical', 'method': 'slid',
               'spec': 'servo mounting ears slid into slots in a printed frame, held by a screwed cover (no screws '
                       'along the span: no tool access in a wing pocket)'}]
    doc = {'schema': 'dbf-interfaces/1', 'subsystem': 'mechanisms',
           '_note': 'GENERATED by subsystems/mechanisms/make_mechanisms.py from fusion/mechanisms.py and the params '
                    '(design D6-R2); do not edit by hand. edges_pending = complete edges to wing parts the wing has '
                    'not declared yet. E-MEC-13..16 of the A4 plan are retired (the link is bonded in the horns, '
                    'E-MEC-19..22, not in the panels).',
           'parts': parts, 'connection_types': ctypes, 'edges': edges, 'edges_pending': pending, 'acknowledges': acks}
    with open(os.path.join(HERE, 'interfaces.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write('\n')
    write_parts_csv(mod, M, LP)
    tot = sum(p['mass_g'] for p in parts)
    alloc = k9.val(P, 'mass.allocation_g.mechanisms', 'g')
    print('mechanisms: %d parts, %d edges, %d pending; mass %.1f g vs allocation %.0f g (%+.1f g margin)'
          % (len(parts), len(edges), len(pending), tot, alloc, alloc - tot))
    for num in sorted(CATALOG):
        ms = [M[p][0] for p in M if number(p) == num]
        print('  %s x%d  %6.2f g each  %s' % (num, len(ms), ms[0], M[[p for p in M if number(p) == num][0]][2]))


def write_parts_csv(mod, M, LP):
    cost = {'MEC-001': mod.lval(LP, 'servo.unit_cost_usd', 'USD'), 'MEC-002': 0.0, 'MEC-003': 2.50,
            'MEC-004': 0.20, 'MEC-005': 1.50, 'MEC-006': 0.20, 'MEC-007': 0.10, 'MEC-008': 0.20, 'MEC-009': 2.00,
            'MEC-010': 0.20}
    note = {'MEC-001': 'UNVERIFIED price (SRC-D6-SH0255-PRICE); 3.9 kgf cm at 6 V, 1.4 A stall; buy 3 (1 spare, I1)',
            'MEC-003': 'per side: 1/3 of a 12 in 2-56 rod + 1 clevis + keeper; EST',
            'MEC-005': 'cut from one 1 m 1/8 in pultruded CF rod (EST $5/rod); D6-R2, was music wire', 'MEC-009': 'cut from one 1 m tube (EST $8): 2 x 0.210 m outboard + 2 x 0.160 m inboard',
            'MEC-002': 'supplied with the servo', 'MEC-010': 'from the wing tape roll'}
    rows = []
    for num in sorted(CATALOG):
        ids = [p for p in M if number(p) == num]
        name, mat, mob, rule, vendor, proc = CATALOG[num]
        rows.append([num, name, len(ids), mob, proc, mat, round(sum(M[i][0] for i in ids) / len(ids), 2), cost[num], vendor,
                     note.get(num, 'mass per unit EST; instances ' + ' '.join(sorted(suffix(i) for i in ids)))])
    with open(os.path.join(HERE, 'parts.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['part_id', 'name', 'qty', 'make_or_buy', 'process', 'material', 'mass_g', 'unit_cost_usd',
                    'vendor_or_file', 'notes'])
        w.writerows(rows)


if __name__ == '__main__':
    main()
