"""C6 / A5: every fastener of every joint stack as its own part (FASTENERS-CAD.md).

    python -I redesign/team/C6/fastener_parts.py          # patch subsystems/*/interfaces.json + parts.csv in place
    python -I redesign/team/C6/fastener_parts.py --check  # exit 1 if a file is not up to date

Then: python -I redesign/fusion/check.py, python -I redesign/interfaces/merge_check.py,
      python -I redesign/team/A3/mass_rollup.py.

Re-run it after any subsystem generator (make_fins, make_propulsion / team/E1/propulsion.py, make_power,
team/D2/pod_data.py, make_mechanisms, team/D7/make_interfaces.py): those rewrite interfaces.json and parts.csv
without the hardware nodes, and check.py then fails with 'missing' / 'unknown-part' on the hardware ids.

What it writes, per hardware part number (table HW below):
  interfaces.json  one node per joint-stack instance (a "set": one component holding every screw / nut / washer of
                   that type at that joint; id rule <PREFIX>-NNN-<suffix>, so qty = nodes); one edge per part it
                   seats in, via CT-HW-SEATED (method clamped: the joint_stack stays on the parent edge, named in
                   "hardware_of", so C6's stack is not copied); acknowledgements on the other side.
  parts.csv        the line (qty = nodes, mass_g and unit cost per set); the parent line that carried the fastener
                   mass loses it (notes tagged [C6-HW], so a second run changes nothing).
The CAD bodies are built by the owner's module with k09kit.hw_* at the joint (only when the node is declared).
CGs are the CAD centroids (stub build, second pass). Masses: ISO / DIN catalogue values (A2 7.9 g/cm3, PA66
1.14 g/cm3, brass 8.5 g/cm3), the ones already booked by E1 / D3 kept where they exist. UNVERIFIED until weighed.
Python 3 standard library only.
"""
import csv
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.dirname(os.path.dirname(HERE))
SUBS = os.path.join(RED, 'subsystems')
for p in (os.path.join(RED, 'fusion'), os.path.join(RED, 'interfaces')):
    if p not in sys.path:
        sys.path.insert(0, p)

ST4 = ('UR', 'UL', 'LR', 'LL')
IDX = {s: i for i, s in enumerate(ST4)}
TAG = '[C6-HW]'
CT = {'id': 'CT-HW-SEATED', 'kind': 'mechanical', 'method': 'clamped',
      'spec': 'fastener hardware seated in a fastened joint (screw in its hole or thread, nut / washer / spacer under '
              'it, heat-set insert in its bore); the joint_stack is on the parent edge named in hardware_of'}
A2, PA66, BRASS = 'A2 stainless', 'nylon PA66', 'brass (CuZn39Pb3)'

