"""Draw the morphological-chart option sketches (one SVG <symbol> per option code) and splice them into app.html.

    python -I redesign/site/make_morph_sketches.py          # rewrites the block between the morph-sketches markers
    python -I redesign/site/make_morph_sketches.py --sheet out.html   # also writes a contact sheet to look at them

Style (redesign/design-system/diagram-style.md): 120 x 80 box, 2 px ink (currentColor), 1.5 px for secondary lines,
bodies filled with 10 % ink so overlaps read, dashed = a ghost pose or an absent part, orange (--highlight) = the
thing that moves or pushes (arrows, tilt arcs, the added part). Nothing else is coloured, so the sketches follow the
theme. Orientation: top view, nose up, unless the option is about motion or the ground, which is drawn from the side
or the front. Source of the option names and codes: redesign/config-study/concepts/MORPH.md section 1.
"""
import math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HI = 'style="stroke:var(--highlight)"'
HIF = 'style="fill:var(--highlight);stroke:none"'
GH = 'stroke-dasharray="3 3" stroke-opacity=".6"'      # ghost pose / absent part
F = 'fill="currentColor" fill-opacity=".10"'


def f(v):
    return ('%.1f' % v).rstrip('0').rstrip('.')


def rect(x, y, w, h, rx=2, extra='', fill=True, rot=None):
    t = ' transform="rotate(%s %s %s)"' % (f(rot[0]), f(rot[1]), f(rot[2])) if rot else ''
    return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" %s %s%s/>' % (f(x), f(y), f(w), f(h), rx, F if fill else '', extra, t)


def line(x1, y1, x2, y2, extra='', w=None):
    sw = ' stroke-width="%s"' % w if w else ''
    return '<path d="M%s %sL%s %s"%s %s/>' % (f(x1), f(y1), f(x2), f(y2), sw, extra)


def poly(pts, extra='', fill=True):
    return '<path d="M%sZ" %s %s/>' % ('L'.join('%s %s' % (f(a), f(b)) for a, b in pts), F if fill else '', extra)


def rotor(cx, cy, r=9, ring=False):
    s = '<circle cx="%s" cy="%s" r="%s" %s stroke-width="1.5"/>' % (f(cx), f(cy), f(r), F)
    s += line(cx - .8 * r, cy + .45 * r, cx + .8 * r, cy - .45 * r, w=1.5)
    if ring:
        s += '<circle cx="%s" cy="%s" r="%s" stroke-width="1.25"/>' % (f(cx), f(cy), f(r * .55))
    s += '<circle cx="%s" cy="%s" r="1.7" fill="currentColor" stroke="none"/>' % (f(cx), f(cy))
    return s


def disc(cx, cy, hw=10, extra=''):
    """a rotor seen edge-on: a thick bar"""
    return line(cx - hw, cy, cx + hw, cy, extra=extra, w=3.5)


def arrow(x1, y1, x2, y2, hl=5.5, w=2):
    a = math.atan2(y2 - y1, x2 - x1)
    s = '<path d="M%s %sL%s %s" %s stroke-width="%s"/>' % (f(x1), f(y1), f(x2), f(y2), HI, w)
    p = ''.join('L%s %s' % (f(x2 - hl * math.cos(a + d)), f(y2 - hl * math.sin(a + d))) for d in (0.5, -0.5))
    p = 'M%s %s' % (f(x2), f(y2)) + 'L%s %s' % (f(x2 - hl * math.cos(a + .5)), f(y2 - hl * math.sin(a + .5)))
    p += 'M%s %sL%s %s' % (f(x2), f(y2), f(x2 - hl * math.cos(a - .5)), f(y2 - hl * math.sin(a - .5)))
    return s + '<path d="%s" %s stroke-width="%s"/>' % (p, HI, w)


