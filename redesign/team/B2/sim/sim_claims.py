"""B2 verification-round claims (B2-R3) for the proof chain: wing aero on the settled geometry and A3 roll-up.

Run from the repo root after verify_wing.py, stall_zcg.py (B2-R4) and cfd2d_section.py (then verify_wing.py --params):
    python -I redesign/team/B2/sim/sim_claims.py      -> team/B2/sim/claims.sim.json
then python -I redesign/proofs/build_graph.py.
Reads P:b2sim.* (sim/params.json), P:b2.* (team/B2/params.json), params.json, mechanisms params, and claims of
B3 (CL-B3-V-XNP, -XNP-AERO), B1 (CL-B1V-CLMAX-SIM, P:b1sim.avl.xnp_m), A3 (CL-A3-MASS-PREDICTED, CL-A3-CG-X, CL-A3-CG-X-PRED) and D6 (CL-D6-TORQUE-FACTOR).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../../params/params.json", "../params.json", "params.json", "params.zcg.json",
                               "../../../subsystems/mechanisms/params.json", "../../B1/params.json"],
             out="claims.sim.json")
G_KGF = 9.80665
WING = ["WNG-001", "WNG-002", "WNG-003"]

kit.source("SRC-B2-SU2", "SU2 8.5 2-D RANS runs, team/B2/sim/cfd2d_section.py", "web",
           url="https://su2code.github.io",
           where="team/B2/sim/out/cfd2d_results.json; INC_RANS Spalart-Allmaras fully turbulent, gmsh meshes "
                 "9k/18k/36k cells (refinement sqrt 2), quad boundary layer, far field 50 c",
           note="fully turbulent: no laminar separation bubble, so clmax and hinge moments bracket XFOIL rather than "
                "replace it; not compared with test data at this Re")

kit.assumption("ASM-B2R4-PROPS-NP", "Props and pod enter the stall trim as a CL-independent NP shift",
               "The AVL model (wing + fins, props off, no pod) is run with its moment reference at x_cg + dprop, "
               "dprop = CL-B3-V-XNP-AERO - CL-B3-V-XNP (B3's Ribner prop and pod terms, 2.9 mm), and at the real CG "
               "height z_cg; the trimmed CLmax is then read directly at the CG point (no static-margin mapping)",
               basis="B3 treats the same terms as CL-independent and uses the same shift in its stall calc "
                     "(verify_asdesigned.py stall_v); the pod carries no elevon and the first-stall strip (y 0.071 m) "
                     "is the inboard elevon end, outside the pod's 0.07 m half-width", status="UNVERIFIED")
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


def bilin(xg, zg, tab, x, z):
    """Bilinear interpolation in tab[x index][z index]; linear extrapolation by the end cells."""
    def cell(gr, v):
        i = 0 if v <= gr[0] else (len(gr) - 2 if v >= gr[-1] else max(j for j in range(len(gr) - 1) if gr[j] <= v))
        return i, (v - gr[i]) / (gr[i + 1] - gr[i])
    i, fx = cell(xg, x)
    j, fz = cell(zg, z)
    return ((1 - fx) * (1 - fz) * tab[i][j] + fx * (1 - fz) * tab[i + 1][j] + (1 - fx) * fz * tab[i][j + 1]
            + fx * fz * tab[i + 1][j + 1])


@kit.calc("CALC-B2R4-STALL-Z", title="Stall speed at the CG points with the CG height (D-62)",
          equation="CLmax = kd * bilinear(x_cg, z_cg; AVL critical-section grid run with Xref = x + dprop, "
                   "Zref = z); Vs = sqrt(2 m g / (rho b c CLmax)); Re correction CLmax *= 1 + s (Re_s - Re_x)/1e5; "
                   "Vtr = k Vs; SM_fwd = (Xnp_B3 - x_fwd)/c (B3 whole-aircraft NP, alpha 4 deg, CG height)",
          inputs={"xg": "P:b2sim.zcg.x_grid_m", "zg": "P:b2sim.zcg.z_grid_m", "tab": "P:b2sim.zcg.clmax_grid",
                  "etab": "P:b2sim.zcg.elevon_grid", "xr": "P:cg.x_range_m", "xt": "P:cg.x_target_m",
                  "zt": "P:cg.z_target_m", "zr": "P:cg.z_range_m", "xnp": "CL-B3-V-XNP",
                  "xbf": "CL-A3-CG-X", "xp": "CL-A3-CG-X-PRED", "kd": "ASM-B2-CLMAX-KD",
                  "mg": "P:requirements.mtow_gate_kg", "mp": "CL-A3-MASS-PREDICTED", "g": "P:env.g_ms2",
                  "rho": "P:env.rho_kgm3", "b": "P:wing.span_m", "c": "P:wing.chord_m",
                  "k": "P:requirements.transition_factor", "s": "P:b2sim.xfoil.clmax_re_slope_per_1e5",
                  "rex": "P:b2.xfoil.re_stall", "vmax": "P:requirements.stall_max_ms"},
          units={"vmax": "m/s", "xg": "m", "zg": "m", "xr": "m", "xt": "m", "zt": "m", "zr": "m", "xnp": "m", "xp": "m",
                 "mg": "kg", "mp": "kg", "g": "m/s2", "rho": "kg/m3", "b": "m", "c": "m"},
          assumes=["ASM-B2R4-PROPS-NP", "ASM-B2-CLMAX-KD"])
def stall(xg, zg, tab, etab, xr, xt, zt, zr, xnp, xbf, xp, kd, mg, mp, g, rho, b, c, k, s, rex, vmax):
    out = {}
    pts = {"fwd": (xr[0], zt), "aft": (xr[1], zt), "target": (xt, zt), "basic": (xbf * c, zt), "pred": (xp, zt),
           "fwd_zlo": (xr[0], zr[0]), "fwd_z0": (xr[0], 0.0)}
    for tag, (x, z) in pts.items():
        cl = kd * bilin(xg, zg, tab, x, z)
        for mtag, m in (("gate", mg), ("predm", mp)):
            vs = math.sqrt(2 * m * g / (rho * b * c * cl))
            re_s = vs * c / 1.48e-5
            clc = cl * (1 + s * (re_s - rex) / 1e5)                 # one Re iteration is enough (|dRe| < 0.2e5)
            vs = math.sqrt(2 * m * g / (rho * b * c * clc))
            out[f"Vs_{tag}_{mtag}"] = vs
            out[f"Vtr_{tag}_{mtag}"] = k * vs
        out[f"CLmax_{tag}"] = cl
        out[f"elev_{tag}"] = bilin(xg, zg, etab, x, z)
    out["SM_fwd"] = (xnp - xr[0]) / c
    out["Vs_fwd_z_gain"] = out["Vs_fwd_z0_gate"] - out["Vs_fwd_gate"]

    def vs_at(x, z):
        cl = kd * bilin(xg, zg, tab, x, z)
        vs = math.sqrt(2 * mg * g / (rho * b * c * cl))
        return math.sqrt(2 * mg * g / (rho * b * c * cl * (1 + s * (vs * c / 1.48e-5 - rex) / 1e5)))

    def solve(f, lo, hi):            # f decreasing in its argument; bisection for f = vmax
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if f(mid) > vmax else (lo, mid)
        return 0.5 * (lo + hi)
    out["x_fwd_stall_at_zlo"] = solve(lambda x: vs_at(x, zr[0]), xg[0], xg[-1])
    out["z_min_stall_at_xfwd"] = solve(lambda z: vs_at(xr[0], z), zg[0], zg[-1])
    out["dx_fwd_needed_at_zlo"] = out["x_fwd_stall_at_zlo"] - xr[0]
    return out


@kit.calc("CALC-B2R4-RECON", title="CR-B1-23: B1 vs B2 trimmed CLmax and NP, one modelling change per step",
          equation="W0 = B1 set-up in the B2 AVL model (x 0.0536, z 0.018, no props/pod, cm_t 0, B1 stall-Re clmax "
                   "table) -> W1 B2 raw stall-Re table -> W2 B2 envelope -> W3 + viscous cm trim -> W4 + props/pod "
                   "shift; repro = W0 / CLmax_B1 - 1; NP: props-off effective Xnp at CL 0.414 with z 0.0185 minus "
                   "B1's Xnp (Zref 0.018); dprop_drift = |dprop used - (CL-B3-V-XNP-AERO - CL-B3-V-XNP)|",
          inputs={"w": "P:b2sim.zcg.recon_clmax", "we": "P:b2sim.zcg.recon_elevon", "b1": "CL-B1V-CLMAX-SIM",
                  "np_z": "P:b2sim.zcg.xnp_aero_z0185_cruise", "np_0": "P:b2sim.zcg.xnp_aero_z0_cruise",
                  "np_b1": "P:b1sim.avl.xnp_m", "np_a0": "P:b2sim.avl.xnp_props_off_m",
                  "dprop": "P:b2sim.zcg.dprop_m", "xa": "CL-B3-V-XNP-AERO", "xw": "CL-B3-V-XNP"},
          units={"np_z": "m", "np_0": "m", "np_b1": "m", "np_a0": "m", "dprop": "m", "xa": "m", "xw": "m"})
def recon(w, we, b1, np_z, np_0, np_b1, np_a0, dprop, xa, xw):
    return {"repro": w["W0"] / b1 - 1, "d_table": w["W1"] - w["W0"], "d_envelope": w["W2"] - w["W1"],
            "d_cmt": w["W3"] - w["W2"], "d_props": w["W4"] - w["W3"], "W4": w["W4"], "elev_W0": we["W0"],
            "np_vs_b1": np_z - np_b1, "np_z_shift": np_z - np_0, "np_trim_vs_a0": np_0 - np_a0,
            "dprop_drift": abs(dprop - (xa - xw))}


@kit.calc("CALC-B2R3-STALL-TURB", title="Stall at the forward CG if the boundary layer were turbulent from the LE",
          equation="CLmax' = CLmax_fwd * clmax_turb / clmax_free; Vs' = Vs_fwd sqrt(clmax_free / clmax_turb); "
                   "clmax_turb = XFOIL tripped at 2 % c (lower bound) or SU2 SA L2 sweep max",
          inputs={"vs": "CL-B2R3-VS-GATE-FWD", "su2": "P:b2sim.cfd.clmax_2d", "trip": "P:b2sim.xfoil.clmax_tripped",
                  "xf": "P:b2.xfoil.clmax_2d_stall"},
          units={"vs": "m/s"})
def stall_turb(vs, su2, trip, xf):
    return {"ratio_trip": trip / xf, "Vs_trip": vs * math.sqrt(xf / trip),
            "ratio_su2": su2 / xf, "Vs_su2": vs * math.sqrt(xf / su2), "su2_over_trip": su2 / trip}


kit.assumption("ASM-B2R3-FB2", "Second stall fallback (pre-computed, CDR-15 / CDR-AE-06)",
               "AIRSPEED_MIN = AIRSPEED_CRUISE = 18 m/s with AIRSPEED_MAX 20 m/s, used if T-B2-STALL measures a gate-mass "
               "stall between 13.07 and 13.85 m/s. PROPOSED: AIRSPEED_MAX 20 needs A1 / C1 to accept 0.5 m/s to VA",
               basis="review/CDR-2026-11-13/CDR-aero.md CDR-AE-06; board decision B6 makes 17 the baseline (first "
                     "fallback of D-96)", value={"airspeed_min": 18.0, "airspeed_max": 20.0, "baseline_min": 17.0},
               unit="m/s", status="PROPOSED")


@kit.calc("CALC-B2R3-FALLBACK", title="Stall the B6 baseline (17 m/s) and the second fallback (18 m/s) hold to",
          equation="Vs_keep = AIRSPEED_MIN / f ; clmax ratio covered = (Vs_free / Vs_keep)^2 ; third step = "
                   "ceil(f x Vs_su2)",
          inputs={"vs": "CL-B2R3-VS-GATE-FWD", "vtrip": "CL-B2R3-VS-GATE-FWD-TURB", "su2": "P:b2sim.cfd.clmax_2d",
                  "xf": "P:b2.xfoil.clmax_2d_stall", "f": "P:requirements.transition_factor", "fb": "ASM-B2R3-FB2",
                  "va": "ASM-B2R3-VA"},
          units={"vs": "m/s", "vtrip": "m/s"}, assumes=["ASM-B2R3-FB2"])
def fallback(vs, vtrip, su2, xf, f, fb, va):
    vs_su2 = vs * math.sqrt(xf / su2)
    k17, k18 = fb["baseline_min"] / f, fb["airspeed_min"] / f
    return {"vs_keep_17": k17, "vs_keep_18": k18, "trip_margin_17": k17 - vtrip, "trip_margin_18": k18 - vtrip,
            "clmax_ratio_17": (vs / k17) ** 2, "clmax_ratio_18": (vs / k18) ** 2, "vs_su2": vs_su2,
            "su2_short_18": vs_su2 - k18, "min_needed_su2": float(math.ceil(f * vs_su2)),
            "max_fb2": fb["airspeed_max"], "va_margin_fb2": va - fb["airspeed_max"]}


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
how_stall = ("T-B2-STALL at the gate mass, the marked forward CG and the CG height read on the balance rig; "
             "CLmax = 2 m g / (rho S Vs^2)")
ST = "CALC-B2R4-STALL-Z"
RC = "CALC-B2R4-RECON"
kit.claim("CL-B2R3-SM-FWD", "Static margin at the forward CG limit, B3 whole-aircraft NP (CG height)", calc=ST,
          output="SM_fwd", unit="-", how="(CL-B3-V-XNP - cg.x_range_m[0]) / c; CG balance test T-A3-CG-BALANCE",
          note="information only: since B2-R4 the stall is read directly at (x, z), not through a static margin")
kit.claim("CL-B2R3-CLMAX-FWD", "Trimmed CLmax at the forward CG limit and the CG height", calc=ST,
          output="CLmax_fwd", unit="-", parts=WING, how=how_stall)
kit.claim("CL-B2R4-ELEV-FWD", "Elevon at the trimmed CLmax, forward CG limit, CG height", calc=ST,
          output="elev_fwd", unit="deg", how="T-B2-STALL: log the servo output at the break",
          note="B3's forward-limit criterion is 12.5 deg of up-elevon at the trimmed stall")
kit.claim("CL-B2R3-VS-GATE-FWD", "Stall at 2.6 kg, forward CG limit, CG height (as designed)", calc=ST,
          output="Vs_fwd_gate", unit="m/s", limit=("<=", "P:requirements.stall_max_ms"), verifies=["R-STALL"],
          parts=WING, how=how_stall)
kit.claim("CL-B2R4-VS-GATE-FWD-ZLO", "Stall at 2.6 kg, forward CG limit, bottom of the CG height range", calc=ST,
          output="Vs_fwd_zlo_gate", unit="m/s", limit=("<=", "P:requirements.stall_max_ms"), parts=WING,
          how=how_stall, note="corner of the CG box: a lower CG needs more up-elevon at the stall")
kit.claim("CL-B2R4-VS-GATE-FWD-Z0", "Stall at 2.6 kg, forward CG limit, CG on the chord plane (old basis)", calc=ST,
          output="Vs_fwd_z0_gate", unit="m/s", parts=WING, how=how_stall,
          note="information: the z = 0 model A1 quoted (~12.05); not a flight case since D-62")
kit.claim("CL-B2R3-VS-GATE-AFT", "Stall at 2.6 kg, aft CG limit, CG height (as designed)", calc=ST,
          output="Vs_aft_gate", unit="m/s", limit=("<=", "P:requirements.stall_max_ms"), verifies=["R-STALL"],
          parts=WING, how=how_stall)
kit.claim("CL-B2R4-X-FWD-AT-ZLO", "Forward CG x that just meets R-STALL at the bottom of the CG height range", calc=ST,
          output="x_fwd_stall_at_zlo", unit="m", how="T-B2-STALL; A1 sets the forward mark at max(this, B3 limit) "
                                                     "or raises cg.z_range_m[0] to CL-B2R4-Z-MIN-AT-XFWD")
kit.claim("CL-B2R4-Z-MIN-AT-XFWD", "Lowest CG height that meets R-STALL at the forward CG limit", calc=ST,
          output="z_min_stall_at_xfwd", unit="m", how="CG height from the balance rig (T-A3-CG-BALANCE)")
kit.claim("CL-B2R4-VS-GATE-TARGET", "Stall at 2.6 kg, CG target, CG height", calc=ST, output="Vs_target_gate",
          unit="m/s", limit=("<=", "P:requirements.stall_max_ms"), parts=WING, how=how_stall)
kit.claim("CL-B2R3-VS-PRED", "Stall at the A3 predicted mass and CG", calc=ST,
          output="Vs_pred_predm", unit="m/s", limit=("<=", "P:requirements.stall_max_ms"), parts=WING,
          how="T-B2-STALL at the as-built mass; the expected flight value")
kit.claim("CL-B2R4-B1-REPRO", "B2 AVL model run in B1's set-up / B1 trimmed CLmax - 1", calc=RC,
          output="repro", unit="-",
          how="Re-run stall_zcg.py; |value| <= 0.02 means the two codes agree and the gap is set-up, not solver")
kit.claim("CL-B2R4-RECON-ENVELOPE", "CLmax change from B2's conservative clmax envelope (vs raw stall-Re XFOIL)",
          calc=RC, output="d_envelope", unit="-", how="T-B2-STALL; XFOIL up-elevon clmax scatters +/- 0.07")
kit.claim("CL-B2R4-RECON-CMT", "CLmax change from trimming the viscous section cm (cm_t)", calc=RC,
          output="d_cmt", unit="-", how="T-B2-STALL: elevon at the break against CL-B2R4-ELEV-FWD")
kit.claim("CL-B2R4-RECON-PROPS", "CLmax change from the props / pod NP shift", calc=RC,
          output="d_props", unit="-", how="T-B3-TWIN-NP")
kit.claim("CL-B2R4-CLMAX-B1POINT", "Trimmed CLmax at B1's CG point (0.0536, z 0.018), B2 method", calc=RC,
          output="W4", unit="-", how="T-B2-STALL", note="replaces B1's 0.862 at the same point (CR-B1-23)")
kit.claim("CL-B2R4-NP-VS-B1", "Props-off effective NP with the CG height at CL 0.414, B2 minus B1", calc=RC,
          output="np_vs_b1", unit="m", how="Re-run stall_zcg.py; |value| < 0.5 mm closes the NP part of CR-B1-23",
          note="B1's 0.0708 had Zref 0.018; B2's 0.0738 is Zref 0 at alpha 0: same model, different reference height")
kit.claim("CL-B2R4-NP-Z-SHIFT", "Props-off NP shift from the CG height 0.0185 m at CL 0.414", calc=RC,
          output="np_z_shift", unit="m", how="T-B3-TWIN-NP")
kit.claim("CL-B2R4-DPROP-DRIFT", "Props/pod NP term used in the AVL runs vs B3's current claims", calc=RC,
          output="dprop_drift", unit="m", limit=("<=", 0.0002),
          how="If it fails, re-run stall_zcg.py (B3 changed CL-B3-V-XNP or -XNP-AERO)")
kit.claim("CL-B2R3-VTR-GATE-FWD", "1.3 Vs at 2.6 kg, forward CG, CG height, vs transition speed", calc=ST,
          output="Vtr_fwd_gate", unit="m/s", limit=("<=", "P:performance.transition_min_ms"),
          verifies=["R-TRANSITION"], parts=WING,
          how="F4 AIRSPEED_MIN 15.6 must be >= this; transition logs show airspeed >= 1.3 Vs")
kit.claim("CL-B2R3-VS-GATE-FWD-TURB", "Stall at 2.6 kg, forward CG, turbulent-LE section (XFOIL tripped)",
          calc="CALC-B2R3-STALL-TURB", output="Vs_trip", unit="m/s", parts=WING,
          how="Planning baseline (board decision B6, CDR-15): the wing has a tape seam at x/c about 0.05, so the "
              "tripped section is the likelier case. T-B2-STALL decides",
          note="B6: planning baseline until T-B2-STALL (AIRSPEED_MIN / CRUISE 17). The free-transition value "
               "CL-B2R3-VS-GATE-FWD stays the R-STALL design value. Exceeds 12.3 m/s")
kit.claim("CL-B2R3-BASE-VS-KEEP", "Largest gate-mass stall the B6 baseline AIRSPEED_MIN 17 holds (1.3 Vs)",
          calc="CALC-B2R3-FALLBACK", output="vs_keep_17", unit="m/s", limit=(">=", "CL-B2R3-VS-GATE-FWD-TURB"),
          verifies=["R-STALL", "R-TRANSITION"], parts=WING,
          how="T-B2-STALL with the real LE tape seam: measured trimmed stall <= 13.07 m/s keeps 17")
kit.claim("CL-B2R3-FB2-VS-KEEP", "Largest gate-mass stall the second fallback AIRSPEED_MIN 18 holds (1.3 Vs)",
          calc="CALC-B2R3-FALLBACK", output="vs_keep_18", unit="m/s", parts=WING,
          how="T-B2-STALL: a measured stall of 13.07-13.85 m/s selects 18 / 18 / 20")
kit.claim("CL-B2R3-FB2-CLMAX-RATIO", "Section-clmax ratio to free transition that the second fallback still covers",
          calc="CALC-B2R3-FALLBACK", output="clmax_ratio_18", unit="-", limit=("<=", "CL-B2R3-CLMAX-TRIP-RATIO"),
          parts=WING, how="Covers the XFOIL tripped ratio 0.871; the unconverged SU2 ratio 0.714 is not covered")
kit.claim("CL-B2R3-FB2-MAX-VA", "Second fallback AIRSPEED_MAX against the full-travel speed VA", calc="CALC-B2R3-FALLBACK",
          output="max_fb2", unit="m/s", limit=("<=", "ASM-B2R3-VA"), parts=WING,
          how="A1 / C1 accept AIRSPEED_MAX 20 (0.5 m/s under VA 20.5) before the fallback is used; T-F4-DIVE re-flown")
kit.claim("CL-B2R3-FB2-SU2-MIN", "AIRSPEED_MIN the SU2-ratio stall (14.2 m/s, bound only) would need",
          calc="CALC-B2R3-FALLBACK", output="min_needed_su2", unit="m/s", parts=WING,
          how="Information: 19 m/s leaves 1 m/s to AIRSPEED_MAX 20 and 1.5 to VA; beyond the second fallback the "
              "wing or the gate mass changes, not the parameter")
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
