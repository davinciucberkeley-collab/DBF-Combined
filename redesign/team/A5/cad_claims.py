"""A5 CAD lead: geometry claims other roles build on (hinge line, spar cover, elevon gaps, layout CG, hover split).

Run:  python -I redesign/team/A5/cad_claims.py      then  python -I redesign/proofs/build_graph.py
Every calculation is a pure function of params.json ids and the A5 assumptions below; the section geometry uses
redesign/fusion/k09kit.py (the same helper the CAD modules use), so the CAD and the claims cannot disagree.
Section: subsystems/wing/s5010.dat (B2's UIUC file, copied 2026-11-09, CR-B2-04 / CR-A1-12), carried into the
graph as assumption ASM-A5-SECTION so the calculations stay pure.
The layout CG reproduces the R1 skeleton (redesign/fusion/skeleton) in closed form: allocated masses at the
DATUMS.md stations. Running this script also builds the skeleton on the stub backend and stops if the two
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

kit = pk.Kit(__file__, params=["../../params/params.json"])
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
kit.assumption("ASM-A5-MASS-SPLIT", "Allocation split and lump stations used for the layout CG (R1 skeleton)",
               "Within each allocation: wing = spar (mass/m x length); the rest split between core and elevon panels "
               "with the tape skin by planform area and foam/fill/consumables by section volume; fins = "
               "4 half-fins (rest) + 2 x 43 tube + 4 x 18 mount + 2 x 20 through-core block + 2 x 30 clip set; "
               "propulsion = 4 x prop (params) at the prop plane + rest (motor, ESC, adapter, nut) as the motor envelope; "
               "power = pack centred in the pod + rest at the pod nose; pod and avionics in the pod; mechanisms 23.5 mm "
               "ahead of the hinge; harness as two bundle legs (channel 14 mm aft of the spar surface, tube inboard face); "
               "printed walls 3 mm; growth reserve not placed",
               basis="params.json#mass.allocation_g notes (CHANGE-LOG D-07); the skeleton modules "
                     "(redesign/fusion/skeleton/*/fusion) use the same numbers",
               value=None, unit=None, status="UNVERIFIED", cites=["SRC-K09-CARD", "SRC-K09-REVIEW"])

WALL, CLIP_D, TIP_OFF, FOOT_CAP = 0.003, 0.010, 0.03, 0.012   # skeleton constants (ASM-A5-MASS-SPLIT)
TUBE_G, MOUNT_G, BLOCK_G, CLIP_G = 43.0, 18.0, 20.0, 30.0
BLOCK_HALF_Y, CHANNEL_AFT, SHAFT_R = 0.012, 0.014, 0.0025


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
          equation="pod = y_in0 - w_pod/2 ; fin_in = (y_fin - t_fin/2) - y_in1 ; fin_out = y_out0 - (y_fin + t_fin/2) ; "
                   "tip = b/2 - y_out1 ; t_fin = layers t_board",
          inputs={"yin": P + "wing.elevon.inboard_y_m", "yout": P + "wing.elevon.outboard_y_m",
                  "pod": P + "pod.size_m", "y_fin": P + "fins.y_m", "layers": P + "fins.layers",
                  "t_board": P + "fins.board_t_m", "b": P + "wing.span_m"},
          units={"yin": "m", "yout": "m", "pod": "m", "y_fin": "m", "t_board": "m", "b": "m"})
def elevon_gaps(yin, yout, pod, y_fin, layers, t_board, b):
    t = layers * t_board
    g = {"gap_pod_m": yin[0] - pod[1] / 2, "gap_fin_inboard_m": (y_fin - t / 2) - yin[1],
         "gap_fin_outboard_m": yout[0] - (y_fin + t / 2), "gap_tip_m": b / 2 - yout[1]}
    g["gap_min_m"] = min(g.values())
    g["fin_thickness_m"] = t
    return g


@kit.calc("CALC-A5-LAYOUT-CG", title="Layout CG: allocations at the R1 datum stations",
          assumes=["ASM-A5-MASS-SPLIT", "ASM-A5-SECTION"],
          equation="x_cg = sum(m_i x_i) / sum(m_i), z likewise (lump centroids from the k09kit geometry); "
                   "pack x for x_target = x_pack + M (x_target - x_cg) / m_pack ; hover split upper/lower = "
                   "(z_m + z_cg) / (z_m - z_cg)",
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
                  "x_target": P + "cg.x_target_m", "x_range": P + "cg.x_range_m", "z_range": P + "cg.z_range_m"},
          units={"a_wing": "g", "a_fins": "g", "a_pod": "g", "a_land": "g", "a_prop": "g", "a_pwr": "g", "a_avn": "g",
                 "a_hrn": "g", "a_mec": "g", "m_pack_kg": "kg", "spar_kgm": "kg/m", "spar_l": "m", "prop_kg": "kg",
                 "c": "m", "b": "m", "skin_kgm2": "kg/m2", "yin": "m", "yout": "m", "x_s": "m", "z_s": "m", "od_s": "m", "xt": "m", "te": "m", "od": "m", "y_fin": "m",
                 "hh": "m", "can_l": "m", "can_d": "m", "x_mount": "m", "x_prop": "m", "z_m": "m", "foot": "m",
                 "pod_x": "m", "pod_size": "m", "pod_z": "m", "pack_size": "m", "x_target": "m", "x_range": "m",
                 "z_range": "m"})
def layout_cg(a_wing, a_fins, a_pod, a_land, a_prop, a_pwr, a_avn, a_hrn, a_mec, m_pack_kg, spar_kgm, spar_l, prop_kg,
              c, sec, f, b, skin_kgm2, yin, yout, x_s, z_s, od_s, xt, te, od, y_fin, hh, can_l, can_d, x_mount, x_prop, z_m, foot, pod_x,
              pod_size, pod_z, pack_size, x_target, x_range, z_range):
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
    # fins: half-fins (upper + lower, area-weighted), block, clip set (two boxes), mounts (z cancels), tubes
    _, (hu_x, hu_z) = cen(k9.half_fin_outline(s, c, xt + od / 2, te, hh))
    _, (hl_x, hl_z) = cen(k9.half_fin_outline(s, c, xt + od / 2, te, -hh))
    m_hf = (a_fins - 2 * TUBE_G - 4 * MOUNT_G - 2 * BLOCK_G - 2 * CLIP_G) / 4
    _, (bx, bz) = cen(k9.section_loop(s, c, (0.0, 0.0), (xt - od / 2 - WALL) / c, (x_s + od_s / 2 + WALL) / c, 8))
    zr_u = k9.surface_z(s, c, (xt + od / 2) / c, "upper")
    zr_l = k9.surface_z(s, c, (xt + od / 2) / c, "lower")
    ztop = z_m - TIP_OFF
    h_u, h_l = ztop - zr_u, zr_l + ztop
    clip_z = (h_u * (zr_u + ztop) / 2 + h_l * (zr_l - ztop) / 2) / (h_u + h_l)
    face = x_mount - od / 2
    mount_x = (face + xt + od / 2 + WALL) / 2
    # propulsion: motor envelope (can + shaft to the prop plane), prop disc
    shaft_l = (face - can_l) - x_prop
    R = can_d / 2
    _, ca = fk.revolve_volume_centroid([(0, 0), (0, R), (-can_l, R), (-can_l, SHAFT_R), (-can_l - shaft_l, SHAFT_R),
                                        (-can_l - shaft_l, 0)])
    prop_g = prop_kg * 1000.0
    # harness: channel leg (pod side -> block face) and tube leg, mass by length
    x_ch = x_s + od_s / 2 + CHANNEL_AFT
    z_ch = (k9.surface_z(s, c, x_ch / c, "upper") + k9.surface_z(s, c, x_ch / c, "lower")) / 2
    l_a, l_b = (y_fin - BLOCK_HALF_Y) - pod_size[1] / 2, 2 * ztop
    m_pack = m_pack_kg * 1000.0
    pod_cx, pod_cz = pod_x + pod_size[0] / 2, pod_z + pod_size[2] / 2
    tray = pod_z + WALL
    pack_z = tray + pack_size[2] / 2
    pwr_x1 = min(pod_x + 0.005 + 0.02, pod_cx - pack_size[0] / 2)
    items = [  # (mass g, x m, z m)
        (cs - m_el, sx, sz), (m_el, ax_, az), (spar_g, x_s, z_s),
        (2 * m_hf, hu_x, hu_z), (2 * m_hf, hl_x, hl_z),                 # each half-fin carries m_hf
        (2 * TUBE_G, xt, 0.0), (4 * MOUNT_G, mount_x, 0.0), (2 * BLOCK_G, bx, bz),
        (2 * CLIP_G, xt + od / 2 + CLIP_D / 2, clip_z),
        (a_prop - 4 * prop_g, face + ca, 0.0), (4 * prop_g, x_prop, 0.0),
        (a_land, (te - FOOT_CAP + te + foot) / 2, 0.0),
        (a_pod, pod_cx, pod_cz), (m_pack, pod_cx, pack_z),
        (a_pwr - m_pack, (pod_x + 0.005 + pwr_x1) / 2, tray + 0.01),
        (a_avn, pod_x + 0.095, pod_z + pod_size[2] - 0.0115),
        (a_mec, c * (1 - f) - 0.0235, 0.0),
        (a_hrn * l_a / (l_a + l_b), x_ch, z_ch), (a_hrn * l_b / (l_a + l_b), xt, 0.0)]
    M = sum(m for m, _, _ in items)
    x = sum(m * xi for m, xi, _ in items) / M
    z = sum(m * zi for m, _, zi in items) / M
    pack_x = pod_cx + M * (x_target - x) / m_pack
    return {"mass_g": M, "cg_x_m": x, "cg_z_m": z, "cg_x_frac_chord": x / c,
            "cg_x_fwd_limit_m": x_range[0], "cg_x_aft_limit_m": x_range[1], "cg_z_up_limit_m": z_range[1],
            "pack_x_for_target_m": pack_x, "pack_shift_m": pack_x - pod_cx,
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
kit.claim("CL-A5-LAYOUT-CG-X", "Layout CG x (allocations at the R1 datum stations, pack centred)", calc="CALC-A5-LAYOUT-CG",
          output="cg_x_m", unit="m", limit=("<=", "CL-A5-CG-X-AFT-LIMIT"), verifies=["R-STATIC-MARGIN"],
          assumes=["ASM-A5-MASS-SPLIT", "ASM-A5-SECTION"],
          how="Equals the CAD roll-up (python -I redesign/fusion/check.py --skeleton, TOTAL line; this script stops if they "
              "differ by > 1 mm). A3 replaces the allocations with part masses (MASS-CG.md); H1 balances the built "
              "aircraft on two knife edges (T-A5-CG-BALANCE).")
kit.claim("CL-A5-PACK-X-FOR-CG", "Pack centre needed for the CG target", calc="CALC-A5-LAYOUT-CG",
          output="pack_x_for_target_m", unit="m", assumes=["ASM-A5-MASS-SPLIT"], parts=["PWR-001", "POD-002"],
          how="D2/A3: compare with the pod (nose at pod.x_le_m) and the +/-0.03 m tray slide; A3's CL-A3-PACK-X-REQ is "
              "the same quantity from the bottom-up model.")
kit.claim("CL-A5-PACK-SHIFT", "Pack shift from the pod centre for the CG target", calc="CALC-A5-LAYOUT-CG",
          output="pack_shift_m", unit="m", assumes=["ASM-A5-MASS-SPLIT"],
          how="Negative = forward. D2 provides +/-0.03 m of slide (params pod.x_le_m note); beyond that the pod moves (D-17).")
kit.claim("CL-A5-CG-Z-UP-LIMIT", "Upper CG z limit (params cg.z_range_m[1])", calc="CALC-A5-LAYOUT-CG",
          output="cg_z_up_limit_m", unit="m", how="B3 / A1 set the range.")
kit.claim("CL-A5-LAYOUT-CG-Z", "Layout CG z (allocations at the R1 datum stations)", calc="CALC-A5-LAYOUT-CG",
          output="cg_z_m", unit="m", limit=("<=", "CL-A5-CG-Z-UP-LIMIT"), assumes=["ASM-A5-MASS-SPLIT"],
          how="H1: hang the aircraft from two points to find z; A3 tracks in MASS-CG.md.")
kit.claim("CL-A5-HOVER-SPLIT", "Hover pitch-trim thrust split, upper / lower pair", calc="CALC-A5-LAYOUT-CG",
          output="hover_split_ratio", unit="-", limit=("<=", P + "requirements.hover_split_max"),
          assumes=["ASM-A5-MASS-SPLIT"],
          how="B3/E1: differential thrust to trim hover pitch; read from the hover log (motor outputs). A3's "
              "CL-A3-HOVER-SPLIT is the bottom-up value.")

kit.test("T-A5-CORE-COVER", "Spar cover on the first cut core", verifies=["CL-A5-SPAR-COVER", "CL-A5-SPAR-COVER-CAMBER"],
         state="planned", procedure="Cut a 100 mm core section, cut the slot, depth-gauge foam above and below the slot (G2).")
kit.test("T-A5-CG-BALANCE", "CG balance of the built aircraft", verifies=["CL-A5-LAYOUT-CG-X", "CL-A5-LAYOUT-CG-Z"],
         state="planned", procedure="Pack in, props on; two knife edges under the wing at the fin roots; mark x (H1).")


def cross_check():
    """Closed form vs the stub-built skeleton roll-up (same params): stop if they differ by more than 1 mm."""
    import build_all
    from backends.stub_backend import StubBackend
    ctx = build_all.build(StubBackend(), *build_all.roots(skeleton=True), log=lambda *a: None)[0]
    M, cg = ctx.rollup()
    P_ = k9.load_params()
    v = lambda k: k9.val(P_, k)
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
                x_target=v("cg.x_target_m"), x_range=v("cg.x_range_m"), z_range=v("cg.z_range_m"))
    r = layout_cg(**args)
    dx, dz = r["cg_x_m"] - cg[0], r["cg_z_m"] - cg[2]
    print("cross-check: closed form %.1f g (%.4f, %.4f) m; CAD skeleton %.1f g (%.4f, %.4f) m; dx %.1f mm dz %.1f mm"
          % (r["mass_g"], r["cg_x_m"], r["cg_z_m"], M, cg[0], cg[2], dx * 1000, dz * 1000))
    if abs(dx) > 0.001 or abs(dz) > 0.001 or abs(r["mass_g"] - M) > 0.5:
        raise SystemExit("closed-form layout CG and the skeleton roll-up disagree: fix one before writing claims")


if __name__ == "__main__":
    cross_check()
    kit.write()
