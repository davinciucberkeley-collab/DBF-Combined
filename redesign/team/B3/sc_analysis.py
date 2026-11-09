"""B3 stability and control: proof-chain claims for the K09-L quad tailsitter.

Run (from the repo root, AVL 3.52 at C:/Users/dillo/tools/avl/avl352.exe; first run ~3 min, then cached):
    python -I redesign/team/B3/xfoil_elevon.py      # once: section inputs (writes team/B3/xfoil/summary.json)
    python -I redesign/team/B3/sc_analysis.py       # AVL + hand models -> claims.json, results/sc_results.json
    python -I redesign/proofs/build_graph.py

Every calculation is a pure function of params.json keys, other roles' claims and ASM-B3 assumptions. AVL runs are
cached in team/B3/avl/cache/ keyed by the generated input text, so build_graph.py re-runs them in milliseconds.
Model and methods: team/B3/S-AND-C.md. Library: avl_model.py (AVL), flight_models.py (hand models).
"""
import cmath
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
import proofkit as pk  # noqa: E402
import avl_model as AV  # noqa: E402
import flight_models as FM  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"
LAT = "fine"

# ---------------------------------------------------------------------------------------------- sources
kit.source("SRC-B3-AVL", "AVL 3.52 vortex-lattice code (Drela, Youngren)", "web",
           url="https://web.mit.edu/drela/Public/web/avl/", checked="2026-11-09",
           where="avl_doc.txt: geometry, CONTROL, ST and MODE output", note="installed at C:/Users/dillo/tools/avl")
kit.source("SRC-B3-XFOIL", "XFOIL 6.99 (Drela)", "web", url="https://web.mit.edu/drela/Public/web/xfoil/",
           checked="2026-11-09", where="GDES FLAP, viscous polars")
kit.source("SRC-B3-MH45-COORD", "MH 45 coordinates, UIUC airfoil database", "web",
           url="https://m-selig.ae.illinois.edu/ads/coord/mh45.dat", checked="2026-11-09",
           where="67 points; t/c 9.85 % recomputed from the file (team/B3/avl/mh45.dat)")
kit.source("SRC-B3-RIBNER", "Ribner, Propellers in yaw, NACA Report 820 (1945)", "paper",
           url="https://ntrs.nasa.gov/citations/19930091895", where="normal-force derivative of a propeller")
kit.source("SRC-B3-PERKINS", "Perkins & Hage, Airplane Performance, Stability and Control (1949)", "book",
           where="ch. 5: propeller normal force dCN/dalpha = 4.25 sigma_e/(1+2 sigma_e) sin(beta+8 deg) f(Tc)")
kit.source("SRC-B3-MIL8785C", "MIL-F-8785C Flying qualities of piloted airplanes (1980)", "standard",
           url="http://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-F/MIL-F-8785C_5295/",
           where="3.2.2.1.2 short-period damping >= 0.35 (Level 1, cat. B); 3.3.4 roll performance")
kit.source("SRC-B3-HOERNER", "Hoerner, Fluid-Dynamic Drag / Lift (1965/1985)", "book",
           where="flat plate normal force at 90 deg, CN ~1.17-1.2 for low aspect ratio")

# ---------------------------------------------------------------------------------------------- assumptions
_xs = json.loads((HERE / "xfoil" / "summary.json").read_text()) if (HERE / "xfoil" / "summary.json").exists() else {}
kit.assumption("ASM-B3-DCM-VISC", "Viscous cm shift of the MH 45",
               "Section cm (viscous, Re 3e5) minus thin-airfoil cm on the MH 45 camber line, added to AVL's Cm",
               basis="team/B3/xfoil/summary.json (XFOIL Re 3e5, Ncrit 9, cl 0.3-0.7): cm -0.0092 vs thin +0.0063. "
                     "Hepperle's published +0.0145 would give +0.008: B2 settles it; S-AND-C.md shows both",
               value=round(_xs.get("dcm_visc", -0.0155), 4), unit="-", status="UNVERIFIED",
               cites=["SRC-B3-XFOIL", "SRC-B3-MH45-COORD"])
kit.assumption("ASM-B3-FLAP-EFF", "Elevon effectiveness factor",
               "Real elevon lift/moment per degree = this factor x AVL (thin-airfoil) value, for up-deflections",
               basis="XFOIL plain flap at 0.78 c, Re 3e5: 0.69 (-5 deg) to 0.59 (-15 deg), mean 0.63; down 0.80-0.84",
               value=round(_xs.get("flap_eff_up_mean", 0.63), 3), unit="-", status="UNVERIFIED",
               cites=["SRC-B3-XFOIL"])
kit.assumption("ASM-B3-PROP-CNA", "Propeller normal-force slope",
               "dCN/dalpha of one 11x4.5MR prop, on its disk area and freestream q, lightly loaded",
               basis="Perkins & Hage with sigma_e 0.09 (2 blades, ~20 mm chord at 0.75 R), beta_0.75 = 9.8 deg, "
                     "f(Tc) ~1.1: 0.10 per rad. Uncertainty +/-50 %", value=0.10, unit="1/rad",
               status="UNVERIFIED", cites=["SRC-B3-PERKINS", "SRC-B3-RIBNER"])
kit.assumption("ASM-B3-UPWASH", "Upwash factor at the props", "1 + d(eps_u)/d(alpha) at the prop planes",
               basis="props 0.05-0.15 m ahead of the LE but 0.19 m off the wing plane; DATCOM upwash chart ~1.1-1.2",
               value=1.15, unit="-")
kit.assumption("ASM-B3-CD-CYL", "Cross-flow CD of tubes and motors", "CD of the 22 mm tubes and the motor cans "
               "normal to their axis", basis="circular cylinder, subcritical Re ~2e4: 1.0-1.2 (Hoerner)",
               value=1.1, unit="-", cites=["SRC-B3-HOERNER"])
kit.assumption("ASM-B3-POD-K", "Pod Munk factor", "Fraction of the slender-body destabilising moment the pod gives, "
               "sitting on the wing upper surface", basis="half-body on a wall ~0.5 (image); ESTIMATE",
               value=0.5, unit="-")
kit.assumption("ASM-B3-TRIM-BUDGET", "Elevon travel allowed for pitch trim",
               "At the trimmed CLmax the pitch-trim elevon may use at most this much of the 25 deg travel",
               basis="leaves 15 deg (60 %) for roll and gust correction; B3 choice", value=10.0, unit="deg")
kit.assumption("ASM-B3-PB2V-MIN", "Minimum roll helix angle", "pb/2V at full available differential, at the trimmed stall",
               basis="small-UAV practice from MIL-F-8785C class I roll times: pb/2V >= 0.07", value=0.07, unit="-",
               cites=["SRC-B3-MIL8785C"])
kit.assumption("ASM-B3-CNB-MIN", "Minimum directional stability", "Cn_beta of the whole aircraft in cruise, per rad",
               basis="positive weathercock stability with ~0.02 margin for the prop term uncertainty; B3 choice",
               value=0.02, unit="1/rad")
kit.assumption("ASM-B3-AUTH-RATIO", "Control power over disturbance", "Available control moment / disturbance moment, "
               "per axis", basis="control power at least twice the 5 m/s disturbance; B3 choice, common VTOL practice",
               value=2.0, unit="-")
