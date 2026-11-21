"""Config study 2026-11-21: propulsion / mass / CG / window / endurance / stall per option.  Uses redesign/qp/A/prop_a.py unchanged
(imported; motor constants swapped in memory for the KV920 variant).  python -I cs_prop.py"""
import sys, math, importlib
A = r"C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A"
sys.path.insert(0, A); sys.dont_write_bytecode = True
import prop_a as P

NP, C = 40.7, 245.0                       # neutral point mm aft of LE, chord mm (t077p8_metrics.py)
def pred(basic_g): return basic_g / 1000 * 1.1174 + 0.032 * 1.47      # CALC-A-MASS-PRED form
def metrics(mp, imax=12.1, der=0.93, kv=None, rm=None):
    if kv:
        P.KV, P.RM = kv, rm; P.KT = 60 / (2 * math.pi * kv)
    cf, cs = P.cap_sched(16.8, mp, imax), P.cap_sched(14.92, mp, imax)
    fr = P.tw_state(16.8, cf, mp, der)[0]; sg = P.tw_state(14.92, cs, mp, der)[0]
    fr_unc = P.tw_state(16.8, 1.0, mp, der)[0]
    win = P.window_pct(sg * 0.97)
    hov = P.hover(mp, der)                # (gf, rpm, A/motor, motor W, pack W x1.10, pack A)
    one = P.one_motor(cf, mp, 16.8)[0]
    usable = 2.8 * 14.8 * 0.9 * 0.8      # O4b pack 2,800 mAh (params-A.json still has 2.3 Ah: stale)
    eh = hov[4] * 180 / 3600; etr = 1.56 * (mp / 1.37) ** 1.5; ecl = 0.29 * (mp / 1.37); pc = 161 * (mp / 1.37) ** 0.58
    cruise = (usable - eh - etr - ecl) / pc * 3600
    vs = math.sqrt(2 * mp * 9.81 / (1.225 * 0.22 * 0.75))
    out = dict(cap_fresh=cf, cap_sag=cs, tw_fresh=fr, tw_fresh_dl=fr * 0.97, tw_sag_dl=sg * 0.97, tw_fresh_uncapped=fr_unc, window=win,
               hover_A=hov[2], hover_rpm=hov[1], one_motor_A=one, pack_hover_W=hov[4], cruise_s=cruise, k13vs=1.3 * vs)
    if kv:
        importlib.reload(P)
    return out
def ceiling(fn_ok, lo=1.5, hi=2.3):
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        if fn_ok(mid): lo = mid
        else: hi = mid
    return lo
def show(tag, basic, cg, **kw):
    mp = pred(basic); m = metrics(mp, **kw)
    print(f"| {tag} | {basic:.1f} | {mp:.3f} | {cg:.2f} | {100*(NP-cg)/C:.2f} | {m['window']:+.2f} | {m['tw_fresh']:.3f} / {m['tw_fresh_dl']:.3f} | {m['tw_sag_dl']:.3f} | "
          f"{m['cap_fresh']:.3f} | {m['one_motor_A']:.2f} | {m['hover_A']:.2f} | {m['cruise_s']:.0f} | {m['k13vs']:.2f} |")
    return m

if __name__ == '__main__':
    print("| State | basic g | pred kg | CG mm | SM % | window % (dl) | T/W fresh (no dl / dl) | T/W sag (dl) | fresh cap | one motor A | hover A/motor | cruise s (2.8 Ah) | 1.3 Vs m/s |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    show("O4b p8 tallied (MN2212 KV780, 12.1 A)", 1598.4, 30.17)
    show("O4b p7 tallied (no passing landing path)", 1481.1, 23.39)
    # Option 1a: MN2212 V2.0 KV920 (T-Motor page: Rm 142 mOhm, 15 A max continuous 180 s, 65 g with cables, 2-4S); A-P16 line rescaled 12.1 x 15/13 = 13.96 A
    I920 = 12.1 * 15 / 13
    show("1a KV920 at p8 mass", 1598.4, 30.17, imax=I920, kv=920.0, rm=0.142)
    show("1a KV920 at p8 mass, derate 0.90", 1598.4, 30.17, imax=I920, kv=920.0, rm=0.142, der=0.90)
    show("1a KV920 at p7 mass", 1481.1, 23.39, imax=I920, kv=920.0, rm=0.142)
    # mass ceilings (window >= 5 % with download, fresh T/W >= 2.0 no download) at derate 0.93
    for tag, kw in (("KV780", {}), ("KV920", dict(imax=I920, kv=920.0, rm=0.142))):
        cw = ceiling(lambda m: metrics(m, **kw)['window'] >= 5.0)
        cf = ceiling(lambda m: metrics(m, **kw)['tw_fresh'] >= 2.0)
        cfd = ceiling(lambda m: metrics(m, **kw)['tw_fresh_dl'] >= 2.0)
        print(f"ceiling {tag}: window 5 % -> {cw:.4f} kg pred (basic {(cw-0.047)/1.1174*1000:.1f} g); fresh T/W 2.0 no dl -> {cf:.4f} kg; with dl -> {cfd:.4f} kg")
    vs_ceiling = (17 / 1.3) ** 2 * 1.225 * 0.22 * 0.75 / (2 * 9.81)
    print(f"A-P6 (1.3 Vs <= 17 m/s, CLmax 0.75 EST, S 0.22) mass ceiling {vs_ceiling:.4f} kg")
