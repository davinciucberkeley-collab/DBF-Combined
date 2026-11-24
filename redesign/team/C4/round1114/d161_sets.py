"""C4 closure round, D-161: separation of the three-mesh cases against the full E/EP operating-point set.
Scratch only. python -I d161_sets.py  -> prints a table, writes out/d161_sets.json.

Forcing (team/B4/claims.json, read 2026-11-14 after D-161): hover CL-B4-HOVER-RPM, cruise 17 m/s CL-B4-CRUISE-RPM,
full CL-B4-RPM-MAX (hot winding, 14.8 V; the rule of record) and CL-B4-RPM-MAX-FULL (fresh pack, F4 caps; envelope max,
BPF CL-B4-BPF-MAX). Rule of record (CALC-C4-SIM-MODES): 1P/2P hover, 1P/2P cruise, 1P max. Extended (information):
adds 2P max and 1P/2P at the envelope max.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
B4 = {n["id"]: n.get("value") for n in json.loads((HERE.parents[1] / "B4" / "claims.json").read_text())["nodes"]}
H, C, X, XF = (B4[k] for k in ("CL-B4-HOVER-RPM", "CL-B4-CRUISE-RPM", "CL-B4-RPM-MAX", "CL-B4-RPM-MAX-FULL"))
RULE = {"1P hover": H / 60, "2P hover": H / 30, "1P cruise": C / 60, "2P cruise": C / 30, "1P max": X / 60}
EXT = dict(RULE, **{"2P max": X / 30, "1P env max": XF / 60, "2P env max": XF / 30})


def sep(fs, pts):
    best = min(((abs(f / v - 1), k, f) for f in fs for k, v in pts.items()))
    return best


if __name__ == "__main__":
    out = {"forcing_hz": EXT, "cases": {}}
    print({k: round(v, 1) for k, v in EXT.items()})
    for f in sorted((HERE / "out").glob("cl_*_123.json")):
        r = json.loads(f.read_text())
        if "ext" not in r or abs(r["rpm"][1] - C) > 1:
            continue
        fs = [r["ext"]] + [x[0] for x in r["levels"]["3"]["station"][1:3]]
        a, b = sep(fs, RULE), sep(fs, EXT)
        out["cases"][f.stem] = {"f_station": fs, "sep_rule": a[0], "nearest_rule": a[1], "sep_ext": b[0],
                                "nearest_ext": b[1]}
        print(f"{f.stem:32s} f {[round(x, 1) for x in fs]}  rule {a[0]:.3f} ({a[1]})  extended {b[0]:.3f} ({b[1]})")
    (HERE / "out" / "d161_sets.json").write_text(json.dumps(out, indent=1))