kit.assumption("ASM-B3-CN90", "Flat-plate normal force at 90 deg", "CN of the wing broadside and the fins broadside",
               basis="Hoerner: 1.17 (AR 1-5); used 1.2", value=1.2, unit="-", cites=["SRC-B3-HOERNER"])
kit.assumption("ASM-B3-XCP-HOVER", "Wing centre of pressure, wind on the face", "x_cp/c of the wing normal force at "
               "70-90 deg incidence", basis="flat plate 0.40-0.50 c; 0.45 used", value=0.45, unit="-",
               cites=["SRC-B3-HOERNER"])
kit.assumption("ASM-B3-GUST-ASYM", "Spanwise gust asymmetry in hover", "Fraction of the wing normal force acting as a "
               "left-right difference at b/4", basis="ESTIMATE for a 1.15 m span in turbulent 5 m/s wind", value=0.10, unit="-")
kit.assumption("ASM-B3-CD0", "Wing profile drag for the transition model", "CD0 of the wing + fins + pod",
               basis="B1 owns the drag build-up; 0.020 at Re 3e5 (MH 45 cd ~0.008, fins, pod, tubes)", value=0.020,
               unit="-")
kit.assumption("ASM-B3-TRANS-USE-MAX", "Pitch differential allowed in transition",
               "Fraction of the motors' pitch differential the quasi-steady transition may use",
               basis="keeps 40 % for pitch rate, gusts and roll/yaw mixing; B3 choice", value=0.6, unit="-")
kit.assumption("ASM-B3-ELEVON-TRANS", "Elevon pitch travel in transition",
               "Elevon deflection available for pitch during the transition", basis="25 deg travel less 10 deg kept for "
               "roll; B3 choice", value=15.0, unit="deg")
kit.assumption("ASM-B3-ELEVON-POST", "Elevon effectiveness at 90 deg",
               "Elevon effectiveness behind the fully stalled wing relative to attached flow (linear in alpha between)",
               basis="flap behind separated flow keeps ~20-30 % (Hoerner, Fluid-Dynamic Lift ch. 5); ESTIMATE",
               value=0.25, unit="-", status="UNVERIFIED", cites=["SRC-B3-HOERNER"])
kit.assumption("ASM-B3-BETA-DIST", "Sideslip disturbance for yaw authority", "Sideslip the yaw control must hold "
               "against", basis="5 m/s crosswind gust at 15 m/s ~ 18 deg; 10 deg used for a sustained case",
               value=10.0, unit="deg")
kit.assumption("ASM-B3-SPLIT-MAX", "Allowed hover pitch-trim split", "Upper/lower pair thrust ratio for hover pitch trim",
               basis="split s uses (s-1)/2 of the pitch differential; 1.25 uses 12.5 %, replaces A3's 1.10 placeholder",
               value=1.25, unit="-")
kit.assumption("ASM-B3-ZETA-SP-MIN", "Short-period damping minimum", "Level 1 short-period damping ratio",
               basis="MIL-F-8785C cat. B Level 1", value=0.30, unit="-", cites=["SRC-B3-MIL8785C"])

GEO = {"b": P + "wing.span_m", "c": P + "wing.chord_m", "ef": P + "wing.elevon.chord_frac",
       "yin": P + "wing.elevon.inboard_y_m", "yout": P + "wing.elevon.outboard_y_m", "fy": P + "fins.y_m",
       "fh": P + "fins.half_height_m", "fle": P + "fins.le_x_m", "fte": P + "fins.te_x_m"}
GEOU = {"b": "m", "c": "m", "yin": "m", "yout": "m", "fy": "m", "fh": "m", "fle": "m", "fte": "m"}


def _g(b, c, ef, yin, yout, fy, fh, fle, fte, xref, zref):
    return AV.geometry_from(b, c, ef, yin, yout, fy, fh, fle, fte, xref, zref)


# ---------------------------------------------------------------------------------------------- AVL runs
@kit.calc("CALC-B3-AVL-CONV", title="AVL lattice convergence", inputs={**GEO, "xref": P + "cg.x_target_m",
          "zref": P + "cg.z_target_m"}, units={**GEOU, "xref": "m", "zref": "m"}, cites=["SRC-B3-AVL"],
          equation="Xnp, Cm_de at alpha 4 deg on coarse / medium / fine lattices; d = |fine - medium|")
def avl_convergence(b, c, ef, yin, yout, fy, fh, fle, fte, xref, zref):
    g = _g(b, c, ef, yin, yout, fy, fh, fle, fte, xref, zref)
    r = {k: AV.derivatives(g, 4.0, k) for k in ("coarse", "medium", "fine")}
    return {"xnp_coarse": r["coarse"]["Xnp"], "xnp_medium": r["medium"]["Xnp"], "xnp_fine": r["fine"]["Xnp"],
            "dxnp_frac_c": abs(r["fine"]["Xnp"] - r["medium"]["Xnp"]) / c,
            "dcmd_rel": abs(r["fine"]["Cmd01"] / r["medium"]["Cmd01"] - 1),
            "dcnb_abs": abs(r["fine"]["Cnb"] - r["medium"]["Cnb"])}


@kit.calc("CALC-B3-AVL-LONG", title="AVL longitudinal derivatives", inputs={**GEO, "xref": P + "cg.x_target_m",
          "zref": P + "cg.z_target_m"}, units={**GEOU, "xref": "m", "zref": "m"}, cites=["SRC-B3-AVL"],
          equation="AVL fine lattice, alpha 4 deg, controls 0: CLa, Xnp, Cm_np = Cm_ref + CL (Xnp - xref)/c, "
                   "control derivatives per deg (thin-airfoil)")
def avl_long(b, c, ef, yin, yout, fy, fh, fle, fte, xref, zref):
    d = AV.derivatives(_g(b, c, ef, yin, yout, fy, fh, fle, fte, xref, zref), 4.0, LAT)
    return {"CLa": d["CLa"], "xnp_aero": d["Xnp"], "alpha0_deg": 4.0 - d["CLtot"] / (d["CLa"] * math.pi / 180),
            "cm_np_thin": d["Cmtot"] + d["CLtot"] * (d["Xnp"] - xref) / c,
            "CLd": d["CLd01"], "Cmd_ref": d["Cmd01"], "Cld": d["Cld02"], "Cnd": d["Cnd02"], "Clp": d["Clp"],
            "Cmq": d["Cmq"], "CLq": d["CLq"], "e": d["e"], "xref": xref}


kit.claim("CL-B3-AVL-CONV", "AVL neutral point grid change", calc="CALC-B3-AVL-CONV", output="dxnp_frac_c", unit="-",
          limit=("<=", 0.005), how="Re-run sc_analysis.py with the cache deleted; compare coarse/medium/fine in "
                                  "results/sc_results.json.")
kit.claim("CL-B3-XNP-AERO", "Neutral point, wing and fins", calc="CALC-B3-AVL-LONG", output="xnp_aero", unit="m",
          how="AVL fine lattice; cross-check: flat plate AR 3.8 with end-plate fins, NP ~0.23 c.")
