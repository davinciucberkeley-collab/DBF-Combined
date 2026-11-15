"""A3 cost re-check 2026-11-14 (D-180): ONE flight pack, CNHL LiHV 4S 6000 120C hard case EC5 (479 +/- 5 g listed).

Reads the live roll-up items (team/A3/rollup/mass_items.json, Gens Ace case) + params.json, swaps the pack, adds the two
unbooked items (harness plugs F2 routes but the lumps do not carry; FIN-108 washers 3.9 g) and re-runs A3's own
mass_rollup() / cg_cases(). WNG-009 (turbulator, 5.9 g) is already a parts.csv line in wing (395.1 g) and the 5.0 g
adder WNG-A3-TURB is retired: nothing is added for it here (no double count). Writes round1114/out/cost_recheck.json.
Run: python -I redesign/team/A3/round1114/cost_recheck.py"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import package as pk  # noqa: E402
p, mr, it, mirror4 = pk.p, pk.mr, pk.it, pk.mirror4
RED = HERE.parents[2]
OVR = p("requirements.build_overrun_kg") * 1000
GATE = p("requirements.mtow_gate_kg")
POD_LE = p("pod.x_le_m")
NOSE = 0.0413
ITEMS = pk.ITEMS
f2 = {c["id"]: c for c in json.loads((RED / "team" / "F2" / "claims.json").read_text(encoding="utf-8"))["nodes"]}["CALC-F2-MASS"]["outputs"]
lumps = sum(r[3] for r in ITEMS if r[1] == "harness")
PLUG_G = f2["mass_g"] - lumps
Y4, Z4 = (0.321, -0.321), (0.186, -0.186)
XM = p("propulsion.stations.x_mount_m")
ADD = {
    "HRN-PLUGS": [it("HRN-A3-ROUTED", "harness", "electrical", PLUG_G, 0.0583, 0.009, 0.0249, "EST")],
    "FIN-108": mirror4("FIN-A3-WASH", "fins", "structure", 3.9 / 4, XM + 0.010, Y4, Z4, "EST"),
}
def sizes(name):
    return {"cnhl": (479.0, 5.0, [0.138, 0.047, 0.037], 0.0538),
            "cnhl10": (479.0, 10.0, [0.138, 0.047, 0.037], 0.0538),
            "gens": (414.0, 10.0, [0.098, 0.047, 0.046], 0.0463),
            "shorty": (419.5, 10.0, [0.097, 0.0475, 0.0475], 0.0471)}[name]

def run(name, xp=None, dnose=0.0, extra=(), foam=0.0, use_add=False, aft=None):
    m, tol, size, zc = sizes(name)
    items = [list(r) for r in ITEMS]
    for r in items:
        if r[2] == "energy":
            r[3] = m; r[7], r[8], r[9] = size; r[6] = zc
            if xp is not None: r[4] = xp
    if use_add: items += [r for k in ADD.values() for r in k]
    if foam: items.append(it("POD-004-SP", "pod", "structure", foam, (xp or -0.0545), 0.0, 0.0293, "EST"))
    if dnose: items.append(it("POD-001-EXT", "pod", "structure", 0.112 * dnose * 1000, POD_LE - dnose / 2, 0.0, 0.045, "EST"))
    items += [r for k in extra for r in k]
    rng = [m - tol, m + tol]
    M = mr.mass_rollup(items, pk.MGA, gate_kg=GATE, growth_g=p("mass.growth_reserve_g"), pack_rng=rng, pack_nom=m,
                       overrun_kg=OVR / 1000, **pk.ALLOC)
    rows = mr._rows(items)
    _, cg = mr._cg(rows)
    _, cgp = mr._cg(rows, lambda r: r["mass_g"] * (1 + mr._growth(r, pk.MGA)))
    lim = POD_LE - dnose + NOSE + size[0] / 2          # most forward pack centroid the crush stack allows (ASM-A3-NOSE-STACK)
    mp = sum(r["mass_g"] for r in rows if r["discipline"] == "energy")
    mt = sum(r["mass_g"] for r in rows)
    C = {"cg_m": cg, "cg_pred_m": cgp, "pack_x_fwd_limit_m": lim,
         "pack_x_req_m": (p("cg.x_target_m") * mt - (mt * cg[0] - mp * (xp if xp is not None else -0.0545))) / mp}
    gm = M["gate_margin_kg"] * 1000
    return {"pack": name, "xp": xp, "dnose": dnose, "basic_g": round(M["basic_kg"] * 1000, 1), "pred_g": round(M["predicted_kg"] * 1000, 1),
            "gate_margin_g": round(gm, 1), "margin_light_g": round(M["gate_margin_pack_light_kg"] * 1000, 1),
            "margin_heavy_g": round(M["gate_margin_pack_heavy_kg"] * 1000, 1), "accept_g": round(m + gm - OVR, 1),
            "accept_need_g": m + tol, "accept_margin_g": round(m + gm - OVR - m - tol, 1),
            "cg_basic": round(C["cg_m"][0], 5), "cg_pred": round(C["cg_pred_m"][0], 5),
            "pack_x_req": round(C["pack_x_req_m"], 4), "x_fwd_lim": round(C["pack_x_fwd_limit_m"], 4),
            "alloc": {s[0]: [s[1], s[2]] for s in M["by_subsystem_g"]},
            "fits_crush_stack": (xp if xp is not None else -0.0545) >= lim - 1e-9,
            "cg_range_ok_basic": p("cg.x_range_m")[0] <= cg[0] <= p("cg.x_range_m")[1],
            "cg_range_ok_pred": p("cg.x_range_m")[0] <= cgp[0] <= p("cg.x_range_m")[1]}

def show(tag, r):
    print(f"{tag:42s} basic {r['basic_g']} pred {r['pred_g']} margin {r['gate_margin_g']} (light {r['margin_light_g']} heavy {r['margin_heavy_g']}) accept {r['accept_g']} need {r['accept_need_g']:.0f} ({r['accept_margin_g']:+.1f}) | cg {r['cg_basic']}/{r['cg_pred']} (range ok {r['cg_range_ok_basic']}/{r['cg_range_ok_pred']}) x_req {r['pack_x_req']} fwdlim {r['x_fwd_lim']} fits {r['fits_crush_stack']}")

out = {"plug_g": PLUG_G, "f2_g": f2["mass_g"], "lumps_g": lumps}
live_ids = {r[0] for r in ITEMS}
print("live items carry the booked adders:", "HRN-A3-ROUTED" in live_ids, "FIN-A3-WASH" in live_ids or "FIN-A3-WASHERS" in live_ids, "| WNG-009 line:", "WNG-009" in live_ids, "| WNG-A3-TURB:", "WNG-A3-TURB" in live_ids)
out["live_gens"] = run("gens", xp=-0.0545); show("live files, Gens Ace 414 g carried", out["live_gens"])
out["shorty"] = run("shorty", xp=-0.0545); show("CNHL Shorty 419.5 g @ -0.0545", out["shorty"])
for tag, kw in (("CNHL 6000 120C @ -0.0545 (asked), foam 5 g", dict(xp=-0.0545, foam=5.0)),
                ("CNHL 6000 120C @ fore-face limit", dict(xp=-0.1035 + 0.069, foam=5.0)),
                ("CNHL 6000 120C @ -0.0545 + nose 20 mm", dict(xp=-0.0545, foam=5.0, dnose=0.020))):
    r = run("cnhl", **kw); out[tag] = r; show(tag, r)
(HERE / "out" / "cost_recheck.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
