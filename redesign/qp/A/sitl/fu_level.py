"""F4 follow-up 1: level speed vs motor duty, pack state and FWD_BAT_VOLT compensation (closed form on the QP-3 plant models, no SITL).
python fu_level.py   Everything EST (a_aero.py models). Level = lift W, thrust x cos(cant) = drag at trim alpha, 4 motors, bus sags with current (R 0.030 ohm + 0.5 A avionics)."""
import math, a_aero as A
RHO = 1.225; CANT = math.radians(16.0); RP = 0.030
def drag_at(m, V):
    W = m * 9.81; lo, hi = 0.0, 20.0
    for _ in range(40):
        al = math.radians((lo + hi) / 2); F = A.airframe(V * math.cos(al), 0, V * math.sin(al), 0, 0, 0, 0, 0)[0]
        L = -F[2] * math.cos(al) + F[0] * math.sin(al); lo, hi = ((lo + hi) / 2, hi) if L < W else (lo, (lo + hi) / 2)
    al = math.radians(lo); F = A.airframe(V * math.cos(al), 0, V * math.sin(al), 0, 0, 0, 0, 0)[0]
    return -F[0] * math.cos(al) - F[2] * math.sin(al)
def thrust(d, V, vrest, hot):
    """total x-thrust (N), bus V, pack A for terminal duty d at airspeed V"""
    vb = vrest
    for _ in range(30):
        rpm, T, Q, I = A.motor(d * vb, V); ib = d * vb * I / 0.98 / vb if I > 0 else 0.0
        vb = vrest - RP * (4 * ib + 0.5)
    rpm, T, Q, I = A.motor(d * vb, V)
    return 4 * T * A.DER * A.DOWNLOAD * hot * math.cos(CANT), vb, 4 * ib + 0.5, rpm
def vlevel(m, d, vrest):
    hot = 0.97 if vrest < 15.5 else 1.0
    lo, hi = 8.0, 40.0
    for _ in range(40):
        V = (lo + hi) / 2
        lo, hi = (V, hi) if thrust(d, V, vrest, hot)[0] > drag_at(m, V) else (lo, V)
    V = (lo + hi) / 2; return V, thrust(d, V, vrest, hot)
def duty_for(m, V, vrest):
    hot = 0.97 if vrest < 15.5 else 1.0; D = drag_at(m, V); lo, hi = 0.2, 1.0
    for _ in range(40):
        d = (lo + hi) / 2; lo, hi = (d, hi) if thrust(d, V, vrest, hot)[0] < D else (lo, d)
    return (lo + hi) / 2
if __name__ == "__main__":
    for m in (1.381, 1.50):
        print("m %.3f" % m)
        for vr, nm in ((16.8, "fresh 16.8 V"), (14.92, "sag 14.92 V"), (13.2 * 4 / 4 + 0.0, "empty 13.2 V")):
            print("  %-13s duty for 17.0 m/s %.3f, for 17.6 m/s %.3f, for 18 m/s %.3f" % (nm, duty_for(m, 17.0, vr), duty_for(m, 17.6, vr), duty_for(m, 18.0, vr)))
        for d in (0.60, 0.65, 0.70, 0.75, 0.80, 0.90):
            r = []
            for vr in (16.8, 14.92):
                V, (T, vb, ip, rpm) = vlevel(m, d, vr); r.append("%s V %.1f m/s (bus %.1f V, %.0f A, %.0f W, rpm %.0f)" % ("fresh" if vr > 16 else "sag  ", V, vb, ip, vb * ip, rpm))
            print("   duty %.2f: %s | %s" % (d, r[0], r[1]))

def roc(m, d, vrest, V=17.0):
    hot = 0.97 if vrest < 15.5 else 1.0
    return (thrust(d, V, vrest, hot)[0] - drag_at(m, V)) * V / (m * 9.81)
def comp(a, vrest, vmax=16.8, vmin=13.2):
    """FWD_BAT compensation (F4 closeout 2026-11-14 reading of servos.cpp): demand and THR_MAX scaled by FWD_BAT_VOLT_MAX / resting voltage, resting clamped to [MIN, MAX]"""
    return min(1.0, a * vmax / max(vmin, min(vrest, vmax)))
def table():
    print("THR_MAX with FWD_BAT_VOLT_MAX 16.8 / MIN 13.2: duty at the ceiling, level speed (m/s) and climb at 17 m/s (m/s), 1.50 kg | 1.381 kg")
    for tm in (60, 63, 64, 66, 68, 70, 75, 80):
        a = tm / 100.0; out = []
        for m in (1.50, 1.381):
            row = []
            for vr in (16.8, 14.92, 13.2):
                d = comp(a, vr); V, _ = vlevel(m, d, vr); row.append("%.3f %.1f/%+.1f" % (d, V, roc(m, d, vr)))
            out.append(" | ".join(row))
        print("  THR_MAX %2d   fresh / 14.92 V / 13.2 V (duty V/climb): %s   ||  %s" % (tm, out[0], out[1]))
if __name__ == "__main__": table()


def loads(m=1.50):
    """C1 re-check at a new VD: same gust formula as structures_a.py (Pratt / FAR Kg), hinge moment scaling from fwd_checks.py (0.0585 N m at 18 m/s, 25 deg)"""
    G = 9.81; S, b, c = 0.22, 0.90, 0.245; W = m * G
    AR = b * b / S; a_w = math.pi * AR / (1 + math.sqrt(1 + (AR / 2) ** 2)); wl = W / S
    mu = 2 * wl / (RHO * c * a_w * G); Kg = 0.88 * mu / (5.3 + mu)
    ng = lambda V, U: 1 + Kg * RHO * U * V * a_w / (2 * wl); ns = lambda V: 0.5 * RHO * V * V * S * 0.75 / W
    print("VD  gust n (4 m/s)  stall line  pitch-rate-limited n (35 deg/s)  hinge 25 deg (N m)  servo 0.167 N m ratio  at 15 deg")
    for VD in (22.0, 23.0, 25.0, 27.5):
        h = 0.0585 * (VD / 18.0) ** 2
        print("%4.1f  %.2f  %.2f  %.2f  %.4f  %.2f  %.2f" % (VD, ng(VD, 4), ns(VD), 1 + VD * math.radians(35) / G, h, 0.167 / h, 0.167 / (h * 15 / 25)))
    for n in (3.4,):
        k = (n - 1) / (ng(1.0, 4) - 1); print("VD at which the 4 m/s gust reaches the limit n %.1f: %.1f m/s" % (n, k))
if __name__ == "__main__": loads()
