"""B3 stability and control: proof-chain claims for the K09-L quad tailsitter (R1 geometry, A1-R2 params).

Run (from the repo root, AVL 3.52 at C:/Users/dillo/tools/avl/avl352.exe; first run ~3 min, then cached):
    python -I redesign/team/B3/sc_analysis.py       # AVL + hand models -> claims.json, results/sc_results.json
    python -I redesign/team/B3/run_avl_study.py     # sensitivities, AVL MODE cross-check, model files
    python -I redesign/team/B3/draw_cg.py           # FIG B3-01
    python -I redesign/proofs/build_graph.py

Every calculation is a pure function of params.json keys, other roles' claims and ASM-B3 assumptions. AVL runs are
cached in team/B3/avl/cache/ keyed by the generated input text, so build_graph.py re-runs them in milliseconds.
Section data (S5010 viscous cm, elevon effectiveness, clmax vs elevon) are B2's. Model and methods: S-AND-C.md.
Library: avl_model.py (AVL), flight_models.py (hand models).
"""
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
LAT_TRIM = "medium"     # trim sweeps with strip output: medium lattice (fine changes Xnp by < 0.02 % c, see CL-B3-AVL-CONV)
CLS = [0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.10, 1.20]      # trim CLs for the critical-section search
SM_GRID = [0.03 + 0.01 * i for i in range(12)]                     # static margins scanned for the forward limit

# ---------------------------------------------------------------------------------------------- sources
kit.source("SRC-B3-AVL", "AVL 3.52 vortex-lattice code (Drela, Youngren)", "web",
           url="https://web.mit.edu/drela/Public/web/avl/", checked="2026-11-09",
           where="avl_doc.txt: geometry, CONTROL, ST, FT, FS and MODE output", note="installed at C:/Users/dillo/tools/avl")
kit.source("SRC-B3-RIBNER", "Ribner, Propellers in yaw, NACA Report 820 (1945)", "paper",
           url="https://ntrs.nasa.gov/citations/19930091895", where="normal-force derivative of a propeller")
kit.source("SRC-B3-PERKINS", "Perkins & Hage, Airplane Performance, Stability and Control (1949)", "book",
           where="ch. 5: propeller normal force dCN/dalpha = 4.25 sigma_e/(1+2 sigma_e) sin(beta+8 deg) f(Tc)")
kit.source("SRC-B3-MIL8785C", "MIL-F-8785C Flying qualities of piloted airplanes (1980)", "standard",
           url="http://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-F/MIL-F-8785C_5295/",
           where="3.2.2.1.2 short-period damping >= 0.30 cat. B Level 1 (0.35 cat. A/C); 3.3.1.1 Dutch roll "
                 "zeta >= 0.08 cat. B Level 1; 3.3.4 roll performance")
kit.source("SRC-B3-HOERNER", "Hoerner, Fluid-Dynamic Drag / Lift (1965/1985)", "book",
           where="flat plate normal force at 90 deg, CN ~1.17-1.2 for low aspect ratio")
kit.source("SRC-B3-MUNK", "Munk, The aerodynamic forces on airship hulls, NACA Report 184 (1924)", "paper",
           url="https://ntrs.nasa.gov/citations/19930091248", where="slender-body moment = 2 q Vol alpha (k2-k1 ~ 1)")

# ---------------------------------------------------------------------------------------------- assumptions
kit.assumption("ASM-B3-CLMAX-FLAP", "S5010 section clmax vs elevon deflection (B2 envelope)",
               "[delta deg, clmax] at Re 2.3e5, conservative envelope of Re 2.3e5 / 3.0e5, non-increasing for up-elevon; "
               "used strip by strip in the critical-section method (elevon strips at their trim deflection, others at 0)",
               basis="team/B2/out/avl_results.json foils.s5010.clmax_vs_flap_re2.3e5 (B2 xfoil_wing.py, avl_wing.py "
                     "clmax_vs_flap). Re at the R1 stall is ~2.6e5, so the table is slightly conservative. B2 to publish it "
                     "as a P:b2 key (CR-B3-13)",
               value=[[-15.0, 1.0276], [-10.0, 1.0276], [-5.0, 1.1199], [0.0, 1.2423], [5.0, 1.3601], [10.0, 1.4677]],
               unit="deg,-", status="UNVERIFIED", cites=["SRC-B2-XFOIL"])
kit.assumption("ASM-B3-PROP-CNA", "Propeller normal-force slope",
               "dCN/dalpha of one 11x5.5MR prop, on its disk area and freestream q, lightly loaded",
               basis="Perkins & Hage with sigma_e 0.09 (2 blades, ~20 mm chord at 0.75 R), beta_0.75 = 12.0 deg for "
                     "5.5 in pitch, f(Tc) ~1.1: 0.11 per rad (0.10 for the 11x4.5MR). Uncertainty +/-50 %",
               value=0.11, unit="1/rad", status="UNVERIFIED", cites=["SRC-B3-PERKINS", "SRC-B3-RIBNER"])
kit.assumption("ASM-B3-UPWASH", "Upwash factor at the props", "1 + d(eps_u)/d(alpha) at the prop planes",
               basis="prop planes 5 mm ahead of the LE but 0.19 m (0.6 c) off the wing plane; DATCOM upwash ~1.1-1.2",
               value=1.15, unit="-")
kit.assumption("ASM-B3-CD-CYL", "Cross-flow CD of tubes and motors", "CD of the 22 mm tubes and the motor cans "
               "normal to their axis", basis="circular cylinder, subcritical Re ~2e4: 1.0-1.2 (Hoerner)",
               value=1.1, unit="-", cites=["SRC-B3-HOERNER"])
kit.assumption("ASM-B3-POD-K", "Pod Munk factor, pitch", "Fraction of the slender-body destabilising pitch moment the "
               "pod gives, sitting on the wing upper surface", basis="half-body on a wall ~0.5 (image); ESTIMATE",
               value=0.5, unit="-", cites=["SRC-B3-MUNK"])
kit.assumption("ASM-B3-POD-K-YAW", "Pod Munk factor, yaw", "Fraction of the slender-body destabilising yaw moment the "
               "pod gives", basis="full side area exposed in sideslip; 1.0 is the conservative upper bound",
               value=1.0, unit="-", cites=["SRC-B3-MUNK"])
kit.assumption("ASM-B3-PB2V-MIN", "Minimum roll helix angle", "pb/2V with the travel left after trim, at the trimmed stall",
               basis="small-UAV practice from MIL-F-8785C class I roll times: pb/2V >= 0.07", value=0.07, unit="-",
               cites=["SRC-B3-MIL8785C"])
kit.assumption("ASM-B3-AUTH-RATIO", "Control power over disturbance, cruise", "Available control moment / disturbance "
               "moment in cruise (motor-out roll)", basis="twice the disturbance; B3 choice, leaves half for manoeuvre",
               value=2.0, unit="-")
kit.assumption("ASM-B3-HOVER-DIFF", "Hover differential allowed for control", "Differential thrust per motor used for "
               "attitude control, as a fraction of hover thrust", basis="R-HOVER-AUTHORITY text (team/A2/claims.json): "
               "'using <= 30 % of hover thrust per motor as differential'", value=0.30, unit="-")
kit.assumption("ASM-B3-CN90", "Flat-plate normal force at 90 deg", "CN of the wing broadside and the fins broadside",
               basis="Hoerner: 1.17 (AR 1-5); used 1.2", value=1.2, unit="-", cites=["SRC-B3-HOERNER"])
kit.assumption("ASM-B3-XCP-HOVER", "Wing centre of pressure, wind on the face", "x_cp/c of the wing normal force at "
               "70-90 deg incidence", basis="flat plate 0.40-0.50 c; 0.45 used", value=0.45, unit="-",
               cites=["SRC-B3-HOERNER"])
