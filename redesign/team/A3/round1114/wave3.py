"""A3 design round 2026-11-14, wave 3: the D-155 package as drawn, both cases, allocation reset.

Case (a) is the live roll-up (team/A3/rollup/mass_items.json, written by mass_rollup.py on the wave-2 parts.csv
with the A3 overrides for D-146 / D-150 and the S08 adder). Case (b) adds S02 / S03 as measured-at-listing
deltas (same rows as package.py). The D-cell rows are C2's fallback. Every number uses mass_rollup()/cg_cases().

Run:  python -I redesign/team/A3/round1114/wave3.py   ->  round1114/out/wave3.json
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import package as pk3  # noqa: E402  (reuses run(), it(), SAVE; reads params.json)

A3 = HERE.parent
P = pk3.p
NOSE = 0.0413                                   # ASM-A3-NOSE-STACK (wave 3)
X_AFT_B3 = 0.05119                              # CL-B3-V-CG-AFT-ENV (B3-W2.md section 4)


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))["a3"]["rollup"]["items"]["value"]


def run_on(items, extra, nose=NOSE):
    pk3.ITEMS = items
    return pk3.run(extra, nose=nose, pod_le=P("pod.x_le_m"))


def alloc_set(r):
    a = {k: math.ceil(round(v[1], 1) - 1e-9) for k, v in r["alloc"].items()}
    return a, sum(a.values()), 2600 - sum(a.values())


def main(before_items=None):
    S = pk3.SAVE
    tests = [S["S02-PWR003-LISTING"], S["S03-PHASE-EXT"]]
    dcell = [[pk3.it("WNG-DCELL", "wing", "structure", 16.5 / 2, 0.058, y, 0.0, "EST") for y in (0.32, -0.32)]]
    live = load(A3 / "rollup" / "mass_items.json")
    out = {"a": run_on(live, []), "b": run_on(live, tests), "c_a": run_on(live, dcell), "c_b": run_on(live, dcell + tests)}
    for k in out:
        xb = P("pod.x_le_m") + 0.012
        out[k]["ballast_d121_g"] = {"basic": pk3.ballast_g(out[k], xb), "pred": pk3.ballast_g(out[k], xb, which="x_cg_pred_m")}
        out[k]["pack_accept_g"] = 550.0 + out[k]["gate_margin_g"] - P("requirements.build_overrun_kg") * 1000
        out[k]["b3_aft_env_margin_mm"] = (X_AFT_B3 - out[k]["cg_x_pred"]) * 1000
        out[k]["params_aft_margin_mm"] = (P("cg.x_range_m")[1] - out[k]["cg_x_pred"]) * 1000
        out[k]["alloc_reset"] = alloc_set(out[k])
    # CG-X-PRED walk from the pre-wave-3 roll-up (stored items) to the live one, one change at a time
    if before_items:
        old = load(before_items)
        walk, cur = [], [list(r) for r in old]
        ref = run_on(cur, [], nose=0.0346)
        steps = [("fins R6 (D3: tubes, mounts, blocks)", lambda r: r[1] == "fins" and not r[0].startswith("FIN-A3")),
                 ("pod D-150 (D2 positions and masses)", lambda r: r[1] == "pod"),
                 ("C6 prop fasteners PRP-005..008 (already moved)", lambda r: r[0] in ("PRP-005", "PRP-006", "PRP-007", "PRP-008")),
                 ("motor, prop, adapter at 9 deg / 12 mm (A3 overrides)", lambda r: r[0] in ("PRP-001", "PRP-003", "PRP-004")),
                 ("pitot AVN-005 -7 mm (A3 override)", lambda r: r[0] == "AVN-005"),
                 ("S08 microlight adder", lambda r: r[0] == "FIN-A3-S08")]
        for name, sel in steps:
            cur = [r for r in cur if not sel(r)] + [list(r) for r in live if sel(r)]
            new = run_on(cur, [], nose=NOSE)
            walk.append({"step": name, "d_pred_g": new["pred_g"] - ref["pred_g"],
                         "d_cg_pred_mm": (new["cg_x_pred"] - ref["cg_x_pred"]) * 1000,
                         "cg_x_pred": new["cg_x_pred"]})
            ref = new
        out["walk"] = walk
        out["walk_start"] = run_on(old, [], nose=0.0346)["cg_x_pred"]
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "wave3.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k in ("a", "b", "c_a", "c_b"):
        r = out[k]
        print(f"{k:4s} basic {r['basic_g']:7.1f} pred {r['pred_g']:7.1f} margin {r['gate_margin_g']:5.1f} "
              f"free {r['free_above_overrun_g']:+5.1f} accept {r['pack_accept_g']:5.1f} | st {r['stations_use']:.3f} "
              f"pred_use {r['pred_range_use']:.3f} cgx {r['cg_x_basic']:.5f}/{r['cg_x_pred']:.5f} "
              f"B3aft {r['b3_aft_env_margin_mm']:+.2f} mm split {r['hover_split']:.3f} fwdlim {r['x_fwd_lim']:.4f} "
              f"worst {r['worst_alloc'][0]} {r['worst_alloc'][1]:.4f} bal {r['ballast_d121_g']['basic']:.0f}/"
              f"{r['ballast_d121_g']['pred']:.0f}")
        print("     alloc", {s: v[1] for s, v in r["alloc"].items()}, "reset", r["alloc_reset"])
        print("     stations", {s: (round(v["pack_x_m"], 4), round(v["x_cg_m"], 5), round(v["x_cg_pred_m"], 5),
                                    round(v["aft_margin_m"] * 1000, 2), round(v["fwd_margin_m"] * 1000, 2), v["clamped"])
                                for s, v in r["stations"].items()})
    for w in out.get("walk", []):
        print(f"  {w['step']:55s} {w['d_pred_g']:+6.1f} g  {w['d_cg_pred_mm']:+.3f} mm  -> {w['cg_x_pred']:.5f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
