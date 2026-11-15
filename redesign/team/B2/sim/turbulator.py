"""B2 closure round 2026-11-14 (D-163 / D163-3): S5010 with an upper-surface turbulator, XFOIL forced transition.

    python -I redesign/team/B2/sim/turbulator.py        -> team/B2/sim/out/turbulator.json, sim/params.trip.json
    (~3-6 min, 4 XFOIL processes at a time; cached polars are re-used unless --force)

Why: B3 (CLOSURE-ROUND-2026-11-14/B3.md, D-163) found a viscous aerodynamic-centre term: on the free-transition polar
dcm/dcl = +0.0126 at 1.3 Vs, NP 4.0 mm forward. A zigzag turbulator at x/c 0.05 on the upper surface fixes the
boundary-layer state. B3's pass lines: dcm/dcl <= 0.0032 and cd(CL 0.39) <= 0.0146.

Cases (same section, 220 panels, Ncrit 9 for the untripped part, as xfoil_wing.py), Re 2.6 / 3.4 / 3.65 / 3.9e5:
  free    no trip (reference)
  t05     xtr_top 0.05, lower free          (design: tape aft edge at x/c 0.05)
  t10     xtr_top 0.10, lower free          (sensitivity: the trip acts late)
  t05b05  xtr_top 0.05, xtr_bot 0.05        (sensitivity: lower surface also turbulent, e.g. a lower seam)
  t02b02  xtr 0.02 both (B3's EST basis, xfoil_tripped.py) at Re 2.6e5 only, read from sim/out/xfoil_tripped.json
Per polar: cd and local dcm/dcl (least-squares slope of cm(cl) within +/-0.15 of the cl point, B3 d163.py method) at
CL 0.30..0.50, CLmax, alpha at CLmax. B3's three wingborne rows (vmax 18, vc 17, vt 1.3 Vs) are re-scaled to the
gate mass (P:requirements.mtow_gate_kg) and read at their own Re by linear interpolation in Re.

XFOIL fixed transition has NO device drag (Gopalarathnam et al. 2003, J. Aircraft 40(4) p. 770). The tape's own
drag is added by a hand model (EST):
  dcd_dev = C_Dk * (k / c) * (u_k / V)^2,    u_k = Ue * f(k / delta)   (Pohlhausen quartic, Lambda 0:
  f(eta) = 2 eta - 2 eta^3 + eta^4, delta = delta* / 0.3), Ue and delta* from an XFOIL DUMP of the free case at
  x/c 0.05 upper surface, C_Dk = 1.0 (ASM, pessimistic for a wall-mounted 2-D step whose top is inside the layer).
  Trip-height check: Re_k = u_k k / nu against 600 (Braslow-Knox 3-D roughness, as cited in the FFA-W3 tape study)
  and 125-200 for zigzag tape (TU Delft thesis), stated as secondary.
Cruise drag and power at performance.cruise_ms and the gate mass: dD = q S dcd_wing (whole span, both panels; the
pod covers the root 0.14 m but the tape runs full span, so the full S is charged), dP_elec = dD V x (P / (D V)) of
E1's CL-E1-CRUISE-P-55-V17 / CL-E1-CRUISE-DRAG (average ratio, EST).
"""
from __future__ import annotations

import concurrent.futures as cf
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
B2 = HERE.parent
REDESIGN = B2.parents[1]
FORCE = "--force" in sys.argv
sys.argv = [sys.argv[0]]
spec = importlib.util.spec_from_file_location("xfoil_wing", B2 / "xfoil_wing.py")
XW = importlib.util.module_from_spec(spec)
spec.loader.exec_module(XW)

P = json.loads((REDESIGN / "params" / "params.json").read_text(encoding="utf-8"))


def pv(path):
    d = P
    for k in path.split("."):
        d = d[k]
    return d["value"]


def claims_of(rel):
    d = json.loads((REDESIGN / rel).read_text(encoding="utf-8"))
    return {n["id"]: n for n in d.get("nodes", [])}


