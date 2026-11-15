"""Concept A (scaled quad tailsitter) hover plant for ArduPilot SITL, JSON backend (UDP 9002, lock-step).
Pure stdlib. Hover-only rigid-body model: 4 fixed motors in an X at 14 deg tangential cant, wing and fins as
cross-flow plates, wind and gusts, fin-tip ground contact. Every constant is EST unless a source is named.
usage: python a_plant.py '<json config>'     (started by run_case.py; writes <out>.csv and <out>.plant.json)
Frames: world NED; body FRD in cruise attitude (x nose/chord, y right wing, z belly). Hover = nose up (x_b up),
copter forward = +z_b (belly), copter right = +y_b, copter down = -x_b (tail)."""
import json, math, socket, struct, sys, random, os

cfg = json.loads(sys.argv[1])
G = 9.81; RHO = 1.225
M = cfg.get("mass", 1.23)
CANT = math.radians(cfg.get("cant_deg", 14.0))
TSCALE = cfg.get("thrust_scale", 0.767)     # 1.0 = maker table at 14.8 V; 0.767 = sagged pack, hot (sizing_a.py: 13.16 V, x0.97)
DOWNLOAD = 0.97                             # 3 % slipstream download (sizing_a.py DOWNLOAD)
KQ = 0.0204                                 # prop torque / thrust, m (sizing: 65 N mm at 3.19 N)
TAU_M = 0.04                                # motor + ESC + rotor lag, s (EST)
WIND = cfg.get("wind", 0.0); WFROM = math.radians(cfg.get("wind_from_deg", 0.0))
GUST = cfg.get("gust", 0.0); GUST_T = cfg.get("gust_s", 2.0)            # 1-cos gust on top of WIND, m/s, rise time s
TURB = cfg.get("turb", 0.0)                                             # OU turbulence sigma, m/s (vertical 0.5x), tau 2 s
HOLD = cfg.get("hold_s", 60.0); ALT_TRIG = cfg.get("alt_trigger", 18.0); SETTLE = cfg.get('settle', 15.0); RAMP = 4.0
CDW, CDF = cfg.get("cd_wing", 2.0), cfg.get("cd_fin", 2.0)              # plate Cd (sizing 2.0-2.05)
ARM = cfg.get("arm", 1.0); WING_S = cfg.get("wing_s", 1.0); FIN_S = cfg.get("fin_s", 1.0); PORT = 9002 + 10 * cfg.get("inst", 0)
S_W, B_W, C_W = 0.22 * WING_S, 0.90, 0.245; A_FIN = 2 * 0.36 * 0.12 * FIN_S
CG_AFT = 0.0246                                                         # CG aft of LE (sizing section 6); replaced by the CAD value below (cad=1, default)
CADM = None
if cfg.get("cad", 1):                                                   # QP-4 7.2 #2: the as-drawn aircraft (sitl/cad_mass.py -> cad_mass.json)
    _cp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cad_mass.json")
    if os.path.exists(_cp):
        CADM = json.load(open(_cp))
        CG_AFT = cfg.get("cg_aft", CADM["cg_x_m"])
random.seed(cfg.get("seed", 1))
# ---- QP-3 forward-flight mode: cfg fwd=1 switches the motors to the APC 9x4.5MR + MN2212 + pack model (a_aero.py) and the wing / elevons / fins to the
#      full-alpha model. fwd=0 is the unchanged hover plant (regression: same numbers as QP-2 / WIND.md).
import os
FWD = bool(cfg.get("fwd", 0))
if FWD:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import a_aero as AE
    AE.SLIP = cfg.get("slip", 0.0)
    if "cg_aft" in cfg and CADM: AE.set_cg(cfg["cg_aft"])
    VREST = cfg.get("vrest", 14.92)            # pack rest voltage, V (14.92 = 3.73 V/cell, the T/W-sag state of MASS-GATE; 16.8 fresh)
    HOT = cfg.get("hot", 0.97 if VREST < 15.5 else 1.0)   # winding-hot thrust factor used with the sag state (sizing_a.py)
    RPACK = cfg.get("rpack", 0.030)            # pack resistance, ohm (prop_a.py EST)
    ES5, ES6 = cfg.get("es5", 1.0), cfg.get("es6", -1.0)  # elevon servo sign: deflection (TE down +) = sign x (pwm - 1500) / 500 x EL_MAX (fit in QP-3; see SITL-FLIGHT.md)
    ELV_SCALE = cfg.get("elv_scale", 1.0)      # 1.0: full 1000-2000 us throw = the physical +-20 deg stop (QP-4: was 25)
    CMDF = cfg.get("cmd_file", None); WIND_T0 = cfg.get("wind_t0", None); WIND_ALT = cfg.get("wind_alt", 20.0)
    ELV_FAIL = cfg.get("elv_scale_fail", 1.0)

