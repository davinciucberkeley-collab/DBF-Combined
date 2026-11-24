"""Small quadplane (concept B, D-181) sizing, QP-1, 2026-11-14.
Reproduce:  python -I redesign/qp/sizing/sizing.py     (stdlib only, prints markdown, writes nothing)

Labels: EST = estimate; PUB = published by the maker (URL + date in SRC); U = price from a search
snippet / reseller, vendor checkout not read; "-" = unknown.
Mission basis: redesign/review/CLOSURE-ROUND-2026-11-14/A2.md s2.1 (see MISSION below).
"""
import math

G, RHO, MU = 9.81, 1.20, 1.8e-5          # sea level ~15-25 C (EST)
BOX = (1.25, 0.55, 0.45)                  # old CLAUDE.md car box, m (root CLAUDE.md of K09-L)

SRC = {
 "MN3110": "https://store.tmotor.com/goods.php?id=334 (T-Motor Navigator MN3110, KV700 14.8 V 12x4 CF table), read 2026-11-14",
 "MN2212": "https://store.tmotor.com/goods.php?id=388 (T-Motor MN2212 V2.0 KV780, 14.8 V 9545B table), read 2026-11-14",
 "pack":   "https://chinahobbyline.com CNHL G+ 3000 mAh 4S 70C XT90 $36.99 (search snippet 2026-11-14, U); 356 g from RESTUDY-2026-11-14.md B",
 "prop":   "APC 12x4.5MR $4.49 getfpv.com (search snippet 2026-11-14, U)",
}

# ------------------------------------------------------------------ published data (PUB)
# MN3110 KV700, 14.8 V, T-Motor 12x4 CF: (throttle %, A, W, thrust g)   [store.tmotor.com/goods.php?id=334]
MN3110 = [(50, 3.2, 47.36, 420), (65, 6.2, 91.76, 790), (75, 8.5, 125.80, 930), (85, 11.6, 171.68, 1190), (100, 14.0, 207.20, 1290)]
MN3110_SPEC = dict(mass_g=99, imax_cont=21.0, pmax_w=466, rint_ohm=0.092, price=61.90)       # PUB (99 g incl. cables)
# MN2212 V2.0 KV780, 14.8 V, 9545B: 100 % = 10.3 A, 152.44 W, 918 g static   [store.tmotor.com/goods.php?id=388]
MN2212_SPEC = dict(mass_g=65, imax_cont=13.0, a_full=10.3, w_full=152.44, thrust_static_g=918, price=46.90)  # PUB (65 g incl. cables)

def interp(x, xs, ys):
    if x <= xs[0]: return ys[0]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            return ys[i-1] + (ys[i]-ys[i-1])*(x-xs[i-1])/(xs[i]-xs[i-1])
    return ys[-1]

TH = [r[3] for r in MN3110]; PW = [r[2] for r in MN3110]; AM = [r[1] for r in MN3110]; TP = [r[0] for r in MN3110]

PACK_G = 356
# ------------------------------------------------------------------ inputs (EST unless noted)
PROP_DERATE = 0.95        # EST: APC 12x4.5MR in place of the T-Motor 12x4 CF used in the table; bench test replaces it
ESC_EFF, CTRL_MARGIN = 0.94, 1.10   # EST; +10 % control margin as RESTUDY / E2 practice
USABLE, RESERVE = 0.90, 0.20        # RESTUDY basis (usable pack fraction EST; 20 % reserve from A2.md)
AV_W = 10.0               # EST: FC + GPS + RX + airspeed + 4 servos average, W
# structure geometry
SPAN, CHORD = 1.20, 0.25
S = SPAN*CHORD; AR = SPAN**2/S
TC = 0.12                 # Clark-Y thickness ratio (EST airfoil data, not cited)
CLMAX = 1.10              # EST, Clark Y-like section at Re ~2e5 with 3-D / foam-surface loss
E_OSW = 0.80              # EST span efficiency
SH, SV = 0.045, 0.030     # tail areas, m2 (EST)
ARM_MOTOR = 0.32          # motor x offset from motor centroid, m
BOOM_Y = 0.25             # lateral boom position, m
D_LIFT = 12*0.0254; D_PUSH = 9*0.0254

