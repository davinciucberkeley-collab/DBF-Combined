"""assembly_plan.py - the K09-L build ORDER as data: BUILD-GUIDE.md step by step, plus the few motions that need a
special case. Pure Python (no bpy); read by assembly_check.py (plans and checks the motions) and render_build.py
(animates the checked plan).

What is data here and what is derived:
  * STEPS     the order. One row per numbered BUILD-GUIDE.md step that puts something on the aircraft (stages 2-11),
              with a one-line caption from that step and the part / wire globs it places, in the order the guide
              gives. Parts the steps do not name are placed in a last catch-all step and listed in the check report.
  * motion kind of each part, derived from repo data (interfaces/interfaces.json part name and material):
              'lay'    tape and labels (material or name says tape / label): laid in place, tested where it lies
              'fill'   wet epoxy beads and fillets (material says epoxy): applied in place, tested where it lies
              'screw'  screws, bolts and nuts (name): driven along their own axis while turning, swept
              'fixture' (OVERRIDES only) cut in place in its fixture: tested where it lies
              'built'  (OVERRIDES only) glued up from flat pieces: each body swept on its own path
              'hinge'  (OVERRIDES only) hooked under a lip and turned about its edge: a rotational sweep
              'slide'  every other rigid part: brought in along an insertion direction found by assembly_check.py
                       from the geometry (bore / pin / tube axes, prism extrusion axes, the normal of the face it
                       mounts on), then checked as a swept path
              'wire'   every routed wire: laid along its route, tested where it lies
  * OVERRIDES the parts that truly need something else (a fixture, a real non-straight motion, a preferred
              direction), one row each, with the BUILD-GUIDE step that says so. No row exempts a pair of parts.
  * ELASTIC   the only interference accepted: a named flexing body riding over a named body, up to the deflection
              its strain allowable gives.

Item grammar in STEPS:
  'GLOB'                 place the matching parts (fnmatch on part ids), in the order listed
  'bench:NAME GLOB|SEL'  as below, only the bodies whose name matches SEL (fnmatch; '!SEL' = all but those): a part
                         glued up in more than one go, another part fitted between (the pod box round the handle)
  'bench:NAME GLOB'      assemble the matching parts on the bench, off the aircraft, as group NAME ('<x>' in NAME is
                         replaced by the part's station / side suffix, so each station gets its own group)
  'install:NAME'         move every bench group whose name starts with NAME onto the aircraft as one rigid body
  'wire:GLOB'            lay the matching wire edges (E-HRN-..)
  'park:NAME'            PARK[NAME]: slide the placed members by move_mm (a checked sweep) and leave them there; parts
                         matching its 'carry' globs placed while parked are planned and placed in the parked frame
  'unpark:NAME'          slide the parked members and what they carry back by -move_mm (a checked sweep) to their seats
  'tails:GLOB'            lay the held runs of the matching wires whose loose end's part is now on: a lead laid while
                         its end part is not yet on is laid only up to its first in-line connector (JR pair, sleeve);
                         the run beyond it waits coiled off the aircraft and is laid here (BUILD-GUIDE 9.4 "lead it
                         into its contact of the JR pair"; 7.3-7.4 the servo lead)
  'swing:te-up'          swing the elevon panel groups to the joint limit that lifts the trailing edge and back
                         (the hinge-tape step: lower strip laid with the panel full TE-up; pose from the collision
                         job, the same joints collide.py sweeps)
"""
import fnmatch
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(HERE))

