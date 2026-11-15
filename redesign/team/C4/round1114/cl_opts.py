"""C4 closure round 2026-11-14: knock-down levers in the 3-D hex8 station-mode model (sim_fin.modes_level).
Scratch only: writes round1114/out/cl_<case>_<side>.json, never a claims file. Results go to the shared sim cache.

  python -I cl_opts.py <case> <side> <levels, e.g. 2 or 123>

Cases (all on the R6 geometry and B4 wave-2 rpm as read from the graph inputs of CALC-C4-SIM-MODES):
  knock         tube E 78.6 / G 10.27 GPa (C4-W2 section 4), as designed
  knock_c05     knock + cheeks +0.5 mm (k_rock 2 550, mount +0.85 g)
  knock_c10     knock + cheeks +1.0 mm (k_rock 2 800, mount +1.69 g)
  nom_c10       page tube 90.2 / 20.5 GPa + cheeks +1.0 mm
  knock_k3000   knock + k_rock 3 000 (no mass change; sensitivity)
k_rock values = CALC-C4-D3-MOUNT-K-EST with the thicker cheeks at ASA E 1.8 GPa (low end of ASM-C4-ASA-E's TDS range
1.8-2.3 GPa), rounded down. Mount mass / CG: cl_mount.py.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "sim"))
sys.path.insert(0, str(HERE))

KNOCK = {"E": 78.6e9, "G": 10.27e9}
# D-173: SunnySky X2814 V3 KV900 108 g (+3.2 g screws as in ASM-C4-A3-STATION-MASS) = 111.2 g; can 9.5 mm longer than
# the X3108S, so the prop stack 37.3 -> 46.8 mm (P:fin_detail.mount.prop_stack_m + 9.5 mm, EST until D3); bell inertia
# ASM-C1-BELL-INERTIA 1.5e-5 x 108 / 81 = 2.0e-5 (EST, mass ratio)
D173_MOTOR, D173_STACK, D173_IBELL = 0.1112, 0.0468, 2.0e-5
CF2220 = {"od": 0.022, "idd": 0.020, "mu": 0.102}            # SRC-CF-TUBE roll-wrapped 22 x 20, wing.spar mass/m
CF2220_NOM, CF2220_LO = {"E": 100e9, "G": 5e9}, {"E": 70e9, "G": 3e9}   # ASM-J1-E-TUBE / ASM-C4-G-TUBE; -LO corner
R4_MOUNT = [0.00988, -0.0046, 0.0005, -0.0097]               # R4 CAD 11.28 g less 1.40 g hardware at (0.0404, ., 0.1803)
R5_MOUNT = [0.01054, -0.0085, 0.0005, -0.0086]               # R5 CAD 11.94 g less 1.40 g hardware at (0.0365, ., 0.1814)
KR_F75, KR_CF, KR_CF30, KR_CF_F75_30 = 2000.0, 2000.0, 3600.0, 3400.0   # cl_mount K-EST at ASA 1.8 GPa, rounded down
KR15 = 2900.0   # D-164 cheeks +1.5: CALC-C4-D3-MOUNT-K-EST 3 255 at 2.0 GPa, 2 929 at 1.8 GPa, rounded down
# mount tuple [kg, dx, dy, dz] from cl_mount.py (cheeks thickened outward, ASA 1.07 g/cm3, solid)
MOUNT_C05 = None
MOUNT_C10 = None


def mount_for(dt):
    import cl_mount
    return cl_mount.mount_tuple(dt)


CASES = {
    "knock": ({}, KNOCK, None),
    "knock_c05": ({"k_rock": 2550.0}, KNOCK, 0.0005),
    "knock_c10": ({"k_rock": 2800.0}, KNOCK, 0.0010),
    "knock_c15": ({"k_rock": 3100.0}, KNOCK, 0.0015),
    "knock_c20": ({"k_rock": 3350.0}, KNOCK, 0.0020),
    "nom_c15": ({"k_rock": 3100.0}, {}, 0.0015),
    "nom_c20": ({"k_rock": 3350.0}, {}, 0.0020),
    "nom_c10": ({"k_rock": 2800.0}, {}, 0.0010),
    "nom_c05": ({"k_rock": 2550.0}, {}, 0.0005),
    "knock_k3000": ({"k_rock": 3000.0}, KNOCK, None),
    # grip cases: mount collar longer by dg, station collar and brace ear move dg toward the wing (as D-91 did),
    # collar ring extension mass added to the mount (cl_mount.collar_ext)
    "knock_c10_g24": ({"k_rock": 3400.0, "grip": 0.024}, KNOCK, 0.0010),
    "nom_c10_g24": ({"k_rock": 3400.0, "grip": 0.024}, {}, 0.0010),
    "knock_k10000": ({"k_rock": 10000.0}, KNOCK, None),
    "knock_k1e5": ({"k_rock": 1e5}, KNOCK, None),
    # RW 35045-S, 0.875 x 0.625 in, page EX 72.3 / GXY 25.0 GPa, 0.289 kg/m; knock-down = 87 % E, half G (same rule)
    "rw45_knock_c15": ({"k_rock": 3100.0, "idd": 0.015875, "mu": 0.289}, {"E": 62.9e9, "G": 12.5e9}, 0.0015),
    "rw45_nom_c15": ({"k_rock": 3100.0, "idd": 0.015875, "mu": 0.289}, {"E": 72.3e9, "G": 25.0e9}, 0.0015),
    # RW 45405 roll-wrapped fabric 0.875 x 0.625 in, page EX 89.7 / GXY 13.56 GPa, 0.289 kg/m; knock 87 % E, half G
    "rw405_knock_c15": ({"k_rock": 3100.0, "idd": 0.015875, "mu": 0.289}, {"E": 78.0e9, "G": 6.78e9}, 0.0015),
    "rw405_nom_c15": ({"k_rock": 3100.0, "idd": 0.015875, "mu": 0.289}, {"E": 89.7e9, "G": 13.56e9}, 0.0015),
    # D-164 design: 10 deg / face_ahead 14 mm (x_prop = x_face - 0.0373 cos 10, CL-D3-X-PROP rule)
    "d164_nom": ({"d164": True, "k_rock": 2050.0}, {}, None),
    "d164_knock": ({"d164": True, "k_rock": 2050.0}, KNOCK, None),
    "d164_nom_c15": ({"d164": True, "k_rock": KR15}, {}, 0.0015),
    "d164_knock_c15": ({"d164": True, "k_rock": KR15}, KNOCK, 0.0015),
    "d164_rw45_knock_c15": ({"d164": True, "k_rock": KR15, "idd": 0.015875, "mu": 0.289}, {"E": 62.9e9, "G": 12.5e9}, 0.0015),
    "d164_rw45_nom_c15": ({"d164": True, "k_rock": KR15, "idd": 0.015875, "mu": 0.289}, {"E": 72.3e9, "G": 25.0e9}, 0.0015),
    "d164_knock_c30": ({"d164": True, "k_rock": 3600.0}, KNOCK, 0.0030),
    "d164_rw45_knock_c30": ({"d164": True, "k_rock": 3600.0, "idd": 0.015875, "mu": 0.289}, {"E": 62.9e9, "G": 12.5e9}, 0.0030),
    "d164_rw45_nom_c30": ({"d164": True, "k_rock": 3600.0, "idd": 0.015875, "mu": 0.289}, {"E": 72.3e9, "G": 25.0e9}, 0.0030),
    "d164_rw405_knock_c15": ({"d164": True, "k_rock": KR15, "idd": 0.015875, "mu": 0.289}, {"E": 78.0e9, "G": 6.78e9}, 0.0015),
    "d173_nom": ({"d173": True, "k_rock": 2050.0}, {}, None),
    "d173_knock": ({"d173": True, "k_rock": 2050.0}, KNOCK, None),
    "d173_knock_c15": ({"d173": True, "k_rock": 2900.0}, KNOCK, 0.0015),
    "d173_knock_c30": ({"d173": True, "k_rock": 3600.0}, KNOCK, 0.0030),
    "d173_f75_knock": ({"d173": True, "x_face": 0.0243, "base_mount": R5_MOUNT, "k_rock": KR_F75}, KNOCK, None),
    "d173_cf_nom": ({"d173": True, "k_rock": KR_CF, **CF2220}, CF2220_NOM, None),
    "d173_cf_lo": ({"d173": True, "k_rock": KR_CF, **CF2220}, CF2220_LO, None),
    "d173_cf_lo_c30": ({"d173": True, "k_rock": KR_CF30, **CF2220}, CF2220_LO, 0.0030),
    "d173_cf_lo_f75_c30": ({"d173": True, "x_face": 0.0243, "base_mount": R5_MOUNT, "k_rock": KR_CF_F75_30, **CF2220},
                           CF2220_LO, 0.0030),
    # face_ahead 4.0 mm (x_face 0.0278; D3 to confirm E1's 25 mm blade gap with the 46.8 mm stack), R4-size mount
    "d173_f40_knock_c15": ({"d173": True, "x_face": 0.0278, "base_mount": R4_MOUNT, "k_rock": 2350.0}, KNOCK, 0.0015),
    "d173_f40_knock_c30": ({"d173": True, "x_face": 0.0278, "base_mount": R4_MOUNT, "k_rock": 2950.0}, KNOCK, 0.0030),
    "d173_f40_nom_c30": ({"d173": True, "x_face": 0.0278, "base_mount": R4_MOUNT, "k_rock": 2950.0}, {}, 0.0030),
    "d173_rw45_f40_knock_c30": ({"d173": True, "x_face": 0.0278, "base_mount": R4_MOUNT, "k_rock": 2950.0,
                                 "idd": 0.015875, "mu": 0.289}, {"E": 62.9e9, "G": 12.5e9}, 0.0030),
    "d173_rw45_f40_nom_c30": ({"d173": True, "x_face": 0.0278, "base_mount": R4_MOUNT, "k_rock": 2950.0,
                               "idd": 0.015875, "mu": 0.289}, {"E": 72.3e9, "G": 25.0e9}, 0.0030),
    "d173_cf_f40_c30_nom": ({"d173": True, "x_face": 0.0278, "base_mount": R4_MOUNT, "k_rock": 2950.0, **CF2220},
                            CF2220_NOM, 0.0030),
    "d173_cf_f40_c30_lo": ({"d173": True, "x_face": 0.0278, "base_mount": R4_MOUNT, "k_rock": 2950.0, **CF2220},
                           CF2220_LO, 0.0030),
    "knock_c10_g22": ({"k_rock": 3250.0, "grip": 0.022}, KNOCK, 0.0010),
}

if __name__ == "__main__":
    import sim_fin as S
    case, side, lvls = sys.argv[1], sys.argv[2], [int(c) for c in sys.argv[3]]
    gch, kch, dt = CASES[case]
    t0 = time.time()
    kw = {a: S.kit.value(r) for a, r in S.kit.nodes["CALC-C4-SIM-MODES"]["inputs"].items()}
    g, k = S._modal_gk(kw)
    grip0 = g["grip"]
    gch = dict(gch)
    if gch.pop("d164", False):
        import cl_mount
        cl_mount.OVR.update(cl_mount.D164)
        cl_mount.BASE_MOUNT = cl_mount.D164_MOUNT
        g.update({"cant": 10.0, "x_face": 0.0178, "x_prop": 0.0178 - 0.0373 * 0.984807753, "mount": cl_mount.D164_MOUNT})
    if gch.pop("d173", False):
        import math as _m
        import cl_mount
        xf = gch.pop("x_face", 0.0178)
        cl_mount.OVR.update({"x_face": xf, "cl": 0.0235 + (0.0178 - xf), "cant": 10.0})
        if "od" in gch:
            cl_mount.OVR["od"] = gch["od"]
        base = gch.pop("base_mount", cl_mount.D164_MOUNT)
        cl_mount.BASE_MOUNT = base
        g.update({"cant": 10.0, "x_face": xf, "x_prop": xf - D173_STACK * _m.cos(_m.radians(10.0)), "mount": base,
                  "i_bell": D173_IBELL})
        kw["a3"] = [D173_MOTOR] + list(kw["a3"][1:])
    g = dict(g, **gch)
    if dt is not None:
        g["mount"] = mount_for(dt)
    if "grip" in gch:
        import cl_mount
        dg = g["grip"] - grip0
        ex, ey, ez = g["ear_xyz"]
        g["ear_xyz"] = [ex, ey, ez - dg]
        g["mount"] = cl_mount.add_collar_ext(g["mount"], dg)
    k = dict(k, **kch)
    rpm = (kw["rpm_h"], kw["rpm_c"], kw["rpm_x"])
    res = {"case": case, "side": side, "g_changes": gch, "k_changes": kch, "mount": g["mount"], "rpm": rpm, "levels": {}}
    f1 = []
    for lv in lvls:
        r = S.modes_level(g, k, side, lv, kw["a3"])
        st = [(f, kind) for f, ke, kind in r["modes"] if ke >= 0.10]
        f1.append(st[0][0])
        res["levels"][lv] = {"station": st[:4], "n_dof": r["n_dof"]}
        print("CL", case, side, lv, round(st[0][0], 2), st[0][1], r["n_dof"], round(time.time() - t0), flush=True)
    if len(f1) == 3:
        p, ext, gci = S.richardson(f1, 2 ** 0.5)
        st3 = [f for f, _ in res["levels"][3]["station"]]
        res.update({"ext": ext, "gci": gci, "order": p, "sep": S.sep_of([ext] + st3[1:3], rpm)})
    else:
        res["sep_l_only"] = S.sep_of([f for f, _ in res["levels"][lvls[-1]]["station"]][:3], rpm)
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / f"cl_{case}_{side}_{''.join(map(str, lvls))}.json").write_text(json.dumps(res, indent=1, default=float))
    print("CL DONE", json.dumps({k_: v for k_, v in res.items() if k_ != "levels"}, default=float), flush=True)
