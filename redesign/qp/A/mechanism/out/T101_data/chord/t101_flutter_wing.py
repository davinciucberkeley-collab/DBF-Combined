"""T-101 U2 COPY of structures/flutter_d205_wing.py: wing bending-torsion flutter with the 0.30 c elevon. python -I t101_flutter_wing.py [new|old] -> flutter_wing_t101.md / flutter_wing_t101_old.md
new: R.setup(0.0076, 0.30); lump per semispan = lead 10.0 + tabs 0.5 + two lens caps WNG-008 (3.69 upper + 3.72 lower, STOP_CHECK/cad interfaces) + half of the 5.0 g dampers 2.5 (CAD WNG-009 2.0 + WNG-010 0.47 = 2.47 g) at x XH - 20 mm = 0.1715 - 0.020, y 0.285.
old: R.setup(0.0067, 0.25); caps 3.72 + 3.75 (git HEAD STOP_CHECK.md), x 0.18375 - 0.020 (like-for-like baseline)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SD = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "structures"))
sys.path.insert(0, SD)
import flutter_a as F
import fixes2_run as R
mode = sys.argv[1] if len(sys.argv) > 1 else "new"
L = []
def P(s=""): print(s, flush=True); L.append(s)
# modes: new = 0.30 c, lead 14.0 g (ladder rung b), caps = CAD part masses 3.69 + 3.72; newstop = same, caps from the post-ladder STOP_CHECK.md 3.10 + 3.15;
# new10 = 0.30 c with the pre-ladder lead 10.0 g; old = pre-change baseline (lead 10.0 g, caps HEAD STOP_CHECK 3.72 + 3.75)
LEAD = 14.0
if mode == "new": me, cf, caps, xh = 0.0076, 0.30, 3.69 + 3.72, 0.1715
elif mode == "newstop": me, cf, caps, xh = 0.0076, 0.30, 3.10 + 3.15, 0.1715
elif mode == "new10": me, cf, caps, xh, LEAD = 0.0076, 0.30, 3.69 + 3.72, 0.1715, 10.0
else: me, cf, caps, xh, LEAD = 0.0067, 0.25, 3.72 + 3.75, 0.18375, 10.0
R.setup(me, cf)
lump = (((LEAD + 0.5 + caps + 2.5) * 1e-3, xh - 0.020, 0.285),)
P("Mode %s: elevon %.1f g, cf %.2f, lead %.1f g, lump %.2f g at x %.4f m, y 0.285" % (mode, me * 1e3, cf, LEAD, lump[0][0] * 1e3, lump[0][1])); P()
P("| case | corner | f1 / f2 / f3 (Hz) | flutter V (m/s) | x 28.8 line |"); P("|---|---|---|---|---|")
for nm, kw in (("fin on tip (base)", dict()), ("fins off (worst sensitivity)", dict(fins=False))):
    for k in ("kd", "nom", "hi"):
        f, ff = F.wing_flutter(k, lumps=lump, **kw)
        P("| %s | %s | %.1f / %.1f / %.1f | %s | %s |" % (nm, k, f[0], f[1], f[2], "%.1f" % ff[0] if ff else ">100", ("PASS" if (not ff or ff[0] >= F.VREQ) else "FAIL")))
open(os.path.join(HERE, "flutter_wing_t101.md" if mode == "new" else "flutter_wing_t101_%s.md" % mode), "w").write("\n".join(L))
