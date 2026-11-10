"""B2 verification round (B2-R3): wing aero re-run on the settled geometry and the A3 mass roll-up.

Run from the repo root after xfoil_wing.py and avl_wing.py (which read the as-designed params: half-fins 0.21 m,
pod 0.14 m wide, CG range 0.0509-0.0548 m) and after cfd2d_section.py (2-D RANS cross-check):
    python -I redesign/team/B2/sim/verify_wing.py           # ~10-15 min (AVL static-margin sweep, XFOIL panels)
Then sim_claims.py (claims) and plots_sim.py (figures).

What it adds to the R2 analysis:
  1. trimmed CLmax on a fine static-margin grid (SM 4.0-8.0 % by 0.25 %), so the stall claims can be read at the
     as-designed CG points expressed against B3's whole-aircraft NP (pod + props, CL-B3-XNP); the pod and props
     enter only through that NP shift (ASM-B2R3-SM-EQUIV)
  2. XFOIL panel convergence on the S5010 itself at the stall Re (R2 did it on the MH 45 at the cruise Re):
     160 / 220 / 300 / 400 panels
  3. AVL lattice convergence on 4 levels (R2 had 3) incl. the trimmed CLmax, not only CLa and Xnp
  4. clmax Reynolds-number slope, so the stall at the A3 predicted mass (lower Re) is corrected
  5. hand checks: Schrenk span loading and root bending; Helmbold lift slope; elevon hinge moment
Writes sim/params.json (P:b2sim.*) and sim/out/verify_results.json.
"""
from __future__ import annotations

import concurrent.futures as cf
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
B2 = HERE.parent
REDESIGN = B2.parents[1]
ARGS = sys.argv[1:]
sys.argv = [sys.argv[0]]                     # the imported drivers read sys.argv for --force


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


AW = load("avl_wing", B2 / "avl_wing.py")
XW = load("xfoil_wing", B2 / "xfoil_wing.py")
P = AW.P
A = json.loads((B2 / "out" / "avl_results.json").read_text())
X = json.loads((B2 / "out" / "xfoil_results.json").read_text())
FOIL = "s5010"
F = A["foils"][FOIL]
SM_GRID = [round(0.04 + 0.0025 * i, 4) for i in range(17)]      # 4.0 .. 8.0 %
LAT = ((6, 0.5), (8, 0.6), (12, 1.0), (16, 1.4))                 # (chordwise, spanwise scale): 4 levels


def sm_case(sm):
    xc = round(F["Xnp_m"] - sm * AW.CHORD, 5)
    r = AW.case(FOIL, F["eta"], f"r3_sm{sm*1e4:.0f}", xcg=xc, cm_t=F["cm_t"],
                cls=[0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 1.0])
    cs = AW.critical_section(r, FOIL, F["clmax_vs_flap"])
    return sm, xc, cs["CLmax_trim"], cs.get("elevator_deg"), cs.get("alpha_deg"), cs.get("y_first_stall"), \
        r["trim"]["0.50"]["elevator"]


def lattice_case(nc, ns):
    xc = A["x_cg_sm5_m"]
    r = AW.case(FOIL, F["eta"], f"r3_lat{nc}", nc=nc, ns=ns, xcg=xc, cm_t=F["cm_t"],
                cls=[0.5, 0.7, 0.75, 0.8, 0.85, 0.9])
    cs = AW.critical_section(r, FOIL, F["clmax_vs_flap"])
    return {"nc": nc, "ns": ns, "CLa": r["clean"]["a0"]["CLa"], "Xnp": r["clean"]["a0"]["Xnp"],
            "Cnb_a4": r["clean"]["a4"]["Cnb"], "CLmax_trim": cs["CLmax_trim"], "elev_cl0.5": r["trim"]["0.50"]["elevator"],
            "vortices": None}


def schrenk(b, c, n=400):
    """Schrenk loading of a rectangular wing: average of the planform (uniform) and the elliptic loading."""
    y = np.linspace(0, b / 2, n + 1)
    ell = 4 / (math.pi * b) * np.sqrt(np.clip(1 - (2 * y / b) ** 2, 0, None))   # integrates to 1 over the span
    rect = np.full_like(y, 1 / b)
    w = 0.5 * (ell + rect)                     # lift per unit span per unit total lift
    half = np.trapezoid(w, y)
    ybar = float(np.trapezoid(w * y, y) / half)
    return {"ybar_frac": ybar / (b / 2), "M_root_per_halflift_m": ybar}


