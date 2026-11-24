"""Candidate A (scaled quad tailsitter) sizing, round QP-1, 2026-11-14.
Reproduce: python -I redesign/qp/sizing_A/sizing_a.py   (stdlib only; prints markdown; writes nothing)

Labels: V = vendor page read 2026-11-14; U = unverified (search snippet / aggregator);
EST = engineering estimate; "-" = unknown.  Every EST is a named constant below so it can be changed.
Scaled from the K09-L closure round (redesign/review/CLOSURE-ROUND-2026-11-14: B3, E1, C4, C5, A3).
"""
import math
G, RHO, NU = 9.81, 1.20, 1.5e-5

# ------------------------------------------------------------------ published motor data (V)
# T-Motor MN2212 V2.0 KV780, 14.8 V, T-MOTOR 9545B prop; https://store.tmotor.com/goods-388-MN2212-V20.html (read 2026-11-14)
TAB_THR = [293, 476, 605, 742, 918]            # g
TAB_P   = [31.08, 59.2, 82.88, 109.52, 152.44] # W
TAB_I   = [2.1, 4.0, 5.6, 7.4, 10.3]           # A
V_TAB = 14.8
MOTOR = dict(name="T-Motor MN2212 V2.0 KV780", mass_g=65.0,  # 55 g bare, 65 g with cables (same page)
             rating_a=13.0, price=46.90)       # 13 A max continuous / 180 s, 200 W; no burst rating (-)

def interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0] * x / xs[0]               # EST: linear to the origin below the first row
    for i in range(1, len(xs)):
        if x <= xs[i]:
            return ys[i-1] + (ys[i]-ys[i-1]) * (x-xs[i-1])/(xs[i]-xs[i-1])
    return ys[-1]

# ------------------------------------------------------------------ design inputs (EST unless noted)
S_WING, SPAN, CHORD = 0.22, 0.90, 0.245   # RESTUDY A planform
CLMAX = 0.75      # EST trimmed flying-wing CLmax (K09-L B3 Vs 12.01 m/s at S 0.345 implies ~0.85; RESTUDY used 0.70)
E_OSW = 0.80      # EST Oswald
CD0_PARTS = dict(motors=4*0.8*math.pi*0.0275**2/4/S_WING, mounts_struts=0.004, gear_misc=0.002)   # EST
FIN_H, FIN_C = 0.36, 0.12     # fin height (= stance width in hover) and chord, m (design choice)
PROP_D = 9.5*0.0254
CANT_DEG = 14.0   # design value here; K09-L used 10 deg (B3 D-163), which gives ratio 1.24 on this airframe (see sweep)
DOWNLOAD = 0.03   # EST thrust loss, wing/fins in slipstream
SAG_V_CELL, R_PACK = 3.6, 0.030   # EST pack internal R, ohm (maker value -)
THERMAL = 0.97    # EST hot-winding thrust loss
CTRL_MARGIN = 1.10  # hover power margin (RESTUDY / E2 practice)
Y_M, Z_M = 0.19, 0.13   # motor grid half-spacings (lateral, cruise-vertical), m: prop tip clearance 0.019 m (design choice)

# (item, g, x aft of wing LE in cruise attitude [m], source)
MASSES = [
 ("wing: foam + CF spar + 2 elevons (0.90 x 0.245)", 220, 0.095, "EST (RESTUDY wing+fins 260)"),
 ("2 fins 0.36 x 0.12 (foam/glass) with foot pads", 36, 0.24, "EST"),
 ("4 x T-Motor MN2212 V2.0 KV780 (with cables)", 260, -0.040, "V: 65 g each, store.tmotor.com 2026-11-14"),
 ("4 x T9545 props", 32, -0.085, "EST 8 g each"),
 ("4 x 45 A ESC", 40, 0.050, "EST 10 g each (RESTUDY)"),
 ("1 x 4S 2000 mAh CNHL 100C pack (in the motor cage, between the pairs)", 232, -0.020, "U: 232 g listed (RaceDayQuads / WREKD, search 2026-11-14)"),
 ("FC + GPS + RX + airspeed + wiring", 110, 0.060, "EST (RESTUDY)"),
 ("2 servos + linkage", 30, 0.200, "EST (RESTUDY)"),
 ("motor mounts / X cage, printed + CF tube", 120, -0.020, "EST (RESTUDY 120)"),
 ("hardware, tape, paint", 35, 0.100, "EST (RESTUDY)"),
]
CONTINGENCY = 0.10      # RESTUDY
PACK_WH, PACK_MAH = 2.0*14.8, 2000
FOOT_X = 0.30           # fin foot aft of LE


