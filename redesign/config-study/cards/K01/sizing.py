"""K01 small twin-boom quadplane 4+1 (class S, 4S) -- first-order sizing.

Run:  python -I sizing.py      (stdlib only; writes sizing.json next to this file)

Mission = REQUIREMENTS.md section 3 default M-A (VTOL demonstrator):
  hover >= 2 min total, cruise >= 5 min threshold / 10 min objective at 14-20 m/s,
  20 % energy reserve, 0 payload + 0.25 kg growth allowance, T/W >= 1.6 (2.0 recommended).
Every assumption is in the block below. ESTIMATE = engineering guess, UNVERIFIED = unchecked claim.
"""
import json
import math
import os

G = 9.81
RHO = 1.225                      # sea level ISA; RFS is ~5 m ASL

# ------------------------------------------------------------------ ASSUMPTIONS
# Geometry (chosen, see CARD.md 3-view)
SPAN = 1.60                      # m, two 0.80 m halves on a carbon joiner (choice: class S 1.5-1.8 m)
CHORD = 0.25                     # m, constant chord (hot-wire friendly)
E_OSWALD = 0.75                  # ESTIMATE, rectangular low-Re wing with pod and boom junctions
CL_MAX = 1.10                    # ESTIMATE, hot-wired ~12 % section (e.g. Clark-Y/MH-type) at Re ~2e5, no flaps
BOOM_Y = 0.30                    # m, boom offset from centreline (11 in prop clears 0.12 m pod by 3 cm)
X_FRONT_MOTOR = -0.25            # m from wing LE (front prop disc ends 0.11 m ahead of LE)
X_REAR_MOTOR = 0.42              # m from wing LE (rear prop disc starts 0.03 m behind TE)
BOOM_LEN = 1.00                  # m per boom (stock 1000 mm tube, no cut)
TAIL_PANEL_SPAN = 0.39           # m, each inverted-V panel, boom tip up to apex
TAIL_CHORD = 0.14                # m
TAIL_ANGLE_DEG = 40.0            # panel angle from horizontal
TAIL_ARM = 0.60                  # m, wing AC to tail AC
POD_LEN, POD_W = 0.62, 0.12      # m

# Mass build-up, kg (all ESTIMATE unless a datasheet is named)
MASS = {
    "wing (2 halves XPS 30 kg/m3 hot-wired, tape skin, 22x20 CF joiner, 2 aileron horns)": 0.45,
    "pod (XPS/foam-board shell, printed nose + battery tray + motor mount)": 0.25,
    "booms 2 x CF 25x22x1000 (~172 g/m) + 4 printed motor mounts + 2 wing saddles": 0.46,
    "inverted-V tail 2 panels (5 mm foam board/Depron) + printed apex + boom-end clamps": 0.07,
    "4 control servos EMAX ES3005HV 43.2 g (datasheet) + linkages": 0.19,
    "4 lift stations: X3108S 81 g (SunnySky) + LANRC 45A 6.6 g + APC 11x4.5MR ~20 g + wiring": 0.48,
    "pusher: X2814 900KV ~108 g (RMRC listing) + 45A ESC + 11x5.5 prop + mount": 0.16,
    "battery 4S 6500 LiPo (Ovonic 50C ~522 g listed; 560 g used)": 0.56,
    "avionics: FC, GPS, RX, airspeed, RID, UBEC, AS150U, harness": 0.17,
    "landing legs 4 x 0.18 m printed PETG + TPU pads under motors (pusher-tip clearance 5 cm)": 0.08,
    "fasteners, glue, tape, Velcro, cable ties": 0.10,
}
GROWTH = 0.25                    # kg, REQUIREMENTS section 3 growth allowance (no payload)

