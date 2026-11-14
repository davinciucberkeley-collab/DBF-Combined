"""C2 simulation-round claims: 3-D FEA of the as-designed wing (gmsh mesh, SU2 ELASTICITY + in-house PCG on the
same mesh). Values come from fea/params.json (P:c2fea.*), written by fea_report.py.

Run from the repo root after the solves and the report:
    python -I redesign/team/C2/fea/fea_report.py
    python -I redesign/team/C2/fea/fea_claims.py
    python -I redesign/proofs/build_graph.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../../params/params.json", "../params.json", "params.json"])
P = "P:"
I = P + "c2.inputs."
F = P + "c2fea."
WING = ["WNG-001", "WNG-002", "WNG-003"]
SM = ["R-STRUCT-MARGIN"]

kit.source("SRC-C2-CELIK-GCI", "Celik et al., Procedure for estimation and reporting of uncertainty due to "
           "discretization in CFD applications, J. Fluids Eng. 130 (2008) 078001", "paper",
           url="https://doi.org/10.1115/1.2960953", where="three-grid GCI, Fs = 1.25, iterative order p for non-constant r")
kit.assumption("ASM-C2-FEA-GCI-TOL", "FEA discretisation uncertainty limit 5 %",
               "GCI (fine grid) of a governing FEA output that a decision rests on", value=0.05, unit="-",
               cites=["SRC-C2-CELIK-GCI"],
               basis="material values are uncertain by +-30 %; 5 % numerical uncertainty is small against that")
kit.assumption("ASM-C2-FEA-VALID-TOL", "FEA element check vs beam theory 5 %",
               "Tube cantilever (spar alone) tip deflection and twist vs Timoshenko / GJ theory, level-2 mesh",
               value=0.05, unit="-",
               basis="linear hexahedra, 3 elements through the 1 mm wall: a few % stiff in bending, converging")


kit.assumption("ASM-C2-TUBE-ET", "CF tube transverse properties for the 3-D FEA",
               "Roll-wrapped tube as transversely isotropic about its axis: E axial 70 GPa, E hoop = E radial 8 GPa, "
               "G axial 3 GPa, nu 0.30 / 0.40", value=8.0e9, unit="Pa", status="UNVERIFIED",
               basis="UD carbon-epoxy transverse modulus 7-10 GPa; woven outer plies raise the hoop value; only the "
                     "local ring deformation under the block and anchors depends on it")


def passthrough(cid, title, ref, eq="value from fea_report.py (3-D FEA)", assumes=()):
    def _f(v):
        return v
    _f.__name__ = _f.__qualname__ = "pt_" + cid.replace("-", "_").lower()
    globals()[_f.__name__] = _f
    return kit.calc(cid, title=title, equation=eq, inputs={"v": ref}, assumes=assumes)(_f)


@kit.calc("CALC-C2-FEA-GCI", title="Largest fine-grid GCI over the governing FEA outputs",
          equation="max GCI over: w_G2 (B, O), u_L1 (B), twist_L4 (T, O), sigma_spar_L1 (B), foam tension and shear "
                   "99.5th pct L4 (O)",
          inputs={"a": F + "w_tip_G2_gci", "b": F + "u_tip_L1_gci", "c": F + "twist_tip_L4_gci",
                  "d": F + "spar_sigma_L1_gci", "e": F + "w_tip_G2_O_gci", "f": F + "twist_tip_L4_O_gci",
                  "g": F + "foam_s1_L4_O_gci", "h": F + "foam_tau_L4_O_gci"}, cites=["SRC-C2-CELIK-GCI"])
def fea_gci(a, b, c, d, e, f, g, h):
    return max(a, b, c, d, e, f, g, h)


@kit.calc("CALC-C2-FEA-TUBE", title="Tube cantilever check, worst of deflection and twist error",
          equation="max(|w_FE / w_beam - 1|, |theta_FE / theta_GJ - 1|)",
          inputs={"a": F + "tube_valid_w_err", "b": F + "tube_valid_twist_err"})
def fea_tube(a, b):
    return max(a, b)


passthrough("CALC-C2-FEA-SU2", "SU2 ELASTICITY vs in-house PCG, same level-1 mesh and loads", F + "su2_vs_pcg_rel")
passthrough("CALC-C2-FEA-SPAR", "Spar outer-fibre stress from the 3-D FEA, ultimate, worst case", F + "spar_sigma_ult_pa", assumes=["ASM-C2-TUBE-ET"])
passthrough("CALC-C2-FEA-DEFL", "Tip flap deflection / semi-span from the 3-D FEA (extrapolated, tape 0 %)",
            F + "tip_defl_frac")
passthrough("CALC-C2-FEA-FOAM-S1", "Foam max principal stress (99.5th percentile), ultimate", F + "foam_s1_p995_ult_pa", assumes=["ASM-C2-TUBE-ET"])
passthrough("CALC-C2-FEA-FOAM-TAU", "Foam max shear stress (99.5th percentile), ultimate", F + "foam_tau_p995_ult_pa", assumes=["ASM-C2-TUBE-ET"])
passthrough("CALC-C2-FEA-PETG", "PETG block / anchor von Mises peak, ultimate", F + "petg_vm_peak_ult_pa", assumes=["ASM-C2-TUBE-ET"])
# C2-R3: the corner claims are on the D-68 geometry (R 3 mm block / pocket edges + 3 mm microballoon fillet beads),
# from the global-local submodel (wing_fea_d68.py); the R2 as-drawn values stay in out/fea_report.json for the record.
kit.source("SRC-C2-TAYLOR-TCD", "D. Taylor, The Theory of Critical Distances: a new perspective in fracture mechanics, "
           "Elsevier 2007", "book", where="ch. 2-3: stress averaged over a material length L (line / volume method) "
                                          "predicts failure at notches; L of the order of a few cells in foams")
kit.assumption("ASM-C2-FOAM-AVG-R", "Foam peak stresses read as the average over a 1 mm sphere",
               "Element stresses at a bonded corner are averaged over a sphere of radius 1 mm round the peak element "
               "before comparing with the coupon allowable", value=0.001, unit="m", status="UNVERIFIED",
               cites=["SRC-C2-TAYLOR-TCD"],
               basis="XPS cells are 0.1-0.3 mm; a continuum stress below a few cells is not what the coupon allowable "
                     "measures. 1 mm is below every TCD length estimated for PS foams (several mm), so the average is "
                     "conservative; the element peak is reported beside it")
kit.assumption("ASM-C2-BEAD", "Microballoon fillet bead: E 1.5 GPa, tension allowable 10 MPa",
               "30-min epoxy thickened 1:1 by volume with glass microballoons (the slot bond mix, sizing.json)",
               value=10e6, unit="Pa", status="UNVERIFIED",
               basis="thickened epoxies of density 0.6-0.8 g/cm3: E 1-3 GPa, tensile strength 15-25 MPa; 10 MPa "
                     "allows for voids in a hand-laid bead; T-C2-XPS-COUPON adds a beaded pocket coupon")
passthrough("CALC-C2-FEA-CORNER-S1", "Foam tension peak at the R 3 mm block-pocket corners with fillet beads, ultimate "
            "(D-68, submodel finest level)", F + "d68_corner_s1_ult_pa", assumes=["ASM-C2-TUBE-ET", "ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-CORNER-S3", "Foam compression peak at the same corners, ultimate (D-68)",
            F + "d68_corner_s3_ult_pa", assumes=["ASM-C2-TUBE-ET", "ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-CORNER-TAU", "Foam shear peak at the same corners, ultimate (D-68)",
            F + "d68_corner_tau_ult_pa", assumes=["ASM-C2-TUBE-ET", "ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-CORNER-S1-CUTS", "Foam tension peak at the pocket corners with the ESC-lead grooves and the "
            "spar-slot cap seams run open (d68g), ultimate", F + "d68g_corner_s1_ult_pa", assumes=["ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-CORNER-S3-CUTS", "Foam compression peak, same (d68g), ultimate", F + "d68g_corner_s3_ult_pa",
            assumes=["ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-CUTS-RATIO", "Corner tension with the grooves and open seams / without, same local level",
            F + "d68g_over_d68_s1")
passthrough("CALC-C2-FEA-CORNER-S1-G431", "Foam tension peak at the pocket corners with the tube at G 4.31 GPa, ultimate",
            F + "d68_g431_corner_s1_ult_pa", assumes=["ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-CORNER-S3-G431", "Foam compression peak, same, tube at G 4.31 GPa, ultimate",
            F + "d68_g431_corner_s3_ult_pa", assumes=["ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-BEAD", "Microballoon bead max principal stress, ultimate (D-68)", F + "d68_bead_s1_ult_pa",
            assumes=["ASM-C2-BEAD"])
passthrough("CALC-C2-FEA-CUTOUT", "Foam shear peak at the R 3 mm elevon cut-out corners, primary load path, ultimate",
            F + "d68_cutout_tau_ult_pa", assumes=["ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-CUTOUT-SENS", "Foam shear peak at the R 3 mm elevon cut-out corners if the fin root fillet "
            "carries the station loads (sensitivity), ultimate", F + "d68_cutout_tau_dist_ult_pa", assumes=["ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-SUB-GCI", "Submodel discretisation uncertainty, pocket-corner foam peaks (3 local levels)",
            F + "d68_corner_gci", eq="max GCI (Celik 2008) of the corner tension, compression and shear peaks")
passthrough("CALC-C2-FEA-SUB-CUT", "Submodel cut-plane check: corner peaks with the cut planes 10 mm closer",
            F + "d68_cut_sens", eq="max |peak(0.28/0.36) / peak(0.27/0.37) - 1|")
passthrough("CALC-C2-FEA-FILLET-SENS", "Foam shear (99.5th percentile), ultimate, if the fin root fillet carries the "
            "station loads into the core along the chord (sensitivity)", F + "sens_foam_tau_p995_ult_pa")
passthrough("CALC-C2-FEA-W-RATIO", "FEA / beam model tip deflection, G2 (both tape 0 %)", F + "fea_beam_w_ratio_G2")
passthrough("CALC-C2-FEA-TW-RATIO", "FEA / beam model tip twist, L4 (both tape 0 %)", F + "fea_beam_twist_ratio_L4")

_claim = kit.claim


def claim(*a, **k):
    k.setdefault("output", "value")
    return _claim(*a, **k)


kit.claim = claim
HOW = "Re-run fea/wing_fea_direct.py (3 levels), fea/fea_report.py; out/fea_report.json"
kit.claim("CL-C2-FEA-GCI", "3-D FEA: largest fine-grid GCI on the governing outputs (3 levels)", calc="CALC-C2-FEA-GCI",
          unit="-", limit=("<=", "ASM-C2-FEA-GCI-TOL"), how=HOW + "#convergence")
kit.claim("CL-C2-FEA-TUBE-VALID", "3-D FEA element check: spar tube cantilever vs beam theory", calc="CALC-C2-FEA-TUBE",
          unit="-", limit=("<=", "ASM-C2-FEA-VALID-TOL"), how="fea/wing_fea_direct.py tube_validation(); SU2 gives the same")
kit.claim("CL-C2-FEA-SU2-AGREE", "SU2 ELASTICITY vs in-house PCG on the same mesh: largest tip difference",
          calc="CALC-C2-FEA-SU2", unit="-", limit=("<=", "ASM-C2-FE-TOL"),
          how="python -I redesign/team/C2/fea/wing_fea.py --levels 1; compare out/su2_*_L1.json with blk_L1*.json")
kit.claim("CL-C2-FEA-SPAR-SIGMA-ULT", "Spar stress from the 3-D FEA (foam shares the load), ultimate", calc="CALC-C2-FEA-SPAR",
          unit="Pa", limit=("<=", I + "spar_sigma_allow_pa"), verifies=SM, parts=["WNG-002"],
          how="T-C1-WING-PROOF; the hand calc CL-C2-SPAR-SIGMA-ULT (spar alone) bounds it from above")
kit.claim("CL-C2-FEA-TIP-DEFL-FRAC", "Tip deflection / semi-span from the 3-D FEA, worst case, E 70 GPa, no tape",
          calc="CALC-C2-FEA-DEFL", unit="-", limit=("<=", P + "requirements.spar_deflection_max"), verifies=SM, parts=WING,
          how="T-C1-WING-PROOF: ruler at the tip under the G2 load")
kit.claim("CL-C2-FEA-FOAM-S1", "Core foam tension (99.5th percentile element), ultimate, station loads on the hard points",
          calc="CALC-C2-FEA-FOAM-S1", unit="Pa", limit=("<=", I + "xps_tens_allow_pa"), verifies=SM, parts=["WNG-001"],
          how="T-C2-XPS-COUPON (allowable) and T-C1-WING-PROOF (no crack at the elevon cut-out corners)")
kit.claim("CL-C2-FEA-FOAM-TAU", "Core foam shear (99.5th percentile element), ultimate, station loads on the hard points",
          calc="CALC-C2-FEA-FOAM-TAU", unit="Pa", limit=("<=", I + "xps_shear_allow_pa"), verifies=SM, parts=["WNG-001"],
          how="T-C2-XPS-COUPON and T-C1-WING-PROOF")
kit.claim("CL-C2-FEA-PETG", "PETG block and anchor von Mises peak, ultimate", calc="CALC-C2-FEA-PETG", unit="Pa",
          limit=("<=", I + "petg_bearing_allow_pa"), verifies=SM, parts=["FIN-004-L", "FIN-004-R", "WNG-004-L", "WNG-004-R", "WNG-005-L", "WNG-005-R"],
          how="T-C4-BLOCK-PROOF (C4)")
PROOF = ("T-C1-WING-PROOF (GT-08) steps 1-2 and T-C1-STATION-PROOF; inspect the four block-pocket corners and beads "
         "with a light after each step (no crack, no bead debond)")
kit.claim("CL-C2-FEA-FOAM-CORNER-S1", "Core foam tension peak at the R 3 mm block-pocket corners with fillet beads, "
          "ultimate (D-68)", calc="CALC-C2-FEA-CORNER-S1", unit="Pa", limit=("<=", I + "xps_tens_allow_pa"), verifies=SM,
          parts=["WNG-001", "FIN-004-L", "FIN-004-R"], how=PROOF + "; D1 builds the pocket to D-68")
kit.claim("CL-C2-FEA-FOAM-CORNER-S3", "Core foam compression peak at the same corners, ultimate (D-68)",
          calc="CALC-C2-FEA-CORNER-S3", unit="Pa", limit=("<=", I + "xps_comp_allow_pa"), verifies=SM,
          parts=["WNG-001", "FIN-004-L", "FIN-004-R"], how=PROOF)
kit.claim("CL-C2-FEA-FOAM-CORNER-TAU", "Core foam shear peak at the same corners, ultimate (D-68)",
          calc="CALC-C2-FEA-CORNER-TAU", unit="Pa", limit=("<=", I + "xps_shear_allow_pa"), verifies=SM,
          parts=["WNG-001", "FIN-004-L", "FIN-004-R"], how=PROOF)
kit.claim("CL-C2-FEA-FOAM-CORNER-S1-CUTS", "Core foam tension peak at the pocket corners with the ESC-lead grooves and "
          "open slot seams (SW-05), ultimate", calc="CALC-C2-FEA-CORNER-S1-CUTS", unit="Pa",
          limit=("<=", I + "xps_tens_allow_pa"), verifies=SM, parts=["WNG-001", "FIN-004-L", "FIN-004-R"],
          note="C2-R4 (CDR-13): grooves at x 54-64 mm to |y| 0.296 on both surfaces and both cap seams removed as "
               "open slits in the local model (the bound opposite to the bonded seam of CL-C2-FEA-FOAM-CORNER-S1)",
          how=PROOF)
kit.claim("CL-C2-FEA-FOAM-CORNER-S3-CUTS", "Core foam compression peak, same corners with the cuts, ultimate",
          calc="CALC-C2-FEA-CORNER-S3-CUTS", unit="Pa", limit=("<=", I + "xps_comp_allow_pa"), verifies=SM,
          parts=["WNG-001", "FIN-004-L", "FIN-004-R"], how=PROOF)
kit.claim("CL-C2-FEA-CUTS-RATIO", "Pocket-corner tension with the grooves and open seams / without (record)",
          calc="CALC-C2-FEA-CUTS-RATIO", unit="-", parts=["WNG-001"],
          note="record: close to 1 means the grooves and seams are not what loads the corner, so stopping the "
               "grooves short (the CDR-13 fallback) does not fix it",
          how="python -I redesign/team/C2/fea/wing_fea_d68.py --phase local --job d68g/3")
kit.claim("CL-C2-FEA-FOAM-CORNER-S1-G431", "Core foam tension peak at the pocket corners if the tube meets the GT-16 "
          "shear-modulus line (G 4.31 GPa, not the 3 GPa low corner), ultimate (record)",
          calc="CALC-C2-FEA-CORNER-S1-G431", unit="Pa", parts=["WNG-001"],
          note="record, no limit: sensitivity. The corner stress follows the twist of the spar under the L4 fin-joint "
               "torque; the tape skin, which also resists that twist, is not in the model",
          how="T-C4-TUBE-TORSION (GT-16) gives G; re-run with C2_TUBE_G set to the measured value")
kit.claim("CL-C2-FEA-FOAM-CORNER-S3-G431", "Core foam compression peak, same, tube at G 4.31 GPa (record)",
          calc="CALC-C2-FEA-CORNER-S3-G431", unit="Pa", parts=["WNG-001"], how="As CL-C2-FEA-FOAM-CORNER-S1-G431.")
kit.claim("CL-C2-FEA-BEAD", "Microballoon fillet bead along the pocket edges, max principal stress, ultimate",
          calc="CALC-C2-FEA-BEAD", unit="Pa", limit=("<=", "ASM-C2-BEAD"), verifies=SM, parts=["WNG-001"],
          how="T-C2-XPS-COUPON beaded-pocket coupon; " + PROOF)
kit.claim("CL-C2-FEA-CUTOUT-TAU", "Foam shear peak at the R 3 mm elevon cut-out corners (fin-root tab), primary path, "
          "ultimate", calc="CALC-C2-FEA-CUTOUT", unit="Pa", limit=("<=", I + "xps_shear_allow_pa"), verifies=SM,
          parts=["WNG-001"], how=PROOF.replace("block-pocket corners and beads", "elevon cut-out corners"))
kit.claim("CL-C2-FEA-CUTOUT-SENS", "Foam shear peak at the R 3 mm elevon cut-out corners if the fin root fillet carries "
          "the station loads (sensitivity)", calc="CALC-C2-FEA-CUTOUT-SENS", unit="Pa",
          limit=("<=", I + "xps_shear_allow_pa"), parts=["WNG-001", "FIN-001-UR", "FIN-001-LR"],
          how="Bounds the fillet-intact case at the corners only; the tab as a whole is CL-C2-FEA-FOAM-FILLET-SENS (C4 "
              "fillet share, CR-C2-12)")
kit.claim("CL-C2-FEA-SUB-GCI", "D-68 submodel: GCI of the pocket-corner foam peaks (3 local levels)",
          calc="CALC-C2-FEA-SUB-GCI", unit="-", limit=("<=", "ASM-C2-FEA-GCI-TOL"), cites=["SRC-C2-CELIK-GCI"],
          how="python -I redesign/team/C2/fea/wing_fea_d68.py; fea_report.py; out/fea_report.json#d68")
kit.claim("CL-C2-FEA-SUB-CUT", "D-68 submodel: corner peaks change with the cut planes 10 mm closer",
          calc="CALC-C2-FEA-SUB-CUT", unit="-", limit=("<=", "ASM-C2-FEA-GCI-TOL"),
          how="out/fea_report.json#d68.cut_check")
kit.claim("CL-C2-FEA-FOAM-FILLET-SENS", "Core foam shear if the fin root fillet carries the station loads (sensitivity)",
          calc="CALC-C2-FEA-FILLET-SENS", unit="Pa", limit=("<=", I + "xps_shear_allow_pa"), parts=["WNG-001", "FIN-001-UR", "FIN-001-UL", "FIN-001-LR", "FIN-001-LL"],
          how="Shows the fin-root tab aft of the hinge cannot take the fin loads (expected FAIL); C4 keeps the fillet "
              "fail-safe (CR-C2-12); T-C1-WING-PROOF inspects the tab")
kit.claim("CL-C2-FEA-W-RATIO", "3-D FEA / beam model, tip deflection (G2, no tape)", calc="CALC-C2-FEA-W-RATIO", unit="-",
          how="Shows the beam model (all deflection, mode and aeroelastic claims) is within a few % of the 3-D model")
kit.claim("CL-C2-FEA-TW-RATIO", "3-D FEA / beam model, tip twist (L4, no tape)", calc="CALC-C2-FEA-TW-RATIO", unit="-",
          how="As above, for twist (GJ): the input of every aeroelastic claim")

if __name__ == "__main__":
    kit.write()
