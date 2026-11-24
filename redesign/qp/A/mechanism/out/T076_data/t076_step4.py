"""T-073 step 4: hand calcs for R1 (windowed pack tray), R2 (FC/ESC bosses, no avionics plate), R4 (tubular strut clamps); R3 mass bookkeeping (R3 checks are
arm_cup_checks.py --r3 / --r3fix).  CATEGORY: rigid-body dynamics (landing_a traces, t076_traces.pkl) + hand-calculation part checks + geometry arithmetic.  No FEA.
Run: python -I t073_step4.py > step4_out.txt   (after t073_traces.py).  All allowables are the repo's EST values unless a source is given; '-' = unknown."""
import sys, os, math, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.abspath(os.path.join(HERE, "..", "..", "..", "structures")); sys.path.insert(0, S)
import numpy as np
import landing_path_a as LP
import landing_a as L
from amodel import electrical as E, wing as W, common as C, propulsion as PR
G = 9.81; KF = LP.KF; KP = LP.KP; BOND = LP.BOND; PETG_ILAY = LP.PETG_ILAY; PETG_BEAR = LP.PETG_BEAR; RHO = 1.27   # g/cm3 (T-067 s3)
tr = pickle.load(open(os.path.join(HERE, "t076_traces.pkl"), "rb"))
def rf(allow, stress): return allow/max(stress, 1e-12)
def row(tag, what, value, allow, r, note=""): print(f"| {tag} | {what} | {value} | {allow} | {r:.2f} | {note} |")
AX = max(v['ax_pk'] for v in tr.values()); AXc = max(tr, key=lambda k: tr[k]['ax_pk'])
AY = max(v['ay_pk'] for v in tr.values()); AYc = max(tr, key=lambda k: tr[k]['ay_pk'])
AZ = max(v['az_pk'] for v in tr.values()); AZc = max(tr, key=lambda k: tr[k]['az_pk'])
M_PACK = float(os.environ.get('T076_MPACK', '0.270'))     # kg, BOM W01 Tattu 2300 4S (270 g, readymaderc 2026-11-14)
print("## Landing peak loads on the pack (limit, 23 cases, M 1.5 kg, plateau 30 N, D2 pad; model: N_x = m_pack (sum|Fx_feet|/M + lam g), lam 0.667 until 0.3 s)")
print(f"- axial (aft lip) {AX/G:.2f} g in '{AXc}': {M_PACK*AX:.1f} N for the 270 g pack; lateral y {AY/G:.2f} g ('{AYc}'): {M_PACK*AY:.1f} N; z {AZ/G:.2f} g ('{AZc}'): {M_PACK*AZ:.1f} N (strap / plate-normal load).")
NX = M_PACK*AX; NY = M_PACK*AY; NZ = M_PACK*AZ
print("\n## R1 pack tray CGE-008 (geometry read from wing.py / electrical.py; R1 per T-070 s4: plate 1.2 mm ~50 % windows + rim/ribs 1.2 mm, end walls 1.2 mm ~60 % windows, lips = 2 tabs x 20 mm x 1.2 mm)")
LIP_R_H, LIP_F_H, LIP_T0 = 0.018-0.008, 0.020-0.008, 0.002      # wing.py l.849-850: rear lip z 8..18, front z 8..20, 2 mm thick, 109 wide
PLATE_T0 = 0.002; PAD = W.HUB_PAD; FL_W = (PAD[1][1]-PAD[0][1])      # hub flange width 26.8 mm (D-208)
WALL_H = 0.030-0.008; WALL_X = (W.PACK_X[1]+W.TRIM)-(W.PACK_X[0]-W.TRIM_FWD)   # end wall z 8..30, x length
print(f"- CAD: rear lip {LIP_T0*1e3:.0f} x {LIP_R_H*1e3:.0f} mm x 109 wide; plate {PLATE_T0*1e3:.0f} mm; hub flange {FL_W*1e3:.1f} mm wide ({PAD[0][2]*1e3:.0f}..{PAD[1][2]*1e3:.0f} z); end wall {WALL_X*1e3:.0f} long x {WALL_H*1e3:.0f} high x 2 mm.")
print("| Tag | Check (printed PETG, EST allowables; K = KP 2.156) | Demand | Allowable | RF | Note |"); print("|---|---|---|---|---|---|")
def tabs(n, w, t, arm=5.5e-3):
    A = w*t; Zt = w*t*t/6; Pt = KP*NX/n
    return Pt*arm/Zt, 1.5*Pt/A