# ---- mass properties from the sizing mass table (g, x aft of LE, y, z); positions relative to CG, x forward
items = [(220, 0.095, 0, 0), (36, 0.24, 0.45, 0), (260, -0.040, 0.19, 0.13), (32, -0.085, 0.19, 0.13), (40, 0.050, 0.19, 0.0),
         (232, -0.020, 0, 0), (110, 0.060, 0, 0), (30, 0.200, 0.30, 0), (120, -0.020, 0.19, 0.13), (35, 0.100, 0, 0)]
tot = sum(i[0] for i in items); kk = M * 1000.0 / tot
Ixx = Iyy = Izz = 0.0
for g, xa, y, z in items:
    if abs(y - 0.19) < 1e-9: y, z = y * ARM, z * ARM
    pts = [(xa, sy * y, sz * z) for sy in ((1, -1) if y else (1,)) for sz in ((1, -1) if z else (1,))]
    gm = g * kk / 1000.0 / len(pts)
    for xx, yy, zz in pts:
        x = -(xx - CG_AFT)
        Ixx += gm * (yy * yy + zz * zz); Iyy += gm * (x * x + zz * zz); Izz += gm * (x * x + yy * yy)
mw = 0.220 * kk * WING_S
Ixx += mw * B_W ** 2 / 12; Iyy += mw * C_W ** 2 / 12; Izz += mw * (B_W ** 2 + C_W ** 2) / 12     # wing plate, own inertia
Iyy += 2 * 0.018 * kk * 0.36 ** 2 / 12 * 0; Izz += 2 * 0.018 * kk * 0.36 ** 2 / 12                # fin own inertia (small)
I = (Ixx, Iyy, Izz)
if CADM:                                                                # CAD point masses + own inertias, scaled to the case mass; body axes (x fwd, y right, z down)
    _k = M / CADM["mass_basic_kg"]; _c = CADM["I_cad_axes_kgm2"]
    I = (_c["Ixx"] * _k, _c["Iyy"] * _k, _c["Izz"] * _k)               # CAD x aft/y right/z up: diagonal terms are the same in body axes

# ---- motors: (copter f = +z_b, r = +y_b, spin +1 CCW). ArduCopter X: 1 FR ccw, 2 RL ccw, 3 FL cw, 4 RR cw
YM, ZM, XM = 0.19 * ARM, 0.13 * ARM, 0.11
if CADM: XM = -CADM["prop_hub_x_aft_of_LE_m"] + CG_AFT                  # prop plane 121 mm ahead of the LE (CAD), forward of the CG by this
mot = [(+ZM, +YM, +1), (-ZM, -YM, +1), (+ZM, -YM, -1), (-ZM, +YM, -1)]
mpos, mtang, mspin = [], [], []
for f, r, s in mot:
    rho = math.hypot(f, r)
    mpos.append((XM, r, f)); mtang.append((0.0, f / rho, -r / rho)); mspin.append(s)   # t = (-r f_hat + f r_hat)/rho in body (x,y,z)