# (stage, step, caption from BUILD-GUIDE.md, items). Five places differ from the guide's order because the CAD says so
# (assembly_check.py found the guide's order blocked): station collars (guide 4.5) go on before the edge strips (4.4),
# whose ends sit in the collar tails; the pitot socket and the carry handle (guide 5.2) go into the pod box on the bench
# (5.1) before the pod is bonded into the recess; the XT30U pairs (guide 6.2) go on the tray before the power frame
# covers them; the servo frames (guide 7.4) are bonded before the servo leads and the skin (the lead runs under the
# frame rim, the tape doubler over its flange). Listed in build/ASSEMBLY-CHECK.md.
# (stage, step, caption from BUILD-GUIDE.md, items). Stage titles stay those of render_build.STAGES (the website and
# the build guide link one clip per stage).
STEPS = [
    (2, '2.1', 'Hot-wire the core blank (elevon strip included); cut the pockets, grooves and recess in its lower bed',
     ['WNG-001', 'WNG-011-*', 'WNG-012-*']),
    (2, '2.3', 'Push the PETG plugs into the spar to the dowel marks, the inboard (anchor) plugs first',
     ['bench:spar WNG-002', 'bench:spar WNG-005-*', 'bench:spar WNG-004-*']),
    (2, '2.4', 'Bond both through-core blocks to the spar in the clocking jig',
     ['bench:spar FIN-004-*']),
    (2, '2.5', 'Bond spar and blocks up the slot into the core; re-bond the slot strip as the cap; fill the lip beads',
     ['install:spar', 'WNG-008', 'WNG-006-*']),
    (3, '3.1', 'Route the torque-tube grooves, then cut the four panels free and slide them aft in the bed',
     ['park:elevons']),
    (3, '3.3', 'Bond the CF torque tubes flush in their grooves',
     ['MEC-009-*']),
    (4, '4.2', 'Plug the motor tubes, then slide them through the bosses and blocks',
     ['bench:tube-<x> FIN-002-*', 'bench:tube-<x> FIN-006-*', 'install:tube']),
    (4, '4.3', 'Bond the half-fin roots in the block slots; run the cove fillets',
     ['FIN-001-*']),
    (4, '4.5a', 'Brace into its anchor and collar ear on the bench; collar down the tube, anchor into its pocket',
     ['bench:brace-<x> FIN-010-*', 'bench:brace-<x> FIN-009-*', 'bench:brace-<x> FIN-008-*', 'install:brace']),
    (4, '4.4', 'Edge strips on both fin faces, ends into the collar tails; CF pins through strip-board-strip',
     ['FIN-011-*', 'FIN-012-*']),
    (4, '4.5', 'ESC pads on the fin faces',
     ['FIN-007-*']),
    (5, '5.1', 'Pod box on the bench: tray, pitot socket, board walls glued round them piece by piece, handle, inserts',
     ['bench:pod POD-002', 'bench:pod POD-006', 'bench:pod POD-001|!fb aft deck', 'bench:pod POD-007',
      'bench:pod POD-001|fb aft deck', 'bench:pod PWR-107']),
    (5, '5.2', 'Bond the pod into the recess; thread the straps under the tray; GPS mast and its cross-screw',
     ['install:pod', 'POD-004', 'POD-005', 'POD-011', 'POD-012']),
    (5, '5.3', 'XT30U pairs, airspeed sensor and RX on the tray; bus board; frame on its spacers, washers, screws; power board on its foam pad; AS150U',
     ['HRN-113-*', 'AVN-004', 'AVN-003', 'PWR-102', 'PWR-004', 'PWR-006', 'PWR-103', 'PWR-101', 'PWR-003', 'PWR-002',
      'wire:E-HRN-11', 'wire:E-HRN-12']),
    (6, '6.2', 'Strap the ESCs on their pads; caps, XT30U pairs and heat-shrink on the soldered leads',
     ['PRP-002-*', 'PWR-008-*', 'HRN-110-*', 'wire:E-HRN-13', 'wire:E-HRN-14', 'wire:E-HRN-15', 'wire:E-HRN-16',
      'wire:E-HRN-34', 'wire:E-HRN-35', 'wire:E-HRN-36', 'wire:E-HRN-37', 'HRN-107-*-P1',
      'HRN-107-*-P2']),
    (6, '6.3', 'Bond the servo frames in their pockets now: the servo lead runs under the frame rim',
     ['MEC-008-*']),
    (6, '6.4', 'DShot and servo leads in the grooves; JR pairs in the recess and on the pod tie bar',
     ['wire:E-HRN-24', 'wire:E-HRN-25', 'wire:E-HRN-26', 'wire:E-HRN-27', 'wire:E-HRN-28', 'wire:E-HRN-29',
      'HRN-107-*-S', 'HRN-105-*']),
    (6, '6.5', 'Skin the wing: lower, upper, then the LE strip; slit the tape round each lead',
     ['WNG-003', 'WNG-020']),
    (6, '6.6', 'Bond a strap eye round the outboard face of each bore boss (D-89c)',
     ['FIN-013-*']),
    (7, '7.1', 'Panels with their tubes slid back against the core; hinge tape: top strip at neutral, lower strip full TE-up',
     ['unpark:elevons', 'MEC-010-*', 'swing:te-up']),
    (7, '7.2', 'Horns on the torque tubes and the inter-panel rod',
     ['MEC-004-*', 'MEC-006-*', 'MEC-005-*', 'MEC-013-*']),
    (7, '7.3', 'Bench-prep each servo at 1500 us: arm on the spline, arm screw',
     ['bench:servo-<x> MEC-001-*', 'bench:servo-<x> MEC-002-*', 'bench:servo-<x> MEC-012-*']),
    (7, '7.4', 'Install the servo in its frame, fit the cover and its screws',
     ['install:servo', 'tails:E-HRN-2[89]', 'MEC-007-*', 'MEC-011-*']),
    (7, '7.5', 'Pushrod and clevis at neutral',
     ['MEC-003-*']),
    (8, '8.3', 'Motor on its mount plate on the bench: four screws through the drilled plate',
     ['bench:motor-<x> FIN-003-*', 'bench:motor-<x> PRP-001-*', 'bench:motor-<x> PRP-005-*']),
    (8, '8.4', 'Mount down the tube onto the station collar; washers, pinch bolt and nyloc',
     ['install:motor', 'FIN-103-*', 'FIN-101-*', 'FIN-102-*']),
    (8, '8.5', 'Phase leads off the ESC, up the cheek into the motor; sleeves on the splices',
     ['wire:E-HRN-17', 'wire:E-HRN-18', 'wire:E-HRN-19', 'wire:E-HRN-20', 'HRN-107-*-PH']),
    (8, '8.6', 'Prop adapter and its screws, balanced prop, washer and nut',
     ['PRP-004-*', 'PRP-006-*', 'PRP-003-*', 'PRP-008-*', 'PRP-007-*']),
    (9, '9.1', 'FC on its gel cubes with the microSD in',
     ['AVN-006', 'bench:fc AVN-001', 'bench:fc AVN-007', 'install:fc']),
    (9, '9.2', 'GPS on the mast pad',
     ['AVN-002']),
    (9, '9.3', 'Pitot boom into its keyed socket',
     ['AVN-005']),
    (9, '9.4', 'Connect power-board ribbon, GPS, RX and airspeed leads to the FC',
     ['tails:E-HRN-*', 'wire:E-HRN-23', 'wire:E-HRN-30', 'wire:E-HRN-31', 'wire:E-HRN-32', 'HRN-107-I2C',
      'HRN-107-RX']),
    (10, '10.4', 'Bond the shoes on the fin tips; inserts by colour; push on the corner caps',
     ['GER-001-*', 'bench:insert-<x> GER-002-*', 'bench:insert-<x> GER-003-*', 'bench:insert-<x> GER-008-*',
      'bench:insert-<x> GER-004-*', 'install:insert', 'GER-007-*']),
    (11, '11.1', 'Pack in with its spacer, crush block and spreader; strap it; mate the AS150U; hatch on',
     ['POD-008', 'POD-009', 'POD-010', 'PWR-001', 'wrap:POD-004', 'HRN-107-PACK', 'wire:E-HRN-10', 'POD-003']),
]

