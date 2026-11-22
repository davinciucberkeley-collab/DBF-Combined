"""a_assembly_plan.py - minimal build sequence of concept A as data. Each step: id, caption, parts placed together as one rigid
body, direction of the final motion INTO the seat (world vector), travel (mm) and sampling step (mm). a_assembly.py checks
(1) support: every placed part has a mechanical edge to something already placed or to a part of its own step,
(2) the swept path: the member bodies, moved from seat - dir * travel to the seat, never penetrate (> 0.05 mm) a part placed
earlier (cuts, bores and pockets count as empty), and (3) every electrical edge is laid after both end parts are on.
Marker steps (parts = []) carry the wires: a 7th element lists the electrical edges LAID (soldered / mated) in that step; a_assembly.py checks that both
end parts of each edge are already on (earlier step) and that every electrical edge is laid exactly once. THREAD steps are marker steps that must come
before the step named in THREAD_BEFORE (the leads are fed through the tubes and channels while the ends are still free).
Not in the sequence: tape skin (the glass skin WNG-011 and cove strip WNG-012 are laid in A1), hinge tape, epoxy fillets (not drawn). Wires are checked in place by collide_a.py.
D-202 (hub redesign): the cage frame is built on the bench in the sub-steps B0a-B0k (BENCH below): hub, arm tube B, its two pins, arm tube A, its pins and the crossing pin, the four doublers,
the bridge, the four motor cups, the two struts, then the lead threading. They are swept in their OWN run (a_assembly.py: bench plan, nothing else placed, because on the bench the
frame is away from the wing: the bridge slides in from aft along x, where the spar would be) and then B1 docks the finished frame (the CAGE group, every frame part, plus the motors and
props) on the spar as one rigid body, exactly as before. B1 is therefore the PLACEMENT of the CAGE parts in the main run; the bench steps list the same parts for the bench run only.
D-198/199: enclosed routes (motor leads in the arm bores, hub conduits, raceways and the foam ditch, servo leads in foam grooves) are threaded, then soldered after the boards are on."""
ST = ('UR', 'UL', 'LR', 'LL')
# T-077 p8 (D-226): torsion-cell path. B2 (printed rib saddles) removed, C1b (lower rib fairings) added, A2..A5 (spar and plugs) moved after the cage dock B1.
# T-077 p7 (D-225): written for wing.py P5_CLAMSHELL = P5_NODE = False (part-4 saddles). If a P5_VARIANT re-draws the clamshell or node, the p5 steps A1b / C1p and the CGE-011..013 CAGE entries (git 428d8368) must be restored.
CAGE = (['CGE-00%d' % i for i in (1, 4, 6)] + ['CGE-002-A', 'CGE-002-B'] + ['CGE-003-' + s for s in ST] + ['CGE-009-' + s for s in ST] + ['CGE-010-' + s for s in ST] + ['CGE-010-C'] +
        ['CGE-005-R', 'CGE-005-L', 'CGE-007-R', 'CGE-007-L'] + ['PRP-006-' + s for s in ST] + ['PRP-001-' + s for s in ST] + ['PRP-004-' + s for s in ST] + ['PRP-002-' + s for s in ST] + ['PRP-005-' + s for s in ST])