# mass table: (subsystem, item, grams, position function of geometry g [m, body frame, aft +], basis)
# geometry g: d = wing AC, xc = CG = lift-motor centroid, xp = pusher plane, xt = tail AC; nose bay at X_NOSE
X_NOSE, X_PACK = -0.30, -0.25
def mass_table():
    return [
     ("wing/fuse/booms/tail", "wing 1.20x0.25 foam core + CF spar + ailerons (2 panels, plug-in joiner)", 360, lambda g: g["d"], "EST; RESTUDY B 330 g + 30 g joiner"),
     ("wing/fuse/booms/tail", "fuselage pod 0.88 m, foam board / EPP", 140, lambda g: (X_NOSE+g["xp"])/2, "EST; RESTUDY B 120 g, longer pod"),
     ("wing/fuse/booms/tail", "2 CF booms 16 mm x ~1.1 m + blocks + motor mounts", 130, lambda g: (g["xc"]-ARM_MOTOR-0.03+g["xt"]+0.05)/2, "EST; RESTUDY B 120 g + mounts"),
     ("wing/fuse/booms/tail", "tail: H-stab 0.045 m2 + 2 fins 0.030 m2, foam", 60, lambda g: g["xt"], "EST; RESTUDY B"),
     ("lift propulsion", "4 x T-Motor MN3110 KV700 (99 g with cable)", 4*99, lambda g: g["xc"], "PUB (store.tmotor.com 2026-11-14)"),
     ("lift propulsion", "4 x ESC 30-45 A (10 g)", 40, lambda g: g["xc"], "EST; RESTUDY"),
     ("lift propulsion", "4 x APC 12x4.5MR (18 g)", 72, lambda g: g["xc"], "EST"),
     ("cruise propulsion", "MN2212 V2.0 KV780 (65 g with cable)", 65, lambda g: g["xp"], "PUB (store.tmotor.com 2026-11-14)"),
     ("cruise propulsion", "ESC 25 A + 9x6 prop + mount", 40, lambda g: g["xp"], "EST"),
     ("pack", "4S 3000 mAh LiPo", PACK_G, lambda g: X_PACK, "listing 356 g (RESTUDY B)"),
     ("avionics", "FC, GPS, RX, airspeed + pitot", 62, lambda g: -0.15, "EST"),
     ("avionics", "4 servos + linkage (2 in wing, 2 at tail)", 56, lambda g: (g["d"]+g["xt"])/2, "EST; RESTUDY B 60 g"),
     ("harness", "power leads XT90, 4-way lift distribution, BEC, signal wire", 70, lambda g: g["xc"], "EST"),
     ("landing gear", "4 printed PETG feet on boom motor mounts + skid", 60, lambda g: g["xc"], "EST"),
    ]
CONT = 0.10

ROWS = mass_table()
M_NP = sum(r[2] for r in ROWS if r[0] != "pack")*(1+CONT)
M = (M_NP + PACK_G)/1000.0
W = M*G
a_ratio, eta_t, deps = 0.70, 0.90, 0.40     # EST: a_t/a_w, tail efficiency, d(eps)/d(alpha)
TAIL_GAP = 0.03

def geometry(d):
    """solve xc (CG = lift-motor centroid) for wing AC at d; pusher plane xp and tail AC xt follow from xc."""
    xc = 0.0
    for _ in range(80):
        xp = xc + ARM_MOTOR + D_LIFT/2 + TAIL_GAP
        g = dict(d=d, xc=xc, xp=xp, xt=xp + 0.18)
        mom = sum(r[2]*((1+CONT) if r[0] != "pack" else 1)*r[3](g) for r in ROWS)
        xn = mom/(M*1000)
        if abs(xn-xc) < 1e-10: break
        xc = xn
    xp = xc + ARM_MOTOR + D_LIFT/2 + TAIL_GAP
    g = dict(d=d, xc=xc, xp=xp, xt=xp + 0.18)
    kk = eta_t*a_ratio*(SH/S)*(1-deps)
    lt = g["xt"] - d
    x_np = d + kk*lt/(1+kk)
    g.update(kk=kk, lt=lt, x_np=x_np, sm=(x_np-xc)/CHORD)
    return g

