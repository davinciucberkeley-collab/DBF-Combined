"""Option 1b/1c: MN3110 (KV780 / KV700) on the same APC 9x4.5MR, repo prop_a model with motor constants from the T-Motor MN3110 page (read 2026-11-21)."""
import sys, math
sys.path.insert(0, r"C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/mechanism/out"); sys.path.insert(0, r"C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/docs/audits/2026-11-21-config-study-data")
import cs_prop as S
P = S.P
def setm(kv, rm, i0): P.KV, P.RM, P.I0 = kv, rm, i0; P.KT = 60/(2*math.pi*kv)
print("| State | basic g | pred kg | CG mm | SM % | window % (dl) | T/W fresh (no dl / dl) | T/W sag (dl) | fresh cap | one motor A | hover A/motor | cruise s (2.8 Ah) | 1.3 Vs m/s |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for tag, kv, rm, i0, imax, dm in (("1b MN3110 KV780 + APC 9x4.5MR", 780.0, 0.071, 0.4, 26*12.1/13, 4*(100-65)), ("1c MN3110 KV700 + APC 9x4.5MR", 700.0, 0.092, 0.3, 21*12.1/13, 4*(99-65))):
    for sub, extra, cgx in (("p8 + motors + cups 20 g + landing growth 30 g", 50, None), ("same + option 3 recovery (-42.8 g)", 50-42.8, None)):
        b = 1598.4 + dm + extra
        mom = dm*(-100.0) + 20*(-90.0) + 30*150.0 + (0 if 'option 3' not in sub else (-23.2*(1.06/23.2*1598.4/1.0)*0 ))
        cg = (1598.4*30.17 + mom)/b
        if 'option 3' in sub: cg -= (1.06 + 1.98) * 1598.4 / b
        setm(kv, rm, i0)
        mp = S.pred(b); m = S.metrics(mp, imax=imax)
        n, i, th, pw, vb = P.full(16.8, m['cap_fresh'])
        print(f"| {tag}: {sub} | {b:.1f} | {mp:.3f} | {cg:.2f} | {100*(S.NP-cg)/S.C:.2f} | {m['window']:+.2f} | {m['tw_fresh']:.3f} / {m['tw_fresh_dl']:.3f} | {m['tw_sag_dl']:.3f} | {m['cap_fresh']:.3f} | {m['one_motor_A']:.2f} | {m['hover_A']:.2f} | {m['cruise_s']:.0f} | {m['k13vs']:.2f} |  full-throttle fresh {n:.0f} rpm {i:.1f} A/motor")
