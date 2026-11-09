"""B09 Flightory Stallion VTOL, bought design files, airframe printed in LW-PLA + PETG: first-order sizing.

Run:   python -I sizing.py      (stdlib only; writes sizing.json next to this file)

Layout (Flightory, fixed by the bought files): 1.34 m span, 0.99 m long, twin wing nacelles + V-tail on a 16 mm
carbon tail boom. VTOL pack: the two wing-nacelle motors tilt 90 deg on servos (hover -> cruise tractors), one fixed
vertical rear motor, stopped in cruise. ArduPilot Plane, Q_FRAME_CLASS 7 (Tri), Q_TILT_TYPE 2 (vectored yaw),
Q_TILT_MASK 3, SpeedyBee F405 Wing (Flightory's output map).
Mission: REQUIREMENTS.md section 3 default M-A (hover 2 min total, cruise 5 min threshold / 10 min objective
at 14-20 m/s, 20 % reserve, 0 payload + 0.25 kg growth allowance).
Method and shared assumptions (usable fraction, reserve, transition energy, contingency, sag, install loss, CD0,
battery candidates) are deliberately the same as cards/K06/sizing.py so the two tilt-tris compare fairly.

Tags: ESTIMATE = engineering guess, UNVERIFIED = not checked against a primary source.
Sources (seen 2026-11-09):
  [F1] https://flightory.com/?p=3082  Stallion: span 1340 mm, length 990 mm, AUW 1500-3000 g, optimal speed
       60-70 km/h, LW-PLA + PETG, carbon tubes 10x800, 8x600, 2x 6x435, 16x430, 2x 4x260, 2x 4x250; $34.99;
       "Licensed for personal use only".
  [F2] https://flightory.com/?p=3755  VTOL pack: AUW 2000-3000 g, Emax ECO II 2807 1300KV or T-Motor F90 1300KV,
       7x4/7x5/7x6 props, 2 tilt servos (Kingmax 1203MD / GDW DS041MG / PowerHD 1810MG), 3x 45 A ESC,
       4S LiPo or up to 4S3P Li-ion; $14.99.
  [F3] Flightory VTOL manual V2 (flightory.com/wp-content/uploads/2025/02/STALLION-MANUAL-VTOL-V2.pdf, via search
       summary): tilt rate 15 deg/s (6 s full tilt), output map assumes SpeedyBee F405 Wing. Forum: CG 60 mm
       from LE; "they only sell designs, not PID values" (discuss.ardupilot.org, UNVERIFIED).
  [E1] Emax ECO II 2807 1700KV listings: 47.9 g w/o leads, max thrust 2100 g on 4S (6-7 in prop), peak 52 A,
       870 W on 4S (robu.in / readymaderc.com / fpvracing.ch search listings; not a maker test table, UNVERIFIED).
"""
import json
import math
import os

# ======================================================================================
# ASSUMPTIONS (edit here only)
# ======================================================================================
G = 9.81
RHO = 1.225                      # kg/m3, sea level ISA (RFS is ~ sea level)

# ---- mission (REQUIREMENTS.md s3, M-A default; same as K06) ----
HOVER_S = 120.0
TRANSITION_S = 2 * 15.0          # forward + back transition, s, ESTIMATE (manual tilt 6 s + accel)
TRANSITION_POWER_FACTOR = 1.25   # x hover power, ESTIMATE
CRUISE_THRESHOLD_MIN = 5.0
CRUISE_OBJECTIVE_MIN = 10.0
RESERVE_FRAC = 0.20
USABLE_FRAC = 0.80               # ESTIMATE
GROWTH_KG = 0.25
MASS_CONTINGENCY = 0.10          # on non-battery build-up, ESTIMATE
TW_GATE = 1.6                    # D11

