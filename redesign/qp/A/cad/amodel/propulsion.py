"""amodel/propulsion.py - LANE B (propulsion): motors (PRP-001), props (PRP-002: real APC 9x4.5MR/MRP blades from the PE0 file),
SunnySky prop adapter + washer (PRP-004), M5 nyloc (PRP-005), SunnySky X-mount (PRP-006), ESC (PRP-003) and its pad layout, joint stacks, edges and the builder
build_propulsion. Prop swept disc stays as a KEEP-OUT only (KO-PROP-*); the visible prop is the blades.

Lane B edits only this file. It reads shared constants from common.py (ST, PHI, CANT, HUB, YM, ZM, station/mrot/mworld frames, ZP
plate height): changing those needs coordination. Constants defined HERE are lane B's alone: PROP_D, CAN_*, SHAFT_*, ESC_X0, ESC_B,
PAD, ESC_PADS, ESC_TOP. Lane C's harness builder imports ESC_PADS and ESC_TOP from this file (the harness wires land on the ESC
pads and, T-083, leave the motor can radially toward +y at X_MB - LEAD_DX): both are unchanged by the fidelity round.

Labels: V = vendor page/drawing (URL, date checked 2026-11-15), PE0 = APC file vendor/apc/9x45MR-PERF.PE0, EST = estimate (flagged,
measure on arrival), CALC = computed here, "-" = unknown.
Motor-local frame (ctx.part at=station, rotate=mrot): x along the shaft, thrust toward -x, cup plate front face at x = -0.012.
"""
import math
import os

from .common import *   # noqa: F401,F403

IN = 0.0254

