"""Concept A forward-flight aerodynamics and APC 9x4.5MR / MN2212 / pack model for a_plant.py (QP-3 SITL-FLIGHT). Pure stdlib.
Every constant is EST unless a source is named. Body frame FRD in cruise attitude: x nose (chord), y right wing, z belly. u, v, w = body velocity relative to the air.
Self test: python a_aero.py  (prints Vs, L/D at 17 m/s, trim, prop thrust and power vs airspeed)."""
import math, bisect
import a_apc_data as D

RHO = 1.225
# ---------------- planform (SIZING-A / sizing_a.py: S 0.22, b 0.90, c 0.245; fins 2 x 0.36 x 0.12)
S_W, B_W, C_W = 0.22, 0.90, 0.245
AR = B_W ** 2 / S_W
CLA = 2 * math.pi * AR / (2 + math.sqrt(4 + AR ** 2))     # finite-wing lift slope per rad (Helmbold), EST: about 3.7
CLMAX = 0.75                                               # MISSION.md s1 (EST); Vs 12.19 m/s at 1.50 kg
ASTALL, WSTALL = math.radians(17.0), 0.03                  # attached-to-plate blend centre and width, rad (EST, tuned so peak CL = CLMAX)
PCLIP = 12                                                  # soft clip sharpness of the attached CL curve
CDW = 2.0                                                  # plate Cd for the post-stall branch (sizing 2.0-2.05; identical to the hover plant)
# CD0 calibrated to MISSION.md s1: L/D 7.19 at CL 0.352 (1.37 kg, 17 m/s) with e = 0.8
E_OSW = 0.8
CD0 = 1.87 / (0.5 * 1.20 * 17 ** 2 * S_W) - 0.352 ** 2 / (math.pi * E_OSW * AR)
SM = 0.065                                                 # static margin MASS-GATE: AC 0.065 c behind the CG
CM0 = 0.015                                                # reflexed flying-wing section Cm about the AC (EST, S5010-like); trim needs a little up elevon
CMQ, CLP = -1.0, -0.30                                     # pitch and roll damping, nondimensional (EST: thin-airfoil -pi/2 reduced for AR; Helmbold-type Clp)
CLB = -0.04                                                # dihedral effect per rad (EST)
# ---------------- elevons (EST, not in REQUIREMENTS-A or SIZING-A: only "2 elevons")
EL_CF = 0.25                                               # chord fraction (K09-L wing.elevon.chord_frac scale, EST)
EL_Y0, EL_Y1 = 0.10, 0.40                                  # span stations each side, m (EST)
EL_S = 2 * (EL_Y1 - EL_Y0) * EL_CF * C_W                   # both elevons, m2
EL_TAU = 0.5                                               # flap effectiveness tau at cf/c 0.25 (thin airfoil)
CLD = CLA * EL_TAU * (EL_S / S_W)                          # dCL per rad of mean deflection, EST
EL_X = -(0.875 * C_W - 0.0246)                             # elevon centroid, m forward of the CG (negative = aft)
EL_Y = 0.5 * (EL_Y0 + EL_Y1)
EL_MAX = math.radians(25.0)                                # physical stops (K09-L B3 "25 deg travel"), EST
EL_RATE = math.radians(300.0)                              # servo rate limit (ES3352HV 0.1 s / 60 deg class), EST
EL_LAG = 0.04                                              # s
POSTSTALL_EL = 0.30                                        # elevon effectiveness in separated flow, EST (B3 K09-L uses its own curve)
SLIP = 0.0                                                 # fraction of the prop-wash dynamic pressure the elevons see; the props are above and below the wing plane (z +-0.156 m),
#                                                            gap about 0.04 m, so 0 by default (no credit, as K09-L and sizing). Sensitivity via cfg.
# ---------------- fins
FIN_S = 2 * 0.36 * 0.12
FIN_X = -(0.24 - 0.0246)                                   # fin centre, m forward of CG (aft = negative), as a_plant.py
CLAF = 2.5                                                 # effective fin lift slope per rad (AR 3, wing as end plate), EST
CDF = 2.0
HINGE_CH = -0.60                                           # hinge-moment coefficient per rad of deflection (EST), for the servo check

