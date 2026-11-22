"""T-084: A-P9 static tip-over (narrow axis) on the DRAWN pads after the T3 change (FIN_H 0.1937), at the drawn and tallied CG and at both pack-trim ends.
Category: geometry arithmetic (rigid-body statics: tip angle = atan(lateral pivot distance / CG height above the ground plane)).
Inputs: cad/amodel (electrical.X_GROUND, common.FIN_H, pad box FIN_H-0.009..FIN_H+0.003 as landing_a.cad_geom), sitl/cad_mass.json (CG x / z, trim travel),
tallied CG = T083b_data/t083b_metrics.py method (+7.0 g undrawn shoe cups at x 298.1 mm, EST); trim ends = CG -/+ 270 g x trim_fwd / trim / basic (t083b_metrics.py).
Definitions: 'edge, toward CG' = pivot on the outer pad edge on the side the CG z is offset to (D-215 s4 definition of A-P9); 'centre' = landing_a.static() tip_narrow (pad centre,
CG z ignored; the T-066 structures_run.md number); 'centre, toward CG' = pad centre minus CG z (conservative bound named in D-215 s4).
Also the D-222 future pad (usable stroke 24 mm, X_GROUND 0.3475 = T-083 demand xf) as a sensitivity.   python -I t084_tipover.py > tipover_t084.txt"""
import os, sys, json, math
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.abspath(os.path.join(H, '..', '..', '..'))
sys.path.insert(0, os.path.join(A, 'cad')); sys.dont_write_bytecode = True
from amodel import electrical as E, common as C
j = json.load(open(os.path.join(A, 'sitl', 'cad_mass.json')))
Mb, cgx, cgz = j['mass_basic_kg']*1000, j['cg_x_m']*1000, j['cg_z_m']*1000
tf, ta = j['trim_fwd_m']*1000, j['trim_m']*1000
UND = (7.0, 298.1)
M2 = Mb+UND[0]; cg2 = (Mb*cgx+UND[0]*UND[1])/M2
zc, ze = (C.FIN_H-0.003)*1000, (C.FIN_H+0.003)*1000
def ang(w, h): return math.degrees(math.atan2(w, h))
rows = []
for xg, lab in ((E.X_GROUND*1000, 'drawn pad, X_GROUND %.1f' % (E.X_GROUND*1000)), (347.5, 'D-222 future pad, X_GROUND 347.5 (sensitivity)')):
    for tag, mb, c in (('drawn', Mb, cgx), ('tallied', M2, cg2)):
        for pos, cc in (('fwd trim end', c-270*tf/mb), ('nominal', c), ('aft trim end', c+270*ta/mb)):
            h = xg-cc
            rows.append((lab, tag, pos, cc, ang(ze-cgz, h), ang(zc, h), ang(zc-cgz, h), ang(ze+cgz, h)))
print(f"# A-P9 static tip-over, narrow axis (FIN_H {C.FIN_H*1000:.1f} mm, pad centre z {zc:.1f}, outer edge z {ze:.1f}, CG z {cgz:.2f} mm; basic {Mb:.1f} g drawn, {M2:.1f} g tallied)")
print("| ground plane | CG basis | pack position | CG x mm | **edge, toward CG (D-215 A-P9)** | centre (landing_a.static) | centre, toward CG (bound) | edge, away from CG | A-P9 30 deg / target 30.5 |")
print("|---|---|---|---|---|---|---|---|---|")
for r in rows:
    v = 'PASS (>= 30.5)' if r[4] >= 30.5 else ('PASS 30, below the 30.5 target' if r[4] >= 30 else 'FAIL')
    print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]:.2f} | **{r[4]:.2f}** | {r[5]:.2f} | {r[6]:.2f} | {r[7]:.2f} | {v} |")
mn = min(r[4] for r in rows if r[0].startswith('drawn'))
print(f"\nMinimum on the drawn pads (edge, toward CG): {mn:.2f} deg (margin {mn-30:+.2f} over A-P9 30, {mn-30.5:+.2f} over the D-215 target 30.5).")
print(f"Before T-084 (FIN_H 180, T066 structures_run.md): centre 29.2 deg at CG 21.08; edge toward CG {ang(183-6.50, 337.5-21.08):.2f} deg.")