def mass():
    base = sum(m for _, m, _, _ in MASSES)
    return base, base*(1+CONTINGENCY)/1000.0


def box_fit():
    """Bounding box in cruise attitude vs 1.25 x 0.55 x 0.45 m (CLAUDE.md)."""
    length = 0.085 + 0.05 + FOOT_X + 0.0      # prop disk (0.085 ahead of LE) + 0.05 prop clearance.. to fin foot
    length = 0.085 + FOOT_X
    z_props = 2*(Z_M + PROP_D/2); z_noprop = 2*Z_M + 0.03
    rows = []
    for lab, z in (("props on", max(z_props, FIN_H)), ("props off", max(z_noprop, FIN_H))):
        dims = sorted([SPAN, z, length], reverse=True)
        box = [1.25, 0.55, 0.45]
        rows.append((lab, dims, [b-d for d, b in zip(dims, box)], all(d <= b for d, b in zip(dims, box))))
    return rows, length


def wing(m):
    W = m*G; AR = SPAN**2/S_WING
    vs = math.sqrt(2*W/(RHO*S_WING*CLMAX)); vc = 15.0
    q = 0.5*RHO*vc**2; cl = W/(q*S_WING); re = vc*CHORD/NU
    cf = 0.074/re**0.2
    cd0_wing = cf*2.04*1.2
    cd0_fin = cf*2*(2*FIN_H*FIN_C)*1.2/S_WING
    cd0 = cd0_wing + cd0_fin + sum(CD0_PARTS.values())
    cdi = cl**2/(math.pi*AR*E_OSW)
    ld = cl/(cd0+cdi)
    return dict(W=W, AR=AR, wl=W/S_WING, vs=vs, v13=1.3*vs, vc=vc, cl=cl, re=re, cd0=cd0, cd0_wing=cd0_wing,
                cd0_fin=cd0_fin, cdi=cdi, ld=ld, drag=W/ld)


def propulsion(m):
    W = m*G; cc = math.cos(math.radians(CANT_DEG))
    t_each = W/4/cc/(1-DOWNLOAD)/G*1000
    p_h = interp(t_each, TAB_THR, TAB_P); i_h = interp(t_each, TAB_THR, TAB_I)
    fresh_g = TAB_THR[-1]*cc*(1-DOWNLOAD)             # table 14.8 V, 100 %: no credit for 16.8 V
    v_sag = 4*SAG_V_CELL - 4*TAB_I[-1]*R_PACK
    sag_g = TAB_THR[-1]*(v_sag/V_TAB)**2*THERMAL*cc*(1-DOWNLOAD)
    i_full_fresh = TAB_I[-1]*(16.8/V_TAB)**2          # EST: current at full duty ~ V^2 (rpm ~ V, torque ~ rpm^2)
    A = math.pi*(PROP_D/2)**2
    p_ideal = (t_each*G/1000)**1.5/math.sqrt(2*RHO*A)
    return dict(t_each=t_each, p_h_each=p_h, i_h_each=i_h, p_hover=4*p_h*CTRL_MARGIN,
                tw_fresh=4*fresh_g/1000/m, tw_sag=4*sag_g/1000/m, v_sag=v_sag,
                i_full_fresh=i_full_fresh, spin_cap=min(1.0, math.sqrt(MOTOR["rating_a"]/i_full_fresh)),
                i_one_cap=i_full_fresh*0.90**2, fm_eta=p_ideal/p_h, i_hover_bat=4*i_h*CTRL_MARGIN,
                i_peak_bat=4*TAB_I[-1], ct_static=TAB_THR[-1]/1000*G/(RHO*(7350/60)**2*PROP_D**4))


