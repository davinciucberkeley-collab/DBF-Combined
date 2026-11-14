"""B08 -- buy an ArduPilot-ready tilt-tricopter PNP. First-order sizing.

Run:  python -I sizing.py      (stdlib only; writes sizing.json next to this file)

Same method as the other concept cards: mass build-up by group, wing loading and stall, hover power from
momentum theory with a figure of merit, cruise power from an assumed L/D, battery energy against the study's
default mission (REQUIREMENTS.md section 3, M-A), packed dimensions.

Three bought aircraft are sized side by side because the card has to choose between them:
  T1   HEEWING T1(-S) Ranger VTOL PNP + F405 FC  (B01 merged here; PRIMARY after research, see CARD.md)
  ALT  ZOHD Altus VTOL PNP (980 mm) + team-supplied FC
  MAN  FIMI Manta VTOL PNP+FC (700 mm)
Sources for every listed number are in the per-aircraft dicts. Anything not from a listing is ESTIMATE.
Listings were read 2026-11-09; none of these makers publishes wing area, prop size AND thrust data together,
so hover and cruise numbers are first-order estimates to be replaced by a thrust-stand run (CARD.md test 1).
"""
import json
import math
import os

# ---------------- global assumptions (same as every concept card) ----------------
G = 9.81                 # m/s^2
RHO = 1.20               # kg/m^3, RFS near sea level at ~20 C (ESTIMATE, ISA 1.225 at 15 C)
FM = 0.55                # hover figure of merit for 5-6 in hobby props, ESTIMATE (0.5-0.65 typical bench data)
ETA_DRIVE = 0.75         # motor x ESC efficiency in hover, ESTIMATE
ETA_CRUISE = 0.50        # prop x motor x ESC in cruise at part throttle, ESTIMATE
CL_MAX = 1.0             # EPP FPV wing, flaps none, ESTIMATE
TRANSITION_MARGIN = 1.3  # transition completes at >= 1.3 Vs (REQUIREMENTS D11)
USABLE_FRACTION = 0.80   # usable fraction of nominal pack energy (land at ~20 % left), REQUIREMENTS M-A reserve
TRANSITION_S = 2 * 15    # two transitions of ~15 s each at hover power (ESTIMATE)
GROWTH_KG = 0.25         # REQUIREMENTS M-A growth allowance; reported as a check, not built in
GUST_MS = 8.0            # REQUIREMENTS D11 gust
CL_GUST = 0.3            # lift coefficient of the level wing hit edge-on by a hover gust, ESTIMATE

# Mission M-A (REQUIREMENTS.md section 3, study default)
MISSION = dict(hover_min=2.0, cruise_min_threshold=5.0, cruise_min_objective=10.0, reserve=0.20,
               payload_kg=0.0)

