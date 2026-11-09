"""B1 aero performance engineer: whole-aircraft performance of the K09-L quad tailsitter.

Run:  python -I redesign/team/B1/performance.py
Writes, beside this file:
  claims.json              proof-chain claims (read by redesign/proofs/build_graph.py)
  performance_results.json corridor table, cruise sweep, transition time history (for PERFORMANCE.md)
  fig-b1-corridor.svg      FIG B1-01 transition corridor, pitch vs airspeed
  fig-b1-endurance.svg     FIG B1-02 cruise time after the 2 min hover vs cruise speed

Method (first order where B2/B3/B4/E1 data do not exist yet). Rev 2 (CR-A1-13): c 0.32, S5010, 11x5.5MR.
  aero      wing: B2 S5010 trimmed polar (XFOIL section drag in AVL: CD0_wing, e, CLa; B2 alpha0, trimmed CLmax)
            x a tape-seam roughness factor; fins, tubes, motors, pod: component build-up. Linear lift to CLmax
            then a decay (e-folding 4 deg) onto a flat plate (CN = CD90 sin a): valid 0-90 deg, which a
            tailsitter sweeps through in transition and in hover in wind. Pessimistic: CD0 x 1.3 and e from
            params (0.80) instead of B2's 0.93.
  prop      APC PER3 11x5.5MR Ct(J), Cp(J) at 6 000 rpm (B4 data file; cruise runs at ~6 000 rpm).
  motor     E1's DC model constants (Kv, Rm, I0), calibrated so the full chain reproduces the maker's hover table
            point (690 gf, 89 W, 11x4.7) with the 11x4.5MR static coefficients; the factor transfers to the
            11x5.5MR (as E1's ASM-E1-CAL-TRANSFER).
  hover     maker thrust table x download factor x (11x5.5MR / 11x4.5MR model power at hover thrust); the mission
            uses the params hover power (E1, 400 W) and B1's figure is the cross-check.
  corridor  quasi-steady level flight at each airspeed: T cos(theta) = D, T sin(theta) + L = W.
  pitch-over  point-mass time simulation, pitch rate limited, altitude hold on thrust below the assist speed,
            speed hold on thrust above it, pitch never below what the wing plus thrust need to hold altitude.
Every calculation is a pure function of its named inputs (proofs/README.md rule 2). Python 3 stdlib only.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../B2/params.json"])
P = "P:"
DEG = math.pi / 180.0

# ================================================================== sources
kit.source("SRC-B1-APC-PER3", "APC PER3 performance file, 11x4.5MR", "datasheet",
           url="https://www.apcprop.com/files/PER3_11x45MR.dat", checked="2026-11-09",
           where="block 'PROP RPM = 6000', columns J, Ct, Cp (all 30 rows to zero thrust at J 0.545)",
           note="APC's own blade-element prediction, not a wind-tunnel test; static values run ~10 % optimistic "
                "(K09 REVIEW section 3, J1 REFERENCES). B4 owns the prop data.")
kit.source("SRC-B1-HOERNER", "Hoerner, Fluid-Dynamic Drag (1965)", "book",
           where="ch. 3: flat plate normal to flow CD 1.17-1.28 by aspect ratio; ch. 2-6 component drag",
           note="CD90 1.28 is the value the K09 card and REVIEW used for the hover-lean check; kept for continuity")
kit.source("SRC-B1-HELMBOLD", "Helmbold lift slope for low aspect ratio", "book",
           where="Raymer, Aircraft Design: A Conceptual Approach, 6th ed., eq. 12.6 (swept form reduces to "
                 "Helmbold at zero sweep)",
           note="a = 2 pi AR / (2 + sqrt(AR^2 + 4)) with a 2-D slope of 2 pi")
kit.source("SRC-B1-ARDUPILOT-TS", "ArduPilot Plane tailsitter and airspeed parameters", "web",
           url="https://ardupilot.org/plane/docs/guide-tailsitter.html",
           where="Q_TAILSIT_ANGLE, Q_TAILSIT_RAT_FW, Q_ASSIST_SPEED, AIRSPEED_MIN/CRUISE",
           note="parameter names only; values below are B1 proposals for F4")

# ================================================================== assumptions
# APC 11x5.5MR, PER3 block RPM = 6000: [J, Ct, Cp], every row of team/B4/data/apc_per3_11x55MR.csv (B4 copied the
# file as printed, every second row near J = 0). The last row is B1's linear extrapolation of the last two rows to
# zero thrust (J 0.639); APC prints no row there.
PROP_TABLE = [
    [0.0000, 0.1121, 0.0418], [0.0446, 0.1083, 0.0423], [0.0891, 0.1038, 0.0426], [0.1337, 0.0987, 0.0426],
    [0.1782, 0.0930, 0.0422], [0.2228, 0.0865, 0.0414], [0.2674, 0.0794, 0.0402], [0.3119, 0.0716, 0.0385],
    [0.3565, 0.0630, 0.0363], [0.4010, 0.0539, 0.0335], [0.4456, 0.0443, 0.0303], [0.4679, 0.0393, 0.0285],
    [0.4902, 0.0343, 0.0267], [0.5124, 0.0292, 0.0247], [0.5347, 0.0241, 0.0226], [0.5570, 0.0189, 0.0204],
    [0.5793, 0.0137, 0.0181], [0.6016, 0.0085, 0.0157], [0.6238, 0.0034, 0.0133], [0.6386, 0.0000, 0.0117],
]
# APC 11x4.5MR, PER3 block RPM = 6000 (rev 1 prop): kept only as the calibration reference against the maker's
# 11x4.7 hover table and for the 11x5.5MR / 11x4.5MR hover power ratio.
PROP_TABLE_REF = [
    [0.0000, 0.0971, 0.0335], [0.0188, 0.0952, 0.0336], [0.0376, 0.0931, 0.0336], [0.0564, 0.0909, 0.0336],
    [0.0752, 0.0887, 0.0335], [0.0940, 0.0863, 0.0334], [0.1128, 0.0838, 0.0332], [0.1316, 0.0813, 0.0330],
    [0.1504, 0.0786, 0.0327], [0.1692, 0.0758, 0.0324], [0.1880, 0.0728, 0.0320], [0.2069, 0.0698, 0.0315],
    [0.2257, 0.0666, 0.0310], [0.2445, 0.0634, 0.0304], [0.2633, 0.0600, 0.0297], [0.2821, 0.0564, 0.0290],
    [0.3009, 0.0528, 0.0281], [0.3197, 0.0491, 0.0273], [0.3385, 0.0453, 0.0263], [0.3573, 0.0415, 0.0253],
    [0.3761, 0.0375, 0.0242], [0.3949, 0.0335, 0.0230], [0.4137, 0.0294, 0.0217], [0.4325, 0.0253, 0.0204],
    [0.4513, 0.0211, 0.0191], [0.4701, 0.0169, 0.0176], [0.4889, 0.0127, 0.0161], [0.5077, 0.0084, 0.0145],
    [0.5265, 0.0042, 0.0129], [0.5453, 0.0000, 0.0112],
]
kit.source("SRC-B1-B4-PER3-55", "APC PER3 11x5.5MR rows as copied by B4", "file",
           url="https://www.apcprop.com/files/PER3_11x55MR.dat", checked="2026-11-09",
           where="team/B4/data/apc_per3_11x55MR.csv, rows rpm = 6000 (19 rows, J 0 to 0.624)",
           note="B1 compared every 6 000 rpm row of B4's file with PROP_TABLE on 2026-11-09. APC's blade-element "
                "prediction, not a test; B4 owns the prop data")
kit.assumption("ASM-B1-PROP", "11x5.5MR Ct and Cp versus J",
               "The fitted prop (APC 11x5.5MR, params propulsion.prop) follows APC's PER3 Ct(J), Cp(J) at 6 000 rpm "
               "at every operating point; rows are [J, Ct, Cp]; last row extrapolated to zero thrust",
               basis="B4's copy of the APC file; cruise runs at 6 000 rpm (CL-B4-CRUISE-RPM); Re effect between the "
                     "5 000 and 7 000 rpm blocks < 1 % on Ct, Cp; the hover-table calibration (CALC-B1-PROPCAL) "
                     "absorbs APC's static optimism", value=PROP_TABLE, unit="-", status="PROPOSED",
               cites=["SRC-B1-B4-PER3-55", "SRC-APC-11X55MR"])
kit.assumption("ASM-B1-PROP-REF", "11x4.5MR Ct and Cp versus J (calibration reference)",
               "APC PER3 11x4.5MR at 6 000 rpm, rows [J, Ct, Cp]; used only to calibrate the chain to the maker "
               "table (11x4.7) and for the 11x5.5MR / 11x4.5MR hover power ratio",
               basis="APC data file read 2026-11-09 (rev 1 of this script); the 11x4.5MR is closer in pitch to the "
                     "maker's 11x4.7 than the 11x5.5MR, so it carries the calibration with less prop error",
               value=PROP_TABLE_REF, unit="-", status="PROPOSED", cites=["SRC-B1-APC-PER3"])
kit.assumption("ASM-B1-DRAG", "Zero-lift drag build-up coefficients, non-wing parts",
               "[Cf fin/pod, FF fin, CD motor tube (frontal, faired by the fin), CdA per motor m2, FF pod, "
               "interference factor] = [0.0070, 1.20, 0.30, 0.0004, 1.30, 1.15]",
               basis="Same coefficients as the K09 card and the K01 card, accepted by the K09 REVIEW (section 4: "
                     "'already pessimistic'); turbulent flat plate at Re 3e5 for the paper-faced board and pod; "
                     "Hoerner for the tube. The wing now uses B2's S5010 section drag (ASM-B1-WING-ROUGH)",
               value=[0.0070, 1.20, 0.30, 0.0004, 1.30, 1.15], unit="-", status="UNVERIFIED",
               cites=["SRC-K09-CARD", "SRC-K09-REVIEW", "SRC-B1-HOERNER"])
kit.assumption("ASM-B1-WING-ROUGH", "Tape-seam factor on the S5010 wing profile drag",
               "The packing-tape wing has 1.10 x the XFOIL Ncrit 9 profile drag that B2's AVL polar carries",
               basis="B2 CR-B2-08: S5010 cd at cl 0.47 is 0.0087 (Re 3e5, Ncrit 9) and 0.0096 (Re 2.3e5, Ncrit 5); "
                     "the ratio 1.10 stands in for early transition at spanwise tape seams. A trip-strip XFOIL run "
                     "(B2) or the cruise-power test replaces it", value=1.10, unit="-", status="PROPOSED",
               cites=["SRC-B2-XFOIL"])
kit.assumption("ASM-B1-CD90", "Flat-plate normal-force coefficient",
               "Wing normal-force coefficient beyond stall CN = CD90 sin(alpha), CD90 = 1.28",
               basis="Hoerner flat plate; the value the K09 card used for hover lean, kept so the numbers compare. "
                     "Low-AR wings with end plates keep more post-stall lift, so this under-predicts lift in "
                     "transition (conservative)", value=1.28, unit="-", status="PROPOSED", cites=["SRC-B1-HOERNER"])
kit.assumption("ASM-B1-ESC", "ESC efficiency", "ESC efficiency 0.95 in hover and cruise",
               basis="K09 card value; BLHeli_S at 7-30 A", value=0.95, unit="-", status="UNVERIFIED",
               cites=["SRC-K09-CARD"])
kit.assumption("ASM-B1-AVIONICS-W", "Avionics and servo power",
               "FC, GPS, receiver, telemetry, airspeed sensor and two elevon servos draw 6 W together",
               basis="card 5 W + 1 W for the two servos", value=6.0, unit="W", status="PROPOSED",
               cites=["SRC-K09-CARD"])
kit.assumption("ASM-B1-TRIM", "Cruise trim drag factor",
               "Trim adds 2 % to cruise drag on top of B2's trimmed wing polar",
               basis="B2's polar (P:b2.avl.e_oswald, cd0_wing) is already trimmed, elevon profile drag included; "
                     "B3 finds +0.2 % induced trim drag at 16 m/s (CR-B3-07). The 2 % left covers the up-trimmed "
                     "elevon gap and pod/fin junctions. Was 1.05 (K09 card) before B2/B3 answered",
               value=1.02, unit="-", status="PROPOSED", cites=["SRC-B2-AVL"])
kit.assumption("ASM-B1-VCRUISE", "Proposed cruise airspeed 16 m/s",
               "B1 proposes AIRSPEED_CRUISE = 16 m/s (params.json#performance.cruise_ms, CHANGE-LOG D-01)",
               basis="lowest whole-number speed above 1.3 Vs at the 2.6 kg gate with B2's trimmed CLmax 0.80 on "
                     "the c 0.32 wing (15.43 m/s, CL-B1-VT-GATE); +3.7 %, about 0.6 m/s for airspeed-hold and "
                     "sensor error (R-AIRSPEED-ERR allows 1 m/s, so the margin is thin)", value=16.0, unit="m/s",
               status="PROPOSED")
kit.assumption("ASM-B1-PESS", "Pessimistic-case factors",
               "[CD0 factor, prop efficiency factor, hover power factor] = [1.30, 0.85, 1.10]; the pessimistic "
               "case also uses params wing.oswald_e (0.80) in place of B2's 0.93",
               basis="CD0 x 1.3 as the K09 REVIEW pessimistic case; prop efficiency 15 % below APC (BEMT "
                     "optimism, tractor prop ahead of a fin and tube); hover +10 % for APC static optimism and "
                     "the 11x4.7 maker table (400 W x 1.10 = 440 W, E2's pessimistic 29.9 A x 14.8 V = 443 W)",
               value=[1.30, 0.85, 1.10], unit="-", status="PROPOSED",
               cites=["SRC-K09-REVIEW"])
kit.assumption("ASM-B1-CTRL-RESERVE", "Thrust kept for attitude control",
               "Steady flight may use at most 80 % of available thrust (sagged pack); 20 % stays for control",
               basis="common multirotor practice (hover throttle <= 50-60 %, never saturate in steady state); "
                     "a tailsitter controls pitch in hover and transition by differential thrust only",
               value=0.80, unit="-", status="PROPOSED")
kit.assumption("ASM-B1-LAND-ERR", "Landing attitude error",
               "Attitude error at touchdown, on top of the steady wind lean, is 10 deg",
               basis="first-order allowance for gusts and controller error in QLAND; C5 and H2 refine from the "
                     "twin's logs", value=10.0, unit="deg", status="PROPOSED")
kit.assumption("ASM-B1-TRANS", "Pitch-over schedule",
               "[pitch rate deg/s, assist speed as a fraction of Vs, back-transition energy as a fraction of "
               "the forward pitch-over] = [12, 1.10, 1.0]",
               basis="12 deg/s is the fastest whole-number pitch-down rate that keeps peak thrust <= 80 % of "
                     "available in CALC-B1-PITCHOVER on the worst-case pack (sag 0.72, D-06): 13 deg/s gives 0.79, "
                     "15 gives 0.84, 20 gives 0.96 (rev 1 used 20 at sag 0.93). On a fresh pack 20 deg/s gives 0.59 "
                     "(performance_results.json#sensitivity). Proposed first-flight Q_TAILSIT_RAT_FW; thrust holds "
                     "altitude below 1.1 Vs (Q_ASSIST_SPEED analogue); the back-transition is a pitch-up deceleration "
                     "of similar length at similar thrust", value=[12.0, 1.10, 1.0], unit="-", status="PROPOSED",
               cites=["SRC-B1-ARDUPILOT-TS"])


# ================================================================== pure model helpers (no side effects)
def interp_table(rows, x, col):
    """Linear interpolation in rows sorted by column 0; clamped at the ends."""
    if x <= rows[0][0]:
        return rows[0][col]
    for a, b in zip(rows, rows[1:]):
        if x <= b[0]:
            return a[col] + (b[col] - a[col]) * (x - a[0]) / (b[0] - a[0])
    return rows[-1][col]


def prop_ct(tab, J):
    return max(0.0, interp_table(tab, J, 1))


def prop_cp(tab, J):
    return interp_table(tab, J, 2)


def prop_operating_point(tab, T, Va, D, rho):
    """Rev/s, shaft W and efficiency for one prop giving thrust T (N) at axial inflow Va (m/s)."""
    if T <= 0:
        return 0.0, 0.0, 0.0
    j_zero = tab[-1][0]
    lo = max(1.0, Va / (j_zero * D) * 1.0001)
    hi = 600.0
    for _ in range(80):
        n = 0.5 * (lo + hi)
        if prop_ct(tab, Va / (n * D)) * rho * n * n * D ** 4 > T:
            hi = n
        else:
            lo = n
    n = 0.5 * (lo + hi)
    J = Va / (n * D)
    p = prop_cp(tab, J) * rho * n ** 3 * D ** 5
    return n, p, (T * Va / p if p > 0 else 0.0)


def prop_tmax(tab, Va, n_max, D, rho):
    """Thrust of one prop at the maximum speed n_max (rev/s) and axial inflow Va."""
    return prop_ct(tab, Va / (n_max * D)) * rho * n_max * n_max * D ** 4


def motor_input_w(p_shaft, n, motor):
    """DC motor model: electrical input (W) at the motor terminals for shaft power p_shaft at n rev/s."""
    if p_shaft <= 0 or n <= 0:
        return 0.0
    kv, rm, i0 = motor
    kt = 60.0 / (2 * math.pi * kv)
    i = p_shaft / (2 * math.pi * n) / kt + i0
    return (n * 60.0 / kv + i * rm) * i


def table_power_w(table_gw, thrust_g):
    """Maker table, input W per motor. Below the first row power scales as thrust^1.5 (momentum theory)."""
    t = sorted(table_gw)
    if thrust_g <= t[0][0]:
        return t[0][1] * (thrust_g / t[0][0]) ** 1.5
    return interp_table(t, thrust_g, 1)


def aero_model(a_deg, cla, a0_deg, clmax, cd0, k, cd90, decay_deg=4.0):
    """Wing CL, CD from 0 to 90 deg angle of attack: linear lift up to CLmax at the stall angle, then an
    exponential decay (e-folding 4 deg) onto the flat-plate values CL = CD90 sin a cos a, CD = CD0 + CD90 sin^2 a.
    Continuous in CL and CD; reaches CLmax exactly at the stall angle."""
    a = a_deg * DEG
    a0 = a0_deg * DEG
    a_s = a0 + clmax / cla
    if a <= a_s:
        cl = cla * (a - a0)
        return cl, cd0 + k * cl * cl
    f = math.exp(-(a - a_s) / (decay_deg * DEG))
    cl_p = cd90 * math.sin(a) * math.cos(a)
    cd_p = cd0 + cd90 * math.sin(a) ** 2
    return cl_p + (clmax - cl_p) * f, cd_p + (cd0 + k * clmax * clmax - cd_p) * f


def level_equilibrium(V, W, rho, S, aero, a_stall):
    """Steady level flight at airspeed V: pitch theta (deg, = angle of attack) with L + D tan(theta) = W and
    thrust T = D / cos(theta) along the body axis. Returns (theta, T, theta). Of the roots, the lowest one with
    an unstalled wing (theta <= a_stall) is taken when it exists (wing-borne branch); otherwise the highest
    (thrust-borne branch, connected to hover)."""
    if V < 0.05:
        return 90.0, W, 90.0
    q = 0.5 * rho * V * V * S

    def g(th):
        cl, cd = aero(th)
        return q * cl + q * cd * math.tan(th * DEG) - W
    roots = []
    th, prev = 89.95, g(89.95)
    while th > -5:
        nxt = th - 0.05
        gn = g(nxt)
        if (gn < 0) != (prev < 0):
            lo, hi = nxt, th
            for _ in range(40):
                mid = 0.5 * (lo + hi)
                if (g(mid) < 0) == (gn < 0):
                    lo = mid
                else:
                    hi = mid
            roots.append(0.5 * (lo + hi))
        th, prev = nxt, gn
    if not roots:
        return None, None, None
    unstalled = [r for r in roots if r <= a_stall]
    th = min(unstalled) if unstalled else max(roots)
    _, cd = aero(th)
    return th, q * cd / math.cos(th * DEG), th


def aero_from(cla, a0, clmax, cd0, k, cd90):
    return lambda a: aero_model(a, cla, a0, clmax, cd0, k, cd90)


# ================================================================== calculations
@kit.calc("CALC-B1-AERO", title="Aero model: CD0, k, lift slope, stall angle",
          equation="CD0 = IF [CD0_wing,B2 f_rough + Cf FF Swet_fins + Cd_tube d L + n CdA_motor + Cf FF Swet_pod] / S, "
                   "Swet_fin = 2 A (1 + 0.2 t/c) ; k = 1/(pi AR e_B2) ; k_pess = 1/(pi AR e_params) ; "
                   "a = CLa (B2 AVL) ; alpha_s = alpha0 + CLmax/a ; L/D max = 1/(2 sqrt(CD0 k))",
          inputs={"b": P + "wing.span_m", "c": P + "wing.chord_m", "tc": P + "wing.t_c",
                  "e_b2": P + "b2.avl.e_oswald", "e_pess": P + "wing.oswald_e", "cd0_w": P + "b2.avl.cd0_wing",
                  "rough": "ASM-B1-WING-ROUGH", "cla": P + "b2.avl.cla_per_rad",
                  "fin_h": P + "fins.half_height_m", "fin_c": P + "fins.chord_m", "tube_l": P + "fins.tube.length_m",
                  "tube_d": P + "fins.tube.od_m", "pod": P + "pod.size_m", "n": P + "propulsion.n_motors",
                  "drag": "ASM-B1-DRAG", "a0": P + "b2.xfoil.alpha0_2d_deg", "clmax": "CL-B2-CLMAX-DESIGN"},
          units={"b": "m", "c": "m", "fin_h": "m", "fin_c": "m", "tube_l": "m", "tube_d": "m", "pod": "m",
                 "a0": "deg", "cla": "1/rad"},
          assumes=["ASM-B1-DRAG", "ASM-B1-WING-ROUGH"], cites=["SRC-B2-AVL", "SRC-B2-XFOIL"])
def aero_build(b, c, tc, e_b2, e_pess, cd0_w, rough, cla, fin_h, fin_c, tube_l, tube_d, pod, n, drag, a0, clmax):
    cf_b, ff_f, cd_tube, cda_m, ff_pod, interf = drag
    S = b * c
    AR = b * b / S
    wet = 2.0 * (1.0 + 0.2 * tc)
    parts = {
        "wing": cd0_w * rough,
        "fins": cf_b * ff_f * wet * (2 * 2 * fin_h * fin_c) / S,
        "motor_tubes": 2 * cd_tube * tube_d * tube_l / S,
        "motors": n * cda_m / S,
        "pod": cf_b * ff_pod * 2 * (pod[0] * pod[1] + pod[0] * pod[2] + pod[1] * pod[2]) / S,
    }
    cd0 = interf * sum(parts.values())
    k = 1.0 / (math.pi * AR * e_b2)
    return {"S_m2": S, "AR": AR, "cd0": cd0, "k": k, "k_pess": 1.0 / (math.pi * AR * e_pess), "cla_per_rad": cla,
            "alpha_stall_deg": a0 + clmax / cla / DEG, "ld_max": 1 / (2 * math.sqrt(cd0 * k)),
            "cl_ldmax": math.sqrt(cd0 / k),
            "cd0_parts": [round(interf * parts[p], 6) for p in ("wing", "fins", "motor_tubes", "motors", "pod")]}


@kit.calc("CALC-B1-STALL", title="Stall and transition speeds",
          equation="Vs = sqrt(2 m g/(rho S CLmax)) ; Vt = 1.3 Vs ; Vs30 = Vs/sqrt(cos 30) ; "
                   "margin = Vcruise/Vt - 1",
          inputs={"m_gate": P + "requirements.mtow_gate_kg", "m_sized": "CL-A1-MASS-SIZED", "g": P + "env.g_ms2",
                  "rho": P + "env.rho_kgm3", "S": "CL-A1-WING-AREA", "clmax": "CL-B2-CLMAX-DESIGN",
                  "kt": P + "requirements.transition_factor", "vc": "ASM-B1-VCRUISE"},
          units={"m_gate": "kg", "m_sized": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2", "vc": "m/s"},
          assumes=["ASM-B1-VCRUISE"])
def stall_speeds(m_gate, m_sized, g, rho, S, clmax, kt, vc):
    vs = lambda m, cl: math.sqrt(2 * m * g / (rho * S * cl))
    v_gate = vs(m_gate, clmax)
    return {"vs_gate_ms": v_gate, "vs_sized_ms": vs(m_sized, clmax), "vt_gate_ms": kt * v_gate,
            "vs_bank30_gate_ms": v_gate / math.sqrt(math.cos(30 * DEG)),
            "vs_gate_clmax086_ms": vs(m_gate, 0.86), "vs_gate_clmax090_ms": vs(m_gate, 0.90),
            "clmax_needed_for_15ms": 2 * m_gate * g / (rho * S * (15.0 / kt) ** 2),
            "cruise_over_vt": vc / (kt * v_gate)}


@kit.calc("CALC-B1-PROPCAL", title="Prop and motor chain, calibrated to the maker table",
          equation="n_max = sqrt(T0/(Ct0 rho D^4)) (11x5.5MR) ; n_max,sag = n_max sqrt(sag) ; "
                   "k_cal = P_table(690 gf) / P_motor(11x4.5MR model at 690 gf, J = 0) ; "
                   "FM = T^1.5/(sqrt(2 rho A) P_shaft) (11x5.5MR)",
          inputs={"tab": "ASM-B1-PROP", "tab_ref": "ASM-B1-PROP-REF", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM",
                  "i0": "ASM-E1-I0", "table": P + "propulsion.thrust_table_g_w",
                  "t_max_kg": P + "propulsion.thrust_max_per_motor_kg", "sag": P + "propulsion.voltage_sag",
                  "D": P + "propulsion.prop_diameter_m", "rho": P + "env.rho_kgm3", "g": P + "env.g_ms2"},
          units={"t_max_kg": "kg", "D": "m", "rho": "kg/m3", "g": "m/s2"},
          assumes=["ASM-B1-PROP", "ASM-B1-PROP-REF", "ASM-E1-KV", "ASM-E1-RM", "ASM-E1-I0"])
def prop_calibration(tab, tab_ref, kv, rm, i0, table, t_max_kg, sag, D, rho, g):
    motor = (kv, rm, i0)
    ct0 = tab[0][1]
    n_max = math.sqrt(t_max_kg * g / (ct0 * rho * D ** 4))
    t_ref = sorted(table)[0]
    T = t_ref[0] / 1000.0 * g
    n, p_shaft, _ = prop_operating_point(tab_ref, T, 0.0, D, rho)
    p_model = motor_input_w(p_shaft, n, motor)
    n55, p55, _ = prop_operating_point(tab, T, 0.0, D, rho)
    fm = T ** 1.5 / math.sqrt(2 * rho * math.pi * D * D / 4) / p55
    return {"n_max_rps": n_max, "n_max_sag_rps": n_max * math.sqrt(sag), "k_cal": t_ref[1] / p_model,
            "hover_ref_rpm": n55 * 60, "fm_apc_static": fm, "motor_eff_hover_ref": p_shaft / p_model}


@kit.calc("CALC-B1-HOVER", title="Hover power, current, endurance and thrust headroom",
          equation="T_motor = m DL / n ; r = P_motor(11x5.5MR, T) / P_motor(11x4.5MR, T) ; "
                   "P = n P_table(T_motor) r / eta_esc + P_av ; I = P / V ; "
                   "t_hover = E (1 - reserve) / P ; throttle = m g DL / (n T_max sag)",
          inputs={"m_gate": P + "requirements.mtow_gate_kg", "m_sized": "CL-A1-MASS-SIZED",
                  "table": P + "propulsion.thrust_table_g_w", "dl": P + "propulsion.download_factor",
                  "n": P + "propulsion.n_motors", "esc": "ASM-B1-ESC", "av": "ASM-B1-AVIONICS-W",
                  "E": P + "battery.energy_wh", "v": P + "battery.v_nom", "res": P + "requirements.energy_reserve_frac",
                  "t_max_kg": P + "propulsion.thrust_max_per_motor_kg", "sag": P + "propulsion.voltage_sag",
                  "pess": "ASM-B1-PESS", "tab": "ASM-B1-PROP", "tab_ref": "ASM-B1-PROP-REF", "kv": "ASM-E1-KV",
                  "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "D": P + "propulsion.prop_diameter_m",
                  "rho": P + "env.rho_kgm3", "g": P + "env.g_ms2"},
          units={"m_gate": "kg", "m_sized": "kg", "av": "W", "E": "Wh", "v": "V", "t_max_kg": "kg", "D": "m",
                 "rho": "kg/m3", "g": "m/s2"},
          assumes=["ASM-B1-ESC", "ASM-B1-AVIONICS-W", "ASM-B1-PESS"])
def hover(m_gate, m_sized, table, dl, n, esc, av, E, v, res, t_max_kg, sag, pess, tab, tab_ref, kv, rm, i0, D, rho,
          g):
    motor = (kv, rm, i0)

    def ratio(m):
        T = m * g * dl / n
        n1, p1, _ = prop_operating_point(tab, T, 0.0, D, rho)
        n0, p0, _ = prop_operating_point(tab_ref, T, 0.0, D, rho)
        return motor_input_w(p1, n1, motor) / motor_input_w(p0, n0, motor)

    def p(m):
        return n * table_power_w(table, m * 1000 * dl / n) * ratio(m) / esc + av
    pg, ps = p(m_gate), p(m_sized)
    return {"p_gate_w": pg, "p_sized_w": ps, "i_gate_a": pg / v, "i_sized_a": ps / v,
            "p_gate_pess_w": pg * pess[2], "prop_ratio_55_45": ratio(m_gate),
            "hover_only_gate_min": E * (1 - res) / pg * 60, "hover_only_sized_min": E * (1 - res) / ps * 60,
            "throttle_frac_gate_sag": m_gate * dl / (n * t_max_kg * sag),
            "tw_gate_sag_download": n * t_max_kg * sag / (m_gate * dl)}


def cruise_point(V, m, g, rho, S, cd0, k, trim, n, tab, motor, kcal, D, esc, av, eta_fac=1.0):
    """Electrical power at level cruise airspeed V (pure helper)."""
    W = m * g
    cl = 2 * W / (rho * V * V * S)
    cd = cd0 + k * cl * cl
    drag = 0.5 * rho * V * V * S * cd * trim
    rps, p_shaft, eta = prop_operating_point(tab, drag / n, V, D, rho)
    p_shaft /= eta_fac
    p_el = n * kcal * motor_input_w(p_shaft, rps, motor) / esc + av
    return {"cl": cl, "ld": cl / cd, "drag_n": drag, "t_prop_n": drag / n, "J": V / (rps * D),
            "rpm": rps * 60, "eta_prop": eta * eta_fac, "p_shaft_w": n * p_shaft, "p_el_w": p_el,
            "eta_drive": n * p_shaft / (p_el - av)}


CRUISE_INPUTS = {"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                 "S": "CL-A1-WING-AREA", "cd0": "CL-B1-CD0", "k": "CL-B1-K", "k_pess": "CL-B1-K-PESS",
                 "trim": "ASM-B1-TRIM",
                 "n": P + "propulsion.n_motors", "tab": "ASM-B1-PROP", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "kcal": "CL-B1-KCAL",
                 "D": P + "propulsion.prop_diameter_m", "esc": "ASM-B1-ESC", "av": "ASM-B1-AVIONICS-W"}
CRUISE_UNITS = {"m": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2", "D": "m", "av": "W"}


@kit.calc("CALC-B1-CRUISE", title="Cruise at the proposed speed, gate mass",
          equation="CL = 2W/(rho V^2 S) ; D = q S (CD0 + k CL^2) trim ; prop: Ct(J) rho n^2 D^4 = D/n ; "
                   "P_el = n k_cal P_motor(Cp rho n^3 D^5) / eta_esc + P_av ; eta_drive = P_shaft / (P_el - P_av) ; "
                   "pess: CD0 x 1.3, k_pess (e 0.80), eta_prop x 0.85",
          inputs={**CRUISE_INPUTS, "vc": "ASM-B1-VCRUISE", "pess": "ASM-B1-PESS", "v": P + "battery.v_nom"},
          units={**CRUISE_UNITS, "vc": "m/s", "v": "V"},
          assumes=["ASM-B1-TRIM", "ASM-B1-VCRUISE", "ASM-B1-PESS", "ASM-B1-PROP", "ASM-E1-KV", "ASM-E1-RM", "ASM-E1-I0"])
def cruise(m, g, rho, S, cd0, k, k_pess, trim, n, tab, kv, rm, i0, kcal, D, esc, av, vc, pess, v):
    motor = (kv, rm, i0)
    base = cruise_point(vc, m, g, rho, S, cd0, k, trim, n, tab, motor, kcal, D, esc, av)
    worst = cruise_point(vc, m, g, rho, S, cd0 * pess[0], k_pess, trim, n, tab, motor, kcal, D, esc, av, pess[1])
    return {"cl": base["cl"], "ld": base["ld"], "drag_n": base["drag_n"], "t_prop_n": base["t_prop_n"],
            "J": base["J"], "rpm": base["rpm"], "eta_prop": base["eta_prop"], "p_shaft_w": base["p_shaft_w"],
            "eta_drive": base["eta_drive"], "p_el_w": base["p_el_w"],
            "i_a": base["p_el_w"] / v, "p_el_pess_w": worst["p_el_w"], "i_pess_a": worst["p_el_w"] / v,
            "drag_pess_n": worst["drag_n"], "eta_prop_pess": worst["eta_prop"],
            "eta_overall": base["drag_n"] * vc / base["p_el_w"]}


@kit.calc("CALC-B1-SWEEP", title="Cruise power and cruise time versus airspeed",
          equation="for V in 14..20 m/s: P_el(V) as CALC-B1-CRUISE ; t = (E(1-res) - P_h t_h - 2 E_tr)/P_el ; "
                   "pess: P_h and E_tr x 1.10 and the pessimistic P_el",
          inputs={**CRUISE_INPUTS, "pess": "ASM-B1-PESS", "E": P + "battery.energy_wh",
                  "res": P + "requirements.energy_reserve_frac", "p_hover": P + "performance.hover_power_w",
                  "t_hover": P + "requirements.hover_time_min", "e_tr": "CL-B1-TRANS-ENERGY",
                  "trans": "ASM-B1-TRANS"},
          units={**CRUISE_UNITS, "E": "Wh", "p_hover": "W", "t_hover": "min", "e_tr": "Wh"},
          assumes=["ASM-B1-PESS", "ASM-B1-TRANS"])
def cruise_sweep(m, g, rho, S, cd0, k, k_pess, trim, n, tab, kv, rm, i0, kcal, D, esc, av, pess, E, res, p_hover,
                 t_hover, e_tr, trans):
    motor = (kv, rm, i0)
    e_left = E * (1 - res) - p_hover * t_hover / 60 - e_tr * (1 + trans[2])
    e_left_p = E * (1 - res) - (p_hover * t_hover / 60 + e_tr * (1 + trans[2])) * pess[2]
    rows = []
    for v10 in range(140, 201, 5):
        V = v10 / 10
        b = cruise_point(V, m, g, rho, S, cd0, k, trim, n, tab, motor, kcal, D, esc, av)
        w = cruise_point(V, m, g, rho, S, cd0 * pess[0], k_pess, trim, n, tab, motor, kcal, D, esc, av, pess[1])
        rows.append([V, round(b["p_el_w"], 1), round(w["p_el_w"], 1), round(b["eta_prop"], 3),
                     round(e_left / b["p_el_w"] * 60, 2), round(e_left_p / w["p_el_w"] * 60, 2)])
    best = min(rows, key=lambda r: r[1])
    return {"rows_V_P_Ppess_eta_t_tpess": rows, "v_min_power_ms": best[0], "e_cruise_wh": e_left}


@kit.calc("CALC-B1-MISSION", title="Mission energy: 2 min hover, two transitions, cruise",
          equation="E_use = E (1 - reserve) ; E_c = E_use - P_hover t_hover - E_tr (1 + back) ; t_cruise = E_c / P_cruise ; "
                   "range = t_cruise V ; pess: P_hover and E_tr x 1.10, P_cruise,pess ; cross-check with B1 hover",
          inputs={"E": P + "battery.energy_wh", "res": P + "requirements.energy_reserve_frac",
                  "p_hover": P + "performance.hover_power_w", "pess": "ASM-B1-PESS",
                  "p_hover_b1": "CL-B1-HOVER-P-GATE",
                  "t_hover": P + "requirements.hover_time_min", "e_tr": "CL-B1-TRANS-ENERGY",
                  "trans": "ASM-B1-TRANS", "p_c": "CL-B1-CRUISE-P", "p_c_pess": "CL-B1-CRUISE-P-PESS",
                  "vc": "ASM-B1-VCRUISE"},
          units={"E": "Wh", "p_hover": "W", "p_hover_b1": "W", "t_hover": "min", "e_tr": "Wh", "p_c": "W",
                 "p_c_pess": "W", "vc": "m/s"},
          assumes=["ASM-B1-TRANS", "ASM-B1-PESS"])
def mission(E, res, p_hover, pess, p_hover_b1, t_hover, e_tr, trans, p_c, p_c_pess, vc):
    use = E * (1 - res)
    e_h = p_hover * t_hover / 60
    e_t = e_tr * (1 + trans[2])
    t_c = (use - e_h - e_t) / p_c * 60
    return {"e_usable_wh": use, "e_hover_wh": e_h, "e_transitions_wh": e_t, "t_cruise_min": t_c,
            "p_hover_pess_w": p_hover * pess[2],
            "t_cruise_pess_min": (use - (e_h + e_t) * pess[2]) / p_c_pess * 60,
            "t_cruise_b1_hover_min": (use - p_hover_b1 * t_hover / 60 - e_t) / p_c * 60,
            "range_km": t_c * 60 * vc / 1000.0, "e_cruise_wh": use - e_h - e_t}


@kit.calc("CALC-B1-CORRIDOR", title="Transition corridor, steady level flight",
          equation="for V in 0..22 m/s: T cos(th) = D(a=th), T sin(th) + L = W ; corridor th_lo..th_eq with "
                   "T = (W - L)/sin(th) <= f T_max(V cos a) ; P_el at T/n ; peaks taken over 0 <= V <= Vcruise",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "S": "CL-A1-WING-AREA", "cla": "CL-B1-CLA", "a0": P + "b2.xfoil.alpha0_2d_deg", "clmax": "CL-B2-CLMAX-DESIGN",
                  "cd0": "CL-B1-CD0", "k": "CL-B1-K", "cd90": "ASM-B1-CD90", "n": P + "propulsion.n_motors",
                  "tab": "ASM-B1-PROP", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "kcal": "CL-B1-KCAL", "nmax": "CL-B1-NMAX-SAG",
                  "D": P + "propulsion.prop_diameter_m", "esc": "ASM-B1-ESC", "av": "ASM-B1-AVIONICS-W",
                  "frac": "ASM-B1-CTRL-RESERVE", "dl": P + "propulsion.download_factor", "vc": "ASM-B1-VCRUISE"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2", "a0": "deg", "D": "m", "av": "W",
                 "nmax": "rev/s", "vc": "m/s"},
          assumes=["ASM-B1-CD90", "ASM-B1-CTRL-RESERVE"])
def corridor(m, g, rho, S, cla, a0, clmax, cd0, k, cd90, n, tab, kv, rm, i0, kcal, nmax, D, esc, av, frac, dl, vc):
    motor = (kv, rm, i0)
    W = m * g
    aero = aero_from(cla, a0, clmax, cd0, k, cd90)
    a_s = a0 + clmax / cla / DEG
    rows = []
    worst_frac, p_peak, v_peak, v_wing = 0.0, 0.0, 0.0, None
    for V in range(0, 23):
        th, T, a = level_equilibrium(float(V), W, rho, S, aero, a_s)
        if th is None:
            continue
        if V == 0:
            T = W * dl                     # hover: download on tube and fin, as in CALC-B1-HOVER
        va = max(0.0, V * math.cos(a * DEG))
        tmax = n * prop_tmax(tab, va, nmax, D, rho)
        if tmax <= T:                       # above the top speed: no level equilibrium on full thrust
            break
        rps, ps, _ = prop_operating_point(tab, T / n, va, D, rho)
        p_el = n * kcal * motor_input_w(ps, rps, motor) / esc + av
        q = 0.5 * rho * V * V * S
        th_lo = th
        t_ = th
        while t_ > 0.5:                     # lowest pitch still holding altitude within the thrust allowance
            t_ -= 0.25
            cl, _ = aero(t_)
            treq = (W - q * cl) / math.sin(t_ * DEG)
            if treq < 0 or treq > frac * tmax:
                break
            th_lo = t_
        rows.append([V, round(th, 2), round(th_lo, 2), round(T / W, 3), round(T / tmax, 3), round(p_el, 1),
                     1 if a > a_s else 0])
        if V > vc:                          # transition range only: hover to cruise speed
            continue
        worst_frac = max(worst_frac, T / tmax)
        if p_el > p_peak:
            p_peak, v_peak = p_el, V
        if v_wing is None and a <= a_s:
            v_wing = V
    lean = {}
    for vw in (5.0, 8.0):
        th, _, _ = level_equilibrium(vw, W, rho, S, aero, a_s)
        lean[vw] = 90.0 - th
    return {"rows_V_th_thlo_TW_Tfrac_P_stalled": rows, "thrust_frac_max": worst_frac, "p_peak_w": p_peak,
            "v_peak_ms": v_peak, "v_wing_unstalled_ms": v_wing, "alpha_stall_deg": a_s,
            "lean_5ms_lift_deg": lean[5.0], "lean_8ms_lift_deg": lean[8.0]}


@kit.calc("CALC-B1-PITCHOVER", title="Forward transition (pitch-over) time simulation",
          equation="m dv/dt = T(th) + L + D - W (2-D point mass, dt 0.01 s, semi-implicit Euler) ; "
                   "th_cmd = max(90 - r t, th_req(V)) ; T holds altitude below V_assist, speed above",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "S": "CL-A1-WING-AREA", "cla": "CL-B1-CLA", "a0": P + "b2.xfoil.alpha0_2d_deg", "clmax": "CL-B2-CLMAX-DESIGN",
                  "cd0": "CL-B1-CD0", "k": "CL-B1-K", "cd90": "ASM-B1-CD90", "n": P + "propulsion.n_motors",
                  "tab": "ASM-B1-PROP", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "kcal": "CL-B1-KCAL", "nmax": "CL-B1-NMAX-SAG",
                  "D": P + "propulsion.prop_diameter_m", "esc": "ASM-B1-ESC", "av": "ASM-B1-AVIONICS-W",
                  "frac": "ASM-B1-CTRL-RESERVE", "trans": "ASM-B1-TRANS", "vs": "CL-B1-VS-GATE",
                  "vc": "ASM-B1-VCRUISE", "kt": P + "requirements.transition_factor"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2", "a0": "deg", "D": "m", "av": "W",
                 "nmax": "rev/s", "vs": "m/s", "vc": "m/s"},
          assumes=["ASM-B1-TRANS", "ASM-B1-CD90", "ASM-B1-CTRL-RESERVE"])
def pitchover(m, g, rho, S, cla, a0, clmax, cd0, k, cd90, n, tab, kv, rm, i0, kcal, nmax, D, esc, av, frac, trans, vs,
              vc, kt):
    motor = (kv, rm, i0)
    return simulate_pitchover(m, g, rho, S, cla, a0, clmax, cd0, k, cd90, n, tab, kv, rm, i0, kcal, nmax, D, esc, av,
                              frac, trans, vs, vc, kt)["summary"]


def simulate_pitchover(m, g, rho, S, cla, a0, clmax, cd0, k, cd90, n, tab, kv, rm, i0, kcal, nmax, D, esc, av, frac,
                       trans, vs, vc, kt, dt=0.01, t_end=20.0):
    motor = (kv, rm, i0)
    aero = aero_from(cla, a0, clmax, cd0, k, cd90)
    W = m * g
    rate, v_assist = trans[0], trans[1] * vs
    u = w = h = 0.0
    th = 90.0
    t = 0.0
    e_j = 0.0
    T = W
    hist = []
    h_min = h_max = 0.0
    t_vt = t_vc = None
    tf_max = 0.0
    kp, kd, kv = 1.0, 2.0, 0.8
    while t < t_end:
        V = math.hypot(u, w)
        gam = math.atan2(w, u) / DEG if V > 0.05 else 0.0
        a = th - gam
        cl, cd = aero(a)
        q = 0.5 * rho * V * V * S
        L, Dr = q * cl, q * cd
        lx, lz = -L * math.sin(gam * DEG), L * math.cos(gam * DEG)
        dx, dz = -Dr * math.cos(gam * DEG), -Dr * math.sin(gam * DEG)
        va = max(0.0, V * math.cos(a * DEG))
        tmax = n * prop_tmax(tab, va, nmax, D, rho)
        s, c = math.sin(th * DEG), math.cos(th * DEG)
        if V < v_assist:
            treq = (m * (g - kp * h - kd * w) - lz - dz) / max(s, 0.05)
        else:
            treq = (m * kv * (vc - V) - lx - dx) / max(c, 0.05)
        T = min(max(treq, 0.0), tmax)
        tf_max = max(tf_max, T / tmax)
        ax = (T * c + lx + dx) / m
        az = (T * s + lz + dz) / m - g
        u += ax * dt
        w += az * dt
        h += w * dt
        # pitch command: scheduled pitch-down, but never below what wing + thrust need to hold altitude
        q2 = 0.5 * rho * (u * u + w * w) * S
        th_req = 90.0
        aa = a0
        while aa < 90.0:
            cl2, _ = aero(aa)
            if q2 * cl2 + frac * tmax * math.sin(aa * DEG) >= W:
                th_req = aa
                break
            aa += 0.5
        th_cmd = max(90.0 - rate * (t + dt), th_req)
        step = rate * dt
        th = th + max(-step, min(step, th_cmd - th))
        rps, ps, _ = prop_operating_point(tab, T / n, va, D, rho)
        e_j += (n * kcal * motor_input_w(ps, rps, motor) / esc + av) * dt
        t += dt
        h_min, h_max = min(h_min, h), max(h_max, h)
        Vn = math.hypot(u, w)
        if t_vt is None and Vn >= kt * vs:
            t_vt = t
        if t_vc is None and Vn >= vc - 0.3:
            t_vc = t
            e_vc = e_j
        if int(round(t / dt)) % 10 == 0:
            hist.append([round(t, 2), round(Vn, 2), round(th, 1), round(a, 1), round(h, 2), round(T / W, 3)])
        if t_vc is not None and t > t_vc + 2.0:
            break
    summary = {"t_to_vt_s": t_vt if t_vt is not None else -1.0, "t_to_cruise_s": t_vc if t_vc is not None else -1.0,
               "alt_loss_m": -h_min, "alt_gain_m": h_max, "thrust_frac_max": tf_max,
               "energy_wh": (e_vc if t_vc is not None else e_j) / 3600.0}
    return {"summary": summary, "history_t_V_th_a_h_TW": hist}


@kit.calc("CALC-B1-WIND", title="Hover lean, wind limits, landing and ground tip-over",
          equation="lean = atan(0.5 rho V^2 S CD90 / W) ; lean_allowed = tipover - err ; "
                   "V_hover,max: lean = lean_allowed ; T/W at 8 m/s = 1/cos(lean) ; "
                   "V_ground,tip = sqrt(2 m_min g z_fin / (h_cp rho S CD90)), h_cp = c/2 + foot",
          inputs={"m": P + "requirements.mtow_gate_kg", "m_sized": "CL-A1-MASS-SIZED",
                  "growth": P + "mass.growth_reserve_g", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "S": "CL-A1-WING-AREA", "cd90": "ASM-B1-CD90", "tip": "CL-A1-TIPOVER", "err": "ASM-B1-LAND-ERR",
                  "z_fin": P + "fins.half_height_m", "c": P + "wing.chord_m", "foot": P + "cg.foot_height_m",
                  "tw_sag": "CL-B1-HOVER-TW-SAG", "frac": "ASM-B1-CTRL-RESERVE",
                  "vw": P + "requirements.wind_limit_ms", "vg": P + "requirements.gust_survive_ms",
                  "vc": "ASM-B1-VCRUISE"},
          units={"m": "kg", "m_sized": "kg", "growth": "g", "g": "m/s2", "rho": "kg/m3", "S": "m2", "tip": "deg",
                 "err": "deg", "z_fin": "m", "c": "m", "foot": "m", "vw": "m/s", "vg": "m/s", "vc": "m/s"},
          assumes=["ASM-B1-CD90", "ASM-B1-LAND-ERR", "ASM-B1-CTRL-RESERVE"])
def wind(m, m_sized, growth, g, rho, S, cd90, tip, err, z_fin, c, foot, tw_sag, frac, vw, vg, vc):
    W = m * g
    lean = lambda V: math.atan(0.5 * rho * V * V * S * cd90 / W) / DEG
    allowed = tip - err
    v_max = math.sqrt(2 * W * math.tan(allowed * DEG) / (rho * S * cd90))
    m_min = m_sized - growth / 1000.0
    h_cp = c / 2 + foot
    return {"lean_5ms_deg": lean(vw), "lean_8ms_deg": lean(vg), "lean_allowed_deg": allowed,
            "v_hover_max_ms": v_max, "tw_needed_8ms": 1 / math.cos(lean(vg) * DEG),
            "thrust_frac_8ms": 1 / math.cos(lean(vg) * DEG) / tw_sag,
            "v_ground_tip_ms": math.sqrt(2 * m_min * g * z_fin / (h_cp * rho * S * cd90)),
            "groundspeed_upwind_ms": vc - vw, "m_min_kg": m_min}


@kit.calc("CALC-B1-CLIMB", title="Vertical climb, fixed-wing climb and top speed",
          equation="VTOL: T = W DL + q S_front CD0 at Vc, prop at J = Vc/(nD) ; FW: ROC = (n T_max(V) f - D) V / W ; "
                   "V_max: n T_max(V) = D(V)",
          inputs={**CRUISE_INPUTS, "vc": "ASM-B1-VCRUISE", "nmax": "CL-B1-NMAX-SAG", "frac": "ASM-B1-CTRL-RESERVE",
                  "dl": P + "propulsion.download_factor"},
          units={**CRUISE_UNITS, "vc": "m/s", "nmax": "rev/s"},
          assumes=["ASM-B1-CTRL-RESERVE"])
def climb(m, g, rho, S, cd0, k, k_pess, trim, n, tab, kv, rm, i0, kcal, D, esc, av, vc, nmax, frac, dl):
    motor = (kv, rm, i0)
    W = m * g
    v_up = 2.5                                            # Q_PILOT_SPD_UP-class vertical climb, m/s
    T_up = W * dl + 0.5 * rho * v_up ** 2 * S * cd0       # nose-first climb: wing edge-on, cruise-like drag
    rps, ps, _ = prop_operating_point(tab, T_up / n, v_up, D, rho)
    p_up = n * kcal * motor_input_w(ps, rps, motor) / esc + av

    def drag(V):
        cl = 2 * W / (rho * V * V * S)
        return 0.5 * rho * V * V * S * (cd0 + k * cl * cl) * trim
    roc = (frac * n * prop_tmax(tab, vc, nmax, D, rho) - drag(vc)) * vc / W
    vmax = None
    V = vc
    while V < 40:
        if n * prop_tmax(tab, V, nmax, D, rho) < drag(V):
            vmax = V
            break
        V += 0.05
    return {"p_vclimb_2p5_w": p_up, "roc_fw_max_ms": roc, "climb_angle_fw_deg": math.asin(min(1.0, roc / vc)) / DEG,
            "v_max_level_ms": vmax if vmax else 40.0}


# ================================================================== claims
kit.claim("CL-B1-CD0", "Zero-lift drag coefficient", calc="CALC-B1-AERO", output="cd0", unit="-",
          how="B2/B3 AVL + XFOIL profile drag; flight: glide or power-off sink at 16 m/s, or cruise power at "
              "known prop data (H2).")
kit.claim("CL-B1-K", "Lift-dependent drag factor (B2 trimmed polar, e 0.93)", calc="CALC-B1-AERO", output="k",
          unit="-", how="B2/B3 re-run AVL at c 0.32 with fins and pod; flight: cruise power at 14/16/18 m/s (H2).")
kit.claim("CL-B1-K-PESS", "Lift-dependent drag factor, pessimistic (e 0.80)", calc="CALC-B1-AERO",
          output="k_pess", unit="-", how="As CL-B1-K.")
kit.claim("CL-B1-CLA", "Wing lift slope (B2 AVL, c 0.30 run)", calc="CALC-B1-AERO", output="cla_per_rad",
          unit="1/rad", how="B3 AVL CLa with fins and pod at c 0.32.")
kit.claim("CL-B1-LDMAX", "Maximum lift-to-drag ratio", calc="CALC-B1-AERO", output="ld_max", unit="-",
          how="Glide test at best-glide speed with airspeed and baro logged (H2).")
kit.claim("CL-B1-ALPHA-STALL", "Wing stall angle of attack", calc="CALC-B1-AERO", output="alpha_stall_deg",
          unit="deg", how="B2 XFOIL CLmax and AVL; tuft the twin at slow flight.")

kit.claim("CL-B1-VS-GATE", "Stall speed at 2.6 kg", calc="CALC-B1-STALL", output="vs_gate_ms", unit="m/s",
          limit=("<=", P + "requirements.stall_max_ms"), verifies=["R-STALL"],
          how="B2 trimmed CLmax 0.80 (XFOIL + AVL); flight: slow-flight stall in FBWA at >= 50 m with airspeed "
              "logged (H2, T-B2-STALL).")
kit.claim("CL-B1-VS-SIZED", "Stall speed at sized mass", calc="CALC-B1-STALL", output="vs_sized_ms", unit="m/s",
          limit=("<=", P + "requirements.stall_max_ms"), verifies=["R-STALL"],
          how="As CL-B1-VS-GATE at the weighed mass.")
kit.claim("CL-B1-VT-GATE", "Transition-complete airspeed 1.3 Vs", calc="CALC-B1-STALL", output="vt_gate_ms",
          unit="m/s", limit=("<=", "ASM-B1-VCRUISE"), verifies=["R-TRANSITION"],
          how="16 m/s cruise (D-01) over 1.3 Vs with B2's trimmed CLmax 0.80 at c 0.32. Log airspeed at "
              "'Transition done' (F4/H2).")
kit.claim("CL-B1-CLMAX-FOR-15", "CLmax that would keep 15 m/s cruise", calc="CALC-B1-STALL",
          output="clmax_needed_for_15ms", unit="-",
          how="B2 compares with the XFOIL/AVL CLmax with elevon up-trim; if B2 shows >= this value, 15 m/s also passes.")

kit.claim("CL-B1-NMAX-SAG", "Prop speed at full throttle, sagged", calc="CALC-B1-PROPCAL", output="n_max_sag_rps",
          unit="rev/s", how="Thrust stand at 14.0 V, full throttle, optical tachometer (H1, T-A1-THRUST-STATION).")
kit.claim("CL-B1-KCAL", "Chain calibration to the maker table", calc="CALC-B1-PROPCAL", output="k_cal", unit="-",
          how="Thrust stand: measured W at 690 gf replaces the maker point; k_cal re-derives (H1).")
kit.claim("CL-B1-FM", "Prop figure of merit, static (APC)", calc="CALC-B1-PROPCAL", output="fm_apc_static",
          unit="-", how="Thrust stand gf and shaft W (from current, Kv, Rm) at hover thrust (H1).")

kit.claim("CL-B1-HOVER-P-GATE", "Hover power at 2.6 kg, 11x5.5MR (B1 cross-check of E1)", calc="CALC-B1-HOVER",
          output="p_gate_w", unit="W", limit=("<=", P + "performance.hover_power_w"),
          how="Tethered hover at the gate mass (ballast), log pack W for 60 s (H2); thrust stand first (H1).")
kit.claim("CL-B1-HOVER-P-PESS", "Hover power at 2.6 kg, pessimistic", calc="CALC-B1-HOVER", output="p_gate_pess_w",
          unit="W", how="As CL-B1-HOVER-P-GATE.")
kit.claim("CL-B1-HOVER-I-GATE", "Hover current at 2.6 kg", calc="CALC-B1-HOVER", output="i_gate_a", unit="A",
          how="Current sensor log in tethered hover; F1 sizes the disconnect on it (x 1.25).")
kit.claim("CL-B1-HOVER-PROP-RATIO", "Hover power ratio 11x5.5MR / 11x4.5MR", calc="CALC-B1-HOVER",
          output="prop_ratio_55_45", unit="-", how="Thrust stand A/B of both props at 690 gf (H1, CR-B1-06).")
kit.claim("CL-B1-HOVER-ONLY", "Hover-only endurance, 20 % reserve", calc="CALC-B1-HOVER",
          output="hover_only_gate_min", unit="min", how="Not flown; follows from the measured hover power.")
kit.claim("CL-B1-HOVER-THROTTLE", "Hover thrust fraction, sagged pack", calc="CALC-B1-HOVER",
          output="throttle_frac_gate_sag", unit="-", limit=("<=", 0.6), verifies=["R-HOVER-TW"],
          how="Hover throttle in the log (MOT_THST_HOVER learned) at the gate mass and low pack (F4/H2).")
kit.claim("CL-B1-HOVER-TW-SAG", "Hover T/W with sag and download", calc="CALC-B1-HOVER",
          output="tw_gate_sag_download", unit="-", limit=(">=", P + "requirements.hover_tw_min_sag"),
          verifies=["R-HOVER-TW"], how="Thrust stand at 14.0 V; download from B4 or a tethered hover.")

kit.claim("CL-B1-CRUISE-P", "Cruise electrical power, 16 m/s, 2.6 kg", calc="CALC-B1-CRUISE", output="p_el_w",
          unit="W", verifies=["R-MISSION"],
          how="Level cruise at 16 m/s for 60 s, pack W logged, both directions on a calm morning (H2).")
kit.claim("CL-B1-CRUISE-P-PESS", "Cruise power, pessimistic", calc="CALC-B1-CRUISE", output="p_el_pess_w",
          unit="W", how="As CL-B1-CRUISE-P.")
kit.claim("CL-B1-CRUISE-I", "Cruise current", calc="CALC-B1-CRUISE", output="i_a", unit="A",
          how="Current sensor in cruise (H2).")
kit.claim("CL-B1-CRUISE-LD", "Cruise L/D at 16 m/s", calc="CALC-B1-CRUISE", output="ld", unit="-",
          how="Follows from CD0 and k; glide test.")
kit.claim("CL-B1-CRUISE-DRAG", "Cruise drag at 16 m/s, 2.6 kg", calc="CALC-B1-CRUISE", output="drag_n", unit="N",
          how="Follows from CD0, k and trim; cruise power test with known prop data (H2).")
kit.claim("CL-B1-CRUISE-DRAG-PESS", "Cruise drag, pessimistic", calc="CALC-B1-CRUISE", output="drag_pess_n",
          unit="N", how="As CL-B1-CRUISE-DRAG.")
kit.claim("CL-B1-CRUISE-P-SHAFT", "Cruise shaft power, 4 props", calc="CALC-B1-CRUISE", output="p_shaft_w",
          unit="W", how="ESC telemetry current and rpm with E1's motor constants (H2).")
kit.claim("CL-B1-CRUISE-ETA-DRIVE", "Motor + ESC + calibration efficiency in cruise", calc="CALC-B1-CRUISE",
          output="eta_drive", unit="-", how="Thrust stand at cruise rpm and torque (H1); replaces E2's eta_motor 0.72.")
kit.claim("CL-B1-CRUISE-I-PESS", "Cruise current, pessimistic", calc="CALC-B1-CRUISE", output="i_pess_a", unit="A",
          how="Current sensor in cruise (H2).")
kit.claim("CL-B1-CRUISE-ETA-PROP", "Prop efficiency in cruise", calc="CALC-B1-CRUISE", output="eta_prop", unit="-",
          how="B4 confirms from APC data and a car-top or wind-tunnel prop test; flight: rpm (ESC telemetry) vs airspeed.")
kit.claim("CL-B1-CRUISE-J", "Cruise advance ratio", calc="CALC-B1-CRUISE", output="J", unit="-",
          how="ESC telemetry rpm and airspeed in cruise.")

kit.claim("CL-B1-V-MINPOWER", "Lowest-power cruise speed in 14-20 m/s", calc="CALC-B1-SWEEP",
          output="v_min_power_ms", unit="m/s", how="Cruise power at 14, 16, 18 m/s on one flight (H2).")

kit.claim("CL-B1-CRUISE-TIME", "Cruise after 2 min hover, 20 % reserve", calc="CALC-B1-MISSION",
          output="t_cruise_min", unit="min", limit=(">=", P + "requirements.cruise_time_min"), verifies=["R-MISSION"],
          how="Fly the mission profile at the gate mass; land with >= 20 % by the pack's mAh count (H2).")
kit.claim("CL-B1-CRUISE-TIME-PESS", "Cruise after hover, pessimistic", calc="CALC-B1-MISSION",
          output="t_cruise_pess_min", unit="min", limit=(">=", P + "requirements.cruise_time_min"),
          verifies=["R-MISSION"], how="As CL-B1-CRUISE-TIME.")
kit.claim("CL-B1-CRUISE-TIME-B1H", "Cruise after hover with B1's own hover power", calc="CALC-B1-MISSION",
          output="t_cruise_b1_hover_min", unit="min", limit=(">=", P + "requirements.cruise_time_min"),
          how="As CL-B1-CRUISE-TIME; cross-check of the E1 hover figure.")
kit.claim("CL-B1-CRUISE-ENERGY", "Energy left for cruise after hover and transitions", calc="CALC-B1-MISSION",
          output="e_cruise_wh", unit="Wh", how="Pack Wh counter at the end of the hover and transition legs (H2).")

kit.claim("CL-B1-CORR-THRUST", "Peak steady thrust fraction in transition", calc="CALC-B1-CORRIDOR",
          output="thrust_frac_max", unit="-", limit=("<=", "ASM-B1-CTRL-RESERVE"), verifies=["R-TRANSITION"],
          how="Throttle output in the transition log stays below 80 % with no motor saturation flag (F4 SITL, H2).")
kit.claim("CL-B1-CORR-P-PEAK", "Peak steady power in transition", calc="CALC-B1-CORRIDOR", output="p_peak_w",
          unit="W", how="Pack W in the transition log (H2).")
kit.claim("CL-B1-V-WINGBORNE", "Speed where the unstalled wing holds level", calc="CALC-B1-CORRIDOR",
          output="v_wing_unstalled_ms", unit="m/s", how="Angle of attack (pitch minus flight-path) and airspeed in the transition log.")
kit.claim("CL-B1-LEAN-5MS-LIFT", "Hover lean at 5 m/s, wing lift counted", calc="CALC-B1-CORRIDOR",
          output="lean_5ms_lift_deg", unit="deg", how="QLOITER in measured 5 m/s wind: log pitch (H2, twin first).")

kit.claim("CL-B1-TRANS-TIME", "Pitch-over time to 1.3 Vs", calc="CALC-B1-PITCHOVER", output="t_to_vt_s", unit="s",
          how="F4 SITL with the tailsitter model at these masses; then the twin's log.")
kit.claim("CL-B1-TRANS-ALT-LOSS", "Altitude lost in the pitch-over", calc="CALC-B1-PITCHOVER", output="alt_loss_m",
          unit="m", limit=("<=", 10.0), verifies=["R-TRANSITION"],
          how="Baro altitude in the transition log; first transitions at >= 50 m (H2). Limit 10 m = 20 % of 50 m.")
kit.claim("CL-B1-TRANS-THRUST", "Peak thrust fraction in the pitch-over", calc="CALC-B1-PITCHOVER",
          output="thrust_frac_max", unit="-", limit=("<=", "ASM-B1-CTRL-RESERVE"), verifies=["R-TRANSITION"], how="Throttle output in the transition log (H2).")
kit.claim("CL-B1-TRANS-ENERGY", "Energy of one pitch-over", calc="CALC-B1-PITCHOVER", output="energy_wh", unit="Wh",
          how="Integrate pack W over the transition in the log.")

kit.claim("CL-B1-LEAN-ALLOWED", "Wind lean allowed at touchdown", calc="CALC-B1-WIND", output="lean_allowed_deg",
          unit="deg", how="Tilt-board tip-over test (C5) minus the landing attitude error from the twin's logs.")
kit.claim("CL-B1-LEAN-5MS", "Hover lean at 5 m/s, flat plate", calc="CALC-B1-WIND", output="lean_5ms_deg",
          unit="deg", limit=("<=", "CL-B1-LEAN-ALLOWED"), verifies=["R-WIND"],
          how="QLOITER in 5 m/s wind measured with the handheld anemometer; log pitch and roll (H2).")
kit.claim("CL-B1-WIND-HOVER-MAX", "Steady wind for a safe fin-tip landing", calc="CALC-B1-WIND",
          output="v_hover_max_ms", unit="m/s", limit=(">=", P + "requirements.wind_limit_ms"), verifies=["R-WIND"],
          how="As CL-B1-LEAN-5MS; flight card stays at 5 m/s.")
kit.claim("CL-B1-GUST-8-THRUST", "Thrust fraction holding 8 m/s gust lean", calc="CALC-B1-WIND",
          output="thrust_frac_8ms", unit="-", limit=("<=", "ASM-B1-CTRL-RESERVE"), verifies=["R-WIND"],
          how="Thrust stand T/W (H1) and the 8 m/s lean from the logs.")
kit.claim("CL-B1-GROUND-TIP-WIND", "Wind that tips the parked aircraft", calc="CALC-B1-WIND",
          output="v_ground_tip_ms", unit="m/s", limit=(">=", P + "requirements.gust_survive_ms"),
          verifies=["R-WIND", "R-TIPOVER"],
          how="Tilt-board tip angle (C5) and a fan test at the lightest flying mass; never leave it standing disarmed in gusts.")

kit.claim("CL-B1-VCLIMB-P", "Power in a 2.5 m/s vertical climb", calc="CALC-B1-CLIMB", output="p_vclimb_2p5_w",
          unit="W", how="Pack W during QHOVER climbs (H2).")
kit.claim("CL-B1-ROC-FW", "Fixed-wing climb rate at 16 m/s", calc="CALC-B1-CLIMB", output="roc_fw_max_ms",
          unit="m/s", how="Full-throttle climb at 16 m/s in FBWA (H2); TECS limits set below it (F4).")
kit.claim("CL-B1-VMAX", "Top level speed (prop runs out)", calc="CALC-B1-CLIMB", output="v_max_level_ms",
          unit="m/s", limit=(">=", 18.0),
          how="Full-throttle level run in FBWA at altitude (H2); AIRSPEED_MAX set 2 m/s below it (F4). Limit 18 m/s "
              "= cruise 16 + 2 m/s speed-hold headroom.")

kit.test("T-B1-CRUISE-POWER", "Cruise power and speed polar", verifies=["CL-B1-CRUISE-P", "CL-B1-CD0", "CL-B1-V-MINPOWER"],
         state="planned", procedure="Twin, then the aircraft: 60 s level legs at 14, 16, 18 m/s both directions, "
                                    "calm morning, log airspeed, pack V and A, ESC rpm (H2).")
kit.test("T-B1-TETHER-HOVER", "Tethered hover power", verifies=["CL-B1-HOVER-P-GATE", "CL-B1-HOVER-THROTTLE"],
         state="planned", procedure="Gate mass by ballast, 60 s tethered hover at 1 m, log pack W and throttle (H2).")
kit.test("T-B1-TRANSITION-LOG", "First transitions logged", verifies=["CL-B1-TRANS-ALT-LOSS", "CL-B1-TRANS-TIME",
                                                                      "CL-B1-CORR-THRUST"],
         state="planned", procedure="At >= 50 m, calm: transition to FBWA, log airspeed, pitch, altitude, throttle (H2).")


# ================================================================== report outputs (not part of the chain)
def svg_corridor(rows, vs, vt, vc, a_s, path):
    W_, H_ = 1200, 620
    x0, y0, x1, y1 = 90, 40, 1150, 540
    vx = lambda v: x0 + (x1 - x0) * v / 22.0
    ty = lambda th: y1 - (y1 - y0) * th / 90.0
    fg, fg2, fg3, line3, acc, accw = "#121619", "#4B5563", "#6B7280", "#9AA4B1", "#1F5FC7", "#E6EEFB"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_} {H_}" font-family="IBM Plex Sans, system-ui, sans-serif">']
    up = " ".join(f"{vx(r[0]):.1f},{ty(r[1]):.1f}" for r in rows)
    lo = " ".join(f"{vx(r[0]):.1f},{ty(r[2]):.1f}" for r in reversed(rows))
    o.append(f'<polygon points="{up} {lo}" fill="{accw}" stroke="none"/>')
    for th in range(0, 91, 15):
        o.append(f'<line x1="{x0}" y1="{ty(th):.1f}" x2="{x1}" y2="{ty(th):.1f}" stroke="#E3E7ED" stroke-width="0.75"/>')
        o.append(f'<text x="{x0 - 10}" y="{ty(th) + 4:.1f}" font-size="12" font-family="IBM Plex Mono, monospace" '
                 f'fill="{fg3}" text-anchor="end">{th}°</text>')
    for v in range(0, 23, 2):
        o.append(f'<text x="{vx(v):.1f}" y="{y1 + 20}" font-size="12" font-family="IBM Plex Mono, monospace" '
                 f'fill="{fg3}" text-anchor="middle">{v}</text>')
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{line3}" stroke-width="1"/>')
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{line3}" stroke-width="1"/>')
    o.append(f'<text x="{(x0 + x1) / 2}" y="{y1 + 46}" font-size="12" fill="{fg2}" text-anchor="middle">airspeed (m/s)</text>')
    o.append(f'<text x="24" y="{(y0 + y1) / 2}" font-size="12" fill="{fg2}" text-anchor="middle" '
             f'transform="rotate(-90 24 {(y0 + y1) / 2})">pitch above horizon (deg)</text>')
    o.append(f'<line x1="{x0}" y1="{ty(a_s):.1f}" x2="{x1}" y2="{ty(a_s):.1f}" stroke="{line3}" stroke-width="0.75" stroke-dasharray="6 4"/>')
    o.append(f'<text x="{x1 - 4}" y="{ty(a_s) - 6:.1f}" font-size="11" fill="{fg3}" text-anchor="end">wing stall angle {a_s:.1f}°</text>')
    for v, lab in ((vs, "Vs"), (vt, "1.3 Vs"), (vc, "cruise")):
        o.append(f'<line x1="{vx(v):.1f}" y1="{y0}" x2="{vx(v):.1f}" y2="{y1}" stroke="{fg3}" stroke-width="0.75"/>')
        o.append(f'<text x="{vx(v) + 4:.1f}" y="{y0 + 12}" font-size="11" fill="{fg3}">{lab} '
                 f'<tspan font-family="IBM Plex Mono, monospace">{v:.1f}</tspan></text>')
    o.append(f'<polyline points="{up}" fill="none" stroke="{acc}" stroke-width="2"/>')
    for r in rows:
        if r[0] in (0, 3, 6, 9, 12, 15, 18, 21):
            o.append(f'<circle cx="{vx(r[0]):.1f}" cy="{ty(r[1]):.1f}" r="3" fill="{acc}"/>')
            o.append(f'<text x="{vx(r[0]) + 6:.1f}" y="{ty(r[1]) - 8:.1f}" font-size="12" '
                     f'font-family="IBM Plex Mono, monospace" fill="{fg}">{r[5]:.0f} W</text>')
    o.append("</svg>")
    Path(path).write_text("\n".join(o) + "\n", encoding="utf-8")


def svg_endurance(rows, vt, t_req, path):
    W_, H_ = 1200, 560
    x0, y0, x1, y1 = 90, 30, 1150, 480
    vmin, vmax = 14.0, 20.0
    tmax = max(r[4] for r in rows) * 1.15
    vx = lambda v: x0 + (x1 - x0) * (v - vmin) / (vmax - vmin)
    ty = lambda t: y1 - (y1 - y0) * t / tmax
    fg, fg2, fg3, line3, acc, fail = "#121619", "#4B5563", "#6B7280", "#9AA4B1", "#1F5FC7", "#B42323"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_} {H_}" font-family="IBM Plex Sans, system-ui, sans-serif">']
    step = 5 if tmax > 20 else 2
    for t in range(0, int(tmax) + 1, step):
        o.append(f'<line x1="{x0}" y1="{ty(t):.1f}" x2="{x1}" y2="{ty(t):.1f}" stroke="#E3E7ED" stroke-width="0.75"/>')
        o.append(f'<text x="{x0 - 10}" y="{ty(t) + 4:.1f}" font-size="12" font-family="IBM Plex Mono, monospace" '
                 f'fill="{fg3}" text-anchor="end">{t}</text>')
    for v in range(14, 21):
        o.append(f'<text x="{vx(v):.1f}" y="{y1 + 20}" font-size="12" font-family="IBM Plex Mono, monospace" '
                 f'fill="{fg3}" text-anchor="middle">{v}</text>')
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{line3}" stroke-width="1"/>')
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{line3}" stroke-width="1"/>')
    o.append(f'<text x="{(x0 + x1) / 2}" y="{y1 + 46}" font-size="12" fill="{fg2}" text-anchor="middle">cruise airspeed (m/s)</text>')
    o.append(f'<text x="24" y="{(y0 + y1) / 2}" font-size="12" fill="{fg2}" text-anchor="middle" '
             f'transform="rotate(-90 24 {(y0 + y1) / 2})">cruise after 2 min hover (min)</text>')
    o.append(f'<rect x="{x0}" y="{y0}" width="{vx(vt) - x0:.1f}" height="{y1 - y0}" fill="#FBE4E4" opacity="0.6"/>')
    o.append(f'<text x="{x0 + 6}" y="{y0 + 16}" font-size="11" fill="{fail}">below 1.3 Vs ({vt:.2f} m/s): FAIL</text>')
    o.append(f'<line x1="{x0}" y1="{ty(t_req):.1f}" x2="{x1}" y2="{ty(t_req):.1f}" stroke="{fg3}" stroke-width="0.75" stroke-dasharray="6 4"/>')
    o.append(f'<text x="{x1 - 4}" y="{ty(t_req) - 6:.1f}" font-size="11" fill="{fg3}" text-anchor="end">required {t_req:.0f} min</text>')
    base = " ".join(f"{vx(r[0]):.1f},{ty(r[4]):.1f}" for r in rows)
    pess = " ".join(f"{vx(r[0]):.1f},{ty(r[5]):.1f}" for r in rows)
    o.append(f'<polyline points="{base}" fill="none" stroke="{acc}" stroke-width="2"/>')
    o.append(f'<polyline points="{pess}" fill="none" stroke="{fg2}" stroke-width="1.5" stroke-dasharray="6 4"/>')
    o.append(f'<text x="{vx(rows[0][0]) + 6:.1f}" y="{ty(rows[0][4]) - 8:.1f}" font-size="12" fill="{acc}">base</text>')
    o.append(f'<text x="{vx(rows[0][0]) + 6:.1f}" y="{ty(rows[0][5]) + 18:.1f}" font-size="12" fill="{fg2}">pessimistic</text>')
    for r in rows:
        if r[0] in (15.0, 16.0, 18.0, 20.0):
            o.append(f'<circle cx="{vx(r[0]):.1f}" cy="{ty(r[4]):.1f}" r="3" fill="{acc}"/>')
            o.append(f'<text x="{vx(r[0]) + 6:.1f}" y="{ty(r[4]) - 8:.1f}" font-size="12" '
                     f'font-family="IBM Plex Mono, monospace" fill="{fg}">{r[4]:.1f} min · {r[1]:.0f} W</text>')
    o.append("</svg>")
    Path(path).write_text("\n".join(o) + "\n", encoding="utf-8")


if __name__ == "__main__":
    kit.write()
    claims = {n["id"]: n for n in json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["nodes"]}
    calcs = {k: v for k, v in claims.items() if v["type"] == "calculation"}
    corr = calcs["CALC-B1-CORRIDOR"]["outputs"]
    sweep = calcs["CALC-B1-SWEEP"]["outputs"]
    st = calcs["CALC-B1-STALL"]["outputs"]
    pv = calcs["CALC-B1-PITCHOVER"]["input_values"]
    hist = simulate_pitchover(**pv)["history_t_V_th_a_h_TW"]
    out = {"_note": "Written by team/B1/performance.py; tables for PERFORMANCE.md. Not read by the proof chain.",
           "corridor_cols": ["V m/s", "pitch_eq deg", "pitch_lo deg", "T/W", "T/Tmax", "P_el W", "wing stalled"],
           "corridor": corr["rows_V_th_thlo_TW_Tfrac_P_stalled"],
           "sweep_cols": ["V m/s", "P_el W", "P_el pess W", "eta_prop", "t_cruise min", "t_cruise pess min"],
           "sweep": sweep["rows_V_P_Ppess_eta_t_tpess"],
           "pitchover_cols": ["t s", "V m/s", "pitch deg", "alpha deg", "h m", "T/W"],
           "pitchover": hist,
           "outputs": {k: v["outputs"] for k, v in calcs.items()}}
    sens = {"pitch_rate_deg_s": {}, "clmax": {}}
    sens["pitch_rate_fresh_pack_deg_s"] = {}
    n_fresh = calcs["CALC-B1-PROPCAL"]["outputs"]["n_max_rps"]
    for r in (10.0, 12.0, 13.0, 15.0, 20.0, 30.0, 50.0):
        pv2 = dict(pv, trans=[r] + list(pv["trans"][1:]))
        sens["pitch_rate_deg_s"][str(r)] = simulate_pitchover(**pv2)["summary"]
        sens["pitch_rate_fresh_pack_deg_s"][str(r)] = simulate_pitchover(**dict(pv2, nmax=n_fresh))["summary"]
    si = calcs["CALC-B1-STALL"]["input_values"]
    for cm in (0.80, 0.86, 0.90):
        sens["clmax"][str(cm)] = {k: v for k, v in stall_speeds(**dict(si, clmax=cm)).items()
                                  if k in ("vs_gate_ms", "vt_gate_ms", "cruise_over_vt")}
    ci = calcs["CALC-B1-CRUISE"]["input_values"]
    sens["cruise_uncalibrated_p_el_w"] = cruise(**dict(ci, kcal=1.0))["p_el_w"]
    out["sensitivity"] = sens
    (HERE / "performance_results.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    svg_corridor(corr["rows_V_th_thlo_TW_Tfrac_P_stalled"], st["vs_gate_ms"], st["vt_gate_ms"],
                 kit.value("ASM-B1-VCRUISE"), corr["alpha_stall_deg"], HERE / "fig-b1-corridor.svg")
    svg_endurance(sweep["rows_V_P_Ppess_eta_t_tpess"], st["vt_gate_ms"], kit.value(P + "requirements.cruise_time_min"),
                  HERE / "fig-b1-endurance.svg")
    print("performance_results.json, fig-b1-corridor.svg, fig-b1-endurance.svg written")