def clip(x, a, b): return a if x < a else (b if x > b else x)
def sgn(x): return 1.0 if x >= 0 else -1.0

def cl_att(a):
    x = CLA * a / CLMAX
    return CLMAX * x / (1 + abs(x) ** PCLIP) ** (1.0 / PCLIP)

def fatt(a, u):
    if u <= 0: return 0.0
    z = (abs(a) - ASTALL) / WSTALL
    return 0.0 if z > 40 else 1.0 / (1.0 + math.exp(z))

def airframe(u, v, w, p, q, r, dl, dr, wash=0.0):
    """Forces (N) and moments (N m) about the CG in body axes for wing + elevons + fins. dl, dr elevon deflection, rad, TE down positive.
    wash = extra dynamic-pressure velocity squared seen by the elevons (m2/s2). Returns F, T, diag dict."""
    V2 = u * u + w * w; V = math.sqrt(V2)
    a = math.atan2(w, u)
    qb = 0.5 * RHO * V2
    f = fatt(a, u)
    dm = 0.5 * (dl + dr)
    # ---- wing, attached branch at the AC
    cl = cl_att(a); cd = CD0 + cl * cl / (math.pi * E_OSW * AR) + 0.08 * dm * dm
    L = qb * S_W * cl; Dg = qb * S_W * cd
    sa, ca = math.sin(a), math.cos(a)
    Fx_a = L * sa - Dg * ca; Fz_a = -L * ca - Dg * sa
    # ---- wing, plate branch (identical to the hover plant): normal force on the z component, small axial force
    # plate normal coefficient: Cd90 sin^2(alpha), with a soft-stall plateau 0.55 for attached-side flow (EST: foam wing does not drop to a bare plate)
    cnp = max(CDW * math.sin(a) ** 2, 0.55 if u > 0 else 0.0)
    Fz_p = -qb * S_W * cnp * sgn(w) if V > 1e-6 else 0.0
    Fx_p = -0.5 * RHO * S_W * 0.10 * abs(u) * u
    Fx = f * Fx_a + (1 - f) * Fx_p; Fz = f * Fz_a + (1 - f) * Fz_p
    x_ac = -SM * C_W; x_cp = -(0.5 * C_W - 0.0246)
    ycp = -0.25 * B_W * clip(-v / (2.75 * abs(w) + 1e-6) * -1.0, -1.0, 1.0) if abs(w) > 1e-3 else 0.0
    ycp = -0.25 * B_W * clip((-v) / (2.75 * abs(w) + 1e-6), -1.0, 1.0) if abs(w) > 1e-3 else 0.0
    # moments: attached force at AC, plate force at CP; r x F with r = (x, y, 0): Mx = y Fz, My = -x Fz (+ z Fx = 0)
    Mx = (1 - f) * ycp * Fz_p
    My = -x_ac * f * Fz_a - x_cp * (1 - f) * Fz_p
    My += f * (CM0 * qb * S_W * C_W)
    # damping and dihedral effect (attached part only)
    if V > 1.0:
        My += f * CMQ * qb * S_W * C_W * (q * C_W / (2 * V))
        Mx += f * CLP * qb * S_W * B_W * (p * B_W / (2 * V))
        beta = math.asin(clip(v / max(V, 1e-3), -1, 1))
        Mx += f * CLB * qb * S_W * B_W * beta
    # ---- elevons: normal force changes at the elevon centroid; effectiveness falls in separated flow
    fe = POSTSTALL_EL + (1 - POSTSTALL_EL) * f
    qe = 0.5 * RHO * (V2 + wash)
    FzR = -qe * S_W * CLD * dr * 0.5 * fe; FzL = -qe * S_W * CLD * dl * 0.5 * fe
    Fz += FzR + FzL
    My += -EL_X * (FzR + FzL)
    Mx += EL_Y * FzR - EL_Y * FzL
    Fx += -0.5 * qe * S_W * 0.04 * (abs(dl) + abs(dr)) * 0.0   # elevon drag already in 0.08 dm^2
    # ---- fins: velocity at the fin includes the yaw rate (rotation about z_b is r)
    vf = v + r * FIN_X
    fa = fatt_f(vf, u)
    qf = 0.5 * RHO * (u * u + vf * vf)
    bf = math.atan2(vf, abs(u) + 1e-6)
    cy = CLAF * clip(bf, -0.35, 0.35)
    Fy_att = -qf * FIN_S * cy
    Fy_pl = -0.5 * RHO * FIN_S * CDF * abs(vf) * vf
    Fy = fa * Fy_att + (1 - fa) * Fy_pl
    Mz = FIN_X * Fy            # r x F: Mz = x Fy - y Fx
    # ---- hinge moment on one elevon (both alike), N m, for the servo check
    ce = EL_CF * C_W; se = (EL_Y1 - EL_Y0) * ce
    hing = abs(HINGE_CH) * qe * se * ce * max(abs(dl), abs(dr))
    return (Fx, Fy, Fz), (Mx, My, Mz), dict(alpha=a, V=V, cl=cl, f=f, hinge=hing)