# ------------------------------------------------------------------ lane B constants (m)
PROP_D = 0.2286                             # 9 in (PE0 RADIUS 4.50 in)
# T-083 (D-227): SunnySky X2216 V3 880KV SHORT shaft (RMRC 84776, SS-XV3-X2216-S-880-V3). Drawing "X2216" on the SunnySky product page
# (https://cdn.shopify.com/s/files/1/2024/0305/files/X2216.jpg, linked from https://sunnyskyusa.com/products/sunnysky-x2216, read 2026-11-21; values
# marked D are read off that drawing). The page and drawing cover the X2216 V3 family; the KV880 table gives 67.5 g, Rm 89 mohm, 450 W.
# The LONG-shaft version (RMRC 85810, named by the config study) has the shaft leaving the BASE 16 mm (D: 50 - 34) with a Phi 9 x 5 collar: it would
# run into the arm tube behind the cup plate, so the short-shaft version is modelled (T083_report.md s3). Was: T-Motor MN2212 V2.0 KV780.
CAN_D, CAN_L = 0.0277, 0.032                           # D: rotor Phi 27.7; base face to bell-top face 32
BOSS_D, BOSS_L = 0.009, 0.002                          # D: bell-top boss Phi 9, 34 - 32 = 2
SHAFT_D = 0.003175                                     # D / V: Phi 3.175
SHAFT_REAR = 0.0025                                    # D (short shaft): 36.5 - 34 = 2.5 behind the base face
SHAFT_FRONT = 0.0                                      # short shaft: no shaft past the bell-top boss (D)
PAT19, PAT16 = 0.019, 0.016                            # D base view: 4-M3x0.5 depth 2.8, one pair 19 apart and one 16 apart on perpendicular lines, each 45 deg from the lead exit
TOP_PCD = 0.012                                        # D bell top: 3-M2x0.4 EQS depth 2.8 on Phi 12
LEAD_DX = 0.0025                                       # EST: lead exit centre 2.5 mm above the base face, radial, at the base end (D side view: lead leaves the can at the base end; exact height not dimensioned)
LEAD_L = 0.100                                         # D: lead length 100 (heat-shrink at the exit); gauge not given ("-"); drawn as the 1.8 mm 20 AWG strands (EST)
# X-mount (PRP-006, supplied with the motor; D view B-B): cross 34 x 34 hole spans, 41 overall, arm width 7 (EST from the "7" dimension), 3 thick,
# R6 root fillets, centre hole Phi 10.2, inner holes 4-Phi3.2 with Phi5.7 countersink on the 19 / 16 pattern, outer holes 4-Phi3.1 on 34. Material not stated ("-", aluminium EST).
BRK_T, BRK_SPAN, BRK_LEN, BRK_W, BRK_FIL = 0.003, 0.034, 0.041, 0.007, 0.006
BRK_C_D, BRK_IN_D, BRK_CS_D, BRK_OUT_D = 0.0102, 0.0032, 0.0057, 0.0031
BRK_ROT = 45.0                                         # T-083: arms on the cup diagonals so the four plate bolts (r 17) sit at |y|, |z| 12.0, clear of the arm sleeve (|z| < 7.9)
# SunnySky prop adapter (PRP-004, supplied; D view A-A): flange Phi 17 x 4 (22.5 - 18.5) with a Phi 9 recess over the bell-top boss (depth EST 2.2), 3-Phi2.1 holes
# with Phi4.1 counterbores on Phi 12, M5x0.8 stud Phi 5 x 18.5 (13 threaded); prop washer Phi 14.8 / Phi 5.1 x 2 (D, left of view A-A).
FLANGE_D, FLANGE_T, FL_REC_D, FL_REC_T = 0.017, 0.004, 0.009, 0.0022
STUD_D, STUD_L = 0.005, 0.0185
WASH_OD, WASH_ID, WASH_T = 0.0148, 0.0051, 0.002
NUT_AF, NUT_M = 0.008, 0.005                           # M5 nyloc ISO 10511 (s 8, m 5.0): chosen instead of the supplied bullet nut, whose size is not published, to keep the 0.50 m box
X_FACE = -0.012                                        # cup plate front face (lane A frame)
X_MB = X_FACE - BRK_T                                  # motor base face on the X-mount: -0.015
X_BELL_TOP = X_MB - CAN_L                              # -0.047
X_FLANGE_TOP = X_BELL_TOP - FLANGE_T                   # -0.051 (flange bears on the bell top; the 2 mm boss sits in the recess)
BASE_PAT = (PAT19, PAT16)                              # (old name kept for importers)
# APC 9x4.5MR. PE0 HUBRAD 0.32 in, retail hub diameter 0.65 in / thickness 0.34 in (amainhobbies, promodels listings, checked
# 2026-11-15; ReadyMadeRC says 0.33), bore 1/4 in "usually" (EST; the pack ships adapter rings)
HUB_D_P, HUB_T_P, HUB_BORE_P = 0.65 * IN, 0.34 * IN, 0.25 * IN
RING_ID, RING_OD = 0.005, HUB_BORE_P - 0.00005          # EST adapter ring: ID 5 for the M5 stud, OD fits the bore (dimensions not published)
MRP = {'UR', 'LL'}                                     # reverse (pusher-type) blade = rotates clockwise seen from the thrust side; others are standard MR
# basis: sitl/a_plant.py lines 69-76: CCW (+1) = LR, UL; CW (-1) = LL, UR. APC MR = standard = CCW, MRP = reverse = CW
# (promodels AP-09045MR / aerobertics AP-09045MRP, 2026-11-15). BOM-A.csv P02 / ORDER-LIST O2 relabelled 2026-11-15: RMRC calls MR "Standard (CW)" seen from behind the prop; seen from the thrust side (the view used here) MR is CCW.

