"""T-083 propulsion numbers for the X2216 V3 880KV on the APC 9x4.5MR (D-227).  Category: illustrative (the repo prop_a.py thrust model, EST).
python -I t083_prop.py BASIC_G [CG_MM]     prints markdown; writes nothing.
Uses redesign/qp/A/prop_a.py as edited by T-083 (Kv 880, Rm 0.089, I0 0.5, line 24.94 A EST) and the config-study arithmetic (cs_prop.py):
predicted = basic x 1.1174 + 0.032 x 1.47 (CALC-A-MASS-PRED); window with the 3 % download x 0.97; pack 2.8 Ah (RDQ 2800, O4b)."""
import sys, os, math
A = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, A); sys.dont_write_bytecode = True
import prop_a as P
NP, C = 40.7, 245.0                            # neutral point mm aft of LE, chord mm (t077p8_metrics.py)
S, CLMAX, RHO_S = 0.22, 0.75, 1.225            # A-P6 basis (claims_a1_flight.py; config study s1)
APC_MAX_RPM = 105000 / 9                       # APC MR props: max rpm = 105,000 / diameter in (apcprop.com/technical-information/rpm-limits/, read 2026-11-21) = 11,667


def pred(basic_g):
    return basic_g / 1000 * 1.1174 + 0.032 * 1.47


def metrics(mp, der=0.93, imax=None):
    imax = P.I_MOTOR_MAX if imax is None else imax
    cf, cs = P.cap_sched(16.8, mp, imax), P.cap_sched(14.92, mp, imax)
    fr, i_fr, vb_fr = P.tw_state(16.8, cf, mp, der)
    sg, i_sg, vb_sg = P.tw_state(14.92, cs, mp, der)
    win = P.window_pct(sg * 0.97)
    hov = P.hover(mp, der)
    one = P.one_motor(cf, mp, 16.8)[0]
    usable = 2.8 * 14.8 * 0.9 * 0.8
    eh = hov[4] * 180 / 3600
    etr = 1.56 * (mp / 1.37) ** 1.5
    ecl = 0.29 * (mp / 1.37)
    pc = 161 * (mp / 1.37) ** 0.58
    cruise = (usable - eh - etr - ecl) / pc * 3600
    vs = math.sqrt(2 * mp * 9.81 / (RHO_S * S * CLMAX))
    nf = P.full(16.8, cf)
    ns = P.full(14.92, cs)
    return dict(cap_fresh=cf, cap_sag=cs, tw_fresh=fr, tw_fresh_dl=fr * 0.97, tw_sag=sg, tw_sag_dl=sg * 0.97, window=win,
                hover_gf=hov[0], hover_rpm=hov[1], hover_A=hov[2], hover_vm=hov[3] / hov[2], hover_pack_W=hov[4], hover_pack_A=hov[5],
                one_motor_A=one, cruise_s=cruise, vs=vs, k13vs=1.3 * vs, full_fresh=nf, full_sag=ns,
                pack_A_fresh=4 * nf[1] * cf, pack_A_sag=4 * ns[1] * cs)


def ceiling(ok, lo=1.5, hi=2.5):
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    return lo


def derate_line(mp, key, lim):
    """lowest derate at which metric key >= lim (bisection)"""
    lo, hi = 0.5, 1.2
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if metrics(mp, mid)[key] >= lim:
            hi = mid
        else:
            lo = mid
    return hi