for lab, n, w, t in (("baseline lip 2 mm x 109 wide", 1, 0.109, 0.002), ("R1 as specified: 2 tabs 20 x 1.2", 2, 0.020, 0.0012), ("R1b: 2 tabs 30 x 2.0", 2, 0.030, 0.002), ("R1c: 2 tabs 20 x 2.0", 2, 0.020, 0.002)):
    sig, tau = tabs(n, w, t); row("R1-a", f"rear-lip tab root bending, load centroid 5.5 mm above the plate; {lab}", f"{sig/1e6:.1f} MPa", "9.5 MPa interlayer (tab rises in z; layers lie in the plate plane)", rf(PETG_ILAY, sig), "EST orientation")
    row("R1-b", f"  tab shear 1.5 V/A; {lab}", f"{tau/1e6:.2f} MPa", "9.5 MPa", rf(PETG_ILAY, tau))
for lab, t in (("baseline plate 2.0", 0.002), ("R1 plate 1.2", 0.0012)):
    A = FL_W*t; sig = KP*NX/A
    row("R1-c", f"plate end face to hub bond, tension from the pack on the aft lip (flange {FL_W*1e3:.1f} x {t*1e3:.1f} mm); {lab}", f"{sig/1e6:.2f} MPa", "2.0 MPa epoxy EST (shear value used for tension: no tensile datum)", rf(BOND, sig), "plate rests on the bridge tube; strap preload not credited")
e = 13.5e-3-7e-3; Mx = KP*NX*e
print(f"- (not an RF) eccentric moment of the lip load about the plate midplane: {KP*NX:.0f} N x {e*1e3:.1f} mm = {Mx:.2f} N m; if the plate had no support but the 26.8 mm flange bond, bending stress would be {6*Mx/(FL_W*0.002**2)/1e6:.0f} MPa (2 mm) / {6*Mx/(FL_W*0.0012**2)/1e6:.0f} MPa (1.2 mm). The plate actually lies on the 16 mm bridge tube (z 6.0 tangent) and is strapped to it, so this is a bound, not the load path; the strap preload and the plate-to-tube contact have no data ('-'): needs a drop coupon.")
for lab, t, frac in (("baseline wall 2.0 mm solid", 0.002, 1.0), ("R1 wall 1.2 mm, 60 % windows (effective width 0.40)", 0.0012, 0.40), ("R1d wall 2.0 mm, 60 % windows", 0.002, 0.40), ("R1e wall 1.6 mm, 60 % windows", 0.0016, 0.40)):
    Zw = frac*WALL_X*t*t/6; Mw = KP*NY*10.5e-3; sig = Mw/Zw
    row("R1-d", f"end wall bending, lateral pack load {NY:.1f} N x KP, load 10.5 mm above the plate over {WALL_X*1e3:.0f} mm; {lab}", f"{sig/1e6:.1f} MPa", "9.5 MPa interlayer", rf(PETG_ILAY, sig), "windows' frame width EST")
