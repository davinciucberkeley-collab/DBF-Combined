"""T-097 plots (illustrative renderings of the rerun time histories). env for the landing part: LAND_MASS_KG=1.881 LAND_MASS_MODEL=cad LAND_PART_TABLE=<cad_part_table_t097.json>"""
import os, sys, csv, json, math
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, "..", "T097_plots"))
os.makedirs(OUT, exist_ok=True)
A = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
# ---- SITL
def load(tag):
    d = os.path.join(A, "sitl", "runs", tag); f = list(csv.DictReader(open(os.path.join(d, "case.fwd.csv")))); res = json.load(open(os.path.join(d, "result.json")))
    return {k: np.array([float(r[k]) for r in f]) for k in f[0]}, res
for tag, name in (("T097_Z5", "sitl_Z5_gb0_1881kg"),):
    f, res = load(tag); mk = res["marks"]; t = f["t"] - mk["t_qstab"]; sel = (t > -5) & (t < 60)
    fig, ax = plt.subplots(4, 1, figsize=(8, 8), sharex=True)
    ax[0].plot(t[sel], f["alt"][sel]); ax[0].set_ylabel("altitude (m)"); ax[1].plot(t[sel], f["V"][sel]); ax[1].set_ylabel("airspeed (m/s)")
    ax[2].plot(t[sel], f["pitch"][sel]); ax[2].set_ylabel("pitch (deg)"); ax[3].plot(t[sel], 0.5 * (f["dl"][sel] + f["dr"][sel]), label="mean elevon"); ax[3].axhline(9, ls="--", c="r", lw=0.8, label="0.60 x 15 deg"); ax[3].axhline(-9, ls="--", c="r", lw=0.8)
    ax[3].set_ylabel("elevon (deg)"); ax[3].set_xlabel("time from QSTABILIZE (s)"); ax[3].legend(fontsize=8)
    for a in ax: a.axvline(mk["t_fbwa"] - mk["t_qstab"], c="gray", lw=0.6); a.grid(alpha=0.3)
    fig.suptitle("T-097 SITL transition, 1.881 kg, X2216 model (flight dynamics, EST plant)"); fig.tight_layout(); fig.savefig(os.path.join(OUT, name + ".png"), dpi=130); plt.close(fig)
# ---- landing foot loads
sys.path.insert(0, os.path.abspath(os.path.join(A, "structures"))); import landing_a as L
cases = {"hard level": dict(v_sink=1.2), "hard 10 narrow + drift .5": dict(v_sink=1.2, th_n=10, drift=0.5, drift_dir=0.0)}
fig, ax = plt.subplots(len(cases), 1, figsize=(8, 6), sharex=True)
for a, (n, kw) in zip(ax, cases.items()):
    r = L.simulate(Fp=30.0, trace=True, T=0.6, **kw); tr = r["trace"]; t = np.arange(len(tr)) * 1e-4
    for i in range(4): a.plot(t, np.abs(tr[:, 3 * i]), label=f"foot {i+1}")      # body x = foot normal axis (stance)
    a.set_ylabel("foot normal force (N)"); a.set_title(f"{n}: stroke max {r['dmax_mm'].max():.1f} mm, n {r['n_peak']:.1f} g", fontsize=9); a.grid(alpha=0.3); a.legend(fontsize=7, ncol=4)
ax[-1].set_xlabel("time from first touch (s)"); fig.suptitle("T-097 landing_a, 1.881 kg CAD mass model, plateau 30 N (rigid-body dynamics; EST foam)"); fig.tight_layout(); fig.savefig(os.path.join(OUT, "landing_30N_1881kg.png"), dpi=130)
print("plots done")
