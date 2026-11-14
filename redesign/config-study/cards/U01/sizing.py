"""U01 wing-assisted quad (tilt-body hybrid) -- first-order sizing.

Run:  python -I sizing.py      (stdlib only; writes sizing.json next to this file)

Concept: bought Holybro X500 V2 carbon X frame (500 mm) + four class-S propulsion stations (same stations as
research/components-cost/cost_model.py) + a removable foam wing fixed at +25 deg incidence on a printed mast above
the rotor plane. Flies in ArduCopter only. In fast forward flight the quad pitches nose-down and the wing carries
part of the weight; the rotors never unload completely (there is no transition).

Mission: REQUIREMENTS.md section 3 default M-A: hover >= 2 min total, cruise >= 5 min threshold / 10 min
objective, 20 % reserve, 0 payload + 0.25 kg growth allowance.

Method: same first-order method intended for every card: mass build-up by group, momentum theory with a figure
of merit for hover, rotor forward-flight power = induced (Glauert) + profile (1 + 4.65 mu^2) + parasite, wing lift
from a lifting-line slope with a stall cap. Every number below is an ASSUMPTION; ESTIMATE = engineering guess,
UNVERIFIED = vendor/forum claim not checked against a primary datasheet.
"""
import json
import math
import os

# ----------------------------------------------------------------------------------------------------------------
# ASSUMPTIONS (all inputs live here)
# ----------------------------------------------------------------------------------------------------------------
RHO = 1.225          # kg/m^3, sea level ISA (RFS is at ~5 m elevation)
G = 9.81

# --- mass build-up, kg ---
MASS = {
    "frame": {
        "Holybro X500 V2 frame kit (plates, 16 mm CF arms, gear)": 0.610,  # Holybro spec via search 2026-11-09, UNVERIFIED
    },
    "propulsion": {
        "4x SunnySky X3108S 900KV": 4 * 0.100,       # ESTIMATE (no datasheet found for 900KV weight)
        "4x LANRC 45A ESC": 4 * 0.040,               # ESTIMATE
        "4x APC 11x4.5MR props": 4 * 0.020,          # ESTIMATE (APC lists ~18-20 g)
        "motor adapter plates (printed/alu) + screws": 0.030,  # ESTIMATE, 16x16 X500 mount vs X3108 pattern UNVERIFIED
    },
    "avionics": {
        "FC CoreWing F405 Wing V2 + GPS + ELRS RX + buzzer": 0.080,   # ESTIMATE
        "Remote ID module (conditional, carried in mass anyway)": 0.015,  # ESTIMATE
    },
    "power_wiring": {
        "PDB/harness, AS150U disconnect, 10 AWG pack lead, UBEC": 0.110,  # ESTIMATE
    },
    "wing": {
        "XPS foam core 1.2 m x 0.22 m, 11 % section, 30 kg/m^3": None,   # computed below
        "packing-tape skin": None,                                         # computed below
        "2x 12 mm CF spar stubs 0.55 m + 14x12 mm sleeve 0.30 m in saddle": 0.065,  # ESTIMATE (~45 g/m, ~55 g/m)
        "printed PETG saddle + 2 masts + clamps": 0.090,  # ESTIMATE
        "nylon bolts, hook-and-loop, glue": 0.020,  # ESTIMATE
    },
    "battery": {
        "4S 6500 mAh LiPo (Ovonic class)": 0.640,  # ESTIMATE (4S 6500 packs listed 0.60-0.70 kg)
    },
    "growth": {
        "growth allowance (REQUIREMENTS M-A)": 0.250,
    },
}

