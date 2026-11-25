"""T-077 p6: assemble the strength table (part, row, RF) from strength_PL66.5_12.json (adopted geometry), the cup MS rows (t077p6_cups.py, RF = 1 + MS) and bosses_p6.json.  Output strength_table_p6.md."""
import json, os, re
H = os.path.dirname(os.path.abspath(__file__))
INTEG = ('integrity', 'peel', 'N1 ', 'N2 ', 'N6b', 'shown only')
rows = json.load(open(os.path.join(H, 'strength_PL66.5_12.json')))
out = ['| Part | Row | RB | x1.5 | x2.23 (D-223 interim wing / saddle DAF) | Verdict at max(DAF, 1.5) |', '|---|---|---|---|---|---|']
def verdict(rf223, integ):
    if integ: return 'integrity class (outside the RF minimum): %s' % ('>= 1' if rf223 >= 1 else '**< 1, open**')
    return 'PASS' if rf223 >= 1 else '**FAIL**'
for r in sorted(rows, key=lambda r: (r['part'], r['rb'])):
    if 'shown only' in r['row'] or r['part'].startswith('Hub-side'): continue
    rb = r['rb']; integ = any(k.lower() in r['row'].lower() for k in INTEG)
    out.append('| %s | %s | %.2f | %.2f | %.2f | %s |' % (r['part'], r['row'].replace('|', '/'), rb, rb / 1.5, rb / 2.23, verdict(rb / 2.23, integ)))
# cups: RF = 1 + MS of the p6 run (strike envelope; landing inertial load is bounded by S1 axial: see the report)
md = open(os.path.join(H, 'arm_cup_checks_p6.md')).read()
cup_keys = ('Strike S2: plate cantilever bending', 'Strike S3 blade stop: hole bearing', 'Strike S3: sleeve wall hoop', 'Strike S2/S3: cup-to-arm bond', 'Strike S2 transverse 30 N', 'Strike S1 axial 30 N', 'Plate bending, cantilever', 'FATIGUE cup plate cantilever')
for ln in md.splitlines():
    if ln.startswith('|') and any(k in ln for k in cup_keys):
        c = [x.strip() for x in ln.strip('|').split('|')]
        try: ms = float(c[4])
        except Exception: continue
        out.append('| Motor cup CGE-003 R3fix (PETG), as drawn: OD 15.8, wall 1.8, web 4.2 | %s | %.2f (strike envelope, KP) | - | - | %s |' % (c[0][:110], 1 + ms, 'PASS' if ms >= 0 else '**FAIL**'))
for r in json.load(open(os.path.join(H, 'bosses_p6.json'))):
    if r['rf'] is None or ('x2.23' not in r['row'] and 'mount f_z' not in r['row']): continue
    out.append('| R2 bosses AVN-010 (PETG) | %s: %s | - | - | %.2f | %s |' % (r['board'][:22], r['row'][:150], r['rf'], 'PASS' if r['rf'] >= 1 else '**FAIL**'))
open(os.path.join(H, 'strength_table_p6.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