# ESC layout on four R2 bosses (T-077 p5: the avionics plate is gone; ZP, the pad plane, is shared in common.py)
ESC_X0 = 0.082 + AV_DX                                                  # T-077 p5: 3b, 15 mm forward
ESC_B = ((ESC_X0, -0.0175, ZP), (ESC_X0 + 0.035, 0.0175, ZP + 0.0055))  # V SpeedyBee 35 x 35 x 5.5 (readymaderc 86873, 2026-11-15)
PAD = 0.003                                                             # half size of an ESC pad body
_e = ESC_X0 - 0.031
ESC_PADS = {'UR': (0.034 + _e, 0.013), 'LR': (0.046 + _e, 0.013), 'UL': (0.034 + _e, -0.013), 'LL': (0.046 + _e, -0.013),
            'BAT': (0.1045 + AV_DX, 0.012), 'SIG': (0.0635 + _e, 0.0)}
ESC_TOP = ZP + 0.0055
ESC_PCB_T = 0.0016                                                      # EST: PCB thickness (not published)
ESC_HOLE_D, ESC_HOLE_PITCH = 0.0035, 0.020                              # V: 20 x 20 pattern, 3.5 mm holes (M2 and M3 compatible)


# ------------------------------------------------------------------ APC PE0 blade data
def _read_pe0():
    path = os.path.join(HERE, 'vendor', 'apc', '9x45MR-PERF.PE0')
    rows = []
    with open(path, encoding='latin-1') as f:
        for ln in f:
            t = ln.split()
            if len(t) == 14:
                try:
                    rows.append([float(x) for x in t])
                except ValueError:
                    pass
    return rows


PE0 = _read_pe0()   # [station, chord, pitchQ, pitchLETE, pitchPrather, sweep, rake, thick ratio, twist, maxthick, xsec, zhigh, cgy, cgz] in inches, deg
_Z0 = 0.214         # in: PE0 z of the flat bottom at the hub (station 0: ZHIGH 0.095 - MAX-THICK 0.309); put on the adapter flange top
_R_START = 0.308    # in: first lofted blade station (hub radius is 0.32 in; the hub cylinder covers the root)
_NACA = lambda x: 0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1036 * x ** 4
_NMAX = max(_NACA(i / 1000.0) for i in range(1, 1000))
_XC = [0.5 * (1 - math.cos(math.pi * i / 8.0)) for i in range(9)]       # cosine spacing, LE (0) to TE (1)


def _section_pts(row):
    """Closed section loop in the PE0 plane (Y chordwise, Z thrust-ward), inches. SECTION SHAPE EST: flat lower surface (APC pitch
    is defined on a flat bottom, PE0 DEFINITIONS) and an upper surface of the NACA 4-digit thickness distribution scaled to the
    published MAX-THICK. PE0 names the real sections (E63 inboard, APC12 = NACA 4412 outboard) but gives no coordinates."""
    _, chord, _, _, _, sweep, rake, tr, tw, _, _, _, _, _ = row
    a = math.radians(tw)
    c = (-math.cos(a), -math.sin(a))             # LE -> TE (TE trails and sits lower)
    n = (-math.sin(a), math.cos(a))              # toward the suction (thrust-ward) side
    le = (sweep, rake)
    up, lo = [], []
    for x in _XC:
        base = (le[0] + x * chord * c[0], le[1] + x * chord * c[1])
        h = tr * chord * _NACA(x) / _NMAX
        up.append((base[0] + h * n[0], base[1] + h * n[1]))
        lo.append(base)
    return up[::-1] + lo[1:-1]                    # TE-up ... LE ... TE-lo (the TE point is the first of the loop)


