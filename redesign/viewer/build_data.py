"""Collect everything the web viewer shows into viewer/data/<dataset>/ (stdlib only, < 1 s).

    python -I redesign/viewer/build_data.py              # the real aircraft  -> data/aircraft/
    python -I redesign/viewer/build_data.py --examples   # the generic test aircraft -> data/examples/

Reads (nothing is edited):
  geometry     redesign/blender/out/<examples|aircraft>/glb/assembly.glb   (from blender/export_glb.py)
  parts+edges  redesign/interfaces/interfaces.json  (examples: interfaces/example-output/interfaces.json)
  vendor/cost  redesign/subsystems/*/parts.csv      (examples: viewer/examples/parts.csv)
  claims       redesign/proofs/out/graph.json       (examples: proofs/examples/out/graph.json)
  mass budget  redesign/params/mass_budget.json     (examples: fusion/examples/mass_budget.json)
Any input may be missing; the viewer then shows what it has and says what is missing.

Writes data/<dataset>/:
  assembly.glb      copy of the GLB (fetched with a progress bar over http/https)
  assembly.glb.js   the same bytes as base64, so index.html also works by double-click (file://)
  viewer-data.js    window.VIEWER_DATA = {...}: parts, edges, connection types, claims, budget, warnings
  viewer-data.json  the same object, for other tools

Exit 1 only if the output cannot be written. Cross-checks (part in GLB but not in interfaces, status or mass
differing between them, claims naming unknown parts) are printed as warnings and shown in the viewer.
"""
import argparse, base64, csv, glob, hashlib, json, os, struct, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.dirname(HERE)  # redesign/


def rel(p):
    return os.path.relpath(p, os.path.dirname(RED)).replace('\\', '/') if p else None


def load_json(p):
    if p and os.path.isfile(p):
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    return None


def glb_nodes(path):
    """Node extras from a GLB's JSON chunk (no geometry decoding needed)."""
    with open(path, 'rb') as f:
        b = f.read()
    if b[:4] != b'glTF':
        raise ValueError('not a GLB file')
    n = struct.unpack('<I', b[12:16])[0]
    j = json.loads(b[20:20 + n])
    return b, [nd.get('extras', {}) for nd in j.get('nodes', [])]