# Lift propulsion (SunnySky X3108S KV900 data, APC 11x4.7 @ 14.8 V, docs/research/budget-lift.md)
N_LIFT = 4
PROP_D_IN = 11.0
LIFT_TABLE = [(690, 89.0), (750, 104.0), (870, 133.0), (1580, 447.0)]   # (thrust g, input W) per motor
LIFT_MAX_G = 1580.0              # g at 30 A, full throttle, 14.8 V
VOLTAGE_SAG = 0.93               # ESTIMATE, loaded 4S at ~3.45 V/cell vs 3.7 nominal: thrust ~ V^1 at fixed throttle
ESC_EFF = 0.95                   # ESTIMATE, BLHeli_S
DOWNLOAD = 1.03                  # ESTIMATE, props sit fore/aft of wing; boom + motor blockage only
FM = 0.65                        # ESTIMATE, figure of merit, 11 in APC MR at ~830 g (momentum cross-check only)
ETA_MOTOR_HOVER = 0.80           # ESTIMATE, cross-check only

# Cruise aerodynamics
V_CRUISE = 16.0                  # m/s, >= 1.3 Vs and inside the 14-20 m/s M-A band
CF_WING, FF_WING = 0.0060, 1.25  # ESTIMATE, Re ~2.7e5, tape skin
CF_BODY = 0.0070                 # ESTIMATE
CDA_PARKED_PROP_C0 = 0.0034      # m2, C0 17 in parked prop, sizing.mjs ESTIMATE (configurations.md 2.4)
PARKED_PROP_SCALE = (PROP_D_IN / 17.0) ** 2   # scale with D^2 (ESTIMATE)
CDA_MOTOR_BODY = 0.0004          # m2 per stopped motor + mount, ESTIMATE
INTERFERENCE = 1.15              # ESTIMATE, +15 % on CD0 for junctions, gear, cooling, antennas
ETA_PROP_CRUISE = 0.60           # ESTIMATE, 11x5.5 pusher at 16 m/s behind the pod
ETA_MOTOR_CRUISE = 0.80          # ESTIMATE, motor + ESC at part load
AVIONICS_W = 5.0                 # W, FC + GPS + RX + servos average (ESTIMATE)

# Battery
PACK_S, PACK_AH = 4, 6.5
V_NOM_CELL = 3.7
RESERVE = 0.20                   # 20 % energy left at touchdown (M-A)
TRANSITION_WH = 3.0              # ESTIMATE, two transitions ~20 s each at hover power + pusher
HOVER_MIN = 2.0                  # M-A: 2 min total hover

# Pusher
PUSHER_STATIC_KGF = 1.4          # UNVERIFIED, X2814 900KV on 4S 11x5.5 (listing says "1200-1400 g aerobatic plane"; no maker table)
PUSHER_FULL_A = 30.0             # ESTIMATE, full-throttle current

# Option deltas (merged concepts) are passed as arguments in main(); each dm is an ESTIMATE:
#   K21 hexa +0.12 kg/station; K04 folding +0.03 kg, CdA x0.5; K05 fairing +0.04 kg, CdA x0.7;
#   U04 foam board -0.05 kg; 4S 5000 pack -0.13 kg; B03 Mini Talon 1.30 m x 0.26 m wing -0.05 kg.
# ---------------------------------------------------------------- END ASSUMPTIONS


def interp_power(thrust_g):
    """Electrical input W per motor from the maker's table (linear interpolation)."""
    t = LIFT_TABLE
    if thrust_g <= t[0][0]:
        return t[0][1] * thrust_g / t[0][0]
    for (g0, w0), (g1, w1) in zip(t, t[1:]):
        if thrust_g <= g1:
            return w0 + (w1 - w0) * (thrust_g - g0) / (g1 - g0)
    return t[-1][1]