# Where this order differs from BUILD-GUIDE.md, and why (each found by assembly_check.py on the guide's order).
DEVIATIONS = [
    ('4.4 / 4.5', 'Station collars FIN-008 go on before the edge strips FIN-011, carrying the brace FIN-009 and its '
     'anchor FIN-010 (bench sub-assembly)',
     'the strip ends sit in the collar tail slot (seats.json FIN-008/FIN-011): with the strips on, the collar cannot '
     'slide down the tube; the brace ends sit 10 mm in blind slots in the anchor and the ear, so the brace cannot go '
     'in once both are fixed (bowing it in strains the CF past its limit: report, BOW)'),
    ('5.1 / 5.2', 'Pitot socket POD-006 and carry handle POD-007 go into the pod box on the bench',
     'with the pod in the recess, neither can reach its seat (handle brackets wrap the pod walls)'),
    ('5.3', 'Bus board PWR-004 goes in before the power frame PWR-006 (not after the screws)',
     'the frame cradle covers the bus-board seat: the board meets the frame 0.86 mm deep 12 mm out (2026-11-13 run)'),
    ('7.2', 'Outboard horn MEC-006 before the inter-panel rod MEC-005',
     'the rod runs through both horn bosses: with the rod in, the outboard horn cannot reach its slot'),
    ('5.3 / 6.2', 'XT30U pairs HRN-113 go on the tray before the power frame PWR-006',
     'the frame cradle floor lies over them'),
    ('5.3 / 9.1', 'Airspeed sensor AVN-004 and receiver AVN-003 go on the tray before the power frame',
     'both sit under the power frame deck and the bus carrier'),
    ('6.4 / 7.4', 'Servo frames MEC-008 are bonded before the servo leads and the skin',
     'the servo lead runs under the frame rim and the tape doubler over its flange'),
]

