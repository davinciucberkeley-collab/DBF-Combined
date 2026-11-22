"""Concept A proof chain, part 2: flutter, divergence, loads and margins, vibration (D-185), servo torque, foam at 103 kPa.

Structural margins, flutter onsets and the modal / forced-response numbers come from heavy runs (FE, p-method sweep, Ritz): they
are read from the stored output files through `read_value`, and the minimum / maximum / ratio that decides a limit is computed
here. Servo torque is re-computed from the load terms. Run via run_all.py.
"""
import math
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
       how="Airspeed limit VD 24 m/s on the flight card; the wing stalls before n 5.03 (stall line 3.16, structures_run.md s2).", equation="structures_run.md s2 C1 table, T-084 rerun (ASM-C1-UDE-D-FRAC half rule); read, not recomputed")

# ================================================================ structural margins at 1.5 x limit (stored tables)
for cid, title, param, parts, reqs in [
        ("CL-A-MS-SPAR", "Spar 12x10 root bending, MS at 1.5 x n 3.4", "P:struct.ms_spar", ["WNG-002"], ["A-P13"]),
        ("CL-A-MS-BOND", "Rib saddle on the spar (thinnest bond), MS", "P:struct.ms_bond_thin", ["FIN-005-R", "FIN-005-L", "WNG-002"], ["A-P13"]),
        ("CL-A-MS-ARM", "Motor arm 12x10 under a 30 N prop strike, MS", "P:struct.ms_arm_strike", ["CGE-002-A", "CGE-002-B"], ["A-P13"]),
        ("CL-A-MS-ARM-SOCKET", "Motor arm in its socket, strike couple, MS", "P:struct.ms_arm_socket", ["CGE-002-A", "CGE-002-B", "CGE-001"], ["A-P13"]),
        ("CL-A-MS-CUP-HEADPULL", "Motor cup head pull-through (PETG) at the 0.90 cap thrust + 1P, MS", "P:struct.ms_cup_op_headpull", ["CGE-003-UR", "CGE-003-UL", "CGE-003-LR", "CGE-003-LL"], ["A-P13"]),
        ("CL-A-MS-CUP-STRIKE", "Motor cup head pull-through under the 30 N transverse prop strike, MS", "P:struct.ms_cup_headpull_strike", ["CGE-003-UR", "CGE-003-UL", "CGE-003-LR", "CGE-003-LL"], ["A-P13"]),
        ("CL-A-MS-CUP-PLATE", "Motor cup plate bending past the sleeve end under the strike, MS", "P:struct.ms_cup_plate_strike", ["CGE-003-UR", "CGE-003-UL", "CGE-003-LR", "CGE-003-LL"], ["A-P13"]),
        ("CL-A-MS-CUP-HOLE", "Motor cup screw-hole bearing under a blade-stop torque, MS", "P:struct.ms_cup_screw_hole_s3", ["CGE-003-UR", "CGE-003-UL", "CGE-003-LR", "CGE-003-LL"], ["A-P13"]),
        ("CL-A-MS-CUP-BOND", "Motor cup to arm bond under strike torsion + torque, MS", "P:struct.ms_cup_bond_strike", ["CGE-003-UR", "CGE-003-UL", "CGE-003-LR", "CGE-003-LL"] + ["CGE-002-A", "CGE-002-B"], ["A-P13"]),
        ("CL-A-MS-ARM-BLADE", "Motor arm 12x10 root bending with the blade-offset strike lever, MS", "P:struct.ms_arm_strike_blade", ["CGE-002-A", "CGE-002-B"], ["A-P13"]),
        ("CL-A-MS-FATIGUE-HUBWALL", "Hub arm-socket wall, 2000 cycles to the cap thrust, MS", "P:struct.ms_fatigue_hub_wall", ["CGE-001"], ["A-P13"]),
        ("CL-A-MS-FATIGUE-ARM", "Arm tube bending amplitude at 4e6 cycles of 1P, MS", "P:struct.ms_fatigue_arm", ["CGE-002-A", "CGE-002-B"], ["A-P13"]),
        ("CL-A-MS-RIB", "Fin rib 14x12 torsion under one foot load, MS", "P:struct.ms_rib_torsion", ["FIN-002-R", "FIN-002-L"], ["A-P13"]),
        ("CL-A-MS-FIN", "Fin tube 16x14 in-plane bending at the foot load, MS", "P:struct.ms_fin_inplane", ["FIN-001-R", "FIN-001-L"], ["A-P13"]),
        ("CL-A-MS-PACK-CRASH", "Bridge under pack + hub at the 12 g crash, MS (pack retention)", "P:struct.ms_bridge_crash", ["CGE-004", "CGE-008", "PWR-001"], ["A-P5", "A-P13"])]:
    stored(cid, title, param, "-", limit=(">=", "P:req.ms_min"), verifies=reqs, parts=parts, assumes=(["ASM-A-HUB-WALL"] if cid == "CL-A-MS-ARM-SOCKET" else []),
           how="Re-run qp/A/structures/iter2_run.py or arm_cup_checks.py (1.5 x limit, CF corner values kd / nom / hi); coupon test of the thinnest bond and of the motor cup before the wing is cut.",
           equation="MS = allowable / design stress - 1 from structures/iter2_margins.md or arm_cup_checks.md (stress already carries the factors); read, not re-run")