kit.claim("CL-B3-CLA", "Lift-curve slope, AVL", calc="CALC-B3-AVL-LONG", output="CLa", unit="1/rad",
          how="Twin glide: alpha from the FC vs CL from airspeed and mass.")


# ---------------------------------------------------------------------------------------------- neutral point
@kit.calc("CALC-B3-NP", title="Neutral point with props and pod",
          assumes=["ASM-B3-PROP-CNA", "ASM-B3-UPWASH", "ASM-B3-POD-K"], cites=["SRC-B3-RIBNER"],
          inputs={"xnp_a": "CL-B3-XNP-AERO", "CLa": "CL-B3-CLA", "n": P + "propulsion.n_motors",
                  "D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "S": "CL-A1-WING-AREA", "c": P + "wing.chord_m", "b": P + "wing.span_m",
                  "cna": "ASM-B3-PROP-CNA", "up": "ASM-B3-UPWASH", "pod": P + "pod.size_m", "kpod": "ASM-B3-POD-K"},
          units={"D": "m", "x_prop": "m", "S": "m2", "c": "m", "b": "m", "pod": "m"},
          equation="Cma about Xnp_aero: dCm_p = n cna A/S up (Xnp_a - x_p)/c ; dCm_pod = 2 k V/(S c), V = 0.6 LWH ; "
                   "Xnp = Xnp_a - (dCm_p + dCm_pod)/(CLa + dCLa_p) c")
def neutral_point(xnp_a, CLa, n, D, x_prop, S, c, b, cna, up, pod, kpod):
    p = FM.prop_terms(n, D, x_prop, xnp_a, S, c, b, cna, up)
    vol = 0.6 * pod[0] * pod[1] * pod[2]
    dpod = FM.pod_dCma(vol, S, c, kpod)
    xnp = xnp_a - (p["dCma"] + dpod) / (CLa + p["dCLa"]) * c
    return {"xnp": xnp, "dx_props": -p["dCma"] / (CLa + p["dCLa"]) * c, "dx_pod": -dpod / (CLa + p["dCLa"]) * c,
            "xnp_frac": xnp / c}


kit.claim("CL-B3-XNP", "Neutral point, whole aircraft", calc="CALC-B3-NP", output="xnp", unit="m",
          how="Twin and aircraft: elevon trim vs CG at two pack positions in FBWA glides; "
                                 "Xnp where the trim-vs-CL slope is zero (MIT 16.06 method).")


# ---------------------------------------------------------------------------------------------- CG limits
TRIM_IN = {"cm_np_thin": "CL-B3-CM-NP-THIN", "dcm": "ASM-B3-DCM-VISC", "eff": "ASM-B3-FLAP-EFF",
           "CLd": "CL-B3-CLD", "Cmd_ref": "CL-B3-CMD", "xref": P + "cg.x_target_m", "c": P + "wing.chord_m"}
kit.claim("CL-B3-CM-NP-THIN", "Cm about the NP, AVL thin", calc="CALC-B3-AVL-LONG", output="cm_np_thin", unit="-",
          how="Follows from AVL; the viscous shift ASM-B3-DCM-VISC is added in each trim calculation.")
kit.claim("CL-B3-CLD", "Elevon lift per degree, AVL", calc="CALC-B3-AVL-LONG", output="CLd", unit="1/deg",
          how="Twin: CL change per degree of trim in level glide.")
kit.claim("CL-B3-CMD", "Elevon pitch moment per degree, AVL", calc="CALC-B3-AVL-LONG", output="Cmd_ref", unit="1/deg",
          how="Twin: pitch-rate response to an elevon step (FC log), fitted.")


def _clmax_trim(sm, cm_np_thin, dcm, eff, CLd, Cmd_ref, xref, c, xnp, clmax):
    xcg = xnp - sm * c
    return FM.trimmed_clmax(clmax, cm_np_thin + dcm, sm, CLd * eff, Cmd_ref * eff, xcg, xref, c)


@kit.calc("CALC-B3-CG-LIMITS", title="CG limits from stability and trim",
          assumes=["ASM-B3-TRIM-BUDGET", "ASM-B3-DCM-VISC", "ASM-B3-FLAP-EFF", "ASM-A1-CLMAX"],
          inputs={**TRIM_IN, "xnp": "CL-B3-XNP", "sm_min": P + "requirements.static_margin_min",
                  "clmax": "ASM-A1-CLMAX", "budget": "ASM-B3-TRIM-BUDGET"},
          units={"xref": "m", "c": "m", "xnp": "m", "budget": "deg"},
          equation="aft: x = Xnp - SMmin c ; forward: SM where the elevon trim at the trimmed CLmax reaches the trim "
                   "budget (Cm_ac - CL SM + Cmd delta = 0, CL = CLmax + CLd delta) ; target = mid-range")
def cg_limits(cm_np_thin, dcm, eff, CLd, Cmd_ref, xref, c, xnp, sm_min, clmax, budget):
    lo, hi = sm_min, 0.40
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        _, d = _clmax_trim(mid, cm_np_thin, dcm, eff, CLd, Cmd_ref, xref, c, xnp, clmax)
        if -d < budget:
            lo = mid
        else:
            hi = mid
    sm_fwd = 0.5 * (lo + hi)
    x_aft, x_fwd = xnp - sm_min * c, xnp - sm_fwd * c
    x_t = 0.5 * (x_aft + x_fwd)
    return {"x_aft": x_aft, "x_fwd": x_fwd, "sm_fwd": sm_fwd, "x_target": x_t, "sm_target": (xnp - x_t) / c,
            "width": x_aft - x_fwd, "x_aft_frac": x_aft / c, "x_fwd_frac": x_fwd / c}


kit.claim("CL-B3-CG-AFT", "Aft CG limit", calc="CALC-B3-CG-LIMITS", output="x_aft", unit="m",
          how="H1 CG balance on the two fin-root marks; never fly with the balance point aft of this line.")
kit.claim("CL-B3-CG-FWD", "Forward CG limit", calc="CALC-B3-CG-LIMITS", output="x_fwd", unit="m",
          how="H1 CG balance; twin: full-up trim margin at slow flight (elevon <= 10 deg up at the stall warning).")
kit.claim("CL-B3-CG-TARGET", "CG design target", calc="CALC-B3-CG-LIMITS", output="x_target", unit="m",
          how="A3 roll-up and H1 balance with the pack centred in its slide.")
kit.claim("CL-B3-SM-TARGET", "Static margin at the CG target", calc="CALC-B3-CG-LIMITS", output="sm_target", unit="-",
          limit=(">=", P + "requirements.static_margin_min"), verifies=["R-STATIC-MARGIN"],
          assumes=["ASM-B3-PROP-CNA"], how="Twin and aircraft: elevon-trim-vs-CL slope at two CG positions (FBWA glides).")


@kit.calc("CALC-B3-CG-CHECK", title="Current CG against the B3 range",
          inputs={"cg_frac": "CL-A3-CG-X", "c": P + "wing.chord_m", "x_fwd": "CL-B3-CG-FWD", "x_aft": "CL-B3-CG-AFT",
                  "x_t": "CL-B3-CG-TARGET"}, units={"c": "m", "x_fwd": "m", "x_aft": "m", "x_t": "m"},
          equation="x_now = cg_frac c ; margin = x_now - x_fwd ; move to target = x_t - x_now")