# --- wing geometry ---
SPAN = 1.20            # m, two 0.60 m halves, each with a glued spar stub that plugs into a sleeve in the saddle
CHORD = 0.22           # m, rectangular
T_C = 0.11             # Clark-Y-like; 0.11*0.22 = 24 mm fits 1 in (25.4 mm) XPS sheet
FOAM_DENSITY = 30.0    # kg/m^3, XPS (Owens Corning Foamular 150 ~ 1.3-1.5 lb/ft^3 = 21-24; 30 is conservative) ESTIMATE
SECTION_AREA_FACTOR = 0.68   # airfoil area ~= 0.68 * t * c
TAPE_AREAL = 0.060     # kg/m^2 per layer, clear packing tape ESTIMATE
INCIDENCE_DEG = 25.0   # wing chord vs rotor plane (concept: 20-30 deg)
WING_HEIGHT_ABOVE_ROTOR = 0.07  # m, mast height; keeps the wing out of the contracted slipstream ESTIMATE
CL_ALPHA_2D = 2 * math.pi * 0.9   # per rad, ESTIMATE
ALPHA_L0_DEG = -3.0    # zero-lift angle, cambered section ESTIMATE
CL_MAX = 1.0           # tape-skinned foam, low Re (~2e5) ESTIMATE
OSWALD_E = 0.80
CD0_WING = 0.020       # ESTIMATE (tape skin, no fairing at root)
K_UPWASH = 0.5         # fraction of rotor induced velocity that reduces wing AoA (wing just above disks) ESTIMATE

# --- body / rotor ---
CDA_BODY = 0.025       # m^2, X500-class quad + pack + gear + mast, ESTIMATE (no fairing)
N_ROTORS = 4
PROP_D = 11 * 0.0254   # m, APC 11x4.5MR
FM = 0.65              # hover figure of merit, small fixed-pitch props, ESTIMATE (typ. 0.55-0.70)
K_IND = 1.15           # induced power factor, ESTIMATE
TIP_SPEED_HOVER = 100.0  # m/s, ~6,800 rpm on 11 in, ESTIMATE
ETA_MOTOR_ESC = 0.80   # ESTIMATE
DOWNLOAD_FRAC = 0.03   # hover thrust lost to the wing in the inflow, ESTIMATE (calc: ~0.028 m^2 of wing over
                       # disk edges at ~0.6 v_i, Cd 1.2 -> ~1.5 %; doubled for inflow distortion)
MAX_THRUST_PER_MOTOR_N = 1.5 * G   # ESTIMATE: X3108S 900KV + 11x4.5 on 4S, from Ct=0.11 at ~9,000 rpm
                                   # (=1.9 kgf, ~300 W) derated to 1.5 kgf. No maker table found -> bench test.

# --- battery ---
PACK_V_NOM = 14.8      # 4S
PACK_AH = 6.5
USABLE_FRAC = 0.80     # REQUIREMENTS: 20 % reserve
PACK_C_RATING = 50     # ESTIMATE (label rating; real sustained much lower)

# --- mission (REQUIREMENTS section 3, M-A) ---
HOVER_MIN_REQ = 2.0
CRUISE_MIN_THRESHOLD = 5.0
CRUISE_MIN_OBJECTIVE = 10.0
ANGLE_MAX_DEG = 35.0   # ArduCopter ANGLE_MAX set to 3500 cdeg for this airframe (default 3000) ASSUMPTION

# --- gust check (REQUIREMENTS D11) ---
WIND_STEADY = 5.0
WIND_GUST = 8.0

# --- packing ---
FRAME_PACKED = (0.39, 0.39, 0.27)  # m: X500 plates+arms with props off (500 mm wheelbase -> 354 mm square motor
                                   # pattern + motor bells), gear height 215 mm + top stack. ESTIMATE
BOX_LIMIT = (1.2, 0.5, 0.4)


# ----------------------------------------------------------------------------------------------------------------
# CALCULATIONS
# ----------------------------------------------------------------------------------------------------------------
def wing_masses():
    S = SPAN * CHORD
    foam = SECTION_AREA_FACTOR * T_C * CHORD * CHORD * SPAN * FOAM_DENSITY
    tape = 2.05 * S * TAPE_AREAL  # top + bottom, small overlap
    return S, foam, tape