def arc(cx, cy, r, a0, a1, hl=5.5, w=2):
    """curved arrow, angles in degrees, screen coordinates (0 = right, 90 = down), a1 > a0 clockwise"""
    p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    sweep = 1 if a1 > a0 else 0
    big = 1 if abs(a1 - a0) > 180 else 0
    s = '<path d="M%s %sA%s %s 0 %d %d %s %s" %s stroke-width="%s" fill="none"/>' % (f(p0[0]), f(p0[1]), f(r), f(r), big, sweep, f(p1[0]), f(p1[1]), HI, w)
    sg = 1 if sweep else -1
    ta = math.atan2(math.cos(math.radians(a1)) * sg, -math.sin(math.radians(a1)) * sg)
    h = 'M%s %sL%s %sM%s %sL%s %s' % (f(p1[0]), f(p1[1]), f(p1[0] - hl * math.cos(ta + .5)), f(p1[1] - hl * math.sin(ta + .5)),
                                       f(p1[0]), f(p1[1]), f(p1[0] - hl * math.cos(ta - .5)), f(p1[1] - hl * math.sin(ta - .5)))
    return s + '<path d="%s" %s stroke-width="%s"/>' % (h, HI, w)


def ground(y=70, x0=10, x1=110):
    return line(x0, y, x1, y, w=1.5) + ''.join(line(x, y, x - 5, y + 5, w=1.25) for x in range(x0 + 10, x1 + 1, 12))


def pod(cx=60, y0=10, y1=70, w=8):
    return rect(cx - w / 2, y0, w, y1 - y0, rx=w / 2)


def wing(cx=60, y=34, span=92, ch=12):
    return rect(cx - span / 2, y, span, ch, rx=2)


def plane(extra_wing=None, tail=True):
    s = wing(60, 32, 92, 12) + pod(60, 10, 70)
    if tail:
        s += rect(46, 62, 28, 6, rx=1.5)
    return s


def battery(x, y, w, h, cells, term=True):
    s = rect(x, y, w, h, rx=3)
    cw = w / cells
    s += ''.join(line(x + cw * i, y + 2, x + cw * i, y + h - 2, w=1.25) for i in range(1, cells))
    if term:
        s += '<path d="M%s %sh4v%sh-4"/>' % (f(x + w), f(y + h / 2 - 4), 8)
    return s


def sec(cx, cy, c=70, t=16):
    """closed airfoil section, leading edge left"""
    x0, x1 = cx - c / 2, cx + c / 2
    return ('<path d="M%s %sC%s %s %s %s %s %sC%s %s %s %s %s %sC%s %s %s %s %s %sZ" %s/>' % (
        f(x0), f(cy), f(x0), f(cy - t * .55), f(x0 + c * .15), f(cy - t * .5), f(x0 + c * .35), f(cy - t * .5),
        f(x0 + c * .6), f(cy - t * .5), f(x1 - c * .15), f(cy - t * .1), f(x1), f(cy),
        f(x1 - c * .2), f(cy + t * .15), f(x0 + c * .5), f(cy + t * .3), f(x0 + c * .3), f(cy + t * .3), F))


G = {}
SIX = ((24, 16), (96, 16), (24, 64), (96, 64))


def frame(pts, hub=(60, 40)):
    return ''.join(line(hub[0], hub[1], x, y, w=2.5) for x, y in pts)


def copter(by, mast=12):
    """side view of a multirotor: body, two masts, two edge-on rotors"""
    return (rect(36, by, 48, 8, rx=4) + line(44, by, 44, by - mast, w=1.5) + line(76, by, 76, by - mast, w=1.5)
            + line(32, by - mast, 56, by - mast, w=3.5) + line(64, by - mast, 88, by - mast, w=3.5))


# ---------------------------------------------------------------- D1 VTOL lift (how it hovers)
G['L1'] = plane() + ''.join(rotor(x, y, 8) for x, y in ((24, 14), (96, 14), (24, 62), (96, 62))) + line(24, 14, 24, 62, w=2.5) + line(96, 14, 96, 62, w=2.5)
G['L2'] = (rect(14, 46, 72, 10, rx=5) + line(64, 46, 64, 40, w=2) + line(64, 40, 64, 18, w=1.5) + line(52, 18, 76, 18, w=3.5)
           + line(64, 40, 88, 40, extra=GH, w=1.5) + line(88, 31, 88, 49, extra=GH, w=3.5) + arc(64, 40, 28, -75, -12))
