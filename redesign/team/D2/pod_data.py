"""D2 pod data generator: builds the pod CAD module on the stub backend, turns body volumes into masses and CGs,
and writes subsystems/pod/interfaces.json and subsystems/pod/parts.csv from one table, so the declared masses and
CGs are the CAD's.

    python -I redesign/team/D2/pod_data.py          # rewrite interfaces.json + parts.csv, print the roll-up
    python -I redesign/team/D2/pod_data.py --check  # exit 1 if the files on disk differ from what it would write

Masses: foam board = area x params fins.areal_mass_kgm2; XPS = volume x wing.core.density_kgm3; printed PETG =
volume x pod petg_kgm3 x fill (plate / block); EVA pad = volume x eva_kgm3; bought items (straps, ties,
inserts, label, glue) from pod params bought_g. All EST until weighed (T-D2-WEIGH).
"""
import csv
import importlib.util
import io
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
POD = REDESIGN / 'subsystems' / 'pod'
sys.path.insert(0, str(REDESIGN / 'fusion'))
import fusionkit as fk                              # noqa: E402
import k09kit as k9                                 # noqa: E402
from backends.stub_backend import StubBackend      # noqa: E402


def pod_mod_net_area(loops):
    return load_module()._net_area(loops)


def load_module():
    spec = importlib.util.spec_from_file_location('pod_module', str(POD / 'fusion' / 'pod.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def local():
    return json.loads((POD / 'params.json').read_text(encoding='utf-8'))


def lv(L, k):
    d = L[k]
    return d['value'] if isinstance(d, dict) and 'value' in d else d


# ----------------------------------------------------------------------------- the part table (one source)
PARTS = [
    # id, name, material, make_or_buy, process, vendor_or_file, bought extras (keys of bought_g), notes
    ('POD-001', 'Pod shell (foam-board box, XPS LE filler, printed nose lip and antenna tube B)', 'foam board + PETG', 'make',
     'knife/laser-cut foam board, hot-wire XPS, FDM lip and tube', 'subsystems/pod/fusion/pod.py', ['glue_shell', 'tape_light', 'fillet_corners'],
     'floor (front edge notched 4 x 54 mm for the forward-stop T, D-69), 2 side walls (16 x 12 mm power/DShot exits, CR-F2-03; '
     'bracket flanges bonded inside), nose wall at x -0.140 (D-62; pitot, vent and antenna holes), aft wall (vent + servo-lead exits), '
     'aft deck; the forward stop sits on a 1 mm epoxy line on the nose wall; 6 mm microballoon fillets floor-to-wall at the straps '
     '(CR-C6-17); light tape on the top (CR-E3-03)'),
    ('POD-002', 'Tray: bay floor (2 pieces) + forward-stop T + 3 mm aft stop + 1.5 mm guides, FC, avionics and ribbed PDB plates, JR tie bar (printed PETG)',
     'PETG (printed)', 'make', 'FDM PETG, 7 prints epoxied full-area to the floor', 'subsystems/pod/fusion/pod.py', ['glue_tray', 'inserts_m3'],
     'R6 (D-62, D-69): forward-stop T (face x -0.1312; upright past the floor edge to a 12 x 54 x 1.2 mm flange bonded under the floor, '
     'CR-C3-15), aft stop face x 0.0475 with 2 root ribs on the rear piece (backed by the POD-007 strut); 4 strap slots 26 x 1.8 mm at '
     'x -0.079 / 0.006 (D-74); 10 mm wire channel across the bay at x -0.0245 (CR-F2-03); FC on 4 gel cubes between end stops with strap '
     'slots (CR-F3-12, CR-C6-19); airspeed between tie posts 21 mm apart, foam tape + 1 tie; PDB plate x -0.038-0.050 with 4 bosses '
     '7.2 mm for M3 heat-set inserts (F1 power frame, 25 mm pattern, CR-C6-27) and a 1.6 x 4 mm rib along each boss row; no UBEC plate '
     '(D-74: the zone x 0.044-0.074 holds the right XT30U pair); JR tie bar x 0.021-0.040 right channel'),
    ('POD-003', 'Hatch (foam board, printed tongue, 12 x 40 hook-and-loop tab, antenna tube A)', 'foam board + PETG', 'make',
     'knife-cut foam board, FDM tongue and tube', 'subsystems/pod/fusion/pod.py', ['velcro_tab'],
     'tool-free, no magnets: tongue under the nose lip, hook-and-loop tab on the aft deck; receiver antenna A up the tube'),
    ('POD-004', 'Pack straps (2, 20 mm hook-and-loop, rubber-backed) + 2 EVA pads 2.5 mm', 'nylon hook-and-loop + EVA', 'buy',
     'cut to length', 'battery strap 20 x 300 mm (any RC vendor); EVA sheet 2.5 mm with anti-slip face', [],
     'two straps at the pack quarter points, overlap >= 50 mm marked; slots let them follow the station range'),
    ('POD-005', 'GPS mast with 45 deg pad (printed PETG, plugs into the handle grip)', 'PETG (printed)', 'make', 'FDM PETG',
     'subsystems/pod/fusion/pod.py', ['mast_hw'], 'GPS taped on the pad tilted 45 deg toward the nose, arrow forward; GPS cable up the '
     'mast bore; PA66 M3 screw + nut (no steel within 50 mm, CR-C6-18)'),
    ('POD-006', 'Pitot boom socket with 32 mm flange (printed PETG, pod nose, left channel)', 'PETG (printed)', 'make', 'FDM PETG',
     'subsystems/pod/fusion/pod.py', ['glue_socket'], 'bore 6.2 mm for the 6 mm keyed boom (F3 accepted); flange bonded to the nose wall inside face (CR-C6-09)'),
    ('POD-007', "Carry handle on the spar with the foot bridge, aft-stop strut and wall brackets (printed PETG) + 'LIFT HERE - do not lift by the motors' label", 'PETG (printed)',
     'make', 'FDM PETG, printed lying flat, 40 % infill feet and grip', 'subsystems/pod/fusion/pod.py', ['tie_each', 'tie_each', 'label', 'glue_handle'],
     'feet saddle the spar top in the open slot, one 7.6 mm nylon tie each round foot + spar; bridge between the feet (x 0.077-0.090) '
     'on the slot fill; R6 (D-69): aft-stop strut (40 x 14 x 1.5 mm pad on the stop back face, three 3 x 14 mm ribs 25 mm long to the '
     'bridge, CR-C3-14) and one wall bracket per side (2 mm web from the foot to a 1.2 mm flange epoxied to the side wall over '
     '1 232 mm2, CR-C3-16); legs through the aft deck; GPS cable in the right leg (window at z 0.055-0.065) and a groove under the '
     'grip (CR-F2-03)'),
    ('POD-008', 'Trim spacer set: PETG U-spacers 2 / 4 / 6 / 8 / 8 mm, colour-coded (white / yellow / green / blue)', 'PETG (printed)', 'make',
     'FDM PETG, one colour per thickness', 'subsystems/pod/fusion/pod.py', [],
     'behind the pack, on the aft stop (x 0.0475); set 2 / 4 / 6 / 8 mm (white / yellow / green / blue), every 2 mm stack 0-20 mm; '
     'A1 frame-estimate stations (D-62): 546 g 16 mm (-0.036), 550 g 14 mm (-0.034), 590 g 8 mm (-0.028), final from A3 (CR-A3-27); '
     'the stack is written on the pack label. CAD and mass: blue 8 + yellow 4 mm (pack at the -0.032 datum); the rest are field kit (ground)'),
    ('POD-009', 'Crush block (XPS F-250, hot-wired, cut per pack, vent groove)', 'XPS', 'make', 'hot-wire XPS F-250',
     'subsystems/pod/fusion/pod.py', [],
     'ahead of the pack on the forward stop (CR-C5-02; C5 minimum 25.7 mm for the 550 g class): length = pack fore face - 1.5 mm - '
     '(-0.1312): 546 g 26.2 mm, 550 g 28.2 mm, 590 g 34.2 mm (30.2 mm in the CAD at the datum); labelled per pack; replace after any '
     'nose-in landing'),
    ('POD-010', 'Spreader (1.5 mm PETG plate, full block section)', 'PETG (printed)', 'make', 'FDM PETG, solid',
     'subsystems/pod/fusion/pod.py', [], 'between the crush block and the pack fore face; spreads the pack face load over the block section (C5)'),
]

EDGES = [
    {'id': 'E-POD-01', 'part_a': 'POD-001', 'part_b': 'WNG-001', 'via': 'CT-EPOXY', 'owner': 'pod',
     'notes': 'shell floor, XPS LE filler, side walls and aft wall bonded to bare, sanded foam: D1 cuts the recess (x_rec0 ... x_rec1, '
              'z = pod base, full pod width) and leaves the tape skin off under the pod (CR-C2-07); skin then taped over the shell foot (CR-D2-04)',
     'bond': 'AREA_POD_WING'},
    {'id': 'E-POD-02', 'part_a': 'POD-002', 'part_b': 'POD-001', 'via': 'CT-EPOXY', 'owner': 'pod',
     'notes': 'tray front and rear pieces, FC, avionics and PDB plates and the JR bar epoxied full-area to the foam-board floor '
              '(paper face scuffed); forward-stop T (D-69, CR-C3-15): upright bonded to the floor front edge and, through the 1 mm '
              'microballoon line, to the nose wall; flange bonded under the floor (9 x 54 mm), tray front piece bonded over the floor '
              'behind it, so the -x root moment clamps the floor; 6 mm microballoon fillets floor-to-side-wall over +/-30 mm of each '
              'strap (CR-C6-17) and over x -0.131 ... -0.010 (CR-C3-01)', 'bond': 'AREA_TRAY'},
    {'id': 'E-POD-03', 'part_a': 'POD-003', 'part_b': 'POD-001', 'via': 'CT-HATCH-HL', 'owner': 'pod',
     'notes': 'opened every flight, tool-free, no magnets; the hatch carries no pack load',
     'retention': {'item': 'tongue under the nose lip + 12 x 40 mm hook-and-loop tab (CR-C3-01)', 'count': 1, 'load_n': 'hatch weight only (< 10 g)',
                   'inspection': 'tab grips, tongue seated: pre-flight card'}},
    {'id': 'E-POD-04', 'part_a': 'POD-004', 'part_b': 'POD-002', 'via': 'CT-STRAP-SLOT', 'owner': 'pod',
     'notes': 'each strap passes down a slot, under the tray in a 1 mm groove cut in the foam floor, up the other slot',
     'retention': {'item': 'strap in 2 slots 37 x 1.8 mm', 'count': 2, 'load_n': 'see E-POD-05', 'inspection': 'no fraying at the slot edges: pre-flight card'}},
    {'id': 'E-POD-05', 'part_a': 'PWR-001', 'part_b': 'POD-002', 'via': 'CT-STRAP-VELCRO', 'owner': 'pod',
     'notes': 'field joint. z/y: 2 straps + guides + EVA pads; fore-aft: crush block POD-009 + spreader POD-010 ahead (on the forward '
              'stop, x -0.1312), U-spacers POD-008 + aft stop (x 0.0475, on the tray, strut-backed) behind. D-62 frame-estimate stations: '
              '546 g -0.036 (16 mm), 550 g -0.034 (14 mm), 590 g -0.028 (8 mm), final from A3 (CR-A3-27); CAD pack at the datum '
              'pod.pack_x_nominal_m -0.032 (aft face 0.0355, 12 mm); block cut per pack to fill the gap (no fore-aft play). Leads exit aft over the stop',
     'retention': 'RET_PACK', 'field_joint': True},
    {'id': 'E-POD-06', 'part_a': 'POD-005', 'part_b': 'POD-007', 'via': 'CT-M3-PA66-NUT', 'owner': 'pod',
     'notes': 'mast plugs 8 mm into the grip socket; cross-screwed with PA66 hardware (C6 CR-C6-18; F3: no steel within 50 mm of the '
              'compass); 6.5 mm counterbore 4.5 deep on +y keeps the grip at 10.0 mm (C6 <= 11.0); the mast is the fuse: replace it after a tip-over',
     'joint_stack': {'fastener': 'M3x16 PA66 (nylon) cheese-head screw, slotted (DIN 84 PA66)', 'count': 1, 'grade': 'PA66',
                     'hole': '3.4 mm clearance across the socket boss (POD-007, 14 mm, counterbored to a 10.0 mm grip) and the mast base (POD-005)',
                     'insert': 'none', 'engagement_mm': 6.0, 'min_engagement_mm': 4.0,
                     'washer_nut': 'M3 PA66 hex nut fully on + 2 pitches; no washer (grip 10.0 mm, 6.0 mm past the grip)',
                     'torque': 'finger tight + 1/4 turn (~0.1 N m); no threadlocker', 'tool': 'flat screwdriver + fingers',
                     'access': 'from +y beside the grip, above the pod', 'install_order': 7, 'removal_order': 1}},
    {'id': 'E-POD-07', 'part_a': 'POD-006', 'part_b': 'POD-001', 'via': 'CT-EPOXY', 'owner': 'pod',
     'notes': 'socket through a 12 mm square hole in the nose wall; 32 x 32 mm flange bonded to the wall inside face (CR-C6-09); the '
              'nose block is cut round the flange; boom bending (1 kg on the tip in handling, 0.8 N m) goes into the nose wall', 'bond': 'AREA_SOCKET'},
    {'id': 'E-POD-08', 'part_a': 'POD-007', 'part_b': 'POD-001', 'via': 'CT-EPOXY', 'owner': 'pod',
     'notes': 'handle legs pass through 7.8 mm slots in the aft deck at y +/-0.048, bonded: locates the deck', 'bond': 'AREA_LEGS'},
    {'id': 'E-POD-14', 'part_a': 'POD-007', 'part_b': 'POD-002', 'via': 'CT-EPOXY', 'owner': 'pod',
     'notes': 'D-69 (CR-C3-14): the strut pad (40 x 14 x 1.5 mm, z 0.026-0.040) on the aft stop back face (x 0.0505), epoxy-bedded when '
              'the handle goes in so it bears without a gap; +x pack load: stop -> pad (bearing) -> 3 ribs -> foot bridge -> feet -> '
              'spar saddle + ties + wall brackets (E-POD-09, E-POD-15)', 'bond': 'AREA_STRUT'},
    {'id': 'E-POD-15', 'part_a': 'POD-007', 'part_b': 'POD-001', 'via': 'CT-EPOXY', 'owner': 'pod',
     'notes': 'D-69 (CR-C3-16): one wall bracket per side, flange epoxied to the side-wall inner face (foam-board paper face '
              'scuffed); ties the handle feet to the shell so the pod shear goes into the spar, not the recess step. Do not count '
              'the wall-edge bonds aft of the recess (E-POD-01) as structure. T-C3-POD-PROOF adds 200 N on the brackets (+x, -z)',
     'bond': 'AREA_BRACKET'},
    {'id': 'E-POD-09', 'part_a': 'POD-007', 'part_b': 'WNG-002', 'via': 'CT-SPAR-TIE', 'owner': 'pod',
     'notes': 'carry point on the spar (D-23): feet saddle the spar top in the open slot (y 0.029 ... 0.053), bonded (scuffed CF, 30 min '
              'epoxy), one 7.6 mm nylon tie per foot at y +/-0.036 laid under the spar before D1 bonds it (CR-D2-04); the foot bridge '
              'between the feet sits on the slot fill (|y| < 0.029). D-69: the strut from the aft stop ends on the bridge and the '
              'wall brackets tie the feet to the shell, so the spar takes the pack +x load and the pod shear',
     'retention': 'RET_SPAR', 'bond': 'AREA_SADDLE'},
    {'id': 'E-POD-10', 'part_a': 'POD-008', 'part_b': 'POD-002', 'via': 'CT-SLIDE-STOP', 'owner': 'pod',
     'notes': 'U-spacers stand between the pack aft face and the aft stop (x 0.0475, D-62; on the tray rear piece), held by the pack; '
              'the pack leads pass over them; +x load: stop -> strut pad -> ribs -> foot bridge (E-POD-14, D-69)',
     'retention': {'item': 'trapped between the pack and the aft stop', 'count': 1, 'load_n': 'pack +x: 38 N hover landing limit (6.6 g x 590 g), 85 N crash ultimate',
                   'inspection': 'spacer set for this pack fitted (label on the pack): pre-flight card'}},
    {'id': 'E-POD-11', 'part_a': 'POD-009', 'part_b': 'POD-002', 'via': 'CT-SLIDE-STOP', 'owner': 'pod',
     'notes': 'crush block against the 3 mm forward stop, between the guides; cut per pack (length = pack fore face - 1.5 mm - '
              '(-0.1312), >= C5 minimum 25.7 mm); the stop T is backed by the nose wall through a 1 mm epoxy line and clamps the floor '
              'with its flange (D-69), so in a nose-in crash the block crushes against a fixed stop',
     'retention': {'item': 'trapped between the forward stop and the pack', 'count': 1,
                   'load_n': 'pack -x: 85 N ultimate; crash: crush, <= 100 g on the pack (C5)',
                   'inspection': 'block intact, not crushed, labelled for this pack: pre-flight card'}},
    {'id': 'E-POD-13', 'part_a': 'POD-010', 'part_b': 'POD-009', 'via': 'CT-SLIDE-STOP', 'owner': 'pod',
     'notes': 'spreader trapped between the crush block and the pack fore face (loose, no bond; R5 split of the trim kit, CR-A5-27)',
     'retention': {'item': 'trapped between the crush block and the pack', 'count': 1, 'load_n': 'pack -x: 85 N ultimate; crash crush load (C5)',
                   'inspection': 'spreader flat, uncracked, on the block: pre-flight card'}},
    {'id': 'E-POD-12', 'part_a': 'PWR-001', 'part_b': 'POD-002', 'via': 'CT-THERMAL-CONTACT', 'owner': 'pod',
     'notes': 'insulating contact (E3 CR-E3-11): pack on 2.5 mm EVA pads on the 1 mm PETG tray over 4.8 mm foam board; the pack '
              'heat leaves by the pod air through the two vents (CR-E3-03), not by this contact',
     'thermal': {'heat_w': 'about 0 through this contact (insulating; pack loss goes to the pod air: E3 3-node model)',
                 't_max_c': 50, 't_ambient_c': 44,
                 'path': 'pack -> pod air -> nose inlet / aft exit vents and the foam-board shell; the pads, tray and floor insulate',
                 'sized_by': 'E3', 't_design_c': 44.8, 'claim': 'CL-E3-PACK-END'}},
]

CTYPES = [
    {'id': 'CT-HATCH-HL', 'kind': 'mechanical', 'method': 'strapped',
     'spec': 'hatch: printed tongue under a fixed lip at one end, hook-and-loop tab at the other (tool-free, no magnets)'},
    {'id': 'CT-STRAP-SLOT', 'kind': 'mechanical', 'method': 'slid', 'spec': 'strap threaded through slots in a printed tray'},
    {'id': 'CT-SPAR-TIE', 'kind': 'mechanical', 'method': 'strapped',
     'spec': 'printed saddle bonded on a round spar + nylon cable tie round saddle and spar (7.6 mm, 50 lb class)'},
    {'id': 'CT-SLIDE-STOP', 'kind': 'mechanical', 'method': 'slid', 'spec': 'loose printed spacer trapped between two stops'},
    {'id': 'CT-M3-PA66-NUT', 'kind': 'mechanical', 'method': 'fastened',
     'spec': 'M3 PA66 (nylon) screw through a clearance hole, PA66 nut, finger tight + 1/4 turn (non-magnetic, near a compass; the screw is a fuse)'},
]

ACKS = ['E-PWR-03', 'E-PWR-05', 'E-AVN-01', 'E-AVN-02', 'E-AVN-03', 'E-AVN-04', 'E-AVN-05', 'E-AVN-07',
        'E-AVN-10', 'E-HRN-01']   # D-103: E-WNG-17 deleted with the fillet   # R4: E-PWR-01/-02 now land on F1's power frame PWR-006 (CR-F1-16), not on POD-002


def build_pod():
    P = k9.load_params()
    L = local()
    parts_info = {p[0]: {'name': p[1], 'material': p[2], 'mass_g': 1.0, 'status': 'MODELLED'} for p in PARTS}
    ctx = fk.Context(StubBackend(), parts=parts_info, params=P)
    ctx.begin_module('pod', str(POD))
    k9.build_datums(ctx)
    mod = load_module()
    mod.build(ctx)
    coords, src = k9.section(ctx)
    G = mod.layout(ctx.value, ctx.local, coords)
    return ctx, P, L, G, src


def masses(ctx, P, L):
    """part id -> (mass_g, cg, per-material breakdown)."""
    ar = k9.val(P, 'fins.areal_mass_kgm2', 'kg/m2')
    tb = k9.val(P, 'fins.board_t_m', 'm')
    xps = k9.val(P, 'wing.core.density_kgm3', 'kg/m3')
    petg, fill, eva = lv(L, 'petg_kgm3'), lv(L, 'fill'), lv(L, 'eva_kgm3')
    bought = lv(L, 'bought_g')
    out = {}
    for pid, name, *_r in PARTS:
        extras = next(p[6] for p in PARTS if p[0] == pid)
        c = ctx.components[pid]
        M, m, br = 0.0, [0.0, 0.0, 0.0], {}
        for s in c.shapes:
            V, cg = s.volume_centroid()
            nm = s.name or ''
            if nm.startswith('fb '):
                g, k = V / tb * ar * 1000, 'foam board'
            elif nm.startswith('xps '):
                g, k = V * xps * 1000, 'XPS'
            elif nm.startswith('petgb '):
                g, k = V * petg * fill['block'] * 1000, 'PETG block'
            elif nm.startswith('petg '):
                g, k = V * petg * fill['plate'] * 1000, 'PETG plate'
            elif nm.startswith('eva '):
                g, k = V * eva * 1000, 'EVA'
            elif nm.startswith('strap'):
                g, k = bought['strap_each'], 'strap (bought)'
            else:
                raise ValueError('body %s of %s has no material tag' % (nm, pid))
            M += g
            m = [m[i] + g * cg[i] for i in range(3)]
            br[k] = br.get(k, 0.0) + g
        geo = [v / M for v in m]
        for e in extras:
            M += bought[e]
            m = [m[i] + bought[e] * geo[i] for i in range(3)]
            br[e] = br.get(e, 0.0) + bought[e]
        out[pid] = (M, [v / M for v in m], br)
    return out


def cg_vs_body(ctx, M):
    """part id -> distance (m) between the declared mass CG and the uniform-density body centroid (A5's check)."""
    out = {}
    for pid in M:
        _V, cen = ctx.components[pid].volume_centroid()
        out[pid] = math.dist(cen, M[pid][1])
    return out


def areas(G, L):
    """Bond areas (mm2) and their inputs from the layout."""
    yi, W, tb = G['yi'], G['W'], G['tb']
    floor = (G['x_rec1'] - G['x_rec0']) * 2 * yi
    filler = G['x_rec0'] * W
    walls = 2 * tb * (G['x1'] - G['x_rec0'])
    aftw = tb * 2 * yi
    fy0, fy1 = lv(L, 'foot_y_m')
    rs = G['rs']
    half = math.sqrt(max(rs * rs - (G['z_cheek'] - G['zs']) ** 2, 0.0))
    arc = 2 * rs * math.asin(min(half / rs, 1.0))
    bridge = (G['xf'][1] - lv(L, 'bridge_x0_m')) * 2 * fy0
    saddle = 2 * (fy1 - fy0) * arc + bridge
    chw = G['ch_y'][1] - G['ch_y'][0]
    ax0, ax1 = lv(L, 'avn_plate_x_m')
    p0, p1 = lv(L, 'pdb_plate_x_m')
    jb = lv(L, 'jr_bar_m')
    p1 = lv(L, 'pdb_plate_x1_m')                        # R6: PDB plate runs aft to here (CR-C6-27)
    tray = sum(pod_mod_net_area(lp) for _n, lp in G['tray_loops']) + \
        (lv(L, 'fc_plate_len_m') + (ax1 - ax0) + (p1 - p0)) * chw + jb[2] * (chw - 0.001)    # D-74: no UBEC plate
    so = lv(L, 'socket_m')
    fl = lv(L, 'flange_m')[0]
    sock = 4 * so[0] * tb + fl * fl - so[0] * so[0]
    lg = lv(L, 'leg_m')[0]
    legs = 2 * 4 * lg * tb
    mm2 = lambda a: round(a * 1e6)
    tray += G['fs_flange_bond']
    strut = G['strut']['pad'][1] * (G['strut']['rib_z'][1] - G['strut']['rib_z'][0])
    bracket = 2 * G['bracket_area']
    return {'AREA_POD_WING': mm2(floor + filler + walls + aftw), 'AREA_TRAY': mm2(tray), 'AREA_SOCKET': mm2(sock),
            'AREA_STRUT': mm2(strut), 'AREA_BRACKET': mm2(bracket), 'bracket_each': mm2(G['bracket_area']),
            'AREA_LEGS': mm2(legs), 'AREA_SADDLE': mm2(saddle), 'bridge': mm2(bridge),
            'tray_front': mm2(G['tray_front_area']), 'tray_rear': mm2(G['tray_rear_area']),
            'parts': {'floor': mm2(floor), 'filler': mm2(filler), 'walls': mm2(walls), 'aft wall': mm2(aftw)}}


BOND = {
    'AREA_POD_WING': ('30 min epoxy thickened with microballoons (foam-safe; no CA on XPS)', 'tape skin off under the pod; '
                      'foam and board faces scuffed, dust off', '24 h at >= 18 degC before load',
                      'CL-C1-POD-F-ULT 121.7 N + 3.0 N m (L1 landing, ultimate); crash: pod group 12.75 g (CL-D2-POD-CRASH-F)',
                      'L1 landing; C1 crash any axis; D1 lays a 5 mm microballoon fillet in the recess-step corner '
                      '(x 0.065, z 0.015-0.020) before the pod goes in (D-69, CR-C3-17)', 'C3 (CR-D2-05)'),
    'AREA_TRAY': ('30 min epoxy; 6 mm microballoon fillets at the floor-to-wall corners by the straps; 1 mm microballoon epoxy line '
                  'between the forward stop / tray front and the nose wall', 'PETG underside sanded 120 grit; board face scuffed 220 grit', '24 h',
                  'pack straps 85 N ultimate (CL-C1-PACK-CRASH-LOAD) into the floor; forward stop 85 N on the front piece '
                  '(CL-D2-FWD-STOP-BOND: tray front piece + stop-T flange); peel at the stop roots is C3 (CL-C3-FEA-FWD-BED-PEEL, '
                  'CL-C3-FEA-AFT-PROP-PEEL)', 'C1 crash', 'C3, C6'),
    'AREA_SOCKET': ('30 min epoxy', 'PETG sanded; hole edges sealed; flange face to the paper face, clamped', '24 h', '1 kg on the boom tip in handling, about 0.8 N m', 'handling', 'C6 (CR-C6-09), C3'),
    'AREA_LEGS': ('30 min epoxy', 'PETG sanded', '24 h', 'shell crash load bearing on the legs', 'C1 crash', 'C3'),
    'AREA_STRUT': ('30 min epoxy thickened with microballoons (bedding, fills the build gap)', 'PETG faces sanded 120 grit', '24 h',
                   'pack +x 85 N ultimate in bearing (0.15 MPa over the pad); the bond only locates', 'C1 crash +x', 'C3 (CR-C3-14)'),
    'AREA_BRACKET': ('30 min epoxy', 'PETG flange sanded 120 grit; foam-board paper face scuffed 220 grit', '24 h',
                     'pod shear into the spar: C3 feet force 200 N crash over both brackets (CL-C3-FEA-SADDLE-TIES); '
                     'area >= 1 000 mm2 per side (CL-C3-FEA-SADDLE-BOND-AREA 1 996 mm2 total)', 'C1 crash, L1 landing', 'C3 (CR-C3-16)'),
    'AREA_SADDLE': ('30 min epoxy', 'spar top scuffed 120 grit and wiped with IPA; PETG sanded', '24 h',
                    'lift by the handle 2 g at 2.6 kg (51 N limit, 77 N ultimate); R5: no pack load (the aft stop is on the tray)',
                    'G1 handling', 'C3 (CR-D2-05), C2 (spar bearing)'),
}


def interfaces(G, L, M):
    A = areas(G, L)
    parts = []
    for pid, name, mat, mob, proc, vend, extras, notes in PARTS:
        mg, cg, br = M[pid]
        parts.append({'id': pid, 'name': name, 'subsystem': 'pod', 'status': 'MODELLED', 'mass_g': round(mg, 1),
                      'material': mat, 'cg_xyz_m': [round(v, 4) for v in cg], 'make_or_buy': mob,
                      'notes': notes + '; mass EST from CAD (team/D2/pod_data.py): ' +
                      ', '.join('%s %.1f g' % (k, v) for k, v in sorted(br.items()))})
    edges = []
    for e in EDGES:
        e = json.loads(json.dumps(e))
        b = e.pop('bond', None)
        if b:
            adh, prep, cure, load, case, by = BOND[b]
            e['bond'] = {'adhesive': adh, 'area_mm2': A[b], 'prep': prep, 'cure': cure, 'load_n': load,
                         'load_case': case, 'sized_by': by}
        if e.get('retention') == 'RET_PACK':
            e['retention'] = {'item': '2 hook-and-loop straps (>= 50 mm overlap) + 1.5 mm guides + EVA pads; crush block on the forward stop ahead, spacers on the aft stop behind', 'count': 2,
                              'load_n': '85 N any axis ultimate (CL-C1-PACK-CRASH-LOAD, 680 g x 12.75 g); preload 40 N per strap '
                                        '(ASM-C1-STRAP-PRELOAD); +x hover landing 6 g x 680 g = 40 N on the aft stop',
                              'inspection': 'strap cinched, overlap mark covered, block and spacer for this pack fitted, no fore-aft play: pre-flight card'}
        if e.get('retention') == 'RET_SPAR':
            e['retention'] = {'item': '7.6 mm nylon cable tie round foot + spar (50 lb class, 222 N each)', 'count': 2,
                              'load_n': 'CL-D2-HANDLE-F-ULT (2 g lift, handling; CR-C3-04: the crash path is straps -> tray -> floor -> bond)',
                              'inspection': 'ties tight, foot not lifting off the spar: weekly and after any hard landing'}
        edges.append(e)
    return {'schema': 'dbf-interfaces/1', 'subsystem': 'pod',
            '_note': 'GENERATED by redesign/team/D2/pod_data.py from the pod CAD module (masses and CGs from body volumes); '
                     'edit PARTS/EDGES there, not here. Interface plan: team/A4/INTERFACE-PLAN.md (pod rows); deviations '
                     'in the edge notes and team/D2/CHANGE-REQUESTS.md.',
            'parts': parts, 'connection_types': CTYPES, 'edges': edges, 'acknowledges': ACKS}


def parts_csv(M):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['part_id', 'name', 'qty', 'make_or_buy', 'process', 'material', 'mass_g', 'unit_cost_usd', 'vendor_or_file', 'notes'])
    cost = {'POD-001': 3.5, 'POD-002': 3.7, 'POD-003': 0.6, 'POD-004': 7.0, 'POD-005': 1.5, 'POD-006': 0.4, 'POD-007': 2.3, 'POD-008': 0.4,
            'POD-009': 0.2, 'POD-010': 0.2}
    for pid, name, mat, mob, proc, vend, extras, notes in PARTS:
        w.writerow([pid, name, 1, mob, proc, mat, round(M[pid][0], 1), cost[pid], vend,
                    notes + ' (mass EST from CAD; cost EST: board, filament, straps, ties, inserts)'])
    return buf.getvalue()


def main(argv):
    ctx, P, L, G, src = build_pod()
    M = masses(ctx, P, L)
    doc = interfaces(G, L, M)
    js = json.dumps(doc, indent=1, ensure_ascii=False) + '\n'
    cs = parts_csv(M)
    tot = sum(v[0] for v in M.values())
    cg = [sum(M[k][0] * M[k][1][i] for k in M) / tot for i in range(3)]
    if '--check' in argv:
        same = (POD / 'interfaces.json').read_text(encoding='utf-8') == js and (POD / 'parts.csv').read_text(encoding='utf-8') == cs
        print('pod_data: %s' % ('up to date' if same else 'STALE - re-run without --check'))
        return 0 if same else 1
    (POD / 'interfaces.json').write_text(js, encoding='utf-8')
    (POD / 'parts.csv').write_text(cs, encoding='utf-8')
    print('section: %s' % src)
    for pid in M:
        print('%-8s %6.1f g  cg %s  %s' % (pid, M[pid][0], ', '.join('%.4f' % v for v in M[pid][1]),
                                          ', '.join('%s %.1f' % (k, v) for k, v in sorted(M[pid][2].items()))))
    print('pod total %.1f g, cg %s m' % (tot, ', '.join('%.4f' % v for v in cg)))
    for pid, d in cg_vs_body(ctx, M).items():                 # CR-A5-27: declared (mass) CG vs uniform-density body centroid
        print('  %-8s mass CG vs body centroid %.1f mm%s' % (pid, d * 1000, '  > 10 mm (A5 tolerance)' if d > 0.010 else ''))
    print('bond areas mm2: %s' % areas(G, L))
    for k in ('stations', 'tray_rear_area', 'ch_x', 'ch_h', 'cross_gap', 'cross_h', 'tray_front_area',
              'x_rec0', 'x_rec1', 'xn', 'x_fs0', 'x_fs', 'nose_block', 'x_as', 'pack_fwd_c', 'pack_c_nom', 'pack_c_hvy', 'travel',
              'spacer_nom', 'spacer_hvy', 'block_nom', 'bay', 'zp', 'overhang_surf', 'overhang_clr', 'pack_z_c', 'z_aft', 'zfoot',
              'z_as_top', 'z_grip0', 'z_grip1', 'z_mast1', 'gps_c', 'pitot_tip', 'boom_len', 'socket_x', 'ch_y', 'strap_x', 'pod_c',
              'ant_a', 'ant_a_pack_clr', 'ant_b_pack_clr', 'ant_b_boom_clr', 'gps_clr', 'ant_b_tip_x', 'strut_x', 'strut_rib_l',
              'strut_clear_skin', 'bracket_area', 'pdb_pad', 'fs_flange', 'fs_flange_bond'):
        print('  %-18s %s' % (k, G[k]))
    return 0


if __name__ == '__main__':
    rc = main(sys.argv[1:])
    if '--check' not in __import__('sys').argv:     # C6 FASTENERS-CAD: re-apply the modelled fastener parts
        import os as _o, runpy as _r
        _r.run_path(_o.path.join(_o.path.abspath(__file__).rsplit(_o.sep + 'redesign' + _o.sep, 1)[0], 'redesign', 'team',
                                 'C6', 'fastener_parts.py'), run_name='c6_hook')['run']()
    sys.exit(rc)
