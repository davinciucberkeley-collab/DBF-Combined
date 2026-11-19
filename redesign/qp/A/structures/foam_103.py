"""QP-4 FIXES2 foam checks at the board allowable.  python -I foam_103.py -> foam_103.md   (stdlib only)
FOAMULAR 150 compressive strength min 15.0 psi = 103 kPa (Owens Corning data sheet, board read 2026-11-15; ASTM D1621) at any density, so the 25 kg/m3 core is rated the same
as 30.  The iteration-2/3 checks used 120 kPa (K09-L XPS value).  Tension (150 -> 129 kPa) and shear (100 -> 86 kPa) are scaled by 103/120 (EST): the data sheet gives no
FOAMULAR 150 shear or tension row (searched 2026-11-15; PINKCORE shear rows are a different product and are not used).
Loads and factors are those of structures_a.py / iter3 (KP = 1.5 x 1.15 x 1.25 = 2.156 printed/bonded ultimate)."""
import math, os
KP, KF = 1.5*1.15*1.25, 1.5*1.15
OLD = dict(comp=120e3, tens=150e3, shear=100e3)
S = 103/120
NEW = {k: v*S for k, v in OLD.items()}; NEW["comp"] = 103e3
L = []
def P(s=""): print(s); L.append(s)
def ms(a, s): return a/s-1
def rate(m): return "PASS" if m >= 0.15 else ("MARGINAL" if m >= 0 else "FAIL")
rows = []
def row(name, stress, kind, note=""):
    rows.append((name, stress, kind, ms(OLD[kind], stress), ms(NEW[kind], stress), note))
T_br = 2.44                      # N m bridge pitch moment (structures_a.py M_pitch)
r_sp = 6e-3                      # 12 mm spar (iteration 3)
row("Foam shear around the spar from the bridge torque, bond rule |y| <= 0.15 m (iter 3)", T_br/(2*math.pi*r_sp**2*0.30)*KP, "shear", "iteration-3 rule: MARGINAL at the board allowable")
row("Same, FIXES2 rule: spar bonded over |y| <= 0.20 m (0.40 m of bond)", T_br/(2*math.pi*r_sp**2*0.40)*KP, "shear", "new build rule; +1 g epoxy EST")
row("Foam bearing at the fin slot (2 x 20 N side load, 65 x 23 mm)", 2*20.0*KP/(0.065*0.0233), "comp")
q = 3.4*1.50*9.81/0.90/0.032
row("Foam shear, lift into the spar slot (n 3.4, 1.50 kg, 32 mm bond width)", q*1.5, "shear")
m_pack = 0.270
A_slot = 0.0325*0.111
row("Pack tray on the LE slot floor, 12 g crash, full slot floor (32.5 x 111 mm)", m_pack*9.81*12*KP/A_slot, "comp", "bearing")
row("Same, worst case: only a quarter of the floor carries (rim contact)", m_pack*9.81*12*KP/(A_slot/4), "comp", "bearing")
# servo stall reacted by the epoxy on the pocket walls
T_stall = 0.397*9.155/8.5        # N m at the elevon through the 8.5 mm arm hole and 9.155 mm horn radius (D-212 rev 2; ES3054HV 0.397 N m at 7.2 V, SERVO.md)
Fy, Fx = (T_stall/2)/0.0267, (T_stall/2)/0.0284
A_f = 0.0267*0.013; A_g = 0.0284*0.013
row("Servo stall (0.427 N m at the elevon, fault: servo driven into the stop), epoxy on all four pocket walls", max(Fy/A_f, Fx/A_g)*KP, "shear", "build rule: epoxy on all four walls, not two")
# stop reaction through the lens cap bond
F_stop = T_stall/0.014           # N at the bosses (contact radius about 14 mm), both bosses of one elevon side
A_cap = (2*34e-3*3e-3 + 108e-3*3e-3 + 2*(34e-3+108e-3)*0.6e-3)      # flange 3 mm on both sides and the fore end + wall footprint
row("Stop reaction at stall (%.0f N) peeling the lens cap off the skin (flange 3 mm + wall footprint %.0f mm2)" % (F_stop, A_cap*1e6), F_stop*KP/A_cap, "tens", "peel of the tape skin is not covered by a foam value: pull coupon required")
P("| Check | Stress (kPa) | Allowable 120 (old) MS | Allowable at 103 basis (kPa) | MS at 103 | Result | Note |"); P("|---|---|---|---|---|---|---|")
for name, st, kind, mo, mn, note in rows:
    P("| %s | %.0f | %+.2f | %.0f | %+.2f | %s | %s |" % (name, st/1e3, mo, NEW[kind]/1e3, mn, rate(mn), note))
P(); P("Allowables used (kPa): compressive 103 (V), tension %.0f (EST, 150 x 103/120), shear %.0f (EST, 100 x 103/120). Old: 120 / 150 / 100." % (NEW["tens"]/1e3, NEW["shear"]/1e3))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "foam_103.md"), "w").write("\n".join(L))
