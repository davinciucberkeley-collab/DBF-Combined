"""B3: draw the chordwise station diagram (NP, CG limits, current CG) from results/sc_results.json.

Run: python -I redesign/team/B3/draw_cg.py  ->  team/B3/fig-b3-cg-stations.svg   (design-system/diagram-style.md)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = json.loads((HERE / "results" / "sc_results.json").read_text())
FG, FG2, FG3, LINE, ACC, HI, FAIL = "#121619", "#4B5563", "#6B7280", "#CBD2DB", "#1F5FC7", "#C2540A", "#B42323"

c = 0.30
lim = R["CALC-B3-CG-LIMITS"]
np_ = R["CALC-B3-NP"]
now = R["CALC-B3-CG-CHECK"]["x_now"]
W, H, X0, X1 = 1200, 300, 80, 1120


def X(x):                                   # x from -0.12 to 0.32 m
    return X0 + (x + 0.12) / 0.44 * (X1 - X0)


s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, system-ui">']
# wing chord bar and fin bar
s.append(f'<rect x="{X(0):.1f}" y="120" width="{X(c) - X(0):.1f}" height="22" fill="none" stroke="{FG}" stroke-width="1.5" rx="2"/>')
s.append(f'<text x="{X(0.15):.1f}" y="135" font-size="12" fill="{FG2}" text-anchor="middle">wing chord 0.30 m</text>')
s.append(f'<line x1="{X(-0.10):.1f}" y1="160" x2="{X(0.30):.1f}" y2="160" stroke="{FG3}" stroke-width="0.75" stroke-dasharray="6 4"/>')
s.append(f'<text x="{X(-0.10):.1f}" y="176" font-size="11" fill="{FG3}">fin −0.10…0.30 (tube at −0.10)</text>')
s.append(f'<circle cx="{X(-0.15):.1f}" cy="160" r="4" fill="none" stroke="{FG3}"/><text x="{X(-0.15):.1f}" y="196" font-size="11" fill="{FG3}" text-anchor="middle">props −0.15</text>')
# CG range band
s.append(f'<rect x="{X(lim["x_fwd"]):.1f}" y="96" width="{X(lim["x_aft"]) - X(lim["x_fwd"]):.1f}" height="70" fill="#E6EEFB" stroke="{ACC}" stroke-width="1"/>')
lab = [(lim["x_fwd"], f'fwd {lim["x_fwd"]:.3f}', ACC, 70), (lim["x_aft"], f'aft {lim["x_aft"]:.3f}', ACC, 52),
       (lim["x_target"], f'target {lim["x_target"]:.3f}', ACC, 34),
       (np_["xnp"], f'NP {np_["xnp"]:.3f}', FG, 230), (np_["xnp"] - np_["dx_props"] - np_["dx_pod"],
                                                     f'NP wing+fins {np_["xnp"] - np_["dx_props"] - np_["dx_pod"]:.3f}', FG3, 250),
       (now, f'CG now (A3) {now:.3f}', FAIL, 212)]
for x, t, col, y in lab:
    s.append(f'<line x1="{X(x):.1f}" y1="{96 if y < 96 else 166}" x2="{X(x):.1f}" y2="{y + 4 if y < 96 else y - 14}" stroke="{col}" stroke-width="1.25"/>')
    s.append(f'<text x="{X(x):.1f}" y="{y}" font-size="12" fill="{col}" text-anchor="middle" font-family="IBM Plex Mono, monospace">{t}</text>')
# axis
s.append(f'<line x1="{X0}" y1="280" x2="{X1}" y2="280" stroke="{LINE}" stroke-width="1"/>')
for i in range(-12, 33, 4):
    x = i / 100
    s.append(f'<line x1="{X(x):.1f}" y1="276" x2="{X(x):.1f}" y2="284" stroke="{LINE}"/>')
    s.append(f'<text x="{X(x):.1f}" y="296" font-size="11" fill="{FG3}" text-anchor="middle" font-family="IBM Plex Mono, monospace">{x:+.2f}</text>')
s.append(f'<text x="{X1}" y="270" font-size="11" fill="{FG3}" text-anchor="end">x aft of wing LE, m</text>')
s.append("</svg>")
(HERE / "fig-b3-cg-stations.svg").write_text("\n".join(s), encoding="utf-8")
print("wrote fig-b3-cg-stations.svg")
