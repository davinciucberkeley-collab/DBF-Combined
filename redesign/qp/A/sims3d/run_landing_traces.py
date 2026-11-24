"""T-105 unit 1(b): the ten AR-014 touchdown cases at the D-243 chosen point (Fp 37.5 N, zeta 0.05, usable stroke 20 mm, drawn rib tube 25x23), as
time histories in sims3d/out/landing_<case>.json (200 Hz), and a peak-value check against mechanism/out/T098_results.json 'chosen_37.5N' rows.
usage: python -I run_landing_traces.py [--cad-mass <cad_mass.json>] [--out <dir>] [--nproc N]
Inputs are exactly those of mechanism/out/T098_data/sweep_t098.py (LAND_MASS_KG 1.881, LAND_MASS_MODEL cad, T097 part table, rib 25x23) with ONE addition:
sitl/cad_mass.json (CG) is read from --cad-mass, default sims3d/T098_cad_mass.json = the file at git HEAD dff3191a, i.e. the CG T-098 used
(x 22.049 mm). The working-tree sitl/cad_mass.json changed after T-098 (T-101 chord work: x 20.688 mm), which moves the landing peaks; pass
--cad-mass ../sitl/cad_mass.json to get the current-CAD histories instead. Default behaviour of landing_a.py is untouched."""
import argparse, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.normpath(os.path.join(HERE, ".."))
ap = argparse.ArgumentParser(); ap.add_argument("--cad-mass", default=os.path.join(HERE, "T098_cad_mass.json")); ap.add_argument("--out", default=os.path.join(HERE, "out")); ap.add_argument("--nproc", type=int, default=10)
args = ap.parse_args()
os.environ.update(LAND_MASS_KG="1.881", LAND_MASS_MODEL="cad", LAND_PART_TABLE=os.path.join(A, "mechanism", "out", "T098_data", "cad_part_table_t097.json"), LAND_RIB_OD="0.025", LAND_RIB_ID="0.023")
sys.path.insert(0, os.path.join(A, "structures"))
CASES = [("hard level", dict(v_sink=1.2)), ("hard 10 narrow", dict(v_sink=1.2, th_n=10)), ("hard 10 narrow neg", dict(v_sink=1.2, th_n=-10)),
         ("hard 10 wide", dict(v_sink=1.2, th_w=10)), ("hard 7/7 combo", dict(v_sink=1.2, th_n=7, th_w=7)),
         ("hard 10 narrow + drift .5", dict(v_sink=1.2, th_n=10, drift=0.5, drift_dir=0.0)),
         ("hard 10 wide + drift .5 y", dict(v_sink=1.2, th_w=10, drift=0.5, drift_dir=math.pi/2)),
         ("normal level .5", dict(v_sink=0.5)), ("normal 10 narrow .5", dict(v_sink=0.5, th_n=10)),
         ("normal 10 wide .5 + drift", dict(v_sink=0.5, th_w=10, drift=0.5, drift_dir=math.pi/2))]   # same list and order as sweep_t098.py / landing_a.py __main__
FP, ZETA = 37.5, 0.05


def job(a):
    name, kw = a
    import numpy as np, landing_a as L
    g = L.cad_geom(); cm = json.load(open(args.cad_mass)); g["cg"] = np.array([cm["cg_x_m"], cm["cg_y_m"], cm["cg_z_m"]])
    h = []
    r = L.simulate(Fp=FP, zeta=ZETA, hist=h, **kw)
    slug = name.replace(" ", "_").replace("+", "plus").replace("/", "-").replace(".", "p")
    p = os.path.join(args.out, "landing_%s.json" % slug)
    L.write_trace(p, name, FP, kw, r, h, extra=dict(zeta=ZETA, s_max_m=0.020, cg_m=[float(x) for x in g["cg"]], cad_mass_source=os.path.relpath(args.cad_mass, A).replace("\\", "/"),
                                                    t098_basis="D-243 chosen point; rib 25x23; mass 1.881 kg; T097 part table"))
    return name, p, dict(stroke_mm=float(r["dmax_mm"].max()), n_g=float(r["n_peak"]), tilt_deg=float(r["tilt_end"]), rib_rf=float(r["rib_rf"]))


if __name__ == "__main__":
    import multiprocessing as mp
    os.makedirs(args.out, exist_ok=True)
    with mp.Pool(args.nproc) as pool: R = pool.map(job, CASES, chunksize=1)
    t98 = json.load(open(os.path.join(A, "mechanism", "out", "T098_results.json")))["rows"]
    M = {"foam stroke (mm)": ("stroke_mm", 1), "peak load factor (g)": ("n_g", 2), "end tilt (deg)": ("tilt_deg", 1), "rib-root RF (min over run)": ("rib_rf", 2)}
    bad = 0
    print("%-28s %-26s %9s %9s %s" % ("case", "metric", "T098", "here", "match"))
    for name, p, pk in R:
        for row in t98:
            if row["case"] == "chosen_37.5N_rib25x23/" + name and row["metric"] in M:
                k, nd = M[row["metric"]]; v = round(pk[k], nd); ok = abs(v - row["value"]) < 0.5 * 10 ** -nd + 1e-9; bad += (not ok)
                print("%-28s %-26s %9s %9s %s" % (name, row["metric"], row["value"], v, "ok" if ok else "MISMATCH"))
    print("mismatches:", bad); print("written:", len(R), "files in", args.out)
