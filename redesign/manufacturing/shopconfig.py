"""shopconfig.py - every shop decision the exporter makes that is NOT geometry (geometry comes from the CAD builders).

Edit this file, not the subsystem modules, when a print setting, spare count, orientation or sheet size changes.
Sources are named next to each value: subsystems/<x>/parts.csv (process / notes columns), subsystems/<x>/BUILD.md,
review/MANUFACTURING.md (MF-xx, "Make x2 from day one"), team/I1/BOM.csv (sheet stock).

Orientation vocabulary (PRINT[...]['orient']), all in the aircraft frame of the BASE instance (UR or R):
    {'down': (x, y, z)}   that world direction goes onto the bed; instances mirrored in y (L, UL, LL) or z (LR, LL)
                          get the direction mirrored the same way, so every variant prints on the same physical face
    {'axes': 'Z'}         automatic (largest flat face), but only faces whose normal is along the named axis/axes
    {}                    automatic: the largest flat face that the whole part rests on (ties -> lowest part)
"""

# ----------------------------------------------------------------------------- printers and filaments
FILAMENT = {   # density g/cm3 (maker data sheets, typical), volumetric rate mm3/s used for the time estimate
    'PETG': {'rho': 1.27, 'flow': 7.0},
    'ASA': {'rho': 1.07, 'flow': 6.0},
    'TPU95A': {'rho': 1.21, 'flow': 2.0},
}
LINE_W_MM = 0.45                 # extrusion width for the perimeter-shell estimate (0.4 mm nozzle)
LAYER_CHANGE_S = 3.0             # travel + layer change per layer (estimate)
JOB_OVERHEAD_MIN = 4.0           # heat-up + first layer per printed file

DEFAULT_LAYER = '0.2'            # used where no source states a layer height; the CSV marks it "(default)"

# Jacobs Hall machine per process (review/MANUFACTURING.md section 1, Jacobs pages checked 2026-11-11)
MACHINE = {
    'PETG': 'Prusa FDM (Jacobs open-access printers, studio 110/120)',
    'TPU95A': 'Prusa FDM with a direct-drive extruder (Jacobs open access); slow, 2 mm3/s',
    'ASA': 'Enclosed printer: NOT on the Jacobs open-access list (MF-15). Staffed Fortus/Markforged lab (room 332) '
           'or a teammate\'s enclosed printer',
    'laser': 'Universal laser cutter (Jacobs studios 110/120): 48 x 25 in bed for sheets over 32 x 18 in',
    'laser_small': 'Universal laser cutter 32 x 18 in or 48 x 25 in',
    'knife': 'Bench: steel rule + box cutter (no machine); panels too big for any Jacobs laser bed',
    'hotwire': 'Hot-wire bow (BOM G11, bought: hot-wire is NOT a listed Jacobs capability, MF-03); templates '
               'laser-cut on the Universal',
}
LASER_BEDS_MM = [(812.8, 457.2), (1219.2, 635.0)]     # 32 x 18 in, 48 x 25 in