def fatt_f(vf, u):
    if u <= 0: return 0.0
    z = (abs(math.atan2(vf, u)) - math.radians(18)) / 0.06
    return 0.0 if z > 40 else 1.0 / (1.0 + math.exp(z))

# ---------------- APC 9x4.5MR, MN2212 KV780, pack
DIA = 9 * 0.0254; KV = 780.0; RM = 0.173; I0 = 0.5; KT = 60 / (2 * math.pi * KV)
DER = 0.93          # prop_a.py R3 derate on thrust (same rpm, same power)
DOWNLOAD = 0.97     # sizing_a.py slipstream download

def _interp(xs, ys, x):
    if x <= xs[0]: return ys[0]
    if x >= xs[-1]:
        k = (ys[-1] - ys[-4]) / (xs[-1] - xs[-4]); return ys[-1] + k * (x - xs[-1])   # linear extrapolation into windmilling (EST)
    i = bisect.bisect_right(xs, x); t = (x - xs[i - 1]) / (xs[i] - xs[i - 1])
    return ys[i - 1] + t * (ys[i] - ys[i - 1])

def ct_cp(J, rpm):
    ks = D.RPMS
    rpm = clip(rpm, ks[0], ks[-1])
    i = max(0, min(len(ks) - 2, bisect.bisect_right(ks, rpm) - 1)); t = (rpm - ks[i]) / (ks[i + 1] - ks[i])
    c = [(_interp(D.J[k], D.CT[k], J), _interp(D.J[k], D.CP[k], J)) for k in (ks[i], ks[i + 1])]
    return c[0][0] + t * (c[1][0] - c[0][0]), c[0][1] + t * (c[1][1] - c[0][1])

def prop_at(rpm, V):
    n = rpm / 60.0; J = V / (n * DIA) if n > 1 else 0.0
    ct, cp = ct_cp(clip(J, 0.0, 1.0), rpm)         # J limited to 1.0: windmilling drag beyond the table is held (EST)
    T = ct * RHO * n * n * DIA ** 4
    Q = cp * RHO * n * n * DIA ** 5 / (2 * math.pi)       # P = Cp rho n^3 D^5, Q = P / (2 pi n)
    return T, Q

def motor_solve(Vm, V):
    """terminal voltage Vm (duty x bus) and axial airspeed V -> rpm, thrust (APC table N), shaft torque, phase current."""
    if Vm <= 0.05: return 0.0, 0.0, 0.0, 0.0
    lo, hi = 300.0, 16000.0
    for _ in range(45):
        n = 0.5 * (lo + hi); T, Q = prop_at(n, V); i = Q / KT + I0; vv = n / KV + i * RM
        lo, hi = (n, hi) if vv < Vm else (lo, n)
    n = 0.5 * (lo + hi); T, Q = prop_at(n, V); i = Q / KT + I0
    if i < 0:          # free-wheeling: ESC does not regenerate; solve Q = -Kt I0 (no phase current beyond the iron loss)
        lo2, hi2 = 300.0, 16000.0
        for _ in range(45):
            m = 0.5 * (lo2 + hi2); T2, Q2 = prop_at(m, V)
            lo2, hi2 = (m, hi2) if Q2 < -KT * I0 else (lo2, m)
        n = 0.5 * (lo2 + hi2); T, Q = prop_at(n, V); i = 0.0
    return n, T, Q, i

