"""compose_drawings.py - stage 3 of make_drawings_a.py: one sheet (17 x 11 in, third-angle projection) per drawing job.

Views (from render_drawings_blender.py) are placed at ONE common scale on the sheet: top view above the front view, right
side view to its right, isometric (not to scale) top right. Overall dimensions are drawn on the front and side views from
the meshed part's bounding box. The feature table lists every CAD body and every shop cut of the part (identical features
merged as 'n x') with its size and position in the part's design frame, in mm, as the CAD records them; long tables run
on to continuation sheets. Writes out/<id>.pdf, out/DRAWINGS-A.pdf (all sheets) and out/DRAWINGS-A.md (index).
"""
import datetime
import json
import os
import shutil
import subprocess
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
WORK = os.path.join(OUT, '_work')
import make_drawings_a as mk                    # noqa: E402

INK, MUTED, RULE = '#111111', '#555555', '#999999'
GH = 'https://github.com/davinciucberkeley-collab/DBF-Combined/blob/redesign/v1/redesign/qp/A/drawings/out/'   # GitHub file view: renders PDF / STL, has a download button
W_IN, H_IN = 17.0, 11.0
PROCESS = {
    'print': 'Printed PETG. Print files (STL, mm, design frame; choose the bed face in the slicer): %s. Slicer settings: not set in the CAD (-).',
    'tube': 'Cut from carbon stock (BOM: see parts_links_a.py), sand the ends square; drill the holes in the feature table with a drill guide (Jacobs). Bonded with epoxy.',
    'foam': 'Cut from foam (XPS 25 kg/m3 or as the material says): hot wire or knife; cuts and grooves in the feature table are routed or knifed.',
    'other': 'See the material and the feature table.',
}


