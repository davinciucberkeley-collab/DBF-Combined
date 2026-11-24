"""make_sheet_a.py - the concept A general-arrangement sheet (FIG A1-01) as an SVG over the Blender orthographic renders.

    blender -b --factory-startup -P redesign/showcase/drawing/render_drawing.py -- --root <abs>/redesign/qp/A/cad/model \
        --out <abs>/redesign/showcase/concept-a/drawing           # 1. top/front/side/iso renders + views.json (~1 min)
    python -I redesign/showcase/concept-a/make_sheet_a.py          # 2. sheet.svg + a-*.webp, copied into site/assets/drawing/

Same layout, styling (diagram-style.md) and one-scale rule as redesign/showcase/drawing/make_sheet.py (K09-L), which is
left untouched. Dimensions come from the CAD itself, not from K09-L's params.json: the model bounding box in views.json
(render_drawing.py, built from qp/A/cad/model) and the constants of qp/A/cad/amodel (span 0.90 m, chord 0.245 m,
motor stations from the cup origins, APC 9x4.5MR = 9 in, fin tube 0.36 m); CG x from qp/A/params-A.json (mass.cg_x_mm,
CAD mass). The block `<!-- GA-SHEET:a1 -->` in redesign/site/app.html is replaced with the A sheet.
"""
import csv
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(REDESIGN, 'site')
SRC = os.path.join(HERE, 'drawing')
SITE_ASSETS = os.path.join(SITE, 'assets', 'drawing')
P = json.load(open(os.path.join(REDESIGN, 'qp', 'A', 'params-A.json'), encoding='utf-8'))
V = json.load(open(os.path.join(SRC, 'views.json'), encoding='utf-8'))

SHEET_W, GUTTER, SCALE = 1200, 48, 520.0
DATE = '2026-11-19'
NBSP = ' '

# CAD facts (m), see the module docstring
span, chord = 0.90, 0.245
motor_y, motor_z = 0.228, 0.156
prop_d = 9 * 0.0254
x_prop = -0.1225                      # prop plane (PRP-002 x -0.133..-0.112)
fin_y, fin_h = 0.38, 0.36
spar_x = 0.060
elev_x0, elev_in, elev_out = 0.183, 0.041, 0.35
cg_x = P['mass']['cg_x_mm']['value'] / 1000.0
lo, hi = V['bbox_m']['lo'], V['bbox_m']['hi']
length_all = hi[0] - lo[0]
ppm = V['ppm']
k = SCALE / ppm


def mm(v):
    s = '%d' % round(v * 1000)
    return s if len(s) < 4 else s[:-3] + NBSP + s[-3:]


class View:
    def __init__(self, name, x0, y0):
        m = V['views'][name]
        self.name, self.m = name, m
        self.x0, self.y0 = x0, y0
        self.w, self.h = m['w'] * k, m['h'] * k
        self.x1, self.y1 = x0 + self.w, y0 + self.h

    def pt(self, x, y, z):
        r, u = self.m['r'], self.m['u']
        pr = x * r[0] + y * r[1] + z * r[2]
        pu = x * u[0] + y * u[1] + z * u[2]
        px = (pr - self.m['cu']) * ppm + self.m['w'] / 2
        py = self.m['h'] / 2 - (pu - self.m['cv']) * ppm
        return (self.x0 + px * k, self.y0 + py * k)

    def image(self, prefix):
        return ('<image class="ga-img" x="%.1f" y="%.1f" width="%.1f" height="%.1f" href="%s%s" '
                'preserveAspectRatio="none"/>' % (self.x0, self.y0, self.w, self.h, prefix, self.m['file']))


TOP_Y = 60
top = View('top', GUTTER, TOP_Y)
GAP_ROW = 104
front = View('front', GUTTER, top.y1 + GAP_ROW)
iso_w = 380.0
iso_h = iso_w * V['views']['iso']['h'] / V['views']['iso']['w']
ISO_X = 640.0
NOTES_H = 5 * 15
side_y0 = max(front.y0, TOP_Y + iso_h + 22 + NOTES_H + 112)
SIDE_X = 790.0
side = View('side', SIDE_X, side_y0)
TB_Y = max(front.y1 + 92, side.y1 + 92)
TB_H = 46
SHEET_H = TB_Y + TB_H + 10


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, cls, anchor='start', extra=''):
    return '<text class="%s" x="%.1f" y="%.1f" text-anchor="%s"%s>%s</text>' % (cls, x, y, anchor, extra, esc(s))