VM_MAX, VM_STEP, V_MAX, V_STEP = 17.5, 0.25, 40.0, 2.0
_GRID = None
def grid():
    global _GRID
    if _GRID is None:
        nv = int(VM_MAX / VM_STEP) + 1; na = int(V_MAX / V_STEP) + 1
        _GRID = [[motor_solve(i * VM_STEP, j * V_STEP) for j in range(na)] for i in range(nv)]
    return _GRID

def motor(Vm, V):
    """bilinear lookup -> (rpm, T table N, Q N m, I phase A)"""
    g = grid()
    x = clip(Vm / VM_STEP, 0, len(g) - 1.001); y = clip(V / V_STEP, 0, len(g[0]) - 1.001)
    i, j = int(x), int(y); fx, fy = x - i, y - j
    a, b, c, d = g[i][j], g[i + 1][j], g[i][j + 1], g[i + 1][j + 1]
    return tuple((a[k] * (1 - fx) + b[k] * fx) * (1 - fy) + (c[k] * (1 - fx) + d[k] * fx) * fy for k in range(4))

if __name__ == "__main__":
    print("CLA %.2f /rad, CD0 %.4f, CLD %.3f /rad, elevon area %.4f m2, CLmax of the blended curve:" % (CLA, CD0, CLD, EL_S))
    for a in (0, 4, 8, 11, 13, 15, 17, 20, 25, 30, 45, 60, 90):
        F, T, dg = airframe(10 * math.cos(math.radians(a)), 0, 10 * math.sin(math.radians(a)), 0, 0, 0, 0, 0)
        L = -F[2] * math.cos(math.radians(a)) + F[0] * math.sin(math.radians(a)); qS = 0.5 * RHO * 100 * S_W
        print("alpha %2d: CL %.3f  CN-ish Fz/qS %.3f  Cm %.4f" % (a, L / qS, -F[2] / qS, T[1] / (qS * C_W)))
    for m in (1.381, 1.50):
        W = m * 9.807
        # Vs: V where max over alpha of L = W
        def Lmax(V):
            return max((-airframe(V * math.cos(math.radians(a)), 0, V * math.sin(math.radians(a)), 0, 0, 0, 0, 0)[0][2] * math.cos(math.radians(a))
                        + airframe(V * math.cos(math.radians(a)), 0, V * math.sin(math.radians(a)), 0, 0, 0, 0, 0)[0][0] * math.sin(math.radians(a))) for a in [x * 0.5 for x in range(0, 60)])
        lo, hi = 5.0, 30.0
        for _ in range(40):
            mid = 0.5 * (lo + hi); lo, hi = (mid, hi) if Lmax(mid) < W else (lo, mid)
        print("m %.3f: model Vs %.2f m/s (MISSION 11.70 / 12.19), 1.3 Vs %.2f" % (m, lo, 1.3 * lo))
        V = 17.0; qS = 0.5 * 1.2 * V * V * S_W; cl = W / qS
        print("   at 17 m/s: CL %.3f; trim drag from the model: " % cl, end="")
        lo, hi = 0.0, 15.0
        for _ in range(40):
            al = math.radians(0.5 * (lo + hi)); F = airframe(V * math.cos(al), 0, V * math.sin(al), 0, 0, 0, 0, 0)[0]
            Lf = -F[2] * math.cos(al) + F[0] * math.sin(al); lo, hi = (0.5 * (lo + hi), hi) if Lf < W else (lo, 0.5 * (lo + hi))
        al = math.radians(lo); F = airframe(V * math.cos(al), 0, V * math.sin(al), 0, 0, 0, 0, 0)[0]
        Dr = -F[0] * math.cos(al) - F[2] * math.sin(al)
        print("alpha %.1f deg, drag %.2f N, L/D %.2f" % (lo, Dr, W / Dr))
    print("APC 9x4.5MR x0.93 x0.97 thrust per motor (N) at airspeed, duty 0.35..0.9, bus 14.9 V:")
    for V in (0, 5, 10, 15, 17, 20):
        row = []
        for duty in (0.35, 0.5, 0.7, 0.9):
            n, T, Q, i = motor(duty * 14.9, V); row.append("%.2f N %.0f rpm %.1f A" % (T * DER * DOWNLOAD, n, i))
        print("  V %2d:" % V, " | ".join(row))