def pieces(stl):
    """Number of separate solids in an STL (1 = one printable piece; more = a body floating free of the part)."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE)))), 'manufacturing'))
    import mesh_ops
    v, f = mesh_ops.weld(mesh_ops.read_stl(stl))
    return len(mesh_ops.islands(f, len(v)))


def git_rev():
    try:
        return subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=HERE, capture_output=True, text=True).stdout.strip() or '-'
    except Exception:
        return '-'


def proj(p, v):
    c, r, u = v['centre'], v['right'], v['up']
    d = [p[i] - c[i] for i in range(3)]
    return sum(d[i] * r[i] for i in range(3)), sum(d[i] * u[i] for i in range(3))


def view_box(meta, name):
    lo, hi = meta['lo'], meta['hi']
    pts = [proj((x, y, z), meta['views'][name]) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    return min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)


def show(ax, meta, name):
    v = meta['views'][name]
    img = plt.imread(os.path.join(WORK, '%s_%s.png' % (meta['id'], name)))
    h = v['span'] / 2
    ax.imshow(img, extent=(-h, h, -h, h), interpolation='lanczos')
    ax.set_axis_off()


def dim(ax, a, b, off, horiz, text):
    """Linear dimension between a and b (data coords) offset 'off' from the part edge."""
    kw = dict(arrowprops=dict(arrowstyle='<|-|>', lw=0.7, color=INK, shrinkA=0, shrinkB=0, mutation_scale=7))
    if horiz:
        y = off
        ax.annotate('', (a, y), (b, y), **kw)
        ax.text((a + b) / 2, y, text, ha='center', va='bottom', fontsize=8, color=INK, backgroundcolor='white')
    else:
        x = off
        ax.annotate('', (x, a), (x, b), **kw)
        ax.text(x, (a + b) / 2, text, ha='right', va='center', fontsize=8, color=INK, rotation=90, backgroundcolor='white')


def place_views(fig, meta, box, job):
    """FRONT / TOP / RIGHT SIDE at ONE scale inside box (x0, y0, w, h, inches), third-angle; the views are oriented by the part's own
    proportions (render stage: long axis across the sheet). Each axes includes its dimension margin, so mm map to inches exactly.
    The largest free region takes the isometric view, or for a carbon tube / rod the cut-and-drill layout. Returns the scale (in/mm)."""
    x0, y0, w, h = box
    vb = {n: view_box(meta, n) for n in ('front', 'top', 'side')}
    W = {n: max(b[1] - b[0], 0.5) for n, b in vb.items()}
    H = {n: max(b[3] - b[2], 0.5) for n, b in vb.items()}
    pad = 0.8
    k = min((w - 3 * pad) / (W['front'] + W['side']), (h - 3.4 * pad) / (H['top'] + H['front']))
    k = min(k, 4.0 / 25.4 * 4)                                 # cap the enlargement at 4:1
    org = {'front': (x0 + pad, y0 + pad), 'side': (x0 + 2 * pad + W['front'] * k, y0 + pad), 'top': (x0 + pad, y0 + 2.2 * pad + H['front'] * k)}
    pm = pad / k
    axes = {}
    for n, (cx, cy) in org.items():
        a0, a1, b0, b1 = vb[n]
        ax = fig.add_axes([(cx - pad) / W_IN, (cy - pad) / H_IN, (W[n] * k + 1.1 * pad) / W_IN, (H[n] * k + 1.1 * pad) / H_IN])
        show(ax, meta, n)
        ax.set_xlim(a0 - pm, a0 + W[n] + 0.1 * pm)
        ax.set_ylim(b0 - pm, b0 + H[n] + 0.1 * pm)
        ax.text(a0, b0 + H[n] + 0.06 * pm, {'top': 'TOP', 'front': 'FRONT', 'side': 'RIGHT SIDE'}[n], fontsize=8.5, color=MUTED, va='bottom')
        axes[n] = (ax, vb[n])
    ax_l = meta.get('axes') or {}
    fa, (a0, a1, b0, b1) = axes['front']
    dim(fa, a0, a1, b0 - 0.45 * pm, True, '%.1f' % (a1 - a0))
    dim(fa, b0, b1, a0 - 0.45 * pm, False, '%.1f' % (b1 - b0))
    sa, (a0, a1, b0, b1) = axes['side']
    dim(sa, a0, a1, b0 - 0.45 * pm, True, '%.1f' % (a1 - a0))
    ta, (a0, a1, b0, b1) = axes['top']
    dim(ta, b0, b1, a0 - 0.45 * pm, False, '%.1f' % (b1 - b0))
    # free regions: right column above the side view, and the band above the top view
    rx0, ry0 = x0 + 2 * pad + W['front'] * k, y0 + 2.2 * pad + H['front'] * k
    r1 = (rx0, ry0, x0 + w - rx0, y0 + h - ry0)
    by0 = y0 + 3.0 * pad + (H['front'] + H['top']) * k
    r2 = (x0 + 0.2, by0, w - 0.4, y0 + h - by0)
    reg = max((r1, r2), key=lambda r: min(r[2], r[3] * 1.6) if r[2] > 1 and r[3] > 1 else 0)
    if job['family'] == 'tube' and job['cut_features']:
        drill_layout(fig, job, meta, (r2 if r2[2] > 1 and r2[3] > 1.2 else reg))
    elif reg[2] > 1 and reg[3] > 1:
        sq = min(reg[2], reg[3] - 0.3)
        ax = fig.add_axes([(reg[0] + (reg[2] - sq) / 2) / W_IN, reg[1] / H_IN, sq / W_IN, sq / H_IN])
        show(ax, meta, 'iso')
        ax.set_title('ISOMETRIC (not to scale)', fontsize=8.5, color=MUTED, loc='left')
    fig.text((x0 + 0.1) / W_IN, (y0 + h + 0.02) / H_IN, 'Views: long axis %s across, short axis %s up in FRONT (part design frame)'
             % (ax_l.get('long', '?'), ax_l.get('short', '?')), fontsize=7, color=MUTED)
    return k


def drill_layout(fig, job, meta, reg):
    """Cut-and-drill layout of a tube / rod: the stock length, then every hole as an ordinate from the left end along the long axis."""
    x0, y0, w, h = reg
    L = (meta.get('axes') or {}).get('long', 'y')
    li = 'xyz'.index(L)
    lo, hi = meta['lo'][li], meta['hi'][li]
    ax = fig.add_axes([x0 / W_IN, y0 / H_IN, w / W_IN, h / H_IN])
    ax.set_axis_off()
    ax.set_xlim(-0.06 * (hi - lo), 1.06 * (hi - lo))
    ax.set_ylim(0, 1)
    ax.text(-0.05 * (hi - lo), 0.95, 'CUT AND DRILL (positions from the left end, along %s; mm)' % L, fontsize=8.5, weight='bold', color=INK, va='top')
    ax.add_patch(plt.Rectangle((0, 0.42), hi - lo, 0.08, fill=False, ec=INK, lw=1.0))
    ax.annotate('', (0, 0.32), (hi - lo, 0.32), arrowprops=dict(arrowstyle='<|-|>', lw=0.7, color=INK, mutation_scale=7))
    ax.text((hi - lo) / 2, 0.3, 'cut length %.1f' % (hi - lo), ha='center', va='top', fontsize=8, color=INK)
    holes = []
    body = job['body_features'][0]
    bc = [(body['lo'][i] + body['hi'][i]) / 2 for i in range(3)]
    ri = (body.get('d_in') or 0) / 2
    for g in mk.collapse(job['cut_features']):
        for f in g['at']:
            c = (f['lo'][li] + f['hi'][li]) / 2 - lo
            ax_ = f.get('axis') or [0, 0, 0]
            k = max(range(3), key=lambda i: abs(ax_[i]))
            if f['lo'][k] < bc[k] - ri and f['hi'][k] > bc[k] + ri:
                how = 'through both walls along %s' % 'xyz'[k]
            else:
                how = 'one wall, %s%s side' % ('+' if (f['lo'][k] + f['hi'][k]) / 2 > bc[k] else '-', 'xyz'[k])
            holes.append((c, f.get('d_out', f['hi'][k] - f['lo'][k]), how, f['name']))
    holes.sort()
    Lt = hi - lo
    for n, (c, d, a, name) in enumerate(holes):          # full length: numbered markers
        ax.plot([c, c], [0.42, 0.5], color=INK, lw=0.8)
        ax.plot(c, 0.46, 'o', ms=4, mfc='white', mec=INK, mew=0.8)
        ax.text(c, 0.52 + 0.035 * (n % 2), str(n + 1), fontsize=6.5, ha='center', va='bottom', color=INK)
    if holes:
        c0, c1 = holes[0][0], holes[-1][0]
        span = max(c1 - c0, 1.0)
        m = max(0.15 * span, 6.0)
        d0, d1 = max(0.0, c0 - m), min(Lt, c1 + m)
        sx = lambda v: (v - d0) / (d1 - d0) * Lt              # noqa: E731  detail coordinate -> axes x
        yb = 0.66
        ax.text(0, yb + 0.2, 'DETAIL: %.1f to %.1f from the left end (enlarged %.0f x)' % (d0, d1, Lt / (d1 - d0)), fontsize=7.5, color=MUTED, va='bottom')
        ax.add_patch(plt.Rectangle((0, yb), Lt, 0.08, fill=False, ec=INK, lw=0.8))
        ax.plot([sx(d0), 0], [yb, 0.5], color=RULE, lw=0.5, ls=':')
        ax.plot([c0 - m if c0 - m > 0 else 0, c0 - m if c0 - m > 0 else 0], [0.42, 0.5], color=RULE, lw=0.5)
        for n, (c, d, a, name) in enumerate(holes):
            x_ = sx(c)
            ax.plot(x_, yb + 0.04, 'o', ms=max(3, d / (d1 - d0) * 400), mfc='white', mec=INK, mew=0.8)
            ax.text(x_, yb + 0.09 + 0.04 * (n % 2), '%d: %.1f' % (n + 1, c), fontsize=6.8, ha='center', va='bottom', color=INK)
    rows = ['%d   %.1f from the left end   dia %.1f, %s   (%s)' % (n + 1, c, d, a, name) for n, (c, d, a, name) in enumerate(holes)]
    ax.text(-0.05 * Lt, 0.22, 'HOLES' + chr(10) + chr(10).join(rows), fontsize=6.8, color=INK, va='top', family='monospace', linespacing=1.35)


def feature_rows(job):
    rows = []
    for tag, feats in (('body', job['body_features']), ('cut', job['cut_features'])):
        for g in mk.collapse(feats):
            f = g['f']
            rows.append((tag, g['n'], f['name'], mk.describe(f, g['at'])))
    return rows


def table(fig, rows, box, start):
    """Draw rows[start:] in box (inches); return the index of the first row that did not fit."""
    x0, y0, w, h = box
    ax = fig.add_axes([x0 / W_IN, y0 / H_IN, w / W_IN, h / H_IN])
    ax.set_axis_off()
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    y = h - 0.05
    ax.text(0, y, 'FEATURES (CAD bodies and shop cuts; part design frame, mm)', fontsize=8.5, weight='bold', va='top', color=INK)
    y -= 0.28
    ax.text(0.0, y, '#', fontsize=7, color=MUTED, va='top')
    ax.text(0.3, y, 'type', fontsize=7, color=MUTED, va='top')
    ax.text(0.92, y, 'feature (CAD name)', fontsize=7, color=MUTED, va='top')
    y -= 0.18
    ax.plot([0, w], [y, y], color=RULE, lw=0.5)
    y -= 0.06
    i = start
    while i < len(rows):
        tag, n, name, desc = rows[i]
        nl = textwrap.wrap(name, 74)
        dl = textwrap.wrap(desc, 78)
        need = 0.145 * (len(nl) + len(dl)) + 0.06
        if y - need < 0:
            break
        ax.text(0.0, y, '%d' % (i + 1), fontsize=7, va='top', color=INK)
        ax.text(0.3, y, ('%d x ' % n if n > 1 else '') + tag, fontsize=7, va='top', color=INK)
        for j, l in enumerate(nl):
            ax.text(0.92, y - j * 0.145, l, fontsize=7, va='top', color=INK)
        for j, l in enumerate(dl):
            ax.text(0.92, y - (len(nl) + j) * 0.145, l, fontsize=6.6, va='top', color=MUTED, family='monospace')
        y -= need
        i += 1
    return i


def title_block(fig, job, meta, sheet, nsheets, k, rev):
    x0, y0, w, h = 10.9, 0.35, 5.75, 2.25
    ax = fig.add_axes([x0 / W_IN, y0 / H_IN, w / W_IN, h / H_IN])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(INK)
        sp.set_linewidth(1.0)
    name = job['name']
    ax.text(0.1, h - 0.12, job['id'], fontsize=15, weight='bold', va='top', color=INK)
    ax.text(0.1, h - 0.5, '\n'.join(textwrap.wrap(name, 82)[:3]), fontsize=7.5, va='top', color=INK)
    mem = ', '.join(job['members'])
    mir = (' (%s: mirror image of the one shown, y -> -y)' % ', '.join(job['mirrored'])) if job.get('mirrored') else ''
    lines = ['Qty %d: %s%s' % (job['qty'], mem, mir),
             'Material: %s    CAD mass: %s g each' % (job['material'], job['mass_g']),
             'Size (design frame): %.1f x %.1f x %.1f mm' % tuple(meta['hi'][i] - meta['lo'][i] for i in range(3)),
             'Units mm. Third-angle projection. Views scale %s on a 17 x 11 in sheet.' % (('%.2g:1' % (k * 25.4)) if k * 25.4 >= 1 else ('1:%.2g' % (1 / (k * 25.4)))),
             'Tolerances: not set in the CAD (-). EST in a feature name = estimate in the CAD: measure the bought part first.',
             'Source: qp/A/cad (commit %s), drawings/make_drawings_a.py, %s. Sheet %d of %d.' % (rev, datetime.date.today().isoformat(), sheet, nsheets)]
    ax.text(0.1, 0.95, '\n'.join(lines), fontsize=7, va='top', color=INK, linespacing=1.45)
    ax.plot([0, w], [1.02, 1.02], color=INK, lw=0.6)
    stls = ', '.join('stl/%s.stl' % p for p in sorted((meta.get('stl') or {}).keys()))
    fig.text(0.6 / W_IN, 0.4 / H_IN, '\n'.join(textwrap.wrap('Process: ' + PROCESS[job['family']].replace('%s', stls or '-'), 150)),
             fontsize=7.5, color=INK, va='bottom')


def sheet_frame(fig):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.add_patch(plt.Rectangle((0.25 / W_IN, 0.25 / H_IN), 1 - 0.5 / W_IN, 1 - 0.5 / H_IN, fill=False, lw=1.2, ec=INK))


def main():
    jobs = json.load(open(os.path.join(WORK, 'jobs.json'), encoding='utf-8'))
    rev = git_rev()
    stl_dir = os.path.join(OUT, 'stl')
    shutil.rmtree(stl_dir, ignore_errors=True)
    os.makedirs(stl_dir)
    links, prints = {}, []
    index, made = [], []
    allpdf = PdfPages(os.path.join(OUT, 'DRAWINGS-A.pdf'))
    for job in jobs:
        mp = os.path.join(WORK, job['id'] + '.json')
        if not os.path.exists(mp):
            index.append((job, None, 'NOT DRAWN: the Blender stage failed for this part (see the stage 2 log)'))
            continue
        meta = json.load(open(mp))
        rows = feature_rows(job)
        pages, i = [], 0
        # first sheet: views left, table right; continuation sheets: table only
        figs = []
        fig = plt.figure(figsize=(W_IN, H_IN))
        fig.patch.set_facecolor('white')
        sheet_frame(fig)
        k = place_views(fig, meta, (0.35, 1.0, 10.3, 9.5), job)
        i = table(fig, rows, (10.95, 2.85, 5.7, 7.85), 0)
        figs.append(fig)
        while i < len(rows):
            fig = plt.figure(figsize=(W_IN, H_IN))
            sheet_frame(fig)
            j = table(fig, rows, (0.6, 2.85, 7.9, 7.85), i)
            if j < len(rows):
                j = table(fig, rows, (8.75, 2.85, 7.9, 7.85), j)
            i = j
            figs.append(fig)
        with PdfPages(os.path.join(OUT, job['id'] + '.pdf')) as pdf:
            for n, f in enumerate(figs):
                title_block(f, job, meta, n + 1, len(figs), k, rev)
                pdf.savefig(f)
                allpdf.savefig(f)
                if n == 0:
                    f.savefig(os.path.join(OUT, job['id'] + '.png'), dpi=110)
                plt.close(f)
        made.append(job['id'])
        nm_all = dict(meta.get('member_non_manifold') or {})
        nm_all[job['members'][0]] = meta.get('non_manifold', 0)
        for pid in job['members']:
            links[pid] = {'drawing_url': GH + job['id'] + '.pdf'}
        if job['family'] == 'print':
            for pid, fn in sorted((meta.get('stl') or {}).items()):
                shutil.copyfile(os.path.join(WORK, fn), os.path.join(stl_dir, pid + '.stl'))
                links[pid]['stl_url'] = GH + 'stl/' + pid + '.stl'
                prints.append((pid, job, meta, nm_all.get(pid, '-'), pieces(os.path.join(stl_dir, pid + '.stl'))))
        index.append((job, meta, '%d sheet(s), %d features' % (len(figs), len(rows))))
    allpdf.close()
    md = ['# Concept A engineering drawings', '',
          'Generated from the CAD by `drawings/make_drawings_a.py` (commit %s, %s). One sheet per distinct made part; mirror pairs and identical parts share a sheet. '
          'Every dimension is the CAD value; feature names that say EST are estimates. Re-run after any CAD change. All sheets: [DRAWINGS-A.pdf](DRAWINGS-A.pdf).' % (rev, datetime.date.today().isoformat()), '',
          '| Drawing | Parts (qty) | Material | Size mm (design frame) | Sheets |', '|---|---|---|---|---|']
    for job, meta, note in index:
        size = '%.1f x %.1f x %.1f' % tuple(meta['hi'][i] - meta['lo'][i] for i in range(3)) if meta else '-'
        link = '[%s](%s.pdf)' % (job['id'], job['id']) if meta else job['id']
        md.append('| %s | %s (%d) | %s | %s | %s |' % (link, ', '.join(job['members']), job['qty'], job['material'], size, note))
    md += ['', '## Print list: every 3-D printed part', '',
           'One STL per printed part (mirror images have their own file), in mm, in the part\'s design frame: choose the bed face in the slicer. '
           'Click a file to see it in 3-D on GitHub; use the download button there. "Open edges" counts non-manifold edges in the mesh '
           '(0 is clean; a slicer usually repairs a few, but check the preview). "Pieces" must be 1: more means a body floats free of the part.', '',
           '| Part | STL | Drawing | Material | CAD mass g | Size mm | Pieces | Open edges |', '|---|---|---|---|---|---|---|---|']
    for pid, job, meta, nm, npc in prints:
        size = '%.1f x %.1f x %.1f' % tuple(meta['hi'][i] - meta['lo'][i] for i in range(3))
        md.append('| %s | [%s.stl](stl/%s.stl) | [%s](%s.pdf) | %s | %s | %s | %s | %s |' % (pid, pid, pid, job['id'], job['id'], job['material'], job['mass_g'], size,
                                                                                    npc if npc == 1 else '**%d: CHECK (a body is not attached)**' % npc, nm))
    bad = [p_ for p_, _j, _m, _n, n_ in prints if n_ != 1]
    print('stage 3: printed parts not in one piece: %s' % (', '.join(bad) or 'none'))
    open(os.path.join(OUT, 'DRAWINGS-A.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    json.dump(links, open(os.path.join(OUT, 'links.json'), 'w', encoding='utf-8'), indent=1, sort_keys=True)
    print('stage 3: %d STL files for printed parts, links for %d parts' % (len(prints), len(links)))
    print('stage 3: %d of %d drawings composed -> out/DRAWINGS-A.pdf' % (len(made), len(jobs)))


if __name__ == '__main__':
    main()
