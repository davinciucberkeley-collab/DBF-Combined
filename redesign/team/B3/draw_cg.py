"""B3 (R5): draw the chordwise station diagram (NP, CG limits of record, D-62 target, A3 CG) from results/verify.json
and params.json (V1 limits with the CG height; the R4 z = 0 limits and the D-59 pack cases are retired).

Run: python -I redesign/team/B3/draw_cg.py  ->  team/B3/fig-b3-cg-stations.svg   (design-system/diagram-style.md)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = json.loads((HERE / "results" / "verify.json").read_text())
PAR = json.loads((HERE.parents[1] / "params" / "params.json").read_text())
FG, FG2, FG3, LINE, ACC, HI, FAIL = "#121619", "#4B5563", "#6B7280", "#CBD2DB", "#1F5FC7", "#C2540A", "#B42323"


def pv(path):
    d = PAR
    for k in path.split("."):
        d = d[k]
    return d["value"]


c = pv("wing.chord_m")
xt_tube, xp, pod_le, pod_l = pv("fins.tube.x_m"), pv("propulsion.stations.x_prop_plane_m"), pv("pod.x_le_m"), pv("pod.size_m")[0]
cgv, env = V["CALC-B3-V-CG"], V["CALC-B3-V-NP-CL"]
lim = {"x_fwd": cgv["x_fwd_gate"], "x_aft": env["x_aft_env"], "x_target": pv("cg.x_target_m")}
x_a3, xnp_env, xa = cgv["x_a3"], env["xnp_env"], cgv["xnp_aero"]
W, H, X0, X1 = 1200, 320, 80, 1120
XMIN, XMAX = -0.12, 0.34


def X(x):
    return X0 + (x - XMIN) / (XMAX - XMIN) * (X1 - X0)


mono = 'font-family="IBM Plex Mono, monospace"'
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, system-ui">']
s.append(f'<rect x="{X(0):.1f}" y="120" width="{X(c) - X(0):.1f}" height="22" fill="none" stroke="{FG}" stroke-width="1.5" rx="2"/>')
s.append(f'<text x="{X(c / 2):.1f}" y="135" font-size="12" fill="{FG2}" text-anchor="middle">wing chord {c:.2f} m (S5010)</text>')
s.append(f'<rect x="{X(pod_le):.1f}" y="100" width="{X(pod_le + pod_l) - X(pod_le):.1f}" height="14" fill="none" stroke="{FG3}" stroke-width="0.75" stroke-dasharray="4 3"/>')
s.append(f'<text x="{X(pod_le):.1f}" y="95" font-size="11" fill="{FG3}">pod {pod_le:+.3f}…{pod_le + pod_l:+.3f}</text>')
s.append(f'<line x1="{X(xt_tube):.1f}" y1="160" x2="{X(c):.1f}" y2="160" stroke="{FG3}" stroke-width="0.75" stroke-dasharray="6 4"/>')
s.append(f'<circle cx="{X(xt_tube):.1f}" cy="160" r="5" fill="none" stroke="{FG3}"/>')
s.append(f'<text x="{X(xt_tube) + 10:.1f}" y="176" font-size="11" fill="{FG3}">motor tube {xt_tube:+.3f}, half-fins to the TE</text>')
s.append(f'<line x1="{X(xp):.1f}" y1="150" x2="{X(xp):.1f}" y2="170" stroke="{FG3}" stroke-width="2"/>')
s.append(f'<text x="{X(xp):.1f}" y="196" font-size="11" fill="{FG3}" text-anchor="middle">props {xp:+.3f}</text>')
s.append(f'<rect x="{X(lim["x_fwd"]):.1f}" y="96" width="{X(lim["x_aft"]) - X(lim["x_fwd"]):.1f}" height="70" fill="#E6EEFB" fill-opacity="0.8" stroke="{ACC}" stroke-width="1"/>')
lab = [(lim["x_fwd"], f'fwd {lim["x_fwd"]:.4f}', ACC, 72), (lim["x_aft"], f'aft {lim["x_aft"]:.4f}', ACC, 54),
       (lim["x_target"], f'target {lim["x_target"]:.4f}', ACC, 36),
       (xnp_env, f'NP at 1.3 Vs, z {pv("cg.z_target_m"):+.4f}: {xnp_env:.4f}', FG, 236),
       (xa, f'NP wing+fins (alpha 4) {xa:.4f}', FG3, 256),
       (x_a3, f'A3-R6a CG (D-47 bay) {x_a3:.4f}', FAIL if x_a3 > lim["x_aft"] else HI, 216)]
for x, t, col, y in lab:
    y0 = 96 if y < 96 else 166
    s.append(f'<line x1="{X(x):.1f}" y1="{y0}" x2="{X(x):.1f}" y2="{y + 4 if y < 96 else y - 14}" stroke="{col}" stroke-width="1.25"/>')
    s.append(f'<text x="{X(x):.1f}" y="{y}" font-size="12" fill="{col}" text-anchor="middle" {mono}>{t}</text>')
s.append(f'<line x1="{X0}" y1="296" x2="{X1}" y2="296" stroke="{LINE}" stroke-width="1"/>')
for i in range(-12, 35, 4):
    x = i / 100
    s.append(f'<line x1="{X(x):.1f}" y1="292" x2="{X(x):.1f}" y2="300" stroke="{LINE}"/>')
    s.append(f'<text x="{X(x):.1f}" y="314" font-size="11" fill="{FG3}" text-anchor="middle" {mono}>{x:+.2f}</text>')
s.append(f'<text x="{X1}" y="288" font-size="11" fill="{FG3}" text-anchor="end">x aft of wing LE, m</text>')
s.append("</svg>")
(HERE / "fig-b3-cg-stations.svg").write_text("\n".join(s), encoding="utf-8")
print("wrote fig-b3-cg-stations.svg")
