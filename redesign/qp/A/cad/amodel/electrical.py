"""amodel/electrical.py - LANE C (avionics, power, mechanisms, harness, hardware): pack (PWR-001), avionics plate + FC/RX/GPS/
airspeed/pitot (AVN-*), servos/arms/pushrods/horns (MEC-*), landing feet (GER-*, kept here so the PARTS/EDGES registration order
stays identical: it sits on the fin tubes, lane A reviews it), harness + hardware lumps (HRN-001, HRD-001), electrical edges and wires,
and builders build_power / build_avionics / build_mechanisms / build_landing / build_harness / build_assembly (the generic joint
pass over EDGES). Split from a_model.py; no geometry change. Lane C also owns gen_interfaces.py.

Lane C edits only this file. It reads shared constants from common.py (see its header: PACK_X, TRIM, TRAY_X1, SERVO_Y, SV_Z1,
PLATE_*/ZP, FIN_*, YFIN, XFIN_T, ELEV_POSE ...): changing those needs coordination. It imports ESC_PADS and ESC_TOP from
propulsion.py (lane B). Constants defined HERE are lane C's alone: PACK_L/W/H, PACK_Z0, X_GROUND, FC_*, GEL, GEL_XY, RX_B, GPS_B,
AS_B, FC_PADS, FC_TOP, SV_X0/X1/DY/Z0, ARM_X0/X1/Z1, ROD_Z, HORN_X0/X1.
IMPORT ORDER MATTERS: PARTS/EDGES are ordered tables; amodel/__init__.py imports wing, propulsion, electrical in that order.
"""
from .common import *   # noqa: F401,F403
from .propulsion import ESC_PADS, ESC_TOP   # noqa: F401  (harness wires land on the ESC pads; lane B owns them)

# ------------------------------------------------------------------ lane C constants (m)
PACK_L, PACK_W, PACK_H = 0.105, 0.035, 0.029                    # V RMRC Tattu 2300 4S: 105 x 35 x 29
PACK_Z0 = 0.008
X_GROUND = 0.3375                           # EST: pad aft face (pad 30 mm DOC)
FC_X0 = 0.045                                                          # QP-4: FC hard-mounted ON the spar centre (spar axis x 0.060 = FC centre); ESC moved aft of it
GEL = 0.0015                                                           # EST thin foam tape (1.5 mm): FC HARD-MOUNTED (BOARD s3 D-186, s1 item 5); was 5 mm gel pads. CAD gates must be re-run
FC_B = ((FC_X0, -0.0125, ZP + GEL), (FC_X0 + 0.030, 0.0125, ZP + GEL + 0.020))             # V Kakute Wing Mini 30 x 25 x 20 (stack envelope)
RX_B = ((0.102, -0.0525, ZP), (0.122, -0.0405, ZP + 0.004))            # EST RP3 V2 (moved aft-left: the ESC took its place)
GPS_B = ((0.045, 0.0275, ZP), (0.070, 0.0525, ZP + 0.008))             # EST TBS M10Q
AS_B = ((0.045, -0.0525, ZP), (0.060, -0.0375, ZP + 0.008))            # EST MS4525 board
_f = FC_X0 - 0.071
FC_PADS = {'ESC': (0.0745 + _f, 0.0), 'GPS': (0.0745 + _f, 0.008), 'I2C': (0.0745 + _f, -0.008), 'S5': (0.0875 + _f, 0.009),
           'S6': (0.0875 + _f, -0.009), 'RX': (0.0975 + _f, 0.0)}
FC_TOP = ZP + GEL + 0.020
GEL_XY = [(0.048, -0.0095), (0.048, 0.0095), (0.072, -0.0095), (0.072, 0.0095)]    # EST under the four M2 holes
SV_X0, SV_X1, SV_DY, SV_Z0 = 0.1270, 0.1554, 0.01335, -0.0013    # SERVO.md: EMAX ES3054HV 28.4 x 13.0 x 26.7 (servodatabase / getfpv, 2026-11-15; spline kept at x 140.5); SV_Z1 = 0.0117 is in common.py
ARM_X0, ARM_X1, ARM_Z1 = 0.1405, 0.1525, SV_Z1 + 0.0020   # FIXES2: servo arm 19 -> 12 mm (pushrod end at 12 mm radius = horn radius 12.9 mm; the QP-4 CAD arm was longer than the horn, which the SERVO.md torque check assumed equal)
ROD_Z = 0.0127
HORN_X0, HORN_X1 = 0.195, 0.209


