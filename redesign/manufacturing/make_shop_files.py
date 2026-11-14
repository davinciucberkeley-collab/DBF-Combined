"""make_shop_files.py - K09-L shop files from the CAD builders (MF-01). One command, deterministic:

    python -B redesign/manufacturing/make_shop_files.py            (about 1-2 min; needs Blender 4.x for the STLs)

Options: --out DIR (default redesign/manufacturing/out) · --blender PATH (else $BLENDER, `blender` on PATH, or
C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe) · --no-stl (DXF/PDF/CSV only, no Blender).

Writes into out/ (wiped and rebuilt each run, so files never go stale):
    print/*.stl                 one STL per printed part geometry, mm, print orientation: <part>_<material>_x<qty>.stl
    jigs/*.stl                  printed jigs (JIG-01 posts, JIG-02 fin collar, JIG-03 cant gauge A/B)
    PRINT-LIST.csv              part, material, qty incl. spares, orientation, layer, perimeters, infill, supports,
                                estimated time and mass, source of every setting
    laser/*.dxf                 nested sheets: foam board (half-fin boards, pod board), Coroplast box panels,
                                3 mm ply (jig board/bar, handle strips, mat); laser/*_1to1_letter.pdf knife templates
    CUT-LIST.csv                every sheet piece: sheet file, size, qty, machine, kerf, fits which laser bed
    hotwire/                    WNG-001 root + tip templates (DXF) and a 1:1 tiled letter PDF with registration marks
    contact-sheet.png           every printed part on its bed;  dxf-preview.png  every nest
    CHECKS.md                   watertight / dimension / params checks (exit code 1 if any FAIL)
    SHOP-PACK.md                what each file is, the order to make them, the Jacobs machine
    manifest.json               sha256 of every output (re-run and diff to prove determinism)
Reads only; edits nothing under subsystems/, fusion/, blender/ or params/ (see README.md).
"""
import argparse
import csv
import glob
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np                 # noqa: E402

import cad_source as cs            # noqa: E402
import contact_sheet               # noqa: E402
import dxf                         # noqa: E402
import hotwire                     # noqa: E402
import jigs                        # noqa: E402
import k09kit as k9                # noqa: E402
import mesh_ops as mo              # noqa: E402
import shopconfig as cfg           # noqa: E402

REDESIGN = cs.REDESIGN
DEFAULT_BLENDER = 'C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe'
GENERATED = ('print', 'jigs', 'laser', 'hotwire', '_work')


class Report:
    def __init__(self):
        self.checks, self.issues = [], []

    def check(self, ok, what, detail=''):
        self.checks.append(('PASS' if ok else 'FAIL', what, detail))
        return ok

    def note(self, what, detail=''):
        self.checks.append(('NOTE', what, detail))


# ----------------------------------------------------------------------------- helpers
def find_blender(arg):
    for c in (arg, os.environ.get('BLENDER'), shutil.which('blender'), DEFAULT_BLENDER):
        if c and os.path.exists(c):
            return c
    return None


def parts_csv():
    rows = {}
    for f in sorted(glob.glob(os.path.join(REDESIGN, 'subsystems', '*', 'parts.csv'))):
        with open(f, encoding='utf-8') as fh:
            for r in csv.DictReader(fh):
                rows[r['part_id']] = r
    return rows


def first_int(s, default):
    m = re.search(r'\d+', s or '')
    return int(m.group()) if m else default


def infill_frac(s, default=0.2):
    m = re.search(r'(\d+)\s*%', s or '')
    return int(m.group(1)) / 100.0 if m else default


def estimate(vol, area, height, mat, layer, perims, infill):
    f = cfg.FILAMENT[mat]
    shell = min(vol, area * perims * cfg.LINE_W_MM)
    ext = shell + infill * max(vol - shell, 0.0)
    layers = max(1, math.ceil(height / layer))
    t_min = ext / f['flow'] / 60.0 + layers * cfg.LAYER_CHANGE_S / 60.0 + cfg.JOB_OVERHEAD_MIN
    return t_min, ext / 1000.0 * f['rho']


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def fmt(x, nd=1):
    return ('%.' + str(nd) + 'f') % x


# ----------------------------------------------------------------------------- printed parts
def run_blender(blender, jobs, work, rep):
    raw = os.path.join(work, 'raw')
    os.makedirs(raw, exist_ok=True)
    jp = os.path.join(work, 'jobs.json')
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(jobs, f)
    cmd = [blender, '-b', '--factory-startup', '--python-exit-code', '1', '-P',
           os.path.join(HERE, 'blender_mesh.py'), '--', jp, raw]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    with open(os.path.join(work, 'blender.log'), 'w', encoding='utf-8') as f:
        f.write(p.stdout + '\n----- stderr\n' + p.stderr)
    rp = os.path.join(raw, 'blender_report.json')
    if p.returncode != 0 or not os.path.exists(rp):
        rep.issues.append('Blender run failed (exit %s); see out/_work/blender.log' % p.returncode)
        return raw, {}
    print('  blender: %d jobs in %.0f s' % (len(jobs), time.time() - t0))
    with open(rp, encoding='utf-8') as f:
        return raw, json.load(f)