G['L3'] = (rect(22, 26, 8, 42, rx=4) + line(12, 26, 40, 26, w=3.5) + arrow(26, 20, 26, 8)
           + rect(64, 36, 44, 8, rx=4, extra=GH) + line(64, 30, 64, 50, extra=GH, w=3.5) + arc(44, 62, 34, -80, -20))
G['L4'] = (rect(14, 50, 76, 7, rx=3) + line(14, 41, 14, 59, w=3.5)
           + rect(38, 12, 7, 44, rx=3, extra=GH) + line(32, 12, 52, 12, extra=GH, w=3.5) + arc(41, 53, 36, -5, -80))
G['L5'] = frame(SIX) + rect(50, 31, 20, 18, rx=4) + ''.join(rotor(x, y, 11) for x, y in SIX)
G['L6'] = rect(24, 30, 9, 46, rx=4, rot=(45, 28, 53)) + line(50, 18, 70, 38, w=3.5) + arrow(56, 24, 46, 12) + arrow(44, 56, 28, 56, hl=4.5, w=1.75)
G['L7'] = rect(8, 26, 104, 28, rx=3) + ''.join('<circle cx="%d" cy="40" r="12" stroke-width="1.5"/>' % x + rotor(x, 40, 8) for x in (32, 88)) + pod(60, 14, 66, 7)
G['L8'] = (rect(52, 44, 16, 16, rx=6) + rect(8, 54, 44, 6, rx=3) + rect(68, 54, 44, 6, rx=3, extra=GH) + rect(68, 54, 34, 6, rx=3, rot=(-68, 68, 57)) + line(34, 54, 34, 36, w=1.5) + line(24, 36, 44, 36, w=3.5) + line(86, 54, 86, 36, extra=GH, w=1.5) + line(76, 36, 96, 36, extra=GH, w=3.5) + arc(68, 57, 40, -12, -50))
# ---------------------------------------------------------------- D2 Cruise thrust
G['T1'] = plane() + disc(60, 74, 8) + arrow(92, 26, 92, 6)
G['T2'] = wing(60, 38, 92, 12) + rect(56, 18, 8, 54, rx=4) + rect(46, 64, 28, 6, rx=1.5) + disc(60, 14, 11) + arrow(92, 26, 92, 6)
G['T3'] = (poly([(60, 26), (112, 58), (112, 70), (8, 70), (8, 58)]) + ''.join(disc(x, 62, 8) for x in (24, 44, 76, 96))
           + ''.join(arrow(x, 52, x, 36, hl=4.5, w=1.75) for x in (24, 44, 76, 96)))
G['T4'] = plane() + line(12, 40, 12, 20, w=3.5) + line(108, 40, 108, 20, w=3.5) + arrow(12, 14, 12, 3) + arrow(108, 14, 108, 3)
G['T5'] = (rect(56, 22, 8, 48, rx=4) + wing(60, 36, 92, 12) + line(18, 20, 18, 46, w=3.5) + line(102, 20, 102, 46, w=3.5)
           + arrow(18, 15, 18, 3) + arrow(102, 15, 102, 3) + '<circle cx="60" cy="76" r="3.5" %s/>' % GH)

# ---------------------------------------------------------------- D3 Transition (how it changes mode)
G['X1'] = (line(14, 68, 108, 68, w=1.5) + line(14, 68, 14, 12, w=1.5) + '<path d="M14 18C44 20 66 44 106 64" %s stroke-width="2.5" fill="none"/>' % HI
           + '<path d="M14 64C44 60 66 36 106 18" stroke-width="2.5" fill="none"/>')