# Special cases. key: part glob (first match wins). No row exempts a pair of parts from the swept-path test: every
# row names a real motion the checker carries out and tests. Fields:
#   kind      'fixture'  cut in place in its fixture (the core in its hot-wire bed, the panels cut free of it): no
#                        motion; checked to appear clear of everything already placed (assembly_check.in_place)
#             'lay'      flexible strap / tape laid in place: the same in-place test
#             'built'    glued up from flat pieces: each CAD body is its own rigid motion, planned and swept
#             'hinge'    hooked under a lip and turned down about the lip's edge (row 'hinge'): a rotational sweep
#   fixture   what holds the part when nothing already placed touches it (a jig, a bed, the bench)
#   dirs      preferred removal directions to try first (world unit vectors, aircraft frame x aft, y right, z up);
#             the part arrives moving the opposite way
#   why       the source (BUILD-GUIDE step) for the row
OVERRIDES = [
    ('WNG-001', dict(kind='fixture', fixture='lower hot-wire foam bed',
                     why='BUILD-GUIDE 2.1-2.2: the core is hot-wired and slotted in its lower bed and stays in it')),
    ('WNG-011-*', dict(kind='fixture', fixture='lower hot-wire foam bed (the TE strip of the core blank)',
                       why='BUILD-GUIDE 2.1, 3.1: the panels are the trailing-edge strip of the same hot-wired blank as '
                           'the core; laid in with it, cut free at 3.1 (PARK elevons)')),
    ('WNG-012-*', dict(kind='fixture', fixture='lower hot-wire foam bed (the TE strip of the core blank)',
                       why='BUILD-GUIDE 2.1, 3.1: the panels are the trailing-edge strip of the same hot-wired blank as '
                           'the core; laid in with it, cut free at 3.1 (PARK elevons)')),
    ('WNG-002', dict(fixture='clocking jig on the bench', dirs=[(0, 0, -1)],
                     why='BUILD-GUIDE 2.2: the spar slot is cut from below (WNG-001 slot, D-89c); 2.4 blocks bonded '
                         'to the spar in the jig; 2.5 spar pushed up the slot')),
    ('WNG-008', dict(dirs=[(0, 0, -1)], why='BUILD-GUIDE 2.5: the slot strip is re-bonded under the spar from below')),
    ('POD-001', dict(kind='built', why='BUILD-GUIDE 5.1 "stop T, tray, walls, fillets": the foam-board box is '
                                       'glued up from flat pieces round the tray, not slid on as one piece')),
    ('POD-006', dict(fixture='held in the nose opening while the board box is glued round it',
                     why='BUILD-GUIDE 5.1: the pod box is built round its inserts')),
    ('POD-003', dict(kind='hinge',
                     hinge=dict(body='petg hatch tongue', host='POD-001', host_body='petg nose lip',
                                angles=[60, 45, 75, 90, 30], lift_mm=40.0, clear_mm=2.0),
                     why='interfaces E-POD-03 "tongue under the nose lip + hook-and-loop tab": the tongue is slid '
                         'under the nose lip with the hatch open, then the hatch turned down about the lip edge')),
    ('POD-004', dict(kind='lay', hold=dict(above='POD-002', bodies='strap', wrap_step='11.1'),
                     why='hook-and-loop straps (interfaces E-POD-04): each passes down a slot, under the tray in the '
                         'floor groove and up the other slot (laid in place, with the EVA pads); the run above the '
                         'tray is left open and wrapped over the pack at BUILD-GUIDE 11.1 "strap it"')),
    ('HRN-113-*', dict(fixture='cable tie in its lane (interfaces E-HRN-38..41 CT-TIE; harness BUILD step 8 '
                               '"tie the body in its lane")',
                       why='XT30U mated pair: no rigid seat; tied in its lane on the tray')),
    ('MEC-003-*', dict(kind='hinge', hinge=dict(pivot='axis', body='pushrod Z-bend leg', angles=[30, 60, 90, 15, 120],
                                                clear_mm=2.0),
                       why='BUILD-GUIDE 7.5 "pushrod and clevis at neutral": the Z-bend leg is threaded through the '
                           'servo-arm hole with the rod swung clear, then the rod is swung about the leg onto the horn '
                           '(the clevis closing round the horn arm)')),
]

