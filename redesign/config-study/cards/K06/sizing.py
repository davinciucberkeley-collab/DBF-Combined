"""K06 scratch-built tilt-tricopter: first-order sizing.

Run:   python -I sizing.py      (stdlib only; writes sizing.json next to this file)

Layout: tailless swept foam wing (elevons + tip fins), central pod on a carbon tail boom.
Two front motors on nacelles ahead of the leading edge tilt 90 deg on servos (hover -> cruise tractors);
one fixed vertical rear motor on the boom end, stopped in cruise. ArduPilot Plane, Q_FRAME_CLASS 7 (Tri),
Q_TILT_TYPE 2 (vectored yaw), Q_TILT_MASK 3.
Mission: REQUIREMENTS.md section 3 default M-A (hover 2 min total, cruise 5 min threshold / 10 min objective
at 14-20 m/s, 20 % reserve, 0 payload + 0.25 kg growth allowance).

Tags: ESTIMATE = engineering guess, UNVERIFIED = not checked against a primary source.
Every assumption is in the block below; nothing else in the file is a number you should edit.
"""
import json
import math
import os

# ======================================================================================
# ASSUMPTIONS (edit here only)
# ======================================================================================
G = 9.81
RHO = 1.225                      # kg/m3, sea level ISA (RFS is ~ sea level)

# ---- mission (REQUIREMENTS.md s3, M-A default) ----
HOVER_S = 120.0                  # total hover time, s
TRANSITION_S = 2 * 15.0          # forward + back transition, s, ESTIMATE
TRANSITION_POWER_FACTOR = 1.25   # x hover power during transition, ESTIMATE
CRUISE_THRESHOLD_MIN = 5.0
CRUISE_OBJECTIVE_MIN = 10.0
RESERVE_FRAC = 0.20              # of usable energy kept in reserve
USABLE_FRAC = 0.80               # usable fraction of nameplate LiPo energy, ESTIMATE (as budget-energy-test.md)
GROWTH_KG = 0.25                 # growth allowance (REQUIREMENTS.md s3)
MASS_CONTINGENCY = 0.10          # +10 % on the non-battery build-up (glue, paint, cable ties), ESTIMATE
TW_GATE = 1.6                    # D11

# ---- propulsion (SunnySky X3108S KV900, APC 11x4.7 table at 14.8 V; docs/research/budget-lift.md B1) ----
N_LIFT = 3
PROP_D_M = 11 * 0.0254
MOTOR_MAX_THRUST_G = 1580.0      # maker table, 14.8 V supply, 30 A, 447 W
MOTOR_TABLE = [                  # (thrust g, A, W) at 14.8 V, maker table
    (690, 6, 89), (750, 7, 104), (870, 9, 133), (1580, 30, 447)]
SAG_THRUST_FACTOR = 0.90         # thrust at loaded-pack voltage vs 14.8 V supply table, ESTIMATE
INSTALL_LOSS = 1.10              # nacelle/wing blockage under front props, boom under rear prop, ESTIMATE
KV = 900.0
V_NOM = 14.8                     # 4S nominal

# ---- airframe geometry ----
SPAN_M = 1.30
ROOT_CHORD_M = 0.32
TIP_CHORD_M = 0.20
LE_SWEEP_DEG = 20.0              # ESTIMATE (enough for elevon pitch arm on a reflexed section)
THICKNESS_RATIO = 0.11           # reflexed flying-wing section (e.g. MH-60 class ~10 %), ESTIMATE
CL_MAX = 0.85                    # whole aircraft, reflexed tailless wing, ESTIMATE
CD0 = 0.040                      # wing + pod + 2 nacelles + 3 skids + fins + stopped rear prop, ESTIMATE
OSWALD_E = 0.80                  # ESTIMATE
FRONT_ARM_X_M = 0.20             # front motor axes ahead of CG (hover), m
FRONT_ARM_Y_M = 0.30             # front motor lateral offset, m
# rear arm set for equal thrust share: 2*T*x_f = T*x_r  ->  x_r = 2*x_f
POD_NOSE_TO_CG_M = 0.33
POD_MAX_WH_M = (0.12, 0.11)      # pod width, height, m
NACELLE_AHEAD_OF_LE_M = 0.13         # pivot ~0.13 m ahead of local LE at y=0.30 (20 deg sweep puts local LE 0.11 m aft of root LE)
PACKED_STACK_H_M = 0.12          # wing half thickness incl. nacelle + motor (props off), m, ESTIMATE