def cg_check(cg_frac, c, x_fwd, x_aft, x_t):
    x = cg_frac * c
    return {"x_now": x, "margin_fwd": x - x_fwd, "margin_aft": x_aft - x, "to_target": x_t - x}


kit.claim("CL-B3-CG-NOW-FWD", "Current CG behind the forward limit", calc="CALC-B3-CG-CHECK", output="margin_fwd",
          unit="m", limit=(">=", 0.0), how="Re-run after A3 updates the roll-up; H1 balance on the built aircraft.")


# ---------------------------------------------------------------------------------------------- trimmed stall
@kit.calc("CALC-B3-STALL-TRIM", title="Trimmed stall and transition speed at the gate",
          assumes=["ASM-B3-DCM-VISC", "ASM-B3-FLAP-EFF", "ASM-A1-CLMAX"],
          inputs={**TRIM_IN, "xnp": "CL-B3-XNP", "clmax": "ASM-A1-CLMAX", "x_t": "CL-B3-CG-TARGET",
                  "x_aft": "CL-B3-CG-AFT", "x_fwd": "CL-B3-CG-FWD", "m": P + "requirements.mtow_gate_kg",
                  "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "S": "CL-A1-WING-AREA",
                  "k": P + "requirements.transition_factor"},
          units={"xref": "m", "c": "m", "xnp": "m", "x_t": "m", "x_aft": "m", "x_fwd": "m", "m": "kg",
                 "g": "m/s2", "rho": "kg/m3", "S": "m2"},
          equation="CLmax_t = CLmax + CLd eff delta, delta from Cm = 0 ; Vs = sqrt(2 m g / (rho S CLmax_t)) ; Vt = k Vs")
def stall_trim(cm_np_thin, dcm, eff, CLd, Cmd_ref, xref, c, xnp, clmax, x_t, x_aft, x_fwd, m, g, rho, S, k):
    out = {}
    for tag, x in (("target", x_t), ("aft", x_aft), ("fwd", x_fwd)):
        sm = (xnp - x) / c
        CL, d = _clmax_trim(sm, cm_np_thin, dcm, eff, CLd, Cmd_ref, xref, c, xnp, clmax)
        out[f"clmax_{tag}"], out[f"delta_{tag}"] = CL, d
        out[f"vs_{tag}"] = FM.stall_speed(m, g, rho, S, CL)
    out["vt_target"] = k * out["vs_target"]
    out["vs_untrimmed"] = FM.stall_speed(m, g, rho, S, clmax)
    return out


kit.claim("CL-B3-VS-TRIM", "Trimmed stall speed at the gate, CG target", calc="CALC-B3-STALL-TRIM",
          output="vs_target", unit="m/s", limit=("<=", P + "requirements.stall_max_ms"), verifies=["R-STALL"],
          assumes=["ASM-A1-CLMAX", "ASM-B3-DCM-VISC"],
          how="Twin, then aircraft at 2.6 kg: FBWA slow-flight to the stall break with airspeed logging, CG on target.")
kit.claim("CL-B3-VT-TRIM", "Transition speed from the trimmed stall", calc="CALC-B3-STALL-TRIM", output="vt_target",
          unit="m/s", limit=("<=", P + "performance.cruise_ms"), verifies=["R-TRANSITION"],
          how="Set ARSPD_FBW_MIN >= this; flight log of the first transition (H2).")