# Parts moved away from their seat for a while and brought back, both moves checked as sweeps (STEPS 'park:' and
# 'unpark:'). While parked their bodies are obstacles at the parked pose, so nothing placed meanwhile may pass there.
PARK = {
    'elevons': dict(members=['WNG-011-*', 'WNG-012-*'], carry=['MEC-009-*'], move_mm=(10.0, 0.0, 0.0),
                    why='BUILD-GUIDE 3.1: the panels are cut free of the core blank along the kerf and slid 10 mm aft in '
                        'the bed (EST: enough to clear the kerf and handle them); the torque tubes are bonded into them '
                        'there (3.3); at 7.1 panels and tubes slide forward back against the core before the hinge '
                        'tape'),
}

# Elastic deflection during a motion: the only interference the check accepts, and only between the named bodies, up
# to the deflection the strain allowable gives (assembly_check.elastic_rows: cantilever tip deflection d, root strain
# eps = 3 t d / (2 L^2), d_allow = 2 eps_allow L^2 / (3 t)), and never past cap_mm (the geometric hook height). Every
# use is reported with its measured deflection and strain.
ELASTIC = [
    dict(id='GER-002 snap finger', mover='GER-002-*', mover_body='hook *', blocker='GER-001-*',
         blocker_body='sleeve wall *', L_mm=6.5, t_mm=0.8, cap_mm=0.6, eps_allow=0.035,
         why='BUILD-GUIDE 10.4 "fit inserts by colour": the two ramped hooks ride over the sleeve wall on the way in '
             'and click into the side windows (interfaces E-GER-05..08)',
         source='finger 6.5 x 5 x 0.8 mm, hook 0.6 mm: interfaces E-GER-05 retention (CR-C6-12); PETG yield strain '
                '3.5 % (lowest of the Prusament PETG TDS values found: V0 sheet Aug 2023 3.5-3.7 %, PETG v1.1 Feb '
                '2022 5.1 %; https://cdn.shopify.com/s/files/1/1745/6181/files/prusament-petg-v0-technical-data-sheet.pdf, '
                'checked 2026-11-13); EST'),
    dict(id='MEC-003 clevis jaw', mover='MEC-003-*', mover_body='clevis', blocker='MEC-004-*',
         blocker_body='horn arm', L_mm=12.5, t_mm=1.2, cap_mm=0.5, eps_allow=0.0108,
         why='BUILD-GUIDE 7.5: the rod swung about its Z-bend leg onto the horn; the clevis jaws spring over the horn arm',
         source='jaw length 12.5 mm = clevis x 235.6-248.1 mm, jaw 1.2 mm = (4.8 mm clevis - 2.4 mm horn arm) / 2: '
                'CAD MEC-003 clevis and MEC-004 horn arm; steel clevis taken as music wire ASTM A228, proof 2050 MPa / '
                'E 190 GPa = 1.08 % (https://www.makeitfrom.com/material-properties/ASTM-A228-SWP-A-K08500-Music-Wire, '
                'checked 2026-11-13); EST'),
    dict(id='MEC-010 hinge film', mover='WNG-01[12]-*', mover_body='xps elevon', blocker='MEC-010-*',
         blocker_body='hinge tape strip (on the core)', L_mm=11.9, t_mm=0.10, cap_mm=0.2, eps_allow=0.02,
         why='BUILD-GUIDE 7.1: on the TE-up swing the panel nose presses the hinge film where it leaves the core edge',
         source='film 0.10 mm thick: CAD MEC-010 strip section; free span 11.9 mm wide across the hinge gap: this check '
                '(swing tape split, x 250.2-262.1 mm); BOPP packing tape (interfaces MEC-010): elongation at break '
                '140 % MD (Transcendia HT2-F BOPP film data sheet, https://www.transcendia.com/sites/default/files/'
                '2025-01/ht2-f_bopp_film_datasheet_01032025.pdf, checked 2026-11-13); elastic limit taken as 2 %, EST'),
    dict(id='POD-003 hatch end-on (lip)', model='axial', mover='POD-003', mover_body='fb hatch', blocker='POD-001',
         blocker_body='petg nose lip', L_mm=195.2, cap_mm=0.2, eps_allow=0.01,
         why='the hatch fits between the nose lip and the aft deck with no clearance in CAD: closing about the lip '
             'edge presses its foam-board front edge against the lip',
         source='hatch length 195.2 mm: CAD POD-003 fb hatch x -129.2..66.0 (pod_data.py); foam-board elastic limit '
                'EST 1 % (XPS of the FOAMULAR family: 40 psi strength over 1800 psi modulus = 2.2 %, FOAMULAR '
                '400/600/1000 data sheet, https://cemstonesupply.com/wp-content/uploads/2020/05/'
                'FOAMULAR-400-600-1000-XPS-Product-Data-Sheet.pdf, checked 2026-11-13; halved); EST'),
    dict(id='POD-003 hatch end-on (deck)', model='axial', mover='POD-003', mover_body='fb hatch', blocker='POD-001',
         blocker_body='fb aft deck', L_mm=195.2, cap_mm=0.2, eps_allow=0.01,
         why='as above, the aft edge against the aft deck edge',
         source='as POD-003 hatch end-on (lip); EST'),
]

