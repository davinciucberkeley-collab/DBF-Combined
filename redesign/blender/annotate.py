"""annotate.py - the 2-D annotation pass: render (JPEG/PNG) + JSON sidecar -> one self-contained SVG figure with
callout labels on leader lines and a caption band. Python 3 standard library only (also runs inside Blender).

    python -I redesign/blender/annotate.py FIGURE.json [...]     # writes FIGURE.svg next to it
    python -I redesign/blender/annotate.py --png FIGURE.json      # also FIGURE.annotated.png (needs Edge or Chrome,
                                                                   # used headless only to rasterise the SVG; optional)
Layout rules (design system: IBM Plex, ink text, orange = the part you act on):
  - labels sit in two columns in the image margins (render_kit leaves 22 % each side free when there are callouts);
    a label goes to the side of the subject its anchor is on, sides are balanced, labels keep their anchors' top-to-
    bottom order so leaders do not cross, and never overlap.
  - label = id (mono) / what (sans) / detail (muted: tool, torque, bend radius). Orange dot = added in this step.
  - a hollow dot and a dashed leader mean the anchor is hidden behind another part (fastener underneath).
  - caption band under the picture: title, check line, and a key for the roles actually shown.
"""
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap

INK, FG2, FG3, LINE, LINE2, PAPER = '#121619', '#4B5563', '#6B7280', '#E3E7ED', '#CBD2DB', '#FFFFFF'
HI, HI_STRONG, HI_WASH = '#C2540A', '#E0661A', '#FBE9DC'
SANS = "IBM Plex Sans, Segoe UI, Helvetica, Arial, sans-serif"
MONO = "IBM Plex Mono, Consolas, SF Mono, Menlo, monospace"
FS_ID, FS_TXT, FS_DET = 17, 20, 16          # px at a 1600 px wide render (figures are shown at ~50-100 %)
PAD, GAP, EDGE, BOX_MAX = 10, 10, 22, 340


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", '&#39;')


def text_w(s, size, mono=False):
    """Rough rendered width (px) of s: average glyph advance 0.6 em (mono) / 0.53 em (sans)."""
    return len(s) * size * (0.6 if mono else 0.53)


UNIT = re.compile(r'(\d) (mm|cm|m|N m|g|kg|AWG|deg|V|A|W|s|min)\b')
NBSP = '\u00a0'


def wrap(s, size, width):
    """Wrap to the box width; a number and its unit never split across lines."""
    if not s:
        return []
    s = UNIT.sub(lambda m: m.group(1) + NBSP + m.group(2).replace(' ', NBSP), s)
    n = max(8, int(width / (size * 0.53)))
    return textwrap.wrap(s, n, break_on_hyphens=False) or ['']


def label_lines(c):
    """[(text, size, mono, colour, weight)] for one callout."""
    inner = BOX_MAX - 2 * PAD - 6
    out = []
    if c.get('title'):
        out.append((c['title'], FS_ID, True, HI if c['role'] == 'focus' else FG2, 600))
    for l in wrap(c.get('text', ''), FS_TXT, inner):
        out.append((l, FS_TXT, False, INK, 500))
    for l in wrap(c.get('detail') or '', FS_DET, inner):
        out.append((l, FS_DET, False, FG2, 400))
    if c.get('occluded'):
        out.append(('(behind other parts in this view)', FS_DET - 1, False, FG3, 400))
    return out


