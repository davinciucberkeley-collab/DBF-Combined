"""B3 design studies on the AVL model (not part of the proof chain; feeds S-AND-C.md tables and CHANGE-REQUESTS.md).

Run: python -I redesign/team/B3/run_avl_study.py   (after sc_analysis.py; uses the same AVL cache)
Writes: avl/k09l.avl, avl/k09l.mass (the baseline model files, open them in AVL directly),
        results/study.json  (yaw-fix options, elevon chord sweep, cm sensitivity, AVL MODE cross-check).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
import avl_model as AV  # noqa: E402
import flight_models as FM  # noqa: E402
import sc_analysis as SC  # noqa: E402  (module import only: claims are not rewritten)

RES = json.loads((HERE / "results" / "sc_results.json").read_text())
PAR = json.loads((HERE.parents[1] / "params" / "params.json").read_text())
A3 = json.loads((HERE.parents[1] / "team" / "A3" / "rollup" / "rollup.json").read_text())


def pv(path):
    d = PAR
    for k in path.split("."):
        d = d[k]
    return d["value"]


b, c = pv("wing.span_m"), pv("wing.chord_m")
S = b * c
ef, yin, yout = pv("wing.elevon.chord_frac"), pv("wing.elevon.inboard_y_m"), pv("wing.elevon.outboard_y_m")
fy, fh, fle, fte = pv("fins.y_m"), pv("fins.half_height_m"), pv("fins.le_x_m"), pv("fins.te_x_m")
lim = RES["CALC-B3-CG-LIMITS"]
xt = lim["x_target"]
m = pv("requirements.mtow_gate_kg")
k = m / A3["mass"]["basic_kg"]
I = A3["inertia_kgm2"]
D, n = pv("propulsion.prop_diameter_m"), pv("propulsion.n_motors")
x_prop_off = pv("propulsion.stations.x_prop_plane_m") - pv("fins.tube.x_m")      # prop plane relative to the tube
cna, cd = 0.10, 1.1
LAT = "medium"


def cnb_total(g, x_tube, xcg, tipfin=None):
    if tipfin:
        g = dict(g, tipfin=tipfin)
    d = AV.derivatives(g, 4.0, LAT)
    p = FM.prop_terms(n, D, x_tube + x_prop_off, xcg, S, c, b, cna, 1.0)
    items = [(2 * cd * 0.022 * 0.42, x_tube), (n * cd * 0.038 * 0.035, x_tube - 0.03)]
    dt = FM.drag_items_dCnb(items, xcg, S, b)
    return {"Cnb_avl": d["Cnb"], "Cnb_props": p["dCnb"], "Cnb_tubes": dt, "Cnb": d["Cnb"] + p["dCnb"] + dt,
            "Xnp_aero": d["Xnp"], "CYb": d["CYb"], "Clb": d["Clb"]}


def main():
    out = {}
    # ---- baseline model files
    g0 = AV.geometry_from(b, c, ef, yin, yout, fy, fh, fle, fte, xt, 0.0)
    (HERE / "avl" / "k09l.avl").write_text(AV.avl_geometry(g0, "fine"))
    (HERE / "avl" / "k09l.mass").write_text(AV.avl_mass(m, xt, 0.0, I["Ixx"] * k, I["Iyy"] * k, I["Izz"] * k,
                                                        I["Ixz"] * k, 1.225, 9.80665))
    # ---- directional options at the CG target (CG held by the pod/pack; A3 sensitivity 0.339 mm/mm for stations)
    dxs = A3["cg"]["dxcg_dx"]["stations"]
    opts = [("O0 baseline: tube -0.10, fin -0.10..0.30", -0.10, {}, None),
            ("O1 tube -0.045 (CG on target without moving the pod)", -0.045, {"fle": -0.045}, None),
            ("O2 tube -0.10, fin LE swept to +0.06 at the tips, tube braced", -0.10, {"fin_le_tip": 0.06}, None),
            ("O3 tube -0.045, fin LE swept to +0.06 at the tips", -0.045, {"fle": -0.045, "fin_le_tip": 0.06}, None),
            ("O4 tube +0.03 through the wing, fin +0.03..0.30", 0.03, {"fle": 0.03}, None),
            ("O4b tube +0.045 through the wing (t = 27 mm), fin +0.045..0.30", 0.045, {"fle": 0.045}, None),
            ("O5 baseline + tip fins 0.05..0.30 x +/-0.19", -0.10, {}, {"xle": 0.05, "c": 0.25, "h": 0.19}),
            ("O6 tube -0.045 + tip fins 0.05..0.30 x +/-0.19", -0.045, {"fle": -0.045},
             {"xle": 0.05, "c": 0.25, "h": 0.19}),
            ("O7 O3 + tip fins", -0.045, {"fle": -0.045, "fin_le_tip": 0.06}, {"xle": 0.05, "c": 0.25, "h": 0.19})]
    rows = []
    for name, xtube, mod, tip in opts:
        g = dict(g0, **mod)
        r = cnb_total(g, xtube, xt, tip)
        r["option"] = name
        r["cg_shift_from_stations_m"] = dxs * (xtube - fle)
        r["pod_group_shift_to_hold_target_m"] = -(r["cg_shift_from_stations_m"] + A3["cg"]["cg_m"][0] - xt) /             A3["cg"]["dxcg_dx"]["pod_group"]
        rows.append(r)
        print(f"{name:62s} Cnb {r['Cnb']:+.4f} (avl {r['Cnb_avl']:+.4f}) Xnp {r['Xnp_aero']:.4f} "
              f"pod shift {1000 * r['pod_group_shift_to_hold_target_m']:+.0f} mm")
    out["yaw_options"] = rows
    # ---- elevon chord sweep at the CG target (trim cost, roll power, area fraction)
    sw = []
    long = RES["CALC-B3-AVL-LONG"]
    xnp = RES["CALC-B3-NP"]["xnp"]
    for f in (0.18, 0.22, 0.26, 0.30):
        d = AV.derivatives(dict(g0, ef=f), 4.0, LAT)
        frac = 2 * ((yin[1] - yin[0]) + (yout[1] - yout[0])) * f * c / S
        cm_ac = long["cm_np_thin"] - 0.0155
        CL, dl = FM.trimmed_clmax(0.9, cm_ac, (xnp - xt) / c, d["CLd01"] * 0.63, d["Cmd01"] * 0.63, xt, xt, c)
        pb = abs(d["Cld02"]) * 0.63 * 15 / abs(d["Clp"])
        sw.append({"ef": f, "area_frac": frac, "CLd": d["CLd01"], "Cmd": d["Cmd01"], "Cld": d["Cld02"],
                   "clmax_trim": CL, "delta_trim": dl, "vs_trim": FM.stall_speed(m, 9.80665, 1.225, S, CL),
                   "pb2v_15deg": pb})
        print(f"ef {f}: area {frac:.3f} Cmd {d['Cmd01']:.5f} CLd {d['CLd01']:.5f} CLmax_t {CL:.3f} d {dl:+.1f} "
              f"Vs {sw[-1]['vs_trim']:.2f} pb2v {pb:.3f}")
    out["elevon_sweep"] = sw
    # ---- cm_ac sensitivity (Hepperle +0.0145 vs XFOIL)
    sens = []
    for label, dcm in (("XFOIL Re 3e5 (baseline)", -0.0155), ("thin airfoil", 0.0), ("Hepperle +0.0145", 0.0145 - 0.0063)):
        cm_ac = long["cm_np_thin"] + dcm
        r = {"case": label, "cm_ac": cm_ac}
        for tag, sm in (("sm5", 0.05), ("target", (xnp - xt) / c), ("sm3", 0.03)):
            CL, dl = FM.trimmed_clmax(0.9, cm_ac, sm, long["CLd"] * 0.63, long["Cmd_ref"] * 0.63, xnp - sm * c,
                                      long["xref"], c)
            r[f"vs_{tag}"] = FM.stall_speed(m, 9.80665, 1.225, S, CL)
            r[f"d_{tag}"] = dl
        sens.append(r)
        print(r)
    out["cm_sensitivity"] = sens
    # ---- AVL MODE cross-check (aero only: no props, no tubes) at the CG target, 15 m/s
    V = pv("performance.cruise_ms")
    CL = 2 * m * 9.80665 / (1.225 * V * V * S)
    g1 = AV.geometry_from(b, c, ef, yin, yout, fy, fh, fle, fte, xt, 0.0)
    mass = AV.avl_mass(m, xt, 0.0, I["Ixx"] * k, I["Iyy"] * k, I["Izz"] * k, I["Ixz"] * k, 1.225, 9.80665)
    r = AV.modes(g1, CL, V, mass, LAT)
    out["avl_modes_aero_only"] = {"CL": CL, "eig": r["eig"], "trim_d1_thin": r["st"]["d1"]}
    print("AVL MODE eigenvalues (aero only):", r["eig"])
    # ---- trim drag for B1 (CR-B1-04): CL at 16 m/s, elevon trim from the sweep (physical x effectiveness = AVL)
    V16 = 16.0
    CL16 = 2 * m * 9.80665 / (1.225 * V16 * V16 * S)
    d16 = [r for r in RES["CALC-B3-TRIM-SWEEP"]["table"]["target"] if abs(r[0] - V16) < 1e-6][0][3]
    eff = 0.63
    r0 = AV.run_case(AV.avl_geometry(g1, LAT), [f"a c {CL16}", "d1 d1 0", "d2 d2 0"])["st"]
    r1 = AV.run_case(AV.avl_geometry(g1, LAT), [f"a c {CL16}", f"d1 d1 {d16 * eff}", "d2 d2 0"])["st"]
    out["trim_drag_16ms"] = {"CL": CL16, "delta_phys_deg": d16, "delta_avl_deg": d16 * eff, "CDi_clean": r0["CDind"],
                             "CDi_trimmed": r1["CDind"], "e_clean": r0["e"], "e_trimmed": r1["e"],
                             "alpha_clean": r0["Alpha"], "alpha_trimmed": r1["Alpha"]}
    print("trim drag 16 m/s:", out["trim_drag_16ms"])
    (HERE / "results" / "study.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
