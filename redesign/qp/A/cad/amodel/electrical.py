"""amodel/electrical.py - LANE C (avionics, power, mechanisms, harness, hardware): pack (PWR-001) + strap (PWR-002), avionics plate +
FC stack / RX / GPS / airspeed / pitot (AVN-*), servos / arms / pushrods / horns (MEC-*), landing feet (GER-*, kept here so the
PARTS/EDGES registration order stays identical), harness wires (real gauges), XT60 female + tail (HRN-002), modelled hardware sets
(HWC-*), the remaining lumps (HRN-001, HRD-001), electrical edges, and builders build_power / build_avionics / build_mechanisms /
build_landing / build_harness / build_assembly (the generic joint pass over EDGES). Lane C also owns gen_interfaces.py.

CAD FIDELITY ROUND (2026-11-15, QP-5 CAD-FIDELITY-AUDIT.md lane C). Source labels in comments:
  V  = vendor page read 2026-11-15 (URL given); DOC = repo document; CALC = computed here; ISO = standard value;
  EST = estimate / CAD interpretation, NOT published: every EST dimension is "measure on arrival" and is listed in the lane C report;
  "-" = not published, not drawn.
Lane C edits only this file. It reads shared constants from common.py (PACK_X, TRIM, TRAY_X1, SERVO_Y, SV_Z1, PLATE_*/ZP, FIN_*,
YFIN, XFIN_T, ELEV_POSE ...) and imports ESC_PADS / ESC_TOP from propulsion.py (lane B): every wire route that ends on the ESC uses
those names, so moving the ESC pads moves the routes. IMPORT ORDER MATTERS: amodel/__init__.py imports wing, propulsion,
electrical in that order.
"""
import math

from .common import *   # noqa: F401,F403
from .wing import HINGE_Z, R_IN   # noqa: F401  (read only: hinge axis height for the horn hole radius)
from .propulsion import ESC_PADS, ESC_TOP   # noqa: F401  (harness wires land on the ESC pads; lane B owns them)

MM = 0.001


# ------------------------------------------------------------------ small geometry helpers (2-D loops, 3-D vectors)
def _ring(cx, cy, r, n=14, ph=0.0):
    return [(cx + r * math.cos(ph + 2 * math.pi * i / n), cy + r * math.sin(ph + 2 * math.pi * i / n)) for i in range(n)]