def cruise_prop(wg, ct0, cp0, j0):
    """EST prop model: CT = CT0 (1-(J/J0)^2), CP = CP0 (1-0.65 J/J0).  Returns (shaft W/motor, eta_p, rpm, J)."""
    T = wg["drag"]/4
    for k in range(1, 2000):
        x = 0.30 + 0.699*k/2000
        J = x*j0; n = wg["vc"]/(J*PROP_D)
        if ct0*(1-x*x)*RHO*n*n*PROP_D**4 <= T:
            p = cp0*(1-0.65*x)*RHO*n**3*PROP_D**5
            return p, T*wg["vc"]/p, n*60, J
    return None


def mission(m, pr, wg, eta):
    hover_s, cruise_s = 180.0, 210.0
    p_tr = 4*interp(1.36*pr["t_each"], TAB_THR, TAB_P)*CTRL_MARGIN
    e_hover = pr["p_hover"]*hover_s/3600
    e_trans = 2*p_tr*10.0/3600
    e_climb = m*G*31/0.40/3600
    p_cr = wg["drag"]*wg["vc"]/eta
    e_cruise = p_cr*cruise_s/3600
    tot = e_hover+e_trans+e_climb+e_cruise
    return dict(e_hover=e_hover, e_trans=e_trans, e_climb=e_climb, p_cruise=p_cr, e_cruise=e_cruise, e_total=tot,
                need_wh=tot/0.80/0.90, usable=PACK_WH*0.90, reserve_frac=1-tot/(PACK_WH*0.90))


def hover_yaw(m, pr, cant=CANT_DEG, wind=5.0, ang=20.0, cd=2.05):
    """Wingtip into wind 20 deg off, wing as a plate (B3 ASM-B3-WTIP-CN, arm 0.25 b EST); authority at 30 % differential."""
    r = math.hypot(Y_M, Z_M); T = m*G/4
    n = math.sqrt(T/(RHO*pr["ct_static"]*PROP_D**4)); om = 2*math.pi*n
    q_each = pr["p_h_each"]*0.80/om                       # shaft = 0.80 x electrical (EST)
    m_cant = 4*0.30*T*math.sin(math.radians(cant))*r
    m_react = 4*0.30*q_each
    nf = 0.5*RHO*wind**2*S_WING*cd*math.sin(math.radians(ang))**2
    mw = nf*0.25*SPAN
    ix = 0.220*SPAN**2/12 + 4*0.065*r**2 + 2*0.018*(SPAN/2)**2   # EST, kg m2 about the vertical body axis
    auth = m_cant + m_react
    return dict(auth=auth, m_cant=m_cant, m_react=m_react, mw=mw, ratio=auth/mw, ratio_nocant=m_react/mw,
                ix=ix, acc=auth/ix, rpm=n*60, q_each=q_each, r=r, nf=nf)


def pitch_over(m, wg, t0w, vz0=0.0, rate_dps=12.0, theta_end=70.0, dt=0.005):
    """Point-mass pitch-over, wing as flat plate, thrust T0 along body axis held constant (B3 entry law). EST, low fidelity."""
    W = m*G; T = t0w*W
    cla = 2*math.pi*wg["AR"]/(2+math.sqrt(4+wg["AR"]**2)); als = math.radians(14); cd90 = 2.0
    th = 0.0; vx = 0.0; vz = vz0; z = 0.0; zmin = 0.0; t = 0.0
    while th < theta_end and t < 30:
        thr = math.radians(th)
        e = (math.sin(thr), math.cos(thr)); nrm = (math.cos(thr), -math.sin(thr))
        v = math.hypot(vx, vz)
        fx = fz = 0.0
        if v > 0.1:
            vc = vx*e[0]+vz*e[1]; vn = vx*nrm[0]+vz*nrm[1]
            a = math.atan2(vn, vc); q = 0.5*RHO*v*v*S_WING
            cn = cla*math.sin(a) if abs(a) <= als else cd90*math.sin(a)*0.75
            fn = q*cn; fa = -q*wg["cd0"]*(1.0 if vc >= 0 else -1.0)
            fx = -fn*nrm[0] + fa*e[0]; fz = -fn*nrm[1] + fa*e[1]
        vx += (T*e[0] + fx)/m*dt; vz += ((T*e[1] + fz)/m - G)*dt
        z += vz*dt; zmin = min(zmin, z); th += rate_dps*dt; t += dt
    return dict(t=t, vx=vx, vz=vz, zmin=zmin)


