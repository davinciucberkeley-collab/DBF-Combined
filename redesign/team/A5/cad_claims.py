"""A5 CAD lead: geometry claims other roles build on (hinge line, spar cover, elevon gaps, layout CG, hover split).

Run:  python -I redesign/team/A5/cad_claims.py      then  python -I redesign/proofs/build_graph.py
Every calculation is a pure function of params.json ids and the A5 assumptions below; the section geometry uses
redesign/fusion/k09kit.py (the same helper the CAD modules use), so the CAD and the claims cannot disagree.
Section: subsystems/wing/s5010.dat (B2's UIUC file, copied 2026-11-09, CR-B2-04 / CR-A1-12), carried into the
graph as assumption ASM-A5-SECTION so the calculations stay pure.
The layout CG reproduces the R3 skeleton (redesign/fusion/skeleton) in closed form: allocated masses at the
DATUMS.md stations. The R3 datums D3 and D5 own (brace ends, motor face, pad contact) and D2's pack station are read
from their subsystem params.json files (P:fin_detail.*, P:landing.*, P:pack_aft_face_m), the same keys k09kit reads. Running this script also builds the skeleton on the stub backend and stops if the two
differ by more than 1 mm (cross-check printed at the end).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
sys.path.insert(0, str(REDESIGN / "proofs"))
sys.path.insert(0, str(REDESIGN / "fusion"))
import proofkit as pk  # noqa: E402
import k09kit as k9    # noqa: E402
import fusionkit as fk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/fins/params.json",
                              "../../subsystems/landing/params.json", "../../subsystems/pod/params.json"])
P = "P:"
DAT = REDESIGN / "subsystems" / "wing" / "s5010.dat"
_COORDS = [[round(x, 6), round(y, 6)] for x, y in k9.read_dat(str(DAT))]

# ---------------------------------------------------------------- assumptions
kit.assumption("ASM-A5-SECTION", "Wing section coordinates (S5010)",
               "Normalised Selig-order coordinates of the S5010 read from subsystems/wing/s5010.dat, the file CAD lofts",
               basis="B2's copy of the UIUC coordinate file (URL and checked date in its header line); D1 owns the "
                     "subsystems/wing copy; params wing.airfoil = S5010 (CHANGE-LOG D-02)",
               value=_COORDS, unit="-", cites=["SRC-S5010"])
kit.assumption("ASM-A5-MIN-COVER", "Minimum foam over the spar",
               "Hot-wired XPS must keep at least 2 mm of foam between the spar tube and the skin on both surfaces",
               basis="A5 modelling standard: thinner foam tears when the slot is cut and the tube bonded; G2 confirms on a test core",
               value=0.002, unit="m", cites=["SRC-K09-CARD"])
kit.assumption("ASM-A5-MIN-GAP", "Minimum elevon end gap",
               "Each elevon panel end stays at least 10 mm from the pod side, the fin face and the wing tip",
               basis="A5 modelling standard: room for tape, a horn and +/-25 deg travel without rubbing; D6 confirms",
               value=0.010, unit="m", cites=["SRC-K09-CARD"])
kit.assumption("ASM-A5-MASS-SPLIT", "Allocation split and lump stations used for the layout CG (R3 skeleton)",
               "Within each allocation: wing = spar (mass/m x length); the rest split between core and elevon panels "
               "with the tape skin by planform area and foam/fill/consumables by section volume; fins = 2 tubes "
               "(spar mass/m x tube length) + per station mount 11.0, station collar 10.6, CF brace 5.2, anchor 3.2 g "
               "+ 2 x 41.0 g through-core blocks (D3 R3 CAD unit masses, rounded) and 4 half-fins carrying the rest "
               "(board, edge strips, pins, ESC pad, plug share); propulsion = 4 x prop (params) at the prop plane + rest "
               "(motor, ESC, adapter, nut) as the motor envelope from DP-MOTOR-FACE; power = pack at the D-24 station "
               "(D2's aft face less half the pack length) + rest at the pod nose; pod and avionics in the pod; mechanisms "
               "23.5 mm ahead of the hinge; harness as two bundle legs (channel 14 mm aft of the spar surface, tube "
               "inboard face); feet from 12 mm ahead of the TE to DP-GROUND; printed walls 3 mm; growth reserve not placed",
               basis="params.json#mass.allocation_g (CHANGE-LOG D-38) and subsystems/fins/parts.csv (D3 R3); the skeleton "
                     "modules (redesign/fusion/skeleton/*/fusion) use the same numbers",
               value=None, unit=None, status="UNVERIFIED", cites=["SRC-K09-CARD", "SRC-K09-REVIEW"])

WALL, FOOT_CAP = 0.003, 0.012                               # skeleton constants (ASM-A5-MASS-SPLIT)
MOUNT_G, BLOCK_G, COLLAR_G, BRACE_G, ANCHOR_G = 11.0, 41.0, 10.6, 5.2, 3.2
BLOCK_HALF_Y, CHANNEL_AFT, SHAFT_R, TIP_OFF = 0.012, 0.014, 0.0025, 0.03


def _sec(coords):
    return [tuple(p) for p in coords]


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-A5-HINGE", title="Elevon hinge line", assumes=["ASM-A5-SECTION"],
          equation="x_h = c (1 - f) ; z_h = upper surface at x_h/c ; t_h = section thickness at the hinge",
          inputs={"c": P + "wing.chord_m", "f": P + "wing.elevon.chord_frac", "sec": "ASM-A5-SECTION"},
          units={"c": "m"})
def hinge(c, f, sec):
    s = _sec(sec)
    h = 1 - f
    return {"x_m": c * h, "z_m": k9.surface_z(s, c, h, "upper"), "thickness_m": k9.thickness_at(s, c, h),
            "elevon_chord_m": c * f}


@kit.calc("CALC-A5-SPAR-COVER", title="Foam cover over the spar", assumes=["ASM-A5-SECTION"],
          equation="cover_up = z_upper(x_s) - (z_s + r) ; cover_lo = (z_s - r) - z_lower(x_s) ; "
                   "z_camber = (z_upper + z_lower)/2 ; cover_on_camber = (t(x_s) - 2r)/2",
          inputs={"c": P + "wing.chord_m", "sec": "ASM-A5-SECTION",
                  "x_s": P + "wing.spar.x_m", "z_s": P + "wing.spar.z_m", "od": P + "wing.spar.od_m"},
          units={"c": "m", "x_s": "m", "z_s": "m", "od": "m"})
def spar_cover(c, sec, x_s, z_s, od):
    s = _sec(sec)
    f, r = x_s / c, od / 2
    zu, zl = k9.surface_z(s, c, f, "upper"), k9.surface_z(s, c, f, "lower")
    up, lo = zu - (z_s + r), (z_s - r) - zl
    return {"cover_upper_m": up, "cover_lower_m": lo, "cover_min_m": min(up, lo),
            "z_camber_m": (zu + zl) / 2, "cover_on_camber_m": ((zu - zl) - 2 * r) / 2}


@kit.calc("CALC-A5-ELEVON-GAPS", title="Elevon end gaps",
          equation="pod = distance between the inboard panel (x >= x_h, y >= y_in0) and the pod box (x <= x_pod + L, "
                   "|y| <= w_pod/2) = hypot(max(0, x_h - x_pod_end), max(0, y_in0 - w_pod/2)) ; "
                   "fin_in = (y_fin - t_fin/2) - y_in1 ; fin_out = y_out0 - (y_fin + t_fin/2) ; "
                   "tip = b/2 - y_out1 ; t_fin = layers t_board ; x_h = c (1 - f)",
          inputs={"yin": P + "wing.elevon.inboard_y_m", "yout": P + "wing.elevon.outboard_y_m",
                  "pod": P + "pod.size_m", "pod_x": P + "pod.x_le_m", "c": P + "wing.chord_m",
                  "f": P + "wing.elevon.chord_frac", "y_fin": P + "fins.y_m", "layers": P + "fins.layers",
                  "t_board": P + "fins.board_t_m", "b": P + "wing.span_m"},
          units={"yin": "m", "yout": "m", "pod": "m", "pod_x": "m", "c": "m", "y_fin": "m", "t_board": "m", "b": "m"})
def elevon_gaps(yin, yout, pod, pod_x, c, f, y_fin, layers, t_board, b):
    t = layers * t_board
    dx = max(0.0, c * (1 - f) - (pod_x + pod[0]))          # pod aft end ahead of the hinge line
    dy = max(0.0, yin[0] - pod[1] / 2)                  # pod side to the panel's inboard end
    g = {"gap_pod_m": (dx * dx + dy * dy) ** 0.5, "gap_fin_inboard_m": (y_fin - t / 2) - yin[1],
         "gap_fin_outboard_m": yout[0] - (y_fin + t / 2), "gap_tip_m": b / 2 - yout[1]}
    g["gap_min_m"] = min(g.values())
    g["gap_pod_spanwise_m"] = yin[0] - pod[1] / 2
    g["pod_end_to_hinge_m"] = c * (1 - f) - (pod_x + pod[0])
    g["fin_thickness_m"] = t
    return g


@kit.calc("CALC-A5-LAYOUT-CG", title="Layout CG: allocations at the R3 datum stations",
          assumes=["ASM-A5-MASS-SPLIT", "ASM-A5-SECTION"],
          equation="x_cg = sum(m_i x_i) / sum(m_i), z likewise (lump centroids from the k09kit geometry); "
                   "pack x for x_target = x_pack + M (x_target - x_cg) / m_pack ; range use = |x_cg - mid| / half "
                   "range ; hover split upper/lower = (z_m + z_cg) / (z_m - z_cg)",
          inputs={"a_wing": P + "mass.allocation_g.wing", "a_fins": P + "mass.allocation_g.fins",
                  "a_pod": P + "mass.allocation_g.pod", "a_land": P + "mass.allocation_g.landing",
                  "a_prop": P + "mass.allocation_g.propulsion", "a_pwr": P + "mass.allocation_g.power",
                  "a_avn": P + "mass.allocation_g.avionics", "a_hrn": P + "mass.allocation_g.harness",
                  "a_mec": P + "mass.allocation_g.mechanisms", "m_pack_kg": P + "battery.mass_kg",
                  "spar_kgm": P + "wing.spar.mass_per_m_kgm", "spar_l": P + "wing.spar.length_m",
                  "prop_kg": P + "propulsion.prop_mass_kg",
                  "c": P + "wing.chord_m", "sec": "ASM-A5-SECTION", "f": P + "wing.elevon.chord_frac",
                  "b": P + "wing.span_m", "skin_kgm2": P + "wing.skin.areal_mass_kgm2",
                  "yin": P + "wing.elevon.inboard_y_m", "yout": P + "wing.elevon.outboard_y_m",
                  "x_s": P + "wing.spar.x_m", "z_s": P + "wing.spar.z_m", "od_s": P + "wing.spar.od_m",
                  "xt": P + "fins.tube.x_m", "te": P + "fins.te_x_m", "od": P + "fins.tube.od_m",
                  "y_fin": P + "fins.y_m", "hh": P + "fins.half_height_m",
                  "can_l": P + "propulsion.motor_length_m", "can_d": P + "propulsion.motor_diameter_m",
                  "x_mount": P + "propulsion.stations.x_mount_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "z_m": P + "propulsion.stations.z_m", "foot": P + "cg.foot_height_m", "pod_x": P + "pod.x_le_m",
                  "pod_size": P + "pod.size_m", "pod_z": P + "pod.z_base_m", "pack_size": P + "battery.size_m",
                  "x_target": P + "cg.x_target_m", "x_range": P + "cg.x_range_m", "z_range": P + "cg.z_range_m",
                  "tube_l": P + "fins.tube.length_m", "bond_gap": P + "fin_detail.bond_gap_m",
                  "col_wall": P + "fin_detail.mount.collar_wall_m", "face_ahead": P + "fin_detail.mount.face_ahead_m",
                  "grip": P + "fin_detail.mount.grip_m", "plate_hz": P + "fin_detail.mount.plate_half_z_m",
                  "sc_gap": P + "fin_detail.station_collar.gap_m", "sc_h": P + "fin_detail.station_collar.height_m",
                  "ear_h": P + "fin_detail.station_collar.ear_h_m", "tail": P + "fin_detail.station_collar.tail_m",
                  "proud": P + "fin_detail.anchor.proud_m", "blk_wall": P + "fin_detail.block.wall_m",
                  "pack_aft": P + "pack_aft_face_m"},
          units={"a_wing": "g", "a_fins": "g", "a_pod": "g", "a_land": "g", "a_prop": "g", "a_pwr": "g", "a_avn": "g",
                 "a_hrn": "g", "a_mec": "g", "m_pack_kg": "kg", "spar_kgm": "kg/m", "spar_l": "m", "prop_kg": "kg",
                 "c": "m", "b": "m", "skin_kgm2": "kg/m2", "yin": "m", "yout": "m", "x_s": "m", "z_s": "m", "od_s": "m", "xt": "m", "te": "m", "od": "m", "y_fin": "m",
                 "hh": "m", "can_l": "m", "can_d": "m", "x_mount": "m", "x_prop": "m", "z_m": "m", "foot": "m",
                 "pod_x": "m", "pod_size": "m", "pod_z": "m", "pack_size": "m", "x_target": "m", "x_range": "m",
                 "z_range": "m", "tube_l": "m", "bond_gap": "m", "col_wall": "m", "face_ahead": "m", "grip": "m",
                 "plate_hz": "m", "sc_gap": "m", "sc_h": "m", "ear_h": "m", "tail": "m", "proud": "m", "blk_wall": "m",
                 "pack_aft": "m"})
def layout_cg(a_wing, a_fins, a_pod, a_land, a_prop, a_pwr, a_avn, a_hrn, a_mec, m_pack_kg, spar_kgm, spar_l, prop_kg,
              c, sec, f, b, skin_kgm2, yin, yout, x_s, z_s, od_s, xt, te, od, y_fin, hh, can_l, can_d, x_mount, x_prop, z_m, foot, pod_x,
              pod_size, pod_z, pack_size, x_target, x_range, z_range, tube_l, bond_gap, col_wall, face_ahead, grip,
              plate_hz, sc_gap, sc_h, ear_h, tail, proud, blk_wall, pack_aft):
    s = _sec(sec)
    cen = lambda loop: fk.poly_area_centroid(loop)
    spar_g = spar_kgm * spar_l * 1000.0
    # wing: core = front loop over the span + aft loop where there is no elevon; elevons = aft loop over their spans.
    # Skin by planform area, the rest by volume (same rule as make_skeleton.wing_split)
    hf = 1 - f
    af, (fx, fz) = cen(k9.section_loop(s, c, (0.0, 0.0), 0.0, hf, 32))
    aa, (ax_, az) = cen(k9.section_loop(s, c, (0.0, 0.0), hf, 1.0, 8))
    cs = a_wing - spar_g
    skin = min(cs, skin_kgm2 * 2 * c * b * 1.02 * 1000.0)
    m_el = 0.0
    for y0, y1 in (yin, yout):
        L = y1 - y0
        m_el += 2 * round((cs - skin) * aa * L / ((af + aa) * b) + skin * (1 - hf) * L / b, 1)
    l_el = 2 * ((yin[1] - yin[0]) + (yout[1] - yout[0]))
    vf, va = af * b, aa * (b - l_el)
    sx, sz = (vf * fx + va * ax_) / (vf + va), (vf * fz + va * az) / (vf + va)
    # fins (R3): half-fins (upper + lower, area-weighted), tubes, blocks; mounts, collars and feet are exact z-mirrors
    # (z cancels); braces from DX-COLLAR to DX-ANCHOR; anchors from the spar face to proud of the skin
    _, (hu_x, hu_z) = cen(k9.half_fin_outline(s, c, xt + od / 2, te, hh))
    _, (hl_x, hl_z) = cen(k9.half_fin_outline(s, c, xt + od / 2, te, -hh))
    tube_g = spar_kgm * tube_l * 1000.0
    m_hf = (a_fins - 2 * tube_g - 2 * BLOCK_G - 4 * (MOUNT_G + COLLAR_G + BRACE_G + ANCHOR_G)) / 4
    _, (bx, bz) = cen(k9.section_loop(s, c, (0.0, 0.0), (xt - od / 2 - blk_wall) / c, (x_s + od_s / 2 + blk_wall) / c, 8))
    face = xt - od / 2 - bond_gap - col_wall - face_ahead                  # DP-MOTOR-FACE
    mount_x = (face + xt + od / 2 + WALL) / 2
    collar_x = (xt - od / 2 - WALL + xt + od / 2 + tail) / 2
    z_ear = tube_l / 2 - grip - sc_gap - ear_h / 2                          # DX-COLLAR |z|
    zs_u, zs_l = k9.surface_z(s, c, x_s / c, "upper"), k9.surface_z(s, c, x_s / c, "lower")
    za_u, za_l = zs_u + proud / 2, zs_l - proud / 2                         # DX-ANCHOR z, upper / lower
    brace_z = ((z_ear + za_u) / 2 + (-z_ear + za_l) / 2) / 2                # mean of the four brace midpoints
    anchor_z = ((z_s + od_s / 2 + zs_u + proud) / 2 + (zs_l - proud + z_s - od_s / 2) / 2) / 2
    # propulsion: motor envelope (can + shaft to the prop plane), prop disc
    shaft_l = (face - can_l) - x_prop
    R = can_d / 2
    _, ca = fk.revolve_volume_centroid([(0, 0), (0, R), (-can_l, R), (-can_l, SHAFT_R), (-can_l - shaft_l, SHAFT_R),
                                        (-can_l - shaft_l, 0)])
    prop_g = prop_kg * 1000.0
    # harness: channel leg (pod side -> block face) and tube leg, mass by length
    x_ch = x_s + od_s / 2 + CHANNEL_AFT
    z_ch = (k9.surface_z(s, c, x_ch / c, "upper") + k9.surface_z(s, c, x_ch / c, "lower")) / 2
    ztop = z_m - TIP_OFF
    l_a, l_b = (y_fin - BLOCK_HALF_Y) - pod_size[1] / 2, 2 * ztop
    m_pack = m_pack_kg * 1000.0
    pod_cx, pod_cz = pod_x + pod_size[0] / 2, pod_z + pod_size[2] / 2
    pack_x = pack_aft[0] - pack_size[0] / 2                                 # D-24 station (D2's aft face)
    tray = pod_z + WALL
    pack_z = tray + pack_size[2] / 2
    pwr_x1 = min(pod_x + 0.005 + 0.02, pack_x - pack_size[0] / 2)
    items = [  # (mass g, x m, z m)
        (cs - m_el, sx, sz), (m_el, ax_, az), (spar_g, x_s, z_s),
        (2 * m_hf, hu_x, hu_z), (2 * m_hf, hl_x, hl_z),                 # each half-fin carries m_hf
        (2 * tube_g, xt, 0.0), (4 * MOUNT_G, mount_x, 0.0), (2 * BLOCK_G, bx, bz),
        (4 * COLLAR_G, collar_x, 0.0), (4 * BRACE_G, (xt + x_s) / 2, brace_z), (4 * ANCHOR_G, x_s, anchor_z),
        (a_prop - 4 * prop_g, face + ca, 0.0), (4 * prop_g, x_prop, 0.0),
        (a_land, (te - FOOT_CAP + te + foot) / 2, 0.0),
        (a_pod, pod_cx, pod_cz), (m_pack, pack_x, pack_z),
        (a_pwr - m_pack, (pod_x + 0.005 + pwr_x1) / 2, tray + 0.01),
        (a_avn, pod_x + 0.095, pod_z + pod_size[2] - 0.0115),
        (a_mec, c * (1 - f) - 0.0235, 0.0),
        (a_hrn * l_a / (l_a + l_b), x_ch, z_ch), (a_hrn * l_b / (l_a + l_b), xt, 0.0)]
    M = sum(m for m, _, _ in items)
    x = sum(m * xi for m, xi, _ in items) / M
    z = sum(m * zi for m, _, zi in items) / M
    pack_req = pack_x + M * (x_target - x) / m_pack
    mid, half = (x_range[0] + x_range[1]) / 2, (x_range[1] - x_range[0]) / 2
    return {"mass_g": M, "cg_x_m": x, "cg_z_m": z, "cg_x_frac_chord": x / c,
            "cg_x_fwd_limit_m": x_range[0], "cg_x_aft_limit_m": x_range[1], "cg_z_up_limit_m": z_range[1],
            "cg_x_range_use": abs(x - mid) / half, "pack_x_m": pack_x,
            "pack_x_for_target_m": pack_req, "pack_shift_m": pack_req - pack_x,
            "hover_upper_pair_share": (z_m + z) / (2 * z_m), "hover_split_ratio": (z_m + z) / (z_m - z)}


# ---------------------------------------------------------------- claims
kit.claim("CL-A5-HINGE-X", "Elevon hinge line station", calc="CALC-A5-HINGE", output="x_m", unit="m",
          parts=["WNG-001"], how="Datum DP-HINGE in Fusion (00 Datums); on the core, measure from the LE to the hinge cut.")
kit.claim("CL-A5-HINGE-Z", "Hinge height (upper skin at the hinge)", calc="CALC-A5-HINGE", output="z_m", unit="m",
          assumes=["ASM-A5-SECTION"], parts=["WNG-001"],
          how="On the first cut core, height of the upper skin at the hinge cut above the chord line (G2).")
kit.claim("CL-A5-SPAR-COVER", "Foam over the spar, thinner side", calc="CALC-A5-SPAR-COVER", output="cover_min_m", unit="m",
          limit=(">=", "ASM-A5-MIN-COVER"), assumes=["ASM-A5-SECTION"], parts=["WNG-001", "WNG-002"],
          how="Spar at params wing.spar.z_m (D-03). Check on the first cut core with a depth gauge on both surfaces (G2).")
kit.claim("CL-A5-SPAR-Z-CAMBER", "Camber-line height at the spar station", calc="CALC-A5-SPAR-COVER", output="z_camber_m",
          unit="m", assumes=["ASM-A5-SECTION"],
          how="Compare with params wing.spar.z_m (B2's CL-B2-SPAR-Z-MID); the slot jig is cut to this height.")
kit.claim("CL-A5-SPAR-COVER-CAMBER", "Foam over the spar if centred on the camber line", calc="CALC-A5-SPAR-COVER",
          output="cover_on_camber_m", unit="m", limit=(">=", "ASM-A5-MIN-COVER"), assumes=["ASM-A5-SECTION"],
          how="Same core check (T-A5-CORE-COVER).")
kit.claim("CL-A5-ELEVON-GAP-MIN", "Smallest elevon end gap", calc="CALC-A5-ELEVON-GAPS", output="gap_min_m", unit="m",
          limit=(">=", "ASM-A5-MIN-GAP"), verifies=["R-ELEVON-AREA"],
          how="check.py --skeleton (bounding boxes); on the aircraft, feeler gauge at each panel end at +/-25 deg.")
kit.claim("CL-A5-CG-X-AFT-LIMIT", "Aft CG limit (params cg.x_range_m[1])", calc="CALC-A5-LAYOUT-CG",
          output="cg_x_aft_limit_m", unit="m", how="B3 re-derives the range at R1 geometry (CHANGE-LOG D-17, CR-A1-10).")
kit.claim("CL-A5-CG-X-FWD-LIMIT", "Forward CG limit (params cg.x_range_m[0])", calc="CALC-A5-LAYOUT-CG",
          output="cg_x_fwd_limit_m", unit="m", how="B3: elevon trim at CLmax (CL-B3-CG-FWD, D-24).")
kit.claim("CL-A5-LAYOUT-CG-X", "Layout CG x (allocations at the R3 datum stations, pack at the D-24 station)",
          calc="CALC-A5-LAYOUT-CG", output="cg_x_m", unit="m", limit=("<=", "CL-A5-CG-X-AFT-LIMIT"),
          verifies=["R-CG-RANGE"],
          assumes=["ASM-A5-MASS-SPLIT", "ASM-A5-SECTION"],
          how="Equals the CAD roll-up (python -I redesign/fusion/check.py --skeleton, TOTAL line; this script stops if they "
              "differ by > 1 mm). A3 replaces the allocations with part masses (MASS-CG.md); H1 balances the built "
              "aircraft on two knife edges (T-A5-CG-BALANCE).")
kit.claim("CL-A5-LAYOUT-CG-X-FWD", "Layout CG x against the forward limit", calc="CALC-A5-LAYOUT-CG",
          output="cg_x_m", unit="m", limit=(">=", "CL-A5-CG-X-FWD-LIMIT"), verifies=["R-CG-RANGE"],
          assumes=["ASM-A5-MASS-SPLIT", "ASM-A5-SECTION"],
          how="Same value as CL-A5-LAYOUT-CG-X, tested against cg.x_range_m[0]; T-A5-CG-BALANCE.")
kit.claim("CL-A5-LAYOUT-CG-X-RANGE-USE", "Layout CG x in the range, |x - mid| / half-range", calc="CALC-A5-LAYOUT-CG",
          output="cg_x_range_use", unit="-", limit=("<=", 1.0), verifies=["R-CG-RANGE"],
          assumes=["ASM-A5-MASS-SPLIT", "ASM-A5-SECTION"],
          how="Same basis as CL-A3-CG-X-RANGE (A3's bottom-up value); T-A5-CG-BALANCE.")
kit.claim("CL-A5-PACK-X-FOR-CG", "Pack centre needed for the CG target", calc="CALC-A5-LAYOUT-CG",
          output="pack_x_for_target_m", unit="m", assumes=["ASM-A5-MASS-SPLIT"], parts=["PWR-001", "POD-002"],
          how="D2/A3: compare with the bay (forward stop subsystems/pod/params.json#fwd_stop_x_m, aft-only spacers); "
              "A3's CL-A3-PACK-X-REQ is the same quantity from the bottom-up model.")
kit.claim("CL-A5-PACK-SHIFT", "Pack shift from the D-24 station for the CG target", calc="CALC-A5-LAYOUT-CG",
          output="pack_shift_m", unit="m", assumes=["ASM-A5-MASS-SPLIT"],
          how="Negative = forward. The bay has aft-only spacers (D2); a forward shift needs the forward stop moved.")
kit.claim("CL-A5-CG-Z-UP-LIMIT", "Upper CG z limit (params cg.z_range_m[1])", calc="CALC-A5-LAYOUT-CG",
          output="cg_z_up_limit_m", unit="m", how="B3 / A1 set the range.")
kit.claim("CL-A5-LAYOUT-CG-Z", "Layout CG z (allocations at the R3 datum stations)", calc="CALC-A5-LAYOUT-CG",
          output="cg_z_m", unit="m", limit=("<=", "CL-A5-CG-Z-UP-LIMIT"), assumes=["ASM-A5-MASS-SPLIT"],
          how="H1: hang the aircraft from two points to find z; A3 tracks in MASS-CG.md.")
kit.claim("CL-A5-HOVER-SPLIT", "Hover pitch-trim thrust split, upper / lower pair", calc="CALC-A5-LAYOUT-CG",
          output="hover_split_ratio", unit="-", limit=("<=", P + "requirements.hover_split_max"),
          assumes=["ASM-A5-MASS-SPLIT"],
          how="B3/E1: differential thrust to trim hover pitch; read from the hover log (motor outputs). A3's "
              "CL-A3-HOVER-SPLIT is the bottom-up value.")

# ---------------------------------------------------------------- integration (assembled designer modules)
def _snapshot():
    """team/A5/integration.json, written by integration_check.py from the delivered subsystems (not from params)."""
    import json
    s = json.loads((HERE / "integration.json").read_text(encoding="utf-8"))
    return {"date": s["date"], "mass_g": s["mass_g"], "cg_m": s["cg_m"], "errors": s["errors"],
            "warnings": s["warnings"], "skeleton_cg_x_m": s["skeleton_cg_m"][0],
            "by_subsystem": {r["sub"]: [r["declared_g"], r["cg_x_m"], r["dcg_x_mm"]] for r in s["subsystems"]}}


kit.assumption("ASM-A5-ASSY-ROLLUP", "Assembled CAD roll-up of the delivered subsystem modules",
               "Declared part masses and CGs (interfaces.json) of the ten modules check.py builds from redesign/subsystems, "
               "summed by merge_check.rollup; per subsystem [mass g, CG x m, share of the CG shift from the R3 skeleton mm]",
               basis="python -I redesign/team/A5/integration_check.py (snapshot team/A5/integration.json, tables in "
                     "INTEGRATION.md); declared masses are the designers' CAD/datasheet numbers, not weighed",
               value=_snapshot(), unit="mixed", status="UNVERIFIED", cites=["SRC-K09-CARD"])


@kit.calc("CALC-A5-ASSY", title="Assembled CAD: mass, CG and check.py result",
          assumes=["ASM-A5-ASSY-ROLLUP"],
          equation="read the roll-up; range use = |x_cg - mid| / half-range; shift = x_cg - x_cg(skeleton)",
          inputs={"snap": "ASM-A5-ASSY-ROLLUP", "x_range": P + "cg.x_range_m", "z_range": P + "cg.z_range_m",
                  "gate_kg": P + "requirements.mtow_gate_kg"},
          units={"snap": "mixed", "x_range": "m", "z_range": "m", "gate_kg": "kg"})
def assy(snap, x_range, z_range, gate_kg):
    x, y, z = snap["cg_m"]
    mid, half = (x_range[0] + x_range[1]) / 2, (x_range[1] - x_range[0]) / 2
    return {"mass_kg": snap["mass_g"] / 1000.0, "cg_x_m": x, "cg_y_m": y, "cg_z_m": z,
            "cg_x_range_use": abs(x - mid) / half, "cg_x_shift_m": x - snap["skeleton_cg_x_m"],
            "check_errors": snap["errors"]}


kit.claim("CL-A5-ASSY-MASS", "Assembled CAD mass (declared part masses, pack 550 g)", calc="CALC-A5-ASSY",
          output="mass_kg", unit="kg", limit=("<=", P + "requirements.mtow_gate_kg"), verifies=["R-MASS-GATE"],
          assumes=["ASM-A5-ASSY-ROLLUP"],
          how="python -I redesign/fusion/check.py (TOTAL line), same basis as A3's CL-A3-MASS-BASIC; weigh the aircraft "
              "(T-A1-WEIGH).")
kit.claim("CL-A5-ASSY-CG-X", "Assembled CAD CG x against the aft limit", calc="CALC-A5-ASSY", output="cg_x_m", unit="m",
          limit=("<=", "CL-A5-CG-X-AFT-LIMIT"), verifies=["R-CG-RANGE"], assumes=["ASM-A5-ASSY-ROLLUP"],
          how="check.py TOTAL line; independent code from A3's mass_rollup.py on the same declared data. T-A5-CG-BALANCE.")
kit.claim("CL-A5-ASSY-CG-X-RANGE-USE", "Assembled CAD CG x, |x - mid| / half-range", calc="CALC-A5-ASSY",
          output="cg_x_range_use", unit="-", limit=("<=", 1.0), verifies=["R-CG-RANGE"], assumes=["ASM-A5-ASSY-ROLLUP"],
          how="Same basis as CL-A3-CG-X-RANGE; T-A5-CG-BALANCE.")
kit.claim("CL-A5-ASSY-CG-SHIFT", "Assembled CG x minus the allocation-layout CG (R3 skeleton)", calc="CALC-A5-ASSY",
          output="cg_x_shift_m", unit="m", assumes=["ASM-A5-ASSY-ROLLUP", "ASM-A5-MASS-SPLIT"],
          how="Per-subsystem shares in team/A5/INTEGRATION.md (they sum to this value).")
kit.claim("CL-A5-ASSY-CG-Z", "Assembled CAD CG z", calc="CALC-A5-ASSY", output="cg_z_m", unit="m",
          limit=("<=", "CL-A5-CG-Z-UP-LIMIT"), assumes=["ASM-A5-ASSY-ROLLUP"],
          how="check.py TOTAL line; H1 hangs the aircraft from two points.")
kit.claim("CL-A5-ASSY-CHECK-ERRORS", "check.py errors on the delivered subsystems", calc="CALC-A5-ASSY",
          output="check_errors", unit="-", limit=("<=", 0), assumes=["ASM-A5-ASSY-ROLLUP"],
          how="python -I redesign/fusion/check.py; the list by role is in team/A5/INTEGRATION.md.")

kit.test("T-A5-CORE-COVER", "Spar cover on the first cut core", verifies=["CL-A5-SPAR-COVER", "CL-A5-SPAR-COVER-CAMBER"],
         state="planned", procedure="Cut a 100 mm core section, cut the slot, depth-gauge foam above and below the slot (G2).")
kit.test("T-A5-CG-BALANCE", "CG balance of the built aircraft",
         verifies=["CL-A5-LAYOUT-CG-X", "CL-A5-LAYOUT-CG-X-FWD", "CL-A5-LAYOUT-CG-X-RANGE-USE", "CL-A5-LAYOUT-CG-Z",
                   "CL-A5-ASSY-CG-X", "CL-A5-ASSY-CG-X-RANGE-USE", "CL-A5-ASSY-CG-Z"],
         state="planned", procedure="Pack in, props on; two knife edges under the wing at the fin roots; mark x (H1).")


def cross_check():
    """Closed form vs the stub-built skeleton roll-up (same params): stop if they differ by more than 1 mm."""
    import build_all
    from backends.stub_backend import StubBackend
    ctx = build_all.build(StubBackend(), *build_all.roots(skeleton=True), log=lambda *a: None)[0]
    M, cg = ctx.rollup()
    P_ = k9.load_params()
    v = lambda k: k9.val(P_, k)
    f = lambda k: k9.val(k9.local("fins"), "fin_detail." + k)
    args = dict(a_wing=v("mass.allocation_g.wing"), a_fins=v("mass.allocation_g.fins"), a_pod=v("mass.allocation_g.pod"),
                a_land=v("mass.allocation_g.landing"), a_prop=v("mass.allocation_g.propulsion"),
                a_pwr=v("mass.allocation_g.power"), a_avn=v("mass.allocation_g.avionics"),
                a_hrn=v("mass.allocation_g.harness"), a_mec=v("mass.allocation_g.mechanisms"),
                m_pack_kg=v("battery.mass_kg"), spar_kgm=v("wing.spar.mass_per_m_kgm"), spar_l=v("wing.spar.length_m"),
                prop_kg=v("propulsion.prop_mass_kg"), c=v("wing.chord_m"), sec=_COORDS, f=v("wing.elevon.chord_frac"),
                b=v("wing.span_m"), skin_kgm2=v("wing.skin.areal_mass_kgm2"), yin=v("wing.elevon.inboard_y_m"),
                yout=v("wing.elevon.outboard_y_m"),
                x_s=v("wing.spar.x_m"), z_s=v("wing.spar.z_m"), od_s=v("wing.spar.od_m"), xt=v("fins.tube.x_m"),
                te=v("fins.te_x_m"), od=v("fins.tube.od_m"), y_fin=v("fins.y_m"), hh=v("fins.half_height_m"),
                can_l=v("propulsion.motor_length_m"), can_d=v("propulsion.motor_diameter_m"),
                x_mount=v("propulsion.stations.x_mount_m"), x_prop=v("propulsion.stations.x_prop_plane_m"),
                z_m=v("propulsion.stations.z_m"), foot=v("cg.foot_height_m"), pod_x=v("pod.x_le_m"),
                pod_size=v("pod.size_m"), pod_z=v("pod.z_base_m"), pack_size=v("battery.size_m"),
                x_target=v("cg.x_target_m"), x_range=v("cg.x_range_m"), z_range=v("cg.z_range_m"),
                tube_l=v("fins.tube.length_m"), bond_gap=f("bond_gap_m"), col_wall=f("mount.collar_wall_m"),
                face_ahead=f("mount.face_ahead_m"), grip=f("mount.grip_m"), plate_hz=f("mount.plate_half_z_m"),
                sc_gap=f("station_collar.gap_m"), sc_h=f("station_collar.height_m"), ear_h=f("station_collar.ear_h_m"),
                tail=f("station_collar.tail_m"), proud=f("anchor.proud_m"), blk_wall=f("block.wall_m"),
                pack_aft=k9.val(k9.local("pod"), "pack_aft_face_m"))
    r = layout_cg(**args)
    dx, dz = r["cg_x_m"] - cg[0], r["cg_z_m"] - cg[2]
    print("cross-check: closed form %.1f g (%.4f, %.4f) m; CAD skeleton %.1f g (%.4f, %.4f) m; dx %.1f mm dz %.1f mm"
          % (r["mass_g"], r["cg_x_m"], r["cg_z_m"], M, cg[0], cg[2], dx * 1000, dz * 1000))
    if abs(dx) > 0.001 or abs(dz) > 0.001 or abs(r["mass_g"] - M) > 0.5:
        raise SystemExit("closed-form layout CG and the skeleton roll-up disagree: fix one before writing claims")


if __name__ == "__main__":
    cross_check()
    kit.write()