def _rrect(x0, y0, x1, y1, r, n=4):
    """Counter-clockwise rounded rectangle."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _hex(cx, cy, af, ph=math.pi / 6):
    return _ring(cx, cy, af / math.sqrt(3), 6, ph)


def _sub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def _add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def _mul(a, k):
    return tuple(a[i] * k for i in range(3))


def _dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a):
    n = math.sqrt(_dot(a, a))
    return tuple(c / n for c in a)


def _strands(P, d, offs):
    """Round strands of diameter d laid along polyline P. offs: list of (a, b) offsets (m) along (side, up), constant, or a list of (a, b)
    per vertex. Rotation-minimising frame per segment; each corner is MITRED (the two offset lines are intersected), so strands of one
    bundle keep their spacing round a bend (D-194: the old per-vertex offsets let strands cross by 0.4-0.5 mm at corners).
    Returns [(polyline, d), ...] for ctx.wire(strands=)."""
    n = len(P)
    segs = [_unit(_sub(P[i + 1], P[i])) for i in range(n - 1)]
    ref = (0.0, 0.0, 1.0) if abs(segs[0][2]) < 0.9 else (1.0, 0.0, 0.0)
    side = _unit(_cross(ref, segs[0]))
    fr = [(side, _cross(segs[0], side))]
    for i in range(1, n - 1):
        e0, e1 = segs[i - 1], segs[i]
        ax = _cross(e0, e1)
        if _dot(ax, ax) < 1e-12:
            fr.append(fr[-1])
            continue
        ax = _unit(ax)
        cth, sth = _dot(e0, e1), _dot(_cross(e0, e1), ax)

        def rot(v):          # Rodrigues rotation about ax by the bend angle
            return _add(_add(_mul(v, cth), _mul(_cross(ax, v), sth)), _mul(ax, _dot(ax, v) * (1 - cth)))
        sd = rot(fr[-1][0])
        fr.append((sd, _cross(e1, sd)))
    out = []
    for o in offs:
        off = []
        for i in range(n - 1):
            a_, b_ = o[i] if isinstance(o, list) else o
            off.append(_add(_mul(fr[i][0], a_), _mul(fr[i][1], b_)))
        line = [_add(P[0], off[0])]
        for i in range(1, n - 1):
            q1, q2 = _add(P[i], off[i - 1]), _add(P[i], off[i])
            e0, e1 = segs[i - 1], segs[i]
            w = _sub(q2, q1)
            c = _dot(e0, e1)
            den = 1 - c * c
            if den < 1e-9:
                line.append(q1)
                continue
            sct = (_dot(w, e0) - c * _dot(w, e1)) / den       # q1 + s e0 meets q2 + u e1 (coplanar for a rotation-minimising frame)
            line.append(_add(q1, _mul(e0, sct)))
        line.append(_add(P[-1], off[-1]))
        out.append((line, d))
    return out


def _terms(ctx, eid, margin=0.0003):
    """Solder joint / crimp block (EST) on the host part at each strand end of the wire just registered, so the strand ends sit in a part
    (a wire end must be seated). Block = strand diameter + 2 x margin, centred on the end point."""
    w = ctx.wires[-1]
    ed = [e for e in EDGES if e['id'] == eid][0]
    pa, pb = ed['part_a'], ed['part_b']
    for line, d in (w.strands or [(w.points, w.dia)]):
        for pt in (line[0], line[-1]):
            def _dist(pid):                                  # distance from the end point to the part's world bounding box
                (l0, l1) = ctx.components[pid].bbox()
                return math.sqrt(sum(max(l0[k] - pt[k], 0.0, pt[k] - l1[k]) ** 2 for k in range(3)))
            host = pa if _dist(pa) <= _dist(pb) else pb
            h = ctx.components.get(host)
            if h is None:
                continue
            r = d / 2 + margin
            pt = h.to_local(pt)
            h.box((pt[0] - r, pt[1] - r, pt[2] - r), (pt[0] + r, pt[1] + r, pt[2] + r), name='solder joint / crimp at the wire end (EST)')


def _tri(d):
    r = d / math.sqrt(3)
    return [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in (90, 210, 330)]


def _legs(part, P, d, name, ext=True):
    """Round wire body along an axis-aligned polyline P (cylinders; interior ends extended by the radius so corners close)."""
    r = d / 2
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        k = [j for j in range(3) if abs(b[j] - a[j]) > 1e-9]
        assert len(k) == 1, 'wire leg not axis-aligned'
        k = k[0]
        s = 1.0 if b[k] > a[k] else -1.0
        p0, p1 = list(a), list(b)
        if ext and i > 0:
            p0[k] -= s * r
        if ext and i < len(P) - 2:
            p1[k] += s * r
        part.cylinder('XYZ'[k], tuple(p0), p1[k] - p0[k], r, name=name)


def _pcb(part, x0, y0, x1, y1, z0, t, holes=(), hole_r=1.1 * MM, r=1.0 * MM, name='PCB'):
    loops = [_rrect(x0, y0, x1, y1, r, 3)] + [_ring(hx, hy, hole_r, 12) for hx, hy in holes]
    part.prism('Z', z0, loops, t, name=name)


def _pad(part, x, y, z, name, s=1.6 * MM, h=0.25 * MM):
    part.box((x - s / 2, y - s / 2, z), (x + s / 2, y + s / 2, z + h), name=name)


RHO_STEEL, RHO_PA66, RHO_BRASS = 7.9, 1.14, 8.5          # g/cm3 ISO / catalogue (A2 stainless 7.9, nylon PA66 1.14)


def _g_screw(d, L, dk, k, rho=RHO_STEEL):
    """CALC: pan-head screw mass g (shank + 0.85 x head disc for the dome and recess)."""
    return rho * (math.pi / 4 * d * d * L + 0.85 * math.pi / 4 * dk * dk * k) * 1e6


def _g_nut(af, m, d, rho=RHO_STEEL):
    return rho * ((math.sqrt(3) / 2 * af * af - math.pi / 4 * d * d) * m) * 1e6


# ------------------------------------------------------------------ D-198 bay cover (AVN-008) and servo-lead grooves
COV_X0, COV_X1 = 0.0225, 0.1265             # cover roof from the tray end to just ahead of the plate end (plate x 40.8..127.0)
COV_Y = 0.0265                              # half width: clear of the GPS board (y >= 27.5) with a 0.6 mm wall
COV_T = 0.0006                              # printed single wall 0.6 mm (same basis as the lens caps WNG-008, EST)
COV_ZH1, COV_ZH2 = 0.0450, 0.0325           # roof heights: over the FC stack (screw heads to 38.5, sensor leads at 40.5 +- 0.5) and over the ESC with the phase bundles (z 29)
SRV_YD = 0.024                              # servo leads drop through the plate window (x 80..122, y 21..40) at |y| 24 mm
SRV_XD = 0.083
SRV_YG = 0.190                              # groove end: 10 mm inboard of the servo centre line
RHO_PETG_ = 1.27


def cov_outer():
    """Roof outer profile (x, z) from the skin at the front, ramp, flat over the FC, step, flat over the ESC, aft wall down to the plate."""
    return [(COV_X0, zu(COV_X0)), (0.040, COV_ZH1), (0.080, COV_ZH1), (0.0833, COV_ZH2), (COV_X1, COV_ZH2), (COV_X1, ZP)]


def cov_loops():
    o = cov_outer()
    i = [(o[0][0] + 0.0012, zu(COV_X0 + 0.0012))] + [(x, z - COV_T) for x, z in o[1:-2]] + [(o[-2][0] - COV_T, o[-2][1] - COV_T), (COV_X1 - COV_T, ZP)]
    return o + i[::-1]


def cov_side_loop():
    """End wall: region under the roof outer line, down to the skin (ahead of the plate) and the plate top (over it)."""
    o = cov_outer()
    bot = [(COV_X1, ZP), (PLATE_X0, ZP), (PLATE_X0, zu(PLATE_X0))] + [(COV_X0 + (PLATE_X0 - COV_X0) * (1 - k / 4.0), zu(COV_X0 + (PLATE_X0 - COV_X0) * (1 - k / 4.0))) for k in range(1, 5)]
    return o[:-1] + bot[:-1] if False else o + [(PLATE_X0, ZP), (PLATE_X0, zu(PLATE_X0))] + [(COV_X0 + (PLATE_X0 - COV_X0) * k / 4.0, zu(COV_X0 + (PLATE_X0 - COV_X0) * k / 4.0)) for k in range(3, 0, -1)][::-1][::-1]


def _poly_area_(l):
    return sum(l[i][0] * l[(i + 1) % len(l)][1] - l[(i + 1) % len(l)][0] * l[i][1] for i in range(len(l))) / 2


def cover_mass_g():
    arch = abs(_poly_area_(cov_loops())) * (2 * COV_Y)
    wall = abs(_poly_area_(cov_side_loop())) * COV_T * 2
    return round((arch + wall) * 1e6 * RHO_PETG_, 1)


def servo_zc(x):
    return max(zu(x) - 0.0030, 0.0073)


# ------------------------------------------------------------------ lane C constants (m)
PACK_L, PACK_W, PACK_H = 0.105, 0.035, 0.029                    # V RMRC Tattu 2300 4S 105 x 35 x 29 (readymaderc.com/products/details/tattu-2300-75c-4s1p-xt60, 2026-11-15; EU retailers list 105 x 33 x 28)
PACK_Z0 = 0.008
PACK_R = 3.0 * MM                           # EST pouch corner radius under the shrink (not published): measure
LEAD_D = 3.0 * MM                           # EST 14 AWG silicone insulation OD (V: Tattu page lists "14 AWG", no OD): measure
LEAD_LEN = 0.100                            # V nextfpv / gravesrc "about 100 mm" (audit; one retailer says 35/60 mm): measure on arrival
LEAD_PITCH = 7.2 * MM                       # EST XT60 pin pitch (Amass XT60: two 3.5 mm pins; not fetched): measure
XT60_W, XT60_H = 15.5 * MM, 8.1 * MM        # V Pololu 2174/2175 listing "15.5 x 8.1 x 20.5" (pololu.com/product/2174, 2026-11-15); Amass drawing not readable (components101 PDF is an image)
XT60_L = 12.0 * MM                          # EST: each half 12 mm so a mated pair is 24 mm (V Fingertech listing, robotshop.com, "mated length 24 mm"); Pololu 20.5 mm probably includes solder cups
XT60_CH = 2.0 * MM                          # EST keying chamfer on the lower corners
PACK_XL = 0.0025                            # EST: power leads leave the pack end face in its aft 10 mm (x -2.5..7.5), clear of the 25 mm strap (x -27.5..-2.5)
PACK_ZL = PACK_Z0 + PACK_H / 2              # lead exit height: mid thickness (EST)
LEAD_Y1 = 0.0635                            # EST: leads leave the end face (y +52.5 mm) 11 mm, then run aft on the skin outboard of the plate (half width 55)
_xt0 = 0.085                                # male housing starts here (EST), female to _xt0 + 2 XT60_L
XT_Z = max(zu(x) for x in (_xt0, _xt0 + 2 * XT60_L)) + XT60_H / 2 + 0.0002          # CALC: connector centre height, sits on the skin
STRAP_W, STRAP_T = 25 * MM, 1.6 * MM        # BOM W/E-PWR-01: 25 mm strap; thickness EST (hook + loop, 2 layers)
STRAP_X0 = PACK_X[0]                        # strap fore edge (nominal pack position): strap x -27.5..-2.5 (pack at trim 0)
X_GROUND = 0.3375                           # EST: pad aft face (pad 30 mm DOC)
FC_X0 = 0.045                                                          # QP-4: FC hard-mounted ON the spar centre (spar axis x 0.060 = FC centre); ESC moved aft of it
GEL = 0.0030                                                           # EST foam tape 3.0 mm (was 1.5; D-194 stock-screw stack height): FC HARD-MOUNTED (BOARD s3 D-186, s1 item 5)
T_PCB = 1.6 * MM                            # EST PCB thickness (not published): measure
FC_CX = FC_X0 + 0.015
FC_HOLES = [(FC_CX + sx * 0.010, sy * 0.010) for sx in (-1, 1) for sy in (-1, 1)]   # V Holybro 20 x 20 mm M2 pattern (phone-readable on retailer pages, 2026-11-15)
GEL_XY = FC_HOLES                           # tape pads sit under the four M2 holes (was 24 x 19 EST)
FC_TOP = ZP + GEL + 0.020                   # V Holybro stack height 20 mm (envelope kept: bottom board on the pads, top board at the top)
FC_B = ((FC_X0, -0.0125, ZP + GEL), (FC_X0 + 0.030, 0.0125, FC_TOP))   # V Holybro 30 x 25 x 20 stack (holybro.com/products/kakute-f405-wing-mini)
FC_ZB = ZP + GEL                            # bottom board underside
FC_ZB_TOP = FC_ZB + T_PCB
FC_STANDOFF = (FC_TOP - T_PCB) - FC_ZB_TOP  # CALC 16.8 mm: ASSUMES the two boards are at the bottom and top of the 20 mm stack: spacing is NOT published ("-")
# solder pad layout (EST: the Holybro pinout page gives pad names only, board images not readable): (x, y, z)
FC_PADS = {'ESC': (0.0475, 0.0, FC_ZB_TOP), 'S5': (0.0725, 0.005, FC_ZB_TOP), 'S6': (0.0725, -0.005, FC_ZB_TOP),
           'GPS': (0.0475, 0.005, FC_TOP), 'I2C': (0.0475, -0.005, FC_TOP), 'RX': (0.0725, 0.0, FC_TOP)}
RX_B = ((0.102, -0.0525), (0.124, -0.0395))  # V RadioMaster RP3 V2 22 x 13 x 4 mm (readymaderc 85670, 2026-11-15): 22 along x, 13 along y
RX_T = 4.0 * MM
GPS_B = ((0.045, 0.0275), (0.070, 0.0525))   # V TBS M10Q 25 x 25 x 7.7 mm (readymaderc 86501)
GPS_T = 7.7 * MM
AS_B = ((0.045, -0.0525), (0.060, -0.0375))  # EST RMRC MS4525 board 15 x 15 (size not published)
AS_T = 8.0 * MM                             # EST
SV_X0, SV_X1, SV_DY, SV_Z0 = 0.1270, 0.1554, 0.01335, -0.0013 - WING_DZ    # SERVO.md: EMAX ES3054HV 28.4 x 13.0 x 26.7 (servodatabase / getfpv, 2026-11-15); ears, output boss: "-" (no drawing)
SV_XS = 0.1405                              # spline axis x (kept; spline axis is vertical, arm turns in the x-y plane)
ARM_R = 12.0 * MM                           # FIXES2 s1.3: servo arm 12 mm to the pushrod hole
ARM_Z0 = SV_Z1                              # arm sits on the case top (output boss height "-": measure; a real boss lifts the arm)
ARM_T = 2.0 * MM                            # EST arm thickness
ARM_Z1 = ARM_Z0 + ARM_T
ROD_D = 1.2 * MM                            # V RMRC linkage set 1.2 mm rods
ROD_Z = ARM_Z1 + ROD_D / 2                  # rod rests on the arm top, Z-bent down through the arm hole
HORN_R = 12.9 * MM                          # FIXES2 s1.3: rod hole radius from the hinge axis
HORN_XH = XH + math.sqrt(HORN_R ** 2 - (ROD_Z - HINGE_Z) ** 2)     # CALC hole x on the 12.9 mm radius
HORN_X0, HORN_X1 = HORN_XH - 0.0015, HORN_XH + 0.0135      # EST blade 15 mm long (horn size "-": RMRC lists "20 mm horns"); D-194: blade starts 1.5 mm ahead of the hole, the clevis sleeve ends 2.0 mm ahead of it
ROD_Y = lambda sy: sy * (SERVO_Y - ARM_R)   # arm tip (neutral) and horn hole share this y: the rod runs parallel to x
HORN_TOP = ROD_Z + 0.0022                   # EST blade top 2.2 mm above the hole axis
SPLINE_TEETH = 23                           # V readymaderc 85975 "23T output gear spline" (read 2026-11-15); the old stack said 25T (ES3352 copy): RESOLVED to 23T

# hardware masses CALC (HW_DIMS M2: pan dk 3.8 k 1.6; thin nut af 4.0 m 1.2; nut ISO 4035/DIN 439 EST)
FCS_L = {}                                  # per-hole screw length, filled below
_NUT_M = 1.2 * MM


def _nut_bottom(x):
    return max(zu(x + dx) for dx in (-2.4 * MM, 0.0, 2.4 * MM)) + 0.0001


FCS_STOCK = 0.025                                              # D-194: stock M2 x 25 pan screw (stock lengths 20/22/25/30); pads 3.0 mm (generic 3 mm double-sided foam tape, EST) set the stack height
FCS_L = {h: FCS_STOCK for h in FC_HOLES}      # stock M2 x 25: tips end 0.1 mm short of to 0.6 mm past the nut bottom (the core carries 4 shop relief holes for the tips: HWC-001 is a core seat guest)
M_FC_SCREWS = round(sum(_g_screw(2.0 * MM, L, 3.8 * MM, 1.6 * MM) for L in FCS_L.values()), 2)
M_FC_NUTS = round(4 * _g_nut(4.0 * MM, _NUT_M, 2.0 * MM), 2)
M_FC_SET = round(M_FC_SCREWS + M_FC_NUTS, 2)    # HWC-001 screws + HWC-003 nuts (nuts are seated in the plate before the plate goes on the skin: separate build step)
M_ARM_SCREW = round(_g_screw(2.0 * MM, 6.0 * MM, 3.8 * MM, 1.6 * MM), 2)     # M2 x 6 pan (kept from the old stack)
M_STANDOFFS = 4 * RHO_PA66 * math.pi / 4 * (4.0 ** 2 - 2.2 ** 2) * FC_STANDOFF   # g, nylon standoffs (part of AVN-002's 17 g)
M_XT60_F = 3.0                              # EST g: XT60 female half
M_TAIL = 5.0   # EST 2 x 0.10 m of 14 AWG at 25 g/m (V: RMRC wire page lists no mass) = 5 g
M_STRAP = 3.0                               # EST g: 25 mm hook-and-loop, 0.32 m


# ------------------------------------------------------------------ parts
# power / avionics
P('PWR-001', 'Pack Tattu 2300 mAh 4S 75C', 'power', 270.0, 'LiPo', 'buy', 'source')
P('PWR-002', 'Pack strap 25 mm hook-and-loop (round pack and tray)', 'power', M_STRAP, 'hook-and-loop nylon', 'buy')
P('AVN-001', 'Avionics plate', 'avionics', 8.0, 'PETG (printed)')   # QP-4 FIXES 12 -> 8 g: 4 lightening windows (now drawn)
P('AVN-002', 'Flight controller Kakute F405 Wing Mini', 'avionics', 17.0, 'PCB', 'buy', 'bus')
P('AVN-007', 'Foam-tape pads x4 (FC hard mount, 3.0 mm)', 'avionics', 1.0, 'VHB-class foam tape', 'buy')
P('AVN-003', 'Receiver RP3 V2 ELRS', 'avionics', 4.6, 'PCB', 'buy', 'sink')       # V 4.6 g with antennas (readymaderc 85670)
P('AVN-004', 'GPS TBS M10Q + compass', 'avionics', 13.5, 'PCB', 'buy', 'sink')
P('AVN-005', 'Airspeed sensor MS4525 board', 'avionics', 3.0, 'PCB', 'buy', 'sink')
P('AVN-006', 'Pitot probe', 'avionics', 5.0, 'brass tube', 'buy')
P('AVN-008', 'Bay cover (D-198): 0.6 mm printed PETG hood over the FC stack, ESC and the phase-lead pad runs; notches for the 4 phase bundles and the battery tail', 'avionics', cover_mass_g(), 'PETG (printed)')
P('HWC-001', 'FC mounting screws: 4 x M2 x 25 pan screw (stock)', 'avionics', M_FC_SCREWS, 'A2 stainless', 'buy')
P('HWC-003', 'FC mounting nuts: 4 x M2 thin nut (DIN 439 1.2 mm) in the plate hex pockets', 'avionics', M_FC_NUTS, 'A2 stainless', 'buy')
# mechanisms (30 g with linkage)
for s in 'RL':
    P('MEC-001-' + s, 'Servo EMAX ES3054HV (%s)' % s, 'mechanisms', 20.5, 'plastic / metal gear', 'buy', 'sink')
    P('MEC-002-' + s, 'Servo arm (%s)' % s, 'mechanisms', 1.0, 'nylon', 'buy')
    P('MEC-003-' + s, 'Pushrod 1.2 mm with Z-bend and clevis (%s)' % s, 'mechanisms', 0.97, 'steel', 'buy')
    P('MEC-005-' + s, 'Clevis pin 1.0 x 4.4 mm (%s); mass CALC steel, carried inside the 1.0 g rod before D-194' % s, 'mechanisms', 0.03, 'steel', 'buy')
    P('MEC-004-' + s, 'Control horn (%s)' % s, 'mechanisms', 1.0, 'nylon', 'buy')
    P('HWC-002-' + s, 'Servo arm screw M2 x 6 pan (%s)' % s, 'mechanisms', M_ARM_SCREW, 'A2 stainless', 'buy')
# landing
for s in ST:
    P('GER-001-' + s, 'Foot shoe (%s)' % s, 'landing', 1.4, 'PETG (printed)')
    P('GER-002-' + s, 'Foot pad EVA/PE 12x15x30 (%s)' % s, 'landing', 0.7, 'EVA / PE foam')
# harness: XT60 female + tail (modelled), remaining lump
P('HRN-002', 'XT60 female + 14 AWG tail to the ESC (modelled)', 'harness', M_XT60_F + M_TAIL, 'copper / silicone / nylon', 'buy', 'bus', carried=True)
P('HRN-001', 'Harness remainder (wire, connectors, ties, tubing; MASS-GATE avionics 110 g less itemised parts) - lumped',
  'harness', None, 'copper / silicone', cg=[0.030, 0.0, 0.020], mass_proxy=True, carried=True)
HRD_BASE_G = 30.0                           # QP-4 FIXES 37 -> 30 g (before this round)
HRD_C_MODELLED_G = round(M_FC_SET + 2 * M_ARM_SCREW, 2)    # lane C hardware now drawn (lanes A and B subtract theirs)
P('HRD-001', 'Hardware: screws, nuts, epoxy fillets, paint (MASS-GATE 40 g less rib saddles) - lumped, less modelled sets', 'assembly',
  round(HRD_BASE_G - HRD_C_MODELLED_G, 2), 'steel / epoxy', cg=[0.100, 0.0, 0.0], mass_proxy=True, carried=True)
HRN_BASE_G = 106.0                          # old MASS-GATE avionics allocation (110 g less itemised parts): superseded by the bottom-up list below (D-198)
PARTS['HRN-001']['mass_g'] = 0.0            # set after phase_route() exists, see HRN_ITEMS


# ------------------------------------------------------------------ edges
# power
E(en('PWR'), 'PWR-002', 'CGE-008', 'CT-STRAP-VELCRO', 'power', 'hook-and-loop strap round pack and tray: over the pack top, outside the tray end walls, under the tray plate AND the 12 mm bridge tube CGE-004 (tangent to the plate underside, z -6..6)',
  retention=dict(item='25 mm strap', count=1, load_n=38.8), field_joint=True)
E(en('PWR'), 'PWR-001', 'CGE-008', 'CT-STRAP-VELCRO', 'power', 'pack sits on the tray floor on a hook-and-loop anti-slip pad (pad not drawn, EST), between the integral lips; strap PWR-002 holds it',
  retention=dict(item='anti-slip pad + strap', count=1), field_joint=True)
E(en('PWR'), 'PWR-002', 'PWR-001', 'CT-STRAP-VELCRO', 'power', 'strap bears on the pack top face')
# avionics
E(en('AVN'), 'AVN-001', 'WNG-001', CA, 'avionics', 'plate base follows the upper skin (same vertices as the core)')
E(en('AVN'), 'AVN-007', 'AVN-001', 'CT-GEL-PAD', 'avionics', 'four thin foam-tape pads on the plate (FC on the wing centre, not on the cage hub: SITL-FLIGHT follow-up 2; hard mount, BOARD D-186)')
E(en('AVN'), 'AVN-002', 'AVN-007', 'CT-GEL-PAD', 'avionics', 'FC on the tape pads, M2 screws (hard mount; gel only if its frequency is measured at 40-70 Hz)')
for pid in ('AVN-003', 'AVN-004', 'AVN-005'):
    E(en('AVN'), pid, 'AVN-001', TAPEF, 'avionics', 'foam tape + tie', retention=dict(item='VHB-class tape', count=1))
E(en('AVN'), 'AVN-006', 'WNG-001', EPX, 'avionics', 'pitot in a groove in the LE at y = +0.41 (outside the rotor wash, EST)')
E(en('AVN'), 'AVN-008', 'AVN-001', TAPEF, 'avionics', 'cover stands on the plate (and its front ramp on the skin ahead of the plate), foam tape + two ties; removable for FC access (D-198)', retention=dict(item='VHB-class tape + ties', count=1))
_e_fc = en('AVN')
EDGES.append(dict(id=_e_fc, part_a='HWC-001', part_b='AVN-002', via='CT-HW-SEATED', owner='avionics', hardware=True,
                  notes='four M2 screws through the stack standoffs (hardware of E-AVN-03)',
                  joint_stack=STACK('M2 x 25 pan screw (stock)', 4, 'boards 2.2 mm clearance (EST), standoffs ID 2.2', 30,
                                    eng=1.2, mineng=1.0)))
_e_fs = en('AVN')
EDGES.append(dict(id=_e_fs, part_a='HWC-001', part_b='HWC-003', via='CT-HW-SEATED', owner='avionics', hardware=True,
                  notes='screw threads into the nut (stock M2 x 25: tip 0.1 mm short of to 0.6 mm past the nut bottom)',
                  joint_stack=STACK('M2 x 25 pan screw into M2 thin nut', 4, 'nut thread', 31, eng=1.1, mineng=1.0)))
_e_fp = en('AVN')
EDGES.append(dict(id=_e_fp, part_a='HWC-003', part_b='AVN-001', via='CT-HW-SEATED', owner='avionics', hardware=True,
                  notes='four M2 thin nuts trapped in hex pockets on the plate underside (seated before the plate goes on the skin)',
                  joint_stack=STACK('M2 pan screw + M2 thin nut (DIN 439, 1.2 mm)', 4, '2.2 mm hole + hex pocket in the plate (plate 1.5-2.1 mm)', 30,
                                    eng=1.2, mineng=1.0)))
# mechanisms
for s in 'RL':
    E(en('MEC'), 'MEC-001-' + s, 'WNG-001', EPX, 'mechanisms', 'servo in its pocket')
    E(en('MEC'), 'MEC-002-' + s, 'MEC-001-' + s, 'CT-SERVO-SPLINE', 'mechanisms', 'arm on the 23T output spline (V readymaderc 85975; the old 25T was an ES3352 copy)',
      joint_stack=STACK('M2x6 retaining screw', 1, 'arm bore on the 23T spline', 20, eng=4.0, mineng=3.0))
    E(en('MEC'), 'MEC-003-' + s, 'MEC-002-' + s, 'CT-CLEVIS', 'mechanisms', 'rod Z-bend in the arm tip hole (vertical pin)',
      motion=dict(axis='Z', range_deg=[-30, 30]))
    E(en('MEC'), 'MEC-003-' + s, 'MEC-004-' + s, 'CT-CLEVIS', 'mechanisms', 'rod clevis on the horn hole (horizontal pin)',
      motion=dict(axis='Y', range_deg=[-ELEV_POSE, ELEV_POSE]))
    E(en('MEC'), 'MEC-004-' + s, 'WNG-006-' + s, EPX, 'mechanisms', 'horn bonded on the elevon upper skin')
    EDGES.append(dict(id='E-MEC-PIN-%s4' % s, part_a='MEC-005-' + s, part_b='MEC-004-' + s, via='CT-HW-SEATED', owner='mechanisms', hardware=True,
                      notes='clevis pin through the horn hole (pressed in along y after the clevis is lowered onto the blade); moves with the horn',
                      joint_stack=STACK('1.0 mm clevis pin', 1, 'horn hole 1.5 mm', 40, eng=2.0, mineng=2.0)))
    EDGES.append(dict(id='E-MEC-PIN-%s3' % s, part_a='MEC-005-' + s, part_b='MEC-003-' + s, via='CT-CLEVIS', owner='mechanisms',
                      notes='clevis pin through the cheek holes of the rod (the rod turns on it); linkage path not modelled in the poses',
                      motion=dict(axis='Y', range_deg=[-ELEV_POSE, ELEV_POSE])))
    for tgt in ('MEC-002-', 'MEC-001-'):
        EDGES.append(dict(id='E-MEC-HW-%s%s' % (s, tgt[6]), part_a='HWC-002-' + s, part_b=tgt + s, via='CT-HW-SEATED', owner='mechanisms',
                          hardware=True, notes='arm retaining screw (hardware of the spline joint)',
                          joint_stack=STACK('M2x6 pan', 1, 'arm bore / output-shaft thread', 20, eng=4.0, mineng=3.0)))
# landing
for s in ST:
    tube = 'FIN-001-' + ('R' if ST[s][0] > 0 else 'L')
    E(en('GER'), 'GER-001-' + s, tube, EPX, 'landing', 'shoe cap on the tube end')
    E(en('GER'), 'GER-002-' + s, 'GER-001-' + s, TAPEF, 'landing', 'pad PSA on the shoe plate')
# lumps (non-structural: located by ties)
E('E-HRN-21', 'HRN-002', 'WNG-001', TAPEF, 'harness', 'XT60 pair and tail taped on the skin (foam tape) and tied', retention=dict(item='VHB-class tape', count=1))
E('E-HRN-20', 'HRN-001', 'WNG-001', 'CT-TIE', 'harness', 'harness lump: ties and tape on the wing')
E('E-ASM-01', 'HRD-001', 'WNG-001', 'CT-TIE', 'assembly', 'hardware lump')
# electrical (owner harness); ELEC[eid] = wire diameter in the CAD (bundle envelope; strands carry the real diameters)
EDGES.append(dict(id='E-HRN-01', part_a='PWR-001', part_b='HRN-002', via='CT-XT60', owner='harness',
                  notes='pack lead XT60 male mated to the ESC-side XT60 female (disconnect); both lead pairs run outboard of the plate',
                  wire=WIRE(14, 'XT60', 'R-A-01', ['tape on the skin'], 6, 'heat-shrink + tie', True),
                  current_a=dict(cont=11, peak=41)))
ELEC['E-HRN-01'] = 0.003
EDGES.append(dict(id='E-HRN-12', part_a='HRN-002', part_b='PRP-003', via='CT-SOLDER-DC', owner='harness',
                  notes='14 AWG tail from the XT60 female to the ESC battery pads (flat pair, inboard over the ESC)',
                  wire=WIRE(14, 'solder + heat-shrink', 'R-A-12', ['tie at the plate edge'], 6, 'heat-shrink + tie'),
                  current_a=dict(cont=11, peak=41)))
ELEC['E-HRN-12'] = 0.0063
for i, s in enumerate(ST):
    eid = 'E-HRN-%02d' % (2 + i)
    EDGES.append(dict(id=eid, part_a='PRP-003', part_b='PRP-001-' + s, via='CT-SOLDER-PHASE', owner='harness',
                      notes='motor phase leads %s (3 x 20 AWG, OD 1.8 mm, V T-Motor / Pimoroni): out of the motor base through the cup lead hole into the cup collar, inside the arm bore to the hub end, out through the socket floor hole, then exposed over the hub and wing (D-198) to the ESC pad' % s,
                      wire=WIRE(20, 'solder + heat-shrink', 'R-A-%02d' % (2 + i),
                                ['cup collar', 'inside the arm tube', 'hub socket floor hole', 'tie at the hub aft face', 'tie at the plate edge'], 4,
                                'heat-shrink + tie at the floor hole'),
                      current_a=dict(cont=10.9, peak=12.1)))
    ELEC[eid] = 0.0039
EDGES.append(dict(id='E-HRN-06', part_a='PRP-003', part_b='AVN-002', via='CT-JST-GH-6', owner='harness',
                  notes='ESC lead to the FC (VBAT, signals, telemetry): 6 conductors, soldered to the FC pads (the Kakute has pads, not sockets: docs.holybro.com pinout 2026-11-15)',
                  wire=WIRE(26, 'JST-GH 6-pin', 'R-A-06', ['tie on the plate'], 3, 'strain loop')))
ELEC['E-HRN-06'] = 0.0078
for i, s in enumerate('RL'):
    eid = 'E-HRN-%02d' % (7 + i)
    EDGES.append(dict(id=eid, part_a='AVN-002', part_b='MEC-001-' + s, via='CT-SERVO-JR', owner='harness',
                      notes='servo lead %s: 3-conductor ribbon, soldered to the FC pad M5/M6 (JR plug cut off; the FC has pads only), laid on the skin to the servo' % s,
                      wire=WIRE(26, 'JR 3-pin', 'R-A-%02d' % (7 + i), ['tie at the plate edge', 'tape on the skin'], 3,
                                'strain loop')))
    ELEC[eid] = 0.0036
for eid, a, b, ct, nm, nc in (('E-HRN-09', 'AVN-002', 'AVN-003', 'CT-JST-GH-4', 'RX UART (CRSF wire soldered at the RX pads)', 4),
                              ('E-HRN-10', 'AVN-002', 'AVN-004', 'CT-JST-GH-6', 'GPS (plug on the GPS board, other end soldered to the FC)', 6),
                              ('E-HRN-11', 'AVN-002', 'AVN-005', 'CT-JST-GH-4', 'airspeed I2C (plug on the MS4525 board, other end soldered to the FC)', 4)):
    EDGES.append(dict(id=eid, part_a=a, part_b=b, via=ct, owner='harness', notes=nm + ' lead',
                      wire=WIRE(28, ct, 'R-' + eid[2:], ['tie on the plate'], 3, 'strain loop')))
    ELEC[eid] = 1.0 * MM * nc               # ribbon width (flat ribbon of nc x 1.0 mm)


# ------------------------------------------------------------------ geometry builders
def _xt60_loop(cx, cz, w=XT60_W, h=XT60_H, ch=XT60_CH):
    """XT60 housing outline in the (y, z) plane (EST keying: the two lower corners chamfered)."""
    return [(cx - w / 2 + ch, cz - h / 2), (cx + w / 2 - ch, cz - h / 2), (cx + w / 2, cz - h / 2 + ch), (cx + w / 2, cz + h / 2),
            (cx - w / 2, cz + h / 2), (cx - w / 2, cz - h / 2 + ch)]


def _lead_path(k):
    """Centre line of pack lead k (+-1: outer / inner) from the end face to the male housing back (axis-aligned legs)."""
    dx = k * LEAD_D * 0.53
    y1 = LEAD_Y1 + k * LEAD_PITCH / 2
    return [(PACK_XL + dx, PACK_L / 2, PACK_ZL), (PACK_XL + dx, y1, PACK_ZL), (PACK_XL + dx, y1, XT_Z), (_xt0, y1, XT_Z)]


def build_power(ctx):
    pk = ctx.part('PWR-001', rgb=(0.15, 0.15, 0.6))
    pk.prism('Y', -PACK_L / 2, [_rrect(PACK_X[0], PACK_Z0, PACK_X[1], PACK_Z0 + PACK_H, PACK_R, 4)], PACK_L, name='pack cells (shrink-wrapped pouch)')
    for k, nm in ((-1, 'lead (black)'), (1, 'lead (red)')):
        _legs(pk, _lead_path(k), LEAD_D, 'pack ' + nm)
    yc = LEAD_Y1
    pk.prism('X', _xt0, [_xt60_loop(yc, XT_Z)], XT60_L, name='XT60 male housing')
    # balance lead: 5 x 26 AWG-class (EST 1.2 mm OD), leaves the end face aft of the strap, up over the top edge and inboard along the pack top, JST-XH 5-pin plug
    bx = PACK_X[1] - 0.0065
    zt = PACK_Z0 + PACK_H
    pts = [(bx, PACK_L / 2, PACK_ZL), (bx, PACK_L / 2 + 0.0015, PACK_ZL), (bx, PACK_L / 2 + 0.0015, zt + 0.0006), (bx, 0.017, zt + 0.0006)]
    _legs(pk, pts, 1.2 * MM, 'balance lead (5 wires bundled)')
    pk.box((bx - 2.9 * MM, 0.017 - 14.8 * MM, zt), (bx + 2.9 * MM, 0.017, zt + 9.8 * MM - 2.6 * MM), name='JST-XH 5-pin plug (EST height; V octopart 14.8 x 5.7 mm)')   # housing 14.8 x 5.7 V (octopart/JST XHP-5 listing 2026-11-15); height listing 9.8 mm is the mounted height: 7.2 EST drawn
    # strap loop: axis x, ring around tray + pack
    ctx_strap = ctx.part('PWR-002', rgb=(0.1, 0.1, 0.1))
    yi = 0.0545
    ctx_strap.prism('X', STRAP_X0, [_rrect(-yi - STRAP_T, -0.006 - STRAP_T, yi + STRAP_T, PACK_Z0 + PACK_H + STRAP_T, 0.0012, 3),
                                    [(-yi, -0.006), (yi, -0.006), (yi, PACK_Z0 + PACK_H), (-yi, PACK_Z0 + PACK_H)]], STRAP_W, name='strap loop')


def build_avionics(ctx):
    # ---- plate with the four lightening windows (QP-4 FIXES: the 8 g assumes them)
    pl = ctx.part('AVN-001', rgb=(0.9, 0.9, 0.9))
    loop = [(XS[i], zu(XS[i])) for i in range(PLATE_I0, PLATE_I1 + 1)] + [(PLATE_X1, ZP), (PLATE_X0, ZP)]
    pl.prism('Y', -PLATE_Y, [loop], 2 * PLATE_Y, name='plate')
    for (wx0, wx1, wy0, wy1) in ((0.080, 0.122, 0.021, 0.040), (0.080, 0.122, -0.040, -0.021),
                                 (0.049, 0.072, 0.0155, 0.026), (0.049, 0.072, -0.026, -0.0155)):
        pl.cut_box((wx0, wy0, -0.05), (wx1, wy1, ZP + 0.01), name='lightening window')       # EST layout, clear of the boards
    for hx, hy in FC_HOLES:
        pl.cut_cylinder('Z', (hx, hy, -0.05), ZP + 0.05, 1.1 * MM, name='M2 clearance hole')
        nb = _nut_bottom(hx)
        pl.cut_prism('Z', nb - 0.0001, [_hex(hx, hy, 4.2 * MM)], _NUT_M + 0.0003, name='M2 nut pocket')
    # ---- foam-tape pads (one per M2 hole)
    gl = ctx.part('AVN-007', rgb=(0.6, 0.8, 0.9))
    for gx, gy in GEL_XY:
        gl.prism('Z', ZP, [[(gx - 3 * MM, gy - 3 * MM), (gx + 3 * MM, gy - 3 * MM), (gx + 3 * MM, gy + 3 * MM), (gx - 3 * MM, gy + 3 * MM)],
                           _ring(gx, gy, 1.1 * MM, 12)], GEL, name='foam tape pad')
    # ---- FC stack: bottom (power) board, 4 nylon standoffs, top (FC) board, solder pads
    fc = ctx.part('AVN-002', rgb=(0.1, 0.1, 0.5))
    _pcb(fc, FC_X0, -0.0125, FC_X0 + 0.030, 0.0125, FC_ZB, T_PCB, FC_HOLES, r=1.5 * MM, name='Kakute power board (EST 1.6 mm)')
    _pcb(fc, FC_X0, -0.0125, FC_X0 + 0.030, 0.0125, FC_TOP - T_PCB, T_PCB, FC_HOLES, r=1.5 * MM, name='Kakute FC board (EST 1.6 mm)')
    for hx, hy in FC_HOLES:
        k9.hw_washer(fc, 'Z', (hx, hy, FC_ZB_TOP), 1, 'M2', od=4.0 * MM, t=FC_STANDOFF, idia=2.2 * MM, name='nylon standoff (EST 4 mm OD)')
    for k, (x, y, z) in FC_PADS.items():
        _pad(fc, x, y, z, {'S5': 'servo pad S5', 'S6': 'servo pad S6', 'ESC': 'ESC signal pad', 'GPS': 'GPS pad', 'I2C': 'I2C pad', 'RX': 'RX pad'}[k])
    # ---- FC mounting hardware set (screws from the top board down to a thin nut under the plate)
    hw = ctx.part('HWC-001', rgb=(0.7, 0.7, 0.75))
    for hx, hy in FC_HOLES:
        L = FCS_L[(hx, hy)]
        k9.hw_screw(hw, 'Z', (hx, hy, FC_TOP), -1, 'M2', L, 'pan', name='M2 pan screw')
    hn = ctx.part('HWC-003', rgb=(0.7, 0.7, 0.75))
    for hx, hy in FC_HOLES:
        nb = _nut_bottom(hx)
        hex_ = _hex(hx, hy, 4.0 * MM)
        hn.prism('Z', nb, [hex_, _ring(hx, hy, 1.0 * MM, 12)], _NUT_M, name='M2 thin nut')
    # ---- receiver RP3 V2: PCB, RF shield, solder pads, 2 antennas (65 mm class, drawn 50 mm: hinge at x 183.75)
    rx = ctx.part('AVN-003', rgb=(0.2, 0.2, 0.2))
    (rx0, ry0), (rx1, ry1) = RX_B
    _pcb(rx, rx0, ry0, rx1, ry1, ZP, 1.2 * MM, r=1.0 * MM, name='RP3 V2 PCB (EST 1.2 mm)')
    rx.box((rx0 + 6 * MM, ry0 + 2.5 * MM, ZP + 1.2 * MM), (rx0 + 16 * MM, ry1 - 2.5 * MM, ZP + RX_T), name='RF shield / SoC (EST: total height 4 mm V)')
    for j in range(4):
        _pad(rx, rx0 + 1.2 * MM, ry0 + 2.2 * MM + j * 2.8 * MM, ZP + 1.2 * MM, 'CRSF pad %d' % j)
    for j, ya in enumerate((ry0 + 2.5 * MM, ry1 - 2.5 * MM)):
        ant = [(rx1, ya, ZP + 0.6 * MM), (rx1 + 0.050, ya, ZP + 0.6 * MM)]
        _legs(rx, ant, 1.1 * MM, 'antenna %d (EST OD 1.1 mm, 65 mm V, drawn 50 mm)' % (j + 1))
    # ---- GPS TBS M10Q: PCB, patch, JST-SH plug, cable stub
    gp = ctx.part('AVN-004', rgb=(0.3, 0.3, 0.3))
    (gx0, gy0), (gx1, gy1) = GPS_B
    _pcb(gp, gx0, gy0, gx1, gy1, ZP, T_PCB, r=1.0 * MM, name='M10Q PCB (EST 1.6 mm)')
    gcx, gcy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
    gp.box((gcx - 9 * MM, gcy - 9 * MM, ZP + T_PCB), (gcx + 9 * MM, gcy + 9 * MM, ZP + GPS_T), name='GNSS patch (EST 18 x 18; total height 7.7 V)')
    gp.box((gcx - 3.9 * MM, gy0, ZP + T_PCB), (gcx + 3.9 * MM, gy0 + 4.2 * MM, ZP + T_PCB + 3.5 * MM), name='JST-SH 6-pin plug (ASSUMED connector, EST size)')
    # ---- airspeed board MS4525 (EST 15 x 15): PCB, sensor, 2 barbed ports, JST-GH plug
    asd = ctx.part('AVN-005', rgb=(0.3, 0.3, 0.3))
    (ax0, ay0), (ax1, ay1) = AS_B
    _pcb(asd, ax0, ay0, ax1, ay1, ZP, T_PCB, r=1.0 * MM, name='MS4525 board (EST 15 x 15 x 1.6)')
    acx, acy = (ax0 + ax1) / 2, (ay0 + ay1) / 2
    asd.box((acx - 3 * MM, acy - 4.5 * MM, ZP + T_PCB), (acx + 3 * MM, acy + 0.5 * MM, ZP + AS_T), name='MS4525DO sensor body (EST)')
    for j, ya in enumerate((acy - 3.0 * MM, acy - 0.5 * MM)):
        asd.cylinder('X', (acx + 3 * MM, ya, ZP + 5.5 * MM), 5 * MM, 1.1 * MM, name='barbed port %d (EST OD 2.2)' % (j + 1))
    asd.box((acx - 3.2 * MM, ay1 - 4.0 * MM, ZP + T_PCB), (acx + 3.2 * MM, ay1, ZP + T_PCB + 4.2 * MM), name='JST-GH 4-pin plug (EST size)')
    # ---- D-198 bay cover: roof band with the ramp / step profile, two 0.6 mm end walls, notches for the bundles that leave at |y| 26.5 mm
    cv = ctx.part('AVN-008', rgb=(0.85, 0.9, 0.95))
    cv.prism('Y', -COV_Y, [cov_loops()], 2 * COV_Y, name='cover roof band (0.6 mm)')
    for sy in (1, -1):
        y0 = COV_Y if sy > 0 else -COV_Y - COV_T
        cv.prism('Y', y0, [cov_side_loop()], COV_T, name='cover end wall (0.6 mm)')
    for sy in (1, -1):
        ya, yb = sorted((sy * (COV_Y - 0.001), sy * (COV_Y + COV_T + 0.001)))
        for xc, zc_ in ((0.085, 0.029), (0.097, 0.0275)):
            cv.cut_box((xc - 0.0026, ya, zc_ - 0.0026), (xc + 0.0026, yb, 0.050), name='phase bundle notch, open to the roof so the cover goes on after the leads are soldered (D-198)')
        zf_ = 0.044 - WING_DZ + 0.0015           # = _ZF, height of the FC-top sensor leads
        for xn, wn, sgn in ((0.0545, 0.0048, 1), (0.0725, 0.0040, -1), (0.0512, 0.0043, -1)):
            if sgn == sy:
                cv.cut_box((xn - wn, ya, zf_ - 0.0028), (xn + wn, yb, 0.050), name='sensor lead notch (GPS / RX / airspeed), open to the roof (D-198)')
        if sy > 0:
            cv.cut_box((0.122 - 0.0035, ya, XT_Z - 0.0030), (0.122 + 0.0035, yb, 0.050), name='battery tail notch, open to the roof (D-198)')
    # ---- pitot: brass probe + silicone tube stub on its rear
    pt = ctx.part('AVN-006', rgb=(0.8, 0.7, 0.2))
    pt.tube('X', (-0.130, YFIN + 0.030, 0.0), 0.175, 0.0015, 0.0010, name='pitot tube (EST 175 x 3 mm; RMRC gives no size)')
    # silicone tubing 2/4 mm (V RMRC): rear connection and run to the sensor NOT designed (rib saddle FIN-005 and spar are at x >= 0.0485): not drawn


def _arm_loop(cx, cy, ux, uy):
    """Tapered servo arm outline (hub r 4, tip r 2, EST) from the hub centre towards unit (ux, uy), tip at ARM_R."""
    ph = math.atan2(uy, ux)
    pts = [(cx + 4.0 * MM * math.cos(ph + math.radians(90 + 180 * i / 8)), cy + 4.0 * MM * math.sin(ph + math.radians(90 + 180 * i / 8)))
           for i in range(9)]
    tx, ty = cx + ux * ARM_R, cy + uy * ARM_R
    pts += [(tx + 2.0 * MM * math.cos(ph + math.radians(-90 + 180 * i / 8)), ty + 2.0 * MM * math.sin(ph + math.radians(-90 + 180 * i / 8)))
            for i in range(9)]
    return pts


def build_mechanisms(ctx):
    for s, sy in (('R', 1), ('L', -1)):
        yc = sy * SERVO_Y
        sv = ctx.part('MEC-001-' + s, rgb=(0.2, 0.2, 0.2))
        sv.box((SV_X0, yc - SV_DY, SV_Z0), (SV_X1, yc + SV_DY, SV_Z1), name='servo case (overall 28.4 x 26.7 x 13.0; ears and output boss "-")')
        sv.cylinder('Z', (0.1305, yc, SV_Z1), 0.003, 0.0020, name='servo lead strain-relief boot (EST)')
        # arm: neutral tip points inboard, perpendicular to the rod (rod parallel to x)
        ux, uy = 0.0, -sy
        ar = ctx.part('MEC-002-' + s, rgb=(0.9, 0.9, 0.9))
        loops = [_arm_loop(SV_XS, yc, ux, uy), _ring(SV_XS, yc, 1.1 * MM, 12), _ring(SV_XS, yc + uy * ARM_R, 0.75 * MM, 12)]
        ar.prism('Z', ARM_Z0, loops, ARM_T, name='servo arm (hub bore for the 23T spline; hole row beyond the used hole "-")')
        # screw
        hw = ctx.part('HWC-002-' + s, rgb=(0.7, 0.7, 0.75))
        k9.hw_screw(hw, 'Z', (SV_XS, yc, ARM_Z1), -1, 'M2', 0.006, 'pan', name='M2x6 pan screw')
        ctx.seat('MEC-001-' + s, 'HWC-002-' + s, 'output-shaft thread for the arm screw', bodies=('shank',))
        # horn: base plate + blade with the rod hole
        zb = max(zu(HORN_X0 - 0.002), zu(HORN_X0), zu(HORN_X1))      # D-194: base plate flat on the highest skin point it covers (epoxy fills the rest)
        hy = ROD_Y(sy)
        hn = ctx.part('MEC-004-' + s, rgb=(0.9, 0.9, 0.9))
        hn.box((HORN_X0 - 0.002, hy - 4 * MM, zb), (HORN_X1, hy + 4 * MM, zb + 1.0 * MM), name='horn base plate (EST 20 x 8 x 1.0)')
        blade = _rrect(HORN_X0, zb + 1.0 * MM, HORN_X1, HORN_TOP, 1.5 * MM, 3)
        hn.prism('Y', hy - 1.0 * MM, [blade, _ring(HORN_XH, ROD_Z, 0.75 * MM, 12)], 2.0 * MM, name='horn blade 2 mm (hole at R 12.9 from the hinge)')
        # pushrod: Z-bend pin in the arm hole, rod to the horn, clevis straddling the blade
        tipx, tipy = SV_XS, yc + uy * ARM_R
        rd = ctx.part('MEC-003-' + s, rgb=(0.6, 0.6, 0.6))
        rd.cylinder('Z', (tipx, tipy, ARM_Z0 + 0.0001), ROD_Z - ARM_Z0 - 0.0001, ROD_D / 2, name='rod Z-bend pin (flush with the arm underside)')
        xe = HORN_XH - 0.0040                                   # clevis body starts here (4 mm before the hole)
        rd.cylinder('X', (tipx, tipy, ROD_Z), xe - tipx, ROD_D / 2, name='pushrod')
        rd.tube('X', (xe, tipy, ROD_Z), 0.0020, 1.5 * MM, ROD_D / 2, name='clevis sleeve (EST OD 3.0, 2 mm; fork cheeks follow)')
        for sg in (-1, 1):
            yb = tipy + sg * 1.5 * MM
            rd.box((xe + 0.0020, yb - 0.4 * MM, ROD_Z - 1.6 * MM), (HORN_XH + 1.5 * MM, yb + 0.4 * MM, ROD_Z + 1.6 * MM), name='clevis cheek (EST 0.8 x 3.2)')
        pn = ctx.part('MEC-005-' + s, rgb=(0.8, 0.8, 0.85))
        pn.cylinder('Y', (HORN_XH, tipy - 2.2 * MM, ROD_Z), 4.4 * MM, 0.5 * MM, name='clevis pin 1.0 mm (EST)')
        ctx.seat('MEC-003-' + s, 'MEC-005-' + s, 'pin holes in the clevis cheeks')


def build_landing(ctx):
    sh = ctx.part('GER-001-UR', rgb=(0.9, 0.9, 0.9))
    sh.tube('Z', (XFIN_T, YFIN, FIN_H - 0.012), 0.012, 0.0105, FIN_OD / 2, name='shoe ring')
    sh.cylinder('Z', (XFIN_T, YFIN, FIN_H), 0.003, 0.0105, name='shoe cap')
    sh.box((XFIN_T + 0.0080, YFIN - 0.0105, FIN_H - 0.012), (XFIN_T + 0.0135, YFIN + 0.0105, FIN_H + 0.003), name='shoe plate')
    pd = ctx.part('GER-002-UR', rgb=(0.1, 0.1, 0.1))
    pd.box((XFIN_T + 0.0135, YFIN - 0.0075, FIN_H - 0.009), (X_GROUND, YFIN + 0.0075, FIN_H + 0.003), name='foot pad')
    for pre in ('GER-001-', 'GER-002-'):
        ctx.mirror(pre + 'UR', pre + 'UL', plane='XZ')
        ctx.mirror(pre + 'UR', pre + 'LR', plane='XY')
        ctx.mirror(pre + 'UL', pre + 'LL', plane='XY')
    for st in ST:
        ctx.seat('GER-001-' + st, 'FIN-001-' + ('R' if ST[st][0] > 0 else 'L'), 'shoe bore on the tube end')
    ctx.keepout_halfspace('KO-GROUND', 'X', X_GROUND, 1, tuple('GER-002-' + s for s in ST))


def _arm_line(st):
    """Wire points along the arm (aft side), then through the cup hole to the motor lead exit."""
    ys = (R_M - 0.085)
    a0 = mworld(st, (0.020, -ys, 0.0135))
    h1 = mworld(st, (0.020, 0.0, 0.0135))
    h2 = mworld(st, (-0.0145, 0.0, 0.0135))
    return a0, h1, h2


# D-194: the harness routes were tuned at absolute heights for the old datum; they follow the skin (-WING_DZ) and the FC stack (+1.5 mm pads)
_DZ = -WING_DZ
_ZF = 0.044 - WING_DZ + 0.0015


def phase_route(st, px, py, z_pad):
    """D-198 phase-lead bundle (tri of 1.8 mm strands), motor to ESC pad. Cup frame: motor base (inside the ring) -> +x through the cup lead hole
    (y 5.5 mm) -> 4 mm bend in the cup collar -> -y inside the arm bore to y -0.150 -> down the bore (shifting to the up side, offset PH_DT) ->
    out of the arm end through the hub socket floor hole -> bend aft at r 23.7 (ENCLOSED to here) -> EXPOSED: aft behind the hub, out to y 62 / 88 mm
    clear of the pack and tray (the pack is 105 mm wide), over the wing at z 35 / 27.5 mm, to the ESC pad. The upper pair passes at x -58.5, the
    lower pair climbs at x -52.5 (6 mm apart); the lower arm bundles climb at y 24.6 mm, outboard of the hub strut boss (clear by 3 mm)."""
    sy, sz = ST[st]
    xa, za = ph_arm_xz(st, R_IN)
    pts = [mworld(st, (-0.0135, PH_Y, 0.0)), mworld(st, (PH_XC, PH_Y, 0.0)), mworld(st, (PH_XC, -0.150, 0.0)),
           a2w(st, (xa, R_IN + 0.020, za)), a2w(st, (xa, R_IN - 0.0035, za)), a2w(st, (xa, R_IN - 0.0075, za))]
    g = pts[-1]
    zl_, yl = (0.029, 0.062) if sz > 0 else (0.0325 + _DZ, 0.088)       # D-198: upper bundles at z 29 (under the cover roof, was 35)
    yl *= sy
    if sz > 0:
        xh = -0.0585
        pts += [(xh, g[1], g[2]), (xh, yl, zl_)]
    else:
        xh = -0.0525
        pts += [(xh, g[1], g[2]), (xh, sy * 0.0246, 0.0176), (xh, yl, zl_)]
    pts += [(px, yl, zl_), (px, py, zl_), (px, py, z_pad)]
    return pts


# D-198 bottom-up mass of the lumped harness remainder HRN-001 (replaces the 50.9 g "110 g allocation less itemised parts"). The 400 mm stock leads of the
# motors are inside the 65 g motor mass (T-Motor page: 55 g without cables, 65 g with), so only the length beyond 0.40 m (+ 30 mm splice overlap) is added.
WIRE_G_PER_M = {20: 7.1, 26: 2.0, 28: 1.2}   # V 20 AWG: Pimoroni dual silicone 14.2 g per metre for 2 conductors (shop.pimoroni.com/en-us/products/dual-silicone-wire-per-metre, 2026-11-15); 26 / 28 AWG: EST (copper 1.15 / 0.72 g/m + insulation)


def _plen(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def hrn_items():
    ext = 0.0
    for st in ST:
        px, py = ESC_PADS[st]
        ext += 3 * max(0.0, _plen(phase_route(st, px, py, ESC_TOP + 0.002)) - 0.40 + 0.030)
    return [('phase-lead extensions: 12 strands of 20 AWG, CAD route beyond the 0.40 m stock lead + 30 mm splice (%.2f m)' % ext, round(ext * WIRE_G_PER_M[20], 1)),
            ('12 splices: solder + 15 mm heat-shrink, 0.15 g each (EST)', 1.8),
            ('ESC signal ribbon 6 x 26 AWG x 73 mm (CAD) at 2.0 g/m (EST)', round(6 * 0.073 * WIRE_G_PER_M[26], 1)),
            ('RX / GPS / airspeed leads: 14 conductors of 28 AWG x about 70 mm at 1.2 g/m (EST) + 3 JST plugs 0.5 g each (EST)', round(14 * 0.070 * WIRE_G_PER_M[28] + 1.5, 1)),
            ('servo leads: the 3-wire leads are in the 20.5 g servo mass (EST: stock length reaches the FC pads), plus 2 groove fish-wire ties', 0.2),
            ('heat-shrink sleeves at the cup collar / floor hole, ties, foam tape, solder (EST)', 5.0)]


HRN_ITEMS = hrn_items()
PARTS['HRN-001']['mass_g'] = round(sum(g for _n, g in HRN_ITEMS), 1)
PARTS['HRN-001']['name'] = 'Harness remainder, bottom-up (D-198): phase-lead extensions, splices, ESC ribbon, sensor leads, servo ties, sleeves / ties / tape / solder - lumped'


def build_harness(ctx):
    h = ctx.part('HRN-001', proxy=True)
    h.cylinder('X', (0.030, 0.0, 0.005), 0.002, 0.001, name='harness lump')
    z_pad = ESC_TOP + 0.002
    bx, by = ESC_PADS['BAT']
    # XT60 female half (mated to the male on the pack lead), tail to the ESC battery pads
    hf = ctx.part('HRN-002', rgb=(0.15, 0.15, 0.15))
    hf.prism('X', _xt0 + XT60_L, [_xt60_loop(LEAD_Y1, XT_Z)], XT60_L, name='XT60 female housing')
    xe = _xt0 + 2 * XT60_L
    m = 0.5 * MM
    ctx.wire('E-HRN-01', [(_xt0 + XT60_L - m, LEAD_Y1, XT_Z), (_xt0 + XT60_L + m, LEAD_Y1, XT_Z)], dia=0.003)
    z_hi = ESC_TOP + 0.008
    # D-194: BAT pad moved to the aft-right corner of the ESC (pad layout is EST). Tail: out of the female back, outboard of the ESC (x 122, past its
    # aft edge 117) inboard along y over the plate at connector height, up and forward above the ESC, down onto the pad. Strands +-1.6 mm.
    tx = 0.122
    tail = [(xe - 0.001, LEAD_Y1, XT_Z), (tx, LEAD_Y1, XT_Z), (tx, by, XT_Z), (tx, by, z_hi), (bx, by, z_hi), (bx, by, z_pad)]
    off = [(LEAD_D * 0.53, 0.0), (-LEAD_D * 0.53, 0.0)]
    ctx.wire('E-HRN-12', tail, dia=ELEC['E-HRN-12'], strands=_strands(tail, LEAD_D, off))
    _terms(ctx, 'E-HRN-12')
    for i, st in enumerate(ST):
        px, py = ESC_PADS[st]
        sy, sz = ST[st]
        eid = 'E-HRN-%02d' % (2 + i)
        pts = phase_route(st, px, py, z_pad)
        ctx.wire(eid, pts, dia=ELEC[eid], strands=_strands(pts, PH_D, _tri(PH_D)))
        _terms(ctx, eid)
    sx, sy_ = ESC_PADS['SIG']
    fx, fy, fz = FC_PADS['ESC']
    # D-194: ESC signal ribbon straight inboard along y = 0 over the ESC at 24 mm, down at x 78 (4 mm ahead of the ESC), into the FC stack between the
    # boards at 19.1 mm to the ESC pad on the bottom board. 6 x 26 AWG as a 3 x 2 bundle (not a flat ribbon: no in-plane inner strand shortening).
    _zr = ESC_TOP + 0.0046
    pts = [(sx, sy_, z_pad), (sx, sy_, _zr), (0.078, sy_, _zr), (0.078, sy_, fz + 0.0016), (fx, fy, fz + 0.0016)]
    wd = 1.3 * MM                                              # EST 26 AWG silicone OD
    rib = [((j % 3 - 1) * wd, (j // 3 - 0.5) * wd) for j in range(6)]
    ctx.wire('E-HRN-06', pts, dia=ELEC['E-HRN-06'], strands=_strands(pts, wd, rib))
    _terms(ctx, 'E-HRN-06')
    core = ctx.components['WNG-001']
    for i, (key, sg) in enumerate((('S5', 1), ('S6', -1))):
        x, y, z = FC_PADS[key]
        yc = sg * SERVO_Y
        z0 = z + 0.0006
        # D-198: out of the FC aft between the boards, over the plate to the window at |y| 24 mm, down through the plate window and a slit in the skin into a
        # groove in the foam core 3 mm under the upper skin (ribbon 3 x 1.2 mm), outboard along y at x 83 mm, then aft along the skin to the servo pocket wall.
        # Only the last 6 mm (pocket wall to the lead boot) is exposed.
        zg1 = servo_zc(SRV_XD)
        xs_ = [0.083, 0.097, 0.110, 0.1215]
        pts = [(x, y, z0), (0.0775, y, z0), (SRV_XD, sg * SRV_YD, z0), (SRV_XD, sg * SRV_YD, zg1), (SRV_XD, sg * SRV_YG, zg1)]
        pts += [(xx, sg * SRV_YG, servo_zc(xx)) for xx in xs_[1:]]
        pts += [(0.1265, sg * SRV_YG, 0.0083), (0.1305, yc, SV_Z1 + 0.003)]
        ctx.wire('E-HRN-%02d' % (7 + i), pts, dia=ELEC['E-HRN-%02d' % (7 + i)], strands=_strands(pts, 1.2 * MM, [(-1.2 * MM, 0.0), (0.0, 0.0), (1.2 * MM, 0.0)]))
        _terms(ctx, 'E-HRN-%02d' % (7 + i))
        # grooves in the core (routed, shop cuts): drop slot, y run, x run following the skin
        ya, yb = sorted((sg * (SRV_YD - 0.0045), sg * (SRV_YD + 0.0045)))
        core.cut_box((SRV_XD - 0.0035, ya, zg1 - 0.0020), (SRV_XD + 0.0035, yb, 0.0150), name='servo lead drop slot through the skin (D-198)')
        ya, yb = sorted((sg * (SRV_YD - 0.0045), sg * (SRV_YG + 0.0030)))
        core.cut_box((SRV_XD - 0.0030, ya, zg1 - 0.0016), (SRV_XD + 0.0030, yb, zg1 + 0.0016), name='servo lead groove along y, 3 mm under the skin (D-198)')
        loop = [(xx, servo_zc(xx) - 0.0016) for xx in [0.0800, 0.083, 0.097, 0.110, 0.1215, 0.1250]] + [(xx, servo_zc(xx) + 0.0016) for xx in [0.1250, 0.1215, 0.110, 0.097, 0.083, 0.0800]]
        ya, yb = sorted((sg * (SRV_YG - 0.0030), sg * (SRV_YG + 0.0030)))
        core.cut_prism('Y', ya, [loop], yb - ya, name='servo lead groove along x, following the skin (D-198)')
    # RX CRSF wire: FC top board RX pad -> RX pads
    x, y, z = FC_PADS['RX']
    (rx0, ry0), _ = RX_B
    rpx, rpy = rx0 + 1.2 * MM, ry0 + 2.2 * MM + 1.5 * 2.8 * MM
    pts = [(x, y, z + 0.0006), (x, y, _ZF), (x, rpy, _ZF), (rpx, rpy, _ZF), (rpx, rpy, ZP + 1.2 * MM + 0.0006)]
    wd = 1.0 * MM
    ctx.wire('E-HRN-09', pts, dia=ELEC['E-HRN-09'], strands=_strands(pts, wd, [((j - 1.5) * wd, 0.0) for j in range(4)]))
    _terms(ctx, 'E-HRN-09')
    # GPS cable: GPS plug (inner edge) -> FC GPS pad
    x, y, z = FC_PADS['GPS']
    (gx0, gy0), (gx1, gy1) = GPS_B
    gcx = (gx0 + gx1) / 2
    pts = [(gcx, gy0 + 4.2 * MM, ZP + T_PCB + 1.8 * MM), (gcx, gy0 + 8.0 * MM, ZP + T_PCB + 1.8 * MM), (gcx, gy0 + 8.0 * MM, _ZF), (x, y, _ZF),
           (x, y, z + 0.0006)]
    ctx.wire('E-HRN-10', pts, dia=ELEC['E-HRN-10'], strands=_strands(pts, wd, [((j - 2.5) * wd, 0.0) for j in range(6)]))
    _terms(ctx, 'E-HRN-10')
    # airspeed cable: JST-GH plug -> FC I2C pad
    x, y, z = FC_PADS['I2C']
    (ax0, ay0), (ax1, ay1) = AS_B
    acx = (ax0 + ax1) / 2
    pts = [(acx, ay1, ZP + T_PCB + 2.1 * MM), (acx, ay1 + 4.0 * MM, ZP + T_PCB + 2.1 * MM), (acx, ay1 + 4.0 * MM, _ZF), (x, y, _ZF), (x, y, z + 0.0006)]
    ctx.wire('E-HRN-11', pts, dia=ELEC['E-HRN-11'], strands=_strands(pts, wd, [((j - 1.5) * wd, 0.0) for j in range(4)]))
    _terms(ctx, 'E-HRN-11')


def build_assembly(ctx):
    """Joints and contacts for every mechanical edge, after all parts exist (wires are registered by the harness)."""
    hw = ctx.part('HRD-001', proxy=True)
    hw.cylinder('X', (0.100, 0.0, 0.0), 0.002, 0.001, name='hardware lump')
    comps = ctx.components
    for e in EDGES:
        via = e['via']
        if e['owner'] == 'harness' and e['id'] in ELEC:
            continue
        a, b = comps.get(e['part_a']), comps.get(e['part_b'])
        if a is None or b is None:
            continue
        ba, bb = a.bbox(), b.bbox()
        lo = [max(ba[0][i], bb[0][i]) for i in range(3)]
        hi = [min(ba[1][i], bb[1][i]) for i in range(3)]
        at = tuple((lo[i] + hi[i]) / 2 if lo[i] <= hi[i] else (min(ba[1][i], bb[1][i]) + max(ba[0][i], bb[0][i])) / 2
                   for i in range(3))
        if via == 'CT-TAPE-HINGE':
            sgn = 1 if e['part_a'].endswith('R') else -1
            ctx.revolute(e['id'], e['part_a'], e['part_b'], (XH, sgn * (ELEV_Y0 + ELEV_Y1) / 2, zu(XH)), 'Y',
                         limits=(-ELEV_POSE, ELEV_POSE))
        elif via == 'CT-CLEVIS':
            ctx.revolute(e['id'], e['part_a'], e['part_b'], at, e['motion']['axis'])
        elif via in ('CT-A-M25-SHCS-MOTOR', 'CT-A-PROP-NUT', 'CT-A-PROP-ADAPTER', 'CT-SERVO-SPLINE') or e.get('hardware'):
            ctx.rigid(e['id'], e['part_a'], e['part_b'], at)
        else:
            ctx.contact(e['id'], via)
