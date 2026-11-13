"""Write subsystems/fins/interfaces.json and parts.csv from the CAD module (one source). Owner: D3. Design R5 (CR-A1-63).

    python -I redesign/subsystems/fins/make_fins.py

Builds fusion/fins.py on the stub backend, takes each part's volume and centroid from the CAD, turns volume into a
declared mass with the rules below (fins/params.json), and writes the parts, the edges (from fins.edge_specs) and the
acknowledgements. An edge to another subsystem's part goes under "edges" only when that part is declared in its
interfaces.json; until then it waits, complete, under "edges_pending" (merge_check ignores that key). Re-run after a
params change or when wing / propulsion declare their parts, then check.py and merge_check.py.

Joint data blocks (A4: bond / clamp / retention): the C6 block for the same edge id in team/C6/joint_stacks.json is
used where C6 sized the joint; where D3 changed the geometry since (e.g. the 15 mm collar, the R4 root fillets) the D3
area replaces C6's and load_n says so; edges C6 has not sized carry the D3 block. A C6 joint_stack adds its 'load'
line to the D3 stack. Thermal blocks (E-FIN-81...88) take t_design_c and heat_w from team/E3 (claims, results).

Mass rules (status UNVERIFIED until weighed, T-D3-WEIGH):
  board   laminate area x (areal mass x layers + laminating adhesive) + tape laps; root fillets = CAD volume x
          fin.root_fillet.gcc (bodies named 'root fillet' in the half-fin part)
  tube    params wing.spar.mass_per_m_kgm (same 22 x 20 stock) x length
  CF      CAD volume x CF density + bond epoxy (plug, brace, strips, pins)
  printed CAD volume x density (PETG; ASA for mounts and ESC pads, D-42) x fill factor (+ hardware, + bond epoxy)
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
    petg, cf, asa = l('materials.petg_gcc', 'g/cm3'), l('materials.cf_gcc', 'g/cm3'), l('materials.asa_gcc', 'g/cm3')
    bond = l('materials.bond_g_per_joint', 'g')
    out = {}
    for pid, name, mat, mob, rule in specs:
        c = ctx.components[pid]
        V, cg = c.volume_centroid()
        cm3 = V * 1e6
        if rule == 'board':
            fil = [s for s in c.shapes if s.name == mod.FILLET]
            vf = sum(s.volume_centroid()[0] for s in fil)
            cf_w = [0.0, 0.0, 0.0]
            for s in fil:
                v, cc = s.volume_centroid()
                cc = c.to_world(cc)
                cf_w = [cf_w[i] + v * cc[i] for i in range(3)]
            area = (V - vf) / G['t_fin']
            lay = G['layers']
            adh = l('fin.adhesive_kgm2', 'kg/m2') * (lay - 1)
            am = k9.val(P, 'fins.areal_mass_kgm2', 'kg/m2')
            m_lam = area * (am * lay + adh) * 1000 + l('fin.root_joint_g', 'g')
            m_fil = vf * 1e6 * G['fil_gcc']
            m = m_lam + m_fil
            cg_lam = [(V * cg[i] - cf_w[i]) / (V - vf) for i in range(3)]
            cg = [(m_lam * cg_lam[i] + m_fil * cf_w[i] / vf) / m for i in range(3)] if vf > 0 else cg
            basis = ('area %.4f m2 x (%.2f x %d + %.3f) kg/m2 + tape laps %.1f g + root fillets %.1f cm3 x %.2f g/cm3 '
                     '= %.1f g' % (area, am, lay, adh, l('fin.root_joint_g', 'g'), vf * 1e6, G['fil_gcc'], m_fil))
        elif rule == 'tube':
            m = k9.val(P, 'wing.spar.mass_per_m_kgm', 'kg/m') * G['L_tube'] * 1000
            basis = '%.3f kg/m x %.3f m' % (k9.val(P, 'wing.spar.mass_per_m_kgm', 'kg/m'), G['L_tube'])
        elif rule in ('plug', 'brace', 'strip', 'pins'):
            ep = {'plug': 'plug.epoxy_g', 'brace': 'brace.epoxy_g', 'strip': 'edge_strip.epoxy_g',
                  'pins': 'edge_strip.pin_epoxy_g'}[rule]
            m = cm3 * cf + l(ep, 'g')
            basis = '%.3f cm3 x %.2f g/cm3 + epoxy %.1f g' % (cm3, cf, l(ep, 'g'))
        elif rule == 'mount':
            m = cm3 * asa * l('mount.fill_factor') + l('mount.hardware_g', 'g')
            basis = '%.2f cm3 x ASA %.2f x fill %.2f + pinch-bolt set %.1f g' % (cm3, asa, l('mount.fill_factor'),
                                                                               l('mount.hardware_g', 'g'))
        elif rule == 'block':
            m = cm3 * petg * l('block.fill_factor') + l('materials.block_bond_g', 'g')
            basis = '%.2f cm3 x PETG %.2f x fill %.2f + bond %.1f g' % (cm3, petg, l('block.fill_factor'),
                                                                       l('materials.block_bond_g', 'g'))
        elif rule == 'collar':
            vt = sum(s.volume_centroid()[0] for s in c.shapes if s.name == 'tail tongue') * 1e6
            ff, tf = l('station_collar.fill_factor'), l('station_collar.tongue_fill')
            m = ((cm3 - vt) * ff + vt * tf) * petg + 3 * bond
            basis = '(%.2f cm3 x %.2f + tongue %.2f cm3 x %.2f) x PETG %.2f + 3 bonds (tube, tongue, strips)' % (
                cm3 - vt, ff, vt, tf, petg)
        elif rule == 'anchor':
            m = cm3 * petg * l('anchor.fill_factor') + 2 * bond
            basis = '%.2f cm3 x PETG %.2f x fill %.2f + 2 bonds' % (cm3, petg, l('anchor.fill_factor'))
        else:
            m = cm3 * asa * l('esc_pad.fill_factor') + bond
            basis = '%.2f cm3 x ASA %.2f + bond' % (cm3, asa)
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


def c6_blocks():
    path = os.path.join(REDESIGN, 'team', 'C6', 'joint_stacks.json')
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f).get('edges', {})
    except (OSError, ValueError):
        return {}


def merge_blocks(e, c6):
    """A4 data blocks for edge e: C6's block where C6 sized it, the D3 geometry where R3 changed it (e['geo'])."""
    out = {}
    for key, mine in e['blocks'].items():
        theirs = c6.get(key)
        if not theirs:
            blk = dict(mine)
            if blk.get('load_n') == 'see C6':
                blk['load_n'] = 'not sized yet (C6)'
            out[key] = blk
            continue
        blk = dict(theirs)
        for g in e['geo']:
            if g in mine and abs(mine[g] - theirs.get(g, 0)) > 0.05 * max(1, mine[g]):
                blk[g] = mine[g]
                blk['load_n'] = '%s [D3 R5 geometry: %s %s, C6 used %s; C6 re-checks]' % (
                    theirs.get('load_n', ''), g, mine[g], theirs.get(g))
        out[key] = blk
    return out