C = pv("wing.chord_m")
S = pv("wing.span_m") * C
RHO, G = pv("env.rho_kgm3"), pv("env.g_ms2")
M_GATE = pv("requirements.mtow_gate_kg")
V_CR = pv("performance.cruise_ms")
NU = XW.NU
FOIL = "s5010"
RES = [2.6e5, 3.4e5, 3.65e5, 3.9e5]
CASES = {"free": (1.0, 1.0), "t05": (0.05, 1.0), "t10": (0.10, 1.0), "t05b05": (0.05, 0.05),
         # lower-surface trip sweep (closure round finding: the dcm/dcl term is the lower-surface laminar run)
         "t05b20": (0.05, 0.20), "t05b40": (0.05, 0.40), "t05b60": (0.05, 0.60), "b05": (1.0, 0.05),
         "b10": (1.0, 0.10), "b20": (1.0, 0.20), "b40": (1.0, 0.40), "b60": (1.0, 0.60), "t10b20": (0.10, 0.20),
         "t02b02": (0.02, 0.02)}   # B3 EST basis, re-run here with 0.25 deg steps from 0 (xfoil_tripped.py stopped at 9.5 deg)
CL_PTS = [0.30, 0.35, 0.39, 0.40, 0.45, 0.47, 0.50]
K_TRIP = 0.4e-3        # m, zigzag tape thickness (B3 D-163 turbulator specification)
X_TRIP = 0.05          # x/c of the tape aft edge
C_DK = 1.0             # ASM-B2C-TRIP-CDK (pessimistic)
PASS_DCM, PASS_CD = 0.0032, 0.0146


def polar(re_, case):
    xt, xb = CASES[case]
    tag = f"trip_{FOIL}_re{re_/1e5:.2f}e5_{case}"
    out = XW.OUT / f"pol_{tag}.txt"
    key = XW.OUT / f"pol_{tag}.key"
    want = f"{FOIL} Re={re_:.0f} n9 xtr={xt},{xb} npan={XW.NPAN} a=-4,18,0.25"
    if out.exists() and key.exists() and key.read_text().strip() == want and not FORCE:
        return (re_, case), np.loadtxt(out, ndmin=2)
    res = []
    for side, a1, step in (("p", 18.0, 0.25), ("n", -4.0, -0.25)):
        f = XW.OUT / f"raw_{tag}_{side}.txt"
        if f.exists():
            f.unlink()
        cmd = XW.geom(FOIL, 0.0, XW.NPAN) + (f"OPER\nVISC {re_:.0f}\nITER 250\nVPAR\nN 9\nXTR {xt} {xb}\n\n"
                                             f"PACC\n{f.name}\n\nASEQ 0 {a1} {step}\nPACC\n\nQUIT\n")
        log = XW.run(cmd, timeout=300)
        (XW.OUT / f"log_{tag}_{side}.txt").write_text(log[-20000:])
        res.append(XW.parse_polar(f))
    a = np.vstack(res)
    if len(a):
        a = a[np.argsort(a[:, 0])]
        _, i = np.unique(a[:, 0], return_index=True)
        a = a[i]
    np.savetxt(out, a, fmt="%10.5f", header="XFOIL 6.99: alpha CL CD CDp Cm xtr_top xtr_bot")
    key.write_text(want + "\n")
    return (re_, case), a


def attached(a):
    return a[: int(np.argmax(a[:, 1])) + 1]


def slope(a, cl0, half=0.15):
    t = attached(a)
    w = t[(t[:, 1] >= cl0 - half) & (t[:, 1] <= cl0 + half)]
    if len(w) < 4:
        return float("nan")
    return float(np.polyfit(w[:, 1], w[:, 4], 1)[0])


def cd_at(a, cl0):
    t = attached(a)
    t = t[np.argsort(t[:, 1])]
    return float(np.interp(cl0, t[:, 1], t[:, 2]))


