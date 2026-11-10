"""Write redesign/subsystems/landing/{interfaces.json, parts.csv} from one place (D5, revision D5-R3).

    python -I redesign/team/D5/feet_calc.py        # first: masses (CALC-D5-MASS), bond area, loads into claims.json
    python -I redesign/team/D5/make_interfaces.py  # then: parts, edges, CGs from the CAD centroids (stub build)
    python -I redesign/team/D5/feet_calc.py        # again: the CAD cross-check now sees every part declared

Masses and joint numbers come from team/D5/claims.json, CGs from the landing module built on the stub backend, so the
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
NAME = {'UR': 'upper right', 'UL': 'upper left', 'LR': 'lower right', 'LL': 'lower left', 'R': 'right', 'L': 'left'}

# base id, name, material, make/buy, mass output (CALC-D5-MASS), instances, notes
PARTS = [
    ('GER-001', 'Foot shoe', 'PETG (printed)', 'make', 'shoe_g', ST,
     'sleeve 19.8 x 17.1 mm on the half-fin TE step, back wall on the step front and strip end faces, legs on both '
     'faces, collar cheeks over the edge-strip ends, rim at the sleeve end; permanent; includes 0.35 g epoxy'),
    ('GER-002', 'Foot piston', 'PETG (printed)', 'make', 'piston_g', ST,
     'tine 17.8 x 15.1 mm, two 6.5 mm snap fingers, stop flange, inspection windows, replace-mark groove; ORANGE on '
     'UR/UL, BLUE on LR/LL; slides 38 mm into the shoe when the cartridge crushes'),
    ('GER-003', 'Crush cartridge type U (solid)', 'XPS foam F-250 (cut)', 'make', 'cartridge_upper_g', ('UR', 'UL'),
     'two 44.5 mm segments 16 x 13.3 mm, crush axis = board thickness, orange stripe; plateau 36.6 N; bonded on the '
     'piston floor; consumable'),
    ('GER-004', 'Foot pad', 'neoprene 40A 1/16 in, adhesive back (bought sheet, cut)', 'make', 'pad_g', ST,
     'ground contact 19.8 x 18.1 mm, mu >= 0.7 (CR-C1-02); outboard edge at z +/-0.219 (contact 0.218)'),
    ('GER-007', 'Wingtip TE corner cap', 'TPU (printed)', 'make', 'cap_g', ('R', 'L'),
     'TPU 95A U-cap over the fixed wingtip TE corner (y 0.5615-0.575) + tip wall, held by 2 wraps of 12 mm filament '
     'tape (CR-C5-04); includes 0.10 g tape'),
    ('GER-008', 'Crush cartridge type L (bored)', 'XPS foam F-250 (cut)', 'make', 'cartridge_lower_g', ('LR', 'LL'),
     'type U with a 6.35 mm axial bore (sharpened 1/4 in brass tube), blue stripe; plateau 31.2 N; bonded on the '
     'piston floor; consumable'),
]

CT = [
    {"id": "CT-GER-CRUSH-SLIDE", "kind": "kinematic", "method": "slid",
     "spec": "printed tine in printed sleeve, 0.2 mm/side; two 6.5 mm snap fingers with 0.6 mm hooks in 41.5 mm "
             "windows retain it through the 38 mm crush stroke; flange stops on the sleeve-end rim"},
    {"id": "CT-GER-END-BEAR", "kind": "mechanical", "method": "slid",
     "spec": "crush cartridge slides in the sleeve and bears on the back wall in compression (0.5 mm preload, not bonded)"},
    {"id": "CT-GER-PSA", "kind": "mechanical", "method": "bonded",
     "spec": "rubber sheet pressure-sensitive adhesive backing on a degreased printed face"},
    {"id": "CT-GER-CAP-TAPE", "kind": "mechanical", "method": "taped",
     "spec": "TPU cap pushed over the TE corner, two wraps of 12 mm filament tape over its legs onto the tape skin"},
]


def claims():
    with open(os.path.join(HERE, 'claims.json'), encoding='utf-8') as f:
        nodes = {n['id']: n for n in json.load(f)['nodes']}
    out = lambda c: nodes[c]['outputs']
    return out('CALC-D5-MASS'), out('CALC-D5-BOND'), out('CALC-D5-CRUSH'), out('CALC-D5-SIDE'), out('CALC-D5-GEOM')


def centroids(declared):
    with open(os.path.join(RED, 'params', 'params.json'), encoding='utf-8') as f:
        params = json.load(f)
    declared = dict(declared, **{landing.CAP_HOST: {"id": landing.CAP_HOST, "material": "-", "mass_g": 1}})
    ctx = fk.Context(StubBackend(), parts=declared, params=params)   # host stand-in: caps built for their CGs
    k9.build_datums(ctx)
    ctx.begin_module('landing', SUB)
    landing.build(ctx)
    return {pid: c.volume_centroid()[1] for pid, c in ctx.components.items()}


def cap_host_declared():
    """True when another subsystem's interfaces.json declares the corner-cap host part (WNG-001)."""
    root = os.path.join(RED, 'subsystems')
    for sub in sorted(os.listdir(root)):
        path = os.path.join(root, sub, 'interfaces.json')
        if sub == 'landing' or not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            if any(p.get('id') == landing.CAP_HOST for p in json.load(f).get('parts', [])):
                return True
    return False


