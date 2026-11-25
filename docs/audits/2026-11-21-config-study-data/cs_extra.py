import sys, math, copy
sys.path.insert(0, r"C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/docs/audits/2026-11-21-config-study-data")
import cs_prop as S
P = S.P
P.KV, P.RM, P.I0 = 880.0, 0.117, 0.5; P.KT = 60/(2*math.pi*880.0)
IM = 320/16.8*12.1/13
b = 1598.4 + 28 - 23.8; cg = (1598.4*30.17 + 28*(-100))/(1598.4+28) - 2.4*1598.4/b
mp = S.pred(b); P.KV, P.RM, P.I0 = 880.0, 0.117, 0.5; P.KT = 60/(2*math.pi*880.0); m = S.metrics(mp, imax=IM)
print(f"1-ii + coupon: basic {b:.1f} pred {mp:.3f} CG {cg:.2f} SM {100*(S.NP-cg)/S.C:.2f} window {m['window']:+.2f} TW fresh {m['tw_fresh']:.3f}/{m['tw_fresh_dl']:.3f} sag {m['tw_sag_dl']:.3f} cruise {m['cruise_s']:.0f} 1.3Vs {m['k13vs']:.2f}")
import cs_bom as C
B = C.B
r = C.drop(C.common_reads(copy.deepcopy(C.BASE)), 'R15'); B.SHIP.pop('Carbonwebshop', None); B.rows[:] = r; t = B.totals()
print(f"3 alone rib 14x12: total {t['total']:.2f} spend {t['spend']:.2f} reserve {t['reserve']:.2f}; held 327.43 -> {t['spend']+327.43:.2f}")
B.SHIP['Carbonwebshop'] = 25.0
r = C.drop(C.common_reads(copy.deepcopy(C.BASE)), 'R15'); C.setu(r, 'R02', qty=2); B.SHIP.pop('Carbonwebshop', None); B.rows[:] = r; t = B.totals()
print(f"3 alone rib 16x14: total {t['total']:.2f} held -> {t['spend']+327.43:.2f}")