kit.assumption("ASM-B3-GUST-ASYM", "Spanwise gust asymmetry in hover", "Fraction of the wing normal force acting as a "
               "left-right difference at b/4", basis="ESTIMATE for a 1.15 m span in turbulent 5 m/s wind", value=0.10,
               unit="-", status="UNVERIFIED")
kit.assumption("ASM-B3-CD0", "Profile drag for the transition and mode models", "CD0 of wing + fins + pod + tubes",
               basis="B1 owns the drag build-up: B2 wing section 0.0074 plus fins, pod, tubes; 0.020 used here (B1's "
                     "0.061 is the whole-aircraft value incl. props windmilling; both bracket the mode results)",
               value=0.020, unit="-")
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
kit.assumption("ASM-B3-ZETA-SP-MIN", "Short-period damping minimum", "Level 1 short-period damping ratio",
               basis="MIL-F-8785C 3.2.2.1.2, cat. B Level 1", value=0.30, unit="-", cites=["SRC-B3-MIL8785C"])
kit.assumption("ASM-B3-ZETA-DR-MIN", "Dutch-roll damping minimum", "Level 1 Dutch-roll damping ratio",
               basis="MIL-F-8785C 3.3.1.1, cat. B Level 1", value=0.08, unit="-", cites=["SRC-B3-MIL8785C"])

GEO = {"b": P + "wing.span_m", "c": P + "wing.chord_m", "ef": P + "wing.elevon.chord_frac",
       "yin": P + "wing.elevon.inboard_y_m", "yout": P + "wing.elevon.outboard_y_m", "fy": P + "fins.y_m",
       "fh": P + "fins.half_height_m", "fle": P + "fins.le_x_m", "fte": P + "fins.te_x_m"}
GEOU = {"b": "m", "c": "m", "yin": "m", "yout": "m", "fy": "m", "fh": "m", "fle": "m", "fte": "m"}
GKEYS = ("b", "c", "ef", "yin", "yout", "fy", "fh", "fle", "fte")


def _g(b, c, ef, yin, yout, fy, fh, fle, fte, xref, zref, **extra):
    return AV.geometry_from(b, c, ef, yin, yout, fy, fh, fle, fte, xref, zref, **extra)


def _interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return ys[-1]


def critical_section(geo, xref_eff, zref, eta, dcm, table, cls=CLS):
    """Trimmed CLmax by the critical-section method (B2's method, WING-AERO.md): AVL trims Cm + dcm = 0 about
    xref_eff at each CL with the elevon in physical degrees (gain eta); the first strip whose cl reaches its local
    clmax (table at that strip's deflection: elevon strips at the trim deflection, others at 0) sets CLmax."""
    g = _g(**geo, xref=xref_eff, zref=zref, egain=eta)
    rows = AV.trim_sweep(g, cls, -dcm, LAT_TRIM)
    ds, cs = [r[0] for r in table], [r[1] for r in table]
    yin, yout = geo["yin"], geo["yout"]

    def in_el(y):
        return yin[0] <= y <= yin[1] or yout[0] <= y <= yout[1]

    prev, hist = None, []
    for r in rows:
        lim0 = _interp(0.0, ds, cs)
        limd = _interp(r["d1"], ds, cs)
        ratio, yfirst = max((s[2] / (limd if in_el(s[0]) else lim0), s[0]) for s in r["strips"])
        h = {"CL": r["CL"], "alpha": r["alpha"], "d1": r["d1"], "ratio": ratio, "y": yfirst}
        hist.append(h)
        if ratio >= 1.0 and prev is not None:
            f = (1.0 - prev["ratio"]) / (ratio - prev["ratio"])
            lerp = lambda k: prev[k] + f * (h[k] - prev[k])   # noqa: E731
            return {"CLmax": lerp("CL"), "delta": lerp("d1"), "alpha": lerp("alpha"), "y_first": yfirst,
                    "history": hist}
        prev = h
    raise RuntimeError("critical section not reached inside the CL sweep: widen CLS")


# ---------------------------------------------------------------------------------------------- AVL runs
@kit.calc("CALC-B3-AVL-CONV", title="AVL lattice convergence", inputs={**GEO, "xref": P + "cg.x_target_m",
          "zref": P + "cg.z_target_m"}, units={**GEOU, "xref": "m", "zref": "m"}, cites=["SRC-B3-AVL"],
          equation="Xnp, Cm_de, Cn_beta at alpha 4 deg on coarse / medium / fine lattices; d = |fine - medium|")
def avl_convergence(b, c, ef, yin, yout, fy, fh, fle, fte, xref, zref):
    g = _g(b, c, ef, yin, yout, fy, fh, fle, fte, xref, zref)
    r = {k: AV.derivatives(g, 4.0, k) for k in ("coarse", "medium", "fine")}
    return {"xnp_coarse": r["coarse"]["Xnp"], "xnp_medium": r["medium"]["Xnp"], "xnp_fine": r["fine"]["Xnp"],
            "dxnp_frac_c": abs(r["fine"]["Xnp"] - r["medium"]["Xnp"]) / c,
            "dcmd_rel": abs(r["fine"]["Cmd01"] / r["medium"]["Cmd01"] - 1),
            "cnb_coarse": r["coarse"]["Cnb"], "cnb_medium": r["medium"]["Cnb"], "cnb_fine": r["fine"]["Cnb"],
            "dcnb_abs": abs(r["fine"]["Cnb"] - r["medium"]["Cnb"])}


@kit.calc("CALC-B3-AVL-LONG", title="AVL derivatives, elevons neutral", inputs={**GEO, "xref": P + "cg.x_target_m",
          "zref": P + "cg.z_target_m"}, units={**GEOU, "xref": "m", "zref": "m"},
          cites=["SRC-B3-AVL", "SRC-B2-S5010-COORD"],
          equation="AVL fine lattice, S5010 camber line, alpha 4 deg, controls 0: CLa, Xnp, alpha0, "
                   "Cm_np = Cm_ref + CL (Xnp - xref)/c, control derivatives per deg (thin-airfoil)")
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
          how="AVL fine lattice; cross-check B2's own AVL wing+fins model (P:b2.avl.xnp_m) after B2 re-runs at R1.")
kit.claim("CL-B3-CLA", "Lift-curve slope, AVL", calc="CALC-B3-AVL-LONG", output="CLa", unit="1/rad",
          how="Twin glide: alpha from the FC vs CL from airspeed and mass.")
kit.claim("CL-B3-ALPHA0", "Zero-lift angle, AVL", calc="CALC-B3-AVL-LONG", output="alpha0_deg", unit="deg",
          how="Follows from AVL with the S5010 camber line.")
kit.claim("CL-B3-CLD", "Elevon lift per degree, AVL thin", calc="CALC-B3-AVL-LONG", output="CLd", unit="1/deg",
          how="Twin: CL change per degree of trim in level glide (x CL-B2-ELEVON-ETA).")
kit.claim("CL-B3-CMD", "Elevon pitch moment per degree, AVL thin", calc="CALC-B3-AVL-LONG", output="Cmd_ref",
          unit="1/deg", how="Twin: pitch-rate response to an elevon step (FC log), fitted.")
kit.claim("CL-B3-CM-NP-THIN", "Cm about the NP, AVL thin", calc="CALC-B3-AVL-LONG", output="cm_np_thin", unit="-",
          how="Follows from AVL; B2's viscous shift CL-B2-DCM-VISC is added in each trim calculation.")
kit.claim("CL-B3-CLDA", "Elevon roll moment per degree, AVL thin", calc="CALC-B3-AVL-LONG", output="Cld",
          unit="1/deg", how="Twin: roll-rate response to a differential elevon step (x CL-B2-ELEVON-ETA).")
