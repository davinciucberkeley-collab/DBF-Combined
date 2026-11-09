"""A5 CAD lead: geometry claims other roles build on (hinge line, spar cover, elevon gaps, layout CG).

Run:  python -I redesign/team/A5/cad_claims.py      then  python -I redesign/proofs/build_graph.py
Every calculation is a pure function of params.json ids and the A5 assumptions below; the section geometry uses
redesign/fusion/k09kit.py (the same helper the CAD modules use), so the CAD and the claims cannot disagree.
The layout CG reproduces the skeleton (redesign/fusion/skeleton) in closed form: allocated masses at the DATUMS.md
stations. Cross-check: python -I redesign/fusion/check.py --skeleton prints the CAD roll-up.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
sys.path.insert(0, str(HERE.parents[1] / "fusion"))
import proofkit as pk  # noqa: E402
import k09kit as k9    # noqa: E402
import fusionkit as fk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"

# ---------------------------------------------------------------- assumptions
kit.assumption("ASM-A5-CAMBER", "Placeholder section camber 1.6 %",
               "Until B2 supplies the MH 45 coordinates, CAD and these claims use a NACA 00xx thickness at "
               "params wing.t_c with a reflexed cubic camber line, maximum camber 1.6 % chord, zero crossing at 80 % chord",
               basis="EST for an MH 45-class reflexed section; replaced by subsystems/wing/mh45.dat (CR-A5-02)",
               value=0.016, unit="-", status="UNVERIFIED", cites=["SRC-MH45"])
kit.assumption("ASM-A5-MIN-COVER", "Minimum foam over the spar",
               "Hot-wired XPS must keep at least 2 mm of foam between the spar tube and the skin on both surfaces",
               basis="A5 modelling standard: thinner foam tears when the slot is cut and the tube bonded; G2 confirms on a test core",
               value=0.002, unit="m", cites=["SRC-K09-CARD"])
kit.assumption("ASM-A5-MIN-GAP", "Minimum elevon end gap",
               "Each elevon panel end stays at least 10 mm from the pod side, the fin face and the wing tip",
               basis="A5 modelling standard: room for tape, a horn and +/-25 deg travel without rubbing; D6 confirms",
               value=0.010, unit="m", cites=["SRC-K09-CARD"])
kit.assumption("ASM-A5-FOAMBOARD-T", "Foam-board layer thickness",
               "One layer of the fin foam board is 4.8 mm (3/16 in)", basis="params fins.material text; measure a sheet",
               value=0.0048, unit="m", status="UNVERIFIED", cites=["SRC-K09-CARD"])
kit.assumption("ASM-A5-MASS-SPLIT", "Allocation split used for the layout CG",
               "Within each allocation: wing = spar 102 g + core/tape/elevons rest; fins = 2 x 111 fin (incl. clips, epoxy) "
               "+ 2 x 43 tube + 4 x 18 mount + 2 x 15 saddle; propulsion = 4 x 87.5 motor+ESC at the motor + 4 x 20 prop; "
               "power = 550 pack + rest behind it; pod, avionics in the pod; mechanisms at the servo pockets; harness on the "
               "skin at x 0.01 m; growth reserve not placed",
               basis="params.json#mass.allocation_g notes; the skeleton (redesign/fusion/skeleton) uses the same split",
               value=None, unit=None, cites=["SRC-K09-CARD", "SRC-K09-REVIEW"])


def _section(t_c, camber):
    return k9.reflex_placeholder(t_c, camber)


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-A5-HINGE", title="Elevon hinge line", assumes=["ASM-A5-CAMBER"],
          equation="x_h = c (1 - f) ; z_h = upper surface at x_h/c ; t_h = section thickness at the hinge",
          inputs={"c": P + "wing.chord_m", "f": P + "wing.elevon.chord_frac", "t_c": P + "wing.t_c",
                  "camber": "ASM-A5-CAMBER"}, units={"c": "m"})
def hinge(c, f, t_c, camber):
    s = _section(t_c, camber)
    h = 1 - f
    return {"x_m": c * h, "z_m": k9.surface_z(s, c, h, "upper"), "thickness_m": k9.thickness_at(s, c, h),
            "elevon_chord_m": c * f}


@kit.calc("CALC-A5-SPAR-COVER", title="Foam cover over the spar", assumes=["ASM-A5-CAMBER"],
          equation="cover_up = z_upper(x_s) - (z_s + r) ; cover_lo = (z_s - r) - z_lower(x_s) ; "
                   "z_camber = (z_upper + z_lower)/2 ; cover_on_camber = (t(x_s) - 2r)/2",
          inputs={"c": P + "wing.chord_m", "t_c": P + "wing.t_c", "camber": "ASM-A5-CAMBER",
                  "x_s": P + "wing.spar.x_m", "z_s": P + "wing.spar.z_m", "od": P + "wing.spar.od_m"},
          units={"c": "m", "x_s": "m", "z_s": "m", "od": "m"})
def spar_cover(c, t_c, camber, x_s, z_s, od):
    s = _section(t_c, camber)
    f, r = x_s / c, od / 2
    zu, zl = k9.surface_z(s, c, f, "upper"), k9.surface_z(s, c, f, "lower")
    up, lo = zu - (z_s + r), (z_s - r) - zl
    return {"cover_upper_m": up, "cover_lower_m": lo, "cover_min_m": min(up, lo),
            "z_camber_m": (zu + zl) / 2, "cover_on_camber_m": ((zu - zl) - 2 * r) / 2}


@kit.calc("CALC-A5-ELEVON-GAPS", title="Elevon end gaps",
          equation="pod = y_in0 - w_pod/2 ; fin_in = (y_fin - t_fin/2) - y_in1 ; fin_out = y_out0 - (y_fin + t_fin/2) ; "
                   "tip = b/2 - y_out1 ; t_fin = layers t_board",
          inputs={"yin": P + "wing.elevon.inboard_y_m", "yout": P + "wing.elevon.outboard_y_m",
                  "pod": P + "pod.size_m", "y_fin": P + "fins.y_m", "layers": P + "fins.layers",
                  "t_board": "ASM-A5-FOAMBOARD-T", "b": P + "wing.span_m"},
          units={"yin": "m", "yout": "m", "pod": "m", "y_fin": "m", "t_board": "m", "b": "m"})
def elevon_gaps(yin, yout, pod, y_fin, layers, t_board, b):
    t = layers * t_board
    g = {"gap_pod_m": yin[0] - pod[1] / 2, "gap_fin_inboard_m": (y_fin - t / 2) - yin[1],
         "gap_fin_outboard_m": yout[0] - (y_fin + t / 2), "gap_tip_m": b / 2 - yout[1]}
    g["gap_min_m"] = min(g.values())
    g["fin_thickness_m"] = t
    return g


@kit.calc("CALC-A5-LAYOUT-CG", title="Layout CG: allocations at the datum stations",
          assumes=["ASM-A5-MASS-SPLIT", "ASM-A5-CAMBER"],
          equation="x_cg = sum(m_i x_i) / sum(m_i), z likewise; pack x for x_target = x_pack + M (x_target - x_cg) / m_pack ; "
                   "upper-pair hover share = (z_m + z_cg) / (2 z_m)",
          inputs={"a_wing": P + "mass.allocation_g.wing", "a_fins": P + "mass.allocation_g.fins",
                  "a_pod": P + "mass.allocation_g.pod", "a_land": P + "mass.allocation_g.landing",
                  "a_prop": P + "mass.allocation_g.propulsion", "a_pwr": P + "mass.allocation_g.power",
                  "a_avn": P + "mass.allocation_g.avionics", "a_hrn": P + "mass.allocation_g.harness",
                  "a_mec": P + "mass.allocation_g.mechanisms", "m_pack_kg": P + "battery.mass_kg",
                  "c": P + "wing.chord_m", "t_c": P + "wing.t_c", "camber": "ASM-A5-CAMBER", "f": P + "wing.elevon.chord_frac",
                  "x_s": P + "wing.spar.x_m", "xt": P + "fins.tube.x_m", "te": P + "fins.te_x_m", "od": P + "fins.tube.od_m",
                  "can_l": P + "propulsion.motor_length_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "z_m": P + "propulsion.stations.z_m", "foot": P + "cg.foot_height_m", "pod_x": P + "pod.x_le_m",
                  "pod_size": P + "pod.size_m", "pod_z": P + "pod.z_base_m", "pack_size": P + "battery.size_m",
                  "x_target": P + "cg.x_target_m", "x_range": P + "cg.x_range_m", "z_range": P + "cg.z_range_m"},
          units={"a_wing": "g", "a_fins": "g", "a_pod": "g", "a_land": "g", "a_prop": "g", "a_pwr": "g", "a_avn": "g",
                 "a_hrn": "g", "a_mec": "g", "m_pack_kg": "kg", "c": "m", "x_s": "m", "xt": "m", "te": "m", "od": "m",
                 "can_l": "m", "x_prop": "m", "z_m": "m", "foot": "m", "pod_x": "m", "pod_size": "m", "pod_z": "m",
                 "pack_size": "m", "x_target": "m", "x_range": "m", "z_range": "m"})
def layout_cg(a_wing, a_fins, a_pod, a_land, a_prop, a_pwr, a_avn, a_hrn, a_mec, m_pack_kg, c, t_c, camber, f,
              x_s, xt, te, od, can_l, x_prop, z_m, foot, pod_x, pod_size, pod_z, pack_size, x_target, x_range, z_range):
    s = _section(t_c, camber)
    _, (sx, sz) = fk.poly_area_centroid(k9.section_loop(s, c, (0.0, 0.0), 0.0, 1.0, 48))
    wall = 0.003
    mount_x = ((xt - od / 2) + (xt + od / 2 + wall)) / 2
    m_pack = m_pack_kg * 1000.0
    pod_cx, pod_cz = pod_x + pod_size[0] / 2, pod_z + pod_size[2] / 2
    pack_z = pod_z + wall + pack_size[2] / 2
    items = [  # (mass g, x m, z m)
        (a_wing - 102.0, sx, sz), (102.0, x_s, 0.0),
        (222.0, (xt + te) / 2, 0.0), (86.0, xt, 0.0), (72.0, mount_x, 0.0), (30.0, (xt + x_s + od / 2 + wall) / 2, 0.0),
        (a_fins - 410.0, (xt + te) / 2, 0.0),
        (a_prop - 80.0, (xt - od / 2) - can_l / 2, 0.0), (80.0, x_prop, 0.0),
        (a_land, te + foot / 2 - 0.006, 0.0),
        (a_pod, pod_cx, pod_cz), (m_pack, pod_cx, pack_z),
        (a_pwr - m_pack, pod_cx + pack_size[0] / 2 + 0.01, pod_z + wall + 0.01),
        (a_avn, pod_x + 0.095, pod_z + pod_size[2] - 0.0115),
        (a_mec, c * (1 - f) - 0.0235, 0.0), (a_hrn, 0.01, 0.007)]
    M = sum(m for m, _, _ in items)
    x = sum(m * xi for m, xi, _ in items) / M
    z = sum(m * zi for m, _, zi in items) / M
    pack_x = pod_cx + M * (x_target - x) / m_pack
    return {"mass_g": M, "cg_x_m": x, "cg_z_m": z, "cg_x_frac_chord": x / c,
            "cg_x_fwd_limit_m": x_range[0], "cg_z_up_limit_m": z_range[1],
            "pack_x_for_target_m": pack_x, "pack_shift_m": pack_x - pod_cx,
            "pod_aft_end_for_target_m": pack_x + pack_size[0] / 2 + wall,
            "hover_upper_pair_share": (z_m + z) / (2 * z_m)}


# ---------------------------------------------------------------- claims
kit.claim("CL-A5-HINGE-X", "Elevon hinge line station", calc="CALC-A5-HINGE", output="x_m", unit="m",
          how="Datum DP-HINGE in Fusion (00 Datums); on the core, measure from the LE to the hinge cut.")
kit.claim("CL-A5-HINGE-Z", "Hinge height (upper skin at the hinge)", calc="CALC-A5-HINGE", output="z_m", unit="m",
          assumes=["ASM-A5-CAMBER"],
          how="Re-run after B2 supplies the MH 45 .dat; on the core, height of the upper skin at the hinge cut above the chord line.")
kit.claim("CL-A5-SPAR-COVER", "Foam over the spar, thinner side", calc="CALC-A5-SPAR-COVER", output="cover_min_m", unit="m",
          limit=(">=", "ASM-A5-MIN-COVER"), assumes=["ASM-A5-CAMBER"],
          how="With the spar on the chord line (wing.spar.z_m = 0) the tube breaks the lower skin; move it to the camber "
              "line (CR-A5-01). Check on the first cut core with a depth gauge on both surfaces.")
kit.claim("CL-A5-SPAR-Z-CAMBER", "Spar height on the local camber line", calc="CALC-A5-SPAR-COVER", output="z_camber_m",
          unit="m", assumes=["ASM-A5-CAMBER"],
          how="Recommended wing.spar.z_m; recompute with the real MH 45 coordinates.")
kit.claim("CL-A5-SPAR-COVER-CAMBER", "Foam over the spar if centred on the camber line", calc="CALC-A5-SPAR-COVER",
          output="cover_on_camber_m", unit="m", limit=(">=", "ASM-A5-MIN-COVER"), assumes=["ASM-A5-CAMBER"],
          how="Same core check after the spar is moved.")
kit.claim("CL-A5-ELEVON-GAP-MIN", "Smallest elevon end gap", calc="CALC-A5-ELEVON-GAPS", output="gap_min_m", unit="m",
          limit=(">=", "ASM-A5-MIN-GAP"), verifies=["R-ELEVON-AREA"],
          how="check.py --skeleton (bounding boxes); on the aircraft, feeler gauge at each panel end at +/-25 deg.")
kit.claim("CL-A5-CG-X-FWD-LIMIT", "Forward CG limit (params cg.x_range_m[0])", calc="CALC-A5-LAYOUT-CG",
          output="cg_x_fwd_limit_m", unit="m", how="B3 sets the range from AVL (CR-A1-06).")
kit.claim("CL-A5-LAYOUT-CG-X", "Layout CG x (allocations at the datum stations)", calc="CALC-A5-LAYOUT-CG",
          output="cg_x_m", unit="m", limit=(">=", "CL-A5-CG-X-FWD-LIMIT"), verifies=["R-STATIC-MARGIN"],
          assumes=["ASM-A5-MASS-SPLIT", "ASM-A5-CAMBER"],
          how="Cross-check with the CAD roll-up (python -I redesign/fusion/check.py --skeleton, TOTAL line). A3 replaces "
              "the allocations with part masses (MASS-CG.md); H1 balances the built aircraft on two knife edges.")
kit.claim("CL-A5-PACK-X-FOR-CG", "Pack centre needed for the CG target", calc="CALC-A5-LAYOUT-CG",
          output="pack_x_for_target_m", unit="m", assumes=["ASM-A5-MASS-SPLIT"],
          how="D2/A3: compare with the pod length; the pod as sized ends at x = 0.18 m.")
kit.claim("CL-A5-CG-Z-UP-LIMIT", "Upper CG z limit (params cg.z_range_m[1])", calc="CALC-A5-LAYOUT-CG",
          output="cg_z_up_limit_m", unit="m", how="B3 / A1 set the range.")
kit.claim("CL-A5-LAYOUT-CG-Z", "Layout CG z (allocations at the datum stations)", calc="CALC-A5-LAYOUT-CG",
          output="cg_z_m", unit="m", limit=("<=", "CL-A5-CG-Z-UP-LIMIT"), assumes=["ASM-A5-MASS-SPLIT"],
          how="H1: hang the aircraft from two points to find z; A3 tracks in MASS-CG.md.")
kit.claim("CL-A5-HOVER-SPLIT", "Hover thrust share of the upper motor pair", calc="CALC-A5-LAYOUT-CG",
          output="hover_upper_pair_share", unit="-", assumes=["ASM-A5-MASS-SPLIT"],
          how="B3/E1: differential thrust needed to trim hover pitch; read from the hover log (motor outputs).")

kit.test("T-A5-CORE-COVER", "Spar cover on the first cut core", verifies=["CL-A5-SPAR-COVER", "CL-A5-SPAR-COVER-CAMBER"],
         state="planned", procedure="Cut a 100 mm core section, cut the slot, depth-gauge foam above and below the slot (G2).")
kit.test("T-A5-CG-BALANCE", "CG balance of the built aircraft", verifies=["CL-A5-LAYOUT-CG-X", "CL-A5-LAYOUT-CG-Z"],
         state="planned", procedure="Pack in, props on; two knife edges under the wing at the fin roots; mark x (H1).")

if __name__ == "__main__":
    kit.write()
