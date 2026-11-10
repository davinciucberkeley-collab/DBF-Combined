"""Power subsystem claims (F1, PWR-R1): mass vs allocation, main jumpers, frame joint, park bond, GPS clearance.

Run:  python -I redesign/subsystems/power/power_claims.py   -> claims.json beside this file
Geometry claims call fusion/power.py#layout() with the named inputs only, so build_graph.py re-runs them exactly.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
sys.path.insert(0, str(HERE.parents[1] / "fusion"))
sys.path.insert(0, str(HERE / "fusion"))
import proofkit as pk  # noqa: E402
import power as pw  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "params.json", "../pod/params.json"])

PARTS_LEFT = ["PWR-002", "PWR-003", "PWR-004", "PWR-006", "PWR-007"]

kit.assumption("ASM-PWR-BEND", "Bend radius of fixed short jumpers",
               "Fine-strand silicone jumpers that are soldered at both ends, tied, and never flexed in service may be "
               "bent to an inside radius of 2 x OD", basis="hobby practice for silicone power wire; NASA-STD-8739.4 "
               "class rules ask 3 x OD for general harness bundles that are handled. Check the formed jumper for "
               "insulation cracking at T-PWR-FIT", value=2.0, unit="-", status="UNVERIFIED")
kit.assumption("ASM-PWR-R-BUDGET", "Main-path wire resistance budget",
               "The aircraft-side wiring between the AS150U cups and the bus may add at most the 0.68 mOhm that the "
               "R2 8 AWG 0.15 m loop carried inside CL-F1-R-EXT 6.5 mOhm", basis="team/F1/POWER.md voltage-drop table",
               value=0.68, unit="mOhm", status="PROPOSED", cites=["CL-F1-R-EXT"])
kit.assumption("ASM-PWR-BOND-PA", "Epoxy on sanded nylon housing",
               "30 min epoxy on a 120-grit nylon (PA) connector housing gives >= 1 MPa lap shear",
               basis="low-end class value; nylon bonds poorly unless abraded; coupon at T-PWR-ARRIVAL", value=1.0,
               unit="MPa", status="UNVERIFIED")
kit.assumption("ASM-PWR-PARK-RF", "Required reserve on the park bond",
               "The park bond needs a reserve factor of 3 on the unplug force (repeated every flight, peel at the "
               "housing edge, hand-mixed epoxy)", basis="F1 choice, between C6's bond factors for printed parts",
               value=3.0, unit="-", status="PROPOSED")
kit.assumption("ASM-PWR-JOINT-H", "Room for the 16 AWG joints on the bars",
               "A 16 AWG lead soldered on top of a bus bar stands 2.6 mm (OD) + 2.4 mm fillet and heat-shrink proud",
               basis="F1 estimate", value=5.0, unit="mm", status="UNVERIFIED")


def _layout(zb, tb, size, pack, pod_in, L_in):
    vals = {"pod.z_base_m": zb, "fins.board_t_m": tb, "pod.size_m": size, "battery.size_m": pack}
    return pw.layout(lambda k, u=None: vals[k], L_in, pod_in)


LAYOUT_IN = {"zb": "P:pod.z_base_m", "tb": "P:fins.board_t_m", "size": "P:pod.size_m", "pack": "P:battery.size_m",
             "tray_t": "P:tray_floor_t_m", "plate_t": "P:plate_t_m", "boss_h": "P:boss_h_m", "bay": "P:bay_min_m",
             "guide_t": "P:guide_t_m", "aft": "P:pack_aft_face_m", "pad_t": "P:pad_t_m", "plate_x": "P:pdb_plate_x_m",
             "pattern": "P:pdb_pattern_m", "park": "P:park_x_m", "ubec_x": "P:ubec_zone_x_m", "stop": "P:aft_stop_m",
             "bus_m": "P:power.bus_board_m", "bar_m": "P:power.bar_m", "spacer": "P:power.spacer_h_m",
             "deck_t": "P:power.deck_t_m", "board": "P:power.board_env_m", "margin": "P:power.deck_margin_m",
             "wall": "P:power.wall_t_m", "win": "P:power.window_x_m", "as_m": "P:power.as150u_half_m",
             "wall_h": "P:power.cradle_wall_h_m", "leg": "P:power.leg_m", "fuse_m": "P:power.fuse_m",
             "fuse_x0": "P:power.fuse_x0_m", "ubec_m": "P:power.ubec_m"}


def _geo(a):
    pod_in = {"tray_floor_t_m": a["tray_t"], "plate_t_m": a["plate_t"], "boss_h_m": a["boss_h"], "bay_min_m": a["bay"],
              "guide_t_m": a["guide_t"], "pack_aft_face_m": a["aft"], "pad_t_m": a["pad_t"],
              "pdb_plate_x_m": a["plate_x"], "pdb_pattern_m": a["pattern"], "park_x_m": a["park"],
              "ubec_zone_x_m": a["ubec_x"], "aft_stop_m": a["stop"]}
    L_in = {"bus_board_m": a["bus_m"], "bar_m": a["bar_m"], "spacer_h_m": a["spacer"], "deck_t_m": a["deck_t"],
            "board_env_m": a["board"], "deck_margin_m": a["margin"], "wall_t_m": a["wall"], "window_x_m": a["win"],
            "as150u_half_m": a["as_m"], "cradle_wall_h_m": a["wall_h"], "leg_m": a["leg"], "fuse_m": a["fuse_m"],
            "fuse_x0_m": a["fuse_x0"], "ubec_m": a["ubec_m"]}
    return _layout(a["zb"], a["tb"], a["size"], a["pack"], pod_in, L_in)


@kit.calc("CALC-PWR-MASS", title="Power subsystem flying mass",
          equation="m = pack + (AS150U half + 2 x (l1 + l2) x m'_10AWG) + board + bus + UBEC + frame + fuse + 4 x cap",
          inputs={"pack": "P:battery.mass_kg", "as_g": "P:power.as150u_mass_g", "jl": "P:power.jumper_len_m",
                  "wire": "P:power.wire_10awg", "board": "P:power.board_mass_g", "bus": "P:power.bus_mass_g",
                  "ubec": "P:power.ubec_mass_g", "frame": "P:power.frame_mass_g", "fuse": "P:power.fuse_mass_g",
                  "cap": "P:power.cap_mass_g"},
          units={"pack": "kg", "as_g": "g", "board": "g"})
def mass(pack, as_g, jl, wire, board, bus, ubec, frame, fuse, cap):
    jumpers = 2 * sum(jl) * wire[2]
    rest = as_g + jumpers + board + bus + ubec + frame + fuse + 4 * cap
    return {"total_g": pack * 1000 + rest, "non_pack_g": rest, "jumpers_g": jumpers}


@kit.calc("CALC-PWR-JUMPER", title="10 AWG main jumpers: loop resistance and temperature rise",
          equation="R = 2 (l1 + l2) r20 (1 + 0.00393 (T - 20)), T 60 degC; dT <= q L^2 / (8 k A), q = I^2 r (ends at terminal temperature)",
          inputs={"jl": "P:power.jumper_len_m", "wire": "P:power.wire_10awg", "i": "CL-F1-I-CONT", "k": "P:power.k_cu_w_mk"},
          units={"i": "A"})
def jumper(jl, wire, i, k):
    r_m = wire[1] * 1e-3 * (1 + 0.00393 * (60 - 20))           # Ohm/m hot
    loop_mohm = 2 * sum(jl) * r_m * 1e3
    area = 1.72e-8 * (1 + 0.00393 * 40) / r_m                 # copper area equivalent to the stated resistance
    q = i ** 2 * r_m                                           # W/m
    dt = q * max(jl) ** 2 / (8 * k * area)                     # conduction-only bound, no convection credit
    return {"loop_mohm": loop_mohm, "rise_c": dt, "loss_w": i ** 2 * loop_mohm / 1e3}


@kit.calc("CALC-PWR-BEND", title="Output-jumper drop vs two bends at the minimum radius",
          equation="ratio = drop / (2 k OD)", inputs={"drop": "P:power.jumper_drop_m", "wire": "P:power.wire_10awg",
                                                      "k": "ASM-PWR-BEND"}, units={"drop": "m"})
def bend(drop, wire, k):
    return {"ratio": drop * 1000 / (2 * k * wire[0])}


@kit.calc("CALC-PWR-ENGAGE", title="Frame screw thread engagement in the brass insert",
          equation="e = min(L - washer - deck - spacer, insert)", inputs={"s": "P:power.screw"})
def engage(s):
    return {"e_mm": min(s["len_mm"] - s["washer_mm"] - s["deck_mm"] - s["spacer_mm"], s["insert_mm"]), "min_mm": 1.5 * 3.0}


@kit.calc("CALC-PWR-PARK", title="AS150U park bond reserve", equation="RF = A tau / F_unplug",
          inputs={"a": "P:power.cradle_bond_mm2", "tau": "P:power.bond_tau_pa", "f": "P:power.unplug_force_n"},
          units={"a": "mm2", "f": "N"})
def park(a, tau, f):
    return {"rf": a * 1e-6 * tau / f}


@kit.calc("CALC-PWR-GEO", title="Power-stack geometry: GPS clearance, deck clearance over the bus joints, channel fit",
          equation="d = min |GPS - corner of any power box|; c = deck underside - bar top",
          inputs=dict(LAYOUT_IN, gps="P:power.gps_xyz_m"))
def geo(gps, **a):
    G = _geo(a)
    boxes = [G["board"], G["bus"], G["as_air"], G["fuse"], G["ubec"]]
    d = min(math.dist(gps, (b[i][0], b[j][1], b[k][2])) for b in boxes for i in (0, 1) for j in (0, 1) for k in (0, 1))
    bar_top = max(b[1][2] for b in G["bars"])
    out = G["deck"][0][1] + G["yi"]                              # deck outboard edge to the side wall (>= 0)
    inn = -G["ci"] - G["deck"][1][1]                             # deck inboard edge to the channel inner edge (>= 0)
    return {"gps_m": d, "deck_clr_mm": (G["dz0"] - bar_top) * 1000, "channel_fit_mm": min(out, inn) * 1000}


C = "subsystems/power/SPEC.md"
kit.claim("CL-PWR-MASS", "Power subsystem flying mass", calc="CALC-PWR-MASS", output="total_g", unit="g",
          limit=("<=", "P:mass.allocation_g.power"), parts=["PWR-001"] + PARTS_LEFT + ["PWR-005"],
          how="Weigh pack, frame stack and UBEC on a 1 g scale at T-PWR-ARRIVAL; fails today by the power board "
              "moved from avionics (CR-F1-19 transfers 28 g)")
kit.claim("CL-PWR-MASS-NONPACK", "Power mass without the pack", calc="CALC-PWR-MASS", output="non_pack_g", unit="g",
          parts=PARTS_LEFT + ["PWR-005"], how="Weigh the built frame stack (board, bus, AS150U, fuse) and the UBEC")
kit.claim("CL-PWR-JUMPER-R", "Main jumpers loop resistance, hot", calc="CALC-PWR-JUMPER", output="loop_mohm", unit="mOhm",
          limit=("<=", "ASM-PWR-R-BUDGET"), parts=["PWR-002"],
          how="4-wire milliohm reading AS150U cup to bus bar at T-F1-DROP")
kit.claim("CL-PWR-JUMPER-RISE", "Main jumper temperature rise above its terminals at 30.3 A", calc="CALC-PWR-JUMPER",
          output="rise_c", unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"), parts=["PWR-002"],
          verifies=["R-DISCONNECT"], how="Thermocouples on the jumper mid-point and the cup, 30 A for 10 min (T-F1-WIRE-HEAT)")
kit.claim("CL-PWR-BEND", "Output jumper drop vs 2 bends at 2 x OD", calc="CALC-PWR-BEND", output="ratio", unit="-",
          limit=(">=", 1.0), parts=["PWR-002", "PWR-006"], assumes=["ASM-PWR-BEND"],
          how="Form the jumper on the printed frame before soldering (T-PWR-FIT); no insulation whitening")
kit.claim("CL-PWR-ENGAGE", "Frame screw engagement in the M3 x 5.7 insert", calc="CALC-PWR-ENGAGE", output="e_mm",
          unit="mm", limit=(">=", 4.5), parts=["PWR-006", "POD-002"],
          how="Count turns to seat (>= 9 turns of 0.5 mm) at T-PWR-FIT")
kit.claim("CL-PWR-PARK-RF", "AS150U park bond reserve on the unplug force", calc="CALC-PWR-PARK", output="rf", unit="-",
          limit=(">=", "ASM-PWR-PARK-RF"), parts=["PWR-002", "PWR-006"], assumes=["ASM-PWR-BOND-PA"],
          how="Pull the bonded aircraft half with 150 N (3 x 50 N) on a luggage scale (T-PWR-PARK-PULL)")
kit.claim("CL-PWR-GPS-CLR", "GPS to the nearest power item", calc="CALC-PWR-GEO", output="gps_m", unit="m",
          limit=(">=", "P:requirements.gps_mast_clearance_m"), parts=PARTS_LEFT + ["PWR-005"],
          how="Tape measure GPS centre to UBEC and AS150U on the built pod; COMPASSMOT at T-F3-COMPASSMOT")
kit.claim("CL-PWR-DECK-CLR", "Deck underside above the bus bars", calc="CALC-PWR-GEO", output="deck_clr_mm", unit="mm",
          limit=(">=", "ASM-PWR-JOINT-H"), parts=["PWR-004", "PWR-006"],
          how="Dry-fit the deck over the soldered bus board (T-PWR-FIT): no contact")
kit.claim("CL-PWR-CHANNEL-FIT", "Frame deck inside the left channel", calc="CALC-PWR-GEO", output="channel_fit_mm",
          unit="mm", limit=(">=", 0.0), parts=["PWR-006", "POD-001"], how="Drop the printed frame into the pod (T-PWR-FIT)")

kit.test("T-PWR-ARRIVAL", "Measure and weigh the bought power parts", verifies=["CL-PWR-MASS", "CL-PWR-MASS-NONPACK"],
         procedure="Calipers on the AS150U halves, the separated CoreWing power board (<= 42 x 32 x 9 mm) and the UBEC; "
                   "1 g scale on every part; unplug force of a mated AS150U pair with a luggage scale; epoxy coupon on a "
                   "sanded spare housing")
kit.test("T-PWR-FIT", "Dry fit of the power stack in the pod", verifies=["CL-PWR-BEND", "CL-PWR-ENGAGE", "CL-PWR-DECK-CLR",
                                                                        "CL-PWR-CHANNEL-FIT"],
         procedure="Bus board taped, frame screwed (4 x M3x18 nylon), jumpers formed on the frame, AS150U seated, hatch closed")
kit.test("T-PWR-PARK-PULL", "Park bond pull", verifies=["CL-PWR-PARK-RF"],
         procedure="After 24 h cure: 150 N along +x on the aircraft half through a mated pack half, 10 s; no movement")

if __name__ == "__main__":
    kit.write()
