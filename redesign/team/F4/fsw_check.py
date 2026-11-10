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
stall need. Lints K09L.param and the stand overlay K09L-STAND.param.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
import proofkit as pk  # noqa: E402

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
kit.assumption("ASM-F4-FW-PASSTHRU", "Fixed-wing motor output bypasses Q_M_SPIN_MAX",
               "In fixed-wing flight the tailsitter sends throttle to the motors through output_motor_mask(); whether that "
               "path applies thrust_to_actuator() (Q_M_SPIN_MIN/MAX, Q_M_THST_EXPO) is not settled from source here. "
               "F4 uses the higher of the two outputs (pass-through or linearised) for every speed and rpm cap; the "
               "two agree within 0.01 at THR_MAX 70", basis="tailsitter.cpp output(), AP_MotorsMulticopter::"
               "output_motor_mask(); SITL S4 logs RCOU at FW full throttle and settles which path the build uses",
               status="UNVERIFIED", cites=["SRC-F4-AP-SRC"])
kit.assumption("ASM-F4-RPM-LIN", "Level-flight top speed scales with motor output",
               "At the top of the level-speed range the 11x5.5 prop runs near its pitch speed, so rpm ~ output x pack "
               "voltage and VMAX ~ rpm; B1's VMAX at 9 350 rpm (output 0.849 on 16.8 V) scales by output",
               basis="team/B1/CHANGE-REQUESTS.md CR-B1-17 (7 950 rpm -> 21.8 m/s, 8 000 -> 21.9, 8 590 -> 23.6: "
               "~linear); first full-throttle level log (H2) replaces it", status="UNVERIFIED")
kit.assumption("ASM-F4-FW-RPM-REQ", "Fixed-wing rpm that holds level speed at 21.8 m/s",
               "<= 7 950 rpm (B1 option b); 21.8 m/s = VD 27.2 / 1.25, the VH C1's VD assumes", basis=
               "team/B1/CHANGE-REQUESTS.md CR-B1-17; team/C1/CHANGE-REQUESTS.md CR-C1-20 (recommended option)",
               value=7950, unit="rpm", status="UNVERIFIED")
kit.assumption("ASM-F4-THRUST-SQ", "Thrust varies with output squared",
               "Static thrust per motor T = k a^2, with k from the hover point (Q_M_THST_HOVER)",
               basis="rpm ~ duty x V and T ~ rpm^2; good to ~10 % between 0.2 and 0.85 output; the stand replaces it",
               status="UNVERIFIED")
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
               "IMU (-0.010, 0.046, 0.039) m: F3's FC point with the board 4 mm higher (old IMU z 0.035 + 0.004); "
               "GPS centre (0.075, 0, 0.178) m", basis="team/F3/CHANGE-REQUESTS.md CR-F3-20 (F3's CALC-F3-OFFSETS "
               "still holds the R3 layout); re-measure as built", value={"imu": [-0.010, 0.046, 0.039],
               "gps": [0.075, 0.0, 0.178]}, unit="m", status="UNVERIFIED")
kit.assumption("ASM-F4-CG-Z", "CG height for the sensor offsets", "+0.018 m above the chord plane, take-off case",
               basis="MASS-CG.md CG table (A3-R5, take-off basic and predicted both +0.018); A3 publishes no CG-z "
               "claim, only CL-A3-CG-Z-RANGE", value=0.018, unit="m", status="UNVERIFIED")
kit.assumption("ASM-F4-THETA-DN", "Servo angle for 25 deg TE down", "-42.9 deg (D6 linkage solution)",
               basis="team/D6/claims.json CALC-D6-KIN output theta_dn_deg -42.87 (no claim id published; "
               "CR-D6-09 quotes it)", value=-42.87, unit="deg", status="UNVERIFIED")

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
          equation="f_min = AIRSPEED_MIN / Vs ; f_cr = AIRSPEED_CRUISE / (1.3 Vs)",
          inputs={"vs": "CL-A1-STALL-GATE", "vmin": "P:fsw.airspeed_min_ms", "vcr": "P:fsw.airspeed_cruise_ms",
                  "f": "P:requirements.transition_factor", "vmax": "P:fsw.airspeed_max_ms"},
          units={"vs": "m/s", "vmin": "m/s", "vcr": "m/s", "vmax": "m/s"})
def airspeed_limits(vs, vmin, vcr, f, vmax):
    return {"min_factor": vmin / vs, "cruise_over_trans": vcr / (f * vs), "vmax": float(vmax), "vmin": float(vmin)}


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


