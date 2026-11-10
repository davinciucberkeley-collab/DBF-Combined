"""E3 figures for THERMAL.md / SIMULATION-REPORT.md (design-system: ink = baseline, accent blue = as-designed or the
selected value, status red = a limit; transparent background, IBM Plex, SVG text kept as text).

Run:  python redesign/team/E3/plots.py   (not -I: matplotlib needs the user site)  -> figs/fig-e3-0*.svg
Needs thermal.py's claims.json (current) and sim/cfd/results.json + mesh/esc_L2.su2.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "proofs"))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

import thermal as th  # noqa: E402

INK, FG2, FG3, LINE, LINE3, ACCENT, FAIL = "#121619", "#4B5563", "#6B7280", "#E3E7ED", "#9AA4B1", "#1F5FC7", "#B42323"
plt.rcParams.update({"font.family": ["IBM Plex Sans", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": LINE3,
                     "axes.labelcolor": FG2, "xtick.color": FG2, "ytick.color": FG2, "axes.linewidth": 0.8,
                     "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none",
                     "figure.facecolor": "none", "axes.facecolor": "none", "savefig.transparent": True,
                     "grid.color": LINE, "grid.linewidth": 0.6})
OUT = HERE / "figs"
OUT.mkdir(exist_ok=True)
M_ASD = next(n["value"] for n in json.loads((HERE.parent / "A3" / "claims.json").read_text(encoding="utf-8"))["nodes"]
             if n["id"] == "CL-A3-MASS-PREDICTED")
CFD = json.loads((HERE / "sim" / "cfd" / "results.json").read_text(encoding="utf-8"))


def save(fig, name, source):
    fig.text(0.01, 0.005, source, color=FG3, fontsize=7, family=["IBM Plex Mono", "DejaVu Sans Mono"])
    fig.savefig(OUT / name, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("wrote", OUT / name)


# ---------------------------------------------------------------- thermal model traces
def traces():
    kit = th.kit
    kit._run("CALC-E3-MISSION")
    used = dict(kit.nodes["CALC-E3-MISSION"]["input_values"])
    k, c, lim, split, t_abuse, design, nominal = th.setup(used)
    amb = c["amb_range"][1]
    out = {}
    for tag, case in (("gate", design), ("asd", c["asd"]), ("r2", c["r2"])):
        tr = []
        th.run_case(k, c, case, amb, split, t_abuse, trace=tr)
        out[tag] = tr
    return out, lim, amb


def fig_mission():
    tr, lim, amb = traces()
    parts = [("mot", "Motor (winding/stator)", lim["motor"]), ("esc", "ESC on its fin pad", lim["esc"]),
             ("pack", "Pack", lim["pack_life"]), ("fc", "Flight controller", lim["fc"])]
    fig, axs = plt.subplots(2, 2, figsize=(8.4, 5.2), sharex=True)
    for ax, (key, title, L) in zip(axs.flat, parts):
        for tag, col, lw, ls, lab in (("r2", LINE3, 1.0, (0, (4, 2)), "R2 (judged ESC wake)"),
                                      ("gate", INK, 1.4, "-", "2.6 kg gate, design inputs"),
                                      ("asd", ACCENT, 1.4, "-", f"as designed, {M_ASD:.3f} kg")):
            if key != "esc" and tag == "r2":
                continue
            t = [p[0] / 60 for p in tr[tag]]
            y = [p[2][key] for p in tr[tag]]
            ax.plot(t, y, color=col, lw=lw, ls=ls, label=lab)
        ax.axhline(L, color=FAIL, lw=0.9, ls=(0, (6, 3)))
        ax.text(0.2, L - 1.0, f"limit {L:.0f} °C" + (" (life, at landing)" if key == "pack" else ""), color=FAIL,
                fontsize=8, va="top")
        ax.set_title(title, loc="left", fontsize=9.5, color=INK)
        ax.set_ylim(amb - 2, max(L + 6, 70))
        ax.grid(True, axis="y")
    for ax in axs[1]:
        ax.set_xlabel("mission time, min")
    for ax in axs[:, 0]:
        ax.set_ylabel("temperature, °C")
    h, lb = axs[0, 1].get_legend_handles_labels()
    fig.legend(h, lb, loc="upper center", ncol=3, frameon=False, fontsize=8, bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    save(fig, "fig-e3-01-mission.svg", f"FIG E3-01 — 30 °C ambient, vented pod. Source: team/E3/thermal.py "
         f"(CALC-E3-MISSION), ESC wake from sim/cfd (CL-E3-CFD-FEQ).")


# ---------------------------------------------------------------- CFD figures
def fig_grid():
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.4))
    air = (15.89e-6, 0.0263, 0.707)
    L = CFD["geometry"]["esc_len"]

    def hl(U):
        return 0.664 * (U * L / air[0]) ** 0.5 * air[2] ** (1 / 3) * air[1] / L

    def ht(U):
        return 0.037 * (U * L / air[0]) ** 0.8 * air[2] ** (1 / 3) * air[1] / L

    for ax, st, lm, U, title in ((axs[0], "hov_sst", "hov_lm_tu1_L2", CFD["U_hov_ms"], "Hover slipstream"),
                                 (axs[1], "cru_sst", "cru_lm_tu1_L2", CFD["U_cru_ms"], "Cruise")):
        s = CFD["studies"].get(st)
        if not s:
            continue
        cells = [CFD["cases"][f"{st}_L{lv}"]["cells"] for lv in (3, 2, 1)]
        hx = [(cells[0] / n) ** 0.5 for n in cells]                   # grid spacing relative to L3
        ax.plot(hx, s["h_L3_L2_L1"], "o-", color=INK, ms=4, lw=1.0, label="SST, L3 / L2 / L1")
        best = s["h_best"]
        ax.errorbar([0], [best], yerr=[[best - s["h_low_band"]], [best * s["gci_fine"]]], fmt="s", color=ACCENT,
                    ms=5, capsize=3, label=f"extrapolated, GCI {100 * s['gci_fine']:.1f} %")
        if lm in CFD["cases"]:
            ax.plot([hx[1]], [CFD["cases"][lm]["h_wm2k"]], "D", color=FG2, ms=4, mfc="none",
                    label="LM transition, Tu 1 % (L2)")
        if st == "hov_sst" and "hov_sa_L2" in CFD["cases"]:
            ax.plot([hx[1]], [CFD["cases"]["hov_sa_L2"]["h_wm2k"]], "v", color=FG2, ms=5, mfc="none",
                    label="Spalart-Allmaras (L2)")
        for f, lab in ((0.5, "flat plate laminar, f 0.5 (R2 design)"), (0.7, "f 0.7 (R2 nominal)"),
                       (1.0, "f 1.0")):
            ax.axhline(hl(f * U), color=LINE3, lw=0.8, ls=(0, (4, 2)))
            ax.text(2.6, hl(f * U) + 0.6, lab, color=FG3, fontsize=7, va="bottom", ha="right")
        ax.axhline(ht(U), color=LINE3, lw=0.8, ls=":")
        ax.text(2.6, ht(U) + 0.6, "flat plate turbulent", color=FG3, fontsize=7, va="bottom", ha="right")
        ax.set_xlim(-0.15, 2.6)
        ax.set_xlabel("grid spacing / fine-grid spacing")
        ax.set_title(f"{title}, U {U:.1f} m/s", loc="left", fontsize=9.5, color=INK)
        ax.grid(True, axis="y")
    axs[0].set_ylabel("ESC film coefficient h, W/m² K")
    hd, lb = axs[0].get_legend_handles_labels()
    fig.legend(hd, lb, loc="upper center", ncol=4, frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(w_pad=3, rect=(0, 0.03, 1, 0.92))
    save(fig, "fig-e3-02-cfd-grid.svg", "FIG E3-02 — ESC average film coefficient vs grid. Source: "
         "team/E3/sim/cfd/esc_cfd.py, results.json (SU2 8.5 INC_RANS).")


def fig_profile():
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    g = CFD["geometry"]
    x0 = g["pad_x0"] - g["x_tube"] + (g["pad_len"] - g["esc_len"]) / 2
    air = (15.89e-6, 0.0263, 0.707)
    for name, col, lab in (("hov_sst_L2", INK, "hover, SST (L2)"), ("cru_sst_L2", ACCENT, "cruise, SST (L2)"),
                           ("hov_lm_tu1_L2", FG3, "hover, LM Tu 1 % (L2)")):
        c = CFD["cases"].get(name)
        if not c or not c.get("h_top_profile"):
            continue
        xs = [(p[0] - x0) * 1000 for p in c["h_top_profile"]]
        ax.plot(xs, [p[1] for p in c["h_top_profile"]], color=col, lw=1.2, label=lab)
    U = CFD["U_hov_ms"]
    xx = [0.5 + i for i in range(45)]
    ax.plot(xx, [0.332 * (U * x / 1000 / air[0]) ** 0.5 * air[2] ** (1 / 3) * air[1] / (x / 1000) for x in xx],
            color=LINE3, lw=0.9, ls=(0, (4, 2)), label="laminar flat plate, hover U (local)")
    ax.set_xlabel("distance along the ESC top face from its front edge, mm")
    ax.set_ylabel("local h, W/m² K")
    ax.set_ylim(0, None)
    ax.grid(True, axis="y")
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    save(fig, "fig-e3-03-esc-profile.svg", "FIG E3-03 — Local film coefficient on the ESC top face. Source: "
         "sim/cfd/results.json (h_top_profile).")


def fig_mesh():
    lines = (HERE / "sim" / "cfd" / "mesh" / "esc_L2.su2").read_text().split("\n")
    i = 0
    polys = []
    pts = []
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("NELEM"):
            n = int(ln.split("=")[1])
            elems = [list(map(int, lines[i + 1 + j].split())) for j in range(n)]
            i += n
        elif ln.startswith("NPOIN"):
            n = int(ln.split("=")[1].split()[0])
            pts = [list(map(float, lines[i + 1 + j].split()[:2])) for j in range(n)]
            i += n
        i += 1
    for e in elems:
        nn = 3 if e[0] == 5 else 4
        poly = [pts[v] for v in e[1:1 + nn]]
        if all(-0.016 < p[0] < 0.090 and -0.012 < p[1] < 0.03 for p in poly):
            polys.append([(p[0] * 1000, p[1] * 1000) for p in poly])
    fig, ax = plt.subplots(figsize=(8.4, 2.9))
    ax.add_collection(PolyCollection(polys, facecolors="none", edgecolors=LINE3, linewidths=0.15, rasterized=True))
    g = CFD["geometry"]
    x0 = (g["pad_x0"] - g["x_tube"] + (g["pad_len"] - g["esc_len"]) / 2) * 1000
    t = g["t"] * 1000
    ax.add_patch(plt.Circle((0, 0), g["D"] * 500, color=FG2, alpha=0.35, lw=0))
    ax.add_patch(plt.Rectangle((0, -t / 2), 90, t, color=FG2, alpha=0.35, lw=0))
    ax.add_patch(plt.Rectangle((x0, t / 2), g["esc_len"] * 1000, g["pad_t"] * 1000, color=FG2, alpha=0.5, lw=0))
    ax.add_patch(plt.Rectangle((x0, t / 2 + g["pad_t"] * 1000), g["esc_len"] * 1000, g["esc_t"] * 1000,
                               color="#C2540A", alpha=0.8, lw=0))
    ax.text(x0 + 22, t / 2 + 9.5, "ESC (isothermal)", color="#C2540A", ha="center", fontsize=8)
    ax.text(-11, 13, "22 mm tube", color=FG2, fontsize=8)
    ax.text(60, -9, "two-layer board 9.6 mm", color=FG2, fontsize=8)
    ax.annotate("", xy=(-14, 22), xytext=(-2, 22), arrowprops=dict(arrowstyle="<-", color=ACCENT, lw=1.2))
    ax.text(-1, 22, "slipstream", color=ACCENT, fontsize=8, va="center")
    ax.set_xlim(-16, 90)
    ax.set_ylim(-12, 30)
    ax.set_aspect("equal")
    ax.set_xlabel("x from the tube centre, mm")
    ax.set_ylabel("y, mm")
    fig.tight_layout()
    save(fig, "fig-e3-04-mesh.svg", "FIG E3-04 — Mesh L2 (36 k cells) near the tube and ESC; quad layers on "
         "every wall, y+ max 1.5. Source: sim/cfd/mesh/esc_L2.su2.")


def fig_margins():
    cl = {n["id"]: n for n in json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["nodes"]}
    m = cl["CALC-E3-MISSION"]["outputs"]
    rows = [("Motor", m["motor_peak_des_c"], m["motor_peak_asd_c"], None, 80),
            ("ESC", m["esc_peak_des_c"], m["esc_peak_asd_c"], m["esc_peak_r2wake_des_c"], 85),
            ("ESC, 30 s at limiter", m["esc_peak_abuse_des_c"], None, None, 85),
            ("Pack at landing", m["pack_end_des_c"], m["pack_end_asd_c"], None, 50),
            ("Flight controller", m["fc_peak_des_c"], m["fc_peak_asd_c"], None, 85),
            ("FC, hover-only sortie", m["fc_peak_hoveronly_des_c"], None, None, 85)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    for i, (lab, g, a, r2, L) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.plot([30, L], [y, y], color=LINE, lw=6, solid_capstyle="butt", zorder=0)
        ax.plot([L, L], [y - 0.3, y + 0.3], color=FAIL, lw=1.4)
        ax.plot(g, y, "o", color=INK, ms=5, zorder=3)
        if a is not None:
            ax.plot(a, y, "o", color=ACCENT, ms=5, zorder=4)
        if r2 is not None:
            ax.plot(r2, y, "o", mfc="none", color=FG3, ms=5, zorder=2)
        ax.text(L + 1, y, f"{L - g:+.0f} K", color=FG2, fontsize=8, va="center",
                family=["IBM Plex Mono", "DejaVu Sans Mono"])
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.set_xlim(30, 100)
    ax.set_xlabel("peak temperature at 30 °C ambient, °C")
    from matplotlib.lines import Line2D
    hd = [Line2D([], [], marker="o", ls="", color=INK, ms=5), Line2D([], [], marker="o", ls="", color=ACCENT, ms=5),
          Line2D([], [], marker="o", ls="", mfc="none", color=FG3, ms=5), Line2D([], [], marker="|", ls="", color=FAIL,
                                                                                 ms=9, mew=1.4)]
    ax.legend(hd, ["2.6 kg gate", f"as designed, {M_ASD:.3f} kg", "R2 judged ESC wake", "limit"], loc="lower center",
              ncol=4, frameon=False, fontsize=7.5, bbox_to_anchor=(0.45, 1.0))
    fig.tight_layout()
    save(fig, "fig-e3-05-margins.svg", "FIG E3-05 — Peaks against limits, margins for the gate case. Source: "
         "team/E3/claims.json (CALC-E3-MISSION).")


if __name__ == "__main__":
    fig_mesh()
    fig_grid()
    fig_profile()
    fig_mission()
    fig_margins()
