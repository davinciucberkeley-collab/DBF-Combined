"""Generate the K09-L skeleton's interfaces.json files, modules.txt and mass_budget.json, then fill every part's
cg_xyz_m from its CAD centroid (stub build). Owner: A5.

    python -I redesign/fusion/skeleton/make_skeleton.py

The skeleton is the reference layout every designer starts from, at params.json revision A1-R3 (geometry R3:
motor tubes 0.344 m through the core at x 0.045, upper and lower 0.21 m half-fins, each braced by a CF strip from a
station collar (DX-COLLAR) to an anchor on the spar (DX-ANCHOR), printed through-core blocks, mounts on the tube
ends with the motor face at DP-MOTOR-FACE (7 deg cant not modelled), 48 mm feet splayed to the pad contact
(DX-FOOT), pod 0.21 x 0.14 at x -0.115 with the pack at the D-24 station, 11x5.5MR props, transport box from
requirements.box_external_m). One envelope per part at the DATUMS.md stations, masses split from
params.json#mass.allocation_g (sum = the 2 324 g allocations, D-38; the 276 g A1 reserve is not placed).
Part ids <PREFIX>-9xx (9xx is reserved for the skeleton; real subsystems number from 001); one node per physical
instance, id <part>-<UR|UL|LR|LL|L|R> (README, CR-A3-09). It is not the design. Re-run after any params.json change,
then python -I redesign/fusion/check.py --skeleton --strict.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FUSION = os.path.dirname(HERE)
sys.path.insert(0, FUSION)

import build_all                                   # noqa: E402
import k09kit as k9                                # noqa: E402
from backends.stub_backend import StubBackend      # noqa: E402

P = k9.load_params()
A = lambda k: float(k9.val(P, 'mass.allocation_g.' + k, 'g'))
V = lambda k, u=None: k9.val(P, k, u)
ST = k9.STATIONS                                   # UR UL LR LL
SIDE = {'UR': 'R', 'UL': 'L', 'LR': 'R', 'LL': 'L'}

# ---------------------------------------------------------------- mass split (ASM-A5-MASS-SPLIT, team/A5/cad_claims.py)
SPAR_G = round(V('wing.spar.mass_per_m_kgm', 'kg/m') * V('wing.spar.length_m', 'm') * 1000.0, 1)   # 102 g
# fins (R3): tube from the spar's mass per metre (same 22 x 20 CF); the printed and CF parts at D3's R3 CAD unit
# masses (subsystems/fins/parts.csv, rounded, EST); each half-fin carries the rest (two-layer board, edge strips,
# pins, ESC pad, plug share, fillets)
FIN_TUBE_G = round(V('wing.spar.mass_per_m_kgm', 'kg/m') * V('fins.tube.length_m', 'm') * 1000.0, 1)   # 35.1 g
FIN_MOUNT_G, FIN_BLOCK_G, FIN_COLLAR_G, FIN_BRACE_G, FIN_ANCHOR_G = 11.0, 41.0, 10.6, 5.2, 3.2       # each
HALF_FIN_G = (A('fins') - 2 * FIN_TUBE_G - 2 * FIN_BLOCK_G
              - 4 * (FIN_MOUNT_G + FIN_COLLAR_G + FIN_BRACE_G + FIN_ANCHOR_G)) / 4
PROP_G = round(V('propulsion.prop_mass_kg', 'kg') * 1000.0, 1)                       # 17 g
MOTOR_G = A('propulsion') / 4 - PROP_G                                               # motor + ESC + adapter + nut
PACK_G = round(V('battery.mass_kg', 'kg') * 1000.0, 1)                               # 550 g
BOX_G = V('mass.transport_box_kg', 'kg') * 1000.0                                    # ground item, flight: false
CRADLE_G, TRAY_G = 75.0, 150.0


def wing_split(params, coords):
    """Wing allocation minus the spar -> (core, elevon inboard, elevon outboard) masses, g. The packing-tape skin
    (params wing.skin.areal_mass_kgm2, both sides, x1.02) goes by planform area, the rest (foam, fill, consumables)
    by volume of the section loops. Shared with team/A5/cad_claims.py so the closed form and the CAD agree."""
    v = lambda k: k9.val(params, k)
    c, b, hf = v('wing.chord_m'), v('wing.span_m'), k9.hinge_frac(params)
    cs = v('mass.allocation_g.wing') - v('wing.spar.mass_per_m_kgm') * v('wing.spar.length_m') * 1000.0
    skin = min(cs, v('wing.skin.areal_mass_kgm2') * 2 * c * b * 1.02 * 1000.0)
    import fusionkit as fk
    af = fk.poly_area_centroid(k9.section_loop(coords, c, (0.0, 0.0), 0.0, hf, 32))[0]
    aa = fk.poly_area_centroid(k9.section_loop(coords, c, (0.0, 0.0), hf, 1.0, 8))[0]
    out = []
    for y0, y1 in (v('wing.elevon.inboard_y_m'), v('wing.elevon.outboard_y_m')):
        L = y1 - y0
        out.append(round((cs - skin) * aa * L / ((af + aa) * b) + skin * (1 - hf) * L / b, 1))
    return cs - 2 * sum(out), out[0], out[1]


CORE, ELI, ELO = wing_split(P, k9.section(P)[0])
FOAM = 'XPS foam F-250 + packing-tape skin'
CF = 'CF tube 22x20 (bought)'
PETG = 'PETG (printed)'
ASA = 'ASA (printed)'
CFS = 'CF strip 10x3, pultruded (bought)'
BOARD = 'foam board 4.8 mm, paper faced'


def part(pid, name, mass, material, mob='make', flight=True):
    p = {'id': pid, 'name': name, 'subsystem': None, 'status': 'MODELLED', 'mass_g': mass, 'material': material,
         'cg_xyz_m': None, 'make_or_buy': mob, 'notes': 'skeleton envelope (A5); mass from the allocation'}
    if not flight:
        p['flight'] = False
        p['notes'] = 'skeleton envelope (A5); ground item, mass from params.json#mass.transport_box_kg'
    return p


def edge(eid, a, b, via, owner, notes='', **kw):
    e = {'id': eid, 'part_a': a, 'part_b': b, 'via': via, 'owner': owner, 'notes': notes}
    e.update(kw)
    return e


MOTOR_STACK = {'fastener': 'M3x8 SHCS', 'count': 4, 'grade': 'A2-70', 'hole': '3.4 mm clearance in the printed mount',
               'insert': 'none (motor base tapped M3, maker pattern)', 'engagement_mm': 4.0, 'min_engagement_mm': 3.0,
               'washer_nut': 'M3 washer', 'torque': 'snug + blue threadlocker', 'tool': '2.5 mm hex key',
               'access': 'from +x through the mount, before the mount is clamped on the tube',
               'install_order': 2, 'removal_order': 1}

PROP_STACK = {'fastener': 'M6x1 hex nut ISO 4032 (LH on the CW motors) + M6 washer', 'count': 1, 'grade': '8 (steel)',
              'hole': '6.35 mm prop bore with adapter ring to 6 mm', 'insert': 'none (threaded aluminium post)',
              'engagement_mm': 5.3, 'min_engagement_mm': 5.2, 'washer_nut': 'M6 washer under the nut',
              'torque': '1.5 N m EST (nylon hub)', 'tool': '10 mm spanner (D-40, the one field tool)',
              'access': 'from the front (-x)', 'install_order': 3, 'removal_order': 1}
PROP = str(V('propulsion.prop')).split(' (')[0].split('/')[0]          # "APC 11x5.5MR"
SPEC = {
    'wing': {
        'parts': [part('WNG-901', 'Wing core (one piece, elevons cut out)', CORE, FOAM),
                  part('WNG-902', 'Spar CF 22x20x1000', SPAR_G, CF, 'buy')] +
                 [part('WNG-903-' + s, 'Elevon inboard ' + s, ELI, FOAM) for s in 'RL'] +
                 [part('WNG-904-' + s, 'Elevon outboard ' + s, ELO, FOAM) for s in 'RL'],
        'edges': [edge('E-WNG-901', 'WNG-902', 'WNG-901', 'CT-EPOXY', 'wing', 'spar in the hot-wired slot')] +
                 [edge('E-WNG-%d' % (902 + i), p, 'WNG-901', 'CT-TAPE-HINGE', 'wing', 'upper-surface tape hinge',
                       motion={'axis': 'Y', 'range_deg': list(V('wing.elevon.deflection_deg'))})
                  for i, p in enumerate(('WNG-903-R', 'WNG-904-R', 'WNG-903-L', 'WNG-904-L'))],
        'acknowledges': ['E-FIN-%d' % n for n in (905, 906, 907, 908, 909, 910, 911, 912, 939, 940, 941, 942)] +
                        ['E-POD-901', 'E-MEC-901', 'E-MEC-902', 'E-HRN-901', 'E-HRN-902', 'E-TRN-904', 'E-TRN-905']},
    'fins': {
        'parts': [part('FIN-901-' + s, 'Half-fin %s (2-layer foam board, edge strips, pins, ESC pad)' % s,
                       HALF_FIN_G, BOARD) for s in ST] +
                 [part('FIN-902-' + s, 'Motor tube %s CF 22x20x%.0f (through the core)'
                       % (s, V('fins.tube.length_m', 'm') * 1000), FIN_TUBE_G, CF, 'buy') for s in 'RL'] +
                 [part('FIN-903-' + s, 'Motor mount %s (slip clamp on the tube end, canted plate)' % s, FIN_MOUNT_G, ASA)
                  for s in ST] +
                 [part('FIN-904-' + s, 'Through-core block %s (tube + spar bores)' % s, FIN_BLOCK_G, PETG) for s in 'RL'] +
                 [part('FIN-905-' + s, 'Station collar %s (ring, brace ear, two-face tail)' % s, FIN_COLLAR_G, PETG)
                  for s in ST] +
                 [part('FIN-906-' + s, 'Brace %s CF strip, DX-COLLAR to DX-ANCHOR' % s, FIN_BRACE_G, CFS, 'buy')
                  for s in ST] +
                 [part('FIN-907-' + s, 'Brace anchor %s on the spar' % s, FIN_ANCHOR_G, PETG) for s in ST],
        'edges': [edge('E-FIN-%d' % (901 + i), 'FIN-901-' + s, 'FIN-902-' + SIDE[s], 'CT-EPOXY', 'fins',
                       'half-fin LE bonded to the tube') for i, s in enumerate(ST)] +
                 [edge('E-FIN-%d' % (905 + i), 'FIN-901-' + s, 'WNG-901', 'CT-EPOXY', 'fins',
                       'half-fin root bonded + taped to the skin') for i, s in enumerate(ST)] +
                 [edge('E-FIN-%d' % (909 + i), 'FIN-904-' + s, 'WNG-901', 'CT-EPOXY', 'fins', 'block bonded in the core cut-out')
                  for i, s in enumerate('RL')] +
                 [edge('E-FIN-%d' % (911 + i), 'FIN-904-' + s, 'WNG-902', 'CT-EPOXY', 'fins', 'spar through the block bore')
                  for i, s in enumerate('RL')] +
                 [edge('E-FIN-%d' % (913 + i), 'FIN-904-' + s, 'FIN-902-' + s, 'CT-EPOXY', 'fins', 'tube through the block bore')
                  for i, s in enumerate('RL')] +
                 [edge('E-FIN-%d' % (915 + i), 'FIN-903-' + s, 'FIN-902-' + SIDE[s], 'CT-TUBE-CLAMP', 'fins',
                       'slit collar clamped on the tube end (slip clamp, D-23 fuse)') for i, s in enumerate(ST)] +
                 [edge('E-FIN-%d' % (919 + i), 'PRP-901-' + s, 'FIN-903-' + s, 'CT-M3-SHCS-MOTOR', 'fins',
                       'example joint stack; C6 sizes', joint_stack=MOTOR_STACK) for i, s in enumerate(ST)] +
                 [edge('E-FIN-%d' % (923 + i), 'PRP-901-' + s, 'FIN-903-' + s, 'CT-THERMAL-CONTACT', 'fins',
                       'motor base heat into the printed ASA mount (D-42); registered with ctx.contact')
                  for i, s in enumerate(ST)] +
                 [edge('E-FIN-%d' % (927 + i), 'FIN-905-' + s, 'FIN-902-' + SIDE[s], 'CT-EPOXY', 'fins',
                       'station collar bonded on the tube under the mount') for i, s in enumerate(ST)] +
                 [edge('E-FIN-%d' % (931 + i), 'FIN-906-' + s, 'FIN-905-' + s, 'CT-EPOXY', 'fins',
                       'brace end bonded in the collar ear slot') for i, s in enumerate(ST)] +
                 [edge('E-FIN-%d' % (935 + i), 'FIN-906-' + s, 'FIN-907-' + s, 'CT-EPOXY', 'fins',
                       'brace end bonded in the anchor slot') for i, s in enumerate(ST)] +
                 [edge('E-FIN-%d' % (939 + i), 'FIN-907-' + s, 'WNG-902', 'CT-EPOXY', 'fins',
                       'anchor foot bonded on the spar through a core pocket') for i, s in enumerate(ST)] +
                 [edge('E-FIN-%d' % (943 + i), 'FIN-905-' + s, 'FIN-901-' + s, 'CT-EPOXY', 'fins',
                       'collar tail tongue bonded in the notched LE-top corner') for i, s in enumerate(ST)],
        'acknowledges': ['E-GER-%d' % (901 + i) for i in range(4)] + ['E-HRN-903', 'E-HRN-904']},
    'propulsion': {
        'parts': [part('PRP-901-' + s, 'Motor %s X3108S (+ ESC, adapter, nut lumped)' % s, MOTOR_G, 'motor (bought)', 'buy')
                  for s in ST] +
                 [part('PRP-902-' + s, 'Prop %s %s (disc)' % (s, PROP), PROP_G, 'nylon-glass prop (bought)', 'buy')
                  for s in ST],
        'edges': [edge('E-PRP-%d' % (901 + i), 'PRP-902-' + s, 'PRP-901-' + s, 'CT-PROP-NUT', 'propulsion',
                       'prop on the adapter post (adapter lumped in the motor); field joint, example stack from E1',
                       field_joint=True, joint_stack=PROP_STACK) for i, s in enumerate(ST)],
        'acknowledges': ['E-FIN-%d' % (919 + i) for i in range(8)] + ['E-TRN-%d' % (906 + i) for i in range(4)]},
    'landing': {
        'parts': [part('GER-901-' + s, 'Foot %s (crush cartridge, %.0f mm, splayed pad)' % (s, V('cg.foot_height_m', 'm') * 1000),
                       A('landing') / 4, 'PETG shoe + piston, XPS cartridge, neoprene pad')
                  for s in ST],
        'edges': [edge('E-GER-%d' % (901 + i), 'GER-901-' + s, 'FIN-901-' + s, 'CT-EPOXY', 'landing',
                       'cap bonded on the half-fin TE tip') for i, s in enumerate(ST)]},
    'pod': {
        'parts': [part('POD-901', 'Pod shell + tray + hatch (envelope)', A('pod'), 'foam board + PETG')],
        'edges': [edge('E-POD-901', 'POD-901', 'WNG-901', 'CT-EPOXY', 'pod', 'bonded + strapped')],
        'acknowledges': ['E-PWR-901', 'E-PWR-902', 'E-AVN-901']},
    'power': {
        'parts': [part('PWR-901', 'Flight pack 4S 6500 (envelope at the D-24 station)', PACK_G, 'LiPo', 'buy'),
                  part('PWR-902', 'Disconnect, main leads, UBEC (lump)', A('power') - PACK_G, 'copper + PVC', 'buy')],
        'edges': [edge('E-PWR-901', 'PWR-901', 'POD-901', 'CT-STRAP-VELCRO', 'power'),
                  edge('E-PWR-902', 'PWR-902', 'POD-901', 'CT-CA', 'power', 'foam tape (bond)')]},
    'avionics': {
        'parts': [part('AVN-901', 'Avionics lump (FC, GPS, RX, airspeed)', A('avionics'), 'electronics (bought)', 'buy')],
        'edges': [edge('E-AVN-901', 'AVN-901', 'POD-901', 'CT-CA', 'avionics', 'foam tape (bond)')]},
    'mechanisms': {
        'parts': [part('MEC-901-' + s, 'Elevon servo %s + horn + pushrod + link (lump)' % s, A('mechanisms') / 2,
                       'servo (bought)', 'buy') for s in 'RL'],
        'edges': [edge('E-MEC-%d' % (901 + i), 'MEC-901-' + s, 'WNG-901', 'CT-EPOXY', 'mechanisms',
                       'printed frame bonded in the core pocket') for i, s in enumerate('RL')]},
    'harness': {
        'parts': [part('HRN-901-' + s, 'Wing-fin harness bundle %s (lumped mass, k09kit.bundle body)' % s,
                       A('harness') / 2, 'copper + silicone') for s in 'RL'],
        'edges': [edge('E-HRN-%d' % (901 + i), 'HRN-901-' + s, 'WNG-901', 'CT-CA', 'harness',
                       'taped in the channel aft of the spar (CR-A4-05: F2/D1 fix x)') for i, s in enumerate('RL')] +
                 [edge('E-HRN-%d' % (903 + i), 'HRN-901-' + s, 'FIN-902-' + s, 'CT-CA', 'harness',
                       'tied along the tube inboard face, clear of the prop discs') for i, s in enumerate('RL')]},
    'transport': {
        'parts': [part('TRN-901', 'Transport box %s (six walls, lining lumped)' % ' x '.join('%.2f' % d for d in
                                                                            V('requirements.box_external_m', 'm')),
                       BOX_G - 2 * CRADLE_G - TRAY_G, 'corrugated PP + PE foam lining', flight=False)] +
                 [part('TRN-902-' + s, 'Spar cradle %s (crush foam >= 70 mm)' % s, CRADLE_G, 'PE foam', flight=False)
                  for s in 'RL'] +
                 [part('TRN-903', 'Prop tray (4 slots)', TRAY_G, 'PE foam', flight=False)],
        'edges': [edge('E-TRN-901', 'TRN-902-R', 'TRN-901', 'CT-EPOXY', 'transport', 'cradle bonded to the floor'),
                  edge('E-TRN-902', 'TRN-902-L', 'TRN-901', 'CT-EPOXY', 'transport', 'cradle bonded to the floor'),
                  edge('E-TRN-903', 'TRN-903', 'TRN-901', 'CT-EPOXY', 'transport', 'tray bonded to the floor')] +
                 [edge('E-TRN-%d' % (904 + i), 'TRN-902-' + s, 'WNG-901', 'CT-CRADLE-CONTACT', 'transport',
                       'wing lower skin rests on the cradle under the spar; fins and tubes never pressed')
                  for i, s in enumerate('RL')] +
                 [edge('E-TRN-%d' % (906 + i), 'PRP-902-' + s, 'TRN-903', 'CT-CRADLE-CONTACT', 'transport',
                       'prop off for transport, one slot each', stowed=True) for i, s in enumerate(ST)]},
}


def write_interfaces():
    for sub, s in SPEC.items():
        os.makedirs(os.path.join(HERE, sub), exist_ok=True)
        doc = {'schema': 'dbf-interfaces/1', 'subsystem': sub,
               '_note': 'GENERATED by redesign/fusion/skeleton/make_skeleton.py - K09-L skeleton (params %s, '
                        'geometry R3), not the design' % V('meta.revision'),
               'parts': [dict(p, subsystem=sub) for p in s['parts']]}
        if s.get('connection_types'):
            doc['connection_types'] = s['connection_types']
        doc['edges'] = s['edges']
        doc['acknowledges'] = s.get('acknowledges', [])
        with open(os.path.join(HERE, sub, 'interfaces.json'), 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, indent=1)
            f.write('\n')


def fill_cg():
    ctx, _, results = build_all.build(StubBackend(), HERE, os.path.join(HERE, 'modules.txt'), log=lambda *a: None)
    bad = [r for r in results if not r[2]]
    if bad:
        raise SystemExit('skeleton build failed: %s' % bad)
    for sub in SPEC:
        path = os.path.join(HERE, sub, 'interfaces.json')
        with open(path, encoding='utf-8') as f:
            doc = json.load(f)
        for p in doc['parts']:
            c = ctx.components[p['id']]
            p['cg_xyz_m'] = [round(v, 4) for v in c.volume_centroid()[1]]
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, indent=1)
            f.write('\n')
    return ctx


def main():
    shutil.copyfile(os.path.join(FUSION, 'modules.txt'), os.path.join(HERE, 'modules.txt'))
    flight = [k for k in SPEC if k != 'transport']
    budget = {'_note': 'GENERATED by make_skeleton.py from params.json: limit and allocations as params/mass_budget.json. '
                       'cg_x_m is left out on purpose: the skeleton CG is reported as claim CL-A5-LAYOUT-CG-X '
                       '(team/A5/claims.json), not a pass/fail gate of the framework test.',
              'limit_g': round(V('requirements.mtow_gate_kg') * 1000),
              'allocations_g': {k: A(k) for k in flight}}
    with open(os.path.join(HERE, 'mass_budget.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(budget, f, indent=1)
        f.write('\n')
    write_interfaces()
    ctx = fill_cg()
    M, cg = ctx.rollup()
    print('skeleton: %d parts (%d flight), %.1f g flight, CG %s m; half-fin %.1f g, tube %.1f g, motor lump %.1f g, '
          'elevons %.1f / %.1f g' % (len(ctx.components), sum(1 for c in ctx.components.values() if c.flight), M,
                                     ', '.join('%.4f' % v for v in cg), HALF_FIN_G, FIN_TUBE_G, MOTOR_G, ELI, ELO))
    return 0


if __name__ == '__main__':
    sys.exit(main())
