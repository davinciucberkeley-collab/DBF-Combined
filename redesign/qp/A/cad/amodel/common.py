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
WING_DZ = float(os.environ.get('A_WING_DZ', '0.005'))                            # D-194 (integrator): airfoil datum lowered 5.0 mm so the 12 mm spar bore (z 0) sits at mid-thickness of the S5010: foam above/below the bore 6.3 / 5.6 mm (was 11.3 / 0.6 mm at x 54-66, S5010 chord line z 0 -> lower skin -6.6 mm). CALC from s5010.dat
COORDS = k9.read_dat(os.path.join(REDESIGN, 'subsystems', 'wing', 's5010.dat'))   # D-193 (A1): Selig S5010, published coordinates, unscaled, 9.82 % t/c (UIUC s5010.dat, checked 2026-11-09; K09-L D-02); replaces reflex_placeholder(0.095, camber 0.012)
COORDS = [(x_, z_ - WING_DZ / C) for x_, z_ in COORDS]   # re-datum (normalised coordinates), see WING_DZ
T083_DX = -0.003                            # T-083 (D-227, A-P4 margin): cage, pack and tray-wall windows a further 3 mm forward (box x 493.9 -> about 496.9 mm of 500)
CAGE_DX = -0.012 + T083_DX                  # T-077 p4 (D-224 rung 3c): the whole cage (hub, arms, motors, props, doublers, pins, cups, conduits, raceway front, tray, collar, struts) 12 mm forward of the wing; bridge BR_X1 and strut ends stay at the wing, so bridge and struts get longer
HUB = (-0.069 + CAGE_DX, 0.0, 0.0)                    # D-205: hub 6 mm aft (DOC: -75) to win back forward trim after the D-202 hub; HUB_X1 (tray face) unchanged
YM, ZM = 0.228, 0.156                       # DOC: motors at y 0.228 / z 0.156
R_M = math.hypot(YM, ZM)                    # 0.2762 (DOC radius 0.276)
CANT = 17.0                                 # D-189 (was 16, D-184): yaw authority 0.3465 -> 0.363 N m
YFIN, XFIN_T, FIN_H = 0.38, 0.294, 0.18     # DOC: fins at y 380, tube at x 0.294, z +-0.18
FIN_OD, FIN_ID = 0.016, 0.014               # DOC 16x14 tube
PACK_X = (-0.0485 + T083_DX, -0.0155 + T083_DX)  # T-083: +3 mm forward with the cage. T-077 p4 (D-224 rung 3a + 3c): pack centre -32 mm absolute = -20 mm in the tray (tray front -57), 12 mm cage shift + 10 mm pack shift; held by two outboard straps (|y| 35), clear of the hub collar (|y| <= 12). Part 3 had (-0.0265, 0.0065)
PACK_X_P2 = (-0.0365, -0.0035)  # T-077 part 2 ladder rung 1: pack 10 mm forward (centre -20 mm, the QP-4 position; front lip -44.5..-42.5 on the root pad, hub face -45). T-077 RDQ 2800 pack 33 mm wide (was 35: -27.5..7.5), same centre -10 mm.                 # QP-4 7.2 #2: pack moved 10 mm aft (centre -10 mm; was -20 mm) so the CAD CG lands mid-band (23 mm) WITH the D-187 elevon balance and the ES3054HV servos; trim +-10 mm in the tray slots
TRIM = 0.010                                # +-10 mm pack trim travel (about +-2.2 mm of CG)
TRIM_FWD = 0.006                            # D-205: forward travel back to 6 mm (D-199 value; D-202 had cut it to 1 mm). The hub moved 6 mm aft (HUB -75 -> -69 mm), doublers s 11-25, lead 12.8 g: CAD CG 21.17 mm, forward trim end must stay >= 19.3 mm (claim CL-A-CG-TRIM-FWD >= 19). Aft travel TRIM unchanged.
TRAY_YI, TRAY_YO = 0.0540, 0.0560          # T-077: tray end wall inner / outer face |y| (RDQ pack 107 long = |y| 53.5 + 0.5 mm clearance; 2.0 mm wall; was 52.5 / 54.5)
TRAY_WALL_TOP = 0.0295                      # T-077: end wall top z (leads leave the end face at z 32, 1.5 mm radius: 1.0 mm over the wall)
TRAY_X0 = -0.045 + CAGE_DX                  # T-077 p4: tray plate front = the hub aft face (HUB_X1), x -57 mm
TRAY_X1 = -0.0028                           # T-077 p4: tray plate aft end -2.8 mm (was +21.5; first draft of part 4 kept +9.5): 2.8 mm aft of the pack's aft edge at +10 trim (-5.5) and the rear lip (-3.5); the two outboard straps (PWR-002) wrap the plate front and aft EDGES, so no slots are cut in the plate. The core tray slot (to 22.5) stays and is open aft of the tray
SERVO_Y = 0.200                             # EST (DOC landing_a: servo y 0.30 is in the elevon; moved inboard)
SV_Z1 = 0.0117 - WING_DZ                              # servo case top (servo case 28.4 x 13.0 x 26.7, see electrical.py); the core servo pocket opens at this z

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


