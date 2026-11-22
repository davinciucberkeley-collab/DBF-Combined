"""T-083 mass / CG / SM / window / T-W / A-P6 / cruise for the X2216 tree. Category: geometry arithmetic (CAD part table via sitl/cad_mass.json) + illustrative
(prop_a.py EST model through t083_prop.metrics). Same undrawn tally as T-077 p8 (enlarged root blocks +12.2 g at 283.1 mm, shoe cups +7.0 g at 298.1 mm, EST),
plus the rib-coupon variant (25x23 -> 14x12: -23.8 g, -2.4 mm x 1,598 / basic, T-077 p8 P8.4).  python -I t083_metrics.py  (prints; writes nothing)"""
import json, os, sys, math
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.abspath(os.path.join(H, '..', '..', '..'))
sys.path.insert(0, H); sys.dont_write_bytecode = True
import t083_prop as T
import t083_packcap as PC
j = json.load(open(os.path.join(A, 'sitl', 'cad_mass.json')))
M, cg = j['mass_basic_kg'] * 1000, j['cg_x_m'] * 1000
NP, C = 40.7, 245.0
UND = [('enlarged root blocks', 12.2, 283.1), ('shoe cups', 7.0, 298.1)]
M2 = M + sum(u[1] for u in UND); cg2 = (M * cg + sum(u[1] * u[2] for u in UND)) / M2
RIB_DM, RIB_DX = -23.8, -2.4 * 1598.4 / M2        # P8.4: -23.8 g, -2.4 mm at the p8 basic; scaled to this basic
M3, cg3 = M2 + RIB_DM, cg2 + RIB_DX * M2 / (M2 + RIB_DM)
trim_f, trim_a = j.get('trim_fwd_m', 0.006) * 1000, j.get('trim_m', 0.010) * 1000
print('| State | basic g | pred kg | CG mm | SM % | fwd / aft trim CG mm | window % (dl) | T/W fresh dl | T/W sag dl | cruise s | 1.3 Vs m/s |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for tag, mb, c_ in (('T-083 as drawn (cad_mass.json)', M, cg), ('T-083 tallied (+ root blocks, shoe cups; EST)', M2, cg2), ('T-083 tallied, rib 14x12 (coupon >= line)', M3, cg3)):
    mp = T.pred(mb)
    cf, cs, twf, tws, w, pf, ps = PC.state(mp, 72.0)
    m_ = T.metrics(mp)
    tf, ta = c_ - 270 * trim_f / mb, c_ + 270 * trim_a / mb
    print(f"| {tag} | {mb:.1f} | {mp:.4f} | {c_:.2f} | {100*(NP-c_)/C:.2f} | {tf:.2f} / {ta:.2f} | {w:+.2f} | {twf:.3f} | {tws:.3f} | {m_['cruise_s']:.0f} | {m_['k13vs']:.2f} |")
print('\nLimits: A-P4 CG 19.3..26.0 mm, hard aft 28.5 (trim end), SM >= 5 %% (CG <= %.2f mm); A-P3 window >= +5 %%; A-P2 T/W fresh >= 2.0, sag >= 1.6 (with the 3 %% download); A-P6 1.3 Vs <= 17.0 m/s; cruise >= 204.6 s.' % (NP - 0.05 * C))
print('T/W and window with Q_M_BAT_CURR_MAX 72 A (t083_packcap.state); cruise and 1.3 Vs from t083_prop.metrics (pack 2.8 Ah).')
