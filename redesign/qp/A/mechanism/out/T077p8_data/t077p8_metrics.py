"""T-077 p8 COPY of the p7 metrics script (unchanged formulas; adds the mass ceiling and the SM-5 % CG line). T-077 p7 COPY of the p6 (= p5) metrics script (undrawn tally is now only the enlarged root blocks and the shoe cups; R2, R3fix, R4, H743, node and clamshell are drawn): CG, SM, predicted mass, transition window, T/W and bench derate lines for the part-4 CAD (geometry arithmetic + prop_a.py model).  CATEGORY: geometry arithmetic + illustrative (prop_a is an EST model).
    python -I t077p4_metrics.py       reads sitl/cad_mass.json (written by the gate run); tally of the decided-but-undrawn items from CG-closure s1.1 (EST)."""
import json, os, sys, math
A = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')); sys.path.insert(0, A); sys.dont_write_bytecode = True
os.chdir(A)
import prop_a as P
j = json.load(open(os.path.join(A, 'sitl', 'cad_mass.json'))); M = j['mass_basic_kg'] * 1000; cg = j['cg_x_m'] * 1000
NP, C = 40.7, 245.0
# undrawn decided items (g, x mm), docs/audits/2026-11-21-CG-closure.md s1.1; R3fix cups sit on the cage, so x -73.6 -> -85.6 after the 12 mm shift
UND = [('enlarged root blocks +12.2 g at 283.1', 12.2, 283.1), ('shoe cups +7 g at 298.1', 7.0, 298.1)]   # T-068 / CG-closure s1.1: still undrawn, EST
dm = sum(u[1] for u in UND); mom = sum(u[1] * u[2] for u in UND)
M2 = M + dm; cg2 = (M * cg + mom) / M2
print('drawn basic %.1f g, CG %.2f mm, SM %.2f %%' % (M, cg, 100 * (NP - cg) / C))
print('undrawn tally %+.2f g -> basic %.1f g, CG %.2f mm, SM %.2f %%  (EST)' % (dm, M2, cg2, 100 * (NP - cg2) / C))
for tag, mb in (('drawn', M), ('tally', M2)):
    mp = mb / 1000 * 1.1174 + 0.032 * 1.47           # CALC-A-MASS-PRED form (CG-closure s0 row 1): basic x 1.1174 + 0.032 x 1.47
    cf, cs = P.cap_sched(16.8, mp), P.cap_sched(14.92, mp)
    fr = P.tw_state(16.8, cf, mp, 0.93)[0]; sg = P.tw_state(14.92, cs, mp, 0.93)[0]
    d = 0.97
    print('[%s] predicted mass %.4f kg; derate 0.93: T/W fresh %.3f (with 3 %% download %.3f), sag %.3f (with download %.3f); window %.2f %% (no download), %.2f %% (with download)' % (tag, mp, fr, fr * d, sg, sg * d, P.window_pct(sg), P.window_pct(sg * d)))
    tw_need = 1.33 * 1.05 / 0.95 / 0.80
    print('   bench derate line: A-P3 (window 5 %%, with download) %.3f ; A-P2 fresh 2.0 without download %.3f, with download %.3f' % (0.93 * tw_need / (sg * d), 0.93 * 2.0 / fr, 0.93 * 2.0 / (fr * d)))
    print('   mass ceiling for window 5 %% at derate 0.93 with download: see prop_a --sched; sag T/W (sched, with download) %.3f vs 1.6' % (sg * d))
# ---- T-077 p8 additions: CG limits and the mass ceiling for window 5 % at derate 0.93 with the download (bisection on the same prop_a model)
def win_dl(mp, der=0.93):
    cs = P.cap_sched(14.92, mp); sg = P.tw_state(14.92, cs, mp, der)[0]; return P.window_pct(sg * 0.97)
lo, hi = 1.5, 1.9
for _ in range(40):
    mid = 0.5 * (lo + hi)
    if win_dl(mid) >= 5.0: lo = mid
    else: hi = mid
print('mass ceiling for window 5 %% at derate 0.93 with download: predicted %.4f kg = basic %.1f g' % (lo, (lo - 0.032 * 1.47) / 1.1174 * 1000))
print('CG limits: A-P4 band 19.3..26.0 mm (tallied <= 25.0, T-077 p7 P7.4), SM 5 %% at CG %.2f mm; tallied CG %.2f mm -> SM %.2f %%' % (NP - 0.05 * C, cg2, 100 * (NP - cg2) / C))
