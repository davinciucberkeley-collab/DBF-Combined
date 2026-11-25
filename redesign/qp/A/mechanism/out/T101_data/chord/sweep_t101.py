"""T-098 landing ladder sweeps (category: rigid-body dynamics).  Drives redesign/qp/A/structures/landing_a.py unchanged (no edit to it).
usage: python -I sweep_t098.py <group> <rib: 14|25> <out.json> [nproc]
groups: plateau  - 10 AR-014 cases x plateau 30..45 N step 1.5, stroke 20 mm (CAD pad 30 mm long, 2/3 usable), zeta 0.05
        zeta     - the band candidates at zeta 0.02 / 0.10
        stroke   - stroke 24 mm (36 mm free foam, CAD change, reference only) plateau 30..45
        card     - rung 1: failing case at 30 N with drift / lean / sink scanned
Env (set by the caller, same as T-097 row 2): LAND_MASS_KG=1.881 LAND_MASS_MODEL=cad LAND_PART_TABLE=<T097_data>/cad_part_table_t101.json
rib 14 = landing_a default (T-097 basis, the pre-D-226 14x12 tube); rib 25 = CAD wing.py RIB_OD/RIB_ID 25x23 (D-226)."""
import sys, os, json, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
SA = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "structures"))
group, rib, out = sys.argv[1], sys.argv[2], sys.argv[3]
nproc = int(sys.argv[4]) if len(sys.argv) > 4 else 16
os.environ.setdefault("LAND_MASS_KG", "1.882"); os.environ.setdefault("LAND_MASS_MODEL", "cad")
os.environ.setdefault("LAND_PART_TABLE", os.path.join(HERE, "cad_part_table_t101.json"))
if rib == "25": os.environ["LAND_RIB_OD"], os.environ["LAND_RIB_ID"] = "0.025", "0.023"
sys.path.insert(0, SA)
CASES = [("hard level", dict(v_sink=1.2)), ("hard 10 narrow", dict(v_sink=1.2, th_n=10)), ("hard 10 narrow neg", dict(v_sink=1.2, th_n=-10)),
         ("hard 10 wide", dict(v_sink=1.2, th_w=10)), ("hard 7/7 combo", dict(v_sink=1.2, th_n=7, th_w=7)),
         ("hard 10 narrow + drift .5", dict(v_sink=1.2, th_n=10, drift=0.5, drift_dir=0.0)),
         ("hard 10 wide + drift .5 y", dict(v_sink=1.2, th_w=10, drift=0.5, drift_dir=math.pi/2)),
         ("normal level .5", dict(v_sink=0.5)), ("normal 10 narrow .5", dict(v_sink=0.5, th_n=10)),
         ("normal 10 wide .5 + drift", dict(v_sink=0.5, th_w=10, drift=0.5, drift_dir=math.pi/2))]


def job(a):
    tag, Fp, smax, zeta, name, kw = a
    import landing_a as L
    r = L.simulate(Fp=Fp, s_max=smax, zeta=zeta, **kw)
    return dict(group=tag, Fp=Fp, s_max_mm=smax*1e3, zeta=zeta, case=name, stroke_mm=float(r["dmax_mm"].max()), n_g=float(r["n_peak"]), side_N=float(r["side"].max()),
                tilt_deg=float(r["tilt_end"]), rib_rf=float(r["rib_rf"]), drift_mm=float(r["drift_end"]*1e3), kw={k: v for k, v in kw.items()})


def tasks():
    T = []
    if group == "plateau":
        for k in range(11):
            Fp = 30.0+1.5*k
            for name, kw in CASES: T.append(("plateau", Fp, 0.020, 0.05, name, kw))
    elif group == "zeta":
        for Fp in [float(x) for x in os.environ.get("T98_FP", "36,37.5,39,40.5").split(",")]:
            for z in [float(x) for x in os.environ.get("T98_Z", "0.02,0.10").split(",")]:
                for name, kw in CASES: T.append(("zeta", Fp, float(os.environ.get("T98_S", "20"))*1e-3, z, name, kw))
    elif group == "stroke":
        for k in range(11):
            Fp = 30.0+1.5*k
            for name, kw in CASES: T.append(("stroke24", Fp, 0.024, 0.05, name, kw))
    elif group == "card":
        for d in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
            T.append(("card_drift", 30.0, 0.020, 0.05, f"hard 10 narrow drift {d}", dict(v_sink=1.2, th_n=10, drift=d, drift_dir=0.0)))
            T.append(("card_drift_neg", 30.0, 0.020, 0.05, f"hard 10 narrow drift {d} (backward)", dict(v_sink=1.2, th_n=10, drift=d, drift_dir=math.pi)))
        for L_ in (0, 2, 4, 6, 8, 10):
            T.append(("card_lean", 30.0, 0.020, 0.05, f"hard lean {L_} narrow drift 0.5", dict(v_sink=1.2, th_n=L_, drift=0.5, drift_dir=0.0)))
        for s in (0.34, 0.5, 0.7, 0.9, 1.0, 1.1, 1.2):
            T.append(("card_sink", 30.0, 0.020, 0.05, f"sink {s} narrow 10 drift 0.5", dict(v_sink=s, th_n=10, drift=0.5, drift_dir=0.0)))
        # SITL-record envelope (AR-012 recs): lean on narrow and wide axes both signs, lateral speed in the lean direction, peak sink 0.34 m/s
        recs = [("Z5_b0", 29.1, 0.16, 0.34), ("Z5_b45", 17.2, 0.21, 0.32), ("Ta_h5", 18.8, 0.11, 0.30), ("Tb_h5", 16.5, 0.09, 0.31), ("Lb_5e", 12.1, 0.45, 0.32), ("Z5_gb45", 11.0, 0.50, 0.32)]
        for n, lean, lat, sink in recs:
            for Fp in (30.0, 36.0, 40.5):
                for ax in ("narrow", "wide"):
                    for sg in (1, -1):
                        kw = dict(v_sink=sink, drift=lat, drift_dir=(0.0 if ax == "narrow" else math.pi/2)+(0 if sg > 0 else math.pi))
                        kw["th_n" if ax == "narrow" else "th_w"] = lean*sg
                        T.append(("sitl_env", Fp, 0.020, 0.05, f"{n} {ax} {sg:+d}", kw))
    return T


if __name__ == "__main__":
    import multiprocessing as mp
    t0 = time.time(); T = tasks()
    with mp.Pool(nproc) as p: R = p.map(job, T, chunksize=1)
    json.dump(dict(group=group, rib=rib, env={k: os.environ[k] for k in ("LAND_MASS_KG", "LAND_MASS_MODEL", "LAND_PART_TABLE")}, wall_s=time.time()-t0, rows=R), open(out, "w"), indent=1)
    print(f"{group} rib{rib}: {len(R)} runs, wall {time.time()-t0:.0f} s -> {out}")
