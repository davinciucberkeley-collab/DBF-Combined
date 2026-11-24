"""D-195 (QP-5): structural re-checks after the CAD fidelity round (D-193/D-194). python -I qp5_checks.py -> qp5_checks.md (stdlib).
Factors as structures_a.py / foam_103.py: KF = 1.5 x 1.15 (ultimate on metal / tube), KP = 1.5 x 1.15 x 1.25 (printed / bonded).
Labels: CALC computed here, EST estimate, V vendor/source."""
import math, os
KF, KP = 1.5 * 1.15, 1.5 * 1.15 * 1.25
L = []
def P(s=""): print(s); L.append(s)
# ---------------------------------------------------------------- 1 pushrod buckling
d = 1.2e-3; E = 200e9            # steel rod, E 200 GPa (EST: music wire A228 is 205-210 GPa; no vendor value read)
I = math.pi * d ** 4 / 64; A = math.pi * d * d / 4
T_stall = 0.397; ARM = 0.012     # N m ES3054HV stall at 7.2 V (review/QP-4/SERVO.md), servo arm 12 mm (CAD ARM_X1; D-194 arm perpendicular to the rod)
P("## 1 Pushrod buckling (1.2 mm steel, Euler, pinned-pinned: Z-bend pin in the arm hole and clevis pin are pins)"); P()
P("| rod length (mm) | Pcr (N) | stall load F = T/(arm cos beta) at beta 0 / 18.3 deg (N) | ultimate F x KF (N) | MS at 18.3 deg | result |"); P("|---|---|---|---|---|---|")
for Lr in (42.5, 52.5):
    Pcr = math.pi ** 2 * E * I / (Lr * 1e-3) ** 2
    F0 = T_stall / ARM; F18 = T_stall / (ARM * math.cos(math.radians(18.3)))
    ms = Pcr / (F18 * KF) - 1
    P("| %.1f%s | %.0f | %.1f / %.1f | %.1f | %+.2f | %s |" % (Lr, " (FIXES2, superseded)" if Lr == 42.5 else " (CAD, D-194)", Pcr, F0, F18, F18 * KF, ms, "PASS" if ms >= 0.15 else ("MARGINAL" if ms >= 0 else "FAIL")))
sig = F18 * KF / A
P(); P("Axial stress at the ultimate stall load: %.0f MPa (yield of music wire 1,500+ MPa, EST: not a limit). Fault case: the servo driven into the +-21 deg stop pushes the full stall torque; no flight load comes near it (hinge moment 0.048 N m per elevon at 18 m/s and 20 deg, fwd_checks.py: rod load %.1f N)." % (sig / 1e6, 0.0483 / 0.0129))
P("Effective-length factor 1.0 is the conservative end (the Z-bend end is a pin; a clevis pin through the horn blade is a pin); free play makes it no worse. Travel: rod load changes sign with the stall direction, so compression is the governing case both ways.")
# ---------------------------------------------------------------- 2 hub arm socket wall
P(); P("## 2 Hub arm socket wall (printed PETG boss round the 12 mm arm tube, 25 mm deep; wall HUB_W)"); P()
F = 8.3 / 0.025                  # N, strike couple 8.3 N m over the 25 mm socket (structures_run.md line 210)
r_in = 6.0e-3
P("Load: prop-strike couple 8.3 N m -> reaction pair F = %.0f N (structures_run.md). Model (CALC, crude): the reaction at the mouth bears on a patch of axial length l; the boss wall is a thin ring in hoop tension N = 2F/(pi l), sigma = KP N / t." % F)
P("Allowable: printed PETG, XY, knock-down 20 MPa (structures_run.md line 212 'PETG socket wall bearing ... 20.0 MPa', EST).")
P(); P("| wall t (mm) | l = 12 mm: sigma (MPa) | MS | l = 6 mm (about 2.5 sqrt(r t) for a thin shell near the mouth): sigma (MPa) | MS | result |"); P("|---|---|---|---|---|---|")
for t in (0.8, 1.2, 1.6, 2.0):
    out = []
    for l in (12e-3, 6e-3):
        s = KP * 2 * F / (math.pi * l * t * 1e-3); out += [s / 1e6, 20e6 / s - 1]
    P("| %.1f | %.1f | %+.2f | %.1f | %+.2f | %s |" % (t, out[0], out[1], out[2], out[3], "PASS" if out[3] >= 0 else ("PASS (l 12 only)" if out[1] >= 0 else "FAIL")))