def merge_stack(mine, c6):
    """D3 joint stack (geometry, engagement, torque) + C6's load line for the same edge where C6 sized it."""
    st = dict(mine)
    theirs = (c6 or {}).get('joint_stack') or {}
    if theirs.get('load'):
        st['load'] = theirs['load'] + ' (C6)'
    return st


def e3_thermal():
    """{claim id: (value, limit)} from team/E3/claims.json and the mission results, for the thermal blocks."""
    out, res = {}, {}
    try:
        with open(os.path.join(REDESIGN, 'team', 'E3', 'claims.json'), encoding='utf-8') as f:
            for n in json.load(f).get('nodes', []):
                if n.get('type') == 'claim':
                    out[n['id']] = (n.get('value'), (n.get('limit') or {}).get('value'))
        with open(os.path.join(REDESIGN, 'team', 'E3', 'thermal_results.json'), encoding='utf-8') as f:
            res = json.load(f).get('mission', {})
    except (OSError, ValueError):
        pass
    return out, res


def fill_thermal(blk, claims, res):
    t = dict(blk)
    cid, hk = t.pop('claim', None), t.pop('heat_key', None)
    val, lim = claims.get(cid, (None, None))
    q = res.get(hk)
    t['heat_w'] = ('%.1f W source loss, hover design (E3 %s); ~0 W credited through this contact' % (q, hk)
                   if q is not None else '— (E3 to publish)')
    if lim is not None:
        t['t_max_c'] = lim
    t['t_design_c'] = round(val, 1) if val is not None else '—'
    t['claim'] = cid
    return t


