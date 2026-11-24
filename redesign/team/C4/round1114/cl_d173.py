"""C4 closure round, D-173 (X2814 108 g, can +9.5 mm, 11x8E) built on cl_d164.py. Was: D-161 / D-164: shell model and mount loads (fin_structures_d3 calcs, in memory) at 10 deg / face_ahead
14.0 mm with the E/EP props, C1's current loads (CL-C1-T-LIMIT 22.03 N). Scratch only: out/cl_d164_<case>.json.

  python -I cl_d164.py <case>

Geometry overrides (D3 has not published 10 / 14 yet): CL-D3-X-FACE 0.0198 - 0.002 = 0.0178, CL-D3-X-PROP = x_face -
0.0373 cos 10 = -0.01893 (CL-D3-X-PROP rule), cheek_len_m 0.0215 + 0.002 = 0.0235, base mount cl_mount.D164_MOUNT (EST).
"""
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

RW46 = {"id": 0.01905, "mu": 0.156, "E": 90.2, "G": 20.5}
RW46K = dict(RW46, E=78.6, G=10.27)
RW45 = {"id": 0.015875, "mu": 0.289, "E": 72.3, "G": 25.0}
RW45K = dict(RW45, E=62.9, G=12.5)
CF = {"od": 0.022, "id": 0.020, "mu": 0.102, "E": 100.0, "G": 5.0}
CFLO = dict(CF, E=70.0, G=3.0)
R4 = [0.00988, -0.0046, 0.0005, -0.0097]
CASES173 = {  # name: (x_face, cheek dt, k_rock, tube, base mount)
    "f14_c0_nom": (0.0178, 0.0, 2050.0, RW46, None), "f14_c0_knock": (0.0178, 0.0, 2050.0, RW46K, None),
    "f40_c30_nom": (0.0278, 0.003, 2950.0, RW46, R4), "f40_c30_knock": (0.0278, 0.003, 2950.0, RW46K, R4),
    "f40_c15_knock": (0.0278, 0.0015, 2350.0, RW46K, R4),
    "rw45_f40_c30_nom": (0.0278, 0.003, 2950.0, RW45, R4), "rw45_f40_c30_knock": (0.0278, 0.003, 2950.0, RW45K, R4),
    "cf_f40_c30_nom": (0.0278, 0.003, 2950.0, CF, R4), "cf_f40_c30_lo": (0.0278, 0.003, 2950.0, CFLO, R4),
}
STACK = 0.0468          # prop stack 37.3 + 9.5 mm (X2814 can), EST until D3
CASES = {  # name: (cheek dt, k_rock model, tube)
    "base_nom": (0.0, 2050.0, RW46), "base_knock": (0.0, 2050.0, RW46K),
    "c15_nom": (0.0015, 2900.0, RW46), "c15_knock": (0.0015, 2900.0, RW46K),
    "rw45_c30_nom": (0.0030, 3600.0, RW45), "rw45_c30_knock": (0.0030, 3600.0, RW45K),
}

if __name__ == "__main__":
    case = sys.argv[1]
    x_face, dt, kr, tube, base = CASES173[case]
    t0 = time.time()
    import fin_structures_d3 as d3
    import cl_mount
    kit = d3.kit
    cl_mount.OVR.update({"x_face": x_face, "cl": 0.0235 + (0.0178 - x_face), "cant": 10.0, "od": tube.get("od", 0.0221)})
    cl_mount.BASE_MOUNT = base or cl_mount.D164_MOUNT
    mt = cl_mount.mount_tuple(dt)
    others = kit._other_claims()
    others["CL-D3-X-FACE"] = dict(others["CL-D3-X-FACE"], value=x_face)
    others["CL-D3-X-PROP"] = dict(others["CL-D3-X-PROP"], value=x_face - STACK * math.cos(math.radians(10.0)))

    def setp(key, v):
        kit._params[key] = dict(kit._params[key], value=v)
    setp("P:fin_detail.mount.cheek_len_m", 0.0235 + (0.0178 - x_face))
    setp("P:fin_detail.mount.prop_stack_m", STACK)
    if "od" in tube:
        setp("P:fins.tube.od_m", tube["od"])
    setp("P:fin_detail.mount.cheek_t_m", kit._params["P:fin_detail.mount.cheek_t_m"]["value"] + dt)
    setp("P:fin_detail.mount.cheek_in_t_m", kit._params["P:fin_detail.mount.cheek_in_t_m"]["value"] + dt)
    setp("P:fins.tube.id_m", tube["id"])
    setp("P:fins.tube.mass_per_m_kgm", tube["mu"])
    setp("P:fins.tube.e_gpa", tube["E"])
    setp("P:fins.tube.g_gpa", tube["G"])
    kit.nodes["ASM-C4-MOUNT-CAD"]["value"] = mt
    kit.nodes["ASM-C4-MOUNT-K-ROCK"]["value"] = kr
    for nid, n in kit.nodes.items():
        if n["type"] == "calculation":
            kit._run(nid)
    out = {}
    for nid, n in kit.nodes.items():
        if n["type"] != "claim" or "calc" not in n:
            continue
        v = kit.nodes[n["calc"]]["outputs"].get(n["output"])
        lim, ok = n.get("limit"), None
        if lim and isinstance(v, (int, float)):
            lv = lim.get("value", None)
            lv = kit.value(lim["ref"]) if lv is None else lv
            ok = v >= lv if lim["op"] == ">=" else v <= lv
            lim = [lim["op"], lv]
        out[nid] = {"value": v, "limit": lim, "pass": ok}
    (HERE / "out" / f"cl_d173_shell_{case}.json").write_text(json.dumps({"case": case, "mount": mt, "k_rock": kr, "tube": tube,
                                                                    "claims": out}, indent=1, default=float))
    fails = [k for k, v in out.items() if v["pass"] is False]
    keys = ("CL-C4-D3-SEP", "CL-C4-D3-SEP-WHIRL", "CL-C4-D3-MOUNT-K-REQ", "CL-C4-D3-MOUNT-K-EST", "CL-C4-D3-CANT-SIDE",
            "CL-C4-D3-MOUNT-AXIAL", "CL-C4-D3-MOUNT-TWIST", "CL-C4-D3-MOUNT-ROCK", "CL-C4-D3-MS-MOUNT-SLIP",
            "CL-C4-D3-MS-CAP-G3", "CL-C4-D3-MS-TUBE", "CL-C4-D3-MS-COLLAR", "CL-C4-D3-MS-COLLAR-16", "CL-C4-D3-MS-ANCHOR",
            "CL-C4-D3-MS-BRACE", "CL-C4-D3-MS-EDGE", "CL-C4-D3-MS-FACE", "CL-C4-D3-BLOCK-MS")
    print("D173", case, json.dumps({k: round(out[k]["value"], 4) for k in keys if k in out}), "FAILS", fails,
          round(time.time() - t0), "s", flush=True)
