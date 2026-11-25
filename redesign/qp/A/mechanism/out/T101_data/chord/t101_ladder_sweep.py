"""T-101 U2 ladder (a): case E (0.3 C0 damper) and B-D, reach sweep, lead 10.0 g, elevon 7.6 g, cf 0.30. plain python (multiprocessing)."""
import sys, multiprocessing as mp
import t101_flutter as T
if __name__ == "__main__":
    C0 = 1.0297e-3
    for reach in [float(a) for a in sys.argv[1:]]:
        tasks = [("E%.1f" % reach, k, 0.0076, 10.0, reach * 1e-3, 0.30, 0.3 * C0) for k in ("kd", "nom", "hi")]
        with mp.Pool(3) as p: res = p.map(T.run_case, tasks)
        print(reach, [("PASS" if r["nunst"] == 0 else "FAIL%d" % r["nunst"], r["vmin"]) for r in res], flush=True)
