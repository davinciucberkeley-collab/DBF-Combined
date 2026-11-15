"""F1 cost re-check 2026-11-14 (D-180): (1) 12 AWG pack leads (CNHL 6000 EC5 listing conflict) against the wire-heating
rules, E2 mission profile, 80 A limiter punches; (2) path resistance / drop with 12 AWG leads; (3) cap leg length 20 -> 22 mm;
(4) 9 caps (2 per ESC + 1 spare) against the CL-F1-CAP-* limits. Imports power.py (reads params + claims), writes nothing.
Run: python -I redesign/team/F1/cost_recheck_2026-11-14.py"""
import importlib.util, json, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pw", HERE / "power.py")
pw = importlib.util.module_from_spec(spec); spec.loader.exec_module(pw)
kit = pw.kit
def calc(cid):
    out = kit._run(cid); return out, kit.nodes[cid]["input_values"]
P = lambda k: kit.value("P:" + k)
lim_wire, lim_short, lim_pack = P("electrical.wire_temp_rise_max_c"), P("electrical.wire_temp_rise_short_max_c"), P("electrical.pack_lead_rise_max_c")
print(f"rules: wire_temp_rise_max_c {lim_wire}, short {lim_short}, pack_lead_rise_max_c {lim_pack}; ambient {P('env.ambient_design_c')}")
out, iv = calc("CALC-F1-PACKLEAD")
ta = max(iv["amb"]); w = {a: pw.wire_props(a, iv["od"]) for a in (10, 12)}
c = (iv["cool"][0], iv["cool"][2], iv["cool"][3])
prof = iv["profile"]
ilim = P("propulsion.current_max_per_motor_a") * P("propulsion.n_motors")
print("profile", [(n, t, round(i, 1)) for n, t, i in prof], "limiter total A", ilim, "peak design", iv["ipeak"])
for awg in (10, 12):
    steady = pw.steady_rise(iv["i_cont"], w[awg], ta, c)
    mission = pw.profile_peak(pw._segments(prof, False, 0, 0, 1.0), w[awg], ta, c)
    punch80 = pw.profile_peak(pw._segments(prof, True, iv["punch"][1], ilim, 1.0), w[awg], ta, c)
    punch120 = pw.profile_peak(pw._segments(prof, True, iv["punch"][1], iv["ipeak"], 1.0), w[awg], ta, c)
    print(f"AWG {awg}: steady@I_cont {steady:.1f} K | mission peak {mission:.1f} K (<= pack {lim_pack}: {mission<=lim_pack}; <= wire {lim_wire}: {mission<=lim_wire}) | "
          f"80 A limiter punch {punch80:.1f} K (<= short {lim_short}: {punch80<=lim_short}) | 120 A design punch {punch120:.1f} K")
# conductor temperature at the 44 degC ceiling
print("conductor at ambient ceiling", P("env.ambient_ceiling_c"), "-> mission 12 AWG", round(P("env.ambient_ceiling_c") + pw.profile_peak(pw._segments(prof, False, 0, 0, 1.0), w[12], ta, c), 1), "degC")
# path resistance
o2, iv2 = calc("CALC-F1-WIRES")
print("path R (10 AWG pigtails + 2 bullets):", round(o2["r_ext_mohm"], 3), "mOhm; drop cont", round(o2["drop_cont_pct"], 3), "% peak", round(o2["drop_peak_pct"], 3), "%; r_hv", round(o2["r_hv_mohm"], 3))
r_b, n_j, l_pig = iv2["hv"]
loop12 = 2 * l_pig * w[12]["r20"] * (1 + pw.ALPHA * (ta + 25.6 - 20)) * 1e3
d12_keepbullets = loop12 - 2 * l_pig * w[10]["r20"] * (1 + pw.ALPHA * 40) * 1e3
rext12 = o2["r_ext_mohm"] + d12_keepbullets
print(f"12 AWG 0.10 m loop {loop12:.3f} mOhm hot; r_ext if bullets kept {rext12:.3f} mOhm; if pack leads solder direct to the AS150U (no bullets) {rext12 - n_j*r_b*1e3:.3f} mOhm")
for lab, r in (("bullets kept", rext12), ("no bullets", rext12 - n_j * r_b * 1e3)):
    dr = (r - o2["r_ext_mohm"])
    print(f"   {lab}: drop at limiter {o2['drop_peak_pct'] + 100 * ilim * dr * 1e-3 / iv2['v']:.3f} % (allow CL-E1-DROP-ALLOW {kit.value('CL-E1-DROP-ALLOW') if 'CL-E1-DROP-ALLOW' in kit.nodes else '-'}), r_ext allow {kit.value('CL-E1-REXT-ALLOW') if 'CL-E1-REXT-ALLOW' in kit.nodes else '-'}")
# cap legs
oc, ivc = calc("CALC-F1-ESC-CAP")
caps = ivc["caps"][1]; name, C, esr, irat, vrat, tcat, mg, kf, kt = caps
rho = pw.RHO_CU
for dia in (0.5e-3, 0.6e-3):
    for l in (0.020, 0.0213, 0.022):
        rleg = 2 * rho * l / (math.pi / 4 * dia ** 2)
        lleg = ivc["lp"] * l                          # loop L' of ASM-F1-LEAD-L (5 mm spacing, conservative for a can's own leg pair)
        for n in (1, 3):
            dv_r = oc["pzj3_vpp_v"] * 0 + 30.1 * (rleg / n)       # extra V_pp from leg resistance at I_ph = 30.1 A (limiter) EST
            dspike = max(P("propulsion.current_max_per_motor_a"), 40.0) * (math.sqrt((ivc["l_esc"] * ivc["lp"] + lleg / n) / (3 * C)) - math.sqrt(ivc["l_esc"] * ivc["lp"] / (3 * C)))
            print(f"leg dia {dia*1e3:.1f} mm l {l*1e3:.1f} mm n_parallel {n}: R_pair {rleg*1e3:.2f} mOhm, L_loop {lleg*1e9:.1f} nH -> +{dv_r:.3f} V p-p, +{dspike*1e3:.1f} mV spike (V_peak {oc['pzj3_v_peak_v']:.2f} -> {oc['pzj3_v_peak_v']+dspike+dv_r/2:.3f} V, limit 21)") if n == 3 else None
print("3 cans: ", {k: round(oc[f'pzj3_{k}'], 3) for k in ('i_hover_per_can_a','i_rms_tau_a','i_trans_per_can_a','t_lim_c','vpp_v','v_peak_v')}, "limits: rating", round(oc["pzj3_rating_a"], 3), "trans 7.28, T 90, vpp 1.0, vpeak 21")
print("2 cans: ", {k: round(oc[f'pzj2_{k}'], 3) for k in ('i_hover_per_can_a','i_rms_tau_a','i_trans_per_can_a','t_lim_c','vpp_v','v_peak_v')})
# end conduction credit for a short 12 AWG run (steady at the hover current held for ever, ends at pack-tab rise 15.3 K, both ends: conservative)
k_cu = P("power.k_cu_w_mk")
for l in (0.05, 0.09, 0.10, 0.15):
    print(f"12 AWG {l*1000:.0f} mm, ends +15.3 K: steady mid-length rise {pw.fin_mid_rise(iv['i_cont'], w[12], ta, c, l, 15.3, k_cu):.1f} K above ambient (incl. the 15.3 K end offset); 10 AWG {pw.fin_mid_rise(iv['i_cont'], w[10], ta, c, l, 15.3, k_cu):.1f} K")
