"""B4 simulation / verification round on the settled CAD geometry and A3's roll-up (claims CL-B4-SIM-*).

Run (standard library; reads the stored SU2 and XFOIL outputs):
    python -I redesign/team/B4/sim/sim_claims.py      -> claims.sim.json + out/sim_results.json beside this file
The heavy runs that feed it (not needed to re-check the claims):
    python -I redesign/team/B4/sim/bemt/xfoil_polars.py          XFOIL polars -> bemt/polars.json
    python redesign/team/B4/sim/cfd/tubefin.py mesh|run|summary  gmsh + SU2 -> cfd/results.json

Four calculations:
  CALC-B4-SIM-OPS       as-designed hover operating points (A3 predicted mass, heavy pack, hover split 1.216):
                        thrust, rpm and shaft power of the hardest-working (upper) prop; headroom at the rpm cap
  CALC-B4-SIM-BEMT      BEMT (UIUC geometry, XFOIL polars) validated against UIUC measurements; radial and azimuth
                        convergence; static FM cross-check of the APC PER3 numbers B4 uses
  CALC-B4-SIM-INC       prop at incidence in the pitch-over (BEMT, 15.6 m/s): thrust/power change and the
                        in-plane H-force each prop puts on the airframe (B3's prop normal force)
  CALC-B4-SIM-TUBEFIN   2-D SU2 RANS of the tube + board section (3 grids, GCI) replacing the bare-cylinder Cd 1.1
                        in the hover download and the cruise drag of the tube span with the board behind it
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "proofs"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE / "bemt"))
import proofkit as pk  # noqa: E402
import props as pp  # noqa: E402
import bemt  # noqa: E402

kit = pk.Kit(__file__, params=["../../../params/params.json", "../../../subsystems/fins/params.json"],
             out="claims.sim.json")
P = "P:"
IN = 0.0254
CFD = json.loads((HERE / "cfd" / "results.json").read_text(encoding="utf-8"))
SEL = "11x5.5MR"
PRP = [f"PRP-003-{s}" for s in ("UR", "UL", "LR", "LL")]
FINS = [f"FIN-001-{s}" for s in ("UR", "UL", "LR", "LL")]

A = kit.assumption
A("ASM-B4-SIM-PER3-FM", "PER3 hover shaft power x 1.047", "APC PER3 over-predicts static figure of merit by 4.5 % on "
  "both APC 11 in props with UIUC data (CL-B4-XCHECK); hover shaft power is carried at PER3 x 1/0.955",
  basis="team/B4/props.py CALC-B4-XCHECK fm_ratio_static 0.955 (11x4.7SF and 11x5.5E)", value=1.047, unit="-",
  status="PROPOSED")
A("ASM-B4-SIM-SECTION", "Blade section NACA 4412 (BEMT)", "APC thin-electric blade modelled with NACA 4412 polars "
  "(XFOIL, Ncrit 5); NACA 3410 as the low-camber bound", basis="UIUC publishes chord and twist only; NACA 4412 / "
  "Clark-Y are the usual APC surrogates. Checked here against UIUC 11x5.5E data (static within 3 %)",
  value="NACA 4412", unit="-", status="UNVERIFIED")
A("ASM-B4-SIM-FILLET", "Epoxy fillet radius 3 mm at the tube-board junction", "the 0.5 mm board-to-tube gap is "
  "filled by an epoxy fillet (fin_detail.fin.le_gap_m); CFD section uses a 3 mm concave fillet",
  basis="G2 practice for a thickened-epoxy fillet on foam board; the result is insensitive to 1-5 mm (nose "
        "separation is set by the tube shoulder)", value=0.003, unit="m", status="UNVERIFIED")
A("ASM-B4-SIM-SA", "Fully turbulent SA RANS for the tube-board section", "steady incompressible RANS, "
  "Spalart-Allmaras, fully turbulent; the prop slipstream is highly turbulent (blade wakes every 5.5 ms), so the "
  "board boundary layer is taken as turbulent from the tube", basis="Leishman, ch. 10 (slipstream turbulence); "
  "a laminar steady solve diverged (vortex shedding at Re_D 1.5e4), which is itself evidence the flow is not "
  "laminar-steady", value="SA", unit="-", status="PROPOSED")
kit.source("SRC-B4-UIUC-GEOM", "UIUC Propeller Database vol. 1, measured blade geometry APC 11x5.5E and 11x4.7SF",
           "dataset", url="https://m-selig.ae.illinois.edu/props/volume-1/data/apce_11x5.5_geom.txt",
           checked="2026-11-10", where="apce_11x5.5_geom.txt, apcsf_11x4.7_geom.txt -> team/B4/data/uiuc_*_geom.csv")
kit.source("SRC-B4-CYL-RE40", "Steady cylinder drag at Re 40 (Dennis and Chang 1970; Fornberg 1980)", "paper",
           url="https://doi.org/10.1017/S0022112070001428", checked="2026-11-10",
           where="Dennis & Chang JFM 42: Cd 1.522 (pressure 0.99, friction 0.53) at Re 40; Fornberg JFM 98: 1.498",
           note="used to validate the SU2 set-up, mesh family and force integration")


# ------------------------------------------------------------------------------------------- 1. operating points
@kit.calc("CALC-B4-SIM-OPS", title="As-designed hover operating points (A3 roll-up, hover split, rpm cap)",
          assumes=["ASM-B4-SIM-PER3-FM"],
          equation="W = m g k_dl ; per pair: upper/lower = s ; T_u = W s / (2 (1 + s) cos(cant)) ; T_l = T_u / s ; "
                   "rpm, shaft power from APC PER3 (11x5.5MR) x 1.047 ; T_cap = PER3 thrust at rpm_max ; "
                   "headroom = T_cap / T_u ; T/W_cap = 4 T_cap cos(cant) / (m g) ; m_heavy = gate - margin_680",
          inputs={"m_pred": "CL-A3-MASS-PREDICTED", "m_gate": P + "requirements.mtow_gate_kg",
                  "mg680": "CL-A3-GATE-MARGIN-680", "s": "CL-A3-HOVER-SPLIT", "kdl": P + "propulsion.download_factor",
                  "cant": P + "propulsion.stations.cant_deg", "rpm_cap": P + "propulsion.rpm_max",
                  "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "fmk": "ASM-B4-SIM-PER3-FM"},
          units={"m_pred": "kg", "m_gate": "kg", "mg680": "kg", "cant": "deg", "rpm_cap": "rpm", "rho": "kg/m3"})
def ops(m_pred, m_gate, mg680, s, kdl, cant, rpm_cap, g, rho, fmk):
    cc = math.cos(math.radians(cant))
    T_cap = pp.thrust_power(SEL, rpm_cap, 0.0, rho)[0]
    out = {"t_cap_n": T_cap}
    for tag, m in (("pred", m_pred), ("heavy", m_gate - mg680), ("gate", m_gate)):
        W = m * g * kdl
        Tu = W * s / (2 * (1 + s)) / cc
        Tl = Tu / s
        Te = W / 4 / cc
        for nm, T in (("upper", Tu), ("lower", Tl), ("even", Te)):
            rpm = pp.rpm_for_thrust(SEL, T, 0.0, rho)
            Pw = pp.thrust_power(SEL, rpm, 0.0, rho)[1] * fmk
            out[f"{nm}_t_n__{tag}"] = T
            out[f"{nm}_rpm__{tag}"] = rpm
            out[f"{nm}_shaft_w__{tag}"] = Pw
        out[f"hover_shaft_total_w__{tag}"] = 2 * (out[f"upper_shaft_w__{tag}"] + out[f"lower_shaft_w__{tag}"])
        out[f"headroom_upper__{tag}"] = T_cap / Tu
        out[f"tw_cap__{tag}"] = 4 * T_cap * cc / (m * g)
        out[f"upper_throttle_frac__{tag}"] = Tu / T_cap
    return out


# ------------------------------------------------------------------------------------------- 2. BEMT validation
UIUC_PTS = {  # prop: (J, Ct, Cp, rpm) from data/uiuc_measured.csv (SRC-B4-UIUC), the points used
    "11x5.5E": [(0.0, 0.0873, 0.0313, 4968), (0.0, 0.0885, 0.0317, 5577), (0.369, 0.0434, 0.0264, 6000),
                (0.462, 0.0279, 0.0204, 6000), (0.549, 0.0136, 0.0143, 6000)],
}


def _uiuc_rows():
    rows = [r for r in pp.UIUC if r["prop"] == "11x5.5E"]
    st = sorted([r for r in rows if r["kind"] == "static"], key=lambda r: r["x"])
    tu = sorted([r for r in rows if r["kind"] == "tunnel"], key=lambda r: r["J"])
    return st, tu


@kit.calc("CALC-B4-SIM-BEMT", title="BEMT validation against UIUC (11x5.5E), convergence, PER3 static cross-check",
          assumes=["ASM-B4-SIM-SECTION"], cites=["SRC-B4-UIUC", "SRC-B4-UIUC-GEOM", "SRC-B4-APC-PER3"],
          equation="annulus momentum + blade element, Prandtl tip/hub loss, swirl ; error = BEMT / UIUC - 1 at the "
                   "measured rpm and J ; convergence: N = 10/20/40/80 radial elements (static, hover rpm) ; "
                   "FM = T^1.5 / sqrt(2 rho A) / P",
          inputs={"rho": P + "env.rho_kgm3", "rpm_h": "CL-B4-HOVER-RPM"}, units={"rho": "kg/m3", "rpm_h": "rpm"})
def bemt_validation(rho, rpm_h):
    out = {}
    st, tu = _uiuc_rows()
    D = 11 * IN
    errs_ct, errs_cp = [], []
    for foil in ("naca4412", "naca3410"):
        for r in st:
            b = bemt.rotor("11x5.5E", r["x"], rho=rho, N=40, foil=foil)
            out[f"static_ct_err_{int(r['x'])}__{foil}"] = b["Ct"] / r["Ct"] - 1
            out[f"static_cp_err_{int(r['x'])}__{foil}"] = b["Cp"] / r["Cp"] - 1
            if foil == "naca4412":
                errs_ct.append(abs(b["Ct"] / r["Ct"] - 1))
                errs_cp.append(abs(b["Cp"] / r["Cp"] - 1))
        for r in tu:
            n = r["x"] / 60
            b = bemt.rotor("11x5.5E", r["x"], V=r["J"] * n * D, rho=rho, N=40, foil=foil)
            out[f"tunnel_ct_err_J{r['J']:.3f}__{foil}"] = b["Ct"] / r["Ct"] - 1 if abs(r["Ct"]) > 0.005 else None
            out[f"tunnel_eta__J{r['J']:.3f}__{foil}"] = b["eta"]
            out[f"tunnel_eta_meas__J{r['J']:.3f}"] = r["eta"]
    for foil in ("naca4412", "naca3410"):
        e = [abs(out[f"tunnel_ct_err_J{r['J']:.3f}__{foil}"]) for r in tu
             if r["J"] <= 0.47 and out[f"tunnel_ct_err_J{r['J']:.3f}__{foil}"] is not None]
        out[f"tunnel_ct_abserr_max_Jle047__{foil}"] = max(e)
        rc = min(tu, key=lambda q: abs(q["J"] - 0.578))           # nearest measured point to the cruise J
        out[f"tunnel_ct_err_near_cruise__{foil}"] = out[f"tunnel_ct_err_J{rc['J']:.3f}__{foil}"]
        out[f"tunnel_eta_err_near_cruise__{foil}"] = out[f"tunnel_eta__J{rc['J']:.3f}__{foil}"] / rc["eta"] - 1
        out["tunnel_J_near_cruise"] = rc["J"]
    out["static_ct_err_max"] = max(errs_ct)
    out["static_cp_err_max"] = max(errs_cp)
    # FM: BEMT and UIUC at the measured static rpm nearest the hover rpm, vs PER3 for the same prop
    r = min(st, key=lambda q: abs(q["x"] - rpm_h))
    b = bemt.rotor("11x5.5E", r["x"], rho=rho, N=40)
    fm_meas = (r["Ct"] ** 1.5) / (r["Cp"] * math.sqrt(math.pi / 2))
    ct_a, cp_a = pp.coeffs("11x5.5E", 0.0, r["x"])
    fm_per3 = (ct_a ** 1.5) / (cp_a * math.sqrt(math.pi / 2))
    out.update({"fm_rpm": r["x"], "fm_bemt": b["FM"], "fm_uiuc": fm_meas, "fm_per3": fm_per3,
                "fm_ratio_bemt_over_per3": b["FM"] / fm_per3, "fm_ratio_uiuc_over_per3": fm_meas / fm_per3})
    # radial convergence at the hover rpm (static), 4 levels
    lv = [bemt.rotor("11x5.5E", rpm_h, rho=rho, N=N) for N in (10, 20, 40, 80)]
    for N, b in zip((10, 20, 40, 80), lv):
        out[f"conv_T_N{N}"] = b["T"]
        out[f"conv_P_N{N}"] = b["P"]
    out["conv_T_change_40_80"] = abs(lv[3]["T"] / lv[2]["T"] - 1)
    out["conv_P_change_40_80"] = abs(lv[3]["P"] / lv[2]["P"] - 1)
    # Richardson on T with r = 2 (uniform halving)
    e1, e2 = lv[3]["T"] - lv[2]["T"], lv[2]["T"] - lv[1]["T"]
    p_obs = math.log(abs(e2 / e1)) / math.log(2) if e1 and e2 and e1 * e2 > 0 else None
    out["conv_T_order"] = p_obs
    out["conv_T_gci_fine"] = 1.25 * abs(e1 / lv[3]["T"]) / (2 ** p_obs - 1) if p_obs else 3 * abs(e1 / lv[3]["T"])
    return out


# ------------------------------------------------------------------------------------------- 3. incidence
INCS = (0.0, 15.0, 30.0, 45.0, 60.0, 75.0, 90.0)


@kit.calc("CALC-B4-SIM-INC", title="Prop at incidence in the pitch-over: thrust, power and in-plane H-force (BEMT)",
          assumes=["ASM-B4-SIM-SECTION"],
          equation="i = angle between the free stream and the shaft ; Vx = V cos i, Vt = V sin i ; quasi-steady "
                   "blade element per azimuth (M stations) with local momentum ; T, P, H averaged over psi ; "
                   "fixed rpm = the BEMT rpm for the hover thrust (static) ; H/T and dH/di at V_t",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "kdl": P + "propulsion.download_factor", "cant": P + "propulsion.stations.cant_deg",
                  "V": P + "performance.transition_min_ms"},
          units={"m": "kg", "rho": "kg/m3", "cant": "deg", "V": "m/s"})
def incidence(m, g, rho, kdl, cant, V):
    T_h = kdl * m * g / 4 / math.cos(math.radians(cant))
    # rpm for the hover thrust (static), 11x5.5E geometry (the MR geometry is not published)
    lo, hi = 3000.0, 9000.0
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if bemt.rotor("11x5.5E", mid, rho=rho, N=20)["T"] < T_h:
            lo = mid
        else:
            hi = mid
    rpm = 0.5 * (lo + hi)
    st = bemt.rotor("11x5.5E", rpm, rho=rho, N=20)
    out = {"rpm": rpm, "T_static_n": st["T"], "P_static_w": st["P"], "mu_edgewise": V / (rpm / 60 * 2 * math.pi *
                                                                                          5.5 * IN)}
    for i in INCS:
        b = bemt.rotor("11x5.5E", rpm, V=V, inc_deg=i, rho=rho, N=20, M=12)
        out[f"T_ratio__i{int(i)}"] = b["T"] / st["T"]
        out[f"P_ratio__i{int(i)}"] = b["P"] / st["P"]
        out[f"H_n__i{int(i)}"] = b["H"]
        out[f"H_over_T__i{int(i)}"] = b["H"] / b["T"] if b["T"] > 0 else None
    out["H_n_max"] = max(out[f"H_n__i{int(i)}"] for i in INCS)
    # section bound: NACA 3410 (matches UIUC in the tunnel within 4 % for J <= 0.47, CL-B4-SIM-BEMT-FWD)
    hb = [bemt.rotor("11x5.5E", rpm, V=V, inc_deg=i, rho=rho, N=20, M=12, foil="naca3410")["H"] for i in INCS]
    out["H_n_max__naca3410"] = max(hb)
    out["H_ratio_3410_over_4412"] = out["H_n_max__naca3410"] / max(out[f"H_n__i{int(i)}"] for i in INCS)
    out["H_4props_max_n"] = 4 * out["H_n_max"]
    hts = [out[f"H_over_T__i{int(i)}"] for i in INCS if i > 0]
    out["H_over_T_max"] = max(hts)
    out["H_at_T_hover_max_n"] = out["H_over_T_max"] * T_h            # if the controller holds hover thrust
    out["H_at_T_hover_4props_n"] = 4 * out["H_at_T_hover_max_n"]
    out["dH_di_n_per_rad"] = (out["H_n__i15"] - out["H_n__i0"]) / math.radians(15)
    # azimuth convergence at i = 45 deg
    for M in (6, 12, 24):
        b = bemt.rotor("11x5.5E", rpm, V=V, inc_deg=45.0, rho=rho, N=20, M=M)
        out[f"conv_H_M{M}"] = b["H"]
        out[f"conv_T_M{M}"] = b["T"]
    out["conv_H_change_12_24"] = abs(out["conv_H_M24"] / out["conv_H_M12"] - 1)
    out["conv_T_change_12_24"] = abs(out["conv_T_M24"] / out["conv_T_M12"] - 1)
    return out


# ------------------------------------------------------------------------------------------- 4. tube + board CFD
@kit.calc("CALC-B4-SIM-TUBEFIN", title="Tube + board section drag (SU2 RANS, grids L0/L1/L2) in the hover download and cruise",
          assumes=["ASM-B4-SIM-FILLET", "ASM-B4-SIM-SA", "ASM-B4-CD-TUBE"], cites=["SRC-B4-CYL-RE40"],
          equation="Cd_hand = Cd_tube + 2 Cf (L_b / D) + 0.5 t / D, Cf = 0.074 Re_L^-0.2 (props.py terms) ; "
                   "Cd_CFD = Richardson value on L2/L1/L0 (GCI band) ; backed fraction f = (z_board_top - z_skin) / "
                   "(z_tube_end - z_skin) ; dD = D_tube f (Cd_CFD - Cd_hand) / Cd_tube ; k_new = k + dD / (m g / 4) ; "
                   "cruise: D_tube+board = Cd_CFD 0.5 rho V^2 D h_backed x 4",
          inputs={"k": "CL-B4-DOWNLOAD", "D_tube": "CL-B4-TUBE-LOAD", "m": P + "requirements.mtow_gate_kg",
                  "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "cd": "ASM-B4-CD-TUBE",
                  "d": P + "fins.tube.od_m", "tube_len": P + "fins.tube.length_m", "grip": P + "fin_detail.mount.grip_m",
                  "sc_gap": P + "fin_detail.station_collar.gap_m", "x_tube": P + "fins.tube.x_m",
                  "c": P + "wing.chord_m", "te": P + "fins.te_x_m", "bt": P + "fins.board_t_m",
                  "layers": P + "fins.layers", "V": P + "performance.cruise_ms", "kdl": P + "propulsion.download_factor",
                  "b1": "ASM-B1-DRAG"},
          units={"m": "kg", "rho": "kg/m3", "d": "m", "tube_len": "m", "grip": "m", "sc_gap": "m", "x_tube": "m",
                 "c": "m", "te": "m", "bt": "m", "V": "m/s"})
def tubefin(k, D_tube, m, g, rho, cd, d, tube_len, grip, sc_gap, x_tube, c, te, bt, layers, V, kdl, b1):
    out = {}
    cf_b1, ff_b1, cd_tube_b1, _, _, if_b1 = b1                 # B1's cruise build-up for the same section
    t = bt * layers
    Lb = te - x_tube - d / 2
    nu = 1.81e-5 / rho
    for tag in ("hov", "cru"):
        st = CFD["studies"][f"{tag}_sa"]
        cases = [CFD["cases"][f"{tag}_sa_L{lv}"] for lv in st["levels"]]
        U = cases[0]["U_ms"]
        cf = 0.074 / (U * Lb / nu) ** 0.2
        cd_hand = cd + 2 * cf * Lb / d + 0.5 * t / d
        cd_cfd = st["f_ext"] if st["f_ext"] is not None else st["cd_fine_mid_coarse"][0]
        out[f"cd_hand__{tag}"] = cd_hand
        out[f"cd_cfd__{tag}"] = cd_cfd
        out[f"cd_fine__{tag}"] = st["cd_fine_mid_coarse"][0]
        out[f"cd_mid__{tag}"] = st["cd_fine_mid_coarse"][1]
        out[f"cd_coarse__{tag}"] = st["cd_fine_mid_coarse"][2]
        out[f"gci_fine__{tag}"] = st["gci_fine"]
        out[f"order__{tag}"] = st["p"]
        out[f"cd_p__{tag}"] = cases[0].get("bd_cd_p")
        out[f"cd_f__{tag}"] = cases[0].get("bd_cd_f")
        out[f"cells_fine__{tag}"] = cases[0]["cells"]
        out[f"ratio_cfd_hand__{tag}"] = cd_cfd / cd_hand
        out[f"cd_upper__{tag}"] = cd_cfd * (1 + st["gci_fine"])
        out[f"cd_nose_eff__{tag}"] = cd_cfd - (cd_hand - cd)        # what the round nose adds beyond the board terms
    zs = pp._z_surf(c)(x_tube)
    z_end = tube_len / 2
    z_top = z_end - grip - sc_gap
    f = (z_top - zs) / (z_end - zs)
    T = m * g / 4
    for tag, cdv in (("", out["cd_cfd__hov"]), ("_upper", out["cd_upper__hov"])):
        dD = D_tube * f * (cdv - out["cd_hand__hov"]) / cd
        out["dD_station_n" + tag] = dD
        out["k_new" + tag] = k + dD / T
    out["backed_frac"] = f
    out["k_old"] = k
    out["k_margin_to_param"] = kdl / out["k_new_upper"] - 1
    h = z_top - zs
    q = 0.5 * rho * V * V
    out["cruise_backed_h_m"] = h
    out["cruise_tubeboard_n_4st"] = 4 * out["cd_cfd__cru"] * q * d * h
    out["cruise_tubeboard_hand_n_4st"] = 4 * out["cd_hand__cru"] * q * d * h
    out["cruise_delta_n_4st"] = out["cruise_tubeboard_n_4st"] - out["cruise_tubeboard_hand_n_4st"]
    # B1's build-up on the same section (what the cruise drag polar actually carries): IF (Cd_tube + 2 Cf FF L_b / D)
    out["cd_b1hand__cru"] = if_b1 * (cd_tube_b1 + 2 * cf_b1 * ff_b1 * Lb / d)
    out["ratio_cfd_b1__cru"] = out["cd_cfd__cru"] / out["cd_b1hand__cru"]
    out["cruise_tubeboard_b1_n_4st"] = 4 * out["cd_b1hand__cru"] * q * d * h
    out["cruise_delta_b1_n_4st"] = out["cruise_tubeboard_n_4st"] - out["cruise_tubeboard_b1_n_4st"]
    out["cruise_cd_on_chord"] = out["cd_cfd__cru"] * d / (te - x_tube + d / 2)
    # validation case
    v = CFD["studies"]["val_lam"]
    out["val_cd_fine"] = v["cd_fine_mid_coarse"][0]
    out["val_cd_ext"] = v["f_ext"] if v["f_ext"] is not None else v["cd_fine_mid_coarse"][0]
    out["val_err_vs_dennis_chang"] = out["val_cd_ext"] / 1.522 - 1
    out["val_gci"] = v["gci_fine"]
    return out


# ------------------------------------------------------------------------------------------- claims
c = kit.claim
c("CL-B4-SIM-T-UPPER", "Hover thrust on each upper prop, A3 predicted mass, split 1.216 (incl. download, cant)",
  calc="CALC-B4-SIM-OPS", output="upper_t_n__pred", unit="N", parts=PRP,
  how="Tethered hover log: ESC rpm of the upper pair vs CL-B4-SIM-RPM-UPPER; thrust from T-B4-STAND rpm map.")
c("CL-B4-SIM-RPM-UPPER", "Hover rpm, upper prop, A3 predicted mass", calc="CALC-B4-SIM-OPS",
  output="upper_rpm__pred", unit="rpm", parts=PRP, how="Bluejay rpm telemetry in a tethered hover.")
c("CL-B4-SIM-RPM-LOWER", "Hover rpm, lower prop, A3 predicted mass", calc="CALC-B4-SIM-OPS",
  output="lower_rpm__pred", unit="rpm", parts=PRP, how="As CL-B4-SIM-RPM-UPPER.")
c("CL-B4-SIM-SHAFT-HOVER", "Hover shaft power, 4 props, A3 predicted mass (PER3 x 1.047)", calc="CALC-B4-SIM-OPS",
  output="hover_shaft_total_w__pred", unit="W", parts=PRP, how="T-B4-STAND torque x rpm at the two thrusts.")
c("CL-B4-SIM-HEADROOM", "Thrust headroom of the upper prop at the rpm cap, heavy pack (680 g)", calc="CALC-B4-SIM-OPS",
  output="headroom_upper__heavy", unit="-", limit=(">=", P + "requirements.hover_ctrl_factor"), parts=PRP,
  how="T-B4-STAND thrust at 9 350 rpm divided by the upper-prop hover thrust at the weighed mass.")
c("CL-B4-SIM-HEADROOM-PRED", "Thrust headroom of the upper prop at the rpm cap, A3 predicted mass",
  calc="CALC-B4-SIM-OPS", output="headroom_upper__pred", unit="-",
  limit=(">=", P + "requirements.hover_ctrl_factor"), parts=PRP, how="As CL-B4-SIM-HEADROOM.")
c("CL-B4-SIM-TW-CAP", "T/W at the rpm cap, A3 predicted mass", calc="CALC-B4-SIM-OPS", output="tw_cap__pred",
  unit="-", limit=(">=", P + "requirements.hover_tw_min"), verifies=["R-HOVER-TW"], parts=PRP,
  how="T-B4-STAND thrust at 9 350 rpm x 4 cos 7 deg / weighed mass.")
c("CL-B4-SIM-BEMT-STATIC", "BEMT static Ct error vs UIUC 11x5.5E (worst of 5 rpm)", calc="CALC-B4-SIM-BEMT",
  output="static_ct_err_max", unit="-", limit=("<=", 0.05),
  how="Re-run sim_claims.py; compare with data/uiuc_measured.csv.")
c("CL-B4-SIM-FM-RATIO", "Static FM, UIUC measured / APC PER3 (11x5.5E, nearest hover rpm)", calc="CALC-B4-SIM-BEMT",
  output="fm_ratio_uiuc_over_per3", unit="-", how="Basis of ASM-B4-SIM-PER3-FM; T-B4-STAND gives the MR value.")
c("CL-B4-SIM-FM-BEMT", "Static FM, BEMT / APC PER3 (11x5.5E)", calc="CALC-B4-SIM-BEMT",
  output="fm_ratio_bemt_over_per3", unit="-", how="Diagnostic only: BEMT (NACA 4412) over-predicts static FM by "
  "~9 % against UIUC (Ct +3 %, Cp -2 to -6 %), so ASM-B4-SIM-PER3-FM rests on the UIUC data, not on BEMT.")
c("CL-B4-SIM-BEMT-FWD", "BEMT Ct error vs UIUC 11x5.5E in the tunnel, worst for J <= 0.47 (NACA 3410 section)",
  calc="CALC-B4-SIM-BEMT", output="tunnel_ct_abserr_max_Jle047__naca3410", unit="-", limit=("<=", 0.05),
  how="Re-run sim_claims.py. Near the cruise J (0.57) the sections miss by +34 % (4412) and -43 % (3410) in Ct, so "
      "cruise numbers stay on PER3 x the UIUC cross-check (CALC-B4-XCHECK), not on BEMT.")
c("CL-B4-SIM-BEMT-CONV", "BEMT thrust change 40 -> 80 radial elements", calc="CALC-B4-SIM-BEMT",
  output="conv_T_change_40_80", unit="-", limit=("<=", 0.005), how="Re-run with N = 160.")
c("CL-B4-SIM-H-MAX", "In-plane H-force per prop in the pitch-over, worst incidence, 15.6 m/s",
  calc="CALC-B4-SIM-INC", output="H_n_max", unit="N", parts=PRP,
  how="Car-top rig with the prop at 45-90 deg to the wind at 15.6 m/s, side-force cell; or B3's transition log fit.")
c("CL-B4-SIM-HT-MAX", "Prop in-plane force / thrust, worst incidence 15-90 deg, 15.6 m/s", calc="CALC-B4-SIM-INC",
  output="H_over_T_max", unit="-", parts=PRP, how="As CL-B4-SIM-H-MAX.")
c("CL-B4-SIM-H-HOVERT", "In-plane force per prop if hover thrust is held through the pitch-over (worst incidence)",
  calc="CALC-B4-SIM-INC", output="H_at_T_hover_max_n", unit="N", parts=PRP, how="As CL-B4-SIM-H-MAX.")
c("CL-B4-SIM-DH-DI", "Prop normal-force slope dH/di per prop at 15.6 m/s, hover rpm", calc="CALC-B4-SIM-INC",
  output="dH_di_n_per_rad", unit="N/rad", parts=PRP, how="As CL-B4-SIM-H-MAX at 0 and 15 deg.")
c("CL-B4-SIM-T-I45", "Thrust at 45 deg incidence / static, fixed hover rpm, 15.6 m/s", calc="CALC-B4-SIM-INC",
  output="T_ratio__i45", unit="-", how="As CL-B4-SIM-H-MAX.")
c("CL-B4-SIM-T-I90", "Thrust edgewise (90 deg) / static, fixed hover rpm, 15.6 m/s", calc="CALC-B4-SIM-INC",
  output="T_ratio__i90", unit="-", how="As CL-B4-SIM-H-MAX.")
c("CL-B4-SIM-INC-CONV", "BEMT H-force change 12 -> 24 azimuth stations (i 45 deg)", calc="CALC-B4-SIM-INC",
  output="conv_H_change_12_24", unit="-", limit=("<=", 0.01), how="Re-run with M = 48.")
c("CL-B4-SIM-CFD-VAL", "SU2 cylinder at Re 40 vs Dennis and Chang 1.522 (relative error)", calc="CALC-B4-SIM-TUBEFIN",
  output="val_err_vs_dennis_chang", unit="-", limit=("<=", 0.03),
  how="Re-run tubefin.py val_lam_L1..L3; published 1.498-1.522.")
c("CL-B4-SIM-CD-TUBEFIN", "Tube + board section Cd on D, hover slipstream (SU2 SA, Richardson)",
  calc="CALC-B4-SIM-TUBEFIN", output="cd_cfd__hov", unit="-", parts=FINS,
  how="T-B4-INSTALLED: thrust loss with the board on vs the bare tube at equal rpm.")
c("CL-B4-SIM-CD-GCI", "Grid-convergence index of the hover section Cd (fine grid)", calc="CALC-B4-SIM-TUBEFIN",
  output="gci_fine__hov", unit="-", limit=("<=", 0.05), how="Re-run tubefin.py on a fourth grid.")
c("CL-B4-SIM-CD-RATIO", "Tube + board Cd, CFD / B4 hand build-up (hover)", calc="CALC-B4-SIM-TUBEFIN",
  output="ratio_cfd_hand__hov", unit="-", how="As CL-B4-SIM-CD-TUBEFIN.")
c("CL-B4-SIM-DOWNLOAD", "Hover download factor with the CFD tube + board section (upper GCI bound)",
  calc="CALC-B4-SIM-TUBEFIN", output="k_new_upper", unit="-", limit=("<=", P + "propulsion.download_factor"),
  parts=PRP + FINS, how="T-B4-INSTALLED: installed / isolated thrust at equal rpm.")
c("CL-B4-SIM-CRUISE-TUBEFIN", "Cruise drag of the board-backed tube spans, 4 stations, 16 m/s (CFD)",
  calc="CALC-B4-SIM-TUBEFIN", output="cruise_tubeboard_n_4st", unit="N", parts=FINS,
  how="Flight: B1's drag polar fit from logged cruise power.")
c("CL-B4-SIM-CRUISE-DELTA", "Cruise drag change vs B4's bare-cylinder build-up on those spans (negative = less)",
  calc="CALC-B4-SIM-TUBEFIN", output="cruise_delta_n_4st", unit="N", how="As CL-B4-SIM-CRUISE-TUBEFIN.")
c("CL-B4-SIM-CD-B1-RATIO", "Tube + board section Cd at 16 m/s, CFD / B1's build-up (ASM-B1-DRAG)",
  calc="CALC-B4-SIM-TUBEFIN", output="ratio_cfd_b1__cru", unit="-", parts=FINS,
  how="Cross-check of B1's cruise polar on this section; flight drag-polar fit (B1).")
c("CL-B4-SIM-CRUISE-DELTA-B1", "Cruise drag change vs B1's build-up on the board-backed tube spans, 4 stations",
  calc="CALC-B4-SIM-TUBEFIN", output="cruise_delta_b1_n_4st", unit="N", how="As CL-B4-SIM-CD-B1-RATIO.")


def _write_results():
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    res = {nid: n.get("outputs") for nid, n in kit.nodes.items() if n["type"] == "calculation"}
    (out / "sim_results.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    kit.write()
    _write_results()
