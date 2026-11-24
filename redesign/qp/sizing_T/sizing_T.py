"""Candidate T (K06 scaled down): scratch tilt-tricopter, 2 front tilt + 1 rear fixed.  Run: python -I sizing_T.py
Thrust table: T-Motor AT2317 KV880 + APC 11x5.5, ~14.2-14.7 V (4S),
https://store.tmotor.com/product/at2317-long-shaft-fixed-wing-motor.html (read 2026-11-14).
EST = estimate.  Prints the numbers used in review/QP-1/SIZING-T.md."""
import math
RHO, G = 1.225, 9.807
# (thrust g, A, W, torque N m) APC 11x5.5, T-Motor table, 40..100 % throttle
TAB = [(592, 4.82, 70.62, .087), (667, 5.68, 83.25, .098), (743, 6.60, 96.57, .110), (828, 7.61, 111.15, .122),
       (928, 8.94, 130.34, .137), (1049, 10.68, 155.23, .156), (1161, 12.43, 180.15, .173), (1282, 14.39, 207.80, .192),
       (1402, 16.69, 240.15, .213), (1627, 21.86, 311.81, .254), (1670, 23.36, 332.14, .264)]


def interp(t, col):
    if t <= TAB[0][0]:  # below table: P ~ T^1.5 (momentum scaling), torque ~ T
        r = t / TAB[0][0]
        v = TAB[0][col]
        return v * (r ** 1.5 if col in (1, 2) else r)
    for a, b in zip(TAB, TAB[1:]):
        if a[0] <= t <= b[0]:
            f = (t - a[0]) / (b[0] - a[0])
            return a[col] + f * (b[col] - a[col])
    return TAB[-1][col]


TMAX = 1670.0
SAG = 0.90      # thrust at loaded/worn pack vs table, EST (K06 card)
INSTALL = 1.10  # nacelle/wing blockage, EST (K06 card)
CTRL = 1.10     # control margin (RESTUDY basis)
# ---- geometry ----
SPAN, CR, CT, SWEEP = 1.20, 0.30, 0.19, 20.0
S = SPAN / 2 * (CR + CT)
lam = CT / CR
MAC = 2 / 3 * CR * (1 + lam + lam ** 2) / (1 + lam)
AR = SPAN ** 2 / S
ymac = SPAN / 6 * (1 + 2 * lam) / (1 + lam)
xle_mac = ymac * math.tan(math.radians(SWEEP))
NP_wing = xle_mac + 0.25 * MAC
NP = NP_wing - 0.018   # -18 mm for pod + tractor props at 90 deg, EST
SM = 0.10
XCG = NP - SM * MAC
XF = 0.20
XR = 2 * XF            # equal thrust shares: 2*T*XF = T*XR
YF = 0.24              # front motor lateral offset
t_c, XPS = 0.10, 33.0  # EST
foam = 0.68 * t_c * (CR ** 2 + CR * CT + CT ** 2) / 3 * SPAN * XPS * 1000
tube = lambda od, idm: math.pi / 4 * (od ** 2 - idm ** 2) * 1e-6 * 1600 * 1000  # g per m
skin = 2.05 * S * 75 * 1.25  # tape skin 75 g/m2 (K06 REVIEW C3)
ITEMS = [
    ("prop", "3x T-Motor AT2317 KV880 (79 g, maker)", 3 * 79),
    ("prop", "3x APC 11x5.5E (0.81 oz = 23 g, apcprop.com 2026-11-14)", 3 * 23),
    ("prop", "3x ESC 45 A BLHeli_S (6.6 g listing, K06 card)", 3 * 6.6),
    ("prop", "motor/ESC wiring, XT60, 14 AWG, caps, EST", 80),
    ("tilt", "2x Powerhobby 329TG tilt servo (63 g listed, K06 card)", 2 * 63),
    ("tilt", "2x printed nacelle + 6 mm shaft + bearings + horn (K06 REVIEW C2 65 g; EST 60)", 2 * 60),
    ("wing", "XPS cores (calc)", foam), ("wing", "tape skin (calc)", skin),
    ("wing", "spar sockets 20x18 CF 2x0.30 m (calc)", tube(20, 18) * 0.60),
    ("wing", "joiner 18x16 CF 0.34 m (calc)", tube(18, 16) * 0.34),
    ("wing", "2x elevon servos 17 g EST", 2 * 17), ("wing", "2x tip fins, horns, pushrods, hinge tape EST", 40),
    ("body", "printed pod + hatch 0.36 m (K06 REVIEW C1 280 g scaled ~0.45) EST", 125),
    ("body", "tail boom 18x16 CF 0.45 m (calc)", tube(18, 16) * 0.45),
    ("body", "rear motor mount EST", 15), ("body", "3 TPU skid feet EST", 30), ("body", "fasteners, inserts, wing bolts EST", 35),
    ("body", "battery tray, strap, extensions, GPS mast (K06 REVIEW C4) EST", 50),
    ("avi", "SpeedyBee F405 Wing APP + cables EST", 30), ("avi", "GPS/compass M100-5883 EST", 12), ("avi", "ELRS RX", 4),
    ("avi", "ASPD-4525 + pitot + tubing EST", 15), ("avi", "Remote ID (conditional) EST", 7),
]
CONT, GROWTH_G, PACK_G, PACK_WH = 0.10, 100.0, 211.0, 14.8 * 2.2  # CNHL Black 4S 2200 mAh 40C XT60, 211 g, $17.99 (chinahobbyline.com, search snippet 2026-11-14)
nonbat = sum(m for *_, m in ITEMS)
mtow_build = nonbat * (1 + CONT) + PACK_G
MTOW = mtow_build + GROWTH_G


