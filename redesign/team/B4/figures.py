"""B4 figures (standalone SVG, design-system light values), drawn from props.py and params.json.

Run:  python -I redesign/team/B4/figures.py   -> out/fig-b4-01-cruise-power.svg, out/fig-b4-02-slipstream.svg
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import props as pp  # noqa: E402

PAR = json.loads((HERE.parents[1] / "params" / "params.json").read_text(encoding="utf-8"))
RES = json.loads((HERE / "out" / "props_results.json").read_text(encoding="utf-8"))
FG, FG2, FG3, LINE, LINE3, ACC, HL = "#121619", "#4B5563", "#6B7280", "#E3E7ED", "#9AA4B1", "#1F5FC7", "#C2540A"
SANS = "IBM Plex Sans, system-ui, sans-serif"
MONO = "IBM Plex Mono, monospace"


def v(path):
    d = PAR
    for k in path.split("."):
        d = d[k]
    return d["value"]


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="{SANS}">\n' + "\n".join(body) + "\n</svg>\n")


def text(x, y, s, size=12, fill=FG2, anchor="start", mono=False, weight=500):
    fam = MONO if mono else SANS
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-family="{fam}" font-weight="{weight}">{s}</text>')


def fig_cruise():
    m, g, rho = v("requirements.mtow_gate_kg"), v("env.g_ms2"), v("env.rho_kgm3")
    ld = v("performance.ld_cruise")
    mot, esc_w = pp._motor(*(pp.kit.value(pp.E1_MOTOR[k]) for k in ("kv", "rm", "i0", "esc", "pack", "tcu")),
                           hot=False)
    W, H, x0, y0, pw, ph = 1200, 560, 90, 40, 900, 440
    Vs = [12 + 0.5 * i for i in range(17)]
    lo, hi = 100, 500

    def X(V):
        return x0 + (V - 12) / 8 * pw

    def Y(P):
        return y0 + ph - (P - lo) / (hi - lo) * ph
    b = [f'<rect x="{x0}" y="{y0}" width="{pw}" height="{ph}" fill="none" stroke="{LINE3}" stroke-width="1"/>']
    for P in range(lo, hi + 1, 50):
        b.append(f'<line x1="{x0}" x2="{x0 + pw}" y1="{Y(P):.1f}" y2="{Y(P):.1f}" stroke="{LINE}" stroke-width="1"/>')
        b.append(text(x0 - 8, Y(P) + 4, f"{P}", anchor="end", mono=True, fill=FG3))
    for V in range(12, 21, 2):
        b.append(text(X(V), y0 + ph + 20, f"{V}", anchor="middle", mono=True, fill=FG3))
    b.append(text(x0 + pw / 2, y0 + ph + 44, "airspeed (m/s)", anchor="middle"))
    b.append(text(20, y0 + ph / 2, "pack power, 4 motors (W)", anchor="middle").replace(
        "<text", f'<text transform="rotate(-90 20 {y0 + ph / 2})"'))
    for prop in pp.PROPS:
        pts = []
        for V in Vs:
            T = m * g / ld / 4 * (1 + 0.0 * V)        # thrust = drag at constant L/D (B1 refines the polar)
            c = pp._cruise(prop, T, V, rho, mot, esc_w)
            pts.append((X(V), Y(4 * c["in_w"])))
        col, wd = (ACC, 2.5) if prop == pp.SEL else ((FG, 2) if prop == pp.OLD else (LINE3, 1.5))
        b.append(f'<polyline fill="none" stroke="{col}" stroke-width="{wd}" points="' +
                 " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '"/>')
        b.append(text(pts[-1][0] + 8, pts[-1][1] + 4, prop, fill=col if col != LINE3 else FG3, mono=True))
    xc = X(v("performance.cruise_ms"))
    b.append(f'<line x1="{xc:.1f}" x2="{xc:.1f}" y1="{y0}" y2="{y0 + ph}" stroke="{LINE3}" stroke-dasharray="6 4"/>')
    b.append(text(xc + 6, y0 + 16, f"cruise {v('performance.cruise_ms'):.0f} m/s", fill=FG3))
    return svg(W, H, b)


def fig_slipstream():
    """Side view at the fin station (y = 0.32 m): wing section, fin, tube, props, hover slipstream edge."""
    W, H, s = 1200, 640, 850.0                        # px per metre
    ox, oz = 330, 320

    def P(x, z):
        return ox + x * s, oz - z * s
    D = v("propulsion.prop_diameter_m")
    Rr = D / 2
    xp, zm = v("propulsion.stations.x_prop_plane_m"), v("propulsion.stations.z_m")
    c, fe = v("wing.chord_m"), v("wing.elevon.chord_frac")
    mix = 0.08
    b = []
    # fin (ghost) and tube
    xt, dt = v("propulsion.stations.x_mount_m"), v("fins.tube.od_m")
    x1, z1 = P(xt, zm)
    x2, z2 = P(v("fins.te_x_m"), -zm)
    b.append(f'<rect x="{x1:.1f}" y="{z1:.1f}" width="{x2 - x1:.1f}" height="{z2 - z1:.1f}" fill="{LINE}" '
             f'stroke="{LINE3}" stroke-width="0.75"/>')
    tx, tz = P(xt - dt / 2, zm)
    b.append(f'<rect x="{tx:.1f}" y="{tz:.1f}" width="{dt * s:.1f}" height="{2 * zm * s:.1f}" fill="{LINE3}"/>')
    # wing section (S5010 coordinates from B2) and elevon
    afu, afl = pp._airfoil_surfaces()
    up = [P(c * xx, c * zz) for xx, zz in afu]
    lo = [P(c * xx, c * zz) for xx, zz in reversed(afl)]
    b.append('<polygon fill="#D6DCE4" stroke="' + FG + '" stroke-width="1.5" points="' +
             " ".join(f"{x:.1f},{y:.1f}" for x, y in up + lo) + '"/>')
    hx, hz = P(c * (1 - fe), 0)
    for d in (-25, 25):
        ex, ez = P(c * (1 - fe) + c * fe * math.cos(math.radians(d)), -c * fe * math.sin(math.radians(d)))
        b.append(f'<line x1="{hx:.1f}" y1="{hz:.1f}" x2="{ex:.1f}" y2="{ez:.1f}" stroke="{HL}" stroke-width="2.5"/>')
    b.append(text(hx + 10, hz + 52, "elevon ±25°", fill=HL))
    # props and hover slipstream (contracting), with the mixing-layer edge
    for sz in (1, -1):
        a, bb = P(xp, sz * zm + Rr), P(xp, sz * zm - Rr)
        b.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{bb[0]:.1f}" y2="{bb[1]:.1f}" stroke="{FG}" stroke-width="3"/>')
        for side in (1, -1):
            pts, pts2 = [], []
            for i in range(61):
                xd = 0.5 * i / 60
                r = pp._r_slip(xd, Rr)
                pts.append(P(xp + xd, sz * zm + side * r))
                pts2.append(P(xp + xd, sz * zm + side * (r + mix * xd)))
            b.append(f'<polyline fill="none" stroke="{ACC}" stroke-width="1.5" points="' +
                     " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '"/>')
            b.append(f'<polyline fill="none" stroke="{ACC}" stroke-width="0.75" stroke-dasharray="6 4" points="' +
                     " ".join(f"{x:.1f},{y:.1f}" for x, y in pts2) + '"/>')
    gap = RES["CALC-B4-WAKE"]["hover_gap_elevon_m"]
    gx, gz = P(c + 0.02, 0.0279)
    gx2, gz2 = P(c + 0.02, 0.0279 + gap)
    b.append(f'<line x1="{gx:.1f}" y1="{gz:.1f}" x2="{gx2:.1f}" y2="{gz2:.1f}" stroke="{ACC}" stroke-width="1.25"/>')
    b.append(text(gx + 8, (gz + gz2) / 2 + 4, f"{gap * 1000:.0f} mm clear", fill=ACC, mono=True))
    # pitot (pod nose, y = 0, drawn projected)
    tip_x, tip_z = RES["CALC-B4-PITOT"]["tip_x_m"], RES["CALC-B4-PITOT"]["tip_z_m"]
    px, pz = P(tip_x, tip_z)
    px2, pz2 = P(v("pod.x_le_m"), tip_z)
    b.append(f'<line x1="{px:.1f}" y1="{pz:.1f}" x2="{px2:.1f}" y2="{pz2:.1f}" stroke="{HL}" stroke-width="2"/>')
    b.append(text(px - 6, pz - 8, "pitot (y = 0)", fill=HL, anchor="end"))
    b.append(text(P(xp, zm + Rr)[0], P(xp, zm + Rr)[1] - 10, "prop plane", fill=FG3, anchor="middle"))
    b.append(text(P(0.42, 0.20)[0], P(0.42, 0.20)[1], "hover wake →", fill=ACC))
    # scale bar
    sx, sy = 40, H - 30
    b.append(f'<line x1="{sx}" y1="{sy}" x2="{sx + 0.1 * s:.1f}" y2="{sy}" stroke="{FG}" stroke-width="1"/>')
    b.append(text(sx, sy - 6, "0 — 100 mm", size=11, mono=True, fill=FG3))
    return svg(W, H, b)


if __name__ == "__main__":
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    (out / "fig-b4-01-cruise-power.svg").write_text(fig_cruise(), encoding="utf-8")
    (out / "fig-b4-02-slipstream.svg").write_text(fig_slipstream(), encoding="utf-8")
    print("wrote out/fig-b4-01-cruise-power.svg, out/fig-b4-02-slipstream.svg")
