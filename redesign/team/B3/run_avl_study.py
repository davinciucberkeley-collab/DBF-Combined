"""B3 design studies on the R3 AVL model (not part of the proof chain; feeds S-AND-C.md tables).

Run: python -I redesign/team/B3/run_avl_study.py   (after sc_analysis.py; shares the AVL cache)
Writes: avl/k09l.avl, avl/k09l.mass (baseline model files, open them in AVL 3.52 directly),
        results/study.json  (sensitivities, elevon chord sweep, layout options for D-17, AVL MODE cross-check,
        trim drag for B1).
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
CLM = {n["id"]: n.get("value") for n in json.loads((HERE / "claims.json").read_text())["nodes"]}
ROOT = HERE.parents[1]
PAR = json.loads((ROOT / "params" / "params.json").read_text())
A3 = json.loads((ROOT / "team" / "A3" / "rollup" / "rollup.json").read_text())
B2 = json.loads((ROOT / "team" / "B2" / "claims.json").read_text())
B2V = {n["id"]: n.get("value") for n in B2["nodes"]}


def pv(path):
    d = PAR
    for k in path.split("."):
        d = d[k]
    return d["value"]


b, c = pv("wing.span_m"), pv("wing.chord_m")
S = b * c
geo = {"b": b, "c": c, "ef": pv("wing.elevon.chord_frac"), "yin": pv("wing.elevon.inboard_y_m"),
       "yout": pv("wing.elevon.outboard_y_m"), "fy": pv("fins.y_m"), "fh": pv("fins.half_height_m"),
       "fle": pv("fins.le_x_m"), "fte": pv("fins.te_x_m")}
m, g0, rho = pv("requirements.mtow_gate_kg"), pv("env.g_ms2"), pv("env.rho_kgm3")
lim = RES["CALC-B3-CG-LIMITS"]
npr = RES["CALC-B3-NP"]
xnp, xnp_a, xt = npr["xnp"], CLM["CL-B3-XNP-AERO"], lim["x_target"]
eta, dcm = B2V["CL-B2-ELEVON-ETA"], B2V["CL-B2-DCM-VISC"]
tab = CLM["ASM-B3-CLMAX-FLAP"]
k = m / A3["mass"]["basic_kg"]
I = A3["inertia_kgm2"]
zcg = A3["cg"]["cg_m"][2]


def cs(x, xnp_tot=xnp, dcm_=dcm, eta_=eta, gg=None):
    r = SC.critical_section(gg or geo, x + (xnp_a - xnp_tot), 0.0, eta_, dcm_, tab)
    r["vs"] = FM.stall_speed(m, g0, rho, S, r["CLmax"])
    r.pop("history", None)
    return r


def main():
    out = {}
    # ---- baseline model files (fine lattice, CG target, A3 z)
    gb = AV.geometry_from(**geo, xref=xt, zref=zcg)
    (HERE / "avl" / "k09l.avl").write_text(AV.avl_geometry(gb, "fine"))
    (HERE / "avl" / "k09l.mass").write_text(AV.avl_mass(m, xt, zcg, I["Ixx"] * k, I["Iyy"] * k, I["Izz"] * k,
                                                        I["Ixz"] * k, rho, g0))
    # ---- where the A3 R3 layout sits for each pack mass and the pack trim travel (D-24 station x -0.001)
    chk = RES["CALC-B3-CG-CHECK"]
    xc = chk["x_centred"]
    lay = {"x_pack_nominal": xc, "x_pack_fwd_stop": chk["cg_slide_fwd"], "x_pack_aft_stop": chk["cg_slide_aft"],
           "pack_x_for_target": chk["pack_x_target"], "dxcg_dx_pack": A3["cg"]["dxcg_dx"]["pack"],
           "pack_light_503g_at_A3_station": A3["cg"]["cg_x_pack_light_heavy_m"][0],
           "pack_heavy_680g_at_A3_station": A3["cg"]["cg_x_pack_light_heavy_m"][1],
           "slide_cg_range": A3["cg"]["cg_x_trim_range_m"], "x_fwd": lim["x_fwd"], "x_aft": lim["x_aft"]}
    out["layout_r3"] = lay
    print("R3 layout:", json.dumps(lay))
    # ---- sensitivities of NP / aft limit / trimmed stall (CG held at the target)
    long = RES["CALC-B3-AVL-LONG"]
    sens = []
    for label, cna in (("prop dCN/da -50 %", 0.055), ("baseline 0.11", 0.11), ("prop dCN/da +50 %", 0.165)):
        p = FM.prop_terms(4, pv("propulsion.prop_diameter_m"), pv("propulsion.stations.x_prop_plane_m"), xnp_a, S, c,
                          b, cna, 1.15)
        vol = 0.6 * math.prod(pv("pod.size_m"))
        x = xnp_a - (p["dCma"] + FM.pod_dCma(vol, S, c, 0.5)) / (long["CLa"] + p["dCLa"]) * c
        sens.append({"case": label, "xnp": x, "x_aft": x - 0.05 * c, "Cnb_props_per_rad_about_xnp": p["dCnb"]})
    for label, d in (("dcm -0.01 (more nose-down)", dcm - 0.01), ("dcm +0.01", dcm + 0.01)):
        r = cs(xt, dcm_=d)
        sens.append({"case": label, "vs_target": r["vs"], "delta": r["delta"], "clmax": r["CLmax"]})
    for label, e_ in (("eta -20 %", eta * 0.8), ("eta +20 %", eta * 1.2)):
        r = cs(xt, eta_=e_)
        sens.append({"case": label, "vs_target": r["vs"], "delta": r["delta"], "clmax": r["CLmax"]})
    out["sensitivity"] = sens
    for s_ in sens:
        print(s_)
    # ---- elevon chord sweep at the CG target (B2's clmax-vs-flap table reused for every hinge: approximate)
    sw = []
    vt = CLM["CL-B3-VT-TRIM"]
    for f in (0.18, 0.22, 0.26):
        gg = dict(geo, ef=f)
        d = AV.derivatives(AV.geometry_from(**gg, xref=xt, zref=0.0), 4.0, "medium")
        r = cs(xt, gg=gg)
        frac = 2 * ((geo["yin"][1] - geo["yin"][0]) + (geo["yout"][1] - geo["yout"][0])) * f * c / S
        da = 25 - abs(r["delta"])
        p = abs(d["Cld02"]) * eta * da / abs(d["Clp"]) * 2 * vt / b
        sw.append({"ef": f, "area_frac": frac, "Cmd_thin": d["Cmd01"], "clmax_trim": r["CLmax"], "delta": r["delta"],
                   "vs": r["vs"], "roll_degs_at_vt_after_stall_trim": math.degrees(p)})
        print(sw[-1])
    out["elevon_sweep"] = sw
    # ---- directional fixes for CL-B3-CNB (aft CG, 1.3 Vs): AVL wing+fins term only; props/tubes/pod terms unchanged
    lat = RES["CALC-B3-LATDIR"]
    other = lat["Cnb"] - lat["Cnb_avl"]
    CLvt = 2 * m * g0 / (rho * vt * vt * S)
    dirs = []
    for label, mod in (("R3 baseline (half-fins 0.21 m, D-26)", {}), ("R1 half-fins 0.19 m", {"fh": 0.19}),
                       ("half-fin TE +15 mm (fte 0.335, feet move aft)", {"fte": 0.335})):
        gg = dict(geo, **mod)
        d = AV.derivatives_cl(AV.geometry_from(**gg, xref=lim["x_aft"], zref=0.0), CLvt, "fine")
        dirs.append({"option": label, "Cnb_avl": d["Cnb"], "Cnb_total": d["Cnb"] + other, "Xnp_aero": d.get("Xnp")})
        print(dirs[-1])
    out["directional_options"] = dirs
    # ---- hover yaw: cant needed and ratio at candidate cants (30 % differential, B4 swirl recovery)
    hv = RES["CALC-B3-HOVER"]
    r_ = math.hypot(pv("propulsion.stations.y_m"), pv("propulsion.stations.z_m"))
    cants = []
    for cd_ in (3.0, 5.0, 7.0, 8.0):
        M = 4 * hv["dT_N"] * (hv["kq_eff_m"] + r_ * math.sin(math.radians(cd_)))
        cants.append({"cant_deg": cd_, "M_yaw_Nm": M, "ratio": M / hv["dist_yaw_Nm"],
                      "acc_rads2": M / (I["Ixx"] * k), "thrust_loss_frac": 1 - math.cos(math.radians(cd_))})
        print(cants[-1])
    out["hover_cant"] = cants
    # ---- AVL MODE cross-check (aero only: no props, tubes, pod) at the CG target, cruise speed
    V = pv("performance.cruise_ms")
    CL = 2 * m * g0 / (rho * V * V * S)
    g1 = AV.geometry_from(**geo, xref=xt, zref=0.0)
    mass = AV.avl_mass(m, xt, 0.0, I["Ixx"] * k, I["Iyy"] * k, I["Izz"] * k, I["Ixz"] * k, rho, g0)
    r = AV.modes(g1, CL, V, mass, "medium")
    out["avl_modes_aero_only"] = {"V": V, "CL": CL, "eig": r["eig"], "trim_d1_thin": r["st"]["d1"]}
    print("AVL MODE eigenvalues (aero only):", r["eig"])
    # ---- trim drag for B1 at cruise (induced only; elevon profile drag is B2's)
    gt = AV.geometry_from(**geo, xref=xt + (xnp_a - xnp), zref=0.0, egain=eta)
    tr = AV.trim_sweep(gt, [CL], -dcm, "medium")[0]
    cl0 = AV.run_case(AV.avl_geometry(g1, "medium"), [f"a c {CL}", "d1 d1 0", "d2 d2 0"])["st"]
    out["trim_drag_cruise"] = {"V": V, "CL": CL, "delta_deg": tr["d1"], "alpha_trim": tr["alpha"],
                               "CDi_trimmed": tr["CDind"], "CDi_clean": cl0["CDind"], "e_clean": cl0["e"]}
    print("trim drag:", out["trim_drag_cruise"])
    (HERE / "results" / "study.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