AIRCRAFT = {
    "T1": dict(
        name="HEEWING T1(-S) Ranger VTOL PNP + HEEWING F405 (ArduPilot) + GPS",
        span_m=0.730, length_m=0.645, height_m=0.140,      # listing (kiwiquads / banggood, 2026-11-09)
        wing_area_m2=0.12,                                  # ESTIMATE: 730 mm span x ~165 mm mean chord
        tow_listed_kg=(0.60, 0.75),                         # listing "takeoff weight 600-750 g"
        mass_g={                                            # build-up by group
            "airframe + 3 motors + 3 ESC + servos (PNP, listing 451 g)": 451,
            "FC/PMU + GPS (bundled; ESTIMATE)": 35,
            "receiver RP3 + antenna": 5,
            "airspeed sensor + pitot (optional, ESTIMATE)": 12,
            "wiring, velcro, straps (ESTIMATE)": 15,
            "battery 4S 1500 mAh LiPo (ESTIMATE 175 g)": 175,
        },
        n_rotors=3, prop_d_m=0.152,                         # 6 in props ESTIMATE (size not listed)
        motor="FX-1806 2000KV x3, FX-25A ESC (listing)",
        thrust_per_motor_g=550,                             # ESTIMATE 1806 2000KV, 6 in, 4S; measure on stand
        cells=4, pack_mAh=1500, v_cell=3.7, pack_cost_each=25.0,
        LD=6.0,                                             # ESTIMATE, calibrated: Altus maker "70 km/h @ 5 A" on 4S at ~1.1 kg gives L/D x eta = 3.0 -> L/D 6 at eta 0.5
        cruise_ms=14.0,
        packed="wing off, fuselage + tail as one piece; ~0.66 x 0.40 x 0.16 m case (ESTIMATE); "
               "T1-S is also sold with a foam case (listing)",
        params="Official ArduPilot board 'HEEWING-F405v2' (ardupilot.org common-heewingf405); community "
               "4.7.1 param file (discuss.ardupilot.org t/145545). V1 board: no logging, bootloader fix needed.",
    ),
    "ALT": dict(
        name="ZOHD Altus VTOL PNP/ARF (980 mm) + Matek H743-WING V3 + GPS/compass",
        span_m=0.980, length_m=0.770, height_m=0.16,       # listing (ReadyMadeRC 86192, 2026-11-09)
        wing_area_m2=0.19,                                  # ESTIMATE: 980 mm x ~195 mm mean chord
        tow_listed_kg=(1.10, 1.30),                         # listing "flying weight 1100-1300 g"
        mass_g={
            "airframe + 3 x 2204 motors + 3 x 30A ESC + servos (ESTIMATE)": 760,
            "FC H743-WING V3 + GPS/compass (ESTIMATE)": 45,
            "receiver RP3 + antenna": 5,
            "airspeed sensor + pitot (ESTIMATE)": 12,
            "wiring, velcro (ESTIMATE)": 25,
            "battery 4S 3000 mAh LiPo (ESTIMATE 330 g)": 330,
        },
        n_rotors=3, prop_d_m=0.127,                         # 5x4.2x3 tri-blade (search result, listing)
        motor="2204 1870KV x3, 30A ESC (listing)",
        thrust_per_motor_g=850,                             # ESTIMATE 2204 1870KV, 5 in tri-blade, 4S
        cells=4, pack_mAh=3000, v_cell=3.7, pack_cost_each=40.0,
        LD=6.0,                                             # ESTIMATE, same calibration as T1 (Altus maker cruise point)
        cruise_ms=17.0,
        packed="wing halves off, fuselage + V-tail ~0.77 m; ~0.80 x 0.45 x 0.22 m case (ESTIMATE)",
        params="No maker ArduPilot param file found (UNVERIFIED); team builds Q_TILT setup from the ArduPilot "
               "tilt-rotor guide.",
    ),
    "MAN": dict(
        name="FIMI Manta VTOL PNP+FC (700 mm)",
        span_m=0.700, length_m=0.445, height_m=0.12,       # listing (HobbyRC UK, oscarliang review)
        wing_area_m2=0.118,                                 # listing 11.8 dm^2
        tow_listed_kg=(0.50, 0.60),                         # listing "takeoff weight 500 g"
        mass_g={
            "airframe + 3 x 2004 motors + servos (listing 325 g)": 325,
            "FC + 3-in-1 ESC + GPS (ESTIMATE)": 30,
            "receiver": 5,
            "wiring (ESTIMATE)": 10,
            "battery 3S1P 21700 5000 mAh Li-ion (ESTIMATE 215 g)": 215,
        },
        n_rotors=3, prop_d_m=0.152,                         # 6026 props (oscarliang)
        motor="2004 2700KV x3, 20A 3-in-1 ESC (oscarliang)",
        thrust_per_motor_g=380,                             # ESTIMATE 2004 2700KV on 3S, 6 in
        cells=3, pack_mAh=5000, v_cell=3.6, pack_cost_each=45.0,
        LD=6.0,                                             # ESTIMATE, same calibration as T1 (Altus maker cruise point)
        cruise_ms=13.0,
        packed="wing off; ~0.50 x 0.36 x 0.12 m (ESTIMATE)",
        params="FIMI param files for its F405 posted via social media/Google Drive (forum t/104248, "
               "UNVERIFIED); no compass in the bundled GPS (forum).",
    ),
}
PRIMARY = "T1"


