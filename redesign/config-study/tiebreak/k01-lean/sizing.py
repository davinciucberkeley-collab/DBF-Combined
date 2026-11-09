"""K01-LEAN: twin-boom quadplane 4+1 re-sized as lean as the physics allows (class S, 4S) -- tie-break vs K09.

Run:  python -I sizing.py      (stdlib only; writes sizing.json and cost.csv next to this file)

Adapted from cards/K01/sizing.py (same X3108S thrust table, Cf, form factors, energy rule) with:
  * K09 construction: ONE-PIECE hot-wired XPS wing, one 22x20 CF spar, foam-board/printed pod, 22x20 CF booms
    (one tube SKU for spar + booms + spare), foam-board H-tail, 3 mechanical field joints (was 5);
  * the K01 skeptic's fixes: spar runs through both boom stations (C3), static margin >= 8 % by construction (C4),
    SpeedyBee F405 Wing on a stable target (C6), spare boom (C11), box/cells/jig costed (section 2);
  * the study lead's budget recovery: no Remote ID module (RFS is a FRIA), 2 packs not 3;
  * the K09 skeptic's corrected coefficients as BASELINE, not as a pessimistic afterthought
    (DOWNLOAD 1.06, eta_motor_cruise reduced, +build overrun in the pessimistic case).

Mission = REQUIREMENTS.md section 3 M-A (hover 2 min, cruise >= 5 min, 20 % reserve, no payload, 0.25 kg growth).
ESTIMATE = engineering guess, UNVERIFIED = unchecked claim. Every assumption is in the block below.
"""
import csv
import json
import math
import os

G = 9.81
RHO = 1.225                      # sea level ISA; RFS is ~5 m ASL

# ------------------------------------------------------------------ ASSUMPTIONS
# ---- Wing (one piece; fits the same 1.25 m box class as K09)
SPAN = 1.20                      # m, one piece, no joiner (box internal length 1.22 m)
CHORD = 0.27                     # m, constant chord, hot-wired from 2 in XPS
T_C = 0.12                       # Clark-Y / S-type cambered section: 32 mm thick, room for the 22 mm spar
E_OSWALD = 0.75                  # ESTIMATE (as K01)
CL_MAX = 1.10                    # ESTIMATE (as K01; cambered section, tailed aircraft needs no reflex)
SPAR_LEN = 1.00                  # m, one stock 22x20x1000 tube, centred: spans +/-0.50 m, booms clamp to it at +/-0.30
BOOM_Y = 0.30                    # m, boom offset (11 in prop clears the 0.10 m pod and the 10 in pusher by 3 cm)
SPAR_X = 0.25                    # fraction of chord: spar at 25 % c (thickest point ~30 %)

# ---- Pod (on TOP of the wing so the pusher hub sits high and the legs stay short)
POD = (0.50, 0.10, 0.08)         # m, L x W x H, foam board box + printed nose and pusher mount
POD_X_FRONT = -0.20              # m from wing LE (pod nose)

# ---- Propulsion, lift (SunnySky X3108S KV900, APC 11x4.7 @ 14.8 V, docs/research/budget-lift.md, as K01/K09)
N_LIFT = 4
PROP_D_IN = 11.0
LIFT_TABLE = [(690, 89.0), (750, 104.0), (870, 133.0), (1580, 447.0)]   # (thrust g, input W) per motor
LIFT_MAX_G = 1580.0
PROP_CLEAR = 0.02                # m, gap between a lift disc and the wing LE/TE in plan view (K01 used 0.03 at TE)
ESC_EFF = 0.95                   # ESTIMATE
FM = 0.65                        # ESTIMATE, momentum cross-check only
ETA_MOTOR_HOVER = 0.80           # ESTIMATE, momentum cross-check only
DOWNLOAD = 1.06                  # K09 skeptic value: 22 mm boom runs under each disc (rear disc: full diameter)
AVIONICS_W = 5.0                 # W

# ---- Propulsion, pusher: a 6th X3108S (same SKU as the lift motors, so ONE spare motor covers all 5 stations)
PUSHER_PROP = "APC 10x6E pusher (LP10060EP)"
PUSHER_STATIC_KGF = 1.0          # UNVERIFIED ESTIMATE: X3108S at ~25-28 A on 10x6E; MEASURE ON THE THRUST STAND
PUSHER_FULL_A = 28.0             # ESTIMATE: Cp(10x6E)/Cp(11x4.7) ~1.5 x (10/11)^5 = 0.93 of the 30 A table point
PUSHER_PITCH_SPEED = 900 * 14.8 * 0.85 / 60 * 6 * 0.0254   # m/s at 85 % of no-load rpm = 28.8 m/s

# ---- Tail: H-tail. Flat foam-board stab between the boom ends (ties the booms -> stiffer in twist),
#      one elevator servo, two FIXED vertical fins on the boom ends (no rudder: hover yaw from motors,
#      cruise yaw damping from fins; ArduPilot Plane flies aileron + elevator aircraft without rudder).
STAB_SPAN = 2 * BOOM_Y           # 0.60 m
STAB_CHORD = 0.15                # m
FIN_H, FIN_CHORD = 0.15, 0.15    # m, each fin
ETA_TAIL = 0.90                  # ESTIMATE, dynamic-pressure ratio at the tail
FIN_ENDPLATE = 1.00              # no end-plate credit on the stab lift slope (conservative)

# ---- Static margin model (Etkin/Raymer textbook form; same method as the K01 skeptic, REVIEW C4)
SM_TARGET = 0.15                 # chosen base SM so that the pessimistic case still clears 8 %
D_NP_FUS_BASE = 0.02             # fraction of MAC: pod + booms + parked props/motors ahead of CG (Raymer K_fus, calc below)
D_NP_FUS_PESS = 0.05             # pessimistic: unmodelled parked props, legs, motor cans
DEPS_PESS_ADD = 0.07             # pessimistic: downwash gradient +0.07 (low-AR wing, tail near wing wake)

