"""T-077: write amodel/printed_mass.json = {part id: grams} for printed parts = CAD solid volume x T-067 print basis (shell + infill, basis S/M/C).
Unchanged parts: the T-067 adopted value (T067_data/t067_merged.json 'adopt_g', h 0.25 mm, hub 0.5 mm). Parts re-computed on the T-077 CAD: the rows of t077_rows_h0.25_only.json
(run `python -I t077_mass_audit.py 0.25 <ids>` first). WNG-009 keeps its listed mass (printed housing + silicone fluid not in the CAD). Category: geometry arithmetic + EST print basis."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
base = {r['id']: r['adopt_g'] for r in json.load(open(os.path.join(H, '..', 'T067_data', 't067_merged.json')))['rows']}
for f in sys.argv[1:]:
    for r in json.load(open(os.path.join(H, f)))['rows']:
        base[r['id']] = r['computed_g']
for k in [k for k in base if k.startswith('WNG-009')]:
    base.pop(k)
out = {k: round(v, 2) for k, v in sorted(base.items())}
json.dump(out, open(os.path.join(H, '..', '..', '..', 'cad', 'amodel', 'printed_mass.json'), 'w'), indent=1)
print(len(out), 'parts written')