TAB_U = [0.0, 0.5, 0.65, 0.75, 0.85, 1.0]; TAB_G = [0.0, 293.0, 476.0, 605.0, 742.0, 918.0]   # V: store.tmotor.com MN2212 V2.0 KV780, 14.8 V
def tstat(u):
    u = min(max(u, 0.0), 1.0)
    if u < 0.5: return 293.0 * (u / 0.5) ** 1.65 * 9.81e-3
    for i in range(1, len(TAB_U)):
        if u <= TAB_U[i]:
            return (TAB_G[i - 1] + (TAB_G[i] - TAB_G[i - 1]) * (u - TAB_U[i - 1]) / (TAB_U[i] - TAB_U[i - 1])) * 9.81e-3
    return TAB_G[-1] * 9.81e-3

def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def add(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def sc(a, s): return (a[0]*s, a[1]*s, a[2]*s)
def qmul(a, b):
    return (a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3], a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2],
            a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1], a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0])
def rot(q, v):   # body -> world
    w, x, y, z = q
    return ((1-2*(y*y+z*z))*v[0] + 2*(x*y-w*z)*v[1] + 2*(x*z+w*y)*v[2],
            2*(x*y+w*z)*v[0] + (1-2*(x*x+z*z))*v[1] + 2*(y*z-w*x)*v[2],
            2*(x*z-w*y)*v[0] + 2*(y*z+w*x)*v[1] + (1-2*(x*x+y*y))*v[2])
def irot(q, v): return rot((q[0], -q[1], -q[2], -q[3]), v)
def qnorm(q):
    n = math.sqrt(sum(c*c for c in q)); return tuple(c/n for c in q)
def mat2q(R):   # R[i][j], body -> world
    t = R[0][0]+R[1][1]+R[2][2]
    if t > 0:
        s = math.sqrt(t+1)*2; return qnorm((s/4, (R[2][1]-R[1][2])/s, (R[0][2]-R[2][0])/s, (R[1][0]-R[0][1])/s))
    if R[0][0] > R[1][1] and R[0][0] > R[2][2]:
        s = math.sqrt(1+R[0][0]-R[1][1]-R[2][2])*2; return qnorm(((R[2][1]-R[1][2])/s, s/4, (R[0][1]+R[1][0])/s, (R[0][2]+R[2][0])/s))
    if R[1][1] > R[2][2]:
        s = math.sqrt(1+R[1][1]-R[0][0]-R[2][2])*2; return qnorm(((R[0][2]-R[2][0])/s, (R[0][1]+R[1][0])/s, s/4, (R[1][2]+R[2][1])/s))
    s = math.sqrt(1+R[2][2]-R[0][0]-R[1][1])*2; return qnorm(((R[1][0]-R[0][1])/s, (R[0][2]+R[2][0])/s, (R[1][2]+R[2][1])/s, s/4))

# ---- state: nose up, belly north, feet on the ground (CG 0.2754 m above the foot line)
FOOT_X = -((CADM["x_ground_m"] if CADM else 0.30) - CG_AFT)
q = mat2q(((0, 0, 1), (0, 1, 0), (-1, 0, 0)))      # body x -> up, y -> east, z -> north
pos = (0.0, 0.0, FOOT_X); vel = (0.0, 0.0, 0.0); om = (0.0, 0.0, 0.0)
uf = [0.0] * 4
feet = [(FOOT_X, sy * (CADM["fin_y_m"] if CADM else 0.45), sz * 0.18) for sy in (1, -1) for sz in (1, -1)]
turb = [0.0, 0.0, 0.0]

def air_wind(t, tw0):
    s = 0.0 if tw0 is None else min(max((t - tw0) / RAMP, 0.0), 1.0)
    w = WIND * s
    if GUST and tw0 is not None:
        tg = t - (tw0 + RAMP + cfg.get("gust_at", 20.0))
        if 0 <= tg <= GUST_T: w += GUST * 0.5 * (1 - math.cos(2 * math.pi * tg / GUST_T))
    return (-w * math.cos(WFROM) + turb[0], -w * math.sin(WFROM) + turb[1], turb[2])

