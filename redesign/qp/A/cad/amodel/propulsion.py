"""amodel/propulsion.py - LANE B (propulsion): motors (PRP-001), props (PRP-002: real APC 9x4.5MR/MRP blades from the PE0 file),
T-Motor prop adapter (PRP-004) and spinner nut (PRP-005), ESC (PRP-003) and its pad layout, joint stacks, edges and the builder
build_propulsion. Prop swept disc stays as a KEEP-OUT only (KO-PROP-*); the visible prop is the blades.

Lane B edits only this file. It reads shared constants from common.py (ST, PHI, CANT, HUB, YM, ZM, station/mrot/mworld frames, ZP
plate height): changing those needs coordination. Constants defined HERE are lane B's alone: PROP_D, CAN_*, SHAFT_*, ESC_X0, ESC_B,
PAD, ESC_PADS, ESC_TOP. Lane C's harness builder imports ESC_PADS and ESC_TOP from this file (the harness wires land on the ESC
pads and on the motor lead exit at motor-local (-0.0145, 0, 0.0135)): both are unchanged by the fidelity round.

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
# T-Motor MN2212 V2.0 KV780. V https://store.tmotor.com/goods-388-MN2212-V20.html and its drawing
# https://store.tmotor.com/images/202606/MN2212-draw-0603-v1.jpg (read 2026-11-15 from a 473 px render: values marked D below are read
# off the drawing, +-0.3 mm; the drawing text is not machine readable). The page also mentions "MN4112" once: the drawing
# (Phi 27.5, shaft Phi 4) was taken to be the MN2212 one.
CAN_D, CAN_L, SHAFT_D = 0.0275, 0.0265, 0.004         # V page: 27.5 x 26.5 (bell + base), shaft 4
SHAFT_FRONT, SHAFT_REAR = 0.0035, 0.0026               # D: 32.6 overall = 3.5 prop-side shaft + 26.5 body + 2.6 base-side stub
SHAFT_L = SHAFT_FRONT                                  # (old name; real prop-side shaft protrusion is 3.5, not 12)
BASE_T = 0.0035                                        # EST: base ring thickness (read off the side view, +-1 mm)
BASE_D = 0.0275                                        # EST: base ring takes the bell diameter (the 4 base holes at 19 x 16 lie 12.4 mm from the axis; ring Phi not published)
BASE_PAT = (0.019, 0.016)                              # D: base view of the drawing: 4-M2.5 on a 19 x 16 mm rectangle (matches lane A's CUP_PAT 19 along y x 16 along z)
TOP_PITCH = 0.012                                      # D: bell-top view: 2 holes at 12 mm pitch (prop adapter, Phi 3.2 thru with Phi 5.7 counterbore on the adapter); orientation about the shaft EST
FLANGE_D, FLANGE_T = 0.019, 0.0045                     # D: prop adapter flange Phi 19 x 4.5
STUD_D, STUD_L = 0.005, 0.0185                         # D: M5 stud; 18.5 above the flange top (the 13 and 24 dimensions are ambiguous in the render: flag)
CONE_D, CONE_L, CONE_TIP, CONE_BORE_D = 0.012, 0.016, 0.003, 0.012   # D: spinner Phi 12 x 16, tip Phi 3, M5 thread depth 12 (ogive curve EST)
X_FACE = -0.012                                        # cup plate front face (lane A frame)
X_BELL_TOP = X_FACE - CAN_L                            # -0.0385
X_FLANGE_TOP = X_BELL_TOP - FLANGE_T                   # -0.0430
# APC 9x4.5MR. PE0 HUBRAD 0.32 in, retail hub diameter 0.65 in / thickness 0.34 in (amainhobbies, promodels listings, checked
# 2026-11-15; ReadyMadeRC says 0.33), bore 1/4 in "usually" (EST; the pack ships adapter rings)
HUB_D_P, HUB_T_P, HUB_BORE_P = 0.65 * IN, 0.34 * IN, 0.25 * IN
RING_ID, RING_OD = 0.005, HUB_BORE_P - 0.00005          # EST adapter ring: ID 5 for the M5 stud, OD fits the bore (dimensions not published)
MRP = {'UR', 'LL'}                                     # reverse (pusher-type) blade = rotates clockwise seen from the thrust side; others are standard MR
# basis: sitl/a_plant.py lines 69-76: CCW (+1) = LR, UL; CW (-1) = LL, UR. APC MR = standard = CCW, MRP = reverse = CW
# (promodels AP-09045MR / aerobertics AP-09045MRP, 2026-11-15). BOM-A.csv P02 / ORDER-LIST O2 relabelled 2026-11-15: RMRC calls MR "Standard (CW)" seen from behind the prop; seen from the thrust side (the view used here) MR is CCW.

# ESC layout on the avionics plate (the plate itself, PLATE_* and ZP, is shared in common.py)
ESC_X0 = 0.082
ESC_B = ((ESC_X0, -0.0175, ZP), (ESC_X0 + 0.035, 0.0175, ZP + 0.0055))  # V SpeedyBee 35 x 35 x 5.5 (readymaderc 86873, 2026-11-15)
PAD = 0.003                                                             # half size of an ESC pad body
_e = ESC_X0 - 0.031
ESC_PADS = {'UR': (0.034 + _e, 0.013), 'LR': (0.046 + _e, 0.013), 'UL': (0.034 + _e, -0.013), 'LL': (0.046 + _e, -0.013),
            'BAT': (0.1045, 0.012), 'SIG': (0.0635 + _e, 0.0)}
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
    P('PRP-001-' + s, 'Motor MN2212 V2.0 KV780 (%s)' % s, 'propulsion', 65.0, 'Al / Cu / NdFeB', 'buy', 'sink')
    P('PRP-002-' + s, 'Prop APC 9x4.5%s (%s), %s' % ('MRP' if s in MRP else 'MR', s, 'CW reverse' if s in MRP else 'CCW standard'),
      'propulsion', 11.06, 'nylon-glass composite', 'buy')
P('PRP-003', 'ESC SpeedyBee BLS 35A Mini V2 4-in-1 with leads', 'propulsion', 20.0, 'PCB', 'buy', 'bus')


def _rev_mass_g(profile, rho_g_cm3):
    v, _ = fk.revolve_volume_centroid(profile)
    return round(v * 1e6 * rho_g_cm3, 1)


def _adapter_profile():
    r_f, r_s, r_b = FLANGE_D / 2, STUD_D / 2 - 0.00005, SHAFT_D / 2
    return [(0, r_b), (0, r_f), (FLANGE_T, r_f), (FLANGE_T, r_s), (FLANGE_T + STUD_L, r_s), (FLANGE_T + STUD_L, 0),
            (FLANGE_T - 0.0010, 0), (FLANGE_T - 0.0010, r_b)]


_CONE_DEPTH = 0.012                         # D: M5 thread depth 12


def _cone_profile():
    n = 8
    outer = [(CONE_L * i / n, CONE_TIP / 2 + (CONE_D / 2 - CONE_TIP / 2) * math.sqrt(max(0.0, 1 - (CONE_L * i / n / CONE_L) ** 2)))
             for i in range(n + 1)]                 # EST ogive between the drawn Phi12 base and Phi3 tip
    return [(0, STUD_D / 2)] + outer + [(CONE_L, 0), (_CONE_DEPTH, 0), (_CONE_DEPTH, STUD_D / 2)]


_cone_profile_fixed = _cone_profile


for s in ST:
    P('PRP-004-' + s, 'Prop adapter, T-Motor (Phi19 x 4.5 flange + M5 stud) (%s); mass CALC 6061, EST' % s, 'propulsion',
      _rev_mass_g(_adapter_profile(), 2.70), '6061 aluminium', 'buy')
    P('PRP-005-' + s, 'Spinner nut, T-Motor (Phi12 x 16, M5) (%s); mass CALC 6061, EST' % s, 'propulsion',
      _rev_mass_g(_cone_profile_fixed(), 2.70), '6061 aluminium', 'buy')

# ------------------------------------------------------------------ edges
# propulsion
for i, s in enumerate(ST):
    E(en('PRP'), 'PRP-001-' + s, 'CGE-003-' + s, 'CT-A-M25-SHCS-MOTOR', 'propulsion',
      'motor on the cup plate, 17 deg cant in the cup; 4 x M2.5x8 on the 19 x 16 base pattern of the T-Motor drawing',
      joint_stack=STACK('M2.5x8 SHCS', 4, '2.9 mm (ISO 273 medium M2.5) clearance holes in the cup plate (CUP_PAT 19 x 16, D-194); motor base tapped M2.5 (drawing 4-M2.5; length EST)', 1 + i,
                        eng=3.0, mineng=2.0))
    E(en('PRP'), 'PRP-002-' + s, 'PRP-004-' + s, 'CT-A-PROP-NUT', 'propulsion',
      'APC hub on the T-Motor adapter stud (APC adapter ring), clamped by the spinner nut',
      joint_stack=STACK('M5 spinner nut (T-Motor)', 1, 'APC adapter ring (ID 5, EST) on the M5 stud', 10 + i, eng=9.0, mineng=5.0),
      field_joint=True)
E(en('PRP'), 'PRP-003', 'AVN-001', TAPEF, 'propulsion', 'ESC on the plate, foam tape + tie',
  retention=dict(item='VHB-class tape', count=1))
for i, s in enumerate(ST):
    E(en('PRP'), 'PRP-004-' + s, 'PRP-001-' + s, 'CT-A-PROP-ADAPTER', 'propulsion',
      'T-Motor prop adapter flange on the bell top, 2 x M3 at 12 mm pitch (drawing: 2-Phi3.2, Phi5.7 counterbore)',
      joint_stack=STACK('M3x6 SHCS', 2, 'Phi3.2 holes with Phi5.7 counterbore in the flange; bell-top thread and thickness not published (EST)', 20 + i, eng=4.0, mineng=2.0),
      field_joint=True)
    E(en('PRP'), 'PRP-005-' + s, 'PRP-004-' + s, 'CT-A-PROP-NUT', 'propulsion', 'spinner nut threaded on the M5 stud',
      joint_stack=STACK('M5 thread (cone nut)', 1, 'internal M5 thread, 12 mm deep (drawing)', 30 + i, eng=9.0, mineng=5.0),
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


def build_propulsion(ctx):
    exempt = {}
    for st in ST:
        # ---- motor (V drawing MN2212-draw-0603-v1.jpg, 2026-11-15)
        m = ctx.part('PRP-001-' + st, at=station(st), rotate=mrot(st), rgb=(0.3, 0.3, 0.35))
        xb = X_FACE - BASE_T
        m.revolve('X', (X_FACE, 0.0, 0.0), [(0, 0), (0, BASE_D / 2), (-BASE_T, BASE_D / 2), (-BASE_T, 0)], name='stator base ring (EST)')
        m.revolve('X', (xb, 0.0, 0.0), [(0, 0), (0, CAN_D / 2), (-(CAN_L - BASE_T), CAN_D / 2), (-(CAN_L - BASE_T), 0)],
                  name='bell (outline V; vents and skirt step not modelled)')
        m.cylinder('X', (X_BELL_TOP, 0.0, 0.0), -SHAFT_FRONT, SHAFT_D / 2 - 0.00001, name='shaft, prop side')
        m.cylinder('X', (X_FACE, 0.0, 0.0), SHAFT_REAR, SHAFT_D / 2, name='shaft stub, base side')
        for sy in (1, -1):
            for sz in (1, -1):
                _m25_screw(m, (X_FACE + 0.0049, sy * BASE_PAT[0] / 2, sz * BASE_PAT[1] / 2), -1, 0.008, 'motor screw')
        # D-198: the 3 x 20 AWG phase leads are drawn as the harness strands E-HRN-02..05 (start inside the base ring at y 5.5 mm: exit position EST, not on the T-Motor drawing)
        ctx.seat('CGE-003-' + st, 'PRP-001-' + st, 'motor shaft-stub relief and M3 clearance holes + head counterbores',
                 bodies=('shaft stub', 'motor screw'))
        # ---- T-Motor prop adapter and spinner nut
        ad = ctx.part('PRP-004-' + st, at=station(st), rotate=mrot(st), rgb=(0.7, 0.7, 0.72))
        ad.revolve('X', (X_BELL_TOP, 0.0, 0.0), [(-a, r) for a, r in _adapter_profile()], name='adapter flange + M5 stud')
        for sg in (1, -1):
            xf = X_FLANGE_TOP + 0.0032                    # counterbore floor (depth EST 3.2 for the 3 mm M3 head)
            ad.cut_cylinder('X', (xf, sg * TOP_PITCH / 2, 0.0), -0.0032, 0.00285, name='counterbore Phi5.7')
            ad.cut_cylinder('X', (xf, sg * TOP_PITCH / 2, 0.0), 0.0013, 0.0016, name='hole Phi3.2')
            k9.hw_screw(ad, 'X', (xf, sg * TOP_PITCH / 2, 0.0), 1, 'M3', 0.006, 'socket', name='adapter screw')
        ctx.seat('PRP-001-' + st, 'PRP-004-' + st, 'M3 thread holes in the bell top', bodies=('adapter screw',))
        x_hub_top = X_FLANGE_TOP - HUB_T_P
        cn = ctx.part('PRP-005-' + st, at=station(st), rotate=mrot(st), rgb=(0.2, 0.2, 0.25))
        cn.revolve('X', (x_hub_top, 0.0, 0.0), [(-a, r) for a, r in _cone_profile_fixed()], name='spinner nut (ogive EST)')
        # ---- prop: real blades from PE0 + hub + adapter ring
        sense = -1 if st in MRP else 1
        p = ctx.part('PRP-002-' + st, at=station(st), rotate=mrot(st), rgb=(0.15, 0.15, 0.15))
        p.loft('Y', _blade_sections(sense, False), name='blade 1 (PE0 chord/twist/sweep/rake; section EST)')
        p.loft('Y', _blade_sections(sense, True), name='blade 2 (PE0 chord/twist/sweep/rake; section EST)')
        p.tube('X', (X_FLANGE_TOP, 0.0, 0.0), -HUB_T_P, HUB_D_P / 2, HUB_BORE_P / 2, name='hub (0.65 x 0.34 in V; bore EST)')
        p.tube('X', (X_FLANGE_TOP, 0.0, 0.0), -HUB_T_P, RING_OD / 2, RING_ID / 2, name='APC adapter ring (EST)')
        hub = mworld(st, (-0.0475, 0.0, 0.0))
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
