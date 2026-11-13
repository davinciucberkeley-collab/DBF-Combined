"""assembly_plan.py - the K09-L build ORDER as data: BUILD-GUIDE.md step by step, plus the few motions that need a
special case. Pure Python (no bpy); read by assembly_check.py (plans and checks the motions) and render_build.py
(animates the checked plan).

What is data here and what is derived:
  * STEPS     the order. One row per numbered BUILD-GUIDE.md step that puts something on the aircraft (stages 2-11),
              with a one-line caption from that step and the part / wire globs it places, in the order the guide
              gives. Parts the steps do not name are placed in a last catch-all step and listed in the check report.
  * motion kind of each part, derived from repo data (interfaces/interfaces.json part name and material):
              'lay'    tape and labels (material or name says tape / label): laid in strips onto what is under them
              'fill'   wet epoxy beads and fillets (material says epoxy): applied in place
              'screw'  screws, bolts and nuts (name): driven along their own axis while turning
              'clip'   (OVERRIDES only) sprung, bowed or hooked on, not a rigid motion: placed, support-checked
              'built'  (OVERRIDES only) glued up from flat pieces in place (the foam-board pod box)
              'slide'  every other rigid part: brought in along an insertion direction found by assembly_check.py
                       from the geometry (bore / pin / tube axes, prism extrusion axes, the normal of the face it
                       mounts on), then checked as a swept path
              'wire'   every routed wire: laid along its route from its supply end (part_a) to its load end (part_b)
  * OVERRIDES the parts that truly need something else (a fixture, a build-time cut, a preferred direction), one row
              each, with the BUILD-GUIDE step that says so. Keep every special case in this one table.

Item grammar in STEPS:
  'GLOB'                 place the matching parts (fnmatch on part ids), in the order listed
  'bench:NAME GLOB'      assemble the matching parts on the bench, off the aircraft, as group NAME ('<x>' in NAME is
                         replaced by the part's station / side suffix, so each station gets its own group)
  'install:NAME'         move every bench group whose name starts with NAME onto the aircraft as one rigid body
  'wire:GLOB'            lay the matching wire edges (E-HRN-..)
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
    (2, '2.1', 'Hot-wire the core; cut the pockets, grooves and recess with it in its lower bed',
     ['WNG-001']),
    (2, '2.3', 'Push the PETG plugs into the spar to the dowel marks, the inboard (anchor) plugs first',
     ['bench:spar WNG-002', 'bench:spar WNG-005-*', 'bench:spar WNG-004-*']),
    (2, '2.4', 'Bond both through-core blocks to the spar in the clocking jig',
     ['bench:spar FIN-004-*']),
    (2, '2.5', 'Bond spar and blocks into the core; fill the lip-bead chamfers',
     ['install:spar', 'WNG-006-*']),
    (3, '3.1', 'Route the torque-tube grooves, then cut the four panels free',
     ['WNG-011-*', 'WNG-012-*']),
    (3, '3.3', 'Bond the CF torque tubes flush in their grooves',
     ['MEC-009-*']),
    (4, '4.2', 'Plug the motor tubes, then slide them through the bosses and blocks',
     ['bench:tube-<x> FIN-002-*', 'bench:tube-<x> FIN-006-*', 'install:tube']),
    (4, '4.3', 'Bond the half-fin roots in the block slots; run the cove fillets',
     ['FIN-001-*']),
    (4, '4.5a', 'Station collars down the tubes first: the edge-strip ends sit in the collar tails',
     ['FIN-008-*']),
    (4, '4.4', 'Edge strips on both fin faces, ends into the collar tails; CF pins through strip-board-strip',
     ['FIN-011-*', 'FIN-012-*']),
    (4, '4.5', 'Brace anchors on the spar, braces into their slots, ESC pads',
     ['FIN-010-*', 'FIN-009-*', 'FIN-007-*']),
    (5, '5.1', 'Pod box on the bench: tray with its stops, board walls round it, straps, inserts, pitot socket, handle',
     ['bench:pod POD-002', 'bench:pod POD-001', 'bench:pod POD-004', 'bench:pod PWR-107', 'bench:pod POD-006',
      'bench:pod POD-007']),
    (5, '5.2', 'Lay the recess-step fillet, bond the pod into the recess; GPS mast and its cross-screw',
     ['install:pod', 'POD-005', 'POD-011', 'POD-012']),
    (5, '5.3', 'XT30U pairs, airspeed sensor and RX on the tray; power frame on spacers; power board on its washers, screwed down through it; bus board, AS150U',
     ['HRN-113-*', 'AVN-004', 'AVN-003', 'PWR-102', 'PWR-006', 'PWR-103', 'PWR-004', 'PWR-003', 'PWR-101', 'PWR-002', 'wire:E-HRN-11',
      'wire:E-HRN-12']),
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
    (7, '7.1', 'Hinge tape: top strip at neutral, lower strip with the panel full TE-up',
     ['MEC-010-*', 'swing:te-up']),
    (7, '7.2', 'Horns on the torque tubes and the inter-panel rod',
     ['MEC-004-*', 'MEC-005-*', 'MEC-006-*', 'MEC-013-*']),
    (7, '7.3', 'Bench-prep each servo at 1500 us: arm on the spline, arm screw',
     ['bench:servo-<x> MEC-001-*', 'bench:servo-<x> MEC-002-*', 'bench:servo-<x> MEC-012-*']),
    (7, '7.4', 'Install the servo in its frame, fit the cover and its screws',
     ['install:servo', 'MEC-007-*', 'MEC-011-*']),
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
     ['wire:E-HRN-23', 'wire:E-HRN-30', 'wire:E-HRN-31', 'wire:E-HRN-32']),
    (10, '10.4', 'Bond the shoes on the fin tips; inserts by colour; push on the corner caps',
     ['GER-001-*', 'bench:insert-<x> GER-002-*', 'bench:insert-<x> GER-003-*', 'bench:insert-<x> GER-008-*',
      'bench:insert-<x> GER-004-*', 'install:insert', 'GER-007-*']),
    (11, '11.1', 'Pack in with its spacer, crush block and spreader; strap it; mate the AS150U; hatch on',
     ['POD-008', 'POD-009', 'POD-010', 'PWR-001', 'HRN-107-PACK', 'wire:E-HRN-10', 'POD-003']),
]

# Where this order differs from BUILD-GUIDE.md, and why (each found by assembly_check.py on the guide's order).
DEVIATIONS = [
    ('4.4 / 4.5', 'Station collars FIN-008 go on before the edge strips FIN-011',
     'the strip ends sit in the collar tail slot (seats.json FIN-008/FIN-011): with the strips on, the collar cannot '
     'slide down the tube'),
    ('5.1 / 5.2', 'Pitot socket POD-006 and carry handle POD-007 go into the pod box on the bench',
     'with the pod in the recess, neither can reach its seat (handle brackets wrap the pod walls)'),
    ('5.3 / 6.2', 'XT30U pairs HRN-113 go on the tray before the power frame PWR-006',
     'the frame cradle floor lies over them'),
    ('5.3 / 9.1', 'Airspeed sensor AVN-004 and receiver AVN-003 go on the tray before the power frame',
     'both sit under the power frame deck and the bus carrier'),
    ('6.4 / 7.4', 'Servo frames MEC-008 are bonded before the servo leads and the skin',
     'the servo lead runs under the frame rim and the tape doubler over its flange'),
]

# Special cases. key: part glob (first match wins). Fields:
#   kind      force a motion kind ('fixture': no motion, the part is held by the named fixture)
#   fixture   what holds the part when nothing already placed touches it (a jig, a bed, the bench)
#   dirs      preferred removal directions to try first (world unit vectors, aircraft frame x aft, y right, z up);
#             the part arrives moving the opposite way
#   cut_by    {host part: why}: the host has material removed along this part's path at build time (a slot cut for
#             it and filled afterwards), so the pair is not tested during THIS part's motion
#   why       the source (BUILD-GUIDE step) for the row
OVERRIDES = [
    ('WNG-001', dict(kind='fixture', fixture='lower hot-wire foam bed',
                     why='BUILD-GUIDE 2.1-2.2: the core is cut and stays in its lower bed')),
    ('WNG-011-*', dict(kind='fixture', fixture='core foam bed (cut free of the core in place)',
                       why='BUILD-GUIDE 3.1: the panels are cut from the whole core')),
    ('WNG-012-*', dict(kind='fixture', fixture='core foam bed (cut free of the core in place)',
                       why='BUILD-GUIDE 3.1: the panels are cut from the whole core')),
    ('WNG-002', dict(fixture='clocking jig on the bench', dirs=[(0, 0, -1)],
                     cut_by={'WNG-001': 'spar slot cut from below with the core in its bed, filled with '
                                        'microballoon epoxy round the spar (BUILD-GUIDE 2.2, 2.5)'},
                     why='BUILD-GUIDE 2.2: "cut the spar slot from below"; 2.4 blocks bonded to the spar in the jig')),
    ('WNG-00[45]-*', dict(cut_by={'WNG-001': 'inside the spar: rides up the same slot (BUILD-GUIDE 2.2, 2.5)'},
                          why='BUILD-GUIDE 2.3: the plugs are inside the spar tube when it goes in')),
    ('POD-001', dict(kind='built', why='BUILD-GUIDE 5.1 "stop T, tray, walls, fillets": the foam-board box is '
                                       'glued up from flat pieces round the tray, not slid on as one piece')),
    ('POD-006', dict(fixture='held in the nose opening while the board box is glued round it',
                     why='BUILD-GUIDE 5.1: the pod box is built round its inserts')),
    ('POD-003', dict(kind='clip', why='BUILD-GUIDE 11 / pod BUILD: the hatch tongue is hooked under the nose lip '
                                      'and the hatch swung down onto its tab: a rotation, placed, not swept')),
    ('GER-002-*', dict(cut_by={'GER-001-*': 'ramped snap hooks of the insert deflect as it is pushed into the shoe '
                                            'sleeve (snap fit, BUILD-GUIDE 10.4 "fit inserts by colour")'},
                       why='BUILD-GUIDE 10.4: the insert snaps into the shoe')),
    ('E-HRN-2[4-9]', dict(flexible=True, why='DShot and servo leads (BUILD-GUIDE 6.4): laid in their grooves with the '
                                            'pod-end tails loose; soldered to the FC output field only in stage 9 '
                                            'step 4, so the FC goes in past them (D-89c)')),
    ('POD-004', dict(kind='lay', flexible=True, why='hook-and-loop straps: threaded through the floor groove under the tray '
                                     '(seats.json POD-001/POD-004), flexible')),
    ('FIN-009-*', dict(kind='clip', why='BUILD-GUIDE 4.5: the 10 x 2 CF brace strip ends sit in blind slots cut to '
                                        'its own section in the anchor and the collar ear (fins.py: the brace body is '
                                        'the slot), so it is bowed in, anchor end first, then sprung into the ear')),
    ('MEC-003-*', dict(kind='clip', fixture='servo arm and horn',
                       why='BUILD-GUIDE 7.5: the Z-bend is turned into the arm hole and the clevis sprung open over '
                           'the horn arm; neither is a rigid straight motion, so the rod is placed, not swept')),
]


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
    ('POD-011', 'Cross-screw: along its own axis the head meets the mast 6 mm out one way and the handle mast-socket '
                'boss 0.3 mm out the other; no out-then-across path. The 4.5 mm counterbore (seats.json POD-005) is '
                'cut to the head only; open it to the mast face, or give the handle boss a through hole.'),
    ('PWR-003', 'Power-board stand-in box rests on the PWR-101 frame-screw heads (0.050 mm, at the threshold): the box '
                'is cut by the whole screw (seats.json "mounting holes of the power board (envelope box)"). Model the '
                'board at its real thickness above the heads.'),
    ('MEC-004-*', 'Horn: the blade straddles the bonded torque tube (blocked by MEC-009 0.15 mm out in x and z) and sits '
                  'in its panel slot (blocked in y). It cannot go on after the tube (guide 3.3 before 7.2), and the '
                  'check found the tube cannot slide through a seated horn either. A horn that clamps on from one '
                  'side, or a blade slot open to the panel edge, would fit.'),
    ('MEC-006-*', 'Link horn: same as MEC-004 (blade over the outboard torque tube).'),
    ('PRP-005-*', 'Motor screws (each screw planned on its own): straight out of the plate hole, and out-then-across, '
                  'every path meets the mount collar / cheeks 7-19 mm out. A tilted entry with a ball-end key was not '
                  'searched (straight and two-segment paths only); check by hand on the first printed mount.'),
    ('PRP-006-*', 'Prop-adapter screws: the head meets the adapter 6 mm out: the counterbore (seats.json PRP-004 / '
                  'PRP-006 "adapter screw counterbores") is cut to the head envelope only, closed above it. Open the '
                  'counterbore to the adapter face.'),
    ('AVN-005', 'Pitot boom: the probe-root barb / coupler is caught by the socket POD-006 at 0.05-0.3 mm in every '
                'direction: the coupler is larger than the socket bore it must pass. Fit the coupler after the probe '
                'is through, or enlarge the bore.'),
]

# Placements that touch nothing placed: why, when the data does not say.
SUPPORT_NOTES = [
    ('HRN-113-*', 'XT30U pair hangs on its leads, tied to the tray (CT-TIE is not structural): no rigid support'),
    ('PWR-003', 'power board stand-in box sits more than 0.6 mm above the deck; held by the frame screws'),
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


def tape_trims(info):
    """{tape part: {parts it is trimmed round}} from interfaces/seats.json rows whose host is a tape ('lay' kind):
    'tape skin trimmed round X'. A tape is cut with a blade on the bench (BUILD-GUIDE 6.5: 'slit the tape round it with
    a fresh blade'), so X may pass the tape where the tape is trimmed for it: the pair is not tested during X's
    motion. Every use is listed in the check report."""
    exp = {'<st>': ['UR', 'UL', 'LR', 'LL'], '<s>': ['L', 'R']}
    out = {}
    for row in _load('seats.json')['seats']:
        h, g = row['host'], row['guest']
        for key, vals in exp.items():
            if key in g:
                gs = [g.replace(key, v) for v in vals]
                break
        else:
            gs = [g]
        if kind_of(h, info) == 'lay':
            out.setdefault(h, set()).update(gs)
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
    acts, used, groups = [], set(), {}
    for stage, step, cap, items in STEPS:
        for it in items:
            base = dict(stage=stage, step=step, caption=cap)
            if it.startswith('bench:'):
                name, glob = it[6:].split(' ', 1)
                for pid in sorted(p for p in part_ids if fnmatch.fnmatch(p, glob) and p not in used):
                    g = name.replace('<x>', suffix(pid))
                    groups.setdefault(g, []).append(pid)
                    used.add(pid)
                    acts.append(dict(base, type='bench', id=pid, group=g))
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