S_WING, m_foam, m_tape = wing_masses()
MASS["wing"]["XPS foam core 1.2 m x 0.22 m, 11 % section, 30 kg/m^3"] = round(m_foam, 3)
MASS["wing"]["packing-tape skin"] = round(m_tape, 3)

group_mass = {g: round(sum(v.values()), 3) for g, v in MASS.items()}
MTOW = sum(group_mass.values())
W = MTOW * G
AR = SPAN ** 2 / S_WING
CL_ALPHA_3D = CL_ALPHA_2D / (1 + CL_ALPHA_2D / (math.pi * AR))   # Helmbold-type lifting line
DISK_A = N_ROTORS * math.pi * (PROP_D / 2) ** 2
OMEGA_R = TIP_SPEED_HOVER


def wing_coeffs(alpha_deg):
    """Return CL, CD for the wing at alpha (deg). Simple stall cap + flat-plate post-stall drag."""
    a = math.radians(alpha_deg - ALPHA_L0_DEG)
    cl_lin = CL_ALPHA_3D * a
    alpha_stall = math.degrees(CL_MAX / CL_ALPHA_3D) + ALPHA_L0_DEG
    if abs(cl_lin) <= CL_MAX:
        cl = cl_lin
        cd = CD0_WING + cl ** 2 / (math.pi * OSWALD_E * AR)
    else:
        cl = math.copysign(CL_MAX * 0.85, cl_lin)  # post-stall lift drop ESTIMATE
        cd = CD0_WING + 1.2 * math.sin(math.radians(alpha_deg)) ** 2 + cl ** 2 / (math.pi * OSWALD_E * AR)
    return cl, cd, alpha_stall


def rotor_power(T_total, V, theta):
    """Shaft power of the four rotors (W). theta = nose-down pitch (rad). Glauert induced + profile + climb-like
    inflow term (T * V sin theta = propulsive power)."""
    T = T_total / N_ROTORS
    A = DISK_A / N_ROTORS
    vh = math.sqrt(T / (2 * RHO * A))
    Vx = V * math.cos(theta)
    Vz = V * math.sin(theta)            # freestream component through the disk (adds to inflow)
    vi = vh
    for _ in range(200):                 # fixed point on Glauert: vi = T / (2 rho A sqrt(Vx^2 + (Vz+vi)^2))
        vi_new = T / (2 * RHO * A * math.sqrt(Vx ** 2 + (Vz + vi) ** 2))
        vi = 0.5 * vi + 0.5 * vi_new
    P_ideal_hover = T * vh
    P0_hover = P_ideal_hover / FM - K_IND * P_ideal_hover   # profile power at hover implied by FM
    mu = Vx / OMEGA_R
    P_profile = P0_hover * (1 + 4.65 * mu ** 2)
    P = N_ROTORS * (K_IND * T * vi + P_profile + T * Vz)
    return P, vi


def trim(V, with_wing=True):
    """Solve level flight at airspeed V for pitch theta (nose-down) and total thrust T."""
    best = None
    for i in range(0, 801):
        th = math.radians(i * 0.1)        # 0..80 deg
        L = D_w = 0.0
        alpha = None
        # induced velocity first guess for the upwash correction
        _, vi_guess = rotor_power(W, V, th) if V > 0 else (0, 0)
        if with_wing and V > 0.5:
            alpha = INCIDENCE_DEG - math.degrees(th) - math.degrees(math.atan2(K_UPWASH * vi_guess, V))
            cl, cd, _ = wing_coeffs(alpha)
            q = 0.5 * RHO * V ** 2
            L = q * S_WING * cl
            D_w = q * S_WING * cd
        D = 0.5 * RHO * V ** 2 * CDA_BODY + D_w
        # horizontal: T sin th = D ; vertical: T cos th + L = W
        if th == 0:
            if D > 1e-6:
                continue
            T = W - L
            resid = 0
        else:
            T = D / math.sin(th)
            resid = T * math.cos(th) + L - W
        if best is None or abs(resid) < abs(best[0]):
            best = (resid, th, T, L, D, alpha)
    resid, th, T, L, D, alpha = best
    P, vi = rotor_power(T, V, th)
    P_el = P / ETA_MOTOR_ESC
    return dict(V=V, theta_deg=round(math.degrees(th), 1), T_N=round(T, 2), wing_lift_N=round(L, 2),
                wing_lift_frac=round(L / W, 3), drag_N=round(D, 2),
                alpha_wing_deg=None if alpha is None else round(alpha, 1),
                P_elec_W=round(P_el, 1), I_A=round(P_el / PACK_V_NOM, 1), trim_resid_N=round(resid, 2),
                within_angle_max=math.degrees(th) <= ANGLE_MAX_DEG)