def entry_window(m, wg, pr):
    out = []
    for vz0 in (0.0, 4.0):
        low = None
        for k in range(60, 260):
            r = pitch_over(m, wg, k/100, vz0)
            if r["zmin"] > -3.0 and r["vx"] >= 1.1*wg["vs"]:
                low = k/100; break
        out.append((vz0, low))
    return out, 0.80*pr["tw_sag"]


def wind_and_tipover(m, wg, pr):
    W = m*G; res = {}
    for lab, v in (("5 m/s steady", 5.0), ("7 m/s (5 + 2 gust)", 7.0), ("8 m/s", 8.0)):
        f = 0.5*RHO*v*v*S_WING*2.0
        res[lab] = (f, math.degrees(math.atan2(f, W)), math.hypot(f, W)/W, math.hypot(f, W)/W/pr["tw_sag"])
    fk = 0.5*RHO*25*0.345*2.0
    k09_lean = math.degrees(math.atan2(fk, 2.6*G))
    xc = sum(mm*x for _, mm, x, _ in MASSES)/sum(mm for _, mm, _, _ in MASSES)
    h = FOOT_X - xc; half = FIN_H/2
    h_cp = FOOT_X - 0.5*CHORD
    f5 = 0.5*RHO*25*S_WING*2.0
    d = math.hypot(half, h)
    wind_k = (2.6*G*0.193)/(0.5*RHO*25*0.345*2.0*0.30)     # K09-L stance 0.193 m, CP height 0.30 m EST
    a = 1.2**2/(2*0.006)
    return res, k09_lean, dict(
        xc=xc, h=h, half=half, tip_static=math.degrees(math.atan2(half, h)), wind_ratio=W*half/(f5*h_cp),
        v_tip=math.sqrt(W*half/(0.5*RHO*S_WING*2.0*h_cp)), v_slide=math.sqrt(2*G*(d-h)), wind_k=wind_k,
        g_impact=a/G, f_impact=m*a, dl=W/(4*math.pi*(PROP_D/2)**2), dl_k09=2.6*G/(4*math.pi*(11*0.0254/2)**2),
        wl_k09=2.6*G/0.345)


def fin_vibration(rpm_fresh, rpm_sag):
    """Fin half as a cantilever (0.18 m): CFRP-skinned foam sandwich (EST laminate), first bending mode, root fixity 0.75-1."""
    L = FIN_H/2; b = FIN_C
    E, t, core = 50e9, 0.2e-3, 5e-3
    EI = 2*E*t*b*((core+t)/2)**2
    mu = b*(2*t*1600 + core*40)
    f_id = (1.875**2/(2*math.pi))*math.sqrt(EI/mu)/L**2
    res = {}
    for fix in (1.0, 0.85, 0.75):
        f1 = f_id*fix; worst = 9e9
        for rpm in (rpm_fresh, rpm_sag):
            for mult in (1, 2):
                fe = mult*rpm/60; worst = min(worst, abs(f1-fe)/fe)
        res[fix] = (f1, worst)
    return dict(EI=EI, mu=mu, f_id=f_id, res=res)


def cg_sm(pack_x=None):
    items = [(n, g, (pack_x if (pack_x is not None and "pack" in n) else x)) for n, g, x, _ in MASSES]
    tot = sum(g for _, g, _ in items); cg = sum(g*x for _, g, x in items)/tot
    ar = SPAN**2/S_WING; cla = 2*math.pi*ar/(2+math.sqrt(4+ar**2))
    a_w = cla*S_WING; a_p = 4*0.6*math.pi*(PROP_D/2)**2     # B4 BEMT slope 0.607 (K09-L) x Ribner k = 1, EST here
    np_ = (a_w*0.25*CHORD + a_p*(-0.085))/(a_w+a_p)
    np_v = np_ - 0.0033                                      # K09-L free-transition shift -4 mm scaled by chord, EST
    return dict(cg=cg, np=np_, np_v=np_v, sm=(np_v-cg)/CHORD, aft=np_v-0.05*CHORD, fwd=np_v-0.15*CHORD)


