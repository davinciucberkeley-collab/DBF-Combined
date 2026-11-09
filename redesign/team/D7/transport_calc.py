"""D7 transport and packaging: box height from the drop stroke, clearances, cradle foam, box and loaded mass,
field set-up time. Writes claims.json beside this file.

Run:  python -I redesign/team/D7/transport_calc.py
Inputs: redesign/params/params.json, redesign/subsystems/transport/params.json (keys P:trn.*), C1's drop allowable
(CL-C1-TRANSPORT-N-ALLOW, CL-C1-CRADLE-STROKE-REQ) and crush efficiency (ASM-C1-CRUSH-EFF).

Drop model (C1, CALC-C1-TRANSPORT-N): n_T = 1 + h / (eta s). The aircraft rests on two spar cradles; in a floor drop it
moves down by the crush stroke, so every part below the wing (the lower tube ends at z = -0.2125 m) needs the same free
travel above the floor. That travel, not the foam, sets the box height.
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
                   "x_clear = (W - 2 shell - env_x) / 2 ; tip_to_pad = (L - 2 shell - env_y) / 2 - pad ; "
                   "A1 box: t_max = (travel_A1 - margin) / eps_bottom, h_allow = (n_allow - 1) eta eps_use t_max",
          inputs={"ext": P + "trn.box.external_m", "ext_a1": P + "requirements.box_external_m",
                  "env": P + "transport.envelope_props_off_m", "shell": P + "trn.box.shell_t_m",
                  "dbl": P + "trn.box.floor_doubler_t_m", "lin": P + "trn.box.lid_lining_t_m",
                  "gap": P + "trn.box.top_gap_min_m", "pad": P + "trn.box.end_pad_t_m",
                  "travel_req": "CL-D7-TRAVEL-REQ", "s_bot": "CL-D7-S-BOTTOM", "margin": P + "trn.foam.travel_margin_m",
                  "eb": P + "trn.foam.eps_bottom", "eu": P + "trn.foam.eps_use", "eta": "ASM-C1-CRUSH-EFF",
                  "n_allow": "CL-C1-TRANSPORT-N-ALLOW"},
          units={"ext": "m", "ext_a1": "m", "env": "m", "shell": "m", "dbl": "m", "lin": "m", "gap": "m", "pad": "m",
                 "travel_req": "m", "s_bot": "m", "margin": "m"})
def box_stack(ext, ext_a1, env, shell, dbl, lin, gap, pad, travel_req, s_bot, margin, eb, eu, eta, n_allow):
    L, W, H = ext
    floor, lid = shell + dbl, shell + lin
    env_y, env_x, env_z = env
    travel = H - floor - lid - env[AC_Z] - gap
    travel_a1 = ext_a1[2] - floor - lid - env_z - gap
    t_max_a1 = max(0.0, (travel_a1 - margin) / eb)
    return {"H_req_m": floor + travel_req + env_z + gap + lid, "travel_m": travel,
            "clear_bottoming_m": travel - s_bot, "x_clear_m": (W - 2 * shell - env_x) / 2,
            "tip_to_pad_m": (L - 2 * shell - env_y) / 2 - pad, "travel_a1_m": travel_a1,
            "h_allow_a1_m": (n_allow - 1) * eta * eu * t_max_a1}


@kit.calc("CALC-D7-CRADLE-STRESS", title="Static stress on the crush columns",
          equation="sigma = (m_gate - m_pack) g / (2 a b)",
          inputs={"gate": P + "requirements.mtow_gate_kg", "pack": P + "battery.mass_kg",
                  "fp": P + "trn.cradle.crush_footprint_m"},
          units={"gate": "kg", "pack": "kg", "fp": "m"}, assumes=["ASM-D7-PACK-OUT"])
def cradle_stress(gate, pack, fp):
    return {"sigma_kpa": (gate - pack) * G / (2 * fp[0] * fp[1]) / 1000.0}


@kit.calc("CALC-D7-MASS", title="Box mass and loaded mass",
          equation="shell = areal (1 + flaps) [L W + 2 (L + W)(H - t) + L W + 2 (L + W) lip] ; "
                   "box = shell + doublers + lining + pads + cradles + tray + straps + handles + corners + consumables ; "
                   "loaded = box + (gate - pack) + spare props + pouch",
          inputs={"ext": P + "trn.box.external_m", "t": P + "trn.box.shell_t_m", "lip": P + "trn.box.lid_lip_m",
                  "flaps": P + "trn.box.flap_frac", "areal": P + "trn.mass.coroplast_areal_kgm2", "dbl": P + "trn.box.floor_doubler_t_m",
                  "lin": P + "trn.box.lid_lining_t_m", "rho_pe": P + "trn.foam.pe_density_kgm3",
                  "rho_xps": P + "wing.core.density_kgm3", "pad_t": P + "trn.box.end_pad_t_m",
                  "pad": P + "trn.box.end_pad_size_m", "cw": P + "trn.cradle.width_m", "sx": P + "trn.cradle.saddle_x_m",
                  "ct": P + "trn.cradle.crush_t_m", "fp": P + "trn.cradle.crush_footprint_m",
                  "cap": P + "trn.cradle.cap_t_m", "travel": "CL-D7-TRAVEL", "env": P + "transport.envelope_props_off_m",
                  "tray": P + "trn.tray.size_m", "solid": P + "trn.tray.solid_frac",
                  "handle": P + "trn.mass.handle_kg", "cam": P + "trn.mass.cam_strap_kg",
                  "hd": P + "trn.holddown.size_m", "pre": P + "trn.holddown.preload_m",
                  "gap": P + "trn.box.top_gap_min_m", "corners": P + "trn.mass.corners_kg",
                  "cons": P + "trn.mass.consumables_kg", "pouch": P + "trn.mass.pouch_kg",
                  "spares": P + "trn.mass.spare_props", "prop": P + "propulsion.prop_mass_kg",
                  "gate": P + "requirements.mtow_gate_kg", "pack": P + "battery.mass_kg", "n_packs": P + "battery.n_packs"},
          units={"ext": "m", "t": "m", "lip": "m", "areal": "kg/m2", "rho_pe": "kg/m3", "rho_xps": "kg/m3",
                 "gate": "kg", "pack": "kg", "prop": "kg"},
          assumes=["ASM-D7-PACK-OUT"], cites=["SRC-D7-COROPLAST", "SRC-D7-PE-FOAM"])
def masses(ext, t, lip, flaps, areal, dbl, lin, rho_pe, rho_xps, pad_t, pad, cw, sx, ct, fp, cap, travel, env, tray, solid,
           handle, cam, hd, pre, gap, corners, cons, pouch, spares, prop, gate, pack, n_packs):
    L, W, H = ext
    base_shell = areal * (1 + flaps) * (L * W + 2 * (L + W) * (H - t))
    doublers = areal * 2 * (0.15 * (W - 2 * t)) * (1 if dbl > 0 else 0)   # 150 mm strip under each cradle, if fitted
    pads = 2 * rho_pe * pad_t * pad[0] * pad[1]
    base = base_shell + doublers + pads + corners + cons        # TRN-001 (corners and consumables booked here)
    lid = areal * (1 + flaps) * (L * W + 2 * (L + W) * lip) + rho_pe * lin * (L - 2 * t) * (W - 2 * t)   # TRN-005
    # saddle: from the column top up to the wing lower surface (~ chord plane), rigid XPS, 70 % solid
    saddle_h = env[AC_Z] / 2 + travel - ct
    cradle = (rho_xps * 0.7 * cw * (sx[1] - sx[0]) * saddle_h + rho_pe * ct * fp[0] * fp[1]
              + rho_pe * cap * cw * (sx[1] - sx[0]))                                  # each, TRN-002-L/R
    tray_m = rho_xps * solid * tray[0] * tray[1] * tray[2]                            # TRN-003
    pillar = rho_pe * hd[0] * hd[1] * (env[AC_Z] / 2 + gap + pre)                     # each, TRN-004-L/R (upper bound)
    box = base + lid + 2 * cradle + tray_m + 2 * pillar + 3 * handle + 2 * cam
    aircraft = gate - pack
    loaded = box + aircraft + spares * prop + pouch
    return {"base_kg": base, "lid_kg": lid, "cradle_each_kg": cradle, "tray_kg": tray_m, "pillar_each_kg": pillar,
            "box_kg": box, "aircraft_kg": aircraft, "loaded_kg": loaded, "loaded_with_packs_kg": loaded + n_packs * pack}


@kit.calc("CALC-D7-SETUP", title="Field set-up time, closed box to the arm check",
          equation="T = sum(step seconds) / 60", inputs={"steps": P + "trn.setup_steps_s"}, units={"steps": "s"})
def setup(steps):
    return {"t_min": sum(s for _, s in steps) / 60.0}


PARTS_BOX = ["TRN-001", "TRN-005"]
PARTS_CR = ["TRN-002-L", "TRN-002-R"]

kit.claim("CL-D7-S-BOTTOM", "Crush column stroke at bottoming", calc="CALC-D7-STROKE", output="s_bottom_m", unit="m",
          parts=PARTS_CR, how="T-D7-CUSHION: crush a column to bottoming on the shop press, measure the stroke.")
kit.claim("CL-D7-TRAVEL-REQ", "Free travel needed under the lower tube ends", calc="CALC-D7-STROKE",
          output="travel_req_m", unit="m", parts=PARTS_CR, how="Ruler in the built box: lower tube end to floor.")
kit.claim("CL-D7-CRADLE-STROKE", "Usable cradle crush stroke", calc="CALC-D7-STROKE", output="s_use_m", unit="m",
          limit=(">=", "CL-C1-CRADLE-STROKE-REQ"), verifies=["R-LOADS", "R-TRANSPORT"], parts=PARTS_CR,
          how="T-D7-CUSHION coupon drop, then T-D7-BOX-DROP with an accelerometer on the spar.")
kit.claim("CL-D7-DROP-N", "Box drop load factor with the 127 mm columns", calc="CALC-D7-STROKE", output="n_T", unit="-",
          limit=("<=", "CL-C1-TRANSPORT-N-ALLOW"), verifies=["R-LOADS", "R-TRANSPORT"], parts=PARTS_CR,
          how="T-D7-BOX-DROP: 0.3 m flat drop of the loaded box, accelerometer on the spar, peak <= n_allow.")
kit.claim("CL-D7-BOX-H-REQ", "External box height needed for the drop stroke", calc="CALC-D7-BOX-STACK",
          output="H_req_m", unit="m", verifies=["R-TRANSPORT"], parts=PARTS_BOX,
          how="Stack-up check on the built box; CR-D7-01 asks A1 for 0.54 m.")
kit.claim("CL-D7-TRAVEL", "Free travel under the lower tube ends in the 0.54 m box", calc="CALC-D7-BOX-STACK",
          output="travel_m", unit="m", parts=PARTS_BOX, how="Ruler in the built box: lower tube end to floor.")
kit.claim("CL-D7-TUBE-CLEAR-DROP", "Lower tube end to floor when the columns bottom", calc="CALC-D7-BOX-STACK",
          output="clear_bottoming_m", unit="m", limit=(">=", P + "trn.foam.travel_margin_m"), verifies=["R-TRANSPORT"],
          parts=PARTS_BOX + PARTS_CR, how="T-D7-BOX-DROP: chalk on the lower motor caps; no mark on the floor.")
kit.claim("CL-D7-SIDE-CLEAR", "Pod nose and foot tips to the side walls", calc="CALC-D7-BOX-STACK", output="x_clear_m",
          unit="m", limit=(">=", P + "trn.box.top_gap_min_m"), verifies=["R-TRANSPORT"], parts=PARTS_BOX,
          how="Place the aircraft on the cradles; feeler of 10 mm foam between nose / feet and walls.")
kit.claim("CL-D7-TIP-PAD-GAP", "Wingtip to end pad", calc="CALC-D7-BOX-STACK", output="tip_to_pad_m", unit="m",
          limit=(">=", 0.0), verifies=["R-TRANSPORT"], parts=PARTS_BOX, how="Ruler in the built box.")
kit.claim("CL-D7-A1-BOX-DROP-ALLOW", "Drop height the 0.50 m box allows (column limited by free travel)",
          calc="CALC-D7-BOX-STACK", output="h_allow_a1_m", unit="m", limit=(">=", P + "requirements.box_drop_m"),
          verifies=["R-TRANSPORT"], parts=PARTS_BOX,
          how="Why D7 asks for 0.54 m (CR-D7-01): the 0.50 m box leaves too little travel under the tube ends.")
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
kit.claim("CL-D7-SETUP-MIN", "Field set-up, closed box to the arm check", calc="CALC-D7-SETUP", output="t_min",
          unit="min", limit=("<=", P + "requirements.field_setup_max_min"), verifies=["R-FIELD-SETUP"],
          parts=PARTS_BOX, how="T-D7-SETUP: one person, timed by a second, three field days.")

kit.test("T-D7-CUSHION", "Crush-column coupon test", verifies=["CL-D7-CRADLE-STROKE", "CL-D7-S-BOTTOM",
         "CL-D7-CRADLE-STRESS"], procedure="Two 60 x 50 x 127 mm PE columns under a 2.05 kg dummy on a saddle; drop "
         "0.3 m onto concrete, phone accelerometer on the dummy (>= 400 Hz app); 1.7 and 2.2 pcf; pick the lower peak")
kit.test("T-D7-BOX-DROP", "Loaded box drop", verifies=["CL-D7-DROP-N", "CL-D7-TUBE-CLEAR-DROP"],
         procedure="Box loaded with the aircraft (or a ballasted spar-and-tube dummy first), 0.3 m flat drop and one "
         "bottom-edge drop; accelerometer taped on the spar at y 0; chalk on the lower motor caps")
kit.test("T-D7-WEIGH-BOX", "Weigh the box empty and loaded", verifies=["CL-D7-BOX-MASS", "CL-D7-LOADED-MASS"],
         procedure="10 kg luggage scale, 3 readings each")
kit.test("T-D7-SETUP", "Timed field set-up", verifies=["CL-D7-SETUP-MIN"],
         procedure="CHECKLIST.md read aloud by one person, stopwatch by a second; three field days")

if __name__ == "__main__":
    kit.write()