def main():
    res = {"_note": "team/B2/sim/verify_wing.py output (B2-R3)", "xnp_props_off_m": F["Xnp_m"]}
    # 1. static-margin sweep (parallel AVL processes; each case has its own file tag)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        sm_rows = list(ex.map(sm_case, SM_GRID))
        lat = list(ex.map(lambda a: lattice_case(*a), LAT))
    res["clmax_vs_sm"] = [[r[0], r[2], r[3], r[5]] for r in sm_rows]
    res["sm_rows"] = [dict(zip(("sm", "x_cg_props_off", "CLmax_trim", "elev_at_clmax", "alpha_at_clmax", "y_first",
                                "elev_cl0.5"), r)) for r in sm_rows]
    res["lattice"] = lat
    for r in sm_rows:
        print(f"  SM {r[0]*100:5.2f} %  CLmax {r[2]:.4f}  elevon {r[3]:+.2f}  first {r[5]}")
    for r in lat:
        print(f"  lattice nc {r['nc']:2} ns {r['ns']}: CLa {r['CLa']:.4f} Xnp {r['Xnp']:.5f} CLmax {r['CLmax_trim']:.4f} Cnb {r['Cnb_a4']:.4f}")
    # 2. XFOIL panel convergence, S5010 at the stall Re (cached polars where they exist)
    pan = {}
    for n in (160, 220, 300, 400):
        tag, a = XW.polar(FOIL, X["re_stall"], 9.0, 0.0, n)
        s = XW.summarize(a)
        pan[n] = {"clmax": s.get("clmax"), "alpha_clmax": s.get("alpha_clmax"), "cm0": s.get("cm0"),
                  "cd_cl0.5": s.get("cd_at_cl", {}).get("0.50"), "cla": s.get("cla_per_rad"), "n_pts": s["n"]}
        print(f"  XFOIL {n} panels: clmax {pan[n]['clmax']}  cm0 {pan[n]['cm0']}  cd@0.5 {pan[n]['cd_cl0.5']}")
    res["xfoil_panels"] = pan
    # 3. clmax Reynolds slope (S5010, elevon neutral, Ncrit 9), 2.0..3.0e5
    re_pts = [(r, X["polars"][f"{FOIL}_re{r/1e5:.1f}e5_n9_f+0_p220"]["summary"]["clmax"]) for r in (2.0e5, 2.3e5, 2.6e5, 3.0e5)]
    k, c0 = np.polyfit([p[0] for p in re_pts], [p[1] for p in re_pts], 1)
    res["clmax_re"] = {"points": re_pts, "dclmax_dRe": float(k), "rel_per_1e5": float(k * 1e5 / np.interp(2.6e5, *zip(*re_pts)))}
    # 4. hand checks
    b, c = AW.SPAN, AW.CHORD
    ar = b * b / (b * c)
    a0 = X["polars"][f"{FOIL}_re{X['re_stall']/1e5:.1f}e5_n9_f+0_p220"]["summary"]["cla_per_rad"]
    k_ = a0 / (math.pi * ar)
    helm = a0 / (math.sqrt(1 + k_ * k_) + k_)                    # Helmbold low-AR lift slope
    res["hand"] = {"schrenk": schrenk(b, c), "helmbold_cla": helm, "a0_2d": a0, "AR": ar,
                   "elliptic_ybar_frac": 4 / (3 * math.pi)}
    L = json.loads((B2 / "out" / "loads_spanwise.json").read_text())
    res["avl_loads"] = {k: {"ybar_frac": v["ybar_frac_semispan"], "bend_root": v["bending_m_per_N"][0],
                            "torsion_root": v["torsion_m_per_N"][0], "elevator": v["elevator_deg"]}
                        for k, v in L["cases"].items()}
    res["derivs_a4"] = F["derivs_a4"]
    res["design_oswald"] = A["design_oswald"]
    res["helmbold_cla"] = helm
    (HERE / "out" / "verify_results.json").write_text(json.dumps(res, indent=1))
    write_params(res)


