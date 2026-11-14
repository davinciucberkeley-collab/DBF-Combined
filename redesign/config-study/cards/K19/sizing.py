"""K19 - Flying-wing (tailless) quadplane 4+1, X8 / DeltaQuad style. First-order sizing.

Run:  python -I sizing.py      (stdlib only; writes sizing.json next to this file)

Method (same as every concept card): mass build-up by group -> wing loading / stall -> hover power from
momentum theory (disk loading, figure of merit) cross-checked against the motor maker's thrust table ->
cruise power from a drag build-up (L/D stated) -> mission energy on the study pack -> packed dimensions.
Mission = REQUIREMENTS.md section 3 default M-A: hover >= 2 min total, cruise >= 5 min threshold / 10 min objective
at 14-20 m/s, land with 20 % reserve, 0 payload + 0.25 kg growth allowance.
Tags: ESTIMATE = engineering guess; SRC = sourced (citation in comment); CALC = derived here.
Status of every number: PROPOSED.
"""
import json, math, os

# ============================== ASSUMPTIONS (edit here) ==============================
G, RHO = 9.81, 1.225                      # sea level, ISA 15 C; RFS is at ~10 m elevation

# ---- geometry (PROPOSED, chosen so the centre section + booms fit a 0.5 m wide box) ----
SPAN = 1.60          # m  ESTIMATE choice: smallest span that gives Vs < 12 m/s at ~3 kg with CLmax 0.75
C_ROOT = 0.42        # m  root chord (centre line)
C_TIP = 0.20         # m  tip chord
SWEEP_LE_DEG = 25.0  # deg leading-edge sweep (X8 ~ 30 deg; less sweep = less tip stall) ESTIMATE
CENTRE_W = 0.44      # m  centre section width (booms clamp at its edges, y = +/-0.22 m)
BOOM_Y = 0.22        # m  boom lateral station
BOOM_DX = 0.38       # m  lift motors +/- this far fore/aft of the CG (0.34 gave 0 mm pusher clearance)
BOOM_L = 0.86        # m  boom tube length (22x20 CF, cut from 1 m)
T_C = 0.12           # thickness/chord, reflexed section (e.g. MH-45 class, 9.85 %; centre bulge thicker) ESTIMATE
WINGLET_AREA = 0.025 # m^2 each (vertical fins at tips; flying wings need them for yaw stability) ESTIMATE
FOOT_H = 0.15        # m  printed feet below boom, sets pusher-prop ground clearance

# ---- propulsion (class S, 4S - same parts as cost_model.py "S quadplane 4+1") ----
N_LIFT = 4
PROP_D_IN = 11.0                     # APC 11x4.5MR  SRC cost_model.py / budget-lift.md
LIFT_TMAX_G = 1580.0                 # SunnySky X3108S KV900 + APC 11x4.7 @14.8 V, max thrust  SRC maker table
MAKER_TABLE = [(690, 89.0), (750, 104.0), (870, 133.0), (1580, 447.0)]  # (g, W) per motor @14.8 V SRC same
FM = 0.62            # figure of merit, 11 in fixed-pitch multirotor prop  ESTIMATE
ETA_MOTOR_HOVER = 0.80   # ESTIMATE
ETA_ESC = 0.95           # ESTIMATE
DOWNLOAD = 0.03      # fraction of hover thrust lost to wing blockage; rear disc overlaps TE by ~30 mm only CALC/ESTIMATE
HOVER_CTRL_MARGIN = 0.10   # extra hover power for attitude control in 5 m/s wind ESTIMATE
PUSHER_PROP = "APC 9x6E"   # 9 in keeps disc clear of rear lift props (see packing/clearance below) PROPOSED
ETA_PROP_CRUISE = 0.55     # pusher prop at J ~ 0.65  ESTIMATE (configurations.md base 0.551)
ETA_MOTOR_CRUISE = 0.80    # ESTIMATE
AVIONICS_W = 6.0           # FC + GPS + RX + RID + servos average  ESTIMATE

