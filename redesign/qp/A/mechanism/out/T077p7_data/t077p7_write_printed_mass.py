"""T-077 p7 (D-225): printed_mass.json for the part-4 saddles. Starts from the p6 file; removes the withdrawn D-221 rows (FIN-007 plates, CGE-011 node plate, CGE-013 outer ears);
the rib saddles FIN-005-R/L and the bridge saddle CGE-006 get the part-4 audited values (T-077 p4 printed_mass.json at commit d923413d: FIN-005 14.39 g, CGE-006 9.67 g,
T-067 print basis, h 0.25 mm): their drawn geometry is the part-4 geometry (wing.py build_fins / build_cage with P5_CLAMSHELL = P5_NODE = False). Cups keep the p6 1.8 mm wall (7.68 g). R4 clamps CGE-007 from the p7 audit of the resized clamp.
Category: geometry arithmetic + EST print basis."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(H, '..', '..', '..', 'cad', 'amodel', 'printed_mass.json')
b = json.load(open(F))
for k in ('FIN-007-R', 'FIN-007-L', 'CGE-011', 'CGE-013'): b.pop(k, None)
b.update({'FIN-005-R': 14.39, 'FIN-005-L': 14.39, 'CGE-006': 9.67})
# T-077 p7 R4 clamp resize (ring OD 21 x 21, socket OD 12.5 / bore 8 x 27, fillet R 4.0): audited by t077p7_mass_audit.py h 0.25 (t077_rows_h0.25_only.json; it also reproduces FIN-005 14.39 and CGE-006 9.67)
for r in json.load(open(os.path.join(H, 't077_rows_h0.25_only.json')))['rows']:
    if r['id'].startswith('CGE-007'): b[r['id']] = r['computed_g']
json.dump({k: round(v, 2) for k, v in sorted(b.items())}, open(F, 'w'), indent=1); print(len(b), 'parts written')
