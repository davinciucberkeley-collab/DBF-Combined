"""B3 stability and control: proof-chain claims for the K09-L quad tailsitter (R5: A1-R5 params; R4 model).

R5 re-run (A1-R5 forward, D-61 / D-62): every AVL run at the take-off CG height cg.z_target_m 0.0185 and the target
cg.x_target_m 0.0490; prop plane -0.0127 (D-61); B4 yaw factors 1.785 / 1.392; D6 losses 0.079 / 0.071; C2 torsion
11.9 / 24.1 Hz; B4's BEMT prop H-force as a hub term in the pitch-over (CALC-B3-TRANSITION) and B4's dH/di as a
cross-check of the Ribner slope (CALC-B3-PROP-AFT). The CG limits of record are the V1 ids in claims.verify.json
(CL-B3-V-CG-FWD, CL-B3-V-CG-AFT-ENV, CL-B3-V-XNP-ENV); every calculation here that needs a limit reads them.
CALC-B3-CG-LIMITS and CALC-B3-CG-CHECK (z = 0 range, D-59 pack stations) are retired.

R4 re-run: pod nose -0.130 / 0.225 m (D-47), pack nominal x -0.022 with per-pack stations (D-47, supersedes CR-B3-18),
prop plane -0.0077 (D-51), sag 0.851 (D-49), A3-R5 mass and inertia, B4 R3 hover-yaw factor 1.79 with the cant sized
on CL-B4-YAW-LOW 1.40 (CR-B4-13), D6 elevon effectiveness and free play in the trim, roll and transition margins
(CR-D6-08), F4's R4 crossovers in the torsion-mode loops and a sweep of the 11.7-14.9 Hz antisymmetric band (D-45).

R3 re-run (CR-A1-26): 7 deg cant (D-27), half-fins 0.21 m (D-26), pod 0.21 x 0.14 x 0.07 at -0.115 (D-25), prop
plane -0.0082 (D-28), pack nominal x -0.001 (D-24) on A3's R3 roll-up and inertia, B4's swirl factor. Added: the
Ribner prop normal force evaluated at the aft CG limit (CR-J1-11, CALC-B3-PROP-AFT) and the hover rate loops with
the first wing torsion modes (CR-C2-03 / D-45, CALC-B3-HOVER-FLEX, model in hover_loop.py).

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
import hover_loop as HL  # noqa: E402

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
               "Fraction of the pitch moment at the 30 % differential cap (R-HOVER-AUTHORITY) that the trim part of "
               "the forward transition may use: the largest |M_aero| along the flown pitch-over (CALC-B3-TRANS-TD), "
               "not the Iyy theta_dd transient, which belongs to the rate reserve",
               basis="Design round 2026-11-14 (B3.md §2.3, A1.md D-149), value unchanged: the 0.40 kept back is the "
                     "pitch-axis reserve for a 2 m/s vertical gust at the worst quasi-steady transition point (forward "
                     "CG, 11 m/s: 0.353 of the cap) plus the R-HOVER-AUTHORITY 2.0 rad/s2 rate floor on Iyy (0.068): "
                     "0.42 (team/B3/results/round1114.json reserve_at_qs_worst; 3 m/s gust: 0.60). Roll and yaw "
                     "already hold their own share through the per-axis 30 % cap, so the earlier 'roll/yaw mixing' "
                     "wording is retired. B3 choice", value=0.6, unit="-")
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
# hover loop with the wing torsion modes (CR-C2-03, D-45)
kit.source("SRC-B3-MIL9490", "MIL-F-9490D Flight control systems, general specification (1975)", "standard",
           url="http://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-F/MIL-F-9490D_6264/",
           where="3.1.3.6.1 stability margins: 6 dB gain, 45 deg phase at the lowest mode frequencies")
kit.assumption("ASM-B3-STATION-IYY", "Fin station pitch inertia about the spar, per side",
               "Motors, mounts, props, ESCs and the two half-fins of one station about the spar axis",
               basis="team/C2/CHANGE-REQUESTS.md CR-C2-03: ~0.0125 kg m2 per side (C2 modal model)", value=0.0125,
               unit="kg m2", status="UNVERIFIED")
kit.assumption("ASM-B3-TORSION-HIGH", "Wing torsion mode frequencies, high corner [antisymmetric, symmetric]",
               "Upper end of C2's frequency bands (GJ 45 N m2); the low corners are C2's claims",
               basis="team/C2/CHANGE-REQUESTS.md CR-C2-03: antisymmetric 11.7-14.9 Hz, symmetric 21-27 Hz",
               value=[14.9, 27.0], unit="Hz", status="UNVERIFIED")
kit.assumption("ASM-B3-FLEX-ZETA", "Structural damping of the torsion modes", "Modal damping ratio, foam/CF wing "
               "with taped skin", basis="0.02 is the low end for bonded foam-core/CF structures (1-3 %); T-C2-TAP-TEST "
               "measures it", value=0.02, unit="-", status="UNVERIFIED")
kit.assumption("ASM-B3-MOTOR-TAU", "Motor + 11 in prop thrust time constant", "First-order lag from ESC command to "
               "thrust at hover", basis="X3108S-class motor with an 11x5.5 prop: 30-50 ms typical for 10-12 in props on "
               "BLHeli_S without active braking; 0.04 s used", value=0.04, unit="s", status="UNVERIFIED")
kit.assumption("ASM-B3-LOOP-DELAY", "Rate-loop transport delay", "Sample, compute and DShot output delay",
               basis="400 Hz main loop (2.5 ms) + DShot frame and ESC (~1.5 ms)", value=0.004, unit="s")
kit.assumption("ASM-B3-FSW-FILT", "Gyro low-pass and D-term filter [INS_GYRO_FILTER, Q_A_RAT_*_FLTD]",
               "2nd-order gyro filter and 1st-order D filter cut-offs", basis="subsystems/flight-software/K09L.param "
               "(F4): INS_GYRO_FILTER 40, Q_A_RAT_PIT_FLTD 32", value=[40.0, 32.0], unit="Hz", status="PROPOSED")
kit.assumption("ASM-B3-FSW-PID-PIT", "Hover pitch rate PID shape [P, I, D]", "F4's starting gains; only the ratios "
               "matter here (the gain is scaled to the crossover)", basis="K09L.param Q_A_RAT_PIT_P/I/D",
               value=[0.08, 0.08, 0.002], unit="-", status="PROPOSED")
kit.assumption("ASM-B3-FSW-PID-YAW", "Hover yaw rate PID shape [P, I, D]", "F4's starting gains (no D)",
               basis="K09L.param Q_A_RAT_YAW_P/I", value=[0.40, 0.04, 0.0], unit="-", status="PROPOSED")
kit.assumption("ASM-B3-XOVER", "Hover rate-loop crossovers [pitch, yaw]", "F4's predicted crossovers at the "
               "starting gains", basis="team/F4/claims.json CL-F4-XOVER-PIT 2.61 Hz, CL-F4-XOVER-YAW 1.01 Hz (F4 R4, "
               "rigid body at the 21.1 N thrust limit, so upper bounds). Copied, not linked: CALC-F4-XOVER reads "
               "CL-B3-XOVER-MAX-*, so a link would close a loop in the graph. R3 used 4.0 / 1.8 Hz",
               value=[2.6, 1.0], unit="Hz", status="PROPOSED")
kit.assumption("ASM-B3-SLOP-TRIM-FRAC", "Share of the elevon free play charged to trim",
               "Fraction of CL-D6-SLOP (worst-case band) the servo must add to hold a steady trim deflection",
               basis="steady hinge moment holds the surface on one side of the play band and T-D6-THROW sets the "
                     "servo neutral at the band centre, so trim costs half the band; roll authority is charged the "
                     "full band (reversal across the play). B3 choice; full band in the sensitivity (S-AND-C.md)",
               value=0.5, unit="-")
kit.assumption("ASM-B3-GM-MIN", "Loop gain margin minimum", "Gain margin at every -180 deg crossing, structural "
               "modes included", basis="MIL-F-9490D 3.1.3.6.1", value=6.0, unit="dB", cites=["SRC-B3-MIL9490"])
kit.assumption("ASM-B3-PM-MIN", "Loop phase margin minimum", "Phase margin at every 0 dB crossing",
               basis="MIL-F-9490D 3.1.3.6.1", value=45.0, unit="deg", cites=["SRC-B3-MIL9490"])

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


def eff_mech(V, loss_o, loss_i, va):
    """D6 elevon effectiveness (panel twist + rod lag, CR-D6-08). The lag is proportional to the hinge moment, so the
    loss fraction scales with q: 1 - max(loss_out, loss_in) (V/VA)^2."""
    return 1.0 - max(loss_o, loss_i) * (V / va) ** 2


def critical_section(geo, xref_eff, zref, eta, dcm, table, cls=CLS, eff=1.0):
    """Trimmed CLmax by the critical-section method (B2's method, WING-AERO.md): AVL trims Cm + dcm = 0 about
    xref_eff at each CL with the elevon in physical degrees (gain eta); the first strip whose cl reaches its local
    clmax (table at that strip's deflection: elevon strips at the trim deflection, others at 0) sets CLmax.
    eff (D6 mechanical effectiveness): AVL sees only the product gain x deflection, so the commanded deflection is
    the AVL value / eff with alpha and the strip loads unchanged (exact in the linear lattice); the clmax table is
    read at the surface's mean deflection, which is the AVL value (the panel lags the servo by the twist)."""
    g = _g(**geo, xref=xref_eff, zref=zref, egain=eta)
    rows = AV.trim_sweep(g, cls, -dcm, LAT_TRIM)
    ds, cs = [r[0] for r in table], [r[1] for r in table]
    yin, yout = geo["yin"], geo["yout"]

    def in_el(y):
        return yin[0] <= y <= yin[1] or yout[0] <= y <= yout[1]

    prev, hist = None, []
    for r in rows:
        d1 = r["d1"] / eff
        lim0 = _interp(0.0, ds, cs)
        limd = _interp(r["d1"], ds, cs)
        ratio, yfirst = max((s[2] / (limd if in_el(s[0]) else lim0), s[0]) for s in r["strips"])
        h = {"CL": r["CL"], "alpha": r["alpha"], "d1": d1, "ratio": ratio, "y": yfirst}
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
         "m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "S": "CL-A1-WING-AREA",
         "lo": "CL-D6-EFF-LOSS-OUT", "li": "CL-D6-EFF-LOSS-IN", "va": "ASM-F4-VA-SCHED", "slop": "CL-D6-SLOP",
         "vmax": P + "requirements.stall_max_ms"}
CS_U = {**GEOU, "zref": "m", "xnp_a": "m", "xnp": "m", "m": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2",
        "va": "m/s", "slop": "deg", "vmax": "m/s"}


def _cs_at(x, geo, zref, xnp_a, xnp, eta, dcm, tab, m, g, rho, S, eff=1.0):
    """Critical section at CG x. AVL has no props or pod: the reference is shifted by (Xnp_aero - Xnp) so the AVL
    model has the whole aircraft's static margin. eff: D6 mechanical effectiveness at the stall speed."""
    r = critical_section(geo, x + (xnp_a - xnp), zref, eta, dcm, tab, eff=eff)
    r["vs"] = FM.stall_speed(m, g, rho, S, r["CLmax"])
    return r


def _crossing(xs, ys, lim):
    """Largest x (xs ascending) at which ys first exceeds lim, linear between grid points; None if never."""
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if y0 <= lim < y1:
            return x0 + (lim - y0) * (x1 - x0) / (y1 - y0)
    return None if ys[0] > lim else xs[-1]


# CALC-B3-CG-LIMITS (R0-R4, planform fins) is retired at R5: the CG limits of record are B3's V1 claims
# (verify_asdesigned.py: CL-B3-V-CG-FWD, CL-B3-V-CG-AFT-ENV, CL-B3-V-XNP-ENV; D-62), which call this function with the CAD
# fins and the CG height. CL-B3-CG-FWD / -AFT / -TARGET survive only as forwarding aliases in claims.verify.json.
def cg_limits(b, c, ef, yin, yout, fy, fh, fle, fte, zref, xnp_a, xnp, dcm, eta, tab, m, g, rho, S, lo, li, va, slop,
              vmax, sm_min, travel, tfrac, kslop):
    geo = dict(zip(GKEYS, (b, c, ef, yin, yout, fy, fh, fle, fte)))
    e_st = eff_mech(vmax, lo, li, va)
    rows = []
    for sm in SM_GRID:
        r = _cs_at(xnp - sm * c, geo, zref, xnp_a, xnp, eta, dcm, tab, m, g, rho, S, eff=e_st)
        rows.append([round(sm, 3), round(xnp - sm * c, 5), round(r["CLmax"], 4), round(r["delta"], 2),
                     round(r["alpha"], 2), round(r["vs"], 3), round(r["y_first"], 3)])
    sms = [r[0] for r in rows]
    budget = tfrac * travel[1] - kslop * slop
    sm_trim = _crossing(sms, [-r[3] for r in rows], budget)
    # sensitivities: no D6 loss and no free play (R3 basis); full play band charged to trim
    r3 = [_crossing(sms, [-r[3] * e_st for r in rows], tfrac * travel[1]),
          _crossing(sms, [-r[3] for r in rows], tfrac * travel[1] - slop)]
    x_fwd_r3basis, x_fwd_fullslop = [None if s_ is None else xnp - s_ * c for s_ in r3]
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
            "trim_budget_deg": budget, "binding": "stall" if sm_fwd == sm_stall else "trim", "eff_stall": e_st,
            "x_fwd_no_d6": x_fwd_r3basis, "x_fwd_full_slop": x_fwd_fullslop,
            "columns": ["SM", "x_cg m", "CLmax_trim", "elevon deg", "alpha deg", "Vs m/s", "y first stall m"],
            "table": rows}



@kit.calc("CALC-B3-PROP-AFT", title="Ribner prop normal force at the aft CG limit (CR-J1-11)",
          assumes=["ASM-B3-PROP-CNA", "ASM-B3-UPWASH"], cites=["SRC-B3-RIBNER", "SRC-B3-PERKINS"],
          inputs={"n": P + "propulsion.n_motors", "D": P + "propulsion.prop_diameter_m",
                  "x_prop": P + "propulsion.stations.x_prop_plane_m", "x_aft": "CL-B3-V-CG-AFT-ENV", "xnp": "CL-B3-XNP",
                  "xnp_a": "CL-B3-XNP-AERO", "CLa": "CL-B3-CLA", "S": "CL-A1-WING-AREA", "c": P + "wing.chord_m",
                  "b": P + "wing.span_m", "cna": "ASM-B3-PROP-CNA", "up": "ASM-B3-UPWASH", "vt": "CL-B3-VT-TRIM",
                  "rho": P + "env.rho_kgm3", "m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2",
                  "ld": P + "performance.ld_cruise", "dhdi": "CL-B4-SIM-DH-DI", "v_h": "ASM-B3-B4-INC-V"},
          units={"D": "m", "x_prop": "m", "x_aft": "m", "xnp": "m", "xnp_a": "m", "S": "m2", "c": "m", "b": "m",
                 "vt": "m/s", "rho": "kg/m3", "m": "kg", "g": "m/s2", "dhdi": "N/rad", "v_h": "m/s"},
          equation="arm = x_aft - x_prop ; dCma_p = n cna A/S up arm/c ; dCnb_p = -n cna A/S arm/b (per rad, about "
                   "the aft CG) ; N_p = n cna A q per rad at 1.3 Vs ; Tc = (W/(L/D))/n / (rho V^2 D^2) (light loading "
                   "check) ; SM at the aft limit without the props = SM_min + (Xnp_props - Xnp)/c ; "
                   "B4 cross-check: cna_B4 = (dH/di) / (q(V_h) A), Xnp shift with cna_B4")