# ================================================================ bridge torsion (D-206)
def bridge_tau(od, idd, m, k):
    j = math.pi / 32 * (od ** 4 - idd ** 4)            # mm4
    return k * m * 1e3 * (od / 2) / j                    # MPa


BR_IN = {"od": "P:struct.bridge_od_mm", "idd": "P:struct.bridge_id_mm"}
kit.calc("CALC-A-BRIDGE-TAU-F2", equation="tau = k x M x (OD / 2) / J, J = pi / 32 (OD^4 - ID^4)", inputs=dict(BR_IN, m="P:struct.bridge_roll_f2_nm", k="P:struct.k_cf"),
         units={"od": "mm", "idd": "mm", "m": "N m"}, output="tau_mpa")(bridge_tau)
kit.calc("CALC-A-BRIDGE-TAU-S2", equation="tau = 1.0 x M x (OD / 2) / J (damage case, D-202)", inputs=dict(BR_IN, m="P:struct.bridge_roll_s2_nm", k="P:struct.k_strike"),
         units={"od": "mm", "idd": "mm", "m": "N m"}, output="tau_mpa")(bridge_tau)
kit.claim("CL-A-BRIDGE-TORSION-F2", "Bridge 16x14 torsion shear, F2 motor fault at the CFRP factor (bridge alone)", calc="CALC-A-BRIDGE-TAU-F2", output="tau_mpa", unit="MPa",
          limit=("<=", "P:struct.cf_shear_mpa"), verifies=["A-P13"], parts=["CGE-004", "CGE-001", "CGE-006"],
          how="python -I qp/A/structures/bridge_torsion_d206.py; hub FEA run d206 (fea_hub.py) shows the bridge field; a torsion coupon on the 16x14 offcut would replace the 30 MPa EST.")
kit.claim("CL-A-BRIDGE-TORSION-S2", "Bridge 16x14 torsion shear, 30 N prop strike in the disc plane (factor 1.0, bridge alone)", calc="CALC-A-BRIDGE-TAU-S2", output="tau_mpa", unit="MPa",
          limit=("<=", "P:struct.cf_shear_mpa"), verifies=["A-P13"], parts=["CGE-004", "CGE-001", "CGE-006"],
          how="As CL-A-BRIDGE-TORSION-F2.")

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
def stored_calc_in_band():
    kit.calc("CALC-A-VIB-IN-BAND-READ", inputs={"v": "P:sim.vib_inband_corners"}, equation="count of corners with a strong mode in the band, read from structures_run.md s4 and T085_report.md s3.1 (not re-run)",
             title="Stored result: strong modes in the band", output="v")(read_value)
    return "CALC-A-VIB-IN-BAND-READ"


@kit.calc("CALC-A-VIB-LOW-LIMIT", equation="limit = hover 1P low edge / 1.2 = (6,789 rpm / 60) / 1.2", inputs={"rpm": "P:sim.hover_1p_rpm_lo", "sep": "P:req.band_sep"}, output="f_hz")
def vib_low_limit(rpm, sep):
    return rpm / 60 / sep


