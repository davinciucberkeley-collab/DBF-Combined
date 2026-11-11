"""cad_source.py - the one place the shop exporter reads the CAD. Read-only adapter over redesign/fusion.

It runs the SAME build(ctx) modules as check.py / BuildAll / the Blender GLB export (fusion/build_all.py, stub
backend: pure python, seconds) and hands out what the shop needs:

    build()                         -> ctx (every component with its recorded fusionkit Shapes)
    print_jobs(ctx)                 -> mesh jobs for the printed parts (bodies filtered / grouped per shopconfig.PRINT)
    sheet_outlines(ctx, part, ...)  -> flat outlines of sheet bodies (foam board, Coroplast) in mm
    shape_to_json / shape_from_json -> transport of shapes to the Blender mesher

Nothing under subsystems/, fusion/, blender/ or params/ is modified. Bytecode writing is switched off so no
__pycache__ appears in other agents' folders.
"""
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(HERE)
FUSION = os.path.join(REDESIGN, 'fusion')
for _p in (FUSION, os.path.join(REDESIGN, 'interfaces'), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fusionkit as fk            # noqa: E402
import shopconfig as cfg          # noqa: E402

STATION_RE = re.compile(r'^([A-Z]{3}-\d{3})(?:-([A-Z]{1,2}))?$')
SIGNS = {'': (1, 1), 'R': (1, 1), 'L': (-1, 1), 'UR': (1, 1), 'UL': (-1, 1), 'LR': (1, -1), 'LL': (-1, -1),
         'U': (1, 1), 'C': (1, 1)}


def split_id(pid):
    """'FIN-003-UR' -> ('FIN-003', 'UR'); 'POD-002' -> ('POD-002', '')."""
    m = STATION_RE.match(pid)
    return (m.group(1), m.group(2) or '') if m else (pid, '')


def build(log=None):
    """Stub build of redesign/subsystems in modules.txt order. Returns (ctx, results)."""
    import build_all
    from backends.stub_backend import StubBackend
    out = []
    ctx, _graph, results = build_all.build(StubBackend(), *build_all.roots(False), log=out.append)
    if log:
        for sub, f, ok, _ms, err in results:
            if not ok:
                log('CAD module FAILED %s/%s: %s' % (sub, f, err))
    return ctx, results


def params():
    with open(os.path.join(REDESIGN, 'params', 'params.json'), encoding='utf-8') as f:
        return json.load(f)


def local_params(sub):
    p = os.path.join(REDESIGN, 'subsystems', sub, 'params.json')
    with open(p, encoding='utf-8') as f:
        return json.load(f)


# ----------------------------------------------------------------------------- shape transport
def shape_to_json(s):
    d = {'kind': s.kind, 'name': s.name or ''}
    if s.kind == 'prism':
        d.update(axis=s.axis, offset=s.offset, depth=s.depth, loops=[[list(p) for p in l] for l in s.loops])
    elif s.kind == 'revolve':
        d.update(axis=s.axis, center=list(s.center), profile=[list(p) for p in s.profile])
    elif s.kind == 'loft':
        d.update(axis=s.axis, smooth=bool(s.smooth), sections=[[o, [list(p) for p in l]] for o, l in s.sections])
    return d


def shape_from_json(d):
    d = dict(d)
    kind, name = d.pop('kind'), d.pop('name', None)
    if kind == 'prism':
        d['loops'] = [[tuple(p) for p in l] for l in d['loops']]
    elif kind == 'revolve':
        d['center'] = tuple(d['center'])
        d['profile'] = [tuple(p) for p in d['profile']]
    elif kind == 'loft':
        d['sections'] = [(o, [tuple(p) for p in l]) for o, l in d['sections']]
    return fk.Shape(kind, name, **d)


# ----------------------------------------------------------------------------- printed parts
def _keep(name, spec):
    if spec.get('include') and not re.search(spec['include'], name or ''):
        return False
    if spec.get('exclude') and re.search(spec['exclude'], name or ''):
        return False
    return True


def mirror_dir(d, station):
    sy, sz = SIGNS.get(station, (1, 1))
    return (d[0], d[1] * sy, d[2] * sz)


def print_jobs(ctx, issues):
    """One job per (component, print group): the bodies to union into one printed solid (or several islands).
    Returns a list of dicts: id, part (component id), base, station, group, material, colour, orient, bodies."""
    jobs = []
    seen = set()
    for pid, comp in ctx.components.items():
        base, st = split_id(pid)
        if base in cfg.SPARE_COMPONENTS:
            continue
        spec = cfg.PRINT.get(base)
        if spec is None:
            mat = (comp.material or '').lower()
            if comp.make_or_buy == 'make' and ('printed' in mat or 'petg' in mat or 'asa' in mat or 'tpu' in mat) \
                    and 'vinyl' not in mat:
                issues.append('printed-looking part %s (%s) has no shopconfig.PRINT entry: not exported'
                              % (pid, comp.material))
            continue
        seen.add(base)
        bodies = [s for s in comp.shapes if _keep(s.name, spec)]
        if base == 'POD-008':
            jobs += spacer_jobs(ctx, comp, spec, issues)
            continue
        groups = spec.get('groups') or [('', r'.*')]
        used = set()
        for suffix, rx in groups:
            sel = [s for s in bodies if id(s) not in used and re.search(rx, s.name or '')]
            used.update(id(s) for s in sel)
            if not sel:
                issues.append('%s: print group "%s" matched no CAD body (regex %s)' % (pid, suffix, rx))
                continue
            jobs.append(_job(comp, base, st, suffix, spec, sel))
        left = [s.name for s in bodies if id(s) not in used]
        if left:
            issues.append('%s: bodies in no print group (not printed): %s' % (pid, ', '.join(sorted(set(left)))))
    for base in cfg.PRINT:
        if base not in seen:
            issues.append('shopconfig.PRINT has %s but the CAD has no component for it' % base)
    return jobs


def _job(comp, base, st, suffix, spec, shapes, colour=None, jid=None):
    orient = dict((spec.get('group_orient') or {}).get(suffix) or spec.get('orient') or {})
    if 'down' in orient:
        orient['down'] = mirror_dir(orient['down'], st)
    col = colour or (spec.get('colour') or {}).get(st, '')
    return {'id': jid or (comp.id + ('.' + suffix if suffix else '')), 'part': comp.id, 'base': base,
            'station': st, 'group': suffix, 'material': spec['material'], 'colour': col, 'orient': orient,
            'matrix': comp.matrix(), 'bodies': [shape_to_json(s) for s in shapes],
            'cad_volume_mm3': sum(s.volume_centroid()[0] for s in shapes) * 1e9}


def spacer_jobs(ctx, comp, spec, issues):
    """POD-008: the CAD models the flown 8 + 4 mm U-spacers; the set is 2/4/6/8 mm (pod/params.json spacer_set_m).
    Adapter: take the CAD spacer section and extrude it to each set thickness (same loop, same builder)."""
    P = local_params('pod')
    sizes = P['spacer_set_m']['value']
    colours = P.get('spacer_colour', {}).get('value', {})
    src = [s for s in comp.shapes if s.kind == 'prism' and 'spacer' in (s.name or '')]
    if not src:
        issues.append('POD-008: no spacer body in the CAD')
        return []
    s0 = src[0]
    out = []
    for t in sizes:
        s = fk.Shape('prism', 'spacer %g mm' % (t * 1000), axis=s0.axis, offset=s0.offset, loops=s0.loops,
                     depth=math.copysign(t, s0.depth))
        col = colours.get('%g' % t) or colours.get('%.3f' % t) or ''
        j = _job(comp, 'POD-008', '', '%gmm' % (t * 1000), spec, [s], colour=col)
        out.append(j)
    return out


# ----------------------------------------------------------------------------- flat sheet parts
def flat_outline(comp, shape, t_m, tol=0.0006):
    """Outline (loops in mm, outer first) of a sheet body of thickness t_m, or (None, reason).
    Case 1: prism whose depth = sheet thickness -> its own loops (plane coordinates).
    Case 2: prism whose loop is a thin rectangle (one side = thickness) -> rectangle (long side x depth)."""
    if shape.kind != 'prism':
        return None, 'not a prism'
    if any(abs(comp.R[i][j] - (1 if i == j else 0)) > 1e-9 for i in range(3) for j in range(3)):
        return None, 'rotated component'
    if abs(abs(shape.depth) - t_m) <= tol:
        loops = [[(u * 1000.0, v * 1000.0) for u, v in l] for l in shape.loops]
        return loops, 'section'
    us = [p[0] for p in shape.loops[0]]
    vs = [p[1] for p in shape.loops[0]]
    du, dv = max(us) - min(us), max(vs) - min(vs)
    if len(shape.loops) == 1 and len(shape.loops[0]) == 4 and min(du, dv) <= t_m + tol:
        L = max(du, dv) * 1000.0
        H = abs(shape.depth) * 1000.0
        return [[(0.0, 0.0), (L, 0.0), (L, H), (0.0, H)]], 'panel'
    return None, 'not a flat sheet body (depth %.1f mm, section %.1f x %.1f mm)' % (
        abs(shape.depth) * 1000, du * 1000, dv * 1000)
