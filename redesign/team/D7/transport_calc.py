"""D7 transport and packaging: box height from the drop stroke, clearances, cradle foam, box and loaded mass,
field set-up time. Writes claims.json beside this file.

Run:  python -I redesign/team/D7/transport_calc.py
Inputs: redesign/params/params.json, redesign/subsystems/transport/params.json (keys P:trn.*), C1's drop allowable
(CL-C1-TRANSPORT-N-ALLOW, CL-C1-CRADLE-STROKE-REQ) and crush efficiency (ASM-C1-CRUSH-EFF).

Drop model (C1, CALC-C1-TRANSPORT-N): n_T = 1 + h / (eta s). The aircraft rests on two spar cradles; in a floor drop it
moves down by the crush stroke, so every part below the wing (lower foot pads at z = -0.219 m, D-31) needs the same
free travel above the floor. That travel, not the foam, sets the box height.

Round 2 (CR-A1-35, D-31): box 1.25 x 0.55 x 0.54 m; column 120 mm; no lid lining; cradle pad and brace-gap check;
M3 handle bolts with backing strips.
Round 3 (C1 CR-C1-22, C5 CR-C5-06/-12, I1 CR-I1-18, A4 CR-A4-24): off-axis drops (end, nose, aft = feet, lid-down)
and the lid-pillar bearing; aircraft 12 mm off the aft wall plus a 1 in PE nose pad; the three carried items (box,
battery can, mat + tote); the props-on option (CR-D7-15) as a geometry check only.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/transport/params.json"])
P = "P:"
G = 9.80665

kit.source("SRC-D7-COROPLAST", "Plaskolite 4 mm 48 x 96 in corrugated plastic sheet, 4.99 lb packaged", "web",
           url="https://www.homedepot.ca/product/plaskolite-0-157-inch-x-48-inch-x-96-inch-white-corrugated-plastic-sheet/1000171722",
           note="packaged weight / 2.973 m2 = 0.76 kg/m2, an upper bound; weigh one sheet (T-D7-WEIGH-BOX)",
           status="UNVERIFIED")
kit.source("SRC-D7-PE-FOAM", "Closed-cell polyethylene plank 1.7-2.2 lb/ft3: density, usable strain, cushion band",
           "handbook", note="typical supplier cushion-curve values (EST); no curve checked yet: T-D7-CUSHION decides "
           "the density", status="UNVERIFIED")
kit.assumption("ASM-D7-PACK-OUT", "Packs travel outside the box", "Flight packs ride in a LiPo bag (E2), not in the box; "
               "the aircraft in the box is the gate mass less one pack", basis="LiPo transport practice (E2 owns); keeps "
               "the loaded box under 6 kg", status="PROPOSED")
kit.assumption("ASM-D7-FLAT-DROP", "Design drop is flat on the floor", "The 0.3 m sill drop is designed for a flat "
               "floor impact; side, end and corner impacts are checked by test only", basis="a box slipping off a sill "
               "lands on its floor or a bottom edge; edge drops rotate the box and load less (ISTA practice)",
               status="UNVERIFIED")
kit.assumption("ASM-D7-REBOUND", "Lid pillars stop the rebound before the upper tube ends reach the lid",
               "After the floor drop the aircraft rebounds into the two PE hold-down pillars; they arrest it before the "
               "upper tube ends and foot pads close the 10 mm static gap to the bare lid shell, so the lid needs no lining",
               basis="EST: rebound at e = 0.5 from 2.43 m/s gives ~1.1 J on 2.05 kg; two 100 x 60 mm PE pillars ~0.23 m "
               "tall at ~40 kPa over 15 mm (5 preload + 10 gap) store ~3.6 J (3x). T-D7-BOX-DROP checks it: chalk on the "
               "upper motor caps, no mark on the lid", status="UNVERIFIED")

AC_Z = 2          # index of height in envelope_props_off_m [span y, depth x, height z]


@kit.calc("CALC-D7-STROKE", title="Cradle crush column: stroke, load factor, free travel",
          equation="s_use = eps_use t ; n_T = 1 + h / (eta s_use) ; s_bottom = eps_bottom t ; "
                   "travel_req = s_bottom + margin ; t_req = h / (eta (n_allow - 1) eps_use)",
          inputs={"h": P + "requirements.box_drop_m", "eta": "ASM-C1-CRUSH-EFF", "n_allow": "CL-C1-TRANSPORT-N-ALLOW",
                  "t": P + "trn.cradle.crush_t_m", "eu": P + "trn.foam.eps_use", "eb": P + "trn.foam.eps_bottom",
                  "margin": P + "trn.foam.travel_margin_m"},
          units={"h": "m", "t": "m", "margin": "m"}, assumes=["ASM-D7-FLAT-DROP"], cites=["SRC-D7-PE-FOAM"])
def stroke(h, eta, n_allow, t, eu, eb, margin):
    s_use = eu * t
    s_bot = eb * t
    return {"s_use_m": s_use, "n_T": 1 + h / (eta * s_use), "s_bottom_m": s_bot, "travel_req_m": s_bot + margin,
            "t_req_m": h / (eta * (n_allow - 1) * eu)}


@kit.calc("CALC-D7-BOX-STACK", title="Box stack-up: height needed, clearances, drop allowed by the 0.50 m box",
          equation="floor = shell + doubler ; lid = shell + lining ; H_req = floor + travel_req + env_z + gap_min + lid ; "
                   "travel = H - floor - lid - env_z - gap_min ; clear_bottoming = travel - s_bottom ; "
                   "nose_gap = W - 2 shell - env_x - aft_gap - nose_pad (- nose_ext) ; x_clear = min(nose_gap_ext, aft_gap) ; "
                   "tip_to_pad = (L - 2 shell - env_y) / 2 - pad ; "
                   "A1 box: t_max = (travel_A1 - margin) / eps_bottom, h_allow = (n_allow - 1) eta eps_use t_max",
          inputs={"ext": P + "trn.box.external_m", "ext_a1": P + "requirements.box_external_m",
                  "env": P + "transport.envelope_props_off_m", "shell": P + "trn.box.shell_t_m",
                  "dbl": P + "trn.box.floor_doubler_t_m", "lin": P + "trn.box.lid_lining_t_m",
                  "gap": P + "trn.box.top_gap_min_m", "pad": P + "trn.box.end_pad_t_m",
                  "aft_gap": P + "trn.box.aft_gap_m", "nose_pad": P + "trn.box.nose_pad_t_m", "nose_ext": "CL-C5-NOSE-EXT",
                  "travel_req": "CL-D7-TRAVEL-REQ", "s_bot": "CL-D7-S-BOTTOM", "margin": P + "trn.foam.travel_margin_m",
                  "eb": P + "trn.foam.eps_bottom", "eu": P + "trn.foam.eps_use", "eta": "ASM-C1-CRUSH-EFF",
                  "n_allow": "CL-C1-TRANSPORT-N-ALLOW"},
          units={"ext": "m", "ext_a1": "m", "env": "m", "shell": "m", "dbl": "m", "lin": "m", "gap": "m", "pad": "m",
                 "aft_gap": "m", "nose_pad": "m", "nose_ext": "m", "travel_req": "m", "s_bot": "m", "margin": "m"})
def box_stack(ext, ext_a1, env, shell, dbl, lin, gap, pad, aft_gap, nose_pad, nose_ext, travel_req, s_bot, margin, eb,
              eu, eta, n_allow):
    L, W, H = ext
    floor, lid = shell + dbl, shell + lin
    env_y, env_x, env_z = env
    travel = H - floor - lid - env[AC_Z] - gap
    travel_a1 = ext_a1[2] - floor - lid - env_z - gap
    t_max_a1 = max(0.0, (travel_a1 - margin) / eb)
    return {"H_req_m": floor + travel_req + env_z + gap + lid, "travel_m": travel,
            "clear_bottoming_m": travel - s_bot, "aft_gap_m": aft_gap,
            "nose_gap_m": W - 2 * shell - env_x - aft_gap - nose_pad,
            "nose_gap_ext_m": W - 2 * shell - env_x - aft_gap - nose_pad - nose_ext,
            "x_clear_m": min(W - 2 * shell - env_x - aft_gap - nose_pad - nose_ext, aft_gap),
            "tip_to_pad_m": (L - 2 * shell - env_y) / 2 - pad, "travel_a1_m": travel_a1,
            "h_allow_a1_m": (n_allow - 1) * eta * eu * t_max_a1}


@kit.calc("CALC-D7-CRADLE-PATCH", title="Cradle saddle and pillar footprint against C2 and the brace anchors",
          equation="A_saddle = w (x1 - x0 - relief) ; side_min = min(w, x1 - x0, hx, hy) ; "
                   "gap_brace = y_anchor - (y_c + max(w, hy, fy) / 2)",
          inputs={"w": P + "trn.cradle.width_m", "sx": P + "trn.cradle.saddle_x_m", "yc": P + "trn.cradle.y_m",
                  "hd": P + "trn.holddown.size_m", "fp": P + "trn.cradle.crush_footprint_m",
                  "ya": P + "trn.cradle.brace_anchor_y_in_m", "rx": P + "trn.cradle.relief_x_m"},
          units={"w": "m", "sx": "m", "yc": "m", "hd": "m", "fp": "m", "ya": "m", "rx": "m"})
def cradle_patch(w, sx, yc, hd, fp, ya, rx):
    span = sx[1] - sx[0]
    return {"A_saddle_m2": w * (span - (rx[1] - rx[0])), "A_pillar_m2": hd[0] * hd[1], "side_min_m": min(w, span, hd[0], hd[1]),
            "gap_brace_m": ya - (yc + max(w, hd[1], fp[1]) / 2)}


@kit.calc("CALC-D7-HANDLE", title="Handle bolt load and wall bearing behind the 140 x 30 mm backing strip",
          equation="F_bolt = m_loaded (2 g) / 2 ; p = 2 F_bolt / (0.140 x 0.030)",
          inputs={"m": "CL-D7-LOADED-MASS"}, units={"m": "kg"})
def handle(m):
    f = m * 2 * G / 2
    return {"F_bolt_N": f, "p_strip_kpa": 2 * f / (0.140 * 0.030) / 1000.0}


@kit.calc("CALC-D7-CRADLE-STRESS", title="Static stress on the crush columns",
          equation="sigma = (m_gate - m_pack) g / (2 a b)",
          inputs={"gate": P + "requirements.mtow_gate_kg", "pack": P + "battery.mass_kg",
                  "fp": P + "trn.cradle.crush_footprint_m"},
          units={"gate": "kg", "pack": "kg", "fp": "m"}, assumes=["ASM-D7-PACK-OUT"])
def cradle_stress(gate, pack, fp):
    return {"sigma_kpa": (gate - pack) * G / (2 * fp[0] * fp[1]) / 1000.0}


@kit.calc("CALC-D7-MASS", title="Box mass and loaded mass",
          equation="shell = areal (1 + flaps) [L W + 2 (L + W)(H - t) + L W + 2 (L + W) lip] ; "
                   "box = shell + doublers + lining + end and nose pads + cradles + tray + straps + handles + backing + corners + consumables ; "
                   "loaded = box + (gate - pack) + spare props + pouch",
          inputs={"ext": P + "trn.box.external_m", "t": P + "trn.box.shell_t_m", "lip": P + "trn.box.lid_lip_m",
                  "flaps": P + "trn.box.flap_frac", "areal": P + "trn.mass.coroplast_areal_kgm2", "dbl": P + "trn.box.floor_doubler_t_m",
                  "lin": P + "trn.box.lid_lining_t_m", "rho_pe": P + "trn.foam.pe_density_kgm3",
                  "rho_xps": P + "wing.core.density_kgm3", "pad_t": P + "trn.box.end_pad_t_m",
                  "pad": P + "trn.box.end_pad_size_m", "npt": P + "trn.box.nose_pad_t_m",
                  "nps": P + "trn.box.nose_pad_size_m", "cw": P + "trn.cradle.width_m", "sx": P + "trn.cradle.saddle_x_m",
                  "ct": P + "trn.cradle.crush_t_m", "fp": P + "trn.cradle.crush_footprint_m",
                  "cap": P + "trn.cradle.cap_t_m", "travel": "CL-D7-TRAVEL", "env": P + "transport.envelope_props_off_m",
                  "tray": P + "trn.tray.size_m", "solid": P + "trn.tray.solid_frac",
                  "handle": P + "trn.mass.handle_kg", "backing": P + "trn.mass.handle_backing_kg", "cam": P + "trn.mass.cam_strap_kg",
                  "hd": P + "trn.holddown.size_m", "pre": P + "trn.holddown.preload_m",
                  "gap": P + "trn.box.top_gap_min_m", "corners": P + "trn.mass.corners_kg",
                  "cons": P + "trn.mass.consumables_kg", "pouch": P + "trn.mass.pouch_kg",
                  "spares": P + "trn.mass.spare_props", "prop": P + "propulsion.prop_mass_kg",
                  "gate": P + "requirements.mtow_gate_kg", "pack": P + "battery.mass_kg", "n_packs": P + "battery.n_packs"},
          units={"ext": "m", "t": "m", "lip": "m", "areal": "kg/m2", "rho_pe": "kg/m3", "rho_xps": "kg/m3", "npt": "m",
                 "nps": "m",
                 "gate": "kg", "pack": "kg", "prop": "kg", "handle": "kg", "backing": "kg"},
          assumes=["ASM-D7-PACK-OUT"], cites=["SRC-D7-COROPLAST", "SRC-D7-PE-FOAM"])
def masses(ext, t, lip, flaps, areal, dbl, lin, rho_pe, rho_xps, pad_t, pad, npt, nps, cw, sx, ct, fp, cap, travel, env, tray, solid,
           handle, backing, cam, hd, pre, gap, corners, cons, pouch, spares, prop, gate, pack, n_packs):
    L, W, H = ext
    base_shell = areal * (1 + flaps) * (L * W + 2 * (L + W) * (H - t))
    doublers = areal * 2 * (0.15 * (W - 2 * t)) * (1 if dbl > 0 else 0)   # 150 mm strip under each cradle, if fitted
    pads = 2 * rho_pe * pad_t * pad[0] * pad[1] + rho_pe * npt * nps[0] * nps[1]      # end pads + nose pad
    base = base_shell + doublers + pads + corners + cons        # TRN-001 (corners and consumables booked here)
    lid = areal * (1 + flaps) * (L * W + 2 * (L + W) * lip) + rho_pe * lin * (L - 2 * t) * (W - 2 * t)   # TRN-005
    # saddle: from the column top up to the wing lower surface (~ chord plane), rigid XPS, 70 % solid
    saddle_h = env[AC_Z] / 2 + travel - ct
    cradle = (rho_xps * 0.7 * cw * (sx[1] - sx[0]) * saddle_h + rho_pe * ct * fp[0] * fp[1]
              + rho_pe * cap * cw * (sx[1] - sx[0]))                                  # each, TRN-002-L/R
    tray_m = rho_xps * solid * tray[0] * tray[1] * tray[2]                            # TRN-003
    pillar = rho_pe * hd[0] * hd[1] * (env[AC_Z] / 2 + gap + pre)                     # each, TRN-004-L/R (upper bound)
    box = base + lid + 2 * cradle + tray_m + 2 * pillar + 3 * (handle + backing) + 2 * cam
    aircraft = gate - pack
    loaded = box + aircraft + spares * prop + pouch
    return {"base_kg": base, "lid_kg": lid, "cradle_each_kg": cradle, "tray_kg": tray_m, "pillar_each_kg": pillar,
            "box_kg": box, "aircraft_kg": aircraft, "loaded_kg": loaded, "loaded_with_packs_kg": loaded + n_packs * pack}


@kit.calc("CALC-D7-SETUP", title="Field set-up time, closed box to the arm check",
          equation="T = sum(step seconds) / 60", inputs={"steps": P + "trn.setup_steps_s"}, units={"steps": "s"})
def setup(steps):
    return {"t_min": sum(s for _, s in steps) / 60.0}


@kit.calc("CALC-D7-OFFAXIS", title="Off-axis drops: drop height each face allows, lid-pillar bearing",
          equation="h_end = (nY - 1) eta eps_use t_endpad ; h_nose = (nX - 1) eta eps_use t_nosepad ; "
                   "F_feet = 2 (F_up + F_lo) ; n_aft = F_feet / (m g) ; h_aft = F_feet s_foot / (m g) - aft_gap - s_foot ; "
                   "h_lid = (nLid - 1) eta gap_top ; p_pillar = F_pillar / (a b) ; p_allow = sigma_xps / SF",
          inputs={"nX": "CL-C1-TRANSPORT-N-ALLOW-X", "nY": "CL-C1-TRANSPORT-N-ALLOW-Y",
                  "nL": "CL-C1-TRANSPORT-N-ALLOW-LID", "eta": "ASM-C1-CRUSH-EFF", "eu": P + "trn.foam.eps_use",
                  "t_end": P + "trn.box.end_pad_t_m", "t_nose": P + "trn.box.nose_pad_t_m",
                  "f_up": "CL-C5-CART-PLATEAU-UPPER", "f_lo": "CL-C5-CART-PLATEAU-LOWER",
                  "s_foot": P + "trn.offaxis.foot_stroke_m", "aft_gap": P + "trn.box.aft_gap_m",
                  "gate": P + "requirements.mtow_gate_kg", "pack": P + "battery.mass_kg",
                  "gap_top": P + "trn.box.top_gap_min_m", "f_pil": "CL-C1-PILLAR-F-LIM", "hd": P + "trn.holddown.size_m",
                  "sxps": P + "trn.holddown.xps_bearing_kpa", "sf": P + "trn.holddown.bearing_sf"},
          units={"t_end": "m", "t_nose": "m", "f_up": "N", "f_lo": "N", "s_foot": "m", "aft_gap": "m", "gate": "kg",
                 "pack": "kg", "gap_top": "m", "f_pil": "N", "hd": "m", "sxps": "kPa"},
          assumes=["ASM-D7-PACK-OUT"], cites=["SRC-D7-PE-FOAM"])
def offaxis(nX, nY, nL, eta, eu, t_end, t_nose, f_up, f_lo, s_foot, aft_gap, gate, pack, gap_top, f_pil, hd, sxps, sf):
    w = (gate - pack) * G
    f_feet = 2 * (f_up + f_lo)
    return {"h_end_m": (nY - 1) * eta * eu * t_end, "h_nose_m": (nX - 1) * eta * eu * t_nose,
            "n_aft": f_feet / w, "h_aft_m": f_feet * s_foot / w - aft_gap - s_foot,
            "h_lid_m": (nL - 1) * eta * gap_top, "p_pillar_kpa": f_pil / (hd[0] * hd[1]) / 1000.0,
            "p_allow_kpa": sxps / sf}


@kit.calc("CALC-D7-CARRY", title="The three carried items and who carries what",
          equation="mat = A (ply + rubber) + hinge ; can = can + n_packs (m_pack + bag) ; tote = tote + tx + spares ; "
                   "two people: A = box + tote (shoulder), B = can + mat (one per hand) ; one person: two trips ; "
                   "item_max = max(can, mat, tote)",
          inputs={"mat": P + "trn.field_bag.mat_size_m", "ply": P + "trn.field_bag.mat_ply_kgm2",
                  "rub": P + "trn.field_bag.mat_rubber_kgm2", "hinge": P + "trn.field_bag.mat_hinge_kg",
                  "can": P + "trn.field_bag.can_kg", "bag": P + "trn.field_bag.lipo_bag_kg",
                  "n_packs": P + "battery.n_packs", "pack": P + "battery.mass_kg", "tote": P + "trn.field_bag.tote_kg",
                  "tx": P + "trn.field_bag.tx_kg", "spares": P + "trn.field_bag.landing_spares_kg",
                  "box": "CL-D7-LOADED-MASS"},
          units={"mat": "m", "ply": "kg/m2", "rub": "kg/m2", "hinge": "kg", "can": "kg", "bag": "kg", "pack": "kg",
                 "tote": "kg", "tx": "kg", "spares": "kg", "box": "kg"},
          assumes=["ASM-D7-PACK-OUT"])
def carry(mat, ply, rub, hinge, can, bag, n_packs, pack, tote, tx, spares, box):
    m_mat = mat[0] * mat[1] * (ply + rub) + hinge
    m_can = can + bag + n_packs * pack            # lipo_bag_kg covers both bags
    m_tote = tote + tx + spares
    return {"mat_kg": m_mat, "can_kg": m_can, "tote_kg": m_tote, "item_max_kg": max(m_can, m_mat, m_tote),
            "person_a_kg": box + m_tote, "person_b_kg": m_can + m_mat, "all_kg": box + m_can + m_mat + m_tote}


@kit.calc("CALC-D7-PROPS-ON", title="Option CR-D7-15: props left on, clocked spanwise, in the same box",
          equation="z_top = z_motor + t_blade ; margin_z = env_z / 2 - z_top ; y_in = y_motor - D / 2 ; "
                   "z_col_top = -env_z / 2 - travel + t_col ; saddle_cut = (-z_motor + t_blade) - z_col_top if y_in < y_c + w / 2",
          inputs={"zm": P + "propulsion.stations.z_m", "ym": P + "propulsion.stations.y_m",
                  "D": P + "propulsion.prop_diameter_m", "tb": P + "trn.offaxis.blade_half_t_m",
                  "env": P + "transport.envelope_props_off_m", "travel": "CL-D7-TRAVEL", "ct": P + "trn.cradle.crush_t_m",
                  "yc": P + "trn.cradle.y_m", "cw": P + "trn.cradle.width_m"},
          units={"zm": "m", "ym": "m", "D": "m", "tb": "m", "env": "m", "travel": "m", "ct": "m", "yc": "m", "cw": "m"})
def props_on(zm, ym, D, tb, env, travel, ct, yc, cw):
    z_col_top = -env[AC_Z] / 2 - travel + ct
    y_in = ym - D / 2
    return {"z_margin_m": env[AC_Z] / 2 - (zm + tb), "y_inner_m": y_in,
            "saddle_cut_m": max(0.0, (-zm + tb) - z_col_top) if y_in < yc + cw / 2 else 0.0}


PARTS_BOX = ["TRN-001", "TRN-005"]
PARTS_CR = ["TRN-002-L", "TRN-002-R"]

kit.claim("CL-D7-S-BOTTOM", "Crush column stroke at bottoming", calc="CALC-D7-STROKE", output="s_bottom_m", unit="m",
          parts=PARTS_CR, how="T-D7-CUSHION: crush a column to bottoming on the shop press, measure the stroke.")
kit.claim("CL-D7-TRAVEL-REQ", "Free travel needed under the lower tube ends", calc="CALC-D7-STROKE",
          output="travel_req_m", unit="m", parts=PARTS_CR, how="Ruler in the built box: lower tube end to floor.")
kit.claim("CL-D7-CRADLE-STROKE", "Usable cradle crush stroke", calc="CALC-D7-STROKE", output="s_use_m", unit="m",
          limit=(">=", "CL-C1-CRADLE-STROKE-REQ"), verifies=["R-LOADS", "R-TRANSPORT"], parts=PARTS_CR,
          how="T-D7-CUSHION coupon drop, then T-D7-BOX-DROP with an accelerometer on the spar.")
kit.claim("CL-D7-DROP-N", "Box drop load factor with the 120 mm columns", calc="CALC-D7-STROKE", output="n_T", unit="-",
          limit=("<=", "CL-C1-TRANSPORT-N-ALLOW"), verifies=["R-LOADS", "R-TRANSPORT"], parts=PARTS_CR,
          how="T-D7-BOX-DROP: 0.3 m flat drop of the loaded box, accelerometer on the spar, peak <= n_allow.")
kit.claim("CL-D7-BOX-H-REQ", "External box height needed for the drop stroke", calc="CALC-D7-BOX-STACK",
          output="H_req_m", unit="m", verifies=["R-TRANSPORT"], parts=PARTS_BOX,
          how="Stack-up check on the built box (0.54 m, D-31).")
kit.claim("CL-D7-TRAVEL", "Free travel under the lower tube ends in the 0.54 m box", calc="CALC-D7-BOX-STACK",
          output="travel_m", unit="m", parts=PARTS_BOX, how="Ruler in the built box: lower tube end to floor.")
kit.claim("CL-D7-TUBE-CLEAR-DROP", "Lower tube end to floor when the columns bottom", calc="CALC-D7-BOX-STACK",
          output="clear_bottoming_m", unit="m", limit=(">=", P + "trn.foam.travel_margin_m"), verifies=["R-TRANSPORT"],
          parts=PARTS_BOX + PARTS_CR, assumes=["ASM-D7-REBOUND"], how="T-D7-BOX-DROP: chalk on the lower motor caps and foot pads; no mark on the floor.")
kit.claim("CL-D7-SIDE-CLEAR", "Smaller of pod nose to nose pad (with C5's 9.3 mm nose extension) and foot pads to aft wall",
          calc="CALC-D7-BOX-STACK", output="x_clear_m",
          unit="m", limit=(">=", P + "trn.box.top_gap_min_m"), verifies=["R-TRANSPORT"], parts=PARTS_BOX,
          how="Place the aircraft on the cradles; a 10 mm foam feeler passes between nose and nose pad and between the "
              "foot pads and the aft wall.")
kit.claim("CL-D7-NOSE-GAP", "Pod nose to the nose pad, today's pod (x_le -0.115)", calc="CALC-D7-BOX-STACK",
          output="nose_gap_m", unit="m", limit=(">=", P + "trn.box.top_gap_min_m"), parts=PARTS_BOX,
          how="Ruler in the built box.")
kit.claim("CL-D7-TIP-PAD-GAP", "Wingtip to end pad", calc="CALC-D7-BOX-STACK", output="tip_to_pad_m", unit="m",
          limit=(">=", 0.0), verifies=["R-TRANSPORT"], parts=PARTS_BOX, how="Ruler in the built box.")
kit.claim("CL-D7-A1-BOX-DROP-ALLOW", "Drop height A1's box (requirements.box_external_m) allows, column limited by travel",
          calc="CALC-D7-BOX-STACK", output="h_allow_a1_m", unit="m", limit=(">=", P + "requirements.box_drop_m"),
          verifies=["R-LOADS", "R-TRANSPORT"], parts=PARTS_BOX + PARTS_CR, assumes=["ASM-D7-REBOUND"],
          how="T-D7-BOX-DROP at 0.3 m in the 0.54 m box. If a car forces 0.50 m this re-runs to ~0.2 m and the box "
              "carries the 'max drop 0.15 m' label (D-31).")
kit.claim("CL-D7-CRADLE-PAD-AREA", "Saddle contact area on the wing lower surface, each cradle",
          calc="CALC-D7-CRADLE-PATCH", output="A_saddle_m2", unit="m2", limit=(">=", "CL-C2-CRADLE-AREA"),
          verifies=["R-TRANSPORT"], parts=PARTS_CR,
          how="Chalk the wing lower surface at y +/-0.20, set it in the saddle, measure the chalked patch (>= 40 x 40 mm, C2).")
kit.claim("CL-D7-PAD-SIDE-MIN", "Smallest side of the saddle and pillar faces", calc="CALC-D7-CRADLE-PATCH",
          output="side_min_m", unit="m", limit=(">=", P + "trn.cradle.pad_min_m"),
          parts=PARTS_CR + ["TRN-004-L", "TRN-004-R"], how="Ruler on the built saddle and pillar.")
kit.claim("CL-D7-BRACE-GAP", "Cradle / pillar / column outboard edge to the fin brace anchor", calc="CALC-D7-CRADLE-PATCH",
          output="gap_brace_m", unit="m", limit=(">=", 0.002), verifies=["R-TRANSPORT"],
          parts=PARTS_CR + ["TRN-004-L", "TRN-004-R", "FIN-010-UR", "FIN-010-LR", "FIN-010-UL", "FIN-010-LL"],
          how="Aircraft in the box: a 2 mm feeler passes between each saddle / pillar and the brace anchor (D3 CR-D3-11).")
kit.claim("CL-D7-HANDLE-BOLT-F", "Load per M3 handle bolt, loaded box at 2 g", calc="CALC-D7-HANDLE", output="F_bolt_N",
          unit="N", parts=["TRN-007-C", "TRN-007-L", "TRN-007-R"],
          how="C6 checks the M3 stack (CR-C6-08: 59 N); T-D7-HANDLE-PULL.")
kit.claim("CL-D7-HANDLE-BEARING", "Wall bearing pressure behind a handle backing strip", calc="CALC-D7-HANDLE",
          output="p_strip_kpa", unit="kPa", parts=["TRN-007-C", "TRN-001"],
          how="T-D7-HANDLE-PULL: Coroplast face shows no dent behind the strip.")
kit.claim("CL-D7-CRADLE-STRESS", "Static stress on each crush column", calc="CALC-D7-CRADLE-STRESS",
          output="sigma_kpa", unit="kPa", limit=(">=", 2.0), parts=PARTS_CR,
          how="Inside the 2-7 kPa cushion band of 1.7-2.2 pcf PE; T-D7-CUSHION picks the density.")
kit.claim("CL-D7-BOX-MASS", "Empty box with cradles, tray, straps, handles", calc="CALC-D7-MASS", output="box_kg",
          unit="kg", parts=PARTS_BOX + PARTS_CR + ["TRN-003", "TRN-004-L", "TRN-004-R"], how="T-D7-WEIGH-BOX: 10 kg luggage scale.")
kit.claim("CL-D7-LOADED-MASS", "Loaded box: aircraft (no pack), spare props, field pouch", calc="CALC-D7-MASS",
          output="loaded_kg", unit="kg", limit=("<=", P + "requirements.box_mass_max_kg"), verifies=["R-TRANSPORT"],
          parts=PARTS_BOX, how="T-D7-WEIGH-BOX: weigh the loaded box, packs in their LiPo bag outside.")
kit.claim("CL-D7-LOADED-WITH-PACKS", "Loaded box if both packs were put in (not allowed)", calc="CALC-D7-MASS",
          output="loaded_with_packs_kg", unit="kg", how="Shows why packs ride in the LiPo bag (ASM-D7-PACK-OUT).")
kit.claim("CL-D7-END-DROP-ALLOW", "Drop height on a box end (wingtip into the 30 mm end pad)", calc="CALC-D7-OFFAXIS",
          output="h_end_m", unit="m", parts=PARTS_BOX, assumes=["ASM-D7-FLAT-DROP"],
          how="Label-and-test case (C1 CR-C1-22): T-D7-BOX-DROP end drop at this height with the dummy; no tip crush.")
kit.claim("CL-D7-NOSE-DROP-ALLOW", "Drop height on the front wall (pod nose into the 1 in nose pad)", calc="CALC-D7-OFFAXIS",
          output="h_nose_m", unit="m", parts=PARTS_BOX, how="T-D7-BOX-DROP front-wall drop with the dummy.")
kit.claim("CL-D7-AFT-N", "Load factor when the four feet take an aft-wall drop", calc="CALC-D7-OFFAXIS", output="n_aft",
          unit="-", limit=("<=", "CL-C1-TRANSPORT-N-ALLOW-X"), parts=PARTS_BOX,
          how="T-D7-BOX-DROP aft-wall drop with the dummy on real feet; accelerometer on the spar.")
kit.claim("CL-D7-AFT-DROP-ALLOW", "Drop height on the aft wall, feet crushing (cartridges replaced after)",
          calc="CALC-D7-OFFAXIS", output="h_aft_m", unit="m", parts=PARTS_BOX,
          how="T-D7-BOX-DROP aft-wall drop; measure cartridge crush against the 40 mm usable.")
kit.claim("CL-D7-LID-DROP-ALLOW", "Drop height upside down (pillars compress until the upper feet reach the lid)",
          calc="CALC-D7-OFFAXIS", output="h_lid_m", unit="m", parts=PARTS_BOX + ["TRN-004-L", "TRN-004-R"],
          how="Label-and-test case: THIS SIDE UP. T-D7-BOX-DROP lid-down drop at this height with the dummy.")
kit.claim("CL-D7-PILLAR-P-ALLOW", "Allowable bearing on the skinned XPS (120 kPa / 1.5)", calc="CALC-D7-OFFAXIS",
          output="p_allow_kpa", unit="kPa", how="C2's XPS F-250 compressive strength and factor (CL-C2-CRADLE-AREA).")
kit.claim("CL-D7-PILLAR-P", "Lid-pillar bearing on the wing upper surface, lid-down drop (C1 102 N limit)",
          calc="CALC-D7-OFFAXIS", output="p_pillar_kpa", unit="kPa", limit=("<=", "CL-D7-PILLAR-P-ALLOW"),
          parts=["TRN-004-L", "TRN-004-R"], how="Chalk the pillar face; lid-down dummy drop; no dent in the skin.")
kit.claim("CL-D7-MAT-MASS", "Folding landing mat 0.8 x 0.8 m, rubber on 3 mm ply (C5 S1)", calc="CALC-D7-CARRY",
          output="mat_kg", unit="kg", how="T-D7-WEIGH-BOX: weigh the mat.")
kit.claim("CL-D7-CAN-MASS", "Battery can with both packs in their LiPo bags", calc="CALC-D7-CARRY", output="can_kg",
          unit="kg", how="T-D7-WEIGH-BOX: weigh the can loaded.")
kit.claim("CL-D7-CARRY-ITEM-MAX", "Heaviest field item other than the box (can, mat or tote)", calc="CALC-D7-CARRY",
          output="item_max_kg", unit="kg", limit=("<=", P + "requirements.box_mass_max_kg"),
          how="T-D7-WEIGH-BOX: weigh the can, the mat and the tote.")
kit.claim("CL-D7-CARRY-A", "Carrier A: loaded box + tote on the shoulder", calc="CALC-D7-CARRY", output="person_a_kg",
          unit="kg", how="Sum of T-D7-WEIGH-BOX readings.")
kit.claim("CL-D7-CARRY-B", "Carrier B (or the second trip): battery can + folded mat, one per hand", calc="CALC-D7-CARRY",
          output="person_b_kg", unit="kg", how="Sum of T-D7-WEIGH-BOX readings.")
kit.claim("CL-D7-CARRY-ALL", "Everything carried to the field (box, can, mat, tote)", calc="CALC-D7-CARRY",
          output="all_kg", unit="kg", how="Sum of T-D7-WEIGH-BOX readings.")
kit.claim("CL-D7-PROPS-ON-ZMARGIN", "Option CR-D7-15: clocked prop blade to the envelope top", calc="CALC-D7-PROPS-ON",
          output="z_margin_m", unit="m", limit=(">=", 0.0), how="Clock a prop spanwise on the built aircraft; ruler.")
kit.claim("CL-D7-PROPS-ON-SADDLE-CUT", "Option CR-D7-15: notch needed in the saddle's lower front corner",
          calc="CALC-D7-PROPS-ON", output="saddle_cut_m", unit="m", parts=PARTS_CR,
          how="Set the aircraft with props on in the cradles; a 2 mm feeler passes under each lower blade.")
kit.claim("CL-D7-SETUP-MIN", "Field set-up, closed box to the arm check", calc="CALC-D7-SETUP", output="t_min",
          unit="min", limit=("<=", P + "requirements.field_setup_max_min"), verifies=["R-FIELD-SETUP"],
          parts=PARTS_BOX, how="T-D7-SETUP: one person, timed by a second, three field days.")

kit.test("T-D7-CUSHION", "Crush-column coupon test", verifies=["CL-D7-CRADLE-STROKE", "CL-D7-S-BOTTOM",
         "CL-D7-CRADLE-STRESS"], procedure="Two 60 x 50 x 120 mm PE columns under a 2.05 kg dummy on a saddle; drop "
         "0.3 m onto concrete, phone accelerometer on the dummy (>= 400 Hz app); 1.7 and 2.2 pcf; pick the lower peak")
kit.test("T-D7-BOX-DROP", "Loaded box drop", verifies=["CL-D7-DROP-N", "CL-D7-TUBE-CLEAR-DROP",
         "CL-D7-A1-BOX-DROP-ALLOW", "CL-D7-END-DROP-ALLOW", "CL-D7-NOSE-DROP-ALLOW", "CL-D7-AFT-N",
         "CL-D7-AFT-DROP-ALLOW", "CL-D7-LID-DROP-ALLOW", "CL-D7-PILLAR-P"],
         procedure="Ballasted spar-and-tube dummy with real feet first, then the aircraft. 0.3 m flat drop and one "
         "bottom-edge drop; then the off-axis faces at their CL-D7-*-DROP-ALLOW heights (end, front, aft, lid-down), "
         "dummy only; accelerometer taped on the spar at y 0; chalk on the motor caps, foot pads, pod nose and "
         "wingtips (no mark on floor, lid or walls except the pads)")
kit.test("T-D7-WEIGH-BOX", "Weigh the box empty and loaded, the mat, the battery can and the tote",
         verifies=["CL-D7-BOX-MASS", "CL-D7-LOADED-MASS", "CL-D7-MAT-MASS", "CL-D7-CAN-MASS", "CL-D7-CARRY-ITEM-MAX"],
         procedure="10 kg luggage scale, 3 readings each")
kit.test("T-D7-HANDLE-PULL", "Handle pull test", verifies=["CL-D7-HANDLE-BOLT-F", "CL-D7-HANDLE-BEARING"],
         procedure="Loaded box hung from each handle in turn for 1 min, then jerked 3 times from 50 mm slack; "
         "no pull-through, no dent")
kit.test("T-D7-SETUP", "Timed field set-up", verifies=["CL-D7-SETUP-MIN"],
         procedure="CHECKLIST.md read aloud by one person, stopwatch by a second; three field days")

if __name__ == "__main__":
    kit.write()