def read_csvs(paths):
    rows = {}
    for p in paths:
        with open(p, encoding='utf-8-sig', newline='') as f:
            for i, r in enumerate(csv.DictReader(f), start=2):
                pid = (r.get('part_id') or '').strip()
                if pid:
                    rows[pid] = dict(r, csv_ref='%s row %d' % (rel(p), i))
    return rows


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--examples', action='store_true', help='the generic test aircraft')
    ap.add_argument('--glb', help='folder with assembly.glb')
    ap.add_argument('--interfaces', help='merged interfaces.json')
    ap.add_argument('--proofs', help='proof graph.json')
    ap.add_argument('--budget', help='mass_budget.json')
    ap.add_argument('--csv', nargs='*', help='parts.csv files')
    ap.add_argument('--out', help='output folder')
    a = ap.parse_args()
    ds = 'examples' if a.examples else 'aircraft'
    if a.examples:
        d = dict(glb=os.path.join(RED, 'blender/out/examples/glb'),
                 interfaces=os.path.join(RED, 'interfaces/example-output/interfaces.json'),
                 proofs=os.path.join(RED, 'proofs/examples/out/graph.json'),
                 budget=os.path.join(RED, 'fusion/examples/mass_budget.json'),
                 csv=[os.path.join(HERE, 'examples/parts.csv')],
                 proofs_viewer='../proofs/viewer/index.html?data=examples#node={id}',
                 proof_alias=None)   # proof_alias: a prefix to strip from claim part ids (none needed now)
    else:
        d = dict(glb=os.path.join(RED, 'blender/out/aircraft/glb'),
                 interfaces=os.path.join(RED, 'interfaces/interfaces.json'),
                 proofs=os.path.join(RED, 'proofs/out/graph.json'),
                 budget=os.path.join(RED, 'params/mass_budget.json'),
                 csv=sorted(glob.glob(os.path.join(RED, 'subsystems/*/parts.csv'))),
                 proofs_viewer='../proofs/viewer/index.html?data=redesign#node={id}', proof_alias=None)
    for k in ('glb', 'interfaces', 'proofs', 'budget', 'csv'):
        if getattr(a, k):
            d[k] = getattr(a, k)
    out = a.out or os.path.join(HERE, 'data', ds)
    warn = []

    # ---- interfaces (parts, edges, connection types) ----
    itf = load_json(d['interfaces']) or {}
    if not itf:
        warn.append('no interfaces file at %s' % rel(d['interfaces']))
    parts = {p['id']: dict(p) for p in itf.get('parts', [])}
    edges = itf.get('edges', [])
    ctypes = {c['id']: c for c in itf.get('connection_types', [])}

    # ---- geometry ----
    glb_path = os.path.join(d['glb'], 'assembly.glb')
    glb_bytes, in_glb = None, {}
    if os.path.isfile(glb_path):
        glb_bytes, extras = glb_nodes(glb_path)
        for x in extras:
            if x.get('part_id'):
                in_glb[x['part_id']] = x
    else:
        warn.append('no 3-D model: %s (run blender/export_glb.py)' % rel(glb_path))
    for pid, x in in_glb.items():
        p = parts.get(pid)
        if p is None:  # in the model but not in the knowledge graph: show it, flag it
            parts[pid] = {k: x.get(k) for k in ('name', 'subsystem', 'status', 'mass_g', 'material', 'make_or_buy')}
            parts[pid].update(id=pid, cg_xyz_m=None)
            warn.append('%s is in the 3-D model but not in interfaces.json' % pid)
            continue
        if x.get('status') != p.get('status'):
            warn.append('%s status: model %s, interfaces %s' % (pid, x.get('status'), p.get('status')))
        if num(x.get('mass_g')) != num(p.get('mass_g')):
            warn.append('%s mass: model %s g, interfaces %s g' % (pid, x.get('mass_g'), p.get('mass_g')))
    for pid, p in parts.items():
        p['in_model'] = pid in in_glb
        if glb_bytes and not p['in_model'] and p.get('flight', True) is not False:
            warn.append('%s (%s) has no geometry in the 3-D model' % (pid, p.get('name')))

    # ---- parts.csv (vendor, cost, process) ----
    rows = read_csvs([c for c in d['csv'] if os.path.isfile(c)])
    for pid, r in rows.items():
        p = parts.get(pid)
        if p is None:
            warn.append('%s is in %s but not in interfaces.json' % (pid, r['csv_ref']))
            continue
        p.update(vendor=r.get('vendor_or_file') or None, unit_cost_usd=num(r.get('unit_cost_usd')),
                 qty=num(r.get('qty')), process=r.get('process') or None, csv_ref=r['csv_ref'])

    # ---- SPEC.md links (real aircraft only) ----
    for p in parts.values():
        spec = os.path.join(RED, 'subsystems', p.get('subsystem') or '-', 'SPEC.md')
        p['spec'] = '../subsystems/%s/SPEC.md' % p['subsystem'] if os.path.isfile(spec) else None

    # ---- claims from the proof chain ----
    claims = []
    g = load_json(d['proofs'])
    if g:
        for n in g.get('nodes', []):
            if n.get('type') != 'claim' or not n.get('parts'):
                continue
            ids = []
            for q in n['parts']:
                q2 = q[len(d['proof_alias']):] if d['proof_alias'] and q.startswith(d['proof_alias']) else q
                if q2 in parts:
                    ids.append(q2)
                else:
                    warn.append('claim %s names %s, not a part of this aircraft' % (n['id'], q))
            claims.append({k: n.get(k) for k in ('id', 'title', 'value', 'unit', 'limit', 'status', 'how', 'margin')}
                          | {'parts': ids})
    else:
        warn.append('no proof graph at %s (run proofs/build_graph.py)' % rel(d['proofs']))

    budget = load_json(d['budget'])
    if budget is None:
        warn.append('no mass budget at %s' % rel(d['budget']))

    data = {
        'schema': 'dbf-viewer/1', 'dataset': ds, 'generated': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()),
        'sources': {k: rel(d[k]) if k != 'csv' else [rel(c) for c in d['csv'] if os.path.isfile(c)]
                    for k in ('glb', 'interfaces', 'proofs', 'budget', 'csv')},
        'glb': {'file': 'assembly.glb', 'bytes': len(glb_bytes),
                'sha256': hashlib.sha256(glb_bytes).hexdigest()} if glb_bytes else None,
        'frame': 'aircraft frame: metres, x aft, y right, z up. glTF (x, y, z) = aircraft (x, z, -y).',
        'parts': sorted(parts.values(), key=lambda p: p['id']),
        'edges': edges, 'connection_types': ctypes, 'claims': claims,
        'proofs_viewer': d['proofs_viewer'], 'budget': budget, 'warnings': warn,
    }
    os.makedirs(out, exist_ok=True)
    # 'generated' = when the DATA last changed: keep the old stamp when nothing else differs, so re-running the
    # checks does not dirty the committed data files
    old = load_json(os.path.join(out, 'viewer-data.json')) or {}
    if old.get('generated') and dict(old, generated=None) == dict(data, generated=None):
        data['generated'] = old['generated']
    js = json.dumps(data, indent=1, ensure_ascii=False)
    with open(os.path.join(out, 'viewer-data.json'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(js + '\n')
    with open(os.path.join(out, 'viewer-data.js'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('// generated by redesign/viewer/build_data.py; do not edit\nwindow.VIEWER_DATA = %s;\n' % js)
    for name in ('assembly.glb', 'assembly.glb.js'):
        p = os.path.join(out, name)
        if os.path.exists(p) and not glb_bytes:
            os.remove(p)  # never leave a stale model next to new data
    if glb_bytes:
        with open(os.path.join(out, 'assembly.glb'), 'wb') as f:
            f.write(glb_bytes)
        with open(os.path.join(out, 'assembly.glb.js'), 'w', encoding='ascii', newline='\n') as f:
            f.write('window.VIEWER_GLB_B64 = "%s";\n' % base64.b64encode(glb_bytes).decode())
    print('%s: %d parts (%d with geometry), %d edges, %d claims, model %s -> %s'
          % (ds, len(parts), sum(p['in_model'] for p in parts.values()), len(edges), len(claims),
             '%.0f kB' % (len(glb_bytes) / 1024) if glb_bytes else 'missing', rel(out)))
    for w in warn:
        print('  WARN', w)
    return 0


if __name__ == '__main__':
    sys.exit(main())