NOTES = {
    'board': 'two 4.8 mm boards spray-laminated (D-26), knife-cut together from the DXF of this outline (notch for the '
             'collar tongue, D5 stepped 45.4 mm tip); LE butts the tube; root fillets are microballoon epoxy (BUILD step 11)',
    'tube': 'two per 1 000 mm stock length; scuff the bond zones (block, collars) with 120 grit',
    'mount': 'ASA (D-42), 0.2 mm layers, 5 perimeters, enclosed printer; collar axis vertical on the bed; slit + ears '
             'outboard; A = UR/LL, B = UL/LR (mirror); drill the motor holes 3.4 mm through the pilots to the measured '
             'pattern; plate face 7.5 mm ahead of the collar front, cheeks 17 mm (D-61), 18 mm grip (D-91)',
    'block': 'PETG, 3 perimeters, 15 % gyroid, spar bore horizontal on the bed; sand the socket top/bottom flush; '
             'strap eyes print with it; four vertical plan-form edges R 3 mm (D-68) to match the R 3 mm pocket corners',
    'plug': 'CF 20 x 18 offcut, 53 mm, sanded to slide in the 20 mm bore, laminating epoxy',
    'collar': 'PETG, 100 %, printed upside down on the tail cap (slots open upward on the bed); 22 mm ring (D-90), 40 mm '
              'two-face tail, brace ear inboard; phase tie lug at x 0.060, slot open along x (CR-F2-16)',
    'brace': 'pultruded CF strip 10 x 2 mm, cut to length on the jig, ends scuffed',
    'anchor': 'PETG, 80 %, brace slot vertical on the bed; foot sits on the spar through a core pocket',
    'strip': 'pultruded CF strip 10 x 1 mm, cut to the template, one per laminate face, ends at the step front x 0.2746',
    'pad': 'ASA 1.2 mm, 100 % (D-42); two strap slots, matching slots knifed through the laminate',
    'pins': 'pultruded CF rod 2.5 mm cut to 12 mm (D-70); 2.5 mm drill through strip-laminate-strip after cure, epoxy injected before the pin, sanded flush',
}