def report(basic, cg):
    mp = pred(basic)
    m = metrics(mp)
    out = []
    p = out.append
    p(f"# T-083 propulsion at basic {basic:.1f} g -> predicted {mp:.4f} kg (CG {cg:.2f} mm, SM {100*(NP-cg)/C:.2f} %)")
    p(f"Motor X2216 V3 880KV: Kv {P.KV}, Rm {P.RM}, I0 {P.I0}; one-motor line {P.I_MOTOR_MAX} A EST; derate {P.DER}; cant {P.CANT}")
    p("| Item | Value | Limit | Verdict |")
    p("|---|---|---|---|")

    def row(n, v, lim, ok):
        p(f"| {n} | {v} | {lim} | {'PASS' if ok else 'FAIL'} |")
    row("A-P3 window, 3 % download, derate 0.93", f"{m['window']:+.2f} %", ">= +5.0 %", m['window'] >= 5.0)
    row("A-P2 T/W fresh, no download / with download", f"{m['tw_fresh']:.3f} / {m['tw_fresh_dl']:.3f}", ">= 2.0", m['tw_fresh_dl'] >= 2.0)
    row("A-P2 T/W sag (3.73 V/cell, hot 0.97), with download", f"{m['tw_sag_dl']:.3f}", ">= 1.6", m['tw_sag_dl'] >= 1.6)
    row("Lua spin cap cap(V): fresh 16.8 V / sag 14.92 V", f"{m['cap_fresh']:.3f} / {m['cap_sag']:.3f}", "<= 1.0 (1.0 = not binding)", True)
    row("One motor saturated + three hovering, fresh, at the cap (A-P16 analogue)", f"{m['one_motor_A']:.2f} A",
        f"<= {P.I_MOTOR_MAX} A EST line (450 W / 16.8 V x 12.1/13)", m['one_motor_A'] <= P.I_MOTOR_MAX)
    nf, ns = m['full_fresh'], m['full_sag']
    row("All four at the cap, fresh: rpm / A per motor / bus V", f"{nf[0]:.0f} / {nf[1]:.2f} / {nf[4]:.2f}",
        f"rpm <= {APC_MAX_RPM:.0f} (APC MR limit); ESC 35 A / channel; motor 32 A / 30 s", nf[0] <= APC_MAX_RPM and nf[1] <= 32)
    row("All four at the cap, sag: rpm / A per motor / bus V", f"{ns[0]:.0f} / {ns[1]:.2f} / {ns[4]:.2f}", "same", ns[0] <= APC_MAX_RPM and ns[1] <= 32)
    pk = max(m['pack_A_fresh'], m['pack_A_sag'])
    row("Pack current, all four at the cap (fresh / sag)", f"{m['pack_A_fresh']:.1f} / {m['pack_A_sag']:.1f} A", "RDQ 2800 100C = 280 A", pk <= 280)
    p(f"| Connector rating needed (A-P16: 1.25 x peak) | {1.25*pk:.1f} A | XT90 (90 A, secondary sources); XT60 is 60 A momentary (secondary sources) | info |")
    row("Hover, derate 0.93: gf / rpm / A per motor / motor V / pack W / pack A",
        f"{m['hover_gf']:.0f} / {m['hover_rpm']:.0f} / {m['hover_A']:.2f} / {m['hover_vm']:.2f} / {m['hover_pack_W']:.0f} / {m['hover_pack_A']:.1f}", "-", True)
    p(f"| Hover throttle, approx. motor V / fresh bus V and / sag bus V | {m['hover_vm']/16.8:.3f} / {m['hover_vm']/14.92:.3f} | A-P2 <= 0.625 | {'PASS' if m['hover_vm']/14.92 <= 0.625 else 'FAIL'} |")
    row("Cruise before BATT_LOW, 2.8 Ah (CALC-A-ENDURANCE form)", f"{m['cruise_s']:.0f} s", ">= 204.6 s", m['cruise_s'] >= 204.6)
    row("A-P6 1.3 Vs at the predicted mass (CLmax 0.75 EST, S 0.22, rho 1.225)", f"Vs {m['vs']:.2f}, 1.3 Vs {m['k13vs']:.2f} m/s", "<= 17.0 m/s", m['k13vs'] <= 17.0)
    vsc = (17 / 1.3) ** 2 * RHO_S * S * CLMAX / (2 * 9.81)
    clreq = 2 * mp * 9.81 / (RHO_S * S * (17 / 1.3) ** 2)
    p(f"| A-P6 mass ceiling at CLmax 0.75 / CLmax needed at {mp:.3f} kg | {vsc:.4f} kg (basic {(vsc-0.047)/1.1174*1000:.0f} g) / {clreq:.3f} | - | info |")
    cw = ceiling(lambda x: metrics(x)['window'] >= 5.0)
    cfr = ceiling(lambda x: metrics(x)['tw_fresh_dl'] >= 2.0)
    csg = ceiling(lambda x: metrics(x)['tw_sag_dl'] >= 1.6)
    p(f"| Mass ceilings at derate 0.93: window 5 % / T/W fresh 2.0 dl / T/W sag 1.6 dl | {cw:.3f} / {cfr:.3f} / {csg:.3f} kg predicted | - | info |")
    dl3, dl2, dls = derate_line(mp, 'window', 5.0), derate_line(mp, 'tw_fresh_dl', 2.0), derate_line(mp, 'tw_sag_dl', 1.6)
    p(f"| Bench derate lines at {mp:.3f} kg (thrust real / APC at equal rpm that just meets): A-P3 / A-P2 fresh dl / A-P2 sag dl | {dl3:.3f} / {dl2:.3f} / {dls:.3f} | bench TP-1 | info |")
    for d in (0.88, 0.85, 0.80):
        q = metrics(mp, d)
        p(f"| Sensitivity derate {d}: window / T/W fresh dl / sag dl / cruise s | {q['window']:+.2f} % / {q['tw_fresh_dl']:.3f} / {q['tw_sag_dl']:.3f} / {q['cruise_s']:.0f} | - | info |")
    for im in (17.7, 15.0, 12.1):
        q = metrics(mp, imax=im)
        p(f"| Sensitivity one-motor line {im} A: cap fresh / window / T/W fresh dl | {q['cap_fresh']:.3f} / {q['window']:+.2f} % / {q['tw_fresh_dl']:.3f} | - | info |")
    p("")
    p("Maker cross-check (SunnySky X2216 V3 880KV table, 'APC9045' at 14.8 V, sunnyskyusa.com read 2026-11-21; the APC variant is not stated): APC 9x4.5MR model rows at the maker's rpm")
    p("| maker rpm | maker A | maker gf | model gf at that rpm | maker / model thrust | model A at that rpm |")
    p("|---|---|---|---|---|---|")
    for rpm, amp, gf in ((5836, 2.7, 300), (7450, 4.9, 500), (8600, 7.8, 700), (9696, 11.2, 900), (10117, 13.05, 1000), (10972, 16.3, 1180)):
        th, pw = P.prop(rpm)
        q = pw / (rpm * 2 * math.pi / 60)
        i = q / P.KT + P.I0
        p(f"| {rpm} | {amp} | {gf} | {th/9.807*1000:.0f} | {gf/(th/9.807*1000):.3f} | {i:.2f} |")
    n, i, th, pw = P.run(14.8)
    p(f"Model at 14.8 V motor terminal, full duty: {n:.0f} rpm, {i:.2f} A, {th/9.807*1000:.0f} gf (maker: 10,972 rpm, 16.3 A, 1,180 gf)")
    return "\n".join(out), m, mp


if __name__ == '__main__':
    basic = float(sys.argv[1])
    cg = float(sys.argv[2]) if len(sys.argv) > 2 else float('nan')
    print(report(basic, cg)[0])