G['X2'] = ('<circle cx="40" cy="58" r="5" fill="currentColor"/>' + line(40, 58, 40, 16, w=1.5) + line(30, 16, 50, 16, w=3.5)
           + line(40, 58, 76, 58, extra=GH, w=1.5) + line(76, 48, 76, 68, extra=GH, w=3.5) + line(40, 58, 66, 32, extra=GH, w=1.5)
           + arc(40, 58, 36, -88, -4))
G['X3'] = (rect(14, 8, 8, 44, rx=4) + rect(42, 19, 8, 42, rx=4, rot=(45, 46, 40), extra=GH) + rect(66, 48, 44, 8, rx=4, extra=GH) + arc(30, 62, 34, -105, -20))
G['X4'] = (rect(12, 56, 96, 10, rx=5) + line(60, 40, 60, 56, w=2) + '<circle cx="60" cy="40" r="4" fill="currentColor" style="stroke:none"/>'
           + line(28, 40, 92, 40, w=3.5) + line(60, 8, 60, 40, extra=GH, w=3.5) + arc(60, 40, 26, -2, -88))
G['X5'] = copter(40) + arrow(40, 66, 84, 66)
G['X6'] = copter(48) + arrow(60, 24, 60, 6, hl=5) + ground(66, 30, 90)
G['X7'] = (rect(52, 38, 16, 16, rx=6) + rect(8, 44, 44, 6, rx=3) + rect(68, 44, 44, 6, rx=3, extra=GH)
           + rect(68, 44, 34, 6, rx=3, rot=(-68, 68, 47)) + arc(68, 47, 40, -12, -50))

# ---------------------------------------------------------------- D4 Wing / body (planform)
G['W1'] = plane()
G['W2'] = poly([(60, 10), (112, 62), (112, 68), (8, 68), (8, 62)]) + line(60, 22, 60, 68, w=1.25)
G['W3'] = rect(14, 20, 92, 6, rx=2) + rect(24, 54, 72, 6, rx=2) + line(38, 26, 38, 54, w=1.5) + line(82, 26, 82, 54, w=1.5) + rect(52, 32, 16, 16, rx=6)
G['W4'] = pod(60, 8, 72, 8) + rect(30, 16, 60, 8, rx=2) + rect(10, 50, 100, 10, rx=2)
G['W5'] = poly([(60, 14), (106, 34), (60, 66), (14, 34)]) + pod(60, 10, 70, 7)
G['W6'] = '<circle cx="60" cy="40" r="32" %s/><circle cx="60" cy="40" r="22"/>' % F + pod(60, 30, 50, 6)
G['W7'] = frame(SIX) + rect(50, 31, 20, 18, rx=4) + ''.join('<circle cx="%d" cy="%d" r="3.5" fill="currentColor"/>' % p for p in SIX)
G['W8'] = pod(60, 8, 72, 8) + rect(10, 34, 100, 12, rx=2, rot=(-14, 60, 40)) + rect(10, 34, 100, 12, rx=2, extra=GH, fill=False) + '<circle cx="60" cy="40" r="3" fill="currentColor" style="stroke:none"/>'

# ---------------------------------------------------------------- D5 Tail / control
G['C1'] = (wing(60, 22, 100, 12) + rect(30, 34, 4, 30, rx=2) + rect(86, 34, 4, 30, rx=2) + rect(24, 62, 72, 6, rx=1.5)
           + rect(10, 31, 26, 3.5, rx=1, extra=HI, fill=False) + rect(84, 31, 26, 3.5, rx=1, extra=HI, fill=False) + pod(60, 14, 48, 8))