# hover
T_hover = W * (1 + DOWNLOAD_FRAC)
disk_loading = T_hover / DISK_A
P_ideal = T_hover ** 1.5 / math.sqrt(2 * RHO * DISK_A)
P_hover_el = P_ideal / FM / ETA_MOTOR_ESC
I_hover = P_hover_el / PACK_V_NOM
E_usable_Wh = PACK_V_NOM * PACK_AH * USABLE_FRAC
t_hover_min = E_usable_Wh / P_hover_el * 60
TW = N_ROTORS * MAX_THRUST_PER_MOTOR_N / W

# speed sweep, with and without wing
sweep = []
for V in [0, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 20, 22]:
    a = trim(V, True)
    b = trim(V, False)
    sweep.append(dict(V=V, wing=a, no_wing=b,
                      current_saving_frac=round(1 - a["I_A"] / b["I_A"], 3) if b["I_A"] > 0 else None))

# cruise point: the speed in 14-20 m/s (M-A band) with minimum electrical power, within ANGLE_MAX
cands = [s for s in sweep if 14 <= s["V"] <= 20 and s["wing"]["within_angle_max"]]
cruise = min(cands, key=lambda s: s["wing"]["P_elec_W"])
P_cruise = cruise["wing"]["P_elec_W"]
t_cruise_min = E_usable_Wh / P_cruise * 60

# mission energy M-A
E_mission_thr = P_hover_el * HOVER_MIN_REQ / 60 + P_cruise * CRUISE_MIN_THRESHOLD / 60
E_mission_obj = P_hover_el * HOVER_MIN_REQ / 60 + P_cruise * CRUISE_MIN_OBJECTIVE / 60
cruise_after_hover_min = (E_usable_Wh - P_hover_el * HOVER_MIN_REQ / 60) / P_cruise * 60

# wing stall speed (wing alone carrying the full weight) -- informative only, U01 never needs it
V_stall_wing_alone = math.sqrt(2 * W / (RHO * S_WING * CL_MAX))

# gust check: hover in a 5 m/s steady headwind, gust to 8 m/s, attitude frozen at the 5 m/s trim
t5 = trim(WIND_STEADY, True)
cl5, cd5, _ = wing_coeffs(t5["alpha_wing_deg"])
cl8, cd8, _ = wing_coeffs(t5["alpha_wing_deg"])  # same AoA (horizontal gust), higher q
dL_gust = 0.5 * RHO * (WIND_GUST ** 2 - WIND_STEADY ** 2) * S_WING * cl8
dD_gust = 0.5 * RHO * (WIND_GUST ** 2 - WIND_STEADY ** 2) * (S_WING * cd8 + CDA_BODY)
dD_gust_no_wing = 0.5 * RHO * (WIND_GUST ** 2 - WIND_STEADY ** 2) * CDA_BODY

# pitch control authority vs wing pitching moment at cruise
ARM_X = 0.25 / math.sqrt(2)          # m, fore/aft lever of each motor on a 500 mm X
T_per_motor_cruise = cruise["wing"]["T_N"] / 4
M_pitch_avail = 2 * (MAX_THRUST_PER_MOTOR_N - T_per_motor_cruise) * ARM_X
CM0 = -0.08                          # Clark-Y-like ESTIMATE
AC_OFFSET = 0.02                     # m, wing AC vs CG placement error ESTIMATE
qc = 0.5 * RHO * cruise["V"] ** 2
M_wing = abs(CM0 * qc * S_WING * CHORD) + AC_OFFSET * cruise["wing"]["wing_lift_N"]

