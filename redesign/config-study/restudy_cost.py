"""Configuration re-study cost + concept sizing (2026-11-14).  Reproduce: python -I restudy_cost.py
Reads nothing, writes nothing (prints markdown).  Stdlib only.

Labels: EST = estimate (engineering guess or unverified price); U = UNVERIFIED (price/spec from a search
snippet or aggregator, vendor page not read); "-" = unknown.  Prices are pre-tax; tax and shipping added below.
Every price line carries source + date seen (2026-11-14 = today; 2026-11-01 / 11-09 = earlier repo cards).
"""
TAX = 0.1025            # Berkeley, CDTFA rate used by the repo cost model (COST-TRADE.md 2026-11-14)
SHIP = 10.71            # per distinct vendor shipment (COST-TRADE.md, DESIGN-TO-COST.md)
FAA = 5.00              # FAA registration, no tax
BUDGET = 2000.0
RHO, G = 1.20, 9.81
RESERVE_FRAC, USABLE = 0.20, 0.90   # 20 % reserve (A2.md); 0.90 = sag/ageing derate (EST)

# ---------------------------------------------------------------- configuration-independent floor
# (id, item, vendor, qty, unit_pess_usd, source / date, flag)
FLOOR = [
 ("F01","RadioMaster Pocket ELRS transmitter","RadioMaster",1,69.99,"reach.dog M2 ELRS FCC $69.99; RadioMaster own $54.99 (diyfpv.com catalog) - search snippets 2026-11-14","U"),
 ("F02","RadioMaster RP3 V2 ELRS receiver","RadioMaster",1,19.99,"redesign/config-study/cards/K01/cost.csv 2026-11-01","U"),
 ("F03","SpeedyBee F405 Wing APP FC (ArduPilot target; SD log)","NewBeeDrone",1,51.99,"newbeedrone.com $51.99, RDQ $47.99, Progressive RC $39.99 - snippets 2026-11-14","U"),
 ("F04","HGLRC M100-5883 GPS + compass","RaceDayQuads",1,20.49,"cards/K01/cost.csv 2026-11-01 (racedayquads.com)","U"),
 ("F05","Matek ASPD-4525 digital airspeed + pitot","GetFPV",1,62.99,"getfpv.com $49.99 (snippet 2026-11-14); $62.99 used by DESIGN-TO-COST.md 2026-11-14","U"),
 ("F06","microSD 16-32 GB + 2 IPEX antennas + FC foam mount","Amazon",1,22.00,"cards/K01 + DESIGN-TO-COST.md (6+6+10)","EST"),
 ("F07","3 x micro servo EMAX ES3352HV (2 elevon/aileron + 1 spare)","GetFPV",3,14.99,"DESIGN-TO-COST.md 3: $12-16 (getfpv.com snippet 2026-11-14); 1.7-2.4 kgf-cm: small aircraft only","U"),
 ("F08","HTRC C150 charger 150 W 1-6S LiHV","Pyrodrone",1,59.99,"pyrodrone.com $44.99-57.99, Island Hobbynut $59.99 (snippets 2026-11-14)","U"),
 ("F09","2 x LiPo bag","Pyrodrone",2,9.99,"cards/K01/cost.csv 2026-11-01","U"),
 ("F10","Metal ammo can (pack storage/transport)","Harbor Freight",1,19.99,"harborfreight.com 63750 per cards/K01/cost.csv 2026-11-01","U"),
 ("F11","Test gear: watt meter, load cell+HX711 thrust stand, IR thermometer, multimeter, 0.1 g scale, caliper","Amazon",1,88.94,"cards/K01/cost.csv (12.99+17.97+8.98+25) + EST scale 12 + caliper 12","EST"),
 ("F12","Soldering: Pinecil V2 + PD supply + solder/flux/wick","Amazon",1,60.99,"cards/B08/cost.csv 2026-11-09 (25.99+20+15)","EST"),
 ("F13","Wire, XT60/bullets, heat-shrink, velcro, threadlocker, hinge tape, epoxy, CA","Amazon",1,60.00,"cards/B08/cost.csv hardware line 40 + 20 EST","EST"),
]
# Jacobs Hall (printers, laser, hot wire, hand tools) is $0 only where Jacobs lists it (BUILD-GUIDE.md labs page 2026-11-13);
# bought items here are the ones DESIGN-TO-COST.md found Jacobs does not list.
FLOOR_VENDORS = {l[2] for l in FLOOR}

