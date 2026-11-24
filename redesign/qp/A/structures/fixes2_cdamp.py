"""FIXES2: D-187 v2 balance with the drawn hinge damper over its temperature range.  python -I fixes2_cdamp.py -> fixes2_cdamp.md  (imports fixes2_run.py; 3 processes, ~3 min)
c nominal 1.03e-3 N m s/rad at 25 C is a_model.py DMP_C; hot (50 C) and cold (0 C) factors are EST (PDMS viscosity-temperature coefficient about 0.6; not looked up)."""
import os, sys, multiprocessing as mp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixes2_run as R
if __name__ == "__main__":
    L = []
    def P(s=""): print(s, flush=True); L.append(s)
    cs = [("hot 50 C (EST x0.6)", 0.6*1.03e-3), ("nominal 25 C", 1.03e-3), ("cold 0 C (EST x2)", 2.06e-3), ("1/2 of hot (leak / half-fill)", 0.31e-3)]
    tasks = [(n, k, 0.0096, 15.6, 0.020, 0.25, c) for n, c in cs for k in ("kd", "nom", "hi")]
    with mp.Pool(3) as pool: res = pool.map(R.run_case, tasks)
    P("| hinge damper state | corner | wing f_h / f_a | no instability <= 28.8 at any K (0.01-20) | unstable K band | worst damping ratio needed | lowest onset over the grid (m/s) |"); P("|---|---|---|---|---|---|---|")
    for r in res: P(R.fmt(r))
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixes2_cdamp.md"), "w").write("\n".join(L))