@kit.calc("CALC-A-VIB-HIGH-LIMIT", equation="limit = highest 2P edge x 1.2 = (8,028 rpm hover lean / 60 x 2 = 267.6 Hz) x 1.2", inputs={"f": "P:sim.hover_lean_2p_hz", "sep": "P:req.band_sep"}, output="f_hz")
def vib_high_limit(f, sep):
    return f * sep


kit.claim("CL-A-VIB-LOW-LIMIT", "Upper edge allowed for strongly coupled modes below the rotor bands", calc="CALC-A-VIB-LOW-LIMIT", output="f_hz", unit="Hz", verifies=["A-P10"],
          how="Lowest hover 1P 113 Hz (6,789 rpm, X2216, 1.8796 kg; structures_run.md s4), 20 % separation rule (A-P10(a)); band 94-321 Hz.")
kit.claim("CL-A-VIB-HIGH-LIMIT", "Lower edge allowed for strongly coupled modes above the rotor bands", calc="CALC-A-VIB-HIGH-LIMIT", output="f_hz", unit="Hz", verifies=["A-P10"],
          how="Highest 2P 268 Hz (hover lean, 8,028 rpm; cruise 2P 248 Hz; structures_run.md s4), 20 % separation rule (A-P10(a)); band 94-321 Hz.")
kit.calc("CALC-A-VIB-LOW", inputs={"x": "P:sim.vib_below_hz"}, output="f_hz",
         equation="highest strongly coupled (coupling >= 0.5) mode below the bands over kd / nom / hi; FE run read from structures/structures_run.md s4 (T-084 rerun, spar-only beam FE), not re-run; excludes the in-band strong mode (CL-A-VIB-IN-BAND)")(highest)
kit.calc("CALC-A-VIB-HIGH", inputs={"x": "P:sim.vib_above_hz"}, output="f_hz",
         equation="lowest strongly coupled mode above the bands over kd / nom / hi; FE run read from structures/structures_run.md s4 (T-084 rerun, spar-only beam FE), not re-run")(lowest)
kit.claim("CL-A-VIB-LOW", "Highest strongly coupled mode below the rotor bands (hi corner)", calc="CALC-A-VIB-LOW", output="f_hz", unit="Hz",
          limit=("<=", "CL-A-VIB-LOW-LIMIT"), verifies=["A-P10"], parts=["CGE-002-A", "CGE-002-B", "CGE-004", "WNG-002"],
          how="Tap test of the built cage (T-A-TAP): modes within +-20 % of FE or re-tune. Margin is 17 % at the hi corner (81 vs 94 Hz), 43 % at kd (structures_run.md s4). This claim alone does NOT show D-185 (a) met: see CL-A-VIB-IN-BAND.")
kit.claim("CL-A-VIB-HIGH", "Lowest strongly coupled mode above the rotor bands (kd corner, fin f1)", calc="CALC-A-VIB-HIGH", output="f_hz", unit="Hz",
          limit=(">=", "CL-A-VIB-HIGH-LIMIT"), verifies=["A-P10"], parts=["FIN-001-R", "FIN-001-L"], how="Fin tap test at build (T-A-TAP): lowest strong mode above the band 438-532 Hz in FE (structures_run.md s4).")
kit.claim("CL-A-VIB-IN-BAND", "Corners (kd / nom / hi) with a strongly coupled mode INSIDE the excluded rotor band (D-185 (a) needs none)",
          calc=stored_calc_in_band(), output="v", unit="-", limit=("<=", 0), verifies=["A-P10"], parts=["CGE-002-A", "CGE-002-B", "CGE-004", "WNG-002"],
          how="CARRIED FAIL (T-066 M-1, T-085, D-236): structures_run.md s4 spar-only model has a strong mode (cy 0.52) at 201 / 215 / 244 Hz inside the 94-321 Hz band; the upgraded model (T085_report.md s3.1) has the governing strong mode at 94.6-108.7 Hz (cx 0.74-0.85, cy 1.12-1.35) at kd / nom / hi, 23 of 24 pad / tray / hub / cell bound groups fail, the one passing group by 0.1 Hz. No limit relaxed, band and 0.5 coupling rule unchanged. TP-10b (T-A-TAP) on the built airframe decides; routes in T085_report.md s7.")