def money(x): return f"{x:,.2f}"

def line_cost(lines):
    return sum(q*u for (_,_,_,q,u,_,_) in lines)

def total(goods_lines, extra_vendors, faa=True):
    """goods_lines: list of (vendor, qty, unit). Returns (goods, tax, shipping, faa, total)."""
    goods = sum(q*u for (_,q,u) in goods_lines)
    vendors = {v for (v,_,_) in goods_lines} | set(extra_vendors)
    tax = goods*TAX
    ship = len(vendors)*SHIP
    return goods, tax, ship, (FAA if faa else 0), goods+tax+ship+(FAA if faa else 0), len(vendors)

floor_goods = [(l[2], l[3], l[4]) for l in FLOOR]
fg, ft, fs, ff, FLOOR_TOTAL, fnv = total(floor_goods, [])

# ---------------------------------------------------------------- candidates
# mass lines in grams (EST unless noted); cost lines (item, vendor, qty, unit_pess, source, flag)
# physics: momentum theory, figure of merit FM, electrical eff, +10 % control margin (E2/B1 practice in repo)
def physics(m_kg, disk_area_m2, fm_eta, wing_area, cl_max, ld, eta_cruise, vcruise, trans_s, trans_w, hover_s=180.0, cruise_s=210.0,
            download=1.0):
    W = m_kg*G
    p_hover = download*1.10 * W**1.5/(2*RHO*disk_area_m2)**0.5 / fm_eta
    vs = (2*W/(RHO*wing_area*cl_max))**0.5
    p_cruise = W*vcruise/ld/eta_cruise
    e_wh = (p_hover*hover_s + p_cruise*cruise_s + 2*trans_w*trans_s)/3600.0
    need_wh = e_wh/(1-RESERVE_FRAC)/USABLE
    return dict(W=W, p_hover=p_hover, vs=vs, p_cruise=p_cruise, e_wh=e_wh, need_wh=need_wh, v13=1.3*vs)

C = {}

