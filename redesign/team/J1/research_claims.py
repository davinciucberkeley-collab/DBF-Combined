"""J1 outside research: the numbers from published data that other roles depend on, as proof-chain claims.

Run:  python -I redesign/team/J1/research_claims.py      (writes claims.json beside this file)
Then: python -I redesign/proofs/build_graph.py

Everything here is a first-order screen from public sources (REFERENCES.md); the owning role re-derives it.
Five results matter: (1) the fin side-area centroid is only 0.04 m aft of the CG, (2) the props sit 0.21 m ahead
of the CG, (3) the bare motor tube's first bending mode lands within 6 % of the hover 2P forcing, (4) the MH 45
section with elevons neutral trims only ~2.7 % static margin at the cruise CL, and (5) an XT60 fails the 120 A
momentary case. Standard library only.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"
SEEN = "2026-11-09"

# ----------------------------------------------------------------- sources (all read 2026-11-09)
kit.source("SRC-J1-AP-TUNING", "ArduPilot: Tailsitter VTOL tuning guide", "web",
           url="https://ardupilot.org/plane/docs/tailsitter-tuning-guide.html", checked=SEEN,
           where="notch first; pitch/yaw FF from log (start X=0.2), I = FF; D then P by oscillate-and-halve; roll like a quad")
kit.source("SRC-J1-AP-VIBE", "ArduPilot: Measuring vibration", "web",
           url="https://ardupilot.org/plane/docs/common-measuring-vibration.html", checked=SEEN,
           where="VIBE < 30 m/s2 acceptable, > 60 m/s2 nearly always problems; Clip0-2 ideally 0, < 100 likely ok")
kit.source("SRC-J1-AP-DAMPING", "ArduPilot: Vibration damping", "web",
           url="https://ardupilot.org/plane/docs/common-vibration-damping.html", checked=SEEN,
           where="gel pads or foam squares; off-the-shelf mounts are for 5-10x heavier boards; 'too much is as bad as too little'")
kit.source("SRC-J1-AP-NOTCH", "ArduPilot: Dynamic harmonic notch", "web",
           url="https://ardupilot.org/plane/docs/common-imu-notch-filtering.html", checked=SEEN,
           where="ESC RPM telemetry (INS_HNTCH_MODE 3) best, throttle-based (MODE 1) second; three harmonics usually safe")
kit.source("SRC-J1-AP-WVANE", "ArduPilot: QuadPlane weathervaning", "web",
           url="https://ardupilot.org/plane/docs/quadplane-weathervaning.html", checked=SEEN,
           where="Q_WVANE_ENABLE 1 nose into wind; GAIN start 1; active in QLOITER/QLAND/QRTL only, not QHOVER/QSTABILIZE")
kit.source("SRC-J1-AP-AIRSPEED", "ArduPilot: Airspeed sensor", "web",
           url="https://ardupilot.org/plane/docs/airspeed.html", checked=SEEN,
           where="pitot out of the prop flow (about a foot from a nose prop); cover at power-up; ARSPD_AUTOCAL needs turns")
kit.source("SRC-J1-AP-MAG", "ArduPilot: Magnetic interference", "web",
           url="https://ardupilot.org/plane/docs/common-magnetic-interference.html", checked=SEEN,
           where="compass on a mast away from the PDB; twist pack-PDB-ESC wires; field rises with loop area and current")
kit.source("SRC-J1-AP-YAW", "ArduPilot: Yaw and yaw control in Plane", "web",
           url="https://ardupilot.org/plane/docs/yaw-in-plane.html", checked=SEEN,
           where="no yaw rate stabilisation in FW modes except ACRO; yaw damper for fin-less wings via split surfaces; RUDD_DT_GAIN for twin throttles")
kit.source("SRC-J1-BOXKITE", "H. Wurzburg: Box Kite copter-tailsitter build instructions", "web",
           url="https://discuss.ardupilot.org/t/box-kite-copter-tailsitter-build-instructions", checked=SEEN,
           where="CG ~15 % chord; 1.5 in elevons at 45 deg; tape LE and contact points; Q_TRIM_PITCH -2; fly on a zero-wind day")
kit.source("SRC-J1-BOXKITE-LEARN", "dpapworth: BoxKite VTOL learning (4 student aircraft, logs)", "web",
           url="https://discuss.ardupilot.org/t/boxkite-vtol-learning/139972", checked=SEEN,
           where="failed first transition; later all four yawed uncommanded in FBWA: Plane does not stabilise yaw in FW by default")
kit.source("SRC-J1-EVIDENCE", "Tie-break tailsitter evidence file (forum survey, 16 builds)", "web",
           where="redesign/config-study/tiebreak/tailsitter-evidence/EVIDENCE.md sections 1.2-1.3", checked=SEEN)
kit.source("SRC-J1-MH45-HEPPERLE", "M. Hepperle: MH 45 airfoil page", "web",
           url="https://www.mh-aerotools.de/airfoils/mh45koo.htm", checked=SEEN,
           where="thickness 9.85 %, cm c/4 = +0.0145, Re >= 100 000, F3B tailless use")
kit.source("SRC-J1-HEPPERLE-PLANK", "M. Hepperle: Basic design of flying wing models (plank)", "web",
           url="https://www.mh-aerotools.de/airfoils/flywing1.htm", checked=SEEN,
           where="unswept wing: NP at c/4; stability coefficient typically 0.02-0.05; trim needs Cm = CL x sigma")
kit.source("SRC-J1-APC-PER3", "APC 11x4.5MR performance file PER3_11x45MR.dat", "datasheet",
           url="https://www.apcprop.com/files/PER3_11x45MR.dat", checked=SEEN,
           where="static: 5.02 N / 41 W at 5000 rpm, 7.25 N / 70 W at 6000, 9.91 N / 110 W at 7000; zero thrust at J ~0.545; "
                 "at 6000 rpm and 14.7 m/s: 0.32 N, eta 0.17; at 7000 rpm and 14.4 m/s: 2.38 N, eta 0.54, 64 W")
kit.source("SRC-J1-HOLYBRO-CONN", "Holybro: connector and wire rating table", "web",
           url="https://docs.holybro.com/power-module-and-pdb/power-module/connector-and-wire-rating", checked=SEEN,
           where="XT60 30 A continuous (4 h, < 60 degC rise) / 60 A 1 min; XT90 45/90; AS150 75/150; 12 AWG with XT60")
kit.source("SRC-J1-AMASS-XT60", "Amass XT60-F specification 2025 V0", "datasheet",
           url="https://www.china-amass.net/uploads/57.XT60-F-SPEC-2025V0.pdf", checked=SEEN,
           where="rated 35 A at 12 AWG, temperature rise <= 85 K; contact resistance <= 1.0 mOhm")
kit.source("SRC-J1-AS150U", "Amass AS150U rating (reseller listings; maker sheet not found)", "web",
           url="https://robu.in/product/amass-as150u-male-connector/",
           where="70 A rated (some list 75 A), 140 A instantaneous, 500 V DC; anti-spark pre-charge contact",
           note="no maker datasheet opened; one forum report of the anti-spark contact melting (discuss.ardupilot.org/t/75032)")
kit.source("SRC-J1-EC-TUBES", "Easy Composites: carbon fibre tubes explained (3-point bend comparison)", "web",
           url="https://www.easycomposites.co.uk/learning/carbon-fibre-tubes-explained", checked=SEEN,
           where="roll-wrapped ~200 kg vs pultruded ~140 kg in their bend test; roll-wrapped trades a little stiffness for hoop strength")
kit.source("SRC-J1-EPSILON", "Epsilon Composite: standard pultruded profiles catalogue 2022", "datasheet",
           url="https://www.epsilon-composite.com/wp-content/uploads/2022/01/ENG-2022-Standard-profiles-catalogue.pdf", checked=SEEN,
           where="HS-fibre pultrusion tensile modulus 100-140 GPa, strength 2000-3000 MPa (unidirectional)")
kit.source("SRC-J1-ALOFT-TUBE", "Aloft Hobbies: 22 x 20 x 1000 mm mandrel-wound carbon tube", "web",
           url="https://alofthobbies.com/products/22-x-20-x-1000mm-mw-carbon-tubing-matte-finish", checked=SEEN,
           where="$24.00, listed in stock (US hobby vendor); layup and modulus not stated")
kit.source("SRC-J1-FOAMULAR", "Owens Corning FOAMULAR NGX 250 product data sheet", "datasheet",
           url="https://www.owenscorning.com/dms/43522",
           where="compressive strength min 25 psi (172 kPa) ASTM D1621; ASTM C578 Type IV; flexural 50-75 psi in older sheets",
           note="PDF opened but not text-extracted here; values from the search snippets of the 2025 sheet and older revisions")
kit.source("SRC-J1-LYU2018", "Lyu et al. 2018, quadrotor tail-sitter: modelling, wind-tunnel ID and unified control", "paper",
           url="https://doi.org/10.1177/1756829318813633", checked=SEEN,
           where="IJMAV; full-attitude wind tunnel tests; transition with negligible altitude loss; custom controller, not stock ArduPilot")
kit.source("SRC-J1-LYU-DOB", "Lyu et al. 2018, disturbance-observer hover control of a quadrotor tail-sitter", "paper",
           url="https://doi.org/10.1109/LRA.2018.2847405", checked=SEEN,
           where="large wing area in hover makes the tail-sitter sensitive to crosswind; DOB improves hover accuracy")
kit.source("SRC-J1-DARKO", "Sansou et al. 2024, hover stabilisation of the DarkO tail-sitter with constant wind", "paper",
           url="https://hal.univ-lyon2.fr/LAAS-MAC/hal-04715046v1", checked=SEEN,
           where="two attitude DOF used to hold hover against unknown constant wind; flight-validated on Paparazzi")
kit.source("SRC-J1-WINGTRA", "WingtraOne GEN II technical specifications (duo tailsitter, elevons)", "datasheet",
           url="https://www.duncan-parnell.com/media/sparsh/product_attachment/WingtraOne_Gen_II_Tech_Specs___Wingtra.pdf", checked=SEEN,
           where="span 125 cm, empty 3.7 kg, MTOW 4.5 kg (4.8 on another sheet), lands on its tail, RTH if cruise wind > 12 m/s for 30 s")
kit.source("SRC-J1-SWAN-K1", "HEQ Swan K1 / K1 PRO motor-only quad tailsitter (ArduPilot page + dealer specs)", "web",
           url="https://ardupilot.org/plane/docs/common-Swan-K1.html", checked=SEEN,
           where="control-surfaceless quad tailsitter; dealer specs: span ~1.1 m, empty 1.0-1.12 kg, MTOW 2.2 kg (one listing), arm only in QHOVER/QLOITER")
kit.source("SRC-J1-RIBNER", "Ribner 1945, NACA Report 820: Propellers in yaw", "paper",
           url="https://ntrs.nasa.gov/citations/19930091897", checked=SEEN,
           where="a yawed propeller produces a side (normal) force like a fin of its projected area; ahead of the CG this is destabilising")
kit.source("SRC-J1-FAA-REC", "FAA: Recreational flyers (page returned 403 to the fetch; rules from secondary summaries)", "web",
           url="https://www.faa.gov/uas/recreational_flyers",
           where="TRUST certificate; register if > 250 g ($5 / 3 yr, number on the aircraft); Remote ID or fly in a FRIA; 400 ft; VLOS",
           note="H3 confirms on the FAA page before the first flight; UNVERIFIED here")
kit.source("SRC-J1-HOTWIRE", "MIT k12maker hot-wire guide and hobby cutting notes", "web",
           url="https://k12maker.mit.edu/uploads/9/7/5/8/97583140/hot_wire_guide.pdf", checked=SEEN,
           where="XPS cuts cleanly; kerf no wider than the wire = right heat; constant feed ~2-3 mm/s; numbered template increments; ventilate")
kit.source("SRC-J1-FT-FOAMBOARD", "Flite Test: alternative foam-board build method (tape-skinned panels)", "web",
           url="https://flitetest.com/articles/an-alternative-foam-board-build-method", checked=SEEN,
           where="packing tape over paper-faced board, burnished with a card edge; the standard hobby method for the fins and the twin")
kit.source("SRC-J1-DESYNC", "Oscar Liang: fixing ESC desync; ModalAI note on low-KV motors", "web",
           url="https://oscarliang.com/fix-esc-desync", checked=SEEN,
           where="low-KV / high-inductance motors desync at high power: raise timing, lower ramp-up power, add a low-ESR capacitor at the ESC")
kit.source("SRC-J1-TUDELFT-GEAR", "TU Delft: origami-inspired drone landing gear drop tests", "paper",
           url="https://repository.tudelft.nl/file/File_1d3c3ae8-bbc3-49da-a470-07c94c81e44f", checked=SEEN,
           where="compliant gear cut peak impact force up to 75 % vs rigid; design by sink speed, load factor, stroke, energy, weight")

# ----------------------------------------------------------------- assumptions
kit.assumption("ASM-J1-E-TUBE", "Axial modulus of the 22 x 20 mm tube",
               "The bought carbon tube has an axial Young's modulus of 100 GPa",
               basis="UD pultrusion 100-140 GPa (Epsilon); generic woven roll-wrapped hobby tubes are often 50-70 GPa. "
                     "UNVERIFIED until I1's tube is bend-tested (T-J1-TUBE-BEND)",
               value=100e9, unit="Pa", status="UNVERIFIED", cites=["SRC-J1-EPSILON", "SRC-J1-EC-TUBES"])
kit.assumption("ASM-J1-MOUNT-MASS", "Printed motor mount mass", "One printed PETG motor mount plus fasteners is 0.018 kg",
               basis="params.json fins allocation note: 4 motor mounts 72 g", value=0.018, unit="kg", cites=["SRC-K09-REVIEW"])
kit.assumption("ASM-J1-APC-KT", "APC 11x4.5MR static thrust per rpm^2",
               "Static thrust of the 11x4.5MR scales as T = kT n^2 with kT = 7.254 N / 6000^2 rpm^2 (APC PER3 file)",
               basis="APC PER3 static rows: 5.02 N at 5000, 7.25 N at 6000, 9.91 N at 7000 rpm (within 2 % of n^2 scaling). "
                     "APC predictions run ~10 % high on static thrust, so real rpm at a given thrust is slightly higher",
               value=7.254 / 6000.0 ** 2, unit="N/rpm2", status="PROPOSED", cites=["SRC-J1-APC-PER3"])
kit.assumption("ASM-J1-SEP-RULE", "Mode separation from forcing",
               "A structural natural frequency must sit at least 20 % away from any steady motor forcing frequency (1P, 2P)",
               basis="common rotorcraft/drone practice for untested structures; the first mode of the fin-tube assembly is then "
                     "confirmed by tap test (T-J1-TAP-TEST) and by the hover VIBE log",
               value=0.20, unit="-", status="PROPOSED")
kit.assumption("ASM-J1-MH45-CM0", "MH 45 quarter-chord moment coefficient",
               "The MH 45 section with elevons neutral has cm c/4 = +0.0145 (2-D, Hepperle)",
               basis="Hepperle's MH 45 page; B2 replaces it with the XFOIL value at Re 2-4e5 and the elevon-deflected polars",
               value=0.0145, unit="-", status="PROPOSED", cites=["SRC-J1-MH45-HEPPERLE"])
kit.assumption("ASM-J1-ETA-CRUISE", "Prop efficiency at ~1 N per prop, 15 m/s",
               "The 11x4.5MR at 15 m/s and ~1 N thrust runs at J ~0.50-0.53, close to its zero-thrust J ~0.545, with eta 0.30-0.45",
               basis="APC PER3 rows: eta 0.17 at 6000 rpm / 14.7 m/s (0.32 N) and 0.54 at 7000 rpm / 14.4 m/s (2.38 N); 1 N lies between. "
                     "The K09 REVIEW used 0.47; B4 interpolates the file properly",
               status="UNVERIFIED", cites=["SRC-J1-APC-PER3"])


# ----------------------------------------------------------------- calculations
@kit.calc("CALC-J1-FIN-YAW-ARM", title="Fin side-area centroid vs CG",
          equation="arm = (x_le + x_te)/2 - x_cg ; ahead = (x_cg - x_le)/(x_te - x_le) ; arm_c = arm / c",
          inputs={"x_le": P + "fins.le_x_m", "x_te": P + "fins.te_x_m", "x_cg": P + "cg.x_target_m", "c": P + "wing.chord_m"},
          units={"x_le": "m", "x_te": "m", "x_cg": "m", "c": "m"}, cites=["SRC-J1-HEPPERLE-PLANK"])
def fin_yaw_arm(x_le, x_te, x_cg, c):
    arm = 0.5 * (x_le + x_te) - x_cg
    return {"arm_m": arm, "arm_chord": arm / c, "fin_area_ahead_frac": (x_cg - x_le) / (x_te - x_le)}


@kit.calc("CALC-J1-PROP-ARM", title="Prop plane ahead of the CG",
          equation="arm = x_cg - x_prop ; arm_c = arm / c",
          inputs={"x_prop": P + "propulsion.stations.x_prop_plane_m", "x_cg": P + "cg.x_target_m", "c": P + "wing.chord_m"},
          units={"x_prop": "m", "x_cg": "m", "c": "m"}, cites=["SRC-J1-RIBNER"])
def prop_arm(x_prop, x_cg, c):
    return {"arm_m": x_cg - x_prop, "arm_chord": (x_cg - x_prop) / c}


@kit.calc("CALC-J1-TUBE-MODE", title="Bare motor-tube first bending mode",
          equation="I = pi/64 (od^4 - id^4) ; k = 3 E I / L^3 ; m_eff = m_motor + m_prop + m_mount + 0.24 mu L ; f1 = sqrt(k/m_eff) / 2 pi",
          inputs={"od": P + "fins.tube.od_m", "id": P + "fins.tube.id_m", "E": "ASM-J1-E-TUBE", "L": P + "fins.half_height_m",
                  "m_motor": P + "propulsion.motor_mass_kg", "m_prop": P + "propulsion.prop_mass_kg", "m_mount": "ASM-J1-MOUNT-MASS",
                  "mu": P + "wing.spar.mass_per_m_kgm"},
          units={"od": "m", "id": "m", "E": "Pa", "L": "m", "m_motor": "kg", "m_prop": "kg", "m_mount": "kg", "mu": "kg/m"},
          assumes=["ASM-J1-E-TUBE", "ASM-J1-MOUNT-MASS"])
def tube_mode(od, id, E, L, m_motor, m_prop, m_mount, mu):
    I = math.pi / 64.0 * (od ** 4 - id ** 4)
    k = 3.0 * E * I / L ** 3
    m_eff = m_motor + m_prop + m_mount + 0.24 * mu * L
    return {"I_m4": I, "EI_Nm2": E * I, "k_Npm": k, "m_eff_kg": m_eff, "f1_hz": math.sqrt(k / m_eff) / (2 * math.pi)}


@kit.calc("CALC-J1-MOTOR-FREQ", title="Motor forcing frequencies",
          equation="T_h = m g dl / n ; rpm = sqrt(T / kT) ; f1P = rpm/60 ; f2P = 2 f1P (2-blade) ; rpm_max from T_max",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "dl": P + "propulsion.download_factor",
                  "n": P + "propulsion.n_motors", "kT": "ASM-J1-APC-KT", "T_max_kg": P + "propulsion.thrust_max_per_motor_kg"},
          units={"m": "kg", "g": "m/s2", "dl": "-", "n": "-", "kT": "N/rpm2", "T_max_kg": "kg"}, assumes=["ASM-J1-APC-KT"])
def motor_freq(m, g, dl, n, kT, T_max_kg):
    T_h = m * g * dl / n
    rpm_h = math.sqrt(T_h / kT)
    rpm_max = math.sqrt(T_max_kg * g / kT)
    return {"T_hover_N": T_h, "rpm_hover": rpm_h, "f1P_hover_hz": rpm_h / 60.0, "f2P_hover_hz": rpm_h / 30.0,
            "rpm_max": rpm_max, "f1P_max_hz": rpm_max / 60.0}


@kit.calc("CALC-J1-MODE-SEP", title="Tube mode separation from motor forcing",
          equation="sep = min |f1/f - 1| over f in {1P hover, 2P hover, 1P max}",
          inputs={"f1": "CL-J1-TUBE-F1", "fa": "CL-J1-MOTOR-1P-HOVER", "fb": "CL-J1-MOTOR-2P-HOVER", "fc": "CL-J1-MOTOR-1P-MAX"},
          units={"f1": "Hz", "fa": "Hz", "fb": "Hz", "fc": "Hz"}, assumes=["ASM-J1-SEP-RULE"])
def mode_separation(f1, fa, fb, fc):
    seps = {"1P_hover": abs(f1 / fa - 1), "2P_hover": abs(f1 / fb - 1), "1P_max": abs(f1 / fc - 1)}
    worst = min(seps, key=seps.get)
    return {"sep_min": seps[worst], "nearest": worst}


@kit.calc("CALC-J1-TRIM-SM", title="Static margin trimmable with elevons neutral",
          equation="CL = m g / (0.5 rho V^2 S) ; sigma_trim = Cm0 / CL  (Hepperle: Cm = CL sigma for a plank)",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "V": P + "performance.cruise_ms", "S": "CL-A1-WING-AREA", "Cm0": "ASM-J1-MH45-CM0"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "V": "m/s", "S": "m2", "Cm0": "-"},
          assumes=["ASM-J1-MH45-CM0"], cites=["SRC-J1-HEPPERLE-PLANK"])
def trim_static_margin(m, g, rho, V, S, Cm0):
    CL = m * g / (0.5 * rho * V ** 2 * S)
    return {"CL_cruise": CL, "sigma_trim": Cm0 / CL}


@kit.calc("CALC-J1-DISCONNECT-REQ", title="Required disconnect rating",
          equation="I_req = k x I_hover",
          inputs={"k": P + "requirements.disconnect_factor", "i_hover": P + "performance.hover_current_a"},
          units={"k": "-", "i_hover": "A"})
def disconnect_required(k, i_hover):
    return {"i_req_a": k * i_hover}


# ----------------------------------------------------------------- claims
kit.claim("CL-J1-FIN-YAW-ARM", "Fin centroid aft of CG", calc="CALC-J1-FIN-YAW-ARM", output="arm_m", unit="m",
          limit=(">=", 0.0), cites=["SRC-J1-HEPPERLE-PLANK", "SRC-J1-BOXKITE-LEARN"],
          how="B3: AVL Cn_beta with fins, tubes and motors; must be positive with margin. Flight: FBWA yaw doublet on the twin.",
          note="Only 0.04 m (13 % chord): 40 % of the fin area is ahead of the CG. Weak weathercock stability in cruise "
               "is the likely mechanism behind the uncommanded FW yaw seen on all four student Box Kites.")
kit.claim("CL-J1-FIN-AREA-AHEAD", "Fin area ahead of the CG", calc="CALC-J1-FIN-YAW-ARM", output="fin_area_ahead_frac", unit="-",
          how="Geometry from params.json; re-run after B3 moves the fins or the CG.")
kit.claim("CL-J1-PROP-ARM", "Prop planes ahead of the CG", calc="CALC-J1-PROP-ARM", output="arm_m", unit="m",
          cites=["SRC-J1-RIBNER"],
          how="B3: include propeller normal force (Ribner) in the AVL/hand pitch and yaw stability sums; 0.7 chord ahead of the CG "
              "is destabilising in both axes.")
kit.claim("CL-J1-TUBE-F1", "Bare tube first bending mode", calc="CALC-J1-TUBE-MODE", output="f1_hz", unit="Hz",
          assumes=["ASM-J1-E-TUBE"],
          how="Tap test of one fin + tube + motor assembly (T-J1-TAP-TEST); bend test of the tube for E (T-J1-TUBE-BEND).",
          note="Tube alone, clamped at the chord plane, motor at the tip. The bonded fin should raise this a lot; it must be measured.")
kit.claim("CL-J1-MOTOR-1P-HOVER", "Motor 1P at hover", calc="CALC-J1-MOTOR-FREQ", output="f1P_hover_hz", unit="Hz",
          how="ESC telemetry or bidirectional DShot RPM in the hover log; harmonic notch centre (INS_HNTCH_FREQ).")
kit.claim("CL-J1-MOTOR-2P-HOVER", "Blade-pass 2P at hover", calc="CALC-J1-MOTOR-FREQ", output="f2P_hover_hz", unit="Hz",
          how="FFT of the hover IMU log (ArduPilot notch review tool) shows the 2P peak.")
kit.claim("CL-J1-MOTOR-1P-MAX", "Motor 1P at maximum thrust", calc="CALC-J1-MOTOR-FREQ", output="f1P_max_hz", unit="Hz",
          how="Thrust-stand RPM at full throttle (H1).")
kit.claim("CL-J1-TUBE-MODE-SEP", "Tube mode separation from forcing", calc="CALC-J1-MODE-SEP", output="sep_min", unit="-",
          limit=(">=", "ASM-J1-SEP-RULE"), assumes=["ASM-J1-SEP-RULE"],
          cites=["SRC-J1-AP-VIBE", "SRC-J1-AP-NOTCH"],
          how="C4 re-derives with the fin as a shear web; H1 tap test; hover VIBE < 30 m/s2 and Clip = 0 (SRC-J1-AP-VIBE).",
          note="FAILS on the bare tube: f1 sits 6 % from the hover 2P. Design the fin bond as the stiffener and move the mode.")
kit.claim("CL-J1-CL-CRUISE", "Cruise lift coefficient at the gate", calc="CALC-J1-TRIM-SM", output="CL_cruise", unit="-",
          how="B1/B2 from the drag polar; airspeed log in cruise.")
kit.claim("CL-J1-SM-TRIMMABLE", "Static margin trimmable, elevons neutral", calc="CALC-J1-TRIM-SM", output="sigma_trim", unit="-",
          limit=(">=", P + "requirements.static_margin_min"), verifies=["R-STATIC-MARGIN"], assumes=["ASM-J1-MH45-CM0"],
          cites=["SRC-J1-HEPPERLE-PLANK", "SRC-J1-MH45-HEPPERLE"],
          how="B2: XFOIL Cm at Re 3e5 with elevon deflection; B3: AVL trim at cruise CL. Flight: elevon trim position in FBWA.",
          note="FAILS against 5 %: the MH 45's +0.0145 trims ~2.7 % with neutral elevons at CL 0.54. Either B3 accepts "
               "~3 % (Hepperle: 2-5 % typical for planks) or the elevons carry up-trim in cruise, which costs CLmax and "
               "worsens CR-A1-05 (transition gate).")
kit.claim("CL-J1-DISCONNECT-REQ", "Required disconnect continuous rating", calc="CALC-J1-DISCONNECT-REQ", output="i_req_a", unit="A",
          verifies=["R-DISCONNECT"], how="1.25 x the logged hover current (tethered hover, H1).")
kit.claim("CL-J1-XT60-CONT", "XT60 continuous rating", value=35.0, unit="A", limit=(">=", "CL-J1-DISCONNECT-REQ"),
          verifies=["R-DISCONNECT"], cites=["SRC-J1-AMASS-XT60", "SRC-J1-HOLYBRO-CONN"],
          how="Maker sheet (35 A at 12 AWG, 85 K rise); Holybro says 30 A for < 60 degC rise. Bench: 30 A for 10 min, connector < 60 degC.",
          note="PROPOSED from the datasheet; margin +17 % on the Amass figure, 0 % on Holybro's. 12 AWG leads required.")
kit.claim("CL-J1-XT60-BURST", "XT60 one-minute rating", value=60.0, unit="A", limit=(">=", P + "electrical.peak_current_a"),
          verifies=["R-DISCONNECT"], cites=["SRC-J1-HOLYBRO-CONN"],
          how="Compare with the logged full-throttle pack current on the thrust stand (4 stations) or F4's output cap.",
          note="FAILS the 120 A momentary case (4 x 30 A). F1: AS150U, or cap the momentary current in F4's output limits.")
kit.claim("CL-J1-AS150U-CONT", "AS150U continuous rating", value=70.0, unit="A", limit=(">=", "CL-J1-DISCONNECT-REQ"),
          verifies=["R-DISCONNECT"], cites=["SRC-J1-AS150U"],
          how="Open the Amass AS150U sheet before ordering (UNVERIFIED reseller value); bench 30 A for 10 min.")
kit.claim("CL-J1-AS150U-BURST", "AS150U instantaneous rating", value=140.0, unit="A", limit=(">=", P + "electrical.peak_current_a"),
          verifies=["R-DISCONNECT"], cites=["SRC-J1-AS150U"],
          how="Same sheet; the pre-charge contact is the weak point (forum melt report): inspect after every full-throttle run.")

# ----------------------------------------------------------------- planned tests (H1 runs them)
kit.test("T-J1-TAP-TEST", "Tap test, fin + tube + motor assembly", verifies=["CL-J1-TUBE-F1", "CL-J1-TUBE-MODE-SEP"],
         procedure="Clamp the finished fin at the spar saddle; tap the motor; FFT of a phone accelerometer or the FC IMU raw log; "
                   "first mode must be >= 20 % from 1P/2P at hover and 1P at max.")
kit.test("T-J1-TUBE-BEND", "Three-point bend of the bought tube", verifies=["CL-J1-TUBE-F1"],
         procedure="Span 0.8 m, load at centre in 0.5 kg steps to 4 kg, dial gauge; E = F L^3 / (48 I delta). Replaces ASM-J1-E-TUBE.")
kit.test("T-J1-XT60-HEAT", "Connector heat run", verifies=["CL-J1-XT60-CONT"],
         procedure="30 A through the mated pair for 10 min on the bench supply or thrust stand; IR thermometer; rise <= 60 degC.")

if __name__ == "__main__":
    kit.write()