def summ(a):
    i = int(np.argmax(a[:, 1]))
    t = attached(a)
    w = t[(t[:, 1] >= 0.3) & (t[:, 1] <= 0.5)]
    return {"n": int(len(a)), "clmax": float(a[i, 1]), "alpha_clmax": float(a[i, 0]),
            "alpha_max_converged": float(a[:, 0].max()),
            "clmax_converged_to_stall": bool(a[:, 0].max() > a[i, 0] + 0.75),
            "cd": {f"{c:.2f}": cd_at(a, c) for c in CL_PTS},
            "dcm_dcl": {f"{c:.2f}": slope(a, c) for c in CL_PTS},
            "dcm_dcl_fit_0p3_0p5": float(np.polyfit(w[:, 1], w[:, 4], 1)[0]) if len(w) >= 4 else float("nan"),
            "cm_at_cl0p7": float(np.interp(0.7, t[np.argsort(t[:, 1]), 1], t[np.argsort(t[:, 1]), 4])),
            "xtr_top_at_cl0p39": float(np.interp(0.39, t[np.argsort(t[:, 1]), 1], t[np.argsort(t[:, 1]), 5]))}


def dump(re_, cl):
    f = XW.OUT / f"dump_trip_{FOIL}_re{re_/1e5:.2f}e5_cl{cl:.2f}.txt"
    if not f.exists() or FORCE:
        cmd = XW.geom(FOIL, 0.0, XW.NPAN) + f"OPER\nVISC {re_:.0f}\nITER 250\nCL {cl}\nDUMP\n{f.name}\n\nQUIT\n"
        XW.run(cmd)
    rows = []
    for line in f.read_text().splitlines():
        v = line.split()
        if len(v) >= 8 and not line.lstrip().startswith("#"):
            try:
                rows.append([float(x) for x in v[:8]])     # s x y Ue/Vinf Dstar Theta Cf H
            except ValueError:
                pass
    r = np.array(rows)
    r = r[r[:, 1] <= 1.0 + 1e-6]                         # airfoil only (wake rows have x > 1)
    i_le = int(np.argmin(r[:, 1]))
    return r[:i_le + 1][::-1], r[i_le:]                  # upper, lower (each LE -> TE)


def bl_at(re_, cl, x, surf, k):
    """Free-transition (untripped) laminar layer just ahead of the trip: Ue/V, delta*, u at height k (Pohlhausen
    quartic, Lambda 0), Re_k = u_k k / nu, device drag C_Dk (k/c)(u_k/V)^2."""
    up, lo = dump(re_, cl)
    r = up if surf == "upper" else lo
    ue = abs(float(np.interp(x, r[:, 1], r[:, 3])))
    ds = float(np.interp(x, r[:, 1], r[:, 4])) * C
    delta = ds / 0.3
    eta = min(1.0, k / delta)
    fk = 2 * eta - 2 * eta ** 3 + eta ** 4
    V = re_ * NU / C
    uk = ue * fk
    return {"re": re_, "cl": cl, "x_c": x, "surface": surf, "k_m": k, "ue_over_v": ue, "dstar_m": ds,
            "delta_m": delta, "k_over_delta": k / delta, "uk_over_v": uk, "re_k": uk * V * k / NU,
            "dcd_device": C_DK * (k / C) * uk ** 2}


def k_for_rek(re_, cl, x, surf, target=600.0):
    lo_, hi_ = 0.05e-3, 2.0e-3
    for _ in range(50):
        mid = 0.5 * (lo_ + hi_)
        lo_, hi_ = (mid, hi_) if bl_at(re_, cl, x, surf, mid)["re_k"] < target else (lo_, mid)
    return 0.5 * (lo_ + hi_)