# upper bound for the gust: wing outside the rotor inflow (no upwash correction), AoA = incidence - pitch
alpha_ub = INCIDENCE_DEG - t5["theta_deg"]
cl_ub, cd_ub, _ = wing_coeffs(alpha_ub)
dL_gust_ub = 0.5 * RHO * (WIND_GUST ** 2 - WIND_STEADY ** 2) * S_WING * cl_ub
dD_gust_ub = 0.5 * RHO * (WIND_GUST ** 2 - WIND_STEADY ** 2) * (S_WING * cd_ub + CDA_BODY)

# sensitivity: pessimistic aero/rotor inputs (each ESTIMATE): dirtier wing, draggier body, full inflow on the
# wing, worse props. Answers "does the screen's >= 20 % saving at 12 m/s survive bad assumptions?"
PESSIMISTIC = dict(CD0_WING=0.040, CDA_BODY=0.035, K_UPWASH=1.0, FM=0.55, CL_MAX=0.8)
_saved = {k: globals()[k] for k in PESSIMISTIC}
globals().update(PESSIMISTIC)
pess = {}
for V in (10, 12, 14, 16):
    a, b = trim(V, True), trim(V, False)
    pess[V] = dict(theta_deg=a["theta_deg"], alpha_wing_deg=a["alpha_wing_deg"], I_wing_A=a["I_A"],
                   I_bare_A=b["I_A"], saving=round(1 - a["I_A"] / b["I_A"], 3))
globals().update(_saved)

# packing: frame (props off) in the box, the two wing halves laid flat on top, spar alongside
wing_half = (SPAN / 2, CHORD, T_C * CHORD + 0.006)
box = (max(FRAME_PACKED[0], wing_half[0]) + 0.05,
       max(FRAME_PACKED[1], wing_half[1]) + 0.05,
       FRAME_PACKED[2] + 2 * wing_half[2] + 0.05)
fits_box = all(b <= l for b, l in zip(sorted(box, reverse=True), sorted(BOX_LIMIT, reverse=True)))

