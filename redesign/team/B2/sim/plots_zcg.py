"""B2-R4 figures (design-system palette as plots_sim.py): stall vs CG x and height; CR-B1-23 CLmax waterfall.

    python redesign/team/B2/sim/plots_zcg.py      -> team/B2/sim/fig/B2-R4-0*.svg   (matplotlib: run without -I)
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG = HERE / "fig"
FIG.mkdir(exist_ok=True)
Z = json.loads((HERE / "out" / "stall_zcg.json").read_text())
CL = {n["id"]: n for n in json.loads((HERE / "claims.sim.json").read_text())["nodes"]}
P = json.loads((HERE.parents[2] / "params" / "params.json").read_text(encoding="utf-8"))

FG, FG2, FG3, LINE3, ACCENT, FAIL = "#121619", "#4B5563", "#6B7280", "#9AA4B1", "#1F5FC7", "#B42323"
plt.rcParams.update({"font.family": ["IBM Plex Sans", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": LINE3,
                     "axes.labelcolor": FG2, "xtick.color": FG3, "ytick.color": FG3, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": "#E3E7ED", "grid.linewidth": 0.6,
                     "svg.fonttype": "none", "figure.facecolor": "none", "axes.facecolor": "none"})


def fig_stall_xz():
    rho, g = P["env"]["rho_kgm3"]["value"], P["env"]["g_ms2"]["value"]
    S = P["wing"]["span_m"]["value"] * P["wing"]["chord_m"]["value"]
    m = P["requirements"]["mtow_gate_kg"]["value"]
    xr = P["cg"]["x_range_m"]["value"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.axvspan(xr[0] * 1000, xr[1] * 1000, color="#E3E7ED", alpha=0.6, lw=0)
    ax.annotate("D-62 CG range", (xr[0] * 1000 + 0.1, 12.13), color=FG3, fontsize=8)
    shades = {0.0: FG3, 0.010: FG2, 0.0185: ACCENT, 0.025: FG}
    for j, z in enumerate(Z["z_grid"]):
        xs = [x * 1000 for x in Z["x_grid"]]
        vs = [math.sqrt(2 * m * g / (rho * S * Z["clmax"][i][j])) for i in range(len(Z["x_grid"]))]
        ax.plot(xs, vs, color=shades[z], lw=1.9 if z == 0.0185 else 1.1, ls="-" if z else "--", marker="o", ms=3,
                label=f"CG height {z * 1000:g} mm" + (" (A3, target)" if z == 0.0185 else ""))
    ax.axhline(P["requirements"]["stall_max_ms"]["value"], color=FAIL, lw=1.0)
    ax.annotate("R-STALL 12 m/s", (44.7, 12.005), color=FAIL, fontsize=8)
    ax.set_xlabel("CG x from the root LE (mm)")
    ax.set_ylabel("trimmed stall at 2.6 kg (m/s)")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG / "B2-R4-01-stall-xz.svg")


def fig_waterfall():
    w = Z["recon"]
    b1 = 0.862248
    fwd = CL["CL-B2R3-CLMAX-FWD"]["value"]
    steps = [("B1 run", b1), ("B2 model,\nB1 set-up", w["W0"]["CLmax_trim"]), ("B2 raw\nXFOIL table", w["W1"]["CLmax_trim"]),
             ("clmax\nenvelope", w["W2"]["CLmax_trim"]), ("viscous cm\ntrim", w["W3"]["CLmax_trim"]),
             ("props + pod\nNP shift", w["W4"]["CLmax_trim"]), ("forward CG\n0.0466", fwd)]
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    prev = None
    for i, (lab, v) in enumerate(steps):
        if prev is None or i == len(steps) - 1:
            ax.bar(i, v - 0.70, bottom=0.70, color=ACCENT if i == len(steps) - 1 else FG2, width=0.6)
        else:
            lo, hi = sorted((prev, v))
            ax.bar(i, hi - lo, bottom=lo, color=FG3 if v < prev else LINE3, width=0.6)
        ax.annotate(f"{v:.3f}", (i, max(v, prev or v) + 0.003), ha="center", fontsize=8, color=FG)
        prev = v
    ax.set_xticks(range(len(steps)), [s[0] for s in steps], fontsize=8)
    ax.set_ylim(0.70, 0.88)
    ax.set_ylabel("trimmed CLmax")
    fig.tight_layout()
    fig.savefig(FIG / "B2-R4-02-clmax-waterfall.svg")


if __name__ == "__main__":
    fig_stall_xz()
    fig_waterfall()
    print("figures written")