# ------------------------------------------------------------------ cost (RESTUDY basis, re-priced)
TAX, SHIP, FAA, BUDGET = 0.1025, 10.71, 5.0, 2000.0
FLOOR = [  # copied from redesign/config-study/restudy_cost.py FLOOR: (vendor, qty, unit); RESTUDY flags U / EST
 ("RadioMaster", 1, 69.99), ("RadioMaster", 1, 19.99), ("NewBeeDrone", 1, 51.99), ("RaceDayQuads", 1, 20.49),
 ("GetFPV", 1, 62.99), ("Amazon", 1, 22.00), ("GetFPV", 3, 14.99), ("Pyrodrone", 1, 59.99), ("Pyrodrone", 2, 9.99),
 ("Harbor Freight", 1, 19.99), ("Amazon", 1, 88.94), ("Amazon", 1, 60.99), ("Amazon", 1, 60.00)]
RESTUDY_A = [("ReadyMadeRC", 5, 30.00), ("Amazon", 2, 30.00), ("APC", 12, 3.50), ("Pyrodrone", 2, 38.00),
             ("Home Depot", 1, 70.00), ("Aloft Hobbies", 1, 40.00), ("West3D", 1, 21.00), ("Amazon", 1, 25.00)]
# T-Motor store $46.90 x 5 (V); T9545 pair $10.42 x 6 pairs (U, rcdrone.top, search 2026-11-14); CNHL 4S 2000 $40.49 x 2
# (U, pessimistic of $24.99-40.49, search 2026-11-14); ESCs and the rest as RESTUDY.
CHOSEN_A = [("T-Motor store", 5, 46.90), ("Amazon", 2, 30.00), ("rcdrone.top", 6, 10.42), ("RaceDayQuads", 2, 40.49),
            ("Home Depot", 1, 70.00), ("Aloft Hobbies", 1, 40.00), ("West3D", 1, 21.00), ("Amazon", 1, 25.00)]


def total(lines, floor=True):
    al = (FLOOR if floor else []) + lines
    goods = sum(q*u for _, q, u in al); tax = goods*TAX
    nv = len({v for v, _, _ in al})
    return goods, tax, nv*SHIP, nv, goods+tax+nv*SHIP+FAA


def crash_reserve(pack, servo=14.99, wing=45.0, vendors=2):
    return (pack+servo+wing)*(1+TAX) + vendors*SHIP


