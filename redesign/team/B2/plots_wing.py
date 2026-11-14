"""Figures for WING-AERO.md (design-system colours: ink/greys for context, accent blue = the chosen section).

    python -I redesign/team/B2/plots_wing.py      -> team/B2/fig/*.svg
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG = HERE / "fig"
FIG.mkdir(exist_ok=True)
X = json.loads((HERE / "out" / "xfoil_results.json").read_text())
A = json.loads((HERE / "out" / "avl_results.json").read_text())
L = json.loads((HERE / "out" / "loads_spanwise.json").read_text())
P = json.loads((HERE.parents[1] / "params" / "params.json").read_text(encoding="utf-8"))

FG, FG2, FG3, LINE3, ACCENT, FAIL = "#121619", "#4B5563", "#6B7280", "#9AA4B1", "#1F5FC7", "#B42323"
GREYS = {"mh45": FG2, "mh60": LINE3, "e186": "#C2C8D0"}
NAME = {"mh45": "MH 45", "mh60": "MH 60", "s5010": "S5010", "e186": "E186"}
CH = A["chosen"]
TS, TC, TD = (f"{X[k]/1e5:.1f}e5" for k in ("re_stall", "re_cruise", "re_dive"))
plt.rcParams.update({"font.family": ["IBM Plex Sans", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": LINE3,
                     "axes.labelcolor": FG2, "xtick.color": FG3, "ytick.color": FG3, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": "#E3E7ED", "grid.linewidth": 0.6,
                     "svg.fonttype": "none", "figure.facecolor": "none", "axes.facecolor": "none"})


def col(f):
    return ACCENT if f == CH else GREYS.get(f, LINE3)


def pol(tag):
    return np.array(X["polars"][tag]["table"])


def fig_polars():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3.4))
    for f in ["e186", "mh60", "mh45", "s5010"]:
        t = pol(f"{f}_re{TS}_n9_f+0_p220")
        lw = 1.8 if f == CH else 1.1
        a1.plot(t[:, 2] * 1e4, t[:, 1], color=col(f), lw=lw)
        a2.plot(t[:, 0], t[:, 1], color=col(f), lw=lw)
        i = int(np.argmax(t[:, 1]))
        a2.annotate(NAME[f], (t[i, 0], t[i, 1]), xytext=(4, 2), textcoords="offset points", color=col(f), fontsize=8)
    a1.set_xlabel("cd (counts)")
    a1.set_ylabel("cl")
    a1.set_xlim(60, 250)
    a2.set_xlabel("alpha (deg)")
    a2.set_ylabel("cl")
    fig.tight_layout()
    fig.savefig(FIG / "B2-01-polars.svg")


def fig_flap():
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    for f in ["mh45", "s5010"]:
        env = np.array(A["foils"][f]["clmax_vs_flap"])
        ax.plot(env[:, 0], env[:, 1], color=col(f), lw=1.8 if f == CH else 1.1, marker="o", ms=3, label=NAME[f])
        for re_, mk in ((TS, "^"), (TC, "v")):
            pts = []
            for d in (-15, -10, -5, 0, 5, 10):
                s = X["polars"].get(f"{f}_re{re_}_n9_f{d:+g}_p220", {}).get("summary", {})
                if s.get("n", 0) >= 20 and s.get("clmax", 0) > 0.5:
                    pts.append((d, s["clmax"]))
            pts = np.array(pts)
            ax.scatter(pts[:, 0], pts[:, 1], s=10, marker=mk, color=col(f), alpha=0.45, lw=0)
    ax.set_xlabel("elevon deflection (deg, + trailing edge down)")
    ax.set_ylabel("section clmax")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "B2-02-clmax-elevon.svg")


def fig_span():
    yin, yout = P["wing"]["elevon"]["inboard_y_m"]["value"], P["wing"]["elevon"]["outboard_y_m"]["value"]
    cfl = np.array(A["foils"][CH]["clmax_vs_flap"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3.2))
    for k, shade in (("CL0.30", "#C2C8D0"), ("CL0.50", LINE3), ("CL0.80", ACCENT)):
        c = L["cases"][k]
        y = np.array(c["y_m"])
        cl = np.array(c["cl"])
        el = np.array([(yin[0] <= v <= yin[1]) or (yout[0] <= v <= yout[1]) for v in y])
        lim = np.where(el, np.interp(c["elevator_deg"], cfl[:, 0], cfl[:, 1]), np.interp(0, cfl[:, 0], cfl[:, 1]))
        a1.plot(y, np.array(c["cl_over_CL"]), color=shade, lw=1.4, label=f"CL {c['CL']:.1f}")
        a2.step(y, cl / lim, where="mid", color=shade, lw=1.4, label=f"CL {c['CL']:.1f}, elevon {c['elevator_deg']:+.1f} deg")
    for ax in (a1, a2):
        for a, b in (yin, yout):
            ax.axvspan(a, b, color="#EEF1F5", lw=0, zorder=0)
        ax.axvline(P["fins"]["y_m"]["value"], color=FG3, lw=0.75, ls=(0, (6, 4)))
        ax.set_xlabel("y (m)")
        ax.set_xlim(0, 0.575)
    a2.axhline(1.0, color=FAIL, lw=1)
    a1.set_ylabel("cl / CL")
    a2.set_ylabel("cl / local clmax")
    a2.legend(frameon=False, fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG / "B2-03-span-stall.svg")


def fig_hinge():
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    for mode, ls, lab in (("i", "-", "inviscid (design)"), ("v", ":", "viscous, converged")):
        ds, lo, hi = [], [], []
        for d in (-25, -20, -15, -10, -5, 5, 10, 15, 20, 25):
            r = X["hinge"].get(f"hm_{CH}_re{TD}_f{d:+g}_{mode}")
            if not r:
                continue
            v = [h for h, c in zip(r["hmom_qc2"], r["converged"]) if c and h == h]
            if v:
                ds.append(d)
                lo.append(min(v))
                hi.append(max(v))
        ds = np.array(ds)
        ax.fill_between(ds, lo, hi, color=ACCENT if mode == "i" else LINE3, alpha=0.18 if mode == "i" else 0.3, lw=0)
        ax.plot(ds, (np.array(lo) + np.array(hi)) / 2, color=ACCENT if mode == "i" else FG2, ls=ls, lw=1.4, label=lab)
    ax.axhline(0, color=LINE3, lw=0.75)
    ax.set_xlabel("elevon deflection (deg)")
    ax.set_ylabel("HMOM / (q c^2)")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "B2-04-hinge.svg")


if __name__ == "__main__":
    fig_polars()
    fig_flap()
    fig_span()
    fig_hinge()
    print("figures:", ", ".join(p.name for p in sorted(FIG.glob("*.svg"))))