P()
P("D-196 (2026-11-15): arm-socket wall set to 2.0 mm over the outer 12 mm of each socket (HUB_SOCK_W, HUB_MOUTH, cad/amodel/wing.py; 0.8 mm deeper in, where the arm tube is bonded and the bearing patch does not reach). It passes this crude model only with the 12 mm bearing patch (MS above); the 6 mm patch still fails, so the claim stays UNVERIFIED until the socket coupon pull test (print, bond, load to 332 N x 1.5) on the bench.")
P(); P("## 2b Bridge sleeve wall (D-196: 1.2 mm, HUB_SLV_W)"); P()
Fs = 8.3 / 0.057               # N, same strike couple reacted over the 57 mm sleeve (HUB_X1 - HUB_X0, wing.py)
P("Load: strike couple 8.3 N m reacted along the 57 mm bridge sleeve -> F = %.0f N; same ring model and allowable as s2." % Fs); P()
P("| wall t (mm) | l = 12 mm: sigma (MPa) | MS | l = 6 mm: sigma (MPa) | MS |"); P("|---|---|---|---|---|")
for t in (0.8, 1.2, 2.0):
    out = []
    for l in (12e-3, 6e-3):
        s_ = KP * 2 * Fs / (math.pi * l * t * 1e-3); out += [s_ / 1e6, 20e6 / s_ - 1]
    P("| %.1f | %.1f | %+.2f | %.1f | %+.2f |" % (t, out[0], out[1], out[2], out[3]))
P(); P("1.2 mm matches the socket case (passes at l = 12 mm); the coupon test covers both. Hub CGE-001 drawn mass 13.1 -> 17.7 g (+4.6 g; a full-length 2.0 mm socket and sleeve would be 24.7 g).")
P()
# ---------------------------------------------------------------- 3 spar foam
P("## 3 Spar foam after the datum change (foam above / below the 12 mm bore 6.27 / 5.62 mm, min 5.65 mm over x 54-66: CAD-INTEGRATION s3 item 1)"); P()
allow_sh = 100e3 * 103 / 120      # foam_103.py shear allowable (EST)
rows = []
T_br = 2.44; r_sp = 6e-3
for Ls in (0.30, 0.40):
    tau = T_br / (2 * math.pi * r_sp ** 2 * Ls) * KP; rows.append(("Bridge pitch torque 2.44 N m through the bond on the bore (r 6 mm), bonded |y| <= %.2f m" % (Ls / 2), tau))
tl = 5.62e-3; Wn = 3.4 * 1.47 * 9.81 / 0.90          # N/m lift per span at n 3.4, 1.47 kg gate
rows.append(("Spar-to-skin shear in the thinner ligament (5.62 mm each of two planes), lift 3.4 g x 1.47 kg", Wn / (2 * tl) * 1.5))
rows.append(("Bridge torque carried by the ligament ring (outer radius 6 + 5.62 mm), bond |y| <= 0.20 m", T_br / (2 * math.pi * (r_sp + tl) ** 2 * 0.40) * KP))
P("| check | shear stress (kPa) | allowable 86 kPa (EST, foam_103.py) | MS |"); P("|---|---|---|---|")
for n_, s in rows: P("| %s | %.1f | %.0f | %+.2f |" % (n_, s / 1e3, allow_sh / 1e3, allow_sh / s - 1))
P(); P("The thinner ligament (5.62 mm, was 0.6 mm in the placeholder-datum CAD) is not shear-limited; the bond rule |y| <= 0.20 m (FIXES2) still governs. Foam allowables are EST (no FOAMULAR 150 shear row).")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "qp5_checks.md"), "w").write("\n".join(L))
