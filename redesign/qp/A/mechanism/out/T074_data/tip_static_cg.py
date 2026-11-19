"""T-074 check 3 step 3: A-P9 static tip-over (T-068 D2 pad: ground plane x 0.3415, pad centre z 0.189, edge 0.195) versus CG x.  Same formula as landing_tip_b.stat().
Category: static geometry.  CG z = CAD 6.37 mm (cad_mass.json); mass does not enter a static tip-over.  python -I tip_static_cg.py"""
import math, json, os
cm = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'sitl', 'cad_mass.json')))
cgz = cm['cg_z_m']
print("CG x mm | h = xg - cgx mm | edge angle deg (A-P9 >= 30; T-068 target 30.5) | pad-centre angle deg (conservative bound)")
for cgx in (19.3, 20.0, cm['cg_x_m']*1e3, 22.0, 24.0, 26.0):
    h = 0.3415 - cgx*1e-3
    print(f"{cgx:6.2f} | {h*1e3:6.1f} | {math.degrees(math.atan2(0.195-cgz, h)):6.2f} | {math.degrees(math.atan2(0.189-cgz, h)):6.2f}")