kit.calc("CALC-A-VIB-FC", inputs={"x": "P:sim.vib_fc_ms2"}, output="a_ms2",
         equation="worst FC acceleration over 6,000-11,415 rpm, U 1.0 g mm per rotor, zeta 1 % and 0.5 %, kd / nom / hi; read from structures/structures_run.md s4, not re-run")(highest)
kit.claim("CL-A-VIB-FC", "Flight-controller vibration, worst of the forced-response sweep", calc="CALC-A-VIB-FC", output="a_ms2", unit="m/s2",
          limit=("<=", "P:req.vibe_max_ms2"), verifies=["A-P10"], parts=["AVN-002", "AVN-010", "AVN-007"],
          how="IMU VIBE < 30 m/s2 in the first tethered hover (T-A-TETHER-VIBE). The worst point (11,400 rpm) is beyond the all-four duty 1.0 state (10,343 rpm), where the sweep reads 18.5-19.1; up to 9,349 rpm it reads 15.0-15.2 (structures_run.md s4).")
kit.calc("CALC-A-VIB-GM", inputs={"x": "P:sim.gm_nominal"}, output="gm", equation="smallest gain margin over pitch / roll / yaw x kd / nom / hi at the nominal mode frequencies (fu_cage.py); STALE: iter3_run.md values (MN2212 / iteration-2 cage); re-run with X2216 inertias pending, not re-run (T-066 M-1)")(lowest)
kit.claim("CL-A-VIB-GM", "Rate-loop gain margin, minimum over axes and corners (nominal modes)", calc="CALC-A-VIB-GM", output="gm", unit="-",
          limit=(">=", "P:req.gm_min"), verifies=["A-P10"], parts=["AVN-002", "CGE-004", "CGE-002-A"], how="UNVERIFIED: inputs are the MN2212-era iter3_run.md values; sitl/fu_cage.py (iteration-2 cage, MN2212 aero) needs rebuilding for the X2216 / 1.8796 kg cage before it can be re-run. Then re-run with the built-cage tap-test frequencies; hard-mounted FC.")


@kit.calc("CALC-A-VIB-GM-SHIFT", equation="smallest gain margin with all flexible modes shifted -20 % and +20 % (tap-test tolerance)", inputs={"lo": "P:sim.gm_shifted", "hi": "P:sim.gm_shifted_up"}, output="gm")
def gm_shifted(lo, hi):
    return min(min(lo), min(hi))


# ================================================================ elevon linkage strength, D-212 rev 3 (review r2 C-1, M-1..M-4). Failing claims stay failing.
LINK_PARTS = ["MEC-003-R", "MEC-003-L", "MEC-004-R", "MEC-004-L", "WNG-006-R", "WNG-006-L"]
LINK_EQ = "read from mechanism/out/linkage_loads_check.json (python -I redesign/qp/A/mechanism/linkage_loads_check.py); model, validity and allowable source in that script's header"
COUPON = ("NOT SHOWN BY ANALYSIS; superseded by the test claims CL-A-HORN-RIB-COUPON, CL-A-HORN-STALL-STEP, CL-A-ELEVON-TORSION-COUPON and CL-A-HORN-STALL-BENCH (test node T-A-HORN-RIB) "
          "once those tests have run and pass (route to A-P13, review r3 M-1). Gate: E1 horn-rib coupon, a 100 mm span of tape-skinned elevon with the printed horn bonded in its slot, both ends clamped 50 mm "
          "either side of the rib; pull the horn hole along the chord with 2.156 x 17.05 = 36.8 N for 30 s (pass: no crack, no slip, < 0.5 deg set; local result only: in flight the elevon continues ~160 mm outboard), "
          "then the 51 N stall step (pass: no crack, hole elongation <= 0.1 mm). Bench stall test on the aircraft (BUILD D5b): endpoints set to +-20 deg, then drive one servo into the stop for 5 s and inspect "
          "horn, rib, elevon and stop. Fallback if these fail: a spanwise CF torsion tube along the hinge line (trade table D-212 rev 3, row J).")
