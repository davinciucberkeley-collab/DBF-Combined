"""C4 design round 2026-11-14 (R-VIBRATION, CL-C4-SIM-SEP): option cases for the station-mode fix.

Scratch analysis only: shared params are never edited. Each case overrides the tube / station inputs in memory and
runs the same hex8 modal model as sim_fin.py (CALC-C4-SIM-MODES), results go to the shared sim cache.

  python -I opts.py modes <case> <side>          three meshes L1-L3 of one quarter
  python -I opts.py lever <case> <side> <level>  one mesh level only
  python -I opts.py face <case> <level> <variant> L4 face-stress quarter (upper), as CALC-C4-SIM-FACE
"""
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "sim"))
import sim_fin as S  # noqa: E402

IN = 0.0254
# Case overrides. Tube properties: Rock West 35046-S product page (read 2026-11-14): OD 0.875 in, ID 0.750 in,
# EX 1.308e7 psi, GXY 2.979e6 psi, linear density 0.105 lb/ft. ECF 22 x 19 page (2026-11-14): 0.14 kg/m, EI 0.54 kN m2.
PSI = 6894.757
CASES = {
    "base": {},
    "rw35046": {"g": {"od": 0.875 * IN, "idd": 0.750 * IN, "mu": 0.105 * 0.45359237 / 0.3048},
                "k": {"E": 1.308e7 * PSI, "G": 2.979e6 * PSI}},
    # robustness: CLT values are not guaranteed; E at the GT-16 shell pass line, G halved
    "rw35046_lo": {"g": {"od": 0.875 * IN, "idd": 0.750 * IN, "mu": 0.105 * 0.45359237 / 0.3048},
                   "k": {"E": 78.6e9, "G": 10.27e9}},
    "w19": {"g": {"idd": 0.019, "mu": 0.140}},                        # 22 x 19 roll-wrapped, nominal 100 / 5 GPa
    "w18": {"g": {"idd": 0.018, "mu": math.pi / 4 * (0.022 ** 2 - 0.018 ** 2) * 1550}},  # EST rho 1.55
    "arm1": {"g_add": {"x_face": 0.001, "x_prop": 0.001}},            # face_ahead 7.5 -> 6.5 mm (E1 least)
    "krock3": {"g_scale": {"k_rock": 3.0}},                           # mount rocking stiffness x 3 (ceiling check)
    # 11x5.5E prop (B4 SRC-B4-APC-PRODUCTS: LP11055EP 23 g vs 11x4.5MR/5.5MR 17 g), inertia scaled by mass
    "base_ep": {"g": {"m_prop": 0.023}, "g_scale": {"ip": 23 / 17}},
    "rw35046_ep": {"g": {"od": 0.875 * IN, "idd": 0.750 * IN, "mu": 0.105 * 0.45359237 / 0.3048,
                         "m_prop": 0.023}, "g_scale": {"ip": 23 / 17},
                   "k": {"E": 1.308e7 * PSI, "G": 2.979e6 * PSI}},
}
# Brace removed (mass offset check): brace strip stiffness ~0 and its mass taken off the collar point mass
CASES["rw35046_nobrace"] = {"g": dict(CASES["rw35046"]["g"], b_t=1e-7), "k": CASES["rw35046"]["k"],
                            "cb_brace0": True}
# Cant 10 deg (B3 upper end): rpm x sqrt(cos 7 / cos 10) EST (thrust along the shaft rises 1/cos c for the same
# axial component); 11x5.5E rpm from team/B4/out/props_results.json (hover 5829.6, cruise 6075.3, max 9735.3).
_C10 = (math.cos(math.radians(7)) / math.cos(math.radians(10))) ** 0.5
RPM_SETS = {
    "MR 7deg": (5415.79, 5994.05, 9319.45),
    "MR 8.5deg": tuple(x * f for x, f in zip((5415.79, 5994.05, 9319.45),
                                            ((math.cos(math.radians(7)) / math.cos(math.radians(8.5))) ** 0.5,) * 2 + (1,))),
    "MR 10deg": (5415.79 * _C10, 5994.05 * _C10, 9319.45),
    "EP 7deg": (5829.57, 6075.31, 9735.26),
    "EP 10deg": (5829.57 * _C10, 6075.31 * _C10, 9735.26),
}
CASES["rw35046_c10"] = dict(CASES["rw35046"], params={"P:propulsion.stations.cant_deg": 10.0,
                                                      "CL-B4-HOVER-RPM": RPM_SETS["MR 10deg"][0],
                                                      "CL-B4-CRUISE-RPM": RPM_SETS["MR 10deg"][1]})
CASES["rw35046_ep_c10"] = dict(CASES["rw35046_ep"], params={"P:propulsion.stations.cant_deg": 10.0,
                                                            "P:propulsion.prop_mass_kg": 0.023,
                                                            "CL-B4-HOVER-RPM": RPM_SETS["EP 10deg"][0],
                                                            "CL-B4-CRUISE-RPM": RPM_SETS["EP 10deg"][1],
                                                            "CL-B4-RPM-MAX": RPM_SETS["EP 10deg"][2],
                                                            "ASM-C4-PROP-IP": 7.5e-5 * 23 / 17})


