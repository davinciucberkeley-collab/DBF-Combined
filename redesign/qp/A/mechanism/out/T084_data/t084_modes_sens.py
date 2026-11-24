"""T-084 (FEA-lite, beam FE fe_a.py): one-at-a-time sensitivity of the D-185 in-band mode (cage lateral sway against wing in-plane bending) and candidate fixes.
Reports, per variant and corner: every strongly coupled mode (cx or cy >= 0.5) inside the excluded band 94-321 Hz (structures_a rule, T-066), and the cy-max mode in 120-330 Hz.
python -I t084_modes_sens.py > modes_sens.txt"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.dont_write_bytecode = True
from t084_modes_probe import fe_a, fekw, BAND
def run(kind, **over):
    F, info = fe_a.build(kind, **fekw(**over)); res = F.solve(130)
    inb = [(f, cx, cy) for (f, e, v, cx, cy) in res if (cx >= 0.5 or cy >= 0.5) and BAND[0] <= f <= BAND[1]]
    cand = max([(cy, f, cx) for (f, e, v, cx, cy) in res if 120 <= f <= 330])
    return inb, cand
VAR = [("current CAD (T-066 basis)", {}),
       ("-- iter3 values, one at a time --", None),
       ("motor_g 88.26 (MN2212 station, iter3)", dict(motor_g=88.26)),
       ("hub_extra_g 20 (PETG hub, iter3)", dict(hub_extra_g=20.0)),
       ("centre_extra_g 65 (iter3)", dict(centre_extra_g=65.0)),
       ("avionics_g 110 (iter3)", dict(avionics_g=110.0)),
       ("pack_g 270 (iter3)", dict(pack_g=270.0)),
       ("wing_g 212 (iter3)", dict(wing_g=212.0)),
       ("bridge 12x10 (iter3)", dict(bridge_tube=(0.012, 0.010))),
       ("struts 6x4.5 (iter3)", dict(vtube=(0.006, 0.0045))),
       ("strut end y 0.30 (iter3)", dict(bridge_yv=0.30)),
       ("x_hub -0.075 (iter3)", dict(x_hub=-0.075)),
       ("rib 14x12 (iter3)", dict(rib_tube=(0.014, 0.012))),
       ("root_g 6 (iter3)", dict(root_g=6.0)),
       ("-- candidate fixes --", None),
       ("struts 10x8", dict(vtube=(0.010, 0.008))),
       ("struts 12x10", dict(vtube=(0.012, 0.010))),
       ("bridge 20x18", dict(bridge_tube=(0.020, 0.018))),
       ("arms 14x12", dict(arm_tube=(0.014, 0.012))),
       ("arms 16x14", dict(arm_tube=(0.016, 0.014))),
       ("strut end y 0.20", dict(bridge_yv=0.20)),
       ("strut end y 0.228", dict(bridge_yv=0.228)),
       ("strut end y 0.35", dict(bridge_yv=0.35)),
       ("spar 14x12", dict(spar_tube=(0.014, 0.012))),
       ("pack 30 g lighter at hub (info)", dict(pack_g=fekw()['pack_g']-30)),
       ]
if __name__ == '__main__':
    print("| variant | kd strong-in-band (f, cx, cy) | nom | hi | max-cy mode 120-330 Hz nom (cy, f) |"); print("|---|---|---|---|---|")
    for name, ov in VAR:
        if ov is None: print(f"| {name} | | | | |"); continue
        row = []; cn = None
        for kind in ('kd', 'nom', 'hi'):
            inb, cand = run(kind, **ov); row.append("; ".join(f"{f:.0f} ({cx:.2f}/{cy:.2f})" for f, cx, cy in inb) or "none")
            if kind == 'nom': cn = cand
        print(f"| {name} | {row[0]} | {row[1]} | {row[2]} | {cn[0]:.3f} @ {cn[1]:.0f} |", flush=True)