def _blade_sections(sense, flip):
    """Loft sections (offset along the radial axis Y, loop (x, z)) for one blade in motor-local metres.
    sense: +1 standard MR (blade-travel direction PE0 +Y -> local -z), -1 reverse MRP (mirror image).
    flip: True for the opposite blade (rotation by 180 deg about the shaft)."""
    secs = []
    rows = [r for r in PE0 if r[0] >= _R_START - 1e-9]
    sel = [rows[i] for i in range(0, len(rows)) if i % 2 == 0 or rows[i][0] > 4.3]    # every second station + the tip stations
    if sel[-1][0] != rows[-1][0]:
        sel.append(rows[-1])
    for row in sel:
        r = row[0] * IN
        loop = []
        for y, z in _section_pts(row):
            u = X_FLANGE_TOP - (z + _Z0) * IN            # PE0 +Z (thrust) -> local -x
            v = -sense * y * IN                          # PE0 +Y (blade travel) -> local -z (MR) / +z (MRP)
            loop.append((u, -v if flip else v))
        if (sense < 0) != flip:
            loop = loop[::-1]                            # keep the winding consistent with the loft direction
        secs.append((-r if flip else r, loop))
    return secs


def prop_min_x_max_x():
    xs = [p[0] for _, l in _blade_sections(1, False) for p in l]
    return min(xs), max(xs)


# ------------------------------------------------------------------ parts
# propulsion
for s in ST:
    P('PRP-001-' + s, 'Motor SunnySky X2216 V3 880KV short shaft (%s), 67.5 g with 100 mm leads (EST that the page mass includes them)' % s, 'propulsion', 67.5,
      'Al / Cu / NdFeB', 'buy', 'sink')
    P('PRP-002-' + s, 'Prop APC 9x4.5%s (%s), %s' % ('MRP' if s in MRP else 'MR', s, 'CW reverse' if s in MRP else 'CCW standard'),
      'propulsion', 11.06, 'nylon-glass composite', 'buy')
P('PRP-003', 'ESC SpeedyBee BLS 35A Mini V2 4-in-1 with leads', 'propulsion', 20.0, 'PCB', 'buy', 'bus')


def _rev_mass_g(profile, rho_g_cm3):
    v, _ = fk.revolve_volume_centroid(profile)
    return round(v * 1e6 * rho_g_cm3, 1)


def _adapter_profile():
    """(a, r) from the bell-top face (a = 0) toward the prop: Phi 9 recess 2.2 deep, flange Phi 17 x 4, M5 stud 18.5 (D view A-A)."""
    r_f, r_s, r_r = FLANGE_D / 2, STUD_D / 2 - 0.00005, FL_REC_D / 2 + 0.0001
    return [(0, r_r), (0, r_f), (FLANGE_T, r_f), (FLANGE_T, r_s), (FLANGE_T + STUD_L, r_s), (FLANGE_T + STUD_L, 0),
            (FL_REC_T, 0), (FL_REC_T, r_r)]


def _bracket_area_m2():
    """X-mount plan area (two crossing 41 x 7 bars with rounded ends, 4 R6 root fillets, less the centre and 8 holes), CALC."""
    bars = 2 * (BRK_LEN - BRK_W) * BRK_W + 2 * math.pi * (BRK_W / 2) ** 2 - BRK_W ** 2
    fil = 4 * (BRK_FIL ** 2 - math.pi * BRK_FIL ** 2 / 4)
    holes = math.pi / 4 * (BRK_C_D ** 2 + 4 * BRK_IN_D ** 2 + 4 * BRK_OUT_D ** 2)
    return bars + fil - holes


for s in ST:
    P('PRP-004-' + s, 'Prop adapter, SunnySky (Phi17 x 4 flange + M5 stud 18.5, 3 x M2 on Phi 12) + prop washer Phi 14.8 x 2 (%s); supplied with the motor; mass CALC 6061, EST' % s,
      'propulsion', round(_rev_mass_g(_adapter_profile(), 2.70) - round(3 * math.pi * 0.00205 ** 2 * 0.002 * 2.7e6, 1)
                          + round(math.pi / 4 * (WASH_OD ** 2 - WASH_ID ** 2) * WASH_T * 2.7e6, 1), 1), '6061 aluminium (EST)', 'buy')
    P('PRP-005-' + s, 'M5 nyloc nut ISO 10511 (s 8, m 5) on the adapter stud (%s); replaces the supplied bullet nut (size not published); mass CALC steel' % s, 'propulsion',
      round((3 * math.sqrt(3) / 2 * (NUT_AF / math.sqrt(3)) ** 2 - math.pi * 0.0025 ** 2) * NUT_M * 7.85e6, 1), 'steel + nylon', 'buy')
    P('PRP-006-' + s, 'X-mount, SunnySky, supplied with the motor (%s): 34 x 34 cross, 3 mm; 4 x M3 countersunk to the motor, 4 x M3x14 + nyloc to the cup; mass CALC (aluminium EST)' % s,
      'propulsion', round(_bracket_area_m2() * BRK_T * 2.70e6 + 4 * 0.45 + 4 * 1.05, 1), 'aluminium (material not stated, EST) + steel screws', 'buy')

