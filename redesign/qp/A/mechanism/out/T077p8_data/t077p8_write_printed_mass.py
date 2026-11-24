"""T-077 p8 (D-226): printed_mass.json for the torsion-cell tree. Starts from the p7 file (backup printed_mass_p7_backup.json); removes FIN-005-R/L (now CF bulkheads, mass in wing.py
fin_node_masses) and CGE-006 (now machined 6061, mass in wing.py cn_volume_m3); writes the p8 voxel audit (t077p8_mass_audit.py 0.25 FIN-003 GER-001 WNG-008 ->
t077_rows_h0.25_only.json): root blocks with the 29 x 29 socket for the 25 mm rib, Onyx shoes (1.20 g/cm3), lens caps after the 10.0 g lead.
Category: geometry arithmetic + EST print basis (T-067)."""
import json, os, time
H = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(H, '..', '..', '..', 'cad', 'amodel', 'printed_mass.json')
b = json.load(open(os.path.join(H, 'printed_mass_p7_backup.json')))
for k in ('FIN-005-R', 'FIN-005-L', 'CGE-006'): b.pop(k, None)
for r in json.load(open(os.path.join(H, 't077_rows_h0.25_only.json')))['rows']:
    b[r['id']] = r['computed_g']
for _ in range(20):
    try:
        json.dump({k: round(v, 2) for k, v in sorted(b.items())}, open(F, 'w'), indent=1); break
    except OSError:
        time.sleep(1)
print(len(b), 'parts written')