G['C2'] = wing(60, 22, 96, 12) + pod(60, 12, 50, 8) + line(60, 50, 60, 66, w=2.5) + line(60, 66, 42, 76, extra=HI, w=2.5) + line(60, 66, 78, 76, extra=HI, w=2.5)
G['C3'] = poly([(60, 10), (112, 58), (112, 66), (8, 66), (8, 58)]) + line(10, 67, 52, 67, extra=HI, w=3.5) + line(68, 67, 110, 67, extra=HI, w=3.5)
G['C4'] = rect(10, 38, 100, 10, rx=2) + line(20, 26, 20, 62, w=3.5) + line(100, 26, 100, 62, w=3.5) + arrow(20, 22, 20, 4) + arrow(100, 22, 100, 12, hl=4.5)
G['C5'] = pod(60, 8, 72, 8) + rect(40, 14, 40, 5, rx=2, extra=HI) + wing(60, 44, 100, 12)
G['C6'] = (frame(SIX) + rect(50, 31, 20, 18, rx=4) + ''.join(rotor(x, y, 8) for x, y in SIX) + arc(60, 40, 14, 200, 330, hl=4.5) + arc(60, 40, 14, 20, 150, hl=4.5))

# ---------------------------------------------------------------- D6 Rotors (count and arrangement)
G['R1'] = plane() + ''.join(rotor(x, y, 8) for x, y in ((22, 16), (98, 16), (22, 56), (98, 56))) + disc(60, 76, 8, extra=HI)
G['R2'] = frame(SIX) + rect(52, 33, 16, 14, rx=3) + ''.join(rotor(x, y, 11, ring=True) for x, y in SIX)
G['R3'] = (frame(((26, 18), (94, 18), (60, 66))) + rect(52, 31, 16, 18, rx=4) + rotor(26, 18, 10) + rotor(94, 18, 10) + rotor(60, 66, 10)
           + arc(26, 18, 16, 190, 280, hl=4.5) + arc(94, 18, 16, 350, 260, hl=4.5))
G['R4'] = (frame(((26, 16), (94, 16), (26, 64), (94, 64))) + rect(52, 31, 16, 18, rx=4) + ''.join(rotor(x, y, 9) for x, y in ((26, 16), (94, 16), (26, 64), (94, 64)))
           + arc(26, 16, 15, 190, 280, hl=4.5) + arc(94, 16, 15, 350, 260, hl=4.5))
G['R5'] = rect(10, 36, 100, 8, rx=2) + rect(17, 14, 6, 52, rx=3) + rect(97, 14, 6, 52, rx=3) + ''.join(rotor(x, y, 8) for x, y in ((20, 12), (100, 12), (20, 68), (100, 68)))
G['R6'] = rect(8, 36, 104, 8, rx=2) + rotor(34, 40, 18) + rotor(86, 40, 18)
G['R7'] = frame(SIX) + rect(50, 31, 20, 18, rx=5) + '<circle cx="60" cy="40" r="3" fill="currentColor" style="stroke:none"/>' + ''.join(rotor(x, y, 11) for x, y in SIX)
G['R8'] = pod(60, 8, 72, 8) + rect(26, 16, 68, 7, rx=2) + rect(10, 56, 100, 7, rx=2) + ''.join(rotor(x, y, 7.5) for x, y in ((18, 19), (102, 19), (6, 59), (114, 59)))
G['R9'] = rotor(60, 40, 28) + '<circle cx="60" cy="40" r="6" %s/>' % F
G['R10'] = (pod(60, 8, 70, 8) + ''.join(line(x, y, 60, y, w=1.5) for x, y in ((24, 14), (24, 38), (24, 62), (96, 14), (96, 38), (96, 62)))
            + ''.join(rotor(x, y, 9) for x, y in ((24, 14), (96, 14), (24, 38), (96, 38), (24, 62), (96, 62))) + disc(60, 76, 7, extra=HI))
G['R11'] = (frame(((26, 16), (94, 16), (60, 54))) + rect(52, 28, 16, 18, rx=4) + rotor(26, 16, 9) + rotor(94, 16, 9) + rotor(60, 54, 9)
            + arc(60, 54, 16, 20, 160, hl=4.5) + disc(60, 76, 7, extra=HI))
G['R12'] = (frame(((60, 16), (24, 60), (96, 60))) + rect(52, 32, 16, 18, rx=4) + rotor(60, 16, 10) + rotor(24, 60, 10) + rotor(96, 60, 10)
            + arc(60, 16, 16, 200, 290, hl=4.5))
