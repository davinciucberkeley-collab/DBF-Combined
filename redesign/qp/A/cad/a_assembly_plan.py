"""a_assembly_plan.py - minimal build sequence of concept A as data. Each step: id, caption, parts placed together as one rigid
body, direction of the final motion INTO the seat (world vector), travel (mm) and sampling step (mm). a_assembly.py checks
(1) support: every placed part has a mechanical edge to something already placed or to a part of its own step,
(2) the swept path: the member bodies, moved from seat - dir * travel to the seat, never penetrate (> 0.05 mm) a part placed
earlier (cuts, bores and pockets count as empty), and (3) every electrical edge is laid after both end parts are on.
Marker steps (parts = []) carry the wires: a 7th element lists the electrical edges LAID (soldered / mated) in that step; a_assembly.py checks that both
end parts of each edge are already on (earlier step) and that every electrical edge is laid exactly once. THREAD steps are marker steps that must come
before the step named in THREAD_BEFORE (the leads are fed through the tubes and channels while the ends are still free).
Not in the sequence: tape skin, hinge tape, epoxy fillets (not drawn). Wires are checked in place by collide_a.py.
D-202 (hub redesign): the cage frame is built on the bench in the sub-steps B0a-B0k (BENCH below): hub, arm tube B, its two pins, arm tube A, its pins and the crossing pin, the four doublers,
the bridge, the four motor cups, the two struts, then the lead threading. They are swept in their OWN run (a_assembly.py: bench plan, nothing else placed, because on the bench the
frame is away from the wing: the bridge slides in from aft along x, where the spar would be) and then B1 docks the finished frame (the CAGE group, every frame part, plus the motors and
props) on the spar as one rigid body, exactly as before. B1 is therefore the PLACEMENT of the CAGE parts in the main run; the bench steps list the same parts for the bench run only.
D-198/199: enclosed routes (motor leads in the arm bores, hub conduits, raceways and the foam ditch, servo leads in foam grooves) are threaded, then soldered after the boards are on."""
ST = ('UR', 'UL', 'LR', 'LL')
CAGE = (['CGE-00%d' % i for i in (1, 4, 6)] + ['CGE-002-A', 'CGE-002-B'] + ['CGE-003-' + s for s in ST] + ['CGE-009-' + s for s in ST] + ['CGE-010-' + s for s in ST] + ['CGE-010-C'] +
        ['CGE-005-R', 'CGE-005-L', 'CGE-007-R', 'CGE-007-L'] + ['PRP-001-' + s for s in ST] + ['PRP-004-' + s for s in ST] + ['PRP-002-' + s for s in ST] + ['PRP-005-' + s for s in ST])