C["A"] = dict(
 name="A  Scaled quad tailsitter (K09 scaled down)", cards="K09 (CARD.md), K09-L repo work",
 masses=[("wing: 0.90 m x 0.245 m foam + CF spar, 2 fins",260),("4 x SunnySky X2212 KV980 (60 g each EST)",240),("4 x 45 A ESC (4-pack, 10 g each EST)",40),
         ("4 x APC 9x4.7 props",36),("pack 4S 2200 mAh (EST 245 g)",245),("FC + GPS + RX + airspeed + wiring",110),("2 servos + linkage",30),
         ("motor mounts, landing legs, joiners (printed)",120),("hardware, tape, paint",35)],
 contingency=0.10, wing_S=0.22, span=0.90, cl_max=0.70, ld=8.0, eta_c=0.50, vcruise=15.0,
 disk=4*3.1416*(0.2286/2)**2, fm_eta=0.60*0.75, trans_s=10, trans_w=400, thrust_each_g=1000,
 thrust_note="X2212 KV980 + 9x4.7, 4S: 1000 g/motor is EST. Maker rows seen: 870 g at 11.1 V, 13.2 A, 10x4.7 (flymod.net snippet 2026-11-14, U); 3S/4S 9 in row not found (-)",
 pack="4S 2200 mAh, 2 flight packs", flight_wh=2*0.0148*2200,
 cost=[("SunnySky X2212 KV980 (4 + 1 spare)","ReadyMadeRC",5,30.00,"flyingtech.co.uk 980KV II GBP 19.60 snippet 2026-11-14; ReadyMadeRC $ -> EST","EST"),
       ("LANRC 45 A BLHeli_S ESC 4-pack x 2 (1 spare set)","Amazon",2,30.00,"cards/K01/cost.csv 2026-11-01","U"),
       ("APC 9x4.7MR props x 12 (4 fit, 8 spare)","APC",12,3.50,"apcprop.com 11x4.5MR $3.83 2026-11-01 -> EST","EST"),
       ("4S 2200 mAh 100C XT60 pack x 2","Pyrodrone",2,38.00,"CNHL 2000 mAh 4S 100C $37.99 pyrodrone.com snippet 2026-11-14","U"),
       ("Foam: 2 in XPS sheet, foam board, packing tape, foam glue","Home Depot",1,70.00,"cards/K01/cost.csv (59.97+7.5 ...) 2026-11-09","EST"),
       ("CF tube 22x20 spar + 4 mm rods","Aloft Hobbies",1,40.00,"cards/K01/cost.csv 2026-11-01","EST"),
       ("PETG 1 kg (mounts, legs, nodes)","West3D",1,21.00,"DESIGN-TO-COST.md W05 2026-11-14","U"),
       ("Hardware: M3 screws, inserts, horns, rods","Amazon",1,25.00,"EST","EST")],
 spare_cost_in_crash=dict(pack=38.0, servo=14.99, wing=45.0, motor=0.0),  # motor spare carried, ESC spares carried
 crash_vendors=2,
 tech="Transition: ArduPilot Q_TAILSIT_ENABLE=1, 4-motor X, elevons (docs: ardupilot.org/plane/docs/guide-tailsitter.html, snippet 2026-11-14). Same architecture as K09-L; hover wind (gust lift ~0.2 W at 8 m/s EST) and pitch-over transition are the risks. Vertical pitch-up/pitch-down needs speed hold with airspeed sensor.",
 risk_tech="Medium", risk_sched="Medium (scratch wing + 4 motor mounts; ~6-8 build weeks EST)",
 carry="Most: FC/airspeed/ArduPilot tailsitter params, harness/test plan, wing aero scripts; mount / fin structure re-sized (no 36 in tube)")

C["B"] = dict(
 name="B  Small quadplane 4+1 (K01 scaled down)", cards="K01, K19",
 masses=[("wing: 1.40 m x 0.215 m EPP/XPS foam + CF spar, ailerons",330),("fuselage pod (foam board/EPP)",120),("2 x CF booms 16 mm + joiners",120),
         ("tail (V or conv.) foam",60),("4 x lift X2212 KV980 (60 g) + 1 x pusher 2212 (60 g)",300),("5 x ESC (10 g EST)",50),("4 x 9 in lift props + 1 pusher 9x6",50),
         ("pack 4S 3000 mAh (356 g, CNHL listing)",356),("FC + GPS + RX + airspeed + wiring",120),("4 servos + linkage",60),("mounts, hardware, tape",140)],
 contingency=0.10, wing_S=0.30, span=1.40, cl_max=1.1, ld=9.0, eta_c=0.50, vcruise=16.0,
 disk=4*3.1416*(0.254/2)**2, fm_eta=0.60*0.75, trans_s=15, trans_w=450, thrust_each_g=1000,
 thrust_note="Lift: X2212 KV980 + 10 in on 4S, 1000 g/motor EST (as A, maker row -). Pusher 2212-class 9x6 EST 800 g.",
 pack="4S 3000 mAh, 2 flight packs", flight_wh=2*0.0148*3000,
 cost=[("SunnySky X2212 KV980 x 5 (4 lift + pusher) + 1 spare","ReadyMadeRC",6,30.00,"as A","EST"),
       ("LANRC 45 A ESC 4-pack x 2","Amazon",2,30.00,"cards/K01/cost.csv","U"),
       ("APC props: 4 lift 10x4.5MR + pusher 9x6 + 8 spare","APC",13,3.80,"apcprop.com 2026-11-01 -> EST","EST"),
       ("4S 3000 mAh pack x 2","chinahobbyline",2,42.00,"CNHL 3000 mAh 4S 70C XT90 356 g (listing, snippet 2026-11-14), price -; EST","EST"),
       ("Foam, tape, glue, foam-board tail","Home Depot",1,80.00,"cards/K01/cost.csv","EST"),
       ("CF tubes 16-22 mm (booms x2, spar) ","Aloft Hobbies",1,75.00,"cards/K01 CF tube lines 2026-11-01","EST"),
       ("2 more servos (4 total: ail x2, elev, rudder/V)","GetFPV",2,14.99,"as F07","U"),
       ("PETG 1 kg + hardware","West3D",1,46.00,"as A","EST")],
 spare_cost_in_crash=dict(pack=42.0, servo=14.99, wing=60.0, motor=0.0),
 crash_vendors=2,
 tech="ArduPilot Q_ENABLE=1, QASSIST/QSTABILIZE, transition by airspeed (docs: ardupilot.org/plane/docs/quadplane-overview.html). Most-documented hobby VTOL. Failure modes: parked-prop drag, tail/boom shake, pusher thrust in transition; hover wind rejection is good (big lift props) but gust response flexes foam boom.",
 risk_tech="Low-Medium", risk_sched="Low-Medium (kit-like parts, foam wing hot-wired at Jacobs; ~5-7 weeks EST)",
 carry="Flight software = ArduPilot quadplane params (new); harness, test plan, FC/airspeed work carry; tailsitter-specific controllers do not")

