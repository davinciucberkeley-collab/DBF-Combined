"""make_drawings_a.py - engineering drawings of every part the team makes for concept A, generated from the CAD.

    python -B redesign/qp/A/drawings/make_drawings_a.py            # all stages
    python -B redesign/qp/A/drawings/make_drawings_a.py --compose  # sheets only (re-uses the Blender renders)

Stage 1 (this file, stub backend, seconds): runs the concept A build (qp/A/cad/model, the same modules as build_a.py /
check.py / the GLB export), picks the made parts (make_or_buy 'make', not lumps or mass proxies), groups identical and
mirror-image parts onto one sheet, and writes out/_work/jobs.json: every body and every shop cut of each part, plus a
feature table in the part's own design frame (component-local axes, mm).
Stage 2 (render_drawings_blender.py, inside Blender): meshes each part exactly as the shop STL (manufacturing/blender_mesh.py:
bodies united, shop cuts subtracted), moves it into its design frame, writes the STL (printed parts) and renders four
orthographic line views (hidden edges dashed) with their mm-per-pixel mapping.
Stage 3 (compose()): one PDF sheet per drawing (views, overall dimensions, feature table, notes, title block), the combined
out/DRAWINGS-A.pdf and the index out/DRAWINGS-A.md.

Dimensions are the CAD's; values the CAD marks EST stay EST on the sheet (feature names carry the CAD wording).
"""
import argparse
import json
import math
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
QA = os.path.dirname(HERE)
REDESIGN = os.path.dirname(os.path.dirname(QA))
ROOT = os.path.dirname(REDESIGN)
MODEL = os.path.join(QA, 'cad', 'model')
OUT = os.path.join(HERE, 'out')
WORK = os.path.join(OUT, '_work')
for _p in (os.path.join(REDESIGN, 'fusion'), os.path.join(REDESIGN, 'interfaces'), os.path.join(REDESIGN, 'manufacturing'), os.path.join(QA, 'cad')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
BLENDER = os.environ.get('BLENDER', r'C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe')

SKIP = {'HRD-001', 'HRN-001'}                     # lumps (hardware, harness remainder): no single shape to draw
FAMILY = {'PETG (printed)': 'print', 'CFRP tube': 'tube', 'CFRP rod': 'tube'}


def family(mat):
    if mat and 'lead' in mat.lower():
        return 'other'                         # lead strip + holder (WNG-007): cut, not a single print
    if mat in FAMILY:
        return FAMILY[mat]
    m = (mat or '').lower()
    if 'petg' in m or 'print' in m:
        return 'print'
    if 'foam' in m or 'xps' in m or 'eva' in m:
        return 'foam'
    return 'other'


def base_id(pid):
    p = pid.split('-')
    return '-'.join(p[:2]) if len(p) > 2 else pid


# ----------------------------------------------------------------------------- geometry helpers (pure python)
def inv(M):
    R = [r[:3] for r in M[:3]]
    t = [M[i][3] for i in range(3)]
    Rt = [[R[j][i] for j in range(3)] for i in range(3)]
    ti = [-sum(Rt[i][k] * t[k] for k in range(3)) for i in range(3)]
    return [Rt[0] + [ti[0]], Rt[1] + [ti[1]], Rt[2] + [ti[2]], [0, 0, 0, 1]]


def mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def app(M, p):
    return tuple(M[i][0] * p[0] + M[i][1] * p[1] + M[i][2] * p[2] + M[i][3] for i in range(3))


def appv(M, v):
    return tuple(M[i][0] * v[0] + M[i][1] * v[1] + M[i][2] * v[2] for i in range(3))


AX = {'X': (1.0, 0.0, 0.0), 'Y': (0.0, 1.0, 0.0), 'Z': (0.0, 0.0, 1.0)}


def feature(s, M):
    """One CAD shape -> a feature record in the part frame (M: shape frame -> part frame), mm."""
    pts = [app(M, p) for p in s.points()]
    lo = [min(p[i] for p in pts) * 1e3 for i in range(3)]
    hi = [max(p[i] for p in pts) * 1e3 for i in range(3)]
    f = dict(name=s.name or '(unnamed)', kind=s.kind, lo=[round(v, 2) for v in lo], hi=[round(v, 2) for v in hi])
    if s.kind == 'revolve':
        a = [p[0] for p in s.profile]
        r = [p[1] for p in s.profile]
        ax = appv(M, AX[s.axis] if isinstance(s.axis, str) else s.axis)
        c = app(M, s.center)
        f.update(d_out=round(2e3 * max(r), 2), d_in=round(2e3 * min(r), 2) if min(r) > 1e-9 else 0.0,
                 length=round(1e3 * (max(a) - min(a)), 2),
                 start=[round(1e3 * (c[i] + ax[i] * min(a)), 2) for i in range(3)], axis=[round(v, 4) for v in ax])
    elif s.kind == 'prism':
        f.update(depth=round(abs(s.depth) * 1e3, 2), axis=s.axis)
    return f


def describe(f, at=None):
    """Size and position text; at = every instance of a merged pattern."""
    at = at or [f]
    if f['kind'] == 'revolve':
        ax = f['axis']
        k = max(range(3), key=lambda i: abs(ax[i]))
        if abs(ax[k]) > 0.9999:                       # axis-aligned: span along the axis + centre in the other two
            o = [i for i in range(3) if i != k]
            d = 'dia %.2f' % f['d_out'] + (' / %.2f bore' % f['d_in'] if f['d_in'] else '')
            spans = sorted({(g['lo'][k], g['hi'][k]) for g in at})
            span = '; '.join('%s %.1f..%.1f' % ('xyz'[k], a, b) for a, b in spans[:3]) + (' ...' if len(spans) > 3 else '')
            cs = ', '.join('(%s %.1f, %s %.1f)' % ('xyz'[o[0]], (g['lo'][o[0]] + g['hi'][o[0]]) / 2, 'xyz'[o[1]], (g['lo'][o[1]] + g['hi'][o[1]]) / 2) for g in at)
            return '%s along %s, %s; centre %s' % (d, 'xyz'[k], span, cs)
        d = 'dia %.2f' % f['d_out'] + (' / %.2f bore' % f['d_in'] if f['d_in'] else '') + ' x %.2f long' % f['length']
        ax = f['axis']
        k = max(range(3), key=lambda i: abs(ax[i]))
        axs = ('along %s%s' % ('+' if ax[k] > 0 else '-', 'xyz'[k])) if abs(ax[k]) > 0.9999 else 'axis (%.3f, %.3f, %.3f)' % tuple(ax)
        return d + ', from (%.1f, %.1f, %.1f) %s' % (tuple(f['start']) + (axs,))
    if len(at) > 1:
        return '; '.join(describe(g) for g in at[:6]) + (' ...' if len(at) > 6 else '')
    ext = [f['hi'][i] - f['lo'][i] for i in range(3)]
    return '%.2f x %.2f x %.2f box, x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f' % (tuple(ext) + (f['lo'][0], f['hi'][0], f['lo'][1], f['hi'][1], f['lo'][2], f['hi'][2]))


def collapse(feats):
    """Merge identical-size features with the same name (patterns): 'n x'."""
    out = []
    for f in feats:
        key = (f['name'], f['kind'], f.get('d_out'), f.get('d_in'), f.get('length'), f.get('depth'),
               None if f['kind'] == 'revolve' else tuple(round(f['hi'][i] - f['lo'][i], 1) for i in range(3)))
        for g in out:
            if g['key'] == key:
                g['n'] += 1
                g['at'].append(f)
                break
        else:
            out.append(dict(key=key, n=1, at=[f], f=f))
    return out


def signature(feats):
    """Mirror-insensitive signature of a part's features (names + sizes + |position|)."""
    return sorted((f['name'], f['kind'], f.get('d_out'), f.get('length'),
                   tuple(round(abs((f['lo'][i] + f['hi'][i]) / 2), 1) for i in range(3)),
                   tuple(round(f['hi'][i] - f['lo'][i], 1) for i in range(3))) for f in feats)


def signed(feats):
    return sorted((f['name'], tuple(round((f['lo'][i] + f['hi'][i]) / 2, 1) for i in range(3))) for f in feats)


# ----------------------------------------------------------------------------- stage 1
def build_ctx():
    import build_all
    from backends.stub_backend import StubBackend
    ctx, _g, _r = build_all.build(StubBackend(), *build_all.roots(False, root=MODEL), log=lambda *a: None)
    return ctx


def jobs():
    import cad_source
    import a_model as m
    ctx = build_ctx()
    parts = m.PARTS
    groups = {}
    for pid, c in ctx.components.items():
        info = parts.get(pid, {})
        if pid in SKIP or getattr(c, 'proxy', False) or (c.make_or_buy or info.get('make_or_buy')) != 'make' or not c.shapes:
            continue
        Mi = inv(c.matrix())
        body = [feature(s, [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) for s in c.shapes]
        cuts = []
        for s, Mc, note, shop in c.cuts:          # the cut's note names a seat ('pin hole 3.0 mm through the tube'); else the shape name
            f = feature(s, mul(Mi, Mc if Mc is not None else c.matrix()))
            f['name'] = (note or s.name or '(unnamed cut)') + ('' if shop else ' [drill / cut on assembly]')
            cuts.append(f)
        rec = dict(part=pid, name=c.name, material=c.material or info.get('material'), mass_g=c.mass_g, matrix=c.matrix(),
                   bodies=[cad_source.shape_to_json(s) for s in c.shapes],
                   cuts=[[cad_source.shape_to_json(s), Mw] for s, Mw in c.world_cuts(shop_only=True)],
                   body_features=body, cut_features=cuts, family=family(c.material or info.get('material')))
        groups.setdefault(base_id(pid), []).append(rec)
    out = []
    for b, recs in sorted(groups.items()):
        sig = {}
        for r in recs:
            sig.setdefault(json.dumps(signature(r['body_features'] + r['cut_features'])), []).append(r)
        for k, (s, rs) in enumerate(sorted(sig.items(), key=lambda kv: kv[1][0]['part'])):
            rs.sort(key=lambda r: r['part'])
            lead = rs[0]
            did = b if len(sig) == 1 else lead['part']
            rs.sort(key=lambda r: (not r['part'].endswith(('-R', '-UR', '-RU')), r['part']))   # show the right-hand part
            lead = rs[0]
            same = signed(lead['body_features'] + lead['cut_features'])
            lead.update(id=did, members=[r['part'] for r in rs], qty=len(rs),
                        mirrored=[r['part'] for r in rs[1:] if signed(r['body_features'] + r['cut_features']) != same],
                        member_jobs=[dict(id=r['part'], part=r['part'], matrix=r['matrix'], bodies=r['bodies'], cuts=r['cuts'])
                                     for r in rs[1:]] if lead['family'] == 'print' else [])   # every printed part gets its own STL
            out.append(lead)
    os.makedirs(WORK, exist_ok=True)
    with open(os.path.join(WORK, 'jobs.json'), 'w') as fh:
        json.dump(out, fh)
    print('stage 1: %d drawings for %d made parts' % (len(out), sum(j['qty'] for j in out)))
    return out


def render():
    r = subprocess.run([BLENDER, '-b', '--factory-startup', '--python-exit-code', '1', '-P', os.path.join(HERE, 'render_drawings_blender.py'),
                        '--', os.path.join(WORK, 'jobs.json'), WORK], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.startswith('drw ') or 'Error' in l or 'Traceback' in l]
    print('\n'.join(lines[-80:]))
    if r.returncode:
        print(r.stderr[-3000:])
        raise SystemExit('stage 2 (Blender) failed')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--compose', action='store_true')
    ap.add_argument('--jobs-only', action='store_true')
    a = ap.parse_args()
    if not a.compose:
        jobs()
        if a.jobs_only:
            raise SystemExit
        render()
    import compose_drawings
    compose_drawings.main()
