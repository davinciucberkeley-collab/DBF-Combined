"""Option 1e: SunnySky X2216 880KV long shaft (RMRC page read 2026-11-21: Kv 880, Rm 117 mOhm, I0 0.5 A/10 V, 72 g, max continuous 320 W, 2-4S, ESC 30 A)
on the same APC 9x4.5MR (repo APC PER3 rows), repo prop_a model; current line = 320 W / 16.8 V x (12.1/13) = 17.7 A (A-P16 analogue, EST: the page gives power, not current)."""
import sys, math
sys.path.insert(0, r"C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/docs/audits/2026-11-21-config-study-data")
import cs_prop as S
P = S.P
def setm(kv, rm, i0): P.KV, P.RM, P.I0 = kv, rm, i0; P.KT = 60/(2*math.pi*kv)
IM = 320/16.8*12.1/13
print("| Case | basic g | pred kg | CG mm | SM % | window % (dl) | T/W fresh (no dl / dl) | T/W sag (dl) | fresh cap | one motor A | hover A | cruise s | 1.3 Vs | full fresh rpm / A | full sag rpm / A |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for tag, b, cg, im, der in (("X2216-880 at p8 mass + 28 g motors", 1598.4+28, (1598.4*30.17+28*(-100))/(1598.4+28), IM, 0.93),
                            ("same, derate 0.88", 1598.4+28, (1598.4*30.17+28*(-100))/(1598.4+28), IM, 0.88),
                            ("same, current line 15 A", 1598.4+28, (1598.4*30.17+28*(-100))/(1598.4+28), 15.0, 0.93),
                            ("X2216-880 + option 3 recovery (-42.8 g)", 1598.4+28-42.8, (1598.4*30.17+28*(-100))/(1598.4+28) - 3.04*1598.4/(1598.4+28-42.8), IM, 0.93),
                            ("X2216-880 at p7 mass (reference)", 1481.1+28, (1481.1*23.39+28*(-100))/(1481.1+28), IM, 0.93)):
    setm(880.0, 0.117, 0.5)
    mp = S.pred(b); m = S.metrics(mp, imax=im, der=der)
    setm(880.0, 0.117, 0.5)
    n, i, th, pw, vb = P.full(16.8, m['cap_fresh']); n2, i2, th2, pw2, vb2 = P.full(14.92, m['cap_sag'])
    print(f"| {tag} | {b:.1f} | {mp:.3f} | {cg:.2f} | {100*(S.NP-cg)/S.C:.2f} | {m['window']:+.2f} | {m['tw_fresh']:.3f} / {m['tw_fresh_dl']:.3f} | {m['tw_sag_dl']:.3f} | {m['cap_fresh']:.3f} | {m['one_motor_A']:.2f} | {m['hover_A']:.2f} | {m['cruise_s']:.0f} | {m['k13vs']:.2f} | {n:.0f} / {i:.1f} | {n2:.0f} / {i2:.1f} |")
for ceil_tag, fn in (("window 5 %", lambda mm: (setm(880.0, 0.117, 0.5), S.metrics(mm, imax=IM))[1]['window'] >= 5.0),
                     ("fresh T/W 2.0 with dl", lambda mm: (setm(880.0, 0.117, 0.5), S.metrics(mm, imax=IM))[1]['tw_fresh_dl'] >= 2.0)):
    c = S.ceiling(fn, 1.6, 2.3); print(f"X2216-880 ceiling {ceil_tag}: predicted {c:.3f} kg = basic {(c-0.047)/1.1174*1000:.0f} g")