C["C"] = dict(
 name="C  Dual-motor tailsitter (twin-motor flying wing, 'bicopter' w/ elevons)", cards="K10 (dropped: motor-out fatal), K16 (tilt bicopter, builder gave up)",
 masses=[("wing 1.00 m x 0.26 m foam + CF spar + 2 fins",230),("2 x SunnySky X2216-class 880 KV (85 g EST)",170),("2 x 45 A ESC (EST)",25),("2 x 11x4.7 props",30),
         ("pack 4S 2200 mAh (EST 245 g)",245),("FC + GPS + RX + airspeed + wiring",110),("2 elevon servos + linkage",30),("motor mounts, legs, hardware",90)],
 contingency=0.10, wing_S=0.26, span=1.00, cl_max=0.70, ld=8.0, eta_c=0.50, vcruise=15.0,
 disk=2*3.1416*(0.2794/2)**2, fm_eta=0.60*0.75, trans_s=10, trans_w=350, thrust_each_g=1150,
 thrust_note="X2216 KV880 + 11x4.7 on 4S: 1150 g/motor EST; no maker row read (-)",
 pack="4S 2200 mAh, 2 flight packs", flight_wh=2*0.0148*2200,
 cost=[("SunnySky X2216 KV880 (2 + 1 spare)","ReadyMadeRC",3,32.00,"buddyrc A2216 880KV $13.99 / X2216 V3 listings seen 2026-11-14; price -; EST","EST"),
       ("LANRC 45 A ESC 4-pack (2 fit, 2 spare)","Amazon",1,30.00,"cards/K01/cost.csv","U"),
       ("APC 11x4.7 props x 6","APC",6,4.50,"apcprop.com EST","EST"),
       ("4S 2200 mAh pack x 2","Pyrodrone",2,38.00,"as A","U"),
       ("Foam, tape, glue","Home Depot",1,70.00,"as A","EST"),
       ("CF tube spar + rods","Aloft Hobbies",1,40.00,"as A","EST"),
       ("PETG 1 kg + hardware","West3D",1,46.00,"as A","EST")],
 spare_cost_in_crash=dict(pack=38.0, servo=14.99, wing=45.0, motor=0.0),
 crash_vendors=2,
 tech="Q_TAILSIT_ENABLE=1, Q_FRAME_CLASS dual (value -, check docs). No motor redundancy; hover roll about the thrust axis comes only from differential thrust, pitch/yaw from elevon prop-wash, so low-authority at low throttle and in gusts. Few public ArduPilot dual-motor tailsitter builds that fly well (forum evidence in config-study K10/K16 reviews).",
 risk_tech="High", risk_sched="Medium-High (tuning dominates)",
 carry="K09-L software mostly (tailsitter code path), harness/test plan; hover tuning from scratch")

