"""T-098: build redesign/qp/A/mechanism/out/T098_results.json (T097_results.json schema) from the sweep JSONs.  python -I t098_collect.py"""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, "..", "T098_results.json")
P25 = json.load(open(os.path.join(H, "plateau_rib25.json")))["rows"]; P14 = json.load(open(os.path.join(H, "plateau_rib14.json")))["rows"]
rows = []
def add(a, cat, case, metric, value, limit, ok, note=""): rows.append(dict(analysis=a, category=cat, case=case, metric=metric, value=value, limit=limit, pass_=ok, note=note))
RB = "rigid-body dynamics"
CH = 37.5
for r in [x for x in P25 if x["Fp"] == CH]:
    c = f"chosen_37.5N_rib25x23/{r['case']}"
    add("AR-016", RB, c, "foam stroke (mm)", round(r["stroke_mm"], 1), "<= 20.0", r["stroke_mm"] <= 20.0, "usable stroke 20 mm (EST); pad 30 mm long, CAD envelope unchanged")
    add("AR-016", RB, c, "peak load factor (g)", round(r["n_g"], 2), "<= 12.0", r["n_g"] <= 12.0, "A-P5 12 g; zeta 0.05")
    add("AR-016", RB, c, "end tilt (deg)", round(r["tilt_deg"], 1), "<= 3.0", r["tilt_deg"] <= 3.0, "")
    add("AR-016", RB, c, "rib-root RF (min over run)", round(r["rib_rf"], 2), ">= 1.0", r["rib_rf"] >= 1.0, "CAD rib 25x23 (D-226); allowables EST; AR-012 rib-root check only")
def worst(rows_, F):
    rs = [x for x in rows_ if x["Fp"] == F]
    return max(x["stroke_mm"] for x in rs), max(x["n_g"] for x in rs), max(x["tilt_deg"] for x in rs), min(x["rib_rf"] for x in rs)
for F in sorted({x["Fp"] for x in P25}):
    s, n, t, rf = worst(P25, F); ok = s <= 20 and n <= 12 and t <= 3 and rf >= 1
    add("AR-016", RB, f"plateau_sweep_rib25x23/{F:g}N", "worst of 10 cases: stroke mm / n g / tilt deg / rib RF", f"{s:.1f} / {n:.2f} / {t:.2f} / {rf:.2f}", "20 / 12 / 3.0 / 1.0", ok, "passes at zeta 0.05 only; the accepted spec is the joint (Fp, zeta) region, see zeta2 rows" if ok else "fails at zeta 0.05")
for F in sorted({x["Fp"] for x in P14}):
    s, n, t, rf = worst(P14, F); ok = s <= 20 and n <= 12 and t <= 3 and rf >= 1
    add("AR-016", RB, f"plateau_sweep_rib14x12_T097_basis/{F:g}N", "worst of 10 cases: stroke mm / n g / tilt deg / rib RF", f"{s:.1f} / {n:.2f} / {t:.2f} / {rf:.2f}", "20 / 12 / 3.0 / 1.0", ok, "stale 14x12 tube, not the drawn part (D-226 is 25x23)")
# pitch-use rows: values from the T-097 SITL runs (AR-015). The standing line is 0.60 of 15 deg (SITL-FLIGHT.md l.25); the 20 deg basis proposal was withdrawn (D-244 rev, review 98-4)
for case, v15, v20, v25 in (("T097_Z5 (Z5_gb0, 1.881 kg)", 0.69, 0.52, 0.41), ("T097_Z5_lua", 0.69, 0.52, 0.41), ("T097_T074", 0.79, 0.59, 0.47), ("T097_T074_lua", 0.77, 0.58, 0.46)):
    add("AR-016", "flight dynamics", case, "elevon pitch use on the 15 deg basis (standing line, governing)", v15, "<= 0.60", v15 <= 0.60, "FAIL, open item (AR-010 item 5); 15 deg = K09-L 25 deg travel less 10 deg kept")
    add("AR-016", "flight dynamics", case, "elevon pitch use on the 20 deg basis (information only, proposal withdrawn)", v20, "information", None, "NOT the line: the 20 deg basis raises the pitch allowance 9 -> 12 deg with no derivation of A's reserve (D-244, review 98-4)")
    add("AR-016", "flight dynamics", case, "elevon pitch use on the 25 deg basis (information only, old plant stop)", v25, "information", None, "A stops are +-21 deg")
add("AR-016", "flight dynamics", "T097_T074 / Z5_gb0 1.881 kg", "worst peak individual elevon deflection (deg): T-074 12.0, Z5 10.6", 12.0, "information (< 19.5 saturation)", None, "T-074 sum.json elevon_max_deg 12.0; t_elevon_sat 0 s in Z5")
Z = json.load(open(os.path.join(H, "zeta_rib25.json")))["rows"]; C = json.load(open(os.path.join(H, "card_rib25.json")))["rows"]
for (F, z) in sorted({(x["Fp"], x["zeta"]) for x in Z}):
    rs = [x for x in Z if x["Fp"] == F and x["zeta"] == z]
    s, n, t, rf = max(x["stroke_mm"] for x in rs), max(x["n_g"] for x in rs), max(x["tilt_deg"] for x in rs), min(x["rib_rf"] for x in rs)
    add("AR-016", RB, f"zeta_sensitivity_rib25x23/{F:g}N_zeta{z}", "worst of 10 cases: stroke mm / n g / tilt deg / rib RF", f"{s:.1f} / {n:.2f} / {t:.2f} / {rf:.2f}", "20 / 12 / 3.0 / 1.0", s <= 20 and n <= 12 and t <= 3 and rf >= 1, "pad damping ratio varied; TP-3 gate is zeta <= 0.05")
