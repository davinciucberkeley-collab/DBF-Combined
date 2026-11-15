"""Concept A prop + pack check (D-183).  Reproduce: python -I prop_a.py  (stdlib; prints markdown; writes nothing).
Prop: APC 9x4.5MR, static rows of https://www.apcprop.com/files/PER3_9x45MR.dat (read 2026-11-14), rho 1.225 SL, V=0.
Motor: T-Motor MN2212 V2.0 KV780: Kv 780 rpm/V and Rm 0.173 ohm (store.tmotor.com page, SIZING-A s3); I0 0.5 A is an ESTIMATE
(no page value; bench step 1 measures it).  Pack: sag = 3.73 V/cell rest (20 % left), pack R 30 mohm EST (SIZING-A).
Hover: m g / (4 cos(CANT) x 0.97 download); input power = V_m I / 0.98 (ESC) x 1.10 control margin (MISSION s4)."""
import math
RHO, D, KV, RM, I0 = 1.225, 9*0.0254, 780.0, 0.173, 0.5
CANT = 16.0   # deg; D-184 (was 14 in D-183)
KT = 60/(2*math.pi*KV)
# rpm: (thrust N, shaft W) from the APC file, V = 0
T = {5000:(2.674,20.063),6000:(3.859,34.224),7000:(5.264,53.842),8000:(6.892,79.836),9000:(8.746,113.149),
     10000:(10.830,154.758),11000:(13.149,205.680),12000:(15.706,266.981)}
def prop(n):
    ks = sorted(T); n = max(ks[0], min(ks[-1], n))
    for a, b in zip(ks, ks[1:]):
        if a <= n <= b:
            f = (n-a)/(b-a); return tuple(T[a][i]+f*(T[b][i]-T[a][i]) for i in (0, 1))
def run(vm):
    """motor terminal voltage vm -> (rpm, I, thrust N, shaft W)"""
    lo, hi = 3000.0, 12000.0
    for _ in range(60):
        n = (lo+hi)/2; th, pw = prop(n); q = pw/(n*2*math.pi/60)
        i = q/KT + I0; v = n/KV + i*RM
        lo, hi = (n, hi) if v < vm else (lo, n)
    n = (lo+hi)/2; th, pw = prop(n); q = pw/(n*2*math.pi/60)
    return n, q/KT + I0, th, pw
def full(vrest, duty=1.0, rp=0.030):
    lo, hi = 3.0, vrest
    for _ in range(50):                       # four motors saturated, pack drop
        vb = (lo+hi)/2; n, i, th, pw = run(vb*duty)
        lo, hi = (vb, hi) if vrest - 4*i*rp > vb else (lo, vb)
    return run(vb*duty) + (vb,)
DER = 0.93   # R3 derate: real thrust = DER x APC table (same rpm, same power)
def hover(m, der=1.0):
    t = m*9.807/(4*math.cos(math.radians(CANT))*0.97)/der
    lo, hi = 3.0, 16.0
    for _ in range(60):
        vm = (lo+hi)/2; th = run(vm)[2]
        lo, hi = (vm, hi) if th < t else (lo, vm)
    n, i, th, pw = run(vm); pin = vm*i/0.98*1.10
    return t*der/9.807*1000, n, i, vm*i, 4*pin, 4*pin/14.8
def one_motor(duty=0.9, m=1.50, vrest=16.8, rp=0.030):
    """one motor at duty cap, three at hover; pack drop from total current"""
    ih = hover(m)[2]; vb = vrest
    for _ in range(30):
        n, i, th, pw = run(vb*duty); ipack = i*duty + 3*ih*(hover(m)[3]/hover(m)[2]/vb)/1.0
        vb = vrest - rp*ipack
    return i, vb
if __name__ == "__main__":
    for tag, vr in (("fresh 16.8 V", 16.8), ("sag 14.92 V rest", 3.73*4)):
        for duty in (1.0, 0.90):
            n, i, th, pw, vb = full(vr, duty)
            hot = 0.97 if "sag" in tag else 1.0
            g = th/9.807*1000*hot
            print(f"{tag} duty {duty:.2f}: bus {vb:.2f} V, {n:.0f} rpm, {i:.1f} A/motor, thrust {g:.0f} gf table / {g*DER:.0f} gf x0.93; "
                  f"T/W at 1.50 kg {4*g/1500*math.cos(math.radians(CANT)):.2f} / {4*g*DER/1500*math.cos(math.radians(CANT)):.2f}")
    for duty in (1.0, 0.9):
        i, vb = one_motor(duty); print(f"one motor duty {duty}, three at hover, 1.50 kg, fresh: {i:.1f} A, bus {vb:.2f} V")
    for m in (1.44, 1.50):
        for der in (1.0, DER):
            g, n, i, pm, pe, ip = hover(m, der)
            print(f"hover {m} kg derate {der}: {g:.0f} gf/motor, {n:.0f} rpm, {i:.2f} A/motor, motor in {pm:.1f} W, pack {pe:.0f} W incl x1.10, pack {ip:.1f} A")
    # ---- pack options: mass roll-up, BATT_LOW cruise time, transition window (D-183) ----
    BASIC0, GROW0, OVER = 1167.0 + 15.0, 140.0 + 3.0, 48.0   # D-184: +15 g arm x1.2 (cage 120->135 g, 20 % growth on it)           # MASS-GATE s2-s4 with Tattu 2300 270 g, props 32 g EST
    def roll(pack_g, leads_g):
        basic = BASIC0 - 270 + pack_g + (4*11.06 - 32) + leads_g
        grow = GROW0 - 6.4 + 0.05*4*11.06                # props 5 % DATASHEET, pack 0 %
        return basic, grow, basic+grow+OVER
    PACKS = (("Tattu 2300 4S 75C (baseline)", 2.3, 270, 0), ("Turnigy Nano-Tech 2800 4S 70C", 2.8, 275, 0),
             ("CNHL G+Plus 3000 4S 70C XT90", 3.0, 356, 3))
    print("\n| Pack | Wh | basic g | growth g | predicted + overrun g | hover W (derated) | trans+climb Wh | cruise W | max cruise s before BATT_LOW | min | mission need 204.6 s |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for name, ah, g, lead in PACKS:
        b, gr, tot = roll(g, lead); m = tot/1000
        wh = 14.8*ah; use = wh*0.90*0.80
        hov = hover(m, DER)[4]*180/3600
        tr = 1.56*(m/1.37)**1.5 + 0.29*(m/1.37)
        pc = 161*(m/1.37)**0.58
        tc = (use - hov - tr)/pc*3600
        print(f"| {name} | {wh:.1f} | {b:.0f} | {gr:.0f} | {tot:.0f} | {hover(m, DER)[4]:.0f} | {tr:.2f} | {pc:.0f} | {tc:.0f} | {tc/60:.2f} | {use:.1f} Wh usable |")
    print("\nTransition window (+-%), low edge 1.33 W, high edge 0.80 x T/W sag (uncapped, as MASS-GATE):")
    for der in (0.93, 0.85):
        n, i, th, pw, vb = full(3.73*4, 1.0)
        row = []
        for m in (1.36, 1.37, 1.44, 1.441, 1.45, 1.50):
            tw = 4*th/9.807*0.97*der*math.cos(math.radians(CANT))/m; hi = 0.8*tw
            row.append(f"{m}: {100*(hi-1.33)/(hi+1.33):.1f}")
        print(f"derate {der}:", "; ".join(row))