def size(span=SPAN, chord=CHORD, n_lift=N_LIFT, prop_cdA_factor=1.0, pack_ah=PACK_AH, dm=0.0, label="baseline"):
    m_empty_groups = sum(MASS.values())
    if n_lift != N_LIFT:   # extra lift stations: 0.12 kg each incl. ESC/prop/mount (ESTIMATE)
        dm_lift = (n_lift - N_LIFT) * 0.12
    else:
        dm_lift = 0.0
    mtow = m_empty_groups + GROWTH + dm + dm_lift
    W = mtow * G
    S = span * chord
    AR = span ** 2 / S
    WS = W / S
    Vs = math.sqrt(2 * WS / (RHO * CL_MAX))

    # ---- hover
    T_motor_g = mtow * 1000 * DOWNLOAD / n_lift
    P_motor = interp_power(T_motor_g)
    P_hover = n_lift * P_motor / ESC_EFF + AVIONICS_W
    V_pack = PACK_S * V_NOM_CELL
    I_hover = P_hover / V_pack
    disk_area = n_lift * math.pi * (PROP_D_IN * 0.0254 / 2) ** 2
    DL = W / disk_area
    P_ideal = (W * DOWNLOAD) ** 1.5 / math.sqrt(2 * RHO * disk_area)
    P_hover_momentum = P_ideal / (FM * ETA_MOTOR_HOVER * ESC_EFF) + AVIONICS_W
    TW = n_lift * LIFT_MAX_G / (mtow * 1000)
    TW_sag = TW * VOLTAGE_SAG
    throttle_hover_frac = T_motor_g / LIFT_MAX_G

    # ---- cruise drag build-up (coefficients on wing area S)
    swet_wing = 2.04 * S
    cd_wing = CF_WING * FF_WING * swet_wing / S
    swet_pod = POD_LEN * math.pi * POD_W
    cd_pod = CF_BODY * 1.3 * swet_pod / S
    swet_booms = 2 * BOOM_LEN * math.pi * 0.025
    cd_booms = CF_BODY * 1.1 * swet_booms / S
    tail_area = 2 * TAIL_PANEL_SPAN * TAIL_CHORD
    cd_tail = CF_BODY * 1.2 * 2.04 * tail_area / S
    cdA_props = n_lift * CDA_PARKED_PROP_C0 * PARKED_PROP_SCALE * prop_cdA_factor
    cd_props = cdA_props / S
    cd_motors = n_lift * CDA_MOTOR_BODY / S
    cd0_parts = dict(wing=cd_wing, pod=cd_pod, booms=cd_booms, tail=cd_tail,
                     parked_props=cd_props, stopped_motors=cd_motors)
    CD0 = sum(cd0_parts.values()) * INTERFERENCE

    def cruise(V):
        CL = 2 * W / (RHO * V ** 2 * S)
        CD = CD0 + CL ** 2 / (math.pi * AR * E_OSWALD)
        D = 0.5 * RHO * V ** 2 * S * CD
        P = D * V / (ETA_PROP_CRUISE * ETA_MOTOR_CRUISE) + AVIONICS_W
        return CL, CD, CL / CD, D, P

    CL_c, CD_c, LD_c, D_c, P_c = cruise(V_CRUISE)
    I_cruise = P_c / V_pack
    # best-endurance-ish sweep for reference
    sweep = []
    for v10 in range(130, 221, 10):
        v = v10 / 10
        c = cruise(v)
        sweep.append(dict(V=v, LD=round(c[2], 2), P_W=round(c[4], 1)))

    # ---- energy
    E_pack = PACK_S * V_NOM_CELL * pack_ah
    E_use = E_pack * (1 - RESERVE)
    E_hover = P_hover * HOVER_MIN / 60
    E_cruise_avail = E_use - E_hover - TRANSITION_WH
    cruise_min = E_cruise_avail / P_c * 60
    hover_only_min = E_use / P_hover * 60

    # ---- transition / electrical
    I_transition_peak = I_hover + PUSHER_FULL_A
    connector_req = 1.25 * I_transition_peak
    pusher_TW = PUSHER_STATIC_KGF / mtow

    # ---- tail volume (inverted V)
    g = math.radians(TAIL_ANGLE_DEG)
    Sh = tail_area * math.cos(g) ** 2
    Sv = tail_area * math.sin(g) ** 2
    Vh = Sh * TAIL_ARM / (S * chord)
    Vv = Sv * TAIL_ARM / (S * span)

    lift_centroid_x = (X_FRONT_MOTOR + X_REAR_MOTOR) / 2
    return dict(
        label=label,
        mtow_kg=round(mtow, 3), span_m=span, chord_m=chord, wing_area_m2=round(S, 3), AR=round(AR, 2),
        wing_loading_N_m2=round(WS, 1), wing_loading_kg_m2=round(WS / G, 2),
        stall_mps=round(Vs, 2), transition_min_mps_1p3Vs=round(1.3 * Vs, 2), cruise_mps=V_CRUISE,
        n_lift=n_lift, disk_loading_N_m2=round(DL, 1), thrust_per_motor_hover_g=round(T_motor_g, 0),
        hover_throttle_frac_of_max_thrust=round(throttle_hover_frac, 2),
        TW_table=round(TW, 2), TW_with_sag=round(TW_sag, 2),
        hover_power_W_table=round(P_hover, 0), hover_power_W_momentum_FM=round(P_hover_momentum, 0),
        hover_current_A=round(I_hover, 1), hover_current_per_motor_A=round(P_motor / ESC_EFF / V_pack, 1),
        CD0=round(CD0, 4), CD0_parts={k: round(v * INTERFERENCE, 4) for k, v in cd0_parts.items()},
        parked_prop_share_of_CD0=round(cd_props / sum(cd0_parts.values()), 2),
        CL_cruise=round(CL_c, 3), LD_cruise=round(LD_c, 2), drag_N=round(D_c, 2),
        cruise_power_W=round(P_c, 0), cruise_current_A=round(I_cruise, 1),
        pusher_static_TW=round(pusher_TW, 2),
        pack=f"{PACK_S}S {pack_ah * 1000:.0f} mAh", pack_Wh=round(E_pack, 1), usable_Wh_after_reserve=round(E_use, 1),
        hover_Wh_2min=round(E_hover, 1), cruise_min_after_2min_hover=round(cruise_min, 1),
        hover_only_endurance_min=round(hover_only_min, 1),
        peak_transition_current_A=round(I_transition_peak, 0), connector_need_A_1p25x=round(connector_req, 0),
        tail_Vh=round(Vh, 2), tail_Vv=round(Vv, 3), lift_centroid_x_from_LE_m=round(lift_centroid_x, 3),
        cg_target_pct_mac=round(100 * lift_centroid_x / chord, 0),
        speed_sweep=sweep,
    )