def prop_aft(n, D, x_prop, x_aft, xnp, xnp_a, CLa, S, c, b, cna, up, vt, rho, m, g, ld, dhdi, v_h):
    p = FM.prop_terms(n, D, x_prop, x_aft, S, c, b, cna, up)
    A = math.pi * D * D / 4
    q = 0.5 * rho * vt * vt
    T1 = m * g / ld / n
    p_np = FM.prop_terms(n, D, x_prop, xnp_a, S, c, b, cna, up)
    dx_props = -p_np["dCma"] / (CLa + p_np["dCLa"]) * c
    cna_b4 = dhdi / (0.5 * rho * v_h * v_h * A)
    p_b4 = FM.prop_terms(n, D, x_prop, xnp_a, S, c, b, cna_b4, up)
    dx_b4 = -p_b4["dCma"] / (CLa + p_b4["dCLa"]) * c
    return {"cna_b4": cna_b4, "cna_ratio_b4": cna_b4 / cna, "dxnp_props_b4_m": dx_b4,
            "xnp_shift_if_b4_m": dx_b4 - dx_props,
            "arm_m": x_aft - x_prop, "dCma_props": p["dCma"], "dCnb_props": p["dCnb"], "dCYb_props": p["dCYb"],
            "N_props_per_deg_N": n * cna * A * q * math.pi / 180, "Tc": T1 / (rho * vt * vt * D * D),
            "dxnp_props_m": dx_props, "sm_aft_if_props_ignored": (xnp - dx_props - x_aft) / c, "sm_aft": (xnp - x_aft) / c}


kit.claim("CL-B3-PROP-ARM-AFT", "Prop plane ahead of the aft CG limit", calc="CALC-B3-PROP-AFT", output="arm_m",
          unit="m", how="Follows from CL-B3-V-CG-AFT-ENV and the prop plane (D3 CAD).",
          note="J1 CL-J1-PROP-ARM 0.049 m at R1")
kit.claim("CL-B3-PROP-CNB-AFT", "Prop Ribner yaw term at the aft CG limit", calc="CALC-B3-PROP-AFT",
          output="dCnb_props", unit="1/rad", assumes=["ASM-B3-PROP-CNA"],
          how="Included in CL-B3-CNB; T-B3-YAW-DOUBLET with and without props (glide) brackets it.")
kit.claim("CL-B3-PROP-CNA-B4-RATIO", "Prop normal-force slope: B4 BEMT (dH/di at ASM-B3-B4-INC-V) / B3 Ribner assumption",
          calc="CALC-B3-PROP-AFT", output="cna_ratio_b4", unit="-",
          how="Car-top rig side force vs incidence (B4); < 1 means the Ribner NP term is conservative.")
kit.claim("CL-B3-PROP-XNP-B4-SHIFT", "Whole-aircraft NP shift if B4's BEMT slope replaced the Ribner assumption",
          calc="CALC-B3-PROP-AFT", output="xnp_shift_if_b4_m", unit="m",
          how="T-B3-TWIN-NP powered vs gliding; positive = NP aft (credit not taken in the CG limits).")
kit.claim("CL-B3-PROP-DXNP", "NP shift from the props (Ribner, all four)", calc="CALC-B3-PROP-AFT",
          output="dxnp_props_m", unit="m", assumes=["ASM-B3-PROP-CNA"],
          how="T-B3-TWIN-NP: NP from powered vs gliding trim-vs-CL slopes.")


# CALC-B3-CG-CHECK (A3 CG and the D-59 pack stations against the R4 range) is retired at R5: the pack cases are
# A1's CALC-A1-PACK-CASES on the D-62 bay against B3's V1 limits; B3 checks A3's CG and the params target in
# CALC-B3-V-CG / CALC-B3-V-NP-CL (claims.verify.json). Retired ids: CL-B3-CG-NOW-*, -CENTRED-*, -PACKS-*,
# CL-B3-PACK-SLIDE-LEFT, CL-B3-PACK-MASS-MAX/-MIN, ASM-B3-PACK-FWD-MOST.


# ---------------------------------------------------------------------------------------------- trimmed stall
@kit.calc("CALC-B3-STALL-TRIM", title="Trimmed CLmax, stall and transition speed at the gate",
          assumes=["ASM-B3-CLMAX-FLAP"], cites=["SRC-B3-AVL"],
          inputs={**CS_IN, "x_t": P + "cg.x_target_m", "x_aft": "CL-B3-V-CG-AFT-ENV", "x_fwd": "CL-B3-V-CG-FWD",
                  "k": P + "requirements.transition_factor"},
          units={**CS_U, "x_t": "m", "x_aft": "m", "x_fwd": "m"},
          equation="critical section at each CG -> CLmax_t, delta (commanded, / e_D6(Vs_max)) ; "
                   "Vs = sqrt(2 m g / (rho S CLmax_t)) ; Vt = k Vs at the forward limit (worst CG in the range)")
def stall_trim(b, c, ef, yin, yout, fy, fh, fle, fte, zref, xnp_a, xnp, dcm, eta, tab, m, g, rho, S, lo, li, va,
               slop, vmax, x_t, x_aft, x_fwd, k):
    geo = dict(zip(GKEYS, (b, c, ef, yin, yout, fy, fh, fle, fte)))
    out = {}
    e_st = eff_mech(vmax, lo, li, va)
    for tag, x in (("target", x_t), ("aft", x_aft), ("fwd", x_fwd)):
        r = _cs_at(x, geo, zref, xnp_a, xnp, eta, dcm, tab, m, g, rho, S, eff=e_st)
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
          inputs={**CS_IN, "x_t": P + "cg.x_target_m", "x_aft": "CL-B3-V-CG-AFT-ENV", "x_fwd": "CL-B3-V-CG-FWD",
                  "vs": "CL-B3-VS-TRIM", "vc": P + "performance.cruise_ms"},
          units={**CS_U, "x_t": "m", "x_aft": "m", "x_fwd": "m", "vs": "m/s", "vc": "m/s"},
          equation="CL = 2 m g/(rho V^2 S) ; AVL: alpha for CL, elevon (gain eta) for Cm + dcm = 0 about "
                   "x_cg + (Xnp_a - Xnp) ; commanded elevon = AVL / e_D6(V)")
def trim_sweep(b, c, ef, yin, yout, fy, fh, fle, fte, zref, xnp_a, xnp, dcm, eta, tab, m, g, rho, S, lo, li, va,
               slop, vmax, x_t, x_aft, x_fwd, vs, vc):
    # the cruise speed of record is always in the sweep (D-145 moved it 16 -> 17 m/s)
    speeds = [round(vs, 2)] + sorted(v for v in {13.0, 14.0, 15.0, 16.0, 18.0, 20.0, 22.0, 25.0, float(vc)}
                                     if v > vs + 0.05)
    cls = [2 * m * g / (rho * V * V * S) for V in speeds]
    rows = {}
    for tag, x in (("fwd", x_fwd), ("target", x_t), ("aft", x_aft)):
        gg = _g(b, c, ef, yin, yout, fy, fh, fle, fte, x + (xnp_a - xnp), zref, egain=eta)
        res = AV.trim_sweep(gg, cls, -dcm, LAT_TRIM)
        rows[tag] = [[V, round(r["CL"], 4), round(r["alpha"], 2), round(r["d1"] / eff_mech(V, lo, li, va), 2)]
                     for V, r in zip(speeds, res)]
    cruise = [r for r in rows["target"] if abs(r[0] - vc) < 1e-6][0]
    worst = min(r[3] for t in rows.values() for r in t)
    return {"columns": ["V m/s", "CL", "alpha deg", "elevon deg (- TE up)"], "table": rows,
            "delta_cruise": cruise[3], "alpha_cruise": cruise[2], "delta_worst": worst}


kit.claim("CL-B3-ELEVON-TRIM-CRUISE", "Elevon trim at cruise speed, CG target", calc="CALC-B3-TRIM-SWEEP",
          output="delta_cruise", unit="deg", how="FBWA level flight at the cruise speed (17 m/s, D-145): servo output vs neutral (FC log).")
kit.claim("CL-B3-ALPHA-CRUISE", "Body angle at cruise speed, CG target", calc="CALC-B3-TRIM-SWEEP",
          output="alpha_cruise", unit="deg", how="FC pitch angle in level flight at 16 m/s (no wind).")


# ---------------------------------------------------------------------------------------------- roll and cruise authority
@kit.calc("CALC-B3-ROLL", title="Roll authority at the trimmed stall",
          inputs={"Cld": "CL-B3-CLDA", "Clp": "CL-B3-CLP", "eta": "CL-B2-ELEVON-ETA",
                  "travel": P + "wing.elevon.deflection_deg", "d_stall": "CL-B3-DELTA-STALL", "vs": "CL-B3-VS-TRIM",
                  "b": P + "wing.span_m", "S": "CL-A1-WING-AREA", "rho": P + "env.rho_kgm3", "Ixx": "CL-A3-IXX",
                  "m_basic": "CL-A3-MASS-BASIC", "m": P + "requirements.mtow_gate_kg",
                  "lo": "CL-D6-EFF-LOSS-OUT", "li": "CL-D6-EFF-LOSS-IN", "va": "ASM-F4-VA-SCHED", "slop": "CL-D6-SLOP"},
          units={"travel": "deg", "d_stall": "deg", "vs": "m/s", "b": "m", "S": "m2", "rho": "kg/m3", "m": "kg",
                 "va": "m/s", "slop": "deg"},
          equation="da = travel - |delta_trim at CLmax| - slop ; pb/2V = |Cld| eta e_D6(Vs) da / |Clp| ; "
                   "tau = Ixx / (|Clp| q S b^2 / 2V) ; t60 from first-order roll response")
def roll_authority(Cld, Clp, eta, travel, d_stall, vs, b, S, rho, Ixx, m_basic, m, lo, li, va, slop):
    da = travel[1] - abs(d_stall) - slop
    pb2v = abs(Cld) * eta * eff_mech(vs, lo, li, va) * da / abs(Clp)
    V = vs
    p = pb2v * 2 * V / b
    q = 0.5 * rho * V * V
    Lp = abs(Clp) * q * S * b * b / (2 * V)
    tau = Ixx * m / m_basic / Lp
    t, phi = 0.0, 0.0
    while phi < math.radians(60) and t < 10:
        t += 0.001
        phi = p * (t - tau * (1 - math.exp(-t / tau)))
    return {"da_deg": da, "pb2v": pb2v, "p_degs": math.degrees(p), "tau_s": tau, "t60_s": t,
            "eff": eff_mech(vs, lo, li, va)}


kit.claim("CL-B3-DELTA-STALL", "Elevon trim at the trimmed CLmax, CG target", calc="CALC-B3-STALL-TRIM",
          output="delta_target", unit="deg", how="Twin slow flight: elevon output at the stall break (FC log).")
kit.claim("CL-B3-ROLL-PB2V", "Roll helix angle at the trimmed stall", calc="CALC-B3-ROLL", output="pb2v", unit="-",
          limit=(">=", "ASM-B3-PB2V-MIN"), how="Twin at 1.1 Vs: full-stick roll, FC roll rate; pb/2V = p b / 2V.")
kit.claim("CL-B3-ROLL-T60", "Time to 60 deg bank at the stall", calc="CALC-B3-ROLL", output="t60_s", unit="s",
          limit=("<=", 1.3), how="Twin roll test, FC log.", note="MIL-F-8785C class I, cat. C, Level 1: 1.3 s")


@kit.calc("CALC-B3-CRUISE-AUTH", title="Elevon authority at 1.3 Vs (trim share, roll rate, motor-out roll)",
          cites=["SRC-B3-AVL"],
          inputs={**CS_IN, "x_aft": "CL-B3-V-CG-AFT-ENV", "x_fwd": "CL-B3-V-CG-FWD", "vt": "CL-B3-VT-TRIM",
                  "travel": P + "wing.elevon.deflection_deg", "Cld": "CL-B3-CLDA", "Clp": "CL-B3-CLP",
                  "M_out": "CL-E1-MOTOROUT-ROLL", "kslop": "ASM-B3-SLOP-TRIM-FRAC"},
          units={**CS_U, "x_aft": "m", "x_fwd": "m", "vt": "m/s", "travel": "deg"},
          equation="AVL trim at CL(Vt) for the aft and forward CG ; e = e_D6(Vt) ; delta = delta_AVL / e ; "
                   "use = (max|delta| + k slop) / travel ; da = travel - max|delta| - slop ; "
                   "p = |Cld| eta e da / |Clp| 2V/b ; M_roll = |Cld| eta e da q S b ; ratio = M_roll / M_motor-out")