# ----------------------------------------------------------------------------- printed parts
# key = base part id (station suffix stripped). Fields:
#   material   filament key in FILAMENT
#   include    regex on the CAD body name: only these bodies are printed (default: all bodies)
#   exclude    regex on the CAD body name: never printed (bought probe, XPS, foam board)
#   groups     [(suffix, regex), ...] split one CAD part into separate prints (POD-002 is 7+ prints)
#   spares     int: extra prints, spread over the geometric variants; or {colour: n}
#   colour     {station: colour} - colour is part of the file name and of the dedupe key
#   orient     see the module docstring; group_orient {suffix: orient} overrides it per print group
#   layer / perimeters / infill / supports: as stated in the source (blank -> default or auto)
#   hold       text: print is on hold (still exported, flagged in PRINT-LIST.csv)
#   src        where the settings come from
PRINT = {
    'WNG-004': dict(material='PETG', perimeters='4', infill='50 % gyroid', orient={},
                    src='wing/parts.csv; wing/BUILD.md stock row'),
    'WNG-005': dict(material='PETG', infill='30 %', orient={}, src='wing/parts.csv'),
    'FIN-003': dict(material='ASA', layer='0.2', perimeters='5', infill='', orient={'down': (0, 0, -1)},
                    spares=4, src='fins/parts.csv ("collar axis vertical on the bed"); spares: MANUFACTURING.md '
                    '"Make x2" (8 total: 4 A + 4 B)', note='A = UR/LL, B = UL/LR; drill 3.4 mm to the measured motor; '
                    'R5 prints only'),
    'FIN-004': dict(material='PETG', perimeters='3', infill='15 % gyroid', orient={'axes': 'XZ'}, spares=1,
                    src='fins/parts.csv ("spar bore horizontal on the bed"); spare: MANUFACTURING.md (3 blocks)'),
    'FIN-007': dict(material='ASA', infill='100 %', orient={}, src='fins/parts.csv'),
    'FIN-008': dict(material='PETG', infill='100 % ring; tongue 3 perimeters + 20 % gyroid', perimeters='3',
                    orient={'down': (0, 0, 1)}, spares=4,
                    src='fins/parts.csv ("upside down on the tail cap"), fins/BUILD.md prints row; spares: '
                    'MANUFACTURING.md (8 collars)',
                    hold='ON HOLD: STATUS issue 1 / MF-13 "do not print collars until settled" (freeze 18 Dec)'),
    'FIN-010': dict(material='PETG', infill='80 %', orient={'axes': 'XY'}, src='fins/parts.csv ("brace slot '
                    'vertical on the bed")'),
    'GER-001': dict(material='PETG', layer='0.2', perimeters='3', infill='100 %', orient={'down': (1, 0, 0)},
                    supports='only under the two leg ends at the TE', spares=2,
                    src='landing/parts.csv + BUILD.md step 1 ("rim end on the bed"); spares = GER-012 x2'),
    'GER-002': dict(material='PETG', layer='0.2', perimeters='2', infill='', orient={'down': (1, 0, 0)},
                    colour={'UR': 'orange', 'UL': 'orange', 'LR': 'blue', 'LL': 'blue'},
                    spares={'orange': 4, 'blue': 4}, supports='none',
                    src='landing/parts.csv + BUILD.md step 2 ("flange on the bed"); spares = GER-005 x4 (orange) '
                    '+ GER-009 x4 (blue) inserts'),
    'GER-007': dict(material='TPU95A', perimeters='2', orient={'down': (0, 1, 0)}, supports='none',
                    src='landing/parts.csv ("open side up")'),
    'MEC-004': dict(material='PETG', infill='100 %', orient={'axes': 'Y'}, spares=2,
                    src='mechanisms/BUILD.md ("horns flat on the y face"); spares: MANUFACTURING.md "Make x2"'),
    'MEC-006': dict(material='PETG', infill='100 %', orient={'axes': 'Y'}, spares=2,
                    src='mechanisms/BUILD.md ("flat on the y face"); spares: MANUFACTURING.md "Make x2"'),
    'MEC-007': dict(material='PETG', perimeters='2', orient={}, src='mechanisms/BUILD.md (cover 2 perimeters)'),
    'MEC-008': dict(material='PETG', perimeters='3', orient={}, spares=2,
                    src='mechanisms/BUILD.md (frame 3 perimeters); spares: MANUFACTURING.md "Make x2"'),
    'POD-001': dict(material='PETG', include=r'^petg', layer='0.2', orient={},
                    groups=[('lip', r'nose lip'), ('tube', r'antenna tube')], group_orient={'tube': {'axes': 'X'}},
                    src='pod/BUILD.md step 1 (nose lip, antenna tube B); board and XPS bodies go to the cut list'),
    'POD-002': dict(material='PETG', layer='0.2', orient={'axes': 'Z'}, supports='none',
                    infill='100 % (T, aft stop, plates); others default',
                    groups=[('floorF', r'bay floor front'), ('floorR', r'bay floor rear|aft stop|stop gusset'),
                            ('stopT', r'forward stop T'), ('guide', r'^petg guide'),
                            ('FC', r'FC plate|FC end stop'), ('avn', r'avionics plate|tie post'),
                            ('UBEC', r'UBEC plate'), ('PDB', r'PDB'), ('JR', r'JR tie bar')],
                    src='pod/BUILD.md step 1 (separate prints, bonded full-area to the floor)'),
    'POD-003': dict(material='PETG', include=r'^petg', layer='0.2', orient={},
                    groups=[('tongue', r'hatch tongue'), ('tab', r'latch tab'), ('tube', r'antenna tube')],
                    group_orient={'tube': {'axes': 'Z'}},
                    src='pod/BUILD.md step 1 (hatch tongue, latch tab, antenna tube A)'),
    'POD-005': dict(material='PETG', layer='0.2', orient={}, src='pod/BUILD.md step 1'),
    'POD-006': dict(material='PETG', layer='0.2', orient={}, src='pod/BUILD.md step 1'),
    'POD-007': dict(material='PETG', layer='0.2', perimeters='3', infill='25 % (40 % feet and grip; bridge 100 %)',
                    orient={'down': (0, 0, -1)}, supports='under the strut ribs (pod/BUILD.md)', spares=1,
                    src='pod/BUILD.md step 1 ("standing on the foot plates"; parts.csv says "lying flat": BUILD.md '
                    'is newer); spare: MANUFACTURING.md "Make x2"'),
    'POD-008': dict(material='PETG', layer='0.2', orient={},
                    src='pod/BUILD.md step 1; set from pod/params.json spacer_set_m, colours spacer_colour'),
    'POD-010': dict(material='PETG', infill='100 %', orient={}, src='pod/parts.csv ("solid")'),
    'PWR-006': dict(material='PETG', layer='0.2', perimeters='4', infill='100 %', orient={'axes': 'Z'},
                    src='power/BUILD.md step 2 ("deck flat on the bed": deck parallel to the bed; the cradle walls '
                    'and legs leave no free deck face, so the wall tops go down)'),
    'AVN-005': dict(material='PETG', infill='100 %', include=r'^petg', orient={}, supports='none; use a brim (tall, '
                    '10 mm footprint)',
                    src='avionics/BUILD.md step 7; the aluminium probe and couplers are bought'),
}

