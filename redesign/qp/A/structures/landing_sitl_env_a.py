import sys, math
sys.path.insert(0, r"C:\Users\dillo\Downloads\Berkeley\Fall\Capstone\DBF-Combined\redesign\qp\A\structures")
import landing_a as L
recs = [("Z5_b0 (belly-on 5 m/s, 1.41 kg)", 29.1, 0.16, 0.34), ("Z5_b45", 17.2, 0.21, 0.32), ("Ta_h5 (1.381 kg)", 18.8, 0.11, 0.30), ("Tb_h5", 16.5, 0.09, 0.31), ("Lb_5e", 12.1, 0.45, 0.32), ("Z5_gb45", 11.0, 0.50, 0.32)]
for n, lean, lat, sink in recs:
    for ax in ("narrow", "wide"):
        for sg in (1, -1):
            kw = dict(v_sink=sink, drift=lat, drift_dir=(0.0 if ax == "narrow" else math.pi/2) + (0 if sg > 0 else math.pi))
            kw["th_n" if ax == "narrow" else "th_w"] = lean*sg
            q = L.simulate(Fp=30.0, **kw)
            print(f"{n:34s} lean {lean:4.1f} {ax:6s} sign {sg:+d} sink {sink} lat {lat}: stroke {q['dmax_mm'].max():5.1f} mm n {q['n_peak']:6.2f} side {q['side'].max():5.1f} N tilt_end {q['tilt_end']:6.1f} drift {q['drift_end']*1e3:5.0f} mm rib RF {q['rib_rf']:.2f}", flush=True)
