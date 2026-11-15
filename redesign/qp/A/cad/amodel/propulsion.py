"""amodel/propulsion.py - LANE B (propulsion): motors (PRP-001), props (PRP-002, swept disc + keep-outs), ESC (PRP-003) and its
pad layout, prop nut / adapter / motor screw joint stacks, and their edges + builder build_propulsion. Split from a_model.py;
no geometry change.

Lane B edits only this file. It reads shared constants from common.py (ST, PHI, CANT, HUB, YM, ZM, station/mrot/mworld frames, ZP
plate height): changing those needs coordination. Constants defined HERE are lane B's alone: PROP_D, CAN_D/L, SHAFT_D/L,
ESC_X0, ESC_B, PAD, ESC_PADS, ESC_TOP. Lane C's harness builder imports ESC_PADS and ESC_TOP from this file (the harness wires
land on the ESC pads), so moving the ESC pads needs lane C to re-check the wire routes.
"""
from .common import *   # noqa: F401,F403

# ------------------------------------------------------------------ lane B constants (m)
PROP_D = 0.2286                             # 9 in
CAN_D, CAN_L, SHAFT_D, SHAFT_L = 0.0275, 0.0265, 0.004, 0.012   # V tmotor page: 27.5 x 26.5, shaft 4; shaft length EST

# ESC layout on the avionics plate (the plate itself, PLATE_* and ZP, is shared in common.py)
ESC_X0 = 0.082
ESC_B = ((ESC_X0, -0.0175, ZP), (ESC_X0 + 0.035, 0.0175, ZP + 0.0055))  # V SpeedyBee 35 x 35 x 5.5
PAD = 0.003                                                             # half size of an ESC pad body
_e = ESC_X0 - 0.031
ESC_PADS = {'UR': (0.034 + _e, 0.013), 'LR': (0.046 + _e, 0.013), 'UL': (0.034 + _e, -0.013), 'LL': (0.046 + _e, -0.013),
            'BAT': (0.034 + _e, 0.0), 'SIG': (0.0635 + _e, 0.0)}
ESC_TOP = ZP + 0.0055


# ------------------------------------------------------------------ parts
# propulsion
for s in ST:
    P('PRP-001-' + s, 'Motor MN2212 V2.0 KV780 (%s)' % s, 'propulsion', 65.0, 'Al / Cu / NdFeB', 'buy', 'sink')
    P('PRP-002-' + s, 'Prop APC 9x4.5MR (%s), swept disc' % s, 'propulsion', 11.06, 'nylon-glass composite', 'buy')
P('PRP-003', 'ESC SpeedyBee BLS 35A Mini V2 4-in-1 with leads', 'propulsion', 20.0, 'PCB', 'buy', 'bus')

# ------------------------------------------------------------------ edges
# propulsion
for i, s in enumerate(ST):
    E(en('PRP'), 'PRP-001-' + s, 'CGE-003-' + s, 'CT-M3-SHCS-MOTOR', 'propulsion',
      'motor on the cup plate, 16 deg cant in the cup',
      joint_stack=STACK('M3x8 SHCS', 4, '3.4 mm clearance in the cup plate (EST pattern); motor base tapped M3', 1 + i,
                        eng=2.5, mineng=2.0))
    E(en('PRP'), 'PRP-002-' + s, 'PRP-001-' + s, 'CT-PROP-NUT', 'propulsion', 'APC adapter ring + prop nut on the shaft',
      joint_stack=STACK('M6x1 prop nut + washer', 1, 'adapter ring on the 4 mm shaft (EST)', 10 + i, eng=6.0, mineng=4.0),
      field_joint=True)
E(en('PRP'), 'PRP-003', 'AVN-001', TAPEF, 'propulsion', 'ESC on the plate, foam tape + tie',
  retention=dict(item='VHB-class tape', count=1))


# ------------------------------------------------------------------ geometry builder
def build_propulsion(ctx):
    for st in ST:
        m = ctx.part('PRP-001-' + st, at=station(st), rotate=mrot(st), rgb=(0.3, 0.3, 0.35))
        k9.motor_envelope(m, (-0.012, 0.0, 0.0), CAN_D, CAN_L, SHAFT_D, SHAFT_L)
        m.cylinder('X', (-0.012, 0.0, 0.0135), -0.005, 0.003, name='phase-lead exit')
        p = ctx.part('PRP-002-' + st, at=station(st), rotate=mrot(st), rgb=(0.2, 0.2, 0.2))
        p.tube('X', (-0.0395, 0.0, 0.0), -0.016, PROP_D / 2, 0.0021, name='prop swept disc')
        hub = mworld(st, (-0.0475, 0.0, 0.0))
        k9.prop_keepout(ctx, 'KO-PROP-' + st, hub, PROP_D, 0.005, ('PRP-001-' + st, 'PRP-002-' + st), rotate=mrot(st))
    e = ctx.part('PRP-003', rgb=(0.1, 0.4, 0.1))
    e.box(ESC_B[0], ESC_B[1], name='ESC board envelope')
    for k, (x, y) in ESC_PADS.items():
        nm = {'BAT': 'battery pad joint', 'SIG': 'signal pad joint'}.get(k, 'motor pad joint ' + k)
        e.box((x - PAD, y - PAD, ESC_TOP), (x + PAD, y + PAD, ESC_TOP + 0.004), name=nm)