# ---------------------------------------------------------------------------------------------- trim sweep
@kit.calc("CALC-B3-TRIM-SWEEP", title="Trim across speeds (target CG)",
          assumes=["ASM-B3-DCM-VISC", "ASM-B3-FLAP-EFF"],
          inputs={**TRIM_IN, "xnp": "CL-B3-XNP", "x_t": "CL-B3-CG-TARGET", "x_aft": "CL-B3-CG-AFT",
                  "x_fwd": "CL-B3-CG-FWD", "CLa": "CL-B3-CLA", "a0": "CL-B3-ALPHA0", "vs": "CL-B3-VS-TRIM",
                  "m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "S": "CL-A1-WING-AREA", "vc": P + "performance.cruise_ms"},
          units={"xref": "m", "c": "m", "xnp": "m", "x_t": "m", "x_aft": "m", "x_fwd": "m", "m": "kg", "g": "m/s2",
                 "rho": "kg/m3", "S": "m2", "vs": "m/s", "vc": "m/s"},
          equation="CL = 2 m g/(rho V^2 S) ; delta = (CL SM - Cm_ac)/Cmd_eff ; alpha = alpha0 + (CL - CLd_eff delta)/CLa")
def trim_sweep(cm_np_thin, dcm, eff, CLd, Cmd_ref, xref, c, xnp, x_t, x_aft, x_fwd, CLa, a0, vs, m, g, rho, S, vc):
    cm_ac = cm_np_thin + dcm
    speeds = [round(vs, 2)] + [v for v in (13.0, 14.0, 15.0, 16.0, 18.0, 20.0, 22.0, 25.0) if v > vs]
    rows = {}
    for tag, x in (("fwd", x_fwd), ("target", x_t), ("aft", x_aft)):
        sm = (xnp - x) / c
        cmd = (Cmd_ref + CLd * (x - xref) / c) * eff
        tab = []
        for V in speeds:
            CL = 2 * m * g / (rho * V * V * S)
            d = (CL * sm - cm_ac) / cmd
            a = a0 + (CL - CLd * eff * d) / (CLa * math.pi / 180)
            tab.append([V, round(CL, 4), round(a, 2), round(d, 2)])
        rows[tag] = tab
    cruise = [r for r in rows["target"] if abs(r[0] - vc) < 1e-6][0]
    worst = min(r[3] for t in rows.values() for r in t)
    return {"table": rows, "delta_cruise": cruise[3], "alpha_cruise": cruise[2], "delta_worst": worst}


kit.claim("CL-B3-ALPHA0", "Zero-lift angle, AVL", calc="CALC-B3-AVL-LONG", output="alpha0_deg", unit="deg",
          how="Follows from AVL with the MH 45 camber line.")
kit.claim("CL-B3-ELEVON-TRIM-CRUISE", "Elevon trim at 15 m/s, CG target", calc="CALC-B3-TRIM-SWEEP",
          output="delta_cruise", unit="deg", how="FBWA level flight at 15 m/s: servo output vs neutral (FC log).")
kit.claim("CL-B3-ALPHA-CRUISE", "Body angle at 15 m/s", calc="CALC-B3-TRIM-SWEEP", output="alpha_cruise", unit="deg",
          how="FC pitch angle in level flight at 15 m/s (no wind).")


# ---------------------------------------------------------------------------------------------- roll
@kit.calc("CALC-B3-ROLL", title="Roll authority at the trimmed stall", assumes=["ASM-B3-FLAP-EFF"],
          inputs={"Cld": "CL-B3-CLDA", "Clp": "CL-B3-CLP", "eff": "ASM-B3-FLAP-EFF",
                  "travel": P + "wing.elevon.deflection_deg", "budget": "ASM-B3-TRIM-BUDGET", "vs": "CL-B3-VS-TRIM",
                  "b": P + "wing.span_m", "S": "CL-A1-WING-AREA", "rho": P + "env.rho_kgm3", "Ixx": "CL-A3-IXX",
                  "m_basic": "CL-A3-MASS-BASIC", "m": P + "requirements.mtow_gate_kg"},
          units={"travel": "deg", "budget": "deg", "vs": "m/s", "b": "m", "S": "m2", "rho": "kg/m3", "Ixx": "kg m2",
                 "m_basic": "kg", "m": "kg"},
          equation="da = travel - budget ; pb/2V = Cld eff da / |Clp| ; tau = Ixx / (|Clp| q S b^2 / 2V) ; "
                   "t60 from first-order roll response")
def roll_authority(Cld, Clp, eff, travel, budget, vs, b, S, rho, Ixx, m_basic, m):
    da = travel[1] - budget
    pb2v = abs(Cld) * eff * da / abs(Clp)
    V = vs
    p = pb2v * 2 * V / b
    q = 0.5 * rho * V * V
    Lp = abs(Clp) * q * S * b * b / (2 * V)
    tau = Ixx * m / m_basic / Lp
    # bank angle phi(t) = p (t - tau (1 - exp(-t/tau)))
    t, phi = 0.0, 0.0
    while phi < math.radians(60) and t < 10:
        t += 0.001
        phi = p * (t - tau * (1 - math.exp(-t / tau)))
    return {"da_deg": da, "pb2v": pb2v, "p_degs": math.degrees(p), "tau_s": tau, "t60_s": t}


kit.claim("CL-B3-CLDA", "Elevon roll moment per degree, AVL", calc="CALC-B3-AVL-LONG", output="Cld", unit="1/deg",
          how="Twin: roll-rate response to a differential elevon step.")
kit.claim("CL-B3-CLP", "Roll damping, AVL", calc="CALC-B3-AVL-LONG", output="Clp", unit="-",
          how="Twin: roll-rate decay after a step (time constant).")
kit.claim("CL-B3-ROLL-PB2V", "Roll helix angle at the trimmed stall", calc="CALC-B3-ROLL", output="pb2v", unit="-",
          limit=(">=", "ASM-B3-PB2V-MIN"),
          how="Twin at 1.1 Vs: full-stick roll, FC roll rate; pb/2V = p b / 2V.")
kit.claim("CL-B3-ROLL-T60", "Time to 60 deg bank at the stall", calc="CALC-B3-ROLL", output="t60_s", unit="s",
          limit=("<=", 1.3), how="Twin roll test, FC log.")


# ---------------------------------------------------------------------------------------------- elevon size
@kit.calc("CALC-B3-ELEVON-AREA", title="Elevon area fraction, upper bound", inputs={"S": "CL-A1-WING-AREA",
          "f": P + "wing.elevon.chord_frac", "yin": P + "wing.elevon.inboard_y_m",
          "yout": P + "wing.elevon.outboard_y_m", "c": P + "wing.chord_m"},
          units={"S": "m2", "yin": "m", "yout": "m", "c": "m"}, equation="A = 2 (span_in + span_out) f c ; frac = A/S",
          output="frac")
def elevon_area(S, f, yin, yout, c):
    return 2 * ((yin[1] - yin[0]) + (yout[1] - yout[0])) * f * c / S


kit.claim("CL-B3-ELEVON-FRAC-MAX", "Elevon area within the upper bound", calc="CALC-B3-ELEVON-AREA", output="frac",
          unit="-", limit=("<=", 0.25), verifies=["R-ELEVON-AREA"],
          how="Measure the cut panels; freeze after the twin's trim and roll tests.")


# ---------------------------------------------------------------------------------------------- lateral-directional
LATIN = {**GEO, "x_t": "CL-B3-CG-TARGET", "zref": P + "cg.z_target_m", "n": P + "propulsion.n_motors",
         "D": P + "propulsion.prop_diameter_m", "dx_prop": P + "propulsion.stations.x_prop_plane_m",
         "x_tube": P + "fins.tube.x_m", "tube_od": P + "fins.tube.od_m", "tube_l": P + "fins.tube.length_m",
         "mot_d": P + "propulsion.motor_diameter_m", "mot_l": P + "propulsion.motor_length_m",
         "x_mount": P + "propulsion.stations.x_mount_m", "cna": "ASM-B3-PROP-CNA", "cd": "ASM-B3-CD-CYL",
         "S": "CL-A1-WING-AREA"}
LATU = {**GEOU, "x_t": "m", "zref": "m", "D": "m", "dx_prop": "m", "x_tube": "m", "tube_od": "m", "tube_l": "m",
        "mot_d": "m", "mot_l": "m", "x_mount": "m", "S": "m2"}


def lat_terms(b, c, ef, yin, yout, fy, fh, fle, fte, x_t, zref, n, D, dx_prop, x_tube, tube_od, tube_l, mot_d,
              mot_l, x_mount, cna, cd, S):
    d = AV.derivatives(_g(b, c, ef, yin, yout, fy, fh, fle, fte, x_t, zref), 4.0, LAT)
    p = FM.prop_terms(n, D, dx_prop, x_t, S, c, b, cna, 1.0)
    items = [(2 * cd * tube_od * tube_l, x_tube), (n * cd * mot_d * mot_l, x_mount - 0.011 - mot_l / 2)]
    dt = FM.drag_items_dCnb(items, x_t, S, b)
    return d, p, dt


@kit.calc("CALC-B3-LATDIR", title="Directional and lateral stability, cruise", inputs=LATIN, units=LATU,
          assumes=["ASM-B3-PROP-CNA", "ASM-B3-CD-CYL"], cites=["SRC-B3-AVL", "SRC-B3-RIBNER"],
          equation="Cnb = Cnb_AVL(wing+fins, at CG target) + Cnb_props (Ribner) + Cnb_tubes/motors (drag rotation)")
def latdir(**kw):
    d, p, dt = lat_terms(**kw)
    return {"Cnb_avl": d["Cnb"], "Cnb_props": p["dCnb"], "Cnb_tubes": dt, "Cnb": d["Cnb"] + p["dCnb"] + dt,
            "Clb": d["Clb"], "CYb": d["CYb"] + p["dCYb"], "Cnr": d["Cnr"], "Clr": d["Clr"], "Cnp": d["Cnp"],
            "CYp": d["CYp"], "CYr": d["CYr"], "Clp": d["Clp"], "Cnda": d["Cnd02"], "Cma": d["Cma"],
            "Cmq": d["Cmq"], "CLa": d["CLa"]}


kit.claim("CL-B3-CNB", "Directional stability Cn_beta, cruise", calc="CALC-B3-LATDIR", output="Cnb", unit="1/rad",
          limit=(">=", "ASM-B3-CNB-MIN"), assumes=["ASM-B3-PROP-CNA"],
          how="Twin in FBWA with yaw assist off: rudder-free yaw doublet (differential thrust pulse); heading must "
              "return. Wind-tunnel-free check: hang the airframe on a vertical pivot at the CG in a car-top run.")


# ---------------------------------------------------------------------------------------------- modes
def _poly_roots(coef):
    """Roots of a monic-normalised polynomial (Durand-Kerner)."""
    a = [x / coef[0] for x in coef]
    n = len(a) - 1
    roots = [complex(0.4, 0.9) ** k for k in range(n)]
    for _ in range(500):
        new = []
        for i, r in enumerate(roots):
            num = sum(a[k] * r ** (n - k) for k in range(n + 1))
            den = 1
            for j, s in enumerate(roots):
                if j != i:
                    den *= (r - s)
            new.append(r - num / den)
        roots = new
    return roots


def _charpoly4(A):
    """Faddeev-LeVerrier: characteristic polynomial [1, c1, ..., c4] of a 4x4 matrix."""
    n = len(A)
    M = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    coef = [1.0]
    for k in range(1, n + 1):
        AM = [[sum(A[i][l] * M[l][j] for l in range(n)) for j in range(n)] for i in range(n)]
        ck = -sum(AM[i][i] for i in range(n)) / k
        coef.append(ck)
        M = [[AM[i][j] + (ck if i == j else 0.0) for j in range(n)] for i in range(n)]
    return coef


def _eig4(A):
    return sorted(_poly_roots(_charpoly4(A)), key=lambda z: (abs(z), z.imag))


@kit.calc("CALC-B3-MODES", title="Rigid-body modes at 15 m/s (linear, props included)",
          assumes=["ASM-B3-PROP-CNA", "ASM-B3-CD0"],
          inputs={**LATIN, "xnp": "CL-B3-XNP",
                  "m": P + "requirements.mtow_gate_kg", "m_basic": "CL-A3-MASS-BASIC", "Ixx": "CL-A3-IXX",
                  "Iyy": "CL-A3-IYY", "Izz": "CL-A3-IZZ", "V": P + "performance.cruise_ms", "rho": P + "env.rho_kgm3",
                  "g": P + "env.g_ms2", "cd0": "ASM-B3-CD0", "e": P + "wing.oswald_e"},
          units={**LATU, "xnp": "m", "m": "kg", "m_basic": "kg", "Ixx": "kg m2", "Iyy": "kg m2", "Izz": "kg m2",
                 "V": "m/s", "rho": "kg/m3", "g": "m/s2"},
          equation="Etkin small-perturbation 4x4 longitudinal (u,w,q,theta) and lateral (v,p,r,phi) state matrices "
                   "from the AVL derivatives; Cma = -CLa SM (props included); eigenvalues by Faddeev-LeVerrier")
def modes(xnp, m, m_basic, Ixx, Iyy, Izz, V, rho, g, cd0, e, **geo):
    lat = latdir(**geo)
    Cnb, x_t, S, c, b = lat["Cnb"], geo["x_t"], geo["S"], geo["c"], geo["b"]
    k = m / m_basic
    Ixx, Iyy, Izz = Ixx * k, Iyy * k, Izz * k
    q = 0.5 * rho * V * V
    CL = m * g / (q * S)
    AR = b * b / S
    CD = cd0 + CL * CL / (math.pi * e * AR)
    CLa = lat["CLa"]
    Cma = -CLa * (xnp - x_t) / c
    Cmq = lat["Cmq"]
    U = V
    qS = q * S
    Xu, Xw = -2 * CD * qS / (m * U), (CL - 2 * CL * CLa / (math.pi * e * AR)) * qS / (m * U)
    Zu, Zw = -2 * CL * qS / (m * U), -(CLa + CD) * qS / (m * U)
    Mw, Mq = Cma * qS * c / (Iyy * U), Cmq * qS * c * c / (2 * U * Iyy)
    Alon = [[Xu, Xw, 0, -g], [Zu, Zw, U, 0], [0, Mw, Mq, 0], [0, 0, 1, 0]]
    Yv = lat["CYb"] * qS / (m * U)
    Yp, Yr = lat["CYp"] * qS * b / (2 * m * U), lat["CYr"] * qS * b / (2 * m * U)
    Lv, Lp, Lr = (lat["Clb"] * qS * b / (Ixx * U), lat["Clp"] * qS * b * b / (2 * Ixx * U),
                  lat["Clr"] * qS * b * b / (2 * Ixx * U))
    Nv, Np, Nr = (Cnb * qS * b / (Izz * U), lat["Cnp"] * qS * b * b / (2 * Izz * U),
                  lat["Cnr"] * qS * b * b / (2 * Izz * U))
    Alat = [[Yv, Yp, Yr - U, g], [Lv, Lp, Lr, 0], [Nv, Np, Nr, 0], [0, 1, 0, 0]]
    elon, elat = _eig4(Alon), _eig4(Alat)
    cpx = sorted([z for z in elon if z.imag > 1e-6], key=lambda z: -abs(z))
    out = {"eig_lon": [[round(z.real, 4), round(z.imag, 4)] for z in elon],
           "eig_lat": [[round(z.real, 4), round(z.imag, 4)] for z in elat]}
    if cpx:
        sp = cpx[0]
        out["sp_wn"], out["sp_zeta"] = abs(sp), -sp.real / abs(sp)
    else:
        out["sp_wn"], out["sp_zeta"] = max(abs(z) for z in elon), 1.0
    mr = max(z.real for z in elat)
    out["lat_max_real"] = mr
    out["lat_t2_s"] = math.log(2) / mr if mr > 0 else float("inf")
    return out


kit.claim("CL-B3-SP-ZETA", "Short-period damping ratio, 15 m/s", calc="CALC-B3-MODES", output="sp_zeta", unit="-",
          limit=(">=", "ASM-B3-ZETA-SP-MIN"), how="Twin: elevon doublet in MANUAL, pitch-rate overshoot.")
kit.claim("CL-B3-LAT-T2", "Lateral-directional divergence, time to double", calc="CALC-B3-MODES", output="lat_t2_s",
          unit="s", limit=(">=", 4.0),
          how="Twin, yaw assist off, at altitude: sideslip/heading drift after a yaw pulse (FC log).",
          note="MIL-F-8785C spiral limit (>= 4 s to double, Level 2 >= 8 s for Level 1 cat. B was 20 s); "
               "a directional divergence faster than this must be stabilised actively")


# ---------------------------------------------------------------------------------------------- cruise yaw by motors
@kit.calc("CALC-B3-YAW-ACTIVE", title="Cruise yaw control by differential thrust",
          assumes=["ASM-B3-BETA-DIST"],
          inputs={"Cnb": "CL-B3-CNB", "beta": "ASM-B3-BETA-DIST", "V": P + "performance.cruise_ms",
                  "rho": P + "env.rho_kgm3", "S": "CL-A1-WING-AREA", "b": P + "wing.span_m",
                  "m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "ld": P + "performance.ld_cruise",
                  "y": P + "propulsion.stations.y_m", "tmax": P + "propulsion.thrust_max_per_motor_kg",
                  "sag": P + "propulsion.voltage_sag"},
          units={"beta": "deg", "V": "m/s", "rho": "kg/m3", "S": "m2", "b": "m", "m": "kg", "g": "m/s2", "y": "m",
                 "tmax": "kg"},
          equation="N_req = |Cnb| beta q S b ; T_m = m g /(L/D) / 4 ; dT = min(T_m, Tmax sag g - T_m) ; "
                   "N_av = 4 dT y (total thrust held)")
def yaw_active(Cnb, beta, V, rho, S, b, m, g, ld, y, tmax, sag):
    q = 0.5 * rho * V * V
    Nreq = abs(min(Cnb, 0.0)) * math.radians(beta) * q * S * b
    Tm = m * g / ld / 4
    dT = min(Tm, tmax * sag * g - Tm)
    Nav = 4 * dT * y
    return {"N_req_Nm": Nreq, "N_av_Nm": Nav, "T_motor_N": Tm, "ratio": Nav / Nreq if Nreq > 0 else float("inf")}


kit.claim("CL-B3-YAW-ACTIVE-RATIO", "Cruise yaw: motor authority / instability", calc="CALC-B3-YAW-ACTIVE",
          output="ratio", unit="-", limit=(">=", "ASM-B3-AUTH-RATIO"),
          how="F4 maps yaw to left/right differential thrust in FW (SITL, then twin yaw doublets).")


# ---------------------------------------------------------------------------------------------- hover
HOV_IN = {"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "dl": P + "propulsion.download_factor",
          "split": "CL-A3-HOVER-SPLIT", "tmax": P + "propulsion.thrust_max_per_motor_kg", "sag": P + "propulsion.voltage_sag",
          "y": P + "propulsion.stations.y_m", "z": P + "propulsion.stations.z_m", "Qh": "CL-B4-HOVER-Q",
          "swirl": "CL-B4-YAW", "cant": "ASM-B4-CANT",
          "Ixx": "CL-A3-IXX", "Iyy": "CL-A3-IYY", "Izz": "CL-A3-IZZ", "m_basic": "CL-A3-MASS-BASIC",
          "rho": P + "env.rho_kgm3", "Vw": P + "requirements.wind_limit_ms", "S": "CL-A1-WING-AREA",
          "c": P + "wing.chord_m", "b": P + "wing.span_m", "x_t": "CL-B3-CG-TARGET", "cn90": "ASM-B3-CN90",
          "xcp": "ASM-B3-XCP-HOVER", "fc": P + "fins.chord_m", "fh": P + "fins.half_height_m",
          "fle": P + "fins.le_x_m", "asym": "ASM-B3-GUST-ASYM"}
HOV_U = {"m": "kg", "g": "m/s2", "tmax": "kg", "y": "m", "z": "m", "cant": "deg", "Ixx": "kg m2", "Iyy": "kg m2",
         "Izz": "kg m2", "m_basic": "kg", "rho": "kg/m3", "Vw": "m/s", "S": "m2", "c": "m", "b": "m", "x_t": "m",
         "fc": "m", "fh": "m", "fle": "m"}


@kit.calc("CALC-B3-HOVER", title="Hover control power vs 5 m/s wind", inputs=HOV_IN, units=HOV_U,
          assumes=["ASM-B3-CN90", "ASM-B3-XCP-HOVER", "ASM-B3-GUST-ASYM"],
          equation="dT = min(T_lower, Tmax sag - T_upper) per motor ; M_pitch = 2 dT (2 z) ; M_roll = 4 dT y ; "
                   "M_yaw = 4 dT (kq swirl + r sin cant), kq = Q_hover/T_hover (B4) ; disturbance: q S CN90 arm "
                   "(pitch), fins (roll), asym F b/4 (yaw)")
def hover(m, g, dl, split, tmax, sag, y, z, Qh, swirl, cant, Ixx, Iyy, Izz, m_basic, rho, Vw, S, c, b, x_t, cn90, xcp, fc, fh,
          fle, asym):
    k = m / m_basic
    z_cg = z * (split - 1) / (split + 1)        # CG height implied by the A3 split (lever balance)
    dist = FM.hover_disturbance(rho, Vw, S, c, x_t, cn90, xcp, 2 * fc * 2 * fh, fle + fc / 2, asym, b)
    kq = Qh / (m * g * dl / 4) * swirl            # effective reaction-torque arm after fin swirl recovery (B4)
    II = (Ixx * k, Iyy * k, Izz * k)
    dd = (dist["M_pitch"], dist["M_roll"], dist["M_yaw"])
    r = FM.hover_authority(m, g, dl, split, tmax * g * sag, y, z, z_cg, kq, 0.0, II, dd)
    r.update({f"dist_{a}_Nm": dist[f"M_{a}"] for a in ("pitch", "roll", "yaw")})
    r["kq_eff_m"] = kq
    rc = FM.hover_authority(m, g, dl, split, tmax * g * sag, y, z, z_cg, kq, cant, II, dd)   # with B4's cant
    r["ratio_yaw_cant"] = rc["ratio_yaw"]
    r["acc_yaw_cant_rads2"] = rc["acc_yaw_rads2"]
    r["M_yaw_cant_Nm"] = rc["M_yaw_Nm"]
    return r


for ax in ("pitch", "roll", "yaw"):
    kit.claim(f"CL-B3-HOVER-{ax.upper()}-RATIO", f"Hover {ax} control power / 5 m/s wind", calc="CALC-B3-HOVER",
              output=f"ratio_{ax}", unit="-", limit=(">=", "ASM-B3-AUTH-RATIO"), verifies=["R-WIND"],
              how="Twin, then aircraft: hover in 5 m/s; FC log of motor outputs - none may saturate (H2).")


kit.claim("CL-B3-HOVER-YAW-RATIO-CANT", "Hover yaw power / wind, 3 deg motor cant", calc="CALC-B3-HOVER",
          output="ratio_yaw_cant", unit="-", limit=(">=", "ASM-B3-AUTH-RATIO"), verifies=["R-WIND"],
          assumes=["ASM-B4-CANT"], how="Bench: yaw torque on a turntable with canted mounts; hover yaw steps (H2).",
          note="Applies once D3 cants the motor mounts 3 deg tangentially (CR-B4-04); without cant the yaw claim fails")


@kit.calc("CALC-B3-HOVER-TRIM", title="Hover pitch-trim share", inputs={"split": "CL-A3-HOVER-SPLIT"},
          equation="share of the pitch differential used by trim = (s - 1)/2", output="use")
def hover_trim_use(split):
    return (split - 1) / 2


@kit.calc("CALC-B3-SPLIT-LIMIT", title="Allowed hover trim share", inputs={"smax": "ASM-B3-SPLIT-MAX"},
          equation="(s_max - 1)/2", output="use")
def split_limit(smax):
    return (smax - 1) / 2


kit.claim("CL-B3-SPLIT-LIMIT", "Allowed hover trim share", calc="CALC-B3-SPLIT-LIMIT", output="use", unit="-",
          how="B3 choice (ASM-B3-SPLIT-MAX); F4 checks motor outputs in a hover log.")
kit.claim("CL-B3-HOVER-TRIM-USE", "Hover pitch-trim share of the differential", calc="CALC-B3-HOVER-TRIM",
          output="use", unit="-", limit=("<=", "CL-B3-SPLIT-LIMIT"),
          how="Hover log: mean upper vs lower motor output (RCOU), H2.")


@kit.calc("CALC-B3-WASH", title="Elevons in the hover slipstream?",
          inputs={"D": P + "propulsion.prop_diameter_m", "z": P + "propulsion.stations.z_m", "tc": P + "wing.t_c",
                  "c": P + "wing.chord_m", "ef": P + "wing.elevon.chord_frac", "defl": P + "wing.elevon.deflection_deg"},
          units={"D": "m", "z": "m", "c": "m", "defl": "deg"},
          equation="gap = (z - D/(2 sqrt 2)) - (t/2 + ef c sin(defl)) ; > 0: elevon outside the contracted wash",
          output="gap")
def wash(D, z, tc, c, ef, defl):
    return FM.slipstream_gap(D, z, tc * c / 2, ef, c, defl[1])


kit.claim("CL-B3-ELEVON-WASH-GAP", "Elevon to hover slipstream gap", calc="CALC-B3-WASH", output="gap", unit="m",
          how="Tuft or ribbon on the elevon in a tethered hover: if it does not stream, the elevons give no hover yaw.",
          note="Positive: the elevons sit outside the props' contracted wash, so hover yaw comes from rotor torque only")


# ---------------------------------------------------------------------------------------------- transition
@kit.calc("CALC-B3-TRANSITION", title="Quasi-steady transition pitch balance",
          assumes=["ASM-B3-CN90", "ASM-B3-CD0", "ASM-A1-CLMAX", "ASM-B3-PROP-CNA", "ASM-B3-DCM-VISC",
                   "ASM-B3-ELEVON-TRANS", "ASM-B3-ELEVON-POST", "ASM-B3-FLAP-EFF"],
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "S": "CL-A1-WING-AREA", "c": P + "wing.chord_m", "b": P + "wing.span_m", "x_t": "CL-B3-CG-TARGET",
                  "x_fwd": "CL-B3-CG-FWD", "xnp": "CL-B3-XNP", "cm_np_thin": "CL-B3-CM-NP-THIN",
                  "dcm": "ASM-B3-DCM-VISC", "CLa": "CL-B3-CLA", "a0": "CL-B3-ALPHA0", "clmax": "ASM-A1-CLMAX",
                  "cd0": "ASM-B3-CD0", "e": P + "wing.oswald_e", "cn90": "ASM-B3-CN90", "n": P + "propulsion.n_motors",
                  "D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "cna": "ASM-B3-PROP-CNA", "tmax": P + "propulsion.thrust_max_per_motor_kg",
                  "sag": P + "propulsion.voltage_sag", "z": P + "propulsion.stations.z_m",
                  "dl": P + "propulsion.download_factor", "vc": P + "performance.cruise_ms",
                  "CLd": "CL-B3-CLD", "Cmd_ref": "CL-B3-CMD", "xref": P + "cg.x_target_m", "eff": "ASM-B3-FLAP-EFF",
                  "dp": "ASM-B3-ELEVON-TRANS", "fpost": "ASM-B3-ELEVON-POST"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2", "c": "m", "b": "m", "x_t": "m", "x_fwd": "m",
                 "xnp": "m", "a0": "deg", "D": "m", "x_prop": "m", "tmax": "kg", "z": "m", "vc": "m/s",
                 "xref": "m", "dp": "deg"},
          equation="level flight at V: T cos a = D, T sin a + L = W ; wing CP from Xnp (attached) to 0.5 c at 90 deg ; "
                   "props' normal force at x_prop ; use = |M_aero| / (2 dT 2z), dT = min(T/4, Tmax sag - T/4)")