# (id, caption, parts, dir, travel_mm, step_mm)
STEPS = [
    ('A1', 'Wing core on the bench (lower surface up)', ['WNG-001'], None, 0, 0),
    ('A2', 'Spar through the core bore from the right tip', ['WNG-002'], (0, -1, 0), 700, 100),
    ('A3', 'Centre plug up the bore', ['WNG-003-C'], (0, -1, 0), 600, 100),
    ('A4', 'Right plugs up the bore', ['WNG-004-R', 'WNG-005-R'], (0, -1, 0), 600, 100),
    ('A5', 'Left plugs up the bore from the left tip', ['WNG-004-L', 'WNG-005-L'], (0, 1, 0), 600, 100),
    # ---- D-202 bench build of the cage frame (swept in the bench run, see BENCH; unit vectors from the CAD: u_A = (0, cos 34.38, sin 34.38) along tube A toward UR, u_B = (0, cos 34.38, -sin 34.38) along tube B toward LR)
    ('B0a', 'Bench: cut the two arm tubes (552.4 mm), the bridge (114 mm) and the two struts (286.2 mm) from the carbon stock; sand the ends square', [], None, 0, 0),
    ('B0b', 'Bench: the printed hub stands on the bench, aft face down', ['CGE-001'], None, 0, 0),
    ('B0c', 'Arm tube B slid through its sleeve and the centre block (from the LL side, along its axis)', ['CGE-002-B'], (0, 0.8253073, -0.5646839), 330, 15),
    ('B0d', 'Two 3 mm pins (LR, UL) pushed in along x from the nose side through the block access holes, the sleeve and tube B', ['CGE-010-LR', 'CGE-010-UL'], (1, 0, 0), 30, 3),
    ('B0e', 'Arm tube A slid through its sleeve and the centre block (from the LL side, along its axis)', ['CGE-002-A'], (0, 0.8253073, 0.5646839), 330, 15),
    ('B0f', 'The crossing pin and the two tube A pins (UR, LL) pushed in along x from the nose side', ['CGE-010-C', 'CGE-010-UR', 'CGE-010-LL'], (1, 0, 0), 40, 4),
    ('B0g1', 'Doubler UR slid over the tube A end (UR side) into the sleeve counterbore', ['CGE-009-UR'], (0, -0.8253073, -0.5646839), 260, 5),
    ('B0g2', 'Doubler LL slid over the tube A end (LL side) into the sleeve counterbore', ['CGE-009-LL'], (0, 0.8253073, 0.5646839), 260, 5),
    ('B0g3', 'Doubler LR slid over the tube B end (LR side) into the sleeve counterbore', ['CGE-009-LR'], (0, -0.8253073, 0.5646839), 260, 5),
    ('B0g4', 'Doubler UL slid over the tube B end (UL side) into the sleeve counterbore', ['CGE-009-UL'], (0, 0.8253073, -0.5646839), 260, 5),
    ('B0h', 'Bridge tube pushed forward into the hub boss bore from aft, to the conical floor', ['CGE-004'], (-1, 0, 0), 130, 10),
    ('B0i1', 'Motor cup UR slid onto the tube A end', ['CGE-003-UR'], (0, -0.8253073, -0.5646839), 60, 5),
    ('B0i2', 'Motor cup LL slid onto the tube A end', ['CGE-003-LL'], (0, 0.8253073, 0.5646839), 60, 5),
    ('B0i3', 'Motor cup LR slid onto the tube B end', ['CGE-003-LR'], (0, -0.8253073, 0.5646839), 60, 5),
    ('B0i4', 'Motor cup UL slid onto the tube B end', ['CGE-003-UL'], (0, 0.8253073, -0.5646839), 60, 5),
    ('B0j1', 'Right strut pushed into its hub socket along its own axis', ['CGE-005-R'], (-0.40179, -0.9157318, 0), 40, 5),
    ('B0j2', 'Left strut pushed into its hub socket along its own axis', ['CGE-005-L'], (-0.40179, 0.9157318, 0), 40, 5),
    ('B0k', 'THREAD (bench, before the motors go on the cups): feed the three 20 AWG leads of each motor (400 mm stock + extension, EST) from the cup side through the 4.8 mm lead hole, the collar and the tube bore to the 4.8 mm exit hole at s +-18 mm; the free ends are laid flat along the tube until the hub conduits are on (B2b1-B2b4); then screw the motors on (B1)', [], None, 0, 0),
    ('B1', 'Cage unit (hub, arms, cups, bridge, struts, saddle, clips, motors, props) built on the bench, docked '
           'from below: clips snap on the spar', CAGE, (0, 0, 1), 30, 3),
    ('B2', 'Rib saddles snap on the spar from below', ['FIN-005-R', 'FIN-005-L'], (0, 0, 1), 30, 3),
    ('B2a', 'D-199: phase-lead raceways R and L lowered from above into their foam grooves (through the slots in the hub pad flange), before the tray', ['HRN-003-R', 'HRN-003-L'], (0, 0, -1), 30, 3),
    ('B2b1', 'D-202: hub conduit UR lowered onto its sleeve and the raceway window (along the tube t axis, toward the tube)', ['HRN-004-UR'], (0, 0.5646839, -0.8253073), 40, 4),
    ('B2b2', 'D-202: hub conduit UL lowered onto its sleeve and the raceway window', ['HRN-004-UL'], (0, -0.5646839, -0.8253073), 40, 4),
    ('B2b3', 'D-202: hub conduit LR raised onto its sleeve and the raceway window (from below)', ['HRN-004-LR'], (0, 0.5646839, 0.8253073), 40, 4),
    ('B2b4', 'D-202: hub conduit LL raised onto its sleeve and the raceway window (from below)', ['HRN-004-LL'], (0, -0.5646839, 0.8253073), 40, 4),
    ('B2c', 'THREAD: feed the free ends of the 12 phase strands (B0) through their hub conduit, the raceway and the foam ditch (fish thread from the ditch end); the free ends stay out at x 29 mm for the ESC pads', [], None, 0, 0),
    ('B3', 'Pack tray lowered from above into the core tray slot, bonded to the hub aft face', ['CGE-008'], (0, 0, -1), 30, 3),
    ('B4', 'Hinge damper units (stator with rotor in its annulus, silicone fluid filled) into the core notches at the elevon tips from aft, before the ribs; the notch is open aft', ['WNG-009-R', 'WNG-010-R', 'WNG-009-L', 'WNG-010-L'], (-1, 0, 0), 30, 5),
    ('C1', 'Ribs in from aft into the saddle sockets', ['FIN-002-R', 'FIN-002-L'], (-1, 0, 0), 300, 60),
    ('C1a', 'Rib fairings (upper blisters over the rib where it leaves the skin) lowered onto the skin from above, bonded', ['FIN-006-R', 'FIN-006-L'], (0, 0, -1), 15, 3),
    ('C2', 'Elevons with their balance horns on from aft (horn and lead enter the core pocket; tape hinge after)', ['WNG-006-R', 'WNG-006-L', 'WNG-007-R', 'WNG-007-L'], (-1, 0, 0), 25, 5),
    ('C2a', 'Upper lens caps (with stop bosses) lowered onto the skin over the strip windows, bonded', ['WNG-008-RU', 'WNG-008-LU'], (0, 0, -1), 15, 3),
    ('C2b', 'Lower lens caps (with stop bosses) raised onto the skin, bonded', ['WNG-008-RL', 'WNG-008-LL'], (0, 0, 1), 15, 3),
    ('C3', 'Fairing, right, from outboard', ['FIN-004-R'], (0, -1, 0), 40, 5),
    ('C4', 'Fairing, left, from outboard', ['FIN-004-L'], (0, 1, 0), 40, 5),
    ('C5', 'Root blocks onto the rib ends from aft', ['FIN-003-R', 'FIN-003-L'], (-1, 0, 0), 60, 5),
    ('C6', 'Fin tubes down through the blocks', ['FIN-001-R', 'FIN-001-L'], (0, 0, -1), 500, 100),
    ('C7', 'Upper shoes on the tube ends', ['GER-001-UR', 'GER-001-UL'], (0, 0, -1), 30, 5),
    ('C8', 'Lower shoes on the tube ends', ['GER-001-LR', 'GER-001-LL'], (0, 0, 1), 30, 5),
    ('C9', 'Foot pads on the shoe plates', ['GER-002-' + s for s in ST], (-1, 0, 0), 30, 5),
    ('D1', 'Servos into their pockets', ['MEC-001-R', 'MEC-001-L'], (0, 0, -1), 30, 5),
    ('D2', 'Servo arms on the splines', ['MEC-002-R', 'MEC-002-L'], (0, 0, -1), 15, 5),
    ('D2a', 'Arm screws M2x6 into the servo output shafts', ['HWC-002-R', 'HWC-002-L'], (0, 0, -1), 10, 5),
    ('D3', 'Horns on the elevons', ['MEC-004-R', 'MEC-004-L'], (0, 0, -1), 15, 5),
    ('D4', 'Pushrods into arm hole (Z-bend) and over the horn blade (clevis cheeks straddle it; pin follows in D5)', ['MEC-003-R', 'MEC-003-L'], (0, 0, -1), 10, 5),
    ('D5', 'Clevis pin R pressed in along y through the cheeks and the horn hole (from outboard)', ['MEC-005-R'], (0, -1, 0), 6, 1),
    ('D5b', 'Clevis pin L pressed in along y (from outboard)', ['MEC-005-L'], (0, 1, 0), 6, 1),
    ('E1', 'Pitot into its groove from the front', ['AVN-006'], (1, 0, 0), 250, 50),
    ('D0', 'THREAD: each servo 3-wire lead is fed from the servo pocket along its foam groove (3 mm under the skin, aft of the spar) to the slit at x 83 mm / |y| 24 mm with a fish wire; the free end stays out of the slit for the FC pads', [], None, 0, 0),
    ('E2', 'Avionics plate on the skin with its four M2 thin nuts already seated in the hex pockets', ['AVN-001', 'HWC-003'], (0, 0, -1), 20, 5),
    ('E3', 'ESC, foam-tape pads (hard mount), FC on the pads, RX, GPS, airspeed on the plate', ['PRP-003', 'AVN-007', 'AVN-002', 'AVN-003', 'AVN-004', 'AVN-005'], (0, 0, -1), 30, 5),
    ('E3a', 'Four M2 x 25 screws down through the FC stack into the nuts', ['HWC-001'], (0, 0, -1), 20, 5),
    ('E3b', 'LAY: solder the ESC signal ribbon to the FC, the servo leads to the FC pads S5 / S6, the RX CRSF lead, the GPS and airspeed leads (JST plugs on the sensor boards)', [], None, 0, 0, ['E-HRN-06', 'E-HRN-07', 'E-HRN-08', 'E-HRN-09', 'E-HRN-10', 'E-HRN-11']),
    ('E3c', 'Anti-slip pad stuck on the tray floor', ['PWR-003'], (0, 0, -1), 10, 2),
    ('E4', 'Pack into the tray', ['PWR-001'], (0, 0, -1), 30, 5),
    ('E4a', 'XT60 female with its tail mated to the pack lead XT60 male (plugs on from aft, taped on the skin; tail soldered to the ESC pads after)', ['HRN-002'], (-1, 0, 0), 15, 3),
    ('E4b', 'LAY: mate the pack XT60 male to the XT60 female (E4a) (done in E4a); the vendor pack power leads (E-HRN-13) and balance lead (E-HRN-14) come on the pack and are taped to the skin along their route, the balance plug on the pack top', [], None, 0, 0, ['E-HRN-01', 'E-HRN-13', 'E-HRN-14']),
    ('E5', 'Pack strap threaded under the bridge tube and closed over the pack (FLEXIBLE: no rigid insertion path exists, so this step checks the fitted position only, travel 0; the threading is by hand)', ['PWR-002'], None, 0, 0),
    ('E6', 'LAY: solder the battery tail to the ESC BAT pads and the 4 x 3 phase leads (free ends from B0 / B2c: out of the foam ditch, up to z 16, over the plate beside the FC, up to z 28 under the cover roof) to the ESC motor pads; heat-shrink', [], None, 0, 0, ['E-HRN-12', 'E-HRN-02', 'E-HRN-03', 'E-HRN-04', 'E-HRN-05']),
    ('E7', 'Bay cover lowered over the FC stack and ESC onto the plate (the sensor leads and the battery tail drop into the roof-open notches; the phase bundles are already inside), foam tape + two ties', ['AVN-008'], (0, 0, -1), 40, 4),
]
THREAD_BEFORE = {'B0k': 'B1', 'D0': 'E2', 'B2c': 'E2'}
# D-202 bench steps: swept in their own run (nothing of the wing placed), their parts are placed in the main run by B1 (the dock of the finished frame)
BENCH = ('B0b', 'B0c', 'B0d', 'B0e', 'B0f', 'B0g1', 'B0g2', 'B0g3', 'B0g4', 'B0h', 'B0i1', 'B0i2', 'B0i3', 'B0i4', 'B0j1', 'B0j2')
BENCH_START = 'B0b'                          # the hub is the first part of the frame: it rests on the bench (like the wing core in A1), so it has no earlier part to bond to