for x in C:
    if x["group"] in ("card_drift", "card_lean", "card_sink"):
        add("AR-016", RB, f"rung1_card_scan_30N/{x['case']}", "foam stroke (mm)", round(x["stroke_mm"], 1), "<= 20.0", x["stroke_mm"] <= 20.0, "30 N plateau, rib 25x23; rung 1 evaluation, not adopted")
Z2 = json.load(open(os.path.join(H, "zeta2_rib25.json")))["rows"]
for (F, z) in sorted({(x["Fp"], x["zeta"]) for x in Z2}, key=lambda t: (t[1], t[0])):
    rs = [x for x in Z2 if x["Fp"] == F and x["zeta"] == z]
    s_, n, t, rf = max(x["stroke_mm"] for x in rs), max(x["n_g"] for x in rs), max(x["tilt_deg"] for x in rs), min(x["rib_rf"] for x in rs)
    add("AR-016", RB, f"zeta_grid_rib25x23/{F:g}N_zeta{z}", "worst of 10 cases: stroke mm / n g / tilt deg / rib RF", f"{s_:.2f} / {n:.2f} / {t:.2f} / {rf:.2f}", "20 / 12 / 3.0 / 1.0", s_ <= 20 and n <= 12 and t <= 3 and rf >= 1, "T-098 rev 2 zeta grid (review 98-1)")
add("AR-016", RB, "accepted_foam_region", "Fp N per foot AND zeta AND usable stroke mm", "37.5-39.0 AND 0.02-0.05 AND >= 20", "model passes every tested corner; D-226 cell path scaled to 39.2 N (EST)", True, "joint region only, 1.5 N wide; outside it rerun landing_a (and T-083 strength rows above 39 N) at the measured pair; UNVERIFIED until TP-3")
S24 = json.load(open(os.path.join(H, "stroke24_rib25.json")))["rows"]; Z24 = json.load(open(os.path.join(H, "zeta24_rib25.json")))["rows"] + json.load(open(os.path.join(H, "zeta24b_rib25.json")))["rows"]
def w24(rs):
    return max(x["stroke_mm"] for x in rs), max(x["n_g"] for x in rs), max(x["tilt_deg"] for x in rs), min(x["rib_rf"] for x in rs)
for F in sorted({x["Fp"] for x in S24}):
    s_, n, t, rf = w24([x for x in S24 if x["Fp"] == F])
    add("AR-016", RB, f"fallback_24mm_stroke24_rib25x23/{F:g}N_zeta0.05", "worst of 10 cases: stroke mm / n g / tilt deg / rib RF", f"{s_:.1f} / {n:.2f} / {t:.2f} / {rf:.2f}", "24 / 12 / 3.0 / 1.0", s_ <= 24 and n <= 12 and t <= 3 and rf >= 1, "TP-3 fallback, 36 mm pad (CAD change, not made)")
for (F, z) in sorted({(x["Fp"], x["zeta"]) for x in Z24}, key=lambda t: (t[1], t[0])):
    s_, n, t, rf = w24([x for x in Z24 if x["Fp"] == F and x["zeta"] == z])
    add("AR-016", RB, f"fallback_24mm_zeta_rib25x23/{F:g}N_zeta{z}", "worst of 10 cases: stroke mm / n g / tilt deg / rib RF", f"{s_:.2f} / {n:.2f} / {t:.2f} / {rf:.2f}", "24 / 12 / 3.0 / 1.0", s_ <= 24 and n <= 12 and t <= 3 and rf >= 1, "TP-3 fallback; 33 N / zeta 0.02 fails on tilt 3.01 deg")
add("AR-016", RB, "fallback_foam_region_24mm", "Fp N per foot AND zeta AND usable stroke mm", "34.5-39.0 AND 0.02-0.05 AND >= 24", "model passes every tested corner; cell cap 39 N (EST scaling)", True, "4.5 N wide (+-6 %); needs a CAD pad change (30 -> 36 mm) and A-P9 re-check; strength rows not rerun on the longer pad")
add("AR-016", RB, "A-P9 static tip-over, edge toward CG, 30 mm pad (x_foot 0.3375)", "deg", 31.08, ">= 30.5", True, "current CG x 22.05 mm, z 6.56 mm")
add("AR-016", RB, "A-P9 static tip-over, edge toward CG, 36 mm pad (x_foot 0.3435)", "deg", 30.60, ">= 30.5", True, "thin (0.10 deg); pad-centre bound 29.81 deg (under 30); fallback only")
add("AR-016", RB, "A-P9 static tip-over, edge toward CG, 40 mm analysis pad (x_foot 0.3475)", "deg", 30.30, ">= 30.5", False, "inside the T-084 record range 30.22-30.52: the T-084 30.22 figure is confirmed and belongs to the 40 mm pad")
decision = "Landing: the foam must be accepted by a joint region, plateau 37.5-39.0 N per foot AND pad damping zeta 0.02-0.05 AND usable stroke >= 20 mm on the drawn 25x23-rib airframe with no CAD change (a plateau band alone is not safe: 33 N fails at zeta 0.02); the elevon pitch-use line stays FAIL on its 15 deg basis as an open item (the 20 deg basis proposal was withdrawn as a relaxation)."
json.dump(dict(task="T-098", generated="2026-11-23", decision=decision, rows=[{("pass" if k == "pass_" else k): v for k, v in r.items()} for r in rows]), open(OUT, "w"), indent=1)
print(len(rows), "rows ->", os.path.abspath(OUT))
