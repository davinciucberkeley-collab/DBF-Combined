"""C4 closure round 2026-11-14 (fix round): 3-D hex8 station modes on the live D3 geometry (face_ahead 3.0 mm, release
0.22-0.27 m, slip 2.55) at B4's hover rpm, three meshes, Richardson. Scratch only: out/cl_final_<case>_<side>.json.

  python -I cl_final.py <nom|knock> <upper|lower>
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
    case, side = sys.argv[1], sys.argv[2]
    import sim_fin as S
    t0 = time.time()
    kw = {a: S.kit.value(r) for a, r in S.kit.nodes["CALC-C4-SIM-MODES"]["inputs"].items()}
    g, k = S._modal_gk(kw)
    if case == "knock":
        k = dict(k, **KNOCK)
    f1, st3 = [], None
    for lv in (1, 2, 3):
        r = S.modes_level(g, k, side, lv, kw["a3"])
        st = [f for f, ke, kind in r["modes"] if ke >= 0.10]
        f1.append(st[0])
        if lv == 3:
            st3 = st
            kinds = [kind for f, ke, kind in r["modes"] if ke >= 0.10][:3]
        print(case, side, lv, round(st[0], 2), round(time.time() - t0), flush=True)
    p, ext, gci = S.richardson(f1, 2 ** 0.5)
    rpm = (kw["rpm_h"], kw["rpm_c"], kw["rpm_x"])
    sep = S.sep_of([ext] + st3[1:3], rpm)
    res = {"case": case, "side": side, "f1": f1, "ext": ext, "gci": gci, "sep": sep, "rpm": rpm, "kinds": kinds,
           "k_rock": g.get("k_rock"), "x_face": g["x_face"], "release": [S.d3.RELEASE_X, S.d3.RELEASE_END]}
    (HERE / "out" / f"cl_final_{case}_{side}.json").write_text(json.dumps(res, indent=1, default=float))
    print("DONE", json.dumps(res, default=float), flush=True)