# ------------------------------------------------------------------ edges
# propulsion
for i, s in enumerate(ST):
    E(en('PRP'), 'PRP-001-' + s, 'PRP-006-' + s, 'CT-A-M3-CSK-MOTOR', 'propulsion',
      'motor base on the SunnySky X-mount: 4 x M3 countersunk (supplied) on the 19 / 16 pattern, heads flush in the mount countersinks (drawing view B-B)',
      joint_stack=STACK('M3x5 countersunk (supplied; length EST)', 4, 'Phi 3.2 holes with Phi 5.7 countersink in the X-mount; motor base 4-M3x0.5 depth 2.8 (drawing)', 1 + i,
                        eng=2.0, mineng=1.5))
    E(en('PRP'), 'PRP-006-' + s, 'CGE-003-' + s, 'CT-A-M3-BOLT-MOUNT', 'propulsion',
      'X-mount on the cup plate, arms on the diagonals: 4 x M3x14 socket head from the front through the mount (Phi 3.1) and the plate (3.4 mm), nyloc nuts behind the plate at |y|, |z| 12.0',
      joint_stack=STACK('M3x14 SHCS + M3 nyloc', 4, '3.4 mm clearance holes through the cup plate at r 17 on the diagonals; nuts on the plate back face', 40 + i,
                        eng=4.0, mineng=3.0))
    E(en('PRP'), 'PRP-002-' + s, 'PRP-004-' + s, 'CT-A-PROP-NUT', 'propulsion',
      'APC hub on the SunnySky adapter stud (APC adapter ring), washer Phi 14.8, M5 nyloc',
      joint_stack=STACK('M5 nyloc nut', 1, 'APC adapter ring (ID 5, EST) on the M5 stud', 10 + i, eng=5.0, mineng=4.0),
      field_joint=True)
E(en('PRP'), 'PRP-003', 'AVN-010', TAPEF, 'propulsion', 'ESC on the four R2 bosses, foam tape + tie',
  retention=dict(item='VHB-class tape', count=1))
for i, s in enumerate(ST):
    E(en('PRP'), 'PRP-004-' + s, 'PRP-001-' + s, 'CT-A-PROP-ADAPTER', 'propulsion',
      'SunnySky prop adapter flange on the bell top over the Phi 9 boss, 3 x M2 on Phi 12 (drawing: 3-Phi2.1, Phi4.1 counterbore; bell top 3-M2x0.4 depth 2.8)',
      joint_stack=STACK('M2x4 socket (supplied; length EST)', 3, 'Phi2.1 holes with Phi4.1 counterbore (depth EST 2.0) in the flange; bell top M2x0.4, 2.8 deep', 20 + i, eng=2.0, mineng=1.5),
      field_joint=True)
    E(en('PRP'), 'PRP-005-' + s, 'PRP-004-' + s, 'CT-A-PROP-NUT', 'propulsion', 'M5 nyloc on the stud, 2.9 mm of stud past the nut',
      joint_stack=STACK('M5 nyloc', 1, 'M5x0.8 stud, 13 mm threaded (drawing)', 30 + i, eng=5.0, mineng=4.0),
      field_joint=True)


