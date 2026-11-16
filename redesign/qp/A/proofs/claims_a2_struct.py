"""Concept A proof chain, part 2: flutter, divergence, loads and margins, vibration (D-185), servo torque, foam at 103 kPa.

Structural margins, flutter onsets and the modal / forced-response numbers come from heavy runs (FE, p-method sweep, Ritz): they
are read from the stored output files through `read_value`, and the minimum / maximum / ratio that decides a limit is computed
here. Servo torque is re-computed from the load terms. Run via run_all.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "proofs"))     # redesign/proofs
import proofkit as pk  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from claimhelp_a import make_stored, pin, read_value  # noqa: E402,F401

kit = pk.Kit(__file__, params=["../params-A.json"], out="claims.a2_struct.json")
stored = make_stored(kit)


def lowest(x):
    return min(x)


def highest(x):
    return max(x)


# ================================================================ the G8 line
@kit.calc("CALC-A-FLUTTER-LINE", equation="line = 1.2 x VD", inputs={"k": "P:req.flutter_factor", "vd": "P:req.vd_ms"}, units={"vd": "m/s"}, output="v_ms")
def flutter_line(k, vd):
    return k * vd


kit.claim("CL-A-FLUTTER-LINE", "Flutter / divergence line, 1.2 x VD", calc="CALC-A-FLUTTER-LINE", output="v_ms", unit="m/s", verifies=["A-P13"],
          how="A-P13 / G8: every flutter, divergence and reversal speed is compared with this value (28.8 m/s at VD 24).")

# ================================================================ elevon flutter with the hinge damper (p-method sweep, stored)
ELEVON_HOW = ("E1 coupon (FIXES2 s8): ring-down damping c >= 7.1e-4 N m s/rad at 25 C, c(50 C) >= 4.0e-4; the model holds for every K from 0.01 to 20 N m/rad, "
              "so free play does not matter while the damper is filled and sealed (O-rings BOM R13, fill checked every preflight).")
PARTS_EL = ["WNG-006-R", "WNG-006-L", "WNG-007-R", "WNG-007-L", "WNG-009-R", "WNG-009-L", "WNG-010-R", "WNG-010-L"]
for cid, title, param, extra in [
        ("CL-A-FLUTTER-ELEVON-NOM", "Elevon flutter onset with the hinge damper, nominal 25 C (lowest of kd / nom / hi)", "P:sim.flutter_nom_ms", []),
        ("CL-A-FLUTTER-ELEVON-HOT", "Elevon flutter onset with the hinge damper, hot 50 C (lowest of kd / nom / hi)", "P:sim.flutter_hot_ms", ["ASM-A-DAMPER-T"]),
        ("CL-A-FLUTTER-ELEVON-COLD", "Elevon flutter onset with the hinge damper, cold 0 C (lowest of kd / nom / hi)", "P:sim.flutter_cold_ms", ["ASM-A-DAMPER-T"])]:
    calc = "CALC-" + cid[3:]
    kit.calc(calc, inputs={"x": param}, equation="min over the three wing corners (kd / nom / hi) of the lowest onset over the K grid 0.01-20 N m/rad, "
             "read from structures/fixes2_cdamp.md (p-method, 600 K points, V <= 60 m/s); not re-run",
             assumes=extra + ["ASM-A-RELIABLE"], output="v_ms")(lowest)
    kit.claim(cid, title, calc=calc, output="v_ms", unit="m/s", limit=(">=", "CL-A-FLUTTER-LINE"), verifies=["A-P13"], parts=PARTS_EL,
              assumes=extra + ["ASM-A-RELIABLE"], how=ELEVON_HOW)
stored("CL-A-FLUTTER-HALF", "Elevon flutter onset with a half-filled (leaking) damper, kd corner", "P:sim.flutter_half_kd_ms", "m/s", parts=PARTS_EL, assumes=["ASM-A-RELIABLE"],
       how="Fault case, no limit stated: seal with the two O-rings (BOM R13) and check the fill at every preflight (FIXES2 s1.3, s9).",
       note="Fault case, not a requirement. D-195: 33.0 m/s (kd; nom 35.0, hi 39.0), all above the 28.8 line; the lighter 6.7 g elevon removed the old 0.3 m/s shortfall. Recorded without a limit on purpose: the mitigation is the seal and the preflight check.",
       equation="min onset, half of the hot damper c, kd corner; read from structures/fixes2_cdamp.md, not re-run")

# ================================================================ wing flutter, divergence, reversal, gust
def wing_flutter_lowest(base, nofin):
    return min(min(base), min(nofin))


kit.calc("CALC-A-FLUTTER-WING", inputs={"base": "P:sim.wing_flutter_ms", "nofin": "P:sim.wing_flutter_nofin_ms"}, output="v_ms",
         equation="min over kd / nom / hi of the base case and of the fins-off sensitivity (Ritz + strip Theodorsen, balance lumps on the wing); read from FIXES s1.3, not re-run")(wing_flutter_lowest)
kit.claim("CL-A-FLUTTER-WING", "Wing bending-torsion flutter speed, lowest case (fins off, kd corner)", calc="CALC-A-FLUTTER-WING", output="v_ms", unit="m/s",
          limit=(">=", "CL-A-FLUTTER-LINE"), verifies=["A-P13"], parts=["WNG-001", "WNG-002", "FIN-001-R", "FIN-001-L"],
          how="Tap / ground-vibration test with the fin on one tip (12 Hz and 44 Hz modes); FLUTTER.md open item 3.")
stored("CL-A-DIVERGENCE", "Torsional divergence speed (kd corner, EA 0.10 c aft)", "P:sim.divergence_ms", "m/s", limit=(">=", "CL-A-FLUTTER-LINE"), verifies=["A-P13"],
       parts=["WNG-001", "WNG-002"], how="Torsion coupon (FLUTTER.md): measured GJ >= 2 N m2; divergence needs only > 0.2 N m2.",
       equation="Ritz / Bredt GJ model, FLUTTER.md verdict (lowest of 128-171 m/s at e/c 0.10); read, not re-run")
kit.calc("CALC-A-REVERSAL", inputs={"x": "P:sim.reversal_3d_ms"}, output="v_ms",
         equation="min over kd / nom (3-D lift basis, y 0.04-0.35, e/c 0.10); read from FIXES s1.3, not re-run")(lowest)
kit.claim("CL-A-REVERSAL", "Control reversal speed, 3-D lift basis (kd corner)", calc="CALC-A-REVERSAL", output="v_ms", unit="m/s",
          limit=(">=", "CL-A-FLUTTER-LINE"), verifies=["A-P13"], parts=["WNG-006-R", "WNG-006-L"],
          how="Measure elevon effectiveness vs airspeed on the first cruise sorties.",
          note="The board ruled the 3-D basis (BOARD QP-4 s3). On the 2-D strip bound the same speeds are 28 / 32 m/s (kd / nom), 28 below the 28.8 line: 'marginal on the 2-D bound' (FLUTTER.md, FIXES s1.3).")
stored("CL-A-GUST-N", "Gust load factor at VD 24 (U 4 m/s)", "P:sim.gust_n_vd", "g", limit=("<=", "P:req.n_limit"), verifies=["A-P13"], parts=["WNG-002"],
       how="Airspeed limit VD 24 m/s on the flight card; the wing stalls before n 5.03 (stall line 3.96).", equation="iter3_run.md C1 table (ASM-C1-UDE-D-FRAC half rule); read, not recomputed")

# ================================================================ structural margins at 1.5 x limit (stored tables)
for cid, title, param, parts, reqs in [
        ("CL-A-MS-SPAR", "Spar 12x10 root bending, MS at 1.5 x n 3.4", "P:struct.ms_spar", ["WNG-002"], ["A-P13"]),
        ("CL-A-MS-BOND", "Rib saddle on the spar (thinnest bond), MS", "P:struct.ms_bond_thin", ["FIN-005-R", "FIN-005-L", "WNG-002"], ["A-P13"]),
        ("CL-A-MS-ARM", "Motor arm 12x10 under a 30 N prop strike, MS", "P:struct.ms_arm_strike", ["CGE-002-UR", "CGE-002-UL", "CGE-002-LR", "CGE-002-LL"], ["A-P13"]),
        ("CL-A-MS-ARM-SOCKET", "Motor arm in its socket, strike couple, MS", "P:struct.ms_arm_socket", ["CGE-002-UR", "CGE-002-UL", "CGE-002-LR", "CGE-002-LL", "CGE-001"], ["A-P13"]),
        ("CL-A-MS-RIB", "Fin rib 14x12 torsion under one foot load, MS", "P:struct.ms_rib_torsion", ["FIN-002-R", "FIN-002-L"], ["A-P13"]),
        ("CL-A-MS-FIN", "Fin tube 16x14 in-plane bending at the foot load, MS", "P:struct.ms_fin_inplane", ["FIN-001-R", "FIN-001-L"], ["A-P13"]),
        ("CL-A-MS-PACK-CRASH", "Bridge under pack + hub at the 12 g crash, MS (pack retention)", "P:struct.ms_bridge_crash", ["CGE-004", "CGE-008", "PWR-001"], ["A-P5", "A-P13"])]:
    stored(cid, title, param, "-", limit=(">=", "P:req.ms_min"), verifies=reqs, parts=parts, assumes=(["ASM-A-HUB-WALL"] if cid == "CL-A-MS-ARM-SOCKET" else []),
           how="Re-run qp/A/structures/iter2_run.py (FE, 1.5 x limit, CF corner values kd / nom / hi); coupon test of the thinnest bond before the wing is cut.",
           equation="MS = allowable / design stress - 1 from structures/iter2_margins.md (stress already carries the 1.5 factor); read, not re-run")
stored("CL-A-LANDING-STROKE", "Landing crush stroke at 1.2 m/s on the fin-tip feet", "P:struct.landing_stroke_mm", "mm", limit=("<=", "P:struct.landing_stroke_max_mm"), verifies=["A-P13"],
       parts=["GER-001-UR", "GER-001-UL", "GER-001-LR", "GER-001-LL", "GER-002-UR", "GER-002-UL", "GER-002-LR", "GER-002-LL"],
       how="Drop test of the feet at 1.2 m/s on the built aircraft; 20 mm available.", equation="landing_a.py via STRUCTURES iteration 2 (A-P13 basis); read, not re-run")

# ================================================================ foam at the 103 kPa basis (stored MS)
for cid, title, param, parts, extra in [
        ("CL-A-FOAM-SPAR-BOND", "Foam shear around the spar, bond over |y| <= 0.20 m (FIXES2 rule), MS at 103 kPa basis", "P:struct.foam_ms_spar_bond", ["WNG-001", "WNG-002"], ["ASM-A-FOAM-ALLOW"]),
        ("CL-A-FOAM-FIN-SLOT", "Foam bearing at the fin slot, MS at 103 kPa", "P:struct.foam_ms_fin_slot", ["WNG-001", "FIN-003-R", "FIN-003-L"], []),
        ("CL-A-FOAM-TRAY", "Pack tray on the LE slot floor, 12 g crash, quarter floor carrying, MS at 103 kPa", "P:struct.foam_ms_tray_quarter", ["WNG-001", "CGE-008", "PWR-001"], []),
        ("CL-A-FOAM-SERVO", "Servo stalled into the stop, epoxy on four pocket walls, MS (shear)", "P:struct.foam_ms_servo_stall", ["WNG-001", "MEC-001-R", "MEC-001-L"], ["ASM-A-FOAM-ALLOW"]),
        ("CL-A-FOAM-CAP-PEEL", "Stop reaction peeling a lens cap off the tape skin, MS on the foam (tension)", "P:struct.foam_ms_cap_peel", ["WNG-008-RU", "WNG-008-RL", "WNG-008-LU", "WNG-008-LL"], ["ASM-A-FOAM-ALLOW"])]:
    stored(cid, title, param, "-", limit=(">=", "P:req.ms_min"), verifies=["A-P13"], parts=parts, assumes=extra,
           how="Weigh and test a FOAMULAR 150 block (M11); pull coupon for the cap bond (E1 step 5): tape-skin peel has no allowable.",
           equation="MS from structures/foam_103.md (compressive 103 kPa data sheet; tension 129 / shear 86 EST); read, not re-run")

# ================================================================ vibration, D-185
@kit.calc("CALC-A-VIB-LOW-LIMIT", equation="limit = hover 1P low edge / 1.2 = (6,018 rpm / 60) / 1.2", inputs={"rpm": "P:sim.hover_1p_rpm_lo", "sep": "P:req.band_sep"}, output="f_hz")
def vib_low_limit(rpm, sep):
    return rpm / 60 / sep


@kit.calc("CALC-A-VIB-HIGH-LIMIT", equation="limit = cruise 2P high edge x 1.2 = 253 Hz x 1.2", inputs={"f": "P:sim.cruise_2p_hz_hi", "sep": "P:req.band_sep"}, output="f_hz")
def vib_high_limit(f, sep):
    return f * sep


kit.claim("CL-A-VIB-LOW-LIMIT", "Upper edge allowed for strongly coupled modes below the rotor bands", calc="CALC-A-VIB-LOW-LIMIT", output="f_hz", unit="Hz", verifies=["A-P10"],
          how="Hover 1P 100-119 Hz (6,018-7,151 rpm), 20 % separation rule (A-P10(a)).")
kit.claim("CL-A-VIB-HIGH-LIMIT", "Lower edge allowed for strongly coupled modes above the rotor bands", calc="CALC-A-VIB-HIGH-LIMIT", output="f_hz", unit="Hz", verifies=["A-P10"],
          how="Cruise 2P 243-253 Hz, 20 % separation rule (A-P10(a)).")
kit.calc("CALC-A-VIB-LOW", inputs={"x": "P:sim.vib_below_hz"}, output="f_hz",
         equation="highest strongly coupled (coupling >= 0.5) mode below the bands over kd / nom / hi; FE run read from structures/iter3_run.md, not re-run")(highest)
kit.calc("CALC-A-VIB-HIGH", inputs={"x": "P:sim.vib_above_hz"}, output="f_hz",
         equation="lowest strongly coupled mode above the bands over kd / nom / hi; FE run read from structures/iter3_run.md, not re-run")(lowest)
kit.claim("CL-A-VIB-LOW", "Highest strongly coupled mode below the rotor bands (hi corner)", calc="CALC-A-VIB-LOW", output="f_hz", unit="Hz",
          limit=("<=", "CL-A-VIB-LOW-LIMIT"), verifies=["A-P10"], parts=["CGE-002-UR", "CGE-002-UL", "CGE-002-LR", "CGE-002-LL", "CGE-004", "WNG-002"],
          how="Tap test of the built cage (T-A-TAP): modes within +-20 % of FE or re-tune. Margin is about 7 % at the hi corner, 31 % at kd.")
kit.claim("CL-A-VIB-HIGH", "Lowest strongly coupled mode above the rotor bands (kd corner, fin f1)", calc="CALC-A-VIB-HIGH", output="f_hz", unit="Hz",
          limit=(">=", "CL-A-VIB-HIGH-LIMIT"), verifies=["A-P10"], parts=["FIN-001-R", "FIN-001-L"], how="Fin tap test at build (T-A-TAP): f1 432-525 Hz in FE.")
kit.calc("CALC-A-VIB-FC", inputs={"x": "P:sim.vib_fc_ms2"}, output="a_ms2",
         equation="worst FC acceleration over 6,000-10,500 rpm, U 1.0 g mm per rotor, zeta 1 % and 0.5 %, kd / nom / hi; read from structures/iter3_run.md, not re-run")(highest)
kit.claim("CL-A-VIB-FC", "Flight-controller vibration, worst of the forced-response sweep", calc="CALC-A-VIB-FC", output="a_ms2", unit="m/s2",
          limit=("<=", "P:req.vibe_max_ms2"), verifies=["A-P10"], parts=["AVN-002", "AVN-001", "AVN-007"],
          how="IMU VIBE < 30 m/s2 in the first tethered hover (T-A-TETHER-VIBE). The worst point (10,500 rpm) is unreachable; at the 0.90 cap (9,349 rpm) the sweep reads 19.6-20.1.")
kit.calc("CALC-A-VIB-GM", inputs={"x": "P:sim.gm_nominal"}, output="gm", equation="smallest gain margin over pitch / roll / yaw x kd / nom / hi at the nominal mode frequencies (fu_cage.py); read from iter3_run.md, not re-run")(lowest)
kit.claim("CL-A-VIB-GM", "Rate-loop gain margin, minimum over axes and corners (nominal modes)", calc="CALC-A-VIB-GM", output="gm", unit="-",
          limit=(">=", "P:req.gm_min"), verifies=["A-P10"], parts=["AVN-002", "CGE-004", "CGE-002-UR"], how="Re-run sitl/fu_cage.py with the built-cage tap-test frequencies; hard-mounted FC.")


@kit.calc("CALC-A-VIB-GM-SHIFT", equation="smallest gain margin with all flexible modes shifted -20 % and +20 % (tap-test tolerance)", inputs={"lo": "P:sim.gm_shifted", "hi": "P:sim.gm_shifted_up"}, output="gm")
def gm_shifted(lo, hi):
    return min(min(lo), min(hi))


kit.claim("CL-A-VIB-GM-SHIFT", "Rate-loop gain margin with the cage modes shifted +-20 %", calc="CALC-A-VIB-GM-SHIFT", output="gm", unit="-",
          limit=(">=", "P:req.gm_min"), verifies=["A-P10"], parts=["AVN-002", "CGE-004", "CGE-002-UR"],
          how="Tap test of the built cage (T-A-TAP): first pitch mode 9-17 Hz, first roll mode 21-43 Hz (GM >= 2 grid, iter3_run.md); outside that window re-tune the rate loop.",
          note="D-191 (CLAIMS-FIX s4): with the QP-3 gains (pitch P 0.15 / D 0.002 / FLTD 40) the minimum was 1.64 (1.56 at cant 17); pitch P 0.12 / D 0.0012 / FLTD 60 and yaw P 0.37 give 2.03 (roll, kd corner, modes -20 %; pitch 2.33).")


# ================================================================ servo torque at the 7.2 V rail (FIXES2 s2)
@kit.calc("CALC-A-SERVO", equation="factor = servo torque / (1.5 x (hinge moment at VD + preload + damper at slew)); cold case with the real arm ratio 12.9 / 12; ratio = servo / hinge",
          inputs=pin("servo", "stall_72_nm", "hinge_vd_nm", "preload_nm", "damper_slew_nm", "damper_slew_cold_nm", "load_factor", "arm_mm", "horn_mm"))
def servo_factors(stall_72_nm, hinge_vd_nm, preload_nm, damper_slew_nm, damper_slew_cold_nm, load_factor, arm_mm, horn_mm):
    req = load_factor * (hinge_vd_nm + preload_nm + damper_slew_nm)
    req_cold = load_factor * (hinge_vd_nm + preload_nm + damper_slew_cold_nm)
    return {"factor_25c": stall_72_nm / req, "factor_0c_equal_arms": stall_72_nm / req_cold,
            "factor_0c_real_arms": stall_72_nm * horn_mm / arm_mm / req_cold, "ratio_to_hinge": stall_72_nm / hinge_vd_nm}


SERVO_PARTS = ["MEC-001-R", "MEC-001-L", "MEC-002-R", "MEC-002-L", "MEC-004-R", "MEC-004-L"]
kit.claim("CL-A-SERVO-FACTOR", "Servo torque factor at 7.2 V, 25 C (ES3054HV)", calc="CALC-A-SERVO", output="factor_25c", unit="-", limit=(">=", "P:req.servo_factor_min"),
          verifies=["A-P11"], parts=SERVO_PARTS, how="M12: measure the rail under two-servo load (7.2 V jumper set; at 6.0 V the factor is 1.30 and fails); E1 measures the hinge and damper torque.")
kit.claim("CL-A-SERVO-COLD", "Servo torque factor at 7.2 V, damper at 0 C, real arm ratio", calc="CALC-A-SERVO", output="factor_0c_real_arms", unit="-", limit=(">=", "P:req.servo_factor_min"),
          verifies=["A-P11"], parts=SERVO_PARTS, assumes=["ASM-A-DAMPER-T"], how="E1 step 6: ring-down at 0 C; confirm the slew + VD hinge-moment bounding case on the bench.",
          note="Equal arms (the SERVO.md convention) give 1.47, 2 % short; FIXES2 s2 reports 1.58 with the drawn 12 mm arm and 12.9 mm horn. Bounding case: VD hinge moment, full slew and 0 C together.")
kit.claim("CL-A-SERVO-RATIO", "Servo stall torque over the hinge moment at VD (A-P11 wording)", calc="CALC-A-SERVO", output="ratio_to_hinge", unit="-", limit=(">=", "P:req.servo_ratio_min"),
          verifies=["A-P11"], parts=SERVO_PARTS, how="Bench: stall torque of the flight servo at 7.2 V.")

if __name__ == "__main__":
    kit.write()