def main():
    base, m = mass()
    print("# sizing_a.py output (candidate A, scaled quad tailsitter)\n\n## 1. Mass")
    print("| Item | g | x aft LE m | Source |\n|---|---|---|---|")
    for n, g, x, s in MASSES:
        print(f"| {n} | {g} | {x:+.3f} | {s} |")
    print(f"\nBase {base:.0f} g; +{CONTINGENCY*100:.0f} % contingency (RESTUDY) -> **{m*1000:.0f} g** (RESTUDY A 1,228 g)")
    rows, length = box_fit()
    print(f"\nBox fit (cruise attitude; box 1.25 x 0.55 x 0.45 m; prop disk to fin foot {length:.3f} m):")
    for lab, dims, slack, ok in rows:
        print(f"- {lab}: {dims[0]:.2f} x {dims[1]:.2f} x {dims[2]:.2f} m, slack {slack[0]:.2f} / {slack[1]:.2f} / {slack[2]:.2f} m -> {'PASS' if ok else 'FAIL'}")
    wg = wing(m); pr = propulsion(m)
    print("\n## 2. Wing")
    print(f"S {S_WING} m2, b {SPAN} m, c {CHORD} m, AR {wg['AR']:.2f}, W {wg['W']:.2f} N, wing loading {wg['wl']:.1f} N/m2")
    print(f"CLmax {CLMAX} (EST): Vs {wg['vs']:.2f} m/s, 1.3 Vs {wg['v13']:.2f} m/s; cruise {wg['vc']:.0f} m/s: CL {wg['cl']:.3f}, Re {wg['re']:.3g}")
    print(f"CD0 {wg['cd0']:.4f} (wing {wg['cd0_wing']:.4f}, fins {wg['cd0_fin']:.4f}, parts {sum(CD0_PARTS.values()):.4f}), CDi {wg['cdi']:.4f}, **L/D {wg['ld']:.2f}**, drag {wg['drag']:.2f} N")
    print("\n## 3. Propulsion (T-Motor MN2212 V2.0 KV780, 4S, T9545 / 9545B)")
    print(f"Hover thrust/motor {pr['t_each']:.0f} g (cos {CANT_DEG:.0f} deg cant, {DOWNLOAD*100:.0f} % download); table {pr['p_h_each']:.1f} W/motor; hover {pr['p_hover']:.0f} W incl. x{CTRL_MARGIN}")
    print(f"Momentum cross-check FM x eta = {pr['fm_eta']:.2f} (K09-L about 0.45); static CT implied by the table at its rpm {pr['ct_static']:.3f} (APC-like 9x4.5 is about 0.10-0.11: table rpm column suspect)")
    print(f"T/W fresh (table 14.8 V, 100 %, no 16.8 V credit) {pr['tw_fresh']:.2f} (>= 2.0 {'PASS' if pr['tw_fresh']>=2.0 else 'FAIL'})")
    print(f"T/W sag (3.6 V/cell, R_pack {R_PACK*1000:.0f} mohm -> {pr['v_sag']:.1f} V, hot x{THERMAL}) {pr['tw_sag']:.2f} (>= 1.6 {'PASS' if pr['tw_sag']>=1.6 else 'FAIL'})")
    print(f"Hover pack current {pr['i_hover_bat']:.1f} A; motor {pr['i_h_each']:.1f} A of {MOTOR['rating_a']} A")
    print(f"Full-duty motor current: table {TAB_I[-1]} A at 14.8 V; fresh 16.8 V EST {pr['i_full_fresh']:.1f} A vs {MOTOR['rating_a']} A / 180 s: {100*(pr['i_full_fresh']/MOTOR['rating_a']-1):+.1f} %")
    print(f"One-motor transient (one saturates, others hover): uncapped {pr['i_full_fresh']:.1f} A; Q_M_SPIN_MAX 0.90 -> {pr['i_one_cap']:.1f} A; cap that holds the rating {pr['spin_cap']:.3f}; peak pack {pr['i_peak_bat']:.0f} A vs 100C x 2 Ah = 200 A")
    print(f"Cant {CANT_DEG:.0f} deg costs cos = {math.cos(math.radians(CANT_DEG)):.4f} of thrust")
    print("\nCruise prop (EST model; no published in-flight data):")
    pr_models = (("9545 (P/D 0.47; static thrust published)", 4.5, 0.11, 0.040, 0.55), ("9x6 (P/D 0.63; EST, no table)", 6.0, 0.095, 0.050, 0.70))
    cr = {}
    for lab, pitch, ct0, cp0, j0 in pr_models:
        r = cruise_prop(wg, ct0, cp0, j0); cr[lab] = r
        print(f"- {lab}: shaft {r[0]:.1f} W/motor, prop eta {r[1]:.2f}, {r[2]:.0f} rpm, J {r[3]:.2f}; pitch speed {r[2]*pitch*0.0254/60:.1f} m/s vs 15 m/s")
    labs = list(cr)
    print("\n## 5. Pack and mission energy (A2: 3.0 min hover-mode incl. go-around, 3.5 min cruise, 20 % reserve, 0.90 usable)")
    for lab, eta in ((f"9545 EST (eta_p {cr[labs[0]][1]:.2f} x 0.76)", cr[labs[0]][1]*0.76), (f"9x6 EST (eta_p {cr[labs[1]][1]:.2f} x 0.76)", cr[labs[1]][1]*0.76), ("RESTUDY eta 0.50", 0.50)):
        mm = mission(m, pr, wg, eta)
        print(f"- {lab}: hover {mm['e_hover']:.2f} Wh ({pr['p_hover']:.0f} W x 180 s), transitions {mm['e_trans']:.2f}, climb {mm['e_climb']:.2f}, cruise {mm['p_cruise']:.0f} W {mm['e_cruise']:.2f} Wh -> {mm['e_total']:.1f} Wh; need {mm['need_wh']:.1f} Wh vs pack {PACK_WH:.1f} Wh (usable {mm['usable']:.1f}); reserve left {mm['reserve_frac']*100:.0f} % -> {'PASS' if mm['reserve_frac']>=0.20 else 'FAIL'}")
    print(f"Pack 4S {PACK_MAH} mAh, 232 g; hover {pr['i_hover_bat']/(PACK_MAH/1000):.1f} C, peak {pr['i_peak_bat']/(PACK_MAH/1000):.0f} C of 100 C; two packs bought.")
    print("\n## 4. Tailsitter specifics\n### Hover yaw (5 m/s, wingtip 20 deg off the wind, Cd 2.05; K09-L 1.52-1.82 vs >= 1.5)")
    hy = hover_yaw(m, pr)
    print(f"authority at 30 % differential: cant {hy['m_cant']:.3f} + reaction {hy['m_react']:.3f} = {hy['auth']:.3f} N m (Q {hy['q_each']*1000:.1f} N mm/motor at {hy['rpm']:.0f} rpm; arm {hy['r']:.3f} m); wind moment {hy['mw']:.3f} N m (force {hy['nf']:.2f} N)")
    print(f"**ratio {hy['ratio']:.2f}** (no cant {hy['ratio_nocant']:.2f}); yaw accel {hy['acc']:.1f} rad/s2 (I_x {hy['ix']:.3f} kg m2 EST; K09-L 3.2, need >= 2.0)")
    print("cant sweep: " + ", ".join(f"{c} deg {hover_yaw(m, pr, cant=c)['ratio']:.2f}" for c in (6, 8, 10, 12, 15)))
    print("### Transition entry window (point-mass pitch-over, flat-plate wing, 12 deg/s to 70 deg; EST, low fidelity)")
    win, hi = entry_window(m, wg, pr)
    for vz0, low in win:
        print(f"- pre-climb {vz0:.0f} m/s: lowest T0/W with altitude loss < 3 m and handover >= 1.1 Vs ({1.1*wg['vs']:.1f} m/s): {low}")
    print(f"- high edge 0.80 x T/W sag = {hi:.2f} W; K09-L window was 1.328-1.397 W; here {win[0][1]}-{hi:.2f} W (ratio {hi/win[0][1]:.2f})")
    for t0 in (1.33, 1.5):
        r = pitch_over(m, wg, t0)
        print(f"- at T0 = {t0} W, no pre-climb: handover {r['vx']:.1f} m/s, min altitude {r['zmin']:.2f} m, {r['t']:.1f} s")
    print(f"- window used for the rating: K09-L scaled low edge 1.28-1.33 W (the sim has no pitch-moment / elevon-use limit, which bound K09-L) to {hi:.2f} W: {1.33:.2f}-{hi:.2f} W, +-{100*(hi-1.33)/(hi+1.33):.0f} % (K09-L +-2.5 %)")
    res, k09, tip = wind_and_tipover(m, wg, pr)
    print("### Wind sensitivity (hover broadside to the wind; plate Cd 2.0)")
    print(f"disk loading {tip['dl']:.0f} N/m2 (K09-L {tip['dl_k09']:.0f}); wing loading {wg['wl']:.1f} N/m2 (K09-L {tip['wl_k09']:.1f})")
    for k, (f, lean, tr, trs) in res.items():
        print(f"- {k}: drag {f:.1f} N, lean {lean:.0f} deg, thrust {tr:.2f} W = {trs*100:.0f} % of sagged max (K09-L 5 m/s lean {k09:.0f} deg)")
    print("### Fin-tip stance and tip-over")
    print(f"CG {tip['xc']*1000:.0f} mm aft of LE, {tip['h']:.3f} m above feet, half-stance {tip['half']:.2f} m -> static tip angle {tip['tip_static']:.1f} deg (K09-L 30.0-30.4, limit >= 30)")
    print(f"parked, steady broadside wind to tip: {tip['v_tip']:.1f} m/s; restoring/overturning at 5 m/s {tip['wind_ratio']:.2f} (K09-L analogue {tip['wind_k']:.2f})")
    print(f"sliding-foot energy bound on drift at touchdown {tip['v_slide']:.2f} m/s (upper bound); 1.2 m/s hard landing on 6 mm crush: {tip['g_impact']:.1f} g, {tip['f_impact']:.0f} N (structure not analysed)")
    rf = hy['rpm']; rs = hy['rpm']*1.08
    fv = fin_vibration(rf, rs)
    print("### Fin vibration (20 % separation from 1P / 2P at hover points)")
    print(f"EI {fv['EI']:.2f} N m2, mu {fv['mu']*1000:.0f} g/m, f1 ideal {fv['f_id']:.0f} Hz (EST); 1P/2P hover fresh {rf/60:.0f}/{2*rf/60:.0f} Hz, hover sag (+8 % rpm EST) {rs/60:.0f}/{2*rs/60:.0f} Hz")
    for fix, (f1, worst) in fv['res'].items():
        print(f"- root fixity {fix}: f1 {f1:.0f} Hz, worst separation {worst*100:.0f} % -> {'PASS' if worst >= 0.2 else 'FAIL'}")
    print("\n## 6. CG and static margin")
    c = cg_sm()
    print(f"CG {c['cg']*1000:.1f} mm aft of LE ({c['cg']/CHORD*100:.1f} % c); NP {c['np']*1000:.1f} mm inviscid, {c['np_v']*1000:.1f} mm with viscous shift; SM {c['sm']*100:.1f} %")
    print(f"limits: aft (SM 5 %) {c['aft']*1000:.1f} mm, forward (SM 15 %, EST) {c['fwd']*1000:.1f} mm")
    for px in (0.04, 0.02, 0.0, -0.02, -0.04):
        cc = cg_sm(px); print(f"  pack centre {px*1000:+.0f} mm: CG {cc['cg']*1000:.1f} mm, SM {cc['sm']*100:.1f} %")
    lo, hi_ = -0.15, 0.15
    for _ in range(60):
        mid = (lo+hi_)/2
        if cg_sm(mid)['sm'] > 0.08: lo = mid
        else: hi_ = mid
    print(f"  pack centre for SM 8 %: {lo*1000:+.0f} mm aft of LE")
    print("\n## 7. Cost vs RESTUDY A $1,461")
    g, t, s, nv, tot = total(RESTUDY_A); cr0 = crash_reserve(38.0)
    print(f"RESTUDY A lines reproduced: goods {g:.2f}, tax {t:.2f}, shipping {nv} vendors {s:.2f}, FAA 5 -> spend {tot:.2f} (RESTUDY 1,331); crash reserve {cr0:.2f}; total {tot+cr0:.2f} (RESTUDY 1,461)")
    g2, t2, s2, nv2, tot2 = total(CHOSEN_A); cr1 = crash_reserve(40.49)
    print(f"Chosen parts: goods {g2:.2f}, tax {t2:.2f}, shipping {nv2} vendors {s2:.2f}, FAA 5 -> spend {tot2:.2f}; crash reserve {cr1:.2f}; **total {tot2+cr1:.2f}**; margin {BUDGET-tot2-cr1:.2f}; delta {tot2+cr1-(tot+cr0):+.2f}")
    cand = sum(q*u for _, q, u in CHOSEN_A); fl = sum(q*u for _, q, u in FLOOR)
    g3 = fl + cand*1.30; tot3 = g3*(1+TAX) + nv2*SHIP + FAA + cr1
    print(f"Candidate lines +30 % (floor unchanged): total {tot3:.2f}, margin {BUDGET-tot3:.2f}")


if __name__ == "__main__":
    main()
