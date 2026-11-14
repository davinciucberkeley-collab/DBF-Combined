"""render_figures.py - render the figures and build steps listed in a JSON spec (PNG + JSON sidecar + annotated SVG).

    blender -b --factory-startup -P redesign/blender/render_figures.py -- --examples
    blender -b --factory-startup -P redesign/blender/render_figures.py -- --spec my_figs.json [--root DIR]
        [--only id,id] [--engine CYCLES|EEVEE] [--samples 48] [--device AUTO|CPU] [--percent 50] [--out DIR] [--png]
--examples uses the example aircraft and redesign/blender/examples/figures_example.json.
--percent 50 renders half size for quick drafts. --png also rasterises each SVG (needs Edge/Chrome; optional).
Output: redesign/blender/out/<examples|aircraft>/figures/<id>.png/.jpg/.json/.svg

Spec (JSON):
{
 "scene": "studio",                        default scene for every figure: studio | workbench
 "figures": [ {
    "id": "iso",                           file name
    "camera": "iso" | {"preset": "closeup", "fit": ["WNG-005"], "lens": 70, "az": 30, "el": 25},
                                           fit: "visible" (default) | "all" (same framing for every step) | [ids]
    "focus": [...], "context": ["*"], "ghost": [...], "hide": [...], "xray": [...]   fnmatch patterns on part /
                                           edge ids; xray = ghosted although in focus (see inside a box)
    "explode": 1.0 | {"factor": 1.0, "root": "FUS-001", "gap": 0.06, "overrides": {"FUS-002": [0, 0, 1]}},
    "pose": {"E-WNG-04": 20},              revolute deg / slider m
    "colour": "material" | "subsystem" | "status",
    "callouts": ["WNG-001", "E-WNG-01", {"at": [x, y, z], "text": "..."}, {"item": "E-WNG-05", "text": "..."}]
              | "parts" (every shown part) | "auto" (focus parts + their fastened / wired edges),
    "caption": {"title": "...", "sub": "..."} } ],
 "steps": {"prefix": "step", "scene": "workbench", "camera": "iso", "rest": "hide" | "ghost",
           "list": [ {"title": "...", "check": "...", "add": ["FUS-*", "E-FUS-03"], "xray": ["FUS-001"],
                      "camera": ..., "callouts": ...} ] }
}
A step shows the parts added in that step in orange, the parts of earlier steps as built, the rest hidden (or ghosted).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import blender_backend as bb     # noqa: E402
import render_kit as rk          # noqa: E402


def args():
    import argparse
    ap = argparse.ArgumentParser(prog='render_figures.py')
    ap.add_argument('--examples', action='store_true')
    ap.add_argument('--root')
    ap.add_argument('--spec')
    ap.add_argument('--only', default='')
    ap.add_argument('--engine', default='CYCLES')
    ap.add_argument('--samples', type=int, default=48)
    ap.add_argument('--device', default='AUTO', help='AUTO (GPU if present) | CPU')
    ap.add_argument('--percent', type=int, default=100)
    ap.add_argument('--out')
    ap.add_argument('--png', action='store_true')
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return ap.parse_args(argv)


def expand_steps(spec):
    """Turn the "steps" block into ordinary figure dicts."""
    st = spec.get('steps')
    if not st:
        return []
    out, done = [], []
    for n, s in enumerate(st['list'], 1):
        add = s['add']
        f = {'id': '%s_%d' % (st.get('prefix', 'step'), n), 'scene': s.get('scene', st.get('scene')),
             'camera': s.get('camera', st.get('camera', 'iso')),
             'focus': add, 'context': list(done), 'ghost': list(s.get('ghost', [])), 'xray': list(s.get('xray', [])),
             'callouts': s.get('callouts', 'auto'),
             'caption': {'title': 'Step %d: %s' % (n, s['title']), 'sub': ('Check: ' + s['check']) if s.get('check') else ''}}
        if st.get('rest') == 'ghost':
            f['ghost'] += ['*']
        for k in ('pose', 'explode', 'colour'):
            if k in s:
                f[k] = s[k]
        out.append(f)
        done += add
    return out


def callouts_for(S, f):
    c = f.get('callouts') or []
    role = S.role
    if c == 'parts':
        return [i for i in S.be.objects if role.get(i) in ('focus', 'context')]
    if c == 'auto':
        focus = [i for i in S.be.objects if role.get(i) == 'focus']
        seen = set()
        out = []
        for e in S.graph.edges.values():
            a, b = e.get('part_a'), e.get('part_b')
            if (role.get(a) == 'focus' or role.get(b) == 'focus') and role.get(a) not in (None, 'hide') \
                    and role.get(b) not in (None, 'hide') and (e.get('joint_stack') or e.get('wire')):
                key = json.dumps(e.get('joint_stack') or e.get('wire'), sort_keys=True)   # mirrored twins: label once
                if key in seen:
                    continue
                seen.add(key)
                out.append(e['id'])
        labelled = {S.graph.edges[e]['part_a'] for e in out}
        return [p for p in focus if p not in labelled][:6] + out
    return c


def render_one(S, f, out_dir, png):
    S.reset()
    S.be.recolour(f.get('colour', 'material'))
    S.roles(focus=f.get('focus', []), context=f.get('context', ['*']), ghost=f.get('ghost', []), hide=f.get('hide', []),
            xray=f.get('xray', []))
    exp = f.get('explode')
    if exp:
        exp = exp if isinstance(exp, dict) else {'factor': exp}
        S.explode(exp.get('factor', 1.0), exp.get('root'), exp.get('gap', 0.06), exp.get('overrides'))
    for e, v in (f.get('pose') or {}).items():
        S.pose(e, v)
    for c in callouts_for(S, f):
        if isinstance(c, dict):
            S.callout(c.get('item'), c.get('text'), c.get('detail'), c.get('at'))
        else:
            S.callout(c)
    cam = f.get('camera', 'iso')
    cam = cam if isinstance(cam, dict) else {'preset': cam}
    S.camera(cam.get('preset', 'iso'), fit=cam.get('fit', 'visible'), lens=cam.get('lens', 50),
             az=cam.get('az'), el=cam.get('el'), frame=cam.get('frame'))
    if f.get('caption'):
        S.caption(f['caption'].get('title', ''), f['caption'].get('sub', ''))
    meta = S.render(os.path.join(out_dir, f['id']), annotate=False)
    import annotate
    annotate.build(os.path.join(out_dir, f['id'] + '.json'), png=png)
    return meta


def main():
    a = args()
    spec_path = a.spec or os.path.join(HERE, 'examples', 'figures_example.json')
    with open(spec_path, encoding='utf-8') as fh:
        spec = json.load(fh)
    figs = spec.get('figures', []) + expand_steps(spec)
    if a.only:
        want = a.only.split(',')
        figs = [f for f in figs if any(f['id'] == w or f['id'].startswith(w) for w in want)]
    out_dir = a.out or os.path.join(HERE, 'out', 'examples' if a.examples else 'aircraft', 'figures')
    t0 = time.time()
    be, ctx, graph, results = bb.build(a.examples, a.root)
    print('built in %.1f s' % (time.time() - t0))
    S = rk.Stage(be, ctx, graph, spec.get('scene', 'studio'), engine=a.engine, samples=a.samples,
                 device=a.device)
    S.set_size(rk.W * a.percent / 100, rk.H * a.percent / 100)
    times = []
    for f in figs:
        scene = f.get('scene') or spec.get('scene', 'studio')
        if scene != S.kind:
            S.set_kind(scene)
        t1 = time.time()
        meta = render_one(S, f, out_dir, a.png)
        times.append((f['id'], meta['render_s'], time.time() - t1))
    print('\n%-14s %9s %9s' % ('figure', 'render s', 'total s'))
    for i, r, t in times:
        print('%-14s %9.1f %9.1f' % (i, r, t))
    print('all figures: %.1f s -> %s' % (time.time() - t0, out_dir))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