# ---- cruise propulsion ----
PROP_EFF_CRUISE = 0.55           # 11x4.5 MR low-pitch prop at J ~ 0.4, ESTIMATE (APC MR curves peak ~0.55-0.6, UNVERIFIED)
MOTOR_ESC_EFF_CRUISE = 0.75      # motor lightly loaded at high rpm + ESC, ESTIMATE
J_CRUISE = 0.40                  # advance ratio for useful thrust on a 4.5 in pitch prop, ESTIMATE
LOADED_RPM_FRAC = 0.85           # loaded rpm / (KV * V_nom), ESTIMATE

# ---- battery (Ovonic 4S 5000 mAh 50C XT60, us.ovonicshop.com, $48.57, 448 g listed, seen 2026-11-09) ----
BATT_CANDIDATES = [  # name, mAh, cells, g, $ (each)
    ("Ovonic 4S 3300 50C (ESTIMATE mass/price)", 3300, 4, 330, 33.00),
    ("Ovonic 4S 5000 50C XT60", 5000, 4, 448, 48.57),
    ("Ovonic 4S 6500 (cost_model.py pack_S, ESTIMATE mass)", 6500, 4, 590, 45.42),
]
BATT_CHOICE = 1

# ---- mass build-up, g (non-battery). (group, item, g, basis) ----
SPAN_HALF_FOAM = None  # computed below
XPS_DENSITY = 28.0        # kg/m3 FOAMULAR NGX F-250 class, ESTIMATE (datasheet density not extracted, airframe-materials.md)
TAPE_SKIN_G_M2 = 60.0     # packing tape, ESTIMATE (budget-airframe.md M2 says weigh a sample)
CF_RHO = 1550.0           # kg/m3 (budget-airframe.md)


def tube_g_per_m(od_mm, id_mm):
    return math.pi / 4 * (od_mm ** 2 - id_mm ** 2) * 1e-6 * CF_RHO * 1000


def wing_area():
    return SPAN_M * (ROOT_CHORD_M + TIP_CHORD_M) / 2


def mac():
    lam = TIP_CHORD_M / ROOT_CHORD_M
    return 2 / 3 * ROOT_CHORD_M * (1 + lam + lam ** 2) / (1 + lam)


S = wing_area()
foam_vol = 0.68 * THICKNESS_RATIO * (ROOT_CHORD_M ** 2 + ROOT_CHORD_M * TIP_CHORD_M + TIP_CHORD_M ** 2) / 3 * SPAN_M
#   (airfoil section area ~0.68 t c; integrate c^2 over a linear taper)
wing_foam_g = foam_vol * XPS_DENSITY * 1000
skin_g = 2.05 * S * TAPE_SKIN_G_M2 * 1.25   # both sides, 25 % overlap

MASS_ITEMS = [
    # propulsion
    ("propulsion", "3x SunnySky X3108S KV900 (81 g, maker page)", 3 * 81),
    ("propulsion", "3x APC 11x4.5MR/MRP props ~18 g ESTIMATE", 3 * 18),
    ("propulsion", "3x LANRC 45A BLHeli_S ESC (6.6 g listing)", 3 * 6.6),
    ("propulsion", "motor/ESC wiring, XT60s, 14 AWG runs, PDB on FC", 95),
    # tilt system
    ("tilt", "2x Powerhobby 329TG tilt servo (63 g listed)", 2 * 63),
    ("tilt", "2x printed PETG nacelle + 6 mm steel pivot + 2 flanged bearings, ESTIMATE", 2 * 45),
    # wing
    ("wing", "XPS cores (calc from planform, t/c, density)", wing_foam_g),
    ("wing", "packing-tape skin (calc, 2.05 S, 25 % overlap)", skin_g),
    ("wing", "spar sockets 25x22 CF 2 x 0.35 m (calc)", tube_g_per_m(25, 22) * 0.70),
    ("wing", "joiner 22x20 CF 0.40 m (calc)", tube_g_per_m(22, 20) * 0.40),
    ("wing", "2x ES3005HV elevon servos (~42 g, ESTIMATE)", 2 * 42),
    ("wing", "2x tip fins 5 mm foam board + horns/pushrods/hinge tape, ESTIMATE", 45),
    # fuselage
    ("fuselage", "printed pod + hatch (LW-PLA/PETG shell), ESTIMATE", 160),
    ("fuselage", "tail boom 22x20 CF 0.55 m (calc)", tube_g_per_m(22, 20) * 0.55),
    ("fuselage", "rear motor mount (printed clamp), ESTIMATE", 18),
    ("fuselage", "3 printed TPU skid feet, ESTIMATE", 36),
    ("fuselage", "fasteners, heat-set inserts, nylon wing bolts, ESTIMATE", 40),
    # avionics
    ("avionics", "CoreWing F405 Wing V2 + cables, ESTIMATE", 32),
    ("avionics", "GPS/compass SAM-M10Q, ESTIMATE", 12),
    ("avionics", "ELRS RP3 V2 receiver + antenna", 4),
    ("avionics", "MS4525DO airspeed + pitot + tubing, ESTIMATE", 15),
    ("avionics", "BeeID Remote ID (conditional, carried in mass), ESTIMATE", 7),
]