for cid, title, param, lim, extra, how in [
        ("CL-A-HORN-RIB-FOAM-HOLD", "Horn rib face shear in the elevon foam at 1.5 x VD hold (x 2.156), beam-on-foundation FE, worst foam case", "P:linkage.rib_foam_hold_kpa", "P:linkage.foam_shear_kpa", ["ASM-A-FOAM-ALLOW"], COUPON),
        ("CL-A-HORN-RIB-FOAM-STALL", "Horn rib face shear in the foam at the 51 N servo stall force (x 1.4375)", "P:linkage.rib_foam_stall_kpa", "P:linkage.foam_shear_kpa", ["ASM-A-FOAM-ALLOW"], COUPON),
        ("CL-A-ELEVON-TORSION-FOAM", "Elevon torsion beside the horn, foam only (tape skin not credited), 1.5 x VD hold (x 2.156)", "P:linkage.elevon_torsion_hold_kpa", "P:linkage.foam_shear_kpa", ["ASM-A-FOAM-ALLOW"], COUPON),
        ("CL-A-HORN-BLADE-HOLD", "Printed horn blade bending at 1.5 x VD hold (x 2.156), printed lying flat (in-layer)", "P:linkage.blade_root_hold_mpa", "P:linkage.petg_allow_mpa", ["ASM-A-PETG-ALLOW"], COUPON),
        ("CL-A-HORN-BLADE-STALL", "Printed horn blade bending at the 51 N stall force (x 1.4375)", "P:linkage.blade_root_stall_mpa", "P:linkage.petg_allow_mpa", ["ASM-A-PETG-ALLOW"], COUPON),
        ("CL-A-HORN-BEARING-HOLD", "Clevis pin bearing in the 2 mm horn at 1.5 x VD hold (x 2.156)", "P:linkage.bearing_hold_mpa", "P:linkage.petg_allow_mpa", ["ASM-A-PETG-ALLOW"], COUPON),
        ("CL-A-HORN-BEARING-STALL", "Clevis pin bearing in the 2 mm horn at the 51 N stall force (x 1.4375)", "P:linkage.bearing_stall_mpa", "P:linkage.petg_allow_mpa", ["ASM-A-PETG-ALLOW"], COUPON),
        ("CL-A-ROD-LEG-STALL", "Z-bend leg: yield needed at 1.5 x the 51 N stall force, rod lifted against the keeper (e 1.9 mm), vs the A228 music-wire allowable", "P:linkage.rod_yield_req_mpa", "P:linkage.a228_allow_mpa", ["ASM-A-ROD-GRADE"],
         "Receipt test of a formed M02 rod at 91 N (1.5 x 51 N x e_hi / e_lo = 1.9 / 1.6, rod lifted against the keeper, review r3 m-3) along the rod, 10 s, no permanent set over 0.2 mm; else A228 1.2 mm wire.")]:
    stored(cid, title, param, "kPa" if "kpa" in param else "MPa", limit=("<=", lim), verifies=["A-P13"], parts=LINK_PARTS, assumes=extra, how=how, equation=LINK_EQ)
stored("CL-A-HORN-SHEAROUT-STALL", "Horn hole shear-out (1.65 mm ligament) at the 51 N stall force (x 1.4375); allowable PETG 20 MPa / sqrt(3) EST", "P:linkage.shearout_stall_mpa", "MPa",
       limit=("<=", "P:linkage.shearout_allow_mpa"), verifies=["A-P13"], parts=LINK_PARTS, assumes=["ASM-A-PETG-ALLOW"],
       how="Passes by 4 % on an EST allowable (review r3 m-13), so it is no margin: the stall step of the horn-rib coupon (CL-A-HORN-STALL-STEP) and the bench stall test decide it.", equation=LINK_EQ)
stored("CL-A-KEEPER-BRIDGE-STALL", "Keeper bridge (MEC-008) bending at the 51 N stall force (x 1.4375), rod lifted against the keeper; allowable PETG 20 MPa EST", "P:linkage.keeper_bridge_stall_mpa", "MPa",
       limit=("<=", "P:linkage.petg_allow_mpa"), verifies=["A-P13"], parts=["MEC-008-R", "MEC-008-L", "MEC-004-R", "MEC-004-L"], assumes=["ASM-A-PETG-ALLOW"],
       how="Passes by 3 % on an EST allowable (19.5 vs 20 MPa; 9.8 MPa at hold), so it is no margin. Creep and preload loss are '-' (not analysed): retorque and inspect the keeper screw at BUILD D2a, D5b and every preflight; the bench stall test (CL-A-HORN-STALL-BENCH) loads it too, inspect the keeper for a crack afterwards (review r3 m-4).", equation=LINK_EQ)