def layout(callouts, W, H, subject):
    """Assign side and box position to each callout; returns list of dicts with box geometry."""
    cx = (subject[0] + subject[2]) / 2 if subject else W / 2
    items = []
    for c in callouts:
        lines = label_lines(c)
        w = min(BOX_MAX, max(text_w(t, s, m) for t, s, m, _, _ in lines) + 2 * PAD + 6)
        h = sum(s * 1.32 for _, s, _, _, _ in lines) + 2 * PAD - 4
        items.append(dict(c, lines=lines, w=w, h=h, side='L' if c['x'] < cx else 'R'))
    for _ in range(len(items)):                       # balance the columns: move the most central label across
        nl = sum(1 for i in items if i['side'] == 'L')
        nr = len(items) - nl
        if abs(nl - nr) <= 1:
            break
        heavy = 'L' if nl > nr else 'R'
        cand = [i for i in items if i['side'] == heavy]
        mv = max(cand, key=lambda i: i['x']) if heavy == 'L' else min(cand, key=lambda i: i['x'])
        mv['side'] = 'R' if heavy == 'L' else 'L'
    for side in 'LR':
        col = sorted([i for i in items if i['side'] == side], key=lambda i: i['y'])
        top, bot = 16, H - 16
        for i in col:                                 # want the box centred on its anchor
            i['by'] = i['y'] - i['h'] / 2
        for a, b in zip(col, col[1:]):                # push down to remove overlaps
            b['by'] = max(b['by'], a['by'] + a['h'] + GAP)
        if col:                                       # then pull up from the bottom edge
            col[-1]['by'] = min(col[-1]['by'], bot - col[-1]['h'])
            for a, b in reversed(list(zip(col, col[1:]))):
                a['by'] = min(a['by'], b['by'] - a['h'] - GAP)
            col[0]['by'] = max(col[0]['by'], top)
            for a, b in zip(col, col[1:]):
                b['by'] = max(b['by'], a['by'] + a['h'] + GAP)
        for i in col:
            i['bx'] = EDGE if side == 'L' else W - EDGE - i['w']
    return items


def svg_callout(i):
    p = []
    focus = i['role'] == 'focus'
    inner_x = i['bx'] + i['w'] if i['side'] == 'L' else i['bx']
    ly = i['by'] + min(i['h'] / 2, 22)
    knee = inner_x + (16 if i['side'] == 'L' else -16)
    dash = " stroke-dasharray='6 4'" if i.get('occluded') else ''
    pts = '%.1f,%.1f %.1f,%.1f %.1f,%.1f' % (inner_x, ly, knee, ly, i['x'], i['y'])
    p.append("<polyline points='%s' fill='none' stroke='%s' stroke-width='5' stroke-linejoin='round' opacity='0.9'/>" % (pts, PAPER))
    p.append("<polyline points='%s' fill='none' stroke='%s' stroke-width='1.6' stroke-linejoin='round'%s/>" % (pts, INK if focus else FG2, dash))
    fill = PAPER if i.get('occluded') else (HI if focus else INK)
    p.append("<circle cx='%.1f' cy='%.1f' r='5.5' fill='%s' stroke='%s' stroke-width='2.2'/>" % (
        i['x'], i['y'], fill, HI if (focus and i.get('occluded')) else (INK if i.get('occluded') else PAPER)))
    p.append("<rect x='%.1f' y='%.1f' width='%.1f' height='%.1f' rx='6' fill='%s' fill-opacity='0.96' stroke='%s' stroke-width='1.2'/>"
             % (i['bx'], i['by'], i['w'], i['h'], PAPER, HI if focus else LINE2))
    if focus:
        p.append("<rect x='%.1f' y='%.1f' width='4' height='%.1f' rx='2' fill='%s'/>" % (i['bx'] + 3, i['by'] + 5, i['h'] - 10, HI))
    y = i['by'] + PAD - 3
    for t, s, mono, col, wt in i['lines']:
        y += s * 1.32
        p.append("<text x='%.1f' y='%.1f' font-family='%s' font-size='%d' font-weight='%d' fill='%s'>%s</text>"
                 % (i['bx'] + PAD + 6, y - s * 0.3, MONO if mono else SANS, s, wt, col, esc(t)))
    return ''.join(p)


KEY = {'focus': ('added in this step', HI, HI), 'context': ('already fitted', '#8A9099', '#8A9099'),
       'ghost': ('shown for context', '#E7ECF2', '#9AA4B1')}