# ---- aerodynamics ----
CLMAX = 0.75         # reflexed flying-wing section, whole aircraft, elevons neutral ESTIMATE (X8 stall ~14 m/s at higher W/S)
E_OSWALD = 0.80      # swept wing with winglets ESTIMATE
CD0_WING = 0.012     # wing + winglets skin friction, Re ~ 3e5  ESTIMATE
CDA = {              # extra parasite area, m^2  (all ESTIMATE; scaled from docs/research/aerodynamics.md C0 values)
    "centre body bulge / battery bay": 0.0030,
    "2 booms, 22 mm, axial + end caps": 0.0012,
    "4 stopped lift units (motor + 11 in prop, random azimuth)": 4 * 0.0016,  # C0 17 in: 0.0034 x (11/17)^2 = 0.0014 -> 0.0016
    "4 printed feet": 4 * 0.0004,
    "elevon horns, pitot, antennas": 0.0006,
}
CD0_MISC_FACTOR = 1.10       # +10 % interference / leakage ESTIMATE
V_CRUISE = 16.0              # m/s, chosen inside 1.3-1.6 Vs band CALC check below

# ---- battery (study pack, class S) ----
PACK_NAME = "Ovonic 4S 6500 mAh 50C (14.8 V nominal)"
PACK_V, PACK_AH = 14.8, 6.5
PACK_MASS_G = 560            # 522 g +/-20 listed (rcdrone.top) + leads/hardcase allowance ESTIMATE
V_UNDER_LOAD = 14.0          # average pack voltage in hover ESTIMATE
RESERVE = 0.20               # land with 20 % (REQUIREMENTS s3)
HOVER_MIN = 2.0              # mission hover, total
TRANS_S = 2 * 20.0           # forward + back transition, s ESTIMATE
CLIMB_EXTRA_WH = 1.5         # climb to 40 m in hover, extra over hover power ESTIMATE

# ---- mass build-up, grams (SRC where a maker mass exists, else ESTIMATE) ----
CF_22x20_G_PER_M = 102       # SRC budget-airframe.md (rho 1.55 calc)
XPS_KG_M3 = 28.0             # FOAMULAR F-250 ~1.75 pcf  ESTIMATE
TAPE_G_M2 = 60.0             # packing-tape skin ESTIMATE (M2 weigh test pending)
MASS = {
    "propulsion": {
        "4 x SunnySky X3108S KV900 (81 g SRC)": 4 * 81,
        "4 x LANRC 45A ESC (6.6 g SRC) + 18 AWG leads": 4 * (6.6 + 12),
        "4 x APC 11x4.5MR (~18 g) ESTIMATE": 4 * 18,
        "4 x printed PETG motor mounts ESTIMATE": 4 * 12,
        "pusher SunnySky X2814 900KV ESTIMATE 107 g + ESC + 9x6E prop + mount": 107 + 19 + 15 + 20,
    },
    "structure": {
        "wing foam (CALC below)": None,
        "tape skin (CALC below)": None,
        "spar/joiner 22x20 CF, 0.74 m": round(0.74 * CF_22x20_G_PER_M),
        "2 booms 22x20 CF, 0.86 m": round(2 * BOOM_L * CF_22x20_G_PER_M),
        "boom-to-spar printed saddles + ply hard-point plates ESTIMATE": 90,
        "centre body: ply battery tray, hatch, printed nose ESTIMATE": 140,
        "2 winglets, 3 mm depron/coroplast + plug ESTIMATE": 60,
        "elevons: hinge tape, horns, pushrods ESTIMATE": 30,
        "4 printed feet ESTIMATE": 4 * 15,
        "joint pins, nylon bolts, magnets, glue ESTIMATE": 60,
    },
    "systems": {
        "2 x EMAX ES3005HV elevon servos (43.2 g SRC)": 2 * 43.2,
        "FC CoreWing F405 Wing V2 + GPS + RX + RID ESTIMATE": 25 + 20 + 5 + 12,
        "airspeed MS5525 + pitot ESTIMATE": 15,
        "power wiring: 10 AWG, AS150U/XT90, bus, UBEC, servo extensions ESTIMATE": 130,
    },
    "battery": {PACK_NAME: PACK_MASS_G},
    "allowances": {"growth allowance (REQUIREMENTS s3)": 250},
}
STRUCT_CONTINGENCY = 0.10     # +10 % on structure+systems for an unbuilt foam airframe ESTIMATE

