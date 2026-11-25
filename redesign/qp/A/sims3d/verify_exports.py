"""T-105 unit 1 pass check: every JSON in sims3d/out loads; 5 values per file compared with the source (independent re-read of the CSV / JSON).
usage: python -I verify_exports.py [--md]    exit 0 = all match, 1 = mismatch.  --md prints the markdown table used in README.md."""
import csv, glob, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "out"); rows = []; bad = 0


def chk(file, what, got, src, tol):
    global bad
    ok = abs(got - src) <= tol; bad += (not ok)
    rows.append((file, what, got, src, "ok" if ok else "MISMATCH"))


# flight: 5 values per file against the raw csv (rows chosen by time, nearest csv row to a json sample)
for p in sorted(glob.glob(os.path.join(OUT, "flight_*.json"))):
    d = json.load(open(p)); run = d["meta"]["run"]; n = len(d["t"])
    src = list(csv.DictReader(open(os.path.join(A, "sitl", "runs", run, "case.fwd.csv")))); T = [float(r["t"]) for r in src]
    picks = [("alt", n // 5), ("pitch", n // 2), ("dl", n // 3), ("V", 3 * n // 4), ("th1", n - 1)]
    for col, i in picks:
        t = d["t"][i]; j = min(range(len(T)), key=lambda q: abs(T[q] - t))
        assert abs(T[j] - t) < 1e-3, (run, t, T[j])
        chk(os.path.basename(p), "%s @t=%.3f" % (col, t), d[col][i], float(src[j][col]), 5e-4)
# landing: 5 values per file against T098_results.json chosen_37.5N rows (stroke, load factor, tilt, rib RF) + Fmax against T098_data/landing_cad_1881_p37p5_rib25.txt
t98 = json.load(open(os.path.join(A, "mechanism", "out", "T098_results.json")))["rows"]
txt = {}
for ln in open(os.path.join(A, "mechanism", "out", "T098_data", "landing_cad_1881_p37p5_rib25.txt")):
    if "stroke max" in ln:
        txt[ln.split("stroke max")[0].strip()] = float(ln.split("Fmax")[1].split("N")[0])
M = {"foam stroke (mm)": ("stroke_mm", 0.05), "peak load factor (g)": ("n_g", 0.005), "end tilt (deg)": ("tilt_end_deg", 0.05), "rib-root RF (min over run)": ("rib_rf", 0.005)}
for p in sorted(glob.glob(os.path.join(OUT, "landing_*.json"))):
    d = json.load(open(p)); name = d["meta"]["case"]
    for r in t98:
        if r["case"] == "chosen_37.5N_rib25x23/" + name and r["metric"] in M:
            k, tol = M[r["metric"]]; chk(os.path.basename(p), "peaks.%s vs T098 '%s'" % (k, r["metric"]), d["peaks"][k], r["value"], tol + 1e-9)
    chk(os.path.basename(p), "peaks.Fmax_N vs T098 txt", d["peaks"]["Fmax_N"], txt[name], 0.05 + 1e-9)
    assert max(d["crush_mm"][i][j] for i in range(len(d["t"])) for j in range(4)) <= d["peaks"]["stroke_mm_fullrate"] + 1e-3
# linkage: the committed linkage_kinematics.csv predates the T-101 chord edit already in the working tree (ARM_R 8.5 -> 6.86 mm, hinge x 183.75 -> 171.5 mm), so it is NOT the
# reference. Reference = independent solve with scipy brentq on linkage_core.g (not the closed form the exporter uses), plus a central difference for the gearing.
sys.path.insert(0, os.path.join(A, "mechanism")); sys.dont_write_bytecode = True
import linkage_core as k
from scipy.optimize import brentq
d = json.load(open(os.path.join(OUT, "linkage.json"))); Rp = {x["delta_deg"]: x for x in d["R"]}
for dd in (-21.0, -10.0, 0.0, 10.0, 20.0):
    t0 = math.radians(Rp[dd]["servo_theta_deg"]); tb = brentq(lambda t: k.g(t, math.radians(dd), 1), t0 - 0.2, t0 + 0.2, xtol=1e-14)
    chk("linkage.json", "R servo_theta_deg @delta=%+g vs brentq re-solve" % dd, Rp[dd]["servo_theta_deg"], math.degrees(tb), 5e-4)
fd = (math.radians(Rp[10.5]["delta_deg"] - Rp[9.5]["delta_deg"])) / (math.radians(Rp[10.5]["servo_theta_deg"] - Rp[9.5]["servo_theta_deg"]))
chk("linkage.json", "R gear @delta=+10 vs central difference (+-0.5 deg)", Rp[10.0]["gear_ddelta_dtheta"], fd, 2e-3)
chk("linkage.json", "R rod_len_mm @delta=+20 vs linkage_core.L_ROD", Rp[20.0]["rod_len_mm"], k.L_ROD * 1e3, 5e-4)
for p in glob.glob(os.path.join(OUT, "*.json")): json.load(open(p))
md = ["| file | value | exported | source | result |", "|---|---|---|---|---|"] + ["| %s | %s | %s | %s | %s |" % (f, w, g, s, r) for f, w, g, s, r in rows]
if "--md" in sys.argv: print("\n".join(md))
print("files loaded: %d; comparisons: %d; mismatches: %d" % (len(glob.glob(os.path.join(OUT, "*.json"))), len(rows), bad))
sys.exit(1 if bad else 0)