# ---- Mass build-up, kg
RHO_XPS = 30.0                   # kg/m3, FOAMULAR F-250 (as K01/K09)
TAPE_KG_M2 = 0.065               # ESTIMATE (as K09)
CF_22x20_KG_M = 0.102            # calc rho 1.55 (as K09)
FOAMBOARD_KG_M2 = 0.20           # ESTIMATE (as K09; weigh one sheet)
AIRFOIL_AREA_FACTOR = 0.68
BOOM_LEN = 1.00                  # m, stock tube, no cut
TAIL_SOCKET_OVERHANG = 0.04      # m, printed tail socket sleeves over the boom end; stab TE overhangs the tube by <= 4 cm


def mass_groups(pack_kg):
    S = SPAN * CHORD
    stab_a = STAB_SPAN * STAB_CHORD
    fin_a = 2 * FIN_H * FIN_CHORD
    return {
        "wing core XPS one piece (calc from geometry, ailerons cut from the core)":
            AIRFOIL_AREA_FACTOR * CHORD * (T_C * CHORD) * SPAN * RHO_XPS,
        "wing skin, packing tape 2 sides": 2 * S * TAPE_KG_M2,
        "spar CF 22x20x1000 (102 g/m calc)": SPAR_LEN * CF_22x20_KG_M,
        "2 booms CF 22x20x1000 (same SKU as spar)": 2 * BOOM_LEN * CF_22x20_KG_M,
        "pod: foam-board box + printed nose, pack tray, pusher mount (ESTIMATE)": 0.10,
        "printed PETG: 4 motor mounts 18 g, 2 boom-spar saddles 25 g, 4 legs 12 g, 2 tail sockets 10 g (ESTIMATE)":
            4 * 0.018 + 2 * 0.025 + 4 * 0.012 + 2 * 0.010,
        "H-tail: foam-board stab + 2 fins + 2 mm CF rod stiffener + hinge tape (calc + ESTIMATE)":
            (stab_a + fin_a) * FOAMBOARD_KG_M2 + 0.012,
        "servos: 2 x EMAX ES08MA II 12 g (ailerons) + 1 x ES3005HV 43 g (elevator) + linkages": 2 * 0.012 + 0.043 + 0.012,
        "4 lift stations: X3108S 81 g (SunnySky) + LANRC 45A 6.6 g + APC 11x4.5MR ~20 g": 4 * (0.081 + 0.0066 + 0.020),
        "pusher station: X3108S 81 g + LANRC 45A 6.6 g + APC 10x6E ~20 g": 0.081 + 0.0066 + 0.020,
        "motor/ESC/servo wiring along 2 booms + pusher, 2 boom connectors (ESTIMATE)": 0.08,
        "battery 4S pack (see PACKS)": pack_kg,
        "avionics: SpeedyBee F405 Wing, M100 GPS, RP3 RX, MS5525 airspeed + pitot, AS150U, 12 AWG harness (ESTIMATE)": 0.15,
        "glue, Velcro straps, cable ties, labels (ESTIMATE)": 0.07,
    }


GROWTH = 0.25                    # kg, REQUIREMENTS section 3 (kept although the target is lean)
PESS_EXTRA = {                   # pessimistic additions (see CARD.md "Own skeptic")
    "build overrun (K09 skeptic +0.10)": 0.10,
    "boom-spar saddle reinforcement + heavier prints (+0.06)": 0.06,
    "pack weighs 420 g not 386 g (+0.034)": 0.034,
}

# ---- Cruise aerodynamics (as K01 unless stated)
V_CRUISE = 15.0                  # m/s, >= 1.3 Vs
CF_WING, FF_WING = 0.0060, 1.25
CF_BODY = 0.0070
CDA_PARKED_PROP = 0.0034 * (PROP_D_IN / 17.0) ** 2   # K01 rule: C0 17 in parked-prop CdA scaled by D^2
CDA_MOTOR_BODY = 0.0004          # m2 per stopped motor + mount (as K01)
LEG_LEN, LEG_T = 0.13, 0.012     # m, printed blade legs; CdA = L t 0.3 (streamlined blade, ESTIMATE)
INTERFERENCE = 1.15              # base (K01); pessimistic 1.35 (K01 skeptic)
ETA_PROP_CRUISE = 0.60           # base, 10x6E at J ~0.45 (APC E-series peak ~0.65-0.7, ESTIMATE)
ETA_MOTOR_CRUISE = 0.76          # base: X3108S at ~120-150 W input, no-load loss ~12 W (K09 skeptic logic)
PESS = dict(eta_prop=0.50, eta_motor=0.70, interference=1.35, parked_prop_factor=1.5)

# ---- Energy
V_NOM_CELL = 3.7
RESERVE = 0.20
TRANSITION_WH = 3.0              # ESTIMATE (as K01)
HOVER_MIN = 2.0
# Low-voltage hover T/W: loaded cell voltage at the 20 % reserve point and thrust ~ V^n at full throttle
V_LOW_CELL_BASE, N_V_BASE = 3.50, 1.5    # ESTIMATE: 40C pack at ~6C hover, end of usable energy
V_LOW_CELL_PESS, N_V_PESS = 3.40, 2.0    # pessimistic: tired pack, thrust ~ rpm^2 ~ V^2

PACKS = [
    dict(name="Admiral 4S 4000 40C XT60", ah=4.0, kg=0.386, usd_2pack=107.00,
         src="Motion RC EPR40004X6 / ADM6024-002 2-pack $107.00 (motionrc.com; $102.49-107.00 seen 2026-11-09); 386 g per K09 card"),
    dict(name="Admiral 4S 5000 40C XT60", ah=5.0, kg=0.50, usd_2pack=None,
         src="Motion RC EPR50004X6 listed (motionrc.eu); mass ESTIMATE 0.50 kg; price not checked -- variant only"),
]

