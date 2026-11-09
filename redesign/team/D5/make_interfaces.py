"""Write redesign/subsystems/landing/{interfaces.json, parts.csv} from one place (D5).

    python -I redesign/team/D5/feet_calc.py        # first: masses (CALC-D5-MASS) into claims.json
    python -I redesign/team/D5/make_interfaces.py  # then: parts, edges, CGs from the CAD centroids (stub build)

Masses come from team/D5/claims.json (CALC-D5-MASS), CGs from the landing module built on the stub backend, so the
declared numbers, the calc and the CAD cannot drift apart.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.dirname(os.path.dirname(HERE))
SUB = os.path.join(RED, 'subsystems', 'landing')
sys.path.insert(0, os.path.join(RED, 'fusion'))
sys.path.insert(0, os.path.join(SUB, 'fusion'))

import fusionkit as fk                              # noqa: E402
import k09kit as k9                                 # noqa: E402
from backends.stub_backend import StubBackend       # noqa: E402
import landing                                      # noqa: E402

ST = ('UR', 'UL', 'LR', 'LL')
NAME = {'UR': 'upper right', 'UL': 'upper left', 'LR': 'lower right', 'LL': 'lower left'}

PARTS = [  # base id, name, material, make/buy, mass key, notes
    ('GER-001', 'Foot shoe', 'PETG (printed)', 'make', 'shoe_g',
     'U-channel + sleeve bonded over the fin TE tip; permanent; includes 0.30 g epoxy'),
    ('GER-002', 'Foot piston', 'PETG (printed)', 'make', 'piston_g',
     'cup with stop flange and two snap hooks; slides 32 mm in the shoe sleeve when the cartridge crushes; replace mark groove'),
    ('GER-003', 'Crush cartridge', 'XPS foam F-250 (cut)', 'make', 'cartridge_g',
     'two 38.5 mm segments 11 x 18 mm, crush axis = board thickness; bonded in the piston; consumable'),
    ('GER-004', 'Foot pad', 'neoprene 40A 1/16 in, adhesive back (bought sheet, cut)', 'make', 'pad_g',
     'ground contact, mu >= 0.7 (CR-C1-02); outboard edge at z +/-0.219 (CR-A1-20 splay)'),
]

CT = [
    {"id": "CT-GER-CRUSH-SLIDE", "kind": "kinematic", "method": "slid",
     "spec": "printed piston in printed sleeve, 0.2 mm/side; two snap hooks in 35 mm windows retain it and let it "
             "travel the 32 mm crush stroke; flange stops on the sleeve end"},
    {"id": "CT-GER-END-BEAR", "kind": "mechanical", "method": "slid",
     "spec": "crush cartridge slides in the sleeve and bears on the back wall in compression (0.5 mm preload, not bonded)"},
    {"id": "CT-GER-PSA", "kind": "mechanical", "method": "bonded",
     "spec": "rubber sheet pressure-sensitive adhesive backing on a degreased printed face"},
]


def masses():
    with open(os.path.join(HERE, 'claims.json'), encoding='utf-8') as f:
        nodes = {n['id']: n for n in json.load(f)['nodes']}
    return nodes['CALC-D5-MASS']['outputs']


def centroids():
    with open(os.path.join(RED, 'params', 'params.json'), encoding='utf-8') as f:
        params = json.load(f)
    ctx = fk.Context(StubBackend(), parts={}, params=params)
    k9.build_datums(ctx)
    ctx.begin_module('landing', SUB)
    landing.build(ctx)
    return {pid: c.volume_centroid()[1] for pid, c in ctx.components.items()}


def main():
    m, cg = masses(), centroids()
    parts = []
    for base, name, mat, mob, key, notes in PARTS:
        for st in ST:
            pid = '%s-%s' % (base, st)
            parts.append({"id": pid, "name": '%s %s' % (name, st), "subsystem": "landing", "status": "MODELLED",
                          "mass_g": round(m[key], 2), "material": mat,
                          "cg_xyz_m": [round(v, 4) for v in cg[pid]], "make_or_buy": mob,
                          "notes": '%s (%s fin tip)' % (notes, NAME[st])})
    edges = []
    for i, st in enumerate(ST):
        fin = 'FIN-001-' + st
        edges.append({"id": "E-GER-%02d" % (1 + i), "part_a": "GER-001-" + st, "part_b": fin, "via": "CT-EPOXY",
                      "owner": "landing",
                      "notes": "shoe bonded over the half-fin TE tip: sleeve floor on the tip edge (x 0.283-0.320, "
                               "9.6 mm) + legs 10 mm down both faces; 1 100 mm2; 30 min epoxy, faces scuffed; "
                               "printed/bonded design 86.8 N (C1 J-FOOT), CL-D5-BOND-SF 2.7. Permanent; a broken shoe "
                               "is cut off with a razor saw and a spare bonded (cure 30 min)"})
        edges.append({"id": "E-GER-%02d" % (5 + i), "part_a": "GER-002-" + st, "part_b": "GER-001-" + st,
                      "via": "CT-GER-CRUSH-SLIDE", "owner": "landing",
                      "notes": "field joint, no tools: press both hooks through the windows (fingernail or 2 mm hex "
                               "key), pull the piston + cartridge out, push a pre-glued spare in until both click; "
                               "<= 3 min (CL-D5-REPLACE-TIME). Crush stroke 32 mm toward -x"})
        edges.append({"id": "E-GER-%02d" % (9 + i), "part_a": "GER-003-" + st, "part_b": "GER-002-" + st,
                      "via": "CT-CA", "owner": "landing",
                      "notes": "foam-safe CA, two drops on the piston floor; segments tacked to each other"})
        edges.append({"id": "E-GER-%02d" % (13 + i), "part_a": "GER-004-" + st, "part_b": "GER-002-" + st,
                      "via": "CT-GER-PSA", "owner": "landing",
                      "notes": "pad cut 14.8 x 29 mm with the flange; wipe the flange with IPA first"})
        edges.append({"id": "E-GER-%02d" % (17 + i), "part_a": "GER-003-" + st, "part_b": "GER-001-" + st,
                      "via": "CT-GER-END-BEAR", "owner": "landing",
                      "notes": "landing load path: pad -> piston floor -> cartridge -> shoe back wall -> fin tip"})
    doc = {"schema": "dbf-interfaces/1", "subsystem": "landing",
           "_note": "GENERATED by redesign/team/D5/make_interfaces.py (masses: team/D5/claims.json CALC-D5-MASS; "
                    "CGs: CAD centroids). D5, revision D5-R1. The fins subsystem acknowledges E-GER-01..04.",
           "parts": parts, "connection_types": CT, "edges": edges, "acknowledges": []}
    with open(os.path.join(SUB, 'interfaces.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, indent=1)
        f.write('\n')

    cost = {'GER-001': 0.12, 'GER-002': 0.12, 'GER-003': 0.0, 'GER-004': 0.30}
    vendor = {'GER-001': 'subsystems/landing/fusion/landing.py (export body GER-001-UR, mirror for L)',
              'GER-002': 'subsystems/landing/fusion/landing.py (export body GER-002-UR)',
              'GER-003': 'wing-core offcut, hot-wire/knife cut (BUILD.md step 4)',
              'GER-004': 'SRC-D5-NEOPRENE: McMaster-Carr neoprene sheet 1/16 in, adhesive back, 12 x 12 in (~$12, '
                         'UNVERIFIED price); 4 pads + 12 spares per sheet'}
    proc = {'GER-001': 'FDM print, PETG, 0.2 mm layers, 2 perimeters 100 % (walls are the part), open end up, no supports',
            'GER-002': 'FDM print, PETG, 0.2 mm layers, flange on the bed, 2 perimeters',
            'GER-003': 'cut from 2 in F-250 board: 11 x 18 mm sticks across the thickness, 38.75 mm long (2 per foot)',
            'GER-004': 'scissors/knife from sheet, 14.8 x 29 mm, 1 mm corner round'}
    with open(os.path.join(SUB, 'parts.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['part_id', 'name', 'qty', 'make_or_buy', 'process', 'material', 'mass_g', 'unit_cost_usd',
                    'vendor_or_file', 'notes'])
        for base, name, mat, mob, key, notes in PARTS:
            w.writerow([base, name + ' (UR UL LR LL)', 4, mob, proc[base], mat, round(m[key], 2), cost[base],
                        vendor[base], notes + '; mass per unit, EST from CALC-D5-MASS'])
        w.writerow(['GER-005', 'Spare insert kit (piston + cartridge + pad, pre-glued)', 8, 'make',
                    'as GER-002/003/004', 'PETG / XPS / neoprene', 5.55, 0.45, 'field box (not flying)',
                    'ground spare, not on the aircraft (no interface node); spare count for 8 hard landings; also 2 spare shoes (GER-001) in the kit'])
        w.writerow(['GER-006', 'Neoprene sheet 1/16 in adhesive back 12 x 12 in', 1, 'buy', 'bought', 'neoprene 40A',
                    0, 12.0, 'SRC-D5-NEOPRENE (UNVERIFIED price)', 'stock for GER-004 and spares; mass counted in GER-004'])
    print('wrote %d parts, %d edges' % (len(parts), len(edges)))


if __name__ == '__main__':
    main()