def solve_wing(sm_target=0.12):
    lo, hi = -0.2, 0.6
    for _ in range(80):
        mid = (lo+hi)/2
        if geometry(mid)["sm"] < sm_target: lo = mid
        else: hi = mid
    return geometry((lo+hi)/2)

GEO = solve_wing(0.12)

# ------------------------------------------------------------------ MISSION (A2.md s2.1, adapted)
V_CRUISE = 17.0
BANK = math.radians(30)
R_TURN = V_CRUISE**2/(G*math.tan(BANK))
LAP = 2*300 + 2*math.pi*R_TURN
T_CRUISE = 15 + 2*LAP/V_CRUISE + LAP/V_CRUISE + 0.5*LAP/V_CRUISE      # settle 15 s + 2 laps + go-around lap + half-lap run-in
T_HOVER = 25 + 35 + 50 + 30 + 40          # A2.md: climb 25, hold 35 (EST), descent 50, land 30, go-around 40 = 180 s
# QUADPLANE ADAPTATION (basis): same hover-mode total 180 s kept (conservative: no pitch-over, but VTOL climb/descent/landing
# and the go-around are unchanged); cruise speed 17 m/s kept (the racetrack, 30 deg bank R=51 m, is speed-driven, not config-driven);
# forward transition 12 s lift motors at 60 % hover power + pusher full (EST); back transition 12 s at 60 % hover power (EST).
T_TRANS = 12.0

# ------------------------------------------------------------------ wing / aero
def cf_turb(re): return 0.455/(math.log10(re)**2.58)
def cf_lam(re): return 1.328/math.sqrt(re)
def cf_mixed(re, xtr=0.25): return xtr*cf_lam(re)*0 + (1-xtr)*cf_turb(re) + xtr*min(cf_lam(re), cf_turb(re))   # EST blend

def drag_buildup(V):
    q = 0.5*RHO*V**2
    rec = RHO*V*CHORD/MU
    cfw = cf_mixed(rec)
    ff_w = 1 + 2*TC + 60*TC**4
    swet_w = 2.04*S
    fus_l, fus_p = 0.70, 0.34                       # EST pod 0.70 m long, perimeter 0.34 m
    cff = cf_turb(RHO*V*fus_l/MU)
    boom_l = 2*1.11; boom_d = 0.016
    cfb = cf_turb(RHO*V*1.11/MU)
    comps = {}
    comps["wing"] = cfw*ff_w*swet_w
    comps["fuselage"] = cff*1.25*fus_l*fus_p
    comps["booms (2)"] = cfb*1.20*boom_l*math.pi*boom_d
    comps["tail (H + 2 fins)"] = cf_turb(RHO*V*0.09/MU)*1.20*2*(SH+SV)*1.0
    comps["4 stopped lift props"] = 4*0.0012          # EST CdA per stopped 12 in prop
    comps["4 motor nacelles"] = 4*0.0003              # EST CdA each
    comps["pusher + mount, gear feet, antennas"] = 0.0012 + 4*0.0001 + 0.0002   # EST
    sub = sum(comps.values())
    comps["interference / gaps / trim (+10 %)"] = 0.10*sub
    return comps, sum(comps.values())/S, q

def drag_at(V, n=1.0):
    comps, cd0, q = drag_buildup(V)
    cl = n*W/(q*S)
    k = 1/(math.pi*E_OSW*AR)
    cd = cd0 + k*cl**2
    return q*S*cd, cl, cd, cd0, k, comps