def cruise_auth(b, c, ef, yin, yout, fy, fh, fle, fte, zref, xnp_a, xnp, dcm, eta, tab, m, g, rho, S, lo, li, va,
                slop, vmax, x_aft, x_fwd, vt, travel, Cld, Clp, M_out, kslop):
    CL = 2 * m * g / (rho * vt * vt * S)
    e = eff_mech(vt, lo, li, va)
    ds = {}
    for tag, x in (("aft", x_aft), ("fwd", x_fwd)):
        gg = _g(b, c, ef, yin, yout, fy, fh, fle, fte, x + (xnp_a - xnp), zref, egain=eta)
        ds[tag] = AV.trim_sweep(gg, [CL], -dcm, LAT_TRIM)[0]["d1"] / e
    dmax = max(abs(v) for v in ds.values())
    da = travel[1] - dmax - slop
    q = 0.5 * rho * vt * vt
    p = abs(Cld) * eta * e * da / abs(Clp) * 2 * vt / b
    M = abs(Cld) * eta * e * da * q * S * b
    d_hold = M_out / (abs(Cld) * eta * e * q * S * b)
    return {"CL": CL, "eff": e, "delta_aft": ds["aft"], "delta_fwd": ds["fwd"],
            "trim_use": (dmax + kslop * slop) / travel[1], "da_deg": da, "p_degs": math.degrees(p), "M_roll_Nm": M,
            "motorout_ratio": M / M_out, "motorout_delta_deg": d_hold}


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
          inputs={**LATIN, "x_aft": "CL-B3-V-CG-AFT-ENV", "x_t": P + "cg.x_target_m", "vt": "CL-B3-VT-TRIM",
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
          inputs={**LATIN, "xnp": "CL-B3-XNP", "x_t": P + "cg.x_target_m", "m_basic": "CL-A3-MASS-BASIC",
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
kit.claim("CL-B3-LAT-T2", "Spiral time to double, params planform fins (R4 model; as designed: CL-B3-V-LAT-T2)",
          calc="CALC-B3-MODES", output="lat_t2_s", unit="s",
          how="Twin, hands-off in MANUAL at altitude: bank-angle drift after a roll pulse (FC log).",
          note="R5: no limit here. The params fin rectangle (0.0578 m2 per half) is not the build; R-SPIRAL is judged on "
               "the CAD fins (CL-B3-V-LAT-T2, -ZTOP). 999 = no divergent lateral mode")


# ---------------------------------------------------------------------------------------------- hover
HOV_IN = {"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "dl": P + "propulsion.download_factor",
          "split": "CL-A3-HOVER-SPLIT", "tmax": P + "propulsion.thrust_max_per_motor_kg",
          "sag": P + "propulsion.voltage_sag", "y": P + "propulsion.stations.y_m", "z": P + "propulsion.stations.z_m",
          "Qh": "CL-B4-HOVER-Q", "swirl": "CL-B4-YAW", "cant": P + "propulsion.stations.cant_deg",
          "dfrac": "ASM-B3-HOVER-DIFF", "Ixx": "CL-A3-IXX", "Iyy": "CL-A3-IYY", "Izz": "CL-A3-IZZ",
          "m_basic": "CL-A3-MASS-BASIC", "rho": P + "env.rho_kgm3", "Vw": P + "requirements.wind_limit_ms",
          "S": "CL-A1-WING-AREA", "c": P + "wing.chord_m", "b": P + "wing.span_m", "x_t": P + "cg.x_target_m",
          "cn90": "ASM-B3-CN90", "xcp": "ASM-B3-XCP-HOVER", "fc": P + "fins.chord_m", "fh": P + "fins.half_height_m",
          "fle": P + "fins.le_x_m", "asym": "ASM-B3-GUST-ASYM", "fac": P + "requirements.hover_ctrl_factor",
          "amin": P + "requirements.hover_ctrl_accel_min", "swirl_lo": "CL-B4-YAW-LOW"}
HOV_U = {"m": "kg", "g": "m/s2", "tmax": "kg", "y": "m", "z": "m", "cant": "deg", "rho": "kg/m3", "Vw": "m/s",
         "S": "m2", "c": "m", "b": "m", "x_t": "m", "fc": "m", "fh": "m", "fle": "m", "amin": "rad/s2"}


@kit.calc("CALC-B3-HOVER", title="Hover control power vs 5 m/s wind (R-HOVER-AUTHORITY)", inputs=HOV_IN, units=HOV_U,
          assumes=["ASM-B3-CN90", "ASM-B3-XCP-HOVER", "ASM-B3-GUST-ASYM", "ASM-B3-HOVER-DIFF"],
          equation="dT = min(dfrac T_h, T_lower, Tmax sag - T_upper) per motor ; M_pitch = 2 dT (2 z) ; "
                   "M_roll = 4 dT y ; M_yaw = 4 dT (kq swirl + r sin cant), kq = Q_h/T_h (B4) ; disturbance: "
                   "q S CN90 arm (pitch), fins (roll), asym F b/4 (yaw) ; cant_req: smallest cant meeting both "
                   "the accel floor and fac x disturbance on yaw, sized on B4's half-fin factor (CL-B4-YAW-LOW)")
def hover(m, g, dl, split, tmax, sag, y, z, Qh, swirl, cant, dfrac, Ixx, Iyy, Izz, m_basic, rho, Vw, S, c, b, x_t,
          cn90, xcp, fc, fh, fle, asym, fac, amin, swirl_lo):
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
    rs = FM.hover_authority(m, g, dl, split, Tmx, y, z, z_cg, kq_iso * swirl_lo, cant, II, dd, dfrac)   # low bracket
    r["ratio_yaw_low"], r["acc_yaw_low_rads2"] = rs["ratio_yaw"], rs["acc_yaw_rads2"]
    r0c = FM.hover_authority(m, g, dl, split, Tmx, y, z, z_cg, 0.0, cant, II, dd, dfrac)
    r["yaw_cant_share"] = r0c["M_yaw_Nm"] / r["M_yaw_Nm"]
    # smallest cant that meets both yaw criteria with the capped differential
    rr = math.hypot(y, z)
    M_need = max(amin * II[0], fac * dist["M_yaw"])
    s = (M_need / (4 * r["dT_N"]) - kq_iso * swirl_lo) / rr        # sized on the low (half-fin) factor, CR-B4-13
    r["cant_req_deg"] = math.degrees(math.asin(min(1.0, max(0.0, s))))
    s_n = (M_need / (4 * r["dT_N"]) - kq) / rr
    r["cant_req_nominal_deg"] = math.degrees(math.asin(min(1.0, max(0.0, s_n))))
    r["k_yaw_m"], r["k_yaw_low_m"] = kq + rr * math.sin(math.radians(cant)), kq_iso * swirl_lo + rr * math.sin(
        math.radians(cant))
    r["k_yaw_need_m"] = M_need / (4 * r["dT_N"])
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
kit.claim("CL-B3-HOVER-CANT-REQ", "Motor cant needed for hover yaw at 30 % differential, B4 half-fin factor",
          calc="CALC-B3-HOVER",
          output="cant_req_deg", unit="deg", limit=("<=", P + "propulsion.stations.cant_deg"),
          verifies=["R-HOVER-AUTHORITY"], how="Bench yaw torque on a turntable with canted mounts; hover yaw steps (H2).")


kit.claim("CL-B3-HOVER-YAW-RATIO-LOW", "Hover yaw control / 5 m/s disturbance, B4 half-fin factor (sizing case)",
          calc="CALC-B3-HOVER", output="ratio_yaw_low", unit="-", limit=(">=", P + "requirements.hover_ctrl_factor"),
          how="T-B4-YAW stand test measures the factor; T-B3-HOVER-WIND.",
          note="CL-B4-YAW-LOW 1.40 (CR-B4-13); R3 carried B4's R0-R2 0.48 here (ASM-B3-SWIRL-LOW, retired)")
kit.claim("CL-B3-HOVER-YAW-ACCEL-LOW", "Hover yaw acceleration, 30 % differential, B4 half-fin factor",
          calc="CALC-B3-HOVER", output="acc_yaw_low_rads2", unit="rad/s2",
          limit=(">=", P + "requirements.hover_ctrl_accel_min"), how="As CL-B3-HOVER-YAW-RATIO-LOW.")

# ---------------------------------------------------------------------------------------------- CDR-16 additions
# (CDR 2026-11-13, findings CDR-AE-04, -10, -11; review/CDR-2026-11-13/CDR-aero.md)
kit.assumption("ASM-B3-WTIP-CN", "Wing normal force with the wind along the span (wingtip into wind)",
               "The wing is a plate of aspect ratio c/b = 0.28 at incidence beta (the hover heading error): "
               "CN = (pi/2)(c/b) sin b cos b + CDc sin^2 b on S, CDc = 2.0 (slender-plate linear term plus cross-flow)",
               basis="review/CDR-2026-11-13/CDR-aero.md CDR-AE-04 (REVIEWER EST: 0.44 sin b cos b + 2 sin^2 b); "
                     "low-aspect-ratio plate theory (Hoerner, Fluid-Dynamic Lift, ch. 17, from memory, not re-read)",
               value=2.0, unit="-", status="UNVERIFIED")
kit.source("SRC-B3-CD-PLATE2D", "Drag coefficient table (Wikipedia, 'Drag coefficient', table of measured shapes)",
           "web", url="https://en.wikipedia.org/wiki/Drag_coefficient", checked="2026-11-14",
           where="'Long flat plate perpendicular to flow (2D)': 1.98-2.05; 'Flat plate perpendicular to flow (3D)': 1.28")
kit.assumption("ASM-B3-WTIP-CDC-MAX", "Upper end of the cross-flow Cd (pessimistic end for the wingtip-into-wind case)",
               "Largest cross-flow drag coefficient the wing can have with the wind along the span: the sharp-edged "
               "2-D flat plate normal to the flow",
               basis="SRC-B3-CD-PLATE2D: 2-D plate 1.98-2.05 (upper end used). K09-L's section has a rounded leading "
                     "edge and a finite length (3-D plate 1.28), both lower; so 2.05 bounds ASM-B3-WTIP-CN from above "
                     "(closure round 2026-11-14)", value=2.05, unit="-", cites=["SRC-B3-CD-PLATE2D"])
kit.assumption("ASM-B3-WTIP-ARM", "Centre of pressure of that force, ahead of mid-span toward the windward tip",
               "linear part at b/4 from mid-span, cross-flow part at b/8 (fractions of b: 0.25, 0.125). The moment "
               "grows with the heading error: the attitude is statically unstable towards broadside",
               basis="EST. Reproduces the reviewer's 0.17 N m at 10 deg and reads 0.42 N m at 20 deg against the "
                     "reviewer's 0.36 (5 m/s). At 90 deg the cross-flow CP is at mid-span, so b/8 is for beta <= 30 deg. "
                     "T-B3-HOVER-YAW-WTIP (twin, TW3) replaces it", value=[0.25, 0.125], unit="-", status="UNVERIFIED")
kit.assumption("ASM-B3-WTIP-BETA", "Hover heading errors checked in the wingtip-into-wind attitude",
               "10 deg (weathervane hold) and 20 deg (the yaw step of the twin test M3)",
               basis="review/CDR-2026-11-13/CDR-aero.md CDR-AE-04 and measure M3", value=[10.0, 20.0], unit="deg")
kit.assumption("ASM-B3-CANT-ALT", "Contingency motor cant", "10 deg instead of the 9 deg of record "
               "(P:propulsion.stations.cant_deg, D-146), with mount face_ahead 14.0 mm. The 10 deg / 14 mm mounts are "
               "printed as ready spares; they replace the 9 deg mounts if T-B3-HOVER-YAW-WTIP, before the first outdoor "
               "hover, reads a wing moment above 1.023 x this model (yaw RCOU spread > 30 % or heading diverges)",
               basis="review/DESIGN-ROUND-2026-11-14/A1.md#D-159 (trigger 1.045 -> 1.023 x model after B4's 9 deg yaw "
                     "factors: CL-B3-HOVER-YAW-WTIP-CDC-AT-FAC) and D-146; B3.md §1.4 (14.0 mm gives a 26.1 mm "
                     "blade-to-tube gap, E1 tip_gap); CDR-AE-04. PROPOSED, not applied. Closure round 2026-11-14: "
                     "9 deg passes at the upper bound of the cross-flow Cd (CL-B3-HOVER-YAW-WTIP-20-CDMAX), so the "
                     "test confirms and this stays a spare, not the planned fix. If ever fitted, it costs cos 10 / "
                     "cos 9 = 0.9971 of thrust: E1's fresh T/W 2.001 at 70.2 A would read 1.995 < 2.0 (E1 re-check)",
               value=10.0, unit="deg",
               status="PROPOSED")
kit.assumption("ASM-B3-GUST-DIFF-MAX", "Differential thrust allowed in the 8 m/s gust (survive-and-land case)",
               "40 % of hover thrust per motor (the 30 % of R-HOVER-AUTHORITY is the cap for the 5 m/s operating case; "
               "the mixer is not limited to it). 40 % leaves more than half of the 90 % the lower pair can give",
               basis="B3 choice for R-GUST-LEAN (CDR-AE-10: about 32 % is needed); A2 to accept (CR-B3-30)",
               value=0.40, unit="-", status="PROPOSED")


@kit.calc("CALC-B3-HOVER-WTIP", title="Hover yaw with a wingtip into the wind (Q_WVANE_LAND / TAKEOFF 3): wing moment "
          "against the yaw control power, cant of record (params, 9 deg D-146) and the 10 deg contingency",
          inputs={**HOV_IN, "Vg": P + "requirements.gust_survive_ms", "cdc": "ASM-B3-WTIP-CN", "arm": "ASM-B3-WTIP-ARM",
                  "betas": "ASM-B3-WTIP-BETA", "cant2": "ASM-B3-CANT-ALT", "cdmax": "ASM-B3-WTIP-CDC-MAX"},
          units={**HOV_U, "Vg": "m/s", "betas": "deg", "cant2": "deg"},
          assumes=["ASM-B3-WTIP-CN", "ASM-B3-WTIP-ARM", "ASM-B3-WTIP-BETA", "ASM-B3-HOVER-DIFF", "ASM-B3-CANT-ALT",
                   "ASM-B3-WTIP-CDC-MAX"],
          equation="M_wing(b, V) = q S [ (pi/2)(c/b) sin b cos b (b_span/4) + CDc sin^2 b (b_span/8) ] (destabilising) ; "
                   "M_fin(b, V) = 2 q A_fin CN90 cos b e, e = 0.75 sin b / (4 + pi cos b) x fin height (Kirchhoff plate "
                   "CP; restoring: the fins are broadside in this attitude) ; M_ctrl = 4 dT (kq_iso f_low + r sin cant), "
                   "dT = 30 % of hover thrust ; ratio = M_ctrl / M_wing (no fin credit) ; b_lim: M_wing = M_ctrl / fac")
def hover_wtip(m, g, dl, split, tmax, sag, y, z, Qh, swirl, cant, dfrac, Ixx, Iyy, Izz, m_basic, rho, Vw, S, c, b, x_t,
               cn90, xcp, fc, fh, fle, asym, fac, amin, swirl_lo, Vg, cdc, arm, betas, cant2, cdmax):
    Th = m * g * dl / 4
    dT = dfrac * Th
    kq_iso = Qh / Th
    rr = math.hypot(y, z)
    ixx = Ixx * m / m_basic
    a_fin = fc * 2 * fh                      # one fin (both half-fins), broadside to a spanwise wind

    def m_wing(beta_deg, V):
        q, bb = 0.5 * rho * V * V, math.radians(beta_deg)
        return q * S * ((math.pi / 2) * (c / b) * math.sin(bb) * math.cos(bb) * arm[0] * b
                        + cdc * math.sin(bb) ** 2 * arm[1] * b)

    def m_fin(beta_deg, V):
        q, bb = 0.5 * rho * V * V, math.radians(beta_deg)
        e = 0.75 * math.sin(bb) / (4 + math.pi * math.cos(bb)) * 2 * fh
        return 2 * q * a_fin * cn90 * math.cos(bb) * e

    def beta_at(M, V):
        lo, hi = 0.0, 60.0
        if m_wing(hi, V) < M:
            return hi
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if m_wing(mid, V) < M else (lo, mid)
        return 0.5 * (lo + hi)

    out = {}
    for tag, ca in (("", cant), ("_cant10", cant2)):
        k_low = kq_iso * swirl_lo + rr * math.sin(math.radians(ca))
        M = 4 * dT * k_low
        out["k_yaw_low_m" + tag], out["M_ctrl_Nm" + tag], out["acc_yaw_rads2" + tag] = k_low, M, M / ixx
        for bd in betas:
            for vt, V in (("5", Vw), ("gust", Vg)):
                out[f"ratio_{bd:.0f}deg_{vt}{tag}"] = M / m_wing(bd, V)
                out[f"ratio_{bd:.0f}deg_{vt}_fins{tag}"] = M / max(m_wing(bd, V) - m_fin(bd, V), 1e-9)
        out["beta_at_factor_5_deg" + tag] = beta_at(M / fac, Vw)      # heading error where the ratio falls to fac (1.5)
        out["beta_at_unity_5_deg" + tag] = beta_at(M, Vw)             # ... to 1.0: yaw control saturates at the cap
        out["beta_at_unity_gust_deg" + tag] = beta_at(M, Vg)
    for bd in betas:
        out[f"M_wing_{bd:.0f}deg_5_Nm"], out[f"M_wing_{bd:.0f}deg_gust_Nm"] = m_wing(bd, Vw), m_wing(bd, Vg)
        out[f"M_fin_{bd:.0f}deg_5_Nm"] = m_fin(bd, Vw)
    # cross-flow Cd sensitivity at the cant of record, 20 deg, 5 m/s (D-146 / D-159)
    q5, b20 = 0.5 * rho * Vw * Vw, math.radians(20.0)
    lin = q5 * S * (math.pi / 2) * (c / b) * math.sin(b20) * math.cos(b20) * arm[0] * b
    cross = q5 * S * math.sin(b20) ** 2 * arm[1] * b
    M0 = out["M_ctrl_Nm"]
    out["ratio_20deg_5_cdc110"] = M0 / (lin + 1.10 * cdc * cross)
    out["ratio_20deg_5_cdcmax"] = M0 / (lin + cdmax * cross)            # pessimistic end (closure round)
    out["ratio_20deg_5_cdcmax_cant10"] = out["M_ctrl_Nm_cant10"] / (lin + cdmax * cross)   # D-163: E/EP props
    out["cdc_at_factor_20deg_5"] = (M0 / fac - lin) / cross            # CDc at which the ratio falls to fac
    out["wing_moment_factor_at_fac"] = (M0 / fac) / m_wing(20.0, Vw)   # model multiplier the 1.5 tolerates
    out["yaw_arm_gain_cant10"] = out["k_yaw_low_m_cant10"] / out["k_yaw_low_m"] - 1
    out["lift_loss_cant10_vs_cant"] = 1 - math.cos(math.radians(cant2)) / math.cos(math.radians(cant))
    out["lift_loss_cant10_vs_0"] = 1 - math.cos(math.radians(cant2))
    return out


kit.claim("CL-B3-HOVER-YAW-WTIP-10", "Hover yaw control / wing moment, wingtip into a 5 m/s wind, 10 deg heading error "
          "(params cant, 9 deg D-146; B4 half-fin factor, no fin credit)", calc="CALC-B3-HOVER-WTIP", output="ratio_10deg_5", unit="-",
          limit=(">=", P + "requirements.hover_ctrl_factor"), verifies=["R-HOVER-AUTHORITY", "R-WIND"],
          how="T-B3-HOVER-YAW-WTIP (twin TW3): QHOVER at 5 m/s, wingtip into wind; yaw RCOU spread <= 30 %.")
kit.claim("CL-B3-HOVER-YAW-WTIP-20", "Hover yaw control / wing moment, wingtip into a 5 m/s wind, 20 deg heading error "
          "(the +/-20 deg yaw step of the twin test)", calc="CALC-B3-HOVER-WTIP", output="ratio_20deg_5", unit="-",
          limit=(">=", P + "requirements.hover_ctrl_factor"), verifies=["R-HOVER-AUTHORITY", "R-WIND"],
          how="T-B3-HOVER-YAW-WTIP: yaw steps of +/-20 deg; pass = heading returns with yaw RCOU spread <= 30 %. "
              "A fail here selects the 10 deg / 14.0 mm contingency (CL-B3-HOVER-YAW-WTIP-20-CANT10) before the flight mounts are printed.")
kit.claim("CL-B3-HOVER-YAW-WTIP-20-FINS", "As CL-B3-HOVER-YAW-WTIP-20 with the fins' restoring moment credited",
          calc="CALC-B3-HOVER-WTIP", output="ratio_20deg_5_fins", unit="-", how="As CL-B3-HOVER-YAW-WTIP-20.")
kit.claim("CL-B3-HOVER-YAW-WTIP-BETA", "Heading error at which the wingtip-into-wind yaw ratio falls to the 1.5 factor, "
          "5 m/s", calc="CALC-B3-HOVER-WTIP", output="beta_at_factor_5_deg", unit="deg",
          how="T-B3-HOVER-YAW-WTIP: largest yaw step from which the heading still returns.")
kit.claim("CL-B3-HOVER-YAW-WTIP-BETA-SAT", "Heading error at which the wing moment equals the capped yaw control, 5 m/s "
          "(beyond it the aircraft swings broadside)", calc="CALC-B3-HOVER-WTIP", output="beta_at_unity_5_deg", unit="deg",
          how="As CL-B3-HOVER-YAW-WTIP-BETA.")
kit.claim("CL-B3-HOVER-YAW-WTIP-GUST-10", "Hover yaw control / wing moment, wingtip into the 8 m/s gust, 10 deg heading "
          "error, 30 % differential", calc="CALC-B3-HOVER-WTIP", output="ratio_10deg_gust", unit="-", limit=(">=", 1.0),
          verifies=["R-GUST-LEAN"], how="Twin: QLAND in gusty wind (logged); yaw RCOU spread and heading error.")
kit.claim("CL-B3-HOVER-YAW-WTIP-BETA-GUST", "Heading error at which the wing moment equals the capped yaw control in "
          "the 8 m/s gust", calc="CALC-B3-HOVER-WTIP", output="beta_at_unity_gust_deg", unit="deg",
          how="Information for the flight card: in a gust the wingtip-into-wind stance holds only for small heading "
              "errors; beyond this the aircraft turns broadside (then the pitch axis carries the wind).")
kit.claim("CL-B3-HOVER-YAW-WTIP-20-CD110", "As CL-B3-HOVER-YAW-WTIP-20 with the cross-flow Cd 10 % higher "
          "(ASM-B3-WTIP-CN x 1.1), information", calc="CALC-B3-HOVER-WTIP", output="ratio_20deg_5_cdc110", unit="-",
          note="A1.md D-159: below 1.5 at 9 deg after B4's 9 deg yaw factors; accepted with the 1.023 trigger and the "
               "10 deg / 14 mm spares", how="T-B3-HOVER-YAW-WTIP.")
kit.claim("CL-B3-HOVER-YAW-WTIP-20-CDMAX", "As CL-B3-HOVER-YAW-WTIP-20 at the upper end of the cross-flow Cd "
          "(ASM-B3-WTIP-CDC-MAX, sharp 2-D plate), no fin credit: the pessimistic end of T-B3-HOVER-YAW-WTIP",
          calc="CALC-B3-HOVER-WTIP", output="ratio_20deg_5_cdcmax", unit="-",
          limit=(">=", P + "requirements.hover_ctrl_factor"), verifies=["R-HOVER-AUTHORITY"],
          note="Closure round 2026-11-14 (B3.md §3): the 9 deg cant passes at the physical upper bound of the "
               "cross-flow Cd, so the hanging yaw test confirms and does not decide. The 10 deg spares stay spares",
          how="T-B3-HOVER-YAW-WTIP: measured wing moment <= 1.023 x model (CDc <= 2.10).")
kit.claim("CL-B3-HOVER-YAW-WTIP-20-CDMAX-CANT10", "As CL-B3-HOVER-YAW-WTIP-20-CDMAX at the 10 deg / 14 mm cant "
          "(ASM-B3-CANT-ALT), information until A1 moves P:propulsion.stations.cant_deg", calc="CALC-B3-HOVER-WTIP",
          output="ratio_20deg_5_cdcmax_cant10", unit="-",
          note="Closure round D-163: with the E/EP props (D-161) the 9 deg value falls below 1.5 at the Cd upper bound",
          how="T-B3-HOVER-YAW-WTIP on the 10 deg mounts.")
kit.claim("CL-B3-HOVER-YAW-WTIP-CDC-AT-FAC", "Cross-flow Cd at which CL-B3-HOVER-YAW-WTIP-20 falls to 1.5 (model "
          "value 2.0), information", calc="CALC-B3-HOVER-WTIP", output="cdc_at_factor_20deg_5", unit="-",
          how="T-B3-HOVER-YAW-WTIP: the trigger of ASM-B3-CANT-ALT is wing_moment_factor_at_fac of this calc.")
kit.claim("CL-B3-HOVER-YAW-WTIP-20-CANT10", "Contingency: as CL-B3-HOVER-YAW-WTIP-20 with 10 deg cant",
          calc="CALC-B3-HOVER-WTIP", output="ratio_20deg_5_cant10", unit="-",
          how="Only if the twin test fails: D3 re-draws the mount at 10 deg, E1 re-checks the blade-to-tube gap.")
kit.claim("CL-B3-CANT10-ARM-GAIN", "Contingency: hover yaw arm gain from the params cant (9 deg) to 10 deg (B4 half-fin factor)",
          calc="CALC-B3-HOVER-WTIP", output="yaw_arm_gain_cant10", unit="-", how="T-B4-YAW with a 10 deg wedge.")
kit.claim("CL-B3-CANT10-LIFT-LOSS", "Contingency: lift lost going from the params cant (9 deg) to 10 deg", calc="CALC-B3-HOVER-WTIP",
          output="lift_loss_cant10_vs_cant", unit="-", how="cos 10 / cos(params cant); E1 re-reads T/W at the gate.")
kit.claim("CL-B3-CANT10-YAW-ACCEL", "Contingency: hover yaw acceleration at 10 deg cant, 30 % differential",
          calc="CALC-B3-HOVER-WTIP", output="acc_yaw_rads2_cant10", unit="rad/s2", how="As CL-B3-HOVER-YAW-ACCEL-LOW.")


@kit.calc("CALC-B3-HOVER-GUST", title="Hover pitch control in the 8 m/s gust, belly into wind (R-GUST-LEAN)",
          inputs={"rp": "CL-B3-HOVER-PITCH-RATIO", "Vw": P + "requirements.wind_limit_ms",
                  "Vg": P + "requirements.gust_survive_ms", "dfrac": "ASM-B3-HOVER-DIFF", "dg": "ASM-B3-GUST-DIFF-MAX"},
          units={"Vw": "m/s", "Vg": "m/s"}, assumes=["ASM-B3-GUST-DIFF-MAX", "ASM-B3-HOVER-DIFF"],
          equation="ratio_cap = ratio(5 m/s) (Vw/Vg)^2 at the 30 % cap ; d_need = 30 % / ratio_cap ; "
                   "ratio_gust = ratio_cap x d_gust / 30 % (control moment is linear in the differential below the "
                   "lower pair's limit, 90 % of hover thrust)")
def hover_gust(rp, Vw, Vg, dfrac, dg):
    r_cap = rp * (Vw / Vg) ** 2
    return {"ratio_cap30": r_cap, "diff_needed": dfrac / r_cap, "ratio_gust": r_cap * dg / dfrac}


kit.claim("CL-B3-HOVER-PITCH-RATIO-GUST", "Hover pitch control / 8 m/s gust moment at the gust differential (40 %)",
          calc="CALC-B3-HOVER-GUST", output="ratio_gust", unit="-", limit=(">=", 1.0), verifies=["R-GUST-LEAN"],
          how="Twin, belly into a gusty wind (logged anemometer): upper / lower RCOU split stays below the 40 % "
              "differential; no motor at its floor.")
kit.claim("CL-B3-HOVER-PITCH-RATIO-GUST-CAP30", "Hover pitch control / 8 m/s gust moment at the 30 % cap of "
          "R-HOVER-AUTHORITY (below 1: the cap does not hold the gust)", calc="CALC-B3-HOVER-GUST", output="ratio_cap30",
          unit="-", how="Information (CDR-AE-10): the gust case needs CL-B3-HOVER-PITCH-DIFF-GUST of differential.")
kit.claim("CL-B3-HOVER-PITCH-DIFF-GUST", "Differential thrust needed to hold the 8 m/s gust in pitch",
          calc="CALC-B3-HOVER-GUST", output="diff_needed", unit="-", limit=("<=", "ASM-B3-GUST-DIFF-MAX"),
          verifies=["R-GUST-LEAN"], how="As CL-B3-HOVER-PITCH-RATIO-GUST.")


kit.assumption("ASM-B3-T-THRMAX", "Total thrust at THR_MAX 70 % and 16 m/s", "20 N (upper end of 15-20 N)",
               basis="review/CDR-2026-11-13/CDR-aero.md CDR-AE-11 (REVIEWER EST); B4 / E1 stand data replace it",
               value=20.0, unit="N", status="UNVERIFIED")
kit.assumption("ASM-B3-THRUST-LINE-MAX", "Elevon equivalent of the thrust-line moment at THR_MAX", "<= 5 deg, so a "
               "throttle step 30 -> 70 % stays well inside the pure-pitch travel left after trim",
               basis="B3 choice; F4 checks in SITL (stage B) that the step holds pitch within the FBWA limits",
               value=5.0, unit="deg", status="PROPOSED")


@kit.calc("CALC-B3-THRUST-LINE", title="Thrust line below the CG: pitch moment and elevon equivalent in cruise (CDR-AE-11)",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "S": "CL-A1-WING-AREA", "c": P + "wing.chord_m", "zcg": P + "cg.z_target_m",
                  "ld": P + "performance.ld_cruise", "vc": P + "performance.cruise_ms", "tmax": "ASM-B3-T-THRMAX",
                  "CLd": "CL-B3-CLD", "Cmd_ref": "CL-B3-CMD", "eta": "CL-B2-ELEVON-ETA", "lo": "CL-D6-EFF-LOSS-OUT",
                  "li": "CL-D6-EFF-LOSS-IN", "va": "ASM-F4-VA-SCHED", "d_cruise": "CL-B3-ELEVON-TRIM-CRUISE"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2", "c": "m", "zcg": "m", "vc": "m/s", "tmax": "N",
                 "va": "m/s", "d_cruise": "deg"}, assumes=["ASM-B3-T-THRMAX"],
          equation="four equal thrusts act in the chord plane, the CG is z_cg above it: M = T z_cg (nose-up) ; "
                   "dCm = M / (q S c) ; d_elevon = dCm / (|Cmd| eta e_D6) (TE-down equivalent: the thrust line "
                   "reduces the TE-up trim) ; T = m g / (L/D) in cruise, ASM-B3-T-THRMAX at THR_MAX")
def thrust_line(m, g, rho, S, c, zcg, ld, vc, tmax, CLd, Cmd_ref, eta, lo, li, va, d_cruise):
    q = 0.5 * rho * vc * vc
    cmd = abs(Cmd_ref) * eta * eff_mech(vc, lo, li, va)        # per deg about the CG target (x_ref = target)
    t_c = m * g / ld
    out = {"T_cruise_N": t_c, "M_cruise_Nm": t_c * zcg, "M_thrmax_Nm": tmax * zcg}
    out["dCm_cruise"], out["dCm_thrmax"] = out["M_cruise_Nm"] / (q * S * c), out["M_thrmax_Nm"] / (q * S * c)
    out["delev_cruise_deg"], out["delev_thrmax_deg"] = out["dCm_cruise"] / cmd, out["dCm_thrmax"] / cmd
    out["delev_step_30_70_deg"] = (tmax * zcg * (1 - 30.0 / 70.0)) / (q * S * c) / cmd     # thrust ~ linear in throttle (EST)
    out["trim_cruise_power_on_deg"] = d_cruise + out["delev_cruise_deg"]                  # d_cruise is negative (TE up)
    return out


kit.claim("CL-B3-THRUST-LINE-M-CRUISE", "Nose-up moment of the thrust line 18.5 mm below the CG, cruise thrust",
          calc="CALC-B3-THRUST-LINE", output="M_cruise_Nm", unit="N*m",
          how="Trim-vs-throttle in FBWA on the twin: elevon trim at 16 m/s power-on against a glide at the same speed.")
kit.claim("CL-B3-THRUST-LINE-DELEV-CRUISE", "Elevon equivalent of the thrust-line moment at cruise thrust "
          "(TE-up trim is this much smaller power-on)", calc="CALC-B3-THRUST-LINE", output="delev_cruise_deg", unit="deg",
          how="As CL-B3-THRUST-LINE-M-CRUISE.")
kit.claim("CL-B3-THRUST-LINE-DELEV-THRMAX", "Elevon equivalent of the thrust-line moment at THR_MAX 70 %, 16 m/s",
          calc="CALC-B3-THRUST-LINE", output="delev_thrmax_deg", unit="deg", limit=("<=", "ASM-B3-THRUST-LINE-MAX"),
          how="SITL stage B and then flight: throttle step 30 -> 70 % at 16 m/s in FBWA holds pitch within the limits.")


FLEX_IN = {"Iyy": "CL-A3-IYY", "Ixx": "CL-A3-IXX", "m_basic": "CL-A3-MASS-BASIC", "m": P + "requirements.mtow_gate_kg",
           "g": P + "env.g_ms2", "dl": P + "propulsion.download_factor", "Qh": "CL-B4-HOVER-Q", "swirl": "CL-B4-YAW",
           "y": P + "propulsion.stations.y_m", "z": P + "propulsion.stations.z_m",
           "cant": P + "propulsion.stations.cant_deg", "f_anti": "CL-C2-F-TORSION-ANTI",
           "f_sym": "CL-C2-F-TORSION-SYM", "f_hi": "ASM-B3-TORSION-HIGH", "Is": "ASM-B3-STATION-IYY",
           "zeta": "ASM-B3-FLEX-ZETA", "tau": "ASM-B3-MOTOR-TAU", "delay": "ASM-B3-LOOP-DELAY",
           "filt": "ASM-B3-FSW-FILT", "pid_p": "ASM-B3-FSW-PID-PIT", "pid_y": "ASM-B3-FSW-PID-YAW",
           "xo": "ASM-B3-XOVER", "gm_min": "ASM-B3-GM-MIN", "pm_min": "ASM-B3-PM-MIN"}
FLEX_U = {"m": "kg", "g": "m/s2", "y": "m", "z": "m", "cant": "deg", "f_anti": "Hz", "f_sym": "Hz", "f_hi": "Hz",
          "tau": "s", "delay": "s", "filt": "Hz", "xo": "Hz", "gm_min": "dB", "pm_min": "deg"}


@kit.calc("CALC-B3-HOVER-FLEX", title="Hover pitch and yaw rate loops with the wing torsion modes (CR-C2-03)",
          inputs=FLEX_IN, units=FLEX_U, cites=["SRC-B3-MIL9490"],
          assumes=["ASM-B3-STATION-IYY", "ASM-B3-FLEX-ZETA", "ASM-B3-MOTOR-TAU", "ASM-B3-FSW-FILT", "ASM-B3-XOVER"],
          equation="L = C_PID(F4 ratios, scaled to the rigid crossover) x motor lag x Pade delay x structure x gyro LPF ;"
                   " pitch: two-inertia, stations 2 I_s on the torsion spring, gyro on the body, free-free f_sym ; "
                   "yaw: rigid k_y/(Ixx s) + thrust tilt of the antisymmetric twist 16 T y z sigma/(2 I_s (s^2+2 zeta w s"
                   "+w^2)) ; GM = min over -180 deg crossings, PM = min over 0 dB crossings, at both frequency corners "
                   "(and sigma = +/-1 for yaw) ; max crossover = highest f_c with GM >= 6 dB and PM >= 45 deg")
def hover_flex(Iyy, Ixx, m_basic, m, g, dl, Qh, swirl, y, z, cant, f_anti, f_sym, f_hi, Is, zeta, tau, delay, filt,
               pid_p, pid_y, xo, gm_min, pm_min):
    k = m / m_basic
    T = m * g * dl / 4
    ky = 4 * (Qh / T * swirl + math.hypot(y, z) * math.sin(math.radians(cant)))
    ph = {"pitch": dict(k=4 * z, I=Iyy * k, I_st=2 * Is),
          "yaw": dict(k=ky, I=Ixx * k, I_st=2 * Is, T=T, y=y, z=z)}
    flt = (tau, delay, filt[0], filt[1])
    corners = {"pitch": [(f_sym, 1.0), (f_hi[1], 1.0)],
               "yaw": [(f_anti, 1.0), (f_hi[0], 1.0), (f_anti, -1.0), (f_hi[0], -1.0)]}
    pid = {"pitch": pid_p, "yaw": pid_y}

    def worst(ax, fc, nominal_only=False, rigid=True):
        rows = []
        for fm, sg in corners[ax]:
            if nominal_only and sg < 0:
                continue
            r = HL.loop(ax, fc, fm, zeta, pid[ax], flt, ph[ax], sg, rigid_margins=rigid)
            row = {"f_mode": fm, "sigma": sg, "gm_db": r["flex"]["gm_db"], "f_gm": r["flex"]["f_gm_hz"],
                   "pm_deg": r["flex"]["pm_deg"], "stable": r["flex"]["stable"], "peak_db": r["mode_peak_db"]}
            if rigid:
                row.update({"gm_rigid_db": r["rigid"]["gm_db"], "pm_rigid_deg": r["rigid"]["pm_deg"]})
            rows.append(row)
        return rows

    def ok(ax, fc):
        return all(r["gm_db"] >= gm_min and r["pm_deg"] >= pm_min and r["stable"]
                   for r in worst(ax, fc, nominal_only=True, rigid=False))

    out = {}
    for i, ax in enumerate(("pitch", "yaw")):
        rows = worst(ax, xo[i])
        out[f"{ax}_cases"] = [{kk: (round(v, 3) if isinstance(v, float) else v) for kk, v in r.items()} for r in rows]
        nom = [r for r in rows if r["sigma"] > 0]
        out[f"gm_{ax}_db"] = min(r["gm_db"] for r in nom)
        out[f"pm_{ax}_deg"] = min(r["pm_deg"] for r in nom)
        out[f"gm_{ax}_any_map_db"] = min(r["gm_db"] for r in rows)
        out[f"stable_{ax}"] = int(all(r["stable"] for r in rows))
        out[f"gm_{ax}_rigid_db"], out[f"pm_{ax}_rigid_deg"] = rows[0]["gm_rigid_db"], rows[0]["pm_rigid_deg"]
        fc = round(xo[i], 1)                          # 0.1 Hz steps from F4's crossover, up while it passes
        if ok(ax, fc):
            while fc < 10.0 and ok(ax, round(fc + 0.1, 1)):
                fc = round(fc + 0.1, 1)
        else:
            while fc > 0.2 and not ok(ax, fc):
                fc = round(fc - 0.1, 1)
        out[f"xover_max_{ax}_hz"] = fc
        r5 = worst(ax, 5.0, nominal_only=True, rigid=False)
        out[f"gm_{ax}_at_5hz_db"] = min(r["gm_db"] for r in r5)
        out[f"pm_{ax}_at_5hz_deg"] = min(r["pm_deg"] for r in r5)
    # antisymmetric mode anywhere in C2's 11.7-14.9 Hz band (D-45: 12-15 Hz), yaw loop at its ceiling, both map signs
    band = [f_anti + (f_hi[0] - f_anti) * i / 8 for i in range(9)]
    gb = []
    for fm in band:
        for sg in (1.0, -1.0):
            r = HL.loop("yaw", out["xover_max_yaw_hz"], fm, zeta, pid["yaw"], flt, ph["yaw"], sg, rigid_margins=False)
            gb.append((r["flex"]["gm_db"], r["flex"]["pm_deg"], fm, sg))
    out["yaw_band_gm_min_db"], out["yaw_band_pm_min_deg"] = min(x[0] for x in gb), min(x[1] for x in gb)
    out["yaw_band_f_worst_hz"] = min(gb)[2]
    # static aeroelastic change of hover yaw control power (antisymmetric twist tilts the thrust), low corner
    w = 2 * math.pi * f_anti
    out["yaw_flex_static_frac"] = 16 * T * y * z / (2 * Is * w * w * ky)
    out["ky_Nm_per_N"] = ky
    return out


kit.claim("CL-B3-FLEX-GM-PITCH", "Hover pitch loop gain margin with the symmetric torsion mode, F4 crossover",
          calc="CALC-B3-HOVER-FLEX", output="gm_pitch_db", unit="dB", limit=(">=", "ASM-B3-GM-MIN"),
          verifies=["R-HOVER-AUTHORITY"], assumes=["ASM-B3-FLEX-ZETA", "ASM-B3-MOTOR-TAU"],
          how="T-C2-TAP-TEST gives f and zeta; tethered hover: raise Q_A_RAT_PIT_P until oscillation (gyro FFT), "
              "margin = 20 log(P_osc / P_used).")
kit.claim("CL-B3-FLEX-GM-YAW", "Hover yaw loop gain margin with the antisymmetric torsion mode, F4 crossover",
          calc="CALC-B3-HOVER-FLEX", output="gm_yaw_db", unit="dB", limit=(">=", "ASM-B3-GM-MIN"),
          verifies=["R-HOVER-AUTHORITY"], assumes=["ASM-B3-FLEX-ZETA", "ASM-B3-MOTOR-TAU"],
          how="As CL-B3-FLEX-GM-PITCH with Q_A_RAT_YAW_P.")
kit.claim("CL-B3-FLEX-PM-PITCH", "Hover pitch loop phase margin, flexible, F4 crossover", calc="CALC-B3-HOVER-FLEX",
          output="pm_pitch_deg", unit="deg", limit=(">=", "ASM-B3-PM-MIN"),
          how="Tethered hover step responses: overshoot <= 25 % (gyro log).")
kit.claim("CL-B3-FLEX-PM-YAW", "Hover yaw loop phase margin, flexible, F4 crossover", calc="CALC-B3-HOVER-FLEX",
          output="pm_yaw_deg", unit="deg", limit=(">=", "ASM-B3-PM-MIN"), how="As CL-B3-FLEX-PM-PITCH.")
kit.claim("CL-B3-XOVER-MAX-PITCH", "Highest hover pitch crossover with 6 dB / 45 deg, torsion mode in",
          calc="CALC-B3-HOVER-FLEX", output="xover_max_pitch_hz", unit="Hz", limit=(">=", 2.6),
          how="F4 tuning ceiling (TUNING-PLAN.md): do not raise pitch P above the value giving this crossover "
              "until a notch is set from T-C2-TAP-TEST.", note="limit 2.6 Hz = F4's starting crossover (ASM-B3-XOVER, CL-F4-XOVER-PIT)")
kit.claim("CL-B3-XOVER-MAX-YAW", "Highest hover yaw crossover with 6 dB / 45 deg, torsion mode in",
          calc="CALC-B3-HOVER-FLEX", output="xover_max_yaw_hz", unit="Hz", limit=(">=", 1.0),
          how="As CL-B3-XOVER-MAX-PITCH for yaw P.", note="limit 1.0 Hz = F4's starting crossover (ASM-B3-XOVER, CL-F4-XOVER-YAW)")
kit.claim("CL-B3-HOVER-YAW-FLEX-STATIC", "Static change of hover yaw control power from the antisymmetric twist",
          calc="CALC-B3-HOVER-FLEX", output="yaw_flex_static_frac", unit="-",
          how="Turntable yaw-torque bench test on the built wing vs the rigid prediction.",
          note="positive = adds to the rigid moment with F4's motor map; not credited in CL-B3-HOVER-YAW-RATIO")


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
# Design round 2026-11-14 (review/DESIGN-ROUND-2026-11-14/B3.md §2, A1.md D-149): the prop normal force is applied
# with its physical sign (nose-up, props ahead of the CG) on B4's BEMT slope, the quasi-steady level pitch-over is kept
# as information, and the pass line is the time-domain pitch-over the firmware flies.
# Closure round 2026-11-14 (review/CLOSURE-ROUND-2026-11-14/B3.md, A2.md §2.3): the entry is a throttle ratio to the
# learnt hover throttle plus a timed pre-climb, sized so that the pitch use, the gust reserve and the handover pass at
# the LOW thrust edge and the sagged-pack thrust fraction (B1's 0.80) passes at the HIGH edge (team/B3/closure1114.py).
kit.source("SRC-B3-AP-TAILSIT", "ArduPilot ArduPlane/tailsitter.cpp at tag Plane-4.7.2", "web",
           url="https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/ArduPlane/tailsitter.cpp",
           checked="2026-11-14",
           where="Tailsitter_Transition::update, state ANGLE_WAIT_FW: nav_pitch_cd ramped at transition_rate_fw "
                 "(Q_TAILSIT_RAT_FW); set_throttle_out(MAX(motors->get_throttle_hover(), "
                 "attitude_control->get_throttle_in()), true, 0), comment 'set throttle at either hover throttle or "
                 "current throttle, whichever is higher, through the transition'; VTOL control until |pitch| > "
                 "Q_TAILSIT_ANGLE (transition_fw_complete, timeout (ANGLE + initial pitch) / RAT_FW x 1.5 s). "
                 "Tailsitter_Transition::VTOL_update calls restart() every VTOL loop, so ANGLE_WAIT_FW starts at the "
                 "mode change from the last Q-mode throttle_in. defaults_table_tailsitter: Q_A_ANGLE_BOOST 0, "
                 "Q_TRANSITION_MS 2000; Tailsitter::setup uses Q_TRANSITION_MS only to default an unconfigured "
                 "Q_TAILSIT_RAT_FW (ANGLE / (Q_TRANSITION_MS / 2000))")
kit.source("SRC-B3-AP-ATCMULTI", "ArduPilot libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp at tag "
           "Plane-4.7.2", "web",
           url="https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/libraries/AC_AttitudeControl/"
               "AC_AttitudeControl_Multi.cpp", checked="2026-11-14",
           where="set_throttle_out: first statement '_throttle_in = throttle_in;', so MAX(hover, get_throttle_in()) "
                 "is stored back each loop and the entry value is held to Q_TAILSIT_ANGLE whatever the stick does; "
                 "get_throttle_boosted returns the input unchanged when ANGLE_BOOST is 0 (else x 1/cos tilt)")
kit.source("SRC-B3-AP-QSTAB", "ArduPilot ArduPlane/mode_qstabilize.cpp and quadplane.cpp at tag Plane-4.7.2", "web",
           url="https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/ArduPlane/mode_qstabilize.cpp",
           checked="2026-11-14",
           where="QSTABILIZE: hold_stabilize(get_pilot_throttle()) -> set_throttle_out(pilot throttle); "
                 "get_pilot_throttle = throttle_curve(get_throttle_hover(), Q_THROTTLE_EXPO, stick) (quadplane.cpp); "
                 "update_throttle_hover returns while the Z controller is not running, so the learnt hover throttle "
                 "does not move in QSTABILIZE")
kit.assumption("ASM-B3-TRANS-T0", "Forward-transition entry setting [r = throttle_in / learnt hover throttle, "
               "pre-climb hold s]",
               "Entry procedure (closure round 2026-11-14): hover in QSTABILIZE; set throttle_in = r x the learnt "
               "Q_M_THST_HOVER (transmitter throttle override on the transition switch, not a stick position); hold "
               "it for the pre-climb time (the aircraft climbs at (r dl - dl) g); then select FBWA. ArduPilot holds "
               "MAX(hover, throttle_in) from the mode change to Q_TAILSIT_ANGLE (SRC-B3-AP-TAILSIT, "
               "SRC-B3-AP-ATCMULTI), with Q_A_ANGLE_BOOST 0. Static thrust / W at entry = dl_true x r",
               basis="team/B3/closure1114.py (results/closure1114.json design): window on static T0/W at 12 deg/s, "
                     "70 deg, forward CG: low end 1.2827 at a 4 m/s pre-climb (use 0.60, gust 1.0, handover 12.94 "
                     "m/s; 1.3278 from a steady hover), high end 0.80 x 1.7456 = 1.3968 (A2.md §2.3). r = 1.285 "
                     "centres the realisation band of ASM-B3-TRANS-REALISE in it (edges 1.2908 / 1.3893). Hold 2.0 s "
                     "gives >= 4.17 m/s at the low edge. Replaces D-149's '>= 1.4 W' (frac 0.802 > 0.80). The firmware "
                     "law is read from source, so SITL S4c confirms it and is no longer a condition. FINAL RE-RUN 2026-11-14: hold "
                     "2.0 -> 1.0 s. With the X2814 + 11x8E the thrust lapse with speed is smaller, the climb to 17 m/s at the "
                     "high edge read 66.2 m (50 m start + 66.2 > the 110 m fence); 1.0 s reads 50.6 m, the low edge still "
                     "credits 2.1 m/s and needs none (use 0.319 without it)",
               value=[1.285, 1.0], unit="-,s", status="PROPOSED",
               cites=["SRC-B3-AP-TAILSIT", "SRC-B3-AP-ATCMULTI", "SRC-B3-AP-QSTAB"])
kit.assumption("ASM-B3-TRANS-REALISE", "Entry thrust realisation band [dl_true low, thrust-linearisation error, "
               "pre-climb credit factor]",
               "T0/W = dl_true x r x (1 +/- e_lin) with dl_true between the low value and P:propulsion."
               "download_factor; vertical speed at the mode change credited as k x (T0 - dl) g x hold",
               basis="dl_true low 1.025 = B4's SU2 download (CL-B4-SIM-DOWNLOAD, params note on "
                     "propulsion.download_factor; 1.038 R3), high = the params key 1.06 kept until T-B4-INSTALLED. "
                     "e_lin 2 % EST: Q_M_THST_EXPO fit between the hover and the entry throttle (0.49 -> 0.63), set "
                     "from the stand. k = 0.8 EST: drag of the edge-on climb and the switch delay. B3 choice",
               value=[1.025, 0.02, 0.8], unit="-,-,-", status="UNVERIFIED")
kit.assumption("ASM-B3-FSW-TRANS", "Firmware transition settings [Q_TAILSIT_RAT_FW, Q_TAILSIT_ANGLE, Q_ASSIST_SPEED]",
               "Pitch-over ramp rate, tilt at which the plane controller takes over, copter-assist speed",
               basis="subsystems/flight-software/K09L.param (F4-R6): Q_TAILSIT_RAT_FW 12, Q_TAILSIT_ANGLE 70, "
                     "Q_ASSIST_SPEED 14", value=[12.0, 70.0, 14.0], unit="deg/s,deg,m/s", cites=["SRC-B3-AP-TAILSIT"])
kit.assumption("ASM-B3-TD-LOOP", "Pitch attitude loop in the time-domain pitch-over [wn rad/s, zeta]",
               "2nd-order following of the ramped pitch target",
               basis="EST, of the order of the hover pitch loop; the swept range 4-10 rad/s changes the hover-throttle "
                     "peak by <= 0.003 (team/B3/results/round1114.json td_summary *_wn4 / *_wn10)",
               value=[6.0, 1.0], unit="rad/s,-", status="UNVERIFIED")
kit.assumption("ASM-B3-B4-INC-V", "Airspeed of B4's prop-at-incidence BEMT points",
               "Speed at which CL-B4-SIM-H-MAX, -H-HOVERT, -DH-DI and -T-I45 are evaluated",
               basis="team/B4/sim/claims.sim.json CALC-B4-SIM-INC input V = 17.0 m/s (B4 wave 2, at 9 deg cant; "
                     "B4-W2.md). Kept as its own node, not P:performance.transition_min_ms, so the H-force speed only "
                     "moves when B4's points move. The 15.6 m/s set is B4's -V156 information claims; never pair "
                     "CL-B4-SIM-DH-DI (17 m/s) with 15.6",
               value=17.0, unit="m/s")

TRANS_IN = {"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
            "S": "CL-A1-WING-AREA", "c": P + "wing.chord_m", "b": P + "wing.span_m", "x_t": P + "cg.x_target_m",
            "x_fwd": "CL-B3-V-CG-FWD", "xnp": "CL-B3-XNP", "cm_np_thin": "CL-B3-CM-NP-THIN",
            "dcm": "CL-B2-DCM-VISC", "CLa": "CL-B3-CLA", "a0": "CL-B3-ALPHA0", "clmax": "CL-B3-CLMAX-TRIM",
            "cd0": "ASM-B3-CD0", "e": P + "wing.oswald_e", "cn90": "ASM-B3-CN90", "n": P + "propulsion.n_motors",
            "D": P + "propulsion.prop_diameter_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
            "cna": "ASM-B3-PROP-CNA", "tmax": P + "propulsion.thrust_max_per_motor_kg",
            "sag": P + "propulsion.voltage_sag", "z": P + "propulsion.stations.z_m",
            "dl": P + "propulsion.download_factor", "vc": P + "performance.cruise_ms",
            "CLd": "CL-B3-CLD", "Cmd_ref": "CL-B3-CMD", "xref": P + "cg.x_target_m", "eta": "CL-B2-ELEVON-ETA",
            "dp": "ASM-B3-ELEVON-TRANS", "fpost": "ASM-B3-ELEVON-POST", "lo": "CL-D6-EFF-LOSS-OUT",
            "li": "CL-D6-EFF-LOSS-IN", "va": "ASM-F4-VA-SCHED", "slop": "CL-D6-SLOP",
            "h_max": "CL-B4-SIM-H-MAX", "h_hov": "CL-B4-SIM-H-HOVERT", "dHdi": "CL-B4-SIM-DH-DI",
            "v_inc": "ASM-B3-B4-INC-V", "dfrac": "ASM-B3-HOVER-DIFF"}
TRANS_U = {"m": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2", "c": "m", "b": "m", "x_t": "m", "x_fwd": "m",
           "xnp": "m", "a0": "deg", "D": "m", "x_prop": "m", "tmax": "kg", "z": "m", "vc": "m/s",
           "xref": "m", "dp": "deg", "va": "m/s", "slop": "deg", "h_max": "N", "h_hov": "N", "dHdi": "N/rad",
           "v_inc": "m/s"}


@kit.calc("CALC-B3-TRANSITION", title="Quasi-steady level transition pitch balance at hover thrust (information "
          "since D-149), prop normal force signed",
          assumes=["ASM-B3-CN90", "ASM-B3-CD0", "ASM-B3-PROP-CNA", "ASM-B3-ELEVON-TRANS", "ASM-B3-ELEVON-POST",
                   "ASM-B3-B4-INC-V"],
          inputs=TRANS_IN, units=TRANS_U,
          equation="level flight at V: T cos a = D, T sin a + L = W ; wing CP from Xnp (attached) to 0.5 c at 90 deg ; "
                   "elevon (dp - slop) deg at Cmd eta e_D6(V) ; prop normal force at x_prop, SIGNED (props ahead of "
                   "the CG: nose-up, against the nose-down wing moment; D-149): Np = max(k Np_Ribner, n H min(1, "
                   "V/V_inc)) with variants nohub (k = 1, H = 0), bemt (k = dH/di / (cna A q(V_inc)), H = 0: the "
                   "basis, smaller nose-up term = conservative), hmax (k = 1, H = CL-B4-SIM-H-MAX), hhov (k = 1, "
                   "H = CL-B4-SIM-H-HOVERT, optimistic) ; use_cap30 = |M_aero| / (2 x 0.30 T_hover 2z), no elevon "
                   "credit ; use_full = (|M_aero| - M_elevon) / (2 dT 2z), dT = min(T/4, Tmax sag - T/4) (information)")
def transition(m, g, rho, S, c, b, x_t, x_fwd, xnp, cm_np_thin, dcm, CLa, a0, clmax, cd0, e, cn90, n, D, x_prop,
               cna, tmax, sag, z, dl, vc, CLd, Cmd_ref, xref, eta, dp, fpost, lo, li, va, slop, h_max, h_hov, dHdi,
               v_inc, dfrac):
    AR = b * b / S
    k_ind = 1 / (math.pi * e * AR)
    out = {}
    m_cap30 = 2 * (dfrac * m * g * dl / 4) * (2 * z)       # N m: the pitch moment of CALC-B3-HOVER at the 30 % cap
    k_bemt = dHdi / (cna * (math.pi * D * D / 4) * 0.5 * rho * v_inc ** 2)
    out["prop_slope_ratio_bemt"] = k_bemt
    for hk, ks, H in (("nohub", 1.0, 0.0), ("bemt", k_bemt, 0.0), ("hmax", 1.0, h_max), ("hhov", 1.0, h_hov)):
        keys = {}
        for tag, x in (("target", x_t), ("fwd", x_fwd)):
            rows = []
            for V in sorted({0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, vc}):
                cmd = (Cmd_ref + CLd * (x - xref) / c) * eta * eff_mech(V, lo, li, va)
                r = FM.transition_point(V, m, g, rho, S, c, x, xnp, cm_np_thin + dcm, CLa, math.radians(a0), clmax,
                                        cd0, k_ind, cn90, n, D, x_prop, cna, tmax * g * sag, z, 0.0, dl, cmd,
                                        dp - slop, fpost, np_scale=ks, np_min=n * H * min(1.0, V / v_inc))
                rows.append([V, round(r["alpha_deg"], 1), round(r["TW"], 3), round(r["M_aero_Nm"], 3),
                             round(r["M_prop_Nm"], 3), round(r["M_elev_Nm"], 3), round(r["M_avail_Nm"], 3),
                             round(r["use"], 3), round(abs(r["M_aero_Nm"]) / m_cap30, 3)])
            keys[tag] = tag if hk == "bemt" else f"{tag}_{hk}"
            out[keys[tag]] = rows
        rows_all = [r for t in ("target", "fwd") for r in out[keys[t]]]
        out[f"use_max_{hk}"] = max(r[7] for r in rows_all)
        out[f"v_at_use_max_{hk}"] = max((r[7], r[0]) for r in rows_all)[1]
        out[f"m_prop_max_{hk}"] = max(r[4] for r in rows_all)
        out[f"use_cap30_max_{hk}"] = max(r[8] for r in rows_all)
        out[f"v_at_use_cap30_max_{hk}"] = max((r[8], r[0]) for r in rows_all)[1]
        out[f"m_motor_noelev_max_{hk}"] = max(r[8] for r in rows_all) * m_cap30
    out["columns"] = ["V m/s", "alpha deg", "T/W", "M_aero N m (incl. signed prop term)", "M_prop N m (nose-up +)",
                      "M_elevon N m", "M_motor avail N m", "use (full differential, elevon credit)",
                      "use (30 % cap, no elevon credit)"]
    out["m_cap30_Nm"] = m_cap30
    out["use_max"] = out["use_max_bemt"]
    out["v_at_use_max"] = out["v_at_use_max_bemt"]
    out["tw_max"] = max(r[2] for r in out["target"])
    return out


kit.claim("CL-B3-TRANS-PITCH-USE-QS", "Transition, quasi-steady level pitch-over at hover thrust: |M_aero| / pitch "
          "moment at the 30 % cap, worst speed, prop normal force signed on B4's BEMT slope (information since D-149)",
          calc="CALC-B3-TRANSITION", output="use_cap30_max_bemt", unit="-",
          note="Design round 2026-11-14 (B3.md §2.1): the R5 value 0.909 added B4's H-force magnitude to |M_aero| with "
               "no sign; the H-force acts at the hubs ahead of the CG, nose-up, the same physics and sense as the "
               "Ribner term, against the nose-down wing moment. Signed on the BEMT slope this is 0.84. It describes a "
               "pitch-over at hover thrust, which D-149 no longer flies: the pass line is CL-B3-TRANS-PITCH-USE "
               "(time domain at the closure-round entry, ASM-B3-TRANS-T0)",
          how="SITL stage B (F4) with hover-throttle entry: logged pitch differential vs this value.")
kit.claim("CL-B3-TRANS-PITCH-USE-NOHUB-CAP30", "Transition, quasi-steady level at hover thrust, Ribner normal force "
          "only (information since D-149)", calc="CALC-B3-TRANSITION", output="use_cap30_max_nohub", unit="-",
          note="Information (closure round B3.md §2): the level pitch-over at hover thrust is a flight condition the "
               "entry procedure excludes (ASM-B3-TRANS-T0: transmitter sequence; F4 bars the other entry paths). The "
               "0.60 limit is unchanged and applies to the flown condition (CL-B3-TRANS-PITCH-USE). Not a loosened "
               "limit. If the condition occurs anyway, the trim stays < 1.0 of the cap (CL-B3-TRANS-PITCH-USE-HOVERTHR)",
          how="As CL-B3-TRANS-PITCH-USE-QS.")
kit.claim("CL-B3-TRANS-PITCH-USE-HMAX-CAP30", "Transition, quasi-steady level at hover thrust, prop normal force "
          "signed at the larger of Ribner and B4's hover-rpm H-force (information since D-149)",
          calc="CALC-B3-TRANSITION", output="use_cap30_max_hmax", unit="-",
          note="Information (closure round B3.md §2): the level pitch-over at hover thrust is a flight condition the "
               "entry procedure excludes (ASM-B3-TRANS-T0: transmitter sequence; F4 bars the other entry paths). The "
               "0.60 limit is unchanged and applies to the flown condition (CL-B3-TRANS-PITCH-USE). Not a loosened "
               "limit. If the condition occurs anyway, the trim stays < 1.0 of the cap (CL-B3-TRANS-PITCH-USE-HOVERTHR)",
          how="As CL-B3-TRANS-PITCH-USE-QS.")
kit.claim("CL-B3-TRANS-PITCH-USE-FULLDIFF", "Transition: pitch differential used against the full differential "
          "(lower pair to zero thrust) with elevon credit: the pre-CDR basis, information only",
          calc="CALC-B3-TRANSITION", output="use_max", unit="-", how="Not a pass line (CDR-AE-07).")
kit.claim("CL-B3-TRANS-MOTOR-MOMENT", "Largest motor pitch moment needed in the level pitch-over at hover thrust, "
          "no elevon credit, BEMT prop slope", calc="CALC-B3-TRANSITION", output="m_motor_noelev_max_bemt", unit="N*m",
          how="Fit of the pitch residual in the twin's transition log.")
kit.claim("CL-B3-TRANS-PITCH-USE-NOHUB", "Transition: pitch differential used, worst, Ribner normal force only (R4 basis)",
          calc="CALC-B3-TRANSITION", output="use_max_nohub", unit="-", limit=("<=", "ASM-B3-TRANS-USE-MAX"),
          how="As CL-B3-TRANS-PITCH-USE.")
kit.claim("CL-B3-TRANS-PITCH-USE-HMAX", "Transition: pitch differential used, worst, prop normal force signed at "
          "B4's hover-rpm H-force", calc="CALC-B3-TRANSITION", output="use_max_hmax", unit="-",
          limit=("<=", "ASM-B3-TRANS-USE-MAX"), how="As CL-B3-TRANS-PITCH-USE.")
kit.claim("CL-B3-TRANS-HUB-MOMENT", "Largest prop normal-force pitch moment (nose-up, signed) in the level "
          "pitch-over, B4's H-force at hover thrust", calc="CALC-B3-TRANSITION", output="m_prop_max_hhov", unit="N*m",
          how="Car-top rig side-force cell (CL-B4-SIM-H-MAX how) or a fit of the pitch residual in the transition log.")


@kit.calc("CALC-B3-TRANS-TD", title="Time-domain forward pitch-over as ArduPilot flies it (ANGLE_WAIT_FW, frozen "
          "throttle), entry per ASM-B3-TRANS-T0 at the edges of the ASM-B3-TRANS-REALISE band",
          assumes=["ASM-B3-TRANS-T0", "ASM-B3-TRANS-REALISE", "ASM-B3-FSW-TRANS", "ASM-B3-TD-LOOP", "ASM-B3-PROP-CNA",
                   "ASM-B3-B4-INC-V", "ASM-B3-ELEVON-TRANS", "ASM-B3-ELEVON-POST", "ASM-B3-CN90", "ASM-B3-CD0"],
          cites=["SRC-B3-AP-TAILSIT", "SRC-B3-AP-ATCMULTI"],
          inputs={**TRANS_IN, "Iyy": "CL-A3-IYY", "m_basic": "CL-A3-MASS-BASIC", "T0": "ASM-B3-TRANS-T0",
                  "rz": "ASM-B3-TRANS-REALISE", "fsw": "ASM-B3-FSW-TRANS", "loop": "ASM-B3-TD-LOOP",
                  "T_I45": "CL-B4-SIM-T-I45", "vs_trip": "CL-B2R3-VS-GATE-FWD-TURB"},
          units={**TRANS_U, "T0": "-,s", "fsw": "deg/s,deg,m/s", "loop": "rad/s,-", "vs_trip": "m/s"},
          equation="entry static thrust / W: T0_lo = dl_lo r (1 - e_lin), T0_nom = dl r, T0_hi = dl r (1 + e_lin) ; "
                   "vertical speed at the mode change w0_lo = k (T0_lo - dl_lo) g t_hold (credit), w0_hi = (T0_hi - 1) "
                   "g t_hold (no drag: climb bound) ; 2-D rigid body (flight_models.pitchover_td): theta_cmd = 90 - "
                   "RAT_FW t until the tilt > Q_TAILSIT_ANGLE, followed through wn, zeta ; T = T0 (1 - V cos a / Vp), "
                   "Vp = V_inc cos 45 / (1 - T_I45) ; M_need = Iyy th_dd - M_aero (wing + prop normal force k x "
                   "Ribner nose-up, k = B4 BEMT slope / Ribner) ; use_trim = max |M_aero| / (2 x 0.30 T_hover 2z) "
                   "over the pitch-over and the copter-assisted phase (V < Q_ASSIST_SPEED); V_done = V at "
                   "Q_TAILSIT_ANGLE ; Iyy scaled to the gate mass ; frac_sag = T0_hi W / (n Tmax sag)")
def trans_td(m, g, rho, S, c, b, x_t, x_fwd, xnp, cm_np_thin, dcm, CLa, a0, clmax, cd0, e, cn90, n, D, x_prop,
             cna, tmax, sag, z, dl, vc, CLd, Cmd_ref, xref, eta, dp, fpost, lo, li, va, slop, h_max, h_hov, dHdi,
             v_inc, dfrac, Iyy, m_basic, T0, rz, fsw, loop, T_I45, vs_trip):
    p = {"m": m, "g": g, "rho": rho, "S": S, "c": c, "b": b, "e": e, "a0": math.radians(a0), "CLa": CLa,
         "clmax": clmax, "cd0": cd0, "cn90": cn90, "n": n, "D": D, "x_prop": x_prop, "cna": cna,
         "cm_ac": cm_np_thin + dcm, "xnp": xnp, "dl": dl, "tmax": tmax * g * sag, "z": z, "dfrac": dfrac,
         "Iyy": Iyy * m / m_basic, "Vp": v_inc * math.cos(math.radians(45)) / (1 - T_I45), "Cmd_ref": Cmd_ref,
         "CLd": CLd, "xref": xref, "eta": eta, "lo": lo, "li": li, "va": va, "slop": slop, "fpost": fpost}
    k_bemt = dHdi / (cna * (math.pi * D * D / 4) * 0.5 * rho * v_inc ** 2)
    rate, ang, vas = fsw
    wn, zeta = loop
    r_ent, t_hold = T0
    dl_lo, e_lin, k_cl = rz
    t_lo, t_nom, t_hi = dl_lo * r_ent * (1 - e_lin), dl * r_ent, dl * r_ent * (1 + e_lin)
    w0_lo = k_cl * (t_lo - dl_lo) * g * t_hold
    w0_hi = (t_hi - 1.0) * g * t_hold
    out = {"Vp_ms": p["Vp"], "Iyy_kgm2": p["Iyy"], "k_prop_bemt": k_bemt, "T0_W_low_edge": t_lo,
           "T0_W_nominal": t_nom, "T0_W_high_edge": t_hi, "w0_credit_ms": w0_lo, "w0_max_ms": w0_hi,
           "preclimb_h_max_m": 0.5 * (t_hi - 1.0) * g * t_hold ** 2,
           "frac_sag_high_edge": t_hi * m / (n * tmax * sag), "frac_sag_nominal": t_nom * m / (n * tmax * sag),
           "throttle_in_at_theta_h_0p49": r_ent * 0.49}
    cases = {"T0_fwd": (x_fwd, t_lo, k_bemt, w0_lo), "T0_fwd_ribner": (x_fwd, t_lo, 1.0, w0_lo),
             "T0_target": (x_t, t_lo, k_bemt, w0_lo), "T0nom_fwd": (x_fwd, t_nom, k_bemt, w0_lo),
             "T0hi_fwd": (x_fwd, t_hi, k_bemt, w0_hi), "T0lo_nopreclimb_fwd": (x_fwd, t_lo, k_bemt, 0.0),
             "hov_fwd": (x_fwd, None, k_bemt, 0.0), "hov_fwd_ribner": (x_fwd, None, 1.0, 0.0)}
    for tag, (x, tw, kp, w0) in cases.items():
        r = FM.pitchover_td(p, x, T0_W=tw, rate=rate, ang_done=ang, v_assist=vas, wn=wn, zeta=zeta, kprop=kp, w0=w0)
        out[f"use_trim_{tag}"] = max(r["max_trim_only_pitchover"], r["peak_fw_assist"])
        out[f"use_trim_po_{tag}"] = r["max_trim_only_pitchover"]
        out[f"use_peak_incl_dyn_{tag}"] = r["peak_pitchover"]
        out[f"use_fw_assist_{tag}"] = r["peak_fw_assist"]
        out[f"sustained_0p5s_{tag}"] = r["sustained_pitchover"]
        out[f"V_done_{tag}"] = r["V_done"]
        out[f"t_done_{tag}"] = r["t_done_s"]
        out[f"t_stalled_fw_{tag}"] = r["t_stalled_fw_s"]
        out[f"alt_change_{tag}"] = r["alt_change_m"]
        out[f"lower_motor_N_{tag}"] = r["lower_motor_N_at_peak"]
        out[f"peak_with_gust3_{tag}"] = r["peak_use30_gust"]
        out[f"T0_N_{tag}"] = r["T0_N"]
    for tag, (tw, w0) in {"T0_fwd": (t_lo, w0_lo), "T0hi_fwd": (t_hi, w0_hi)}.items():
        r2 = FM.pitchover_td(p, x_fwd, T0_W=tw, rate=rate, ang_done=ang, v_assist=vas, wn=wn, zeta=zeta,
                             kprop=k_bemt, gust_w=2.0, w0=w0)
        out[f"peak_with_gust2_{tag}"] = r2["peak_use30_gust"]
    out["gust2_worst_edge"] = max(out["peak_with_gust2_T0_fwd"], out["peak_with_gust2_T0hi_fwd"])
    out["V_done_margin_T0_fwd"] = out["V_done_T0_fwd"] - vs_trip
    out["climb_max_incl_preclimb_m"] = out["alt_change_T0hi_fwd"] + out["preclimb_h_max_m"]
    return out


TD_NOTE = ("Closure round 2026-11-14 (review/CLOSURE-ROUND-2026-11-14/B3.md): evaluated at the LOW thrust edge of the "
           "entry band (dl_true 1.025, linearisation -2 %), with the pre-climb credit; the high edge sets the B1 "
           "thrust fraction (CL-B3-TRANS-ENTRY-FRAC-SAG). Design round: D-149, B3-W2.md")
kit.claim("CL-B3-TRANS-PITCH-USE", "Transition: trim pitch moment / pitch moment at the 30 % differential cap, "
          "time-domain pitch-over as the firmware flies it, entry per ASM-B3-TRANS-T0 at the low thrust edge, forward "
          "CG, prop normal force signed on B4's BEMT slope, no elevon credit in the pitch-over",
          calc="CALC-B3-TRANS-TD", output="use_trim_T0_fwd", unit="-", limit=("<=", "ASM-B3-TRANS-USE-MAX"),
          verifies=["R-TRANSITION"], assumes=["ASM-B3-TRANS-T0", "ASM-B3-TRANS-REALISE"],
          note=TD_NOTE + ". History: 0.909 (QS, unsigned H) -> 0.348 at 1.4 W (D-149) -> this. Hover-throttle entry: "
               "CL-B3-TRANS-PITCH-USE-HOVERTHR (information; that entry is not flown)",
          how="F4 SITL S4c confirms the held throttle (logic); stage B with the K09-L aero; twin transitions: RCOU "
              "upper vs lower pair, pitch differential <= 0.60 x 30 % of hover thrust except transients < 0.5 s.")
kit.claim("CL-B3-TRANS-ENTRY-FRAC-SAG", "Transition entry: static thrust at the HIGH edge of the entry band / "
          "sagged-pack maximum thrust at the gate mass (the R-TRANSITION 20 % control reserve)",
          calc="CALC-B3-TRANS-TD", output="frac_sag_high_edge", unit="-", limit=("<=", "ASM-B1-CTRL-RESERVE"),
          verifies=["R-TRANSITION"], assumes=["ASM-B3-TRANS-T0", "ASM-B3-TRANS-REALISE"],
          note="A2 closure §2.3: D-149's 1.4 W gave 1.4 / 1.7456 = 0.802. B1's CL-B1-TRANS-THRUST should read "
               "T0_W_high_edge from CALC-B3-TRANS-TD as the held thrust (frozen-throttle law)",
          how="Stand thrust at the entry throttle (T-E1-STAND) / the sagged maximum; transition RCOU log.")
kit.claim("CL-B3-TRANS-T0-HIGH", "Transition entry: static thrust / weight at the high edge of the entry band "
          "(input for B1)", calc="CALC-B3-TRANS-TD", output="T0_W_high_edge", unit="-",
          how="As CL-B3-TRANS-ENTRY-FRAC-SAG.")
kit.claim("CL-B3-TRANS-T0-LOW", "Transition entry: static thrust / weight at the low edge of the entry band",
          calc="CALC-B3-TRANS-TD", output="T0_W_low_edge", unit="-", how="As CL-B3-TRANS-ENTRY-FRAC-SAG.")
@kit.calc("CALC-B3-TRANS-FRAC-E1", title="Entry thrust fraction on E1's own worst-state T/W (final re-run)",
          equation="frac = T0_high / TW_worst ; T0_high = CL-B3-TRANS-T0-HIGH (static thrust / W at the high edge of the "
                   "entry band) ; TW_worst = CL-E1-TW-WORST-RBAND (E1: axial thrust / W at the gate, 80 A limiter, "
                   "3.73 V/cell, 10 C, 80 C winding, R_m +10 %, sensor tolerance). No cos(cant) credit (conservative)",
          inputs={"t0": "CL-B3-TRANS-T0-HIGH", "tw": "CL-E1-TW-WORST-RBAND"})
def trans_frac_e1(t0, tw):
    return {"frac": t0 / tw}


kit.claim("CL-B3-TRANS-ENTRY-FRAC-E1", "Transition entry: static thrust at the HIGH edge of the entry band / E1's worst-state "
          "thrust (E1 CL-E1-TW-WORST-RBAND)", calc="CALC-B3-TRANS-FRAC-E1", output="frac", unit="-",
          limit=("<=", "ASM-B1-CTRL-RESERVE"), verifies=["R-TRANSITION"],
          note="Final re-run 2026-11-14: params thrust_max_per_motor_kg x voltage_sag are the 75 A values (A1 to re-base to E1's "
               "80 A band edge); this claim reads E1's worst-state T/W directly",
          how="Same as CL-B3-TRANS-ENTRY-FRAC-SAG: log the throttle and thrust at the entry on the stand (T-E1-STAND).")
kit.claim("CL-B3-TRANS-PITCH-USE-HOVERTHR", "Transition, time domain, entry at hover throttle (not flown: every "
          "forward transition starts through ASM-B3-TRANS-T0), forward CG: trim use of the 30 % cap in the pitch-over",
          calc="CALC-B3-TRANS-TD", output="use_trim_po_hov_fwd", unit="-",
          note="After the handover (below the tripped stall) the copter-assisted phase needs use_fw_assist_hov_fwd of "
               "the cap, stalled for t_stalled_fw_hov_fwd s (CALC-B3-TRANS-TD outputs). Still < 1.0 of the 30 % cap: "
               "an unplanned hover-throttle entry eats the gust / rate reserve; it does not saturate",
          how="SITL S4c with a hover-throttle entry (information).")
kit.claim("CL-B3-TRANS-PITCH-USE-NOPRECLIMB", "Transition, time domain, low thrust edge entered from a steady hover "
          "(pre-climb skipped; information: the transmitter sequence enforces the hold)", calc="CALC-B3-TRANS-TD",
          output="use_trim_T0lo_nopreclimb_fwd", unit="-", how="As CL-B3-TRANS-PITCH-USE.")
kit.claim("CL-B3-TRANS-GUST2-T0", "Transition, time domain, entry band edges, forward CG: trim plus the moment of a "
          "2 m/s vertical gust at every point, fraction of the 30 % cap (the reserve the 0.60 limit holds)",
          calc="CALC-B3-TRANS-TD", output="gust2_worst_edge", unit="-", limit=("<=", 1.0),
          note="The gust increment uses atan(w / V): at low speed it over-states (a near-hover 'vertical gust' is "
               "largely axial); the 3 m/s column is peak_with_gust3_T0_fwd (information)",
          how="SITL stage B with the turbulence model; twin transitions in light wind first.")
kit.claim("CL-B3-TRANS-PITCH-USE-T0-TARGET", "Transition, time domain, low thrust edge, target CG: trim use of the "
          "30 % cap", calc="CALC-B3-TRANS-TD", output="use_trim_T0_target", unit="-",
          how="As CL-B3-TRANS-PITCH-USE.")
kit.claim("CL-B3-TRANS-V-HANDOVER", "Transition, time domain, low thrust edge, forward CG: airspeed when the tilt "
          "reaches Q_TAILSIT_ANGLE (plane controller takes over)", calc="CALC-B3-TRANS-TD", output="V_done_T0_fwd",
          unit="m/s", limit=(">=", "CL-B2R3-VS-GATE-FWD-TURB"), verifies=["R-TRANSITION"],
          note="Q_ASSIST_SPEED 14 m/s keeps the motors stabilising below 14; at hover-throttle entry the handover is "
               "below the tripped stall (CL-B3-TRANS-V-HANDOVER-HOVERTHR)",
          how="SITL stage B and twin logs: airspeed at the 'Transition FW done' message.")
kit.claim("CL-B3-TRANS-V-HANDOVER-HOVERTHR", "Transition, time domain, hover-throttle entry, forward CG: airspeed at "
          "Q_TAILSIT_ANGLE (information)", calc="CALC-B3-TRANS-TD", output="V_done_hov_fwd", unit="m/s",
          how="As CL-B3-TRANS-V-HANDOVER.")
kit.claim("CL-B3-TRANS-CLIMB", "Transition, time domain, high thrust edge with the most pre-climb: height gained from "
          "the start of the pre-climb to 17 m/s", calc="CALC-B3-TRANS-TD", output="climb_max_incl_preclimb_m",
          unit="m", limit=("<=", 60.0), how="Twin logs; H2 / H3 start first transitions at 50 m AGL (fence 110 m: 50 + this < 110, so this <= 60; limit added in the final re-run).")
kit.claim("CL-B3-TRANS-LOWER-MOTOR", "Transition, time domain, low thrust edge, forward CG: lower-pair thrust per "
          "motor at the pitch-use peak", calc="CALC-B3-TRANS-TD", output="lower_motor_N_T0_fwd", unit="N",
          limit=(">=", 0.0), how="RCOU of the lower pair at the peak (twin transitions).")


# ---------------------------------------------------------------------------------------------- belly into wind
# D-152 (A1.md, C5.md): land belly (-z face, the copter nose) into the wind. B3 confirms the heading stability under
# Q_WVANE (NOSE_IN) at 5 m/s and in the 8 m/s gust.
kit.source("SRC-B3-AP-WVANE", "ArduPilot libraries/AC_AttitudeControl/AC_WeatherVane.cpp at tag Plane-4.7.2", "web",
           url="https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/libraries/AC_AttitudeControl/"
               "AC_WeatherVane.cpp", checked="2026-11-14",
           where="get_yaw_out, NOSE_IN: output = max(|roll| - ANG_MIN, 0) with the sign of roll (pitch used only with "
                 "OPTIONS bit 0), x GAIN through a 0.98 / 0.02 low-pass; parameter defaults ANG_MIN 1.0 deg, HGT_MIN 0, "
                 "SPD_MAX 0 and VELZ_MAX 0 on Plane (checks off); off while pilot yaw is non-zero")
kit.assumption("ASM-B3-WVANE", "Weathervane settings [Q_WVANE_GAIN, Q_WVANE_ANG_MIN deg]",
               "Yaw rate demand deg/s per deg of roll lean beyond the dead zone, NOSE_IN (belly into wind)",
               basis="subsystems/flight-software/K09L.param Q_WVANE_ENABLE 1, Q_WVANE_GAIN 1; Q_WVANE_ANG_MIN not set, "
                     "firmware default 1.0 deg (AC_WeatherVane.cpp)", value=[1.0, 1.0], unit="-,deg",
               cites=["SRC-B3-AP-WVANE"])


@kit.calc("CALC-B3-HOVER-BELLY", title="Hover yaw with the belly into the wind (D-152): aerodynamic yaw stiffness and "
          "the weathervane dead band",
          inputs={**HOV_IN, "Vg": P + "requirements.gust_survive_ms", "z_cg": P + "cg.z_target_m",
                  "wv": "ASM-B3-WVANE"},
          units={**HOV_U, "Vg": "m/s", "z_cg": "m", "wv": "-,deg"},
          assumes=["ASM-B3-CN90", "ASM-B3-HOVER-DIFF", "ASM-B3-WVANE"], cites=["SRC-B3-AP-WVANE"],
          equation="heading error psi from belly-into-wind ; wing broadside (restoring): M_w = q S CN90 cos psi e_w, "
                   "e_w = 0.75 sin psi / (4 + pi cos psi) b (Kirchhoff CP shift toward the upwind tip, the form of "
                   "M_fin in CALC-B3-HOVER-WTIP) ; upwind half-fins (destabilising, CP upwind of the CG): F_f = 2 kq q "
                   "a_f psi fc fh, a_f = 2 pi A / (2 + sqrt(A^2 + 4)), A = fc / fh (Helmbold, EST), kq = (u/U)^2 at "
                   "the fin quarter chord in front of a plate normal to the flow, u/U = x / sqrt(x^2 + (c/2)^2), "
                   "x = 0.75 fh, and kq = 1 as a bound ; arm = 0.75 fh + z_cg ; downwind half-fins in the wake: 0 "
                   "(their moment is restoring, so leaving them out is conservative) ; props: H-forces cancel in "
                   "y/z-symmetric pairs ; M_net = M_w - M_f (restoring +) ; weathervane: roll lean phi = atan(F_f / "
                   "W) ; dead band psi_db where phi = ANG_MIN ; with a roll trim error d the band reaches "
                   "(ANG_MIN + d) on one side ; M_ctrl = 4 dT (kq_iso f_low + r sin cant)")
def hover_belly(m, g, dl, split, tmax, sag, y, z, Qh, swirl, cant, dfrac, Ixx, Iyy, Izz, m_basic, rho, Vw, S, c, b,
                x_t, cn90, xcp, fc, fh, fle, asym, fac, amin, swirl_lo, Vg, z_cg, wv):
    W = m * g
    Th = W * dl / 4
    M_ctrl = 4 * dfrac * Th * (Qh / Th * swirl_lo + math.hypot(y, z) * math.sin(math.radians(cant)))
    A = fc / fh
    a_f = 2 * math.pi * A / (2 + math.sqrt(A * A + 4))
    xq = 0.75 * fh
    kq = (xq / math.hypot(xq, c / 2)) ** 2
    arm = 0.75 * fh + z_cg
    gain, ang_min = wv

    def mw(psi, V):
        q, p_ = 0.5 * rho * V * V, math.radians(psi)
        return q * S * cn90 * math.cos(p_) * 0.75 * math.sin(p_) / (4 + math.pi * math.cos(p_)) * b

    def ff(psi, V, k):
        return 2 * k * 0.5 * rho * V * V * a_f * math.radians(psi) * fc * fh

    def lean_deg(psi, V, k):
        return math.degrees(math.atan(ff(psi, V, k) / W))

    def psi_at_lean(phi, V, k):
        lo, hi = 0.0, 60.0
        if lean_deg(hi, V, k) < phi:
            return hi
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if lean_deg(mid, V, k) < phi else (lo, mid)
        return 0.5 * (lo + hi)

    out = {"M_ctrl_Nm": M_ctrl, "fin_cla_per_rad": a_f, "kq_fin": kq, "fin_arm_m": arm}
    for vt, V in (("5", Vw), ("gust", Vg)):
        for psi in (10.0, 20.0, 30.0):
            for kt, k in (("", kq), ("_kq1", 1.0)):
                Mf = ff(psi, V, k) * arm
                net = mw(psi, V) - Mf
                out[f"M_net_{psi:.0f}deg_{vt}{kt}_Nm"] = net
                if net < 0:
                    out[f"ctrl_over_destab_{psi:.0f}deg_{vt}{kt}"] = M_ctrl / -net
            out[f"M_wing_{psi:.0f}deg_{vt}_Nm"] = mw(psi, V)
            out[f"M_fin_{psi:.0f}deg_{vt}_Nm"] = ff(psi, V, kq) * arm
            out[f"lean_{psi:.0f}deg_{vt}_deg"] = lean_deg(psi, V, kq)
        out[f"stiffness_{vt}_Nm_per_rad"] = (mw(1.0, V) - ff(1.0, V, kq) * arm) / math.radians(1.0)
        out[f"stiffness_{vt}_kq1_Nm_per_rad"] = (mw(1.0, V) - ff(1.0, V, 1.0) * arm) / math.radians(1.0)
        out[f"deadband_{vt}_deg"] = psi_at_lean(ang_min, V, kq)
        out[f"deadband_{vt}_kq1_deg"] = psi_at_lean(ang_min, V, 1.0)
        out[f"deadband_trim1deg_{vt}_deg"] = psi_at_lean(ang_min + 1.0, V, kq)
        out[f"yaw_rate_30deg_{vt}_degs"] = gain * max(lean_deg(30.0, V, kq) - ang_min, 0.0)
    return out


kit.claim("CL-B3-HOVER-BELLY-YAW-NET-30", "Belly into a 5 m/s wind, 30 deg heading error: aerodynamic yaw moment "
          "toward belly-into-wind (wing broadside restoring less the upwind half-fins, fin q not reduced)",
          calc="CALC-B3-HOVER-BELLY", output="M_net_30deg_5_kq1_Nm", unit="N*m", limit=(">=", 0.0),
          verifies=["R-WIND"],
          note="D-152 condition 'B3 confirms weathervane stability'. EST model: Kirchhoff CP shift on a plate of "
               "aspect ratio 0.28 and a low-AR fin slope; > 0 means the heading is statically stable about "
               "belly-into-wind without any yaw control",
          how="Twin hover logs (C5 M2): heading error and yaw RCOU at touchdown with the belly to the wind; hanging "
              "yaw test in a measured 5 m/s wind (free to yaw, motors off): the aircraft settles belly to the wind.")
kit.claim("CL-B3-HOVER-BELLY-YAW-STIFF", "Belly into a 5 m/s wind: aerodynamic yaw stiffness about belly-into-wind "
          "(restoring +, fin q reduced in front of the wing)", calc="CALC-B3-HOVER-BELLY",
          output="stiffness_5_Nm_per_rad", unit="N*m/rad", limit=(">=", 0.0), verifies=["R-WIND"],
          how="As CL-B3-HOVER-BELLY-YAW-NET-30.")
kit.claim("CL-B3-HOVER-BELLY-WVANE-DEADBAND", "Belly into a 5 m/s wind: heading error at which the roll lean reaches "
          "Q_WVANE_ANG_MIN (inside it the weathervane does not act; the heading stays where the controller holds it)",
          calc="CALC-B3-HOVER-BELLY", output="deadband_5_deg", unit="deg",
          note="Compare with the +/-30 deg of D-152 (C5's 5.7 m/s at +/-30 deg)",
          how="F4 SITL (D-152 condition): heading within +/-30 deg through touchdown in a 5 m/s crosswind; twin logs.")
kit.claim("CL-B3-HOVER-BELLY-WVANE-DEADBAND-TRIM1", "As CL-B3-HOVER-BELLY-WVANE-DEADBAND with a 1 deg roll trim error "
          "(the one-sided band)", calc="CALC-B3-HOVER-BELLY", output="deadband_trim1deg_5_deg", unit="deg",
          how="H1 AHRS trim (level calibration) before the twin flights; twin logs.")
kit.claim("CL-B3-HOVER-BELLY-YAW-NET-30-GUST", "Belly into the 8 m/s gust, 30 deg heading error: aerodynamic yaw moment "
          "toward belly-into-wind (fin q not reduced)", calc="CALC-B3-HOVER-BELLY", output="M_net_30deg_gust_kq1_Nm",
          unit="N*m", how="As CL-B3-HOVER-BELLY-YAW-NET-30.")


# ---------------------------------------------------------------------------------------------- tests (planned)
kit.test("T-B3-CG-BALANCE", "CG balance at the limits", verifies=["CL-B3-V-CG-FWD", "CL-B3-V-CG-AFT-ENV", "CL-B3-V-CG-TARGET"],
         procedure="H1: balance the ready-to-fly aircraft on two fingertips (or a knife-edge jig) at the fin roots; "
                   "the balance line must lie between the two marks drawn at the B3 limits.")
kit.test("T-B3-TWIN-NP", "Twin neutral point from glides", verifies=["CL-B3-XNP", "CL-B3-V-XNP-ENV", "CL-B3-V-SM-TARGET-ENV"],
         procedure="Twin, FBWA glides at 3 speeds for 2 pack positions; plot elevon trim vs CL; Xnp where the slope is 0.")
kit.test("T-B3-YAW-DOUBLET", "Twin FW yaw doublet", verifies=["CL-B3-CNB", "CL-B3-DR-ZETA"],
         procedure="Twin in FBWA at 1.3 Vs, 50 m AGL, CG on the aft mark: yaw pulse by differential thrust; heading and "
                   "sideslip return within 2 s, yaw-rate oscillation decays.")
kit.test("T-B3-HOVER-YAW-WTIP", "Twin (TW3): QHOVER at 5 m/s measured wind with a wingtip into the wind, yaw steps of "
         "+/-10 and +/-20 deg", verifies=["CL-B3-HOVER-YAW-WTIP-10", "CL-B3-HOVER-YAW-WTIP-20"],
         procedure="Hold heading with a wingtip into wind (Q_WVANE off for the test, heading by stick), step the heading "
                   "+/-10 then +/-20 deg and release. Pass: heading returns, yaw RCOU spread (diagonal pairs) <= 30 % "
                   "of hover output. Confirmation (closure round): the claim passes at the cross-flow Cd upper bound "
                   "(CL-B3-HOVER-YAW-WTIP-20-CDMAX); a reading above 1.023 x model would mean the model form is wrong "
                   "(not the Cd), and B3 re-opens the claim with the measured moment; the 10 deg spares exist for that.")
kit.test("T-B3-HOVER-WIND", "Hover authority in wind",
         verifies=["CL-B3-HOVER-PITCH-RATIO", "CL-B3-HOVER-ROLL-RATIO", "CL-B3-HOVER-YAW-RATIO"],
         procedure="Tethered then free hover at 5 m/s measured wind; no motor output above 85 % or below 10 % (RCOU).")


if __name__ == "__main__":
    kit.write()
    res = {n["id"]: n.get("outputs") for n in kit.nodes.values() if n["type"] == "calculation"}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "sc_results.json").write_text(json.dumps(res, indent=1, default=str))
    print("wrote results/sc_results.json")
