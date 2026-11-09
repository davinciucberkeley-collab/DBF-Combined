"""F4 flight-control software: checks the K09-L ArduPilot parameter file and emits its proof-chain claims.

Run:  python -I redesign/team/F4/fsw_check.py        -> claims.json beside this file, exit 1 on a lint error
Then: python -I redesign/proofs/build_graph.py

What it does (one paragraph). (1) Lints subsystems/flight-software/K09L.param: every parameter line has a comment
line above it, no name appears twice, values are numbers, and it lists the names not yet matched against an
ArduPilot source this session. (2) Confirms every mirrored key in subsystems/flight-software/params.json equals the
.param line it names (one source, two readers). (3) Derives the station -> ArduPilot motor number -> rotation map
from the station geometry and ArduPilot's Quad-X table in the tailsitter hover frame, and the direction of each
motor's 3 deg tangential cant; checks it against the published map. (4) Emits claims: airspeed limits against the
stall and VA, the rpm cap in Q and FW modes, descent speeds against vortex-ring onset, body-rate limits against
C1's 3 rad/s, differential-thrust yaw gain, harmonic-notch coverage, battery thresholds, geofence.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
import proofkit as pk  # noqa: E402

PARAM_FILE = HERE.parents[1] / "subsystems" / "flight-software" / "K09L.param"

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/flight-software/params.json"])

# ---------------------------------------------------------------- sources and assumptions
kit.source("SRC-F4-AP-TAILSITTER", "ArduPilot Plane: Tailsitter planes guide", "doc",
           url="https://ardupilot.org/plane/docs/guide-tailsitter.html", checked="2026-11-09",
           note="Q_TAILSIT_MOTMX, RAT_FW/VT, ANGLE, GSCMSK bits, DSKLD, Q_OPTIONS bits 7/8/18")
kit.source("SRC-F4-AP-SRC", "ArduPilot master source: quadplane.cpp, tailsitter.cpp, Parameters.cpp, "
           "AP_MotorsMulticopter.cpp, AC_WPNav.cpp, AP_FixedWing.h", "code",
           url="https://github.com/ArduPilot/ardupilot", checked="2026-11-09",
           note="parameter names, units, ranges; output_motor_mask(): diff = roll_factor * rudder_dt * 0.5; "
                "AIRSPEED_MIN/MAX are AP_Int16; Q_M_SPIN_MAX documented range 0.9-1.0")
kit.assumption("ASM-F4-DT-MIX", "Differential-thrust mixing in fixed-wing flight",
               "Per-motor output = throttle + roll_factor * rudder_dt * 0.5 with Quad-X roll factors normalised to "
               "+/-0.5, so full rudder moves each motor by 0.25 x RUDD_DT_GAIN/100", basis="SRC-F4-AP-SRC "
               "AP_MotorsMulticopter::output_motor_mask and AP_MotorsMatrix::normalise_rpy_factors",
               value=0.25, unit="-", status="UNVERIFIED", cites=["SRC-F4-AP-SRC"])
kit.assumption("ASM-F4-FW-PASSTHRU", "Fixed-wing motor output bypasses Q_M_SPIN_MAX",
               "In fixed-wing flight the tailsitter writes throttle straight to the motor actuators, so the rpm cap "
               "there is THR_MAX plus the yaw differential, not Q_M_SPIN_MAX", basis="tailsitter.cpp output() calls "
               "output_motor_mask(throttle, mask, rudder_dt), no thrust linearisation seen; SITL S4 logs RCOU",
               status="UNVERIFIED", cites=["SRC-F4-AP-SRC"])
kit.assumption("ASM-F4-THRUST-SQ", "Thrust varies with output squared",
               "Static thrust per motor T = k a^2, with k from the hover point (Q_M_THST_HOVER)",
               basis="rpm ~ duty x V and T ~ rpm^2; good to ~10 % between 0.2 and 0.85 output; the stand replaces it",
               status="UNVERIFIED")
kit.assumption("ASM-F4-YAW-M-REQ", "Cruise yaw moment to hold", "1.0 N*m at beta 10 deg (B3's N_req 0.9985 N*m, "
               "R0 geometry with Cn_beta -0.105; smaller at R1 where Cn_beta is +0.044)",
               basis="team/B3/claims.json CALC-B3-YAW-ACTIVE, CR-B3-04", value=1.0, unit="N*m", status="UNVERIFIED")
kit.assumption("ASM-F4-ARSPD-CAP", "Airspeed ceiling asked by C1", "AIRSPEED_MAX <= 20 m/s (below VD and VA)",
               basis="team/C1/CHANGE-REQUESTS.md CR-C1-08", value=20.0, unit="m/s")
kit.assumption("ASM-F4-MIN-FACTOR", "TECS floor above stall", "AIRSPEED_MIN >= 1.2 x trimmed stall speed, wings "
               "level; stall prevention (AIRSPEED_STALL) raises it in turns", basis="usual ArduPilot practice; "
               "B1 CR-B1-12 sets 15 m/s = 1.26 Vs", value=1.2, unit="-")

# ---------------------------------------------------------------- ArduPilot Quad-X table (AP_MotorsMatrix, viewed from above)
# motor number: (angle from copter forward, clockwise positive, deg; rotation viewed from above)
AP_QUAD_X = {1: (45, "CCW"), 2: (-135, "CCW"), 3: (-45, "CW"), 4: (135, "CW")}


def station_xy(ids, y, z):
    """Station -> (forward, right) in the hover copter frame. Copter forward = belly = -z; right = +y."""
    out = {}
    for sid in ids:
        sy = y if sid[1] == "R" else -y
        sz = z if sid[0] == "U" else -z
        out[sid] = (-sz, sy, sz)          # forward, right, aircraft z
    return out


@kit.calc("CALC-F4-MOTOR-MAP", title="Station -> motor number -> rotation, and cant sense",
          equation="copter fwd = -z, right = +y; motor n where atan2(right, fwd) = AP angle; cant side force along "
                   "the tangent that turns the airframe like the prop reaction torque",
          inputs={"ids": "P:propulsion.stations.ids", "y": "P:propulsion.stations.y_m", "z": "P:propulsion.stations.z_m",
                  "cant": "P:propulsion.stations.cant_deg", "pub": "P:fsw.motor_map"},
          units={"y": "m", "z": "m", "cant": "deg"}, cites=["SRC-F4-AP-SRC"])
def motor_map(ids, y, z, cant, pub):
    pos = station_xy(ids, y, z)
    derived, errors = {}, 0
    for sid, (fwd, right, _) in pos.items():
        ang = math.degrees(math.atan2(right, fwd))
        n = min(AP_QUAD_X, key=lambda k: abs(((AP_QUAD_X[k][0] - ang + 180) % 360) - 180))
        if abs(((AP_QUAD_X[n][0] - ang + 180) % 360) - 180) > 45:
            errors += 1
        derived[sid] = (n, AP_QUAD_X[n][1])
    for row in pub:                                     # published map must equal the derived one
        if derived[row["station"]] != (row["ap_motor"], row["rotation_from_nose"]):
            errors += 1
    # diagonal pairs share a sense (params note: UR+LL, UL+LR)
    if derived["UR"][1] != derived["LL"][1] or derived["UL"][1] != derived["LR"][1] or derived["UR"][1] == derived["UL"][1]:
        errors += 1
    # cant: side force s = sin(cant) T along the tangent whose torque about +x has the reaction-torque sign.
    # Viewed from the nose (looking along +x), a CCW prop gives a CW reaction torque = positive about +x.
    s = math.sin(math.radians(cant))
    fy = fz = 0.0
    tangents = {}
    for sid, (fwd, right, az) in pos.items():
        ay = right
        sign = +1 if derived[sid][1] == "CCW" else -1                 # wanted torque sign about +x
        r = math.hypot(ay, az)
        ty, tz = -az / r, ay / r                                      # +x torque tangent: tau_x = y Fz - z Fy > 0
        ty, tz = sign * ty, sign * tz
        tangents[sid] = [round(ty, 3), round(tz, 3)]
        fy += s * ty
        fz += s * tz
        if (ay * tz - az * ty) * sign <= 0:
            errors += 1
    return {"errors": errors, "net_side_force_frac": math.hypot(fy, fz) / 4.0,
            "cant_dir_yz": tangents, "derived": {k: list(v) for k, v in derived.items()}}


@kit.calc("CALC-F4-ARSPD", title="Airspeed limits against stall, transition gate, VA and Vmax",
          equation="f_min = AIRSPEED_MIN / Vs ; f_cr = AIRSPEED_CRUISE / (1.3 Vs)",
          inputs={"vs": "CL-A1-STALL-GATE", "vmin": "P:fsw.airspeed_min_ms", "vcr": "P:fsw.airspeed_cruise_ms",
                  "f": "P:requirements.transition_factor", "vmax": "P:fsw.airspeed_max_ms"},
          units={"vs": "m/s", "vmin": "m/s", "vcr": "m/s", "vmax": "m/s"})
def airspeed_limits(vs, vmin, vcr, f, vmax):
    return {"min_factor": vmin / vs, "cruise_over_trans": vcr / (f * vs), "vmax": float(vmax)}


@kit.calc("CALC-F4-ACT-CAP", title="Highest motor output in Q and FW modes",
          equation="a_Q = Q_M_SPIN_MAX ; a_FW = THR_MAX/100 + 0.25 RUDD_DT_GAIN/100",
          inputs={"spin": "P:fsw.spin_max", "thr": "P:fsw.thr_max_pct", "dt": "P:fsw.rudd_dt_gain_pct",
                  "k": "ASM-F4-DT-MIX"}, units={"thr": "%", "dt": "%"}, assumes=["ASM-F4-DT-MIX", "ASM-F4-FW-PASSTHRU"])
def actuator_cap(spin, thr, dt, k):
    return {"a_q": spin, "a_fw": thr / 100.0 + k * dt / 100.0}


@kit.calc("CALC-F4-YAW-DT", title="RUDD_DT_GAIN needed for the cruise yaw moment",
          equation="T_c = m g /(L/D)/n ; k = (m g / n)/a_h^2 ; a_c = sqrt(T_c/k) ; dT = M/(n y) ; "
                   "da = dT/(2 k a_c) ; gain = da / 0.25",
          inputs={"m": "P:requirements.mtow_gate_kg", "g": "P:env.g_ms2", "ld": "CL-B1-CRUISE-LD",
                  "n": "P:propulsion.n_motors", "a_h": "P:fsw.thst_hover", "y": "P:propulsion.stations.y_m",
                  "M": "ASM-F4-YAW-M-REQ", "k_mix": "ASM-F4-DT-MIX"},
          units={"m": "kg", "g": "m/s2", "y": "m", "M": "N*m"}, assumes=["ASM-F4-THRUST-SQ", "ASM-F4-DT-MIX"])
def yaw_dt(m, g, ld, n, a_h, y, M, k_mix):
    w = m * g
    t_c = w / ld / n
    k = (w / n) / a_h ** 2
    a_c = math.sqrt(t_c / k)
    d_t = M / (n * y)
    d_a = d_t / (2 * k * a_c)
    return {"gain_req_pct": 100 * d_a / k_mix, "a_cruise": a_c, "a_low_side": a_c - d_a, "dT_N": d_t}


@kit.calc("CALC-F4-DESCENT", title="Fastest commanded vertical descent",
          equation="v = max(Q_WP_SPD_DN, Q_PILOT_SPD_DN, Q_LAND_FINAL_SPD)",
          inputs={"wp": "P:fsw.wp_spd_dn_ms", "pil": "P:fsw.pilot_spd_dn_ms", "fin": "P:fsw.land_final_spd_ms"},
          units={"wp": "m/s", "pil": "m/s", "fin": "m/s"})
def descent(wp, pil, fin):
    return max(wp, pil, fin)


@kit.calc("CALC-F4-RATES", title="Largest commanded body rate", equation="w = max(rate limits) x pi/180",
          inputs={"q": "P:fsw.rate_max_q_degs", "fw": "P:fsw.rate_max_fw_degs"}, units={"q": "deg/s", "fw": "deg/s"})
def rates(q, fw):
    return math.radians(max(list(q) + list(fw)))


@kit.calc("CALC-F4-NOTCH", title="Harmonic notch coverage",
          equation="r_low = (hover rpm/60)/f_min ; r_top = n_h (rpm_max/60) / (f_gyro/2)",
          inputs={"rpm_h": "CL-B4-HOVER-RPM", "rpm_max": "P:propulsion.rpm_max", "f": "P:fsw.notch_freq_hz",
                  "nh": "P:fsw.notch_harmonics", "fg": "P:fsw.gyro_rate_hz"},
          units={"rpm_h": "rpm", "rpm_max": "rpm", "f": "Hz", "fg": "Hz"})
def notch(rpm_h, rpm_max, f, nh, fg):
    return {"low_ratio": (rpm_h / 60.0) / f, "top_ratio": nh * (rpm_max / 60.0) / (fg / 2.0)}


@kit.calc("CALC-F4-BATT", title="Battery thresholds", equation="r = BATT_CRT_MAH / (reserve x capacity)",
          inputs={"crt": "P:fsw.batt_crt_mah", "cap": "P:battery.capacity_ah", "res": "P:requirements.energy_reserve_frac"},
          units={"crt": "mAh", "cap": "Ah"})
def batt(crt, cap, res):
    return crt / (res * cap * 1000.0)


@kit.calc("CALC-F4-BATT-LOW", title="BATT_LOW_MAH as set", equation="BATT_LOW_MAH",
          inputs={"low": "P:fsw.batt_low_mah"}, units={"low": "mAh"})
def batt_low(low):
    return float(low)


@kit.calc("CALC-F4-FENCE", title="Geofence inside the ceiling and VLOS",
          equation="r_alt = FENCE_ALT_MAX / (ceiling ft x 0.3048) ; r_rad = FENCE_RADIUS / VLOS",
          inputs={"alt": "P:fsw.fence_alt_max_m", "ceil": "P:mission.ceiling_ft_agl", "rad": "P:fsw.fence_radius_m",
                  "vlos": "P:requirements.vlos_max_m"}, units={"alt": "m", "ceil": "ft", "rad": "m", "vlos": "m"})
def fence(alt, ceil, rad, vlos):
    return {"alt_ratio": alt / (ceil * 0.3048), "rad_ratio": rad / vlos}


# ---------------------------------------------------------------- claims
FC = ["AVN-001"]
MOT = ["PRP-002-UR", "PRP-002-UL", "PRP-002-LR", "PRP-002-LL"]
kit.claim("CL-F4-MOTOR-MAP-ERR", "Motor map errors (derived vs published, pairs, cant sense)", calc="CALC-F4-MOTOR-MAP",
          output="errors", limit=("<=", 0), verifies=["R-FSW-PARAMS"], parts=FC + MOT,
          how="Props off, Mission Planner motor test A-B-C-D: A spins LR, B UR, C UL, D LL (test order 1,4,2,3), "
              "each in the listed sense (T-F4-BENCH-MAP).")
kit.claim("CL-F4-CANT-NET-FORCE", "Net side force of the four canted motors, fraction of thrust",
          calc="CALC-F4-MOTOR-MAP", output="net_side_force_frac", limit=("<=", 0.001), parts=MOT,
          how="Check the printed mounts against SPEC.md: every prop end leans outboard and toward the wing plane.")
kit.claim("CL-F4-ARSPD-MIN-FACTOR", "AIRSPEED_MIN over trimmed stall (A1 R1 gate)", calc="CALC-F4-ARSPD",
          output="min_factor", limit=(">=", "ASM-F4-MIN-FACTOR"), parts=FC,
          how="Re-run when B3 publishes the trimmed stall at R1 geometry (D-21); slow-flight stall test T-B2-STALL.")
kit.claim("CL-F4-CRUISE-TRANS", "AIRSPEED_CRUISE over 1.3 Vs", calc="CALC-F4-ARSPD", output="cruise_over_trans",
          limit=(">=", 1.0), verifies=["R-TRANSITION"], parts=FC,
          how="SITL S4 and flight logs: airspeed reaches 16 m/s after every pitch-over before the first turn.")
kit.claim("CL-F4-ARSPD-MAX-VA", "AIRSPEED_MAX against manoeuvre speed VA", calc="CALC-F4-ARSPD", output="vmax", unit="m/s",
          limit=("<=", "CL-C1-VA"), parts=FC, how="Read AIRSPEED_MAX after loading; C1 re-derives VA.")
kit.claim("CL-F4-ARSPD-MAX-CAP", "AIRSPEED_MAX against the 20 m/s ceiling (CR-C1-08)", calc="CALC-F4-ARSPD", output="vmax", unit="m/s",
          limit=("<=", "ASM-F4-ARSPD-CAP"), parts=FC, how="Read AIRSPEED_MAX after loading.")
kit.claim("CL-F4-ARSPD-MAX-VMAX", "AIRSPEED_MAX reachable in level flight", calc="CALC-F4-ARSPD", output="vmax", unit="m/s",
          limit=("<=", "CL-B1-VMAX"), parts=FC, how="FBWB full-stick leg on the cruise-power test.")
kit.claim("CL-F4-SPIN-MAX", "Q-mode motor output cap", calc="CALC-F4-ACT-CAP", output="a_q",
          limit=("<=", "CL-B4-SPIN-MAX"), verifies=["R-ESC-CURRENT"], parts=MOT,
          how="Stand, fresh pack, QSTABILIZE full stick, props on: ESC telemetry rpm <= 9 350 (T-F4-STAND-RPM-CAP).")
kit.claim("CL-F4-FW-ACT-MAX", "FW motor output cap incl. yaw differential", calc="CALC-F4-ACT-CAP", output="a_fw",
          limit=("<=", "CL-B4-SPIN-MAX"), parts=MOT,
          how="SITL S4: RCOU of each motor at FBWA full throttle with full rudder stays <= 0.84 of range.")
kit.claim("CL-F4-RUDD-DT-REQ", "RUDD_DT_GAIN needed for 1.0 N*m cruise yaw", calc="CALC-F4-YAW-DT",
          output="gain_req_pct", unit="%", limit=("<=", "P:fsw.rudd_dt_gain_pct"), parts=MOT,
          how="FBWA yaw doublet on the twin, then on K09-L at 16 m/s (T-B3-YAW-DOUBLET): yaw rate damps in < 2 cycles.")
kit.claim("CL-F4-YAW-LOW-SIDE", "Output of the slow side at full yaw demand in cruise", calc="CALC-F4-YAW-DT",
          output="a_low_side", limit=(">=", 0.05), parts=MOT,
          how="Flight log RCOU at full rudder in cruise: no motor below 5 % output.")
kit.claim("CL-F4-DESCENT", "Fastest commanded vertical descent", calc="CALC-F4-DESCENT", output="value", unit="m/s",
          limit=("<=", "CL-B4-DESCENT"), verifies=["R-FAILSAFES"], parts=MOT,
          how="QLAND and QHOVER full-down logs: CTUN/QTUN DCRt >= -1.2 m/s.")
kit.claim("CL-F4-BODY-RATE", "Largest commanded body rate", calc="CALC-F4-RATES", output="value", unit="rad/s",
          limit=("<=", "ASM-C1-PITCH-RATE"), parts=FC, how="Read the six rate limits after loading; log RATE in QAUTOTUNE.")
kit.claim("CL-F4-NOTCH-LOW", "Hover 1P over the lowest notch frequency", calc="CALC-F4-NOTCH", output="low_ratio",
          limit=(">=", 1.1), verifies=["R-VIBRATION"], parts=FC,
          how="Hover FFT (INS_LOG_BAT) with the notch on: no gyro peak above the noise floor at 1P or 2P.")
kit.claim("CL-F4-NOTCH-TOP", "Highest notch harmonic at the rpm cap over gyro Nyquist", calc="CALC-F4-NOTCH",
          output="top_ratio", limit=("<=", 1.0), parts=FC, how="Confirm INS_GYRO_RATE on the chosen board (F3).")
kit.claim("CL-F4-BATT-CRT", "BATT_CRT_MAH over the 20 % reserve", calc="CALC-F4-BATT", output="value", limit=(">=", 1.0),
          verifies=["R-FAILSAFES", "R-MISSION"], parts=["PWR-001"],
          how="SITL S8 and props-off bench with a bench supply: low -> RTL, critical -> QLAND.")
kit.claim("CL-F4-BATT-LOW", "BATT_LOW_MAH set against E2's landing allowance", calc="CALC-F4-BATT-LOW",
          output="value", unit="mAh",
          limit=(">=", "CL-E2-BATT-LOW-MAH"), verifies=["R-FAILSAFES"], parts=["PWR-001"],
          how="Read BATT_LOW_MAH after loading; E2 re-emits 2 600 or 2 700.")
kit.claim("CL-F4-FENCE-ALT", "FENCE_ALT_MAX over the 400 ft ceiling", calc="CALC-F4-FENCE", output="alt_ratio",
          limit=("<=", 0.95), verifies=["R-FAILSAFES"], parts=FC, how="SITL S9: climb through 110 m triggers RTL.")
kit.claim("CL-F4-FENCE-RADIUS", "FENCE_RADIUS over VLOS", calc="CALC-F4-FENCE", output="rad_ratio",
          limit=("<=", 1.0), verifies=["R-FAILSAFES"], parts=FC, how="SITL S9; H3 checks the circle sits inside the sub-field.")

# ---------------------------------------------------------------- tests (all planned)
kit.test("T-F4-SITL-NAMES", "Load K09L.param in SITL and on the board; no unknown name except the 3 LEGACY pairs",
         verifies=["CL-F4-MOTOR-MAP-ERR", "CL-F4-SPIN-MAX"], procedure="SITL-PLAN.md S1")
kit.test("T-F4-BENCH-MAP", "Props-off motor order, rotation and elevon direction",
         verifies=["CL-F4-MOTOR-MAP-ERR"], procedure="TUNING-PLAN.md step 1")
kit.test("T-F4-STAND-RPM-CAP", "Fresh-pack full-stick rpm and pack current on the stand",
         verifies=["CL-F4-SPIN-MAX"], procedure="TUNING-PLAN.md step 2: ESC rpm <= 9 350, BAT.Curr <= 100 A")
kit.test("T-F4-SITL-FAILSAFES", "RC, battery, geofence, GPS/EKF, transition-fail and e-stop in SITL",
         verifies=["CL-F4-BATT-CRT", "CL-F4-FENCE-ALT", "CL-F4-FENCE-RADIUS", "CL-F4-DESCENT"],
         procedure="SITL-PLAN.md S7-S13")
kit.test("T-F4-SITL-TRANSITION", "Pitch-over 12/20/30 deg/s and back-transition 20/30/50 deg/s on a sagged pack",
         verifies=["CL-F4-CRUISE-TRANS", "CL-F4-FW-ACT-MAX"], procedure="SITL-PLAN.md S4-S5")
kit.test("T-F4-SITL-MOTOR-OUT", "Motor-failure injection in hover, pitch-over and cruise",
         verifies=["CL-F4-YAW-LOW-SIDE"], procedure="SITL-PLAN.md S11 (SIM_ENGINE_FAIL, SIM_ENGINE_MUL)")


# ---------------------------------------------------------------- lint of the parameter file (not a claim)
CHECKED_NAMES = {   # matched against SRC-F4-AP-SRC / SRC-F4-AP-TAILSITTER / the Plane parameter index, 2026-11-09
    "Q_TAILSIT_ENABLE", "Q_TAILSIT_MOTMX", "Q_TAILSIT_RAT_FW", "Q_TAILSIT_RAT_VT", "Q_TAILSIT_ANGLE",
    "Q_TAILSIT_THR_VT", "Q_TAILSIT_GSCMSK", "Q_TAILSIT_DSKLD", "Q_FRAME_CLASS", "Q_FRAME_TYPE", "Q_OPTIONS",
    "INITIAL_MODE", "Q_M_SPIN_MAX", "Q_M_BAT_CURR_MAX", "Q_M_BAT_CURR_TC", "Q_M_BAT_VOLT_MAX", "Q_M_BAT_VOLT_MIN",
    "Q_M_THST_HOVER", "Q_M_PWM_TYPE", "THR_MAX", "THR_MIN", "Q_A_RATE_R_MAX", "Q_A_ANGLE_MAX", "Q_WP_SPD_DN",
    "Q_PILOT_SPD_DN", "Q_LAND_FINAL_SPD", "Q_WVANE_ENABLE", "Q_WVANE_GAIN", "Q_ASSIST_SPEED", "Q_ASSIST_ALT",
    "Q_TRANS_FAIL", "Q_TRANS_FAIL_ACT", "AIRSPEED_CRUISE", "AIRSPEED_MIN", "AIRSPEED_MAX", "AIRSPEED_STALL",
    "ROLL_LIMIT_DEG", "PTCH_LIM_MAX_DEG", "PTCH_LIM_MIN_DEG", "TECS_CLMB_MAX", "RUDD_DT_GAIN", "INS_HNTCH_MODE",
    "BATT_FS_LOW_ACT", "BATT_ARM_VOLT", "BATT_FS_VOLTSRC", "THR_FAILSAFE", "FS_SHORT_ACTN", "FS_LONG_ACTN",
    "FS_LONG_TIMEOUT", "FS_EKF_THRESH", "Q_RTL_MODE", "RTL_ALTITUDE", "RTL_RADIUS", "FLTMODE_CH", "FLTMODE1",
    "FLTMODE2", "FLTMODE3", "FLTMODE4", "FLTMODE5", "FLTMODE6", "FENCE_TYPE", "FENCE_ACTION", "FENCE_ALT_MAX",
}
LEGACY = {"Q_WP_SPEED_DN": "Q_WP_SPD_DN", "Q_PILOT_SPEED_DN": "Q_PILOT_SPD_DN", "Q_LAND_SPEED": "Q_LAND_FINAL_SPD"}
LEGACY_SCALE = {"Q_WP_SPEED_DN": 100, "Q_PILOT_SPEED_DN": 100, "Q_LAND_SPEED": 100}


def lint(path):
    errors, values, comment_above = [], {}, False
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            comment_above = False
            continue
        if line.startswith("#"):
            comment_above = True if len(line) > 2 else comment_above
            continue
        if "," not in line:
            errors.append(f"line {i}: not NAME,VALUE: {line}")
            continue
        name, val = (s.strip() for s in line.split(",", 1))
        if name in values:
            errors.append(f"line {i}: {name} set twice")
        try:
            values[name] = float(val)
        except ValueError:
            errors.append(f"line {i}: {name} value '{val}' is not a number")
        if not comment_above:      # a comment covers the parameter lines below it until a blank line
            errors.append(f"line {i}: {name} has no comment")
    for old, new in LEGACY.items():
        if old in values and abs(values[old] - LEGACY_SCALE[old] * values.get(new, -1)) > 1e-6:
            errors.append(f"LEGACY {old} = {values[old]} does not equal {LEGACY_SCALE[old]} x {new}")
    return values, errors


def mirror_check(values):
    """Every params.json key with an 'ap' name must equal the .param value(s)."""
    errors = []
    local = pk.load_params(HERE.parents[1] / "subsystems" / "flight-software" / "params.json")
    import json
    raw = json.loads((HERE.parents[1] / "subsystems" / "flight-software" / "params.json").read_text(encoding="utf-8"))
    for key, leaf in raw["fsw"].items():
        ap = leaf.get("ap") if isinstance(leaf, dict) else None
        if not ap:
            continue
        names = ap.split(",")
        vals = leaf["value"] if isinstance(leaf["value"], list) else [leaf["value"]]
        for nm, v in zip(names, vals):
            if nm not in values or abs(values[nm] - float(v)) > 1e-9:
                errors.append(f"params.json fsw.{key} = {v} but K09L.param {nm} = {values.get(nm)}")
    for row in raw["fsw"]["motor_map"]["value"]:
        sf = values.get(f"SERVO{row['fc_output']}_FUNCTION")
        if sf != row["servo_function"] or row["servo_function"] != 32 + row["ap_motor"]:
            errors.append(f"motor map {row['station']}: SERVO{row['fc_output']}_FUNCTION {sf} != {row['servo_function']}")
    for row in raw["fsw"]["elevon_outputs"]["value"]:
        if values.get(f"SERVO{row['fc_output']}_FUNCTION") != row["servo_function"]:
            errors.append(f"elevon {row['side']}: SERVO{row['fc_output']}_FUNCTION mismatch")
    del local
    return errors


if __name__ == "__main__":
    vals, errs = lint(PARAM_FILE)
    errs += mirror_check(vals)
    unchecked = sorted(n for n in vals if n not in CHECKED_NAMES and n not in LEGACY)
    print(f"{PARAM_FILE.name}: {len(vals)} parameters, {len(LEGACY)} LEGACY duplicates, "
          f"{len(vals) - len(unchecked) - len(LEGACY)} names matched to a source, {len(unchecked)} to match on the "
          f"installed build (SITL S1):")
    print("  " + " ".join(unchecked))
    kit.write()
    mm = kit.nodes["CALC-F4-MOTOR-MAP"]["outputs"]
    print("motor map (station: [AP motor, rotation seen from the nose]):", mm["derived"])
    print("cant side-force direction (y, z unit vector) per station:", mm["cant_dir_yz"])
    yd = kit.nodes["CALC-F4-YAW-DT"]["outputs"]
    print(f"yaw: cruise output {yd['a_cruise']:.3f}, dT {yd['dT_N']:.2f} N/motor, slow side {yd['a_low_side']:.3f}")
    if errs:
        print("LINT ERRORS:\n  " + "\n  ".join(errs))
        sys.exit(1)
    print("lint: OK (every parameter commented, no duplicates, params.json mirrors K09L.param)")