# ---- forward-flight loads (fwd=1): motors from APC data, wing / elevons / fins from a_aero.airframe
DG = dict(alpha=0.0, V=0.0, hinge=0.0, vbus=0.0, ipack=0.0, rpm=[0] * 4, ibus=[0] * 4, dl=0.0, dr=0.0, wh=0.0, thr_tot=0.0)
ST = dict(dl=0.0, dr=0.0, vbus=0.0, ipack=0.0, wh=0.0, vrest=None, dead=[False] * 4, elv_dead=False)
if FWD:
    ST["vbus"] = VREST; ST["vrest"] = VREST
def fwd_loads(dt, pwm, vrel):
    F = (0.0, 0.0, 0.0); T = (0.0, 0.0, 0.0); thr = []
    vbus = max(ST["vbus"], 6.0); itot = 0.0; wsum = 0.0; tsum = 0.0
    for i in range(4):
        u = min(max((pwm[i] - 1000.0) / 1000.0, 0.0), 1.0)
        if ST["dead"][i]: u = 0.0
        uf[i] += (u - uf[i]) * min(1.0, dt / TAU_M)
        rv = add(vrel, sc(cross(om, mpos[i]), -1.0))
        vax = max(0.0, -rv[0])
        rpm, Tt, Qt, Ip = AE.motor(uf[i] * vbus, vax)
        th = Tt * AE.DER * AE.DOWNLOAD * HOT
        if ST["dead"][i]: th = 0.0; Qt = 0.0; Ip = 0.0     # failed motor: rotor drag neglected (EST: it is a fatal case either way)
        thr.append(th)
        pm = uf[i] * vbus * Ip / 0.98 if Ip > 0 else 0.0   # bus power incl ESC 0.98
        itot += pm / vbus; DG["rpm"][i] = rpm; DG["ibus"][i] = pm / vbus; tsum += th
        s = math.sin(CANT) * mspin[i]
        d = (math.cos(CANT), s * mtang[i][1], s * mtang[i][2])
        fv = (th * d[0], th * d[1], th * d[2])
        F = add(F, fv); T = add(T, cross(mpos[i], fv))
        T = add(T, sc(d, -mspin[i] * Qt))                       # reaction torque about the shaft
    itot += 0.5                                                  # avionics + servos, A (EST)
    ST["ipack"] = itot; ST["vbus"] = max(ST["vrest"] - RPACK * itot, 6.0); ST["wh"] += ST["vbus"] * itot * dt / 3600.0
    # elevon servos: rate limit + lag, physical stop
    for k, (pidx, sg) in enumerate(((4, ES5), (5, ES6))):
        tgt = sg * (pwm[pidx] - 1500.0) / 500.0 * AE.EL_MAX * ELV_SCALE
        if ST["elv_dead"]: tgt = 0.0
        tgt = max(-AE.EL_MAX, min(AE.EL_MAX, tgt))
        key = "dl" if k == 0 else "dr"
        want = (tgt - ST[key]) * min(1.0, dt / AE.EL_LAG)
        lim = AE.EL_RATE * dt; want = max(-lim, min(lim, want)); ST[key] += want
    u_, v_, w_ = -vrel[0], -vrel[1], -vrel[2]
    p_, q_, r_ = om
    wash = 0.0
    if AE.SLIP > 0: wash = AE.SLIP * max(0.0, 2.0 * (tsum / 4.0) / (RHO * 0.0410))
    Fa, Ta, dg = AE.airframe(u_, v_, w_, p_, q_, r_, ST["dl"], ST["dr"], wash)
    DG.update(alpha=dg["alpha"], V=dg["V"], hinge=dg["hinge"], vbus=ST["vbus"], ipack=itot, dl=ST["dl"], dr=ST["dr"], wh=ST["wh"], thr_tot=tsum)
    return add(F, Fa), add(T, Ta), thr