def pusher_thrust_avail(V, eta_tot=0.45):
    """Thrust at speed V from the published full-throttle electrical power (152 W) x EST overall efficiency (motor x ESC x prop)."""
    return eta_tot*MN2212_SPEC["w_full"]/V

# ------------------------------------------------------------------ lift system
def hover_motor(T_total_g):
    """per-motor electrical W and A at 14.8 V for per-motor thrust (table thrust needed = T/derate)."""
    t = T_total_g/4/PROP_DERATE
    return interp(t, TH, PW), interp(t, TH, AM), interp(t, TH, TP)

R_PACK = 0.045                     # EST: 4S 3000 mAh 70C ~ 0.035 + wiring/ESC/connectors 0.010 ohm
V_OCV_FRESH, V_OCV_LOW = 16.6, 14.9   # EST open-circuit: 4.15 V/cell fresh, 3.72 V/cell at ~20 % SoC

def tw_state(v_ocv):
    """max total thrust at full throttle with pack sag solved (thrust ~ V^2, current ~ V^2 about the 14.8 V table row)."""
    v = v_ocv
    for _ in range(60):
        i_m = MN3110[-1][1]*(v/14.8)**2
        v = v_ocv - R_PACK*4*i_m
    t_m = MN3110[-1][3]*PROP_DERATE*(v/14.8)**2
    return 4*t_m/1000.0, v, i_m