# The brace (FIN-009) is NOT bowed in: both ends sit 10 mm in blind slots cut to its own section (interfaces E-FIN-37..44)
# and bowing a 10 x 2 CF strip enough to shorten its chord by 10 mm strains it past its limit (assembly_check reports the
# number: BOW). It goes on the bench into the anchor and the collar ear, each slid along the brace axis, and the three
# go on as one rigid sub-assembly (STEPS 4.5a).
BOW = dict(part='FIN-009-UR', embed_mm=10.0, clear_mm=0.5, t_mm=2.0, eps_ult=0.013,
           source='brace ends 10 mm in each slot: interfaces E-FIN-37..44; CF strip 10 x 2 (parts FIN-009); '
                  'pultruded carbon ultimate tensile strain 1.30 % (TAP Plastics pultruded carbon rods & tubes '
                  'sheet, https://www.tapplastics.com/image/pdf/Pultruded_Carbon_Rods__Tubes.pdf, checked '
                  '2026-11-13); EST')


# Open design blockers the BUILD-GUIDE already names, which no motion can route round until the CAD changes. A swept-path
# hit matching a row (moving part glob, blocking part glob) is still reported, loudly, in its own section with the
# finding; it does not count as an unexplained violation. Remove the row when the fix lands: the check then shows
# whether the fix works.
KNOWN = [
]


# Reading of each remaining violation from the check's attempt log (assembly_check.json 'attempts'): what blocks every
# direction tried. A diagnosis to start from, not a verified cause; the fix belongs in the CAD (this tool never moves
# a part to make a path pass).
FINDINGS = [
    # empty: the five blockers of 2026-11-13 (servo and cover through the tape, cover in the core, pushrod in the arm
    # plane, pod aft deck, hatch tab under the grip) are fixed in CAD by D-139...D-143 (review/CDR-2026-11-13/fixes/
    # ASSEMBLY.md). Add a row here with its reading when a run reports a new violation.
]

# Placements that touch nothing placed: why, when the data does not say.
SUPPORT_NOTES = [
    ('AVN-002', 'GPS on the mast pad: gap to the pad over 0.6 mm in CAD (pad tape not modelled)'),
]


def note(table, pid):
    for g, text in table:
        if fnmatch.fnmatch(pid, g):
            return text
    return None


def known(mover, blocker):
    for mg, bg, fid, why in KNOWN:
        if fnmatch.fnmatch(mover or '', mg) and fnmatch.fnmatch(blocker or '', bg):
            return {'finding': fid, 'why': why}
    return None


def bonded_pairs():
    """Pairs of part ids joined by an interfaces.json edge (bond, tape, pad, fastener): a bond line may leave a gap."""
    return {frozenset((e['part_a'], e['part_b'])) for e in _load('interfaces.json')['edges']}


FOAM_TAPE = re.compile(r'(\d+(?:\.\d+)?) mm foam tape', re.I)


def bond_gaps():
    """{pair: allowed gap mm} for interfaces.json edges whose notes state a foam-tape layer ('on 1 mm foam tape'): the
    tape fills that gap (BUILD data; the tape itself is not modelled)."""
    out = {}
    for e in _load('interfaces.json')['edges']:
        m = FOAM_TAPE.search(e.get('notes') or '')
        if m:
            out[frozenset((e['part_a'], e['part_b']))] = float(m.group(1)) + 0.1
    return out


