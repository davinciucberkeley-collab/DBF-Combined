"""C2 wave 2 (D-153, design round 2026-11-14): reduce the block-pocket corner FE measures to the few numbers the
claims need, so fea_claims.py and the proof graph re-run from small committed files only.

Inputs (committed, small):
  out/c2r5/measures.json       wave-1 measures (c2r5_measure.py over the out/c2r5/*.npz field dumps, git-ignored)
  data/c2w2_measures.json      wave-2 measures (same script over the wave-2 dumps, which were written outside the repo)
  data/c2w2_runs.json          wave-2 run records (arguments, mesh size, wall time) from c2r5_corner.py
Output:
  c2r5_reduced.json            params file, namespace c2r5 (P:c2r5.*), read by fea_claims.py

Measure: vm(L/2), the foam-only volume average over a ball of radius L/2, maximised over the ball centre (Taylor's
theory of critical distances, volume form; c2r5_measure.py). Values are at LIMIT load in Pa; the claims multiply by
the ultimate factor. s3 is stored as a positive compression magnitude.

Cases (all block load introduction, L4-CORNER-SIDE-Y / MC-C, local cuts 0.27 / 0.37 m):
  base       D-68 as modelled before D-153, no skin                         levels 1-3   (information rows)
  tape50     WNG-003 tape skin x <= 0.24 at 50 % credit (E t 0.044 MN/m) + 2-layer block doubler (3 x E t over
             y 0.29-0.35, x <= 0.12) = the decided model                    levels 1-2
  tape25     the same at 25 % credit (E t 0.022 MN/m)                       levels 1-2   (sensitivity)
  tape50g    tape50 with the ESC-lead grooves and open slot seams (d68g)    level 2      (-CUTS)
  tape50g431 tape50 with the tube at G 4.31 GPa (GT-16 line)                level 2      (-G431)
  *_servo    zone = within 15 mm of the lower-skin servo-pocket opening (opening modelled, no skin over it)

Run: python -I redesign/team/C2/fea/c2r5_reduce.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
W1 = HERE / "out" / "c2r5" / "measures.json"
W2 = HERE / "data" / "c2w2_measures.json"
RUNS = HERE / "data" / "c2w2_runs.json"
OUTF = HERE / "c2r5_reduced.json"
SRC = "team/C2/fea/c2r5_reduce.py"
CASE = "L4-CORNER-SIDE-Y"

# reduced case id -> (file, measures key)
CASES = {
    "base_L1": (W1, f"base_L1_narrow_{CASE}"),
    "base_L2": (W1, f"base_L2_narrow_{CASE}"),
    "base_L3": (W1, f"base_L3_narrow_{CASE}"),
    "tape50_L1": (W1, f"tapeA_L1_{CASE}"),
    "tape50_L2": (W2, f"tapeA_L2s_{CASE}"),        # wave-2 re-run on the current params (D-147 tube bore)
    "tape25_L1": (W1, f"tapeAlo_L1_{CASE}"),
    "tape25_L2": (W2, f"tapeAlo_L2_{CASE}"),
    "tape50g_L2": (W2, f"tapeAg_L2_{CASE}"),
    "tape50g431_L2": (W2, f"tapeA431_L2_{CASE}"),
    "tape50_L2_servo": (W2, f"tapeA_L2s_{CASE}@servo"),
    "tape25_L2_servo": (W2, f"tapeAlo_L2_{CASE}@servo"),
    "tape50g_L2_servo": (W2, f"tapeAg_L2_{CASE}@servo"),
    "tape50g431_L2_servo": (W2, f"tapeA431_L2_{CASE}@servo"),
    "base_L2_servo": (W2, f"base_L2s_{CASE}@servo"),
}
CHECK = (W1, f"tapeA_L2_{CASE}")        # wave-1 run of the decided model, before the D-147 params edit


def pv(v, unit, note):
    return {"value": v, "unit": unit, "source": SRC, "status": "UNVERIFIED", "note": note}


def main():
    m = {W1: json.loads(W1.read_text()), W2: json.loads(W2.read_text())}
    meta = m[W1]["_meta"]
    out = {"_note": "Written by team/C2/fea/c2r5_reduce.py from out/c2r5/measures.json and data/c2w2_*.json. "
                    "Do not edit by hand. Stresses at LIMIT load, Pa; s3 = compression magnitude.",
           "c2r5": {"tcd_K_Ic_pa_sqrtm": pv(meta["K_Ic"], "Pa m^0.5", "XPS fracture toughness, KEM 776:160 "
                                            "(K_Ice 0.0547 MPa m^0.5, n = 3), C2.md section 1.3"),
                    "tcd_sigma0_pa": pv(meta["sigma0"], "Pa", "plain strength for the TCD length: FOAMULAR 250 "
                                        "flexural minimum 75 psi (ASTM C203), C2.md section 1.3"),
                    "measure_radius_m": pv(round(meta["L_tcd_m"] / 2, 5), "m",
                                           "ball radius used in the FE measure, L/2 rounded to 0.01 mm")}}
    c = out["c2r5"]
    for cid, (f, key) in CASES.items():
        r = m[f][key]
        c[f"{cid}_h_m"] = pv(r["h_m"], "m", f"local element size at the corners, {key}")
        for k in ("s1", "s3", "tau"):
            c[f"{cid}_vm_{k}_lim_pa"] = pv(abs(r["foam"][k]["vm_1.78"]), "Pa",
                                           f"vm(L/2) {k}, limit, {key} (ball centre {r['foam'][k]['vm_1.78_at']})")
            c[f"{cid}_peak_{k}_lim_pa"] = pv(abs(r["foam"][k]["peak"]), "Pa",
                                             f"element peak {k}, limit, {key} (at {r['foam'][k]['peak_at']}; "
                                             "singular, information only)")
        if "bead" in r.get("other", {}) and not cid.endswith("_servo"):
            c[f"{cid}_bead_s1_lim_pa"] = pv(r["other"]["bead"]["s1"], "Pa", f"bead max principal, limit, {key}")
    a, b = m[CHECK[0]][CHECK[1]]["foam"], m[W2][CASES["tape50_L2"][1]]["foam"]
    dev = max(abs(a[k]["vm_1.78"] / b[k]["vm_1.78"] - 1) for k in a)
    c["rerun_check_rel"] = pv(dev, "-", "largest |wave-1 / wave-2 - 1| of the decided-model vm(L/2) at level 2: "
                                        "wave 1 ran before A1's D-147 params edit (fin tube OD 22.10 mm, block bore "
                                        "follows), wave 2 on the current params")
    runs = json.loads(RUNS.read_text())
    out["_runs"] = {t: {k: r[k] for k in ("args", "stats")} for t, r in runs.items() if not t.startswith("_")}
    OUTF.write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k, v in c.items():
        if "_vm_" in k or k.startswith("rerun"):
            val = v["value"]
            print(f"{k:34s} {val * 1.5 / 1e3:8.1f} kPa ult" if "_pa" in k else f"{k:34s} {val:.3g}")
    print("wrote", OUTF.relative_to(HERE.parents[2]))


if __name__ == "__main__":
    main()