# num, sub, instances, name (per set, {s} = suffix), material, mass_g per set, cost per set, vendor, parent edge(s)
# per instance, joins (other parts it seats on), fold (parent part number, grams per set it carried), flight, notes
HW = [
    dict(num='PRP-005', sub='propulsion', inst=ST4, name='Motor screw set {s}: 4 x M3x8 SHCS ISO 4762 A2',
         mat=A2, mass=3.2, cost=0.40, vendor='Bolt Depot (I1 B07)',
         parent=lambda s: ['E-FIN-%02d' % (61 + IDX[s])], joins=['FIN-003-{s}', 'PRP-001-{s}'], fold=('PRP-001', 3.2),
         notes='16 fitted + 4 spare (I1 B07); 0.8 g each (E1 ASM-E1-PART-MASS); joint stack E-FIN-61..64 (fins owns '
               'the joint, propulsion the screw line); 0.20 N m + Loctite 243 on the tips; mass moved out of PRP-001'),
    dict(num='PRP-006', sub='propulsion', inst=ST4, name='Prop adapter screw set {s}: 4 x M3x4 SHCS (supplied with PRP-004)',
         mat=A2, mass=1.2, cost=0.0, vendor='supplied with PRP-004',
         parent=lambda s: ['E-PRP-%02d' % (1 + IDX[s])], joins=['PRP-004-{s}', 'PRP-001-{s}'], fold=('PRP-004', 1.2),
         notes='4 x 0.3 g (E1 ASM-E1-PART-MASS); 0.5 N m + 243 on the tips (D-58 a); mass moved out of PRP-004'),
    dict(num='PRP-007', sub='propulsion', inst=ST4, name='Prop nut {s}: M6x1 hex nut ISO 4032 ({h}, supplied with PRP-004)',
         mat='steel (zinc plated)', mass=1.9, cost=0.0, vendor='supplied with PRP-004',
         parent=lambda s: ['E-PRP-%02d' % (5 + IDX[s])], joins=['PRP-004-{s}'], fold=('PRP-004', 1.9),
         notes='field joint (prop on / off); 1.5 N m, bell held; LH on the CW motors UR / LL; mass moved out of PRP-004'),
    dict(num='PRP-008', sub='propulsion', inst=ST4, name='Prop washer {s}: M6 6 x 12 x 1.0 (supplied with PRP-004)',
         mat='steel (zinc plated)', mass=0.6, cost=0.0, vendor='supplied with PRP-004',
         parent=lambda s: ['E-PRP-%02d' % (5 + IDX[s])], joins=['PRP-003-{s}', 'PRP-004-{s}'], fold=('PRP-004', 0.6),
         notes='between the prop hub and the nut; mass moved out of PRP-004'),
    dict(num='FIN-101', sub='fins', inst=ST4, name='Pinch bolt {s}: M3x16 SHCS ISO 4762 A2',
         mat=A2, mass=1.1, cost=0.10, vendor='Bolt Depot (I1 C01)',
         parent=lambda s: ['E-FIN-%02d' % (5 + IDX[s])], joins=['FIN-003-{s}'], fold=('FIN-003', 1.0),
         notes='4 fitted + 2 spare (I1 C01); ISO 4762 M3x16 1.1 g (was booked 1.0 g in FIN-003 mount.hardware_g)'),
    dict(num='FIN-102', sub='fins', inst=ST4, name='Pinch-bolt nut {s}: M3 nyloc ISO 10511 A2',
         mat=A2, mass=0.36, cost=0.05, vendor='Bolt Depot (I1 C01)',
         parent=lambda s: ['E-FIN-%02d' % (5 + IDX[s])], joins=['FIN-101-{s}', 'FIN-003-{s}'], fold=('FIN-003', 0.25),
         notes='4 fitted + 4 spare (I1 C01); reuse <= 3 times; DIN 985 / ISO 10511 M3 0.36 g'),
    dict(num='FIN-103', sub='fins', inst=ST4, name='Pinch-bolt washer pair {s}: 2 x M3 ISO 7089 A2',
         mat=A2, mass=0.24, cost=0.06, vendor='Bolt Depot (I1 C01)',
         parent=lambda s: ['E-FIN-%02d' % (5 + IDX[s])], joins=['FIN-003-{s}'], fold=('FIN-003', 0.15),
         notes='one under the head, one under the nyloc; 8 fitted + 4 spare (I1 C01); ISO 7089 M3 0.12 g each'),
    dict(num='PWR-101', sub='power', inst=(None,), name='Power-frame screw set: 4 x M3x18 pan head, nylon PA66',
         mat=PA66, mass=0.64, cost=0.40, vendor='any nylon M3 assortment (I1 C06)',
         parent=lambda s: ['E-PWR-03'], joins=['PWR-006', 'PWR-107'], fold=('PWR-006', 0.64),
         notes='4 fitted + 7 in I1 C06 (T-C6-NYLON-TORQUE, spares); 0.16 g each; 0.08 N m (1.6 N at 50 mm), no 243; '
               'mass moved out of PWR-006'),
    dict(num='PWR-102', sub='power', inst=(None,), name='Power-frame spacer set: 4 x nylon spacer M3, 10 mm, OD 6 / ID 3.2',
         mat=PA66, mass=0.92, cost=0.40, vendor='any (I1 C06)',
         parent=lambda s: ['E-PWR-03'], joins=['PWR-006', 'POD-002'], fold=('PWR-006', 0.92),
         notes='4 fitted + 2 spare (I1 C06); 0.23 g each; mass moved out of PWR-006'),
    dict(num='PWR-103', sub='power', inst=(None,), name='Power-frame washer set: 4 x M3 nylon washer 0.5 mm',
         mat=PA66, mass=0.08, cost=0.08, vendor='any (I1 C06)',
         parent=lambda s: ['E-PWR-03'], joins=['PWR-006'], fold=('PWR-006', 0.08),
         notes='under the screw heads; 4 fitted + 2 spare (I1 C06); mass moved out of PWR-006'),
    dict(num='PWR-107', sub='power', inst=(None,), name='Power-frame insert set: 4 x M3 x 5.7 brass heat-set insert in POD-002',
         mat=BRASS, mass=1.6, cost=0.60, vendor='Ruthex-class RX-M3x5.7 (I1 C02)',
         parent=lambda s: ['E-PWR-03'], joins=['POD-002'], fold=None,
         notes='set at 230-245 C in D2\'s 7.2 mm bosses (bore 4.0 x 6.5); 0.40 g each EST; new mass (no part carried '
               'it before); 12 in I1 C02 incl. T-C6-INSERT coupons'),
    dict(num='POD-011', sub='pod', inst=(None,), name='GPS mast cross-screw: M3x16 cheese head, nylon PA66 (DIN 84)',
         mat=PA66, mass=0.14, cost=0.10, vendor='any nylon M3 assortment (I1 C06)',
         parent=lambda s: ['E-POD-06'], joins=['POD-007', 'POD-005'], fold=None,
         notes='non-magnetic (CR-C6-18); finger tight + 1/4 turn; new mass (POD-005 is CAD volume only)'),
    dict(num='POD-012', sub='pod', inst=(None,), name='GPS mast nut: M3 hex nut, nylon PA66',
         mat=PA66, mass=0.05, cost=0.05, vendor='any nylon M3 assortment (I1 C06)',
         parent=lambda s: ['E-POD-06'], joins=['POD-011', 'POD-007'], fold=None,
         notes='fully on + 2 pitches; new mass'),
    dict(num='MEC-011', sub='mechanisms', inst=('R', 'L'),
         name='Servo cover screw pair {s}: 2 x M2 x 6 self-tapping pan head A2',
         mat=A2, mass=0.4, cost=0.30, vendor='supplied with the servo if 6 mm, else I1 H02 (M2 x 6 self-tapping)',
         parent=lambda s: ['E-MEC-%02d' % (36 if s == 'R' else 35), 'E-MEC-%02d' % (4 if s == 'R' else 3)],
         joins=['MEC-007-{s}', 'MEC-008-{s}'], fold=('MEC-007', 0.2),
         notes='closes E-MEC-35/36 and holds the servo in its ear slots (E-MEC-03/04, FIX 1); 1.6 mm pilot 6 mm deep, '
               'snug; 0.2 g each (was booked 0.1 g each in MEC-007); D-58 b'),
    dict(num='MEC-012', sub='mechanisms', inst=('R', 'L'), name='Servo arm screw {s}: M2 x 4 pan head (supplied with MEC-001)',
         mat=A2, mass=0.17, cost=0.0, vendor='supplied with MEC-001',
         parent=lambda s: ['E-MEC-%02d' % (6 if s == 'R' else 5)], joins=['MEC-002-{s}', 'MEC-001-{s}'], fold=None,
         notes='Loctite 222; new mass (no part carried it before)'),
    dict(num='TRN-102', sub='transport', inst=('C', 'L', 'R'),
         name='Handle bolt set {s}: 2 x (M3x16 SHCS + M3 nyloc + M3 x 12 fender washer)',
         mat=A2, mass=4.6, cost=0.60, vendor='hardware store (I1 T04)',
         parent=lambda s: ['E-TRN-%02d' % {'C': 13, 'L': 14, 'R': 15}[s]], joins=['TRN-007-{s}', 'TRN-001'],
         fold=None, flight=False,
         notes='flight: false; handles (C6 CR-C6-08); 3 mm ply strip inside not modelled'),
]
HAND = {'UR': 'LH', 'LL': 'LH', 'UL': 'RH', 'LR': 'RH'}
PREFIX = {'fins': 'FIN', 'propulsion': 'PRP', 'power': 'PWR', 'pod': 'POD', 'mechanisms': 'MEC', 'transport': 'TRN'}


