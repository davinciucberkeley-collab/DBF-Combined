"""J1 outside research: the numbers from published data that other roles depend on, as proof-chain claims.

Run:  python -I redesign/team/J1/research_claims.py      (writes claims.json beside this file)
Then: python -I redesign/proofs/build_graph.py

Everything here is a first-order screen from public sources (REFERENCES.md); the owning role re-derives it.
Revision A1-R2 (2026-11-09, second pass): chord 0.32, S5010, motor tubes through the wing at x 0.045, 11x5.5MR,
cruise 16 m/s, hover 27 A. What matters now: (1) with the tubes at x 0.045 the fin side-area centroid sits 0.14 m
(43 % chord) aft of the CG and no fin area is ahead of it, (2) the props are only 0.05 m ahead of the CG,
(3) the bare motor tube's first bending mode (~183 Hz at E 100 GPa) still lands within 2 % of the hover 2P
(B4's 5 396 rpm), (4) the S5010 with elevons neutral trims no positive static margin (cm0 ~ 0), which is why D-19
carries the elevon up-trim inside the trimmed CLmax, and (5) an XT60 passes 1.25 x 27 A by 4 % and fails the
120 A momentary case. Standard library only.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../B2/params.json"])
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
           url="redesign/config-study/tiebreak/tailsitter-evidence/EVIDENCE.md",
           where="sections 1.2-1.3 (repo file, no external URL)", checked=SEEN)
kit.source("SRC-J1-MH45-HEPPERLE", "M. Hepperle: MH 45 airfoil page", "web",
           url="https://www.mh-aerotools.de/airfoils/mh45koo.htm", checked=SEEN,
           where="thickness 9.85 %, cm c/4 = +0.0145, Re >= 100 000, F3B tailless use",
           note="the MH 45 was the R0 section; superseded by the S5010 (CHANGE-LOG D-02). Kept as the comparison point")
kit.source("SRC-J1-HEPPERLE-PLANK", "M. Hepperle: Basic design of flying wing models (plank)", "web",
           url="https://www.mh-aerotools.de/airfoils/flywing1.htm", checked=SEEN,
           where="unswept wing: NP at c/4; stability coefficient typically 0.02-0.05; trim needs Cm = CL x sigma")
kit.source("SRC-J1-APC-PER3", "APC 11x4.5MR performance file PER3_11x45MR.dat", "datasheet",
           url="https://www.apcprop.com/files/PER3_11x45MR.dat", checked=SEEN,
           where="static: 5.02 N / 41 W at 5000 rpm, 7.25 N / 70 W at 6000, 9.91 N / 110 W at 7000; zero thrust at J ~0.545; "
                 "at 6000 rpm and 14.7 m/s: 0.32 N, eta 0.17; at 7000 rpm and 14.4 m/s: 2.38 N, eta 0.54, 64 W",
           note="the 11x4.5MR is now the stand A/B prop only (D-05); flight prop is the 11x5.5MR, whose rpm come from B4's claims")
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
kit.assumption("ASM-J1-APC-KT", "APC 11x4.5MR static thrust per rpm^2 (superseded)",
               "Static thrust of the 11x4.5MR scales as T = kT n^2 with kT = 7.254 N / 6000^2 rpm^2 (APC PER3 file)",
               basis="APC PER3 static rows: 5.02 N at 5000, 7.25 N at 6000, 9.91 N at 7000 rpm (within 2 % of n^2 scaling). "
                     "Superseded by D-05 (flight prop 11x5.5MR): J1's forcing frequencies now read B4's CL-B4-HOVER-RPM / "
                     "CL-B4-CRUISE-RPM; kept only because team/C1/claims.json still names it (C1 re-runs loads.py, CR-J1-10)",
               value=7.254 / 6000.0 ** 2, unit="N/rpm2", status="UNVERIFIED", cites=["SRC-J1-APC-PER3"])
kit.assumption("ASM-J1-MH45-CM0", "MH 45 quarter-chord moment coefficient (superseded)",
               "The MH 45 section with elevons neutral has cm c/4 = +0.0145 (2-D, Hepperle)",
               basis="Hepperle's MH 45 page. Superseded by D-02 (S5010, cm0 -0.004 at Re 2.3e5, P:b2.xfoil.cm0_2d_re2.3e5); "
                     "kept only because team/C1/claims.json still names it (C1 re-runs loads.py, CR-J1-10)",
               value=0.0145, unit="-", status="UNVERIFIED", cites=["SRC-J1-MH45-HEPPERLE"])
kit.assumption("ASM-J1-ETA-CRUISE", "Prop efficiency at ~1 N per prop, 15 m/s (11x4.5MR, superseded)",
               "The 11x4.5MR at 15 m/s and ~1 N thrust runs at J ~0.50-0.53, close to its zero-thrust J ~0.545, with eta 0.30-0.45",
               basis="APC PER3 rows: eta 0.17 at 6000 rpm / 14.7 m/s (0.32 N) and 0.54 at 7000 rpm / 14.4 m/s (2.38 N); 1 N lies between. "
                     "Superseded by D-05: the flight prop is the 11x5.5MR, B4 CL-B4-CRUISE-ETA 0.46 and E1 CL-E1-CRUISE-ETA-55 0.39 "
                     "(B4 CL-B4-CRUISE-ETA-OLD 0.37 for the 11x4.5MR confirms this band)",
               status="UNVERIFIED", cites=["SRC-J1-APC-PER3"])


# ----------------------------------------------------------------- calculations
@kit.calc("CALC-J1-FIN-YAW-ARM", title="Fin side-area centroid vs CG",
          equation="arm = (x_le + x_te)/2 - x_cg ; ahead = max(0, (x_cg - x_le)/(x_te - x_le)) ; arm_c = arm / c",
          inputs={"x_le": P + "fins.le_x_m", "x_te": P + "fins.te_x_m", "x_cg": P + "cg.x_target_m", "c": P + "wing.chord_m"},
          units={"x_le": "m", "x_te": "m", "x_cg": "m", "c": "m"}, cites=["SRC-J1-HEPPERLE-PLANK"])
def fin_yaw_arm(x_le, x_te, x_cg, c):
    arm = 0.5 * (x_le + x_te) - x_cg
    return {"arm_m": arm, "arm_chord": arm / c, "fin_area_ahead_frac": max(0.0, (x_cg - x_le) / (x_te - x_le))}


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


@kit.calc("CALC-J1-MOTOR-FREQ", title="Motor forcing frequencies at the three steady rpm",
          equation="f1P = rpm/60 ; f2P = 2 f1P (2-blade) at hover (B4), cruise (B4) and the capped full-throttle rpm",
          inputs={"rpm_h": "CL-B4-HOVER-RPM", "rpm_c": "CL-B4-CRUISE-RPM", "rpm_max": P + "propulsion.rpm_max"},
          units={"rpm_h": "rpm", "rpm_c": "rpm", "rpm_max": "rpm"})
def motor_freq(rpm_h, rpm_c, rpm_max):
    return {"f1P_hover_hz": rpm_h / 60.0, "f2P_hover_hz": rpm_h / 30.0,
            "f1P_cruise_hz": rpm_c / 60.0, "f2P_cruise_hz": rpm_c / 30.0,
            "f1P_max_hz": rpm_max / 60.0, "f2P_max_hz": rpm_max / 30.0,
            "band_lo_hz": 0.8 * rpm_h / 60.0, "band_hi_hz": 1.2 * rpm_max / 30.0}


@kit.calc("CALC-J1-MODE-SEP", title="Tube mode separation from motor forcing",
          equation="sep = min |f1/f - 1| over f in {1P, 2P} x {hover, cruise, max rpm}",
          inputs={"f1": "CL-J1-TUBE-F1", "a": "CL-J1-MOTOR-1P-HOVER", "b": "CL-J1-MOTOR-2P-HOVER",
                  "c": "CL-J1-MOTOR-1P-CRUISE", "d": "CL-J1-MOTOR-2P-CRUISE", "e": "CL-J1-MOTOR-1P-MAX", "f": "CL-J1-MOTOR-2P-MAX"},
          units={"f1": "Hz", "a": "Hz", "b": "Hz", "c": "Hz", "d": "Hz", "e": "Hz", "f": "Hz"})
def mode_separation(f1, a, b, c, d, e, f):
    seps = {"1P_hover": abs(f1 / a - 1), "2P_hover": abs(f1 / b - 1), "1P_cruise": abs(f1 / c - 1),
            "2P_cruise": abs(f1 / d - 1), "1P_max": abs(f1 / e - 1), "2P_max": abs(f1 / f - 1)}
    worst = min(seps, key=seps.get)
    return {"sep_min": seps[worst], "nearest": worst}


@kit.calc("CALC-J1-TRIM-SM", title="Static margin trimmable with elevons neutral (S5010)",
          equation="CL = m g / (0.5 rho V^2 S) ; sigma_trim = cm0 / CL  (Hepperle: Cm = CL sigma for a plank)",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "V": P + "performance.cruise_ms", "S": "CL-A1-WING-AREA", "cm0": P + "b2.xfoil.cm0_2d_re2.3e5"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "V": "m/s", "S": "m2", "cm0": "-"},
          cites=["SRC-J1-HEPPERLE-PLANK"])
def trim_static_margin(m, g, rho, V, S, cm0):
    CL = m * g / (0.5 * rho * V ** 2 * S)
    return {"CL_cruise": CL, "sigma_trim": cm0 / CL}


@kit.calc("CALC-J1-DISCONNECT-REQ", title="Required disconnect rating",
          equation="I_req = k x I_hover ; I_req_pess = k x I_hover_gate_wind (E2)",
          inputs={"k": P + "requirements.disconnect_factor", "i_hover": P + "performance.hover_current_a",
                  "i_hover_pess": "CL-E2-HOVER-I-GATE"},
          units={"k": "-", "i_hover": "A", "i_hover_pess": "A"})
def disconnect_required(k, i_hover, i_hover_pess):
    return {"i_req_a": k * i_hover, "i_req_pess_a": k * i_hover_pess}


# ----------------------------------------------------------------- claims
kit.claim("CL-J1-FIN-YAW-ARM", "Fin centroid aft of CG", calc="CALC-J1-FIN-YAW-ARM", output="arm_m", unit="m",
          limit=(">=", 0.0), verifies=["R-DIRECTIONAL"], cites=["SRC-J1-HEPPERLE-PLANK", "SRC-J1-BOXKITE-LEARN"],
          how="B3: AVL Cn_beta >= P:requirements.cnbeta_min with fins, tubes and props at R1 geometry (CL-B3-CNB re-run). "
              "Flight: FBWA yaw doublet on the twin; no growing yaw oscillation hands-off.",
          note="Geometry screen only, not Cn_beta. With the tubes through the wing at x 0.045 (D-04) the fin centroid is "
               "0.14 m (43 % chord) aft of the CG and no fin area is ahead of it; at R0 it was 0.04 m with 40 % ahead. "
               "This is the geometric reason B3's option O4b turned Cn_beta from -0.105 to +0.044 /rad. The FW yaw "
               "actuator question (CR-J1-05, F4) stands: Plane has no FW yaw stabilisation by default.")
kit.claim("CL-J1-FIN-AREA-AHEAD", "Fin area ahead of the CG", calc="CALC-J1-FIN-YAW-ARM", output="fin_area_ahead_frac", unit="-",
          how="Geometry from params.json; re-run after B3 moves the CG range (D-17).",
          note="Zero at R1: the fin LE (tube axis 0.045) is 1 mm aft of the CG target 0.044; at the aft CG limit 0.049 "
               "about 1.5 % of the fin area is ahead of the CG, still negligible.")
kit.claim("CL-J1-PROP-ARM", "Prop planes ahead of the CG", calc="CALC-J1-PROP-ARM", output="arm_m", unit="m",
          cites=["SRC-J1-RIBNER"],
          how="B3: include propeller normal force (Ribner) in the AVL/hand pitch and yaw stability sums.",
          note="0.05 m (15 % chord) ahead of the CG at R1 (was 0.21 m, 70 % chord, at R0): the destabilising prop "
               "normal-force moment is 4x smaller than it was. B3's R1 neutral point should move aft (D-17).")
kit.claim("CL-J1-TUBE-F1", "Bare tube first bending mode", calc="CALC-J1-TUBE-MODE", output="f1_hz", unit="Hz",
          assumes=["ASM-J1-E-TUBE"],
          how="Tap test of one fin + tube + motor assembly (T-J1-TAP-TEST); bend test of the tube for E (T-J1-TUBE-BEND).",
          note="Tube alone, cantilevered 0.19 m from the chord plane, motor + 11x5.5MR + mount at the tip. The bonded "
               "half-fin should raise this a lot; it must be measured. E 50-140 GPa puts f1 at 130-215 Hz.")
kit.claim("CL-J1-MOTOR-1P-HOVER", "Motor 1P at hover", calc="CALC-J1-MOTOR-FREQ", output="f1P_hover_hz", unit="Hz",
          how="ESC telemetry or bidirectional DShot RPM in the hover log; harmonic notch centre (INS_HNTCH_FREQ).",
          note="From B4's CL-B4-HOVER-RPM (11x5.5MR at the gate).")
kit.claim("CL-J1-MOTOR-2P-HOVER", "Blade-pass 2P at hover", calc="CALC-J1-MOTOR-FREQ", output="f2P_hover_hz", unit="Hz",
          how="FFT of the hover IMU log (ArduPilot notch review tool) shows the 2P peak.")
kit.claim("CL-J1-MOTOR-1P-CRUISE", "Motor 1P at cruise", calc="CALC-J1-MOTOR-FREQ", output="f1P_cruise_hz", unit="Hz",
          how="RPM telemetry in the cruise log (B4 CL-B4-CRUISE-RPM, 15 m/s).")
kit.claim("CL-J1-MOTOR-2P-CRUISE", "Blade-pass 2P at cruise", calc="CALC-J1-MOTOR-FREQ", output="f2P_cruise_hz", unit="Hz",
          how="FFT of the cruise IMU log.")
kit.claim("CL-J1-MOTOR-1P-MAX", "Motor 1P at the capped full-throttle rpm", calc="CALC-J1-MOTOR-FREQ", output="f1P_max_hz", unit="Hz",
          how="Thrust-stand RPM at the F4 output cap (H1); P:propulsion.rpm_max 9 350.",
          note="Unlimited on a fresh pack B4 gives 10 637 rpm (CL-B4-RPM-MAX-FULL): 1P 177 Hz, 2P 355 Hz for < 5 s.")
kit.claim("CL-J1-MOTOR-2P-MAX", "Blade-pass 2P at the capped full-throttle rpm", calc="CALC-J1-MOTOR-FREQ", output="f2P_max_hz", unit="Hz",
          how="Same stand run; the top of the forcing band C4 must clear (B4 CR-B4-07: 80-330 Hz).")
kit.claim("CL-J1-TUBE-MODE-SEP", "SUPERSEDED (bare-tube screen): tube mode separation from forcing", calc="CALC-J1-MODE-SEP",
          output="sep_min", unit="-", cites=["SRC-J1-AP-VIBE", "SRC-J1-AP-NOTCH"],
          how="C4 re-derives with the half-fin as a bonded shear web (CR-J1-03 / CR-B4-07); H1 tap test; hover VIBE "
              "< P:requirements.fc_vibe_max_ms2 and Clip = 0 (SRC-J1-AP-VIBE).",
          note="FAILS on the bare tube: f1 ~183 Hz sits 2 % from the hover 2P (180 Hz) and 9 % from the cruise 2P (200 Hz). "
               "The forcing sweeps 90-156 Hz (1P) and 180-312 Hz (2P) between hover and the capped maximum, so no bare-tube "
               "mode in 72-374 Hz clears 20 % at every steady point: the fin bond must put the first mode above ~375 Hz, "
               "or the tap test must show it damped (R-VIBRATION allows either). C4 owns the fix. D-100 (2026-11-13): no limit "
               "and no requirement link: the bare tube is not the design; C4's 3-D station model of the bonded fin "
               "(CL-C4-SIM-SEP) and T-C4-TAP-D3 are the claim and test of record for R-VIBRATION.")
kit.claim("CL-J1-CL-CRUISE", "Cruise lift coefficient at the gate", calc="CALC-J1-TRIM-SM", output="CL_cruise", unit="-",
          how="B1/B2 from the drag polar; airspeed log in cruise.",
          note="At 2.6 kg, 16 m/s, S 0.368 (was 0.54 at 15 m/s, S 0.345).")
kit.claim("CL-J1-SM-TRIMMABLE", "Static margin trimmable, elevons neutral (S5010)", calc="CALC-J1-TRIM-SM", output="sigma_trim", unit="-",
          cites=["SRC-J1-HEPPERLE-PLANK", "SRC-J1-MH45-HEPPERLE"],
          how="B2: XFOIL cm at the cruise Re (~3.5e5) with elevon deflection; B3: AVL trim at the cruise CL and SM 5 %. "
              "Flight: elevon trim position in FBWA (A2 limit elevon_trim_travel_max).",
          note="Informational since D-19 (SM stays 0.05; CR-J1-02 rejected). The S5010's cm0 is about zero "
               "(-0.004 at Re 2.3e5, +0.003 at 3e5, B2), so elevons-neutral it trims no positive static margin "
               "(-0.9 %): all 5 % of SM is carried by elevon up-trim (B2: about -4 deg at CL 0.5), and that penalty "
               "is already inside the trimmed CLmax 0.80 (CL-B2-CLMAX-DESIGN). The MH 45's +0.0145 would have trimmed "
               "3.3 % at this CL. R-STATIC-MARGIN is verified by B3's CL-B3-CG-AFT, not by this screen.")
kit.claim("CL-J1-DISCONNECT-REQ", "Required disconnect continuous rating", calc="CALC-J1-DISCONNECT-REQ", output="i_req_a", unit="A",
          verifies=["R-DISCONNECT"], how="1.25 x the logged hover current (tethered hover, H1).",
          note="1.25 x 27.0 A (params, E1). F1 sizes on E2's 29.9 A gate-wind hover (CR-E2-04): see CL-J1-DISCONNECT-REQ-PESS.")
kit.claim("CL-J1-DISCONNECT-REQ-PESS", "Required disconnect rating, E2 gate-wind hover", calc="CALC-J1-DISCONNECT-REQ",
          output="i_req_pess_a", unit="A", verifies=["R-DISCONNECT"],
          how="1.25 x the hover current logged in 5 m/s wind at the gate mass (H2).")
kit.claim("CL-J1-XT60-CONT", "SUPERSEDED (D-32, AS150U fitted): XT60 continuous rating", value=35.0, unit="A",
          cites=["SRC-J1-AMASS-XT60", "SRC-J1-HOLYBRO-CONN"],
          how="Maker sheet (35 A at 12 AWG, 85 K rise); Holybro says 30 A for < 60 degC rise. Bench: 34 A for 10 min, connector < 60 degC.",
          note="PROPOSED from the datasheet; +4 % on the Amass figure against 33.75 A, and Holybro's 30 A (< 60 degC) "
               "already fails it. Against E2's 37.4 A (CL-J1-DISCONNECT-REQ-PESS) the XT60 fails on both figures. 12 AWG leads required.")
kit.claim("CL-J1-XT60-CONT-PESS", "SUPERSEDED (D-32, AS150U fitted): XT60 continuous rating vs E2 gate-wind hover",
          value=35.0, unit="A", cites=["SRC-J1-AMASS-XT60"],
          how="Same heat run at 37 A for 10 min; rise <= 60 degC.",
          note="Was FAILS by 6 %. D-100: no limit and no requirement link, the XT60 is not fitted (D-32 AS150U; "
               "CL-J1-AS150U-CONT and F1's CL-F1-DISC-* verify R-DISCONNECT).")
kit.claim("CL-J1-XT60-BURST", "SUPERSEDED (D-32, AS150U fitted): XT60 one-minute rating", value=60.0, unit="A",
          cites=["SRC-J1-HOLYBRO-CONN"],
          how="Compare with the logged full-throttle pack current on the thrust stand (4 stations) or F4's output cap.",
          note="FAILS the 120 A momentary case (4 x 30 A). F1: AS150U, or a claim that the <= 5 s case at the 100 A "
               "limiter is inside a cited XT60 short-time rating (A1's condition, CHANGE-LOG CR-A2-08 row). D-100: no limit "
               "and no requirement link, the XT60 is not fitted (D-32 AS150U).")
kit.claim("CL-J1-AS150U-CONT", "AS150U continuous rating", value=70.0, unit="A", limit=(">=", "CL-J1-DISCONNECT-REQ-PESS"),
          verifies=["R-DISCONNECT"], cites=["SRC-J1-AS150U"],
          how="Open the Amass AS150U sheet before ordering (UNVERIFIED reseller value); bench 37 A for 10 min.")
kit.claim("CL-J1-AS150U-BURST", "AS150U instantaneous rating", value=140.0, unit="A", limit=(">=", P + "electrical.peak_current_a"),
          verifies=["R-DISCONNECT"], cites=["SRC-J1-AS150U"],
          how="Same sheet; the pre-charge contact is the weak point (forum melt report): inspect after every full-throttle run.")

# ----------------------------------------------------------------- planned tests (H1 runs them)
kit.test("T-J1-TAP-TEST", "Tap test, fin + tube + motor assembly", verifies=["CL-J1-TUBE-F1", "CL-J1-TUBE-MODE-SEP"],
         procedure="Clamp the finished half-fin at the through-core block; tap the motor; FFT of a phone accelerometer or the "
                   "FC IMU raw log; first mode must be >= 20 % from 1P and 2P at hover, cruise and the capped maximum "
                   "(outside 72-374 Hz), or its damping ratio recorded for C4.")
kit.test("T-J1-TUBE-BEND", "Three-point bend of the bought tube", verifies=["CL-J1-TUBE-F1"],
         procedure="Span 0.8 m, load at centre in 0.5 kg steps to 4 kg, dial gauge; E = F L^3 / (48 I delta). Replaces ASM-J1-E-TUBE.")
kit.test("T-J1-XT60-HEAT", "Connector heat run", verifies=["CL-J1-XT60-CONT", "CL-J1-XT60-CONT-PESS"],
         procedure="37 A through the mated pair for 10 min on the bench supply or thrust stand; IR thermometer; rise <= 60 degC.")

if __name__ == "__main__":
    kit.write()