def override(pid):
    for g, row in OVERRIDES:
        if fnmatch.fnmatch(pid, g):
            return row
    return {}


def _load(name):
    with open(os.path.join(REDESIGN, 'interfaces', name), encoding='utf-8') as f:
        return json.load(f)


def part_info():
    """Part id -> interfaces.json part record (name, material, ...)."""
    return {p['id']: p for p in _load('interfaces.json')['parts']}


SCREW_RE = re.compile(r'\b(screws?|bolts?|nuts?|nyloc)\b', re.I)


def kind_of(pid, info):
    """Motion kind from the part record (see module docstring); OVERRIDES win."""
    k = override(pid).get('kind')
    if k:
        return k
    p = info.get(pid, {})
    name, mat = (p.get('name') or '').lower(), (p.get('material') or '').lower()
    if 'tape' in mat or 'label' in mat:
        return 'lay'
    if 'epoxy' in mat:
        return 'fill'
    if SCREW_RE.search(name) and 'washer' not in name and 'spacer' not in name:
        return 'screw'
    return 'slide'


def base_id(pid):
    """'FIN-011-URO' -> 'FIN-011'; 'E-HRN-13' -> 'E-HRN'."""
    return '-'.join(pid.split('-')[:2])


def suffix(pid):
    return '-'.join(pid.split('-')[2:])


def sequence(part_ids, wire_ids):
    """Expand STEPS into an ordered action list. Each action:
        {'stage', 'step', 'caption', 'type': 'part'|'wire'|'bench'|'install'|'swing', 'id', 'group'}
    'bench' actions place one part into a bench group; 'install' moves one whole group ('id' = group name).
    Returns (actions, unplaced part ids appended to a catch-all step at the end)."""
    acts, used, groups, partial = [], set(), {}, set()
    for stage, step, cap, items in STEPS:
        for it in items:
            base = dict(stage=stage, step=step, caption=cap)
            if it.startswith('bench:'):
                name, glob = it[6:].split(' ', 1)
                glob, sel = glob.split('|', 1) if '|' in glob else (glob, None)
                for pid in sorted(p for p in part_ids if fnmatch.fnmatch(p, glob) and (p not in used or
                                                                                       (sel and p in partial))):
                    g = name.replace('<x>', suffix(pid))
                    if pid not in groups.get(g, []):
                        groups.setdefault(g, []).append(pid)
                    used.add(pid)
                    if sel:
                        partial.add(pid)
                    acts.append(dict(base, type='bench', id=pid, group=g, bodies=sel))
            elif it.startswith('install:'):
                name = it[8:]
                for g in sorted(groups):
                    if g == name or g.startswith(name + '-'):
                        if any(a['type'] == 'install' and a['id'] == g for a in acts):
                            continue
                        acts.append(dict(base, type='install', id=g, group=g, members=list(groups[g])))
            elif it.startswith('wire:'):
                for w in sorted(w for w in wire_ids if fnmatch.fnmatch(w, it[5:]) and w not in used):
                    used.add(w)
                    acts.append(dict(base, type='wire', id=w, group=None))
            elif it.startswith('wrap:'):
                acts.append(dict(base, type='wrap', id=it[5:], group=None))
            elif it.startswith(('park:', 'unpark:')):
                kind_, name = it.split(':', 1)
                acts.append(dict(base, type=kind_, id=name, group=None))
            elif it.startswith('tails:'):
                acts.append(dict(base, type='tails', id=it[6:], group=None))
            elif it.startswith('swing:'):
                acts.append(dict(base, type='swing', id=it[6:], group=None))
            else:
                for pid in sorted(p for p in part_ids if fnmatch.fnmatch(p, it) and p not in used):
                    used.add(pid)
                    acts.append(dict(base, type='part', id=pid, group=None))
    rest = sorted(p for p in part_ids if p not in used)
    for pid in rest:
        acts.append(dict(stage=STEPS[-1][0], step=STEPS[-1][1], caption='Parts no BUILD-GUIDE step names',
                         type='part', id=pid, group=None))
    rest_w = sorted(w for w in wire_ids if w not in used)
    for w in rest_w:
        acts.append(dict(stage=STEPS[-1][0], step=STEPS[-1][1], caption='Wires no BUILD-GUIDE step names',
                         type='wire', id=w, group=None))
    return acts, rest + rest_w
