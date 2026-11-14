"""make_sheet.py - the K09-L general-arrangement sheet (FIG A1-01 / FIG CFG-01) as an SVG overlay on the Blender
orthographic renders from render_drawing.py.

    python -I redesign/showcase/drawing/make_sheet.py

Reads redesign/params/params.json (dimensions) and redesign/site/assets/drawing/views.json (pixel mapping of the
renders), writes redesign/site/assets/drawing/sheet.svg (standalone) and replaces the two
<!-- GA-SHEET:<key> --> ... <!-- /GA-SHEET --> blocks in redesign/site/app.html (inline, themed by tokens.css).
Design: redesign/design-system/diagram-style.md. Sheet 1200 px wide; one scale for the three elevations.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(REDESIGN, 'site')
ASSETS = os.path.join(SITE, 'assets', 'drawing')

SHEET_W = 1200
GUTTER = 48
SCALE = 520.0                   # sheet px per metre (all three elevations)
DATE = '2026-11-11'
NBSP = ' '                 # thin space: thousands separator and value/unit gap

P = json.load(open(os.path.join(REDESIGN, 'params', 'params.json'), encoding='utf-8'))
V = json.load(open(os.path.join(ASSETS, 'views.json'), encoding='utf-8'))


def pv(path):
    d = P
    for k in path.split('.'):
        d = d[k]
    return d['value']


def mm(v):
    s = '%d' % round(v * 1000)
    return s if len(s) < 4 else s[:-3] + NBSP + s[-3:]


# ---------------------------------------------------------------- geometry from params (m)
span = pv('wing.span_m')
chord = pv('wing.chord_m')
motor_y, motor_z = pv('propulsion.stations.y_m'), pv('propulsion.stations.z_m')
prop_d = pv('propulsion.prop_diameter_m')
x_prop = pv('propulsion.stations.x_prop_plane_m')
fin_chord, fin_half = pv('fins.chord_m'), pv('fins.half_height_m')
tube_len = pv('fins.tube.length_m')
pod_l, pod_w, pod_h = pv('pod.size_m')
pod_x0, pod_z0 = pv('pod.x_le_m'), pv('pod.z_base_m')
foot = pv('cg.foot_height_m')
pad_z = pv('landing.pad_contact_z_m')
cg_x, cg_z = pv('cg.x_target_m'), pv('cg.z_target_m')
spar_x, spar_len = pv('wing.spar.x_m'), pv('wing.spar.length_m')
elev_frac = pv('wing.elevon.chord_frac')
elev_in, elev_out = pv('wing.elevon.inboard_y_m'), pv('wing.elevon.outboard_y_m')
rev = pv('meta.revision')
prop_name = pv('propulsion.prop').split(' / ')[0]          # 'APC 11x5.5MR'
prop_name = prop_name.replace('x', '×')
motor_name = ' '.join(pv('propulsion.motor').split()[:2])  # 'SunnySky X3108S'
lo, hi = V['bbox_m']['lo'], V['bbox_m']['hi']               # model extent: pitot tip .. foot pad, prop tips
length_all = hi[0] - lo[0]
ppm = V['ppm']
k = SCALE / ppm


class View:
    """One orthographic render placed on the sheet; world (x, y, z) -> sheet px."""
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


# ---------------------------------------------------------------- layout (sheet px)
TOP_Y = 60
top = View('top', GUTTER, TOP_Y)
GAP_ROW = 104
front = View('front', GUTTER, top.y1 + GAP_ROW)
SIDE_X = SHEET_W - GUTTER - 12 - V['views']['side']['w'] * k
side = View('side', SIDE_X, front.y0)
iso_w = V['views']['side']['w'] * k
iso_h = iso_w * V['views']['iso']['h'] / V['views']['iso']['w']
TB_Y = side.y1 + 92
TB_H = 46
SHEET_H = TB_Y + TB_H + 10


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, cls, anchor='start', extra=''):
    return '<text class="%s" x="%.1f" y="%.1f" text-anchor="%s"%s>%s</text>' % (cls, x, y, anchor, extra, esc(s))


def dim_h(x1, x2, y, label, ext_from, mk, above=True, ext_gap=3):
    """Horizontal dimension between sheet x1..x2 on line y; ext_from = [(x, y_feature), ...] extension lines."""
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
    """Leader from the anchor (dot) through bends to the text; the text sits beside the last point."""
    pts = [anchor] + bends
    d = 'M' + ' L'.join('%.1f,%.1f' % p for p in pts)
    out = ['<path class="ga-lead" d="%s"/>' % d,
           '<circle class="ga-anchor" cx="%.1f" cy="%.1f" r="2.4"/>' % anchor]
    lines = label if isinstance(label, list) else [label]
    for i, ln in enumerate(lines):
        out.append(text(tx, ty + i * 15, ln, 'ga-call', align))
    return '\n'.join(out)


def cg_symbol(x, y):
    return ('<g transform="translate(%.1f,%.1f)"><circle class="ga-cgc" r="6"/>'
            '<path class="ga-cgf" d="M0,0 L6,0 A6,6 0 0 0 0,-6 Z M0,0 L-6,0 A6,6 0 0 0 0,6 Z"/></g>' % (x, y))


def build(prefix, mk, standalone=False):
    o = []
    # ---------------------------------------------------------------- views
    o.append(top.image(prefix)); o.append(front.image(prefix)); o.append(side.image(prefix))
    iso = V['views']['iso']
    iso_x, iso_y = side.x0, TOP_Y
    o.append('<image class="ga-img" x="%.1f" y="%.1f" width="%.1f" height="%.1f" href="%s%s"/>' % (iso_x, iso_y, iso_w, iso_h, prefix, iso['file']))

    # view labels (small caps, top-left of each view area)
    lab_y_a, lab_y_b = TOP_Y - 36, front.y0 - 88
    o.append(text(top.x0, lab_y_a, 'TOP · NOSE UP', 'ga-view'))
    o.append(text(iso_x, lab_y_a, 'ISO · NO SCALE', 'ga-view'))
    # FRONT label sits below the elevon callout so the elevon leader (dropping from the top view) never crosses it
    o.append(text(front.x0, front.y0 - 34, 'FRONT · FROM THE NOSE', 'ga-view'))
    o.append(text(side.x0, lab_y_b, 'SIDE · NOSE LEFT', 'ga-view'))

    # ---------------------------------------------------------------- construction: prop discs, hidden spar, CG
    r = prop_d / 2
    for sy in (1, -1):
        for sz in (1, -1):
            c = front.pt(0, sy * motor_y, sz * motor_z)
            o.append('<circle class="ga-hid" cx="%.1f" cy="%.1f" r="%.1f"/>' % (c[0], c[1], r * SCALE))
        a, b = top.pt(x_prop, sy * (motor_y - r), 0), top.pt(x_prop, sy * (motor_y + r), 0)
        o.append('<line class="ga-hid" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (a[0], a[1], b[0], b[1]))
        a, b = side.pt(x_prop, 0, sy * (motor_z - r)), side.pt(x_prop, 0, sy * (motor_z + r))
        o.append('<line class="ga-hid" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (a[0], a[1], b[0], b[1]))
    a, b = top.pt(spar_x, -spar_len / 2, 0), top.pt(spar_x, spar_len / 2, 0)
    o.append('<line class="ga-hid" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (a[0], a[1], b[0], b[1]))
    o.append(cg_symbol(*top.pt(cg_x, 0, 0)))
    c = side.pt(cg_x, 0, cg_z)
    o.append(cg_symbol(*c))
    o.append(text(c[0] + 9, c[1] - 7, 'CG', 'ga-cgl'))

    # ---------------------------------------------------------------- dimensions (mm)
    # TOP: motor axes 640 above; chord 320 right
    hub_l, hub_r = top.pt(x_prop - 0.012, -motor_y, 0), top.pt(x_prop - 0.012, motor_y, 0)
    yline = top.y0 - 16
    o.append(dim_h(hub_l[0], hub_r[0], yline, mm(2 * motor_y) + ' motor axes', [hub_l, hub_r], mk))
    le, te = top.pt(0, span / 2, 0), top.pt(chord, span / 2, 0)
    xline = top.x1 + 16
    o.append(dim_v(le[1], te[1], xline, mm(chord), [le, te], mk, 'right'))
    # FRONT: span 1150 below (outside the prop discs); motor z spacing 380 right, from the blade tips
    tip_l, tip_r = front.pt(0, span / 2, -0.009), front.pt(0, -span / 2, -0.009)
    yline = front.y1 + 52
    o.append(dim_h(tip_l[0], tip_r[0], yline, mm(span) + ' span', [tip_l, tip_r], mk, above=False))
    up_, lo_ = front.pt(0, -(motor_y + r + 0.01), motor_z), front.pt(0, -(motor_y + r + 0.01), -motor_z)
    xline = front.x1 + 16
    o.append(dim_v(up_[1], lo_[1], xline, mm(2 * motor_z), [up_, lo_], mk, 'right'))
    # SIDE: pod length above; overall length below; foot-pad stance right
    p0, p1 = side.pt(pod_x0, 0, pod_z0 + pod_h), side.pt(pod_x0 + pod_l, 0, pod_z0 + pod_h)
    o.append(dim_h(p0[0], p1[0], side.y0 - 16, mm(pod_l) + ' pod', [p0, p1], mk))
    n0, n1 = side.pt(lo[0], 0, 0.045), side.pt(hi[0], 0, -pad_z)
    o.append(dim_h(n0[0], n1[0], side.y1 + 18, mm(length_all) + ' overall · standing height in hover', [n0, n1], mk, above=False))
    f0, f1 = side.pt(hi[0], 0, pad_z), side.pt(hi[0], 0, -pad_z)
    o.append(dim_v(f0[1], f1[1], side.x1 + 16, mm(2 * pad_z), [f0, f1], mk, 'right'))

    # ---------------------------------------------------------------- callouts
    # elevon (top view, left outboard panel) -> gap under the top view, left
    a = top.pt(chord * (1 - elev_frac / 2), -(elev_out[0] + elev_out[1]) / 2, 0)
    ty = front.y0 - 70
    o.append(callout(a, [(a[0], ty - 4)], a[0] + 6, ty,
                     'Elevon, 2 per side, %d %% chord, tape hinge' % round(elev_frac * 100)))
    # pod (top view) -> the empty corner ahead of the left wing, between the motor-axis extension line and the pod
    a = top.pt(-0.09, -pod_w / 2, 0)
    o.append(callout(a, [(a[0] - 12, a[1])], a[0] - 18, a[1] - 4,
                     ['Pod %s×%s×%s' % (mm(pod_l), mm(pod_w), mm(pod_h)), 'pack, FC, GPS'], 'end'))
    # prop disc (front view, upper-right circle) -> gap above the front view, right
    c = front.pt(0, -motor_y, motor_z)
    ang = 0.9
    import math
    a = (c[0] + r * SCALE * math.cos(ang), c[1] - r * SCALE * math.sin(ang))
    ty = front.y0 - 52
    o.append(callout(a, [(a[0] + 14, ty - 4)], a[0] + 8, ty,
                     'Ø %s prop disc × 4 · %s on %s' % (mm(prop_d), prop_name, motor_name), 'end'))
    # motor tube (side view) -> above the side view, left of the pod dimension's right extension line
    a = side.pt(0.045, 0, 0.14)
    bx = side.pt(0.11, 0, 0)[0]
    ty = side.y0 - 42
    o.append(callout(a, [(bx, a[1] - (bx - a[0])), (bx, ty - 4)], bx - 6, ty,
                     'Motor tube CF 22 × 20, %s mm long' % mm(tube_len), 'end'))
    # foot (side view, upper foot) -> above the side view, right
    a = side.pt(0.345, 0, pad_z - 0.004)
    ty = side.y0 - 60
    o.append(callout(a, [(a[0], ty - 4)], a[0] - 6, ty,
                     'Foot, crushable XPS cartridge, %s mm' % mm(foot), 'end'))
    # fin (side view, lower fin) -> below the side view, right, past the overall dimension
    a = side.pt(0.24, 0, -0.11)
    bx = side.x1 + 8
    ty = side.y1 + 56
    o.append(callout(a, [(bx, a[1] + (bx - a[0])), (bx, ty - 4)], bx - 6, ty,
                     'Fin, foam board %s × %s mm per half, 2 per side' % (mm(fin_chord), mm(fin_half)), 'end'))

    # ---------------------------------------------------------------- notes under the iso inset
    nx, ny = iso_x, iso_y + iso_h + 22
    notes = ['Frame: x aft from the wing LE, y right, z up (cruise).',
             'Hover: nose up on the four feet; props cant 7° for yaw.',
             'Elevon panels at y %s–%s and %s–%s mm each side.'
             % (mm(elev_in[0]), mm(elev_in[1]), mm(elev_out[0]), mm(elev_out[1])),
             'Dashed: prop disc, hidden spar. Blue: dimension, mm.',
             'Geometry: Fusion build, revision %s.' % rev]
    for i, ln in enumerate(notes):
        o.append(text(nx, ny + i * 15, ln, 'ga-note'))

    # ---------------------------------------------------------------- title block with the scale bar
    x, y = GUTTER, TB_Y
    w = SHEET_W - 2 * GUTTER
    o.append('<rect class="ga-tb" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>' % (x, y, w, TB_H))
    cells = [('', None, 290), ('K09-L', 'General arrangement · three views, one scale', 330),
             ('REV', rev, 90), ('SCALE', 'bar · %d px/m' % SCALE, 120), ('UNITS', 'mm', 64),
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
        elif lab == 'K09-L':
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
            'aria-label="K09-L general arrangement: top, front and side views at one scale with an iso inset, dimensions in mm">'
            % (SHEET_W, SHEET_H))
    bg = '<rect width="%d" height="%d" fill="#FFFFFF"/>' % (SHEET_W, SHEET_H) if standalone else ''
    return head + '\n' + style + '\n' + defs + '\n' + bg + '\n'.join(o) + '\n</svg>'


def webp():
    """PNG renders -> WebP (quality 88, alpha kept): 3.8 MB -> 0.25 MB for the four views. PNGs are not kept."""
    try:
        from PIL import Image
    except ImportError:
        return
    for m in V['views'].values():
        png = os.path.join(ASSETS, m['file'])
        if m['file'].endswith('.png') and os.path.exists(png):
            Image.open(png).save(png[:-4] + '.webp', 'WEBP', quality=88, method=6)
            os.remove(png)
        m['file'] = m['file'].replace('.png', '.webp')
    json.dump(V, open(os.path.join(ASSETS, 'views.json'), 'w', encoding='utf-8'), indent=1)


def main():
    webp()
    svg = build('', 'ga0', standalone=True)
    with open(os.path.join(ASSETS, 'sheet.svg'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg + '\n')
    app = os.path.join(SITE, 'app.html')
    html = open(app, encoding='utf-8').read()
    n = 0
    for key in ('cfg', 'a1'):
        pat = re.compile(r'(<!-- GA-SHEET:%s -->)(.*?)(<!-- /GA-SHEET -->)' % key, re.S)
        html, c = pat.subn(lambda m: m.group(1) + '\n' + build('assets/drawing/', 'ga-' + key) + '\n' + m.group(3), html)
        n += c
    with open(app, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print('sheet %d x %d px; app.html blocks replaced: %d' % (SHEET_W, SHEET_H, n))


if __name__ == '__main__':
    main()
