"""A3 closure round 2026-11-14: mass packages for gates 2.60 / 2.65 / 2.70 kg with the E/EP props, no test-gated item.

Reads the live roll-up (team/A3/rollup/mass_items.json, written by mass_rollup.py --no-doc) and params.json, adds
delta items (no shared file is edited) and re-runs A3's own mass_rollup() / cg_cases(), so every number uses the
claims' equations. Gate is an argument here; params.json is not touched.

Run:  python -I redesign/team/A3/round1114/closure.py   ->  round1114/out/closure.json
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import package as pk  # noqa: E402  (it(), mirror4(), p(), mr, MGA, ALLOC)

p, mr, it, mirror4 = pk.p, pk.mr, pk.it, pk.mirror4
NOSE = 0.0413                                    # ASM-A3-NOSE-STACK (A3-W3)
POD_LE = p("pod.x_le_m")                         # -0.147 (D-150)
X_B = POD_LE + 0.012                             # D-121 lead behind the nose block (A3.md 3.3, EST position)
X_FF = 0.0465                                    # D-121 first-flight CG line (NP 0.06733 - 0.065 c)
OVR = p("requirements.build_overrun_kg") * 1000  # 84 g
Y4, Z4 = (0.321, -0.321), (0.186, -0.186)
XPROP = p("propulsion.stations.x_prop_plane_m")  # -0.01704
ITEMS = json.loads((HERE.parent / "rollup" / "mass_items.json").read_text(encoding="utf-8"))["a3"]["rollup"]["items"]["value"]


def f2_mass():
    n = {c["id"]: c for c in json.loads((HERE.parents[1] / "F2" / "claims.json").read_text(encoding="utf-8"))["nodes"]}
    return n["CALC-F2-MASS"]["outputs"]


F2 = f2_mass()
LUMPS = sum(r[3] for r in ITEMS if r[1] == "harness" and r[0].startswith("HRN-00"))  # parts.csv lumps (128.22 g)
F2_PRED = 160.31   # F2 mass_estimate.csv by maturity: CALC rows 102.02 g x 1.10 + EST rows 40.05 g x 1.20 (see A3.md closure)
PLUG_G = F2["mass_g"] - LUMPS                                    # 13.86 g: plugs / grommets / sleeves not in the lumps
PLUG_GP = (F2_PRED - LUMPS * 1.10) / PLUG_G * 100 - 100          # growth that makes harness predicted = F2 by maturity

# ---------------------------------------------------------------- corrections and booked adders (not savings)
FIX = {
    # model correction: the HRN-A3-ROUTED adder retired on a 1.2 g parts.csv change; F2 still routes 142.08 g
    "HRN-PLUGS": [it("HRN-A3-PLUGS", "harness", "electrical", PLUG_G, 0.0583, 0.009, 0.0249, "EST", PLUG_GP)],
    # D-161: E/EP props + thin nuts +23.8 g (A1 note on mass.allocation_g.propulsion; CL-E1-MASS-PRP 485.8 g)
    "E1-E-PROPS": mirror4("PRP-003", "propulsion", "propulsion", 5.95, XPROP, Y4, Z4, "DATASHEET"),
    # D-160 named adders: second ESC caps (4 x 2.2 g, next to PWR-008) and XT30U saddles 1.2 g
    "D160-CAPS2": mirror4("PWR-008b", "power", "electrical", 2.2, 0.147, Y4, (0.118, -0.118), "DATASHEET"),
    "D160-SADDLES": [it("HRN-SADDLE", "harness", "electrical", 1.2, 0.0465, 0.0, 0.031, "EST")],
}

BOOKED = {"HRN-PLUGS": "HRN-A3-PLUGS", "E1-E-PROPS": "PRP-A3-EPROP", "D160-CAPS2": "PWR-A3-CAPS2",
          "D160-SADDLES": "HRN-A3-SADDLE"}            # mass_model.csv ids: once booked in the live roll-up, not re-added
LIVE_IDS = {r[0] for r in ITEMS}
FIX = {k: v for k, v in FIX.items() if BOOKED[k] not in LIVE_IDS}

# ---------------------------------------------------------------- savings (design changes; sources in the report)
SAVE = {
    # L1 thin M6 nut ISO 4035 (E hub 0.41 in): 1.9 g x (1 - 3.2/5.2) per nut (A3.md 1.1)
    "L1-THIN-NUT": mirror4("PRP-007", "propulsion", "propulsion", -1.9 * (1 - 3.2 / 5.2), XPROP - 0.008, Y4, Z4, "DATASHEET"),
    # L2 through-core block 3 per + 15 % -> 2 per + 10 % gyroid (A3.md S04): -6.9 g per block
    "L2-BLOCK-INFILL": [it("FIN-004", "fins", "structure", -6.9, 0.062, y, 0.007, "CAD") for y in (0.32, -0.32)],
    # L4 Ti Gr5 motor screws (16) + pinch bolts (4): density 4.43 / 7.93 (A3.md S06)
    "L4-TI-SCREWS": (mirror4("PRP-005", "propulsion", "propulsion", -4 * 0.8 * (1 - 4.43 / 7.93), 0.023, Y4, Z4, "DATASHEET")
                     + mirror4("FIN-101", "fins", "structure", -1.1 * (1 - 4.43 / 7.93), 0.044, Y4, (0.163, -0.163), "DATASHEET")),
    # L5 spar 1000 -> 880 mm (A3.md S05)
    "L5-SPAR-880": [it("WNG-002", "wing", "structure", -0.06 * 102, 0.080, y, 0.0066, "DATASHEET") for y in (0.47, -0.47)],
    # L6 second ESC caps not fitted (F1 shows one 680 uF per ESC passes ripple): removes D160-CAPS2
    "L6-NO-CAPS2": mirror4("PWR-008b", "power", "electrical", -2.2, 0.147, Y4, (0.118, -0.118), "DATASHEET"),
}


def run(extra, gate):
    items = [list(r) for r in ITEMS] + [r for k in extra for r in k]
    pack_rng = [546.0, 590.0]
    M = mr.mass_rollup(items, pk.MGA, gate_kg=gate, growth_g=p("mass.growth_reserve_g"), pack_rng=pack_rng,
                       pack_nom=551.0, overrun_kg=OVR / 1000, **pk.ALLOC)
    C = mr.cg_cases(items, pk.MGA, x_rng=p("cg.x_range_m"), z_rng=p("cg.z_range_m"), x_t=p("cg.x_target_m"),
                    z_m=p("propulsion.stations.z_m"), c=p("wing.chord_m"), te=p("wing.te_x_m"), pack=p("battery.size_m"),
                    slide=pk.SLIDE, foot=p("cg.foot_height_m"), pack_rng=pack_rng, pod_le=POD_LE, nose=NOSE,
                    y_max=p("requirements.cg_lateral_max_m"), aft=p("pod.pack_aft_travel_m"),
                    stations=p("pod.pack_spacer_step_m"), pack_nom=551.0)
    st = C["station_cases"]
    gm = M["gate_margin_kg"] * 1000
    return {"basic_g": M["basic_kg"] * 1000, "pred_g": M["predicted_kg"] * 1000, "gate_margin_g": gm,
            "pack_accept_g": 550.0 + gm - OVR, "margin_546_g": gm + 4.0,
            "alloc": {s[0]: [s[1], s[2], s[3]] for s in M["by_subsystem_g"]},
            "cg_x_basic": C["cg_m"][0], "cg_x_pred": C["cg_pred_m"][0], "stations_use": C["cg_x_station_range_use"],
            "pred_range_use": C["cg_x_pred_range_use"], "hover_split": C["hover_split"], "cg_z": C["cg_z_m"],
            "z_use": C.get("cg_z_range_use"), "y_use": C["cg_y_use"],
            "stations": {k: {kk: v[kk] for kk in ("pack_x_m", "x_cg_m", "x_cg_pred_m", "aft_margin_m", "fwd_margin_m")}
                         for k, v in st.items()}}


def with_ballast(extra, gate):
    """Book D-121 first-flight lead (551 g pack, predicted CG to 0.0465 m) as a 0 %-growth adder, then re-run."""
    r0 = run(extra, gate)
    s = r0["stations"]["551"]
    b = max(0.0, r0["pred_g"] * (s["x_cg_pred_m"] - X_FF) / (X_FF - X_B))
    lead = [[it("BAL-D121", "pod", "structure", b, X_B, 0.0, 0.045, "WEIGHED", 0.0)]] if b > 0 else []
    r = run(extra + lead, gate)
    r["ballast_g"] = b
    r["no_ballast"] = {k: r0[k] for k in ("gate_margin_g", "pack_accept_g", "cg_x_basic", "cg_x_pred", "stations",
                                          "stations_use", "pred_range_use", "hover_split", "y_use", "z_use")}
    r["ff_cg_pred"] = r["stations"]["551"]["x_cg_pred_m"]
    return r


def main():
    out = {"inputs": {"lumps_g": LUMPS, "f2_g": F2["mass_g"], "plug_g": PLUG_G, "plug_gp": PLUG_GP, "fix_added": list(FIX)}}
    fix = list(FIX.values())
    for g in (2.60, 2.65, 2.70):
        key = f"{g:.2f}"
        o = out[key] = {}
        o["live"] = run([], g)
        o["corrected"] = with_ballast(fix, g)
        o["alone"] = {}
        for k, v in SAVE.items():
            r = with_ballast(fix + [v], g)
            o["alone"][k] = {"d_basic": r["basic_g"] - o["corrected"]["basic_g"], "d_pred": r["pred_g"] - o["corrected"]["pred_g"],
                             "d_ballast": r["ballast_g"] - o["corrected"]["ballast_g"],
                             "d_cg_mm": (r["no_ballast"]["cg_x_pred"] - o["corrected"]["no_ballast"]["cg_x_pred"]) * 1000}
        S = SAVE
        pk_a = [S["L6-NO-CAPS2"]]          # L1 thin nut is already inside D-161 (+23.8 g)
        pk_b = pk_a + [S["L2-BLOCK-INFILL"]]
        pk_c = pk_b + [S["L5-SPAR-880"]]
        pk_d = pk_c + [S["L4-TI-SCREWS"]]
        o["P-A"] = with_ballast(fix + pk_a, g)
        o["P-B"] = with_ballast(fix + pk_b, g)
        o["P-C"] = with_ballast(fix + pk_c, g)
        o["P-D"] = with_ballast(fix + pk_d, g)
        o["P-D-noballast"] = run(fix + pk_d, g)
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "closure.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(out["inputs"])
    for g in ("2.60", "2.65", "2.70"):
        print("gate", g)
        for k in ("live", "corrected", "P-A", "P-B", "P-C", "P-D", "P-D-noballast"):
            r = out[g][k]
            s = r["stations"]
            print(f"  {k:9s} basic {r['basic_g']:7.1f} pred {r['pred_g']:7.1f} margin {r['gate_margin_g']:6.1f} "
                  f"(546: {r['margin_546_g']:6.1f}) accept {r['pack_accept_g']:6.1f} bal {r.get('ballast_g', 0):5.1f} "
                  f"cgx {r['cg_x_basic']:.5f}/{r['cg_x_pred']:.5f} st {r['stations_use']:.3f} pu {r['pred_range_use']:.3f} "
                  f"split {r['hover_split']:.3f} aft546 {s['546']['aft_margin_m']*1000:+.2f} aft551 {s['551']['aft_margin_m']*1000:+.2f} "
                  f"fwd590 {s['590']['fwd_margin_m']*1000:+.2f} ff {r.get('ff_cg_pred', 0):.5f}")
        if g == "2.60":
            for k, v in out[g]["alone"].items():
                print(f"    {k:18s} basic {v['d_basic']:+6.2f} pred {v['d_pred']:+6.2f} ballast {v['d_ballast']:+5.2f} cg {v['d_cg_mm']:+.3f} mm")
            print("    alloc corrected", {k: round(v[1], 1) for k, v in out[g]["corrected"]["alloc"].items()})
            for k in ("P-A", "P-B", "P-C", "P-D"):
                print("    alloc", k, {kk: round(v[1], 1) for kk, v in out[g][k]["alloc"].items()})
            for k in ("corrected", "P-B", "P-C", "P-D"):
                nb = out[g][k]["no_ballast"]
                print("    normal flights (no lead)", k, f"cgx {nb['cg_x_basic']:.5f}/{nb['cg_x_pred']:.5f} st {nb['stations_use']:.3f} "
                      f"pu {nb['pred_range_use']:.3f} split {nb['hover_split']:.3f} y {nb['y_use']:.3f} z {nb['z_use']}",
                      {s_: (round(v['pack_x_m'], 4), round(v['x_cg_m'], 5), round(v['x_cg_pred_m'], 5), round(v['aft_margin_m']*1000, 2),
                            round(v['fwd_margin_m']*1000, 2)) for s_, v in nb['stations'].items()})
                fb = out[g][k]["stations"]
                print("    first flights (lead)", k, out[g][k]["ballast_g"], {s_: (round(v['x_cg_m'], 5), round(v['x_cg_pred_m'], 5),
                      round(v['aft_margin_m']*1000, 2), round(v['fwd_margin_m']*1000, 2)) for s_, v in fb.items()})


if __name__ == "__main__" and len(sys.argv) == 1:
    main()


# ---------------------------------------------------------------- D-168 re-book (closure round, second pass)
PACKS = {   # name: (carried g, tolerance g, size m, pack centroid z m, spacer g)  -- sources in A3.md section D-168
    "ovonic6500": (550.0, 5.0, [0.135, 0.046, 0.049], None, 0.0),
    "cnhl6000": (479.0, 10.0, [0.139, 0.047, 0.037], 0.0538, 5.0),
    "gensace6000": (452.0, 10.0, [0.139, 0.047, 0.037], 0.0538, 5.0),
}


def run_pack(name, gate, extra=(), dnose=0.0):
    m, tol, size, zc, sp = PACKS[name]
    items = [list(r) for r in ITEMS]
    for r in items:
        if r[2] == "energy":
            r[3] = m
            r[7], r[8], r[9] = size
            if zc is not None:
                r[6] = zc
    if sp:
        items.append(it("POD-004-SP", "pod", "structure", sp, -0.0362 - dnose, 0.0, 0.0293, "EST"))
    if dnose:   # nose extension: pod shell +0.112 g/mm (POD-001 25.1 g / 225 mm, EST), nose items not moved (conservative)
        items.append(it("POD-001-EXT", "pod", "structure", 0.112 * dnose * 1000, POD_LE - dnose / 2, 0.0, 0.045, "EST"))
    items += [r for k in extra for r in k]
    rng = [m - tol, m + tol]
    M = mr.mass_rollup(items, pk.MGA, gate_kg=gate, growth_g=p("mass.growth_reserve_g"), pack_rng=rng, pack_nom=m,
                       overrun_kg=OVR / 1000, **pk.ALLOC)
    C = mr.cg_cases(items, pk.MGA, x_rng=p("cg.x_range_m"), z_rng=p("cg.z_range_m"), x_t=p("cg.x_target_m"),
                    z_m=p("propulsion.stations.z_m"), c=p("wing.chord_m"), te=p("wing.te_x_m"), pack=size,
                    slide=pk.SLIDE, foot=p("cg.foot_height_m"), pack_rng=rng, pod_le=POD_LE - dnose, nose=NOSE,
                    y_max=p("requirements.cg_lateral_max_m"), aft=p("pod.pack_aft_travel_m"),
                    stations=p("pod.pack_spacer_step_m"), pack_nom=m)
    gm = M["gate_margin_kg"] * 1000
    return {"pack": name, "gate": gate, "basic_g": M["basic_kg"] * 1000, "pred_g": M["predicted_kg"] * 1000,
            "gate_margin_g": gm, "gate_margin_light_g": M["gate_margin_pack_light_kg"] * 1000,
            "gate_margin_heavy_g": M["gate_margin_pack_heavy_kg"] * 1000,
            "pack_accept_g": m + gm - OVR, "accept_need_g": m + tol,
            "alloc": {s[0]: s[2] for s in M["by_subsystem_g"]},
            "cg_x_basic": C["cg_m"][0], "cg_x_pred": C["cg_pred_m"][0], "stations_use": C["cg_x_station_range_use"],
            "pred_range_use": C["cg_x_pred_range_use"], "hover_split": C["hover_split"], "z_use": C.get("cg_z_range_use"),
            "y_use": C["cg_y_use"], "x_fwd_lim": C["pack_x_fwd_limit_m"],
            "stations": {k: {kk: v[kk] for kk in ("pack_x_m", "x_cg_m", "x_cg_pred_m", "aft_margin_m", "fwd_margin_m")}
                         for k, v in C["station_cases"].items()}}


def main168():
    out = {}
    for name in PACKS:
        for lev, ex in (("asis", []), ("L2", [SAVE["L2-BLOCK-INFILL"]])):
            r = run_pack(name, p("requirements.mtow_gate_kg"), ex)
            out[f"{name}_{lev}"] = r
            st = " ".join(f"{k}:{v['pack_x_m']:.4f}/{v['x_cg_pred_m']:.5f} aft{v['aft_margin_m']*1000:+.2f} fwd{v['fwd_margin_m']*1000:+.2f}"
                          for k, v in r["stations"].items())
            print(f"{name:12s} {lev:4s} basic {r['basic_g']:7.1f} pred {r['pred_g']:7.1f} margin {r['gate_margin_g']:6.1f} "
                  f"(light {r['gate_margin_light_g']:.1f} heavy {r['gate_margin_heavy_g']:.1f}) accept {r['pack_accept_g']:6.1f} "
                  f"need {r['accept_need_g']:.0f} | cg {r['cg_x_basic']:.5f}/{r['cg_x_pred']:.5f} st {r['stations_use']:.3f} "
                  f"pu {r['pred_range_use']:.3f} split {r['hover_split']:.3f} z {r['z_use']} y {r['y_use']:.3f} fwdlim {r['x_fwd_lim']:.4f}")
            print("      ", st)
        print("      alloc", {k: round(v, 1) for k, v in out[f"{name}_asis"]["alloc"].items()})
        for d in (0.004, 0.008, 0.012, 0.016, 0.020, 0.024):
            r = run_pack(name, p("requirements.mtow_gate_kg"), [], dnose=d)
            w = min(r["stations"].values(), key=lambda v: v["aft_margin_m"])
            out[f"{name}_nose{int(d*1000)}"] = r
            print(f"      nose +{d*1000:.0f} mm: margin {r['gate_margin_g']:.1f} accept {r['pack_accept_g']:.1f} worst aft {w['aft_margin_m']*1000:+.2f} "
                  f"fwd {min(v['fwd_margin_m'] for v in r['stations'].values())*1000:+.2f} st {r['stations_use']:.3f} pu {r['pred_range_use']:.3f} pack x {w['pack_x_m']:.4f}")
    (HERE / "out" / "closure_d168.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "d168":
    main168()