def process_meshes(all_jobs, raw, brep, rep):
    """Raw united meshes -> islands -> print orientation -> variants (identical geometry merged)."""
    variants = {}
    for job in all_jobs:
        r = brep.get(job['id'])
        if not r or not r.get('ok'):
            rep.issues.append('%s: Blender union failed: %s' % (job['id'], (r or {}).get('error', 'no result')))
            continue
        tris = mo.read_stl(os.path.join(raw, job['id'] + '.stl'))
        verts, faces = mo.weld(tris)
        isl = mo.islands(faces, len(verts))
        if len(isl) > 1 and not job['group'] and not job['base'].startswith('JIG-'):
            rep.issues.append('%s: the united CAD bodies form %d separate pieces (a body does not touch the rest); '
                              'each piece is its own STL - check the CAD' % (job['id'], len(isl)))
        for ix in isl:
            v, f = mo.compact(verts, faces[ix])
            vol, area = mo.volume_area(v, f)
            if vol < 0:
                f = f[:, ::-1].copy()
                vol = -vol
            ok, bad, mis = mo.watertight(f)
            R, onote = mo.orient(v, f, job['orient'])
            v2 = v @ R.T
            R2, t = mo.yaw_and_place(v2)
            v3 = v2 @ R2.T + t
            sig = mo.signature(v3, f)
            key = (job['base'], job['group'], job['material'], job['colour'])
            lst = variants.setdefault(key, [])
            inst = job['station'] or job['part']
            for var in lst:
                if mo.same_shape(var['sig'], sig):
                    var['inst'].append(inst)
                    break
            else:
                aligned = _axis_aligned(R2 @ R)
                lst.append(dict(sig=sig, v=v3, f=f, inst=[inst], ok=ok, bad=bad, mis=mis, vol=vol, area=area,
                                onote=onote, job=job, aligned=aligned, n_islands=len(isl), grown=r.get('grown_mm', 0.0),
                                raw_bbox=np.ptp(v, axis=0)))
    return variants


def _axis_aligned(R):
    return bool(np.all(np.isclose(np.abs(R), 0, atol=1e-6) | np.isclose(np.abs(R), 1, atol=1e-6)))


