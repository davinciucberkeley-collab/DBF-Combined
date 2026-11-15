"""C4 closure round, D-173 (X2814 KV900 + APC 11x8E/EP): separation against E1's operating-point ranges.
Scratch only. python -I d173_sets.py -> table; out/d173_sets.json.

Ranges (E1.md section "D-173 motor", relayed by the coordinator 2026-11-14): hover 5 256-5 693 rpm, cruise 17 m/s
4 899-5 007, full at the limiter 7 244-7 940, one motor at the 0.81 cap 9 663-9 964. Each point is a band [lo, hi] Hz; the
separation of a mode f from a band is |f / clamp(f, lo, hi) - 1| (0 inside the band).
Rule of record (CALC-C4-SIM-MODES): 1P / 2P hover, 1P / 2P cruise, 1P max (max = the cap, the highest rpm a motor sees).
Extended (information): 1P / 2P at the limiter, 2P at the cap.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RPM = {"hover": (5256, 5693), "cruise": (4899, 5007), "full": (7244, 7940), "cap": (9663, 9964)}
RULE = {"1P hover": (1, "hover"), "2P hover": (2, "hover"), "1P cruise": (1, "cruise"), "2P cruise": (2, "cruise"),
        "1P max": (1, "cap")}
EXT = dict(RULE, **{"1P full": (1, "full"), "2P full": (2, "full"), "2P cap": (2, "cap")})


def band(p, pt):
    lo, hi = RPM[pt]
    return p * lo / 60, p * hi / 60


def sep(fs, pts):
    best = (9.0, "")
    for f in fs:
        for name, (p, pt) in pts.items():
            lo, hi = band(p, pt)
            s = abs(f / min(max(f, lo), hi) - 1)
            best = min(best, (s, f"{name} vs {f:.1f}"))
    return best


if __name__ == "__main__":
    out = {"bands_hz": {k: band(*v) for k, v in EXT.items()}, "cases": {}}
    print({k: tuple(round(x, 1) for x in band(*v)) for k, v in EXT.items()})
    for f in sorted(p for p in (HERE / "out").glob("cl_d173_*.json") if "shell" not in p.name):
        r = json.loads(f.read_text())
        lv = sorted(r["levels"], key=int)
        if "ext" in r:
            fs = [r["ext"]] + [x[0] for x in r["levels"]["3"]["station"][1:3]]
        else:
            fs = [x[0] for x in r["levels"][lv[-1]]["station"][:3]]
        a, b = sep(fs, RULE), sep(fs, EXT)
        out["cases"][f.stem] = {"f": fs, "kind": r["levels"][lv[-1]]["station"][0][1], "rule": a, "ext": b}
        print(f"{f.stem:34s} f {[round(x, 1) for x in fs]} {out['cases'][f.stem]['kind']:16s} rule {a[0]:.3f} ({a[1]})  "
              f"ext {b[0]:.3f} ({b[1]})")
    (HERE / "out" / "d173_sets.json").write_text(json.dumps(out, indent=1))