# ---- Hover in wind: side area seen by a horizontal wind with the wing level (quadplane hovers flat)
SIDE_AREA_FRONT = SPAN * T_C * CHORD + POD[1] * POD[2] + 4 * 0.03 * 0.04 + STAB_SPAN * 0.005
SIDE_AREA_SIDE = POD[0] * POD[2] + 2 * BOOM_LEN * 0.022 + 2 * FIN_H * FIN_CHORD + CHORD * T_C * CHORD
CD_PLATE = 1.28
GUSTS = (5.0, 8.0)

# ---- Structure checks
CF_SIGMA_ALLOW = 300e6           # Pa, roll-wrapped CF tube bending allowable, ESTIMATE (UNVERIFIED; real ~500-600 MPa)
XPS_SIGMA_ALLOW = 0.30e6         # Pa, building-grade XPS flexural strength, order of magnitude (K01 REVIEW C3)
N_LOAD = 3.0                     # cruise manoeuvre/gust load factor
N_HOVER = 2.5                    # hover/landing dynamic factor on boom reactions
# ---------------------------------------------------------------- END ASSUMPTIONS


def interp_power(thrust_g):
    t = LIFT_TABLE
    if thrust_g <= t[0][0]:
        return t[0][1] * thrust_g / t[0][0]   # linear through zero below the table (conservative, K09 skeptic)
    for (g0, w0), (g1, w1) in zip(t, t[1:]):
        if thrust_g <= g1:
            return w0 + (w1 - w0) * (thrust_g - g0) / (g1 - g0)
    return t[-1][1]


def helmbold(ar):
    return 2 * math.pi * ar / (2 + math.sqrt(ar ** 2 + 4))


def geometry():
    """Place CG for the target static margin, put the lift centroid ON the CG, then place the tail behind the rear
    prop disc. Iterate because the tail arm depends on the motor positions."""
    S = SPAN * CHORD
    AR = SPAN ** 2 / S
    a_w = helmbold(AR)
    S_t = STAB_SPAN * STAB_CHORD
    a_t = helmbold(STAB_SPAN ** 2 / S_t) * FIN_ENDPLATE
    r = PROP_D_IN * 0.0254 / 2
    x_ac = 0.25 * CHORD
    cg = 0.25 * CHORD
    for _ in range(50):
        d = max(cg + r + PROP_CLEAR, (CHORD + r + PROP_CLEAR) - cg)   # half-distance between front and rear motor
        x_f, x_r = cg - d, cg + d
        tail_le = x_r + r + PROP_CLEAR
        x_t_ac = tail_le + 0.25 * STAB_CHORD
        l_t = x_t_ac - x_ac
        Vh = S_t * l_t / (S * CHORD)
        deps = 2 * a_w / (math.pi * AR)
        hn = 0.25 + ETA_TAIL * Vh * (a_t / a_w) * (1 - deps) - D_NP_FUS_BASE
        cg_new = (hn - SM_TARGET) * CHORD
        if abs(cg_new - cg) < 1e-6:
            break
        cg = cg_new
    hn_pess = 0.25 + ETA_TAIL * Vh * (a_t / a_w) * (1 - deps - DEPS_PESS_ADD) - D_NP_FUS_PESS
    boom_front = x_f - 0.02
    boom_rear_needed = tail_le + STAB_CHORD
    boom_rear = boom_front + BOOM_LEN
    fin_area = 2 * FIN_H * FIN_CHORD
    Vv = fin_area * l_t / (S * SPAN)
    # Raymer fuselage term, shown for checking D_NP_FUS_BASE (K_fus ~0.01 /deg, wing at ~40 % pod length)
    k_fus = 0.01
    dcm_pod = k_fus * POD[1] ** 2 * POD[0] / (CHORD * S) * 180 / math.pi
    dcm_booms = 2 * k_fus * 0.022 ** 2 * BOOM_LEN / (CHORD * S) * 180 / math.pi
    return dict(
        S=S, AR=AR, a_w_per_rad=round(a_w, 3), a_t_per_rad=round(a_t, 3), deps_dalpha=round(deps, 3),
        x_front_motor_m=round(x_f, 3), x_rear_motor_m=round(x_r, 3), motor_half_spacing_m=round(d, 3),
        lift_centroid_x_m=round((x_f + x_r) / 2, 3), cg_x_m=round(cg, 3), cg_pct_mac=round(100 * cg / CHORD, 1),
        neutral_point_pct_mac_base=round(100 * hn, 1), neutral_point_pct_mac_pess=round(100 * hn_pess, 1),
        static_margin_pct_base=round(100 * (hn - cg / CHORD), 1),
        static_margin_pct_pess=round(100 * (hn_pess - cg / CHORD), 1),
        tail_le_x_m=round(tail_le, 3), tail_arm_m=round(l_t, 3), Vh=round(Vh, 3), Vv=round(Vv, 4),
        stab_area_m2=round(S_t, 3), fin_area_m2=round(fin_area, 3),
        boom_front_x_m=round(boom_front, 3), boom_rear_x_m=round(boom_rear, 3),
        boom_rear_needed_x_m=round(boom_rear_needed, 3), boom_long_enough=boom_rear + TAIL_SOCKET_OVERHANG >= boom_rear_needed,
        tail_overhang_past_tube_m=round(max(0.0, boom_rear_needed - boom_rear), 3),
        raymer_fus_dNP_check_pct_mac=round(100 * (dcm_pod + dcm_booms) / a_w, 2),
    )


