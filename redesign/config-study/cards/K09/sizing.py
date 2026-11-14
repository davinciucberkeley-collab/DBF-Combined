"""K09 quad tailsitter, flat flying wing, motor-only (class S, 4S) -- first-order sizing.

Run:  python -I sizing.py      (stdlib only; writes sizing.json and cost.csv next to this file)

Mission = REQUIREMENTS.md section 3 default M-A (VTOL demonstrator):
  hover >= 2 min total, cruise >= 5 min threshold / 10 min objective at 14-20 m/s,
  20 % energy reserve, 0 payload + 0.25 kg growth allowance, T/W >= 1.6 (2.0 recommended).
Method, coefficients and propulsion table are the same as cards/K01/sizing.py so the cards compare;
the differences are tailsitter-specific and listed under "K09-SPECIFIC".
ESTIMATE = engineering guess, UNVERIFIED = unchecked claim.

Merged options (SCREENING.md section 2): U03 (= K09, motor-only), K11 biplane "Box Kite" planform,
U06 folding outer panels (phase 2). Each is a variant below.
"""
import csv
import json
import math
import os

G = 9.81
RHO = 1.225                      # sea level ISA; RFS is ~5 m ASL

# ------------------------------------------------------------------ ASSUMPTIONS
# Geometry (chosen; see CARD.md 3-view). Chosen so the WHOLE aircraft fits the 1.2 x 0.5 x 0.4 m box (C3a)
# with props off and no wing joint.
SPAN = 1.15                      # m, one-piece wing (box length 1.20 m)
CHORD = 0.30                     # m, constant chord, hot-wired from 2 in XPS
T_C = 0.10                       # reflexed section, e.g. MH 45 (9.85 %) -- flying wing needs reflex (no elevons)
E_OSWALD = 0.80                  # ESTIMATE: low AR, fins at 55 % semi-span act as partial end plates
CL_MAX = 0.90                    # ESTIMATE: reflexed section loses ~0.2 CLmax vs the 1.10 used for K01's cambered wing
MOTOR_Y = 0.32                   # m, fin / motor station from centreline (11 in props clear by 0.36 m L-R)
FIN_HALF_H = 0.19                # m, fin extends 0.19 m above and below the wing; motors at the fin tips
FIN_CHORD = 0.40                 # m, fin runs from the motor tube (0.10 m ahead of LE) to the wing TE; its TE tips are the 4 feet
X_MOTOR = -0.10                  # m, motor mount face ahead of the wing LE (prop disc 0.12-0.14 m ahead of LE)
POD = (0.20, 0.10, 0.06)         # m, centre battery/FC pod on top surface L x W x H (ESTIMATE)

# Mass build-up, kg. Wing core from geometry; rest ESTIMATE unless a datasheet is named.
RHO_XPS = 30.0                   # kg/m3, FOAMULAR NGX F-250 (same value as K01)
TAPE_KG_M2 = 0.065               # ESTIMATE, Scotch heavy-duty packing tape incl. 10 % overlap
CF_22x20_KG_M = 0.102            # calc rho 1.55, docs/research/budget-airframe.md
FOAMBOARD_KG_M2 = 0.20           # ESTIMATE, 3/16 in paper-faced foam board (weigh one, M2)
AIRFOIL_AREA_FACTOR = 0.68       # section area = 0.68 * c * t (thin-airfoil rule of thumb)


