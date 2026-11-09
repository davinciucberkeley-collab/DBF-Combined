"""Cost-per-configuration template for a $2,000 student VTOL.

Run:  python -I cost_model.py
Every unit price comes from FINDINGS.md tables (source + date there). ESTIMATE items marked.
Edit the CONFIGS dict to try a new layout; the floor (avionics + ground + hardware) is fixed.
"""

TAX = 0.1025          # Berkeley, CDTFA rate effective 2026-10-01 (Richmond 9.75 %, Oakland 10.75 %)
BUDGET = 2000.00

# ---- unit prices, USD pre-tax (see FINDINGS.md tables) ----
P = {
    # propulsion stations = motor + ESC + 1 prop
    "lift_S":   24.99 + 7.50 + 3.83,    # SunnySky X3108S 900KV (4S) + LANRC 45A + APC 11x4.5MR
    "lift_M":   44.99 + 7.50 + 8.73,    # SunnySky X3515S 400KV (6S) + LANRC 45A + APC 16x5.5MR
    "cruise_S": 29.99 + 7.50 + 4.50,    # SunnySky X2814 900KV + LANRC 45A + APC ~11x5.5 (prop ESTIMATE)
    "cruise_M": 79.99 + 41.99 + 6.79,   # T-Motor AT3520 KV550 + Hobbywing 60A + APC 14x8.5EP
    "prop_S": 3.83, "prop_M": 8.73, "prop_cruise_S": 4.50, "prop_cruise_M": 6.79,
    "servo_ctrl": 19.99,                # EMAX ES3005HV, 8 kg.cm @6 V
    "servo_tilt": 27.95,                # Powerhobby 329TG, 19 kg.cm @6 V
    "pack_S": 45.42,                    # 4S 6500 LiPo, Ovonic 2-pack $90.84 / 2 (Ampow, OOS) ESTIMATE
    "pack_M": 69.50,                    # 6S 6500 LiPo, Ovonic 2-pack $138.99 / 2 (Amazon)
}

AVIONICS = {  # fixed floor, any configuration
    "FC CoreWing F405 Wing V2 (RMRC)": 67.26,
    "GPS+compass HGLRC M100-5883 (RDQ)": 20.49,
    "Remote ID NewBeeDrone BeeID v1.1 (NBD)": 39.99,
    "TX RadioMaster Pocket Crush ELRS": 64.99,
    "RX RadioMaster RP3 V2 (ELRS, MAVLink-capable)": 19.99,
    "Telemetry: ELRS MAVLink over RC link": 0.00,
}
AIRSPEED = 59.99  # Holybro MS5525 + pitot, optional

GROUND = {
    "Charger HTRC C150 (150 W AC)": 56.99,
    "LiPo bags x2 (Pyrodrone)": 2 * 9.99,
    "Ammo can (Harbor Freight 63750)": 19.99,
    "Watt meter 150 A": 12.99,
    "IR thermometer": 8.98,
    "Thrust stand: 20 kg load cell+HX711 + Nano": 8.98 + 8.99,
    "Pinecil V2 soldering iron": 25.99,
    "USB-C PD supply for iron (ESTIMATE)": 20.00,
    "Multimeter (ESTIMATE)": 25.00,
    "Solder, flux, wick (ESTIMATE)": 15.00,
    "Hot-wire: 30 V 10 A supply + Ni80 wire": 33.24 + 8.49,
}

HARDWARE_MIN = 124.01  # wiring, XT90, screws, inserts, horns, pushrods, hinge tape, UBEC, epoxy

AIRFRAME = {
    "S": {"XPS 2 in 4x8": 59.97, "XPS 1 in 4x8": 30.97,
          "CF tubes 2x(25x22x1000) + 1x(22x20x1000)": 2 * 40.99 + 28.32,
          "PETG 4 kg": 39.99, "Packing-tape skin 6 rolls": 19.98, "Foam-safe glue": 12.99},
    "M": {"XPS 2 in 4x8": 59.97, "XPS 1 in 4x8": 30.97,
          "6061 tube set (booms, sockets, joiner)": 124.82,
          "PETG 4 kg": 39.99, "Packing-tape skin 6 rolls": 19.98, "Foam-safe glue": 12.99},
}
SHIPPING = {"S": 120.00, "M": 186.94}  # S ESTIMATE; M = cart quotes + estimates, bom-savings.md 2026-11-01