print(f"- strap: z load on the pack {NZ:.1f} N limit ({KF*NZ:.1f} N design); strap 20 mm webbing breaking load '-' (not in BOM W08 text), so no RF.")
base = 25.80
plate = 66.5*109*1.2*0.5; ribs = 1.2e3; walls = 1.08e3; tabsv = 2*20*1.2*(LIP_R_H*1e3+LIP_F_H*1e3)
v = (plate+ribs+walls+tabsv)/1e3
print(f"\n- R1 mass: volume plate {plate/1e3:.2f} + ribs {ribs/1e3:.2f} + walls {walls/1e3:.2f} + tabs {tabsv/1e3:.2f} = {v:.2f} cm3 (T-070 numbers; the 1.2 mm members are < 2 x 1.26 mm so fully solid in the T-067 M basis) x {RHO} = **{v*RHO:.1f} g** against T-067 adopted {base:.2f} g: **dm = {v*RHO-base:+.1f} g**.")
tabsv2 = 2*20*2.0*(LIP_R_H*1e3+LIP_F_H*1e3); wallsv = 1.08e3*2.0/1.2
v2 = (plate+ribs+wallsv+tabsv2)/1e3
print(f"- R1' (tabs 2 x 20 x 2.0 mm, walls 2.0 mm with 60 % windows, rest as R1): {v2:.2f} cm3 = {v2*RHO:.1f} g, dm {v2*RHO-base:+.1f} g.")
# R1'' passing variant
for lab, n, w, t in (("R1'' tabs 2 x 40 x 2.0", 2, 0.040, 0.002),):
    sig, tau = tabs(n, w, t); row("R1-a", f"rear-lip tab root bending; {lab}", f"{sig/1e6:.1f} MPa", "9.5 MPa interlayer", rf(PETG_ILAY, sig))
Zw = 0.70*WALL_X*0.002**2/6; row("R1-d", "end wall 2.0 mm with 30 % windows (effective width 0.70), R1''", f"{KP*NY*10.5e-3/Zw/1e6:.1f} MPa", "9.5 MPa interlayer", rf(PETG_ILAY, KP*NY*10.5e-3/Zw))
row("R1-c", f"plate 1.2 mm with a 2.0 mm root pad over the 27.2 mm flange, R1''", f"{KP*NX/(FL_W*0.002)/1e6:.2f} MPa", "2.0 MPa EST", rf(BOND, KP*NX/(FL_W*0.002)))
v3 = (plate+ribs+0.15e3+4.488e3*0.70+2*40*2.0*(LIP_R_H*1e3+LIP_F_H*1e3))/1e3
print(f"- R1'' (PASSING VARIANT, EST geometry: plate 1.2 mm 50 % windows + ribs + 2.0 mm root pad, walls 2.0 mm with 30 % windows, 2 tabs 40 x 2.0 per lip): {v3:.2f} cm3 = {v3*RHO:.1f} g, **dm {v3*RHO-base:+.1f} g**.")
R1_DM = v*RHO-base; R1P_DM = v3*RHO-base
# ---------------- R2
print("\n## R2 FC / ESC on bosses, avionics plate AVN-001 removed")
FC_M, ESC_M = 17.0e-3, 7.2e-3          # electrical.py AVN-002 17.0 g; BOM P04 7.2 g board
holes_fc = E.FC_HOLES; cx_esc = PR.ESC_X0+0.0175
holes_esc = [(cx_esc+sx*0.010, sy*0.010) for sx in (-1, 1) for sy in (-1, 1)]
top_fc, top_esc = E.ZP+E.GEL, E.ZP
hs = [top_fc-C.zu(x) for x, y in holes_fc]+[top_esc-C.zu(x) for x, y in holes_esc]
print(f"- FC hole x (mm) {sorted(set(round(x*1e3,1) for x,y in holes_fc))} boss heights above the skin (to ZP+GEL = {top_fc*1e3:.1f} mm) {[round(h*1e3,1) for h in hs[:4]]} mm; ESC hole x {sorted(set(round(x*1e3,1) for x,y in holes_esc))} heights (to ZP = {top_esc*1e3:.1f} mm) {[round(h*1e3,1) for h in hs[4:]]} mm (skin upper surface zu(x) from common.py; glass skin 0.05 mm ignored).")
E_P = 2.1e9; a = 6e-3; Apad = a*a
k_col = [E_P*Apad/h for h in hs]; k_colb = [3*E_P*(a**4/12)/h**3 for h in hs]
EF, GF, NUF = LP.E_F, LP.G_F, 0.2
r_eq = a/math.sqrt(math.pi); k_fz = 2*r_eq*EF/(1-NUF**2); k_fh = 8*GF*r_eq/(2-NUF)
def series(*k): return 1/sum(1/x for x in k)
kz = [series(kc, k_fz) for kc in k_col]; kh = [series(kb, k_fh) for kb in k_colb]
print(f"- Boss column 6 x 6 mm, PETG E {E_P/1e9:.1f} GPa (fe_a.py nom): axial {min(k_col)/1e6:.1f}-{max(k_col)/1e6:.1f} MN/m, bending {min(k_colb)/1e6:.2f}-{max(k_colb)/1e6:.2f} MN/m. Foam under the pad (rigid square punch on a half-space, a_eq {r_eq*1e3:.2f} mm, foam E {EF/1e6:.0f} MPa, G {GF/1e6:.0f} MPa, nu 0.2 EST; the 0.05 mm glass skin adds nothing): vertical {k_fz/1e6:.2f} MN/m, shear {k_fh/1e6:.2f} MN/m per boss. Series per boss: z {min(kz)/1e6:.2f}-{max(kz)/1e6:.2f}, horizontal {min(kh)/1e6:.2f}-{max(kh)/1e6:.2f} MN/m.")
print("| Mount | mass g | translation f_z (Hz) | f_horizontal (Hz) | rocking about pattern centroid (Hz, c.g. above boss top, EST) | limit | |"); print("|---|---|---|---|---|---|---|")
frs = {}
for nm, m, ks_z, ks_h, pts, hcg in (("FC stack (4 bosses)", FC_M, kz[:4], kh[:4], holes_fc, 0.010), ("ESC (4 bosses)", ESC_M, kz[4:], kh[4:], holes_esc, 0.003)):
    fz = math.sqrt(sum(ks_z)/m)/(2*math.pi); fh = math.sqrt(sum(ks_h)/m)/(2*math.pi)
    xc = sum(p[0] for p in pts)/4
    kth = sum(k*(p[0]-xc)**2 for k, p in zip(ks_z, pts))+sum(ks_h)*hcg**2; I = m*(hcg**2+0.030**2/12)
    fr = math.sqrt(kth/I)/(2*math.pi); frs[nm] = min(fz, fh, fr)
    print(f"| {nm} | {m*1e3:.1f} | {fz:.0f} | {fh:.0f} | {fr:.0f} | >= 304 Hz (1.2 x top 2P band 253 Hz, A-P10a convention, applied to a mount: EST) | RF {min(fz,fh,fr)/304:.2f} |")