def structure(mtow, geo):
    W = mtow * G
    D, d = 0.022, 0.020
    I = math.pi / 64 * (D ** 4 - d ** 4)
    Z = I / (D / 2)
    # cruise: elliptic-ish lift, half-span lift acts at 4/(3 pi) * b/2 from centreline; boom+motor relief ignored (conservative)
    M_root_cruise = N_LOAD * W / 2 * (4 / (3 * math.pi)) * SPAN / 2
    # hover: each boom pushes up half the weight at y = BOOM_Y; centre (pod+pack) hangs; conservative: all weight at centre
    M_root_hover = N_HOVER * (W * DOWNLOAD / 2) * BOOM_Y
    # foam outboard of the spar end (y > 0.50): uniform lift over the last (b/2 - 0.50) m
    tip = SPAN / 2 - SPAR_LEN / 2
    w_per_m = N_LOAD * W / SPAN
    M_tip = w_per_m * tip ** 2 / 2
    t = T_C * CHORD
    Z_foam = 0.1 * CHORD * t ** 2
    # boom: front motor cantilever from saddle, motor thrust at max x hover factor
    arm = abs(geo["x_front_motor_m"] - SPAR_X * CHORD)
    M_boom = N_HOVER * LIFT_MAX_G / 1000 * G * arm
    return dict(
        spar_Z_m3=f"{Z:.3e}",
        spar_root_stress_cruise_MPa=round(M_root_cruise / Z / 1e6, 1),
        spar_root_stress_hover_MPa=round(M_root_hover / Z / 1e6, 1),
        spar_allowable_MPa_ESTIMATE=CF_SIGMA_ALLOW / 1e6,
        spar_covers_boom_stations=SPAR_LEN / 2 > BOOM_Y + 0.05,
        foam_tip_outboard_of_spar_m=round(tip, 3),
        foam_stress_at_spar_end_kPa=round(M_tip / Z_foam / 1e3, 1),
        foam_allowable_kPa_order=XPS_SIGMA_ALLOW / 1e3,
        boom_cantilever_m=round(arm, 3), boom_stress_at_max_thrust_x2p5_MPa=round(M_boom / Z / 1e6, 1),
    )


def size(pack, dm=0.0, download=DOWNLOAD, eta_prop=ETA_PROP_CRUISE, eta_motor=ETA_MOTOR_CRUISE,
         interference=INTERFERENCE, parked_prop_factor=1.0, v_low=(V_LOW_CELL_BASE, N_V_BASE), label="baseline",
         extra=None):
    geo = geometry()
    groups = mass_groups(pack["kg"])
    if extra:
        groups.update(extra)
    mtow = sum(groups.values()) + GROWTH + dm
    W = mtow * G
    S, AR = geo["S"], geo["AR"]
    WS = W / S
    Vs = math.sqrt(2 * WS / (RHO * CL_MAX))

    # hover
    T_motor_g = mtow * 1000 * download / N_LIFT
    P_motor = interp_power(T_motor_g)
    P_hover = N_LIFT * P_motor / ESC_EFF + AVIONICS_W
    V_pack = 4 * V_NOM_CELL
    I_hover = P_hover / V_pack
    disk = N_LIFT * math.pi * (PROP_D_IN * 0.0254 / 2) ** 2
    P_ideal = (W * download) ** 1.5 / math.sqrt(2 * RHO * disk)
    P_hover_mom = P_ideal / (FM * ETA_MOTOR_HOVER * ESC_EFF) + AVIONICS_W
    TW = N_LIFT * LIFT_MAX_G / (mtow * 1000)
    TW_eff = TW / download
    v_cell, n = v_low
    TW_low = TW * (v_cell / V_NOM_CELL) ** n
    TW_low_eff = TW_low / download
    # hover in wind
    tilt = {}
    for v in GUSTS:
        Ff = 0.5 * RHO * v ** 2 * SIDE_AREA_FRONT * CD_PLATE
        Fs = 0.5 * RHO * v ** 2 * SIDE_AREA_SIDE * CD_PLATE
        tilt[f"{v:.0f}mps"] = dict(nose_into_wind_deg=round(math.degrees(math.atan(Ff / W)), 1),
                                   broadside_deg=round(math.degrees(math.atan(Fs / W)), 1))

    # cruise drag build-up on S
    stab_a = STAB_SPAN * STAB_CHORD
    fin_a = 2 * FIN_H * FIN_CHORD
    parts = dict(
        wing=CF_WING * FF_WING * 2.04,
        pod=CF_BODY * 1.3 * 2 * (POD[0] * POD[1] + POD[0] * POD[2] + POD[1] * POD[2]) / S,
        booms=CF_BODY * 1.1 * 2 * BOOM_LEN * math.pi * 0.022 / S,
        tail=CF_BODY * 1.2 * 2.04 * (stab_a + fin_a) / S,
        parked_props=N_LIFT * CDA_PARKED_PROP * parked_prop_factor / S,
        stopped_motors=N_LIFT * CDA_MOTOR_BODY / S,
        legs=4 * LEG_LEN * LEG_T * 0.3 / S,
    )
    CD0 = sum(parts.values()) * interference
    k = 1 / (math.pi * AR * E_OSWALD)

    def cruise(V):
        CL = 2 * W / (RHO * V ** 2 * S)
        CD = CD0 + k * CL ** 2
        Dr = 0.5 * RHO * V ** 2 * S * CD
        P = Dr * V / (eta_prop * eta_motor) + AVIONICS_W
        return CL, CD, CL / CD, Dr, P

    V_c = max(V_CRUISE, math.ceil(1.3 * Vs * 2) / 2)
    CL_c, CD_c, LD_c, D_c, P_c = cruise(V_c)
    sweep = [dict(V=v / 10, LD=round(cruise(v / 10)[2], 2), P_W=round(cruise(v / 10)[4], 1)) for v in range(120, 221, 10)]

    E_pack = 4 * V_NOM_CELL * pack["ah"]
    E_use = E_pack * (1 - RESERVE)
    E_hover = P_hover * HOVER_MIN / 60
    E_cr = E_use - E_hover - TRANSITION_WH
    cruise_min = E_cr / P_c * 60
    hover_only = E_use / P_hover * 60
    I_peak = I_hover + PUSHER_FULL_A
    return dict(
        label=label, pack=pack["name"], mtow_kg=round(mtow, 3),
        mass_groups_kg={kk: round(v, 3) for kk, v in groups.items()}, growth_kg=GROWTH,
        span_m=SPAN, chord_m=CHORD, wing_area_m2=round(S, 3), AR=round(AR, 2),
        wing_loading_kg_m2=round(WS / G, 2), stall_mps=round(Vs, 2), transition_min_mps_1p3Vs=round(1.3 * Vs, 2),
        cruise_mps=V_c, download=download,
        thrust_per_motor_hover_g=round(T_motor_g, 0), hover_frac_of_max_thrust=round(T_motor_g / LIFT_MAX_G, 2),
        hover_power_W_table=round(P_hover, 0), hover_power_W_momentum_FM=round(P_hover_mom, 0),
        hover_current_A=round(I_hover, 1), hover_C_rate=round(I_hover / pack["ah"], 1),
        TW_table_full_voltage=round(TW, 2), TW_full_voltage_net_of_download=round(TW_eff, 2),
        TW_low_voltage=round(TW_low, 2), TW_low_voltage_net_of_download=round(TW_low_eff, 2),
        low_voltage_rule=f"{v_cell} V/cell loaded, thrust ~ V^{n}",
        hover_wind_lean_deg=tilt,
        CD0=round(CD0, 4), CD0_parts={kk: round(v * interference, 4) for kk, v in parts.items()},
        parked_prop_share_of_CD0=round(parts["parked_props"] / sum(parts.values()), 2),
        CL_cruise=round(CL_c, 3), LD_cruise=round(LD_c, 2), drag_N=round(D_c, 2),
        cruise_power_W=round(P_c, 0), cruise_current_A=round(P_c / V_pack, 1),
        pusher_static_TW=round(PUSHER_STATIC_KGF / mtow, 2), pusher_thrust_vs_cruise_drag=round(PUSHER_STATIC_KGF * G / D_c, 2),
        pack_Wh=round(E_pack, 1), usable_Wh=round(E_use, 1), hover_Wh_2min=round(E_hover, 1),
        cruise_min_after_2min_hover=round(cruise_min, 1), hover_only_endurance_min=round(hover_only, 1),
        peak_transition_current_A=round(I_peak, 0), connector_need_A_1p25x=round(1.25 * I_peak, 0),
        speed_sweep=sweep,
    )


