"""T-074 check 3 (side check, s7 item 2 'Q_M_BAT_CURR_MAX re-check'): pack current at full duty on the sag state and the duty a 41 A limit would impose.
Category: illustrative (prop_a.py motor model, EST).  Pack current = 4 x duty x I_motor / 0.98 (the a_plant.py / run_fwd.py ib convention).  python -I batt_curr_check.py"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
import prop_a as pa
def ipack(vr, u): n, i, th, pw, vb = pa.full(vr, u); return 4*u*i/0.98, th, i
for vr in (14.92, 16.8):
    for u in (0.90, 1.0):
        ip, th, i = ipack(vr, u); print(f"V_rest {vr} duty {u:.2f}: pack {ip:.1f} A, motor {i:.2f} A, thrust {th:.2f} N")
for lim in (41.0, 43.9, 45.0):
    lo, hi = 0.5, 1.0
    for _ in range(40):
        m = (lo+hi)/2; lo, hi = (m, hi) if ipack(14.92, m)[0] <= lim else (lo, m)
    th = pa.full(14.92, lo)[2]; th1 = pa.full(14.92, 1.0)[2]
    print(f"limit {lim} A at sag: equivalent duty {lo:.3f}, thrust {th:.2f} N vs {th1:.2f} N at duty 1.0 ({100*(th/th1-1):+.1f} %)")
    for m_ in (1.64,):
        tw = 4*th*0.97*pa.DER*math.cos(math.radians(pa.CANT))/(m_*9.807)
        print(f"   T/W sag {tw:.3f}, window +-{pa.window_pct(tw):.1f} %, +-5 % mass {tw*m_*0.8/(1.33*1.05/0.95)*1000:.0f} g")
