"""F4 flight-control software: checks the K09-L ArduPilot parameter file and emits its proof-chain claims.

Run:  python -I redesign/team/F4/fsw_check.py        -> claims.json beside this file, exit 1 on a lint error
Then: python -I redesign/proofs/build_graph.py

What it does (one paragraph). (1) Lints subsystems/flight-software/K09L.param: every parameter line has a comment
line above it, no name appears twice, values are numbers, and it lists the names not yet matched against an
ArduPilot source this session. (2) Confirms every mirrored key in subsystems/flight-software/params.json equals the
.param line it names (one source, two readers). (3) Derives the station -> ArduPilot motor number -> rotation map
from the station geometry and ArduPilot's Quad-X table in the tailsitter hover frame, and the direction of each
motor's tangential cant (7 deg); checks it against the published map and against D3's printed cant sense. (4) Emits
claims: airspeed limits against the stall, the D-36 floor and VA; the elevon deflection schedule (steady dive at the
pitch floor <= VA, level speed <= VH, speed scaler); the rpm cap in Q and FW modes; hover rate-loop crossover and
filter separation from the wing torsion mode; descent speeds against vortex-ring onset; the touchdown cut time;
body-rate limits; differential-thrust yaw gain; upper-pair hover output at the pitch-trim split; harmonic-notch coverage; battery thresholds; geofence; the 100 A
limiter setting and its per-motor share; final landing speed against the foot cartridges (CR-D5-21); sensor
offsets from F3's points and the CG; elevon servo limits from D6's linkage; elevon mixer gain against the trimmed
stall need. R5 (D-65, D-66, D-71): touchdown sink in the altitude-holding Q modes against the hard-landing sink, no
raw-stick flight mode (R-SPIRAL), AIRSPEED_MIN against 1.3 x the forward-CG stall. Lints K09L.param and the stand
overlay K09L-STAND.param (incl. no RCn_OPTION that selects MANUAL / ACRO).
R6 (CDR fix round 2026-11-13, CDR-07 a): every parameter name in both files must be in ArduPilot's published Plane
parameter list (ap_plane_param_names_4.7.1.txt beside this file: names only, taken from apm.pdef.xml of stable-4.7.1),
and no name that 4.7 removed or renamed may appear. Runs offline. New claims: AIRSPEED_MIN against 1.3 x the tripped
stall (B6), the yaw acceleration limit against the airframe's yaw authority (CDR-16), RC loss to QLAND time (CDR-26).
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
import proofkit as pk  # noqa: E402

NAMES_FILE = HERE / "ap_plane_param_names_4.7.1.txt"
PARAM_FILE = HERE.parents[1] / "subsystems" / "flight-software" / "K09L.param"
STAND_FILE = HERE.parents[1] / "subsystems" / "flight-software" / "K09L-STAND.param"

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/flight-software/params.json",
                                     "../../subsystems/fins/params.json"])

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
kit.source("SRC-F4-AP-472", "ArduPlane source at tag Plane-4.7.2: VTOL_Assist.cpp, tailsitter.cpp, quadplane.cpp, "
           "mode_rtl.cpp, mode_qrtl.cpp, mode_LoiterAltQLand.cpp, events.cpp, fence.cpp; AP_MotorsMulticopter.cpp; "
           "AC_AttitudeControl.cpp", "code",
           url="https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/ArduPlane/VTOL_Assist.cpp",
           checked="2026-11-14",
           note="should_assist(): Q_ASSIST_ALT <= 0 and Q_ASSIST_ANGLE <= 0 disable those triggers; angle assist needs attitude "
                "outside the FW limits + 5 deg AND error > Q_ASSIST_ANGLE for Q_ASSIST_DELAY. Tailsitter output(): FW throttle "
                "-> output_motor_mask() (pass-through); with Q_OPTIONS bit 8 the surfaces stay on the plane controllers in assist. "
                "setup(): tailsitter defaults table only for Q_FRAME_CLASS 10. ModeRTL::_enter(): QRTL only within 1.5 x "
                "max(WP_LOITER_RAD, RTL_RADIUS) and below Q_RTL_ALT. ModeLoiterAltQLand::_enter(): VTOL -> QLAND. Q_A_ANGLE_BOOST "
                "default 1; Q_TRANSITION_MS default 5000")
kit.assumption("ASM-F4-FW-PASSTHRU", "Fixed-wing motor output is pass-through (no Q_M_SPIN_MAX, no thrust curve)",
               "In fixed-wing flight Tailsitter::output() takes throttle = k_throttle/100 and calls output_motor_mask(), "
               "where actuator = throttle + roll_factor x rudder_dt x 0.5 and PWM = min + range x actuator. Settled from "
               "source (F4-R8; was 'higher of pass-through or linearised')", basis="SRC-F4-AP-472 tailsitter.cpp output(), "
               "AP_MotorsMulticopter::output_motor_mask(), tag Plane-4.7.2 (B4 closure 2.1 reads master the same); SITL S4 "
               "RCOU at FBWA full throttle confirms", status="CHECKED", cites=["SRC-F4-AP-472"])
kit.assumption("ASM-F4-THR-VH", "FW output that reaches VH 21.76 m/s in level flight, fresh pack, X2814 V3 + APC 11x8E (D-173)",
               "0.414 on a fresh 17.4 V LiHV pack at 2.70 kg (F4 estimate, the lower of E1's two prop calibrations; 0.420 with the other). At 16.8 V it was 0.429 (R10)", basis="F4 scratch vh_11x8.py (F4.md D-173): APC PER3 11x8E 6 000 rpm block (team/E1/data/apc_per3_11x8E.csv), E1 D-173.2 factors kT/kP 0.885/1.021 and 1.039/1.240, Kv 900, R_m 33.6 mOhm x 0.9 + 10 mOhm ESC, 17.4 V, B4 CALC-B4-PROP-AB CD0 0.0585 / k 0.1107, 2.64-2.70 kg, 10 deg cant. B4 to confirm with props.py", value=0.4144, unit="-", status="UNVERIFIED")
kit.assumption("ASM-F4-VLEVEL-SAG", "Level speed at THR_MAX 41 with FWD_BAT_VOLT_MAX 17.4 on a 14.4 V resting / 13.9 V loaded pack, 2.70 kg",
               "19.97 m/s (output 0.41 x 17.4 / 14.4 = 0.495; hot winding R_m x 1.43); 20.2 with the other prop factor",
               basis="F4 scratch vh_11x8.py, same inputs as ASM-F4-THR-VH; H2 gate 5 late-pack leg replaces it", value=19.97, unit="m/s", status="UNVERIFIED")
kit.assumption("ASM-F4-RPM-LOW", "Lowest steady rpm flown (cruise, 17 m/s), D-173", "4 899 rpm = 1P 81.7 Hz",
               basis="review/CLOSURE-ROUND-2026-11-14/E1.md D-173.4 (range over both prop factors)", value=4899, unit="rpm", status="UNVERIFIED")
kit.assumption("ASM-F4-RPM-MAX", "Highest rpm flown, D-173: one motor at the 0.81 cap on a fresh pack (transient)", "9 964 rpm",
               basis="review/CLOSURE-ROUND-2026-11-14/E1.md D-173.4", value=9964, unit="rpm", status="UNVERIFIED")
kit.assumption("ASM-F4-RPM-FULL-LIM", "Highest 1P at full throttle on the 80 A limiter, 11x8E (C4: 2P 241.5-264.7 Hz)", "7 942 rpm (2P 264.7 Hz)",
               basis="review/CLOSURE-ROUND-2026-11-14/C4.md extended set (A2 / F4 to confirm the notch tracks 2P to 265 Hz); first-mode band 229.2-240.7 Hz",
               value=7942, unit="rpm", status="UNVERIFIED")
kit.assumption("ASM-F4-YAW-M-REQ", "Cruise yaw moment to hold", "1.0 N*m at beta 10 deg (B3's N_req 0.9985 N*m, "
               "R0 geometry with Cn_beta -0.105; smaller at R1 where Cn_beta is +0.044)",
               basis="team/B3/claims.json CALC-B3-YAW-ACTIVE, CR-B3-04", value=1.0, unit="N*m", status="UNVERIFIED")
kit.assumption("ASM-F4-ARSPD-CAP", "Airspeed ceiling asked by C1", "ARSPD_FBW_MAX (= AIRSPEED_MAX in 4.5+) <= 22 m/s",
               basis="team/C1/CHANGE-REQUESTS.md CR-C1-08; CR-A1-36", value=22.0, unit="m/s")
kit.assumption("ASM-F4-VA-SCHED", "Speed up to which full elevon travel is allowed", "VA 20.5 m/s: full travel to VA, "
               "<= 1/3 at VD 27.2 (D-29, FAR 23.441 practice). C1's current CL-C1-VA is 21.96 m/s; the lower is used",
               basis="params/CHANGE-LOG.md D-29; team/C1/CHANGE-REQUESTS.md CR-C1-15", value=20.5, unit="m/s")
kit.assumption("ASM-F4-TORSION-HI", "Top of the antisymmetric wing torsion band", "11.7-14.9 Hz over C2's stiffness "
               "corners; 14.9 Hz is the upper corner", basis="team/C2/CHANGE-REQUESTS.md CR-C2-03 (CL-C2-F-TORSION-ANTI "
               "is the low corner)", value=14.9, unit="Hz", status="UNVERIFIED")
kit.assumption("ASM-F4-XOVER-MAX", "Hover rate-loop crossover ceiling, roll", "<= 4.5 Hz: B3's pitch ceiling "
               "(CL-B3-XOVER-MAX-PITCH, 6 dB / 45 deg with the torsion mode in the loop) also used for copter roll, "
               "which B3 did not bound; tighter than D-45's 5 Hz", basis="team/B3/CHANGE-REQUESTS.md CR-B3-19; "
               "params/CHANGE-LOG.md D-45", value=4.5, unit="Hz")
kit.assumption("ASM-F4-HOVER-DIFF", "Differential thrust reserved for hover control", "30 % of hover thrust per motor "
               "on top of the pitch-trim split (R-HOVER-AUTHORITY cap)", basis="team/A2/REQUIREMENTS.md R-HOVER-AUTHORITY",
               value=0.30, unit="-")
kit.assumption("ASM-F4-SAG", "Thrust factor of a sagged pack", "0.76 of fresh-pack thrust at the same output (D-35)",
               basis="params/CHANGE-LOG.md D-35; team/B1/CHANGE-REQUESTS.md CR-B1-12", value=0.76, unit="-",
               status="UNVERIFIED")
kit.assumption("ASM-F4-FILT-SEP", "Filter separation from the torsion mode", "gyro and D-term low-pass >= 2 x the "
               "torsion band", basis="team/C2/CHANGE-REQUESTS.md CR-C2-03", value=2.0, unit="-")
kit.assumption("ASM-F4-QT-ARM", "Prop torque-to-thrust ratio Q/T", "0.020 m for an APC 11x5.5 near hover "
               "(Cq D / Ct with Ct ~0.10, Cp ~0.045)", basis="APC static data class values; B4/E1 stand replaces it",
               value=0.020, unit="m", status="UNVERIFIED")
kit.assumption("ASM-F4-REACT", "Pilot cut reaction at a seen touchdown", "0.25 s from contact to switch movement, "
               "anticipated event", basis="simple visual reaction time 0.2-0.25 s; H2 logs 20 twin touchdowns",
               value=0.25, unit="s", status="UNVERIFIED")
kit.assumption("ASM-F4-SPINDOWN", "Thrust decay after motor stop", "0.15 s from stop command to thrust below the "
               "spin-min level (11-inch prop, active braking off)", basis="estimate; ESC log on the stand (GT-02d)",
               value=0.15, unit="s", status="UNVERIFIED")
kit.assumption("ASM-F4-TD-REQ", "Time from touchdown to spin-min", "<= 0.5 s (C5: above 0.72 W at contact a 10 deg "
               "tilt tips over)", basis="team/C5/CHANGE-REQUESTS.md CR-C5-05b", value=0.5, unit="s")
kit.assumption("ASM-F4-MIN-FACTOR", "TECS floor above stall", "AIRSPEED_MIN >= 1.2 x trimmed stall speed, wings "
               "level; stall prevention (AIRSPEED_STALL) raises it in turns", basis="usual ArduPilot practice; "
               "B1 CR-B1-12 sets 15 m/s = 1.26 Vs", value=1.2, unit="-")
kit.assumption("ASM-F4-AVN-POINTS", "IMU and GPS centres in the aircraft frame",
               "IMU (-0.010, 0.046, 0.039) m: F3's CoreWing FC point with the board 4 mm higher (old IMU z 0.035 + 0.004; D-173b back from the Kakute); "
               "GPS centre (0.075, 0, 0.178) m", basis="team/F3/CHANGE-REQUESTS.md CR-F3-20 (F3's CALC-F3-OFFSETS "
               "still holds the R3 layout); re-measure as built", value={"imu": [-0.010, 0.046, 0.039],
               "gps": [0.075, 0.0, 0.178]}, unit="m", status="UNVERIFIED")
kit.assumption("ASM-F4-THETA-DN", "Servo angle for 25 deg TE down", "-42.9 deg (D6 linkage solution)",
               basis="team/D6/claims.json CALC-D6-KIN output theta_dn_deg -42.87 (no claim id published; "
               "CR-D6-09 quotes it)", value=-42.87, unit="deg", status="UNVERIFIED")

kit.source("SRC-F4-AP-PDEF", "ArduPilot Plane parameter definitions, stable-4.7.1 (apm.pdef.xml, tag Plane-4.7.1 dbe79216)",
           "doc", url="https://autotest.ardupilot.org/Parameters/versioned/Plane/stable-4.7.1/apm.pdef.xml",
           checked="2026-11-13",
           note="5 721 parameter names; name list committed as team/F4/ap_plane_param_names_4.7.1.txt. The stable-4.7.2 "
                "folder is not published (HTTP 404 on 2026-11-13); the latest-master list gives the same result for K09L.param")
kit.source("SRC-F4-AP-RELNOTES", "ArduPlane ReleaseNotes.txt at tag Plane-4.7.2", "doc",
           url="https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/ArduPlane/ReleaseNotes.txt",
           checked="2026-11-13",
           note="4.7.2: CoreWing F405 Wing V2 board added (PR 33717). 4.7.0: FS_SHORT_TIMEOUT removed (PR 30350), "
                "RC_FS_TIMEOUT added (PR 31441), ATC_ACC_R/P/Y_MAX renamed and scaled to deg/s/s (PR 32192), QuadPlane "
                "attitude and position control converted to SI units (PR 30683)")
kit.source("SRC-F4-AP-EVENTS", "ArduPlane/events.cpp and radio.cpp at tag Plane-4.7.2", "code",
           url="https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/ArduPlane/events.cpp",
           checked="2026-11-13",
           note="rc_failsafe_short_on_event(): QSTABILIZE / QLOITER / QHOVER -> QLAND unless Q_OPTIONS bit 5 or 20; "
                "radio.cpp control_failsafe(): failsafe set after 10 consecutive checks with no valid frame for "
                "RC_FS_TIMEOUT (default 1.0 s, RC_Channels_VarInfo.h)")
kit.assumption("ASM-F4-FS-COUNT", "RC failsafe debounce", "10 consecutive failed checks at the 50 Hz radio task = 0.2 s "
               "after RC_FS_TIMEOUT has run out", basis="radio.cpp control_failsafe() (throttle_counter == 10), tag "
               "Plane-4.7.2; the 50 Hz rate of read_radio is from the scheduler table (not re-read here): SITL measured "
               "1.15 s in total on 2026-11-13 (team/F4/sitl/RESULTS.md S7a)", value=0.2, unit="s",
               status="UNVERIFIED", cites=["SRC-F4-AP-EVENTS"])
kit.assumption("ASM-F4-QLAND-MAX", "RC loss to QLAND in a Q mode", "<= 3 s after the last valid frame "
               "(CDR-EL-11 pass line, REVIEWER EST: 5 s without control in 5 m/s wind is about 25 m of drift)",
               basis="review/CDR-2026-11-13/CDR-electrical.md CDR-EL-11", value=3.0, unit="s")
kit.assumption("ASM-F4-YAW-ACC-FRAC", "Share of the yaw authority the attitude shaper may ask for",
               "Q_A_ACC_Y_MAX <= 0.85 x the yaw acceleration at 30 % differential (B4 half-fin factor)",
               basis="review/CDR-2026-11-13/CDR-aero.md CDR-AE-12 (85 % of 2.8 rad/s2); T-B4-YAW measures the factor",
               value=0.85, unit="-")

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
                  "cant": "P:propulsion.stations.cant_deg", "pub": "P:fsw.motor_map",
                  "d3": "P:fin_detail.mount.cant_sense_UR"},
          units={"y": "m", "z": "m", "cant": "deg"}, cites=["SRC-F4-AP-SRC"])
def motor_map(ids, y, z, cant, pub, d3):
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
    # D3 prints: sense +1 gives UR thrust a side component along +t = x_hat x r_hat = (-z, y)/r
    py, pz = pos["UR"][1], pos["UR"][2]
    r = math.hypot(py, pz)
    t_plus = (-pz / r, py / r)
    need = 1 if (tangents["UR"][0] * t_plus[0] + tangents["UR"][1] * t_plus[1]) > 0 else -1
    return {"errors": errors, "net_side_force_frac": math.hypot(fy, fz) / 4.0,
            "cant_dir_yz": tangents, "derived": {k: list(v) for k, v in derived.items()},
            "d3_sense_needed": need, "d3_sense_agree": need * d3}


@kit.calc("CALC-F4-ARSPD", title="Airspeed limits against stall, transition gate, VA and Vmax",
          equation="f_min = AIRSPEED_MIN / Vs ; f_cr = AIRSPEED_CRUISE / (1.3 Vs) ; Vs_keep = AIRSPEED_MIN / 1.3 "
                   "(largest measured stall that keeps AIRSPEED_MIN, D-71)",
          inputs={"vs": "CL-A1-STALL-GATE", "vmin": "P:fsw.airspeed_min_ms", "vcr": "P:fsw.airspeed_cruise_ms",
                  "f": "P:requirements.transition_factor", "vmax": "P:fsw.airspeed_max_ms"},
          units={"vs": "m/s", "vmin": "m/s", "vcr": "m/s", "vmax": "m/s"})
def airspeed_limits(vs, vmin, vcr, f, vmax):
    return {"min_factor": vmin / vs, "cruise_over_trans": vcr / (f * vs), "vmax": float(vmax), "vmin": float(vmin),
            "vs_keep": vmin / f}


@kit.calc("CALC-F4-DIVE", title="Elevon schedule: steady dive at the pitch floor, speed scaler at VA and VD",
          equation="CD0 = CL_c/LD - k CL_c^2 ; W sin(theta) = q S CD0 + W^2 k /(q S) -> V_dive ; "
                   "s(V) = max(min(0.5, SCALING_SPEED/(2 AIRSPEED_MAX)), SCALING_SPEED / V)",
          inputs={"m": "P:requirements.mtow_gate_kg", "g": "P:env.g_ms2", "rho": "P:env.rho_kgm3", "b": "P:wing.span_m",
                  "c": "P:wing.chord_m", "e": "P:wing.oswald_e", "ld": "CL-B1-CRUISE-LD", "vc": "P:performance.cruise_ms",
                  "th": "P:fsw.pitch_lim_min_deg", "sc": "P:fsw.scaling_speed_ms", "vmax": "P:fsw.airspeed_max_ms",
                  "vd": "CL-C1-VD", "va": "ASM-F4-VA-SCHED"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "b": "m", "c": "m", "vc": "m/s", "th": "deg", "sc": "m/s",
                 "vmax": "m/s", "vd": "m/s"}, cites=["SRC-F4-AP-SRC"])
def dive(m, g, rho, b, c, e, ld, vc, th, sc, vmax, vd, va):
    w, s_ref = m * g, b * c
    k = 1.0 / (math.pi * (b / c) * e)
    cl_c = w / (0.5 * rho * vc ** 2 * s_ref)
    cd0 = cl_c / ld - k * cl_c ** 2
    d = w * math.sin(math.radians(abs(th)))      # zero thrust: prop past its pitch speed; windmill drag ignored (conservative)
    a, bb = s_ref * cd0, w ** 2 * k / s_ref
    q = (d + math.sqrt(d * d - 4 * a * bb)) / (2 * a)
    smin = min(0.5, sc / (2.0 * vmax))
    return {"v_dive": math.sqrt(2 * q / rho), "cd0": cd0, "scaler_va": max(smin, sc / va),
            "scaler_vd": max(smin, sc / vd)}


@kit.calc("CALC-F4-VLEVEL", title="Level speed at THR_MAX: fresh pack against the VH that VD 27.2 m/s assumes, sagged pack "
          "against AIRSPEED_MAX (D-173: X2814 V3 + 11x8E, FWD_BAT compensation)",
          equation="a = THR_MAX/100 (pass-through, fresh pack: compensation ratio 1) ; r_VH = a / a_VH ; V_sag from "
                   "ASM-F4-VLEVEL-SAG (valid at THR_MAX 41 with FWD_BAT_VOLT_MAX 17.4)",
          inputs={"thr": "P:fsw.thr_max_pct", "a_vh": "ASM-F4-THR-VH", "v_sag": "ASM-F4-VLEVEL-SAG", "vd": "P:requirements.vd_ms",
                  "vmax": "P:fsw.fwd_bat_volt_max_v"},
          units={"thr": "%", "vd": "m/s", "v_sag": "m/s", "vmax": "V"},
          assumes=["ASM-F4-FW-PASSTHRU", "ASM-F4-THR-VH", "ASM-F4-VLEVEL-SAG"], cites=["SRC-F4-AP-472"])
def vlevel(thr, a_vh, v_sag, vd, vmax):
    a = thr / 100.0
    return {"a_fw_thr": a, "vh_req": vd / 1.25, "ratio": a / a_vh, "v_lvl_sag": v_sag if (thr == 41 and vmax == 17.4) else float("nan")}


@kit.calc("CALC-F4-XOVER", title="Hover rate-loop crossover per axis (rigid body, upper-bound thrust)",
          equation="K = 2 T arm / I (mixer factors +/-0.5, four motors) ; |L(jw)| = K sqrt(P^2 + D^2 w^2) / w = 1 "
                   "-> w = K P / sqrt(1 - K^2 D^2) ; P ceiling = w_max sqrt(1/K^2 - D^2), w_max per axis",
          inputs={"T": "P:requirements.thrust_limit_per_motor_n", "y": "P:propulsion.stations.y_m",
                  "z": "P:propulsion.stations.z_m", "cant": "P:propulsion.stations.cant_deg", "qt": "ASM-F4-QT-ARM",
                  "izz": "CL-A3-IZZ", "iyy": "CL-A3-IYY", "ixx": "CL-A3-IXX", "p": "P:fsw.rate_p", "d": "P:fsw.rate_d",
                  "fr": "ASM-F4-XOVER-MAX", "fp": "CL-B3-XOVER-MAX-PITCH", "fy": "CL-B3-XOVER-MAX-YAW"},
          units={"T": "N", "y": "m", "z": "m", "cant": "deg"}, assumes=["ASM-F4-QT-ARM"])
def crossover(T, y, z, cant, qt, izz, iyy, ixx, p, d, fr, fp, fy):
    arm_yaw = math.sin(math.radians(cant)) * math.hypot(y, z) + qt
    ks = {"rll": 2 * T * y / izz, "pit": 2 * T * z / iyy, "yaw": 2 * T * arm_yaw / ixx}
    gp = {"rll": p[0], "pit": p[1], "yaw": p[2]}
    gd = {"rll": d[0], "pit": d[1], "yaw": 0.0}
    out, fmax = {}, {"rll": fr, "pit": fp, "yaw": fy}
    for ax, kk in ks.items():
        wmax = 2 * math.pi * fmax[ax]
        w = kk * gp[ax] / math.sqrt(1 - (kk * gd[ax]) ** 2)
        out[f"f_{ax}_hz"] = w / (2 * math.pi)
        out[f"p_ceiling_{ax}"] = wmax * math.sqrt(1 / kk ** 2 - gd[ax] ** 2)
    return out


@kit.calc("CALC-F4-FILT", title="Gyro and D-term low-pass over the top of the torsion band",
          equation="r = min(INS_GYRO_FILTER, Q_A_RAT_RLL/PIT_FLTD) / f_torsion_hi",
          inputs={"fg": "P:fsw.gyro_filter_hz", "fd": "P:fsw.rate_fltd_hz", "ft": "ASM-F4-TORSION-HI"},
          units={"fg": "Hz", "fd": "Hz"})
def filt(fg, fd, ft):
    return min([fg] + list(fd)) / ft


@kit.calc("CALC-F4-SPLIT", title="Upper-pair motor output in hover with the pitch-trim split, control reserve and a sagged pack",
          equation="T_up/T_mean = 2 s /(1 + s) ; a_up = a_h / sqrt(sag) x sqrt(T_up/T_mean x (1 + d))",
          inputs={"s": "CL-A3-HOVER-SPLIT", "smax": "P:requirements.hover_split_max", "a_h": "P:fsw.thst_hover",
                  "d": "ASM-F4-HOVER-DIFF", "sag": "ASM-F4-SAG"},
          assumes=["ASM-F4-THRUST-SQ", "ASM-F4-SAG"])
def split(s, smax, a_h, d, sag):
    f = lambda r: a_h / math.sqrt(sag) * math.sqrt(2 * r / (1 + r) * (1 + d))
    return {"a_up": f(s), "a_up_at_limit": f(smax)}


@kit.calc("CALC-F4-TD-CUT", title="Touchdown to motors below spin-min with the RC9 cut",
          equation="t = pilot reaction + switch-channel link latency + thrust decay",
          inputs={"r": "ASM-F4-REACT", "l": "CL-F5-SWITCH-LATENCY", "s": "ASM-F4-SPINDOWN"},
          assumes=["ASM-F4-REACT", "ASM-F4-SPINDOWN"])
def td_cut(r, l, s):
    return r + l + s


@kit.calc("CALC-F4-ACT-CAP", title="Highest motor output in Q and FW modes",
          equation="a_Q = Q_M_SPIN_MAX ; a_FW = THR_MAX/100 x FWD_BAT_VOLT_MAX / FWD_BAT_VOLT_MIN + 0.25 RUDD_DT_GAIN/100 "
                   "(largest compensation ratio, servos.cpp FWD_BATT_CMP)",
          inputs={"spin": "P:fsw.spin_max", "thr": "P:fsw.thr_max_pct", "dt": "P:fsw.rudd_dt_gain_pct",
                  "k": "ASM-F4-DT-MIX", "vx": "P:fsw.fwd_bat_volt_max_v", "vn": "P:fsw.fwd_bat_volt_min_v"},
          units={"thr": "%", "dt": "%", "vx": "V", "vn": "V"}, assumes=["ASM-F4-DT-MIX", "ASM-F4-FW-PASSTHRU"])
def actuator_cap(spin, thr, dt, k, vx, vn):
    return {"a_q": spin, "a_fw": min(1.0, thr / 100.0 * vx / vn) + k * dt / 100.0}


@kit.calc("CALC-F4-SPIN-A1", title="Q_M_SPIN_MAX in K09L.param against A1's fixed cap", equation="diff = |set - A1|",
          inputs={"set": "P:fsw.spin_max", "a1": "P:fsw.q_m_spin_max"})
def spin_a1(set, a1):
    return {"diff": abs(set - a1)}


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
          equation="v = max(Q_WP_SPD_DN, Q_PILOT_SPD_DN, Q_LAND_FINAL_SPD) ; v_td = max(Q_PILOT_SPD_DN, "
                   "Q_LAND_FINAL_SPD) (Q_WP_SPD_DN ends at Q_LAND_FINAL_ALT 6 m, so it never reaches the ground)",
          inputs={"wp": "P:fsw.wp_spd_dn_ms", "pil": "P:fsw.pilot_spd_dn_ms", "fin": "P:fsw.land_final_spd_ms"},
          units={"wp": "m/s", "pil": "m/s", "fin": "m/s"})
def descent(wp, pil, fin):
    return {"value": max(wp, pil, fin), "touchdown": max(pil, fin)}


RAW_MODES = {0: "MANUAL", 2: "STABILIZE", 3: "TRAINING", 4: "ACRO", 23: "QACRO"}   # Plane mode numbers (control_mode)


@kit.calc("CALC-F4-FLTMODES", title="Flight modes a pilot can select or boot into that pass raw stick to a surface or motor",
          equation="n = count(m in FLTMODE1-6 + INITIAL_MODE, m in {0 MANUAL, 2 STABILIZE, 3 TRAINING, 4 ACRO, 23 QACRO})",
          inputs={"modes": "P:fsw.fltmodes", "init": "P:fsw.initial_mode"}, cites=["SRC-F4-AP-SRC"])
def fltmodes(modes, init):
    raw = [m for m in list(modes) + [init] if int(m) in RAW_MODES]
    return {"value": len(raw), "raw": [RAW_MODES[int(m)] for m in raw]}


@kit.calc("CALC-F4-RATES", title="Largest commanded body rate", equation="w = max(rate limits) x pi/180",
          inputs={"q": "P:fsw.rate_max_q_degs", "fw": "P:fsw.rate_max_fw_degs"}, units={"q": "deg/s", "fw": "deg/s"})
def rates(q, fw):
    return math.radians(max(list(q) + list(fw)))


@kit.calc("CALC-F4-NOTCH", title="Harmonic notch coverage",
          equation="r_low = (hover rpm/60)/f_min ; r_top = n_h (rpm_max/60) / (f_gyro/2)",
          inputs={"rpm_h": "ASM-F4-RPM-LOW", "rpm_max": "ASM-F4-RPM-MAX", "f": "P:fsw.notch_freq_hz",
                  "nh": "P:fsw.notch_harmonics", "fg": "P:fsw.gyro_rate_hz"},
          units={"rpm_h": "rpm", "rpm_max": "rpm", "f": "Hz", "fg": "Hz"})
def notch(rpm_h, rpm_max, f, nh, fg):
    return {"low_ratio": (rpm_h / 60.0) / f, "top_ratio": nh * (rpm_max / 60.0) / (fg / 2.0)}


@kit.calc("CALC-F4-NOTCH-2P", title="Harmonic notch tracks 2P at full throttle on the limiter",
          equation="r = 2 (rpm_lim/60) / (0.48 f_gyro) ; needs harmonic bit 1 (2P) set and 1P >= INS_HNTCH_FREQ",
          inputs={"rpm_lim": "ASM-F4-RPM-FULL-LIM", "rpm_l": "ASM-F4-RPM-LOW", "f": "P:fsw.notch_freq_hz",
                  "nh": "P:fsw.notch_harmonics", "fg": "P:fsw.gyro_rate_hz"},
          units={"rpm_lim": "rpm", "rpm_l": "rpm", "f": "Hz", "fg": "Hz"})
def notch2p(rpm_lim, rpm_l, f, nh, fg):
    # HarmonicNotchFilter.cpp (tag Plane-4.7.2, read 2026-11-14): HARMONIC_NYQUIST_CUTOFF 0.48 x filter sample rate
    has2p = 1.0 if (int(nh) & 2) else 0.0
    return {"ratio": 2.0 * (rpm_lim / 60.0) / (0.48 * fg) if has2p else 9.99,
            "min_ok": 1.0 if (rpm_l / 60.0) >= f else 0.0}


@kit.calc("CALC-F4-BATT", title="Battery thresholds", equation="r = BATT_CRT_MAH / (reserve x capacity)",
          inputs={"crt": "P:fsw.batt_crt_mah", "cap": "P:battery.capacity_ah", "res": "P:requirements.energy_reserve_frac"},
          units={"crt": "mAh", "cap": "Ah"})
def batt(crt, cap, res):
    return round(crt / (res * cap * 1000.0), 9)   # rounded: 0.2 x 6.0 x 1000 is 1200.0000000000002 in binary floating point


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


@kit.calc("CALC-F4-SENSOR-POS", title="INS_POS and GPS1_POS from F3's points and the CG (FRD body axes)",
          equation="X_fwd = -(x - x_cg) ; Y = y ; Z_down = -(z - z_cg) ; err = max |set - derived|",
          inputs={"pts": "ASM-F4-AVN-POINTS", "xcg": "P:cg.x_target_m", "zcg": "P:cg.z_target_m",
                  "ins": "P:fsw.ins_pos_m", "gps": "P:fsw.gps_pos_m"}, units={"xcg": "m", "zcg": "m"},
          assumes=["ASM-F4-AVN-POINTS"])
def sensor_pos(pts, xcg, zcg, ins, gps):
    frd = lambda q: [-(q[0] - xcg), q[1], -(q[2] - zcg)]
    i, g = frd(pts["imu"]), frd(pts["gps"])
    err = max(abs(a - b) for a, b in zip(i + g, list(ins) + list(gps)))
    return {"ins_derived_m": i, "gps_derived_m": g, "err_m": err}


@kit.calc("CALC-F4-ELEVON-PWM", title="SERVO5/6 MIN/MAX for +/-25 deg TE from D6's linkage",
          equation="k = 500 us / servo throw ; up = theta_up k ; dn = |theta_dn| k ; right (normal): MAX = TRIM + up, "
                   "MIN = TRIM - dn ; left (reversed): MIN = TRIM - up, MAX = TRIM + dn ; err = max |set - derived| ; "
                   "span = max |end - TRIM|",
          inputs={"th_up": "CL-D6-THROW-NEED", "th_dn": "ASM-F4-THETA-DN", "throw": "ASM-D6-SERVO-THROW",
                  "left": "P:fsw.elevon_pwm_left_us", "right": "P:fsw.elevon_pwm_right_us"},
          units={"th_up": "deg", "th_dn": "deg", "throw": "deg"}, assumes=["ASM-F4-THETA-DN", "ASM-D6-SERVO-THROW"])
def elevon_pwm(th_up, th_dn, throw, left, right):
    k = 500.0 / throw
    up, dn = th_up * k, abs(th_dn) * k
    lmin, ltrim, lmax, lrev = left
    rmin, rtrim, rmax, rrev = right
    want = {"l_min": ltrim - up, "l_max": ltrim + dn, "r_min": rtrim - dn, "r_max": rtrim + up}
    have = {"l_min": lmin, "l_max": lmax, "r_min": rmin, "r_max": rmax}
    err = max(abs(want[n] - have[n]) for n in want)
    span = max(abs(lmin - ltrim), abs(lmax - ltrim), abs(rmin - rtrim), abs(rmax - rtrim))
    return {"err_us": err, "span_us": span, "us_per_deg": k, "derived_us": want,
            "mirror_ok": 1 if (lrev, rrev) == (1, 0) else 0}


@kit.calc("CALC-F4-MIX", title="Elevon travel for pure pitch with MIXING_GAIN against the trimmed-CLmax need",
          equation="d_pitch = MIXING_GAIN x full travel ; r = |delta_stall| / d_pitch",
          inputs={"g": "P:fsw.mixing_gain", "trav": "P:wing.elevon.deflection_deg", "ds": "CL-B3-DELTA-STALL",
                  "half": "P:requirements.elevon_trim_travel_max"}, units={"trav": "deg", "ds": "deg"})
def mix(g, trav, ds, half):
    full = max(abs(t) for t in trav)
    return {"d_pitch_deg": g * full, "ratio": abs(ds) / (g * full), "gain_over_trim_limit": g / half}


@kit.calc("CALC-F4-LAND-SPD", title="Final landing descent as set", equation="Q_LAND_FINAL_SPD",
          inputs={"v": "P:fsw.land_final_spd_ms"}, units={"v": "m/s"})
def land_spd(v):
    return float(v)


@kit.calc("CALC-F4-BAT-CURR", title="Pack-current limiter as set and its per-motor share",
          equation="I_set = Q_M_BAT_CURR_MAX ; I_motor = I_set / n",
          inputs={"i": "P:fsw.bat_curr_max_a", "n": "P:propulsion.n_motors", "idx": "P:fsw.bat_idx"},
          units={"i": "A"})
def bat_curr(i, n, idx):
    return {"i_set_a": float(i), "i_motor_a": i / n, "idx": idx}


@kit.calc("CALC-F4-ARSPD-TRIP", title="AIRSPEED_MIN against the tripped-boundary-layer stall (planning baseline, B6)",
          equation="V_need = f x Vs_trip ; Vs_keep = AIRSPEED_MIN / f ; second fallback: AIRSPEED_MIN 18 holds to 18 / f",
          inputs={"vs": "CL-B2R3-VS-GATE-FWD-TURB", "f": "P:requirements.transition_factor",
                  "vmin": "P:fsw.airspeed_min_ms", "vcr": "P:fsw.airspeed_cruise_ms", "vas": "P:fsw.assist_speed_ms"},
          units={"vs": "m/s", "vmin": "m/s", "vcr": "m/s", "vas": "m/s"})
def arspd_trip(vs, f, vmin, vcr, vas):
    return {"v_need": f * vs, "vmin": float(vmin), "vs_keep": vmin / f, "vs_keep_fb2": 18.0 / f,
            "cruise_minus_min": vcr - vmin, "assist_over_vs": vas / vs}


@kit.calc("CALC-F4-PTCH-RMAX", title="FW pitch-rate caps against C1's load-factor ceilings at VD and the turn need",
          equation="q_up = PTCH2SRV_RMAX_UP ; q_dn = PTCH2SRV_RMAX_DN ; q_turn = g sin(phi) tan(phi) / AIRSPEED_MIN x 180/pi "
                   "(coordinated turn at ROLL_LIMIT_DEG)",
          inputs={"fw": "P:fsw.rate_max_fw_degs", "vmin": "P:fsw.airspeed_min_ms", "phi": "P:fsw.roll_limit_deg",
                  "g": "P:env.g_ms2"}, units={"fw": "deg/s", "vmin": "m/s", "phi": "deg", "g": "m/s2"})
def ptch_rmax(fw, vmin, phi, g):
    p = math.radians(phi)
    return {"q_up": float(fw[1]), "q_dn": float(fw[2]),
            "q_turn": math.degrees(g * math.sin(p) * math.tan(p) / vmin),
            "turn_frac": math.degrees(g * math.sin(p) * math.tan(p) / vmin) / fw[1]}


@kit.calc("CALC-F4-QASSIST", title="Q-assist triggers that can run the multicopter mixer above Q_ASSIST_SPEED, and the "
          "load factor the speed trigger can reach",
          equation="n_trig = [Q_ASSIST_ALT > 0] + [Q_ASSIST_ANGLE > 0] (VTOL_Assist::should_assist) ; "
                   "n_assist = (Q_ASSIST_SPEED / Vs)^2 (stall line caps the load factor below the assist speed)",
          inputs={"alt": "P:fsw.assist_alt_m", "ang": "P:fsw.assist_angle_deg", "vas": "P:fsw.assist_speed_ms",
                  "vs": "CL-C1-VS", "qopt": "P:fsw.q_options"},
          units={"alt": "m", "ang": "deg", "vas": "m/s", "vs": "m/s"}, cites=["SRC-F4-AP-472"])
def qassist(alt, ang, vas, vs, qopt):
    return {"n_trig": int(alt > 0) + int(ang > 0), "n_assist": (vas / vs) ** 2,
            "motors_only_bit8": int((int(qopt) >> 8) & 1)}


@kit.calc("CALC-F4-TRANS-ENTRY", title="Forward-transition throttle hold: angle boost and the Q_TRANSITION_MS fallback rate",
          equation="boost = Q_A_ANGLE_BOOST ; rate_fallback = Q_TAILSIT_ANGLE / (Q_TRANSITION_MS / 2000) ; "
                   "err = |rate_fallback - Q_TAILSIT_RAT_FW|",
          inputs={"boost": "P:fsw.angle_boost", "ms": "P:fsw.transition_ms", "ang": "P:fsw.tailsit_angle_deg",
                  "rat": "P:fsw.rat_fw_degs"}, units={"ms": "ms", "ang": "deg", "rat": "deg/s"}, cites=["SRC-F4-AP-472"])
def trans_entry(boost, ms, ang, rat):
    r = ang / (ms / 2000.0)
    return {"boost": float(boost), "rate_fallback": r, "err": abs(r - rat)}


@kit.calc("CALC-F4-FS-PITCHOVER", title="Battery and RC failsafe actions that start a forward transition from a Q mode",
          equation="n = [BATT_FS_LOW_ACT in {1 RTL, 2 Land, 7 AUTOLAND_OR_RTL}] + [BATT_FS_CRT_ACT in {1, 2, 7}] + "
                   "[Q_OPTIONS bit 20 Force RTL on RC loss in VTOL] ; 6 Loiter-to-QLand and 4 QLand enter QLAND from a "
                   "Q mode (ModeLoiterAltQLand::_enter, handle_battery_failsafe; tag Plane-4.7.2)",
          inputs={"low": "P:fsw.batt_fs_low_act", "crt": "P:fsw.batt_fs_crt_act", "qopt": "P:fsw.q_options"},
          cites=["SRC-F4-AP-472"])
def fs_pitchover(low, crt, qopt):
    fw = {1, 2, 7}
    return {"value": int(int(low) in fw) + int(int(crt) in fw) + int((int(qopt) >> 20) & 1)}


@kit.calc("CALC-F4-YAW-ACC", title="Yaw acceleration limit of the attitude shaper against the airframe's yaw authority",
          equation="a_set = Q_A_ACC_Y_MAX x pi/180 ; r = a_set / a_yaw(30 % differential, half-fin factor)",
          inputs={"a": "P:fsw.yaw_acc_max_degs2", "ay": "CL-B3-HOVER-YAW-ACCEL-LOW"}, units={"a": "deg/s2", "ay": "rad/s2"},
          cites=["SRC-F4-AP-PDEF", "SRC-F4-AP-RELNOTES"])
def yaw_acc(a, ay):
    return {"a_set_rads2": math.radians(a), "ratio": math.radians(a) / ay, "old_unit_cdegs2": a * 100.0}


@kit.calc("CALC-F4-RC-FS", title="RC loss to QLAND in a Q mode (4.7: the short failsafe event selects QLAND)",
          equation="t = RC_FS_TIMEOUT + debounce",
          inputs={"t": "P:fsw.rc_fs_timeout_s", "d": "ASM-F4-FS-COUNT", "tl": "P:fsw.fs_long_timeout_s"},
          units={"t": "s", "d": "s", "tl": "s"}, assumes=["ASM-F4-FS-COUNT"], cites=["SRC-F4-AP-EVENTS", "SRC-F4-AP-RELNOTES"])
def rc_fs(t, d, tl):
    return {"t_qland_s": t + d, "t_fw_rtl_s": float(tl)}


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
kit.claim("CL-F4-ARSPD-MIN-FACTOR", "AIRSPEED_MIN over stall at the gate", calc="CALC-F4-ARSPD",
          output="min_factor", limit=(">=", "ASM-F4-MIN-FACTOR"), parts=FC,
          how="Slow-flight stall test T-B2-STALL; re-run when A1/B3 re-issue the stall.")
kit.claim("CL-F4-ARSPD-MIN-D71", "AIRSPEED_MIN against 1.3 x the stall at the gate mass and the forward CG (D-71)",
          calc="CALC-F4-ARSPD", output="vmin", unit="m/s", limit=(">=", "CL-B2R3-VTR-GATE-FWD"),
          verifies=["R-STALL", "R-TRANSITION"], parts=FC,
          how="T-B2-STALL (three slow-flight stalls at 2.6 kg, forward CG, airspeed logged): set AIRSPEED_MIN = "
              "ceil(1.3 x measured trimmed stall); 16 holds while the measured stall is <= 12.31 m/s (vs_keep).")
kit.claim("CL-F4-ARSPD-MIN-FLOOR", "AIRSPEED_MIN against the transition end speed transition_min_ms (17 m/s, D-145; was the D-36 15.6)", calc="CALC-F4-ARSPD", output="vmin",
          unit="m/s", limit=(">=", "P:performance.transition_min_ms"), verifies=["R-TRANSITION"], parts=FC,
          how="Read AIRSPEED_MIN after loading (integer: 17).")
kit.claim("CL-F4-VDIVE-VA", "Steady dive speed at the pitch floor, idle, against the full-travel speed VA",
          calc="CALC-F4-DIVE", output="v_dive", unit="m/s", limit=("<=", "ASM-F4-VA-SCHED"), parts=FC,
          how="FBWA full-down stick at >= 80 m, throttle idle, 20 s: logged airspeed <= 20.5 m/s (T-F4-DIVE).")
kit.claim("CL-F4-SCALER-VD", "Surface demand scaling at VD (fraction of the cruise deflection per unit demand)",
          calc="CALC-F4-DIVE", output="scaler_vd", limit=("<=", 1.0), parts=FC,
          how="Information: the speed scaler alone does not hold <= 1/3 at VD; the schedule rests on CL-F4-VDIVE-VA "
              "and CL-F4-VLEVEL-VH (CR-F4-12).")
kit.claim("CL-F4-VLEVEL-VH", "FW output at THR_MAX over the output that reaches VH 21.8 m/s (= VD 27.2 / 1.25) in level "
          "flight, fresh pack, B4's in-flight prop model", calc="CALC-F4-VLEVEL", output="ratio", limit=("<=", 1.0), parts=FC,
          how="FBWB full-throttle level leg, fresh pack, >= 60 m (H2 gate 5, TUNING-PLAN 6c): logged airspeed <= 21.8 m/s; "
              "TECS caps demand at AIRSPEED_MAX 18 in normal flight.")
kit.claim("CL-F4-VLEVEL", "Level speed at THR_MAX 41 with FWD_BAT compensation on a sagged pack (F4 estimate, D-174)", calc="CALC-F4-VLEVEL",
          output="v_lvl_sag", unit="m/s", limit=(">=", "P:fsw.airspeed_max_ms"), parts=FC,
          how="FBWB full-throttle level leg flown late in a pack (H2 gate 5): logged airspeed >= 18 m/s. Below it TECS "
              "saturates at THR_MAX and trades height for speed within TECS_SINK_MAX; AIRSPEED_MIN 17 keeps +7 %.")
kit.claim("CL-F4-XOVER-RLL", "Hover copter-roll rate-loop crossover", calc="CALC-F4-XOVER", output="f_rll_hz", unit="Hz",
          limit=("<=", "ASM-F4-XOVER-MAX"), verifies=["R-VIBRATION"], parts=FC,
          how="Tethered hover: doublets on the rate loop (RATE log), crossover from the log; P stays below p_ceiling.")
kit.claim("CL-F4-XOVER-PIT", "Hover copter-pitch rate-loop crossover (stiffest axis)", calc="CALC-F4-XOVER",
          output="f_pit_hz", unit="Hz", limit=("<=", "CL-B3-XOVER-MAX-PITCH"), verifies=["R-VIBRATION"], parts=FC,
          how="As roll; after QAUTOTUNE reject any Q_A_RAT_PIT_P above p_ceiling_pit.")
kit.claim("CL-F4-XOVER-YAW", "Hover copter-yaw rate-loop crossover", calc="CALC-F4-XOVER", output="f_yaw_hz", unit="Hz",
          limit=("<=", "CL-B3-XOVER-MAX-YAW"), parts=FC, how="As roll.")
kit.claim("CL-F4-FILT-SEP", "Gyro / D-term low-pass over the top of the torsion band", calc="CALC-F4-FILT",
          output="value", limit=(">=", "ASM-F4-FILT-SEP"), verifies=["R-VIBRATION"], parts=FC,
          how="Read INS_GYRO_FILTER and Q_A_RAT_*_FLTD after loading; T-C2-TAP-TEST gives the measured mode.")
kit.claim("CL-F4-TD-CUT", "Touchdown to motors below spin-min (RC9 cut)", calc="CALC-F4-TD-CUT", output="value",
          unit="s", limit=("<=", "ASM-F4-TD-REQ"), parts=FC + MOT,
          how="Twin: 20 logged touchdowns, contact (IMU spike) to RCOU at minimum <= 0.5 s (H2, CR-F4-14).")
kit.claim("CL-F4-CANT-SENSE-D3", "D3's printed cant sense agrees with the motor map (+1 agree, -1 reversed)",
          calc="CALC-F4-MOTOR-MAP", output="d3_sense_agree", limit=(">=", 1), parts=MOT,
          how="Look along the UR shaft from the nose: the prop end must lean outboard (+y) and toward the wing "
              "plane (-z); D3 sets cant_sense_UR = d3_sense_needed (CR-F4-11).")
kit.claim("CL-F4-SPLIT-OUT", "Upper-pair hover output at the A3 split, 30 % control reserve, sagged pack",
          calc="CALC-F4-SPLIT", output="a_up", limit=("<=", "P:fsw.spin_max"), parts=MOT,
          how="Tethered-hover log on a pack near BATT_LOW: mean RCOU of the upper pair (UR, UL) / lower pair gives the "
              "split; peak upper-pair RCOU during pitch inputs stays below 0.84 (CR-A3-04, R-HOVER-SPLIT).")
kit.claim("CL-F4-SPLIT-OUT-LIMIT", "Upper-pair hover output at the 1.25 split limit (D-18), same reserve and pack",
          calc="CALC-F4-SPLIT", output="a_up_at_limit", limit=("<=", "P:fsw.spin_max"), parts=MOT,
          how="As CL-F4-SPLIT-OUT; holds for any CG z A3 can report within R-HOVER-SPLIT.")
kit.claim("CL-F4-BAT-CURR-MAX", "Parameter file sets Q_M_BAT_CURR_MAX = 80 A on the flight pack (Q_M_BAT_IDX 0; D-174)",
          calc="CALC-F4-BAT-CURR", output="i_set_a", unit="A", limit=("<=", "P:performance.full_throttle_current_a"),
          verifies=["R-ESC-CURRENT", "R-FSW-PARAMS"], parts=FC + ["PWR-001"],
          how="T-F1-SENSOR-CAL first (current reading within +/-1.1 % at 70-75 A, BATT_AMP_PERVLT set from it), then a "
              "parameter diff of the board against K09L.param: Q_M_BAT_CURR_MAX 80, Q_M_BAT_IDX 0, Q_M_BAT_CURR_TC 1; "
              "H1's restrained four-motor run shows BAT.Curr <= 80 A (D-174).")
kit.claim("CL-F4-CRUISE-TRANS", "AIRSPEED_CRUISE over 1.3 Vs", calc="CALC-F4-ARSPD", output="cruise_over_trans",
          limit=(">=", 1.0), verifies=["R-TRANSITION"], parts=FC,
          how="SITL S4 and flight logs: airspeed reaches 16 m/s after every pitch-over before the first turn.")
kit.claim("CL-F4-ARSPD-MAX-VA", "AIRSPEED_MAX against manoeuvre speed VA", calc="CALC-F4-ARSPD", output="vmax", unit="m/s",
          limit=("<=", "ASM-F4-VA-SCHED"), parts=FC, how="Read AIRSPEED_MAX after loading; C1 re-derives VA.")
kit.claim("CL-F4-ARSPD-MAX-CAP", "AIRSPEED_MAX against the 22 m/s ARSPD_FBW_MAX ceiling (CR-C1-08)", calc="CALC-F4-ARSPD", output="vmax", unit="m/s",
          limit=("<=", "ASM-F4-ARSPD-CAP"), parts=FC, how="Read AIRSPEED_MAX after loading.")
kit.claim("CL-F4-ARSPD-MAX-VMAX", "AIRSPEED_MAX reachable in level flight at THR_MAX", calc="CALC-F4-ARSPD", output="vmax", unit="m/s",
          limit=("<=", "CL-F4-VLEVEL"), parts=FC, how="FBWB full-stick leg on the cruise-power test.")
kit.claim("CL-F4-SPIN-MAX", "Q-mode motor output cap", calc="CALC-F4-ACT-CAP", output="a_q",
          limit=("<=", "CL-B4-SPIN-MAX"), verifies=["R-ESC-CURRENT"], parts=MOT,
          how="Stand, fresh pack, one motor at full stick with the others light (E1 D-173): winding <= 50 A, ESC <= 45 A, rpm <= 13 360 "
              "(T-F4-STAND-RPM-CAP); on a worst-state pack the 75 A limiter binds before 0.81 (E1).")
kit.claim("CL-F4-SPIN-MAX-A1", "Q_M_SPIN_MAX as set against A1's P:fsw.q_m_spin_max (D-174), difference",
          calc="CALC-F4-SPIN-A1", output="diff", limit=("<=", 0.0), verifies=["R-ESC-CURRENT"], parts=MOT,
          how="Parameter diff of the board against K09L.param: Q_M_SPIN_MAX 0.81.")
kit.claim("CL-F4-FW-ACT-MAX", "FW motor output cap incl. yaw differential against B4's in-flight cap at VD",
          calc="CALC-F4-ACT-CAP", output="a_fw", limit=("<=", "CL-B4-FW-CAP-VD"), parts=MOT,
          how="SITL S4: RCOU of each motor at FBWA full throttle with full rudder = 0.60 + 0.0875 of range (pass-through).")
kit.claim("CL-F4-RUDD-DT-REQ", "RUDD_DT_GAIN needed for 1.0 N*m cruise yaw", calc="CALC-F4-YAW-DT",
          output="gain_req_pct", unit="%", limit=("<=", "P:fsw.rudd_dt_gain_pct"), parts=MOT,
          how="FBWA yaw doublet on the twin, then on K09-L at 16 m/s (T-B3-YAW-DOUBLET): yaw rate damps in < 2 cycles.")
kit.claim("CL-F4-YAW-LOW-SIDE", "Output of the slow side at full yaw demand in cruise", calc="CALC-F4-YAW-DT",
          output="a_low_side", limit=(">=", 0.05), parts=MOT,
          how="Flight log RCOU at full rudder in cruise: no motor below 5 % output.")
kit.claim("CL-F4-DESCENT", "Fastest commanded vertical descent", calc="CALC-F4-DESCENT", output="value", unit="m/s",
          limit=("<=", "CL-B4-DESCENT"), verifies=["R-FAILSAFES"], parts=MOT,
          how="QLAND and QHOVER full-down logs: CTUN/QTUN DCRt >= -1.2 m/s.")
kit.claim("CL-F4-TOUCHDOWN-SINK", "Fastest commanded descent that can reach the ground (QHOVER/QLOITER full down stick, "
          "QLAND final) against the hard-landing sink", calc="CALC-F4-DESCENT", output="touchdown", unit="m/s",
          limit=("<=", "P:requirements.landing_sink_ms"), verifies=["R-LANDING-IMPACT"], parts=FC,
          how="QHOVER full-down-stick log from 10 m to touchdown on the twin: CTUN/QTUN CRt at contact >= -1.2 m/s "
              "(peak overshoot read from the log). QSTABILIZE has no climb-rate loop: the flight card bars landing in "
              "it (CR-F4-21).")
kit.claim("CL-F4-NO-RAW-MODES", "Raw-stick modes among FLTMODE1-6 and INITIAL_MODE (R-SPIRAL, D-66)",
          calc="CALC-F4-FLTMODES", output="value", limit=("<=", 0), verifies=["R-SPIRAL", "R-FSW-PARAMS"], parts=FC,
          how="Lint of K09L.param by fsw_check.py (17 / 18 / 19 / 5 / 7 / 11, boot 17) and a parameter diff of the board "
              "after loading; H3's card forbids MANUAL / ACRO / STABILIZE from the GCS.")
kit.claim("CL-F4-BODY-RATE", "Largest commanded body rate", calc="CALC-F4-RATES", output="value", unit="rad/s",
          limit=("<=", "ASM-C1-PITCH-RATE"), parts=FC, how="Read the six rate limits after loading; log RATE in QAUTOTUNE.")
kit.claim("CL-F4-NOTCH-LOW", "Lowest steady 1P (cruise, D-173) over the lowest notch frequency", calc="CALC-F4-NOTCH", output="low_ratio",
          limit=(">=", 1.1), verifies=["R-VIBRATION"], parts=FC,
          how="Hover FFT (INS_LOG_BAT) with the notch on: no gyro peak above the noise floor at 1P or 2P.")
kit.claim("CL-F4-NOTCH-TOP", "Highest notch harmonic at the rpm cap over gyro Nyquist", calc="CALC-F4-NOTCH",
          output="top_ratio", limit=("<=", 1.0), parts=FC, how="Confirm INS_GYRO_RATE on the chosen board (F3).")
kit.claim("CL-F4-NOTCH-2P-265", "2P at full throttle on the limiter (264.7 Hz) over the notch's 0.48 x sample-rate ceiling", calc="CALC-F4-NOTCH-2P",
          output="ratio", limit=("<=", 1.0), verifies=["R-VIBRATION"], parts=FC,
          how="Full-throttle run (T-C4-TAP-D3 / VIBE): post-filter gyro FFT shows no peak at 2P (241-265 Hz) above the noise floor.")
kit.claim("CL-F4-BATT-CRT", "BATT_CRT_MAH over the 20 % reserve", calc="CALC-F4-BATT", output="value", limit=(">=", 1.0),
          verifies=["R-FAILSAFES", "R-MISSION"], parts=["PWR-001"],
          how="SITL S8 and props-off bench with a bench supply: low -> RTL, critical -> QLAND.")
kit.claim("CL-F4-BATT-LOW", "BATT_LOW_MAH set against E2's landing allowance", calc="CALC-F4-BATT-LOW",
          output="value", unit="mAh",
          limit=(">=", "CL-E2-BATT-LOW-MAH-V17"), verifies=["R-FAILSAFES"], parts=["PWR-001"],
          how="Read BATT_LOW_MAH after loading: 3 000 (E2 D-173, Gens Ace 6.0 Ah HV Shorty). BATT_CAPACITY = the "
              "lowest measured T-E2-CAPACITY of the packs flown (placeholder 5 520 = 0.92 x 6 000 until measured).")
kit.claim("CL-F4-FENCE-ALT", "FENCE_ALT_MAX over the 400 ft ceiling", calc="CALC-F4-FENCE", output="alt_ratio",
          limit=("<=", 0.95), verifies=["R-FAILSAFES"], parts=FC, how="SITL S9: climb through 110 m triggers RTL.")
kit.claim("CL-F4-FENCE-RADIUS", "FENCE_RADIUS over VLOS", calc="CALC-F4-FENCE", output="rad_ratio",
          limit=("<=", 1.0), verifies=["R-FAILSAFES"], parts=FC, how="SITL S9; H3 checks the circle sits inside the sub-field.")
kit.claim("CL-F4-BAT-CURR-MOTOR", "Per-motor share of the 70.2 A limiter against the 25 A motor rating",
          calc="CALC-F4-BAT-CURR", output="i_motor_a", unit="A", limit=("<=", "P:propulsion.motor_max_a"),
          verifies=["R-ESC-CURRENT"], parts=MOT,
          how="T-H1-RESTRAINED-RUN: ESC telemetry current per motor <= 25 A during the 2 s full-throttle run.")
kit.claim("CL-F4-LAND-SPD", "Final landing descent against the no-set touchdown speed of the foot cartridges",
          calc="CALC-F4-LAND-SPD", output="value", unit="m/s", limit=("<=", "CL-D5-V-NO-SET"),
          parts=FC, how="QLAND logs: CTUN/QTUN climb rate over the last 1 m >= -0.3 m/s; cartridge set read after 10 "
          "landings (CR-D5-21).")
kit.claim("CL-F4-SENSOR-POS-ERR", "INS_POS / GPS1_POS as set against F3's points and the CG", calc="CALC-F4-SENSOR-POS",
          output="err_m", unit="m", limit=("<=", 0.002), parts=FC + ["AVN-002"],
          how="Measure the as-built IMU and GPS centres from the CG mark (T-A3-CG-BALANCE) and reset the six lines.")
kit.claim("CL-F4-ELEVON-PWM-ERR", "SERVO5/6 MIN/MAX as set against D6's +/-25 deg servo angles",
          calc="CALC-F4-ELEVON-PWM", output="err_us", unit="us", limit=("<=", 1.5), parts=FC,
          how="T-D6-THROW: protractor on each trailing edge at full pitch + roll demand reads +25 / -25 deg; the "
          "bench values replace these starting values.")
kit.claim("CL-F4-ELEVON-PWM-SPAN", "Largest servo pulse excursion from trim", calc="CALC-F4-ELEVON-PWM",
          output="span_us", unit="us", limit=("<=", 500.0), parts=FC,
          how="T-D6-THROW; the 500 us end is D6's assumed +/-45 deg servo range (ASM-D6-SERVO-THROW).")
kit.claim("CL-F4-ARSPD-TRIP-NEED", "1.3 x the tripped stall at the gate mass, forward CG (B2 XFOIL tripped, 12.85 m/s)",
          calc="CALC-F4-ARSPD-TRIP", output="v_need", unit="m/s", parts=FC,
          how="T-B2-STALL replaces the tripped-section estimate with the measured trimmed stall.")
kit.claim("CL-F4-ARSPD-MIN-TRIP", "AIRSPEED_MIN against 1.3 x the tripped stall at the gate mass, forward CG (B6 baseline)",
          calc="CALC-F4-ARSPD-TRIP", output="vmin", unit="m/s", limit=(">=", "CL-F4-ARSPD-TRIP-NEED"),
          verifies=["R-STALL", "R-TRANSITION"], parts=FC,
          how="T-B2-STALL with the real LE tape seam (twin, then K09-L): AIRSPEED_MIN = ceil(1.3 x measured trimmed "
              "stall); 17 holds to 13.07 m/s, the second fallback 18 to 13.85 m/s (vs_keep, vs_keep_fb2).")
kit.claim("CL-F4-YAW-ACC-SET", "Q_A_ACC_Y_MAX over the hover yaw acceleration at 30 % differential",
          calc="CALC-F4-YAW-ACC", output="ratio", limit=("<=", "ASM-F4-YAW-ACC-FRAC"), verifies=["R-FSW-PARAMS"],
          parts=FC + MOT,
          how="Read Q_A_ACC_Y_MAX after loading (135 deg/s/s; the 4.6 name Q_A_ACCEL_Y_MAX must not load). T-B4-YAW "
              "(hanging yaw stand) measures the yaw moment per differential; re-set to 0.85 x the measured value.")
kit.claim("CL-F4-RC-FS-QLAND", "RC loss to QLAND in QSTABILIZE / QHOVER / QLOITER", calc="CALC-F4-RC-FS",
          output="t_qland_s", unit="s", limit=("<=", "ASM-F4-QLAND-MAX"), verifies=["R-FAILSAFES"], parts=FC,
          how="SITL S7 (measured 1.15 s on the stock tailsitter model, 2026-11-13) and T-F5-BENCH step 9: transmitter "
              "off, props off, QHOVER selected: the HUD shows QLAND within 3 s. Needs the receiver in failsafe mode "
              "No Pulses (RC-LINK.md).")
kit.claim("CL-F4-PTCH-RMAX-UP", "FW pull-up pitch-rate cap PTCH2SRV_RMAX_UP against C1's ceiling for n 3.4 at VD",
          calc="CALC-F4-PTCH-RMAX", output="q_up", unit="deg/s", limit=("<=", "CL-C1-Q-UP-MAX"), verifies=["R-LOADS"],
          parts=FC, how="TUNING-PLAN 6e: FBWA full-pull step at AIRSPEED_MAX; logged peak pitch rate <= 1.25 x 35 = 43.75 deg/s.")
kit.claim("CL-F4-PTCH-RMAX-DN", "FW push-over pitch-rate cap PTCH2SRV_RMAX_DN against C1's ceiling for n -1.5 at VD",
          calc="CALC-F4-PTCH-RMAX", output="q_dn", unit="deg/s", limit=("<=", "CL-C1-Q-DN-MAX"), verifies=["R-LOADS"],
          parts=FC, how="TUNING-PLAN 6e: FBWA full-push step at AIRSPEED_MAX; logged peak rate <= 1.25 x 20 = 25 deg/s.")
kit.claim("CL-F4-PTCH-RMAX-TURN", "Pitch rate a coordinated turn at ROLL_LIMIT_DEG needs at AIRSPEED_MIN, as a fraction "
          "of the pull-up cap PTCH2SRV_RMAX_UP", calc="CALC-F4-PTCH-RMAX", output="turn_frac", limit=("<=", 1.0),
          parts=FC, how="FBWA 45 deg banked turn at 17 m/s on the twin: height held, pitch-rate demand below the cap "
          "(PIDP.Tar <= 35 deg/s; need 23.4 deg/s).")
kit.claim("CL-F4-QASSIST-TRIGGERS", "Q-assist triggers that can run the multicopter mixer at any airspeed (Q_ASSIST_ALT, "
          "Q_ASSIST_ANGLE)", calc="CALC-F4-QASSIST", output="n_trig", limit=("<=", 0), verifies=["R-FSW-PARAMS"],
          parts=FC + MOT, how="Parameter diff after loading: Q_ASSIST_ALT 0, Q_ASSIST_ANGLE 0, Q_ASSIST_SPEED 14. SITL: "
          "FBWA upset at 18 m/s gives no 'Angle assist' message (SITL-PLAN S22).")
kit.claim("CL-F4-QASSIST-N", "Load factor the speed-triggered assist can reach: stall line at Q_ASSIST_SPEED",
          calc="CALC-F4-QASSIST", output="n_assist", limit=("<=", "CL-C1-N-LIMIT-POS"), verifies=["R-LOADS"], parts=FC,
          how="Below 14 m/s the wing stalls before n 1.38, whatever the motor rate loop asks; T-B2-STALL measures Vs.")
kit.claim("CL-F4-ANGLE-BOOST", "Q_A_ANGLE_BOOST as set (must be 0: the pitch-over holds throttle with boost applied)",
          calc="CALC-F4-TRANS-ENTRY", output="boost", limit=("<=", 0), verifies=["R-TRANSITION"], parts=FC,
          how="Parameter diff after loading; SITL S4c reads Q_A_ANGLE_BOOST 0 and a flat CTUN/QTUN throttle through the "
              "pitch-over.")
kit.claim("CL-F4-TRANS-MS-RATE", "Pitch-over rate the firmware would derive from Q_TRANSITION_MS if Q_TAILSIT_RAT_FW were "
          "unconfigured, error against Q_TAILSIT_RAT_FW", calc="CALC-F4-TRANS-ENTRY", output="err", unit="deg/s",
          limit=("<=", 0.1), parts=FC, how="Parameter diff after loading (Q_TRANSITION_MS 11667).")
kit.claim("CL-F4-FS-Q-PITCHOVER", "Battery-failsafe and RC-failsafe actions that start a forward transition from a Q mode",
          calc="CALC-F4-FS-PITCHOVER", output="value", limit=("<=", 0), verifies=["R-FAILSAFES", "R-TRANSITION"], parts=FC,
          how="SITL S8 (2026-11-14, stock tailsitter model): BATT_FS_LOW_ACT 6 in QLOITER at 60 m -> QLAND, no pitch-over; "
              "control run with 1 -> RTL and a pitch-over. S7a: RC loss in a Q mode -> QLAND.")
kit.claim("CL-F4-MIX-PITCH", "Trimmed-CLmax elevon need at the CG target over the pure-pitch travel MIXING_GAIN leaves",
          calc="CALC-F4-MIX", output="ratio", limit=("<=", 1.0), parts=FC,
          how="T-B2-STALL slow flight in FBWA: elevon output not at the pitch end at the stall break.")

# ---------------------------------------------------------------- tests (all planned)
kit.test("T-F4-SITL-NAMES", "Load K09L.param in SITL and on the board; no unknown name. SITL part run 2026-11-13 "
         "(ArduPlane 4.7.3-beta1 Windows SITL): 156 of 158 names accepted and read back after a reboot; "
         "SERVO_BLH_BDMASK and SERVO_BLH_POLES are not in the SITL build (board only). Board part: T-F3-FW-LOAD",
         verifies=["CL-F4-MOTOR-MAP-ERR", "CL-F4-SPIN-MAX"], procedure="SITL-PLAN.md S1; team/F4/sitl/RESULTS.md")
kit.test("T-F4-BENCH-MAP", "Props-off motor order, rotation and elevon direction",
         verifies=["CL-F4-MOTOR-MAP-ERR"], procedure="TUNING-PLAN.md step 1")
kit.test("T-F4-STAND-RPM-CAP", "Fresh-pack full-stick rpm and pack current on the stand",
         verifies=["CL-F4-SPIN-MAX"], procedure="TUNING-PLAN.md step 2: ESC rpm <= 13 360, BAT.Curr <= 73.2 A")
kit.test("T-F4-SITL-FAILSAFES", "RC, battery, geofence, GPS/EKF, transition-fail and e-stop in SITL",
         verifies=["CL-F4-BATT-CRT", "CL-F4-FENCE-ALT", "CL-F4-FENCE-RADIUS", "CL-F4-DESCENT"],
         procedure="SITL-PLAN.md S7-S13")
kit.test("T-F4-SITL-TRANSITION", "Pitch-over 12/16 deg/s (CR-B1-12) and back-transition 20/30/50 deg/s on a sagged pack",
         verifies=["CL-F4-CRUISE-TRANS", "CL-F4-FW-ACT-MAX"], procedure="SITL-PLAN.md S4-S5")
kit.test("T-F4-DIVE", "FBWA full-down stick, idle, 20 s at >= 80 m on the twin then K09-L",
         verifies=["CL-F4-VDIVE-VA"], procedure="TUNING-PLAN.md step 6b")
kit.test("T-F4-TD-CUT", "Touchdown cut timing on 20 twin landings", verifies=["CL-F4-TD-CUT"],
         procedure="TUNING-PLAN.md step 5; H2 logs")
kit.test("T-F4-HANG-YAW", "Hanging yaw test before first hover (CR-B4-16b): airframe nose-up on one line, UR + LL "
         "only at low throttle; frame yaws the way of their reaction torque (-x); repeat with UL + LR (+x)",
         verifies=["CL-F4-CANT-SENSE-D3", "CL-F4-MOTOR-MAP-ERR"], procedure="TUNING-PLAN.md step 1b")
kit.test("T-F4-THRUST-LAG", "Motor thrust lag on the stand: 10 % output step, time to 63 % of the thrust change "
         "(CR-B3-19: below 30 ms the 4 Hz pitch margin falls under 6 dB)", verifies=["CL-F4-XOVER-PIT"],
         procedure="TUNING-PLAN.md step 2")
kit.test("T-F4-SITL-MOTOR-OUT", "Motor-failure injection in hover, pitch-over and cruise",
         verifies=["CL-F4-YAW-LOW-SIDE"], procedure="SITL-PLAN.md S11 (SIM_ENGINE_FAIL, SIM_ENGINE_MUL)")


# ---------------------------------------------------------------- lint of the parameter file (not a claim)
def load_names():
    """Parameter names of ArduPlane stable-4.7.1 (SRC-F4-AP-PDEF). One name per line; lines starting '#' are the header."""
    return {ln.strip() for ln in NAMES_FILE.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")}


# Names that existed up to 4.6 and that ArduPlane 4.7 removed or renamed (SRC-F4-AP-RELNOTES; each new name is in the
# 4.7.1 list). A K09L line under an old name would be skipped silently by the loader, so it is a lint error here.
RENAMED_47 = {
    "FS_SHORT_TIMEOUT": "removed (PR 30350); RC loss time is RC_FS_TIMEOUT",
    "Q_A_ACCEL_Y_MAX": "Q_A_ACC_Y_MAX in deg/s/s (PR 32192; was cdeg/s/s)",
    "Q_A_ACCEL_R_MAX": "Q_A_ACC_R_MAX in deg/s/s (PR 32192)",
    "Q_A_ACCEL_P_MAX": "Q_A_ACC_P_MAX in deg/s/s (PR 32192)",
    "Q_ANGLE_MAX": "Q_A_ANGLE_MAX in deg (PR 31978; was cdeg)",
    "Q_WP_SPEED_DN": "Q_WP_SPD_DN in m/s (PR 32147)",
    "Q_WP_SPEED_UP": "Q_WP_SPD_UP in m/s (PR 32147)",
    "Q_WP_SPEED": "Q_WP_SPD in m/s (PR 32147)",
    "Q_PILOT_SPEED_DN": "Q_PILOT_SPD_DN in m/s (4.7 list)",
    "Q_PILOT_SPEED_UP": "Q_PILOT_SPD_UP in m/s (4.7 list)",
    "Q_LAND_SPEED": "Q_LAND_FINAL_SPD in m/s (4.7 list)",
    "Q_P_VELXY_P": "Q_P_NE_VEL_P (PR 30683)",
    "Q_P_POSXY_P": "Q_P_NE_POS_P (PR 30683)",
    "GPS_POS1_X": "GPS1_POS_X (4.6)", "GPS_POS1_Y": "GPS1_POS_Y (4.6)", "GPS_POS1_Z": "GPS1_POS_Z (4.6)",
    "ARSPD_FBW_MIN": "AIRSPEED_MIN (4.5)", "ARSPD_FBW_MAX": "AIRSPEED_MAX (4.5)",
}
# In the 4.7.1 list but not in the SITL build (no BLHeli / bidirectional-DShot backend there): read back on the board only.
BOARD_ONLY = {"SERVO_BLH_BDMASK", "SERVO_BLH_POLES"}


def name_check(values, known, label):
    errs = [f"{label}: {n} is a pre-4.7 name: {RENAMED_47[n]}" for n in values if n in RENAMED_47]
    errs += [f"{label}: {n} is not an ArduPlane 4.7.1 parameter name ({NAMES_FILE.name})"
             for n in values if n not in known and n not in RENAMED_47]
    return errs


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


RC_RAW_MODE_OPTIONS = {51: "MANUAL mode", 52: "ACRO mode"}   # RCn_OPTION aux functions that select a raw-stick mode


def rc_option_check(values):
    """No RC aux switch may select a raw-stick mode (R-SPIRAL); option numbers to confirm in SITL S1."""
    return [f"{n} = {int(v)} selects {RC_RAW_MODE_OPTIONS[int(v)]} (R-SPIRAL)" for n, v in values.items()
            if n.startswith("RC") and n.endswith("_OPTION") and n != "RC_OPTIONS" and int(v) in RC_RAW_MODE_OPTIONS]


if __name__ == "__main__":
    vals, errs = lint(PARAM_FILE)
    errs += rc_option_check(vals)
    errs += mirror_check(vals)
    svals, serrs = lint(STAND_FILE)
    errs += [f"{STAND_FILE.name}: {e}" for e in serrs]
    known = load_names()
    name_errs = name_check(vals, known, PARAM_FILE.name) + name_check(svals, known, STAND_FILE.name)
    errs += name_errs
    print(f"{PARAM_FILE.name}: {len(vals)} parameters, {STAND_FILE.name}: {len(svals)}; {len(known)} names in "
          f"{NAMES_FILE.name}; {len(vals) + len(svals) - len(name_errs)} of {len(vals) + len(svals)} names matched "
          f"(ArduPlane stable-4.7.1), {len(name_errs)} unknown or renamed; board-only (not in SITL): "
          f"{' '.join(sorted(BOARD_ONLY & set(vals)))}")
    kit.write()
    mm = kit.nodes["CALC-F4-MOTOR-MAP"]["outputs"]
    print("motor map (station: [AP motor, rotation seen from the nose]):", mm["derived"])
    print("cant side-force direction (y, z unit vector) per station:", mm["cant_dir_yz"])
    print(f"D3 cant_sense_UR needed {mm['d3_sense_needed']:+d}, agreement {mm['d3_sense_agree']:+d}")
    xo = kit.nodes["CALC-F4-XOVER"]["outputs"]
    print("crossover Hz / P ceiling at the axis limit (4.5/4.5/2.4 Hz):", {a: (round(xo[f'f_{a}_hz'], 2), round(xo[f'p_ceiling_{a}'], 3))
                                                 for a in ("rll", "pit", "yaw")})
    dv = kit.nodes["CALC-F4-DIVE"]["outputs"]
    print(f"dive: V {dv['v_dive']:.2f} m/s, CD0 {dv['cd0']:.4f}, scaler VA {dv['scaler_va']:.3f} VD {dv['scaler_vd']:.3f}")
    sp = kit.nodes["CALC-F4-SPLIT"]["outputs"]
    print(f"hover split: upper-pair output {sp['a_up']:.3f} at A3's split, {sp['a_up_at_limit']:.3f} at 1.25 (cap 0.84)")
    fm = kit.nodes["CALC-F4-FLTMODES"]["outputs"]
    ar = kit.nodes["CALC-F4-ARSPD"]["outputs"]
    de = kit.nodes["CALC-F4-DESCENT"]["outputs"]
    so = kit.nodes["CALC-F4-SENSOR-POS"]["outputs"]
    print(f"R5: raw-stick modes {fm['value']} {fm['raw']}; touchdown sink {de['touchdown']} m/s; AIRSPEED_MIN "
          f"{ar['vmin']:.0f} holds to a measured stall of {ar['vs_keep']:.2f} m/s; sensor offsets INS "
          f"{[round(v, 4) for v in so['ins_derived_m']]} GPS {[round(v, 4) for v in so['gps_derived_m']]} "
          f"(err {so['err_m'] * 1000:.2f} mm)")
    yd = kit.nodes["CALC-F4-YAW-DT"]["outputs"]
    print(f"yaw: cruise output {yd['a_cruise']:.3f}, dT {yd['dT_N']:.2f} N/motor, slow side {yd['a_low_side']:.3f}")
    if errs:
        print("LINT ERRORS:\n  " + "\n  ".join(errs))
        sys.exit(1)
    print("lint: OK (every parameter commented, no duplicates, params.json mirrors K09L.param)")