def band(meta, W, y0):
    cap = meta.get('caption') or {}
    title, sub = cap.get('title', ''), cap.get('sub', '')
    keys = [k for k in ('focus', 'context', 'ghost') if k in meta.get('legend', [])]
    if 'focus' not in keys:
        keys = []                                     # a key is only useful when something is highlighted
    keyw = 230 if keys else 0
    tl = wrap(title, 26, W - 2 * 28 - keyw)[:2]
    sl = wrap(sub, 19, W - 2 * 28 - keyw)[:3]
    h = 24 + 36 * len(tl) + 28 * len(sl) + 18 if (tl or sl) else (24 + 30 * len(keys) if keys else 0)
    h = max(h, 24 + 30 * len(keys) + 6 if keys else 0)
    if h == 0:
        return '', 0
    p = ["<rect x='0' y='%d' width='%d' height='%d' fill='%s'/>" % (y0, W, h, PAPER),
         "<line x1='0' x2='%d' y1='%d' y2='%d' stroke='%s' stroke-width='2'/>" % (W, y0, y0, LINE)]
    y = y0 + 16
    for t in tl:
        y += 36
        p.append("<text x='28' y='%d' font-family='%s' font-size='26' font-weight='600' fill='%s'>%s</text>" % (y - 6, SANS, INK, esc(t)))
    for t in sl:
        y += 28
        p.append("<text x='28' y='%d' font-family='%s' font-size='19' fill='%s'>%s</text>" % (y - 4, SANS, FG2, esc(t)))
    ky = y0 + 22
    for k in keys:
        lab, fill, stroke = KEY[k]
        p.append("<rect x='%d' y='%d' width='18' height='18' rx='3' fill='%s' stroke='%s' stroke-width='1.5'/>"
                 % (W - keyw, ky, fill, stroke))
        p.append("<text x='%d' y='%d' font-family='%s' font-size='17' fill='%s'>%s</text>" % (W - keyw + 28, ky + 15, SANS, FG2, lab))
        ky += 30
    return ''.join(p), h


def build(json_path, embed=True, png=False):
    with open(json_path, encoding='utf-8') as f:
        meta = json.load(f)
    d = os.path.dirname(os.path.abspath(json_path))
    # lay out on a fixed 1600 px wide canvas whatever the render size, so drafts (--percent 50) look the same
    k = 1600.0 / meta['size'][0]
    W, H = 1600, int(round(meta['size'][1] * k))
    cal = [dict(c, x=c['x'] * k, y=c['y'] * k) for c in meta.get('callouts', [])]
    subj = [v * k for v in meta['subject_px']] if meta.get('subject_px') else None
    img = meta['files'].get('jpg') if embed else meta['files']['png']
    if embed and img and os.path.exists(os.path.join(d, img)):
        with open(os.path.join(d, img), 'rb') as f:
            href = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()
    else:
        href = meta['files']['png']
    items = layout(cal, W, H, subj)
    bandsvg, bh = band(meta, W, H)
    title = (meta.get('caption') or {}).get('title') or meta['id']
    p = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 %d %d' width='%d' height='%d' role='img'>" % (W, H + bh, W, H + bh),
         '<title>%s</title>' % esc(title),
         "<image href='%s' x='0' y='0' width='%d' height='%d'/>" % (href, W, H)]
    p += [svg_callout(i) for i in items]
    p.append(bandsvg)
    p.append('</svg>\n')
    out = os.path.splitext(os.path.abspath(json_path))[0] + '.svg'
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(''.join(p))
    print('annotated %s (%d callouts, %.0f kB)' % (os.path.basename(out), len(items), os.path.getsize(out) / 1024))
    if png:
        rasterize(out, os.path.splitext(out)[0] + '.annotated.png', W, H + bh)
    return out


def browser():
    """Edge or Chrome executable for headless rasterising (optional)."""
    cands = [shutil.which(n) for n in ('msedge', 'chrome', 'google-chrome', 'chromium', 'chromium-browser')]
    cands += [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
              r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
              r'C:\Program Files\Google\Chrome\Application\chrome.exe',
              '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    return next((c for c in cands if c and os.path.exists(c)), None)


def rasterize(svg, png, w, h):
    exe = browser()
    if not exe:
        print('  (no Edge/Chrome found: SVG only)')
        return None
    url = 'file:///' + os.path.abspath(svg).replace('\\', '/')
    subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                    '--window-size=%d,%d' % (w, h), '--screenshot=%s' % os.path.abspath(png), url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    if os.path.exists(png):
        print('  rasterised %s' % os.path.basename(png))
        return png
    return None


if __name__ == '__main__':
    args = sys.argv[1:]
    want_png = '--png' in args
    files = [a for a in args if not a.startswith('--')]
    if not files:
        print(__doc__)
        sys.exit(2)
    for jp in files:
        build(jp, png=want_png)
