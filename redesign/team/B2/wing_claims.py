"""B2 wing aero claims for the proof chain (K09-L).

Run from the repo root after xfoil_wing.py -> avl_wing.py -> results_to_params.py:
    python -I redesign/team/B2/wing_claims.py
then python -I redesign/proofs/build_graph.py. Every calculation below is a pure function of its named inputs.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "params.json"])

# ---------------------------------------------------------------- sources and assumptions
kit.source("SRC-B2-XFOIL", "XFOIL 6.99 runs, team/B2/xfoil_wing.py", "web",
           url="https://web.mit.edu/drela/Public/web/xfoil/",
           where="team/B2/out/xfoil_results.json; panels 220 (160/300 convergence), Ncrit 9, Re 2.0-4.5e5; design Re follow wing.chord_m (c 0.32 m: stall 2.6e5, cruise 3.5e5, dive 4.5e5)",
           note="not yet compared with wind-tunnel data at this Re; flight stall test T-B2-STALL closes it")
kit.source("SRC-B2-AVL", "AVL 3.52 runs, team/B2/avl_wing.py", "web",
           url="https://web.mit.edu/drela/Public/web/avl/",
           where="team/B2/out/avl_results.json; 3 lattice levels; geometry from params.json (A1-R2: wing 1.15 x 0.32 m, half-fins x 0.045..0.32 m, 0.275 m chord, +/-0.19 m)",
           note="props-off wing + flat-plate fins, no pod; not yet compared with flight data")
kit.source("SRC-B2-S5010-COORD", "S5010 coordinates, UIUC airfoil database", "web",
           url="https://m-selig.ae.illinois.edu/ads/coord/s5010.dat", checked="2026-11-09",
           where="61 points; t/c 9.82 % from the file matches the published 9.8 %")
kit.source("SRC-B2-MH45-COORD", "MH 45 coordinates, UIUC airfoil database", "web",
           url="https://m-selig.ae.illinois.edu/ads/coord/mh45.dat", checked="2026-11-09",
           where="67 points; t/c 9.84 % from the file matches the published 9.85 %")

kit.assumption("ASM-B2-CLMAX-KD", "No net knock-down on CLmax",
               "Design CLmax = 1.0 x the critical-section CLmax built on the XFOIL clmax envelope",
               basis="XFOIL tends to over-predict clmax at Re 2-3e5 by a few per cent, while the critical-section method "
                     "under-predicts a low-AR rectangular wing (stall spreads before CL peaks) and the clmax envelope is "
                     "already the lower of Re 2.3e5 / 3.0e5; the biases offset. Replaced by the slow-flight stall T-B2-STALL",
               value=1.0, unit="-", status="UNVERIFIED")
kit.assumption("ASM-B2-DIVE-FACTOR", "Dive speed 1.3 x cruise",
               "Elevon hinge moments are sized at 1.3 x cruise speed with full 25 deg travel",
               basis="R-SERVO-TORQUE text (1.3 x cruise; 20.8 m/s at the 16 m/s cruise)", value=1.3, unit="-")
kit.assumption("ASM-B2-HINGE-INVISCID", "Inviscid hinge moment is the bound",
               "Design hinge moment = XFOIL inviscid HMOM, the larger of viscous and inviscid",
               basis="converged viscous XFOIL values are 70-80 % of inviscid at +10..+25 deg; viscous up-deflection "
                     "cases do not converge (separated), so the inviscid value is used for both directions")
kit.assumption("ASM-B2-MIN-COVER", "Foam over the spar >= 2 mm",
               "At least 2 mm of XPS above and below the spar tube at the spar station",
               basis="hot-wire kerf ~1 mm plus slot tolerance; thinner foam tears when the slot is cut (G2 confirms)",
               value=0.002, unit="m")

kit.assumption("ASM-B2-RE-TOL", "Stall polars valid within 10 % of their Re",
               "XFOIL clmax and cm used at the stall are taken from polars within 10 % of the actual stall Re",
               basis="S5010 clmax changes ~0.02 per 0.3e5 of Re in this band (Re 2.0-3.0e5 polars, xfoil_results.json)",
               value=0.10, unit="-")

G_KGF = 9.80665


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-B2-CLMAX", title="Trimmed CLmax, critical section",
          equation="CLmax_cs = min_i(clmax_i / (cl_i/CL)); CLmax_design = kd * CLmax_cs",
          inputs={"cl_ratio": "P:b2.avl.cs.cl_over_CL", "clmax_local": "P:b2.avl.cs.clmax_local",
                  "kd": "ASM-B2-CLMAX-KD"},
          assumes=["ASM-B2-CLMAX-KD"])
def clmax_trim(cl_ratio, clmax_local, kd):
    cs = min(cm / r for cm, r in zip(clmax_local, cl_ratio) if r > 0)
    return {"CLmax_cs": cs, "CLmax_design": kd * cs}


@kit.calc("CALC-B2-STALL", title="Stall and transition speed at the gate",
          equation="Vs = sqrt(2 m g / (rho b c CLmax)); Vtr = 1.3 Vs; Re_s = Vs c / nu",
          inputs={"m": "P:requirements.mtow_gate_kg", "g": "P:env.g_ms2", "rho": "P:env.rho_kgm3",
                  "b": "P:wing.span_m", "c": "P:wing.chord_m", "clmax": "CL-B2-CLMAX-DESIGN",
                  "k": "P:requirements.transition_factor", "re_x": "P:b2.xfoil.re_stall"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "b": "m", "c": "m"})
def stall(m, g, rho, b, c, clmax, k, re_x):
    vs = math.sqrt(2 * m * g / (rho * b * c * clmax))
    re_s = vs * c / 1.48e-5
    return {"Vs_ms": vs, "Vtr_ms": k * vs, "Re_stall": re_s, "Re_dev": abs(re_s / re_x - 1.0)}


@kit.calc("CALC-B2-STALL-FWD", title="Stall speed at the forward CG limit",
          equation="SM_fwd = SM_min + (x_aft - x_fwd)/c; CLmax_fwd = kd * interp(SM_fwd, CLmax(SM)); "
                   "Vs = sqrt(2 m g / (rho b c CLmax_fwd))",
          inputs={"tab": "P:b2.avl.clmax_vs_sm", "sm_min": "P:requirements.static_margin_min",
                  "xr": "P:cg.x_range_m", "kd": "ASM-B2-CLMAX-KD", "m": "P:requirements.mtow_gate_kg",
                  "g": "P:env.g_ms2", "rho": "P:env.rho_kgm3", "b": "P:wing.span_m", "c": "P:wing.chord_m",
                  "k": "P:requirements.transition_factor"},
          units={"xr": "m", "m": "kg", "g": "m/s2", "rho": "kg/m3", "b": "m", "c": "m"},
          assumes=["ASM-B2-CLMAX-KD"])
def stall_fwd(tab, sm_min, xr, kd, m, g, rho, b, c, k):
    sm = sm_min + (xr[1] - xr[0]) / c
    xs, ys = [r[0] for r in tab], [r[1] for r in tab]
    i = max(j for j in range(len(xs) - 1) if xs[j] <= sm or j == 0)
    cl = kd * (ys[i] + (ys[i + 1] - ys[i]) * (sm - xs[i]) / (xs[i + 1] - xs[i]))
    vs = math.sqrt(2 * m * g / (rho * b * c * cl))
    return {"SM_fwd": sm, "CLmax_fwd": cl, "Vs_fwd_ms": vs, "Vtr_fwd_ms": k * vs}


@kit.calc("CALC-B2-HINGE", title="Elevon hinge moment per servo",
          equation="M = C_h q c^2 (s_in + s_out), q = rho (f V)^2 / 2; T_req = SF M",
          inputs={"ch": "P:b2.xfoil.hinge_coef_max", "rho": "P:env.rho_kgm3", "v": "P:performance.cruise_ms",
                  "f": "ASM-B2-DIVE-FACTOR", "c": "P:wing.chord_m", "yin": "P:wing.elevon.inboard_y_m",
                  "yout": "P:wing.elevon.outboard_y_m", "sf": "ASM-A2-SERVO-TORQUE-FACTOR"},
          units={"rho": "kg/m3", "v": "m/s", "c": "m", "yin": "m", "yout": "m"},
          assumes=["ASM-B2-HINGE-INVISCID"])
def hinge(ch, rho, v, f, c, yin, yout, sf):
    q = 0.5 * rho * (f * v) ** 2
    span = (yin[1] - yin[0]) + (yout[1] - yout[0])
    m = ch * q * c * c * span
    return {"q_dive_Pa": q, "M_hinge_Nm": m, "T_req_Nm": sf * m, "T_req_kgfcm": sf * m / G_KGF * 100}


@kit.calc("CALC-B2-SPAR-COVER", title="Foam cover over the spar",
          equation="cover_up = zu c - (z + d/2); cover_lo = (z - d/2) - zl c; z_mid = (zu + zl) c / 2",
          inputs={"zu": "P:b2.section.upper_zc_at_spar", "zl": "P:b2.section.lower_zc_at_spar",
                  "c": "P:wing.chord_m", "d": "P:wing.spar.od_m", "z": "P:wing.spar.z_m"},
          units={"c": "m", "d": "m", "z": "m"})
def spar_cover(zu, zl, c, d, z):
    up = zu * c - (z + d / 2)
    lo = (z - d / 2) - zl * c
    zmid = (zu + zl) * c / 2
    return {"cover_up_m": up, "cover_lo_m": lo, "cover_min_m": min(up, lo), "z_mid_m": zmid,
            "cover_centred_m": ((zu - zl) * c - d) / 2}


@kit.calc("CALC-B2-WING-LOADS", title="Wing root bending and torsion per g",
          equation="M_root = (m g / 2) ybar_frac b/2; T_root = (m g / 2) t_root",
          inputs={"m": "P:requirements.mtow_gate_kg", "g": "P:env.g_ms2", "b": "P:wing.span_m",
                  "yb": "P:b2.avl.ybar_frac", "t": "P:b2.avl.torsion_root_m_per_N"},
          units={"m": "kg", "g": "m/s2", "b": "m", "t": "m"})
def wing_loads(m, g, b, yb, t):
    half = m * g / 2
    return {"M_root_1g_Nm": half * yb * b / 2, "T_root_1g_Nm": half * t, "ybar_m": yb * b / 2}


# ---------------------------------------------------------------- claims
WING = ["WNG-001", "WNG-002", "WNG-003"]
kit.claim("CL-B2-CLMAX-CS", "Trimmed CLmax, critical section", calc="CALC-B2-CLMAX", output="CLmax_cs", unit="-",
          parts=WING, how="Re-run avl_wing.py; compare with the twin / XPS slow-flight stall at known mass")
kit.claim("CL-B2-CLMAX-DESIGN", "Design trimmed CLmax", calc="CALC-B2-CLMAX", output="CLmax_design", unit="-",
          parts=WING, how="Slow-flight stall at the gate mass with airspeed logging (T-B2-STALL); "
                          "CLmax = 2 m g / (rho S Vs^2)")
kit.claim("CL-B2-STALL-GATE", "Stall speed at the gate, SM floor (B2)", calc="CALC-B2-STALL", output="Vs_ms", unit="m/s",
          limit=("<=", "P:requirements.stall_max_ms"), verifies=["R-STALL"], parts=WING,
          how="T-B2-STALL: FBWA slow flight, 1 kt/s deceleration, three runs, airspeed sensor calibrated")
kit.claim("CL-B2-TRANSITION-GATE", "1.3 Vs against cruise, SM floor (B2)", calc="CALC-B2-STALL", output="Vtr_ms", unit="m/s",
          limit=("<=", "P:performance.cruise_ms"), verifies=["R-TRANSITION"], parts=WING,
          how="Re-run with the cruise speed B1 sets (CR-B2-01); flight: transition logs show airspeed >= 1.3 Vs")
kit.claim("CL-B2-RE-STALL", "Reynolds number at stall", calc="CALC-B2-STALL", output="Re_stall", unit="-",
          how="Must stay within 10 % of the XFOIL stall polar Re (P:b2.xfoil.re_stall, which follows the chord); re-run xfoil_wing.py if not")
kit.claim("CL-B2-SM-FWD", "Static margin at the forward CG limit", calc="CALC-B2-STALL-FWD", output="SM_fwd",
          unit="-", how="B3's CG range width over the chord, added to the SM floor; B3 re-derives the range (D-17)")
kit.claim("CL-B2-CLMAX-FWD", "Trimmed CLmax at the forward CG limit", calc="CALC-B2-STALL-FWD",
          output="CLmax_fwd", unit="-", parts=WING,
          how="T-B2-STALL flown at the forward CG ballast as well as the aft")
kit.claim("CL-B2-STALL-GATE-FWD", "Stall speed at the gate, forward CG (B2)", calc="CALC-B2-STALL-FWD",
          output="Vs_fwd_ms", unit="m/s", limit=("<=", "P:requirements.stall_max_ms"),
          parts=WING, how="T-B2-STALL at the forward CG limit, 2.6 kg",
          note="R2 basis (CG on the chord plane, SM from the range width): superseded for R-STALL by "
               "CL-B2R3-VS-GATE-FWD (B2-R4, real CG height, team/B2/sim/stall_zcg.py)")
kit.claim("CL-B2-TRANSITION-GATE-FWD", "1.3 Vs against cruise, forward CG (B2)", calc="CALC-B2-STALL-FWD",
          output="Vtr_fwd_ms", unit="m/s", limit=("<=", "P:performance.cruise_ms"),
          parts=WING, how="Transition logs at the forward CG: airspeed >= 1.3 Vs before the wing carries the weight",
          note="R2 basis: superseded for R-TRANSITION by CL-B2R3-VTR-GATE-FWD (B2-R4, real CG height)")
kit.claim("CL-B2-RE-STALL-DEV", "Stall Re vs the XFOIL stall polars", calc="CALC-B2-STALL", output="Re_dev",
          unit="-", limit=("<=", "ASM-B2-RE-TOL"),
          how="|Re at Vs / Re of the stall polars - 1|; re-run xfoil_wing.py (Re follow the chord) if it fails")
kit.claim("CL-B2-HINGE-MOMENT", "Hinge moment per servo, dive", calc="CALC-B2-HINGE", output="M_hinge_Nm",
          unit="N*m", parts=WING,
          how="Bench: hang M / (0.5 x elevon chord) on the trailing edge of a linked panel pair at 25 deg")
kit.claim("CL-B2-SERVO-TORQUE-REQ", "Required servo stall torque", calc="CALC-B2-HINGE", output="T_req_kgfcm",
          unit="kgf*cm", parts=WING,
          how="D6 selects a servo with rated stall torque >= this at 5 V; T-B2-HINGE bench test")
kit.claim("CL-B2-SPAR-COVER", "Foam cover over spar, params z", calc="CALC-B2-SPAR-COVER", output="cover_min_m",
          unit="m", limit=(">=", "ASM-B2-MIN-COVER"), parts=["WNG-001", "WNG-002"],
          how="Measure foam above and below the slot on the first cut core (calipers)",
          note="At z = 0 the 22 mm tube breaks the lower skin; with params z = +6.6 mm (CR-B2-03) it passes; z_mid at c 0.32 is +7.0 mm (CR-B2-09)")
kit.claim("CL-B2-SPAR-Z-MID", "Spar centre on the camber line", calc="CALC-B2-SPAR-COVER", output="z_mid_m",
          unit="m", parts=["WNG-002"], how="Template check: slot centre midway between the skins at x = 0.08 m")
kit.claim("CL-B2-SPAR-COVER-CENTRED", "Foam cover, spar centred", calc="CALC-B2-SPAR-COVER",
          output="cover_centred_m", unit="m", limit=(">=", "ASM-B2-MIN-COVER"), parts=["WNG-001", "WNG-002"],
          how="Measure on the first cut core")
kit.claim("CL-B2-ROOT-BM-1G", "Wing root bending, 1 g", calc="CALC-B2-WING-LOADS", output="M_root_1g_Nm",
          unit="N*m", parts=["WNG-002"], how="C1 multiplies by n; spar proof load test (H1)")
kit.claim("CL-B2-ROOT-TORSION-1G", "Wing root torsion, 1 g", calc="CALC-B2-WING-LOADS", output="T_root_1g_Nm",
          unit="N*m", parts=["WNG-001", "WNG-002"], how="C1 multiplies by n; included in the spar proof test")
kit.claim("CL-B2-ELEVON-ETA", "Elevon effectiveness factor", calc="CALC-B2-SECTION", output="eta", unit="-",
          how="Replaces ASM-B3-FLAP-EFF / ASM-C1-ELEVON-EFF; flight: FBWA trim elevon vs AVL at two speeds")
kit.claim("CL-B2-DCM-VISC", "Viscous cm correction to AVL", calc="CALC-B2-SECTION", output="dcm", unit="-",
          how="Replaces ASM-B3-DCM-VISC; flight: trimmed elevon at known CG and speed (twin, XPS)")
kit.claim("CL-B2-CLA-3D", "Wing lift slope, AVL", calc="CALC-B2-SECTION", output="cla3d", unit="1/rad",
          how="For C1 gust loads; Helmbold check at AR 3.59: 3.70 /rad with 2 pi, 3.79 /rad with the XFOIL 6.61 /rad, vs AVL 3.48 /rad (rectangular, elevon gaps)")
kit.claim("CL-B2-CLMIN-2D", "Section negative clmax", calc="CALC-B2-SECTION", output="clmin", unit="-",
          how="For C1 (ASM-C1-CLMIN); XFOIL last converged point at the cruise Re, treat as magnitude 0.44 until flight")


@kit.calc("CALC-B2-SECTION", title="Section and elevon data (pass-through)",
          equation="values from the XFOIL/AVL runs, re-checked by results_to_params.py",
          inputs={"eta": "P:b2.xfoil.elevon_eta", "dcm": "P:b2.avl.dcm_visc", "cla3d": "P:b2.avl.cla_per_rad",
                  "clmin": "P:b2.xfoil.clmin_2d"}, units={"cla3d": "1/rad"})
def section_data(eta, dcm, cla3d, clmin):
    return {"eta": eta, "dcm": dcm, "cla3d": cla3d, "clmin": clmin}


kit.test("T-B2-STALL", "Slow-flight stall at the gate mass", verifies=["CL-B2-STALL-GATE", "CL-B2-CLMAX-DESIGN"],
         procedure="Twin first, then the XPS aircraft in FBWA at >= 50 m: ballast to 2.6 kg, CG at B3's value, "
                   "decelerate 0.5 m/s per s to the stall break three times; Vs = mean airspeed at the break")
kit.test("T-B2-HINGE", "Elevon servo bench load", verifies=["CL-B2-SERVO-TORQUE-REQ"],
         procedure="Wing on the bench, linked panel pair at 25 deg up and down: hang a weight giving "
                   "CL-B2-HINGE-MOMENT at the panel mid-chord; servo holds position, linkage does not slip")

if __name__ == "__main__":
    kit.write()
