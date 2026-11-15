"""A3 design round 2026-11-14: mass-reduction search, scratch analysis only.

Reads the live roll-up items (team/A3/rollup/mass_items.json) and params.json, applies the wave-1 additions and
candidate savings as delta items (no shared file is edited), and re-runs A3's own pure functions
mass_rollup() and cg_cases() from team/A3/mass_rollup.py, so every number uses the same equations as the claims.

Run:  python -I redesign/team/A3/round1114/package.py   ->  round1114/out/package.json
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
A3 = HERE.parent
RED = A3.parent.parent
sys.path.insert(0, str(A3))
import mass_rollup as mr  # noqa: E402  (pure functions only; nothing is written)

P = json.loads((RED / "params" / "params.json").read_text(encoding="utf-8"))


def p(key):
    d = P
    for k in key.split("."):
        d = d[k]
    return d["value"] if isinstance(d, dict) and "value" in d else d


ITEMS = json.loads((A3 / "rollup" / "mass_items.json").read_text(encoding="utf-8"))["a3"]["rollup"]["items"]["value"]
MGA = {"EST": 20, "CALC": 10, "DATASHEET": 5, "CAD": 5, "WEIGHED": 1}
ALLOC = {k: v["value"] for k, v in P["mass"]["allocation_g"].items() if isinstance(v, dict)}
NOSE0 = 0.0346                                 # ASM-A3-NOSE-STACK
SLIDE = 0.028                                  # ASM-A3-PACK-SLIDE


def it(i, sub, disc, g, x, y, z, mat, gp=None):
    return [i, sub, disc, g, x, y, z, 0.01, 0.01, 0.01, mat, gp, "A3 round1114 delta"]


def mirror4(i, sub, disc, g, x, ys, zs, mat):
    return [it(i, sub, disc, g, x, y, z, mat) for y in ys for z in zs]


Y4, Z4 = (0.321, -0.321), (0.186, -0.186)
# ------------------------------------------------------------------ wave-1 additions (sources in A3.md section 2)
ADD = {
    "C4-RW-TUBE": [it("FIN-002", "fins", "structure", 0.344 * 156 - 35.09, 0.045, y, 0.0, "DATASHEET") for y in (0.32, -0.32)],
    "C4B3-CHEEKS": mirror4("FIN-003", "fins", "structure", 0.59, 0.030, Y4, (0.179, -0.179), "CAD"),
    # B3 9 deg / face_ahead 12 mm: motor + prop + adapter + nut + washer + screws move 4.5 mm forward (C4 1.5)
    "B3-STATION-FWD": (mirror4("PRP-MOVE", "propulsion", "propulsion", -(81 + 17 + 3 + 1.2 + 1.9 + 0.6 + 3.2), 0.008, Y4, Z4, "DATASHEET")
                       + mirror4("PRP-MOVE", "propulsion", "propulsion", (81 + 17 + 3 + 1.2 + 1.9 + 0.6 + 3.2), 0.008 - 0.0045, Y4, Z4, "DATASHEET")),
    "C5-NOSE": [it("POD-001", "pod", "structure", 1.4, -0.144, 0, 0.045, "EST"),
                it("POD-009", "pod", "structure", 0.23, -0.12, 0, 0.047, "EST"),
                # pitot socket, pitot boom, nose wall move 7 mm forward
                it("POD-MOVE", "pod", "structure", -(5.8 + 2.0), -0.135, -0.03, 0.045, "CAD"),
                it("POD-MOVE", "pod", "structure", (5.8 + 2.0), -0.142, -0.03, 0.045, "CAD"),
                it("AVN-MOVE", "avionics", "avionics", -4.24, -0.160, -0.046, 0.045, "EST"),
                it("AVN-MOVE", "avionics", "avionics", 4.24, -0.167, -0.046, 0.045, "EST")],
    "C2-DOUBLER": [it("WNG-003", "wing", "structure", 10.0, 0.06, y, 0.0, "EST") for y in (0.32, -0.32)],
    "E1-E-PROPS": mirror4("PRP-003", "propulsion", "propulsion", 6.0, -0.013 - 0.0045, Y4, Z4, "DATASHEET"),
    "E1-THIN-NUT": mirror4("PRP-007", "propulsion", "propulsion", -1.9 * (1 - 3.2 / 5.2), -0.021 - 0.0045, Y4, Z4, "EST"),
    "E2-LIION": [],                                # pack mass handled through the pack cases (see run())
}

# ------------------------------------------------------------------ candidate savings
SAVE = {
    "S01-FIN006-PLUG": [it("FIN-006", "fins", "structure", -5.45, 0.045, y, 0.007, "DATASHEET") for y in (0.32, -0.32)],
    # plug kept but re-sourced to fit the 19.05 mm bore: CF 19 x 17 vs 20 x 18, same 53 mm (area ratio 72 / 76)
    "S01R-PLUG-19x17": [it("FIN-006", "fins", "structure", -5.45 * (1 - 72 / 76), 0.045, y, 0.007, "EST") for y in (0.32, -0.32)],
    "S02-PWR003-LISTING": [it("PWR-003", "power", "electrical", -28.0, -0.036, -0.046, 0.046, "EST"),
                           it("PWR-003", "power", "electrical", 11.4, -0.036, -0.046, 0.046, "DATASHEET")],
    "S03-PHASE-EXT": [it("HRN-PH", "harness", "electrical", -13.84, 0.0556, 0, 0, "EST")],
    "S04-BLOCK-INFILL": [it("FIN-004", "fins", "structure", -6.9, 0.062, y, 0.007, "CAD") for y in (0.32, -0.32)],
    "S05-SPAR-880": [it("WNG-002", "wing", "structure", -0.06 * 102, 0.080, y, 0.0066, "DATASHEET") for y in (0.47, -0.47)],
    "S06-TI-SCREWS": (mirror4("PRP-005", "propulsion", "propulsion", -4 * 0.8 * (1 - 4.43 / 7.93), 0.028 - 0.0045, Y4, Z4, "DATASHEET")
                      + mirror4("FIN-101", "fins", "structure", -1.1 * (1 - 4.43 / 7.93), 0.044, Y4, (0.163, -0.163), "DATASHEET")),
    "S07-AL-PROP-NUT": mirror4("PRP-007", "propulsion", "propulsion", -1.9 * (1 - 2.81 / 7.85), -0.021 - 0.0045, Y4, Z4, "EST"),
    "S08-FILLET-MICROLIGHT": mirror4("FIN-001", "fins", "structure", -5.6 * 16.4 / 30.6 / 4, 0.17, (0.32, -0.32), (0.02, -0.02), "EST"),
    # glass band replaces the 60 mm tape doubler it overlays: 0.025 m2 per station x 0.065 kg/m2 (notes-W; skin.areal)
    "S09-DOUBLER-TAPE-CREDIT": [it("WNG-003", "wing", "structure", -0.025 * 65, 0.06, y, 0.0, "CAD") for y in (0.32, -0.32)],
}


def run(extra, nose=NOSE0, pod_le=None, pack_carried=None):
    items = [list(r) for r in ITEMS] + [r for k in extra for r in k]
    if pack_carried is not None:
        for r in items:
            if r[2] == "energy":
                r[3] = pack_carried
    pack_rng = [546.0, 590.0]
    M = mr.mass_rollup(items, MGA, gate_kg=p("requirements.mtow_gate_kg"), growth_g=p("mass.growth_reserve_g"),
                       pack_rng=pack_rng, pack_nom=551.0, overrun_kg=p("requirements.build_overrun_kg"), **ALLOC)
    C = mr.cg_cases(items, MGA, x_rng=p("cg.x_range_m"), z_rng=p("cg.z_range_m"), x_t=p("cg.x_target_m"),
                    z_m=p("propulsion.stations.z_m"), c=p("wing.chord_m"), te=p("wing.te_x_m"), pack=p("battery.size_m"),
                    slide=SLIDE, foot=p("cg.foot_height_m"), pack_rng=pack_rng, pod_le=pod_le or p("pod.x_le_m"),
                    nose=nose, y_max=p("requirements.cg_lateral_max_m"), aft=p("pod.pack_aft_travel_m"),
                    stations=p("pod.pack_spacer_step_m"), pack_nom=551.0)
    st = C["station_cases"]
    return {"basic_g": M["basic_kg"] * 1000, "pred_g": M["predicted_kg"] * 1000,
            "gate_margin_g": M["gate_margin_kg"] * 1000,
            "free_above_overrun_g": (M["gate_margin_kg"] - p("requirements.build_overrun_kg")) * 1000,
            "alloc": {s[0]: [s[1], s[2], s[3]] for s in M["by_subsystem_g"]},
            "worst_alloc": [M["worst_alloc_subsystem"], M["worst_alloc_ratio"]],
            "cg_x_basic": C["cg_m"][0], "cg_x_pred": C["cg_pred_m"][0], "cg_z": C["cg_z_m"], "cg_y_use": C["cg_y_use"],
            "hover_split": C["hover_split"], "stations_use": C["cg_x_station_range_use"],
            "pred_range_use": C["cg_x_pred_range_use"],
            "stations": {k: {kk: v[kk] for kk in ("pack_x_m", "x_cg_m", "x_cg_pred_m", "range_use", "aft_margin_m",
                                                  "fwd_margin_m", "clamped")} for k, v in st.items()},
            "x_fwd_lim": C["pack_x_fwd_limit_m"]}


def ballast_g(r, x_b, x_max=0.0465, pack="551", which="x_cg_m"):
    """Nose ballast that brings the 551 g case CG to x_max (D-121 first-flight line), lead at x_b."""
    s = r["stations"][pack]
    m = r["basic_g"] if which == "x_cg_m" else r["pred_g"]
    x = s[which]
    return max(0.0, m * (x - x_max) / (x_max - x_b))


def main():
    out = {}
    base = run([])
    out["baseline"] = base
    nose_c5 = dict(nose=NOSE0 + 0.007 - 0.0003, pod_le=-0.147)   # C5: stack 41.3 mm (34.6 + 7 - 0.3 step), nose -0.147
    firm = [ADD["C4-RW-TUBE"], ADD["C4B3-CHEEKS"], ADD["B3-STATION-FWD"], ADD["C5-NOSE"], ADD["C2-DOUBLER"]]
    props = [ADD["E1-E-PROPS"], ADD["E1-THIN-NUT"]]
    out["round_MR"] = run(firm, **nose_c5)
    out["round_E"] = run(firm + props, **nose_c5)
    out["round_E_liion"] = run(firm + props, pack_carried=573.5, **nose_c5)
    out["round_MR_liion"] = run(firm, pack_carried=573.5, **nose_c5)
    # each addition alone (incremental on the baseline)
    out["adds_alone"] = {k: {kk: run([v], **(nose_c5 if k == "C5-NOSE" else {}))[kk] - base[kk]
                             for kk in ("basic_g", "pred_g", "cg_x_pred", "stations_use")}
                         for k, v in ADD.items() if v}
    # each saving alone, on the round_E and round_MR states
    for tag, adds in (("E", firm + props), ("MR", firm)):
        ref = out[f"round_{tag}"]
        out[f"save_on_{tag}"] = {}
        for k, v in SAVE.items():
            if k == "S07-AL-PROP-NUT" and tag == "E":        # thin steel nut -> thin Al nut
                v = mirror4("PRP-007", "propulsion", "propulsion", -1.9 * 3.2 / 5.2 * (1 - 2.81 / 7.85),
                            -0.021 - 0.0045, Y4, Z4, "EST")
            r = run(adds + [v], **nose_c5)
            out[f"save_on_{tag}"][k] = {"d_basic_g": r["basic_g"] - ref["basic_g"], "d_pred_g": r["pred_g"] - ref["pred_g"],
                                        "d_cg_pred_mm": (r["cg_x_pred"] - ref["cg_x_pred"]) * 1000,
                                        "stations_use": r["stations_use"]}
    # packages
    pk_firm = [SAVE["S01-FIN006-PLUG"], SAVE["S07-AL-PROP-NUT"]]
    pk_cond = [SAVE["S02-PWR003-LISTING"], SAVE["S03-PHASE-EXT"]]
    al_thin = mirror4("PRP-007", "propulsion", "propulsion", -1.9 * 3.2 / 5.2 * (1 - 2.81 / 7.85), -0.0255, Y4, Z4, "EST")
    out["pkg_MR_firm"] = run(firm + pk_firm, **nose_c5)
    out["pkg_MR_firm_cond"] = run(firm + pk_firm + pk_cond, **nose_c5)
    out["pkg_MR_all"] = run(firm + pk_firm + pk_cond + [SAVE["S06-TI-SCREWS"]], **nose_c5)
    out["pkg_E_firm_cond"] = run(firm + props + [SAVE["S01-FIN006-PLUG"], al_thin] + pk_cond, **nose_c5)
    out["pkg_E_all"] = run(firm + props + [SAVE["S01-FIN006-PLUG"], al_thin] + pk_cond
                           + [SAVE["S06-TI-SCREWS"], SAVE["S04-BLOCK-INFILL"], SAVE["S08-FILLET-MICROLIGHT"]], **nose_c5)
    pk_firm2 = [SAVE["S01-FIN006-PLUG"], SAVE["S09-DOUBLER-TAPE-CREDIT"]]
    out["pkg_E_firm"] = run(firm + props + pk_firm2 + [al_thin], **nose_c5)
    out["pkg_MR_rec"] = run(firm + pk_firm + pk_firm2[1:] + pk_cond + [SAVE["S06-TI-SCREWS"]], **nose_c5)
    out["pkg_MR_rec_nonose"] = run(firm + pk_firm + pk_firm2[1:] + pk_cond + [SAVE["S06-TI-SCREWS"]])
    out["pkg_E_rec"] = run(firm + props + pk_firm2 + [al_thin] + pk_cond
                           + [SAVE["S06-TI-SCREWS"], SAVE["S04-BLOCK-INFILL"], SAVE["S08-FILLET-MICROLIGHT"]], **nose_c5)
    out["pkg_E_rec_spar"] = run(firm + props + pk_firm2 + [al_thin] + pk_cond
                           + [SAVE["S06-TI-SCREWS"], SAVE["S05-SPAR-880"], SAVE["S08-FILLET-MICROLIGHT"]], **nose_c5)
    out["round_MR_nonose"] = run(firm)
    S = SAVE
    base_set = [S["S01R-PLUG-19x17"], S["S08-FILLET-MICROLIGHT"], S["S09-DOUBLER-TAPE-CREDIT"], S["S06-TI-SCREWS"]]
    tests = [S["S02-PWR003-LISTING"], S["S03-PHASE-EXT"]]
    out["REC_MR_designonly"] = run(firm + base_set + [S["S07-AL-PROP-NUT"]], **nose_c5)
    out["REC_MR"] = run(firm + base_set + [S["S07-AL-PROP-NUT"]] + tests, **nose_c5)
    out["REC_MR_nonose"] = run(firm + base_set + [S["S07-AL-PROP-NUT"]] + tests)
    out["REC_E_designonly"] = run(firm + props + base_set + [al_thin], **nose_c5)
    out["REC_E"] = run(firm + props + base_set + [al_thin] + tests, **nose_c5)
    out["REC_E_block"] = run(firm + props + base_set + [al_thin] + tests + [S["S04-BLOCK-INFILL"]], **nose_c5)
    out["REC_E_block_spar"] = run(firm + props + base_set + [al_thin] + tests + [S["S04-BLOCK-INFILL"], S["S05-SPAR-880"]], **nose_c5)
    out["REC_MR_plugdel"] = run(firm + base_set[1:] + [S["S01-FIN006-PLUG"], S["S07-AL-PROP-NUT"]] + tests, **nose_c5)
    # ---- A1 final decisions (message 2026-11-14): MR props, RW tube + S01R, 9 deg / 12 mm + cheeks, C5 nose, S08
    fin_base = [ADD["C4-RW-TUBE"], ADD["C4B3-CHEEKS"], ADD["B3-STATION-FWD"], ADD["C5-NOSE"],
                S["S01R-PLUG-19x17"], S["S08-FILLET-MICROLIGHT"]]
    dcell = [[it("WNG-DCELL", "wing", "structure", 16.5 / 2, 0.058, y, 0.0, "EST") for y in (0.32, -0.32)]]
    out["FINAL_a"] = run(fin_base, **nose_c5)
    out["FINAL_b"] = run(fin_base + tests, **nose_c5)
    out["FINAL_c_a"] = run(fin_base + dcell, **nose_c5)
    out["FINAL_c_b"] = run(fin_base + dcell + tests, **nose_c5)
    # D-121 first-flight ballast (lead behind the nose block, x = nose + 12 mm)
    for k in ("baseline", "round_MR", "round_E", "pkg_MR_firm_cond", "pkg_E_firm_cond", "pkg_MR_rec", "pkg_E_rec", "REC_MR", "REC_E", "REC_E_block", "FINAL_a", "FINAL_b", "FINAL_c_a", "FINAL_c_b"):
        xb = (-0.140 if k == "baseline" else -0.147) + 0.012
        out[k]["ballast_d121_g"] = {"basic": ballast_g(out[k], xb), "pred": ballast_g(out[k], xb, which="x_cg_pred_m")}
    # growth by maturity, baseline
    g = {}
    for r in ITEMS:
        gp = r[11] if r[11] is not None else (0 if r[2] == "energy" else MGA[r[10]])
        g.setdefault(r[10], [0.0, 0.0])
        g[r[10]][0] += r[3]
        g[r[10]][1] += r[3] * gp / 100
    out["growth_by_maturity"] = g
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "package.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k in ("baseline", "round_MR", "round_E", "round_E_liion", "round_MR_liion", "pkg_MR_firm", "pkg_MR_firm_cond",
              "pkg_MR_all", "pkg_E_firm_cond", "pkg_E_all", "pkg_E_firm", "pkg_MR_rec",
              "pkg_MR_rec_nonose", "pkg_E_rec", "pkg_E_rec_spar", "round_MR_nonose", "REC_MR_designonly", "REC_MR", "REC_MR_nonose",
              "REC_E_designonly", "REC_E", "REC_E_block", "REC_E_block_spar", "REC_MR_plugdel", "FINAL_a", "FINAL_b", "FINAL_c_a", "FINAL_c_b"):
        r = out[k]
        print(f"{k:18s} basic {r['basic_g']:7.1f} pred {r['pred_g']:7.1f} margin {r['gate_margin_g']:6.1f} "
              f"free {r['free_above_overrun_g']:6.1f} | stations {r['stations_use']:.3f} pred_use {r['pred_range_use']:.3f} "
              f"cgx {r['cg_x_basic']:.5f}/{r['cg_x_pred']:.5f} split {r['hover_split']:.3f} worst {r['worst_alloc'][0]} "
              f"{r['worst_alloc'][1]:.3f} fwdlim {r['x_fwd_lim']:.4f} pack {r['stations']['546']['pack_x_m']:.3f} "
              f"bal {r.get('ballast_d121_g', '')}")
    print(json.dumps(out["adds_alone"], indent=0))
    for tag in ("MR", "E"):
        print(tag)
        for k, v in out[f"save_on_{tag}"].items():
            print(f"  {k:24s} {v['d_basic_g']:7.2f} {v['d_pred_g']:7.2f} cg {v['d_cg_pred_mm']:+.3f} mm  st {v['stations_use']:.3f}")
    print({k: [round(a, 1), round(b, 1)] for k, (a, b) in g.items()})
    for k in ("FINAL_a", "FINAL_b", "FINAL_c_a", "FINAL_c_b"):
        print(k, {s: v for s, v in out[k]["alloc"].items()})
        print(k, json.dumps(out[k]["stations"]))


if __name__ == "__main__":
    main()