def transition(m, g, rho, S, c, b, x_t, x_fwd, xnp, cm_np_thin, dcm, CLa, a0, clmax, cd0, e, cn90, n, D, x_prop,
               cna, tmax, sag, z, dl, vc, CLd, Cmd_ref, xref, eff, dp, fpost):
    AR = b * b / S
    k_ind = 1 / (math.pi * e * AR)
    out = {}
    for tag, x in (("target", x_t), ("fwd", x_fwd)):
        rows = []
        for V in sorted({0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, vc}):
            cmd = (Cmd_ref + CLd * (x - xref) / c) * eff
            r = FM.transition_point(V, m, g, rho, S, c, x, xnp, cm_np_thin + dcm, CLa, math.radians(a0), clmax, cd0,
                                    k_ind, cn90, n, D, x_prop, cna, tmax * g * sag, z, 0.0, dl, cmd, dp, fpost)
            rows.append([V, round(r["alpha_deg"], 1), round(r["TW"], 3), round(r["M_aero_Nm"], 3),
                         round(r["M_elev_Nm"], 3), round(r["M_avail_Nm"], 3), round(r["use"], 3)])
        out[tag] = rows
    out["columns"] = ["V m/s", "alpha deg", "T/W", "M_aero N m", "M_elevon N m", "M_motor avail N m", "use"]
    out["use_max"] = max(r[6] for t in ("target", "fwd") for r in out[t])
    out["v_at_use_max"] = max(((r[6], r[0]) for t in ("target", "fwd") for r in out[t]))[1]
    out["tw_max"] = max(r[2] for r in out["target"])
    return out