stored("CL-A-SERVO-SPEED", "Elevon servo speed margin: loaded rate over the 152 deg/s of the +-11 deg, 2.2 Hz roll sinusoid (AR-005, 6.0 V pair)", "P:linkage.servo_speed_margin_r2", "-",
       limit=(">=", "P:linkage.servo_speed_margin_min"), verifies=["A-P11"], parts=["MEC-001-R", "MEC-001-L", "MEC-002-R", "MEC-002-L", "MEC-004-R", "MEC-004-L"],
       how="Hand calculation (AR-005): linear torque-speed line, gearing 0.909-0.928 from the solved linkage, end-point load. Required rates are EST; 7.2 V speed is not published so the 6 V no-load speed is used. Bench ramp of the built rail at BUILD D5b closes it. The full-throw sinusoid R3 (0.84) is not a required case.",
       equation="read from mechanism/out/linkage_loads_check.json servo_speed_torque_T056 (python -I redesign/qp/A/mechanism/linkage_loads_check.py)")

# ---- test-form claims (review r3 M-1): value "-" until the test is run, so they stay PROPOSED, never FAIL. Pass criteria are numeric. When a test
# ---- passes, the analysis FAIL claim it supersedes is re-pointed at the test claim by a logged edit (A-P13 then rests on the test).
TEST_PARTS = ["MEC-004-R", "MEC-004-L", "WNG-006-R", "WNG-006-L"]
kit.claim("CL-A-HORN-RIB-COUPON", "Horn-rib coupon: load held 30 s without damage, over the required 36.8 N (2.156 x the 17.05 N hold force)", unit="-", limit=(">=", 1.0), value="-",
          verifies=["A-P13"], parts=TEST_PARTS, assumes=[],
          how="E1 coupon: 100 mm tape-skinned elevon span, horn bonded in the slot, clamps 50 mm each side of the rib; 36.8 N along the chord for 30 s. Value = held load / 36.8 N, pass >= 1.0 with no crack, no slip, set < 0.5 deg. Local result only (clamps 50 mm from the rib, ~160 mm of elevon in flight). Supersedes CL-A-HORN-RIB-FOAM-HOLD once run and passed.")
kit.claim("CL-A-HORN-STALL-STEP", "Horn-rib coupon, stall step: 51 N held 5 s, hole elongation and cracks", unit="mm", limit=("<=", 0.1), value="-",
          verifies=["A-P13"], parts=TEST_PARTS,
          how="After the 36.8 N step, 51 N (the servo stall force, 0.397 N m / (8.5 mm x 0.916)) along the chord for 5 s. Value = hole elongation measured with a 1.2 mm pin gauge, pass <= 0.1 mm with no crack and set < 0.5 deg. Record what yields first. Supersedes CL-A-HORN-RIB-FOAM-STALL and CL-A-HORN-BEARING-STALL once run and passed; the 1.4375 scatter factor is not in the coupon (one coupon): run 3 coupons, lowest governs.")
kit.claim("CL-A-ELEVON-TORSION-COUPON", "Elevon-section torsion coupon: torque held over the required 0.161 N m (2.156 x the 74.65 N mm outboard hinge moment at VD)", unit="-", limit=(">=", 1.0), value="-",
          verifies=["A-P13"], parts=["WNG-006-R", "WNG-006-L"],
          how="A tape-skinned elevon section about 160 mm long, root clamped, torque applied through the horn hole path (horn force x 9.155 mm) to 0.161 N m held 30 s. Value = held torque / 0.161 N m, pass >= 1.0 with no tape debond or crack and twist set < 0.5 deg at the trailing edge. Supersedes CL-A-ELEVON-TORSION-FOAM (foam only, tape skin not credited) once run and passed. If it fails: the spanwise CF tube (trade row J).")