# ---- configuration template ----
# lift: number of lift/hover stations; cruise: dedicated cruise stations; tilt: tilt servos;
# ctrl: control-surface servos; packs: flight packs bought.
CONFIGS = {
    "S quadplane 4+1":          dict(cls="S", lift=4, cruise=1, tilt=0, ctrl=4, packs=3),
    "S tilt-tri (2 tilt + 1)":  dict(cls="S", lift=3, cruise=0, tilt=2, ctrl=2, packs=3),
    "S tilt-quad (front tilt)": dict(cls="S", lift=4, cruise=0, tilt=2, ctrl=2, packs=3),
    "S quad tailsitter":        dict(cls="S", lift=4, cruise=0, tilt=0, ctrl=0, packs=3),
    "S twin tailsitter (6S stations)": dict(cls="S", lift=0, cruise=0, tilt=0, ctrl=2, packs=3, extra_M_lift=2, pack="M"),
    "M quadplane 4+1":          dict(cls="M", lift=4, cruise=1, tilt=0, ctrl=4, packs=2),
    "M octo 8+1":               dict(cls="M", lift=8, cruise=1, tilt=0, ctrl=4, packs=2),
}


def config_cost(c):
    k = c["cls"]
    lift_unit = P["lift_" + k]
    prop_unit = P["prop_" + k]
    prop_cruise = P["prop_cruise_" + k]
    lines = {}
    lines["lift stations"] = c["lift"] * lift_unit + c.get("extra_M_lift", 0) * P["lift_M"]
    lines["cruise stations"] = c["cruise"] * P["cruise_" + k]
    lines["tilt servos"] = c["tilt"] * P["servo_tilt"]
    lines["control servos"] = c["ctrl"] * P["servo_ctrl"]
    lines["flight packs"] = c["packs"] * P["pack_" + c.get("pack", k)]
    # spares: 1 extra lift station (or M station), 2 spare prop sets, 1 spare servo
    spare_station = lift_unit if c["lift"] else P["lift_M"]
    n_props = c["lift"] + c.get("extra_M_lift", 0)
    lines["spares (1 station, 2 prop sets, 1 servo)"] = (
        spare_station + 2 * (n_props * prop_unit + c["cruise"] * prop_cruise) + P["servo_ctrl"])
    lines["airframe materials"] = sum(AIRFRAME[k].values())
    lines["hardware + wiring kit"] = HARDWARE_MIN
    lines["avionics floor"] = sum(AVIONICS.values())
    lines["ground + test floor"] = sum(GROUND.values())
    goods = sum(lines.values())
    tax = goods * TAX
    ship = SHIPPING[k]
    total = goods + tax + ship
    return lines, goods, tax, ship, total


if __name__ == "__main__":
    print(f"Avionics floor: ${sum(AVIONICS.values()):.2f}  (+ airspeed ${AIRSPEED:.2f} optional)")
    print(f"Ground/test floor: ${sum(GROUND.values()):.2f}")
    for k in AIRFRAME:
        print(f"Airframe materials class {k}: ${sum(AIRFRAME[k].values()):.2f}")
    # one bad crash, class S: 2 lift stations + full prop set + FC + GPS + airframe rebuild (ESTIMATE $100)
    crash = 2 * P["lift_S"] + 4 * P["prop_S"] + P["prop_cruise_S"] + 67.26 + 20.49 + 100.00
    print(f"One bad crash (class S): ${crash:.2f} pre-tax, ${crash * (1 + TAX):.2f} with tax")
    print()
    for name, c in CONFIGS.items():
        lines, goods, tax, ship, total = config_cost(c)
        print(f"== {name}")
        for l, v in lines.items():
            print(f"   {l:45s} {v:8.2f}")
        print(f"   goods {goods:.2f} | tax {tax:.2f} | ship {ship:.2f} | TOTAL {total:.2f} | "
              f"reserve {BUDGET - total:.2f} ({(BUDGET - total) / BUDGET:.0%})")
