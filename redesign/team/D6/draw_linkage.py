"""FIG D6-01: elevon linkage section at the arm plane (y 0.285 m) at -25 / 0 / +25 deg, with the bridge-rod sweep
in D3's fin notch. Drawn from params (mechanisms/params.json, params.json, fins/params.json) and the CAD module's
four-bar, so it moves with the design.   python -I redesign/team/D6/draw_linkage.py  -> fig-d6-linkage.svg
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE.parents[1]
sys.path.insert(0, str(R / "fusion"))
sys.path.insert(0, str(R / "subsystems" / "mechanisms" / "fusion"))
import k09kit as k9          # noqa: E402
import mechanisms as M       # noqa: E402

INK, INK2, INK3, LINE3 = "#121619", "#4B5563", "#6B7280", "#9AA4B1"
ACC, HIL, WNG = "#1F5FC7", "#C2540A", "#4C8DE0"
S = 7000.0                   # px per metre (7 px/mm)
X0, X1, Z0, Z1 = 0.163, 0.326, -0.040, 0.022


def px(x, z):
    return (40 + (x - X0) * S, 30 + (Z1 - z) * S)


def path(pts, close=False):
    s = " ".join("%s%.1f %.1f" % ("M" if i == 0 else "L", *px(*p)) for i, p in enumerate(pts))
    return s + (" Z" if close else "")


def rot(X, Z, d):
    r = math.radians(d)
    return (X * math.cos(r) + Z * math.sin(r), -X * math.sin(r) + Z * math.cos(r))


def main():
    P = k9.load_params()
    LP = M.load_local()
    co, _ = k9.section(P)
    G = M.geometry(P, LP, co)
    F = json.load(open(R / "subsystems" / "fins" / "params.json", encoding="utf-8"))["fin_detail"]["link_slot"]
    hw, dep = F["half_width_m"]["value"], F["depth_m"]["value"]
    xh, zh = G["xh"], G["zh"]
    lk = (xh, zh, G["rh"], G["xs"], G["zs"], G["rs"])
    xs_ = [X0 + (0.32 - X0) * i / 60 for i in range(61)]
    up = [(x, G["zu"](x)) for x in xs_]
    lo = [(x, G["zl"](x)) for x in xs_]
    core = [p for p in up if p[0] <= xh] + [(xh, G["zl"](xh))] + [p for p in reversed(lo) if p[0] <= xh]
    panel = [(x - xh, z - zh) for x, z in up if x >= xh] + [(x - xh, z - zh) for x, z in reversed(lo) if x >= xh + 0.0056]
    horn = [(X / 1000, Z / 1000) for X, Z in LP["mec"]["horn"]["outline_mm"]["value"]]
    W = 40 + (X1 - X0) * S + 20
    H = 30 + (Z1 - Z0) * S + 60
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.0f %.0f" font-family="IBM Plex Sans, system-ui, '
         'sans-serif">' % (W, H)]
    o.append('<path d="%s" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="1.5"/>' % (path(core, True), WNG, INK))
    # servo case and frame
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.25" stroke="%s" '
             'stroke-width="1.5"/>' % (*px(G["cx0"], G["cz1"]), (G["cx1"] - G["cx0"]) * S, (G["cz1"] - G["cz0"]) * S,
                                      INK3, INK))
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="0.75" '
             'stroke-dasharray="6 4"/>' % (*px(G["fx0"], G["fz1"]), (G["fx1"] - G["fx0"]) * S,
                                          (G["fz1"] - G["cz0"]) * S, INK2))
    for d, op, dash in ((-25, 0.55, "6 4"), (25, 0.55, "6 4"), (0, 1.0, "")):
        pan = [(xh + a, zh + b) for a, b in (rot(X, Z, d) for X, Z in panel)]
        hn = [(xh + a, zh + b) for a, b in (rot(X, Z, d) for X, Z in horn)]
        th = M.theta_of_delta(lk, d)
        p, q = M.arm_hole(lk, th), M.horn_hole(lk, d)
        bx, bz = rot(0.0, -G["rb"], d)
        da = ' stroke-dasharray="%s"' % dash if dash else ""
        o.append('<path d="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="1.5"%s/>' % (
            path(pan, True), WNG, 0.18 * op, INK if d == 0 else INK3, da))
        o.append('<path d="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="1.5"%s/>' % (
            path(hn, True), HIL, 0.35 * op, HIL, da))
        o.append('<path d="%s" stroke="%s" stroke-width="2" fill="none" opacity="%.2f"%s/>' % (
            path([(G["xs"], G["zs"]), p]), HIL, op, da))
        o.append('<path d="%s" stroke="%s" stroke-width="2" fill="none" opacity="%.2f"%s/>' % (
            path([p, q]), INK, op, da))
        c = px(xh + bx, zh + bz)
        o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity="%.2f"/>' % (*c, G["rod_r"] * S, INK, op))
        lab = px(q[0], q[1] - 0.004)
        o.append('<text x="%.1f" y="%.1f" font-size="12" font-family="IBM Plex Mono, monospace" fill="%s" '
                 'text-anchor="middle">%+d°</text>' % (lab[0] + (-18 if d > 0 else 18 if d < 0 else 0), lab[1] + 4,
                                                        INK2, d))
    # fin notch (section at the fin plane, drawn in place) and the rod sweep arc
    nb = G["zl"](xh) - dep
    o.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.25" stroke-dasharray="6 4"/>' % (
        path([(xh - hw, G["zl"](xh - hw)), (xh - hw, nb), (xh + hw, nb), (xh + hw, G["zl"](xh + hw))]), ACC))
    arc = [(xh + a, zh + b) for a, b in (rot(0.0, -G["rb"], d) for d in range(-30, 31, 2))]
    o.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.25"/>' % (path(arc), ACC))
    t = px(xh + hw + 0.002, nb + 0.002)
    o.append('<text x="%.1f" y="%.1f" font-size="11" fill="%s">fin notch 24 × 12 mm (D3)</text>' % (*t, ACC))
    for txt, x, z in (("servo SH-0255MG+", G["cx0"], G["cz1"] + 0.003), ("hinge axis", xh - 0.002, zh + 0.004),
                      ("core", 0.205, 0.016), ("elevon", 0.29, 0.006)):
        a = px(x, z)
        o.append('<text x="%.1f" y="%.1f" font-size="12" fill="%s">%s</text>' % (*a, INK2, txt))
    hx = px(xh, zh)
    o.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (*hx, INK))
    # scale bar
    a, b = px(X0 + 0.002, Z0 + 0.004), px(X0 + 0.012, Z0 + 0.004)
    o.append('<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="1"/>' % (*a, *b, INK))
    o.append('<text x="%.1f" y="%.1f" font-size="11" font-family="IBM Plex Mono, monospace" fill="%s">0 — 10 mm'
             '</text>' % (a[0], a[1] + 14, INK3))
    o.append("</svg>")
    (HERE / "fig-d6-linkage.svg").write_text("\n".join(o) + "\n", encoding="utf-8")
    print("wrote", HERE / "fig-d6-linkage.svg")


if __name__ == "__main__":
    main()