def pid(h, s):
    return h['num'] if s is None else '%s-%s' % (h['num'], s)


def fmt(t, s):
    return t.replace('{s}', s or '').replace('{h}', HAND.get(s, 'LH on UR / LL, RH on UL / LR')).replace(' :', ':')


def load(sub):
    with open(os.path.join(SUBS, sub, 'interfaces.json'), encoding='utf-8') as f:
        return json.load(f)


def dump(doc):
    return json.dumps(doc, indent=1, ensure_ascii=False) + '\n'


def read_csv(sub):
    with open(os.path.join(SUBS, sub, 'parts.csv'), encoding='utf-8', newline='') as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def write_csv(head, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(head)
    w.writerows(rows)
    return buf.getvalue()


def nodes_edges(cgs):
    """Hardware part nodes and seat edges per owner subsystem; cgs = {part id: centroid} from the CAD."""
    out = {}
    count = {}
    for h in HW:
        sub = h['sub']
        P, E = out.setdefault(sub, ([], []))
        for s in h['inst']:
            p = pid(h, s)
            parents = h['parent'](s)
            node = {'id': p, 'name': fmt(h['name'], s), 'subsystem': sub, 'status': 'MODELLED', 'mass_g': h['mass'],
                    'material': h['mat'], 'cg_xyz_m': cgs.get(p), 'make_or_buy': 'buy',
                    'notes': 'fastener set modelled in CAD (C6 FASTENERS-CAD); joint stack on %s' % ', '.join(parents),
                    'hardware_of': parents[0]}
            if h.get('flight') is False:
                node['flight'] = False
            P.append(node)
            for o in h['joins']:
                count[sub] = count.get(sub, 100) + 1
                E.append({'id': 'E-%s-%d' % (PREFIX[sub], count[sub]), 'part_a': p, 'part_b': fmt(o, s),
                          'via': CT['id'], 'owner': sub,
                          'notes': 'hardware of %s (joint stack there); seated on %s' % (parents[0], fmt(o, s)),
                          'hardware': True, 'hardware_of': parents[0]})
    return out


def folds():
    """parent part number -> grams per parent node moved out to hardware."""
    f = {}
    for h in HW:
        if h['fold']:
            f[h['fold'][0]] = round(f.get(h['fold'][0], 0.0) + h['fold'][1], 3)
    return f


def patch_interfaces(doc, sub, NE, F, csv_mass):
    """Strip earlier hardware from doc, then add NE[sub]; parent nodes lose the folded mass once."""
    hw_ids = {p['id'] for s in NE.values() for p in s[0]}
    hw_edges = {e['id'] for s in NE.values() for e in s[1]}
    doc['parts'] = [p for p in doc['parts'] if not p.get('hardware_of')]
    doc['edges'] = [e for e in doc['edges'] if not e.get('hardware')]
    doc['connection_types'] = [c for c in doc.get('connection_types', []) if c['id'] != CT['id']]
    doc['acknowledges'] = [a for a in doc.get('acknowledges', []) if a not in hw_edges]
    for p in doc['parts']:
        num = '-'.join(p['id'].split('-')[:2])
        if num in F and p.get('mass_g') is not None:
            target = csv_mass.get(num)
            if target is not None and abs(p['mass_g'] - target) < 0.05:
                p['mass_g'] = target                     # node already at the patched csv value (generator read it)
            else:
                p['mass_g'] = round(p['mass_g'] - F[num], 3)
            p['hw_moved_g'] = F[num]
    if sub in NE:
        P, E = NE[sub]
        doc['parts'] += P
        doc['edges'] += E
        doc.setdefault('connection_types', []).append(dict(CT))
    acks = [e['id'] for s, (P, E) in NE.items() for e in E
            if any(e[k].startswith(PREFIX_OF[sub]) for k in ('part_a', 'part_b')) and s != sub]
    doc['acknowledges'] = doc.get('acknowledges', []) + [a for a in acks if a not in doc.get('acknowledges', [])]
    return doc


PREFIX_OF = {'wing': 'WNG-', 'fins': 'FIN-', 'pod': 'POD-', 'landing': 'GER-', 'propulsion': 'PRP-',
             'mechanisms': 'MEC-', 'power': 'PWR-', 'avionics': 'AVN-', 'harness': 'HRN-', 'transport': 'TRN-'}


def patch_csv(sub, F):
    """Hardware lines (qty = sets, mass and cost per set) and parent lines (folded mass out, tagged)."""
    head, rows = read_csv(sub)
    ix = {k: i for i, k in enumerate(head)}
    by = {r[0]: r for r in rows}
    for num, g in F.items():
        r = by.get(num)
        if r is not None and TAG not in r[ix['notes']]:
            r[ix['mass_g']] = ('%.2f' % (float(r[ix['mass_g']]) - g)).rstrip('0').rstrip('.')
            r[ix['notes']] += ' %s %.2f g of fasteners now modelled as their own parts (team/C6/fastener_parts.py)' % (TAG, g)
    for h in HW:
        if h['sub'] != sub:
            continue
        name = fmt(h['name'], None)
        line = [h['num'], name, str(len(h['inst'])), 'buy', '-', h['mat'], ('%g' % h['mass']), '%.2f' % h['cost'],
                h['vendor'], '%s per set (one node per joint, CAD set of bodies; C6 FASTENERS-CAD); %s' % (TAG, h['notes'])]
        line = line + [''] * (len(head) - len(line))
        if h['num'] in by:
            by[h['num']][:] = line
        else:
            rows.append(line)
            by[h['num']] = line
    return head, rows, {r[0]: float(r[ix['mass_g']]) for r in rows if r[ix['mass_g']] not in ('', None)}


def cad_centroids():
    import build_all
    import k09kit as k9
    from backends.stub_backend import StubBackend
    k9._HW_EDGES.clear()
    ctx, _, _ = build_all.build(StubBackend(), *build_all.roots(), log=lambda *a: None)
    ids = {pid(h, s) for h in HW for s in h['inst']}
    out = {}
    for p in ids:
        c = ctx.components.get(p)
        if c and c.shapes:
            out[p] = [round(v, 4) for v in c.volume_centroid()[1]]
    return out


def run(check=False):
    subs = sorted({h['sub'] for h in HW} | {'fins', 'propulsion', 'pod', 'power', 'mechanisms', 'transport'})
    F = folds()
    texts = {}
    for cgs_pass in ((1,) if check else (0, 1)):
        cgs = cad_centroids() if cgs_pass else {}
        NE = nodes_edges(cgs)
        if cgs_pass:
            for sub, (P, _) in NE.items():
                for p in P:
                    if p['cg_xyz_m'] is None:
                        raise SystemExit('%s: not built by the %s CAD module' % (p['id'], sub))
        texts = {}
        for sub in subs:
            Fs = {k: v for k, v in F.items() if k.startswith(PREFIX_OF[sub])}
            head, rows, csv_mass = patch_csv(sub, Fs)
            doc = patch_interfaces(load(sub), sub, NE, Fs, csv_mass)
            texts[os.path.join(SUBS, sub, 'interfaces.json')] = dump(doc)
            texts[os.path.join(SUBS, sub, 'parts.csv')] = write_csv(head, rows)
        if check:
            break
        for path, t in texts.items():
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(t)
    stale = []
    for path, t in texts.items():
        with open(path, encoding='utf-8', newline='') as f:
            if f.read().replace('\r\n', '\n') != t:
                stale.append(os.path.relpath(path, RED))
    n = sum(len(h['inst']) for h in HW)
    if check:
        print('fastener parts: %s' % ('up to date' if not stale else 'STALE: ' + ', '.join(stale)))
        return 1 if stale else 0
    print('fastener parts: %d nodes in %d part numbers, %d seat edges; parents lightened: %s'
          % (n, len(HW), sum(len(h['joins']) * len(h['inst']) for h in HW),
             ', '.join('%s -%.2f g' % kv for kv in sorted(F.items()))))
    return 0


if __name__ == '__main__':
    sys.exit(run('--check' in sys.argv))