def mass_groups(span=SPAN, chord=CHORD, n_wings=1, fin_half_h=FIN_HALF_H, fin_chord=FIN_CHORD,
                pack_kg=0.386, extra=None):
    S = span * chord * n_wings
    core = AIRFOIL_AREA_FACTOR * chord * (T_C * chord) * span * n_wings * RHO_XPS
    tape = 2 * S * TAPE_KG_M2
    spar = min(1.0, span - 0.10) * CF_22x20_KG_M * n_wings       # 1 m stock tube, centred
    fin_area = 2 * (2 * fin_half_h) * fin_chord                     # two full-height fins
    fins = fin_area * 2 * FOAMBOARD_KG_M2                           # two foam-board layers sandwich the tube
    fin_tubes = 2 * (2 * fin_half_h + 0.04) * CF_22x20_KG_M         # vertical motor tubes cut from 22x20 stock
    m = {
        "wing core XPS (hot-wired, calc from geometry)": core,
        "wing skin, packing tape 2 sides": tape,
        "spar CF 22x20 (1 m stock, 102 g/m calc)": spar,
        "2 fins, 2 x 3/16 in foam board sandwich": fins,
        "2 vertical motor tubes CF 22x20 (cut from stock)": fin_tubes,
        "printed PETG: 4 motor mounts, 2 tube-spar saddles, 4 crushable feet (ESTIMATE)": 4 * 0.018 + 2 * 0.015 + 4 * 0.006,
        "centre pod: foam-board/XPS hatch + printed FC/battery tray (ESTIMATE)": 0.07,
        "4 stations: X3108S 81 g (SunnySky) + LANRC 45A 6.6 g + APC 11x4.5MR ~20 g": 4 * (0.081 + 0.0066 + 0.020),
        "motor/ESC wiring 4 x 0.5 m 16 AWG pairs + bullet connectors (ESTIMATE)": 4 * 0.015,
        "battery 4S pack (see PACKS)": pack_kg,
        "avionics: CoreWing F405 Wing V2, M100 GPS, RP3 RX, RID, AS150U, 12 AWG harness (ESTIMATE)": 0.14,
        "glue, Velcro straps, cable ties, labels (ESTIMATE)": 0.06,
    }
    if extra:
        m.update(extra)
    return m


GROWTH = 0.25                    # kg, REQUIREMENTS section 3 growth allowance (no payload)

# Propulsion -- identical to K01 (SunnySky X3108S KV900, APC 11x4.7 @ 14.8 V, docs/research/budget-lift.md)
N_LIFT = 4
PROP_D_IN = 11.0
LIFT_TABLE = [(690, 89.0), (750, 104.0), (870, 133.0), (1580, 447.0)]   # (thrust g, input W) per motor
LIFT_MAX_G = 1580.0
VOLTAGE_SAG = 0.93               # ESTIMATE (as K01)
ESC_EFF = 0.95                   # ESTIMATE (as K01)
FM = 0.65                        # ESTIMATE (as K01), momentum cross-check only
ETA_MOTOR_HOVER = 0.80           # ESTIMATE (as K01)
AVIONICS_W = 5.0                 # W (as K01; no servos here, so slightly pessimistic)

# K09-SPECIFIC hover
DOWNLOAD = 1.02                  # ESTIMATE: props sit off the wing plane (disc 0.05-0.33 m from it), wing is edge-on
                                 # to the slipstream; only fin/tube blockage

# Cruise aerodynamics (same Cf/FF/interference as K01)
CF_WING, FF_WING = 0.0060, 1.25  # ESTIMATE, Re ~3e5, tape skin
CF_BODY = 0.0070                 # ESTIMATE
INTERFERENCE = 1.15              # ESTIMATE
CDA_MOTOR_BODY = 0.0004          # m2 per motor + mount (as K01); here the motors are running, props windmill-free
ETA_MOTOR_CRUISE = 0.80          # ESTIMATE (as K01)
# K09-SPECIFIC cruise
ETA_PROP_CRUISE = 0.55           # base: hover prop near its own peak (old study configurations.md: 0.551 base);
ETA_PROP_PESS = 0.35             # pessimistic: lightly loaded 11x4.5 near zero-thrust J (old study: 0.351)
TRIM_FACTOR = 1.05               # ESTIMATE: +5 % for upper/lower differential thrust trimming pitch
                                 # (Q_TAILSIT_ENABLE 2 keeps the copter controller active in cruise)

# Energy (as K01)
V_NOM_CELL = 3.7
RESERVE = 0.20
TRANSITION_WH = 3.0              # ESTIMATE (as K01): two ~15-20 s pitch-overs at ~hover power
HOVER_MIN = 2.0
CRUISE_OBJ_MIN = 10.0

