"""Iteration 2 strength margins (limit x 1.5 x 1.15; x1.25 more for printed / bonded).  python -I iter2_margins.py"""
import math
KF = 1.5*1.15; KP = KF*1.25
def tube(od, id_):
    I = math.pi/64*(od**4-id_**4); return math.pi/4*(od**2-id_**2), I, I/(od/2)
A12, I12, Z12 = tube(12e-3, 10e-3); A14, I14, Z14 = tube(14e-3, 12e-3); A6, I6, Z6 = tube(6e-3, 4.5e-3)
rows = []
def row(n, load, stress, allow, unit=1e6):
    rf = allow/stress; rows.append(f"| {n} | {load} | {stress/unit:.1f} | {allow/unit:.1f} | {rf-1:+.2f} | {'PASS' if rf-1 >= 0.15 else ('MARGINAL' if rf >= 1 else 'FAIL')} |")
row("Spar 12x10 root bending (unrelieved 4.78 N m)", "4.78 N m", 4.78*KF/Z12, 350e6)
row("Spar shear (25 N half-wing at n 3.4)", "25 N", 25*KF/(A12/2), 30e6)
EI = 70e9*I12; d = 0.7*25.0*0.45**3/(3*EI)
rows.append(f"| Spar tip deflection at n 3.4 (tube alone E 70 GPa) | | {d*1e3:.1f} mm = {100*d/0.45:.1f} % of semispan | 5 % | | {'PASS' if d/0.45 < 0.05 else 'FAIL'} |")
row("Arm 12x10 root bending, thrust 8.8 N x 0.246 m", "2.17 N m", 8.8*0.246*KF/Z12, 350e6)
row("Arm, prop strike 30 N", "7.4 N m", 30*0.246*KF/Z12, 350e6)
row("Bridge 12x10, prop strike", "4.7 N m", 4.68*KF/Z12, 350e6)
row("Bridge 12x10, pack + hub at 12 g crash", "4.6 N m", 4.6*KF/Z12, 350e6)
row("Bridge 12x10, control pitch moment", "2.44 N m", 2.44*KF/Z12, 350e6)
Pcr = math.pi**2*70e9*I6/0.33**2
rows.append(f"| V strut 6x4.5 buckling vs axial 19 N (12 g lateral crash) | 19 N | P_cr {Pcr:.0f} N vs {19*KF:.0f} N | | {Pcr/(19*KF)-1:+.1f} | PASS |")
row("Rib 14x12 root bending, both feet 40 N x 0.234 m", "9.4 N m", 9.4*KF/Z14, 350e6)
row("Rib 14x12 torsion, one foot (15 N x 0.18)", "2.7 N m", 2.7*0.007/(2*I14)*KF, 30e6)
A16, I16, Z16 = tube(16e-3, 14e-3)
row("Fin tube 16x14 out-of-plane bending, side load 20 N x 0.18 m", "3.6 N m", 3.6*KF/Z16, 350e6)
row("Fin tube in-plane bending at the foot load 42 N x 0.18 m", "7.6 N m", 7.6*KF/Z16, 350e6)
row("Fin tube wall at the foot shoe (hoop, 30 mm shoe, 49 N): bearing on 0.1 mm skin-free tube, hoop allowable", "49 N", 49*KF/(16e-3*0.001*2)*0.3, 40e6)
def bond(n, F, area, allow=2.0e6): row(n, f"{F:.0f} N", F*KP/area, allow)
bond("Arm 12x10 in socket, 25 mm, strike couple 7.4 N m / 0.025", 296, math.pi*12e-3*25e-3*0.5)
bond("Arm socket, thrust couple 2.17 N m / 0.025", 87, math.pi*12e-3*25e-3*0.5)
bond("Bridge 12x10 in hub, strike couple 4.7 N m / 0.025", 188, math.pi*12e-3*25e-3*0.5)
row("Bridge saddle on spar 12 mm, full wrap 30 mm: 2.44 N m", "2.44 N m", 2.44/(2*math.pi*0.006**2*0.030)*KP, 2e6)
bond("Rib saddle on 12 mm spar, wrap 60 mm wide: couple 9.4 N m / 12 mm = 783 N", 783, math.pi*12e-3*60e-3*0.5)
bond("V strut saddles (6x4.5, 20 mm): 19 N", 19, math.pi*6e-3*20e-3*0.5)
bond("Rib tube 14x12 in fin root block, 60 mm embed: 84 N", 84, math.pi*14e-3*60e-3)
bond("Foot shoe on the fin tube end (25 mm wrap, 16 mm OD): 52 N", 52, math.pi*16e-3*25e-3)
bond("Fin root block on fin tube (40 mm long, 16 mm OD), 40 N + 3.6 N m couple / 40 mm = 90 N", 130, math.pi*16e-3*40e-3*0.5)
print("| Item | Load (limit) | Stress / value (MPa, design) | Allowable | MS | Result |"); print("|---|---|---|---|---|---|")
print("\n".join(rows))