# ------------------------------------------------------------------ parts
# power / avionics
P('PWR-001', 'Pack Tattu 2300 mAh 4S 75C', 'power', 270.0, 'LiPo', 'buy', 'source')
P('AVN-001', 'Avionics plate', 'avionics', 8.0, 'PETG (printed)')   # QP-4 FIXES 12 -> 8 g: 4 lightening windows, EST
P('AVN-002', 'Flight controller Kakute F405 Wing Mini', 'avionics', 17.0, 'PCB', 'buy', 'bus')
P('AVN-007', 'Foam-tape pads x4 (FC hard mount, 1.5 mm)', 'avionics', 1.0, 'VHB-class foam tape', 'buy')
P('AVN-003', 'Receiver RP3 V2 ELRS', 'avionics', 3.0, 'PCB', 'buy', 'sink')
P('AVN-004', 'GPS TBS M10Q + compass', 'avionics', 13.5, 'PCB', 'buy', 'sink')
P('AVN-005', 'Airspeed sensor MS4525 board', 'avionics', 3.0, 'PCB', 'buy', 'sink')
P('AVN-006', 'Pitot probe', 'avionics', 5.0, 'brass tube', 'buy')
# mechanisms (30 g with linkage)
for s in 'RL':
    P('MEC-001-' + s, 'Servo EMAX ES3054HV (%s)' % s, 'mechanisms', 20.5, 'plastic / metal gear', 'buy', 'sink')
    P('MEC-002-' + s, 'Servo arm (%s)' % s, 'mechanisms', 1.0, 'nylon', 'buy')
    P('MEC-003-' + s, 'Pushrod 1.2 mm (%s)' % s, 'mechanisms', 1.0, 'steel', 'buy')
    P('MEC-004-' + s, 'Control horn (%s)' % s, 'mechanisms', 1.0, 'nylon', 'buy')
# landing
for s in ST:
    P('GER-001-' + s, 'Foot shoe (%s)' % s, 'landing', 1.4, 'PETG (printed)')
    P('GER-002-' + s, 'Foot pad EVA/PE 12x15x30 (%s)' % s, 'landing', 0.7, 'EVA / PE foam')
# harness / hardware lumps (proxies: mass and CG count, not drawn)
P('HRN-001', 'Harness remainder (wire, connectors, ties, tubing; MASS-GATE avionics 110 g less itemised parts) - lumped',
  'harness', None, 'copper / silicone', cg=[0.030, 0.0, 0.020], mass_proxy=True, carried=True)
P('HRD-001', 'Hardware: screws, nuts, epoxy fillets, paint (MASS-GATE 40 g less rib saddles) - lumped', 'assembly',
  30.0, 'steel / epoxy', cg=[0.100, 0.0, 0.0], mass_proxy=True, carried=True)   # QP-4 FIXES 37 -> 30 g: no paint (tape-skinned), EST bottom-up in FIXES.md
PARTS['HRN-001']['mass_g'] = round(106.0 - sum(PARTS[k]['mass_g'] for k in PARTS if k.startswith('AVN-')), 1)

# ------------------------------------------------------------------ edges
# power
E(en('PWR'), 'PWR-001', 'CGE-008', 'CT-STRAP-VELCRO', 'power', 'hook-and-loop strap round pack and tray, lips fore and aft',
  retention=dict(item='25 mm strap', count=1, load_n=38.8), field_joint=True)
# avionics
E(en('AVN'), 'AVN-001', 'WNG-001', CA, 'avionics', 'plate base follows the upper skin (same vertices as the core)')
E(en('AVN'), 'AVN-007', 'AVN-001', 'CT-GEL-PAD', 'avionics', 'four thin foam-tape pads on the plate (FC on the wing centre, not on the cage hub: SITL-FLIGHT follow-up 2; hard mount, BOARD D-186)')
E(en('AVN'), 'AVN-002', 'AVN-007', 'CT-GEL-PAD', 'avionics', 'FC on the tape pads, M2 screws (hard mount; gel only if its frequency is measured at 40-70 Hz)')
for pid in ('AVN-003', 'AVN-004', 'AVN-005'):
    E(en('AVN'), pid, 'AVN-001', TAPEF, 'avionics', 'foam tape + tie', retention=dict(item='VHB-class tape', count=1))
