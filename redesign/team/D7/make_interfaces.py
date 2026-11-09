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

M = {n['id']: n for n in json.load(open(os.path.join(HERE, 'claims.json'), encoding='utf-8'))['nodes']}['CALC-D7-MASS']['outputs']
LOC = json.load(open(os.path.join(SUB, 'params.json'), encoding='utf-8'))['trn']['mass']
g = lambda kg: round(1000.0 * kg, 1)

ST = 'MODELLED'
COR, PE, XPS = 'Coroplast 4 mm (PP twin-wall)', 'PE foam 1.7 pcf (closed cell)', 'XPS foam F-250'
# id, name, mass_g, material, make_or_buy, process, unit cost USD (EST), vendor/file, notes
PARTS = [
    ('TRN-001', 'Box base (floor, walls, end pads)', g(M['base_kg']), COR, 'make', 'scored, folded, LSE tape + hot-melt',
     30.0, 'Home Depot Coroplast 48x96 4 mm (2 sheets incl. lid)', 'incl. end pads, 8 corner protectors, consumables; 1.25 x 0.55 x 0.54 m external'),
    ('TRN-005', 'Lid with PE lining and plug lip', g(M['lid_kg']), COR, 'make', 'scored, folded; 6 mm PE lining taped', 8.0,
     'from TRN-001 sheets + 6 mm PE roll', 'lip 30 mm inside the walls'),
    ('TRN-002-L', 'Spar cradle L (saddle + crush column)', g(M['cradle_each_kg']), XPS + ' + ' + PE, 'make',
     'hot-wire saddle to the S5010 template; laminate 2+2+1 in PE column', 6.0, 'XPS offcut; PE plank 2 in + 1 in',
     'column 60 x 50 x 127 mm under the spar; 6 mm PE cap'),
    ('TRN-002-R', 'Spar cradle R (saddle + crush column)', g(M['cradle_each_kg']), XPS + ' + ' + PE, 'make',
     'as TRN-002-L (mirror)', 6.0, 'as TRN-002-L', ''),
    ('TRN-003', 'Prop tray with pitot-boom and pouch pockets', g(M['tray_kg']), XPS, 'make',
     'hot-wire / knife cut slots in a 60 mm block', 3.0, 'XPS offcut', '8 prop slots on edge, pitot pocket 220 x 25 x 25 mm'),
    ('TRN-004-L', 'Lid hold-down pillar L', g(M['pillar_each_kg']), PE, 'make', 'cut from PE plank, 10 mm soft face', 3.0,
     'PE plank', '5 mm preload over the spar at y -0.20'),
    ('TRN-004-R', 'Lid hold-down pillar R', g(M['pillar_each_kg']), PE, 'make', 'as TRN-004-L', 3.0, 'PE plank', ''),
    ('TRN-006-A', 'Cam-buckle strap A', g(LOC['cam_strap_kg']['value']), '25 mm PP webbing + cam buckle', 'buy', '-', 6.0,
     'hardware store tie-down strap', 'EST mass; closes the lid, y -0.40'),
    ('TRN-006-B', 'Cam-buckle strap B', g(LOC['cam_strap_kg']['value']), '25 mm PP webbing + cam buckle', 'buy', '-', 6.0,
     'hardware store tie-down strap', 'y +0.40'),
    ('TRN-007-C', 'Side carry handle', g(LOC['handle_kg']['value']), 'strap handle (bought)', 'buy', 'bolt 2 x M5', 4.0,
     'luggage / tool-box strap handle', 'at the CG (y 0) on the front wall: one-person carry'),
    ('TRN-007-L', 'End handle L', g(LOC['handle_kg']['value']), 'strap handle (bought)', 'buy', 'bolt 2 x M5', 4.0, 'as TRN-007-C',
     'two-person carry'),
    ('TRN-007-R', 'End handle R', g(LOC['handle_kg']['value']), 'strap handle (bought)', 'buy', 'bolt 2 x M5', 4.0, 'as TRN-007-C', ''),
    ('TRN-008', 'Field pouch (wrench if needed, spare nuts, tape, checklist card)', g(LOC['pouch_kg']['value']),
     'nylon pouch + contents', 'buy', '-', 8.0, 'any zip pouch', 'carried mass, part of the loaded box'),
]
# BOM-only lines (no CAD part): consumables already booked in TRN-001 mass
BOM_ONLY = [
    ('TRN-101', 'LSE double-sided tape (3M 300LSE class), 1 roll', 1, 'buy', '-', 'acrylic adhesive tape', 0, 12.0, 'hardware store', 'mass in TRN-001'),
    ('TRN-102', 'M5 x 16 pan-head bolt + nyloc + 2 fender washers', 6, 'buy', '-', 'A2-70', 0, 0.5, 'hardware store', 'handles; mass in TRN-001'),
    ('TRN-103', 'Laminated CHECKLIST.md card', 1, 'make', 'print + laminate', 'paper', 0, 1.0, 'redesign/subsystems/transport/CHECKLIST.md', 'in TRN-008'),
    ('TRN-104', 'Ground mat 0.6 x 0.6 m (aircraft stands on it at the field)', 1, 'buy', '-', 'EVA foam tile', 0, 10.0, 'hardware store', 'rides on the lid outside, under strap A/B'),
]


