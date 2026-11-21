"""T-077 p5 COPY (starts from the current printed_mass.json, so unchanged rows stay; the p5 audit rows override; adds the analytic CF plate / pin rows: FIN-007 4.88 g per side, CGE-011 1.04 g, FIN-008 and CGE-012 from the drawn rod volume x 1.6; removes AVN-001 and FIN-005 old rows when re-audited) of the T-077: write amodel/printed_mass.json = {part id: grams} for printed parts = CAD solid volume x T-067 print basis (shell + infill, basis S/M/C).
Unchanged parts: the T-067 adopted value (T067_data/t067_merged.json 'adopt_g', h 0.25 mm, hub 0.5 mm). Parts re-computed on the T-077 CAD: the rows of t077_rows_h0.25_only.json
(run `python -I t077_mass_audit.py 0.25 <ids>` first). WNG-009 keeps its listed mass (printed housing + silicone fluid not in the CAD). Category: geometry arithmetic + EST print basis."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
import math
base = json.load(open(os.path.join(H, '..', '..', '..', 'cad', 'amodel', 'printed_mass.json')))
base.pop('AVN-001', None)
for f in sys.argv[1:]:
    for r in json.load(open(os.path.join(H, f)))['rows']:
        base[r['id']] = r['computed_g']
for k in [k for k in base if k.startswith('WNG-009')]:
    base.pop(k)
# analytic CF sheet rows (T-077 p5): plates = (area - boss holes) x thickness x 1.6 g/cm3 (ACP PDS Dec 2014 density, T-071b A.4)
plate_clam = (50.0 * 64.0 - 3 * math.pi * 4.0 ** 2) * 0.5 * 2            # mm3 per side (two plates), boss holes r 4.0 mm
plate_node = (39.5 * 19.0 - (math.pi * 6.0 ** 2 / 2 + 13.0 * 9.5) - 4 * math.pi * 1.5 ** 2) * 0.5 * 2   # mm3 per node, two plates: 39.5 x 19 mm, less the spar hole (lower half circle r 6) and the 13 mm notch above it (z 0..9.5), less four 3 mm pin holes per plate
for s in 'RL':
    base['FIN-007-' + s] = plate_clam * 1.6e-3
base['CGE-011'] = plate_node * 1.6e-3
out = {k: round(v, 2) for k, v in sorted(base.items())}
json.dump(out, open(os.path.join(H, '..', '..', '..', 'cad', 'amodel', 'printed_mass.json'), 'w'), indent=1)
print(len(out), 'parts written')
