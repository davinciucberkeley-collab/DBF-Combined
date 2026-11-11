"""dxf.py - minimal DXF R12 (AC1009) writer/reader for laser and knife files, plus a deterministic shelf nester.

R12 is the most widely read DXF (LightBurn, Inkscape, Illustrator, CorelDRAW, the Universal driver via any of
those). Every outline is a closed POLYLINE (flag 70 = 1), units mm ($INSUNITS 4). Layers:
    CUT     red    (colour 1)  through-cuts: closed outlines and holes
    MARK    blue   (colour 5)  engrave / pen lines (centre lines, stations, the true section on templates)
    NOTES   white  (colour 7)  text and sheet frame: do NOT cut (switch the layer off or set it to "no output")
"""
import math

LAYERS = (('CUT', 1), ('MARK', 5), ('NOTES', 7))


class Drawing:
    def __init__(self):
        self.ents = []

    def poly(self, pts, layer='CUT', closed=True):
        pts = [(float(x), float(y)) for x, y in pts]
        if closed and len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-9:
            pts = pts[:-1]
        self.ents.append(('POLY', layer, closed, pts))

    def text(self, x, y, h, s, layer='NOTES'):
        s = ''.join(ch if 32 <= ord(ch) < 127 else '?' for ch in str(s))
        self.ents.append(('TEXT', layer, float(x), float(y), float(h), s))

    def write(self, path):
        L = []
        a = lambda *kv: L.extend(str(v) for v in kv)
        a(0, 'SECTION', 2, 'HEADER', 9, '$ACADVER', 1, 'AC1009', 9, '$INSUNITS', 70, 4, 9, '$MEASUREMENT', 70, 1)
        xs = [p[0] for e in self.ents if e[0] == 'POLY' for p in e[3]] or [0.0]
        ys = [p[1] for e in self.ents if e[0] == 'POLY' for p in e[3]] or [0.0]
        a(9, '$EXTMIN', 10, _f(min(xs)), 20, _f(min(ys)), 30, '0.0', 9, '$EXTMAX', 10, _f(max(xs)), 20, _f(max(ys)),
          30, '0.0', 0, 'ENDSEC')
        a(0, 'SECTION', 2, 'TABLES')
        a(0, 'TABLE', 2, 'LTYPE', 70, 1, 0, 'LTYPE', 2, 'CONTINUOUS', 70, 0, 3, 'Solid line', 72, 65, 73, 0, 40, '0.0',
          0, 'ENDTAB')
        a(0, 'TABLE', 2, 'LAYER', 70, len(LAYERS))
        for name, col in LAYERS:
            a(0, 'LAYER', 2, name, 70, 0, 62, col, 6, 'CONTINUOUS')
        a(0, 'ENDTAB', 0, 'ENDSEC')
        a(0, 'SECTION', 2, 'ENTITIES')
        for e in self.ents:
            if e[0] == 'POLY':
                _k, layer, closed, pts = e
                a(0, 'POLYLINE', 8, layer, 66, 1, 10, '0.0', 20, '0.0', 30, '0.0', 70, 1 if closed else 0)
                for x, y in pts:
                    a(0, 'VERTEX', 8, layer, 10, _f(x), 20, _f(y), 30, '0.0')
                a(0, 'SEQEND', 8, layer)
            else:
                _k, layer, x, y, h, s = e
                a(0, 'TEXT', 8, layer, 10, _f(x), 20, _f(y), 30, '0.0', 40, _f(h), 1, s)
        a(0, 'ENDSEC', 0, 'EOF')
        with open(path, 'w', encoding='ascii', newline='\r\n') as f:
            f.write('\n'.join(L) + '\n')


def _f(v):
    return '%.4f' % v