# K07 option: 4th rear motor (two counter-rotating rear motors on a cross-bar), adds:
K07_ADD_G = 81 + 18 + 6.6 + 25 + 30   # motor, prop, ESC, wiring, cross-bar ESTIMATE
# U05 option: one coupled tilt servo (remove one servo + one linkage arm, add a torque tube)
U05_DELTA_G = -63 - 10 + 25           # ESTIMATE

# ======================================================================================
# CALCULATIONS
# ======================================================================================


def interp_power(thrust_g):
    """Electrical power per motor (W) from the maker table, linear between points."""
    tab = MOTOR_TABLE
    if thrust_g <= tab[0][0]:
        t0, a0, w0 = tab[0]
        return w0 * (thrust_g / t0) ** 1.5
    for (t0, a0, w0), (t1, a1, w1) in zip(tab, tab[1:]):
        if t0 <= thrust_g <= t1:
            f = (thrust_g - t0) / (t1 - t0)
            return w0 + f * (w1 - w0)
    return tab[-1][2]


def momentum_power(thrust_n, area_m2, overall_eff):
    return thrust_n ** 1.5 / math.sqrt(2 * RHO * area_m2) / overall_eff


def size(extra_g=0.0, n_lift=N_LIFT, batt_idx=BATT_CHOICE):
    name, mah, cells, batt_g, batt_usd = BATT_CANDIDATES[batt_idx]
    groups = {}
    for grp, _, g in MASS_ITEMS:
        groups[grp] = groups.get(grp, 0.0) + g
    nonbatt = sum(groups.values()) + extra_g
    contingency = nonbatt * MASS_CONTINGENCY
    mtow_g = nonbatt + contingency + batt_g + GROWTH_KG * 1000
    W = mtow_g / 1000 * G

    # ---- wing ----
    ws = mtow_g / 1000 / S
    vs = math.sqrt(2 * W / (RHO * S * CL_MAX))
    ar = SPAN_M ** 2 / S

    # ---- hover ----
    per_motor_g = mtow_g / n_lift                     # equal share by arm design (x_r = 2 x_f)
    tw_table = MOTOR_MAX_THRUST_G * n_lift / mtow_g
    tw_sag = tw_table * SAG_THRUST_FACTOR
    disk_a = math.pi * PROP_D_M ** 2 / 4
    disk_loading = W / (n_lift * disk_a)
    p_table = interp_power(per_motor_g) * INSTALL_LOSS * n_lift
    # calibrate figure of merit x motor x ESC from the table's 750 g point
    t750 = 0.750 * G
    eff_cal = (t750 ** 1.5 / math.sqrt(2 * RHO * disk_a)) / 104.0
    p_mom = momentum_power(per_motor_g / 1000 * G, disk_a, eff_cal) * INSTALL_LOSS * n_lift
    p_hover = max(p_table, p_mom)
    i_hover = p_hover / V_NOM
    p_trans = p_hover * TRANSITION_POWER_FACTOR
    i_peak_full = n_lift * 30.0                       # all motors full throttle, table
    i_transition = p_trans / (V_NOM * 0.95)           # sagged pack ~ 3.5 V/cell

    # ---- cruise (speed sweep in the 14-20 m/s band, >= 1.3 Vs) ----
    k = 1 / (math.pi * OSWALD_E * ar)
    sweep = []
    for v10 in range(140, 201, 5):
        v = v10 / 10
        q = 0.5 * RHO * v * v
        cl = W / (q * S)
        cd = CD0 + k * cl * cl
        drag = q * S * cd
        p_aero = drag * v
        p_elec = p_aero / (PROP_EFF_CRUISE * MOTOR_ESC_EFF_CRUISE)
        rpm_need = v / (J_CRUISE * PROP_D_M) * 60
        sweep.append(dict(v=v, cl=round(cl, 3), LD=round(cl / cd, 2), drag_N=round(drag, 2),
                          p_elec_W=round(p_elec, 1), rpm_needed=round(rpm_need),
                          ok_vs=v >= 1.3 * vs))
    valid = [s for s in sweep if s["ok_vs"]]
    best = min(valid, key=lambda s: s["p_elec_W"])
    rpm_avail = KV * V_NOM * LOADED_RPM_FRAC

    # ---- energy ----
    wh = mah / 1000 * cells * 3.7
    usable = wh * USABLE_FRAC
    e_hover = p_hover * HOVER_S / 3600
    e_trans = p_trans * TRANSITION_S / 3600
    e_cruise_avail = usable * (1 - RESERVE_FRAC) - e_hover - e_trans
    cruise_min = e_cruise_avail / best["p_elec_W"] * 60
    hover_only_min = usable * (1 - RESERVE_FRAC) / p_hover * 60
    e_obj = e_hover + e_trans + best["p_elec_W"] * CRUISE_OBJECTIVE_MIN / 60
    pack_wh_needed_obj = e_obj / (USABLE_FRAC * (1 - RESERVE_FRAC))

    # ---- hover in wind: lateral gust 8 m/s on side area ----
    side_area = 0.07   # pod + fins + nacelles side area, m2, ESTIMATE
    f_side = 0.5 * RHO * 8 ** 2 * side_area * 1.2
    tilt_deg = math.degrees(math.atan(f_side / W))

    # ---- tilt-servo load: gyroscopic moment of the prop at hover rpm, 2 rad/s body rate ----
    prop_mass = 0.018
    i_prop = prop_mass * PROP_D_M ** 2 / 12
    rpm_hover = 7000.0   # ESTIMATE from table (750-870 g at ~6500-7500 rpm, UNVERIFIED)
    m_gyro = i_prop * rpm_hover * 2 * math.pi / 60 * 2.0
    servo_torque_nm = 24.0 * G / 100  # 329TG 24 kg-cm @ 8.4 V listing; ~19 kg-cm @ 6 V
    servo_torque_6v = 19.0 * G / 100

    # ---- geometry / packing ----
    x_r = 2 * FRONT_ARM_X_M
    pod_len = POD_NOSE_TO_CG_M + x_r + 0.05
    half_span = SPAN_M / 2 - POD_MAX_WH_M[0] / 2
    half_chordwise = ROOT_CHORD_M + NACELLE_AHEAD_OF_LE_M
    box = (round(max(pod_len, half_span) + 0.10, 2),
           round(max(half_chordwise, 2 * POD_MAX_WH_M[0]) + 0.05, 2),
           round(2 * PACKED_STACK_H_M + POD_MAX_WH_M[1] + 0.04, 2))
    prop_clear_front = 2 * FRONT_ARM_Y_M - PROP_D_M
    prop_clear_rear = math.hypot(FRONT_ARM_X_M + x_r, FRONT_ARM_Y_M) - PROP_D_M

    return dict(
        battery=dict(name=name, mAh=mah, cells=cells, g=batt_g, usd=batt_usd, Wh=round(wh, 1),
                     usable_Wh=round(usable, 1), hover_C=round(i_hover / (mah / 1000), 1)),
        mass_g=dict(groups={k2: round(v2) for k2, v2 in groups.items()},
                    option_extra=round(extra_g), contingency=round(contingency),
                    battery=batt_g, growth=GROWTH_KG * 1000, mtow=round(mtow_g)),
        wing=dict(span_m=SPAN_M, area_m2=round(S, 3), MAC_m=round(mac(), 3), AR=round(ar, 2),
                  wing_loading_kg_m2=round(ws, 2), CLmax=CL_MAX, stall_m_s=round(vs, 1),
                  transition_min_m_s=round(1.3 * vs, 1)),
        hover=dict(n_lift=n_lift, per_motor_g=round(per_motor_g), TW_table=round(tw_table, 2),
                   TW_with_sag=round(tw_sag, 2), TW_gate=TW_GATE, passes=tw_sag >= TW_GATE,
                   disk_loading_N_m2=round(disk_loading, 1), FMxeta_calibrated=round(eff_cal, 3),
                   P_table_W=round(p_table), P_momentum_W=round(p_mom), P_hover_W=round(p_hover),
                   I_hover_A=round(i_hover, 1), I_transition_A=round(i_transition, 1),
                   I_full_throttle_A=i_peak_full,
                   disconnect_rating_needed_A=round(1.25 * i_transition, 1),
                   gust8_side_tilt_deg=round(tilt_deg, 1)),
        cruise=dict(CD0=CD0, e=OSWALD_E, best_speed_m_s=best["v"], LD=best["LD"],
                    P_elec_W=best["p_elec_W"], I_A=round(best["p_elec_W"] / V_NOM, 1),
                    rpm_needed=best["rpm_needed"], rpm_available_loaded=round(rpm_avail),
                    sweep=sweep),
        endurance=dict(hover_only_min=round(hover_only_min, 1), cruise_min_after_2min_hover=round(cruise_min, 1),
                       threshold_min=CRUISE_THRESHOLD_MIN, objective_min=CRUISE_OBJECTIVE_MIN,
                       meets_threshold=cruise_min >= CRUISE_THRESHOLD_MIN,
                       meets_objective=cruise_min >= CRUISE_OBJECTIVE_MIN,
                       pack_Wh_needed_for_objective=round(pack_wh_needed_obj, 1),
                       E_hover_Wh=round(e_hover, 1), E_transition_Wh=round(e_trans, 1)),
        tilt_servo=dict(gyro_moment_Nm=round(m_gyro, 3), servo_stall_Nm_6V=round(servo_torque_6v, 2),
                        margin_6V=round(servo_torque_6v / m_gyro, 1),
                        note="pivot on the thrust line so thrust gives no hinge moment; drag/offset moments ESTIMATE <0.2 Nm"),
        geometry=dict(front_arm_x_m=FRONT_ARM_X_M, front_arm_y_m=FRONT_ARM_Y_M, rear_arm_x_m=x_r,
                      pod_boom_length_m=round(pod_len, 2), wing_half_length_m=round(half_span, 3),
                      prop_tip_gap_front_m=round(prop_clear_front, 3),
                      prop_tip_gap_front_rear_m=round(prop_clear_rear, 3)),
        packed=dict(box_LxWxH_m=box, longest_piece_m=round(max(pod_len, half_span), 2),
                    pieces="pod+boom (1), wing halves (2), 3 props, battery",
                    passes_C3a=box[0] <= 1.2 and box[1] <= 0.5 and box[2] <= 0.4),
    )