C["D1"] = dict(
 name="D1 HEEWING T1-S VTOL Ranger PNP + F405 + GPS (tilt-tri kit)", cards="B08 (CARD.md + REVIEW.md)",
 masses=[("airframe, 3 motors, 3 ESC, servos (listing flight weight 600-950 g w/ pack)",650),("pack 4S 2200 mAh in place of stock 1500 (EST 245 g)",245)],
 contingency=0.0, wing_S=0.13, span=0.79, cl_max=0.85, ld=6.0, eta_c=0.45, vcruise=14.0,
 disk=3*3.1416*(0.1295/2)**2, fm_eta=0.55*0.70, trans_s=15, trans_w=150, thrust_each_g=490, download=1.10,
 thrust_note="FX-1806 2000KV 5.1 in: 490 g/motor EST (B08 REVIEW C4: no maker data). Maker gives flight weight 600-950 g (rotorama listing as read in B08 REVIEW)",
 pack="4S 1500-2200 mAh, 2 flight packs", flight_wh=2*0.0148*2200,
 cost=[("HEEWING T1-S VTOL Ranger PNP w/ F405 + GPS + foam case","RaceDayQuads",1,393.49,"racedayquads.com $393.49 snippet 2026-11-09 (NextFPV $360, DefianceRC $409.99); stock U","U"),
       ("T1 PNP->VTOL conversion kit (3 motors + 2 tilt servos) as spares (fit to T1-S U)","DefianceRC",1,159.99,"defiancerc.com 2026-11-09 snippet","U"),
       ("Spare foam: second set wing halves/tail -","Heewing",1,0.00,"- (not found; foam breaks first)","-"),
       ("4S 2200 mAh pack x 2","Pyrodrone",2,38.00,"as A","U"),
       ("Spare props x 12","RaceDayQuads",12,1.00,"B08 cost.csv 3.00 per set EST","EST"),
       ("Modification budget: printed pod/skids/wing-tip, CF rod","Amazon",1,60.00,"B08 cost.csv","EST")],
 spare_cost_in_crash=dict(pack=38.0, servo=0.0, wing=130.0, motor=0.0),   # new PNP foam airframe ~ 1/3 of kit; spares carried: motors/servos
 crash_vendors=2, credit_floor=["F03","F04"],  # bundled F405 + GPS replace our FC + GPS
 tech="Tilt-tri on ArduPilot (Q_ENABLE + tilt rotor); official HEEWING-F405 target (ardupilot.org/plane/docs/common-heewingf405.html, per B08). V2 board: no SD log, no compass; forum reports of factory transition abort and QLOITER trouble. Mass margin at listing limit 950 g if pack grows.",
 risk_tech="Medium (controls proven, not turnkey)", risk_sched="Low (ships assembled; first hover week 1) but near-zero team design content",
 carry="Software: ArduPilot param/logging/test-plan work; K09-L tailsitter control code does not carry; CAD/harness do not carry")