E(en('AVN'), 'AVN-006', 'WNG-001', EPX, 'avionics', 'pitot in a groove in the LE at y = +0.41 (outside the rotor wash, EST)')
# mechanisms
for s in 'RL':
    E(en('MEC'), 'MEC-001-' + s, 'WNG-001', EPX, 'mechanisms', 'servo in its pocket')
    E(en('MEC'), 'MEC-002-' + s, 'MEC-001-' + s, 'CT-SERVO-SPLINE', 'mechanisms', 'arm on the output spline',
      joint_stack=STACK('M2x6 retaining screw', 1, 'arm bore on the 25T spline', 20, eng=4.0, mineng=3.0))
    E(en('MEC'), 'MEC-003-' + s, 'MEC-002-' + s, 'CT-CLEVIS', 'mechanisms', 'rod end in the arm hole',
      motion=dict(axis='Z', range_deg=[-30, 30]))
    E(en('MEC'), 'MEC-003-' + s, 'MEC-004-' + s, 'CT-CLEVIS', 'mechanisms', 'rod end in the horn hole',
      motion=dict(axis='Y', range_deg=[-ELEV_POSE, ELEV_POSE]))
    E(en('MEC'), 'MEC-004-' + s, 'WNG-006-' + s, EPX, 'mechanisms', 'horn bonded on the elevon upper skin')
# landing
for s in ST:
    tube = 'FIN-001-' + ('R' if ST[s][0] > 0 else 'L')
    E(en('GER'), 'GER-001-' + s, tube, EPX, 'landing', 'shoe cap on the tube end')
    E(en('GER'), 'GER-002-' + s, 'GER-001-' + s, TAPEF, 'landing', 'pad PSA on the shoe plate')
# lumps (non-structural: located by ties)
E('E-HRN-20', 'HRN-001', 'WNG-001', 'CT-TIE', 'harness', 'harness lump: ties and tape on the wing')
E('E-ASM-01', 'HRD-001', 'WNG-001', 'CT-TIE', 'assembly', 'hardware lump')
# electrical (owner harness); ELEC[eid] = wire diameter in the CAD
EDGES.append(dict(id='E-HRN-01', part_a='PWR-001', part_b='PRP-003', via='CT-XT60', owner='harness',
                  notes='pack main lead (XT60 at the pack, disconnect) to the ESC battery pads',
                  wire=WIRE(14, 'XT60', 'R-A-01', ['rear tray lip', 'plate front edge'], 6, 'heat-shrink + tie', True),
                  current_a=dict(cont=11, peak=41)))
ELEC['E-HRN-01'] = 0.004
for i, s in enumerate(ST):
    eid = 'E-HRN-%02d' % (2 + i)
    EDGES.append(dict(id=eid, part_a='PRP-003', part_b='PRP-001-' + s, via='CT-SOLDER-PHASE', owner='harness',
                      notes='motor phase leads %s: ESC pad, over the LE, along the arm on the aft side, through the cup hole' % s,
                      wire=WIRE(18, 'solder + heat-shrink', 'R-A-%02d' % (2 + i),
                                ['tie at the plate edge', 'tie along the arm every 0.1 m', 'cup hole grommet'], 6,
                                'heat-shrink + tie at the cup'),
                      current_a=dict(cont=10.9, peak=12.1)))
    ELEC[eid] = 0.004
EDGES.append(dict(id='E-HRN-06', part_a='PRP-003', part_b='AVN-002', via='CT-JST-GH-6', owner='harness',
                  notes='ESC lead to the FC (VBAT, signals, telemetry)',
                  wire=WIRE(26, 'JST-GH 6-pin', 'R-A-06', ['tie on the plate'], 3, 'strain loop')))