# ---- bought-shell variant (Skywalker X8, 2.12 m) - checked, not baseline ----
X8 = dict(span=2.12, area=0.80, airframe_g=1300, aw_note="kit airframe mass ESTIMATE; builder X8 quadplane 5.1 kg (configurations.md S33)",
          quadplane_mtow_g=5100)

# ============================== CALCULATIONS ==============================
def interp(table, x):
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError("outside table")

# geometry
taper = C_TIP / C_ROOT
S = SPAN * (C_ROOT + C_TIP) / 2
AR = SPAN ** 2 / S
MAC = 2 / 3 * C_ROOT * (1 + taper + taper ** 2) / (1 + taper)
Y_MAC = SPAN / 6 * (1 + 2 * taper) / (1 + taper)
X_LE_MAC = Y_MAC * math.tan(math.radians(SWEEP_LE_DEG))
X_NP = X_LE_MAC + 0.25 * MAC * 1.0 + 0.0  # quarter-MAC, aft-swept wing aero centre ESTIMATE (no tail)
STATIC_MARGIN = 0.08                       # flying-wing target 6-10 % MAC ESTIMATE
X_CG = X_NP - STATIC_MARGIN * MAC          # m behind root LE
X_FRONT, X_REAR = X_CG - BOOM_DX, X_CG + BOOM_DX
X_PUSHER_PROP = C_ROOT + 0.05

# foam volume ~ 0.68 * t * area (airfoil area factor), centre bulge adds 20 %
wing_vol = 0.68 * T_C * (C_ROOT + C_TIP) / 2 * S * 1.20 + 2 * WINGLET_AREA * 0.0
MASS["structure"]["wing foam (CALC below)"] = round(wing_vol * XPS_KG_M3 * 1000)
MASS["structure"]["tape skin (CALC below)"] = round(2.05 * S * TAPE_G_M2)

group = {g: sum(v.values()) for g, v in MASS.items()}
contingency = STRUCT_CONTINGENCY * (group["structure"] + group["systems"])
mtow_g = sum(group.values()) + contingency
W = mtow_g / 1000 * G

# wing loading and stall
WS = W / S
VS = math.sqrt(2 * WS / (RHO * CLMAX))
V_TRANS_MIN = 1.3 * VS

# hover: momentum theory and maker table
prop_d = PROP_D_IN * 0.0254
A_disc = math.pi * prop_d ** 2 / 4
T_motor = W * (1 + DOWNLOAD) / N_LIFT
DL = T_motor / A_disc
P_ideal = T_motor ** 1.5 / math.sqrt(2 * RHO * A_disc)
P_mt = P_ideal / FM / ETA_MOTOR_HOVER / ETA_ESC              # electrical per motor
P_table = interp(MAKER_TABLE, T_motor / G * 1000) / ETA_ESC   # maker table (motor input) + ESC loss
P_motor_hover = max(P_mt, P_table)
P_hover = N_LIFT * P_motor_hover * (1 + HOVER_CTRL_MARGIN) + AVIONICS_W
I_hover = P_hover / V_UNDER_LOAD
TW = N_LIFT * LIFT_TMAX_G / mtow_g

# cruise
q = 0.5 * RHO * V_CRUISE ** 2
CL = WS / q
cda_sum = sum(CDA.values())
CD0 = (CD0_WING + cda_sum / S) * CD0_MISC_FACTOR
k = 1 / (math.pi * E_OSWALD * AR)
CD = CD0 + k * CL ** 2
LD = CL / CD
D = W / LD
P_cruise = D * V_CRUISE / (ETA_PROP_CRUISE * ETA_MOTOR_CRUISE * ETA_ESC) + AVIONICS_W
I_cruise = P_cruise / PACK_V
# best-L/D speed for reference
CL_md = math.sqrt(CD0 / k)
V_md = math.sqrt(2 * WS / (RHO * CL_md))
LD_max = 1 / (2 * math.sqrt(CD0 * k))

