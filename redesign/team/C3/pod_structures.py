"""C3 pod structures: load path from the pack to the wing core, sized against C1's loads (K09-L).

Run:  python -I redesign/team/C3/pod_structures.py      (prints value + margin per claim, writes claims.json)
      python -I redesign/proofs/build_graph.py
Inputs: params.json, C1 joint loads (team/C1/data/joints.csv, rows J-POD and J-PACK, envelope families only),
D2's pod geometry (subsystems/pod/params.json and CL-D2-* claims), shared allowables (ASM-C4-*, ASM-D2-*, ASM-D5-*).
File data enter the graph as ASM-C3-* assumptions written when this script runs, so every calculation stays a pure
function of node ids (same pattern as team/D2/pod_claims.py).

Load path checked, element by element (FUSELAGE-STRUCTURES.md section 2):
  pack -> aft stop (+x) / forward stop (-x) / guides (+-y) / straps (+z) / tray (-z)
       -> tray-to-floor bond -> foam-board floor + side walls (overhang ahead of the LE)
       -> pod-to-wing bond (LE filler + recess floor) -> XPS core -> spar
  carry handle -> 2 ties -> spar ; hatch -> tongue + hook-and-loop tab (suction only)
Factors (C1 convention): design = limit x 1.5 x 1.15 (fitting) x 1.25 (printed / bonded into foam);
crash = C1 ultimate as given, no further factor.
"""
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
sys.path.insert(0, str(REDESIGN / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"
G0 = 9.80665
_POD = json.loads((REDESIGN / "subsystems" / "pod" / "params.json").read_text(encoding="utf-8"))
_pv = lambda k: _POD[k]["value"]
_PAR = json.loads((REDESIGN / "params" / "params.json").read_text(encoding="utf-8"))
_gv = lambda sec, k: _PAR[sec][k]["value"]
ENVELOPE_FAMILIES = ("flight", "hover", "transition", "landing", "ground")


def _joint_rows(joint):
    rows = []
    with open(REDESIGN / "team" / "C1" / "data" / "joints.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["joint"] == joint and r["family"] in ENVELOPE_FAMILIES:
                rows.append([f"{r['case']}/{r['mass_config']}"] +
                            [round(float(r[k]), 4) for k in ("Fx_N", "Fy_N", "Fz_N", "Mx_Nm", "My_Nm", "Mz_Nm")])
    return rows


SRC = ["SRC-K09-CARD"]
# ---------------------------------------------------------------- assumptions
kit.assumption("ASM-C3-POD-LOADS", "C1 pod-group joint loads, envelope cases, limit",
               "Six components [case, Fx, Fy, Fz (N), Mx, My, Mz (N m)] the pod group (pod, pack, avionics, power, "
               "harness, MC-C growth) passes to the wing, about C1's point (pod centre x, y 0, pod base z)",
               basis="team/C1/data/joints.csv rows J-POD, families flight/hover/transition/landing/ground, MC-C and MC-P",
               value=_joint_rows("J-POD"), unit="N, N m", cites=SRC)
kit.assumption("ASM-C3-PACK-LOADS", "C1 pack-to-tray loads, envelope cases, limit",
               "Forces [case, Fx, Fy, Fz] the pack passes to the tray (x aft, z up, cruise frame)",
               basis="team/C1/data/joints.csv rows J-PACK, same families", value=[r[:4] for r in _joint_rows("J-PACK")],
               unit="N", cites=SRC)
kit.assumption("ASM-C3-XPS-SHEAR", "Epoxy-to-XPS bond shear allowable 100 kPa",
               "Allowable shear at an epoxy bond line on F-250 XPS, foam failure",
               basis="C6 value (CR-C6-16): ASM-C6-FOAM-KD 0.5 x ASM-C6-XPS-SHEAR-TYP 0.20 MPa; kept for C6's "
                     "CALC-C6-POD-ALLOW comparison, the C3 calcs read C6's nodes through CALC-C3-ALLOW",
               value=100000.0, unit="Pa", status="UNVERIFIED", cites=["SRC-XPS-F250"])
kit.assumption("ASM-C3-STOP-H", "Forward stop height 25 mm", "Printed forward stop height above the tray top "
               "(C5's CALC-C5-CRASH reads it as the stop section height)",
               basis="subsystems/pod/params.json fwd_stop_m[1] (D2-R4; stop_wall_h_m retired)",
               value=_pv("fwd_stop_m")[1], unit="m", cites=SRC)
kit.assumption("ASM-C3-AFT-STOP-H", "Aft stop height 27 mm", "Printed aft stop top above the pack underside: "
               "lever of the pack load at the stop root (uniform pressure over this height)",
               basis="subsystems/pod/params.json aft_stop_m[1] (D2-R4)", value=_pv("aft_stop_m")[1], unit="m", cites=SRC)
kit.assumption("ASM-C3-PAD", "Pack underside 2.5 mm above the tray top (EVA pads)",
               "The pack bears on the aft stop from the pad top to the stop top, so the resultant of a uniform contact "
               "sits pad + h/2 above the stop root (C3-R2 used h/2 alone: 13.5 vs 16.0 mm, -16 % on stress)",
               basis="subsystems/pod/params.json pad_t_m (D2-R5a); found in the C3-R3 FEA round (M2 section-linearised "
                     "root moment)", value=_pv("pad_t_m"), unit="m", cites=SRC)


def _a3_group():
    """Pod-group items from A3's roll-up that load the pod-to-wing bond: pod, avionics, power less the pack and the
    fin-mounted ESC pads, the pod harness. The handle group (POD-005 mast, POD-007 handle, AVN-002 GPS) is bonded and
    tied to the spar (E-POD-09) and passes through deck holes, so its inertia does not cross the bond."""
    rows = json.loads((REDESIGN / "team" / "A3" / "rollup" / "mass_items.json").read_text(encoding="utf-8"))
    rows = rows["a3"]["rollup"]["items"]["value"]
    keep = [r for r in rows if r[1] in ("pod", "avionics", "power", "harness") and abs(r[5]) < 0.07
            and r[0] not in ("PWR-001", "POD-005", "POD-007", "AVN-002")]
    m = sum(r[3] for r in keep)
    return [round(m, 2), round(sum(r[3] * r[4] for r in keep) / m, 5), round(sum(r[3] * r[6] for r in keep) / m, 5)]


kit.assumption("ASM-C3-GROUP-A3", "Pod group less the pack, as designed (A3-R6a roll-up)",
               "[mass g, x m, z m] of the items whose inertia crosses the pod-to-wing bond: POD-001..004, -006, -008..010, "
               "PWR-002..007, AVN-001, -003..007, HRN-001; the handle group (POD-005, POD-007, AVN-002, 41.5 g) is on the "
               "spar (E-POD-09) and the pack is added per case",
               basis="team/A3/rollup/mass_items.json (A3-R6a, generated by mass_rollup.py); replaces the allocation-based "
                     "sum of C3-R2 (CL-D2-MASS + avionics + power allocations)", value=_a3_group(), unit="g, m",
               cites=SRC)


def _fea_summary():
    """Key numbers from fea/fea_results.json (written by pod_fea.py, SU2 ELASTICITY on gmsh meshes, 4 levels).
    Each value is the finest-mesh result, or the Richardson extrapolation when that is larger (conservative)."""
    f = HERE / "fea" / "fea_results.json"
    if not f.exists():
        return {}
    r = json.loads(f.read_text(encoding="utf-8"))
    fp, bd, m2 = r["M1_FOOTPRINT"], r["M1_BONDED"], r["M2"]

    def best(conv, fine):
        """Conservative: the largest of the finest-mesh value, every coarser level, and the Richardson extrapolation
        when the observed order is > 0.5 (a singular, non-converging corner value therefore reports its finest level)."""
        v = max([fine] + list(conv.get("q", [])))
        q = conv.get("q_ext")
        return max(v, q) if (q is not None and conv.get("p") is not None and conv["p"] > 0.5) else v

    def crash_max(m, lv_):
        return max(best(m["convergence"]["crash_%s_R_d0" % d], lv_["crash_%s" % d]["R_peak_d0"])
                   for d in ("up", "dn", "px", "mx"))

    lf, lb = fp["levels"][-1], bd["levels"][-1]
    out = {"R_design_inplane_fea": best(fp["convergence"]["design_R_d0"], lf["design"]["R_peak_d0"]),
           "R_design_inplane_hand": fp["hand_design_inplane"]["R"],
           "R_crash_fea": max(best(fp["convergence"]["crash_up_R_d0"], lf["crash_up"]["R_peak_d0"]),
                              best(fp["convergence"]["crash_dn_R_d0"], lf["crash_dn"]["R_peak_d0"]),
                              best(fp["convergence"]["crash_px_R_d0"], lf["crash_px"]["R_peak_d0"]),
                              best(fp["convergence"]["crash_mx_R_d0"], lf["crash_mx"]["R_peak_d0"])),
           "R_crash_up_hand": fp["hand_crash_up_inplane"]["R"],
           "R_bonded_design_fea": lb["design"]["R_peak_d0"],
           "R_bonded_crash_fea": max(lb[k]["R_peak_d0"] for k in ("crash_up", "crash_dn", "crash_px", "crash_mx")),
           "overhang_crash_fea_pa": best(fp["convergence"]["overhang_crash_top"], lf["overhang_crash_top_pa"]),
           "group_mass_kg": fp["group_mass_kg"],
           "R_design_5mm_fea": lf["design"]["R_peak_5mm"],
           "R_crash_5mm_fea": max(lf[k]["R_peak_5mm"] for k in ("crash_up", "crash_dn", "crash_px", "crash_mx"))}
    for key, tag in (("M1_TIED_FOOTPRINT", "tied"), ("M1_TIED_STEPGAP", "fix")):
        if key in r:
            m = r[key]
            lt = m["levels"][-1]
            out["R_%s_design_fea" % tag] = best(m["convergence"]["design_R_d0"], lt["design"]["R_peak_d0"])
            out["R_%s_crash_fea" % tag] = crash_max(m, lt)
            out["R_%s_crash_5mm_fea" % tag] = max(lt[k]["R_peak_5mm"] for k in ("crash_up", "crash_dn", "crash_px",
                                                                                 "crash_mx"))
            out["F_%s_saddle_crash_n" % tag] = max(math.hypot(*f) for c, f in m["F_saddle_N"].items()
                                                   if c.startswith("CRASH")) if "F_saddle_N" in m else None
    if "M1_TIED_FOOTPRINT" in r and "F_saddle_limit_N" in r["M1_TIED_FOOTPRINT"]["levels"][-1]:
        lt = r["M1_TIED_FOOTPRINT"]["levels"][-1]                # C3-R4: bracket loads for H1 (CR-H1-23)
        out["F_tied_saddle_limit_n"] = math.hypot(*lt["F_saddle_limit_N"])
        out["F_tied_saddle_limit_x_n"] = abs(lt["F_saddle_limit_N"][0])
        out["F_tied_saddle_limit_z_n"] = abs(lt["F_saddle_limit_N"][1])
        out["F_tied_saddle_crash_max_n"] = max(math.hypot(*lt["F_saddle_crash_%s_N" % d]) for d in ("dn", "up", "px", "mx"))
    if "M1_TIED_STEPGAP" in r:                                     # C3-R4: fail-safe state after the aft-end peel
        m = r["M1_TIED_STEPGAP"]
        lt = m["levels"][-1]
        for d in ("dn", "mx", "up", "px"):
            out["R_fix_crash_%s_fea" % d] = best(m["convergence"]["crash_%s_R_d0" % d], lt["crash_" + d]["R_peak_d0"])
    if "M1_TIED_FOOTPRINT" in r:
        m = r["M1_TIED_FOOTPRINT"]
        lt = m["levels"][-1]
        for d in ("dn", "mx", "up", "px"):
            out["R_tied_crash_%s_fea" % d] = best(m["convergence"]["crash_%s_R_d0" % d], lt["crash_" + d]["R_peak_d0"])
    for key, tag in (("M1_TIED_FILLET", "fil"), ("M1_TIED_FILLET_SOFT", "fil_soft"), ("M1_TIED_SCARF15", "scarf15")):
        # C3-R4: the drawn WNG-007 recess-step fillet + bevelled floor end, feet tied, wall-edge bonds not credited
        if key not in r:
            continue
        m = r[key]
        lt = m["levels"][-1]
        cv = m["convergence"]
        out["R_%s_design_fea" % tag] = best(cv["design_R_d0"], lt["design"]["R_peak_d0"])
        out["R_%s_crash_fea" % tag] = crash_max(m, lt)
        out["R_%s_crash_5mm_fea" % tag] = max(best(cv[d + "_R_5mm"], lt[d]["R_peak_5mm"])
                                              for d in ("crash_up", "crash_dn", "crash_px", "crash_mx"))
        out["R_%s_design_5mm_fea" % tag] = best(cv["design_R_5mm"], lt["design"]["R_peak_5mm"])
        out["R_%s_ff_fea" % tag] = max(best(cv["ff_%s_R_d0" % d], lt["ff_" + d]["R_peak_d0"])
                                       for d in ("design", "crash_up", "crash_dn", "crash_px", "crash_mx"))
        out["R_%s_ff_design_mean" % tag] = lt["ff_design"].get("Rcore_mean", lt["ff_design"].get("R_mean"))
        out["R_%s_crash_up_fea" % tag] = best(cv["crash_up_R_d0"], lt["crash_up"]["R_peak_d0"])
        out["R_%s_crash_dn_5mm" % tag] = best(cv["crash_dn_R_5mm"], lt["crash_dn"]["R_peak_5mm"])
        out["%s_crash_peak_xz" % tag] = max(((lt[d]["R_peak_d0"], [lt[d]["x_R_peak"], lt[d]["z_R_peak"]])
                                             for d in ("crash_up", "crash_dn", "crash_px", "crash_mx")))[1]
        if "F_saddle_limit_N" in lt:
            out["F_%s_saddle_limit_n" % tag] = math.hypot(*lt["F_saddle_limit_N"])
            out["F_%s_saddle_limit_xz_n" % tag] = lt["F_saddle_limit_N"]
            out["F_%s_saddle_crash_n" % tag] = max(math.hypot(*lt["F_saddle_crash_%s_N" % d])
                                                   for d in ("dn", "up", "px", "mx"))
    for k, v in r.get("M2F", {}).items():
        # C3-R4: the D2-R6 forward-stop T with its flange (as drawn, and with the C3-R4 fix)
        lv_ = v["levels"][-1]
        c = v["convergence"]
        out[k] = {q: best(c[q], lv_[q]) for q in c}
    for k, v in m2.items():
        lv_ = v["levels"][-1]
        c = v["convergence"]
        out[k] = {"stop_peak_pa": best(c["peak_s1_pa"], lv_["peak_s1_pa"]),
                  "tray_peak_pa": best(c["tray_peak_pa"], lv_["tray_peak_pa"]),
                  "peel_pa": best(c["peel_peak_d0_pa"], lv_["peel_peak_d0_pa"]),
                  "sigma_lin_pa": lv_["sigma_lin_pa"]}
        for q in ("wall_face_peak_pa", "bed_peel_peak_pa", "tray_path_share"):
            if q in lv_:
                out[k][q] = best(c[q], lv_[q]) if q in c else lv_[q]
    return out


kit.assumption("ASM-C3-FEA", "C3 FEA results (SU2 ELASTICITY, gmsh, 4 mesh levels)",
               "Finest-mesh (or Richardson-extrapolated, whichever is larger) peaks from pod_fea.py: bond interaction "
               "averaged over d0 = 2 mm (M1, 2.5-D section, footprint and fully bonded variants), overhang wall-top face "
               "stress, stop root peak principal stress, tray bending peak, board flat-wise peel averaged over 2 mm (M2, "
               "plane strain, per stop variant)",
               basis="team/C3/fea/fea_results.json (python -I redesign/team/C3/pod_fea.py); materials ASM-C3-XPS-E, "
                     "ASM-C3-PETG-E, ASM-C4-FACE-*, ASM-C4-CORE-E; see team/C3/SIMULATION-REPORT.md",
               value=_fea_summary(), unit="-, Pa", status="UNVERIFIED", cites=SRC)
kit.assumption("ASM-C3-XPS-E", "XPS F-250 modulus 20 MPa (FEA)", "Young's modulus of the wing core and LE filler, "
               "nu 0.25", basis="2 G (1 + nu) with G 8 MPa (ASM-D6-XPS-G); published XPS 10-40 MPa; T-C3-BOND-COUPON "
               "stiffness", value=20.0e6, unit="Pa", status="UNVERIFIED", cites=SRC)
kit.assumption("ASM-C3-PETG-E", "Printed PETG modulus 1.8 GPa (FEA)", "Young's modulus of the printed tray and stops, "
               "nu 0.38", basis="Prusament-class PETG 1.5-2.0 GPa (SRC-D5-PETG class data)", value=1.8e9, unit="Pa",
               status="UNVERIFIED", cites=SRC)
kit.assumption("ASM-C3-EPOXY-E", "Bed epoxy modulus 3.0 GPa (FEA)", "Young's modulus of the 1 mm microballoon-epoxy "
               "bed between the forward stop and the nose wall, nu 0.35", basis="laminating epoxy 2.5-3.5 GPa, filled; "
               "the bed is thin, so the result is insensitive to it", value=3.0e9, unit="Pa", status="UNVERIFIED",
               cites=SRC)
kit.assumption("ASM-C3-STRUT", "Aft-stop strut to the handle foot bridge (CR-C3-14)",
               "[length x, n ribs, rib thickness y, rib height z, pad width y, pad thickness x] of printed PETG ribs on the "
               "handle foot bridge (POD-007) ending in a pad that bears on the aft stop's back face, z 0.026-0.040 (the "
               "FEA prop face)",
               basis="length = bridge_x0_m - (aft_stop_x_m + aft_stop_m[0]) from subsystems/pod/params.json; 3 ribs "
                     "3 x 14 mm; pad 40 x 14 x 2 mm (inside the legs, clear of the guides)",
               value=[round(_pv("bridge_x0_m") - _pv("aft_stop_x_m") - _pv("aft_stop_m")[0], 4), 3, 0.003, 0.014,
                      0.040, 0.002],
               unit="m", status="PROPOSED", cites=SRC)
kit.assumption("ASM-C3-FEA-D0", "Bond peak averaging length 2 mm", "Peel / shear peaks at the bi-material bond corners "
               "are singular in linear FEA; the margin uses the mean over 2 mm (about 10 XPS cells) and the report shows "
               "the raw and 5 mm values", basis="point/average-stress practice for foam bonds; T-C3-POD-PROOF",
               value=0.002, unit="m", status="UNVERIFIED", cites=SRC)

kit.assumption("ASM-C3-D47-NOSE", "D-47 nose stack: forward stop aft face -0.1212 m, stack 8.8 mm",
               "[forward stop aft face x, nose wall + block A + forward stop length] that A1 decided at D-47",
               basis="params/CHANGE-LOG.md D-47 (CR-A3-22, CR-D2-16): nose block 14.8 -> 8.8 mm, forward stop "
                     "-0.1002 -> -0.1212; D2 has not yet re-laid subsystems/pod/params.json (nose_block_l_m 0.007)",
               value=[-0.1212, 0.0088], unit="m", cites=["SRC-K09-CARD"])
kit.assumption("ASM-C3-FILLET-LEG", "Floor-to-side-wall corner fillet leg 6 mm",
               "Microballoon-epoxy fillet along both floor-to-wall corners +-30 mm of each strap; widens the glue line",
               basis="C6 CR-C6-17, adopted by D2 at R4 (subsystems/pod/params.json bought_g.fillet_corners)",
               value=0.006, unit="m", cites=SRC)
kit.assumption("ASM-C3-GUIDE", "Bay guides as modelled by D2", "Guide thickness and height above the tray [t, h]",
               basis="subsystems/pod/params.json guide_t_m, guide_h_m", value=[_pv("guide_t_m"), _pv("guide_h_m")],
               unit="m", cites=SRC)
kit.assumption("ASM-C3-REC", "C3 recommended sizes",
               "[aft stop t, forward stop t, guide t, guide h] for printed PETG (tray printed flat: wall bending "
               "loads the layer bonds)", basis="sized in this script to margin >= 0 at 15 MPa", value=[0.003, 0.003, 0.0015, 0.008],
               unit="m", cites=SRC)
kit.assumption("ASM-C3-HL", "Hook-and-loop allowables",
               "[shear N/cm2 of overlap, flat-wise tension N/cm2] for sew-on nylon hook-and-loop, knocked down 2x",
               basis="ESTIMATE from catalogue class values (shear 10-15, tension 5-10 N/cm2); T-D2-STRAP-PULL",
               value=[5.0, 2.5], unit="N/cm2", status="UNVERIFIED", cites=SRC)
kit.assumption("ASM-C3-STRAP-OVERLAP", "Strap hook-and-loop overlap 50 mm", "Specified overlap of each 20 mm strap",
               basis="C3 specification for D2 (BUILD step: mark 50 mm on the strap)", value=0.05, unit="m", cites=SRC)
kit.assumption("ASM-C3-FB-FLAT", "Foam-board flat-wise tension 100 kPa",
               "Paper-face-to-core flat-wise tension allowable of 4.8 mm paper-faced board",
               basis="C6 value (CR-C6-16): ASM-C6-FOAM-KD 0.5 x ASM-C6-BOARD-FLAT-TYP 0.10 MPa = 50 kPa (was 100); kept "
                     "for C6's comparison, the C3 calcs read C6's nodes through CALC-C3-ALLOW",
               value=50000.0, unit="Pa", status="UNVERIFIED", cites=SRC)
kit.assumption("ASM-C3-SPREAD", "Plate load spread 10 mm each side of a strap",
               "Length of 1 mm PETG tray that shares a strap's pull either side of the 20 mm strap", basis="~10 x tray thickness",
               value=0.010, unit="m", cites=SRC)
def _a3_ahead():
    rows = json.loads((REDESIGN / "team" / "A3" / "rollup" / "mass_items.json").read_text(encoding="utf-8"))
    rows = rows["a3"]["rollup"]["items"]["value"]
    return [[round(r[3], 2), round(r[4], 4)] for r in rows
            if r[1] in ("pod", "avionics", "power", "harness") and abs(r[5]) < 0.07 and r[4] < 0
            and r[0] not in ("PWR-001", "POD-005", "POD-007", "AVN-002")]


kit.assumption("ASM-C3-OVERHANG-ITEMS", "Non-pack masses ahead of the wing LE (A3-R6a roll-up)",
               "[mass g, x m] of every pod-group item whose centroid is ahead of x = 0 (pack excluded, added per case)",
               basis="team/A3/rollup/mass_items.json (A3-R6a); replaces C3-R2's allocation split (83 g); weigh "
                     "(T-D2-WEIGH)", value=_a3_ahead(), unit="g, m", status="UNVERIFIED", cites=SRC)
kit.assumption("ASM-C3-CP-HATCH", "Hatch suction Cp -1.0", "Peak suction on the pod top at VD (bluff box top, separated LE corner)",
               basis="ESTIMATE, conservative for a 70 mm box on a wing", value=-1.0, unit="-", status="UNVERIFIED", cites=SRC)
kit.assumption("ASM-C3-HATCH", "Hatch plan and latch", "[hatch length x, width y, latch tab x, tab y] (m)",
               basis="params.json pod.x_le_m + fins.board_t_m + pod lip_m[0] to hatch_aft_x_m; pod.size_m[1]; "
                     "subsystems/pod/params.json latch_tab_m",
               value=[_pv("hatch_aft_x_m") - (_gv("pod", "x_le_m") + _gv("fins", "board_t_m") + _pv("lip_m")[0]),
                      _gv("pod", "size_m")[1]] + _pv("latch_tab_m"),
               unit="m", cites=SRC)
kit.assumption("ASM-C3-GRIP", "Carry-handle grip 10 x 8 mm PETG, legs at +-34 mm", "[grip x, grip z, leg y]",
               basis="subsystems/pod/params.json grip_m, leg_y_m", value=_pv("grip_m") + [_pv("leg_y_m")], unit="m", cites=SRC)
kit.assumption("ASM-C3-PETG-INPLANE", "Printed PETG in-plane (along-raster) allowable 25 MPa",
               "Bending allowable along the filament (part printed so the stress runs along the layers)",
               basis="filament data 40-50 MPa (ASM-D5-PETG-SIGMA basis) x ~0.6", value=25.0e6, unit="Pa", status="UNVERIFIED",
               cites=SRC)

# ---------------------------------------------------------------- calculations
F_IN = {"sf": P + "requirements.safety_factor_ult", "kf": "ASM-C1-FITTING-FACTOR", "kp": "ASM-C1-PRINTED-FACTOR"}


@kit.calc("CALC-C3-ALLOW", title="Pod joint allowables from C6 (CR-C6-16)",
          equation="design allowable = C6 knock-down x typical: XPS shear kd tau_xps, epoxy on the paper face kd tau_b, "
                   "board flat-wise kd f_b",
          inputs={"kd": "ASM-C6-FOAM-KD", "t_xps": "ASM-C6-XPS-SHEAR-TYP", "tau_b": "ASM-D5-BOND-TAU",
                  "f_b": "ASM-C6-BOARD-FLAT-TYP"})
def allow(kd, t_xps, tau_b, f_b):
    return {"xps_shear_pa": kd * t_xps, "paper_shear_pa": kd * tau_b, "board_flat_pa": kd * f_b}


@kit.calc("CALC-C3-BOND", title="Pod-to-wing bond: flight/ground envelope and crash",
          equation="loads moved from C1's point (pod centre, base) to the bond centroid: M' = M + (r_ref - r_c) x F; "
                   "footprint b x L, x 0 ... recess end; sigma = Fz/A + 6|My|/(b L^2) + 6|Mx|/(L b^2) (tension only); "
                   "tau = |Fxy|/A + |Mz| r_max / J; R = sigma/sigma_a + tau/tau_a; design = limit x SF x k_fit x k_print; "
                   "crash: m_group n_c g any axis at the group CG (A3 roll-up items + heaviest pack at the most forward "
                   "station), no further factor",
          inputs=dict(F_IN, rows="ASM-C3-POD-LOADS", xle=P + "pod.x_le_m", size=P + "pod.size_m", zb=P + "pod.z_base_m",
                      b="ASM-D2-POD-WIDTH", xs=P + "wing.spar.x_m", od=P + "wing.spar.od_m", wall="ASM-D2-SLOT-WALL",
                      sa="ASM-D2-XPS-ALLOW", ta="CL-C3-ALLOW-XPS-SHEAR", tfb="CL-C3-ALLOW-PAPER-SHEAR",
                      grp="ASM-C3-GROUP-A3", pack_rng="ASM-A3-PACK-RANGE", px="CL-D2-PACK-X-FWD-MIN", pz="CL-D2-PACK-Z",
                      nc="CL-C1-CRASH-N", g=P + "env.g_ms2"))
def bond(rows, xle, size, zb, b, xs, od, wall, sa, ta, tfb, grp, pack_rng, px, pz, nc, g, sf, kf, kp):
    x0, x1 = 0.0, xs - od / 2 - wall
    L = x1 - x0
    xc = (x0 + x1) / 2
    A, Iy, Ix = b * L, b * L ** 3 / 12, L * b ** 3 / 12
    rmax = math.hypot(L / 2, b / 2)
    tau_a = min(ta, tfb)
    ref = (xle + size[0] / 2, 0.0, zb)
    d = (ref[0] - xc, 0.0, 0.0)          # r_ref - r_c (bond plane at the pod base)

    def stresses(F, M):
        Mc = (M[0] + d[1] * F[2] - d[2] * F[1], M[1] + d[2] * F[0] - d[0] * F[2], M[2] + d[0] * F[1] - d[1] * F[0])
        sig = max(F[2], 0.0) / A + abs(Mc[1]) * (L / 2) / Iy + abs(Mc[0]) * (b / 2) / Ix
        tau = math.hypot(F[0], F[1]) / A + abs(Mc[2]) * rmax / (Ix + Iy)
        return sig, tau, sig / sa + tau / tau_a

    k = sf * kf * kp
    best = None
    for r in rows:
        s, t, R = stresses([k * v for v in r[1:4]], [k * v for v in r[4:7]])
        if best is None or R > best[2]:
            best = (s, t, R, r[0])
    # crash: pod group with the heaviest pack, 6 directions at the group CG
    items = [(grp[0], grp[1], grp[2]), (max(pack_rng), px, pz)]
    m = sum(i[0] for i in items) / 1000
    cg = (sum(i[0] * i[1] for i in items) / 1000 / m, 0.0, sum(i[0] * i[2] for i in items) / 1000 / m)
    Fc = m * nc * g
    worst_c = None
    for ax in range(3):
        for sgn in (1, -1):
            F = [0.0, 0.0, 0.0]
            F[ax] = sgn * Fc
            rr = (cg[0] - xc, 0.0, cg[2] - zb)
            M = (rr[1] * F[2] - rr[2] * F[1], rr[2] * F[0] - rr[0] * F[2], rr[0] * F[1] - rr[1] * F[0])
            sig = max(F[2], 0.0) / A + abs(M[1]) * (L / 2) / Iy + abs(M[0]) * (b / 2) / Ix
            tau = math.hypot(F[0], F[1]) / A + abs(M[2]) * rmax / (Ix + Iy)
            R = sig / sa + tau / tau_a
            if worst_c is None or R > worst_c[2]:
                worst_c = (sig, tau, R, "+-"[sgn < 0] + "xyz"[ax])
    return {"area_m2": A, "length_m": L, "sigma_design_pa": best[0], "tau_design_pa": best[1], "R_design": best[2],
            "case": best[3], "group_mass_kg": m, "group_cg_x": cg[0], "crash_F_n": Fc, "sigma_crash_pa": worst_c[0],
            "tau_crash_pa": worst_c[1], "R_crash": worst_c[2], "crash_dir": worst_c[3]}


def _wall_sigma(F, h, b, t):
    """Cantilever stop wall printed with the tray: uniform pack pressure over the wall height, root bending."""
    return 6 * F * (h / 2) / (b * t * t)


@kit.calc("CALC-C3-STOPS", title="Pack stops: aft stop wall (+x), forward stop (-x)",
          equation="F_design = max over cases of the pack force x SF x k_fit x k_print; crash F = C1 85 N; "
                   "sigma = 6 F (pad + h/2) / (b t^2) aft (pack bears from the pad top to the stop top), 6 F (h/2) / (b t^2) "
                   "fwd (block on the tray); b = bay + 2 guides; "
                   "fuse load of the forward stop F_f = sigma_a b t^2 / (6 h_f / 2); t_req = sqrt(6 F h/2 / (b sigma_a)); "
                   "nose wall (foam board) as a strip between the side walls: M = F/4 (S - c/2), "
                   "m_cap = sigma_f t_f (t - t_f) per unit width over the pack height",
          inputs=dict(F_IN, rows="ASM-C3-PACK-LOADS", fc="CL-C1-PACK-CRASH-LOAD", h="ASM-C3-AFT-STOP-H",
                      hf="ASM-C3-STOP-H", bw="ASM-D2-BAY-W", pad="ASM-C3-PAD",
                      gd="ASM-C3-GUIDE", t0="ASM-D2-STOP-T", rec="ASM-C3-REC", sa="ASM-C4-PETG-TENSILE",
                      W="ASM-D2-POD-WIDTH", tb=P + "fins.board_t_m", tf="ASM-C4-FACE-T", sf_face="ASM-C4-FACE-SIGMA",
                      pack=P + "battery.size_m"))
def stops(rows, fc, h, hf, bw, gd, t0, rec, sa, W, tb, tf, sf_face, pack, pad, sf, kf, kp):
    k = sf * kf * kp
    f_aft = max(max(r[1] for r in rows) * k, fc)
    f_fwd_flight = max(-min(r[1] for r in rows), 0.0) * k
    f_fwd = max(f_fwd_flight, fc)
    b = bw + 2 * gd[0]
    span = W - 2 * tb
    m_req = f_fwd / 4 * (span - pack[1] / 2) / pack[2]
    m_cap = sf_face * tf * (tb - tf)
    return {"F_aft_n": f_aft, "F_fwd_n": f_fwd, "F_fwd_flight_n": f_fwd_flight,
            "sigma_aft_d2_pa": _wall_sigma(f_aft, h + 2 * pad, b, t0),
            "t_req_m": math.sqrt(6 * f_aft * (pad + h / 2) / (b * sa)),
            "sigma_aft_rec_pa": _wall_sigma(f_aft, h + 2 * pad, b, rec[0]), "sigma_fwd_rec_pa": _wall_sigma(f_fwd, hf, b, rec[1]),
            "fwd_fuse_n": sa * b * rec[1] ** 2 / (6 * hf / 2),
            "nose_m_req_nmm_per_mm": m_req, "nose_m_cap_nmm_per_mm": m_cap}


@kit.calc("CALC-C3-GUIDES", title="Bay guides (+-y) and strap legs in a lateral crash",
          equation="q = F / L_pack on the guide, resultant at h/2: sigma = 6 q (h/2) / t^2; overturn about the far guide "
                   "top: T_legs = F (z_pack/2 + pad - h) / w_bay, per strap = T_legs / n",
          inputs=dict(F_IN, rows="ASM-C3-PACK-LOADS", fc="CL-C1-PACK-CRASH-LOAD", gd="ASM-C3-GUIDE", rec="ASM-C3-REC",
                      pack=P + "battery.size_m", bw="ASM-D2-BAY-W", n="ASM-D2-N-STRAPS"))
def guides(rows, fc, gd, rec, pack, bw, n, sf, kf, kp):
    f = max(max(abs(r[2]) for r in rows) * sf * kf * kp, fc)
    q = f / pack[0]
    sig = lambda t, hh: 6 * q * (hh / 2) / (t * t)
    t_leg = f * (pack[2] / 2 - gd[1]) / bw / n
    return {"F_n": f, "sigma_d2_pa": sig(gd[0], gd[1]), "sigma_rec_pa": sig(rec[2], rec[3]), "strap_leg_n": t_leg}


@kit.calc("CALC-C3-STRAPS", title="Straps (+z): loop tension, hook-and-loop overlap, tray and floor under the strap",
          equation="per strap P = max(F_flight x SF x k_fit x k_print, F_crash) / n; leg T = P/2 + preload/(2n); "
                   "overlap_req = T / (tau_hl w); tray flat-wise = P / (w_tray (w + 2 s)); front strap on the overhang: "
                   "floor-to-wall glue line q = P / (2 (w + 2 s)), stress = q / t_board (as drawn) or q / (t_board + fillet leg) "
                   "with C6's corner fillet (CR-C6-17)",
          inputs=dict(F_IN, rows="ASM-C3-PACK-LOADS", fc="CL-C1-PACK-CRASH-LOAD", n="ASM-D2-N-STRAPS",
                      pre="ASM-C1-STRAP-PRELOAD", hl="ASM-C3-HL", bw="ASM-D2-BAY-W", gd="ASM-C3-GUIDE",
                      s="ASM-C3-SPREAD", tb=P + "fins.board_t_m", leg="ASM-C3-FILLET-LEG"))
def straps(rows, fc, n, pre, hl, bw, gd, s, tb, leg, sf, kf, kp):
    w = 0.020
    f = max(max(r[3] for r in rows) * sf * kf * kp, fc)
    p = f / n
    t_leg = p / 2 + pre / (2 * n)
    ov = t_leg / (hl[0] * 1e4 * w)
    tray_w = bw + 2 * gd[0]
    lw = w + 2 * s
    return {"F_n": f, "per_strap_n": p, "leg_t_n": t_leg, "overlap_req_m": ov,
            "tray_flat_pa": p / (tray_w * lw), "glue_line_pa": p / (2 * lw) / tb,
            "glue_fillet_pa": p / (2 * lw) / (tb + leg)}


@kit.calc("CALC-C3-OVERHANG", title="Pod overhang ahead of the wing LE: section at x = 0",
          equation="M = n g [m_pack,ahead x_bar + sum m_i |x_i|] (pack uniform over its length at the forward stop); "
                   "section = foam-board faces only: 2 side walls (2 faces t_f x h_w) + floor bottom face (strap groove "
                   "cuts the top face); tray left out (strap slot at x 0); sigma_top = M c / I",
          inputs=dict(F_IN, n_lim="CL-C1-N-LIMIT-POS", nc="CL-C1-CRASH-N", pack_rng="ASM-A3-PACK-RANGE",
                      pack=P + "battery.size_m", px="CL-D2-PACK-X-FWD-MIN", items="ASM-C3-OVERHANG-ITEMS",
                      W="ASM-D2-POD-WIDTH", H=P + "pod.size_m", tb=P + "fins.board_t_m", tf="ASM-C4-FACE-T", g=P + "env.g_ms2"))
def overhang(n_lim, nc, pack_rng, pack, px, items, W, H, tb, tf, g, sf, kf, kp):
    x_front = px - pack[0] / 2
    frac = max(0.0, min(1.0, -x_front / pack[0]))
    m_p = max(pack_rng) / 1000 * frac
    mom = m_p * (-x_front / 2) + sum(m / 1000 * abs(x) for m, x in items)
    hw = H[2] - tb                          # side wall height: pod base to hatch underside
    parts = [(2 * 2 * tf * hw, hw / 2, 2 * 2 * tf * hw ** 3 / 12), ((W - 2 * tb) * tf, tf / 2, 0.0)]
    A = sum(p[0] for p in parts)
    zna = sum(p[0] * p[1] for p in parts) / A
    I = sum(p[2] + p[0] * (p[1] - zna) ** 2 for p in parts)
    c = hw - zna
    n_d = n_lim * sf * kf * kp
    return {"M_unit_nm_per_g": mom * g, "I_m4": I, "c_m": c, "n_design": n_d,
            "sigma_design_pa": n_d * mom * g * c / I, "sigma_crash_pa": nc * mom * g * c / I}


@kit.calc("CALC-C3-HANDLE", title="Carry handle on the spar (G1, whole aircraft at 2 g)",
          equation="F = m_gate g n_h x SF x k_fit x k_print; ties: F vs n x rating; grip: uniform hand load over the "
                   "leg span s = 2 y_leg, M = F s / 8, sigma = 6 M / (b h^2)",
          inputs=dict(F_IN, m=P + "requirements.mtow_gate_kg", g=P + "env.g_ms2", nh="ASM-C1-HANDLING-N",
                      tie="ASM-D2-TIE-CAP", nt="ASM-D2-N-TIES", grip="ASM-C3-GRIP"))
def handle(m, g, nh, tie, nt, grip, sf, kf, kp):
    f = m * g * nh * sf * kf * kp
    s = 2 * grip[2]
    return {"F_design_n": f, "tie_cap_n": nt * tie, "sigma_grip_pa": 6 * (f * s / 8) / (grip[1] * grip[0] ** 2)}


@kit.calc("CALC-C3-HATCH", title="Hatch suction at VD",
          equation="F = |Cp| q_VD A_hatch x SF x k_fit; aft half on the hook-and-loop tab: sigma = F/2 / A_tab",
          inputs={"q": "CL-C1-Q-VD", "cp": "ASM-C3-CP-HATCH", "ht": "ASM-C3-HATCH", "sf": P + "requirements.safety_factor_ult",
                  "kf": "ASM-C1-FITTING-FACTOR"})
def hatch(q, cp, ht, sf, kf):
    f = abs(cp) * q * ht[0] * ht[1] * sf * kf
    return {"F_design_n": f, "tab_n_per_cm2": f / 2 / (ht[2] * ht[3] * 1e4)}


@kit.calc("CALC-C3-MASS", title="Pod mass: C3 sizing against D2's model, and the full-section forward stop option",
          equation="dm = rho [(t_aft,rec - t_aft,D2) h_a b + (t_fwd,rec - t_fwd,D2) h_f b + 2 (t_g,rec - t_g,D2) h_g L_bay]; "
                   "m = CL-D2-MASS + dm; full-section option (CR-C5-13): + rho t_fwd b (H_bay - h_f)",
          inputs={"m0": "CL-D2-MASS", "rho": "ASM-C4-PETG-RHO", "rec": "ASM-C3-REC", "t0": "ASM-D2-STOP-T",
                  "fs": "ASM-D2-FWD-STOP", "gd": "ASM-C3-GUIDE", "h": "ASM-C3-AFT-STOP-H", "hf": "ASM-C3-STOP-H",
                  "bw": "ASM-D2-BAY-W", "bay": "CL-D2-BAY-L", "hb": "CL-D2-BAY-H"})
def mass(m0, rho, rec, t0, fs, gd, h, hf, bw, bay, hb):
    b = bw + 2 * rec[2]
    dv = (rec[0] - t0) * h * b + (rec[1] - fs[1]) * hf * b + 2 * (rec[2] - gd[0]) * rec[3] * bay
    full = rho * rec[1] * bw * (hb - hf) * 1000
    return {"dm_g": dv * rho * 1000, "mass_g": m0 + dv * rho * 1000, "full_section_dm_g": full,
            "mass_full_section_g": m0 + dv * rho * 1000 + full}


@kit.calc("CALC-C3-NOSE-PATH", title="Nose-in crush path with the D-47 nose (8.8 mm nose stack, block A ~1 mm)",
          equation="L_A = (x_fs - t_fs) - (x_le + t_b) ; per pack m (503/550/680 g): F = min(n_pack m g, sigma A_bay), "
                   "KE = m v^2/2, eff = eps_d - eps_y/2 ; block A energy E_A = min(F, sigma A_stop) eff L_A, share = E_A/KE ; "
                   "block B gap penalty of a stop of height h_f vs the full section = (min(F, sigma A_bay) - "
                   "min(F, sigma h_f b_bay)) L_A / F ; same at the D2-R3/R4 block A (ASM-D2-FWD-STOP[0]) for comparison ; "
                   "stack = t_b + L_A + t_fs",
          inputs={"x_le": P + "pod.x_le_m", "tb": P + "fins.board_t_m", "d47": "ASM-C3-D47-NOSE", "fs": "ASM-D2-FWD-STOP",
                  "rec": "ASM-C3-REC", "pack_rng": "ASM-A3-PACK-RANGE", "m_nom": P + "battery.mass_kg",
                  "v": "ASM-C1-CRASH-V", "n_pack": "ASM-C5-PACK-G-MAX", "sigma": "ASM-D5-XPS-PLATEAU",
                  "eps_d": "ASM-D5-DENSIFY", "eps_y": "ASM-D5-YIELD-STRAIN", "bw": "ASM-D2-BAY-W", "hb": "CL-D2-BAY-H",
                  "hf": "ASM-C3-STOP-H", "g": P + "env.g_ms2"})
def nose_path(x_le, tb, d47, fs, rec, pack_rng, m_nom, v, n_pack, sigma, eps_d, eps_y, bw, hb, hf, g):
    L_A = (d47[0] - rec[1]) - (x_le + tb)
    eff = eps_d - eps_y / 2
    A_bay, A_c3 = bw * hb, bw * hf
    out = {"L_A_m": L_A, "L_A_r4_m": fs[0], "stack_m": tb + L_A + rec[1]}
    share_full, share_c3, pen, pen_r4, FB = 0.0, 0.0, 0.0, 0.0, 0.0
    for m in (min(pack_rng) / 1000, m_nom, max(pack_rng) / 1000):
        F = min(n_pack * m * g, sigma * A_bay)
        KE = 0.5 * m * v * v
        FA_full, FA_c3 = min(F, sigma * A_bay), min(F, sigma * A_c3)
        share_full = max(share_full, FA_full * eff * L_A / KE)
        share_c3 = max(share_c3, FA_c3 * eff * L_A / KE)
        pen = max(pen, (FA_full - FA_c3) * L_A / F)
        pen_r4 = max(pen_r4, (FA_full - FA_c3) * fs[0] / F)
        FB = max(FB, F)
    out.update({"blockA_share_full": share_full, "blockA_share_c3": share_c3, "gap_penalty_c3_m": pen,
                "gap_penalty_c3_r4_m": pen_r4, "F_blockB_n": FB})
    return out


@kit.calc("CALC-C3-FEA", title="FEA verification of the pod load path (SU2 ELASTICITY, 4 mesh levels)",
          equation="bond design R = R_hand(full 3-D row) x R_FEA,in-plane / R_hand,in-plane (FEA concentration factor on "
                   "the hand calc's Fz, My, Fx part; d0-averaged peaks); bond crash R = max over +-x, +-z of R_FEA (d0); "
                   "overhang = wall-top face stress E_f exx at x = 0 (section fit); stops: peak principal stress at the "
                   "root fillet, tray bending peak, board flat-wise peel (paper face to core, 2 mm mean), per variant",
          inputs={"fea": "ASM-C3-FEA", "rh": "CL-C3-BOND-R-DESIGN", "d0": "ASM-C3-FEA-D0", "e_xps": "ASM-C3-XPS-E",
                  "e_petg": "ASM-C3-PETG-E", "tp": "CL-C3-ALLOW-PAPER-SHEAR"})
def fea(fea, rh, d0, e_xps, e_petg, tp):
    if not fea:
        raise ValueError("fea/fea_results.json missing: run python -I redesign/team/C3/pod_fea.py first")
    k = fea["R_design_inplane_fea"] / fea["R_design_inplane_hand"]
    out = {"k_bond_design": k, "R_design_corrected": rh * k, "R_crash_fea": fea["R_crash_fea"],
           "R_bonded_crash_fea": fea["R_bonded_crash_fea"], "overhang_crash_pa": fea["overhang_crash_fea_pa"],
           "d0_m": d0, "E_xps_pa": e_xps, "E_petg_pa": e_petg,
           "R_design_5mm": fea["R_design_5mm_fea"], "R_crash_5mm": fea["R_crash_5mm_fea"]}
    if "R_tied_design_fea" in fea:            # fix study: handle feet bonded to the pod walls (CR-C3-16)
        out.update({"R_tied_design": fea["R_tied_design_fea"], "R_tied_crash": fea["R_tied_crash_fea"],
                    "R_tied_crash_5mm": fea["R_tied_crash_5mm_fea"], "saddle_F_crash_n": fea["F_tied_saddle_crash_n"],
                    "saddle_bond_area_req_m2": fea["F_tied_saddle_crash_n"] / tp})
    if "R_fix_design_fea" in fea:
        out.update({"R_stepgap_design": fea["R_fix_design_fea"], "R_stepgap_crash": fea["R_fix_crash_fea"]})
    for v in ("AFT_FILLET_SOLID", "AFT_FILLET_WIN", "AFT_HEEL_FILLET", "AFT_PROPPED_WIN", "FWD_FILLET", "FWD_BEDDED"):
        for q in ("stop_peak_pa", "tray_peak_pa", "peel_pa", "wall_face_peak_pa", "bed_peel_peak_pa", "tray_path_share"):
            if q in fea[v]:
                out["%s_%s" % (v.lower(), q)] = fea[v][q]
    return out


@kit.calc("CALC-C3-FEA-R4", title="C3-R4 FEA: forward-stop T as drawn (D-69), recess-step fillet (CR-C3-17), bracket loads",
          equation="from ASM-C3-FEA (pod_fea.py parts m2f, m1tfl, m1tf, m1tg; each value the finest level or the "
                   "Richardson extrapolation if larger with p > 0.5). Stop T (M2F, plane strain, pack crash load "
                   "CALC-C3-STOPS F_fwd on the bay + guides width): board flat-wise peel on both paper-face-to-core "
                   "planes and core shear (2 mm means), upright / flange section-linearised stress; nose wall face peel "
                   "behind the 1 mm bed. Fillet (M1, feet tied, wall edges not credited): wing-side bond R = sigma+/"
                   "100 kPa + |tau|/100 kPa (2 mm mean), floor-bevel-on-fillet R on the board core (foam allowables). "
                   "Fail-safe: the same with the floor end released (M1_TIED_STEPGAP). Bracket proof (CR-H1-23): "
                   "F_limit = |F_saddle(design row)| / (sf ff pf) from M1_TIED_FOOTPRINT; crash = max over +-x, +-z",
          inputs={"fea": "ASM-C3-FEA"})
def fea_r4(fea):
    out = {}
    for v, tag in (("FWD_FLANGE_BED_HELD", "t_bed"), ("FWD_FLANGE_BED_BOX", "t_bed_box"), ("FWD_FLANGE_HELD", "t_nobed"),
                   ("FWD_FLANGE_BOX", "t_nobed_box")):
        if v in fea:
            for q in ("upright_lin_pa", "flange_lin_pa", "peel_peak_d0_pa", "shear_peak_d0_pa", "wall_peel_d0_pa",
                      "wall_shear_d0_pa", "bed_peel_d0_pa"):
                if q in fea[v]:
                    out["%s_%s" % (tag, q)] = fea[v][q]
    for k in ("R_fil_design_fea", "R_fil_crash_up_fea", "R_fil_crash_fea", "R_fil_crash_dn_5mm", "R_fil_ff_design_mean",
              "R_fix_crash_dn_fea", "R_fix_crash_mx_fea", "R_tied_crash_up_fea", "R_tied_crash_px_fea",
              "R_tied_crash_dn_fea", "R_tied_crash_mx_fea", "R_design_inplane_fea", "R_tied_design_fea",
              "F_tied_saddle_limit_n", "F_tied_saddle_limit_x_n", "F_tied_saddle_limit_z_n", "F_tied_saddle_crash_max_n",
              "R_scarf15_ff_design_mean", "R_scarf15_crash_up_fea"):
        if k in fea:
            out[k] = fea[k]
    # fail-safe crash: worst of (intact holds) or (released holds) per direction, the -z and -x peel first
    out["R_crash_failsafe"] = max(min(fea["R_tied_crash_dn_fea"], fea["R_fix_crash_dn_fea"]),
                                  min(fea["R_tied_crash_mx_fea"], fea["R_fix_crash_mx_fea"]),
                                  fea["R_tied_crash_up_fea"], fea["R_tied_crash_px_fea"])
    return out


@kit.calc("CALC-C3-STRUT", title="Aft-stop strut to the handle foot bridge (CR-C3-14 fix)",
          equation="rib bearing sigma = F / (n t h); Euler per rib (pinned, conservative) pi^2 E (h t^3 / 12) / L^2, "
                   "x n; bridge: F vs the 2 spar ties (+x along the spar); mass = rho (n t h L + w_p h t_p)",
          inputs={"F": "CL-C3-AFT-STOP-BOND", "st": "ASM-C3-STRUT", "E": "ASM-C3-PETG-E", "cap": "CL-C3-HANDLE-TIE-CAP"})
def strut(F, st, E, cap):
    L, n, t, h, wp, tp = st
    I = h * t ** 3 / 12
    return {"sigma_bearing_pa": F / (n * t * h), "P_cr_n": n * math.pi ** 2 * E * I / L ** 2, "F_n": F,
            "tie_cap_n": cap, "L_m": L, "mass_g": 1270.0 * (n * t * h * L + wp * h * tp) * 1000}


# ---------------------------------------------------------------- claims
SHELL, TRAY, STRAP, HANDLE, HATCH = "POD-001", "POD-002", "POD-004", "POD-007", "POD-003"
_FEA_HOW = "Re-run python -I redesign/team/C3/pod_fea.py (SU2 + gmsh, 4 levels); then "
kit.claim("CL-C3-FEA-BOND-R-DESIGN", "Pod-to-wing bond interaction, design, hand calc x FEA concentration factor",
          calc="CALC-C3-FEA", output="R_design_corrected", parts=[SHELL, "WNG-001"],
          how=_FEA_HOW + "record only.",
          note="SUPERSEDED (C3-R4): pod without the D-69 wall brackets (not built); the built pod is "
               "CL-C3-FEA-TIED-R-DESIGN / CL-C3-FEA-STEP-R-DESIGN. Kept without a limit as the record of why the "
               "brackets exist")
kit.claim("CL-C3-FEA-BOND-R-CRASH", "Pod-to-wing bond interaction, 12.75 g crash in the x-z plane (FEA)",
          calc="CALC-C3-FEA", output="R_crash_fea", parts=[SHELL, "WNG-001"], how=_FEA_HOW + "record only.",
          note="SUPERSEDED (C3-R4): pod without the D-69 brackets (not built); retention of the built pod is "
               "CL-C3-FEA-CRASH-FAILSAFE. +-x, +-z at the A3 group CG, 680 g pack most forward")
kit.claim("CL-C3-FEA-BOND-R-DESIGN-5MM", "Pod-to-wing bond interaction, design, FEA peak averaged over 5 mm (reference)",
          calc="CALC-C3-FEA", output="R_design_5mm", parts=[SHELL, "WNG-001"], how=_FEA_HOW + "T-C3-POD-PROOF.",
          note="no limit: shows the failure is not an artefact of the 2 mm averaging length (converged, GCI < 1 %)")
kit.claim("CL-C3-FEA-TIED-R-DESIGN", "Bond interaction, design, with the handle feet bonded to the pod walls (CR-C3-16)",
          calc="CALC-C3-FEA", output="R_tied_design", limit=("<=", 1.0), verifies=["R-STRUCT-MARGIN"],
          parts=[SHELL, HANDLE, "WNG-001"], how=_FEA_HOW + "T-C3-POD-PROOF on the pod built with the brackets.",
          note="fix study, 3 mesh levels; feet smeared as PETG over 48 of the 140 mm model depth; wall edges aft of the "
               "recess not bonded")
kit.claim("CL-C3-FEA-TIED-R-CRASH", "Bond interaction, 12.75 g crash, with the feet bonded to the walls (CR-C3-16)",
          calc="CALC-C3-FEA", output="R_tied_crash", parts=[SHELL, HANDLE, "WNG-001"],
          how=_FEA_HOW + "post-crash inspection of the aft bond line.",
          note="intact-bond peak, no limit since C3-R4: +z 0.95, +x 0.20 hold; -z and -x peel the bond end at the "
               "TOP of the recess step (x 0.065, z 0.0197; 5 mm mean converges to 3.6, so it is a real local peel, "
               "not only a singularity). CR-C3-17's fillet sits at the bottom corner and does not reach it (4.43 with "
               "it). Retention is CL-C3-FEA-CRASH-FAILSAFE")
kit.claim("CL-C3-FEA-SADDLE-TIES", "Pod force into the handle feet in the crash vs the 2 spar ties (CR-C3-16)",
          calc="CALC-C3-FEA", output="saddle_F_crash_n", unit="N", limit=("<=", "CL-C3-HANDLE-TIE-CAP"),
          verifies=["R-PACK-RETENTION"], parts=[HANDLE, "WNG-002"],
          how="T-C3-BRACKET-CRASH on a test article to the crash force (CR-H1-23: a crash load does not go on the "
              "flight pod); the flight pod sees CL-C3-BRACKET-PROOF-LIMIT in T-C3-POD-PROOF.")
kit.claim("CL-C3-FEA-SADDLE-BOND-AREA", "Bracket bond area needed, handle feet to pod walls (paper face shear)",
          calc="CALC-C3-FEA", output="saddle_bond_area_req_m2", unit="m2", parts=[HANDLE, SHELL],
          how="D2 draws >= this area per aircraft (both brackets together); T-C3-BOND-COUPON paper lap shear.")
kit.claim("CL-C3-FEA-BOND-WALL-EDGE", "Side-wall edge bonds aft of the recess end, crash peak interaction (reference)",
          calc="CALC-C3-FEA", output="R_bonded_crash_fea", parts=[SHELL, "WNG-001"],
          how=_FEA_HOW + "inspect the wall-edge bond lines after T-C3-POD-PROOF.",
          note="no limit: the 4.8 mm wall edges over the spar attract load as drawn and may peel locally; the footprint "
               "variant (CL-C3-FEA-BOND-R-*) shows the bond holds without them")
kit.claim("CL-C3-FEA-OVERHANG-CRASH", "Overhang wall-top face stress at the LE, 12.75 g crash (FEA)", calc="CALC-C3-FEA",
          output="overhang_crash_pa", unit="Pa", limit=("<=", "ASM-C4-FACE-SIGMA"), verifies=["R-PACK-RETENTION"],
          parts=[SHELL], how=_FEA_HOW + "T-C3-POD-PROOF to 12.75 x pack weight.")
kit.claim("CL-C3-FEA-AFT-STOP-PEAK", "Aft stop as drawn (+2 mm fillet), root peak principal stress, design (FEA)",
          calc="CALC-C3-FEA", output="aft_fillet_solid_stop_peak_pa", unit="Pa", limit=("<=", "ASM-C4-PETG-TENSILE"),
          verifies=["R-PACK-RETENTION"], parts=[TRAY], how=_FEA_HOW + "T-C3-STOP-PUSH on the built tray rear piece.",
          note="solid tray section (best case); the 1 mm tray rotates under the stop, so the root is the tray, not the stop")
kit.claim("CL-C3-FEA-AFT-TRAY-BEND", "Tray rear piece bending under the aft stop root moment, design (FEA)",
          calc="CALC-C3-FEA", output="aft_fillet_solid_tray_peak_pa", unit="Pa", limit=("<=", "ASM-C3-PETG-INPLANE"),
          verifies=["R-PACK-RETENTION"], parts=[TRAY], how=_FEA_HOW + "T-C3-STOP-PUSH.")
kit.claim("CL-C3-FEA-AFT-PEEL", "Board flat-wise peel under the aft stop, design (FEA, 2 mm mean)", calc="CALC-C3-FEA",
          output="aft_fillet_solid_peel_pa", unit="Pa", limit=("<=", "CL-C3-ALLOW-BOARD-FLAT"),
          verifies=["R-PACK-RETENTION"], parts=[TRAY, SHELL], how=_FEA_HOW + "T-C3-STOP-PUSH on a tray bonded to board.")
kit.claim("CL-C3-FEA-AFT-PROP-PEEL", "Board peel with the aft stop strutted to the handle bridge (CR-C3-14, FEA)",
          calc="CALC-C3-FEA", output="aft_propped_win_peel_pa", unit="Pa", limit=("<=", "CL-C3-ALLOW-BOARD-FLAT"),
          verifies=["R-PACK-RETENTION"], parts=[TRAY, HANDLE], how=_FEA_HOW + "T-C3-STOP-PUSH with the strut fitted.",
          note="fix candidate; strut idealised as rigid on the stop back face, z 0.026-0.040")
kit.claim("CL-C3-FEA-AFT-PROP-PEAK", "Aft stop root peak with the strut (CR-C3-14, FEA)", calc="CALC-C3-FEA",
          output="aft_propped_win_stop_peak_pa", unit="Pa", limit=("<=", "ASM-C4-PETG-TENSILE"),
          verifies=["R-PACK-RETENTION"], parts=[TRAY], how=_FEA_HOW + "T-C3-STOP-PUSH with the strut fitted.")
kit.claim("CL-C3-FEA-AFT-HEEL-PEEL", "Board peel with a 2 mm heel under the aft stop (option, FEA)", calc="CALC-C3-FEA",
          output="aft_heel_fillet_peel_pa", unit="Pa", limit=("<=", "CL-C3-ALLOW-BOARD-FLAT"), parts=[TRAY],
          how=_FEA_HOW + "not adopted.", note="option studied and rejected: the heel fixes the PETG but not the peel")
kit.claim("CL-C3-FEA-FWD-PEEL", "Board peel under the forward stop as a cantilever, 85 N crash (FEA)", calc="CALC-C3-FEA",
          output="fwd_fillet_peel_pa", unit="Pa", parts=[TRAY, SHELL], how=_FEA_HOW + "record only.",
          note="SUPERSEDED (C3-R4): the stop printed with the tray (pre-D-69) is not built; D-69's T is checked by "
               "CL-C3-FEA-FWD-T-*. Kept without a limit as the record of why D-69 exists")
kit.claim("CL-C3-FEA-FWD-BED-PEEL", "Board peel under the forward stop with the 1 mm bed to the nose wall, 85 N (FEA)",
          calc="CALC-C3-FEA", output="fwd_bedded_peel_pa", unit="Pa", parts=[TRAY, SHELL],
          how=_FEA_HOW + "record only.",
          note="SUPERSEDED (C3-R4): D2-R5's stop on the tray with the bed is not built; D-69's T with its flange and "
               "the bed is CL-C3-FEA-FWD-T-PEEL. Kept without a limit as the record")
kit.claim("CL-C3-STRUT-BEARING", "Aft-stop strut bearing stress, design (CR-C3-14)", calc="CALC-C3-STRUT",
          output="sigma_bearing_pa", unit="Pa", limit=("<=", "ASM-C4-PETG-TENSILE"), verifies=["R-PACK-RETENTION"],
          parts=[TRAY, HANDLE], how="T-C3-STOP-PUSH with the strut fitted.",
          note="compression, checked against the across-layer tension allowable (conservative)")
kit.claim("CL-C3-STRUT-BUCKLE", "Aft-stop strut Euler load vs the design stop load (CR-C3-14)", calc="CALC-C3-STRUT",
          output="P_cr_n", unit="N", limit=(">=", "CL-C3-AFT-STOP-BOND"), verifies=["R-PACK-RETENTION"],
          parts=[HANDLE], how="T-C3-STOP-PUSH with the strut fitted.")
kit.claim("CL-C3-STRUT-BRIDGE", "Stop load into the handle foot bridge vs the 2 spar ties (CR-C3-14)", calc="CALC-C3-STRUT",
          output="F_n", unit="N", limit=("<=", "CL-C3-HANDLE-TIE-CAP"), verifies=["R-PACK-RETENTION"],
          parts=[HANDLE, "WNG-002"], how="T-D2-HANDLE-PULL repeated along +x (90 N, 10 s), no slip on the spar.",
          note="the feet are also epoxied to the spar saddle; ties alone are the conservative path")
kit.claim("CL-C3-FEA-FWD-TRAY-BEND", "Tray front piece bending under the forward stop, 85 N crash (FEA)",
          calc="CALC-C3-FEA", output="fwd_fillet_tray_peak_pa", unit="Pa", parts=[TRAY], how=_FEA_HOW + "record only.",
          note="SUPERSEDED (C3-R4): since D-69 the tray front piece does not carry the stop (the T is its own body, "
               "CL-C3-FEA-FWD-T-UPRIGHT / -FLANGE)")
# ---------------------------------------------------------------- C3-R4 (2026-11-13): D-69 drawings checked by FEA
_R4 = "Re-run python -I redesign/team/C3/pod_fea.py --part m2f / m1tf / m1tfl / m1tg, then --combine; "
kit.claim("CL-C3-FEA-FWD-T-PEEL", "Forward-stop T as drawn (D-69) with the 1 mm bed: board flat-wise peel, pack crash "
          "load (FEA, 2 mm mean)", calc="CALC-C3-FEA-R4", output="t_bed_peel_peak_d0_pa", unit="Pa",
          limit=("<=", "CL-C3-ALLOW-BOARD-FLAT"), verifies=["R-PACK-RETENTION"], parts=[TRAY, SHELL],
          how=_R4 + "T-C3-STOP-PUSH in -x on a built nose (T, flange, floor, 1 mm bed, nose-wall offcut).",
          note="floor underside held aft of the flange (C3 M2 rule); the floor-strip-alone bound (BOX) puts 59.6 kPa at "
               "the tray front piece's window edge, 30 mm aft, which the nose box (walls, bed) does not let happen")
kit.claim("CL-C3-FEA-FWD-T-CORE-SHEAR", "Forward-stop T with the bed: board core shear under the paper faces (FEA)",
          calc="CALC-C3-FEA-R4", output="t_bed_shear_peak_d0_pa", unit="Pa", limit=("<=", "CL-C3-ALLOW-PAPER-SHEAR"),
          verifies=["R-PACK-RETENTION"], parts=[TRAY, SHELL], how=_R4 + "T-C3-STOP-PUSH (-x, with the bed).",
          note="held-floor bound: the whole stop force crosses the core within 36 mm; the BOX bound gives 59 kPa")
kit.claim("CL-C3-FEA-FWD-T-UPRIGHT", "Forward-stop T upright, section-linearised stress, with the bed (FEA)",
          calc="CALC-C3-FEA-R4", output="t_bed_upright_lin_pa", unit="Pa", limit=("<=", "ASM-C4-PETG-TENSILE"),
          verifies=["R-PACK-RETENTION"], parts=[TRAY], how=_R4 + "T-C3-STOP-PUSH.")
kit.claim("CL-C3-FEA-FWD-T-FLANGE", "Forward-stop T flange at the upright, section-linearised stress, with the bed (FEA)",
          calc="CALC-C3-FEA-R4", output="t_bed_flange_lin_pa", unit="Pa", limit=("<=", "ASM-C4-PETG-TENSILE"),
          verifies=["R-PACK-RETENTION"], parts=[TRAY], how=_R4 + "T-C3-STOP-PUSH.")
kit.claim("CL-C3-FEA-FWD-T-WALL-SHEAR", "Nose wall behind the bed: core shear under its inner paper face (FEA)",
          calc="CALC-C3-FEA-R4", output="t_bed_wall_shear_d0_pa", unit="Pa", limit=("<=", "CL-C3-ALLOW-PAPER-SHEAR"),
          verifies=["R-PACK-RETENTION"], parts=[SHELL], how=_R4 + "T-C3-STOP-PUSH with the nose-wall offcut.",
          note="wall foot held (in 3-D it stands on the floor outside the 54 mm notch); face peel there 0.3 kPa")
kit.claim("CL-C3-FEA-FWD-T-BED", "1 mm microballoon bed between the T and the nose wall: tension across it (FEA)",
          calc="CALC-C3-FEA-R4", output="t_bed_bed_peel_d0_pa", unit="Pa", limit=("<=", "ASM-C6-PEEL"),
          verifies=["R-PACK-RETENTION"], parts=[TRAY, SHELL], how="BUILD.md step 9 inspection: no void behind the stop.")
kit.claim("CL-C3-FEA-FWD-T-PEEL-NOBED", "Forward-stop T without the bed (record: why BUILD.md step 9 is structural)",
          calc="CALC-C3-FEA-R4", output="t_nobed_peel_peak_d0_pa", unit="Pa", parts=[TRAY, SHELL],
          how=_R4 + "no test: the bed is a hold point.",
          note="no limit: fails the 50 kPa board allowable at the tray / upright notch; the bed takes the moment")
kit.claim("CL-C3-FEA-STEP-R-DESIGN", "Pod-to-wing bond, design, square floor end on the recess step, feet tied (FEA)",
          calc="CALC-C3-FEA-R4", output="R_tied_design_fea", limit=("<=", 1.0), verifies=["R-STRUCT-MARGIN"],
          parts=[SHELL, "WNG-001"], how=_R4 + "T-C3-POD-PROOF on the built pod.",
          note="C3-R4 recommends the square floor end (no WNG-007 fillet, no bevel); the board end's bond is the same "
               "line, so it carries this R on the C6 foam allowables")
kit.claim("CL-C3-FEA-CRASH-FAILSAFE", "Pod retention in the 12.75 g crash, per direction: intact bond or, after the "
          "aft-end peel, the released aft end (FEA)", calc="CALC-C3-FEA-R4", output="R_crash_failsafe", limit=("<=", 1.0),
          verifies=["R-PACK-RETENTION"], parts=[SHELL, HANDLE, "WNG-001"],
          how=_R4 + "T-C3-POD-PROOF on a test pod (not the flight pod) to the crash loads; post-crash inspection of "
              "the aft bond line.",
          note="-z and -x peel the step-top bond end locally (intact R 4.4 / 1.9, a bond termination that no corner "
               "fillet reaches); the released aft end then holds (M1_TIED_STEPGAP -z 0.43, -x 0.87); +z and +x hold "
               "intact (0.95, 0.20)")
kit.claim("CL-C3-FEA-FILLET-FF-DESIGN", "With the WNG-007 fillet as drawn: floor bevel on the fillet, design, mean R over "
          "the bevel on the board core (record)", calc="CALC-C3-FEA-R4", output="R_fil_ff_design_mean",
          parts=[SHELL, "WNG-007"], how=_R4 + "not adopted.",
          note="no limit: the 45 deg bevel turns the floor end's bearing on the step into shear on the bond (mean "
               "R 1.2 over the whole face); the fillet does not lower the crash peak at the step top either (4.43 vs "
               "4.50). C3-R4 asks D1/D2 to delete WNG-007 and the floor bevel (square end, as R3)")
kit.claim("CL-C3-BRACKET-PROOF-LIMIT", "Handle-bracket force at limit, design row / (1.5 x 1.15 x 1.25): the proof load "
          "on the flight pod (CR-H1-23)", calc="CALC-C3-FEA-R4", output="F_tied_saddle_limit_n", unit="N",
          parts=[HANDLE, SHELL], how="T-C3-POD-PROOF (flight pod): pull the brackets to this load along +x and -z "
                                     "components (CL-C3-BRACKET-PROOF-LIMIT-X/-Z), 10 s, then inspect; stop at limit.")
kit.claim("CL-C3-BRACKET-PROOF-LIMIT-X", "Handle-bracket limit force, +x component (CR-H1-23)", calc="CALC-C3-FEA-R4",
          output="F_tied_saddle_limit_x_n", unit="N", parts=[HANDLE, SHELL], how="T-C3-POD-PROOF (flight pod).")
kit.claim("CL-C3-BRACKET-PROOF-LIMIT-Z", "Handle-bracket limit force, -z component (CR-H1-23)", calc="CALC-C3-FEA-R4",
          output="F_tied_saddle_limit_z_n", unit="N", parts=[HANDLE, SHELL], how="T-C3-POD-PROOF (flight pod).")
kit.claim("CL-C3-BRACKET-CRASH-F", "Handle-bracket crash force, worst of +-x, +-z (test article only, CR-H1-23)",
          calc="CALC-C3-FEA-R4", output="F_tied_saddle_crash_max_n", unit="N", parts=[HANDLE, SHELL],
          how="T-C3-BRACKET-CRASH on a test article: one printed foot + bracket epoxied to a foam-board wall offcut "
              "(1 232 mm2 flange) and to a spar stub; pull to this force along +x, then a second article along -z.")
kit.claim("CL-C3-BOND-R-DESIGN", "Pod-to-wing bond interaction, flight/ground envelope (design)", calc="CALC-C3-BOND",
          output="R_design", limit=("<=", 1.0), verifies=["R-STRUCT-MARGIN"], parts=[SHELL, "WNG-001"],
          how="T-C3-BOND-COUPON (allowables) then T-C3-POD-PROOF (built pod, 1.5 x limit).",
          note="footprint is the LE filler + recess floor only (x 0 ... recess end, full width); walls left out")
kit.claim("CL-C3-BOND-SIGMA-DESIGN", "Pod-to-wing bond peak tension (design)", calc="CALC-C3-BOND", output="sigma_design_pa",
          unit="Pa", limit=("<=", "ASM-D2-XPS-ALLOW"), verifies=["R-STRUCT-MARGIN"], parts=[SHELL, "WNG-001"],
          how="As CL-C3-BOND-R-DESIGN.")
kit.claim("CL-C3-BOND-R-CRASH", "Pod-to-wing bond interaction, 12.75 g crash any axis", calc="CALC-C3-BOND",
          output="R_crash", limit=("<=", 1.0), verifies=["R-PACK-RETENTION"], parts=[SHELL, "WNG-001"],
          how="T-C3-POD-PROOF: crash-direction pulls on the built pod with a 680 g dummy pack.")
kit.claim("CL-C3-POD-GROUP-MASS", "Pod group mass, heaviest pack (crash case)", calc="CALC-C3-BOND", output="group_mass_kg",
          unit="kg", parts=[SHELL], how="Weigh the pod group with the 680 g listing pack.")
kit.claim("CL-C3-AFT-STOP-D2", "Aft stop as modelled by D2 (ASM-D2-STOP-T): root bending stress, design", calc="CALC-C3-STOPS",
          output="sigma_aft_d2_pa", unit="Pa", limit=("<=", "ASM-C4-PETG-TENSILE"), verifies=["R-PACK-RETENTION"],
          parts=[TRAY], how="T-C3-STOP-PUSH on a printed tray: 89 N on a 680 g-pack-size block at 13 mm height.",
          note="D2-R5: printed with the tray rear piece at x 0.056; 2 gussets behind it ignored (conservative)")
kit.claim("CL-C3-AFT-STOP-BOND", "Aft stop design load vs D2's tray rear piece bond (stop on the tray since D-47)",
          calc="CALC-C3-STOPS", output="F_aft_n", unit="N", limit=("<=", "CL-D2-AFT-STOP-BOND"),
          verifies=["R-PACK-RETENTION"], parts=[TRAY, SHELL],
          how="T-C3-STOP-PUSH on the built tray rear piece: 90 N at 13 mm height, no peel at the piece ends.",
          note="D2-R5 moved the stop off the spar bridge onto the tray rear piece (x 0.056) with 2 gussets; root moment "
               "F h/2 = 1.2 N m peels the piece ends, covered by the push test")
kit.claim("CL-C3-AFT-STOP-T-REQ", "Aft stop thickness required", calc="CALC-C3-STOPS", output="t_req_m", unit="m",
          parts=[TRAY], how="Recompute after T-C3-STOP-PUSH sets the printed-PETG allowable.")
kit.claim("CL-C3-AFT-STOP-REC", "Aft stop 3.0 mm (C3): root bending stress, design", calc="CALC-C3-STOPS",
          output="sigma_aft_rec_pa", unit="Pa", limit=("<=", "ASM-C4-PETG-TENSILE"), verifies=["R-PACK-RETENTION"],
          parts=[TRAY], how="T-C3-STOP-PUSH.")
kit.claim("CL-C3-NOSE-WALL-M", "Foam-board nose wall as the forward stop: moment needed per mm (85 N crash)",
          calc="CALC-C3-STOPS", output="nose_m_req_nmm_per_mm", unit="N mm/mm",
          parts=[SHELL],
          how="Push a pack-size block into a built nose wall to 85 N; expect failure (the printed forward stop replaces it).",
          note="reference, no limit: capacity sigma_f t_f (t - t_f) = 4.7 N mm/mm (ASM-C4-FACE-*) is ~1/10 of the need, "
               "which is why the printed forward stop exists (adopted by D2, fwd_stop_m); the wall carries pack load only "
               "when the ground backs it in a nose-in impact")
kit.claim("CL-C3-FWD-STOP-REC", "Forward stop 3.0 mm printed with the tray (C3): root bending stress",
          calc="CALC-C3-STOPS", output="sigma_fwd_rec_pa", unit="Pa", limit=("<=", "ASM-C4-PETG-TENSILE"),
          verifies=["R-PACK-RETENTION"], parts=[TRAY], how="T-C3-STOP-PUSH in -x.")
kit.claim("CL-C3-GUIDE-D2", "Bay guide as modelled by D2 (guide_t_m): bending stress, lateral crash", calc="CALC-C3-GUIDES",
          output="sigma_d2_pa", unit="Pa", limit=("<=", "ASM-C4-PETG-TENSILE"), verifies=["R-PACK-RETENTION"], parts=[TRAY],
          how="T-C3-STOP-PUSH sideways, 85 N along the guide.")
kit.claim("CL-C3-GUIDE-REC", "Bay guide 1.5 mm (C3): bending stress, lateral crash", calc="CALC-C3-GUIDES",
          output="sigma_rec_pa", unit="Pa", limit=("<=", "ASM-C4-PETG-TENSILE"), verifies=["R-PACK-RETENTION"], parts=[TRAY],
          how="T-C3-STOP-PUSH sideways.")
kit.claim("CL-C3-STRAP-LEG", "Strap leg tension, +z crash incl. preload", calc="CALC-C3-STRAPS", output="leg_t_n", unit="N",
          limit=("<=", "ASM-D2-STRAP-CAP"), verifies=["R-PACK-RETENTION"], parts=[STRAP],
          how="T-D2-STRAP-PULL (one loop to 2 x 85 N covers it).")
kit.claim("CL-C3-STRAP-OVERLAP-REQ", "Hook-and-loop overlap needed per strap", calc="CALC-C3-STRAPS", output="overlap_req_m",
          unit="m", limit=("<=", "ASM-C3-STRAP-OVERLAP"), verifies=["R-PACK-RETENTION"], parts=[STRAP],
          how="T-D2-STRAP-PULL with the 50 mm overlap marked.")
kit.claim("CL-C3-TRAY-FLAT", "Tray-to-floor bond flat-wise tension under one strap", calc="CALC-C3-STRAPS",
          output="tray_flat_pa", unit="Pa", limit=("<=", "CL-C3-ALLOW-BOARD-FLAT"), verifies=["R-PACK-RETENTION"], parts=[TRAY, SHELL],
          how="T-C3-BOND-COUPON flat-wise on board.")
kit.claim("CL-C3-FLOOR-GLUE", "Floor-to-side-wall glue line under the front strap, board edge only (reference)",
          calc="CALC-C3-STRAPS", output="glue_line_pa", unit="Pa", parts=[SHELL],
          how="T-C6-BOARD-CORNER without the fillet.",
          note="no limit: as drawn before CR-C6-17 it exceeds C6's 100 kPa paper allowable (C6 CL-C6-POD-FLOOR-RF 0.90); "
               "C6 reads this value, CL-C3-FLOOR-GLUE-FILLET is the flown check")
kit.claim("CL-C3-FLOOR-GLUE-FILLET", "Floor-to-side-wall glue line under the front strap, with the 6 mm corner fillet",
          calc="CALC-C3-STRAPS", output="glue_fillet_pa", unit="Pa", limit=("<=", "CL-C3-ALLOW-PAPER-SHEAR"),
          verifies=["R-PACK-RETENTION"], parts=[SHELL], how="T-C6-BOARD-CORNER with the fillet; T-C3-POD-PROOF +z pull.")
kit.claim("CL-C3-OVERHANG-DESIGN", "Overhang root (x = 0) wall-top face stress, flight design", calc="CALC-C3-OVERHANG",
          output="sigma_design_pa", unit="Pa", limit=("<=", "ASM-C4-FACE-SIGMA"), verifies=["R-STRUCT-MARGIN"], parts=[SHELL],
          how="T-C3-POD-PROOF: wing held at the spar, 7.3 x pack weight down on the pack.")
kit.claim("CL-C3-OVERHANG-CRASH", "Overhang root (x = 0) wall-top face stress, 12.75 g crash", calc="CALC-C3-OVERHANG",
          output="sigma_crash_pa", unit="Pa", limit=("<=", "ASM-C4-FACE-SIGMA"), verifies=["R-PACK-RETENTION"], parts=[SHELL],
          how="T-C3-POD-PROOF to 12.75 x pack weight.")
kit.claim("CL-C3-HANDLE-TIES", "Carry-handle design load (G1) vs 2 spar ties", calc="CALC-C3-HANDLE", output="F_design_n",
          unit="N", limit=("<=", "CL-C3-HANDLE-TIE-CAP"), verifies=["R-STRUCT-MARGIN"], parts=[HANDLE, "WNG-002"],
          how="T-D2-HANDLE-PULL (120 N, 10 s) proves 1.1 x this.")
kit.claim("CL-C3-HANDLE-TIE-CAP", "Spar ties capacity (2 x 222 N)", calc="CALC-C3-HANDLE", output="tie_cap_n", unit="N",
          parts=[HANDLE], how="Tie catalogue rating; T-D2-HANDLE-PULL.")
kit.claim("CL-C3-GRIP", "Carry-handle grip bending stress (along raster)", calc="CALC-C3-HANDLE", output="sigma_grip_pa",
          unit="Pa", limit=("<=", "ASM-C3-PETG-INPLANE"), verifies=["R-STRUCT-MARGIN"], parts=[HANDLE],
          how="T-D2-HANDLE-PULL; print the handle lying flat so the grip runs along the layers.")
kit.claim("CL-C3-HATCH-TAB", "Hatch latch tab tension at VD suction (design)", calc="CALC-C3-HATCH", output="tab_n_per_cm2",
          unit="N/cm2", limit=("<=", 2.5), parts=[HATCH], how="Spring scale on the closed hatch centre: >= 2 x F_design/2 before it opens.",
          note="limit = ASM-C3-HL flat-wise 2.5 N/cm2")
kit.claim("CL-C3-POD-MASS-REC", "Pod mass with the C3 sizing (D2 model + any C3 delta)", calc="CALC-C3-MASS", output="mass_g", unit="g",
          limit=("<=", P + "mass.allocation_g.pod"), verifies=["R-MASS-ALLOC"], parts=[TRAY], how="T-D2-WEIGH.")

kit.claim("CL-C3-ALLOW-XPS-SHEAR", "Epoxy-to-XPS shear allowable (C6)", calc="CALC-C3-ALLOW", output="xps_shear_pa",
          unit="Pa", how="T-C6-XPS-PULL shear coupons.")
kit.claim("CL-C3-ALLOW-PAPER-SHEAR", "Epoxy on foam-board paper face, shear allowable (C6)", calc="CALC-C3-ALLOW",
          output="paper_shear_pa", unit="Pa", how="T-C6-BOARD-LAP.")
kit.claim("CL-C3-ALLOW-BOARD-FLAT", "Foam-board flat-wise tension allowable (C6)", calc="CALC-C3-ALLOW",
          output="board_flat_pa", unit="Pa", how="T-C6-BOARD-LAP flat-wise pulls.")
kit.claim("CL-C3-FWD-STOP-FUSE", "Forward stop root capacity (fuse) vs the 85 N crash pack load", calc="CALC-C3-STOPS",
          output="fwd_fuse_n", unit="N", limit=(">=", "CL-C1-PACK-CRASH-LOAD"), verifies=["R-PACK-RETENTION"],
          parts=[TRAY], how="T-C3-STOP-PUSH in -x to failure.",
          note="holds every airframe-decelerated case (pack load <= 12.75 g); in a nose-in impact it is backed by the "
               "nose wall and the ground, so the fuse no longer has to break (block A ~1 mm, CALC-C3-NOSE-PATH)")
kit.claim("CL-C3-NOSE-BLOCK-A", "Block A length left by the D-47 nose stack", calc="CALC-C3-NOSE-PATH", output="L_A_m",
          unit="m", parts=[SHELL, "POD-008"], how="Rule from the nose wall inside face to the forward stop fore face.",
          note="7.0 mm at D2-R4 -> 1.0 mm at D-47: too thin to cut from XPS; C3 asks D2 to fill it with the "
               "stop-to-nose-wall epoxy bed (CR-C3-08)")
kit.claim("CL-C3-NOSE-STACK", "Nose stack (wall + block A + forward stop) at D-47", calc="CALC-C3-NOSE-PATH",
          output="stack_m", unit="m", parts=[SHELL], how="D2 CAD read-out.", note="D-47 states 8.8 mm")
kit.claim("CL-C3-BLOCK-A-SHARE", "Share of the nose-in pack energy block A can take (full-section stop, worst pack)",
          calc="CALC-C3-NOSE-PATH", output="blockA_share_full", unit="-", limit=("<=", 0.10),
          verifies=["R-PACK-RETENTION"], parts=["POD-008"],
          how="C5 CALC-C5-CRASH re-run on the D-47 bay.",
          note="<= 10 % means block B (removable, behind the spreader) carries the crush path alone; the shorter nose "
               "block keeps the path, it only drops block A's contribution")
kit.claim("CL-C3-STOP-SECTION-PENALTY", "Block B length a 25 mm stop costs vs a full-section stop (D-47, worst pack)",
          calc="CALC-C3-NOSE-PATH", output="gap_penalty_c3_m", unit="m", limit=("<=", 0.001),
          verifies=["R-PACK-RETENTION"], parts=[TRAY, "POD-008"],
          how="C5 CL-C5-PACK-ROOM-C3-STOP re-run on the D-47 bay.",
          note="limit 1 mm: below it the full-section stop (CR-C5-13, +6 g) buys nothing worth its mass; was ~3.8 mm "
               "with block A 7 mm")
kit.claim("CL-C3-BLOCK-B-FORCE", "Block B crush force the forward stop and nose wall react (worst pack)",
          calc="CALC-C3-NOSE-PATH", output="F_blockB_n", unit="N", parts=["POD-008", SHELL],
          how="Block coupon crush force x bay section (T-D5-COUPON method).",
          note="far above the stop fuse: reacted only when the nose wall is backed by the ground (nose-in); in any "
               "other crash the pack load is <= 85 N and the stop holds it")
kit.claim("CL-C3-POD-MASS-FULL-STOP", "Pod mass with the full-section forward stop (CR-C5-13 option)", calc="CALC-C3-MASS",
          output="mass_full_section_g", unit="g", parts=[TRAY],
          how="T-D2-WEIGH.", note="option not recommended (CL-C3-STOP-SECTION-PENALTY); would exceed the 131 g pod "
                                   "allocation unless 4-6 g came from the reserve")

# ---------------------------------------------------------------- tests (planned)
kit.test("T-C3-BOND-COUPON", "Bond coupons: epoxy on F-250 and on paper-faced board",
         verifies=["CL-C3-BOND-SIGMA-DESIGN", "CL-C3-BOND-R-DESIGN", "CL-C3-TRAY-FLAT", "CL-C3-FLOOR-GLUE"],
         procedure="Build epoxy, 24 h cure. Three 50 x 50 mm PETG pads on F-250 offcut and three on board: flat-wise pull to "
                   "failure (spring scale or luggage scale). Three 25 x 50 mm lap shears on F-250. Record failure load and mode "
                   "(foam / paper / adhesive). Allowable = mean - 2 s, foam or paper failure required.")
kit.test("T-C3-STOP-PUSH", "Printed stop wall and guide push test",
         verifies=["CL-C3-AFT-STOP-REC", "CL-C3-FWD-STOP-REC", "CL-C3-GUIDE-REC", "CL-C3-FEA-AFT-PROP-PEEL",
                   "CL-C3-FEA-FWD-T-PEEL", "CL-C3-FEA-FWD-T-CORE-SHEAR", "CL-C3-FEA-FWD-T-UPRIGHT",
                   "CL-C3-FEA-FWD-T-FLANGE", "CL-C3-FEA-FWD-T-WALL-SHEAR", "CL-C3-STRUT-BEARING"],
         procedure="Print the tray rear piece (with the strut on a handle-bridge offcut) and the tray front piece, same "
                   "settings as flight, and epoxy each to a foam-board floor offcut as built (the FEA shows the board peel "
                   "governs, so a bare tray proves nothing). Push a 50 x 50 mm block at 16 mm above the tray to 90 N "
                   "(aft, +x) and at 13 mm to 85 N (forward, -x, with the 1 mm bed and a nose-wall offcut), 85 N spread "
                   "over 60 mm (guide); no crack, no board delamination, set < 0.5 mm. Then to failure once.")
kit.test("T-C3-BRACKET-CRASH", "Handle bracket to the crash force on a test article (CR-H1-23)",
         verifies=["CL-C3-BRACKET-CRASH-F", "CL-C3-FEA-SADDLE-TIES"],
         procedure="Two test articles, never flown: print one handle foot + wall bracket (flight settings), epoxy the "
                   "flange to a 60 x 40 mm foam-board wall offcut (scuffed as BUILD.md step 11) and the foot onto a "
                   "22 mm CF tube stub with one tie. 24 h cure. Pull the foot with a strap and luggage scale to "
                   "CL-C3-BRACKET-CRASH-F along +x (article 1) and -z (article 2), 10 s; pass = no flange lift, no "
                   "paper tear, no tie slip. Then to failure once and record the mode.")
kit.test("T-C3-POD-PROOF", "Built pod on the wing: proof loads with a 680 g dummy pack",
         verifies=["CL-C3-BOND-R-CRASH", "CL-C3-OVERHANG-DESIGN", "CL-C3-OVERHANG-CRASH", "CL-C3-FLOOR-GLUE"],
         procedure="Wing on its spar ends. Dummy pack (680 g, pack size) strapped in. Pull the dummy pack with a luggage "
                   "scale at 1.5 x the design value to the slowest-failing direction: down (overhang) 64 N, up 85 N, aft 85 N, "
                   "sideways 85 N, 10 s each; inspect the bond edges, nose and wall tops for creases. C3-R4 "
                   "(CR-H1-23): this is the flight pod, so every pull stops at limit; the handle brackets get "
                   "CL-C3-BRACKET-PROOF-LIMIT-X along +x and CL-C3-BRACKET-PROOF-LIMIT-Z along -z (10 s each), "
                   "never the crash force (that is T-C3-BRACKET-CRASH on a test article).")

if __name__ == "__main__":
    kit.write()
    out = {k: kit._run(k) for k in [n for n in kit.nodes if n.startswith("CALC-")]}
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "results.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