ELEC['E-HRN-06'] = 0.0025
for i, s in enumerate('RL'):
    eid = 'E-HRN-%02d' % (7 + i)
    EDGES.append(dict(id=eid, part_a='AVN-002', part_b='MEC-001-' + s, via='CT-SERVO-JR', owner='harness',
                      notes='servo lead %s: FC servo pad, over the plate, laid on the skin to the servo pocket' % s,
                      wire=WIRE(26, 'JR 3-pin', 'R-A-%02d' % (7 + i), ['tie at the plate edge', 'tape on the skin'], 3,
                                'strain loop')))
    ELEC[eid] = 0.0025
for eid, a, b, ct, nm in (('E-HRN-09', 'AVN-002', 'AVN-003', 'CT-JST-GH-4', 'RX UART'),
                          ('E-HRN-10', 'AVN-002', 'AVN-004', 'CT-JST-GH-6', 'GPS'),
                          ('E-HRN-11', 'AVN-002', 'AVN-005', 'CT-JST-GH-4', 'airspeed I2C')):
    EDGES.append(dict(id=eid, part_a=a, part_b=b, via=ct, owner='harness', notes=nm + ' lead',
                      wire=WIRE(28, ct, 'R-' + eid[2:], ['tie on the plate'], 3, 'strain loop')))
    ELEC[eid] = 0.0015


# ------------------------------------------------------------------ geometry builders
def build_power(ctx):
    pk = ctx.part('PWR-001', rgb=(0.15, 0.15, 0.6))
    pk.box((PACK_X[0], -PACK_L / 2, PACK_Z0), (PACK_X[1], PACK_L / 2, PACK_Z0 + PACK_H), name='pack cells')
    pk.box((PACK_X[1], -0.004, 0.0300), (PACK_X[1] + 0.0055, 0.004, 0.0350), name='lead exit')


def build_avionics(ctx):
    pl = ctx.part('AVN-001', rgb=(0.9, 0.9, 0.9))
    loop = [(XS[i], zu(XS[i])) for i in range(PLATE_I0, PLATE_I1 + 1)] + [(PLATE_X1, ZP), (PLATE_X0, ZP)]
    pl.prism('Y', -PLATE_Y, [loop], 2 * PLATE_Y, name='plate')
    gl = ctx.part('AVN-007', rgb=(0.6, 0.8, 0.9))
    for gx, gy in GEL_XY:
        gl.box((gx - 0.003, gy - 0.003, ZP), (gx + 0.003, gy + 0.003, ZP + GEL), name='foam tape pad')
    fc = ctx.part('AVN-002', rgb=(0.1, 0.1, 0.5))
    fc.box(*FC_B, name='FC board envelope')
    for k, (x, y) in FC_PADS.items():
        nm = {'S5': 'servo pad S5', 'S6': 'servo pad S6'}.get(k, k + ' header')
        fc.box((x - 0.002, y - 0.002, FC_TOP), (x + 0.002, y + 0.002, FC_TOP + 0.003), name=nm)
    rx = ctx.part('AVN-003', rgb=(0.2, 0.2, 0.2))
    rx.box(*RX_B, name='RX board envelope')
    rx.box((0.1045, -0.0485, ZP + 0.004), (0.1085, -0.0445, ZP + 0.007), name='UART header')
    gp = ctx.part('AVN-004', rgb=(0.3, 0.3, 0.3))
    gp.box(*GPS_B, name='GPS envelope')
    gp.box((0.0465, 0.0285, ZP + 0.008), (0.0505, 0.0325, ZP + 0.011), name='JST-SH plug')
    asd = ctx.part('AVN-005', rgb=(0.3, 0.3, 0.3))
    asd.box(*AS_B, name='airspeed board envelope')
    asd.box((0.0465, -0.0325, ZP + 0.008), (0.0505, -0.0285, ZP + 0.011), name='I2C header')
    pt = ctx.part('AVN-006', rgb=(0.8, 0.7, 0.2))
    pt.tube('X', (-0.130, YFIN + 0.030, 0.0), 0.175, 0.0015, 0.0010, name='pitot tube')


