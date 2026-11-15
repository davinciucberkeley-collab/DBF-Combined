"""gen_interfaces.py - writes model/<sub>/interfaces.json, model/<sub>/fusion/<sub>.py stubs, modules.txt, mass_budget.json.
Two passes (build_a.py): pass 1 without CGs, pass 2 with the CAD volume centroids (declared CG = CAD centroid, as K09-L)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a_model as m  # noqa: E402

MODEL = os.path.join(HERE, 'model')
STUB = '''import os, sys
CAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if CAD not in sys.path:
    sys.path.insert(0, CAD)
import a_model


def build(ctx):
    a_model.build_%s(ctx)
'''


def write(cgs=None):
    cgs = cgs or {}
    for sub in m.SUBS:
        d = os.path.join(MODEL, sub)
        os.makedirs(os.path.join(d, 'fusion'), exist_ok=True)
        with open(os.path.join(d, 'fusion', sub + '.py'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(STUB % sub)
        parts = []
        for pid, p in m.PARTS.items():
            if p['subsystem'] != sub:
                continue
            q = dict(id=pid, name=p['name'], subsystem=sub, status='MODELLED', mass_g=p['mass_g'], material=p['material'],
                     cg_xyz_m=p['cg'] or cgs.get(pid), make_or_buy=p['make_or_buy'])
            if p.get('electrical'):
                q['electrical'] = p['electrical']
            for k in ('mass_proxy', 'carried'):
                if p.get(k):
                    q[k] = True
            q['notes'] = 'concept A CAD (qp/A/cad/a_model.py); mass per MASS-GATE / STRUCTURES iteration 2 or vendor page (EST where marked in a_model.py)'
            parts.append(q)
        edges, acks = [], set()
        for e in m.EDGES:
            if e['owner'] == sub:
                edges.append(e)
            else:
                subs = {m.PARTS[e['part_a']]['subsystem'], m.PARTS[e['part_b']]['subsystem']}
                if sub in subs:
                    acks.add(e['id'])
        doc = {'schema': 'dbf-interfaces/1', 'subsystem': sub, 'parts': parts, 'edges': edges,
               'acknowledges': sorted(acks)}
        if parts or edges:
            with open(os.path.join(d, 'interfaces.json'), 'w', encoding='utf-8', newline='\n') as f:
                json.dump(doc, f, indent=1)
    with open(os.path.join(MODEL, 'modules.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(m.SUBS) + '\n')
    with open(os.path.join(MODEL, 'mass_budget.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'_note': 'concept A: gate 1.50 kg (MASS-GATE s1); CG band 4.0..28.5 mm aft of the LE (forward limit / aft hard limit, MASS-GATE s5)',
                   'limit_g': 1500, 'allocations_g': {}, 'cg_x_m': [0.004, 0.0285]}, f, indent=1)


if __name__ == '__main__':
    write()
