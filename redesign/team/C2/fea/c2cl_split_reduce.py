"""C2 closure round 2026-11-14: reduce the fin-root fillet-split runs ("c4split") to a small committed file.

The drawn design bonds the half-fin root and its cove fillets to the wing along the whole chord, so the fillet is a
real load path. How much it carries is set by compatibility. C4 computed it (CR-C2-12 answer: team/C4/claims.d3.json,
CALC-C4-D3-STATIC output fillet_share_table): the -reactions of the fin root, pinned (rigid), split at the hinge, per
quarter, L4 and G2, both senses. A rigid root attracts the most load, so for a foam wing these are upper bounds.
wing_fea.INTRO "c4split" puts each segment's resultant on the station-strip skin of its own surface and side of the
hinge and the rest of the station load on the block. C4's frame vs C2's (load sense, y sign) is not pinned down, so
all four combinations are run and the worst is taken; k scales C4's resultants.

Inputs (outside the repo; regenerate with RUNS):
  <dir>/L2_<t>.json                      global, level 2, per combination t in p_0 m_0 p_1 m_1 (p/m = C4 sense +/-,
                                          0/1 = C4 y kept / mirrored)
  <dir>/d68_local_<t>_d68_L<l>.json       local submodel (cut-out corners), level l
Output: team/C2/fea/data/c2cl_split.json (small), read by fea_report.py.

Run: python -I redesign/team/C2/fea/c2cl_split_reduce.py <dir>
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = {
    "global": "C2_C4SPLIT=<sense>,<ymir>,<k> OMP_NUM_THREADS=4 python -I redesign/team/C2/fea/wing_fea_direct.py "
              "--intro c4split --levels 2 --sets O --cases L4-CORNER-SIDE-Y G2-HANG-MOTOR --no-validation "
              "--out <dir>/L2_<t>.json",
    "d68_global": "C2_C4SPLIT=... C2_D68_OUT=<dir> C2_D68_INTROS=c4split C2_D68_TAG=<t> python -I "
                  "redesign/team/C2/fea/wing_fea_d68.py --phase global --intro c4split",
    "d68_local": "same environment; wing_fea_d68.py --phase local --job d68/<l>",
    "c2r5": "C2_X_BREAK=0.22 python -I redesign/team/C2/fea/c2r5_corner.py local --variant band --level 2 --band-x 0.24 "
            "--band-dy 0.2 --dbl-mult 3 --Et 0.044e6 --cases L4 G2 --intro c4split --global-pkl "
            "<dir>/d68_global_c4split_bm_1.pkl --tag split_bm_1_L2 --out-dir <dir>/c2r5; c2r5_measure.py --dir <dir>/c2r5",
    "env": "all split runs: C2_X_BREAK=0.22 (bond break), C2_C4SPLIT=<sense>,<ymir>,1,1 (k 1, aft share moved ahead)",
}


def main(d):
    d = Path(d)
    out = {"_note": "closure round 2026-11-14, written by c2cl_split_reduce.py; stresses at LIMIT (x 1.5 for ultimate)",
           "runs": RUNS, "global": {}, "cutout": {}}
    for f in sorted(d.glob("L*_*.json")):
        m = re.match(r"L(\d)_(.+)\.json", f.name)
        if not m:
            continue
        t = m.group(2)
        r = json.loads(f.read_text())
        for lev, dd in r["levels"].items():
            for k, v in dd["runs"].items():
                fo = v["post"]["foam"]
                out["global"].setdefault(t, {}).setdefault(lev, {})[k] = {
                    kk: fo[kk] for kk in ("s1_p995v_pa", "tau_p995v_pa", "s1_max_pa", "s1_at", "tau_max_pa", "tau_at")}
    for f in sorted(d.glob("d68_local_*_d68_L*.json")):
        m = re.match(r"d68_local_(.+)_d68_L(\d)\.json", f.name)
        t, lev = m.group(1), m.group(2)
        r = json.loads(f.read_text())
        for k, v in r["runs"].items():
            pk = v["peaks"].get("cutout/foam", {})
            out["cutout"].setdefault(t, {}).setdefault(lev, {})[k] = {
                kk: pk.get(kk) for kk in ("s1_avg_pa", "s3_avg_pa", "tau_avg_pa", "s1_pa", "s3_pa", "tau_pa", "s1_at")}
            out["cutout"][t][lev][k]["equilibrium_residual_N"] = v["equilibrium_residual_N"]
        out["cutout"][t][lev]["_h_local_mm"] = r["stats"]["h_local_mm"]
    # block-pocket corners on the decided tape model (c2r5_corner.py band, 50 % credit, level 2) with the split:
    # vm(L/2) of c2r5_measure.py (key vm_1.78 = L/2 1.782 mm, CL-C2-FEA-TCD-HALF-L)
    mp = d / "c2r5" / "measures.json"
    if mp.exists():
        ms = json.loads(mp.read_text())
        out["corner"] = {k: {f: v["foam"][f]["vm_1.78"] for f in ("s1", "s3", "tau")}
                         for k, v in ms.items() if not k.startswith("_") and "@" not in k}
    p = HERE / "data" / "c2cl_split.json"
    p.write_text(json.dumps(out, indent=1, sort_keys=True))
    print("wrote", p, {t: sorted(v) for t, v in out["cutout"].items()}, {t: sorted(v) for t, v in out["global"].items()})


if __name__ == "__main__":
    main(sys.argv[1])