print("- Tape being replaced (AVN-007 foam tape 3.0 mm, 'hard mount') has no stiffness datum ('-'), so no 'better than before' claim; A-P25 allows thin foam tape or hard mount; bosses are harder. The FE forced response (A-P10b) still treats the FC node as the rigid spar centre.")
shear_boss = KP*(FC_M+ESC_M)*AX/8; bond_b = shear_boss/Apad
print(f"- Landing load on the boss bonds: FC + ESC {(FC_M+ESC_M)*1e3:.1f} g at {AX/G:.1f} g (in-plane, worst axis): {KP*(FC_M+ESC_M)*AX:.1f} N design over 8 bosses = {shear_boss:.2f} N each, bond {bond_b/1e6:.3f} MPa vs 2.0 MPa: RF {BOND/bond_b:.0f}. Foam bearing under 8 bosses (A 8 x 36 mm2) at {AZ/G:.1f} g normal: {KP*(FC_M+ESC_M)*AZ/(8*Apad)/1e3:.1f} kPa vs compression 103 kPa EST: RF {LP.F_COMP/(KP*(FC_M+ESC_M)*AZ/(8*Apad)):.0f}.")
def boss_v(h): return a*a*h*1e9 - 4.0*3.46*1.6 - math.pi/4*2.2**2*h*1e3   # mm3: 6x6 column less M2 nut pocket (4 across flats x 1.6, EST) and 2.2 mm hole
mb = [boss_v(h)*1e-3*RHO for h in hs]
print(f"- Boss mass (6 x 6 x h less M2 nut pocket and 2.2 mm hole, x1.27; thin walls solid): {[round(x,2) for x in mb]} g, total {sum(mb):.2f} g (T-070 EST 8 x 0.35 = 2.8 g). M2 nuts 8 x about 0.03 g (EST, not looked up). AVN-001 adopted 17.91 g removed. **dm = {sum(mb)-17.91:+.1f} g** (T-070: -15.0).")
R2_DM = sum(mb)-17.91
print("- Not covered by R2 and flagged for Phase 2 (the plate also carries them in the CAD): GPS 13.5 g + compass (x 45..70, y 27.5..52.5), receiver RP3 (x 102..124), cover AVN-008 seat, ESC lead lanes. Each needs its own pad/bond (mass not in R2: EST +1..3 g). ESC hole pattern/screw size: '-' (SpeedyBee 20 x 20 listing not re-read here).")
# ---------------- R4
print("\n## R4 tubular strut clamps CGE-007 (socket OD 9 x 25 mm, wall 1.5 mm; ring wall 2.5 mm)")
ux, uy, Ls = LP._strut_geom()
LP.set_pad(LP.PAD_D2["x_foot"], LP.PAD_D2["z_foot"])
mins = {}
for name, d in tr.items():
    for kk, (lab, a_) in LP.strut_checks(d['FB'], id_=4.0e-3, Lb_clamp=0.025).items():
        c = mins.get(kk, (1e9, ''))
        if float(a_.min()) < c[0]: mins[kk] = (float(a_.min()), name)