# A1 2026-11-14 (B3.md): cant 9 deg with face_ahead 7.5 -> 12.0 mm; contingency 10 deg with 14.0 mm.
# Hub and plate move forward by the face_ahead change; x_prop = x_face - prop_stack 0.0373 cos(cant)
# (fin_detail.mount note, CL-D3-X-PROP rule). Cheeks lengthen by the same amount. Mount mass and CG from the R4 -> R5
# CAD step (face_ahead +5 mm: 11.28 -> 11.94 g, CG x 0.0404 -> 0.0365, ASM-C4-MOUNT-CAD note): +0.13 g/mm and
# CG dx -0.78 mm/mm, EST. Mount rocking stiffness kept at the 2200 N m/rad model value: the _mount_k estimate rises
# to 2507 (9/12) and 2273 (10/14) N m/rad (longer cheeks add sway inertia), so 2200 stays conservative.
X_FACE0 = 0.02435


def _mount_case(d_face, cant):
    xf = X_FACE0 - d_face
    return {"g_set": {"x_face": xf, "x_prop": xf - 0.0373 * math.cos(math.radians(cant)), "cant": cant},
            "mount_add": (0.13e-3 * d_face * 1000, -0.78 * d_face)}


for _tag, _d, _c in (("f12", 0.0045, 9.0), ("f14", 0.0065, 10.0)):
    for _base in ("base", "rw35046", "w19", "w18", "rw35046_ep"):
        _cc = dict(CASES[_base])
        _cc.update(_mount_case(_d, _c))
        _f = ((math.cos(math.radians(7)) / math.cos(math.radians(_c))) ** 0.5)
        _mc = _mount_case(_d, _c)
        _cc["params"] = dict(_cc.get("params", {}), **{
            "P:propulsion.stations.cant_deg": _c, "CL-D3-X-FACE": _mc["g_set"]["x_face"],
            "CL-D3-X-PROP": _mc["g_set"]["x_prop"], "P:fin_detail.mount.cheek_len_m": 0.017 + _d,
            "ASM-C4-MOUNT-CAD": [0.01085 + _mc["mount_add"][0], -0.0084 + _mc["mount_add"][1], 0.0007, -0.0110],
            "CL-B4-HOVER-RPM": 5415.79 * _f, "CL-B4-CRUISE-RPM": 5994.05 * _f})
        CASES[f"{_base}_{_tag}"] = _cc
_C9 = (math.cos(math.radians(7)) / math.cos(math.radians(9))) ** 0.5
RPM_SETS["MR 9deg"] = (5415.79 * _C9, 5994.05 * _C9, 9319.45)
RPM_SETS["EP 9deg"] = (5829.57 * _C9, 6075.31 * _C9, 9735.26)


def modal_inputs(case):
    kit = S.kit
    kw = {a: kit.value(r) for a, r in kit.nodes["CALC-C4-SIM-MODES"]["inputs"].items()}
    g, k = S._modal_gk(kw)
    c = CASES[case]
    g = dict(g, **c.get("g", {}))
    for n, f in c.get("g_scale", {}).items():
        g[n] = g[n] * f
    for n, d in c.get("g_add", {}).items():
        g[n] = g[n] + d
    k = dict(k, **c.get("k", {}))
    for n, v in c.get("g_set", {}).items():
        g[n] = v
    if "mount_add" in c:
        dm, dx = c["mount_add"]
        mm = list(g["mount"])
        g["mount"] = [mm[0] + dm, mm[1] + dx, mm[2], mm[3]]
    if c.get("cb_brace0"):
        g["cb_mass"] = [g["cb_mass"][0], 0.0]
    return g, k, list(kw["a3"]), kw


def face_inputs(case):
    kit = S.kit
    kw = {a: kit.value(r) for a, r in kit.nodes["CALC-C4-SIM-FACE"]["inputs"].items()}
    g, k = S._split(kw)
    c = CASES[case]
    g = dict(g, **c.get("g", {}))
    k = dict(k, **c.get("k", {}))
    return g, k


if __name__ == "__main__":
    what, case = sys.argv[1], sys.argv[2]
    t0 = time.time()
    if what == "modes":
        side = sys.argv[3]
        g, k, a3, _ = modal_inputs(case)
        for lv in (1, 2, 3):
            r = S.modes_level(g, k, side, lv, a3)
            st = [f for f, ke, kind in r["modes"] if ke >= 0.10]
            print("MODES", case, side, lv, round(st[0], 2), r["n_dof"], round(time.time() - t0), flush=True)
    elif what == "lever":
        side, lv = sys.argv[3], int(sys.argv[4])
        g, k, a3, _ = modal_inputs(case)
        r = S.modes_level(g, k, side, lv, a3)
        st = [f for f, ke, kind in r["modes"] if ke >= 0.10]
        print("LEVER", case, side, lv, round(st[0], 2), round(time.time() - t0), flush=True)
    elif what == "face":
        lv, var = sys.argv[3], sys.argv[4]
        lv = lv if lv == "G" else int(lv)
        side = sys.argv[5] if len(sys.argv) > 5 else "upper"
        g, k = face_inputs(case)
        S.su2_quarter(g, k, side, lv, var)
        print("FACE", case, side, lv, var, round(time.time() - t0), flush=True)