G['R13'] = (frame(((24, 22), (96, 22), (60, 64))) + line(24, 22, 96, 22, extra=HI, w=1.5) + rect(52, 30, 16, 18, rx=4)
            + rotor(24, 22, 10, ring=True) + rotor(96, 22, 10, ring=True) + rotor(60, 64, 10, ring=True))

# ---------------------------------------------------------------- D7 Landing (side / front view with a ground line)
G['G1'] = rect(22, 28, 76, 12, rx=6) + line(40, 40, 40, 56, w=2) + line(80, 40, 80, 56, w=2) + line(26, 58, 94, 58, w=3.5) + ground(66, 10, 110)
G['G2'] = rect(20, 14, 80, 8, rx=2) + line(32, 22, 32, 60, w=3) + line(88, 22, 88, 60, w=3) + line(28, 62, 36, 62, w=3) + line(84, 62, 92, 62, w=3) + ground(66, 10, 110)
G['G3'] = rect(22, 24, 76, 12, rx=6) + line(40, 36, 40, 50, w=2) + line(80, 36, 80, 50, w=2) + '<circle cx="40" cy="55" r="9" %s/><circle cx="80" cy="55" r="9" %s/>' % (F, F) + ground(64, 10, 110)
G['G4'] = rect(22, 24, 76, 24, rx=10) + rect(32, 48, 56, 8, rx=3, extra='stroke-width="2.5"') + ground(60, 10, 110)
G['G5'] = (rect(22, 20, 76, 12, rx=6) + '<path d="M34 32l-4 26h20l-4-26M70 32l-4 26h20l-4-26"/>'
           + '<path d="M32 40l12 4M33 48l14 4M68 40l14 4M69 48l14 4" stroke-width="1.25"/>' + ground(60, 10, 110))

# ---------------------------------------------------------------- D8 Transport
G['P1'] = rect(6, 30, 44, 11, rx=2) + rect(70, 30, 44, 11, rx=2) + line(34, 36, 86, 36, extra=HI, w=2.5) + arrow(53, 56, 60, 56, hl=4.5) + arrow(67, 56, 60, 56, hl=4.5)
G['P2'] = rect(8, 10, 104, 12, rx=2) + rect(52, 46, 16, 28, rx=7) + arrow(60, 42, 60, 26, hl=5)
G['P3'] = rect(8, 12, 104, 58, rx=4) + line(8, 24, 112, 24, w=1.5) + wing(60, 38, 76, 8) + pod(60, 28, 66, 6)
G['P4'] = (rect(50, 31, 20, 18, rx=4) + line(60, 40, 22, 14, w=2.5) + line(60, 40, 98, 14, w=2.5) + line(60, 40, 22, 66, extra=GH, w=2.5) + line(60, 40, 98, 66, extra=GH, w=2.5) + line(60, 40, 54, 74, w=2.5) + line(60, 40, 66, 74, w=2.5) + arc(60, 40, 44, 148, 108, hl=4.5) + arc(60, 40, 44, 32, 72, hl=4.5))
G['P5'] = line(8, 40, 112, 40, w=3.5) + rect(18, 30, 18, 20, rx=2) + rect(44, 30, 18, 20, rx=2) + rect(74, 30, 18, 20, rx=2, extra=GH) + arrow(100, 62, 84, 62, hl=4.5)
G['P6'] = rect(10, 24, 100, 46, rx=6) + '<path d="M44 24v-8h32v8"/>' + line(10, 42, 110, 42, w=1.5) + rect(54, 38, 12, 8, rx=1.5, extra='stroke-width="1.5"')

