"""Figures for SIMULATION-REPORT.md (B2-R3), design-system style (same palette as team/B2/plots_wing.py:
ink/greys for context, accent blue = the result, red = a limit).

    python redesign/team/B2/sim/plots_sim.py      -> team/B2/sim/fig/*.svg   (matplotlib: run without -I)
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
B2 = HERE.parent
FIG = HERE / "fig"
FIG.mkdir(exist_ok=True)
V = json.loads((HERE / "out" / "verify_results.json").read_text())
C = json.loads((HERE / "out" / "cfd2d_results.json").read_text()) if (HERE / "out" / "cfd2d_results.json").exists() else None
X = json.loads((B2 / "out" / "xfoil_results.json").read_text())
L = json.loads((B2 / "out" / "loads_spanwise.json").read_text())
CL = json.loads((HERE / "claims.sim.json").read_text())
P = json.loads((B2.parents[1] / "params" / "params.json").read_text(encoding="utf-8"))

FG, FG2, FG3, LINE3, ACCENT, FAIL = "#121619", "#4B5563", "#6B7280", "#9AA4B1", "#1F5FC7", "#B42323"
plt.rcParams.update({"font.family": ["IBM Plex Sans", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": LINE3,
                     "axes.labelcolor": FG2, "xtick.color": FG3, "ytick.color": FG3, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": "#E3E7ED", "grid.linewidth": 0.6,
                     "svg.fonttype": "none", "figure.facecolor": "none", "axes.facecolor": "none"})


def claim(cid):
    for n in CL.get("nodes", CL if isinstance(CL, list) else []):
        if n.get("id") == cid:
            return n.get("value")
    return None


def calc_out(cid):
    for n in CL.get("nodes", []):
        if n.get("id") == cid:
            return n.get("outputs") or n.get("value")
    return None


def fig_stall():
    rows = V["sm_rows"]
    sm = np.array([r["sm"] for r in rows]) * 100
    clm = np.array([r["CLmax_trim"] for r in rows])
    rho, g = P["env"]["rho_kgm3"]["value"], P["env"]["g_ms2"]["value"]
    S = P["wing"]["span_m"]["value"] * P["wing"]["chord_m"]["value"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3.3))
    a1.plot(sm, clm, color=ACCENT, lw=1.8)
    a1.set_xlabel("static margin (% c)")
    a1.set_ylabel("trimmed CLmax")
    for m, lab, ls in ((2.6, "2.6 kg gate", "-"), (claim("CL-A3-MASS-PREDICTED") or 2.436, "A3 predicted", "--")):
        a2.plot(sm, np.sqrt(2 * m * g / (rho * S * clm)), color=ACCENT if ls == "-" else FG2, lw=1.6, ls=ls, label=lab)
    a2.axhline(P["requirements"]["stall_max_ms"]["value"], color=FAIL, lw=1.0)
    a2.annotate("R-STALL 12 m/s", (sm[0], 12.0), xytext=(2, 3), textcoords="offset points", color=FAIL, fontsize=8)
    o = calc_out("CALC-B2R3-STALL") or {}
    marks = {lab: o[f"SM_{k}"] for k, lab in (("fwd", "fwd limit"), ("aft", "aft limit"), ("basic", "A3 basic"),
                                               ("pred", "A3 predicted")) if f"SM_{k}" in o}
    for lab, s in marks.items():
        for ax in (a1, a2):
            ax.axvline(s * 100, color=LINE3, lw=0.8, ls=":")
        a1.annotate(lab, (s * 100, clm.max()), xytext=(2, -10), textcoords="offset points", color=FG3, fontsize=7,
                    rotation=90, va="top")
    a2.set_xlabel("static margin (% c)")
    a2.set_ylabel("Vs (m/s)")
    a2.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "B2-R3-01-stall-vs-sm.svg")


def fig_conv():
    fig, axs = plt.subplots(1, 3, figsize=(8.4, 2.8))
    pan = V["xfoil_panels"]
    n = sorted(int(k) for k in pan)
    axs[0].plot(n, [pan[str(k)]["clmax"] for k in n], "o-", color=ACCENT, lw=1.4, ms=4)
    axs[0].set_xlabel("XFOIL panels")
    axs[0].set_ylabel("S5010 clmax, Re 2.6e5")
    lat = V["lattice"]
    nv = [r["nc"] for r in lat]
    axs[1].plot(nv, [r["CLmax_trim"] for r in lat], "o-", color=ACCENT, lw=1.4, ms=4)
    axs[1].set_xlabel("AVL chordwise vortices")
    axs[1].set_ylabel("trimmed CLmax, SM 5 %")
    if C and C["gci"]:
        g = list(C["gci"].values())[0]
        cells = g["cells"]
        h = [1 / math.sqrt(c) for c in cells]
        ch = [abs(g["ch"][k]) for k in ("L1", "L2", "L3")]
        axs[2].plot(h, ch, "o-", color=ACCENT, lw=1.4, ms=4)
        fx = g["ch"].get("f_exact")
        if fx:
            axs[2].plot([0], [abs(fx)], "s", color=FG2, ms=4)
            axs[2].annotate("Richardson", (0, abs(fx)), xytext=(4, 4), textcoords="offset points", fontsize=7, color=FG2)
        axs[2].set_xlim(left=-0.0005)
        axs[2].set_xlabel("h = 1/sqrt(cells)")
        axs[2].set_ylabel("|C_h|, -25 deg, SU2")
    for ax in axs:
        ax.ticklabel_format(useOffset=False, axis="y")
    fig.tight_layout()
    fig.savefig(FIG / "B2-R3-02-convergence.svg")


def fig_cfd():
    if not C:
        return
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3.3))
    t = np.array(X["polars"][f"s5010_re{X['re_stall']/1e5:.1f}e5_n9_f+0_p220"]["table"])
    a1.plot(t[:, 0], t[:, 1], color=FG2, lw=1.2, label="XFOIL Ncrit 9")
    cs = sorted([c for c in C["cases"] if c["delta"] == 0.0 and c["level"] == 2], key=lambda c: c["alpha"])
    a1.plot([c["alpha"] for c in cs], [c["CL"] for c in cs], "o", color=ACCENT, ms=5, label="SU2 SA (L2)")
    a1.set_xlabel("alpha (deg)")
    a1.set_ylabel("cl, Re 2.6e5")
    a1.legend(frameon=False, fontsize=8)
    for vis, ls, lab in (("i", "-", "XFOIL inviscid"), ("v", "--", "XFOIL viscous (converged)")):
        ds, lo, hi = [], [], []
        for d in (-25, -20, -15, -10, -5, 5, 10, 15, 20, 25):
            h = X["hinge"].get(f"hm_s5010_re{X['re_dive']/1e5:.1f}e5_f{d:+d}_{vis}")
            if not h:
                continue
            v = [x for x, ok in zip(h["hmom_qc2"], h["converged"]) if ok and x == x]
            if v:
                ds.append(d)
                lo.append(min(v))
                hi.append(max(v))
        a2.fill_between(ds, lo, hi, color=LINE3 if vis == "i" else "#C2C8D0", alpha=0.5, lw=0)
        a2.plot(ds, [(a + b) / 2 for a, b in zip(lo, hi)], color=FG2, lw=1.0, ls=ls, label=lab)
    hs = [c for c in C["cases"] if c["delta"] != 0.0 and c["level"] == 2]
    a2.plot([c["delta"] for c in hs], [c["ch"] for c in hs], "o", color=ACCENT, ms=5, label="SU2 SA (L2)")
    a2.set_xlabel("elevon deflection (deg, + TE down)")
    a2.set_ylabel("C_h = H / (q c^2)")
    a2.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "B2-R3-03-cfd-vs-xfoil.svg")


def fig_span():
    d = L["cases"]["CL0.80"]
    y = np.array(d["y_m"])
    b2 = P["wing"]["span_m"]["value"] / 2
    fig, ax = plt.subplots(figsize=(5, 3.0))
    ax.plot(y, d["cl_over_CL"], color=ACCENT, lw=1.8, label="AVL trimmed, CL 0.8")
    yy = np.linspace(0, b2, 200)
    ell = 4 / math.pi * np.sqrt(1 - (yy / b2) ** 2)
    ax.plot(yy, ell, color=LINE3, lw=1.0, ls="--", label="elliptic")
    ax.plot(yy, 0.5 * (ell + 1), color=FG2, lw=1.0, ls="-.", label="Schrenk")
    ax.axvline(P["fins"]["y_m"]["value"], color=FG3, lw=0.8, ls=":")
    ax.set_xlabel("y (m)")
    ax.set_ylabel("c cl / (c CL)")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "B2-R3-04-span-loading.svg")


if __name__ == "__main__":
    fig_stall()
    fig_conv()
    fig_cfd()
    fig_span()
    print("figures:", sorted(p.name for p in FIG.glob("*.svg")))
