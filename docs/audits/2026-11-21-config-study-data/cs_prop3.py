"""Option 1d: 10 in prop by static similarity scaling of the APC 9x4.5MR rows (T x (10/9)^4, P x (10/9)^5; EST: APC 10x4.5MR PER3 file not readable 2026-11-21, Cloudflare block).
Sanity check: MN2212 KV780 at the 12.1 A line vs D-217 ('10x4.5 at most +0.8 %')."""
import sys, math
sys.path.insert(0, r"C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/docs/audits/2026-11-21-config-study-data")
import cs_prop as S
P = S.P
T9 = dict(P.T)
def setp(D_in):
    k = D_in/9.0; P.D = D_in*0.0254
    P.T = {n: (t*k**4, p*k**5) for n, (t, p) in T9.items()}
def setm(kv, rm, i0): P.KV, P.RM, P.I0 = kv, rm, i0; P.KT = 60/(2*math.pi*kv)
print("| Case | basic g | pred kg | CG mm | SM % | window % (dl) | T/W fresh (no dl / dl) | T/W sag (dl) | fresh cap | one motor A | hover A | cruise s | 1.3 Vs | full-throttle fresh rpm / A |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
cases = [("MN2212 KV780, 9 in (check = p8)", 780, .173, .5, 12.1, 9, 0, 0),
         ("MN2212 KV780, 10 in scaled (D-217 check)", 780, .173, .5, 12.1, 10, 4*4.0, 0),
         ("MN3110 KV780, 10 in scaled, p8 + motors/cups/props/landing", 780, .071, .4, 26*12.1/13, 10, 4*35+20+4*4.0+30, 1),
         ("same + option 3 recovery (-42.8 g)", 780, .071, .4, 26*12.1/13, 10, 4*35+20+4*4.0+30-42.8, 2)]
for tag, kv, rm, i0, imax, D, dm, cgmode in cases:
    setm(kv, rm, i0); setp(D)
    b = 1598.4 + dm
    mom = 0.0
    if cgmode: mom = 140*(-100.0) + 20*(-90.0) + 16*(-126.0) + 30*150.0
    cg = (1598.4*30.17 + mom)/b
    if cgmode == 2: cg -= (1.06 + 1.98)*1598.4/b
    mp = S.pred(b); m = S.metrics(mp, imax=imax)
    setm(kv, rm, i0); setp(D)
    n, i, th, pw, vb = P.full(16.8, m['cap_fresh'])
    print(f"| {tag} | {b:.1f} | {mp:.3f} | {cg:.2f} | {100*(S.NP-cg)/S.C:.2f} | {m['window']:+.2f} | {m['tw_fresh']:.3f} / {m['tw_fresh_dl']:.3f} | {m['tw_sag_dl']:.3f} | {m['cap_fresh']:.3f} | {m['one_motor_A']:.2f} | {m['hover_A']:.2f} | {m['cruise_s']:.0f} | {m['k13vs']:.2f} | {n:.0f} / {i:.1f} |")