# transition: lift motors at hover power fading + pusher near full (ESTIMATE pusher 25 A)
P_pusher_max = 25.0 * PACK_V
P_trans = N_LIFT * P_motor_hover + P_pusher_max + AVIONICS_W
I_trans = P_trans / 13.5
I_all_max = N_LIFT * 30 + 25          # every motor at full throttle, A (maker table 30 A each)

# energy
E_pack = PACK_V * PACK_AH
E_usable = E_pack * (1 - RESERVE)
E_hover = P_hover * HOVER_MIN / 60
E_trans = P_trans * TRANS_S / 3600
E_cruise_avail = E_usable - E_hover - E_trans - CLIMB_EXTRA_WH
cruise_min = E_cruise_avail / P_cruise * 60
hover_only_min = E_usable / P_hover * 60

# packing: centre section with booms + feet + motors; outer panels; winglets plug in
outer_panel_span = (SPAN - CENTRE_W) / 2
centre_pkg = (round(max(BOOM_L, 2 * BOOM_DX + prop_d) + 0.02, 2),   # props parked fore-aft along booms
              round(CENTRE_W + 0.025 + 0.01, 2),
              round(FOOT_H + 0.025 + 0.06 + 0.03, 2))                 # feet + boom + motor/prop + wing
panel_pkg = (round(outer_panel_span, 2), round(C_ROOT - (C_ROOT - C_TIP) * CENTRE_W / SPAN + 0.0, 2), 0.06)
box = (1.20, 0.50, 0.40)
fits_box = (centre_pkg[0] <= box[0] and centre_pkg[1] <= box[1]
            and centre_pkg[2] + 2 * panel_pkg[2] <= box[2] and panel_pkg[0] <= box[0] - 0.0)

# pusher / rear lift prop clearance, worst case: both discs treated as coplanar in plan view
# (rear lift prop plane sits within the pusher disc height band). Distance from the pusher disc edge point
# (X_PUSHER_PROP, r_p) to the rear lift hub, minus the lift prop radius.
r_l, r_p = prop_d / 2, 9 * 0.0254 / 2
clear_x = math.hypot(X_REAR - X_PUSHER_PROP, BOOM_Y - r_p) - r_l

# X8 bought-shell variant on the same class-S stations
x8_tw = N_LIFT * LIFT_TMAX_G / X8["quadplane_mtow_g"]
x8_ws = X8["quadplane_mtow_g"] / 1000 * G / X8["area"]
x8_vs = math.sqrt(2 * x8_ws / (RHO * CLMAX))

