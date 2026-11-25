"""T-083: motor mount and cup rows for the X2216 V3 on its SunnySky X-mount (PRP-006) bolted to the printed cup CGE-003. Category: HAND CALCULATION (statics,
bolt-group, plate strips) on loads from the prop_a.py EST model; no FEA.  python -I t083_cup_checks.py  -> prints markdown (t083_cup_checks.md written beside it).
Method, factors and allowables are those of T077p6_data/t077p6_cups.py / arm_cup_checks_p6.md (KF 1.5 x 1.15 = 1.725, KP = KF x 1.25 = 2.156; PETG bearing 20 MPa,
interlayer 9.5 MPa, M3 steel 450 MPa tension, thread shear in the Al motor base 90 MPa: all EST as there; MS >= 0.15 = PASS, 0..0.15 MARGINAL). The prop strike is
judged with the ultimate factors as in that file. Rows that do not depend on the motor mount (arm root, bonds, fatigue) are scaled by the load ratio stated in each row."""
import math, os, sys
H = os.path.dirname(os.path.abspath(__file__))
A = os.path.abspath(os.path.join(H, '..', '..', '..'))
sys.path.insert(0, A); sys.path.insert(0, os.path.join(A, 'cad')); sys.dont_write_bytecode = True
import prop_a as PA
from amodel import propulsion as PR, wing as W
KF = 1.5 * 1.15; KP = KF * 1.25
ROWS = []


def row(item, load, val, allow, note=''):
    ms = allow / val - 1 if val > 0 else 99
    ROWS.append((item, load, '%.2f MPa' % val, '%.1f MPa' % allow, ms, 'PASS' if ms >= 0.15 else ('MARGINAL' if ms >= 0 else 'FAIL'), note))


# ---- geometry (m), from the CAD modules (T-083)
X_PROP = -(PR.X_FLANGE_TOP - PR.HUB_T_P / 2)      # prop mid-plane above the arm axis (cup frame x = 0): 55.3 mm (was 47.0)
LEV_PLATE = X_PROP - 0.012                         # above the plate front face (bolt group plane)
LEV_BASE = X_PROP + PR.X_MB                        # above the motor base face (inner screw group)
R_B = 17.0e-3                                      # X-mount bolt radius (34 mm spans), arms on the diagonals
SIG_D2 = 2 * R_B ** 2                              # sum of d^2 of 4 bolts on a circle at 90 deg, any in-plane axis
R19, R16 = PR.PAT19 / 2, PR.PAT16 / 2
NUT_A = 3 * math.sqrt(3) / 2 * (0.0055 / math.sqrt(3)) ** 2 - math.pi / 4 * 0.0034 ** 2     # M3 nyloc bearing annulus on the plate (s 5.5, hole 3.4)
HEAD_A = math.pi / 4 * (0.0055 ** 2 - 0.0031 ** 2)                                          # M3 SHCS head on the X-mount (hole 3.1)
AS_M3 = 5.03e-6                                    # M3 tensile stress area
# ---- loads
cap = 0.993                                        # fresh pack-current cap at Q_M_BAT_CURR_MAX 72 A (t083_packcap.py, 1.913 kg)
n, i, th, pw, vb = PA.full(16.8, cap)
T_CAP = th * PA.DER                                # thrust per motor at the cap, fresh, derate 0.93
Q_CAP = pw / (n * 2 * math.pi / 60)
n1, i1, th1, pw1 = PA.run(16.8)                    # FAULT: one motor uncapped at the fresh rest voltage (no pack sag), table thrust
F1P = 1e-6 * (n * 2 * math.pi / 60) ** 2           # 1P from U = 1.0 g mm (A-P10 (b) basis) at the cap rpm
T_HOV = PA.hover(1.913, PA.DER)[0] / 1000 * 9.807
S = 30.0                                           # prop strike, N (arm_cup_checks basis, damage case judged with KF/KP as there)
Q_STOP = 2.4                                       # blade-stop torque N m (S3, as there)