# ------------------------------------------------------------------ geometry builder
def _polyloop(cx, cy, r, n=16):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def _m25_screw(part, seat, sense, length, name):
    """ISO 4762 M2.5 socket head (dk 4.5, k 2.5, hex 2.0, 1.2 deep) + 2.5 mm shank; seat = head bearing face on the X axis line."""
    R, k, rr, rt = 0.00225, 0.0025, 0.001, 0.0012
    prof = [(0, 0), (0, R), (-k, R), (-k, rr), (-(k - rt), rr), (-(k - rt), 0)]
    if sense < 0:
        prof = [(-a, r) for a, r in reversed(prof)]
    part.revolve('X', seat, prof, name=name + ' head')
    part.cylinder('X', seat, sense * length, 0.00125, name=name + ' shank')


def _hex_loop(u, v, af, phase=0.0):
    r = af / math.sqrt(3)
    return [(u + r * math.cos(phase + math.pi * k / 3), v + r * math.sin(phase + math.pi * k / 3)) for k in range(6)]


def _diag(r, k):
    """point at radius r on the cup diagonal k (0: +y+z, 1: -y+z, 2: -y-z, 3: +y-z) = BRK_ROT + 90 k deg from +y"""
    a = math.radians(BRK_ROT + 90 * k)
    return r * math.cos(a), r * math.sin(a)


def _bracket_loops():
    """X-mount plan outline in the (y, z) plane, CCW: two crossing 41 x 7 bars with round ends on the diagonals and R6 root fillets (CALC; D view B-B)."""
    hw, R, n = BRK_W / 2, BRK_FIL, 8
    tip = BRK_LEN / 2 - hw
    pts = []
    for k in range(4):
        a = math.radians(BRK_ROT + 90 * k)
        u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
        P_ = lambda s_, t_: (s_ * u[0] + t_ * v[0], s_ * u[1] + t_ * v[1])
        pts.append(P_(hw + R, -hw))
        for t in range(n + 1):
            th = -math.pi / 2 + math.pi * t / n
            pts.append(P_(tip + hw * math.cos(th), hw * math.sin(th)))
        pts.append(P_(hw + R, hw))
        c = P_(hw + R, hw + R)
        for t in range(1, n):
            th = a - math.pi / 2 - (math.pi / 2) * t / n
            pts.append((c[0] + R * math.cos(th), c[1] + R * math.sin(th)))
    return pts


