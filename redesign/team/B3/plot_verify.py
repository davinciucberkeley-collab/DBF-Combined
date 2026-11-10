"""Figures for SIMULATION-REPORT.md (design-system: ink/greys for context, accent blue = the as-designed result,
fail red only next to the word FAIL, IBM Plex, transparent background).

    python -I redesign/team/B3/plot_verify.py      -> team/B3/fig/B3-V*.svg
Reads results/verify.json, results/sc_results.json (R4 basis), cfd/cfd_results.json.
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
V = json.loads((HERE / "results" / "verify.json").read_text())
R4 = json.loads((HERE / "results" / "sc_results.json").read_text())
CFDF = HERE / "cfd" / "cfd_results.json"
CFD = json.loads(CFDF.read_text()) if CFDF.exists() else None
PAR = json.loads((HERE.parents[1] / "params" / "params.json").read_text(encoding="utf-8"))

FG, FG2, FG3, LINE, LINE3, ACCENT, FAIL = "#121619", "#4B5563", "#6B7280", "#E3E7ED", "#9AA4B1", "#1F5FC7", "#B42323"
plt.rcParams.update({"font.family": ["IBM Plex Sans", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": LINE3,
                     "axes.labelcolor": FG2, "xtick.color": FG3, "ytick.color": FG3, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": LINE, "grid.linewidth": 0.6,
                     "svg.fonttype": "none", "figure.facecolor": "none", "axes.facecolor": "none",
                     "legend.frameon": False, "legend.fontsize": 8})
MONO = {"family": ["IBM Plex Mono", "DejaVu Sans Mono"], "size": 8}
C = PAR["wing"]["chord_m"]["value"]
A3C = json.loads((HERE.parents[0] / "A3" / "claims.json").read_text())
PRED = next(n["value"] for n in A3C["nodes"] if n["id"] == "CL-A3-CG-X-PRED")


def fig_lattice():
    L = V["CALC-B3-V-LATTICE"]
    lv = ["coarse", "medium", "fine", "xfine"]
    N = [L["N"][k] for k in lv]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3.0))
    for ax, key, scale, lab in ((a1, "Xnp", 1000, "Xnp, wing + fins (mm from LE)"), (a2, "Cnb", 1, "Cn_beta, AVL part (1/rad)")):
        y = [L["rows"][k][key] * scale for k in lv]
        ax.plot(N, y, color=ACCENT, marker="o", ms=4, lw=1.6)
        for n_, y_, k in zip(N, y, lv):
            ax.annotate(k, (n_, y_), xytext=(3, 4), textcoords="offset points", fontsize=7, color=FG3)
        g = L[f"gci_{key}"]
        if g.get("f_ext"):
            fe = g["f_ext"] * scale
            ax.axhline(fe, color=FG3, lw=0.8, ls=(0, (4, 3)))
            ax.annotate(f"extrapolated {fe:.4g}  GCI {g['gci_pct']:.2f} %", (N[0], fe), xytext=(0, 4),
                        textcoords="offset points", fontsize=7, color=FG2)
        ax.set_xscale("log")
        ax.set_xlabel("horseshoe vortices (log)")
        ax.set_ylabel(lab)
    fig.tight_layout()
    fig.savefig(FIG / "B3-V1-lattice.svg")
    plt.close(fig)


def fig_cfd():
    if not CFD or "levels_SA" not in CFD:
        return
    lv = CFD["levels_SA"]
    ks = sorted(lv, key=int)
    h = [1 / math.sqrt(lv[k]["cells"]) * 1e3 for k in ks]
    e = [lv[k]["eta_cm"] for k in ks]
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.plot(h, e, color=ACCENT, marker="o", ms=4, lw=1.6, label=f"SU2 RANS SA, {len(ks)} converged meshes (L3 not converged)")
    g = CFD.get("gci_eta_cm", {})
    if g.get("f_ext"):
        ax.plot([0], [g["f_ext"]], marker="D", ms=5, color=ACCENT, ls="none", label="Richardson extrapolation")
    if CFD.get("eta_cm_L2_SSTLM") is not None:
        ax.plot([h[1]], [CFD["eta_cm_L2_SSTLM"]], marker="s", ms=5, mfc="none", color=FG2, ls="none",
                label="SU2 SST-LM transition (medium)")
    xf = CFD.get("xfoil", {})
    xs = [v.get("eta_cm_a4") for k, v in sorted(xf.items(), key=lambda kv: int(kv[0]))]
    if any(x is not None for x in xs):
        for x, n in zip(xs, sorted(xf, key=int)):
            ax.axhline(x, color=LINE3, lw=0.8)
        ax.annotate(f"XFOIL Ncrit 9, 160 / 240 / 320 panels: {min(xs):.3f} to {max(xs):.3f}", (0.2, max(xs)),
                    xytext=(0, 4), textcoords="offset points", fontsize=7, color=FG2)
    ax.axhline(0.606, color=FG3, lw=0.8, ls=(0, (4, 3)))
    ax.annotate("CL-B2-ELEVON-ETA 0.606 (XFOIL, cl 0.5)", (0.2, 0.606), xytext=(0, -10), textcoords="offset points",
                fontsize=7, color=FG3)
    ax.axhline(0.606 * 0.8, color=FAIL, lw=0.8, ls=(0, (2, 2)))
    ax.annotate("-20 %: CG range closes (FAIL)", (0.2, 0.606 * 0.8), xytext=(0, 4), textcoords="offset points",
                fontsize=7, color=FAIL)
    ax.set_xlim(left=-0.2)
    ax.set_ylim(0.45, 0.95)
    ax.set_xlabel("mesh size h = 1/sqrt(cells) (x 1e-3)")
    ax.set_ylabel("eta = (dcm/ddelta) / thin airfoil")
    ax.legend(loc="center right")
    fig.tight_layout()
    fig.savefig(FIG / "B3-V2-cfd-eta.svg")
    plt.close(fig)


def fig_cg():
    cg = V["CALC-B3-V-CG"]
    env = V["CALC-B3-V-NP-CL"]
    r4 = R4["CALC-B3-CG-LIMITS"]
    rows = [("R4 model (CG on chord plane, alpha 4)", r4["x_fwd"], r4["x_aft"], FG3),
            ("As designed, alpha 4 basis", cg["x_fwd_gate"], cg["x_aft_gate"], FG3),
            ("As designed, SM 5 % at 1.3 Vs (governs)", cg["x_fwd_gate"], env["x_aft_env"], ACCENT)]
    fig, ax = plt.subplots(figsize=(7.4, 2.6))
    for i, (lab, f, a, col) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y, (a - f) * 1000, left=f * 1000, height=0.42, color=col, alpha=0.30 if col == FG3 else 0.45,
                edgecolor=col, lw=1.2)
        ax.text(f * 1000 - 0.1, y, f"{f * 1000:.1f}", ha="right", va="center", fontdict=MONO, color=FG2)
        ax.text(a * 1000 + 0.1, y, f"{a * 1000:.1f}", ha="left", va="center", fontdict=MONO, color=FG2)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    x3 = cg["x_a3"] * 1000
    x3p = PRED * 1000
    ax.axvline(x3, color=FG, lw=1.2)
    ax.axvline(x3p, color=FG, lw=0.8, ls=(0, (2, 2)))
    ax.annotate("A3 CG", (x3, len(rows) - 0.45), xytext=(-3, 0), textcoords="offset points", fontsize=7,
                color=FG, ha="right")
    ax.annotate("A3 predicted", (x3p, len(rows) - 0.45), xytext=(3, 0), textcoords="offset points", fontsize=7,
                color=FG)
    if env["a3_aft_margin_env"] < 0:
        ax.annotate(f"FAIL: A3 CG {-env['a3_aft_margin_env'] * 1000:.1f} mm aft of the limit", (x3, -0.45),
                    xytext=(-3, 0), ha="right", textcoords="offset points", fontsize=7, color=FAIL)
    ax.set_ylim(-0.6, len(rows) - 0.3)
    ax.set_xlim(45.0, 56.0)
    ax.set_xlabel("CG x from the wing LE (mm)")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(FIG / "B3-V3-cg-range.svg")
    plt.close(fig)


def fig_npcl():
    env = V["CALC-B3-V-NP-CL"]
    rows = sorted(env["rows"].values(), key=lambda r: r["CL"])
    CL = [r["CL"] for r in rows]
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    d = env["dprop_pod"]
    ax.plot(CL, [(r["xnp_aero_z0"] + d) * 1000 for r in rows], color=FG3, marker="o", ms=3.5, lw=1.2,
            label="CG on the chord plane (R4 basis, z = 0)")
    ax.plot(CL, [r["xnp"] * 1000 for r in rows], color=ACCENT, marker="o", ms=4, lw=1.8,
            label="A3 CG height z = +18.5 mm (AVL)")
    ax.plot(CL, [(r["xnp_aero_z0"] + r["dxnp_hand"] + d) * 1000 for r in rows], color=ACCENT, lw=0.9,
            ls=(0, (3, 2)), label="hand formula on z = 0")
    lim = [(r["xnp"] - 0.05 * C) * 1000 for r in rows]
    ax.plot(CL, lim, color=FG, lw=1.0, ls=(0, (4, 3)), label="aft CG limit (SM 5 %)")
    x3 = V["CALC-B3-V-CG"]["x_a3"] * 1000
    ax.axhline(x3, color=FAIL, lw=0.9)
    ax.annotate(f"A3 CG {x3:.1f} mm: aft of the limit at 1.3 Vs (FAIL)" if env["a3_aft_margin_env"] < 0 else
                f"A3 CG {x3:.1f} mm", (CL[-1], x3), xytext=(0, 4), textcoords="offset points", fontsize=7,
                color=FAIL, ha="right")
    for r in rows:
        ax.annotate(f"{r['V']:.1f} m/s", (r["CL"], r["xnp"] * 1000), xytext=(3, -10), textcoords="offset points",
                    fontsize=7, color=FG3)
    ax.set_xlabel("trim CL (gate mass 2.6 kg)")
    ax.set_ylabel("x from the wing LE (mm)")
    ax.set_ylim(46, 76)
    ax.legend(loc="upper right", ncol=2)
    fig.tight_layout()
    fig.savefig(FIG / "B3-V6-np-vs-cl.svg")
    plt.close(fig)


def fig_cnb():
    L = V["CALC-B3-V-LATDIR"]
    r4 = R4["CALC-B3-LATDIR"]
    cases = [("R4 model\n(0.275 x 0.21 rectangle)", r4["Cnb_avl"], r4["Cnb_props"], r4["Cnb_tubes"], r4["Cnb_pod"], FG3),
             ("As designed\nboard only", L["Cnb_avl_board"], L["Cnb_props"], L["Cnb_tubes"], L["Cnb_pod"], ACCENT),
             ("As designed\ntube as fin LE", L["Cnb_avl_tube"], L["Cnb_props"],
              L["Cnb_tube"] - L["Cnb_avl_tube"] - L["Cnb_props"] - L["Cnb_pod"], L["Cnb_pod"], ACCENT)]
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    lim = PAR["requirements"]["cnbeta_min"]["value"]
    for i, (lab, avl, pr, tb, pod, col) in enumerate(cases):
        tot = avl + pr + tb + pod
        ax.bar(i - 0.17, avl, width=0.3, color=col, alpha=0.35, edgecolor=col, lw=1.0)
        ax.bar(i + 0.17, tot, width=0.3, color=col, alpha=0.85 if tot >= lim else 0.25,
               edgecolor=FAIL if tot < lim else col, lw=1.2)
        ax.text(i - 0.17, avl + 0.0008, f"{avl:.4f}", ha="center", fontdict=MONO, color=FG2)
        word = "" if tot >= lim else "\nFAIL"
        ax.text(i + 0.17, tot + 0.0008, f"{tot:.4f}{word}", ha="center", fontdict=MONO,
                color=FAIL if tot < lim else FG)
    ax.axhline(lim, color=FG, lw=1.0, ls=(0, (4, 3)))
    ax.annotate(f"R-DIRECTIONAL >= {lim}", (2.45, lim), xytext=(0, 4), textcoords="offset points", fontsize=7,
                color=FG, ha="right")
    ax.set_xticks(range(len(cases)))
    ax.set_xticklabels([c[0] for c in cases])
    ax.set_ylabel("Cn_beta (1/rad), 1.3 Vs, aft limit")
    ax.set_ylim(0, 0.085)
    ax.text(0.0, -0.27, "left bar: AVL wing + fins; right bar: total with props (Ribner), tubes/motors and pod",
            transform=ax.transAxes, fontsize=7, color=FG3)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(FIG / "B3-V4-cnbeta.svg")
    plt.close(fig)


def fig_fin():
    f = V["cad_now"]
    fig, ax = plt.subplots(figsize=(6.0, 2.9))
    fle, fte, fh = PAR["fins"]["le_x_m"]["value"], PAR["fins"]["te_x_m"]["value"], PAR["fins"]["half_height_m"]["value"]
    ax.plot([fle * 1e3, fte * 1e3, fte * 1e3, fle * 1e3, fle * 1e3], [0, 0, fh * 1e3, fh * 1e3, 0], color=FG3, lw=1.0,
            ls=(0, (4, 3)), label=f"R4 model {(fte - fle) * fh * 1e4:.0f} cm2")
    xs = [x for x, z in V["cad_loop"]] if "cad_loop" in V else None
    if xs:
        zs = [z for x, z in V["cad_loop"]]
        ax.fill([x * 1e3 for x in xs], [z * 1e3 for z in zs], color=ACCENT, alpha=0.25, lw=0)
        ax.plot([x * 1e3 for x in xs + xs[:1]], [z * 1e3 for z in zs + zs[:1]], color=ACCENT, lw=1.5,
                label=f"CAD laminate {f['area_half_board'] * 1e4:.0f} cm2")
    xt, rt = f["x_tube_front"] + 0.011, 0.011
    ax.fill_between([f["x_tube_front"] * 1e3, (xt + rt) * 1e3], 0, f["z_collar_bottom"] * 1e3, color=FG2, alpha=0.25,
                    lw=0, label="22 mm motor tube")
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("z above the wing plane (mm)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "B3-V5-fin-outline.svg")
    plt.close(fig)


if __name__ == "__main__":
    fig_lattice()
    fig_cfd()
    fig_cg()
    fig_cnb()
    fig_fin()
    fig_npcl()
    print("wrote", sorted(p.name for p in FIG.glob("B3-V*.svg")))