for kk, (v_, n_) in mins.items(): print(f"- strut 6x4.0, clamp bond length 25 mm: {kk}: RF {v_:.2f} ({n_})")
Nmax = 0.0
for name, d in tr.items():
    for k in (0, 1):
        N = np.sum([d['FB'][:, 2*k+j, 0] for j in (0, 1)], axis=0)/ux; Nmax = max(Nmax, float(np.abs(N).max()))
D = W.STRUT_OD
print(f"- strut peak axial {Nmax:.1f} N limit (23 cases, N = fin Fx / ux, ux {ux:.3f}, uy {uy:.3f}); x KP {KP*Nmax:.0f} N.")
print("| Tag | Check | Demand | Allowable | RF | Note |"); print("|---|---|---|---|---|---|")
for Lb in (0.0142, 0.020, 0.025):
    row("R4-a", f"strut-in-socket bond D6 x {Lb*1e3:.1f} mm", f"{KP*Nmax/(math.pi*D*Lb)/1e6:.2f} MPa", "2.0 MPa EST", rf(BOND, KP*Nmax/(math.pi*D*Lb)), "14.2 = the present solid block" if Lb == 0.0142 else "")
Aw = math.pi/4*(0.009**2-0.006**2); sw = KP*Nmax/Aw
row("R4-b", "socket wall axial (OD 9 / ID 6, A 35.3 mm2), axis in the print plane", f"{sw/1e6:.1f} MPa", "20 MPa in-layer EST (PETG_BEAR of arm_cup_checks)", rf(PETG_BEAR, sw), "if printed standing (interlayer 9.5 MPa) RF %.2f" % rf(PETG_ILAY, sw))
Ny = Nmax*uy; Nx = Nmax*ux; Mt = Nx*(0.060-W.STRUT_E[0])
tau_ring = math.hypot(KP*Ny/(math.pi*0.012*0.016), KP*Mt/(2*math.pi*0.006**2*0.016))
row("R4-c", "clamp ring on the spar (D12 x 16 mm bond): axial Ny + torque Nx x 10 mm, vector sum", f"{tau_ring/1e6:.2f} MPa", "2.0 MPa EST", rf(BOND, tau_ring), "ring wall does not change the bond area")
jun = KP*Nmax/(0.009*0.0025*2)
row("R4-d", "socket-to-ring junction: strut load through two 2.5 mm x 9 mm wall strips (EST footprint)", f"{jun/1e6:.1f} MPa", "9.5 MPa interlayer EST", rf(PETG_ILAY, jun), "needs 2 mm fillets / wider footprint (CAD)")

