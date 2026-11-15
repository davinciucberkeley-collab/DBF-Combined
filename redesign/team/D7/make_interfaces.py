"""Write redesign/subsystems/transport/{interfaces.json, parts.csv} from the D7 mass calc (claims.json) and the CAD
centroids of fusion/transport.py (stub build). Run after transport_calc.py:

    python -I redesign/team/D7/transport_calc.py
    python -I redesign/team/D7/make_interfaces.py
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.dirname(os.path.dirname(HERE))
SUB = os.path.join(RED, 'subsystems', 'transport')
sys.path.insert(0, os.path.join(RED, 'fusion'))

NODES = {n['id']: n for n in json.load(open(os.path.join(HERE, 'claims.json'), encoding='utf-8'))['nodes']}
M = NODES['CALC-D7-MASS']['outputs']
LOC = json.load(open(os.path.join(SUB, 'params.json'), encoding='utf-8'))['trn']['mass']
g = lambda kg: round(1000.0 * kg, 1)

ST = 'MODELLED'
# closure 2026-11-14 (I1 cost request): board box from 4 Home Depot XLBX blanks, Walmart PE sheets, cord lashings, hand holes
COR, PE, XPS = 'corrugated board, single wall (ECT 32 EST)', 'PE foam (closed cell, 1.7 pcf assumed)', 'XPS foam F-250'
CARD = 'corrugated board offcut (from TRN-001 blanks)'
# id, name, mass_g, material, make_or_buy, process, unit cost USD (EST), vendor/file, notes
PARTS = [
    ('TRN-001', 'Box base (floor, walls, end pads, nose pad)', g(M['base_kg']), COR, 'make', 'panels cut from 4 flattened XLBX blanks (SPEC.md panel nest): floor 2 x 610 x 565 + 30 mm strip, front / aft walls 1250 x 536, end walls 557 x 536; seams packing tape both sides',
     3.48, 'Home Depot XLBX 24 x 20 x 21 in moving box, x4 ($3.48 each, snippet 2026-11-14; I1 T01)', 'unit cost per blank, 4 blanks incl. lid; incl. 2 end pads, 1/2 in PE nose pad (D-150), consumables; 1.25 x 0.565 x 0.54 m external (closure 2026-11-14); aircraft 12 mm off the aft wall, against the saddle LE lips (x-stops)'),
    ('TRN-005', 'Lid with plug lip (no lining, D-31)', g(M['lid_kg']), COR, 'make', 'top 2 x 610 x 565 + 30 mm strip, four 30 mm lip strips taped under it', 0.0,
     'from TRN-001 blanks', 'lip 30 mm inside the walls; pillars taped to the shell'),
    ('TRN-002-L', 'Spar cradle L (saddle + crush column)', g(M['cradle_each_kg']), XPS + ' + ' + PE, 'make',
     'hot-wire saddle to the S5010 template; stack 3 x 2 in PE (one cut to 18.6 mm) = 120 mm, packing-tape wrap', 0.0, 'XPS offcut; PE from T06',
     'column 60 x 50 x 120 mm under the spar in a 30 mm board collar; saddle 60 x 250 mm at y 0.17-0.23 (4 mm inboard of the brace anchor); 6 mm PE cap'),
    ('TRN-002-R', 'Spar cradle R (saddle + crush column)', g(M['cradle_each_kg']), XPS + ' + ' + PE, 'make',
     'as TRN-002-L (mirror)', 0.0, 'as TRN-002-L', ''),
    ('TRN-003', 'Prop tray with pitot-boom slot and pouch pocket', g(M['tray_kg']), XPS, 'make',
     'hot-wire / knife cut slots in a 60 mm block', 0.0, 'XPS offcut',
     '8 prop slots on edge (APC 11x5.5E, D-161); pitot slot 220 x 25 x 25 mm with a PE tip plug; props stowed here, packs never in the box'),
    ('TRN-004-L', 'Lid hold-down pillar L', g(M['pillar_each_kg']), PE, 'make', 'stack 5 x 2 in PE cut to length, tape wrap; 10 mm soft face', 0.0,
     'PE from T06', '5 mm preload over the spar at y -0.20'),
    ('TRN-004-R', 'Lid hold-down pillar R', g(M['pillar_each_kg']), PE, 'make', 'as TRN-004-L', 0.0, 'PE from T06', ''),
    ('TRN-006-L', 'Cord lashing L', g(LOC['cord_kg']['value']), 'paracord 550, 2.6 m', 'make', 'slipped trucker\'s hitch over board edge saddles', 0.0,
     'I1 G18 paracord roll (already bought)', 'EST mass; closes the lid, y -0.40'),
    ('TRN-006-R', 'Cord lashing R', g(LOC['cord_kg']['value']), 'paracord 550, 2.6 m', 'make', 'as TRN-006-L', 0.0,
     'I1 G18 paracord roll', 'y +0.40'),
    ('TRN-007-C', 'Side hand hole + 2-layer patch', g(M['patch_each_kg']), CARD, 'make', 'die-cut 100 x 30 mm hole through wall + patch', 0.0,
     'offcut', 'aft wall at y 0: one-person carry (CL-D7-HANDHOLE-Q)'),
    ('TRN-007-L', 'End hand hole L + patch', g(M['patch_each_kg']), CARD, 'make', 'as TRN-007-C', 0.0, 'offcut', 'two-person carry'),
    ('TRN-007-R', 'End hand hole R + patch', g(M['patch_each_kg']), CARD, 'make', 'as TRN-007-C', 0.0, 'offcut', ''),
    ('TRN-008', 'Field pouch (10 mm prop spanner, spare M6 prop nuts, 2.5 mm key, tape, checklist card)', g(LOC['pouch_kg']['value']),
     'nylon pouch + contents', 'buy', '-', 8.0, 'any zip pouch', 'carried mass, part of the loaded box'),
]
# BOM-only lines (no CAD part): consumables already booked in TRN-001 mass
BOM_ONLY = [
    ('TRN-101', 'Packaging tape 1.88 in x 54.6 yd, 1 roll (Scotch 3350-RD; pess. 3M 3850-DC)', 1, 'buy', '-', 'PP film tape', 0, 4.30, 'Home Depot (snippet 2026-11-14; I1 T02)', 'mass in TRN-001'),
    ('TRN-110', 'PE foam sheet 16 x 12 x 2 in, 2-count (columns, pillars, pads, caps)', 1, 'buy', '-', 'PE foam', 0, 11.38, 'Walmart ip/12596320554 (snippet 2026-11-14, pess. $15.96; I1 T06)', 'mass in the parts it is cut into'),
    ('TRN-106', '10 mm prop spanner (D-40)', 1, 'buy', '-', 'steel', 0, 4.0, 'hardware store', 'in TRN-008; mass in TRN-008'),
    ('TRN-103', 'Laminated CHECKLIST.md card', 1, 'make', 'print + laminate', 'paper', 0, 1.0, 'redesign/subsystems/transport/CHECKLIST.md', 'in TRN-008'),
    ('TRN-104', 'Landing mat 0.8 x 0.8 m, two 0.8 x 0.4 m panels hinged with cloth tape: 1.5 mm rubber on 3 mm birch ply (C5 S1, CR-C5-06)', 1, 'make', 'laser-cut ply, contact-glued rubber, cloth-tape hinge, webbing loop', 'birch ply 3 mm + SBR/neoprene 1.5 mm', 2700, 25.0, 'ply: Jacobs Hall stock; rubber sheet: hardware store (EST price)', 'carried folded by its loop (CL-D7-MAT-MASS); replaces the EVA tile of round 2 (I1 CR-I1-18)'),
    ('TRN-107', 'Field tote (TX, landing-spares box, flight card, anemometer)', 1, 'buy', '-', 'canvas tote', 150, 8.0, 'any tote about 0.45 x 0.35 x 0.25 m', 'carried on the shoulder by carrier A (CL-D7-CARRY-A)'),
    ('TRN-108', 'Landing-spares box 1 L (holds the GER-005/009/010/011/012 spares)', 1, 'buy', '-', 'PP food box', 0, 3.0, 'any 1 L food box', 'contents are D5 parts; mass in trn.field_bag.landing_spares_kg'),
    ('TRN-109', 'Lid and end-wall labels (6 lines, trn.box.labels)', 1, 'make', 'print on label sheet', 'paper label', 0, 2.0, 'subsystems/transport/params.json#trn.box.labels', 'end-first and lid-down drops are label-and-test cases'),
]


def cad_centroids():
    import build_all
    from backends.stub_backend import StubBackend
    ctx, _, _ = build_all.build(StubBackend(), os.path.join(RED, 'subsystems'), os.path.join(RED, 'fusion', 'modules.txt'))
    return {pid: c.volume_centroid()[1] for pid, c in ctx.components.items() if c.subsystem == 'transport'}


CT = [
    {"id": "CT-TRN-LSE-TAPE", "kind": "mechanical", "method": "taped",
     "spec": "packaging-tape tabs and wraps on board / PE (closure 2026-11-14; id kept), column in a 30 mm board collar"},
    {"id": "CT-CRADLE-CONTACT", "kind": "mechanical", "method": "slid",
     "spec": "aircraft rests in a foam-lined cradle, no fastening (transport only)"},
    {"id": "CT-TRN-PRELOAD-PAD", "kind": "mechanical", "method": "slid",
     "spec": "foam pillar pressed onto the part by the closed lid (5 mm preload), no fastening"},
    {"id": "CT-TRN-PLUG-LID", "kind": "mechanical", "method": "slid",
     "spec": "plug lid: folded lip inside the base walls, held closed by two cord lashings"},
    {"id": "CT-TRN-CAM-STRAP", "kind": "mechanical", "method": "strapped",
     "spec": "paracord 550 lashing around the box girth, slipped trucker's hitch, folded-board edge saddles (closure 2026-11-14; id kept)"},
    {"id": "CT-TRN-POCKET", "kind": "mechanical", "method": "slid", "spec": "item sits in a cut foam pocket, no fastening"},
    {"id": "CT-TRN-PATCH", "kind": "mechanical", "method": "taped",
     "spec": "2-layer board patch taped and pressed inside the wall around a die-cut hand hole, flutes vertical"},
]
E = [
    ('E-TRN-01', 'TRN-002-L', 'TRN-001', 'CT-TRN-LSE-TAPE', 'column base in a 30 mm board collar taped to the floor'),
    ('E-TRN-02', 'TRN-002-R', 'TRN-001', 'CT-TRN-LSE-TAPE', 'as E-TRN-01'),
    ('E-TRN-03', 'TRN-003', 'TRN-001', 'CT-TRN-LSE-TAPE', 'tray on the floor between the cradles'),
    ('E-TRN-04', 'TRN-004-L', 'TRN-005', 'CT-TRN-LSE-TAPE', 'pillar on the lid shell'),
    ('E-TRN-05', 'TRN-004-R', 'TRN-005', 'CT-TRN-LSE-TAPE', 'pillar on the lid shell'),
    ('E-TRN-06', 'TRN-002-L', 'WNG-001', 'CT-CRADLE-CONTACT', 'bears on the tape skin WNG-003 over the core (also_contacts WNG-003, CR-D7-19 / CR-A4-46; saddle cut to the outer skin face, preload 0). Saddle under the lower surface at y -0.20 (0.17-0.23), x -0.015..0.235 (spar line), 15 000 mm2 >= C2 1 080 mm2; 4 mm inboard of the brace anchors (0.234); elevons, fins, tubes, braces never pressed (P:transport.cradle). Wing keeps this patch free of servo covers and horns (CR-D7-04)'),
    ('E-TRN-07', 'TRN-002-R', 'WNG-001', 'CT-CRADLE-CONTACT', 'as E-TRN-06 at y +0.20'),
    ('E-TRN-08', 'TRN-004-L', 'WNG-001', 'CT-TRN-PRELOAD-PAD', 'on the tape skin over the core (also_contacts WNG-003); upper surface over the spar at y -0.20, x 0.03..0.13; replaces the strap of the A4 plan (E-TRN-07 there)'),
    ('E-TRN-09', 'TRN-004-R', 'WNG-001', 'CT-TRN-PRELOAD-PAD', 'as E-TRN-08 at y +0.20'),
    ('E-TRN-10', 'TRN-005', 'TRN-001', 'CT-TRN-PLUG-LID', ''),
    ('E-TRN-11', 'TRN-006-L', 'TRN-001', 'CT-TRN-CAM-STRAP', 'y -0.40'),
    ('E-TRN-12', 'TRN-006-R', 'TRN-001', 'CT-TRN-CAM-STRAP', 'y +0.40'),
    ('E-TRN-13', 'TRN-007-C', 'TRN-001', 'CT-TRN-PATCH', 'side hand hole on the aft wall at y 0 (box CG)'),
    ('E-TRN-14', 'TRN-007-L', 'TRN-001', 'CT-TRN-PATCH', 'end hand hole'),
    ('E-TRN-15', 'TRN-007-R', 'TRN-001', 'CT-TRN-PATCH', 'end hand hole'),
    ('E-TRN-16', 'TRN-008', 'TRN-003', 'CT-TRN-POCKET', 'pouch pocket at the tray aft end'),
    ('E-TRN-17', 'PRP-003-UR', 'TRN-003', 'CT-TRN-POCKET', 'prop UR on edge in a 285 x 30 x 40 mm tray slot, label to the motor colour'),
    ('E-TRN-18', 'PRP-003-UL', 'TRN-003', 'CT-TRN-POCKET', 'as E-TRN-17'),
    ('E-TRN-19', 'PRP-003-LR', 'TRN-003', 'CT-TRN-POCKET', 'as E-TRN-17'),
    ('E-TRN-20', 'PRP-003-LL', 'TRN-003', 'CT-TRN-POCKET', 'as E-TRN-17'),
    ('E-TRN-21', 'AVN-005', 'TRN-003', 'CT-TRN-POCKET', 'pitot boom in its 220 x 25 x 25 mm tray slot, tip cover on, tip end against the PE plug (CR-D7-09)'),
]
STOWED = {'E-TRN-17', 'E-TRN-18', 'E-TRN-19', 'E-TRN-20', 'E-TRN-21'}
# A4 retention blocks (CR-A4-24b): item, count, load_n (limit, source), inspection
RET = {
    'E-TRN-01': ('30 mm board collar taped to the floor + tape wrap', 1, 10, 'C1 drop is compression; 10 N = half the aircraft weight at a 45 deg tilt, EST', 'pull by hand before every trip'),
    'E-TRN-03': ('packing-tape tabs, 4', 1, 6, 'tray + props at 2 g, EST', 'tray does not lift when the box is tipped'),
    'E-TRN-04': ('packing-tape tabs around the pillar base', 1, 102, 'CL-C1-PILLAR-F-LIM (compression)', 'pillar square on the lid; re-tape if it peels'),
    'E-TRN-06': ('wing in the saddle, 6 mm LE lip; saddle cut to the outer skin face, no preload', 1, 102, 'CL-C1-CRADLE-F-LIM', 'chalk patch >= 40 x 40 mm after T-D7-BOX-DROP'),
    'E-TRN-08': ('lid pillar, 5 mm preload', 1, 102, 'ASM-C1-LID-PRELOAD 5 N static; CL-C1-PILLAR-F-LIM lid-down', 'aircraft does not move when the closed box is tilted 45 deg'),
    'E-TRN-10': ('30 mm plug lip + 2 cord lashings', 1, 102, 'rebound into the pillars, CL-C1-PILLAR-F-LIM', 'lid seated, no gap > 3 mm'),
    'E-TRN-11': ('paracord 550 lashing, slipped trucker\'s hitch', 1, 50, 'hand-cinched tension, EST', 'cord not frayed, edge saddles in place, hitch holds'),
    'E-TRN-13': ('2-layer board patch, packing tape', 1, 114, 'CL-D7-HANDHOLE-F (loaded box at 2 g)', 'no crease or tear at the hole edge'),
    'E-TRN-16': ('pouch in its pocket', 1, 3, 'pouch 0.15 kg at 2 g', 'pocket not torn'),
    'E-TRN-17': ('prop on edge in its slot', 1, 2, 'prop 0.017 kg at 10 g (floor drop)', 'slot walls whole; prop tips not touching the floor of the slot'),
}
RET['E-TRN-02'], RET['E-TRN-05'], RET['E-TRN-07'], RET['E-TRN-09'], RET['E-TRN-12'] = (RET['E-TRN-01'], RET['E-TRN-04'],
                                                                                      RET['E-TRN-06'], RET['E-TRN-08'], RET['E-TRN-11'])
RET['E-TRN-14'] = RET['E-TRN-15'] = RET['E-TRN-13']
for _e in ('E-TRN-18', 'E-TRN-19', 'E-TRN-20'):
    RET[_e] = RET['E-TRN-17']
# CR-A4-46 / CR-D7-19: the saddles and pillars bear on the tape skin bonded over the core
ALSO = {e: ['WNG-003'] for e in ('E-TRN-06', 'E-TRN-07', 'E-TRN-08', 'E-TRN-09')}
_LOCC = json.load(open(os.path.join(SUB, 'params.json'), encoding='utf-8'))['trn']
_ps, _pp = _LOCC['cradle']['saddle_preload_m']['value'], _LOCC['holddown']['preload_m']['value']
PRELOAD = {'E-TRN-06': (_ps, 'trn.cradle.saddle_preload_m: modelled at contact with the outer face of WNG-003, rests by weight'),
           'E-TRN-07': (_ps, 'as E-TRN-06'),
           'E-TRN-08': (_pp, 'trn.holddown.preload_m: pillar cut 5 mm long, modelled at contact (preload not modelled as overlap)'),
           'E-TRN-09': (_pp, 'as E-TRN-08')}
RET['E-TRN-21'] = ('boom in its slot, PE tip plug', 1, 1, 'boom about 0.01 kg at 10 g, EST', 'tip cover on; slot not crushed')


def main():
    cg = cad_centroids()
    parts = []
    for pid, name, m, mat, mob, _p, _c, _v, note in PARTS:
        c = cg.get(pid)
        parts.append({"id": pid, "name": name, "subsystem": "transport", "status": ST, "mass_g": m, "material": mat,
                      "cg_xyz_m": [round(x, 4) for x in c] if c else None, "make_or_buy": mob, "flight": False,
                      "notes": note})
    edges = []
    for i, (eid, a, b, via, note) in enumerate(E):
        e = {"id": eid, "part_a": a, "part_b": b, "via": via, "owner": "transport", "notes": note}
        if eid in ALSO:
            e["also_contacts"] = ALSO[eid]
        if eid in STOWED:
            e["stowed"] = True
        if eid in RET:
            item, n, load, basis, insp = RET[eid]
            e["retention"] = {"item": item, "count": n, "load_n": load, "load_basis": basis, "inspection": insp}
            if eid in PRELOAD:
                e["retention"]["preload_m"], e["retention"]["preload_basis"] = PRELOAD[eid]
        edges.append(e)
    doc = {"schema": "dbf-interfaces/1", "subsystem": "transport",
           "_note": "GENERATED by redesign/team/D7/make_interfaces.py from team/D7/claims.json (masses) and the stub CAD "
                    "(centroids). Ground items: flight false. Aircraft frame, aircraft upright in the box.",
           "parts": parts, "connection_types": CT, "edges": edges, "acknowledges": []}
    with open(os.path.join(SUB, 'interfaces.json'), 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write('\n')
    with open(os.path.join(SUB, 'parts.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['part_id', 'name', 'qty', 'make_or_buy', 'process', 'material', 'mass_g', 'unit_cost_usd',
                    'vendor_or_file', 'notes'])
        for pid, name, m, mat, mob, proc, cost, ven, note in PARTS:
            w.writerow([pid, name, 1, mob, proc, mat, m, cost, ven, ('flight: false; ' + note).strip('; ')])
        for pid, name, q, mob, proc, mat, m, cost, ven, note in BOM_ONLY:
            w.writerow([pid, name, q, mob, proc, mat, m, cost, ven, 'flight: false; ' + note])
    print('wrote interfaces.json (%d parts, %d edges) and parts.csv; box %.0f g (parts sum %.0f g)' % (
        len(parts), len(edges), 1000 * M['box_kg'], sum(p['mass_g'] for p in parts if p['id'] != 'TRN-008')))


if __name__ == '__main__':
    main()
    if '--check' not in __import__('sys').argv:     # C6 FASTENERS-CAD: re-apply the modelled fastener parts
        import os as _o, runpy as _r
        _r.run_path(_o.path.join(_o.path.abspath(__file__).rsplit(_o.sep + 'redesign' + _o.sep, 1)[0], 'redesign', 'team',
                                 'C6', 'fastener_parts.py'), run_name='c6_hook')['run']()