# D-202: opposite arms are ONE continuous 12x10 tube each, crossing at the hub. Tube A (UR-LL) lies at x = HUB_x - 6.5 mm, tube B (UL-LR) at HUB_x + 6.5 mm
# (offsets symmetric, so the mean motor x is unchanged). Every motor station therefore sits TUBE_DX ahead of / behind the old common plane.
TUBE_DX = 0.0065                            # D-202 (qp/A/structures/fea_hub.py GEO XA / XB = -6.5 / +6.5 mm)
TUBE_OF = {'UR': 'A', 'LL': 'A', 'LR': 'B', 'UL': 'B'}              # tube that carries each station (A: UR at +s, LL at -s; B: LR at +s, UL at -s)
TUBE_X = {'A': HUB[0] - TUBE_DX, 'B': HUB[0] + TUBE_DX}             # x of each tube axis (m)
TUBE_PHI = {'A': math.degrees(math.atan2(ZM, YM)), 'B': -math.degrees(math.atan2(ZM, YM))}   # +s direction of the tube in the y-z plane (deg from +y); PHI['UR'] / PHI['LR']
XOFF = {s: TUBE_X[TUBE_OF[s]] - HUB[0] for s in ST}                 # station x offset from HUB_x
SIG = {'UR': 1, 'UL': 1, 'LR': -1, 'LL': -1}                        # D-202 phase-lead exit side on the tube tangential face: +1 = +t (t = x_hat cross u), -1 = -t (lower arms, see D-202 CAD note: strut socket)


def station(st):
    return (HUB[0] + XOFF[st], ST[st][0] * YM, ST[st][1] * ZM)


def mrot(st):
    return rot_to_axang(motor_R(st))


def mworld(st, p):
    """Point p in the motor-station frame -> world."""
    q = fk.mat_vec(motor_R(st), p)
    s = station(st)
    return tuple(q[i] + s[i] for i in range(3))

# ------------------------------------------------------------------ D-198 phase-lead conduit (shared: wing.py cuts it, electrical.py lays it)
PH_D = 0.0018                               # V phase-lead strand OD 1.8 mm: Pimoroni 20 AWG silicone listing (shop.pimoroni.com/en-us/products/dual-silicone-wire-per-metre, read 2026-11-15: OD 1.8 mm, 14.2 g per metre for the 2-conductor cable); the T-Motor MN2212 page lists 20 AWG x 400 mm leads (store.tmotor.com/goods-388-MN2212-V20.html, 2026-11-15) but not their OD: measure on arrival
PH_RHO = PH_D / math.sqrt(3.0)              # tri-bundle: strand centres on a circle of this radius
PH_ENV = PH_RHO + PH_D / 2                  # bundle envelope radius (1.94 mm)
PH_HOLE_R = 0.0024                          # printed lead hole radius (envelope + 0.46 mm)
PH_Y = 0.0180                               # T-083: cup lead hole y (cup frame). The X2216 leads leave the can radially at the base end (SunnySky drawing), so the hole sits
                                            # outside the can (r 13.85) after a 4 mm bend: 13.85 + 4 = 17.85 -> 18.0; collar bore y 3.5..20.5 holds the second bend (was 5.5 / 3.5..8.0, MN2212)
PH_XC = -0.0010                             # arm-run bundle x in the cup frame
PH_DT = 0.0027                              # bundle offset from the arm axis toward the up side (arm bore ID 10: 1.0 + 2.7 -> 2.9 + 1.94 = 4.83 < 5.0)


def arm_up_sign(st):
    """+1 if the arm-local +z (t) axis of station st points the same way as the tube t axis (right-hand stations UR, LR), else -1 (left: UL, LL)."""
    return 1.0 if ST[st][0] > 0 else -1.0


def a2w(st, q):
    """Arm-local point (x, y along the arm toward the motor, z = t) -> world. Arm frame: origin on the tube axis at the hub axis plane, x offset XOFF[st]."""
    p = fk.mat_vec(fk.rot_matrix('X', PHI[st]), q)
    return (HUB[0] + XOFF[st] + p[0], HUB[1] + p[1], HUB[2] + p[2])