kit.claim("CL-A-HORN-STALL-BENCH", "Bench stall test on the built aircraft: 51 N for 5 s into the 21 deg stop, hole elongation", unit="mm", limit=("<=", 0.1), value="-",
          verifies=["A-P13"], parts=TEST_PARTS + ["MEC-001-R", "MEC-001-L"],
          how="BUILD D5b: endpoints temporarily set past the stop, servo at 7.2 V driven into the +21 deg stop (smallest arm lever, 51 N) for 5 s, each elevon. Value = hole elongation (1.2 mm pin gauge), pass <= 0.1 mm with no crack in horn, rib, slot tape or stop, and trailing-edge set < 0.5 deg. Then the endpoints go back to +-20 deg.")

stored("CL-A-LINKAGE-FREEPLAY", "Elevon linkage free play from the hole clearances and the Z-bend freedom (clevis cheek holes '-')", "P:linkage.free_play_deg", "deg",
       limit=("<=", "P:linkage.free_play_guide_deg"), verifies=["A-P13"], parts=["MEC-002-R", "MEC-002-L", "MEC-003-R", "MEC-003-L", "MEC-004-R", "MEC-004-L", "MEC-008-R", "MEC-008-L"],
       how="BASIS = FLUTTER (review r3 m-7): the 1 deg limit is the SERVO.md s4 flutter guide, the only sourced number; a control-precision limit has none. BUILD D5b / E1: measure the BUILT trailing-edge free play with the servo powered at neutral (dial gauge, +-0.05 mm); the budget excludes servo gear backlash and the clevis cheek holes (both '-'). The hinge damper (FIXES2 s1) removes the linear flutter dependence on K, but a free-play limit cycle is nonlinear and not covered, so a measured value above 1 deg stays a FAIL; the +-20 deg endpoints (1 deg short of the 21 deg stop) prevent a servo-driven stall only.",
       equation="read from mechanism/out/linkage_kinematics.json free_play_budget_deg (python -I redesign/qp/A/mechanism/elevon_linkage.py)")

kit.claim("CL-A-VIB-GM-SHIFT", "Rate-loop gain margin with the cage modes shifted +-20 %", calc="CALC-A-VIB-GM-SHIFT", output="gm", unit="-",
          limit=(">=", "P:req.gm_min"), verifies=["A-P10"], parts=["AVN-002", "CGE-004", "CGE-002-A"],
          how="Tap test of the built cage (T-A-TAP): first pitch mode 9-17 Hz, first roll mode 21-43 Hz (GM >= 2 grid, iter3_run.md); outside that window re-tune the rate loop.",
          note="D-191 (CLAIMS-FIX s4): with the QP-3 gains (pitch P 0.15 / D 0.002 / FLTD 40) the minimum was 1.64 (1.56 at cant 17); pitch P 0.12 / D 0.0012 / FLTD 60 and yaw P 0.37 give 2.03 (roll, kd corner, modes -20 %; pitch 2.33).")


# ================================================================ servo torque at the 7.2 V rail (FIXES2 s2)
@kit.calc("CALC-A-SERVO", equation="factor = servo torque / (1.5 x (hinge moment at VD + preload + damper at slew)); cold case with the real arm ratio 9.155 / 8.5 (D-212 rev 2; the gearing of the solved linkage is 0.906 to 0.929, 1 / 1.077 = 0.929); ratio = servo / hinge",
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
          note="Equal arms (the SERVO.md convention) give 1.47, 2 % short; FIXES2 s2 reported 1.58 with a 12 mm arm and 12.9 mm horn; D-212 rev 2 (arm hole 8.5 mm, horn hole 9.155 mm over the hinge) gives 1.58 again, and the solved linkage gearing at +-20 deg (0.906 to 0.929) now matches the 8.5 / 9.155 ratio the claim assumes. Bounding case: VD hinge moment, full slew and 0 C together.")
kit.claim("CL-A-SERVO-RATIO", "Servo stall torque over the hinge moment at VD (A-P11 wording)", calc="CALC-A-SERVO", output="ratio_to_hinge", unit="-", limit=(">=", "P:req.servo_ratio_min"),
          verifies=["A-P11"], parts=SERVO_PARTS, how="Bench: stall torque of the flight servo at 7.2 V.")

if __name__ == "__main__":
    kit.write()