C["D2"] = dict(
 name="D2 ZOHD Altus VTOL PNP (980 mm tilt-tri), team supplies FC", cards="B08 alt",
 masses=[("airframe + 3 motors + 3 ESC + 4+2 servos (maker flying weight 1100-1300 g w/ 4S 3000)",800),("pack 4S 3000 mAh (356 g)",356)],
 contingency=0.0, wing_S=0.158, span=0.98, cl_max=0.85, ld=6.0, eta_c=0.45, vcruise=17.0,
 disk=3*3.1416*(0.1651/2)**2, fm_eta=0.55*0.70, trans_s=15, trans_w=300, thrust_each_g=700, download=1.10,
 thrust_note="3 x 2204-class: 700 g each EST (maker motor not named -; 5 x 4.2 3-blade props per UnmannedTechShop snippet 2026-11-14)",
 pack="4S 3000 mAh, 2 flight packs", flight_wh=2*0.0148*3000,
 cost=[("ZOHD Altus VTOL PNP (airframe, 3 motors, 3 ESC, servos)","ReadyMadeRC",1,299.99,"readymaderc.com/products/details/86192 read 2026-11-14: in stock, FC/RX/battery not included","V"),
       ("2 x 2204 motor + 2 tilt servos + props spares","GetFPV",1,80.00,"B08 cost.csv alt line EST","EST"),
       ("4S 3000 mAh pack x 2","chinahobbyline",2,42.00,"as B","EST"),
       ("Modification budget","Amazon",1,60.00,"B08 cost.csv","EST")],
 spare_cost_in_crash=dict(pack=42.0, servo=14.99, wing=110.0, motor=0.0),
 crash_vendors=2, credit_floor=[],
 tech="Tilt-tri, own FC (SpeedyBee F405 Wing APP, ArduPilot); no maker ArduPilot param file found (B08). Twin tilt servos + 3rd motor; EPP foam, modifiable.",
 risk_tech="Medium", risk_sched="Low-Medium (assembly ~1 week, tuning on own params)",
 carry="ArduPilot FC/airspeed/log/test-plan work carries; airframe design does not")

C["D3"] = dict(
 name="D3 HEEWING T2 Cruza 1.2 m PNP + VTOL conversion kit (tilt-tri, 6S)", cards="B08 family",
 masses=[("T2 Cruza airframe, motors (EST)",900),("VTOL conversion: 3 motors FX-3110 680KV, 2 tilt servos, hardware",650),("pack 6S 3000 mAh (EST 450 g)",450),("FC, GPS, RX, airspeed, wiring",120)],
 contingency=0.05, wing_S=0.28, span=1.20, cl_max=0.9, ld=9.0, eta_c=0.50, vcruise=17.0,
 disk=3*3.1416*(0.254/2)**2, fm_eta=0.55*0.70, trans_s=15, trans_w=500, thrust_each_g=1300, download=1.10,
 thrust_note="FX-3110 680KV: 1300 g/motor on 6S EST (no maker table found -). Maker flight weight 2000-3500 g (zbotic.in snippet 2026-11-14)",
 pack="6S 3000 mAh, 2 flight packs", flight_wh=2*0.0222*3000,
 cost=[("HEEWING T2 Cruza 1.2 m PNP","BuddyRC",1,339.99,"buddyrc.com $339.99 (DefianceRC $339, NextFPV $354) snippets 2026-11-14","U"),
       ("T2 Cruza VTOL conversion kit","NextFPV",1,226.00,"nextfpv.com $226 (Defiance $228) snippet 2026-11-14","U"),
       ("6S 3000 mAh pack x 2","chinahobbyline",2,60.00,"EST (CNHL 6S class)","EST"),
       ("Spares: 1 motor, 1 tilt servo, props, 6S pack in reserve","GetFPV",1,60.00,"EST","EST"),
       ("Modification budget","Amazon",1,40.00,"EST","EST")],
 spare_cost_in_crash=dict(pack=60.0, servo=14.99, wing=170.0, motor=0.0),
 crash_vendors=2, credit_floor=[],
 tech="Tilt-tri on ArduPilot, maker recommends ArduPilot + FX-405 board with preset VTOL params (nextfpv.com snippet). Heavy (2-3.5 kg), big foam wing; crash repair costs more.",
 risk_tech="Medium", risk_sched="Low-Medium",
 carry="ArduPilot FC/airspeed/log/test-plan work carries; heavy 6S harness differs")

def crash_reserve(c):
    s = c["spare_cost_in_crash"]
    parts = s["pack"] + s["servo"] + s["wing"] + s["motor"]
    return parts*(1+TAX) + c["crash_vendors"]*SHIP