# Packs considered (4S, US stock). Script picks the lightest that meets the 10 min objective in the
# PESSIMISTIC cruise case, so the choice survives the worst prop efficiency.
PACKS = [
    dict(name="Admiral 4S 4000 40C XT60", ah=4.0, kg=0.386, usd=53.50,
         src="Motion RC ADM6024-002 2-pack $107.00, 386 g, 138x42x29 mm (motionrc.com, seen 2026-11-09)"),
    dict(name="Ovonic 4S 6500 130C XT60", ah=6.5, kg=0.68, usd=39.63,
         src="us.ovonicshop.com 2-pack $79.25 (seen 2026-11-09); 680 g per pack from a reseller listing UNVERIFIED "
             "(car-style pack; K01 used 0.56 kg for a 50C soft pack)"),
]

# Wind (same method as configurations.md: F = 0.5 rho V^2 A 1.28, tilt = atan(F/W))
CD_PLATE = 1.28
GUSTS = (5.0, 8.0)               # m/s steady and gust (D11)
Q_ANGLE_MAX_DEG = 30.0           # ArduPilot default Q_ANGLE_MAX 3000 cdeg (UNVERIFIED for 4.6)

# Transport box (C3a)
BOX = (1.20, 0.50, 0.40)
# ---------------------------------------------------------------- END ASSUMPTIONS


def interp_power(thrust_g):
    """Electrical input W per motor from the maker's table (linear interpolation; below the first row it is
    linear through zero, the same conservative rule K01 uses)."""
    t = LIFT_TABLE
    if thrust_g <= t[0][0]:
        return t[0][1] * thrust_g / t[0][0]
    for (g0, w0), (g1, w1) in zip(t, t[1:]):
        if thrust_g <= g1:
            return w0 + (w1 - w0) * (thrust_g - g0) / (g1 - g0)
    return t[-1][1]