def main():
    jobs = [(r, c) for r in RES for c in CASES]
    pol = {}
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for k, a in ex.map(lambda j: polar(*j), jobs):
            pol[k] = a
    res = {"_note": "team/B2/sim/turbulator.py (closure round 2026-11-14, D163-3). XFOIL 6.99, S5010, 220 panels, "
                    "Ncrit 9 where free. EST: device drag hand model, cruise power scaling.",
           "k_trip_m": K_TRIP, "x_trip_c": X_TRIP, "c_dk": C_DK, "pass": {"dcm_dcl": PASS_DCM, "cd_0p39": PASS_CD},
           "polars": {}}
    for (r, c), a in sorted(pol.items()):
        res["polars"][f"re{r/1e5:.2f}e5_{c}"] = {"re": r, "case": c, "summary": summ(a),
                                                 "table": [[round(float(x), 5) for x in row] for row in a]}
    trip02 = json.loads((HERE / "out" / "xfoil_tripped.json").read_text())
    t02 = np.array(trip02["clean_tripped"])
    res["polars"]["re2.60e5_t02b02_xfoil_tripped_py"] = {"re": 2.6e5, "case": "t02b02", "summary": summ(t02),
                                        "table": trip02["clean_tripped"]}

    # --- B3 rows at the gate mass, interpolated in Re (3.4-3.9e5)
    b3 = json.loads((REDESIGN / "team" / "B3" / "results" / "d163.json").read_text())["viscous"]
    m_b3 = 2.6                                   # B3 d163 rows are at 2.6 kg (CL = 2 m g / (rho V^2 S))
    rows = {}
    for tag, r in b3.items():
        V = r["V"] if tag != "vt" else r["V"] * math.sqrt(M_GATE / m_b3)
        CL = 2 * M_GATE * G / (RHO * V * V * S)
        Re = V * C / NU
        row = {"V": V, "CL": CL, "Re": Re}
        for case in CASES:
            rs = [x for x in RES if x >= 3.4e5]
            sl = [slope(pol[(x, case)], CL) for x in rs]
            cd = [cd_at(pol[(x, case)], CL) for x in rs]
            row[f"dcm_dcl_{case}"] = float(np.interp(Re, rs, sl))
            row[f"cd_{case}"] = float(np.interp(Re, rs, cd))
        rows[tag] = row
    res["b3_rows_gate"] = rows

    # --- trip designs: XFOIL forced transition + device drag (EST) at cruise; Re_k at cruise and 1.3 Vs
    vc, vt = rows["vc"], rows["vt"]
    E1 = claims_of("team/E1/claims.json")
    p_e1, d_e1 = E1["CL-E1-CRUISE-P-55-V17"]["value"], E1["CL-E1-CRUISE-DRAG"]["value"]
    ratio = p_e1 / (d_e1 * V_CR)
    q = 0.5 * RHO * V_CR ** 2
    re_vt = vt["Re"]
    designs = {   # case: [(surface, x/c, k)] ; k None = sized for Re_k 600 at 1.3 Vs, rounded up to 0.1 mm
        "U05_k0.4 (B3 spec)": ("t05", [("upper", 0.05, 0.4e-3)]),
        "U05L05": ("t05b05", [("upper", 0.05, 0.4e-3), ("lower", 0.05, None)]),
        "L05": ("b05", [("lower", 0.05, None)]),
        "L10": ("b10", [("lower", 0.10, None)]),
        "L20": ("b20", [("lower", 0.20, None)]),
        "L40": ("b40", [("lower", 0.40, None)]),
    }
    dz = {}
    for name, (case, trips) in designs.items():
        tl, dev = [], 0.0
        for surf, x, k in trips:
            if k is None:
                k = math.ceil(k_for_rek(re_vt, vt["CL"], x, surf) * 1e4) / 1e4
            b_c = bl_at(vc["Re"], vc["CL"], x, surf, k)
            b_t = bl_at(re_vt, vt["CL"], x, surf, k)
            b_s = bl_at(2.6e5, 0.8, x, surf, k)
            dev += b_c["dcd_device"]
            tl.append({"surface": surf, "x_c": x, "k_m": k, "cruise": b_c, "vt": b_t, "stall_cl0.8": b_s})
        dcd_x = vc[f"cd_{case}"] - vc["cd_free"]
        dcd = dcd_x + dev
        dz[name] = {"case": case, "trips": tl, "dcm_dcl_rows": {t: rows[t][f"dcm_dcl_{case}"] for t in rows},
                    "dcm_dcl_max": max(rows[t][f"dcm_dcl_{case}"] for t in rows),
                    "cd_free": vc["cd_free"], "cd_xfoil": vc[f"cd_{case}"], "dcd_xfoil": dcd_x,
                    "dcd_device_est": dev, "dcd_total": dcd, "cd_total": vc["cd_free"] + dcd,
                    "dD_N": q * S * dcd, "dP_shaft_W": q * S * dcd * V_CR, "dP_elec_W": q * S * dcd * V_CR * ratio,
                    "dP_frac_of_E1": q * S * dcd * V_CR * ratio / p_e1,
                    "clmax_re2p6": res["polars"][f"re2.60e5_{case}"]["summary"]["clmax"],
                    "pass_dcm": max(rows[t][f"dcm_dcl_{case}"] for t in rows) <= PASS_DCM,
                    "pass_cd": vc["cd_free"] + dcd <= PASS_CD}
    res["designs"] = dz
    res["cruise"] = {"V": V_CR, "m": M_GATE, "CL": vc["CL"], "q": q, "S": S, "p_e1_W": p_e1, "d_e1_N": d_e1,
                     "p_over_dv": ratio, "b3_est": {"dcd": 0.0067, "dP_elec_W": 0.0067 * q * S * V_CR * ratio}}
    (HERE / "out" / "turbulator.json").write_text(json.dumps(res, indent=1))
    try:
        write_params(res)
    except Exception as ex:  # noqa: BLE001
        print("write_params skipped:", ex)
    # --- print
    print(f"gate {M_GATE} kg; rows (V, CL, Re):", {k: (round(r['V'], 2), round(r['CL'], 3), round(r['Re'])) for k, r in rows.items()})
    for k, p in res["polars"].items():
        s = p["summary"]
        print(f"  {k:<18} clmax {s['clmax']:.3f} @ {s['alpha_clmax']:5.2f} (to {s['alpha_max_converged']:.2f})  "
              f"cd .30/.39/.47/.50 {s['cd']['0.30']:.4f}/{s['cd']['0.39']:.4f}/{s['cd']['0.47']:.4f}/{s['cd']['0.50']:.4f}"
              f"  dcm/dcl .30/.39/.47/.50 {s['dcm_dcl']['0.30']:+.4f}/{s['dcm_dcl']['0.39']:+.4f}/"
              f"{s['dcm_dcl']['0.47']:+.4f}/{s['dcm_dcl']['0.50']:+.4f}  fit {s['dcm_dcl_fit_0p3_0p5']:+.4f}  "
              f"xtr_top@.39 {s['xtr_top_at_cl0p39']:.3f}")
    for k, r in rows.items():
        print(f"  row {k}: " + "  ".join(f"{c}: dcm {r['dcm_dcl_' + c]:+.4f} cd {r['cd_' + c]:.4f}" for c in CASES))
    for n, o in dz.items():
        ks = ", ".join(f"{t['surface']} {t['x_c']} k {t['k_m']*1e3:.1f} mm Re_k cr/vt/stall {t['cruise']['re_k']:.0f}/"
                       f"{t['vt']['re_k']:.0f}/{t['stall_cl0.8']['re_k']:.0f} k/d {t['vt']['k_over_delta']:.2f}"
                       for t in o["trips"])
        print(f"  {n}: dcm/dcl max {o['dcm_dcl_max']:+.4f}  cd {o['cd_xfoil']:.4f} + dev {o['dcd_device_est']:.4f}"
              f" = {o['cd_total']:.4f} (dcd {o['dcd_total']:+.4f})  dD {o['dD_N']:+.3f} N dP {o['dP_elec_W']:+.1f} W "
              f"({o['dP_frac_of_E1']*100:+.1f} %)  clmax2.6 {o['clmax_re2p6']:.3f}  pass {o['pass_dcm']}/{o['pass_cd']}"
              f"\n      {ks}")