def write_prints(variants, out, rep, rows_csv, P):
    """Name, count, write STLs and PRINT-LIST rows. Returns contact-sheet items."""
    pcsv = parts_csv()
    sheet_items, plist = [], []
    for key in variants:
        base, group, mat, colour = key
        lst = variants[key]
        is_jig = base.startswith('JIG-')
        spec = jigs.JIG_PRINT[base] if is_jig else cfg.PRINT[base]
        spares = spec.get('spares', 0) if not is_jig else spec.get('qty_extra', 0)
        if isinstance(spares, dict):
            spares = spares.get(colour, 0)
        nv = len(lst)
        for i, var in enumerate(lst):
            extra = spares // nv + (1 if i < spares % nv else 0)
            n_fl = len(var['inst'])
            qty = n_fl + extra
            name = base + ('-' + group if group else '') + ('-' + 'ABCDEFGH'[i] if nv > 1 else '')
            mtok = mat + ('-' + colour if colour else '')
            fname = '%s_%s_x%d.stl' % (name, mtok, qty)
            sub = 'jigs' if is_jig else 'print'
            path = os.path.join(out, sub, fname)
            tris = var['v'][var['f']]
            mo.write_stl(path, tris, '%s %s qty %d (%s)' % (name, mtok, qty, ', '.join(var['inst'])))
            size = os.path.getsize(path)
            dims = np.ptp(var['v'], axis=0)
            layer = float(spec.get('layer') or cfg.DEFAULT_LAYER)
            perims = first_int(spec.get('perimeters'), 2)
            infill = infill_frac(spec.get('infill'), 0.2)
            t_min, g = estimate(var['vol'], var['area'], dims[2], mat, layer, perims, infill)
            oh = mo.overhang_area(var['v'], var['f'])
            sup = spec.get('supports') or ('none' if oh < 25 else 'check: %.0f mm2 overhang > 50 deg (auto)' % oh)
            cad_m = ''
            row = pcsv.get(base)
            if row and not group and not is_jig and base not in ('POD-008',) and var['n_islands'] == 1:
                cad_m = row.get('mass_g', '')
            var.update(file=fname, path=path, qty=qty, name=name, t_min=t_min, mass=g)
            plist.append({
                'file': sub + '/' + fname, 'part': name, 'instances': ' '.join(var['inst']),
                'material': mat, 'colour': colour, 'qty_flight': n_fl, 'qty_spare': extra, 'qty_total': qty,
                'orientation': var['onote'],
                'layer_mm': spec.get('layer') or cfg.DEFAULT_LAYER + ' (default)',
                'perimeters': spec.get('perimeters') or '2 (default)',
                'infill': spec.get('infill') or '20 % (default)',
                'supports': sup, 'size_on_bed_mm': '%.1f x %.1f x %.1f' % tuple(dims),
                'est_time_each_min': '%.0f' % t_min, 'est_mass_each_g': '%.1f' % g, 'cad_mass_each_g': cad_m,
                'status': spec.get('hold', '') or ('JIG (shop aid)' if is_jig else 'print'),
                'machine': cfg.MACHINE[mat], 'source': spec.get('src', 'manufacturing/jigs.py'),
                'notes': (spec.get('note', '') + ('; CAD bodies touching along an edge fused with a %g mm overlap'
                                                   % var['grown'] if var['grown'] else '')).strip('; ')})
            rep.check(var['ok'], 'STL watertight: %s' % fname,
                      'open/non-manifold edges %d, mis-oriented %d' % (var['bad'], var['mis']))
            rep.check(size < 5e6, 'STL size < 5 MB: %s' % fname, '%.2f MB' % (size / 1e6))
            # sorted bounding box vs the CAD bodies when the turn was a pure axis swap
            if var['aligned'] and var['n_islands'] == 1:
                cad = sorted(_cad_bbox(var['job']))
                got = sorted(dims)
                rep.check(all(abs(a - b) < 0.3 for a, b in zip(cad, got)), 'bbox = CAD bodies: %s' % fname,
                          'STL %s vs CAD %s mm' % (_d3(got), _d3(cad)))
            cv = var['job']['cad_volume_mm3']
            if var['n_islands'] == 1:
                up = cv * 1.01 + 1 + var['area'] * var['grown'] * 1.2
                rep.check(var['vol'] <= up and var['vol'] >= 0.25 * cv, 'volume sane: %s' % fname,
                          'mesh %.0f mm3, sum of CAD bodies %.0f mm3 (overlaps make the sum larger)' % (var['vol'], cv))
            title = '%s  x%d  %s%s' % (name, qty, mat, (' ' + colour) if colour else '')
            sheet_items.append((path, title, mat, colour))
    with open(os.path.join(out, 'PRINT-LIST.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(plist[0].keys()))
        w.writeheader()
        w.writerows(plist)
    rows_csv.extend(plist)
    return sheet_items


def _cad_bbox(job):
    M = job['matrix']
    pts = []
    for b in job['bodies']:
        s = cs.shape_from_json(b)
        for p in (s.hull_points(96) if s.kind == 'revolve' else s.points()):
            pts.append([sum(M[i][j] * p[j] for j in range(3)) + M[i][3] for i in range(3)])
    a = np.array(pts) * 1000
    return list(np.ptp(a, axis=0))


def _d3(d):
    return '%.1f x %.1f x %.1f' % tuple(d)


# ----------------------------------------------------------------------------- sheet parts
def loops_sig(loops):
    def norm(ls, mx):
        q = [[((-x if mx else x), y) for x, y in l] for l in ls]
        x0, y0, _a, _b = dxf.bbox(q)
        return sorted(tuple(sorted((round(x - x0, 1), round(y - y0, 1)) for x, y in l)) for l in q)
    return norm(loops, False), norm(loops, True)


def reg_holes(loops, margin=20.0, step=4.0):
    """Two optional pin-registration points inside the outline, >= margin from every edge, farthest apart."""
    x0, y0, x1, y1 = dxf.bbox(loops)
    cand = []
    y = y0 + margin
    while y < y1 - margin:
        x = x0 + margin
        while x < x1 - margin:
            p = (x, y)
            if dxf.point_in(p, loops[0]) and not any(dxf.point_in(p, h) for h in loops[1:]) \
                    and dxf.edge_dist(p, loops) >= margin:
                cand.append(p)
            x += step
        y += step
    if len(cand) < 2:
        return []
    best = max(((a, b) for i, a in enumerate(cand) for b in cand[i + 1:i + 400]), key=lambda ab: math.dist(*ab))
    return list(best)


def collect_sheet_items(ctx, P, rep, jig_flat):
    """-> {sheet: [item]}; item = dict(part, piece, loops (mm), marks, qty, flight, spare, source, note, holes)."""
    items = {k: [] for k in cfg.SHEETS}
    # foam board: half-fin boards
    layers = int(k9.val(P, 'fins.layers'))
    bt = k9.board_t(P)
    fins = []
    for pid, comp in ctx.components.items():
        base, st = cs.split_id(pid)
        if base != 'FIN-001':
            continue
        lam = [s for s in comp.shapes if s.kind == 'prism' and 'laminate' in (s.name or '')]
        if not lam:
            rep.issues.append('%s: no laminate body found (name "laminate")' % pid)
            continue
        loops, how = cs.flat_outline(comp, lam[0], abs(lam[0].depth))
        sig = loops_sig(loops)
        for f in fins:
            if sig[0] in (f['sig'][0], f['sig'][1]):
                f['inst'].append(st)
                break
        else:
            fins.append(dict(sig=sig, loops=loops, inst=[st], z_up=lam[0].offset))
    sp = cfg.SHEET_SPARES.get('FIN-001', 0)
    for i, f in enumerate(fins):
        extra = (sp // len(fins) + (1 if i < sp % len(fins) else 0)) * layers
        regs = reg_holes(f['loops'])
        items['foamboard'].append(dict(part='FIN-001', piece='half-fin board %s (%s)' % ('ABCD'[i], '/'.join(f['inst'])),
                                       loops=f['loops'], marks=[dxf.circle(x, y, 1.5, 16) for x, y in regs],
                                       flight=len(f['inst']) * layers, spare=extra, source='fins/fusion/fins.py '
                                       'FIN-001 laminate body', note='%d boards per laminate (fins.layers), %.1f mm each; '
                                       'MARK circles = optional pin-registration holes for laminating on pins (D3 to '
                                       'agree)' % (layers, bt)))
    # foam board: pod shell and hatch
    for pid in ('POD-001', 'POD-003'):
        comp = ctx.components.get(pid)
        if comp is None:
            continue
        for s in comp.shapes:
            if not (s.name or '').startswith('fb '):
                continue
            loops, how = cs.flat_outline(comp, s, bt)
            if loops is None:
                rep.notes_sheet.append('%s "%s": %s -> shaped by hand (pod/BUILD.md step 3)' % (pid, s.name, how))
                continue
            items['foamboard'].append(dict(part=pid, piece=s.name[3:], loops=loops, marks=[], flight=1, spare=0,
                                           source='pod/fusion/pod.py body "%s"' % s.name, note=''))
    # Coroplast box panels
    for pid in ('TRN-001', 'TRN-005'):
        comp = ctx.components.get(pid)
        if comp is None:
            continue
        sht = cfg.SHEETS['coroplast']
        for s in comp.shapes:
            if re.search(cfg.SHEET_EXCLUDE.get(pid, r'^$'), s.name or ''):
                continue
            loops, how = cs.flat_outline(comp, s, sht['t_mm'] / 1000.0)
            if loops is None:
                rep.notes_sheet.append('%s "%s": %s' % (pid, s.name, how))
                continue
            items['coroplast'].append(dict(part=pid, piece=s.name, loops=loops, marks=[], flight=1, spare=0,
                                           source='transport/fusion/transport.py body "%s"' % s.name,
                                           note='panel: join with taped / hot-melted corner angles (MF-16)'))
    # ply: jig board + bar, and the BUILD.md-only pieces
    for name, loops, marks, texts in jig_flat:
        items['ply3'].append(dict(part=name.split()[0], piece=name, loops=loops, marks=marks, flight=1, spare=0,
                                  source='manufacturing/jigs.py (from fins.y_m, fins.tube.*)', note='', texts=texts))
    for part, piece, sheet, w, h, qty, holes, src in cfg.EXTRA_SHEET_PARTS:
        loops = [[(0, 0), (w, 0), (w, h), (0, h)]] + [dxf.circle(x, y, d / 2, 24) for x, y, d in holes]
        items[sheet].append(dict(part=part, piece=piece, loops=loops, marks=[], flight=qty, spare=0, source=src,
                                 note='NOT IN CAD: drawn from the BUILD.md numbers'))
    return items, fins


def write_sheets(items, out, rep, cut_rows):
    files = []
    for sheet, lst in items.items():
        if not lst:
            continue
        S = cfg.SHEETS[sheet]
        W, H = S['size_mm']
        expanded = []
        for k, it in enumerate(lst):
            x0, y0, x1, y1 = dxf.bbox(it['loops'])
            for q in range(it['flight'] + it['spare']):
                expanded.append(('%03d-%02d' % (k, q), x1 - x0, y1 - y0))
        placed, misfit, nsheets = dxf.nest(expanded, W, H, S['margin_mm'], S['gap_mm'])
        for key in misfit:
            it = lst[int(key[:3])]
            rep.issues.append('%s %s does not fit a %g x %g mm %s sheet: cut by hand' % (it['part'], it['piece'], W, H,
                                                                                          sheet))
        per_sheet = {}
        for si, key, x, y, rot in placed:
            per_sheet.setdefault(si, []).append((key, x, y, rot))
        for si in range(nsheets):
            d = dxf.Drawing()
            d.poly([(0, 0), (W, 0), (W, H), (0, H)], 'NOTES')
            d.text(S['margin_mm'], H - S['margin_mm'] + 2, 6, 'K09-L %s  sheet %d/%d  %g x %g mm  t %g mm  kerf %.2f mm '
                   '(outlines NOMINAL, no kerf offset)  CUT red / MARK blue / NOTES do not cut' % (
                       S['name'], si + 1, nsheets, W, H, S['t_mm'], S['kerf_mm']))
            for key, x, y, rot in sorted(per_sheet.get(si, [])):
                it = lst[int(key[:3])]
                loops = dxf.transform(it['loops'] + it['marks'], rot90=rot, dx=x, dy=y)
                nl = len(it['loops'])
                for l in loops[:nl]:
                    d.poly(l, 'CUT')
                for l in loops[nl:]:
                    d.poly(l, 'MARK')
                if it.get('marks') and it['part'] == 'JIG-01':
                    pass
                bx0, by0, bx1, by1 = dxf.bbox(loops[:1])
                d.text(bx0 + 3, by0 + 3, 4, '%s %s' % (it['part'], it['piece'][:40]))
            fname = '%s_sheet%dof%d.dxf' % (sheet, si + 1, nsheets)
            path = os.path.join(out, 'laser', fname)
            d.write(path)
            files.append((path, '%s sheet %d/%d' % (sheet, si + 1, nsheets), W, H))
            # CUT-LIST rows
            counts = {}
            for key, x, y, rot in per_sheet.get(si, []):
                counts.setdefault(int(key[:3]), 0)
                counts[int(key[:3])] += 1
            for k in sorted(counts):
                it = lst[k]
                x0, y0, x1, y1 = dxf.bbox(it['loops'])
                w, h = x1 - x0, y1 - y0
                fits = [('%gx%g in' % (bw / 25.4, bh / 25.4)) for bw, bh in cfg.LASER_BEDS_MM
                        if (max(w, h) <= bw and min(w, h) <= bh)]
                cut_rows.append({
                    'file': 'laser/' + fname, 'part': it['part'], 'piece': it['piece'], 'qty_on_sheet': counts[k],
                    'qty_flight_total': it['flight'], 'qty_spare_total': it['spare'], 'material': S['name'],
                    'thickness_mm': S['t_mm'], 'size_mm': '%.1f x %.1f' % (w, h),
                    'area_cm2': '%.0f' % (sum(dxf.area(l) for l in it['loops'][:1]) / 100 -
                                          sum(dxf.area(l) for l in it['loops'][1:]) / 100),
                    'holes_cutouts': len(it['loops']) - 1, 'machine': cfg.MACHINE[S['machine']],
                    'kerf_mm': S['kerf_mm'], 'fits_laser_bed': ' / '.join(fits) or 'NONE: knife-cut',
                    'stock': S['bom'], 'source': it['source'], 'notes': (it['note'] + ' ' + S['note']).strip()})
    return files


def check_sheets(items, fins, P, rep, files):
    # every CUT polyline in every written DXF is closed; pieces read back with their source sizes
    for path, title, W, H in files:
        polys, _t = dxf.read(path)
        cut = [p for p in polys if p[0] == 'CUT']
        rep.check(all(c for _l, c, _p in cut) and len(cut) > 0, 'DXF closed CUT polylines: %s' % os.path.basename(path),
                  '%d closed outlines' % len(cut))
        xs = [q[0] for _l, _c, p in cut for q in p]
        ys = [q[1] for _l, _c, p in cut for q in p]
        rep.check(min(xs) >= -0.01 and min(ys) >= -0.01 and max(xs) <= W + 0.01 and max(ys) <= H + 0.01,
                  'DXF pieces inside the sheet: %s' % os.path.basename(path), '%g x %g mm' % (W, H))
    # half-fin boards against params
    ht = k9.val(P, 'fins.half_height_m', 'm') * 1000
    te = k9.val(P, 'fins.te_x_m', 'm') * 1000
    for f in fins:
        x0, y0, x1, y1 = dxf.bbox(f['loops'])
        zt = max(abs(y0), abs(y1))
        rep.check(abs(zt - ht) < 0.05 and abs(x1 - te) < 0.05, 'FIN-001 board %s: tip |z| = fins.half_height_m, TE x = '
                  'fins.te_x_m' % '/'.join(f['inst']), 'tip %.2f (params %.2f), TE %.2f (params %.2f) mm' % (zt, ht, x1, te))
    # pod floor width = pod width - 2 boards
    pw = k9.val(P, 'pod.size_m', 'm')[1] * 1000
    bt = k9.board_t(P) * 1000
    for it in items['foamboard']:
        if it['part'] == 'POD-001' and it['piece'] == 'floor':
            x0, y0, x1, y1 = dxf.bbox(it['loops'])
            rep.check(abs((y1 - y0) - (pw - 2 * bt)) < 0.05, 'POD-001 floor width = pod.size_m[1] - 2 board_t',
                      '%.1f vs %.1f mm' % (y1 - y0, pw - 2 * bt))
    # Coroplast floor = box external L x W
    T = cs.local_params('transport')['trn']['box']['external_m']['value']
    for it in items['coroplast']:
        if it['piece'] == 'floor':
            x0, y0, x1, y1 = dxf.bbox(it['loops'])
            rep.check(abs(max(x1 - x0, y1 - y0) - T[0] * 1000) < 0.05 and abs(min(x1 - x0, y1 - y0) - T[1] * 1000) < 0.05,
                      'TRN-001 floor = trn.box.external_m L x W', '%.1f x %.1f mm' % (max(x1 - x0, y1 - y0),
                                                                                     min(x1 - x0, y1 - y0)))
    for it in items['ply3']:
        if it['piece'] == 'JIG-01 base board':
            hs = [l for l in it['loops'][1:]]
            cx = sorted({round(sum(p[0] for p in h) / len(h), 1) for h in hs})
            span = (cx[-1] + cx[-2]) / 2 - (cx[0] + cx[1]) / 2 if len(cx) >= 4 else 0
            want = 2 * k9.val(P, 'fins.y_m', 'm') * 1000
            rep.check(abs(span - want) < 0.05, 'JIG-01 board post spacing = 2 x fins.y_m', '%.2f vs %.2f mm' % (span, want))


# ----------------------------------------------------------------------------- hot-wire templates + 1:1 PDFs
def write_hotwire(P, out, rep, cut_rows):
    G = hotwire.template_geometry(P)
    srcs = []
    for end in G['ends']:
        d, pins, zb = hotwire.template_drawing(G, end)
        path = os.path.join(out, 'hotwire', 'WNG-001_template_%s.dxf' % end['name'])
        d.write(path)
        polys, _t = dxf.read(path)
        cut = [p for l, c, p in polys if l == 'CUT']
        outline = max(cut, key=lambda p: dxf.area(p))
        x0, y0, x1, y1 = dxf.bbox([outline])
        chord, off = end['chord_mm'], G['offset_mm']
        rep.check(abs((x1 - x0) - (chord + 2 * off)) < 0.1, 'template %s chord = wing.chord_m + 2 x kerf offset'
                  % end['name'], '%.2f vs %.2f mm' % (x1 - x0, chord + 2 * off))
        coords = k9.section(P)[0]
        tmax = max(k9.thickness_at(coords, chord, i / 400) for i in range(1, 400))
        rep.check(abs(tmax - G['t_c'] * chord) < 0.3, 'template %s section max thickness = wing.t_c x chord'
                  % end['name'], '%.2f vs %.2f mm' % (tmax, G['t_c'] * chord))
        zr = [y for _x, y in coords]
        span_z = (max(zr) - min(zr)) * chord
        rep.check(abs((y1 - y0) - (span_z + 2 * off)) < 0.3, 'template %s depth = section z-extent (.dat) + 2 x offset'
                  % end['name'], '%.2f vs %.2f mm' % (y1 - y0, span_z + 2 * off))
        te = [p for p in end['true'] if abs(p[0] - max(q[0] for q in end['true'])) < 1e-6]
        te_t = max(p[1] for p in te) - min(p[1] for p in te)
        rep.check(te_t >= G['te_min_mm'] - 0.01, 'template %s TE >= k09kit.TE_MIN_M' % end['name'],
                  'TE %.2f mm' % te_t)
        sx, sz = G['spar']
        rep.check(abs(sx - k9.val(P, 'wing.spar.x_m', 'm') * 1000) < 1e-6 and
                  abs(sz - k9.val(P, 'wing.spar.z_m', 'm') * 1000) < 1e-6,
                  'template %s spar mark at wing.spar.x_m / z_m' % end['name'], 'x %.1f z %.1f mm, bore D %.1f' % (
                      sx, sz, 2 * G['bore_r']))
        cut_rows.append({'file': 'hotwire/' + os.path.basename(path), 'part': 'WNG-001', 'piece': 'hot-wire template '
                         + end['name'], 'qty_on_sheet': 1, 'qty_flight_total': 1, 'qty_spare_total': 0,
                         'material': cfg.SHEETS['hardboard2']['name'], 'thickness_mm': 2.0,
                         'size_mm': '%.1f x %.1f' % (x1 - x0, y1 - y0), 'area_cm2': '%.0f' % (dxf.area(outline) / 100),
                         'holes_cutouts': len(cut) - 1, 'machine': cfg.MACHINE['laser_small'],
                         'kerf_mm': cfg.SHEETS['hardboard2']['kerf_mm'], 'fits_laser_bed': '32x18 in / 48x25 in',
                         'stock': cfg.SHEETS['hardboard2']['bom'], 'source': 'k09kit.section + section_loop (%s)'
                         % G['src'], 'notes': 'riding edge = CUT outline (true + %.2f mm); sand the riding edge smooth, '
                         'no notches; TE is fragile: back it with tape' % off})

        def draw(ax, end=end, path=path, zb=zb):
            for layer, closed, pts in dxf.read(path)[0]:
                xs = [q[0] for q in pts] + ([pts[0][0]] if closed else [])
                ys = [q[1] for q in pts] + ([pts[0][1]] if closed else [])
                ax.plot(xs, ys, color={'CUT': 'k', 'MARK': '#1f5fbf', 'NOTES': '0.6'}[layer],
                        lw={'CUT': 0.6, 'MARK': 0.3, 'NOTES': 0.3}[layer])
            for _l, s in dxf.read(path)[1][:1]:
                ax.text(5, zb - 8, s, fontsize=7)
            ax.text(5, zb - 14, 'black = CUT (template edge), blue = true section / chord / 10 %% stations / spar bore / '
                    'hinge, grey = blank end %g x %g mm' % cfg.HOTWIRE['blank_mm'][1:], fontsize=6)
        B = cfg.HOTWIRE['blank_mm']
        lm = cfg.HOTWIRE['le_margin_mm']
        srcs.append(('WNG-001 template %s' % end['name'].upper(), draw, (-lm, zb - 16, B[1] - lm, zb + B[2])))
    n = hotwire.tiled_pdf(os.path.join(out, 'hotwire', 'WNG-001_templates_1to1_letter.pdf'), srcs,
                          'K09-L WNG-001 hot-wire templates 1:1')
    return G, n


def foam_pdf(items, out):
    srcs = []
    seen = set()
    for it in items['foamboard']:
        if it['piece'] in seen:
            continue
        seen.add(it['piece'])
        loops = dxf.transform(it['loops'] + it['marks'], dx=0, dy=0)
        nl = len(it['loops'])
        x0, y0, x1, y1 = dxf.bbox(loops)

        def draw(ax, loops=loops, nl=nl, it=it, y1=y1):
            hotwire.draw_loops(ax, [(loops[:nl], {'c': 'k', 'lw': 0.6}), (loops[nl:], {'c': '#1f5fbf', 'lw': 0.4})])
            ax.text(0, y1 + 3, '%s %s - cut on the black line (nominal size)' % (it['part'], it['piece']), fontsize=7)
        srcs.append(('%s %s' % (it['part'], it['piece']), draw, (x0, y0, x1, y1 + 6)))
    return hotwire.tiled_pdf(os.path.join(out, 'laser', 'foamboard_1to1_letter.pdf'), srcs,
                             'K09-L foam-board parts 1:1 (knife templates)')


# ----------------------------------------------------------------------------- param spot checks on prints
def check_print_params(variants, P, rep):
    W = cs.local_params('wing')['plugs']
    F = cs.local_params('fins')['fin_detail']['esc_pad']
    pod = cs.local_params('pod')

    def var_of(base, group=''):
        for (b, g, _m, _c), lst in variants.items():
            if b == base and g == group:
                return lst
        return []
    for base, L in (('WNG-004', W['block_len_m']['value']), ('WNG-005', W['anchor_len_m']['value'])):
        for var in var_of(base):
            d = sorted(np.ptp(var['v'], axis=0))
            want = sorted([W['od_m']['value'] * 1000] * 2 + [L * 1000])
            rep.check(all(abs(a - b) < 0.15 for a, b in zip(d, want)), '%s = wing plugs.od_m x length' % base,
                      'STL %s vs params %s mm' % (_d3(d), _d3(want)))
    for var in var_of('FIN-007'):
        d = sorted(np.ptp(var['v'], axis=0))
        want = sorted([F['len_m']['value'] * 1000, F['h_m']['value'] * 1000, F['t_m']['value'] * 1000])
        rep.check(all(abs(a - b) < 0.05 for a, b in zip(d, want)), 'FIN-007 ESC pad = fin_detail.esc_pad len x h x t',
                  'STL %s vs params %s mm' % (_d3(d), _d3(want)))
    for t in pod['spacer_set_m']['value']:
        lst = var_of('POD-008', '%gmm' % (t * 1000))
        ok = bool(lst) and abs(min(np.ptp(lst[0]['v'], axis=0)) - t * 1000) < 0.02
        rep.check(ok, 'POD-008 spacer %g mm = pod spacer_set_m' % (t * 1000),
                  '%.2f mm thick' % min(np.ptp(lst[0]['v'], axis=0)) if lst else 'missing')
    for var in var_of('JIG-01'):
        h = np.ptp(var['v'], axis=0)[2]
        rep.check(abs(h - (jigs.POST['flange_t'] + jigs.POST['ring_h']) * 1000) < 0.05, 'JIG-01 post height',
                  '%.1f mm' % h)
    n3 = sum(len(v['inst']) for v in var_of('FIN-003'))
    rep.check(n3 == int(k9.val(P, 'propulsion.n_motors')), 'FIN-003 mounts = propulsion.n_motors', '%d' % n3)


# ----------------------------------------------------------------------------- docs
def write_checks(rep, out, meta):
    lines = ['# Shop-file checks', '', 'Generated by `make_shop_files.py` (%s). PASS/FAIL per check; NOTE = information.' %
             meta, '']
    n_fail = sum(1 for c in rep.checks if c[0] == 'FAIL')
    lines += ['**%d checks, %d FAIL.**' % (sum(1 for c in rep.checks if c[0] != 'NOTE'), n_fail), '']
    lines += ['| Result | Check | Detail |', '|---|---|---|']
    lines += ['| %s | %s | %s |' % c for c in rep.checks]
    if rep.issues:
        lines += ['', '## Issues (not exported or needs a decision)', ''] + ['- ' + i for i in rep.issues]
    with open(os.path.join(out, 'CHECKS.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    return n_fail


def write_shop_pack(out, prints, cuts, G, n_pdf, n_fpdf, rep, angles):
    stl_p = [r for r in prints if r['file'].startswith('print/')]
    stl_j = [r for r in prints if r['file'].startswith('jigs/')]

    def tot(rows, k):
        return sum(int(r[k]) for r in rows)
    hrs = sum(float(r['est_time_each_min']) * int(r['qty_total']) for r in stl_p) / 60
    gsum = {}
    for r in stl_p:
        gsum[r['material']] = gsum.get(r['material'], 0) + float(r['est_mass_each_g']) * int(r['qty_total'])
    L = []
    a = L.append
    a('# K09-L shop pack')
    a('')
    a('Generated by `python -B redesign/manufacturing/make_shop_files.py` from the CAD builders (stub backend) and '
      'Blender %s. Re-run after any CAD change; every file below is rebuilt. Checks: [`CHECKS.md`](CHECKS.md). '
      'Fixes MF-01 (review/MANUFACTURING.md).' % '4.2')
    a('')
    a('## What is here')
    a('')
    a('| File(s) | What | Make on (Jacobs Hall) |')
    a('|---|---|---|')
    a('| `print/*.stl` (%d files, %d prints) | Every printed flight part, one STL per distinct geometry, mm, already in '
      'print orientation (flat face down; see the `orientation` column). Name = `<part>_<material>_x<qty incl. '
      'spares>.stl`. Mirror parts are separate files (A/B) | PETG/TPU: Prusa (open access). ASA: enclosed printer, not '
      'on the open-access list (MF-15) |' % (len(stl_p), tot(stl_p, 'qty_total')))
    a('| `PRINT-LIST.csv` | Per file: part, material, colour, qty (flight + spare), orientation, layer, perimeters, '
      'infill, supports, est. time and mass each, CAD mass, source of each setting, hold status | - |')
    a('| `jigs/*.stl` (%d files) | JIG-01 tube posts, JIG-02 fin-alignment collar, JIG-03 cant gauge A/B | Prusa, PETG |'
      % len(stl_j))
    a('| `laser/foamboard_sheet*.dxf` | Half-fin boards (2 per laminate, incl. %d spare laminates) and the pod shell / '
      'hatch boards, nested on 20 x 30 in sheets | Universal laser **48 x 25 in** (the only bed a 20 x 30 sheet fits); '
      'or print `foamboard_1to1_letter.pdf` and knife-cut |' % cfg.SHEET_SPARES.get('FIN-001', 0))
    a('| `laser/coroplast_sheet*.dxf` | Box floor, walls, lid and lid lips as separate panels on 48 x 96 in sheets '
      '(MF-16: the cross blank does not fit a sheet) | Knife and straightedge on the bench (panels exceed every laser bed) |')
    a('| `laser/ply3_sheet*.dxf` | JIG-01 base board and top bar, 3 handle backing strips, 2 landing-mat panels | '
      'Universal laser 48 x 25 in |')
    a('| `laser/foamboard_1to1_letter.pdf` (%d pages) | 1:1 knife templates of every foam-board piece | any printer at '
      '100 %% |' % n_fpdf)
    a('| `hotwire/WNG-001_template_root.dxf`, `..._tip.dxf` | S5010 c %.0f hot-wire templates, true size + %.2f mm kerf '
      'offset, TE %.1f mm; MARK layer: true section, chord line, 10 %% stations, spar bore D %.1f at x %.0f z %.1f, '
      'hinge x %.1f; pin holes on the chord line | Universal laser, 2 mm hardboard/ply |' % (
          G['chord_mm'], G['offset_mm'], G['te_min_mm'], 2 * G['bore_r'], G['spar'][0], G['spar'][1], G['hinge_x']))
    a('| `hotwire/WNG-001_templates_1to1_letter.pdf` (%d pages) | The same templates tiled 1:1 on letter paper with '
      'registration crosses and a 100 mm scale check, for gluing onto hardboard if the laser is not available | any '
      'printer at 100 %% |' % n_pdf)
    a('| `CUT-LIST.csv` | Every sheet piece: file, qty, size, material, kerf, which laser bed it fits, source | - |')
    a('| `contact-sheet.png`, `dxf-preview.png` | Picture of every print on its bed; every nest | - |')
    a('')
    a('Estimated printing: about **%.0f printer-hours** for all flight prints incl. spares (PRINT-LIST estimate: volume '
      'flow + layer changes, not a slicer), filament about %s.' % (
          hrs, ', '.join('%s %.0f g' % (k, v) for k, v in sorted(gsum.items()))))
    a('')
    a('## Order to make them')
    a('')
    a('Shop access ends 18 Dec (MF-04): items 1-6 before then.')
    a('')
    a('1. **Print the jigs and the fit-test set** (`jigs/`, then one each of FIN-004, FIN-003-A, GER-001, GER-002). '
      'Check the 22.3 mm bores on a real tube, the shoe/piston slide, the block on the spar. If a fit is off, change '
      'the CAD params (not the STL) and re-run.')
    a('2. **Laser-cut the hot-wire templates** (`hotwire/*.dxf`, 2 mm hardboard). Sand the riding edge. Pin both to '
      'the blank ends through the chord-line holes so both LEs sit on one line. Cut 2-3 practice cores; measure the '
      'kerf and update `shopconfig.HOTWIRE["kerf_mm"]` if it is not 1.0 mm (MF-05).')
    a('3. **Laser-cut the ply** (`laser/ply3_*`): JIG-01 board and top bar first (needed for the spar bond), then '
      'handle strips and mat panels.')
    a('4. **Print the long-lead flight parts**: FIN-004 blocks (+1 spare; MF-06), FIN-003 mounts in ASA (A and B, '
      '8 total), WNG-004/005 plugs, POD-002 tray set, POD-007 handle, PWR-006 frame, MEC-* horns/frames/covers, '
      'GER-001/002 (colours), GER-007 in TPU. **FIN-008 collars are ON HOLD** until the 18 Dec freeze (MF-13).')
    a('5. **Cut the foam-board** (`laser/foamboard_*`): laminate fin boards in pairs (3M 77, spray booth) - either cut '
      'single boards and laminate on pins through the MARK circles, or laminate first and knife-cut the pair from '
      'the 1:1 PDF. Then the pod board set.')
    a('6. **Wing core** (wing/BUILD.md 2-5) with the templates; then **spar + block bond in JIG-01**: bolt the two posts '
      'to the base board, stand dummy 22 mm tubes (tape-wrapped as release) in the posts, thread both blocks, slide '
      'the spar through, drop the top bar over both tube tops, check the tubes with a square in two directions, '
      'bond and cure 24 h without moving the jig.')
    a('7. **Half-fin root bonds with JIG-02**: slide a collar down each motor tube to the tube end, half-fin in the '
      'slot, root fillet, cure. Remove before the station collars go on.')
    a('8. **Motor mounts with JIG-03** (fins/BUILD.md step 18): hold the gauge (A on UR/LL, B on UL/LR) flat on the '
      'outboard fin face against the tube at |z| 60-85 mm (clear of the ESC pad), zero an angle cube on face D (the '
      'face looking forward, -x), move the cube to the bell top (prop off): 0.0 +/- 0.5 deg; turn the cube 90 deg '
      'and repeat. Face D is %.2f deg from square to the tube (the modelled cant, %s).' % (
          sum(angles.values()) / max(len(angles), 1), 'params propulsion.stations.cant_deg'))
    a('9. **Coroplast box** (`laser/coroplast_*`, knife): panels, corner angles, then transport/BUILD.md 5-16.')
    a('')
    a('## Jigs: how to use')
    a('')
    a('| Jig | Files | Use |')
    a('|---|---|---|')
    a('| JIG-01 tube-bore / block clocking (MF-06) | `jigs/JIG-01_*` (2 posts), `laser/ply3_*` (base board, top bar) | '
      'Board flat on the bench; posts bolted with 4 x M4 each into the engraved squares; the LE line on the board '
      'is parallel to the tube line. Bores in post and bar are tube OD + 0.3 / + 0.4 mm. The two supports 45 mm and '
      '~%s mm apart hold each tube within about 0.4 deg, so both blocks are clocked by the tubes, not by eye |'
      % 'cradle + core height')
    a('| JIG-02 fin-alignment collar (MF-08) | `jigs/JIG-02_*` (x4) | On the motor tube near its end; the half-fin '
      'laminate sits in the slot (laminate + 0.3 mm), so the fin plane passes through the tube axis and stays square '
      'to the wing while the root fillet cures |')
    a('| JIG-03 cant gauge (MF-07) | `jigs/JIG-03-A_*` (UR/LL), `JIG-03-B_*` (UL/LR) | Datum face D = the bell top of '
      'that station as modelled (7 deg tangential cant). Relieved over the 10 mm LE edge strip so it sits on the '
      'board face. Check after every prop strike or mount slip |')
    a('')
    a('## Not exported, or exported with a caveat')
    a('')
    for i in rep.issues:
        a('- ' + i)
    for n in rep.notes_sheet:
        a('- ' + n)
    a('- Hot-wired and hand-cut foam parts (wing core cuts, elevons, pod LE filler and crush block, cradle saddles, '
      'prop tray, cartridges) are not sheet or print parts: the templates and BUILD.md numbers cover them.')
    a('- DXF outlines are nominal (no kerf offset). Laser kerf is listed per sheet; the hot-wire templates DO include '
      'the wire kerf.')
    with open(os.path.join(out, 'SHOP-PACK.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


# ----------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', default=os.path.join(HERE, 'out'))
    ap.add_argument('--blender')
    ap.add_argument('--no-stl', action='store_true')
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out)
    t0 = time.time()
    for d in GENERATED:
        shutil.rmtree(os.path.join(out, d), ignore_errors=True)
    for d in GENERATED:
        os.makedirs(os.path.join(out, d), exist_ok=True)
    for f in ('PRINT-LIST.csv', 'CUT-LIST.csv', 'CHECKS.md', 'SHOP-PACK.md', 'contact-sheet.png', 'dxf-preview.png',
              'manifest.json'):
        if os.path.exists(os.path.join(out, f)):
            os.remove(os.path.join(out, f))
    rep = Report()
    rep.notes_sheet = []
    print('make_shop_files: building the CAD (stub backend)')
    ctx, results = cs.build(log=rep.issues.append)
    rep.check(all(r[2] for r in results), 'every CAD module builds', '%d modules' % len(results))
    P = cs.params()
    jobs = cs.print_jobs(ctx, rep.issues)
    jig_jobs, jig_flat, _g, angles = jigs.jobs(ctx, P, rep.issues)
    for k, v in cfg.NOT_IN_CAD.items():
        rep.issues.append('%s not exported: %s' % (k, v))
    prints, sheet_items = [], []
    if not a.no_stl:
        blender = find_blender(a.blender)
        if not blender:
            rep.issues.append('Blender not found: no STLs written (pass --blender or set BLENDER)')
        else:
            print('make_shop_files: meshing %d print jobs in Blender' % (len(jobs) + len(jig_jobs)))
            raw, brep = run_blender(blender, jobs + jig_jobs, os.path.join(out, '_work'), rep)
            for d in brep.get('_defects', []):
                rep.issues.append('CAD defect (repaired in the export only, tell the owner): ' + d)
            variants = process_meshes(jobs + jig_jobs, raw, brep, rep)
            sheet_items = write_prints(variants, out, rep, prints, P)
            check_print_params(variants, P, rep)
            contact_sheet.render(sheet_items, os.path.join(out, 'contact-sheet.png'))
    print('make_shop_files: sheets, templates, jigs')
    cut_rows = []
    items, fins = collect_sheet_items(ctx, P, rep, jig_flat)
    files = write_sheets(items, out, rep, cut_rows)
    check_sheets(items, fins, P, rep, files)
    G, n_pdf = write_hotwire(P, out, rep, cut_rows)
    n_fpdf = foam_pdf(items, out)
    files += [(os.path.join(out, 'hotwire', 'WNG-001_template_%s.dxf' % e['name']), 'template ' + e['name'],
               cfg.SHEETS['hardboard2']['size_mm'][0], cfg.SHEETS['hardboard2']['size_mm'][1]) for e in G['ends']]
    contact_sheet.dxf_preview(files, os.path.join(out, 'dxf-preview.png'))
    with open(os.path.join(out, 'CUT-LIST.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(cut_rows[0].keys()))
        w.writeheader()
        w.writerows(cut_rows)
    shutil.rmtree(os.path.join(out, '_work', 'raw'), ignore_errors=True)
    write_shop_pack(out, prints, cut_rows, G, n_pdf, n_fpdf, rep, angles)
    n_fail = write_checks(rep, out, 'params %s' % P.get('meta', {}).get('version', {}).get('value', '')
                          if isinstance(P.get('meta', {}).get('version'), dict) else 'params.json')
    man = {}
    for root, _d, fs in os.walk(out):
        for fn in sorted(fs):
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, out).replace('\\', '/')
            if rel.startswith('_work') or rel == 'manifest.json':
                continue
            man[rel] = {'bytes': os.path.getsize(p), 'sha256': sha(p)}
    with open(os.path.join(out, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(sorted(man.items())), f, indent=1)
    kinds = {}
    for rel in man:
        kinds[rel.rsplit('.', 1)[-1]] = kinds.get(rel.rsplit('.', 1)[-1], 0) + 1
    print('make_shop_files: %s in %.0f s -> %s' % (', '.join('%d %s' % (v, k) for k, v in sorted(kinds.items())),
                                                    time.time() - t0, out))
    print('  checks: %d, FAIL %d; issues %d (see CHECKS.md)' % (
        sum(1 for c in rep.checks if c[0] != 'NOTE'), n_fail, len(rep.issues)))
    for i in rep.issues:
        print('  issue: ' + i)
    return 1 if n_fail else 0


if __name__ == '__main__':
    sys.exit(main())