@kit.calc("CALC-F4-VLEVEL", title="Highest level speed at THR_MAX against the VH that VD 27.2 m/s assumes",
          equation="a_pass = THR_MAX/100 ; a_lin = s_min + (s_max - s_min) (sqrt((1-e)^2 + 4 e THR_MAX/100) - (1-e)) "
                   "/ (2 e) ; a = max(a_pass, a_lin) ; V_lvl = VMAX(9 350 rpm) x a / a(9 350 rpm) ; "
                   "VH_req = VD / 1.25 ; r = V_lvl / VH_req (fresh pack: worst case, voltage scaling 1)",
          inputs={"vmax": "CL-B1-VMAX", "a_cap": "CL-B4-SPIN-MAX", "thr": "P:fsw.thr_max_pct",
                  "smax": "P:fsw.spin_max", "smin": "P:fsw.spin_min", "e": "P:fsw.thst_expo",
                  "vd": "P:requirements.vd_ms", "rpm_cap": "P:propulsion.rpm_max"},
          units={"vmax": "m/s", "thr": "%", "vd": "m/s", "rpm_cap": "rpm"}, assumes=["ASM-F4-FW-PASSTHRU", "ASM-F4-RPM-LIN"],
          cites=["SRC-F4-AP-SRC"])
def vlevel(vmax, a_cap, thr, smax, smin, e, vd, rpm_cap):
    t = thr / 100.0
    a_lin = smin + (smax - smin) * (math.sqrt((1 - e) ** 2 + 4 * e * t) - (1 - e)) / (2 * e)
    a = max(t, a_lin)
    v = vmax * a / a_cap
    vh_req = vd / 1.25
    return {"v_lvl": v, "a_fw_thr": a, "a_pass": t, "a_lin": a_lin, "vh_req": vh_req, "ratio": v / vh_req,
            "rpm_fw": rpm_cap * a / a_cap}


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


@kit.calc("CALC-F4-SENSOR-POS", title="INS_POS and GPS1_POS from F3's points and the CG (FRD body axes)",
          equation="X_fwd = -(x - x_cg) ; Y = y ; Z_down = -(z - z_cg) ; err = max |set - derived|",
          inputs={"pts": "ASM-F4-AVN-POINTS", "xcg": "P:cg.x_target_m", "zcg": "ASM-F4-CG-Z",
                  "ins": "P:fsw.ins_pos_m", "gps": "P:fsw.gps_pos_m"}, units={"xcg": "m", "zcg": "m"},
          assumes=["ASM-F4-AVN-POINTS", "ASM-F4-CG-Z"])
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
kit.claim("CL-F4-ARSPD-MIN-FLOOR", "AIRSPEED_MIN against the D-36 floor 15.6 m/s", calc="CALC-F4-ARSPD", output="vmin",
          unit="m/s", limit=(">=", "P:performance.transition_min_ms"), verifies=["R-TRANSITION"], parts=FC,
          how="Read AIRSPEED_MIN after loading (integer: 16).")
kit.claim("CL-F4-VDIVE-VA", "Steady dive speed at the pitch floor, idle, against the full-travel speed VA",
          calc="CALC-F4-DIVE", output="v_dive", unit="m/s", limit=("<=", "ASM-F4-VA-SCHED"), parts=FC,
          how="FBWA full-down stick at >= 80 m, throttle idle, 20 s: logged airspeed <= 20.5 m/s (T-F4-DIVE).")
kit.claim("CL-F4-SCALER-VD", "Surface demand scaling at VD (fraction of the cruise deflection per unit demand)",
          calc="CALC-F4-DIVE", output="scaler_vd", limit=("<=", 1.0), parts=FC,
          how="Information: the speed scaler alone does not hold <= 1/3 at VD; the schedule rests on CL-F4-VDIVE-VA "
              "and CL-F4-VLEVEL-VH (CR-F4-12).")
kit.claim("CL-F4-VLEVEL-VH", "Highest level speed at THR_MAX over the VH that VD 27.2 m/s assumes (21.8 m/s)",
          calc="CALC-F4-VLEVEL", output="ratio", limit=("<=", 1.0), parts=FC,
          how="FBWB full-throttle level leg, fresh pack, >= 60 m (H2): logged airspeed <= 21.8 m/s and ESC rpm "
              "<= 7 950 (CR-B1-17 b, CR-C1-20); TECS caps demand at AIRSPEED_MAX 18 in normal flight.")
kit.claim("CL-F4-VLEVEL", "Highest level speed at THR_MAX 70 %, fresh pack", calc="CALC-F4-VLEVEL", output="v_lvl",
          unit="m/s", limit=(">=", "P:fsw.airspeed_max_ms"), parts=FC,
          how="As CL-F4-VLEVEL-VH; the same log shows AIRSPEED_MAX 18 m/s is reachable.")
