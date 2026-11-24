"""T-101 U2 ladder (b): lead mass sweep at a given reach, case E, cf 0.30, elevon 7.6 g. args: reach_mm then lead masses g. plain python."""
import sys, multiprocessing as mp
import t101_flutter as T
if __name__ == "__main__":
    C0 = 1.0297e-3; reach = float(sys.argv[1])
    for ld in [float(a) for a in sys.argv[2:]]:
        tasks = [("E", k, 0.0076, ld, reach * 1e-3, 0.30, 0.3 * C0) for k in ("kd", "nom", "hi")]
        with mp.Pool(3) as p: res = p.map(T.run_case, tasks)
        print(reach, ld, [("PASS" if r["nunst"] == 0 else "FAIL%d" % r["nunst"], float(r["vmin"])) for r in res], flush=True)
