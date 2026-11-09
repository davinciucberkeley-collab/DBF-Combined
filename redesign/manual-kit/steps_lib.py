"""steps_lib.py - load every subsystem's steps.json + parts.csv + interfaces.json, check them, and work out what each
step needs (fasteners from the joint stacks, tools, consumables, wires, figure roles, mass targets).
Python 3 standard library only. Used by build_manual.py; `python -I build_manual.py --check` runs only this part.

Nothing here knows the aircraft configuration: parts, edges and numbers all come from the input files.
The step format is documented in redesign/manual-kit/README.md.
"""
import csv
import fnmatch
import json
import os
import re

KIT = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(KIT)

ID_RE = re.compile(r'\b(E-[A-Z]{3}-\d{2,3}|[A-Z]{3}-\d{3})\b')        # part ids (WNG-003) and edge ids (E-WNG-01)
# {ex_wing.tip_y_m*2|mm}: a number taken from a params.json. First word = subsystem (or "params" for the shared file)
PARAM_RE = re.compile(r'\{([A-Za-z_]\w*)\.([\w.\[\]]+?)(?:\*([0-9.]+))?(?:\|(mm|deg|g))?\}')
CHECK_TYPES = ('dimension', 'mass', 'fit', 'torque', 'continuity', 'voltage', 'function', 'visual')
LEVELS = ('note', 'caution', 'stop')
STEP_STATUS = ('PROPOSED', 'CHECKED', 'VERIFIED')     # VERIFIED = a teammate built it from these words and the CHECK passed
FRAME = [0.07, 0.93, 0.07, 0.93]     # subject box on the image: numbered markers replace side labels, so use the width
MAX_ACTIONS, MAX_MIN = 8, 45          # more than this: split the step (warning)


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def first_existing(*paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def split_list(s):
    """'3 mm hex key + 7 mm spanner' -> ['3 mm hex key', '7 mm spanner']; drops '(...)' notes and 'none'."""
    out = []
    for x in re.split(r'\s\+\s|,\s', s or ''):
        x = re.sub(r'\(.*?\)', '', x).strip()
        if x and not x.lower().startswith('none'):
            out.append(x)
    return out


def num(v):
    """Pretty number: 1200.0 -> '1200', 0.5 -> '0.5'."""
    return ('%d' % round(v)) if abs(v - round(v)) < 1e-6 else ('%.3g' % v if abs(v) < 10 else '%.1f' % v)


class Manual:
    """All inputs plus the derived build plan. Errors stop the build; warnings are printed and shown in the manual."""

    def __init__(self, src, ifaces=None, manual_path=None):
        self.src = os.path.abspath(src)
        self.ifaces = os.path.abspath(ifaces or src)
        self.errors, self.warnings = [], []
        self.parts, self.edges, self.ctypes, self.params = {}, {}, {}, {}
        mp = first_existing(manual_path, os.path.join(self.src, 'manual.json'),
                            os.path.join(REDESIGN, 'manufacturing', 'manual.json'))
        self.meta = load_json(mp) if mp else {}
        self.meta_path = mp
        self._load_ctypes()
        self.subsystems = self._discover()
        self._load_graph()
        self._load_steps()
        self._order()
        self._enrich()
        self._coverage()

    # ------------------------------------------------------------------ loading
    def err(self, where, msg):
        self.errors.append('%s: %s' % (where, msg))

    def warn(self, where, msg):
        self.warnings.append('%s: %s' % (where, msg))

    def _load_ctypes(self):
        p = os.path.join(REDESIGN, 'interfaces', 'connection_types.json')
        if os.path.exists(p):
            for c in load_json(p).get('connection_types', []):
                self.ctypes[c['id']] = c

    def _discover(self):
        """Subsystem folders that have a steps.json, in manual.json order (then modules.txt, then by name)."""
        have = sorted(d for d in os.listdir(self.src) if os.path.isfile(os.path.join(self.src, d, 'steps.json')))
        order = list(self.meta.get('subsystems', []))
        mt = os.path.join(self.ifaces, 'modules.txt')
        if not order and os.path.exists(mt):
            order = [l.strip() for l in open(mt, encoding='utf-8') if l.strip() and not l.startswith('#')]
        return [s for s in order if s in have] + [s for s in have if s not in order]

    def _iface_dirs(self):
        """Every subsystem with an interfaces.json (parts may be built in another subsystem's steps)."""
        names = set()
        for root in {self.src, self.ifaces}:
            for d in os.listdir(root):
                if os.path.isfile(os.path.join(root, d, 'interfaces.json')):
                    names.add(d)
        return sorted(names)

    def _load_graph(self):
        for s in self._iface_dirs():
            ip = first_existing(os.path.join(self.src, s, 'interfaces.json'), os.path.join(self.ifaces, s, 'interfaces.json'))
            d = load_json(ip)
            for c in d.get('connection_types', []):
                self.ctypes[c['id']] = c
            for p in d.get('parts', []):
                self.parts[p['id']] = dict(p, _iface=os.path.relpath(ip, REDESIGN).replace('\\', '/'))
            for e in d.get('edges', []):
                self.edges[e['id']] = e
            pc = first_existing(os.path.join(self.src, s, 'parts.csv'), os.path.join(self.ifaces, s, 'parts.csv'))
            if pc:
                with open(pc, encoding='utf-8', newline='') as f:
                    for row in csv.DictReader(f):
                        pid = row.get('part_id', '').strip()
                        if not pid:
                            continue
                        if pid not in self.parts:
                            self.warn(os.path.relpath(pc, REDESIGN), '%s is in parts.csv but not in interfaces.json' % pid)
                            self.parts[pid] = {'id': pid, 'name': row.get('name'), 'status': 'PROPOSED', 'subsystem': s}
                        p = self.parts[pid]
                        p['csv'] = row
                        try:
                            mc = float(row.get('mass_g') or 'nan')
                            if p.get('mass_g') is not None and abs(mc - float(p['mass_g'])) > 0.5:
                                self.warn(pid, 'mass %s g in parts.csv, %s g in interfaces.json' % (num(mc), p['mass_g']))
                        except ValueError:
                            pass
            pp = first_existing(os.path.join(self.src, s, 'params.json'), os.path.join(self.ifaces, s, 'params.json'))
            if pp:
                self.params[s] = (load_json(pp), os.path.relpath(pp, REDESIGN).replace('\\', '/'))
        shared = os.path.join(REDESIGN, 'params', 'params.json')
        if os.path.exists(shared):
            self.params['params'] = (load_json(shared), 'params/params.json')

    def _load_steps(self):
        self.steps = []
        seen = set()
        for s in self.subsystems:
            path = os.path.join(self.src, s, 'steps.json')
            d = load_json(path)
            for st in d.get('steps', []):
                st = dict(st)
                st['_file'] = os.path.relpath(path, REDESIGN).replace('\\', '/')
                st['_subsystem'] = s
                sid = st.get('id') or '?'
                if sid in seen:
                    self.err(sid, 'duplicate step id')
                seen.add(sid)
                self.steps.append(st)
        # work packages: from manual.json, else one per wp id in order of first use
        wps = list(self.meta.get('work_packages', []))
        known = {w['id'] for w in wps}
        for st in self.steps:
            w = st.get('wp')
            if not w:
                self.err(st.get('id'), 'no "wp" (work package)')
            elif w not in known:
                if self.meta.get('work_packages'):
                    self.err(st['id'], 'work package %s is not in manual.json' % w)
                wps.append({'id': w, 'title': w})
                known.add(w)
        self.wps = wps

    # ------------------------------------------------------------------ order
    def _order(self):
        """Steps sorted by work package, then by 'after' (a dependency must come earlier), then file order."""
        wi = {w['id']: i for i, w in enumerate(self.wps)}
        byid = {s.get('id'): s for s in self.steps}
        for s in self.steps:
            for a in s.get('after', []):
                if a not in byid:
                    self.err(s['id'], '"after" names unknown step %s' % a)
                elif wi.get(byid[a].get('wp'), 0) > wi.get(s.get('wp'), 0):
                    self.err(s['id'], 'depends on %s, which is in a later work package' % a)
        ordered = []
        for w in self.wps:
            pending = [s for s in self.steps if s.get('wp') == w['id']]
            while pending:
                for s in pending:
                    deps = [a for a in s.get('after', []) if a in byid and byid[a].get('wp') == w['id']]
                    if all(byid[a] in ordered for a in deps):
                        ordered.append(s)
                        pending.remove(s)
                        break
                else:
                    self.err(w['id'], 'circular "after" between ' + ', '.join(s['id'] for s in pending))
                    ordered += pending
                    break
        for n, s in enumerate(ordered, 1):
            s['n'] = n
        self.steps = ordered
        for w in self.wps:
            w['steps'] = [s for s in ordered if s.get('wp') == w['id']]

    # ------------------------------------------------------------------ params in text
    def param(self, name, path):
        """Value of {name.path} (path may hold dots and [i]); raises KeyError with a readable message."""
        if name not in self.params:
            raise KeyError('no params.json for "%s"' % name)
        v, f = self.params[name]
        for tok in re.findall(r'[^.\[\]]+|\[\d+\]', path):
            v = v[int(tok[1:-1])] if tok.startswith('[') else v[tok]
        return float(v), f

    def sub_params(self, text, wrap=None):
        """Replace {sub.key*k|unit} with the number. wrap(value_text, source_text) can decorate it (HTML title)."""
        def rep(m):
            name, path, k, unit = m.groups()
            try:
                v, f = self.param(name, path)
            except (KeyError, IndexError, ValueError, TypeError):
                return m.group(0)
            v *= float(k) if k else 1.0
            if unit == 'mm':
                v *= 1000
            src = '%s: %s%s%s' % (f, path, (' x ' + k) if k else '', ' (m to mm)' if unit == 'mm' else '')
            t = num(v)
            return wrap(t, src) if wrap else t
        return PARAM_RE.sub(rep, text or '')

    def _check_params(self, where, text):
        for m in PARAM_RE.finditer(text or ''):
            try:
                self.param(m.group(1), m.group(2))
            except (KeyError, IndexError, ValueError, TypeError) as e:
                self.err(where, 'number %s cannot be resolved (%s)' % (m.group(0), e))

    def _check_ids(self, where, text):
        for i in ID_RE.findall(text or ''):
            if i not in self.parts and i not in self.edges:
                self.err(where, 'unknown id %s in text' % i)

    # ------------------------------------------------------------------ derived data per step
    def _enrich(self):
        built_parts, built_edges = [], []
        for s in self.steps:
            sid = s.get('id', '?')
            for k in ('title', 'actions', 'check'):
                if not s.get(k):
                    self.err(sid, 'missing "%s"' % k)
            s.setdefault('status', 'PROPOSED')
            if s['status'] not in STEP_STATUS:
                self.err(sid, 'status must be one of ' + ' '.join(STEP_STATUS))
            # parts and edges
            s['parts_n'] = []
            for p in s.get('parts', []):
                p = {'id': p, 'qty': 1} if isinstance(p, str) else dict(p)
                if p['id'] not in self.parts:
                    self.err(sid, 'unknown part %s' % p['id'])
                s['parts_n'].append(p)
            for e in s.get('edges', []):
                if e not in self.edges:
                    self.err(sid, 'unknown interface edge %s' % e)
            pids = [p['id'] for p in s['parts_n']]
            eids = [e for e in s.get('edges', []) if e in self.edges]
            # every edge needs both its parts present by the end of this step
            have = set(built_parts) | set(pids)
            for e in eids:
                for side in ('part_a', 'part_b'):
                    if self.edges[e].get(side) not in have:
                        self.err(sid, '%s joins %s, which no earlier step installs' % (e, self.edges[e].get(side)))
            s['joints'], s['wires'], s['fasteners'] = [], [], []
            for e in eids:
                E = self.edges[e]
                ct = self.ctypes.get(E.get('via'), {})
                row = {'edge': e, 'a': E.get('part_a'), 'b': E.get('part_b'), 'via': E.get('via'),
                       'spec': ct.get('spec', E.get('via', '')), 'method': ct.get('method', ''), 'kind': ct.get('kind', ''),
                       'stack': E.get('joint_stack'), 'notes': E.get('notes', '')}
                if E.get('wire'):
                    s['wires'].append(dict(row, wire=E['wire']))
                else:
                    s['joints'].append(row)
                js = E.get('joint_stack')
                if js:
                    n = int(js.get('count', 1))
                    s['fasteners'].append({'item': ' '.join(x for x in (js.get('fastener'), js.get('grade')) if x),
                                           'qty': n, 'edge': e})
                    for x in split_list(js.get('washer_nut')) + split_list(js.get('insert')):
                        s['fasteners'].append({'item': x, 'qty': n, 'edge': e})
                    if ct.get('method') == 'fastened' and js.get('min_engagement_mm') is not None \
                            and float(js.get('engagement_mm', 0)) < float(js['min_engagement_mm']):
                        self.err(sid, '%s thread engagement %s mm is below the minimum %s mm'
                                 % (e, js.get('engagement_mm'), js['min_engagement_mm']))
                elif ct.get('method') == 'fastened':
                    self.warn(sid, '%s is fastened but has no joint_stack in interfaces.json' % e)
            for f in s.get('fasteners_extra', []):
                s['fasteners'].append({'item': f['item'], 'qty': f.get('qty', 1), 'edge': None})
            # tools: written ones first, then those the joint stacks name
            tools = list(s.get('tools', []))
            for j in s['joints']:
                js = j['stack'] or {}
                tools += split_list(js.get('tool'))
                if re.search(r'\d\s*N\s*[·.]?\s*m', js.get('torque', '')):
                    tools.append('Torque screwdriver')
            s['tools_n'] = dedupe(tools)
            cons = [dict(c) for c in s.get('consumables', [])]
            drops = sum(int((j['stack'] or {}).get('count', 1)) for j in s['joints']
                        if 'threadlocker' in ((j['stack'] or {}).get('torque') or '').lower())
            if drops and not any('threadlocker' in c['item'].lower() for c in cons):
                cons.append({'item': 'Threadlocker, medium strength (blue)', 'qty': drops, 'unit': 'drops'})
            s['consumables_n'] = cons
            # figure roles: act on this step's parts; show earlier parts of the same subassembly; hide the rest
            focus = pids + [e for e in eids if self.edges[e].get('wire')]
            if not pids:
                focus = dedupe([self.edges[e]['part_a'] for e in eids if not self.edges[e].get('wire')]) + focus
            context = self._same_assembly(focus, built_parts, built_edges, eids)
            s['focus'], s['context'] = focus, context
            # actions and callouts
            s['actions_n'] = []
            for i, a in enumerate(s.get('actions', []), 1):
                a = {'do': a} if isinstance(a, str) else dict(a)
                self._check_ids('%s action %d' % (sid, i), a.get('do'))
                self._check_params('%s action %d' % (sid, i), a.get('do'))
                at = a.get('at')
                if isinstance(at, str) and at not in self.parts and at not in self.edges:
                    self.err(sid, 'action %d points at unknown id %s' % (i, at))
                s['actions_n'].append(a)
            if len(s['actions_n']) > MAX_ACTIONS:
                self.warn(sid, '%d actions: consider splitting the step' % len(s['actions_n']))
            if (s.get('time_min') or 0) > MAX_MIN:
                self.warn(sid, '%s min hands-on: consider splitting the step' % s.get('time_min'))
            if not s.get('time_min'):
                self.warn(sid, 'no time_min')
            for x in s.get('safety', []):
                if x.get('level') not in LEVELS:
                    self.err(sid, 'safety level must be one of ' + ', '.join(LEVELS))
            if not s.get('can_go_wrong'):
                self.warn(sid, 'no "can_go_wrong" entries')
            built_parts += pids
            built_edges += eids
            s['checks'] = [self._check(sid, c, built_parts) for c in
                           (s['check'] if isinstance(s.get('check'), list) else [s['check']] if s.get('check') else [])]
            s['figures'] = self._figures(s)

    def _same_assembly(self, focus, built_parts, built_edges, eids):
        """Earlier parts (and wires) joined to this step's parts through the edges made so far."""
        parent = {}

        def find(x):
            while parent.setdefault(x, x) != x:
                x = parent[x]
            return x
        for e in built_edges + eids:
            E = self.edges[e]
            if not E.get('wire'):
                parent[find(E['part_a'])] = find(E['part_b'])
        groups = {find(f) for f in focus if f in self.parts}
        ctx = [p for p in built_parts if find(p) in groups and p not in focus]
        ctx += [e for e in built_edges if self.edges[e].get('wire') and find(self.edges[e]['part_a']) in groups]
        return ctx

    def _check(self, sid, c, built_parts):
        c = dict(c)
        t = c.get('type')
        if t not in CHECK_TYPES:
            self.err(sid, 'check type must be one of ' + ', '.join(CHECK_TYPES))
        if t == 'mass':
            pats = c.get('of', ['*'])
            ids = [p for p in built_parts if any(fnmatch.fnmatchcase(p, x) for x in pats)
                   and self.parts.get(p, {}).get('flight', True) is not False]      # fixtures never weigh in
            m = sum(float(self.parts.get(p, {}).get('mass_g') or 0) for p in ids)
            tol = float(c.get('tol_pct', 5))
            c['target'] = '%s g ± %s %% (%s to %s g)' % (num(m), num(tol), num(m * (1 - tol / 100)), num(m * (1 + tol / 100)))
            c['source'] = 'sum of mass_g of %d parts installed so far (interfaces.json)' % len(ids)
        elif not c.get('target'):
            self.err(sid, 'check needs a measurable "target"')
        if t == 'visual':
            self.warn(sid, 'visual check: prefer a measurable one (dimension, mass, fit, continuity)')
        if not c.get('text'):
            self.err(sid, 'check needs "text" (what to do)')
        for k in ('text', 'target'):
            self._check_params(sid + ' check', c.get(k))
            self._check_ids(sid + ' check', c.get(k))
        return c

    def _figures(self, s):
        """Render specs (render_figures.py format) for the step's main figure and its details."""
        f = s.get('figure', {})
        if f is False:
            self.warn(s['id'], 'no figure')
            return []
        callouts = dedupe([a['at'] for a in s['actions_n'] if isinstance(a.get('at'), str)])
        callouts += [{'at': a['at'], 'text': ''} for a in s['actions_n'] if isinstance(a.get('at'), list)]
        out = []
        for k, spec in enumerate([f] + list(s.get('details', []))):
            cam = spec.get('camera', 'iso')
            cam = dict({'preset': cam} if isinstance(cam, str) else cam)
            cam.setdefault('frame', FRAME)
            fid = s['id'].lower() + ('' if k == 0 else '-d%d' % k)
            title = spec.get('title') or ('Step %d: %s' % (s['n'], s.get('title', '')) if k == 0 else '')
            fig = {'id': fid, 'scene': spec.get('scene', 'workbench'), 'camera': cam,
                   'focus': spec.get('focus', s['focus']), 'context': spec.get('context', s['context']),
                   'ghost': spec.get('ghost', []), 'xray': spec.get('xray', f.get('xray', []) if k else []),
                   'hide': spec.get('hide', []), 'callouts': spec.get('callouts', callouts),
                   'caption': {'title': title, 'sub': ''}}
            if k == 0 and 'xray' in f:
                fig['xray'] = f['xray']
            for key in ('pose', 'explode', 'colour'):
                v = spec.get(key, f.get(key) if k else None)
                if v is not None:
                    fig[key] = v
            out.append(fig)
        return out

    # ------------------------------------------------------------------ completeness
    def _coverage(self):
        """Every part and every interface edge is installed by exactly one step (missing ones are listed)."""
        where = {}
        for s in self.steps:
            for i in [p['id'] for p in s['parts_n']] + list(s.get('edges', [])):
                if i in where:
                    self.err(s['id'], '%s is already installed in %s' % (i, where[i]))
                where.setdefault(i, s['id'])
        self.installed_in = where
        self.missing_parts = [p for p in sorted(self.parts) if p not in where]
        self.missing_edges = [e for e in sorted(self.edges) if e not in where]
        for p in self.missing_parts:
            self.warn(p, 'not installed in any step')
        for e in self.missing_edges:
            self.warn(e, 'interface not made in any step')

    # ------------------------------------------------------------------ roll-ups
    def kit(self, steps):
        """Kitting list for a set of steps: parts, fasteners (summed), consumables (summed per unit), tools."""
        parts = []
        for s in steps:
            for p in s['parts_n']:
                P = self.parts.get(p['id'], {})
                row = P.get('csv', {})
                parts.append({'id': p['id'], 'name': P.get('name', ''), 'qty': p.get('qty', 1), 'step': s['id'],
                              'make_or_buy': P.get('make_or_buy') or row.get('make_or_buy', ''),
                              'vendor': row.get('vendor_or_file', ''), 'mass_g': P.get('mass_g'),
                              'status': P.get('status', '')})
        fas = {}
        for s in steps:
            for f in s['fasteners']:
                r = fas.setdefault(f['item'], {'item': f['item'], 'qty': 0, 'steps': []})
                r['qty'] += int(f['qty'])
                r['steps'] = dedupe(r['steps'] + [s['id']])
        con = {}
        for s in steps:
            for c in s['consumables_n']:
                key = (c['item'], c.get('unit', ''))
                r = con.setdefault(key, {'item': c['item'], 'unit': c.get('unit', ''), 'qty': 0, 'steps': []})
                try:
                    r['qty'] += float(c.get('qty', 0))
                except (TypeError, ValueError):
                    r['qty'] = c.get('qty')
                r['steps'] = dedupe(r['steps'] + [s['id']])
        tools = {}
        for s in steps:
            for t in s['tools_n']:
                r = tools.setdefault(t.lower(), {'tool': t, 'steps': []})
                r['steps'] = dedupe(r['steps'] + [s['id']])
        return {'parts': parts, 'fasteners': sorted(fas.values(), key=fastener_key),
                'consumables': list(con.values()), 'tools': sorted(tools.values(), key=lambda r: r['tool'].lower()),
                'time_min': sum(s.get('time_min') or 0 for s in steps),
                'wait_min': sum(s.get('wait_min') or 0 for s in steps)}

    def texts(self):
        """All words a reader sees (for the glossary filter)."""
        out = []
        for s in self.steps:
            out += [s.get('title', ''), s.get('goal', '')] + [a['do'] for a in s['actions_n']]
            out += [c.get('text', '') + ' ' + c.get('target', '') for c in s['checks']]
            out += [x.get('text', '') for x in s.get('safety', [])] + s['tools_n']
            out += [g.get('problem', '') + ' ' + g.get('fix', '') for g in s.get('can_go_wrong', [])]
            out += [f['item'] for f in s['fasteners']] + [j['spec'] for j in s['joints'] + s['wires']]
            out += [(w['wire'].get('connector') or '') + ' AWG strain relief bend radius' for w in s['wires']]
        out += [x.get('text', '') for x in self.meta.get('safety', [])]
        return '\n'.join(out)


def dedupe(xs):
    seen, out = set(), []
    for x in xs:
        k = x.lower() if isinstance(x, str) else json.dumps(x, sort_keys=True)
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out


def fastener_key(r):
    """Sort fasteners by thread size then length: M2 < M3 < M4; screws before washers and nuts."""
    m = re.match(r'M(\d+(?:\.\d+)?)(?:x(\d+(?:\.\d+)?))?', r['item'])
    screw = bool(m and m.group(2)) and not re.search(r'insert|heat-set', r['item'], re.I)
    return (float(m.group(1)) if m else 99, 0 if screw else 1, float(m.group(2)) if screw else 0, r['item'])


def glossary(manual, path=os.path.join(KIT, 'glossary.json')):
    """Glossary terms that the manual uses, alphabetical, each with a compiled regex for its words."""
    if not os.path.exists(path):
        return []
    text = manual.texts()
    out = []
    for t in load_json(path).get('terms', []):
        words = [t['term']] + t.get('alias', [])
        rx = re.compile(r'(?<![\w-])(' + '|'.join(re.escape(w) for w in sorted(words, key=len, reverse=True)) + r')(?![\w-])',
                        re.I)
        if rx.search(text):
            out.append(dict(t, rx=rx))
    return sorted(out, key=lambda t: t['term'].lower())