def packing():
    # Pieces (L x W x H, m), ESTIMATE from the geometry above
    pieces = {
        "wing half L": (0.80, 0.25, 0.035),
        "wing half R": (0.80, 0.25, 0.035),
        "pod with pusher motor (prop off)": (POD_LEN + 0.05, 0.13, 0.14),
        "boom L with 2 motors + legs (props off)": (BOOM_LEN, 0.06, 0.27),
        "boom R with 2 motors + legs (props off)": (BOOM_LEN, 0.06, 0.27),
        "tail (2 panels hinged at apex, folded flat)": (0.40, 0.14, 0.03),
        "props 5 + joiner tube 0.40 m": (0.40, 0.30, 0.05),
    }
    box = (1.20, 0.50, 0.40)
    # Layout check: layer 1 = two booms + pod side by side (0.06+0.06+0.13 = 0.25 m wide) + wing halves stacked 0.25 wide
    layer_w = 0.06 + 0.06 + 0.13 + 0.25
    layer_h = max(0.27, 0.14, 2 * 0.035 + 0.03 + 0.05)   # legs set the height
    longest = max(p[0] for p in pieces.values())
    return dict(pieces_m=pieces, box_m=box, fits_one_box=layer_w <= box[1] and layer_h <= box[2] and longest <= box[0],
                layout="booms + pod + stacked wing halves side by side (0.50 m), tail/props/joiner on top",
                longest_piece_m=longest, boxes_flight_hardware=1,
                second_box="charger, packs in ammo can, tools, spares (field case, not flight hardware)")