kit.claim("CL-F4-FW-RPM-CAP", "Motor rpm at THR_MAX in fixed-wing flight, fresh pack", calc="CALC-F4-VLEVEL",
          output="rpm_fw", unit="rpm", limit=("<=", "ASM-F4-FW-RPM-REQ"), parts=MOT,
          how="ESC rpm telemetry in the FBWB full-throttle leg (H2) and on the stand at RCOU = a_fw_thr.")
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
kit.claim("CL-F4-BAT-CURR-MAX", "Parameter file sets Q_M_BAT_CURR_MAX = 100 A on the flight pack (Q_M_BAT_IDX 0)",
          calc="CALC-F4-BAT-CURR", output="i_set_a", unit="A", limit=("<=", "P:performance.full_throttle_current_a"),
          verifies=["R-ESC-CURRENT", "R-FSW-PARAMS"], parts=FC + ["PWR-001"],
          how="Parameter diff of the board against K09L.param after loading: Q_M_BAT_CURR_MAX 100, Q_M_BAT_IDX 0, "
              "Q_M_BAT_CURR_TC 1; H1's restrained four-motor run shows BAT.Curr <= 100 A (CR-A2-14).")
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
          how="Read BATT_LOW_MAH after loading: 2 600 (CR-E2-20).")
kit.claim("CL-F4-FENCE-ALT", "FENCE_ALT_MAX over the 400 ft ceiling", calc="CALC-F4-FENCE", output="alt_ratio",
          limit=("<=", 0.95), verifies=["R-FAILSAFES"], parts=FC, how="SITL S9: climb through 110 m triggers RTL.")
kit.claim("CL-F4-FENCE-RADIUS", "FENCE_RADIUS over VLOS", calc="CALC-F4-FENCE", output="rad_ratio",
          limit=("<=", 1.0), verifies=["R-FAILSAFES"], parts=FC, how="SITL S9; H3 checks the circle sits inside the sub-field.")
kit.claim("CL-F4-BAT-CURR-MOTOR", "Per-motor share of the 100 A limiter against the 25 A motor rating",
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
kit.claim("CL-F4-MIX-PITCH", "Trimmed-CLmax elevon need over pure-pitch travel at MIXING_GAIN 0.5",
          calc="CALC-F4-MIX", output="ratio", limit=("<=", 1.0), parts=FC,
          how="T-B2-STALL slow flight in FBWA: elevon output not at the pitch end at the stall break.")

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
    "Q_WVANE_LAND", "Q_WVANE_TAKEOFF", "RC_OPTIONS", "SCALING_SPEED",
}
LEGACY = {"Q_WP_SPEED_DN": "Q_WP_SPD_DN", "Q_PILOT_SPEED_DN": "Q_PILOT_SPD_DN", "Q_LAND_SPEED": "Q_LAND_FINAL_SPD",
          "GPS_POS1_X": "GPS1_POS_X", "GPS_POS1_Y": "GPS1_POS_Y", "GPS_POS1_Z": "GPS1_POS_Z"}
LEGACY_SCALE = {"Q_WP_SPEED_DN": 100, "Q_PILOT_SPEED_DN": 100, "Q_LAND_SPEED": 100,
                "GPS_POS1_X": 1, "GPS_POS1_Y": 1, "GPS_POS1_Z": 1}


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
        if old in values and new in values and abs(values[old] - LEGACY_SCALE[old] * values.get(new, -1)) > 1e-6:
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
    svals, serrs = lint(STAND_FILE)
    errs += [f"{STAND_FILE.name}: {e}" for e in serrs]
    unchecked = sorted(n for n in vals if n not in CHECKED_NAMES and n not in LEGACY)
    print(f"{PARAM_FILE.name}: {len(vals)} parameters, {len(LEGACY)} LEGACY duplicates, "
          f"{len(vals) - len(unchecked) - len(LEGACY)} names matched to a source, {len(unchecked)} to match on the "
          f"installed build (SITL S1):")
    print("  " + " ".join(unchecked))
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
    yd = kit.nodes["CALC-F4-YAW-DT"]["outputs"]
    print(f"yaw: cruise output {yd['a_cruise']:.3f}, dT {yd['dT_N']:.2f} N/motor, slow side {yd['a_low_side']:.3f}")
    if errs:
        print("LINT ERRORS:\n  " + "\n  ".join(errs))
        sys.exit(1)
    print("lint: OK (every parameter commented, no duplicates, params.json mirrors K09L.param)")
