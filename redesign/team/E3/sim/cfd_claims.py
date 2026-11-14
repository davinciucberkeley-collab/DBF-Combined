"""E3 simulation round: claims from the ESC CFD study (sim/cfd/esc_cfd.py -> sim/cfd/results.json).

Run:  python -I redesign/team/E3/sim/cfd_claims.py      -> claims.json beside this file (read by thermal.py)
The SU2 runs themselves are not re-run by the proof build (minutes each); their film coefficients enter as value
claims citing results.json, and the conversion to the lumped model's local-velocity factor is a calculation that
the build re-checks. Python 3 standard library only.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../../params/params.json"])
RES = json.loads((HERE / "cfd" / "results.json").read_text(encoding="utf-8"))
ST, CS = RES["studies"], RES["cases"]

kit.source("SRC-E3-CFD-RESULTS", "E3 ESC-section CFD: SU2 8.5 INC_RANS SST/LM, 3 meshes, results.json", kind="web",
           url="redesign/team/E3/sim/cfd/results.json",
           where="studies.hov_sst / cru_sst (GCI), cases.hov_lm_tu1_L2 / cru_lm_tu1_L2 (transition, quiet inflow), "
                 "cases.hov_sst_tu1_L2, hov_sa_L2, hov_lm_L2 (sensitivity); script sim/cfd/esc_cfd.py")
kit.source("SRC-E3-CELIK-GCI", "Celik et al. (2008), Procedure for estimation and reporting of uncertainty due to "
           "discretization in CFD applications, J. Fluids Eng. 130(7) 078001", kind="paper",
           url="https://doi.org/10.1115/1.2960953", where="three-grid Richardson extrapolation, GCI with Fs 1.25")


def hv(case):
    return CS[case]["h_wm2k"]


# value claims (SU2 output, per unit span, ESC faces at T_amb + 30 K)
H = {
    "CL-E3-CFD-H-HOV": ("ESC film coefficient, hover slipstream, SST Tu 5 %, fine grid (L3)",
                        ST["hov_sst"]["h_L3_L2_L1"][0]),
    "CL-E3-CFD-H-HOV-EXT": ("ESC film coefficient, hover, SST, Richardson-extrapolated (or L3 if not asymptotic)",
                            ST["hov_sst"]["h_best"]),
    "CL-E3-CFD-H-HOV-LOW": ("ESC film coefficient, hover, SST, lower GCI band", ST["hov_sst"]["h_low_band"]),
    "CL-E3-CFD-H-CRU-EXT": ("ESC film coefficient, cruise 16 m/s, SST, extrapolated", ST["cru_sst"]["h_best"]),
    "CL-E3-CFD-H-CRU-LOW": ("ESC film coefficient, cruise, SST, lower GCI band", ST["cru_sst"]["h_low_band"]),
    "CL-E3-CFD-H-HOV-LMTU1": ("ESC film coefficient, hover, LM transition, quiet inflow Tu 1 % (L2)",
                              hv("hov_lm_tu1_L2")),
    "CL-E3-CFD-H-CRU-LMTU1": ("ESC film coefficient, cruise, LM transition, Tu 1 % (L2)", hv("cru_lm_tu1_L2")),
    "CL-E3-CFD-H-HOV-SA": ("ESC film coefficient, hover, Spalart-Allmaras, Tu 5 % (L2): turbulence-model bracket",
                           hv("hov_sa_L2")),
    "CL-E3-CFD-H-HOV-L2": ("ESC film coefficient, hover, SST (L2), same grid as the model brackets", hv("hov_sst_L2")),
    "CL-E3-CFD-H-CRU-L2": ("ESC film coefficient, cruise, SST (L2)", hv("cru_sst_L2")),
}
for cid, (title, v) in H.items():
    kit.claim(cid, title, value=v, unit="W/m2 K", cites=["SRC-E3-CFD-RESULTS"], parts=["PRP-002-UR", "FIN-007-UR"],
              how="T-E3-ESC-PAD: ESC on the half-fin mock-up behind the 22 mm tube at hover power; h = (loss - "
                  "radiation) / (A (T_esc - T_amb)); within the band of CL-E3-CFD-FEQ.")
kit.claim("CL-E3-CFD-U", "CFD inflow speeds [hover slipstream at the pad, cruise]", value=[RES["U_hov_ms"],
          RES["U_cru_ms"]], unit="m/s", cites=["SRC-E3-CFD-RESULTS"],
          how="Hover value from thermal.py's design hover (B4 momentum model at the pad); cruise = params.")
kit.claim("CL-E3-CFD-GCI-HOV", "Grid convergence index on the hover film coefficient (fine grid)", value=ST["hov_sst"]
          ["gci_fine"], unit="-", limit=("<=", 0.15), cites=["SRC-E3-CFD-RESULTS", "SRC-E3-CELIK-GCI"],
          how="Re-run esc_cfd.py mesh/run/summary; three levels L1-L3. An L4 (~150 k cells) would tighten it.",
          note="h rises monotonically with refinement, so the fine-grid and lower-band values used for design are on "
               "the cool side of the converged answer; limit 15 % = E3 acceptance for a design input carried with the "
               "lower band")
kit.claim("CL-E3-CFD-YPLUS-L2", "Largest first-cell y+ on the ESC (L2; L3 is 1.5 x finer)", value=max(
          CS["hov_sst_L2"].get("yplus_max") or 0.0, CS["cru_sst_L2"].get("yplus_max") or 0.0), unit="-",
          limit=("<=", 2.0), cites=["SRC-E3-CFD-RESULTS"], how="surface_flow.vtk Y_Plus on the esc marker.")
kit.claim("CL-E3-CFD-GCI-CRU", "Grid convergence index on the cruise film coefficient (fine grid)", value=ST["cru_sst"]
          ["gci_fine"], unit="-", limit=("<=", 0.15), cites=["SRC-E3-CFD-RESULTS", "SRC-E3-CELIK-GCI"],
          how="As CL-E3-CFD-GCI-HOV.")


@kit.calc("CALC-E3-CFD-FEQ", title="Local-velocity factor the lumped ESC model needs to reproduce the CFD film",
          equation="h_lam(fU) = 0.664 (f U L/nu)^0.5 Pr^1/3 k/L  =>  f = (h / h_lam(U))^2 ; model factor k_m = "
                   "h_SA / h_SST (hover, L2) ; design = min(SST lower GCI band, LM Tu 1 %, k_m x SST L2) per regime "
                   "(the lowest of the three turbulence models on the same grid) ; nominal = SST extrapolated",
          inputs={"u": "CL-E3-CFD-U", "air": "ASM-E3-AIR", "esc": "ASM-E3-ESC",
                  "h_hov": "CL-E3-CFD-H-HOV-EXT", "h_hov_low": "CL-E3-CFD-H-HOV-LOW",
                  "h_hov_lm": "CL-E3-CFD-H-HOV-LMTU1", "h_cru": "CL-E3-CFD-H-CRU-EXT",
                  "h_cru_low": "CL-E3-CFD-H-CRU-LOW", "h_cru_lm": "CL-E3-CFD-H-CRU-LMTU1",
                  "h_hov_sa": "CL-E3-CFD-H-HOV-SA", "h_hov_l2": "CL-E3-CFD-H-HOV-L2", "h_cru_l2": "CL-E3-CFD-H-CRU-L2",
                  "wake_r2": "ASM-E3-WAKE"},
          units={"u": "m/s", "h_hov": "W/m2 K", "h_hov_low": "W/m2 K", "h_hov_lm": "W/m2 K", "h_cru": "W/m2 K",
                 "h_cru_low": "W/m2 K", "h_cru_lm": "W/m2 K", "h_hov_sa": "W/m2 K", "h_hov_l2": "W/m2 K",
                 "h_cru_l2": "W/m2 K"},
          assumes=["ASM-E3-AIR", "ASM-E3-ESC"], cites=["SRC-E3-CFD-RESULTS"])
def feq(u, air, esc, h_hov, h_hov_low, h_hov_lm, h_cru, h_cru_low, h_cru_lm, h_hov_sa, h_hov_l2, h_cru_l2, wake_r2):
    nu, k, pr = air
    L = esc[0]

    def hl(U):
        return 0.664 * (U * L / nu) ** 0.5 * pr ** (1 / 3) * k / L

    f = {name: (h / hl(U)) ** 2 for name, h, U in (
        ("hov", h_hov, u[0]), ("hov_low", h_hov_low, u[0]), ("hov_lm", h_hov_lm, u[0]),
        ("cru", h_cru, u[1]), ("cru_low", h_cru_low, u[1]), ("cru_lm", h_cru_lm, u[1]),
        ("hov_sa", h_hov_sa, u[0]), ("cru_sa_est", h_cru_l2 * h_hov_sa / h_hov_l2, u[1]))}
    des_h = min(f["hov_low"], f["hov_lm"], f["hov_sa"])
    des_c = min(f["cru_low"], f["cru_lm"], f["cru_sa_est"])
    return {"value": [des_h, des_c, f["hov"], f["cru"]], "all": f, "model_factor_sa_sst": h_hov_sa / h_hov_l2, "h_lam_hov": hl(u[0]), "h_lam_cru": hl(u[1]),
            "h_r2_design_hov": hl(u[0] * wake_r2[1]), "h_r2_nominal_hov": hl(u[0] * wake_r2[0]),
            "ratio_design_vs_r2": des_h / wake_r2[1]}


kit.claim("CL-E3-CFD-FEQ", "ESC local-velocity factor from CFD [hover design, cruise design, hover nominal, cruise "
          "nominal]", calc="CALC-E3-CFD-FEQ", output="value", unit="-", parts=["PRP-002-UR", "FIN-007-UR"],
          how="T-E3-ESC-PAD back-solves f = (h_meas / h_lam(U))^2; pass if f_meas >= the design value.",
          note="replaces the judged ASM-E3-WAKE (0.5 design / 0.7 nominal) in thermal.py R3")
kit.test("T-E3-ESC-PAD-CFD", "ESC film coefficient on the half-fin mock-up (validates the CFD)",
         verifies=["CL-E3-CFD-FEQ", "CL-E3-CFD-H-HOV"],
         procedure="As T-E3-ESC-PAD: foam-board half-fin with the 22 mm tube and the ASA pad behind the stand prop at "
                   "hover power; ESC replaced by a 45 x 20 x 6 mm aluminium dummy with a 3 W resistor and a thermocouple; "
                   "steady rise -> h. Pass: f_meas >= design value of CL-E3-CFD-FEQ.")

if __name__ == "__main__":
    kit.write()
    print(json.dumps(kit.nodes["CALC-E3-CFD-FEQ"]["outputs"], indent=1))
