"""F3 avionics hardware: flight controller, I2C map, compass interference, FC isolation, airspeed error budget,
5 V load, FC dissipation, mass and fit.

Run:  python -I redesign/team/F3/avionics.py      -> claims.json beside this script
Then: python -I redesign/proofs/build_graph.py

Models (Python standard library only):
  magnetic dipole, worst (axial) direction:   B = mu0 m / (2 pi r^3),  m = I A
  two-wire line (spacing d), perpendicular:    B = mu0 I d / (2 pi r^2)
  base-excited single-dof isolator:            T = sqrt((1 + (2 z r)^2) / ((1 - r^2)^2 + (2 z r)^2)),  r = f / fn
  airspeed:                                    dv = dq / (rho v); error budget RSS of independent terms
All positions in the aircraft frame of params.json (x aft, y right, z up, origin wing root LE).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
MU0_2PI = 2e-7  # mu0 / (2 pi), T m / A
CHECKED = "2026-11-09"

# ---------------------------------------------------------------- sources
kit.source("SRC-F3-AP-COREWING", "ArduPilot board page: CoreWing F405 Wing V2 / Wing Mini V2", "web",
           url="https://ardupilot.org/plane/docs/common-CoreWingF405WingV2.html", checked=CHECKED,
           where="12 PWM: 10 DShot, PWM 1-4 bi-directional DShot (V2 only, not Mini); groups incl. PWM 5-7 (TIM8); "
                 "1 I2C; SERIAL5 = GPS (UART5), SERIAL6 = RCIN (USART6), SERIAL1 = wireless module; "
                 "BATT_VOLT_MULT 11.05, BATT_AMP_PERVLT 64 (V2); 90 A cont / 215 A peak sensing; FC BEC 5.2 V 4 A, "
                 "servo BEC 5/6/7.2 V 8 A cont / 14 A peak; 52 x 32 x 17 mm, 40 g; microSD logging")
kit.source("SRC-F3-HWDEF-COREWING", "ArduPilot hwdef CoreWingF405WingV2 (master)", "datasheet",
           url="https://raw.githubusercontent.com/ArduPilot/ardupilot/master/libraries/AP_HAL_ChibiOS/hwdef/"
               "CoreWingF405WingV2/hwdef.dat", checked=CHECKED,
           where="BARO SPL06 I2C:0:0x76; I2C_ORDER I2C1 (one bus); IMU ICM42688 + BMI270; PWM1 TIM4 BIDIR, PWM2 TIM4, "
                 "PWM3 TIM3 BIDIR, PWM4 TIM3, PWM5-7 TIM8, PWM8-10 TIM2, PWM11-12 TIM1 NODMA")
kit.source("SRC-F3-FW-COREWING", "ArduPilot firmware server, Plane stable, CoreWingF405WingV2", "web",
           url="https://firmware.ardupilot.org/Plane/stable/CoreWingF405WingV2/", checked=CHECKED,
           where="firmware-version.txt '4.7.2-FIRMWARE_VERSION_TYPE_OFFICIAL', files dated 2026-10-13; features.txt: "
                 "HAL_QUADPLANE_ENABLED on, harmonic notch on, AP_AIRSPEED_MS4525 on, MS5525 on, ASP5033 on, "
                 "DLVR off, QMC5883L/P on, uBlox on, logging on, CRSF on, AP_SCRIPTING off (no Lua on 1 MB flash)")
kit.source("SRC-F3-AP-TAILSITTER", "ArduPilot Plane tailsitter guide", "web",
           url="https://ardupilot.org/plane/docs/guide-tailsitter.html", checked=CHECKED,
           where="AHRS_ORIENTATION, accel calibration and level trim are done for fixed-wing flight; all tailsitters "
                 "are QuadPlanes; airspeed sensor recommended")
kit.source("SRC-F3-AP-SPEEDYBEE", "ArduPilot board page + hwdef: SpeedyBee F405 WING (fallback board)", "web",
           url="https://ardupilot.org/plane/docs/common-speedybeef405wing.html", checked=CHECKED,
           where="Plane stable folder SpeedyBeeF405WING dated 2026-10-13; BARO SPL06 0x76, one I2C; single IMU "
                 "ICM42605; servo BEC 4.5 A; 90/215 A sensing, 50 A/V; 52 x 32 x 19 mm, 35 g; bdshot not documented")
kit.source("SRC-F3-HWDEF-MATEK", "ArduPilot hwdef MatekF405-Wing (master)", "datasheet",
           url="https://raw.githubusercontent.com/ArduPilot/ardupilot/master/libraries/AP_HAL_ChibiOS/hwdef/"
               "MatekF405-Wing/hwdef.dat", checked=CHECKED,
           where="BARO BMP280 or DPS310, both I2C:0:0x76; no BIDIR outputs")
kit.source("SRC-F3-COREWING-MANUAL", "CoreWing F405 Wing manual (EN), flymod.net", "datasheet",
           url="https://flymod.net/download/corewing_f405_wing_fc_manual_en",
           where="search summary only: servo BEC 4.5 A sustained / 8 A peak, FC BEC 2.4 A (conflicts with the "
                 "ArduPilot page and listings: 8 A / 4 A). Lower values carried", status="UNVERIFIED")
kit.source("SRC-F3-D7", "Prior decision D7: airspeed sensor I2C addresses from ArduPilot driver source", "web",
           url="https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp",
           where="redesign/inputs/decisions/D7.md: MS4525DO probes 0x28/0x36/0x46; MS5525 0x76/0x77 (CSB strap, "
                 "Holybro default 0x76); MS4525 14-bit, 1 psi, ~1.05 Pa per count; RMRC sensor $59.99 US stock",
           status="UNVERIFIED")
kit.source("SRC-F3-RMRC-ASPD", "ReadyMadeRC digital airspeed sensor (MS4525DO) with pitot", "web",
           url="https://www.readymaderc.com/products/details/rmrc-digital-air-speed-sensor-pixhawk-ii-2",
           where="$59.99, in stock 2026-11-01 (D7); chip 'MS4525DO equivalent', address not listed", status="UNVERIFIED")
kit.source("SRC-F3-HGLRC-M100", "HGLRC M100-5883 GPS + compass", "web",
           url="https://www.racedayquads.com/products/hglrc-m100-5883-gps-module-10th-gen",
           where="u-blox M10, QMC5883-class compass, $20.49 (I1 BOM A02); mass not read", status="UNVERIFIED")
kit.source("SRC-F3-AP-QMC5883", "ArduPilot QMC5883L / QMC5883P compass drivers", "web",
           url="https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Compass",
           where="QMC5883L at 0x0D, QMC5883P at 0x2C (from memory of the driver headers, not re-read)",
           status="UNVERIFIED")
kit.source("SRC-F3-NOAA-WMM", "NOAA magnetic field calculator (WMM) for Richmond Field Station", "web",
           url="https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml",
           where="37.91 N, 122.34 W: total ~48 uT, horizontal ~23.5 uT (recalled, not re-run)", status="UNVERIFIED")

# ---------------------------------------------------------------- assumptions
kit.assumption("ASM-F3-LAYOUT", "Avionics and power positions in the pod (D2 layout)",
               "positions [x, y, z] m: GPS/compass on the mast; FC IMU; pack centroid; pod power group (AS150U, "
               "power board, PDB, UBEC on the left floor); ESC lead grooves on the upper skin behind the pod",
               basis="team/D2 pod SPEC and CR-D2-06 (GPS antenna centre, FC centre, left-floor items x 0.030-0.060), "
                     "CL-D2-PACK-X-FWD / -Z; grooves per F1 CR-F1-07; refreshed when D2 or F2 move them",
               value={"gps": [0.080, 0.0, 0.169], "fc_imu": [-0.010, 0.046, 0.035], "pack": [-0.0302, 0.0, 0.046],
                      "pod_power": [0.045, -0.046, 0.025], "esc_groove_line_xz": [0.100, 0.016]},
               unit="m", status="PROPOSED", cites=["SRC-K09-CARD"])
kit.assumption("ASM-F3-EARTH-FIELD", "Earth field at the field site", "total 48 uT, horizontal 23.5 uT",
               basis="WMM order of magnitude for the San Francisco Bay; re-run the NOAA calculator before compassmot",
               value=[48.0, 23.5], unit="uT", status="UNVERIFIED", cites=["SRC-F3-NOAA-WMM"])
kit.assumption("ASM-F3-LOOP-AREAS", "Current-loop areas seen by the compass",
               "pack internal loop 1 000 mm2; pod main-path loop where + and - part (plug, power board, PDB) 600 mm2; "
               "ESC lead pair spacing 5 mm (two grooves, not twisted)",
               basis="4S1P pack 160 x 50 mm with cells in series gives a net loop of order cell pitch x length; the "
                     "pod path is twisted except over ~30 x 20 mm at the terminals; groove spacing from CR-F1-07. "
                     "Upper estimates; compassmot measures the real value",
               value=[1.0e-3, 6.0e-4, 0.005], unit="m2,m2,m", status="UNVERIFIED")
kit.assumption("ASM-F3-ISOLATOR", "FC isolation mount", "natural frequency 35 Hz, damping ratio 0.10, board mass 0.042 kg",
               basis="silicone gel pads (Kyosho Zeal class) under a ~40 g board; 35 Hz sits above the attitude "
                     "control bandwidth (< 10 Hz, rule fn >= 20 Hz) and well below hover 1P (~90 Hz). zeta 0.10 is "
                     "the low end for gel (less damping = better isolation, larger resonance)",
               value=[35.0, 0.10, 0.042], unit="Hz,-,kg", status="UNVERIFIED")
kit.assumption("ASM-F3-ASPD-ERR", "Airspeed error terms after calibration",
               "MS4525DO resolution 1.05 Pa per count; zero drift in flight 3 Pa (after the pre-flight zero); "
               "ARSPD_RATIO residual after ARSPD_AUTOCAL and reciprocal GPS legs 2 %",
               basis="1 psi 14-bit 10-90 % transfer (D7); drift and ratio residual are typical small-UAS values, "
                     "to be replaced by the box-pattern result",
               value=[1.05, 3.0, 0.02], unit="Pa,Pa,-", status="UNVERIFIED", cites=["SRC-F3-D7"])
kit.assumption("ASM-F3-5V-LOADS", "5 V rail loads",
               "FC (MCU, 2 IMUs, baro, OSD) 0.20 A; wireless module 0.05 A; GPS + compass 0.05 A; ELRS receiver with "
               "telemetry 0.08 A; MS4525DO 0.003 A; LEDs and buzzer 0.05 A",
               basis="typical datasheet-class currents for these parts; bench-measured in T-F3-5V",
               value=[0.20, 0.05, 0.05, 0.08, 0.003, 0.05], unit="A", status="UNVERIFIED")
kit.assumption("ASM-F3-BEC", "FC BEC ratings carried", "FC 5 V BEC 2.4 A continuous; servo BEC 4.5 A continuous",
               basis="lower of the maker manual and the ArduPilot page / listings (4 A, 8 A); the lower values are "
                     "carried until the manual PDF is opened",
               value=[2.4, 4.5], unit="A", status="UNVERIFIED", cites=["SRC-F3-COREWING-MANUAL", "SRC-F3-AP-COREWING"])
kit.assumption("ASM-F3-MASS", "Avionics part masses",
               "[part, g]: AVN-001 CoreWing F405 Wing APP V2 incl. power board 40 + pigtails 2; AVN-002 GPS 10; "
               "AVN-003 RX + antennas 3; AVN-004 MS4525DO board 5; AVN-005 pitot tube, sleeve boom, 0.4 m tubing, "
               "2 couplers 13; AVN-006 gel pads, tape, ties 5; AVN-007 microSD 0.5",
               basis="FC from the ArduPilot page (40 g); the rest EST from listings and A3's model; weigh on arrival",
               value=[["AVN-001", 42.0], ["AVN-002", 10.0], ["AVN-003", 3.0], ["AVN-004", 5.0], ["AVN-005", 13.0],
                      ["AVN-006", 5.0], ["AVN-007", 0.5]], unit="g", status="UNVERIFIED",
               cites=["SRC-F3-AP-COREWING"])
kit.assumption("ASM-F3-I2C-MAP", "Devices on the single I2C bus (I2C1)",
               "board baro SPL06 0x76; GPS compass QMC5883L 0x0D (or QMC5883P 0x2C); airspeed MS4525DO 0x28 (driver "
               "also probes 0x36, 0x46). Rejected: MS5525 at 0x76 (default) / 0x77",
               basis="hwdef baro line; driver addresses",
               value={"baro": [0x76], "compass": [0x0D, 0x2C], "airspeed_ms4525": [0x28, 0x36, 0x46],
                      "airspeed_ms5525": [0x76, 0x77]}, unit="-", status="PROPOSED",
               cites=["SRC-F3-HWDEF-COREWING", "SRC-F3-D7", "SRC-F3-AP-QMC5883"])
kit.assumption("ASM-F3-FC-SIZE", "FC envelope on its mount", "52 x 32 x 17 mm board stack, no header pins, 6 mm gel/boss",
               basis="ArduPilot page dimensions; signal leads soldered as 100 mm pigtails with in-line JR connectors",
               value=[0.052, 0.032, 0.017, 0.006], unit="m", status="PROPOSED", cites=["SRC-F3-AP-COREWING"])
kit.assumption("ASM-F3-GPS-TILT", "GPS antenna tilt", "patch normal tilted 45 deg from +z toward -x (the nose)",
               basis="a tailsitter arms, takes off and lands nose-up; a level patch faces the horizon then",
               value=45.0, unit="deg", status="PROPOSED")


def dist(a, b):
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(a, b)))


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-F3-MAG", title="Compass interference from pack and power currents",
          equation="B = sum mu0 I A/(2 pi r^3) (loops) + mu0 (I/4) d/(2 pi r^2) x 4 (ESC pairs); ratio = B / F_earth",
          inputs={"lay": "ASM-F3-LAYOUT", "areas": "ASM-F3-LOOP-AREAS", "earth": "ASM-F3-EARTH-FIELD",
                  "i_hover": "CL-F1-I-CONT", "i_lim": "P:performance.full_throttle_current_a"},
          units={"i_hover": "A", "i_lim": "A"})
def mag(lay, areas, earth, i_hover, i_lim):
    gps = lay["gps"]
    r_pack = dist(gps, lay["pack"])
    r_pod = dist(gps, lay["pod_power"])
    gx, gz = lay["esc_groove_line_xz"]
    r_esc = math.hypot(gps[0] - gx, gps[2] - gz)

    def b_ut(i):
        b_pack = MU0_2PI * i * areas[0] / r_pack ** 3
        b_pod = MU0_2PI * i * areas[1] / r_pod ** 3
        b_esc = 4 * MU0_2PI * (i / 4) * areas[2] / r_esc ** 2
        return (b_pack + b_pod + b_esc) * 1e6

    b_h, b_l = b_ut(i_hover), b_ut(i_lim)
    return {"b_hover_ut": b_h, "ratio_hover": b_h / earth[0], "ratio_limit": b_l / earth[0],
            "heading_err_hover_deg": math.degrees(math.atan2(b_h, earth[1])),
            "r_min_power_m": min(r_pod, r_esc), "r_pack_m": r_pack}


@kit.calc("CALC-F3-I2C", title="I2C address clashes on the single bus",
          equation="count of addresses shared between the board baro and each external device set",
          inputs={"m": "ASM-F3-I2C-MAP"})
def i2c(m):
    used = set(m["baro"])
    chosen = [set(m["compass"]), set(m["airspeed_ms4525"])]
    clash = 0
    for s in chosen:
        clash += len(used & s)
        used |= s
    n_dev = 1 + len(chosen)
    return {"clashes": clash, "clean_devices": n_dev - clash, "n_devices": n_dev,
            "clashes_ms5525": len(set(m["baro"]) & set(m["airspeed_ms5525"]))}


@kit.calc("CALC-F3-VIBE", title="FC isolation: transmissibility at hover 1P and 2P",
          equation="T(r) = sqrt((1+(2 z r)^2)/((1-r^2)^2+(2 z r)^2)), r = f/fn, f1P = rpm/60, 2P = 2 f1P",
          inputs={"rpm": "CL-B4-HOVER-RPM", "iso": "ASM-F3-ISOLATOR"}, units={"rpm": "rpm"})
def vibe(rpm, iso):
    fn, z, m = iso

    def t(f):
        r = f / fn
        return math.sqrt((1 + (2 * z * r) ** 2) / ((1 - r * r) ** 2 + (2 * z * r) ** 2))

    f1 = rpm / 60.0
    k = m * (2 * math.pi * fn) ** 2
    return {"f1p_hz": f1, "t_1p": t(f1), "t_2p": t(2 * f1), "r_1p": f1 / fn, "fn_hz": fn,
            "k_total_n_per_m": k, "static_sag_mm": 9.80665 / (2 * math.pi * fn) ** 2 * 1000}


@kit.calc("CALC-F3-ASPD", title="Airspeed error budget at cruise",
          equation="q = rho v^2/2; dv = dq/(rho v); RSS(wash, ratio residual, drift, half count)",
          inputs={"v": "P:performance.cruise_ms", "rho": "P:env.rho_kgm3", "wash": "CL-B4-PITOT",
                  "e": "ASM-F3-ASPD-ERR"}, units={"v": "m/s", "rho": "kg/m3"})
def aspd(v, rho, wash, e):
    count, drift, ratio = e
    dvdq = 1 / (rho * v)
    terms = [wash * v, ratio * v, drift * dvdq, 0.5 * count * dvdq]
    return {"q_pa": 0.5 * rho * v * v, "dv_per_count_ms": count * dvdq,
            "err_rss_ms": math.sqrt(sum(t * t for t in terms)), "err_linear_ms": sum(terms)}


@kit.calc("CALC-F3-5V", title="FC 5 V rail load and board dissipation",
          equation="I5 = sum loads; required = 2 I5 (R-AVIONICS-POWER); P_board = 5 V x (FC + wireless) + "
                   "5 V x I5 (1/eta - 1) + 0.1 W servo-BEC idle, eta 0.85",
          inputs={"loads": "ASM-F3-5V-LOADS", "bec": "ASM-F3-BEC"})
def five_v(loads, bec):
    i5 = sum(loads)
    p_board = 5.0 * (loads[0] + loads[1]) + 5.0 * i5 * (1 / 0.85 - 1) + 0.1
    return {"i5_a": i5, "required_a": 2 * i5, "bec_a": bec[0], "p_board_w": p_board}


@kit.calc("CALC-F3-MASS", title="Avionics mass roll-up", equation="sum of part masses",
          inputs={"m": "ASM-F3-MASS"})
def mass(m):
    return sum(g for _, g in m)


@kit.calc("CALC-F3-FIT", title="FC envelope vs the pod right channel", equation="height = board + mount; width, length",
          inputs={"s": "ASM-F3-FC-SIZE"})
def fit(s):
    return {"h_mm": (s[2] + s[3]) * 1000, "w_mm": s[1] * 1000, "l_mm": s[0] * 1000}


@kit.calc("CALC-F3-GPS-SKY", title="GPS patch off-boresight angle to zenith, worst of hover and cruise",
          equation="max(|90 - tilt| (hover, nose up), tilt (cruise))", inputs={"tilt": "ASM-F3-GPS-TILT"},
          units={"tilt": "deg"})
def gps_sky(tilt):
    return {"worst_deg": max(abs(90 - tilt), tilt), "level_patch_hover_deg": 90.0}


@kit.calc("CALC-F3-OFFSETS", title="Sensor position offsets for ArduPilot (FRD body axes, from the CG)",
          equation="X_fwd = -(x - x_cg); Y_right = y; Z_down = -(z - z_cg)",
          inputs={"lay": "ASM-F3-LAYOUT", "xcg": "P:cg.x_target_m", "zcg": "P:cg.z_target_m"},
          units={"xcg": "m", "zcg": "m"})
def offsets(lay, xcg, zcg):
    def frd(p):
        return [round(-(p[0] - xcg), 3), round(p[1], 3), round(-(p[2] - zcg), 3)]
    imu, g = frd(lay["fc_imu"]), frd(lay["gps"])
    return {"ins_pos_m": imu, "gps_pos_m": g, "imu_r_m": math.sqrt(sum(c * c for c in imu))}


# ---------------------------------------------------------------- claims
FC = ["AVN-001"]
kit.claim("CL-F3-FC-STABLE", "Stable ArduPilot Plane build with QuadPlane (tailsitter) for the chosen FC",
          value="ArduPilot Plane 4.7.2 OFFICIAL, target CoreWingF405WingV2, HAL_QUADPLANE_ENABLED, logging on",
          verifies=["R-FC-STABLE"], parts=FC, cites=["SRC-F3-FW-COREWING", "SRC-F3-AP-TAILSITTER"],
          how="T-F3-FW-LOAD: flash the stable .apj, set Q_ENABLE 1 + reboot, Q_TAILSIT_ENABLE appears; a log file is "
              "written to the microSD.")
kit.claim("CL-F3-BDSHOT-OUTS", "Outputs 1-4 bi-directional DShot, no servo in their timer groups",
          value="PWM1-2 TIM4, PWM3-4 TIM3 (BIDIR); elevons on PWM5-6 (TIM8 group 5-7, PWM 50 Hz)", parts=FC,
          cites=["SRC-F3-AP-COREWING", "SRC-F3-HWDEF-COREWING"],
          how="T-F3-FW-LOAD: ESC rpm telemetry on all four motors in the ESC status page with SERVO_BLH_BDMASK 15.")
kit.claim("CL-F3-I2C-CLASH", "I2C devices on the bus with a unique address (of 3: baro, compass, airspeed)",
          calc="CALC-F3-I2C", output="clean_devices", limit=(">=", 3), parts=["AVN-001", "AVN-002", "AVN-004"],
          how="T-F3-I2C-SCAN: baro, compass and airspeed all detected at boot (messages tab) and all three read.")
kit.claim("CL-F3-I2C-CLASH-MS5525", "I2C clashes if the MS5525 (0x76 default) were fitted", calc="CALC-F3-I2C",
          output="clashes_ms5525", note="1 clash with the SPL06 baro at 0x76: why the MS5525 is replaced",
          how="Read the hwdef BARO line and the MS5525 strap.")
kit.claim("CL-F3-COMPASS-RATIO", "Compass interference at hover current / Earth field", calc="CALC-F3-MAG",
          output="ratio_hover", limit=("<=", "P:requirements.compass_interference_max"), verifies=["R-COMPASS"],
          parts=["AVN-002"], how="T-F3-COMPASSMOT: COMPASS_MOT calibration to hover current; interference <= 30 %.")
kit.claim("CL-F3-COMPASS-RATIO-LIM", "Compass interference at the 100 A limiter / Earth field", calc="CALC-F3-MAG",
          output="ratio_limit", limit=("<=", "P:requirements.compass_interference_max"), parts=["AVN-002"],
          how="As CL-F3-COMPASS-RATIO, extrapolated from the compassmot slope.")
kit.claim("CL-F3-COMPASS-B", "Field from pack and power currents at the compass, hover", calc="CALC-F3-MAG",
          output="b_hover_ut", unit="uT", parts=["AVN-002"], how="Compassmot log (MAG field vs current).")
kit.claim("CL-F3-COMPASS-HDG", "Uncorrected heading error at hover current", calc="CALC-F3-MAG",
          output="heading_err_hover_deg", unit="deg", parts=["AVN-002"],
          how="Hover log heading vs GPS course at take-off; compassmot removes most of it.")
kit.claim("CL-F3-GPS-CLEAR", "GPS/compass distance to the nearest power item", calc="CALC-F3-MAG",
          output="r_min_power_m", unit="m", limit=(">=", "P:requirements.gps_mast_clearance_m"),
          verifies=["R-COMPASS"], parts=["AVN-002", "POD-005"],
          how="Tape measure on the built pod: mast top to power board, PDB, UBEC, ESC leads.")
kit.claim("CL-F3-GPS-SKY", "GPS patch off-boresight to zenith, worst attitude", calc="CALC-F3-GPS-SKY",
          output="worst_deg", unit="deg", limit=("<=", 50.0), parts=["AVN-002", "POD-005"],
          note="a level patch is 90 deg off in hover (faces the horizon while the aircraft stands for arming)",
          how="T-F3-HDOP: standing on the fin tips, HDOP <= 1.2 within 3 min of power-up.")
kit.claim("CL-F3-VIBE-T1P", "FC mount transmissibility at hover 1P", calc="CALC-F3-VIBE", output="t_1p",
          limit=("<=", 0.3), verifies=["R-VIBRATION"], parts=["AVN-001", "AVN-006"],
          how="T-F3-VIBE: tethered hover, VIBE X/Y/Z < 30 m/s2, clip 0; batch-sampler FFT shows the 1P peak.")
kit.claim("CL-F3-VIBE-FN", "FC mount natural frequency", calc="CALC-F3-VIBE", output="fn_hz", unit="Hz",
          limit=(">=", 20.0), parts=["AVN-006"],
          how="Tap test on the mounted board with the IMU batch log; peak 25-45 Hz accepted.")
kit.claim("CL-F3-ASPD-ERR", "Airspeed error at cruise, RSS budget", calc="CALC-F3-ASPD", output="err_rss_ms",
          unit="m/s", limit=("<=", "P:requirements.airspeed_err_max_ms"), verifies=["R-AIRSPEED"],
          parts=["AVN-004", "AVN-005"],
          note="also meets B1's proposed 0.5 m/s (CR-B1-13) by 11 %; the linear sum (CL-F3-ASPD-ERR-LIN) does not",
          how="T-F3-ARSPD-CAL: ARSPD_AUTOCAL then calm-air box pattern; airspeed vs GPS ground speed both ways.")
kit.claim("CL-F3-ASPD-ERR-LIN", "Airspeed error at cruise, linear sum", calc="CALC-F3-ASPD", output="err_linear_ms",
          unit="m/s", parts=["AVN-004"], how="As CL-F3-ASPD-ERR.")
kit.claim("CL-F3-ASPD-RES", "Airspeed resolution at cruise, one count", calc="CALC-F3-ASPD",
          output="dv_per_count_ms", unit="m/s", limit=("<=", 0.1), parts=["AVN-004"],
          how="Bench log ARSP at a steady blow; steps of one count.")
kit.claim("CL-F3-5V-REQ", "Required FC 5 V BEC rating (2 x avionics load)", calc="CALC-F3-5V", output="required_a",
          unit="A", limit=("<=", 2.4), verifies=["R-AVIONICS-POWER"], parts=["AVN-001"],
          note="limit = FC BEC 2.4 A (lowest published value, ASM-F3-BEC)",
          how="T-F3-5V: bench supply 16.8 V, all avionics on, ELRS telemetry on; measure the 5 V rail current.")
kit.claim("CL-F3-FC-DISS", "FC board dissipation", calc="CALC-F3-5V", output="p_board_w", unit="W",
          limit=("<=", 2.0), parts=["AVN-001"], note="limit = E3's assumption ASM-E3-FC 2.0 W",
          how="T-F3-5V: input power at 16.8 V minus the power delivered to the 5 V peripherals.")
kit.claim("CL-F3-SENSE-CONT", "CoreWing power-board current sensing, continuous", value=90.0, unit="A",
          limit=(">=", "CL-F1-DISC-REQ-CONT"), verifies=["R-AVIONICS-POWER"], parts=["PWR-003"],
          cites=["SRC-F3-AP-COREWING"], how="T-F1-SENSOR-CAL: clamp meter at 25-30 A, within 5 %.")
kit.claim("CL-F3-SENSE-PEAK", "CoreWing power-board current sensing, peak", value=215.0, unit="A",
          limit=(">=", "P:electrical.peak_current_a"), parts=["PWR-003"], cites=["SRC-F3-AP-COREWING"],
          how="Data sheet; the 100 A limiter keeps flight peaks below it.")
kit.claim("CL-F3-SERVO-BEC", "FC servo BEC continuous rating carried", value=4.5, unit="A",
          limit=(">=", "CL-F1-SERVO-BEC-REQ"), parts=["AVN-001"], cites=["SRC-F3-COREWING-MANUAL"],
          note="FAILS on the manual value: F1's UBEC stays fitted. Listings give 8 A (would pass)",
          how="T-F1-SERVO-STALL on the CoreWing Vx rail; F1's UBEC drop rule.")
kit.claim("CL-F3-MASS", "Avionics mass", calc="CALC-F3-MASS", output="value", unit="g",
          limit=("<=", "P:mass.allocation_g.avionics"),
          parts=["AVN-001", "AVN-002", "AVN-003", "AVN-004", "AVN-005", "AVN-006", "AVN-007"],
          note="includes the CoreWing power board (PWR-003 position, 0 g in power); CR-F3-01 asks +5 g",
          how="Weigh each part on arrival; A3 replaces the EST rows.")
kit.claim("CL-F3-FC-H", "FC height on its mount", calc="CALC-F3-FIT", output="h_mm", unit="mm",
          limit=("<=", 28.0), parts=["AVN-001", "POD-002"], note="limit from D2 CR-D2-06 (connectors up <= 28 mm)",
          how="Caliper on the mounted board, hatch closes.")
kit.claim("CL-F3-FC-W", "FC width across the right channel", calc="CALC-F3-FIT", output="w_mm", unit="mm",
          limit=("<=", 36.0), parts=["AVN-001", "POD-002"], how="Dry fit in the printed tray.")
kit.claim("CL-F3-FC-L", "FC length along the right channel", calc="CALC-F3-FIT", output="l_mm", unit="mm",
          limit=("<=", 56.0), parts=["AVN-001", "POD-002"], how="Dry fit in the printed tray.")
kit.claim("CL-F3-INS-POS", "IMU offset from the CG (INS_POS1/2_X,Y,Z, FRD)", calc="CALC-F3-OFFSETS",
          output="ins_pos_m", unit="m", parts=["AVN-001"], how="Measure the as-built FC centre from the CG mark.")
kit.claim("CL-F3-GPS-POS", "GPS antenna offset from the CG (GPS1_POS_X,Y,Z, FRD)", calc="CALC-F3-OFFSETS",
          output="gps_pos_m", unit="m", parts=["AVN-002"], how="Measure the as-built mast top from the CG mark.")

# ---------------------------------------------------------------- tests
kit.test("T-F3-FW-LOAD", "Load stable Plane, tailsitter parameters present, bdshot telemetry, SD log",
         verifies=["CL-F3-FC-STABLE", "CL-F3-BDSHOT-OUTS"],
         procedure="DFU-flash arduplane_with_bl.hex (stable 4.7.x); Q_ENABLE 1, reboot; Q_TAILSIT_ENABLE 1; "
                   "SERVO_BLH_BDMASK 15 with Bluejay ESCs; spin each motor in motor test (props off); check log on SD")
kit.test("T-F3-I2C-SCAN", "All I2C devices detected and reading", verifies=["CL-F3-I2C-CLASH"],
         procedure="boot with GPS and airspeed connected: messages list SPL06, QMC5883, MS4525; blow on the pitot, "
                   "airspeed rises and baro altitude does not jump")
kit.test("T-F3-COMPASSMOT", "Compass interference at hover current", verifies=["CL-F3-COMPASS-RATIO"],
         procedure="props on, aircraft tied down standing, COMPASS_MOT calibration ramped to hover throttle; record "
                   "interference %")
kit.test("T-F3-HDOP", "GPS fix standing on the fin tips", verifies=["CL-F3-GPS-SKY"],
         procedure="cold start at RFS, aircraft standing; time to 3D fix and HDOP at 3 min; pass HDOP <= 1.2")
kit.test("T-F3-VIBE", "FC vibration in tethered hover", verifies=["CL-F3-VIBE-T1P", "CL-F3-VIBE-FN"],
         procedure="INS_LOG_BAT_MASK 1; 60 s tethered QHOVER; VIBE < 30 m/s2 each axis, clip 0; FFT 1P and 2P "
                   "peaks; repeat with the board hard-mounted once to measure isolation")
kit.test("T-F3-ARSPD-CAL", "Airspeed calibration and accuracy", verifies=["CL-F3-ASPD-ERR"],
         procedure="pre-flight zero; ARSPD_AUTOCAL 1 in a FBWA box; reciprocal straight legs at 16 m/s in < 2 m/s "
                   "wind; airspeed vs GPS-derived TAS within the requirement")
kit.test("T-F3-5V", "5 V rail current and board dissipation", verifies=["CL-F3-5V-REQ", "CL-F3-FC-DISS"],
         procedure="bench supply 16.8 V through a meter; all avionics on with telemetry; meter on the 5 V rail")

if __name__ == "__main__":
    kit.write()
