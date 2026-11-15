"""C4 closure round: shell model (fin_structures_d3 calcs, in memory) for the cheek options, nominal and knock-down tube.
Scratch only: writes round1114/out/cl_d3_<case>.json, never a claims file.

  python -I cl_d3.py <case>     cases: base_knock, c10_nom, c10_knock, c05_knock

cXX: both mount cheeks +XX/10 mm outward (fin_detail.mount.cheek_t_m / cheek_in_t_m), ASM-C4-MOUNT-K-ROCK = the
CALC-C4-D3-MOUNT-K-EST value at ASA E 1.8 GPa rounded down (cl_mount.py), ASM-C4-MOUNT-CAD from cl_mount.mount_tuple.
knock: tube E 78.6 / G 10.27 GPa (C4-W2 section 4).
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

KNOCK = (78.6, 10.27)
CASES = {"base_knock": (0.0, None, KNOCK), "c10_nom": (0.0010, 2800.0, None), "c10_knock": (0.0010, 2800.0, KNOCK),
         "c05_knock": (0.0005, 2550.0, KNOCK), "c05_nom": (0.0005, 2550.0, None),
         "c15_nom": (0.0015, 3100.0, None), "c15_knock": (0.0015, 3100.0, KNOCK), "base_nom": (0.0, None, None)}

if __name__ == "__main__":
    case = sys.argv[1]
    dt, kr, eg = CASES[case]
    t0 = time.time()
    import fin_structures_d3 as d3
    import cl_mount
    kit = d3.kit
    mt = cl_mount.mount_tuple(dt)
    if dt:
        for key in ("P:fin_detail.mount.cheek_t_m", "P:fin_detail.mount.cheek_in_t_m"):
            kit._params[key] = dict(kit._params[key], value=kit._params[key]["value"] + dt)
        kit.nodes["ASM-C4-MOUNT-CAD"]["value"] = mt
    if kr:
        kit.nodes["ASM-C4-MOUNT-K-ROCK"]["value"] = kr
    if eg:
        kit._params["P:fins.tube.e_gpa"] = dict(kit._params["P:fins.tube.e_gpa"], value=eg[0])
        kit._params["P:fins.tube.g_gpa"] = dict(kit._params["P:fins.tube.g_gpa"], value=eg[1])
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
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / f"cl_d3_{case}.json").write_text(json.dumps({"case": case, "mount": mt, "k_rock": kr, "eg": eg,
                                                                 "claims": out}, indent=1, default=float))
    fails = [k for k, v in out.items() if v["pass"] is False]
    keys = ("CL-C4-D3-SEP", "CL-C4-D3-SEP-WHIRL", "CL-C4-D3-MOUNT-K-REQ", "CL-C4-D3-MOUNT-K-EST", "CL-C4-D3-MS-MOUNT-SLIP",
            "CL-C4-D3-FINS-MASS", "CL-C4-D3-MS-COLLAR", "CL-C4-D3-MS-TUBE")
    print("D3", case, {k: round(out[k]["value"], 4) for k in keys if k in out}, "FAILS", fails, round(time.time() - t0), "s",
          flush=True)