def step(t, dt, pwm, tw0):
    global q, pos, vel, om, uf, turb
    if TURB and tw0 is not None:
        a = math.exp(-dt / 2.0); b = TURB * math.sqrt(1 - a * a)
        turb = [turb[0]*a + b*random.gauss(0, 1), turb[1]*a + b*random.gauss(0, 1), turb[2]*a + 0.5*b*random.gauss(0, 1)]
    wn = air_wind(t, tw0)
    wb = irot(q, wn); vb = irot(q, vel)
    vrel = (wb[0]-vb[0], wb[1]-vb[1], wb[2]-vb[2])          # air velocity relative to the body, body axes
    if FWD:
        F, T, thr = fwd_loads(dt, pwm, vrel)
    else:
        F = (0.0, 0.0, 0.0); T = (0.0, 0.0, 0.0); thr = []
        for i in range(4):
            u = min(max((pwm[i] - 1000.0) / 1000.0, 0.0), 1.0)
            uf[i] += (u - uf[i]) * min(1.0, dt / TAU_M)
            ts = tstat(uf[i]) * TSCALE * DOWNLOAD
            rpm = 4248.0 * math.sqrt(max(ts, 0.05) / 3.2); v0 = rpm * 4.5 * 0.0254 / 60.0
            rv = add(vrel, sc(cross(om, mpos[i]), -1.0))
            vc = -rv[0]                                          # air flowing through the disc from the thrust side
            fct = 1 - (vc / v0) ** 2 if vc >= 0 else 1 + 0.3 * (-vc / v0)
            th = ts * min(max(fct, 0.3), 1.2); thr.append(th)
            s = math.sin(CANT) * mspin[i]
            fv = (th * math.cos(CANT), th * s * mtang[i][1], th * s * mtang[i][2])
            F = add(F, fv); T = add(T, cross(mpos[i], fv))
            T = add(T, (-mspin[i] * KQ * th, 0.0, 0.0))          # CCW motor: reaction +yaw about copter-down = -x_b
        # wing: cross-flow plate on the z_b component + small chordwise drag; CP shifts to the windward quarter span
        fz = 0.5 * RHO * S_W * CDW * abs(vrel[2]) * vrel[2]
        fx = 0.5 * RHO * S_W * 0.10 * abs(vrel[0]) * vrel[0]
        ycp = -0.25 * B_W * max(-1.0, min(1.0, vrel[1] / (2.75 * abs(vrel[2]) + 1e-6))) if abs(vrel[2]) > 1e-3 else 0.0
        xcp = -(0.5 * C_W - CG_AFT)
        F = add(F, (fx, 0.0, fz)); T = add(T, cross((xcp, ycp, 0.0), (fx, 0.0, fz)))
        # fins: two plates normal to y, centre 0.2154 m aft of the CG
        fy = 0.5 * RHO * A_FIN * CDF * abs(vrel[1]) * vrel[1]
        F = add(F, (0.0, fy, 0.0)); T = add(T, cross((-(0.24 - CG_AFT), 0.0, 0.0), (0.0, fy, 0.0)))
    # ground contact: four fin-foot points
    Fc = (0.0, 0.0, 0.0); Tc = (0.0, 0.0, 0.0); touch = 0
    for fp in feet:
        rw = rot(q, fp); pz = pos[2] + rw[2]
        if pz > 0:
            vp = add(vel, rot(q, cross(om, fp)))
            n = max(0.0, 4000.0 * pz + 25.0 * vp[2]); touch += 1
            fh = (-200.0 * vp[0], -200.0 * vp[1]); fm = math.hypot(*fh); lim = 0.6 * n
            if fm > lim and fm > 0: fh = (fh[0] * lim / fm, fh[1] * lim / fm)
            fb = irot(q, (fh[0], fh[1], -n)); Fc = add(Fc, fb); Tc = add(Tc, cross(fp, fb))
    Ft = add(F, Fc); Tt = add(T, Tc)
    aspec = sc(Ft, 1.0 / M)
    aw = add(rot(q, aspec), (0.0, 0.0, G))
    vel = add(vel, sc(aw, dt)); pos = add(pos, sc(vel, dt))
    Iom = (I[0]*om[0], I[1]*om[1], I[2]*om[2]); gy = cross(om, Iom)
    al = ((Tt[0]-gy[0]) / I[0], (Tt[1]-gy[1]) / I[1], (Tt[2]-gy[2]) / I[2])
    if touch >= 3: al = tuple(a - 8.0 * w for a, w in zip(al, om))
    om = add(om, sc(al, dt))
    dq = qmul(q, (0.0, om[0], om[1], om[2])); q = qnorm(tuple(q[j] + 0.5 * dt * dq[j] for j in range(4)))
    return aspec, wn, vrel, thr, touch