def _ring(cx, cy, r, n=16):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def build_propulsion(ctx):
    exempt = {}
    for st in ST:
        # ---- motor (D drawing X2216.jpg, 2026-11-21): can Phi 27.7 x 32 from the base face, bell-top boss Phi 9 x 2, rear shaft stub Phi 3.175 x 2.5
        m = ctx.part('PRP-001-' + st, at=station(st), rotate=mrot(st), rgb=(0.15, 0.3, 0.75))
        m.revolve('X', (X_MB, 0.0, 0.0), [(0, 0), (0, CAN_D / 2), (-CAN_L, CAN_D / 2), (-CAN_L, 0)],
                  name='can Phi 27.7 x 32, base face to bell top (D; base vent openings, bell-top spokes and skirt slots not modelled)')
        m.revolve('X', (X_BELL_TOP, 0.0, 0.0), [(0, 0), (0, BOSS_D / 2), (-BOSS_L, BOSS_D / 2), (-BOSS_L, 0)], name='bell-top boss Phi 9 x 2 (D)')
        m.cylinder('X', (X_MB, 0.0, 0.0), SHAFT_REAR, SHAFT_D / 2, name='shaft stub, base side, Phi 3.175 x 2.5 (D, short-shaft version)')
        for k, rr in ((0, PAT19 / 2), (2, PAT19 / 2), (1, PAT16 / 2), (3, PAT16 / 2)):
            y, z = _diag(rr, k)
            # countersunk M3 (supplied): head flush with the X-mount back face (= cup plate front face), shank 2.0 mm into the base (depth 2.8)
            m.revolve('X', (X_FACE, y, z), [(0, 0), (0, 0.0028), (-0.00125, 0.00155), (-0.00125, 0)], name='motor screw countersunk head (EST)')
            m.cylinder('X', (X_FACE - 0.00125, y, z), -(BRK_T - 0.00125 + 0.002), 0.0015, name='motor screw shank M3')
        # D-198 / T-083: the 3 phase leads are drawn as the harness strands E-HRN-02..05; they leave the can radially at the base end toward +y (cup frame)
        # ---- X-mount (supplied; D view B-B), arms on the cup diagonals
        b = ctx.part('PRP-006-' + st, at=station(st), rotate=mrot(st), rgb=(0.12, 0.12, 0.12))
        holes = [_ring(0.0, 0.0, BRK_C_D / 2, 24)]
        for k in range(4):
            holes.append(_ring(*_diag(BRK_SPAN / 2, k), BRK_OUT_D / 2, 12))
            holes.append(_ring(*_diag(PAT19 / 2 if k % 2 == 0 else PAT16 / 2, k), BRK_IN_D / 2, 12))
        b.prism('X', X_MB, [_bracket_loops()] + holes, BRK_T, name='X-mount plate 3 mm (D view B-B; arm width 7 EST)')
        for k in range(4):
            y, z = _diag(PAT19 / 2 if k % 2 == 0 else PAT16 / 2, k)
            b.cut(fk.Shape('revolve', 'countersink Phi 5.7 x 90 deg (D)', axis='X', center=(X_FACE, y, z),
                           profile=[(0.0, 0.0), (0.0, BRK_CS_D / 2), (-(BRK_CS_D - BRK_IN_D) / 2, BRK_IN_D / 2), (-(BRK_CS_D - BRK_IN_D) / 2, 0.0)]))
        for k in range(4):
            y, z = _diag(BRK_SPAN / 2, k)
            k9.hw_screw(b, 'X', (X_MB, y, z), 1, 'M3', 0.014, 'socket', name='mount bolt M3x14')
            xb = X_FACE + (0.0042 if y < 0 else 0.0050)            # plate back face: web 4.2 mm on the sleeve side (y < 0), 5.0 mm on the cantilever
            b.prism('X', xb, [_hex_loop(y, z, 0.0055, 0.0), _ring(y, z, 0.0015, 12)], 0.004, name='mount nyloc M3 (s 5.5, m 4; flat toward the arm)')
        # ---- SunnySky prop adapter + washer, M5 nyloc
        ad = ctx.part('PRP-004-' + st, at=station(st), rotate=mrot(st), rgb=(0.15, 0.3, 0.75))
        ad.revolve('X', (X_BELL_TOP, 0.0, 0.0), [(-a, r) for a, r in _adapter_profile()], name='adapter flange Phi 17 x 4 + M5 stud 18.5 (D)')
        for k in range(3):
            a = math.radians(90 + 120 * k)
            yy, zz = TOP_PCD / 2 * math.cos(a), TOP_PCD / 2 * math.sin(a)
            ad.cut_cylinder('X', (X_FLANGE_TOP, yy, zz), 0.0020, 0.00205, name='counterbore Phi4.1 (depth EST 2.0)')
            ad.cut_cylinder('X', (X_FLANGE_TOP + 0.0020, yy, zz), 0.0020, 0.00105, name='hole Phi2.1')
            k9.hw_screw(ad, 'X', (X_FLANGE_TOP + 0.0020, yy, zz), 1, 'M2', 0.004, 'socket', name='adapter screw M2x4')
        ctx.seat('PRP-001-' + st, 'PRP-004-' + st, 'M2 thread holes in the bell top (depth 2.8)', bodies=('adapter screw',))
        x_hub_top = X_FLANGE_TOP - HUB_T_P
        ad.tube('X', (x_hub_top, 0.0, 0.0), -WASH_T, WASH_OD / 2, WASH_ID / 2, name='prop washer Phi 14.8 x 2 (D)')
        cn = ctx.part('PRP-005-' + st, at=station(st), rotate=mrot(st), rgb=(0.6, 0.6, 0.62))
        x_nut = x_hub_top - WASH_T
        cn.prism('X', x_nut - NUT_M, [_hex_loop(0.0, 0.0, NUT_AF, math.pi / 6), _ring(0.0, 0.0, 0.0025, 16)], NUT_M, name='M5 nyloc nut ISO 10511 s 8 x 5')
        # ---- prop: real blades from PE0 + hub + adapter ring
        sense = -1 if st in MRP else 1
        p = ctx.part('PRP-002-' + st, at=station(st), rotate=mrot(st), rgb=(0.15, 0.15, 0.15))
        p.loft('Y', _blade_sections(sense, False), name='blade 1 (PE0 chord/twist/sweep/rake; section EST)')
        p.loft('Y', _blade_sections(sense, True), name='blade 2 (PE0 chord/twist/sweep/rake; section EST)')
        p.tube('X', (X_FLANGE_TOP, 0.0, 0.0), -HUB_T_P, HUB_D_P / 2, HUB_BORE_P / 2, name='hub (0.65 x 0.34 in V; bore EST)')
        p.tube('X', (X_FLANGE_TOP, 0.0, 0.0), -HUB_T_P, RING_OD / 2, RING_ID / 2, name='APC adapter ring (EST)')
        hub = mworld(st, (X_FLANGE_TOP - HUB_T_P / 2, 0.0, 0.0))
        k9.prop_keepout(ctx, 'KO-PROP-' + st, hub, PROP_D, 0.005,
                        tuple('PRP-00%d-%s' % (k, st) for k in (1, 2, 4, 5)), rotate=mrot(st))
    # ---- ESC (V readymaderc 86873, 2026-11-15: 35 x 35 x 5.5, 20 x 20 pattern, 3.5 mm holes; pad layout, capacitor size, corner radius: not published)
    e = ctx.part('PRP-003', rgb=(0.1, 0.4, 0.1))
    (x0, y0, z0), (x1, y1, _) = ESC_B
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    holes = [_polyloop(cx + sx * ESC_HOLE_PITCH / 2, cy + sy * ESC_HOLE_PITCH / 2, ESC_HOLE_D / 2, 16) for sx in (1, -1) for sy in (1, -1)]
    sq = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    e.prism('Z', z0, [sq] + holes, ESC_PCB_T, name='PCB 35 x 35, 4 x 3.5 mm holes at 20 x 20 (thickness EST)')
    # component volume: the shape is not published, only the 5.5 mm overall height; drawn as the inset outline with relief round each hole
    ins = 0.0015
    comp = [(x0 + ins, y0 + ins), (x1 - ins, y0 + ins), (x1 - ins, y1 - ins), (x0 + ins, y1 - ins)]
    reliefs = [_polyloop(cx + sx * ESC_HOLE_PITCH / 2, cy + sy * ESC_HOLE_PITCH / 2, 0.0035, 16) for sx in (1, -1) for sy in (1, -1)]
    e.prism('Z', z0 + ESC_PCB_T, [comp] + reliefs, ESC_TOP - z0 - ESC_PCB_T, name='component volume envelope (shape unknown, 5.5 mm height V, EST outline)')
    for k, (x, y) in ESC_PADS.items():
        nm = {'BAT': 'battery pad joint', 'SIG': 'signal pad joint'}.get(k, 'motor pad joint ' + k)
        e.revolve('Z', (x, y, ESC_TOP), [(0, 0), (0, 0.0024), (0.002, 0.0016), (0.004, 0.0009), (0.004, 0)], name=nm + ' (solder mound, EST)')
