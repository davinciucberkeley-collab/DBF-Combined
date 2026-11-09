"""Generate the K09-L skeleton's interfaces.json files, modules.txt and mass_budget.json, then fill every part's
cg_xyz_m from its CAD centroid (stub build). Owner: A5.

    python -I redesign/fusion/skeleton/make_skeleton.py

The skeleton is the reference layout every designer starts from: one envelope per part at the DATUMS.md stations,
masses split from params.json#mass.allocation_g (sum = 2 132 g, growth reserve not placed), part ids <PREFIX>-9xx
(9xx is reserved for the skeleton; real subsystems number from 001). It is not the design. Re-run after any
params.json change, then python -I redesign/fusion/check.py --skeleton --strict.
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


def elevon_masses():
    """Core+tape+consumables (the wing allocation minus the spar) split by planform area."""
    cs = A('wing') - 102.0                                                  # spar 102 g (allocation note)
    c, b, f = k9.val(P, 'wing.chord_m'), k9.val(P, 'wing.span_m'), k9.val(P, 'wing.elevon.chord_frac')
    yi, yo = k9.val(P, 'wing.elevon.inboard_y_m'), k9.val(P, 'wing.elevon.outboard_y_m')
    mi = round(cs * (yi[1] - yi[0]) * f * c / (b * c))           # whole grams: the roll-up stays exact
    mo = round(cs * (yo[1] - yo[0]) * f * c / (b * c))
    return cs - 2 * (mi + mo), float(mi), float(mo)


CORE, ELI, ELO = elevon_masses()
FOAM = 'XPS foam F-250 + packing-tape skin'
CF = 'CF tube 22x20 (bought)'
PETG = 'PETG (printed)'
STATIONS = k9.STATIONS


def part(pid, name, mass, material, mob='make', sub=None):
    return {'id': pid, 'name': name, 'subsystem': sub, 'status': 'MODELLED', 'mass_g': mass, 'material': material,
            'cg_xyz_m': None, 'make_or_buy': mob, 'notes': 'skeleton envelope (A5); mass from the allocation'}


def edge(eid, a, b, via, owner, notes='', **kw):
    e = {'id': eid, 'part_a': a, 'part_b': b, 'via': via, 'owner': owner, 'notes': notes}
    e.update(kw)
    return e


MOTOR_STACK = {'fastener': 'M3x8 SHCS', 'count': 4, 'grade': 'A2-70', 'hole': '3.4 mm clearance in the printed mount',
               'insert': 'none (motor base tapped M3, maker pattern)', 'engagement_mm': 4.0, 'min_engagement_mm': 3.0,
               'washer_nut': 'M3 washer', 'torque': 'snug + blue threadlocker', 'tool': '2.5 mm hex key',
               'access': 'from +x through the mount, before the mount is clamped on the tube',
               'install_order': 2, 'removal_order': 1}

SPEC = {
    'wing': {
        'parts': [part('WNG-901', 'Wing core (one piece, elevons cut out)', CORE, FOAM),
                  part('WNG-902', 'Spar CF 22x20x1000', 102.0, CF, 'buy'),
                  part('WNG-903', 'Elevon R inboard', ELI, FOAM), part('WNG-904', 'Elevon R outboard', ELO, FOAM),
                  part('WNG-905', 'Elevon L inboard', ELI, FOAM), part('WNG-906', 'Elevon L outboard', ELO, FOAM)],
        'edges': [edge('E-WNG-901', 'WNG-902', 'WNG-901', 'CT-EPOXY', 'wing', 'spar in slot')] +
                 [edge('E-WNG-%d' % (902 + i), p, 'WNG-901', 'CT-TAPE-HINGE', 'wing', 'upper-surface tape hinge',
                       motion={'axis': 'Y', 'range_deg': list(k9.val(P, 'wing.elevon.deflection_deg'))})
                  for i, p in enumerate(('WNG-903', 'WNG-904', 'WNG-905', 'WNG-906'))],
        'acknowledges': ['E-FIN-905', 'E-FIN-906', 'E-FIN-907', 'E-FIN-908', 'E-POD-901', 'E-MEC-901', 'E-MEC-902',
                         'E-HRN-901', 'E-HRN-902']},
    'fins': {
        'parts': [part('FIN-901', 'Fin R (2-layer foam board, clips + epoxy lumped)', 111.0, 'foam board 4.8 mm, paper faced'),
                  part('FIN-902', 'Fin L (2-layer foam board, clips + epoxy lumped)', 111.0, 'foam board 4.8 mm, paper faced'),
                  part('FIN-903', 'Motor tube R CF 22x20x420', 43.0, CF, 'buy'),
                  part('FIN-904', 'Motor tube L CF 22x20x420', 43.0, CF, 'buy')] +
                 [part('FIN-%d' % (905 + i), 'Motor mount ' + s, 18.0, PETG) for i, s in enumerate(STATIONS)] +
                 [part('FIN-909', 'Tube-to-spar saddle R', 15.0, PETG), part('FIN-910', 'Tube-to-spar saddle L', 15.0, PETG)],
        'edges': [edge('E-FIN-901', 'FIN-901', 'FIN-903', 'CT-EPOXY', 'fins', 'printed clips + epoxy'),
                  edge('E-FIN-902', 'FIN-902', 'FIN-904', 'CT-EPOXY', 'fins', 'printed clips + epoxy'),
                  edge('E-FIN-903', 'FIN-909', 'FIN-903', 'CT-EPOXY', 'fins'),
                  edge('E-FIN-904', 'FIN-910', 'FIN-904', 'CT-EPOXY', 'fins'),
                  edge('E-FIN-905', 'FIN-909', 'WNG-902', 'CT-EPOXY', 'fins', 'bonded + strapped'),
                  edge('E-FIN-906', 'FIN-910', 'WNG-902', 'CT-EPOXY', 'fins', 'bonded + strapped'),
                  edge('E-FIN-907', 'FIN-901', 'WNG-901', 'CT-EPOXY', 'fins', 'fin root bonded + taped'),
                  edge('E-FIN-908', 'FIN-902', 'WNG-901', 'CT-EPOXY', 'fins', 'fin root bonded + taped')] +
                 [edge('E-FIN-%d' % (909 + i), 'FIN-%d' % (905 + i), 'FIN-903' if s[1] == 'R' else 'FIN-904',
                       'CT-TUBE-CLAMP', 'fins', 'split clamp on the tube end') for i, s in enumerate(STATIONS)] +
                 [edge('E-FIN-%d' % (913 + i), 'PRP-%d' % (901 + i), 'FIN-%d' % (905 + i), 'CT-M3-SHCS-MOTOR', 'fins',
                       'example joint stack; C6 sizes', joint_stack=MOTOR_STACK) for i in range(4)],
        'acknowledges': ['E-GER-901', 'E-GER-902', 'E-GER-903', 'E-GER-904']},
    'propulsion': {
        'parts': [part('PRP-%d' % (901 + i), 'Motor %s X3108S (+ ESC lumped)' % s, 87.5, 'motor (bought)', 'buy')
                  for i, s in enumerate(STATIONS)] +
                 [part('PRP-%d' % (905 + i), 'Prop %s APC 11x4.5MR (disc)' % s, 20.0, 'nylon-glass prop (bought)', 'buy')
                  for i, s in enumerate(STATIONS)],
        'connection_types': [{'id': 'CT-PROP-ADAPTER', 'kind': 'mechanical', 'method': 'clamped',
                              'spec': 'prop adapter (collet) + prop nut, per motor maker'}],
        'edges': [edge('E-PRP-%d' % (901 + i), 'PRP-%d' % (905 + i), 'PRP-%d' % (901 + i), 'CT-PROP-ADAPTER',
                       'propulsion') for i in range(4)],
        'acknowledges': ['E-FIN-913', 'E-FIN-914', 'E-FIN-915', 'E-FIN-916']},
    'landing': {
        'parts': [part('GER-%d' % (901 + i), 'Foot ' + s, A('landing') / 4, 'TPU or PETG (printed, crushable)')
                  for i, s in enumerate(STATIONS)],
        'edges': [edge('E-GER-%d' % (901 + i), 'GER-%d' % (901 + i), 'FIN-901' if s[1] == 'R' else 'FIN-902',
                       'CT-EPOXY', 'landing', 'cap bonded on the fin TE tip') for i, s in enumerate(STATIONS)]},
    'pod': {
        'parts': [part('POD-901', 'Pod shell + tray + hatch (envelope)', A('pod'), 'foam board + PETG')],
        'edges': [edge('E-POD-901', 'POD-901', 'WNG-901', 'CT-EPOXY', 'pod', 'bonded + strapped')],
        'acknowledges': ['E-PWR-901', 'E-PWR-902', 'E-AVN-901']},
    'power': {
        'parts': [part('PWR-901', 'Flight pack 4S 6500 (envelope)', 550.0, 'LiPo', 'buy'),
                  part('PWR-902', 'Disconnect, main leads, UBEC (lump)', A('power') - 550.0, 'copper + PVC', 'buy')],
        'edges': [edge('E-PWR-901', 'PWR-901', 'POD-901', 'CT-STRAP-VELCRO', 'power'),
                  edge('E-PWR-902', 'PWR-902', 'POD-901', 'CT-CA', 'power', 'foam tape (bond)')]},
    'avionics': {
        'parts': [part('AVN-901', 'Avionics lump (FC, GPS, RX, airspeed)', A('avionics'), 'electronics (bought)', 'buy')],
        'edges': [edge('E-AVN-901', 'AVN-901', 'POD-901', 'CT-CA', 'avionics', 'foam tape (bond)')]},
    'mechanisms': {
        'parts': [part('MEC-901', 'Elevon servo R + horn + pushrod (lump)', A('mechanisms') / 2, 'servo (bought)', 'buy'),
                  part('MEC-902', 'Elevon servo L + horn + pushrod (lump)', A('mechanisms') / 2, 'servo (bought)', 'buy')],
        'edges': [edge('E-MEC-901', 'MEC-901', 'WNG-901', 'CT-EPOXY', 'mechanisms', 'printed frame bonded in pocket'),
                  edge('E-MEC-902', 'MEC-902', 'WNG-901', 'CT-EPOXY', 'mechanisms', 'printed frame bonded in pocket')]},
    'harness': {
        'parts': [part('HRN-901', 'Harness R (lump)', A('harness') / 2, 'copper + silicone'),
                  part('HRN-902', 'Harness L (lump)', A('harness') / 2, 'copper + silicone')],
        'edges': [edge('E-HRN-901', 'HRN-901', 'WNG-901', 'CT-CA', 'harness', 'taped to the skin (bond)'),
                  edge('E-HRN-902', 'HRN-902', 'WNG-901', 'CT-CA', 'harness', 'taped to the skin (bond)')]},
}


def write_interfaces():
    for sub, s in SPEC.items():
        doc = {'schema': 'dbf-interfaces/1', 'subsystem': sub,
               '_note': 'GENERATED by redesign/fusion/skeleton/make_skeleton.py - K09-L skeleton, not the design',
               'parts': [dict(p, subsystem=sub) for p in s['parts']]}
        if s.get('connection_types'):
            doc['connection_types'] = s['connection_types']
        doc['edges'] = s['edges']
        doc['acknowledges'] = s.get('acknowledges', [])
        path = os.path.join(HERE, sub, 'interfaces.json')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
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
    budget = {'_note': 'GENERATED by make_skeleton.py from params.json: limit and allocations as params/mass_budget.json. '
                       'cg_x_m is left out on purpose: the skeleton CG is reported as claim CL-A5-LAYOUT-CG-X '
                       '(team/A5/claims.json), not a pass/fail gate of the framework test.',
              'limit_g': round(k9.val(P, 'requirements.mtow_gate_kg') * 1000),
              'allocations_g': {k: A(k) for k in SPEC}}
    with open(os.path.join(HERE, 'mass_budget.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(budget, f, indent=1)
        f.write('\n')
    write_interfaces()
    ctx = fill_cg()
    M, cg = ctx.rollup()
    print('skeleton: %d parts, %.1f g, CG %s m; elevon panels %.1f / %.1f g, core %.1f g' % (
        len(ctx.components), M, ', '.join('%.4f' % v for v in cg), ELI, ELO, CORE))
    return 0


if __name__ == '__main__':
    sys.exit(main())