def read(path):
    """-> list of (layer, closed, pts) polylines and (layer, text) texts. Enough to check our own files."""
    with open(path, encoding='ascii') as f:
        tok = [l.strip() for l in f.read().splitlines()]
    pairs = list(zip(tok[0::2], tok[1::2]))
    polys, texts, i = [], [], 0
    while i < len(pairs):
        c, v = pairs[i]
        if c == '0' and v == 'POLYLINE':
            layer, closed, pts = '', False, []
            i += 1
            while pairs[i][0] != '0':
                if pairs[i][0] == '8':
                    layer = pairs[i][1]
                if pairs[i][0] == '70':
                    closed = int(pairs[i][1]) & 1 == 1
                i += 1
            while pairs[i] == ('0', 'VERTEX'):
                i += 1
                x = y = None
                while pairs[i][0] != '0':
                    if pairs[i][0] == '10':
                        x = float(pairs[i][1])
                    if pairs[i][0] == '20':
                        y = float(pairs[i][1])
                    i += 1
                pts.append((x, y))
            polys.append((layer, closed, pts))
            continue
        if c == '0' and v == 'TEXT':
            layer, s = '', ''
            i += 1
            while pairs[i][0] != '0':
                if pairs[i][0] == '8':
                    layer = pairs[i][1]
                if pairs[i][0] == '1':
                    s = pairs[i][1]
                i += 1
            texts.append((layer, s))
            continue
        i += 1
    return polys, texts


# ----------------------------------------------------------------------------- geometry helpers
def bbox(loops):
    xs = [p[0] for l in loops for p in l]
    ys = [p[1] for l in loops for p in l]
    return min(xs), min(ys), max(xs), max(ys)


def transform(loops, rot90=False, dx=0.0, dy=0.0, flip=False):
    """Rotate 90 deg (optional), mirror x (optional), then move so the bbox min sits at (dx, dy)."""
    out = []
    for l in loops:
        q = [(-y, x) if rot90 else (x, y) for x, y in l]
        q = [(-x, y) if flip else (x, y) for x, y in q]
        out.append(q)
    x0, y0, _x1, _y1 = bbox(out)
    return [[(x - x0 + dx, y - y0 + dy) for x, y in l] for l in out]


def area(loop):
    return abs(sum(loop[i][0] * loop[i - 1][1] - loop[i - 1][0] * loop[i][1] for i in range(len(loop)))) / 2


def point_in(pt, loop):
    x, y = pt
    inside = False
    for i in range(len(loop)):
        (x1, y1), (x2, y2) = loop[i - 1], loop[i]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    L = ax * ax + ay * ay
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L))
    return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)


def edge_dist(p, loops):
    return min(seg_dist(p, l[i - 1], l[i]) for l in loops for i in range(len(l)))


def circle(cx, cy, r, n=36):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


# ----------------------------------------------------------------------------- nesting
def nest(items, sheet_w, sheet_h, margin, gap):
    """Deterministic shelf nesting on bounding boxes. items: [(key, w, h)] (mm). Each item may turn 90 deg.
    Returns [(sheet index, key, x, y, rotated)] and a list of keys that fit on no sheet."""
    order = sorted(items, key=lambda it: (-max(it[1], it[2]), -min(it[1], it[2]), it[0]))
    W, H = sheet_w - 2 * margin, sheet_h - 2 * margin
    sheets = []                      # each: list of shelves [y, height, x_used]
    placed, misfit = [], []
    for key, w, h in order:
        opts = [o for o in ((w, h, False), (h, w, True)) if o[0] <= W + 1e-6 and o[1] <= H + 1e-6]
        if not opts:
            misfit.append(key)
            continue
        opts.sort(key=lambda o: (o[1], o[0]))          # prefer the low orientation (long side along the shelf)
        done = False
        for si, shelves in enumerate(sheets):
            for sh in shelves:
                for ww, hh, rot in opts:
                    if hh <= sh[1] + 1e-6 and sh[2] + ww <= W + 1e-6:
                        placed.append((si, key, margin + sh[2], margin + sh[0], rot))
                        sh[2] += ww + gap
                        done = True
                        break
                if done:
                    break
            if done:
                break
            top = (shelves[-1][0] + shelves[-1][1] + gap) if shelves else 0.0
            for ww, hh, rot in opts:
                if top + hh <= H + 1e-6:
                    shelves.append([top, hh, ww + gap])
                    placed.append((si, key, margin, margin + top, rot))
                    done = True
                    break
            if done:
                break
        if not done:
            ww, hh, rot = opts[0]
            sheets.append([[0.0, hh, ww + gap]])
            placed.append((len(sheets) - 1, key, margin, margin, rot))
    return placed, misfit, len(sheets)
