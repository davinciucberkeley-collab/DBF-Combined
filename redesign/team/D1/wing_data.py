"""D1 wing data generator: builds subsystems/wing/fusion/wing.py on the stub backend, turns the bodies into masses and
CGs, and writes subsystems/wing/interfaces.json and subsystems/wing/parts.csv from one table, so the declared masses
and CGs are the CAD's.

    python -I redesign/team/D1/wing_data.py          # rewrite interfaces.json + parts.csv, print the roll-up
    python -I redesign/team/D1/wing_data.py --check  # exit 1 if the files on disk differ from what it would write

Masses (all EST until T-D1-WEIGH): XPS = CAD volume x params wing.core.density_kgm3 (+ the C2 slot fill in the core);
tape = surface arc length x span x params wing.skin.areal_mass_kgm2 (the CAD tape bodies are 0.1 mm thick for display
only); spar = params wing.spar.mass_per_m_kgm x length; plugs and label from subsystems/wing/params.json.
Acknowledgements: edges other subsystems declare on wing parts. An edge still parked in its owner's edges_pending is
listed under acknowledges_pending and moves to acknowledges the next time this script runs after the owner declares it.
"""
import csv
import glob
import importlib.util
import io
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
WING = REDESIGN / 'subsystems' / 'wing'
sys.path.insert(0, str(REDESIGN / 'fusion'))
import fusionkit as fk                              # noqa: E402
import k09kit as k9                                 # noqa: E402
from backends.stub_backend import StubBackend      # noqa: E402