def write_parts_csv(specs, M, P):
    groups = {}
    for pid, name, mat, mob, rule in specs:
        base = '-'.join(pid.split('-')[:2])
        groups.setdefault(base, []).append((pid, name, mat, mob, rule))
    cost = {'FIN-001': 0.40, 'FIN-002': 14.16, 'FIN-003': 0.40, 'FIN-004': 0.70, 'FIN-006': 1.06,
            'FIN-007': 0.05, 'FIN-008': 0.15, 'FIN-009': 2.00, 'FIN-010': 0.10, 'FIN-011': 2.00, 'FIN-012': 0.75}
    vendor = {'FIN-001': 'Dollar Tree / Adams foam board 20 x 30 in, $1.25 (SRC-K09-CARD)',
              'FIN-002': 'SRC-CF-TUBE 22 x 20 x 1000 mm $28.32, two tubes per stock length (I1 fixes the listing)',
              'FIN-003': 'fusion/fins.py (Fusion export STL), ASA ~$25/kg (D-42)',
              'FIN-004': 'fusion/fins.py, PETG',
              'FIN-006': 'CF tube 20 x 18 x 1000 mm, $20 per metre (I1 D03): one length gives both FIN-006 plugs (2 x 53 mm) and '
                          'C2 six 36 mm spar plugs (216 mm) with ~0.65 m spare (CR-I1-17); cost = 53 mm share',
              'FIN-007': 'fusion/fins.py, ASA (D-42)', 'FIN-008': 'fusion/fins.py, PETG',
              'FIN-009': 'pultruded CF strip 10 x 2 x 1000 mm, ~$10 per length, 4 braces per length UNVERIFIED (I1, CR-D3-09)',
              'FIN-010': 'fusion/fins.py, PETG',
              'FIN-011': 'pultruded CF strip 10 x 1 x 1000 mm, ~$6 per length, 4 strips per length UNVERIFIED (I1, CR-D3-09)',
              'FIN-012': 'pultruded CF rod 2.5 x 1000 mm, ~$4, one rod makes all four pin sets UNVERIFIED (I1)'}
    process = {'board': 'laminate + knife cut', 'tube': 'cut (fine-tooth saw, tape-wrapped)', 'mount': '3D print + drill',
               'block': '3D print', 'plug': 'cut + sand', 'pad': '3D print', 'collar': '3D print',
               'brace': 'cut', 'anchor': '3D print', 'strip': 'cut', 'pins': 'cut + drill + bond'}
    title = {'board': 'Half-fin, two-layer foam board (UR/UL/LR/LL)',
             'tube': 'Motor tube CF 22x20, %.0f mm' % (k9.val(P, 'fins.tube.length_m', 'm') * 1000),
             'mount': 'Motor mount ASA, 7 deg canted plate, slip clamp (prints A and B)',
             'block': 'Through-core block (tube socket + spar saddle + strap eyes)',
             'plug': 'Tube plug CF 20x18 x 53 mm', 'pad': 'ESC pad, ASA',
             'collar': 'Station collar, 22 mm + 40 mm two-face tail', 'brace': 'Brace, CF strip 10 x 2 (C4 CR-C4-16)',
             'anchor': 'Brace anchor on the spar', 'strip': 'Edge strip, CF 10 x 1',
             'pins': 'Edge-strip pin set, CF rod 2.5 mm'}
    rows = []
    for base, items in groups.items():
        pid, name, mat, mob, rule = items[0]
        ms = [M[i[0]][0] for i in items]
        rows.append([base, title[rule], len(items), mob, process[rule], mat, round(sum(ms) / len(ms), 2), cost[base],
                     vendor[base], NOTES[rule] + '; per-unit mass = mean of ' +
                     ', '.join('%s %.2f g' % (i[0][8:], M[i[0]][0]) for i in items)])
    hw = [['FIN-101', 'M3x16 SHCS ISO 4762 A2 (mount pinch bolt)', 6, 'buy', '-', 'A2 stainless', 0, 0.10,
           'Bolt Depot', '4 + 2 spare; mass inside FIN-003 (joint stack of E-FIN-05...08)'],
          ['FIN-102', 'M3 nyloc nut ISO 10511 A2', 6, 'buy', '-', 'A2 stainless', 0, 0.05, 'Bolt Depot',
           'mass inside FIN-003; reuse <= 3 times'],
          ['FIN-103', 'M3 washer ISO 7089 A2', 12, 'buy', '-', 'A2 stainless', 0, 0.03, 'Bolt Depot', 'mass inside FIN-003'],
          ['FIN-104', 'Hook-and-loop strap 10 x 200 mm + 25 x 40 mm tape', 4, 'buy', '-', 'nylon', 0, 0.40,
           'any (Velcro ONE-WRAP class)', 'ESC retention, one strap per ESC (E-FIN-65...68, CR-E3-02); mass with the ESC (propulsion)'],
          ['FIN-105', '30 min epoxy + glass microballoons + colloidal silica (consumable)', 1, 'buy', '-', 'epoxy', 0, 0.0,
           'shared shop stock (G2)', 'mass inside the bonded parts'],
          ['FIN-106', 'Spray adhesive 3M 77 class (consumable)', 1, 'buy', '-', '-', 0, 0.0, 'shared shop stock (G2)',
           'laminates the two board layers (D-26); mass inside FIN-001 (fin.adhesive_kgm2)'],
          ['FIN-107', 'Loctite 243 (consumable)', 1, 'buy', '-', '-', 0, 0.0, 'shared shop stock (G2)',
           'motor screws, tip only (E-FIN-61...64)']]
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
    specs = mod.part_specs(G)
    ctx = stub_build(mod, P, LP, specs)
    M = masses(ctx, specs, P, LP, G, mod)
    parts = []
    for pid, name, mat, mob, rule in specs:
        m, cg, basis, cm3 = M[pid]
        parts.append({'id': pid, 'name': name, 'subsystem': 'fins', 'status': 'MODELLED', 'mass_g': m, 'material': mat,
                      'cg_xyz_m': cg, 'make_or_buy': mob,
                      'notes': 'mass EST (%s); CG = CAD centroid; section %s' % (basis, src)})
    have = declared_elsewhere()
    c6 = c6_blocks()
    e3c, e3r = e3_thermal()
    edges, pending = [], []
    for e in mod.edge_specs(G):
        d = {k: e[k] for k in ('id', 'part_a', 'part_b', 'via', 'notes')}
        d['owner'] = 'fins'
        if e['joint_stack']:
            d['joint_stack'] = merge_stack(e['joint_stack'], c6.get(e['id']))
        d.update(merge_blocks(e, c6.get(e['id'], {})))
        if 'thermal' in d:
            d['thermal'] = fill_thermal(d['thermal'], e3c, e3r)
        missing = [x for x in e['needs'] if x not in have]
        if missing:
            d['waits_for'] = missing
            pending.append(d)
        else:
            edges.append(d)
    acks = ['E-GER-%02d' % i for i in range(1, 5)]          # landing feet on the half-fin stepped tips (CR-D5-11)
    acks += ['E-HRN-03', 'E-HRN-05'] + ['E-HRN-%02d' % i for i in range(6, 10)]   # lead ties: boss / collar lugs (CR-F2-05)
    acks += ['E-HRN-%02d' % i for i in range(42, 46)]       # fin-hole grommets HRN-110-<st> CA'd in the lead hole (D-83)
    acks += ['E-PWR-%02d' % i for i in range(11, 15)]       # ESC caps foam-taped on the half-fin faces (CR-F1-22)
    doc = {'schema': 'dbf-interfaces/1', 'subsystem': 'fins',
           '_note': 'GENERATED by subsystems/fins/make_fins.py from fusion/fins.py and params.json (design R5); do not '
                    'edit by hand. edges_pending = complete edges to parts other subsystems have not declared yet.',
           'parts': parts, 'edges': edges, 'edges_pending': pending, 'acknowledges': acks}
    with open(os.path.join(HERE, 'interfaces.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write('\n')
    write_parts_csv(specs, M, P)
    tot = sum(p['mass_g'] for p in parts)
    alloc = k9.val(P, 'mass.allocation_g.fins', 'g')
    by = {}
    for pid, name, mat, mob, rule in specs:
        by[rule] = by.get(rule, 0) + M[pid][0]
    print('fins: %d parts, %d edges, %d pending; mass %.1f g vs allocation %.0f g (%+.1f g margin)'
          % (len(parts), len(edges), len(pending), tot, alloc, alloc - tot))
    print('  ' + ', '.join('%s %.1f' % kv for kv in by.items()))
    print('  prop gap %.1f mm, cap-to-tube-end %.1f mm, screw engagement %.2f mm, slip force %.0f N, '
          'plate corner %.1f mm ahead of the face at the axis'
          % (G['prop_gap'] * 1000, G['slip'] * 1000, G['engage_min'] * 1000, G['slip_force'],
             (G['x_face'] - G['plate_x_min']) * 1000))
    print('  collar z %.4f..%.4f, ear mid %.4f, brace L %.1f / %.1f mm, strip %.0f mm (tail %.1f mm), %d pins/half'
          % (G['z_sc0'], G['z_sc1'], G['z_ear_mid'], G['brace_len'] * 1000, G['brace_len_l'] * 1000,
             G['strip_len'] * 1000, G['strip_tail_len'] * 1000, len(G['pins'])))
    fil = {pid: M[pid][2].split('root fillets ')[1] for pid, _, _, _, r in specs if r == 'board'}
    print('  tongue %.2f mm in the %.0f mm collar (fit %.2f mm), last pin x %.4f (+r %.4f <= %.4f), x_prop %.5f, '
          'x_face %.5f' % (G['tongue_d'] * 1000, G['sc_h'] * 1000, G['tongue_fit'] * 1000, G['pins'][-1][0],
                          G['pins'][-1][0] + G['pin_r'], G['x_tip_clear'], G['x_prop'], G['x_face']))
    print('  root fillets: ' + '; '.join('%s %s' % (k[8:], v) for k, v in fil.items()))
    print('  fillet couple capacity upper %.3e / lower %.3e m3, skin bond %.0f / %.0f mm2, elevon gap aft %.1f mm'
          % (G['fil_cap_u'], G['fil_cap_l'], G['fil_bond_u'], G['fil_bond_l'], G['elevon_gap_aft'] * 1000))
    return 0


if __name__ == '__main__':
    rc = main()
    if '--check' not in __import__('sys').argv:     # C6 FASTENERS-CAD: re-apply the modelled fastener parts
        import os as _o, runpy as _r
        _r.run_path(_o.path.join(_o.path.abspath(__file__).rsplit(_o.sep + 'redesign' + _o.sep, 1)[0], 'redesign', 'team',
                                 'C6', 'fastener_parts.py'), run_name='c6_hook')['run']()
    sys.exit(rc)
