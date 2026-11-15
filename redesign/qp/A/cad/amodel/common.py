"""amodel/common.py - SHARED base of the concept A CAD model (split from a_model.py, refactor only, no geometry change).

OWNER: nobody alone. Every name defined here is used by more than one lane (A wing/cage, B propulsion, C electrical) or by the
registries, so CHANGING A VALUE HERE NEEDS COORDINATION between the lanes that use it (grep the other amodel/*.py files).

Shared constants (lane users): C, B, XH, ELEV_FRAC, ELEV_Y0, ELEV_Y1, ELEV_STOP, ELEV_POSE (A + C edges/assembly), COORDS (A, C),
SPAR_X, SPAR_OD, SPAR_ID (A), HUB, YM, ZM, R_M, CANT, PHI, ST (A + B + C: frames, motor stations), YFIN, XFIN_T, FIN_H,
FIN_OD, FIN_ID (A fins; C landing + pitot), PACK_X, TRIM, TRAY_X1 (A pack tray + C pack/harness), SERVO_Y, SV_Z1 (A servo
pocket in the core + C servos), XS/NST + PLATE_* + ZP (B ESC and C plate sit on the plate), SUBS.
Shared helpers: rot_to_axang, matmul3, motor_R, station, mrot, mworld, zu, zl, tube_g, P/PARTS, E/EDGES, STACK, WIRE, en, ELEC.

Frame: metres, x aft from the wing LE, y right, z up in cruise.
Labels in comments: DOC = number from an A document (file named), V = vendor page read 2026-11-15, EST = estimate /
CAD interpretation (listed in review/QP-3/CAD.md section 6), CALC = computed here.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # the cad/ folder (parent of amodel/), as in the old a_model.py
REDESIGN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for _p in (os.path.join(REDESIGN, 'fusion'), os.path.join(REDESIGN, 'interfaces')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import fusionkit as fk   # noqa: E402
import k09kit as k9      # noqa: E402

SUBS = ('wing', 'fins', 'cage', 'propulsion', 'power', 'avionics', 'mechanisms', 'landing', 'harness', 'assembly')
ST = {'UR': (1, 1), 'UL': (-1, 1), 'LR': (1, -1), 'LL': (-1, -1)}      # (y sign, z sign)

# ------------------------------------------------------------------ shared dimensions (m)
C, B = 0.245, 0.90                          # DOC STRUCTURES s1: chord, span
ELEV_FRAC = 0.25                            # EST elevon chord fraction (A documents give none)
XH = C * (1 - ELEV_FRAC)                    # hinge station
ELEV_Y0, ELEV_Y1 = 0.04, 0.35               # elevon y range; QP-4 FIXES item 2: outboard end 0.34 -> 0.35 for roll rate (fin plane y 0.372 inner face: 22 mm clear); inboard end EST
ELEV_STOP = 21.0                            # QP-4 FIXES2: MECHANICAL stops at +-21 deg (1 deg overtravel past the 20 deg authority, covers servo calibration)
ELEV_POSE = float(os.environ.get('A_ELEV_POSE', str(ELEV_STOP)))   # angle of the collision-sweep poses (joint limits); default = the stop; env A_ELEV_POSE = 20 or 22 for the +-20 / +-22 deg checks
SPAR_X, SPAR_OD, SPAR_ID = 0.060, 0.012, 0.010     # DOC iteration 2: CF 12x10 at x 60
COORDS = k9.reflex_placeholder(0.095, camber=0.012)      # EST: no A section file; 9.5 % t/c (DOC), K09-L placeholder camber
HUB = (-0.075, 0.0, 0.0)                    # DOC: hub (-75, 0, 0)
YM, ZM = 0.228, 0.156                       # DOC: motors at y 0.228 / z 0.156
R_M = math.hypot(YM, ZM)                    # 0.2762 (DOC radius 0.276)
CANT = 17.0                                 # D-189 (was 16, D-184): yaw authority 0.3465 -> 0.363 N m
YFIN, XFIN_T, FIN_H = 0.38, 0.294, 0.18     # DOC: fins at y 380, tube at x 0.294, z +-0.18
FIN_OD, FIN_ID = 0.016, 0.014               # DOC 16x14 tube
PACK_X = (-0.0275, 0.0075)                  # QP-4 7.2 #2: pack moved 10 mm aft (centre -10 mm; was -20 mm) so the CAD CG lands mid-band (23 mm) WITH the D-187 elevon balance and the ES3054HV servos; trim +-10 mm in the tray slots
TRIM = 0.010                                # +-10 mm pack trim travel (about +-2.2 mm of CG)
TRAY_X1 = 0.0215                            # tray plate aft end (pack aft edge at +TRIM is 17.5 mm; core tray slot ends at 0.0225)
SERVO_Y = 0.200                             # EST (DOC landing_a: servo y 0.30 is in the elevon; moved inboard)
SV_Z1 = 0.0117                              # servo case top (servo case 28.4 x 13.0 x 26.7, see electrical.py); the core servo pocket opens at this z

PHI = {s: math.degrees(math.atan2(ST[s][1] * ZM, ST[s][0] * YM)) for s in ST}

def rot_to_axang(R):
    tr = R[0][0] + R[1][1] + R[2][2]
    ang = math.degrees(math.acos(max(-1.0, min(1.0, (tr - 1) / 2))))
    if ang < 1e-9:
        return ('X', 0.0)
    v = (R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1])
    n = math.sqrt(sum(c * c for c in v))
    return (tuple(c / n for c in v), ang)


def matmul3(A, Bm):
    return [[sum(A[i][k] * Bm[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def motor_R(st):
    return matmul3(fk.rot_matrix('X', PHI[st]), fk.rot_matrix('Y', CANT))


def station(st):
    return (HUB[0], ST[st][0] * YM, ST[st][1] * ZM)


def mrot(st):
    return rot_to_axang(motor_R(st))


def mworld(st, p):
    """Point p in the motor-station frame -> world."""
    q = fk.mat_vec(motor_R(st), p)
    s = station(st)
    return tuple(q[i] + s[i] for i in range(3))

# ------------------------------------------------------------------ airfoil helpers
def zu(x):
    return k9.surface_z(COORDS, C, x / C, 'upper')


def zl(x):
    return k9.surface_z(COORDS, C, x / C, 'lower')


NST = 32
XS = [XH * (1 - math.cos(math.pi * i / NST)) / 2 for i in range(NST + 1)]



PLATE_I0, PLATE_I1 = 10, 20                   # QP-4: plate starts at x 40.8 mm (was 26.9) to clear the pack at +10 mm trim
PLATE_X0, PLATE_X1 = XS[PLATE_I0], XS[PLATE_I1]
PLATE_ZTOP = max(zu(x) for x in XS[PLATE_I0:PLATE_I1 + 1]) + 0.0015
PLATE_Y = 0.055
ZP = PLATE_ZTOP



# ------------------------------------------------------------------ parts table
PARTS = {}


def P(pid, name, sub, mass_g, material, mob='make', elec=None, cg=None, **flags):
    PARTS[pid] = dict(id=pid, name=name, subsystem=sub, mass_g=mass_g, material=material, make_or_buy=mob,
                      electrical=elec, cg=cg, **flags)


def tube_g(d, o, i):
    return math.pi / 4 * (o ** 2 - i ** 2) * d * 1600 * 1000        # CF tube mass g (rho 1600, STRUCTURES)

# ------------------------------------------------------------------ edges table
EDGES = []


def STACK(f, n, hole, order, eng=5.0, mineng=3.0):
    return dict(fastener=f, count=n, grade='A2-70', hole=hole, insert='none', engagement_mm=eng, min_engagement_mm=mineng,
                washer_nut='none', torque='snug + threadlocker', tool='2.0 mm hex key',
                access='from the aft side before the arm is bonded', install_order=order, removal_order=order)


def WIRE(awg, conn, rid, sup, bend, strain, disc=False):
    return dict(gauge_awg=awg, connector=conn, route_id=rid, support_points=sup, bend_radius_mm=bend,
                strain_relief=strain, disconnect=disc)


def E(eid, a, b, via, owner, notes='', **kw):
    EDGES.append(dict(id=eid, part_a=a, part_b=b, via=via, owner=owner, notes=notes, **kw))


_n = {}


def en(prefix):
    _n[prefix] = _n.get(prefix, 0) + 1
    return 'E-%s-%02d' % (prefix, _n[prefix] + (1 if prefix == 'WNG' else 0))


EPX, CA, TAPEF = 'CT-EPOXY', 'CT-CA', 'CT-TAPE-FOAM'
ELEC = {}                                   # ELEC[eid] = wire diameter in the CAD (filled by electrical.py, read by build_assembly)