# ---- X-mount to plate bolts (4 x M3x14 + nyloc at r 17)
Ts2 = S * LEV_PLATE * R_B / SIG_D2 + T_HOV / 4
row('S2 transverse 30 N at the prop mid-plane (%.1f mm above the plate): worst mount-bolt tension + hover share; M3 stress area' % (LEV_PLATE * 1e3), '%.1f N/bolt' % Ts2, Ts2 * KF / AS_M3 * 1e-6, 450.0)
row('S2: nyloc bearing on the PETG plate back face (annulus %.1f mm2)' % (NUT_A * 1e6), '%.1f N/bolt' % Ts2, Ts2 * KP / NUT_A * 1e-6, 20.0, 'no washer; a 7 mm washer halves it')
row('S2: bolt head bearing on the X-mount (Al, EST)', '%.1f N/bolt' % Ts2, Ts2 * KF / HEAD_A * 1e-6, 240.0, 'X-mount material not stated: 6061-T6 240 MPa assumed (EST, "-")')
# plate strips: -y bolts on the 4.2 mm web, cantilever from the sleeve + 1 mm fillet edge (|z| 8.9) to the bolt (|z| 12.02); +y bolts on the 5.0 mm cantilever, from the collar + web edge (|z| 8.0)
for tag, t_, edge in (('-y bolts, 4.2 mm web, arm %.1f mm', 0.0042, 0.0089), ('+y bolts, 5.0 mm plate, arm %.1f mm', 0.0050, 0.0080)):
    arm = R_B / math.sqrt(2) - edge; w_eff = 0.0055 + 2 * t_       # EST strip width: nut flats + 2 x thickness (45 deg spread)
    M = Ts2 * arm
    row('S2: plate strip bending at the nut, ' + tag % (arm * 1e3) + ' (strip %.1f mm, EST)' % (w_eff * 1e3), '%.0f N mm' % (M * 1e3), 6 * M * KP / (w_eff * t_ ** 2) * 1e-6, 9.5, 'interlayer allowable (worst), as the p6 plate rows')
    row('S2: plate punching shear round the nut (pi x 5.5 x %.1f mm), interlayer' % (t_ * 1e3), '%.1f N/bolt' % Ts2, Ts2 * KP / (math.pi * 0.0055 * t_) * 1e-6, 9.5)
# X-mount arm between the inner motor screw and the outer bolt (net section at the inner hole: (7 - 3.2) x 3 mm)
arm_x = R_B - R16
Zn = (0.007 - 0.0032) * 0.003 ** 2 / 6
row('S2: X-mount arm bending at the inner hole, lever %.1f mm (net 3.8 x 3 mm; material "-", 6061-T6 240 MPa assumed, EST)' % (arm_x * 1e3), '%.0f N mm' % (Ts2 * arm_x * 1e3), Ts2 * arm_x * KF / Zn * 1e-6, 240.0,
    'the "7" arm width is read off the drawing (EST)')
# motor countersunk screws into the motor base (2.0 mm engagement in 4-M3 x 2.8 deep)
Mb = S * LEV_BASE
Tm = Mb * R19 / (2 * R19 ** 2) + T_HOV / 4
row('S2: motor countersunk M3 into the base, thread strip at 2.0 mm engagement (lever %.1f mm above the base, 19-pair carries it)' % (LEV_BASE * 1e3), '%.1f N/screw' % Tm,
    Tm * KF / (math.pi * 0.00268 * 0.0020 * 0.5) * 1e-6, 90.0, 'base alloy not published (EST), as p6')