def build_mechanisms(ctx):
    for s, sy in (('R', 1), ('L', -1)):
        yc = sy * SERVO_Y
        sv = ctx.part('MEC-001-' + s, rgb=(0.2, 0.2, 0.2))
        sv.box((SV_X0, yc - SV_DY, SV_Z0), (SV_X1, yc + SV_DY, SV_Z1), name='servo case')
        sv.box((0.1285, yc - 0.003, SV_Z1), (0.1325, yc + 0.003, SV_Z1 + 0.003), name='servo lead exit')
        ar = ctx.part('MEC-002-' + s, rgb=(0.9, 0.9, 0.9))
        ar.box((ARM_X0, yc - 0.003, SV_Z1), (ARM_X1, yc + 0.003, ARM_Z1), name='servo arm')
        rd = ctx.part('MEC-003-' + s, rgb=(0.6, 0.6, 0.6))
        rd.cylinder('X', (ARM_X1, yc, ROD_Z), HORN_X0 - ARM_X1, 0.0006, name='pushrod')
        zb = zu(HORN_X0)
        hn = ctx.part('MEC-004-' + s, rgb=(0.9, 0.9, 0.9))
        hn.box((HORN_X0, yc - 0.001, zb), (HORN_X1, yc + 0.001, zb + 0.010), name='control horn')


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


def build_harness(ctx):
    h = ctx.part('HRN-001', proxy=True)
    h.cylinder('X', (0.030, 0.0, 0.005), 0.002, 0.001, name='harness lump')
    z_pad = ESC_TOP + 0.002
    bx, by = ESC_PADS['BAT']
    x0 = PACK_X[1] + 0.0025                                  # lead leaves the pack, passes round the FC (y -26.5 mm) to the ESC battery pad
    xb = FC_B[1][0] + 0.0035
    ctx.wire('E-HRN-01', [(x0, 0.0, 0.0325), (x0, -0.0265, 0.0325), (xb, -0.0265, 0.0325), (xb, 0.0, 0.0325), (bx, 0.0, 0.0325), (bx, by, z_pad)], dia=0.004)
    for i, st in enumerate(ST):
        px, py = ESC_PADS[st]
        sy, sz = ST[st]
        a0, h1, h2 = _arm_line(st)
        zl_, yl = (0.040, 0.062) if sz > 0 else (0.0325, 0.088)
        yl *= sy
        pts = [(px, py, z_pad), (px, py, zl_), (px, yl, zl_), (a0[0], yl, zl_), a0, h1, h2]
        ctx.wire('E-HRN-%02d' % (2 + i), pts, dia=0.004)
    sx, sy_ = ESC_PADS['SIG']
    fx, fy = FC_PADS['ESC']
    ctx.wire('E-HRN-06', [(sx, sy_, z_pad), (sx, sy_, 0.052), (fx, fy, 0.052), (fx, fy, FC_TOP + 0.0015)], dia=0.0025)
    for i, (key, sg) in enumerate((('S5', 1), ('S6', -1))):
        x, y = FC_PADS[key]
        yc = sg * SERVO_Y
        pts = [(x, y, FC_TOP + 0.0015), (x, y, 0.048), (x, sg * 0.075, 0.048), (x, sg * 0.075, 0.016), (x, yc, 0.016),
               (0.1305, yc, 0.016), (0.1305, yc, SV_Z1 + 0.0015)]
        ctx.wire('E-HRN-%02d' % (7 + i), pts, dia=0.0025)
    x, y = FC_PADS['RX']
    ctx.wire('E-HRN-09', [(x, y, FC_TOP + 0.0015), (x, y, 0.050), (x, -0.0465, 0.050), (0.1065, -0.0465, 0.050), (0.1065, -0.0465, ZP + 0.0055)], dia=0.0015)
    x, y = FC_PADS['GPS']
    ctx.wire('E-HRN-10', [(x, y, FC_TOP + 0.0015), (x, y, 0.054), (x, 0.0305, 0.054), (x, 0.0305, ZP + 0.0095)], dia=0.0015)
    x, y = FC_PADS['I2C']
    ctx.wire('E-HRN-11', [(x, y, FC_TOP + 0.0015), (x, y, 0.054), (x, -0.0305, 0.054), (x, -0.0305, ZP + 0.0095)], dia=0.0015)


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
        elif via in ('CT-M3-SHCS-MOTOR', 'CT-PROP-NUT', 'CT-SERVO-SPLINE'):
            ctx.rigid(e['id'], e['part_a'], e['part_b'], at)
        else:
            ctx.contact(e['id'], via)
