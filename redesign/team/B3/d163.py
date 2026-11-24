"""B3 closure round 2026-11-14, D-163 (review/CLOSURE-ROUND-2026-11-14/B3.md section D-163).

Part A: first-flight CG (D-121) re-derived from stability physics. The 5 % static margin stays. The question is where
the neutral point is at the pessimistic end of what the models know today, and how much lead the A3 predicted CG needs
to sit at SM 5 % against that NP. Terms:
  - AVL envelope NP with the CG height, props (Ribner, k = 1) and pod (Munk) as stored in CALC-B3-V-NP-CL;
  - viscous section aerodynamic-centre shift that AVL (thin, inviscid) does not carry: B2's XFOIL S5010 polars give
    dcm(c/4)/dcl > 0 at Re 2-4.5e5 (laminar bubble); for an unswept wing the NP moves by -(dcm/dcl) c. Free-transition
    (Ncrit 9 and 5) and tripped (xtr 0.02, B2 xfoil_tripped.json) bracket it; SU2 SA (fully turbulent) cross-checks;
  - the remaining model terms (AVL vs independent VLM, lattice, CG-height hand check) from claims.verify.json.
Part B: B4's elevon fin-root TE chamfers (CR-B4-32, 20 / 70 mm) run through AVL (avl_model te_chamfer) and the same
calc functions as the claims of record: Cmd / Cld, forward CG limit, stall trim (F4 MIXING_GAIN check), trim share and
roll rate at 1.3 Vs, motor-out roll, roll at the stall, elevon area.

Reads team/B3/claims.json, claims.verify.json, team/B2/out/xfoil_results.json, team/B2/sim/out/xfoil_tripped.json,
team/B2/sim/out/cfd2d_results.json, team/A3/claims.json, team/B1/claims.json, team/E1/claims.json. Writes
team/B3/results/d163.json only. Run (from the repo root):  python -I redesign/team/B3/d163.py [--no-avl]
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs"))


def nodes(p):
    return {n["id"]: n for n in json.loads((ROOT / p).read_text(encoding="utf-8"))["nodes"]}


B3 = nodes("team/B3/claims.json")
V = nodes("team/B3/claims.verify.json")
A3 = nodes("team/A3/claims.json")
B1 = nodes("team/B1/claims.json")
E1 = nodes("team/E1/claims.json")
NPCL = V["CALC-B3-V-NP-CL"]
c = NPCL["input_values"]["c"]
sm_min = NPCL["input_values"]["sm_min"]
nu = json.loads((ROOT / "team/B2/out/xfoil_results.json").read_text())["nu_m2s"]
out = {"_note": "B3 closure round D-163; EST throughout (models UNVERIFIED until T-B3-TWIN-NP)."}

# ------------------------------------------------------------------------------- A1. viscous ac shift (XFOIL, SU2)
XF = json.loads((ROOT / "team/B2/out/xfoil_results.json").read_text())["polars"]


def slope_cm_cl(table, cl0, half=0.15):
    pts = [(r[1], r[4]) for r in table if cl0 - half <= r[1] <= cl0 + half]
    n = len(pts)
    mx, my = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    return sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)


def xfoil_slope(Re, cl, ncrit=9):
    keys = sorted((float(k.split("_re")[1].split("_")[0]), k) for k in XF
                  if k.startswith("s5010_re") and f"_n{ncrit}_f+0_p220" in k and k.endswith("p220"))
    rs = [r for r, _ in keys]
    sl = [slope_cm_cl(XF[k]["table"], cl) for _, k in keys]
    if Re <= rs[0]:
        return sl[0]
    if Re >= rs[-1]:
        return sl[-1]
    for (r0, s0), (r1, s1) in zip(zip(rs, sl), zip(rs[1:], sl[1:])):
        if r0 <= Re <= r1:
            return s0 + (s1 - s0) * (Re - r0) / (r1 - r0)


trip = json.loads((ROOT / "team/B2/sim/out/xfoil_tripped.json").read_text())
cfd = json.loads((ROOT / "team/B2/sim/out/cfd2d_results.json").read_text())
su2 = {r["alpha"]: r for r in cfd["cases"] if r["delta"] == 0.0 and r["level"] == 2 and r["re"] == 260000.0}
out["su2_dcm_dcl_a4_a8"] = (su2[8.0]["CMz"] - su2[4.0]["CMz"]) / (su2[8.0]["CL"] - su2[4.0]["CL"])
rows = NPCL["outputs"]["rows"]
visc = {}
for tag in ("vmax", "vc", "vt"):
    r = rows[tag]
    Re = r["V"] * c / nu
    s9, s5 = xfoil_slope(Re, r["CL"], 9), slope_cm_cl(XF["s5010_re2.6e5_n5_f+0_p220"]["table"], r["CL"])
    st = slope_cm_cl(trip["clean_tripped"], r["CL"])
    visc[tag] = {"V": r["V"], "CL": r["CL"], "Re": Re, "dcm_dcl_free_n9": s9, "dcm_dcl_free_n5_re26": s5,
                 "dcm_dcl_tripped": st, "dnp_free_m": -max(s9, s5) * c, "dnp_tripped_m": -max(st, out["su2_dcm_dcl_a4_a8"]) * c,
                 "xnp_avl": r["xnp"]}
out["viscous"] = visc

# ------------------------------------------------------------------------------- A2. NP budget, aft limits, lead
vlm_c = V["CL-B3-V-VLM-XNP"]["value"]                  # (AVL - VLM) / c, flat wing; < 0: AVL NP ahead (conservative)
lattice = V["CL-B3-V-XNP-LATTICE"]["value"]            # m
hand = V["CL-B3-V-NPZ-HAND"]["value"] * rows["vt"]["dxnp_avl"]   # m, CG-height term hand vs AVL
other = abs(lattice) + abs(hand) + max(0.0, vlm_c * c)  # only a non-conservative AVL-VLM difference is charged
out["other_terms_m"] = {"lattice": lattice, "cg_height_hand_vs_avl": hand, "avl_minus_vlm": vlm_c * c, "charged": other}
x_pred = A3["CL-A3-CG-X-PRED"]["value"]
m_pred = A3["CL-A3-MASS-PREDICTED"]["value"]
X_LEAD = -0.135                                         # A3 closure §1.1: lead at the nose + 12 mm


def lead_g(x_cg, x_target, m):
    return 0.0 if x_cg <= x_target else 1000 * m * (x_cg - x_target) / (x_target - X_LEAD)


cases = {}
for case, key in (("model_of_record", None), ("free_transition", "dnp_free_m"), ("tripped", "dnp_tripped_m")):
    xa = []
    for tag, v in visc.items():
        dnp = 0.0 if key is None else v[key]
        xnp = v["xnp_avl"] + dnp - (0.0 if key is None else other)
        xa.append((xnp - sm_min * c, tag, xnp))
    x_aft, tag, xnp = min(xa)
    cases[case] = {"x_aft_sm5": x_aft, "binding_speed": tag, "xnp": xnp, "a3pred_margin_mm": 1000 * (x_aft - x_pred),
                   "sm_at_a3pred": (xnp - x_pred) / c, "lead_g": lead_g(x_pred, x_aft, m_pred),
                   "lead_g_to_0p5mm_inside": lead_g(x_pred, x_aft - 0.0005, m_pred)}
cases["d121_line"] = {"x": 0.0465, "lead_g": lead_g(x_pred, 0.0465, m_pred),
                      "sm_free_transition": (cases["free_transition"]["xnp"] - 0.0465) / c,
                      "sm_model": (cases["model_of_record"]["xnp"] - 0.0465) / c}
out["cg_cases"] = cases
out["x_a3_pred"], out["m_pred"], out["g_per_mm"] = x_pred, m_pred, lead_g(x_pred + 0.001, x_pred, m_pred)

# ------------------------------------------------------------------------------- A3. turbulator drag cost
xc = XF["s5010_re3.5e5_n9_f+0_p220"]["table"]
cl_c = rows["vc"]["CL"]


def cd_at(table, cl, col_cl=1, col_cd=2):
    t = sorted(table, key=lambda r: r[col_cl])
    for a, b in zip(t, t[1:]):
        if a[col_cl] <= cl <= b[col_cl]:
            return a[col_cd] + (b[col_cd] - a[col_cd]) * (cl - a[col_cl]) / (b[col_cl] - a[col_cl])


cd_free, cd_trip = cd_at(xc, cl_c), cd_at(trip["clean_tripped"], cl_c)
q = 0.5 * 1.225 * rows["vc"]["V"] ** 2
S = NPCL["input_values"]["S"]
D_cr = B1["CL-B1-CRUISE-DRAG"]["value"]
P_cr = E1["CL-E1-CRUISE-P-55-V17"]["value"] if "CL-E1-CRUISE-P-55-V17" in E1 else None
eta = (D_cr * rows["vc"]["V"]) / P_cr if P_cr else None
dD = (cd_trip - cd_free) * q * S
out["turbulator"] = {"cl_cruise": cl_c, "cd_free_re35": cd_free, "cd_tripped": cd_trip, "dD_N": dD,
                     "D_cruise_N": D_cr, "P_cruise_W": P_cr, "eta_chain": eta,
                     "dP_W": None if eta is None else dD * rows["vc"]["V"] / eta,
                     "note": "tripped polar at B2's xtr 0.02 (re_stall), cd at the cruise CL; B1 already carries a "
                             "1.10 tape factor on the free-transition cd (ASM-B1-WING-ROUGH)"}

# ------------------------------------------------------------------------------- B. elevon chamfers through AVL
if "--no-avl" not in sys.argv:
    import avl_model as AV
    import sc_analysis as SC
    import verify_asdesigned as VA
    CH = [0.02, 0.07]
    _orig = AV.geometry_from

    def geometry_ch(*a, **k):
        g = _orig(*a, **k)
        g["te_chamfer"] = CH
        return g

    AV.geometry_from = geometry_ch
    iv = lambda n, d=B3: dict(d[n]["input_values"])  # noqa: E731
    lon = SC.avl_long(**iv("CALC-B3-AVL-LONG"))
    vcg_in = iv("CALC-B3-V-CG", V)
    vcg = VA.cg_v(**vcg_in)
    st_in = iv("CALC-B3-STALL-TRIM")
    st_in["x_fwd"] = vcg["x_fwd_gate"]
    st = SC.stall_trim(**st_in)
    ca_in = iv("CALC-B3-CRUISE-AUTH")
    ca_in.update(x_fwd=vcg["x_fwd_gate"], Cld=lon["Cld"], Clp=lon["Clp"])
    ca = SC.cruise_auth(**ca_in)
    ro_in = iv("CALC-B3-ROLL")
    ro_in.update(Cld=lon["Cld"], Clp=lon["Clp"], d_stall=st["delta_target"])
    ro = SC.roll_authority(**ro_in)
    ea = B3["CALC-B3-ELEVON-AREA"]["input_values"]
    a0 = 2 * ((ea["yin"][1] - ea["yin"][0]) + (ea["yout"][1] - ea["yout"][0])) * ea["f"] * ea["c"]
    a_cut = 2 * 0.5 * (CH[0] + CH[1]) * ea["f"] * ea["c"]
    mix = B3["CALC-B3-STALL-TRIM"]  # F4 mix: |delta_stall| / (MIXING_GAIN x full travel)
    fsw = json.loads((ROOT / "subsystems/flight-software/params.json").read_text(encoding="utf-8"))
    mg = fsw["fsw"]["mixing_gain"]["value"] if "fsw" in fsw else fsw["mixing_gain"]["value"]
    trav = max(abs(t) for t in ca_in["travel"])
    before = {"Cmd": B3["CALC-B3-AVL-LONG"]["outputs"]["Cmd_ref"], "Cld": B3["CALC-B3-AVL-LONG"]["outputs"]["Cld"],
              "x_fwd": V["CALC-B3-V-CG"]["outputs"]["x_fwd_gate"],
              "delta_stall": B3["CALC-B3-STALL-TRIM"]["outputs"]["delta_target"],
              "trim_use": B3["CALC-B3-CRUISE-AUTH"]["outputs"]["trim_use"],
              "p_degs": B3["CALC-B3-CRUISE-AUTH"]["outputs"]["p_degs"],
              "motorout": B3["CALC-B3-CRUISE-AUTH"]["outputs"]["motorout_ratio"],
              "pb2v": B3["CALC-B3-ROLL"]["outputs"]["pb2v"], "t60": B3["CALC-B3-ROLL"]["outputs"]["t60_s"],
              "frac": a0 / ea["S"]}
    after = {"Cmd": lon["Cmd_ref"], "Cld": lon["Cld"], "x_fwd": vcg["x_fwd_gate"], "binding": vcg["binding_gate"],
             "delta_stall": st["delta_target"], "vs_fwd": st["vs_fwd"], "trim_use": ca["trim_use"],
             "p_degs": ca["p_degs"], "motorout": ca["motorout_ratio"], "pb2v": ro["pb2v"], "t60": ro["t60_s"],
             "frac": (a0 - a_cut) / ea["S"]}
    for d in (before, after):
        d["f4_mix_ratio"] = abs(d["delta_stall"]) / (mg * trav)
    out["chamfer"] = {"te_chamfer_m": CH, "before": before, "after": after, "mixing_gain": mg, "travel_deg": trav}

(HERE / "results" / "d163.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k not in ("viscous",)}, indent=1, default=str))
print(json.dumps(out["viscous"], indent=1))
