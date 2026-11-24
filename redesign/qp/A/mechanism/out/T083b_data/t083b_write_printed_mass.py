"""T-083b: printed_mass.json = the T-083 file (backup printed_mass_t083_backup.json) without FIN-003-R/L: the root fitting is machined 6061, its mass comes from
wing.fin_block_volume_m3() x RHO_AL in the P() line (as CGE-001 / CGE-006). Category: geometry arithmetic.  python -I t083b_write_printed_mass.py"""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(H, '..', '..', '..', 'cad', 'amodel', 'printed_mass.json')
b = json.load(open(os.path.join(H, 'printed_mass_t083_backup.json')))
for k in ('FIN-003-R', 'FIN-003-L'): b.pop(k)
json.dump({k: round(v, 2) for k, v in sorted(b.items())}, open(F, 'w'), indent=1)
print(len(b), 'parts written (FIN-003-R/L removed)')