out = {
    "concept": "U01 wing-assisted quad (tilt-body hybrid), Holybro X500 V2 + class-S stations + 1.2 m foam wing",
    "status": "CHECKED (calc only; every input ESTIMATE/UNVERIFIED as tagged in sizing.py)",
    "mass_kg": {"groups": group_mass, "MTOW": round(MTOW, 3), "MTOW_without_growth": round(MTOW - 0.25, 3)},
    "wing": {"span_m": SPAN, "chord_m": CHORD, "area_m2": round(S_WING, 4), "AR": round(AR, 2),
             "incidence_deg": INCIDENCE_DEG, "wing_loading_N_m2": round(W / S_WING, 1),
             "wing_loading_g_dm2": round(MTOW * 1000 / (S_WING * 100), 1),
             "stall_speed_wing_alone_m_s": round(V_stall_wing_alone, 1),
             "note": "the wing never carries the full weight; stall speed is informative only"},
    "hover": {"disk_area_m2": round(DISK_A, 4), "disk_loading_N_m2": round(disk_loading, 1),
              "P_elec_W": round(P_hover_el, 1), "I_A": round(I_hover, 1),
              "T_W_max": round(TW, 2), "T_W_gate_1p6": TW >= 1.6,
              "endurance_min_80pct": round(t_hover_min, 1)},
    "cruise": {"V_m_s": cruise["V"], **cruise["wing"], "no_wing_I_A": cruise["no_wing"]["I_A"],
               "current_saving_vs_bare_quad": cruise["current_saving_frac"],
               "endurance_min_80pct": round(t_cruise_min, 1),
               "screen_condition_20pct_at_12_m_s": next(s["current_saving_frac"] for s in sweep if s["V"] == 12)},
    "mission_MA": {"usable_Wh": round(E_usable_Wh, 1),
                   "E_threshold_Wh": round(E_mission_thr, 1), "E_objective_Wh": round(E_mission_obj, 1),
                   "threshold_met": E_mission_thr <= E_usable_Wh, "objective_met": E_mission_obj <= E_usable_Wh,
                   "cruise_min_after_2min_hover": round(cruise_after_hover_min, 1),
                   "pack_C_at_hover": round(I_hover / PACK_AH, 1)},
    "gust_check_hover_5_to_8_m_s": {"trim_at_5": t5, "dLift_N": round(dL_gust, 2),
                                    "dLift_over_W": round(dL_gust / W, 3), "dDrag_N": round(dD_gust, 2),
                                    "dDrag_bare_quad_N": round(dD_gust_no_wing, 2),
                                    "upper_bound_wing_outside_inflow": {"alpha_deg": round(alpha_ub, 1),
                                        "dLift_N": round(dL_gust_ub, 2), "dLift_over_W": round(dL_gust_ub / W, 3),
                                        "dDrag_N": round(dD_gust_ub, 2)},
                                    "note": "headwind only; tail/quartering wind on a 25 deg wing with no yaw "
                                            "weathervane in ArduCopter is worse and not modelled"},
    "pitch_authority": {"M_avail_Nm": round(M_pitch_avail, 2), "M_wing_cruise_Nm": round(M_wing, 2),
                        "fraction_used": round(M_wing / M_pitch_avail, 2)},
    "sensitivity_pessimistic": {"inputs": PESSIMISTIC, "by_speed": pess},
    "packing": {"frame_props_off_m": FRAME_PACKED, "wing_half_m": [round(x, 3) for x in wing_half],
                "box_m": [round(x, 2) for x in box], "fits_1_2x0_5x0_4_box": fits_box,
                "boxes": 1, "longest_piece_m": SPAN / 2, "longest_piece": "wing half with its glued 0.55 m spar stub"},
    "sweep": sweep,
}

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "sizing.json"), "w") as f:
    json.dump(out, f, indent=1)

print(f"MTOW {MTOW:.3f} kg  groups {group_mass}")
print(f"Wing S={S_WING:.3f} m2 AR={AR:.1f} WL={MTOW*1000/(S_WING*100):.1f} g/dm2 Vs(wing alone)={V_stall_wing_alone:.1f}")
print(f"Hover: DL={disk_loading:.0f} N/m2 P={P_hover_el:.0f} W I={I_hover:.1f} A T/W={TW:.2f} t={t_hover_min:.1f} min")
print(f"{'V':>4} {'th':>5} {'aw':>6} {'L/W':>6} {'I_wing':>7} {'I_bare':>7} {'save':>6}")
for s in sweep:
    a, b = s["wing"], s["no_wing"]
    print(f"{s['V']:>4} {a['theta_deg']:>5} {str(a['alpha_wing_deg']):>6} {a['wing_lift_frac']:>6} "
          f"{a['I_A']:>7} {b['I_A']:>7} {str(s['current_saving_frac']):>6}  bare th={b['theta_deg']}")
print(f"Cruise {cruise['V']} m/s: {P_cruise:.0f} W, {t_cruise_min:.1f} min; after 2 min hover {cruise_after_hover_min:.1f} min")
print(f"Gust 5->8 m/s: dL={dL_gust:.1f} N ({dL_gust/W:.0%} W), dD={dD_gust:.1f} N vs bare {dD_gust_no_wing:.1f} N")
print(f"Gust upper bound (wing outside inflow, alpha {alpha_ub:.1f}): dL={dL_gust_ub:.1f} N ({dL_gust_ub/W:.0%} W), dD={dD_gust_ub:.1f} N")
print("Pessimistic:", pess)
print(f"Pitch: wing {M_wing:.2f} Nm of {M_pitch_avail:.2f} Nm available")
print(f"Box {box} fits={fits_box}")
