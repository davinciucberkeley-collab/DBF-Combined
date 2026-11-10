"""D3 fins and motor tubes, design R3: the checks that belong to the fins CAD (subsystems/fins). Emits claims.json.

    python -I redesign/subsystems/fins/make_fins.py     (CAD -> interfaces.json, masses)
    python -I redesign/team/D3/fins_calcs.py            then   python -I redesign/proofs/build_graph.py

Vibration, fin-face, tube, brace and block strength are C4's (team/C4/fin_structures_d3.py: CL-C4-D3-SEP,
CL-C4-D3-SEP-WORST, CL-C4-D3-F1-LO, CL-C4-D3-MS-FACE, CL-C4-D3-BLOCK-MS, CL-C4-D3-MOUNT-K-REQ); joint strength is
C6's (team/C6/joints.py). This script checks what D3's R3 geometry adds or changes: the slip-clamp fuse (D-23), prop
gap (B4), screw engagement on the 7 deg canted plate (D-27), the collar height and tail length against C6's
requirements, the strap eye (H1), the square foot tip (D5), ESC pads in the wash, the root fillet, the brace geometry
against C4's model, and the mass. Every input is a params key, another role's claim or an ASM-D3 assumption.
Python 3 stdlib.
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
               "reacted by the root fillets; the rest goes up the pinned CF edge strips to the station collar and brace",
               "C4 static FE: edge strips carry the L4 side load to the tube; 0.5 is conservative",
               0.5, "-", status="UNVERIFIED")
kit.assumption("ASM-D3-FILLET-LEG", "Root fillet leg 12 mm", "Microballoon-epoxy fillet leg on the skin, each side",
               "BUILD.md", 0.012, "m", status="PROPOSED")
kit.assumption("ASM-D3-WASH", "Slipstream radius 0.71 R", "Fully contracted hover slipstream radius = R / sqrt 2",
               "momentum theory", 0.7071, "-", status="PROPOSED")
kit.assumption("ASM-D3-HUB", "Hub dead zone 0.2 R", "Inner radius below which the wash is weak", "11 in MR prop hub "
               "16.5 mm + root cut-out", 0.2, "-", status="PROPOSED")
kit.assumption("ASM-D3-PETG-SHEAR", "Printed PETG shear 15 MPa", "Shear strength of printed PETG, load across the "
               "perimeters (eye ligaments), 100 % walls", "about 1/3 of the 45-50 MPa bulk tensile on PETG TDS, knocked "
               "down for layer adhesion; coupon with T-D3-EYE", 15e6, "Pa", status="UNVERIFIED")
kit.assumption("ASM-D3-SHOE-LEN", "Foot shoe length 37 mm", "Length of D5's shoe sleeve along the tip edge",
               "team/D5/CHANGE-REQUESTS.md#CR-D5-03 (37 x 9.6 mm floor)", 0.037, "m", status="PROPOSED")


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
                  "pat": "P:fin_detail.mount.bolt_pattern_m", "cant": "P:propulsion.stations.cant_deg",
                  "ym": "P:propulsion.stations.y_m", "zm": "P:propulsion.stations.z_m"},
          equation="R3 canted plate (front and back faces both on the cant plane): engagement = L_screw - t_plate at "
                   "every hole; for comparison the R2 flat plate + canted pads would give L - (t + tan(cant) max|t.hole|)",
          title="Motor screw thread engagement on the 7 deg canted plate")
def screw_engage(Ls, tp, pat, cant, ym, zm):
    n = math.hypot(ym, zm)
    dmax = max(abs(-zm / n * pat[0] / 2), abs(ym / n * pat[1] / 2))
    return {"engage": Ls - tp, "stack_max": tp, "flat_plate_engage": Ls - (tp + math.tan(math.radians(cant)) * dmax),
            "head_tilt_flat_deg": cant}


@kit.calc("CALC-D3-COLLAR",
          inputs={"h": "P:fin_detail.station_collar.height_m", "h_req": "CL-C6-COLLAR-L-REQ",
                  "tail": "P:fin_detail.station_collar.tail_m", "gap": "P:fin_detail.fin.le_gap_m",
                  "embed_req": "CL-C6-STRIP-EMBED-REQ"},
          equation="collar ratio = h / h_req (C6, on C4's 9.3 N m torsion); strip embedment = tail - LE gap, "
                   "ratio = embedment / embed_req (C6, two faces bonded: tongue + wall)",
          title="Station collar height and two-face tail length against C6")
def collar(h, h_req, tail, gap, embed_req):
    emb = tail - gap
    return {"h_ratio": h / h_req, "embed": emb, "embed_ratio": emb / embed_req}


@kit.calc("CALC-D3-STRAP-EYE",
          inputs={"F": "P:fin_detail.strap_eye.load_n", "L": "P:fin_detail.strap_eye.len_m",
                  "yh": "P:fin_detail.strap_eye.hole_y_m", "d": "P:fin_detail.strap_eye.hole_d_m",
                  "h": "P:fin_detail.strap_eye.h_m", "t": "P:fin_detail.strap_eye.t_m",
                  "tau": "ASM-D3-PETG-SHEAR", "sf": "P:requirements.safety_factor_ult",
                  "pf": "ASM-C1-PRINTED-FACTOR"},
          equation="worst ligament e = min(L - yh - d/2, (h - d)/2); shear-out capacity 2 e t tau; "
                   "RF = capacity / (F sf pf)",
          title="Strap eye on the block boss (H1 restrained run)")
def strap_eye(F, L, yh, d, h, t, tau, sf, pf):
    e = min(L - yh - d / 2, (h - d) / 2)
    cap = 2 * e * t * tau
    return {"lig": e, "capacity": cap, "rf": cap / (F * sf * pf)}


@kit.calc("CALC-D3-TIP",
          inputs={"sq": "P:fin_detail.fin.tip_square_m", "shoe": "ASM-D3-SHOE-LEN", "tb": "P:fins.board_t_m",
                  "n": "P:fins.layers"},
          equation="square-tip ratio = flat tip length / shoe length; tip edge width = n t_board",
          title="Square foot tip for D5's shoe")
def tip(sq, shoe, tb, n):
    return {"ratio": sq / shoe, "width": n * tb}


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
                  "hh": "P:fins.half_height_m", "tb": "P:fins.board_t_m", "n": "P:fins.layers",
                  "share": "ASM-D3-ROOT-SHARE", "leg": "ASM-D3-FILLET-LEG", "Leff": "ASM-D3-ROOT-LEFF",
                  "sx": "ASM-D3-XPS-TENSILE"},
          equation="M = share mu F_foot pf h; fillet couple capacity M_cap = sigma_xps leg L_eff (t_fin + leg)",
          title="Half-fin root fillet joint, foot side load")
def root(F, mu, pf, hh, tb, n, share, leg, Leff, sx):
    M = share * mu * F * pf * hh
    return {"M": M, "rf_fillet": sx * leg * Leff * (tb * n + leg) / M}


@kit.calc("CALC-D3-BRACE",
          inputs={"L_tube": "P:fins.tube.length_m", "grip": "P:fin_detail.mount.grip_m",
                  "g_sc": "P:fin_detail.station_collar.gap_m", "ear_h": "P:fin_detail.station_collar.ear_h_m",
                  "zm": "P:propulsion.stations.z_m", "xt": "P:fins.tube.x_m", "yf": "P:fins.y_m",
                  "od": "P:fins.tube.od_m", "gap": "P:fin_detail.bond_gap_m",
                  "wall": "P:fin_detail.station_collar.ring_wall_m", "ear": "P:fin_detail.station_collar.ear_len_m",
                  "xs": "P:wing.spar.x_m", "ya": "P:fin_detail.brace.anchor_y_m", "zsk": "ASM-D3-SKIN-Z-SPAR",
                  "proud": "P:fin_detail.anchor.proud_m", "t": "P:fin_detail.brace.t_m",
                  "w": "P:fin_detail.brace.w_m", "F_d": "CL-C4-D3-BRACE-F", "E": "ASM-D3-CF-E-STRIP"},
          equation="ear point (x_t, y_f - r_collar - ear/2, z_ear_mid = L_tube/2 - grip - gap - ear_h/2), anchor (x_s, "
                   "y_a, z_skin + proud/2); Pcr = pi^2 E (w t^3/12) / L^2 (pinned, thin axis); Pcr ratio = Pcr / F_design "
                   "(C4); lateral axial stiffness ky = E w t (dy/L)^2 / L (information). R3: no longer reads C4's R1 strut "
                   "(CR-C4-26)",
          title="Brace geometry, D3 R3")
def brace(L_tube, grip, g_sc, ear_h, zm, xt, yf, od, gap, wall, ear, xs, ya, zsk, proud, t, w, F_d, E):
    z_mid = L_tube / 2 - grip - g_sc - ear_h / 2
    e = (xt, yf - (od / 2 + gap + wall) - ear / 2, z_mid)
    a = (xs, ya, zsk + proud / 2)
    L = math.dist(e, a)
    ky = E * w * t * ((e[1] - a[1]) / L) ** 2 / L
    pcr = math.pi ** 2 * E * (w * t ** 3 / 12) / L ** 2
    return {"L": L, "pcr": pcr, "pcr_ratio": pcr / F_d, "ky": ky, "attach_dz": zm - z_mid}


kit.assumption("ASM-D3-CF-E-STRIP", "Pultruded CF strip E 110 GPa", "Axial modulus of a pultruded CF strip",
               "typical pultruded CF 110-135 GPa (vendor sheets); low end", 110e9, "Pa", status="UNVERIFIED")


# ----------------------------------------------------------------------------- claims
kit.assumption("ASM-D3-SKIN-Z-HOLE", "Upper skin height 22.7 mm at x 0.086", "Upper surface at the ESC-lead hole",
               "S5010 at x/c 0.269 (k09kit.surface_z); the lower skin is 8.7 mm below the chord, so the upper hole is "
               "the one closest to the ESC pad", 0.0227, "m", status="PROPOSED")
kit.assumption("ASM-D3-TAPE-LAP", "Skin tape lapped 15 mm up the laminate", "Height of the skin-tape lap on both "
               "laminate faces at the root", "README.md interface table; BUILD.md step 17", 0.015, "m", status="PROPOSED")
kit.assumption("ASM-D3-GROMMET-OD", "Grommet flange OD 10 mm", "Printed ASA grommet 10/7 mm in the 8 mm lead hole (F2)",
               "team/F2/CHANGE-REQUESTS.md#CR-F2-05", 0.010, "m", status="PROPOSED")


@kit.calc("CALC-D3-WIRE-HOLE",
          inputs={"x": "P:fin_detail.wire_hole.x_m", "off": "P:fin_detail.wire_hole.off_skin_m",
                  "d": "P:fin_detail.wire_hole.d_m", "xt": "P:fins.tube.x_m", "od": "P:fins.tube.od_m",
                  "tail": "P:fin_detail.boss.tail_m", "pz": "P:fin_detail.esc_pad.z_m", "ph": "P:fin_detail.esc_pad.h_m",
                  "zsk": "ASM-D3-SKIN-Z-HOLE", "leg": "ASM-D3-FILLET-LEG", "lap": "ASM-D3-TAPE-LAP",
                  "g": "ASM-D3-GROMMET-OD"},
          equation="flange edge above the skin = off - g/2; root clearance = that - max(fillet leg, tape lap); boss "
                   "clearance = x - g/2 - (x_tube + od/2 + boss tail); pad clearance = (pz - ph/2) - (zsk + off + g/2); "
                   "min of the three",
          title="ESC-lead hole through the half-fin (CR-F2-05): clear of the root joint, boss and ESC pad")
def wire_hole(x, off, d, xt, od, tail, pz, ph, zsk, leg, lap, g):
    root = off - g / 2 - max(leg, lap)
    boss = x - g / 2 - (xt + od / 2 + tail)
    pad = (pz - ph / 2) - (zsk + off + g / 2)
    return {"root": root, "boss": boss, "pad": pad, "min": min(root, boss, pad)}


MT = ["FIN-003-UR", "FIN-003-UL", "FIN-003-LR", "FIN-003-LL"]
SC = ["FIN-008-UR", "FIN-008-UL", "FIN-008-LR", "FIN-008-LL"]
HF = ["FIN-001-UR", "FIN-001-UL", "FIN-001-LR", "FIN-001-LL"]
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
          how="Measure motor face to prop hub face on the built station; Fusion interference check",
          note="the canted plate corners sit up to 2.5 mm ahead of the face at the axis, inside the motor-base shadow")
kit.claim("CL-D3-X-PROP", "Prop plane x with the D3 mount", calc="CALC-D3-PROP-GAP", output="x_prop", unit="m",
          parts=MT, how="D-28: params propulsion.stations.x_prop_plane_m carries this value")
kit.claim("CL-D3-X-FACE", "Motor face x at the axis (D3 mount)", calc="CALC-D3-PROP-GAP", output="x_face", unit="m",
          parts=MT, how="D-28: noted in propulsion.stations.x_mount_m")
kit.claim("CL-D3-SCREW-ENGAGE", "Motor-screw engagement, every hole, 7 deg canted plate", calc="CALC-D3-SCREW-ENGAGE",
          output="engage", unit="m", limit=(">=", 0.003), verifies=["R-JOINT-STACK"], parts=MT,
          how="Probe the motor screw-hole depth on arrival (T-E1-MOTOR-RM); count turns on assembly",
          note="limit = requirements.thread_engagement_min 1.0 x d, d = 3 mm; the R2 flat plate + pads gives 2.5 mm at 7 deg")
kit.claim("CL-D3-COLLAR-H", "Station collar height / C6 required bond length", calc="CALC-D3-COLLAR", output="h_ratio",
          unit="-", limit=(">=", 1.0), verifies=["R-FIN-TUBE-JOINT"], parts=SC,
          how="C6 coupon T-C6-COLLAR; measure the printed collar")
kit.claim("CL-D3-TAIL-EMBED", "Edge-strip embedment in the collar tail / C6 required", calc="CALC-D3-COLLAR",
          output="embed_ratio", unit="-", limit=(">=", 1.0), verifies=["R-FIN-TUBE-JOINT"],
          parts=SC + ["FIN-011-URO"], how="Measure on the dry fit; C6 strip-anchor coupon")
kit.claim("CL-D3-STRAP-EYE-RF", "Strap eye shear-out reserve factor at the H1 tie load", calc="CALC-D3-STRAP-EYE",
          output="rf", unit="-", limit=(">=", 1.0), verifies=["R-STRUCT-MARGIN"], parts=["FIN-004-R", "FIN-004-L"],
          how="T-D3-EYE: spring scale on a printed eye to 2 x 29.4 N, then to failure")
kit.claim("CL-D3-TIP-SQUARE", "Square tip length / D5 shoe length", calc="CALC-D3-TIP", output="ratio", unit="-",
          limit=(">=", 1.0), verifies=["R-LANDING-IMPACT"], parts=HF, how="Dry-fit the D5 shoe on the cut half-fin")
kit.claim("CL-D3-TIP-W", "Tip edge width for the D5 shoe (two layers)", calc="CALC-D3-TIP", output="width", unit="m",
          parts=HF, how="Calliper on the laminate")
kit.claim("CL-D3-ESC-WASH", "ESC pad outer edge / slipstream radius", calc="CALC-D3-ESC-WASH", output="r_out_frac", unit="-",
          limit=("<=", 1.0), verifies=["R-THERMAL"], parts=["FIN-007-UR"], how="Tuft on the pad in a tethered hover; ESC "
          "temperature log in the E3 hover test")
kit.claim("CL-D3-ESC-HUB", "ESC pad inner edge / hub dead zone", calc="CALC-D3-ESC-WASH", output="r_in_over_hub", unit="-",
          limit=(">=", 1.0), parts=["FIN-007-UR"], how="as CL-D3-ESC-WASH")
kit.claim("CL-D3-ROOT-FILLET-RF", "Half-fin root fillet joint reserve factor, foot side load", calc="CALC-D3-ROOT",
          output="rf_fillet", unit="-", limit=(">=", 1.0), verifies=["R-LANDING-IMPACT"], parts=["FIN-001-UR"],
          how="T-D3-ROOT: side pull at the fin TE tip on a core offcut to 1.25 x 28 N, then to failure")
kit.claim("CL-D3-BRACE-PCR", "Brace (10 x 2) Euler load / C4 design brace force", calc="CALC-D3-BRACE",
          output="pcr_ratio", unit="-", limit=(">=", 1.0), verifies=["R-STRUCT-MARGIN"], parts=["FIN-009-LR"],
          how="C4 CL-C4-D3-MS-BRACE; T-C4-TAP-D3")
kit.claim("CL-D3-BRACE-KY", "Brace lateral axial stiffness at the ear, upper (information)", calc="CALC-D3-BRACE",
          output="ky", unit="N/m", parts=["FIN-009-UR"],
          how="Information only since C4 CR-C4-16: the brace stores 2-6 % of the modal strain energy; the mode check "
              "is CL-C4-D3-SEP (two layers, brace 10 x 2: 0.39)")
kit.claim("CL-D3-BRACE-L", "Brace length (upper), D3 geometry", calc="CALC-D3-BRACE", output="L", unit="m",
          parts=["FIN-009-UR"], how="Measure on the jig")
kit.claim("CL-D3-BRACE-DZ", "Brace attach depth below the motor axis, D3 geometry", calc="CALC-D3-BRACE",
          output="attach_dz", unit="m", parts=["FIN-008-UR"],
          how="C4 modelled this value (CL-C4-D3-*); kept at R3 by the 12 mm ear flush with the collar top")

kit.claim("CL-D3-WIRE-HOLE-CLEAR", "ESC-lead hole: least clearance of the grommet flange to the root joint, boss and "
          "ESC pad", calc="CALC-D3-WIRE-HOLE", output="min", unit="m", limit=(">=", 0.001), verifies=["R-STRUCT-MARGIN"],
          parts=HF, how="Measure the drilled hole position on the dry fit (BUILD.md step 11a)",
          note="F2's 10 mm off the skin would put the hole edge 6 mm up, inside the 12 mm fillet and 15 mm tape lap "
               "(clearance -10 mm); D3 set 22 mm (CR-D3-23 to F2)")

for tid, title, ver, proc in (
        ("T-D3-SLIP", "Mount slip setting", ["CL-D3-SLIP-FUSE", "CL-D3-SLIP-HOLD"],
         "luggage scale hooked on the motor can, pull along y; adjust the pinch bolt until the collar turns at 85-100 N"),
        ("T-D3-ROOT", "Half-fin root side pull", ["CL-D3-ROOT-FILLET-RF"],
         "half-fin bonded to a core offcut per BUILD.md; pull at the TE tip along y to 35 N, then to failure"),
        ("T-D3-EYE", "Strap eye pull", ["CL-D3-STRAP-EYE-RF"],
         "printed block offcut with one eye; spring scale through the eye along z and along y to 60 N, then to failure"),
        ("T-D3-WEIGH", "Weigh every fins part", ["CL-D3-MASS"], "1 g scale; update mass_g and status VERIFIED")):
    kit.test(tid, title, ver, procedure=proc)


def _mass():
    d = json.loads((ROOT / "subsystems" / "fins" / "interfaces.json").read_text(encoding="utf-8"))
    return round(sum(p["mass_g"] for p in d["parts"]), 1)


kit.claim("CL-D3-MASS", "Fins subsystem flying mass, design R3", value=_mass(), unit="g",
          limit=("<=", "P:mass.allocation_g.fins"), verifies=["R-MASS-ALLOC"], parts=HF,
          how="T-D3-WEIGH; sum of subsystems/fins/interfaces.json",
          note="from make_fins.py (CAD volumes x densities). Over the 408 g allocation: the R3 joint additions (16 mm "
               "collar with 40 mm two-face tail, pins, strap eyes) were not in C4's 402 g basis; CR-D3-16 to A1")

if __name__ == "__main__":
    kit.write()
