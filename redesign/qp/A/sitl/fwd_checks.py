"""Closed-form checks on the QP-3 forward-flight model (no SITL): Vs, trim elevon, roll rate, hinge moment, Cn_beta. python fwd_checks.py"""
import math, a_aero as A
RHO = 1.225
def trim(m, V, d_el=0.0):
    W = m * 9.81; lo, hi = 0.0, 15.0
    for _ in range(40):
        al = math.radians((lo + hi) / 2); F = A.airframe(V * math.cos(al), 0, V * math.sin(al), 0, 0, 0, d_el, d_el)[0]
        L = -F[2] * math.cos(al) + F[0] * math.sin(al); lo, hi = ((lo + hi) / 2, hi) if L < W else (lo, (lo + hi) / 2)
    return math.radians(lo)
def vs(m):
    W = m * 9.81
    def lmax(V): return max((-A.airframe(V * math.cos(math.radians(a)), 0, V * math.sin(math.radians(a)), 0, 0, 0, 0, 0)[0][2] * math.cos(math.radians(a))
                            + A.airframe(V * math.cos(math.radians(a)), 0, V * math.sin(math.radians(a)), 0, 0, 0, 0, 0)[0][0] * math.sin(math.radians(a))) for a in [x * 0.5 for x in range(0, 50)])
    lo, hi = 5.0, 30.0
    for _ in range(40):
        mid = (lo + hi) / 2; lo, hi = (mid, hi) if lmax(mid) < W else (lo, mid)
    return lo
for m in (1.381, 1.50):
    print("m %.3f: model Vs %.2f (MISSION %.2f, density 1.225 vs 1.20 explains +1.2 %%), 1.3 Vs %.2f" % (m, vs(m), 11.70 * math.sqrt(m / 1.381), 1.3 * vs(m)))
    for V in (15.0, 17.0, 18.0):
        al = trim(m, V)
        # elevon needed for Cm = 0 at that alpha (both elevons, deg, TE down +)
        lo, hi = -0.43, 0.43
        for _ in range(40):
            d = (lo + hi) / 2; T = A.airframe(V * math.cos(al), 0, V * math.sin(al), 0, 0, 0, d, d)[1][1]
            lo, hi = (d, hi) if T > 0 else (lo, d)
        print("   V %.0f: alpha %.1f deg, trim elevon %.1f deg (TE %s), hinge moment at that deflection %.4f N m per elevon"
              % (V, math.degrees(al), abs(math.degrees(d)), "up" if d < 0 else "down", A.airframe(V * math.cos(al), 0, V * math.sin(al), 0, 0, 0, d, d)[2]["hinge"]))
V = 17.0; qS = 0.5 * RHO * V * V * A.S_W
for da in (5.0, 8.7, 15.0):
    dr = math.radians(da); Mx = A.EL_Y * qS * A.CLD * 0.5 * dr * 2
    rate = Mx / (-A.CLP * qS * A.B_W * A.B_W / (2 * V))
    print("roll at 17 m/s, differential +-%.1f deg: moment %.2f N m, steady rate %.0f deg/s (requirement >= 90 deg/s, A-P11)" % (da, Mx, math.degrees(rate)))
print("Cn_beta (fins, wing neglected) = %.3f /rad (requirement >= 0.03, A-P15)" % (A.CLAF * A.FIN_S * abs(A.FIN_X) / (A.S_W * A.B_W)))
V = 18.0; al = trim(1.5, V)
print("peak hinge moment at 18 m/s, 25 deg, alpha %.0f deg: %.4f N m vs servo 0.167-0.235 N m (ES3352HV 1.7-2.4 kgf-cm, U); ratio %.1f" %
      (math.degrees(al), A.airframe(V * math.cos(al), 0, V * math.sin(al), 0, 0, 0, math.radians(25), math.radians(25))[2]["hinge"],
       0.167 / A.airframe(V * math.cos(al), 0, V * math.sin(al), 0, 0, 0, math.radians(25), math.radians(25))[2]["hinge"]))
print("elevon area both %.4f m2 (cf/c %.2f, y %.2f-%.2f m each side), CL_delta %.3f /rad, tau %.2f; stops +-%.0f deg, rate %.0f deg/s" % (A.EL_S, A.EL_CF, A.EL_Y0, A.EL_Y1, A.CLD, A.EL_TAU, math.degrees(A.EL_MAX), math.degrees(A.EL_RATE)))