def xfoil_hinge_max(delta):
    """Largest |H/(q c^2)| of the XFOIL inviscid hinge cases at this deflection over alpha -4..8 deg."""
    d = X["hinge"][f"hm_{FOIL}_re{X['re_dive']/1e5:.1f}e5_f{delta:+g}_i"]
    return max(abs(x) for x in d["hmom_qc2"] if x == x)


def write_params(res):
    """sim/params.json (P:b2sim.*) from verify_results.json and cfd2d_results.json; --params re-writes it only."""
    def e(v, unit, src, note):
        return {"value": v, "unit": unit, "source": src, "status": "MODELLED", "note": note}
    sm_rows = [[r["sm"], r["x_cg_props_off"], r["CLmax_trim"], r["elev_at_clmax"]] for r in res["sm_rows"]]
    lat, pan, helm = res["lattice"], {int(k): v for k, v in res["xfoil_panels"].items()}, res["hand"]["helmbold_cla"]
    ar, a0 = res["hand"]["AR"], res["hand"]["a0_2d"]
    L = json.loads((B2 / "out" / "loads_spanwise.json").read_text())
    l1, l2, l3, l4 = lat
    ch10 = xfoil_hinge_max(-10.0), xfoil_hinge_max(-5.0)
    p = {"_note": "Written by team/B2/sim/verify_wing.py (B2-R3 verification round) from AVL / XFOIL re-runs on the "
                  "as-designed params (A1-R4: half-fins 0.21 m, pod 0.14 m, CG range 0.0509-0.0548 m) and by "
                  "cfd2d_section.py (SU2). Do not edit by hand.",
         "b2sim": {
             "avl": {
                 "clmax_vs_sm": e([[r[0], r[2]] for r in sm_rows], "-", "SRC-B2-AVL",
                                  "[static margin, trimmed CLmax], critical section, props-off NP of the wing + fins; "
                                  "SM 4-8 % by 0.25 %"),
                 "elev_vs_sm": e([[r[0], r[3]] for r in sm_rows], "deg", "SRC-B2-AVL",
                                 "[static margin, elevon at the trimmed CLmax]"),
                 "xnp_props_off_m": e(F["Xnp_m"], "m", "SRC-B2-AVL", "wing + 0.21 m half-fins, props off, no pod"),
                 "lattice_clmax": e([l1["CLmax_trim"], l2["CLmax_trim"], l3["CLmax_trim"], l4["CLmax_trim"]], "-",
                                    "SRC-B2-AVL", "trimmed CLmax at SM 5 %, lattice 6x0.5 / 8x0.6 / 12x1 / 16x1.4"),
                 "lattice_xnp": e([l1["Xnp"], l2["Xnp"], l3["Xnp"], l4["Xnp"]], "m", "SRC-B2-AVL", "same 4 levels"),
                 "cnb_a4": e(F["derivs_a4"]["Cnb"], "1/rad", "SRC-B2-AVL", "alpha 4 deg, ref CG target, props off"),
                 "ybar_frac": e(L["cases"]["CL0.80"]["ybar_frac_semispan"], "-", "SRC-B2-AVL",
                                "lift centroid / semispan, trimmed CL 0.8, SM 5 %"),
             },
             "xfoil": {
                 "panel_clmax": e([pan[n]["clmax"] for n in (160, 220, 300, 400)], "-", "SRC-B2-XFOIL",
                                  "S5010 clmax at the stall Re, 160/220/300/400 panels"),
                 "ch_inv_m10_max": e(ch10[0], "-", "SRC-B2-XFOIL", "max |H/(q c^2)|, inviscid, delta -10 deg, alpha -4..8"),
                 "ch_inv_m5_max": e(ch10[1], "-", "SRC-B2-XFOIL", "max |H/(q c^2)|, inviscid, delta -5 deg, alpha -4..8"),
                 "clmax_re_slope_per_1e5": e(res["clmax_re"]["rel_per_1e5"], "1/1e5", "SRC-B2-XFOIL",
                                             "relative clmax change per 1e5 of Re, S5010 Re 2.0-3.0e5 (linear fit)"),
             },
             "hand": {
                 "schrenk_ybar_frac": e(res["hand"]["schrenk"]["ybar_frac"], "-", "B2 hand calc",
                                        "Schrenk rectangular wing, lift centroid / semispan"),
                 "helmbold_cla": e(helm, "1/rad", "B2 hand calc", f"Helmbold, AR {ar:.2f}, a0 {a0:.2f} /rad (XFOIL)"),
             },
         }}
    trf = HERE / "out" / "xfoil_tripped.json"
    if trf.exists():
        T = json.loads(trf.read_text())
        p["b2sim"]["xfoil"]["clmax_tripped"] = e(T["clmax_tripped"], "-", "SRC-B2-XFOIL",
                                                 f"S5010, Re {T['re_stall']:.2g}, transition fixed at x/c {T['xtr']} both "
                                                 f"surfaces; last converged point (alpha {T['alpha_clmax_tripped']} deg), "
                                                 "so a lower bound on the fully turbulent clmax")
    cfdf = HERE / "out" / "cfd2d_results.json"
    if cfdf.exists():
        C = json.loads(cfdf.read_text())
        p["b2sim"]["cfd"] = cfd_params(C, e)
    (HERE / "params.json").write_text(json.dumps(p, indent=1))
    print("sim/params.json written")


