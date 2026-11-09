"""D2 pod data generator: builds the pod CAD module on the stub backend, turns body volumes into masses and CGs,
and writes subsystems/pod/interfaces.json and subsystems/pod/parts.csv from one table, so the declared masses and
CGs are the CAD's.

    python -I redesign/team/D2/pod_data.py          # rewrite interfaces.json + parts.csv, print the roll-up
    python -I redesign/team/D2/pod_data.py --check  # exit 1 if the files on disk differ from what it would write

Masses: foam board = area x params fins.areal_mass_kgm2; XPS = volume x wing.core.density_kgm3; printed PETG =
volume x pod petg_kgm3 x fill (plate / block); rubber pad = volume x rubber_kgm3; bought items (straps, ties,
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
    ('POD-001', 'Pod shell (foam-board box, XPS LE filler, printed nose lip)', 'foam board + PETG', 'make',
     'knife/laser-cut foam board, hot-wire XPS filler, FDM lip', 'subsystems/pod/fusion/pod.py', ['glue_shell'],
     'floor, 2 side walls, nose wall, aft wall, aft deck; walls follow the S5010 upper surface aft of the recess'),
    ('POD-002', 'Tray: bay floor + guides + aft stop, FC plate, avionics plate (printed PETG)', 'PETG (printed)', 'make',
     'FDM PETG, 3 prints bonded to the floor', 'subsystems/pod/fusion/pod.py', ['glue_tray', 'inserts_m3'],
     '4 strap slots 31 x 1.8 mm; 4 M3 heat-set inserts (FC, 30.5 mm pattern UNVERIFIED) + 2 M2 bosses (airspeed)'),
    ('POD-003', 'Hatch (foam board, printed tongue, hook-and-loop latch tab)', 'foam board + PETG', 'make',
     'knife-cut foam board, FDM tongue', 'subsystems/pod/fusion/pod.py', ['velcro_tab'],
     'tool-free, no magnets: tongue under the nose lip, hook-and-loop tab on the aft deck'),
    ('POD-004', 'Pack straps (2, 20 mm hook-and-loop, rubber-backed) + anti-slip pad', 'nylon hook-and-loop + silicone', 'buy',
     'cut to length', 'battery strap 20 x 300 mm (any RC vendor); silicone sheet 0.5 mm', [],
     'two straps at the pack quarter points; slots let them follow the 23 mm trim travel'),
    ('POD-005', 'GPS mast (printed PETG, plugs into the handle grip)', 'PETG (printed)', 'make', 'FDM PETG',
     'subsystems/pod/fusion/pod.py', ['mast_hw'], 'GPS taped on the 30 mm top plate; cable runs down the mast and a handle leg'),
    ('POD-006', 'Pitot boom socket (printed PETG, pod nose, left channel)', 'PETG (printed)', 'make', 'FDM PETG',
     'subsystems/pod/fusion/pod.py', [], 'bore 6.2 mm for a 6 mm boom (UNVERIFIED, F3), keyed; 35 mm deep'),
    ('POD-007', "Carry handle on the spar (printed PETG) + 'LIFT HERE - do not lift by the motors' label", 'PETG (printed)',
     'make', 'FDM PETG, 40 % infill feet and grip', 'subsystems/pod/fusion/pod.py', ['tie_each', 'tie_each', 'label', 'glue_handle'],
     'feet saddle the spar top in the open slot, one 7.6 mm nylon tie each round foot + spar; legs through the aft deck'),
    ('POD-008', 'Trim spacer set (3 printed U-spacers 5 / 8 / 10 mm)', 'PETG (printed)', 'make', 'FDM PETG',
     'subsystems/pod/fusion/pod.py', [], 'in front of or behind the pack: 0 ... 23 mm aft trim in 8 steps'),
]

EDGES = [
    {'id': 'E-POD-01', 'part_a': 'POD-001', 'part_b': 'WNG-001', 'via': 'CT-EPOXY', 'owner': 'pod',
     'notes': 'shell floor, XPS LE filler, side walls and aft wall bonded to bare foam: D1 cuts the recess (x_rec0 ... x_rec1, '
              'z = pod base, full pod width) and leaves the tape skin off under the pod; skin then taped over the shell foot (CR-D2-04)',
     'bond': 'AREA_POD_WING'},
    {'id': 'E-POD-02', 'part_a': 'POD-002', 'part_b': 'POD-001', 'via': 'CT-EPOXY', 'owner': 'pod',
     'notes': 'tray, FC plate and avionics plate bonded to the foam-board floor (paper face scuffed)', 'bond': 'AREA_TRAY'},
    {'id': 'E-POD-03', 'part_a': 'POD-003', 'part_b': 'POD-001', 'via': 'CT-HATCH-HL', 'owner': 'pod',
     'notes': 'opened every flight, tool-free, no magnets; the hatch carries no pack load',
     'retention': {'item': 'tongue under the nose lip + 30 mm hook-and-loop tab', 'count': 1, 'load_n': 'hatch weight only (7 g)',
                   'inspection': 'tab grips, tongue seated: pre-flight card'}},
    {'id': 'E-POD-04', 'part_a': 'POD-004', 'part_b': 'POD-002', 'via': 'CT-STRAP-SLOT', 'owner': 'pod',
     'notes': 'each strap passes down a slot, under the tray in a 1 mm groove cut in the foam floor, up the other slot',
     'retention': {'item': 'strap in 2 slots 31 x 1.8 mm', 'count': 2, 'load_n': 'see E-POD-05', 'inspection': 'no fraying at the slot edges: pre-flight card'}},
    {'id': 'E-POD-05', 'part_a': 'PWR-001', 'part_b': 'POD-002', 'via': 'CT-STRAP-VELCRO', 'owner': 'pod',
     'notes': 'field joint. z/y: 2 straps + guides + pad; fore-aft: nose wall in front, aft stop behind, POD-008 spacers fill the '
              '23 mm (aft-only trim, CR-D2-02). Hover landing loads (+x) go into the aft stop, not the straps',
     'retention': 'RET_PACK'},
    {'id': 'E-POD-06', 'part_a': 'POD-005', 'part_b': 'POD-007', 'via': 'CT-M3-SHCS-NYLOC', 'owner': 'pod',
     'notes': 'mast plugs 10 mm into the grip socket; cross-bolted; replace the mast after a tip-over (A4 planned mast-to-shell bond: '
              'changed so the mast is replaceable and on structure)',
     'joint_stack': {'fastener': 'M3x16 SHCS', 'count': 1, 'grade': 'A2-70',
                     'hole': '3.4 mm clearance across the socket boss (POD-007) and the mast base (POD-005)', 'insert': 'none',
                     'engagement_mm': 4.0, 'min_engagement_mm': 3.0, 'washer_nut': 'M3 nyloc + M3 washer',
                     'torque': 'snug, about 0.3 N m (printed parts)', 'tool': '2.5 mm hex key + 5.5 mm spanner',
                     'access': 'from +y beside the grip, above the pod', 'install_order': 7, 'removal_order': 1}},
    {'id': 'E-POD-07', 'part_a': 'POD-006', 'part_b': 'POD-001', 'via': 'CT-EPOXY', 'owner': 'pod',
     'notes': 'socket through a 14 mm square hole in the nose wall, bonded both faces; boom bending (handling, 1 kg on the tip) '
              'goes into the nose wall and the left side wall', 'bond': 'AREA_SOCKET'},
    {'id': 'E-POD-08', 'part_a': 'POD-007', 'part_b': 'POD-001', 'via': 'CT-EPOXY', 'owner': 'pod',
     'notes': 'handle legs pass through 8.8 mm slots in the aft deck, bonded: locates the deck; the shell crash load bears on the legs',
     'bond': 'AREA_LEGS'},
    {'id': 'E-POD-09', 'part_a': 'POD-007', 'part_b': 'WNG-002', 'via': 'CT-SPAR-TIE', 'owner': 'pod',
     'notes': 'carry point on the spar (D-23): feet saddle the spar top in the open slot, bonded (scuffed CF, 30 min epoxy) and one '
              '7.6 mm nylon tie per foot laid under the spar before D1 bonds it (CR-D2-04). Also the positive pod retention',
     'retention': 'RET_SPAR', 'bond': 'AREA_SADDLE'},
    {'id': 'E-POD-10', 'part_a': 'POD-008', 'part_b': 'POD-002', 'via': 'CT-SLIDE-STOP', 'owner': 'pod',
     'notes': 'spacers stand on the tray between the guides, held by the pack and the stops; unused ones ride behind the pack',
     'retention': {'item': 'trapped between pack and nose wall / aft stop', 'count': 3, 'load_n': 'pack +x hover landing, see E-POD-05',
                   'inspection': 'all three spacers in the pod: pre-flight card'}},
]

CTYPES = [
    {'id': 'CT-HATCH-HL', 'kind': 'mechanical', 'method': 'strapped',
     'spec': 'hatch: printed tongue under a fixed lip at one end, hook-and-loop tab at the other (tool-free, no magnets)'},
    {'id': 'CT-STRAP-SLOT', 'kind': 'mechanical', 'method': 'slid', 'spec': 'strap threaded through slots in a printed tray'},
    {'id': 'CT-SPAR-TIE', 'kind': 'mechanical', 'method': 'strapped',
     'spec': 'printed saddle bonded on a round spar + nylon cable tie round saddle and spar (7.6 mm, 50 lb class)'},
    {'id': 'CT-SLIDE-STOP', 'kind': 'mechanical', 'method': 'slid', 'spec': 'loose printed spacer trapped between two stops'},
]

ACKS = ['E-PWR-01', 'E-PWR-02', 'E-PWR-03', 'E-PWR-04', 'E-AVN-01', 'E-AVN-02', 'E-AVN-03', 'E-AVN-04', 'E-AVN-05', 'E-HRN-01']


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
    petg, fill, rub = lv(L, 'petg_kgm3'), lv(L, 'fill'), lv(L, 'rubber_kgm3')
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
            elif nm.startswith('rub '):
                g, k = V * rub * 1000, 'rubber'
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
    saddle = 2 * (fy1 - fy0) * arc
    tray = (G['x_rec1'] - G['xn']) * (G['bw'] + 2 * G['tg']) + 2 * lv(L, 'fc_plate_len_m') * (G['ch_y'][1] - G['ch_y'][0])
    so = lv(L, 'socket_m')
    sock = 4 * so[0] * tb
    lg = lv(L, 'leg_m')[0]
    legs = 2 * 4 * lg * tb
    mm2 = lambda a: round(a * 1e6)
    return {'AREA_POD_WING': mm2(floor + filler + walls + aftw), 'AREA_TRAY': mm2(tray), 'AREA_SOCKET': mm2(sock),
            'AREA_LEGS': mm2(legs), 'AREA_SADDLE': mm2(saddle),
            'parts': {'floor': mm2(floor), 'filler': mm2(filler), 'walls': mm2(walls), 'aft wall': mm2(aftw)}}


BOND = {
    'AREA_POD_WING': ('30 min epoxy thickened with microballoons (foam-safe; no CA on XPS)', 'tape skin off under the pod; '
                      'foam and board faces scuffed, dust off', '24 h at >= 18 degC before load',
                      'CL-C1-POD-F-ULT 121.7 N + 3.0 N m (L1 landing, ultimate); crash: pod group 12.75 g (CL-D2-POD-CRASH-F)',
                      'L1 landing; C1 crash any axis', 'C3 (CR-D2-05)'),
    'AREA_TRAY': ('30 min epoxy', 'PETG underside sanded 120 grit; board face scuffed', '24 h',
                  'pack straps 85 N ultimate (CL-C1-PACK-CRASH-LOAD) into the floor', 'C1 crash', 'C3'),
    'AREA_SOCKET': ('30 min epoxy', 'PETG sanded; hole edges sealed', '24 h', '1 kg on the boom tip in handling, about 0.8 N m', 'handling', 'C3'),
    'AREA_LEGS': ('30 min epoxy', 'PETG sanded', '24 h', 'shell crash load bearing on the legs', 'C1 crash', 'C3'),
    'AREA_SADDLE': ('30 min epoxy', 'spar top scuffed 120 grit and wiped with IPA; PETG sanded', '24 h',
                    'lift by the handle 2 g at 2.6 kg (51 N limit, 77 N ultimate); pod group crash (CL-D2-POD-CRASH-F)',
                    'G1 handling; C1 crash', 'C3, C2 (spar bearing)'),
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
            e['retention'] = {'item': '2 hook-and-loop straps + guides; nose wall, aft stop, spacers fore-aft', 'count': 2,
                              'load_n': '85 N any axis ultimate (CL-C1-PACK-CRASH-LOAD, 680 g x 12.75 g); preload 40 N per strap '
                                        '(ASM-C1-STRAP-PRELOAD); +x hover landing 6 g x 680 g = 40 N on the aft stop',
                              'inspection': 'strap cinched, spacer set complete, pack against a stop: pre-flight card'}
        if e.get('retention') == 'RET_SPAR':
            e['retention'] = {'item': '7.6 mm nylon cable tie round foot + spar (50 lb class, 222 N each)', 'count': 2,
                              'load_n': 'CL-D2-POD-CRASH-F (pod group 12.75 g) and CL-D2-HANDLE-F-ULT (2 g lift)',
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
    cost = {'POD-001': 3.0, 'POD-002': 2.5, 'POD-003': 0.5, 'POD-004': 6.0, 'POD-005': 0.5, 'POD-006': 0.3, 'POD-007': 2.0, 'POD-008': 0.4}
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
    print('bond areas mm2: %s' % areas(G, L))
    for k in ('x_rec0', 'x_rec1', 'x_stop0', 'xn', 'pack_fwd_c', 'travel', 'bay', 'zp', 'pack_z_c', 'z_aft', 'zfoot',
              'z_grip0', 'z_grip1', 'z_mast1', 'gps_c', 'pitot_tip', 'boom_len', 'socket_x', 'ch_y', 'strap_x', 'pod_c'):
        print('  %-18s %s' % (k, G[k]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