def dim_h(x1, x2, y, label, ext_from, mk, above=True, ext_gap=3):
    out = []
    for ex, ey in ext_from:
        d = 1 if y > ey else -1
        out.append('<line class="ga-ext" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (ex, ey + d * ext_gap, ex, y + d * 4))
    out.append('<line class="ga-dim" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" marker-start="url(#%s-a)" marker-end="url(#%s-a)"/>'
               % (x1, y, x2, y, mk, mk))
    out.append(text((x1 + x2) / 2, y - 5 if above else y + 14, label, 'ga-dimt', 'middle'))
    return '\n'.join(out)


def dim_v(y1, y2, x, label, ext_from, mk, side_='right', ext_gap=3):
    out = []
    for ex, ey in ext_from:
        d = 1 if x > ex else -1
        out.append('<line class="ga-ext" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (ex + d * ext_gap, ey, x + d * 4, ey))
    out.append('<line class="ga-dim" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" marker-start="url(#%s-a)" marker-end="url(#%s-a)"/>'
               % (x, y1, x, y2, mk, mk))
    if side_ == 'right':
        out.append(text(x + 7, (y1 + y2) / 2 + 4, label, 'ga-dimt', 'start'))
    else:
        out.append(text(x - 7, (y1 + y2) / 2 + 4, label, 'ga-dimt', 'end'))
    return '\n'.join(out)


def callout(anchor, bends, tx, ty, label, align='start'):
    pts = [anchor] + bends
    d = 'M' + ' L'.join('%.1f,%.1f' % p for p in pts)
    out = ['<path class="ga-lead" d="%s"/>' % d, '<circle class="ga-anchor" cx="%.1f" cy="%.1f" r="2.4"/>' % anchor]
    lines = label if isinstance(label, list) else [label]
    for i, ln in enumerate(lines):
        out.append(text(tx, ty + i * 15, ln, 'ga-call', align))
    return '\n'.join(out)


def cg_symbol(x, y):
    return ('<g transform="translate(%.1f,%.1f)"><circle class="ga-cgc" r="6"/>'
            '<path class="ga-cgf" d="M0,0 L6,0 A6,6 0 0 0 0,-6 Z M0,0 L-6,0 A6,6 0 0 0 0,6 Z"/></g>' % (x, y))


def build(prefix, mk, standalone=False):
    o = [top.image(prefix), front.image(prefix), side.image(prefix)]
    iso = V['views']['iso']
    iso_x, iso_y = ISO_X, TOP_Y
    o.append('<image class="ga-img" x="%.1f" y="%.1f" width="%.1f" height="%.1f" href="%s%s"/>' % (iso_x, iso_y, iso_w, iso_h, prefix, iso['file']))
    lab_y_a, lab_y_b = TOP_Y - 36, side.y0 - 88
    o.append(text(top.x0, lab_y_a, 'TOP · NOSE UP', 'ga-view'))
    o.append(text(iso_x, lab_y_a, 'ISO · NO SCALE', 'ga-view'))
    o.append(text(front.x0, front.y0 - 20, 'FRONT · FROM THE NOSE', 'ga-view'))
    o.append(text(side.x0, lab_y_b, 'SIDE · NOSE LEFT', 'ga-view'))

    # construction: prop discs (dashed), spar, CG
    r = prop_d / 2
    for sy in (1, -1):
        for sz in (1, -1):
            c = front.pt(0, sy * motor_y, sz * motor_z)
            o.append('<circle class="ga-hid" cx="%.1f" cy="%.1f" r="%.1f"/>' % (c[0], c[1], r * SCALE))
        a, b = top.pt(x_prop, sy * (motor_y - r), 0), top.pt(x_prop, sy * (motor_y + r), 0)
        o.append('<line class="ga-hid" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (a[0], a[1], b[0], b[1]))
        a, b = side.pt(x_prop, 0, sy * (motor_z - r)), side.pt(x_prop, 0, sy * (motor_z + r))
        o.append('<line class="ga-hid" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (a[0], a[1], b[0], b[1]))
    a, b = top.pt(spar_x, -span / 2, 0), top.pt(spar_x, span / 2, 0)
    o.append('<line class="ga-hid" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (a[0], a[1], b[0], b[1]))
    o.append(cg_symbol(*top.pt(cg_x, 0, 0)))
    c = top.pt(cg_x, 0, 0)
    o.append(text(c[0] + 9, c[1] - 7, 'CG', 'ga-cgl'))

    # dimensions
    hub_l, hub_r = top.pt(x_prop - 0.012, -motor_y, 0), top.pt(x_prop - 0.012, motor_y, 0)
    o.append(dim_h(hub_l[0], hub_r[0], top.y0 - 16, mm(2 * motor_y) + ' motor axes', [hub_l, hub_r], mk))
    le, te = top.pt(0, span / 2, 0), top.pt(chord, span / 2, 0)
    o.append(dim_v(le[1], te[1], top.x1 + 16, mm(chord), [le, te], mk, 'right'))
    tip_l, tip_r = front.pt(0, span / 2, -0.012), front.pt(0, -span / 2, -0.012)
    o.append(dim_h(tip_l[0], tip_r[0], front.y1 + 52, mm(span) + ' span', [tip_l, tip_r], mk, above=False))
    up_, lo_ = front.pt(0, -(motor_y + r + 0.01), motor_z), front.pt(0, -(motor_y + r + 0.01), -motor_z)
    o.append(dim_v(up_[1], lo_[1], front.x1 + 16, mm(2 * motor_z), [up_, lo_], mk, 'right'))
    n0, n1 = side.pt(lo[0], 0, 0.0), side.pt(hi[0], 0, 0.0)
    o.append(dim_h(n0[0], n1[0], side.y1 + 18, mm(length_all) + ' overall · standing height in hover', [n0, n1], mk, above=False))
    f0, f1 = side.pt(hi[0], 0, fin_h / 2), side.pt(hi[0], 0, -fin_h / 2)
    o.append(dim_v(f0[1], f1[1], side.x1 + 16, mm(fin_h) + ' fin', [f0, f1], mk, 'right'))

    # callouts
    a = top.pt(chord * 0.88, -(elev_in + elev_out) / 2, 0)
    ty = front.y0 - 70
    o.append(callout(a, [(a[0], ty - 4)], a[0] + 6, ty, 'Elevon, 1 per side, 25 % chord, tape hinge'))
    a = top.pt(-0.07, -0.02, 0)
    tx, ty0 = top.pt(0.088, -0.43, 0)
    o.append(callout(a, [(tx - 4, ty0 - 5)], tx, ty0 + 4, ['Cage: hub, 4 CF arms,', 'bridge tube, V struts']))
    c = front.pt(0, -motor_y, motor_z)
    import math
    ang = 0.9
    a = (c[0] + r * SCALE * math.cos(ang), c[1] - r * SCALE * math.sin(ang))
    ty = front.y0 - 52
    o.append(callout(a, [(a[0] + 14, ty - 4)], a[0] + 8, ty,
                     'Ø %s prop disc × 4 · APC 9×4.5MR on SunnySky X2216' % mm(prop_d), 'end'))
    a = side.pt(-0.075, 0, 0.10)
    bx = side.pt(0.02, 0, 0)[0]
    ty = side.y0 - 42
    o.append(callout(a, [(bx, a[1] - (bx - a[0])), (bx, ty - 4)], bx - 6, ty, 'Arm CF 12 × 10, %s mm, canted 17°' % mm(0.245), 'end'))
    a = side.pt(0.335, 0, fin_h / 2 - 0.004)
    ty = side.y0 - 60
    o.append(callout(a, [(a[0], ty - 4)], a[0] - 6, ty, 'Foot pad EVA/PE 12 × 15 × 30 mm', 'end'))
    a = side.pt(0.29, 0, -0.09)
    bx = side.x1 + 8
    ty = side.y1 + 56
    o.append(callout(a, [(bx, a[1] + (bx - a[0])), (bx, ty - 4)], bx - 6, ty, 'Fin: CF tube 16 × 14, XPS fairing, 1 per side', 'end'))

    nx, ny = iso_x, iso_y + iso_h + 22
    notes = ['Frame: x aft from the wing LE, y right, z up (cruise).',
             'Hover: nose up on the four fin-tip feet; props cant 17°.',
             'Elevon panels at y %s–%s mm each side.' % (mm(elev_in), mm(elev_out)),
             'Dashed: prop disc, hidden spar. Blue: dimension, mm.',
             'Geometry: qp/A/cad CAD build, %d parts.' % P['cad3d']['parts']['value']]  # modelled parts (collision report); parts-a.csv also lists the consumable kits HRN-001 / HRD-001
    for i, ln in enumerate(notes):
        o.append(text(nx, ny + i * 15, ln, 'ga-note'))

    x, y = GUTTER, TB_Y
    w = SHEET_W - 2 * GUTTER
    o.append('<rect class="ga-tb" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>' % (x, y, w, TB_H))
    cells = [('', None, 290), ('Concept A', 'General arrangement · three views, one scale', 330),
             ('REV', 'D-196', 90), ('SCALE', 'bar · %d px/m' % SCALE, 120), ('UNITS', 'mm', 64),
             ('DATE', DATE, 110), ('STATUS', 'PROPOSED', 100)]
    cx = x
    for i, (lab, val, cw) in enumerate(cells):
        if i:
            o.append('<line class="ga-tbl" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (cx, y, cx, y + TB_H))
        if lab == '':
            bx0, by = cx + 14, y + 26
            bw = 0.5 * SCALE
            o.append('<path class="ga-bar" d="M%.1f,%.1f h%.1f M%.1f,%.1f v8 M%.1f,%.1f v8 M%.1f,%.1f v8" />'
                     % (bx0, by, bw, bx0, by - 4, bx0 + bw / 2, by - 4, bx0 + bw, by - 4))
            o.append(text(bx0, by + 16, '0', 'ga-tbv'))
            o.append(text(bx0 + bw / 2, by + 16, '250', 'ga-tbv', 'middle'))
            o.append(text(bx0 + bw, by + 16, '500 mm', 'ga-tbv', 'end'))
        elif lab == 'Concept A':
            o.append(text(cx + 12, y + 19, lab, 'ga-tbt'))
            o.append(text(cx + 12, y + 36, val, 'ga-tbv'))
        else:
            o.append(text(cx + 10, y + 16, lab, 'ga-tbk'))
            o.append(text(cx + 10, y + 34, val, 'ga-tbv'))
        cx += cw

    style = '''<style>
.ga-sheet text { font-family: var(--font-sans, "IBM Plex Sans", system-ui, sans-serif); }
.ga-sheet .ga-view { font-size: 11px; font-weight: 600; letter-spacing: 0.04em; fill: var(--fg-3, #6B7280); }
.ga-sheet .ga-dim { stroke: var(--accent, #1F5FC7); stroke-width: 1; fill: none; }
.ga-sheet .ga-ext { stroke: var(--accent, #1F5FC7); stroke-width: 0.75; opacity: 0.8; }
.ga-sheet .ga-dimt { font-family: var(--font-mono, "IBM Plex Mono", monospace); font-size: 12px; font-weight: 500; fill: var(--accent, #1F5FC7); }
.ga-sheet .ga-arr { fill: var(--accent, #1F5FC7); }
.ga-sheet .ga-hid { stroke: var(--fg-3, #6B7280); stroke-width: 0.75; stroke-dasharray: 5 3; fill: none; }
.ga-sheet .ga-lead { stroke: var(--fg-2, #4B5563); stroke-width: 1; fill: none; }
.ga-sheet .ga-anchor { fill: var(--fg-2, #4B5563); }
.ga-sheet .ga-call { font-size: 12px; font-weight: 500; fill: var(--fg-2, #4B5563); }
.ga-sheet .ga-note { font-size: 11px; fill: var(--fg-3, #6B7280); }
.ga-sheet .ga-cgc { fill: var(--panel, #fff); stroke: var(--fg, #121619); stroke-width: 1; }
.ga-sheet .ga-cgf { fill: var(--fg, #121619); }
.ga-sheet .ga-cgl { font-family: var(--font-mono, "IBM Plex Mono", monospace); font-size: 10px; font-weight: 500; fill: var(--fg, #121619); }
.ga-sheet .ga-tb { fill: none; stroke: var(--line-2, #CBD2DB); stroke-width: 1; }
.ga-sheet .ga-tbl { stroke: var(--line-2, #CBD2DB); stroke-width: 1; }
.ga-sheet .ga-tbk { font-size: 9px; font-weight: 600; letter-spacing: 0.06em; fill: var(--fg-3, #6B7280); }
.ga-sheet .ga-tbv { font-family: var(--font-mono, "IBM Plex Mono", monospace); font-size: 11px; fill: var(--fg, #121619); }
.ga-sheet .ga-tbt { font-size: 14px; font-weight: 600; fill: var(--fg, #121619); }
.ga-sheet .ga-bar { stroke: var(--fg, #121619); stroke-width: 1; fill: none; }
</style>'''
    defs = ('<defs><marker id="%s-a" markerWidth="8" markerHeight="6" refX="7.5" refY="3" orient="auto-start-reverse" markerUnits="userSpaceOnUse">'
            '<path class="ga-arr" d="M0,0 L8,3 L0,6 Z"/></marker></defs>' % mk)
    head = ('<svg class="ga-sheet" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 %d %d" role="img" '
            'aria-label="Concept A general arrangement: top, front and side views at one scale with an iso inset, dimensions in mm">'
            % (SHEET_W, SHEET_H))
    bg = '<rect width="%d" height="%d" fill="#FFFFFF"/>' % (SHEET_W, SHEET_H) if standalone else ''
    return head + '\n' + style + '\n' + defs + '\n' + bg + '\n'.join(o) + '\n</svg>'


def webp():
    """PNG renders -> a-<view>.webp (quality 88, alpha kept) in this folder and in site/assets/drawing/; views.json updated."""
    from PIL import Image
    os.makedirs(SITE_ASSETS, exist_ok=True)
    for m in V['views'].values():
        base = os.path.splitext(m['file'])[0].replace('a-', '', 1) if m['file'].startswith('a-') else os.path.splitext(m['file'])[0]
        png = os.path.join(SRC, base + '.png')
        out = os.path.join(SRC, 'a-' + base + '.webp')
        if os.path.exists(png):
            Image.open(png).save(out, 'WEBP', quality=88, method=6)
            os.remove(png)
        m['file'] = 'a-' + base + '.webp'
        shutil.copyfile(out, os.path.join(SITE_ASSETS, m['file']))
    json.dump(V, open(os.path.join(SRC, 'views.json'), 'w', encoding='utf-8'), indent=1)


def main():
    webp()
    svg = build('a-' if False else '', 'ga0', standalone=True)
    with open(os.path.join(SRC, 'a-sheet.svg'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg + '\n')
    shutil.copyfile(os.path.join(SRC, 'a-sheet.svg'), os.path.join(SITE_ASSETS, 'a-sheet.svg'))
    app = os.path.join(SITE, 'app.html')
    html = open(app, encoding='utf-8').read()
    pat = re.compile(r'(<!-- GA-SHEET:a1 -->)(.*?)(<!-- /GA-SHEET -->)', re.S)
    html, c = pat.subn(lambda m: m.group(1) + '\n' + build('assets/drawing/', 'ga-a1') + '\n' + m.group(3), html)
    with open(app, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print('sheet %d x %d px; app.html blocks replaced: %d' % (SHEET_W, SHEET_H, c))


if __name__ == '__main__':
    main()
