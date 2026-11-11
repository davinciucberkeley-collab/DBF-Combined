"""Write subsystems/power/interfaces.json and parts.csv from one table (F1, PWR-R1).

    python -I redesign/subsystems/power/make_power.py

Masses come from params.json (pack) and subsystems/power/params.json (everything else); CGs are the centroid of
each part's main body in fusion/power.py#layout(), so the CAD, the graph and the BOM agree. Edit this file, not the
outputs.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, 'fusion'))
sys.path.insert(0, os.path.join(RED, 'fusion'))
import power as pw  # noqa: E402

ST = ('UR', 'UL', 'LR', 'LL')


def _load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


P = _load(os.path.join(RED, 'params', 'params.json'))
LP = _load(os.path.join(HERE, 'params.json'))['power']
L = {k: d['value'] for k, d in LP.items()}
POD = {k: v['value'] for k, v in _load(os.path.join(RED, 'subsystems', 'pod', 'params.json')).items()
       if isinstance(v, dict) and 'value' in v}
FIN = _load(os.path.join(RED, 'subsystems', 'fins', 'params.json'))['fin_detail']['esc_pad']


def get(key, unit=None):
    d = P
    for k in key.split('.'):
        d = d[k]
    if unit is not None and d.get('unit') != unit:
        raise KeyError('%s is in %s, not %s' % (key, d.get('unit'), unit))
    return d['value']


G = pw.layout(get, L, POD)
c = lambda b: [round((b[0][i] + b[1][i]) / 2, 4) for i in range(3)]


def frame_cg():
    """Volume-weighted centroid of the frame boxes (the deck window is small and near the deck centroid)."""
    boxes = [G['deck'], G['cradle_floor'], G['front_wall']] + G['side_walls'] + G['legs']
    vol = lambda b: (b[1][0] - b[0][0]) * (b[1][1] - b[0][1]) * (b[1][2] - b[0][2])
    vt = sum(vol(b) for b in boxes)
    return [round(sum(vol(b) * (b[0][i] + b[1][i]) / 2 for b in boxes) / vt, 4) for i in range(3)]


def jumper_mass_g():
    od, _r, gpm = L['wire_10awg']
    return round(2 * sum(L['jumper_len_m']) * gpm, 1)       # + and - conductors, W-MAIN-1 and W-MAIN-2


def cap_cg(st):
    x0 = FIN['x0_m']['value'] + FIN['len_m']['value'] + L['cap_gap_x_m']
    face = get('fins.y_m', 'm') + get('fins.layers', '-') * get('fins.board_t_m', 'm') / 2
    sy, sz = (1 if st[1] == 'R' else -1), (1 if st[0] == 'U' else -1)
    return [round(x0 + L['cap_m'][0] / 2, 4), round(sy * (face + L['cap_m'][1] / 2), 4), round(sz * FIN['z_m']['value'], 4)]


AS_G = round(L['as150u_mass_g'] + jumper_mass_g(), 1)
PARTS = [
    # id, name, make/buy, process, material, mass_g, electrical, cg, cost, vendor, notes
    ('PWR-001', 'Flight pack 4S 6500 mAh (re-terminated AS150U, own 10 AWG leads 0.10 m)', 'buy', 're-terminate (solder AS150U pack half)',
     'LiPo', round(get('battery.mass_kg', 'kg') * 1000, 1), 'source', [round(v, 4) for v in G['pack_c']], 41.49,
     'team/I1/BOM.csv#P01 (Ovonic 4S 6500 130C 2-pack $82.97)',
     'mass UNVERIFIED (listings 503-680 g, weigh on arrival); CG = pack centroid at the D-24 station; the body also shows the leads and the AS150U pack half'),
    ('PWR-002', 'Main disconnect AS150U aircraft half + two 10 AWG main jumpers', 'buy', 'solder, bond into PWR-006',
     'electronics (bought)', AS_G, 'bus', c(G['as_air']), 5.0, 'team/I1/BOM.csv#F01 (Amass AS150U pair)',
     'AS150U half %.1f g EST + 10 AWG jumpers %.1f g (W-MAIN-1 0.030 m + W-MAIN-2 0.050 m, + and -); the wires are harness edges E-HRN-11/12, their mass is booked here (CR-F1-18)' % (L['as150u_mass_g'], jumper_mass_g())),
    ('PWR-003', 'Power module: CoreWing F405 Wing V2 power board (V/I sense, servo BEC), separated from the FC stack', 'buy', 'separate from the stack, set the servo-BEC jumper to 6 V, foam-tape on PWR-006',
     'electronics (bought)', L['board_mass_g'], 'bus', c(G['board']), 0.0, 'team/I1/BOM.csv#A01 (part of the CoreWing V2 stack, F3)',
     '90 A cont / 215 A peak sense, 64 A/V (CL-F3-SENSE-*; CoreWing manual V2.1); servo BEC 8 A cont / 14 A peak on the 6 V jumper feeds the elevon servos through the FC Vx rail (D-74, CL-F1-SERVO-BEC-RATING; Vx >= 5.8 V at BOARD-CHECK.md step 7); outline 52 x 32 mm (manual), M2 holes 30.5 x 26.5; drawn 52 mm pads-aft in keep-out KO-PWR-BOARD 56 x 34 x 24 mm (deck re-drawn to it, D-74), fits split (PDB alone) and whole stack (SPEC.md); height and link pitch measured at BOARD-CHECK.md; mass ~28 g EST (listing 11.4 g) moved from AVN-001 (F3 CR-F3-13, CR-F1-19)'),
    ('PWR-004', 'Bus board: FR4 strip with two tinned 8 AWG bus bars (+ / -)', 'make', 'shear FR4, file isolation slot, solder bars',
     'FR4 + copper (made)', L['bus_mass_g'], 'bus', c(G['bus']), 3.0, 'FR4 1 oz single-sided sheet + 8 AWG offcut (team/I1/BOM.csv#F02, F08 replaced)',
     '4 ESC pigtails (XT30U female at the pod side exits, D-74) and the main input solder to the bars on the bench; 36 x 16 mm between D2 boss rows'),
    ('PWR-006', 'Power frame: deck on 4 spacers (56 x 34 mm board seat = KO-PWR-BOARD), wire window, AS150U cradle, legs (printed PETG)', 'make', 'FDM PETG, deck flat on the bed',
     'PETG (printed)', L['frame_mass_g'], None, frame_cg(), 1.5, 'subsystems/power/fusion/power.py (export STL)',
     'PETG 100 % (2 mm plates), 4 perimeters; screws, spacers, washers, tie and tape inside the mass; D-74: deck 42 -> 56 mm, fuse clip deleted'),
]
# D-74 (params/CHANGE-LOG.md): the UBEC PWR-005 and its 5 A fuse PWR-007 are deleted; the power board's servo BEC
# (6 V jumper) feeds the servos through the FC Vx rail. Fallback only if BOARD-CHECK.md step 7 fails (BOM gate X12):
# then F1 names a 4S-input UBEC and D2 gives it its own zone; the ids PWR-005 / PWR-007 stay retired.
CAPS = [('PWR-008-' + s, 'ESC capacitor 680 uF 25 V low-ESR, %s' % s, cap_cg(s)) for s in ST]

HARDWARE = [
    ('PWR-101', 'M3x18 pan head screw, nylon PA66', 6, 'buy', '-', 'nylon PA66', 0, 0.10, 'any (nylon M3 assortment)', '4 + 2 spare; mass inside PWR-006'),
    ('PWR-102', 'Nylon spacer M3, 10 mm, OD 6 / ID 3.2', 6, 'buy', '-', 'nylon PA66', 0, 0.10, 'any', '4 + 2 spare; mass inside PWR-006'),
    ('PWR-103', 'M3 nylon washer 0.5 mm', 6, 'buy', '-', 'nylon PA66', 0, 0.02, 'any', 'mass inside PWR-006'),
    ('PWR-104', 'Silicone wire 10 AWG red + black, 0.3 m each', 1, 'buy', '-', 'copper + silicone', 0, 4.0, 'team/I1/BOM.csv#F02 (replaces 8 AWG)', 'main jumpers; mass inside PWR-002'),
    ('PWR-105', 'FR4 sheet 1.6 mm, 1 oz copper one side, 100 x 70 mm', 1, 'buy', '-', 'FR4', 0, 3.0, 'any', 'bus board; 3 boards per sheet'),
    ('PWR-106', 'Foam tape 3M VHB-class 1.1 mm, 25 mm wide', 1, 'buy', '-', 'acrylic foam', 0, 0.0, 'shared shop stock', 'power board, bus board, caps; mass inside each part'),
    ('PWR-201', 'Second flight pack (ground: charge / rotate; flight false)', 1, 'buy', '-', 'LiPo', 0, 41.49, 'team/I1/BOM.csv#P01', 'not on the aircraft; 550 g in the LiPo bag, not in the flying roll-up'),
    ('PWR-202', 'AS150U-to-XT60 charge lead (built from F01 + H03)', 1, 'make', 'solder', 'copper + PA', 0, 0.0, 'team/I1/BOM.csv#H03', 'ground item; 6.5 A charge'),
]


def part(pid, name, mb, mat, mass, elec, cg, notes):
    d = {'id': pid, 'name': name, 'subsystem': 'power', 'status': 'MODELLED', 'mass_g': mass, 'material': mat,
         'cg_xyz_m': cg, 'make_or_buy': mb}
    if elec:
        d['electrical'] = elec
    d['notes'] = notes
    return d


def tape(item, load, insp, count=1):
    return {'item': item, 'count': count, 'load_n': load, 'inspection': insp}


def main():
    parts = [part(p[0], p[1], p[2], p[4], p[5], p[6], p[7], p[10]) for p in PARTS]
    parts += [part(i, n, 'buy', 'electronics (bought)', L['cap_mass_g'], 'sink', cg,
                   'at the ESC power pads, leads <= 20 mm; on the outboard face beside the ESC, never under its strap')
              for i, n, cg in CAPS]
    s = L['screw']
    eng = s['len_mm'] - s['washer_mm'] - s['deck_mm'] - s['spacer_mm']
    cts = [
        {'id': 'CT-CONN-PARK', 'kind': 'mechanical', 'method': 'bonded',
         'spec': 'connector half seated in a printed cradle: sanded housing bonded with 30 min epoxy, front wall takes the plug-in push, one cable tie over it as secondary retention'},
    ]
    edges = [
        {'id': 'E-PWR-01', 'part_a': 'PWR-002', 'part_b': 'PWR-006', 'via': 'CT-CONN-PARK', 'owner': 'power',
         'notes': 'AS150U aircraft half in the frame cradle (x %.3f ... %.3f, left channel); the cradle, not the 10 AWG cups, takes the plug and unplug force at every field set-up; plug reachable through the hatch with the pack in. Replaces the R2 slot in POD-002 (CR-F1-16)' % (G['as_air'][0][0], G['as_air'][1][0]),
         'bond': {'adhesive': '30 min epoxy (housing sanded 120 grit, IPA wipe)', 'area_mm2': L['cradle_bond_mm2'],
                  'prep': 'housing and cradle sanded; cups masked', 'cure': '24 h at >= 18 degC before the first plug-in',
                  'load_n': 'unplug %.0f N EST every flight (CL-PWR-PARK-RF)' % L['unplug_force_n'],
                  'load_case': 'field unplug / plug', 'sized_by': 'F1 (CALC-PWR-PARK)'},
         'retention': tape('1 nylon tie 2.5 mm through two floor slots over the housing', 'secondary', 'housing does not move when the pack half is pulled: pre-flight card')},
        {'id': 'E-PWR-02', 'part_a': 'PWR-003', 'part_b': 'PWR-006', 'via': 'CT-TAPE-FOAM', 'owner': 'power',
         'notes': 'power board on 3M foam tape on the deck, battery/output pads at the aft edge over the wire window; one tie round board and deck through two deck slots. Inside KO-PWR-BOARD (power SPEC.md); whole-stack fallback (case U): stack on 4 gel cubes + strap instead of tape. Replaces the R2 tape-to-tray (CR-F1-16); the frame screws sit under the board, so tape the board after E-PWR-03',
         'retention': tape('foam tape 1.1 mm, full underside + 1 tie', '28 g x 12.75 g crash = 3.5 N', 'board flat, tie tight: weekly')},
        {'id': 'E-PWR-03', 'part_a': 'PWR-006', 'part_b': 'POD-002', 'via': 'CT-M3-SHCS-INSERT', 'owner': 'power',
         'notes': 'frame deck on four 10 mm nylon spacers over D2\'s four PDB-plate bosses (25 mm pattern, inserts at z %.4f); nylon keeps the stack insulating next to the bus bars and non-magnetic. Supersedes the C6 M3x10 A2 stack drawn for a bought PCB (CR-F1-20)' % G['zboss'],
         'joint_stack': {'fastener': 'M3x%d pan head, nylon PA66' % s['len_mm'], 'count': 4, 'grade': 'PA66 nylon (insulating, non-magnetic)',
                         'hole': '3.4 mm clearance in the deck (PWR-006) and in the 10 mm nylon spacer (OD 6 / ID 3.2); POD-002 boss bore 4.0 x 6.5 mm with the insert',
                         'insert': 'M3 x 5.7 brass heat-set in POD-002 (D2)', 'engagement_mm': round(eng, 1), 'min_engagement_mm': 4.5,
                         'washer_nut': 'M3 nylon washer 0.5 mm under the head; spacer 10 mm under the deck',
                         'torque': '0.20 N m max (nylon), snug, no threadlocker; paint-pen witness',
                         'tool': 'PH1 screwdriver', 'access': 'from above (+z) through the hatch, before the power board is taped on (the board covers the heads)',
                         'install_order': 3, 'removal_order': 3}},
        {'id': 'E-PWR-05', 'part_a': 'PWR-004', 'part_b': 'POD-002', 'via': 'CT-TAPE-FOAM', 'owner': 'power',
         'notes': 'bus board on foam tape on the PDB plate between D2\'s boss rows, under the deck; every bar joint (4 ESC pigtails, W-MAIN-2) is soldered on the bench before the board goes in (D-74, BUILD.md step 3); the pigtails are tied to the tray within 80 mm (F2), so plug and lead pulls do not reach the tape',
         'retention': tape('foam tape 1.1 mm, full underside', '7.3 g x 12.75 g = 0.9 N; lead pulls taken by F2 ties', 'with the deck off (bench): board flat, no lifted corner')},
    ]
    for i, st in enumerate(ST):
        edges.append({'id': 'E-PWR-%d' % (11 + i), 'part_a': 'PWR-008-' + st, 'part_b': 'FIN-001-' + st, 'via': 'CT-TAPE-FOAM', 'owner': 'power',
                      'notes': 'cap laid along x on the half-fin outboard face %.0f mm aft of the ESC pad, clear of the ESC strap and FET face (E3); leads to the ESC power pads <= 20 mm (harness edge, CR-F1-18)' % (L['cap_gap_x_m'] * 1000),
                      'retention': tape('foam tape 1.1 mm + 1 packing-tape strip over the can', '2.2 g x 12.75 g = 0.3 N; prop-wash drag < 0.1 N', 'pre-flight: cap tight on the fin')})
    doc = {'schema': 'dbf-interfaces/1', 'subsystem': 'power',
           '_note': 'GENERATED by subsystems/power/make_power.py (F1, PWR-R1 + D-74) - edit the script, not this file. Electrical edges (pack plug, main jumpers, ESC leads with their XT30U, power-board link, cap leads) are harness edges (F2, D-20); power acknowledges E-HRN-10...16, -23, -34...37. D-74 deleted the UBEC PWR-005, its fuse PWR-007, their edges E-PWR-04 / -07 and the harness edges E-HRN-21 / -22 / -33.',
           'parts': parts, 'connection_types': cts, 'edges': edges, 'acknowledges': ['E-POD-05', 'E-POD-12'] + ['E-HRN-%02d' % i for i in list(range(10, 17)) + [23] + list(range(34, 38))]}
    with open(os.path.join(HERE, 'interfaces.json'), 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write('\n')
    with open(os.path.join(HERE, 'parts.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['part_id', 'name', 'qty', 'make_or_buy', 'process', 'material', 'mass_g', 'unit_cost_usd', 'vendor_or_file', 'notes'])
        for p in PARTS:
            w.writerow([p[0], p[1], 1, p[2], p[3], p[4], p[5], p[8], p[9], p[10]])
        w.writerow(['PWR-008', 'ESC capacitor 680 uF 25 V low-ESR (UR/UL/LR/LL)', 4, 'buy', 'solder at the ESC pads, foam-tape', 'electronics (bought)',
                    L['cap_mass_g'], 1.0, 'team/I1/BOM.csv#F07 (x5, 1 spare)', 'one per ESC, leads <= 20 mm'])
        for h in HARDWARE:
            w.writerow(h)
    tot = sum(p[5] for p in PARTS) + 4 * L['cap_mass_g']
    print('power: %d nodes, %d edges, flying mass %.1f g (allocation %s g)' % (len(parts), len(edges), tot, get('mass.allocation_g.power', 'g')))


if __name__ == '__main__':
    main()
    if '--check' not in __import__('sys').argv:     # C6 FASTENERS-CAD: re-apply the modelled fastener parts
        import os as _o, runpy as _r
        _r.run_path(_o.path.join(_o.path.abspath(__file__).rsplit(_o.sep + 'redesign' + _o.sep, 1)[0], 'redesign', 'team',
                                 'C6', 'fastener_parts.py'), run_name='c6_hook')['run']()
