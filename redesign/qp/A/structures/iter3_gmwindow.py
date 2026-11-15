"""Tap-test window for the rate-loop clause: GM vs a uniform scale s on all cage flexible modes (A.param gains). python -I iter3_gmwindow.py (~3 min); appends to iter3_run.md"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "sitl")); sys.dont_write_bytecode = True
import fu_cage as FC
C = FC.cases(); corners = ("kd", "nom", "hi"); OUT = []
def P(s=""): print(s); OUT.append(s)
SET = {"pit": dict(gyro_lpf=60, fltd=40, P=0.15, D=0.002), "rll": dict(gyro_lpf=60, fltd=32, P=0.20, D=0.003)}
P("\n### Tap-test window (rate-loop clause)\nLowest GM, zeta 0.3 %, thrust x0.77 / x1.25, every flexible mode scaled by s (first cage mode Hz in brackets), IMU at the spar centre:")
P("| s | pit kd | pit nom | pit hi | rll kd | rll nom | rll hi |"); P("|---|---|---|---|---|---|---|")
win = {}
for sc in (0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5):
    row = []
    for ax in ("pit", "rll"):
        for k in corners:
            c = [x for x in C if x["ax"] == ax and x["node"] == "spar centre" and x["k"] == k][0]
            modes = [(ff*sc if ff >= 1.0 else ff, gg) for ff, gg in c["modes"]]
            gm = 99.0
            for ts in (0.77, 1.25):
                L = FC.loop(modes, ax, 0.003, tfull_scale=ts, **SET[ax])
                gm = 1.0 if FC.maxre(L) >= -1e-6 else min(gm, FC.margins(L)[0])
            f1 = [ff for ff, gg in c["flex"] if ff > 3][0] if ax == "pit" else [ff for ff, gg in c["flex"] if ff > 20][0]
            row.append(f"{gm:.2f} ({f1*sc:.0f})"); win.setdefault((ax, k), []).append((gm, f1*sc))
    P(f"| {sc:.1f} | " + " | ".join(row) + " |")
for key, v in win.items():
    okf = [f for g, f in v if g >= 2.0]
    P(f"- {key[0]} {key[1]}: GM >= 2 for the first cage mode (pit: ~12 Hz mode; rll: ~31 Hz) from {min(okf):.0f} to {max(okf):.0f} Hz (grid)" if okf else f"- {key[0]} {key[1]}: never >= 2")
open(os.path.join(HERE, "iter3_run.md"), "a").write("\n".join(OUT)+"\n")