r = lambda x, n=2: round(x, n)
out = {
    "concept": "K19 flying-wing (tailless) quadplane 4+1, scratch XPS foam, class S 4S",
    "status": "PROPOSED",
    "mission": "M-A default (REQUIREMENTS s3): hover 2 min, cruise >=5/10 min, 20 % reserve, +0.25 kg growth",
    "geometry": {"span_m": SPAN, "area_m2": r(S, 3), "AR": r(AR), "root_chord_m": C_ROOT, "tip_chord_m": C_TIP,
                 "MAC_m": r(MAC, 3), "x_cg_behind_root_LE_m": r(X_CG, 3), "static_margin_MAC": STATIC_MARGIN,
                 "lift_motor_x_m": [r(X_FRONT, 3), r(X_REAR, 3)], "boom_y_m": BOOM_Y,
                 "outer_panel_span_m": r(outer_panel_span), "pusher_to_rear_disc_clearance_m": r(clear_x, 3)},
    "mass_g": {g: {k2: round(v2, 1) for k2, v2 in v.items()} for g, v in MASS.items()},
    "mass_group_totals_g": {g: round(v) for g, v in group.items()},
    "contingency_g": round(contingency), "mtow_kg": r(mtow_g / 1000, 3),
    "mass_gate_kg_(+5%)": r(mtow_g / 1000 * 1.05, 3),
    "wing_loading_N_m2": r(WS, 1), "wing_loading_kg_m2": r(WS / G, 2),
    "stall_mps": r(VS), "transition_min_1p3Vs_mps": r(V_TRANS_MIN), "cruise_mps": V_CRUISE,
    "hover": {"thrust_per_motor_g": r(T_motor / G * 1000, 0), "disk_loading_N_m2": r(DL, 1),
              "P_momentum_per_motor_W": r(P_mt, 1), "P_maker_table_per_motor_W": r(P_table, 1),
              "P_total_W": r(P_hover, 0), "I_pack_A": r(I_hover, 1), "T_W": r(TW, 2)},
    "cruise": {"CL": r(CL, 3), "CD0": r(CD0, 4), "CDA_extras_m2": r(cda_sum, 4), "k": r(k, 4), "L_D": r(LD, 1),
               "L_D_max": r(LD_max, 1), "V_best_LD_mps": r(V_md, 1), "drag_N": r(D, 2),
               "P_elec_W": r(P_cruise, 0), "I_pack_A": r(I_cruise, 1)},
    "transition": {"P_peak_W": r(P_trans, 0), "I_peak_A": r(I_trans, 0), "I_all_motors_full_A": I_all_max},
    "battery": {"pack": PACK_NAME, "E_Wh": r(E_pack, 1), "E_usable_Wh": r(E_usable, 1),
                "E_hover_Wh": r(E_hover, 1), "E_transitions_Wh": r(E_trans, 1),
                "cruise_endurance_min": r(cruise_min, 1), "hover_only_endurance_min": r(hover_only_min, 1),
                "meets_threshold_5min": cruise_min >= 5, "meets_objective_10min": cruise_min >= 10},
    "packing": {"centre_section_with_booms_LxWxH_m": centre_pkg, "outer_panel_LxWxH_m_each": panel_pkg,
                "box_m": box, "fits_one_box": fits_box, "longest_piece_m": max(centre_pkg[0], panel_pkg[0]),
                "flight_pack_separate": "LiPo travels in bag/ammo can (D12)"},
    "x8_shell_variant": {"mtow_kg_builder_reported": X8["quadplane_mtow_g"] / 1000, "T_W_class_S": r(x8_tw, 2),
                         "stall_mps": r(x8_vs, 1), "verdict": "fails T/W 1.6 on class-S stations; needs 6S class-M "
                         "stations -> over budget (see CARD.md)", "note": X8["aw_note"]},
}
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sizing.json")
with open(path, "w") as f:
    json.dump(out, f, indent=2)

print(f"MTOW {mtow_g/1000:.2f} kg (gate {mtow_g/1000*1.05:.2f}) | S {S:.3f} m2 AR {AR:.2f} | W/S {WS:.1f} N/m2 | Vs {VS:.1f} m/s")
print(f"Hover: {T_motor/G*1000:.0f} g/motor, DL {DL:.0f} N/m2, MT {P_mt:.0f} W vs table {P_table:.0f} W/motor -> "
      f"{P_hover:.0f} W, {I_hover:.1f} A, T/W {TW:.2f}")
print(f"Cruise {V_CRUISE} m/s: CL {CL:.2f} CD0 {CD0:.4f} L/D {LD:.1f} (max {LD_max:.1f} at {V_md:.1f} m/s) "
      f"-> {P_cruise:.0f} W, {I_cruise:.1f} A")
print(f"Transition peak {P_trans:.0f} W ~{I_trans:.0f} A; all-motors-full {I_all_max} A")
print(f"Energy: {E_pack:.1f} Wh, usable {E_usable:.1f}; hover {E_hover:.1f}, trans {E_trans:.1f} -> cruise "
      f"{cruise_min:.1f} min; hover-only {hover_only_min:.1f} min")
print(f"CG {X_CG:.3f} m, motors at {X_FRONT:.3f}/{X_REAR:.3f}, pusher clearance {clear_x*1000:.0f} mm")
print(f"Pack: centre {centre_pkg}, panels {panel_pkg} x2, one box {box}: {fits_box}")
print(f"X8 variant: T/W {x8_tw:.2f}, Vs {x8_vs:.1f} m/s")
print("groups:", {g: round(v) for g, v in group.items()}, "contingency", round(contingency))
