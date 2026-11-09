"""Write subsystems/fins/interfaces.json and parts.csv from the CAD module (one source). Owner: D3.

    python -I redesign/subsystems/fins/make_fins.py

Builds fusion/fins.py on the stub backend, takes each part's volume and centroid from the CAD, turns volume into a
declared mass with the rules below (fins/params.json), and writes the parts, the edges (from fins.edge_specs) and the
acknowledgements. An edge to another subsystem's part goes under "edges" only when that part is declared in its
interfaces.json; until then it waits, complete, under "edges_pending" (merge_check ignores that key). Re-run after a
params change or when wing / propulsion declare their parts, then check.py and merge_check.py.

Mass rules (status UNVERIFIED until weighed, T-D3-WEIGH):
  board   area x (areal mass x layers + laminating adhesive) + root joint (fillets, tape laps)
  tube    params wing.spar.mass_per_m_kgm (same 22 x 20 stock) x length
  sleeve  CAD volume x CF density + bond epoxy
  printed CAD volume x PETG density x fill factor (+ hardware for mounts, + bond epoxy per joint)
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
import merge_check                               # noqa: E402
from backends.stub_backend import StubBackend    # noqa: E402


def load_module():
    spec = importlib.util.spec_from_file_location('fins_module', os.path.join(HERE, 'fusion', 'fins.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stub_build(mod, P, LP, specs):
    draft = {pid: {'id': pid, 'name': name, 'material': mat, 'mass_g': 1.0, 'status': 'MODELLED'}
             for pid, name, mat, mob, rule in specs}
    ctx = fusionkit.Context(StubBackend(), parts=draft, params=P)
    k9.build_datums(ctx)
    ctx.begin_module('fins', HERE)
    ctx.dir = None                                       # register every edge spec (volumes only here)
    mod.build(ctx)
    return ctx


def masses(ctx, specs, P, LP, G, mod):
    l = lambda k, u=None: mod.lval(LP, k, u)
    petg, cf = l('materials.petg_gcc', 'g/cm3'), l('materials.cf_gcc', 'g/cm3')
    bond = l('materials.bond_g_per_joint', 'g')
    out = {}
    for pid, name, mat, mob, rule in specs:
        c = ctx.components[pid]
        V, cg = c.volume_centroid()
        cm3 = V * 1e6
        if rule == 'board':
            area = V / G['t_fin']
            lay = G['layers']
            adh = l('fin.adhesive_kgm2', 'kg/m2') * (lay - 1)
            m = area * (k9.val(P, 'fins.areal_mass_kgm2', 'kg/m2') * lay + adh) * 1000 + l('fin.root_joint_g', 'g')
            basis = 'area %.4f m2 x (0.20 x %d + %.3f) kg/m2 + root joint %.1f g' % (area, lay, adh, l('fin.root_joint_g', 'g'))
        elif rule == 'tube':
            m = k9.val(P, 'wing.spar.mass_per_m_kgm', 'kg/m') * G['L_tube'] * 1000
            basis = '0.102 kg/m x %.3f m' % G['L_tube']
        elif rule in ('plug', 'brace', 'strip'):
            ep = {'plug': 'plug.epoxy_g', 'brace': 'brace.epoxy_g', 'strip': 'edge_strip.epoxy_g'}[rule]
            m = cm3 * cf + l(ep, 'g')
            basis = '%.2f cm3 x %.2f g/cm3 + epoxy %.1f g' % (cm3, cf, l(ep, 'g'))
        elif rule == 'mount':
            m = cm3 * petg * l('mount.fill_factor') + l('mount.hardware_g', 'g')
            basis = '%.2f cm3 x %.2f x fill %.2f + pinch-bolt set %.1f g' % (cm3, petg, l('mount.fill_factor'),
                                                                           l('mount.hardware_g', 'g'))
        elif rule == 'block':
            m = cm3 * petg * l('block.fill_factor') + l('materials.block_bond_g', 'g')
            basis = '%.2f cm3 x %.2f x fill %.2f + bond %.1f g' % (cm3, petg, l('block.fill_factor'),
                                                                  l('materials.block_bond_g', 'g'))
        elif rule == 'clip':
            m = cm3 * petg * l('clip.fill_factor') + 2 * bond
            basis = '%.2f cm3 x %.2f + 2 bonds' % (cm3, petg)
        elif rule == 'collar':
            m = cm3 * petg * l('station_collar.fill_factor') + 2 * bond
            basis = '%.2f cm3 x %.2f + 2 bonds' % (cm3, petg)
        elif rule == 'anchor':
            m = cm3 * petg * l('anchor.fill_factor') + 2 * bond
            basis = '%.2f cm3 x %.2f x fill %.2f + 2 bonds' % (cm3, petg, l('anchor.fill_factor'))
        else:
            m = cm3 * petg * l('esc_pad.fill_factor') + bond
            basis = '%.2f cm3 x %.2f + bond' % (cm3, petg)
        out[pid] = (round(m, 2), [round(v, 4) for v in cg], basis, cm3)
    return out


def declared_elsewhere():
    ids = set()
    for path in merge_check.find_sources(os.path.join(REDESIGN, 'subsystems')):
        if os.path.normcase(os.path.dirname(path)) == os.path.normcase(HERE):
            continue
        try:
            with open(path, encoding='utf-8') as f:
                ids.update(p.get('id') for p in json.load(f).get('parts', []))
        except Exception:
            pass
    return ids


NOTES = {
    'board': 'one 4.8 mm board (layers per fins/params.json), laser- or knife-cut from the DXF of this outline; LE butts the tube',
    'tube': 'two per 1 000 mm stock length; scuff the bond zones (block, collars) with 120 grit',
    'mount': 'PETG, 0.2 mm layers, plate vertical on the bed; slit + ears outboard; A = UR/LL, B = UL/LR (mirror)',
    'block': 'PETG, 3 perimeters, 15 % gyroid, spar bore horizontal on the bed; sand the socket top/bottom flush',
    'clip': 'PETG, 100 %, keyhole loop flat on the bed (slot opening aft)',
    'plug': 'CF 20 x 18 offcut, 53 mm, sanded to slide in the 20 mm bore, laminating epoxy',
    'collar': 'PETG, 100 %, flat on the bed; slot aft for board + both edge strips, brace ear inboard',
    'brace': 'pultruded CF strip 10 x 3 mm, cut to length on the jig (BUILD step 12), ends scuffed',
    'anchor': 'PETG, 80 %, brace slot vertical on the bed; foot sits on the spar through a core pocket',
    'strip': 'pultruded CF strip 10 x 1 mm, cut to the template, one per board face',
    'pad': 'PETG 1.2 mm, 100 %; two strap slots, matching slots knifed through the board',
}


def write_parts_csv(specs, M):
    groups = {}
    for pid, name, mat, mob, rule in specs:
        base = '-'.join(pid.split('-')[:2])
        groups.setdefault(base, []).append((pid, name, mat, mob, rule))
    cost = {'FIN-001': 0.20, 'FIN-002': 14.16, 'FIN-003': 0.45, 'FIN-004': 0.70, 'FIN-005': 0.06, 'FIN-006': 1.00,
            'FIN-007': 0.05, 'FIN-008': 0.10, 'FIN-009': 2.00, 'FIN-010': 0.10, 'FIN-011': 2.00}
    vendor = {'FIN-001': 'Dollar Tree / Adams foam board 20 x 30 in, $1.25 (SRC-K09-CARD)',
              'FIN-002': 'SRC-CF-TUBE 22 x 20 x 1000 mm $28.32, two tubes per stock length (I1 fixes the listing)',
              'FIN-003': 'fusion/fins.py (Fusion export STL), PETG ~$22/kg',
              'FIN-004': 'fusion/fins.py, PETG', 'FIN-005': 'fusion/fins.py, PETG',
              'FIN-006': 'CF tube 20 x 18 offcut (any 20 x 18 stock), ~$1 share UNVERIFIED (I1)',
              'FIN-007': 'fusion/fins.py, PETG', 'FIN-008': 'fusion/fins.py, PETG',
              'FIN-009': 'pultruded CF strip 10 x 3 x 1000 mm, ~$10 per length, 4 braces per length UNVERIFIED (I1, CR-D3-09)',
              'FIN-010': 'fusion/fins.py, PETG',
              'FIN-011': 'pultruded CF strip 10 x 1 x 1000 mm, ~$6 per length, 3 strips per length UNVERIFIED (I1, CR-D3-09)'}
    process = {'board': 'laser/knife cut', 'tube': 'cut (fine-tooth saw, tape-wrapped)', 'mount': '3D print',
               'block': '3D print', 'clip': '3D print', 'plug': 'cut + sand', 'pad': '3D print', 'collar': '3D print',
               'brace': 'cut', 'anchor': '3D print', 'strip': 'cut'}
    rows = []
    for base, items in groups.items():
        pid, name, mat, mob, rule = items[0]
        ms = [M[i[0]][0] for i in items]
        rows.append([base, {'board': 'Half-fin (upper/lower, L/R)', 'tube': 'Motor tube CF 22x20, 324 mm',
                            'mount': 'Motor mount, 3 deg canted slip clamp (prints A and B)',
                            'block': 'Through-core block (tube socket + spar saddle)', 'clip': 'Root clip',
                            'plug': 'Tube plug CF 20x18 x 53 mm', 'pad': 'ESC pad', 'collar': 'Station collar',
                            'brace': 'Brace, CF strip 10 x 3', 'anchor': 'Brace anchor on the spar',
                            'strip': 'Edge strip, CF 10 x 1'}[rule],
                     len(items), mob, process[rule], mat, round(sum(ms) / len(ms), 2), cost[base], vendor[base],
                     NOTES[rule] + '; per-unit mass = mean of ' + ', '.join('%s %.1f g' % (i[0][8:], M[i[0]][0]) for i in items)])
    hw = [['FIN-101', 'M3x16 SHCS ISO 4762 A2 (mount pinch bolt)', 6, 'buy', '-', 'A2 stainless', 0, 0.10,
           'Bolt Depot', '4 + 2 spare; mass inside FIN-003 (joint stack of the mount-to-tube edges)'],
          ['FIN-102', 'M3 nyloc nut ISO 10511 A2', 6, 'buy', '-', 'A2 stainless', 0, 0.05, 'Bolt Depot',
           'mass inside FIN-003'],
          ['FIN-103', 'M3 washer ISO 7089 A2', 12, 'buy', '-', 'A2 stainless', 0, 0.03, 'Bolt Depot', 'mass inside FIN-003'],
          ['FIN-104', 'Hook-and-loop strap 10 x 200 mm + 25 x 40 mm tape', 4, 'buy', '-', 'nylon', 0, 0.40,
           'any (Velcro ONE-WRAP class)', 'ESC retention (PRP-002 to FIN-007 edges); mass with the ESC (propulsion)'],
          ['FIN-105', '30 min epoxy + glass microballoons (consumable)', 1, 'buy', '-', 'epoxy', 0, 0.0,
           'shared shop stock (G2)', 'mass inside the bonded parts'],
          ['FIN-106', 'Spray adhesive 3M 77 class (consumable)', 1, 'buy', '-', '-', 0, 0.0, 'shared shop stock (G2)',
           'only if two board layers are kept (CR-D3-02)']]
    with open(os.path.join(HERE, 'parts.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['part_id', 'name', 'qty', 'make_or_buy', 'process', 'material', 'mass_g', 'unit_cost_usd',
                    'vendor_or_file', 'notes'])
        w.writerows(rows + hw)
    return rows


def main():
    P = k9.load_params()
    mod = load_module()
    LP = mod.load_local()
    coords, src = k9.section(P)
    G = mod.geometry(P, LP, coords)
    specs = mod.part_specs()
    ctx = stub_build(mod, P, LP, specs)
    M = masses(ctx, specs, P, LP, G, mod)
    parts = []
    for pid, name, mat, mob, rule in specs:
        m, cg, basis, cm3 = M[pid]
        parts.append({'id': pid, 'name': name, 'subsystem': 'fins', 'status': 'MODELLED', 'mass_g': m, 'material': mat,
                      'cg_xyz_m': cg, 'make_or_buy': mob,
                      'notes': 'mass EST (%s); CG = CAD centroid; section %s' % (basis, src)})
    have = declared_elsewhere()
    edges, pending = [], []
    for e in mod.edge_specs(G):
        d = {k: e[k] for k in ('id', 'part_a', 'part_b', 'via', 'notes')}
        d['owner'] = 'fins'
        if e['joint_stack']:
            d['joint_stack'] = e['joint_stack']
        missing = [x for x in e['needs'] if x not in have]
        if missing:
            d['waits_for'] = missing
            pending.append(d)
        else:
            edges.append(d)
    acks = ['E-GER-%02d' % i for i in range(1, 5)]          # landing feet on the half-fin TE tips (CR-D3-08 ids)
    doc = {'schema': 'dbf-interfaces/1', 'subsystem': 'fins',
           '_note': 'GENERATED by subsystems/fins/make_fins.py from fusion/fins.py and params.json; do not edit by '
                    'hand. edges_pending = complete edges to parts other subsystems have not declared yet.',
           'parts': parts, 'edges': edges, 'edges_pending': pending, 'acknowledges': acks}
    with open(os.path.join(HERE, 'interfaces.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write('\n')
    write_parts_csv(specs, M)
    tot = sum(p['mass_g'] for p in parts)
    alloc = k9.val(P, 'mass.allocation_g.fins', 'g')
    by = {}
    for pid, name, mat, mob, rule in specs:
        by[rule] = by.get(rule, 0) + M[pid][0]
    print('fins: %d parts, %d edges, %d pending; mass %.1f g vs allocation %.0f g (%+.1f g)'
          % (len(parts), len(edges), len(pending), tot, alloc, alloc - tot))
    print('  ' + ', '.join('%s %.1f' % kv for kv in by.items()))
    print('  prop gap %.1f mm, slip %.1f mm, screw engagement %.2f mm, slip force %.0f N'
          % (G['prop_gap'] * 1000, G['slip'] * 1000, G['engage_min'] * 1000, G['slip_force']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