# ---- propulsion: Emax ECO II 2807 1700KV + 7x5 two-blade, 4S ----
# Flightory lists the 1300KV (a 6S motor); on 4S its thrust drops to roughly (14.8/22.2)^2 = 0.44 of its 6S value,
# so this card specifies the same-size 1700KV variant (same can, same mount) as the 4S choice. ESTIMATE/UNVERIFIED.
N_LIFT = 3
PROP_D_M = 7 * 0.0254
MOTOR_MAX_THRUST_G = 2100.0      # [E1] listing, 4S
MOTOR_MAX_POWER_W = 870.0        # [E1] listing, 4S
MOTOR_PEAK_A = 52.0              # [E1]
HOVER_EFF_GAIN = 1.15            # FM*eta at part throttle vs at the max point, ESTIMATE
SAG_THRUST_FACTOR = 0.90         # as K06, ESTIMATE
INSTALL_LOSS = 1.10              # nacelle/wing blockage under front props, boom/V-tail under rear prop, ESTIMATE
KV = 1700.0
V_NOM = 14.8
ESC_RATING_A = 45.0              # [F2]

# hover arms (Stallion geometry not published; ESTIMATE from 990 mm length, CG 60 mm aft of LE [F3])
FRONT_ARM_X_M = 0.21             # front prop axes ahead of CG in hover, ESTIMATE
REAR_ARM_X_M = 0.36              # rear prop axis behind CG, ESTIMATE (equal share would need 0.42)
FRONT_ARM_Y_M = 0.22             # nacelle lateral offset, ESTIMATE

# ---- airframe geometry (span [F1]; chords ESTIMATE, consistent with CG 60 mm at ~25 % root chord) ----
SPAN_M = 1.34
ROOT_CHORD_M = 0.24
TIP_CHORD_M = 0.16
LENGTH_M = 0.99                  # [F1]
CL_MAX = 1.20                    # cambered section + conventional (V) tail, flaperons neutral, ESTIMATE
CD0 = 0.040                      # same as K06: fuselage + 2 nacelles + V-tail + stopped rear 7 in prop, ESTIMATE
OSWALD_E = 0.80                  # ESTIMATE

# ---- cruise propulsion: two front motors as tractors ----
PROP_EFF_CRUISE = 0.58           # 7x5 at J ~ 0.6, ESTIMATE
MOTOR_ESC_EFF_CRUISE = 0.72      # high-KV motor lightly loaded, ESTIMATE
J_CRUISE = 0.60
LOADED_RPM_FRAC = 0.85

# ---- battery candidates (same list as K06) ----
BATT_CANDIDATES = [  # name, mAh, cells, g, $ (each)
    ("Ovonic 4S 3300 50C (ESTIMATE mass/price)", 3300, 4, 330, 33.00),
    ("Ovonic 4S 5000 50C XT60", 5000, 4, 448, 48.57),
    ("Ovonic 4S 6500 (cost_model.py pack_S, ESTIMATE mass)", 6500, 4, 590, 45.42),
]
BATT_CHOICE = 1

# ---- printing ----
LWPLA_RATE_G_H = 10.0            # foamed LW-PLA on a Prusa MK4/MK3S, ESTIMATE
PETG_RATE_G_H = 15.0             # ESTIMATE
PRINT_SCRAP_FACTOR = 1.30        # failed/reprinted parts, first-time LW-PLA tuning, ESTIMATE
N_PRINTERS = 2                   # Jacobs Prusas the team can hold at once, ESTIMATE
PRINTER_H_PER_DAY = 8.0          # staffed hours only, ESTIMATE (Jacobs overnight-print policy UNVERIFIED)

CF_RHO = 1550.0


def tube_g(od_mm, id_mm, length_m):
    return math.pi / 4 * (od_mm ** 2 - id_mm ** 2) * 1e-6 * CF_RHO * 1000 * length_m


