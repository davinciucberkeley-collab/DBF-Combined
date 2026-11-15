"""C4 design round 2026-11-14, wave 2: information rows on the R6 geometry (params as applied by A1, D3 R6 mount).
Scratch only: does not write any claims file.

  python -I w2_knock.py modes <side>   3-D hex8 station modes, three meshes, tube knocked down to E 78.6 / G 10.3 GPa
  python -I w2_knock.py d3             shell model (fin_structures_d3 calcs) at the knock-down, -> out/d3_w2_knock.json

Knock-down: E 78.6 GPa = the R5 GT-16 shell pass line (CL-C4-D3-TUBE-E-REQ, R5), G 10.27 GPa = half the page GXY
(C4.md wave 1, section 1.3). Results go to the shared sim cache (sim/out/cache) like every sim_fin.py run.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "sim"))

KNOCK = {"E": 78.6e9, "G": 10.27e9}

if __name__ == "__main__":
    what = sys.argv[1]
    t0 = time.time()
    if what == "modes":
        import sim_fin as S
        side = sys.argv[2]
        kw = {a: S.kit.value(r) for a, r in S.kit.nodes["CALC-C4-SIM-MODES"]["inputs"].items()}
        g, k = S._modal_gk(kw)
        k = dict(k, **KNOCK)
        f1 = []
        for lv in (1, 2, 3):
            r = S.modes_level(g, k, side, lv, kw["a3"])
            st = [f for f, ke, kind in r["modes"] if ke >= 0.10]
            f1.append(st[0])
            print("KNOCK", side, lv, round(st[0], 2), r["n_dof"], round(time.time() - t0), flush=True)
        p, ext, gci = S.richardson(f1, 2 ** 0.5)
        r3 = S.modes_level(g, k, side, 3, kw["a3"])
        st3 = [f for f, ke, kind in r3["modes"] if ke >= 0.10]
        rpm = (kw["rpm_h"], kw["rpm_c"], kw["rpm_x"])
        sep = S.sep_of([ext] + st3[1:3], rpm)
        res = {"side": side, "knock": KNOCK, "f1": f1, "ext": ext, "gci": gci, "order": p, "sep": sep,
               "kinds": [kind for f, ke, kind in r3["modes"] if ke >= 0.10][:3], "rpm": rpm}
        (HERE / "out").mkdir(exist_ok=True)
        (HERE / "out" / f"w2_knock_{side}.json").write_text(json.dumps(res, indent=1, default=float))
        print("KNOCK DONE", json.dumps(res, default=float), flush=True)
    elif what == "d3":
        import fin_structures_d3 as d3
        kit = d3.kit
        # Override the converted tube moduli (the GPa keys feed CALC-C4-TUBE-EG)
        kit._params["P:fins.tube.e_gpa"] = {"value": KNOCK["E"] / 1e9}
        kit._params["P:fins.tube.g_gpa"] = {"value": KNOCK["G"] / 1e9}
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
        (HERE / "out" / "d3_w2_knock.json").write_text(json.dumps({"knock": KNOCK, "claims": out}, indent=1,
                                                                  default=float))
        print("D3 KNOCK DONE", round(time.time() - t0), "s", flush=True)