def size(pack, span=SPAN, chord=CHORD, n_wings=1, e=E_OSWALD, cd0_factor=1.0, eta_prop=ETA_PROP_CRUISE,
         hover_area_factor=1.0, extra_mass=None, dm=0.0, label="baseline", biplane_sigma=0.0, gap=None):
    groups = mass_groups(span, chord, n_wings, pack_kg=pack["kg"], extra=extra_mass)
    mtow = sum(groups.values()) + GROWTH + dm
    W = mtow * G
    S = span * chord * n_wings
    AR = span ** 2 / S                     # biplane: span^2 / total area
    WS = W / S
    Vs = math.sqrt(2 * WS / (RHO * CL_MAX))

    # ---- hover
    T_motor_g = mtow * 1000 * DOWNLOAD / N_LIFT
    P_motor = interp_power(T_motor_g)
    P_hover = N_LIFT * P_motor / ESC_EFF + AVIONICS_W
    V_pack = 4 * V_NOM_CELL
    I_hover = P_hover / V_pack
    disk_area = N_LIFT * math.pi * (PROP_D_IN * 0.0254 / 2) ** 2
    DL = W / disk_area
    P_ideal = (W * DOWNLOAD) ** 1.5 / math.sqrt(2 * RHO * disk_area)
    P_hover_mom = P_ideal / (FM * ETA_MOTOR_HOVER * ESC_EFF) + AVIONICS_W
    FM_implied = P_ideal / (N_LIFT * P_motor * ETA_MOTOR_HOVER)
    TW = N_LIFT * LIFT_MAX_G / (mtow * 1000)
    TW_sag = TW * VOLTAGE_SAG
    I_full = N_LIFT * 30.0                 # 30 A per motor at full throttle (maker table)

    # ---- cruise drag build-up (on total wing area S)
    cd_wing = CF_WING * FF_WING * 2.04 * S / S
    fin_area = 2 * (2 * FIN_HALF_H) * FIN_CHORD
    cd_fins = CF_BODY * 1.2 * 2.04 * fin_area / S
    # vertical motor tube at each fin leading edge, axis normal to the flow, faired by the fin behind it:
    # CdA = L * d * 0.3 (ESTIMATE)
    cd_tubes = 2 * (2 * FIN_HALF_H) * 0.022 * 0.3 / S
    cd_motors = N_LIFT * CDA_MOTOR_BODY / S
    cd_pod = CF_BODY * 1.3 * (2 * (POD[0] * POD[1] + POD[0] * POD[2] + POD[1] * POD[2])) / S
    parts = dict(wing=cd_wing, fins=cd_fins, motor_tubes=cd_tubes, motors=cd_motors, pod=cd_pod)
    CD0 = sum(parts.values()) * INTERFERENCE * cd0_factor

    if biplane_sigma:
        k_ind = (1 + biplane_sigma) / 2 / (math.pi * span ** 2 / S * e)   # Prandtl biplane, equal spans
    else:
        k_ind = 1 / (math.pi * AR * e)

    def cruise(V, eta=eta_prop):
        CL = 2 * W / (RHO * V ** 2 * S)
        CD = CD0 + k_ind * CL ** 2
        D = 0.5 * RHO * V ** 2 * S * CD
        P = D * V * TRIM_FACTOR / (eta * ETA_MOTOR_CRUISE) + AVIONICS_W
        return CL, CD, CL / CD, D, P

    sweep = []
    for v10 in range(120, 221, 10):
        c = cruise(v10 / 10)
        sweep.append(dict(V=v10 / 10, LD=round(c[2], 2), P_W=round(c[4], 1)))
    # cruise speed: >= 1.3 Vs (D11), >= 14 m/s (M-A band), else min-power speed
    v_minp = min(sweep, key=lambda r: r["P_W"])["V"]
    V_c = max(math.ceil(1.3 * Vs * 2) / 2, 14.0, v_minp)
    CL_c, CD_c, LD_c, D_c, P_c = cruise(V_c)
    # pessimistic also takes CD0 x 1.3 (tape seams, fin junctions)
    CD0_save = CD0
    CD0 = CD0_save * 1.3
    P_c_pess = cruise(V_c, ETA_PROP_PESS)[4]
    LD_pess = cruise(V_c, ETA_PROP_PESS)[2]
    CD0 = CD0_save

    # ---- energy
    E_pack = 4 * V_NOM_CELL * pack["ah"]
    E_use = E_pack * (1 - RESERVE)
    E_hover = P_hover * HOVER_MIN / 60
    E_cr = E_use - E_hover - TRANSITION_WH
    cruise_min = E_cr / P_c * 60
    cruise_min_pess = E_cr / P_c_pess * 60
    hover_only_min = E_use / P_hover * 60
    cruise_only_min = (E_use - TRANSITION_WH) / P_c * 60

    # ---- hover in wind (wing broadside; hover_area_factor < 1 for K11 shielding or U06 fold)
    A_side = S * hover_area_factor
    tilt = {}
    for v in GUSTS:
        F = 0.5 * RHO * v ** 2 * A_side * CD_PLATE
        tilt[f"{v:.0f}mps"] = round(math.degrees(math.atan(F / W)), 1)
    lean_max_TW = math.degrees(math.acos(min(1.0, 1 / TW_sag)))

    # ---- stance (standing on the 4 fin trailing-edge tips); CG at 25 % chord, aircraft vertical
    cg_height = chord * 0.75 + 0.01
    tip_narrow = math.degrees(math.atan(FIN_HALF_H / cg_height))
    tip_wide = math.degrees(math.atan(MOTOR_Y / cg_height))

    return dict(
        label=label, pack=pack["name"], mtow_kg=round(mtow, 3),
        mass_groups_kg={k: round(v, 3) for k, v in groups.items()}, growth_kg=GROWTH,
        span_m=span, chord_m=chord, n_wings=n_wings, wing_area_m2=round(S, 3), AR=round(AR, 2),
        wing_loading_N_m2=round(WS, 1), wing_loading_kg_m2=round(WS / G, 2),
        stall_mps=round(Vs, 2), transition_min_mps_1p3Vs=round(1.3 * Vs, 2), cruise_mps=V_c,
        disk_loading_N_m2=round(DL, 1), thrust_per_motor_hover_g=round(T_motor_g, 0),
        hover_frac_of_max_thrust=round(T_motor_g / LIFT_MAX_G, 2),
        TW_table=round(TW, 2), TW_with_sag=round(TW_sag, 2),
        hover_power_W_table=round(P_hover, 0), hover_power_W_momentum_FM=round(P_hover_mom, 0),
        FM_implied_by_table=round(FM_implied, 2),
        hover_current_A=round(I_hover, 1), hover_current_per_motor_A=round(P_motor / ESC_EFF / V_pack, 1),
        full_throttle_current_A=I_full, connector_need_A_1p25x_transition=round(1.25 * 1.3 * I_hover, 0),
        CD0=round(CD0, 4), CD0_parts={k: round(v * INTERFERENCE, 4) for k, v in parts.items()},
        CL_cruise=round(CL_c, 3), LD_cruise=round(LD_c, 2), LD_cruise_pess=round(LD_pess, 2), drag_N=round(D_c, 2),
        cruise_power_W=round(P_c, 0), cruise_power_W_pess=round(P_c_pess, 0),
        cruise_current_A=round(P_c / V_pack, 1),
        pack_Wh=round(E_pack, 1), usable_Wh_after_reserve=round(E_use, 1), hover_Wh_2min=round(E_hover, 1),
        cruise_min_after_2min_hover=round(cruise_min, 1),
        cruise_min_after_2min_hover_pess=round(cruise_min_pess, 1),
        hover_only_endurance_min=round(hover_only_min, 1), cruise_only_endurance_min=round(cruise_only_min, 1),
        gust_tilt_deg=tilt, max_lean_from_TW_deg=round(lean_max_TW, 1),
        gust_8mps_exceeds_Q_ANGLE_MAX=tilt["8mps"] > Q_ANGLE_MAX_DEG,
        stance_tipover_deg=dict(narrow=round(tip_narrow, 1), wide=round(tip_wide, 1), cg_height_m=round(cg_height, 3)),
        speed_sweep=sweep,
    )