# ---- mass build-up, g (non-battery) ----
MASS_ITEMS = [
    # printed structure (Stallion files; masses ESTIMATE, base Stallion AUW 1500 g lower bound [F1])
    ("printed", "2 VTOL wing halves LW-PLA incl. nacelles, ailerons/flaperons, ESTIMATE", 380),
    ("printed", "fuselage + hatch LW-PLA, ESTIMATE", 250),
    ("printed", "V-tail halves LW-PLA, ESTIMATE", 70),
    ("printed", "PETG hard points: spar roots, tilt mounts, motor mounts, boom clamps, skids, ESTIMATE", 100),
    # carbon (sizes [F1]; wall thickness ESTIMATE)
    ("carbon", "main spar 10x8x800 (calc)", tube_g(10, 8, 0.80)),
    ("carbon", "secondary spar 8x6x600 (calc)", tube_g(8, 6, 0.60)),
    ("carbon", "2x wing spar 6x4x435 (calc)", tube_g(6, 4, 0.87)),
    ("carbon", "tail boom 16x14x430 (calc)", tube_g(16, 14, 0.43)),
    ("carbon", "4x V-tail spar 4x2x255 (calc)", tube_g(4, 2, 1.02)),
    # propulsion
    ("propulsion", "3x Emax ECO II 2807 1700KV (47.9 g + leads) [E1]", 3 * 54),
    ("propulsion", "3x 7x5 two-blade props, ESTIMATE", 3 * 9),
    ("propulsion", "3x LANRC 45A BLHeli_S ESC (6.6 g listing, as K06)", 3 * 6.6),
    ("propulsion", "motor/ESC wiring, XT60s, 14 AWG runs through wing, ESTIMATE", 85),
    # tilt
    ("tilt", "2x PowerHD 1810MG class tilt servo (~16 g, ESTIMATE)", 2 * 16),
    ("tilt", "2x 3x8x4 flange bearings + M3 pivot hardware [F2], ESTIMATE", 2 * 4),
    # control
    ("control", "4x EMAX ES08MA II (12 g) ailerons + ruddervators", 4 * 12),
    ("control", "horns, pushrods, hinges (printed-in), ESTIMATE", 15),
    # avionics
    ("avionics", "SpeedyBee F405 Wing + cables, ESTIMATE", 32),
    ("avionics", "GPS/compass M10 class, ESTIMATE", 12),
    ("avionics", "ELRS RP3 V2 receiver + antenna", 4),
    ("avionics", "MS5525/4525 airspeed + pitot + tubing, ESTIMATE", 15),
    ("avionics", "BeeID Remote ID (conditional, carried in mass), ESTIMATE", 7),
    ("avionics", "AS150U disconnect + pack lead, ESTIMATE", 25),
    ("hardware", "M3 screws, heat-set inserts, CA/epoxy, ESTIMATE", 40),
]

# ======================================================================================
# CALCULATIONS
# ======================================================================================


def wing_area():
    return SPAN_M * (ROOT_CHORD_M + TIP_CHORD_M) / 2


S = wing_area()
DISK_A = math.pi * PROP_D_M ** 2 / 4
# overall FM x motor x ESC at the max point [E1], then a part-throttle gain
_T_MAX_N = MOTOR_MAX_THRUST_G / 1000 * G
EFF_MAX = (_T_MAX_N ** 1.5 / math.sqrt(2 * RHO * DISK_A)) / MOTOR_MAX_POWER_W
EFF_HOVER = EFF_MAX * HOVER_EFF_GAIN


def motor_power(thrust_g):
    t = thrust_g / 1000 * G
    return t ** 1.5 / math.sqrt(2 * RHO * DISK_A) / EFF_HOVER