# ---------------------------------------------------------------- D9 Structure (material and process, sections or details)
G['M1'] = sec(60, 46, 90, 30) + '<circle cx="46" cy="44" r="4" %s/>' % HI + '<path d="M14 18L106 16" %s stroke-width="1.25"/>' % GH
G['M2'] = rect(14, 24, 92, 5, rx=1.5) + rect(14, 33, 92, 5, rx=1.5) + rect(14, 42, 92, 5, rx=1.5) + line(14, 58, 106, 58, extra=HI, w=4)
G['M3'] = sec(60, 46, 90, 36) + ''.join(line(x0, y, x1, y, w=1.25) for y, x0, x1 in ((36, 36, 86), (42, 26, 96), (48, 30, 92), (54, 42, 76))) + '<circle cx="42" cy="44" r="4" %s/>' % HI
G['M4'] = line(10, 40, 110, 40, w=3.5) + ''.join(rect(x, 24, 5, 32, rx=1) for x in (18, 34, 50, 66, 82, 98)) + '<path d="M10 24H110M10 56H110" %s stroke-width="1.5"/>' % GH
G['M5'] = (poly([(60, 6), (66, 20), (110, 40), (110, 48), (66, 46), (64, 64), (78, 70), (78, 74), (42, 74), (42, 70), (56, 64), (54, 46), (10, 48), (10, 40), (54, 20)])
           + '<circle cx="100" cy="14" r="7" %s/>' % HI + '<path d="M97 14l2 2 4-4" %s stroke-width="1.5" fill="none"/>' % HI)
G['M6'] = (line(24, 62, 96, 62, w=3) + line(24, 62, 60, 16, w=3) + line(96, 62, 60, 16, w=3) + line(60, 62, 60, 16, w=1.5)
           + ''.join('<circle cx="%d" cy="%d" r="5" %s/>' % (x, y, F) for x, y in ((24, 62), (96, 62), (60, 16), (60, 62))))
G['M7'] = (sec(60, 46, 94, 34) + '<path d="M14 46C14 28 38 26 60 28S100 36 106 46C100 56 80 56 60 58S14 62 14 46" stroke-width="1.25" fill="none"/>'
           + '<path d="M26 44l10-4M40 48l10-4M54 48l10-4M68 46l10-4" stroke-width="1.25"/>')

# ---------------------------------------------------------------- D10 Energy
G['E1'] = battery(26, 26, 68, 28, 4)
G['E2'] = battery(26, 26, 68, 28, 6)
G['E3'] = battery(14, 14, 80, 20, 4) + battery(14, 46, 80, 20, 4) + line(96, 24, 106, 24, extra=HI, w=2) + line(96, 56, 106, 56, extra=HI, w=2) + line(106, 24, 106, 56, extra=HI, w=2)
G['E4'] = ''.join('<rect x="%d" y="22" width="14" height="36" rx="5" %s/><path d="M%d 28h6" stroke-width="1.25"/>' % (x, F, x + 4) for x in (20, 40, 60, 80))
G['E5'] = battery(8, 24, 52, 32, 4, term=False) + ''.join('<rect x="%d" y="24" width="12" height="32" rx="4" %s/>' % (x, F) for x in (72, 90)) + line(60, 40, 72, 40, extra=HI, w=2.5)
G['E7'] = battery(8, 22, 48, 36, 4, term=False) + battery(64, 22, 48, 36, 4, term=False)
G['E8'] = battery(26, 26, 68, 28, 3)

# ---------------------------------------------------------------- D11 Buy vs build
G['B1'] = (rect(10, 12, 74, 58, rx=3) + rect(44, 26, 6, 36, rx=3, extra=GH, fill=False) + rect(22, 38, 50, 6, rx=2, extra=GH, fill=False)
           + line(94, 62, 108, 22, w=3) + '<path d="M94 62l-2 8 8-4z" fill="currentColor"/>')