DESIGN = "L20"     # B2 recommendation (closure round): lower-surface zigzag at x/c 0.20, k sized for Re_k 600 at 1.3 Vs


def write_params(res):
    def e(v, unit, note, src="SRC-B2-XFOIL", st="MODELLED"):
        return {"value": v, "unit": unit, "source": src, "status": st, "note": note}
    dz = res["designs"]
    d = dz[DESIGN]
    u = dz["U05_k0.4 (B3 spec)"]
    pol = res["polars"]
    p = {"_note": "Written by team/B2/sim/turbulator.py (closure round 2026-11-14). Do not edit by hand.",
         "b2sim": {"trip": {
             "design": e(DESIGN, "-", "turbulator design evaluated: " + json.dumps(
                 [{"surface": t["surface"], "x_c": t["x_c"], "k_m": t["k_m"]} for t in d["trips"]])),
             "dcm_dcl_design_max": e(d["dcm_dcl_max"], "-", "XFOIL forced transition, max over B3's rows vmax/vc/vt "
                                     "at the gate mass (local slope +/-0.15 in cl, Re-interpolated 3.4-3.9e5)"),
             "dcm_dcl_upper05_max": e(u["dcm_dcl_max"], "-", "same, B3's spec (upper x/c 0.05 only, lower free)"),
             "dcm_dcl_free_max": e(max(r["dcm_dcl_free"] for r in res["b3_rows_gate"].values()), "-",
                                   "same, free transition (Ncrit 9)"),
             "dcm_dcl_lower_late_max": e(max(max(r["dcm_dcl_b40"], r["dcm_dcl_b60"]) for r in res["b3_rows_gate"].values()),
                                         "-", "lower transition at x/c 0.40 / 0.60 (trip acting late), upper free"),
             "cd_design_cruise": e(d["cd_total"], "-", "section cd at the cruise CL (17 m/s, gate mass): XFOIL forced "
                                   "transition + device drag (EST)", st="ESTIMATED"),
             "cd_free_cruise": e(d["cd_free"], "-", "free transition at the cruise CL"),
             "dcd_design_cruise": e(d["dcd_total"], "-", "design minus free, incl. device drag", st="ESTIMATED"),
             "dcd_device_design": e(d["dcd_device_est"], "-", "C_Dk (k/c)(u_k/V)^2, C_Dk 1.0 (EST)", st="ESTIMATED"),
             "dcd_upper05_cruise": e(u["dcd_total"], "-", "B3's spec, incl. device drag", st="ESTIMATED"),
             "re_k_design_vt": e(min(t["vt"]["re_k"] for t in d["trips"]), "-", "u_k k / nu at 1.3 Vs, gate mass"),
             "k_design_m": e(max(t["k_m"] for t in d["trips"]), "m", "tape height for Re_k >= 600 at 1.3 Vs"),
             "clmax_design_re2p6": e(d["clmax_re2p6"], "-", "section clmax, design trip state, Re 2.6e5"),
             "clmax_free_re2p6": e(pol["re2.60e5_free"]["summary"]["clmax"], "-", "free n9, Re 2.6e5 (same run set)"),
             "clmax_tripped_min": e(min(v["summary"]["clmax"] for k, v in pol.items()
                                        if k.startswith("re2.60e5_") and v["case"] != "free"
                                        and "xfoil_tripped_py" not in k and v["summary"]["clmax_converged_to_stall"]),
                                    "-", "lowest section clmax at Re 2.6e5 over every forced-transition case of this "
                                         "script that converged past its clmax (upper 0.02-0.10, lower 0.05-0.60)"),
             "clmax_t05b05_re2p6": e(pol["re2.60e5_t05b05"]["summary"]["clmax"], "-", "xtr 0.05 both, Re 2.6e5"),
             "e1_p_over_dv": e(res["cruise"]["p_over_dv"], "-", "CL-E1-CRUISE-P-55-V17 / (CL-E1-CRUISE-DRAG x V)",
                               src="SRC-B2-AVL", st="ESTIMATED"),
         }}}
    (HERE / "params.trip.json").write_text(json.dumps(p, indent=1))
    print("sim/params.trip.json written")


if __name__ == "__main__":
    main()