def ph_arm_xz(st, R_IN_=None):
    """Arm-local (x, z) of the phase-lead bundle in the tube bore (D-202): on the side of the tube where the lead exits (SIG), 2.7 mm off the axis, 0.4 mm toward the cup (x-)
    so that it passes the 4.8 mm exit hole (radius 2.4) with the bundle envelope (radius 1.94) and clears the bore wall (2.7 + 1.94 = 4.64 < 5.0)."""
    return (PH_XD, PH_DT * SIG[st] * arm_up_sign(st))


PH_XD = 0.0                                 # D-202: bundle x offset in the tube bore (arm frame): on the hole axis, so the bundle (radius 1.94) passes the hole (radius 2.4) with 0.46 mm to spare


# ------------------------------------------------------------------ D-199 phase-lead raceway (shared: wing.py cuts the hub pad and the foam, electrical.py draws the printed parts and routes the bundles)
# One closed printed raceway per side (HRN-003-R / -L) runs from the hub aft face under the pack tray plate to the tray end (x 22.5), carrying the upper-arm and the
# lower-arm bundle of that side side by side; four printed hub conduits (HRN-004-*) take each bundle from the arm-socket floor hole, along the hub web, down (upper
# arms) or up (lower arms) into it. Past the tray end the bundles run in an open foam ditch under the bay cover, rise inside the cover and reach the ESC pads.
# All dimensions are drawn CAD features (printed, 0.6 mm wall, EST basis as the cover and lens caps); bundle = tri of 3 x 1.8 mm strands, envelope 3.88 mm.
RW_T = 0.0006                               # EST printed wall, 1 perimeter (as AVN-008)
RW_YO, RW_YI = (0.0142, 0.0238), (0.0148, 0.0232)     # raceway outer / interior y range (right side), interior 8.4 mm: two bundles side by side (lanes y 17.0 and 21.0, 4.0 apart)
RW_ZO, RW_ZI = (-0.0006, 0.0060), (0.0, 0.0054)       # outer z -0.6..6.0 (the top touches the tray plate underside z 6.0); interior 5.4 mm (bundle centre z 2.7)
RW_DX = HUB[0] + 0.075                      # D-205: raceway front and the conduit drop follow the hub (drawn for HUB x -75 mm; hub now 6 mm aft)
RW_XO0, RW_XI0, RW_X1 = -0.0588 + RW_DX, -0.0582 + RW_DX, 0.0225      # outer front, interior front, aft end (open) = end of the core tray slot
RW_YU, RW_YL, RW_ZB = 0.0170, 0.0210, 0.0027          # bundle lanes (upper-arm, lower-arm bundle) and bundle centre height in the raceway
CD_DX = 0.0038 + CAGE_DX                              # D-205: conduit drop shift aft (hub moved 6 mm; the drop column is held 3.8 mm so its aft wall stays ahead of the tray plate front x -45)
RW_XD = -0.052 + CD_DX                              # x of the vertical drop (hub conduit leg B) behind the hub; the arc of the 4 mm bend starts 4 mm ahead of it, inside leg B; strut socket boss clear by >= 1.4 mm
DITCH_X1 = 0.0320                           # foam ditch (open top, under the bay cover) x 22.5..32; the bundles rise at x 29
RW_XR = 0.029
PADN_X = (-0.0467 + CAGE_DX, -0.0440 + CAGE_DX)                 # hub tray-pad notch, x (pad x -46.2..-45)
PADN_Y, PADN_Z = (0.0138, 0.0244), (0.0029, 0.0111)   # y and z of the notch (full pad height so the raceway can be lowered from above)


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
AV_DX = -0.015                                # T-077 p5 (D-224 3b): the avionics group (FC, ESC, GPS, RX, XT60, bay cover) sits 15 mm further forward than in part 4; the plate is gone (R2): PLATE_I0/I1/X0/X1 now only fix the pad plane height ZP



# ------------------------------------------------------------------ parts table
PARTS = {}


def _load_printed_mass():
    import json
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'printed_mass.json')   # {pid: grams}, written by mechanism/out/T077_data/t077_write_printed_mass.py
    return json.load(open(p)) if os.path.exists(p) else {}


PRINTED_MASS = _load_printed_mass()


def P(pid, name, sub, mass_g, material, mob='make', elec=None, cg=None, **flags):
    mass_g = PRINTED_MASS.get(pid, mass_g)      # T-077 (T-067 s7 option A): printed parts = CAD volume x print basis from printed_mass.json, else the number given
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
