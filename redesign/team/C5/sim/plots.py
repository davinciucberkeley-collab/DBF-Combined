"""C5 simulation-round figures (design-system style: SVG, transparent, IBM Plex, ink + accent, status red only for
FAIL limits). Run after the simulations:  python -I redesign/team/C5/sim/plots.py  -> sim/fig/*.svg"""
import json
import math
from pathlib import Path

import logging
import matplotlib
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG = HERE / "fig"
FIG.mkdir(exist_ok=True)
INK, FG2, FG3, LINE = "#121619", "#4B5563", "#6B7280", "#CBD2DB"
ACC, ACC_L, HL, FAIL = "#1F5FC7", "#A9C3EE", "#C2540A", "#B42323"
plt.rcParams.update({
    "font.family": ["IBM Plex Sans", "Segoe UI", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": LINE,
    "axes.labelcolor": FG2, "xtick.color": FG3, "ytick.color": FG3, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": "#E3E7ED", "grid.linewidth": 0.6,
    "axes.titlesize": 10, "axes.titleweight": "semibold", "axes.titlecolor": INK, "legend.frameon": False,
    "legend.fontsize": 8, "savefig.transparent": True, "svg.fonttype": "none", "lines.linewidth": 1.5})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name)
    plt.close(fig)
    print("wrote", FIG / name)


def limit(ax, y, text, fail=False, x=0.99, va="bottom"):
    ax.axhline(y, color=FAIL if fail else FG3, lw=1.0, ls=(0, (6, 4)))
    ax.text(x, y, " " + text, transform=ax.get_yaxis_transform(), ha="right", va=va, fontsize=8,
            color=FAIL if fail else FG3)


def fig_envelope(S):
    env = S["hard_envelope"]["gate"]["rows"]
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.6))
    for mag, col in ((5.0, ACC_L), (7.5, "#6C93D9"), (10.0, ACC)):
        rows = sorted([r for r in env if abs(math.hypot(r[0], r[1]) - mag) < 1e-6],
                      key=lambda r: math.degrees(math.atan2(r[1], r[0])) % 360)
        az = [math.degrees(math.atan2(r[1], r[0])) % 360 for r in rows]
        axs[0].plot(az, [r[2] * 1000 for r in rows], color=col, marker="o", ms=3, label="|tilt| %.1f°" % mag)
        axs[1].plot(az, [r[3] for r in rows], color=col, marker="o", ms=3, label="|tilt| %.1f°" % mag)
    limit(axs[0], S["inputs"]["s_av"] * 1000 - S["inputs"]["guard"] * 1000, "usable 35 mm", x=0.33)
    limit(axs[0], S["inputs"]["s_av"] * 1000, "rim stop 38 mm", fail=True, x=0.33)
    axs[0].axhline(S["inputs"]["planar"]["cur_pair_design_m"] * 1000, color=HL, lw=1.0)
    axs[0].text(2, S["inputs"]["planar"]["cur_pair_design_m"] * 1000,
                "planar worst %.1f mm" % (S["inputs"]["planar"]["cur_pair_design_m"] * 1000), color=HL,
                fontsize=8, va="bottom")
    limit(axs[1], S["inputs"]["n_max"], "n limit %.1f" % S["inputs"]["n_max"])
    axs[0].set_title("%.1f m/s sink, 2/3 W lift, 2.6 kg" % S["inputs"]["v_sink"], loc="left")
    for ax in axs:
        ax.set_xlabel("tilt direction (°)  0 = pod-side pads low, 90 = left fin low")
        ax.set_xticks(range(0, 361, 45))
    axs[0].set_ylabel("largest foot stroke (mm)")
    axs[1].set_ylabel("peak load factor n")
    axs[0].legend(loc="lower left", ncol=3)
    axs[0].set_ylim(14, 40.5)
    save(fig, "fig-c5-s1-envelope.svg")


