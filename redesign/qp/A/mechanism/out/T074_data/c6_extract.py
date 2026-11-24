"""T-074 check 3: pull the C6 (T-071b A.2 'H3 + N2') rigid-body and x1.5 RF rows out of landing_centre_a.py outputs.  python -I c6_extract.py file...
C6 rows as listed in T071b_centre_nodes.md A.2: H3 hub bearing / collar (interlayer) / bridge, S0 saddle socket (bearing, as drawn), N2 node rows (skin->plate lap, plate shear, ear bond, pins) and the printed saddle body shear."""
import re, sys
def rows(fn):
    t = open(fn, encoding='utf-8').read().splitlines(); out = {}
    for l in t:
        if l.startswith('| H3 '):
            c = [x.strip() for x in l.strip('|').split('|')]
            out['hub bearing RB/x1.5/2T'] = c[5]; out['bridge bending RB'] = c[4]; out['collar interlayer RB/x1.5/2T'] = c[6]
        if l.startswith('| S0 '):
            out['saddle socket bearing RB/x1.5/2T'] = [x.strip() for x in l.strip('|').split('|')][2]
        if l.startswith('Printed saddle body'):
            m = re.search(r'RF ([\d.]+) \(RB\), ([\d.]+) \(RBx1\.5\)', l); out['saddle body shear RB'] = m.group(1); out['saddle body shear x1.5'] = m.group(2)
    # N2 rows: lines following '| N2 rung 4' (RB) and the next line (RBx1.5)
    for i, l in enumerate(t):
        if l.startswith('| N2 rung 4'):
            for tag, ln in (('RB', l), ('x1.5', t[i+1])):
                cells = [x.strip() for x in ln.strip('|').split('|')]
                out['N2 min rows ' + tag] = cells[-2]
                out['N2 rows ' + tag] = cells[-3][:400]
    return out
for fn in sys.argv[1:]:
    print('##', fn)
    for k, v in rows(fn).items(): print('  ', k, '=', v)
