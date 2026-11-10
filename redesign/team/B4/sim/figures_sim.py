"""B4 simulation-round figures (matplotlib, design-system light values, SVG, 1200 px master width).

Run after sim_claims.py:  python redesign/team/B4/sim/figures_sim.py   -> out/fig-b4-sim-0*.svg
"""
import csv
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE / "bemt"))
import props as pp  # noqa: E402
import bemt  # noqa: E402

OUT = HERE / "out"
RES = json.loads((OUT / "sim_results.json").read_text(encoding="utf-8"))
CFD = json.loads((HERE / "cfd" / "results.json").read_text(encoding="utf-8"))
FG, FG2, FG3, LINE, LINE3 = "#121619", "#4B5563", "#6B7280", "#E3E7ED", "#9AA4B1"
ACC, HL, FAIL, CHK = "#1F5FC7", "#C2540A", "#B42323", "#0E6F74"
plt.rcParams.update({
    "font.family": ["IBM Plex Sans", "Segoe UI", "DejaVu Sans"], "font.size": 12, "axes.edgecolor": LINE3,
    "axes.linewidth": 1.0, "axes.labelcolor": FG2, "xtick.color": FG3, "ytick.color": FG3, "axes.grid": True,
    "grid.color": LINE, "grid.linewidth": 1.0, "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "legend.fontsize": 11, "svg.fonttype": "none", "figure.facecolor": "none",
    "axes.facecolor": "none", "savefig.transparent": True, "lines.linewidth": 1.5})
IN = 0.0254


def save(fig, name):
    fig.savefig(OUT / name, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT / name)


def fig_bemt():
    rows = [r for r in pp.UIUC if r["prop"] == "11x5.5E" and r["kind"] == "tunnel"]
    Js = [0.02 * i for i in range(1, 33)]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    per3 = [r for r in pp.DATA["11x5.5E"] if r["rpm"] == 6000]
    for foil, col, ls, lab in (("naca4412", ACC, "-", "BEMT, NACA 4412 (baseline)"),
                               ("naca3410", ACC, "--", "BEMT, NACA 3410 (low camber)")):
        b = [bemt.rotor("11x5.5E", 6000, V=J * 100 * 11 * IN, N=40, foil=foil) for J in Js]
        ax[0].plot(Js, [x["Ct"] for x in b], color=col, ls=ls, label=lab)
        ax[1].plot(Js, [x["eta"] for x in b], color=col, ls=ls)
    ax[0].plot([r["J"] for r in per3], [r["Ct"] for r in per3], color=FG3, lw=1.0, label="APC PER3 (prediction)")
    ax[1].plot([r["J"] for r in per3], [r["Ct"] * r["J"] / r["Cp"] if r["Cp"] > 0 else 0 for r in per3], color=FG3,
               lw=1.0)
    ax[0].plot([r["J"] for r in rows], [r["Ct"] for r in rows], "o", ms=5, mfc="none", mec=HL,
               label="UIUC measured, 6 000 rpm")
    ax[1].plot([r["J"] for r in rows], [r["eta"] for r in rows], "o", ms=5, mfc="none", mec=HL)
    st = [r for r in pp.UIUC if r["prop"] == "11x5.5E" and r["kind"] == "static"]
    ax[0].plot([0] * len(st), [r["Ct"] for r in st], "o", ms=5, mfc="none", mec=HL)
    ax[0].set(xlabel="advance ratio J", ylabel="thrust coefficient Ct", xlim=(0, 0.66), ylim=(-0.01, 0.12))
    ax[1].set(xlabel="advance ratio J", ylabel="propulsive efficiency η", xlim=(0, 0.66), ylim=(0, 0.8))
    ax[0].legend(loc="lower left")
    jc = next(n["value"] for n in json.loads((HERE.parent / "claims.json").read_text(encoding="utf-8"))["nodes"]
              if n["id"] == "CL-B4-CRUISE-J")
    ax[0].axvline(jc, color=LINE3, lw=0.75, ls=(0, (6, 4)))
    ax[0].text(jc - 0.005, 0.105, f"cruise J {jc:.2f}\n(11×5.5MR)", color=FG3, fontsize=11, ha="right")
    save(fig, "fig-b4-sim-01-bemt-validation.svg")


def fig_conv():
    fig, ax = plt.subplots(1, 3, figsize=(12, 4.0))
    for a, (st, title) in zip(ax, (("val_lam", "Cylinder, Re 40 (validation)"), ("hov_sa", "Tube + board, 10 m/s"),
                                   ("cru_sa", "Tube + board, 16 m/s"))):
        s = CFD["studies"].get(st)
        if not s:
            continue
        cells = [CFD["cases"][f"{st}_L{lv}"]["cells"] for lv in s["levels"]]
        h = [c ** -0.5 / cells[0] ** -0.5 for c in cells]
        a.plot(h, s["cd_fine_mid_coarse"], "o-", color=ACC, ms=5)
        if s.get("f_ext") is not None:
            a.plot([0], [s["f_ext"]], "s", color=HL, ms=6)
            a.plot([0, h[0]], [s["f_ext"], s["cd_fine_mid_coarse"][0]], color=HL, lw=0.75, ls=(0, (6, 4)))
        if st == "val_lam":
            a.axhspan(1.498, 1.522, color=LINE, lw=0)
            a.text(0.05, 1.509, "published 1.498–1.522", color=FG3, fontsize=11, va="center")
        a.set(title=title, xlabel="grid size h / h_fine", xlim=(-0.1, max(h) * 1.1))
        a.title.set_color(FG2)
        a.title.set_fontsize(12)
    ax[0].set_ylabel("drag coefficient Cd (on D)")
    save(fig, "fig-b4-sim-02-cfd-convergence.svg")