def packing(geo):
    boom_h = 0.04 + LEG_LEN + 0.03          # motor can + leg below + mount
    pieces = {
        "wing + pod + pusher motor (one piece, prop off)": (SPAN, CHORD - POD_X_FRONT, T_C * CHORD + POD[2]),
        "boom L with 2 motors, 2 ESCs, 2 legs (props off)": (BOOM_LEN, 0.06, boom_h),
        "boom R with 2 motors, 2 ESCs, 2 legs (props off)": (BOOM_LEN, 0.06, boom_h),
        "H-tail (stab + 2 fins, one piece)": (STAB_SPAN, STAB_CHORD, FIN_H + 0.01),
        "props 4 x 11 in + 1 x 10 in in a tray": (0.30, 0.30, 0.05),
    }
    # layer 1: wing+pod flat (0.47 deep, 0.112 tall). Layer 2 on a foam shelf: 2 booms + tail + prop tray side by side.
    l1_h = T_C * CHORD + POD[2]
    l2_w = 0.06 + 0.06 + STAB_CHORD + 0.30 - 0.15   # tail and prop tray share the length
    l2_h = max(boom_h, FIN_H + 0.01)
    internal = (SPAN + 0.02, max(CHORD - POD_X_FRONT, l2_w) + 0.02, l1_h + l2_h + 0.03)
    external = tuple(round(x + 0.03, 2) for x in internal)
    return dict(
        pieces_m={k: [round(x, 3) for x in v] for k, v in pieces.items()},
        box_internal_m=[round(x, 2) for x in internal], box_external_m=list(external),
        box_loaded_kg_ESTIMATE=5.0, pieces=4, longest_piece_m=SPAN,
        mechanical_field_joints=3,
        joints="2 boom clamps (2 thumbscrews each into the spar saddle) + H-tail onto both boom ends (1 pin each)",
        plugs="2 boom power (XT60: 2 x 30 A full-throttle burst per boom) + 2 boom signal (4-pin: 2 DShot + GND, elevator lead runs along the R boom) + pack",
        assembly_min_ESTIMATE=7, people="1 (2 easier)",
        vs_K01_card="K01: 5 joints + 6 plugs, 1.2 x 0.5 x 0.4 m box, ~7 kg; K09: 0 joints, 1.25 x 0.55 x 0.45 m, ~6 kg",
    )


# ------------------------------------------------------------------ COST
TAX = 0.1025
BUDGET = 2000.00
SHIPPING = 120.00                # class S ESTIMATE (cost_model.py SHIPPING["S"]); vendors: SunnySky, Amazon, APC/BuddyRC,
                                 # Motion RC, RDQ, WREKD, EMAX, RadioMaster, Holybro, GetFPV, Home Depot (pickup)