def main():
    m, bd, cr, sd, ge = claims()
    host = cap_host_declared()
    stub = {}
    for base, name, mat, mob, key, insts, notes in PARTS:
        for st in insts:
            pid = '%s-%s' % (base, st)
            stub[pid] = {"id": pid, "name": name, "material": mat, "mass_g": m[key]}
    cg = centroids(stub)
    parts = []
    for base, name, mat, mob, key, insts, notes in PARTS:
        for st in insts:
            pid = '%s-%s' % (base, st)
            status = 'MODELLED' if (base != 'GER-007' or host) else 'PROPOSED'
            parts.append({"id": pid, "name": '%s %s' % (name, st), "subsystem": "landing", "status": status,
                          "mass_g": round(m[key], 2), "material": mat,
                          "cg_xyz_m": [round(v, 4) for v in cg[pid]], "make_or_buy": mob,
                          "notes": '%s (%s); mass EST from CALC-D5-MASS' % (notes, NAME[st])})

    area = round(bd['area_m2'] * 1e6)
    design = round(bd['design_N'], 1)
    stroke = round(ge['stroke_m'] * 1000)
    edges = []
    cart = {'UR': 'GER-003-UR', 'UL': 'GER-003-UL', 'LR': 'GER-008-LR', 'LL': 'GER-008-LL'}
    for i, st in enumerate(ST):
        edges.append({
            "id": "E-GER-%02d" % (1 + i), "part_a": "GER-001-" + st, "part_b": "FIN-001-" + st, "via": "CT-EPOXY",
            "owner": "landing",
            "notes": "shoe bonded on the half-fin TE step (D3 cuts the tip to |z| %.4f from x %.4f to the TE, CR-D5-11): "
                     "sleeve floor on the step edge, legs 10 mm down both faces, back wall on the step front and the "
                     "strip end faces, collar cheeks over both edge-strip ends (CR-C4-09). Permanent; a broken shoe is cut off with "
                     "a razor saw and a spare bonded (24 h cure)" % (ge['z_step_m'], ge['x_step_m']),
            "bond": {"adhesive": "30 min laminating epoxy + ~5 % colloidal silica (non-sag)", "area_mm2": area,
                     "prep": "board paper scuffed 220 grit, not torn; cut foam edge and CF strip ends wiped with IPA; "
                             "PETG 120 grit",
                     "cure": "24 h at >= 18 degC before load",
                     "load_n": "%.1f N printed/bonded design (upper foot ult %.1f N x 1.4375); RF %.2f at %.2f MPa "
                               "(CL-D5-BOND-SF)" % (design, cr['F_ult_upper_N'], bd['sf'], bd['allow_Pa'] / 1e6),
                     "load_case": "L1 (landing, C1) with the C5 biased upper foot", "sized_by": "D5, C6"}})
        edges.append({
            "id": "E-GER-%02d" % (5 + i), "part_a": "GER-002-" + st, "part_b": "GER-001-" + st,
            "via": "CT-GER-CRUSH-SLIDE", "owner": "landing",
            "notes": "field joint, no tools: press both snap fingers through the side windows (thumb and finger), pull "
                     "the insert out, push a pre-glued spare of the SAME COLOUR in until both click; <= 3 min "
                     "(CL-D5-REPLACE-TIME). Crush stroke %d mm toward -x; side load at the pad %.1f N ult, lip "
                     "reaction %.0f N (CL-D5-SIDE-RIM-SF %.2f)" % (stroke, sd['F_N'], sd['R_lip_N'], sd['sf_rim']),
            "retention": {"item": "2 PETG snap fingers 6.5 x 5 x 0.8 mm, 0.6 mm hooks (CR-C6-12)", "count": 2,
                          "load_n": "< 1 N in service (crush load is compression on the back wall); pull-out by hand",
                          "inspection": "pre-flight: both hooks visible in their windows; replace-mark groove outside "
                                        "the rim; colour matches the station (orange up, blue down)"}})
        edges.append({
            "id": "E-GER-%02d" % (9 + i), "part_a": cart[st], "part_b": "GER-002-" + st, "via": "CT-CA",
            "owner": "landing",
            "notes": "foam-safe CA, two drops on the piston floor; segments tacked to each other",
            "bond": {"adhesive": "foam-safe CA (odourless)", "area_mm2": round(cr['area_upper_m2' if st[0] == 'U' else
                                                                                 'area_lower_m2'] * 1e6),
                     "prep": "cartridge end cut square; piston floor wiped with IPA", "cure": "2 min",
                     "load_n": "locates only: in service the cartridge is in compression", "load_case": "handling",
                     "sized_by": "D5"}})
        edges.append({
            "id": "E-GER-%02d" % (13 + i), "part_a": "GER-004-" + st, "part_b": "GER-002-" + st, "via": "CT-GER-PSA",
            "owner": "landing", "notes": "pad cut to the flange outline; wipe the flange with IPA first, press 30 s",
            "bond": {"adhesive": "neoprene sheet adhesive backing (PSA)",
                     "area_mm2": round(ge['pad_y_m'] * ge['pad_z_m'] * 1e6), "prep": "IPA wipe",
                     "cure": "press 30 s; 1 h before flight",
                     "load_n": "side friction %.1f N limit (C5 mat, mu 0.7) in shear" % (sd['F_N'] / 1.5),
                     "load_case": "L4/L5 (C1), CR-C5-09", "sized_by": "D5"}})
        edges.append({
            "id": "E-GER-%02d" % (17 + i), "part_a": cart[st], "part_b": "GER-001-" + st, "via": "CT-GER-END-BEAR",
            "owner": "landing",
            "notes": "landing load path: pad -> flange -> cartridge -> shoe back wall -> step and legs -> half-fin",
            "retention": {"item": "cartridge end in the sleeve bore, 0.5 mm preload", "count": 1,
                          "load_n": "plateau %.1f N (type U) / %.1f N (type L)" % (cr['F_upper_N'], cr['F_lower_N']),
                          "inspection": "after a hard landing: replace-mark groove"}})
    caps = []
    for eid, side in (('E-GER-21', 'R'), ('E-GER-22', 'L')):
        caps.append({
            "id": eid, "part_a": "GER-007-" + side, "part_b": "WNG-001", "via": "CT-GER-CAP-TAPE", "owner": "landing",
            "notes": "TPU corner cap on the fixed wingtip TE corner (outboard of the elevon end at |y| 0.560), over the "
                     "tape skin; sacrificial contact in a roll-first landing (CR-C5-04, CL-C5-WINGTIP-CLEAR-ROLL); keeps "
                     "clear of the CG-jig patch at |y| 0.45 (CR-H1-08)",
            "retention": {"item": "2 wraps of 12 mm filament tape over the cap legs", "count": 1,
                          "load_n": "ground contact in a roll landing: a few N; scuff only",
                          "inspection": "pre-flight: cap present, tape not lifting"}})
    if host:
        edges += caps
    else:
        for e in caps:
            e["waits_for"] = [landing.CAP_HOST]
    doc = {"schema": "dbf-interfaces/1", "subsystem": "landing",
           "_note": "GENERATED by redesign/team/D5/make_interfaces.py (masses, bond area and loads: team/D5/claims.json; "
                    "CGs: CAD centroids). D5, revision D5-R3. E-GER-01..04 point at the R3 half-fin ids FIN-001-UR/UL/"
                    "LR/LL (D-26). Corner caps GER-007-R/L: PROPOSED (not built in CAD) and E-GER-21/22 in edges_pending until a "
                    "subsystem declares WNG-001; re-run this script then and they move to MODELLED / edges.",
           "parts": parts, "connection_types": CT, "edges": edges, "acknowledges": []}
    if not host:
        doc["edges_pending"] = caps
    with open(os.path.join(SUB, 'interfaces.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, indent=1)
        f.write('\n')

    cost = {'GER-001': 0.10, 'GER-002': 0.08, 'GER-003': 0.0, 'GER-004': 0.25, 'GER-007': 0.03, 'GER-008': 0.0}
    vendor = {'GER-001': 'subsystems/landing/fusion/landing.py (export body GER-001-UR; one part for all four)',
              'GER-002': 'subsystems/landing/fusion/landing.py (export GER-002-UR; print 2 orange + 2 blue)',
              'GER-003': 'wing-core offcut, knife cut (BUILD.md step 4)',
              'GER-004': 'from GER-006 sheet',
              'GER-007': 'subsystems/landing/fusion/landing.py (export GER-007-R, mirror for L)',
              'GER-008': 'wing-core offcut, knife cut + brass-tube bore (BUILD.md step 4)'}
    proc = {'GER-001': 'FDM print, PETG, 0.2 mm layers, 2 perimeters (4 at the rim), back wall on the bed, no supports',
            'GER-002': 'FDM print, PETG, 0.2 mm layers, flange on the bed, 2 perimeters, slots cut in the slicer model',
            'GER-003': 'cut from 2 in F-250: 16.0 x 13.3 mm sticks across the thickness, 44.5 mm long (2 per foot)',
            'GER-004': 'scissors/knife from sheet, 19.8 x 18.1 mm, 1 mm corner round',
            'GER-007': 'FDM print, TPU 95A, 2 perimeters, open side up',
            'GER-008': 'as GER-003, then a 6.35 mm axial bore with a sharpened 1/4 in K&S brass tube'}
    with open(os.path.join(SUB, 'parts.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['part_id', 'name', 'qty', 'make_or_buy', 'process', 'material', 'mass_g', 'unit_cost_usd',
                    'vendor_or_file', 'notes'])
        for base, name, mat, mob, key, insts, notes in PARTS:
            w.writerow([base, '%s (%s)' % (name, ' '.join(insts)), len(insts), mob, proc[base], mat, round(m[key], 2),
                        cost[base], vendor[base], notes + '; mass per unit, EST from CALC-D5-MASS'])
        ground = [
            ('GER-005', 'Spare insert, upper (orange piston + type-U cartridge + pad, pre-glued)', 4, 'make',
             'as GER-002/003/004', 'PETG / XPS / neoprene', round(m['insert_upper_g'], 2), 0.35, 'field kit',
             'ground spare, not flying'),
            ('GER-009', 'Spare insert, lower (blue piston + type-L cartridge + pad, pre-glued)', 4, 'make',
             'as GER-002/008/004', 'PETG / XPS / neoprene', round(m['insert_lower_g'], 2), 0.35, 'field kit',
             'ground spare, not flying'),
            ('GER-010', 'Spare cartridge pair type U, loose (orange stripe)', 16, 'make', 'as GER-003', 'XPS F-250',
             round(m['cartridge_upper_g'], 2), 0.0, 'field kit', 'ground spare, not flying (C5 CR-C5-06: 16 per type)'),
            ('GER-011', 'Spare cartridge pair type L, loose (blue stripe)', 16, 'make', 'as GER-008', 'XPS F-250',
             round(m['cartridge_lower_g'], 2), 0.0, 'field kit', 'ground spare, not flying (C5 CR-C5-06: 16 per type)'),
            ('GER-012', 'Spare shoe', 2, 'make', 'as GER-001', 'PETG (printed)', round(m['shoe_g'] - 0.35, 2), 0.10,
             'field kit', 'ground spare, not flying'),
            ('GER-006', 'Neoprene sheet 1/16 in 40A adhesive back 12 x 12 in', 1, 'buy', 'bought', 'neoprene 40A', 0,
             12.0, 'SRC-D5-NEOPRENE (UNVERIFIED price)', 'stock for GER-004 and spares; not flying (mass in GER-004)'),
            ('GER-013', 'Brass tube 1/4 in OD (K&S), sharpened, cartridge bore cutter', 1, 'buy', 'bought', 'brass', 0,
             3.0, 'hobby shop, K&S 1/4 in round tube (UNVERIFIED price)', 'shop tool, not flying'),
        ]
        for row in ground:
            w.writerow(row)
    print('wrote %d parts, %d edges' % (len(parts), len(edges)))


if __name__ == '__main__':
    main()
