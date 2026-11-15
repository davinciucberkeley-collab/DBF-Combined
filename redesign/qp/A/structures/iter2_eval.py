import sys, math, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, fe_a
FIN = (5e-3, 1e-3, 110e9, 10e-3, 0.055)
RPM_HOVER = (6018.0, 6272.0, 7151.0)      # 1.381 kg, 1.50 kg (prop_a.py), 8 m/s lean 1.3 W
RPM_CRUISE = (7300.0, 7450.0, 7600.0)    # SITL cruise band (BOARD s1 item 2, fu_level.py); the 8,900-10,500 EST band is withdrawn
RPM_SWEEP = list(range(6000, 10501, 250))    # D-185: forced response swept over the full rpm range incl. cruise 7,300-7,600
F_HOV1 = (RPM_HOVER[0]/60, RPM_HOVER[2]/60); F_CR1 = (RPM_CRUISE[0]/60, RPM_CRUISE[2]/60)
BANDS = [("hover 1P", RPM_HOVER[0]/60, RPM_HOVER[2]/60), ("hover 2P", RPM_HOVER[0]/30, RPM_HOVER[2]/30),
         ("cruise 1P", RPM_CRUISE[0]/60, RPM_CRUISE[2]/60), ("cruise 2P", RPM_CRUISE[0]/30, RPM_CRUISE[2]/30)]
def sep(f):
    """worst separation (fraction) of f to any band edge; negative if inside a band"""
    worst = 9
    for n, lo, hi in BANDS:
        if lo <= f <= hi: s = 0.0
        elif f < lo: s = (lo-f)/lo
        else: s = (f-hi)/hi
        # 20 % rule against the band: f <= lo/1.2 or f >= 1.2 hi  <=> (lo-f)/lo >= 1-1/1.2 = 0.1667 or (f-hi)/hi >= 0.2
        worst = min(worst, s)
    return worst
def ok(f):
    return all((f <= lo/1.2) or (f >= 1.2*hi) for n, lo, hi in BANDS)
def forced(F, res, rpm, thrust, U=1e-6, zeta=0.01):
    idx = F._idx; om = rpm/60*2*math.pi
    mot = [m for m in idx if (m.startswith("m+") or m.startswith("m-")) and ">" not in m]
    imu = idx["s+0.000"]; out = {}
    for tag, mult, fm in (("1P", 1, U*om**2), ("2P", 2, 0.05*thrust)):
        w = mult*om; a = 0.0
        for (f, e, v, cx, cy) in res:
            wi = 2*math.pi*f
            gam = fm*(sum(abs(v[6*idx[m]+1])+abs(v[6*idx[m]+2]) for m in mot) if tag == "1P" else sum(abs(v[6*idx[m]]) for m in mot))
            h = 1/math.sqrt((wi*wi-w*w)**2+(2*zeta*wi*w)**2)
            a += w*w*gam*h*sum(abs(v[6*imu+q]) for q in range(3))
        out[tag] = a
    return out
STRONG = 0.5   # D-185 (BOARD s3): 'strongly coupled' = motor coupling >= 0.5
LO_LIM = min(b[1] for b in BANDS)/1.2; HI_LIM = 1.2*max(b[2] for b in BANDS)   # separation limits from the four rotor bands
def evaluate(label, thr=STRONG, **kw):
    kw.setdefault("fin_strip", FIN)
    row = {"label": label}; viol = []; low = []; acc = {}
    for k in ("kd", "nom", "hi"):
        F, info = fe_a.build(k, **kw); res = F.solve(100)
        for (f, e, v, cx, cy) in res:
            if (cx >= thr or cy >= thr) and f > 2 and not ok(f): viol.append((k, round(f), round(cx, 1), round(cy, 1)))
        low.append((k, [round(f) for (f, e, v, cx, cy) in res if f > 2][:1]))
        worst = 0
        for rpm, th in [(r, 5.4 if r <= 7200 else 0.6) for r in RPM_SWEEP] + [(6272, 3.94), (RPM_HOVER[0], 3.8), (RPM_HOVER[2], 5.4), (7300, 0.45), (7450, 0.49), (7600, 0.52)]:   # QP-4 D-185 sweep (thrust per rotor EST: hover 3.8-5.4 N, cruise ~0.5 N)
            o = forced(F, res, rpm, th); worst = max(worst, o["1P"], o["2P"])
        acc[k] = worst
        row[k] = (F, res, info)
    row["viol"] = viol; row["acc"] = acc; row["low"] = low
    return row
if __name__ == "__main__":
    base = dict(spar_tube=(12e-3, 10e-3), rib_tube=(10e-3, 8e-3), arm_tube=(12e-3, 10e-3))
    for lab, kw in (("single 8x6", dict(bridge_cfg="single", bridge_tube=(8e-3, 6e-3))),
                    ("single 10x8", dict(bridge_cfg="single", bridge_tube=(10e-3, 8e-3))),
                    ("V 8x6 yv.18", dict(bridge_cfg="V", bridge_tube=(8e-3, 6e-3), bridge_yv=0.18)),
                    ("V 10x8 yv.18", dict(bridge_cfg="V", bridge_tube=(10e-3, 8e-3), bridge_yv=0.18)),
                    ("V 10x8 yv.12", dict(bridge_cfg="V", bridge_tube=(10e-3, 8e-3), bridge_yv=0.12))):
        r = evaluate(lab, **base, **kw)
        print(lab, "viol", r["viol"], "acc", {k: round(v, 1) for k, v in r["acc"].items()}, r["low"])