def analyse(key):
    c = C[key]
    base = sum(m for _,m in c["masses"])
    mass = base*(1+c["contingency"])/1000.0
    ph = physics(mass, c["disk"], c["fm_eta"], c["wing_S"], c["cl_max"], c["ld"], c["eta_c"], c["vcruise"],
                 c["trans_s"], c["trans_w"], download=c.get("download", 1.0))
    tw = 4*c["thrust_each_g"]/1000.0/mass if key in ("A","B") else (2*c["thrust_each_g"]/1000.0/mass if key=="C" else 3*c["thrust_each_g"]/1000.0/mass)
    goods = [(v,q,u) for (_,v,q,u,_,_) in c["cost"]]
    # floor lines remain except credited ones
    credit = sum(l[3]*l[4] for l in FLOOR if l[0] in c.get("credit_floor", []))
    gl = floor_goods + goods
    g, t, s, f, tot, nv = total(gl, [])
    g -= credit; t = g*TAX
    # shipments: recompute after credits (credited vendors still count: NewBeeDrone/RDQ keep an unshipped credit => minus nothing)
    tot = g + t + s + f
    res = crash_reserve(c)
    flight_wh = c["flight_wh"]
    return dict(mass=mass, ph=ph, tw=tw, goods=g, tax=t, ship=s, faa=f, spend=tot, reserve=res, total=tot+res, margin=BUDGET-tot-res,
                vendors=nv, flight_wh=flight_wh, credit=credit, base=base)

if __name__ == "__main__":
    print("## Floor (configuration-independent), pre-tax pessimistic")
    print("| ID | Item | Vendor | Qty | Unit $ | Line $ | Flag | Source / date |")
    print("|---|---|---|---|---|---|---|---|")
    for (i,it,v,q,u,src,fl) in FLOOR:
        print(f"| {i} | {it} | {v} | {q} | {money(u)} | {money(q*u)} | {fl} | {src} |")
    print(f"\nGoods {money(fg)}; tax 10.25 % {money(ft)}; shipping {fnv} vendors x {SHIP} = {money(fs)}; FAA {FAA}; "
          f"**floor total {money(FLOOR_TOTAL)}**; left for airframe + propulsion + packs + crash reserve: **{money(BUDGET-FLOOR_TOTAL)}**\n")
    print("## Candidates")
    print("| Cand | MTOW kg | Wing S m2 / span | Vs / 1.3Vs m/s | T/W hover | Hover W | Cruise W | Mission Wh (EST) | Pack need Wh | Pack fitted Wh/pack | Spend $ | Crash reserve $ | Total $ | Margin $ |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in C:
        c = C[k]; r = analyse(k); p = r["ph"]
        print(f"| {c['name'][:40]} | {r['mass']:.2f} | {c['wing_S']} / {c['span']} | {p['vs']:.1f} / {p['v13']:.1f} | {r['tw']:.2f} | {p['p_hover']:.0f} | {p['p_cruise']:.0f} | {p['e_wh']:.1f} | {p['need_wh']:.1f} | {r['flight_wh']/2:.1f} | {money(r['spend'])} | {money(r['reserve'])} | {money(r['total'])} | {money(r['margin'])} |")
    for k in C:
        c = C[k]; r = analyse(k)
        print(f"\n### {c['name']}")
        print(f"Mass build-up (EST, g): " + "; ".join(f"{n} {m}" for n,m in c["masses"]) + f"; base {r['base']} g, contingency {c['contingency']*100:.0f} % -> {r['mass']*1000:.0f} g")
        print(f"Thrust: {c['thrust_note']}")
        print("| Line | Vendor | Qty | Unit $ | Ext $ | Flag | Source |")
        print("|---|---|---|---|---|---|---|")
        for (it,v,q,u,src,fl) in c["cost"]:
            print(f"| {it} | {v} | {q} | {money(u)} | {money(q*u)} | {fl} | {src} |")
        print(f"Floor {money(FLOOR_TOTAL)} (credit for bundled FC/GPS {money(r['credit'])}); candidate goods + floor goods {money(r['goods'])} + tax {money(r['tax'])} + shipping {money(r['ship'])} ({r['vendors']} vendors) + FAA {FAA} = spend {money(r['spend'])}; crash reserve {money(r['reserve'])}; total {money(r['total'])}; margin {money(r['margin'])}")