FAA_REG = 5.00                   # not taxed
# (group, item, qty, unit USD pre-tax, vendor / source URL, date seen, note)
BOM = [
    ("propulsion", "SunnySky X3108S KV900 motor (4 lift + 1 pusher + 1 spare: one SKU)", 6, 24.99,
     "SunnySky USA https://sunnyskyusa.com/collections/multirotor-motors/products/sunnysky-x3108s-motors (via docs/research/budget-lift.md)",
     "2026-11-01", ""),
    ("propulsion", "LANRC BLHeli_S 45A ESC 4-pack (5 used + 3 spare)", 2, 30.00,
     "Amazon https://www.amazon.com/dp/B0D2HS4Y4J (docs/research/bom-savings.md)", "2026-11-01", ""),
    ("propulsion", "APC 11x4.5MR / MRP lift props (4 fitted + 8 spare, CW/CCW)", 12, 3.83,
     "APC https://www.apcprop.com/product/11x4-5mr/", "2026-11-01", ""),
    ("propulsion", "APC LPAR06E-type adapter rings", 12, 0.50, "APC (price ESTIMATE, as K09)", "2026-11-09", "ESTIMATE"),
    ("propulsion", "APC 10x6E pusher prop LP10060EP (1 + 2 spare)", 3, 3.47,
     "BuddyRC https://buddyrc.com/products/copy-of-apc-10x4-7-slow-flyer-pusher-propeller", "2026-11-09",
     "search snippet; 10x6E tractor $3.64 at reach.dog as fallback"),
    ("servos", "EMAX ES08MA II 12 g metal-gear servo (2 ailerons + 1 spare)", 3, 13.49,
     "WREKD https://wrekd.com/products/emax-es08ma-ii-12g-analog-metal-gear-servo", "2026-11-09",
     "search snippet; Amain $8.99 backorder"),
    ("servos", "EMAX ES3005HV 8 kg.cm servo (elevator: pusher wash, needs torque)", 1, 19.99,
     "EMAX USA https://shop.emax-usa.com/products/es3005hv-high-voltage-servo", "2026-11-01", "as K01"),
    ("battery", "Admiral 4S 4000 40C XT60 LiPo, 2-pack (2 packs total)", 1, 107.00,
     "Motion RC https://www.motionrc.com/products/admiral-4000mah-4s-14-8v-40c-lipo-battery-with-xt60-connector-multi-pack-2-batteries-adm6024-002",
     "2026-11-09", "cached pages show $102.49-$107.00; higher used"),
    ("avionics", "SpeedyBee F405 Wing APP flight controller (stable ArduPilot target SpeedyBeeF405WING: CHECK)", 1, 47.99,
     "RaceDayQuads https://www.racedayquads.com/products/speedybee-f405-wing-app-fixed-wing-flight-controller",
     "2026-11-09", "search snippet; stock UNVERIFIED (NewBeeDrone $51.99 sold out)"),
    ("avionics", "HGLRC M100-5883 GPS + compass", 1, 20.49,
     "RaceDayQuads https://www.racedayquads.com/products/hglrc-m100-5883-gps-module-10th-gen", "2026-11-01", ""),
    ("avionics", "Holybro MS5525 airspeed sensor + pitot (speed-scheduled transition)", 1, 59.99,
     "Holybro (cost_model.py AIRSPEED)", "2026-11-09", "kept: the documented QuadPlane path uses it"),
    ("avionics", "RadioMaster Pocket Crush ELRS transmitter", 1, 64.99,
     "RadioMaster https://www.radiomasterrc.com/products/pocket-crush-radio-controller", "2026-11-01", ""),
    ("avionics", "18650 cells 2-pack for the Pocket (not included)", 1, 24.49,
     "GetFPV Lumenier 18650 2-pack (K09 REVIEW section 6)", "2026-11-09", ""),
    ("avionics", "RadioMaster RP3 V2 ELRS receiver", 1, 19.99,
     "RadioMaster https://www.radiomasterrc.com/products/rp3-expresslrs-2-4ghz-nano-receiver", "2026-11-01", ""),
    ("airframe", "FOAMULAR XPS 2 in x 4 x 8 ft (wing cores: ~5 one-piece cores per sheet)", 1, 59.97,
     "Home Depot / Lowe's (docs/research/budget-airframe.md)", "2026-11-01", "local pickup"),
    ("airframe", "Foam board 20x30 in 10-pack (pod, H-tail, fins, test panels)", 1, 35.92,
     "Amazon B074QZMLQF (budget-airframe.md)", "2026-10", ""),
    ("airframe", "CF tube 22x20x1000 matte (spar + 2 booms + 1 spare: one SKU)", 4, 28.32,
     "Amazon https://www.amazon.com/s?k=carbon+fiber+tube+22mm+1000mm (budget-airframe.md)", "2026-11-01",
     "overseas lead time ~2 weeks: order first"),
    ("airframe", "PETG filament 1 kg (Ambrosia)", 2, 20.99, "West3D (docs/research/airframe-materials.md)", "2026-10", ""),
    ("airframe", "Scotch Heavy Duty packing tape 6 rolls", 1, 19.98, "Amazon B000087KUA (budget-airframe.md)", "2026-10", ""),
    ("airframe", "Foam-safe glue (UHU Por / Gorilla clear)", 1, 12.99, "cost_model.py AIRFRAME", "2026-11", "ESTIMATE vendor"),
    ("hardware", "Wiring + hardware kit (AS150U, 12/16 AWG, XT60 pairs x2, bullets, screws, inserts, horns, pushrods, hinge tape, UBEC, epoxy)",
     1, 124.01, "cost_model.py HARDWARE_MIN (bom-savings.md)", "2026-11-01", "shared floor, unchanged"),
    ("hardware", "Re-terminate 2 packs + charge lead XT60 -> AS150U", 1, 15.00, "K09 REVIEW section 6", "2026-11-09", "ESTIMATE"),
    ("ground", "HTRC C150 charger 150 W AC", 1, 56.99, "Amazon (budget-energy-test.md)", "2026-11-01", ""),
    ("ground", "LiPo bag (Pyrodrone)", 2, 9.99, "Pyrodrone (cost_model.py)", "2026-11-01", ""),
    ("ground", "Ammo can (Harbor Freight 63750)", 1, 19.99,
     "Harbor Freight https://www.harborfreight.com/50-caliber-metal-ammo-can-63750.html", "2026-11-01", ""),
    ("ground", "Watt meter 150 A", 1, 12.99, "Amazon B0F13JWDFV (budget-energy-test.md)", "2026-11-01", ""),
    ("ground", "IR thermometer", 1, 8.98, "Amazon B0BN317X6Z (budget-energy-test.md)", "2026-11-01", ""),
    ("ground", "Thrust stand: 20 kg load cell + HX711 + Nano", 1, 17.97, "Amazon (budget-energy-test.md)", "2026-11-01", ""),
    ("ground", "Pinecil V2 soldering iron", 1, 25.99, "Pine64 (cost_model.py)", "2026-11-01", ""),
    ("ground", "USB-C PD supply for iron", 1, 20.00, "ESTIMATE", "2026-11-09", "ESTIMATE"),
    ("ground", "Multimeter", 1, 25.00, "ESTIMATE", "2026-11-09", "ESTIMATE"),
    ("ground", "Solder, flux, wick", 1, 15.00, "ESTIMATE", "2026-11-09", "ESTIMATE"),
    ("ground", "Hot-wire: NICE-POWER 30 V 10 A supply + Ni80 24 AWG", 1, 41.73,
     "Amazon B0CRSS744F + B0CP9V3DBX (bom-savings.md)", "2026-11-01", ""),
    ("ground", "Hot-wire bow/jig + airfoil template stock", 1, 15.00, "K01 REVIEW section 2", "2026-11-09", "ESTIMATE"),
    ("ground", "Smoke stopper / fused first-power lead", 1, 10.00, "K01 REVIEW section 2", "2026-11-09", "ESTIMATE"),
    ("ground", "Transport box 1.25 x 0.52 x 0.37 m external (1/4 in ply + foam cradles)", 1, 55.00,
     "K09 REVIEW section 6 ($60 for a taller box)", "2026-11-09", "ESTIMATE"),
]