def main():
    base = size()
    variants = [base]
    variants.append(size(n_lift=6, label="K21 hexa 6+1"))
    variants.append(size(prop_cdA_factor=0.5, dm=0.03, label="K04 folding lift props"))
    variants.append(size(prop_cdA_factor=0.7, dm=0.04, label="K05 faired parked props"))
    variants.append(size(prop_cdA_factor=2.0, label="sensitivity: parked-prop CdA x2"))
    variants.append(size(dm=-0.05, label="U04 foam-board wing"))
    variants.append(size(pack_ah=5.0, dm=-0.13, label="4S 5000 pack (T/W 2.0 option)"))
    variants.append(size(span=1.30, chord=0.26, dm=-0.05, label="B03 Mini Talon 1.3 m EPO wing"))
    variants.append(size(dm=0.30, label="sensitivity: +0.30 kg mass growth"))
    out = dict(
        concept="K01 small twin-boom quadplane 4+1 (class S, 4S)",
        mission="REQUIREMENTS.md section 3 M-A: hover 2 min, cruise >=5/10 min, 20 % reserve, 0 payload + 0.25 kg growth",
        status="PROPOSED; every number ESTIMATE unless a datasheet is named in sizing.py",
        mass_groups_kg=MASS, growth_kg=GROWTH,
        baseline=base,
        variants=[{k: v[k] for k in ("label", "mtow_kg", "TW_table", "TW_with_sag", "stall_mps", "LD_cruise",
                                     "cruise_power_W", "hover_current_A", "cruise_min_after_2min_hover",
                                     "hover_only_endurance_min")} for v in variants],
        packing=packing(),
        gates=dict(
            G6_TW_ge_1p6=base["TW_table"] >= 1.6, TW_ge_2p0_recommended=base["TW_table"] >= 2.0,
            cruise_threshold_5min=base["cruise_min_after_2min_hover"] >= 5,
            cruise_objective_10min=base["cruise_min_after_2min_hover"] >= 10,
            AS150U_70A_cont_ok=base["connector_need_A_1p25x"] <= 70,
        ),
    )
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "sizing.json"), "w") as f:
        json.dump(out, f, indent=2)
    b = base
    print(f"MTOW {b['mtow_kg']} kg | S {b['wing_area_m2']} m2 AR {b['AR']} | W/S {b['wing_loading_kg_m2']} kg/m2 | "
          f"Vs {b['stall_mps']} m/s -> transition >= {b['transition_min_mps_1p3Vs']} m/s")
    print(f"Hover: DL {b['disk_loading_N_m2']} N/m2, {b['thrust_per_motor_hover_g']} g/motor, "
          f"{b['hover_power_W_table']} W table / {b['hover_power_W_momentum_FM']} W momentum, {b['hover_current_A']} A; "
          f"T/W {b['TW_table']} ({b['TW_with_sag']} with sag)")
    print(f"Cruise {b['cruise_mps']} m/s: CD0 {b['CD0']} (parked props {b['parked_prop_share_of_CD0']:.0%}), "
          f"L/D {b['LD_cruise']}, {b['cruise_power_W']} W, {b['cruise_current_A']} A")
    print(f"Pack {b['pack']} {b['pack_Wh']} Wh: cruise {b['cruise_min_after_2min_hover']} min after 2 min hover; "
          f"hover-only {b['hover_only_endurance_min']} min")
    print(f"Peak transition {b['peak_transition_current_A']} A -> connector >= {b['connector_need_A_1p25x']} A; "
          f"tail Vh {b['tail_Vh']} Vv {b['tail_Vv']}; CG target {b['cg_target_pct_mac']} % MAC")
    for v in out["variants"]:
        print("  ", v)
    print("packing:", out["packing"]["fits_one_box"], out["packing"]["layout"])
    print("gates:", out["gates"])


if __name__ == "__main__":
    main()