# Parts that are printed but whose geometry is another part's (spare components placed in the CAD)
SPARE_COMPONENTS = {'GER-012': 'GER-001', 'GER-005': 'GER-002', 'GER-009': 'GER-002'}

# Printed parts in the BOM with no CAD body (reported, not exported)
NOT_IN_CAD = {
    'HRN-110': 'Fin-hole grommet ASA 10/7 x 12 mm (x6 incl. 2 spare): harness/parts.csv lists it, no CAD body exists '
               '(mass is lumped into HRN-001/002). F2 to model it; until then print a 10/7 x 12 mm tube by hand.',
}

# ----------------------------------------------------------------------------- sheet stock (team/I1/BOM.csv)
SHEETS = {
    'foamboard': dict(name='Foam board 4.8 mm (3/16 in), paper faced', size_mm=(762.0, 508.0), t_mm=4.8,
                      bom='W02 (20 x 30 in, 10-pack)', kerf_mm=0.3, margin_mm=8.0, gap_mm=4.0,
                      machine='laser', note='20 x 30 in sheet fits only the 48 x 25 in Universal bed; ask Jacobs '
                      'whether foam board may be lasered (MF-21); otherwise print the 1:1 PDF and knife-cut'),
    'coroplast': dict(name='Coroplast 4 mm (PP twin-wall)', size_mm=(2438.4, 1219.2), t_mm=4.0,
                      bom='T01 (48 x 96 in x 2)', kerf_mm=0.0, margin_mm=6.0, gap_mm=6.0, machine='knife',
                      note='separate panels joined with taped/hot-melted corner angles (MF-16); flutes along the '
                      '1.25 m length; score lines are not drawn'),
    'ply3': dict(name='Birch plywood 3 mm', size_mm=(1219.2, 609.6), t_mm=3.0,
                 bom='T05 "3 mm birch ply (Jacobs stock)"; jig board/bar in the same stock (or 6 mm MDF)',
                 kerf_mm=0.15, margin_mm=8.0, gap_mm=5.0, machine='laser',
                 note='48 x 24 in sheet on the 48 x 25 in Universal bed; confirm the Jacobs stock size'),
    'hardboard2': dict(name='Hardboard or plywood 2 mm (hot-wire templates)', size_mm=(457.2, 304.8), t_mm=2.0,
                       bom='not in BOM (wing/BUILD.md tools row: "2 mm ply or hardboard")', kerf_mm=0.15,
                       margin_mm=8.0, gap_mm=6.0, machine='laser_small', note='18 x 12 in offcut is enough'),
}

# Sheet parts: spares and the not-in-CAD pieces (source named; they are drawn from the BUILD.md numbers)
SHEET_SPARES = {'FIN-001': 4}     # spare half-fin LAMINATES (x 2 boards): MANUFACTURING.md "Make x2" (4 spare)
EXTRA_SHEET_PARTS = [
    # (part, piece, sheet, w mm, h mm, qty, holes [(x, y, d)], source)
    ('TRN-105', 'handle backing strip', 'ply3', 140.0, 30.0, 3, [(20.0, 15.0, 3.4), (120.0, 15.0, 3.4)],
     'transport/BUILD.md step 11 (not modelled in CAD)'),
    ('TRN-104', 'landing mat panel', 'ply3', 800.0, 400.0, 2, [],
     'transport/BUILD.md step 15 (not modelled in CAD)'),
]
SHEET_EXCLUDE = {'TRN-001': r'pad', 'TRN-005': r'lining'}   # PE foam pads are not Coroplast

# Hot-wire (wing/params.json elevon.end_gap_m note: "hot-wire kerf ~1 mm"; BOM G11: Ni80 24 AWG = 0.51 mm)
HOTWIRE = dict(kerf_mm=1.0, wire_d_mm=0.511, blank_mm=(1200.0, 330.0, 50.0), le_margin_mm=5.0,
               src='kerf: wing/params.json elevon.end_gap_m note; wire: BOM G11 Ni80 24 AWG; blank: wing/BUILD.md')

# Letter paper tiling for 1:1 PDFs
LETTER_MM = (279.4, 215.9)        # landscape
PAGE_MARGIN_MM = 9.0
TILE_OVERLAP_MM = 12.0
