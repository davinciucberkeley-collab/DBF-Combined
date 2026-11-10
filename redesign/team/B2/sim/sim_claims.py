"""B2 verification-round claims (B2-R3) for the proof chain: wing aero on the settled geometry and A3 roll-up.

Run from the repo root after verify_wing.py (and cfd2d_section.py, then verify_wing.py --params):
    python -I redesign/team/B2/sim/sim_claims.py      -> team/B2/sim/claims.sim.json
then python -I redesign/proofs/build_graph.py.
Reads P:b2sim.* (sim/params.json), P:b2.* (team/B2/params.json), params.json, mechanisms params, and claims of
B3 (CL-B3-XNP), A3 (CL-A3-MASS-PREDICTED, CL-A3-CG-X, CL-A3-CG-X-PRED) and D6 (CL-D6-TORQUE-FACTOR).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../../params/params.json", "../params.json", "params.json",
                               "../../../subsystems/mechanisms/params.json"], out="claims.sim.json")
G_KGF = 9.80665
WING = ["WNG-001", "WNG-002", "WNG-003"]

kit.source("SRC-B2-SU2", "SU2 8.5 2-D RANS runs, team/B2/sim/cfd2d_section.py", "web",
           url="https://su2code.github.io",
           where="team/B2/sim/out/cfd2d_results.json; INC_RANS Spalart-Allmaras fully turbulent, gmsh meshes "
                 "9k/18k/36k cells (refinement sqrt 2), quad boundary layer, far field 50 c",
           note="fully turbulent: no laminar separation bubble, so clmax and hinge moments bracket XFOIL rather than "
                "replace it; not compared with test data at this Re")

kit.assumption("ASM-B2R3-SM-EQUIV", "Trimmed CLmax follows the static margin",
               "The pod and propellers change the trimmed CLmax only through the NP shift; trimmed CLmax is read "
               "from the props-off wing + fin model at the same static margin as the real aircraft (B3 NP)",
               basis="R2 sweep: CLmax depends on SM, not on CG station (WING-AERO.md section 3); the pod carries no "
                     "elevon and sits on the wing root strip that never stalls first (first stall y 0.071 m is the "
                     "inboard elevon end, outside the pod's 0.07 m half-width)", status="UNVERIFIED")
kit.assumption("ASM-B2R3-VA", "Full elevon travel up to VA 20.5 m/s",
               "Elevon hinge moments: 25 deg at VA 20.5 m/s and <= 1/3 travel (8.33 deg) at VD",
               basis="params requirements.vd_ms note (D-50, F4 CR-F4-12): full travel to VA 20.5 m/s, <= 1/3 at VD "
                     "held by the flight envelope", value=20.5, unit="m/s", status="PROPOSED")
kit.assumption("ASM-B2R3-CFD-TOL", "Grid uncertainty limit",
               "A CFD number that drives a requirement must have a fine-grid GCI <= 5 %",
               basis="Roache GCI, Fs 1.25, three levels at r = sqrt 2 (SIM-TOOLS.md practice)", value=0.05, unit="-")
kit.assumption("ASM-B2R3-CONV-RULE", "Discretisation acceptance rule",
               "An XFOIL panel or AVL lattice value used for a requirement is accepted if the finest level run gives "
               "a value at least as favourable (the value used is conservative); the spread is reported",
               basis="clmax spreads 1.7 % (XFOIL 160-400 panels, monotone rising) and 1.6 % (AVL, non-monotone) "
                     "exceed the 1 % used in R2; a conservative value is the professional fallback")


def interp(tab, x):
    xs, ys = [r[0] for r in tab], [r[1] for r in tab]
    if x <= xs[0]:
        i = 0
    elif x >= xs[-1]:
        i = len(xs) - 2
    else:
        i = max(j for j in range(len(xs) - 1) if xs[j] <= x)
    return ys[i] + (ys[i + 1] - ys[i]) * (x - xs[i]) / (xs[i + 1] - xs[i])


@kit.calc("CALC-B2R3-STALL", title="Stall speed at the as-designed CG points and masses",
          equation="SM = (Xnp_B3 - x_cg)/c; CLmax = kd * interp(SM, CLmax(SM)); "
                   "Vs = sqrt(2 m g / (rho b c CLmax)); Re correction: CLmax *= 1 + s (Re_s - Re_x)/1e5",
          inputs={"tab": "P:b2sim.avl.clmax_vs_sm", "xnp": "CL-B3-XNP", "xr": "P:cg.x_range_m",
                  "xbf": "CL-A3-CG-X", "xp": "CL-A3-CG-X-PRED", "kd": "ASM-B2-CLMAX-KD",
                  "mg": "P:requirements.mtow_gate_kg", "mp": "CL-A3-MASS-PREDICTED", "g": "P:env.g_ms2",
                  "rho": "P:env.rho_kgm3", "b": "P:wing.span_m", "c": "P:wing.chord_m",
                  "k": "P:requirements.transition_factor", "s": "P:b2sim.xfoil.clmax_re_slope_per_1e5",
                  "rex": "P:b2.xfoil.re_stall"},
          units={"xnp": "m", "xr": "m", "xp": "m", "mg": "kg", "mp": "kg", "g": "m/s2", "rho": "kg/m3", "b": "m",
                 "c": "m"},
          assumes=["ASM-B2R3-SM-EQUIV", "ASM-B2-CLMAX-KD"])
def stall(tab, xnp, xr, xbf, xp, kd, mg, mp, g, rho, b, c, k, s, rex):
    out = {}
    pts = {"fwd": xr[0], "aft": xr[1], "basic": xbf * c, "pred": xp}
    for tag, x in pts.items():
        sm = (xnp - x) / c
        cl = kd * interp(tab, sm)
        for mtag, m in (("gate", mg), ("predm", mp)):
            vs = math.sqrt(2 * m * g / (rho * b * c * cl))
            re_s = vs * c / 1.48e-5
            clc = cl * (1 + s * (re_s - rex) / 1e5)                 # one Re iteration is enough (|dRe| < 0.2e5)
            vs = math.sqrt(2 * m * g / (rho * b * c * clc))
            out[f"Vs_{tag}_{mtag}"] = vs
            out[f"Vtr_{tag}_{mtag}"] = k * vs
        out[f"SM_{tag}"] = sm
        out[f"CLmax_{tag}"] = cl
    return out


@kit.calc("CALC-B2R3-STALL-TURB", title="Stall at the forward CG if the boundary layer were turbulent from the LE",
          equation="CLmax' = CLmax_fwd * clmax_turb / clmax_free; Vs' = Vs_fwd sqrt(clmax_free / clmax_turb); "
                   "clmax_turb = XFOIL tripped at 2 % c (lower bound) or SU2 SA L2 sweep max",
          inputs={"vs": "CL-B2R3-VS-GATE-FWD", "su2": "P:b2sim.cfd.clmax_2d", "trip": "P:b2sim.xfoil.clmax_tripped",
                  "xf": "P:b2.xfoil.clmax_2d_stall"},
          units={"vs": "m/s"})
def stall_turb(vs, su2, trip, xf):
    return {"ratio_trip": trip / xf, "Vs_trip": vs * math.sqrt(xf / trip),
            "ratio_su2": su2 / xf, "Vs_su2": vs * math.sqrt(xf / su2), "su2_over_trip": su2 / trip}


@kit.calc("CALC-B2R3-HINGE", title="Elevon hinge moment per servo, VA full travel and VD 1/3 travel",
          equation="H = C_h q c^2 s; C_h(25) = XFOIL inviscid max (design), C_h(8.3) = interp of XFOIL inviscid "
                   "max at 5 and 10 deg; T_servo = SF * max(H) * k_linkage (envelope: 25 deg to VA, 1/3 at VD); "
                   "T_servo_vdfull = SF * H(25 deg, VD) * k_linkage (R-SERVO-TORQUE as written); ratio_visc = max(|C_h SU2 L2 alpha -4|, SU2 bound alpha 0) / C_h XFOIL inviscid",
          inputs={"ch25": "P:b2.xfoil.hinge_coef_max", "ch5": "P:b2sim.xfoil.ch_inv_m5_max",
                  "ch10": "P:b2sim.xfoil.ch_inv_m10_max", "su2_25": "P:b2sim.cfd.ch_m25_am4",
                  "su2_25b": "P:b2sim.cfd.ch_m25_a0_bound", "rho": "P:env.rho_kgm3", "va": "ASM-B2R3-VA",
                  "vd": "P:requirements.vd_ms", "c": "P:wing.chord_m", "yin": "P:wing.elevon.inboard_y_m",
                  "yout": "P:wing.elevon.outboard_y_m", "sf": "P:requirements.servo_torque_factor",
                  "kl": "CL-D6-TORQUE-FACTOR"},
          units={"rho": "kg/m3", "va": "m/s", "vd": "m/s", "c": "m", "yin": "m", "yout": "m"},
          assumes=["ASM-B2-HINGE-INVISCID", "ASM-B2R3-VA"])
def hinge(ch25, ch5, ch10, su2_25, su2_25b, rho, va, vd, c, yin, yout, sf, kl):
    s = (yin[1] - yin[0]) + (yout[1] - yout[0])
    d3 = 25.0 / 3.0
    ch8 = ch5 + (ch10 - ch5) * (d3 - 5.0) / 5.0
    h_va = ch25 * 0.5 * rho * va * va * c * c * s
    h_vd = ch8 * 0.5 * rho * vd * vd * c * c * s
    h = max(h_va, h_vd)
    h_full = ch25 * 0.5 * rho * vd * vd * c * c * s          # R-SERVO-TORQUE as written: +/-25 deg at VD
    return {"H_VA_Nm": h_va, "H_VD_Nm": h_vd, "H_design_Nm": h, "ch8": ch8, "H_VD_full_Nm": h_full,
            "T_direct_kgfcm": sf * h / G_KGF * 100, "T_servo_kgfcm": sf * h * kl / G_KGF * 100,
            "T_servo_vdfull_kgfcm": sf * h_full * kl / G_KGF * 100, "T_direct_vdfull_kgfcm": sf * h_full / G_KGF * 100,
            "visc_ratio": max(abs(su2_25), abs(su2_25b)) / ch25}


@kit.calc("CALC-B2R3-CONV", title="Discretisation checks: XFOIL panels, AVL lattice, SU2 grid",
          equation="spread = (max - min) / mean over the levels; cons = finest / used - 1; GCI_fine (SU2, 3 levels)",
          inputs={"pan": "P:b2sim.xfoil.panel_clmax", "lat": "P:b2sim.avl.lattice_clmax",
                  "latx": "P:b2sim.avl.lattice_xnp", "g": "P:b2sim.cfd.gci_f-25_a0_re4.4e5",
                  "g2": "P:b2sim.cfd.gci_f+0_a12_re2.6e5"})
def conv(pan, lat, latx, g, g2):
    sp = lambda v: (max(v) - min(v)) / (sum(v) / len(v))
    # pan: 160/220/300/400 panels (220 used); lat: 6x0.5/8x0.6/12x1/16x1.4 (12x1 used). "cons" = finest / used - 1:
    # >= 0 means the value carried into the stall claims is below the finest-discretisation value (conservative)
    return {"xfoil_spread": sp(pan), "avl_clmax_spread": sp(lat), "avl_xnp_spread": sp(latx),
            "xfoil_cons": pan[3] / pan[1] - 1, "avl_cons": lat[3] / lat[2] - 1,
            "gci_ch": g["ch"]["gci_fine"], "gci_cl": g["CL"]["gci_fine"], "gci_clmax": g2["CL"]["gci_fine"]}


@kit.calc("CALC-B2R3-LOADS", title="Root bending at the limit load factor, AVL vs Schrenk",
          equation="M = n (m g / 2) ybar b/2; ratio = ybar_Schrenk / ybar_AVL",
          inputs={"yb": "P:b2sim.avl.ybar_frac", "ys": "P:b2sim.hand.schrenk_ybar_frac",
                  "n": "P:requirements.load_factor_limit_pos", "mg": "P:requirements.mtow_gate_kg",
                  "g": "P:env.g_ms2", "b": "P:wing.span_m"},
          units={"mg": "kg", "g": "m/s2", "b": "m"})
def loads(yb, ys, n, mg, g, b):
    m1 = mg * g / 2 * yb * b / 2
    return {"M_root_1g": m1, "M_root_limit": n * m1, "M_root_limit_schrenk": n * m1 * ys / yb, "schrenk_ratio": ys / yb}


@kit.calc("CALC-B2R3-CLA-HAND", title="AVL lift slope vs Helmbold",
          equation="ratio = CLa_AVL / CLa_Helmbold",
          inputs={"avl": "P:b2.avl.cla_per_rad", "h": "P:b2sim.hand.helmbold_cla"},
          units={"avl": "1/rad", "h": "1/rad"})
def cla_hand(avl, h):
    return {"ratio": avl / h}


# ---------------------------------------------------------------- claims
how_stall = "T-B2-STALL at the gate mass and the marked forward CG; CLmax = 2 m g / (rho S Vs^2)"
kit.claim("CL-B2R3-SM-FWD", "Static margin at the forward CG limit, B3 NP", calc="CALC-B2R3-STALL",
          output="SM_fwd", unit="-", how="(CL-B3-XNP - cg.x_range_m[0]) / c; CG balance test T-A3-CG-BALANCE")
kit.claim("CL-B2R3-CLMAX-FWD", "Trimmed CLmax at the forward CG limit", calc="CALC-B2R3-STALL", output="CLmax_fwd",
          unit="-", parts=WING, how=how_stall)
kit.claim("CL-B2R3-VS-GATE-FWD", "Stall at 2.6 kg, forward CG limit (as designed)", calc="CALC-B2R3-STALL",
          output="Vs_fwd_gate", unit="m/s", limit=("<=", "P:requirements.stall_max_ms"), verifies=["R-STALL"],
          parts=WING, how=how_stall)
kit.claim("CL-B2R3-VS-GATE-AFT", "Stall at 2.6 kg, aft CG limit (as designed)", calc="CALC-B2R3-STALL",
          output="Vs_aft_gate", unit="m/s", limit=("<=", "P:requirements.stall_max_ms"), verifies=["R-STALL"],
          parts=WING, how=how_stall)
kit.claim("CL-B2R3-VS-PRED", "Stall at the A3 predicted mass and CG", calc="CALC-B2R3-STALL",
          output="Vs_pred_predm", unit="m/s", limit=("<=", "P:requirements.stall_max_ms"), parts=WING,
          how="T-B2-STALL at the as-built mass; the expected flight value")
kit.claim("CL-B2R3-VTR-GATE-FWD", "1.3 Vs at 2.6 kg, forward CG, vs transition speed", calc="CALC-B2R3-STALL",
          output="Vtr_fwd_gate", unit="m/s", limit=("<=", "P:performance.transition_min_ms"),
          verifies=["R-TRANSITION"], parts=WING,
          how="F4 AIRSPEED_MIN 15.6 must be >= this; transition logs show airspeed >= 1.3 Vs")
kit.claim("CL-B2R3-VS-GATE-FWD-TURB", "Stall at 2.6 kg, forward CG, turbulent-LE section (XFOIL tripped)",
          calc="CALC-B2R3-STALL-TURB", output="Vs_trip", unit="m/s", parts=WING,
          how="Sensitivity (no limit): the value if the LE is rough (tape seam, bugs, rain). T-B2-STALL decides",
          note="informational; the design value is CL-B2R3-VS-GATE-FWD (free transition). Exceeds 12 m/s")
kit.claim("CL-B2R3-CLMAX-TRIP-RATIO", "Section clmax, tripped / free transition (XFOIL)", calc="CALC-B2R3-STALL-TURB",
          output="ratio_trip", unit="-", how="Re-run xfoil_tripped.py; T-B2-STALL with and without an LE trip strip")
kit.claim("CL-B2R3-CLMAX-SU2-RATIO", "Section clmax, SU2 SA (L2) / XFOIL free transition", calc="CALC-B2R3-STALL-TURB",
          output="ratio_su2", unit="-", how="Re-run cfd2d_section.py",
          note="not grid-converged (CL-B2R3-SU2-GCI-CLMAX): supports the tripped-XFOIL bracket, does not replace it")
kit.claim("CL-B2R3-CLMAX-SU2-TRIP", "Section clmax, SU2 SA (L2) / XFOIL tripped", calc="CALC-B2R3-STALL-TURB",
          output="su2_over_trip", unit="-", how="Like-for-like solver check (both fully turbulent); expected 0.9-1.1")
kit.claim("CL-B2R3-HINGE-VA", "Hinge moment per servo, 25 deg at VA", calc="CALC-B2R3-HINGE", output="H_VA_Nm",
          unit="N*m", parts=WING, how="T-B2-HINGE bench load: H / (0.5 x 0.0704 m) on the trailing edge")
kit.claim("CL-B2R3-HINGE-VD", "Hinge moment per servo, 8.3 deg at VD", calc="CALC-B2R3-HINGE", output="H_VD_Nm",
          unit="N*m", parts=WING, how="T-B2-HINGE")
kit.claim("CL-B2R3-SERVO-TORQUE-REQ", "Servo stall torque needed through the D6 linkage, 25 deg at VD",
          calc="CALC-B2R3-HINGE", output="T_servo_vdfull_kgfcm", unit="kgf*cm",
          limit=("<=", "P:mec.servo.stall_torque_6v_kgfcm"), verifies=["R-SERVO-TORQUE"], parts=["MEC-001"],
          how="1.5 x H(25 deg, VD 27.2 m/s) x CL-D6-TORQUE-FACTOR; T-B2-HINGE bench test at 6 V",
          note="R-SERVO-TORQUE as A2 wrote it (full travel at VD); the flight envelope (full travel to VA only) "
               "needs CL-B2R3-SERVO-TORQUE-ENV")
kit.claim("CL-B2R3-SERVO-TORQUE-ENV", "Servo stall torque needed through the D6 linkage, F4 envelope",
          calc="CALC-B2R3-HINGE", output="T_servo_kgfcm", unit="kgf*cm", limit=("<=", "P:mec.servo.stall_torque_6v_kgfcm"),
          parts=["MEC-001"], how="1.5 x max(H 25 deg at VA, H 8.3 deg at VD) x CL-D6-TORQUE-FACTOR")
kit.claim("CL-B2R3-SERVO-TORQUE-DIRECT", "Servo torque needed at a 1:1 linkage, 25 deg at VD", calc="CALC-B2R3-HINGE",
          output="T_direct_vdfull_kgfcm", unit="kgf*cm",
          how="For any linkage other than D6's; replaces CL-B2-SERVO-TORQUE-REQ (3.93 at 1.3 x cruise)")
kit.claim("CL-B2R3-HINGE-VD-FULL", "Hinge moment per servo, 25 deg at VD", calc="CALC-B2R3-HINGE",
          output="H_VD_full_Nm", unit="N*m", parts=WING, how="T-B2-HINGE")
kit.claim("CL-B2R3-HINGE-VISC-RATIO", "Hinge moment, SU2 viscous / XFOIL inviscid at -25 deg",
          calc="CALC-B2R3-HINGE", output="visc_ratio", unit="-", limit=("<=", 1.0),
          how="<= 1 confirms ASM-B2-HINGE-INVISCID (inviscid is the bound); bench test T-B2-HINGE")
kit.claim("CL-B2R3-XFOIL-PANEL-SPREAD", "XFOIL clmax spread, 160-400 panels", calc="CALC-B2R3-CONV",
          output="xfoil_spread", unit="-", how="Re-run verify_wing.py",
          note="clmax still rises with panels (1.246/1.256/1.263/1.268): not converged to 1 %, but the 220-panel "
               "value carried is the lower one (CL-B2R3-XFOIL-PANEL-CONS)")
kit.claim("CL-B2R3-XFOIL-PANEL-CONS", "XFOIL clmax, 400 panels / 220 used - 1", calc="CALC-B2R3-CONV",
          output="xfoil_cons", unit="-", limit=(">=", 0.0), how=">= 0: the value used is conservative (ASM-B2R3-CONV-RULE)")
kit.claim("CL-B2R3-AVL-LATTICE-SPREAD", "AVL trimmed CLmax spread, 4 lattices", calc="CALC-B2R3-CONV",
          output="avl_clmax_spread", unit="-", how="Re-run verify_wing.py",
          note="non-monotone (strip edges move relative to the elevon end); the 12x1 lattice used is below the finest")
kit.claim("CL-B2R3-AVL-LATTICE-CONS", "AVL CLmax, finest / used lattice - 1", calc="CALC-B2R3-CONV",
          output="avl_cons", unit="-", limit=(">=", 0.0), how=">= 0: the value used is conservative (ASM-B2R3-CONV-RULE)")
kit.claim("CL-B2R3-SU2-GCI-CH", "SU2 hinge-moment grid uncertainty (GCI fine)", calc="CALC-B2R3-CONV",
          output="gci_ch", unit="-", how="Re-run cfd2d_section.py",
          note="above ASM-B2R3-CFD-TOL (5 %): the SU2 hinge value is not a design value; only its bound "
               "(CL-B2R3-HINGE-VISC-RATIO) is used")
kit.claim("CL-B2R3-SU2-GCI-CL", "SU2 lift grid uncertainty (GCI fine)", calc="CALC-B2R3-CONV",
          output="gci_cl", unit="-", how="Re-run cfd2d_section.py",
          note="above ASM-B2R3-CFD-TOL (5 %): separated elevon, steady RANS does not settle")
kit.claim("CL-B2R3-SU2-GCI-CLMAX", "SU2 clean-section lift near clmax, grid uncertainty (GCI fine)",
          calc="CALC-B2R3-CONV", output="gci_clmax", unit="-",
          how="Re-run cfd2d_section.py (alpha 12 deg, Re 2.6e5, 3 levels)",
          note="above ASM-B2R3-CFD-TOL (5 %): post-stall steady RANS; SU2 clmax is not a design value")
kit.claim("CL-B2R3-ROOT-BM-LIMIT", "Wing root bending at n limit, 2.6 kg (AVL)", calc="CALC-B2R3-LOADS",
          output="M_root_limit", unit="N*m", parts=["WNG-002"], how="C1/C2 spar sizing; H1 spar proof load")
kit.claim("CL-B2R3-ROOT-BM-LIMIT-SCHRENK", "Root bending at n limit, Schrenk hand calc", calc="CALC-B2R3-LOADS",
          output="M_root_limit_schrenk", unit="N*m", parts=["WNG-002"], how="Conservative bound for C2")
kit.claim("CL-B2R3-SCHRENK-RATIO", "Root bending, Schrenk / AVL", calc="CALC-B2R3-LOADS", output="schrenk_ratio",
          unit="-", how="Hand check of the AVL loading")
kit.claim("CL-B2R3-CLA-HAND-RATIO", "Lift slope, AVL / Helmbold", calc="CALC-B2R3-CLA-HAND", output="ratio",
          unit="-", how="Expected 0.9-1.0 (rectangular, elevon gaps, fins)")

if __name__ == "__main__":
    kit.write()