# ------------------------------------------------------------------ main
def main():
    out = []
    P = out.append
    # ---- mass
    P("## 1 Mass\n")
    P("| Subsystem | g | Items |\n|---|---|---|")
    sub = {}
    for s_, it, g, _f, b in ROWS:
        sub.setdefault(s_, []).append((it, g, b))
    tot0 = 0
    for s_, lst in sub.items():
        g = sum(l[1] for l in lst); tot0 += g
        P(f"| {s_} | {g} | " + "; ".join(f"{l[0]} {l[1]} g ({l[2]})" for l in lst) + " |")
    P(f"| contingency 10 % of non-pack mass (fasteners, glue, paint, EST) | {0.10*(tot0-PACK_G):.0f} | |")
    P(f"| **MTOW** | **{M*1000:.0f}** | {M:.3f} kg, W = {W:.1f} N |\n")

    # ---- mission-time basis
    P("## 2 Mission basis\n")
    P(f"- racetrack: V {V_CRUISE} m/s, 30 deg bank, R = {R_TURN:.1f} m, lap {LAP:.1f} m = {LAP/V_CRUISE:.1f} s; cruise segment {T_CRUISE:.1f} s = {T_CRUISE/60:.2f} min (requirement 3.5 min)")
    P(f"- hover-mode time {T_HOVER} s = {T_HOVER/60:.1f} min (A2.md s2.1: 25 + 35 + 50 + 30 + 40); forward and back transitions {T_TRANS:.0f} s each (EST)\n")

    # ---- wing
    P("## 3 Wing and aero (EST)\n")
    vs = math.sqrt(2*W/(RHO*S*CLMAX))
    P(f"- span {SPAN} m, chord {CHORD} m, S = {S:.3f} m2, AR = {AR:.2f}, loading {M/S:.2f} kg/m2 ({W/S:.1f} N/m2), airfoil Clark Y-like 12 % (flat bottom, hot-wire cut), CLmax {CLMAX} EST")
    P(f"- stall Vs = {vs:.2f} m/s; 1.3 Vs = {1.3*vs:.1f} m/s; Vs in 30 deg turn = {vs*math.sqrt(1/math.cos(BANK)):.1f} m/s")
    D, cl, cd, cd0, k, comps = drag_at(V_CRUISE)
    P(f"- cruise {V_CRUISE} m/s: CL = {cl:.3f}, CD0 = {cd0:.4f}, k = {k:.4f}, CD = {cd:.4f}, **L/D = {cl/cd:.1f}**, drag {D:.2f} N ({D/G*1000:.0f} gf)")
    P("\n| Drag item (CdA m2) | value |\n|---|---|")
    for kk, vv in comps.items(): P(f"| {kk} | {vv:.5f} |")
    best = max(((drag_at(v)[1]/drag_at(v)[2], v) for v in [x/2 for x in range(16, 50)]))
    P(f"\n- best L/D {best[0]:.1f} at {best[1]:.1f} m/s (EST)\n")

    # ---- lift system
    P("## 4 Lift system\n")
    P(f"- motors: 4 x T-Motor MN3110 KV700, 4S, APC 12x4.5MR (D = {D_LIFT:.3f} m). Table (PUB, T-Motor 12x4 CF at 14.8 V): 100 % = {MN3110[-1][3]} g, {MN3110[-1][1]} A, {MN3110[-1][2]} W per motor; derate {PROP_DERATE} EST for the APC prop (bench test replaces it)")
    tw_f, v_f, i_f = tw_state(V_OCV_FRESH)
    tw_s, v_s, i_s = tw_state(V_OCV_LOW)
    P(f"- fresh (OCV {V_OCV_FRESH} V, R {R_PACK} ohm EST): loaded {v_f:.1f} V, {i_f:.1f} A per motor, thrust {tw_f:.2f} kgf, **T/W = {tw_f/M:.2f}** (limit >= 2.0)")
    P(f"- at sag (OCV {V_OCV_LOW} V, about 20 % SoC): loaded {v_s:.1f} V, {i_s:.1f} A, thrust {tw_s:.2f} kgf, **T/W = {tw_s/M:.2f}** (limit >= 1.6)")
    pw, am, tm = hover_motor(M*1000)
    P(f"- hover per motor: {M*1000/4:.0f} g needs table {M*1000/4/PROP_DERATE:.0f} g -> {pw:.0f} W, {am:.1f} A (about {interp(M*1000/4/PROP_DERATE, TH, TP):.0f} % throttle); total 4 motors {4*pw:.0f} W motor, "
      f"{4*pw/ESC_EFF*CTRL_MARGIN:.0f} W pack incl. ESC {ESC_EFF} and +10 % control margin; pack current {4*pw/ESC_EFF*CTRL_MARGIN/14.8:.1f} A ({4*pw/ESC_EFF*CTRL_MARGIN/14.8/3.0:.1f} C)")
    P(f"- current limits: motor max {i_f:.1f} A fresh vs {MN3110_SPEC['imax_cont']} A continuous (180 s) rating (PUB) = {100*i_f/MN3110_SPEC['imax_cont']:.0f} %; {4*i_f:.0f} A pack peak vs 70C x 3 Ah = 210 A; ESC 30-45 A part >= {i_f:.0f} A with margin")
    p_tot_sag_hover = 4*pw/ESC_EFF*CTRL_MARGIN
    # geometry
    xm_gap_same_boom = 2*ARM_MOTOR - D_LIFT
    lat_gap = 2*BOOM_Y - D_LIFT
    P(f"- geometry: motors at +/-{ARM_MOTOR} m fore/aft of the motor centroid, booms at y = +/-{BOOM_Y} m; boom length {GEO['xt']+0.05-(GEO['xc']-ARM_MOTOR-0.03):.2f} m")
    P(f"  - prop tip gap on one boom {xm_gap_same_boom:.3f} m ({xm_gap_same_boom/D_LIFT:.2f} D); across booms (same station) {lat_gap:.3f} m ({lat_gap/D_LIFT:.2f} D)")
    P(f"  - pusher disc (R {D_PUSH/2:.3f}) sits {GEO['xp']-GEO['xc']-ARM_MOTOR-D_LIFT/2:.3f} m behind the rear lift discs; clear of lift discs in plan (x gap)\n")

    # ---- CG / SM
    P("## 5 CG and static margin (EST)\n")
    g = GEO; d = g["d"]
    vh = SH*g["lt"]/(S*CHORD); vv = SV*g["lt"]/(S*SPAN)
    P(f"- body frame, aft +, nose bay at {X_NOSE} m. Solved: wing AC at x = {d:.3f} m, CG = motor centroid = {g['xc']:.3f} m, pusher plane {g['xp']:.3f} m, tail AC {g['xt']:.3f} m; pack at {X_PACK} m (nose bay, slides +/-60 mm)")
    P(f"- tail arm {g['lt']:.2f} m, S_H/S = {SH/S:.2f}, V_H = {vh:.2f}, V_V = {vv:.3f} (typical light-aircraft values 0.4-0.6 / 0.02-0.05, EST)")
    P(f"- neutral point {1000*(g['x_np']-d):.0f} mm aft of wing AC (tail k = {g['kk']:.3f}; a_t/a_w {a_ratio}, eta_t {eta_t}, 1-de/da {1-deps}, all EST); CG {1000*(g['xc']-d):+.0f} mm from AC = {(0.25+(g['xc']-d)/CHORD)*100:.0f} % chord")
    P(f"- **static margin {g['sm']*100:.1f} % chord** (design 12 %; 5-15 % is the usual range for a stable light aircraft, EST)")
    xf_edge = g['xc']-ARM_MOTOR+D_LIFT/2; xr_edge = g['xc']+ARM_MOTOR-D_LIFT/2
    le, te = d-0.25*CHORD, d+0.75*CHORD
    P(f"- hover geometry: front disc trailing edge {1000*(le-xf_edge):+.0f} mm ahead of wing LE; rear disc leading edge {1000*(te-xr_edge):+.0f} mm (positive = disc overlaps wing TE)")
    for dx in (-0.06, 0.0, 0.06):
        xc2 = (g['xc']*M*1000 + PACK_G*dx)/(M*1000)
        P(f"  - pack {dx*1000:+.0f} mm: CG {1000*(xc2-g['xc']):+.0f} mm from hover centroid, SM = {(g['x_np']-xc2)/CHORD*100:.1f} %")
    P(f"- overall length {g['xt']+0.05-X_NOSE:.2f} m (nose to boom end), pod {g['xp']-X_NOSE:.2f} m\n")
    lt = g['lt']

    # ---- cruise pusher
    P("## 6 Cruise pusher (EST dynamic, PUB static)\n")
    P(f"- MN2212 V2.0 KV780 + 9x6 prop, 4S: PUB full throttle {MN2212_SPEC['a_full']} A, {MN2212_SPEC['w_full']} W, {MN2212_SPEC['thrust_static_g']} g static (9545B prop; 9x6 static is lower, EST), rating {MN2212_SPEC['imax_cont']} A continuous")
    Tc = D
    ETA_C = 0.45
    ta = pusher_thrust_avail(V_CRUISE, ETA_C)
    P(f"- cruise thrust needed {Tc:.2f} N ({Tc/G*1000:.0f} gf); available at {V_CRUISE} m/s = {ETA_C} x {MN2212_SPEC['w_full']} W / V = {ta:.2f} N")
    roc = (ta - Tc)*V_CRUISE/W
    gamma = math.degrees(math.asin(min(1, roc/V_CRUISE)))
    P(f"- climb: excess {ta-Tc:.2f} N -> rate of climb {roc:.2f} m/s ({gamma:.1f} deg)")
    p_rated = MN2212_SPEC['imax_cont']*14.8
    ta_r = ETA_C*p_rated/V_CRUISE
    roc_r = (ta_r - Tc)*V_CRUISE/W
    P(f"- climb at the 13 A continuous rating ({p_rated:.0f} W, PUB rating, 180 s): thrust {ta_r:.2f} N, rate of climb {roc_r:.2f} m/s; lift motors add Q_ASSIST in any climb below Vs")
    p_cr = Tc*V_CRUISE/ETA_C
    P(f"- cruise electrical power {p_cr:.0f} W = {p_cr/14.8:.1f} A ({100*p_cr/14.8/MN2212_SPEC['imax_cont']:.0f} % of 13 A rating)")
    t_turn = drag_at(V_CRUISE, 1/math.cos(BANK))[0]
    P(f"- turn (n = {1/math.cos(BANK):.3f}): drag {t_turn:.2f} N, power {t_turn*V_CRUISE/ETA_C:.0f} W")
    # transition accel
    a_tr = (ta*0 + MN2212_SPEC['thrust_static_g']*0.85/1000*G - drag_at(8)[0])/M
    P(f"- transition: 0 to ~12 m/s with static thrust EST {0.85*MN2212_SPEC['thrust_static_g']:.0f} g -> a = {a_tr:.1f} m/s2, {12/a_tr:.1f} s (lift motors assist, Q_ASSIST)\n")

    # ---- energy
    P("## 7 Energy and pack (EST)\n")
    f_turn = 2*math.pi*R_TURN/LAP
    p_cruise_avg = ((1-f_turn)*Tc + f_turn*t_turn)*V_CRUISE/ETA_C + AV_W
    p_h = p_tot_sag_hover + AV_W
    p_ft = 0.60*p_tot_sag_hover + MN2212_SPEC['w_full'] + AV_W
    p_bt = 0.60*p_tot_sag_hover + AV_W
    e = (p_h*T_HOVER + p_ft*T_TRANS + p_cruise_avg*T_CRUISE + p_bt*T_TRANS)/3600
    need = e/(1-RESERVE)/USABLE
    P("| Segment | s | W (pack) | Wh |\n|---|---|---|---|")
    for nm, t, p in (("hover-mode (VTOL climb, hold, descent, landing, go-around)", T_HOVER, p_h),
                     ("forward transition", T_TRANS, p_ft), ("cruise (turn fraction %.0f %%)" % (100*f_turn), T_CRUISE, p_cruise_avg),
                     ("back transition", T_TRANS, p_bt)):
        P(f"| {nm} | {t:.0f} | {p:.0f} | {p*t/3600:.2f} |")
    P(f"| **mission** | {T_HOVER+2*T_TRANS+T_CRUISE:.0f} | | **{e:.1f}** |")
    P(f"\n- need = {e:.1f} / (1 - {RESERVE}) / {USABLE} = **{need:.1f} Wh**; 4S 3000 mAh = {4*3.7*3.0:.1f} Wh nominal -> margin {4*3.7*3.0/need:.2f}x ({100*(4*3.7*3.0*USABLE*(1-RESERVE)-e)/e:.0f} % spare energy over mission)")
    e22 = 4*3.7*2.2
    P(f"- 4S 2200 mAh alternative: {e22:.1f} Wh, margin {e22/need:.2f}x, mass about {(245-356)} g (245 g EST); not chosen (margin {e22/need:.2f}x on an EST energy)")
    P("- two packs: one flies, one charges (HTRC C150 150 W charges 3 Ah at 1C in about 60 min, EST); a third pack is not budgeted\n")

    # ---- cost check
    P("## 8 Rough cost check against RESTUDY B ($1,625 total, spend $1,475 + crash reserve $150)\n")
    TAX, SHIP = 0.1025, 10.71
    mine = [
     ("T-Motor MN3110 KV700 x 5 (4 + 1 spare)", "T-Motor", 5, 61.90, "store.tmotor.com/goods.php?id=334 2026-11-14; resellers $61.90-90.90 (U)"),
     ("T-Motor MN2212 V2.0 KV780 x 1", "T-Motor", 1, 46.90, "store.tmotor.com/goods.php?id=388 2026-11-14"),
     ("LANRC 45 A ESC 4-pack x 2", "Amazon", 2, 30.00, "RESTUDY B (U)"),
     ("APC 12x4.5MR x 8 (4 + 4 spare, CW/CCW per rotation)", "APC", 8, 4.49, "getfpv.com snippet 2026-11-14 (U)"),
     ("APC 9x6 pusher x 3", "APC", 3, 3.80, "RESTUDY B (EST)"),
     ("CNHL 4S 3000 mAh 70C XT90 x 2", "chinahobbyline", 2, 36.99, "chinahobbyline snippet 2026-11-14 (U)"),
     ("Foam, tape, glue, tail foam board", "Home Depot", 1, 80.00, "RESTUDY B (EST)"),
     ("CF tubes: 2 booms 1.11 m, spar, joiner", "Aloft Hobbies", 1, 75.00, "RESTUDY B (EST)"),
     ("2 more servos", "GetFPV", 2, 14.99, "RESTUDY B (U)"),
     ("PETG 1 kg + hardware", "West3D", 1, 46.00, "RESTUDY B (EST)"),
    ]
    resB = [180.00, 60.00, 49.40, 84.00, 80.00, 75.00, 29.98, 46.00]   # RESTUDY B lines, restudy_cost.py C["B"]
    gm = sum(q*u for _, _, q, u, _ in mine); gb = sum(resB)
    delta = (gm-gb)*(1+TAX)
    P("| Item | Qty | $ ea | $ | Source |\n|---|---|---|---|---|")
    for it, v, q, u, s_ in mine: P(f"| {it} | {q} | {u:.2f} | {q*u:.2f} | {s_} |")
    P(f"| **Parts goods** | | | **{gm:.2f}** | RESTUDY B parts goods {gb:.2f} |")
    P(f"\n- delta pre-tax {gm-gb:+.2f}, with tax 10.25 % {delta:+.2f}; vendor count unchanged (shipping $10.71 per vendor, T-Motor international shipping may be higher: -)")
    tot = 1625 + delta
    P(f"- **total {tot:,.0f} against 2,000 -> margin {2000-tot:,.0f}** (RESTUDY B: 1,625 / +375; its own rule +$100 minimum margin)")
    P("- prices are `U` or `EST`; the largest swing is the 5 MN3110 ($309.50, resellers up to $90.90 each = +$145)\n")

    # ---- box
    P("## 9 Transport box\n")
    P(f"- box {BOX[0]} x {BOX[1]} x {BOX[2]} m. Assembled airframe (props off) : booms span 1.08 m, overall length {GEO["xt"]+0.05-X_NOSE:.2f} m, width {2*BOOM_Y+0.03:.2f} m, height about 0.25 m with fins -> fits.")
    P(f"- span {SPAN} m wing does not fit with the body in one rigid piece: a rigid cross of {SPAN} x {GEO['xt']+0.05-X_NOSE:.2f} m cannot fit a 1.25 x 0.55 footprint at any yaw angle (rotate check below).")
    ok = False
    for th in [i*0.5 for i in range(0, 181)]:
        t_ = math.radians(th)
        L_ = GEO['xt']+0.05-X_NOSE; w1 = SPAN*abs(math.cos(t_)) + L_*abs(math.sin(t_)); w2 = SPAN*abs(math.sin(t_)) + L_*abs(math.cos(t_))
        if w1 <= BOX[0] and w2 <= BOX[1]: ok = True
    P(f"  - rotate check (any angle): {'fits' if ok else 'does NOT fit'}")
    P("- baseline therefore: the two wing panels unplug at the spar (tool-less) and travel beside the airframe: DEVIATION from strict one-piece, flagged in the report; a detachable wing is the span limit driver: each panel <= box length 1.25 m, spar tube length and the stack height 0.45 m.")
    print("\n".join(out))
    # summary line
    print(f"\nSUMMARY mass {M:.3f} kg | span {SPAN} | S {S:.3f} | T/W {tw_f/M:.2f} fresh {tw_s/M:.2f} sag | Vs {vs:.1f} | L/D {cl/cd:.1f} | cruise {p_cr:.0f} W | mission {e:.1f} Wh need {need:.1f} | cost {tot:,.0f}")

if __name__ == "__main__":
    main()