def fig_wind(S):
    W = S["wind"]
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.4), sharey=False)
    for ax, axis in zip(axs, ("broadside", "spanwise")):
        for key, col, ls in (("%s/lull/0.5" % axis, ACC, "-"), ("%s/lull/%.1f" % (axis, S["inputs"]["v_sink"]), ACC_L, "-"),
                             ("%s/steady/0.5" % axis, FG3, "--")):
            w = W[key]
            ax.plot(w["V"], [min(m, 90) for m in w["tilt_max"]], color=col, ls=ls, label=key.split("/", 1)[1].replace("/", ", sink ") + " m/s")
            tv = [v for v, t in zip(w["V"], w["tipped"]) if t]
            tm = [m for m, t in zip(w["tilt_max"], w["tipped"]) if t]
            ax.plot(tv, [min(m, 90) for m in tm], "x", color=col, ms=5)
        ax.axvline(S["inputs"]["v_card"], color=FG3, lw=1.0, ls=(0, (6, 4)))
        ax.text(S["inputs"]["v_card"], 2, " card 5 m/s", color=FG3, fontsize=8)
        if axis == "broadside":
            ax.axvline(S["inputs"]["static_v_land_broadside"], color=HL, lw=1.0)
            ax.text(S["inputs"]["static_v_land_broadside"], 80, "static 4.4 ", color=HL, fontsize=8, ha="right")
        ax.set_xlabel("wind at touchdown attitude (m/s)")
        ax.set_ylabel("largest tilt after touchdown (°)")
        ax.set_title("%s: lean + 10°, 0.3 m/s drift (× = tipped)" % axis, loc="left")
        ax.set_ylim(0, 95)
    axs[0].legend(loc="upper left")
    save(fig, "fig-c5-s2-wind-tipover.svg")


def fig_dt(S):
    lad = S["dt_ladder"]
    dts = sorted(lad, key=float)
    x = [float(d) * 1e6 for d in dts]
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.2))
    axs[0].plot(x, [lad[d]["stroke_m"] * 1000 for d in dts], color=ACC, marker="o", ms=4)
    axs[0].set_ylabel("worst stroke (mm)")
    axs[1].plot(x, [lad[d]["side_1ms_N"] for d in dts], color=ACC, marker="o", ms=4, label="1 ms filtered")
    axs[1].plot(x, [lad[d]["side_peak_N"] for d in dts], color=FG3, marker="o", ms=4, ls="--", label="unfiltered")
    axs[1].set_ylabel("worst foot side load (N)")
    axs[1].legend()
    for ax in axs:
        ax.set_xscale("log")
        ax.set_xlabel("time step (µs)")
        ax.axvline(40, color=FG3, lw=0.8, ls=":")
    save(fig, "fig-c5-s3-dt-convergence.svg")


def fig_history(S):
    h = S["history_worst"]
    t = [1000 * v for v in h["t"]]
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.2))
    names = ("UR", "UL", "LR", "LL")
    cols = (ACC, ACC_L, HL, "#E0A070")
    for j in range(4):
        axs[0].plot(t, [1000 * s[j] for s in h["s"]], color=cols[j], label=names[j])
        axs[1].plot(t, [s[j] for s in h["side"]], color=cols[j], label=names[j])
    limit(axs[0], 35.0, "usable 35 mm")
    axs[0].set_ylabel("foot stroke (mm)")
    axs[1].set_ylabel("foot side load (N)")
    for ax in axs:
        ax.set_xlabel("time from touchdown (ms)")
        ax.set_xlim(0, 120)
    axs[0].legend(ncol=4, loc="lower right")
    wc = S["hard_envelope"]["gate"]["worst_case"]
    axs[0].set_title("worst case: tilt θ %.1f°, φ %.1f°, %.1f m/s, 2.6 kg" % (wc["theta"], wc["phi"], wc["v_sink"]),
                     loc="left")
    save(fig, "fig-c5-s4-history.svg")


