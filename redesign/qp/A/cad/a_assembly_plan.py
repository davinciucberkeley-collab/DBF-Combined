"""a_assembly_plan.py - minimal build sequence of concept A as data. Each step: id, caption, parts placed together as one rigid
body, direction of the final motion INTO the seat (world vector), travel (mm) and sampling step (mm). a_assembly.py checks
(1) support: every placed part has a mechanical edge to something already placed or to a part of its own step,
(2) the swept path: the member bodies, moved from seat - dir * travel to the seat, never penetrate (> 0.05 mm) a part placed
earlier (cuts, bores and pockets count as empty), and (3) every electrical edge is laid after both end parts are on.
Not in the sequence: laid wires (checked in place by collide_a.py), tape skin, hinge tape, epoxy fillets (not drawn)."""
ST = ('UR', 'UL', 'LR', 'LL')
CAGE = (['CGE-00%d' % i for i in (1, 4, 6)] + ['CGE-002-' + s for s in ST] + ['CGE-003-' + s for s in ST] +
        ['CGE-005-R', 'CGE-005-L', 'CGE-007-R', 'CGE-007-L'] + ['PRP-001-' + s for s in ST] + ['PRP-002-' + s for s in ST])
# (id, caption, parts, dir, travel_mm, step_mm)
STEPS = [
    ('A1', 'Wing core on the bench (lower surface up)', ['WNG-001'], None, 0, 0),
    ('A2', 'Spar through the core bore from the right tip', ['WNG-002'], (0, -1, 0), 700, 100),
    ('A3', 'Centre plug up the bore', ['WNG-003-C'], (0, -1, 0), 600, 100),
    ('A4', 'Right plugs up the bore', ['WNG-004-R', 'WNG-005-R'], (0, -1, 0), 600, 100),
    ('A5', 'Left plugs up the bore from the left tip', ['WNG-004-L', 'WNG-005-L'], (0, 1, 0), 600, 100),
    ('B1', 'Cage unit (hub, arms, cups, bridge, struts, saddle, clips, motors, props) built on the bench, docked '
           'from below: clips snap on the spar', CAGE, (0, 0, 1), 30, 3),
    ('B2', 'Rib saddles snap on the spar from below', ['FIN-005-R', 'FIN-005-L'], (0, 0, 1), 30, 3),
    ('B3', 'Pack tray lowered from above into the core tray slot, bonded to the hub aft face', ['CGE-008'], (0, 0, -1), 30, 3),
    ('C1', 'Ribs in from aft into the saddle sockets', ['FIN-002-R', 'FIN-002-L'], (-1, 0, 0), 300, 60),
    ('C2', 'Elevons with their balance horns on from aft (horn and lead enter the core pocket; tape hinge after)', ['WNG-006-R', 'WNG-006-L', 'WNG-007-R', 'WNG-007-L'], (-1, 0, 0), 25, 5),
    ('C3', 'Fairing, right, from outboard', ['FIN-004-R'], (0, -1, 0), 40, 5),
    ('C4', 'Fairing, left, from outboard', ['FIN-004-L'], (0, 1, 0), 40, 5),
    ('C5', 'Root blocks onto the rib ends from aft', ['FIN-003-R', 'FIN-003-L'], (-1, 0, 0), 60, 5),
    ('C6', 'Fin tubes down through the blocks', ['FIN-001-R', 'FIN-001-L'], (0, 0, -1), 500, 100),
    ('C7', 'Upper shoes on the tube ends', ['GER-001-UR', 'GER-001-UL'], (0, 0, -1), 30, 5),
    ('C8', 'Lower shoes on the tube ends', ['GER-001-LR', 'GER-001-LL'], (0, 0, 1), 30, 5),
    ('C9', 'Foot pads on the shoe plates', ['GER-002-' + s for s in ST], (-1, 0, 0), 30, 5),
    ('D1', 'Servos into their pockets', ['MEC-001-R', 'MEC-001-L'], (0, 0, -1), 30, 5),
    ('D2', 'Servo arms on the splines', ['MEC-002-R', 'MEC-002-L'], (0, 0, -1), 15, 5),
    ('D3', 'Horns on the elevons', ['MEC-004-R', 'MEC-004-L'], (0, 0, -1), 15, 5),
    ('D4', 'Pushrods into arm and horn', ['MEC-003-R', 'MEC-003-L'], (0, 0, -1), 10, 5),
    ('E1', 'Pitot into its groove from the front', ['AVN-006'], (1, 0, 0), 250, 50),
    ('E2', 'Avionics plate on the skin', ['AVN-001'], (0, 0, -1), 20, 5),
    ('E3', 'ESC, foam-tape pads (hard mount), FC on the pads, RX, GPS, airspeed on the plate', ['PRP-003', 'AVN-007', 'AVN-002', 'AVN-003', 'AVN-004', 'AVN-005'], (0, 0, -1), 30, 5),
    ('E4', 'Pack into the tray', ['PWR-001'], (0, 0, -1), 30, 5),
]
