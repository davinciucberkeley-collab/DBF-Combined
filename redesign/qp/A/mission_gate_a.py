"""Concept A mission and mass-gate arithmetic (D-183 props/pack, D-184 arm x1.2 + cant 16 deg).  Reproduce: python -I mission_gate_a.py  (stdlib; prints; writes nothing)
Inputs are SIZING-A.md / BOARD.md numbers (cited in the dict); EST where marked."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prop_a as pa   # APC 9x4.5MR model, CANT 16 deg, derate 0.93
G, RHO = 9.807, 1.20
S, CLMAX, CD0, E, AR = 0.22, 0.75, 0.0356, 0.8, 0.90**2/0.22          # SIZING-A s2
VS = math.sqrt(2*1.226*G/(RHO*S*CLMAX))                               # at 1.226 kg sized mass (SIZING-A)
def vs(m): return math.sqrt(2*m*G/(RHO*S*CLMAX))
print("Stall (CLmax 0.75 EST):", {m: round(vs(m), 2) for m in (1.226, 1.37, 1.45, 1.50)})
print("1.3 Vs at 1.50 kg:", round(1.3*vs(1.50), 2), " 1.45 Vs:", round(1.45*vs(1.5), 2))

def aero(V, m=1.37):
    q = 0.5*RHO*V*V; CL = m*G/(q*S); CD = CD0 + CL*CL/(math.pi*AR*E); D = q*S*CD
    return CL, CD, CL/CD, D, D*V
for V in (15.0, 16.0, 17.0):
    CL, CD, LD, D, Pa = aero(V); print(f"V {V}: CL {CL:.3f} L/D {LD:.2f} drag {D:.2f} N aero {Pa:.1f} W elec {Pa/(0.26*0.76):.0f} W (eta_p 0.26 x 0.76 EST)")

V = 17.0
R = V*V/(G*math.tan(math.radians(30)))
LEG_REF, LEG = 300.0, 150.0          # QP-4 (BOARD s3): requirement time defined on the 300 m reference lap; flown leg 150 m
lap_ref = 2*LEG_REF + 2*math.pi*R; tl_ref = lap_ref/V
lap = 2*LEG + 2*math.pi*R; tl = lap/V
settle, laps2, goaround, runin = 15.0, 2*tl_ref, tl_ref, 0.5*tl_ref
cruise_s = settle + laps2 + goaround + runin
print(f"R {R:.1f} m; reference lap (300 m leg) {lap_ref:.1f} m = {tl_ref:.2f} s; cruise requirement {cruise_s:.1f} s = {cruise_s/60:.2f} min")
print(f"flown: leg {LEG:.0f} m, lap {lap:.1f} m = {tl:.2f} s, {(cruise_s-settle)/tl:.1f} laps of cruise after the {settle:.0f} s settle; racetrack far point {LEG/2+R:.0f} m; any-direction bound after BATT_LOW L/2 + 51 + 94 = {LEG/2+R+94:.0f} m vs fence 250 - 10 = 240 m (margin {240-(LEG/2+R+94):.0f} m)")
# ---- mass roll-up (basic g, maturity, growth by ASM-A3-MGA: EST 20, CALC 10, DATASHEET 5, CAD 5, WEIGHED 1, pack 0) ----
items = [("wing: foam 25 kg/m3 + 12x10 spar + 2 elevons y 0.04-0.35 + 2 balances 32.2 g + 4 lens caps with stops 12.4 g + 2 hinge dampers 5.0 g (CAD as drawn, QP-4 FIXES2)", 223.4, "EST", .20), ("2 fins: tubes + ribs + fairing + feet (CAD, lightened printed parts, EST)", 117.4, "EST", .20),
         ("4 x MN2212 with cables (65 g, T-Motor page)", 260, "DATASHEET", .05), ("4 x APC 9x4.5MR/MRP (11.06 g each, RMRC page)", 44.2, "DATASHEET", .05),
         ("ESC 4-in-1 7.2 g board + leads/caps (page; leads EST)", 20, "EST", .20), ("1 x Tattu 2300 (listing 270 g)", 270, "pack", 0.0),
         ("FC + GPS + RX + airspeed + plate + wiring (106 g: plate 12 -> 8 g)", 106, "EST", .20), ("2 x ES3054HV 20.5 g + linkage (SERVO.md)", 47, "DATASHEET", .05),
         ("motor cage incl. tray, hub 13 g, cups 4 g (CAD)", 113.3, "EST", .20), ("hardware, tape (no paint; CAD lump 30 g)", 30, "EST", .20)]
base = sum(i[1] for i in items); gr = sum(i[1]*i[3] for i in items); OVER = 0.032*1500
PRED = base+gr+OVER; M = PRED/1000
print(f"basic {base} g; growth {gr:.1f} g; predicted {base+gr:.1f} g; overrun {OVER:.0f} g; predicted+overrun {PRED:.0f} g; headroom to 1500 {1500-PRED:.0f} g, to 1440 {1440-PRED:.0f} g")
# ---- stall ----
print("Stall (CLmax 0.75 EST):", {m: round(vs(m), 2) for m in (1.226, round(M,3), 1.44, 1.50)})
print(f"1.3 Vs at 1.50 kg: {1.3*vs(1.50):.2f} (cruise 17 is {100*(17/(1.3*vs(1.5))-1):.1f} % over); at {M:.3f} kg: {1.3*vs(M):.2f}")
# ---- thrust-to-weight (prop_a model, x0.93 derate, hot x0.97 on sag; uncapped and 0.90 spin cap) ----
th = {}
for tag, vr in (("fresh", 16.8), ("sag", 3.73*4)):
    for duty in (1.0, 0.90):
        n, i, t_, pw, vb = pa.full(vr, duty); hot = 0.97 if tag == "sag" else 1.0
        th[(tag, duty)] = 4*t_/9.807*1000*hot*pa.DER*math.cos(math.radians(pa.CANT))   # total vertical gf
for m in (round(M,3), 1.44, 1.50):
    r = {k: v/(m*1000) for k, v in th.items()}
    print(f"m {m}: T/W fresh {r[('fresh',1.0)]:.2f} (cap {r[('fresh',0.9)]:.2f}); sag {r[('sag',1.0)]:.2f} (cap {r[('sag',0.9)]:.2f})")
    for tag, k in (("uncapped sag", ("sag",1.0)), ("0.90-capped sag", ("sag",0.9))):
        lo, hi = 1.33, 0.80*r[k]; print(f"   window {tag}: {lo}-{hi:.3f} W, +-{100*(hi-lo)/(hi+lo):.1f} %")
for tag, k, lim in (("fresh 2.0", ("fresh",1.0), 2.0), ("fresh 2.0 capped", ("fresh",0.9), 2.0), ("sag 1.6", ("sag",1.0), 1.6), ("sag 1.6 capped", ("sag",0.9), 1.6)):
    print(f"max mass T/W {tag}: {th[k]/lim/1000:.3f} kg")
hi5 = 1.33*1.05/0.95
for tag, k in (("uncapped", ("sag",1.0)), ("capped", ("sag",0.9))):
    print(f"mass for +-5 % window {tag}: {th[k]*0.80/hi5/1000:.3f} kg")
# ---- energy: Tattu 2300 4S ----
PACK_WH = 2.3*14.8; USABLE = PACK_WH*0.90*0.80
print(f"Pack {PACK_WH:.1f} Wh, usable after 0.90 floor and 20 % reserve {USABLE:.1f} Wh; BATT_LOW remaining = {2300-USABLE/PACK_WH*2300:.0f} mAh of 2300")
for m in (round(M,3), 1.44, 1.50):
    Ph = pa.hover(m, pa.DER)[4]; Eh = Ph*180/3600; Etr = 1.56*(m/1.37)**1.5; Ecl = 0.29*(m/1.37)
    Pc = 161*(m/1.37)**0.58; Ecr = Pc*cruise_s/3600; E_ = Eh+Etr+Ecl+Ecr
    tc = (USABLE-Eh-Etr-Ecl)/Pc*3600
    print(f"m {m}: hover {Ph:.0f} W {Eh:.2f} Wh (180 s incl 40 s go-around); trans {Etr:.2f}; climb {Ecl:.2f}; cruise {Pc:.0f} W {Ecr:.2f} Wh; total {E_:.2f} Wh; pack margin {USABLE/E_:.2f}x; "
          f"hover pack {Ph/14.8:.1f} A; max cruise to BATT_LOW {tc:.0f} s = {tc/60:.2f} min (need {cruise_s/60:.2f}); spare laps (150 m leg) {(tc-cruise_s)/tl:.1f}")
# aero cross-check of cruise power
for V_ in (17.0,):
    CL, CD, LD, D, Pa = aero(V_, M); print(f"aero check at {M:.3f} kg, {V_} m/s: CL {CL:.3f} L/D {LD:.2f} elec {Pa/(0.26*0.76):.0f} W (EST eta)")
# landing
print("hard landing 1.2 m/s on 6 mm crush: decel g =", round(1.2**2/(2*0.006)/G, 1), "; impact energy at 1.50 kg (J) =", round(0.5*1.5*1.44, 2))
# CG (QP-4): anchored on the CAD (QP-3 CAD s4): basic 1,204.6 g, CG 16.2 mm aft of LE with the pack centred at x -20 mm. The old 'rest of aircraft 35.7 mm' estimate is withdrawn.
NP, CHORD = 40.7, 245.0
CAD_BASIC, CAD_CG, PACK_X = 1215.9, 22.5, -10.0   # QP-4 FIXES: as-drawn CAD (was 1204.6 / 16.2 / -20 at QP-3)
cg = CAD_CG
for px in (-20.0, -3.0, +7.0):
    print(f"CAD CG with the pack centre at x {px:+.0f} mm: {CAD_CG + 270*(px-PACK_X)/CAD_BASIC:.1f} mm aft of LE, SM {(NP-(CAD_CG + 270*(px-PACK_X)/CAD_BASIC))/CHORD*100:.1f} %")
print(f"CG {cg:.1f} mm aft of LE, SM {(NP-cg)/CHORD*100:.1f} %; pack 10 mm aft -> CG {cg+270*10/PRED:.1f}")
print("CG aft limit SM 5 %:", NP-0.05*CHORD, " fwd limit SM 15 %:", NP-0.15*CHORD)