kit.claim("CL-B3-CLP", "Roll damping, AVL", calc="CALC-B3-AVL-LONG", output="Clp", unit="-",
          how="Twin: roll-rate decay after a step (time constant).")


# ---------------------------------------------------------------------------------------------- neutral point
@kit.calc("CALC-B3-NP", title="Neutral point with props and pod",
          assumes=["ASM-B3-PROP-CNA", "ASM-B3-UPWASH", "ASM-B3-POD-K"], cites=["SRC-B3-RIBNER", "SRC-B3-MUNK"],
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
          how="Twin and aircraft: elevon trim vs CL at two pack positions in FBWA glides; "
                                 "Xnp where the trim-vs-CL slope is zero (T-B3-TWIN-NP).")


# ---------------------------------------------------------------------------------------------- CG limits
CS_IN = {**GEO, "zref": P + "cg.z_target_m", "xnp_a": "CL-B3-XNP-AERO", "xnp": "CL-B3-XNP",
         "dcm": "CL-B2-DCM-VISC", "eta": "CL-B2-ELEVON-ETA", "tab": "ASM-B3-CLMAX-FLAP",
         "m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "S": "CL-A1-WING-AREA"}
CS_U = {**GEOU, "zref": "m", "xnp_a": "m", "xnp": "m", "m": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2"}


def _cs_at(x, geo, zref, xnp_a, xnp, eta, dcm, tab, m, g, rho, S):
    """Critical section at CG x. AVL has no props or pod: the reference is shifted by (Xnp_aero - Xnp) so the AVL
    model has the whole aircraft's static margin."""
    r = critical_section(geo, x + (xnp_a - xnp), zref, eta, dcm, tab)
    r["vs"] = FM.stall_speed(m, g, rho, S, r["CLmax"])
    return r


def _crossing(xs, ys, lim):
    """Largest x (xs ascending) at which ys first exceeds lim, linear between grid points; None if never."""
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if y0 <= lim < y1:
            return x0 + (lim - y0) * (x1 - x0) / (y1 - y0)
    return None if ys[0] > lim else xs[-1]


@kit.calc("CALC-B3-CG-LIMITS", title="CG limits from stability, elevon trim and the trimmed stall",
          assumes=["ASM-B3-CLMAX-FLAP"], cites=["SRC-B3-AVL"],
          inputs={**CS_IN, "sm_min": P + "requirements.static_margin_min",
                  "travel": P + "wing.elevon.deflection_deg", "tfrac": P + "requirements.elevon_trim_travel_max",
                  "vmax": P + "requirements.stall_max_ms"},
          units={**CS_U, "travel": "deg", "vmax": "m/s"},
          equation="aft: x = Xnp - SMmin c ; for SM 3..14 %: AVL trim (Cm + dcm = 0, elevon gain eta) at CL 0.4..1.2, "
                   "critical section -> CLmax_t(SM), delta(SM), Vs(SM) ; forward = smaller SM of "
                   "{|delta| = tfrac travel, Vs = Vs_max} ; target = mid-range")
def cg_limits(b, c, ef, yin, yout, fy, fh, fle, fte, zref, xnp_a, xnp, dcm, eta, tab, m, g, rho, S, sm_min, travel,
              tfrac, vmax):
    geo = dict(zip(GKEYS, (b, c, ef, yin, yout, fy, fh, fle, fte)))
    rows = []
    for sm in SM_GRID:
        r = _cs_at(xnp - sm * c, geo, zref, xnp_a, xnp, eta, dcm, tab, m, g, rho, S)
        rows.append([round(sm, 3), round(xnp - sm * c, 5), round(r["CLmax"], 4), round(r["delta"], 2),
                     round(r["alpha"], 2), round(r["vs"], 3), round(r["y_first"], 3)])
    sms = [r[0] for r in rows]
    budget = tfrac * travel[1]
    sm_trim = _crossing(sms, [-r[3] for r in rows], budget)
    sm_stall = _crossing(sms, [r[5] for r in rows], vmax)
    x_aft = xnp - sm_min * c
    cand = [s for s in (sm_trim, sm_stall) if s is not None]
    sm_fwd = min(cand) if cand else sm_min
    closed = sm_fwd <= sm_min
    if closed:
        sm_fwd = sm_min
    x_fwd = xnp - sm_fwd * c
    x_t = 0.5 * (x_aft + x_fwd)
    return {"x_aft": x_aft, "x_fwd": x_fwd, "sm_fwd": sm_fwd, "x_target": x_t, "sm_target": (xnp - x_t) / c,
            "width": x_aft - x_fwd, "x_aft_frac": x_aft / c, "x_fwd_frac": x_fwd / c, "range_closed": int(closed),
            "sm_fwd_trim": sm_trim, "sm_fwd_stall": sm_stall,
            "x_fwd_trim": None if sm_trim is None else xnp - sm_trim * c,
            "x_fwd_stall": None if sm_stall is None else xnp - sm_stall * c,
            "trim_budget_deg": budget, "binding": "stall" if sm_fwd == sm_stall else "trim",
            "columns": ["SM", "x_cg m", "CLmax_trim", "elevon deg", "alpha deg", "Vs m/s", "y first stall m"],
            "table": rows}


kit.claim("CL-B3-CG-AFT", "Aft CG limit", calc="CALC-B3-CG-LIMITS", output="x_aft", unit="m",
          how="T-B3-CG-BALANCE: balance on the two fin-root marks; never fly with the balance point aft of this line.")
kit.claim("CL-B3-CG-FWD", "Forward CG limit", calc="CALC-B3-CG-LIMITS", output="x_fwd", unit="m",
          how="T-B3-CG-BALANCE; twin slow flight at the forward mark: stall at <= 12 m/s (scaled) with <= 12.5 deg up.")
kit.claim("CL-B3-CG-TARGET", "CG design target", calc="CALC-B3-CG-LIMITS", output="x_target", unit="m",
          how="A3 roll-up and H1 balance with the pack at its nominal station.")
kit.claim("CL-B3-CG-WIDTH", "CG range width", calc="CALC-B3-CG-LIMITS", output="width", unit="m",
          limit=(">=", 0.004), how="Follows from the two limits; >= 4 mm so the pack slide and build scatter fit.",
          note="4 mm = +/-2 mm H1 balance repeatability; ESTIMATE")
kit.claim("CL-B3-SM-TARGET", "Static margin at the CG target", calc="CALC-B3-CG-LIMITS", output="sm_target", unit="-",
          limit=(">=", P + "requirements.static_margin_min"), verifies=["R-STATIC-MARGIN"],
          assumes=["ASM-B3-PROP-CNA"], how="T-B3-TWIN-NP: elevon-trim-vs-CL slope at two CG positions (FBWA glides).")


@kit.calc("CALC-B3-CG-CHECK", title="A3 CG (pack at the A3 station and pack centred) against the B3 range",
          inputs={"cg_frac": "CL-A3-CG-X", "c": P + "wing.chord_m", "x_fwd": "CL-B3-CG-FWD", "x_aft": "CL-B3-CG-AFT",
                  "x_t": "CL-B3-CG-TARGET", "pod_le": P + "pod.x_le_m", "pod": P + "pod.size_m",
                  "x_pack": "CL-A3-PACK-X-REQ", "m_pack": P + "battery.mass_kg", "m_basic": "CL-A3-MASS-BASIC",
                  "slide": "ASM-A3-PACK-SLIDE"},
          units={"c": "m", "x_fwd": "m", "x_aft": "m", "x_t": "m", "pod_le": "m", "pod": "m", "m_pack": "kg"},
          equation="x_now = cg_frac c ; x_centred = x_now + (x_pod_centre - x_pack) m_pack/m ; margins to the limits ; "
                   "pack station for the target = x_pack + (x_t - x_now) m/m_pack")
def cg_check(cg_frac, c, x_fwd, x_aft, x_t, pod_le, pod, x_pack, m_pack, m_basic, slide):
    x = cg_frac * c
    x_pc = pod_le + pod[0] / 2
    xc = x + (x_pc - x_pack) * m_pack / m_basic
    xp_t = x_pack + (x_t - x) * m_basic / m_pack
    return {"x_now": x, "margin_fwd": x - x_fwd, "margin_aft": x_aft - x, "to_target": x_t - x,
            "x_centred": xc, "centred_margin_fwd": xc - x_fwd, "centred_margin_aft": x_aft - xc,
            "pack_x_target": xp_t, "pack_offset_target": xp_t - x_pc,
            "pack_slide_left": slide - abs(xp_t - x_pc),
            "cg_slide_fwd": xc - slide * m_pack / m_basic, "cg_slide_aft": xc + slide * m_pack / m_basic}


kit.claim("CL-B3-CG-NOW-FWD", "A3 CG (pack 29 mm forward) behind the forward limit", calc="CALC-B3-CG-CHECK",
          output="margin_fwd", unit="m", limit=(">=", 0.0),
          how="Re-run after A3 updates the roll-up; T-B3-CG-BALANCE on the built aircraft.")
kit.claim("CL-B3-CG-NOW-AFT", "A3 CG (pack 29 mm forward) ahead of the aft limit", calc="CALC-B3-CG-CHECK",
          output="margin_aft", unit="m", limit=(">=", 0.0), how="As CL-B3-CG-NOW-FWD.")
kit.claim("CL-B3-CG-CENTRED-AFT", "CG with the pack centred, ahead of the aft limit (D-17 test)",
          calc="CALC-B3-CG-CHECK", output="centred_margin_aft", unit="m", limit=(">=", 0.0),
          how="A3 roll-up with the pack at the pod centre; T-B3-CG-BALANCE.",
          note="D-17: if negative, A1 moves the pod nose to -0.125 m")
kit.claim("CL-B3-CG-CENTRED-FWD", "CG with the pack centred, behind the forward limit", calc="CALC-B3-CG-CHECK",
          output="centred_margin_fwd", unit="m", limit=(">=", 0.0), how="As CL-B3-CG-CENTRED-AFT.")
kit.claim("CL-B3-PACK-SLIDE-LEFT", "Pack slide left with the pack at the target station", calc="CALC-B3-CG-CHECK",
          output="pack_slide_left", unit="m", limit=(">=", 0.0),
          how="D2 marks the pack station on the tray; H1 balance confirms the CG on target.")


# ---------------------------------------------------------------------------------------------- trimmed stall
@kit.calc("CALC-B3-STALL-TRIM", title="Trimmed CLmax, stall and transition speed at the gate",
          assumes=["ASM-B3-CLMAX-FLAP"], cites=["SRC-B3-AVL"],
          inputs={**CS_IN, "x_t": "CL-B3-CG-TARGET", "x_aft": "CL-B3-CG-AFT", "x_fwd": "CL-B3-CG-FWD",
                  "k": P + "requirements.transition_factor"},
          units={**CS_U, "x_t": "m", "x_aft": "m", "x_fwd": "m"},
          equation="critical section at each CG -> CLmax_t, delta ; Vs = sqrt(2 m g / (rho S CLmax_t)) ; "
                   "Vt = k Vs at the forward limit (worst CG in the range)")
def stall_trim(b, c, ef, yin, yout, fy, fh, fle, fte, zref, xnp_a, xnp, dcm, eta, tab, m, g, rho, S, x_t, x_aft,
               x_fwd, k):
    geo = dict(zip(GKEYS, (b, c, ef, yin, yout, fy, fh, fle, fte)))
    out = {}
    for tag, x in (("target", x_t), ("aft", x_aft), ("fwd", x_fwd)):
        r = _cs_at(x, geo, zref, xnp_a, xnp, eta, dcm, tab, m, g, rho, S)
        out[f"clmax_{tag}"], out[f"delta_{tag}"], out[f"alpha_{tag}"] = r["CLmax"], r["delta"], r["alpha"]
        out[f"vs_{tag}"], out[f"y_first_{tag}"] = r["vs"], r["y_first"]
    out["vt_target"] = k * out["vs_target"]
    out["vt_fwd"] = k * out["vs_fwd"]
    return out


kit.claim("CL-B3-CLMAX-TRIM", "Trimmed CLmax at the CG target", calc="CALC-B3-STALL-TRIM", output="clmax_target",
          unit="-", assumes=["ASM-B3-CLMAX-FLAP"],
          how="T-B2-STALL at the gate mass, CG on target: CLmax = 2 m g / (rho S Vs^2).")
kit.claim("CL-B3-VS-TRIM", "Trimmed stall speed at the gate, CG target", calc="CALC-B3-STALL-TRIM",
          output="vs_target", unit="m/s", limit=("<=", P + "requirements.stall_max_ms"), verifies=["R-STALL"],
          how="Twin, then aircraft at 2.6 kg: FBWA slow-flight to the stall break with airspeed logging, CG on target.")
kit.claim("CL-B3-VS-TRIM-FWD", "Trimmed stall speed at the gate, forward CG limit", calc="CALC-B3-STALL-TRIM",
          output="vs_fwd", unit="m/s", limit=("<=", P + "requirements.stall_max_ms"), verifies=["R-STALL"],
          how="As CL-B3-VS-TRIM with the CG on the forward mark.")
kit.claim("CL-B3-VT-TRIM", "Transition speed 1.3 Vs, forward CG limit (ARSPD_FBW_MIN)", calc="CALC-B3-STALL-TRIM",
          output="vt_fwd", unit="m/s", limit=("<=", P + "performance.cruise_ms"), verifies=["R-TRANSITION"],
          how="F4 sets ARSPD_FBW_MIN >= this (rounded up); flight log of the first transition (H2).")


# ---------------------------------------------------------------------------------------------- trim sweep
@kit.calc("CALC-B3-TRIM-SWEEP", title="Trim across speeds (AVL, elevon in physical degrees)",
          cites=["SRC-B3-AVL"],
          inputs={**CS_IN, "x_t": "CL-B3-CG-TARGET", "x_aft": "CL-B3-CG-AFT", "x_fwd": "CL-B3-CG-FWD",
                  "vs": "CL-B3-VS-TRIM", "vc": P + "performance.cruise_ms"},
          units={**CS_U, "x_t": "m", "x_aft": "m", "x_fwd": "m", "vs": "m/s", "vc": "m/s"},
          equation="CL = 2 m g/(rho V^2 S) ; AVL: alpha for CL, elevon (gain eta) for Cm + dcm = 0 about "
                   "x_cg + (Xnp_a - Xnp)")
def trim_sweep(b, c, ef, yin, yout, fy, fh, fle, fte, zref, xnp_a, xnp, dcm, eta, tab, m, g, rho, S, x_t, x_aft,
               x_fwd, vs, vc):
    speeds = [round(vs, 2)] + [v for v in (13.0, 14.0, 15.0, 16.0, 18.0, 20.0, 22.0, 25.0) if v > vs + 0.05]
    cls = [2 * m * g / (rho * V * V * S) for V in speeds]
    rows = {}
    for tag, x in (("fwd", x_fwd), ("target", x_t), ("aft", x_aft)):
        gg = _g(b, c, ef, yin, yout, fy, fh, fle, fte, x + (xnp_a - xnp), zref, egain=eta)
        res = AV.trim_sweep(gg, cls, -dcm, LAT_TRIM)
        rows[tag] = [[V, round(r["CL"], 4), round(r["alpha"], 2), round(r["d1"], 2)] for V, r in zip(speeds, res)]
    cruise = [r for r in rows["target"] if abs(r[0] - vc) < 1e-6][0]
    worst = min(r[3] for t in rows.values() for r in t)
    return {"columns": ["V m/s", "CL", "alpha deg", "elevon deg (- TE up)"], "table": rows,
            "delta_cruise": cruise[3], "alpha_cruise": cruise[2], "delta_worst": worst}


kit.claim("CL-B3-ELEVON-TRIM-CRUISE", "Elevon trim at cruise speed, CG target", calc="CALC-B3-TRIM-SWEEP",
          output="delta_cruise", unit="deg", how="FBWA level flight at 16 m/s: servo output vs neutral (FC log).")
kit.claim("CL-B3-ALPHA-CRUISE", "Body angle at cruise speed, CG target", calc="CALC-B3-TRIM-SWEEP",
          output="alpha_cruise", unit="deg", how="FC pitch angle in level flight at 16 m/s (no wind).")


# ---------------------------------------------------------------------------------------------- roll and cruise authority
@kit.calc("CALC-B3-ROLL", title="Roll authority at the trimmed stall",
          inputs={"Cld": "CL-B3-CLDA", "Clp": "CL-B3-CLP", "eta": "CL-B2-ELEVON-ETA",
                  "travel": P + "wing.elevon.deflection_deg", "d_stall": "CL-B3-DELTA-STALL", "vs": "CL-B3-VS-TRIM",
                  "b": P + "wing.span_m", "S": "CL-A1-WING-AREA", "rho": P + "env.rho_kgm3", "Ixx": "CL-A3-IXX",
                  "m_basic": "CL-A3-MASS-BASIC", "m": P + "requirements.mtow_gate_kg"},
          units={"travel": "deg", "d_stall": "deg", "vs": "m/s", "b": "m", "S": "m2", "rho": "kg/m3", "m": "kg"},
          equation="da = travel - |delta_trim at CLmax| ; pb/2V = |Cld| eta da / |Clp| ; tau = Ixx / (|Clp| q S b^2 / 2V) ;"
                   " t60 from first-order roll response")
def roll_authority(Cld, Clp, eta, travel, d_stall, vs, b, S, rho, Ixx, m_basic, m):
    da = travel[1] - abs(d_stall)
    pb2v = abs(Cld) * eta * da / abs(Clp)
    V = vs
    p = pb2v * 2 * V / b
    q = 0.5 * rho * V * V
    Lp = abs(Clp) * q * S * b * b / (2 * V)
    tau = Ixx * m / m_basic / Lp
    t, phi = 0.0, 0.0
    while phi < math.radians(60) and t < 10:
        t += 0.001
        phi = p * (t - tau * (1 - math.exp(-t / tau)))
    return {"da_deg": da, "pb2v": pb2v, "p_degs": math.degrees(p), "tau_s": tau, "t60_s": t}


kit.claim("CL-B3-DELTA-STALL", "Elevon trim at the trimmed CLmax, CG target", calc="CALC-B3-STALL-TRIM",
          output="delta_target", unit="deg", how="Twin slow flight: elevon output at the stall break (FC log).")
kit.claim("CL-B3-ROLL-PB2V", "Roll helix angle at the trimmed stall", calc="CALC-B3-ROLL", output="pb2v", unit="-",
          limit=(">=", "ASM-B3-PB2V-MIN"), how="Twin at 1.1 Vs: full-stick roll, FC roll rate; pb/2V = p b / 2V.")
kit.claim("CL-B3-ROLL-T60", "Time to 60 deg bank at the stall", calc="CALC-B3-ROLL", output="t60_s", unit="s",
          limit=("<=", 1.3), how="Twin roll test, FC log.", note="MIL-F-8785C class I, cat. C, Level 1: 1.3 s")


@kit.calc("CALC-B3-CRUISE-AUTH", title="Elevon authority at 1.3 Vs (trim share, roll rate, motor-out roll)",
          cites=["SRC-B3-AVL"],
          inputs={**CS_IN, "x_aft": "CL-B3-CG-AFT", "x_fwd": "CL-B3-CG-FWD", "vt": "CL-B3-VT-TRIM",
                  "travel": P + "wing.elevon.deflection_deg", "Cld": "CL-B3-CLDA", "Clp": "CL-B3-CLP",
                  "M_out": "CL-E1-MOTOROUT-ROLL"},
          units={**CS_U, "x_aft": "m", "x_fwd": "m", "vt": "m/s", "travel": "deg"},
          equation="AVL trim at CL(Vt) for the aft and forward CG ; use = max|delta| / travel ; da = travel - max|delta| ;"
                   " p = |Cld| eta da / |Clp| 2V/b ; M_roll = |Cld| eta da q S b ; ratio = M_roll / M_motor-out")
def cruise_auth(b, c, ef, yin, yout, fy, fh, fle, fte, zref, xnp_a, xnp, dcm, eta, tab, m, g, rho, S, x_aft, x_fwd,
                vt, travel, Cld, Clp, M_out):
    CL = 2 * m * g / (rho * vt * vt * S)
    ds = {}
    for tag, x in (("aft", x_aft), ("fwd", x_fwd)):
        gg = _g(b, c, ef, yin, yout, fy, fh, fle, fte, x + (xnp_a - xnp), zref, egain=eta)
        ds[tag] = AV.trim_sweep(gg, [CL], -dcm, LAT_TRIM)[0]["d1"]
    dmax = max(abs(v) for v in ds.values())
    da = travel[1] - dmax
    q = 0.5 * rho * vt * vt
    p = abs(Cld) * eta * da / abs(Clp) * 2 * vt / b
    M = abs(Cld) * eta * da * q * S * b
    d_hold = M_out / (abs(Cld) * eta * q * S * b)
    return {"CL": CL, "delta_aft": ds["aft"], "delta_fwd": ds["fwd"], "trim_use": dmax / travel[1], "da_deg": da,
            "p_degs": math.degrees(p), "M_roll_Nm": M, "motorout_ratio": M / M_out, "motorout_delta_deg": d_hold}


kit.claim("CL-B3-TRIM-USE-VT", "Elevon trim share of travel at 1.3 Vs, worst CG", calc="CALC-B3-CRUISE-AUTH",
          output="trim_use", unit="-", limit=("<=", P + "requirements.elevon_trim_travel_max"),
          verifies=["R-CRUISE-AUTHORITY"], how="Twin/aircraft FBWA at 1.3 Vs, CG on each mark: servo output (FC log).")
kit.claim("CL-B3-ROLL-RATE-VT", "Steady roll rate at 1.3 Vs with the travel left after trim", calc="CALC-B3-CRUISE-AUTH",
          output="p_degs", unit="deg/s", limit=(">=", P + "requirements.roll_rate_min_degs"),
          verifies=["R-CRUISE-AUTHORITY"], how="Twin at 1.3 Vs: full-stick roll in MANUAL, FC roll rate (H2).")
kit.claim("CL-B3-MOTOROUT-ROLL-RATIO", "Elevon roll moment / cruise motor-out roll torque at 1.3 Vs",
          calc="CALC-B3-CRUISE-AUTH", output="motorout_ratio", unit="-", limit=(">=", "ASM-B3-AUTH-RATIO"),
          how="SITL motor-failure test (F4), then twin: cut one diagonal pair in FBWA at altitude, roll held.",
          note="CR-E1-04: E1's 0.22 N m (diagonal pair left running, unbalanced prop torque)")


@kit.calc("CALC-B3-ELEVON-AREA", title="Elevon area fraction", inputs={"S": "CL-A1-WING-AREA",
          "f": P + "wing.elevon.chord_frac", "yin": P + "wing.elevon.inboard_y_m",
          "yout": P + "wing.elevon.outboard_y_m", "c": P + "wing.chord_m"},
          units={"S": "m2", "yin": "m", "yout": "m", "c": "m"}, equation="A = 2 (span_in + span_out) f c ; frac = A/S",
          output="frac")
def elevon_area(S, f, yin, yout, c):
    return 2 * ((yin[1] - yin[0]) + (yout[1] - yout[0])) * f * c / S


kit.claim("CL-B3-ELEVON-FRAC-MAX", "Elevon area within the upper bound", calc="CALC-B3-ELEVON-AREA", output="frac",
          unit="-", limit=("<=", 0.25), verifies=["R-ELEVON-AREA"],
          how="Measure the cut panels; freeze after the twin's trim and roll tests.")
kit.claim("CL-B3-ELEVON-FRAC-MIN", "Elevon area above the lower bound", calc="CALC-B3-ELEVON-AREA", output="frac",
          unit="-", limit=(">=", 0.15), verifies=["R-ELEVON-AREA"], how="As CL-B3-ELEVON-FRAC-MAX.")


# ---------------------------------------------------------------------------------------------- lateral-directional
LATIN = {**GEO, "zref": P + "cg.z_target_m", "n": P + "propulsion.n_motors",
         "D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
         "x_tube": P + "fins.tube.x_m", "tube_od": P + "fins.tube.od_m", "tube_l": P + "fins.tube.length_m",
         "mot_d": P + "propulsion.motor_diameter_m", "mot_l": P + "propulsion.motor_length_m",
         "x_mount": P + "propulsion.stations.x_mount_m", "cna": "ASM-B3-PROP-CNA", "cd": "ASM-B3-CD-CYL",
         "S": "CL-A1-WING-AREA", "pod": P + "pod.size_m", "kyaw": "ASM-B3-POD-K-YAW",
         "m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3"}
LATU = {**GEOU, "zref": "m", "D": "m", "x_prop": "m", "x_tube": "m", "tube_od": "m", "tube_l": "m",
        "mot_d": "m", "mot_l": "m", "x_mount": "m", "S": "m2", "pod": "m", "m": "kg", "g": "m/s2", "rho": "kg/m3"}


def lat_terms(x_cg, CL, b, c, ef, yin, yout, fy, fh, fle, fte, zref, n, D, x_prop, x_tube, tube_od, tube_l, mot_d,
              mot_l, x_mount, cna, cd, S, pod, kyaw, **_):
    """Cn_beta build-up about x_cg at CL: AVL wing + fins, Ribner props, tube/motor cross-flow drag, Munk pod."""
    d = AV.derivatives_cl(_g(b, c, ef, yin, yout, fy, fh, fle, fte, x_cg, zref), CL, LAT)
    p = FM.prop_terms(n, D, x_prop, x_cg, S, c, b, cna, 1.0)
    x_can = x_mount - tube_od / 2 - mot_l / 2                 # motor can centre: mount face at the tube front
    items = [(2 * cd * tube_od * tube_l, x_tube), (n * cd * mot_d * mot_l, x_can)]
    dt = FM.drag_items_dCnb(items, x_cg, S, b)
    dpod = -2 * kyaw * 0.6 * pod[0] * pod[1] * pod[2] / (S * b)
    return {"Cnb_avl": d["Cnb"], "Cnb_props": p["dCnb"], "Cnb_tubes": dt, "Cnb_pod": dpod,
            "Cnb": d["Cnb"] + p["dCnb"] + dt + dpod, "Clb": d["Clb"], "CYb": d["CYb"] + p["dCYb"], "Cnr": d["Cnr"],
            "Clr": d["Clr"], "Cnp": d["Cnp"], "CYp": d["CYp"], "CYr": d["CYr"], "Clp": d["Clp"], "Cma": d["Cma"],
            "Cmq": d["Cmq"], "CLa": d["CLa"], "alpha": d["Alpha"]}


@kit.calc("CALC-B3-LATDIR", title="Directional stability at 1.3 Vs, aft CG (R-DIRECTIONAL)",
          inputs={**LATIN, "x_aft": "CL-B3-CG-AFT", "x_t": "CL-B3-CG-TARGET", "vt": "CL-B3-VT-TRIM",
                  "vc": P + "performance.cruise_ms"},
          units={**LATU, "x_aft": "m", "x_t": "m", "vt": "m/s", "vc": "m/s"},
          assumes=["ASM-B3-PROP-CNA", "ASM-B3-CD-CYL", "ASM-B3-POD-K-YAW"],
          cites=["SRC-B3-AVL", "SRC-B3-RIBNER", "SRC-B3-MUNK"],
          equation="Cnb = Cnb_AVL(wing+fins, elevons 0) + Cnb_props (Ribner) + Cnb_tubes/motors (drag rotation) "
                   "+ Cnb_pod (Munk) ; at CL(1.3 Vs) about the aft limit, and at CL(cruise) about the target")
def latdir(x_aft, x_t, vt, vc, **kw):
    q = lambda V: 0.5 * kw["rho"] * V * V   # noqa: E731
    W = kw["m"] * kw["g"]
    a = lat_terms(x_aft, W / (q(vt) * kw["S"]), **kw)
    t = lat_terms(x_t, W / (q(vc) * kw["S"]), **kw)
    out = {k: v for k, v in a.items()}
    out["Cnb_cruise_target"] = t["Cnb"]
    out["Cnb_avl_cruise_target"] = t["Cnb_avl"]
    return out


kit.claim("CL-B3-CNB", "Directional stability Cn_beta, 1.3 Vs, aft CG", calc="CALC-B3-LATDIR", output="Cnb",
          unit="1/rad", limit=(">=", P + "requirements.cnbeta_min"), verifies=["R-DIRECTIONAL"],
          assumes=["ASM-B3-PROP-CNA"],
          how="T-B3-YAW-DOUBLET: twin in FBWA, rudder-free yaw pulse (differential thrust); heading returns. "
              "Wind-tunnel-free check: hang the airframe on a vertical pivot at the CG in a car-top run.")
kit.claim("CL-B3-CNB-CRUISE", "Directional stability Cn_beta, cruise, CG target", calc="CALC-B3-LATDIR",
          output="Cnb_cruise_target", unit="1/rad", limit=(">=", P + "requirements.cnbeta_min"),
          how="As CL-B3-CNB at 16 m/s.")


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


@kit.calc("CALC-B3-MODES", title="Rigid-body modes at cruise speed (linear, props included)",
          assumes=["ASM-B3-PROP-CNA", "ASM-B3-CD0"],
          inputs={**LATIN, "xnp": "CL-B3-XNP", "x_t": "CL-B3-CG-TARGET", "m_basic": "CL-A3-MASS-BASIC",
                  "Ixx": "CL-A3-IXX", "Iyy": "CL-A3-IYY", "Izz": "CL-A3-IZZ", "V": P + "performance.cruise_ms",
                  "cd0": "ASM-B3-CD0", "e": P + "wing.oswald_e"},
          units={**LATU, "xnp": "m", "x_t": "m", "V": "m/s"},
          equation="Etkin small-perturbation 4x4 longitudinal (u,w,q,theta) and lateral (v,p,r,phi) state matrices "
                   "from the AVL derivatives at the cruise CL, CG target; Cma = -CLa SM (props included); "
                   "eigenvalues by Faddeev-LeVerrier + Durand-Kerner")
def modes(xnp, x_t, m_basic, Ixx, Iyy, Izz, V, cd0, e, **kw):
    m, g, rho, S, c, b = kw["m"], kw["g"], kw["rho"], kw["S"], kw["c"], kw["b"]
    q = 0.5 * rho * V * V
    CL = m * g / (q * S)
    lat = lat_terms(x_t, CL, **kw)
    k = m / m_basic
    Ixx, Iyy, Izz = Ixx * k, Iyy * k, Izz * k
    AR = b * b / S
    CD = cd0 + CL * CL / (math.pi * e * AR)
    CLa = lat["CLa"]
    Cma = -CLa * (xnp - x_t) / c
    U, qS = V, q * S
    Xu, Xw = -2 * CD * qS / (m * U), (CL - 2 * CL * CLa / (math.pi * e * AR)) * qS / (m * U)
    Zu, Zw = -2 * CL * qS / (m * U), -(CLa + CD) * qS / (m * U)
    Mw, Mq = Cma * qS * c / (Iyy * U), lat["Cmq"] * qS * c * c / (2 * U * Iyy)
    Alon = [[Xu, Xw, 0, -g], [Zu, Zw, U, 0], [0, Mw, Mq, 0], [0, 0, 1, 0]]
    Yv = lat["CYb"] * qS / (m * U)
    Yp, Yr = lat["CYp"] * qS * b / (2 * m * U), lat["CYr"] * qS * b / (2 * m * U)
    Lv, Lp, Lr = (lat["Clb"] * qS * b / (Ixx * U), lat["Clp"] * qS * b * b / (2 * Ixx * U),
                  lat["Clr"] * qS * b * b / (2 * Ixx * U))
    Nv, Np, Nr = (lat["Cnb"] * qS * b / (Izz * U), lat["Cnp"] * qS * b * b / (2 * Izz * U),
                  lat["Cnr"] * qS * b * b / (2 * Izz * U))
    Alat = [[Yv, Yp, Yr - U, g], [Lv, Lp, Lr, 0], [Nv, Np, Nr, 0], [0, 1, 0, 0]]
    elon, elat = _eig4(Alon), _eig4(Alat)
    out = {"CL": CL, "Cnb": lat["Cnb"], "eig_lon": [[round(z.real, 4), round(z.imag, 4)] for z in elon],
           "eig_lat": [[round(z.real, 4), round(z.imag, 4)] for z in elat]}
    cpx = sorted([z for z in elon if z.imag > 1e-6], key=lambda z: -abs(z))
    if cpx:
        out["sp_wn"], out["sp_zeta"] = abs(cpx[0]), -cpx[0].real / abs(cpx[0])
    else:
        out["sp_wn"], out["sp_zeta"] = max(abs(z) for z in elon), 1.0
    dr = [z for z in elat if z.imag > 1e-6]
    if dr:
        out["dr_wn"], out["dr_zeta"] = abs(dr[0]), -dr[0].real / abs(dr[0])
    else:
        out["dr_wn"], out["dr_zeta"] = 0.0, 1.0
    mr = max(z.real for z in elat)
    out["lat_max_real"] = mr
    out["lat_t2_s"] = min(999.0, math.log(2) / mr) if mr > 1e-9 else 999.0
    return out


kit.claim("CL-B3-SP-ZETA", "Short-period damping ratio, cruise", calc="CALC-B3-MODES", output="sp_zeta", unit="-",
          limit=(">=", "ASM-B3-ZETA-SP-MIN"), how="Twin: elevon doublet in MANUAL, pitch-rate overshoot.")
kit.claim("CL-B3-DR-ZETA", "Dutch-roll damping ratio, cruise", calc="CALC-B3-MODES", output="dr_zeta", unit="-",
          limit=(">=", "ASM-B3-ZETA-DR-MIN"), verifies=["R-DIRECTIONAL"],
          how="T-B3-YAW-DOUBLET: yaw pulse in FBWA, yaw-rate oscillation decays (FC log).")
kit.claim("CL-B3-LAT-T2", "Slowest lateral divergence (spiral), time to double", calc="CALC-B3-MODES",
          output="lat_t2_s", unit="s", limit=(">=", 4.0),
          how="Twin, hands-off in MANUAL at altitude: bank-angle drift after a roll pulse (FC log).",
          note="MIL-F-8785C spiral limit (>= 4 s to double, Level 3); 999 = no divergent lateral mode")


# ---------------------------------------------------------------------------------------------- hover
HOV_IN = {"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "dl": P + "propulsion.download_factor",
          "split": "CL-A3-HOVER-SPLIT", "tmax": P + "propulsion.thrust_max_per_motor_kg",
          "sag": P + "propulsion.voltage_sag", "y": P + "propulsion.stations.y_m", "z": P + "propulsion.stations.z_m",
          "Qh": "CL-B4-HOVER-Q", "swirl": "CL-B4-YAW", "cant": P + "propulsion.stations.cant_deg",
          "dfrac": "ASM-B3-HOVER-DIFF", "Ixx": "CL-A3-IXX", "Iyy": "CL-A3-IYY", "Izz": "CL-A3-IZZ",
          "m_basic": "CL-A3-MASS-BASIC", "rho": P + "env.rho_kgm3", "Vw": P + "requirements.wind_limit_ms",
          "S": "CL-A1-WING-AREA", "c": P + "wing.chord_m", "b": P + "wing.span_m", "x_t": "CL-B3-CG-TARGET",
          "cn90": "ASM-B3-CN90", "xcp": "ASM-B3-XCP-HOVER", "fc": P + "fins.chord_m", "fh": P + "fins.half_height_m",
          "fle": P + "fins.le_x_m", "asym": "ASM-B3-GUST-ASYM", "fac": P + "requirements.hover_ctrl_factor",
          "amin": P + "requirements.hover_ctrl_accel_min"}
HOV_U = {"m": "kg", "g": "m/s2", "tmax": "kg", "y": "m", "z": "m", "cant": "deg", "rho": "kg/m3", "Vw": "m/s",
         "S": "m2", "c": "m", "b": "m", "x_t": "m", "fc": "m", "fh": "m", "fle": "m", "amin": "rad/s2"}


@kit.calc("CALC-B3-HOVER", title="Hover control power vs 5 m/s wind (R-HOVER-AUTHORITY)", inputs=HOV_IN, units=HOV_U,
          assumes=["ASM-B3-CN90", "ASM-B3-XCP-HOVER", "ASM-B3-GUST-ASYM", "ASM-B3-HOVER-DIFF"],
          equation="dT = min(dfrac T_h, T_lower, Tmax sag - T_upper) per motor ; M_pitch = 2 dT (2 z) ; "
                   "M_roll = 4 dT y ; M_yaw = 4 dT (kq swirl + r sin cant), kq = Q_h/T_h (B4) ; disturbance: "
                   "q S CN90 arm (pitch), fins (roll), asym F b/4 (yaw) ; cant_req: smallest cant meeting both "
                   "the accel floor and fac x disturbance on yaw")
def hover(m, g, dl, split, tmax, sag, y, z, Qh, swirl, cant, dfrac, Ixx, Iyy, Izz, m_basic, rho, Vw, S, c, b, x_t,
          cn90, xcp, fc, fh, fle, asym, fac, amin):
    k = m / m_basic
    z_cg = z * (split - 1) / (split + 1)        # CG height implied by the A3 split (lever balance)
    dist = FM.hover_disturbance(rho, Vw, S, c, x_t, cn90, xcp, 2 * fc * 2 * fh, fle + fc / 2, asym, b)
    kq_iso = Qh / (m * g * dl / 4)
    kq = kq_iso * swirl                           # effective reaction-torque arm after fin swirl recovery (B4)
    II = (Ixx * k, Iyy * k, Izz * k)
    dd = (dist["M_pitch"], dist["M_roll"], dist["M_yaw"])
    Tmx = tmax * g * sag
    r = FM.hover_authority(m, g, dl, split, Tmx, y, z, z_cg, kq, cant, II, dd, dfrac)
    r.update({f"dist_{a}_Nm": dist[f"M_{a}"] for a in ("pitch", "roll", "yaw")})
    r["kq_iso_m"], r["kq_eff_m"] = kq_iso, kq
    r0 = FM.hover_authority(m, g, dl, split, Tmx, y, z, z_cg, kq, 0.0, II, dd, dfrac)
    r["ratio_yaw_nocant"], r["acc_yaw_nocant_rads2"] = r0["ratio_yaw"], r0["acc_yaw_rads2"]
    rf = FM.hover_authority(m, g, dl, split, Tmx, y, z, z_cg, kq, cant, II, dd, 1.0)
    r["ratio_yaw_fulldiff"], r["acc_yaw_fulldiff_rads2"], r["dT_full_N"] = rf["ratio_yaw"], rf["acc_yaw_rads2"], rf["dT_N"]
    # smallest cant that meets both yaw criteria with the capped differential
    rr = math.hypot(y, z)
    M_need = max(amin * II[0], fac * dist["M_yaw"])
    s = (M_need / (4 * r["dT_N"]) - kq) / rr
    r["cant_req_deg"] = math.degrees(math.asin(min(1.0, max(0.0, s))))
    r["M_yaw_need_Nm"] = M_need
    r["yaw_iso_30pct_Nm"] = 4 * dfrac * (m * g * dl / 4) * kq_iso     # isolated props, no swirl, no cant (E1 basis)
    return r


for ax in ("pitch", "roll", "yaw"):
    kit.claim(f"CL-B3-HOVER-{ax.upper()}-RATIO", f"Hover {ax} control power / 5 m/s wind moment", calc="CALC-B3-HOVER",
              output=f"ratio_{ax}", unit="-", limit=(">=", P + "requirements.hover_ctrl_factor"),
              verifies=["R-HOVER-AUTHORITY", "R-WIND"],
              how="T-B3-HOVER-WIND: twin, then aircraft, hover in 5 m/s; no motor output above 85 % or below 10 % (RCOU).")
    kit.claim(f"CL-B3-HOVER-{ax.upper()}-ACCEL", f"Hover {ax} angular acceleration, 30 % differential",
              calc="CALC-B3-HOVER", output=f"acc_{ax}_rads2", unit="rad/s2",
              limit=(">=", P + "requirements.hover_ctrl_accel_min"), verifies=["R-HOVER-AUTHORITY"],
              how="Hover step inputs (twin, then aircraft): peak angular acceleration from the FC gyro log.")
kit.claim("CL-B3-HOVER-CANT-REQ", "Motor cant needed for hover yaw at 30 % differential", calc="CALC-B3-HOVER",
          output="cant_req_deg", unit="deg", limit=("<=", P + "propulsion.stations.cant_deg"),
          verifies=["R-HOVER-AUTHORITY"], how="Bench yaw torque on a turntable with canted mounts; hover yaw steps (H2).")


@kit.calc("CALC-B3-HOVER-TRIM", title="Hover pitch-trim share", inputs={"split": "CL-A3-HOVER-SPLIT"},
          equation="share of the pitch differential used by trim = (s - 1)/2", output="use")
def hover_trim_use(split):
    return (split - 1) / 2


@kit.calc("CALC-B3-SPLIT-LIMIT", title="Allowed hover trim share", inputs={"smax": P + "requirements.hover_split_max"},
          equation="(s_max - 1)/2", output="use")
def split_limit(smax):
    return (smax - 1) / 2


kit.claim("CL-B3-SPLIT-LIMIT", "Allowed hover trim share", calc="CALC-B3-SPLIT-LIMIT", output="use", unit="-",
          how="From requirements.hover_split_max (D-18); F4 checks motor outputs in a hover log.")
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
          how="Tuft or ribbon on the elevon in a tethered hover: if it does not stream, the elevons give no hover authority.",
          note="Positive: the elevons sit outside the props' contracted wash (B4 CL-B4-ELEVON-HOVER agrees), so hover "
               "control is by motors only")


# ---------------------------------------------------------------------------------------------- transition
@kit.calc("CALC-B3-TRANSITION", title="Quasi-steady transition pitch balance",
          assumes=["ASM-B3-CN90", "ASM-B3-CD0", "ASM-B3-PROP-CNA", "ASM-B3-ELEVON-TRANS", "ASM-B3-ELEVON-POST"],
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "S": "CL-A1-WING-AREA", "c": P + "wing.chord_m", "b": P + "wing.span_m", "x_t": "CL-B3-CG-TARGET",
                  "x_fwd": "CL-B3-CG-FWD", "xnp": "CL-B3-XNP", "cm_np_thin": "CL-B3-CM-NP-THIN",
                  "dcm": "CL-B2-DCM-VISC", "CLa": "CL-B3-CLA", "a0": "CL-B3-ALPHA0", "clmax": "CL-B3-CLMAX-TRIM",
                  "cd0": "ASM-B3-CD0", "e": P + "wing.oswald_e", "cn90": "ASM-B3-CN90", "n": P + "propulsion.n_motors",
                  "D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "cna": "ASM-B3-PROP-CNA", "tmax": P + "propulsion.thrust_max_per_motor_kg",
                  "sag": P + "propulsion.voltage_sag", "z": P + "propulsion.stations.z_m",
                  "dl": P + "propulsion.download_factor", "vc": P + "performance.cruise_ms",
                  "CLd": "CL-B3-CLD", "Cmd_ref": "CL-B3-CMD", "xref": P + "cg.x_target_m", "eta": "CL-B2-ELEVON-ETA",
                  "dp": "ASM-B3-ELEVON-TRANS", "fpost": "ASM-B3-ELEVON-POST"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2", "c": "m", "b": "m", "x_t": "m", "x_fwd": "m",
                 "xnp": "m", "a0": "deg", "D": "m", "x_prop": "m", "tmax": "kg", "z": "m", "vc": "m/s",
                 "xref": "m", "dp": "deg"},
          equation="level flight at V: T cos a = D, T sin a + L = W ; wing CP from Xnp (attached) to 0.5 c at 90 deg ; "
                   "props' normal force at x_prop ; use = |M_aero - M_elevon| / (2 dT 2z), dT = min(T/4, Tmax sag - T/4)")