def packing(span=SPAN, chord=CHORD):
    env = (span, chord - X_MOTOR + 0.045, 2 * FIN_HALF_H + 0.01)   # L, depth (motor can + adapter), H (+feet)
    box = sorted(BOX, reverse=True)
    fits = all(a <= b for a, b in zip(sorted(env, reverse=True), box))
    return dict(
        envelope_props_off_m=[round(x, 3) for x in env], box_m=list(BOX), fits_one_box=fits,
        envelope_props_on_height_m=round(2 * (FIN_HALF_H + PROP_D_IN * 0.0254 / 2), 3),
        pieces=1, structural_field_joints=0, longest_piece_m=span,
        field_steps="4 prop nuts (or leave props in a separate tray), battery in + strap, arm check",
        assembly_min_ESTIMATE=5, people=1,
        box_mass_kg_ESTIMATE="aircraft ~2 kg + foam-lined box ~3 kg = ~5 kg",
    )


def pick_pack():
    for p in sorted(PACKS, key=lambda p: p["kg"]):
        r = size(p)
        if r["cruise_min_after_2min_hover_pess"] >= CRUISE_OBJ_MIN:
            return p, r
    p = max(PACKS, key=lambda p: p["ah"])
    return p, size(p)


# ------------------------------------------------------------------ COST (same structure as cost_model.py)
TAX = 0.1025
BUDGET = 2000.00
CRASH_RESERVE_PLANNED = 150.00   # REQUIREMENTS C1
SHIPPING = 120.00                # class S ESTIMATE (cost_model.py SHIPPING["S"])
# (group, item, qty, unit USD pre-tax, vendor / source, date seen, note)
BOM = [
    ("propulsion", "SunnySky X3108S KV900 motor (4 + 1 spare)", 5, 24.99,
     "SunnySky USA sunnyskyusa.com/products/sunnysky-x3108s-motors (docs/research/budget-lift.md)", "2026-11-01", ""),
    ("propulsion", "LANRC BLHeli_S 45A ESC 4-pack (4 + 4 spare)", 2, 30.00,
     "Amazon B0D2HS4Y4J (docs/research/bom-savings.md)", "2026-11-01", "45 A cont / 55 A 10 s, 2-6S"),
    ("propulsion", "APC 11x4.5MR / MRP props (2 CW + 2 CCW fitted, 8 spare)", 12, 3.83,
     "APC apcprop.com/product/11x4-5mr (docs/research/budget-lift.md)", "2026-11-01", "1/4 in bore"),
    ("propulsion", "APC LPAR06E-type adapter rings", 12, 0.50,
     "APC (ESTIMATE price)", "2026-11-09", "ESTIMATE"),
    ("battery", "OVONIC 4S 6500 130C XT60 LiPo, 2-pack (4 packs total)", 2, 79.25,
     "OVONIC US store us.ovonicshop.com (2-x-ovonic-4s-6500mah-14-8v-130c...)", "2026-11-09",
     "sale price (was $119.88); 680 g UNVERIFIED; fallback Admiral 4S 4000 2-pack $107 (Motion RC) if 6500 is OOS"),
    ("avionics", "CoreWing F405 Wing APP V2 (pins)", 1, 67.26,
     "ReadyMadeRC (docs/research/budget-avionics.md)", "2026-10-13", "ArduPilot target"),
    ("avionics", "HGLRC M100-5883 GPS + compass", 1, 20.49, "RaceDayQuads (budget-avionics.md)", "2026-10-13", ""),
    ("avionics", "NewBeeDrone BeeID v1.1 Remote ID", 1, 39.99, "newbeedrone.com (bom-savings.md)", "2026-11-01",
     "conditional: only if flown outside the RFS FRIA (D4); kept for parity with cost_model"),
    ("avionics", "RadioMaster Pocket Crush ELRS transmitter", 1, 64.99, "radiomasterrc.com (budget-avionics.md)",
     "2026-10-13", ""),
    ("avionics", "RadioMaster RP3 V2 ELRS receiver", 1, 19.99, "radiomasterrc.com (budget-avionics.md)", "2026-10-13", ""),
    ("airframe", "FOAMULAR NGX F-250 XPS 2 in x 4 x 8 ft (wing cores: ~6 wings per sheet)", 1, 59.97,
     "Home Depot El Cerrito (docs/research/budget-airframe.md)", "2026-10", "local pickup"),
    ("airframe", "Foam board 20x30 in 10-pack (fins + first foam-board prototype)", 1, 35.92,
     "Amazon B074QZMLQF (budget-airframe.md)", "2026-10", ""),
    ("airframe", "CF tube 22x20x1000 matte (spar, 2 motor tubes, 1 spare)", 3, 28.32,
     "Amazon (budget-airframe.md)", "2026-10", "overseas lead time ~2 weeks: order mid-Dec"),
    ("airframe", "PETG filament 1 kg (Ambrosia)", 2, 20.99,
     "West3D (docs/research/airframe-materials.md)", "2026-10", "or free Prusa PLA at Jacobs"),
    ("airframe", "Scotch Heavy Duty packing tape 6 rolls", 1, 19.98, "Amazon B000087KUA (budget-airframe.md)", "2026-10", ""),
    ("airframe", "Foam-safe glue (UHU Por / Gorilla clear)", 1, 12.99, "cost_model.py AIRFRAME (ESTIMATE vendor)", "2026-11", ""),
    ("hardware", "Wiring + hardware kit (AS150U, 12/16 AWG, bullets, screws, inserts, Velcro, epoxy, UBEC)", 1, 124.01,
     "cost_model.py HARDWARE_MIN (bom-savings.md)", "2026-11-01",
     "kept at the shared floor for parity; K09 needs no horns/pushrods/hinge tape (~-$15 ESTIMATE)"),
    ("ground", "HTRC C150 charger 150 W AC", 1, 56.99, "Amazon B0H4QLJYHY (budget-energy-test.md)", "2026-11-01", ""),
    ("ground", "LiPo bag (Pyrodrone)", 2, 9.99, "Pyrodrone (cost_model.py)", "2026-11-01", ""),
    ("ground", "Ammo can (Harbor Freight 63750)", 1, 19.99, "Harbor Freight (cost_model.py)", "2026-11-01", ""),
    ("ground", "Watt meter 150 A", 1, 12.99, "Amazon (budget-energy-test.md)", "2026-11-01", ""),
    ("ground", "IR thermometer", 1, 8.98, "Amazon (budget-energy-test.md)", "2026-11-01", ""),
    ("ground", "Thrust stand: 20 kg load cell + HX711 + Nano", 1, 17.97, "Amazon (budget-energy-test.md)", "2026-11-01", ""),
    ("ground", "Pinecil V2 soldering iron", 1, 25.99, "Pine64 (cost_model.py)", "2026-11-01", ""),
    ("ground", "USB-C PD supply for iron", 1, 20.00, "ESTIMATE", "2026-11-09", "ESTIMATE"),
    ("ground", "Multimeter", 1, 25.00, "ESTIMATE", "2026-11-09", "ESTIMATE"),
    ("ground", "Solder, flux, wick", 1, 15.00, "ESTIMATE", "2026-11-09", "ESTIMATE"),
    ("ground", "Hot-wire: NICE-POWER 30 V 10 A supply + Ni80 24 AWG", 1, 41.73,
     "Amazon B0CRSS744F + B0CP9V3DBX (bom-savings.md)", "2026-11-01", ""),
    ("ground", "Foam-lined transport box (corrugated/plywood + packing foam)", 1, 25.00, "ESTIMATE (Home Depot)", "2026-11-09",
     "ESTIMATE; the one box that carries the aircraft"),
]