def fig_inc():
    r = RES["CALC-B4-SIM-INC"]
    incs = [0, 15, 30, 45, 60, 75, 90]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    ax[0].plot(incs, [r[f"T_ratio__i{i}"] for i in incs], "o-", color=ACC, ms=4, label="thrust / static thrust")
    ax[0].plot(incs, [r[f"P_ratio__i{i}"] for i in incs], "o-", color=FG3, ms=4, label="power / static power")
    ax[0].set(xlabel="inflow angle to the shaft i (deg)   0 = cruise, 90 = edgewise", ylabel="ratio, fixed hover rpm",
              xlim=(0, 90))
    ax[0].legend(loc="upper left")
    ax[1].plot(incs[1:], [r[f"H_over_T__i{i}"] for i in incs[1:]], "o-", color=HL, ms=4)
    ax[1].set(xlabel="inflow angle to the shaft i (deg)", ylabel="in-plane H-force / thrust", xlim=(0, 90),
              ylim=(0, 0.16))
    ax[1].text(47, 0.142, f"worst {r['H_over_T_max']:.3f}: {r['H_at_T_hover_max_n']:.2f} N per prop\nat hover thrust",
               color=FG2, fontsize=11)
    save(fig, "fig-b4-sim-03-incidence.svg")


def fig_ops():
    r = RES["CALC-B4-SIM-OPS"]
    cases = [("pred", "A3 predicted\n2.436 kg"), ("heavy", "680 g pack\n2.566 kg"), ("gate", "gate\n2.600 kg")]
    fig, ax = plt.subplots(figsize=(12, 4.2))
    x = range(len(cases))
    w = 0.26
    ax.bar([i - w for i in x], [r[f"upper_t_n__{c}"] for c, _ in cases], w, color=HL, label="upper prop (hardest working)")
    ax.bar([i for i in x], [r[f"even_t_n__{c}"] for c, _ in cases], w, color=LINE3, label="even split")
    ax.bar([i + w for i in x], [r[f"lower_t_n__{c}"] for c, _ in cases], w, color=ACC, label="lower prop")
    ax.axhline(r["t_cap_n"], color=FG, lw=1.0)
    ax.text(2.45, r["t_cap_n"] - 1.4, f"thrust at the 9 350 rpm cap {r['t_cap_n']:.1f} N", ha="right", color=FG2)
    ax.axhline(r["t_cap_n"] / 1.5, color=FG3, lw=0.75, ls=(0, (6, 4)))
    ax.text(2.45, r["t_cap_n"] / 1.5 + 0.4, "cap / 1.5 (hover_ctrl_factor)", ha="right", color=FG3, fontsize=11)
    for i, (c, _) in enumerate(cases):
        ax.text(i - w, r[f"upper_t_n__{c}"] + 0.3, f"{r[f'upper_t_n__{c}']:.2f}\n{r[f'upper_rpm__{c}']:.0f} rpm",
                ha="center", fontsize=10, color=FG2, family="monospace")
    ax.set_xticks(list(x), [lab for _, lab in cases])
    ax.set(ylabel="hover thrust per prop (N)", ylim=(0, 22))
    ax.legend(loc="upper left", ncol=3)
    save(fig, "fig-b4-sim-04-hover-ops.svg")


def fig_cp():
    fn = HERE / "cfd" / "cases" / "hov_sa_L2" / "surface_flow.csv"
    if not fn.exists():
        return
    rows = list(csv.DictReader(open(fn)))
    k = {kk.strip().strip('"'): kk for kk in rows[0]}
    x = [float(r[k["x"]]) for r in rows]
    y = [float(r[k["y"]]) for r in rows]
    cp = [float(r[k["Pressure_Coefficient"]]) for r in rows]
    cf = [float(r[k["Skin_Friction_Coefficient_x"]]) for r in rows] if "Skin_Friction_Coefficient_x" in k else None
    pts = sorted(zip(x, y, cp, cf or [0] * len(x)))
    up = [p for p in pts if p[1] >= 0]
    fig, ax = plt.subplots(2, 1, figsize=(12, 5.2), sharex=True, gridspec_kw={"height_ratios": [3, 1.3]})
    ax[0].plot([p[0] * 1000 for p in up], [p[2] for p in up], color=ACC)
    ax[0].invert_yaxis()
    ax[0].set(ylabel="pressure coefficient Cp")
    if cf:
        ax[1].plot([p[0] * 1000 for p in up if abs(p[1]) > 0.004], [p[3] for p in up if abs(p[1]) > 0.004],
                   color=HL, lw=1.0)
        ax[1].axhline(0, color=LINE3, lw=0.75)
        ax[1].set(ylabel="Cf_x", ylim=(-0.01, 0.03))
    ax[1].set(xlabel="x from the tube centre (mm), upper half; board TE at 275 mm")
    save(fig, "fig-b4-sim-05-tubefin-cp.svg")


if __name__ == "__main__":
    fig_ops()
    fig_bemt()
    fig_inc()
    fig_conv()
    fig_cp()