def cad_centroids():
    import build_all
    from backends.stub_backend import StubBackend
    ctx, _, _ = build_all.build(StubBackend(), os.path.join(RED, 'subsystems'), os.path.join(RED, 'fusion', 'modules.txt'))
    return {pid: c.volume_centroid()[1] for pid, c in ctx.components.items() if c.subsystem == 'transport'}


CT = [
    {"id": "CT-TRN-LSE-TAPE", "kind": "mechanical", "method": "taped",
     "spec": "double-sided tape for low-surface-energy plastics (3M 300LSE class) on PP/PE, plus zip ties where stated"},
    {"id": "CT-CRADLE-CONTACT", "kind": "mechanical", "method": "slid",
     "spec": "aircraft rests in a foam-lined cradle, no fastening (transport only)"},
    {"id": "CT-TRN-PRELOAD-PAD", "kind": "mechanical", "method": "slid",
     "spec": "foam pillar pressed onto the part by the closed lid (5 mm preload), no fastening"},
    {"id": "CT-TRN-PLUG-LID", "kind": "mechanical", "method": "slid",
     "spec": "plug lid: folded lip inside the base walls, held closed by cam-buckle straps"},
    {"id": "CT-TRN-CAM-STRAP", "kind": "mechanical", "method": "strapped",
     "spec": "25 mm PP webbing with cam buckle around the box, through wall loops"},
    {"id": "CT-TRN-POCKET", "kind": "mechanical", "method": "slid", "spec": "item sits in a cut foam pocket, no fastening"},
    {"id": "CT-TRN-M5-BOLT", "kind": "mechanical", "method": "fastened",
     "spec": "M5 pan-head bolt through the Coroplast wall, fender washer both sides, nyloc inside"},
]
STACK = {"fastener": "M5x16 pan head", "count": 2, "grade": "A2-70",
         "hole": "5.5 mm clearance through handle strap and 4 mm wall; 15 mm fender washer each side",
         "insert": "none", "engagement_mm": 5.0, "min_engagement_mm": 5.0, "washer_nut": "M5 nyloc + fender washer (inside)",
         "torque": "snug (wall must not crush)", "tool": "3 mm hex key + 8 mm spanner", "access": "nut from inside the box, lid off",
         "install_order": 0, "removal_order": 0}
E = [
    ('E-TRN-01', 'TRN-002-L', 'TRN-001', 'CT-TRN-LSE-TAPE', 'column base on the floor + 2 zip ties through the floor'),
    ('E-TRN-02', 'TRN-002-R', 'TRN-001', 'CT-TRN-LSE-TAPE', 'as E-TRN-01'),
    ('E-TRN-03', 'TRN-003', 'TRN-001', 'CT-TRN-LSE-TAPE', 'tray on the floor between the cradles'),
    ('E-TRN-04', 'TRN-004-L', 'TRN-005', 'CT-TRN-LSE-TAPE', 'pillar on the lid lining'),
    ('E-TRN-05', 'TRN-004-R', 'TRN-005', 'CT-TRN-LSE-TAPE', 'pillar on the lid lining'),
    ('E-TRN-06', 'TRN-002-L', 'WNG-001', 'CT-CRADLE-CONTACT', 'saddle under the lower surface at y -0.20, x -0.015..0.235 (spar line); elevons, fins, tubes never pressed (P:transport.cradle). Wing must keep this patch free of servo covers and horns (CR-D7-04)'),
    ('E-TRN-07', 'TRN-002-R', 'WNG-001', 'CT-CRADLE-CONTACT', 'as E-TRN-06 at y +0.20'),
    ('E-TRN-08', 'TRN-004-L', 'WNG-001', 'CT-TRN-PRELOAD-PAD', 'upper surface over the spar at y -0.20, x 0.03..0.13; replaces the strap of the A4 plan (E-TRN-07 there)'),
    ('E-TRN-09', 'TRN-004-R', 'WNG-001', 'CT-TRN-PRELOAD-PAD', 'as E-TRN-08 at y +0.20'),
    ('E-TRN-10', 'TRN-005', 'TRN-001', 'CT-TRN-PLUG-LID', ''),
    ('E-TRN-11', 'TRN-006-A', 'TRN-001', 'CT-TRN-CAM-STRAP', 'y -0.40'),
    ('E-TRN-12', 'TRN-006-B', 'TRN-001', 'CT-TRN-CAM-STRAP', 'y +0.40'),
    ('E-TRN-13', 'TRN-007-C', 'TRN-001', 'CT-TRN-M5-BOLT', 'side handle at the box CG'),
    ('E-TRN-14', 'TRN-007-L', 'TRN-001', 'CT-TRN-M5-BOLT', 'end handle'),
    ('E-TRN-15', 'TRN-007-R', 'TRN-001', 'CT-TRN-M5-BOLT', 'end handle'),
    ('E-TRN-16', 'TRN-008', 'TRN-003', 'CT-TRN-POCKET', 'pouch pocket at the tray aft end'),
]


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
        if via == 'CT-TRN-M5-BOLT':
            e["joint_stack"] = dict(STACK, install_order=i, removal_order=len(E) - i)
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