def load_module():
    spec = importlib.util.spec_from_file_location('wing_module', str(WING / 'fusion' / 'wing.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ----------------------------------------------------------------------------- the part table (one source)
# id, name, material, make_or_buy, process, vendor_or_file, notes, extra fields
PARTS = [
    ('WNG-001', 'Wing core, one piece (XPS), with all cuts', 'XPS foam F-250', 'make',
     'hot-wire (templates from wing.py), slot and pockets by hot tool / knife', 'FOAMULAR NGX F-250 2 in sheet (SRC-XPS-F250), 6 cores per sheet',
     'S5010, 1.150 x 0.320 m, hot-wired LE sanded smooth; spar bore 22.4 mm (slot from below, cap re-bonded); pod recess '
     'x 0.0226-0.065 floor z 0.015, |y| <= 0.07; pod saddle windows |y| 0.029-0.053 with tie channels at 0.036; anchor '
     'pockets |y| 0.2335-0.2505 top and bottom; block pockets |y| 0.302-0.338 x 0.028-0.097 full depth, corners R 3.15, '
     '3 x 3 mm lip chamfers inboard and outboard both surfaces; ESC grooves both surfaces |y| 0.086-0.296; servo groove and '
     'branch with the JR recess x 0.150-0.168 |y| 0.280-0.290 5 mm deep; servo pockets (open below) x 0.1722-0.2075 '
     '|y| 0.2527-0.2879; elevon cut-outs with R 3 mm corners at the fin-root tabs', {}),
    ('WNG-002', 'Spar CF 22x20x1000', 'CF tube 22x20 (bought)', 'buy', 'cut square, scuff 120 grit, IPA',
     'SRC-CF-TUBE 22 x 20 x 1000 mm $28.32', 'unspliced, |y| <= 0.50, axis x 0.080 z +0.0066 (D-03); stock length used as is', {}),
    ('WNG-003', 'Tape skin (packing tape, both surfaces, doublers, tip edge layer)', 'packing tape (BOPP), 48 mm', 'make',
     'hand-laid spanwise strips, 10 % overlap', 'Scotch Heavy Duty packing tape 48 mm (cost.csv)',
     '1 layer each side; one 100 mm LE strip laid last (edges x 0.045 upper / 0.047 lower, aft of x/c 0.10); none under the '
     'pod (x 0-0.095, |y| <= 0.07) or the half-fin roots; 60 mm doublers over the block pockets (wrapped round the LE, '
     'continuous over the lip beads) and the servo pockets; 24 mm strip folded round each fin-root tab edge; 2nd layer '
     'folded round each tip', {}),
    ('WNG-004', 'Spar plug under the through-core block (PETG)', 'PETG (printed)', 'make', 'FDM PETG 4 perimeters 50 % gyroid',
     'subsystems/wing/fusion/wing.py', 'D 19.8 x 36 mm inside the spar at |y| 0.320, bonded with thickened epoxy (C2 CR-C2-01)', {}),
    ('WNG-005', 'Spar plug at the brace anchors (PETG)', 'PETG (printed)', 'make', 'FDM PETG 30 % fill',
     'subsystems/wing/fusion/wing.py', 'D 19.8 x 20 mm inside the spar at |y| 0.242; upper and lower anchors share it; pushed in first', {}),
    ('WNG-006', 'Block-pocket lip beads (microballoon epoxy)', 'epoxy + glass microballoons 1:1 by volume', 'make',
     'chamfer the pocket lip 3 x 3 mm 45 deg, fill wet with the block bond, sand flush', 'subsystems/wing/fusion/wing.py',
     'inboard and outboard pocket lips, upper and lower, x 0.0279-0.0972 (D-68, CR-C2-11); 60 mm tape doubler over them', {}),
    ('WNG-011', 'Elevon inboard', 'XPS foam F-250 + packing-tape skin', 'make', 'cut from the core after the hot-wire pass; tape both faces',
     'subsystems/wing/fusion/wing.py', 'y 0.071-0.299, hinge x 0.2496 on the upper skin, lower edge bevelled 30 deg; D6 torque-tube groove (open below) |y| 0.1335-0.296 and 2.5 mm horn-blade slot at y 0.285; outboard front corner relieved round the R 3 mm tab fill; tape cut back for the horn flange (14 mm) and backplate (12 mm)', {}),
    ('WNG-012', 'Elevon outboard', 'XPS foam F-250 + packing-tape skin', 'make', 'cut from the core after the hot-wire pass; tape both faces',
     'subsystems/wing/fusion/wing.py', 'y 0.341-0.559, hinge x 0.2496 on the upper skin, lower edge bevelled 30 deg; D6 torque-tube groove |y| 0.344-0.556 and 2.5 mm link-horn slot at y 0.355; inboard front corner relieved round the R 3 mm tab fill; tape cut back for the horn flange and backplate', {}),
    ('WNG-020', 'FAA registration label', 'vinyl label (printed)', 'make', 'print, laminate, apply',
     'registration number from H3 (FAADroneZone)', 'right wing upper surface x 0.115-0.215, y 0.375-0.405; visible without tools', {'carried': True}),
]
INSTANCES = {'WNG-006': ('R', 'L'), 'WNG-004': ('R', 'L'), 'WNG-005': ('R', 'L'), 'WNG-011': ('R', 'L'), 'WNG-012': ('R', 'L')}

ACK_ALL = ['E-POD-01', 'E-POD-09', 'E-TRN-06', 'E-TRN-07', 'E-TRN-08', 'E-TRN-09',
           'E-FIN-49', 'E-FIN-50', 'E-FIN-51', 'E-FIN-52', 'E-FIN-53', 'E-FIN-54', 'E-FIN-55', 'E-FIN-56',
           'E-FIN-57', 'E-FIN-58', 'E-FIN-59', 'E-FIN-60', 'E-GER-21', 'E-GER-22', 'E-HRN-02', 'E-HRN-04',
           'E-MEC-01', 'E-MEC-02', 'E-MEC-11', 'E-MEC-12',
           'E-MEC-17', 'E-MEC-18']
ACK_OWNER = {'E-POD': 'pod (D2)', 'E-TRN': 'transport (D7)', 'E-FIN': 'fins (D3)', 'E-GER': 'landing (D5)',
             'E-HRN': 'harness (F2)', 'E-MEC': 'mechanisms (D6)'}
PATCH_PANEL = {'WNG-011': 0, 'WNG-012': 1}           # horn station index per panel (mechanisms mec.horn flange / backplate)


def ids():
    out = []
    for pid, *_r in PARTS:
        out += ['%s-%s' % (pid, s) for s in INSTANCES[pid]] if pid in INSTANCES else [pid]
    return out


def base(iid):
    return iid[:7]


def build_wing():
    P = k9.load_params()
    parts_info = {}
    for pid, name, mat, *_r in PARTS:
        for iid in (['%s-%s' % (pid, s) for s in INSTANCES[pid]] if pid in INSTANCES else [pid]):
            parts_info[iid] = {'name': name, 'material': mat, 'mass_g': 1.0, 'status': 'MODELLED'}
    ctx = fk.Context(StubBackend(), parts=parts_info, params=P)
    ctx.begin_module('wing', str(WING))
    k9.build_datums(ctx)
    mod = load_module()
    g = mod.build(ctx)
    return ctx, P, g, mod


# ----------------------------------------------------------------------------- geometry helpers
def arc_len(mod, g, x0, x1, side, n=200):
    return mod.arc(g, x0, x1, side, n)


def perimeter(loop):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(loop, loop[1:] + loop[:1]))


def shape_mass(mod, g, P, L, s):
    """(grams, centroid) of one body."""
    rho = k9.val(P, 'wing.core.density_kgm3', 'kg/m3')
    ar = k9.val(P, 'wing.skin.areal_mass_kgm2', 'kg/m2')
    V, cg = s.volume_centroid()
    nm = s.name or ''
    if nm.startswith('xps elevon'):
        span = abs(s.depth)
        xs = [p[0] for p in s.loops[0]]
        x0, x1 = min(xs), max(xs)
        tape = arc_len(mod, g, x0, x1, 'upper') + (arc_len(mod, g, max(x0, g['xh'] + g['bevel']), x1, 'lower')
                                                   if x1 > g['xh'] + g['bevel'] else 0.0)
        return V * rho * 1000 + tape * span * ar * 1000, cg
    if nm.startswith('xps '):
        return V * rho * 1000, cg
    if nm.startswith('bead ') or nm.startswith('fillet '):
        return V * k9.lval(L, 'block_pocket.bead_density_gcc', 'g/cm3') * 1e6, cg
    if nm == 'tape tab edge':
        return perimeter(s.loops[0]) * k9.lval(L, 'skin.tab_edge_tape_w_m', 'm') * ar * 1000, cg
    if nm == 'tape tip edge':
        w = k9.lval(L, 'skin.tip_tape_w_m', 'm')
        n = k9.lval(L, 'skin.tip_extra_layers', '-')
        return perimeter(s.loops[0]) * w * n * ar * 1000, cg
    if nm.startswith('tape '):
        xs = [p[0] for p in s.loops[0]]
        side = 'upper' if 'upper' in nm else 'lower'
        return arc_len(mod, g, min(xs), max(xs), side) * abs(s.depth) * ar * 1000, cg
    raise ValueError('no mass rule for body %r' % nm)


def masses(ctx, P, g, mod):
    L = k9.local('wing')
    lv = lambda k, u=None: k9.lval(L, k, u)
    out = {}
    for iid, c in ctx.components.items():
        if iid == 'WNG-002':
            m = k9.val(P, 'wing.spar.mass_per_m_kgm', 'kg/m') * k9.val(P, 'wing.spar.length_m', 'm') * 1000
            out[iid] = (m, c.volume_centroid()[1], {'CF tube': m})
            continue
        if base(iid) in ('WNG-004', 'WNG-005'):
            m = lv('plugs.block_mass_g' if base(iid) == 'WNG-004' else 'plugs.anchor_mass_g', 'g')
            out[iid] = (m, c.volume_centroid()[1], {'PETG + bond': m})
            continue
        if iid == 'WNG-020':
            m = lv('label.mass_g', 'g')
            out[iid] = (m, c.volume_centroid()[1], {'label': m})
            continue
        M, mom, br = 0.0, [0.0, 0.0, 0.0], {}
        for s in c.shapes:
            gm, cg = shape_mass(mod, g, P, L, s)
            M += gm
            mom = [mom[i] + gm * cg[i] for i in range(3)]
            nm = s.name or ''
            k = ('XPS' if nm.startswith('xps') else 'microballoon epoxy' if nm.startswith(('bead', 'fillet')) else
                 'tape doubler' if 'doubler' in nm else 'tape LE strip' if 'LE strip' in nm else
                 'tape tab edge' if 'tab edge' in nm else 'tape tip' if 'tip' in nm else 'tape')
            br[k] = br.get(k, 0.0) + gm
        if iid == 'WNG-001':
            fill = lv('slot.fill_g', 'g')
            M += fill
            mom = [mom[0] + fill * g['xs'], mom[1], mom[2] + fill * g['zs']]
            br['slot fill (C2)'] = fill
        if base(iid) in PATCH_PANEL:                    # bare-foam patches under D6's horn flange and backplate
            Mh = k9.local('mechanisms')
            fl = k9.lval(Mh, 'mec.horn.flange_mm', 'mm', [8.0, 38.0, 14.0, 1.2])
            bp = k9.lval(Mh, 'mec.horn.backplate_mm', 'mm', [14.0, 38.0, 12.0, 1.0])
            cut = ((fl[1] - fl[0]) * fl[2] + (bp[1] - bp[0]) * bp[2]) * 1e-6 * k9.val(P, 'wing.skin.areal_mass_kgm2', 'kg/m2') * 1000
            mom = [m * (M - cut) / M for m in mom]      # patches near the panel CG: CG kept
            M -= cut
            br['tape patches cut'] = -cut
        out[iid] = (M, tuple(m / M for m in mom), br)
    return out


# ----------------------------------------------------------------------------- read-outs used by claims and notes
def readouts(ctx, P, g, mod):
    """Geometry numbers other roles depend on (m, mm2, deg)."""
    r = {}
    # spar foam cover in the plain segments
    r['cover_upper'] = mod.surf(g, g['xs'], 'upper') - (g['zs'] + g['rb'])
    r['cover_lower'] = (g['zs'] - g['rb']) - mod.surf(g, g['xs'], 'lower')
    r['cover_min'] = min(min(mod.surf(g, x, 'upper') - (g['zs'] + math.sqrt(max(g['rb'] ** 2 - (x - g['xs']) ** 2, 0))),
                             (g['zs'] - math.sqrt(max(g['rb'] ** 2 - (x - g['xs']) ** 2, 0))) - mod.surf(g, x, 'lower'))
                         for x in [g['xs'] - g['rb'] + i * 2 * g['rb'] / 40 for i in range(41)])
    # wall between the aft ESC groove and the spar slot (F2 asked >= 3 mm)
    xc, w, _d = g['grooves'][-1]
    r['groove_wall'] = g['x_slot'][0] - (xc + w / 2)
    # deepest groove / local thickness between x 0.06 and 0.10 (C2: <= 50 %)
    r['groove_depth_frac'] = max((d / (mod.surf(g, xc, 'upper') - mod.surf(g, xc, 'lower'))) for xc, w, d in g['grooves'])
    # servo pocket (open below): foam over the ceiling, depth range, bare-foam bond surface (ceiling + 4 walls)
    (x0, x1), (y0, y1), zc = g['sp_x'], g['sp_y'], g['sp_zc']
    xs20 = [x0 + (x1 - x0) * i / 20 for i in range(21)]
    r['pocket_roof_foam'] = min(mod.surf(g, x, 'upper') - zc for x in xs20)
    r['pocket_depth'] = (zc - mod.surf(g, x0, 'lower'), zc - mod.surf(g, x1, 'lower'))
    wall_x = sum((zc - mod.surf(g, x, 'lower')) for x in (x0, x1)) * (y1 - y0)
    wall_y = 2 * sum((zc - mod.surf(g, x0 + (x1 - x0) * (i + 0.5) / 20, 'lower')) * (x1 - x0) / 20 for i in range(20))
    r['pocket_bond_mm2'] = ((x1 - x0) * (y1 - y0) + wall_x + wall_y) * 1e6
    # torque-tube groove in the panels: foam + skin over the groove ceiling
    gx0, gx1, gzc = g['tube_groove']
    r['tube_groove_cover'] = min(mod.surf(g, x, 'upper') for x in (gx0, gx1)) - gzc
    # elevon area fraction (panels as built, end gaps off)
    span_e = sum((b - a) - 2 * g['e_gap'] for a, b in g['spans']) * 2
    r['elevon_area_frac'] = span_e * (g['c'] - g['xh']) / (2 * g['half'] * g['c'])
    # hinge clearance: lower bevel corner of the panel against the core aft face (vertical at x_h) at both stops
    t, b = g['t_hinge'], g['bevel']
    zl = mod.surf(g, g['xh'] + b, 'lower') - mod.surf(g, g['xh'], 'upper')
    clr = {}
    for d in g['defl']:
        a = math.radians(d)                        # + = trailing edge down
        clr[d] = b * math.cos(a) + zl * math.sin(a)
    r['hinge_clear'] = clr
    r['t_hinge'], r['bevel'] = t, b
    # pod recess
    r['recess_x'] = (g['x_rec0'], g['x_rec1'])
    r['recess_depth_max'] = max(mod.surf(g, g['x_rec0'] + i * (g['x_rec1'] - g['x_rec0']) / 30, 'upper') - g['z_rec'] for i in range(31))
    r['recess_foam_under'] = g['z_rec'] - mod.surf(g, g['x_rec1'], 'lower')
    # spar bond area (full bore segments + the lower part of the window bores)
    bond = 0.0
    for y0, y1, act in mod.segments(g):
        if 'spar' not in act or 'block' in act or 'anchor' in act:
            continue
        frac = 1.0
        if 'window' in act:
            tt = math.asin((g['z_cheek'] - g['zs']) / g['rb'])
            frac = (math.pi + 2 * tt) / (2 * math.pi)
        bond += 2 * math.pi * g['rb'] * frac * (y1 - y0) * 2          # both sides (the y0 = 0 body spans +/-y1)
    r['spar_bond_mm2'] = bond * 1e6
    # D-68 / D-69 / CR-B2-17 / CR-F2-14 geometry
    r['bead_len'] = g['blk_x'][1] - g['blk_x'][0]
    r['bead_leg'] = g['bead_leg']
    r['blk_corner_r'] = g['blk_rp']
    r['cutout_corner_r'] = g['ecr']
    r['le_edge'] = (g['le_edge']['upper'], g['le_edge']['lower'])
    r['le_seam_min_x'] = min(g['le_edge'].values())
    r['rf_legs'] = g['rf_legs']
    r['jr_wall'] = g['sp_x'][0] - g['jr_x'][1]
    r['jr_foam_under'] = min(mod.surf(g, x, 'upper') - g['jr_d'] - mod.surf(g, x, 'lower') for x in g['jr_x'])
    return r


# ----------------------------------------------------------------------------- declared and pending acknowledgements
def declared_elsewhere():
    """(ids of edges other subsystems declare, ids of those that touch a wing part)."""
    found, touching = set(), set()
    for f in glob.glob(str(REDESIGN / 'subsystems' / '*' / 'interfaces.json')):
        if Path(f).parent.name == 'wing':
            continue
        try:
            d = json.loads(Path(f).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        for e in d.get('edges', []):
            found.add(e.get('id'))
            if str(e.get('part_a', '')).startswith('WNG-') or str(e.get('part_b', '')).startswith('WNG-'):
                touching.add(e.get('id'))
    return found, touching


# ----------------------------------------------------------------------------- edges
def edges(g, r, M):
    bond_foam = '30 min laminating epoxy + glass microballoons 1:1 by volume (foam-safe; no CA, no solvent glue on XPS)'
    bond_cf = '30 min laminating epoxy + ~5 % colloidal silica (non-sag)'
    cure = '24 h at >= 18 degC before load or tape'
    E = [
        {'id': 'E-WNG-01', 'part_a': 'WNG-002', 'part_b': 'WNG-001', 'via': 'CT-EPOXY', 'owner': 'wing',
         'notes': 'spar in the 22.4 mm bore on the camber line (x 0.080, z +0.0066): slot cut from the lower surface to z_s + 11.2 mm '
                  'with a round top, spar bonded, slot strip trimmed and re-bonded as the cap; four PETG plugs and the two pod ties '
                  '(y +/-0.036) go in first; the through-core blocks are threaded on before the spar is bonded (E-FIN-49/50)',
         'bond': {'adhesive': bond_foam, 'area_mm2': round(r['spar_bond_mm2']),
                  'prep': 'tube 120 grit to matte + IPA, gloves; slot vacuumed, foam dust off',
                  'cure': cure, 'load_n': 'air load into the spar 186 N/m: slot shear 8.1 kPa vs 100 kPa, MS +11 (CL-C2-SPAR-BOND-TAU)',
                  'load_case': 'C1 flight envelope (F1 pull-up at VD)', 'sized_by': 'C2'}},
        {'id': 'E-WNG-02', 'part_a': 'WNG-003', 'part_b': 'WNG-001', 'via': 'CT-TAPE-SKIN', 'owner': 'wing',
         'notes': 'spanwise strips TE to LE, 10 %% overlap, the forward strip of each face stopping under the LE strip (x %.4f upper / '
                  '%.4f lower); one 100 mm LE strip laid last, edges at x %.4f upper / %.4f lower, aft of x/c 0.10 (CR-B2-17: no seam, '
                  'overlap or doubler edge ahead of 32 mm except the block-pocket doublers); tape laps 15 mm up both faces of each '
                  'half-fin root (L-angle, E-FIN-53...56); no tape under the pod; 60 mm doublers over the block pockets (continuous '
                  'over the lip beads) and the servo pockets; a 24 mm strip folded round each fin-root tab side face and its R 3 mm '
                  'corner (CR-C2-13); second layer folded round each tip (damage fuse)' % (
                      g['skin_lap']['upper'], g['skin_lap']['lower'], g['le_edge']['upper'], g['le_edge']['lower']),
         'retention': {'item': 'packing tape 48 mm, pressure-sensitive acrylic', 'count': 'continuous',
                       'load_n': 'chordwise bending aft of the spar 13.0 MPa vs 60 MPa (CL-C2-CHORD-TAPE); torsion cell',
                       'inspection': 'pre-flight: no lifted edge at the LE strip, pockets, tab edges, tips or fin roots; no seam, '
                                     'wrinkle or dent within 32 mm of the LE; re-tape any lift'}},
        {'id': 'E-WNG-03', 'part_a': 'WNG-020', 'part_b': 'WNG-003', 'via': 'CT-LABEL', 'owner': 'wing',
         'notes': 'FAA registration number on the right wing upper skin, x 0.115-0.215, y 0.375-0.405; readable without tools '
                  '(14 CFR 48.205); laminated label, one clear tape strip over the edges',
         'retention': {'item': 'self-adhesive vinyl + clear tape border', 'count': 1, 'load_n': 'none (non-structural)',
                       'inspection': 'pre-flight: number readable'}},
    ]
    hm = 257
    for eid, iid, (y0, y1) in (('E-WNG-04', 'WNG-011-L', g['spans'][0]), ('E-WNG-05', 'WNG-012-L', g['spans'][1]),
                               ('E-WNG-06', 'WNG-011-R', g['spans'][0]), ('E-WNG-07', 'WNG-012-R', g['spans'][1])):
        E.append({'id': eid, 'part_a': iid, 'part_b': 'WNG-001', 'via': 'CT-TAPE-HINGE', 'owner': 'wing',
                  'notes': 'tape hinge on the upper skin at x %.4f (DP-HINGE), panel |y| %.3f-%.3f with %.0f mm end gaps; panel front '
                           'face bevelled %.0f deg on the lower side (%.1f mm at the lower skin); hinge tape and stops by D6 '
                           '(mechanisms), surfaces by D1' % (g['xh'], y0 + g['e_gap'], y1 - g['e_gap'], g['e_gap'] * 1000,
                                                              k9.lval(k9.local('wing'), 'elevon.bevel_deg', 'deg'), g['bevel'] * 1000),
                  'motion': {'axis': 'Y', 'range_deg': list(g['defl'])},
                  'clearance_mm': {'down_stop_%+d_deg' % g['defl'][1]: round(r['hinge_clear'][g['defl'][1]] * 1000, 2),
                                   'up_stop_%+d_deg' % g['defl'][0]: round(r['hinge_clear'][g['defl'][0]] * 1000, 2),
                                   'hinge_moment_nmm': '%d per servo (two panels) at 25 deg, 20.8 m/s (CL-B2-HINGE-MOMENT)' % hm}})
    plug = [('E-WNG-08', 'WNG-004-L', 'plugs.block_len_m', 'ring bearing under the block bore: 961 N design couple, 5.3 MPa vs 20 MPa PETG, MS +2.7 (CL-C2-PLUG-BEARING)', 'C4 corner case (961 N couple)'),
            ('E-WNG-09', 'WNG-004-R', 'plugs.block_len_m', 'as E-WNG-08', 'C4 corner case (961 N couple)'),
            ('E-WNG-10', 'WNG-005-L', 'plugs.anchor_len_m', 'brace saddle 146 N design over 16 mm: the plug removes the ring-bending FAIL (CL-C2-RING-ANCHOR)', 'C4 brace load'),
            ('E-WNG-11', 'WNG-005-R', 'plugs.anchor_len_m', 'as E-WNG-10', 'C4 brace load')]
    L = k9.local('wing')
    for eid, iid, key, load, case in plug:
        ln = k9.lval(L, key, 'm')
        where = 'the through-core block at |y| %.3f' % g['y_fin'] if 'block' in key else 'the brace anchors at |y| %.3f' % g['y_anchor']
        E.append({'id': eid, 'part_a': iid, 'part_b': 'WNG-002', 'via': 'CT-EPOXY', 'owner': 'wing',
                  'notes': 'PETG plug D %.1f x %.0f mm bonded inside the spar under %s; pushed from the spar end with a marked dowel '
                           '(anchor plug first, then the block plug) before the spar is bonded' % (g['plug_r'] * 2000, ln * 1000, where),
                  'bond': {'adhesive': bond_cf, 'area_mm2': round(math.pi * g['plug_r'] * 2 * ln * 1e6),
                           'prep': 'plug 120 grit; spar bore scuffed with a 120-grit flap on a rod, IPA', 'cure': cure,
                           'load_n': load, 'load_case': case, 'sized_by': 'C2'}})
    # D-68 lip beads and D-69 recess-step fillet
    bl, lb = r['bead_len'], g['bead_leg']
    E += [{'id': eid, 'part_a': iid, 'part_b': 'WNG-001', 'via': 'CT-EPOXY', 'owner': 'wing',
           'notes': 'lip bead in the 3 x 3 mm 45 deg chamfer along the inboard and outboard block-pocket lips, upper and lower '
                    'surface, x %.4f-%.4f (4 beads per side); laid wet in the same pour as the block bond, sanded flush; the 60 mm '
                    'doubler covers it' % g['blk_x'],
           'bond': {'adhesive': bond_foam, 'area_mm2': round(4 * bl * lb * math.sqrt(2) * 1e6),
                    'prep': 'chamfer cut with a 45 deg hot tool or sanding block guided on the pocket wall; foam dust off',
                    'cure': cure, 'load_n': 'block corner load into the foam: as drawn (square corners, no bead) 203 / 199 kPa vs 150 / '
                                            '120 kPa ultimate at the inboard-front-lower corner (CL-C2-FEA-FOAM-CORNER-S1/-S3); C2 '
                                            're-runs the FEA on the R 3 mm pocket with these beads',
                    'load_case': 'L4 corner + side landing, ultimate', 'sized_by': 'C2'}}
          for eid, iid in (('E-WNG-12', 'WNG-006-R'), ('E-WNG-13', 'WNG-006-L'))]
    E += [{'id': eid, 'part_a': iid, 'part_b': blk, 'via': 'CT-EPOXY', 'owner': 'wing',
           'notes': 'the lip bead wets the block side face over its top and bottom 3 mm (inboard and outboard face), continuous '
                    'with the block-to-core bond E-FIN-51/52',
           'bond': {'adhesive': bond_foam, 'area_mm2': round(4 * bl * lb * 1e6),
                    'prep': 'block side faces 120 grit + IPA (as E-FIN-51/52)', 'cure': cure,
                    'load_n': 'spreads the block corner load into the lip (see E-WNG-12); C2 FEA re-run',
                    'load_case': 'L4 corner + side landing, ultimate', 'sized_by': 'C2'}}
          for eid, iid, blk in (('E-WNG-14', 'WNG-006-R', 'FIN-004-R'), ('E-WNG-15', 'WNG-006-L', 'FIN-004-L'))]
    # D-103: E-WNG-16 / -17 (recess-step fillet, WNG-007) removed with the fillet
    return E


def interfaces(M, g, r):
    have, touching = declared_elsewhere()
    ack = sorted(set(e for e in ACK_ALL if e in have) | touching)
    pend = [{'id': e, 'owner': ACK_OWNER[e[:5]], 'note': 'declared by its owner in edges_pending (or not yet); moves to acknowledges when declared'}
            for e in ACK_ALL if e not in have]
    parts = []
    for pid, name, mat, mob, _proc, _vend, notes, extra in PARTS:
        for iid in (['%s-%s' % (pid, s) for s in INSTANCES[pid]] if pid in INSTANCES else [pid]):
            m, cg, _br = M[iid]
            nm = name + (' ' + iid[-1] if pid in INSTANCES else '')
            p = {'id': iid, 'name': nm, 'subsystem': 'wing', 'status': 'MODELLED', 'mass_g': round(m, 1), 'material': mat,
                 'cg_xyz_m': [round(v, 4) + 0.0 for v in cg], 'make_or_buy': mob, 'notes': notes}
            p.update(extra)
            parts.append(p)
    return {'schema': 'dbf-interfaces/1', 'subsystem': 'wing',
            '_note': 'GENERATED by redesign/team/D1/wing_data.py from subsystems/wing/fusion/wing.py (D1, revision D1-R2, params A1-R5). '
                     'Masses and CGs are the CAD estimate (EST, T-D1-WEIGH). Edit the script or the module, not this file.',
            'parts': parts, 'edges': edges(g, r, M), 'acknowledges': ack, 'acknowledges_pending': pend}


def parts_csv(M):
    L = k9.local('wing')
    cost = k9.lval(L, 'cost_usd', 'USD')
    unit_cost = {'WNG-001': cost['xps_sheet'] / cost['cores_per_sheet'] + cost['epoxy'], 'WNG-002': cost['spar'],
                 'WNG-003': cost['tape_roll'] * cost['rolls'] + cost['le_tape_roll'], 'WNG-004': cost['petg_plugs'] / 4, 'WNG-005': cost['petg_plugs'] / 4,
                 'WNG-006': 0.0, 'WNG-011': 0.0, 'WNG-012': 0.0, 'WNG-020': cost['label']}
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['part_id', 'name', 'qty', 'make_or_buy', 'process', 'material', 'mass_g', 'unit_cost_usd', 'vendor_or_file', 'notes'])
    for pid, name, mat, mob, proc, vend, notes, _x in PARTS:
        inst = ['%s-%s' % (pid, s) for s in INSTANCES[pid]] if pid in INSTANCES else [pid]
        ms = [M[i][0] for i in inst]
        mean = sum(ms) / len(ms)
        note = notes + ('; per-unit mass = mean of %s' % ', '.join('%s %.1f g' % (i[-1], m) for i, m in zip(inst, ms)) if len(inst) > 1 else '')
        if pid == 'WNG-001':
            note += '; mass incl. the 15 g slot fill (C2); cost incl. the wing epoxy, microballoons and silica ($%.2f, shared kit)' % cost['epoxy']
        w.writerow([pid, name, len(inst), mob, proc, mat, '%.1f' % mean, '%.2f' % unit_cost[pid], vend, note])
    return buf.getvalue()


def main(argv):
    ctx, P, g, mod = build_wing()
    M = masses(ctx, P, g, mod)
    r = readouts(ctx, P, g, mod)
    js = json.dumps(interfaces(M, g, r), indent=1, ensure_ascii=False) + '\n'
    cs = parts_csv(M)
    if '--check' in argv:
        same = (WING / 'interfaces.json').read_text(encoding='utf-8') == js and (WING / 'parts.csv').read_text(encoding='utf-8') == cs
        print('wing_data: %s' % ('up to date' if same else 'STALE: re-run without --check'))
        return 0 if same else 1
    (WING / 'interfaces.json').write_text(js, encoding='utf-8')
    (WING / 'parts.csv').write_text(cs, encoding='utf-8')
    tot = sum(m for m, _c, _b in M.values())
    mom = [sum(m * c[i] for m, c, _b in M.values()) / tot for i in range(3)]
    alloc = json.loads((REDESIGN / 'params' / 'mass_budget.json').read_text(encoding='utf-8'))['allocations_g']['wing']
    for iid in ids():
        m, cg, br = M[iid]
        print('  %-10s %7.1f g  cg (%.4f, %+.4f, %+.4f)  %s' % (iid, m, cg[0], cg[1], cg[2],
                                                               ', '.join('%s %.1f' % kv for kv in br.items())))
    print('wing: %.1f g (allocation %d g, margin %+.1f g); CG (%.4f, %+.4f, %+.4f) m; %d core bodies' % (
        tot, alloc, alloc - tot, mom[0], mom[1], mom[2], len(ctx.components['WNG-001'].shapes)))
    for k, val in r.items():
        print('  %-20s %s' % (k, val))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
