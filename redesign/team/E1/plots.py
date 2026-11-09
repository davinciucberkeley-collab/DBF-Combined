"""E1 figures from the propulsion model (design-system colours: ink = baseline, accent blue = recommended).

Run:  python redesign/team/E1/plots.py   (not -I: matplotlib needs `packaging` from the user site)   -> fig-prp-01-efficiency-map.svg, fig-prp-02-static.svg beside this file
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
import propulsion as pm  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

INK, FG2, FG3, LINE, ACCENT = "#121619", "#4B5563", "#6B7280", "#E3E7ED", "#1F5FC7"
plt.rcParams.update({"font.family": ["IBM Plex Sans", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": FG3,
                     "axes.labelcolor": FG2, "xtick.color": FG2, "ytick.color": FG2, "axes.linewidth": 0.8,
                     "svg.fonttype": "none", "figure.facecolor": "none", "axes.facecolor": "none",
                     "savefig.transparent": True})

RHO, G = 1.225, 9.80665
KV, RM, I0, ESC = 900.0, 0.086, 0.9, (0.010, 0.5)
kT, kP, _ = pm.calibrate(RHO, KV, RM, I0, ESC)
RM_WARM = pm.r_hot(RM, 0.00393, 40.0)
_PJ = __import__("json").loads((HERE.parents[1] / "params" / "params.json").read_text(encoding="utf-8"))
M = _PJ["requirements"]["mtow_gate_kg"]["value"]
B, E = _PJ["wing"]["span_m"]["value"], _PJ["wing"]["oswald_e"]["value"]
S = B * _PJ["wing"]["chord_m"]["value"]
LD, VREF = _PJ["performance"]["ld_cruise"]["value"], _PJ["performance"]["cruise_ms"]["value"]


def eff_map():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9), sharey=True)
    Vs = [6 + 0.5 * i for i in range(29)]           # 6..20 m/s
    Ts = [0.4 + 0.2 * j for j in range(24)]         # 0.4..5.0 N per motor
    for ax, prop, col in ((axes[0], "11x4.5MR", INK), (axes[1], "11x5.5MR", ACCENT)):
        Z = []
        for T in Ts:
            row = []
            for V in Vs:
                try:
                    s = pm.at_thrust(prop, T, V, RHO, 1.0, kP, KV, RM_WARM, I0, ESC[0], ESC[1], 14.8)
                    row.append(T * V / s["P_bat_W"] if s["T_N"] > 0 else float("nan"))
                except Exception:
                    row.append(float("nan"))
            Z.append(row)
        cs = ax.contour(Vs, Ts, Z, levels=[0.1, 0.2, 0.3, 0.4, 0.5], colors=FG3, linewidths=0.75)
        ax.clabel(cs, fmt="%.1f", fontsize=8, colors=FG2)
        vd = [12 + 0.25 * i for i in range(33)]
        td = [pm.cruise_drag(v, M, G, RHO, S, B, E, LD, VREF)[0] / 4 for v in vd]
        ax.plot(vd, td, color=col, lw=2)
        tc = pm.cruise_drag(VREF, M, G, RHO, S, B, E, LD, VREF)[0] / 4
        s = pm.at_thrust(prop, tc, VREF, RHO, 1.0, kP, KV, RM_WARM, I0, ESC[0], ESC[1], 14.8)
        ax.plot([VREF], [tc], "o", color=col, ms=6)
        ax.annotate(f"cruise {VREF:.0f} m/s\n{4 * s['P_bat_W']:.0f} W, eta {tc * VREF / s['P_bat_W']:.2f}", (VREF, tc),
                    xytext=(16.2, 3.4), fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", color=FG3, lw=0.8))
        ax.set_title(f"X3108S KV900 + APC {prop}", fontsize=10, color=INK, loc="left")
        ax.set_xlabel("airspeed along the prop axis (m/s)")
        ax.grid(color=LINE, lw=0.6)
        ax.set_xlim(6, 20)
        ax.set_ylim(0.4, 5.0)
    axes[0].set_ylabel("thrust per motor (N)")
    fig.tight_layout()
    out = HERE / "fig-prp-01-efficiency-map.svg"
    fig.savefig(out)
    print(out.name)


def static():
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    for prop, col, lab in (("11x4.5MR", INK, "11x4.5MR (params baseline)"), ("11x5.5MR", ACCENT, "11x5.5MR (proposed)")):
        xs, ys = [], []
        for k in range(10, 101, 2):
            s = pm.full_throttle(prop, 0.0, RHO, kT, kP, KV, RM, I0, ESC[0], ESC[1], 14.8, 0.0, 1.0, 4,
                                 duty_max=k / 100)
            xs.append(s["I_bat_A"])
            ys.append(s["T_N"] / G * 1000)
        ax.plot(xs, ys, color=col, lw=2, label=lab)
    ax.plot([r[0] for r in pm.MAKER_1147], [r[1] for r in pm.MAKER_1147], "o", ms=3.5, mfc="none", mec=FG3,
            label="maker table, 11x4.7 (supply sags above 12 A)")
    th = M * G * 1.06 / 4 / G * 1000
    ax.axhline(th, color=FG3, lw=0.8, ls=(0, (6, 4)))
    ax.text(17, th - 95, f"hover at the 2.6 kg gate: {th:.0f} gf", fontsize=8, color=FG2)
    for x, t in ((25, "motor 25 A / 30 s"), (36, "ESC 45 A / 1.25")):
        ax.axvline(x, color=FG3, lw=0.8, ls=(0, (6, 4)))
        ax.text(x - 1.2, 60, t, rotation=90, fontsize=8, color=FG2)
    ax.set_xlabel("battery current per motor at a held 14.8 V (A)")
    ax.set_ylabel("static thrust per motor (gf)")
    ax.grid(color=LINE, lw=0.6)
    ax.set_xlim(0, 45)
    ax.set_ylim(0, 2400)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    out = HERE / "fig-prp-02-static.svg"
    fig.savefig(out)
    print(out.name)


if __name__ == "__main__":
    eff_map()
    static()
