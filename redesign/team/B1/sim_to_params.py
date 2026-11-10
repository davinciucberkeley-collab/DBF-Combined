"""Copy the B1 verification-run results into team/B1/params.json (keys b1sim.*), the file the proof chain reads.

Order: python -I redesign/team/B1/cfd_sections.py ; python -I redesign/team/B1/vlm_xfoil.py ;
       python -I redesign/team/B1/sim_to_params.py ; python -I redesign/team/B1/sim_verify.py
Do not edit params.json by hand. Fine-grid (L3 / 320-panel / finest-lattice) values are the ones used; the GCI or the
three-level spread is the numerical uncertainty that goes with each.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIM = HERE / "sim"


def ent(v, unit, src, note):
    return {"value": round(v, 6) if isinstance(v, float) else v, "unit": unit, "source": src, "note": note}


def main():
    cfd = json.loads((SIM / "cfd" / "cfd_results.json").read_text())
    vx = json.loads((SIM / "vlm_xfoil_results.json").read_text())
    C, G = cfd["cases"], cfd["gci"]
    cr, fit, conv = vx["cruise"], vx["fit_CDwing_A_plus_K_CL2"], vx["avl_convergence"]
    es = [conv[k]["e"] for k in ("L1", "L2", "L3")]
    pc = vx["xfoil_panel_convergence"]
    cds = [pc[k]["cd_at_cl"] for k in sorted(pc, key=int)]
    S_CFD, S_VX = "SRC-B1-SIM-CFD", "SRC-B1-SIM-VLMXF"
    out = {"_note": "Written by team/B1/sim_to_params.py from sim/cfd/cfd_results.json and sim/vlm_xfoil_results.json. "
                    "Do not edit by hand.",
           "b1sim": {
               "cfd": {
                   "fin_a_cd": ent(C["finA"]["L3"]["cd"], "-", S_CFD, "fin section through the motor tube (22 mm tube + 9.6 mm board, 3 mm fillet, square TE), SA, 16 m/s, on the 0.275 m fin chord, L3 grid"),
                   "fin_b_cd": ent(C["finB"]["L3"]["cd"], "-", S_CFD, "bare 9.6 mm board, square LE and TE, SA, on the fin chord, L3 grid"),
                   "fin_a_gci_pct": ent(G["finA"]["cd"]["gci_fine_pct"], "%", S_CFD, "Celik GCI, fine grid, Fs 1.25"),
                   "fin_b_gci_pct": ent(G["finB"]["cd"]["gci_fine_pct"], "%", S_CFD, "Celik GCI, fine grid, Fs 1.25"),
                   "s5010_cd_sa": ent(C["s5010"]["L3"]["cd"], "-", S_CFD, "S5010, alpha 2.5 deg, fully turbulent SA, L3"),
                   "s5010_cl_sa": ent(C["s5010"]["L3"]["cl"], "-", S_CFD, "S5010, alpha 2.5 deg, fully turbulent SA, L3"),
                   "s5010_gci_pct": ent(G["s5010"]["cd"]["gci_fine_pct"], "%", S_CFD, "Celik GCI on cd, fine grid"),
               },
               "xfoil": {
                   "cd_trip_a2p5": ent(vx["xfoil_trip_alpha2p5"]["cd"], "-", S_VX, "XFOIL S5010 alpha 2.5 deg, transition forced at 2 % c both sides (like-for-like with SU2 SA)"),
                   "cl_trip_a2p5": ent(vx["xfoil_trip_alpha2p5"]["cl"], "-", S_VX, "as cd_trip_a2p5"),
                   "cd_free_a2p5": ent(vx["xfoil_free_alpha2p5"]["cd"], "-", S_VX, "XFOIL S5010 alpha 2.5 deg, free transition Ncrit 9"),
                   "panel_spread_pct": ent(100 * (max(cds) - min(cds)) / cds[-1], "%", S_VX, "cd at cruise cl, 160/240/320 panels"),
               },
               "avl": {
                   "e_cruise": ent(cr["e"], "-", S_VX, "AVL span efficiency, trimmed at the as-designed cruise CL, A3 predicted CG, wing + fins, finest lattice is L3; this is L2 (medium)"),
                   "cdi_cruise": ent(cr["CDi"], "-", S_VX, "AVL trimmed induced drag at cruise CL (L2)"),
                   "cla_per_rad": ent(cr["CLa"], "1/rad", S_VX, "AVL trimmed lift slope (L2)"),
                   "xnp_m": ent(cr["Xnp"], "m", S_VX, "AVL neutral point, wing + fins, props off (L2)"),
                   "elevon_cruise_deg": ent(cr["elevon_deg"], "deg", S_VX, "trim elevon at cruise, + TE down"),
                   "alpha_cruise_deg": ent(cr["alpha_deg"], "deg", S_VX, "trimmed alpha at cruise"),
                   "lattice_spread_pct": ent(100 * (max(es) - min(es)) / es[-1], "%", S_VX, "spread of e over the 3 lattices"),
               },
               "wing": {
                   "cd0_fit": ent(fit["ncrit9"]["cd0_wing"], "-", S_VX, "CD_wing = A + K CL^2 fit, AVL CDi + XFOIL strip profile drag, Ncrit 9, CL 0.3-0.7, trimmed"),
                   "k_fit": ent(fit["ncrit9"]["k_wing"], "-", S_VX, "as cd0_fit"),
                   "cd0_fit_ncrit5": ent(fit["ncrit5"]["cd0_wing"], "-", S_VX, "as cd0_fit, Ncrit 5"),
                   "k_fit_ncrit5": ent(fit["ncrit5"]["k_wing"], "-", S_VX, "as cd0_fit, Ncrit 5"),
                   "cd0_fit_tripped": ent(fit["tripped"]["cd0_wing"], "-", S_VX, "as cd0_fit, transition forced at 2 % c (fully turbulent bound)"),
                   "k_fit_tripped": ent(fit["tripped"]["k_wing"], "-", S_VX, "as cd0_fit_tripped"),
                   "clmax_trim": ent(vx["clmax_trimmed"]["CLmax"], "-", S_VX, "critical-section trimmed CLmax at the A3 predicted CG, XFOIL clmax at the stall Re per strip and elevon deflection"),
                   "elevon_at_clmax_deg": ent(vx["clmax_trimmed"]["elevon_deg"], "deg", S_VX, "trim elevon at CLmax"),
               },
           }}
    (HERE / "params.json").write_text(json.dumps(out, indent=1) + "\n")
    print("team/B1/params.json written")


if __name__ == "__main__":
    main()
