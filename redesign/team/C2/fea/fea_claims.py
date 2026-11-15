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

kit = pk.Kit(__file__, params=["../../../params/params.json", "../params.json", "params.json", "c2r5_reduced.json"])
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
                   "99.5th pct by volume L4 (O; closure round: volume-weighted percentile)",
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
# D-153 (design round 2026-11-14, C2 wave 2): the block-pocket corner claims use the critical-distance measure vm(L/2)
# on the decided model (WNG-003 tape skin + 2-layer block doubler at 50 % credit), from the small committed reduction
# c2r5_reduced.json (P:c2r5.*, written by c2r5_reduce.py). The 25 % credit case is the sensitivity; the untaped base
# stays as information rows so the coupon outcome (T-C2-XPS-COUPON) is traceable. The D-68 1 mm-average values stay
# in out/fea_report.json (P:c2fea.d68_corner_*) for the record.
R5 = P + "c2r5."
SFU = P + "requirements.safety_factor_ult"
kit.source("SRC-C2-XPS-KIC", "XPS fracture parameters from notched beams: K_Ice 0.0547 MPa m^0.5 (CoV 16.7 %, n = 3), "
           "E 10.7 MPa, Key Eng. Mater. 776:160", "paper", url="https://www.scientific.net/KEM.776.160",
           where="abstract via search 2026-11-14 (page returns 403 to fetch)")
kit.source("SRC-C2-FOAMULAR250", "Owens Corning FOAMULAR 250 data sheet: flexural strength 75 psi minimum (ASTM C203)",
           "datasheet", url="https://www2.owenscorning.com/comminsul/documents/foamular250.pdf",
           where="search snippet 2026-11-14")
kit.source("SRC-C2-NEGRU-TCD", "Negru R. et al., Application of TCD for brittle fracture of notched PUR materials, "
           "Theor. Appl. Fract. Mech. 80 (2015) 87-95", "paper", url="https://imechanica.egr.uh.edu/node/25514",
           where="TCD applied to notched polymer foams (checked 2026-11-14)")
kit.assumption("ASM-C2-FOAM-TCD", "Block-pocket corner foam stress read as vm(L/2), L = (1/pi)(K_Ic/sigma_0)^2 (D-153)",
               "Foam-only volume average over a ball of radius L/2 = 1.78 mm, maximised over the ball centre (the 3000 "
               "highest foam elements tried as centres), compared with the unchanged allowables", value=0.00178,
               unit="m", status="UNVERIFIED", cites=["SRC-C2-TAYLOR-TCD", "SRC-C2-NEGRU-TCD", "SRC-C2-XPS-KIC",
                                                       "SRC-C2-FOAMULAR250"],
               basis="the corner is a bimaterial singularity (Williams exponents 0.255 / 0.30, c2r5_wedge.py), so any "
                     "peak or fixed sub-L average grows with refinement; for those exponents the ball average reads "
                     "the point-method stress at about 0.35 L, more conservative than the point (0.5 L) and line "
                     "methods; sigma_0 is the highest strength on record (shortest L). The basis is mode-I cracks in "
                     "homogeneous foam; T-C2-XPS-COUPON (taped and untaped torsion coupons, 3 SENB beams) checks it")
kit.assumption("ASM-C2-TAPE-CREDIT", "WNG-003 tape skin and block doubler carried at 50 % membrane credit (D-153)",
               "BOPP packing-tape skin as a 0.35 mm offset layer with E t 0.044 MN/m (1 layer at 50 %) for x <= 0.24 m, "
               "3x over the block doubler band y 0.29-0.35, x <= 0.12 m; 25 % (E t 0.022 MN/m) is the reported "
               "sensitivity", value=0.5, unit="-", status="UNVERIFIED",
               basis="50 % is the credit the beam design basis already uses for the tape (team/C2/sizing.json); the "
                     "PSA shear-lag length on foam is about 2-5 mm EST, so the credit is decided by T-C2-XPS-COUPON "
                     "(taped vs untaped block coupon); fallback if it fails: glass D-cell (A1.md D-153)")
TCD = ["ASM-C2-TUBE-ET", "ASM-C2-FOAM-TCD", "ASM-C2-TAPE-CREDIT"]


