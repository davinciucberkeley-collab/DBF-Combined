"""D3 fins and motor tubes, design R2: the checks that belong to the fins CAD (subsystems/fins). Emits claims.json.

    python -I redesign/subsystems/fins/make_fins.py     (CAD -> interfaces.json, masses)
    python -I redesign/team/D3/fins_calcs.py            then   python -I redesign/proofs/build_graph.py

Vibration, fin-face, tube and block strength are C4's (team/C4/fin_structures.py: CL-C4-SEP-1LB, CL-C4-MS-FACE-1L,
CL-C4-BLOCK-MS). This script checks what D3's geometry adds or changes: the slip-clamp fuse (D-23), prop gap (B4),
screw engagement on the canted face (D-09), ESC pads in the wash, the root fillet, the brace geometry against C4's
model, and the mass. Every input is a params key, another role's claim or an ASM-D3 assumption. Python 3 stdlib.
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]                 # redesign/
sys.path.insert(0, str(ROOT / "proofs"))
import proofkit as pk                                              # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/fins/params.json"])

# ----------------------------------------------------------------------------- assumptions
kit.assumption("ASM-D3-SKIN-Z-SPAR", "Skin height over the spar 22.6 mm", "Upper surface at x 0.080 (anchor seat)",
               "S5010 at x/c 0.25 (k09kit.surface_z, subsystems/wing/s5010.dat)", 0.0226, "m", status="PROPOSED")
kit.assumption("ASM-D3-XPS-TENSILE", "XPS tensile 0.25 MPa", "Through-thickness tensile strength of F-250 under a fillet",
               "not on the TDS; typical XPS 0.2-0.4 MPa; coupon T-D3-ROOT", 0.25e6, "Pa", status="UNVERIFIED")
kit.assumption("ASM-D3-ROOT-LEFF", "Root joint effective length 0.15 m", "Root length that reacts a foot side load at the "
               "TE tip", "~55 % of the 0.26 m root; load enters at the aft end", 0.15, "m", status="UNVERIFIED")
kit.assumption("ASM-D3-ROOT-SHARE", "Root carries 50 % of the foot side load", "Share of the L4 side load at the foot "
               "reacted by the root fillets; the rest goes up the CF edge strips to the station collar and brace",
               "C4 static FE: edge strips carry the L4 side load to the tube (ASM-C4-EDGE-W note); 0.5 is conservative",
               0.5, "-", status="UNVERIFIED")
kit.assumption("ASM-D3-FILLET-LEG", "Root fillet leg 12 mm", "Microballoon-epoxy fillet leg on the skin, each side",
               "BUILD.md step 10", 0.012, "m", status="PROPOSED")
kit.assumption("ASM-D3-WASH", "Slipstream radius 0.71 R", "Fully contracted hover slipstream radius = R / sqrt 2",
               "momentum theory", 0.7071, "-", status="PROPOSED")
kit.assumption("ASM-D3-HUB", "Hub dead zone 0.2 R", "Inner radius below which the wash is weak", "11 in MR prop hub "
               "16.5 mm + root cut-out", 0.2, "-", status="PROPOSED")


# ----------------------------------------------------------------------------- calculations
@kit.calc("CALC-D3-MOUNT-SLIP",
          inputs={"T": "P:fin_detail.mount.slip_torque_nm", "xt": "P:fins.tube.x_m", "od": "P:fins.tube.od_m",
                  "gap": "P:fin_detail.bond_gap_m", "wall": "P:fin_detail.mount.collar_wall_m",
                  "ahead": "P:fin_detail.mount.face_ahead_m", "can": "P:propulsion.motor_length_m",
                  "stack": "P:fin_detail.mount.prop_stack_m", "zm": "P:propulsion.stations.z_m",
                  "M_mount": "CL-C1-MOUNT-M-ULT", "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR",
                  "M_joint": "CL-C1-FINJOINT-M-DESIGN", "mu": "P:fin_detail.mount.mu_petg_cf"},
          equation="side force at the can that turns the collar F = T / (x_tube - x_can_mid); root moment = F z_m "
                   "(brace ignored: conservative); hold ratio = T / (M_mount,ult ff pf); bolt clamp N = T / (mu pi r)",
          title="Motor-mount slip clamp: the D-23 fuse")
def mount_slip(T, xt, od, gap, wall, ahead, can, stack, zm, M_mount, ff, pf, M_joint, mu):
    x_face = xt - (od / 2 + gap + wall) - ahead
    F = T / (xt - (x_face - can / 2))
    r = od / 2
    return {"F_side": F, "F_hub": T / (xt - (x_face - stack)), "M_root": F * zm, "fuse_ratio": M_joint / (F * zm),
            "hold_ratio": T / (M_mount * ff * pf), "F_axial": T / r, "clamp_n": T / (mu * math.pi * r)}


@kit.calc("CALC-D3-PROP-GAP",
          inputs={"ahead": "P:fin_detail.mount.face_ahead_m", "stack": "P:fin_detail.mount.prop_stack_m",
                  "D": "P:propulsion.prop_diameter_m", "xt": "P:fins.tube.x_m", "od": "P:fins.tube.od_m",
                  "gap": "P:fin_detail.bond_gap_m", "wall": "P:fin_detail.mount.collar_wall_m"},
          equation="gap = collar front - prop plane = face_ahead + stack; required 0.14 D (B4 CR-B4-04)",
          title="Prop plane to the nearest structure behind it")
def prop_gap(ahead, stack, D, xt, od, gap, wall):
    x_face = xt - (od / 2 + gap + wall) - ahead
    return {"gap": ahead + stack, "ratio": (ahead + stack) / (0.14 * D), "x_prop": x_face - stack, "x_face": x_face,
            "tube_gap": xt - od / 2 - (x_face - stack)}


@kit.calc("CALC-D3-SCREW-ENGAGE",
          inputs={"Ls": "P:fin_detail.mount.motor_screw_len_m", "tp": "P:fin_detail.mount.plate_t_m",
                  "hp": "P:fin_detail.mount.pad_h_m", "pat": "P:fin_detail.mount.bolt_pattern_m",
                  "cant": "P:propulsion.stations.cant_deg", "ym": "P:propulsion.stations.y_m",
                  "zm": "P:propulsion.stations.z_m"},
          equation="engagement = L_screw - (plate + pad + tan(cant) max|t . hole|), t = tangential unit vector",
          title="Motor screw thread engagement on the canted face")
def screw_engage(Ls, tp, hp, pat, cant, ym, zm):
    n = math.hypot(ym, zm)
    dmax = max(abs(-zm / n * pat[0] / 2), abs(ym / n * pat[1] / 2))
    stack = tp + hp + math.tan(math.radians(cant)) * dmax
    return {"engage": Ls - stack, "stack_max": stack}


@kit.calc("CALC-D3-ESC-WASH",
          inputs={"zm": "P:propulsion.stations.z_m", "zp": "P:fin_detail.esc_pad.z_m", "h": "P:fin_detail.esc_pad.h_m",
                  "D": "P:propulsion.prop_diameter_m", "wash": "ASM-D3-WASH", "hub": "ASM-D3-HUB"},
          equation="pad radial extent from the motor axis r = |z_m - z_pad| -/+ h/2 inside [hub R, wash R]",
          title="ESC pad inside the hover slipstream")
def esc_wash(zm, zp, h, D, wash, hub):
    R = D / 2
    return {"r_out_frac": (zm - zp + h / 2) / (wash * R), "r_in_over_hub": (zm - zp - h / 2) / (hub * R)}


@kit.calc("CALC-D3-ROOT",
          inputs={"F": "CL-C1-FOOT-F-ULT", "mu": "ASM-C1-FRICTION", "pf": "ASM-C1-PRINTED-FACTOR",
                  "hh": "P:fins.half_height_m", "tb": "P:fins.board_t_m", "n": "P:fin_detail.layers",
                  "share": "ASM-D3-ROOT-SHARE", "leg": "ASM-D3-FILLET-LEG", "Leff": "ASM-D3-ROOT-LEFF",
                  "sx": "ASM-D3-XPS-TENSILE"},
          equation="M = share mu F_foot pf h; fillet couple capacity M_cap = sigma_xps leg L_eff (t_fin + leg)",
          title="Half-fin root fillet joint, foot side load")
def root(F, mu, pf, hh, tb, n, share, leg, Leff, sx):
    M = share * mu * F * pf * hh
    return {"M": M, "rf_fillet": sx * leg * Leff * (tb * n + leg) / M}


@kit.calc("CALC-D3-BRACE",
          inputs={"L_tube": "P:fin_detail.tube_length_m", "grip": "P:fin_detail.mount.grip_m",
                  "g_sc": "P:fin_detail.station_collar.gap_m", "h_sc": "P:fin_detail.station_collar.height_m",
                  "zm": "P:propulsion.stations.z_m", "xt": "P:fins.tube.x_m", "yf": "P:fins.y_m",
                  "od": "P:fins.tube.od_m", "gap": "P:fin_detail.bond_gap_m",
                  "wall": "P:fin_detail.station_collar.ring_wall_m", "ear": "P:fin_detail.station_collar.ear_len_m",
                  "xs": "P:wing.spar.x_m", "ya": "P:fin_detail.brace.anchor_y_m", "zsk": "ASM-D3-SKIN-Z-SPAR",
                  "proud": "P:fin_detail.anchor.proud_m", "L_c4": "CL-C4-STRUT-LEN", "dz_c4": "ASM-C4-STRUT-DZ",
                  "dy_c4": "ASM-C4-STRUT-DY", "core_c4": "ASM-C4-CORE-T-TUBE", "t": "P:fin_detail.brace.t_m",
                  "t_c4": "ASM-C4-STRUT-T"},
          equation="ear point (x_t, y_f - r_collar - ear/2, z_sc_mid), anchor (x_s, y_a, z_skin + proud/2); "
                   "Pcr ratio = (t/t_C4)^3 (L_C4 / L)^2 (pinned strip, buckles about its thin axis); lateral axial "
                   "stiffness ratio = [t (dy/L)^2/L] / same for C4's strut (station - (od/2, od/2, dz) to (x_s, y_f - dy_C4, core/2 + 2 mm))",
          title="Brace geometry against C4's braced model")
def brace(L_tube, grip, g_sc, h_sc, zm, xt, yf, od, gap, wall, ear, xs, ya, zsk, proud, L_c4, dz_c4, dy_c4, core_c4,
          t, t_c4):
    z_mid = L_tube / 2 - grip - g_sc - h_sc / 2
    e = (xt, yf - (od / 2 + gap + wall) - ear / 2, z_mid)
    a = (xs, ya, zsk + proud / 2)
    L = math.dist(e, a)
    e4 = (xt - od / 2, yf - od / 2, zm - dz_c4)
    a4 = (xs, yf - dy_c4, core_c4 / 2 + 0.002)
    L4 = math.dist(e4, a4)
    ky = ((e[1] - a[1]) / L) ** 2 / L
    ky4 = ((e4[1] - a4[1]) / L4) ** 2 / L4
    return {"L": L, "pcr_ratio": (t / t_c4) ** 3 * (L_c4 / L) ** 2, "ky_ratio": t * ky / (t_c4 * ky4), "attach_dz": zm - z_mid,
            "attach_dz_ratio": (zm - z_mid) / dz_c4, "L_c4_check": L4}


# ----------------------------------------------------------------------------- claims
MT = ["FIN-003-UR", "FIN-003-UL", "FIN-003-LR", "FIN-003-LL"]
kit.claim("CL-D3-SLIP-FUSE", "Fin-joint design moment / root moment when the mount slips", calc="CALC-D3-MOUNT-SLIP",
          output="fuse_ratio", unit="-", limit=(">=", 1.0), verifies=["R-CRASH-REPAIR"], parts=MT + ["FIN-004-R"],
          how="T-D3-SLIP: luggage scale at the motor can along y; the collar turns between 85 and 100 N")
kit.claim("CL-D3-SLIP-HOLD", "Slip torque / mount design moment (holds in flight)", calc="CALC-D3-MOUNT-SLIP",
          output="hold_ratio", unit="-", limit=(">=", 1.0), verifies=["R-STRUCT-MARGIN"], parts=MT,
          how="T-D3-SLIP; witness line checked before every flight")
kit.claim("CL-D3-SLIP-F", "Side force at the motor can that turns the collar", calc="CALC-D3-MOUNT-SLIP",
          output="F_side", unit="N", parts=MT, how="T-D3-SLIP")
kit.claim("CL-D3-PROP-GAP", "Prop plane to collar front / B4 minimum 0.14 D", calc="CALC-D3-PROP-GAP", output="ratio",
          unit="-", limit=(">=", 1.0), verifies=["R-PROP-CLEAR"], parts=MT,
          how="Measure motor face to prop hub face on the built station; Fusion interference check")
kit.claim("CL-D3-X-PROP", "Prop plane x with the D3 mount", calc="CALC-D3-PROP-GAP", output="x_prop", unit="m",
          parts=MT, how="CR-D3-04: A1 updates propulsion.stations.x_prop_plane_m (-0.005 -> this value)")
kit.claim("CL-D3-X-FACE", "Motor face x at the axis (D3 mount)", calc="CALC-D3-PROP-GAP", output="x_face", unit="m",
          parts=MT, how="CR-D3-04: A1 notes the mount face in propulsion.stations.x_mount_m")
kit.claim("CL-D3-SCREW-ENGAGE", "Motor-screw engagement, worst hole on the canted face", calc="CALC-D3-SCREW-ENGAGE",
          output="engage", unit="m", limit=(">=", 0.003), verifies=["R-JOINT-STACK"], parts=MT,
          how="Probe the motor screw-hole depth on arrival (CL-E1-SCREW-ENGAGE); count turns on assembly",
          note="limit = requirements.thread_engagement_min 1.0 x d, d = 3 mm")
kit.claim("CL-D3-ESC-WASH", "ESC pad outer edge / slipstream radius", calc="CALC-D3-ESC-WASH", output="r_out_frac", unit="-",
          limit=("<=", 1.0), verifies=["R-THERMAL"], parts=["FIN-007-UR"], how="Tuft on the pad in a tethered hover; ESC "
          "temperature log in the E3 hover test")
kit.claim("CL-D3-ESC-HUB", "ESC pad inner edge / hub dead zone", calc="CALC-D3-ESC-WASH", output="r_in_over_hub", unit="-",
          limit=(">=", 1.0), parts=["FIN-007-UR"], how="as CL-D3-ESC-WASH")
kit.claim("CL-D3-ROOT-FILLET-RF", "Half-fin root fillet joint reserve factor, foot side load", calc="CALC-D3-ROOT",
          output="rf_fillet", unit="-", limit=(">=", 1.0), verifies=["R-LANDING-IMPACT"], parts=["FIN-001-RU"],
          how="T-D3-ROOT: side pull at the fin TE tip on a core offcut to 1.25 x 28 N, then to failure")
kit.claim("CL-D3-BRACE-PCR", "Brace buckling load / C4's modelled brace", calc="CALC-D3-BRACE", output="pcr_ratio", unit="-",
          limit=(">=", 1.0), verifies=["R-STRUCT-MARGIN"], parts=["FIN-009-UR"],
          how="C4 re-runs CALC-C4-STATIC-1L with CL-D3-BRACE-L (CR-D3-10)")
kit.claim("CL-D3-BRACE-KY", "Brace lateral axial stiffness / C4's modelled brace", calc="CALC-D3-BRACE",
          output="ky_ratio", unit="-", limit=(">=", 1.0), verifies=["R-VIBRATION"], parts=["FIN-009-UR"], how="C4 re-runs the modes with the D3 brace (CR-D3-10)",
          note="anchor moved outboard to y 0.242 to clear D7's cradles; steeper brace, 10 x 3 strip restores the stiffness")
kit.claim("CL-D3-BRACE-L", "Brace length, D3 geometry", calc="CALC-D3-BRACE", output="L", unit="m", parts=["FIN-009-UR"],
          how="Measure on the jig")
kit.claim("CL-D3-BRACE-DZ", "Brace attach depth below the motor axis, D3 geometry", calc="CALC-D3-BRACE",
          output="attach_dz", unit="m", parts=["FIN-008-UR"],
          how="C4 re-runs the modes with this value (C4 assumed 25 mm; CR-D3-10)",
          note="deeper than C4's 25 mm because the mount collar and its slip stroke sit directly under the motor")

for tid, title, ver, proc in (
        ("T-D3-SLIP", "Mount slip setting", ["CL-D3-SLIP-FUSE", "CL-D3-SLIP-HOLD"],
         "luggage scale hooked on the motor can, pull along y; adjust the pinch bolt until the collar turns at 85-100 N"),
        ("T-D3-ROOT", "Half-fin root side pull", ["CL-D3-ROOT-FILLET-RF"],
         "half-fin bonded to a core offcut per BUILD step 10; pull at the TE tip along y to 35 N, then to failure"),
        ("T-D3-WEIGH", "Weigh every fins part", ["CL-D3-MASS"], "1 g scale; update mass_g and status VERIFIED")):
    kit.test(tid, title, ver, procedure=proc)


def _mass():
    d = json.loads((ROOT / "subsystems" / "fins" / "interfaces.json").read_text(encoding="utf-8"))
    return round(sum(p["mass_g"] for p in d["parts"]), 1)


kit.claim("CL-D3-MASS", "Fins subsystem flying mass (one-layer boards, CR-D3-02)", value=_mass(), unit="g",
          limit=("<=", "P:mass.allocation_g.fins"), verifies=["R-MASS-ALLOC"], parts=["FIN-001-RU"],
          how="T-D3-WEIGH; sum of subsystems/fins/interfaces.json",
          note="from make_fins.py (CAD volumes x densities); with two board layers it is about 396 g (CR-D3-02)")

if __name__ == "__main__":
    kit.write()