G['B2'] = plane() + ''.join(rotor(x, 54, 8) + '<circle cx="%d" cy="54" r="12" %s fill="none" stroke-width="1.5"/>' % (x, HI) for x in (18, 102))
G['B3'] = rect(8, 12, 104, 58, rx=4) + line(8, 26, 112, 26, w=1.5) + wing(60, 40, 56, 8) + pod(60, 32, 64, 6) + ''.join(rotor(x, y, 5) for x, y in ((38, 36), (82, 36), (38, 56), (82, 56)))
G['B4'] = (frame(((24, 16), (96, 16), (24, 52), (96, 52)), hub=(60, 34)) + rect(52, 28, 16, 12, rx=3) + ''.join(rotor(x, y, 8) for x, y in ((24, 16), (96, 16), (24, 52), (96, 52)))
           + rect(14, 62, 92, 10, rx=2, extra=HI, fill=False) + line(60, 40, 60, 62, extra=HI, w=1.5))
G['B5'] = rect(6, 40, 40, 6, rx=2) + rect(23, 28, 6, 30, rx=3) + rect(18, 54, 16, 3, rx=1) + rect(54, 20, 58, 11, rx=2, extra=HI, fill=False) + line(46, 43, 54, 28, w=1.5, extra=GH)
G['B6'] = ('<path d="M12 10h30l10 10v46H12z" %s/><path d="M42 10v10h10"/>' % F + line(20, 32, 44, 32, w=1.5) + line(20, 42, 44, 42, w=1.5) + line(20, 52, 36, 52, w=1.5)
           + arrow(58, 40, 74, 40, hl=5) + rect(80, 54, 30, 6, rx=2) + rect(84, 46, 26, 6, rx=2) + rect(88, 38, 22, 6, rx=2) + line(80, 66, 110, 66, w=1.5))
G['B7'] = (rect(8, 12, 104, 58, rx=4) + line(8, 26, 112, 26, w=1.5) + wing(52, 40, 56, 8) + pod(52, 32, 64, 6)
           + '<circle cx="94" cy="50" r="10" %s fill="none"/>' % HI + line(94, 45, 94, 55, extra=HI, w=2) + line(89, 50, 99, 50, extra=HI, w=2))

# ---------------------------------------------------------------- output
ORDER = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'T1', 'T2', 'T3', 'T4', 'T5', 'X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7',
         'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6'] + ['R%d' % i for i in range(1, 14)] + \
        ['G1', 'G2', 'G3', 'G4', 'G5', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7',
         'E1', 'E2', 'E3', 'E4', 'E5', 'E7', 'E8', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']
ATTR = 'viewBox="0 0 120 80" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"'
BEGIN, END = '<!-- morph-sketches:begin', '<!-- morph-sketches:end -->'


def block():
    out = [BEGIN + ' (generated by make_morph_sketches.py; 120 x 80, 2 px currentColor, orange = what moves or pushes) -->']
    for k in ORDER:
        out.append('    <symbol id="sk-%s" %s>%s</symbol>' % (k, ATTR, G[k]))
    out.append('    ' + END)
    return '\n'.join(out)


if __name__ == '__main__':
    p = os.path.join(HERE, 'app.html')
    s = open(p, encoding='utf-8').read()
    b = block()
    if BEGIN in s:
        s = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END), lambda m: b.strip(), s, flags=re.S)
    else:  # first run: replace the old hand-drawn <symbol id="sk-..."> lines
        s, n = re.subn(r'(    <!-- morph sketches:[^\n]*-->\n)?(    <symbol id="sk-[A-Z]\d+".*?</symbol>\n)+', '    ' + b.strip() + '\n', s, count=1, flags=re.S)
        assert n == 1
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print('wrote %d sketches' % len(ORDER))
    if '--sheet' in sys.argv:
        out = sys.argv[sys.argv.index('--sheet') + 1]
        cells = ''.join('<figure><svg viewBox="0 0 120 80" width="180" height="120" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">%s</svg><figcaption>%s</figcaption></figure>' % (G[k], k) for k in ORDER)
        open(out, 'w', encoding='utf-8').write('<!doctype html><meta charset=utf-8><style>:root{--highlight:#C2540A}body{font:12px monospace;color:#121619;background:#fff;display:flex;flex-wrap:wrap;gap:6px;padding:8px}figure{margin:0;border:1px solid #ccd;border-radius:4px;padding:4px}</style>' + cells)