@kit.calc("CALC-C2-TCD-HALF-L", title="Critical-distance half-length L/2 for XPS",
          equation="L/2 = (1/(2 pi)) (K_Ic / sigma_0)^2",
          inputs={"k": R5 + "tcd_K_Ic_pa_sqrtm", "s0": R5 + "tcd_sigma0_pa"},
          cites=["SRC-C2-TAYLOR-TCD", "SRC-C2-XPS-KIC", "SRC-C2-FOAMULAR250"])
def tcd_half_l(k, s0):
    import math
    return (k / s0) ** 2 / math.pi / 2


def ultc(cid, title, key, assumes=TCD):
    """Ultimate = SF x the limit-load vm(L/2) value stored in c2r5_reduced.json."""
    def _f(v, sf):
        return sf * v
    _f.__name__ = _f.__qualname__ = "ult_" + cid.replace("-", "_").lower()
    globals()[_f.__name__] = _f
    return kit.calc(cid, title=title, equation="sigma_ult = SF_ult x vm(L/2) at limit (c2r5_reduced.json)",
                    inputs={"v": R5 + key, "sf": SFU}, assumes=assumes)(_f)


for _k, _n in (("s1", "tension"), ("s3", "compression"), ("tau", "shear")):
    _K = _k.upper()
    ultc(f"CALC-C2-FEA-CORNER-{_K}", f"Foam {_n} vm(L/2) at the block-pocket corners, tape skin + doubler at 50 %, "
         "ultimate (D-153, local level 2)", f"tape50_L2_vm_{_k}_lim_pa")
    ultc(f"CALC-C2-FEA-CORNER-{_K}-T25", f"Foam {_n} vm(L/2) at the corners, tape at 25 % credit, ultimate "
         "(sensitivity, level 2)", f"tape25_L2_vm_{_k}_lim_pa")
    ultc(f"CALC-C2-FEA-CORNER-{_K}-BASE", f"Foam {_n} vm(L/2) at the corners with no skin (untaped base, the "
         "coupon control), ultimate, level 3", f"base_L3_vm_{_k}_lim_pa", assumes=["ASM-C2-TUBE-ET", "ASM-C2-FOAM-TCD"])
    ultc(f"CALC-C2-FEA-SERVO-{_K}", f"Foam {_n} vm(L/2) round the lower-skin servo-pocket opening, tape at 50 %, "
         "ultimate (level 2)", f"tape50_L2_servo_vm_{_k}_lim_pa")
ultc("CALC-C2-FEA-CORNER-S1-CUTS", "Foam tension vm(L/2) at the corners with the ESC-lead grooves and open slot seams "
     "(d68g), tape at 50 %, ultimate", "tape50g_L2_vm_s1_lim_pa")
ultc("CALC-C2-FEA-CORNER-S3-CUTS", "Foam compression vm(L/2), same (d68g), ultimate", "tape50g_L2_vm_s3_lim_pa")
ultc("CALC-C2-FEA-CORNER-S1-G431", "Foam tension vm(L/2) at the corners, tube at G 4.31 GPa, tape at 50 %, ultimate",
     "tape50g431_L2_vm_s1_lim_pa")
ultc("CALC-C2-FEA-CORNER-S3-G431", "Foam compression vm(L/2), same, tube at G 4.31 GPa, ultimate",
     "tape50g431_L2_vm_s3_lim_pa")


@kit.calc("CALC-C2-FEA-CUTS-RATIO", title="Corner tension vm(L/2) with the grooves and open seams / without "
          "(tape model, level 2)", equation="vm_s1(d68g) / vm_s1(d68)",
          inputs={"a": R5 + "tape50g_L2_vm_s1_lim_pa", "b": R5 + "tape50_L2_vm_s1_lim_pa"})
def cuts_ratio(a, b):
    return a / b


@kit.calc("CALC-C2-FEA-BEAD", title="Microballoon bead max principal stress, ultimate, worst of the untaped D-68 "
          "model and the tape models", equation="max(d68 finest level, SF x tape 50 % L2, SF x tape 25 % L2)",
          inputs={"d68": F + "d68_bead_s1_ult_pa", "t50": R5 + "tape50_L2_bead_s1_lim_pa",
                  "t25": R5 + "tape25_L2_bead_s1_lim_pa", "sf": SFU}, assumes=["ASM-C2-BEAD"])
