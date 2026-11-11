"""hotwire.py - hot-wire templates for the wing core (WNG-001) and the 1:1 tiled letter-paper PDF printer.

Section: k09kit.section() (subsystems/wing/s5010.dat, the same call wing.py makes) at the chord of each core end,
TE opened to k09kit.TE_MIN_M (0.6 mm) by k09kit.section_loop exactly as the CAD does. The wing is one piece with
constant chord and no twist (params wing.twist_deg, wing.chord_m), so the two end templates have the same outline;
they are still computed separately from the params so a taper or twist would show up.

Kerf: the wire rides on the template edge, so the wire centre runs one wire radius outside it and the foam burns
back kerf/2 from the wire centre. Template = true section offset OUTWARD by (kerf/2 - wire radius); with the
defaults (kerf 1.0 mm, 0.51 mm wire) that is 0.24 mm. Both values are in shopconfig.HOTWIRE: measure the kerf on
the first practice cut (cut a 50 mm wide test block, measure the thickness loss) and re-run.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cad_source as cs            # noqa: E402  (fusion path)
import dxf                         # noqa: E402
import k09kit as k9                # noqa: E402
import shopconfig as cfg           # noqa: E402


def offset_loop(loop, d):
    """Offset a closed polygon by d (mm, + = outward) with mitred vertices (miter limit 4 d)."""
    n = len(loop)
    sgn = 1.0 if sum(loop[i - 1][0] * loop[i][1] - loop[i][0] * loop[i - 1][1] for i in range(n)) > 0 else -1.0
    out = []
    for i in range(n):
        p0, p1, p2 = loop[i - 1], loop[i], loop[(i + 1) % n]
        def nrm(a, b):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1.0
            return (dy / L * sgn, -dx / L * sgn)       # outward for a CCW loop when sgn = +1
        n1, n2 = nrm(p0, p1), nrm(p1, p2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        bl = math.hypot(bx, by)
        if bl < 1e-9:
            bx, by, bl = n1[0], n1[1], 1.0
        bx, by = bx / bl, by / bl
        cosh = bx * n1[0] + by * n1[1]
        m = d / max(cosh, 0.25)
        out.append((p1[0] + bx * m, p1[1] + by * m))
    return out


def template_geometry(P):
    """All template numbers (mm) from params + wing params + the section file."""
    v = lambda k, u=None: k9.val(P, k, u)
    W = cs.local_params('wing')
    coords, src = k9.section(P)
    c = v('wing.chord_m', 'm')
    twist = v('wing.twist_deg', 'deg')
    span = v('wing.span_m', 'm')
    hf = k9.hinge_frac(P)
    spar_x, spar_z = v('wing.spar.x_m', 'm'), v('wing.spar.z_m', 'm')
    gap = W['slot']['bond_gap_m']['value'] if 'slot' in W and 'bond_gap_m' in W['slot'] else 0.0002
    bore_r = v('wing.spar.od_m', 'm') / 2 + gap
    k = cfg.HOTWIRE
    off = k['kerf_mm'] / 2 - k['wire_d_mm'] / 2
    ends = []
    for name, y in (('root', -span / 2), ('tip', span / 2)):
        loop = k9.section_loop(coords, c, n=90)                           # m, (x, z), TE opened to 0.6 mm
        true = [(x * 1000, z * 1000) for x, z in loop]
        cut = offset_loop(true, off)
        ends.append(dict(name=name, y_mm=y * 1000, chord_mm=c * 1000, twist_deg=twist, true=true, cut=cut))
    return dict(ends=ends, src=src, offset_mm=off, kerf_mm=k['kerf_mm'], wire_mm=k['wire_d_mm'],
                spar=(spar_x * 1000, spar_z * 1000), bore_r=bore_r * 1000, hinge_x=hf * c * 1000,
                te_min_mm=k9.TE_MIN_M * 1000, t_c=v('wing.t_c'), chord_mm=c * 1000)


def template_drawing(G, end):
    """One template as a Drawing in template coordinates (mm, x aft from the LE, z up from the chord line)."""
    d = dxf.Drawing()
    d.poly(end['cut'], 'CUT')
    c = end['chord_mm']
    sx, sz = G['spar']
    # pin holes on the chord line: same position on both templates -> both ends register on the same line
    pins = [(0.10 * c, 0.0), (0.60 * c, 0.0)]
    for px, pz in pins:
        d.poly(dxf.circle(px, pz, 1.0, 16), 'CUT')
    d.poly(end['true'], 'MARK')                                            # true section (core surface)
    d.poly([(1.0, 0.0), (c - 1.0, 0.0)], 'MARK', closed=False)              # chord line
    for i in range(1, 10):                                                 # 10 % chord stations
        x = c * i / 10
        d.poly([(x, -1.5), (x, 1.5)], 'MARK', closed=False)
    d.poly(dxf.circle(sx, sz, G['bore_r'], 48), 'MARK')                     # spar bore position (cut later, from below)
    d.poly([(sx - 3, sz), (sx + 3, sz)], 'MARK', closed=False)
    d.poly([(sx, sz - 3), (sx, sz + 3)], 'MARK', closed=False)
    hx = G['hinge_x']
    d.poly([(hx, -2.0), (hx, 2.0)], 'MARK', closed=False)                  # elevon hinge station
    B = cfg.HOTWIRE['blank_mm']
    lm = cfg.HOTWIRE['le_margin_mm']
    zlo = min(p[1] for p in end['true'])
    zb = zlo - (B[2] - (max(p[1] for p in end['true']) - zlo)) / 2          # centre the section in the blank
    d.poly([(-lm, zb), (B[1] - lm, zb), (B[1] - lm, zb + B[2]), (-lm, zb + B[2])], 'NOTES')
    txt = [(4, 'K09-L WNG-001 hot-wire template  %s END (y %+.0f mm)' % (end['name'].upper(), end['y_mm'])),
           (3, 'S5010 c %.1f mm  twist %.1f deg  TE %.1f mm  (%s)' % (c, end['twist_deg'], G['te_min_mm'], G['src'])),
           (3, 'CUT = true section + %.2f mm (kerf %.2f / 2 - wire %.2f / 2). MARK = true section, chord, 10 %% '
               'stations, spar bore D %.1f at x %.1f z %.1f, hinge x %.1f' % (
                   G['offset_mm'], G['kerf_mm'], G['wire_mm'], 2 * G['bore_r'], sx, sz, hx)),
           (3, 'NOTES rectangle = blank end %g x %g mm, LE %g mm in from the front face. Pins D2 on the chord line.'
               % (B[1], B[2], lm))]
    y = zb - 6
    for h, s in txt:
        d.text(0, y, h, s)
        y -= h + 3
    return d, pins, zb


# ----------------------------------------------------------------------------- 1:1 tiled PDF
def tiled_pdf(path, pages_src, title):
    """pages_src: [(name, draw(ax), (xmin, ymin, xmax, ymax))] in mm. Each source is tiled onto landscape letter
    pages at exactly 1:1 (axes fill the page; 1 data unit = 1 mm), with registration crosses in the overlap."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    pw, ph = cfg.LETTER_MM
    m, ov = cfg.PAGE_MARGIN_MM, cfg.TILE_OVERLAP_MM
    uw, uh = pw - 2 * m, ph - 2 * m                       # usable area per page
    step_x, step_y = uw - ov, uh - ov
    n_pages = 0
    with PdfPages(path, metadata={'Title': title, 'Creator': 'make_shop_files.py', 'CreationDate': None,
                                  'ModDate': None}) as pdf:
        for name, draw, (x0, y0, x1, y1) in pages_src:
            x0, y0, x1, y1 = x0 - 10, y0 - 10, x1 + 10, y1 + 10
            nx = max(1, math.ceil((x1 - x0 - ov) / step_x))
            ny = max(1, math.ceil((y1 - y0 - ov) / step_y))
            for j in range(ny):
                for i in range(nx):
                    fig = plt.figure(figsize=(pw / 25.4, ph / 25.4))
                    ax = fig.add_axes([0, 0, 1, 1])
                    ax.set_axis_off()
                    tx, ty = x0 + i * step_x, y0 + (ny - 1 - j) * step_y
                    ax.set_xlim(tx - m, tx - m + pw)
                    ax.set_ylim(ty - m, ty - m + ph)
                    ax.set_aspect('equal')
                    draw(ax)
                    # registration crosses: on a global grid inside the overlap bands (identical on both pages)
                    for gx in [x0 + k * step_x for k in range(nx + 1)] + [x0 + k * step_x + ov for k in range(nx + 1)]:
                        for gy in [y0 + k * step_y for k in range(ny + 1)] + [y0 + k * step_y + ov for k in range(ny + 1)]:
                            if tx - 0.5 <= gx <= tx + uw + 0.5 and ty - 0.5 <= gy <= ty + uh + 0.5:
                                ax.plot([gx - 5, gx + 5], [gy, gy], color='k', lw=0.4)
                                ax.plot([gx, gx], [gy - 5, gy + 5], color='k', lw=0.4)
                                ax.add_patch(plt.Circle((gx, gy), 2.5, fill=False, lw=0.4))
                    ax.plot([tx, tx + uw, tx + uw, tx, tx], [ty, ty, ty + uh, ty + uh, ty], color='0.6', lw=0.3,
                            ls=(0, (2, 2)))
                    ax.text(tx + 2, ty + uh - 4, '%s  page %d/%d (row %d, col %d)  PRINT AT 100 %% / ACTUAL SIZE. '
                            'Overlap %g mm: align the crosses.' % (name, j * nx + i + 1, nx * ny, j + 1, i + 1, ov),
                            fontsize=6, va='top')
                    sb = ty + 3                                          # 100 mm scale check
                    ax.plot([tx + 2, tx + 102], [sb, sb], color='k', lw=0.8)
                    for q in (0, 50, 100):
                        ax.plot([tx + 2 + q, tx + 2 + q], [sb, sb + 2.5], color='k', lw=0.6)
                    ax.text(tx + 104, sb, 'measure: must be 100.0 mm', fontsize=6, va='center')
                    pdf.savefig(fig)
                    plt.close(fig)
                    n_pages += 1
    return n_pages


def draw_loops(ax, loops_by_style):
    for loops, style in loops_by_style:
        for l in loops:
            xs = [p[0] for p in l] + ([l[0][0]] if style.get('closed', True) else [])
            ys = [p[1] for p in l] + ([l[0][1]] if style.get('closed', True) else [])
            ax.plot(xs, ys, color=style.get('c', 'k'), lw=style.get('lw', 0.5), ls=style.get('ls', '-'))