def cost():
    rows, goods = [], 0.0
    for g, item, q, u, src, date, note in BOM:
        ext = q * u
        goods += ext
        rows.append([g, item, q, f"{u:.2f}", f"{ext:.2f}", src, date, note])
    tax = goods * TAX
    total = goods + tax + SHIPPING
    reserve_total = BUDGET - total
    rows += [
        ["subtotal", "Goods pre-tax", "", "", f"{goods:.2f}", "", "", ""],
        ["tax", "Sales tax 10.25 % (Berkeley, CDTFA 2026-10-01)", "", "", f"{tax:.2f}", "cost_model.py TAX", "", ""],
        ["shipping", "Shipping, all vendors (class S)", "", "", f"{SHIPPING:.2f}", "cost_model.py SHIPPING['S']", "",
         "ESTIMATE; SunnySky/APC/OVONIC/Amazon"],
        ["TOTAL", "Spend at order time (tax + shipping included)", "", "", f"{total:.2f}", "", "", ""],
        ["reserve", "Planned crash reserve (REQUIREMENTS C1)", "", "", f"{CRASH_RESERVE_PLANNED:.2f}", "", "",
         "one bad crash class S = $280.21 pre-tax / $308.93 incl. tax (cost_model.py formula); K09 airframe rebuild is cheaper (~$20 of foam)"],
        ["unallocated", "Left after the planned reserve", "", "", f"{reserve_total - CRASH_RESERVE_PLANNED:.2f}", "", "", ""],
        ["budget", "Budget (hard)", "", "", f"{BUDGET:.2f}", "", "", f"total reserve {reserve_total:.2f}"],
    ]
    return rows, dict(goods=round(goods, 2), tax=round(tax, 2), shipping=SHIPPING, total=round(total, 2),
                      reserve_total=round(reserve_total, 2), planned_crash_reserve=CRASH_RESERVE_PLANNED,
                      unallocated=round(reserve_total - CRASH_RESERVE_PLANNED, 2),
                      passes_G1_1850=total <= 1850.0)