def bead_worst(d68, t50, t25, sf):
    return max(d68, sf * t50, sf * t25)
passthrough("CALC-C2-FEA-CUTOUT", "Foam shear peak at the R 3 mm elevon cut-out corners, primary load path, ultimate",
            F + "d68_cutout_tau_ult_pa", assumes=["ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-CUTOUT-SENS", "Foam shear peak at the R 3 mm elevon cut-out corners if the fin root fillet "
            "carries the station loads (sensitivity), ultimate", F + "d68_cutout_tau_dist_ult_pa", assumes=["ASM-C2-FOAM-AVG-R"])
def _gci3(f1, f2, f3, h1, h2, h3):
    """Celik et al. (2008) fine-grid GCI, Fs 1.25; 1 = fine. Observed order p by bisection on (0.05, 20)."""
    import math
    r21, r32 = h2 / h1, h3 / h2
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0:
        return 0.0
    sgn = math.copysign(1, e32 / e21)

    def g(p):
        return p - abs(math.log(abs(e32 / e21)) + math.log((r21 ** p - sgn) / (r32 ** p - sgn))) / math.log(r21)
    lo, hi = 0.05, 20.0
    if g(lo) * g(hi) > 0:
        return float("inf")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if g(lo) * g(mid) <= 0:
            hi = mid
        else:
            lo = mid
    p = 0.5 * (lo + hi)
    return 1.25 * abs((f1 - f2) / f1) / (r21 ** p - 1)


_GIN = {f"{k}{l}": R5 + f"base_L{l}_vm_{k}_lim_pa" for k in ("s1", "s3", "tau") for l in (1, 2, 3)}
_GIN.update({f"h{l}": R5 + f"base_L{l}_h_m" for l in (1, 2, 3)})


@kit.calc("CALC-C2-FEA-SUB-GCI", title="Corner measure vm(L/2): fine-grid GCI over three local levels (untaped D-68 "
          "geometry)", equation="max over s1, s3, tau of GCI_fine (Celik 2008, Fs 1.25) of vm(L/2), levels 1-3",
          inputs=_GIN, cites=["SRC-C2-CELIK-GCI"], assumes=["ASM-C2-FOAM-TCD"])
def sub_gci(s11, s12, s13, s31, s32, s33, tau1, tau2, tau3, h1, h2, h3):
    return max(_gci3(a3, a2, a1, h3, h2, h1) for a1, a2, a3 in ((s11, s12, s13), (s31, s32, s33), (tau1, tau2, tau3)))


@kit.calc("CALC-C2-FEA-SUB-TAPE-L1L2", title="Decided tape model: largest change of vm(L/2) from local level 1 to 2",
          equation="max over s1, s3, tau of |vm(L2) / vm(L1) - 1|, tape 50 %",
          inputs={f"{k}{l}": R5 + f"tape50_L{l}_vm_{k}_lim_pa" for k in ("s1", "s3", "tau") for l in (1, 2)})
def sub_tape_l1l2(s11, s12, s31, s32, tau1, tau2):
    return max(abs(b / a - 1) for a, b in ((s11, s12), (s31, s32), (tau1, tau2)))
passthrough("CALC-C2-FEA-SUB-CUT", "Submodel cut-plane check: corner peaks with the cut planes 10 mm closer",
            F + "d68_cut_sens", eq="max |peak(0.28/0.36) / peak(0.27/0.37) - 1|")
passthrough("CALC-C2-FEA-FILLET-SENS", "Foam shear (99.5th percentile), ultimate, if the fin root fillet carries the "
            "station loads into the core along the chord (sensitivity)", F + "sens_foam_tau_p995_ult_pa")
kit.source("SRC-C2-PTFE-TAPE", "Uline S-14538 PTFE film tape, 1 in x 36 yd, 3.5 mil, silicone adhesive", "web",
           url="https://www.uline.com/Product/Detail/S-14538/Specialty-Tape/Uline-PTFE-Film-Tape-1-x-36-yds",
           checked="2026-11-14", where="USD 60 per roll (1 roll); 1 in wide, 3.5 mil, silicone adhesive")
kit.assumption("ASM-C2-FILLET-BREAK", "Fin root bond break from x 0.22 to the TE (design, closure round)",
               "From x 0.22 (30 mm ahead of the elevon hinge, 10 R ahead of the cut-out corners) to the TE, under "
               "each half-fin root (4 places), two overlapping 25.4 mm "
               "strips of PTFE film tape (about 45 mm wide, centred on the fin plane) are laid on the wing skin before "
               "the root bond; the root edge, its "
               "13 mm coves and the fin's 15 mm skin-tape laps sit on it and bond to the fin only. Ahead of the "
               "hinge the root, coves and laps bond as drawn",
               value=0.22, unit="m", status="PROPOSED", cites=["SRC-C2-PTFE-TAPE"],
               basis="epoxy and packing-tape adhesive do not bond to PTFE (a release surface); 45 mm covers the two "
                     "13 mm cove legs, the root edge and 8 mm of margin each side, so no epoxy or lap reaches the wing "
                     "skin aft of x 0.22. Mass about 4.9 g for the four roots (EST: 3.5 mil PTFE + silicone "
                     "adhesive, about 0.24 kg/m2, 8 strips x 100 x 25.4 mm). The break sits 30 mm ahead of the hinge "
                     "because a bonded root ending at the hinge line loads the cut-out corners (closure-round runs: "
                     "corner compression 118.7 kPa vs 120 at local level 2, rising with refinement; 75.9 with the "
                     "break at 0.22)")
kit.assumption("ASM-C2-FILLET-SPLIT", "Fin root fillet load = C4's fillet-intact split, aft share moved ahead of the "
               "bond break (rigid root)",
               "The bonded half-fin root and coves carry, per quarter, the force and moment C4 computed with the root "
               "pinned (team/C4/claims.d3.json CALC-C4-D3-STATIC fillet_share_table, L4 and G2, both senses, limit); "
               "the share C4 puts aft of x 0.22 is moved, with its moment, onto the bonded root ahead of x 0.22 "
               "(ASM-C2-FILLET-BREAK); the block carries the rest of the station load",
               value=1.0, unit="-", status="PROPOSED",
               basis="a pinned (rigid) root attracts the most load; the real root sits on foam and sheds load back "
                     "to the tube / block path, so the split is an upper bound for the fillet; moving the aft share "
                     "forward (rather than back to the block) is the larger load on the bonded root. C4's table is "
                     "for the shoe before D-106 (C4 to re-issue it on the drawn shoe with the root free aft of the "
                     "hinge)")
for _k, _n in (("S1", "tension"), ("S3", "compression"), ("TAU", "shear")):
    passthrough(f"CALC-C2-FEA-CORNER-{_k}-SPLIT", f"Block-pocket corner foam {_n}, vm(L/2), tape 50 %, C4 fillet split, "
                "ultimate", F + f"split_corner_{_k.lower()}_ult_pa", assumes=TCD)
passthrough("CALC-C2-FEA-SPLIT-S1", "Foam tension 99.5th pct by volume, C4 fillet split, ultimate",
            F + "split_foam_s1_p995v_ult_pa", assumes=["ASM-C2-TUBE-ET"])
passthrough("CALC-C2-FEA-SPLIT-TAU", "Foam shear 99.5th pct by volume, C4 fillet split, ultimate",
            F + "split_foam_tau_p995v_ult_pa", assumes=["ASM-C2-TUBE-ET"])
passthrough("CALC-C2-FEA-CUTOUT-SPLIT-S1", "Cut-out corner foam tension, 1 mm average, C4 fillet split, ultimate",
            F + "split_cutout_s1_ult_pa", assumes=["ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-CUTOUT-SPLIT-S3", "Cut-out corner foam compression, 1 mm average, C4 fillet split, ultimate",
            F + "split_cutout_s3_ult_pa", assumes=["ASM-C2-FOAM-AVG-R"])
passthrough("CALC-C2-FEA-CUTOUT-SPLIT-TAU", "Cut-out corner foam shear, 1 mm average, C4 fillet split, ultimate",
            F + "split_cutout_tau_ult_pa", assumes=["ASM-C2-FOAM-AVG-R"])
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
kit.claim("CL-C2-FEA-FOAM-S1", "Core foam tension (99.5th percentile by volume), ultimate, station loads on the hard points",
          calc="CALC-C2-FEA-FOAM-S1", unit="Pa", limit=("<=", I + "xps_tens_allow_pa"), verifies=SM, parts=["WNG-001"],
          how="T-C2-XPS-COUPON (allowable) and T-C1-WING-PROOF (no crack at the elevon cut-out corners)")
kit.claim("CL-C2-FEA-FOAM-TAU", "Core foam shear (99.5th percentile by volume), ultimate, station loads on the hard points",
          calc="CALC-C2-FEA-FOAM-TAU", unit="Pa", limit=("<=", I + "xps_shear_allow_pa"), verifies=SM, parts=["WNG-001"],
          how="T-C2-XPS-COUPON and T-C1-WING-PROOF")
kit.claim("CL-C2-FEA-PETG", "PETG block and anchor von Mises peak, ultimate", calc="CALC-C2-FEA-PETG", unit="Pa",
          limit=("<=", I + "petg_bearing_allow_pa"), verifies=SM, parts=["FIN-004-L", "FIN-004-R", "WNG-004-L", "WNG-004-R", "WNG-005-L", "WNG-005-R"],
          how="T-C4-BLOCK-PROOF (C4)")
PROOF = ("T-C1-WING-PROOF (GT-08) steps 1-2 and T-C1-STATION-PROOF; inspect the four block-pocket corners and beads "
         "with a light after each step (no crack, no bead debond)")
RERUN = ("c2r5_corner.py local --variant band --level 2 --band-x 0.24 --band-dy 0.2 --Et 0.044e6 --dbl-mult 3 "
         "--dump-servo --out-dir <scratch>; c2r5_measure.py --dir <scratch>; data/c2w2_measures.json; c2r5_reduce.py; "
         "fea_claims.py")
COUPON = ("T-C2-XPS-COUPON decides the tape credit (taped vs untaped block torsion coupon, 3 SENB beams for K_Ic); "
          "fallback glass D-cell (A1.md D-153)")
DBL = ("D-153: the WNG-003 base skin (no strip end, butt or splice in |y| 0.27-0.37 for x <= 0.24) and the 2-layer "
       "block doubler band (|y| 0.29-0.35, LE wrap to x 0.120 both surfaces) are structural")
CORNER_PARTS = ["WNG-001", "WNG-003", "FIN-004-L", "FIN-004-R"]
for _k, _n, _lim in (("S1", "tension", "xps_tens_allow_pa"), ("S3", "compression", "xps_comp_allow_pa"),
                     ("TAU", "shear", "xps_shear_allow_pa")):
    kit.claim(f"CL-C2-FEA-FOAM-CORNER-{_k}", f"Core foam {_n} at the R 3 mm block-pocket corners, vm(L/2), with the "
              "tape skin and 2-layer block doubler at 50 % credit, ultimate (D-153)", calc=f"CALC-C2-FEA-CORNER-{_k}",
              unit="Pa", limit=("<=", I + _lim), verifies=SM, parts=CORNER_PARTS, note=DBL,
              how=PROOF + "; " + COUPON + ". Re-run: " + RERUN)
    kit.claim(f"CL-C2-FEA-FOAM-CORNER-{_k}-T25", f"Core foam {_n} at the block-pocket corners, vm(L/2), tape at 25 % "
              "credit (sensitivity)", calc=f"CALC-C2-FEA-CORNER-{_k}-T25", unit="Pa", limit=("<=", I + _lim),
              parts=CORNER_PARTS, note="sensitivity to the tape credit; does not verify the requirement",
              how=COUPON + ". Re-run: as the 50 % case with --Et 0.022e6")
    kit.claim(f"CL-C2-FEA-FOAM-CORNER-{_k}-BASE", f"Core foam {_n} at the block-pocket corners, vm(L/2), no skin "
              "(untaped base, information)", calc=f"CALC-C2-FEA-CORNER-{_k}-BASE", unit="Pa", parts=["WNG-001"],
              note="record, no limit: the model before D-153 and the coupon control. It exceeds the allowable (the "
                   "untaped wing does not pass); the untaped coupon shows how conservative the measure is",
              how="c2r5_corner.py local --variant base --level 3; c2r5_measure.py; c2r5_reduce.py")
    kit.claim(f"CL-C2-FEA-FOAM-SERVO-{_k}", f"Core foam {_n} round the lower-skin servo-pocket opening (skin cut "
              "out, inside the no-seam zone), vm(L/2), tape at 50 %, ultimate", calc=f"CALC-C2-FEA-SERVO-{_k}",
              unit="Pa", limit=("<=", I + _lim), verifies=SM, parts=["WNG-001", "WNG-003"],
              note="servo-pocket opening |y| 0.2527-0.2879, x 0.1722-0.2075 (subsystems/wing/params.json "
                   "servo_pocket), modelled as a void with no skin over it; the servo-pocket tape doubler is not "
                   "modelled (conservative); local cut plane at y 0.27, results kept 6 mm clear of it",
              how=PROOF.replace("block-pocket corners and beads", "servo-pocket opening corners") + ". Re-run: " + RERUN)
kit.claim("CL-C2-FEA-FOAM-CORNER-S1-CUTS", "Core foam tension at the pocket corners with the ESC-lead grooves and "
          "open slot seams (SW-05), vm(L/2), tape at 50 %, ultimate", calc="CALC-C2-FEA-CORNER-S1-CUTS", unit="Pa",
          limit=("<=", I + "xps_tens_allow_pa"), verifies=SM, parts=CORNER_PARTS,
          note="grooves at x 54-64 mm to |y| 0.296 on both surfaces and both cap seams removed as open slits in the "
               "local model (geometry d68g); the tape skin bridges them, as built (harness SPEC: tape tabs, then the "
               "skin)", how=PROOF + ". Re-run: as the corner claim with --geom d68g")
kit.claim("CL-C2-FEA-FOAM-CORNER-S3-CUTS", "Core foam compression, same corners with the cuts, vm(L/2), ultimate",
          calc="CALC-C2-FEA-CORNER-S3-CUTS", unit="Pa", limit=("<=", I + "xps_comp_allow_pa"), verifies=SM,
          parts=CORNER_PARTS, how=PROOF + ". Re-run: as the corner claim with --geom d68g")
kit.claim("CL-C2-FEA-CUTS-RATIO", "Pocket-corner tension with the grooves and open seams / without (record)",
          calc="CALC-C2-FEA-CUTS-RATIO", unit="-", parts=["WNG-001"],
          note="record: close to 1 means the grooves and seams are not what loads the corner",
          how="c2r5_corner.py --geom d68g vs d68, tape model, level 2")
kit.claim("CL-C2-FEA-FOAM-CORNER-S1-G431", "Core foam tension at the pocket corners if the tube meets the GT-16 "
          "shear-modulus line (G 4.31 GPa, not the 3 GPa low corner), vm(L/2), tape at 50 %, ultimate (record)",
          calc="CALC-C2-FEA-CORNER-S1-G431", unit="Pa", parts=["WNG-001"],
          note="record, no limit: sensitivity to the tube G (the corner stress follows the spar twist under the L4 "
               "fin-joint torque)",
          how="T-C4-TUBE-TORSION (GT-16) gives G; re-run with C2_TUBE_G set and --global-pkl "
              "out/d68_global_block_g431.pkl")
kit.claim("CL-C2-FEA-FOAM-CORNER-S3-G431", "Core foam compression, same, tube at G 4.31 GPa, vm(L/2) (record)",
          calc="CALC-C2-FEA-CORNER-S3-G431", unit="Pa", parts=["WNG-001"], how="As CL-C2-FEA-FOAM-CORNER-S1-G431.")
kit.claim("CL-C2-FEA-TCD-HALF-L", "Critical-distance half-length L/2 for XPS (the corner measure radius, record)",
          calc="CALC-C2-TCD-HALF-L", unit="m", parts=["WNG-001"],
          note="1.78 mm = 6-18 XPS cells (cell 0.1-0.3 mm); L scales with K_Ic^2, so the SENB beams check it",
          how="T-C2-XPS-COUPON: 3 notched 40 x 40 x 160 mm XPS beams (SENB) on the purchased board")
kit.claim("CL-C2-FEA-BEAD", "Microballoon fillet bead along the pocket edges, max principal stress, ultimate",
          calc="CALC-C2-FEA-BEAD", unit="Pa", limit=("<=", "ASM-C2-BEAD"), verifies=SM, parts=["WNG-001"],
          note="worst of the untaped D-68 model and the tape models (the skin stiffens the surface over the bead)",
          how="T-C2-XPS-COUPON beaded-pocket coupon; " + PROOF)
kit.claim("CL-C2-FEA-CUTOUT-TAU", "Foam shear peak at the R 3 mm elevon cut-out corners (fin-root tab), primary path, "
          "ultimate", calc="CALC-C2-FEA-CUTOUT", unit="Pa", limit=("<=", I + "xps_shear_allow_pa"), verifies=SM,
          parts=["WNG-001"], how=PROOF.replace("block-pocket corners and beads", "elevon cut-out corners"))
SENS_NOTE = ("record, no limit (closure round 2026-11-14): 100 % of the station loads through the fin root fillet "
             "is not a state the drawn wing can reach. The fin is fixed to the tube and the through-core block, which "
             "is far stiffer than a microballoon cove on foam, so the bonded fillet carries only what compatibility "
             "gives it; C4 computed that split with the root pinned (rigid, an upper bound: CR-C2-12 answer, "
             "CL-C4-D3-FILLET-L4-SHARE 0.73 % of the root moment). The real path is checked with C4's split in "
             "CL-C2-FEA-SPLIT-* and CL-C2-FEA-CUTOUT-SPLIT-*. A 100 % path needs the block path gone (a broken "
             "block), which T-C4-BLOCK-PROOF and CL-C2-FEA-PETG cover")
kit.claim("CL-C2-FEA-CUTOUT-SENS", "Foam shear peak at the R 3 mm elevon cut-out corners if the fin root fillet carried "
          "100 % of the station loads (not a reachable state, record)",
          calc="CALC-C2-FEA-CUTOUT-SENS", unit="Pa", parts=["WNG-001", "FIN-001-UR", "FIN-001-LR"], note=SENS_NOTE,
          how="Bounding record; the real path is CL-C2-FEA-CUTOUT-SPLIT-*")
kit.claim("CL-C2-FEA-SUB-GCI", "Corner measure vm(L/2): GCI over three local levels (D-68 geometry, untaped)",
          calc="CALC-C2-FEA-SUB-GCI", unit="-", limit=("<=", "ASM-C2-FEA-GCI-TOL"), cites=["SRC-C2-CELIK-GCI"],
          note="D-153: the measure is shown to converge on the untaped geometry (3 levels). The tape model has two "
               "levels (CL-C2-FEA-SUB-TAPE-L1L2); its level 3 (2.3 M dofs) is open",
          how="c2r5_corner.py local --variant base --level 1/2/3; c2r5_measure.py; c2r5_gci.py; c2r5_reduce.py")
kit.claim("CL-C2-FEA-SUB-TAPE-L1L2", "Decided tape model: change of the corner vm(L/2) from local level 1 to 2",
          calc="CALC-C2-FEA-SUB-TAPE-L1L2", unit="-", limit=("<=", "ASM-C2-FEA-GCI-TOL"),
          note="two levels only (not a GCI): level 3 of the tape model is open (A1 to schedule on a free machine)",
          how="c2r5_corner.py local --variant band --level 1/2 (tape 50 %); c2r5_measure.py; c2r5_reduce.py")
kit.claim("CL-C2-FEA-SUB-CUT", "D-68 submodel: corner peaks change with the cut planes 10 mm closer",
          calc="CALC-C2-FEA-SUB-CUT", unit="-", limit=("<=", "ASM-C2-FEA-GCI-TOL"),
          how="out/fea_report.json#d68.cut_check")
kit.claim("CL-C2-FEA-FOAM-FILLET-SENS", "Core foam shear if the fin root fillet carried 100 % of the station loads (not a "
          "reachable state, record)", calc="CALC-C2-FEA-FILLET-SENS", unit="Pa",
          parts=["WNG-001", "FIN-001-UR", "FIN-001-UL", "FIN-001-LR", "FIN-001-LL"], note=SENS_NOTE,
          how="Bounding record; the real path is CL-C2-FEA-SPLIT-S1 / -TAU")
SPLIT_PARTS = ["WNG-001", "WNG-003", "FIN-001-UR", "FIN-001-UL", "FIN-001-LR", "FIN-001-LL"]
SPLIT_HOW = ("c2cl_split_reduce.py RUNS (wing_fea_direct.py / wing_fea_d68.py --intro c4split, four sense / y-sign "
             "combinations); data/c2cl_split.json; T-C1-STATION-PROOF inspects the fin root and the cut-out corners")
SPLIT_NOTE = ("worst of the four C4 sense / y-sign combinations; C4's rigid-root split is an upper bound for a "
              "foam wing; the root is released from x 0.22 to the TE (ASM-C2-FILLET-BREAK)")
kit.claim("CL-C2-FEA-SPLIT-S1", "Core foam tension (99.5th pct by volume), fin root fillet carrying C4's intact split, "
          "rest on the block, ultimate", calc="CALC-C2-FEA-SPLIT-S1", unit="Pa", limit=("<=", I + "xps_tens_allow_pa"),
          verifies=SM, parts=SPLIT_PARTS, assumes=["ASM-C2-FILLET-SPLIT", "ASM-C2-FILLET-BREAK"], note=SPLIT_NOTE, how=SPLIT_HOW)
kit.claim("CL-C2-FEA-SPLIT-TAU", "Core foam shear (99.5th pct by volume), fin root fillet carrying C4's intact split, "
          "rest on the block, ultimate", calc="CALC-C2-FEA-SPLIT-TAU", unit="Pa", limit=("<=", I + "xps_shear_allow_pa"),
          verifies=SM, parts=SPLIT_PARTS, assumes=["ASM-C2-FILLET-SPLIT", "ASM-C2-FILLET-BREAK"], note=SPLIT_NOTE, how=SPLIT_HOW)
for _k, _lim, _n in (("S1", "xps_tens_allow_pa", "tension"), ("S3", "xps_comp_allow_pa", "compression"),
                     ("TAU", "xps_shear_allow_pa", "shear")):
    kit.claim(f"CL-C2-FEA-FOAM-CORNER-{_k}-SPLIT", f"Core foam {_n} at the block-pocket corners, vm(L/2), tape 50 %, fin "
              "root fillet carrying C4's split (bond break at x 0.22), ultimate", calc=f"CALC-C2-FEA-CORNER-{_k}-SPLIT",
              unit="Pa", limit=("<=", I + _lim), verifies=SM, parts=CORNER_PARTS + ["FIN-001-UR", "FIN-001-LR"],
              assumes=TCD + ["ASM-C2-FILLET-SPLIT", "ASM-C2-FILLET-BREAK"], note=SPLIT_NOTE + "; governing combination",
              how=SPLIT_HOW)
    kit.claim(f"CL-C2-FEA-CUTOUT-SPLIT-{_k}", f"Foam {_n} at the R 3 mm elevon cut-out corners (1 mm average), fin "
              "root fillet carrying C4's intact split, ultimate", calc=f"CALC-C2-FEA-CUTOUT-SPLIT-{_k}", unit="Pa",
              limit=("<=", I + _lim), verifies=SM, parts=SPLIT_PARTS, note=SPLIT_NOTE,
              assumes=["ASM-C2-FILLET-SPLIT", "ASM-C2-FILLET-BREAK", "ASM-C2-FOAM-AVG-R"], how=SPLIT_HOW)
    # local level 2 (h 1.1 mm), as CL-C2-FEA-CUTOUT-TAU; the corner 1 mm average grew 10 % from level 1 to 2 on the
    # hinge-break variant, well inside these margins (closure-round report C2.md 1.3)
kit.claim("CL-C2-FEA-W-RATIO", "3-D FEA / beam model, tip deflection (G2, no tape)", calc="CALC-C2-FEA-W-RATIO", unit="-",
          how="Shows the beam model (all deflection, mode and aeroelastic claims) is within a few % of the 3-D model")
kit.claim("CL-C2-FEA-TW-RATIO", "3-D FEA / beam model, tip twist (L4, no tape)", calc="CALC-C2-FEA-TW-RATIO", unit="-",
          how="As above, for twist (GJ): the input of every aeroelastic claim")

if __name__ == "__main__":
    kit.write()