def copter_yaw_lean(q):
    xb = rot(q, (1, 0, 0)); fb = rot(q, (0, 0, 1))
    lean = math.degrees(math.acos(max(-1, min(1, -xb[2]))))
    return math.degrees(math.atan2(fb[1], fb[0])), lean

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("0.0.0.0", PORT)); sock.settimeout(8 if FWD else 180)
t = 0.0; last_fc = None; tw0 = None; t_alt = None; rows = []; t_end = None; yaw0 = None; home_xy = None; log_acc = 0.0
out = cfg["out"]; frows = []; fl_acc = 0.0; cmd_mt = 0.0; cmd_n = 0; evlog = []
def euler_rpy(q):
    xb = rot(q, (1, 0, 0)); yb = rot(q, (0, 1, 0)); zb = rot(q, (0, 0, 1))
    pitch = math.degrees(math.asin(max(-1, min(1, -xb[2]))))
    # heading of the belly (copter forward) projected on the horizontal; in cruise the nose heading
    hdg_nose = math.degrees(math.atan2(xb[1], xb[0])); hdg_belly = math.degrees(math.atan2(zb[1], zb[0]))
    roll = math.degrees(math.atan2(yb[2], zb[2]))
    return pitch, roll, hdg_nose, hdg_belly
try:
    while True:
        data, addr = sock.recvfrom(1024)
        if len(data) < 40: continue
        magic, frate, fc = struct.unpack("<HHI", data[:8])
        if magic == 18458: pwm = struct.unpack("<16H", data[8:40])
        elif magic == 29569: pwm = struct.unpack("<32H", data[8:72])
        else: continue
        nfr = 1 if (last_fc is None or fc <= last_fc) else fc - last_fc
        last_fc = fc; dt = nfr / float(frate)
        if FWD and CMDF:
            cmd_n += 1
            if cmd_n % 200 == 0:
                try:
                    mt = os.path.getmtime(CMDF)
                    if mt != cmd_mt:
                        cmd_mt = mt; c = json.load(open(CMDF))
                        if "motor_out" in c: ST["dead"][int(c["motor_out"])] = True; evlog.append((round(t, 2), "motor_out", c["motor_out"]))
                        if "vrest" in c: ST["vrest"] = float(c["vrest"]); evlog.append((round(t, 2), "vrest", c["vrest"]))
                        if "elv_dead" in c: ST["elv_dead"] = bool(c["elv_dead"])
                        if "wind" in c: WIND = float(c["wind"]); evlog.append((round(t, 2), "wind", WIND))
                        if "wind_from" in c: WFROM = math.radians(float(c["wind_from"]))
                        if "gust" in c: GUST = float(c["gust"]); cfg["gust_at"] = t - (tw0 if tw0 is not None else 0) - RAMP + 1.0
                except Exception: pass
        aspec, wn, vrel, thr, touch = step(t, dt, pwm, tw0)
        t += dt
        alt = -pos[2]
        yaw, lean = copter_yaw_lean(q)
        if FWD:
            if tw0 is None and ((WIND_T0 is not None and t >= WIND_T0) or (WIND_T0 is None and alt >= WIND_ALT and touch == 0)): tw0 = t
            fl_acc += dt
            if fl_acc >= 0.05:
                fl_acc = 0.0
                pit, rol, hn, hb = euler_rpy(q); wspd = math.hypot(wn[0], wn[1])
                frows.append((round(t, 3), round(pos[0], 3), round(pos[1], 3), round(alt, 3), round(vel[0], 3), round(vel[1], 3), round(-vel[2], 3), round(pit, 2),
                              round(rol, 2), round(hn, 2), round(hb, 2), round(math.degrees(DG["alpha"]), 2), round(DG["V"], 2), round(max(0.0, -vrel[0]), 2),
                              *[round((p_ - 1000) / 1000.0, 3) for p_ in pwm[:4]], *[round(x, 3) for x in thr], round(math.degrees(DG["dl"]), 2), round(math.degrees(DG["dr"]), 2),
                              round(DG["ipack"], 2), round(DG["vbus"], 2), *[round(x, 2) for x in DG["ibus"]], round(DG["hinge"], 4), round(DG["wh"], 3), touch,
                              round(wspd, 2), round(-vrel[2], 2), round(-vrel[1], 2), round(math.degrees(om[0]), 1), round(math.degrees(om[1]), 1), round(math.degrees(om[2]), 1),
                              round(-aspec[2] / G, 2)))
            if t > cfg.get("max_t", 900.0): break
        else:
            if t_alt is None and alt >= ALT_TRIG and touch == 0:
                t_alt = t; tw0 = t + SETTLE; t_end = tw0 + RAMP + HOLD; yaw0 = yaw
            log_acc += dt
            if int(t * 2) != int((t - dt) * 2) and int(t) % 5 == 0 and int(t * 2) % 2 == 0:
                print('t=%.1f alt=%.2f lean=%.1f touch=%d u=%s' % (t, alt, lean, touch, [round((p_ - 1000) / 1000, 2) for p_ in pwm[:4]]), flush=True)
            if log_acc >= 0.05 and tw0 is not None:
                log_acc = 0.0
                if home_xy is None and t >= tw0: home_xy = pos
                us = [(p - 1000.0) / 1000.0 for p in pwm[:4]]
                wd = (yaw - yaw0 + 180) % 360 - 180
                hx = (pos[0] - home_xy[0], pos[1] - home_xy[1], pos[2] - home_xy[2]) if home_xy else (0, 0, 0)
                rows.append((round(t - tw0, 3), round(math.hypot(wn[0], wn[1]), 3), round(lean, 3), round(wd, 3), round(math.hypot(hx[0], hx[1]), 3),
                             round(-hx[2], 3), *[round(x, 4) for x in us], round(pos[0], 3), round(pos[1], 3), round(alt, 3), *[round(x, 3) for x in thr]))
            if t_end is not None and t > t_end: break
            if t > cfg.get("max_t", 400.0) and t_end is None: break
        js = {"timestamp": t, "imu": {"gyro": list(om), "accel_body": list(aspec)}, "position": list(pos), "quaternion": list(q),
              "velocity": list(vel), "airspeed": max(0.0, -vrel[0]) if not FWD else max(0.0, -vrel[0])}
        sock.sendto(("\n" + json.dumps(js) + "\n").encode(), addr)
finally:
    if FWD:
        with open(out + ".fwd.csv", "w") as f:
            f.write("t,pn,pe,alt,vn,ve,vu,pitch,roll,hdg_nose,hdg_belly,alpha,V,u_ax,u1,u2,u3,u4,th1,th2,th3,th4,dl,dr,ipack,vbus,i1,i2,i3,i4,hinge,wh,touch,wind,w_air,v_air,p,q,r,nz\n")
            for r in frows: f.write(",".join(str(x) for x in r) + "\n")
        json.dump(evlog, open(out + ".events.json", "w"))
    with open(out + ".csv", "w") as f:
        f.write("t,wind,lean,yaw_err,pos_err,alt_dev,u1,u2,u3,u4,pn,pe,alt,th1,th2,th3,th4\n")
        for r in rows: f.write(",".join(str(x) for x in r) + "\n")
    json.dump({"t_end": t, "I": I, "mass": M, "reached_alt": t_alt is not None, "cfg": cfg}, open(out + ".plant.json", "w"))
