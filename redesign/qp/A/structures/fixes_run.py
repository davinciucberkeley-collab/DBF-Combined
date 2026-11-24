"""QP-4 FIXES (D6/D1): elevon balance v2 (D-187), elevon span 0.04-0.35, foam 25 kg/m3: flutter, reversal.  python -I fixes_run.py -> fixes_run.md
Uses flutter_a.py unchanged except the added options FOAM_RHO, ritz(lumps=), first_flutter(gthr=)."""
import math, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flutter_a as F
L = []
def P(s=""): print(s, flush=True); L.append(s)
Ks = (0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)
def fmt(ff): return "%.0f" % ff[0] if ff else ">100"
def elev_table(title, fh, fa, ME, span, arm, mlead_g, gs_list=(0.0, 0.02)):
    F.ME_EL = ME; F.EL_Y1 = F.EL_Y0 + span
    P("**%s** (elevon %.1f g, span %.2f m, lead %.1f g at %.0f mm ahead of the hinge; moment %.0f g mm vs elevon %.0f g mm)" % (title, ME*1e3, span, mlead_g, arm*1e3, mlead_g*arm*1e3, ME*1e3*0.35*F.EL_CF*F.CH*1e3))
    P("| structural damping g_s | " + " | ".join("K=%g" % k for k in Ks) + " |"); P("|---|" + "---|"*len(Ks))
    for gs in gs_list:
        row = []
        for Kb in Ks:
            ff = F.elevon_flutter(fh, fa, Kb, gthr=gs, xb_bal=arm, mbal=(mlead_g*1e-3/span if mlead_g > 0 else 0.0)); row.append(fmt(ff))
        P("| %.2f | %s |" % (gs, " | ".join(row)))
    P()
# --- A. reference: as drawn in QP-4 (foam 30, span .30, ME 10 g, 10.7 g at 30 mm, wing without balance lump)
F.FOAM_RHO = 30.0; F.EL_Y1 = 0.34; F.ME_EL = 0.010
f0, ff0 = F.wing_flutter("nom"); fh0, fa0 = f0[0], f0[1]
P("## 1 Elevon flutter, speeds in m/s (G8 28.8; target >= 37)"); P()
P("Wing modes from the Ritz run (nom): QP-4 reference f_h %.1f / f_alpha %.1f Hz." % (fh0, fa0)); P()
elev_table("A. QP-4 as drawn (10.7 g at 30 mm)", fh0, fa0, 0.010, 0.30, 0.030, 10.7)
# --- B. new design
LEAD_G, HORN_G, CAP_G = 15.6, 0.5, 1.0
lump = (LEAD_G+HORN_G)*1e-3     # caps sit on the fixed wing: not in the elevon lump but in the wing lump below
F.FOAM_RHO = 25.0; F.EL_Y1 = 0.35
lumps = ((( LEAD_G+HORN_G+2*CAP_G)*1e-3, 0.18375-0.020, 0.285),)
f1, ff1 = F.wing_flutter("nom", lumps=lumps); fh1, fa1 = f1[0], f1[1]
P("New design wing modes with the balance lump (13.3 g lead + 0.5 horn + 2 caps, 25 kg/m3 foam): f_h %.1f / f_alpha %.1f Hz." % (fh1, fa1)); P()
elev_table("B. D-187 v2 SELECTED: 15.6 g lead strip + 0.5 g tabs, 20 mm ahead of the hinge, elevon y 0.04-0.35, foam 25", fh1, fa1, 0.0096, 0.31, 0.020, LEAD_G+HORN_G)
elev_table("B'. same, lead 12.8 g + 0.5 tabs (lighter; passes only with g_s 0.02)", fh1, fa1, 0.0096, 0.31, 0.020, 13.3)
elev_table("B''. same, lead 17.0 g (heavier, margin check)", fh1, fa1, 0.0096, 0.31, 0.020, 17.5)
# --- C. wing flutter, divergence with the new masses
P("## 2 Wing bending-torsion flutter with the balance lumps on the wing (V m/s; G8 28.8)"); P("| case | kd | nom | hi |"); P("|---|---|---|---|")
def wrow(nm, **kw):
    r = []
    for k in ("kd", "nom", "hi"):
        f, ff = F.wing_flutter(k, **kw); r.append("%.1f" % ff[0] if ff else ">100")
    P("| %s | %s |" % (nm, " | ".join(r)))
F.FOAM_RHO = 30.0; wrow("QP-4 reference (foam 30, no balance lump)")
F.FOAM_RHO = 25.0
wrow("foam 25, no balance lump"); wrow("foam 25 + balance lumps (D-187 v2)", lumps=lumps)
wrow("foam 25 + balance lumps, fins off (worst)", lumps=lumps, fins=False)
wrow("foam 25 + balance lumps, strip lift x0.59 (3-D)", lumps=lumps, cl_scale=0.59)
P()
# --- D. reversal with the longer elevon
P("## 3 Control reversal, elevon y 0.04-0.35 (V m/s; 3-D lift / 2-D strip)"); P("| corner | e/c | 3-D | 2-D |"); P("|---|---|---|---|")
for yy in (0.34, 0.35):
    F.EL_Y1 = yy
    for k in ("kd", "nom"):
        GJ = sum(F.GJ_parts(k))
        q3, _ = F.reversal(GJ, 0.10); q2, _ = F.reversal(GJ, 0.10, scale=F.CLA2D/F.CLA3D)
        P("| %s, y1 %.2f | 0.10 | %.0f | %.0f |" % (k, yy, math.sqrt(2*q3/F.RHO), math.sqrt(2*q2/F.RHO)))
P()
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixes_run.md"), "w").write("\n".join(L))