if __name__ == "__main__":
    base = size()
    out = dict(
        concept="K06 scratch-built tilt-tricopter (2 front tilt + 1 fixed rear)",
        mission="REQUIREMENTS.md s3 M-A default",
        mass_items_g=[dict(group=g, item=i, g=round(m, 1)) for g, i, m in MASS_ITEMS],
        baseline=base,
        battery_trade={c[0]: {k: size(batt_idx=i)[k] for k in ("endurance",)} | {
            "mtow_g": size(batt_idx=i)["mass_g"]["mtow"], "TW_with_sag": size(batt_idx=i)["hover"]["TW_with_sag"]}
            for i, c in enumerate(BATT_CANDIDATES)},
        option_K07_fourth_rear_motor=size(extra_g=K07_ADD_G, n_lift=4),
        option_U05_single_tilt_servo=size(extra_g=U05_DELTA_G),
    )
    # strip sweeps from options to keep json short
    for key in ("option_K07_fourth_rear_motor", "option_U05_single_tilt_servo"):
        out[key]["cruise"].pop("sweep")
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sizing.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    b = base
    print(f"MTOW {b['mass_g']['mtow']} g  groups {b['mass_g']['groups']}  contingency {b['mass_g']['contingency']} g")
    print(f"Wing S {b['wing']['area_m2']} m2  W/S {b['wing']['wing_loading_kg_m2']} kg/m2  Vs {b['wing']['stall_m_s']} m/s"
          f"  1.3Vs {b['wing']['transition_min_m_s']}")
    h = b["hover"]
    print(f"Hover {h['P_hover_W']} W ({h['P_table_W']} table / {h['P_momentum_W']} momentum)  {h['I_hover_A']} A"
          f"  T/W {h['TW_table']} (sag {h['TW_with_sag']})  DL {h['disk_loading_N_m2']} N/m2  gust tilt {h['gust8_side_tilt_deg']} deg")
    c = b["cruise"]
    print(f"Cruise {c['best_speed_m_s']} m/s  L/D {c['LD']}  {c['P_elec_W']} W  {c['I_A']} A  rpm need {c['rpm_needed']}"
          f" / avail {c['rpm_available_loaded']}")
    e = b["endurance"]
    print(f"Pack {b['battery']['name']} {b['battery']['Wh']} Wh: hover-only {e['hover_only_min']} min; cruise after 2 min hover"
          f" {e['cruise_min_after_2min_hover']} min (threshold {e['meets_threshold']}, objective {e['meets_objective']})")
    print(f"Packed box {b['packed']['box_LxWxH_m']} m  C3a {b['packed']['passes_C3a']}")
    k7 = out["option_K07_fourth_rear_motor"]
    print(f"K07: MTOW {k7['mass_g']['mtow']} g  T/W sag {k7['hover']['TW_with_sag']}  P {k7['hover']['P_hover_W']} W"
          f"  cruise {k7['endurance']['cruise_min_after_2min_hover']} min")
    print("wrote", path)