def crash_costs():
    """Two crash definitions: the study's class-S formula (cost_model.py) and this aircraft's own bill."""
    study = 2 * (24.99 + 7.50 + 3.83) + 4 * 3.83 + 4.50 + 67.26 + 20.49 + 100.00
    # K01-lean: 2 lift stations + 4 lift props + pusher prop + FC + GPS + airframe rebuild
    # (XPS core from the sheet already bought ~$0, 1 CF tube $28.32, foam board/tape/glue/PETG ~$15)
    own = 2 * (24.99 + 7.50 + 3.83) + 4 * 3.83 + 3.47 + 47.99 + 20.49 + 28.32 + 15.00
    return dict(study_formula_pretax=round(study, 2), study_formula_incl_tax=round(study * (1 + TAX), 2),
                k01_card_quoted=266.00,
                own_bill_pretax=round(own, 2), own_bill_incl_tax=round(own * (1 + TAX), 2),
                note="own bill assumes the spares already in the BOM are used first (1 motor, 3 ESC, 8 props, 1 tube, 1 servo)")


def cost():
    rows, goods = [], 0.0
    for g, item, q, u, src, date, note in BOM:
        ext = q * u
        goods += ext
        rows.append([g, item, q, f"{u:.2f}", f"{ext:.2f}", src, date, note])
    tax = goods * TAX
    total = goods + tax + SHIPPING + FAA_REG
    reserve = BUDGET - total
    cr = crash_costs()
    rows += [
        ["subtotal", "Goods pre-tax", "", "", f"{goods:.2f}", "", "", ""],
        ["tax", "Sales tax 10.25 % (Berkeley, CDTFA 2026-10-01)", "", "", f"{tax:.2f}", "cost_model.py TAX", "",
         "a 0.5 % Berkeley increase was on the 2026-11-03 ballot: +~$7 if it applies (K01 REVIEW)"],
        ["shipping", "Shipping, all vendors (class S)", "", "", f"{SHIPPING:.2f}", "cost_model.py SHIPPING['S']", "", "ESTIMATE"],
        ["fee", "FAA registration (not taxed)", "", "", f"{FAA_REG:.2f}", "faa.gov DroneZone", "", ""],
        ["TOTAL", "Spend at order time (tax + shipping + FAA included)", "", "", f"{total:.2f}", "", "", ""],
        ["reserve", "Reserve left of $2,000", "", "", f"{reserve:.2f}", "", "",
         f"vs one bad crash: study formula ${cr['study_formula_incl_tax']:.2f} incl. tax; K01 card $266; "
         f"this aircraft's own bill ${cr['own_bill_incl_tax']:.2f}"],
        ["dropped", "NewBeeDrone BeeID Remote ID module (RFS is a FRIA)", "", "", "0.00", "README section 1", "", "saves $44.09 incl. tax"],
        ["dropped", "Third flight pack", "", "", "0.00", "README section 4.2", "", "2 packs only"],
        ["option", "Admiral 4S 5000 2-pack instead of 4000 (variant in sizing.json)", "", "", "~+30 ESTIMATE", "motionrc.eu listing", "",
         "price not checked"],
    ]
    return rows, dict(goods=round(goods, 2), tax=round(tax, 2), shipping=SHIPPING, faa=FAA_REG, total=round(total, 2),
                      reserve=round(reserve, 2), crash=cr,
                      reserve_minus_study_crash=round(reserve - cr["study_formula_incl_tax"], 2),
                      reserve_minus_k01_crash=round(reserve - 266.00, 2),
                      passes_G1_1850=total <= 1850.0)


