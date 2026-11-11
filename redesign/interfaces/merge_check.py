"""merge_check.py - merge every subsystem interfaces.json into one knowledge graph and check it.

Run (repo root):
    python -I redesign/interfaces/merge_check.py              # real subsystems -> redesign/interfaces/{interfaces.json,REPORT.md}
    python -I redesign/interfaces/merge_check.py --examples   # generic test aircraft -> redesign/interfaces/example-output/
    python -I redesign/interfaces/merge_check.py --root DIR --out DIR [--budget FILE] [--strict]

Exit code 1 if any ERROR (or any WARN with --strict). Schema: redesign/interfaces/SCHEMA.md.
Also imported by redesign/fusion/ (fusionkit, check.py) so CAD and the graph read the same data.

D-46 (A4, 2026-11-09): harness-owned electrical edges are exempt from the 'owner' warning (D-20); connection types
marked "structural": false (ties, wire channels, labels, pitot tubing) do not count as a load path in the floating
check; a part flagged "carried": true (harness bundle, label, consumables) held only by them is not floating, any
other part held only by them is; 'unpowered' follows power-carrying wires from
part_a (supply) to part_b (load), skipping "signal_only" leads and radio links; method "radio" (no wire block).
Python 3 stdlib only.
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(HERE)
SCHEMA_ID = 'dbf-interfaces/1'

STATUS = ('PROPOSED', 'MODELLED', 'CHECKED', 'VERIFIED')
KINDS = ('mechanical', 'electrical', 'thermal', 'kinematic')
METHODS = ('fastened', 'bonded', 'clamped', 'press_fit', 'taped', 'strapped', 'hinged', 'slid',
           'connector', 'soldered', 'conductive', 'radio')
MAKE_OR_BUY = ('make', 'buy')
ELEC_ROLES = ('source', 'bus', 'sink')

PART_FIELDS = ('id', 'name', 'subsystem', 'status', 'mass_g', 'material', 'cg_xyz_m', 'make_or_buy')
CT_FIELDS = ('id', 'kind', 'method', 'spec')
EDGE_FIELDS = ('id', 'part_a', 'part_b', 'via', 'owner', 'notes')
STACK_FIELDS = ('fastener', 'count', 'grade', 'hole', 'insert', 'engagement_mm', 'min_engagement_mm',
                'washer_nut', 'torque', 'tool', 'access', 'install_order', 'removal_order')
WIRE_FIELDS = ('gauge_awg', 'connector', 'route_id', 'support_points', 'bend_radius_mm', 'strain_relief',
               'disconnect')
MOTION_FIELDS = ('axis', 'range_deg')
STRUCTURAL = ('mechanical', 'kinematic')      # edge kinds that hold a part in place
WIRELESS = ('radio',)                         # electrical methods with no wire (no wire block, no power)
HARNESS = 'harness'                           # owns every electrical edge although it holds neither side (D-20)


class Graph:
    """Merged knowledge graph + findings. issues: list of (severity, code, item, message)."""

    def __init__(self):
        self.sources = []          # (path, subsystem)
        self.parts = {}            # id -> part dict (+ '_src')
        self.ctypes = {}           # id -> connection type
        self.edges = {}            # id -> edge dict (+ '_src', '_sub')
        self.acks = {}             # subsystem -> set(edge ids)
        self.issues = []

    def add(self, sev, code, item, msg):
        self.issues.append((sev, code, item, msg))

    def errors(self, strict=False):
        return [i for i in self.issues if i[0] == 'ERROR' or (strict and i[0] == 'WARN')]

    def kind(self, edge):
        ct = self.ctypes.get(edge.get('via'))
        return ct['kind'] if ct else None

    def method(self, edge):
        ct = self.ctypes.get(edge.get('via'))
        return ct['method'] if ct else None

    def flight_parts(self):
        return {k: p for k, p in self.parts.items() if p.get('flight', True)}

    def load_bearing(self, edge):
        """True if the edge can hold a part in place: a mechanical/kinematic type not marked "structural": false."""
        ct = self.ctypes.get(edge.get('via'))
        return bool(ct) and ct['kind'] in STRUCTURAL and ct.get('structural', True) is not False

    def carries_power(self, edge):
        """True for a wire that carries supply current: electrical, not a radio link, not "signal_only"."""
        ct = self.ctypes.get(edge.get('via'))
        return bool(ct) and ct['kind'] == 'electrical' and ct['method'] not in WIRELESS and not edge.get('signal_only')


# ----------------------------------------------------------------------------- loading
def find_sources(root):
    """<root>/<subsystem>/interfaces.json, sorted. The shared connection-type library is added by load()."""
    return sorted(glob.glob(os.path.join(root, '*', 'interfaces.json')))


def _read(path, g):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:                     # broken JSON is an error, not a crash
        g.add('ERROR', 'json', os.path.relpath(path, REDESIGN), 'cannot read: %s' % e)
        return None


def _missing(d, fields):
    return [f for f in fields if f not in d or d[f] is None or d[f] == '']


def load(root, library=os.path.join(HERE, 'connection_types.json')):
    """Read the shared connection-type library and every subsystem file under root into one Graph."""
    g = Graph()
    if library and os.path.exists(library):
        lib = _read(library, g) or {}
        for ct in lib.get('connection_types', []):
            _add_ctype(g, ct, 'library')
    sources = find_sources(root)
    if not sources:                                # an empty graph must not read as a clean PASS
        g.add('WARN', 'no-sources', os.path.relpath(root, REDESIGN).replace('\\', '/'),
              'no <subsystem>/interfaces.json found under this folder; nothing was checked')
    for path in sources:
        doc = _read(path, g)
        if doc is None:
            continue
        rel = os.path.relpath(path, REDESIGN).replace('\\', '/')
        sub = doc.get('subsystem') or os.path.basename(os.path.dirname(path))
        g.sources.append((rel, sub))
        if doc.get('schema') != SCHEMA_ID:
            g.add('WARN', 'schema', rel, 'schema should be "%s"' % SCHEMA_ID)
        for ct in doc.get('connection_types', []):
            _add_ctype(g, ct, rel)
        for p in doc.get('parts', []):
            pid = p.get('id')
            if pid in g.parts:
                g.add('ERROR', 'duplicate', pid, 'part id in %s and %s' % (g.parts[pid]['_src'], rel))
                continue
            p = dict(p, _src=rel)
            g.parts[pid] = p
            if p.get('subsystem') != sub:
                g.add('ERROR', 'schema', pid, 'subsystem "%s" != file subsystem "%s"' % (p.get('subsystem'), sub))
        for e in doc.get('edges', []):
            eid = e.get('id')
            if eid in g.edges:
                g.add('ERROR', 'duplicate', eid, 'edge id in %s and %s' % (g.edges[eid]['_src'], rel))
                continue
            g.edges[eid] = dict(e, _src=rel, _sub=sub)
        g.acks.setdefault(sub, set()).update(doc.get('acknowledges', []))
    return g


def _add_ctype(g, ct, src):
    cid = ct.get('id')
    old = g.ctypes.get(cid)
    clean = {k: v for k, v in ct.items() if not k.startswith('_')}
    if old is not None:
        if {k: v for k, v in old.items() if not k.startswith('_')} != clean:
            g.add('ERROR', 'duplicate', cid, 'connection type differs between %s and %s' % (old['_src'], src))
        return
    g.ctypes[cid] = dict(ct, _src=src)


# ----------------------------------------------------------------------------- checks
def check(g):
    _check_schema(g)
    _check_edges(g)
    _check_one_sided(g)
    _check_floating(g)
    _check_electrical(g)
    return g


def _check_schema(g):
    for cid, ct in g.ctypes.items():
        miss = _missing(ct, CT_FIELDS)
        if miss:
            g.add('ERROR', 'schema', cid, 'connection type missing ' + ', '.join(miss))
        if ct.get('kind') not in KINDS:
            g.add('ERROR', 'schema', cid, 'kind must be one of ' + '|'.join(KINDS))
        if ct.get('method') not in METHODS:
            g.add('ERROR', 'schema', cid, 'method must be one of ' + '|'.join(METHODS))
    for pid, p in g.parts.items():
        # mass_g and cg_xyz_m may be null while PROPOSED (reported below as missing)
        miss = [f for f in _missing(p, PART_FIELDS) if f not in ('mass_g', 'cg_xyz_m')]
        miss += [f for f in ('mass_g', 'cg_xyz_m') if f not in p]
        if miss:
            g.add('ERROR', 'schema', pid, 'part missing ' + ', '.join(miss))
        if p.get('status') not in STATUS:
            g.add('ERROR', 'schema', pid, 'status must be one of ' + '|'.join(STATUS))
        if p.get('make_or_buy') not in MAKE_OR_BUY:
            g.add('ERROR', 'schema', pid, 'make_or_buy must be make|buy')
        if p.get('electrical') not in (None,) + ELEC_ROLES:
            g.add('ERROR', 'schema', pid, 'electrical must be source|bus|sink')
        cg = p.get('cg_xyz_m')
        if cg is not None and not (isinstance(cg, list) and len(cg) == 3):
            g.add('ERROR', 'schema', pid, 'cg_xyz_m must be [x, y, z] in metres or null')
        if p.get('flight', True):
            if p.get('mass_g') in (None, ''):
                g.add('WARN', 'no-mass', pid, 'mass_g missing (%s)' % p.get('status'))
            elif p.get('status') != 'PROPOSED' and cg is None:
                g.add('WARN', 'no-cg', pid, 'cg_xyz_m missing on a %s part' % p.get('status'))


def _check_edges(g):
    for eid, e in g.edges.items():
        miss = [f for f in _missing(e, EDGE_FIELDS) if f != 'notes'] + (['notes'] if 'notes' not in e else [])
        if miss:
            g.add('ERROR', 'schema', eid, 'edge missing ' + ', '.join(miss))
        for side in ('part_a', 'part_b'):
            if e.get(side) and e[side] not in g.parts:
                g.add('ERROR', 'dangling', eid, '%s "%s" is not declared by any subsystem' % (side, e[side]))
        if e.get('part_a') == e.get('part_b'):
            g.add('ERROR', 'schema', eid, 'edge connects a part to itself')
        ct = g.ctypes.get(e.get('via'))
        if ct is None:
            g.add('ERROR', 'dangling', eid, 'via "%s" is not a known connection type' % e.get('via'))
            continue
        if ct['method'] == 'fastened':
            st = e.get('joint_stack') or {}
            miss = _missing(st, STACK_FIELDS)
            if miss:
                g.add('ERROR', 'joint-stack', eid, 'missing ' + ', '.join(miss))
            if 'engagement_mm' not in miss and 'min_engagement_mm' not in miss:
                try:
                    if float(st['engagement_mm']) < float(st['min_engagement_mm']):
                        g.add('ERROR', 'joint-stack', eid, 'thread engagement %s mm < minimum %s mm'
                              % (st['engagement_mm'], st['min_engagement_mm']))
                except (TypeError, ValueError):
                    g.add('ERROR', 'joint-stack', eid, 'engagement_mm / min_engagement_mm must be numbers')
        if ct['method'] == 'hinged':
            miss = _missing(e.get('motion') or {}, MOTION_FIELDS)
            if miss:
                g.add('ERROR', 'motion', eid, 'hinged edge missing motion.' + ', motion.'.join(miss))
        if ct['kind'] == 'electrical' and ct['method'] not in WIRELESS:
            miss = _missing(e.get('wire') or {}, WIRE_FIELDS)
            if miss:
                g.add('ERROR', 'wire', eid, 'electrical edge missing wire.' + ', wire.'.join(miss))
        subs = {g.parts[e[s]]['subsystem'] for s in ('part_a', 'part_b') if e.get(s) in g.parts}
        if e.get('owner') == HARNESS and ct['kind'] == 'electrical':
            continue                           # D-20: the wire is the installation; harness owns it, power/avionics hold the ends
        if e.get('owner') and subs and e['owner'] not in subs:
            g.add('WARN', 'owner', eid, 'owner "%s" is neither side (%s)' % (e['owner'], ', '.join(sorted(subs))))


def _check_one_sided(g):
    """An edge between two subsystems is declared once (by its file) and acknowledged by the other side."""
    for eid, e in g.edges.items():
        for s in ('part_a', 'part_b'):
            p = g.parts.get(e.get(s))
            if p and p['subsystem'] != e['_sub'] and eid not in g.acks.get(p['subsystem'], set()):
                g.add('WARN', 'one-sided', eid, 'declared by %s; %s has not acknowledged it'
                      % (e['_sub'], p['subsystem']))
    for sub, ids in g.acks.items():
        for eid in sorted(ids - set(g.edges)):
            g.add('WARN', 'one-sided', eid, '%s acknowledges an edge nobody declares' % sub)


def clusters(g, kinds=STRUCTURAL, parts=None, load_only=True):
    """Connected groups of parts joined by edges of the given kinds (largest first). load_only: skip connection
    types marked "structural": false (a tie or a label does not hold a part on)."""
    parts = parts if parts is not None else g.flight_parts()
    adj = {p: set() for p in parts}
    for e in g.edges.values():
        a, b = e.get('part_a'), e.get('part_b')
        if a in adj and b in adj and g.kind(e) in kinds and (not load_only or g.load_bearing(e)):
            adj[a].add(b)
            adj[b].add(a)
    seen, out = set(), []
    for p in sorted(adj):
        if p in seen:
            continue
        stack, grp = [p], set()
        while stack:
            q = stack.pop()
            if q not in grp:
                grp.add(q)
                stack.extend(adj[q] - grp)
        seen |= grp
        out.append(grp)
    out.sort(key=lambda s: (-sum(float(parts[q].get('mass_g') or 0) for q in s), -len(s)))
    return out


def carried(g, parts=None):
    """Flight parts flagged "carried": true (harness bundles, labels, consumables) that are located by at least one
    non-structural type and held by no load-bearing edge: carried items, exempt from the floating check. A part
    without the flag held only by ties (a pack on a cable tie) still floats. A "mass_proxy": true part (lumped
    harness mass, not drawn: the routed wires are) counts as carried too."""
    parts = parts if parts is not None else g.flight_parts()
    held, located = set(), set()
    for e in g.edges.values():
        if g.kind(e) not in STRUCTURAL:
            continue
        for s in ('part_a', 'part_b'):
            (held if g.load_bearing(e) else located).add(e.get(s))
    return {p for p in parts if p in located and p not in held
            and ((g.parts.get(p) or {}).get('carried') or (g.parts.get(p) or {}).get('mass_proxy'))}


def _check_floating(g):
    keep = g.flight_parts()
    for p in carried(g, keep):
        keep.pop(p)
    groups = clusters(g, parts=keep)
    for grp in groups[1:]:
        ids = ', '.join(sorted(grp))
        if len(grp) == 1:
            g.add('WARN', 'floating', ids, 'no structural (mechanical/kinematic) edge to the aircraft')
        else:
            g.add('WARN', 'floating', ids, 'group not structurally connected to the main aircraft')


def _check_electrical(g):
    """'unconnected': an electrical part with no wire at all. 'unpowered': no power-carrying wire path from a
    source, followed part_a (supply) -> part_b (load); signal-only leads and radio links do not feed a part."""
    elec = {k: p for k, p in g.parts.items() if p.get('electrical')}
    adj = {k: set() for k in elec}          # any wire, undirected (connectedness)
    feed = {k: set() for k in elec}         # power wires, directed supply -> load
    for eid, e in g.edges.items():
        if g.kind(e) != 'electrical' or g.method(e) in WIRELESS:
            continue
        for s in ('part_a', 'part_b'):
            p = g.parts.get(e.get(s))
            if p is not None and not p.get('electrical'):
                g.add('WARN', 'electrical', eid, '%s has no "electrical" role (source|bus|sink)' % p['id'])
        a, b = e.get('part_a'), e.get('part_b')
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)
            if g.carries_power(e):
                feed[a].add(b)
    live = set(k for k, p in elec.items() if p['electrical'] == 'source')
    stack = list(live)
    while stack:
        for q in feed[stack.pop()] - live:
            live.add(q)
            stack.append(q)
    for k, p in sorted(elec.items()):
        if not adj[k]:
            g.add('WARN', 'unconnected', k, 'electrical %s with no electrical edge' % p['electrical'])
        elif k not in live:
            g.add('WARN', 'unpowered', k, 'no power-carrying wire from a source (followed part_a -> part_b, '
                                          'signal-only leads skipped)')


# ----------------------------------------------------------------------------- mass / CG
def load_budget(path=None):
    """Mass budget: JSON {"limit_g", "allocations_g": {subsystem: g}, "cg_x_m": [lo, hi]}, or the first
    markdown table in MASS-CG.md with a 'subsystem' column and an 'alloc' (g) column (row 'total' = limit)."""
    cands = [path] if path else [os.path.join(REDESIGN, 'params', 'mass_budget.json'),
                                 os.path.join(REDESIGN, 'MASS-CG.md')]
    for c in cands:
        if not c or not os.path.exists(c):
            continue
        if c.endswith('.json'):
            with open(c, encoding='utf-8') as f:
                b = json.load(f)
            b['_src'] = c
            return b
        return _budget_from_md(c)
    return None


def _budget_from_md(path):
    with open(path, encoding='utf-8') as f:
        rows = [l.strip() for l in f if l.strip().startswith('|')]
    b = {'allocations_g': {}, '_src': path}
    hdr = None
    for r in rows:
        cells = [c.strip().lower() for c in r.strip('|').split('|')]
        if hdr is None:
            si = next((i for i, c in enumerate(cells) if 'subsystem' in c), None)
            ai = next((i for i, c in enumerate(cells) if 'alloc' in c), None)
            if si is not None and ai is not None:
                hdr = (si, ai)
            continue
        if set(''.join(cells)) <= set('-: '):
            continue
        m = re.search(r'[-+]?\d+(\.\d+)?', cells[hdr[1]].replace(',', '')) if len(cells) > hdr[1] else None
        if m:
            name = re.sub(r'[*`]', '', cells[hdr[0]]).strip()
            if name in ('total', 'limit', 'total limit'):
                b['limit_g'] = float(m.group())
            else:
                b['allocations_g'][name] = float(m.group())
    return b if hdr else None


def rollup(g, cg_override=None):
    """Per-subsystem mass and CG from declared part data. cg_override: {part_id: [x,y,z]} (e.g. CAD centroids)
    used only where the part declares no cg. Returns {sub: dict}, total dict."""
    subs = {}
    for pid, p in sorted(g.flight_parts().items()):
        s = subs.setdefault(p['subsystem'], {'mass_g': 0.0, 'm_cg': [0.0, 0.0, 0.0], 'm_with_cg': 0.0,
                                             'parts': 0, 'no_mass': [], 'no_cg': [], 'status': {}})
        s['parts'] += 1
        s['status'][p['status']] = s['status'].get(p['status'], 0) + 1
        m = p.get('mass_g')
        if m in (None, ''):
            s['no_mass'].append(pid)
            continue
        m = float(m)
        s['mass_g'] += m
        cg = p.get('cg_xyz_m') or (cg_override or {}).get(pid)
        if cg is None:
            s['no_cg'].append(pid)
            continue
        s['m_with_cg'] += m
        for i in range(3):
            s['m_cg'][i] += m * cg[i]
    tot = {'mass_g': 0.0, 'm_cg': [0.0] * 3, 'm_with_cg': 0.0}
    for s in subs.values():
        s['cg'] = [v / s['m_with_cg'] for v in s['m_cg']] if s['m_with_cg'] else None
        tot['mass_g'] += s['mass_g']
        tot['m_with_cg'] += s['m_with_cg']
        for i in range(3):
            tot['m_cg'][i] += s['m_cg'][i]
    tot['cg'] = [v / tot['m_with_cg'] for v in tot['m_cg']] if tot['m_with_cg'] else None
    return subs, tot


def check_budget(g, budget, subs, tot):
    if not budget:
        return
    for name, alloc in (budget.get('allocations_g') or {}).items():
        have = subs.get(name, {}).get('mass_g', 0.0)
        if have > alloc:
            g.add('WARN', 'mass', name, 'subsystem %.0f g > allocation %.0f g' % (have, alloc))
    lim = budget.get('limit_g')
    if lim is not None and tot['mass_g'] > lim:
        g.add('ERROR', 'mass', 'TOTAL', 'aircraft %.0f g > limit %.0f g' % (tot['mass_g'], lim))
    rng = budget.get('cg_x_m')
    if rng and tot['cg'] and not (rng[0] <= tot['cg'][0] <= rng[1]):
        g.add('ERROR', 'cg', 'TOTAL', 'CG x %.3f m outside %.3f..%.3f m' % (tot['cg'][0], rng[0], rng[1]))


# ----------------------------------------------------------------------------- output
def merged_doc(g):
    strip = lambda d: {k: v for k, v in d.items() if not k.startswith('_')}
    return {'schema': SCHEMA_ID, 'generated_by': 'redesign/interfaces/merge_check.py',
            'sources': [s for s, _ in g.sources],
            'parts': [strip(p) for _, p in sorted(g.parts.items())],
            'connection_types': [strip(c) for _, c in sorted(g.ctypes.items())],
            'edges': [dict(strip(e), declared_in=e['_sub']) for _, e in sorted(g.edges.items())]}


def dump_lines(doc):
    """JSON with one list item per line (readable, small diffs)."""
    out = []
    for k, v in doc.items():
        if isinstance(v, list):
            body = ',\n'.join('  ' + json.dumps(x, ensure_ascii=False) for x in v)
            out.append(' %s: [\n%s\n ]' % (json.dumps(k), body) if v else ' %s: []' % json.dumps(k))
        else:
            out.append(' %s: %s' % (json.dumps(k), json.dumps(v)))
    return '{\n' + ',\n'.join(out) + '\n}\n'


def _fmt(v, nd=3):
    return '-' if v is None else ('%.*f' % (nd, v))


def report_md(g, subs, tot, budget, title='Interfaces merge report'):
    L = ['# %s' % title, '',
         'Generated by `python -I redesign/interfaces/merge_check.py`. Do not edit by hand.', '',
         '| Sources | Parts | Connection types | Edges | Errors | Warnings |', '|---|---|---|---|---|---|',
         '| %d | %d | %d | %d | %d | %d |' % (len(g.sources), len(g.parts), len(g.ctypes), len(g.edges),
                                           sum(1 for i in g.issues if i[0] == 'ERROR'),
                                           sum(1 for i in g.issues if i[0] == 'WARN')), '',
         '## Mass and CG (declared part data, flight parts)', '',
         '| Subsystem | Parts | Status P/M/C/V | Mass g | Alloc g | CG x,y,z m | No mass | No CG |',
         '|---|---|---|---|---|---|---|---|']
    alloc = (budget or {}).get('allocations_g') or {}
    for name, s in sorted(subs.items()):
        st = '/'.join(str(s['status'].get(k, 0)) for k in STATUS)
        cg = ', '.join(_fmt(v) for v in s['cg']) if s['cg'] else '-'
        L.append('| %s | %d | %s | %.0f | %s | %s | %s | %s |' % (
            name, s['parts'], st, s['mass_g'], _fmt(alloc.get(name), 0), cg,
            ' '.join(s['no_mass']) or '-', ' '.join(s['no_cg']) or '-'))
    cg = ', '.join(_fmt(v) for v in tot['cg']) if tot['cg'] else '-'
    L.append('| **total** | %d | | **%.0f** | %s | %s | | |' % (
        sum(s['parts'] for s in subs.values()), tot['mass_g'], _fmt((budget or {}).get('limit_g'), 0), cg))
    L += ['', 'Budget: %s' % (os.path.relpath(budget['_src'], REDESIGN).replace('\\', '/') if budget else
                             'none found (redesign/params/mass_budget.json or MASS-CG.md)'), '',
          '## Findings', '']
    if not g.issues:
        L.append('None.')
    else:
        L += ['| Severity | Check | Item | Detail |', '|---|---|---|---|']
        for sev, code, item, msg in sorted(g.issues, key=lambda i: (i[0] != 'ERROR', i[1], str(i[2]))):
            L.append('| %s | %s | %s | %s |' % (sev, code, item, msg.replace('|', '/')))
    return '\n'.join(L) + '\n'


def run(root, out=None, budget_path=None, strict=False, quiet=False, title=None):
    g = check(load(root))
    budget = load_budget(budget_path)
    subs, tot = rollup(g)
    check_budget(g, budget, subs, tot)
    if out:
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, 'interfaces.json'), 'w', encoding='utf-8') as f:
            f.write(dump_lines(merged_doc(g)))
        with open(os.path.join(out, 'REPORT.md'), 'w', encoding='utf-8') as f:
            f.write(report_md(g, subs, tot, budget, title or 'Interfaces merge report'))
    if not quiet:
        print('merge_check: %d sources, %d parts, %d connection types, %d edges; total %.0f g, CG %s'
              % (len(g.sources), len(g.parts), len(g.ctypes), len(g.edges), tot['mass_g'],
                 ', '.join(_fmt(v) for v in tot['cg']) if tot['cg'] else '-'))
        for sev, code, item, msg in sorted(g.issues, key=lambda i: (i[0] != 'ERROR', i[1])):
            print('  %-5s %-12s %-14s %s' % (sev, code, item, msg))
        bad = g.errors(strict)
        print('merge_check: %s (%d errors, %d warnings%s)%s' % (
            'FAIL' if bad else 'PASS', sum(1 for i in g.issues if i[0] == 'ERROR'),
            sum(1 for i in g.issues if i[0] == 'WARN'), ', strict' if strict else '',
            ('; wrote ' + os.path.relpath(out, REDESIGN).replace('\\', '/') + '/{interfaces.json,REPORT.md}') if out else ''))
    return g


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--examples', action='store_true', help='check the generic test aircraft in redesign/fusion/examples')
    ap.add_argument('--root', help='folder holding <subsystem>/interfaces.json')
    ap.add_argument('--out', help='folder for interfaces.json + REPORT.md')
    ap.add_argument('--budget', help='mass budget file (.json or MASS-CG.md)')
    ap.add_argument('--strict', action='store_true', help='warnings also fail')
    a = ap.parse_args(argv)
    if a.examples:
        root = a.root or os.path.join(REDESIGN, 'fusion', 'examples')
        out = a.out or os.path.join(HERE, 'example-output')
        budget = a.budget or os.path.join(root, 'mass_budget.json')
    else:
        root = a.root or os.path.join(REDESIGN, 'subsystems')
        out = a.out or (HERE if not a.root else None)
        budget = a.budget
    g = run(root, out, budget, a.strict, title='Interfaces merge report (example aircraft)' if a.examples else None)
    return 1 if g.errors(a.strict) else 0


if __name__ == '__main__':
    sys.exit(main())
