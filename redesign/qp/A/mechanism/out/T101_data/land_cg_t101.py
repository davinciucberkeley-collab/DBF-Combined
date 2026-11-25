"""T-101 AM-061: C5 landing (landing_a.py unchanged) at the D-255 flying CG 23.49 mm vs the as-drawn 22.049 mm.
Corners of the D-243 foam region (Fp 37.5 / 39.0 N, zeta 0.02 / 0.05), stroke 20 mm, rib 25x23, the 10 AR-014 cases (as sweep_t098.py).
Env as T-098: LAND_MASS_KG 1.881, LAND_MASS_MODEL cad, LAND_PART_TABLE T097_data/cad_part_table_t097.json; CG shift via simulate(cgdx=...) from the cad_mass.json CG 22.049 mm (first version used LAND_CG_X_MM, which landing_a caches per process: both CGs ran at 22.049).
usage (repo root): python -I redesign/qp/A/mechanism/out/T101_data/land_cg_t101.py <out.json> [nproc]"""
import sys, os, json, math
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
SA = os.path.abspath(os.path.join(HERE, "..", "..", "..", "structures"))
T098 = os.path.abspath(os.path.join(HERE, "..", "T098_data"))
sys.path.insert(0, T098)
CASES = [("hard level", dict(v_sink=1.2)), ("hard 10 narrow", dict(v_sink=1.2, th_n=10)), ("hard 10 narrow neg", dict(v_sink=1.2, th_n=-10)),
         ("hard 10 wide", dict(v_sink=1.2, th_w=10)), ("hard 7/7 combo", dict(v_sink=1.2, th_n=7, th_w=7)),
         ("hard 10 narrow + drift .5", dict(v_sink=1.2, th_n=10, drift=0.5, drift_dir=0.0)),
         ("hard 10 wide + drift .5 y", dict(v_sink=1.2, th_w=10, drift=0.5, drift_dir=math.pi/2)),
         ("normal level .5", dict(v_sink=0.5)), ("normal 10 narrow .5", dict(v_sink=0.5, th_n=10)),
         ("normal 10 wide .5 + drift", dict(v_sink=0.5, th_w=10, drift=0.5, drift_dir=math.pi/2))]

def job(a):
    cg, Fp, zeta, name, kw = a
    os.environ.update(LAND_MASS_KG="1.881", LAND_MASS_MODEL="cad", LAND_PART_TABLE=os.path.join(HERE, "..", "T097_data", "cad_part_table_t097.json"),
                      LAND_RIB_OD="0.025", LAND_RIB_ID="0.023")
    sys.path.insert(0, SA)
    import landing_a as L
    r = L.simulate(Fp=Fp, s_max=0.020, zeta=zeta, cgdx=(cg-22.049)*1e-3, **kw)   # CG shift via landing_a cgdx (body x = aft = down in stance); LAND_CG_X_MM is cached per process, so not used
    return dict(cg_mm=cg, Fp=Fp, zeta=zeta, case=name, stroke_mm=float(r["dmax_mm"].max()), n_g=float(r["n_peak"]), tilt_deg=float(r["tilt_end"]), rib_rf=float(r["rib_rf"]))

if __name__ == "__main__":
    out = sys.argv[1]; npr = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    T = [(cg, Fp, z, n, kw) for cg in (22.049, 23.49) for Fp in (37.5, 39.0) for z in (0.02, 0.05) for n, kw in CASES]
    with Pool(npr) as p: R = p.map(job, T)
    json.dump(R, open(out, "w"), indent=1)
    for cg in (22.049, 23.49):
        for Fp in (37.5, 39.0):
            for z in (0.02, 0.05):
                g = [r for r in R if r["cg_mm"] == cg and r["Fp"] == Fp and r["zeta"] == z]
                w = dict(stroke=max(r["stroke_mm"] for r in g), n=max(r["n_g"] for r in g), tilt=max(r["tilt_deg"] for r in g), rf=min(r["rib_rf"] for r in g))
                ok = w["stroke"] <= 20 and w["n"] <= 12 and w["tilt"] <= 3 and w["rf"] >= 1.0
                print(f"CG {cg:6.3f} Fp {Fp} zeta {z}: stroke {w['stroke']:.2f} mm, n {w['n']:.2f} g, tilt {w['tilt']:.2f} deg, rib RF {w['rf']:.2f} -> {'PASS' if ok else 'FAIL'}")