def main():
    pack, base = pick_pack()
    sigma = (1 - 0.66 * (2 * FIN_HALF_H) / 0.80) / (1.055 + 3.7 * (2 * FIN_HALF_H) / 0.80)   # Prandtl approx
    variants = [
        base,
        size(PACKS[0], label="fallback pack Admiral 4S 4000 (lighter; check pess column)"),
        size(pack, eta_prop=ETA_PROP_PESS, cd0_factor=1.3, label="pessimistic (eta_prop 0.35, CD0 x1.3): read cruise_min_after_2min_hover only"),
        size(pack, dm=0.30, label="sensitivity: +0.30 kg mass growth"),
        # K11 Box Kite: two 0.80 x 0.22 m wings stacked 0.38 m, fins at the tips; downstream wing ~50 % shielded
        size(pack, span=0.80, chord=0.22, n_wings=2, cd0_factor=1.15, biplane_sigma=sigma,
             hover_area_factor=0.75, label="K11 biplane Box Kite 0.80 m (2 x 0.80 x 0.22)"),
        # U06: outer panels (outboard of fins, 2 x 0.255 m) fold for hover; +2 hinges, 2 servos, locks
        size(pack, dm=0.09, hover_area_factor=(2 * MOTOR_Y) / SPAN,
             extra_mass=None, label="U06 folding outer panels (phase 2)"),
    ]
    rows, c = cost()
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "cost.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "item", "qty", "unit_usd", "ext_usd", "vendor_source", "date_seen", "note"])
        w.writerows(rows)
    out = dict(
        concept="K09 quad tailsitter, flat flying wing, motor-only (U03 = K09); options K11, U06",
        mission="REQUIREMENTS.md section 3 M-A: hover 2 min, cruise >=5/10 min, 20 % reserve, 0 payload + 0.25 kg growth",
        status="PROPOSED; every number ESTIMATE unless a datasheet is named in sizing.py",
        pack_choice=dict(name=pack["name"], source=pack["src"],
                         rule="lightest 4S pack meeting the 10 min objective in the pessimistic cruise case"),
        baseline=base,
        variants=[{k: v[k] for k in ("label", "pack", "mtow_kg", "span_m", "wing_area_m2", "TW_table", "stall_mps",
                                     "cruise_mps", "LD_cruise", "cruise_power_W", "hover_current_A",
                                     "cruise_min_after_2min_hover", "cruise_min_after_2min_hover_pess",
                                     "hover_only_endurance_min", "gust_tilt_deg")} for v in variants],
        K11_biplane_sigma=round(sigma, 3),
        packing=packing(),
        packing_K11=dict(envelope_props_off_m=[0.80, round(0.22 - X_MOTOR + 0.045, 3), round(2 * FIN_HALF_H + 0.01, 3)],
                         note="one piece, 0.8 m: fits a back seat or a 0.8 m box"),
        cost=c,
        gates=dict(
            G1_cost_le_1850=c["passes_G1_1850"],
            G3_one_box=packing()["fits_one_box"],
            G6_TW_ge_1p6=base["TW_table"] >= 1.6, TW_ge_2p0_recommended=base["TW_table"] >= 2.0,
            cruise_threshold_5min=base["cruise_min_after_2min_hover"] >= 5,
            cruise_objective_10min=base["cruise_min_after_2min_hover"] >= 10,
            cruise_objective_10min_pess=base["cruise_min_after_2min_hover_pess"] >= 10,
            AS150U_70A_cont_ok_for_transition=base["connector_need_A_1p25x_transition"] <= 70,
            hover_in_8mps_gust_within_Q_ANGLE_MAX=not base["gust_8mps_exceeds_Q_ANGLE_MAX"],
        ),
    )
    with open(os.path.join(here, "sizing.json"), "w") as f:
        json.dump(out, f, indent=2)
    b = base
    print(f"Pack: {pack['name']}")
    print(f"MTOW {b['mtow_kg']} kg | S {b['wing_area_m2']} m2 AR {b['AR']} | W/S {b['wing_loading_kg_m2']} kg/m2 | "
          f"Vs {b['stall_mps']} -> transition >= {b['transition_min_mps_1p3Vs']} m/s, cruise {b['cruise_mps']} m/s")
    print(f"Hover: DL {b['disk_loading_N_m2']} N/m2, {b['thrust_per_motor_hover_g']} g/motor, {b['hover_power_W_table']} W "
          f"table / {b['hover_power_W_momentum_FM']} W momentum (FM implied {b['FM_implied_by_table']}), "
          f"{b['hover_current_A']} A; T/W {b['TW_table']} ({b['TW_with_sag']} sag)")
    print(f"Cruise: CD0 {b['CD0']} {b['CD0_parts']} L/D {b['LD_cruise']} (pess {b['LD_cruise_pess']}), "
          f"{b['cruise_power_W']} W (pess {b['cruise_power_W_pess']}), {b['cruise_current_A']} A")
    print(f"Energy {b['pack_Wh']} Wh: cruise {b['cruise_min_after_2min_hover']} min (pess "
          f"{b['cruise_min_after_2min_hover_pess']}) after 2 min hover; hover-only {b['hover_only_endurance_min']} min; "
          f"cruise-only {b['cruise_only_endurance_min']} min")
    print(f"Wind tilt {b['gust_tilt_deg']} (Q_ANGLE_MAX {Q_ANGLE_MAX_DEG}); max lean {b['max_lean_from_TW_deg']}; "
          f"stance {b['stance_tipover_deg']}")
    print("mass groups:", b["mass_groups_kg"])
    for v in out["variants"]:
        print("  ", v)
    print("packing:", out["packing"])
    print("cost:", c)
    print("gates:", out["gates"])


if __name__ == "__main__":
    main()
