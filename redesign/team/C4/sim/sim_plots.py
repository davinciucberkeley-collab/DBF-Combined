"""C4 simulation-round figures (design-system style: SVG, transparent, IBM Plex, ink + accent, red only for a FAIL
limit). Run after sim_fin.py:  python redesign/team/C4/sim/sim_plots.py (not -I: matplotlib needs user site-packages)  ->  team/C4/fig-c4-s*.svg"""
import json
import logging
import math
from pathlib import Path

import matplotlib
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FIG = HERE.parent
INK, FG2, FG3, LINE = "#121619", "#4B5563", "#6B7280", "#CBD2DB"
ACC, ACC_L, HL, FAIL = "#1F5FC7", "#A9C3EE", "#C2540A", "#B42323"
plt.rcParams.update({
    "font.family": ["IBM Plex Sans", "Segoe UI", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": LINE,
    "axes.labelcolor": FG2, "xtick.color": FG3, "ytick.color": FG3, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": "#E3E7ED", "grid.linewidth": 0.6,
    "axes.titlesize": 10, "axes.titleweight": "semibold", "axes.titlecolor": INK, "legend.frameon": False,
    "legend.fontsize": 8, "savefig.transparent": True, "svg.fonttype": "none", "lines.linewidth": 1.5})

R = json.loads((OUT / "sim_results.json").read_text())
CL = json.loads((HERE.parent / "claims.sim.json").read_text())
NODES = {n["id"]: n for n in CL["nodes"]}


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name)
    plt.close(fig)
    print("wrote", FIG / name)


def limit(ax, y, text, fail=False, x=0.99, va="bottom"):
    ax.axhline(y, color=FAIL if fail else FG3, lw=1.0, ls=(0, (6, 4)))
    ax.text(x, y, " " + text, transform=ax.get_yaxis_transform(), ha="right", va=va, fontsize=8,
            color=FAIL if fail else FG3)


def fig_face():
    F = R["CALC-C4-SIM-FACE"]
    sf = NODES["CALC-C4-SIM-FACE"]["input_values"]["sf"]
    s_all = NODES["CALC-C4-SIM-FACE"]["input_values"]["s_face"] / sf / 1e6        # limit-load allowable, MPa
    h = [F["levels"][k][1] * 1000 for k in ("1", "2", "3")]
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.6))
    for var, col, lab in (("drawn", ACC, "D5 shoe as drawn"), ("proposed", HL, "cheeks to |z| 0.171 m")):
        hs = np.array(F[f"hs_{var}_lim_pa"]) / 1e6
        axs[0].plot(h, hs, color=col, marker="o", ms=4, label=f"{lab}, 3-D hot-spot")
        axs[0].plot([0], [F[f"hs_{var}_ext_lim_pa"] / 1e6], color=col, marker="D", ms=5, ls="none")
        axs[0].axhline(F[f"plate_hs_{var}_lim_pa"] / 1e6, color=col, lw=1.0, ls=":")
        axs[1].plot(h, np.array(F[f"peak_{var}_lim_pa"]) / 1e6, color=col, marker="s", ms=4, label=f"{lab}, raw peak")
        axs[1].axhline(F[f"plate_peak_{var}_lim_pa"] / 1e6, color=col, lw=1.0, ls=":")
    limit(axs[0], s_all, f"allowable at limit {s_all:.2f} MPa (10 MPa / {sf})", x=0.99)
    limit(axs[1], s_all, f"allowable at limit {s_all:.2f} MPa", x=0.99)
    axs[0].set_title("Face hot-spot at the shoe edge, L4 limit")
    axs[1].set_title("Largest face element outside the shoe, L4 limit")
    for ax in axs:
        ax.set_xlabel("element size in the tip box (mm); diamond = Richardson, dotted = R4 shell")
        ax.set_ylabel("in-plane face stress (MPa)")
        ax.set_xlim(-0.1, 2.2)
        ax.set_ylim(bottom=0)
        ax.legend(loc="upper left")
    save(fig, "fig-c4-s1-face-convergence.svg")