def size(a):
    m_kg = sum(a["mass_g"].values()) / 1000.0
    W = m_kg * G
    S = a["wing_area_m2"]
    wl = m_kg / S                                       # kg/m^2
    vs = math.sqrt(2 * W / (RHO * S * CL_MAX))
    v_tr = TRANSITION_MARGIN * vs
    # hover: momentum theory over total disk area, equal loading (tricopter rear motor actually works harder)
    A = a["n_rotors"] * math.pi * (a["prop_d_m"] / 2) ** 2
    dl = W / A
    p_ideal = W ** 1.5 / math.sqrt(2 * RHO * A)
    p_hover = p_ideal / FM / ETA_DRIVE
    v_pack = a["cells"] * a["v_cell"]
    i_hover = p_hover / v_pack
    tw = a["n_rotors"] * a["thrust_per_motor_g"] / 1000.0 / m_kg
    # cruise
    v_c = max(a["cruise_ms"], v_tr)
    p_cruise = W * v_c / a["LD"] / ETA_CRUISE
    i_cruise = p_cruise / v_pack
    # energy
    e_nom = v_pack * a["pack_mAh"] / 1000.0
    e_use = e_nom * USABLE_FRACTION
    e_hover = p_hover * (MISSION["hover_min"] * 60 + TRANSITION_S) / 3600.0
    e_left = e_use - e_hover
    cruise_min = max(0.0, e_left / p_cruise * 60.0)
    hover_only_min = e_use / p_hover * 60.0
    c_rate_hover = i_hover / (a["pack_mAh"] / 1000.0)
    # gust sensitivity in hover: lift from an 8 m/s gust on the level wing / weight
    gust_lift_ratio = 0.5 * RHO * GUST_MS ** 2 * S * CL_GUST / W
    # growth check
    m_growth = m_kg + GROWTH_KG
    tw_growth = a["n_rotors"] * a["thrust_per_motor_g"] / 1000.0 / m_growth
    return dict(
        name=a["name"], motor=a["motor"],
        mass_buildup_g=a["mass_g"], tow_kg=round(m_kg, 3),
        tow_listed_kg=a["tow_listed_kg"],
        tow_inside_listing=a["tow_listed_kg"][0] <= m_kg <= a["tow_listed_kg"][1],
        span_m=a["span_m"], length_m=a["length_m"], wing_area_m2=S,
        wing_loading_kg_m2=round(wl, 2), wing_loading_N_m2=round(W / S, 1),
        stall_ms=round(vs, 1), transition_ms=round(v_tr, 1),
        disk_area_m2=round(A, 4), disk_loading_N_m2=round(dl, 0),
        hover_power_W=round(p_hover, 0), hover_current_A=round(i_hover, 1), hover_C_rate=round(c_rate_hover, 1),
        thrust_to_weight=round(tw, 2), thrust_to_weight_with_growth=round(tw_growth, 2),
        tw_gate_1p6=tw >= 1.6,
        cruise_speed_ms=round(v_c, 1), LD_assumed=a["LD"],
        cruise_power_W=round(p_cruise, 0), cruise_current_A=round(i_cruise, 1),
        pack=f"{a['cells']}S {a['pack_mAh']} mAh", pack_Wh_nominal=round(e_nom, 1), pack_Wh_usable=round(e_use, 1),
        mission_hover_Wh=round(e_hover, 1),
        cruise_min_after_2min_hover=round(cruise_min, 1),
        meets_threshold_5min=cruise_min >= MISSION["cruise_min_threshold"],
        meets_objective_10min=cruise_min >= MISSION["cruise_min_objective"],
        hover_only_endurance_min=round(hover_only_min, 1),
        gust_lift_over_weight=round(gust_lift_ratio, 2),
        mass_with_growth_kg=round(m_growth, 3),
        growth_inside_listing=m_growth <= a["tow_listed_kg"][1],
        packed=a["packed"], params=a["params"],
    )


def main():
    out = dict(
        concept="B08 buy an ArduPilot-ready tilt-tri PNP",
        primary=PRIMARY,
        assumptions=dict(rho=RHO, FM=FM, eta_drive=ETA_DRIVE, eta_cruise=ETA_CRUISE, CL_max=CL_MAX,
                         transition_margin=TRANSITION_MARGIN, usable_fraction=USABLE_FRACTION,
                         transition_s=TRANSITION_S, growth_kg=GROWTH_KG, gust_ms=GUST_MS, CL_gust=CL_GUST,
                         mission=MISSION),
        aircraft={k: size(a) for k, a in AIRCRAFT.items()},
    )
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "sizing.json"), "w") as f:
        json.dump(out, f, indent=2)
    keys = ["tow_kg", "wing_loading_kg_m2", "stall_ms", "transition_ms", "disk_loading_N_m2", "hover_power_W",
            "hover_current_A", "hover_C_rate", "thrust_to_weight", "thrust_to_weight_with_growth",
            "cruise_power_W", "cruise_current_A", "pack_Wh_usable", "cruise_min_after_2min_hover",
            "hover_only_endurance_min", "gust_lift_over_weight", "growth_inside_listing"]
    print(f"{'':32s}" + "".join(f"{k:>10s}" for k in out["aircraft"]))
    for k in keys:
        print(f"{k:32s}" + "".join(f"{str(v[k]):>10s}" for v in out["aircraft"].values()))
    print("wrote sizing.json")


if __name__ == "__main__":
    main()