def fig_fea(F):
    lv = F["levels"]
    R = F["inputs"]["R_lip_N"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    for case, zone, col, mk in (("+y", "rim", ACC, "o"), ("+z", "aft box", HL, "s"), ("+z", "rim", ACC_L, "o"),
                                ("+y", "aft box", "#E0A070", "s")):
        rows = [r for r in lv if r["case"] == case]
        ax.plot([0.8 / r["h_mm"] for r in rows], [r["zones"][zone]["vm_max_MPa"] for r in rows], color=col,
                marker=mk, ms=4, label="%s, %s%s" % (case, zone, " (clamp edge, not used)" if (case, zone) == ("+z", "aft box") else ""))
        c = F["convergence"]["%s|%s" % (case, zone)]
        if c.get("f_ext"):
            ax.plot([3.4], [c["f_ext"]], marker=mk, mfc="none", color=col, ms=6)
    limit(ax, 40.0, "PETG allowable 40 MPa", fail=True)
    limit(ax, F["inputs"]["d5_sigma_rim_MPa"], "D5 beam %.1f MPa" % F["inputs"]["d5_sigma_rim_MPa"], x=0.6, va="top")
    ax.set_xlabel("elements through the 0.8 mm wall (open marker: Richardson)")
    ax.set_ylabel("von Mises at %.0f N lip reaction (MPa)" % R)
    ax.set_ylim(0, None)
    ax.legend(loc="upper left", ncol=2)
    save(fig, "fig-c5-s5-fea-convergence.svg")


def fig_fea_d65(F, side_ult):
    """C5-R6: D-65 shoe, stress scaled to the design ultimate side load."""
    lv = F["levels"]
    k = side_ult / F["inputs"]["F_side_ult_N"]
    w = F["inputs"]["geometry_mm"]["w"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    for case, zone, col, mk in (("+y", "rim", ACC, "o"), ("+z", "rim", ACC_L, "o"), ("+y", "window strips", HL, "s"),
                                ("+z", "window strips", "#E0A070", "s")):
        rows = [r for r in lv if r["case"] == case]
        ax.plot([w / r["h_mm"] for r in rows], [k * r["zones"][zone]["vm_max_MPa"] for r in rows], color=col,
                marker=mk, ms=4, label="%s, %s" % (case, zone))
        c = F["convergence"]["%s|%s" % (case, zone)]
        if c.get("f_ext"):
            ax.plot([w / 0.2667 * 1.15], [k * c["f_ext"]], marker=mk, mfc="none", color=col, ms=6)
    limit(ax, 40.0, "PETG allowable 40 MPa", fail=True)
    ax.set_xlabel("elements through the %.1f mm wall (open marker: Richardson)" % w)
    ax.set_ylabel("von Mises at %.2f N ult side load (MPa)" % side_ult)
    ax.set_ylim(0, 45)
    ax.legend(loc="lower right", ncol=2)
    ax.set_title("D-65 shoe: wall 2.0, rim 3.0, R 1.0, engagement 25 mm", loc="left")
    save(fig, "fig-c5-r6-fea-d65.svg")


if __name__ == "__main__":
    S = json.loads((HERE / "out" / "sim3d.json").read_text())
    fig_envelope(S)
    fig_wind(S)
    fig_dt(S)
    fig_history(S)
    fp = HERE / "out" / "fea_shoe.json"
    if fp.exists():
        fig_fea(json.loads(fp.read_text()))
    fp = HERE / "out" / "fea_shoe_v_engage25_rim_t3_w2_rin1.json"
    cl = HERE.parent / "claims.sim.json"
    if fp.exists() and cl.exists():
        ult = [n for n in json.loads(cl.read_text("utf-8"))["nodes"] if n["id"] == "CL-C5-SIM3D-SIDE-ULT"][0]["value"]
        fig_fea_d65(json.loads(fp.read_text()), ult)
