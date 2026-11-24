"""D-195 (QP-5): wing bending-torsion flutter with the CAD of 2026-11-15. python -I flutter_d195_wing.py -> flutter_d195_wing.md (numpy, scipy; ~1 min)
Uses flutter_a.py unchanged with the FIXES2 settings (foam 25 kg/m3, elevon to y 0.35, hinge at 0.75 c) plus the new masses:
elevon 6.7 g (was 9.6), per semispan on the wing at y 0.285: lead 15.6 + tabs 0.5 + two lens caps 2 x 3.98 g (4 caps 15.9 g, CAD-INTEGRATION s2) + half of the 5.0 g hinge dampers = 26.6 g (FIXES2 lumped 18.1 g) at x 0.164 m (20 mm ahead of the hinge).
Elevon-hinge-free wing modes; the damper stiffness is not credited."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flutter_a as F
import fixes2_run as R
L = []
def P(s=""): print(s, flush=True); L.append(s)
R.setup(0.0067, 0.25)
lump = (((15.6 + 0.5 + 2 * 3.98 + 2.5) * 1e-3, 0.18375 - 0.020, 0.285),)
P("| case | corner | f1 / f2 / f3 (Hz) | flutter V (m/s) | x 28.8 line |"); P("|---|---|---|---|---|")
for nm, kw in (("fin on tip (base)", dict()), ("fins off (worst sensitivity)", dict(fins=False))):
    for k in ("kd", "nom", "hi"):
        f, ff = F.wing_flutter(k, lumps=lump, **kw)
        P("| %s | %s | %.1f / %.1f / %.1f | %s | %s |" % (nm, k, f[0], f[1], f[2], "%.1f" % ff[0] if ff else ">100", ("PASS" if (not ff or ff[0] >= F.VREQ) else "FAIL")))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "flutter_d195_wing.md"), "w").write("\n".join(L))
