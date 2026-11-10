"""Figures for the C3 FEA (design-system diagram style: SVG, 1200 px master, IBM Plex, light-theme values embedded,
transparent background, title in the caption not in the SVG). Called by pod_fea.py; re-draw alone with
`python -I redesign/team/C3/pod_fea.py --plots`.
"""
import math
from pathlib import Path

FG, FG2, FG3 = "#121619", "#4B5563", "#6B7280"
LINE, LINE2, LINE3 = "#E3E7ED", "#CBD2DB", "#9AA4B1"
ACCENT, ORANGE = "#1F5FC7", "#D9480F"
FAIL, CHECKED = "#B42323", "#0E6F74"
GREY_FILL = ("#E6E8EB", "#CBD2DB", "#9AA4B1", "#B9C0CA", "#DADFE5")
MONO = 'font-family="IBM Plex Mono, monospace"'


def _svg(W, H):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'font-family="IBM Plex Sans, system-ui, sans-serif">']


def _fmt(v):
    a = abs(v)
    if a >= 100:
        return "%.0f" % v
    if a >= 10:
        return "%.0f" % v
    if a >= 1:
        return "%.1f" % v
    return "%.2f" % v


class Axes:
    def __init__(self, o, x0, y0, w, h, xr, yr, xlabel, ylabel, xticks, yticks, xfmt=_fmt, yfmt=_fmt):
        self.o, self.x0, self.y0, self.w, self.h, self.xr, self.yr = o, x0, y0, w, h, xr, yr
        for t in yticks:
            y = self.sy(t)
            o.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + w}" y2="{y:.1f}" stroke="{LINE}" stroke-width="0.75"/>')
            o.append(f'<text x="{x0 - 8}" y="{y + 4:.1f}" font-size="12" {MONO} fill="{FG3}" text-anchor="end">'
                     f'{yfmt(t)}</text>')
        for t in xticks:
            x = self.sx(t)
            o.append(f'<line x1="{x:.1f}" y1="{y0 + h}" x2="{x:.1f}" y2="{y0 + h + 5}" stroke="{LINE3}" stroke-width="1"/>')
            o.append(f'<text x="{x:.1f}" y="{y0 + h + 20}" font-size="12" {MONO} fill="{FG3}" text-anchor="middle">'
                     f'{xfmt(t)}</text>')
        o.append(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{LINE3}" stroke-width="1"/>')
        o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{LINE3}" stroke-width="1"/>')
        o.append(f'<text x="{x0 + w / 2}" y="{y0 + h + 40}" font-size="12" fill="{FG2}" text-anchor="middle">{xlabel}</text>')
        o.append(f'<text x="{x0}" y="{y0 - 12}" font-size="12" fill="{FG2}">{ylabel}</text>')

    def sx(self, v):
        return self.x0 + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def sy(self, v):
        return self.y0 + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def line(self, xs, ys, colour, width=1.75, dash=None):
        pts = " ".join(f"{self.sx(x):.1f},{self.sy(max(self.yr[0], min(self.yr[1], y))):.1f}" for x, y in zip(xs, ys))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.o.append(f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="{width}"{d}/>')

    def hline(self, y, colour, label, dash="6 4"):
        yy = self.sy(y)
        self.o.append(f'<line x1="{self.x0}" y1="{yy:.1f}" x2="{self.x0 + self.w}" y2="{yy:.1f}" stroke="{colour}" '
                      f'stroke-width="1.25" stroke-dasharray="{dash}"/>')
        self.o.append(f'<text x="{self.x0 + self.w - 4}" y="{yy - 6:.1f}" font-size="12" fill="{colour}" '
                      f'text-anchor="end">{label}</text>')

    def label(self, x, y, text, colour=FG2, anchor="start", size=12, mono=False):
        f = " " + MONO if mono else ""
        self.o.append(f'<text x="{self.sx(x) if x is not None else 0:.1f}" y="{self.sy(y):.1f}" font-size="{size}"'
                      f'{f} fill="{colour}" text-anchor="{anchor}">{text}</text>')


def fig_model(res, out):
    """FIG C3-FEA-01: M1 section, regions and boundary conditions."""
    import pod_fea as F
    G = F.m1_geometry(True)
    g = res["inputs"]["geometry"]
    W, H = 1200, 520
    o = _svg(W, H)
    xr, zr = (-0.14, 0.17), (-0.02, 0.09)
    s = (W - 80) / (xr[1] - xr[0])
    X = lambda x: 40 + (x - xr[0]) * s
    Z = lambda z: H - 70 - (z - zr[0]) * s

    def poly(pts, fill, stroke=FG, sw=1.5, op=1.0):
        p = " ".join(f"{X(x):.1f},{Z(z):.1f}" for x, z in pts)
        o.append(f'<polygon points="{p}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"/>')

    poly(G["wing"], GREY_FILL[0])
    poly(G["filler"], GREY_FILL[4])
    poly(G["walls"], "#FFFFFF", sw=1.5)
    poly([(g["x0"], g["zb"]), (g["xn"], g["zb"]), (g["xn"], g["zh"]), (g["x0"], g["zh"])], GREY_FILL[2])
    poly([(g["xn"], g["zb"]), (g["x_rec1"], g["zb"]), (g["x_rec1"], g["zf"]), (g["xn"], g["zf"])], GREY_FILL[2])
    sp = F.gv("wing.spar.x_m"), F.gv("wing.spar.z_m"), F.gv("wing.spar.od_m") / 2
    o.append(f'<circle cx="{X(sp[0]):.1f}" cy="{Z(sp[1]):.1f}" r="{sp[2] * s:.1f}" fill="#FFFFFF" stroke="{FG}" '
             f'stroke-width="2.5"/>')
    # bond line
    bl = [(x, z) for x, z in G["filler"][2:][::-1]] + [(g["x_rec0"], g["zb"]), (g["x_rec1"], g["zb"])]
    o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (
        " ".join(f"{X(x):.1f},{Z(z):.1f}" for x, z in [(0.0, 0.0)] + bl), ACCENT))
    # load arrows on the floor top (pack footprint, crash down)
    for x in [F.PACK_X_FWD - F.PACK_L / 2 + i * F.PACK_L / 6 for i in range(7)]:
        o.append(f'<line x1="{X(x):.1f}" y1="{Z(g["zf"]) - 34:.1f}" x2="{X(x):.1f}" y2="{Z(g["zf"]) - 4:.1f}" '
                 f'stroke="{ORANGE}" stroke-width="1.5"/>')
        o.append(f'<polygon points="{X(x) - 4:.1f},{Z(g["zf"]) - 10:.1f} {X(x) + 4:.1f},{Z(g["zf"]) - 10:.1f} '
                 f'{X(x):.1f},{Z(g["zf"]) - 3:.1f}" fill="{ORANGE}"/>')
    lab = lambda x, z, t, c=FG2, a="start": o.append(
        f'<text x="{X(x):.1f}" y="{Z(z):.1f}" font-size="12" fill="{c}" text-anchor="{a}">{t}</text>')
    lab(-0.05, 0.062, "side walls 2 × 4.8 mm board")
    lab(-0.05, 0.050, "floor-top load segments, 5 mm", ORANGE)
    lab(0.105, 0.035, "spar slot: clamped")
    lab(0.12, -0.012, "XPS wing core (S5010, c 0.32 m)")
    lab(0.012, -0.012, "pod-to-wing bond line", ACCENT)
    lab(-0.128, 0.087, "nose wall")
    # scale bar
    o.append(f'<line x1="{X(-0.13):.1f}" y1="{H - 20}" x2="{X(-0.08):.1f}" y2="{H - 20}" stroke="{FG}" stroke-width="1"/>')
    o.append(f'<text x="{X(-0.13):.1f}" y="{H - 28}" font-size="11" {MONO} fill="{FG3}">0 — 50 mm</text>')
    o.append("</svg>")
    (out / "fig-c3-fea-01-model.svg").write_text("\n".join(o), encoding="utf-8")


def fig_bond(res, out):
    """FIG C3-FEA-02: peel along the bond (finest mesh, footprint variant) vs the hand calc's linear distribution."""
    m1 = res["M1_FOOTPRINT"]
    W, H = 1200, 520
    o = _svg(W, H)
    panels = [("design (L2 pair, MC-C, in-plane part)", m1["profile_design"], m1["hand_design_inplane"],
               m1["design_inplane_N_Nm"]),
              ("crash 12.75 g, +z", m1["profile_crash_up"], m1["hand_crash_up_inplane"], None)]
    allow = res["inputs"]["allowables"]["xps_t"] / 1e3
    for k, (title, pr, hand, _) in enumerate(panels):
        x0 = 90 + k * 570
        xs = [x * 1000 for x in pr["x"]]
        sg = [v / 1e3 for v in pr["sigma"]]
        ymax = 50 * math.ceil(max(max(sg), allow) * 1.15 / 50)
        ymin = -50 * math.ceil(max(0.0, -min(sg)) / 50)
        ax = Axes(o, x0, 50, 480, 380, (0, 100), (ymin, ymax), "x from the wing LE, mm", "peel σn, kPa",
                  [0, 20, 40, 60, 80, 100], list(range(int(ymin), int(ymax) + 1, 50)))
        o.append(f'<text x="{x0}" y="20" font-size="14" font-weight="600" fill="{FG}">{title}</text>')
        ax.hline(0, LINE3, "", dash="2 3")
        ax.hline(allow, FAIL, "allowable %.0f kPa" % allow)
        sel = [(x, s) for x, s in zip(xs, sg) if x <= 100]
        ax.line([p[0] for p in sel], [p[1] for p in sel], ACCENT, 1.75)
        # hand: linear Navier distribution over 0 ... 65 mm with peak hand["sigma"] at the tension end
        L = res["inputs"]["geometry"]["x_rec1"] * 1000
        sh = hand["sigma"] / 1e3
        ax.line([0, L], [sh, sh], FG3, 1.25, dash="6 4")
        ax.label(L, sh + 0.03 * (ymax - ymin), "hand peak %.0f kPa" % sh, FG3, "end")
        ax.label(2, ymax - 0.06 * (ymax - ymin), "FEA, finest mesh", ACCENT)
    o.append("</svg>")
    (out / "fig-c3-fea-02-bond-peel.svg").write_text("\n".join(o), encoding="utf-8")


def fig_convergence(res, out):
    """FIG C3-FEA-03: each reported quantity / its finest-mesh value vs element size."""
    items = [("bond R design (d0)", res["M1_FOOTPRINT"]["convergence"]["design_R_d0"]),
             ("bond R crash +z (d0)", res["M1_FOOTPRINT"]["convergence"]["crash_up_R_d0"]),
             ("overhang face, crash", res["M1_FOOTPRINT"]["convergence"]["overhang_crash_top"]),
             ("aft stop fillet peak", res["M2"]["AFT_FILLET_SOLID"]["convergence"]["peak_s1_pa"]),
             ("aft tray bending peak", res["M2"]["AFT_FILLET_SOLID"]["convergence"]["tray_peak_pa"]),
             ("board peel, solid tray (d0)", res["M2"]["AFT_FILLET_SOLID"]["convergence"]["peel_peak_d0_pa"]),
             ("bond peel raw, design", res["M1_FOOTPRINT"]["convergence"]["design_sigma_raw"])]
    W, H = 1200, 520
    o = _svg(W, H)
    ax = Axes(o, 90, 40, 760, 400, (0, 3.2), (0.6, 1.4), "mesh level (0 coarsest … 3 finest; h halves per level)",
              "value / finest-mesh value", [0, 1, 2, 3], [0.6, 0.8, 1.0, 1.2, 1.4], xfmt=lambda v: "%d" % v)
    ax.hline(1.0, LINE3, "", dash="2 3")
    shades = [ACCENT, "#3D6FCF", "#5B85D8", FG, FG2, FG3, FAIL]
    for k, (name, c) in enumerate(items):
        q = c["q"][::-1]                  # coarse -> fine
        qf = c["q"][0]
        ys = [v / qf for v in q]
        col = shades[k]
        dash = "6 4" if name.startswith("bond peel raw") else None
        ax.line([0, 1, 2, 3], ys, col, 1.75, dash)
        gci = c.get("gci_pct")
        txt = "%s  GCI %s" % (name, ("%.1f %%" % gci) if gci is not None else "n/a")
        o.append(f'<line x1="880" y1="{70 + 26 * k}" x2="910" y2="{70 + 26 * k}" stroke="{col}" stroke-width="2"'
                 + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
        o.append(f'<text x="918" y="{74 + 26 * k}" font-size="12" fill="{FG2}">{txt}</text>')
    o.append(f'<text x="880" y="{74 + 26 * len(items) + 14}" font-size="11" fill="{FG3}">dashed: singular corner value,'
             f' not a design number</text>')
    o.append("</svg>")
    (out / "fig-c3-fea-03-convergence.svg").write_text("\n".join(o), encoding="utf-8")


def fig_stops(res, out):
    """FIG C3-FEA-04: stop variants, each check as a ratio to its allowable (finest mesh)."""
    al = res["inputs"]["allowables"]
    rows = []
    names = {"AFT_FILLET_WIN": "aft, as drawn + 2 mm fillet (y 0)", "AFT_FILLET_SOLID": "aft, as drawn + fillet (tray edge)",
             "AFT_HEEL_FILLET": "aft + 2 mm heel", "AFT_PROPPED_WIN": "aft + strut to the spar bridge",
             "FWD_FILLET": "forward, cantilever + fillet", "FWD_BEDDED": "forward + 1 mm bed to nose wall"}
    for k, nm in names.items():
        if k not in res["M2"]:
            continue
        f = res["M2"][k]["levels"][-1]
        rows.append((nm, f["peak_s1_pa"] / al["petg"], f["tray_peak_pa"] / 25e6, f["peel_peak_d0_pa"] / al["board_flat"]))
    W, H = 1200, 80 + 56 * len(rows)
    o = _svg(W, H)
    x0, w = 330, 760
    vmax = max(1.5, max(max(r[1:]) for r in rows) * 1.05)
    sx = lambda v: x0 + min(v, vmax) / vmax * w
    for t in [0, 1, 2, 4, 6, 8, 10]:
        if t <= vmax:
            o.append(f'<line x1="{sx(t):.1f}" y1="40" x2="{sx(t):.1f}" y2="{H - 30}" stroke="{LINE}" stroke-width="0.75"/>')
            o.append(f'<text x="{sx(t):.1f}" y="{H - 12}" font-size="12" {MONO} fill="{FG3}" text-anchor="middle">{t}</text>')
    o.append(f'<line x1="{sx(1):.1f}" y1="34" x2="{sx(1):.1f}" y2="{H - 30}" stroke="{FAIL}" stroke-width="1.25" '
             f'stroke-dasharray="6 4"/>')
    o.append(f'<text x="{sx(1) + 6:.1f}" y="30" font-size="12" fill="{FAIL}">allowable</text>')
    marks = [("stop root σ1 / 15 MPa", "circle", ACCENT), ("tray bending / 25 MPa", "square", FG),
             ("board peel / 50 kPa", "diamond", ORANGE)]
    for i, (lab, shp, col) in enumerate(marks):
        x = 330 + i * 250
        o.append(_mark(shp, x, 14, col))
        o.append(f'<text x="{x + 10}" y="18" font-size="12" fill="{FG2}">{lab}</text>')
    for j, r in enumerate(rows):
        y = 70 + 56 * j
        o.append(f'<text x="{x0 - 14}" y="{y + 4}" font-size="12" fill="{FG2}" text-anchor="end">{r[0]}</text>')
        o.append(f'<line x1="{x0}" y1="{y}" x2="{x0 + w}" y2="{y}" stroke="{LINE}" stroke-width="0.75"/>')
        for (lab, shp, col), v in zip(marks, r[1:]):
            o.append(_mark(shp, sx(v), y, col))
            if v > vmax:
                o.append(f'<text x="{sx(v) + 8:.1f}" y="{y + 4}" font-size="11" {MONO} fill="{FG3}">{v:.1f}</text>')
    o.append("</svg>")
    (out / "fig-c3-fea-04-stops.svg").write_text("\n".join(o), encoding="utf-8")


def fig_bond_variants(res, out):
    """FIG C3-FEA-05: pod-to-wing bond interaction per load case and per bond-layout variant (finest mesh, 2 mm mean)."""
    rows = [("as drawn: walls bonded (wall edges)", "M1_BONDED"), ("as drawn: footprint only", "M1_FOOTPRINT"),
            ("fix: feet tied to walls", "M1_TIED_FOOTPRINT"), ("fix + floor end released", "M1_TIED_STEPGAP")]
    rows = [(n, res[k]["levels"][-1]) for n, k in rows if k in res]
    cases = [("design", "design", "circle", ACCENT), ("crash +z", "crash_up", "square", FG),
             ("crash −z", "crash_dn", "diamond", ORANGE), ("crash +x", "crash_px", "circle", FG3),
             ("crash −x", "crash_mx", "square", FAIL)]
    W, H = 1200, 80 + 56 * len(rows)
    o = _svg(W, H)
    x0, w = 330, 760
    vmax = 12.0
    sx = lambda v: x0 + math.log10(max(v, 0.1) / 0.1) / math.log10(vmax / 0.1) * w
    for t in [0.1, 0.2, 0.5, 1, 2, 5, 10]:
        o.append(f'<line x1="{sx(t):.1f}" y1="40" x2="{sx(t):.1f}" y2="{H - 30}" stroke="{LINE}" stroke-width="0.75"/>')
        o.append(f'<text x="{sx(t):.1f}" y="{H - 12}" font-size="12" {MONO} fill="{FG3}" text-anchor="middle">{t:g}</text>')
    o.append(f'<line x1="{sx(1):.1f}" y1="34" x2="{sx(1):.1f}" y2="{H - 30}" stroke="{FAIL}" stroke-width="1.25" '
             f'stroke-dasharray="6 4"/>')
    o.append(f'<text x="{sx(1) + 6:.1f}" y="{H - 34}" font-size="12" fill="{FAIL}">R = 1</text>')
    for i, (lab, _, shp, col) in enumerate(cases):
        x = 330 + i * 160
        o.append(_mark(shp, x, 14, col))
        o.append(f'<text x="{x + 10}" y="18" font-size="12" fill="{FG2}">{lab}</text>')
    for j, (name, lv) in enumerate(rows):
        y = 70 + 56 * j
        o.append(f'<text x="{x0 - 14}" y="{y + 4}" font-size="12" fill="{FG2}" text-anchor="end">{name}</text>')
        o.append(f'<line x1="{x0}" y1="{y}" x2="{x0 + w}" y2="{y}" stroke="{LINE}" stroke-width="0.75"/>')
        for _, key, shp, col in cases:
            v = lv[key]["R_peak_d0"]
            o.append(_mark(shp, sx(min(v, vmax)), y, col))
            if v > vmax:
                o.append(f'<text x="{sx(vmax) + 8:.1f}" y="{y + 4}" font-size="11" {MONO} fill="{FG3}">{v:.0f}</text>')
    o.append("</svg>")
    (out / "fig-c3-fea-05-bond-variants.svg").write_text("\n".join(o), encoding="utf-8")


def _mark(shp, x, y, col):
    if shp == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{col}"/>'
    if shp == "square":
        return f'<rect x="{x - 5.5:.1f}" y="{y - 5.5:.1f}" width="11" height="11" fill="{col}"/>'
    return f'<polygon points="{x:.1f},{y - 7:.1f} {x + 7:.1f},{y:.1f} {x:.1f},{y + 7:.1f} {x - 7:.1f},{y:.1f}" fill="{col}"/>'


def draw(res, out):
    out = Path(out)
    fig_model(res, out)
    fig_bond(res, out)
    fig_convergence(res, out)
    fig_stops(res, out)
    fig_bond_variants(res, out)
    print("figures written to %s" % out)