row('S1 axial 30 N: nyloc bearing on the plate (4 bolts)', '%.1f N/bolt' % (S / 4), S / 4 * KP / NUT_A * 1e-6, 20.0)
# S3 blade stop: torque through the 4 bolts at r 17 in shear and bearing in the PETG plate (hole 3.4 x plate t)
Vb = Q_STOP / (4 * R_B)
row('S3 blade stop %.1f N m: bolt bearing in the PETG plate hole (3.0 x 4.2 mm), 4 bolts at r 17' % Q_STOP, '%.1f N/bolt' % Vb, Vb * KP / (0.003 * 0.0042) * 1e-6, 20.0, 'p6 had 97 N/screw on 2 of 4 M2.5 at r 12.4')
row('S3: M3 bolt shank single shear', '%.1f N/bolt' % Vb, Vb * KF / (math.pi / 4 * 0.003 ** 2) * 1e-6, 270.0)
# cap thrust + torque + 1P on the bolts (prying 2x as p6)
Tc = (2 * T_CAP + F1P) / 4
row('Thrust at the cap %.1f N (fresh, Q_M_BAT_CURR_MAX 72 A, derate 0.93) x2 prying + 1P %.2f N: nyloc bearing' % (T_CAP, F1P), '%.1f N/bolt' % Tc, Tc * KP / NUT_A * 1e-6, 20.0)
row('FAULT one motor uncapped %.1f N (table) x2 prying: nyloc bearing' % th1, '%.1f N/bolt' % (th1 / 2), th1 / 2 * KP / NUT_A * 1e-6, 20.0)
# scaled p6 rows (arm_cup_checks_p6.md) by the load ratio
r_thr = T_CAP / 8.8
row('Arm 12x10 root bending, thrust at the cap + torque (p6 42.64 MPa at 8.8 N x %.2f)' % r_thr, '%.2f N m' % (2.17 * r_thr), 42.64 * r_thr, 350.0)
r_lev = X_PROP / 0.047
row('S2/S3 cup-to-arm bond, torsion 30 N x %.1f mm + torque couple 2.4 N m / 25 mm (p6 0.69 MPa; torsion part x %.2f, upper bound on the vector sum)' % (X_PROP * 1e3, r_lev), '-', 0.69 * r_lev, 2.0)
row('Arm 12x10 root bending, strike force at the blade (lever 0.246 + 0.080 m; the 8 mm higher prop plane does not change it)', '9.8 N m', 192.07, 350.0)
row('FATIGUE cup bond, 1P couple at %.1f mm (p6 0.01 MPa x %.2f)' % (X_PROP * 1e3, r_lev * F1P / 0.96), '-', 0.01 * r_lev * F1P / 0.96, 0.6)
out = ['# T-083 motor mount + cup rows (hand calculation, EST allowables as T077p6 cups; X2216 V3 on the SunnySky X-mount)', '',
       'Loads: cap thrust %.2f N/motor at %.0f rpm, torque %.3f N m (prop_a EST, fresh, cap %.3f); FAULT uncapped %.2f N; 1P %.2f N (U 1 g mm); hover %.2f N; strike 30 N; blade stop 2.4 N m.' % (T_CAP, n, Q_CAP, cap, th1, F1P, T_HOV),
       'Geometry: prop mid-plane %.1f mm above the arm axis (was 47.0), %.1f mm above the plate, %.1f mm above the motor base; bolts r 17 on the diagonals (|y|, |z| 12.02).' % (X_PROP * 1e3, LEV_PLATE * 1e3, LEV_BASE * 1e3), '',
       '| Item | Load | Stress | Allowable | MS | Result | Note |', '|---|---|---|---|---|---|---|']
for r in ROWS:
    out.append('| %s | %s | %s | %s | %+.2f | %s | %s |' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
out.append('')
out.append('Thrust-line tilt / arm tip deflection at the cap scale with thrust: p6 1.36 mm / 0.48 deg at 8.8 N (kd) -> %.2f mm / %.2f deg at %.1f N (info; no limit in the repo).' % (1.36 * r_thr, 0.48 * r_thr, T_CAP))
out.append('Minimum MS: %+.2f (%s)' % min((r[4], r[0][:70]) for r in ROWS))
open(os.path.join(H, 't083_cup_checks.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