def main():
    p4, p5 = PACKS
    geo = geometry()
    base = size(p4)
    pess = size(p4, extra=PESS_EXTRA, download=1.10, eta_prop=PESS["eta_prop"], eta_motor=PESS["eta_motor"],
                interference=PESS["interference"], parked_prop_factor=PESS["parked_prop_factor"],
                v_low=(V_LOW_CELL_PESS, N_V_PESS), label="PESSIMISTIC (own skeptic): +0.19 kg, download 1.10, "
                "eta_prop 0.50, eta_motor 0.70, interference 1.35, parked props x1.5, 3.4 V/cell, thrust ~V^2")
    variants = [
        base, pess,
        size(p5, label="4S 5000 pack (more endurance, less T/W)"),
        size(p5, extra=PESS_EXTRA, download=1.10, eta_prop=PESS["eta_prop"], eta_motor=PESS["eta_motor"],
             interference=PESS["interference"], parked_prop_factor=PESS["parked_prop_factor"],
             v_low=(V_LOW_CELL_PESS, N_V_PESS), label="4S 5000 pack, pessimistic"),
        size(p4, dm=0.30, label="sensitivity: +0.30 kg on baseline"),
        size(p4, dm=-GROWTH, label="as-built if growth allowance is not used"),
    ]
    rows, c = cost()
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "cost.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "item", "qty", "unit_usd_pretax", "ext_usd", "vendor_source", "date_seen", "note"])
        w.writerows(rows)
    keys = ("label", "pack", "mtow_kg", "TW_table_full_voltage", "TW_low_voltage", "TW_low_voltage_net_of_download",
            "hover_current_A", "stall_mps", "LD_cruise", "cruise_power_W", "cruise_min_after_2min_hover",
            "hover_only_endurance_min", "peak_transition_current_A")
    out = dict(
        concept="K01-LEAN twin-boom quadplane 4+1, one-piece XPS wing, H-tail, 4S (tie-break vs K09)",
        mission="REQUIREMENTS.md section 3 M-A: hover 2 min, cruise >=5 min, 20 % reserve, 0 payload + 0.25 kg growth",
        status="PROPOSED; every number ESTIMATE unless a datasheet is named in sizing.py",
        geometry=geo, structure=structure(base["mtow_kg"], geo),
        baseline=base, pessimistic=pess,
        variants=[{k: v[k] for k in keys} for v in variants],
        pusher=dict(prop=PUSHER_PROP, static_kgf_UNVERIFIED=PUSHER_STATIC_KGF, full_A_ESTIMATE=PUSHER_FULL_A,
                    pitch_speed_mps=round(PUSHER_PITCH_SPEED, 1)),
        packing=packing(geo), cost=c,
        build_hours=dict(
            items_h={"wing core (one piece) + ailerons": 8, "spar slot, skin, servo bays": 8,
                     "pod (foam board + printed nose/tray/pusher mount)": 8,
                     "boom saddles, motor mounts, legs: design + print iteration": 12,
                     "H-tail + fins + sockets": 5, "wiring: 5 ESCs, 2 boom connectors, 3 servos, airspeed": 14,
                     "ArduPilot QuadPlane setup, params, failsafes, SITL check": 16,
                     "thrust-stand tests (lift + pusher) and bench tests": 10,
                     "integration, CG, tethered first hover": 8, "slack (first-time team)": 11},
            base_total_h=100, range_h="90-110", pessimistic_h=130,
            after_first_hover="+25-35 h of flight-test sessions to a clean transition (documented QuadPlane path)"),
        gates=dict(
            G1_cost_le_1850=c["passes_G1_1850"],
            reserve_ge_one_crash_study_formula=c["reserve"] >= c["crash"]["study_formula_incl_tax"],
            reserve_ge_one_crash_K01_quote=c["reserve"] >= 266.0,
            mass_in_2p4_2p8_target=2.4 <= base["mtow_kg"] <= 2.8,
            TW_low_voltage_ge_1p6=base["TW_low_voltage"] >= 1.6,
            TW_low_voltage_pess_ge_1p6=pess["TW_low_voltage"] >= 1.6,
            static_margin_base_ge_8=geo["static_margin_pct_base"] >= 8,
            static_margin_pess_ge_8=geo["static_margin_pct_pess"] >= 8,
            cruise_ge_5min_pess=pess["cruise_min_after_2min_hover"] >= 5,
            boom_long_enough=geo["boom_long_enough"],
        ),
    )
    with open(os.path.join(here, "sizing.json"), "w") as f:
        json.dump(out, f, indent=2)
    b = base
    print(f"MTOW {b['mtow_kg']} kg (pess {pess['mtow_kg']}) | S {b['wing_area_m2']} AR {b['AR']} | "
          f"W/S {b['wing_loading_kg_m2']} kg/m2 | Vs {b['stall_mps']} -> trans >= {b['transition_min_mps_1p3Vs']} m/s")
    print(f"Hover {b['hover_power_W_table']} W / {b['hover_current_A']} A ({b['hover_C_rate']} C); "
          f"T/W {b['TW_table_full_voltage']} full V, {b['TW_low_voltage']} low V "
          f"({b['TW_low_voltage_net_of_download']} net of download); pess low V {pess['TW_low_voltage']} "
          f"({pess['TW_low_voltage_net_of_download']} net)")
    print(f"Cruise {b['cruise_mps']} m/s: CD0 {b['CD0']}, L/D {b['LD_cruise']}, {b['cruise_power_W']} W; "
          f"{b['cruise_min_after_2min_hover']} min after 2 min hover (pess {pess['cruise_min_after_2min_hover']}); "
          f"hover-only {b['hover_only_endurance_min']} min")
    print("geometry:", {k: geo[k] for k in ("x_front_motor_m", "x_rear_motor_m", "cg_pct_mac", "neutral_point_pct_mac_base",
                                            "static_margin_pct_base", "static_margin_pct_pess", "Vh", "Vv", "tail_arm_m",
                                            "boom_front_x_m", "boom_rear_x_m", "boom_rear_needed_x_m",
                                            "raymer_fus_dNP_check_pct_mac")})
    print("structure:", out["structure"])
    print("wind lean:", b["hover_wind_lean_deg"])
    print(f"cost: goods {c['goods']} tax {c['tax']} total {c['total']} reserve {c['reserve']} crash {c['crash']}")
    print("packing:", out["packing"]["box_external_m"])
    for v in out["variants"]:
        print("  ", v)
    print("gates:", out["gates"])


if __name__ == "__main__":
    main()