def size(batt_idx=BATT_CHOICE):
    name, mah, cells, batt_g, batt_usd = BATT_CANDIDATES[batt_idx]
    groups = {}
    for grp, _, g in MASS_ITEMS:
        groups[grp] = groups.get(grp, 0.0) + g
    nonbatt = sum(groups.values())
    contingency = nonbatt * MASS_CONTINGENCY
    mtow_g = nonbatt + contingency + batt_g + GROWTH_KG * 1000
    W = mtow_g / 1000 * G

    # wing
    ws = mtow_g / 1000 / S
    vs = math.sqrt(2 * W / (RHO * S * CL_MAX))
    ar = SPAN_M ** 2 / S

    # hover thrust split from moment balance: 2 Tf xf = Tr xr, 2 Tf + Tr = W
    xf, xr = FRONT_ARM_X_M, REAR_ARM_X_M
    # 2 Tf xf = Tr xr  ->  Tf = Tr xr / (2 xf);  2 Tf + Tr = W  ->  Tr (xr/xf + 1) = W
    tr_g = mtow_g / (xr / xf + 1)
    tf_g = (mtow_g - tr_g) / 2
    worst_g = max(tr_g, tf_g)
    tw_total = MOTOR_MAX_THRUST_G * N_LIFT / mtow_g
    tw_worst = MOTOR_MAX_THRUST_G / worst_g   # the most-loaded motor saturates first
    tw_worst_sag = tw_worst * SAG_THRUST_FACTOR
    disk_loading = W / (N_LIFT * DISK_A)
    p_hover = (2 * motor_power(tf_g) + motor_power(tr_g)) * INSTALL_LOSS
    i_hover = p_hover / V_NOM
    p_trans = p_hover * TRANSITION_POWER_FACTOR
    i_transition = p_trans / (V_NOM * 0.95)
    i_worst_motor = motor_power(worst_g) * INSTALL_LOSS / V_NOM

    # cruise sweep 14-20 m/s, >= 1.3 Vs
    k = 1 / (math.pi * OSWALD_E * ar)
    sweep = []
    for v10 in range(140, 201, 5):
        v = v10 / 10
        q = 0.5 * RHO * v * v
        cl = W / (q * S)
        cd = CD0 + k * cl * cl
        drag = q * S * cd
        p_elec = drag * v / (PROP_EFF_CRUISE * MOTOR_ESC_EFF_CRUISE)
        rpm_need = v / (J_CRUISE * PROP_D_M) * 60
        sweep.append(dict(v=v, cl=round(cl, 3), LD=round(cl / cd, 2), drag_N=round(drag, 2),
                          p_elec_W=round(p_elec, 1), rpm_needed=round(rpm_need), ok_vs=v >= 1.3 * vs))
    valid = [s for s in sweep if s["ok_vs"]]
    best = min(valid, key=lambda s: s["p_elec_W"])
    rpm_avail = KV * V_NOM * LOADED_RPM_FRAC

    # energy
    wh = mah / 1000 * cells * 3.7
    usable = wh * USABLE_FRAC
    e_hover = p_hover * HOVER_S / 3600
    e_trans = p_trans * TRANSITION_S / 3600
    e_cruise_avail = usable * (1 - RESERVE_FRAC) - e_hover - e_trans
    cruise_min = e_cruise_avail / best["p_elec_W"] * 60
    hover_only_min = usable * (1 - RESERVE_FRAC) / p_hover * 60
    e_obj = e_hover + e_trans + best["p_elec_W"] * CRUISE_OBJECTIVE_MIN / 60
    pack_wh_needed_obj = e_obj / (USABLE_FRAC * (1 - RESERVE_FRAC))

    # hover in an 8 m/s lateral gust
    side_area = 0.10   # fuselage 0.99 m x ~0.09 m + V-tail projection + nacelles, m2, ESTIMATE
    f_side = 0.5 * RHO * 8 ** 2 * side_area * 1.2
    tilt_deg = math.degrees(math.atan(f_side / W))

    # tilt servo: gyroscopic moment, 2 rad/s body rate
    prop_mass = 0.009
    i_prop = prop_mass * PROP_D_M ** 2 / 12
    rpm_hover = 13000.0   # ESTIMATE for ~0.75 kg on a 7x5
    m_gyro = i_prop * rpm_hover * 2 * math.pi / 60 * 2.0
    servo_6v = 3.9 * G / 100   # PowerHD 1810MG ~3.9 kg-cm @ 6 V, UNVERIFIED

    # packing: wing halves slide off the 10 mm main spar; spar comes out; fuselage + boom + V-tail stays whole
    # V-tail halves unplug from their 4 mm spars (UNVERIFIED: may be glued -> box height +0.1 m)
    half_span = SPAN_M / 2 - 0.05
    half_chordwise = ROOT_CHORD_M + 0.15          # nacelle ahead of LE, ESTIMATE
    fus_wh = (0.11, 0.13)                         # fuselage width, height, ESTIMATE
    wing_stack_t = 0.07                           # wing half thickness at the nacelle, motor on, props off, ESTIMATE
    # layout: fuselage on the box floor, two wing halves stacked flat above it, V-tail halves + spar alongside
    box = (round(max(LENGTH_M, half_span) + 0.10, 2),
           round(max(half_chordwise, fus_wh[0] + 0.15) + 0.05, 2),
           round(fus_wh[1] + 2 * wing_stack_t + 0.04, 2))
    prop_gap_front = 2 * FRONT_ARM_Y_M - PROP_D_M

    # print time
    lw_g = sum(g for grp, i, g in MASS_ITEMS if grp == "printed" and "LW-PLA" in i)
    petg_g = sum(g for grp, i, g in MASS_ITEMS if grp == "printed" and "PETG" in i)
    print_h = (lw_g / LWPLA_RATE_G_H + petg_g / PETG_RATE_G_H) * PRINT_SCRAP_FACTOR
    print_days = print_h / (N_PRINTERS * PRINTER_H_PER_DAY)
    wing_half_reprint_h = 190 / LWPLA_RATE_G_H * PRINT_SCRAP_FACTOR

    return dict(
        battery=dict(name=name, mAh=mah, cells=cells, g=batt_g, usd=batt_usd, Wh=round(wh, 1),
                     usable_Wh=round(usable, 1), hover_C=round(i_hover / (mah / 1000), 1)),
        mass_g=dict(groups={k2: round(v2) for k2, v2 in groups.items()}, contingency=round(contingency),
                    battery=batt_g, growth=GROWTH_KG * 1000, mtow=round(mtow_g),
                    flightory_AUW_band_g=[2000, 3000], inside_band=2000 <= mtow_g <= 3000),
        wing=dict(span_m=SPAN_M, area_m2=round(S, 3), AR=round(ar, 2), wing_loading_kg_m2=round(ws, 2),
                  CLmax=CL_MAX, stall_m_s=round(vs, 1), transition_min_m_s=round(1.3 * vs, 1),
                  flightory_optimal_m_s=[16.7, 19.4]),
        hover=dict(n_lift=N_LIFT, front_motor_g=round(tf_g), rear_motor_g=round(tr_g),
                   TW_total=round(tw_total, 2), TW_worst_motor=round(tw_worst, 2),
                   TW_worst_motor_with_sag=round(tw_worst_sag, 2), TW_gate=TW_GATE,
                   passes=tw_worst_sag >= TW_GATE, disk_loading_N_m2=round(disk_loading, 1),
                   FMxeta_at_max=round(EFF_MAX, 3), FMxeta_hover=round(EFF_HOVER, 3),
                   P_hover_W=round(p_hover), I_hover_A=round(i_hover, 1),
                   I_worst_motor_hover_A=round(i_worst_motor, 1), I_transition_A=round(i_transition, 1),
                   I_full_throttle_A=N_LIFT * MOTOR_PEAK_A, ESC_rating_A=ESC_RATING_A,
                   ESC_below_motor_peak=ESC_RATING_A < MOTOR_PEAK_A,
                   disconnect_rating_needed_A=round(1.25 * i_transition, 1),
                   gust8_side_tilt_deg=round(tilt_deg, 1)),
        cruise=dict(CD0=CD0, e=OSWALD_E, best_speed_m_s=best["v"], LD=best["LD"], P_elec_W=best["p_elec_W"],
                    I_A=round(best["p_elec_W"] / V_NOM, 1), rpm_needed=best["rpm_needed"],
                    rpm_available_loaded=round(rpm_avail), sweep=sweep),
        endurance=dict(hover_only_min=round(hover_only_min, 1),
                       cruise_min_after_2min_hover=round(cruise_min, 1),
                       threshold_min=CRUISE_THRESHOLD_MIN, objective_min=CRUISE_OBJECTIVE_MIN,
                       meets_threshold=cruise_min >= CRUISE_THRESHOLD_MIN,
                       meets_objective=cruise_min >= CRUISE_OBJECTIVE_MIN,
                       pack_Wh_needed_for_objective=round(pack_wh_needed_obj, 1),
                       E_hover_Wh=round(e_hover, 1), E_transition_Wh=round(e_trans, 1)),
        tilt_servo=dict(gyro_moment_Nm=round(m_gyro, 3), servo_stall_Nm_6V=round(servo_6v, 2),
                        margin_6V=round(servo_6v / m_gyro, 1),
                        note="thrust-line offset and aero moments on the nacelle not modelled; bench-test it"),
        geometry=dict(front_arm_x_m=xf, rear_arm_x_m=xr, front_arm_y_m=FRONT_ARM_Y_M,
                      prop_tip_gap_between_front_props_m=round(prop_gap_front, 3)),
        packed=dict(box_LxWxH_m=box, longest_piece_m=LENGTH_M,
                    pieces="fuselage+boom+V-tail (1), wing halves (2), 10 mm main spar (1), 3 props, battery",
                    passes_C3a=box[0] <= 1.2 and box[1] <= 0.5 and box[2] <= 0.4),
        printing=dict(LWPLA_g=lw_g, PETG_g=petg_g, printer_hours=round(print_h), calendar_days=round(print_days, 1),
                      wing_half_reprint_h=round(wing_half_reprint_h, 1)),
    )