# (id, caption, parts, dir, travel_mm, step_mm)
STEPS = [
    ('A1', 'Wing core on the bench (lower surface up), built in segments round the four CF bulkheads (centre WNG-013-R/L at |y| 60, fin node FIN-005-R/L) with the fin-node in-plane plates FIN-009 under the skin, the cove CF strip and the glass skin (ply 1 + plies 2-3 over |y| 52..400) wet-laid on it (T-070, T-077 p8 / D-226; the packing-tape skin, hinge tape and bulkhead tape laps are not drawn)',
     ['WNG-001', 'WNG-011', 'WNG-012', 'WNG-014-R', 'WNG-014-L', 'WNG-013-R', 'WNG-013-L', 'FIN-005-R', 'FIN-005-L', 'FIN-009-R', 'FIN-009-L'], None, 0, 0),
    # ---- D-202 bench build of the cage frame (swept in the bench run, see BENCH; unit vectors from the CAD: u_A = (0, cos 34.38, sin 34.38) along tube A toward UR, u_B = (0, cos 34.38, -sin 34.38) along tube B toward LR)
    ('B0a', 'Bench: cut the two arm tubes (552.4 mm of 12x10), the bridge (117.5 mm, D-206 / T-077 p8, from the 16x14 fin-tube offcut) and the two struts (291.2 mm of 8x6) from the carbon stock; sand the ends square', [], None, 0, 0),
    ('B0b', 'Bench: the machined hub stands on the bench, aft face down', ['CGE-001'], None, 0, 0),
    ('B0c', 'Arm tube B slid through its sleeve and the centre block (from the LL side, along its axis)', ['CGE-002-B'], (0, 0.8253073, -0.5646839), 330, 15),
    ('B0d', 'Two 3 mm pins (LR, UL) pushed in along x from the nose side through the block access holes, the sleeve and tube B', ['CGE-010-LR', 'CGE-010-UL'], (1, 0, 0), 30, 3),
    ('B0e', 'Arm tube A slid through its sleeve and the centre block (from the LL side, along its axis)', ['CGE-002-A'], (0, 0.8253073, 0.5646839), 330, 15),
    ('B0f', 'The crossing pin and the two tube A pins (UR, LL) pushed in along x from the nose side', ['CGE-010-C', 'CGE-010-UR', 'CGE-010-LL'], (1, 0, 0), 40, 4),
    ('B0g1', 'Doubler UR slid over the tube A end (UR side) into the sleeve counterbore', ['CGE-009-UR'], (0, -0.8253073, -0.5646839), 260, 5),
    ('B0g2', 'Doubler LL slid over the tube A end (LL side) into the sleeve counterbore', ['CGE-009-LL'], (0, 0.8253073, 0.5646839), 260, 5),
    ('B0g3', 'Doubler LR slid over the tube B end (LR side) into the sleeve counterbore', ['CGE-009-LR'], (0, -0.8253073, 0.5646839), 260, 5),
    ('B0g4', 'Doubler UL slid over the tube B end (UL side) into the sleeve counterbore', ['CGE-009-UL'], (0, 0.8253073, -0.5646839), 260, 5),
    ('B0h', 'Bridge tube pushed forward into the hub bore from aft, seated on the conical floor', ['CGE-004'], (-1, 0, 0), 130, 10),
    ('B0i1', 'Motor cup UR slid onto the tube A end', ['CGE-003-UR'], (0, -0.8253073, -0.5646839), 60, 5),
    ('B0i2', 'Motor cup LL slid onto the tube A end', ['CGE-003-LL'], (0, 0.8253073, 0.5646839), 60, 5),
    ('B0i3', 'Motor cup LR slid onto the tube B end', ['CGE-003-LR'], (0, -0.8253073, 0.5646839), 60, 5),
    ('B0i4', 'Motor cup UL slid onto the tube B end', ['CGE-003-UL'], (0, 0.8253073, -0.5646839), 60, 5),
    ('B0j1', 'Right strut pushed into its hub socket along its own axis', ['CGE-005-R'], (-0.42766, -0.90394, 0), 40, 5),  # T-083b: axis for the 9 mm cage shift (T083_DX +3, STRUT_S x -74 mm). T-083: axis after the 15 mm cage shift (STRUT_S x -80 mm); was (-0.43605, -0.89992) for 12 mm  # D-224 p4: strut axis direction after the 12 mm cage shift (STRUT_S x -77 mm: atan2(262.1, 127) = 64.15 deg; was 66.3 deg, (-0.40179, -0.91573))
    ('B0j2', 'Left strut pushed into its hub socket along its own axis', ['CGE-005-L'], (-0.42766, 0.90394, 0), 40, 5),
    ('B0k', 'THREAD (bench, before the motors go on the cups): feed the three 20 AWG leads of each motor (100 mm X2216 stock + extension, EST) from the cup side through the 4.8 mm lead hole, the collar and the tube bore to the 4.8 mm exit hole at s +-18 mm; the free ends are laid flat along the tube until the hub conduits are on (B2b1-B2b4); then screw the motors on (B1)', [], None, 0, 0),
    ('B1', 'Cage unit (hub, arms, cups, bridge with the machined centre node CGE-006 bonded on it, struts, strut clamps, motors, props) built on the bench, docked '
           'from below BEFORE the spar (T-077 p8, D-226: the centre node sleeve is a closed bore): sleeve, socket boss and end flanges rise into their open-below core channels, the flanges beside the centre bulkheads', CAGE, (0, 0, 1), 30, 3),
    ('A2', 'Spar through the core bore from the right tip (T-077 p8: after the cage dock, through the fin-node and centre bulkhead holes, the strut clamps and the centre node sleeve)', ['WNG-002'], (0, -1, 0), 700, 100),
    ('A3', 'Centre plug up the bore', ['WNG-003-C'], (0, -1, 0), 600, 100),
    ('A4', 'Right plugs up the bore', ['WNG-004-R', 'WNG-005-R'], (0, -1, 0), 600, 100),
    ('A5', 'Left plugs up the bore from the left tip', ['WNG-004-L', 'WNG-005-L'], (0, 1, 0), 600, 100),
    ('B2a', 'D-199: phase-lead raceways R and L lowered from above into their foam grooves (through the slots in the hub pad flange), before the tray', ['HRN-003-R', 'HRN-003-L'], (0, 0, -1), 30, 3),
    ('B2b1', 'D-202: hub conduit UR lowered onto its sleeve and the raceway window (along the tube t axis, toward the tube)', ['HRN-004-UR'], (0, 0.5646839, -0.8253073), 40, 4),
    ('B2b2', 'D-202: hub conduit UL lowered onto its sleeve and the raceway window', ['HRN-004-UL'], (0, -0.5646839, -0.8253073), 40, 4),
    ('B2b3', 'D-202: hub conduit LR raised onto its sleeve and the raceway window (from below)', ['HRN-004-LR'], (0, 0.5646839, 0.8253073), 40, 4),
    ('B2b4', 'D-202: hub conduit LL raised onto its sleeve and the raceway window (from below)', ['HRN-004-LL'], (0, -0.5646839, 0.8253073), 40, 4),
    ('B2c', 'THREAD: feed the free ends of the 12 phase strands (B0) through their hub conduit, the raceway and the foam ditch (fish thread from the ditch end); the free ends stay out at x 29 mm for the ESC pads', [], None, 0, 0),
    ('B3', 'Pack tray lowered from above into the core tray slot, bonded to the hub aft face', ['CGE-008'], (0, 0, -1), 30, 3),
    ('B4', 'Hinge damper units (stator with rotor in its annulus, silicone fluid filled) into the core notches at the elevon tips from aft, before the ribs; the notch is open aft', ['WNG-009-R', 'WNG-010-R', 'WNG-009-L', 'WNG-010-L'], (-1, 0, 0), 30, 5),
    ('C1', 'Ribs (25x23, T-077 p8) in from aft between the fin-node bulkheads, through the plate notches; flox fillets, then the 4-ply rib straps over the rib top and bottom (straps not drawn)', ['FIN-002-R', 'FIN-002-L'], (-1, 0, 0), 300, 60),
    ('C1a', 'Upper rib fairings (half-round blisters over the rib and strap) lowered onto the skin from above, bonded', ['FIN-006-R', 'FIN-006-L'], (0, 0, -1), 15, 3),
    ('C1b', 'Lower rib fairings (half-round blisters under the rib, T-077 p8) raised onto the lower skin from below, bonded', ['FIN-010-R', 'FIN-010-L'], (0, 0, 1), 15, 3),
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
    ('D3', 'Horns on the elevons: each printed horn rib pushed down into its slot through the elevon, bonded (D-212 rev 3)', ['MEC-004-R', 'MEC-004-L'], (0, 0, -1), 15, 5),
    ('D4', 'Pushrods into arm hole (Z-bend) and over the horn blade (clevis cheeks straddle it; pin follows in D5)', ['MEC-003-R', 'MEC-003-L'], (0, 0, -1), 10, 5),
    ('D2a', 'Z-bend keepers over the Z-bends, then the M2x8 arm screws through keeper and arm into the output shafts (D-212 rev 3; was M2x6 before D4)', ['MEC-008-R', 'MEC-008-L', 'HWC-002-R', 'HWC-002-L'], (0, 0, -1), 10, 5),
    ('D5', 'Clevis pin R pressed in along y through the cheeks and the horn hole (from outboard)', ['MEC-005-R'], (0, -1, 0), 6, 1),
    ('D5b', 'Clevis pin L pressed in along y (from outboard)', ['MEC-005-L'], (0, 1, 0), 6, 1),
    ('E1', 'Pitot into its groove from the front (left wing, y -420; its attachment block runs in the nose channel)', ['AVN-006'], (1, 0, 0), 250, 50),
    ('D0', 'THREAD: each servo 3-wire lead is fed from the servo pocket along its foam groove (3 mm under the skin, aft of the spar) to the slit at x 64 mm / |y| 24 mm with a fish wire; the free end stays out of the slit for the FC pads', [], None, 0, 0),
    ('E2', 'R2 bosses and pads on the skin with the four M2 thin nuts already seated in the FC boss hex pockets (no plate, T-073 R2)', ['AVN-010', 'HWC-003'], (0, 0, -1), 20, 5),
    ('E3', 'ESC, foam-tape pads (hard mount), FC on the pads, RX, GPS on their pads; airspeed board into its pocket in the left wing tip', ['PRP-003', 'AVN-007', 'AVN-002', 'AVN-003', 'AVN-004', 'AVN-005'], (0, 0, -1), 30, 5),
    ('E3a', 'Four M2 x 25 screws down through the FC stack into the nuts', ['HWC-001'], (0, 0, -1), 20, 5),
    ('E3d', 'Pitot lines (FLEXIBLE silicone: no rigid insertion path, so this step checks the fitted position only, travel 0): each 39 mm line pushed on its probe barb, laid in the pocket over the spar and pushed on its board port; pocket taped', ['AVN-009-T', 'AVN-009-S'], None, 0, 0),
    ('E3b', 'LAY: solder the ESC signal ribbon to the FC, the servo leads to the FC pads S5 / S6, the RX CRSF lead, the GPS and airspeed leads (JST plugs on the sensor boards); the I2C and RX leads run inside the cover lane, then the RX antennas are taped in a 90 deg V on the plate and skin (T-022 Q1, Q4)', [], None, 0, 0, ['E-HRN-06', 'E-HRN-07', 'E-HRN-08', 'E-HRN-09', 'E-HRN-10', 'E-HRN-11']),
    ('E3c', 'Anti-slip pad stuck on the tray floor', ['PWR-003'], (0, 0, -1), 10, 2),
    ('E4', 'Pack into the tray', ['PWR-001'], (0, 0, -1), 30, 5),
    ('E4a', 'XT60 female with its tail mated to the pack lead XT60 male (plugs on from aft, taped on the skin; tail soldered to the ESC pads after)', ['HRN-002'], (-1, 0, 0), 15, 3),
    ('E4b', 'LAY: mate the pack XT60 male to the XT60 female (E4a) (done in E4a); the vendor pack power leads (E-HRN-13) and balance lead (E-HRN-14) come on the pack and are taped to the skin along their route, the balance plug on the pack top', [], None, 0, 0, ['E-HRN-01', 'E-HRN-13', 'E-HRN-14']),
    ('E5', 'Two pack straps (y +-35 mm), each passed round the tray plate front edge and aft end and closed over the pack (FLEXIBLE: no rigid insertion path exists, so this step checks the fitted position only, travel 0; the threading is by hand; D-224 rung 3a: the bridge tube and the hub collar are not enclosed)', ['PWR-002'], None, 0, 0),
    ('E6', 'LAY: solder the battery tail to the ESC BAT pads and the 4 x 3 phase leads (free ends from B0 / B2c: out of the foam ditch at x 29, straight up to z 36, aft over the FC, down to z 28 behind it under the cover roof) to the ESC motor pads; heat-shrink', [], None, 0, 0, ['E-HRN-12', 'E-HRN-02', 'E-HRN-03', 'E-HRN-04', 'E-HRN-05']),
    ('E7', 'Bay cover lowered over the FC and ESC onto the skin (the GPS lead and the battery tail drop into the bottom-open slots, the two antennas into the slots of the RX hood aft wall; the RX UART and I2C leads and the phase bundles are already inside), foam tape + two ties', ['AVN-008'], (0, 0, -1), 40, 4),
]
THREAD_BEFORE = {'B0k': 'B1', 'D0': 'E2', 'B2c': 'E2'}
# D-202 bench steps: swept in their own run (nothing of the wing placed), their parts are placed in the main run by B1 (the dock of the finished frame)
BENCH = ('B0b', 'B0c', 'B0d', 'B0e', 'B0f', 'B0g1', 'B0g2', 'B0g3', 'B0g4', 'B0h', 'B0i1', 'B0i2', 'B0i3', 'B0i4', 'B0j1', 'B0j2')
BENCH_START = 'B0b'                          # the hub is the first part of the frame: it rests on the bench (like the wing core in A1), so it has no earlier part to bond to

