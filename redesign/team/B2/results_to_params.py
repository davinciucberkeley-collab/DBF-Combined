"""Copy the XFOIL / AVL results the proof chain needs into team/B2/params.json (keys under "b2").

Run after xfoil_wing.py and avl_wing.py, before wing_claims.py:
    python -I redesign/team/B2/results_to_params.py
Every value cites the run that produced it (SRC-B2-XFOIL, SRC-B2-AVL, declared in wing_claims.py).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
P = json.loads((REDESIGN / "params" / "params.json").read_text(encoding="utf-8"))
X = json.loads((HERE / "out" / "xfoil_results.json").read_text())
A = json.loads((HERE / "out" / "avl_results.json").read_text())
L = json.loads((HERE / "out" / "loads_spanwise.json").read_text())
FOIL = A["chosen"]
CS_CASE = "CL0.80"            # trimmed case nearest the predicted stall CL (critical-section arrays)


def p(value, unit, src, note=None, status=None):
    d = {"value": value, "unit": unit, "source": src}
    if note:
        d["note"] = note
    if status:
        d["status"] = status
    return d


def section_at(foil, xc):
    a = np.loadtxt(HERE / "airfoils" / f"{foil}.dat", skiprows=1)
    i = int(np.argmin(a[:, 0]))
    up, lo = a[: i + 1][::-1], a[i:]
    return float(np.interp(xc, up[:, 0], up[:, 1])), float(np.interp(xc, lo[:, 0], lo[:, 1])), a


def hinge_max(foil, re_tag="4.0e5"):
    best, where = 0.0, None
    vbest = 0.0
    for k, d in X["hinge"].items():
        if not k.startswith(f"hm_{foil}_re{re_tag}_f"):
            continue
        flap = float(k.split("_f")[1].split("_")[0])
        if abs(flap) != 25.0:
            continue
        for a, h, c in zip(d["alpha"], d["hmom_qc2"], d["converged"]):
            if h != h:
                continue
            if k.endswith("_i") and abs(h) > abs(best):
                best, where = h, (flap, a)
            if k.endswith("_v") and c and abs(h) > abs(vbest):
                vbest = h
    return best, where, vbest


def main():
    chord = P["wing"]["chord_m"]["value"]
    xs = P["wing"]["spar"]["x_m"]["value"] / chord
    yu, yl, a = section_at(FOIL, xs)
    i = int(np.argmin(a[:, 0]))
    up, lo = a[: i + 1][::-1], a[i:]
    xx = np.linspace(0.01, 0.99, 981)
    t = np.interp(xx, up[:, 0], up[:, 1]) - np.interp(xx, lo[:, 0], lo[:, 1])
    case = L["cases"][CS_CASE]
    cfl = A["foils"][FOIL]["clmax_vs_flap_re2.3e5"]
    dl, cm = [r[0] for r in cfl], [r[1] for r in cfl]
    yin, yout = P["wing"]["elevon"]["inboard_y_m"]["value"], P["wing"]["elevon"]["outboard_y_m"]["value"]
    in_el = [(yin[0] <= y <= yin[1]) or (yout[0] <= y <= yout[1]) for y in case["y_m"]]
    clmax_local = [float(np.interp(case["elevator_deg"] if e else 0.0, dl, cm)) for e in in_el]
    hmax, hwhere, hv = hinge_max(FOIL)
    F = A["foils"][FOIL]
    xsum = {k: v["summary"] for k, v in X["polars"].items()}
    s23 = xsum[f"{FOIL}_re2.3e5_n9_f+0_p220"]
    neg = np.array(X["polars"][f"{FOIL}_re3.0e5_n9_f+0_p220_neg16"]["table"])
    clmin = float(neg[:, 1].min())
    out = {
        "_note": "Written by team/B2/results_to_params.py from out/xfoil_results.json and out/avl_results.json. "
                 "Do not edit by hand; re-run xfoil_wing.py, avl_wing.py, then this script.",
        "b2": {
            "section": {
                "foil": p(FOIL.upper(), "-", "SRC-B2-S5010-COORD", "recommended section (WING-AERO.md section 2)"),
                "t_c": p(round(float(t.max()), 4), "-", "SRC-B2-S5010-COORD", "from the coordinate file"),
                "upper_zc_at_spar": p(round(yu, 5), "-", "SRC-B2-S5010-COORD", f"upper surface z/c at x/c = {xs:.4f}"),
                "lower_zc_at_spar": p(round(yl, 5), "-", "SRC-B2-S5010-COORD", f"lower surface z/c at x/c = {xs:.4f}"),
            },
            "xfoil": {
                "re_stall": p(2.3e5, "-", "SRC-B2-XFOIL", "Re of the stall polars (V 11.3-11.9 m/s, c 0.30 m)"),
                "clmax_2d_re2.3e5": p(round(s23["clmax"], 4), "-", "SRC-B2-XFOIL", "elevon neutral, Ncrit 9"),
                "cm0_2d_re2.3e5": p(round(s23["cm0"], 4), "-", "SRC-B2-XFOIL", "about c/4, elevon neutral"),
                "cla_2d_per_rad": p(round(s23["cla_per_rad"], 3), "1/rad", "SRC-B2-XFOIL", "alpha -2..4 deg, Re 2.3e5"),
                "alpha0_2d_deg": p(round(s23["alpha0_deg"], 2), "deg", "SRC-B2-XFOIL", "Re 2.3e5, elevon neutral"),
                "cm_cl07_2d": p(round(F["cm_section_cl0.7"], 4), "-", "SRC-B2-XFOIL", "section cm c/4 at cl 0.7, Re 2.3e5"),
                "clmin_2d": p(round(clmin, 3), "-", "SRC-B2-XFOIL",
                              "last converged point of the negative sweep, Re 3e5 (lower-surface separation beyond)"),
                "elevon_eta": p(round(F["eta"], 3), "-", "SRC-B2-XFOIL",
                                "XFOIL dcm/d(delta) at cl 0.5, -10..0 deg, mean of Re 2.3e5/3.0e5, over thin-airfoil theory"),
                "hinge_coef_max": p(round(abs(hmax), 5), "-", "SRC-B2-XFOIL",
                                    f"max |HMOM/(q c^2)| at +/-25 deg, alpha -4..8 deg, Re 4e5, INVISCID (upper bound); "
                                    f"at delta {hwhere[0]:+g}, alpha {hwhere[1]:+g}; converged viscous max {abs(hv):.4f}"),
            },
            "avl": {
                "dcm_visc": p(round(F["dcm_visc"], 5), "-", "SRC-B2-AVL",
                              "XFOIL section cm (cl 0.7, Re 2.3e5) minus AVL thin-airfoil Cm_ac; added to AVL Cm"),
                "xnp_m": p(round(F["Xnp_m"], 5), "m", "SRC-B2-AVL", "props-off wing + flat-plate fins, no pod"),
                "cla_per_rad": p(round(F["CLa_per_rad"], 4), "1/rad", "SRC-B2-AVL"),
                "e_oswald": p(round(A["design_oswald"]["e_oswald"], 4), "-", "SRC-B2-AVL",
                              "trimmed parabolic fit CL 0.3-0.9, wing + fins only"),
                "cd0_wing": p(round(A["design_oswald"]["CD0_wing"], 5), "-", "SRC-B2-AVL", "wing section drag only"),
                "cnb_per_rad": p(round(F["derivs_a4"]["Cnb"], 4), "1/rad", "SRC-B2-AVL",
                                 "AVL stability axes, + = weathercock stable; alpha 4 deg, CG 0.060 m"),
                "ybar_frac": p(round(L["cases"]["CL0.90"]["ybar_frac_semispan"], 4), "-", "SRC-B2-AVL",
                               "half-wing lift centroid / semi-span, trimmed CL 0.9"),
                "torsion_root_m_per_N": p(round(L["cases"]["CL0.90"]["torsion_m_per_N"][0], 5), "m", "SRC-B2-AVL",
                                          "root torsion about the spar line per N of half-wing lift, nose-up +"),
                "cs": {
                    "cl_over_CL": p(case["cl_over_CL"], "-", "SRC-B2-AVL", f"strip cl / CL, right half, trimmed {CS_CASE}"),
                    "clmax_local": p([round(c, 4) for c in clmax_local], "-", "SRC-B2-XFOIL",
                                     f"XFOIL clmax at Re 2.3e5 at each strip's elevon deflection ({case['elevator_deg']:+.2f} deg on elevon strips)"),
                    "y_m": p(case["y_m"], "m", "SRC-B2-AVL"),
                },
            },
        },
    }
    (HERE / "params.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"team/B2/params.json written: foil {FOIL}, hinge |C| {abs(hmax):.4f}, Xnp {F['Xnp_m']:.4f}, "
          f"cover upper {yu*chord*1000:.1f} mm lower {yl*chord*1000:.1f} mm")


if __name__ == "__main__":
    main()