def cfd_params(C, e):
    """SU2 results the claims read: clean clmax (L2 sweep + alpha 4 grid case), hinge coefficients, GCI."""
    cs = [c for c in C["cases"] if c["usable"]]
    clean = sorted([c for c in cs if c["delta"] == 0.0 and c["level"] == 2], key=lambda c: c["alpha"])
    out = {}
    if clean:
        i = int(np.argmax([c["CL"] for c in clean]))
        out["clmax_2d"] = e(clean[i]["CL"], "-", "SRC-B2-SU2",
                            f"S5010 SA fully turbulent, Re {C['re']['stall']:.2g}, L2 mesh, max over alpha "
                            f"{[c['alpha'] for c in clean]} (at {clean[i]['alpha']} deg)")
        out["alpha_clmax"] = e(clean[i]["alpha"], "deg", "SRC-B2-SU2", "alpha of the highest converged cl")
    allc = C["cases"]
    for dl, a, tag in ((-25.0, 0.0, "ch_m25_a0"), (-25.0, -4.0, "ch_m25_am4"), (25.0, 4.0, "ch_p25_a4"),
                       (C["d_vd_deg"], 2.0, "ch_p8_a2"), (-C["d_vd_deg"], 2.0, "ch_m8_a2")):
        # the hinge moment is read from every L2 case: it settles even where the lift still oscillates (separated
        # elevon); the note says whether the case met the lift-oscillation criterion
        r = [c for c in allc if c["delta"] == dl and c["alpha"] == a and c["level"] == 2]
        if r:
            out[tag] = e(r[0]["ch"], "-", "SRC-B2-SU2", f"H/(q c^2), delta {dl:+g} deg, alpha {a:g} deg, "
                                                        f"Re {r[0]['re']:.2g}, L2 mesh, pressure only, "
                                                        f"cl oscillation {r[0]['CL_osc_last200']:.3f} "
                                                        f"({'usable' if r[0]['usable'] else 'unsteady'})")
    g = C.get("gci", {}).get("f-25_a0_re4.4e5")
    if g:
        vals = [abs(g["ch"][k]) for k in ("L1", "L2", "L3")] + ([abs(g["ch"]["f_exact"])] if g["ch"].get("f_exact") else [])
        out["ch_m25_a0_bound"] = e(max(vals), "-", "SRC-B2-SU2",
                                   "largest |H/(q c^2)| at delta -25, alpha 0 over L1/L2/L3 and the Richardson "
                                   "extrapolation (p floored at 0.5): the SU2 upper estimate")
    for key, g in C.get("gci", {}).items():
        out[f"gci_{key}"] = e({q: {"L1": g[q]["L1"], "L2": g[q]["L2"], "L3": g[q]["L3"], "gci_fine": g[q]["gci_fine"],
                                   "p": g[q].get("p")} for q in ("CL", "CD", "CMz", "ch")},
                              "-", "SRC-B2-SU2", f"3-level grid study, cells {g['cells']}")
    return out


if __name__ == "__main__":
    if "--params" in sys.argv[1:] or "--params" in ARGS:
        write_params(json.loads((HERE / "out" / "verify_results.json").read_text()))
    else:
        main()