kit.claim("CL-B3-TRANS-PITCH-USE", "Transition: pitch differential used, worst", calc="CALC-B3-TRANSITION",
          output="use_max", unit="-", limit=("<=", "ASM-B3-TRANS-USE-MAX"), verifies=["R-TRANSITION"],
          assumes=["ASM-B3-CN90"],
          how="SITL with the AVL/flat-plate aero table (F4); then twin transitions: RCOU of upper vs lower pair "
              "stays below 80 % of range.")

# ---------------------------------------------------------------------------------------------- tests (planned)
kit.test("T-B3-CG-BALANCE", "CG balance at the limits", verifies=["CL-B3-CG-AFT", "CL-B3-CG-FWD", "CL-B3-CG-TARGET"],
         procedure="H1: balance the ready-to-fly aircraft on two fingertips (or a knife-edge jig) at the fin roots; "
                   "the balance line must lie between the two marks drawn at the B3 limits.")
kit.test("T-B3-TWIN-NP", "Twin neutral point from glides", verifies=["CL-B3-XNP", "CL-B3-SM-TARGET"],
         procedure="Twin, FBWA glides at 3 speeds for 2 pack positions; plot elevon trim vs CL; Xnp where the slope is 0.")
kit.test("T-B3-YAW-DOUBLET", "Twin FW yaw doublet", verifies=["CL-B3-CNB", "CL-B3-YAW-ACTIVE-RATIO"],
         procedure="Twin in FBWA at 15 m/s, 50 m AGL: yaw pulse by differential thrust; with assist off, record heading "
                   "and sideslip divergence; with assist on, it must return within 2 s.")
kit.test("T-B3-HOVER-WIND", "Hover authority in wind", verifies=["CL-B3-HOVER-PITCH-RATIO", "CL-B3-HOVER-ROLL-RATIO",
                                                                 "CL-B3-HOVER-YAW-RATIO"],
         procedure="Tethered then free hover at 5 m/s measured wind; no motor output above 85 % or below 10 % (RCOU).")


if __name__ == "__main__":
    kit.write()
    # human-readable dump of every calc output for S-AND-C.md
    res = {n["id"]: n.get("outputs") for n in kit.nodes.values() if n["type"] == "calculation"}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "sc_results.json").write_text(json.dumps(res, indent=1, default=str))
    print("wrote results/sc_results.json")