def hover(mass_g):
    per = mass_g / 3
    return per, interp(per, 2) * 3 * INSTALL * CTRL, interp(per, 1) * 3 * INSTALL


def run(mass_g, v=16.0, cd0=0.040, e=0.8, clmax=0.85):
    W = mass_g / 1000 * G
    vs = math.sqrt(2 * W / (RHO * S * clmax))
    cl = 2 * W / (RHO * S * v * v)
    cd = cd0 + cl * cl / (math.pi * e * AR)
    ld = cl / cd
    pel = W / ld * v / (0.55 * 0.75)
    per, ph, ih = hover(mass_g)
    tw = 3 * TMAX / mass_g
    return dict(vs=vs, v13=1.3 * vs, cl=cl, ld=ld, pcruise=pel, icruise=pel / 14.8, per=per, phover=ph, ihover=ih,
                tw_fresh=tw, tw_sag=tw * SAG, wl=mass_g / 1000 / S)


def mission(mass_g, **k):
    r = run(mass_g, **k)
    ph = r["phover"]
    e_h = ph * 180 / 3600 * 1.05
    e_c = r["pcruise"] * 210 / 3600
    e_t = 2 * 12 * ph * 1.30 / 3600
    return e_h + e_c + e_t, e_h, e_c, e_t


if __name__ == "__main__":
    print(f"S {S:.3f} m2  AR {AR:.2f}  MAC {MAC:.3f} m  NP {NP:.3f}  CG {XCG:.3f} m aft of root LE (SM {SM:.0%} MAC)")
    cat = {}
    for g_, n, m in ITEMS:
        cat[g_] = cat.get(g_, 0) + m
        print(f"| {g_} | {n} | {m:.0f} |")
    print({k: round(v) for k, v in cat.items()}, f"nonbat {nonbat:.0f} +10% {nonbat * CONT:.0f} pack {PACK_G:.0f} "
          f"build {mtow_build:.0f} +growth {GROWTH_G:.0f} -> MTOW {MTOW:.0f} g")
    for m in (mtow_build, MTOW, MTOW + 100):
        r = run(m)
        e = mission(m)
        print(f"\nmass {m:.0f}: vs {r['vs']:.1f} 1.3vs {r['v13']:.1f} WL {r['wl']:.1f} L/D {r['ld']:.1f} "
              f"Pcruise {r['pcruise']:.0f} W ({r['icruise']:.1f} A) per-motor {r['per']:.0f} g Phover {r['phover']:.0f} W "
              f"Ih {r['ihover']:.1f} A TW fresh {r['tw_fresh']:.2f} sag {r['tw_sag']:.2f}")
        print(f"   mission Wh {e[0]:.1f} (hover {e[1]:.1f} cruise {e[2]:.1f} trans {e[3]:.1f}); pack need {e[0] / 0.72:.1f} Wh "
              f"vs {PACK_WH:.1f}; hover-only {PACK_WH * 0.72 / r['phover'] * 60:.1f} min")
        print(f"   cruise to reserve after 180 s hover + 2 trans: {(PACK_WH * 0.72 - e[1] - e[3]) / r['pcruise'] * 60:.1f} min")
    per = MTOW / 3
    T = per / 1000 * G
    for ang in (10, 15, 20):
        print(f"yaw N at +-{ang} deg front tilt: {2 * T * math.sin(math.radians(ang)) * YF:.2f} N m")
    print(f"rear prop reaction torque at hover {interp(per, 3):.3f} N m; Izz EST {MTOW / 1000 * 0.18 ** 2:.3f}")
    for dx in (0.01, 0.02, 0.03):
        W_ = MTOW / 1000 * G
        R = W_ * (XF - dx) / ((XF - dx) + (XR + dx))
        F = (W_ - R) / 2
        print(f"CG {dx * 1000:.0f} mm forward: rear {R / G * 1000:.0f} g, front each {F / G * 1000:.0f} g")
    Fs = 0.5 * RHO * 25 * 0.07
    print(f"5 m/s side force {Fs:.2f} N bank {math.degrees(math.atan(Fs / (MTOW / 1000 * G))):.1f} deg")
    print(f"5 m/s yaw disturbance EST {0.5 * RHO * 25 * 0.024 * 0.30:.2f} N m")
    om = 6300 * 2 * math.pi / 60
    print(f"gyro torque at 90 deg/s {3.5e-5 * om * math.radians(90):.3f} N m")
