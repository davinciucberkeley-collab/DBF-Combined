"""C5 design round 2026-11-14: CL-C5-PACK-STACK-MARGIN options on the C5 crash model (landing_calc.crash, unchanged).

Run:  python -I redesign/team/C5/dr1114/crash_stack.py   -> dr1114/out/crash_stack.json
Inputs are the recorded input values of CALC-C5-CRASH (team/C5/claims.json) and of CALC-A3-CG (team/A3/claims.json);
options are in-script overrides. The A3 CG function (team/A3/mass_rollup.cg_cases) is called unchanged with the
moved pod nose and nose stack, to get the pack stations and CG margins the D-98 rule would pick.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
C5 = HERE.parent
sys.path.insert(0, str(C5))
sys.path.insert(0, str(C5.parent / "A3"))
import landing_calc as LC  # noqa: E402
import mass_rollup as A3  # noqa: E402


def node(f, i):
    ns = json.loads(Path(f).read_text("utf-8"))["nodes"]
    return ns[i] if isinstance(ns, dict) else next(n for n in ns if n["id"] == i)


IV = node(C5 / "claims.json", "CALC-C5-CRASH")["input_values"]
AV = node(C5.parent / "A3" / "claims.json", "CALC-A3-CG")["input_values"]
NOSE0 = 0.0088          # nose wall 4.8 + bond line 1.0 + stop 3.0 mm (ASM-A3-NOSE-STACK)
SP = IV["t_sp"]


def crash(**ov):
    kw = dict(IV)
    kw.update(ov)
    return LC.crash(**kw)


def a3(**ov):
    kw = dict(AV)
    kw.update(ov)
    c = A3.cg_cases(**kw)
    return {"pack_x_fwd_limit_m": c["pack_x_fwd_limit_m"],
            "stations": {k: {"pack_x_m": v["pack_x_m"], "fwd_margin_mm": v["fwd_margin_m"] * 1e3,
                             "aft_margin_mm": v["aft_margin_m"] * 1e3, "clamped": v["clamped"]}
                         for k, v in c["station_cases"].items()}}


def per_pack_margin(r, stations):
    """Margin of each pack at the A3 station: x_station - x_fwd_max (>= 0 keeps block B)."""
    return {k: (stations[k]["pack_x_m"] - r["packs"][k if k != "551" else "551"]["x_fwd_max_m"]) * 1e3
            for k in ("546", "551", "590")}


def summary(label, r, st=None, **extra):
    s = {"label": label, "stack_margin_mm": r["stack_margin_worst_m"] * 1e3,
         "block_L_mm": {k: v["L_m"] * 1e3 for k, v in r["packs"].items()},
         "n_pack": {k: v["n"] for k, v in r["packs"].items()},
         "x_fwd_max_m": {k: v["x_fwd_max_m"] for k, v in r["packs"].items()},
         "x_stack_m": r["x_stack_m"], "box_x_slack_mm": r["box_x_slack_m"] * 1e3}
    if st:
        s["a3"] = st
        s["pack_at_station_margin_mm"] = per_pack_margin(r, st["stations"])
    s.update(extra)
    return s


def main():
    out = []
    # 0. as is
    r0 = crash()
    st0 = a3()
    out.append(summary("as is (D-62 bay, 34.6 mm stack)", r0, st0))
    need = max(v["L_m"] for v in r0["packs"].values())                 # worst pack block (590 g)
    stack_req = NOSE0 + SP + need
    # 1. notes-P option: block 28 mm cut, stack 38.3, nose -4 mm
    for dn, stack in ((0.004, 0.0383), (0.005, 0.0393), (0.007, 0.0413), (0.008, 0.0423)):
        x_le = IV["x_le"] - dn
        r = crash(x_le=x_le, blk_min=stack)
        st = a3(pod_le=x_le, nose=stack)
        out.append(summary("nose -%d mm, stack %.1f mm" % (dn * 1e3, stack * 1e3), r, st, nose_move_mm=dn * 1e3))
    # 2. plateau sensitivity at the -4 mm / 38.3 option and the window of sigma it tolerates
    win = {}
    for dn, stack in ((0.004, 0.0383), (0.007, 0.0413)):
        x_le = IV["x_le"] - dn
        Lmax = stack - NOSE0 - SP                                    # block length the stack holds
        KE = 0.5 * 0.590 * IV["v"] ** 2
        eff = IV["eps_d"] - IV["eps_y"] / 2
        A = IV["bay_w"] * IV["bay_h"]
        s_lo = KE / (eff * Lmax) / A                                  # plateau below this: 590 g block too short
        s_hi = IV["n_pack"] * 0.546 * IV["g"] / A                     # plateau above this: 546 g pack > 100 g
        rows = {}
        for f in (0.90, 0.95, 1.0, 1.05, 1.10):
            r = crash(x_le=x_le, blk_min=stack, sigma=IV["sigma"] * f)
            rows["%.2f" % f] = {"stack_margin_mm": r["stack_margin_worst_m"] * 1e3, "n_pack_max": r["n_pack_max"]}
        win["nose -%d / stack %.1f mm" % (dn * 1e3, stack * 1e3)] = {
            "sigma_min_kPa": s_lo / 1e3, "sigma_max_kPa": s_hi / 1e3, "rows": rows}
    # 3. C3 / A1 2026-11-14: the drawn block section (D-143 top 3 mm under the hatch) and C3's 3 x 3 mm step option.
    #    The crash model's force is sigma * bay_w * bay_h, so the section is set through bay_h = A / bay_w. The step
    #    (3 mm high over the full 52 mm width, 3 mm long at the fore top edge) lowers the force over its first 3 mm of
    #    block length; its extra length is 3 mm x (1 - F_step / F), added by hand below.
    sec = {"drawn D-143 (top 3 mm clear)": (0.052 * (0.0594 - 0.003) - 2.4e-4, 0.0),
           "C3 step (top 0.5 mm clear, 3x3 step)": (0.052 * (0.0594 - 0.0005) - 2.4e-4,
                                                    0.003 * (0.052 * 0.003) / (0.052 * (0.0594 - 0.0005) - 2.4e-4))}
    sect = {}
    for name, (A, dL) in sec.items():
        bh = A / IV["bay_w"]
        rows = []
        for dn in (0.0, 0.004, 0.005, 0.006, 0.007, 0.008):
            stack = 0.0343 + dn                                       # C3 condition: forward limit stays -0.0382
            if dn == 0.0:
                stack = IV["blk_min"]
            x_le = IV["x_le"] - dn
            r = crash(x_le=x_le, blk_min=stack, bay_h=bh)
            L590 = r["packs"]["590"]["L_m"] + dL
            row = {"nose_move_mm": dn * 1e3, "stack_mm": stack * 1e3, "x_le_m": x_le,
                   "x_fwd_limit_m": x_le + stack + IV["pack"][0] / 2,
                   "F_N": r["packs"]["590"]["F_N"], "L590_mm": L590 * 1e3,
                   "stack_margin_mm": (r["stack_margin_worst_m"] - dL) * 1e3,
                   "n_546": r["packs"]["546"]["n"], "rows_sigma": {}}
            for f in (0.90, 0.95, 1.05, 1.10):
                rr = crash(x_le=x_le, blk_min=stack, bay_h=bh, sigma=IV["sigma"] * f)
                row["rows_sigma"]["%.2f" % f] = {"stack_margin_mm": (rr["stack_margin_worst_m"] - dL / f) * 1e3,
                                                 "n_546_uncapped": f * IV["sigma"] * A / (0.546 * IV["g"])}
            Lmax = stack - NOSE0 - SP - dL
            row["sigma_min_kPa"] = 0.5 * 0.590 * IV["v"] ** 2 / (0.525 * Lmax) / A / 1e3
            row["sigma_max_kPa_546_100g"] = IV["n_pack"] * 0.546 * IV["g"] / A / 1e3
            rows.append(row)
        sect[name] = {"A_m2": A, "dL_step_mm": dL * 1e3, "rows": rows}
    # 3. no hardware: per-pack forward limit (590 g pack to its own x_fwd_max, next aft 2 mm step)
    res = {"as_is": out[0], "need_block_590_mm": need * 1e3, "stack_required_mm": stack_req * 1e3,
           "nose_move_required_mm": (stack_req - IV["blk_min"]) * 1e3, "options": out[1:], "plateau_window": win, "sections": sect}
    (HERE / "out" / "crash_stack.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
