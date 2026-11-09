"""General-arrangement 3-view of the K09-L tailsitter, drawn from params/params.json (design-system
diagram-style.md: third-angle, top above side, front to the right; ink outlines, subsystem fills at 35 %,
accent-blue dimensions, scale bar). Standalone SVG with the light-theme token values embedded.

Run:  python -I redesign/team/A1/draw_ga.py   -> ga-3view.svg beside this file
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARAMS = HERE.parents[1] / "params" / "params.json"


def leaf(d, path):
    for k in path.split("."):
        d = d[k]
    return d["value"] if isinstance(d, dict) and "value" in d else d


# ---- tokens (light theme values from design-system/tokens.css)
INK, INK2, INK3 = "#121619", "#4B5563", "#6B7280"
ACCENT = "#1F5FC7"
SUB = {"wing": "#4C8DE0", "fins": "#2BA6A0", "pod": "#7F8C9E", "propulsion": "#D45C8E", "landing": "#B07A3A"}
MONO = "'IBM Plex Mono', monospace"
SANS = "'IBM Plex Sans', system-ui, sans-serif"
PX_PER_M = 500.0          # 1200 px master; 1 m = 500 px


def main():
    p = json.loads(PARAMS.read_text(encoding="utf-8"))
    b, c = leaf(p, "wing.span_m"), leaf(p, "wing.chord_m")
    yf, hf, cf, xf = leaf(p, "fins.y_m"), leaf(p, "fins.half_height_m"), leaf(p, "fins.chord_m"), leaf(p, "fins.le_x_m")
    tube_l, tube_od = leaf(p, "fins.tube.length_m"), leaf(p, "fins.tube.od_m")
    D = leaf(p, "propulsion.prop_diameter_m")
    zm, xprop = leaf(p, "propulsion.stations.z_m"), leaf(p, "propulsion.stations.x_prop_plane_m")
    mot_d, mot_l = leaf(p, "propulsion.motor_diameter_m"), leaf(p, "propulsion.motor_length_m")
    pod = leaf(p, "pod.size_m")
    pod_x, pod_z = leaf(p, "pod.x_le_m"), leaf(p, "pod.z_base_m")
    xcg, zcg = leaf(p, "cg.x_target_m"), leaf(p, "cg.z_target_m")
    spar_x, spar_l = leaf(p, "wing.spar.x_m"), leaf(p, "wing.spar.length_m")
    tc = leaf(p, "wing.t_c")
    e_f, e_in, e_out = leaf(p, "wing.elevon.chord_frac"), leaf(p, "wing.elevon.inboard_y_m"), leaf(p, "wing.elevon.outboard_y_m")
    foot = leaf(p, "cg.foot_height_m")

    S = PX_PER_M
    out = []
    W = lambda s: out.append(s)

    def rect(x, y, w, h, fill, extra=""):
        W(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" fill-opacity="0.35" '
          f'stroke="{INK}" stroke-width="1.5" {extra}/>')

    def dim(x1, y1, x2, y2, text, tx, ty, anchor="middle"):
        W(f'<g stroke="{ACCENT}" stroke-width="1.25" fill="none"><line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
        if y1 == y2:
            W(f'<line x1="{x1:.1f}" y1="{y1-6:.1f}" x2="{x1:.1f}" y2="{y1+6:.1f}"/><line x1="{x2:.1f}" y1="{y2-6:.1f}" x2="{x2:.1f}" y2="{y2+6:.1f}"/>')
        else:
            W(f'<line x1="{x1-6:.1f}" y1="{y1:.1f}" x2="{x1+6:.1f}" y2="{y1:.1f}"/><line x1="{x2-6:.1f}" y1="{y2:.1f}" x2="{x2+6:.1f}" y2="{y2:.1f}"/>')
        W(f'</g><text x="{tx:.1f}" y="{ty:.1f}" font-family="{MONO}" font-size="12" fill="{ACCENT}" text-anchor="{anchor}">{text}</text>')

    def cg_symbol(x, y):
        W(f'<g transform="translate({x:.1f},{y:.1f})"><circle r="6" fill="#fff" stroke="{INK}" stroke-width="1"/>'
          f'<path d="M0,0 L6,0 A6,6 0 0 0 0,-6 Z M0,0 L-6,0 A6,6 0 0 0 0,6 Z" fill="{INK}"/></g>')

    def label(x, y, text, anchor="start", size=12, color=INK2, mono=False, weight=500):
        W(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO if mono else SANS}" font-size="{size}" font-weight="{weight}" '
          f'fill="{color}" text-anchor="{anchor}">{text}</text>')

    def axis(x, y, dx, dy, name):
        W(f'<g stroke="{INK3}" stroke-width="1" fill="{INK3}"><line x1="{x}" y1="{y}" x2="{x+dx}" y2="{y+dy}"/>'
          f'<circle cx="{x+dx}" cy="{y+dy}" r="2"/></g>')
        label(x + dx + (6 if dx else 0), y + dy + (4 if dx else -6), name, size=11, color=INK3, mono=True)

    # ---------------- TOP view (nose up): screen x = +y aircraft, screen y = +x aircraft (aft down)
    tx0, ty0 = 60 + (b / 2) * S, 70 + (-xprop + 0.06) * S      # screen origin = aircraft (x=0, y=0)
    ax = lambda y: tx0 + y * S
    ay = lambda x: ty0 + x * S
    label(ax(0), 40, "TOP (nose up)", "middle", 12, INK, weight=600)
    rect(ax(-b / 2), ay(0), b * S, c * S, SUB["wing"])
    for sgn in (1, -1):                                                 # elevons (wing subsystem, dashed hinge)
        for (y0, y1) in (e_in, e_out):
            x0 = ax(min(sgn * y0, sgn * y1))
            W(f'<rect x="{x0:.1f}" y="{ay(c*(1-e_f)):.1f}" width="{(y1-y0)*S:.1f}" height="{c*e_f*S:.1f}" fill="none" '
              f'stroke="{INK}" stroke-width="1" stroke-dasharray="6 4"/>')
    W(f'<line x1="{ax(-spar_l/2):.1f}" y1="{ay(spar_x):.1f}" x2="{ax(spar_l/2):.1f}" y2="{ay(spar_x):.1f}" '
      f'stroke="{INK3}" stroke-width="0.75" stroke-dasharray="6 4"/>')                        # hidden spar
    rect(ax(-pod[1] / 2), ay(pod_x), pod[1] * S, pod[0] * S, SUB["pod"])
    for sgn in (1, -1):
        # fin (edge-on): a thin line from the tube to the TE
        W(f'<line x1="{ax(sgn*yf):.1f}" y1="{ay(xf):.1f}" x2="{ax(sgn*yf):.1f}" y2="{ay(c):.1f}" stroke="{SUB["fins"]}" stroke-width="3"/>')
        W(f'<circle cx="{ax(sgn*yf):.1f}" cy="{ay(xf):.1f}" r="{tube_od/2*S:.1f}" fill="{SUB["fins"]}" fill-opacity="0.35" stroke="{INK}" stroke-width="1.5"/>')
        # motor (upper one visible) and prop disc edge-on
        rect(ax(sgn * yf - mot_d / 2), ay(xf - tube_od / 2 - mot_l), mot_d * S, mot_l * S, SUB["propulsion"])
        W(f'<line x1="{ax(sgn*yf-D/2):.1f}" y1="{ay(xprop):.1f}" x2="{ax(sgn*yf+D/2):.1f}" y2="{ay(xprop):.1f}" '
          f'stroke="{INK3}" stroke-width="2" stroke-dasharray="6 4"/>')
    cg_symbol(ax(0), ay(xcg))
    dim(ax(-b / 2), ay(c) + 26, ax(b / 2), ay(c) + 26, f"span {b*1000:.0f} mm", ax(0), ay(c) + 44)
    dim(ax(b / 2) + 30, ay(0), ax(b / 2) + 30, ay(c), f"chord {c*1000:.0f} mm", ax(b / 2) + 38, ay(c / 2) + 4, "start")
    dim(ax(-yf), ay(xf) - 36, ax(yf), ay(xf) - 36, f"motors ±{yf*1000:.0f} mm", ax(0), ay(xf) - 42)
    dim(ax(-b / 2) - 30, ay(0), ax(-b / 2) - 30, ay(xcg), f"CG {xcg*1000:.0f} mm", ax(-b / 2) - 36, ay(xcg) + 4, "end")
    axis(ax(-b / 2) - 20, ay(c) + 70, 0, 26, "+x")
    axis(ax(-b / 2) - 20, ay(c) + 70, 26, 0, "+y")

    # ---------------- SIDE view (nose left): screen x = +x aircraft, screen y = -z aircraft
    sx0, sy0 = 60 + (-xprop + 0.06) * S, ay(c) + 140 + (hf + D / 2) * S
    bx = lambda x: sx0 + x * S
    by = lambda z: sy0 - z * S
    label(bx(c / 2), sy0 - (hf + D / 2) * S - 20, "SIDE (nose left)", "middle", 12, INK, weight=600)
    # fin (full), tube, motors, props
    rect(bx(xf), by(hf), cf * S, 2 * hf * S, SUB["fins"])
    rect(bx(xf - tube_od / 2), by(tube_l / 2), tube_od * S, tube_l * S, SUB["fins"])
    for sgn in (1, -1):
        rect(bx(xf - tube_od / 2 - mot_l), by(sgn * zm + mot_d / 2), mot_l * S, mot_d * S, SUB["propulsion"])
        W(f'<line x1="{bx(xprop):.1f}" y1="{by(sgn*zm+D/2):.1f}" x2="{bx(xprop):.1f}" y2="{by(sgn*zm-D/2):.1f}" '
          f'stroke="{INK3}" stroke-width="2" stroke-dasharray="6 4"/>')
        # foot at the fin trailing-edge tip
        rect(bx(c), by(sgn * hf + 0.008), foot * S, 0.016 * S, SUB["landing"])
    # wing section (simple reflexed outline from t/c)
    t = tc * c
    W(f'<path d="M{bx(0):.1f},{by(0):.1f} Q{bx(0.12*c):.1f},{by(0.62*t):.1f} {bx(0.3*c):.1f},{by(0.5*t):.1f} '
      f'Q{bx(0.75*c):.1f},{by(0.2*t):.1f} {bx(c):.1f},{by(0.02*t):.1f} Q{bx(0.75*c):.1f},{by(-0.18*t):.1f} {bx(0.3*c):.1f},{by(-0.4*t):.1f} '
      f'Q{bx(0.1*c):.1f},{by(-0.4*t):.1f} {bx(0):.1f},{by(0):.1f} Z" fill="{SUB["wing"]}" fill-opacity="0.35" stroke="{INK}" stroke-width="1.5"/>')
    rect(bx(pod_x), by(pod_z + pod[2]), pod[0] * S, pod[2] * S, SUB["pod"])
    cg_symbol(bx(xcg), by(zcg))
    dim(bx(xf) - 40, by(hf), bx(xf) - 40, by(-hf), f"fin {2*hf*1000:.0f} mm", bx(xf) - 46, by(0) + 4, "end")
    dim(bx(xf), by(-hf) - 30, bx(c), by(-hf) - 30, f"fin chord {cf*1000:.0f} mm", bx((xf + c) / 2), by(-hf) - 48)
    dim(bx(xprop) - 50, by(zm + D / 2), bx(xprop) - 50, by(zm - D / 2), f"prop {D*1000:.0f} mm", bx(xprop) - 56, by(zm) + 4, "end")
    axis(bx(xf) - 20, by(-hf) - 80, 26, 0, "+x")
    axis(bx(xf) - 20, by(-hf) - 80, 0, -26, "+z")

    # ---------------- FRONT view (from the nose): screen x = +y aircraft, screen y = -z aircraft
    fx0 = bx(c) + 160 + (b / 2) * S
    fx = lambda y: fx0 + y * S
    fy = by
    label(fx(0), sy0 - (hf + D / 2) * S - 20, "FRONT (from the nose)", "middle", 12, INK, weight=600)
    rect(fx(-b / 2), fy(t / 2), b * S, t * S, SUB["wing"])
    rect(fx(-pod[1] / 2), fy(pod_z + pod[2]), pod[1] * S, pod[2] * S, SUB["pod"])
    for sgn in (1, -1):
        rect(fx(sgn * yf - tube_od / 2), fy(tube_l / 2), tube_od * S, tube_l * S, SUB["fins"])
        for s2 in (1, -1):
            W(f'<circle cx="{fx(sgn*yf):.1f}" cy="{fy(s2*zm):.1f}" r="{mot_d/2*S:.1f}" fill="{SUB["propulsion"]}" fill-opacity="0.35" stroke="{INK}" stroke-width="1.5"/>')
            W(f'<circle cx="{fx(sgn*yf):.1f}" cy="{fy(s2*zm):.1f}" r="{D/2*S:.1f}" fill="none" stroke="{INK3}" stroke-width="1" stroke-dasharray="6 4"/>')
    cg_symbol(fx(0), fy(zcg))
    dim(fx(b / 2) + 30, fy(zm), fx(b / 2) + 30, fy(-zm), f"motors ±{zm*1000:.0f} mm", fx(b / 2) + 38, fy(0) + 4, "start")
    axis(fx(-b / 2) - 20, by(-hf) - 80, 26, 0, "+y")
    axis(fx(-b / 2) - 20, by(-hf) - 80, 0, -26, "+z")

    # ---------------- scale bar, legend
    sb_y = by(-hf - D / 2) + 60
    W(f'<g stroke="{INK}" stroke-width="1"><line x1="60" y1="{sb_y}" x2="{60+0.5*S}" y2="{sb_y}"/>'
      f'<line x1="60" y1="{sb_y-4}" x2="60" y2="{sb_y+4}"/><line x1="{60+0.5*S}" y1="{sb_y-4}" x2="{60+0.5*S}" y2="{sb_y+4}"/></g>')
    label(60, sb_y + 16, "0 — 500 mm", size=11, color=INK, mono=True)
    lx = 60 + 0.5 * S + 40
    for k, name in (("wing", "wing"), ("fins", "fins + motor tubes"), ("pod", "pod"), ("propulsion", "propulsion"), ("landing", "feet")):
        W(f'<rect x="{lx}" y="{sb_y-8}" width="14" height="14" fill="{SUB[k]}" fill-opacity="0.35" stroke="{INK}" stroke-width="1"/>')
        label(lx + 20, sb_y + 4, name, size=11, color=INK2)
        lx += 20 + 7.5 * len(name) + 24
    label(lx, sb_y + 4, "dashed: prop disc, hidden spar, elevon hinge  ·  frame: x aft from the wing LE, y right, z up (cruise)", size=11, color=INK3)

    width, height = int(fx(b / 2) + 140), int(sb_y + 40)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
           f'role="img" aria-label="K09-L general arrangement, three views to scale">\n' + "\n".join(out) + "\n</svg>\n")
    (HERE / "ga-3view.svg").write_text(svg, encoding="utf-8")
    print(f"ga-3view.svg: {width} x {height} px, 1 m = {S:.0f} px")


if __name__ == "__main__":
    main()