# T-076: R4 junction with fillets (hand calc, EST).  Each 2.5 mm x 9 mm strip gets a fillet of radius rf on both faces: thickness at the fillet tangent line 2.5 + 2 rf.
# Peak stress = nominal at the tangent section x Kt; Kt for a shoulder fillet in tension at r/t = rf/2.5 is taken from a fit of Peterson-type charts: EST (no source file read), 1.5 at r/t 0.8, 1.9 at r/t 0.4, 2.4 at r/t 0.2.
for rf_ in (1.0, 1.5, 2.0, 3.0):
    tt = 2.5+2*rf_; rt = rf_/2.5; kt = 2.4 if rt <= 0.2 else (1.9 if rt <= 0.4 else 1.5 if rt <= 0.8 else 1.3)
    sj = KP*Nmax/(0.009*tt*1e-3*2)*kt
    row("R4-d'", f"junction with fillets r {rf_:.1f} mm both faces (tangent thickness {tt:.1f} mm, Kt {kt} EST)", f"{sj/1e6:.1f} MPa", "9.5 MPa interlayer EST", rf(PETG_ILAY, sj), "CAD fillet needed; Kt EST")
vsock = math.pi/4*(81-36)*25; vring = math.pi/4*(17**2-12**2)*16; vjun = 200
vtot = (vsock+vring+vjun)/1e3
print(f"- R4 mass: socket {vsock/1e3:.2f} + ring {vring/1e3:.2f} + junction fillets {vjun/1e3:.2f} (EST) = {vtot:.2f} cm3 x {RHO} = {vtot*RHO:.2f} g each (thin walls, solid) against T-067 adopted 6.58: **dm = {2*(vtot*RHO-6.58):+.1f} g** for two (T-070: -5.2).")
R4_DM = 2*(vtot*RHO-6.58)
# R3 mass
d_sleeve = -math.pi/4*(19.2**2-17.2**2)*28.5/1e3 + 0.34          # cm3, wall 3.5 -> 2.5 mm over 28.5 mm, local pocket bosses +0.34 (EST)
old_plate = (33*33-(4-math.pi)*36)*5/1e3                          # 5.29 cm3
f_old = (2*1.0+3.0*0.40)/5.0                                       # T-067 S basis: 5 layers x 0.2 mm top/bottom, 40 % infill core
new_spec = 2.6                                                     # T-070 cross plate
reg5 = 13*33*5/1e3; web_cross = 33*20*0.55*3/1e3                   # r3fix: 5 mm over y 3.5..16.5 (13 mm of the 33), 3 mm cross web (55 % of 20 mm x 33) elsewhere (EST)
new_fix = reg5*f_old + web_cross
dm_spec = (d_sleeve + (new_spec - old_plate*f_old))*RHO*4
dm_fix = (d_sleeve + (new_fix - old_plate*f_old))*RHO*4
print(f"\n## R3 mass (cup CGE-003 x4): sleeve wall 3.5 -> 2.5 mm: {d_sleeve:+.2f} cm3 (incl. +0.34 local pocket bosses, EST); plate adopted-basis volume old {old_plate*f_old:.2f} (5.29 solid x {f_old:.2f}); new spec {new_spec:.2f}; r3fix {new_fix:.2f} (5 mm over the +y 13 mm x f_old + 3 mm cross web). dm x4 x 1.27: **spec {dm_spec:+.1f} g, r3fix {dm_fix:+.1f} g** (T-070: -12.0).")
print(f"\nSUMMARY dm (g, basic): R1 as specified {R1_DM:+.1f} (FAILS), R1'' passing {R1P_DM:+.1f}, R2 {R2_DM:+.1f}, R3 spec {dm_spec:+.1f} / r3fix {dm_fix:+.1f}, R4 {R4_DM:+.1f}")