def transition(m, g, rho, S, c, b, x_t, x_fwd, xnp, cm_np_thin, dcm, CLa, a0, clmax, cd0, e, cn90, n, D, x_prop,
               cna, tmax, sag, z, dl, vc, CLd, Cmd_ref, xref, eta, dp, fpost):
    AR = b * b / S
    k_ind = 1 / (math.pi * e * AR)
    out = {}
    for tag, x in (("target", x_t), ("fwd", x_fwd)):
        rows = []
        for V in sorted({0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, vc}):
            cmd = (Cmd_ref + CLd * (x - xref) / c) * eta
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
kit.test("T-B3-YAW-DOUBLET", "Twin FW yaw doublet", verifies=["CL-B3-CNB", "CL-B3-DR-ZETA"],
         procedure="Twin in FBWA at 1.3 Vs, 50 m AGL, CG on the aft mark: yaw pulse by differential thrust; heading and "
                   "sideslip return within 2 s, yaw-rate oscillation decays.")
kit.test("T-B3-HOVER-WIND", "Hover authority in wind",
         verifies=["CL-B3-HOVER-PITCH-RATIO", "CL-B3-HOVER-ROLL-RATIO", "CL-B3-HOVER-YAW-RATIO"],
         procedure="Tethered then free hover at 5 m/s measured wind; no motor output above 85 % or below 10 % (RCOU).")


if __name__ == "__main__":
    kit.write()
    res = {n["id"]: n.get("outputs") for n in kit.nodes.values() if n["type"] == "calculation"}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "sc_results.json").write_text(json.dumps(res, indent=1, default=str))
    print("wrote results/sc_results.json")