def fig_field():
    Fd = json.loads((OUT / "field_L2.json").read_text())
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.9), sharey=True)
    vmax = max(max(Fd[v]["s"]) for v in Fd) / 1e6
    for ax, var, title in zip(axs, ("drawn", "proposed"), ("D5 shoe as drawn", "cheeks to |z| 0.171 m (CR-C4-30)")):
        f = Fd[var]
        x, z, s = np.array(f["x"]) * 1000, np.array(f["z"]) * 1000, np.array(f["s"]) / 1e6
        tc = ax.tricontourf(x, z, s, levels=np.linspace(0, vmax, 15), cmap="Blues")
        poly = np.array(f["fin_poly"]) * 1000
        ax.plot(np.r_[poly[:, 0], poly[0, 0]], np.r_[poly[:, 1], poly[0, 1]], color=FG2, lw=0.8)
        for (xa, za, xb, zb) in f["shoes"]:
            ax.add_patch(plt.Rectangle((xa * 1000, za * 1000), (xb - xa) * 1000, (zb - za) * 1000, fill=False,
                                       ec=HL, lw=1.2))
        ax.set_aspect("equal")
        ax.set_title(title)
        ax.set_xlabel("x aft (mm)")
        ax.grid(False)
    axs[0].set_ylabel("z from the wing (mm)")
    cb = fig.colorbar(tc, ax=axs, shrink=0.85, pad=0.02)
    cb.set_ticks(np.arange(0, vmax + 0.01, 1.0))
    cb.set_label("face stress, L4 limit, + side (MPa)")
    fig.savefig(FIG / "fig-c4-s2-face-field.svg")
    plt.close(fig)
    print("wrote", FIG / "fig-c4-s2-face-field.svg")


def fig_modes():
    M = R["CALC-C4-SIM-MODES"]
    iv = NODES["CALC-C4-SIM-MODES"]["input_values"]
    rpm = {"hover": iv["rpm_h"], "cruise": iv["rpm_c"]}
    sep = iv["sep_min"]
    fig, ax = plt.subplots(figsize=(9.6, 3.6))
    nd = {s: [M[f"ndof_{s}_L{lv}"] for lv in (1, 2, 3)] for s in ("up", "lo")}
    for s, col, lab in (("up", ACC, "upper station"), ("lo", HL, "lower station")):
        ax.plot(nd[s], M[f"f1_{s}"], color=col, marker="o", ms=4, label=f"{lab}, 3-D")
        ax.axhline(M[f"f1_{s}_ext"], color=col, lw=0.8, ls=(0, (2, 2)))
        ax.axhline(M[f"plate_f1_{s}_a3"], color=col, lw=1.0, ls=":")
    for name, r in rpm.items():
        for n_, tag in ((1, "1P"), (2, "2P")):
            f = r / 60 * n_
            ax.axhspan(f * (1 - sep), f * (1 + sep), color=FAIL, alpha=0.06, lw=0)
            ax.axhline(f, color=FAIL, lw=0.8)
            ax.text(1.0, f, f" {tag} {name} {f:.0f} Hz", transform=ax.get_yaxis_transform(), fontsize=7.5,
                    color=FAIL, va="center")
    ax.set_xscale("log")
    ax.set_xlabel("degrees of freedom (meshes 8 / 5.7 / 4 mm); dashed = Richardson, dotted = R4 shell with A3 masses")
    ax.set_ylabel("first station mode (Hz)")
    ax.set_title(f"Station modes vs rotor forcing ± {sep:.0%}")
    ax.set_ylim(60, max(M["f1_up_ext"], M["f1_lo_ext"]) * 1.25)
    ax.legend(loc="lower left")
    save(fig, "fig-c4-s3-modes.svg")


def fig_bench():
    B = R["CALC-C4-SIM-BENCH"]
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    e = [B["err_coarse"], B["err_mid"], B["err_fine"]]
    ax.plot([2, 4, 8], [abs(v) * 100 for v in e], color=ACC, marker="o", ms=4, label="SU2 hex8, |error|")
    ax.axhline(abs(B["err_extrap"]) * 100, color=ACC, lw=0.8, ls=(0, (2, 2)), label="Richardson extrapolated")
    limit(ax, 1.0, "1 % acceptance")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("elements through the depth")
    ax.set_ylabel("tip deflection error vs beam theory (%)")
    ax.set_title("SU2 ELASTICITY benchmark")
    ax.legend(loc="lower left")
    save(fig, "fig-c4-s4-su2-bench.svg")


if __name__ == "__main__":
    fig_face()
    fig_field()
    fig_modes()
    fig_bench()
