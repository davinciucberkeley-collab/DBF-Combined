"""T-083: printed_mass.json = the p8 file (backup printed_mass_p8_backup.json) with the voxel audit of the T-083 cup CGE-003 (t083_mass_audit.py 0.25 CGE-003 ->
t077_rows_h0.25_only.json, basis S, PETG 1.27 g/cm3). Category: geometry arithmetic + EST print basis (T-067).  python -I t083_write_printed_mass.py"""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(H, '..', '..', '..', 'cad', 'amodel', 'printed_mass.json')
b = json.load(open(os.path.join(H, 'printed_mass_p8_backup.json')))
for r in json.load(open(os.path.join(H, 't077_rows_h0.25_only.json')))['rows']:
    b[r['id']] = r['computed_g']
json.dump({k: round(v, 2) for k, v in sorted(b.items())}, open(F, 'w'), indent=1)
print(len(b), 'parts written')