if __name__ == "__main__":
    base = size()
    out = dict(
        concept="B09 Flightory Stallion VTOL, bought files, printed LW-PLA/PETG airframe, tilt-tri",
        mission="REQUIREMENTS.md s3 M-A default",
        mass_items_g=[dict(group=g, item=i, g=round(m, 1)) for g, i, m in MASS_ITEMS],
        baseline=base,
        battery_trade={c[0]: dict(mtow_g=size(i)["mass_g"]["mtow"],
                                  TW_worst_sag=size(i)["hover"]["TW_worst_motor_with_sag"],
                                  **size(i)["endurance"]) for i, c in enumerate(BATT_CANDIDATES)},
    )
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sizing.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    b = base
    print(f"MTOW {b['mass_g']['mtow']} g  groups {b['mass_g']['groups']}  contingency {b['mass_g']['contingency']} g")
    print(f"Wing S {b['wing']['area_m2']} m2 AR {b['wing']['AR']}  W/S {b['wing']['wing_loading_kg_m2']} kg/m2"
          f"  Vs {b['wing']['stall_m_s']}  1.3Vs {b['wing']['transition_min_m_s']}")
    h = b["hover"]
    print(f"Hover {h['P_hover_W']} W {h['I_hover_A']} A  front {h['front_motor_g']} g rear {h['rear_motor_g']} g"
          f"  T/W total {h['TW_total']} worst {h['TW_worst_motor']} (sag {h['TW_worst_motor_with_sag']})"
          f"  DL {h['disk_loading_N_m2']} N/m2  FM*eta {h['FMxeta_hover']}  trans {h['I_transition_A']} A"
          f"  gust tilt {h['gust8_side_tilt_deg']} deg")
    c = b["cruise"]
    print(f"Cruise {c['best_speed_m_s']} m/s L/D {c['LD']} {c['P_elec_W']} W {c['I_A']} A"
          f"  rpm {c['rpm_needed']}/{c['rpm_available_loaded']}")
    e = b["endurance"]
    print(f"Pack {b['battery']['name']}: hover-only {e['hover_only_min']} min; cruise after hover"
          f" {e['cruise_min_after_2min_hover']} min (thr {e['meets_threshold']}, obj {e['meets_objective']})")
    for n, r in out["battery_trade"].items():
        print(f"   {n}: MTOW {r['mtow_g']} g  cruise {r['cruise_min_after_2min_hover']} min  T/W {r['TW_worst_sag']}")
    print(f"Tilt servo margin {b['tilt_servo']['margin_6V']}x  Packed {b['packed']['box_LxWxH_m']} C3a "
          f"{b['packed']['passes_C3a']}  Print {b['printing']}")
    print("wrote", path)
